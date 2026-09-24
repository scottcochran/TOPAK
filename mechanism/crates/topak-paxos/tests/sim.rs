//! Deterministic simulation of the sans-IO replicas under a hostile network.
//!
//! Every run checks, at every step:
//! - `OneValuePerBallot` and chosen-uniqueness on the `Voting` ghost, fed from durable votes;
//! - agreement: no two replicas deliver different values for one slot;
//! - learner soundness: every delivered value is the one the ghost says was chosen.
//!
//! Then the network heals and every proposal must be delivered everywhere (liveness).
//! Each `Mutation` must make some seed fail — otherwise the checks are vacuous.

use std::collections::{BTreeMap, BTreeSet};

use topak_paxos::voting::Voting;
use topak_paxos::*;

/// xorshift64*: tiny, seedable, no dependency.
struct Rng(u64);
impl Rng {
    fn next(&mut self) -> u64 {
        self.0 ^= self.0 >> 12;
        self.0 ^= self.0 << 25;
        self.0 ^= self.0 >> 27;
        self.0.wrapping_mul(0x2545F4914F6CDD1D)
    }
    fn below(&mut self, n: u64) -> u64 {
        self.next() % n
    }
    fn chance(&mut self, pct: u64) -> bool {
        self.below(100) < pct
    }
}

struct Node {
    replica: Replica<u64>,
    durable: Durable<u64>,
    up: bool,
    delivered: BTreeMap<Slot, u64>,
}

struct Sim {
    rng: Rng,
    now: u64,
    nodes: BTreeMap<NodeId, Node>,
    net: Vec<(u64, NodeId, NodeId, Msg<u64>)>,
    cut: BTreeSet<NodeId>,
    ghost: Voting<u64>,
    decided: BTreeMap<Slot, u64>,
    proposed: BTreeSet<u64>,
    hostile: bool,
    cfg: Config,
}

impl Sim {
    fn new(seed: u64, n: u32, mutation: Option<Mutation>) -> Self {
        let members: Vec<NodeId> = (1..=n).collect();
        let mut cfg = Config::new(0, members.clone());
        cfg.mutation = mutation;
        let nodes = members
            .iter()
            .map(|id| {
                let mut c = cfg.clone();
                c.id = *id;
                (
                    *id,
                    Node {
                        replica: Replica::new(c),
                        durable: Durable::default(),
                        up: true,
                        delivered: BTreeMap::new(),
                    },
                )
            })
            .collect();
        Sim {
            rng: Rng(seed.wrapping_mul(0x9E3779B97F4A7C15) | 1),
            now: 0,
            nodes,
            net: Vec::new(),
            cut: BTreeSet::new(),
            ghost: Voting::new(n as usize),
            decided: BTreeMap::new(),
            proposed: BTreeSet::new(),
            hostile: true,
            cfg,
        }
    }

    fn feed(&mut self, id: NodeId, input: Input<u64>) -> Result<(), String> {
        let node = self.nodes.get_mut(&id).unwrap();
        if !node.up {
            return Ok(());
        }
        let outs = node.replica.handle(input);
        for o in outs {
            match &o {
                Output::PersistPromise { .. } => self.nodes.get_mut(&id).unwrap().durable.absorb(&o),
                Output::PersistAccept { slot, ballot, cmd } => {
                    self.nodes.get_mut(&id).unwrap().durable.absorb(&o);
                    self.ghost.vote(id, *slot, *ballot, cmd)?;
                }
                Output::Send { to, msg } => {
                    let hostile = self.hostile;
                    if hostile && self.rng.chance(8) {
                        continue; // drop
                    }
                    let copies = if hostile && self.rng.chance(4) { 2 } else { 1 };
                    for _ in 0..copies {
                        let delay = 1 + if hostile { self.rng.below(40) } else { self.rng.below(5) };
                        self.net.push((self.now + delay, id, *to, msg.clone()));
                    }
                }
                Output::Deliver { slot, value } => {
                    if let Some(prev) = self.decided.get(slot) {
                        if prev != value {
                            return Err(format!("Agreement: slot {slot} delivered {prev} and {value}"));
                        }
                    } else {
                        self.decided.insert(*slot, *value);
                    }
                    match self.ghost.chosen(*slot) {
                        Some(Cmd::Value(v)) if v == value => {}
                        other => return Err(format!("Learner: slot {slot} delivered {value}, ghost has {other:?}")),
                    }
                    self.nodes.get_mut(&id).unwrap().delivered.insert(*slot, *value);
                }
            }
        }
        Ok(())
    }

    fn step(&mut self) -> Result<(), String> {
        self.now += 1;
        // Deliver due messages.
        let (due, rest): (Vec<_>, Vec<_>) = std::mem::take(&mut self.net).into_iter().partition(|m| m.0 <= self.now);
        self.net = rest;
        for (_, from, to, msg) in due {
            if self.cut.contains(&from) != self.cut.contains(&to) {
                continue; // partitioned
            }
            self.feed(to, Input::Receive { from, msg })?;
        }
        let ids: Vec<NodeId> = self.nodes.keys().copied().collect();
        for id in &ids {
            self.feed(*id, Input::Tick { now_ms: self.now })?;
        }
        if self.hostile {
            // Proposals at random replicas.
            if self.rng.chance(6) {
                let v = self.proposed.len() as u64 + 1;
                self.proposed.insert(v);
                let at = ids[self.rng.below(ids.len() as u64) as usize];
                self.feed(at, Input::Propose(v))?;
            }
            // Partitions come and go.
            if self.rng.chance(1) {
                self.cut.clear();
                let at = ids[self.rng.below(ids.len() as u64) as usize];
                if self.rng.chance(50) {
                    self.cut.insert(at);
                }
            }
            // Crash rarely; a crashed replica restarts from durable state only.
            for id in &ids {
                let node = self.nodes.get_mut(id).unwrap();
                if node.up && self.rng.chance(1) && self.rng.chance(30) {
                    node.up = false;
                } else if !node.up && self.rng.chance(2) {
                    let mut c = self.cfg.clone();
                    c.id = *id;
                    node.replica = Replica::recover(c, node.durable.clone());
                    node.up = true;
                    node.delivered.clear();
                }
            }
        }
        Ok(())
    }

    /// Host-level retry, as the mechanism does: re-propose anything not yet decided.
    fn retry_undecided(&mut self) -> Result<(), String> {
        let decided: BTreeSet<u64> = self.decided.values().copied().collect();
        let missing: Vec<u64> = self.proposed.difference(&decided).copied().collect();
        let ids: Vec<NodeId> = self.nodes.keys().copied().collect();
        for v in missing {
            let at = ids[self.rng.below(ids.len() as u64) as usize];
            self.feed(at, Input::Propose(v))?;
        }
        Ok(())
    }

    fn run(&mut self, hostile_steps: u64, heal_steps: u64) -> Result<(), String> {
        for _ in 0..hostile_steps {
            self.step()?;
        }
        // Heal: everyone up, no partition, reliable-ish network.
        self.hostile = false;
        self.cut.clear();
        for (id, node) in self.nodes.iter_mut() {
            if !node.up {
                let mut c = self.cfg.clone();
                c.id = *id;
                node.replica = Replica::recover(c, node.durable.clone());
                node.up = true;
                node.delivered.clear();
            }
        }
        for i in 0..heal_steps {
            if i % 400 == 0 {
                self.retry_undecided()?;
            }
            self.step()?;
        }
        Ok(())
    }

    fn check_liveness(&self) -> Result<(), String> {
        let decided: BTreeSet<u64> = self.decided.values().copied().collect();
        let missing: Vec<_> = self.proposed.difference(&decided).collect();
        if !missing.is_empty() {
            return Err(format!("Liveness: {} proposals never decided", missing.len()));
        }
        for (id, node) in &self.nodes {
            let got: BTreeSet<u64> = node.delivered.values().copied().collect();
            // A recovered node rebuilds its learner state; after healing it must have caught up.
            if node.replica.next_deliver() <= *self.decided.keys().next_back().unwrap_or(&0) {
                return Err(format!(
                    "Liveness: node {id} stuck at slot {} ({} values)",
                    node.replica.next_deliver(),
                    got.len()
                ));
            }
        }
        Ok(())
    }
}

#[test]
fn safety_and_liveness_under_faults() {
    for seed in 0..60 {
        for n in [3, 5] {
            let mut sim = Sim::new(seed, n, None);
            sim.run(3_000, 6_000).unwrap_or_else(|e| panic!("seed {seed} n {n}: {e}"));
            sim.check_liveness().unwrap_or_else(|e| panic!("seed {seed} n {n}: {e}"));
            assert!(!sim.decided.is_empty(), "seed {seed}: nothing decided — the run is vacuous");
        }
    }
}

#[test]
fn a_leader_change_happens() {
    // Reachability witness: without one, safety could hold because leadership never moves.
    let mut changed = false;
    for seed in 0..20 {
        let mut sim = Sim::new(seed, 3, None);
        let mut leaders = BTreeSet::new();
        for _ in 0..3_000 {
            sim.step().unwrap();
            for (id, n) in &sim.nodes {
                if n.replica.is_leader() {
                    leaders.insert(*id);
                }
            }
        }
        changed |= leaders.len() > 1;
    }
    assert!(changed, "no seed ever changed leader");
}

fn mutation_is_caught(m: Mutation) {
    for seed in 0..400 {
        let mut sim = Sim::new(seed, 3, Some(m));
        if sim.run(3_000, 0).is_err() {
            return;
        }
    }
    panic!("{m:?} was never caught: the invariant checks are vacuous");
}

#[test]
fn mutation_ignore_promised_values_is_caught() {
    mutation_is_caught(Mutation::IgnorePromisedValues);
}

#[test]
fn mutation_accept_below_promise_is_caught() {
    mutation_is_caught(Mutation::AcceptBelowPromise);
}
