//! A workflow's requests (ADR-0054, Proposed) lifted from the replicated state and decided by the
//! linked floor, the `workflow` stage: `Route` through `R8`, `R9` and `R3`, and the one behaviour of
//! ADR-0054 §12 that needs the floor, "a `clear` input raises the receiver's `clearSet` and R5 then
//! refuses its outward call". The state is built with the core's harness (`topak-core/tests/support`).

#[path = "../../topak-core/tests/support/wf.rs"]
mod wf;

use serde_json::{Map, json};
use topak_core::action::{Action, ActionRequest};
use topak_core::admit::FloorOutcome;
use topak_core::labels::{Delivery, LabelFacts, RESTRICTED, UNTRUSTED};
use topak_core::lift::lift;
use topak_core::*;
use topak_floor::Floor;
use wf::*;

fn decide(log: &Log, req: &ActionRequest, observer_live: bool, facts: Option<&LabelFacts>) -> FloorOutcome {
    let rec = &log.s.leases[&req.lease];
    let frozen = lift(req, &log.s, &params(), rec, observer_live, facts).expect("lifted");
    Floor::load().expect("pinned floor").decide(&frozen)
}

fn permitted_by(o: &FloorOutcome, id: &str) -> bool {
    matches!(o, FloorOutcome::Permit { reasons } if reasons.iter().any(|r| r == id))
}

fn denied_by(o: &FloorOutcome, id: &str) -> bool {
    matches!(o, FloorOutcome::Deny { reasons } if reasons.iter().any(|r| r == id))
}

/// `s` runs and reports `outcome` after reading `label` in the clear, its Observer covers it, and
/// the orchestrator is granted the decision event.
fn at_decision(log: &mut Log, label: &[&str], outcome: &str) {
    log.grant_ready();
    if !label.is_empty() {
        log.reads("ws", label);
    }
    let fs = log.fence_of("ws");
    log.outcome("ws", outcome);
    log.cover(fs);
    log.grant_ready();
}

#[test]
fn a_route_is_decided_by_r8_r9_and_r3() {
    let mut log = Log::started(&dag());
    at_decision(&mut log, &[], "ok");
    let route = log.request("orc", Action::Route { edge: "e1".into() });
    // The orchestrator's round is granted for s's decision point, and e1 is a chosen edge out of it.
    assert!(permitted_by(&decide(&log, &route, true, None), "R8-route-own-decision"));
    // With no live cell Observer, R3 couples the orchestrator as it does a Thinker (ADR-0039 A3).
    assert!(denied_by(&decide(&log, &route, false, None), "R3-observer-live"));
    // A computed edge is not the orchestrator's to take: R8 does not permit it.
    let computed = log.request("orc", Action::Route { edge: "e3".into() });
    assert!(matches!(decide(&log, &computed, true, None), FloorOutcome::Deny { reasons } if reasons.is_empty()));
    // Its Report is R2's, to its own round topic.
    let report = log.request("orc", Action::Report { record: json!({ "note": "chose e1" }) });
    assert!(permitted_by(&decide(&log, &report, true, None), "R2-report-own-topic"));
    // A Thinker's lease, lifted with no decision point: R9 refuses `Route` from any other kind.
    let thinker = ActionRequest { seat: "ws".into(), ..route.clone() };
    let mut st = log.s.clone();
    let fo = log.fence_of("orc");
    st.leases.get_mut(&fo).unwrap().lease.seat = "ws".into();
    let rec = &st.leases[&fo];
    let frozen = lift(&thinker, &st, &params(), rec, true, None).unwrap();
    assert!(denied_by(&Floor::load().unwrap().decide(&frozen), "R9-only-orchestrators-route"));
}

#[test]
fn a_clear_input_raises_the_receivers_clear_set_and_r5_then_refuses_its_outward_call() {
    // b's round, after `s` read untrusted content and routed to b along the clear e1.
    let mut log = Log::started(&dag());
    at_decision(&mut log, &[UNTRUSTED], "ok");
    log.route("e1");
    log.cover_orc();
    log.grant_ready();
    // b reads restricted content itself, then makes an outward call.
    log.reads("wb", &[RESTRICTED]);
    let fb = log.fence_of("wb");
    let cs = log.s.leases[&fb].labels.clear_set.clone();
    assert!(cs.contains(UNTRUSTED) && cs.contains(RESTRICTED), "{cs:?}");
    let call = Action::Actuate { tool: "post".into(), digest: Digest("d5".into()), inputs: Map::new() };
    let facts = LabelFacts { clear_set: cs, outward: true, delivery: Delivery::Clear, ..Default::default() };
    let req = log.request("wb", call.clone());
    assert!(denied_by(&decide(&log, &req, true, Some(&facts)), "R5-no-read-then-send"));

    // The same round with s clean: b's clearSet holds restricted and not untrusted, and R1 admits it.
    let mut clean = Log::started(&dag());
    at_decision(&mut clean, &[], "ok");
    clean.route("e1");
    clean.cover_orc();
    clean.grant_ready();
    clean.reads("wb", &[RESTRICTED]);
    let fb = clean.fence_of("wb");
    let cs = clean.s.leases[&fb].labels.clear_set.clone();
    assert!(!cs.contains(UNTRUSTED));
    let facts = LabelFacts { clear_set: cs, outward: true, delivery: Delivery::Clear, ..Default::default() };
    let req = clean.request("wb", call);
    assert!(permitted_by(&decide(&clean, &req, true, Some(&facts)), "R1-actuate-allowlisted"));
}

#[test]
fn every_run_request_carries_its_decision_point() {
    // A worker's request lifts an empty decision point and decides as before the stage: the field
    // is required in S, so a request without it would be an error, and every error is a deny.
    let mut log = Log::started(&dag());
    log.grant_ready();
    let req = log.request("ws", Action::Report { record: json!({ "progress": 1 }) });
    let rec = &log.s.leases[&req.lease];
    let frozen = lift(&req, &log.s, &params(), rec, true, None).unwrap();
    assert_eq!(frozen.context["decisionPoint"], json!([]));
    assert!(permitted_by(&Floor::load().unwrap().decide(&frozen), "R2-report-own-topic"));
}
