#!/usr/bin/env python3
"""Run TLC once on a module and print one row. For working on a module; the evidence comes from tlc_rows.py.

    tlc_run.py <Module> <mut> <property> [KEY=value ...]
               [--kind INVARIANT|PROPERTY|DEADLOCK|SIMULATE] [--spec Spec] [--expect VERDICT] [--name N]
               [--rows FILE] [--cfg LINE]... [--workers N|auto] [--trace] [--dir D]

    tlc_run.py Coupling none UnreadBounded                      the property under the mechanism as specified
    tlc_run.py Coupling M_MARK UnreadBounded --expect COUNTEREXAMPLE --trace
    tlc_run.py Coupling none NeverRefused K=2 R=4               a witness, at other constants
    tlc_run.py Coupling_live none AdmitStallEnds --kind PROPERTY --spec SpecA12
    tlc_run.py Draft - TypeOK                                   a module that has no Mut constant yet

It writes the .cfg itself, in a temp directory with a copy of the module chain, so no .cfg is tracked and nothing
is written beside the module. mut is the value of the Mut constant, or - for a module without one. KEY=value sets
a constant (Persons={p1,p2}, no spaces) or one of states=N, depth=D, num=N, seed=S, constraint=Op, as in a row
list. When the module has a row list (<Module>-rows.txt beside it or in rows/, or --rows), its `# const:` and
`# cfg:` lines are the defaults, so a single run uses the constants the results file will.

Prints the row tlc_rows.py would print:

    name | Mut=mut | Spec | property | HOLDS, COUNTEREXAMPLE, DEADLOCK, NO-ERROR-SAMPLED or ERROR | N distinct states

and TLC's own output after it when the verdict is ERROR, is not the one --expect names, or --trace is given (the
counterexample trace is there). Exits 0 when the verdict is the expected one, or, with no --expect, when it is
not ERROR. No results file is written. The jar must be the pinned one unless TLC_UNPINNED=1.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.dont_write_bytecode = True  # leave no __pycache__ in the skill directory
import tla_common as t  # noqa: E402


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("module")
    ap.add_argument("mut")
    ap.add_argument("property")
    ap.add_argument("pairs", nargs="*", metavar="KEY=value")
    ap.add_argument("--kind", default="INVARIANT", choices=t.KINDS)
    ap.add_argument("--spec", default="Spec")
    ap.add_argument("--expect", metavar="VERDICT")
    ap.add_argument("--name")
    ap.add_argument("--rows")
    ap.add_argument("--cfg", action="append", default=[], metavar="LINE")
    ap.add_argument("--workers", default="1")
    ap.add_argument("--trace", action="store_true")
    ap.add_argument("--dir")
    a = ap.parse_args(argv)
    layout = t.Layout(a.dir)
    module = a.module[:-4] if a.module.endswith(".tla") else a.module
    if not os.path.exists(layout.module(module)):
        raise SystemExit(f"no {layout.module(module)} (run from the modules' directory, or pass --dir)")
    meta = {"const": [], "cfg": []}
    rows_file = a.rows
    if not rows_file:
        for cand in (os.path.join(layout.spec, f"{module}-rows.txt"), os.path.join(layout.spec, "rows", f"{module}-rows.txt")):
            if os.path.exists(cand):
                rows_file = cand
                break
    if rows_file:
        meta, _ = t.parse_rows(os.path.abspath(rows_file))
    meta["cfg"] = meta["cfg"] + a.cfg
    exp = a.expect or ("NO-ERROR-SAMPLED" if a.kind == "SIMULATE" else "HOLDS")
    row = t.make_row(a.name or f"{module}-{a.mut}-{a.property}", a.mut, a.spec, a.kind, a.property, exp, a.pairs,
                     where="tlc_run.py")
    checker = t.require_checker(layout)
    verdict, states, ok, out = t.run_row(layout, checker, module, meta, row, workers=a.workers)
    count = t.count_text(row, verdict, states)
    what = row["prop"] if a.kind == "INVARIANT" else f"{a.kind} {row['prop']}"
    extra = "".join(f" {k}={v}" for k, v in row["consts"].items())
    line = f"{row['name']} | Mut={a.mut} | {a.spec}{extra} | {what} | {verdict} | {count}"
    if a.expect or "states" in row["opts"]:
        line += " | as expected" if ok else f" | UNEXPECTED (expected {row['exp']}" + (
            f", states={row['opts']['states']}" if "states" in row["opts"] else "") + ")"
    print(line)
    failed = verdict == "ERROR" or ((a.expect or "states" in row["opts"]) and not ok)
    if failed or a.trace:
        print(out.rstrip())
    if not checker.pinned:
        print(f"(checker is NOT the pin in {checker.pin_label}: sha256 {checker.sha})", file=sys.stderr)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
