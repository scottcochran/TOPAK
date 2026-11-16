#!/usr/bin/env python3
"""The specification graph and its checker (ADR-0057, Proposed).

The graph (`spec/specification-graph.json`) holds the corpus's artifacts as nodes, each with a layer (§1), and typed
edges between them (§3): an edge runs from a lower node to the node it discharges, says how, by one of eight types
ordered by what it leaves to a person, and pins the content it relates. Each edge contributes a premise (§4); the
graph also holds ADR-0053's derived premises re-expressed over those premises, and T-0045-28 as a derived premise of
every theorem (§4). This script builds the graph from the tree and the evidence the corpus already keeps, and checks
it.

    specification-graph.py build [--repin ID ...] [--repin-all]
        Writes the graph. An edge already in the graph keeps its pins, its evidence file and anything written into it
        by hand (a reader, a note): re-pinning is the review, as `drift.rs` asks of its pins (§3). `--repin` takes an
        edge's pins afresh, from its evidence where it has one and from the tree where it has none. A new edge is
        pinned the same way. An edge whose basis is gone is dropped and named.
    specification-graph.py check [--strict]
        The checker (§8). Prints, in order: every stale edge; the clauses the reference follows that no model reads,
        and what each replay's model does not read; every guarantee stated twice (§6); the modules no theorem in the
        binding is checked in; each module's edges up (§5); the four lists read against the graph (§8); the
        inventory at grade *trusted* against `inventory.py`'s for the reference's declaration, theorem by theorem,
        and `premise-routes.sh`'s five declarations against the graph's; and the inventory at every grade, with each
        theorem's grade and the route that carried it (§5). Exits 1 if the graph is malformed, a list disagrees with
        it, or the inventory at grade *trusted* differs from `inventory.py`'s for Annex B. Stale edges and a premise
        route that differs are reported, not failed on (`--strict` fails on both).

**Pins** (§3). An edge with a results file pins what that file records, both ends and the file itself: the digests
its header prints, or the commit it names (`git <commit> <path>`: fresh while nothing under the path differs from that
commit). An executed edge pins the digest the code pins (`const`) and the file the code links (`include`). An edge
with no results file pins the tree at the review that last pinned it: a read edge from a module pins both ends; a
read edge from the reference pins what was read, by clause for a record and by file for a module, as
`corpus-pins.sha256` does (the code moves on every commit and is reviewed by commit); a trusted edge pins the node the
row vouches for, since its lower end is a row and not content. A record's clauses are pinned by `clauses.py` (§7).

**Premises** (§4). An edge's premise is `edge(<type>, <from> → <to>)`, or, where ADR-0053 R7 already named the
premise, that name (`enc-faithful(Seats)`, `model-faithful(apply/Seats)`): its value is then the column's own (its
check, or its declaration) and the edge's freshness. Otherwise it is the edge's freshness and its results file's
verdict; a trusted edge's is its row's class and its freshness. **At grade *g*** every edge premise of a type weaker
than *g* is false (§5); rows, parameters and gap premises do not grade. Evaluation is `inventory.py`'s, imported, not
changed.
"""
import glob
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
GRAPH = os.path.join(HERE, "specification-graph.json")
BINDING = os.path.join(HERE, "theorem-premise-binding.json")
ADR45 = os.path.join(ROOT, "decisions", "ADR-0045.md")

sys.path.insert(0, HERE)
import clauses as C  # noqa: E402

_spec = importlib.util.spec_from_file_location("inventory", os.path.join(HERE, "inventory.py"))
inv = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(inv)

TYPES = ["executed", "generated", "proved", "proved of a reading", "replayed", "tested", "read", "trusted"]
LEAVES = {
    "executed": "the engine that runs it (a row)",
    "generated": "the generator",
    "proved": "the prover or kernel (a row)",
    "proved of a reading": "the reading (enc-faithful, model-faithful), which a check may support",
    "replayed": "the paths no trace reached",
    "tested": "the inputs no test chose, and whether the tests state the properties",
    "read": "the reader",
    "trusted": "the row",
}
LAYERS = {
    "intent": "The ToO's principles and threat model; ADR-0025's intent",
    "vocabulary": "narrative/glossary.md",
    "record": "decisions/, and the checkpoint that is the state of record",
    "assurance": "ADR-0045 Annex A and B; the binding table; the residual-risk statement",
    "model": "spec/*.tla; the proof modules; spec/lean/",
    "interface": "Schema S; the allowlist entry (ADR-0049); every format the format inventory lists",
    "policy": "floor/ and its stages; policies/",
    "implementation": "mechanism/ crates; mechanism/lean/, as a transcription of them",
    "runtime": "Recorded traces; the trace-validation results",
    "deployment": "A deployment's declaration (ADR-0058)",
}
# Theorems the binding checks in no module: the node each is stated at (the drafter's reading of the binding's
# "Record" and "Checked in" columns).
STATED_AT = {
    "Effect exclusivity": ["ADR-0015"],
    "PromotionMeetsIssuedQuorum": ["ADR-0024"],
    "OneValuePerBallot": ["ADR-0033 §2"],
    "floor gates": ["floor/proposed/workflow-floor.cedar"],
    "TraceMatches": ["spec/Mechanism.tla", "spec/ConfinementRefinement.tla"],
}
# Guarantees stated twice or more (§6): where each statement is. The checker lists the edge, or the lack of one,
# between every pair.
RESTATES = [{
    "guarantee": "the operator's envelope, C1 to C9 (ADR-0050 §4; mechanism/ I47 (e))",
    "statements": [
        {"node": "floor/proposed/workflow-floor.cedar", "where": "entries C1 to C9, for the decision"},
        {"node": "mechanism/crates/topak-core", "where": "control.rs ControlFacts::permitted, restated at apply"},
        {"node": "spec/Mechanism.tla", "where": "the control entry, restated on every traced request"},
    ],
}]
TROW = re.compile(r"T-0045-\d+$")
CLAUSE_KEY = re.compile(r"^(ADR-\d{4}) (.+)$")


# ---------------------------------------------------------------------------------------------------------------------
# The tree


def rel(p):
    return os.path.relpath(p, ROOT)


def d16(path):
    full = os.path.join(ROOT, path)
    if not os.path.isfile(full):
        return None
    return hashlib.sha256(open(full, "rb").read()).hexdigest()[:16]


def git(*args):
    return subprocess.run(["git", "-C", ROOT, *args], capture_output=True, text=True).stdout


def tracked(prefix):
    out = git("ls-files", "-co", "--exclude-standard", "--", prefix).split("\n")
    return sorted(p for p in out if p and "/target/" not in p and os.path.isfile(os.path.join(ROOT, p)))


def dir_d16(prefix):
    h = hashlib.sha256()
    for p in tracked(prefix):
        h.update(f"{d16(p)}  {p}\n".encode())
    return h.hexdigest()[:16]


_clause_cache = {}


def record_path(rec):
    return f"decisions/{rec}.md"


def record_clauses(rec, text=None):
    """{clause id: pin} for a record, from the tree or from a given text."""
    if text is None and rec in _clause_cache:
        return _clause_cache[rec]
    path = os.path.join(ROOT, record_path(rec))
    if text is not None:
        return {cid: pin for cid, _h, pin in C.clauses_of(text)}
    out = {cid: pin for cid, _h, pin in C.clauses(path)} if os.path.isfile(path) else {}
    _clause_cache[rec] = out
    return out


def clause_headings(rec):
    path = os.path.join(ROOT, record_path(rec))
    return {cid: h for cid, h, _ in C.clauses(path)} if os.path.isfile(path) else {}


def record_at_digest(path, digest):
    """The text of a file as it was when its sha256 was `digest`, from git history; None if never."""
    full = os.path.join(ROOT, path)
    if os.path.isfile(full) and hashlib.sha256(open(full, "rb").read()).hexdigest() == digest:
        return open(full, encoding="utf-8").read()
    for c in git("log", "--format=%H", "--", path).split():
        blob = subprocess.run(["git", "-C", ROOT, "show", f"{c}:{path}"], capture_output=True).stdout
        if hashlib.sha256(blob).hexdigest() == digest:
            return blob.decode("utf-8")
    return None


# ---------------------------------------------------------------------------------------------------------------------
# Evidence: the results files the corpus already keeps


def newest(pattern):
    files = sorted(glob.glob(os.path.join(ROOT, pattern)))
    return rel(files[-1]) if files else None


DIGEST_LINE = re.compile(r"^(Transcribes|Floor|Sources|Model|Reference|Modules|Module):")
NAMED = re.compile(r"([A-Za-z0-9_./-]+) \(sha256 ([0-9a-f]{16})")


def recorded(results, keep=None):
    """{repository path: digest16} that a results file's header records, resolved against the tree."""
    out = {}
    base = os.path.dirname(results)
    for line in open(os.path.join(ROOT, results), encoding="utf-8"):
        if not DIGEST_LINE.match(line):
            continue
        for name, dig in NAMED.findall(line):
            cands = [name] if "/" in name else [os.path.join(base, name), "spec/" + name, "floor/" + name]
            path = next((c for c in cands if os.path.isfile(os.path.join(ROOT, c))), None)
            if path and (keep is None or keep(path)):
                out[os.path.normpath(path)] = dig
    return out


def verdict(results, spec):
    """(ok, why) of a results file's verdict lines."""
    text = open(os.path.join(ROOT, results), encoding="utf-8").read().splitlines()
    if "line" in spec:
        ok = any(re.search(spec["line"], ln) for ln in text)
        return ok, ("verdict line present" if ok else f"no line {spec['line']!r}")
    picked = [ln for ln in text if re.search(spec["lines"], ln)]
    if not picked:
        return False, f"no line {spec['lines']!r}"
    bad = [ln for ln in picked if not ln.rstrip().endswith(spec["want"])]
    if bad:
        return False, f"{len(bad)} of {len(picked)} lines not {spec['want']!r}"
    return True, f"{len(picked)} of {len(picked)} lines {spec['want'].strip(' |')}"


V_TLAPS = {"line": r"^\[INFO\]: All \d+ obligations proved\.$"}
V_LEAN = {"line": r"^Replay: leanchecker --fresh \w+: .*accepted$"}
V_REPLAY = {"line": r"^\d+ traces · \d+ steps · 0 not matching$"}
V_TRACE = {"lines": r" \| \d+ steps \| ", "want": "MATCH"}
V_GATES = {"line": r"^RESULT: all gates pass$"}


def lean_imports(path, pkg_dir, prefix):
    """The Lean files a file imports within its package, transitively, itself included."""
    seen, todo = set(), [path]
    while todo:
        p = todo.pop()
        if p in seen or not os.path.isfile(os.path.join(ROOT, p)):
            continue
        seen.add(p)
        for m in re.findall(rf"^import {prefix}\.([\w.]+)", open(os.path.join(ROOT, p), encoding="utf-8").read(), re.M):
            todo.append(f"{pkg_dir}/{prefix}/{m.replace('.', '/')}.lean")
    return seen


# ---------------------------------------------------------------------------------------------------------------------
# Citations


def code_sources(crate_dir):
    out = []
    for dp, dns, fns in os.walk(os.path.join(ROOT, crate_dir)):
        dns[:] = [d for d in dns if d != "target"]
        for f in fns:
            if f.rsplit(".", 1)[-1] in ("rs", "toml", "sh", "py"):
                out.append(os.path.join(dp, f))
    return sorted(out)


def code_citations(text):
    """What `drift.rs` counts as a citation: ADR-NNNN, and Name.tla where spec/Name.tla exists."""
    found = {f"decisions/ADR-{n}.md" for n in re.findall(r"ADR-(\d{4})", text)}
    for m in re.finditer(r"([A-Za-z0-9_]+)\.tla", text):
        if os.path.isfile(os.path.join(ROOT, "spec", m.group(1) + ".tla")):
            found.add(f"spec/{m.group(1)}.tla")
    return found


def module_citations(path):
    """(record, clause or None) a module's text cites: `ADR-NNNN`, with the first `§N` that follows it."""
    text = open(os.path.join(ROOT, path), encoding="utf-8").read()
    out = set()
    for m in re.finditer(r"ADR-(\d{4})((?:\s*(?:A\d+\s*)?§\s*\d+[a-z]?)?)", text):
        sec = re.search(r"§\s*(\d+[a-z]?)", m.group(2))
        out.add((f"ADR-{m.group(1)}", f"§{sec.group(1)}" if sec else None))
    return out


# ---------------------------------------------------------------------------------------------------------------------
# Build


def premise_name(t, a, b):
    return f"edge({t}, {a} → {b})"


def edge_id(t, a, b):
    return f"{t}: {a} → {b}"


class Builder:
    def __init__(self):
        self.nodes, self.edges = {}, {}
        self.binding = json.load(open(BINDING))
        self.pins = {}
        for line in open(os.path.join(ROOT, "mechanism", "corpus-pins.sha256")):
            if line.strip():
                dig, path = line.split("  ", 1)
                self.pins[path.strip()] = dig.strip()

    # nodes -------------------------------------------------------------------------------------------------------
    def node(self, nid, layer, path=None, **kw):
        if nid not in self.nodes:
            n = {"id": nid, "layer": layer}
            if path:
                n["path"] = path
            n.update(kw)
            self.nodes[nid] = n
        return nid

    def record(self, rec):
        if not os.path.isfile(os.path.join(ROOT, record_path(rec))):
            return None
        self.node(rec, "record", record_path(rec), clauses=list(record_clauses(rec)))
        for cid in record_clauses(rec):
            layer = "assurance" if rec == "ADR-0045" and cid.startswith("Annex") else "record"
            self.node(f"{rec} {cid}", layer, record_path(rec), clause=cid, of=rec)
        return rec

    def clause(self, rec, cid):
        """The clause node for a citation, or the record's node when the clause is not one of its clauses."""
        if not self.record(rec):
            return None
        return f"{rec} {cid}" if cid and cid in record_clauses(rec) else rec

    def file(self, path, layer):
        return self.node(path, layer, path)

    # edges -------------------------------------------------------------------------------------------------------
    def edge(self, t, a, b, pins, evidence=None, alias=None, leaves=None, **kw):
        assert t in TYPES, t
        eid = edge_id(t, a, b)
        e = {"id": eid, "type": t, "from": a, "to": b, "premise": alias or premise_name(t, a, b),
             "leaves": leaves or LEAVES[t], "pins": dict(sorted(pins.items()))}
        if evidence:
            e["evidence"] = evidence
        e.update(kw)
        self.edges[eid] = e
        return e

    def upper_pins(self, node_id):
        """Pins of an upper end from the tree: a clause, a record's every clause, a file or a directory."""
        n = self.nodes[node_id]
        if "clause" in n:
            return {node_id: record_clauses(n["of"])[n["clause"]]}
        if n["layer"] == "record" and n.get("clauses") is not None:
            return {f"{node_id} {c}": p for c, p in record_clauses(node_id).items()}
        p = n["path"]
        if os.path.isdir(os.path.join(ROOT, p)):
            return {p + "/": dir_d16(p)}
        return {p: d16(p)}

    # rules -------------------------------------------------------------------------------------------------------
    def build(self):
        self.node("mechanism", "implementation", "mechanism", note="the reference as a whole: its crates, scripts and register")
        crates = sorted(d for d in os.listdir(os.path.join(ROOT, "mechanism", "crates")) if not d.startswith("."))
        for c in crates:
            self.node(f"mechanism/crates/{c}", "implementation", f"mechanism/crates/{c}")
        self.node("mechanism/scripts", "implementation", "mechanism/scripts")
        modules = sorted(rel(p) for p in glob.glob(os.path.join(HERE, "*.tla")) if not os.path.basename(p).startswith("Trace_"))
        for m in modules:
            self.file(m, "model")
        self.node("spec/theorem-premise-binding.md", "assurance", "spec/theorem-premise-binding.md")
        self.node("spec/theorem-premise-binding.json", "assurance", "spec/theorem-premise-binding.json")

        self.rule_tlaps(modules)
        self.rule_spec_lean()
        self.rule_mechanism_lean()
        self.rule_traces()
        self.rule_floor()
        self.rule_tested(crates)
        self.rule_reference_reads(crates)
        self.rule_module_reads(modules)
        self.rule_assurance()
        self.rule_trusted()
        self.re_express()

    def rule_tlaps(self, modules):
        for pm in [m for m in modules if m.endswith("_proof.tla")]:
            name = os.path.basename(pm)[:-len("_proof.tla")]
            res = newest(f"spec/{name}-proof-results-*.txt")
            if not res:
                continue
            target = f"spec/{name}.tla"
            pins = recorded(res)
            pins[res] = d16(res)
            self.edge("proved", pm, target, pins, leaves="T-0045-31 (the prover)", row="T-0045-31",
                      evidence={"results": f"spec/{name}-proof-results-*.txt", "file": res, "verdict": V_TLAPS})

    def encoding_of(self, m):
        p = f"spec/lean/TopakSpec/{m}.lean"
        if os.path.isfile(os.path.join(ROOT, p)):
            return p
        spec = self.binding["premises"].get(f"enc-faithful({m})", {})
        found = re.findall(r"spec/lean/TopakSpec/[\w/]+\.lean", spec.get("text", ""))
        if found:
            return found[0]
        if "_" in m:  # a successor or a liveness module encoded beside its base (Emergency_live in Emergency.lean)
            return self.encoding_of(m.rsplit("_", 1)[0])
        return None

    def rule_spec_lean(self):
        res = newest("spec/lean/TopakSpec-results-*.txt")
        allpins = recorded(res)
        shared = {p for p in allpins if not p.startswith("spec/lean/TopakSpec/") and not p.startswith("spec/") or
                  p.startswith("spec/lean/") and not p.startswith("spec/lean/TopakSpec/")}
        for path in sorted(allpins):
            m = re.fullmatch(r"spec/(\w+)\.tla", path)
            if not m:
                continue
            enc = self.encoding_of(m.group(1))
            if not enc:
                continue
            self.file(enc, "model")
            deps = lean_imports(enc, "spec/lean", "TopakSpec")
            pins = {p: d for p, d in allpins.items() if p == path or p in deps or p in shared}
            pins[res] = d16(res)
            self.edge("proved of a reading", enc, path, pins, row="T-0045-37",
                      leaves=f"T-0045-37 (the kernel) and the reading enc-faithful({m.group(1)})",
                      evidence={"results": "spec/lean/TopakSpec-results-*.txt", "file": res, "verdict": V_LEAN})
            col = self.binding["premises"].get(f"enc-faithful({m.group(1)})")
            if col and col.get("kind") == "condition":
                # the reading the edge leaves, as ADR-0053 R7 named it: read by someone other than the drafter, or not
                self.edge("read", enc, path, {path: allpins[path], enc: allpins.get(enc) or d16(enc)},
                          alias=f"enc-faithful({m.group(1)})", reader="none yet: the premise asks for someone other "
                          "than the drafter (ADR-0053 §5 R1(b)); a declaration sets it")
        for series, glob_, label in (("GraphCheck", "spec/lean/GraphCheck-results-*.txt", None),
                                     ("GraphCheckEmergency", "spec/lean/GraphCheckEmergency-results-*.txt", None)):
            res = newest(glob_)
            if not res:
                continue
            allpins = recorded(res)
            mods = [p for p in allpins if re.fullmatch(r"spec/\w+\.tla", p)]
            stem = lambda q: re.fullmatch(r"spec/(\w+)\.tla", q).group(1)  # noqa: E731
            for path in mods:
                name = stem(path)
                enc = self.encoding_of(name)
                self.file(enc, "model")
                others = {self.encoding_of(stem(q)) for q in mods if q != path}
                others |= {"spec/lean/TopakSpec/Mirror/" + stem(q) + ".lean" for q in mods if q != path}
                pins = {p: d for p, d in allpins.items() if p not in others and not (p.startswith("spec/") and p.endswith(".tla") and p != path)}
                pins[res] = d16(res)
                col = self.binding["premises"].get(f"enc-faithful({name})")
                alias = f"enc-faithful({name})" if col and col.get("kind") == "check" else None
                self.edge("proved", enc, path, pins, alias=alias, row="T-0045-37",
                          leaves="T-0045-37 and TLC: equal state graphs on the checked instance, under every Mut",
                          evidence={"results": glob_, "file": res,
                                    "verdict": {"lines": rf"^{name} Mut=", "want": "| MATCH"}})

    def rule_mechanism_lean(self):
        res = newest("mechanism/lean/Admit-results-*.txt")
        allpins = recorded(res)
        allpins[res] = d16(res)
        ev = {"results": "mechanism/lean/Admit-results-*.txt", "file": res, "verdict": V_LEAN}
        core = "mechanism/crates/topak-core"
        for lean in ("Admit", "Clock", "FloorRefinement", "SeatsModel", "CouplingModel"):
            self.file(f"mechanism/lean/Topak/{lean}.lean", "implementation")
        self.edge("proved of a reading", core, "spec/FloorComposition.tla", allpins, evidence=ev, row="T-0045-37",
                  via="mechanism/lean/Topak/Admit.lean, FloorRefinement.lean (codeDecide_refines)",
                  route=False, note="the code's decision is a Decide step of the module: a step, not the module's "
                  "behaviours; not a route of T-0045-28 (ADR-0057 §4: today the row is the only route but for Seats)",
                  leaves="T-0045-37 and the reading: the transcriptions of admit.rs, the topak-floor wrapper and mechanism.rs")
        self.edge("proved of a reading", core, "spec/Seats.tla", allpins, evidence=ev, row="T-0045-37",
                  via="mechanism/lean/Topak/SeatsModel.lean (model_refines_seats)",
                  leaves="T-0045-37 and the reading model-faithful(apply/Seats)")
        self.record("ADR-0039")
        self.edge("proved of a reading", core, "ADR-0039 §2", allpins, evidence=ev, row="T-0045-37",
                  via="mechanism/lean/Topak/CouplingModel.lean", route=False,
                  leaves="T-0045-37 and the reading: the Coupling-shaped model of State::apply")
        self.record("ADR-0032")
        self.edge("proved of a reading", core, "ADR-0032 §2", allpins, evidence=ev, row="T-0045-37",
                  via="mechanism/lean/Topak/Clock.lean", route=False,
                  leaves="T-0045-37 and the reading: the transcription of clock.rs")
        for series, model, alias in (("SeatsReplay", "SeatsModel", "model-faithful(apply/Seats)"),
                                     ("CouplingReplay", "CouplingModel", None)):
            res = newest(f"mechanism/lean/{series}-results-*.txt")
            pins = recorded(res)
            pins[res] = d16(res)
            self.edge("replayed", core, f"mechanism/lean/Topak/{model}.lean", pins, alias=alias,
                      evidence={"results": f"mechanism/lean/{series}-results-*.txt", "file": res, "verdict": V_REPLAY})

    def rule_traces(self):
        res = newest("spec/Mechanism-trace-results-*.txt")
        text = open(os.path.join(ROOT, res), encoding="utf-8").read()
        commit = re.search(r"^Reference: mechanism/ at (\w+)", text, re.M).group(1)
        pins = recorded(res)
        pins[res] = d16(res)
        for c in ("topak-core", "topak-node"):
            pins[f"git {commit} mechanism/crates/{c}"] = "unchanged"
        dirty = "+ working tree" in text.splitlines()[2]
        ev = {"results": "spec/Mechanism-trace-results-*.txt", "file": res, "verdict": V_TRACE}
        note = "recorded on a working tree over the commit it names" if dirty else None
        self.edge("replayed", "mechanism/crates/topak-core", "spec/Mechanism.tla", pins, evidence=ev,
                  **({"note": note} if note else {}))
        p2 = dict(pins)
        p2["spec/ConfinementRefinement.tla"] = d16("spec/ConfinementRefinement.tla")
        self.edge("replayed", "mechanism/crates/topak-core", "spec/ConfinementRefinement.tla", p2, evidence=ev,
                  **({"note": note + "; the module's digest is the tree's at the first build (the results file "
                      "names Mechanism.tla only)"} if note else {}))

    def rule_floor(self):
        lib = "mechanism/crates/topak-floor/src/lib.rs"
        src = open(os.path.join(ROOT, lib), encoding="utf-8").read()
        inc = {k: v for k, v in re.findall(r'pub const (\w+_SRC): &str = include_str!\("(?:\.\./)*([^"]+)"\)', src)}
        const = dict(re.findall(r'pub const (PINNED_\w+_SHA256): &str = "([0-9a-f]{64})"', src))
        self.file("floor/genesis-floor.cedar", "policy")
        stages = re.search(r'STAGES = \[([^\]]+)\]', open(os.path.join(ROOT, "floor/proposed/build.py")).read()).group(1)
        stages = re.findall(r'"(\w+)"', stages)
        for s in stages:
            self.file(f"floor/proposed/{s}-floor.cedar", "policy")
        linked = inc["FLOOR_SRC"]
        pins = {}
        for k, c in (("FLOOR_SRC", "PINNED_FLOOR_SHA256"), ("SCHEMA_SRC", "PINNED_SCHEMA_SHA256"),
                     ("VALUES_SRC", "PINNED_VALUES_SHA256")):
            pins[f"include {lib} {k}"] = inc[k]
            pins[f"const {lib} {c}"] = const[c][:16]
            pins[inc[k]] = const[c][:16]
        self.edge("executed", "mechanism/crates/topak-floor", linked, pins, row="T-0045-3",
                  leaves="T-0045-3 (the Cedar engine)", route=False,
                  note="the reference links the stage verbatim and refuses to start on another digest; the stage is "
                  "not the floor in force (G11 item 102; ADR-0057 finding 6). Not a route of T-0045-28 (§4)")
        gen = "floor/proposed/build.py"
        for s in stages:
            st = f"floor/proposed/{s}-floor.cedar"
            pins = {p: d16(p) for p in (gen, "floor/genesis-floor.cedar", "floor/genesis.cedarschema", st,
                                         f"floor/proposed/{s}.cedarschema", f"floor/proposed/{s}-tests.json")}
            self.edge("generated", st, "floor/genesis-floor.cedar", pins, leaves="the generator, floor/proposed/build.py")
        self.record("ADR-0030")
        for st, pattern in [("floor/genesis-floor.cedar", "floor/genesis-gates-results-*.txt")] + \
                [(f"floor/proposed/{s}-floor.cedar", f"floor/proposed/{s}-gates-results-*.txt") for s in stages]:
            res = newest(pattern)
            if not res:
                continue
            pins = recorded(res)
            pins[res] = d16(res)
            self.edge("proved", st, "ADR-0030 §5", pins, row="T-0045-14",
                      leaves="T-0045-14 (cvc5 under the ethos checker)",
                      evidence={"results": pattern, "file": res, "verdict": V_GATES})
        res = newest("floor/lean/TopakFloor-results-*.txt")
        allpins = recorded(res)
        allpins[res] = d16(res)
        self.node("floor/lean", "policy", "floor/lean", note="the floor stated in Lean under cedar-spec's model")
        line = next(ln for ln in open(os.path.join(ROOT, res), encoding="utf-8") if ln.startswith("Floor:"))
        for p in sorted(set(re.findall(r"(floor/[\w/-]+-floor\.cedar|floor/genesis-floor\.cedar)", line))):
            self.edge("proved", "floor/lean", p, allpins, row="T-0045-37",
                      leaves="T-0045-37 (the kernel), cedar-spec's model of Cedar, and gen.py's walk of the parser's output",
                      evidence={"results": "floor/lean/TopakFloor-results-*.txt", "file": res, "verdict": V_LEAN})

    def rule_tested(self, crates):
        for c in crates:
            for tf in sorted(glob.glob(os.path.join(ROOT, "mechanism", "crates", c, "tests", "*.rs"))):
                if tf.endswith("drift.rs"):
                    continue
                head = []
                for ln in open(tf, encoding="utf-8"):
                    if not ln.startswith("//!"):
                        break
                    head.append(ln)
                for m in sorted(code_citations("".join(head)) - {p for p in code_citations("".join(head)) if p.startswith("decisions/")}):
                    if m in ("spec/Mechanism.tla",):
                        continue
                    t = rel(tf)
                    self.edge("tested", f"mechanism/crates/{c}", m, {t: d16(t), m: d16(m)},
                              evidence={"tests": t}, reader="the drafter: the tests are named after the module's properties")
        tests = ["mechanism/crates/topak-core/tests/operators.rs", "mechanism/crates/topak-node/tests/e2e.rs"]
        st = "floor/proposed/workflow-floor.cedar"
        pins = {t: d16(t) for t in tests}
        pins[st] = d16(st)
        self.edge("tested", "mechanism/crates/topak-core", st, pins, evidence={"tests": ", ".join(tests)},
                  restates=RESTATES[0]["guarantee"],
                  note="nothing checks the Rust restatement against the Cedar entries but the tests (I47 (e))")

    def rule_reference_reads(self, crates):
        cites = {}
        for c in crates + ["../scripts"]:
            node = f"mechanism/crates/{c}" if c != "../scripts" else "mechanism/scripts"
            for f in code_sources(f"mechanism/crates/{c}" if c != "../scripts" else "mechanism/scripts"):
                for p in code_citations(open(f, encoding="utf-8", errors="replace").read()):
                    cites.setdefault(p, set()).add(node)
        for path, dig in sorted(self.pins.items()):
            lowers = sorted(cites.get(path, set())) or ["mechanism"]
            if path.startswith("decisions/"):
                rec = os.path.basename(path)[:-3]
                text = record_at_digest(path, dig)
                if not self.record(rec):
                    continue
                cl = record_clauses(rec, text) if text is not None else {}
                pins = {f"{rec} {c}": p for c, p in cl.items()} or {f"{rec} ?": "the pinned text is not in history"}
                upper = rec
            else:
                pins = {path: dig[:16]}
                upper = self.file(path, "model")
            for low in lowers:
                self.edge("read", low, upper, pins, reader="the drafter", pinned_by="mechanism/corpus-pins.sha256",
                          cited=("by the code" if low != "mechanism" else "pinned, cited by no source file"))

    def rule_module_reads(self, modules):
        for m in modules:
            if m.endswith("_proof.tla"):
                continue
            seen = set()
            for rec, cid in sorted(module_citations(m), key=lambda x: (x[0], x[1] or "")):
                tgt = self.clause(rec, cid)
                if not tgt or tgt in seen:
                    continue
                seen.add(tgt)
                pins = {m: d16(m)}
                pins.update(self.upper_pins(tgt))
                self.edge("read", m, tgt, pins, reader="the drafter")

    def rule_assurance(self):
        self.record("ADR-0045")
        b = "spec/theorem-premise-binding.md"
        pins = {b: d16(b)}
        pins.update(self.upper_pins("ADR-0045 Annex A"))
        self.edge("read", b, "ADR-0045 Annex A", pins, reader="the drafter")
        j = "spec/theorem-premise-binding.json"
        self.edge("read", j, b, {j: d16(j), b: d16(b)}, reader="the drafter",
                  note="its row premises are checked against the table at every rung by inventory.py --check; its "
                  "other columns are transcribed")

    def theorem_targets(self, t):
        if t.get("proved_in"):
            return [f"spec/{p[:-len('_proof.tla')]}.tla" for p in t["proved_in"]]
        for k, v in STATED_AT.items():
            if k in t["names"]:
                return v
        return None

    def rule_trusted(self):
        self.trusted_for = {}
        for t in self.binding["theorems"]:
            targets = self.theorem_targets(t)
            if not targets:
                sys.exit(f"specification-graph.py: no node for {t['names']}; add it to STATED_AT")
            nodes = []
            for tgt in targets:
                if tgt.startswith("ADR-"):
                    rec, _, cid = tgt.partition(" ")
                    tgt = self.clause(rec, cid or None)
                elif tgt not in self.nodes:
                    self.file(tgt, "policy" if tgt.startswith("floor/") else "model")
                self.edge("trusted", "mechanism", tgt, self.upper_pins(tgt), row="T-0045-28",
                          leaves="T-0045-28: the running code refines the checked specification; no edge exists")
                nodes.append(tgt)
            self.trusted_for[tuple(t["names"])] = nodes

    def re_express(self):
        """ADR-0053's derived premises over edge premises, and T-0045-28 as a derived premise of every theorem (§4)."""
        der = {}
        by_alias = {e["premise"]: e for e in self.edges.values()}

        def find(t, a, b):
            e = self.edges.get(edge_id(t, a, b))
            return e["premise"] if e else None

        for name, spec in self.binding["derived"].items():
            m = re.fullmatch(r"invariant\((\w+)\)", name)
            routes = []
            for route in spec["any_of"]:
                r = list(route)
                if m and "T-0045-31" in r:
                    p = find("proved", f"spec/{m.group(1)}_proof.tla", f"spec/{m.group(1)}.tla")
                    if not p:
                        sys.exit(f"specification-graph.py: no TLAPS edge for {name}")
                    r.append(p)
                if m and "T-0045-37" in r:
                    enc = self.encoding_of(m.group(1))
                    p = find("proved of a reading", enc, f"spec/{m.group(1)}.tla")
                    if not p:
                        sys.exit(f"specification-graph.py: no Lean edge for {name}")
                    r.insert(r.index("T-0045-37") + 1, p)
                if name == "refines(Seats)":
                    if r == ["T-0045-28"]:
                        r = [find("trusted", "mechanism", "spec/Seats.tla")]
                    elif "T-0045-37" in r:
                        r.insert(1, find("proved of a reading", "mechanism/crates/topak-core", "spec/Seats.tla"))
                routes.append(r)
            der[name] = {"any_of": routes, "re-expresses": spec["any_of"]}
            if spec.get("corrects"):
                der[name]["corrects"] = spec["corrects"]
            if name == "refines(Seats)":
                der[name]["corrects"] = ("T-0045-28 is the row of the trusted edge from the code to Seats.tla, which "
                                         "stands where its route was (ADR-0057 §4)")
        replaces = []
        for t in self.binding["theorems"]:
            rep = dict(t.get("replaces", {}))
            if "T-0045-28" not in rep:
                targets = self.trusted_for[tuple(t["names"])]
                names = []
                for tgt in targets:
                    n = f"reaches-code({tgt})"
                    der.setdefault(n, {"any_of": [[find("trusted", "mechanism", tgt)]],
                                       "corrects": "T-0045-28 is the row of the trusted edge from the code to the node "
                                                   "the theorem is stated at (ADR-0057 §4); today it is the only route"})
                    names.append(n)
                if len(names) == 1:
                    rep["T-0045-28"] = names[0]
                else:
                    n = f"reaches-code({', '.join(targets)})"
                    der.setdefault(n, {"any_of": [names], "corrects": "every module the row is checked in"})
                    rep["T-0045-28"] = n
            replaces.append({"names": t["names"], "replaces": rep})
        for e in self.edges.values():
            assert e["premise"] in by_alias
        self.binding_out = {"derived": der, "replaces": replaces}


def build(argv):
    repin = set()
    repin_all = "--repin-all" in argv
    if "--repin" in argv:
        i = argv.index("--repin")
        repin = set(argv[i + 1:])
    b = Builder()
    b.build()
    old = json.load(open(GRAPH)) if os.path.isfile(GRAPH) else {"edges": []}
    old_edges = {e["id"]: e for e in old["edges"]}
    kept = new = repinned = 0
    edges = []
    for eid in sorted(b.edges):
        e = b.edges[eid]
        o = old_edges.get(eid)
        if o and not repin_all and eid not in repin:
            merged = dict(e)
            for k in ("pins", "evidence", "reader", "note", "reviewed"):
                if k in o:
                    merged[k] = o[k]
            edges.append(merged)
            kept += 1
        else:
            if o:
                repinned += 1
            else:
                new += 1
            edges.append(e)
    gone = sorted(set(old_edges) - set(b.edges))
    head = git("rev-parse", "--short", "HEAD").strip()
    dirty = git("status", "--porcelain", "--", "spec", "decisions", "floor", "mechanism").strip()
    graph = {
        "_about": "The specification graph (ADR-0057, Proposed): the corpus's artifacts as nodes with an open set of "
                  "layers (§1), typed edges between them, each pinned and each contributing a premise (§3, §4), "
                  "ADR-0053's derived premises re-expressed over those premises and T-0045-28 as a derived premise of "
                  "every theorem (§4). Built and checked by spec/specification-graph.py; a record's clauses are "
                  "pinned by spec/clauses.py (§7). The binding table stays canonical for its row premises.",
        "record": "ADR-0057",
        "built": {"at": head + (" + working tree" if dirty else "")},
        "types": [{"type": t, "leaves": LEAVES[t]} for t in TYPES],
        "layers": LAYERS,
        "nodes": [b.nodes[k] for k in sorted(b.nodes)],
        "edges": edges,
        "restates": RESTATES,
        "binding": b.binding_out,
    }
    if gone:
        graph["dropped"] = gone
    json.dump(graph, open(GRAPH, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    open(GRAPH, "a").write("\n")
    print(f"{len(b.nodes)} nodes, {len(edges)} edges: {kept} kept with their pins, {repinned} re-pinned, {new} new"
          + (f"; {len(gone)} dropped: " + "; ".join(gone) if gone else ""))


# ---------------------------------------------------------------------------------------------------------------------
# Check


class Graph:
    def __init__(self, path=GRAPH):
        self.g = json.load(open(path, encoding="utf-8"))
        self.nodes = {n["id"]: n for n in self.g["nodes"]}
        self.edges = self.g["edges"]
        self.by_premise = {e["premise"]: e for e in self.edges}
        self._fresh = {}

    def pin_now(self, key):
        m = re.match(r"^git (\w+) (.+)$", key)
        if m:
            changed = [p for p in git("diff", "--name-only", m.group(1), "--", m.group(2)).split("\n") if p]
            untracked = [p for p in git("ls-files", "-o", "--exclude-standard", "--", m.group(2)).split("\n") if p]
            return "unchanged" if not changed and not untracked else changed + untracked
        m = re.match(r"^const (\S+) (\w+)$", key)
        if m:
            v = re.search(rf'{m.group(2)}: &str = "([0-9a-f]{{64}})"', open(os.path.join(ROOT, m.group(1))).read())
            return v.group(1)[:16] if v else None
        m = re.match(r"^include (\S+) (\w+)$", key)
        if m:
            v = re.search(rf'{m.group(2)}: &str = include_str!\("(?:\.\./)*([^"]+)"\)', open(os.path.join(ROOT, m.group(1))).read())
            return v.group(1) if v else None
        m = CLAUSE_KEY.match(key)
        if m and not key.startswith("decisions/"):
            return record_clauses(m.group(1)).get(m.group(2))
        if key.endswith("/"):
            return dir_d16(key[:-1])
        return d16(key)

    def fresh(self, e):
        """(fresh, [why not])."""
        if e["id"] in self._fresh:
            return self._fresh[e["id"]]
        why = []
        for k, v in e["pins"].items():
            now = self.pin_now(k)
            if now != v:
                if isinstance(now, list):
                    why.append(f"{k.split(' ', 2)[2]} changed since {k.split(' ')[1]}: {len(now)} files: "
                               + ", ".join(os.path.relpath(p, k.split(' ', 2)[2]) for p in now))
                else:
                    why.append(f"{k} {v} -> {now or 'gone'}")
        ev = e.get("evidence", {})
        if "file" in ev and "verdict" in ev and os.path.isfile(os.path.join(ROOT, ev["file"])):
            ok, w = verdict(ev["file"], ev["verdict"])
            if not ok:
                why.append(f"{ev['file']}: {w}")
        self._fresh[e["id"]] = (not why, why)
        return self._fresh[e["id"]]

    def newer_evidence(self, e):
        ev = e.get("evidence", {})
        if "results" in ev and "file" in ev:
            n = newest(ev["results"])
            if n and n != ev["file"]:
                return n
        return None


class GradedValues(inv.Values):
    """inventory.py's evaluation, with every edge premise valued from the graph and graded (§5)."""

    def __init__(self, binding, decl, graph, grade):
        super().__init__(binding, decl)
        self.graph, self.grade = graph, TYPES.index(grade)

    def atom(self, a, seen=()):
        e = self.graph.by_premise.get(a)
        if e is None:
            return super().atom(a, seen)
        if TYPES.index(e["type"]) > self.grade:
            return False, f"{a} below grade"
        ok, why = self.graph.fresh(e)
        if e["type"] == "trusted":
            v, x = super().atom(e["row"], seen)
        elif self.b["premises"].get(a, {}).get("kind") != "edge":
            v, x = self.d[a], (a if a not in self.why else f"{a} ({self.why[a]})")
        else:
            v, x = True, a
        if not ok:
            return False, f"{a} stale"
        return v, (x if v else f"{a}: {x}")


def graph_binding(graph, binding):
    """The binding with the graph's re-expression applied: derived premises replaced, replacements per theorem."""
    b = json.loads(json.dumps(binding))
    b["derived"] = {k: {kk: vv for kk, vv in v.items() if kk != "re-expresses"} for k, v in graph.g["binding"]["derived"].items()}
    for e in graph.edges:
        if e["premise"] not in b["premises"]:
            b["premises"][e["premise"]] = {"kind": "edge", "type": e["type"]}
    reps = {tuple(r["names"]): r["replaces"] for r in graph.g["binding"]["replaces"]}
    for t in b["theorems"]:
        t["replaces"] = reps[tuple(t["names"])]
    return b


def verdicts(binding, decl, values_cls=inv.Values, **kw):
    v = values_cls(binding, decl, **kw)
    out = {}
    for t in binding["theorems"]:
        need = inv.requirement(binding, t, v.rung)
        vals = [(a, *v.atom(a)) for a in need]
        bad = [e for _, ok, e in vals if not ok]
        via = [e for a, ok, e in vals if ok and a in binding.get("derived", {})]
        out[", ".join(t["names"])] = (not bad, bad, via)
    return out


def routes_declarations(binding):
    """premise-routes.sh's five declarations, built as it builds them."""
    ref = inv.annex_b(ADR45)
    cols = binding["premises"]

    def faith(p):
        return p.startswith("enc-faithful(") or p.startswith("model-faithful(")
    base = {p: True for p, s in cols.items() if "derived" not in s and s.get("kind") != "check" and not faith(p)}
    others = {p: True for p, s in cols.items() if s.get("kind") == "condition" and p.startswith("enc-faithful")}

    def decl(rows=None, premises=None):
        return {"rung": 0, "rows": dict(ref["rows"], **(rows or {})), "premises": dict(base, **(premises or {}))}
    return [
        ("1-reference", decl()),
        ("2-lean-not-tlaps", decl({"T-0045-31": "excluded", "T-0045-37": "trust root"})),
        ("3-lean-every-encoding-read", decl({"T-0045-31": "excluded", "T-0045-37": "trust root"}, others)),
        ("4-lean-stage-not-T28", decl({"T-0045-28": "excluded", "T-0045-37": "trust root"}, {"model-faithful(apply/Seats)": True})),
        ("5-graph-check-refused", decl({"T-0045-31": "excluded", "T-0045-37": "trust root"},
                                       {"enc-faithful(Seats)": False, "enc-faithful(FloorComposition)": False})),
    ]


def routes_results():
    """The newest premise-routes results file's verdicts: {declaration: {theorem: holds}}."""
    f = newest("spec/premise-routes-results-*.txt")
    out, cur = {}, None
    for ln in open(os.path.join(ROOT, f), encoding="utf-8"):
        m = re.match(r"^=== (\S+)", ln)
        if m:
            cur = out.setdefault(m.group(1), {})
            continue
        m = re.match(r"^- (.+?): (holds|void)", ln)
        if m and cur is not None:
            cur[m.group(1)] = m.group(2) == "holds"
    return f, out


def grade_of(binding, decl, graph):
    """{theorem: (grade or None, explanation at that grade, why void one grade up)}."""
    by = {g: verdicts(binding, decl, GradedValues, graph=graph, grade=g) for g in TYPES}
    out = {}
    for name in by["trusted"]:
        g = next((g for g in TYPES if by[g][name][0]), None)
        if g is None:
            out[name] = (None, by["trusted"][name][1], None)
            continue
        up = TYPES[TYPES.index(g) - 1] if TYPES.index(g) > 0 else None
        out[name] = (g, by[g][name][2], by[up][name][1] if up else None)
    return out, by


def lists_against_graph(graph, b):
    """§8: each of the four lists checked against the graph. [(list, ok, lines)]."""
    out = []
    # 1. corpus-pins.sha256: exactly the upper ends of the reference's read edges, at the same pins
    pins = {}
    for line in open(os.path.join(ROOT, "mechanism", "corpus-pins.sha256")):
        if line.strip():
            d, p = line.split("  ", 1)
            pins[p.strip()] = d.strip()
    reads = [e for e in graph.edges if e["type"] == "read" and e.get("pinned_by") == "mechanism/corpus-pins.sha256"]
    uppers = {}
    for e in reads:
        n = graph.nodes[e["to"]]
        uppers.setdefault(n["path"], []).append(e)
    lines, ok = [], True
    for p in sorted(set(pins) | set(uppers)):
        if p not in uppers:
            ok = False
            lines.append(f"pinned, no read edge from the reference: {p}")
        elif p not in pins:
            ok = False
            lines.append(f"a read edge from the reference, not pinned: {p}")
        else:
            e = uppers[p][0]
            if p.startswith("spec/"):
                if e["pins"].get(p) != pins[p][:16]:
                    ok = False
                    lines.append(f"{p}: pin file {pins[p][:16]}, graph {e['pins'].get(p)}")
            else:
                rec = os.path.basename(p)[:-3]
                text = record_at_digest(p, pins[p])
                want = {f"{rec} {c}": d for c, d in record_clauses(rec, text).items()} if text else None
                if want is not None and want != e["pins"]:
                    ok = False
                    lines.append(f"{p}: the graph's clause pins are not the pinned text's clauses")
    lines.insert(0, f"{len(pins)} pinned paths, {len(uppers)} upper ends of read edges from the reference, "
                    f"{len(reads)} such edges" + (": the same paths, at the same pins" if ok else ""))
    out.append(("mechanism/corpus-pins.sha256", ok, lines))
    # 2. the binding's check columns: each is a graph edge's premise, on the same results
    lines, ok = [], True
    for p, s in b["premises"].items():
        if s.get("kind") != "check":
            continue
        e = graph.by_premise.get(p)
        if not e:
            ok = False
            lines.append(f"{p}: no edge carries it")
        elif e.get("evidence", {}).get("results") != s["check"]["results"]:
            ok = False
            lines.append(f"{p}: binding reads {s['check']['results']}, edge {e.get('evidence', {}).get('results')}")
        else:
            lines.append(f"{p}: the edge {e['id']}, on {s['check']['results']}")
    for p, s in b["premises"].items():
        if s.get("kind") == "condition" and (p.startswith("enc-faithful(") or p.startswith("model-faithful(")):
            if p not in graph.by_premise:
                ok = False
                lines.append(f"{p}: a reading ADR-0053 named, and no edge carries it")
    lines.append(f"every faithfulness column of kind condition is an edge's premise" if ok else "")
    out.append(("the binding's check columns", ok, [x for x in lines if x]))
    # 3. the manifest index: the newest reference cut's crates are the implementation nodes
    lines, ok = [], True
    rows = [ln.rstrip("\n").split("\t") for ln in open(os.path.join(ROOT, "manifests", "index.tsv"))][1:]
    refrow = [r for r in rows if r[1] == "reference"][-1]
    gcut = [r for r in rows if r[1] == "checkpoint"][-1]
    man = [ln.split("  ", 1)[1].strip() for ln in open(os.path.join(ROOT, "manifests", refrow[0])) if "  " in ln]
    mcrates = {"/".join(p.split("/")[:3]) for p in man if p.startswith("mechanism/crates/")}
    gcrates = {n for n in graph.nodes if n.startswith("mechanism/crates/") and graph.nodes[n]["layer"] == "implementation"}
    if mcrates != gcrates:
        ok = False
        lines.append(f"{refrow[0]} crates {sorted(mcrates - gcrates)} not nodes; nodes {sorted(gcrates - mcrates)} not in it")
    else:
        lines.append(f"{refrow[0]} ({refrow[2]}, {refrow[3]}): its {len(mcrates)} crates are the graph's {len(gcrates)} crate nodes")
    gman = {ln.split("  ", 1)[1].strip() for ln in open(os.path.join(ROOT, "manifests", gcut[0])) if "  " in ln}
    later = sorted({n["path"] for n in graph.nodes.values() if n.get("path") and n["layer"] in ("model", "record", "policy")
                    and os.path.isfile(os.path.join(ROOT, n["path"])) and n["path"] not in gman})
    lines.append(f"{gcut[0]} ({gcut[2]}): {len(later)} file nodes entered since that cut (information)"
                 + (": " + ", ".join(later) if later else ""))
    out.append(("manifests/index.tsv", ok, lines))
    # 4. the sync scripts' file lists
    lines, ok = [], True
    proofs = {rel(p) for p in glob.glob(os.path.join(HERE, "*_proof.tla"))}
    tl = {e["from"] for e in graph.edges if e["type"] == "proved" and e.get("row") == "T-0045-31"}
    if proofs != tl:
        ok = False
        lines.append(f"proof-sync.sh reads {sorted(proofs - tl)} that no edge does; edges {sorted(tl - proofs)} it does not")
    else:
        lines.append(f"spec/proof-sync.sh: its {len(proofs)} proof modules are the {len(tl)} TLAPS edges' lower ends")
    ls = open(os.path.join(ROOT, "tools", "lean-sync.sh")).read()
    series = set(re.findall(r"\) echo (\w+);;", ls.split("series()")[1].split("}")[0]))
    gseries = set()
    for e in graph.edges:
        r = e.get("evidence", {}).get("results", "")
        m = re.search(r"/(\w+)-results-\*\.txt$", r)
        if m and ("lean/" in r):
            gseries.add(m.group(1))
    if series != gseries:
        ok = False
        lines.append(f"tools/lean-sync.sh series {sorted(series - gseries)} carry no edge; edges read {sorted(gseries - series)} it does not")
    else:
        lines.append(f"tools/lean-sync.sh: its {len(series)} series are the Lean edges' evidence ({', '.join(sorted(series))})")
    if not any(e.get("evidence", {}).get("results") == "spec/Mechanism-trace-results-*.txt" for e in graph.edges):
        ok = False
        lines.append("spec/mechanism-trace-results.sh: no replayed edge reads its results")
    else:
        lines.append("spec/mechanism-trace-results.sh: its results are the replayed edges' evidence")
    out.append(("the sync scripts", ok, lines))
    return out


def check(argv):
    strict = "--strict" in argv
    graph = Graph()
    binding = json.load(open(BINDING))
    gb = graph_binding(graph, binding)
    fail = []
    s16 = lambda p: d16(p)  # noqa: E731
    print("TOPAK — the specification graph, checked (ADR-0057, Proposed): stale edges, what no model reads, guarantees "
          "stated twice, the four lists against the graph, and the inventory at every grade")
    print("Sources: " + " · ".join(f"{p} (sha256 {s16(p)})" for p in (
        "spec/specification-graph.json", "spec/specification-graph.py", "spec/clauses.py", "spec/inventory.py",
        "spec/theorem-premise-binding.json", "decisions/ADR-0045.md")))
    print(f"Graph: {len(graph.nodes)} nodes, {len(graph.edges)} edges, built at {graph.g['built']['at']} · "
          + "types, strongest first: " + " > ".join(TYPES))
    counts = {}
    for n in graph.nodes.values():
        counts[n["layer"]] = counts.get(n["layer"], 0) + 1
    print("Layers: " + " · ".join(f"{l} {counts.get(l, 0)}" for l in LAYERS)
          + "".join(f" · {l} {c}" for l, c in counts.items() if l not in LAYERS))
    ecounts = {}
    for e in graph.edges:
        ecounts[e["type"]] = ecounts.get(e["type"], 0) + 1
    print("Edges: " + " · ".join(f"{t} {ecounts.get(t, 0)}" for t in TYPES))

    # well-formed
    errs = []
    for e in graph.edges:
        if e["type"] not in TYPES:
            errs.append(f"{e['id']}: unknown type")
        for end in ("from", "to"):
            if e[end] not in graph.nodes:
                errs.append(f"{e['id']}: {end} {e[end]} is not a node")
        if not e.get("pins"):
            errs.append(f"{e['id']}: no pins")
    for name, spec in graph.g["binding"]["derived"].items():
        for route in spec["any_of"]:
            for a in route:
                if not (TROW.match(a) or a in binding["premises"] or a in graph.g["binding"]["derived"] or a in graph.by_premise):
                    errs.append(f"derived {name}: {a} is undefined")
    errs += inv.check_derived(gb)
    if errs:
        fail.append("malformed")
    print()
    print("== Well formed: " + ("yes" if not errs else f"{len(errs)} errors"))
    for x in errs:
        print("  " + x)

    # 1. stale edges
    stale = [(e, graph.fresh(e)[1]) for e in graph.edges if not graph.fresh(e)[0]]
    print()
    print(f"== Stale edges (§3, §8): {len(stale)} of {len(graph.edges)}")
    groups = {}
    for e, why in stale:
        key = e.get("evidence", {}).get("results") or e.get("pinned_by") or e["type"]
        groups.setdefault(key, []).append((e, why))
    for key in sorted(groups):
        print(f"- {key}: {len(groups[key])} edge(s)")
        for e, why in groups[key]:
            print(f"    {e['id']}  [{e['premise'] if e['premise'] != premise_name(e['type'], e['from'], e['to']) else 'premise false'}]")
            for w in why[:4]:
                print(f"      {w}")
            if len(why) > 4:
                print(f"      … and {len(why) - 4} more")
    newer = [(e, graph.newer_evidence(e)) for e in graph.edges if graph.newer_evidence(e)]
    for e, n in newer:
        print(f"  newer evidence than the pin: {e['id']}: {e['evidence']['file']} -> {n}")

    # 2. what no model reads
    print()
    print("== Clauses the reference follows with no edge but the reference's own reading (§8)")
    into = {}
    for e in graph.edges:
        into.setdefault(e["to"], []).append(e)
    followed = sorted({e["to"] for e in graph.edges if e.get("pinned_by") and graph.nodes[e["to"]]["layer"] == "record"})

    def beyond_reading(e):
        return not (e["type"] in ("read", "trusted") and graph.nodes[e["from"]]["layer"] == "implementation")
    nomodel = []
    for rec in followed:
        for cid in graph.nodes[rec].get("clauses", []):
            cn = f"{rec} {cid}"
            if not [e for e in into.get(cn, []) + into.get(rec, []) if beyond_reading(e)]:
                nomodel.append(cn)
    byrec = {}
    for cn in nomodel:
        r, c = cn.split(" ", 1)
        byrec.setdefault(r, []).append(c)
    print(f"  {len(nomodel)} clauses of {len(byrec)} of the {len(followed)} records it follows: no module, stage, "
          "proof or check reads them; the code's reading is their only discharge")
    for r in sorted(byrec):
        print(f"  {r}: {', '.join(byrec[r])}")
    print("  Each replay's model, against the records the replayed code follows and some other module reads:")
    modelled = {}
    for x in graph.edges:
        if x["type"] == "read" and graph.nodes[x["from"]]["layer"] == "model":
            modelled.setdefault(graph.nodes[x["to"]].get("of", x["to"]), set()).add(os.path.basename(x["from"]))
    for e in [e for e in graph.edges if e["type"] == "replayed" and e["to"].startswith("spec/")]:
        code_reads = {x["to"] for x in graph.edges if x["type"] == "read" and x["from"] == e["from"] and graph.nodes[x["to"]]["layer"] == "record"}
        mods = {e["to"]} | ({"spec/Mechanism.tla"} if e["to"] == "spec/ConfinementRefinement.tla" else set())
        mod_reads = {graph.nodes[x["to"]].get("of", x["to"]) for x in graph.edges if x["from"] in mods and x["type"] == "read"}
        missing = sorted(r for r in code_reads if r not in mod_reads and r in modelled)
        print(f"  - {e['to']} ({'fresh' if graph.fresh(e)[0] else 'stale'}) reads none of: "
              + "; ".join(f"{r} (read by {', '.join(sorted(modelled[r]))})" for r in missing))

    # 3. twice-stated guarantees
    print()
    print("== Guarantees stated more than once (§6)")
    for r in graph.g["restates"]:
        print(f"- {r['guarantee']}")
        st = r["statements"]
        for i in range(len(st)):
            for j in range(i + 1, len(st)):
                a, b2 = st[i]["node"], st[j]["node"]
                es = [e for e in graph.edges if {e["from"], e["to"]} == {a, b2} and e["type"] != "trusted"]
                desc = "; ".join(f"{e['type']} ({'fresh' if graph.fresh(e)[0] else 'stale'})" for e in es) or "no edge"
                print(f"    {st[i]['where']}  ~  {st[j]['where']}: {desc}")

    # 4. modules no theorem is checked in
    print()
    checked = set()
    for t in binding["theorems"]:
        for m in re.findall(r"(\w+)\.tla", t.get("checked_in", "")):
            checked.add(m)
    mods = sorted(os.path.basename(n)[:-4] for n in graph.nodes if re.fullmatch(r"spec/\w+\.tla", n) and not n.endswith("_proof.tla"))
    unbound = [m for m in mods if m not in checked]
    print(f"== Modules no theorem in the binding is checked in: {len(unbound)} of {len(mods)}")
    print("  " + ", ".join(unbound))

    # 5. edges up, graded once per module
    print()
    print("== Edges up, from each module to what it reads (§5): graded once per module")
    ups = {}
    for e in graph.edges:
        if e["from"].startswith("spec/") and e["from"].endswith(".tla") and graph.nodes[e["to"]]["layer"] in ("record", "assurance"):
            ups.setdefault(e["from"], []).append(e)
    readers = {}
    for m, es in sorted(ups.items()):
        t = max((x["type"] for x in es), key=TYPES.index)
        rd = sorted({x.get("reader", "-") for x in es})
        readers.setdefault((t, tuple(rd)), []).append(os.path.basename(m))
    for (t, rd), ms in readers.items():
        print(f"  {t}, by {', '.join(rd)}: {len(ms)} modules ({', '.join(ms)})")
    noread = sorted(os.path.basename(n) for n in graph.nodes if re.fullmatch(r"spec/\w+\.tla", n)
                    and not n.endswith("_proof.tla") and n not in ups)
    print("  modules that read no record: " + (", ".join(noread) or "none"))

    # 6. the four lists
    print()
    print("== The four lists, read against the graph (§8)")
    for name, ok, lines in lists_against_graph(graph, binding):
        print(f"- {name}: {'agrees' if ok else 'DISAGREES'}")
        for x in lines:
            print(f"    {x}")
        if not ok:
            fail.append(name)

    # 7. inventory at grade trusted against inventory.py's
    print()
    print("== The inventory at grade trusted against inventory.py's (§14)")
    ann = inv.annex_b(ADR45)
    plain = verdicts(binding, ann)
    graded = verdicts(gb, ann, GradedValues, graph=graph, grade="trusted")
    diff = [n for n in plain if plain[n][0] != graded[n][0]]
    print(f"- Annex B as declared (inventory.py --annex-b): {sum(v[0] for v in plain.values())} of {len(plain)} hold by "
          f"inventory.py, {sum(v[0] for v in graded.values())} at grade trusted by the graph; "
          + ("the same, theorem by theorem" if not diff else f"{len(diff)} DIFFER: {', '.join(diff)}"))
    if diff:
        fail.append("annex-b")
    rf, rr = routes_results()
    print(f"- premise-routes.sh's five declarations ({rf}), each against the graph at grade trusted:")
    route_diffs = []
    for name, decl in routes_declarations(binding):
        p = verdicts(binding, decl)
        q = verdicts(gb, decl, GradedValues, graph=graph, grade="trusted")
        mism = [n for n in p if rr.get(name, {}).get(n) is not None and rr[name][n] != p[n][0]]
        d = [n for n in p if p[n][0] != q[n][0]]
        route_diffs += [(name, n, q[n][1]) for n in d]
        print(f"    {name}: {sum(v[0] for v in p.values())} hold in the results file's run"
              + (f" (this run's evaluation differs from the file on {len(mism)})" if mism else "")
              + f", {sum(v[0] for v in q.values())} by the graph; "
              + ("the same verdicts" if not d else f"{len(d)} differ: " + "; ".join(f"{n} void: {', '.join(q[n][1])}" for n in d)))
    if route_diffs and strict:
        fail.append("premise-routes")
    if stale and strict:
        fail.append("stale")

    # 8. graded inventory
    print()
    print("== The inventory at every grade (§5): each theorem's grade, the route that carried it, and why it fails one grade up")
    for title, decl in (("the reference, Annex B as declared", ann),
                        ("the reference with every parameter, condition and gap premise true (premise-routes.sh's 1-reference)",
                         routes_declarations(binding)[0][1])):
        grades, by = grade_of(gb, decl, graph)
        print(f"=== {title}")
        print("  held at each grade: " + " · ".join(f"{g} {sum(v[0] for v in by[g].values())}" for g in TYPES))
        for name, (g, info, up) in grades.items():
            if g is None:
                print(f"- {name}: void at every grade: {', '.join(info)}")
            else:
                print(f"- {name}: {g}" + (f" (via {'; '.join(info)})" if info else "")
                      + (f" · one grade up: {', '.join(up)}" if up else ""))
    print()
    print("Result: " + ("graph well formed, the four lists agree, and the inventory at grade trusted is inventory.py's"
                        if not fail else "FAILED: " + ", ".join(fail))
          + f" · {len(stale)} stale edges · {len(route_diffs)} premise-route verdicts moved by stale edges")
    return 1 if fail else 0


def main():
    argv = sys.argv[1:]
    if not argv or argv[0] not in ("build", "check"):
        sys.exit(__doc__.split("\n\n")[1])
    if argv[0] == "build":
        build(argv[1:])
    else:
        sys.exit(check(argv[1:]))


if __name__ == "__main__":
    main()
