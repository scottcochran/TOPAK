"""Layer: runtime · TDD · TOPAK source: trace.rs, trace2tla.py, Mechanism.tla; spec/Mechanism-trace-results-2026.10.05.txt.

The TDD-framework counterpart of trace validation: a pytest that loads every recorded JSONL trace
and replays it, step by step, through the Python model of the state machine (05-model), asserting
the same result kind and the same projected state after every entry. This is `TraceMatches` with
pytest as the checker and the Python model standing in for `Mechanism.tla`. Edge type to the model:
*replayed* (what it leaves: the paths no trace reached). Run: TOPAK_TRACE_DIR=/tmp/t pytest test_replay.py
"""
import json
import os
from pathlib import Path

import pytest

from model.mechanism import Mechanism      # the Python port of Mechanism.tla's step relation

TRACES = sorted(Path(os.environ.get("TOPAK_TRACE_DIR", "/tmp/t")).glob("*.jsonl"))


def decode(v):
    """trace.rs encoding: {"$f": [[k, v]...]} a function, {"$s": [...]} a set, an array a tuple."""
    if isinstance(v, dict):
        if "$f" in v: return {decode(k) if not isinstance(k, (list, dict)) else json.dumps(k): decode(x) for k, x in v["$f"]}
        if "$s" in v: return frozenset(json.dumps(decode(x), sort_keys=True) for x in v["$s"])
        return {k: decode(x) for k, x in v.items()}
    if isinstance(v, list): return tuple(decode(x) for x in v)
    return v


@pytest.mark.parametrize("trace", TRACES, ids=lambda p: p.stem)
def test_trace_matches(trace):
    lines = [json.loads(l) for l in trace.read_text().splitlines() if l.strip()]
    assert "init" in lines[0], "first line must be the init projection"
    m = Mechanism.from_projection(decode(lines[0]["init"]))
    for step in lines[1:]:
        entry, oracle = decode(step["entry"]), decode(step.get("oracle", {}))
        applied = m.step(step["index"], entry, oracle)             # the model's step relation
        assert applied.kind == decode(step["applied"])["kind"], f"{trace.stem} step {step['index']}: result differs"
        assert m.projection() == decode(step["state"]), f"{trace.stem} step {step['index']}: state differs"
        assert m.confinement_invariants(), f"{trace.stem} step {step['index']}: a confinement invariant broken"


def test_every_suite_was_traced():
    """The results file's coverage line, as a test: the tests the trace run expects to see."""
    suites = {"mut", "conf", "contain", "e2e", "ops", "emg"}
    assert suites <= {p.stem.split("_")[0] for p in TRACES}, "a suite recorded no trace"
