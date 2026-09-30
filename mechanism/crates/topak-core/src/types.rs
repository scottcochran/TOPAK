use serde::{Deserialize, Serialize};
use sha2::{Digest as _, Sha256};
use std::fmt;

pub type SeatId = String;
pub type Epoch = u64;
pub type RulesEpoch = u64;
pub type Round = u64;
/// A position in the Paxos log. A lease's `fence` is the log index at which it was granted
/// (ADR-0031 §2), so it also serves as the lease's identity.
pub type LogIndex = u64;

/// Lowercase hex SHA-256. Identity is the digest of bytes (G-C1).
#[derive(Clone, Debug, PartialEq, Eq, Hash, PartialOrd, Ord, Serialize, Deserialize)]
#[serde(transparent)]
pub struct Digest(pub String);

impl Digest {
    pub fn of(bytes: &[u8]) -> Self {
        Digest(hex::encode(Sha256::digest(bytes)))
    }

    /// Digest of a value's canonical JSON. `serde_json` with the default (non-`preserve_order`)
    /// features serializes maps with sorted keys, so equal values give equal bytes.
    pub fn of_json<T: Serialize>(value: &T) -> Self {
        Digest::of(&canonical_json(value))
    }

    pub fn short(&self) -> &str {
        &self.0[..self.0.len().min(16)]
    }
}

impl fmt::Display for Digest {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.write_str(&self.0)
    }
}

/// Canonical JSON bytes: sorted object keys, no insignificant whitespace.
pub fn canonical_json<T: Serialize>(value: &T) -> Vec<u8> {
    // Round-trip through `Value` so struct field order does not leak into the bytes.
    let v = serde_json::to_value(value).expect("serializable");
    serde_json::to_vec(&v).expect("serializable")
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash, PartialOrd, Ord, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum Domain {
    Build,
    Run,
}

impl Domain {
    pub fn as_str(self) -> &'static str {
        match self {
            Domain::Build => "build",
            Domain::Run => "run",
        }
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum RoundRole {
    Author,
    Voter,
}

impl RoundRole {
    pub fn as_str(self) -> &'static str {
        match self {
            RoundRole::Author => "author",
            RoundRole::Voter => "voter",
        }
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum Verdict {
    Grant,
    Deny,
}

impl Verdict {
    pub fn as_str(self) -> &'static str {
        match self {
            Verdict::Grant => "grant",
            Verdict::Deny => "deny",
        }
    }
}

/// The action variants. Names match the Cedar actions in `floor/genesis.cedarschema`.
///
/// Build's six are ADR-0022 §1. Run's three are ADR-0040 §1 (Proposed): `Consult` is ingress over
/// the pinned Run root, and `Actuate` and `Report` are ADR-0015's two effect classes. No name is
/// shared between the domains (ADR-0040 §2).
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash, PartialOrd, Ord, Serialize, Deserialize)]
pub enum ActionKind {
    Read,
    Draft,
    Invoke,
    Emit,
    Submit,
    Vote,
    Consult,
    Actuate,
    Report,
}

impl ActionKind {
    pub const BUILD: [ActionKind; 6] = [
        ActionKind::Read,
        ActionKind::Draft,
        ActionKind::Invoke,
        ActionKind::Emit,
        ActionKind::Submit,
        ActionKind::Vote,
    ];
    pub const RUN: [ActionKind; 3] = [ActionKind::Consult, ActionKind::Actuate, ActionKind::Report];

    pub fn as_str(self) -> &'static str {
        match self {
            ActionKind::Read => "Read",
            ActionKind::Draft => "Draft",
            ActionKind::Invoke => "Invoke",
            ActionKind::Emit => "Emit",
            ActionKind::Submit => "Submit",
            ActionKind::Vote => "Vote",
            ActionKind::Consult => "Consult",
            ActionKind::Actuate => "Actuate",
            ActionKind::Report => "Report",
        }
    }

    pub fn domain(self) -> Domain {
        match self {
            ActionKind::Consult | ActionKind::Actuate | ActionKind::Report => Domain::Run,
            _ => Domain::Build,
        }
    }

    /// ADR-0042 §2: the Run variants that bear an effect. These advance the sequence an Observer's
    /// watermark is over, and these are what `R3-observer-live` couples (ADR-0041 §2). `Consult`
    /// is ingress and does neither.
    pub fn is_run_effect(self) -> bool {
        matches!(self, ActionKind::Actuate | ActionKind::Report)
    }
}

impl fmt::Display for ActionKind {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.write_str(self.as_str())
    }
}

/// A seat's kind (ADR-0037 §2), declared with the seat in the issued rules and never changed.
/// Only a `thinker` seat holds a variant that writes, runs or offers (§4): in Run, `Actuate`
/// (ADR-0043 §2).
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash, PartialOrd, Ord, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum SeatKind {
    Thinker,
    Observer,
    Grant,
}

impl SeatKind {
    pub fn as_str(self) -> &'static str {
        match self {
            SeatKind::Thinker => "thinker",
            SeatKind::Observer => "observer",
            SeatKind::Grant => "grant",
        }
    }

    /// ADR-0037 §4 for Build and ADR-0043 §2 for Run: the variants a seat of this kind may be
    /// issued. The floor states the same bound (B10, B6); the grant path checks it first, as it
    /// does the domain. An observer seat's `Consult` is scoped to the Run root its Thinker's is.
    pub fn allows(self, k: ActionKind) -> bool {
        use ActionKind::*;
        match self {
            SeatKind::Thinker => {
                matches!(k, Read | Draft | Invoke | Emit | Submit | Consult | Actuate | Report)
            }
            SeatKind::Observer => matches!(k, Read | Emit | Vote | Consult | Report),
            SeatKind::Grant => matches!(k, Read | Emit | Vote),
        }
    }
}

impl fmt::Display for SeatKind {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.write_str(self.as_str())
    }
}
