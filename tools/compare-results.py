#!/usr/bin/env python3
"""Compare a freshly generated TLC results file with the committed one it should reproduce.

  tools/compare-results.py <committed> <fresh>

Compared:
  - the Module line (the module's digest and those of the modules it extends, TLC's version and the jar's digest),
    without the Java version, which differs between machines;
  - the Runner line (generator, rows file and their digests, constants) and, where there is one, the expected line;
  - every row: its heading (name, Mut, constants, specification, property), its verdict, and its distinct-state
    count. The verdict is TLC's first line after the heading ("Model checking completed. ..." or the first
    "Error: ..."), and live-gen-results.sh's "→ ..." line where there is one. The state count is compared when the
    row ran to completion, or when the Runner line says TLC ran with one worker: a violation found by several
    workers is found after a number of states that varies from run to run;
  - the summary line ("Rows: ..."), where there is one.
Not compared: the title line, which the regeneration copies; timestamps and timings; fingerprint-collision
estimates; counterexample traces.

Exit 0 when they agree; 1 with every difference listed otherwise. A difference means either the committed file is
stale (regenerate it as a new dated file) or the checker behaves differently on this machine (investigate).
Adapted from f1-tla's tools/compare-results.py (Apache-2.0) for TOPAK's generators; ADR-0069 §10.2 (Proposed).
"""
import re
import sys


def parse(path):
    lines = open(path, encoding="utf-8").read().splitlines()
    if len(lines) < 3 or not lines[1].startswith("Module:"):
        raise SystemExit(f"{path}: not a results file")
    head = {"module": " · ".join(s for s in lines[1].split(" · ") if " version " not in s),
            "runner": lines[2]}
    if len(lines) > 3 and lines[3].startswith("expected"):
        head["expected"] = lines[3]
    one_worker = "-workers 1" in lines[2]
    rows, cur, summary = {}, None, None
    for ln in lines[3:]:
        if ln.startswith("=== "):
            name = ln[4:].split(" · ", 1)[0]
            cur = rows.setdefault(name, {"heading": ln, "tlc": None, "verdict": None, "states": None,
                                         "complete": False})
        elif cur is None:
            continue
        elif cur["tlc"] is None and (ln.startswith("Model checking completed") or ln.startswith("Error:")):
            cur["tlc"] = ln
            cur["complete"] = ln.startswith("Model checking completed")
        elif ln.startswith("→ "):
            cur["verdict"] = ln
        elif m := re.search(r"(\d+) distinct states found", ln):
            cur["states"] = m.group(1)
        elif ln.startswith("Rows: "):
            summary = ln
    for r in rows.values():
        if not (r["complete"] or one_worker):
            r["states"] = None
    return head, rows, summary


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        return 2
    (h1, r1, s1), (h2, r2, s2) = parse(sys.argv[1]), parse(sys.argv[2])
    diffs = []
    for k in sorted(set(h1) | set(h2)):
        if h1.get(k) != h2.get(k):
            diffs.append(f"{k} line differs:\n  committed: {h1.get(k)}\n  fresh:     {h2.get(k)}")
    for name in sorted(set(r1) | set(r2)):
        a, b = r1.get(name), r2.get(name)
        if a is None or b is None:
            diffs.append(f"row {name}: only in {'fresh' if a is None else 'committed'}")
            continue
        for k in ("heading", "tlc", "verdict", "states"):
            if a[k] != b[k] and not (k == "states" and None in (a[k], b[k])):
                diffs.append(f"row {name}: {k} differs:\n  committed: {a[k]}\n  fresh:     {b[k]}")
    if s1 != s2:
        diffs.append(f"summary differs:\n  committed: {s1}\n  fresh:     {s2}")
    for d in diffs:
        print(d)
    print(f"{sys.argv[1]}: {len(r1)} rows compared, {len(diffs)} differences")
    return 1 if diffs else 0


if __name__ == "__main__":
    sys.exit(main())
