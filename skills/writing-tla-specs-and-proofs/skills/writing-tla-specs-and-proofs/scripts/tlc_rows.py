#!/usr/bin/env python3
"""Run a module's TLC row list and write its dated results file.

    tlc_rows.py <Module>-rows.txt [-j N] [--only a,b] [--dry-run] [--date YYYY.MM.DD] [--dir D] [--results-dir R]

The row list is the only input. Its header comments give the module, a title, the prose expectation, the default
constants and any extra .cfg lines; each row names one TLC run and the verdict it must give:

    # module: Coupling
    # title: Coupling.tla - the coupling of a Thinker to its Observer
    # expected: Mut = "none" HOLDS on every property; each mutation is COUNTEREXAMPLE on the property it must break ...
    # const: K = 1
    # cfg: CONSTRAINT Bound
    name  mut  spec  kind  property  expected  [KEY=value ...]

mut is the value of the module's Mut constant, or - for a module that has none. kind is INVARIANT, PROPERTY (a
temporal or action property), DEADLOCK (the property as an invariant with TLC's deadlock check on) or SIMULATE
(the property as an invariant, random behaviours). expected is HOLDS, COUNTEREXAMPLE, DEADLOCK (DEADLOCK rows
only) or NO-ERROR-SAMPLED (SIMULATE rows only); VIOLATED is read as COUNTEREXAMPLE, or as DEADLOCK on a DEADLOCK
row. KEY=value overrides a constant (Persons={p1,p2}, no spaces), or sets states=N (assert the exact
distinct-state count), depth=D, num=N, seed=S (SIMULATE rows), or constraint=Op (add CONSTRAINT Op for this row).

Every row runs with -workers 1 so a counterexample row's state count is reproducible; PROPERTY rows add -fp 0 for
the same reason; every row but a DEADLOCK row passes -deadlock (DEADLOCK rows exist to audit that flag). One count
is not reproducible and is not printed: TLC checks temporal properties at intervals of the clock, so the number
of states it has when it finds a liveness counterexample differs with the machine and its load, and so does
whether the search ended first. A violated PROPERTY row says "count not recorded". Each row runs on a copy of the
module chain in a temp directory, so nothing is written beside the module.

The results file names the checker, this script and every local module in the EXTENDS chain by sha256, prints
the rows, and is written as <results>/<Module>-results-<date>.txt. It is never overwritten: a rerun that
reproduces it byte for byte says so, a rerun that differs is written beside it with a letter suffix, and a run
with any row not as expected writes nothing. --date regenerates under an earlier date, to show that a cited file
still reproduces. Exits non-zero if the list has no rows, if any row is ERROR or not as expected, or if the jar
is not the pinned one (unless TLC_UNPINNED=1). --only and --dry-run run rows without writing a results file.

tla_common.py says where the modules, the jar, the pin and the results directory are looked for.
"""
import argparse
import concurrent.futures as cf
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.dont_write_bytecode = True  # leave no __pycache__ in the skill directory
import tla_common as t  # noqa: E402


def spec_dir_for(module, rows_path, given):
    """The directory holding <module>.tla: --dir or $TLA_SPEC_DIR, else the current directory, the row list's, or its parent."""
    if given or os.environ.get("TLA_SPEC_DIR"):
        return given
    here = os.path.dirname(rows_path)
    for d in (os.getcwd(), here, os.path.dirname(here)):
        if os.path.exists(os.path.join(d, module + ".tla")):
            return d
    raise SystemExit(f"{module}.tla is not in the current directory, beside {rows_path}, or one level up; pass --dir")


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("rows")
    ap.add_argument("-j", type=int, default=1, metavar="N", help="rows to run at once")
    ap.add_argument("--only", metavar="a,b", help="run only these rows; no results file")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--date", default=t.today())
    ap.add_argument("--dir")
    ap.add_argument("--results-dir")
    a = ap.parse_args(argv)
    rows_path = os.path.abspath(a.rows)
    meta, rows = t.parse_rows(rows_path)
    module = meta["module"][0].strip()
    layout = t.Layout(spec_dir_for(module, rows_path, a.dir), a.results_dir)
    if not os.path.exists(layout.module(module)):
        raise SystemExit(f"no {layout.module(module)}")
    dry = a.dry_run
    if a.only:
        only = set(a.only.split(","))
        missing = only - {r["name"] for r in rows}
        if missing:
            raise SystemExit(f"--only: no row named {', '.join(sorted(missing))}")
        rows = [r for r in rows if r["name"] in only]
        dry = True
    if not rows:
        print("no rows to run: a row list with no rows is not a green file", file=sys.stderr)
        return 1
    checker = t.require_checker(layout)

    # Read what the results file will describe before TLC runs, so an edit made during the run cannot make the
    # file describe text that was not checked.
    chain = t.module_chain(module, layout.spec)
    digests = [(m, t.sha256(layout.module(m))) for m in chain]
    rows_sha = t.sha256(rows_path)

    results = [None] * len(rows)
    with cf.ThreadPoolExecutor(max_workers=max(1, a.j)) as ex:
        futs = {ex.submit(t.run_row, layout, checker, module, meta, r): i for i, r in enumerate(rows)}
        for fut in cf.as_completed(futs):
            i = futs[fut]
            verdict, states, ok, out = fut.result()
            results[i] = (verdict, states, ok)
            print(t.format_row(rows[i], verdict, states, ok), flush=True)
            if verdict == "ERROR" or not ok:
                print("\n".join(out.rstrip().splitlines()[-30:]), file=sys.stderr)

    if any(t.sha256(layout.module(m)) != d for m, d in digests) or t.sha256(rows_path) != rows_sha:
        print(f"\n{module}.tla, a module it extends or the row list changed during the run; no results file written.")
        return 1
    bad = [r["name"] for r, (v, s, ok) in zip(rows, results) if not ok]
    errors = [r["name"] for r, (v, s, ok) in zip(rows, results) if v == "ERROR"]
    pin = checker.pin
    ident = " ".join(x for x in (pin.get("version"), pin.get("tlc") and f"({pin['tlc']})") if x) if checker.pinned else ""
    lines = [
        f"{layout.project} - {' '.join(meta['title']) or module + '.tla'}",
        f"TLC results {a.date}, generated by tlc_rows.py from {layout.rel(rows_path)}; never edited",
        f"Checker: tla2tools.jar {ident + ' ' if ident else ''}sha256 {checker.sha} "
        + (f"(pinned by {checker.pin_label})" if checker.pinned else f"(NOT the pin in {checker.pin_label})"),
        "Modules: " + " ".join(f"{layout.rel(layout.module(m))} {d}" for m, d in digests),
        f"Rows: {layout.rel(rows_path)} sha256 {rows_sha}",
        t.runner_line(os.path.abspath(__file__)),
        "Constants: " + ("; ".join(f"{k} = {v}" for k, v in t.default_consts(meta)) or "none by default")
        + " (Mut and any KEY=value on a row override these)",
    ]
    lines += [f"Config: {c}" for c in meta["cfg"]]
    lines += [f"Expected: {' '.join(meta['expected']) or 'as each row states'}",
              "Flags: -workers 1; -deadlock on every row but a DEADLOCK row; -fp 0 on PROPERTY rows",
              "Words: HOLDS and COUNTEREXAMPLE are checked results at these constants (every reachable state);"
              " NO-ERROR-SAMPLED is a sample, never a check; none of them is a proof",
              ""]
    lines += [t.format_row(r, *res) for r, res in zip(rows, results)]
    lines += ["", f"{len(rows)} rows: {len(rows) - len(bad)} as expected, {len(bad)} not"
              + (f" ({', '.join(bad)})" if bad else "") + f", {len(errors)} ERROR"]
    if dry or bad:
        print("\n(no results file written: " + ("dry run" if dry else "rows not as expected") + ")")
    else:
        print("\n" + t.write_results(layout, f"{module}-results", a.date, "\n".join(lines) + "\n"))
    print(lines[-1])
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
