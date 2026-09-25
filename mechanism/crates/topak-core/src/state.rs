//! The replicated state machine, applied in log order on every replica (ADR-0015).
//!
//! Every effect has a consensus-ordered, authorizing predecessor in the log: an `Admit` entry.
//! Denials are never logged. Subtractions (lease end, epoch increment) are logged too — not
//! because they need approval (they do not; ADR-0031 §5) but because the state they change is
//! replicated and every replica must agree on it. *Ordered* is not the same as *authorized*.
//!
//! `apply` is deterministic and re-checks every state-dependent mechanism condition, because
//! the replica that decided an admit did so against a snapshot that may have moved by the time
//! the entry commits.

use serde::{Deserialize, Serialize};
use std::collections::{BTreeMap, BTreeSet};
use std::fmt;

use crate::action::{ActionRequest, tool_id};
use crate::authentic::{self, KeyHex, Signed};
use crate::lease::{Confinement, Lease, MAX_RUNG};
use crate::promotion::{Candidate, Tally, VoteRecord, tally};
use crate::rules::{self, Issuance, Rules, Violation};
use crate::types::*;

/// The three mechanism parameters of ADR-0022 §3, plus the lease-expiry margin (ADR-0032).
/// These ship with the mechanism configuration and must be identical on every replica; their
/// digest is recorded in every admit.
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct Params {
    /// The pinned, content-addressed corpus root.
    pub corpus: BTreeSet<Digest>,
    /// Build tool allowlist, by `name@digest`.
    pub build_tools: BTreeSet<String>,
    /// PROVISIONAL (Run alphabet): Run tool allowlist, by `name@digest`.
    pub run_tools: BTreeSet<String>,
    /// Maximum admitted actions per round (termination; bounds the state space).
    pub round_bound: u64,
    /// Asymmetric margin subtracted from every lease TTL (ADR-0032 §2).
    pub lease_margin_ms: u64,
}

impl Params {
    pub fn digest(&self) -> Digest {
        Digest::of_json(self)
    }
}

/// Why a round ended. Every variant is a subtraction.
#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum EndReason {
    /// `Submit(digest)` is terminal for the authoring round.
    Submitted,
    /// `Submit(⊥)`: the author abstains.
    Abstained,
    /// `Vote` is terminal for the voter's promotion round.
    Voted,
    /// Passive expiry observed on a replica's local clock.
    Expired,
    /// The epoch was incremented (revocation fences it; ADR-0031 §5).
    Fenced,
    /// A new rules epoch was issued.
    RulesChanged,
    /// Ended by an operator (e-stop).
    Operator,
    /// Replaced by a narrower renewal at a new fence.
    Renewed,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct LeaseRecord {
    pub lease: Lease,
    pub ended: Option<EndReason>,
    /// Admitted actions this round (checked against the round bound).
    pub actions: u64,
    /// Per-principal emission sequence number, the ADR-0015 residual for admit-to-emit order.
    pub emit_seq: u64,
}

impl LeaseRecord {
    pub fn live(&self) -> bool {
        self.ended.is_none()
    }
}

/// A grant request: everything in the lease except what the log assigns (`epoch`, `fence`,
/// `rulesEpoch` are assigned at apply, never supplied).
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct GrantRequest {
    pub principal: String,
    pub seat: SeatId,
    pub persona: Digest,
    pub bundle: Digest,
    pub confinement: Confinement,
    pub alphabet: BTreeSet<ActionKind>,
    pub ttl_ms: u64,
    pub round: Round,
    pub role: RoundRole,
}

/// A renewal names the live lease and the narrowed values.
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct RenewRequest {
    pub seat: SeatId,
    pub fence: LogIndex,
    pub alphabet: BTreeSet<ActionKind>,
    pub rung: u8,
    pub ttl_ms: u64,
}

/// The typed control-plane summary of an admitted action (payloads by digest; ADR-0004).
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(tag = "kind")]
pub enum Admitted {
    Read { object: Digest },
    Draft { target: String, content: Digest },
    Invoke { tool: String, inputs: Digest },
    Emit { record: Digest },
    Submit { artifact: Digest },
    Vote { verdict: Verdict, artifact: Digest, evidence: Digest, rules_epoch: RulesEpoch },
    RunInvoke { tool: String, inputs: Digest, break_glass: bool },
    RunEmit { record: Digest },
}

impl Admitted {
    pub fn from_request(req: &ActionRequest, break_glass: bool) -> Self {
        use crate::action::Action as A;
        match &req.action {
            A::Read { object } => Admitted::Read { object: object.clone() },
            A::Draft { target, content } => {
                Admitted::Draft { target: target.clone(), content: Digest::of(content.as_bytes()) }
            }
            A::Invoke { tool, digest, inputs } => {
                Admitted::Invoke { tool: tool_id(tool, digest), inputs: Digest::of_json(inputs) }
            }
            A::Emit { record } => Admitted::Emit { record: Digest::of_json(record) },
            A::Submit { artifact } => Admitted::Submit { artifact: artifact.clone() },
            A::Vote { verdict, artifact, evidence, rules_epoch } => Admitted::Vote {
                verdict: *verdict,
                artifact: artifact.clone(),
                evidence: evidence.clone(),
                rules_epoch: *rules_epoch,
            },
            A::RunInvoke { tool, digest, inputs } => {
                Admitted::RunInvoke { tool: tool_id(tool, digest), inputs: Digest::of_json(inputs), break_glass }
            }
            A::RunEmit { record } => Admitted::RunEmit { record: Digest::of_json(record) },
        }
    }

    pub fn kind(&self) -> ActionKind {
        match self {
            Admitted::Read { .. } => ActionKind::Read,
            Admitted::Draft { .. } => ActionKind::Draft,
            Admitted::Invoke { .. } => ActionKind::Invoke,
            Admitted::Emit { .. } => ActionKind::Emit,
            Admitted::Submit { .. } => ActionKind::Submit,
            Admitted::Vote { .. } => ActionKind::Vote,
            Admitted::RunInvoke { .. } => ActionKind::RunInvoke,
            Admitted::RunEmit { .. } => ActionKind::RunEmit,
        }
    }
}

/// Which bundle engine produced the bundle decision.
#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum BundleEngine {
    Sidecar,
    LocalWasm,
}

/// An admit decision as it enters the log: forensic class F1 (ADR-0028). Everything needed to
/// attribute the effect, and nothing that is cognitive payload.
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct AdmitRecord {
    pub seat: SeatId,
    pub lease: LogIndex,
    pub epoch: Epoch,
    pub action: Admitted,
    /// Digest of the frozen input both tiers evaluated (ADR-0030 §4).
    pub input: Digest,
    pub floor: Digest,
    pub schema: Digest,
    pub floor_reasons: Vec<String>,
    pub bundle: Digest,
    pub engine: BundleEngine,
    pub params: Digest,
    /// The replica that decided. Its host runs the effect after the entry commits.
    pub decided_by: u32,
}

/// One log entry. `id` is unique per proposal so a retried proposal applies at most once.
#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
#[serde(tag = "entry")]
pub enum Entry {
    Grant {
        id: String,
        req: GrantRequest,
    },
    Renew {
        id: String,
        req: RenewRequest,
    },
    Admit {
        id: String,
        rec: AdmitRecord,
    },
    EndRound {
        id: String,
        seat: SeatId,
        fence: LogIndex,
        reason: EndReason,
        attribution: String,
    },
    /// Revocation (ADR-0031 §5): increments the epoch, fencing every lease at the old one.
    /// Stop attribution, forensic class F2.
    EpochIncrement {
        id: String,
        reason: String,
        attribution: String,
    },
    /// An anchor issuance: forensic class F4.
    Issue {
        id: String,
        issuance: Issuance,
    },
    /// PROVISIONAL (gate runner): who runs the ADR-0007 gates and how their evidence is
    /// authenticated is unspecified; the baseline records it from the operator channel.
    GatesPassed {
        id: String,
        artifact: Digest,
        evidence: Digest,
    },
    /// One break-glass approval by a roster key, scoped to (seat, epoch). F5 is the invocation
    /// admitted under it.
    BreakGlassApprove {
        id: String,
        seat: SeatId,
        epoch: Epoch,
        approval: Signed,
    },
}

impl Entry {
    pub fn id(&self) -> &str {
        match self {
            Entry::Grant { id, .. }
            | Entry::Renew { id, .. }
            | Entry::Admit { id, .. }
            | Entry::EndRound { id, .. }
            | Entry::EpochIncrement { id, .. }
            | Entry::Issue { id, .. }
            | Entry::GatesPassed { id, .. }
            | Entry::BreakGlassApprove { id, .. } => id,
        }
    }
}

/// Why the mechanism refuses an action before or after consulting policy.
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub enum MechanismDeny {
    UnknownLease,
    WrongSeat,
    /// The epoch fence (ADR-0022 §2). Rejected by the mechanism, not by policy.
    FencedEpoch {
        lease: Epoch,
        current: Epoch,
    },
    RequestEpochMismatch {
        request: Epoch,
        lease: Epoch,
    },
    /// PROVISIONAL (rules-epoch fence): a lease granted under superseded rules.
    FencedRulesEpoch {
        lease: RulesEpoch,
        current: RulesEpoch,
    },
    LeaseEnded(EndReason),
    LeaseExpired,
    NotInAlphabet(ActionKind),
    RoundBoundReached(u64),
    ArtifactNotSubmitted,
    ArtifactAlreadySubmitted,
    GatesNotPassed,
    EvidenceMismatch,
    AlreadyPromoted,
    Other(String),
}

impl fmt::Display for MechanismDeny {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{self:?}")
    }
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub enum Applied {
    LeaseGranted {
        fence: LogIndex,
    },
    Renewed {
        fence: LogIndex,
    },
    Admitted {
        emit_seq: Option<u64>,
        promoted: Option<Digest>,
    },
    RoundEnded,
    EpochIncremented {
        epoch: Epoch,
    },
    Issued {
        rules_epoch: RulesEpoch,
    },
    GatesRecorded,
    BreakGlassApproved {
        approvals: usize,
    },
    /// The entry was ordered but voided by the deterministic apply-time check.
    Rejected(String),
    /// A retried proposal whose id was already applied.
    Duplicate,
}

/// The replicated state. Identical on every replica after applying the same log prefix.
#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct State {
    /// The rules-epoch chain this state belongs to: the digest of its genesis rules. A
    /// re-genesis starts a new chain (ADR-0025).
    pub chain: Digest,
    pub epoch: Epoch,
    pub rules: Rules,
    pub floor_exceptions: usize,
    pub leases: BTreeMap<LogIndex, LeaseRecord>,
    pub live_by_seat: BTreeMap<SeatId, LogIndex>,
    pub last_round: BTreeMap<SeatId, Round>,
    pub candidates: BTreeMap<Digest, Candidate>,
    pub gates: BTreeMap<Digest, Digest>,
    /// seat → epoch → approving roster keys.
    pub break_glass: BTreeMap<SeatId, BTreeMap<Epoch, BTreeSet<KeyHex>>>,
    /// PROVISIONAL (dedupe growth): unbounded; no snapshotting or compaction yet.
    pub applied_ids: BTreeSet<String>,
    pub last_applied: LogIndex,
}

pub const BREAK_GLASS_PURPOSE: &str = "break-glass";

impl State {
    /// Epoch 0. The runtime analogue of the unwritten `GenesisSatisfiesFloor` invariant: the
    /// mechanism refuses to start on rules that violate the rules floor (ADR-0027).
    pub fn genesis(rules: Rules, floor_exceptions: usize) -> Result<Self, Vec<Violation>> {
        let mut bad = rules::check_well_formed(&rules);
        bad.extend(rules::check_rules_floor(&rules, floor_exceptions));
        if !bad.is_empty() {
            return Err(bad);
        }
        Ok(State {
            chain: Digest::of_json(&rules),
            epoch: 0,
            rules,
            floor_exceptions,
            leases: BTreeMap::new(),
            live_by_seat: BTreeMap::new(),
            last_round: BTreeMap::new(),
            candidates: BTreeMap::new(),
            gates: BTreeMap::new(),
            break_glass: BTreeMap::new(),
            applied_ids: BTreeSet::new(),
            last_applied: 0,
        })
    }

    pub fn live_lease(&self, seat: &str) -> Option<&LeaseRecord> {
        self.live_by_seat.get(seat).and_then(|f| self.leases.get(f))
    }

    pub fn break_glass_quorum(&self, seat: &str) -> bool {
        let Some(bg) = &self.rules.break_glass else { return false };
        if !bg.actions.contains(ActionKind::RunInvoke.as_str()) {
            return false;
        }
        self.break_glass
            .get(seat)
            .and_then(|by_epoch| by_epoch.get(&self.epoch))
            .is_some_and(|keys| keys.len() >= bg.quorum as usize)
    }

    /// The mechanism checks that precede policy, in the order the corpus fixes: the epoch fence
    /// first (ADR-0022 §2), then the lease. Used both before the floor is consulted and again
    /// at apply time.
    pub fn check_live(&self, req: &ActionRequest, params: &Params) -> Result<&LeaseRecord, MechanismDeny> {
        let rec = self.leases.get(&req.lease).ok_or(MechanismDeny::UnknownLease)?;
        if rec.lease.seat != req.seat {
            return Err(MechanismDeny::WrongSeat);
        }
        if rec.lease.epoch != self.epoch {
            return Err(MechanismDeny::FencedEpoch { lease: rec.lease.epoch, current: self.epoch });
        }
        if req.epoch != rec.lease.epoch {
            return Err(MechanismDeny::RequestEpochMismatch { request: req.epoch, lease: rec.lease.epoch });
        }
        if rec.lease.rules_epoch != self.rules.rules_epoch {
            return Err(MechanismDeny::FencedRulesEpoch {
                lease: rec.lease.rules_epoch,
                current: self.rules.rules_epoch,
            });
        }
        if let Some(r) = rec.ended {
            return Err(MechanismDeny::LeaseEnded(r));
        }
        let kind = req.action.kind();
        if !rec.lease.alphabet.contains(&kind) {
            return Err(MechanismDeny::NotInAlphabet(kind));
        }
        if rec.actions >= params.round_bound {
            return Err(MechanismDeny::RoundBoundReached(params.round_bound));
        }
        self.check_action_preconditions(req)?;
        Ok(rec)
    }

    /// Action-specific mechanism preconditions. `Vote` is enabled only once the gates have
    /// passed (ADR-0024 §4), and only on a submitted artifact.
    fn check_action_preconditions(&self, req: &ActionRequest) -> Result<(), MechanismDeny> {
        use crate::action::Action as A;
        match &req.action {
            A::Submit { artifact } if self.candidates.contains_key(artifact) => {
                Err(MechanismDeny::ArtifactAlreadySubmitted)
            }
            A::Vote { artifact, evidence, .. } => {
                let c = self.candidates.get(artifact).ok_or(MechanismDeny::ArtifactNotSubmitted)?;
                if c.promoted_at.is_some() {
                    return Err(MechanismDeny::AlreadyPromoted);
                }
                match self.gates.get(artifact) {
                    None => Err(MechanismDeny::GatesNotPassed),
                    Some(e) if e != evidence => Err(MechanismDeny::EvidenceMismatch),
                    Some(_) => Ok(()),
                }
            }
            _ => Ok(()),
        }
    }

    fn end_lease(&mut self, fence: LogIndex, reason: EndReason) {
        if let Some(rec) = self.leases.get_mut(&fence)
            && rec.ended.is_none()
        {
            rec.ended = Some(reason);
            if self.live_by_seat.get(&rec.lease.seat) == Some(&fence) {
                self.live_by_seat.remove(&rec.lease.seat);
            }
        }
    }

    fn end_all_live(&mut self, reason: EndReason) {
        let fences: Vec<LogIndex> = self.live_by_seat.values().copied().collect();
        for f in fences {
            self.end_lease(f, reason);
        }
    }

    /// Apply one committed entry at log index `index`. Deterministic.
    pub fn apply(&mut self, index: LogIndex, entry: &Entry, params: &Params) -> Applied {
        self.last_applied = index;
        if !self.applied_ids.insert(entry.id().to_string()) {
            return Applied::Duplicate;
        }
        match entry {
            Entry::Grant { req, .. } => self.apply_grant(index, req),
            Entry::Renew { req, .. } => self.apply_renew(index, req),
            Entry::Admit { rec, .. } => self.apply_admit(index, rec, params),
            Entry::EndRound { seat, fence, reason, .. } => match self.leases.get(fence) {
                Some(r) if &r.lease.seat == seat && r.live() => {
                    self.end_lease(*fence, *reason);
                    Applied::RoundEnded
                }
                _ => Applied::Rejected("no such live lease".into()),
            },
            Entry::EpochIncrement { .. } => {
                self.epoch += 1;
                self.end_all_live(EndReason::Fenced);
                Applied::EpochIncremented { epoch: self.epoch }
            }
            Entry::Issue { issuance, .. } => {
                match rules::validate_issuance(&self.rules, issuance, self.floor_exceptions) {
                    Ok(()) => {
                        self.rules = issuance.rules.clone();
                        // Any rules-epoch change voids in-flight votes (ADR-0024 §3): the tally
                        // compares each vote's rules epoch, so nothing to clear here.
                        self.end_all_live(EndReason::RulesChanged);
                        Applied::Issued { rules_epoch: self.rules.rules_epoch }
                    }
                    Err(v) => Applied::Rejected(v.iter().map(ToString::to_string).collect::<Vec<_>>().join("; ")),
                }
            }
            Entry::GatesPassed { artifact, evidence, .. } => {
                self.gates.insert(artifact.clone(), evidence.clone());
                Applied::GatesRecorded
            }
            Entry::BreakGlassApprove { seat, epoch, approval, .. } => {
                let Some(bg) = &self.rules.break_glass else {
                    return Applied::Rejected("no break-glass roster is issued".into());
                };
                if *epoch != self.epoch {
                    return Applied::Rejected("approval is for a fenced epoch".into());
                }
                let body = serde_json::json!({ "seat": seat, "epoch": epoch });
                if !bg.roster.contains(&approval.key) || !authentic::verify(BREAK_GLASS_PURPOSE, &body, approval) {
                    return Applied::Rejected("approval is not from the break-glass roster".into());
                }
                let set = self.break_glass.entry(seat.clone()).or_default().entry(*epoch).or_default();
                set.insert(approval.key.clone());
                Applied::BreakGlassApproved { approvals: set.len() }
            }
        }
    }

    fn apply_grant(&mut self, index: LogIndex, req: &GrantRequest) -> Applied {
        let Some(domain) = self.rules.seat_domain(&req.seat) else {
            return Applied::Rejected(format!("seat {} is not declared in the rules", req.seat));
        };
        // ADR-0031 §2: at most one live lease; a grant requires that none is live.
        if self.live_by_seat.contains_key(&req.seat) {
            return Applied::Rejected("a live lease exists; widening authority requires ending the round".into());
        }
        if let Some(k) = req.alphabet.iter().find(|k| k.domain() != domain) {
            return Applied::Rejected(format!("{k} is outside the {} alphabet", domain.as_str()));
        }
        if req.role == RoundRole::Voter && domain != Domain::Build {
            return Applied::Rejected("only Build seats vote".into());
        }
        if req.confinement.rung > MAX_RUNG {
            return Applied::Rejected("no such confinement rung".into());
        }
        if self.last_round.get(&req.seat).is_some_and(|r| req.round <= *r) {
            return Applied::Rejected("round numbers are not reused: a round's topic is sealed".into());
        }
        let lease = Lease {
            principal: req.principal.clone(),
            seat: req.seat.clone(),
            persona: req.persona.clone(),
            epoch: self.epoch,
            fence: index,
            rules_epoch: self.rules.rules_epoch,
            bundle: req.bundle.clone(),
            confinement: req.confinement.clone(),
            alphabet: req.alphabet.clone(),
            round: req.round,
            role: req.role,
            ttl_ms: req.ttl_ms,
        };
        self.leases.insert(index, LeaseRecord { lease, ended: None, actions: 0, emit_seq: 0 });
        self.live_by_seat.insert(req.seat.clone(), index);
        self.last_round.insert(req.seat.clone(), req.round);
        Applied::LeaseGranted { fence: index }
    }

    /// A renewal replaces the live lease with a narrower one at a new fence (ADR-0031 §4).
    fn apply_renew(&mut self, index: LogIndex, req: &RenewRequest) -> Applied {
        let Some(old) = self.leases.get(&req.fence) else {
            return Applied::Rejected("unknown lease".into());
        };
        if old.lease.seat != req.seat || !old.live() {
            return Applied::Rejected("renewal names a lease that is not the seat's live lease".into());
        }
        if old.lease.epoch != self.epoch || old.lease.rules_epoch != self.rules.rules_epoch {
            return Applied::Rejected("renewal of a fenced lease".into());
        }
        let mut new = old.lease.clone();
        new.fence = index;
        new.alphabet = req.alphabet.clone();
        new.confinement.rung = req.rung;
        new.ttl_ms = req.ttl_ms;
        if let Err(e) = old.lease.check_renewal(&new) {
            return Applied::Rejected(e);
        }
        let rec = LeaseRecord { lease: new, ..old.clone() };
        let old_fence = req.fence;
        if let Some(o) = self.leases.get_mut(&old_fence) {
            o.ended = Some(EndReason::Renewed);
        }
        self.leases.insert(index, rec);
        self.live_by_seat.insert(req.seat.clone(), index);
        Applied::Renewed { fence: index }
    }

    fn apply_admit(&mut self, index: LogIndex, rec: &AdmitRecord, params: &Params) -> Applied {
        if rec.params != params.digest() {
            return Applied::Rejected("admit was decided under different mechanism parameters".into());
        }
        // Re-run the state-dependent checks against the state at this log position.
        let probe = ActionRequest {
            seat: rec.seat.clone(),
            lease: rec.lease,
            epoch: rec.epoch,
            action: probe_action(&rec.action),
        };
        if let Err(d) = self.check_live(&probe, params) {
            return Applied::Rejected(format!("fenced between decision and commit: {d}"));
        }
        let fence = rec.lease;
        let lr = self.leases.get_mut(&fence).expect("checked");
        lr.actions += 1;
        let mut emit_seq = None;
        let mut promoted = None;
        match &rec.action {
            Admitted::Emit { .. } | Admitted::RunEmit { .. } => {
                lr.emit_seq += 1;
                emit_seq = Some(lr.emit_seq);
            }
            Admitted::Submit { artifact } => {
                self.candidates.insert(
                    artifact.clone(),
                    Candidate {
                        artifact: artifact.clone(),
                        author: rec.seat.clone(),
                        votes: BTreeMap::new(),
                        promoted_at: None,
                    },
                );
                self.end_lease(fence, EndReason::Submitted);
            }
            Admitted::Vote { verdict, artifact, evidence, rules_epoch } => {
                let c = self.candidates.get_mut(artifact).expect("checked");
                c.votes.insert(
                    rec.seat.clone(),
                    VoteRecord { verdict: *verdict, evidence: evidence.clone(), rules_epoch: *rules_epoch },
                );
                if tally(c, &self.rules, self.gates.get(artifact)) == Tally::Promoted {
                    c.promoted_at = Some(index);
                    promoted = Some(artifact.clone());
                }
                self.end_lease(fence, EndReason::Voted);
            }
            _ => {}
        }
        Applied::Admitted { emit_seq, promoted }
    }
}

/// Rebuild an `Action` shape sufficient for `check_live` from the control-plane summary. Only
/// the variant and the fields the preconditions read matter; payloads are not needed.
fn probe_action(a: &Admitted) -> crate::action::Action {
    use crate::action::Action as A;
    let none = serde_json::Map::new;
    match a {
        Admitted::Read { object } => A::Read { object: object.clone() },
        Admitted::Draft { target, .. } => A::Draft { target: target.clone(), content: String::new() },
        Admitted::Invoke { .. } => A::Invoke { tool: String::new(), digest: Digest(String::new()), inputs: none() },
        Admitted::Emit { .. } => A::Emit { record: serde_json::Value::Null },
        Admitted::Submit { artifact } => A::Submit { artifact: artifact.clone() },
        Admitted::Vote { verdict, artifact, evidence, rules_epoch } => A::Vote {
            verdict: *verdict,
            artifact: artifact.clone(),
            evidence: evidence.clone(),
            rules_epoch: *rules_epoch,
        },
        Admitted::RunInvoke { .. } => {
            A::RunInvoke { tool: String::new(), digest: Digest(String::new()), inputs: none() }
        }
        Admitted::RunEmit { .. } => A::RunEmit { record: serde_json::Value::Null },
    }
}
