//! The operator protocol. These are environment steps, not principal actions: lease grant and
//! renewal, revocation, anchor issuance, gate evidence, break-glass approvals.
//!
//! Two paths share this socket (ADR-0050, Proposed).
//!
//! `Control` is an operator's request: one of the six control actions, signed with the key of an
//! `operator` seat, decided by the floor's control entries `C1` to `C9` and checked again by
//! every replica when it is applied. Issuances and break-glass approvals carry their own
//! signatures, as before.
//!
//! Everything else here is unsigned, from whoever can reach the socket, which filesystem
//! permissions alone protect. Where the issued rules declare an `operator` seat, that is a
//! **BOOTSTRAP path**: `Grant` and `Launch` make a first seating, standing in for the quorum
//! ADR-0050 §2 asks for, and the unsigned `Renew`, `EndRound`, `Revoke`, `FenceEpoch` and
//! `GatesPassed` are refused when applied. Where the rules declare none, the deployment is
//! D-0050-1 and the unsigned requests do what they always did.

use std::collections::BTreeSet;

use serde::{Deserialize, Serialize};
use topak_core::authentic::Signed;
use topak_core::lease::Confinement;
use topak_core::rules::Issuance;
use topak_core::state::{EndReason, RevocationTarget};
use topak_core::*;

// One request per connection, parsed and dropped: a variant's size costs nothing here.
#[allow(clippy::large_enum_variant)]
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(tag = "op", rename_all = "snake_case")]
pub enum OperatorOp {
    Grant {
        principal: String,
        seat: SeatId,
        persona: Digest,
        bundle: Digest,
        confinement: Confinement,
        alphabet: BTreeSet<ActionKind>,
        ttl_ms: u64,
        round: Round,
        role: RoundRole,
        /// ADR-0047 §1: the task's label, declared by whoever issues the grant. Where the
        /// round's `clearSet` starts. This reference carries no task, so it is optional.
        #[serde(default)]
        task_label: Option<BTreeSet<String>>,
        /// ADR-0050 §5: the labels a later task for this seating may carry.
        #[serde(default)]
        task_labels_allowed: Option<BTreeSet<String>>,
        /// ADR-0050 §3: an operator seat's sign-on assertion for this boundary.
        #[serde(default)]
        sign_on: Option<Signed>,
    },
    Renew {
        token: String,
        alphabet: BTreeSet<ActionKind>,
        rung: u8,
        ttl_ms: u64,
    },
    EndRound {
        token: String,
        #[serde(default = "operator")]
        reason: EndReason,
    },
    /// Increment the epoch, fencing every lease (ADR-0031 §5). Stop attribution, F2.
    /// Targeted revocation (ADR-0031 §5 R3). The target is required: the fleet-wide tool is
    /// `FenceEpoch`, and nobody should reach it by leaving an argument out.
    Revoke {
        target: RevocationTarget,
        reason: String,
        attribution: String,
    },
    /// The fleet fence: increments the epoch and ends every live round (ADR-0031 §5).
    FenceEpoch {
        reason: String,
        attribution: String,
    },
    Issue {
        issuance: Issuance,
    },
    /// BOOTSTRAP: prepares an emergency seating (ADR-0052 §2), standing in for the promotion
    /// that prepares one. Unsigned.
    PrepareEmergency {
        seat: SeatId,
        seating: topak_core::control::EmergencySeating,
    },
    /// Activates an emergency seating (ADR-0052 §2): the break-glass roster's quorum seats one
    /// named person for one round. The approvals are the roster members' signatures over the
    /// activation. `task` is the bytes its digest names. No operator's request is involved.
    Activate {
        activation: topak_core::control::Activation,
        approvals: Vec<Signed>,
        #[serde(default)]
        task: Option<String>,
    },
    /// An operator's signed request (ADR-0050 §4). `assertion` is the operator's own sign-on
    /// assertion, for a deny made with no live lease. `task` is the bytes of a `Regrant`'s task,
    /// whose digest the signed request carries (§5).
    Control {
        request: topak_core::control::ControlRequest,
        sig: Signed,
        #[serde(default)]
        assertion: Option<Signed>,
        #[serde(default)]
        task: Option<String>,
    },
    GatesPassed {
        artifact: Digest,
        evidence: Digest,
    },
    BreakGlassApprove {
        seat: SeatId,
        epoch: Epoch,
        approval: Signed,
    },
    /// ADR-0036 §6: the node starts the guest from a registered profile, appraises, grants to
    /// itself at the seat's declared rung, and bridges. The Persona is the profile's (F26); there
    /// is no token, because the bridge, or at rungs 2 and 3 the guest's session key, is the
    /// session. Rung 0 launches nothing: it is a `Grant`.
    Launch {
        principal: String,
        seat: SeatId,
        profile: Digest,
        bundle: Digest,
        alphabet: BTreeSet<ActionKind>,
        ttl_ms: u64,
        round: Round,
        role: RoundRole,
        /// ADR-0047 §1: the task's label, declared by whoever issues the grant. Where the
        /// round's `clearSet` starts. This reference carries no task, so it is optional.
        #[serde(default)]
        task_label: Option<BTreeSet<String>>,
    },
    /// Register a profile whose single-file workspace was promoted (ADR-0034 §1). The file's
    /// bytes, verbatim: its digest is what a lease's `confinement` names.
    RegisterProfile {
        profile: String,
    },
    Status,
}

fn operator() -> EndReason {
    EndReason::Operator
}
