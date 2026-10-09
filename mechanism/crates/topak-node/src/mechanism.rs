//! The admit path and effect execution for one replica.
//!
//! For every agent action, in this order:
//!
//! 1. **Session → request.** The session token names the seat, lease and epoch. Every action
//!    carries all three (ADR-0022 §2).
//! 2. **Local expiry** on this replica's monotonic clock, with the asymmetric margin
//!    (ADR-0032). A liveness check: the fence below is what carries safety.
//! 3. **Mechanism checks** (`State::check_live`): epoch fence first, then the lease, alphabet,
//!    round bound, and action preconditions. Not policy.
//! 4. **Lift** into one frozen input.
//! 5. **Floor** (Cedar, linked). Deny or any error short-circuits.
//! 6. **Bundle** (OPA sidecar, WASM fallback bound to the lease's bundle). Can only refuse.
//! 7. **Order**: propose `Admit`, wait for commit. `apply` re-runs step 3 at the committed
//!    position; an admit fenced in between is void.
//! 8. **Effect**, only after commit, only on the deciding replica.
//!
//! Denials are never ordered (ADR-0015). Each is written to the principal's round topic while
//! that topic is open (ADR-0020: the replayable record includes actions attempted and denied),
//! by the deciding replica, and logged locally with attribution.
//!
//! A session is a bearer token for an operator's grant (I14), or, for a launched guest, the lease
//! itself: the bridge holds it at rung 1, and at rungs 2 and 3 every action carries the attested
//! guest's proof (ADR-0034 §3.5; `launch.rs`).

mod launch;
pub use launch::{Contain, GuestCtl};

use std::collections::{BTreeMap, HashMap};
use std::future::Future;
use std::io::Write;
use std::path::{Path, PathBuf};
use std::pin::Pin;
use std::sync::atomic::{AtomicBool, AtomicU64, Ordering};
use std::sync::{Arc, Mutex, RwLock, Weak};
use std::time::{Duration, Instant};

use serde_json::{Value, json};
use tokio::sync::{mpsc, oneshot};
use topak_core::control::{Activation, CONTROL_PURPOSE, Control, ControlAction, ControlRequest, Envelope};
use topak_core::lift::lift_control;
use topak_core::labels::{Delivery, Handle, Label, LabelFacts, RoundLabels};
use topak_bundle::BundleTier;
use topak_core::action::{Action, ActionRequest, tool_id};
use topak_core::admit::{BundleOutcome, Decision, DenyReason, compose, floor_gate};
use topak_core::clock::{MonoMillis, MonotonicClock, SystemMonotonic, subtracting_interval_elapsed};
use topak_core::confine::{AGENT_OP_PURPOSE, SessionProof, session_body};
use topak_core::lift::{self, after_topic_name, lift, topic_name, workspace_id, workspace_relative};
use topak_core::promotion::tally;
use topak_core::state::*;
use topak_core::*;
use topak_floor::Floor;
use topak_mcp::proto::{AgentOp, AgentRequest, AgentResponse};
use topak_mcp::toolhost::ToolHost;
use topak_paxos::NodeId;
use topak_transport::{EmitRecord, RecordKind, Transport};

use crate::ops::OperatorOp;

pub type BoxFuture<'a, T> = Pin<Box<dyn Future<Output = T> + Send + 'a>>;

/// The bundle tier as the mechanism sees it.
pub trait BundleDecider: Send + Sync {
    fn decide<'a>(&'a self, lease_bundle: &'a Digest, input: &'a Value) -> BoxFuture<'a, BundleOutcome>;
    /// ADR-0044 §3: whether this revision's signature verified at load. A grant naming one that
    /// did not is refused before it is proposed.
    fn verified(&self, rev: &Digest) -> bool;
    /// The channel the allowlist entry `tool` (`name@digest`) of revision `rev` declares: the one
    /// statement of where a Run tool may connect (ADR-0049 §5), read by the tool host.
    fn channel(&self, rev: &Digest, tool: &str) -> Option<topak_contain::wasmtool::Channel>;
    /// The tool list of a lease on `rev` (ADR-0048 §2): that revision's entries for `domain`
    /// whose key is in `callable`, rendered in the mechanism's fixed form.
    fn tool_list(&self, rev: &Digest, domain: Domain, callable: &std::collections::BTreeSet<String>) -> Value;
    /// What the mechanism computes about a `Consult` or an `Actuate` before the floor sees it
    /// (ADR-0047 §4): the labels `rev` declares, joined over the round's. `kind` is the seat's.
    fn label_facts(
        &self,
        rev: &Digest,
        kind: &str,
        action: &Action,
        round: &RoundLabels,
    ) -> Result<Option<LabelFacts>, String>;
    /// The declared type of each input of the entry `tool` in `rev`, for resolving a handle
    /// (ADR-0049 §3): the item a handle names must match the input's type.
    fn input_types(&self, rev: &Digest, tool: &str) -> BTreeMap<String, String>;
    /// The keys of the Run entries of `rev`: what an emergency seating whose envelope is the
    /// domain's is given from that revision (ADR-0052 §2).
    fn run_entries(&self, rev: &Digest) -> std::collections::BTreeSet<String>;
}

impl BundleDecider for BundleTier {
    fn decide<'a>(&'a self, lease_bundle: &'a Digest, input: &'a Value) -> BoxFuture<'a, BundleOutcome> {
        Box::pin(BundleTier::decide(self, lease_bundle, input))
    }
    fn verified(&self, rev: &Digest) -> bool {
        BundleTier::verified(self, rev)
    }
    fn channel(&self, rev: &Digest, tool: &str) -> Option<topak_contain::wasmtool::Channel> {
        let c = self.entry(rev, tool)?.channel.as_ref()?;
        Some(topak_contain::wasmtool::Channel { kind: c.kind.clone(), target: c.target.clone() })
    }
    fn tool_list(&self, rev: &Digest, domain: Domain, callable: &std::collections::BTreeSet<String>) -> Value {
        BundleTier::tool_list(self, rev, domain, callable)
    }
    fn label_facts(
        &self,
        rev: &Digest,
        kind: &str,
        action: &Action,
        round: &RoundLabels,
    ) -> Result<Option<LabelFacts>, String> {
        BundleTier::label_facts(self, rev, kind, action, round)
    }
    fn input_types(&self, rev: &Digest, tool: &str) -> BTreeMap<String, String> {
        let inputs = self.entry(rev, tool).map(|e| &e.inputs);
        inputs.into_iter().flatten().map(|(f, i)| (f.clone(), i.ty.clone())).collect()
    }
    fn run_entries(&self, rev: &Digest) -> std::collections::BTreeSet<String> {
        BundleTier::run_entries(self, rev)
    }
}

/// A session: what a bearer token stands for on this replica.
#[derive(Clone, Debug)]
pub struct Session {
    pub seat: SeatId,
    pub fence: LogIndex,
    pub epoch: Epoch,
}

pub struct Parts {
    pub id: NodeId,
    pub params: Params,
    pub genesis: State,
    pub floor: Floor,
    pub bundle: Box<dyn BundleDecider>,
    pub transport: Transport,
    pub tools: ToolHost,
    /// Tools run as Wasm modules (`topak-contain` `wasmtool`): Run's channel fidelity by
    /// construction (ADR-0034 A2, pending). Must host every id `Params::wasm_tools` names.
    pub wasm_tools: Option<Arc<topak_contain::wasmtool::WasmToolHost>>,
    pub corpus_dir: PathBuf,
    pub data_dir: PathBuf,
    pub proposals: mpsc::Sender<Entry>,
    /// The launcher's backends and appraisers, by rung. `None`: this replica launches nothing.
    pub contain: Option<Contain>,
}

pub struct Mechanism {
    pub id: NodeId,
    pub params: Params,
    pub floor: Floor,
    bundle: Box<dyn BundleDecider>,
    pub transport: Transport,
    tools: ToolHost,
    wasm_tools: Option<Arc<topak_contain::wasmtool::WasmToolHost>>,
    pub state: RwLock<State>,
    pub clock: SystemMonotonic,
    pub leader: AtomicBool,
    observed: Mutex<HashMap<LogIndex, MonoMillis>>,
    proposals: mpsc::Sender<Entry>,
    waiters: Mutex<HashMap<String, oneshot::Sender<(LogIndex, Applied)>>>,
    sessions: Mutex<HashMap<String, Session>>,
    boot: u64,
    counter: AtomicU64,
    corpus_dir: PathBuf,
    workspace_root: PathBuf,
    /// Working directories for Run tools, one per seat per round. Not the Run root: that is a
    /// pinned set of digests (`Params::run_root`), served from the content-addressed store.
    run_work: PathBuf,
    /// `Actuate` calls admitted and not yet returned, by round topic and sequence number
    /// (ADR-0042 §3). Keyed by topic, not fence, because a renewal moves the fence and keeps
    /// the round. The lock is held across the record write and across the seal, so a call's
    /// record is written either by the call, before the seal marker, or by the seal, as
    /// `unknown`; never both and never neither.
    in_flight: tokio::sync::Mutex<HashMap<String, BTreeMap<u64, InFlight>>>,
    /// What each `Actuate` of an open round returned, by topic and sequence number: what a handle
    /// names (ADR-0047 §2). Held by the replica that ran the call, and dropped when the round seals.
    results: tokio::sync::Mutex<HashMap<String, BTreeMap<u64, Value>>>,
    archive: Mutex<Option<std::fs::File>>,
    /// Denial records written per `after` topic by this replica (ADR-0003 A2).
    after_written: Mutex<HashMap<String, u64>>,
    /// `heard(o)` (ADR-0039 §1): this replica's clock when it last applied an admitted heartbeat
    /// from each observer seat. Per replica, like lease expiry: a subtracting interval on the
    /// mechanism's own clock (ADR-0032 §2), never replicated state.
    heard: Mutex<HashMap<SeatId, MonoMillis>>,
    contain: Option<Contain>,
    /// Guests this replica launched, by seat. Local: a guest is one host's process (P6).
    launched: Mutex<HashMap<SeatId, GuestCtl>>,
    /// ADR-0054 (Proposed): the session token of each workflow lease this replica granted and
    /// opened, by fence. BOOTSTRAP (PROVISIONAL workflow-occupant): handed out by `WorkflowStatus`.
    wf_sessions: Mutex<BTreeMap<LogIndex, String>>,
    /// The payload of every report a workflow worker made through this replica, by fence and
    /// sequence number: what a clear edge delivers to the next node. Per replica and not
    /// replicated, as `results` is (PROVISIONAL workflow-inputs).
    wf_reports: Mutex<BTreeMap<LogIndex, BTreeMap<u64, Value>>>,
    me: Weak<Mechanism>,
}

const COMMIT_DEADLINE: Duration = Duration::from_secs(5);
const RETRY_EVERY: Duration = Duration::from_millis(750);

fn deny(reason: DenyReason) -> AgentResponse {
    AgentResponse { admitted: false, detail: json!({ "decision": "deny", "reason": reason }) }
}

impl Mechanism {
    pub fn new(p: Parts) -> anyhow::Result<Arc<Self>> {
        std::fs::create_dir_all(&p.data_dir)?;
        // ADR-0039 §1: K must be below the round bound of every domain, or the coupling check is
        // vacuous. The values are the floor's; the round bounds are the mechanism's parameters.
        let k = p.floor.observer_values().k;
        for d in [Domain::Build, Domain::Run] {
            let r = p.params.round_bound_for(d);
            anyhow::ensure!(
                k < r,
                "policy-floor value K = {k} is not below {}'s round bound R = {r} (ADR-0039 §1)",
                d.as_str()
            );
        }
        // ADR-0034 A2 (pending): every replica checks at apply that a Run profile's P4 holds by the
        // set `Params::wasm_tools`. A replica that does not host one of them would run it some
        // other way, so it does not start.
        for id in &p.params.wasm_tools {
            anyhow::ensure!(
                p.wasm_tools.as_ref().is_some_and(|w| w.hosts(id)),
                "the parameters name {id} as a Wasm tool held to its channel, and this replica does not host it"
            );
        }
        let mut genesis = p.genesis;
        genesis.observer = p.floor.observer_values().clone();
        genesis.persona = p.floor.persona_values().clone();
        // The archive is a projection of the log, rebuilt as the log is re-delivered.
        let archive = std::fs::File::create(p.data_dir.join("archive.jsonl"))?;
        Ok(Arc::new_cyclic(|me| Self {
            id: p.id,
            params: p.params,
            floor: p.floor,
            bundle: p.bundle,
            transport: p.transport,
            tools: p.tools,
            wasm_tools: p.wasm_tools,
            state: RwLock::new(genesis),
            after_written: Mutex::new(HashMap::new()),
            heard: Mutex::new(HashMap::new()),
            clock: SystemMonotonic::new(),
            leader: AtomicBool::new(false),
            observed: Mutex::new(HashMap::new()),
            proposals: p.proposals,
            waiters: Mutex::new(HashMap::new()),
            sessions: Mutex::new(HashMap::new()),
            boot: rand::random(),
            counter: AtomicU64::new(0),
            corpus_dir: p.corpus_dir,
            workspace_root: p.data_dir.join("workspaces"),
            run_work: p.data_dir.join("run"),
            in_flight: tokio::sync::Mutex::new(HashMap::new()),
            results: tokio::sync::Mutex::new(HashMap::new()),
            archive: Mutex::new(Some(archive)),
            contain: p.contain,
            launched: Mutex::new(HashMap::new()),
            wf_sessions: Mutex::new(BTreeMap::new()),
            wf_reports: Mutex::new(BTreeMap::new()),
            me: me.clone(),
        }))
    }

    fn fresh_id(&self) -> String {
        format!("n{}-{:016x}-{}", self.id, self.boot, self.counter.fetch_add(1, Ordering::Relaxed))
    }

    // ---- ordering ----------------------------------------------------------------------------

    /// Propose and wait for the entry to be applied. Re-proposes under the same id until the
    /// deadline; the state machine applies an id at most once.
    pub async fn propose(&self, entry: Entry) -> Result<(LogIndex, Applied), String> {
        let id = entry.id().to_string();
        let (tx, mut rx) = oneshot::channel();
        self.waiters.lock().unwrap().insert(id.clone(), tx);
        let start = Instant::now();
        loop {
            if self.proposals.send(entry.clone()).await.is_err() {
                return Err("replica driver stopped".into());
            }
            match tokio::time::timeout(RETRY_EVERY, &mut rx).await {
                Ok(Ok(r)) => return Ok(r),
                Ok(Err(_)) => return Err("waiter dropped".into()),
                Err(_) if start.elapsed() >= COMMIT_DEADLINE => {
                    self.waiters.lock().unwrap().remove(&id);
                    return Err("not committed before the deadline".into());
                }
                Err(_) => {}
            }
        }
    }

    /// Apply a committed entry. Called by the driver in log order.
    pub async fn apply_committed(&self, slot: LogIndex, entry: Entry) {
        let (applied, ended) = {
            let mut st = self.state.write().unwrap();
            let before: Vec<LogIndex> = st.live_by_seat.values().copied().collect();
            let applied = st.apply(slot, &entry, &self.params);
            // The local observation of a grant is recorded before the state lock is released.
            // A lease visible in the state with no observation reads as expired (fail closed),
            // so recording it afterwards left a window in which the sweeper, or an admit, could
            // see a lease just granted and end it. Lock order is state, then `observed`, as in
            // `sweep_expired` and `admit`.
            if let Applied::LeaseGranted { fence } | Applied::Renewed { fence } = &applied {
                self.observed.lock().unwrap().insert(*fence, self.clock.now_ms());
            }
            let ended: Vec<(LogIndex, String, String)> = before
                .into_iter()
                .filter_map(|f| {
                    let r = st.leases.get(&f)?;
                    // A renewal continues the round under a new fence: its topic stays open.
                    let reason = r.ended.filter(|e| *e != EndReason::Renewed)?;
                    let d = st.rules.seat_domain(&r.lease.seat)?;
                    Some((
                        f,
                        topic_name(&st.chain, d, &r.lease.seat, r.lease.epoch, r.lease.round),
                        format!("{reason:?}"),
                    ))
                })
                .collect();
            (applied, ended)
        };
        // ADR-0039 §1: `heard(o)` is when *this replica* applied the heartbeat, on its own clock.
        if let Entry::Admit { rec, .. } = &entry
            && matches!(rec.action, Admitted::Heartbeat { .. })
            && matches!(applied, Applied::Admitted { .. })
        {
            self.heard.lock().unwrap().insert(rec.seat.clone(), self.clock.now_ms());
        }
        if let Some(f) = self.archive.lock().unwrap().as_mut() {
            let line = json!({ "slot": slot, "entry": entry, "applied": applied });
            let _ = writeln!(f, "{line}");
        }
        // Seal the topics of rounds that just ended, for sessions this replica serves. A call
        // still in flight is written as `unknown` ahead of the seal marker (ADR-0042 §3), in
        // sequence order, so the sealed topic has a record at every sequence number.
        let mut local: Vec<LogIndex> = self.sessions.lock().unwrap().values().map(|s| s.fence).collect();
        local.extend(self.launched.lock().unwrap().values().map(|g| g.fence));
        let ended_fences = ended.clone();
        for (fence, topic, reason) in ended {
            if !local.contains(&fence) {
                continue;
            }
            // ADR-0042 A3 (pending): a round that ends on its own admit, a worker's outcome or an
            // orchestrator's route, seals after that admit's record, which its effect writes.
            if reason == format!("{:?}", EndReason::Outcome) || reason == format!("{:?}", EndReason::Routed) {
                continue;
            }
            self.seal_round(&topic, &reason).await;
        }
        // P6: a launched guest is destroyed when its round ends, whatever ended it. A renewal is
        // not an end; the launcher moves the guest to the new fence itself.
        for (fence, _, _) in &ended_fences {
            self.end_launched(*fence).await;
        }
        if let Some(tx) = self.waiters.lock().unwrap().remove(entry.id()) {
            let _ = tx.send((slot, applied));
        }
    }

    /// Seal a round's topic: a call still in flight is written as `unknown` ahead of the seal
    /// marker (ADR-0042 §3), in sequence order, so the sealed topic has a record at every sequence
    /// number.
    async fn seal_round(&self, topic: &str, reason: &str) {
        let mut in_flight = self.in_flight.lock().await;
        for (seq, call) in in_flight.remove(topic).unwrap_or_default() {
            let rec = call.record(topic, seq, Outcome::Unknown, None);
            if let Err(e) = self.transport.emit(&rec).await {
                tracing::warn!(topic, seq, error = %e, "unknown Actuate record not written");
            }
        }
        drop(in_flight);
        self.results.lock().await.remove(topic);
        if let Err(e) = self.transport.seal(topic, reason).await {
            tracing::warn!(topic, error = %e, "seal marker not written");
        }
    }

    // ---- sessions and expiry -----------------------------------------------------------------

    fn session(&self, token: &str) -> Option<Session> {
        self.sessions.lock().unwrap().get(token).cloned()
    }

    /// ADR-0039 §1, condition 2: fewer than T_obs have elapsed since `heard(o)`, read with the
    /// asymmetric margin (elapsing early). No heartbeat heard means not fresh.
    fn fresh(&self, observer: &str, t_obs_ms: u64) -> bool {
        let Some(at) = self.heard.lock().unwrap().get(observer).copied() else { return false };
        !subtracting_interval_elapsed(at, t_obs_ms, self.params.lease_margin_ms, self.clock.now_ms())
    }

    fn expired(&self, fence: LogIndex, ttl: u64) -> bool {
        let Some(start) = self.observed.lock().unwrap().get(&fence).copied() else {
            // No local observation of the grant: treat as expired (fail closed).
            return true;
        };
        subtracting_interval_elapsed(start, ttl, self.params.lease_margin_ms, self.clock.now_ms())
    }

    /// Propose `EndRound(Expired)` for every live lease this replica has seen expire.
    /// Subtractions need no approval; they are ordered only so replicas agree.
    pub async fn sweep_expired(&self) {
        let expired: Vec<(SeatId, LogIndex)> = {
            let st = self.state.read().unwrap();
            st.live_by_seat
                .iter()
                .filter_map(|(seat, f)| {
                    let rec = st.leases.get(f)?;
                    self.expired(*f, rec.lease.ttl_ms).then(|| (seat.clone(), *f))
                })
                .collect()
        };
        for (seat, fence) in expired {
            let e = Entry::EndRound {
                id: self.fresh_id(),
                seat,
                fence,
                reason: EndReason::Expired,
                attribution: format!("replica {} local clock", self.id),
            };
            let _ = self.propose(e).await;
        }
    }

    // ---- the admit path ----------------------------------------------------------------------

    pub async fn act(&self, req: AgentRequest) -> AgentResponse {
        let Some(sess) = self.session(&req.token) else {
            // No session names no principal and no round, so there is no round record for it
            // (ADR-0003 A2 note). It is an authentication event at this replica's socket (G5).
            tracing::warn!(target: "security", "action with an unknown session token refused");
            return deny(DenyReason::Mechanism(MechanismDeny::UnknownLease));
        };
        // ADR-0052 §1: every action under an emergency seat's lease is signed with the person's
        // key. A bearer token signs nothing, so there is no token path to that lease.
        if self.state.read().unwrap().leases.get(&sess.fence).is_some_and(|r| r.person.is_some()) {
            return deny(DenyReason::Mechanism(MechanismDeny::Other(
                "an emergency seat's actions are signed with the person's key (ADR-0052 §1)".into(),
            )));
        }
        Box::pin(self.act_session(&sess, req.op, None)).await
    }

    /// An action from a launched guest, under the lease at `fence` (ADR-0036 §2.4). Under an
    /// attested session key the guest's proof is checked here, at decide, against the action it
    /// names; and again at apply, where it binds (ADR-0034 §3.5; `State::apply_admit`).
    pub async fn act_bound(&self, fence: LogIndex, op: AgentOp, proof: Option<SessionProof>) -> AgentResponse {
        let looked = {
            let st = self.state.read().unwrap();
            st.leases.get(&fence).map(|r| {
                // ADR-0052 §1: under an emergency seat's lease the key is the person's.
                let key = r.attestation.as_ref().and_then(|a| a.session_key.clone()).or_else(|| r.person.clone());
                (Session { seat: r.lease.seat.clone(), fence, epoch: r.lease.epoch }, key)
            })
        };
        let Some((sess, key)) = looked else { return deny(DenyReason::Mechanism(MechanismDeny::UnknownLease)) };
        if let Some(key) = key {
            let bad = |why: &str| {
                tracing::warn!(target: "security", seat = %sess.seat, fence, "{why}");
                deny(DenyReason::Mechanism(MechanismDeny::Other(format!("{why} (ADR-0034 §3.5)"))))
            };
            let Some(p) = &proof else { return bad("the attested session signed nothing") };
            if p.op != Digest::of_json(&op) {
                return bad("the session proof is for another action");
            }
            let body = session_body(fence, sess.epoch, p.ctr, &p.op);
            if !topak_core::authentic::verify(
                AGENT_OP_PURPOSE,
                &body,
                &topak_core::authentic::Signed { key, sig: p.sig.clone() },
            ) {
                return bad("the session proof is not the attested guest's");
            }
        }
        Box::pin(self.act_session(&sess, op, proof)).await
    }

    /// Replace each input that is a handle with the item it names (ADR-0047 §3; ADR-0049 §3):
    /// the result of an earlier `Actuate` of this round, or the content of a consulted object.
    /// The floor and the bundle have already decided the call on the handle's label; this is the
    /// tool host's half, and the bytes go to the tool and not to the principal.
    async fn resolve_handles(
        &self,
        topic: &str,
        rev: &Digest,
        tool: &str,
        inputs: &serde_json::Map<String, Value>,
    ) -> anyhow::Result<serde_json::Map<String, Value>> {
        let types = self.bundle.input_types(rev, tool);
        let mut out = inputs.clone();
        for (f, v) in inputs {
            let Some(h) = Handle::parse(v) else { continue };
            let item = match &h {
                Handle::Actuate(seq) => {
                    let results = self.results.lock().await;
                    let found = results.get(topic).and_then(|r| r.get(seq)).cloned();
                    found.ok_or_else(|| anyhow::anyhow!("input {f:?}: the result at {seq} is not held here"))?
                }
                Handle::Consult(object) => {
                    let bytes = std::fs::read(self.corpus_dir.join(&object.0))?;
                    anyhow::ensure!(Digest::of(&bytes) == *object, "object does not match its address");
                    Value::String(String::from_utf8_lossy(&bytes).into_owned())
                }
            };
            let fits = match types.get(f).map(String::as_str) {
                Some("string") => item.is_string(),
                Some("number") => item.is_number(),
                Some("boolean") => item.is_boolean(),
                _ => false,
            };
            anyhow::ensure!(fits, "input {f:?}: the item the handle names is not of the input's declared type");
            out.insert(f.clone(), item);
        }
        Ok(out)
    }

    /// The tool list of the lease at `fence` (ADR-0048 §2), and the topic it opens. It is a
    /// function of the grant: the allowlist of the revision the lease names, narrowed to what
    /// the lease may call. A reader with the log and the bundle can recompute it.
    ///
    /// The narrowing is the reference's: the lease schema carries no tool set (ADR-0031 §1 is
    /// closed), so a lease may call the tools the parameters allowlist for its domain when its
    /// alphabet holds the action that names a tool, and none when it does not.
    fn tool_list(&self, fence: LogIndex) -> Option<(String, Value)> {
        let st = self.state.read().unwrap();
        let lease = &st.leases.get(&fence)?.lease;
        let domain = st.rules.seat_domain(&lease.seat)?;
        let (action, tools) = match domain {
            Domain::Build => (ActionKind::Invoke, &self.params.build_tools),
            Domain::Run => (ActionKind::Actuate, &self.params.run_tools),
        };
        let none = std::collections::BTreeSet::new();
        let callable = if lease.alphabet.contains(&action) { tools } else { &none };
        let topic = topic_name(&st.chain, domain, &lease.seat, lease.epoch, lease.round);
        // ADR-0052 §2: an emergency seat's tool list is its envelope, each entry rendered from
        // the revision that holds it. The person is told what is in it.
        if let Some(envelope) = &st.leases[&fence].envelope {
            let mut by_rev: BTreeMap<&Digest, std::collections::BTreeSet<String>> = BTreeMap::new();
            for (tool, rev) in envelope {
                by_rev.entry(rev).or_default().insert(tool.clone());
            }
            let mut listed: Vec<Value> = Vec::new();
            for (rev, keys) in by_rev {
                let part = self.bundle.tool_list(rev, domain, &keys);
                for mut t in part["tools"].as_array().cloned().unwrap_or_default() {
                    t["revision"] = json!(rev);
                    listed.push(t);
                }
            }
            listed.sort_by_key(|t| (t["name"].to_string(), t["digest"].to_string()));
            return Some((topic, json!({ "bundle": lease.bundle, "domain": domain, "envelope": true, "tools": listed })));
        }
        Some((topic, self.bundle.tool_list(&lease.bundle, domain, callable)))
    }

    /// Write the round's opening record (ADR-0048 §2) and return what the principal is given:
    /// the list and its digest. Called once, at grant, before the session exists, so nothing the
    /// principal does can precede it on the topic. A renewal writes none: the bundle is fixed
    /// across renewal (ADR-0031 R2), and so is the list.
    ///
    /// `task` is the round's task where the grant carried one (ADR-0050 §5): its digest and label
    /// are on the log with the grant, and its bytes are in the round's payload, here.
    pub(crate) async fn open_round(&self, fence: LogIndex, seat: &str, task: Option<Value>) -> anyhow::Result<Value> {
        let (topic, list) = self.tool_list(fence).ok_or_else(|| anyhow::anyhow!("the lease is not in state"))?;
        let digest = Digest::of_json(&list);
        let rec = EmitRecord {
            topic,
            seat: seat.to_string(),
            fence,
            kind: RecordKind::Open,
            admit: None,
            seq: None,
            digest: digest.clone(),
            payload: match task {
                Some(task) => json!({ "tool_list": list, "task": task }),
                None => json!({ "tool_list": list }),
            },
        };
        self.transport.emit(&rec).await?;
        Ok(json!({ "digest": digest, "list": rec.payload["tool_list"] }))
    }

    async fn act_session(&self, sess: &Session, op: AgentOp, proof: Option<SessionProof>) -> AgentResponse {
        let sess = sess.clone();
        let action = match op {
            // Delivery, not an action: no admit, no count, the same answer all round.
            AgentOp::ToolList => {
                // A renewal moves the session's fence and not the list: the bundle and the
                // parameters are fixed, and the alphabet can only narrow, which this follows.
                return match self.tool_list(sess.fence) {
                    Some((_, list)) => AgentResponse {
                        admitted: true,
                        detail: json!({ "tool_list": { "digest": Digest::of_json(&list), "list": list } }),
                    },
                    None => deny(DenyReason::Mechanism(MechanismDeny::Other("no lease for this session".into()))),
                };
            }
            AgentOp::Act { action } => action,
            AgentOp::SubmitWorkspace => match self.workspace_digest(&sess) {
                Ok(artifact) => Action::Submit { artifact },
                Err(e) => return deny(DenyReason::Mechanism(MechanismDeny::Other(e))),
            },
            AgentOp::Abstain => {
                // ADR-0042 §5: a Run principal cannot end its own round. `apply` refuses the
                // entry too; refusing here keeps it off the log.
                if self.state.read().unwrap().rules.seat_domain(&sess.seat) == Some(Domain::Run) {
                    return deny(DenyReason::Mechanism(MechanismDeny::Other(
                        "a Run seat cannot abstain: its round ends with its lease (ADR-0042 §5)".into(),
                    )));
                }
                let e = Entry::EndRound {
                    id: self.fresh_id(),
                    seat: sess.seat.clone(),
                    fence: sess.fence,
                    reason: EndReason::Abstained,
                    attribution: format!("seat {}", sess.seat),
                };
                return match self.propose(e).await {
                    Ok((_, Applied::RoundEnded)) => {
                        AgentResponse { admitted: true, detail: json!({ "abstained": true }) }
                    }
                    Ok((_, a)) => deny(DenyReason::NotCommitted(format!("{a:?}"))),
                    Err(e) => deny(DenyReason::NotCommitted(e)),
                };
            }
        };
        let kind = action.kind();
        let attempted = action.clone();
        let resp = self.admit(&sess, action, proof).await;
        if !resp.admitted {
            tracing::info!(seat = %sess.seat, lease = sess.fence, action = %kind, detail = %resp.detail, "denied");
            self.record_denial(&sess, &attempted, &resp).await;
        }
        resp
    }

    /// ADR-0020: a denial is part of the round's replayable record. Written to the round topic
    /// while it is open: the seat's live lease is in the same epoch and round as the session's
    /// (a renewal keeps the topic open). Once the round has sealed, it goes to the round's
    /// `after` companion, up to `after_topic_limit` records and then one overflow marker.
    /// Content is reduced to digests (ADR-0004). The companion is ADR-0003 A2.
    async fn record_denial(&self, sess: &Session, action: &Action, resp: &AgentResponse) {
        let target = {
            let st = self.state.read().unwrap();
            let Some(rec) = st.leases.get(&sess.fence) else { return };
            let Some(d) = st.rules.seat_domain(&sess.seat) else { return };
            let (epoch, round) = (rec.lease.epoch, rec.lease.round);
            let open = st.live_lease(&sess.seat).is_some_and(|l| l.lease.epoch == epoch && l.lease.round == round);
            let topic = if open {
                topic_name(&st.chain, d, &sess.seat, epoch, round)
            } else {
                after_topic_name(&st.chain, d, &sess.seat, epoch, round)
            };
            (topic, open, epoch, round, st.last_applied)
        };
        let (topic, open, epoch, round, at) = target;
        let mut kind = RecordKind::Deny;
        if !open {
            let mut written = self.after_written.lock().unwrap();
            let n = written.entry(topic.clone()).or_insert(0);
            *n += 1;
            let limit = self.params.after_topic_limit;
            if *n > limit + 1 {
                return;
            }
            if *n == limit + 1 {
                kind = RecordKind::Overflow;
            }
        }
        if kind == RecordKind::Overflow {
            let payload = json!({ "overflow": true, "limit": self.params.after_topic_limit, "epoch": epoch,
                                  "round": round, "at": at, "decided_by": self.id });
            let rec = EmitRecord {
                topic,
                seat: sess.seat.clone(),
                fence: sess.fence,
                kind,
                admit: None,
                seq: None,
                digest: Digest::of_json(&payload),
                payload,
            };
            if let Err(e) = self.transport.emit(&rec).await {
                tracing::warn!(topic = rec.topic, error = %e, "overflow marker not written");
            }
            return;
        }
        let req =
            ActionRequest { seat: sess.seat.clone(), lease: sess.fence, epoch: sess.epoch, action: action.clone() };
        let payload = json!({
            "denied": Admitted::from_request(&req, false),
            "reason": resp.detail["reason"],
            "epoch": epoch,
            "round": round,
            "at": at,
            "decided_by": self.id,
        });
        let rec = EmitRecord {
            topic,
            seat: sess.seat.clone(),
            fence: sess.fence,
            kind: RecordKind::Deny,
            admit: None,
            seq: None,
            digest: Digest::of_json(&payload),
            payload,
        };
        if let Err(e) = self.transport.emit(&rec).await {
            tracing::warn!(topic = rec.topic, error = %e, "denial record not written");
        }
    }

    async fn admit(&self, sess: &Session, action: Action, proof: Option<SessionProof>) -> AgentResponse {
        let req = ActionRequest { seat: sess.seat.clone(), lease: sess.fence, epoch: sess.epoch, action };

        // 3–4: mechanism checks, then the lift, against one snapshot.
        let prepared = {
            let st = self.state.read().unwrap();
            st.check_live(&req, &self.params).and_then(|rec| {
                if self.expired(rec.lease.fence, rec.lease.ttl_ms) {
                    return Err(MechanismDeny::LeaseExpired);
                }
                // ADR-0039 §1: live(o) for the seat's cell Observers, freshness on this clock.
                let t_obs = st.observer.t_obs_ms;
                let live = st.observer_covers(&req.seat, &|o| self.fresh(o, t_obs));
                // ADR-0034 A2 (pending): a Run profile's P4 is checked here and again at apply.
                if let Action::Actuate { tool, digest, .. } = &req.action {
                    st.channel_fidelity(rec.lease.fence, &tool_id(tool, digest), &self.params)
                        .map_err(MechanismDeny::Other)?;
                }
                // ADR-0047 §4: the call's labels, from the entry of the lease's revision and the
                // round so far. Computed here, lifted into S, and carried by the admit.
                let kind = st.rules.seat_kind(&req.seat).map(SeatKind::as_str).unwrap_or("unknown");
                // ADR-0052 §2: an emergency seat's envelope holds entries of every revision in
                // force in the domain. A call is decided against the revision that holds its
                // entry: that revision's labels, its bundle tier, its channel.
                let call_rev = match (&rec.envelope, &req.action) {
                    (Some(envelope), Action::Actuate { tool, digest, .. }) => {
                        envelope.get(&tool_id(tool, digest)).unwrap_or(&rec.lease.bundle).clone()
                    }
                    _ => rec.lease.bundle.clone(),
                };
                let facts = self
                    .bundle
                    .label_facts(&call_rev, kind, &req.action, &rec.labels)
                    .map_err(MechanismDeny::Other)?;
                let frozen = lift(&req, &st, &self.params, rec, live, facts.as_ref())?;
                let domain = st.rules.seat_domain(&req.seat).expect("lifted");
                // ADR-0052 §5: a call under an activation is forensic class F5. ADR-0054 §4, §8: a
                // route is stamped with its workflow, event and basis, and a worker's report with
                // its outcome, from this snapshot, the one the mechanism checks were made against.
                let admitted = st.admitted(&req, kind == SeatKind::Emergency.as_str());
                Ok((frozen, call_rev, rec.lease.epoch, rec.lease.round, domain, facts, kind, admitted))
            })
        };
        let (frozen, lease_bundle, lease_epoch, round, domain, labels, seat_kind, admitted) = match prepared {
            Ok(p) => p,
            Err(MechanismDeny::LeaseExpired) => {
                let e = Entry::EndRound {
                    id: self.fresh_id(),
                    seat: sess.seat.clone(),
                    fence: sess.fence,
                    reason: EndReason::Expired,
                    attribution: format!("replica {} local clock", self.id),
                };
                let _ = self.proposals.send(e).await;
                return deny(DenyReason::Mechanism(MechanismDeny::LeaseExpired));
            }
            Err(d) => return deny(DenyReason::Mechanism(d)),
        };
        // Effect precondition for Submit: the artifact is the sealed workspace. Syntactic.
        if let Action::Submit { artifact } = &req.action {
            match self.workspace_digest(sess) {
                Ok(d) if &d == artifact => {}
                Ok(d) => {
                    return deny(DenyReason::Mechanism(MechanismDeny::Other(format!(
                        "artifact is not the workspace digest {}",
                        d.short()
                    ))));
                }
                Err(e) => return deny(DenyReason::Mechanism(MechanismDeny::Other(e))),
            }
        }

        // 5: the floor. 6: the bundle, only on a floor permit.
        let floor_out = self.floor.decide(&frozen);
        if let Some(d) = floor_gate(&floor_out) {
            return deny(d);
        }
        let bundle_out = self.bundle.decide(&lease_bundle, &frozen.bundle_input).await;
        let Decision::Admit { floor_reasons, engine, bundle } = compose(&floor_out, &bundle_out) else {
            let Decision::Deny(d) = compose(&floor_out, &bundle_out) else { unreachable!() };
            return deny(d);
        };

        // 7: order the admit.
        // ADR-0052 §5: a call under an activation is forensic class F5, as a break-glass
        // invocation was. It is admitted by the ordinary permit and not by an exception.
        let rec = AdmitRecord {
            seat: req.seat.clone(),
            lease: req.lease,
            epoch: req.epoch,
            action: admitted.clone(),
            input: frozen.digest(),
            floor: self.floor.floor_digest().clone(),
            schema: self.floor.schema_digest().clone(),
            floor_reasons: floor_reasons.clone(),
            bundle,
            engine,
            params: self.params.digest(),
            decided_by: self.id,
            session: proof,
            labels: labels.clone(),
        };
        let (slot, applied) = match self.propose(Entry::Admit { id: self.fresh_id(), rec }).await {
            Ok(r) => r,
            Err(e) => return deny(DenyReason::NotCommitted(e)),
        };
        let (seq, promoted) = match applied {
            Applied::Admitted { seq, promoted } => (seq, promoted),
            other => return deny(DenyReason::NotCommitted(format!("{other:?}"))),
        };

        // 8: the effect.
        let ctx = EffectCtx { sess, slot, lease_epoch, round, domain, seq, promoted, seat_kind, labels, lease_bundle, admitted };
        let result = self.effect(&req, &ctx).await;
        let (ok, result) = match result {
            Ok(v) => (true, v),
            // The admit stands (F1); absence of effect is not an event.
            Err(e) => (false, json!({ "effect_error": e.to_string() })),
        };
        AgentResponse {
            admitted: ok,
            detail: json!({
                "decision": "admit",
                "slot": slot,
                "floor": floor_reasons,
                "engine": engine,
                "result": result,
            }),
        }
    }

    // ---- effects -----------------------------------------------------------------------------

    fn workspace_dir(&self, seat: &str, epoch: Epoch, round: Round) -> PathBuf {
        self.workspace_root.join(workspace_id(seat, epoch, round))
    }

    fn session_workspace(&self, sess: &Session) -> Result<PathBuf, String> {
        let st = self.state.read().unwrap();
        let rec = st.leases.get(&sess.fence).ok_or("unknown lease")?;
        Ok(self.workspace_dir(&sess.seat, rec.lease.epoch, rec.lease.round))
    }

    /// The workspace digest: SHA-256 over sorted (relative path, bytes).
    pub fn workspace_digest(&self, sess: &Session) -> Result<Digest, String> {
        let dir = self.session_workspace(sess)?;
        let mut files = Vec::new();
        walk(&dir, &dir, &mut files).map_err(|e| e.to_string())?;
        let mut contents = Vec::new();
        for rel in files {
            let bytes = std::fs::read(dir.join(&rel)).map_err(|e| e.to_string())?;
            contents.push((rel, bytes));
        }
        Ok(topak_core::confine::workspace_digest(contents))
    }

    async fn effect(&self, req: &ActionRequest, cx: &EffectCtx<'_>) -> anyhow::Result<Value> {
        let seat = &req.seat;
        let ws = self.workspace_dir(seat, cx.lease_epoch, cx.round);
        let chain = self.state.read().unwrap().chain.clone();
        match &req.action {
            Action::Read { object } => {
                let bytes = std::fs::read(self.corpus_dir.join(&object.0))?;
                anyhow::ensure!(Digest::of(&bytes) == *object, "corpus object does not match its address");
                Ok(json!({ "object": object, "content": String::from_utf8_lossy(&bytes) }))
            }
            Action::Draft { target, content } => {
                let rel = workspace_relative(target).ok_or_else(|| anyhow::anyhow!("not workspace-relative"))?;
                let path = ws.join(&rel);
                std::fs::create_dir_all(path.parent().unwrap_or(&ws))?;
                std::fs::write(&path, content)?;
                Ok(json!({ "written": rel, "digest": Digest::of(content.as_bytes()) }))
            }
            Action::Invoke { tool, digest, inputs } => {
                std::fs::create_dir_all(&ws)?;
                let tid = tool_id(tool, digest);
                match &self.wasm_tools {
                    // Build's P4: a hermetic tool is handed no channel, whatever an entry says.
                    Some(w) if w.hosts(&tid) => w.call(&tid, inputs, None).await.map(|(v, _)| v),
                    _ => self.tools.call(&tid, inputs, &ws).await,
                }
            }
            Action::Consult { object } => {
                // The store is content-addressed; membership in the Run root was the floor's
                // decision (R4), from `Params::run_root`.
                let bytes = std::fs::read(self.corpus_dir.join(&object.0))?;
                anyhow::ensure!(Digest::of(&bytes) == *object, "object does not match its address");
                // ADR-0047 §2: the Listener looks the label up and does what the table says. The
                // label is a field of the envelope, written here and never read from the content.
                let (label, delivery) = delivered(cx);
                Ok(match delivery {
                    Delivery::Clear => json!({
                        "object": object, "label": label, "delivery": delivery,
                        "content": String::from_utf8_lossy(&bytes),
                    }),
                    // The handle is the reference the principal supplied, so it discloses nothing.
                    Delivery::Handle => json!({
                        "object": object, "label": label, "delivery": delivery,
                        "handle": Handle::Consult(object.clone()).to_value()["handle"],
                    }),
                })
            }
            Action::Actuate { tool, digest, inputs } => {
                let topic = topic_name(&chain, cx.domain, seat, cx.lease_epoch, cx.round);
                let seq = cx.seq.unwrap_or(0);
                let tid = tool_id(tool, digest);
                // ADR-0049 §5; ADR-0034 A2 R4: a hosted tool's target is the one its entry declares
                // in the bundle revision this lease names. Node configuration says nothing of it.
                let hosted = self.wasm_tools.as_ref().filter(|w| w.hosts(&tid));
                let channel = match hosted {
                    Some(_) => {
                        // The revision the call was decided against: the lease's, or, for an
                        // emergency seat, the one that holds the entry (ADR-0052 §2).
                        let declared = self.bundle.channel(&cx.lease_bundle, &tid);
                        anyhow::ensure!(
                            declared.is_some(),
                            "the lease's bundle revision declares no channel for {tid}, so the tool is not run"
                        );
                        declared
                    }
                    None => None,
                };
                let call = InFlight {
                    seat: seat.clone(),
                    fence: cx.sess.fence,
                    admit: cx.slot,
                    tool: tid.clone(),
                    seat_kind: cx.seat_kind,
                    inputs: Value::Object(inputs.clone()),
                    channel: channel.clone(),
                    labels: cx.labels.clone(),
                };
                self.in_flight.lock().await.entry(topic.clone()).or_default().insert(seq, call);
                let dir = self.run_work.join(format!("{seat}-e{}-r{}", cx.lease_epoch, cx.round));
                std::fs::create_dir_all(&dir)?;
                // ADR-0047 §3: a handle among the inputs is resolved here, on the mechanism's side,
                // and the tool receives the bytes. A handle that does not resolve to the input's
                // type is a failed call, recorded as one (ADR-0049 §3).
                let out = match self.resolve_handles(&topic, &cx.lease_bundle, &tid, inputs).await {
                    Err(e) => Err(e),
                    Ok(resolved) => match hosted {
                        Some(w) => w.call(&tid, &resolved, channel).await.map(|(v, _)| v),
                        None => self.tools.call(&tid, &resolved, &dir).await,
                    },
                };

                // Take the call back under the lock the seal holds. If the seal took it first,
                // the topic says `unknown`, and the result is withheld: what the principal
                // receives must be what the record's digest names (ADR-0042 §4), and an
                // `unknown` record names nothing.
                let mut in_flight = self.in_flight.lock().await;
                let Some(call) = in_flight.get_mut(&topic).and_then(|m| m.remove(&seq)) else {
                    return Ok(json!({
                        "seq": seq, "outcome": Outcome::Unknown,
                        "withheld": "the round sealed before the call returned (ADR-0042 §3, §4)",
                    }));
                };
                let outcome = if out.is_ok() { Outcome::Returned } else { Outcome::Failed };
                let rec = call.record(&topic, seq, outcome, out.as_ref().ok());
                let result_digest = rec.payload["actuate"]["result"].clone();
                let offset = self.transport.emit(&rec).await?;
                drop(in_flight);
                let result = out?;
                // Kept on this side for a later handle to name. The round's results go with the round.
                self.results.lock().await.entry(topic.clone()).or_default().insert(seq, result.clone());
                let (label, delivery) = delivered(cx);
                Ok(match delivery {
                    Delivery::Clear => json!({
                        "topic": topic, "offset": offset, "seq": seq, "outcome": outcome,
                        "label": label, "delivery": delivery,
                        "result_digest": result_digest, "result": result,
                    }),
                    // ADR-0047 §2, §3: suppressed. The bytes do not enter the guest, and neither
                    // does their digest, which low-entropy content would let it confirm by guessing.
                    Delivery::Handle => json!({
                        "topic": topic, "offset": offset, "seq": seq, "outcome": outcome,
                        "label": label, "delivery": delivery,
                        "handle": Handle::Actuate(seq).to_value()["handle"],
                    }),
                })
            }
            Action::Emit { record } | Action::Report { record } => {
                if matches!(cx.admitted, Admitted::Report { .. })
                    && self.state.read().unwrap().wf_bindings.contains_key(&cx.sess.fence)
                {
                    let seq = cx.seq.unwrap_or(0);
                    self.wf_reports.lock().unwrap().entry(cx.sess.fence).or_default().insert(seq, record.clone());
                }
                let rec = EmitRecord {
                    topic: topic_name(&chain, cx.domain, seat, cx.lease_epoch, cx.round),
                    seat: seat.clone(),
                    fence: cx.sess.fence,
                    kind: RecordKind::Emit,
                    admit: Some(cx.slot),
                    seq: Some(cx.seq.unwrap_or(0)),
                    digest: Digest::of_json(record),
                    payload: record.clone(),
                };
                let offset = self.transport.emit(&rec).await?;
                // ADR-0042 A3: the outcome ended the round; its record is the last before the seal.
                let ended = self.state.read().unwrap().leases.get(&cx.sess.fence).and_then(|r| r.ended);
                if ended == Some(EndReason::Outcome) {
                    self.seal_round(&rec.topic, &format!("{:?}", EndReason::Outcome)).await;
                }
                Ok(json!({ "topic": rec.topic, "offset": offset, "seq": rec.seq }))
            }
            // ADR-0040 A2, ADR-0015 A1 (pending): a route is a principal emission, a typed record on
            // the orchestrator's round topic. The lease it leads to was granted at apply, under the
            // workflow's promotion; its Observer reads what the orchestrator chose, and on what basis.
            Action::Route { edge } => {
                let stamp = match &cx.admitted {
                    Admitted::Route { stamp: Some(s), .. } => json!(s),
                    _ => Value::Null,
                };
                let payload = json!({ "route": { "edge": edge, "stamp": stamp } });
                let rec = EmitRecord {
                    topic: topic_name(&chain, cx.domain, seat, cx.lease_epoch, cx.round),
                    seat: seat.clone(),
                    fence: cx.sess.fence,
                    kind: RecordKind::Emit,
                    admit: Some(cx.slot),
                    seq: Some(cx.seq.unwrap_or(0)),
                    digest: Digest::of_json(&payload),
                    payload,
                };
                let offset = self.transport.emit(&rec).await?;
                // ADR-0042 A3: the route ended the round; its record is the last before the seal.
                self.seal_round(&rec.topic, &format!("{:?}", EndReason::Routed)).await;
                Ok(json!({ "topic": rec.topic, "offset": offset, "seq": rec.seq, "routed": edge }))
            }
            Action::Submit { artifact } => Ok(json!({ "submitted": artifact })),
            Action::Vote { artifact, .. } => {
                Ok(json!({ "recorded": true, "artifact": artifact, "promoted": cx.promoted.is_some() }))
            }
        }
    }

    // ---- operator ----------------------------------------------------------------------------

    pub async fn operate(&self, op: OperatorOp) -> Value {
        let id = self.fresh_id();
        let entry = match op {
            OperatorOp::Status => return self.status(),
            OperatorOp::Launch { principal, seat, profile, bundle, alphabet, ttl_ms, round, role, task_label } => {
                let req =
                    launch::LaunchOp { principal, seat, profile, bundle, alphabet, ttl_ms, round, role, task_label };
                return Box::pin(self.launch(req)).await;
            }
            OperatorOp::RegisterProfile { profile } => Entry::ProfileRegister { id, profile },
            OperatorOp::LoadWorkflow { text } => {
                // ADR-0044 §3: a seating naming a revision with no verified signature is refused at
                // decide, as a grant naming one is.
                if let Ok(def) = topak_core::workflow::Definition::parse(&text) {
                    let seatings = def.nodes.values().map(|n| &n.seating).chain(def.orchestrator.iter());
                    if let Some(s) = seatings.into_iter().find(|s| !self.bundle.verified(&s.bundle)) {
                        return json!({
                            "ok": false,
                            "error": format!("{}'s bundle {} has no verified signature (ADR-0044 §3)", s.seat, s.bundle.short()),
                        });
                    }
                }
                let outward = self.workflow_outward(&text);
                Entry::WorkflowLoad { id, text, outward }
            }
            OperatorOp::WorkflowStatus { workflow } => return self.workflow_status(&workflow),
            OperatorOp::Grant {
                principal,
                seat,
                persona,
                bundle,
                confinement,
                alphabet,
                ttl_ms,
                round,
                role,
                task_label,
                task_labels_allowed,
                sign_on,
            } => {
                // ADR-0044 §3: a grant naming a revision with no verified signature is refused,
                // here at decide, as a grant under superseded rules is at apply (I6). The
                // verified set is per replica, like the parameters, and must agree across them.
                if !self.bundle.verified(&bundle) {
                    return json!({
                        "ok": false,
                        "error": format!("bundle {} has no verified signature (ADR-0044 §3)", bundle.short()),
                    });
                }
                let req = GrantRequest {
                    principal,
                    seat: seat.clone(),
                    persona,
                    bundle,
                    confinement,
                    alphabet,
                    ttl_ms,
                    round,
                    role,
                    task_label,
                    task_labels_allowed,
                    sign_on,
                };
                return match self.propose(Entry::Grant { id, req, appraisal: None }).await {
                    Ok((_, Applied::LeaseGranted { fence })) => {
                        let (epoch, lease, containment) = {
                            let st = self.state.read().unwrap();
                            let l = st.leases[&fence].lease.clone();
                            (l.epoch, l, st.contained(fence))
                        };
                        // ADR-0048 §2: the opening record is on the topic before the session
                        // exists. If it cannot be written the lease stands unused: no token.
                        let tool_list = match self.open_round(fence, &seat, None).await {
                            Ok(l) => l,
                            Err(e) => {
                                return json!({
                                    "ok": false, "fence": fence,
                                    "error": format!("the round's opening record was not written, so no session was opened: {e}"),
                                });
                            }
                        };
                        let token = hex::encode(rand::random::<[u8; 32]>());
                        self.sessions.lock().unwrap().insert(token.clone(), Session { seat, fence, epoch });
                        json!({
                            "ok": true, "fence": fence, "token": token, "lease": lease,
                            "contained": containment.contained, "because": containment.because,
                            "tool_list": tool_list,
                        })
                    }
                    Ok((_, a)) => json!({ "ok": false, "applied": a }),
                    Err(e) => json!({ "ok": false, "error": e }),
                };
            }
            // BOOTSTRAP: stands in for the promotion that prepares an emergency seating.
            OperatorOp::PrepareEmergency { seat, seating } => Entry::EmergencySeating { id, seat, seating },
            OperatorOp::Activate { activation, approvals, task } => {
                return Box::pin(self.activate(activation, approvals, task)).await;
            }
            OperatorOp::Control { request, sig, assertion, task } => {
                return Box::pin(self.control(request, sig, assertion, task)).await;
            }
            OperatorOp::Renew { token, alphabet, rung, ttl_ms } => {
                let Some(sess) = self.session(&token) else { return json!({ "ok": false, "error": "unknown token" }) };
                let req = RenewRequest { seat: sess.seat.clone(), fence: sess.fence, alphabet, rung, ttl_ms };
                return match self.propose(Entry::Renew { id, req, appraisal: None }).await {
                    Ok((_, Applied::Renewed { fence })) => {
                        if let Some(s) = self.sessions.lock().unwrap().get_mut(&token) {
                            s.fence = fence;
                        }
                        json!({ "ok": true, "fence": fence })
                    }
                    Ok((_, a)) => json!({ "ok": false, "applied": a }),
                    Err(e) => json!({ "ok": false, "error": e }),
                };
            }
            OperatorOp::EndRound { token, reason } => {
                let Some(sess) = self.session(&token) else { return json!({ "ok": false, "error": "unknown token" }) };
                Entry::EndRound { id, seat: sess.seat, fence: sess.fence, reason, attribution: "operator".into() }
            }
            OperatorOp::Revoke { target, reason, attribution } => Entry::Revoke { id, target, reason, attribution },
            OperatorOp::FenceEpoch { reason, attribution } => Entry::EpochIncrement { id, reason, attribution },
            OperatorOp::Issue { issuance } => Entry::Issue { id, issuance },
            OperatorOp::GatesPassed { artifact, evidence } => Entry::GatesPassed { id, artifact, evidence },
            OperatorOp::BreakGlassApprove { seat, epoch, approval } => {
                Entry::BreakGlassApprove { id, seat, epoch, approval }
            }
        };
        match self.propose(entry).await {
            Ok((slot, applied)) => {
                json!({ "ok": !matches!(applied, Applied::Rejected(_)), "slot": slot, "applied": applied })
            }
            Err(e) => json!({ "ok": false, "error": e }),
        }
    }

    /// An operator's signed request (ADR-0050 §4): the facts, the lift, the floor's control
    /// entries, and then the log. Every replica verifies and re-checks it at apply; this replica
    /// writes it to the operator's topic, where its peers read it (§6).
    async fn control(
        &self,
        request: ControlRequest,
        sig: topak_core::authentic::Signed,
        assertion: Option<topak_core::authentic::Signed>,
        task: Option<String>,
    ) -> Value {
        let refuse = |why: String| json!({ "ok": false, "error": why });
        let op = request.operator.clone();
        // The facts and the lift, against one snapshot.
        let prepared = {
            let st = self.state.read().unwrap();
            st.control_facts(&request, assertion.as_ref()).and_then(|facts| {
                let frozen = lift_control(&request, &facts, &st).map_err(|d| d.to_string())?;
                let grant = match &request.action {
                    ControlAction::Regrant { target, round, alphabet, ttl_ms, task_label, sign_on, .. } => {
                        let s = st.seatings.get(target).ok_or_else(|| format!("seat {target} is not seated"))?;
                        Some(GrantRequest {
                            principal: s.principal.clone(),
                            seat: target.clone(),
                            persona: s.persona.clone(),
                            bundle: s.bundle.clone(),
                            confinement: s.confinement.clone(),
                            alphabet: alphabet.clone(),
                            ttl_ms: *ttl_ms,
                            round: *round,
                            role: s.role,
                            task_label: task_label.clone(),
                            task_labels_allowed: None,
                            sign_on: sign_on.clone(),
                        })
                    }
                    _ => None,
                };
                let renew = match &request.action {
                    ControlAction::Renew { target, alphabet, ttl_ms, .. } => st.live_lease(target).map(|l| RenewRequest {
                        seat: target.clone(),
                        fence: l.lease.fence,
                        alphabet: alphabet.clone(),
                        rung: l.lease.confinement.rung,
                        ttl_ms: *ttl_ms,
                    }),
                    _ => None,
                };
                Ok((facts, frozen, grant, renew))
            })
        };
        let (facts, frozen, grant, renew) = match prepared {
            Ok(p) => p,
            Err(e) => return refuse(e),
        };
        // §3: between boundaries a request is signed with the seat's key, and the mechanism checks
        // a signature it can check itself. Checked here so that a forgery is not ordered, and
        // again by every replica at apply.
        {
            let st = self.state.read().unwrap();
            let key = st.rules.seats.get(&op).map(|d| d.key.clone());
            let body = request.body(&st.chain);
            if key.as_ref() != Some(&sig.key) || !topak_core::authentic::verify(CONTROL_PURPOSE, &body, &sig) {
                return refuse("the request is not signed by the operator seat's key (ADR-0050 §3)".into());
            }
        }
        // §5: the task's bytes are the ones the signed digest names.
        if let ControlAction::Regrant { task: digest, .. } = &request.action {
            match (digest, &task) {
                (Some(d), Some(t)) if Digest::of(t.as_bytes()) == *d => {}
                (None, None) => {}
                _ => return refuse("the task's bytes are not the ones the request's digest names (ADR-0050 §5)".into()),
            }
        }
        if let Some(g) = &grant {
            if g.confinement.rung > 0 {
                return refuse("a Regrant of a seat at rung 1 or above launches a guest, which this reference has not built".into());
            }
            if !self.bundle.verified(&g.bundle) {
                return refuse(format!("bundle {} has no verified signature (ADR-0044 §3)", g.bundle.short()));
            }
        }
        // The floor. There is no bundle tier: the control entries are the whole envelope.
        let reasons = match self.floor.decide(&frozen) {
            topak_core::admit::FloorOutcome::Permit { reasons } => reasons,
            topak_core::admit::FloorOutcome::Deny { reasons } => {
                // The facts the floor was asked about: what the operator needs to see why.
                return json!({ "ok": false, "denied": "floor", "floor": reasons, "facts": facts });
            }
            topak_core::admit::FloorOutcome::Error { diagnostics } => {
                return json!({ "ok": false, "denied": "floor", "error": diagnostics });
            }
        };
        let action = request.action.clone();
        let control = Control { request, sig, assertion, facts };
        let entry = Entry::Control { id: self.fresh_id(), control: control.clone(), grant: grant.clone(), renew, appraisal: None };
        let (slot, applied) = match self.propose(entry).await {
            Ok(r) => r,
            Err(e) => return refuse(e),
        };
        if matches!(applied, Applied::Rejected(_)) {
            return json!({ "ok": false, "slot": slot, "applied": applied, "floor": reasons });
        }
        self.record_control(&op, slot, &control).await;
        let mut out = json!({ "ok": true, "slot": slot, "applied": applied, "floor": reasons });
        match (&action, &applied) {
            // A successor grant opens the target's next round: its opening record, with the
            // task, and a session for whoever the operator hands the token to.
            (ControlAction::Regrant { target, task_label, task: digest, .. }, Applied::LeaseGranted { fence }) => {
                let delivered = task.as_ref().map(|t| json!({ "digest": digest, "label": task_label, "text": t }));
                match self.open_round(*fence, target, delivered.clone()).await {
                    Ok(tool_list) => {
                        let (epoch, lease) = {
                            let st = self.state.read().unwrap();
                            let l = st.leases[fence].lease.clone();
                            (l.epoch, l)
                        };
                        let token = hex::encode(rand::random::<[u8; 32]>());
                        let sess = Session { seat: target.clone(), fence: *fence, epoch };
                        self.sessions.lock().unwrap().insert(token.clone(), sess);
                        out["fence"] = json!(fence);
                        out["token"] = json!(token);
                        out["lease"] = json!(lease);
                        out["tool_list"] = tool_list;
                        out["task"] = json!(delivered);
                    }
                    Err(e) => {
                        out["ok"] = json!(false);
                        out["error"] = json!(format!("the round's opening record was not written, so no session was opened: {e}"));
                    }
                }
            }
            // A renewal moves the lease to a new fence, and the seat's sessions here with it.
            (ControlAction::Renew { target, .. }, Applied::Renewed { fence }) => {
                for s in self.sessions.lock().unwrap().values_mut().filter(|s| &s.seat == target) {
                    s.fence = *fence;
                }
                out["fence"] = json!(fence);
            }
            _ => {}
        }
        out
    }

    /// An activation of an emergency seating (ADR-0052 §2): the roster's approvals are checked by
    /// every replica at apply. This replica computes the envelope, orders the activation, and
    /// opens the round: the envelope as the tool list, and the task. There is no token: the
    /// person acts under the lease's fence, signing each action.
    async fn activate(
        &self,
        activation: Activation,
        approvals: Vec<topak_core::authentic::Signed>,
        task: Option<String>,
    ) -> Value {
        let refuse = |why: String| json!({ "ok": false, "error": why });
        match (&activation.task, &task) {
            (Some(d), Some(t)) if Digest::of(t.as_bytes()) == *d => {}
            (None, None) => {}
            _ => return refuse("the task's bytes are not the ones the activation's digest names (ADR-0050 §5)".into()),
        }
        // The envelope, from the log at this point: the seating's own bundle, and, where the
        // seating says the envelope is the domain's, every revision a seating in force in the
        // domain names. An entry held by more than one revision is taken from the seating's own
        // first, and then from the first that holds it.
        let (own, revisions) = {
            let st = self.state.read().unwrap();
            let Some(seating) = st.emergency_seatings.get(&activation.seat) else {
                return refuse(format!("no emergency seating is prepared for seat {} (ADR-0052 §2)", activation.seat));
            };
            let mut revisions = vec![seating.bundle.clone()];
            let named = match &seating.envelope {
                Envelope::Named(named) => Some(named.clone()),
                Envelope::Domain => {
                    let in_force = st.seatings.iter().filter(|(seat, s)| {
                        st.rules.seat_domain(seat) == Some(Domain::Run)
                            && !st.revoked.iter().any(|t| t.matches(&s.principal, &s.persona, &s.confinement.digest))
                    });
                    for (_, s) in in_force {
                        if !revisions.contains(&s.bundle) {
                            revisions.push(s.bundle.clone());
                        }
                    }
                    None
                }
            };
            (named, revisions)
        };
        let mut envelope: BTreeMap<String, Digest> = BTreeMap::new();
        for rev in &revisions {
            if !self.bundle.verified(rev) {
                continue;
            }
            for tool in self.bundle.run_entries(rev) {
                if own.as_ref().is_none_or(|named| named.contains(&tool)) {
                    envelope.entry(tool).or_insert_with(|| rev.clone());
                }
            }
        }
        let entry = Entry::Activate { id: self.fresh_id(), activation: activation.clone(), approvals, envelope };
        let (slot, applied) = match self.propose(entry).await {
            Ok(r) => r,
            Err(e) => return refuse(e),
        };
        let Applied::LeaseGranted { fence } = applied else {
            return json!({ "ok": false, "slot": slot, "applied": applied });
        };
        let delivered =
            task.as_ref().map(|t| json!({ "digest": activation.task, "label": activation.task_label, "text": t }));
        match self.open_round(fence, &activation.seat, delivered.clone()).await {
            Ok(tool_list) => {
                let lease = self.state.read().unwrap().leases[&fence].lease.clone();
                json!({ "ok": true, "slot": slot, "fence": fence, "lease": lease, "tool_list": tool_list, "task": delivered })
            }
            Err(e) => json!({
                "ok": false, "fence": fence,
                "error": format!("the round's opening record was not written, so the round was not opened: {e}"),
            }),
        }
    }

    /// ADR-0050 §6: every control action is written to the operator's round topic, where the
    /// other operators of its domain read it. An operator with no live lease has no open round:
    /// its deny goes to the `after` companion of its last one.
    async fn record_control(&self, op: &str, slot: LogIndex, control: &Control) {
        let target = {
            let st = self.state.read().unwrap();
            let Some(d) = st.rules.seat_domain(op) else { return };
            let Some(rec) = st.last_lease.get(op).and_then(|f| st.leases.get(f)) else { return };
            let (epoch, round) = (rec.lease.epoch, rec.lease.round);
            let topic = if rec.live() {
                topic_name(&st.chain, d, op, epoch, round)
            } else {
                after_topic_name(&st.chain, d, op, epoch, round)
            };
            (topic, rec.lease.fence)
        };
        let payload = json!({ "control": control.request, "sig": control.sig, "facts": control.facts });
        let rec = EmitRecord {
            topic: target.0,
            seat: op.to_string(),
            fence: target.1,
            kind: RecordKind::Control,
            admit: Some(slot),
            seq: None,
            digest: Digest::of_json(&payload),
            payload,
        };
        if let Err(e) = self.transport.emit(&rec).await {
            tracing::warn!(topic = rec.topic, error = %e, "control record not written");
        }
    }

    pub fn status(&self) -> Value {
        let st = self.state.read().unwrap();
        let live: Vec<Value> = st
            .live_by_seat
            .values()
            .filter_map(|f| st.leases.get(f))
            .map(|r| {
                json!({
                    "seat": r.lease.seat, "fence": r.lease.fence, "epoch": r.lease.epoch, "round": r.lease.round,
                    "role": r.lease.role, "actions": r.actions, "alphabet": r.lease.alphabet,
                    "rung": r.lease.confinement.rung, "contained": st.contained(r.lease.fence),
                })
            })
            .collect();
        let candidates: Vec<Value> = st
            .candidates
            .values()
            .map(|c| {
                json!({
                    "artifact": c.artifact, "author": c.author, "votes": c.votes.len(),
                    "promoted_at": c.promoted_at,
                    "tally": format!("{:?}", tally(c, &st.rules, st.gates.get(&c.artifact))),
                })
            })
            .collect();
        json!({
            "replica": self.id,
            "chain": st.chain,
            "leader": self.leader.load(Ordering::Relaxed),
            "last_applied": st.last_applied,
            "epoch": st.epoch,
            "rules_epoch": st.rules.rules_epoch,
            "floor": self.floor.floor_digest(),
            "schema": self.floor.schema_digest(),
            "params": self.params.digest(),
            "live_leases": live,
            "candidates": candidates,
            "launched": self.launched.lock().unwrap().iter().map(|(seat, g)| json!({
                "seat": seat, "fence": g.fence, "instance": g.handle.instance(),
            })).collect::<Vec<_>>(),
        })
    }
}

struct EffectCtx<'a> {
    sess: &'a Session,
    slot: LogIndex,
    lease_epoch: Epoch,
    round: Round,
    domain: Domain,
    seq: Option<u64>,
    promoted: Option<Digest>,
    seat_kind: &'static str,
    /// The labels the admit carried (ADR-0047): how the Listener delivers what this effect returns.
    labels: Option<LabelFacts>,
    lease_bundle: Digest,
    /// The admit as it was ordered: a route's stamp is what its record names.
    admitted: Admitted,
}

/// How an `Actuate` call ended, as its record says it (ADR-0042 §3).
#[derive(Clone, Copy, Debug, PartialEq, Eq, serde::Serialize, serde::Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum Outcome {
    /// The tool returned, and `result` is the digest of what it returned.
    Returned,
    /// The call failed: the tool host refused it, or the tool returned an error.
    Failed,
    /// The round sealed before the call returned. Whether the effect happened is not known.
    Unknown,
}

/// An admitted `Actuate` whose record is not yet on the topic.
#[derive(Clone, Debug)]
struct InFlight {
    seat: SeatId,
    fence: LogIndex,
    admit: LogIndex,
    tool: String,
    /// The kind of the seat that made the call (ADR-0042 A2, pending): `emergency` marks a call
    /// under an activation, where the record used to say `breakGlass`.
    seat_kind: &'static str,
    inputs: Value,
    /// The declared channel a Wasm tool was held to (ADR-0034 A2): recorded, so the record says
    /// which channel the effect could have used. It is the entry's declaration in the lease's
    /// bundle revision (ADR-0049 §5). Absent for a native tool, which nothing holds.
    channel: Option<topak_contain::wasmtool::Channel>,
    /// ADR-0047 §5: the call's labels, for the record's envelope.
    labels: Option<LabelFacts>,
}

/// The label and the delivery mode of what an effect returns. An effect whose admit carried no
/// labels delivers nothing labelled, and nothing in the clear.
fn delivered(cx: &EffectCtx<'_>) -> (Label, Delivery) {
    match &cx.labels {
        Some(f) => (f.result_label.clone(), f.delivery),
        None => (Label::new(), Delivery::Handle),
    }
}

impl InFlight {
    /// The record of ADR-0042 §3. `actuate` is the envelope: control-plane facts, with the
    /// inputs and the result by digest, and the record's own digest is over it. `body` is the
    /// cognitive payload, the inputs and the result themselves (ADR-0004).
    fn record(&self, topic: &str, seq: u64, outcome: Outcome, result: Option<&Value>) -> EmitRecord {
        let mut envelope = json!({
            "tool": self.tool,
            "seatKind": self.seat_kind,
            "inputs": Digest::of_json(&self.inputs),
            "outcome": outcome,
            "result": result.map(Digest::of_json),
        });
        if let Some(ch) = &self.channel {
            envelope["channel"] = json!(ch);
        }
        // ADR-0047 §5: four fields on the control-plane side. A reader of envelopes alone sees
        // that an untrusted result was delivered clear and that an outward call followed.
        if let Some(f) = &self.labels {
            envelope["inputLabels"] = json!(f.input_labels);
            envelope["resultLabel"] = json!(f.result_label);
            envelope["delivery"] = json!(f.delivery);
            envelope["clearSet"] = json!(f.clear_set);
        }
        EmitRecord {
            topic: topic.to_string(),
            seat: self.seat.clone(),
            fence: self.fence,
            kind: RecordKind::Actuate,
            admit: Some(self.admit),
            seq: Some(seq),
            digest: Digest::of_json(&envelope),
            payload: json!({ "actuate": envelope, "body": { "inputs": self.inputs, "result": result } }),
        }
    }
}

fn walk(root: &Path, dir: &Path, out: &mut Vec<String>) -> std::io::Result<()> {
    if !dir.exists() {
        return Ok(());
    }
    for e in std::fs::read_dir(dir)? {
        let p = e?.path();
        if p.is_dir() {
            walk(root, &p, out)?;
        } else if let Ok(rel) = p.strip_prefix(root) {
            out.push(rel.to_string_lossy().replace('\\', "/"));
        }
    }
    Ok(())
}

// Re-exported so tests can build frozen inputs the way the node does.
pub use lift::FrozenInput;

// ---- workflows (ADR-0054, ADR-0055; Proposed) ----------------------------------------------------

impl Mechanism {
    /// What the bundle says of a workflow's nodes when it is loaded: a node whose lease reaches an
    /// outward entry (ADR-0049 §5) is outward, whatever the text declares. The text can only add.
    fn workflow_outward(&self, text: &str) -> std::collections::BTreeSet<String> {
        let Ok(def) = topak_core::workflow::Definition::parse(text) else { return Default::default() };
        def.nodes
            .iter()
            .filter(|(_, n)| n.seating.alphabet.contains(&ActionKind::Actuate))
            .filter(|(_, n)| {
                let list = self.bundle.tool_list(&n.seating.bundle, Domain::Run, &self.params.run_tools);
                list["tools"].as_array().is_some_and(|ts| ts.iter().any(|t| t["channel"]["outward"] == json!(true)))
            })
            .map(|(id, _)| id.clone())
            .collect()
    }

    /// Propose the mechanism's grant for every slot that is ready (ADR-0054 §2), and open each round
    /// this replica's proposal was the one that granted. Any replica may propose; the log orders
    /// them, and a proposal for a slot no longer ready is refused at apply and changes nothing.
    pub async fn drive_workflows(&self) {
        let ready: Vec<(Digest, topak_core::workflow::Slot, GrantRequest)> = {
            let st = self.state.read().unwrap();
            st.workflow_ready()
                .into_iter()
                .filter_map(|(wf, slot)| st.workflow_grant_request(&wf, &slot).ok().map(|r| (wf, slot, r)))
                .collect()
        };
        for (workflow, slot, req) in ready {
            let seat = req.seat.clone();
            let e = Entry::WorkflowGrant { id: self.fresh_id(), workflow: workflow.clone(), slot: slot.clone(), req, appraisal: None };
            let Ok((_, Applied::LeaseGranted { fence })) = self.propose(e).await else { continue };
            let task = self.workflow_opening(&workflow, &slot);
            if self.open_round(fence, &seat, Some(task)).await.is_err() {
                continue;
            }
            let epoch = self.state.read().unwrap().leases[&fence].lease.epoch;
            let token = hex::encode(rand::random::<[u8; 32]>());
            self.sessions.lock().unwrap().insert(token.clone(), Session { seat, fence, epoch });
            self.wf_sessions.lock().unwrap().insert(fence, token);
        }
    }

    /// What the round is told at its opening (ADR-0043 A3, ADR-0048 §2). A worker: its task, by
    /// template digest and label, and its inputs, each in its edge's delivery mode; a clear input
    /// is the predecessor's reports, where this replica holds them. An orchestrator: the track
    /// (ADR-0055 §6), the event's enabled chosen edges with each target's interface, the attributes
    /// of the event's causal history with their labels, handles for every output, and the basis.
    /// Never bytes to an orchestrator: its delivery table is a mechanism constant.
    fn workflow_opening(&self, wf: &Digest, slot: &topak_core::workflow::Slot) -> Value {
        use topak_core::workflow::Slot;
        let st = self.state.read().unwrap();
        let Some(run) = st.workflows.get(wf) else { return Value::Null };
        let output_of = |i: usize| -> Value {
            let a = &run.acts[i];
            json!({
                "activation": i, "node": a.node,
                "attributes": a.attrs, "found": a.found, "covered": a.covered,
                "outputs": a.attrs.as_ref().map(|x| x.output.clone()).unwrap_or_default(),
            })
        };
        match slot {
            Slot::Node(i) => {
                let a = &run.acts[*i];
                let n = &run.def.nodes[&a.node];
                let reports = self.wf_reports.lock().unwrap();
                let inputs: Vec<Value> = run.def.in_edges(&a.node)
                    .filter(|(id, _)| a.fired.contains(*id))
                    .map(|(id, e)| {
                        let src = a.trig.filter(|t| run.acts[*t].node == e.from)
                            .or_else(|| a.hist.iter().rev().copied().find(|j| run.acts[*j].node == e.from));
                        let label = src.and_then(|j| run.acts[j].attrs.as_ref()).map(|x| x.label.clone()).unwrap_or_default();
                        let fence = src.and_then(|j| st.wf_bindings.iter().find(|(_, b)| b.workflow == *wf && b.slot == Slot::Node(j)).map(|(f, _)| *f));
                        match e.delivery {
                            topak_core::labels::Delivery::Clear => json!({
                                "edge": id, "from": src, "delivery": "clear", "label": label,
                                "reports": fence.and_then(|f| reports.get(&f).cloned()),
                            }),
                            topak_core::labels::Delivery::Handle => json!({
                                "edge": id, "from": src, "delivery": "handle", "label": label,
                                "handle": { "input": { "activation": src, "edge": id } },
                            }),
                        }
                    })
                    .collect();
                json!({
                    "workflow": wf, "activation": i, "node": a.node,
                    "task": { "template": n.seating.task, "label": n.seating.task_label },
                    "outcomes": n.outcomes, "inputs": inputs,
                })
            }
            Slot::Decision(ev) => {
                let node = &run.acts[*ev].node;
                let edges: Vec<Value> = run.def.out_edges(node)
                    .filter(|(_, e)| e.kind == topak_core::workflow::EdgeKind::Chosen)
                    .map(|(id, e)| json!({
                        "edge": id, "to": e.to, "delivery": e.delivery,
                        "interface": { "task": run.def.nodes[&e.to].seating.task, "outcomes": run.def.nodes[&e.to].outcomes },
                        "enabled": run.disabled(*ev, id).is_none(),
                    }))
                    .collect();
                json!({
                    "workflow": wf, "event": ev, "node": node, "basis": st.last_applied,
                    "edges": edges,
                    "history": run.acts[*ev].hist.iter().map(|j| output_of(*j)).collect::<Vec<_>>(),
                })
            }
        }
    }

    fn workflow_status(&self, wf: &Digest) -> Value {
        let st = self.state.read().unwrap();
        let Some(run) = st.workflows.get(wf) else { return json!({ "ok": false, "error": "no such workflow" }) };
        let sessions: BTreeMap<String, Value> = self.wf_sessions.lock().unwrap().iter()
            .filter_map(|(f, t)| {
                let b = st.wf_bindings.get(f)?;
                let live = st.leases.get(f).is_some_and(|r| r.live());
                (b.workflow == *wf && live).then(|| (st.leases[f].lease.seat.clone(), json!({ "fence": f, "token": t, "slot": b.slot })))
            })
            .collect();
        json!({ "ok": true, "run": run, "sessions": sessions })
    }
}
