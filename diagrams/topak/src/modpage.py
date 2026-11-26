"""The page every diagram of one TLA+ module is built from (family I): layout helpers and the bands whose content
is the module's evidence, read by modules.py. A module's own diagram (d_i<n>_<slug>.py) supplies the cards and
prose that need writing by hand, and calls these for the rest.

Not a diagram itself: the generator imports only d_*.py.
"""
import re

import lib
import modules as M
from lib import STATUS, text_width

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


def md_table(rel, header):
    """The Markdown table under the header row `header` (its cells, as a list) in `rel` at the pin: list of rows,
    each a list of cells."""
    lines = M.text(rel).split("\n")
    hits = [i for i, ln in enumerate(lines) if ln.startswith("|") and _cells(ln) == header]
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
    """The rows of md_table(rel, header) whose first cell is one of `keys` (code runs), in the order of keys; each
    must be there once."""
    rows = md_table(rel, header)
    out = []
    for k in keys:
        hit = [r for r in rows if r[0] == f"`{k}`"]
        if len(hit) != 1:
            raise M.CorpusError(f"{rel}: a row for {k} {len(hit)} times, not once")
        out.append(hit[0])
    return out


# ---------------------------------------------------------------------------------------------- the bands
def matrix_table(c, x, y, w, ev, props, expect, labels):
    """The mutation x property matrix (#matrix), every cell from the results file, each compared with `expect`
    {(mut, prop): verdict}, the diagram's own reading of the module's header, which must match the file in both
    directions. labels: {mut: what it is}."""
    res = ev["tlc"]
    muts, got_props, cells = M.matrix(res)
    if got_props != props:
        raise M.CorpusError(f"{res['file']}: properties {got_props}, the diagram expects {props}")
    if set(cells) != set(expect):
        raise M.CorpusError(f"{res['file']}: cells {sorted(cells)} are not the {len(expect)} the diagram expects")
    rows = []
    for mt in muts:
        r = [f"`{mt}`", labels[mt]]
        for p in props:
            row = cells[(mt, p)]
            if row["verdict"] != expect[(mt, p)]:
                raise M.CorpusError(f"{res['file']}: {mt} x {p} is {row['verdict']}, the diagram expects "
                                    f"{expect[(mt, p)]}")
            r.append(verdict(row))
        rows.append({"cells": r, "accent": "grey" if mt == "none" else "red"})
    pw = (w - 230 - 640) / len(props)
    cols = [("Mutation", 230, {}), ("What it is (the module's header)", 640)] + [(f"`{p}`", pw) for p in props]
    return c.table(x, y, cols, rows, size=13.5, anchor="matrix")


def witnesses_table(c, x, y, w, ev, readings):
    """The Never... rows (#witnesses): each property's definition, and the row that violates it. readings:
    {prop: the diagram's own reading of what it shows reachable}."""
    rel = ev["files"]["module"]
    ws = M.witnesses(ev["tlc"])
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
        acc = "red" if route.startswith("LS4") else "grey"
        rows.append({"cells": [route, n(k), note or "—"], "accent": acc})
    cols = [("Route, as the file names it", 560, {}), ("Obligations", 140), ("The file's note", w - 700)]
    h = c.table(x, y, cols, rows, size=13.5, accent="blue" if ce["certified"] else "red", anchor="certification")
    h += 14
    h += c.para(x, y + h, w, ("**The file's last line:** " if ce["certified"] else "[[red|The file's last line:]] ")
                + ce["last"], 14, "ink") + 4
    return h


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
