"""E5 — Two bounds below the intent boundary (ADR-0063 and ADR-0064, Proposed, revised R1): revocation bounded in
effects, with no premise about time, and duration bounded by the plane's ticks, under a declared premise."""
from lib import Canvas, STATUS, STATE_CC, text_width, fs

ID, SLUG = "E5", "revocation-and-ticks"

W = 3400


# ---------------------------------------------------------------------------------------------- helpers (from C10)
def row_cards(c, x, y, w, gap, specs, size=14):
    """A row of cards of equal height, measured over every card. specs: (title, body, accent, kwargs)."""
    n = len(specs)
    cw = (w - (n - 1) * gap) / n
    h = max(c.card(0, 0, cw, t, b, draw=False, size=size, status=k.get("status")) for t, b, _, k in specs)
    for i, (t, b, acc, k) in enumerate(specs):
        c.card(x + i * (cw + gap), y, cw, t, b, accent=acc, h=h, size=size, **k)
    return h


def stack(c, x, y, w, specs, gap=16, size=14):
    """Cards one under another. specs: (title, body, accent, kwargs). Returns the bottom."""
    for t, b, acc, k in specs:
        y += c.card(x, y, w, t, b, accent=acc, size=size, **k) + gap
    return y - gap


def band(c, x, y, title, accent="ink", status=None, extra=""):
    c.text(x, y + 22, title, 22, accent, bold=True)
    if status:
        c.status(x + text_width(title, 22, True) + 20, y + 4, status, extra)
    return y + 54


def circle(c, cx, cy, r, label, accent, dash=None, size=13):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    c.add(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" {fs(accent + "-t", accent)} stroke-width="1.8"{d}/>', cy + r)
    c.text(cx, cy + size * 0.36, label, size, accent, "middle", bold=True)


def meter(c, x, y, w, filled, accent, caption):
    """The outstanding charge against `K_up`: cells 1 .. K_up - 1 may be charged, the K_up cell never is."""
    labels = ["1", "2", "…", "`K_up` − 1", "`K_up`"]
    gap = 6
    cw = (w - gap * (len(labels) - 1)) / len(labels)
    h = 34
    for i, lab in enumerate(labels):
        cx = x + i * (cw + gap)
        if i == len(labels) - 1:
            c.rect(cx, y, cw, h, "red", tint=True, dash="5 4", rx=5, sw=1.6)
            c.text(cx + cw / 2, y + 22, lab, 13, "red", "middle", bold=True)
        else:
            c.rect(cx, y, cw, h, accent, tint=i < filled, rx=5, sw=1.4, fill_token=None if i < filled else "bg")
            c.text(cx + cw / 2, y + 22, lab, 13, accent if i < filled else "muted", "middle", bold=True)
    return h + 8 + c.para(x, y + h + 8, w, caption, 13, "muted")


def meter_h(c, w, caption):
    return 34 + 8 + c.para(0, 0, w, caption, 13, "muted", draw=False)


def pills_line(c, X0, X1, y, items, size=13.5):
    """A status strip: items are (label, [(text, accent, dash)]). Wraps; returns the y below it."""
    px0 = X0 + 80
    px = px0
    c.text(X0, y + 15, "Status", 15, "faint", bold=True)
    for lab, pills in items:
        lw = text_width(lab, size, True) + 8
        pw = sum(text_width(t, 11.5, True) + 18 + 8 for t, _, _ in pills)
        if px + lw + pw > X1:
            px = px0
            y += 34
        c.text(px, y + 15, lab, size, "ink", bold=True)
        px += lw
        for t, acc, dash in pills:
            px += c.pill(px, y, t, acc, 11.5, dash=dash) + 8
        px += 22
    return y + 34


# ---------------------------------------------------------------------------------------------- the diagram
def build():
    c = Canvas(ID, "Two bounds below the intent boundary: revocation bounded in effects, with no premise about time, "
               "and duration bounded by the plane's ticks, under a declared premise",
               "A plane that is cut off cannot tell \"not revoked\" from \"revoked, and not yet heard\". **ADR-0063** makes "
               "it stop on something of its own: the intent boundary reads the plane's record and answers with "
               "watermarks, and a plane may have fewer than `K_up` effects outstanding, a count with no clock in it. "
               "**ADR-0064** adds the bound a count cannot give, on duration: the plane's clock is its ticks, numbered "
               "from the charter and each signed by a certificate of replicas on their own clocks, with every interval "
               "a count of ticks from a named tick. **The second bound has a premise about time and the first has none, "
               "and that is why they are two records** (ADR-0064 Findings, 2). **Both are Proposed, both are an "
               "overlay and not the archetype, and nothing here is built.**",
               W, "ADR-0063 (Proposed, R1): provenance note, Status note, Context and its precedents table, Decision "
               "§1–§8, §4's table, Options, Consequences, Open obligations, History R1; ADR-0064 (Proposed, R1): "
               "provenance note, Status note, Context, Decision §1–§8, §6's table, Options, Consequences, Findings 1–2, "
               "Open obligations, History R1; ADR-0032 §1–§3 and §2's table, Options (B5); ADR-0039 §1, §8 (`K`, "
               "strict, `Coupling.tla`); ADR-0042 §2; ADR-0059 §4–§6; ADR-0061 §1's table; ADR-0062 §1, §2, §5, §6, "
               "§11; ADR-0065; ADR-0067 §3 (`FD10-outstanding-bound`, R1); ADR-0068 §1 TM14, §2 T-0068-2, T-0068-3, "
               "T-0068-5, T-0068-11, §3 A-0068-2, A-0068-10; ADR-0058 §6; ADR-0029 A2; spec/Outstanding.tla "
               "(8ecb0b147c7748ac; header, findings 1–4, `Safe`, witnesses), spec/Outstanding-rows.txt, "
               "spec/Outstanding-results-2026.11.10.txt (b5cfced141d1926e), spec/Outstanding-proof-results-"
               "2026.11.10.txt (98a3a4be28d53ce7), spec/Outstanding-proof-cert-results-2026.11.10.txt "
               "(eefef346a4a7f2ca); spec/PlaneClock.tla (7d7ced23419c1df2; header, `ClockPremise`, properties, "
               "witnesses), spec/PlaneClock-rows.txt, spec/PlaneClock-results-2026.11.10.txt (60505f0b484ecf8f), "
               "spec/PlaneClock-proof-results-2026.11.10.txt (7494a3a6bc66c1e5), spec/PlaneClock-proof-cert-results-"
               "2026.11.10.txt (11e2a6d24dd954d1). The tick timeline in band 4 is a schematic of ADR-0064 Findings 1, "
               "with illustrative positions", state=STATE_CC)
    X0, X1 = c.x0, c.x1
    WW = X1 - X0
    y = c.y

    # ================================================================== status strip
    V, R, G = "violet", "red", "grey"
    y = pills_line(c, X0, X1, y, [
        ("ADR-0063", [(STATUS["proposed"][0] + " · C1 · R1", "amber", "6 4")]),
        ("ADR-0064", [(STATUS["proposed"][0] + " · no confirmation criterion · R1", "amber", "6 4")]),
        ("both", [("An overlay, not the archetype ⟨Q11⟩", G, None)]),
        ("`Outstanding`", [("Checked · 40 rows, all as expected", V, None),
                           ("Proved · 1,871 obligations", V, None),
                           ("certified, with 6 LS4 temporal steps that no checker confirms", V, "4 3"),
                           ("No clock in the module", "green", None)]),
        ("`PlaneClock`", [("Checked · 38 rows, all as expected", V, None),
                          ("Proved · 535 obligations", V, None),
                          ("certified, with 6 LS4 temporal steps that no checker confirms", V, "4 3"),
                          ("In discrete time, under §4's premise", "amber", "6 4")]),
        ("Lean arithmetic of ADR-0064 §2's two rules", [("Not met", R, "2 3")]),
        ("`FD10-outstanding-bound` (ADR-0067)", [("Not written", R, "2 3")]),
        ("the reference", [(STATUS["notbuilt"][0], R, "2 3")]),
        ("ratified, or in force", [("Nothing", R, "2 3")]),
    ])
    y += 8
    y += c.para(X0, y, WW, "**Proposed means nothing here is in force.** The custodian decided ⟨2⟩ (the TTL as the "
                "safety parameter, later overtaken), ⟨12⟩ (revocation is bounded in effects, and that is the safety "
                "property), ⟨13⟩ (a clock held by a quorum as the second bound, for duration), ⟨18⟩ (a governor's own "
                "clock as a watchdog only), answered ⟨Q11⟩, ⟨Q12⟩ and ⟨Q13⟩, and on 2026.11.10 decided that overdue is "
                "by the governor's own clock. **Every other choice is the drafter's.** **R1** took the modules' "
                "findings the same day. **Checked** is TLC's rows at small constants; **proved** is TLAPS obligations "
                "under each module's assumptions; neither word is used of running code, and there is none. **One "
                "author, one day**, and §4's argument as corrected has been read by its author only (ADR-0063 §8).",
                14.5, "muted") + 40

    # ================================================================== band 1: the watermark loop
    y = band(c, X0, y, "The record goes up, the watermark comes down, and what no watermark covers stays under `K_up` "
             "(ADR-0063 §1–§3, §5)", status="proposed", extra="C1 · nothing here is built")
    top = y + 20
    WL = 2250
    GAPC = 70
    WR = WW - WL - GAPC
    xr = X0 + WL + GAPC
    S = 14
    inset = 30
    iw = WL - 2 * inset

    MECH = ("The intent boundary's mechanism: the plane's Observer ⟨12⟩", [
        "**This is `R3-observer-live`'s shape (ToO §5.4), pointed upward** (§1).",
        "**It archives a segment of the plane's record and runs its checks**, then orders a watermark. What those "
        "checks are is open (Open obligations).",
        "**The watermark is the mechanism's act. No person signs it** ⟨Q12⟩: the plane's tempo would be that "
        "person's attention (Options).",
        "**Its reading is a trust root for the watermark** (T-0068-5): a watermark for a record nobody checked "
        "releases a charge nobody read (Consequences).",
    ], "teal")
    CMD = ("The commander", [
        "**Stops a plane by a fence or a revocation**, and not by withholding attention ⟨Q12⟩.",
        "The intent boundary orders it, and **every watermark ordered after it carries the moved fence** (§2, §4).",
    ], "brown")
    wm, wc = 1300, iw - 1300 - 60
    hm = c.card(0, 0, wm, MECH[0], MECH[1], draw=False, size=S)
    hcmd = c.card(0, 0, wc, CMD[0], CMD[1], draw=False, size=S)
    hb = max(hm, hcmd)
    ytop_card = top + 40
    c.region(X0, top, WL, hb + 70, "Above: the intent boundary, the commanded plane's mechanism (ADR-0060)", "teal",
             dash=None)
    c.card(X0 + inset, ytop_card, wm, MECH[0], MECH[1], accent="teal", size=S, h=hb)
    xcmd = X0 + inset + wm + 60
    c.card(xcmd, ytop_card, wc, CMD[0], CMD[1], accent="brown", size=S, h=hb, tint=False)
    bnd_bot = top + hb + 70

    # the plane
    link_gap = 230
    ptop = bnd_bot + link_gap
    PL = ("The plane's replicas: its charge (§3)", [
        "**Charges what is outstanding**: a lease's whole count when the lease is granted, and an `ordered` entry "
        "when it is admitted.",
        "**A charge is released when a watermark covers it.**",
        "**Grants no lease, and admits no `ordered` entry, that would take the charge to `K_up`.** The charter gains "
        "`kUp`.",
        "**A plane is a havoc issuer** (ADR-0059 §4). Under capture its charge means nothing, and each governor's "
        "account below does (`Outstanding`'s header).",
    ], "violet")
    wp = 1300
    wpm = iw - wp - 60
    cap_p = ("**Strict**: the charge, with this grant, stays under `K_up`, so the capacity is `K_up` − 1. \"At most "
             "`K_up`\" lets one more through (`M_ATMOST`).")
    hpl = c.card(0, 0, wp, PL[0], PL[1], draw=False, size=S)
    hpm_body = c.card(0, 0, wpm, "The plane's charge, against `K_up`", ["Cells charged by leases' counts and "
                      "`ordered` entries that no watermark covers yet."], draw=False, size=S)
    hpm = hpm_body + meter_h(c, wpm - 32, cap_p) + 6
    hp = max(hpl, hpm)
    c.region(X0, ptop, WL, hp + 70, "The autonomous plane: seven replicas (ADR-0061)", "violet", dash=None)
    ypc = ptop + 40
    c.card(X0 + inset, ypc, wp, PL[0], PL[1], accent="violet", size=S, h=hp)
    xpm = X0 + inset + wp + 60
    c.card(xpm, ypc, wpm, "The plane's charge, against `K_up`", ["Cells charged by leases' counts and `ordered` "
           "entries that no watermark covers yet."], accent="violet", size=S, h=hp, tint=False)
    meter(c, xpm + 16, ypc + hpm_body - 6, wpm - 32, 3, "violet", cap_p)
    pl_bot = ptop + hp + 70

    # the vehicles
    vgap = 230
    vtop = pl_bot + vgap
    G1 = ("Governor g1: its own account, kept for itself ⟨R1⟩", [
        "**Accepts a lease, or carries out an `ordered` entry, only if** its own leases **and `ordered` entries** that "
        "no watermark covers, with this one, stay under `K_up`.",
        "**Checks each watermark's certificate against the chain.** It does not take its plane's word for what has "
        "been read (`M_TRUSTMARK`).",
    ], "teal")
    G2 = ("Governor g2: the same account", [
        "**Under a captured plane, each honest vehicle produces fewer than `K_up` effects** after a revocation (§4).",
        "**Writes each entry it permits or refuses to a chain**, and at the lease's end **seals** it; the plane orders "
        "the seal (ADR-0062 §6).",
    ], "teal")
    wg = (iw - 60) / 2
    cap_g = "Its own leases' counts and its `ordered` entries, uncovered: under `K_up`, strictly."
    hg = max(c.card(0, 0, wg, t, b, draw=False, size=S) for t, b, _ in (G1, G2)) + meter_h(c, wg - 32, cap_g) + 4
    c.region(X0, vtop, WL, hg + 70, "Each vehicle: a governor and a stack (ADR-0062 §1)", "teal")
    ygc = vtop + 40
    for i, (t, b, a) in enumerate((G1, G2)):
        gx = X0 + inset + i * (wg + 60)
        hgb = c.card(0, 0, wg, t, b, draw=False, size=S)
        c.card(gx, ygc, wg, t, b, accent=a, size=S, h=hg)
        meter(c, gx + 16, ygc + hgb - 6, wg - 32, 2 if i == 0 else 1, "teal", cap_g)
    v_bot = vtop + hg + 70

    # the link, between the boundary and the plane
    ly1, ly2 = bnd_bot + 30, ptop - 30
    c.line(X0, ly1, X0 + WL, ly1, "grey", 1.6, "3 6")
    c.line(X0, ly2, X0 + WL, ly2, "grey", 1.6, "3 6")
    c.para(X0 + 10, ly1 + 22, 330, "**The link** (T-0068-11, delegated). **Loss only subtracts**: cut, no watermark "
           "arrives and the plane stops granting before `K_up` (§5).", 13.5, "grey")
    # arrows across the link
    xu, xd, xf = X0 + 700, X0 + 1150, xcmd + wc / 2
    c.arrow([(xu, ypc), (xu, ytop_card + hb)], "violet", sw=2.6,
            label="its log, with each lease's sealed record, as it is made, while the link holds (§1)", lpos=0.5, lw=330)
    c.arrow([(xd, ytop_card + hb), (xd, ypc)], "teal", sw=2.6,
            label="a watermark, with a commit certificate (§2; ADR-0059 §5)", lpos=0.5, lw=300)
    c.arrow([(xf, ytop_card + hb), (xf, ypc)], "red", sw=2.2, dash="7 5",
            label="a fence or a revocation: pushed, and pulled in every watermark (§2; ADR-0059 §6)", lpos=0.5, lw=360)
    # arrows between the plane and the vehicles
    yv1, yv2 = ypc + hp, ygc
    xa, xb, xc = X0 + 560, X0 + 900, X0 + 1700
    c.arrow([(xa, yv1), (xa, yv2)], "violet", sw=2.4, label="a lease: its whole count charged at the grant", lpos=0.5,
            lw=300)
    c.arrow([(xb, yv2), (xb, yv1)], "teal", sw=2.4, label="the seal: the lease's closed chain (ADR-0062 §6)", lpos=0.5,
            lw=300)
    c.arrow([(xc, yv1), (xc, yv2)], "teal", sw=2.4,
            label="the watermark, relayed: each governor checks its certificate", lpos=0.5, lw=300)

    # right column
    rb = stack(c, xr, top - 10, WR, [
        ("A watermark carries three things, and a certificate (§2)", [
            "**The plane index it has read through.**",
            "**The digests of the lease records sealed in that segment.**",
            "**The fences of every plane above**, so the fence is pulled as well as pushed (ADR-0059 §6).",
            "**It comes down with a commit certificate** (ADR-0059 §5). A captured plane cannot forge one, nor a "
            "vehicle's seal (`Outstanding`'s header).",
            "**It covers one segment and is not cumulative** (§4).",
        ], "teal", {}),
        ("Coupling's shape, between planes (ADR-0039; ADR-0063 §1, §3, §7)", [
            "**ADR-0039 couples a Thinker's admits to its Observer's watermark**: `seq(t) − mark(o, r) < K`, a count "
            "and not a time, **strict because `≤ K` admits a `K+1` backlog**, which `Coupling.tla` found.",
            "**ADR-0063 points that shape upward**: the intent boundary reads the plane, and what it has not read "
            "stays under `K_up`.",
            "**Reported upstream under ADR-0058 §6** ⟨Q11⟩: liveness coupled to admission between planes, and a "
            "record read as it is made. If the archetype takes them, ADR-0039, ADR-0031 and ADR-0005 owe entries (§7).",
        ], "grey", {"tint": False}),
        ("A cut link fails closed (§5)", [
            "**With the link above cut, no watermark arrives, the charge only grows, and the plane stops granting "
            "before `K_up`.** Vehicles spend the leases they hold, and then hold.",
            "[[red|The first revision's pushed fence failed open]]: no news meant carry on until `T_intent`.",
            "**A jammed plane stops after `K_up` effects** (Consequences). A small `K_up` stops it sooner; a large one "
            "lets more through under a revoked intent.",
        ], "green", {}),
        ("What reading buys besides (§5)", [
            "**What the intent boundary has read is archived above.** A captured plane's log is not evidence, **and "
            "that now holds of the unread tail only**, fewer than `K_up` effects.",
        ], "teal", {"tint": False}),
        ("The seal, and a vehicle alone (ADR-0062 §5, §6)", [
            "**Under a lease the governor writes each entry it permits or refuses** to a chain on the vehicle, "
            "hash-linked and signed. **At the lease's end it seals the chain**, and the plane orders the seal as one "
            "entry and runs the mechanism checks there.",
            "**Nothing a governor permitted is void**: the effect has happened. A check that fails at the seal, or "
            "above, is a finding, and can only subtract. **A captured vehicle's chain is not evidence.**",
            "**A vehicle that stops hearing its plane is alone and loses its lease at once**: it permits no "
            "actuation, keeps listening, and may send a beacon within its count, which is an effect ⟨R1⟩.",
        ], "grey", {"tint": False}),
    ], gap=18, size=14)

    fbot = max(v_bot, rb) + 36
    lg = c.legend(X0, fbot, [
        ("arrow", "violet", "the plane (P, the replicas)"),
        ("arrow", "teal", "the mechanism: the intent boundary's, and each governor's"),
        ("arrow", "red", "a fence or a revocation: only removes authority", "7 5"),
        ("box", "violet", "a charge cell: outstanding, not yet covered"),
        ("box", "red", "`K_up`: never reached", "5 4"),
    ])
    y = fbot + lg + 80

    # ================================================================== band 2: §3
    y = band(c, X0, y, "What is charged, the strict rule, and each governor's own account (ADR-0063 §3, as revised ⟨R1⟩)",
             status="proposed", extra="C1: a condition on every grant an autonomous plane makes")
    h = row_cards(c, X0, y, WW, 28, [
        ("What is charged, and what releases it", [
            "**A lease's whole count, when the lease is granted**; **an `ordered` entry, when it is admitted.**",
            "**A charge is released when a watermark covers it.**",
            "**What is charged is an effect**: a `local` entry and an `ordered` one, as ADR-0042 §2 counts effects "
            "for an Observer.",
            "[[grey|Not charged]]: a report to a peer topic (ADR-0065); a tick, which is not an effect.",
        ], "teal", {}),
        ("The rule is strict, so `kUp` is at least 2 ⟨R1⟩", [
            "**The plane grants no lease, and admits no `ordered` entry, that would take the outstanding charge to "
            "`K_up`.**",
            "**\"At most `K_up`\" lets one more through**, which ADR-0039's model found of `K` (`M_ATMOST`).",
            "**The capacity is `K_up` − 1, and a `kUp` of one grants nothing**: `NeverGranted` holds at `KUp` = 1 "
            "(row `w-k1-nogrant`; `Outstanding` finding 4).",
            "**A lease whose count is `K_up` or more can never be granted.**",
        ], "amber", {"status": "proposed"}),
        ("Each governor keeps the same account for itself ⟨R1⟩", [
            "**It accepts a lease, or carries out an `ordered` entry, only if** the counts of its own leases **and "
            "`ordered` entries** that no watermark covers, with this one, stay under `K_up`.",
            "[[red|M_ORDEREDFREE]]: a rule that named only leases, as §3 first read, lets a captured plane admit "
            "`ordered` entries without limit (`Outstanding` finding 1).",
            "[[red|M_TRUSTMARK]]: a governor that takes its plane's word for what has been read. **A plane is a havoc "
            "issuer** (ADR-0059 §4), so a governor checks each watermark's certificate against the chain.",
        ], "teal", {}),
        ("Why at the grant, and where the floor would carry it", [
            "**A governor's permits are not ordered** (ADR-0062 §2), **so the charge is taken at the grant** "
            "(Options: \"count at each permit\" is not available).",
            "**`FD10-outstanding-bound`** (ADR-0067 §3, R1) would forbid both: at the plane, a grant or `ordered` "
            "admit that takes the charge to `K_up`; at a governor, a lease or `ordered` entry that takes its own "
            "there. [[red|Not written.]]",
            "**`K_up` is a placeholder**: at least 2 and above any lease's count, and its relation to an intent's "
            "budget is open.",
        ], "grey", {"tint": False}),
    ], size=14)
    y += h + 80

    # ================================================================== band 3: §4
    y = band(c, X0, y, "What that bounds, with no premise about time, and the argument as revised (ADR-0063 §4, §6; "
             "Context)", status="proposed", extra="§4's argument read by its author only")
    top = y
    wl3 = 1640
    wr3 = WW - wl3 - 60
    xr3 = X0 + wl3 + 60
    c.text(X0, top + 16, "**§4's table, whole**", 16, "ink")
    t4 = c.table(X0, top + 32, [("Property", 330, {"bold": True}), ("Statement", wl3 - 330)], [
        {"cells": ["Effects after a revocation are bounded", "After the intent boundary orders a revocation or a fence, "
                   "**the vehicles of an honest plane produce fewer than `K_up` further effects.** Under a captured "
                   "plane, **each honest vehicle produces fewer than `K_up`.** A vehicle revoked by its own plane "
                   "produces at most what is left of its lease's count"], "accent": "teal"},
        {"cells": ["Stale rules are bounded", "A narrower intent or a tightened bundle cannot reach a plane that is cut "
                   "off. **Superseded rules govern fewer than `K_up` effects there**"], "accent": "teal"},
        {"cells": ["Exposure is bounded", "**An intent never grants more leases than its budget. A lease never permits "
                   "more entries than its count. An entry never runs past its extent** (ADR-0062 §4)"],
         "accent": "teal"},
    ], size=14, accent="teal")
    ly = top + 32 + t4 + 24
    lb = stack(c, X0, ly, wl3, [
        ("ADR-0032's first clause is kept (§6)", [
            "**\"Clocks buy liveness, never safety.\"** The bound in §4 reads no clock. **C3 does not apply, and this "
            "is the point of the record**: the proposal's first revision reversed the clause (Status note; Context).",
            "**The lattice analysis proposes that no safety theorem have a timing premise among its ancestors**, so "
            "that the clause is computed and not only stated. §4's properties meet that: no variable or guard in "
            "`Outstanding` is a time (§8).",
            "**What a clock can still extend is one entry in progress**, by the residual ADR-0064 §5 states (band 4).",
        ], "blue", {"tint": False}),
    ], size=14)
    c.text(xr3, top + 16, "**The Context's precedents: the corpus has met a clock problem four times and has not once "
           "answered with a better clock**", 16, "ink")
    tp = c.table(xr3, top + 32, [("Precedent", wr3 * 0.66), ("What it did", wr3 * 0.34, {"bold": True})], [
        ["ADR-0034's nonce is a hash of epoch and log index, \"so freshness comes from the log and not a clock\" (ToO "
         "§2.6). ADR-0050's sign-on is fresh \"because of what it names\" (ToO §7.10)", "Took an interval's origin "
         "from the log"],
        ["ADR-0039's bound on unread effects is \"a count, not a time\" (ToO §5.4)", "Counted the mechanism's own acts, "
         "which have no drift"],
        ["ADR-0039 coupled liveness to admission, so that a dead Observer stops its Thinker", "Made silence fail "
         "closed"],
        ["R8, the break-glass TTL, was withdrawn because it needed trusted time, and ADR-0045 refused a time source "
         "(ToO §10)", "Withdrew the interval"],
    ], size=14, accent="grey")
    rb3 = stack(c, xr3, top + 32 + tp + 24, wr3, [
        ("A log orders and does not measure (Context)", [
            "ADR-0032: **\"Causality orders events and bounds no interval.\"**",
            "**A fence is a message**, and a plane that is cut off cannot tell \"not revoked\" from \"revoked, and not "
            "yet heard\". **So it has to stop on something of its own. A count of its own acts is exact.**",
        ], "grey", {"tint": False}),
    ], size=14)
    y = max(lb, rb3) + 50

    # the argument as a chain
    c.text(X0, y + 16, "**§4's argument for the first row, as revised ⟨R1⟩**, step by step (`Outstanding` findings 2 "
           "and 3)", 17, "ink")
    y += 34
    STEPS = [
        ("① Watermarks after the revocation carry the fence", [
            "**Every watermark ordered after the revocation carries the moved fence**, since every watermark carries "
            "the fences of every plane above (§2).",
        ], "red", {"tint": False}),
        ("② The stop on hearing one carries the bound", [
            "**A plane or a governor that hears one stops.** A later watermark releases a charge whose lease may have "
            "produced effects after the revocation.",
            "A hearer that released it and went on granting would break the bound: [[red|M_NOSTOP]] (finding 3).",
        ], "teal", {}),
        ("③ What was covered before is sealed", [
            "**Every lease covered by a watermark ordered before the revocation is sealed and produces nothing more**: "
            "`SealedIsSpent` (`M_EARLYRELEASE` breaks it).",
        ], "teal", {}),
        ("④ A watermark is not cumulative", [
            "**It covers one segment.** So what stays charged is what **no** watermark ordered before the revocation "
            "covers, and not only what the last one left (finding 2).",
        ], "teal", {}),
        ("⑤ So every later effect is already charged", [
            "**Every effect after the revocation is charged to a lease or an entry that no pre-revocation watermark "
            "covers**, and those charges together stay under `K_up` (§3's strict rule).",
        ], "teal", {}),
        ("⑥ Delay only lowers what is released", [
            "**An adversary can deliver such a watermark late or not at all**, which only lowers what is released.",
            "**No clock is read at any step** (§6).",
        ], "green", {}),
    ]
    gap6 = 54
    h6 = row_cards(c, X0, y, WW, gap6, STEPS, size=14)
    cw6 = (WW - 5 * gap6) / 6
    for i in range(5):
        ax = X0 + (i + 1) * cw6 + i * gap6
        c.arrow([(ax + 4, y + h6 / 2), (ax + gap6 - 4, y + h6 / 2)], "teal", sw=2.4)
    y += h6 + 90

    # ================================================================== band 4: ADR-0064
    y = band(c, X0, y, "An autonomous plane's clock is its ticks: numbered from the charter, signed by a certificate "
             "on its replicas' own clocks (ADR-0064 §1–§6)", status="proposed",
             extra="no confirmation criterion · nothing here is built")
    top = y
    WT = 1780
    xr4 = X0 + WT + 60
    wr4 = WW - WT - 60

    # ---- the tick timeline (Findings 1)
    c.text(X0, top + 16, "**Ticks numbered from the charter, and the stall the first draft would have hidden** (§1; "
           "Findings 1)", 17, "ink")
    lab_w = 470
    xt0 = X0 + lab_w + 40
    u = (WT - lab_w - 90) / 12
    px = [xt0 + i * u for i in range(13)]
    LA = ("**§1: tick τ says τ periods of `T_tick` have passed since the charter was applied.** The numbers need not "
          "be consecutive. Each replica keeps one reading of its own monotonic clock, taken at the charter.")
    LB = ("[[red|The first draft: each period measured from the tick before.]] Rejected (Findings 1; Options); "
          "`M_RELATIVETICK` breaks `NoGrantPastExpiry`.")
    hLA = c.para(0, 0, lab_w, LA, 13.5, draw=False)
    hLB = c.para(0, 0, lab_w, LB, 13.5, draw=False)
    yA = top + 60
    rowA_c = yA + max(hLA, 60) / 2
    yB = yA + max(hLA, 60) + 50
    rowB_c = yB + max(hLB, 60) / 2
    # the stall
    sx0, sx1 = px[4] + u * 0.45, px[11] - u * 0.45
    c.rect(sx0, yA - 6, sx1 - sx0, (yB + max(hLB, 60) + 6) - (yA - 6), "red", tint=True, dash="5 4", rx=8, sw=1.4)
    c.para(sx0 + 14, (rowA_c + rowB_c) / 2 - 30, sx1 - sx0 - 28, "**A stall**: an adversary lets no tick through, "
           "for a week, say, and then lets one through", 13.5, "red", anchor="middle")
    c.para(X0, yA + (max(hLA, 60) - hLA) / 2, lab_w, LA, 13.5, "ink")
    c.para(X0, yB + (max(hLB, 60) - hLB) / 2, lab_w, LB, 13.5, "ink")
    for i in range(5):
        circle(c, px[i], rowA_c, 19, str(i), "violet")
        circle(c, px[i], rowB_c, 19, str(i), "red", dash="4 3")
    circle(c, px[11], rowA_c, 22, "11", "violet")
    circle(c, px[11], rowB_c, 22, "5", "red", dash="4 3")
    # the axis
    ax_y = yB + max(hLB, 60) + 40
    c.line(px[0], ax_y, px[12] + 30, ax_y, "muted", 1.6)
    for i in range(13):
        c.line(px[i], ax_y - 6, px[i], ax_y + 6, "muted", 1.4)
        c.text(px[i], ax_y + 24, str(i), 12.5, "muted", "middle")
    c.para(px[0], ax_y + 34, WT - lab_w - 60, "Real time, in periods of `T_tick` from the charter's application "
           "(tick zero). **Numbered from the charter, the first tick after the stall carries it** (11). **From the "
           "tick before, the count moves by one** (5), **and the stall is hidden.** Schematic positions.", 13.5,
           "muted")
    tl_bot = ax_y + 34 + c.para(0, 0, WT - lab_w - 60, "Real time, in periods of `T_tick` from the charter's "
                                "application (tick zero). **Numbered from the charter, the first tick after the stall "
                                "carries it** (11). **From the tick before, the count moves by one** (5), **and the "
                                "stall is hidden.** Schematic positions.", 13.5, draw=False)
    c.para(X0, ax_y - 6, lab_w, "**The charter gains `tick`, the period.** The first intent counts from tick zero "
           "⟨Q13⟩.", 13.5, "muted")

    # ---- §2's two rules
    c.text(xr4, top + 16, "**§2: two rules on a replica's vote**, and which carries what ⟨R1⟩", 17, "ink")
    h2 = row_cards(c, xr4, top + 40, wr4, 28, [
        ("Rule 1: never sign a tick ahead of its own clock", [
            "**A replica signs tick τ only when its own elapsed time has reached τ periods.**",
            "**It carries availability**, ADR-0032's liveness side: it stops a captured or fast quorum burning a "
            "plane's intervals.",
            "**It carries no property in `PlaneClock`**: a tick ahead of real time moves an expiry and an extent "
            "nearer, which only subtracts (the module's finding on §2).",
        ], "violet", {}),
        ("Rule 2: never sign a grant behind its own clock", [
            "**A replica signs no lease and no `ordered` admit while, by its own clock read with the early margin "
            "(ADR-0031 E1), the next tick is due.**",
            "**It carries §4's bound**: `NoGrantPastExpiry` rests on it.",
            "**No time crosses a boundary**: a replica reads its own clock and signs or does not. No timestamp is "
            "exchanged and no external time is read, so ADR-0032 §3 holds as written.",
        ], "violet", {}),
    ], size=14)
    r2b = top + 40 + h2 + 20
    r2b = stack(c, xr4, r2b, wr4, [
        ("§2 and the arithmetic", [
            "**The arithmetic of the two rules is to be transcribed and proved**, as `mechanism/lean/Topak/Clock.lean` "
            "does for the subtracting interval (§8). [[red|Not met.]]",
            "**How far the rules fit PBFT's validity check** (ADR-0061 §2) is open, once PBFT is read.",
        ], "red", {"tint": False}),
    ], size=14)
    y = max(tl_bot, r2b) + 60

    # ---- §3, §4, §5
    top = y
    w3 = (WW - 2 * 40) / 3
    xs = [X0, X0 + w3 + 40, X0 + 2 * (w3 + 40)]
    b31 = stack(c, xs[0], top, w3, [
        ("§3: every interval is a number of ticks from a named tick ⟨Q13⟩", [
            "**An intent's `expiry`, a lease's `ttl`, a charter's `expiry`, an entry's duration and a release act's "
            "freshness are tick numbers.** Each end is a comparison in the log: the same on every replica, and "
            "checkable again at apply, which a per-replica clock is not (ToO §15 found that of `T_obs`).",
            "**An intent names a tick the plane has handed up**, and its `expiry` counts from that tick.",
            "**A lease's `ttl` counts from the tick at which the plane ordered the grant**, and ends no later than its "
            "intent's `expiry`.",
            "**The first intent counts from the charter's application, tick zero** ⟨Q13⟩. It is granted by the "
            "promotion, before the plane has ticked.",
            "**Anything withheld for a day arrives a day old.** That is the answer to the NATO reading's F1: an "
            "interval that starts at receipt can be started late by whoever holds the message (`M_RECEIPT`).",
        ], "amber", {"status": "proposed"}),
    ], size=14)

    # §4: the premise, with a picture of seven replicas
    P4 = ("§4: the premise, and the bound", [
        "**Premise: captured and slow replicas together are fewer than a certificate.** At seven replicas that is at "
        "most four (ADR-0061 §1). A replica is slow when its clock lags by more than its margin.",
        "**Then every certificate includes a replica that is neither captured nor slow.** It signed only because, by "
        "a sound clock, the latest tick was current. So at every grant the tick count is less than one period behind "
        "real time, and **no grant is made under an intent more than one tick period past its `expiry`.** A lease "
        "ends no later than its intent, so effects are bounded too, up to §5's residual.",
        "**A fast clock only subtracts**: it refuses grants early, and draws on the silence a plane tolerates.",
        "**A declared bound, not a safety theorem.** [[red|With the premise false the bound fails]] (`M_TOOSLOW`) "
        "⟨R1⟩, **and ADR-0063's bound still holds.**",
    ], "violet")
    pic_h = 150
    h4 = c.card(0, 0, w3, P4[0], P4[1], draw=False, size=14, status="proposed")
    c.card(xs[1], top, w3, P4[0], P4[1], accent="violet", size=14, status="proposed", h=h4 + pic_h)
    # the picture: seven replicas, four captured or slow, a certificate of five
    py = top + h4 + 20
    r = 24
    step = (w3 - 120) / 6
    cxs = [xs[1] + 60 + i * step for i in range(7)]
    cyr = py + 70
    for i, cx in enumerate(cxs):
        if i < 4:
            circle(c, cx, cyr, r, "C/S", "red", dash="4 3", size=12)
        else:
            circle(c, cx, cyr, r, "S", "violet", size=13)
    # bracket over a certificate of five
    bx0, bx1 = cxs[0] - r - 6, cxs[4] + r + 6
    c.line(bx0, py + 30, bx1, py + 30, "violet", 2)
    c.line(bx0, py + 30, bx0, py + 40, "violet", 2)
    c.line(bx1, py + 30, bx1, py + 40, "violet", 2)
    c.text((bx0 + bx1) / 2, py + 22, "**a certificate: 5 of 7** (ADR-0061 §1)", 13, "violet", "middle")
    c.text((cxs[0] + cxs[3]) / 2, cyr + r + 24, "captured or slow: at most 4", 13, "red", "middle")
    c.text((cxs[4] + cxs[6]) / 2, cyr + r + 24, "sound", 13, "violet", "middle")

    b33 = stack(c, xs[2], top, w3, [
        ("§5: a governor's own clock decides one thing: that the next tick is overdue ⟨18⟩", [
            "**A governor counts an entry's duration in ticks, and checks each tick number against its own elapsed "
            "time.** When the next tick is overdue, **the vehicle is alone and the lease ends** (ADR-0062 §5).",
            "**Overdue is by the governor's own clock** ⟨R1⟩, on the custodian's decision of 2026.11.10: the next "
            "tick is overdue when that clock reaches the tick's due time.",
            "**Under a captured plane the ticks are the captor's**, and the duration bound for an honest vehicle rests "
            "on that governor's own clock, which treats a lagging tick as overdue.",
        ], "teal", {}),
        ("The residual (§5; T-0068-2)", [
            "**A slow governor clock finds a tick overdue late, and can stretch the entry in progress, only when the "
            "plane's ticks have also stopped reaching it.** A bound on a declared value, plus drift: the shape of "
            "ADR-0045's finding 2.",
            "**Reachable**: `NeverStretched` is violated with a slow governor (`w-stretched-slow`), and holds with a "
            "sound or fast one.",
            "**Nothing else reaches it**: `NoStretchUnlessSlow`, proved.",
        ], "red", {"tint": False}),
    ], gap=18, size=14)
    y = max(b31, top + h4 + pic_h, b33) + 50

    # ---- §6 trades, and ADR-0032's table
    top = y
    w6 = 1500
    c.text(X0, top + 16, "**§6's table, whole: the trades are declared**", 16, "ink")
    t6 = c.table(X0, top + 32, [("Value", 330, {"bold": True}), ("Small", (w6 - 330) / 2),
                                 ("Large", (w6 - 330) / 2)], [
        ["`T_tick`", "A short loss of signal ends a lease", "A longer stretch for an entry in progress when the plane "
         "is gone"],
        ["`T_intent`, an intent's life in ticks", "A plane stopped at `K_up` gives up waiting for the link sooner",
         "An idle plane may act on an older intent"],
    ], size=14, accent="amber")
    c.para(X0, top + 32 + t6 + 14, w6, "**`T_tick` has to be long against a round of the plane over its radios**, or "
           "ticks fall behind and leases end with no adversary present (§6; A-0068-10). **Both values are "
           "placeholders**, and a measurement of a round is owed (Open obligations).", 14, "muted")
    xr6 = X0 + w6 + 60
    wr6 = WW - w6 - 60
    c.text(xr6, top + 16, "**ADR-0032 §2's table** (ratified, B5), and the row ADR-0064 §7 says it would owe if the "
           "archetype took the overlay", 16, "ink")
    t32 = c.table(xr6, top + 32, [("If the interval's failure…", wr6 * 0.25), ("Then it may use", wr6 * 0.42),
                                  ("Examples", wr6 * 0.33)], [
        {"cells": ["**Subtracts** authority", "a **local monotonic clock**, read with an asymmetric margin",
                   "lease expiry, passive e-stop, vote timeout"], "accent": "blue"},
        {"cells": ["**Adds or preserves** authority", "**trusted time**: a signed, attested time source outside the "
                   "principal", "break-glass TTL, Persona expiry, re-attestation intervals"], "accent": "blue"},
        {"cells": ["[[amber|Owed, not written]] (ADR-0064 §7)", "**an interval read by a quorum of local clocks**, "
                   "beside \"local clock\" and \"trusted time\"", "an intent's `expiry` and a lease's `ttl` in ticks, "
                   "at a plane that has them"], "accent": "amber"},
    ], size=14, accent="blue")
    y = max(top + 32 + t6 + 14 + 60, top + 32 + t32) + 80

    # ================================================================== band 5: the comparison
    y = band(c, X0, y, "The two bounds fail differently, and that is why they are two records (ADR-0064 Findings, 2)",
             status="proposed")
    wa = 330
    wb = (WW - wa) / 2
    tc = c.table(X0, y, [("", wa, {"bold": True}), ("ADR-0063: revocation, bounded in effects", wb),
                         ("ADR-0064: duration, bounded by the plane's ticks", wb)], [
        ["Premise", "**None about time.** No variable or guard in `Outstanding` is a time (§8)",
         "**Captured and slow replicas together are fewer than a certificate** (§4), and each sound clock's margin "
         "covers its drift (A-0068-2). The module's named `ASSUME ClockPremise`"],
        ["What it bounds", "**Effects after a revocation or a fence**: fewer than `K_up` from an honest plane, or from "
         "each honest vehicle under a captured one. Stale rules, and exposure (§4's table)",
         "**Duration**: no grant under an intent more than one tick period past its `expiry` (§4). A lease ends no "
         "later than its intent, so effects too, up to §5's residual"],
        ["Counted in", "**The mechanism's own acts**: a count, exact, with no drift (Context)",
         "**Ticks**: numbered entries in the log, from the charter, each signed by a certificate (§1)"],
        ["What it rests on", "**Each honest governor's own account**, and the intent boundary's reading, **a trust "
         "root for the watermark** (T-0068-5)",
         "**A plane's clocks, taken together: a trust root for the duration bound only** (T-0068-3). **The governor's "
         "clock: a residual in the slow direction** (T-0068-2)"],
        {"cells": ["When it fails, or under capture", "**No premise to fail.** Under a captured plane, each honest "
                   "governor still bounds its own vehicle (`HavocPlaneBoundedInEffects`). A cut link fails closed (§5)",
                   "[[red|With the premise false the bound fails]] (`M_TOOSLOW`): `NoGrantPastExpiry` is void and "
                   "`EffectsAfterRevocationBounded` is not (A-0068-2; TM14). **Under a captured plane the ticks are the "
                   "captor's**, and the duration bound is the honest governor's own clock"], "accent": "red"},
        ["What it does not stop", "**A plane that idles and then acts on an old intent is inside it.** ADR-0064 is for "
         "that (Consequences)", "**A slow governor clock stretches the entry in progress**, only when the ticks have "
         "also stopped reaching it (§5)"],
        ["ADR-0032", "**Its first clause stands**: the bound reads no clock (§6). C3 does not apply",
         "**Kept, with a residual** (Status note). **A declared bound and not a safety theorem** in the lattice "
         "analysis's sense (§4)"],
        {"cells": ["What its module proves", "**`Outstanding`**: `EffectsAfterRevocationBounded`, "
                   "`HavocPlaneBoundedInEffects`, `SealedIsSpent`, `CountExact`. **1,871 obligations proved**, with "
                   "no hypothesis about time; checked in 40 rows at `KUp` 2 and 3",
                   "**`PlaneClock`**: `NoGrantPastExpiry` under `ClockPremise`, `EntryEndsAtExtent`, "
                   "`NoStretchUnlessSlow`. **535 obligations proved, in discrete time**, with no clock rates or "
                   "margins; checked in 38 rows"], "accent": "violet"},
        ["The declared trade", "A small `K_up` stops a jammed plane sooner; a large one lets more through under a "
         "revoked intent (Consequences)", "`T_tick` and `T_intent`, small and large (§6's table)"],
    ], size=14, accent="grey")
    y += tc + 90

    # ================================================================== band 6: the modules
    y = band(c, X0, y, "The modules: what each states, what each mutation breaks, and what each abstracts (ADR-0063 "
             "§8, ADR-0064 §8)", "violet")
    top = y
    wm2 = (WW - 60) / 2
    xm = [X0, X0 + wm2 + 60]
    HV, HD = "[[red|breaks]]", "holds"

    # ---- Outstanding
    xo = xm[0]
    yo = top
    c.text(xo, yo + 18, "**`spec/Outstanding.tla`** (`8ecb0b147c7748ac`): revocation bounded in effects. "
           "**There is no clock in this module.**", 17, "ink")
    yo += 36
    yo += c.table(xo, yo, [("Property", wm2 * 0.3, {"mono": True}), ("States", wm2 * 0.48),
                           ("Proved as", wm2 * 0.22, {"mono": True})], [
        ["EffectsAfterHonest", "After a revocation, the vehicles of an honest plane produce fewer than `KUp` further "
         "effects (§4, first row)", "EffectsAfterHonestAlways"],
        ["EffectsAfterPerGovernor", "Under any plane, each honest governor produces fewer than `KUp` further effects",
         "EffectsAfterPerGovernorAlways"],
        ["EffectsAfterRevocationBounded", "The two together", "SafeAlways"],
        ["HavocPlaneBoundedInEffects", "Each honest governor has permitted fewer than `KUp` effects that no watermark "
         "covers, the plane signing anything (§3)", "HavocPlaneBoundedInEffectsAlways"],
        ["SealedIsSpent", "A lease a watermark covers produces no further effect (§4's argument)",
         "SealedIsSpentAlways"],
        ["CountExact", "No lease permits more entries than its count: §4's \"at most what is left of its lease's "
         "count\"", "CountExactAlways"],
    ], size=13.5, accent="violet") + 16
    yo += c.para(xo, yo, wm2, "**`Safe`, all four, holds in five rows**: `KUp` = 2 and 3, an honest and a captured "
                 "plane, and three slots at `KUp` = 3. **Mutations and what each breaks** (rows file; the plane is "
                 "honest unless the row says captured):", 14, "ink") + 10
    mc = [("Mutation", wm2 * 0.17, {"mono": True}), ("What it does", wm2 * 0.27), ("Honest", wm2 * 0.11),
          ("PerGovernor", wm2 * 0.12), ("HavocPlane", wm2 * 0.11), ("SealedIsSpent", wm2 * 0.11),
          ("Plane in the rows", wm2 * 0.11)]
    yo += c.table(xo, yo, mc, [
        ["M_NOCHARGE", "A lease is granted without charging the plane", HV, HD, HD, HD, "honest"],
        ["M_ATMOST", "The bound is \"at most `KUp`\", one more through", HV, HV, HV, HD, "honest"],
        ["M_TRUSTMARK", "A governor takes a captured plane's word for what has been read", "—", HV, HV, HD,
         "captured; `Safe` holds when honest"],
        ["M_EARLYRELEASE", "A watermark may cover a lease not yet sealed", HV, HV, HV, HV, "honest"],
        {"cells": ["M_NOSTOP", "A plane or governor that hears the moved fence does not stop. **Added, finding 3**",
                   HV, HV, HD, HD, "honest"], "accent": "amber"},
        {"cells": ["M_ORDEREDFREE", "§3's governor rule read literally: leases only. **Added, finding 1**", "—", HV,
                   HV, HD, "captured; `Safe` holds when honest"], "accent": "amber"},
    ], size=13.5, accent="violet") + 16
    yo += c.table(xo, yo, [("Witness", wm2 * 0.3, {"mono": True}), ("Violated: so this is reachable", wm2 * 0.7)], [
        ["NeverGranted", "A lease is granted. **It holds at `KUp` = 1**: the strict form grants nothing (finding 4)"],
        ["NeverEffect · NeverEffectAfter", "An effect; an effect after the revocation"],
        ["NeverTight", "`KUp` − 1 effects after the revocation, at `KUp` = 3: the bound is reached"],
        ["NeverRefusedAtBound", "The plane refuses at the bound"],
        ["NeverGovernorRefused", "A governor refuses, under a captured plane"],
        ["NeverStopped", "A plane or a governor stops"],
        ["NeverLateRelease", "A watermark ordered after the revocation releases a charge"],
        ["NeverRecycled · NeverCovered", "A slot is reclaimed; a watermark covers a lease"],
    ], size=13.5, accent="grey") + 16
    yo = stack(c, xo, yo, wm2, [
        ("What `Outstanding` abstracts (its header)", [
            "**Three lease slots**, of which `Active` may be used; a slot is reclaimed once read and released, so "
            "leases over a behaviour are unbounded and at most three are outstanding at once. **Two governors, "
            "honest.**",
            "**A watermark is one lease's coverage**, marked `before` or `after` the revocation; a watermark covering "
            "several is several delivered together, and the adversary may deliver fewer.",
            "**A pushed fence is not modelled**: it can only stop a plane or a vehicle earlier, so it subtracts. A plane "
            "is not re-seated. **An `ordered` entry is a lease of count one.** Reports and ticks do not appear.",
            "**A cut link, a late watermark and one never delivered are the same actions, taken or not.** Deadlock is "
            "not checked: a plane that has stopped is safe.",
        ], "grey", {"tint": False}),
        ("Results, 2026.11.10", [
            "**Checked**: 40 rows, all as expected, at `KUp` = 2, `MaxCount` = 2, two active slots, unless the row "
            "says otherwise (TLC 2.19).",
            "**Proved**: all 1,871 obligations of `Outstanding_proof.tla` (`f118d16087ce08d2`), under the one "
            "assumption `MaxCount \\in Nat` (tlapm 7824dab).",
            "**Certified, with 6 LS4 temporal steps that no checker confirms**: 1,257 closed by tlapm with no "
            "backend, 608 by SMT with a proof ethos accepted.",
        ], "violet", {}),
    ], gap=16, size=14)

    # ---- PlaneClock
    xp = xm[1]
    yp = top
    c.text(xp, yp + 18, "**`spec/PlaneClock.tla`** (`7d7ced23419c1df2`): duration, in explicit **discrete** time, "
           "under §4's premise", 17, "ink")
    yp += 36
    yp += c.table(xp, yp, [("Property", wm2 * 0.3, {"mono": True}), ("States", wm2 * 0.48),
                           ("Proved as", wm2 * 0.22, {"mono": True})], [
        ["NoGrantPastExpiry", "No grant under an intent one tick period or more past its `expiry`, as real time, the "
         "`expiry` being the one the intent named (§4). **Rests on `ClockPremise`**", "NoGrantPastExpiryAlways"],
        ["EntryEndsAtExtent", "A running entry is short of its extent and of the largest extent, in ticks applied, and "
         "its governor's own clock has not passed the next tick's due time (ADR-0062 §4; §5)",
         "EntryEndsAtExtentAlways"],
        ["NoStretchUnlessSlow", "A governor whose clock is not slow runs no entry past one overdue tick in real time. "
         "**Added ⟨R1⟩**", "NoStretchUnlessSlowAlways"],
    ], size=13.5, accent="violet") + 16
    yp += c.para(xp, yp, wm2, "**`ClockPremise`**: `Cardinality(Captured \\cup Slow) < Cert`, waived only under "
                 "`M_TOOSLOW`. **`Safe` holds in seven rows**: one captured and one slow of four replicas with a "
                 "certificate of three (ADR-0061's 4 / 3 / tolerated 2), a fast replica, none faulty, `Base` = 1, a fast "
                 "or slow governor, extent 2. **Mutations and what each breaks**:", 14, "ink") + 10
    mp = [("Mutation", wm2 * 0.18, {"mono": True}), ("What it does", wm2 * 0.36), ("NoGrantPastExpiry", wm2 * 0.15),
          ("EntryEndsAtExtent", wm2 * 0.15), ("NoStretchUnlessSlow", wm2 * 0.16)]
    yp += c.table(xp, yp, mp, [
        ["M_ONECLOCK", "One replica's clock decides a certificate", HV, HD, HD],
        ["M_RECEIPT", "An intent's interval starts at receipt, not at the tick it names: F1", HV, HD, HD],
        ["M_RELATIVETICK", "A tick is measured from the tick before: §2's first draft (Findings 1)", HV, HD, HD],
        {"cells": ["M_TOOSLOW", "The premise is waived: two slow and one captured, a certificate. **Added ⟨R1⟩**. With "
                   "the default classes the bound still holds", HV, HD, HD], "accent": "amber"},
        ["M_NOEXTENT", "An entry with no extent loads (ADR-0062 §11)", HD, HV, HD],
        ["M_NOWATCHDOG", "An overdue tick ends nothing", HD, HV, HV],
    ], size=13.5, accent="violet") + 16
    yp += c.table(xp, yp, [("Witness", wm2 * 0.3, {"mono": True}), ("Violated: so this is reachable", wm2 * 0.7)], [
        ["NeverGranted · NeverGrantInSlack", "A grant; a grant after the true expiry, inside the one period of slack"],
        ["NeverGrantRefused · NeverTickRefused", "A certificate refuses a grant; refuses a tick"],
        ["NeverWithheld", "The intent reaches the plane after the tick it names"],
        ["NeverEntryRan · NeverExtentEnded", "An entry runs; an entry ends at its extent"],
        ["NeverAlone · NeverStalled", "A vehicle goes alone; real time passes the next tick's due time"],
        {"cells": ["NeverStretched", "**Only with a slow governor**: the residual. It holds with a sound or a fast "
                   "governor (`n-stretched-sound`, `n-stretched-fast`)"], "accent": "red"},
    ], size=13.5, accent="grey") + 16
    yp = stack(c, xp, yp, wm2, [
        ("What `PlaneClock` abstracts (its header; ADR-0064 §8)", [
            "**Discrete time**: `now` in whole units, `P` units to a period. **No clock rates and no margins**: a "
            "clock is of a class, sound (margin folded in), slow, fast or captured. **It says nothing of a real "
            "clock's drift.**",
            "**Going alone is urgent**: real time does not pass a running entry's overdue tick by the governor's own "
            "clock until the watchdog has acted.",
            "**A certificate is one atomic step** by at least `Cert` replicas: no ballot, primary or view (ADR-0061's "
            "and `Membership.tla`'s). **One intent, one governor, one lease flag, one entry at a time**; a lease's "
            "`ttl` is not modelled.",
            "**The timing budget is only partly expressible in TLA+** (ToO §11.3), and ADR-0032 defers a timed "
            "automaton.",
        ], "grey", {"tint": False}),
        ("Results, 2026.11.10", [
            "**Checked**: 38 rows, all as expected (TLC 2.19).",
            "**Proved**: all 535 obligations of `PlaneClock_proof.tla` (`bbfe21580db67b9d`); "
            "`NoGrantPastExpiryAlways` by `ClockPremise`.",
            "**Certified, with 6 LS4 temporal steps that no checker confirms**: 334 closed by tlapm with no backend, "
            "195 by SMT with a proof ethos accepted.",
        ], "violet", {}),
    ], gap=16, size=14)
    y = max(yo, yp) + 90

    # ================================================================== band 7: ratification, options, consequences
    y = band(c, X0, y, "What ratification needs, item by item; the options; the consequences (ADR-0063 §8, ADR-0064 "
             "§8; Options; Consequences)")
    top = y
    MET, NOT = "[[violet|Met for TLC and TLAPS ⟨R1⟩]]", "[[red|Not met]]"
    rc = [("Item", wm2 * 0.74), ("State", wm2 * 0.26)]
    c.text(xm[0], top + 16, "**ADR-0063 §8**", 17, "amber")
    c.text(xm[1], top + 16, "**ADR-0064 §8**", 17, "amber")
    r63 = c.table(xm[0], top + 32, rc, [
        ["**ADR-0059, ADR-0060 and ADR-0062 are ratified first**, or with this record", NOT + ": all three are "
         "Proposed"],
        ["**A module, `Outstanding`**, states at least `EffectsAfterRevocationBounded`, with no premise about time; "
         "`HavocPlaneBoundedInEffects`; `SealedIsSpent`. Mutations `M_NOCHARGE`, `M_ATMOST`, `M_TRUSTMARK`, "
         "`M_EARLYRELEASE`; `M_NOSTOP` and `M_ORDEREDFREE` added", MET + ". §4's argument as corrected is what is "
         "proved"],
        ["**The floor carries `FD10-outstanding-bound`** (ADR-0067)", NOT + ": the `federation` stage is not written"],
        ["**The reference shows** a plane that stops granting at the bound with its link cut, a governor that refuses "
         "a lease its own account cannot carry, and a watermark that releases a charge", NOT + ": not built"],
        ["**A reader who is not the drafter** (ADR-0029 A2)", NOT + ": read by its author only"],
    ], size=14, accent="amber")
    r64 = c.table(xm[1], top + 32, rc, [
        ["**ADR-0059 to ADR-0061 are ratified first**, or with this record", NOT + ": all three are Proposed"],
        ["**A module with explicit time, `PlaneClock`**, states at least `NoGrantPastExpiry` under a named `ASSUME` "
         "for §4's premise, and `EntryEndsAtExtent`. Mutations `M_ONECLOCK`, `M_RECEIPT`, `M_RELATIVETICK`, "
         "`M_NOWATCHDOG`; `M_TOOSLOW` and `NoStretchUnlessSlow` added", MET + ", **in discrete time**"],
        ["**The arithmetic of the two rules is transcribed and proved**, as `mechanism/lean/Topak/Clock.lean` does for "
         "the subtracting interval", NOT],
        ["**The reference shows** a tick refused by a replica whose clock has not reached it, a grant refused while a "
         "tick is due, and a lease ended by an overdue tick", NOT + ": not built"],
        ["**A reader who is not the drafter** (ADR-0029 A2)", NOT],
    ], size=14, accent="amber")
    y = top + 32 + max(r63, r64) + 50

    top = y
    c.text(xm[0], top + 16, "**ADR-0063: Options considered, whole**", 16, "ink")
    c.text(xm[1], top + 16, "**ADR-0064: Options considered, whole**", 16, "ink")
    oc = [("Option", wm2 * 0.36, {"bold": True}), ("Disposition", wm2 * 0.64)]
    o63 = c.table(xm[0], top + 32, oc, [
        {"cells": ["A TTL on a local clock as the safety bound, the first revision", "[[grey|Not taken ⟨12⟩.]] A slow "
                   "clock preserves authority, which is ADR-0032's test for an interval that needs trusted time"],
         "accent": "grey"},
        {"cells": ["A trusted time source", "[[grey|Not taken.]] ADR-0045 refused one: no issuance fixes a clock's "
                   "identity"], "accent": "grey"},
        {"cells": ["The intent's budget alone", "[[teal|Kept, as the absolute bound.]] It does not slide, so a long "
                   "mission needs either a large budget or a new intent for every stretch"], "accent": "teal"},
        {"cells": ["A pushed fence alone", "[[red|Rejected.]] It fails open under a cut link"], "accent": "red"},
        {"cells": ["A person signs each watermark", "[[grey|Not taken ⟨Q12⟩.]] The plane's tempo would be that "
                   "person's attention"], "accent": "grey"},
        {"cells": ["Count at each permit, in the plane's log", "[[grey|Not available.]] A governor's permits are not "
                   "ordered (ADR-0062 §2), so the charge is taken at the grant"], "accent": "grey"},
        {"cells": ["A governor that trusts its plane's account", "[[red|Rejected.]] `M_TRUSTMARK`"], "accent": "red"},
    ], size=14, accent="grey")
    o64 = c.table(xm[1], top + 32, oc, [
        {"cells": ["Each checker's own clock, with a margin, the first revision", "[[grey|Not taken ⟨13⟩.]] Every "
                   "clock is then a trust root in the slow direction"], "accent": "grey"},
        {"cells": ["A trusted time source", "[[grey|Not taken.]] ADR-0045 refused one"], "accent": "grey"},
        {"cells": ["Timestamps exchanged and a median taken", "[[grey|Not taken.]] A timestamp from another party is "
                   "content (ADR-0032 §3). Here a replica signs or does not, and no time value is exchanged"],
         "accent": "grey"},
        {"cells": ["Ticks measured from the tick before", "[[red|Rejected]] (Findings, 1). `M_RELATIVETICK`"],
         "accent": "red"},
        {"cells": ["An interval that starts at receipt", "[[red|Rejected.]] `M_RECEIPT`, the NATO reading's F1"],
         "accent": "red"},
        {"cells": ["The first intent counts from the first tick read above", "[[grey|Not taken ⟨Q13⟩.]] One rule for "
                   "every plane, at the price of a plane seated long before it deploys spending part of its first "
                   "intent waiting"], "accent": "grey"},
        {"cells": ["No duration bound", "[[grey|Not taken ⟨13⟩.]] An idle plane could act on an intent of any age"],
         "accent": "grey"},
        {"cells": ["Derive duration from the log's order", "[[grey|Not available.]] \"Causality orders events and "
                   "bounds no interval\" (ADR-0032)"], "accent": "grey"},
    ], size=14, accent="grey")
    y = top + 32 + max(o63, o64) + 50

    c.text(X0, y + 16, "**Consequences, as each record states them**", 16, "ink")
    y += 34
    h = row_cards(c, X0, y, WW, 28, [
        ("ADR-0063 · positive", [
            "**The safety bound has no premise about time**, and ADR-0032's first clause stands below the intent "
            "boundary.",
            "**A cut link fails closed.**",
            "**A captured plane is bounded in effects**, per honest vehicle, by a check each governor makes itself.",
            "**The unread record is bounded** by the same number.",
        ], "green", {}),
        ("ADR-0063 · negative", [
            "**The bound is in effects and not in seconds.** A plane that idles and then acts on an old intent is "
            "inside it. ADR-0064 is for that.",
            "**A jammed plane stops after `K_up` effects.** The trade is declared.",
            "**The intent boundary's reading is a trust root** for the watermark.",
            "**`K_up` is a placeholder**, and nothing here says how to choose it.",
            "**One author, one day.**",
        ], "red", {"tint": False}),
        ("ADR-0064 · positive", [
            "**One slow clock no longer holds authority open.** It takes a certificate's worth of captured and slow "
            "replicas.",
            "**Every interval has an origin an adversary cannot move.**",
            "**An expiry is a log comparison**, the same on every replica and checkable again at apply.",
            "**A governor's own clock is a watchdog**, and its failure stretches one entry.",
        ], "green", {}),
        ("ADR-0064 · negative", [
            "**A premise about time**, which the corpus had kept out of every bound below ADR-0032 §2's second row.",
            "**The plane must order one tick per period.** A plane that cannot complete a round in `T_tick` ends its "
            "own leases.",
            "**Drift accrues from the charter**, over the plane's whole life, and the margin has to cover it.",
            "**Under a captured plane the duration bound is one clock's again**, the honest governor's own.",
            "**One author, one day.**",
        ], "red", {"tint": False}),
    ], size=14)
    y += h + 30
    h = row_cards(c, X0, y, WW, 28, [
        ("ADR-0063 · open obligations", [
            "**The floor entry and the reference** (§8).",
            "**A value for `K_up`**, at least 2 and above any lease's count (§3), and its relation to an intent's "
            "budget.",
            "**What the intent boundary's checks are**, before it orders a watermark.",
            "**How a plane comes to know of a captured vehicle** (the swarm reading, Z2), which this record does not "
            "answer.",
        ], "red", {"tint": False, "status": "open"}),
        ("ADR-0064 · open obligations", [
            "**The transcription and the reference** (§8).",
            "**Values** for `T_tick`, `T_intent` and the margin, as placeholders first, and a measurement of a round.",
            "**How far the two rules fit PBFT's validity check** (ADR-0061 §2), once PBFT is read.",
            "**If the archetype takes it** (§7): ADR-0032 a third row, ADR-0031 a `ttl` in ticks, ADR-0045 the "
            "clock's row and finding 2 restated for §5's residual.",
        ], "red", {"tint": False, "status": "open"}),
    ], size=14)
    c.ymax = max(c.ymax, y + h)
    return c
