"""Layer: assurance · TDD (pytest) · TOPAK source: spec/theorem-premise-binding.md, spec/inventory.py, ADR-0023 §2.

pytest can carry premises as markers and compute the inventory at collection: a test marked with
rows a deployment's declaration does not hold is not run and not failed, it is reported `void`.
That reproduces ADR-0023 §2's "theorems minus those whose premises are lost" as a test outcome.
The binding is the markers; the declaration is a YAML file the deployment ships (10-deployment).

What it cannot do: grade. A skipped test and a passed test are the two outcomes; there is no
"holds at *tested*" beside "holds at *proved*". The `grade` marker below is a label, not a threshold.
"""
import pytest
import yaml

ROWS = {"T-0045-1", "T-0045-11", "T-0045-28", "T-0045-29", "T-0045-30"}   # BASE


def pytest_addoption(parser):
    parser.addoption("--declaration", default="declaration.yaml",
                     help="the deployment's trusted-base declaration (ADR-0045 §4)")
    parser.addoption("--min-grade", default="trusted",
                     help="run only tests whose edge grade is at least this (ADR-0057 §5); a label here, not a computation")


GRADES = ["executed", "generated", "proved", "proved-of-a-reading", "replayed", "tested", "read", "trusted"]


def pytest_configure(config):
    config.addinivalue_line("markers", "premise(row): a trusted-base row or derived premise the test rests on")
    config.addinivalue_line("markers", "theorem(name): the binding-table row this test restates")
    config.addinivalue_line("markers", "grade(type): the ADR-0057 §3 edge type of this test's edge to the module")
    with open(config.getoption("--declaration")) as f:
        decl = yaml.safe_load(f)
    config.declared = {r["id"] for r in decl["rows"] if r["status"] in ("delegated", "trust root")}
    config.derived = {d["name"]: d["routes"] for d in decl.get("derived", [])}


def holds(config, premise):
    if premise == "BASE":
        return all(holds(config, r) for r in ROWS)
    if premise in config.derived:                                   # ADR-0053 R7: OR of ANDed routes
        return any(all(holds(config, p) for p in route) for route in config.derived[premise])
    return premise in config.declared


def pytest_collection_modifyitems(config, items):
    threshold = GRADES.index(config.getoption("--min-grade"))
    for item in items:
        lost = [m.args[0] for m in item.iter_markers("premise") if not holds(config, m.args[0])]
        if lost:
            item.add_marker(pytest.mark.skip(reason=f"void: premise {', '.join(lost)} not declared (ADR-0023 §2)"))
        g = next((m.args[0] for m in item.iter_markers("grade")), "trusted")
        if GRADES.index(g) > threshold:
            item.add_marker(pytest.mark.skip(reason=f"below grade {config.getoption('--min-grade')}: this edge is {g}"))
