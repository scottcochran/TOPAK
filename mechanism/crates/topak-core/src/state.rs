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
use crate::confine::*;
use crate::lease::{Confinement, Lease, MAX_RUNG};
use crate::observer::{Heartbeat, ObserverValues, PersonaValues};
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
    /// The Run tools the tool host runs as Wasm modules whose only network capability is their
    /// declared target: channel fidelity by construction (ADR-0034 A2, pending; `topak-contain`
    /// `wasmtool`). PROVISIONAL (wasm-tools): a mechanism parameter so every replica can check at
    /// apply what a Run profile's P4 claims; the node refuses to start unless it hosts every one.
    #[serde(default, skip_serializing_if = "BTreeSet::is_empty")]
    pub wasm_tools: BTreeSet<String>,
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
    /// The appraisal the lease was granted, or last renewed, on (ADR-0034 §3.2). `None` at rung 0.
    #[serde(default)]
    pub attestation: Option<Attestation>,
    /// The last session-proof counter admitted under this lease's session key (ADR-0034 §3.5).
    /// Carried across renewal: the session is the guest's, not the fence's.
    #[serde(default)]
    pub session_ctr: u64,
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
    /// At rungs 2 and 3, the attested guest's proof that it sent this action (ADR-0034 §3.5).
    /// Checked again at apply, because the generation binding at `Act` is what
    /// `ContainedMeansConfined` rests on (`spec/theorem-premise-binding.md`).
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub session: Option<SessionProof>,
}

/// One log entry. `id` is unique per proposal so a retried proposal applies at most once.
#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
#[serde(tag = "entry")]
pub enum Entry {
    /// At rung ≥ 1 the grant carries the appraisal it rests on: profile digest and rung in `req`,
    /// verdict, nonce, evidence digest and session key in the statement (ADR-0034 §3.2). Every
    /// replica re-checks it at apply.
    Grant {
        id: String,
        req: GrantRequest,
        #[serde(default, skip_serializing_if = "Option::is_none")]
        appraisal: Option<Appraisal>,
    },
    /// A renewal of an attested lease re-attests the same guest with a fresh nonce (ADR-0034 §3.6).
    Renew {
        id: String,
        req: RenewRequest,
        #[serde(default, skip_serializing_if = "Option::is_none")]
        appraisal: Option<Appraisal>,
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
    /// A Contested verdict (ADR-0034 §3.3, §3.7): a targeted, permanent revocation of the
    /// principal the statement names, never its profile or Persona, with the evidence by digest.
    /// Ordered, no quorum. Stop attribution, forensic class F2.
    Contested {
        id: String,
        appraisal: Appraisal,
        attribution: String,
    },
    /// Registers a confinement profile whose single-file workspace was promoted (ADR-0034 §1).
    /// A digest nobody promoted is not a reference value. The file's bytes, verbatim.
    ProfileRegister {
        id: String,
        profile: String,
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
            | Entry::Contested { id, .. }
            | Entry::ProfileRegister { id, .. }
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
    /// A Contested principal was revoked; `ended` live leases matched.
    Contested {
        ended: usize,
    },
    ProfileRegistered {
        digest: Digest,
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
    /// `T_persona` (ADR-0031 A2): the bound on a lease's `ttl` at grant and renewal. Set from the
    /// linked floor at startup; the default is the placeholder, for states built without one.
    #[serde(default)]
    pub persona: PersonaValues,
    /// `mark(o, topic)` (ADR-0039 §1): observer seat → watched round topic → watermark. Kept per
    /// seat, not per lease, so an Observer's next lease continues where its last left off.
    #[serde(default)]
    pub marks: BTreeMap<SeatId, BTreeMap<String, u64>>,
    /// The seal of each Thinker seat's last ended round: its topic and its final sequence
    /// number. Read by the cross-round grant condition (ADR-0039 §2) and by coverage (§3).
    #[serde(default)]
    pub seals: BTreeMap<SeatId, Seal>,
    /// Registered confinement profiles by file digest (ADR-0034 §1, ADR-0036 §1).
    #[serde(default)]
    pub profiles: BTreeMap<Digest, ProfileRecord>,
    /// Principals revoked on a Contested verdict, with the evidence digest (ADR-0034 §3.7). The
    /// set `ContestedStopped` quantifies over.
    #[serde(default)]
    pub contested: BTreeMap<String, Digest>,
    /// A trace name, set by a test or an operator: with `TOPAK_TRACE_DIR`, every `apply` is
    /// recorded for checking against `spec/Mechanism.tla` (`trace.rs`). Never replicated state.
    #[serde(skip)]
    pub trace: Option<String>,
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct ProfileRecord {
    pub profile: Profile,
    /// The promoted workspace the profile was registered from.
    pub artifact: Digest,
    pub registered_at: LogIndex,
}

/// What an appraisal must match, from the request it is attached to.
struct Want<'a> {
    principal: &'a str,
    round: Round,
    profile: &'a Digest,
    persona: &'a Digest,
    rung: u8,
    /// The seat's domain: Build and Run share the schema, not the profile (ADR-0034 §1).
    domain: Domain,
    /// A renewal's nonce is from no earlier than the lease it renews.
    min_index: LogIndex,
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
            persona: PersonaValues::default(),
            marks: BTreeMap::new(),
            seals: BTreeMap::new(),
            profiles: BTreeMap::new(),
            contested: BTreeMap::new(),
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
            Entry::Grant { req, appraisal, .. } => self.apply_grant(index, req, appraisal.as_ref()),
            Entry::Renew { req, appraisal, .. } => self.apply_renew(index, req, appraisal.as_ref()),
            Entry::Contested { appraisal, .. } => self.apply_contested(appraisal),
            Entry::ProfileRegister { profile, .. } => self.apply_profile_register(index, profile),
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

    fn apply_grant(&mut self, index: LogIndex, req: &GrantRequest, appraisal: Option<&Appraisal>) -> Applied {
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
        // ADR-0034 §3.4: a grant is at the seat's declared rung or not at all. Without this an
        // Unattestable principal could be granted at rung 0 (`Confinement.tla` `M_DOWNGRADE`).
        let declared = self.rules.seats.get(&req.seat).map_or(0, |d| d.rung);
        if req.confinement.rung != declared {
            return Applied::Rejected(format!(
                "rung {} is not seat {}'s declared rung {declared}: no silent downgrade (ADR-0034 §3.4)",
                req.confinement.rung, req.seat
            ));
        }
        let attestation = match (req.confinement.rung, appraisal) {
            (0, None) => None,
            (0, Some(_)) => return Applied::Rejected("a rung-0 grant rests on no appraisal".into()),
            (_, None) => {
                return Applied::Rejected("a grant at rung 1 or above carries its appraisal (ADR-0034 §3.2)".into());
            }
            (rung, Some(a)) => {
                let want = Want {
                    principal: &req.principal,
                    round: req.round,
                    profile: &req.confinement.digest,
                    persona: &req.persona,
                    rung,
                    domain,
                    min_index: 0,
                };
                match self.check_appraisal(index, a, &want) {
                    Ok(att) => Some(att),
                    Err(e) => return Applied::Rejected(e),
                }
            }
        };
        // ADR-0031 A2: a lease's ttl is at most T_persona, so the Persona is re-attested at least
        // that often (ADR-0016 §6). Refused by the mechanism, not by policy.
        if req.ttl_ms > self.persona.t_persona_ms {
            return Applied::Rejected(format!(
                "ttl {} ms exceeds T_persona {} ms (ADR-0031 A2)",
                req.ttl_ms, self.persona.t_persona_ms
            ));
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
        self.leases.insert(index, LeaseRecord { lease, ended: None, actions: 0, seq: 0, attestation, session_ctr: 0 });
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
    fn apply_renew(&mut self, index: LogIndex, req: &RenewRequest, appraisal: Option<&Appraisal>) -> Applied {
        let Some(old) = self.leases.get(&req.fence) else {
            return Applied::Rejected("unknown lease".into());
        };
        if old.lease.seat != req.seat || !old.live() {
            return Applied::Rejected("renewal names a lease that is not the seat's live lease".into());
        }
        if old.lease.epoch != self.epoch || old.lease.rules_epoch != self.rules.rules_epoch {
            return Applied::Rejected("renewal of a fenced lease".into());
        }
        // ADR-0031 A2: the renewal's ttl is bounded by T_persona again.
        if req.ttl_ms > self.persona.t_persona_ms {
            return Applied::Rejected(format!(
                "renewal ttl {} ms exceeds T_persona {} ms (ADR-0031 A2)",
                req.ttl_ms, self.persona.t_persona_ms
            ));
        }
        let mut new = old.lease.clone();
        new.fence = index;
        new.alphabet = req.alphabet.clone();
        new.confinement.rung = req.rung;
        new.ttl_ms = req.ttl_ms;
        if let Err(e) = old.lease.check_renewal(&new) {
            return Applied::Rejected(e);
        }
        // ADR-0034 §3.6: an attested lease renews only on a fresh appraisal of the same guest.
        // Unattestable lets it lapse; nothing renews it at a lower rung (`M_RENEWLOW`).
        let attestation = match (&old.attestation, appraisal) {
            (None, None) => None,
            (None, Some(_)) => return Applied::Rejected("a rung-0 lease renews on no appraisal".into()),
            (Some(_), None) => {
                return Applied::Rejected("an attested lease renews only on a fresh appraisal (ADR-0034 §3.6)".into());
            }
            (Some(prev), Some(a)) => {
                let l = &old.lease;
                let want = Want {
                    principal: &l.principal,
                    round: l.round,
                    profile: &l.confinement.digest,
                    persona: &l.persona,
                    rung: l.confinement.rung,
                    domain: self.rules.seat_domain(&l.seat).unwrap_or(Domain::Build),
                    min_index: l.fence,
                };
                let att = match self.check_appraisal(index, a, &want) {
                    Ok(att) => att,
                    Err(e) => return Applied::Rejected(e),
                };
                // `Confinement.tla` `SameGuest`: the renewal is the guest the lease was granted to.
                if att.instance != prev.instance || att.session_key != prev.session_key {
                    return Applied::Rejected("renewal appraises another guest (ADR-0034 §3.6)".into());
                }
                Some(att)
            }
        };
        let rec = LeaseRecord { lease: new, attestation, ..old.clone() };
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
        // ADR-0034 A2 (pending): a Run profile's channel fidelity, re-checked at apply.
        if let Admitted::Actuate { tool, .. } = &rec.action
            && let Err(e) = self.channel_fidelity(rec.lease, tool, params)
        {
            return Applied::Rejected(e);
        }
        // ADR-0034 §3.5: under an attested session key, the action is the attested guest's. The
        // generation binding at `Act`: a proof under any other key, or a replayed counter, is void.
        let key = self.leases[&rec.lease].attestation.as_ref().and_then(|a| a.session_key.clone());
        let ctr = match (&key, &rec.session) {
            (None, _) => None,
            (Some(_), None) => {
                return Applied::Rejected("the lease's session key signed nothing (ADR-0034 §3.5)".into());
            }
            (Some(k), Some(proof)) => {
                let body = session_body(rec.lease, rec.epoch, proof.ctr, &proof.op);
                if !authentic::verify(AGENT_OP_PURPOSE, &body, &Signed { key: k.clone(), sig: proof.sig.clone() }) {
                    return Applied::Rejected("the session proof is not the attested guest's (ADR-0034 §3.5)".into());
                }
                if proof.ctr <= self.leases[&rec.lease].session_ctr {
                    return Applied::Rejected("the session proof's counter is replayed".into());
                }
                Some(proof.ctr)
            }
        };
        let fence = rec.lease;
        let lr = self.leases.get_mut(&fence).expect("checked");
        lr.actions += 1;
        if let Some(c) = ctr {
            lr.session_ctr = c;
        }
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

    /// The conditions ADR-0034 §3.2 adds to ADR-0033 §4's apply-time re-check, in the order
    /// `Mechanism.tla` `AppraisalOk` states them. One replica appraised; every replica checks.
    fn check_appraisal(&self, index: LogIndex, a: &Appraisal, w: &Want) -> Result<Attestation, String> {
        let st = &a.statement;
        if st.verdict != Appraised::Attested {
            return Err(format!("the verdict is {}: only Attested grants (ADR-0034 §3.3)", st.verdict.as_str()));
        }
        if st.rung != w.rung {
            return Err(format!("the appraisal is at rung {}, the request at {}", st.rung, w.rung));
        }
        if &st.profile != w.profile {
            return Err("the appraisal is of another profile".into());
        }
        let Some(pr) = self.profiles.get(w.profile) else {
            return Err("the profile is not registered from a promoted artifact (ADR-0034 §1)".into());
        };
        // ADR-0034 §1: Build and Run share the schema, not the profile. A Run seat is never
        // granted on a Build profile, and no Run profile exists to register (ADR-0042 §6).
        if pr.profile.domain != w.domain {
            return Err(format!(
                "a {} profile does not confine a {} seat (ADR-0034 §1)",
                pr.profile.domain.as_str(),
                w.domain.as_str()
            ));
        }
        pr.profile.check_for_rung(w.rung)?;
        // F26: one Persona digest across the lease, the profile and the statement.
        if &st.persona != w.persona || pr.profile.persona.model_json_sha256.as_ref() != Some(w.persona) {
            return Err("the Persona is not the profile's (ADR-0034 P5, P7)".into());
        }
        if st.nonce.principal != w.principal || st.nonce.round != w.round {
            return Err("the nonce names another principal or round".into());
        }
        // `Confinement.tla` `FreshEpoch`: an epoch fence invalidates every pending appraisal.
        if st.nonce.epoch != self.epoch {
            return Err(format!("the nonce is from epoch {}, fenced (ADR-0034 §3.6)", st.nonce.epoch));
        }
        if st.nonce.index >= index || st.nonce.index < w.min_index {
            return Err("the nonce is not from the log between the lease and this entry".into());
        }
        if w.rung >= 2 {
            if st.session_key.is_none() {
                return Err("rungs 2 and 3 bind a session key (ADR-0034 §3.5)".into());
            }
            // The verifier's verdict is checked against the profile's own reference values too:
            // a measurement or TCB the profile does not admit is not Attested whoever signs it.
            if st.measurement != pr.profile.reference.launch_measurement {
                return Err("the measurement is not the profile's reference value (P7)".into());
            }
            if st.tcb.unwrap_or(0) < pr.profile.reference.min_tcb.unwrap_or(0) {
                return Err("the platform TCB is below the profile's minimum (P7)".into());
            }
        }
        let verified_by = match w.rung {
            1 => {
                if st.platform != PLATFORM_LAUNCHER {
                    return Err("rung 1 is the launcher's assertion".into());
                }
                None
            }
            2 => return Err("rung 2 appraisal is not implemented (no measured-boot quote check)".into()),
            _ => Some(self.verifier_signer(a)?),
        };
        Ok(Attestation {
            verdict: st.verdict,
            n_epoch: st.nonce.epoch,
            nonce_index: st.nonce.index,
            instance: a.instance.clone(),
            session_key: st.session_key.clone(),
            evidence: st.evidence.clone(),
            verified_by,
            platform: st.platform.clone(),
        })
    }

    /// ADR-0025 §1 (f): the issued verifier key that signed the statement.
    fn verifier_signer(&self, a: &Appraisal) -> Result<KeyHex, String> {
        let sigs: Vec<Signed> = a.signature.iter().cloned().collect();
        authentic::valid_signers(APPRAISAL_PURPOSE, &a.body(), &sigs, &self.rules.verifier_keys)
            .into_iter()
            .next()
            .ok_or_else(|| "the appraisal is not signed by an issued verifier key (ADR-0025 §1 (f))".into())
    }

    /// ADR-0034 §3.3, §3.7: a Contested verdict revokes the principal, permanently, with the
    /// evidence. Rung 1 has no measurement to diverge from (`NeverContested`), so only a signed
    /// rung-3 statement may order one; the operator's `Revoke` remains for everything else.
    fn apply_contested(&mut self, a: &Appraisal) -> Applied {
        let st = &a.statement;
        if st.verdict != Appraised::Contested {
            return Applied::Rejected("the statement is not Contested".into());
        }
        match st.rung {
            0 | 1 => return Applied::Rejected("rungs 0 and 1 cannot produce Contested (ADR-0034 §7)".into()),
            2 => return Applied::Rejected("rung 2 appraisal is not implemented".into()),
            _ => {}
        }
        if let Err(e) = self.verifier_signer(a) {
            return Applied::Rejected(e);
        }
        let principal = st.nonce.principal.clone();
        let evidence = st.evidence.clone();
        let Applied::Revoked { ended } = self.apply_revoke(&RevocationTarget::Principal(principal.clone())) else {
            unreachable!("apply_revoke reports Revoked")
        };
        self.contested.insert(principal, evidence);
        Applied::Contested { ended }
    }

    /// ADR-0034 §1: a profile is a reference value only once its artifact is promoted. A Run
    /// profile is refused while ADR-0042 §6 is Proposed: Run principals are `Mediated`.
    fn apply_profile_register(&mut self, index: LogIndex, text: &str) -> Applied {
        let profile = match Profile::parse(text) {
            Ok(p) => p,
            Err(e) => return Applied::Rejected(e),
        };
        let bad = profile.check_well_formed();
        if !bad.is_empty() {
            return Applied::Rejected(format!("malformed profile: {}", bad.join("; ")));
        }
        // PROVISIONAL (run-profile): Run profiles register under ADR-0034 A2, which is pending, and
        // ADR-0042 §6, which is Proposed. What A2 makes a Run profile's P4 mean is checked at
        // every `Actuate` (`State::channel_fidelity`).
        let artifact = profile_artifact(text.as_bytes());
        if !self.candidates.get(&artifact).is_some_and(|c| c.promoted_at.is_some()) {
            return Applied::Rejected("the profile's artifact is not promoted (ADR-0034 §1)".into());
        }
        let digest = Digest::of(text.as_bytes());
        self.profiles.entry(digest.clone()).or_insert(ProfileRecord { profile, artifact, registered_at: index });
        Applied::ProfileRegistered { digest }
    }

    /// ADR-0034 A2 (pending), P4 for Run: under an attested lease whose Run profile says P4
    /// passes, an `Actuate` names only a tool the tool host holds to its declared channel
    /// (`Params::wasm_tools`). The profile's claim is made true here, at decide and at apply, and
    /// not left to the declaration. A profile that declares P4 `fail` claims nothing, and its
    /// principals are `Mediated` (D-0034-6). Rung 0 rests on no appraisal and is not checked.
    /// `RunConfinement.tla` `Fidelity`; its `M_NATIVE` drops this check.
    pub fn channel_fidelity(&self, fence: LogIndex, tool: &str, params: &Params) -> Result<(), String> {
        let Some(lr) = self.leases.get(&fence) else { return Ok(()) };
        if lr.attestation.is_none() {
            return Ok(());
        }
        let Some(pr) = self.profiles.get(&lr.lease.confinement.digest) else { return Ok(()) };
        if pr.profile.domain == Domain::Run
            && pr.profile.verdict(Clause::P4) == Some(ClauseVerdict::Pass)
            && !params.wasm_tools.contains(tool)
        {
            return Err(format!(
                "tool {tool} is not held to its declared channel, and the lease's profile says P4 passes (ADR-0034 A2)"
            ));
        }
        Ok(())
    }

    /// `Contained(p)` (ADR-0034 §4) for the lease at `fence`: a lookup, never a judgment. Every
    /// conjunct that fails is named. Rung 0 is `Mediated`, always (ADR-0031 §3).
    pub fn contained(&self, fence: LogIndex) -> Containment {
        let mut because = Vec::new();
        let Some(lr) = self.leases.get(&fence) else {
            return Containment { contained: false, because: vec!["no such lease".into()], simulated: false };
        };
        let l = &lr.lease;
        if !lr.live() {
            because.push("the lease is not live".into());
        }
        if l.confinement.rung == 0 {
            because.push("rung 0 is Mediated (ADR-0031 §3)".into());
        } else if self.rules.seats.get(&l.seat).map_or(0, |d| d.rung) != l.confinement.rung {
            because.push("the lease is not at its seat's declared rung".into());
        }
        if lr.attestation.as_ref().map(|a| a.verdict) != Some(Appraised::Attested) {
            because.push("no Attested appraisal".into());
        }
        match self.profiles.get(&l.confinement.digest) {
            None => because.push("the profile is not registered".into()),
            Some(pr) => because.extend(pr.profile.meets_p3_p5(&l.alphabet)),
        }
        if !self.rules.personas.get(&l.persona).is_some_and(|p| p.in_house()) {
            because.push("the Persona is not in house on ADR-0017's axis".into());
        }
        if self.rules.criterion.is_none() {
            because.push("ADR-0035's criterion is not in force in the issued rules".into());
        }
        // ADR-0034 §1: the profile is the seat's domain's. Apply refuses any other grant; this is
        // the second guard. A Run seat on a Run profile is `Contained` on the same conjuncts as a
        // Build seat, with P4 read as channel fidelity (ADR-0034 A2, pending).
        if let Some(pr) = self.profiles.get(&l.confinement.digest)
            && Some(pr.profile.domain) != self.rules.seat_domain(&l.seat)
        {
            because.push("the profile is not for the seat's domain (ADR-0034 §1)".into());
        }
        let simulated = lr.attestation.as_ref().is_some_and(|a| a.platform == PLATFORM_SIM_SNP);
        Containment { contained: because.is_empty(), because, simulated }
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
