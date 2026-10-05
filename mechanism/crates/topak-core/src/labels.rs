//! Labels on Run's ingress (ADR-0047), as the replicated state and the lift carry them.
//!
//! A label is a set of names from a bundle's vocabulary. This crate reads no bundle: the replica
//! that decides an admit computes the call's `LabelFacts` from the allowlist entry of the lease's
//! revision and from the round's `RoundLabels`, and the admit carries them. `apply` folds them into
//! the round, on every replica, in log order, so `clearSet` is a fold over the round's deliveries
//! that only grows (§4), and a reader with the log can recompute it.
//!
//! The lift (ADR-0007) hands four of the facts to the floor as attributes of schema S, and
//! `outward` as an attribute of the tool. No policy computes any of them.

use std::collections::{BTreeMap, BTreeSet};

use serde::{Deserialize, Serialize};
use serde_json::Value;

use crate::Digest;

pub type Label = BTreeSet<String>;

/// The two names the floor reserves (ADR-0047 §7).
pub const UNTRUSTED: &str = "untrusted";
pub const RESTRICTED: &str = "restricted";

/// How the Listener delivers an item (ADR-0047 §2).
#[derive(Clone, Copy, Debug, Default, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum Delivery {
    /// The item's bytes, with its label.
    #[default]
    Clear,
    /// A handle and the item's label. The bytes do not enter the guest.
    Handle,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct ItemLabel {
    pub label: Label,
    pub delivery: Delivery,
}

/// A handle names an item by its place in the record (ADR-0047 §2), in ADR-0049 §3's one form:
/// `{"handle": {"actuate": <seq>}}` or `{"handle": {"consult": "<digest>"}}`.
#[derive(Clone, Debug, PartialEq, Eq)]
pub enum Handle {
    Actuate(u64),
    Consult(Digest),
}

impl Handle {
    /// A handle cannot be mistaken for a literal: every literal input is a scalar, and a handle is
    /// an object with the one reserved key. Told apart by shape, with no judgment.
    pub fn parse(v: &Value) -> Option<Handle> {
        let outer = v.as_object().filter(|o| o.len() == 1)?;
        let inner = outer.get("handle")?.as_object().filter(|o| o.len() == 1)?;
        match inner.iter().next()? {
            (k, v) if k == "actuate" => v.as_u64().map(Handle::Actuate),
            (k, v) if k == "consult" => v.as_str().map(|d| Handle::Consult(Digest(d.to_string()))),
            _ => None,
        }
    }

    pub fn to_value(&self) -> Value {
        match self {
            Handle::Actuate(seq) => serde_json::json!({ "handle": { "actuate": seq } }),
            Handle::Consult(d) => serde_json::json!({ "handle": { "consult": d } }),
        }
    }
}

/// The labels of one round, for one principal: what it has read in the clear, and the label of
/// every item a handle of its own can name. A handle names an item in the same round and for the
/// same principal (ADR-0049 §3), so nothing here outlives the round.
#[derive(Clone, Debug, Default, PartialEq, Eq, Serialize, Deserialize)]
pub struct RoundLabels {
    /// The join of the labels of every item delivered clear this round, the task included.
    pub clear_set: Label,
    /// By the sequence number of the `Actuate` record.
    #[serde(default, skip_serializing_if = "BTreeMap::is_empty")]
    pub results: BTreeMap<u64, ItemLabel>,
    /// By the reference the principal supplied.
    #[serde(default, skip_serializing_if = "BTreeMap::is_empty")]
    pub consults: BTreeMap<Digest, ItemLabel>,
}

impl RoundLabels {
    pub fn item(&self, h: &Handle) -> Option<&ItemLabel> {
        match h {
            Handle::Actuate(seq) => self.results.get(seq),
            Handle::Consult(d) => self.consults.get(d),
        }
    }
}

/// What the mechanism computed about one `Consult` or `Actuate` before the floor saw it.
#[derive(Clone, Debug, Default, PartialEq, Eq, Serialize, Deserialize)]
pub struct LabelFacts {
    /// `clearSet` as it stood when the call was decided. `apply` refuses the admit if the round's
    /// has grown since: the floor's answer was about this set and no other.
    pub clear_set: Label,
    /// The join of the labels of the call's inputs that are handles.
    pub input_labels: Label,
    /// An input the entry marks a destination is a literal.
    pub dest_literal: bool,
    /// The join of the labels of destination inputs that are handles.
    pub dest_labels: Label,
    /// The entry is outward (ADR-0049 §4): derived from its channel and the issued rules.
    pub outward: bool,
    /// The label of what the call returns: for an `Actuate`, after the join of ADR-0047 §1; for
    /// a `Consult`, the label the root declares for the object.
    pub result_label: Label,
    pub delivery: Delivery,
}

impl LabelFacts {
    /// The facts of a call that names no entry's labels: nothing joined, delivered clear. What a
    /// test stub says of a tool it has no entry for.
    pub fn unlabelled(clear_set: &Label) -> Self {
        LabelFacts { clear_set: clear_set.clone(), ..Default::default() }
    }
}
