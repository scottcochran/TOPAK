//! The allowlist entry, and what makes a bundle's allowlist well-formed (ADR-0049, Proposed).
//!
//! ADR-0049 is the one statement of the entry: five parts (identity, inputs, interface, labels,
//! channel), keyed `name@digest` in bundle data at `topak.tools`. `check` reads that data once,
//! when a bundle loads, and refuses the bundle for any of W1 to W10 (§6). Each refusal names its
//! check. Nothing here needs judgment: every check is on the data's shape.
//!
//! What the checks read from outside the bundle is `Issued`: the targets the issued rules list as
//! inside the deployment (W7, W9) and the entries they name as allowed to release a reserved label
//! (W8). ADR-0025 A2, which issues both, is pending; until the rules carry them the node passes
//! the empty lists, under which every entry with a channel is outward and no entry releases a
//! reserved name. That is the strict reading, and the one ADR-0049 §8 illustrates.
//!
//! Beyond the table: a field ADR-0049 does not define is refused, on an entry and on an input, and
//! so is the labels part on a Build entry (§1: "a Build entry has no channel and no labels"). W10,
//! `accepts` or `destination` on an input the entry does not have, cannot be written in §8's form,
//! where both sit inside the input they describe; the unknown-field refusal is what stands there.

use std::collections::{BTreeMap, BTreeSet};

use serde::Serialize;
use serde_json::{Map, Value, json};
use topak_core::{Digest, Domain};

/// ADR-0047 §1: the two names every vocabulary holds.
pub const RESERVED: [&str; 2] = ["untrusted", "restricted"];
/// ADR-0048 §1's size bound, a mechanism parameter. The values are this reference's.
pub const PURPOSE_MAX: usize = 1024;
pub const NOTE_MAX: usize = 256;

const TYPES: [&str; 3] = ["string", "number", "boolean"];
const ENTRY_FIELDS: [&str; 8] =
    ["name", "digest", "domain", "purpose", "inputs", "destinations", "result", "channel"];
const INPUT_FIELDS: [&str; 5] = ["type", "required", "note", "destination", "accepts"];

/// What the issued rules say that the load checks read (ADR-0025 A2, pending).
#[derive(Clone, Debug, Default)]
pub struct Issued {
    /// Channel targets inside the deployment. An entry whose target is not here is outward.
    pub inside_targets: BTreeSet<String>,
    /// Entry keys allowed to carry a reserved name in `result.releases`.
    pub releasers: BTreeSet<String>,
}

/// An entry's one declaration of where a Run tool may connect (ADR-0049 §5).
#[derive(Clone, Debug, PartialEq, Eq, Serialize)]
pub struct Channel {
    pub kind: String,
    pub target: String,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize)]
pub struct Input {
    #[serde(rename = "type")]
    pub ty: String,
    pub required: bool,
    pub note: String,
    pub destination: bool,
    pub accepts: BTreeSet<String>,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize)]
pub struct Entry {
    pub name: String,
    pub digest: String,
    pub domain: Domain,
    pub purpose: String,
    pub inputs: BTreeMap<String, Input>,
    pub label: BTreeSet<String>,
    pub releases: BTreeSet<String>,
    pub channel: Option<Channel>,
    /// Derived and never declared (ADR-0049 §4): a channel whose target is not issued as inside.
    pub outward: bool,
}

/// A well-formed allowlist: the entries of one bundle revision, and the vocabulary they name.
#[derive(Clone, Debug, Default)]
pub struct Allowlist {
    pub entries: BTreeMap<String, Entry>,
    pub vocabulary: BTreeSet<String>,
}

impl Entry {
    /// The entry as a Thinker is told it (ADR-0048 §1, §2): every field of the interface, the
    /// inputs and the labels, and the channel by its kind and by whether it is outward. The
    /// target is not delivered: a Thinker needs to know a call leaves the deployment, not where to.
    fn listed(&self) -> Value {
        let run = self.domain == Domain::Run;
        let inputs: Map<String, Value> = self
            .inputs
            .iter()
            .map(|(f, i)| {
                let mut v = json!({ "type": i.ty, "required": i.required, "note": i.note });
                if run {
                    v["destination"] = json!(i.destination);
                    v["accepts"] = json!(i.accepts);
                }
                (f.clone(), v)
            })
            .collect();
        let mut v = json!({ "name": self.name, "digest": self.digest, "purpose": self.purpose, "inputs": inputs });
        if run {
            v["result"] = json!({ "label": self.label, "releases": self.releases });
        }
        if let Some(c) = &self.channel {
            v["channel"] = json!({ "kind": c.kind, "outward": self.outward });
        }
        v
    }
}

impl Allowlist {
    /// The tool list of a lease (ADR-0048 §2): the entries of this revision for `domain` whose key
    /// is in `callable`, every one and no other, in the mechanism's one fixed form. The rendering
    /// is total over an entry's fields and makes no choice, so it is a syntactic lift (ADR-0007).
    /// Entries are in key order; the digest of the list is over its canonical JSON.
    pub fn tool_list(&self, rev: &Digest, domain: Domain, callable: &BTreeSet<String>) -> Value {
        let tools: Vec<Value> = self
            .entries
            .iter()
            .filter(|(key, e)| e.domain == domain && callable.contains(*key))
            .map(|(_, e)| e.listed())
            .collect();
        json!({ "bundle": rev, "domain": domain, "tools": tools })
    }
}

fn text<'a>(o: &'a Map<String, Value>, k: &str) -> Option<&'a str> {
    o.get(k).and_then(Value::as_str).filter(|s| !s.is_empty())
}

/// A set of label names, or `None` when the value is not a list of strings.
fn names(v: Option<&Value>) -> Option<BTreeSet<String>> {
    match v {
        None => Some(BTreeSet::new()),
        Some(Value::Array(a)) => a.iter().map(|x| x.as_str().map(str::to_string)).collect(),
        Some(_) => None,
    }
}

/// Read `data.topak.tools`, or say every reason the bundle is refused.
pub fn check(data: &Value, issued: &Issued) -> Result<Allowlist, Vec<String>> {
    let mut out = Vec::new();
    let mut list = Allowlist::default();
    list.vocabulary = RESERVED.iter().map(|s| s.to_string()).collect();
    match names(data.pointer("/topak/labels/vocabulary")) {
        Some(v) => list.vocabulary.extend(v),
        None => out.push("W6: labels.vocabulary is not a list of names".to_string()),
    }
    let tools = match data.pointer("/topak/tools") {
        None => return if out.is_empty() { Ok(list) } else { Err(out) },
        Some(Value::Object(t)) => t,
        Some(_) => return Err(vec!["W1: the allowlist is not a map from key to entry".to_string()]),
    };
    for (key, v) in tools {
        let before = out.len();
        let entry = check_entry(key, v, &list.vocabulary, issued, &mut out);
        if let (Some(e), true) = (entry, out.len() == before) {
            list.entries.insert(key.clone(), e);
        }
    }
    if out.is_empty() { Ok(list) } else { Err(out) }
}

fn check_entry(
    key: &str,
    v: &Value,
    vocabulary: &BTreeSet<String>,
    issued: &Issued,
    out: &mut Vec<String>,
) -> Option<Entry> {
    let mut no = |w: &str, why: String| out.push(format!("{w}: entry {key}: {why}"));
    let Some(o) = v.as_object() else {
        no("W1", "is not an object".into());
        return None;
    };
    for k in o.keys().filter(|k| !ENTRY_FIELDS.contains(&k.as_str())) {
        no("§1", format!("field {k:?} is not part of an entry"));
    }

    // Identity (W1).
    let (name, digest) = (text(o, "name").unwrap_or(""), text(o, "digest").unwrap_or(""));
    if name.is_empty() || digest.is_empty() || key != format!("{name}@{digest}") {
        no("W1", "the key is not the entry's name and digest".into());
    }
    let domain = match o.get("domain").and_then(Value::as_str) {
        Some("build") => Domain::Build,
        Some("run") => Domain::Run,
        _ => {
            no("W1", "domain is missing, or is neither build nor run".into());
            return None;
        }
    };
    let run = domain == Domain::Run;

    // Interface (W3).
    let purpose = o.get("purpose").and_then(Value::as_str).unwrap_or("");
    if purpose.is_empty() {
        no("W3", "purpose is empty".into());
    } else if purpose.len() > PURPOSE_MAX {
        no("W3", format!("purpose is {} bytes, over the bound of {PURPOSE_MAX}", purpose.len()));
    }

    // Inputs (W2), each with its note (W3) and, for Run, its labels part.
    let mut inputs = BTreeMap::new();
    let declared = match o.get("inputs") {
        None => Map::new(),
        Some(Value::Object(m)) => m.clone(),
        Some(_) => {
            no("W2", "inputs is not a map from input to its declaration".into());
            Map::new()
        }
    };
    for (f, d) in &declared {
        let Some(d) = d.as_object() else {
            no("W2", format!("input {f:?} is not an object"));
            continue;
        };
        for k in d.keys().filter(|k| !INPUT_FIELDS.contains(&k.as_str())) {
            no("§1", format!("input {f:?}: field {k:?} is not part of an input"));
        }
        let ty = d.get("type").and_then(Value::as_str).unwrap_or("");
        if !TYPES.contains(&ty) {
            no("W2", format!("input {f:?} has no type, or one that is not string, number or boolean"));
        }
        let required = d.get("required").and_then(Value::as_bool);
        if required.is_none() {
            no("W2", format!("input {f:?} does not say whether it is required"));
        }
        let note = d.get("note").and_then(Value::as_str).unwrap_or("");
        if note.is_empty() {
            no("W3", format!("input {f:?} has no note"));
        } else if note.len() > NOTE_MAX {
            no("W3", format!("input {f:?}: note is {} bytes, over the bound of {NOTE_MAX}", note.len()));
        }
        if !run && (d.contains_key("destination") || d.contains_key("accepts")) {
            no("§1", format!("input {f:?}: a Build entry has no labels"));
        }
        let destination = match d.get("destination") {
            None => false,
            Some(Value::Bool(b)) => *b,
            Some(_) => {
                no("W9", format!("input {f:?}: destination is not true or false"));
                false
            }
        };
        let accepts = names(d.get("accepts")).unwrap_or_else(|| {
            no("W6", format!("input {f:?}: accepts is not a list of names"));
            BTreeSet::new()
        });
        for l in accepts.iter().filter(|l| !vocabulary.contains(*l)) {
            no("W6", format!("input {f:?}: accepts names {l:?}, which is outside the vocabulary"));
        }
        inputs.insert(
            f.clone(),
            Input {
                ty: ty.to_string(),
                required: required.unwrap_or(false),
                note: note.to_string(),
                destination,
                accepts,
            },
        );
    }

    // Channel (W4, W5).
    let channel = match (run, o.get("channel")) {
        (false, None) => None,
        (false, Some(_)) => {
            no("W5", "a Build entry declares a channel".into());
            None
        }
        (true, None) => {
            no("W4", "a Run entry declares no channel".into());
            None
        }
        (true, Some(c)) => {
            let c = c.as_object();
            let (kind, target) = (c.and_then(|c| text(c, "kind")), c.and_then(|c| text(c, "target")));
            if c.is_some_and(|c| c.keys().any(|k| k != "kind" && k != "target")) {
                no("§1", "channel has a field other than kind and target".into());
            }
            match (kind, target) {
                (Some(kind), Some(target)) => Some(Channel { kind: kind.into(), target: target.into() }),
                _ => {
                    no("W4", "channel lacks kind or target".into());
                    None
                }
            }
        }
    };
    let outward = channel.as_ref().is_some_and(|c| !issued.inside_targets.contains(&c.target));

    // Labels (W6 to W9). A Build entry has none.
    let (mut label, mut releases) = (BTreeSet::new(), BTreeSet::new());
    if !run {
        if o.contains_key("result") || o.contains_key("destinations") {
            no("§1", "a Build entry has no labels".into());
        }
    } else {
        let result = o.get("result").and_then(Value::as_object);
        match result.and_then(|r| r.get("label")).map(|l| names(Some(l))) {
            Some(Some(l)) => label = l,
            _ => no("W6", "a Run entry has no result.label".into()),
        }
        match names(result.and_then(|r| r.get("releases"))) {
            Some(r) => releases = r,
            None => no("W6", "result.releases is not a list of names".into()),
        }
        if result.is_some_and(|r| r.keys().any(|k| k != "label" && k != "releases")) {
            no("§1", "result has a field other than label and releases".into());
        }
        for l in label.iter().chain(&releases).filter(|l| !vocabulary.contains(*l)) {
            no("W6", format!("label {l:?} is outside the vocabulary"));
        }
        if outward && !label.contains("untrusted") {
            no("W7", "an outward entry's result.label lacks untrusted".into());
        }
        if releases.iter().any(|l| RESERVED.contains(&l.as_str())) && !issued.releasers.contains(key) {
            no("W8", "result.releases holds a reserved name and the issued rules do not name the entry".into());
        }
        let marked = inputs.values().any(|i| i.destination);
        let none = match o.get("destinations") {
            None => false,
            Some(Value::String(s)) if s == "none" => true,
            Some(_) => {
                no("W9", "destinations is present and is not \"none\"".into());
                false
            }
        };
        if none && marked {
            no("W9", "the entry says it has no destination and marks an input as one".into());
        }
        if outward && !inputs.is_empty() && !marked && !none {
            no("W9", "an outward entry takes inputs, marks none as a destination and does not say it has none".into());
        }
    }

    Some(Entry {
        name: name.to_string(),
        digest: digest.to_string(),
        domain,
        purpose: purpose.to_string(),
        inputs,
        label,
        releases,
        channel,
        outward,
    })
}
