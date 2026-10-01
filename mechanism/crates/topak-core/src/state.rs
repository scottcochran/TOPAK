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
use crate::observer::{Heartbeat, ObserverValues};
use crate::promotion::{Candidate, Tally, VoteRecord, tally_with_coverage};
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
    /// Run tool allowlist, by `name@digest` (ADR-0040 §3). What channel each entry declares is
    /// bundle data (`policies/data.json`), PROVISIONAL until a record writes the entry's schema.
    pub run_tools: BTreeSet<String>,
    /// The pinned, content-addressed Run root (ADR-0040 §3). `Consult` is scoped to it. It is
    /// its own set: an object in Build's corpus root is not thereby in Run's.
    #[serde(default)]
    pub run_root: BTreeSet<Digest>,
    /// Maximum admitted actions per round (termination; bounds the state space). Build's `R`
    /// (ADR-0022 §3).
    pub round_bound: u64,
    /// Run's `R` (ADR-0039 §1, a placeholder of 64 in the dev rules). `None` reads as Build's,
    /// which is what the reference did before 2026.09.29.
    #[serde(default)]
    pub run_round_bound: Option<u64>,
    /// Asymmetric margin subtracted from every lease TTL (ADR-0032 §2).
    pub lease_margin_ms: u64,
    /// Most denial records written to one round's `after` topic before a single overflow marker
    /// (ADR-0003 A2). Bounds what a principal can make the mechanism write by acting
    /// under a dead lease.
    #[serde(default = "default_after_topic_limit")]
    pub after_topic_limit: u64,
}

fn default_after_topic_limit() -> u64 {
    64
}

impl Params {
    pub fn digest(&self) -> Digest {
        Digest::of_json(self)
    }

    pub fn round_bound_for(&self, domain: Domain) -> u64 {
        match domain {
            Domain::Build => self.round_bound,
            Domain::Run => self.run_round_bound.unwrap_or(self.round_bound),
        }
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
    /// The epoch was incremented: the fleet fence (ADR-0031 §5).
    Fenced,
    /// A targeted revocation named this lease's principal, Persona or confinement profile
    /// (ADR-0031 §5 R3).
    Revoked,
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
    /// The per-principal sequence number an Observer's watermark is over. In Build it counts
    /// emissions, the ADR-0015 residual for admit-to-emit order. In Run it counts effect-bearing
    /// admits, `Actuate` and `Report`, and not `Consult` (ADR-0042 §2). Counting reports only is
    /// D-0042-1, and `RunCoupling.tla`'s `M_EMITSEQ`.
    pub seq: u64,
}

impl LeaseRecord {
    pub fn live(&self) -> bool {
        self.ended.is_none()
    }
}

/// What a targeted revocation names (ADR-0031 §5 R3). It ends every live lease it matches and
/// bars every later grant it would match. Revocation is permanent within a chain.
#[derive(Clone, Debug, PartialEq, Eq, PartialOrd, Ord, Serialize, Deserialize)]
#[serde(tag = "kind", content = "id", rename_all = "snake_case")]
pub enum RevocationTarget {
    Principal(String),
    Persona(Digest),
    Confinement(Digest),
}

impl RevocationTarget {
    pub fn matches(&self, principal: &str, persona: &Digest, confinement: &Digest) -> bool {
        match self {
            RevocationTarget::Principal(p) => p == principal,
            RevocationTarget::Persona(d) => d == persona,
            RevocationTarget::Confinement(d) => d == confinement,
        }
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
    Read {
        object: Digest,
    },
    Draft {
        target: String,
        content: Digest,
    },
    Invoke {
        tool: String,
        inputs: Digest,
    },
    Emit {
        record: Digest,
    },
    Submit {
        artifact: Digest,
    },
    Vote {
        verdict: Verdict,
        artifact: Digest,
        evidence: Digest,
        rules_epoch: RulesEpoch,
    },
    Consult {
        object: Digest,
    },
    Actuate {
        tool: String,
        inputs: Digest,
        break_glass: bool,
    },
    Report {
        record: Digest,
    },
    /// An observer seat's heartbeat (ADR-0039 §1), carried verbatim: it is a fact, and every
    /// replica applies the mark from the log. `via` is the emission variant it arrived as.
    Heartbeat {
        via: ActionKind,
        topic: String,
        watermark: u64,
    },
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
            A::Emit { record } => match Heartbeat::parse(record) {
                Some(h) => Admitted::Heartbeat { via: ActionKind::Emit, topic: h.topic, watermark: h.watermark },
                None => Admitted::Emit { record: Digest::of_json(record) },
            },
            A::Submit { artifact } => Admitted::Submit { artifact: artifact.clone() },
            A::Vote { verdict, artifact, evidence, rules_epoch } => Admitted::Vote {
                verdict: *verdict,
                artifact: artifact.clone(),
                evidence: evidence.clone(),
                rules_epoch: *rules_epoch,
            },
            A::Consult { object } => Admitted::Consult { object: object.clone() },
            A::Actuate { tool, digest, inputs } => {
                Admitted::Actuate { tool: tool_id(tool, digest), inputs: Digest::of_json(inputs), break_glass }
            }
            A::Report { record } => match Heartbeat::parse(record) {
                Some(h) => Admitted::Heartbeat { via: ActionKind::Report, topic: h.topic, watermark: h.watermark },
                None => Admitted::Report { record: Digest::of_json(record) },
            },
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
            Admitted::Consult { .. } => ActionKind::Consult,
            Admitted::Actuate { .. } => ActionKind::Actuate,
            Admitted::Report { .. } => ActionKind::Report,
            Admitted::Heartbeat { via, .. } => *via,
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
    /// Targeted revocation (ADR-0031 §5 R3): ends the matching live leases and bars later
    /// grants. The epoch is untouched. Ordered, no quorum. Stop attribution, forensic class F2.
    Revoke {
        id: String,
        target: RevocationTarget,
        reason: String,
        attribution: String,
    },
    /// The fleet fence (ADR-0031 §5): increments the epoch, fencing every lease at the old one.
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
            | Entry::Revoke { id, .. }
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
    /// A malformed or dishonest heartbeat (ADR-0039 §1): from a non-observer, naming no round of
    /// a Thinker in its reach, above what exists, or below its last watermark.
    BadHeartbeat(String),
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
        seq: Option<u64>,
        promoted: Option<Digest>,
    },
    RoundEnded,
    /// A targeted revocation applied; `ended` live leases matched it.
    Revoked {
        ended: usize,
    },
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
    /// Targeted revocations in force (ADR-0031 §5 R3). Checked at every grant.
    pub revoked: BTreeSet<RevocationTarget>,
    /// PROVISIONAL (dedupe growth): unbounded; no snapshotting or compaction yet.
    pub applied_ids: BTreeSet<String>,
    pub last_applied: LogIndex,
    /// The policy-floor values the lift reads (ADR-0039 §1). Set from the linked floor at
    /// startup; the default is the placeholders, for states built without one.
    #[serde(default)]
    pub observer: ObserverValues,
    /// `mark(o, topic)` (ADR-0039 §1): observer seat → watched round topic → watermark. Kept per
    /// seat, not per lease, so an Observer's next lease continues where its last left off.
    #[serde(default)]
    pub marks: BTreeMap<SeatId, BTreeMap<String, u64>>,
    /// The seal of each Thinker seat's last ended round: its topic and its final sequence
    /// number. Read by the cross-round grant condition (ADR-0039 §2) and by coverage (§3).
    #[serde(default)]
    pub seals: BTreeMap<SeatId, Seal>,
    /// A trace name, set by a test or an operator: with `TOPAK_TRACE_DIR`, every `apply` is
    /// recorded for checking against `spec/Mechanism.tla` (`trace.rs`). Never replicated state.
    #[serde(skip)]
    pub trace: Option<String>,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct Seal {
    pub topic: String,
    pub seq: u64,
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
            revoked: BTreeSet::new(),
            applied_ids: BTreeSet::new(),
            last_applied: 0,
            observer: ObserverValues::default(),
            marks: BTreeMap::new(),
            seals: BTreeMap::new(),
            trace: None,
        })
    }

    fn topic_of(&self, rec: &LeaseRecord) -> Option<String> {
        let d = self.rules.seat_domain(&rec.lease.seat)?;
        Some(crate::lift::topic_name(&self.chain, d, &rec.lease.seat, rec.lease.epoch, rec.lease.round))
    }

    fn mark(&self, observer: &str, topic: &str) -> u64 {
        self.marks.get(observer).and_then(|m| m.get(topic)).copied().unwrap_or(0)
    }

    /// The deterministic half of `live(o)` (ADR-0039 §1, conditions 1 and 3) for some cell
    /// Observer of `thinker`: a live lease and a watermark within K of the Thinker's sequence,
    /// which in Run counts every effect-bearing admit (ADR-0042 §2).
    /// The strict form, so that after the admit being decided at most K are unread (the
    /// `Coupling.tla` finding). Re-checked at apply; the heartbeat's freshness (condition 2)
    /// is a per-replica clock and is checked at decide only, as lease expiry is.
    pub fn observer_covers(&self, thinker: &str, fresh: &dyn Fn(&str) -> bool) -> bool {
        let Some(t) = self.live_lease(thinker) else { return false };
        let Some(topic) = self.topic_of(t) else { return false };
        self.rules.cell_observers(thinker).iter().any(|o| {
            self.live_lease(o).is_some() && fresh(o) && t.seq.saturating_sub(self.mark(o, &topic)) < self.observer.k
        })
    }

    /// ADR-0039 §3 (ADR-0024 A2.3, pending): the author's cell Observer has reported reading
    /// the author's round to its seal.
    pub fn author_covered(&self, author: &str) -> bool {
        let Some(seal) = self.seals.get(author) else { return false };
        self.rules.cell_observers(author).iter().any(|o| self.mark(o, &seal.topic) >= seal.seq)
    }

    /// ADR-0039 §1: a heartbeat names a round of a Thinker in the observer's reach, its watermark
    /// is at most what exists in that round and at least the last one reported.
    fn check_heartbeat(&self, seat: &str, h: &Heartbeat) -> Result<(), MechanismDeny> {
        let bad = |s: &str| Err(MechanismDeny::BadHeartbeat(s.into()));
        if self.rules.seat_kind(seat) != Some(SeatKind::Observer) {
            return bad("only an observer seat reports liveness");
        }
        let mut found = None;
        for (t, d) in &self.rules.seats {
            if d.kind != SeatKind::Thinker {
                continue;
            }
            if let Some(rec) = self.live_lease(t)
                && self.topic_of(rec).as_deref() == Some(&h.topic)
            {
                found = Some((t.clone(), rec.seq));
            } else if let Some(seal) = self.seals.get(t)
                && seal.topic == h.topic
            {
                found = Some((t.clone(), seal.seq));
            }
        }
        let Some((thinker, upper)) = found else { return bad("names no round of a Thinker") };
        if !self.rules.watches(seat, &thinker) {
            return bad("the watched Thinker is outside this observer's reach");
        }
        if h.watermark > upper {
            return bad("watermark is above what exists in the round");
        }
        if h.watermark < self.mark(seat, &h.topic) {
            return bad("watermark falls below the last one reported");
        }
        Ok(())
    }

    pub fn live_lease(&self, seat: &str) -> Option<&LeaseRecord> {
        self.live_by_seat.get(seat).and_then(|f| self.leases.get(f))
    }

    pub fn break_glass_quorum(&self, seat: &str) -> bool {
        let Some(bg) = &self.rules.break_glass else { return false };
        if !bg.actions.contains(ActionKind::Actuate.as_str()) {
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
        let bound = params.round_bound_for(self.rules.seat_domain(&req.seat).unwrap_or(Domain::Build));
        if rec.actions >= bound {
            return Err(MechanismDeny::RoundBoundReached(bound));
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
            A::Emit { record } | A::Report { record } => match Heartbeat::parse(record) {
                Some(h) => self.check_heartbeat(&req.seat, &h),
                None => Ok(()),
            },
            _ => Ok(()),
        }
    }

    fn end_lease(&mut self, fence: LogIndex, reason: EndReason) {
        let Some(rec) = self.leases.get(&fence) else { return };
        if rec.ended.is_some() {
            return;
        }
        // ADR-0039 §2, §3: a Thinker's round seals at its final sequence number. In Run that
        // number counts invocations as well as reports, so coverage to the seal covers both
        // (ADR-0042 §5). A renewal does not come through here: the round continues.
        let seal = (self.rules.seat_kind(&rec.lease.seat) == Some(SeatKind::Thinker))
            .then(|| self.topic_of(rec).map(|topic| (rec.lease.seat.clone(), Seal { topic, seq: rec.seq })))
            .flatten();
        let rec = self.leases.get_mut(&fence).expect("present");
        rec.ended = Some(reason);
        if self.live_by_seat.get(&rec.lease.seat) == Some(&fence) {
            self.live_by_seat.remove(&rec.lease.seat);
        }
        if let Some((seat, seal)) = seal {
            self.seals.insert(seat, seal);
        }
    }

    fn end_all_live(&mut self, reason: EndReason) {
        let fences: Vec<LogIndex> = self.live_by_seat.values().copied().collect();
        for f in fences {
            self.end_lease(f, reason);
        }
    }

    /// Apply one committed entry at log index `index`. Deterministic. With a trace name and
    /// `TOPAK_TRACE_DIR` set, the step is recorded for `spec/Mechanism.tla` (`trace.rs`).
    pub fn apply(&mut self, index: LogIndex, entry: &Entry, params: &Params) -> Applied {
        if crate::trace::enabled(self) {
            let oracle = crate::trace::oracle(self, entry, params);
            let pre = self.clone();
            let applied = self.apply_inner(index, entry, params);
            crate::trace::record(&pre, self, index, entry, &applied, oracle, params);
            return applied;
        }
        self.apply_inner(index, entry, params)
    }

    fn apply_inner(&mut self, index: LogIndex, entry: &Entry, params: &Params) -> Applied {
        self.last_applied = index;
        if !self.applied_ids.insert(entry.id().to_string()) {
            return Applied::Duplicate;
        }
        match entry {
            Entry::Grant { req, .. } => self.apply_grant(index, req),
            Entry::Renew { req, .. } => self.apply_renew(index, req),
            Entry::Admit { rec, .. } => self.apply_admit(index, rec, params),
            // ADR-0042 §5: a Run principal cannot end its own round. Abstention is `Submit(⊥)`
            // and belongs to Build; a Run round ends when its lease ends.
            Entry::EndRound { seat, reason: EndReason::Abstained, .. }
                if self.rules.seat_domain(seat) == Some(Domain::Run) =>
            {
                Applied::Rejected("a Run seat cannot abstain: its round ends with its lease (ADR-0042 §5)".into())
            }
            Entry::EndRound { seat, fence, reason, .. } => match self.leases.get(fence) {
                Some(r) if &r.lease.seat == seat && r.live() => {
                    self.end_lease(*fence, *reason);
                    Applied::RoundEnded
                }
                _ => Applied::Rejected("no such live lease".into()),
            },
            Entry::Revoke { target, .. } => self.apply_revoke(target),
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
        // ADR-0037 §4: the alphabet is bounded by the seat's kind. The floor states the same
        // bound (B10, B6); like recusal, it is enforced twice.
        let kind = self.rules.seat_kind(&req.seat).expect("declared seat has a kind");
        if let Some(k) = req.alphabet.iter().find(|k| !kind.allows(**k)) {
            return Applied::Rejected(format!("{k} is outside the {kind} alphabet (ADR-0037 §4)"));
        }
        // ADR-0037 §1: a principal holds exactly one seat. `live_by_seat` keys the one-live-lease
        // rule by seat; this keys it by principal, which Seats.tla's M_SEAT shows is not the same.
        if let Some(other) =
            self.live_by_seat.values().filter_map(|f| self.leases.get(f)).find(|r| r.lease.principal == req.principal)
        {
            return Applied::Rejected(format!(
                "principal {} holds a live lease on seat {} (ADR-0037 §1)",
                req.principal, other.lease.seat
            ));
        }
        if req.role == RoundRole::Voter && domain != Domain::Build {
            return Applied::Rejected("only Build seats vote".into());
        }
        if let Some(t) = self.revoked.iter().find(|t| t.matches(&req.principal, &req.persona, &req.confinement.digest))
        {
            return Applied::Rejected(format!("revoked: {t:?} (ADR-0031 §5)"));
        }
        if req.confinement.rung > MAX_RUNG {
            return Applied::Rejected("no such confinement rung".into());
        }
        // ADR-0039 §2: in Run, a Thinker's next round is granted only once a cell Observer has
        // read its last round to the seal. Build needs no cross-round rule (§3).
        if domain == Domain::Run
            && kind == SeatKind::Thinker
            && let Some(seal) = self.seals.get(&req.seat)
            && !self.rules.cell_observers(&req.seat).iter().any(|o| self.mark(o, &seal.topic) >= seal.seq)
        {
            return Applied::Rejected(format!(
                "seat {}'s last round ({}) is unread by its cell Observer past sequence {} (ADR-0039 §2)",
                req.seat, seal.topic, seal.seq
            ));
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
        self.leases.insert(index, LeaseRecord { lease, ended: None, actions: 0, seq: 0 });
        self.live_by_seat.insert(req.seat.clone(), index);
        self.last_round.insert(req.seat.clone(), req.round);
        Applied::LeaseGranted { fence: index }
    }

    /// A targeted revocation (ADR-0031 §5 R3). Ends every live lease the target matches and
    /// lapses break-glass approvals for those seats: under the fleet fence they lapsed with the
    /// epoch, and a targeted revocation must not leave them for the seat's next holder.
    fn apply_revoke(&mut self, target: &RevocationTarget) -> Applied {
        self.revoked.insert(target.clone());
        let hit: Vec<(LogIndex, SeatId)> = self
            .live_by_seat
            .values()
            .filter_map(|f| self.leases.get(f).map(|r| (*f, r)))
            .filter(|(_, r)| target.matches(&r.lease.principal, &r.lease.persona, &r.lease.confinement.digest))
            .map(|(f, r)| (f, r.lease.seat.clone()))
            .collect();
        for (fence, seat) in &hit {
            self.end_lease(*fence, EndReason::Revoked);
            self.break_glass.remove(seat);
        }
        Applied::Revoked { ended: hit.len() }
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
        // ADR-0039 §2, re-checked at apply (ADR-0033 §4): the deterministic half of live(o).
        // Effects only: `Consult` is not coupled (ADR-0041 §2).
        if matches!(rec.action, Admitted::Actuate { .. } | Admitted::Report { .. })
            && self.rules.seat_kind(&rec.seat) == Some(SeatKind::Thinker)
            && !self.observer_covers(&rec.seat, &|_| true)
        {
            return Applied::Rejected("no cell Observer covers this seat at commit (ADR-0039 §2)".into());
        }
        let fence = rec.lease;
        let lr = self.leases.get_mut(&fence).expect("checked");
        lr.actions += 1;
        let mut seq = None;
        let mut promoted = None;
        match &rec.action {
            // ADR-0042 §2: in Run the sequence counts every effect-bearing admit, so an
            // invocation advances it as a report does. `Consult` advances `actions` only.
            Admitted::Emit { .. } | Admitted::Report { .. } | Admitted::Actuate { .. } => {
                lr.seq += 1;
                seq = Some(lr.seq);
            }
            Admitted::Heartbeat { topic, watermark, .. } => {
                lr.seq += 1;
                seq = Some(lr.seq);
                self.marks.entry(rec.seat.clone()).or_default().insert(topic.clone(), *watermark);
                // Coverage may complete a promotion whose votes are all in (ADR-0039 §3).
                let authors: Vec<SeatId> =
                    self.seals.iter().filter(|(_, s)| &s.topic == topic).map(|(a, _)| a.clone()).collect();
                for author in authors {
                    let covered = self.author_covered(&author);
                    let gates = &self.gates;
                    let rules = &self.rules;
                    for c in self.candidates.values_mut().filter(|c| c.author == author && c.promoted_at.is_none()) {
                        if tally_with_coverage(c, rules, gates.get(&c.artifact), covered) == Tally::Promoted {
                            c.promoted_at = Some(index);
                            promoted = Some(c.artifact.clone());
                        }
                    }
                }
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
                let author = self.candidates.get(artifact).expect("checked").author.clone();
                let covered = self.author_covered(&author);
                let c = self.candidates.get_mut(artifact).expect("checked");
                c.votes.insert(
                    rec.seat.clone(),
                    VoteRecord { verdict: *verdict, evidence: evidence.clone(), rules_epoch: *rules_epoch },
                );
                if tally_with_coverage(c, &self.rules, self.gates.get(artifact), covered) == Tally::Promoted {
                    c.promoted_at = Some(index);
                    promoted = Some(artifact.clone());
                }
                self.end_lease(fence, EndReason::Voted);
            }
            _ => {}
        }
        Applied::Admitted { seq, promoted }
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
        Admitted::Consult { object } => A::Consult { object: object.clone() },
        Admitted::Actuate { .. } => A::Actuate { tool: String::new(), digest: Digest(String::new()), inputs: none() },
        Admitted::Report { .. } => A::Report { record: serde_json::Value::Null },
        Admitted::Heartbeat { via, topic, watermark } => {
            let record = Heartbeat { topic: topic.clone(), watermark: *watermark }.record();
            if *via == ActionKind::Emit { A::Emit { record } } else { A::Report { record } }
        }
    }
}
