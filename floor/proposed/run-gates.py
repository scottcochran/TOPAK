#!/usr/bin/env python3
"""Run the ADR-0030 §5 floor gates on one stage of the proposed floor.

This drives ../run-gates.py, the genesis gate runner, unchanged: the same gates, the same checked solver
(`../cvc5-checked`, ADR-0030 §5 A1), the same negative and checker controls, pointed at a stage's schema
and floor. It then adds, per stage, routing controls for the entries the stage introduces: a candidate
that drops or weakens a new entry must be classed a relaxation, and one that strengthens it a tightening.

The evidence (every solver query, its proof and the checker's verdict) is left in a temporary directory
and not copied; the results file carries its tree digest.

Requires what ../run-gates.py requires: cedar with `--features analyze`, CVC5, and the ethos checker.
Usage: run-gates.py <labels|control|emergency|workflow> [results-file]
"""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.dirname(HERE)
spec = importlib.util.spec_from_file_location("genesis_gates", os.path.join(GEN, "run-gates.py"))
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)

CONTROL_SIGS = {"Regrant": "Seat", "Renew": "Seat", "AttestGates": "Artifact",
                "EndRound": "Seat", "Revoke": "Seat", "FenceEpoch": "Fleet"}
WORKFLOW_SIGS = {"Route": "Edge"}
STAGES = ("labels", "control", "emergency", "workflow")


def once(text, old, new):
    assert text.count(old) == 1, f"expected exactly one occurrence of: {old[:60]!r}"
    return text.replace(old, new)


def candidates(stage, text):
    """(name, action, candidate floor text, expected class) for the entries this stage and earlier ones add."""
    pols = dict(g.split_policies(text))
    drop = lambda pid: once(text, pols[pid], "")
    c = [
        ("relax: R6 removed", "Actuate", drop("R6-no-steered-destination"), "relaxation"),
        ("relax: R5 reads only what was read in the clear", "Actuate",
         once(text, '  (context.clearSet.contains("restricted") || context.inputLabels.contains("restricted"))\n',
              '  context.clearSet.contains("restricted")\n'), "relaxation"),
        ("tighten: R6 without the untrusted-read condition", "Actuate",
         once(text, '  context.clearSet.contains("untrusted") &&\n  context.destLiteral\n', '  context.destLiteral\n'), "tightening"),
        ("relax: R7 removed", "Actuate", drop("R7-no-replayed-destination"), "relaxation"),
    ]
    if stage in ("control", "emergency", "workflow"):
        c += [
            ("relax: C5 without the peer condition", "Regrant",
             once(text, "when { !context.hasLease || !context.peerLive };", "when { !context.hasLease };"), "relaxation"),
            ("relax: C7 removed, a lapsed operator may fence", "FenceEpoch", drop("C7-fence-needs-lease"), "relaxation"),
            ("tighten: C4 needs a live lease", "Revoke",
             once(text, "  (context.hasLease || context.freshAssertion)\n", "  context.hasLease\n"), "tightening"),
            ("relax: C1 without the alphabet comparison", "Regrant",
             once(text, "  context.nextRound &&\n  context.lastAlphabet.containsAll(context.newAlphabet)\n", "  context.nextRound\n"), "relaxation"),
            ("relax: C8 removed, an unlabelled task", "Regrant", drop("C8-task-label-in-bounds"), "relaxation"),
        ]
    if stage in ("emergency", "workflow"):
        b10 = ('when {\n  principal.kind != "thinker" &&\n'
               '  !(principal.kind == "emergency" && action == Topak::Action::"Actuate")\n};')
        c += [
            ("tighten: B10 as at genesis, no emergency seat", "Actuate",
             once(text, b10, 'when { principal.kind != "thinker" };'), "tightening"),
            ("relax: B10 admits every kind for Actuate", "Actuate",
             once(text, b10, 'when { principal.kind != "thinker" && action != Topak::Action::"Actuate" };'), "relaxation"),
        ]
    if stage == "workflow":
        r3 = 'when { (principal.kind == "thinker" || principal.kind == "orchestrator") && !context.observerLive };'
        c += [
            ("relax: R9 removed, any seat with Route may route", "Route", drop("R9-only-orchestrators-route"), "relaxation"),
            ("relax: R8 without the decision-point condition", "Route",
             once(text, "  resource.chosen &&\n  context.decisionPoint.contains(resource.source)\n",
                  "  resource.chosen\n"), "relaxation"),
            ("relax: R8 admits a computed edge", "Route",
             once(text, "  resource.chosen &&\n  context.decisionPoint", "  context.decisionPoint"), "relaxation"),
            ("relax: R3 couples Thinkers only, as before", "Route",
             once(text, r3, 'when { principal.kind == "thinker" && !context.observerLive };'), "relaxation"),
            ("tighten: no Route after reading untrusted", "Route",
             text + '\n@id("T-no-route-untrusted")\nforbid (principal, action == Topak::Action::"Route", resource)\n'
                    'when { context.clearSet.contains("untrusted") };\n', "tightening"),
            ("equivalent: the kind test moved into R8", "Route",
             once(text, '  principal.domain == "run" &&\n  context.lease.alphabet.contains("Route") &&',
                  '  principal.domain == "run" &&\n  principal.kind == "orchestrator" &&\n  context.lease.alphabet.contains("Route") &&'),
             "equivalent"),
        ]
    return c


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in STAGES:
        sys.exit(__doc__)
    stage = sys.argv[1]
    results = sys.argv[2] if len(sys.argv) > 2 else None
    g.SCHEMA = os.path.join(HERE, f"{stage}.cedarschema")
    g.FLOOR = os.path.join(HERE, f"{stage}-floor.cedar")
    if stage in ("control", "emergency", "workflow"):
        g.SIGS.update(CONTROL_SIGS)
    if stage == "workflow":
        g.SIGS.update(WORKFLOW_SIGS)
    g.out(f"TOPAK — PROPOSED policy floor, stage `{stage}`: the genesis gates (below), then routing controls for the new entries")
    g.out("Built by floor/proposed/build.py from the genesis floor. Not ratified, and not what the reference follows.")
    g.out()
    argv, sys.argv = sys.argv, sys.argv[:1]          # the genesis runner writes nothing and leaves its evidence in place
    failures = g.main()
    sys.argv = argv
    # Drop the genesis runner's own closing section: it names a temporary path, and this run is not over.
    cut = next((i for i, l in enumerate(g.LOG) if l.lstrip("\n").startswith("=== evidence: every solver query")), len(g.LOG))
    del g.LOG[cut:]
    base_failed = failures != 0

    text = open(g.FLOOR).read()
    g.out(f"\n=== routing, new entries: a weakened entry is a relaxation, a strengthened one a tightening")
    extra = 0
    for n, (name, a, ctext, expect) in enumerate(candidates(stage, text)):
        cf = g.write(f"new-cand-{n}.cedar", ctext)
        new_old, _ = g.symcc(a, "implies", "--policies1", cf, "--policies2", g.FLOOR)
        old_new, _ = g.symcc(a, "implies", "--policies1", g.FLOOR, "--policies2", cf)
        h = lambda v: "holds" if v in ("holds✓", "holds°") else v
        cls = {("holds", "holds"): "equivalent", ("holds", "refuted"): "tightening",
               ("refuted", "holds"): "relaxation", ("refuted", "refuted"): "incomparable"}.get((h(new_old), h(old_new)), "ERROR")
        route = "ordinary promotion" if cls in ("equivalent", "tightening") else "anchor issuance + promotion"
        ok = cls == expect
        extra += not ok
        g.out(f"  {name:50} F'=>F {new_old:8} F=>F' {old_new:8} -> {cls:12} -> {route:28} {'pass' if ok else 'FAIL'}")
    bad = g.unchecked_holds()
    extra += bad
    g.out(f"  {'holds without a checked proof, whole run':50} {bad:8} -> {'none' if bad == 0 else 'FAIL'}")

    g.out(f"\n=== evidence, whole run")
    g.out(f"  {g.STATS['calls']} cedar calls · {g.STATS['queries']} solver queries · {g.STATS['checked']} unsat with a checked proof · "
          f"{g.STATS['sat']} sat (counterexample) · {g.STATS['unknown']} unknown/unchecked (the three checker controls)")
    g.out(f"  evidence tree sha256 {g.tree_digest(g.CALLS)} · not copied; a rerun reproduces it")
    ok = not base_failed and extra == 0
    g.out(f"\nRESULT: {'all gates pass' if ok else 'FAILURES: genesis gates ' + ('failed' if base_failed else 'pass') + f', new-entry controls {extra} failure(s)'}")
    if results:
        with open(results, "w") as f:
            f.write("\n".join(g.LOG) + "\n")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
