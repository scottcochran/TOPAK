//! The evaluators of a use-case simulation, behind one line-oriented process.
//!
//!     topak-sim-engine name=policy.wasm:data.json ...
//!
//! One JSON request per line on stdin, one JSON reply per line on stdout. An error is reported and
//! is never read as an allow.
//!
//!   {"b": bundle, "e": entrypoint, "i": input}         a bundle, in opa-wasm (topak-bundle's engine)
//!   {"op": "floor", "req": {principal, action, resource, context, entities}}
//!                                                      the linked, digest-pinned Cedar floor
//!   {"op": "info"}                                     the floor's digests and engine
//!   {"op": "wf_load" | "wf_grant" | "wf_end" | "wf_cover" | "wf_route" | "wf_lapse" | "wf_fail" |
//!    "wf_finding" | "wf_fence", "run": name, ...}      the reference's workflow `Run`
//!
//! The `wf_*` handlers call `topak_core::workflow::Run` and follow `State::workflow_advance`
//! (mechanism/crates/topak-core/src/workflow.rs) step for step. Each returns the run without its
//! definition, and the edges that fired.
use std::collections::{BTreeSet, HashMap};
use std::io::{BufRead, Write};

use opa_wasm::wasmtime::{Config, Engine, Module, Store};
use opa_wasm::{DefaultContext, Policy, Runtime};
use serde_json::{Value, json};
use topak_core::admit::FloorOutcome;
use topak_core::labels::Label;
use topak_core::lift::FrozenInput;
use topak_core::workflow::{ActStatus, Attributes, Definition, EdgeKind, EndKind, EventState, Run};
use topak_core::{Digest, Domain, SeatKind};
use topak_floor::Floor;

struct Compiled {
    store: Store<()>,
    policy: Policy<DefaultContext>,
}

fn view(run: &Run, fired: Vec<Value>) -> Value {
    let mut v = serde_json::to_value(run).expect("a run serialises");
    v.as_object_mut().expect("object").remove("def");
    json!({"ok": true, "run": v, "fired": fired})
}

/// Steps 4 to 6 of the reference's advance: computed edges once each, dead decision events, then
/// joins, skips, completion and failure.
fn advance(run: &mut Run, at: u64) -> Vec<Value> {
    let mut fired = Vec::new();
    if !run.running() {
        return fired;
    }
    loop {
        let mut fire = None;
        'find: for (i, a) in run.acts.iter().enumerate() {
            if a.status != ActStatus::Ended || !a.covered {
                continue;
            }
            for (eid, e) in run.def.out_edges(&a.node) {
                if e.kind == EdgeKind::Computed && !run.evaluated.contains(&(i, eid.clone())) {
                    fire = Some((i, eid.clone()));
                    break 'find;
                }
            }
        }
        let Some((i, eid)) = fire else { break };
        run.evaluated.insert((i, eid.clone()));
        match run.disabled(i, &eid) {
            None => {
                let n = run.acts.len();
                run.enter(i, &eid, at);
                let new = (run.acts.len() > n).then_some(n);
                fired.push(json!({"from_act": i, "edge": eid, "to": run.def.edges[&eid].to, "act": new}));
            }
            Some(why) => {
                if why != "guard" {
                    fired.push(json!({"from_act": i, "edge": eid, "blocked": why}));
                }
            }
        }
    }
    let dead: Vec<usize> = run
        .events
        .iter()
        .filter(|(ev, s)| {
            **s == EventState::Open
                && run.acts[**ev].covered
                && run
                    .def
                    .out_edges(&run.acts[**ev].node)
                    .filter(|(_, e)| e.kind == EdgeKind::Chosen)
                    .all(|(eid, _)| run.disabled(**ev, eid).is_some())
        })
        .map(|(ev, _)| *ev)
        .collect();
    for ev in dead {
        run.events.insert(ev, EventState::Failed { why: "no chosen edge is enabled".into() });
    }
    run.settle_joins(at);
    run.settle();
    fired
}

fn usize_of(r: &Value, k: &str) -> Result<usize, String> {
    r[k].as_u64().map(|x| x as usize).ok_or(format!("{k} is required"))
}

fn str_of<'a>(r: &'a Value, k: &str) -> Result<&'a str, String> {
    r[k].as_str().ok_or(format!("{k} is required"))
}

fn wf_op(runs: &mut HashMap<String, Run>, op: &str, r: &Value, tick: &mut u64) -> Result<Value, String> {
    *tick += 1;
    let at = *tick;
    let name = str_of(r, "run")?;
    if op == "wf_load" {
        let text = str_of(r, "text")?;
        let def = Definition::parse(text)?;
        let seats = r["seats"].clone();
        let lookup = |s: &str| -> Option<(SeatKind, Domain, u8)> {
            let e = seats.get(s)?;
            let kind = serde_json::from_value(e["kind"].clone()).ok()?;
            let domain = serde_json::from_value(e["domain"].clone()).ok()?;
            Some((kind, domain, e["rung"].as_u64().unwrap_or(0) as u8))
        };
        let check = def.check(&lookup);
        let outward: BTreeSet<String> = def.nodes.iter().filter(|(_, n)| n.outward).map(|(k, _)| k.clone()).collect();
        let run = Run::new(def, Digest::of(text.as_bytes()), at, 1, 1, outward);
        let reply = json!({"ok": true, "check": check, "run": view(&run, vec![])["run"]});
        runs.insert(name.to_string(), run);
        return Ok(reply);
    }
    let run = runs.get_mut(name).ok_or("no such run")?;
    match op {
        // A grant for a node's round. `Err` refuses it, and a mesh then fails (ADR-0055 §2).
        "wf_grant" => {
            let i = usize_of(r, "act")?;
            if run.acts[i].status != ActStatus::Ready {
                return Err("the activation is not ready".into());
            }
            let node = run.acts[i].node.clone();
            if let Err(why) = run.charge(&node) {
                let fired = advance(run, at);
                return Ok(json!({"refused": why, "run": view(run, fired)["run"]}));
            }
            run.acts[i].status = ActStatus::Running { fence: r["fence"].as_u64().unwrap_or(at) };
        }
        // An orchestrator's round for a decision event.
        "wf_grant_decision" => {
            let ev = usize_of(r, "event")?;
            if run.events.get(&ev) != Some(&EventState::Open) {
                return Err("the decision event is not open".into());
            }
            let seat = run.def.orchestrator.as_ref().ok_or("no orchestrator is seated")?.seat.as_str().to_string();
            if let Err(why) = run.charge(&seat) {
                let fired = advance(run, at);
                return Ok(json!({"refused": why, "run": view(run, fired)["run"]}));
            }
            run.events.insert(ev, EventState::Served { fence: r["fence"].as_u64().unwrap_or(at) });
        }
        "wf_end" => {
            let i = usize_of(r, "act")?;
            let end: EndKind = serde_json::from_value(r["end"].clone()).map_err(|e| e.to_string())?;
            let label: Label = serde_json::from_value(r["label"].clone()).unwrap_or_default();
            let a = &mut run.acts[i];
            if matches!(end, EndKind::Fenced | EndKind::Revoked) {
                a.status = ActStatus::Failed { why: format!("its round ended {end:?}") };
            } else {
                a.status = ActStatus::Ended;
                a.attrs = Some(Attributes {
                    end,
                    actuates: r["actuates"].as_u64().unwrap_or(0),
                    label,
                    outcome: r["outcome"].as_str().map(str::to_string),
                    output: vec![],
                });
                let node = a.node.clone();
                if run.def.has_chosen(&node) {
                    run.events.insert(i, EventState::Open);
                }
            }
        }
        "wf_cover" => run.acts[usize_of(r, "act")?].covered = true,
        "wf_finding" => run.acts[usize_of(r, "act")?].found = true,
        "wf_fail" => run.acts[usize_of(r, "act")?].status = ActStatus::Failed { why: str_of(r, "why")?.to_string() },
        // The checks of `route_check`, for a round that holds the event.
        "wf_route" => {
            let ev = usize_of(r, "event")?;
            let edge = str_of(r, "edge")?;
            if !run.running() {
                return Err("ended".into());
            }
            if !matches!(run.events.get(&ev), Some(EventState::Served { .. })) {
                return Err("closed".into());
            }
            let e = run.def.edges.get(edge).ok_or("guard")?;
            if e.kind != EdgeKind::Chosen || e.from != run.acts[ev].node {
                return Err("guard".into());
            }
            if let Some(why) = run.disabled(ev, edge) {
                return Err(why.into());
            }
            run.events.insert(ev, EventState::Consumed { edge: edge.to_string() });
            run.enter(ev, edge, at);
        }
        // A lapsed orchestrator fails its decision point and takes no edge (ADR-0054 §8).
        "wf_lapse" => {
            let ev = usize_of(r, "event")?;
            run.events.insert(ev, EventState::Failed { why: str_of(r, "why")?.to_string() });
        }
        // The epoch or rules epoch moved (ADR-0054 §9).
        "wf_fence" => {
            for a in run.acts.iter_mut().filter(|a| matches!(a.status, ActStatus::Ready | ActStatus::Waiting)) {
                a.status = ActStatus::Failed { why: "fenced before its grant".into() };
            }
            run.fail("the epoch or rules epoch moved (ADR-0054 §9)");
        }
        // Which chosen edges are enabled at a decision event, and why the rest are not.
        "wf_enabled" => {
            let ev = usize_of(r, "event")?;
            let node = run.acts[ev].node.clone();
            let mut out = serde_json::Map::new();
            for (id, e) in run.def.out_edges(&node) {
                if e.kind == EdgeKind::Chosen {
                    out.insert(id.clone(), json!(run.disabled(ev, id)));
                }
            }
            return Ok(json!({"ok": true, "edges": out}));
        }
        _ => return Err(format!("unknown op {op}")),
    }
    let fired = advance(run, at);
    Ok(view(run, fired))
}

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    let mut bundles = HashMap::new();
    for arg in std::env::args().skip(1) {
        let (name, paths) = arg.split_once('=').expect("name=policy.wasm:data.json");
        let (wasm, data) = paths.split_once(':').expect("policy.wasm:data.json");
        let engine = Engine::new(&Config::new())?;
        let module = Module::new(&engine, std::fs::read(wasm)?)?;
        let mut store = Store::new(&engine, ());
        let runtime = Runtime::new(&mut store, &module).await?;
        let data: Value = serde_json::from_str(&std::fs::read_to_string(data)?)?;
        let policy = runtime.with_data(&mut store, &data).await?;
        bundles.insert(name.to_string(), Compiled { store, policy });
    }
    // A floor whose bytes are not the gated bytes refuses to load, here as in the reference.
    let floor = Floor::load().map_err(|e| anyhow::anyhow!("{e}"))?;
    let mut runs: HashMap<String, Run> = HashMap::new();
    let mut tick = 0u64;
    let stdin = std::io::stdin();
    let mut out = std::io::stdout().lock();
    for line in stdin.lock().lines() {
        let req: Value = serde_json::from_str(&line?)?;
        let op = req["op"].as_str().unwrap_or("bundle").to_string();
        let reply = match op.as_str() {
            "bundle" => match bundles.get_mut(req["b"].as_str().unwrap_or("")) {
                None => json!({"err": "no such bundle"}),
                Some(c) => {
                    let entry = req["e"].as_str().unwrap_or("");
                    let res: anyhow::Result<Value> = c.policy.evaluate(&mut c.store, entry, &req["i"]).await;
                    match res {
                        Ok(v) => json!({"r": v}),
                        Err(e) => json!({"err": e.to_string()}),
                    }
                }
            },
            "floor" => {
                let r = &req["req"];
                let input = FrozenInput {
                    principal: r["principal"].clone(),
                    action: r["action"].clone(),
                    resource: r["resource"].clone(),
                    context: r["context"].clone(),
                    entities: r["entities"].clone(),
                    bundle_input: Value::Null,
                };
                match floor.decide(&input) {
                    FloorOutcome::Permit { reasons } => json!({"permit": true, "reasons": reasons}),
                    FloorOutcome::Deny { reasons } => json!({"permit": false, "reasons": reasons}),
                    FloorOutcome::Error { diagnostics } => json!({"permit": false, "reasons": [], "error": diagnostics}),
                }
            }
            "info" => json!({
                "floor": floor.floor_digest().0,
                "schema": floor.schema_digest().0,
                "values": floor.values_digest().0,
                "engine": topak_floor::ENGINE,
            }),
            o if o.starts_with("wf_") => match wf_op(&mut runs, o, &req, &mut tick) {
                Ok(v) => v,
                Err(e) => json!({"err": e}),
            },
            o => json!({"err": format!("unknown op {o}")}),
        };
        writeln!(out, "{reply}")?;
        out.flush()?;
    }
    Ok(())
}
