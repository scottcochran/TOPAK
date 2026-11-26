"""Build-time reads of one TLA+ module's evidence, for the diagrams that draw one module each (family I).

Ported from gov-tla's diagrams/gov-tla/src/corpus.py (the same author), for TOPAK's files. Every reader parses
strictly and raises CorpusError on anything it does not expect, so a diagram that draws from a file fails to build
when the file changes shape, the way a gate fails.

The files a diagram draws are NAMED here, never chosen as "the newest matching a pattern": a new results file
changes no diagram until this table is moved on purpose, which is an amendment of the diagrams that draw it. Where
the records cite a file, the file named is the one they cite (the Lean results: ADR-0053 R6).

Every file is read as it is at the diagram's pin (lib.PIN_LINKS), so a link lands on the line drawn, and the tree's
copy must be the same bytes: when a file a diagram draws moves on, the diagram fails until it is amended or its pin
is moved. Standard library only.

TOPAK's TLC results come in three shapes, older than the -rows.txt row lists of the modules built since October:
  pipe  "TOPAK — <M>.tla (<record>), TLC results <date>", "key: value" lines, then
        "<row> | Mut=<m> | <property> | HOLDS|COUNTEREXAMPLE | <n> distinct states found"
  bare  the same rows with no header, and a mechanism column in place of Mut= (RulesFloorNV, 2026.09.15)
  log   a header, then TLC's own output in sections "=== [<Module> · ]<row> · <k>=<v> · ... · INVARIANT <P>"
"""
import hashlib
import pathlib
import re
import subprocess

import lib
import sources

ROOT = pathlib.Path(__file__).resolve().parents[3]

# The trace validation that reads the reference's recorded behaviours against Mechanism.tla and, state by state,
# against ConfinementRefinement.tla's invariants (G10 §3's row; ADR-0033 A14).
TRACE_RESULTS = "spec/Mechanism-trace-results-2026.10.05.txt"

# The Lean results the records cite (ADR-0053 R6 cites TopakSpec-results-2026.10.06b.txt; ADR-0053 and
# spec/theorem-premise-binding.md cite GraphCheck-results-2026.10.06.txt). A later file is compared, not drawn.
LEAN_RESULTS = "spec/lean/TopakSpec-results-2026.10.06b.txt"
LEAN_LATER = "spec/lean/TopakSpec-results-2026.10.07.txt"
GRAPH_RESULTS = "spec/lean/GraphCheck-results-2026.10.06.txt"
GRAPH_LATER = "spec/lean/GraphCheck-results-2026.10.07.txt"

# Per module: its files, and the TLC results file and shape it draws (section: the module's sections of a log
# shared with another module). None where the module has no such evidence.
MODULES = {
    "Seats": dict(
        module="spec/Seats.tla", proof="spec/Seats_proof.tla",
        tlc="spec/Seats-results-2026.09.29.txt", shape="pipe", section=None,
        proof_results="spec/Seats-proof-results-2026.10.02.txt",
        cert="spec/Seats-proof-cert-results-2026.10.04.txt",
        lean="spec/lean/TopakSpec/Seats.lean", mirror="spec/lean/TopakSpec/Mirror/Seats.lean", graph=True),
    "RunSeats": dict(
        module="spec/RunSeats.tla", proof="spec/RunSeats_proof.tla",
        tlc="spec/RunSeats-results-2026.09.29.txt", shape="pipe", section=None,
        proof_results="spec/RunSeats-proof-results-2026.10.02.txt",
        cert="spec/RunSeats-proof-cert-results-2026.10.04.txt",
        lean="spec/lean/TopakSpec/RunSeats.lean", mirror=None, graph=False),
    "FloorComposition": dict(
        module="spec/FloorComposition.tla", proof="spec/FloorComposition_proof.tla",
        tlc="spec/FloorComposition-results-2026.09.24.txt", shape="log", section="FloorComposition",
        proof_results="spec/FloorComposition-proof-results-2026.10.02.txt",
        cert="spec/FloorComposition-proof-cert-results-2026.10.04.txt",
        lean="spec/lean/TopakSpec/FloorComposition.lean",
        mirror="spec/lean/TopakSpec/Mirror/FloorComposition.lean", graph=True),
    "FloorRouting": dict(
        module="spec/FloorRouting.tla", proof="spec/FloorRouting_proof.tla",
        tlc="spec/FloorComposition-results-2026.09.24.txt", shape="log", section="FloorRouting",
        proof_results="spec/FloorRouting-proof-results-2026.10.02.txt",
        cert="spec/FloorRouting-proof-cert-results-2026.10.04.txt",
        lean="spec/lean/TopakSpec/FloorRouting.lean", mirror=None, graph=False),
    "RulesFloorNV_rev5": dict(
        module="spec/RulesFloorNV_rev5.tla", proof="spec/RulesFloorNV_rev5_proof.tla",
        tlc="spec/RulesFloorNV-rev5-results-2026.09.23.txt", shape="log", section=None,
        proof_results="spec/RulesFloorNV_rev5-proof-results-2026.10.02.txt",
        cert="spec/RulesFloorNV_rev5-proof-cert-results-2026.10.04.txt",
        lean="spec/lean/TopakSpec/RulesFloorNV_rev5.lean", mirror=None, graph=False),
    "RulesFloorBase": dict(
        module="spec/RulesFloorBase.tla", proof=None, tlc=None, shape=None, section=None,
        proof_results=None, cert=None,
        lean="spec/lean/TopakSpec/RulesFloorBase.lean", mirror=None, graph=False),
    "RulesFloorNV": dict(
        module="spec/RulesFloorNV.tla", proof=None,
        tlc="spec/RulesFloorNV-results-2026.09.15.txt", shape="bare", section=None,
        proof_results=None, cert=None, lean=None, mirror=None, graph=False),
    "Confinement": dict(
        module="spec/Confinement.tla", proof="spec/Confinement_proof.tla",
        tlc=("spec/Confinement-results-2026.09.28.txt", "spec/Confinement-results-2026.09.30.txt"), shape="log",
        section=None, proof_results="spec/Confinement-proof-results-2026.10.02.txt",
        cert="spec/Confinement-proof-cert-results-2026.10.04.txt",
        lean="spec/lean/TopakSpec/Confinement.lean", mirror=None, graph=False),
    "Confinement_A1": dict(
        module="spec/Confinement_A1.tla", proof="spec/Confinement_A1_proof.tla",
        tlc="spec/Confinement_A1-results-2026.10.02.txt", shape="log", section=None,
        proof_results="spec/Confinement_A1-proof-results-2026.10.02.txt",
        cert="spec/Confinement_A1-proof-cert-results-2026.10.04.txt",
        lean="spec/lean/TopakSpec/Confinement.lean", mirror=None, graph=False),
    "ConfinementRefinement": dict(
        module="spec/ConfinementRefinement.tla", proof=None, tlc=None, shape=None, section=None,
        proof_results=None, cert=None, lean=None, mirror=None, graph=False),
    "RunConfinement": dict(
        module="spec/RunConfinement.tla", proof="spec/RunConfinement_proof.tla",
        tlc="spec/RunConfinement-results-2026.10.02.txt", shape="log", section=None,
        proof_results="spec/RunConfinement-proof-results-2026.10.02.txt",
        cert="spec/RunConfinement-proof-cert-results-2026.10.04.txt", lean=None, mirror=None, graph=False),
    "Lease": dict(
        module="spec/Lease.tla", proof=None, tlc="spec/Lease-results-2026.09.25.txt", shape="log", section=None,
        proof_results=None, cert=None, lean=None, mirror=None, graph=False),
    "Lease_A1": dict(
        module="spec/Lease_A1.tla", proof="spec/Lease_A1_proof.tla",
        tlc="spec/Lease_A1-results-2026.09.28.txt", shape="log", section=None,
        proof_results="spec/Lease_A1-proof-results-2026.10.02.txt",
        cert="spec/Lease_A1-proof-cert-results-2026.10.04.txt",
        lean="spec/lean/TopakSpec/Lease_A1.lean", mirror=None, graph=False),
    "Labels": dict(
        module="spec/Labels.tla", proof="spec/Labels_proof.tla",
        tlc="spec/Labels-results-2026.10.04.txt", shape="log", section=None,
        proof_results="spec/Labels-proof-results-2026.10.04.txt",
        cert="spec/Labels-proof-cert-results-2026.10.04.txt", lean=None, mirror=None, graph=False),
    "ToolList": dict(
        module="spec/ToolList.tla", proof="spec/ToolList_proof.tla",
        tlc="spec/ToolList-results-2026.10.04.txt", shape="log", section=None,
        proof_results="spec/ToolList-proof-results-2026.10.04.txt",
        cert="spec/ToolList-proof-cert-results-2026.10.04.txt", lean=None, mirror=None, graph=False),
}


class CorpusError(Exception):
    """A file a diagram reads is missing, has moved on from the pin, or is not the shape the diagram expects."""


def _need(cond, rel, what):
    if not cond:
        raise CorpusError(f"{rel}: {what}")


def pin():
    return sources.at(lib.CTX.pin)


def text(rel):
    """The file as it is at the pin; the tree's copy must be the same bytes."""
    p = pin()
    t = p.text(rel)
    _need(t is not None, rel, f"not tracked at {p.commit[:7]}")
    tree = ROOT / rel
    _need(tree.is_file(), rel, "missing from the tree")
    _need(tree.read_bytes().decode("utf-8") == t, rel,
          f"the tree's copy differs from the pin's ({p.commit[:7]}): amend the diagram, or move its pin")
    return t


def sha16(rel):
    text(rel)
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()[:16]


def _shas(v, rel, what):
    """'a.tla (sha256 0123…) · b.tla (sha256 …)' -> {name: sha16}."""
    out = {}
    for part in v.split(" · "):
        m = re.fullmatch(r"(\S+) \(sha256 ([0-9a-f]{16})\)", part.strip())
        _need(m, rel, f"bad {what} entry {part[:60]!r}")
        out[m.group(1)] = m.group(2)
    return out


# ---------------------------------------------------------------------------------------------- the module
def header_comment(rel):
    """The module's leading comment, as lines with the (* *) frame stripped and trailing space removed."""
    lines = text(rel).split("\n")
    _need(lines and re.match(r"^-+ MODULE \w+ -+$", lines[0]), rel, "line 1 is not the MODULE line")
    out = []
    for ln in lines[1:]:
        m = re.fullmatch(r"\(\*(.*)\*\)\s*", ln)
        if not m:
            break
        out.append(m.group(1).rstrip())
    _need(out, rel, "no leading comment")
    return out


def header_mutations(rel, var="Mut"):
    """The mutations the module's header lists, in order: [(name, description)], description joined from its
    continuation lines, up to the next entry or an empty comment line."""
    out, cur = [], None
    for ln in header_comment(rel):
        s = ln.strip()
        m = re.match(rf'^{var} = ((?:"\w+"(?:, )?)+):\s*(.*)$', s)
        if m:
            # one entry may name several mutations that share a description ('Mut = "M_F1", "M_F2": ...')
            cur = [re.findall(r'"(\w+)"', m.group(1)), m.group(2)]
            out.append(cur)
        elif cur is not None and s:
            cur[1] += " " + s
        else:
            cur = None
    _need(out, rel, f'the header lists no {var} = "..." entries')
    return [(n, re.sub(r"\s+", " ", d).strip()) for ns, d in out for n in ns]


def definition(rel, name):
    """(line, text) of a top-level definition, from its line to the line before the next top-level line (a
    definition, a comment, a separator or the end), trailing blank lines dropped."""
    lines = text(rel).split("\n")
    rx = re.compile(rf"^{re.escape(name)}\s*(?:\([^)]*\))?\s*==")
    hits = [i for i, ln in enumerate(lines) if rx.match(ln)]
    _need(len(hits) == 1, rel, f"{name} is defined {len(hits)} times, not once")
    i = hits[0]
    j = i + 1
    while j < len(lines) and (lines[j].startswith((" ", "\t")) or not lines[j].strip()):
        j += 1
    body = lines[i:j]
    while body and not body[-1].strip():
        body.pop()
    return i + 1, "\n".join(body)


def line_of(rel, pattern):
    """The 1-based line of the one line that matches."""
    hits = [i + 1 for i, ln in enumerate(text(rel).split("\n")) if re.search(pattern, ln)]
    _need(len(hits) == 1, rel, f"{pattern!r} matches {len(hits)} lines, not one")
    return hits[0]


def header_properties(rel):
    """The properties the module's header lists with the section each states: [(name, section, words)], the
    words joined from continuation lines, up to the next entry or an empty comment line."""
    out, cur = [], None
    defined = set(re.findall(r"^([A-Za-z_]\w*)\s*(?:\([^)]*\))?\s*==", text(rel), re.M))
    for ln in header_comment(rel):
        if re.match(r'^\s*(?:Mut|Mech) = "', ln):
            break
        m = re.match(r"^\s{3,}([A-Z]\w*)(?:\s+((?:\d{4} )?§[\d.]+))?\s+(\S.*)$", ln)
        if m and m.group(1) in defined:
            cur = [m.group(1), m.group(2), m.group(3)]
            out.append(cur)
        elif cur is not None and ln.strip() and re.match(r"^\s{20,}\S", ln):
            cur[2] += " " + ln.strip()
        else:
            cur = None
    _need(out, rel, "the header lists no properties with their sections")
    return [(a, b, re.sub(r"\s+", " ", c).strip()) for a, b, c in out]  # b is None: the header names no section


_STMT = re.compile(r"^(THEOREM|LEMMA)\s+(\w+)\s*==\s*(.*)$")
_PROOF_START = re.compile(r"^(?:<\d+>|BY\b|PROOF\b|OBVIOUS\b|OMITTED\b)")


def statements(rel):
    """Every THEOREM and LEMMA of a proof module, in order: dict(kind, name, line, assume, prove), where assume
    is the ASSUME clause's text (None without one) and prove the statement proper, whitespace collapsed."""
    lines = text(rel).split("\n")
    out = []
    for i, ln in enumerate(lines):
        m = _STMT.match(ln)
        if not m:
            continue
        parts = [m.group(3)]
        j = i + 1
        while j < len(lines) and lines[j].strip() and not _PROOF_START.match(lines[j].strip()) \
                and not _STMT.match(lines[j]):
            parts.append(lines[j].strip())
            j += 1
        s = re.sub(r"\s+", " ", " ".join(parts)).strip()
        a = re.fullmatch(r"ASSUME (.+?) PROVE (.+)", s)
        out.append(dict(kind=m.group(1), name=m.group(2), line=i + 1,
                        assume=a.group(1) if a else None, prove=a.group(2) if a else s))
    _need(out, rel, "no THEOREM or LEMMA")
    names = [s["name"] for s in out]
    _need(len(set(names)) == len(names), rel, "a statement name twice")
    return out


# ---------------------------------------------------------------------------------------------- TLC results
_PIPE_ROW = re.compile(r"^([\w-]+) \| Mut=(\S+) \| (\w+) \| (HOLDS|COUNTEREXAMPLE) \| (\d+) distinct states found$")
_BARE_ROW = re.compile(r"^([\w-]+) \| (\w+) \| (\w+) \| (HOLDS|COUNTEREXAMPLE) \| (\d+) distinct states found$")


def tlc_pipe(rel):
    """Shape pipe. Returns dict(module, cite, date, head {key: value}, rows [dict(name, mut, prop, verdict,
    states)])."""
    lines = [ln for ln in text(rel).split("\n") if ln.strip()]
    m = re.fullmatch(r"TOPAK — (\w+)\.tla \((.+)\), TLC results (\d{4}\.\d{2}\.\d{2})", lines[0])
    _need(m, rel, "line 1 is not 'TOPAK — <M>.tla (<record>), TLC results <date>'")
    out = dict(module=m.group(1), cite=m.group(2), date=m.group(3), head={}, rows=[])
    for ln in lines[1:]:
        r = _PIPE_ROW.match(ln)
        if r:
            out["rows"].append(dict(name=r.group(1), mut=r.group(2), prop=r.group(3), verdict=r.group(4),
                                    states=int(r.group(5))))
            continue
        _need(not out["rows"], rel, f"a line after the rows that is not a row: {ln[:80]!r}")
        k, sep, v = ln.partition(": ")
        _need(sep and re.fullmatch(r"[a-z]+", k) and k not in out["head"], rel, f"bad header line {ln[:80]!r}")
        out["head"][k] = v
    _need(out["rows"], rel, "no rows")
    names = [r["name"] for r in out["rows"]]
    _need(len(set(names)) == len(names), rel, "a row name twice")
    return out


def tlc_bare(rel):
    """Shape bare. Returns dict(rows [dict(name, mech, prop, verdict, states)])."""
    rows = []
    for ln in text(rel).split("\n"):
        if not ln.strip():
            continue
        r = _BARE_ROW.match(ln)
        _need(r, rel, f"row does not parse: {ln[:80]!r}")
        rows.append(dict(name=r.group(1), mech=r.group(2), prop=r.group(3), verdict=r.group(4),
                         states=int(r.group(5))))
    _need(rows, rel, "no rows")
    return dict(rows=rows)


_SEC = re.compile(r"^=== (.+)$")
_STATES = re.compile(r"^(\d+) states generated, (\d+) distinct states found, (\d+) states left on queue\.$")


def tlc_log(rel, section=None):
    """Shape log. Returns dict(head [lines], rows [dict(module, name, params {k: v}, prop, verdict, states, left,
    line)]). section: keep only the rows of that module (its name leads the section line)."""
    lines = text(rel).split("\n")
    starts = [i for i, ln in enumerate(lines) if _SEC.match(ln)]
    _need(starts, rel, "no '=== ' sections")
    head = [ln for ln in lines[:starts[0]] if ln.strip()]
    _need(head and head[0].startswith("TOPAK — "), rel, "line 1 is not 'TOPAK — ...'")
    rows = []
    for n, i in enumerate(starts):
        body = lines[i + 1:(starts[n + 1] if n + 1 < len(starts) else len(lines))]
        parts = _SEC.match(lines[i]).group(1).split(" · ")
        inv = re.fullmatch(r"(INVARIANT|PROPERTY) (\w+)", parts[-1])
        _need(inv, rel, f"section line {i + 1} does not end 'INVARIANT <P>' or 'PROPERTY <P>'")
        kind, prop = inv.group(1), inv.group(2)
        params, plain = {}, []
        for p in parts[:-1]:
            k, sep, v = p.partition("=")
            if sep and re.fullmatch(r"[A-Z]\w*", k):
                params[k] = v
            else:
                plain.append(p)
        _need(len(plain) in (1, 2), rel, f"section line {i + 1}: expected '[<Module> · ]<row>'")
        mod, name = (plain[0], plain[1]) if len(plain) == 2 else (None, plain[0])
        ok = [ln for ln in body if ln.strip() == "Model checking completed. No error has been found."]
        bad = [re.match(r"^Error: (?:Invariant|Action property) (\w+) is violated\.$|"
                        r"^Error: Temporal properties were violated\.$", ln) for ln in body]
        bad = [b for b in bad if b]
        _need(len(ok) + len(bad) == 1, rel, f"section {name}: not exactly one verdict")
        _need(not bad or bad[0].group(1) in (prop, None), rel, f"section {name}: violates another property")
        _need(not bad or kind == "PROPERTY" or bad[0].group(1) == prop, rel, f"section {name}: an invariant "
              f"section whose violation is not that invariant's")
        _need(not any(re.match(r"^Error: (?!Invariant \w+ is violated\.|Action property \w+ is violated\.|"
                               r"Temporal properties were violated\.|The behavior up to this point is:)", ln)
                      for ln in body), rel, f"section {name}: an error that is not a property's violation")
        _need(not any("Deadlock" in ln for ln in body), rel, f"section {name}: a deadlock")
        st = [_STATES.match(ln) for ln in body]
        st = [s for s in st if s]
        _need(len(st) == 1, rel, f"section {name}: not one 'states generated' line")
        rows.append(dict(module=mod, name=name, params=params, prop=prop, kind=kind,
                         verdict="HOLDS" if ok else "COUNTEREXAMPLE", states=int(st[0].group(2)),
                         left=int(st[0].group(3)), line=i + 1))
    names = [(r["module"], r["name"]) for r in rows]
    _need(len(set(names)) == len(names), rel, "a section name twice")
    if section is not None:
        rows = [r for r in rows if r["module"] == section]
        _need(rows, rel, f"no sections of {section}")
    return dict(head=head, rows=rows)


def tlc(name):
    """The module's TLC results in its file's shape, rows normalised to dict(name, mut, prop, verdict, states)
    (mut: the mutation, or the mechanism of a bare or log row that names one)."""
    m = MODULES[name]
    if m["tlc"] is None:
        return None
    if isinstance(m["tlc"], (list, tuple)):
        # one module drawn from several log files (a later run supplementing an earlier one)
        _need(m["shape"] == "log", name, "several results files must be logs")
        parts = [tlc_log(f, m["section"]) for f in m["tlc"]]
        rows = []
        for f, part in zip(m["tlc"], parts):
            for r in part["rows"]:
                r["file"] = f
                r["mut"] = r["params"].get("Mut", r["params"].get("Mech"))
                _need(r["mut"], f, f"section {r['name']} names neither Mut= nor Mech=")
                rows.append(r)
        names = [r["name"] for r in rows]
        _need(len(set(names)) == len(names), name, "a row name in two of its results files")
        return dict(head=[ln for part in parts for ln in part["head"]], heads=[part["head"] for part in parts],
                    rows=rows, file=" and ".join(m["tlc"]), files=list(m["tlc"]))
    if m["shape"] == "pipe":
        out = tlc_pipe(m["tlc"])
        _need(out["module"] == name, m["tlc"], f"is the results of {out['module']}, not {name}")
    elif m["shape"] == "bare":
        out = tlc_bare(m["tlc"])
        for r in out["rows"]:
            r["mut"] = r.pop("mech")
    else:
        out = tlc_log(m["tlc"], m["section"])
        for r in out["rows"]:
            r["mut"] = r["params"].get("Mut", r["params"].get("Mech"))
            _need(r["mut"], m["tlc"], f"section {r['name']} names neither Mut= nor Mech=")
    out["file"] = m["tlc"]
    return out


def mutations(res):
    """The mutations in the order the results first run them (none excluded)."""
    seen = []
    for r in res["rows"]:
        if r["mut"] != "none" and r["mut"] not in seen:
            seen.append(r["mut"])
    return seen


def witnesses(res, unmutated=("none",)):
    """The Never... rows: unmutated rows on a property named Never... (unmutated: the variants that are the
    mechanism as specified; a floor module's is its mechanism, `rev5`)."""
    return [r for r in res["rows"] if r["mut"] in unmutated and r["prop"].startswith("Never")]


def enclosing(rel, line):
    """The name of the top-level definition whose text holds `line` (1-based)."""
    lines = text(rel).split("\n")
    for i in range(line - 1, -1, -1):
        m = re.match(r"^([A-Za-z_]\w*)\s*(?:\([^)]*\))?\s*==", lines[i])
        if m:
            return m.group(1)
        if i < line - 1 and lines[i].strip() and not lines[i].startswith((" ", "\t")):
            break
    _need(False, rel, f"line {line} is in no top-level definition")


def code_lines_with(rel, needle):
    """The 1-based lines of the module's code (not its comments) that contain `needle`."""
    out = []
    for i, ln in enumerate(text(rel).split("\n")):
        code_part = re.sub(r"\\\*.*$", "", re.sub(r"\(\*.*?\*\)", "", ln))
        if needle in code_part:
            out.append(i + 1)
    return out


def matrix(res, key=lambda r: r["mut"]):
    """Variant x property verdicts, witnesses excluded. Returns (variants, props, cells), cells[(variant, prop)] =
    row, variants in the order first run. key: what a row's variant is (its mutation, by default; a floor module's
    variant is the entry it drops). A cell run twice raises."""
    variants, props, cells = [], [], {}
    for r in res["rows"]:
        if r["prop"].startswith("Never"):
            continue
        k = key(r)
        if k not in variants:
            variants.append(k)
        if r["prop"] not in props:
            props.append(r["prop"])
        _need((k, r["prop"]) not in cells, res["file"], f"{k} x {r['prop']} is run twice")
        cells[(k, r["prop"])] = r
    return variants, props, cells


# ---------------------------------------------------------------------------------------------- proof results
_WORDS = ("A proved obligation is a theorem of the module under its assumptions and the hypotheses the statement "
          "names; the prover, not the constants, bounds the claim. Mutations and witnesses are behaviours and stay "
          "with TLC.")


def proof_results(rel):
    """A spec/proof-results.sh file. Returns dict(module, modules {file: sha16}, prover, assumptions, theorems,
    lemmas, words, notes [lines the run printed besides its result], obligations)."""
    lines = text(rel).split("\n")
    m = re.fullmatch(r"TOPAK — TLAPS proof results for (\w+)\.tla: every obligation of (\w+)_proof\.tla, "
                     r"checked by the prover below", lines[0])
    _need(m and m.group(1) == m.group(2), rel, "line 1 is not the proof results title")
    out = dict(module=m.group(1), notes=[])
    head, i = {}, 1
    while i < len(lines) and lines[i].strip():
        k, sep, v = lines[i].partition(": ")
        if lines[i] == _WORDS:
            out["words"] = lines[i]
        else:
            _need(sep and k not in head, rel, f"bad header line {lines[i][:60]!r}")
            head[k] = v
        i += 1
    for k in ("Modules", "Prover", "Assumptions", "Theorems", "Lemmas"):
        _need(k in head, rel, f"no {k}: line")
    _need("words" in out, rel, "the words line is not the one every proof results file carries")
    out["modules"] = _shas(head["Modules"], rel, "Modules")
    out["prover"], out["assumptions"] = head["Prover"], head["Assumptions"]
    out["theorems"] = head["Theorems"].split(" · ")
    out["lemmas"] = head["Lemmas"].split(" · ")
    body = [ln for ln in lines[i:] if ln.strip()]
    res = [re.fullmatch(r"\[INFO\]: All (\d+) obligations proved\.", ln) for ln in body]
    res = [r for r in res if r]
    _need(len(res) == 1 and body[-1] == res[0].group(0), rel, "does not end with one 'All <n> obligations proved.'")
    out["obligations"] = int(res[0].group(1))
    out["notes"] = [ln for ln in body[:-1] if not ln.startswith('File "./')]
    return out


def cert_results(rel):
    """A spec/proof-cert.sh file. Returns dict(module, modules, prover, smt, total, routes [(route, n, note)],
    certified, last, ls4)."""
    lines = [ln for ln in text(rel).split("\n")]
    m = re.fullmatch(r"TOPAK — TLAPS certified proof results for (\w+)\.tla: every obligation of (\w+)_proof\.tla, "
                     r"by the route that discharged it", lines[0])
    _need(m and m.group(1) == m.group(2), rel, "line 1 is not the certified results title")
    out = dict(module=m.group(1), routes=[])
    head = {}
    for ln in lines[1:4]:
        k, sep, v = ln.partition(": ")
        _need(sep, rel, f"bad header line {ln[:60]!r}")
        head[k] = v
    for k in ("Modules", "Prover", "Checked SMT route"):
        _need(k in head, rel, f"no {k}: line")
    out["modules"] = _shas(head["Modules"], rel, "Modules")
    out["prover"], out["smt"] = head["Prover"], head["Checked SMT route"]
    t = [i for i, ln in enumerate(lines) if re.fullmatch(r"Obligations: \d+", ln)]
    _need(len(t) == 1, rel, "not one 'Obligations: <n>' line")
    out["total"] = int(lines[t[0]].split()[1])
    i = t[0] + 1
    while i < len(lines) and lines[i].startswith("  "):
        f = re.fullmatch(r"  failed / (\w+): (\d+)", lines[i])
        if f:  # obligations the certified run could not discharge, by the last backend tried
            out["routes"].append((f"failed, last backend tried: {f.group(1)}", int(f.group(2)), None))
            i += 1
            continue
        r = re.fullmatch(r"  (\S.*?\S)\s{2,}(\d+)(?:\s+\((.*)\))?", lines[i])
        _need(r, rel, f"route line does not parse: {lines[i][:70]!r}")
        out["routes"].append((r.group(1), int(r.group(2)), r.group(3)))
        i += 1
    _need(sum(n for _, n, _ in out["routes"]) == out["total"], rel, "the routes do not sum to the obligations")
    rest = [ln for ln in lines[i:] if ln.strip()]
    _need(len(rest) == 1, rel, "not one closing line")
    out["last"] = rest[0]
    ls4 = [n for r, n, _ in out["routes"] if r.startswith("LS4")]
    _need(len(ls4) == 1, rel, "no LS4 route line")
    out["ls4"] = ls4[0]
    ok = re.fullmatch(rf"All {out['total']} obligations proved\. (\d+) of them rest on tlapm's own normalization or "
                      rf"on a checked proof; (\d+) rest on LS4, whose answer no checker confirms\.", rest[0])
    if ok:
        _need(int(ok.group(1)) + int(ok.group(2)) == out["total"] and int(ok.group(2)) == out["ls4"], rel,
              "the closing line's counts do not match the routes")
        out["certified"] = True
    else:
        _need(rest[0].startswith("NOT CERTIFIED: "), rel, "the closing line is neither 'All …' nor 'NOT CERTIFIED: …'")
        out["certified"] = False
    return out


# ---------------------------------------------------------------------------------------------- Lean
_AXIOMS = re.compile(r"^info: ((?:TopakSpec|Topak)/\S+\.lean):(\d+):0: '([\w.]+)' "
                     r"(?:depends on axioms: \[(.*)\]|does not depend on any axioms)$")


def lean_results(rel):
    """A spec/lean/results.sh or mechanism/lean/results.sh file. Returns dict(title, transcribes, sources
    {path: sha16}, prover, theorems {unit: [names]}, words, axioms {qualified name: (file, line, [axioms])}, built,
    replay)."""
    lines = text(rel).split("\n")
    _need(lines[0].startswith("TOPAK — Lean results for "), rel, "line 1 is not a Lean results title")
    out = dict(title=lines[0], theorems={}, axioms={})
    for ln in lines[1:]:
        if ln.startswith("Transcribes: "):
            out["transcribes"] = _shas(ln[len("Transcribes: "):], rel, "Transcribes")
        elif ln.startswith("Sources: "):
            out["sources"] = _shas(ln[len("Sources: "):], rel, "Sources")
        elif ln.startswith("Prover: "):
            out["prover"] = ln[len("Prover: "):]
        elif ln.startswith("Theorems ("):
            m = re.fullmatch(r"Theorems \(([\w/]+)\): (.+)", ln)
            _need(m and m.group(1) not in out["theorems"], rel, f"bad Theorems line {ln[:60]!r}")
            out["theorems"][m.group(1)] = m.group(2).split(" · ")
        elif ln.startswith("A theorem holds of the "):
            out["words"] = ln
        elif ln.startswith("info: "):
            a = _AXIOMS.match(ln)
            _need(a, rel, f"an info line that is not an axiom report: {ln[:70]!r}")
            axs = [x.strip() for x in (a.group(4) or "").split(",") if x.strip()]
            _need("sorryAx" not in axs, rel, f"{a.group(3)} depends on sorryAx")
            out["axioms"][a.group(3)] = (a.group(1), int(a.group(2)), axs)
        elif ln.startswith("Build completed successfully"):
            out["built"] = ln
        elif ln.startswith("Replay: "):
            out["replay"] = ln
    for k in ("transcribes", "sources", "prover", "words", "built", "replay"):
        _need(k in out, rel, f"no {k} line")
    _need(out["replay"].endswith(", accepted"), rel, "the kernel replay is not accepted")
    return out


_GRAPH = re.compile(r"^(\w+) Mut=(\S+) \| (\d+) states · (\d+) edges · (\d+) Next steps · (\d+) initial \| (\S+)$")
_GDETAIL = re.compile(r"^  edges not Next steps: (\d+) · Next steps not TLC edges: (\d+) · Init (agrees|DIFFERS) · "
                      r"(.+)$")
_GPROP = re.compile(r"^(\w+) agrees on (\d+) of (\d+) states, false in (\d+)$")


def graph_results(rel):
    """A spec/lean/graph-check.sh file. Returns dict(transcribes, sources, checker, rows [dict(module, mut, states,
    edges, steps, initial, verdict, not_next, not_edge, init, props [(prop, agrees, of, false)])])."""
    lines = text(rel).split("\n")
    _need(lines[0].startswith("TOPAK — the Lean re-encodings checked against TLC's state graphs"), rel,
          "line 1 is not the graph-check title")
    out = dict(rows=[])
    for i, ln in enumerate(lines):
        if ln.startswith("Transcribes: "):
            out["transcribes"] = _shas(ln[len("Transcribes: "):], rel, "Transcribes")
        elif ln.startswith("Sources: "):
            out["sources"] = _shas(ln[len("Sources: "):], rel, "Sources")
        elif ln.startswith("Checker: "):
            out["checker"] = ln[len("Checker: "):]
        g = _GRAPH.match(ln)
        if g:
            d = _GDETAIL.match(lines[i + 1]) if i + 1 < len(lines) else None
            _need(d, rel, f"no detail line after {ln[:50]!r}")
            props = []
            for p in d.group(4).split(" · "):
                pm = _GPROP.fullmatch(p)
                _need(pm, rel, f"property clause does not parse: {p[:60]!r}")
                props.append((pm.group(1), int(pm.group(2)), int(pm.group(3)), int(pm.group(4))))
            out["rows"].append(dict(module=g.group(1), mut=g.group(2), states=int(g.group(3)),
                                    edges=int(g.group(4)), steps=int(g.group(5)), initial=int(g.group(6)),
                                    verdict=g.group(7), not_next=int(d.group(1)), not_edge=int(d.group(2)),
                                    init=d.group(3), props=props))
    for k in ("transcribes", "sources", "checker"):
        _need(k in out, rel, f"no {k} line")
    _need(out["rows"], rel, "no rows")
    return out


# ---------------------------------------------------------------------------------------------- one module, checked
def _git(*args):
    r = subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True)
    if r.returncode:
        raise CorpusError(f"git {' '.join(args)}: {r.stderr.strip()[:160]}")
    return r.stdout.strip()


def unchanged_since(results, module):
    """True when the last commit to touch `module` at the pin is an ancestor of the commit that added `results`:
    the module has not changed since the results file was committed. (A results file that names no digest is
    checked against its module this way, which shows order and not which text TLC ran.)"""
    p = lib.CTX.pin
    added = _git("log", "--diff-filter=A", "--format=%H", p, "--", results).split()
    last = _git("log", "-1", "--format=%H", p, "--", module)
    _need(added and last, results, "no commit history at the pin")
    return subprocess.run(["git", "-C", str(ROOT), "merge-base", "--is-ancestor", last, added[-1]]).returncode == 0


def evidence(name):
    """Everything a module's diagram draws, read and cross-checked: the digests every results file cites against
    the files at the pin, the proof results' theorems against the proof module, the certified run against the
    proof run, and the later Lean files against the cited ones for this module. Raises on any disagreement."""
    m = MODULES[name]
    mod = pathlib.PurePosixPath(m["module"]).name
    out = dict(name=name, files=m, sha={}, cited={})

    def cite(rel, sha, where):
        got = sha16(rel)
        _need(got == sha, where, f"cites {rel} as {sha}, but it is {got}")
        out["sha"][rel] = got
        out["cited"].setdefault(rel, []).append(where)

    out["sha"][m["module"]] = sha16(m["module"])
    out["tlc"] = tlc(name)
    if out["tlc"] is not None:
        files = out["tlc"].get("files") or [m["tlc"]]
        heads = out["tlc"].get("heads") or [out["tlc"].get("head", [])]
        for f, head in zip(files, heads):
            head = [ln for ln in head if isinstance(ln, str)] if isinstance(head, list) else []
            many = [ln[len("Modules: "):] for ln in head if ln.startswith("Modules: ")]
            one = [re.match(r"^Module: (\S+) \(sha256 ([0-9a-f]{16})\)", ln) for ln in head]
            one = [o for o in one if o]
            if many:
                cite(m["module"], _shas(many[0], f, "Modules").get(mod), f)
            elif one:
                _need(one[0].group(1) == mod, f, f"is a run of {one[0].group(1)}, not {mod}")
                cite(m["module"], one[0].group(2), f)
            else:
                _need(unchanged_since(f, m["module"]), f, f"{mod} changed after this file was committed")
                out["tlc"]["order_only"] = True
    if m["proof"]:
        prf = pathlib.PurePosixPath(m["proof"]).name
        pr = proof_results(m["proof_results"])
        _need(pr["module"] == name, m["proof_results"], f"is the proofs of {pr['module']}")
        cite(m["module"], pr["modules"].get(mod), m["proof_results"])
        cite(m["proof"], pr["modules"].get(prf), m["proof_results"])
        st = statements(m["proof"])
        _need([s["name"] for s in st if s["kind"] == "THEOREM"] == pr["theorems"], m["proof_results"],
              "its Theorems line is not the proof module's THEOREMs, in order")
        _need([s["name"] for s in st if s["kind"] == "LEMMA"] == pr["lemmas"], m["proof_results"],
              "its Lemmas line is not the proof module's LEMMAs, in order")
        ce = cert_results(m["cert"])
        _need(ce["module"] == name, m["cert"], f"is the certified proofs of {ce['module']}")
        cite(m["module"], ce["modules"].get(mod), m["cert"])
        cite(m["proof"], ce["modules"].get(prf), m["cert"])
        _need(ce["total"] == pr["obligations"], m["cert"], "counts other obligations than the proof run")
        out.update(proof=pr, statements=st, cert=ce)
    if m["lean"]:
        lr = lean_results(LEAN_RESULTS)
        unit = pathlib.PurePosixPath(m["lean"]).stem
        _need(unit in lr["theorems"], LEAN_RESULTS, f"no Theorems ({unit}) line")
        cite(m["module"], lr["transcribes"].get(m["module"]), LEAN_RESULTS)
        cite(m["lean"], lr["sources"].get(m["lean"]), LEAN_RESULTS)
        later = lean_results(LEAN_LATER)
        _need(later["theorems"].get(unit) == lr["theorems"][unit]
              and later["transcribes"].get(m["module"]) == lr["transcribes"][m["module"]]
              and later["sources"].get(m["lean"]) == lr["sources"][m["lean"]], LEAN_LATER,
              f"says otherwise of {unit} than {LEAN_RESULTS}")
        out["lean"] = lr
        out["lean_unit"] = unit
        if m["mirror"]:
            mu = "Mirror/" + pathlib.PurePosixPath(m["mirror"]).stem
            _need(mu in lr["theorems"], LEAN_RESULTS, f"no Theorems ({mu}) line")
            cite(m["mirror"], lr["sources"].get(m["mirror"]), LEAN_RESULTS)
            _need(later["theorems"].get(mu) == lr["theorems"][mu], LEAN_LATER, f"says otherwise of {mu}")
            out["mirror_unit"] = mu
    if m["graph"]:
        g = graph_results(GRAPH_RESULTS)
        cite(m["module"], g["transcribes"].get(m["module"]), GRAPH_RESULTS)
        cite(m["lean"], g["sources"].get(m["lean"]), GRAPH_RESULTS)
        cite(m["mirror"], g["sources"].get(m["mirror"]), GRAPH_RESULTS)
        rows = [r for r in g["rows"] if r["module"] == name]
        _need(rows, GRAPH_RESULTS, f"no rows of {name}")
        gl = graph_results(GRAPH_LATER)
        _need([r for r in gl["rows"] if r["module"] == name] == rows, GRAPH_LATER,
              f"says otherwise of {name} than {GRAPH_RESULTS}")
        out["graph"] = dict(g, rows=rows)
    return out


_TRACE = re.compile(r"^([a-z][\w-]*) \| (\d+) steps \| (MATCH|.+)$")


def trace_results(rel):
    """A spec/mechanism-trace-results.sh file. Returns dict(title, module {file: sha16}, reference, suites, words,
    tests [the cargo 'test result:' lines], rows [dict(name, steps, verdict)], traces, steps)."""
    lines = text(rel).split("\n")
    _need(lines[0].startswith("TOPAK — Mechanism.tla trace validation"), rel, "line 1 is not the trace title")
    out = dict(title=lines[0], rows=[], tests=[])
    for ln in lines[1:]:
        if ln.startswith("Module: "):
            m = re.match(r"^Module: (\S+) \(sha256 ([0-9a-f]{16})\)", ln)
            _need(m, rel, "bad Module: line")
            out["module"] = {m.group(1): m.group(2)}
        elif ln.startswith("Reference: "):
            out["reference"] = ln[len("Reference: "):]
        elif ln.startswith("Suites traced: "):
            out["suites"] = ln[len("Suites traced: "):]
        elif ln.startswith("A MATCH line means"):
            out["words"] = ln
        elif ln.startswith("test result: "):
            out["tests"].append(ln)
        else:
            t = _TRACE.match(ln)
            if t:
                out["rows"].append(dict(name=t.group(1), steps=int(t.group(2)), verdict=t.group(3)))
            elif re.fullmatch(r"\d+ traces · \d+ steps", ln.strip()):
                a, b = re.findall(r"\d+", ln)
                out["traces"], out["steps"] = int(a), int(b)
    for k in ("module", "reference", "suites", "words", "traces", "steps"):
        _need(k in out, rel, f"no {k}")
    _need(len(out["rows"]) == out["traces"] and sum(r["steps"] for r in out["rows"]) == out["steps"], rel,
          "the summary does not count the rows")
    _need(all("0 failed" in t for t in out["tests"]), rel, "a traced suite failed")
    return out
