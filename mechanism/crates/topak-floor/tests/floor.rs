//! The linked floor against the gate suite and the ADR-0030 hazards.

use std::str::FromStr;

use cedar_policy::EntityUid;
use serde_json::{Value, json};
use topak_core::admit::FloorOutcome;
use topak_floor::*;

/// The linked stage's cases: the genesis suite's 62, lifted to the stage's schema, 12 for `R5` to
/// `R7` and 32 for `C1` to `C9` (`floor/proposed/build.py`).
const TESTS: &str = include_str!("../../../../floor/proposed/control-tests.json");

/// Every behavioral case the `cedar run-tests` gate ran must decide identically through the
/// engine the mechanism links, with the same reasons. This is the differential check between
/// the CLI the gates used and the library the mechanism runs.
///
/// It is also what caught "B6 vote from an unseated principal" voting `grant`, so that forbid B8
/// was the reason for its deny and B6's roster conjunct was never isolated (GAPS-AND-ASSUMPTIONS
/// §4 finding 1). The case now votes `deny`; no divergence is allowed.
#[test]
fn replays_the_gate_suite() {
    let floor = Floor::load().expect("pinned floor loads");
    let cases: Vec<Value> = serde_json::from_str(TESTS).unwrap();
    assert_eq!(cases.len(), 106);
    for c in &cases {
        let name = c["name"].as_str().unwrap();
        let r = &c["request"];
        let uid = |k: &str| EntityUid::from_str(r[k].as_str().unwrap()).unwrap();
        let out = floor.evaluate(uid("principal"), uid("action"), uid("resource"), &r["context"], &c["entities"]);
        let mut want: Vec<String> =
            c["reason"].as_array().unwrap().iter().map(|v| v.as_str().unwrap().to_string()).collect();
        want.sort();
        match (c["decision"].as_str().unwrap(), out) {
            ("allow", FloorOutcome::Permit { mut reasons }) => {
                reasons.sort();
                assert_eq!(reasons, want, "{name}");
            }
            ("deny", FloorOutcome::Deny { mut reasons }) => {
                reasons.sort();
                assert_eq!(reasons, want, "{name}");
            }
            (d, other) => panic!("{name}: expected {d}, got {other:?}"),
        }
    }
}

#[test]
fn exception_count_is_two_under_r6() {
    let floor = Floor::load().unwrap();
    assert_eq!(floor.exception_count(), 2);
    assert!(floor.exception_count() <= topak_core::rules::EXCEPTION_BOUND);
}

#[test]
fn an_edited_floor_does_not_load() {
    let edited = FLOOR_SRC.replace("B1-read-corpus", "B1-read-anything");
    match Floor::load_from(&edited, SCHEMA_SRC, true) {
        Err(FloorLoadError::FloorDigest { .. }) => {}
        Err(e) => panic!("unexpected: {e}"),
        Ok(_) => panic!("an edited floor loaded under the pinned digest"),
    }
}

/// ADR-0030 §9 finding 1, the `M_ERR` hazard: a slice missing `sealed` must not let an emit to
/// a sealed topic through. With S enforced on the slice the input is rejected, and the
/// composition turns that rejection into a deny.
#[test]
fn an_incomplete_slice_is_a_deny_not_a_skipped_forbid() {
    let floor = Floor::load().unwrap();
    let seat = || json!({ "type": "Topak::Seat", "id": "a1" });
    let entities = json!([
        { "uid": seat(), "attrs": { "domain": "build", "kind": "thinker" }, "parents": [] },
        { "uid": { "type": "Topak::Topic", "id": "t" },
          "attrs": { "owner": { "__entity": seat() }, "epoch": 1, "round": 1 }, "parents": [] },
        { "uid": { "type": "Topak::CorpusRoot", "id": "pinned" }, "attrs": {}, "parents": [] },
        { "uid": { "type": "Topak::Workspace", "id": "w" }, "attrs": {}, "parents": [] },
        { "uid": { "type": "Topak::ToolSet", "id": "build-allow" }, "attrs": {}, "parents": [] },
    ]);
    let context = json!({
        "lease": { "alphabet": ["Emit"], "rulesEpoch": 0 }, "epoch": 1, "round": 1, "roundRole": "author",
        "corpusRoot": { "__entity": { "type": "Topak::CorpusRoot", "id": "pinned" } },
        "workspace": { "__entity": { "type": "Topak::Workspace", "id": "w" } },
        "toolAllowlist": { "__entity": { "type": "Topak::ToolSet", "id": "build-allow" } },
        "inputsInWorkspace": true,
    });
    let out = floor.evaluate(
        EntityUid::from_str(r#"Topak::Seat::"a1""#).unwrap(),
        EntityUid::from_str(r#"Topak::Action::"Emit""#).unwrap(),
        EntityUid::from_str(r#"Topak::Topic::"t""#).unwrap(),
        &context,
        &entities,
    );
    assert!(matches!(out, FloorOutcome::Error { .. }), "{out:?}");
    let composed = topak_core::admit::compose(
        &out,
        &topak_core::admit::BundleOutcome::Allow {
            engine: topak_core::state::BundleEngine::LocalWasm,
            bundle: topak_core::Digest("b".into()),
        },
    );
    assert!(matches!(composed, topak_core::admit::Decision::Deny(_)));
}

/// ADR-0040 §1, ADR-0041 §4: the provisional names are retired. A request naming one fails
/// validation against S, and the composition turns any floor error into a deny. This cannot be a
/// `cedar run-tests` case, because the request never reaches evaluation.
#[test]
fn a_retired_run_action_is_an_error_not_a_decision() {
    let floor = Floor::load().unwrap();
    let seat = || json!({ "type": "Topak::Seat", "id": "r1" });
    let root = || json!({ "type": "Topak::CorpusRoot", "id": "run-pinned" });
    let set = |id: &str| json!({ "type": "Topak::ToolSet", "id": id });
    let tool = || json!({ "type": "Topak::Tool", "id": "search@d3" });
    let topic = || json!({ "type": "Topak::Topic", "id": "t" });
    let entities = json!([
        { "uid": seat(), "attrs": { "domain": "run", "kind": "thinker" }, "parents": [] },
        { "uid": root(), "attrs": {}, "parents": [] },
        { "uid": set("run-allow"), "attrs": {}, "parents": [] },
        { "uid": set("bg-tools"), "attrs": {}, "parents": [] },
        { "uid": tool(), "attrs": { "digest": "d3", "outward": true }, "parents": [set("run-allow")] },
        { "uid": topic(),
          "attrs": { "owner": { "__entity": seat() }, "epoch": 1, "round": 1, "sealed": false }, "parents": [] },
    ]);
    let context = |alphabet: Value| {
        json!({
            "lease": { "alphabet": alphabet, "rulesEpoch": 0 }, "epoch": 1, "round": 1,
            "runRoot": { "__entity": root() },
            "toolAllowlist": { "__entity": set("run-allow") },
            "breakGlass": { "quorum": false, "tools": { "__entity": set("bg-tools") } },
            "observerLive": true,
            "clearSet": [], "inputLabels": [], "destLiteral": false, "destLabels": [],
        })
    };
    let ask = |action: &str, resource: &str, alphabet: Value| {
        floor.evaluate(
            EntityUid::from_str(r#"Topak::Seat::"r1""#).unwrap(),
            EntityUid::from_str(&format!(r#"Topak::Action::"{action}""#)).unwrap(),
            EntityUid::from_str(resource).unwrap(),
            &context(alphabet),
            &entities,
        )
    };
    // The same request under the new names is decided, so the error below is the name's.
    let out = ask("Actuate", r#"Topak::Tool::"search@d3""#, json!(["Actuate"]));
    assert!(matches!(out, FloorOutcome::Permit { .. }), "{out:?}");
    let out = ask("Report", r#"Topak::Topic::"t""#, json!(["Report"]));
    assert!(matches!(out, FloorOutcome::Permit { .. }), "{out:?}");
    for (retired, resource) in [("RunInvoke", r#"Topak::Tool::"search@d3""#), ("RunEmit", r#"Topak::Topic::"t""#)] {
        let out = ask(retired, resource, json!([retired]));
        assert!(matches!(out, FloorOutcome::Error { .. }), "{retired}: {out:?}");
        assert!(topak_core::admit::floor_gate(&out).is_some(), "{retired}: any floor error is a deny");
    }
}
