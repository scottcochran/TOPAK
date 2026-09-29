//! The syntactic lift (ADR-0007, ADR-0018 validator side, ADR-0030 §4).
//!
//! Mechanical, total extraction from the typed request and replicated state into the one frozen
//! input both policy tiers evaluate. Nothing here interprets meaning: every fact is a set
//! membership, an equality, or a path-syntax check. The floor's inputs are written only here and
//! from the issued rules; no bundle has a write path to any of it (ADR-0030 §3).
//!
//! Output shapes follow Cedar's JSON formats for `genesis.cedarschema`, so the floor crate can
//! hand them to the engine unchanged and the schema validator enforces S on every request.

use serde::{Deserialize, Serialize};
use serde_json::{Value, json};

use crate::action::{Action, ActionRequest, tool_id};
use crate::state::{LeaseRecord, MechanismDeny, Params, State};
use crate::types::*;

pub const NS: &str = "Topak";

/// The frozen input. Resolved once; floor and bundle evaluate the same facts, and the bundle
/// may not re-fetch anything about the request (ADR-0030 §4).
#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct FrozenInput {
    pub principal: Value,
    pub action: Value,
    pub resource: Value,
    pub context: Value,
    pub entities: Value,
    /// The bundle tier's view, derived from the same facts at lift time.
    pub bundle_input: Value,
}

impl FrozenInput {
    pub fn digest(&self) -> Digest {
        Digest::of_json(self)
    }
}

/// One topic per principal per round (ADR-0003). The chain id — the genesis rules' digest —
/// keeps a successor system after re-genesis from reopening its predecessor's topics.
pub fn topic_name(chain: &Digest, domain: Domain, seat: &str, epoch: Epoch, round: Round) -> String {
    format!("topak.{}.{}.{}.e{}.r{}", &chain.0[..chain.0.len().min(12)], domain.as_str(), seat, epoch, round)
}

/// The round's `after` companion (ADR-0003 A2): denials under the round's lease once
/// its topic has sealed. Same subject and round, so it is erased with the round.
pub fn after_topic_name(chain: &Digest, domain: Domain, seat: &str, epoch: Epoch, round: Round) -> String {
    format!("{}.after", topic_name(chain, domain, seat, epoch, round))
}

pub fn workspace_id(seat: &str, epoch: Epoch, round: Round) -> String {
    format!("ws-{seat}-e{epoch}-r{round}")
}

/// A workspace-relative path, or `None` if the string could reach outside the workspace.
/// Syntax only: no filesystem is consulted, so the answer cannot depend on the environment.
pub fn workspace_relative(p: &str) -> Option<String> {
    if p.is_empty() || p.starts_with('/') || p.contains('\\') || p.contains('\0') || p.contains("://") {
        return None;
    }
    let parts: Vec<&str> = p.split('/').filter(|c| !c.is_empty() && *c != ".").collect();
    if parts.is_empty() || parts.contains(&"..") {
        return None;
    }
    Some(parts.join("/"))
}

/// PROVISIONAL (inputs-in-workspace lift): tool schemas do not mark which arguments are paths,
/// so every string leaf must be workspace-relative by syntax. Coarse and fail-closed: an
/// argument that merely looks like a URL or absolute path refuses the invocation.
pub fn inputs_in_workspace(v: &Value) -> bool {
    match v {
        Value::String(s) => workspace_relative(s).is_some(),
        Value::Array(a) => a.iter().all(inputs_in_workspace),
        Value::Object(o) => o.values().all(inputs_in_workspace),
        _ => true,
    }
}

fn uid(t: &str, id: &str) -> Value {
    json!({ "type": format!("{NS}::{t}"), "id": id })
}

fn eref(t: &str, id: &str) -> Value {
    json!({ "__entity": uid(t, id) })
}

fn ent(t: &str, id: &str, attrs: Value, parents: Vec<Value>) -> Value {
    json!({ "uid": uid(t, id), "attrs": attrs, "parents": parents })
}

fn long(n: u64) -> Result<i64, MechanismDeny> {
    i64::try_from(n).map_err(|_| MechanismDeny::Other("value exceeds Cedar Long".into()))
}

/// Lift a request that already passed `State::check_live`.
pub fn lift(
    req: &ActionRequest,
    state: &State,
    params: &Params,
    rec: &LeaseRecord,
    observer_live: bool,
) -> Result<FrozenInput, MechanismDeny> {
    let rules = &state.rules;
    let seat = req.seat.as_str();
    let domain = rules.seat_domain(seat).ok_or_else(|| MechanismDeny::Other(format!("seat {seat} is not declared")))?;
    let lease = &rec.lease;
    let round = lease.round;
    let ws = workspace_id(seat, lease.epoch, round);

    let seat_entity = |s: &str| -> Value {
        let mut parents = Vec::new();
        if rules.grant_roster.contains(s) {
            parents.push(uid("Roster", "grant"));
        }
        if rules.veto_roster.contains(s) {
            parents.push(uid("Roster", "veto"));
        }
        let d = rules.seat_domain(s).map(Domain::as_str).unwrap_or("unknown");
        let k = rules.seat_kind(s).map(SeatKind::as_str).unwrap_or("unknown");
        ent("Seat", s, json!({ "domain": d, "kind": k }), parents)
    };

    // The slice must be complete for every entity the floor can reference (ADR-0030 §4).
    let mut entities = vec![
        ent("Roster", "grant", json!({}), vec![]),
        ent("Roster", "veto", json!({}), vec![]),
        seat_entity(seat),
        ent("CorpusRoot", "pinned", json!({}), vec![]),
        ent("Workspace", &ws, json!({}), vec![]),
        ent("ToolSet", "build-allow", json!({}), vec![]),
        ent("ToolSet", "run-allow", json!({}), vec![]),
        ent("ToolSet", "bg-tools", json!({}), vec![]),
    ];

    let alphabet: Vec<&str> = lease.alphabet.iter().map(|k| k.as_str()).collect();
    let lease_ctx = json!({ "alphabet": alphabet, "rulesEpoch": long(lease.rules_epoch)? });
    let build_ctx = |inputs_ok: bool| -> Result<Value, MechanismDeny> {
        Ok(json!({
            "lease": lease_ctx,
            "epoch": long(state.epoch)?,
            "round": long(round)?,
            "roundRole": lease.role.as_str(),
            "corpusRoot": eref("CorpusRoot", "pinned"),
            "workspace": eref("Workspace", &ws),
            "toolAllowlist": eref("ToolSet", "build-allow"),
            "inputsInWorkspace": inputs_ok,
        }))
    };
    let run_ctx = || -> Result<Value, MechanismDeny> {
        Ok(json!({
            "lease": lease_ctx,
            "epoch": long(state.epoch)?,
            "round": long(round)?,
            "corpusRoot": eref("CorpusRoot", "pinned"),
            "toolAllowlist": eref("ToolSet", "run-allow"),
            "breakGlass": {
                "quorum": state.break_glass_quorum(seat),
                "tools": eref("ToolSet", "bg-tools"),
            },
            // ADR-0039 §1: live(o) for some cell Observer of this seat, computed by the mechanism.
            "observerLive": observer_live,
        }))
    };
    let topic = |d: Domain| -> Result<(Value, String), MechanismDeny> {
        let name = topic_name(&state.chain, d, seat, lease.epoch, round);
        let e = ent(
            "Topic",
            &name,
            json!({
                "owner": eref("Seat", seat),
                "epoch": long(lease.epoch)?,
                "round": long(round)?,
                "sealed": !rec.live(),
            }),
            vec![],
        );
        Ok((e, name))
    };

    let kind = req.action.kind();
    let (resource, context, bundle_resource) = match &req.action {
        Action::Read { object } => {
            let parents = if params.corpus.contains(object) { vec![uid("CorpusRoot", "pinned")] } else { vec![] };
            entities.push(ent("CorpusObject", &object.0, json!({}), parents));
            (uid("CorpusObject", &object.0), build_ctx(true)?, json!({ "object": object }))
        }
        Action::Draft { target, .. } => {
            let (id, parents) = match workspace_relative(target) {
                Some(rel) => (format!("{ws}/{rel}"), vec![uid("Workspace", &ws)]),
                None => (format!("{ws}/!{target}"), vec![]),
            };
            entities.push(ent("WorkspaceTarget", &id, json!({}), parents));
            (uid("WorkspaceTarget", &id), build_ctx(true)?, json!({ "target": target }))
        }
        Action::Invoke { tool, digest, inputs } | Action::RunInvoke { tool, digest, inputs } => {
            let tid = tool_id(tool, digest);
            let mut parents = Vec::new();
            if kind == ActionKind::Invoke && params.build_tools.contains(&tid) {
                parents.push(uid("ToolSet", "build-allow"));
            }
            if kind == ActionKind::RunInvoke && params.run_tools.contains(&tid) {
                parents.push(uid("ToolSet", "run-allow"));
            }
            if kind == ActionKind::RunInvoke && rules.break_glass.as_ref().is_some_and(|bg| bg.tools.contains(&tid)) {
                parents.push(uid("ToolSet", "bg-tools"));
            }
            entities.push(ent("Tool", &tid, json!({ "digest": digest }), parents));
            let ctx = if kind == ActionKind::Invoke {
                build_ctx(inputs_in_workspace(&Value::Object(inputs.clone())))?
            } else {
                run_ctx()?
            };
            (uid("Tool", &tid), ctx, json!({ "tool": tool, "digest": digest }))
        }
        Action::Emit { .. } | Action::RunEmit { .. } => {
            let (e, name) = topic(kind.domain())?;
            entities.push(e);
            let ctx = if kind == ActionKind::Emit { build_ctx(true)? } else { run_ctx()? };
            (uid("Topic", &name), ctx, json!({ "topic": name }))
        }
        Action::Submit { artifact } => {
            // The submitter is the author: a syntactic fact of who performed `Submit`.
            entities.push(ent("Artifact", &artifact.0, json!({ "author": eref("Seat", seat) }), vec![]));
            (uid("Artifact", &artifact.0), build_ctx(true)?, json!({ "artifact": artifact }))
        }
        Action::Vote { verdict, artifact, rules_epoch, evidence } => {
            let c = state.candidates.get(artifact).ok_or(MechanismDeny::ArtifactNotSubmitted)?;
            entities.push(ent("Artifact", &artifact.0, json!({ "author": eref("Seat", &c.author) }), vec![]));
            if c.author != seat {
                entities.push(seat_entity(&c.author));
            }
            let ctx = json!({
                "lease": lease_ctx,
                "epoch": long(state.epoch)?,
                "rulesEpoch": long(rules.rules_epoch)?,
                "verdict": verdict.as_str(),
                "voteRulesEpoch": long(*rules_epoch)?,
                "grantRoster": eref("Roster", "grant"),
                "vetoRoster": eref("Roster", "veto"),
            });
            (uid("Artifact", &artifact.0), ctx, json!({ "artifact": artifact, "evidence": evidence }))
        }
    };

    let inputs = match &req.action {
        Action::Invoke { inputs, .. } | Action::RunInvoke { inputs, .. } => Value::Object(inputs.clone()),
        _ => Value::Null,
    };
    let bundle_input = json!({
        "action": kind.as_str(),
        "principal": { "seat": seat, "domain": domain.as_str() },
        "resource": bundle_resource,
        "inputs": inputs,
        "request": req.action,
        "context": {
            "epoch": state.epoch,
            "round": round,
            "roundRole": lease.role.as_str(),
            "rulesEpoch": rules.rules_epoch,
            "lease": lease.fence,
        },
    });

    Ok(FrozenInput {
        principal: uid("Seat", seat),
        action: json!({ "type": format!("{NS}::Action"), "id": kind.as_str() }),
        resource,
        context,
        entities: Value::Array(entities),
        bundle_input,
    })
}
