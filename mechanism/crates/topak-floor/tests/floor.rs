//! The linked floor against the gate suite and the ADR-0030 hazards.

use std::str::FromStr;

use cedar_policy::EntityUid;
use serde_json::{Value, json};
use topak_core::admit::FloorOutcome;
use topak_floor::*;

const TESTS: &str = include_str!("../../../../floor/genesis-tests.json");

/// Cases whose recorded `reason` differs from what the engine reports, with the reason the
/// engine gives. The decision still matches.
///
/// "B6 vote from an unseated principal" votes `grant`, so forbid B8 fires and is the reason
/// for the deny. The case therefore does not exercise B6's roster conjunct on its own; a `deny`
/// vote from the unseated seat would. Finding against `floor/gen-tests.py`, not fixed here.
const KNOWN_REASON_DIVERGENCE: &[(&str, &[&str])] =
    &[("B6 vote from an unseated principal", &["B8-grant-only-from-grant-seat"])];

/// Every behavioral case the `cedar run-tests` gate ran must decide identically through the
/// engine the mechanism links, with the same reasons. This is the differential check between
/// the CLI the gates used and the library the mechanism runs.
#[test]
fn replays_the_gate_suite() {
    let floor = Floor::load().expect("pinned floor loads");
    let cases: Vec<Value> = serde_json::from_str(TESTS).unwrap();
    assert_eq!(cases.len(), 38);
    for c in &cases {
        let name = c["name"].as_str().unwrap();
        let r = &c["request"];
        let uid = |k: &str| EntityUid::from_str(r[k].as_str().unwrap()).unwrap();
        let out = floor.evaluate(uid("principal"), uid("action"), uid("resource"), &r["context"], &c["entities"]);
        let mut want: Vec<String> = match KNOWN_REASON_DIVERGENCE.iter().find(|(n, _)| *n == name) {
            Some((_, r)) => r.iter().map(|s| s.to_string()).collect(),
            None => c["reason"].as_array().unwrap().iter().map(|v| v.as_str().unwrap().to_string()).collect(),
        };
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
        { "uid": seat(), "attrs": { "domain": "build" }, "parents": [] },
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
