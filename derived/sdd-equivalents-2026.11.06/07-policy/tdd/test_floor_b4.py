"""Layer: policy · TDD (pytest) · TOPAK source: floor/genesis-floor.cedar B4; floor/genesis-tests.json.

The floor's behavioural cases as unit tests that drive the real evaluator (`cedar authorize`). The
test is the paper's "tests derived from the spec"; the gates (run-gates.py, floor/lean) are not
expressible here, and the assertion that B4 *discriminates* (some request is denied only because
of it) is the one gate a unit test can approximate, at the end.
"""
import json
import subprocess
from pathlib import Path

import pytest

FLOOR = Path("../../../../floor")
EPOCH, ROUND, RULES = 3, 7, 5


def authorize(principal, action, resource, context, entities):
    out = subprocess.run(
        ["cedar", "authorize", "--policies", FLOOR / "genesis-floor.cedar", "--schema", FLOOR / "genesis.cedarschema",
         "--entities", "/dev/stdin", "--principal", principal, "--action", action, "--resource", resource,
         "--context-json", json.dumps(context), "--verbose"],
        input=json.dumps(entities), capture_output=True, text=True)
    assert out.returncode in (0, 2), out.stderr          # 0 allow, 2 deny; anything else is an error == deny
    return ("Allow" if out.returncode == 0 else "Deny"), out.stdout


def seat(i, domain, kind): return {"uid": {"type": "Topak::Seat", "id": i}, "attrs": {"domain": domain, "kind": kind}, "parents": []}
def topic(i, owner, epoch=EPOCH, rnd=ROUND, sealed=False):
    return {"uid": {"type": "Topak::Topic", "id": i},
            "attrs": {"owner": {"__entity": {"type": "Topak::Seat", "id": owner}}, "epoch": epoch, "round": rnd, "sealed": sealed}, "parents": []}
def ref(t, i): return {"__entity": {"type": "Topak::" + t, "id": i}}
def build_ctx(alphabet):
    return {"lease": {"alphabet": alphabet, "rulesEpoch": RULES}, "epoch": EPOCH, "round": ROUND, "roundRole": "author",
            "corpusRoot": ref("CorpusRoot", "pinned"), "workspace": ref("Workspace", "ws-a1-r7"),
            "toolAllowlist": ref("ToolSet", "build-allow"), "inputsInWorkspace": True}


ENTITIES = [seat("a1", "build", "thinker"), seat("v1", "build", "grant"), seat("r1", "run", "thinker"),
            topic("a1-r7", "a1"), topic("v1-r7", "v1"), topic("a1-r7-sealed", "a1", sealed=True), topic("a1-e2", "a1", epoch=EPOCH - 1),
            topic("r1-r7", "r1"),
            {"uid": {"type": "Topak::CorpusRoot", "id": "pinned"}, "attrs": {}, "parents": []},
            {"uid": {"type": "Topak::Workspace", "id": "ws-a1-r7"}, "attrs": {}, "parents": []},
            {"uid": {"type": "Topak::ToolSet", "id": "build-allow"}, "attrs": {}, "parents": []}]
FULL = ["Read", "Draft", "Invoke", "Emit", "Submit"]


@pytest.mark.parametrize("topic_id, expected", [
    ("a1-r7", "Allow"), ("v1-r7", "Deny"), ("a1-r7-sealed", "Deny"), ("a1-e2", "Deny")])
def test_b4_own_unsealed_current_topic_only(topic_id, expected):
    d, why = authorize('Topak::Seat::"a1"', 'Topak::Action::"Emit"', f'Topak::Topic::"{topic_id}"', build_ctx(FULL), ENTITIES)
    assert d == expected, why
    if expected == "Allow":
        assert "B4-emit-own-topic" in why


def test_b4_needs_emit_in_the_alphabet():
    d, _ = authorize('Topak::Seat::"a1"', 'Topak::Action::"Emit"', 'Topak::Topic::"a1-r7"', build_ctx(["Read", "Draft"]), ENTITIES)
    assert d == "Deny"


def test_b4_is_scoped_to_build():
    d, _ = authorize('Topak::Seat::"r1"', 'Topak::Action::"Emit"', 'Topak::Topic::"r1-r7"', build_ctx(FULL), ENTITIES)
    assert d == "Deny"


def test_b4_discriminates():
    """The one gate a unit test can approximate: with B4 removed, the allowing case is denied, so B4
    is the reason for some decision (ADR-0030 §5 every-entry-matters)."""
    without = (FLOOR / "genesis-floor.cedar").read_text().replace('@id("B4-emit-own-topic")\npermit', '@id("B4-emit-own-topic")\n// removed\n//permit', 1)
    assert "// removed" in without
    (Path("/tmp") / "floor-without-b4.cedar").write_text(without)
    out = subprocess.run(["cedar", "authorize", "--policies", "/tmp/floor-without-b4.cedar", "--schema", FLOOR / "genesis.cedarschema",
                          "--entities", "/dev/stdin", "--principal", 'Topak::Seat::"a1"', "--action", 'Topak::Action::"Emit"',
                          "--resource", 'Topak::Topic::"a1-r7"', "--context-json", json.dumps(build_ctx(FULL))],
                         input=json.dumps(ENTITIES), capture_output=True, text=True)
    assert out.returncode != 0
