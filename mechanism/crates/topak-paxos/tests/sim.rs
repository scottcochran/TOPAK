//! Deterministic simulation of the sans-IO replicas under a hostile network.
//!
//! Every run checks, at every step:
//! - `OneValuePerBallot` and chosen-uniqueness on the `Voting` ghost, fed from durable votes;
//! - agreement: no two replicas deliver different values for one slot;
//! - learner soundness: every delivered value is the one the ghost says was chosen;
//! - no amplification (GAPS finding 9): a value sits in no more slots than the host handed it in
//!   plus the forwards of it the network duplicated.
//!
//! Then the network heals and every proposal must be delivered everywhere (liveness).
//! Each `Mutation` must make some seed fail — otherwise the checks are vacuous. So must a host
//! that restarts a replica without its durable state (`Opts::no_persist`).
//!
//! These are the properties of `spec/Paxos.tla`, restated. With `TOPAK_TRACE_DIR` set, the
//! `traced_*` tests also write what every replica did, one JSON line per call of `handle`, and
//! `spec/paxos-trace-run.sh` replays each file through that module (`spec/PaxosTrace.tla`).

use std::collections::{BTreeMap, BTreeSet};
use std::io::Write;

use serde_json::{Value, json};
use topak_paxos::voting::Voting;
use topak_paxos::*;

// ---- the trace, in the shapes `spec/Paxos.tla` gives a replica's state and its messages ---------
// Encoding, as `topak-core`'s recorder: {"$f": [[k, v], ...]} is a TLA+ function, {"$s": [...]} a
// set, an array a tuple, any other object a record. A ballot (round, node) is the number
// round * (n + 1) + node, and a command is its value, 0 for `Noop`: the module's encodings.

fn bal(n: u64, b: Ballot) -> u64 {
    b.round * (n + 1) + b.node as u64
}

fn cmd(c: &Cmd<u64>) -> u64 {
    match c {
        Cmd::Noop => 0,
        Cmd::Value(v) => *v,
    }
}

fn triples(n: u64, acc: &[(Slot, Ballot, Cmd<u64>)]) -> Value {
    json!({ "$s": acc.iter().map(|(s, b, c)| json!([s, bal(n, *b), cmd(c)])).collect::<Vec<_>>() })
}

fn msg_json(n: u64, from: NodeId, to: NodeId, m: &Msg<u64>) -> Value {
    match m {
        Msg::Prepare { ballot, from_slot } => {
            json!({"type": "prepare", "from": from, "to": to, "bal": bal(n, *ballot), "slot": from_slot})
        }
        Msg::Promise { ballot, accepted } => {
            json!({"type": "promise", "from": from, "to": to, "bal": bal(n, *ballot), "acc": triples(n, accepted)})
        }
        Msg::Nack { rejected, promised } => {
            json!({"type": "nack", "from": from, "to": to, "rejected": bal(n, *rejected), "promised": bal(n, *promised)})
        }
        Msg::Accept { ballot, slot, cmd: c } => {
            json!({"type": "accept", "from": from, "to": to, "bal": bal(n, *ballot), "slot": slot, "cmd": cmd(c)})
        }
        Msg::Accepted { ballot, slot } => {
            json!({"type": "accepted", "from": from, "to": to, "bal": bal(n, *ballot), "slot": slot})
        }
        Msg::Commit { slot, cmd: c } => json!({"type": "commit", "from": from, "to": to, "slot": slot, "cmd": cmd(c)}),
        Msg::Heartbeat { ballot, next } => {
            json!({"type": "heartbeat", "from": from, "to": to, "bal": bal(n, *ballot), "next": next})
        }
        Msg::CatchUp { from_slot } => json!({"type": "catchup", "from": from, "to": to, "slot": from_slot}),
        Msg::Forward { value } => json!({"type": "forward", "from": from, "to": to, "value": value}),
    }
}

fn state_json(n: u64, s: &Snapshot<u64>) -> Value {
    let (role, b, from, promises, next_slot, inflight) = match &s.role {
        RoleSnapshot::Follower => ("follower", 0, 0, vec![], 0, vec![]),
        RoleSnapshot::Candidate { ballot, from, promises } => (
            "candidate",
            bal(n, *ballot),
            *from,
            promises.iter().map(|(a, acc)| json!([a, triples(n, acc)])).collect(),
            0,
            vec![],
        ),
        RoleSnapshot::Leader { ballot, next_slot, inflight } => (
            "leader",
            bal(n, *ballot),
            0,
            vec![],
            *next_slot,
            inflight.iter().map(|(sl, c, acks)| json!([sl, {"cmd": cmd(c), "acks": {"$s": acks}}])).collect(),
        ),
    };
    json!({
        "promised": bal(n, s.promised),
        "accepted": {"$f": s.accepted.iter().map(|(sl, b, c)| json!([sl, [bal(n, *b), cmd(c)]])).collect::<Vec<_>>()},
        "chosen": {"$f": s.chosen.iter().map(|(sl, c)| json!([sl, cmd(c)])).collect::<Vec<_>>()},
        "maxSeen": bal(n, s.max_seen),
        "role": role,
        "bal": b,
        "from": from,
        "promises": {"$f": promises},
        "nextSlot": next_slot,
        "inflight": {"$f": inflight},
        "hint": s.leader_hint.unwrap_or(0),
        "queue": s.queue,
    })
}

/// What a mutation of the code is called in the module.
fn mut_name(m: Option<Mutation>, no_persist: bool) -> &'static str {
    match (m, no_persist) {
        (None, false) => "none",
        (None, true) => "M_NOPERSIST",
        (Some(Mutation::IgnorePromisedValues), _) => "M_IGNOREPROMISED",
        (Some(Mutation::AcceptBelowPromise), _) => "M_BELOWPROMISE",
        (Some(Mutation::RequeueOnStepDown), _) => "M_REQUEUE",
    }
}

/// How a simulation differs from the default one.
#[derive(Clone, Default)]
struct Opts {
    /// (heartbeat, election timeout), for a short run that still changes leader.
    timing: Option<(u64, u64)>,
    /// The host restarts a replica without its durable state: it sent before it persisted.
    no_persist: bool,
    /// Record the run as `$TOPAK_TRACE_DIR/<name>.jsonl`, when that variable is set.
    trace: Option<String>,
}

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
    no_persist: bool,
    /// Per value: times the host handed it in, forwards of it the network duplicated, and the
    /// slots it has been proposed in.
    handed: BTreeMap<u64, u64>,
    duped: BTreeMap<u64, u64>,
    slots: BTreeMap<u64, BTreeSet<Slot>>,
    rec: Option<std::io::BufWriter<std::fs::File>>,
}

impl Sim {
    fn new(seed: u64, n: u32, mutation: Option<Mutation>) -> Self {
        Self::with(seed, n, mutation, Opts::default())
    }

    fn with(seed: u64, n: u32, mutation: Option<Mutation>, opts: Opts) -> Self {
        let members: Vec<NodeId> = (1..=n).collect();
        let mut cfg = Config::new(0, members.clone());
        cfg.mutation = mutation;
        if let Some((heartbeat, election)) = opts.timing {
            cfg.heartbeat_ms = heartbeat;
            cfg.election_timeout_ms = election;
        }
        let rec = opts.trace.as_ref().and_then(|name| {
            let dir = std::env::var("TOPAK_TRACE_DIR").ok()?;
            let file = std::fs::File::create(std::path::Path::new(&dir).join(format!("{name}.jsonl")))
                .expect("TOPAK_TRACE_DIR is a writable directory");
            let mut w = std::io::BufWriter::new(file);
            writeln!(w, "{}", json!({"init": {"n": n, "mut": mut_name(mutation, opts.no_persist)}})).unwrap();
            Some(w)
        });
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
            no_persist: opts.no_persist,
            handed: BTreeMap::new(),
            duped: BTreeMap::new(),
            slots: BTreeMap::new(),
            rec,
        }
    }

    fn n(&self) -> u64 {
        self.cfg.members.len() as u64
    }

    fn record(&mut self, event: Value) {
        if let Some(w) = &mut self.rec {
            writeln!(w, "{event}").unwrap();
        }
    }

    /// A crashed replica restarts from durable state only, or from nothing if the host is broken.
    fn restart(&mut self, id: NodeId) {
        let n = self.n();
        let mut c = self.cfg.clone();
        c.id = id;
        let node = self.nodes.get_mut(&id).unwrap();
        if self.no_persist {
            node.durable = Durable::default();
        }
        node.replica = Replica::recover(c, node.durable.clone());
        node.up = true;
        node.delivered.clear();
        let after = state_json(n, &node.replica.snapshot());
        self.record(json!({"ev": "crash", "node": id, "after": after}));
    }

    fn feed(&mut self, id: NodeId, input: Input<u64>) -> Result<(), String> {
        let n = self.n();
        let node = self.nodes.get_mut(&id).unwrap();
        if !node.up {
            return Ok(());
        }
        if let Input::Propose(v) = &input {
            *self.handed.entry(*v).or_default() += 1;
        }
        let before = self.rec.as_ref().map(|_| (node.replica.snapshot(), input.clone()));
        let outs = node.replica.handle(input);
        let after = before.as_ref().map(|_| node.replica.snapshot());
        let (mut sent, mut fwds, mut dups) = (Vec::new(), Vec::new(), Vec::new());
        let mut touched = BTreeSet::new();
        // The first check this call fails. The call is still recorded, so that a trace of a
        // mutated run ends with the event that broke the property.
        let mut failed: Option<String> = None;
        for o in outs {
            match &o {
                Output::PersistPromise { .. } => self.nodes.get_mut(&id).unwrap().durable.absorb(&o),
                Output::PersistAccept { slot, ballot, cmd } => {
                    self.nodes.get_mut(&id).unwrap().durable.absorb(&o);
                    if let Err(e) = self.ghost.vote(id, *slot, *ballot, cmd) {
                        failed.get_or_insert(e);
                    }
                    if let Cmd::Value(v) = cmd {
                        self.slots.entry(*v).or_default().insert(*slot);
                        touched.insert(*v);
                    }
                }
                Output::Send { to, msg } => {
                    match msg {
                        Msg::Forward { value } => fwds.push(json!([to, value])),
                        _ => sent.push(msg_json(n, id, *to, msg)),
                    }
                    let hostile = self.hostile;
                    if hostile && self.rng.chance(8) {
                        continue; // drop
                    }
                    let copies = if hostile && self.rng.chance(4) { 2 } else { 1 };
                    if let (2, Msg::Forward { value }) = (copies, msg) {
                        *self.duped.entry(*value).or_default() += 1;
                        dups.push(json!({"ev": "dup", "from": id, "to": to, "value": value}));
                    }
                    for _ in 0..copies {
                        let delay = 1 + if hostile { self.rng.below(40) } else { self.rng.below(5) };
                        self.net.push((self.now + delay, id, *to, msg.clone()));
                    }
                }
                Output::Deliver { slot, value } => {
                    if let Some(prev) = self.decided.get(slot) {
                        if prev != value {
                            failed.get_or_insert(format!("Agreement: slot {slot} delivered {prev} and {value}"));
                        }
                    } else {
                        self.decided.insert(*slot, *value);
                    }
                    match self.ghost.chosen(*slot) {
                        Some(Cmd::Value(v)) if v == value => {}
                        other => {
                            failed
                                .get_or_insert(format!("Learner: slot {slot} delivered {value}, ghost has {other:?}"));
                        }
                    }
                    self.nodes.get_mut(&id).unwrap().delivered.insert(*slot, *value);
                }
            }
        }
        if let (Some((before, input)), Some(after)) = (before, after) {
            // A tick is an election if the replica has a new ballot of its own, a heartbeat if it
            // sent anything, and otherwise nothing: the model has no clock, so nothing is recorded.
            let own = |s: &Snapshot<u64>| match &s.role {
                RoleSnapshot::Follower => None,
                RoleSnapshot::Candidate { ballot, .. } | RoleSnapshot::Leader { ballot, .. } => Some(*ballot),
            };
            let what = match &input {
                Input::Propose(v) => Some(json!({"ev": "hand", "value": v})),
                Input::Receive { from, msg: Msg::Forward { value } } => {
                    Some(json!({"ev": "fwd", "from": from, "value": value}))
                }
                Input::Receive { from, msg } => Some(json!({"ev": "recv", "msg": msg_json(n, *from, id, msg)})),
                Input::Tick { .. } if own(&after) != own(&before) => Some(json!({"ev": "elect"})),
                Input::Tick { .. } if !sent.is_empty() => Some(json!({"ev": "beat"})),
                Input::Tick { .. } => {
                    assert_eq!(before, after, "a tick that sent nothing changed the replica");
                    None
                }
            };
            if let Some(mut event) = what {
                let fields = event.as_object_mut().unwrap();
                fields.insert("node".into(), json!(id));
                fields.insert("after".into(), state_json(n, &after));
                fields.insert("nextDeliver".into(), json!(after.next_deliver));
                fields.insert("sent".into(), json!({ "$s": sent }));
                fields.insert("fwds".into(), json!(fwds));
                self.record(event);
            }
            for d in dups {
                self.record(d);
            }
        }
        for v in touched {
            let (in_slots, handed, duped) = (
                self.slots[&v].len() as u64,
                self.handed.get(&v).copied().unwrap_or(0),
                self.duped.get(&v).copied().unwrap_or(0),
            );
            if in_slots > handed + duped {
                failed.get_or_insert(format!(
                    "NoAmplification: value {v} is in {in_slots} slots, handed in {handed} times, {duped} forwards duplicated"
                ));
            }
        }
        failed.map_or(Ok(()), Err)
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
                    self.restart(*id);
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
        let down: Vec<NodeId> = self.nodes.iter().filter(|(_, node)| !node.up).map(|(id, _)| *id).collect();
        for id in down {
            self.restart(id);
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

/// The first seed whose run under the mutation fails, and the check that failed.
fn first_caught(m: Option<Mutation>, opts: &Opts, hostile_steps: u64) -> Option<(u64, String)> {
    (0..400).find_map(|seed| Sim::with(seed, 3, m, opts.clone()).run(hostile_steps, 0).err().map(|e| (seed, e)))
}

fn mutation_is_caught(m: Mutation) {
    if first_caught(Some(m), &Opts::default(), 3_000).is_none() {
        panic!("{m:?} was never caught: the invariant checks are vacuous");
    }
}

#[test]
fn mutation_ignore_promised_values_is_caught() {
    mutation_is_caught(Mutation::IgnorePromisedValues);
}

#[test]
fn mutation_accept_below_promise_is_caught() {
    mutation_is_caught(Mutation::AcceptBelowPromise);
}

#[test]
fn mutation_requeue_on_step_down_is_caught() {
    // GAPS finding 9. Only the amplification check can see it: the log stays a log.
    let (_, e) = first_caught(Some(Mutation::RequeueOnStepDown), &Opts::default(), 3_000)
        .expect("RequeueOnStepDown was never caught: the amplification check is vacuous");
    assert!(e.starts_with("NoAmplification"), "caught by another check: {e}");
}

#[test]
fn a_host_that_does_not_persist_is_caught() {
    // lib.rs: recovery is safe only if every `Persist*` is durable before the `Send` after it.
    let opts = Opts { no_persist: true, ..Opts::default() };
    assert!(first_caught(None, &opts, 3_000).is_some(), "a host without durable state was never caught");
}

// ---- traced runs, for `spec/PaxosTrace.tla` -----------------------------------------------------
// Short runs with short timeouts, so that a file holds elections, restarts, forwards and catch-ups
// and is still small enough to replay. Without `TOPAK_TRACE_DIR` they run and record nothing.

/// Hostile steps, then steps after the network heals.
const TRACED_STEPS: (u64, u64) = (150, 100);
/// (heartbeat, election timeout) of the three-replica runs and of the mutated ones.
const TRACED_TIMING: (u64, u64) = (5, 30);
/// The unmutated runs: replicas, seed, timing. Chosen from seeds 0..150 for what the run holds:
/// seeds 78 and 101 for restarts with forwards and catch-ups, seed 48 for a forward the network
/// duplicated. With five replicas a run this short decides nothing while the network is hostile,
/// so that one has a long election timeout and does its work after the heal, with five restarts
/// before it.
const TRACED: [(u32, u64, (u64, u64)); 4] =
    [(3, 78, TRACED_TIMING), (3, 101, TRACED_TIMING), (3, 48, TRACED_TIMING), (5, 29, (10, 150))];

#[test]
fn traced_runs_under_faults() {
    for (n, seed, timing) in TRACED {
        let trace = Some(format!("paxos-none-n{n}-seed{seed}"));
        let mut sim = Sim::with(seed, n, None, Opts { timing: Some(timing), trace, ..Opts::default() });
        sim.run(TRACED_STEPS.0, TRACED_STEPS.1).unwrap_or_else(|e| panic!("seed {seed} n {n}: {e}"));
        assert!(!sim.decided.is_empty(), "seed {seed} n {n}: nothing decided");
    }
}

/// One traced run per mutation: the first seed a check catches, recorded up to the step that
/// catches it. Replayed under `Mut = "none"` it must not match, and under its own mutation it must.
#[test]
fn traced_runs_under_each_mutation() {
    let cases = [
        (Some(Mutation::IgnorePromisedValues), false),
        (Some(Mutation::AcceptBelowPromise), false),
        (Some(Mutation::RequeueOnStepDown), false),
        (None, true),
    ];
    for (m, no_persist) in cases {
        let mut opts = Opts { timing: Some(TRACED_TIMING), no_persist, trace: None };
        let name = mut_name(m, no_persist);
        let (seed, _) = first_caught(m, &opts, 600).unwrap_or_else(|| panic!("{name} was never caught in a short run"));
        opts.trace = Some(format!("paxos-{name}-n3-seed{seed}"));
        assert!(Sim::with(seed, 3, m, opts).run(600, 0).is_err(), "{name}: seed {seed} is not deterministic");
    }
}
