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

use std::collections::HashMap;
use std::future::Future;
use std::io::Write;
use std::path::{Path, PathBuf};
use std::pin::Pin;
use std::sync::atomic::{AtomicBool, AtomicU64, Ordering};
use std::sync::{Arc, Mutex, RwLock};
use std::time::{Duration, Instant};

use serde_json::{Value, json};
use tokio::sync::{mpsc, oneshot};
use topak_bundle::BundleTier;
use topak_core::action::{Action, ActionRequest, tool_id};
use topak_core::admit::{BundleOutcome, Decision, DenyReason, compose, floor_gate, via_break_glass};
use topak_core::clock::{MonoMillis, MonotonicClock, SystemMonotonic, subtracting_interval_elapsed};
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
}

impl BundleDecider for BundleTier {
    fn decide<'a>(&'a self, lease_bundle: &'a Digest, input: &'a Value) -> BoxFuture<'a, BundleOutcome> {
        Box::pin(BundleTier::decide(self, lease_bundle, input))
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
    pub corpus_dir: PathBuf,
    pub data_dir: PathBuf,
    pub proposals: mpsc::Sender<Entry>,
}

pub struct Mechanism {
    pub id: NodeId,
    pub params: Params,
    pub floor: Floor,
    bundle: Box<dyn BundleDecider>,
    pub transport: Transport,
    tools: ToolHost,
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
    run_root: PathBuf,
    archive: Mutex<Option<std::fs::File>>,
    /// Denial records written per `after` topic by this replica (ADR-0003 A2).
    after_written: Mutex<HashMap<String, u64>>,
}

const COMMIT_DEADLINE: Duration = Duration::from_secs(5);
const RETRY_EVERY: Duration = Duration::from_millis(750);

fn deny(reason: DenyReason) -> AgentResponse {
    AgentResponse { admitted: false, detail: json!({ "decision": "deny", "reason": reason }) }
}

impl Mechanism {
    pub fn new(p: Parts) -> anyhow::Result<Arc<Self>> {
        std::fs::create_dir_all(&p.data_dir)?;
        // The archive is a projection of the log, rebuilt as the log is re-delivered.
        let archive = std::fs::File::create(p.data_dir.join("archive.jsonl"))?;
        Ok(Arc::new(Self {
            id: p.id,
            params: p.params,
            floor: p.floor,
            bundle: p.bundle,
            transport: p.transport,
            tools: p.tools,
            state: RwLock::new(p.genesis),
            after_written: Mutex::new(HashMap::new()),
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
            run_root: p.data_dir.join("run"),
            archive: Mutex::new(Some(archive)),
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
        if let Applied::LeaseGranted { fence } | Applied::Renewed { fence } = &applied {
            self.observed.lock().unwrap().insert(*fence, self.clock.now_ms());
        }
        if let Some(f) = self.archive.lock().unwrap().as_mut() {
            let line = json!({ "slot": slot, "entry": entry, "applied": applied });
            let _ = writeln!(f, "{line}");
        }
        // Seal the topics of rounds that just ended, for sessions this replica serves.
        let local: Vec<LogIndex> = self.sessions.lock().unwrap().values().map(|s| s.fence).collect();
        for (fence, topic, reason) in ended {
            if local.contains(&fence)
                && let Err(e) = self.transport.seal(&topic, &reason).await
            {
                tracing::warn!(topic, error = %e, "seal marker not written");
            }
        }
        if let Some(tx) = self.waiters.lock().unwrap().remove(entry.id()) {
            let _ = tx.send((slot, applied));
        }
    }

    // ---- sessions and expiry -----------------------------------------------------------------

    fn session(&self, token: &str) -> Option<Session> {
        self.sessions.lock().unwrap().get(token).cloned()
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
        let action = match req.op {
            AgentOp::Act { action } => action,
            AgentOp::SubmitWorkspace => match self.workspace_digest(&sess) {
                Ok(artifact) => Action::Submit { artifact },
                Err(e) => return deny(DenyReason::Mechanism(MechanismDeny::Other(e))),
            },
            AgentOp::Abstain => {
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
        let resp = self.admit(&sess, action).await;
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

    async fn admit(&self, sess: &Session, action: Action) -> AgentResponse {
        let req = ActionRequest { seat: sess.seat.clone(), lease: sess.fence, epoch: sess.epoch, action };

        // 3–4: mechanism checks, then the lift, against one snapshot.
        let prepared = {
            let st = self.state.read().unwrap();
            st.check_live(&req, &self.params).and_then(|rec| {
                if self.expired(rec.lease.fence, rec.lease.ttl_ms) {
                    return Err(MechanismDeny::LeaseExpired);
                }
                let frozen = lift(&req, &st, &self.params, rec)?;
                let domain = st.rules.seat_domain(&req.seat).expect("lifted");
                Ok((frozen, rec.lease.bundle.clone(), rec.lease.epoch, rec.lease.round, domain))
            })
        };
        let (frozen, lease_bundle, lease_epoch, round, domain) = match prepared {
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
        let rec = AdmitRecord {
            seat: req.seat.clone(),
            lease: req.lease,
            epoch: req.epoch,
            action: Admitted::from_request(&req, via_break_glass(&floor_reasons)),
            input: frozen.digest(),
            floor: self.floor.floor_digest().clone(),
            schema: self.floor.schema_digest().clone(),
            floor_reasons: floor_reasons.clone(),
            bundle,
            engine,
            params: self.params.digest(),
            decided_by: self.id,
        };
        let (slot, applied) = match self.propose(Entry::Admit { id: self.fresh_id(), rec }).await {
            Ok(r) => r,
            Err(e) => return deny(DenyReason::NotCommitted(e)),
        };
        let (emit_seq, promoted) = match applied {
            Applied::Admitted { emit_seq, promoted } => (emit_seq, promoted),
            other => return deny(DenyReason::NotCommitted(format!("{other:?}"))),
        };

        // 8: the effect.
        let ctx = EffectCtx { sess, slot, lease_epoch, round, domain, emit_seq, promoted };
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
        files.sort();
        let mut bytes = Vec::new();
        for rel in files {
            bytes.extend(rel.as_bytes());
            bytes.push(0);
            bytes.extend(std::fs::read(dir.join(&rel)).map_err(|e| e.to_string())?);
            bytes.push(0);
        }
        Ok(Digest::of(&bytes))
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
                self.tools.call(&tool_id(tool, digest), inputs, &ws).await
            }
            Action::RunInvoke { tool, digest, inputs } => {
                let dir = self.run_root.join(format!("{seat}-e{}-r{}", cx.lease_epoch, cx.round));
                std::fs::create_dir_all(&dir)?;
                self.tools.call(&tool_id(tool, digest), inputs, &dir).await
            }
            Action::Emit { record } | Action::RunEmit { record } => {
                let rec = EmitRecord {
                    topic: topic_name(&chain, cx.domain, seat, cx.lease_epoch, cx.round),
                    seat: seat.clone(),
                    fence: cx.sess.fence,
                    kind: RecordKind::Emit,
                    admit: Some(cx.slot),
                    seq: Some(cx.emit_seq.unwrap_or(0)),
                    digest: Digest::of_json(record),
                    payload: record.clone(),
                };
                let offset = self.transport.emit(&rec).await?;
                Ok(json!({ "topic": rec.topic, "offset": offset, "seq": rec.seq }))
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
            OperatorOp::Grant { principal, seat, persona, bundle, confinement, alphabet, ttl_ms, round, role } => {
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
                };
                return match self.propose(Entry::Grant { id, req }).await {
                    Ok((_, Applied::LeaseGranted { fence })) => {
                        let (epoch, lease) = {
                            let st = self.state.read().unwrap();
                            let l = st.leases[&fence].lease.clone();
                            (l.epoch, l)
                        };
                        let token = hex::encode(rand::random::<[u8; 32]>());
                        self.sessions.lock().unwrap().insert(token.clone(), Session { seat, fence, epoch });
                        json!({
                            "ok": true, "fence": fence, "token": token, "lease": lease,
                            "contained": lease.is_contained(),
                            "note": "rung 0 and no provenance criterion: this principal is Mediated",
                        })
                    }
                    Ok((_, a)) => json!({ "ok": false, "applied": a }),
                    Err(e) => json!({ "ok": false, "error": e }),
                };
            }
            OperatorOp::Renew { token, alphabet, rung, ttl_ms } => {
                let Some(sess) = self.session(&token) else { return json!({ "ok": false, "error": "unknown token" }) };
                let req = RenewRequest { seat: sess.seat.clone(), fence: sess.fence, alphabet, rung, ttl_ms };
                return match self.propose(Entry::Renew { id, req }).await {
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
                    "rung": r.lease.confinement.rung, "contained": r.lease.is_contained(),
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
        })
    }
}

struct EffectCtx<'a> {
    sess: &'a Session,
    slot: LogIndex,
    lease_epoch: Epoch,
    round: Round,
    domain: Domain,
    emit_seq: Option<u64>,
    promoted: Option<Digest>,
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
