"""The page every diagram of one TLA+ module is built from (family I): layout helpers and the bands whose content
is the module's evidence, read by modules.py. A module's own diagram (d_i<n>_<slug>.py) supplies the cards and
prose that need writing by hand, and calls these for the rest.

Not a diagram itself: the generator imports only d_*.py.
"""
import json
import pathlib
import re

import lib
import modules as M
from lib import STATUS, linked, poster_link, text_width

HERE = pathlib.Path(__file__).resolve().parents[1]

S = 14

# The state every module diagram is drawn against, until one is amended against a later one.
STATE = ("State of record: Genesis Checkpoint G12 (2026.11.16), with Batch 40 (2026.11.17) · narrative: Theory of "
         "Operation rev 16 · drawn 2026.11.26, every file read at the pin its links open")


# ---------------------------------------------------------------------------------------------- layout
def row_cards(c, x, y, w, gap, specs, size=S):
    """A row of cards of equal height, measured over every card in the row. specs: (title, body, accent, kwargs).
    Returns the height."""
    n = len(specs)
    cw = (w - (n - 1) * gap) / n
    h = max(c.card(0, 0, cw, t, b, draw=False, size=size, status=k.get("status"), sub=k.get("sub"),
                   bullets=k.get("bullets", True)) for t, b, _, k in specs)
    for i, (t, b, acc, k) in enumerate(specs):
        c.card(x + i * (cw + gap), y, cw, t, b, accent=acc, h=h, size=size, **k)
    return h


def band(c, x, y, title, accent="ink", status=None, extra=""):
    """A section heading with an optional status pill. Returns the y where content starts."""
    c.text(x, y + 22, title, 22, accent, bold=True)
    if status:
        c.status(x + text_width(lib.unlinked(title), 22, True) + 20, y + 4, status, extra)
    return y + 54


def status_strip(c, x0, x1, y, items):
    """items: (label, key, extra); key a STATUS key or (label, accent, dash). Wraps at x1. Returns the y below."""
    c.text(x0, y + 15, "Status", 15, "faint", bold=True)
    px0 = x0 + 80
    px = px0
    for lab, key, extra in items:
        lw = text_width(lib.unlinked(lab), 13.5, True) + 8
        if isinstance(key, tuple):
            plab, acc, dash = key
            pw = text_width(plab, 11.5, True) + 18
        else:
            pw = text_width(STATUS[key][0] + (f" · {extra}" if extra else ""), 11.5, True) + 18
        if px + lw + pw > x1:
            px = px0
            y += 34
        c.text(px, y + 15, lab, 13.5, "ink", bold=True)
        px += lw
        if isinstance(key, tuple):
            px += c.pill(px, y, plab, acc, 11.5, dash=dash) + 26
        else:
            px += c.status(px, y, key, extra) + 26
    return y + 42


def strike(cell):
    """A Markdown cell's struck text (~~x~~), drawn as "struck: x" (the library has no strike-through)."""
    return re.sub(r"~~(.+?)~~", r"struck: \1", cell)


def n(x):
    return f"{x:,}"


def code(s):
    """One line of TLA+ as a code run, indentation dropped."""
    s = s.strip()
    return f"`{s}`" if s else ""


def code_lines(src):
    """A definition's lines as code runs, one per line."""
    return [code(ln) for ln in src.split("\n") if ln.strip()]


def verdict(row, expect=None):
    """A TLC row as a cell: the verdict, the states, and whether it is what the diagram expects."""
    v = row["verdict"]
    word = f"[[red|{v}]]" if v == "COUNTEREXAMPLE" else f"**{v}**"
    return f"{word} · {n(row['states'])} states · row `{row['name']}`"


# ---------------------------------------------------------------------------------------------- markdown tables
def _cells(line):
    """A Markdown table row's cells, splitting on | outside code runs."""
    out, cur, inside = [], "", False
    for ch in line.strip().strip("|"):
        if ch == "`":
            inside = not inside
        if ch == "|" and not inside:
            out.append(cur.strip())
            cur = ""
        else:
            cur += ch
    out.append(cur.strip())
    return out


def md_table(rel, header, occurrence=None):
    """The Markdown table under the header row `header` (its cells, as a list) in `rel` at the pin: list of rows,
    each a list of cells. occurrence: which of several tables with that header (0-based), when there are several;
    otherwise there must be one."""
    lines = M.text(rel).split("\n")
    hits = [i for i, ln in enumerate(lines) if ln.startswith("|") and _cells(ln) == header]
    if occurrence is not None:
        if len(hits) <= occurrence:
            raise M.CorpusError(f"{rel}: no table {occurrence} headed {header[:2]}…")
        hits = [hits[occurrence]]
    if len(hits) != 1:
        raise M.CorpusError(f"{rel}: the table headed {header[:2]}… is there {len(hits)} times, not once")
    rows = []
    for ln in lines[hits[0] + 2:]:
        if not ln.startswith("|"):
            break
        cells = _cells(ln)
        if len(cells) != len(header):
            raise M.CorpusError(f"{rel}: a row of {len(cells)} cells under a header of {len(header)}: {ln[:60]!r}")
        rows.append(cells)
    return rows


def md_rows(rel, header, keys):
    """The rows of md_table(rel, header) whose first cell names one of `keys` in code, in the order of keys; each
    key must be in one row, and a row naming two keys is drawn once."""
    rows = md_table(rel, header)
    out = []
    for k in keys:
        hit = [r for r in rows if k in re.findall(r"`([^`]+)`", r[0])]
        if len(hit) != 1:
            raise M.CorpusError(f"{rel}: a row for {k} {len(hit)} times, not once")
        if hit[0] not in out:
            out.append(hit[0])
    return out


# ---------------------------------------------------------------------------------------------- the bands
WORDS = ("**Checked**, **proved** and **certified** mean what ADR-0046 §1 says: TLC checks the mutations and "
         "witnesses at the module's constants; TLAPS proves each invariant under the hypothesis its statement names; "
         "the certified run accounts for every obligation by a route an independent checker accepted, or names LS4. "
         "Nothing here is said of the running reference.")


def status_items(ev, record_items, tail=()):
    """The status strip: the records, then the module's evidence as the files state it."""
    name = ev["name"]
    items = list(record_items)
    if ev["tlc"] is not None:
        items.append((f"`{name}.tla`", (f"Checked by TLC · {len(ev['tlc']['rows'])} rows", "teal", None), ""))
    else:
        items.append((f"`{name}.tla`", ("No TLC run of its own", "grey", "2 3"), ""))
    if "proof" in ev:
        pr, ce = ev["proof"], ev["cert"]
        items.append((f"`{name}_proof.tla`", (f"Proved · {n(pr['obligations'])} obligations", "blue", None), ""))
        items.append(("The certified run", (f"Certified · {ce['ls4']} obligations on LS4" if ce["certified"]
                                            else "NOT CERTIFIED", "blue" if ce["certified"] else "red",
                                            None if ce["certified"] else "6 4"), ""))
    else:
        items.append(("TLAPS", ("No proof module", "grey", "2 3"), ""))
    if "lean" in ev:
        items.append((f"`{ev['lean_unit']}.lean`", ("Proved in Lean, of the re-encoding", "blue", None), ""))
    if "graph" in ev:
        items.append(("The graph check", ("Checked against TLC's graphs · a test", "teal", "6 4"), ""))
    return items + list(tail)


def machine(c, x, y, w, rel, rows, size=13.5, gap=30):
    """Rows of definition cards. rows: [[(title or None, [names], [prose], accent)]]; each card draws its names'
    definitions as written, then its prose. A None title is "`<first name>` · line <n>"."""
    for row in rows:
        specs = []
        for title, names, prose, acc in row:
            body = []
            first = None
            for nm in names:
                ln, src = M.definition(rel, nm)
                first = first or ln
                body += code_lines(src)
            t = title or f"`{names[0]}` · line {first}"
            specs.append((t, body + list(prose), acc, {"bullets": False}))
        y += row_cards(c, x, y, w, gap, specs, size=size) + gap
    return y - gap


def theorem_for(ev, prop):
    """The THEOREM whose statement is Spec => []prop, or None."""
    hits = [s for s in ev.get("statements", ()) if s["kind"] == "THEOREM" and s["prove"] == f"Spec => []{prop}"]
    return hits[0] if len(hits) == 1 else None


def properties(c, x, y, w, ev, props, key=None, record="ADR", safe=True, note=None):
    """Returns the y below. One row per property: the section it states, the header's words, its definition, the variants that break
    it per TLC, and the theorem that proves it. props: [(name, section text or None, words)]. note: {name: an
    extra line for its section cell}."""
    rel = ev["files"]["module"]
    res = ev["tlc"]
    cells = M.matrix(res, key)[2] if key else M.matrix(res)[2]
    rows = []
    names = [p for p, _, _ in props] + (["Safe"] if safe else [])
    for p in names:
        sec, words = next(((s_, w_) for p_, s_, w_ in props if p_ == p), ("their conjunction", None))
        ln, src = M.definition(rel, p)
        breaks = sorted({k for (k, pp), r in cells.items() if pp == p and r["verdict"] == "COUNTEREXAMPLE"},
                        key=lambda k: list(dict.fromkeys(k_ for k_, _ in cells)).index(k))
        t = theorem_for(ev, p)
        proved = (f"`{t['name']}`, under `{t['assume']}`" if t and t["assume"] else f"`{t['name']}`" if t else
                  "[[red|no theorem states it]]")
        sec_cell = (sec if sec else "[[red|the header names no section]]") + (f"\n{note[p]}" if note and p in note
                                                                              else "")
        rows.append([f"`{p}`", sec_cell, f"\"{words}\"" if words else "—", " ".join(code_lines(src)),
                     ", ".join(f"`{b}`" for b in breaks) if breaks else "—", proved])
    return y + c.table(x, y, [("Property", 290, {}), ("States (the module's header)", 230), ("The header's words", 520),
                          ("Its definition", 1060), ("Broken, per TLC, by", 330),
                          (f"Proved as (`{pathlib.PurePosixPath(ev['files']['proof'] or '').name}`)", w - 2430)],
                   rows, size=13.5, accent="teal", anchor="properties")


def mutations(c, x, y, w, ev, head_muts, var="Mut", key=None):
    """Returns the y below. One row per mutation the header lists: what it does, every code line it acts on, what it breaks and leaves
    holding per TLC, and the proof module's lemmas about it."""
    rel = ev["files"]["module"]
    cells = M.matrix(ev["tlc"], key)[2] if key else M.matrix(ev["tlc"])[2]
    lines = M.text(rel).split("\n")
    rows = []
    for mt, words in head_muts:
        if mt == "none":
            continue
        at = M.code_lines_with(rel, f'{var} = "{mt}"')
        if not at:
            raise M.CorpusError(f"{rel}: {mt} acts on no line of code")
        where = "; ".join(f"`{M.enclosing(rel, ln)}`, line {ln}: {code(lines[ln - 1])}" for ln in at)
        run = {pp: r for (k, pp), r in cells.items() if k == mt}
        br = [pp for pp, r in run.items() if r["verdict"] == "COUNTEREXAMPLE"]
        ho = [pp for pp, r in run.items() if r["verdict"] == "HOLDS"]
        lem = [s for s in ev.get("statements", ()) if s["kind"] == "LEMMA" and f'{var} = "{mt}"' in (s["assume"] or "")]
        rows.append([f"`{mt}`", words, where, ", ".join(f"`{p}`" for p in br) or "—",
                     ", ".join(f"`{p}`" for p in ho) or "—",
                     "; ".join(f"`{s['name']}` (line {s['line']}): `{s['prove']}`" for s in lem) or "—"])
    return y + c.table(x, y, [("Mutation", 200, {}), ("What it does (the module's header)", 620), ("Where it acts", 760),
                          ("Breaks, per TLC", 300), ("Leaves holding, per TLC", 300),
                          ("Why it must fail (the proof module's lemma; the counterexample is TLC's)", w - 2180)],
                   rows, size=13.5, accent="red", anchor="mutations")


def matrix_table(c, x, y, w, ev, props, expect, labels, key=None, head="Mutation"):
    """The variant x property matrix (#matrix), every cell from the results file, each compared with `expect`
    {(variant, prop): verdict}, the diagram's literal, in both directions. A cell not run is drawn so. labels:
    {variant: what it is}."""
    res = ev["tlc"]
    variants, got_props, cells = M.matrix(res, key) if key else M.matrix(res)
    if got_props != props:
        raise M.CorpusError(f"{res['file']}: properties {got_props}, the diagram expects {props}")
    if set(cells) != set(expect):
        raise M.CorpusError(f"{res['file']}: cells {sorted(cells)} are not the {len(expect)} the diagram expects")
    rows = []
    for v in variants:
        r = [f"`{v}`", labels[v]]
        for p in props:
            row = cells.get((v, p))
            if row is None:
                r.append("[[grey|not run]]")
                continue
            if row["verdict"] != expect[(v, p)]:
                raise M.CorpusError(f"{res['file']}: {v} x {p} is {row['verdict']}, the diagram expects "
                                    f"{expect[(v, p)]}")
            r.append(verdict(row))
        base = all(cells.get((v, p), {}).get("verdict", "HOLDS") == "HOLDS" for p in props)
        rows.append({"cells": r, "accent": "grey" if base else "red"})
    lw = 520 if len(props) > 3 else 640
    pw = (w - 230 - lw) / len(props)
    cols = [(head, 230, {}), ("What it is", lw)] + [(f"`{p}`", pw) for p in props]
    return c.table(x, y, cols, rows, size=13 if len(props) > 4 else 13.5, anchor="matrix")


def witnesses_table(c, x, y, w, ev, readings, unmutated=("none",)):
    """The Never... rows (#witnesses): each property's definition, and the row that violates it. readings:
    {prop: the diagram's own reading of what it shows reachable}."""
    rel = ev["files"]["module"]
    ws = M.witnesses(ev["tlc"], unmutated)
    if [r["prop"] for r in ws] != list(readings):
        raise M.CorpusError(f"{ev['tlc']['file']}: witnesses {[r['prop'] for r in ws]}, the diagram reads "
                            f"{list(readings)}")
    rows = []
    for r in ws:
        if r["verdict"] != "COUNTEREXAMPLE":
            raise M.CorpusError(f"{ev['tlc']['file']}: witness {r['prop']} is {r['verdict']}, so what it forbids "
                                f"was never reached")
        ln, src = M.definition(rel, r["prop"])
        rows.append([f"`{r['prop']}`", " ".join(code_lines(src)), readings[r["prop"]], verdict(r)])
    cols = [("Witness", 300, {}), (f"Its definition (`{rel[5:]}`)", 1000),
            ("What its violation shows reachable (the diagram's reading)", 900), ("TLC, unmutated", w - 2200)]
    return c.table(x, y, cols, rows, size=13.5, anchor="witnesses")


def other_rows_table(c, x, y, w, ev, readings, unmutated=("none",)):
    """The rows that are neither a matrix cell nor an unmutated witness: a Never... property run under a
    mutation. readings: {row name: the diagram's reading}."""
    rows_ = [r for r in ev["tlc"]["rows"] if r["prop"].startswith("Never") and r["mut"] not in unmutated]
    if [r["name"] for r in rows_] != list(readings):
        raise M.CorpusError(f"{ev['tlc']['file']}: such rows {[r['name'] for r in rows_]}, the diagram reads "
                            f"{list(readings)}")
    rows = [[f"`{r['name']}`", f"`{r['mut']}`", f"`{r['prop']}`", verdict(r), readings[r["name"]]] for r in rows_]
    return c.table(x, y, [("Row", 260, {}), ("Under", 200), ("Property", 330), ("TLC", 500),
                          ("What it shows (the diagram's reading)", w - 1290)], rows, size=13.5, accent="amber")


def theorems_table(c, x, y, w, ev, roles):
    """Every THEOREM and LEMMA of the proof module (#theorems), in order, with its hypothesis and statement.
    roles: {name: what it is for (the diagram's reading)}, one per statement."""
    st = ev["statements"]
    if [s["name"] for s in st] != list(roles):
        raise M.CorpusError(f"{ev['files']['proof']}: statements {[s['name'] for s in st]}, the diagram reads "
                            f"{list(roles)}")
    rows = []
    for s in st:
        hyp = f"`{s['assume']}`" if s["assume"] else "—"
        rows.append({"cells": [f"`{s['name']}`", s["kind"].lower(), hyp, f"`{s['prove']}`", roles[s["name"]]],
                     "accent": "blue" if s["kind"] == "THEOREM" else "grey"})
    cols = [("Statement", 330, {}), ("Kind", 90), ("Hypotheses (ASSUME)", 560), ("Proves", 1180),
            ("What it is for (the diagram's reading)", w - 2160)]
    return c.table(x, y, cols, rows, size=13.5, anchor="theorems")


def cert_table(c, x, y, w, ev):
    """The certified run's routes, every line of the file's table, and its closing line."""
    ce = ev["cert"]
    rows = []
    for route, k, note in ce["routes"]:
        bad = route.startswith("LS4") or (note and "REJECTED" in note)
        rows.append({"cells": [route, n(k), note or "—"], "accent": "red" if bad else "grey"})
    cols = [("Route, as the file names it", 560, {}), ("Obligations", 140), ("The file's note", w - 700)]
    h = c.table(x, y, cols, rows, size=13.5, accent="blue" if ce["certified"] else "red", anchor="certification")
    h += 14
    h += c.para(x, y + h, w, ("**The file's last line:** " if ce["certified"] else "[[red|The file's last line:]] ")
                + ce["last"], 14, "ink") + 4
    return h


def proofs(c, x, y, w, ev, roles, assumptions_note=None):
    """The band of the proofs: every statement, then the proof run beside the certified run."""
    pr = ev["proof"]
    y += theorems_table(c, x, y, w, ev, roles) + 24
    half = (w - 30) / 2
    body = [f"`{ev['files']['proof_results'][5:]}`: \"All {pr['obligations']} obligations proved.\"",
            f"Assumptions: **{pr['assumptions']}**" + (f" ({assumptions_note})" if assumptions_note else ""),
            f"Prover: {pr['prover']}",
            "The run printed nothing else." if not pr["notes"] else
            "[[red|The run also printed:]] " + "; ".join(f"\"{x_}\"" for x_ in pr["notes"]),
            f"\"{pr['words']}\""]
    hh = c.card(0, 0, half, "The proof run", body, draw=False, size=13.5)
    th = cert_table(c, x + half + 30, y, half, ev)
    c.card(x, y, half, "The proof run", body, accent="blue", size=13.5, h=max(hh, th))
    return y + max(hh, th)


def lean(c, x, y, w, ev, ns, mirror_ns=None, extra_card=None):
    """The Lean band: the encoding's theorems with the axioms each depends on, the mirror's, and the graph check."""
    lr = ev["lean"]
    ax = lr["axioms"]

    def thm_lines(prefix, names):
        out = []
        for t in names:
            k = f"{prefix}.{t}"
            if k not in ax:
                continue
            f_, ln_, axs = ax[k]
            out.append(f"`{t}` (`{f_}`, line {ln_}): depends on {', '.join(f'`{a}`' for a in axs) or 'no axioms'}")
        missing = [t for t in names if f"{prefix}.{t}" not in ax]
        if missing:
            out.append(f"Also stated: {', '.join(f'`{t}`' for t in missing)}, which the results file lists and "
                       f"reports no axioms for.")
        return out

    words = lr["words"].split("; ")[0]
    unit = ev["lean_unit"]
    cards = [(f"`TopakSpec/{unit}.lean`: the theorems, by induction on reachable states",
              thm_lines(ns, lr["theorems"][unit]) + [f"\"{words}\" (`{M.LEAN_RESULTS[5:]}`)"], "blue", {})]
    if mirror_ns:
        mu = ev["mirror_unit"]
        cards.append((f"`TopakSpec/{mu}.lean`: a decidable mirror, proved equal to the encoding",
                      thm_lines(mirror_ns, lr["theorems"][mu]), "blue", {}))
    if "graph" in ev:
        cards.append(("What the graph check is", [
            "`graph-check.sh` dumps TLC's state graph for each `Mut` and evaluates the mirror on it: every edge a "
            "`Next` step, every `Next` step an edge or a stutter, the same initial states, every property TLC's "
            "value in every state. **A test, not a proof**: the mirror's theorems are the proof."], "teal", {}))
    cards.append(("Which files", [
        f"`{M.LEAN_RESULTS[5:]}`" + (f" and `{M.GRAPH_RESULTS[5:]}`" if "graph" in ev else "") +
        " are the files ADR-0053 cites. The later " + f"`{M.LEAN_LATER[10:]}`" +
        (f" and `{M.GRAPH_LATER[10:]}`" if "graph" in ev else "") + f" are compared, and say the same of "
        f"`{ev['name']}`."] + ([extra_card] if extra_card else []), "grey", {}))
    y += row_cards(c, x, y, w, 30, cards, size=13.5)
    if "graph" in ev:
        y += 24
        y += graph_table(c, x, y, w, ev)
    return y


PREMISES = "spec/theorem-premise-binding.md"
PREMISE_HEAD = ["Theorem", "Checked in", "Record", "Breaks under", "Row premises", "Parameter and gap premises",
                "At the reference (Annex B)"]
DERIVED_HEAD = ["Derived premise", "Holds when (any route)", "Record"]


def premises(c, x, y, w, ev, props, derived, note=None):
    """The rows of the binding's theorem table that are this module's, every cell, and its derived premise."""
    prem = [[strike(x_) for x_ in r] for r in md_rows(PREMISES, PREMISE_HEAD, props)]
    y += c.table(x, y, [(h_, w_) for h_, w_ in zip(PREMISE_HEAD, (290, 700, 180, 300, 560, 330, w - 2360))],
                 prem, size=13.5, accent="blue") + 14
    der = md_rows(PREMISES, DERIVED_HEAD, derived)
    y += c.table(x, y, [(DERIVED_HEAD[0], 290, {}), (DERIVED_HEAD[1], 1300), (DERIVED_HEAD[2], w - 1590)],
                 der, size=13.5, accent="blue") + 14
    y += c.para(x, y, w, f"The rows of `{PREMISES[5:]}`'s theorem table that are this module's, and its derived "
                "premise, every cell. G3 draws the whole table; the T-0045 rows open on G1." +
                (f" {note}" if note else ""), 13.5, "muted")
    return y


def elsewhere(c, x, y, w, ev, ids):
    """The other diagrams that name the module's file in their committed SVGs: `ids`, checked equal to the set
    that do (the I family aside)."""
    manifest = json.loads((HERE / "manifest.json").read_text("utf-8"))
    fname = pathlib.PurePosixPath(ev["files"]["module"]).name
    rx = re.compile(rf"(?<![\w_]){re.escape(fname)}")
    found = [pid for pid in manifest if not pid.startswith(lib.LOCAL_FAMILIES)
             and rx.search((HERE / manifest[pid]["file"]).read_text("utf-8"))]
    if sorted(found) != sorted(ids):
        raise M.CorpusError(f"the diagrams that name {fname} are {sorted(found)}, the diagram lists {sorted(ids)}")
    rows = [[linked(poster_link(pid), f"**{pid}**"), lib.unlinked(manifest[pid]["title"])] for pid in ids]
    h = c.table(x, y, [("Diagram", 160, {}), ("Its title (the manifest's)", w - 160)], rows, size=13.5) + 14
    h += c.para(x, y + h, w, f"Every diagram whose committed SVG names `{fname}`, found at build time and compared "
                "with this list. Those diagrams draw the module as part of a record; this one draws the module.",
                13.5, "muted")
    return y + h


def digests(c, x, y, w, ev, extra=(), note=None):
    """Every file drawn whose digest is cited, its digest at the pin, and every place that cites it."""
    y += digests_table(c, x, y, w, ev, extra) + 14
    tf = ev["tlc"]["file"] if ev["tlc"] else None
    txt = "Each citation is compared with the file at the pin when the diagram is built, and the build fails on any " \
          "that differs."
    if ev["tlc"] is not None and ev["tlc"].get("order_only"):
        txt = (f"`{tf}` names no digest of the module: the build checks that the module has not changed since the "
               f"file was committed (git, at the pin), which shows order, not which text TLC ran. ") + txt
    y += c.para(x, y, w, txt + (f" {note}" if note else ""), 13.5, "muted")
    return y


def record_table(c, x, y, w, rel, header, widths, compare, accent="blue", anchor=None,
                 against="Against the results file (compared at build time)"):
    """A record's results table, drawn whole, and each row compared with the results file by `compare(row)`,
    which returns a cell for the diagram's comparison column or raises. Returns the height."""
    rows = md_table(rel, header)
    out = [[strike(x_) for x_ in r] + [compare(r)] for r in rows]
    cols = [(h_, w_) for h_, w_ in zip(header, widths)] + [(against, w - sum(widths))]
    return c.table(x, y, cols, out, size=13.5, accent=accent, anchor=anchor)


def graph_table(c, x, y, w, ev):
    """The Lean mirror evaluated on TLC's state graphs: every row of the module's, every number."""
    rows = []
    for r in ev["graph"]["rows"]:
        props = "; ".join(f"`{p}` agrees on {n(a)} of {n(o)}, false in {n(f)}" for p, a, o, f in r["props"])
        rows.append([f"`{r['mut']}`", n(r["states"]), n(r["edges"]), n(r["steps"]), str(r["initial"]),
                     f"{n(r['not_next'])} · {n(r['not_edge'])}", r["init"], props, f"**{r['verdict']}**"])
    cols = [("`Mut`", 150, {}), ("States", 110), ("Edges", 120), ("`Next` steps", 130), ("Initial", 90),
            ("Edges not `Next` · `Next` not edges", 210), ("`Init`", 90), ("Properties, state by state", w - 1060),
            ("Verdict", 160)]
    return c.table(x, y, cols, rows, size=13.5, accent="teal")


def digests_table(c, x, y, w, ev, extra=()):
    """Every file drawn whose digest a results file or record cites, with its digest at the pin and every place
    that cites it (each citation already checked equal by modules.evidence). extra: further (file, sha16, cited by)
    rows the diagram has checked itself."""
    rows = []
    for rel in sorted(ev["sha"]):
        by = ev["cited"].get(rel, [])
        rows.append([f"`{rel}`", f"`{ev['sha'][rel]}`",
                     ", ".join(f"`{b}`" for b in by) if by else "[[red|no results file names its digest]]"])
    for rel, sha, by in extra:
        rows.append([f"`{rel}`", f"`{sha}`", by])
    cols = [("File, at the pin", 900, {}), ("sha256, first 16 hex digits", 330),
            ("Cited, with that digest, by (each compared at build time)", w - 1230)]
    return c.table(x, y, cols, rows, size=13.5, accent="grey")



def flow_picture(c, X0, y, WW, src, gate, refused, region, record, props, arrows, key, sz=13.5):
    """The mechanism as a flow: a source -> a gate (a refusal below it) -> the state, a region of cards -> a record
    -> the properties, each read on the record or the state. src, gate, refused, record: (title, [body], accent);
    region: (label, accent, [(title, [body], accent)]); props: [(title, [body], "record" | "state")]; arrows:
    {"ask", "write", "act", "end"} labels (None to omit); key: the key paragraph. Card titles do not lead with a
    code name, so the picture takes no anchor from the definitions drawn below it. Returns the y below the key."""
    xa, wa = X0, 300
    xb, wb = X0 + 420, 760
    xc, wc = X0 + 1360, 820
    xd, wd = X0 + 2340, 470
    xe = X0 + 2940
    we = WW - (xe - X0)
    gap = 18
    label, racc, cards = region
    sh = [c.card(0, 0, wc - 40, t, b, draw=False, size=sz) for t, b, _ in cards]
    region_h = 40 + sum(sh) + gap * (len(sh) - 1) + 24
    top = y + 14
    gh = c.card(0, 0, wb, gate[0], gate[1], draw=False, size=sz, bullets=False)
    rh = c.card(0, 0, wb, refused[0], refused[1], draw=False, size=sz) if refused else 0
    region_h = max(region_h, gh + rh + 60 if refused else gh + 20)
    c.region(xc, top, wc, region_h, label, racc)
    sy = top + 40
    for (t, b, acc), h in zip(cards, sh):
        c.card(xc + 20, sy, wc - 40, t, b, accent=acc, size=sz, h=h)
        sy += h + gap
    gy = top + 10
    c.card(xb, gy, wb, gate[0], gate[1], accent=gate[2], size=sz, h=gh, bullets=False)
    ph = c.card(0, 0, wa, src[0], src[1], draw=False, size=sz)
    c.card(xa, gy + gh / 2 - ph / 2, wa, src[0], src[1], accent=src[2], size=sz, h=ph)
    ay = gy + gh / 2
    if refused:
        ry = top + region_h - rh
        c.card(xb, ry, wb, refused[0], refused[1], accent=refused[2], size=sz, h=rh, dash="6 4")
        c.arrow([(xb + wb / 2, gy + gh), (xb + wb / 2, ry)], "red", dash="7 5")
    c.arrow([(xa + wa, ay), (xb, ay)], src[2], label=arrows.get("ask"), lpos=0.5, loff=(0, -16))
    c.arrow([(xb + wb, ay), (xc, ay)], gate[2], label=arrows.get("write"), lpos=0.5, loff=(0, -16))
    dy = top + 10
    dh = 0
    if record:
        dh = c.card(0, 0, wd, record[0], record[1], draw=False, size=sz)
        c.card(xd, dy, wd, record[0], record[1], accent=record[2], size=sz, h=dh)
        c.arrow([(xc + wc, dy + dh / 2), (xd, dy + dh / 2)], racc, label=arrows.get("act"), lpos=0.5,
                loff=(0, -16))
    on_record = [p_ for p_ in props if p_[2] == "record"]
    on_state = [p_ for p_ in props if p_[2] == "state"]
    py = dy
    rec_mid = dy + (dh / 2 if record else 0)
    bx = xd + wd + (xe - xd - wd) / 2
    for i, (t, b, _) in enumerate(on_record):
        h = c.card(0, 0, we, t, b, draw=False, size=sz)
        c.card(xe, py, we, t, b, accent="blue", size=sz, h=h)
        if i == 0:
            c.arrow([(xd + wd, rec_mid), (xe, rec_mid)], "blue", dash="4 4")
        else:
            c.arrow([(bx, rec_mid), (bx, py + h / 2), (xe, py + h / 2)], "blue", dash="4 4")
        py += h + gap
    hs = [c.card(0, 0, we, t, b, draw=False, size=sz) for t, b, _ in on_state]
    qy = max(py, top + region_h - sum(hs) - gap * (len(hs) - 1))
    for (t, b, _), h in zip(on_state, hs):
        c.card(xe, qy, we, t, b, accent="blue", size=sz, h=h)
        c.arrow([(xc + wc, qy + h / 2), (xe, qy + h / 2)], "blue", dash="4 4")
        qy += h + gap
    bottom = max(top + region_h, qy - gap)
    if arrows.get("end"):
        end_y = top + region_h + 40
        c.arrow([(xc + wc / 2, top + region_h), (xc + wc / 2, end_y)], "green", dash="7 5")
        c.label(xc + wc / 2, end_y + 14, arrows["end"], "green", sz)
        bottom = max(bottom, end_y + 24)
    key_y = bottom + 30
    return key_y + c.para(X0, key_y, WW, key, 13.5, "muted")
