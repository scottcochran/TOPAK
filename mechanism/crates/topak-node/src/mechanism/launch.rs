//! The launcher in the node (ADR-0036 §6): one `launch` operator request starts the guest from a
//! registered profile, appraises it, grants to itself, and bridges.
//!
//! 1. **Refuse** an unregistered profile, a revoked principal, Persona or profile, a seat at rung
//!    0, or a rung this replica has no backend for. Nothing has started.
//! 2. **Launch**, and read the guest's identity line. None in time: Unattestable.
//! 3. **Nonce** from the log: epoch, last applied index, principal, round (ADR-0034 §3.1).
//! 4. **Evidence**: the guest binds the nonce; the platform reports. The bytes are retained here.
//! 5. **Appraise**. Unattestable is never ordered: the guest is destroyed and nothing is granted,
//!    at no rung. Contested is ordered: the principal is revoked. Attested is proposed as a grant
//!    carrying the appraisal, and every replica re-checks it at apply.
//! 6. **Bridge** the guest to the lease; **renew** on events, re-attesting the same guest with a
//!    fresh nonce at TTL/2 on the local monotonic clock, whose failure only subtracts (ADR-0032 §2).

use std::collections::{BTreeMap, BTreeSet};
use std::path::PathBuf;
use std::sync::Arc;
use std::time::Duration;

use serde_json::{Value, json};
use tokio::sync::{mpsc, oneshot};
use topak_contain::appraise::{AppraiseCtx, Appraiser};
use topak_contain::backend::{Backend, Evidence, GuestHandle, LaunchRequest, LaunchedGuest};
use topak_contain::bridge::{ActSink, BridgeEnd, Ctl, bridge};
use topak_contain::guest::GuestHello;
use topak_core::confine::*;
use topak_core::lease::Confinement;
use topak_core::state::*;
use topak_core::*;
use topak_mcp::proto::{AgentOp, AgentResponse};

use super::{BoxFuture, Mechanism};

/// What a replica launches with, by rung.
pub struct Contain {
    pub backends: BTreeMap<u8, Arc<dyn Backend>>,
    pub appraisers: BTreeMap<u8, Arc<dyn Appraiser>>,
    /// F18: evidence bytes by digest. Local to the appraising node; G9's archive does not exist.
    pub evidence_dir: PathBuf,
    pub hello_timeout: Duration,
}

/// A guest this replica launched and still runs.
pub struct GuestCtl {
    pub principal: String,
    pub fence: LogIndex,
    pub ctl: mpsc::Sender<Ctl>,
    pub handle: Arc<dyn GuestHandle>,
}

pub(super) struct LaunchOp {
    pub principal: String,
    pub seat: SeatId,
    pub profile: Digest,
    pub bundle: Digest,
    pub alphabet: BTreeSet<ActionKind>,
    pub ttl_ms: u64,
    pub round: Round,
    pub role: RoundRole,
    pub task_label: Option<BTreeSet<String>>,
}

/// The bridge's view of the mechanism.
struct Sink(std::sync::Weak<Mechanism>);

impl ActSink for Sink {
    fn act_bound<'a>(
        &'a self,
        fence: LogIndex,
        op: AgentOp,
        proof: Option<SessionProof>,
    ) -> BoxFuture<'a, AgentResponse> {
        Box::pin(async move {
            match self.0.upgrade() {
                Some(m) => m.act_bound(fence, op, proof).await,
                None => AgentResponse { admitted: false, detail: json!({ "error": "replica stopped" }) },
            }
        })
    }
}

fn refused(verdict: &str, why: impl std::fmt::Display) -> Value {
    json!({ "ok": false, "verdict": verdict, "reason": why.to_string() })
}

/// What a renewal needs to re-appraise the guest it launched.
struct Launched {
    seat: SeatId,
    principal: String,
    round: Round,
    profile: Profile,
    profile_digest: Digest,
    hello: GuestHello,
    rung: u8,
    appraiser: Arc<dyn Appraiser>,
    handle: Arc<dyn GuestHandle>,
    ctl: mpsc::Sender<Ctl>,
}

impl Mechanism {
    pub(super) async fn launch(&self, op: LaunchOp) -> Value {
        let Some(contain) = &self.contain else { return refused("refused", "this replica has no launcher configured") };
        if !self.bundle.verified(&op.bundle) {
            return refused("refused", format!("bundle {} has no verified signature (ADR-0044 §3)", op.bundle.short()));
        }
        // 1. Refusals that need nothing started.
        let checked = {
            let st = self.state.read().unwrap();
            (|| {
                let pr = st
                    .profiles
                    .get(&op.profile)
                    .ok_or("the profile is not registered from a promoted artifact (ADR-0034 §1)")?;
                let rung = st.rules.seats.get(&op.seat).map(|d| d.rung).ok_or("the seat is not declared")?;
                if rung == 0 {
                    return Err("the seat is declared at rung 0: a launch asserts nothing there; grant it");
                }
                // ADR-0034 §1: the profile is the seat's domain's. No Run profile exists (ADR-0042 §6),
                // so a Run seat launches nothing; apply refuses the grant too.
                if st.rules.seat_domain(&op.seat) != Some(pr.profile.domain) {
                    return Err(
                        "the profile is not for the seat's domain: Build and Run share the schema, not the profile (ADR-0034 §1)",
                    );
                }
                let persona = pr.profile.persona.model_json_sha256.clone().ok_or("the profile names no Persona")?;
                if st.revoked.iter().any(|t| t.matches(&op.principal, &persona, &op.profile)) {
                    return Err("revoked (ADR-0031 §5)");
                }
                Ok((pr.profile.clone(), rung, persona))
            })()
        };
        let (profile, rung, persona) = match checked {
            Ok(c) => c,
            Err(why) => return refused("refused", why),
        };
        let (Some(backend), Some(appraiser)) = (contain.backends.get(&rung), contain.appraisers.get(&rung)) else {
            return refused("refused", format!("this replica cannot launch or appraise at rung {rung}"));
        };

        // 2. Launch, and the guest's identity.
        let req = LaunchRequest { profile: &profile, profile_digest: &op.profile, seat: &op.seat };
        let LaunchedGuest { handle, mut io } = match backend.launch(req).await {
            Ok(g) => g,
            Err(e) => return refused("unattestable", format!("launch failed: {e:#}")),
        };
        let unattestable = |why: String| {
            let handle = handle.clone();
            let seat = op.seat.clone();
            async move {
                tracing::warn!(target: "security", %seat, instance = %handle.instance().short(), "Unattestable: {why}; no grant");
                handle.destroy().await;
                refused("unattestable", why)
            }
        };
        let hello = match io.read_hello(contain.hello_timeout).await {
            Ok(h) => h,
            Err(e) => return unattestable(e).await,
        };

        // 3–4. The nonce, and the evidence that binds it.
        let nonce = {
            let st = self.state.read().unwrap();
            NonceInput { epoch: st.epoch, index: st.last_applied, principal: op.principal.clone(), round: op.round }
        };
        let ev = match io.attest(&nonce.digest(), contain.hello_timeout).await {
            Ok(ge) => match handle.evidence(&ge, &hello) {
                Ok(ev) => ev,
                Err(e) => return unattestable(format!("no evidence: {e:#}")).await,
            },
            Err(e) => return unattestable(e).await,
        };
        let evidence = self.retain(contain, &ev);

        // 5. Appraise.
        let ctx = AppraiseCtx { nonce: &nonce, profile: &profile, profile_digest: &op.profile, hello: &hello };
        let (statement, signature) = match appraiser.appraise(ctx, &ev).await {
            Ok(s) => s,
            Err(e) => return unattestable(e.to_string()).await,
        };
        let appraisal = Appraisal { statement, instance: handle.instance().clone(), signature };
        match appraisal.statement.verdict {
            Appraised::Attested => {}
            Appraised::Unattestable => return unattestable("the appraiser found it unattestable".into()).await,
            Appraised::Contested => {
                // ADR-0034 §3.3: refuse, and revoke the principal, with the evidence. F2.
                handle.destroy().await;
                let e = Entry::Contested {
                    id: self.fresh_id(),
                    appraisal,
                    attribution: format!("replica {} launcher: evidence {}", self.id, evidence.short()),
                };
                tracing::warn!(target: "security", principal = %op.principal, "Contested: the launch measurement diverges; revoking the principal");
                return match self.propose(e).await {
                    Ok((_, applied)) => {
                        json!({ "ok": false, "verdict": "contested", "evidence": evidence, "applied": applied })
                    }
                    Err(e) => refused("contested", format!("the revocation was not ordered: {e}")),
                };
            }
        }
        // The fleet fence moved while appraising: apply would refuse it; do not ask (ADR-0034 §3.6).
        if self.state.read().unwrap().epoch != nonce.epoch {
            return unattestable("the epoch was fenced while the appraisal was pending".into()).await;
        }
        let grant = GrantRequest {
            principal: op.principal.clone(),
            seat: op.seat.clone(),
            persona,
            bundle: op.bundle,
            confinement: Confinement { digest: op.profile.clone(), rung },
            alphabet: op.alphabet,
            ttl_ms: op.ttl_ms,
            round: op.round,
            role: op.role,
            task_label: op.task_label,
        };
        let fence =
            match self.propose(Entry::Grant { id: self.fresh_id(), req: grant, appraisal: Some(appraisal) }).await {
                Ok((_, Applied::LeaseGranted { fence })) => fence,
                Ok((_, a)) => {
                    handle.destroy().await;
                    return json!({ "ok": false, "verdict": "attested", "applied": a });
                }
                Err(e) => return unattestable(format!("the grant was not ordered: {e}")).await,
            };

        // ADR-0048 §2: the round's opening record, before the guest is told it holds a lease.
        if let Err(e) = self.open_round(fence, &op.seat).await {
            handle.destroy().await;
            return json!({
                "ok": false, "verdict": "attested", "fence": fence,
                "error": format!("the round's opening record was not written, so the guest was not bridged: {e}"),
            });
        }

        // 6. Bridge, and renew on events.
        let (ctl, rx) = mpsc::channel(8);
        let epoch = nonce.epoch;
        let _ = ctl.send(Ctl::Granted { fence, epoch }).await;
        self.launched.lock().unwrap().insert(
            op.seat.clone(),
            GuestCtl { principal: op.principal.clone(), fence, ctl: ctl.clone(), handle: handle.clone() },
        );
        let me = self.me.upgrade().expect("a running mechanism");
        {
            let me = me.clone();
            let seat = op.seat.clone();
            let sink: Arc<dyn ActSink> = Arc::new(Sink(self.me.clone()));
            tokio::spawn(async move {
                let end = bridge(io, fence, sink, rx).await;
                me.bridge_ended(&seat, end).await;
            });
        }
        let renewal = Launched {
            seat: op.seat.clone(),
            principal: op.principal.clone(),
            round: op.round,
            profile,
            profile_digest: op.profile.clone(),
            hello,
            rung,
            appraiser: appraiser.clone(),
            handle: handle.clone(),
            ctl,
        };
        tokio::spawn(me.clone().renew_loop(renewal, op.ttl_ms));
        let (containment, lease) = {
            let st = self.state.read().unwrap();
            (st.contained(fence), st.leases[&fence].lease.clone())
        };
        json!({
            "ok": true, "verdict": "attested", "fence": fence, "lease": lease, "rung": rung,
            "instance": handle.instance(), "evidence": evidence,
            "contained": containment.contained, "because": containment.because,
            "simulated": containment.simulated,
        })
    }

    /// F18: keep the evidence bytes, by digest. Local: the archive (G9) does not exist.
    fn retain(&self, contain: &Contain, ev: &Evidence) -> Digest {
        let d = ev.digest();
        if std::fs::create_dir_all(&contain.evidence_dir).is_ok() {
            let _ = std::fs::write(
                contain.evidence_dir.join(format!("{}.json", d.0)),
                serde_json::to_vec(ev).unwrap_or_default(),
            );
        }
        d
    }

    /// ADR-0034 §3.6: re-attest the same guest with a fresh nonce before the lease lapses.
    /// Attested renews at the same rung; Unattestable stops renewing and the lease lapses on its
    /// TTL; Contested revokes. No interval re-measures a running guest.
    async fn renew_loop(self: Arc<Self>, g: Launched, ttl_ms: u64) {
        let Some(contain) = &self.contain else { return };
        loop {
            tokio::time::sleep(Duration::from_millis((ttl_ms / 2).max(1))).await;
            let Some(fence) =
                self.launched.lock().unwrap().get(&g.seat).filter(|c| c.principal == g.principal).map(|c| c.fence)
            else {
                return;
            };
            let (lease, nonce) = {
                let st = self.state.read().unwrap();
                let Some(r) = st.leases.get(&fence).filter(|r| r.live()) else { return };
                let n = NonceInput {
                    epoch: st.epoch,
                    index: st.last_applied,
                    principal: g.principal.clone(),
                    round: g.round,
                };
                (r.lease.clone(), n)
            };
            let (tx, rx) = oneshot::channel();
            if g.ctl.send(Ctl::Attest { nonce: nonce.digest(), reply: tx }).await.is_err() {
                return;
            }
            let lapse = |why: String| {
                tracing::warn!(target: "security", seat = %g.seat, fence, "renewal Unattestable: {why}; the lease lapses");
            };
            let ge = match tokio::time::timeout(contain.hello_timeout, rx).await {
                Ok(Ok(ge)) => ge,
                _ => return lapse("the guest gave no evidence".into()),
            };
            let ev = match g.handle.evidence(&ge, &g.hello) {
                Ok(ev) => ev,
                Err(e) => return lapse(format!("{e:#}")),
            };
            let evidence = self.retain(contain, &ev);
            let ctx =
                AppraiseCtx { nonce: &nonce, profile: &g.profile, profile_digest: &g.profile_digest, hello: &g.hello };
            let appraisal = match g.appraiser.appraise(ctx, &ev).await {
                Ok((statement, signature)) => Appraisal { statement, instance: g.handle.instance().clone(), signature },
                Err(e) => return lapse(e.to_string()),
            };
            match appraisal.statement.verdict {
                Appraised::Attested => {}
                Appraised::Unattestable => return lapse("unattestable".into()),
                Appraised::Contested => {
                    let e = Entry::Contested {
                        id: self.fresh_id(),
                        appraisal,
                        attribution: format!("replica {} launcher at renewal: evidence {}", self.id, evidence.short()),
                    };
                    let _ = self.propose(e).await;
                    return;
                }
            }
            let req = RenewRequest {
                seat: g.seat.clone(),
                fence,
                alphabet: lease.alphabet.clone(),
                rung: g.rung,
                ttl_ms: lease.ttl_ms,
            };
            match self.propose(Entry::Renew { id: self.fresh_id(), req, appraisal: Some(appraisal) }).await {
                Ok((_, Applied::Renewed { fence: next })) => {
                    if let Some(c) = self.launched.lock().unwrap().get_mut(&g.seat) {
                        c.fence = next;
                    }
                    let _ = g.ctl.send(Ctl::Granted { fence: next, epoch: lease.epoch }).await;
                }
                other => return lapse(format!("the renewal was not applied: {other:?}")),
            }
        }
    }

    /// The guest's channel ended. If its lease is still live the launcher ends the round: an
    /// ordered subtraction, attributed under F2 (ADR-0036 §2).
    async fn bridge_ended(&self, seat: &str, end: BridgeEnd) {
        let Some(g) = self.launched.lock().unwrap().remove(seat) else { return };
        g.handle.destroy().await;
        let live = self.state.read().unwrap().leases.get(&g.fence).is_some_and(|r| r.live());
        if live {
            let why = match &end {
                BridgeEnd::GuestClosed => "the guest closed its channel".to_string(),
                BridgeEnd::Shutdown => "the guest was shut down".to_string(),
                BridgeEnd::ProtocolError(e) => format!("protocol error: {e}"),
            };
            let e = Entry::EndRound {
                id: self.fresh_id(),
                seat: seat.to_string(),
                fence: g.fence,
                reason: EndReason::Operator,
                attribution: format!("replica {} launcher: {why}", self.id),
            };
            let _ = self.propose(e).await;
        }
    }

    /// P6: the lease at `fence` ended; destroy the guest that held it, if this replica runs it.
    pub(super) async fn end_launched(&self, fence: LogIndex) {
        let g = {
            let mut l = self.launched.lock().unwrap();
            let seat = l.iter().find(|(_, g)| g.fence == fence).map(|(s, _)| s.clone());
            seat.and_then(|s| l.remove(&s))
        };
        if let Some(g) = g {
            let _ = g.ctl.try_send(Ctl::Shutdown);
            g.handle.destroy().await;
        }
    }
}
