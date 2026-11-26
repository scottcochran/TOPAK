"""H9 — The corpus's specifications form a graph (ADR-0057, Proposed) and a deployment declares its own against it
(ADR-0058, Proposed). Nodes are artifacts with open layers; every edge is typed by what it leaves to a person; each
edge contributes a premise; a theorem is inherited at the grade of its weakest edge. The graph's counts, the picture's
edges, the checker's lists and the digests ADR-0057 §14 cites are read from `spec/specification-graph.json`,
`spec/specification-graph-results-2026.11.07.txt` and `decisions/ADR-0057.md` at build time: a missing file, a line
that does not parse or an edge the picture draws that the graph no longer holds is an error, not a blank. Where the
graph file and the results file disagree, both are drawn. Every file is read at PIN_G12 (lib.py), the commit H9 was
drawn at: the graph rebuilt after it (2026.11.17) is not drawn here."""
import hashlib
import json
import pathlib
import re

from lib import PIN_G12, Canvas, STATE_G12, STATUS, read_at, text_width

ID, SLUG = "H9", "specification-graph"
RECORDS = ('ADR-0057', 'ADR-0058',)   # the records this diagram draws in full: a name of one opens it
PIN_LINKS = PIN_G12   # its files are read at this commit, and its links open them there

W = 3600

_HERE = pathlib.Path(__file__).resolve()
ROOT = next((p for p in [*_HERE.parents, pathlib.Path.cwd(), *pathlib.Path.cwd().parents]
             if (p / "spec" / "specification-graph.json").exists() and (p / "decisions").is_dir()), _HERE.parents[3])
SPEC = ROOT / "spec"
GRAPH = SPEC / "specification-graph.json"
RESULTS = SPEC / "specification-graph-results-2026.11.07.txt"   # named, never "the newest"
RECORD = ROOT / "decisions" / "ADR-0057.md"

TYPES = ["executed", "generated", "proved", "proved of a reading", "replayed", "tested", "read", "trusted"]
LAYERS = ["intent", "vocabulary", "record", "assurance", "model", "interface", "policy", "implementation", "runtime",
          "deployment"]
# the diagram's colour per edge type: what the edge leaves decides it
TACC = {"executed": "blue", "generated": "blue", "proved": "teal", "proved of a reading": "teal", "replayed": "green",
        "tested": "green", "read": "brown", "trusted": "grey"}

# The picture's seventeen edges: (number, type, from, to). Each must exist in the graph file, or the build fails.
PIC = [
    ("①", "proved", "spec/Seats_proof.tla", "spec/Seats.tla"),
    ("②", "proved", "spec/lean/TopakSpec/Seats.lean", "spec/Seats.tla"),
    ("③", "proved of a reading", "spec/lean/TopakSpec/Seats.lean", "spec/Seats.tla"),
    ("④", "read", "spec/Seats.tla", "ADR-0037 §4"),
    ("⑤", "trusted", "mechanism", "spec/Seats.tla"),
    ("⑥", "read", "mechanism/crates/topak-core", "spec/Seats.tla"),
    ("⑦", "proved of a reading", "mechanism/crates/topak-core", "spec/Seats.tla"),
    ("⑧", "replayed", "mechanism/crates/topak-core", "mechanism/lean/Topak/SeatsModel.lean"),
    ("⑨", "proved of a reading", "mechanism/crates/topak-core", "spec/FloorComposition.tla"),
    ("⑩", "proved of a reading", "mechanism/crates/topak-core", "ADR-0039 §2"),
    ("⑪", "tested", "mechanism/crates/topak-core", "spec/Operators.tla"),
    ("⑫", "read", "spec/Operators.tla", "ADR-0050 §2"),
    ("⑬", "replayed", "mechanism/crates/topak-core", "spec/Mechanism.tla"),
    ("⑭", "read", "spec/Mechanism.tla", "ADR-0031 §4"),
    ("⑮", "executed", "mechanism/crates/topak-floor", "floor/proposed/workflow-floor.cedar"),
    ("⑯", "generated", "floor/proposed/workflow-floor.cedar", "floor/genesis-floor.cedar"),
    ("⑰", "read", "spec/FloorComposition.tla", "ADR-0030 §1"),
]


# ------------------------------------------------------------------------------------------------- readers
def _read(path):
    """`path` (under ROOT) at PIN_G12, the commit H9 was drawn at, not the working tree (lib.py, diagrams/README.md)."""
    return read_at(ROOT, PIN_G12, path.relative_to(ROOT).as_posix())


def _need(pat, text, what, flags=re.M):
    m = re.search(pat, text, flags)
    if not m:
        raise ValueError(f"H9: cannot parse {what}: /{pat}/")
    return m


def digest(path):
    return hashlib.sha256(_read(path)).hexdigest()[:16]


def read_graph():
    g = json.loads(_read(GRAPH).decode("utf-8"))
    for k in ("nodes", "edges", "types", "layers", "built", "restates", "binding"):
        if k not in g:
            raise ValueError(f"H9: the graph file has no {k!r}")
    nodes, edges = g["nodes"], g["edges"]
    by_layer = {l: 0 for l in LAYERS}
    for n in nodes:
        if n["layer"] not in by_layer:
            by_layer[n["layer"]] = 0     # an open set: a new layer is drawn, not refused (§1)
        by_layer[n["layer"]] += 1
    by_type = {t: 0 for t in TYPES}
    index = {}
    for e in edges:
        if e["type"] not in by_type:
            raise ValueError(f"H9: edge type {e['type']!r} is not one of §3's eight")
        by_type[e["type"]] += 1
        index[(e["type"], e["from"], e["to"])] = e
    if [t["type"] for t in g["types"]] != TYPES:
        raise ValueError("H9: the graph's type order is not §3's")
    clauses = sum(1 for n in nodes if n.get("clause"))
    records = sum(1 for n in nodes if n["layer"] == "record" and not n.get("clause"))
    route_false = sorted(e["id"] for e in edges if e.get("route") is False)
    derived = g["binding"]["derived"]
    names = list(derived) if isinstance(derived, dict) else [str(d.get("name", "")) for d in derived]
    reaches = sum(1 for n in names if n.startswith("reaches-code("))
    return dict(n=len(nodes), m=len(edges), by_layer=by_layer, by_type=by_type, index=index, clauses=clauses,
                records=records, route_false=route_false, built=g["built"].get("at", "?"), derived=len(derived),
                reaches=reaches, restates=len(g["restates"]))


def read_results():
    t = _read(RESULTS).decode("utf-8")
    lines = t.splitlines()
    m = _need(r"^Graph: (\d+) nodes, (\d+) edges, built at (.+?) · types", t, "the Graph line")
    r = dict(n=int(m.group(1)), m=int(m.group(2)), built=m.group(3))
    lay = _need(r"^Layers: (.+)$", t, "the Layers line").group(1)
    r["by_layer"] = {k: int(v) for k, v in re.findall(r"(\w+) (\d+)", lay)}
    ed = _need(r"^Edges: (.+)$", t, "the Edges line").group(1)
    r["by_type"] = {k.strip(): int(v) for k, v in re.findall(r"([a-z ]+?) (\d+)", ed)}
    if set(r["by_type"]) != set(TYPES) or set(r["by_layer"]) != set(LAYERS):
        raise ValueError("H9: the results header's types or layers are not the record's")
    r["well"] = _need(r"^== Well formed: (\w+)$", t, "well formed").group(1)
    m = _need(r"^== Stale edges \(§3, §8\): (\d+) of (\d+)$", t, "the stale count")
    r["stale_n"], r["stale_of"] = int(m.group(1)), int(m.group(2))
    # the stale edges, with their evidence group and what moved
    stale, group, cur = [], None, None
    i = lines.index(next(l for l in lines if l.startswith("== Stale edges")))
    for ln in lines[i + 1:]:
        if ln.startswith("== "):
            break
        g = re.match(r"^- (.+?): (\d+) edge\(s\)$", ln)
        e = re.match(r"^    ([a-z ]+): (.+?) → (.+?)  \[(.+)\]$", ln)
        p = re.match(r"^      (\S+) [0-9a-f]{16} -> [0-9a-f]{16}$", ln)
        more = re.match(r"^      … and (\d+) more$", ln)
        ch = re.match(r"^      (\S+) changed since (\w+): (\d+) files: (.+)$", ln)
        if g:
            group = g.group(1)
        elif e:
            cur = dict(group=group, type=e.group(1), frm=e.group(2), to=e.group(3), note=e.group(4), moved=[])
            stale.append(cur)
        elif p and cur:
            cur["moved"].append(p.group(1))
        elif more and cur:
            cur["moved"].append(f"and {more.group(1)} more")
        elif ch and cur:
            cur["moved"].append(f"{ch.group(1)}: {ch.group(3)} files since {ch.group(2)}")
        elif ln.strip():
            raise ValueError(f"H9: cannot parse a stale-edge line: {ln!r}")
    if len(stale) != r["stale_n"]:
        raise ValueError(f"H9: {len(stale)} stale edges listed, header says {r['stale_n']}")
    r["stale"] = stale
    r["stale_keys"] = {(s["type"], s["frm"], s["to"]) for s in stale}
    m = _need(r"^  (\d+) clauses of (\d+) of the (\d+) records it follows", t, "the unread clauses line")
    r["unread"] = (int(m.group(1)), int(m.group(2)), int(m.group(3)))
    i = lines.index(next(l for l in lines if l.startswith("== Clauses the reference follows")))
    r["unread_rows"] = []
    for ln in lines[i + 2:]:
        m = re.match(r"^  (ADR-\d{4}): (.+)$", ln)
        if not m:
            break
        r["unread_rows"].append((m.group(1), m.group(2)))
    if len(r["unread_rows"]) != r["unread"][1]:
        raise ValueError("H9: the unread-clause records listed do not match the count")
    i = lines.index(next(l for l in lines if l.startswith("== Guarantees stated more than once")))
    r["twice"] = []
    for ln in lines[i + 1:]:
        if ln.startswith("== ") or not ln.strip():
            break
        if ln.startswith("- "):
            r["twice"].append((ln[2:], []))
        else:
            r["twice"][-1][1].append(ln.strip())
    m = _need(r"^== Modules no theorem in the binding is checked in: (\d+) of (\d+)$", t, "the unchecked modules")
    r["unchecked"] = (int(m.group(1)), int(m.group(2)))
    r["unchecked_list"] = lines[lines.index(m.group(0)) + 1].strip()
    if len(r["unchecked_list"].split(", ")) != r["unchecked"][0]:
        raise ValueError("H9: the unchecked module list does not match its count")
    m = _need(r"^  read, by the drafter: (\d+) modules", t, "edges up")
    r["up"] = int(m.group(1))
    r["up_none"] = _need(r"^  modules that read no record: (.+)$", t, "modules that read no record").group(1)
    i = lines.index(next(l for l in lines if l.startswith("== The four lists")))
    r["lists"] = []
    for ln in lines[i + 1:]:
        if ln.startswith("== "):
            break
        m = re.match(r"^- (.+?): (agrees|disagrees)$", ln)
        if m:
            r["lists"].append([m.group(1), m.group(2), []])
        elif ln.strip():
            r["lists"][-1][2].append(ln.strip())
    if len(r["lists"]) != 4:
        raise ValueError("H9: the checker reports other than four lists")
    m = _need(r"^- Annex B as declared \(inventory\.py --annex-b\): (\d+) of (\d+) hold by inventory\.py, (\d+) at grade "
              r"trusted by the graph; (.+)$", t, "the Annex B line")
    r["annexb"] = (int(m.group(1)), int(m.group(2)), int(m.group(3)), m.group(4))
    r["routes"] = []
    for m in re.finditer(r"^    ([1-5])-(\S+): (\d+) hold in the results file's run, (\d+) by the graph; (.+)$", t, re.M):
        rest = m.group(5)
        if rest.startswith(("1 differ", "2 differ", "3 differ")) or " differ: " in rest:
            names = re.findall(r"(\w+) void", rest)
            rest = rest.split(":")[0] + ": " + ", ".join(f"`{n}`" for n in names) + " void by the graph, holding in the file"
        r["routes"].append((m.group(1), m.group(2), int(m.group(3)), int(m.group(4)), rest))
    if len(r["routes"]) != 5:
        raise ValueError("H9: the checker reports other than five premise-route declarations")
    r["routes_file"] = _need(r"premise-routes\.sh's five declarations \((spec/[\w.-]+)\)", t, "the routes file").group(1)
    held = _need(r"^  held at each grade: (.+)$", t, "held at each grade").group(1)
    r["held"] = {k.strip(): int(v) for k, v in re.findall(r"([a-z ]+?) (\d+)", held)}
    r["result"] = _need(r"^Result: (.+)$", t, "the Result line").group(1)
    srcs = _need(r"^Sources: (.+)$", t, "the Sources line").group(1)
    r["src_digests"] = dict(re.findall(r"(\S+) \(sha256 ([0-9a-f]{16})\)", srcs))
    return r


def read_record():
    t = _read(RECORD).decode("utf-8")
    cited = {}
    for name in ("spec/specification-graph.json", "spec/specification-graph.py", "spec/clauses.py",
                 "spec/specification-graph-results-2026.11.07.txt"):
        cited[name] = _need(r"`" + re.escape(name) + r"` \(`([0-9a-f]{16})`\)", t, f"§14's digest of {name}").group(1)
    m = _need(r"It has (\d+) nodes: (\d+) clauses of (\d+) records", t, "§14's node count")
    n, clauses, records = int(m.group(1)), int(m.group(2)), int(m.group(3))
    m = _need(r"It has (\d+) edges, each typed and pinned: (.+?)\.", t, "§14's edge count", flags=re.S)
    e = int(m.group(1))
    by_type = {k.strip(): int(v) for k, v in re.findall(r"([a-z ]+?) (\d+)", m.group(2))}
    mods = _need(r"the (\d+) modules and (\d+) proof modules", t, "§14's module count")
    status = _need(r"^\*\*Status:\*\* (\w+) · ([\d.]+)$", t, "the status line")
    return dict(cited=cited, n=n, clauses=clauses, records=records, m=e, by_type=by_type,
                mods=int(mods.group(1)), proofs=int(mods.group(2)), status=status.group(1), date=status.group(2))


# ------------------------------------------------------------------------------------------------- helpers
def row_cards(c, x, y, w, gap, specs, size=14):
    """A row of cards of equal height, measured over every card. specs: (title, body, accent, kwargs)."""
    n = len(specs)
    cw = (w - (n - 1) * gap) / n
    h = max(c.card(0, 0, cw, t, b, draw=False, size=size, status=k.get("status"), sub=k.get("sub"),
                   bullets=k.get("bullets", True)) for t, b, _, k in specs)
    for i, (t, b, acc, k) in enumerate(specs):
        c.card(x + i * (cw + gap), y, cw, t, b, accent=acc, h=h, size=size, **k)
    return h


def stack(c, x, y, w, specs, gap=16, size=14):
    for t, b, acc, k in specs:
        y += c.card(x, y, w, t, b, accent=acc, size=size, **k) + gap
    return y - gap


def band(c, x, y, title, accent="ink", status=None, extra=""):
    c.text(x, y + 22, title, 22, accent, bold=True)
    if status:
        c.status(x + text_width(title, 22, True) + 20, y + 4, status, extra)
    return y + 54


def node(c, x, y, w, title, sub, accent, h=None, draw=True, dash=None, tint=True):
    return c.card(x, y, w, title, [sub] if sub else [], accent=accent, size=12.5, tsize=14, pad=12, h=h, draw=draw,
                  bullets=False, dash=dash, tint=tint)


def fresh_word(res, key):
    return "[[red|stale]]" if key in res["stale_keys"] else "[[green|fresh]]"


# ------------------------------------------------------------------------------------------------- build
def build():
    G = read_graph()
    R = read_results()
    REC = read_record()
    for num, ty, frm, to in PIC:
        if (ty, frm, to) not in G["index"]:
            raise ValueError(f"H9: the graph no longer holds the picture's edge {num} {ty}: {frm} → {to}")
    counts_agree = (G["n"], G["m"]) == (R["n"], R["m"]) and G["by_type"] == R["by_type"] and \
        all(G["by_layer"].get(l, 0) == R["by_layer"][l] for l in LAYERS)
    rec_agree = (REC["n"], REC["m"], REC["clauses"], REC["records"]) == (G["n"], G["m"], G["clauses"], G["records"]) \
        and all(REC["by_type"].get(t) == G["by_type"][t] for t in TYPES)
    dig = {name: digest(ROOT / name) for name in REC["cited"]}
    dig_ok = {name: dig[name] == REC["cited"][name] for name in REC["cited"]}
    stale_drawn = [num for num, ty, frm, to in PIC if (ty, frm, to) in R["stale_keys"]]

    c = Canvas(ID, "The corpus's specifications form a graph: layers are open, every edge is typed by what it leaves "
                   "to a person, a guarantee carries its givens, and a theorem is inherited at the grade of its "
                   "weakest edge",
               "ADR-0057 (**Proposed**, 2026.11.06; R1 2026.11.07) reads the corpus's four separate keepers of \"what "
               "discharges what\" (the drift pins, the binding table, the manifests, the sync scripts) as one graph: "
               "artifacts are nodes with an open set of layers ⟨K1⟩, every edge is one of eight types ordered by what "
               "it leaves to a person ⟨K2⟩, each edge is a premise, and a theorem holds at a grade. ADR-0058 "
               "(**Proposed**, 2026.11.06) gives a deployment the same graph as an overlay: keep, replace, add or omit "
               "each node, type every edge it re-establishes, publish its inventory at every grade, and report upstream "
               "what the archetype lacks ⟨K4⟩. **Both are Proposed and nothing here is in force**: the graph is built "
               f"and its checker has run ({G['n']} nodes, {G['m']} edges, built at `{G['built']}`; results of "
               "2026.11.07), the three dependent entries are drafted and pending, clause pins are not run in "
               "`drift.rs`, and no overlay ADR-0058 describes is computed. The graph in this tree is the build of "
               "2026.11.07: it holds neither the overlay's eight modules nor the `Workflow` and `Mesh` proofs (G12 "
               "item 111).",
               W, "ADR-0057 provenance (⟨K1⟩–⟨K5⟩), Status note, Context, Decision §1–§14 (§1's table, §3's table, "
               "§11's table, §12's table), Options, Consequences, Findings 1–11, Open obligations, History (R1); "
               "ADR-0058 provenance, Status note, Context, Decision §1–§12 (§1's table, §8's table, §9's table, §10's "
               "table), Options, Consequences, Findings 1–5, Open obligations, History; spec/README.md (the paragraph "
               "on `specification-graph.json`); the docstring of spec/specification-graph.py; "
               "spec/specification-graph.json, read at build time (the build of 2026.11.07 in this tree: counts, "
               "layers, types, the picture's seventeen edges, `route: false`, the binding section; a rebuilt graph "
               "moves every count read from it); spec/specification-graph-results-2026.11.07.txt, read at build time "
               "(header, stale edges, unread clauses, twice-stated, unchecked modules, edges up, the four lists, the "
               "inventory at grade trusted, the premise routes, held at each grade, Result); decisions/ADR-0057.md "
               "§14, read at build time for the digests and counts it cites; ADR-0033 A18, ADR-0045 A5, ADR-0053 A1 "
               "(pending, drafted 2026.11.07); ADR-0045 Annex A (T-0045-3, T-0045-28, T-0045-31, T-0045-37); ADR-0023 "
               "§2, §4–§7; ADR-0053 §5 R7; ADR-0049 §4; ADR-0029 A2; ADR-0046; G12 §9's table row and items 76, 103, "
               "111; mechanism/GAPS-AND-ASSUMPTIONS.md I47, I49 as ADR-0057 cites them", state=STATE_G12)
    X0, X1 = c.x0, c.x1
    WW = X1 - X0
    y = c.y

    # ================================================================== status strip
    c.text(X0, y + 15, "Status", 15, "faint", bold=True)
    px0 = X0 + 80
    px = px0
    strip = [
        ("ADR-0057", "proposed", f"C2, C4 · drafted {REC['date']} · R1 2026.11.07", None),
        ("ADR-0058", "proposed", "C2 · drafted 2026.11.06 · rests on ADR-0057", None),
        ("`spec/specification-graph.json`", None, f"Built 2026.11.07 at `{G['built']}` · not in force", "teal"),
        ("its checker, `specification-graph.py check`", None, "Run 2026.11.07 · well formed, the four lists agree", "teal"),
        ("the graph against the tree at G12", None, f"Behind: holds {REC['mods']} of 41 modules, {REC['proofs']} of 34 "
                                                    "proof modules (G12 item 111)", "red"),
        ("ADR-0033 A18 · ADR-0045 A5 · ADR-0053 A1", None, "Pending, drafted 2026.11.07", "amber"),
        ("clause pins in `drift.rs` (§7)", None, "Not run · A18 records no run", "red"),
        ("ADR-0058 §12's computed overlays", None, "Not computed", "red"),
        ("ADR-0058's dependent entries (ADR-0023 §6; the Guide)", None, "Not drafted", "red"),
    ]
    for lab, key, extra, pacc in strip:
        lw = text_width(lab, 13.5, True) + 8
        if key:
            pw = text_width(STATUS[key][0] + (f" · {extra}" if extra else ""), 11.5, True) + 18
        else:
            pw = text_width(extra, 11.5, True) + 18
        if px + lw + pw > X1:
            px = px0
            y += 34
        c.text(px, y + 15, lab, 13.5, "ink", bold=True)
        px += lw
        if key:
            px += c.status(px, y, key, extra) + 26
        else:
            px += c.pill(px, y, extra, pacc, 11.5, dash=None if pacc == "teal" else "6 4") + 26
    y += 42
    y += c.para(X0, y, WW, "**Proposed means nothing here is in force.** The custodian settled five things on 2026.11.06: "
                "the set of layers is open ⟨K1⟩; inheritance is graded ⟨K2⟩; the graph carries no brand name ⟨K3⟩; "
                "there are two records, ADR-0057 for the corpus and ADR-0058 for adopters and the ecosystem ⟨K4⟩; both "
                "are prescriptive, saying what to produce and what the corpus does, should do and could do ⟨K5⟩. Every "
                "other choice is the drafter's. **C2** applies to both because each makes an exhaustiveness claim (every "
                "relation the corpus relies on is an edge; every edge an inventory relies on is in the overlay); **C4** "
                "applies to ADR-0057 because three open-list items (G11 56, 90, 103) become computed. **Nothing in "
                "ADR-0057 changes a theorem, a premise or a verdict at the reference**: at grade *trusted* its inventory "
                "is the one `inventory.py` computes today (§5; the checker confirms it theorem by theorem). One author, "
                "one day, for both; R1 built and not reviewed.", 14.5, "muted") + 34

    # ================================================================== band 1: the picture
    y = band(c, X0, y, "The graph, drawn on seventeen of its edges: five layers of nodes, and the edges that discharge "
                       "them (ADR-0057 §1, §3; the edges from the graph file; fresh or stale from the results file)")
    PICW = 2190
    KX = X0 + PICW + 40
    KW = X1 - KX
    cx = [X0 + 20 + i * 360 for i in range(6)]
    CW, NW, G_ = 330, 250, 50
    top = y + 16

    # measure the node rows
    rec_specs = [
        (cx[0], CW, "`ADR-0037 §4`", "a clause of a record (§2); read by `Seats.tla` ④", "blue"),
        (cx[1], CW, "`ADR-0039 §2`", "the admit decision's record; `Admit.lean` transcribes the code that follows it ⑩", "blue"),
        (cx[2], CW, "`ADR-0030 §1`", "read by `FloorComposition.tla` ⑰", "blue"),
        (cx[3], CW, "`ADR-0050 §2`", "read by `Operators.tla` ⑫", "blue"),
        (cx[4], CW, "`ADR-0031 §4`", "one of the clauses `Mechanism.tla` reads ⑭", "blue"),
        (cx[5], CW, f"{G['clauses']} clauses of {G['records']} records", f"{G['by_layer']['record']} nodes in this "
                    "layer (a record and each of its clauses, §2, §7); the rest are not drawn", "grey"),
    ]
    h_rc = max(node(c, 0, 0, w, t, s, a, draw=False) for _, w, t, s, a in rec_specs)
    y_r = top
    c.region(X0, y_r, PICW, 26 + h_rc + 18, "record", "blue")
    for x, w, t, s, a in rec_specs:
        node(c, x, y_r + 26, w, t, s, a, h=h_rc, tint=(a != "grey"))
    h_R = 26 + h_rc + 18

    y_a = y_r + h_R + G_
    asr = (cx[5], CW, "`ADR-0045` Annex A, Annex B; the binding table (`.md`, `.json`)",
           f"{G['by_layer']['assurance']} nodes. The rows stand where edges would be: T-0045-28 is ⑤", "blue")
    h_ac = node(c, 0, 0, asr[1], asr[2], asr[3], asr[4], draw=False)
    c.region(X0, y_a, PICW, 26 + h_ac + 18, "assurance", "blue")
    node(c, asr[0], y_a + 26, asr[1], asr[2], asr[3], asr[4])
    h_A = 26 + h_ac + 18

    y_m = y_a + h_A + G_
    m1 = [
        (cx[1], NW, "`spec/Seats_proof.tla`", "the proof module: every obligation proved (T-0045-31) ①", "teal"),
        (cx[2], NW, "`spec/FloorComposition.tla`", "the admit decision's module; proved by its proof module (not drawn)", "teal"),
        (cx[3], NW, "`spec/Operators.tla`", "the operator path's module; proved by its proof module (not drawn)", "teal"),
        (cx[4], NW, "`spec/Mechanism.tla`", "the trace-validation model; reads 31 clauses (one drawn)", "teal"),
    ]
    m2 = [
        (cx[1], NW, "`spec/lean/TopakSpec/Seats.lean`", "the Lean encoding; the graph check ② and the Lean proof ③", "teal"),
    ]
    minfo = (cx[5], CW, f"{G['by_layer']['model']} nodes in this layer", f"{REC['mods']} modules, {REC['proofs']} proof "
             "modules and 14 encodings at the 2026.11.07 build (§14); the tree at G12 has 41 and 34 (item 111)", "grey")
    h_m1 = max(node(c, 0, 0, w, t, s, a, draw=False) for _, w, t, s, a in m1)
    h_m2 = max(node(c, 0, 0, w, t, s, a, draw=False) for _, w, t, s, a in m2)
    h_mi = node(c, 0, 0, minfo[1], minfo[2], minfo[3], minfo[4], draw=False)
    h_seats = h_m1 + 14 + h_m2
    if h_mi > h_seats:
        h_m2 += h_mi - h_seats
        h_seats = h_m1 + 14 + h_m2
    c.region(X0, y_m, PICW, 26 + h_seats + 18, "model", "teal")
    node(c, cx[0], y_m + 26, NW, "`spec/Seats.tla`", "the module whose two theorems are the only ones with a route "
         "to the code besides the row (§4); discharged by ①②③, ⑤⑥⑦; reads ④", "teal", h=h_seats)
    for x, w, t, s, a in m1:
        node(c, x, y_m + 26, w, t, s, a, h=h_m1)
    for x, w, t, s, a in m2:
        node(c, x, y_m + 26 + h_m1 + 14, w, t, s, a, h=h_m2)
    node(c, minfo[0], y_m + 26, minfo[1], minfo[2], minfo[3], minfo[4], h=h_seats, tint=False)
    h_M = 26 + h_seats + 18
    y_sb = y_m + 26 + h_seats   # bottom of Seats.tla

    y_p = y_m + h_M + G_
    p1 = (cx[5], CW, "`floor/genesis-floor.cedar`", "the genesis floor, genesis-provisional (ADR-0030 A3)", "violet")
    p2 = (cx[5], CW, "`floor/proposed/workflow-floor.cedar`", "the linked stage; Proposed (G11 item 102; finding 6)",
          "amber")
    pinfo = (cx[4], CW, f"{G['by_layer']['policy']} nodes in this layer", "the genesis floor, four proposed stages and "
             "`floor/lean`; the three other stages' generated edges are not drawn", "grey")
    h_p1 = max(node(c, 0, 0, p1[1], p1[2], p1[3], p1[4], draw=False),
               node(c, 0, 0, pinfo[1], pinfo[2], pinfo[3], pinfo[4], draw=False))
    h_p2 = node(c, 0, 0, p2[1], p2[2], p2[3], p2[4], draw=False)
    PG = 60
    c.region(X0, y_p, PICW, 26 + h_p1 + PG + h_p2 + 18, "policy", "violet")
    node(c, p1[0], y_p + 26, p1[1], p1[2], p1[3], p1[4], h=h_p1, tint=False, dash="4 3")
    node(c, p2[0], y_p + 26 + h_p1 + PG, p2[1], p2[2], p2[3], p2[4], h=h_p2, tint=False, dash="6 4")
    h_P = 26 + h_p1 + PG + h_p2 + 18
    y_wf_top = y_p + 26 + h_p1 + PG
    y_wf_bot = y_wf_top + h_p2
    y_gf_bot = y_p + 26 + h_p1

    y_i = y_p + h_P + G_
    i1 = [
        (cx[0], NW, "`mechanism`", "the reference as a whole: the trusted edge's lower end is the row T-0045-28 ⑤", "teal"),
        (cx[1], cx[4] + CW - cx[1], "`mechanism/crates/topak-core`", "`State::apply`, `admit.rs`, the operator path; "
         "read by the drafter ⑥, transcribed into `mechanism/lean` ⑦ ⑨ ⑩, replayed ⑧ ⑬, tested ⑪", "teal"),
        (cx[5], CW, "`mechanism/crates/topak-floor`", "links the stage by digest (`PINNED_*_SHA256`) ⑮", "teal"),
    ]
    i2 = [
        (cx[0], NW, "`mechanism/lean/Topak/SeatsModel.lean`", "a model of `apply`, in `mechanism/lean`; replayed ⑧", "teal"),
        (cx[1], 690, f"{G['by_layer']['implementation']} nodes in this layer", "the reference, its eight crates and "
         "scripts, and `mechanism/lean`'s five files; the rest are not drawn", "grey"),
    ]
    h_i1 = max(node(c, 0, 0, w, t, s, a, draw=False) for _, w, t, s, a in i1)
    h_i2 = max(node(c, 0, 0, w, t, s, a, draw=False) for _, w, t, s, a in i2)
    IG = 50
    c.region(X0, y_i, PICW, 26 + h_i1 + IG + h_i2 + 18, "implementation", "teal")
    for x, w, t, s, a in i1:
        node(c, x, y_i + 26, w, t, s, a, h=h_i1)
    for x, w, t, s, a in i2:
        node(c, x, y_i + 26 + h_i1 + IG, w, t, s, a, h=h_i2, tint=(a != "grey"))
    h_I = 26 + h_i1 + IG + h_i2 + 18
    y_it = y_i + 26               # top of row 1
    y_i2m = y_i + 26 + h_i1 + IG + h_i2 / 2

    # the five layers with no node today
    y_e = y_i + h_I + 36
    c.text(X0, y_e + 13, "Layers with no node at the 2026.11.07 build (§1; the results header):", 13, "faint", bold=True)
    y_e += 24
    empties = [("intent", "The ToO's principles and threat model; ADR-0025's intent, \"the sole axiom\""),
               ("vocabulary", "`narrative/glossary.md`"),
               ("interface", "Schema S; the allowlist entry (ADR-0049); every format the format inventory lists"),
               ("runtime", "Recorded traces; the trace-validation results"),
               ("deployment", "A deployment's declaration (ADR-0058)")]
    ew = (PICW - 4 * 20) / 5
    h_e = max(node(c, 0, 0, ew, f"{l} · {R['by_layer'][l]} nodes", s, "grey", draw=False) for l, s in empties)
    for k, (l, s) in enumerate(empties):
        node(c, X0 + k * (ew + 20), y_e, ew, f"{l} · {R['by_layer'][l]} nodes", s, "grey", h=h_e, tint=False, dash="2 3")
    y_pic_end = y_e + h_e

    # ---- arrows
    def A(num, pts, lab_at=None, lab=None):
        ty = next(p[1] for p in PIC if p[0] == num)
        key = next((p[1], p[2], p[3]) for p in PIC if p[0] == num)
        stale = key in R["stale_keys"]
        acc = "red" if stale else TACC[ty]
        c.arrow(pts, acc, sw=2)
        if lab_at:
            c.label(lab_at[0], lab_at[1], lab or num, acc, 12.5)

    y_row1 = y_m + 26 + h_m1 / 2
    y_row2 = y_m + 26 + h_m1 + 14 + h_m2 / 2
    midgap = cx[0] + NW + (cx[1] - cx[0] - NW) / 2
    A("①", [(cx[1], y_row1), (cx[0] + NW, y_row1)], (midgap, y_row1 - 20))
    A("②", [(cx[1], y_row2), (cx[0] + NW, y_row2)], (midgap, y_row2 - 20), "② ③")
    y_rb = y_r + 26 + h_rc
    y_al = y_a + h_A / 2
    A("④", [(cx[0] + NW / 2, y_m + 26), (cx[0] + NW / 2, y_rb)], (cx[0] + NW / 2, y_al), "④ read, by the drafter")
    A("⑰", [(cx[2] + NW / 2, y_m + 26), (cx[2] + NW / 2, y_rb)], (cx[2] + NW / 2, y_al), "⑰ read, by the drafter")
    A("⑫", [(cx[3] + NW / 2, y_m + 26), (cx[3] + NW / 2, y_rb)], (cx[3] + NW / 2, y_al), "⑫ read, by the drafter")
    A("⑭", [(cx[4] + NW / 2, y_m + 26), (cx[4] + NW / 2, y_rb)], (cx[4] + NW / 2, y_al), "⑭ read, by the drafter")
    lane1 = cx[1] + NW + (CW - NW) / 2 + 10
    A("⑩", [(lane1, y_it), (lane1, y_rb)], (lane1, y_al + 40), "⑩ stale")
    y_pl = y_p + 26 + h_p1 / 2          # labels for the verticals through the policy band
    A("⑤", [(cx[0] + NW / 2, y_it), (cx[0] + NW / 2, y_sb)], (cx[0] + NW / 2, y_pl + 70), "⑤ trusted")
    y_pa, y_pb = y_p + 30, y_p + 70
    gapx = cx[0] + CW + (cx[1] - cx[0] - CW) / 2
    A("⑥", [(cx[1] + 90, y_it), (cx[1] + 90, y_pa), (cx[0] + 230, y_pa), (cx[0] + 230, y_sb)], (gapx, y_pa))
    A("⑦", [(cx[1] + 40, y_it), (cx[1] + 40, y_pb), (cx[0] + 180, y_pb), (cx[0] + 180, y_sb)], (gapx, y_pb))
    A("⑧", [(cx[1], y_it + h_i1 * 0.72), (gapx, y_it + h_i1 * 0.72), (gapx, y_i2m), (cx[0] + NW, y_i2m)],
      (gapx, (y_it + h_i1 * 0.72 + y_i2m) / 2))
    y_m1b = y_m + 26 + h_m1
    A("⑨", [(cx[2] + NW / 2, y_it), (cx[2] + NW / 2, y_m1b)], (cx[2] + NW / 2, y_pl), "⑨ proved of a reading · stale")
    A("⑪", [(cx[3] + NW / 2, y_it), (cx[3] + NW / 2, y_m1b)], (cx[3] + NW / 2, y_pl), "⑪ tested")
    A("⑬", [(cx[4] + NW / 2, y_it), (cx[4] + NW / 2, y_m1b)], (cx[4] + NW / 2, y_pl - 50), "⑬ replayed · stale")
    A("⑮", [(cx[5] + CW / 2, y_it), (cx[5] + CW / 2, y_wf_bot)], (cx[5] + CW / 2, y_wf_bot + G_ / 2 + 9), "⑮ executed")
    A("⑯", [(cx[5] + CW / 2, y_wf_top), (cx[5] + CW / 2, y_gf_bot)], (cx[5] + CW / 2, y_gf_bot + PG / 2),
      "⑯ generated")

    # ---- the key, on the right
    ky = top - 10
    c.text(KX, ky + 16, "The seventeen edges, from the graph file; fresh or stale from the results file (§3, §4)", 16,
           "ink", bold=True)
    ky += 30
    kcols = [("#", 40, {"bold": True}), ("Type", 150, {"bold": True}), ("From → to", 420, {}),
             ("What the edge leaves (the graph's `leaves`)", 350), ("At 2026.11.07", 112), ("Route", KW - 1072)]
    krows = []
    for num, ty, frm, to in PIC:
        e = G["index"][(ty, frm, to)]
        route = "not a route (`route: false`; finding 8)" if e.get("route") is False else "—"
        rd = e.get("reader")
        leaves = e.get("leaves", "")
        if rd and ty == "read":
            leaves = f"the reader: {rd}"
        elif rd:
            leaves += f"; reader: {rd}"
        krows.append({"cells": [num, f"[[{TACC[ty]}|{ty}]]", f"`{frm}` → `{to}`", leaves,
                                fresh_word(R, (ty, frm, to)), route],
                      "accent": "red" if (ty, frm, to) in R["stale_keys"] else None})
    ky += c.table(KX, ky, kcols, krows, size=12.5, accent="grey") + 22
    ky = stack(c, KX, ky, KW, [
        ("What the picture is, and is not", [
            f"**Seventeen of {G['m']} edges**, chosen by the diagram around `Seats`, the only module whose theorems have "
            "a route to the code besides the row (§4), and around the strongest edge, ⑮, which ends at a node not in "
            "force (finding 6). An edge runs from a lower node to the node it discharges (§3).",
            f"**{len(stale_drawn)} of the eight stale edges are drawn** ({', '.join(stale_drawn)}), in red. Every "
            "module's edge up to its record is *read*, by the drafter (finding 10); only four are drawn.",
            "Layers are labels for reading and carry no premise (§1); the picture stacks the five that have nodes. The "
            "assurance layer's rows are not nodes: a *trusted* edge's lower end is a row (§3).",
        ], "grey", {"tint": False}),
        ("How a theorem's grade is read off the picture (§5)", [
            "`OnlyThinkersAuthor` and `OneSeatPerPrincipal` are `invariant(Seats)` by ① and `refines(Seats)` by ⑤, "
            "or by ⑦ + ⑧ (`model-faithful(apply/Seats)`). **Their grade is the strongest, over the routes that hold, "
            "of each route's weakest edge**: ⑤ holds, so *trusted*; the Lean route is stale, so no higher.",
            "At grade *trusted* the inventory is today's: 19 of 43 of Annex B hold, the same theorems `inventory.py` "
            "holds. **No theorem of Annex B holds at any grade above *trusted*** (the results file's \"held at each "
            "grade\").",
        ], "teal", {}),
    ], gap=16, size=13.5)
    y = max(y_pic_end, ky) + 60

    # ================================================================== band 2: nodes, layers, clauses
    y = band(c, X0, y, "1 · Nodes are artifacts with open layers (ADR-0057 §1); a record's guarantees are numbered "
                       "clauses (§2)", status="proposed")
    wl = 1900
    xr = X0 + wl + 50
    wr = X1 - xr
    lcols = [("Layer", 180, {"bold": True}), ("What it holds in the corpus (§1)", 980),
             ("Nodes at the 2026.11.07 build (the diagram's column: results header; graph file)", wl - 1160)]
    lrows = []
    for l in LAYERS:
        hold = {"intent": "The ToO's principles and threat model; ADR-0025's intent, \"the sole axiom\"",
                "vocabulary": "`narrative/glossary.md`",
                "record": "`decisions/`, and the checkpoint that is the state of record",
                "assurance": "ADR-0045 Annex A and B; the binding table; the residual-risk statement",
                "model": "`spec/*.tla`; the proof modules; `spec/lean/`",
                "interface": "Schema S; the allowlist entry (ADR-0049); every format the format inventory lists",
                "policy": "`floor/` and its stages; `policies/`",
                "implementation": "`mechanism/` crates; `mechanism/lean/`, as a transcription of them",
                "runtime": "Recorded traces; the trace-validation results",
                "deployment": "A deployment's declaration (ADR-0058)"}[l]
        rn, gn = R["by_layer"][l], G["by_layer"].get(l, 0)
        cell = f"**{rn}**" if rn == gn else f"[[red|results {rn}, graph file {gn}]]"
        if rn == 0 and gn == 0:
            cell = "[[red|0]] · no node yet"
        lrows.append([f"**{l}**", hold, cell])
    for l in sorted(set(G["by_layer"]) - set(LAYERS)):
        lrows.append({"cells": [f"**{l}**", "a layer the record does not list: open set (§1)", f"**{G['by_layer'][l]}**"],
                      "accent": "amber"})
    t = c.table(X0, y, lcols, lrows, size=13.5, accent="blue")
    yl = y + t + 20
    yl = stack(c, X0, yl, wl, [
        ("A node, and its layer (§1)", [
            "**A node is an artifact that states something normative or checks something stated**: a record's clause, "
            "a module, a proof module, a Lean file, a floor stage, a Rego policy, a crate or a function in it, a schema. "
            "Named by its path, or by record and section; its content identified by digest.",
            "**The set of layers is open ⟨K1⟩.** A new kind of artifact is given a layer name when it first enters the "
            "graph, and no record is needed to add one *(drafter's choice: a layer carries no premise; only edges do, §4)*.",
            "**No name beyond its description**, *the specification graph* ⟨K3⟩.",
        ], "blue", {"tint": False}),
    ], size=14)
    yr = stack(c, xr, y, wr, [
        ("The clause is the binding point above the model layer (§2)", [
            "A numbered subsection of a record's Decision, with its inline amendments, cited as the corpus already cites "
            "it (\"ADR-0031 §4, A1\"). Records are append-only with typed History rows, so **a clause's number is "
            "stable**. A clause may number its guarantees `§n.k`.",
            "**Records already ratified are not rewritten.** Their givens are read from the binding table, their "
            "discharge from the graph. A clause gains the four parts when an amendment next touches it.",
        ], "blue", {"tint": False}),
        ("A record drafted after ADR-0057 gives each clause four parts, in this order (§2)", [
            "**Goal.** One sentence: why the clause exists. Not normative, and not bound.",
            "**Givens.** What the guarantees rest on: rows, parameters, derived premises and other clauses, by id. "
            "\"None beyond BASE\" is a claim, stated as one.",
            "**Guarantees.** The normative statements, numbered.",
            "**Discharge.** The edges that discharge each guarantee (§3), with their types, or \"none yet\", stated as a "
            "claim. Named *discharge* and not *gate* *(drafter's choice; the custodian proposed \"gates\")*: the corpus "
            "already has floor gates and promotion gates, and a record's own gate is its Ratification condition.",
        ], "amber", {"tint": False}),
        (f"What the graph holds at the 2026.11.07 build (§14 ⟨R1⟩; the graph file)", [
            f"**{G['n']} nodes**: {G['clauses']} clauses of {G['records']} records, among them every clause of the 42 "
            f"records the reference follows; the {REC['mods']} modules and {REC['proofs']} proof modules; 14 Lean "
            "encodings and `mechanism/lean`'s five files; the genesis floor, its four stages and `floor/lean`; the "
            "reference's eight crates, its scripts and the reference as a whole.",
            f"**{G['m']} edges**, each typed and pinned: " + ", ".join(f"{t} {G['by_type'][t]}" for t in TYPES) + ".",
            ("**§14's counts match the graph file.**" if rec_agree else
             f"[[red|§14's counts differ from the graph file]]: the record says {REC['n']} nodes, {REC['m']} edges, "
             f"{REC['clauses']} clauses of {REC['records']} records; the file has {G['n']}, {G['m']}, {G['clauses']} of "
             f"{G['records']}. The graph was rebuilt after R1 and the record not revised."),
            ("**The results header matches the graph file**, node for node and type for type." if counts_agree else
             f"[[red|The results file of 2026.11.07 and the graph file disagree]]: results {R['n']} nodes, {R['m']} "
             f"edges; graph file {G['n']}, {G['m']}. The checker has not been rerun on this graph."),
        ], "teal", {}),
    ], gap=16, size=14)
    y = max(yl, yr) + 80

    # ================================================================== band 3: the eight edge types
    y = band(c, X0, y, "2 · Every edge is typed by what it leaves to a person: eight types, strongest first (ADR-0057 "
                       "§3 ⟨K2⟩)", status="proposed")
    ecols = [("Type", 190, {"bold": True}), ("The lower node", 640), ("What the edge leaves", 560),
             ("In the corpus today (§3)", 1230), ("Edges at the 2026.11.07 build (the diagram's column)", WW - 2620)]
    E3 = [
        ("executed", "Is the higher, run as written", "The engine that runs it (a row)",
         "The linked floor stage, pinned by digest (`PINNED_*_SHA256`); Cedar on T-0045-3"),
        ("generated", "Is produced from the higher by a pinned tool and not edited", "The generator",
         "The floor stages, built by `floor/proposed/build.py` from the genesis files"),
        ("proved", "Is related to the higher by a machine-checked proof between two formal artifacts: implication, "
                   "refinement, or equal state graphs", "The prover or kernel (a row)",
         "Proof modules to their modules (T-0045-31); the graph check of the `Seats`, `FloorComposition` and "
         "`Emergency` encodings (T-0045-37)"),
        ("proved of a reading", "Is proved, but one end is a hand transcription or a model of the other",
         "The reading (`enc-faithful`, `model-faithful`), which a check may support",
         "`mechanism/lean/` `Admit.lean`, `Clock.lean`, `FloorRefinement.lean`, `SeatsModel.lean`"),
        ("replayed", "Has its recorded behaviour replayed through the higher, step by step", "The paths no trace reached",
         "The reference's traces through `spec/Mechanism.tla` and `spec/ConfinementRefinement.tla`; the Lean replays"),
        ("tested", "Passes tests named after the higher's properties",
         "The inputs no test chose, and whether the tests state the properties",
         "`Operators.tla` and the reference (I47); the floor gates' case suites"),
        ("read", "Was written against the higher and read by a person", "The reader",
         "Every module against its record; the Rust against its records; the narrative"),
        ("trusted", "Has no edge; a row stands where the edge would be", "The row",
         "T-0045-28, for every theorem whose route reaches the code"),
    ]
    erows = []
    for ty, lower, leaves, today in E3:
        gn, rn = G["by_type"][ty], R["by_type"][ty]
        n_stale = sum(1 for s in R["stale"] if s["type"] == ty)
        cell = f"**{gn}**" if gn == rn else f"[[red|graph file {gn}, results {rn}]]"
        if n_stale:
            cell += f" · [[red|{n_stale} stale]]"
        if ty == "read":
            cell += f" · {R['up']} modules' edges up, all by the drafter"
        erows.append([f"[[{TACC[ty]}|{ty}]]", lower, leaves, today, cell])
    y += c.table(X0, y, ecols, erows, size=13.5, accent="grey") + 22
    y += row_cards(c, X0, y, WW, 30, [
        ("A citation is not an edge (§3)", [
            "A record citing another, or code citing a record in a comment, **discharges nothing**; it is how a reader "
            "finds the edge.",
        ], "grey", {"tint": False}),
        ("A read edge names its reader (§3)", [
            "A reading by the drafter and a reading by someone else are **the same type**, and the graph shows which it "
            "was (ADR-0053 R1(b), ADR-0029 A2).",
            "Mutations and witnesses (ADR-0046) support a reading: they show the module tells the clause from its "
            "negation, not that it reads the clause rightly. **They do not change the edge's type.**",
        ], "brown", {"tint": False}),
        ("An edge is fresh or stale (§3)", [
            "It pins the content of both ends: by clause for records (§7), by digest otherwise. **An edge whose pin no "
            "longer matches is stale**, and is re-pinned by the review `drift.rs` already asks for: read the change, "
            "bring the lower node into line or register why not, then re-pin.",
            "The builder keeps an edge's pins until `--repin` names it: re-pinning is the review (the docstring).",
        ], "red", {"tint": False}),
        ("The method is the corpus's choice; the type is not (§10)", [
            "Which formalism states a node is chosen by the kind of property: a protocol in TLA+, an authorization in "
            "Cedar, a functional core in Lean, a data shape in a schema.",
            "**Some components cannot be specified, and the architecture keeps them outside the verified object** "
            "(ADR-0007, ADR-0016): nodes with no edge below the record, so every theorem that would need one is "
            "computed void rather than assumed. A new method enters with its toolchain row (ADR-0045 §4).",
        ], "teal", {"tint": False}),
    ], size=14) + 80

    # ================================================================== band 4: premises, grades, the rest of the decision
    y = band(c, X0, y, "3 · Each edge is a premise (§4), a theorem is inherited at a grade (§5), and the rest of the "
                       "decision (§6–§9, §13)", status="proposed")
    y += row_cards(c, X0, y, WW, 30, [
        ("Each edge contributes a named premise (§4)", [
            "An edge of type *t* from *x* to *y* contributes **`edge(t, x → y)`**, a premise column of kind `check` "
            "(ADR-0053 R7): its value is the edge's freshness and, where the type has a results file, that file's "
            "verdict. **A stale edge's premise is false. An absent edge's premise is false**, as an undeclared row is "
            "(ADR-0045 §3, rule 1).",
            "**ADR-0053's derived premises become instances**, and nothing they compute changes: `invariant(M)` is "
            "T-0045-31, or T-0045-37 with `edge(proved of a reading, encoding(M) → M)`; `refines(Seats)` is T-0045-28, "
            "or the route through `SeatsModel`.",
            "**T-0045-28 becomes a derived premise for every theorem whose route reaches the code**: the row, or any "
            "route of edges from the implementation to the module. Today the row is the only route for every theorem "
            f"but the two of `Seats`, so no verdict moves. The graph's `binding` section holds {G['derived']} derived "
            "premises, `reaches-code(…)` among them.",
            "**An edge is added with its premise in the same commit**, and `inventory.py --check` passes before it lands.",
        ], "teal", {}),
        ("A theorem is inherited at a grade; each grade is a binary inventory (§5 ⟨K2⟩)", [
            "**A grade is an edge type used as a threshold.** The inventory at grade *g* is ADR-0023 §2's inventory "
            "computed with every edge premise of a type weaker than *g* set false. A theorem holds at *g* when it is "
            "present there; **its grade is the strongest *g* at which it holds**: over the routes that hold, the "
            "strongest of each route's weakest edge. Rows, parameters and gap premises hold or fail as today.",
            "**At grade *trusted* the inventory is the one the corpus computes today.** Raising the grade can only void "
            "a theorem, never revive one. ADR-0023 §2 holds at every grade: present or absent, no weaker version.",
            "**Graded on its way down** *(drafter's choice)*: over the edges from the layer a theorem is stated at to the "
            "layer that runs. **The edges up, from a module to its record, are graded once per module** and reported "
            "beside the inventory: every one is *read* today, by the drafter (finding 5).",
        ], "teal", {}),
        ("A guarantee stated twice is two nodes and an edge (§6)", [
            "The graph holds both and the typed edge between them. The operator envelope (I47 (e)) is a Cedar node and "
            "a Rust node with a *tested* edge. **The checker lists every such pair with its type**, so each is raised "
            "(generated from the other, or proved equal) or kept with the type showing. Listing is this record's "
            "obligation; raising is not.",
            f"The checker lists **{R['twice'][0][0] if R['twice'] else 'none'}** (band 5).",
        ], "teal", {"tint": False}),
    ], size=14) + 26
    y += row_cards(c, X0, y, WW, 30, [
        ("Pins bind to clauses (§7)", [
            "The drift pins move from whole files to clauses for records: **a record's pin is the digest of each clause "
            "the reference follows**, by section, with its inline amendments. A History row, a status line or a pending "
            "amendment not yet inline changes no clause and trips no pin. Modules, floor files and code stay pinned by "
            "file. `drift.rs`'s rule that every cited record or module is pinned is kept, read by clause.",
            "**A debt against ADR-0033, not a change to it**: ADR-0033 A18 is drafted (2026.11.07) and pending; it "
            "records no run. `spec/clauses.py` splits and pins a record's clauses (finding 9b).",
        ], "amber", {"tint": False, "status": "notbuilt", "status_extra": "in `drift.rs`; A18 pending"}),
        ("One graph, and the four lists are read against it (§8)", [
            "**One machine-readable file under `spec/`**, of nodes and typed edges, each with its pins and evidence by "
            "digest. A checker computes every stale edge; every clause with guarantees and no discharging edge; every "
            "twice-stated guarantee; and, through `inventory.py`, the inventory at each grade with each theorem's grade "
            "and route.",
            "**Checked against it first, generated from it later** *(drafter's choice)*: `corpus-pins.sha256`, the "
            "binding JSON's `check` columns, the manifest index and the sync scripts' file lists each gain a check that "
            "they agree with the graph. **The binding table stays canonical for its row premises.**",
        ], "teal", {}),
        ("Interfaces are a layer (§9); the trusted base (§13)", [
            "**A format gains an interface node, with a machine-readable schema, when a record next touches it** "
            "*(drafter's choice: not a sweep)*: JSON Schema for a lease, an allowlist entry, a tool result; AsyncAPI for "
            "a topic and its records. Its edges run to the clause that defines it and from the code and the floor that "
            "read it. The interface layer has no node today.",
            "**No row is added (§13).** The checker decides no admit, promotion or issuance; its failure can misstate a "
            "grade, a claim about evidence and not an addition of authority. A grade is only as good as the graph, as "
            "a verdict is only as good as the declaration.",
        ], "grey", {"tint": False}),
    ], size=14) + 80

    # ================================================================== band 5: does, should, could
    y = band(c, X0, y, "4 · The corpus against ADR-0057: what it does, should do and could do (§11 ⟨K5⟩)",
             status="proposed")
    dcols = [("", 200, {"bold": True}), ("Does", 900), ("Should (this record)", 1000), ("Could (not decided here)",
                                                                                           WW - 2100)]
    drows = [
        ["**Layers**", "Records, models, proofs, Lean, floor, bundle, reference, manifests",
         "Name each node's layer; add layers as artifacts arrive (§1)", "—"],
        ["**Guarantees**", "Clauses cited by section; premises held in the binding, not the record",
         "Goal, givens, guarantees, discharge in each new clause (§2)",
         "Export the assurance layer as GSN for an outside reviewer"],
        ["**Edges**", "Pins, sync scripts, derived premises, each apart",
         "Type every edge; contribute its premise; one graph (§3, §4, §8)", "Generate the four lists from the graph"],
        ["**Grades**", "Holds or void", "Inventory at each grade (§5)",
         "Per-axis grades, if the order of §3 is found wrong (finding 4)"],
        ["**Drift**", "Whole-file pins", "Clause pins (§7)", "—"],
        ["**Twice-stated**", "Tied by tests (I47 (e))", "Listed with their type (§6)",
         "Generate the Rust envelope from the Cedar, or prove them equal"],
        ["**Model to code**", "T-0045-28 trusted; replay; transcriptions read by the drafter",
         "T-0045-28 as a derived premise with every route (§4)",
         "Rust-to-Lean extraction (Aeneas) in place of hand transcription, removing `enc-faithful` for the mechanism; "
         "Verus or Kani on local properties"],
        ["**Coverage of replay**", "Tested paths only; workflows not replayed", "Stale and missing edges reported (§8)",
         "Tests generated from the modules (model-based testing), the downward complement of replay"],
        ["**Interfaces**", "Prose and schema S", "A schema node when a record touches a format (§9)",
         "AsyncAPI for every topic"],
        ["**Runtime**", "Replay of test traces", "—", "Monitors derived from the modules' invariants in a deployment"],
    ]
    y += c.table(X0, y, dcols, drows, size=13.5, accent="grey") + 80

    # ================================================================== band 6: the checker's lists
    y = band(c, X0, y, "5 · The checker's lists, read from spec/specification-graph-results-2026.11.07.txt (§8, §14; "
                       "spec/README.md)", status="proposed")
    y += c.para(X0, y, WW, f"**The checker ran 2026.11.07 on the graph built at `{R['built']}`** ({R['n']} nodes, "
                f"{R['m']} edges). Well formed: **{R['well']}**. **Result line:** \"{R['result']}\". It exits 1 if the "
                "graph is malformed, a list disagrees with it, or the inventory at grade *trusted* differs from "
                "`inventory.py`'s for Annex B; stale edges and a premise route that differs are reported, not failed on "
                "(the docstring). **The graph was built at `9749dfa` and does not hold the overlay's modules or the "
                "`Workflow` and `Mesh` proofs** (G12 item 111); every count here is of that build.", 14.5, "muted") + 20
    scols = [("Evidence file", 330, {}), ("Type", 170, {"bold": True}), ("From → to", 560), ("Premise", 220),
             ("What moved since the pin (the results file)", WW - 1280)]
    srows = []
    for s in R["stale"]:
        srows.append({"cells": [f"`{s['group']}`", f"[[red|{s['type']}]]", f"`{s['frm']}` → `{s['to']}`",
                                f"`{s['note']}`" if s["note"] != "premise false" else "[[red|premise false]]",
                                "; ".join(f"`{m}`" if not m.startswith("and ") and ":" not in m else m
                                          for m in s["moved"])], "accent": "red"})
    c.text(X0, y + 16, f"Stale edges (§3, §8): {R['stale_n']} of {R['stale_of']}. G11 item 103 (`mechanism/lean` stale) "
           "is the six to `mechanism/lean`'s series; G11 item 56 (workflows not replayed) is the two Mechanism-trace "
           "replays, named without being told (§14)", 15, "red", bold=True)
    y += 30
    y += c.table(X0, y, scols, srows, size=13, accent="red") + 30

    w3 = (WW - 2 * 40) / 3
    xs = [X0, X0 + w3 + 40, X0 + 2 * (w3 + 40)]
    ucols = [("Record", 130, {"bold": True}), ("Clauses no model, stage, proof or check reads", w3 - 130)]
    c.text(xs[0], y + 16, f"Clauses the reference follows with no edge but its own reading (§8): {R['unread'][0]} "
           f"clauses of {R['unread'][1]} of the {R['unread'][2]} records (finding 11)", 15, "ink", bold=True)
    c.text(xs[1], y + 16, "Guarantees stated more than once (§6)", 15, "ink", bold=True)
    c.text(xs[2], y + 16, f"Modules no theorem in the binding is checked in: {R['unchecked'][0]} of "
           f"{R['unchecked'][1]} (G11 item 90, computed)", 15, "ink", bold=True)
    y += 30
    t1 = c.table(xs[0], y, ucols, [[f"`{r}`", cl] for r, cl in R["unread_rows"]], size=13, accent="grey")
    t1 += 16 + c.card(xs[0], y + t1 + 16, w3, None, [
        "No module, stage, proof or check reads them; the code's reading is their only discharge. They include every "
        "clause of ADR-0016, ADR-0035 and ADR-0044, and seven of ADR-0049's nine. **Some are by nature outside any "
        "model (§10)**, such as ADR-0018's decoder; the list is where to look for the rest (finding 11).",
    ], accent="grey", size=13.5, tint=False)
    tw_rows = []
    for g, items in R["twice"]:
        tw_rows.append({"group": g})
        for it in items:
            a, b = it.split("  ~  ", 1) if "  ~  " in it else (it, "")
            stmt, ty = (b.rsplit(": ", 1) if ": " in b else (b, ""))
            tw_rows.append([a, stmt, ty.replace("stale", "[[red|stale]]").replace("no edge", "[[red|no edge]]")])
    t2 = c.table(xs[1], y, [("Statement", (w3 - 160) / 2), ("Beside", (w3 - 160) / 2), ("Edge", 160)], tw_rows,
                 size=13, accent="grey")
    t2 += 16 + c.card(xs[1], y + t2 + 16, w3, "Edges up, from each module to what it reads (§5): graded once per module", [
        f"**read, by the drafter: {R['up']} modules.** Modules that read no record: {R['up_none']}. This is finding 5, "
        "computed (finding 10): the corpus's strongest results sit on its weakest edge type at the top, as the code sits "
        "on T-0045-28 at the bottom.",
    ], accent="brown", size=13.5, tint=False)
    t3 = c.card(xs[2], y, w3, None, [
        f"`{R['unchecked_list']}`",
        "G11's ten, with `Correlator` and the two modules that state no theorem of their own (`RulesFloorBase`, "
        "`RulesFloorNV`) (§14). `Workflow` and `Mesh` are proved since 2026.11.11 (ADR-0054 R7, ADR-0055 R3); the graph "
        "of 2026.11.07 does not hold those proofs.",
    ], accent="red", size=13.5, tint=False)
    t3 += 16 + c.card(xs[2], y + t3 + 16, w3, "The four lists, read against the graph (§8)", [
        f"**`{name}`: {verdict}.** " + " ".join(details) for name, verdict, details in R["lists"]
    ], accent="green" if all(v == "agrees" for _, v, _ in R["lists"]) else "red", size=13.5, tint=False)
    y += max(t1, t2, t3) + 30

    a_same = R["annexb"][0] == R["annexb"][2]
    held = " · ".join(f"{t} {R['held'][t]}" for t in TYPES)
    y += row_cards(c, X0, y, WW, 30, [
        ("The inventory at grade trusted against inventory.py's (§14, condition 2)", [
            f"**Annex B as declared: {R['annexb'][0]} of {R['annexb'][1]} hold by `inventory.py`, {R['annexb'][2]} at "
            f"grade *trusted* by the graph; {R['annexb'][3]}.**" if a_same else
            f"[[red|Annex B: {R['annexb'][0]} of {R['annexb'][1]} hold by inventory.py, {R['annexb'][2]} by the graph]]",
            f"**Held at each grade (Annex B):** {held}. No theorem holds above *trusted*; \"grades will look worse than "
            "the prose\" (Consequences).",
        ], "green" if a_same else "red", {}),
        (f"`premise-routes.sh`'s five declarations against the graph at grade trusted (`{R['routes_file']}`)", [
            f"**{n}-`{name}`**: {a} hold in the file's run, {b} by the graph; {rest}" for n, name, a, b, rest in R["routes"]
        ], "green" if all(a == b for _, _, a, b, _ in R["routes"]) else "amber", {"tint": False}),
        ("The digests ADR-0057 §14 cites, against the files in this tree (the diagram's check)", [
            (f"`{name}`: §14 cites `{REC['cited'][name]}`; the file is `{dig[name]}` · "
             + ("[[green|matches]]" if dig_ok[name] else "[[red|moved]]")) for name in REC["cited"]
        ] + [
            ("**All four match**: the graph, its builder, the clause splitter and the results file are the ones R1 names."
             if all(dig_ok.values()) else
             "[[red|A cited file has moved]]: the record names a build this tree no longer holds; the counts drawn here "
             "are the tree's."),
            "The results file's own Sources line names " + ", ".join(f"`{k}` `{v}`" for k, v in R["src_digests"].items()
                                                                     if k.startswith("spec/specification-graph.json")) +
            ("; it matches the graph file" if R["src_digests"].get("spec/specification-graph.json") == dig["spec/specification-graph.json"]
             else "; [[red|it is not this tree's graph file]]"),
        ], "blue", {"tint": False}),
    ], size=13.5) + 26
    y += row_cards(c, X0, y, WW, 30, [
        ("Edges marked `route: false` in the graph file (finding 8; the diagram's read)", [
            f"**{len(G['route_false'])} edges** carry `\"route\": false`: " + "; ".join(f"`{r}`" for r in G["route_false"]) + ".",
            "Finding 8 names two that reach the code and are not counted as routes: the executed edge from `topak-floor` "
            "to the stage it links, and `FloorRefinement`'s proof that the code's decision is a `Decide` step of "
            "`FloorComposition`. Counted, the executed edge would grade the floor gates *executed*. **Whether that edge "
            "is a route is the custodian's choice.**",
        ], "amber", {"tint": False}),
        ("Six controls, each on an in-memory copy of the graph (§14, condition 2)", [
            "A pinned module with no read edge makes the pin file disagree; a `lean-sync.sh` series with no edge makes "
            "the sync scripts disagree; a stale TLAPS edge moves the two `Seats` theorems to the Lean route, and a stale "
            "graph check with it voids them; trusted edges on an undeclared row void all 19. **They move what they "
            "should.**",
        ], "teal", {"tint": False}),
        ("What the checker does not do", [
            "**It decides nothing** (§13). It was run once, 2026.11.07, by the drafter; no reader who is not the drafter "
            "has read the graph or the record (Open obligations; ADR-0029 A2).",
            "**It has not been rerun** since: `Paxos.tla`, `PaxosTrace.tla`, the overlay's eight modules and the "
            "`Workflow` and `Mesh` proofs entered `spec/` after `9749dfa` and are not nodes (G12 §9, item 111).",
        ], "red", {"tint": False, "dash": "6 4"}),
    ], size=13.5) + 80

    # ================================================================== band 7: degeneracy
    y = band(c, X0, y, "6 · One degeneracy on each record (ADR-0057 §12; ADR-0058 §10)", status="proposed")
    gcols = [("Id", 130, {"bold": True}), ("Kind", 150), ("Parameter → deployed value", 520), ("Premises falsified", 760),
             ("Theorems voided", 1100), ("Type changes (ADR-0023 §6b)", WW - 2660)]
    y += c.table(X0, y, gcols, [
        {"group": "ADR-0057 §12 · A corpus or deployment that keeps no graph has the inventory it has today, and cannot "
                  "say at what grade", "accent": "amber"},
        ["**D-0057-1**", "Declaration", "The graph: kept → not kept", "Every `edge(…)` premise",
         "None at grade *trusted*; every theorem's grade above *trusted* is unknown", "None"],
        {"group": "ADR-0058 §10 · A deployment that publishes no overlay has the inventory it has today and cannot say "
                  "at what grade; because every edge from its own nodes is absent, it cannot claim a kept archetype edge "
                  "either, if it replaced the node above it", "accent": "amber"},
        ["**D-0058-1**", "Declaration", "The overlay: published → not published",
         "Every `edge(…)` premise the deployment's own nodes would carry",
         "None at grade *trusted*; every grade above it unknown", "None"],
    ], size=13.5, accent="amber") + 80

    # ================================================================== band 8: ADR-0057 ratification, options, findings
    y = band(c, X0, y, "7 · ADR-0057's ratification condition item by item (§14, as R1 marks it), its options, "
                       "consequences, findings and open obligations", status="proposed", extra="R1 2026.11.07, not reviewed")
    y += row_cards(c, X0, y, WW, 30, [
        ("1 · The graph is built for the corpus at a named commit", [
            "Every clause the reference follows, every module and proof module, the Lean packages, the floor and its "
            "stages, and the reference's crates, with every edge typed and pinned.",
            f"**Met, but for the commit ⟨R1⟩**: `spec/specification-graph.json` built by `spec/specification-graph.py` "
            f"on the tree at `9749dfa`, R1's files not yet committed; {REC['n']} nodes, {REC['m']} edges. Built again "
            "with every pin taken afresh, the graph is the same file. **G12 §9 records it built and committed** (item "
            "111), so the commit now exists; the record's wording stands as R1 wrote it.",
        ], "amber", {"tint": False, "status": "proposed", "status_extra": "Met, but for the commit"}),
        ("2 · The checker runs, and its inventory at grade trusted equals inventory.py's", [
            "For the reference's declaration (Annex B), theorem by theorem; its stale-edge report names G11 items 56 "
            "and 103 without being told them.",
            f"**Met ⟨R1⟩**: the results file, byte for byte on a rerun; {R['annexb'][0]} of {R['annexb'][1]} holding in "
            f"each; {R['stale_n']} stale edges naming items 56 and 103; item 90 computed as well (band 5); six controls.",
        ], "green", {"tint": False, "status": "proposed", "status_extra": "Met"}),
        ("3 · ADR-0053's derived premises are re-expressed as edge premises, and premise-routes.sh prints the same verdicts", [
            "**Met for four of the five declarations ⟨R1⟩.** All eighteen derived premises re-expressed, and twenty-three "
            "`reaches-code(…)` added. Declarations 1, 2, 3 and 5 give the verdicts of `premise-routes-results-2026.11.03.txt`. "
            "**Declaration 4, with T-0045-28 excluded, differs on the two `Seats` theorems**, void by the graph and "
            "holding in the file, because the Lean route of `refines(Seats)` names edges that are stale (finding 7).",
            "**Met once `mechanism/lean` is brought into step (item 103), or if read as \"wherever the routes' edges "
            "are fresh\": the custodian's choice.** `premise-routes.sh` was not rerun (R1).",
        ], "amber", {"tint": False, "status": "open", "status_extra": "Met for 4 of 5; custodian's reading"}),
        ("4 · The dependent entries are drafted", [
            "An ADR-0033 addendum (clause pins, §7); an ADR-0045 §3 note (the binding read beside the graph, §8); an "
            "ADR-0053 note (§4).",
            "**Met ⟨R1⟩**: ADR-0033 A18, ADR-0045 A5, ADR-0053 A1, each pending and marked inline with a History row. "
            "ADR-0033 and ADR-0045 re-pinned; `drift.rs` passes. **Drafting them put §7 to work**: A18 moved the file "
            "pin and no clause pin; A5 moved §3's clause pin, so eight read edges went stale and were re-pinned.",
        ], "green", {"tint": False, "status": "proposed", "status_extra": "Met; all three pending"}),
    ], size=13.5) + 26
    wl = 1700
    xr = X0 + wl + 50
    wr = X1 - xr
    ocols = [("Option", 520, {"bold": True}), ("Disposition", wl - 520)]
    t = c.table(X0, y, ocols, [
        ["Place the project on Piskala's line", "Rejected. The corpus sits at five points at once (Context); the level is the edge's"],
        ["One record for the corpus and adopters together", "Not taken ⟨K4⟩. The method is the corpus's; what a deployment declares is an interface, and ADR-0058 holds it formalism-neutral"],
        ["A tree of specifications", "Rejected. One clause is read by several modules and one module reads several clauses"],
        ["A fixed set of layers", "Not taken ⟨K1⟩. A layer carries no premise, so adding one costs nothing the computation sees"],
        ["Holds or void, no grades", "Not taken ⟨K2⟩. It hides the difference between a theorem carried by a proof and one carried by a trust root, which is the difference T-0045-28 exists to name"],
        ["Grades as partial credit on a theorem", "Rejected. ADR-0023 §2. A grade is the threshold at which a binary inventory is taken (§5)"],
        ["A partial order of edge types", "Not taken now *(drafter's choice)*. A total order gives one grade per theorem; finding 4 names where it may fail, and ADR-0023 §5's per-axis precedent is the way out"],
        ["\"Gates\" as the clause's fourth part", "Not taken *(drafter's choice)*. The word is taken twice in the corpus (§2)"],
        ["Pinned as an edge type", "Rejected. A pin detects change at the far end; it says nothing of the relation. Freshness is an attribute of every edge"],
        ["Generate the four lists at once", "Not taken *(drafter's choice)*. Check against the graph first (§8)"],
        ["A brand name for the graph", "Not taken ⟨K3⟩"],
    ], size=13.5, accent="grey")
    yl = y + t + 20
    yl = stack(c, X0, yl, wl, [
        ("Consequences", [
            "**Positive.** The corpus can say how strongly each theorem reaches the code, not only whether its premises "
            "are declared. Staleness is computed: what G11 lists by hand at items 56, 90 and 103 the checker reports. "
            "History rows stop tripping the drift test, and a changed clause still does. Twice-stated guarantees are "
            "listed with the type of the edge that ties them. Adopters get an interface (ADR-0058) built on what the "
            "corpus already does.",
            "**Negative.** One more artifact to keep in step, with its own checker, beside four it does not yet replace. "
            "The total order may be wrong in places (finding 4), and every grade inherits the error. **Grades will look "
            "worse than the prose**: most mechanism theorems grade *trusted* today, which is true and has been stated "
            "only in T-0045-28's note. One author, one day, as every record since G2.",
        ], "grey", {"tint": False}),
        ("Open obligations", [
            "**The graph, the checker, and the dependent entries** (§14): built, run and drafted ⟨R1⟩. Two things remain: "
            "the commit that carries them, and the custodian's reading of findings 7 and 8.",
            "**The custodian's reading of every drafter's choice**, above all the order of §3 and the downward grading of §5.",
            "**Who reads the edges up.** Finding 5 is the bootstrap reviewer's question in another form (ADR-0029 A2).",
            "**The archetype-evolution record** (unwritten) owns the graph's versioning, as it owns the binding table's.",
            "**Narrative.** The ToO and the glossary owe *specification graph*, *edge type*, *grade*, *givens*, "
            "*discharge* and *stale edge* at the next cut.",
        ], "red", {"tint": False, "status": "open"}),
    ], gap=16, size=13.5)
    F = [
        "**1. The paper's levels are properties of edges.** Spec-as-source is the floor's edge; anchored by proof the "
        "admit decision's; by replay `apply`'s; by tests the operator path's; spec-first the workflow path's, for now.",
        "**2. The rule that a stale edge is false is already in the corpus**, for ADR-0053 R7's `check` premises. This "
        "record extends a rule; it does not make one.",
        "**3. Graded inheritance and ADR-0023 §2.** §5 keeps \"no weaker version\" by taking a binary inventory per "
        "threshold. A C3 reviewer may still read a grade as partial credit; the record that settles it is ADR-0023's.",
        "**4. The order of §3 is not obviously total.** *Executed* and *generated* each leave one tool; *proved of a "
        "reading* and *replayed* leave different things. If a pair is incomparable, the grade becomes per axis.",
        "**5. Every module is a reading of a record, by the drafter.** The corpus's strongest results sit on its weakest "
        "edge type at the top, as the code sits on T-0045-28 at the bottom. The checkpoints have said so since G2.",
        "**6. The strongest edge points at a node not in force.** The reference executes the `workflow` stage, which is "
        "Proposed (G11 item 102). A grade measures the edge, not the standing of its ends; the graph shows both.",
        "**7. §14's third condition cannot be met as worded on today's tree, and §4 says why ⟨R1⟩.** The Lean route of "
        "`refines(Seats)` names stale edges (item 103); with T-0045-28 excluded the two `Seats` theorems are void by the "
        "graph. Which of two readings meets it is the custodian's choice.",
        "**8. Two edges reach the code and are not counted as routes ⟨R1⟩**: the executed edge and `FloorRefinement`'s "
        "proof, both `\"route\": false`. `FloorRefinement` is one step, not the module's behaviours (ADR-0053 §5 R2). "
        "Whether the executed edge is a route is the custodian's choice.",
        "**9. The drafter's choices in building ⟨R1⟩.** (a) Pins: a read edge from the code or a trusted edge pins its "
        "upper end only, as `corpus-pins.sha256` does; pinning both would stale 139 read edges on every commit. (b) "
        "Clauses: a record without a Decision is one clause, `text`; unnumbered subsections, annexes and ADR-0033's "
        "`## 7.` are clauses; a pending subsection is left out, pending text inline stays in. (c) `Admit-results` edges "
        "pin every file `mechanism/lean` transcribes. (d) The graph check is *proved*; a Lean proof of an encoding is "
        "*proved of a reading*. (e) Theorems no module states are stated at `STATED_AT`'s nodes.",
        f"**10. Every module's edges up are *read*, by the drafter ⟨R1⟩**: all {R['up']} modules. Finding 5, computed.",
        f"**11. {R['unread'][0]} clauses of {R['unread'][1]} records the reference follows have no edge but the code's "
        "reading ⟨R1⟩.** Some are by nature outside any model (§10); the list is where to look for the rest.",
    ]
    yr = c.card(xr, y, wr, "Findings 1–11", F, accent="amber", size=13.5, tint=False) + y
    y = max(yl, yr) + 80

    # ================================================================== band 9: ADR-0058
    y = band(c, X0, y, "8 · ADR-0058: a deployment declares its specification graph against the archetype's "
                       "(Proposed; rests on ADR-0057: ratified together, or it waits)", status="proposed",
             extra="C2 · 2026.11.06")
    y += c.para(X0, y, WW, "**Adopting TOPAK is already a declaration** (the Adopter's Guide §1): parameters moved "
                "(ADR-0023 §6), the rung per seat, the trusted-base rows instantiated (ADR-0045 §4). **It says nothing "
                "about artifacts**: an adopter who writes their own mechanism has no place to state what ties it to the "
                "modules; a supplier has no form in which to publish what its artifact discharges. ADR-0049 §4 already "
                "grades one schema in two grades, *checked* or *claimed*; ADR-0057 gives the corpus eight, and this record "
                "gives deployments and suppliers the same ⟨K4⟩ (Context).", 14.5, "muted") + 20
    wl = 1500
    xr = X0 + wl + 50
    wr = X1 - xr
    opcols = [("Operation", 150, {"bold": True}), ("What the deployment does", 560), ("What it declares", wl - 710)]
    t = c.table(X0, y, opcols, [
        ["**Keep**", "Uses the node as published", "The node's digest; the archetype's edges below it stand, as typed"],
        ["**Replace**", "Substitutes its own artifact",
         "The artifact's digest, and each edge the archetype node had, re-established and typed (§2)"],
        ["**Add**", "Brings a node the archetype has no counterpart for: a tool's schema, a deployment's own policy, a "
                    "runtime monitor", "The node and its edges, typed"],
        ["**Omit**", "Does not use the node", "Nothing; its edges are absent and their premises false"],
    ], size=13.5, accent="amber")
    yl = y + t + 20
    yl = stack(c, X0, yl, wl, [
        ("The archetype publishes its graph; a deployment's graph is an overlay on it (§1)", [
            "The archetype's graph (ADR-0057 §8) is published with each archetype version, by digest. **For each "
            "archetype node, one of four operations, and for each edge, a type.** The reference is the first overlay "
            "(§9): it keeps every record and module, and adds its crates.",
        ], "amber", {"tint": False}),
        ("A replaced node re-establishes its edges, each typed (§2)", [
            "**Every edge the archetype node had is re-established at a declared type, or declared absent.** An edge "
            "not mentioned is absent, and its premise is false (ADR-0045 §3 rule 1, as ADR-0057 §4 reads it).",
            "**Re-establish at the strongest type you can.** A replacement that reruns the archetype's checks against "
            "itself (the floor's gate suite, the trace replay, the graph check) takes the type of that check. One that "
            "does not takes *read*, with its reader named, or is absent.",
        ], "amber", {"tint": False}),
        ("The method is the deployment's; the type follows from what it leaves (§3 ⟨K1⟩)", [
            "P, Quint, Alloy, Dafny, Verus, Kani, Coq, Isabelle, or the corpus's own TLA+, TLAPS and Lean. **A Verus "
            "proof that a Rust mechanism refines a module is *proved*, and its prover is a row.**",
            "**A prover or checker the archetype has no row for is declared as a degeneracy** under ADR-0023 §4a, a "
            "D-row beside the nearest archetype row (T-0045-29, T-0045-31 or T-0045-37), and **reported upstream** (§6): "
            "Annex A has no generic row for a prover a deployment chose (finding 2).",
        ], "amber", {"tint": False}),
        ("Inheritance is graded, and the declaration publishes every grade (§4 ⟨K2⟩)", [
            "The deployment's inventory is computed from its overlay, at every grade, as ADR-0057 §5 computes the "
            "corpus's. **A claim made outside the declaration names its grade**: \"`NoActionUnderFencedEpoch` holds at "
            "*replayed*\", not \"holds\". **A claim with no grade is read at *trusted*.**",
            "**Show each node's standing beside each grade**: a deployment that executes a Proposed floor stage has a "
            "strong edge to a node not in force (ADR-0057 finding 6), and its declaration says both.",
            "**The composition note carries grades** (ADR-0023 §7a): theorems whose grade falls by the joint effect of "
            "several overlay operations, computed from the overlay; an empty delta is still a claim.",
        ], "amber", {"tint": False}),
    ], gap=16, size=13.5)
    yr = stack(c, xr, y, wr, [
        ("A deployment may grade above the archetype; the admission test is unchanged (§5)", [
            "A mechanism proved to refine the modules where the reference has T-0045-28 **has the archetype's inventory "
            "at a higher grade**. Not a capability the archetype lacks in ADR-0023 §4's sense (the inventory is not "
            "larger; the archetype stays the unique maximum). **It is a route the archetype lacks, and it is reported "
            "upstream** (§6), so the archetype can add it as an alternative in the derived premise.",
        ], "amber", {"tint": False}),
        ("Report upstream what the archetype lacks (§6)", [
            "A route stronger than the archetype's (§5); a method with no row (§3); a node every deployment of its kind "
            "will need, a schema above all (ADR-0057 §9); an edge it could not re-establish because the archetype node "
            "was underspecified. **Each report is a finding about the archetype**, as ADR-0023 §4's rejections are.",
        ], "amber", {"tint": False}),
        ("Suppliers publish subgraphs, and a deployment imports them (§7)", [
            "A supplier of a tool, a Persona, a policy library, a transport or a mechanism publishes **its nodes by "
            "digest, the archetype nodes it claims to discharge, the edges with their types, and the evidence by "
            "digest**. An imported edge keeps its type if the deployment reruns its check, and enters as *read*, with "
            "the supplier as its reader, if it does not. ADR-0049 §4 is the case already in force.",
            "**Rerun what you can.** A supplier's proof that a deployment re-checks is the deployment's proof; one it "
            "does not is the supplier's word. The form of a supplier's subgraph is owed (Open obligations).",
        ], "amber", {"tint": False}),
        ("The declaration gains its graph, and the gate reads it (§8)", [
            "ADR-0023 §6's declaration gains one field, **graph**: the overlay by digest and the graded inventory "
            "computed from it *(dependent entry: an ADR-0023 amendment, not drafted)*. The Build promotion gate that "
            "reads §6's schema (§7b) reads the overlay on the same check: an overlay that does not parse against the "
            "archetype version it names, or an inventory not the one computed from it, **fails as a missing composition "
            "note fails**.",
        ], "amber", {"tint": False, "status": "notbuilt", "status_extra": "ADR-0023 amendment not drafted"}),
    ], gap=16, size=13.5)
    y = max(yl, yr) + 30
    gcols2 = [("#", 90, {"bold": True}), ("Item (§9.2)", 420, {"bold": True}), ("Done when", WW - 510)]
    c.text(X0, y + 16, "The Adopter's Guide gains five checklist items (§8; its §2 and §9.2 entries are not drafted)",
           15, "ink", bold=True)
    y += 30
    y += c.table(X0, y, gcols2, [
        ["D-g1", "The overlay", "Every archetype node is kept, replaced or omitted, and every added node is listed"],
        ["D-g2", "Each replaced node's edges", "Re-established with a type, or declared absent"],
        ["D-g3", "The inventory at every grade",
         "Computed from the overlay, each theorem with its grade, route and the standing of its nodes"],
        ["D-g4", "Imported subgraphs", "Each with its supplier, and each edge marked rerun or read"],
        ["D-g5", "Upstream reports", "Filed for every case §6 names, or stated as none"],
    ], size=13.5, accent="amber") + 40

    # §9 the reference's overlay, read; beside it what the checker's graph says
    c.text(X0, y + 16, "The reference is the first overlay (§9), \"read and not computed\" on 2026.11.06, when the "
           "checker did not yet exist; the last column is the diagram's: what the graph and results of 2026.11.07 say "
           "of the same edge", 15, "ink", bold=True)
    y += 30

    def inj(ty, frm, to):
        return (ty, frm, to) in G["index"]

    def fr(ty, frm, to):
        return fresh_word(R, (ty, frm, to))

    rcols = [("From → to (§9)", 760), ("Type (§9)", 230), ("Fresh (§9, as read 2026.11.06)", 520),
             ("In the graph and results of 2026.11.07 (the diagram's column)", WW - 1510)]
    rrows = [
        ["`topak-floor`'s linked stage → `floor/proposed/workflow-floor.cedar`", "executed",
         "yes; the stage is Proposed (G11 item 102)",
         f"`executed: mechanism/crates/topak-floor → floor/proposed/workflow-floor.cedar`, {fr('executed', 'mechanism/crates/topak-floor', 'floor/proposed/workflow-floor.cedar')}; "
         "`route: false` (ADR-0057 finding 8). The stage is Proposed at G12 (ADR-0054 Proposed)."],
        ["`floor/proposed/` stages → `floor/genesis-floor.cedar`", "generated", "yes",
         f"{G['by_type']['generated']} generated edges, one per stage, all fresh."],
        ["`admit.rs` with the floor wrapper → `FloorComposition.tla` `Decide`", "proved of a reading",
         "as of `mechanism/lean`",
         f"`proved of a reading: mechanism/crates/topak-core → spec/FloorComposition.tla`, {fr('proved of a reading', 'mechanism/crates/topak-core', 'spec/FloorComposition.tla')} "
         "(`Admit-results`; `rules.rs`, `state.rs`, `types.rs`, `topak-floor`'s `lib.rs` moved: G11 item 103); "
         "`route: false`. [[red|§9 does not say stale; the results file does.]]"],
        ["`State::apply`, seat and lease arms → `Seats.tla`", "proved of a reading, and replayed",
         "**stale**: `mechanism/lean` (G11 item 103)",
         f"`proved of a reading: topak-core → spec/Seats.tla`, {fr('proved of a reading', 'mechanism/crates/topak-core', 'spec/Seats.tla')}; "
         f"`replayed: topak-core → mechanism/lean/Topak/SeatsModel.lean`, {fr('replayed', 'mechanism/crates/topak-core', 'mechanism/lean/Topak/SeatsModel.lean')} "
         "(`model-faithful(apply/Seats)`). The same."],
        ["`State::apply` → `Mechanism.tla`", "replayed", "**stale** for workflows (G11 item 56)",
         f"`replayed: topak-core → spec/Mechanism.tla`, {fr('replayed', 'mechanism/crates/topak-core', 'spec/Mechanism.tla')}, "
         f"and → `spec/ConfinementRefinement.tla`, {fr('replayed', 'mechanism/crates/topak-core', 'spec/ConfinementRefinement.tla')}: "
         "`topak-core` changed in 17 files since `9c57221`, `workflow.rs` among them; `topak-node` in 4. The same."],
        ["Operator path → `Operators.tla`", "tested", "yes",
         f"`tested: topak-core → spec/Operators.tla`, {fr('tested', 'mechanism/crates/topak-core', 'spec/Operators.tla')} "
         f"(`tests/operators.rs`); {G['by_type']['tested']} tested edges in all."],
        ["Every other mechanism theorem's route to the code", "trusted (T-0045-28)", "—",
         f"{G['by_type']['trusted']} trusted edges, `mechanism → <module>`, each `reaches-code(…)`."],
    ]
    y += c.table(X0, y, rcols, rrows, size=13.5, accent="amber") + 22
    y += row_cards(c, X0, y, WW, 30, [
        ("Read at grades (§9)", [
            "Every floor theorem the stage carries is inherited at *executed*; the two `Seats` theorems at *proved of a "
            "reading* until `mechanism/lean` is brought into step, and at *replayed* or *trusted* while it is not; the "
            "operator theorems at *tested*; every other mechanism theorem at *trusted*. **At *trusted* the inventory is "
            "Annex B's.**",
            "[[red|The checker of 2026.11.07 grades every theorem of Annex B trusted]], the floor gates included, because "
            "the executed edge is `route: false` (ADR-0057 finding 8) and the `Seats` route is stale. §9's reading and "
            "the checker's computation differ where §9 says *executed* and *proved of a reading*; neither is revised.",
        ], "amber", {"tint": False}),
        ("Two hypothetical adopters (§9; the record's examples)", [
            "**One replaces the Kafka transport with another log**: the transport carries no ordering authority "
            "(ADR-0005), its edges are *tested* against the reference's e2e suite rerun, and no theorem's grade moves.",
            "**One writes the mechanism in another language and proves it refines `Seats`, `Lease_A1` and "
            "`FloorComposition` with Verus**: those theorems rise to *proved*, its prover is a D-row beside T-0045-31 "
            "(§3), and both the route and the missing row are reported upstream (§5, §6).",
        ], "grey", {"tint": False}),
        ("The trusted base (§11)", [
            "**No row is added by this record.** A method a deployment brings enters by §3, as a D-row. A supplier's "
            "word enters as *read*, which is a premise and not a row.",
        ], "grey", {"tint": False}),
    ], size=13.5) + 26

    # ADR-0058 ratification condition: the record marks no item; drawn as the files show
    y += row_cards(c, X0, y, WW, 30, [
        ("§12 · 1 · ADR-0057 is ratified, or is ratified in the same batch", [
            "**Not met.** ADR-0057 is Proposed (R1 2026.11.07); Batch 40 ratified ADR-0033 A19 and A20 only. The "
            "record marks none of its four items.",
        ], "red", {"tint": False, "status": "open", "status_extra": "Not met"}),
        ("§12 · 2 · The reference's overlay is computed by ADR-0057's checker at a named commit, and its inventory at trusted equals Annex B's", [
            "**Not met as an overlay.** ADR-0057's checker computed the corpus graph at `9749dfa` and its inventory at "
            f"*trusted* is Annex B's ({R['annexb'][0]} of {R['annexb'][1]}, theorem by theorem). No overlay in §1's "
            "form (keep, replace, add, omit per node) is computed; §9 is read, not computed. The diagram's reading: the "
            "record marks nothing.",
        ], "red", {"tint": False, "status": "open", "status_extra": "Not met; the inventory part exists"}),
        ("§12 · 3 · One replacement overlay is computed, a stand-in replacing one node, with the grade changes and voids §2 predicts", [
            "**Not met.** No replacement overlay exists in `spec/`; the checker has no overlay input.",
        ], "red", {"tint": False, "status": "open", "status_extra": "Not met"}),
        ("§12 · 4 · The dependent entries are drafted: the ADR-0023 amendment (§8) and the Adopter's Guide's §2 and §9.2 entries", [
            "**Not met.** ADR-0023 carries no pending amendment for a `graph` field, and the Guide's §2 and §9.2 carry "
            "no D-g items (Open obligations).",
        ], "red", {"tint": False, "status": "open", "status_extra": "Not drafted"}),
    ], size=13.5) + 26

    wl = 1700
    xr = X0 + wl + 50
    wr = X1 - xr
    t = c.table(X0, y, [("Option", 520, {"bold": True}), ("Disposition", wl - 520)], [
        ["Fold this into ADR-0057", "Not taken ⟨K4⟩. The method is the archetype's and is not a deployment's to weaken; the overlay is what deployments and suppliers use, and it is formalism-neutral"],
        ["Prescribe the corpus's methods to adopters", "Rejected. An edge is typed by what it leaves, not by its tool (§3)"],
        ["Let a deployment declare grades without an overlay", "Rejected. A grade is computed from edges; asserted, it is the \"declared by the operator and verified by nobody\" ADR-0036 R1 names"],
        ["Read a supplier's claims at their claimed type", "Rejected. A claim not rerun is *read*, by the supplier (§7)"],
        ["Treat a stronger route as a capability under ADR-0023 §4", "Rejected. It would make the archetype incomplete for want of evidence, not of a capability (§5)"],
        ["A generic prover row in Annex A now", "Not taken *(drafter's choice)*. Adding a row is a relaxation that needs its own record (ADR-0045 §4); the reports of §6 are its evidence"],
        ["Ungraded inheritance for adopters, graded for the corpus", "Rejected ⟨K2⟩. The same computation, or the two inventories cannot be compared"],
    ], size=13.5, accent="grey")
    yl = y + t + 20
    yl = stack(c, X0, yl, wl, [
        ("Consequences", [
            "**Positive.** An adopter can say what ties their artifacts to the theorems, and at what strength, in a form "
            "the gate reads. Suppliers can publish what they discharge, and deployments can see what they rerun and what "
            "they take on word. The ecosystem feeds the archetype: stronger routes, missing rows and missing schemas "
            "arrive as findings. **A claim carries its grade**, so \"TOPAK-conformant\" stops meaning one thing for a "
            "proof and another for a trust root.",
            "**Negative.** A declaration is larger, and a deployment needs ADR-0057's checker to produce it. **Graded "
            "claims invite grade-shopping**: §4 asks the whole inventory to be published, and nothing stops a quotation "
            "from leaving it out. Everything rests on ADR-0057's order of types (its finding 4).",
        ], "grey", {"tint": False}),
    ], size=13.5)
    yr = stack(c, xr, y, wr, [
        ("Findings 1–5", [
            "**1. ADR-0049 already grades declarations**, for one schema and in two grades. This record is that "
            "distinction, generalized.",
            "**2. Annex A has no row for a prover a deployment chose.** Every method beyond TLC, TLAPS and Lean enters as "
            "a degeneracy, which reads as a weakening even where it strengthens.",
            "**3. A deployment can exceed the archetype's grade and not its inventory.** Grades are a second order on "
            "deployments, and the archetype is not its maximum.",
            "**4. The reference's strongest edge ends at a Proposed node** (§9). Grade and standing are separate, and a "
            "declaration that shows one without the other misleads.",
            "**5. A supplier's evidence is one hand's**, as the corpus's is (G11 §4). The reader on a *read* edge is how "
            "a deployment sees it.",
        ], "amber", {"tint": False}),
        ("Open obligations", [
            "**ADR-0057, and its checker**, on which every computation here rests.",
            "**The ADR-0023 amendment and the Guide's entries** (§8).",
            "**The form of a supplier's subgraph**, as a schema node (ADR-0057 §9).",
            "**The custodian's reading of every drafter's choice.**",
            "**Narrative.** The glossary owes *overlay*, *keep*, *replace*, *add*, *omit*, *subgraph* and *supplier* at "
            "the next cut.",
        ], "red", {"tint": False, "status": "open"}),
    ], gap=16, size=13.5)
    y = max(yl, yr) + 40

    c.legend(X0, y, [
        ("box", "amber", "Proposed (ADR-0057, ADR-0058); nothing in force", "6 4"),
        ("box", "teal", "the graph file, the checker's run, the modules"),
        ("box", "blue", "records and clauses; the diagram's checks against the record"),
        ("box", "red", "stale, not met, not run, not drafted, not computed", "6 4"),
        ("box", "green", "agrees, fresh, met"),
        ("arrow", "teal", "proved, proved of a reading"),
        ("arrow", "green", "replayed, tested"),
        ("arrow", "brown", "read, by a named reader"),
        ("arrow", "grey", "trusted: a row where the edge would be"),
        ("arrow", "blue", "executed, generated"),
        ("arrow", "red", "a stale edge (premise false)"),
    ])
    return c
