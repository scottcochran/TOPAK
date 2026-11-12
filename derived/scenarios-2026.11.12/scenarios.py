#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6", "jsonschema>=4.18"]
# ///
"""Check the scenario inventory and regenerate its index.

  uv run --script scenarios.py check            validate every <id>.md here; exit 1 on any problem
  uv run --script scenarios.py index            rewrite INDEX.md from the front matter
  uv run --script scenarios.py vocab [Module..] list what a trace step, property or mutation may name

check validates each file's YAML front matter against schema.yaml, then:
  - the file name is <id>.md, ids are unique, and the id's sector code matches `sector`;
  - the body has the five sections, in order: Summary, Defensive position, Adversarial
    position, Outcome, Analysis;
  - every reference into the corpus resolves under BINDINGS below: trace and counterfactual steps,
    model.properties and counterfactual.holds, model.mutations, model.modules (unless proposed:),
    model.records and analogue[].record, model.findings.

The schema is generic; BINDINGS is the only part of this directory that knows the corpus is TOPAK.
"""
import collections
import pathlib
import re
import sys

import jsonschema
import yaml

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
SECTIONS = ["Summary", "Defensive position", "Adversarial position", "Outcome", "Analysis"]

SECTOR_CODES = {
    "telecom": "TEL", "networking": "NET", "cloud": "CLD", "fintech": "FIN", "control": "CTL",
    "game-theory": "GAM", "industrial-control": "ICS", "energy": "NRG", "robotics": "ROB",
    "aviation": "AVI", "space": "SPC", "medical": "MED", "ai-agents": "AIA",
}


# ---------------------------------------------------------------- BINDINGS (TOPAK)
def _spec_modules():
    """spec/*.tla, without the generated Trace_* modules (gitignored, regenerated per run)."""
    return [p for p in sorted((ROOT / "spec").glob("*.tla")) if not p.name.startswith("Trace_")]


def _operators(src):
    return set(re.findall(r"^([A-Za-z][A-Za-z0-9_]*)\s*(?:\([^)]*\))?\s*==", src, re.M))


def _mutations(src):
    return set(re.findall(r'"(M_[A-Z0-9_]+|M[0-9]+)"', src))


def bind_spec():
    ops, muts, mods = set(), set(), set()
    for tla in _spec_modules():
        src = tla.read_text(encoding="utf-8")
        mods.add(tla.stem)
        ops |= _operators(src)
        muts |= _mutations(src)
    return ops, muts, mods


def bind_records():
    return {p.stem for p in (ROOT / "decisions").glob("ADR-[0-9][0-9][0-9][0-9].md")}


def bind_findings():
    """CR-n from the critical reviews in derived/; TMn, the adversaries of ADR-0068's table;
    T-NNNN-n and A-NNNN-n, the trusted-base and assumption rows of any record's tables."""
    ids = set()
    for p in (ROOT / "derived").glob("topak-critical-review-*.md"):
        ids |= set(re.findall(r"\bCR-[0-9]+\b", p.read_text(encoding="utf-8")))
    adr68 = ROOT / "decisions" / "ADR-0068.md"
    if adr68.exists():
        ids |= set(re.findall(r"^\| (TM[0-9]+) \|", adr68.read_text(encoding="utf-8"), re.M))
    for p in (ROOT / "decisions").glob("ADR-*.md"):
        ids |= set(re.findall(r"^\| \**([TA]-[0-9]{4}-[0-9]+)\** \|", p.read_text(encoding="utf-8"), re.M))
    return ids
# ---------------------------------------------------------------- end BINDINGS


class _NoDates(yaml.SafeLoader):
    """SafeLoader that leaves YYYY-MM-DD and clock times as strings: the schema checks dates by pattern,
    and YAML 1.1 would otherwise read an unquoted 21:34:49 as a base-60 integer."""


_SEXAGESIMAL = re.compile(r"^[-+]?[0-9][0-9_]*(?::[0-5]?[0-9])+(?:\.[0-9_]*)?$")
_NoDates.yaml_implicit_resolvers = {
    k: ([("tag:yaml.org,2002:str", _SEXAGESIMAL)] if k in "+-0123456789" else [])
       + [r for r in v if r[0] != "tag:yaml.org,2002:timestamp"]
    for k, v in yaml.SafeLoader.yaml_implicit_resolvers.items()
}


def load(path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        raise ValueError("no front matter")
    return yaml.load(m.group(1), Loader=_NoDates), m.group(2)


NOT_SCENARIOS = ("README.md", "INDEX.md", "FINDINGS_TOPAK.md")


def files():
    return sorted(p for p in HERE.glob("*.md") if p.name not in NOT_SCENARIOS)


def check():
    schema = yaml.safe_load((HERE / "schema.yaml").read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)
    ops, muts, mods = bind_spec()
    recs, fids = bind_records(), bind_findings()
    problems, seen = [], {}
    paths = files()
    if not paths:
        problems.append("no scenario files")
    for p in paths:
        def bad(msg, p=p):
            problems.append(f"{p.name}: {msg}")
        try:
            fm, body = load(p)
        except Exception as e:  # noqa: BLE001
            bad(str(e))
            continue
        for err in sorted(validator.iter_errors(fm), key=lambda e: list(map(str, e.path))):
            bad(f"schema: {'/'.join(map(str, err.path)) or '(top)'}: {err.message}")
        if not isinstance(fm, dict) or "id" not in fm:
            continue
        if p.stem != fm["id"]:
            bad(f"file name does not match id {fm['id']}")
        if fm["id"] in seen:
            bad(f"duplicate id, also in {seen[fm['id']]}")
        seen[fm["id"]] = p.name
        code = SECTOR_CODES.get(fm.get("sector"))
        if code and fm["id"].split("-")[1] != code:
            bad(f"id sector code is {fm['id'].split('-')[1]}, expected {code} for sector {fm['sector']}")
        heads = re.findall(r"^## (.+?)\s*$", body, re.M)
        if heads != SECTIONS:
            bad(f"sections are {heads}, expected {SECTIONS}")
        cf = fm.get("counterfactual") or {}
        for where, steps in (("trace", fm.get("trace", [])), ("counterfactual step", cf.get("trace", []))):
            for step in steps:
                s = step.get("step", "")
                if not s.startswith("outside:") and s not in ops:
                    bad(f"{where} {s} is not an operator in spec/*.tla")
        model = fm.get("model", {})
        for where, props in (("property", model.get("properties", [])), ("counterfactual holds", cf.get("holds", []))):
            for prop in props:
                if prop not in ops:
                    bad(f"{where} {prop} is not defined in spec/*.tla")
        for m in model.get("mutations", []):
            if m not in muts:
                bad(f"mutation {m} is not used in spec/*.tla")
        for m in model.get("modules", []):
            if not m.startswith("proposed:") and m not in mods:
                bad(f"module {m} is not in spec/")
        for r in model.get("records", []) + [a.get("record") for a in fm.get("analogue", [])]:
            if r not in recs:
                bad(f"record {r} is not a file in decisions/")
        for f in model.get("findings", []):
            if f not in fids:
                bad(f"finding {f} is not a CR- id in derived/topak-critical-review-*.md or a TM row of ADR-0068")
    for line in problems:
        print(line)
    print(f"scenarios: {len(paths)} files, {len(problems)} problems")
    return 1 if problems else 0


def index():
    by_sector = collections.defaultdict(list)
    outside, proposed, kinds = collections.Counter(), collections.Counter(), collections.Counter()
    for p in files():
        fm, _ = load(p)
        kinds[fm["kind"]] += 1
        faults = sorted({a["fault"] for a in fm["actors"]
                         if a["fault"] not in ("honest", "none-alleged")})
        mods = ", ".join(fm["model"]["modules"])
        by_sector[fm["sector"]].append((fm["date"], (
            f"| {fm['date'][:4]} | [{fm['title']}]({p.name}) | {fm['kind']} | "
            f"{', '.join(fm['concerns'])} | {', '.join(faults) or '—'} | {mods} | "
            f"{fm['outcome']['effect_reversed']} |")))
        for s in fm["trace"]:
            if s["step"].startswith("outside:"):
                outside[s["step"]] += 1
        for m in fm["model"]["modules"]:
            if m.startswith("proposed:"):
                proposed[m.removeprefix("proposed:")] += 1
    n = sum(len(v) for v in by_sector.values())
    out = ["# Scenario index", "",
           "Generated by `scenarios.py index` from each file's front matter. Do not edit by hand.", "",
           f"{n} scenarios: " + ", ".join(f"{c} {k}" for k, c in sorted(kinds.items())) + ".", ""]
    for sector in SECTOR_CODES:
        rows = by_sector.get(sector)
        if not rows:
            continue
        out += [f"## {sector}", "",
                "| Year | Scenario | Kind | Concerns | Faults | Modules | Effect reversed |",
                "|---|---|---|---|---|---|---|"]
        out += [r for _, r in sorted(rows)] + [""]
    out += ["## Steps no module has yet", "",
            "Every `outside:` trace step, by the number of scenarios that need it.", "",
            "| Step | Scenarios |", "|---|---|"]
    out += [f"| `{s}` | {c} |" for s, c in sorted(outside.items(), key=lambda x: (-x[1], x[0]))] + [""]
    out += ["## Proposed modules", "", "| Module | Scenarios |", "|---|---|"]
    out += [f"| `{m}` | {c} |" for m, c in sorted(proposed.items(), key=lambda x: (-x[1], x[0]))]
    (HERE / "INDEX.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"wrote INDEX.md ({n} scenarios)")
    return 0


def vocab(names):
    """Per module: operators (actions and properties alike) and mutations, for an author choosing steps."""
    for tla in _spec_modules():
        if tla.stem.endswith("_proof") or (names and tla.stem not in names):
            continue
        src = tla.read_text(encoding="utf-8")
        print(f"{tla.stem}\n  operators: {' '.join(sorted(_operators(src)))}")
        m = _mutations(src)
        if m:
            print(f"  mutations: {' '.join(sorted(m))}")
    return 0


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    if cmd == "vocab":
        sys.exit(vocab(set(sys.argv[2:])))
    sys.exit({"check": check, "index": index}.get(cmd, lambda: (print(__doc__), 2)[1])())
