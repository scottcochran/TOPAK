//! Monotone composition of the two policy tiers (ADR-0030 §1):
//!
//! > **admit ⟺ floor_permit ∧ ¬bundle_deny**
//!
//! - `floor_permit` holds only when the floor engine returns Allow **with no evaluation errors**.
//!   Cedar skips a policy that errors, so an erroring `forbid` would not fire; any floor error
//!   is therefore a deny, whatever decision the engine returned.
//! - `bundle_deny` holds unless the bundle affirmatively allows. A deny, an error, undefined, an
//!   absent or unreachable bundle are all denies. A bundle is never asked whether to grant, only
//!   whether to refuse.
//! - A floor deny short-circuits: the bundle is consulted only on a floor permit.
//! - A floor deny names its reason (ADR-0030 §1, R4): the forbids that fired, or `FloorNoPermit`
//!   when none did. Cedar reports determining policies only for forbids, so without the second
//!   case most denials would carry no reason at all.

use serde::{Deserialize, Serialize};

use crate::state::{BundleEngine, MechanismDeny};
use crate::types::Digest;

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub enum FloorOutcome {
    /// Allow with an empty error list. `reasons` are the permitting policy ids.
    Permit {
        reasons: Vec<String>,
    },
    Deny {
        reasons: Vec<String>,
    },
    /// Any evaluation error or input-validation failure, whatever the engine decided.
    Error {
        diagnostics: Vec<String>,
    },
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub enum BundleOutcome {
    /// An affirmative `allow` from the bundle version the lease names.
    Allow { engine: BundleEngine, bundle: Digest },
    /// Anything else.
    Refuse { engine: Option<BundleEngine>, reason: String },
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub enum DenyReason {
    Mechanism(MechanismDeny),
    /// The floor denied because these forbids fired.
    Floor(Vec<String>),
    /// The floor denied because no permit matched: the request is outside every envelope.
    FloorNoPermit,
    FloorError(Vec<String>),
    Bundle(String),
    /// The admit was decided but voided at apply time, or never committed.
    NotCommitted(String),
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub enum Decision {
    Admit { floor_reasons: Vec<String>, engine: BundleEngine, bundle: Digest },
    Deny(DenyReason),
}

/// The floor half of the composition. `Some(deny)` means stop: do not consult the bundle.
pub fn floor_gate(floor: &FloorOutcome) -> Option<DenyReason> {
    match floor {
        FloorOutcome::Permit { .. } => None,
        FloorOutcome::Deny { reasons } if reasons.is_empty() => Some(DenyReason::FloorNoPermit),
        FloorOutcome::Deny { reasons } => Some(DenyReason::Floor(reasons.clone())),
        FloorOutcome::Error { diagnostics } => Some(DenyReason::FloorError(diagnostics.clone())),
    }
}

/// The whole composition. A bundle allow never admits what the floor did not permit.
pub fn compose(floor: &FloorOutcome, bundle: &BundleOutcome) -> Decision {
    if let Some(d) = floor_gate(floor) {
        return Decision::Deny(d);
    }
    let FloorOutcome::Permit { reasons } = floor else { unreachable!("floor_gate") };
    match bundle {
        BundleOutcome::Allow { engine, bundle } => {
            Decision::Admit { floor_reasons: reasons.clone(), engine: *engine, bundle: bundle.clone() }
        }
        BundleOutcome::Refuse { reason, .. } => Decision::Deny(DenyReason::Bundle(reason.clone())),
    }
}

/// Whether the floor admitted through the break-glass exception rather than an ordinary
/// envelope: the invocation is then forensic class F5.
pub fn via_break_glass(reasons: &[String]) -> bool {
    reasons.iter().any(|r| r == "X1-break-glass") && !reasons.iter().any(|r| r == "R1-actuate-allowlisted")
}
