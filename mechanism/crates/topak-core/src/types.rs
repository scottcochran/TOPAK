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
/// Build's six are ADR-0022 §1. `RunInvoke` and `RunEmit` are PROVISIONAL: no record defines
/// Run's alphabet; they carry ADR-0015's two Run effects, as the draft floor does.
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash, PartialOrd, Ord, Serialize, Deserialize)]
pub enum ActionKind {
    Read,
    Draft,
    Invoke,
    Emit,
    Submit,
    Vote,
    RunInvoke,
    RunEmit,
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
    pub const RUN: [ActionKind; 2] = [ActionKind::RunInvoke, ActionKind::RunEmit];

    pub fn as_str(self) -> &'static str {
        match self {
            ActionKind::Read => "Read",
            ActionKind::Draft => "Draft",
            ActionKind::Invoke => "Invoke",
            ActionKind::Emit => "Emit",
            ActionKind::Submit => "Submit",
            ActionKind::Vote => "Vote",
            ActionKind::RunInvoke => "RunInvoke",
            ActionKind::RunEmit => "RunEmit",
        }
    }

    pub fn domain(self) -> Domain {
        match self {
            ActionKind::RunInvoke | ActionKind::RunEmit => Domain::Run,
            _ => Domain::Build,
        }
    }
}

impl fmt::Display for ActionKind {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.write_str(self.as_str())
    }
}
