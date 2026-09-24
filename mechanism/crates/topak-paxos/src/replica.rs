//! Message-level Multi-Paxos as a sans-IO state machine.
//!
//! One replica plays acceptor, learner and (when elected) proposer. A stable leader runs phase 1
//! once for every slot at or beyond its commit point, then phase 2 per command. Leadership is
//! driven by heartbeats on the host-supplied clock; clocks here buy liveness only (ADR-0032 §1):
//! nothing in the safety argument reads `now`.

use serde::{Deserialize, Serialize};
use std::collections::{BTreeMap, BTreeSet, VecDeque};

use crate::{Ballot, Cmd, NodeId, Slot};

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub enum Msg<V> {
    Prepare {
        ballot: Ballot,
        from_slot: Slot,
    },
    Promise {
        ballot: Ballot,
        accepted: Vec<(Slot, Ballot, Cmd<V>)>,
    },
    /// `rejected` was refused because the acceptor has promised `promised`.
    Nack {
        rejected: Ballot,
        promised: Ballot,
    },
    Accept {
        ballot: Ballot,
        slot: Slot,
        cmd: Cmd<V>,
    },
    Accepted {
        ballot: Ballot,
        slot: Slot,
    },
    Commit {
        slot: Slot,
        cmd: Cmd<V>,
    },
    /// `next` is the leader's first undelivered slot.
    Heartbeat {
        ballot: Ballot,
        next: Slot,
    },
    CatchUp {
        from_slot: Slot,
    },
    Forward {
        value: V,
    },
}

#[derive(Clone, Debug, PartialEq)]
pub enum Input<V> {
    Propose(V),
    Receive { from: NodeId, msg: Msg<V> },
    Tick { now_ms: u64 },
}

/// Outputs are ordered. A host MUST make each `Persist*` durable before it transmits any `Send`
/// that follows it in the same batch; `Deliver`s arrive in slot order with no gaps other than
/// `Noop` slots.
#[derive(Clone, Debug, PartialEq)]
pub enum Output<V> {
    PersistPromise { ballot: Ballot },
    PersistAccept { slot: Slot, ballot: Ballot, cmd: Cmd<V> },
    Send { to: NodeId, msg: Msg<V> },
    Deliver { slot: Slot, value: V },
}

/// Deliberately broken protocol variants. Each must be caught by the simulation's invariant
/// checks; if one is not, the checks are vacuous (the corpus's mutation discipline).
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Mutation {
    /// A new leader ignores the values reported in promises (breaks phase 1's purpose).
    IgnorePromisedValues,
    /// Acceptors accept at ballots below their promise.
    AcceptBelowPromise,
}

#[derive(Clone, Debug)]
pub struct Config {
    pub id: NodeId,
    pub members: Vec<NodeId>,
    pub heartbeat_ms: u64,
    pub election_timeout_ms: u64,
    pub max_catchup: usize,
    pub mutation: Option<Mutation>,
}

impl Config {
    pub fn new(id: NodeId, members: Vec<NodeId>) -> Self {
        Self { id, members, heartbeat_ms: 50, election_timeout_ms: 300, max_catchup: 256, mutation: None }
    }
}

/// Durable acceptor state, for recovery after a crash.
#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct Durable<V> {
    pub promised: Ballot,
    pub accepted: BTreeMap<Slot, (Ballot, Cmd<V>)>,
}

impl<V> Default for Durable<V> {
    fn default() -> Self {
        Self { promised: Ballot::default(), accepted: BTreeMap::new() }
    }
}

impl<V: Clone> Durable<V> {
    /// Fold one persisted output into the durable image (what a WAL replay does).
    pub fn absorb(&mut self, out: &Output<V>) {
        match out {
            Output::PersistPromise { ballot } => self.promised = self.promised.max(*ballot),
            Output::PersistAccept { slot, ballot, cmd } => {
                self.promised = self.promised.max(*ballot);
                self.accepted.insert(*slot, (*ballot, cmd.clone()));
            }
            _ => {}
        }
    }
}

enum Role<V> {
    Follower,
    Candidate { ballot: Ballot, from: Slot, promises: BTreeMap<NodeId, Vec<(Slot, Ballot, Cmd<V>)>> },
    Leader { ballot: Ballot, next_slot: Slot, inflight: BTreeMap<Slot, (Cmd<V>, BTreeSet<NodeId>)> },
}

pub struct Replica<V> {
    cfg: Config,
    now: u64,
    // acceptor
    promised: Ballot,
    accepted: BTreeMap<Slot, (Ballot, Cmd<V>)>,
    // learner
    chosen: BTreeMap<Slot, Cmd<V>>,
    next_deliver: Slot,
    // proposer
    max_seen: Ballot,
    role: Role<V>,
    leader_hint: Option<NodeId>,
    last_heard: u64,
    last_heartbeat: u64,
    election_started: u64,
    queue: VecDeque<V>,
    out: Vec<Output<V>>,
    local: VecDeque<(NodeId, Msg<V>)>,
}

impl<V: Clone + PartialEq + std::fmt::Debug> Replica<V> {
    pub fn new(cfg: Config) -> Self {
        Self::recover(cfg, Durable { promised: Ballot::default(), accepted: BTreeMap::new() })
    }

    /// Restart from durable acceptor state. Learner state is volatile and is rebuilt from the
    /// leader (`CatchUp`) or, if every replica restarted, by the next leader's phase 1.
    pub fn recover(cfg: Config, d: Durable<V>) -> Self {
        Self {
            cfg,
            now: 0,
            max_seen: d.promised,
            promised: d.promised,
            accepted: d.accepted,
            chosen: BTreeMap::new(),
            next_deliver: 1,
            role: Role::Follower,
            leader_hint: None,
            last_heard: 0,
            last_heartbeat: 0,
            election_started: 0,
            queue: VecDeque::new(),
            out: Vec::new(),
            local: VecDeque::new(),
        }
    }

    pub fn id(&self) -> NodeId {
        self.cfg.id
    }

    pub fn is_leader(&self) -> bool {
        matches!(self.role, Role::Leader { .. })
    }

    pub fn leader_hint(&self) -> Option<NodeId> {
        self.leader_hint
    }

    /// The first slot not yet delivered.
    pub fn next_deliver(&self) -> Slot {
        self.next_deliver
    }

    pub fn handle(&mut self, input: Input<V>) -> Vec<Output<V>> {
        match input {
            Input::Propose(v) => self.propose(v),
            Input::Receive { from, msg } => self.on_msg(from, msg),
            Input::Tick { now_ms } => {
                self.now = self.now.max(now_ms);
                self.tick();
            }
        }
        while let Some((from, msg)) = self.local.pop_front() {
            self.on_msg(from, msg);
        }
        std::mem::take(&mut self.out)
    }

    // ---- plumbing ----------------------------------------------------------------------------

    fn majority(&self) -> usize {
        self.cfg.members.len() / 2 + 1
    }

    fn send(&mut self, to: NodeId, msg: Msg<V>) {
        if to == self.cfg.id {
            self.local.push_back((to, msg));
        } else {
            self.out.push(Output::Send { to, msg });
        }
    }

    fn broadcast(&mut self, msg: Msg<V>) {
        for to in self.cfg.members.clone() {
            self.send(to, msg.clone());
        }
    }

    fn election_timeout(&self) -> u64 {
        // Deterministic stagger so replicas do not duel forever.
        let rank = self.cfg.members.iter().position(|m| *m == self.cfg.id).unwrap_or(0) as u64;
        let n = self.cfg.members.len().max(1) as u64;
        self.cfg.election_timeout_ms + rank * self.cfg.election_timeout_ms / n
    }

    fn role_ballot(&self) -> Option<Ballot> {
        match &self.role {
            Role::Follower => None,
            Role::Candidate { ballot, .. } | Role::Leader { ballot, .. } => Some(*ballot),
        }
    }

    /// Note a ballot seen on the wire; step down if someone is ahead of us.
    fn observe(&mut self, b: Ballot) {
        if b > self.max_seen {
            self.max_seen = b;
        }
        if self.role_ballot().is_some_and(|mine| b > mine) {
            self.step_down();
        }
    }

    /// Values in flight are *not* re-queued. Some were inherited through phase 1 and the next
    /// leader recovers them the same way; re-queuing would duplicate the backlog at every
    /// leadership change. A value that is simply lost is retried by the host, which proposes
    /// under an idempotent entry id (liveness is the host's; safety is here).
    fn step_down(&mut self) {
        self.role = Role::Follower;
    }

    fn flush_queue(&mut self) {
        if self.is_leader() {
            while let Some(v) = self.queue.pop_front() {
                self.propose(v);
            }
        } else if let Some(l) = self.leader_hint.filter(|l| *l != self.cfg.id) {
            while let Some(v) = self.queue.pop_front() {
                self.send(l, Msg::Forward { value: v });
            }
        }
    }

    // ---- proposer ----------------------------------------------------------------------------

    fn propose(&mut self, v: V) {
        match &mut self.role {
            Role::Leader { ballot, next_slot, inflight } => {
                let (b, slot) = (*ballot, *next_slot);
                *next_slot += 1;
                inflight.insert(slot, (Cmd::Value(v.clone()), BTreeSet::new()));
                self.broadcast(Msg::Accept { ballot: b, slot, cmd: Cmd::Value(v) });
            }
            _ => {
                self.queue.push_back(v);
                self.flush_queue();
            }
        }
    }

    fn start_election(&mut self) {
        let ballot = Ballot { round: self.max_seen.round + 1, node: self.cfg.id };
        self.max_seen = ballot;
        self.step_down();
        self.role = Role::Candidate { ballot, from: self.next_deliver, promises: BTreeMap::new() };
        self.election_started = self.now;
        self.leader_hint = None;
        self.broadcast(Msg::Prepare { ballot, from_slot: self.next_deliver });
    }

    fn become_leader(&mut self, ballot: Ballot, from: Slot, promises: BTreeMap<NodeId, Vec<(Slot, Ballot, Cmd<V>)>>) {
        // Phase 1's purpose: for every slot, adopt the value accepted at the highest ballot.
        let mut merged: BTreeMap<Slot, (Ballot, Cmd<V>)> = BTreeMap::new();
        if self.cfg.mutation != Some(Mutation::IgnorePromisedValues) {
            for (slot, b, cmd) in promises.into_values().flatten() {
                if merged.get(&slot).is_none_or(|(mb, _)| b > *mb) {
                    merged.insert(slot, (b, cmd));
                }
            }
        }
        let top = merged.keys().next_back().copied().unwrap_or(0).max(from.saturating_sub(1));
        let mut inflight = BTreeMap::new();
        let mut accepts = Vec::new();
        for slot in from..=top {
            let cmd = match (self.chosen.get(&slot), merged.remove(&slot)) {
                (Some(c), _) => c.clone(),
                (None, Some((_, c))) => c,
                (None, None) => Cmd::Noop,
            };
            inflight.insert(slot, (cmd.clone(), BTreeSet::new()));
            accepts.push(Msg::Accept { ballot, slot, cmd });
        }
        self.role = Role::Leader { ballot, next_slot: top + 1, inflight };
        self.leader_hint = Some(self.cfg.id);
        for m in accepts {
            self.broadcast(m);
        }
        self.last_heartbeat = self.now;
        self.broadcast(Msg::Heartbeat { ballot, next: self.next_deliver });
        self.flush_queue();
    }

    // ---- learner -----------------------------------------------------------------------------

    fn learn(&mut self, slot: Slot, cmd: Cmd<V>) {
        if slot < self.next_deliver {
            return;
        }
        if self.chosen.contains_key(&slot) {
            // A second, different value here would be an agreement violation; the protocol
            // rules it out and the simulation checks it. Not asserted, so mutation runs report
            // the violation through the checker instead of aborting.
            return;
        }
        self.chosen.insert(slot, cmd);
        while let Some(c) = self.chosen.get(&self.next_deliver) {
            if let Cmd::Value(v) = c {
                self.out.push(Output::Deliver { slot: self.next_deliver, value: v.clone() });
            }
            self.next_deliver += 1;
        }
    }

    // ---- messages ----------------------------------------------------------------------------

    fn on_msg(&mut self, from: NodeId, msg: Msg<V>) {
        match msg {
            Msg::Prepare { ballot, from_slot } => {
                if ballot >= self.promised {
                    if ballot > self.promised {
                        self.promised = ballot;
                        self.out.push(Output::PersistPromise { ballot });
                    }
                    self.observe(ballot);
                    let accepted = self.accepted.range(from_slot..).map(|(s, (b, c))| (*s, *b, c.clone())).collect();
                    self.send(from, Msg::Promise { ballot, accepted });
                } else {
                    self.send(from, Msg::Nack { rejected: ballot, promised: self.promised });
                }
            }
            Msg::Promise { ballot, accepted } => {
                let majority = self.majority();
                let ready = match &mut self.role {
                    Role::Candidate { ballot: b, promises, .. } if *b == ballot => {
                        promises.insert(from, accepted);
                        promises.len() >= majority
                    }
                    _ => false,
                };
                if ready
                    && let Role::Candidate { ballot, from, promises } =
                        std::mem::replace(&mut self.role, Role::Follower)
                {
                    self.become_leader(ballot, from, promises);
                }
            }
            Msg::Nack { rejected, promised } => {
                if self.role_ballot() == Some(rejected) {
                    self.observe(promised);
                }
            }
            Msg::Accept { ballot, slot, cmd } => {
                let below = ballot < self.promised;
                if !below || self.cfg.mutation == Some(Mutation::AcceptBelowPromise) {
                    if ballot > self.promised {
                        self.promised = ballot;
                    }
                    self.accepted.insert(slot, (ballot, cmd.clone()));
                    self.out.push(Output::PersistAccept { slot, ballot, cmd });
                    self.observe(ballot);
                    if from != self.cfg.id {
                        self.leader_hint = Some(ballot.node);
                        self.last_heard = self.now;
                    }
                    self.send(from, Msg::Accepted { ballot, slot });
                } else {
                    self.send(from, Msg::Nack { rejected: ballot, promised: self.promised });
                }
            }
            Msg::Accepted { ballot, slot } => {
                let majority = self.majority();
                let mut commit = None;
                if let Role::Leader { ballot: b, inflight, .. } = &mut self.role
                    && *b == ballot
                    && let Some((cmd, acks)) = inflight.get_mut(&slot)
                {
                    acks.insert(from);
                    if acks.len() >= majority {
                        commit = Some(cmd.clone());
                        inflight.remove(&slot);
                    }
                }
                if let Some(cmd) = commit {
                    self.broadcast(Msg::Commit { slot, cmd });
                }
            }
            Msg::Commit { slot, cmd } => self.learn(slot, cmd),
            Msg::Heartbeat { ballot, next } => {
                if ballot >= self.max_seen {
                    self.observe(ballot);
                    if ballot.node != self.cfg.id {
                        self.leader_hint = Some(ballot.node);
                        self.last_heard = self.now;
                        self.flush_queue();
                        if next > self.next_deliver {
                            self.send(from, Msg::CatchUp { from_slot: self.next_deliver });
                        }
                    }
                }
            }
            Msg::CatchUp { from_slot } => {
                if from_slot >= self.next_deliver {
                    return; // the asker is not behind us
                }
                let batch: Vec<(Slot, Cmd<V>)> = self
                    .chosen
                    .range(from_slot..self.next_deliver)
                    .take(self.cfg.max_catchup)
                    .map(|(s, c)| (*s, c.clone()))
                    .collect();
                for (slot, cmd) in batch {
                    self.send(from, Msg::Commit { slot, cmd });
                }
            }
            // Only a leader acts on a forward. Anyone else queues it until it hears from a leader;
            // re-forwarding on a stale hint lets two replicas bounce a value between them.
            Msg::Forward { value } => {
                if self.is_leader() {
                    self.propose(value);
                } else {
                    self.queue.push_back(value);
                }
            }
        }
    }

    fn tick(&mut self) {
        match &self.role {
            Role::Leader { ballot, inflight, .. } => {
                if self.now.saturating_sub(self.last_heartbeat) >= self.cfg.heartbeat_ms {
                    let b = *ballot;
                    // Retransmit what is not yet chosen: the network may drop anything.
                    let resend: Vec<Msg<V>> = inflight
                        .iter()
                        .map(|(s, (c, _))| Msg::Accept { ballot: b, slot: *s, cmd: c.clone() })
                        .collect();
                    self.last_heartbeat = self.now;
                    self.broadcast(Msg::Heartbeat { ballot: b, next: self.next_deliver });
                    for m in resend {
                        self.broadcast(m);
                    }
                }
            }
            Role::Candidate { .. } => {
                if self.now.saturating_sub(self.election_started) >= self.election_timeout() {
                    self.start_election();
                }
            }
            Role::Follower => {
                if self.now.saturating_sub(self.last_heard) >= self.election_timeout() {
                    self.start_election();
                }
            }
        }
    }
}
