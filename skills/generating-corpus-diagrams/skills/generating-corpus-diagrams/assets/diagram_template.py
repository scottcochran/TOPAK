"""__ID__ — __TITLE__

Scaffolded by skills/generating-corpus-diagrams/scripts/new_diagram.py. Replace every placeholder card and row with
what the records say, cite each by section, and list every source in `sources`. Delete this paragraph."""
from lib import Canvas, STATUS, text_width

ID, SLUG = "__ID__", "__SLUG__"

W = 3400          # 3400 is usual; up to 3600. Height is computed.
S = 14            # body size for cards


# ---------------------------------------------------------------------------------------------- layout helpers
def row_cards(c, x, y, w, gap, specs, size=S):
    """A row of cards of equal height, MEASURED OVER EVERY CARD IN THE ROW (the overlap checker cannot see a card
    that outgrows a height computed over others). specs: (title, body, accent, kwargs). Returns the height."""
    n = len(specs)
    cw = (w - (n - 1) * gap) / n
    h = max(c.card(0, 0, cw, t, b, draw=False, size=size, status=k.get("status")) for t, b, _, k in specs)
    for i, (t, b, acc, k) in enumerate(specs):
        c.card(x + i * (cw + gap), y, cw, t, b, accent=acc, h=h, size=size, **k)
    return h


def stack(c, x, y, w, specs, gap=16, size=S):
    """Cards one under another. specs: (title, body, accent, kwargs). Returns the bottom."""
    for t, b, acc, k in specs:
        y += c.card(x, y, w, t, b, accent=acc, size=size, **k) + gap
    return y - gap


def band(c, x, y, title, accent="ink", status=None, extra=""):
    """A section heading with an optional status pill. Returns the y where content starts."""
    c.text(x, y + 22, title, 22, accent, bold=True)
    if status:
        c.status(x + text_width(title, 22, True) + 20, y + 4, status, extra)
    return y + 54


def status_strip(c, x0, x1, y, items):
    """items: (label, key, extra). key is a lib STATUS key, or ("Custom label", accent, dash) for a pill the
    library has no key for (for example ("Not written", "red", "2 3")). Wraps at x1. Returns the y below."""
    c.text(x0, y + 15, "Status", 15, "faint", bold=True)
    px0 = x0 + 80
    px = px0
    for lab, key, extra in items:
        lw = text_width(lab, 13.5, True) + 8
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


# ---------------------------------------------------------------------------------------------- the diagram
def build():
    c = Canvas(ID, "__TITLE__",
               "SUBTITLE: two to five sentences. What question the diagram answers, what the record decides, and "
               "**what is not in force or not built**, in bold.",
               W, "SOURCES: every record section, table and file drawn from, e.g. ADR-00nn §1–§4 (§2's table); "
               "spec/Module.tla header",
               # state="State of record: ... · drawn <date> for ...",   # set when drawn after the family's cut
               )
    X0, X1 = c.x0, c.x1
    WW = X1 - X0
    y = c.y

    # ---- status strip: every record drawn, with its status; what exists and what does not
    y = status_strip(c, X0, X1, y, [
        ("ADR-00nn", "proposed", "C1"),
        ("its module", ("Not written", "red", "2 3"), ""),
        ("the reference", "notbuilt", ""),
    ])
    y += c.para(X0, y, WW, "**Proposed means nothing here is in force.** One paragraph on what is settled and by "
                "whom, and what is the drafter's choice.", 14.5, "muted") + 34

    # ---- band 1: a row of cards
    y = band(c, X0, y, "BAND: the first question the diagram answers (ADR-00nn §1)", status="proposed")
    y += row_cards(c, X0, y, WW, 40, [
        ("CARD: a claim, as a title", ["**The claim in bold.** Then the sentence that says it, with its section "
                                       "(ADR-00nn §1)."], "blue", {}),
        ("CARD: what subtracts", ["A subtraction or a refusal is green or red; a dashed arrow only removes "
                                  "authority."], "green", {}),
        ("CARD: what is not built", ["Say it, do not imply it."], "red", {"status": "notbuilt"}),
    ]) + 40

    # ---- band 2: a record's table, drawn whole
    y = band(c, X0, y, "BAND: a record's table, every row and column (ADR-00nn §2)")
    y += c.table(X0, y, [("Column", 500, {"bold": True}), ("Column", 900), ("From", WW - 1400)], [
        ["`Name`", "What the record says of it", "ADR-00nn §2"],
        ["`Other`", "Every row of the record's table, none left out", "ADR-00nn §2"],
    ]) + 30
    return c
