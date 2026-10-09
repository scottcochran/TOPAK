//! Workflows (ADR-0054) and meshes (ADR-0055), both Proposed, at the state. The properties are
//! `spec/Workflow.tla`'s and `spec/Mesh.tla`'s; each test names the property it shows and the
//! mutation whose state it shows is refused. Every behaviour of ADR-0054 §12 and ADR-0055 §11's
//! reference item is here but one, "a clear input raises the receiver's `clearSet` and R5 then
//! refuses its outward call", whose second half needs the floor: `topak-floor/tests/workflow.rs`.
//!
//! | Test | Property (mutation) | Record |
//! |---|---|---|
//! | `a_computed_edge_fires_on_a_typed_attribute` | `NeverComputed` witness; a false guard never fires | 0054 §3, §4 |
//! | `a_route_applies_and_the_workflow_completes_by_its_sink` | `AppliedRouteEnabled`, `CompletedOnlyBySink` | 0054 §8, §9 |
//! | `a_route_decided_before_a_finding_and_applied_after_is_void` | `FindingPrecedesNoRoute` (`M_DECIDEONLY`) | 0054 §8 |
//! | `a_second_route_to_a_consumed_decision_point_is_void` | `OneRoutePerDecision` (`M_NOCONSUME`) | 0054 §8 |
//! | `a_lapsed_orchestrator_fails_its_decision_point` | `ChosenOnlyByRoute` (`M_DEFAULT`) | 0054 §8 |
//! | `an_untrusted_attribute_disables_the_edge_into_an_outward_node` | `TaintedNeverOutward` (`M_NOTAINT`) | 0054 §5 |
//! | `a_clear_input_joins_the_receivers_clear_set` | ADR-0043 A3, ADR-0047 A1 | 0054 §5 |
//! | `an_edge_waits_for_its_sources_coverage` | `EdgeAfterCoverage` (`M_UNCOVERED`) | 0054 §7 |
//! | `a_fence_fails_a_node_not_yet_granted` | `GrantUnderPromotion` (`M_GRANTANYEPOCH`) | 0054 §2, §9 |
//! | `a_workflow_loads_only_promoted_and_well_formed` | a cycle, no promotion, `PromotedAlternates` (`M_NOLINEAGE`) | 0054 §1, §6 |
//! | `only_the_orchestrator_routes_and_only_its_own_decision` | `Route`'s envelope | 0054 §3 |
//! | `the_loop_turns_twice_and_exits` | `NeverCompletedAfterLoop` witness | 0055 §2, §3 |
//! | `the_budget_refuses_a_grant_and_the_workflow_fails` | `BudgetBound` (`M_OVERRUN`), `CompletedOnlyBySink` (`M_BUDGETDONE`) | 0055 §2 |
//! | `an_orchestrator_round_is_charged` | `BudgetBound` (`M_ORCHFREE`) | 0055 §2, §6 |
//! | `a_finding_against_the_workers_round_voids_the_decision_nodes_next_route` | `NoActivationAfterFinding` (`M_SOURCEONLY`) | 0055 §3 |
//! | `a_route_decided_in_one_round_and_committed_after_it_ends_is_void` | `RouteOnItsEvent` (`M_TRACKER`) | 0055 §6 |
//! | `untrusted_content_read_on_the_loop_disables_the_exit` | `LabelCoversTruth`, `TaintedNeverOutward` (`M_FORGETTAINT`) | 0055 §5 |
//! | `a_mesh_loads_only_with_a_budget_and_two_coloured_clear_edges` | `ClearHopsAlternate` (`M_NOLINEAGE`) | 0055 §1, §5 |

mod support;

use serde_json::json;
use support::wf::*;
use topak_core::action::Action;
use topak_core::labels::UNTRUSTED;
use topak_core::state::*;
use topak_core::workflow::*;
use topak_core::*;

fn running(log: &Log) -> bool {
    log.run().status == RunStatus::Running
}

fn failed(log: &Log, why: &str) -> bool {
    matches!(&log.run().status, RunStatus::Failed { why: w } if w.contains(why))
}

/// `s` runs, reports `outcome`, and is covered; its decision event opens and the orchestrator is
/// granted a round for it.
fn decide_at_s(log: &mut Log, outcome: &str) -> LogIndex {
    let fs = log.work("ws", outcome);
    assert_eq!(
        log.grant_ready(),
        vec![Applied::LeaseGranted { fence: log.at }],
        "the orchestrator is granted the event"
    );
    fs
}

// ---- ADR-0054 ------------------------------------------------------------------------------------

#[test]
fn a_computed_edge_fires_on_a_typed_attribute() {
    let mut log = Log::started(&dag());
    decide_at_s(&mut log, "ok");
    assert!(matches!(log.route("e1"), Applied::Admitted { .. }));
    log.cover_orc();
    // `b` reports `done`: once its Observer has read it to the seal, e3 fires in that apply.
    let fb = log.work("wb", "done");
    let j = log.acts("j");
    assert_eq!(j.len(), 1);
    assert_eq!(j[0].status, ActStatus::Ready, "e3 fired on b's typed outcome");
    assert_eq!(j[0].via.as_deref(), Some("e3"));
    assert!(log.run().evaluated.contains(&(log.act_of("b"), "e3".to_string())));
    let _ = fb;

    // The same graph, with `b` reporting `retry`: e3's guard is false when first evaluable, and a
    // computed edge is evaluated once. `j` is skipped, no sink ends, and the workflow fails.
    let mut log = Log::started(&dag());
    decide_at_s(&mut log, "ok");
    log.route("e1");
    log.cover_orc();
    log.work("wb", "retry");
    assert_eq!(log.acts("j")[0].status, ActStatus::Skipped, "a false guard never fires, and the skip propagates");
    assert!(failed(&log, "quiescent"));
}

#[test]
fn a_route_applies_and_the_workflow_completes_by_its_sink() {
    let mut log = Log::started(&dag());
    decide_at_s(&mut log, "ok");
    let fo = log.fence_of("orc");
    assert!(matches!(log.route("e1"), Applied::Admitted { seq: Some(1), .. }));
    // The route consumed the event, entered b, and ended the orchestrator's round (ADR-0042 A3).
    assert_eq!(log.run().events[&0], EventState::Consumed { edge: "e1".into() });
    assert_eq!(log.s.leases[&fo].ended, Some(EndReason::Routed));
    assert_eq!(log.acts("b")[0].status, ActStatus::Ready);
    log.work("wb", "done");
    assert!(running(&log), "the sink has not ended");
    log.work("wj", "done");
    assert_eq!(log.run().status, RunStatus::Completed);
    // `c` was never entered: e2 is dead once the event is consumed by e1, and `c` is skipped.
    assert_eq!(log.acts("c")[0].status, ActStatus::Skipped);
    // Every lease the workflow issued was granted at the promotion's epoch, under its seating.
    for b in log.s.wf_bindings.keys() {
        assert_eq!(log.s.leases[b].lease.epoch, 0);
    }
}

#[test]
fn a_route_decided_before_a_finding_and_applied_after_is_void() {
    let mut log = Log::started(&dag());
    let fs = decide_at_s(&mut log, "ok");
    // Decided at this state: s ended, covered, no finding. Not yet ordered.
    let decided = log.decide("orc", Action::Route { edge: "e1".into() }).expect("enabled at decide");
    // The correlator's finding against s's round is ordered first: coverage did not close the race.
    assert!(matches!(log.finding(fs), Applied::Admitted { .. }));
    let a = log.apply(decided);
    assert!(refused(&a, "route void (finding)"), "{a:?}");
    // Without the re-check at apply (`M_DECIDEONLY`) b would have been entered past the finding.
    assert!(log.acts("b").is_empty());
    // After a void the decision point stays open while the orchestrator's round is live; every
    // chosen edge out of s is disabled now, so it fails when that round ends, and with it the dag.
    let fo = log.fence_of("orc");
    assert_eq!(log.run().events[&0], EventState::Served { fence: fo });
    assert!(log.decide("orc", Action::Route { edge: "e2".into() }).unwrap_err().to_string().contains("finding"));
    let id = log.id("expire");
    log.apply(Entry::EndRound {
        id,
        seat: "orc".into(),
        fence: fo,
        reason: EndReason::Expired,
        attribution: "clock".into(),
    });
    assert!(matches!(log.run().events[&0], EventState::Failed { .. }));
    assert!(failed(&log, "a decision point failed"));
}

#[test]
fn a_second_route_to_a_consumed_decision_point_is_void() {
    let mut log = Log::started(&dag());
    decide_at_s(&mut log, "ok");
    // A Byzantine orchestrator decides both chosen edges before either is ordered.
    let r1 = log.decide("orc", Action::Route { edge: "e1".into() }).unwrap();
    let r2 = log.decide("orc", Action::Route { edge: "e2".into() }).unwrap();
    assert!(matches!(log.apply(r1), Applied::Admitted { .. }));
    let a = log.apply(r2);
    assert!(refused(&a, "route void (consumed)"), "{a:?}");
    assert!(log.acts("c").iter().all(|a| a.status == ActStatus::Skipped), "c is never entered");
}

#[test]
fn a_lapsed_orchestrator_fails_its_decision_point() {
    let mut log = Log::started(&dag());
    decide_at_s(&mut log, "ok");
    let fo = log.fence_of("orc");
    let id = log.id("expire");
    log.apply(Entry::EndRound {
        id,
        seat: "orc".into(),
        fence: fo,
        reason: EndReason::Expired,
        attribution: "clock".into(),
    });
    // No default edge: a grant made by a timeout is forbidden (ADR-0024 §2). The event fails.
    assert!(matches!(&log.run().events[&0], EventState::Failed { why } if why.contains("orchestrator")));
    // Neither b nor c is entered: both are skipped once the decision point has failed.
    assert!(log.acts("b").iter().chain(log.acts("c").iter()).all(|a| a.status == ActStatus::Skipped));
    assert!(failed(&log, "a decision point failed"));
    // A route under the lapsed round is refused at decide.
    let req = topak_core::action::ActionRequest {
        seat: "orc".into(),
        lease: fo,
        epoch: 0,
        action: Action::Route { edge: "e1".into() },
    };
    assert!(log.s.check_live(&req, &params()).is_err());
}

#[test]
fn an_untrusted_attribute_disables_the_edge_into_an_outward_node() {
    let mut log = Log::started(&dag());
    log.grant_ready();
    // s reads untrusted content in the clear: its label, and every attribute it lifts, is untrusted.
    assert!(matches!(log.reads("ws", &[UNTRUSTED]), Applied::Admitted { .. }));
    let fs = log.fence_of("ws");
    log.outcome("ws", "ok");
    log.cover(fs);
    log.grant_ready();
    assert!(log.acts("s")[0].attrs.as_ref().unwrap().label.contains(UNTRUSTED));
    // e2 enters the outward c: disabled by the routing rule, at decide, whatever the orchestrator wants.
    let d = log.decide("orc", Action::Route { edge: "e2".into() }).unwrap_err();
    assert!(d.to_string().contains("taint"), "{d}");
    // e1 into b, which is not outward and receives nothing restricted, stays enabled.
    assert!(matches!(log.route("e1"), Applied::Admitted { .. }));
}

#[test]
fn a_clear_input_joins_the_receivers_clear_set() {
    let mut log = Log::started(&dag());
    log.grant_ready();
    log.reads("ws", &[UNTRUSTED]);
    let fs = log.fence_of("ws");
    log.outcome("ws", "ok");
    log.cover(fs);
    log.grant_ready();
    log.route("e1");
    log.cover_orc();
    log.grant_ready();
    // b's round starts from its task's label joined with its clear input's: s's untrusted reading
    // crossed the cell boundary with s's output (ADR-0043 A3, ADR-0047 A1).
    let fb = log.fence_of("wb");
    let cs = &log.s.leases[&fb].labels.clear_set;
    assert!(cs.contains(UNTRUSTED) && cs.contains("internal"), "{cs:?}");
}

#[test]
fn an_edge_waits_for_its_sources_coverage() {
    let mut log = Log::started(&dag());
    decide_at_s(&mut log, "ok");
    log.route("e1");
    log.cover_orc();
    log.grant_ready();
    let fb = log.fence_of("wb");
    log.outcome("wb", "done");
    // b has ended with `done`, and its Observer has not read it to the seal: e3 is not evaluated.
    assert!(log.acts("j").is_empty(), "no edge out of an uncovered round (M_UNCOVERED)");
    assert!(!log.run().evaluated.contains(&(log.act_of("b"), "e3".to_string())));
    log.cover(fb);
    assert_eq!(log.acts("j")[0].status, ActStatus::Ready);
}

#[test]
fn a_fence_fails_a_node_not_yet_granted() {
    let mut log = Log::started(&dag());
    decide_at_s(&mut log, "ok");
    log.route("e1");
    log.cover_orc();
    assert_eq!(log.acts("b")[0].status, ActStatus::Ready, "b is ready and not granted");
    let b = log.act_of("b");
    let req = log.s.workflow_grant_request(&log.wf, &Slot::Node(b)).unwrap();
    let id = log.id("fence");
    log.apply(Entry::EpochIncrement { id, reason: "test".into(), attribution: "test".into() });
    assert!(matches!(&log.acts("b")[0].status, ActStatus::Failed { why } if why.contains("fenced before its grant")));
    assert!(failed(&log, "epoch"));
    // A grant proposed before the fence and ordered after it is refused (M_GRANTANYEPOCH).
    let id = log.id("late");
    let a = log.apply(Entry::WorkflowGrant { id, workflow: log.wf.clone(), slot: Slot::Node(b), req, appraisal: None });
    assert!(refused(&a, "not running"), "{a:?}");
    assert!(!log.s.live_by_seat.contains_key("wb"));
}

#[test]
fn a_workflow_loads_only_promoted_and_well_formed() {
    // Not promoted.
    let mut log = Log::new();
    let text = serde_json::to_string(&dag()).unwrap();
    assert!(refused(&log.load(&text), "not promoted"));
    // A dag with a cycle does not load, though its artifact was promoted.
    let mut cyclic = dag();
    cyclic["edges"]["back"] = json!({ "from": "j", "to": "b", "kind": "computed", "delivery": "handle" });
    let text = serde_json::to_string(&cyclic).unwrap();
    log.promote(&text);
    assert!(refused(&log.load(&text), "has a cycle"));
    // A clear edge with one lineage on both ends (`PromotedAlternates`, M_NOLINEAGE).
    let mut same = dag();
    same["nodes"]["b"]["lineage"] = json!("A");
    let text = serde_json::to_string(&same).unwrap();
    log.promote(&text);
    assert!(refused(&log.load(&text), "joins one lineage on both ends"));
    // A guard that reads a node which does not dominate its source (ADR-0054 §4).
    let mut unsettled = dag();
    unsettled["edges"]["e4"]["guard"] = json!({ "outcome": { "node": "b", "any_of": ["done"] } });
    let text = serde_json::to_string(&unsettled).unwrap();
    log.promote(&text);
    assert!(refused(&log.load(&text), "does not dominate c"));
    // A chosen edge and no orchestrator; and a worker seat that is not a thinker's.
    let mut bare = dag();
    bare.as_object_mut().unwrap().remove("orchestrator");
    let text = serde_json::to_string(&bare).unwrap();
    log.promote(&text);
    assert!(refused(&log.load(&text), "no orchestrator"));
    let mut wrong = dag();
    wrong["nodes"]["c"]["seat"] = json!("orc");
    let text = serde_json::to_string(&wrong).unwrap();
    log.promote(&text);
    assert!(refused(&log.load(&text), "not a thinker seat"));
}

#[test]
fn only_the_orchestrator_routes_and_only_its_own_decision() {
    let mut log = Log::started(&dag());
    decide_at_s(&mut log, "ok");
    // A computed edge, and an edge that is not out of the event's node.
    assert!(log.decide("orc", Action::Route { edge: "e3".into() }).unwrap_err().to_string().contains("guard"));
    assert!(log.decide("orc", Action::Route { edge: "nowhere".into() }).is_err());
    // An outcome outside the node's enum is refused at decide.
    log.route("e1");
    log.cover_orc();
    log.grant_ready();
    let d = log.decide("wb", Action::Report { record: json!({ "outcome": "shipped" }) }).unwrap_err();
    assert!(d.to_string().contains("not in the node's enum"), "{d}");
    // A worker's lease holds no Route (ADR-0037 A5), so the mechanism refuses it before policy.
    assert!(log.decide("wb", Action::Route { edge: "e3".into() }).is_err());
}

// ---- ADR-0055 ------------------------------------------------------------------------------------

/// One turn of the loop from the open event at s: route e1, run w, and let e3 enter s again.
fn turn(log: &mut Log) {
    assert!(matches!(log.route("e1"), Applied::Admitted { .. }), "e1 routes");
    log.cover_orc();
    log.work("ww", "done");
}

#[test]
fn the_loop_turns_twice_and_exits() {
    let mut log = Log::started(&mesh(10));
    decide_at_s(&mut log, "again");
    turn(&mut log);
    decide_at_s(&mut log, "again");
    turn(&mut log);
    decide_at_s(&mut log, "ok");
    assert!(matches!(log.route("e2"), Applied::Admitted { .. }), "e2 exits");
    log.cover_orc();
    log.work("wx", "done");
    assert_eq!(log.acts("s").len(), 3, "s ran three times: the loop turned twice");
    assert_eq!(log.acts("w").len(), 2);
    assert_eq!(log.run().status, RunStatus::Completed);
    // Each activation's causal history runs back to the root, through every turn.
    let x = log.run().acts.iter().position(|a| a.node == "x").unwrap();
    assert_eq!(log.run().acts[x].hist.len(), 6);
    // Nine leases, each charged: three of s, two of w, one of x, three orchestrator rounds.
    assert_eq!(log.run().charged, 9);
}

#[test]
fn the_budget_refuses_a_grant_and_the_workflow_fails() {
    // Four leases: s, its orchestrator round, w, and s again. The next orchestrator round is the fifth.
    let mut log = Log::started(&mesh(4));
    decide_at_s(&mut log, "again");
    turn(&mut log);
    log.work("ws", "again");
    assert_eq!(log.run().charged, 4);
    let a = log.grant_ready();
    assert!(matches!(&a[..], [Applied::WorkflowFailed { reason }] if reason.contains("budget")), "{a:?}");
    assert!(log.run().exhausted);
    // Running out of budget fails the workflow and never completes it (M_BUDGETDONE).
    assert!(failed(&log, "budget"));
    assert_eq!(log.s.live_by_seat.get("orc"), None, "no lease past the budget (M_OVERRUN)");
}

#[test]
fn an_orchestrator_round_is_charged() {
    let mut log = Log::started(&mesh(10));
    log.grant_ready();
    assert_eq!(log.run().charged, 1);
    let fs = log.fence_of("ws");
    log.outcome("ws", "again");
    log.cover(fs);
    log.grant_ready();
    assert!(log.s.live_by_seat.contains_key("orc"));
    assert_eq!(log.run().charged, 2, "the orchestrator's round is charged (M_ORCHFREE)");
    assert_eq!(log.run().charged_node["orchestrator"], 1);
}

#[test]
fn a_finding_against_the_workers_round_voids_the_decision_nodes_next_route() {
    let mut log = Log::started(&mesh(10));
    decide_at_s(&mut log, "again");
    assert!(matches!(log.route("e1"), Applied::Admitted { .. }));
    log.cover_orc();
    let fw = log.work("ww", "done");
    decide_at_s(&mut log, "again");
    // The second s round is clean, and a route out of it is decided.
    let decided = log.decide("orc", Action::Route { edge: "e1".into() }).expect("enabled at decide");
    // A finding against w's round, which is in the second s's causal history, is ordered first.
    assert!(matches!(log.finding(fw), Applied::Admitted { .. }));
    let a = log.apply(decided);
    assert!(refused(&a, "route void (history)"), "{a:?} (M_SOURCEONLY would admit it)");
    assert_eq!(log.acts("w").len(), 1, "no activation after the finding");
    // And none can follow: every edge out of the second s is closed for good.
    assert!(log.decide("orc", Action::Route { edge: "e2".into() }).is_err());
}

#[test]
fn a_route_decided_in_one_round_and_committed_after_it_ends_is_void() {
    let mut log = Log::started(&mesh(10));
    decide_at_s(&mut log, "again");
    // Two routes decided in the first orchestrator round, for the first event.
    let first = log.decide("orc", Action::Route { edge: "e1".into() }).unwrap();
    let stale = log.decide("orc", Action::Route { edge: "e1".into() }).unwrap();
    let Entry::Admit { rec, .. } = &stale else { unreachable!() };
    let round1 = rec.lease;
    assert!(matches!(log.apply(first), Applied::Admitted { .. }));
    log.cover(round1);
    log.work("ww", "done");
    decide_at_s(&mut log, "again");
    let round2 = log.fence_of("orc");
    assert_ne!(round1, round2);
    // The stale route names the first event and the first round. Committed now, it is void and
    // lands on nothing: the second event is still served by the second round (M_TRACKER).
    let a = log.apply(stale);
    assert!(refused(&a, "route void (consumed)"), "{a:?}");
    let ev2 = log.run().acts.iter().rposition(|a| a.node == "s").unwrap();
    assert_eq!(log.run().events[&ev2], EventState::Served { fence: round2 });
    assert_eq!(log.acts("w").len(), 1);
}

#[test]
fn untrusted_content_read_on_the_loop_disables_the_exit() {
    let mut log = Log::started(&mesh(10));
    decide_at_s(&mut log, "again");
    log.route("e1");
    log.cover_orc();
    log.grant_ready();
    // w reads untrusted content in the clear, and reports.
    log.reads("ww", &[UNTRUSTED]);
    let fw = log.fence_of("ww");
    log.outcome("ww", "done");
    log.cover(fw);
    // e3 is clear: the second s starts with w's label in its clearSet (`LabelCoversTruth`).
    log.grant_ready();
    let fs2 = log.fence_of("ws");
    assert!(log.s.leases[&fs2].labels.clear_set.contains(UNTRUSTED));
    log.outcome("ws", "ok");
    log.cover(fs2);
    log.grant_ready();
    // s reports ok, and the exit into the outward x is closed by its label (M_FORGETTAINT).
    let d = log.decide("orc", Action::Route { edge: "e2".into() }).unwrap_err();
    assert!(d.to_string().contains("taint"), "{d}");
    // The loop stays open: taint only accumulates, and the exit stays closed on every later turn.
    turn(&mut log);
    decide_at_s(&mut log, "ok");
    assert!(log.decide("orc", Action::Route { edge: "e2".into() }).unwrap_err().to_string().contains("taint"));
}

#[test]
fn a_mesh_loads_only_with_a_budget_and_two_coloured_clear_edges() {
    let mut log = Log::new();
    let mut unbudgeted = mesh(4);
    unbudgeted.as_object_mut().unwrap().remove("budget");
    let text = serde_json::to_string(&unbudgeted).unwrap();
    log.promote(&text);
    assert!(refused(&log.load(&text), "without a budget"));
    // A clear self-loop cannot be seated with two lineages (ADR-0055 §5).
    let mut selfloop = mesh(4);
    selfloop["edges"]["again"] = json!({ "from": "w", "to": "w", "kind": "computed", "delivery": "clear" });
    let text = serde_json::to_string(&selfloop).unwrap();
    log.promote(&text);
    assert!(refused(&log.load(&text), "joins one lineage on both ends"));
    // The same cycle as a dag does not load either.
    let mut dagged = mesh(4);
    dagged["kind"] = json!("dag");
    dagged.as_object_mut().unwrap().remove("budget");
    let text = serde_json::to_string(&dagged).unwrap();
    log.promote(&text);
    assert!(refused(&log.load(&text), "cycle"));
}
