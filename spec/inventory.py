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

**Derived premises** (ADR-0053 §5, R7, Proposed). A binding may define premises as alternatives: under `"derived"`,
`{"invariant(Seats)": {"any_of": [["T-0045-31"], ["T-0045-37", "enc-faithful(Seats)"]]}}` holds when every atom of
some route holds, an atom being a row, a premise column or another derived premise. Only AND and OR: excluding a
premise can still only void a theorem, never revive one (ADR-0045 §3). A theorem may replace a BASE row with a
derived premise (`"replaces": {"T-0045-29": "invariant(Seats)"}`). A premise column of kind `check` takes its value
from a results file, `{"results": "<glob from the repository root>", "lines": "<regex>", "want": "<suffix>"}`: true
when the newest such file's every `path (sha256 …)` matches the tree and every line the regex selects ends with the
suffix; a declaration may set it false, never true against the check.

    inventory.py <declaration.json> <binding.json> --with <overlay.json> [--cuts]
    inventory.py --annex-b [ADR-0045.md]            the reference's rows as a declaration, from Annex B
    inventory.py --check [binding.json] [binding.md] [ADR-0045.md] [--with overlay.json]

`--with` applies an overlay: its premise columns and derived premises are added, and each of its theorems, named as
the binding names them, gets its `replaces`. `--cuts` prints, for each theorem that holds, its minimal cut sets of
one and two atoms: what a deployment cannot lose, alone or in pairs, and keep it.
"""
import glob
import hashlib
import itertools
import json
import os
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


ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
TROW = re.compile(r"T-0045-\d+$")


def check_value(spec):
    """A `check` premise: (value, why), from the newest results file the glob names."""
    files = sorted(glob.glob(os.path.join(ROOT, spec["results"])))
    if not files:
        return False, f"no {spec['results']}"
    f = files[-1]
    text = open(f, encoding="utf-8").read()
    stale = []
    for line in text.splitlines():
        if not re.match(r"(Transcribes|Floor|Sources|Model|Reference):", line):
            continue
        for path, dig in re.findall(r"([A-Za-z0-9_./-]+) \(sha256 ([0-9a-f]{16})", line):
            full = os.path.join(ROOT, path)
            if not os.path.isfile(full) or hashlib.sha256(open(full, "rb").read()).hexdigest()[:16] != dig:
                stale.append(path)
    picked = [ln for ln in text.splitlines() if re.search(spec["lines"], ln)]
    name = os.path.relpath(f, ROOT)
    if stale:
        return False, f"{name} is stale: {', '.join(stale)} moved"
    if not picked:
        return False, f"{name} has no line {spec['lines']!r}"
    failed = [ln for ln in picked if not ln.rstrip().endswith(spec["want"])]
    if failed:
        return False, f"{name}: {len(failed)} of {len(picked)} lines not {spec['want']!r}"
    return True, f"{name}: {len(picked)} of {len(picked)} lines {spec['want'].strip(' |')}, in sync"


def merge(binding, overlay):
    """The binding with an overlay's premise columns, derived premises and replacements applied."""
    b = json.loads(json.dumps(binding))
    clash = (set(overlay.get("premises", {})) & set(b["premises"])) | (set(overlay.get("derived", {})) & set(b.get("derived", {})))
    if clash:
        sys.exit("inventory.py: the overlay redefines " + ", ".join(sorted(clash)))
    b["premises"].update(overlay.get("premises", {}))
    b.setdefault("derived", {}).update(overlay.get("derived", {}))
    by = {tuple(t["names"]): t for t in b["theorems"]}
    for ot in overlay.get("theorems", []):
        t = by.get(tuple(ot["names"]))
        if t is None:
            sys.exit(f"inventory.py: the overlay names {ot['names']}, which the binding does not have")
        t.setdefault("replaces", {}).update(ot.get("replaces", {}))
    return b


def base_of(binding, t):
    rep_ = t.get("replaces", {})
    return [rep_.get(r, r) for r in binding["base"]]


class Values:
    """Every atom's value for one declaration: rows, premise columns, derived premises."""

    def __init__(self, binding, decl):
        self.b, self.rung = binding, decl["rung"]
        self.declared, values = decl.get("rows", {}), decl.get("premises", {})
        unknown = sorted(set(values) - set(binding["premises"]))
        if unknown:
            sys.exit("inventory.py: the declaration sets premises the binding does not have: " + ", ".join(unknown))
        self.d, self.why = {}, {}
        for p, spec in binding["premises"].items():
            if "derived" in spec:
                self.d[p] = derived_value(spec["derived"], self.rung)
            elif spec.get("kind") == "check":
                ok, why = check_value(spec["check"])
                if values.get(p) is False:
                    ok, why = False, "declared false"
                self.d[p], self.why[p] = ok, why
            else:
                self.d[p] = values.get(p) is True
        self.holds_when = binding.get("row_holds_when", HOLDS)

    def atom(self, a, seen=()):
        """(value, explanation) of one atom; a derived premise reports the route that carried it, or every
        route's failing atoms."""
        if TROW.match(a):
            cls = self.declared.get(a, "undeclared")
            return cls in self.holds_when, f"{a} {cls}"
        if a in self.b.get("derived", {}):
            if a in seen:
                sys.exit(f"inventory.py: derived premise {a} refers to itself")
            fails = []
            for route in self.b["derived"][a]["any_of"]:
                vals = [self.atom(x, seen + (a,)) for x in route]
                if all(v for v, _ in vals):
                    return True, f"{a} by {' + '.join(route)}"
                fails.append(" + ".join(e for v, e in vals if not v))
            return False, f"{a} [{' | '.join(fails)}]"
        if a in self.d:
            return self.d[a], a
        sys.exit(f"inventory.py: {a} is neither a row, a premise column nor a derived premise")


def requirement(binding, t, rung):
    rows, premises = matrix_rows(t, rung)
    return list(dict.fromkeys(base_of(binding, t) + rows + premises))


def dnf(binding, atoms, seen=()):
    """The requirement over leaf atoms, as a list of alternative sets (each a frozenset)."""
    terms = [frozenset()]
    for a in atoms:
        if a in binding.get("derived", {}):
            alts = []
            for route in binding["derived"][a]["any_of"]:
                alts += dnf(binding, route, seen + (a,))
        else:
            alts = [frozenset([a])]
        terms = [t | u for t in terms for u in alts]
    return [t for t in terms if not any(u < t for u in terms)]


def cuts(binding, t, rung, up_to=2):
    """Minimal sets of leaf atoms, of at most `up_to`, whose loss voids the theorem."""
    terms = dnf(binding, requirement(binding, t, rung))
    leaves = sorted(set().union(*terms))
    found = []
    for k in range(1, up_to + 1):
        for c in itertools.combinations(leaves, k):
            cs = set(c)
            if all(cs & term for term in terms) and not any(set(f) <= cs for f in found):
                found.append(c)
    return found


def evaluate(decl, path, overlay=None, show_cuts=False):
    """holds = NOT(B · NOT d), row by row; a derived premise is an OR of such rows."""
    binding = json.load(open(path))
    if overlay:
        binding = merge(binding, json.load(open(overlay)))
    v = Values(binding, decl)
    rung = v.rung
    print(f"Inventory for rung {rung}, {len(v.declared)} rows and {sum(v.d.values())} of {len(v.d)} other premises "
          f"true · from {path}" + (f" with {overlay}" if overlay else ""))
    for p, why in v.why.items():
        print(f"  check {p}: {'true' if v.d[p] else 'false'} ({why})")
    held = 0
    for t in binding["theorems"]:
        need = requirement(binding, t, rung)
        vals = [(a, *v.atom(a)) for a in need]
        bad = [e for _, ok, e in vals if not ok]
        via = [e for a, ok, e in vals if ok and a in binding.get("derived", {})]
        held += not bad
        line = f"- {', '.join(t['names'])}: " + ("holds" if not bad else "void: " + ", ".join(bad))
        if not bad and via:
            line += f" (via {'; '.join(via)})"
        print(line)
        if show_cuts and not bad:
            cs = cuts(binding, t, rung)
            single = [c[0] for c in cs if len(c) == 1]
            pairs = [" + ".join(c) for c in cs if len(c) == 2]
            print(f"    cuts: {len(single)} single" + (f"; pairs: {', '.join(pairs)}" if pairs else "; no pair"))
    print(f"{held} of {len(binding['theorems'])} rows hold")


def annex_b(path):
    """ADR-0045 Annex B's classes, as a declaration of the reference's rows at rung 0."""
    rows, inb = {}, False
    for line in open(path):
        if line.startswith("## Annex B"):
            inb = True
        elif line.startswith("## ") and inb:
            break
        m = re.match(r"\| (T-0045-[\d, to]+) \|", line) if inb else None
        if not m:
            continue
        cells = [c.strip() for c in line.strip().strip("|").split(" | ")]
        cls = strip_struck(cells[2]).replace("*", "").lower() if len(cells) > 2 else ""
        cls = next((c for c in ("excluded", "trust root", "delegated") if c in cls), None)
        nums = []
        for a, b in re.findall(r"(\d+)(?:\s+to\s+(\d+))?", m.group(1).replace("T-0045-", "")):
            nums += range(int(a), int(b or a) + 1)
        for n in nums:
            if cls:
                rows[f"T-0045-{n}"] = cls
    return {"rung": 0, "rows": rows, "premises": {}}


def check_derived(binding):
    """Every derived premise names only defined atoms, has a route, and does not refer to itself."""
    errors = []
    derived = binding.get("derived", {})
    known = set(binding["premises"]) | set(derived)
    for name, spec in derived.items():
        if not spec.get("any_of") or not all(spec["any_of"]):
            errors.append(f"derived {name} has an empty route")
        for route in spec.get("any_of", []):
            for a in route:
                if not TROW.match(a) and a not in known:
                    errors.append(f"derived {name}: {a} is undefined")

    def reach(n, path):
        for route in derived.get(n, {}).get("any_of", []):
            for a in route:
                if a in path:
                    errors.append(f"derived {n} refers to itself through {a}")
                elif a in derived:
                    reach(a, path | {a})
    for n in derived:
        reach(n, {n})
    for t in binding["theorems"]:
        for r, dname in t.get("replaces", {}).items():
            if r not in binding["base"]:
                errors.append(f"{t['names']}: replaces {r}, which is not a BASE row")
            if dname not in derived:
                errors.append(f"{t['names']}: replaces {r} with {dname}, which is not a derived premise")
            elif [r] not in derived[dname]["any_of"] and not derived[dname].get("corrects"):
                errors.append(f"{t['names']}: {dname} neither keeps {r} as a route nor says what it corrects")
    for p, spec in binding["premises"].items():
        if spec.get("kind") == "check" and not all(k in spec.get("check", {}) for k in ("results", "lines", "want")):
            errors.append(f"check premise {p} lacks results, lines or want")
    return errors


def check(path, table_path, annex_path, overlay=None):
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
    derrs = check_derived(binding)
    if overlay:
        derrs += check_derived(merge(binding, json.load(open(overlay))))
    for e in derrs:
        print("DERIVED", e)
    if overlay or binding.get("derived"):
        merged = merge(binding, json.load(open(overlay))) if overlay else binding
        print(f"{len(merged.get('derived', {}))} derived premises"
              + (f" with {overlay}" if overlay else "") + (": well formed" if not derrs else f": {len(derrs)} errors"))
    return not errors and not derrs


def main():
    here = __file__.rsplit("/", 1)[0]
    argv = sys.argv[1:]
    overlay = None
    if "--with" in argv:
        i = argv.index("--with")
        overlay = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    show_cuts = "--cuts" in argv
    argv = [a for a in argv if a != "--cuts"]
    if argv[0] == "--annex-b":
        print(json.dumps(annex_b(argv[1] if len(argv) > 1 else here + "/../decisions/ADR-0045.md"), indent=1))
        return
    if argv[0] == "--check":
        args = argv[1:] + [None] * 3
        sys.exit(0 if check(args[0] or here + "/theorem-premise-binding.json",
                            args[1] or here + "/theorem-premise-binding.md",
                            args[2] or here + "/../decisions/ADR-0045.md", overlay) else 1)
    decl = json.load(open(argv[0]))
    binding = argv[1] if len(argv) > 1 else here + "/theorem-premise-binding.md"
    if binding.endswith(".json"):
        return evaluate(decl, binding, overlay, show_cuts)
    applies = annex_rungs(argv[2] if len(argv) > 2 else here + "/../decisions/ADR-0045.md")
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
