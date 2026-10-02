#!/usr/bin/env python3
"""ADR-0023 §2's inventory, computed from `theorem-premise-binding.md` instead of listed by hand
(feature item 5; ADR-0045 §3).

Usage: inventory.py <declaration.json> [binding.md] [ADR-0045.md]

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


def main():
    decl = json.load(open(sys.argv[1]))
    here = __file__.rsplit("/", 1)[0]
    binding = sys.argv[2] if len(sys.argv) > 2 else here + "/theorem-premise-binding.md"
    applies = annex_rungs(sys.argv[3] if len(sys.argv) > 3 else here + "/../decisions/ADR-0045.md")
    rung = decl["rung"]
    declared = decl.get("rows", {})
    print(f"Inventory for rung {rung}, {len(declared)} rows declared · from {binding}")
    for theorem, _checked, _record, _breaks, premises, params, _ref in table(binding):
        need = BASE + rows_in(premises, rung, applies)
        bad = [r for r in dict.fromkeys(need) if declared.get(r, "undeclared") in ("undeclared", "excluded")]
        verdict = "rows hold" if not bad else "void: " + ", ".join(f"{r} {declared.get(r, 'undeclared')}" for r in bad)
        print(f"- {theorem}: {verdict}")
        if params not in ("—", ""):
            print(f"    to judge: {strip_struck(params)}")


if __name__ == "__main__":
    main()
