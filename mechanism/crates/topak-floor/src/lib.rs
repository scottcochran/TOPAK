//! The policy floor, linked into the mechanism (ADR-0030 §3).
//!
//! No process, no socket, no fetch: the floor text and schema S are compiled into this binary
//! from `floor/` at the repository root — the same bytes the ADR-0030 §5 gates ran on — and the
//! mechanism refuses to start if their digests differ from the gated ones. The enforced text is
//! the proven text, and that is a check the code performs rather than a claim.
//!
//! S is enforced at the decision point on every request (ADR-0030 §4): the request, context and
//! entity slice are all validated against the schema, and any validation failure is a deny.

use std::collections::BTreeMap;
use std::str::FromStr;

use cedar_policy::{
    Authorizer, Context, Decision, Entities, EntityUid, PolicyId, PolicySet, Request, Schema, ValidationMode, Validator,
};
use serde_json::Value;
use topak_core::admit::FloorOutcome;
use topak_core::lift::FrozenInput;
use topak_core::{Digest, ObserverValues};

/// The gated floor text (`floor/genesis-floor.cedar`, DRAFT, not ratified).
pub const FLOOR_SRC: &str = include_str!("../../../../floor/genesis-floor.cedar");
/// Schema S (`floor/genesis.cedarschema`, DRAFT, not ratified).
pub const SCHEMA_SRC: &str = include_str!("../../../../floor/genesis.cedarschema");
/// The policy-floor values (`floor/genesis-values.json`, ADR-0039 §1): the third file of the
/// floor bundle. Placeholders, not measured.
pub const VALUES_SRC: &str = include_str!("../../../../floor/genesis-values.json");

/// Digests recorded in `floor/genesis-gates-results-2026.09.29-adr0039.txt` (the ADR-0039 §2 run:
/// `observerLive` in RunCtx, R3-observer-live, the values file in the bundle; after the ADR-0037
/// §4 run of the same day). Changing any of the three means re-running the gates and changing
/// these: a mechanism release. The 09.24 digests were 9b6adeee… and 77d9b566….
pub const PINNED_FLOOR_SHA256: &str = "49a6e3140726a9a53eeb363b622677e7d72c7fde9dc16276339a66ddb9ebf252";
pub const PINNED_SCHEMA_SHA256: &str = "ac2a0accca51f5f8ef8bdc36f0780c24244abba4d9524037d4e61e92cf1ba4ee";
pub const PINNED_VALUES_SHA256: &str = "0d19c9e3ffa3e7148fac21dfec52cee6886203ec405c1308147eaab0e7c8aec0";

/// The Cedar engine version this mechanism links. The gates ran with cedar-policy-cli 4.13.0.
pub const ENGINE: &str = "cedar-policy 4.13";

#[derive(Debug, thiserror::Error)]
pub enum FloorLoadError {
    #[error("floor digest {actual} is not the gated digest {pinned}")]
    FloorDigest { actual: String, pinned: &'static str },
    #[error("schema digest {actual} is not the gated digest {pinned}")]
    SchemaDigest { actual: String, pinned: &'static str },
    #[error("values digest {actual} is not the gated digest {pinned}")]
    ValuesDigest { actual: String, pinned: &'static str },
    #[error("values: {0}")]
    Values(String),
    #[error("schema: {0}")]
    Schema(String),
    #[error("policies: {0}")]
    Policies(String),
    #[error("floor does not validate against schema S: {0}")]
    Validation(String),
    #[error("policy without an @id annotation: {0}")]
    MissingId(String),
}

pub struct Floor {
    policies: PolicySet,
    schema: Schema,
    ids: BTreeMap<PolicyId, String>,
    floor_digest: Digest,
    schema_digest: Digest,
    values: ObserverValues,
    values_digest: Digest,
}

impl Floor {
    /// Load the pinned floor. Refuses a floor whose bytes are not the gated bytes.
    pub fn load() -> Result<Self, FloorLoadError> {
        Self::load_from(FLOOR_SRC, SCHEMA_SRC, true)
    }

    /// The `observer` block of the values file (ADR-0039 §1).
    pub fn observer_values(&self) -> &ObserverValues {
        &self.values
    }

    pub fn values_digest(&self) -> &Digest {
        &self.values_digest
    }

    /// Load an arbitrary floor text with the pinned values. `pinned = false` is for tests of the
    /// mechanism against mutated floors; a running mechanism uses [`Floor::load`].
    pub fn load_from(floor_src: &str, schema_src: &str, pinned: bool) -> Result<Self, FloorLoadError> {
        Self::load_all(floor_src, schema_src, VALUES_SRC, pinned)
    }

    pub fn load_all(floor_src: &str, schema_src: &str, values_src: &str, pinned: bool) -> Result<Self, FloorLoadError> {
        let floor_digest = Digest::of(floor_src.as_bytes());
        let schema_digest = Digest::of(schema_src.as_bytes());
        let values_digest = Digest::of(values_src.as_bytes());
        if pinned {
            if floor_digest.0 != PINNED_FLOOR_SHA256 {
                return Err(FloorLoadError::FloorDigest { actual: floor_digest.0, pinned: PINNED_FLOOR_SHA256 });
            }
            if schema_digest.0 != PINNED_SCHEMA_SHA256 {
                return Err(FloorLoadError::SchemaDigest { actual: schema_digest.0, pinned: PINNED_SCHEMA_SHA256 });
            }
            if values_digest.0 != PINNED_VALUES_SHA256 {
                return Err(FloorLoadError::ValuesDigest { actual: values_digest.0, pinned: PINNED_VALUES_SHA256 });
            }
        }
        let values: ObserverValues = serde_json::from_str::<Value>(values_src)
            .map_err(|e| FloorLoadError::Values(e.to_string()))?
            .get("observer")
            .cloned()
            .ok_or_else(|| FloorLoadError::Values("no `observer` block".into()))
            .and_then(|v| serde_json::from_value(v).map_err(|e| FloorLoadError::Values(e.to_string())))?;
        let (schema, _warnings) =
            Schema::from_cedarschema_str(schema_src).map_err(|e| FloorLoadError::Schema(e.to_string()))?;
        let policies = PolicySet::from_str(floor_src).map_err(|e| FloorLoadError::Policies(e.to_string()))?;
        let result = Validator::new(schema.clone()).validate(&policies, ValidationMode::Strict);
        if !result.validation_passed() {
            let errs: Vec<String> = result.validation_errors().map(|e| e.to_string()).collect();
            return Err(FloorLoadError::Validation(errs.join("; ")));
        }
        let mut ids = BTreeMap::new();
        for p in policies.policies() {
            let id = p.annotation("id").ok_or_else(|| FloorLoadError::MissingId(p.id().to_string()))?;
            ids.insert(p.id().clone(), id.to_string());
        }
        Ok(Self { policies, schema, ids, floor_digest, schema_digest, values, values_digest })
    }

    pub fn floor_digest(&self) -> &Digest {
        &self.floor_digest
    }

    pub fn schema_digest(&self) -> &Digest {
        &self.schema_digest
    }

    /// Declared floor exceptions (ADR-0013 §2): entries whose `@id` starts with `X`. Checked
    /// against rules-floor entry R6 at startup.
    pub fn exception_count(&self) -> usize {
        self.ids.values().filter(|id| id.starts_with('X')).count()
    }

    pub fn policy_ids(&self) -> impl Iterator<Item = &str> {
        self.ids.values().map(String::as_str)
    }

    /// Decide a frozen input. Allow with any error is `Error`, which the composition treats as
    /// a deny (ADR-0030 §1).
    pub fn decide(&self, input: &FrozenInput) -> FloorOutcome {
        let uid = |v: &Value| EntityUid::from_json(v.clone()).map_err(|e| e.to_string());
        let (p, a, r) = match (uid(&input.principal), uid(&input.action), uid(&input.resource)) {
            (Ok(p), Ok(a), Ok(r)) => (p, a, r),
            (p, a, r) => {
                let diagnostics = [p.err(), a.err(), r.err()].into_iter().flatten().collect();
                return FloorOutcome::Error { diagnostics };
            }
        };
        self.evaluate(p, a, r, &input.context, &input.entities)
    }

    /// Decide from Cedar-format parts. Used by [`Floor::decide`] and by the replay of the gate
    /// suite's behavioral cases.
    pub fn evaluate(
        &self,
        principal: EntityUid,
        action: EntityUid,
        resource: EntityUid,
        context: &Value,
        entities: &Value,
    ) -> FloorOutcome {
        let err = |d: String| FloorOutcome::Error { diagnostics: vec![d] };
        let context = match Context::from_json_value(context.clone(), Some((&self.schema, &action))) {
            Ok(c) => c,
            Err(e) => return err(format!("context: {e}")),
        };
        let request = match Request::new(principal, action, resource, context, Some(&self.schema)) {
            Ok(r) => r,
            Err(e) => return err(format!("request: {e}")),
        };
        let entities = match Entities::from_json_value(entities.clone(), Some(&self.schema)) {
            Ok(e) => e,
            Err(e) => return err(format!("entities: {e}")),
        };
        let response = Authorizer::new().is_authorized(&request, &self.policies, &entities);
        let diagnostics: Vec<String> = response.diagnostics().errors().map(|e| e.to_string()).collect();
        if !diagnostics.is_empty() {
            // Cedar skipped the erroring policy; a skipped forbid must not let a permit through.
            return FloorOutcome::Error { diagnostics };
        }
        let reasons: Vec<String> = response
            .diagnostics()
            .reason()
            .map(|id| self.ids.get(id).cloned().unwrap_or_else(|| id.to_string()))
            .collect();
        match response.decision() {
            Decision::Allow => FloorOutcome::Permit { reasons },
            Decision::Deny => FloorOutcome::Deny { reasons },
        }
    }
}
