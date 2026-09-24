//! The typed action alphabet (ADR-0022 §1) and the request that carries it.

use serde::{Deserialize, Serialize};
use serde_json::{Map, Value};

use crate::types::*;

/// One action a principal expresses. Egress only: the alphabet types what a principal *does*.
#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
#[serde(tag = "kind")]
pub enum Action {
    /// Resolve a content-addressed object inside the pinned corpus root.
    Read { object: Digest },
    /// Write into the round-scoped workspace.
    Draft { target: String, content: String },
    /// Run a tool allowlisted by name and digest.
    Invoke { tool: String, digest: Digest, inputs: Map<String, Value> },
    /// Append to the principal's round topic.
    Emit { record: Value },
    /// Offer the sealed workspace for promotion. Abstention (`Submit(⊥)`) is not an action that
    /// crosses the boundary; it is an `EndRound` log entry (see `state::EndReason::Abstained`).
    Submit { artifact: Digest },
    /// Cast a promotion vote bound to (artifact, gate evidence, rules epoch) (ADR-0024 §3).
    Vote { verdict: Verdict, artifact: Digest, evidence: Digest, rules_epoch: RulesEpoch },
    /// PROVISIONAL (Run alphabet): invoke a Run tool.
    RunInvoke { tool: String, digest: Digest, inputs: Map<String, Value> },
    /// PROVISIONAL (Run alphabet): append to the Run principal's round topic.
    RunEmit { record: Value },
}

impl Action {
    pub fn kind(&self) -> ActionKind {
        match self {
            Action::Read { .. } => ActionKind::Read,
            Action::Draft { .. } => ActionKind::Draft,
            Action::Invoke { .. } => ActionKind::Invoke,
            Action::Emit { .. } => ActionKind::Emit,
            Action::Submit { .. } => ActionKind::Submit,
            Action::Vote { .. } => ActionKind::Vote,
            Action::RunInvoke { .. } => ActionKind::RunInvoke,
            Action::RunEmit { .. } => ActionKind::RunEmit,
        }
    }

    /// The control-plane form of the action (ADR-0004): payloads replaced by their digests.
    /// This is what enters the consensus log; the payload itself goes to its effect path.
    pub fn control_plane(&self) -> Value {
        match self {
            Action::Draft { target, content } => serde_json::json!({
                "kind": "Draft", "target": target, "content": Digest::of(content.as_bytes()),
            }),
            Action::Emit { record } => serde_json::json!({
                "kind": "Emit", "record": Digest::of_json(record),
            }),
            Action::RunEmit { record } => serde_json::json!({
                "kind": "RunEmit", "record": Digest::of_json(record),
            }),
            Action::Invoke { tool, digest, inputs } => serde_json::json!({
                "kind": "Invoke", "tool": tool, "digest": digest, "inputs": Digest::of_json(inputs),
            }),
            Action::RunInvoke { tool, digest, inputs } => serde_json::json!({
                "kind": "RunInvoke", "tool": tool, "digest": digest, "inputs": Digest::of_json(inputs),
            }),
            other => serde_json::to_value(other).expect("serializable"),
        }
    }
}

/// An action as it reaches the mechanism. Every action carries epoch and lease (ADR-0022 §2).
/// The lease is named by its fence, which is unique because it is a log index.
#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct ActionRequest {
    pub seat: SeatId,
    pub lease: LogIndex,
    pub epoch: Epoch,
    pub action: Action,
}

/// The tool identity used on the allowlist and as the Cedar `Tool` entity id.
pub fn tool_id(name: &str, digest: &Digest) -> String {
    format!("{name}@{digest}")
}
