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

/// The `persona` block of `floor/genesis-values.json` (ADR-0031 A2): the upper bound on a lease's
/// `ttl` at grant and at every renewal, so the Persona is re-attested at least this often
/// (ADR-0016 §6). A **placeholder** of one hour until measured. It bounds the declared value;
/// expiry runs on the local clock, so the interval it bounds is `T_persona` plus drift (ADR-0045
/// finding 2).
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct PersonaValues {
    #[serde(rename = "T_persona_ms")]
    pub t_persona_ms: u64,
}

impl Default for PersonaValues {
    fn default() -> Self {
        Self { t_persona_ms: 3_600_000 }
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

/// `{"finding": {"topic": "<round topic>"}}`, and nothing else: an Observer's finding against one
/// round (ADR-0007; ADR-0054 §4's `found`). PROVISIONAL (finding-record): no record fixes a finding's
/// form, and the reference had no producer of one (G12). It is a fact the mechanism reads by shape,
/// as it reads a heartbeat, and it only subtracts: a workflow edge out of that round, or out of any
/// activation whose causal history holds it, is no longer enabled.
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct Finding {
    pub topic: String,
}

impl Finding {
    pub fn parse(record: &Value) -> Option<Finding> {
        let obj = record.as_object()?;
        if obj.len() != 1 {
            return None;
        }
        serde_json::from_value(obj.get("finding")?.clone()).ok()
    }

    pub fn record(&self) -> Value {
        serde_json::json!({ "finding": self })
    }
}
