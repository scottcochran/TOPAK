//! The operator as a principal (ADR-0050, provisional): the control alphabet, a seating, and what
//! the mechanism holds about an operator's request.
//!
//! An operator holds a seat of kind `operator` and signs each request with the seat's key. The
//! request is decided by the floor's control entries, `C1` to `C9`, over `ControlFacts`: thirteen
//! facts the mechanism computes about the operator, the target and the request. The operator
//! supplies none of them. The entry that is ordered carries the request, its signature and the
//! facts; every replica verifies the signature, recomputes the facts against its own state at that
//! log position, refuses the entry if they differ, and re-states the envelope (`permitted`), as
//! the grant path re-states B10 and recusal.
//!
//! A deployment whose rules declare no `operator` seat is D-0050-1, the socket: requests are
//! unsigned and from whoever reaches it. Where the rules declare one, the unsigned path is a
//! BOOTSTRAP path and does one thing, a first seating (§2): a `Grant` that is not a successor.
//! A first lease from a completed tally is not built.

use std::collections::BTreeSet;

use serde::{Deserialize, Serialize};
use serde_json::{Value, json};

use crate::authentic::{self, KeyHex, Signed};
use crate::labels::Label;
use crate::lease::Confinement;
use crate::state::RevocationTarget;
use crate::types::*;

/// Signing purposes (ADR-0025 §1 (f) for the provider's).
pub const CONTROL_PURPOSE: &str = "control";
pub const SIGN_ON_PURPOSE: &str = "sign-on";

/// What a quorum seats (ADR-0050 §2): the binding a successor grant may keep and may not widen,
/// and the labels a task for the principal may carry (§5). At the reference a seating is made by
/// the bootstrap path and not by a promotion.
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct Seating {
    pub principal: String,
    pub persona: Digest,
    pub bundle: Digest,
    pub confinement: Confinement,
    pub alphabet: BTreeSet<ActionKind>,
    pub role: RoundRole,
    pub task_labels: Label,
    pub seated_at: LogIndex,
}

/// The control alphabet (ADR-0050 §4). Three add and three deny.
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(tag = "action", rename_all = "snake_case")]
pub enum ControlAction {
    /// A successor grant: the target's next round, every field the last lease's or narrower.
    Regrant {
        target: SeatId,
        round: Round,
        alphabet: BTreeSet<ActionKind>,
        ttl_ms: u64,
        /// The round's task, by digest (§5). Its bytes travel beside the request.
        #[serde(default, skip_serializing_if = "Option::is_none")]
        task: Option<Digest>,
        /// The operator's signed declaration of the task's label (ADR-0047 §1). Required.
        #[serde(default, skip_serializing_if = "Option::is_none")]
        task_label: Option<Label>,
        /// Where the target is an operator: its sign-on assertion for this boundary (§3).
        #[serde(default, skip_serializing_if = "Option::is_none")]
        sign_on: Option<Signed>,
    },
    Renew {
        target: SeatId,
        alphabet: BTreeSet<ActionKind>,
        ttl_ms: u64,
        #[serde(default, skip_serializing_if = "Option::is_none")]
        sign_on: Option<Signed>,
    },
    AttestGates {
        artifact: Digest,
        evidence: Digest,
    },
    EndRound {
        target: SeatId,
    },
    Revoke {
        target: RevocationTarget,
        reason: String,
    },
    FenceEpoch {
        reason: String,
    },
}

impl ControlAction {
    /// The action's name in schema S.
    pub fn name(&self) -> &'static str {
        match self {
            ControlAction::Regrant { .. } => "Regrant",
            ControlAction::Renew { .. } => "Renew",
            ControlAction::AttestGates { .. } => "AttestGates",
            ControlAction::EndRound { .. } => "EndRound",
            ControlAction::Revoke { .. } => "Revoke",
            ControlAction::FenceEpoch { .. } => "FenceEpoch",
        }
    }

    pub fn is_add(&self) -> bool {
        matches!(self, ControlAction::Regrant { .. } | ControlAction::Renew { .. } | ControlAction::AttestGates { .. })
    }
}

/// One request, as the operator signs it. `epoch` fences it; `ctr` orders an operator's requests
/// so that one cannot be replayed.
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct ControlRequest {
    pub operator: SeatId,
    pub epoch: Epoch,
    pub ctr: u64,
    #[serde(flatten)]
    pub action: ControlAction,
}

impl ControlRequest {
    pub fn body(&self, chain: &Digest) -> Value {
        json!({ "chain": chain, "request": self })
    }
}

/// The facts the control entries read: schema S's `ControlCtx`, and the two the lift states as
/// attributes of the principal and the resource.
#[derive(Clone, Debug, Default, PartialEq, Eq, Serialize, Deserialize)]
pub struct ControlFacts {
    pub persona_in_force: bool,
    pub has_lease: bool,
    pub peer_live: bool,
    pub fresh_assertion: bool,
    pub target_seated: bool,
    pub target_live: bool,
    pub same_binding: bool,
    pub next_round: bool,
    pub last_alphabet: BTreeSet<String>,
    pub new_alphabet: BTreeSet<String>,
    pub task_labelled: bool,
    pub task_label: Label,
    pub task_labels_allowed: Label,
    /// The operator's domain, and the target's: `principal.domain` and `resource.domain`.
    pub domain: Option<Domain>,
    pub target_domain: Option<Domain>,
    /// The seat the request acts on, where it acts on one: the floor's resource.
    pub target_seat: Option<SeatId>,
}

impl ControlFacts {
    /// The envelope of `C1` to `C9`, restated. The floor decides a request; this is what `apply`
    /// holds every replica to, so that an entry no floor permitted is not applied. Returns the
    /// entry that refuses.
    pub fn permitted(&self, action: &ControlAction, operator: &str) -> Result<(), &'static str> {
        let own = self.domain.is_some() && self.domain == self.target_domain;
        let is_self = self.target_seat.as_deref() == Some(operator);
        if action.is_add() && (!self.has_lease || !self.peer_live) {
            return Err("C5-add-needs-lease-and-peer");
        }
        match action {
            ControlAction::Regrant { .. } => {
                if is_self {
                    return Err("C6-no-self");
                }
                if !self.task_labelled || !self.task_label.is_subset(&self.task_labels_allowed) {
                    return Err("C8-task-label-in-bounds");
                }
                let narrower = self.new_alphabet.is_subset(&self.last_alphabet);
                if !(own && self.target_seated && !self.target_live && self.same_binding && self.next_round && narrower) {
                    return Err("C1-regrant-successor");
                }
            }
            ControlAction::Renew { .. } => {
                if is_self {
                    return Err("C6-no-self");
                }
                if !(own && self.target_live) {
                    return Err("C2-renew");
                }
            }
            ControlAction::AttestGates { .. } => {
                if self.domain != Some(Domain::Build) {
                    return Err("C3-attest-gates");
                }
            }
            ControlAction::EndRound { .. } | ControlAction::Revoke { .. } | ControlAction::FenceEpoch { .. } => {
                if matches!(action, ControlAction::FenceEpoch { .. }) && !self.has_lease {
                    return Err("C7-fence-needs-lease");
                }
                if !matches!(action, ControlAction::FenceEpoch { .. }) && !own {
                    return Err("C9-stop-in-own-domain");
                }
                if !(self.persona_in_force && (self.has_lease || self.fresh_assertion)) {
                    return Err("C4-deny");
                }
            }
        }
        Ok(())
    }
}

/// A decided request, as the log carries it: what was asked, the operator's signature over it,
/// the operator's own sign-on assertion where it denies without a lease, and the facts.
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct Control {
    pub request: ControlRequest,
    pub sig: Signed,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub assertion: Option<Signed>,
    pub facts: ControlFacts,
}

/// What an identity provider signs (ADR-0050 §3): the operator's key, and the fence the mechanism
/// asks it to name. No wall clock is read: an assertion is fresh because of what it names. The
/// fence is the fleet epoch and the operator seat's last lease, so an assertion is good for one
/// lease boundary, or, for an operator with no lease, until it is seated again or the fleet is
/// fenced.
pub fn sign_on_body(chain: &Digest, key: &KeyHex, epoch: Epoch, last_fence: LogIndex) -> Value {
    json!({ "chain": chain, "key": key, "epoch": epoch, "fence": last_fence })
}

pub fn sign_on_verifies(
    providers: &BTreeSet<KeyHex>,
    chain: &Digest,
    key: &KeyHex,
    epoch: Epoch,
    last_fence: LogIndex,
    assertion: Option<&Signed>,
) -> bool {
    assertion.is_some_and(|a| {
        providers.contains(&a.key) && authentic::verify(SIGN_ON_PURPOSE, &sign_on_body(chain, key, epoch, last_fence), a)
    })
}

// ---- the emergency seating (ADR-0052, provisional) ------------------------------------------------

pub const ACTIVATION_PURPOSE: &str = "emergency-activation";

/// What an emergency seat may call (ADR-0052 §2).
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(tag = "envelope", content = "tools", rename_all = "snake_case")]
pub enum Envelope {
    /// The generic default: every Run allowlist entry in force in the domain, computed at
    /// activation and fixed for the round. It cannot go stale.
    Domain,
    /// A narrower one, named entry by entry (`name@digest`), from the seating's own bundle.
    Named(BTreeSet<String>),
}

/// An emergency seating, prepared in advance (ADR-0052 §2): the seat, the persons who may hold
/// it, its envelope, and the labels a task for it may carry. At the reference it is prepared by
/// the BOOTSTRAP path and not by a promotion.
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct EmergencySeating {
    /// The persons' signing keys. The roster's approvals name the one seated.
    pub persons: BTreeSet<KeyHex>,
    pub bundle: Digest,
    pub envelope: Envelope,
    pub task_labels: Label,
    /// A drill seating (§6): a real activation that can do nothing. Marked, and on the log.
    #[serde(default)]
    pub drill: bool,
}

/// One activation, as the roster's members sign it: one named person, one round, the round's
/// task. There is no field for the reason: why the quorum acted is unknown to the mechanism, by
/// construction (§5).
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct Activation {
    pub seat: SeatId,
    pub person: KeyHex,
    pub epoch: Epoch,
    pub round: Round,
    pub ttl_ms: u64,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub task: Option<Digest>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub task_label: Option<Label>,
}

impl Activation {
    pub fn body(&self, chain: &Digest) -> Value {
        json!({ "chain": chain, "activation": self })
    }
}

/// The forensic record of an activation (ADR-0052 §5; ADR-0028 F5): who approved, whom, on which
/// seating, for which round, with the task's digest and label. Erasure does not remove it.
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct ActivationRecord {
    pub at: LogIndex,
    pub activation: Activation,
    pub approvers: BTreeSet<KeyHex>,
    pub drill: bool,
    /// The envelope as computed at activation: each entry, and the bundle revision that holds it.
    pub envelope: std::collections::BTreeMap<String, Digest>,
}
