#!/usr/bin/env python3
"""ADR-0023 §2's inventory, computed from `theorem-premise-binding.md` instead of listed by hand
(feature item 5; ADR-0045 §3).

Usage: inventory.py <declaration.json> [binding.md|binding.json] [ADR-0045.md]
       inventory.py --check [binding.json] [binding.md] [ADR-0045.md]

The declaration names the deployment's confinement rung and its trusted-base rows, each with its
class (ADR-0045 §1): `{"rung": 3, "rows": {"T-0045-16": "trust root", ...}}`. A row the declaration
does not name is undeclared, and an `excluded` row is excluded; either makes a premise false
(ADR-0045 §3, rule 1).

What this computes is the row half of each theorem: the BASE rows plus the `T-0045-n` its "Row
premises" cell names, where a segment that begins "at rung N", or a row followed by "(N)" or
"at N", counts only at rung N, and "T-0045-a to b" is a range. A row whose Rungs column in
ADR-0045 Annex A excludes the declared rung is not required at it. A theorem with every such row declared and not
excluded prints `rows hold`; otherwise `void` with the rows that fail. The parameter and gap
premises are prose, and are printed beside the verdict for a reader to judge: this script does not
decide them, and a `rows hold` line is not a `holds`.

Given `theorem-premise-binding.json` in place of the table, it evaluates the whole binding as a Boolean
matrix (`derived/topak-rung-DAG-as-matrix-2026.10.03.md`): every parameter, condition and gap premise
is a column, and the declaration gives each one a value under `"premises"`, `{"coupling-on": true, ...}`.
A premise marked `derived` is computed from the declared rung; any other premise the declaration does not
set true is false (ADR-0045 §3, rule 1). A theorem prints `holds` when every premise in its row holds at
the declared rung, otherwise `void` with the premises that fail. The verdict is only as good as the
declaration: a premise declared true is not thereby verified.

`--check` compares the JSON's row premises with the table's at every rung, and fails on any difference:
the table is canonical for its rows, and the JSON adds the other columns.
"""
import json
import re
import sys

BASE = ["T-0045-1", "T-0045-11", "T-0045-28", "T-0045-29", "T-0045-30"]
ROW = re.compile(r"T-0045-(\d+)(?:\s+to\s+(\d+))?(?:\s*\((\d)\)|\s+at\s+(\d)\b)?")


def strip_struck(s):
    return re.sub(r"~~.*?~~", "", s)


def annex_rungs(path):
    """ADR-0045 Annex A: the rungs each row applies at. "all", or "confinement N" / "N–M"."""
    out = {}
    for line in open(path):
        m = re.match(r"\| \*\*(T-0045-\d+)\*\* \|", line)
        if not m:
            continue
        cells = [c.strip() for c in line.strip().strip("|").split(" | ")]
        r = re.search(r"confinement (\d)(?:\s*[–-]\s*(\d))?", cells[4]) if len(cells) > 4 else None
        out[m.group(1)] = set(range(int(r.group(1)), int(r.group(2) or r.group(1)) + 1)) if r else set(range(4))
    return out


def rows_in(cell, rung, applies):
    """The T-rows a premise cell requires at this rung."""
    out = []
    for seg in strip_struck(cell).split(";"):
        m = re.match(r"\s*at rung (\d)", seg)
        if m and int(m.group(1)) != rung:
            continue
        for a, b, paren, at in ROW.findall(seg):
            only = paren or at
            if only and int(only) != rung:
                continue
            for n in range(int(a), int(b or a) + 1):
                row = f"T-0045-{n}"
                if rung in applies.get(row, set(range(4))):
                    out.append(row)
    return out


def table(path):
    rows = []
    for line in open(path):
        if not line.startswith("| ") or line.startswith("| Theorem") or line.startswith("|---"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split(" | ")]
        if len(cells) == 7:
            rows.append(cells)
    return rows


HOLDS = ("trust root", "delegated")


def matrix_rows(theorem, rung):
    """One row of the matrix at a rung: the T-rows, then the other premise columns."""
    return theorem["rows"] + theorem.get("rows_at_rung", {}).get(str(rung), []), theorem["premises"]


def derived_value(rule, rung):
    m = re.fullmatch(r"rung\s*(>=|==)\s*(\d)", rule)
    if not m:
        sys.exit(f"inventory.py: unknown derived premise rule {rule!r}")
    return rung >= int(m.group(2)) if m.group(1) == ">=" else rung == int(m.group(2))


def evaluate(decl, path):
    """holds = NOT(B · NOT d), row by row."""
    binding = json.load(open(path))
    rung, declared, values = decl["rung"], decl.get("rows", {}), decl.get("premises", {})
    unknown = sorted(set(values) - set(binding["premises"]))
    if unknown:
        sys.exit("inventory.py: the declaration sets premises the binding does not have: " + ", ".join(unknown))
    d = {p: derived_value(spec["derived"], rung) if "derived" in spec else values.get(p) is True
         for p, spec in binding["premises"].items()}
    print(f"Inventory for rung {rung}, {len(declared)} rows and {sum(d.values())} of {len(d)} other premises "
          f"true · from {path}")
    held = 0
    for t in binding["theorems"]:
        rows, premises = matrix_rows(t, rung)
        bad = [f"{r} {declared.get(r, 'undeclared')}" for r in dict.fromkeys(binding["base"] + rows)
               if declared.get(r, "undeclared") not in binding.get("row_holds_when", HOLDS)]
        bad += [p for p in premises if not d[p]]
        held += not bad
        print(f"- {', '.join(t['names'])}: " + ("holds" if not bad else "void: " + ", ".join(bad)))
    print(f"{held} of {len(binding['theorems'])} rows hold")


def check(path, table_path, annex_path):
    binding = json.load(open(path))
    rows, applies = table(table_path), annex_rungs(annex_path)
    errors = []
    if len(rows) != len(binding["theorems"]):
        errors.append(f"{len(rows)} rows in the table, {len(binding['theorems'])} in the JSON")
    for cells, t in zip(rows, binding["theorems"]):
        if not all(n in cells[0] for n in t["names"]):
            errors.append(f"{t['names']} not in the table's row {cells[0]!r}")
        for rung in range(4):
            want = set(rows_in(cells[4], rung, applies))
            got = set(matrix_rows(t, rung)[0])
            if want != got:
                errors.append(f"{', '.join(t['names'])} at rung {rung}: table {sorted(want)}, JSON {sorted(got)}")
        for p in t["premises"]:
            if p not in binding["premises"]:
                errors.append(f"{', '.join(t['names'])}: premise {p} has no column")
    for e in errors:
        print("MISMATCH", e)
    print(f"{len(binding['theorems'])} rows, {len(binding['premises'])} non-row premises: "
          + ("JSON and table agree at every rung" if not errors else f"{len(errors)} mismatches"))
    return not errors


def main():
    here = __file__.rsplit("/", 1)[0]
    if sys.argv[1] == "--check":
        args = sys.argv[2:] + [None] * 3
        sys.exit(0 if check(args[0] or here + "/theorem-premise-binding.json",
                            args[1] or here + "/theorem-premise-binding.md",
                            args[2] or here + "/../decisions/ADR-0045.md") else 1)
    decl = json.load(open(sys.argv[1]))
    binding = sys.argv[2] if len(sys.argv) > 2 else here + "/theorem-premise-binding.md"
    if binding.endswith(".json"):
        return evaluate(decl, binding)
    applies = annex_rungs(sys.argv[3] if len(sys.argv) > 3 else here + "/../decisions/ADR-0045.md")
    rung = decl["rung"]
    declared = decl.get("rows", {})
    print(f"Inventory for rung {rung}, {len(declared)} rows declared · from {binding}")
    for theorem, _checked, _record, _breaks, premises, params, _ref in table(binding):
        need = BASE + rows_in(premises, rung, applies)
        bad = [r for r in dict.fromkeys(need) if declared.get(r, "undeclared") not in HOLDS]
        verdict = "rows hold" if not bad else "void: " + ", ".join(f"{r} {declared.get(r, 'undeclared')}" for r in bad)
        print(f"- {theorem}: {verdict}")
        if params not in ("—", ""):
            print(f"    to judge: {strip_struck(params)}")


if __name__ == "__main__":
    main()
