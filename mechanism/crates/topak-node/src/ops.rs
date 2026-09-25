//! The operator protocol. These are environment steps, not principal actions: lease grant and
//! renewal, revocation, anchor issuance, gate evidence, break-glass approvals.
//!
//! PROVISIONAL (operator authentication): the operator socket is protected by filesystem
//! permissions only. Issuances and break-glass approvals carry their own signatures and are
//! validated in the replicated state machine; grants, revocations and gate evidence are not
//! signed, and whoever can reach the socket can issue them.

use std::collections::BTreeSet;

use serde::{Deserialize, Serialize};
use topak_core::authentic::Signed;
use topak_core::lease::Confinement;
use topak_core::rules::Issuance;
use topak_core::state::{EndReason, RevocationTarget};
use topak_core::*;

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
    GatesPassed {
        artifact: Digest,
        evidence: Digest,
    },
    BreakGlassApprove {
        seat: SeatId,
        epoch: Epoch,
        approval: Signed,
    },
    Status,
}

fn operator() -> EndReason {
    EndReason::Operator
}
