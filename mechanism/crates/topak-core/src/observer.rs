//! Observer liveness (ADR-0039 §1): the heartbeat and the policy-floor values the lift reads.
//!
//! A heartbeat is the one fixed-schema record an `observer` seat emits to report liveness. It
//! is a fact, not a finding (ADR-0004): it names a watched round topic and a watermark, the
//! sequence number in that topic through which the Observer says it has read. It never says
//! what was read. Because it is a fact it survives into the control plane verbatim, so every
//! replica applies the same mark from the log.

use serde::{Deserialize, Serialize};
use serde_json::Value;

/// The `observer` block of `floor/genesis-values.json` (ADR-0039 §1). **Placeholders** until
/// measured; deployment or rung choices, not the pattern's values. `K` must be below the round
/// bound `R` of every domain, which the mechanism checks at startup.
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct ObserverValues {
    #[serde(rename = "T_obs_ms")]
    pub t_obs_ms: u64,
    #[serde(rename = "K")]
    pub k: u64,
}

impl Default for ObserverValues {
    /// The placeholders of 2026.09.29, for states built without a floor (tests). A running
    /// mechanism takes the linked floor's values.
    fn default() -> Self {
        Self { t_obs_ms: 5000, k: 8 }
    }
}

/// `{"heartbeat": {"topic": "<watched round topic>", "watermark": n}}`, and nothing else.
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct Heartbeat {
    pub topic: String,
    pub watermark: u64,
}

impl Heartbeat {
    pub fn parse(record: &Value) -> Option<Heartbeat> {
        let obj = record.as_object()?;
        if obj.len() != 1 {
            return None;
        }
        serde_json::from_value(obj.get("heartbeat")?.clone()).ok()
    }

    pub fn record(&self) -> Value {
        serde_json::json!({ "heartbeat": self })
    }
}
