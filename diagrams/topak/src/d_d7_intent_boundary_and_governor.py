"""D7 — Every effect is admitted at the intent boundary, and below it the lease pre-authorizes (ADR-0060 and ADR-0062,
Proposed, both revised R1 on 2026.11.10): a governor permits each entry against an exact count, and a vehicle that
stops hearing its plane loses its lease. With spec/Intent.tla and spec/Alone.tla."""
from lib import Canvas, STATUS, STATE_CC, text_width

ID, SLUG = "D7", "intent-boundary-and-governor"

W = 3400


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


def sub(c, x, y, s, size=16):
    c.text(x, y + size, s, size, "ink")
    return size + 16


MET = "[[green|Met for TLC and TLAPS ⟨R1⟩]]"
NOT = "[[red|Not met]]"


def build():
    c = Canvas(
        ID, "Every effect is admitted at the intent boundary, and below it the lease pre-authorizes: a governor permits "
            "each entry against an exact count, and a vehicle that stops hearing its plane loses its lease",
        "A command chain decides by one commander, and the corpus decides by quorum. ADR-0060 puts the commander "
        "where ADR-0050 already has one person act, **inside what a quorum voted and not above it**: a reversible "
        "effect is admitted at the intent boundary as an **intent**, an irreversible one singly, and **the autonomous "
        "plane below has no path that changes authority**. ADR-0062 makes the lease pre-authorize: **the plane orders "
        "one grant per lease, and a trusted governor on each vehicle permits each `local` entry with no further "
        "round**, against an exact count, every entry declaring an extent. **Going alone ends the lease at once.** "
        "Both records are **Proposed** and **an overlay, not the archetype** ⟨Q11⟩. Their modules are checked and "
        "proved in TLA+ (R1); **no floor entry is written, nothing is built, and nothing here is in force**.",
        W,
        "ADR-0060 (Proposed 2026.11.10, R1): provenance note, Status note, Context, Decision §1 (its table), §2, §3 (its "
        "table), §4–§7, Options considered, Consequences, Open obligations, History; ADR-0062 (Proposed 2026.11.10, R1): "
        "provenance note, Status note, Context, Decision §1, §2 (its table), §3 (its table), §4–§7, §8 (its table), "
        "§9 (D-0062-1), §10, §11, Options considered, Consequences, Open obligations, History; ADR-0050 §2, §6, "
        "`Regrant` (the successor grant; Accepted, provisional, B34); ADR-0055 §1, §2 (Proposed); ADR-0039 §1 "
        "(`K`); ADR-0041 §2 (`R3-observer-live`); ADR-0067 §3 (FD4, FD7, FD8, FD11, FD14; Proposed); "
        "diagrams/topak/src/d_d1_admit_pipeline.py (decide, order, effect); spec/Intent.tla header and actions "
        "(0c90ea5004c4f127), spec/Intent-rows.txt, spec/Intent-results-2026.11.10.txt, "
        "spec/Intent-proof-results-2026.11.10.txt, spec/Intent-proof-cert-results-2026.11.10.txt; spec/Alone.tla header "
        "and properties (9e7e04adb2ab5161), spec/Alone-rows.txt, spec/Alone-results-2026.11.10.txt, "
        "spec/Alone-proof-results-2026.11.10.txt, spec/Alone-proof-cert-results-2026.11.10.txt; spec/PlaneClock.tla "
        "header, spec/PlaneClock-rows.txt and the summary lines of its three result files; spec/Release.tla header, "
        "spec/Release-rows.txt and the summary lines of its three result files",
        state=STATE_CC)
    X0, X1 = c.x0, c.x1
    WW = X1 - X0
    y = c.y

    # ================================================================== status strip
    c.text(X0, y + 15, "Status", 15, "faint", bold=True)
    px0 = X0 + 80
    px = px0
    TEAL = "teal"
    strip = [
        ("ADR-0060", [(STATUS["proposed"][0] + " · C1, C2 · R1", "amber", "6 4")]),
        ("ADR-0062", [(STATUS["proposed"][0] + " · C1, C2 · R1", "amber", "6 4")]),
        ("position", [("An overlay, not the archetype ⟨Q11⟩", "amber", "6 4")]),
        ("rests on ADR-0050", [(STATUS["provisional"][0] + " · C1, C3, C4 · Batch 34", "blue", "4 3")]),
        ("ADR-0055 (the mesh)", [(STATUS["proposed"][0], "amber", "6 4")]),
        ("`spec/Intent.tla`", [("Checked · 35 rows, all as expected", TEAL, None),
                               ("677 obligations proved", TEAL, None),
                               ("Certified, with 5 LS4 temporal steps that no checker confirms", TEAL, None)]),
        ("`spec/Alone.tla`", [("Checked · 47 rows, all as expected", TEAL, None),
                              ("263 obligations proved", TEAL, None),
                              ("Certified, with 6 LS4 temporal steps that no checker confirms", TEAL, None)]),
        ("floor entries FD4, FD7, FD8, FD11, FD14 (ADR-0067)", [("Not written", "red", "2 3")]),
        ("the reference", [(STATUS["notbuilt"][0], "red", "2 3")]),
        ("ratified", [("None · nothing in force", "red", "2 3")]),
    ]
    for lab, pills in strip:
        lw = text_width(lab, 13.5, True) + 8
        pw = sum(text_width(p[0], 11.5, True) + 18 + 8 for p in pills)
        if px + lw + pw > X1:
            px = px0
            y += 34
        c.text(px, y + 15, lab, 13.5, "ink", bold=True)
        px += lw
        for t, acc, d in pills:
            px += c.pill(px, y, t, acc, 11.5, dash=d) + 8
        px += 18
    y += 42
    y += c.para(X0, y, WW, "**Proposed means nothing here is in force.** The custodian settled that each effect is "
                "admitted at the last commander's intent boundary ⟨10⟩, asked whether the last plane is a \"TOPAK lite\" "
                "⟨11⟩, and chose that **the lease pre-authorizes** and that going alone ends it ⟨21⟩ ⟨22⟩; answers ⟨Q2⟩–⟨Q4⟩, "
                "⟨Q9⟩, ⟨Q10⟩, ⟨Q14⟩, ⟨Q15⟩, ⟨Q20⟩ are marked where used, and every other choice is the drafter's. **C1** "
                "applies to both: an intent is a grant one operator makes (ADR-0060), and a governor's permit is a path "
                "every effect below the intent boundary travels (ADR-0062). **C2** applies to both: ADR-0060 §3 claims an "
                "autonomous plane's log holds no act that changes authority, and ADR-0062 §1 claims the governor is the "
                "only path to a vehicle's actuators and radio. **C3 does not apply while these are an overlay, and would "
                "on admission**: ADR-0060 §2 changes what bounds ADR-0050's successor grant, and ADR-0062 gives up "
                "ADR-0015's ordered admit before every effect and ADR-0033 §4's void, for the entries a governor permits. "
                "**Checked** is TLC at small constants; **proved** is TLAPS; neither word is used of running code, and "
                "there is none. One author, one day.", 14.5, "muted") + 34

    # ================================================================== band 1: the picture
    y = band(c, X0, y, "From the intent boundary to the actuators: one ordered intent, one ordered lease, and no round "
             "per entry (ADR-0060 §1–§3; ADR-0062 §1, §2, §5)", status="proposed", extra="nothing here is built")
    S = 13.5
    top = y + 40
    # columns
    RA_x, RA_w = X0, 1000
    a_lx, a_lw = RA_x + 24, 400
    a_rx, a_rw = RA_x + RA_w - 24 - 420, 420
    RB_x, RB_w = RA_x + RA_w + 130, 700
    b_x, b_w = RB_x + 24, RB_w - 48
    RC_x = RB_x + RB_w + 240
    RC_w = X1 - RC_x
    g_x, g_w = RC_x + 24, 660
    r_x = g_x + g_w + 150
    r_w = X1 - 24 - r_x

    def mh(spec, w_, **k):
        return c.card(0, 0, w_, spec[0], spec[1], draw=False, size=S, **k)

    # ---- the commanded plane
    QU = ("The quorum that promoted the mesh", [
        "**One tally** votes a mission's bundle revision, its mesh, and the charters and seatings it needs, together "
        "(ADR-0060 §5).",
        "The mesh is promoted at the intent boundary with its seatings and its activation budget (ADR-0055, "
        "Proposed). **That tally grants the first charter** (§2).",
    ], "violet")
    CO = ("The commander: one operator", [
        "**Later intents come from one person**: ADR-0050's successor grant (provisional). The request is an add, so "
        "it needs **a live lease and a live peer** (§2).",
        "**Inside what a quorum voted, not above it** (Context): \"the quorum acts once per seating, and round by "
        "round one operator acts\" (ToO §7.10).",
        "A person may hold an **orchestrator seat** here and choose among edges the mechanism already enabled ⟨Q10⟩: "
        "`Mediated`, attributed and not contained (§5).",
    ], "brown")
    RP = ("A person at a `release` seat (ADR-0066)", [
        "**An irreversible effect is admitted here, one at a time** (§1's table).",
        "HITL, and needs the link (§5).",
    ], "brown")
    IN = ("An intent: a charter for one round ⟨Q4⟩", [
        "Names the round's **task**, an **envelope**, an **activation budget**, an **`expiry`** and **the tick the "
        "`expiry` counts from** (ADR-0064). The charter gains `round` and `task` (§2).",
        "**Every field is the promoted seating's or narrower**, and not merely the last intent's, so a commander who "
        "narrows for one phase can restore the mission's bounds without a quorum.",
        "**Ends** at its `expiry`, when its budget is spent, when the commander ends or revokes it, or when any plane "
        "above is fenced (ADR-0059 §6).",
        "**What is admitted is an envelope, and not the act.** The commander voted for, or signed, everything it "
        "allows (§1).",
    ], "amber")
    # ---- the autonomous plane
    AB = ("Defined by one absence ⟨11⟩ ⟨Q2⟩ ⟨Q3⟩", [
        "**No path that changes authority.** ADR-0015 enumerates authority changes as exactly promotion and anchor "
        "issuance, and it has neither. **No person holds a seat at it.** \"Lite\" is a nickname for that (§3).",
    ], "violet")
    GR = ("Its one grant: a node's lease", [
        "**Made by the mechanism under a live intent**, \"with every field the seating's or narrower\" (ToO §2.11), "
        "and charged to the intent's activation budget.",
        "**Ordered once per lease**: the vehicle, the alphabet, the envelope, **a count** of entries and a `ttl` in "
        "ticks (ADR-0062 §2). A count is at most `K` (§8).",
        "A vehicle that hears its plane again may be leased again under the same intent, charged to its budget ⟨Q15⟩.",
    ], "teal")
    RL = ("It relays, and it ticks", [
        "**An irreversible act is relayed. The plane can refuse one and cannot originate one** (ADR-0060 §1).",
        "**Ticks, once per period** (ADR-0064), each a round of the plane, by which a vehicle hears it.",
        "Subtraction: a round's end, a revocation, an Observer's finding, expiry; a step of its charter's shrink "
        "schedule (ADR-0061).",
    ], "violet")
    HO = ("A claim about an honest plane's log ⟨R1⟩", [
        "**A captured plane is a havoc issuer** (ADR-0059 §4): it can sign a lease under an intent that has ended, and "
        "its log is not evidence. **What bounds it is the chain check and ADR-0063.**",
    ], "red")
    BR = ("By role (§3)", [
        "**T**: the same modules; nothing of T runs on a vehicle. **O**: the same floor, linked in, with bundles in "
        "Wasm only (ADR-0067). **P**: Byzantine agreement among the replicas (ADR-0061). **A**: stacks only. **K**: "
        "the governors' radios as transport, the archive above (ADR-0063, ADR-0065).",
        "A relay node with no stack may host a replica, and is declared ⟨Q3⟩.",
    ], "grey")
    # ---- the vehicle
    GV = ("The governor: trusted, mechanism, not a principal (§1)", [
        "**Verifies the chain** (ADR-0059 §5) and **holds the lease and the vehicle's key**.",
        "**Hosts the vehicle's replica** of the autonomous plane (ADR-0060 §3).",
        "**Evaluates the floor in Cedar** and each bundle on the chain as a Wasm module (ADR-0067).",
        "**Permits each `local` entry under the lease, and counts it** (§2). **The count is exact**: its own "
        "arithmetic over its own acts.",
        "**Lifts its own facts**: elapsed time, position, the lease's count, an entry's extent. No safety decision "
        "reads a clock a principal supplies (ADR-0032 §3), nor a position the stack supplies.",
        "**Hosts each tool as a Wasm component with one capability**, its declared channel: for a vehicle, an "
        "actuator interface (ADR-0034 A2).",
        "**Holds the radio**: the link to the plane and the peer topics (ADR-0065), so a stack cannot make its own "
        "vehicle alone.",
        "**Writes the record** (§6), and carries out hold and the terminal behaviour (§7).",
    ], "teal")
    SK = ("The stack: Byzantine", [
        "The autonomy software: **planning, perception, any model**. It is the Thinker (§1).",
        "**Asks; does not permit.** It does not choose hold or the terminal behaviour, and does not carry either out "
        "(§4, §7).",
        "**\"Fully Byzantine\" holds of the stack and cannot hold of the vehicle** (Context).",
    ], "red")
    RA = ("The radio", [
        "The link to the plane, and the peer topics (ADR-0065). **On the governor's side** (§1). "
        "[[red|Rejected]]: the radio on the stack's side, which would let the stack decide when its vehicle is alone.",
    ], "grey")
    AC = ("The actuators", [
        "**Reachable only through the governor** (§1; C2's exhaustiveness claim).",
        "An **extent** that is a distance or a region is a measurement, with the governor's position source a "
        "trust root for it (ADR-0068).",
    ], "grey")
    AL = ("Alone: it stops hearing its plane (§5) ⟨14⟩ ⟨22⟩", [
        "**Hears its plane** when it has applied the plane's log up to a tick that, **by its own clock**, is not yet "
        "overdue (ADR-0064 §5).",
        "**Going alone ends the lease at once.** The governor ends it where it stands; the plane orders the end when "
        "it learns of it, as ADR-0031 E1 has expiry: local, then ordered.",
        "**It permits no actuation**, so a stack gains nothing by being alone.",
        "**It keeps three things**: its terminal behaviour; **listening**, so a relayed fence or revocation still "
        "applies and a tick heard again ends the state; and **a beacon**, where the rules of engagement permit one: a "
        "report of fixed schema, of facts the governor measures, counted per lease.",
        "**The beacon is an effect** ⟨R1⟩ (ADR-0015, ADR-0065 §2). The proposal's \"the only effects are hold and the "
        "seating's terminal behaviour\" is true of actuation, and is read that way.",
    ], "red")
    TB = ("Hold, and an ending that grants nothing (§4, §7)", [
        "**Hold** ⟨Q14⟩: when an extent ends and no entry follows, the governor holds. Fixed at seating; the stack "
        "does not choose it; **the lease stays live**.",
        "**A lease ends** when its count is spent and its last entry's extent has run, at its `ttl`, when the plane "
        "ends or revokes it, when a fence arrives, and at once when the vehicle becomes alone.",
        "**The terminal behaviour is part of the seating**, voted with it: hold, return on a voted route, land or "
        "stop. **A recovery function in the governor's trust domain** carries it out.",
        "**\"A timeout is never a grant\"** (ADR-0024). Each vehicle class declares a safe state; reaching it in "
        "bounded time is the builder's obligation. \"A stall that never ends is safe\" (ToO §12 item 21) is false of a "
        "vehicle in flight.",
    ], "green")

    # heights
    hqu, hco, hrp, hin = mh(QU, a_lw), mh(CO, a_lw), mh(RP, a_lw), mh(IN, a_rw, status="proposed")
    hab, hgr, hrl, hho, hbr = (mh(AB, b_w), mh(GR, b_w), mh(RL, b_w), mh(HO, b_w), mh(BR, b_w))
    hsk = mh(SK, g_w - 150)
    hra, hac = mh(RA, r_w), mh(AC, r_w)
    vgap = 56
    bgap = 36

    # autonomous plane: the absence on top, then the grant and the relay, level with the governor
    yab = top + 40
    ygr = yab + hab + bgap
    yrl = ygr + hgr + bgap
    yho = yrl + hrl + bgap
    ybr = yho + hho + bgap
    b_bot = ybr + hbr + 30
    # vehicle: the governor's top is level with the grant, and it spans the relay
    ygv = ygr
    hgv = max(mh(GV, g_w), yrl + hrl - ygv)
    yra = ygv
    yac = max(yra + hra + 40, ygv + hgv - 40)
    ysk = ygv + hgv + 70
    row3 = max(ysk + hsk, yac + hac) + 70
    rw3 = RC_w - 48
    al_w = (rw3 - 30) / 2
    h3 = max(c.card(0, 0, al_w, AL[0], AL[1], draw=False, size=S),
             c.card(0, 0, al_w, TB[0], TB[1], draw=False, size=S))
    c_bot = row3 + h3 + 30
    # commanded plane: quorum, commander, release person down the left; the intent to their right
    yqu = top + 40
    yco = yqu + hqu + vgap
    yrp = max(yco + hco + vgap, yrl + hrl * 0.62 - hrp / 2)
    yin = max(top + 40, yqu + (yco + hco - yqu) / 2 - hin / 2)
    a_bot = max(yrp + hrp, yin + hin) + 30

    c.region(RA_x, top, RA_w, a_bot - top, "The commanded plane: the intent boundary ⟨10⟩ · people seated", "brown",
             dash=None)
    c.region(RB_x, top, RB_w, b_bot - top, "The autonomous plane · nobody seated · replicas on the governors",
             "violet", dash="10 6")
    c.region(RC_x, top, RC_w, c_bot - top, "A vehicle: a governor and a stack (ADR-0062 §1)", "teal", dash="10 6")

    c.card(a_lx, yqu, a_lw, QU[0], QU[1], accent=QU[2], size=S)
    c.card(a_lx, yco, a_lw, CO[0], CO[1], accent=CO[2], size=S)
    c.card(a_lx, yrp, a_lw, RP[0], RP[1], accent=RP[2], size=S)
    c.card(a_rx, yin, a_rw, IN[0], IN[1], accent=IN[2], size=S, status="proposed")
    c.card(b_x, yab, b_w, AB[0], AB[1], accent=AB[2], size=S)
    c.card(b_x, ygr, b_w, GR[0], GR[1], accent=GR[2], size=S)
    c.card(b_x, yrl, b_w, RL[0], RL[1], accent=RL[2], size=S)
    c.card(b_x, yho, b_w, HO[0], HO[1], accent=HO[2], size=S, tint=False, dash="6 4")
    c.card(b_x, ybr, b_w, BR[0], BR[1], accent=BR[2], size=S, tint=False)
    c.card(g_x, ygv, g_w, GV[0], GV[1], accent=GV[2], size=S, h=hgv)
    c.card(g_x + 150, ysk, g_w - 150, SK[0], SK[1], accent=SK[2], size=S, tint=False)
    c.card(r_x, yra, r_w, RA[0], RA[1], accent=RA[2], size=S)
    c.card(r_x, yac, r_w, AC[0], AC[1], accent=AC[2], size=S)
    c.card(g_x, row3, al_w, AL[0], AL[1], accent=AL[2], size=S, h=h3, tint=False)
    c.card(g_x + al_w + 30, row3, al_w, TB[0], TB[1], accent=TB[2], size=S, h=h3)

    def link(x0_, y0_, span0, x1_, y1_, span1, xv, **k):
        """Horizontal where both spans allow it, else one elbow at xv."""
        lo, hi = max(span0[0], span1[0]) + 24, min(span0[1], span1[1]) - 24
        if lo <= hi:
            yy_ = min(max(y1_, lo), hi)
            c.arrow([(x0_, yy_), (x1_, yy_)], **k)
        else:
            c.arrow([(x0_, y0_), (xv, y0_), (xv, y1_), (x1_, y1_)], **k)

    # arrows: commanded plane
    link(a_lx + a_lw, yqu + hqu / 2, (yqu, yqu + hqu), a_rx, yin + 50, (yin, yin + hin), a_rx - 50,
         accent="violet", sw=2.4, label="the first", lpos=0.5)
    link(a_lx + a_lw, yco + hco / 2, (yco, yco + hco), a_rx, yin + hin - 50, (yin, yin + hin), a_rx - 80,
         accent="brown", sw=2.4, label="each later", lpos=0.5)
    # intent -> the plane's one grant
    ygm = ygr + hgr * 0.4
    link(a_rx + a_rw, yin + hin / 2, (yin, yin + hin), b_x, ygm, (ygr, ygr + hgr), RA_x + RA_w + 65,
         accent="amber", sw=2.6, label="ordered here: the predecessor", lpos=0.5, lw=150)
    # release person -> relay
    link(a_lx + a_lw, yrp + hrp / 2, (yrp, yrp + hrp), b_x, yrl + hrl * 0.62, (yrl, yrl + hrl), RA_x + RA_w + 65,
         accent="brown", sw=2.2, label="an irreversible act, one at a time", lpos=0.5, lw=170)
    # plane <-> governor: five straight lanes
    xl, xg = b_x + b_w, g_x
    lm = 0.5
    c.arrow([(xl, ygr + hgr * 0.3), (xg, ygr + hgr * 0.3)], "teal", sw=2.8, label="the lease: one round, once",
            lpos=lm)
    c.arrow([(xg, ygr + hgr * 0.72), (xl, ygr + hgr * 0.72)], "teal", sw=2.0,
            label="the record; the seal at the lease's end", lpos=lm, lw=230)
    c.arrow([(xl, yrl + hrl * 0.22), (xg, yrl + hrl * 0.22)], "violet", sw=2.2, label="ticks, once per period",
            lpos=lm)
    c.arrow([(xl, yrl + hrl * 0.5), (xg, yrl + hrl * 0.5)], "green", sw=2.2, dash="7 5",
            label="a relayed fence or revocation", lpos=lm, lw=230)
    c.arrow([(xl, yrl + hrl * 0.8), (xg, yrl + hrl * 0.8)], "brown", sw=2.2, label="relayed: the act", lpos=lm)
    # governor <-> radio, governor -> actuators
    c.arrow([(g_x + g_w, yra + hra / 2), (r_x, yra + hra / 2)], "teal", sw=2.4, both=True, label="holds", lpos=0.5)
    yacm = yac + min(hac / 2, 70)
    c.arrow([(g_x + g_w, yacm), (r_x, yacm)], "teal", sw=2.8, label="permits each `local` entry: no round",
            lpos=0.5, lw=120)
    # the stack asks the governor
    sx = g_x + 150 + (g_w - 150) / 2
    c.arrow([(sx, ysk), (sx, ygv + hgv)], "red", sw=2.2, label="asks for an entry", lpos=0.5)
    # D-0062-1: a path that is not the governor
    ysm = ysk + hsk / 2
    dx = r_x + r_w / 2
    c.arrow([(g_x + g_w, ysm), (dx, ysm), (dx, yac + hac)], "red", sw=2.0, dash="3 4",
            label="D-0062-1: a path not through the governor", lpos=0.35, lw=190)
    # going alone
    ax_ = g_x + 70
    c.arrow([(ax_, ygv + hgv), (ax_, row3)], "red", sw=2.4, dash="7 5", label="ticks overdue by its own clock: "
            "the lease ends at once", lpos=0.5, lw=120)

    # postures (ADR-0060 §5) under the two planes; the degeneracy under the vehicle
    y = max(a_bot, b_bot) + 40
    c.text(X0, y + 16, "**Postures** (ADR-0060 §5). A5 says unattended operation is something \"the pattern does "
           "not model\".", 15, "ink")
    y += 26
    c.text(X0, y + 16, "**Nothing a cut-off plane does may rest on a person's response**; what bounds it is ADR-0063.",
           15, "ink")
    y += 34
    pw_ = RB_x + RB_w - X0
    hp = row_cards(c, X0, y, pw_, 24, [
        ("HITL: an irreversible effect", ["A person at a release seat admits each one, **and needs the link** "
                                          "(ADR-0066)."], "brown", {}),
        ("HOTL: a reversible effect, in contact", ["While the plane is in contact with the intent boundary. **Nobody "
                                                   "there sees the individual act**: the envelope is what was "
                                                   "authorized (Consequences)."], "blue", {}),
        ("Unattended: a reversible effect, out of contact", ["When the plane is not in contact. **Operation with no "
                                                             "person seated** is reported upstream (§6)."], "red",
         {"tint": False}),
    ], size=14)
    yl_ = y + hp + 20
    yl_ += c.legend(X0, yl_, [
        ("arrow", "violet", "a quorum; the plane's rounds"),
        ("arrow", "brown", "a person acts"),
        ("arrow", "amber", "an intent (Proposed)"),
        ("arrow", "teal", "the mechanism: grant, permit, record"),
        ("arrow", "green", "only subtracts", "7 5"),
        ("arrow", "red", "the stack; going alone", "7 5"),
        ("arrow", "red", "a degeneracy", "3 4"),
    ], maxw=pw_)
    yd = c_bot + 40
    hd = c.card(RC_x, yd, RC_w, "D-0062-1 (ADR-0062 §9)", [
        "**A stack that reaches an actuator or the radio by a path that is not the governor.** The stack is "
        "`Mediated`, and **every property in ADR-0062 to ADR-0066 is void for that vehicle**. This is A1 for a "
        "vehicle.",
    ], accent="red", size=14, tint=False, dash="6 4")
    y = max(yl_, yd + hd)
    y += 80

    # ================================================================== band 2: ADR-0060
    y = band(c, X0, y, "ADR-0060: every effect is admitted at the intent boundary, and an autonomous plane has no path "
             "that changes authority", status="proposed", extra="C1, C2 · R1")
    top = y
    g = 50
    wl = 1700
    wr = WW - wl - g
    xr = X0 + wl + g
    y = top + sub(c, X0, top, "**§1's table, whole** ⟨10⟩")
    cols = [("Effect", 170, {"bold": True}), ("What is admitted at the intent boundary", 560), ("By whom", 380),
            ("What happens below", wl - 170 - 560 - 380)]
    y += c.table(X0, y, cols, [
        {"cells": ["Reversible", "An **intent**: a task, an envelope, a budget of activations and an expiry",
                   "The commander, an operator", "The autonomous plane grants each lease inside the intent "
                   "(ADR-0062)"], "accent": "amber"},
        {"cells": ["Irreversible", "The effect itself, one at a time", "A person at a release seat (ADR-0066)",
                   "The plane relays it. It can refuse one and cannot originate one"], "accent": "brown"},
    ], size=14.5, accent="amber") + 22
    hh = row_cards(c, X0, y, wl, 24, [
        ("ADR-0015's sentence, one level up", [
            "\"Every effect therefore has a consensus-ordered, signed, authorizing predecessor\" (ToO §4.1). **Here the "
            "predecessor is the intent, ordered at a commanded plane.**",
            "**What is admitted for a reversible effect is an envelope, and not the act.**",
        ], "blue", {"tint": False}),
        ("Ordered before the effect, and need not be live at it ⟨R1⟩", [
            "An intent ended, revoked or fenced before its `expiry` **leaves a lease under it live until the news "
            "arrives**, so an effect can follow the intent's end.",
            "**ADR-0063 bounds how many.** `Intent.tla`'s witness `NeverEffectAfterIntentEnded` is violated: the case "
            "is reachable.",
        ], "amber", {}),
    ], size=14)
    y += hh + 30
    y += sub(c, X0, y, "**§2: an intent is a charter for one round, bounded by the promoted seating** ⟨Q4⟩")
    hh = row_cards(c, X0, y, wl, 24, [
        ("The first intent comes from a quorum", [
            "The mesh is promoted at the intent boundary with its seatings and its budget (ADR-0055), **and that tally "
            "grants the first charter**.",
        ], "violet", {}),
        ("Later intents come from one person", [
            "**ADR-0050's successor grant.** The request is an add, so it needs a live lease and a live peer.",
        ], "brown", {}),
        ("Every field the promoted seating's or narrower ⟨Q4⟩", [
            "ADR-0050 bounds a successor by the last lease. **Under that rule a commander who narrowed an intent for one "
            "phase could not restore the mission's bounds without a quorum, and would learn not to narrow.**",
        ], "amber", {}),
        ("An intent ends", [
            "At its `expiry`, when its budget is spent, when the commander ends or revokes it, or when any plane above "
            "is fenced (ADR-0059 §6).",
        ], "green", {}),
    ], size=14)
    bl = stack(c, X0, y + hh + 24, wl, [
        ("§6: reported upstream under ADR-0058 §6 ⟨Q11⟩", [
            "**Operation with no person seated**, and **a grant by one operator bounded by a seating and not by the "
            "last lease**.",
            "If the archetype takes them, its records owe: ADR-0050 (the successor bound for intents; **C3**), "
            "ADR-0054 (a person in an orchestrator seat), ADR-0037 (seat kinds), ADR-0055 (where a mesh runs), A5 and "
            "ToO §13 (a plane with nobody in reach).",
        ], "grey", {"tint": False}),
    ], size=14)
    # right column
    yy = top + sub(c, xr, top, "**§3's table, whole**: the autonomous plane is defined by one absence ⟨11⟩ ⟨Q2⟩ ⟨Q3⟩")
    cols = [("Absent", wr * 0.42, {}), ("Present", wr * 0.58)]
    yy += c.table(xr, yy, cols, [
        ["**Build**: no authoring and no promotion", "**The admit path**, for a grant and for an `ordered` entry "
         "(ADR-0062)"],
        ["**Grant seats, operators, release seats**: no person", "**The lease, the floor, every bundle on the chain, "
         "the fences**"],
        ["**Anchor issuance, new bundles, seating of planes**", "**The workflow interpreter**: a mesh, its activations "
         "and its budget"],
        ["**Any grant but one**", "**One grant:** a node's lease, made by the mechanism under a live intent, \"with "
         "every field the seating's or narrower\" (ToO §2.11)"],
        ["", "**Subtraction**: the end of a round, a revocation, an Observer's finding, expiry"],
        ["", "**A step of its charter's shrink schedule** (ADR-0061)"],
    ], size=14.5, accent="violet") + 18
    br = stack(c, xr, yy, wr, [
        ("§3, narrowed at R1: a claim about an honest plane's log", [
            "A captured plane is a havoc issuer (ADR-0059 §4): it can sign a lease under an intent that has ended, "
            "and its log is not evidence. **What bounds it is the chain check and ADR-0063.**",
        ], "red", {"tint": False}),
        ("§4: a declared degeneracy and an addition, not a second pattern ⟨Q2⟩", [
            "**A degenerate plane.** It omits Build, the people and Kafka. A deployment declares that under ADR-0058.",
            "**An addition.** Charters, commit certificates and operation with no person present are capabilities the "
            "archetype lacks. By ADR-0023 §4 **the archetype is incomplete, and the report is a finding about it** "
            "(§6).",
        ], "amber", {}),
        ("§5: missions are workflows, and a person may route at a commanded plane ⟨Q10⟩", [
            "**A DAG is a plan with branches**, promoted at a commanded plane (ADR-0054). A person in an orchestrator "
            "seat there chooses among edges the mechanism has already enabled.",
            "**A mesh is promoted at the intent boundary and runs at the autonomous plane** (ADR-0055). A node is one "
            "round of one cell, and the activation budget is the intent's.",
            "**\"Missions are promoted bundles\"**: one tally votes a mission's bundle revision, its mesh, and the "
            "charters and seatings it needs, together.",
        ], "blue", {"tint": False}),
    ], gap=18, size=14)
    y = max(bl, br) + 80

    # ================================================================== band 3: ADR-0062
    y = band(c, X0, y, "ADR-0062: the lease pre-authorizes, every entry declares an extent, and going alone ends the "
             "lease", status="proposed", extra="C1, C2 · R1")
    top = y
    wl = 1500
    wr = WW - wl - g
    xr = X0 + wl + g
    yl = top + sub(c, X0, top, "**§2's table, whole**: one round of the plane per lease, and none per entry ⟨21⟩ ⟨22⟩")
    cols = [("Waits for a round of the plane", wl / 2), ("Waits for none", wl / 2)]
    yl += c.table(X0, yl, cols, [
        ["A lease, once", "**A `local` entry under a live lease**"],
        ["An entry marked `ordered` (§3)", "A report to a peer topic (ADR-0065)"],
        ["A tick, once per period", "Listening, and applying a relayed fence or revocation"],
        ["A seal, a heartbeat, a finding or a revocation, for the record", "Any refusal"],
        ["A step of the shrink schedule", "Hold, and the terminal behaviour"],
    ], size=14.5, accent="teal") + 18
    yl = stack(c, X0, yl, wl, [
        (None, [
            "**The plane orders the grant**: the vehicle, the alphabet, the envelope, a **count** of entries and a `ttl` "
            "in ticks. **The governor then permits each entry** under the lease, against the floor, the bundles, the "
            "envelope and the count, with no further round. **The count is exact**: the governor's own arithmetic "
            "over its own acts.",
            "**An effect's ordered predecessors are the intent and the lease.** Two things still depend on the plane "
            "completing rounds: a lease is usable only while ticks are heard (§5), and a vehicle's next lease is a "
            "round. **Neither is on the path of a pre-authorized act.** `Alone.tla`'s `LocalNeverWaits` states it.",
        ], "teal", {"tint": False}),
    ], size=14)
    yr = top + sub(c, xr, top, "**§3's table, whole**: the allowlist entry (ADR-0049) gains a sixth part, `effect` ⟨Q20⟩")
    cols = [("Field", wr * 0.36, {"bold": True}), ("Says", wr * 0.64)]
    yr += c.table(xr, yr, cols, [
        ["The class, with its `T_irrev`", "`reversible` or `irreversible` (ADR-0066)"],
        ["How it is permitted", "`local`, by the governor; or `ordered`, by the plane before the effect"],
        ["Its extent", "§4"],
        ["Whether it is the beacon", "§5. At most one entry per seat kind"],
    ], size=14.5, accent="teal") + 18
    yr = stack(c, xr, yr, wr, [
        ("The archetype marks no entry `ordered` ⟨Q20⟩", [
            "**The bundle marks an entry `ordered` where the tally wants agreement across vehicles**: a count that "
            "spans vehicles, an admit that can be void, an Observer checked at each act. That entry waits for a round.",
            "**The archetype marks none**, and the tally marks them per mission. **No irreversible entry is `local`.**",
        ], "amber", {}),
    ], size=14)
    y = max(yl, yr) + 40

    hh = row_cards(c, X0, y, WW, 24, [
        ("§4: every entry declares an extent ⟨18⟩ ⟨Q14⟩", [
            "**An extent says how far one entry runs**: one act; a number of ticks; or a distance or a region, which "
            "the governor measures.",
            "**An entry with no extent does not load**, as a bundle whose allowlist is not well-formed does not (ToO "
            "§2.10). Without one a count bounds nothing: one entry could run for ever.",
            "**When an extent ends and no entry follows, the governor holds** ⟨Q14⟩. Hold is fixed at seating; the "
            "stack does not choose it; the lease stays live.",
            "**An extent that is not a count of ticks is a measurement**, its position source a trust root (ADR-0068). "
            "**An extent is a declaration** (A15): one declared shorter than the act is seen by nothing here.",
        ], "teal", {}),
        ("§5: going alone ends the lease at once ⟨14⟩ ⟨22⟩ ⟨Q15⟩", [
            "**Alone**: it has not applied the plane's log up to a tick that, by its own clock, is not yet overdue "
            "(ADR-0064 §5).",
            "**The lease ends**: locally where it stands, then ordered when the plane learns of it.",
            "**Kept**: the terminal behaviour, listening, and a beacon within its count. **No actuation.**",
            "**The beacon is an effect** ⟨R1⟩, and may be sent after the lease ends, within its count.",
            "**Heard again**: it may be leased again under the same intent, charged to its budget ⟨Q15⟩.",
        ], "red", {"tint": False}),
        ("§6: the record, and what can be void", [
            "**Under a lease** the governor writes each entry it permits or refuses, and each report it sends or "
            "delivers, to a chain on the vehicle: hash-linked, signed with the vehicle's key, numbered by the "
            "per-lease sequence (ToO §4.2).",
            "**At the lease's end, the seal**: the governor closes the chain; the plane orders it as one entry and runs "
            "the mechanism checks at that position.",
            "**Void works only for an `ordered` entry** (ADR-0033 §4). **Nothing a governor permitted is void**: the "
            "effect has happened. A failed check at the seal or above is **a finding, and it can only subtract**.",
            "**A captured vehicle's chain is not evidence.** It says what its captor signed.",
        ], "teal", {"tint": False}),
        ("§7: an ending grants nothing", [
            "\"A timeout is never a grant\" (ADR-0024). A body in motion still has to do something when its lease "
            "ends.",
            "**A lease ends**: count spent and last extent run; at its `ttl`; ended or revoked by the plane; a fence; "
            "and at once when alone.",
            "**The terminal behaviour is part of the seating**: hold, return on a voted route, land or stop. The stack "
            "neither chooses it nor carries it out; a recovery function in the governor's trust domain does.",
            "**Each vehicle class declares a safe state**, and reaching it in bounded time is the builder's obligation.",
        ], "green", {}),
    ], size=14)
    y += hh + 40

    top = y
    wl = 1500
    wr = WW - wl - g
    xr = X0 + wl + g
    yl = stack(c, X0, top, wl, [
        ("§8: coupling moves to the grant ⟨Q9⟩", [
            "**`R3-observer-live` refuses `Actuate` under a `thinker` seat with no live cell Observer** (ADR-0041; as "
            "ADR-0062 §8 quotes it, ADR-0041 §2's row also names `Report`).",
            "**For an `ordered` entry it applies as written.**",
            "**For a `local` entry it applies at the grant.** A lease's count is at most `K`, and a vehicle's next "
            "lease is granted only once its cell Observer has read the last one to its seal (ADR-0039). So **at most "
            "`K` of a Thinker's effects are unread by its Observer at any moment**, the bound ADR-0039 states.",
            "**What is given up is the refusal in the middle of a lease.** `M_WAITOBSERVER` in `Alone.tla` is R3 kept "
            "mid-lease, and it breaks `LocalNeverWaits`.",
        ], "pink", {}),
    ], size=14)
    yr = top + sub(c, xr, top, "**§8's table, whole**: the mesh's promotion declares where each cell's Observer sits, "
                     "and the claim follows the declaration")
    cols = [("Declared", wr * 0.2, {"bold": True}), ("What it gives", wr * 0.3), ("What it costs", wr * 0.5)]
    yr += c.table(xr, yr, cols, [
        {"cells": ["On another vehicle", "No hardware shared with the Thinker it watches",
                   "The governors' radios carry the round's payloads to it, and **the loss of that vehicle holds up "
                   "the watched vehicle's next lease**"], "accent": "pink"},
        {"cells": ["On the same vehicle", "No dependence on a radio or on another vehicle",
                   "It shares hardware and fate with its Thinker, and **no claim rests on it**"], "accent": "red"},
    ], size=14.5, accent="pink") + 18
    yr = stack(c, xr, yr, wr, [
        ("§10: reported upstream under ADR-0058 §6 ⟨Q11⟩", [
            "**A trusted component that permits, away from the replicas**; and **an entry's extent**.",
            "If the archetype takes them, its records owe: ADR-0015's sentence on predecessors and ADR-0033 §4's void, "
            "each for a `local` entry, **which is C3**; ADR-0039 and ADR-0041, coupling at the grant; ADR-0049, the "
            "`effect` part; ADR-0031, a count in the lease and an ending when its holder stops hearing the mechanism; "
            "ADR-0034 A2, the radio as a declared channel.",
        ], "grey", {"tint": False}),
    ], size=14)
    y = max(yl, yr) + 80

    # ================================================================== band 4: the modules
    y = band(c, X0, y, "The modules: what each states, what breaks it, what it shows reachable, and what it leaves out "
             "(ADR-0060 §7; ADR-0062 §11)")
    top = y
    wl = (WW - g) / 2
    xr = X0 + wl + g

    def module_col(x, w, name, ident, pills, props, muts, wit_title, wits, abstr):
        yy = top
        c.text(x, yy + 18, name, 19, "teal", bold=True)
        yy += 30
        px = x
        for t in pills:
            pw = text_width(t, 11.5, True) + 18
            if px + pw > x + w:
                px = x
                yy += 30
            px += c.pill(px, yy, t, "teal", 11.5) + 8
        yy += 40
        cols = [("Property", w * 0.27, {"mono": True}), ("Says", w * 0.73)]
        yy += c.table(x, yy, cols, props, size=14, accent="teal") + 18
        cols = [("Mutation", w * 0.24, {"mono": True}), ("What it does", w * 0.46), ("Breaks (TLC)", w * 0.30)]
        yy += c.table(x, yy, cols, muts, size=14, accent="red") + 18
        yy = stack(c, x, yy, w, [
            (wit_title, wits, "violet", {"tint": False}),
            ("What is abstracted", abstr, "grey", {"tint": False}),
        ], gap=16, size=13.5)
        return yy

    bl = module_col(
        X0, wl, "`spec/Intent.tla` · ADR-0060 §7, with ADR-0062 §2's `EveryEffectHasALease`",
        "",
        ["Checked · 35 rows, all as expected", "677 obligations proved",
         "Certified, with 5 LS4 temporal steps that no checker confirms"],
        [
            ["EveryEffectHasAnIntent", "Every reversible effect has an intent **ordered at the commanded plane before "
             "it**, live when the effect's lease was granted (ADR-0060 §1)"],
            ["EveryEffectHasALease", "Every reversible effect has a lease ordered at its plane before it, **and is "
             "within that lease's count** (ADR-0062 §2)"],
            ["IntentNarrows", "Every intent is **within the promoted seating**, and not merely within the last intent "
             "(§2)"],
            ["AutonomousAddsNothing", "The autonomous plane's log holds **no promotion, seating, issuance, bundle "
             "change or operator's grant**, and no change of membership off its schedule (§3)"],
        ],
        [
            ["M_NOINTENT", "The autonomous plane grants a lease with no live intent", "`EveryEffectHasAnIntent` only"],
            ["M_NOCOUNT", "The governor does not count", "`EveryEffectHasALease` only"],
            ["M_WIDEINTENT", "A successor widens the envelope past the seating", "`IntentNarrows` only"],
            {"cells": ["M_LASTINTENT", "ADR-0050's rule, which ⟨Q4⟩ declined: a successor is bounded by the last "
                       "intent. Added at R1", "**No property.** The witness `NeverRestored` holds: **a commander who "
                       "narrows cannot restore**, which is ⟨Q4⟩'s reason"], "accent": "amber"},
            ["M_LITEPROMOTES", "The autonomous plane orders a promotion", "`AutonomousAddsNothing` only"],
        ],
        "Witnesses: each must be violated, so each is reachable (14 rows)",
        [
            "**An intent is ordered** (`NeverOrdered`), **a later one** (`NeverSuccessor`), and **a narrowed intent "
            "restored to the seating's bounds** (`NeverRestored`); **a widening refused** (`NeverRefusedWide`).",
            "**A lease** (`NeverLeased`), **an effect** (`NeverEffect`), **a count spent** (`NeverCountSpent`), **a "
            "re-lease under the same intent** ⟨Q15⟩ (`NeverReletSameIntent`, at `SeatingBudget=2`).",
            "**Refusals**: at the count, with no live intent, with the budget spent, and of an act that changes "
            "authority (`NeverRefusedAtCount`, `NeverRefusedNoIntent`, `NeverRefusedBudget`, `NeverRefusedAuthority`); "
            "**a scheduled membership step** is taken (`NeverScheduleStep`).",
            "`NeverEffectAfterIntentEnded` [[red|is violated]] ⟨R1⟩: **an effect can follow its intent's end**, since a "
            "lease may outlive its intent. That is the case ADR-0063 bounds, and why §1's predecessor is ordered before "
            "the effect, not live at it.",
        ],
        [
            "**The plane is honest.** \"Live when its lease was granted\" and §3 are claims about an honest plane; a "
            "captured one is bounded by `Federation.tla`'s chain check and `Outstanding.tla`.",
            "**Every effect is reversible**: the irreversible one is `Release.tla`'s. **Time is nondeterminism**: "
            "`EndIntent` stands for expiry, revocation and a fence alike. An intent has two fields, `envelope` "
            "(narrowed by subset) and `budget` (by ≤); `expiry` and `task` have their shape and are not repeated.",
            "**ADR-0050's live lease and live peer are not modelled.** A lease's fields but its count are within the "
            "intent by `Federation.tla`'s `LeaseWithinChain`. The membership schedule's rule is `Membership.tla`'s.",
            "**Constants**: one vehicle, `SeatingBudget=1`, `MaxRound=2`, `MaxLease=2`, `MaxCount=1`, `MaxEffects=2`; "
            "`Safe` also at two vehicles and at budget 2. **Proof**: assumes `SeatingBudget` and `MaxCount` in `Nat`; "
            "444 obligations trivial, 228 SMT with proofs ethos accepted, 5 LS4.",
        ])
    br = module_col(
        xr, wl, "`spec/Alone.tla` · ADR-0062 §5, §7, and §11's invariants over `ENABLED`",
        "",
        ["Checked · 47 rows, all as expected", "263 obligations proved",
         "Certified, with 6 LS4 temporal steps that no checker confirms"],
        [
            ["AlonePermitsNothing", "A governor whose vehicle is alone **permits nothing but the beacon, and the beacon "
             "within its count** (§5)"],
            ["ExpiryGrantsNothing", "After a lease ends **no entry is permitted**, and the only terminal act is hold or "
             "the seating's terminal behaviour, **which the stack does not select** (§7)"],
            {"cells": ["LocalNeverWaits", "**Invariant over `ENABLED`**: while a lease is live and its vehicle hears its "
                       "plane, a `local` entry within its count **can be permitted, whatever the plane's primary, any "
                       "other vehicle or any Observer is doing** (§11; ⟨21⟩ as a property)"], "accent": "teal"},
            {"cells": ["TerminalNeverWaits", "**Invariant over `ENABLED`**: with a lease ended, **the terminal behaviour "
                       "is enabled whatever the stack does**. The custodian's decision of 2026.11.10"],
             "accent": "teal"},
        ],
        [
            ["M_ALONEACTS", "Going alone does not end the lease, so the vehicle goes on permitting within its count",
             "`AlonePermitsNothing` only"],
            ["M_BEACONUNCOUNTED", "The beacon's count is one higher than declared", "`AlonePermitsNothing` only"],
            ["M_STACKCHOOSES", "The stack selects the terminal act", "`ExpiryGrantsNothing` only"],
            ["M_ENTRYAFTEREND", "An entry is permitted under an ended lease", "`ExpiryGrantsNothing` and "
             "`AlonePermitsNothing` (going alone is one way a lease ends)"],
            ["M_WAITPRIMARY", "A `local` permit waits for the primary", "`LocalNeverWaits` only"],
            ["M_WAITPEER", "A `local` permit waits for another vehicle", "`LocalNeverWaits` only"],
            ["M_WAITOBSERVER", "A `local` permit waits for a live Observer: R3 kept mid-lease, which §8 moves to the "
             "grant", "`LocalNeverWaits` only"],
            ["M_STACKGATED", "The terminal behaviour waits for the stack", "`TerminalNeverWaits` only"],
        ],
        "Witnesses: each must be violated, so each is reachable (9 rows)",
        [
            "**A `local` entry permitted** (`NeverLocalPermitted`) and **an `ordered` one** (`NeverOrderedPermitted`).",
            "**A vehicle alone** (`NeverAlone`), **a lease ended by going alone** (`NeverEndedByAlone`), **a beacon** "
            "(`NeverBeacon`), **a terminal act carried out** (`NeverRecovered`), **a fence applied while alone** "
            "(`NeverFenceWhileAlone`, at `MaxFence=1`), **a lease again after alone** (`NeverLeasedAfterAlone`, at "
            "`MaxGrant=2`).",
            "**An `ordered` entry does wait on the primary** (`NeverOrderedWaits`): the contrast `LocalNeverWaits` "
            "draws. What shows the two `ENABLED` invariants state the claim is the mutations that break them, which no "
            "other row sees.",
            "**The module's finding**, settled by R1: the proposal's \"the only effects are hold and the seating's "
            "terminal behaviour\" and §5's beacon cannot both be read literally. `ExpiryGrantsNothing` is stated of "
            "entries and terminal acts, and the beacon is bounded in `AlonePermitsNothing`.",
        ],
        [
            "**One vehicle, one governor, one stack.** \"Hears its plane\" is the flag `hears`, and `GoAlone` is free: "
            "overdue is read off the governor's clock, which is `PlaneClock.tla`'s, with its residual. A stalled "
            "primary reaches the governor as `GoAlone`, never as a wait on a permit.",
            "**`alphabet` membership** stands for everything static a permit reads (envelope, floor, bundles): a "
            "refusal is not a wait. The count is the constant `Count`; one `local` entry `l1` and one `ordered` `o1`.",
            "**`EndLease`** stands for every ending in §7 but going alone and a fence. What a fence fences on a chain is "
            "`Federation.tla`'s; **hold while the lease stays live, when an extent ends, is deferred to "
            "`PlaneClock.tla`**; peer reports are `Peer.tla`'s; **reaching a safe state is physics**.",
            "**Constants**: `Count=1`, `MaxBeacon=1`, `MaxGrant=1`, `MaxFence=0`, `Seated=\"return\"`; `Safe` also at "
            "`Count=2`, `MaxGrant=2`, `MaxFence=1`. **Proof**: 173 obligations trivial, 78 SMT with proofs ethos "
            "accepted, 6 Isabelle, 6 LS4.",
        ])
    y = max(bl, br) + 40
    y += sub(c, X0, y, "**ADR-0062 §11 as revised: its module item is met across four modules.** `EveryEffectHasALease` "
                       "and `M_NOCOUNT` are `Intent.tla`'s (above); `EntryEndsAtExtent` and `ConflictIsAFinding`, with three "
                       "mutations, live in two others, each drawn in full with its own record")
    hh = row_cards(c, X0, y, WW, 24, [
        ("`spec/PlaneClock.tla` (ADR-0064 §8): `EntryEndsAtExtent`, `M_NOEXTENT`, `M_NOWATCHDOG`", [
            "**`EntryEndsAtExtent`**: a running entry is short of its extent and of the largest extent an entry may "
            "declare, counted in ticks applied, **and its governor's own clock has not passed the next tick's due "
            "time** (ADR-0062 §4, ADR-0064 §5).",
            "**`M_NOEXTENT`**, an entry with no extent loads: breaks `EntryEndsAtExtent`. **`M_NOWATCHDOG`**, an "
            "overdue tick ends nothing: breaks `EntryEndsAtExtent` and `NoStretchUnlessSlow`.",
            "**The residual**: overdue is by the governor's own clock, so a slow governor clock can stretch an entry in "
            "real time, and only when the plane's ticks have also stopped reaching it (witness `NeverStretched`).",
            "Checked · 38 rows, all as expected · proved · 535 obligations · certified, with 6 LS4 temporal steps that "
            "no checker confirms.",
        ], "teal", {"tint": False}),
        ("`spec/Release.tla` (ADR-0066 §7): `ConflictIsAFinding`, `M_VOID`", [
            "**`ConflictIsAFinding`**: a check failing at a seal or above **subtracts, and voids nothing a governor "
            "permitted** (ADR-0062 §6 as a property; the custodian's decision of 2026.11.10).",
            "**`M_VOID`**, a failed check voids an effect that happened: breaks `ConflictIsAFinding`, and only it.",
            "**Not modelled there**: a void before the effect, which §6 allows of an `ordered` entry; every check in "
            "that module fails after the effect.",
            "Checked · 67 rows, all as expected · proved · 613 obligations · certified, with 10 LS4 temporal steps "
            "that no checker confirms.",
        ], "teal", {"tint": False}),
        ("Where §4's hold ⟨Q14⟩ is, and is not, stated", [
            "**No module header names hold as a property.** `Alone.tla` defers \"hold while the lease stays live, when "
            "an extent ends\" to `PlaneClock.tla`.",
            "`PlaneClock.tla`'s `EntryEndsAtExtent` says the entry stops at its extent (\"an entry at its extent "
            "ends\"); what the governor does next, hold with the lease live, is not among its properties.",
            "`ExpiryGrantsNothing` and `TerminalNeverWaits` cover hold only as a terminal act, after a lease has "
            "ended.",
        ], "red", {"tint": False}),
    ], size=14)
    y += hh + 80

    # ================================================================== band 5: ratification, options, consequences
    y = band(c, X0, y, "Ratification conditions, item by item; the Options tables, whole; and the Consequences")
    top = y
    wl = (WW - g) / 2
    xr = X0 + wl + g

    def rat(x, w, title, rows):
        yy = top + sub(c, x, top, title)
        cols = [("Condition item", w * 0.68), ("State", w * 0.32)]
        return yy + c.table(x, yy, cols, rows, size=14, accent="blue")

    bl = rat(X0, wl, "**ADR-0060 §7**: ratification condition", [
        {"cells": ["**ADR-0059 is ratified first**, or with this record. **ADR-0050 is no longer provisional**, and "
                   "**ADR-0054 and ADR-0055 are ratified**", NOT + ": ADR-0059, ADR-0054, ADR-0055 Proposed; ADR-0050 "
                   "provisional"], "accent": "red"},
        {"cells": ["**A module** states at least `EveryEffectHasAnIntent`, `IntentNarrows` and `AutonomousAddsNothing`, "
                   "with `M_NOINTENT`, `M_WIDEINTENT` and `M_LITEPROMOTES`. `M_LASTINTENT` added",
                   MET + ": `spec/Intent.tla`, 35 rows; 677 obligations"], "accent": "green"},
        {"cells": ["**The floor** carries `FD4-autonomous-adds-nothing` (ADR-0067)",
                   NOT + ": the `federation` stage is not written"], "accent": "red"},
        {"cells": ["**The reference** shows an intent granted by one operator inside a seating, a widening refused, and "
                   "a promotion refused at an autonomous plane", NOT + ": not built"], "accent": "red"},
        {"cells": ["**A reader who is not the drafter** (ADR-0029 A2)", NOT + ": one author, one day"],
         "accent": "red"},
    ])
    br = rat(xr, wl, "**ADR-0062 §11**: ratification condition", [
        {"cells": ["**ADR-0059 to ADR-0061, and ADR-0064, are ratified first**, or with this record",
                   NOT + ": all four Proposed"], "accent": "red"},
        {"cells": ["**A module** states at least `EveryEffectHasALease`, `AlonePermitsNothing`, `ExpiryGrantsNothing` "
                   "and `EntryEndsAtExtent`, with `M_NOCOUNT`, `M_ALONEACTS`, `M_STACKCHOOSES`, `M_NOEXTENT` and "
                   "`M_NOWATCHDOG`, and one invariant over `ENABLED` (⟨21⟩). Two more by the custodian's decision: "
                   "`TerminalNeverWaits`; `ConflictIsAFinding` with `M_VOID`",
                   MET + ", across four modules: `Alone.tla`, `Intent.tla`, `PlaneClock.tla`, `Release.tla`"],
         "accent": "green"},
        {"cells": ["**The floor** carries `FD7`, `FD8`, `FD11` and `FD14` (ADR-0067)",
                   NOT + ": the `federation` stage is not written"], "accent": "red"},
        {"cells": ["**The reference** shows a lease spent to its count with no round between; an entry with no extent "
                   "refused at load; a lease ended on a missed tick; and a failed check at a seal recorded as a "
                   "finding", NOT + ": not built"], "accent": "red"},
        {"cells": ["**A reader who is not the drafter** (ADR-0029 A2)", NOT + ": one author, one day"],
         "accent": "red"},
    ])
    y = max(bl, br) + 22
    hh = row_cards(c, X0, y, WW, 20, [
        ("`FD4-autonomous-adds-nothing` · forbid", ["At an autonomous plane: no promotion, no seating, no operator's "
                                                     "request, no bundle change, no grant but a node's lease under a "
                                                     "live intent, and no change of membership but a step of its "
                                                     "charter's schedule (ADR-0060 §3)."], "red",
         {"tint": False, "dash": "2 3"}),
        ("`FD7-local-marked` · forbid", ["No permit by a governor of an entry its bundle revision does not mark "
                                         "`local`, and none of an irreversible entry (ADR-0062 §3)."], "red",
         {"tint": False, "dash": "2 3"}),
        ("`FD8-local-bounds` · forbid", ["No permit by a governor with the lease's count spent, past its `ttl` in "
                                         "ticks, or under a lease that has ended (ADR-0062 §2, §7)."], "red",
         {"tint": False, "dash": "2 3"}),
        ("`FD11-alone-permits-nothing` · forbid", ["No permit by a governor whose vehicle is alone, but the beacon "
                                                   "within its count (ADR-0062 §5)."], "red",
         {"tint": False, "dash": "2 3"}),
        ("`FD14-count-within-K` · forbid", ["No lease whose count exceeds `K`, or its charter's `countMax` (ADR-0062 "
                                            "§8)."], "red", {"tint": False, "dash": "2 3"}),
    ], size=13.5)
    y += hh + 12
    y += c.para(X0, y, WW, "The five floor entries the two conditions name, as ADR-0067 §3's table states them: "
                "**not written**. The `federation` stage would follow `workflow` in `floor/proposed/README.md`.", 14,
                "muted") + 40

    top = y
    yl = top + sub(c, X0, top, "**ADR-0060's Options considered, whole**")
    cols = [("Option", wl * 0.38, {"bold": True}), ("Disposition", wl * 0.62)]
    yl += c.table(X0, yl, cols, [
        {"cells": ["A person on every plane", "**The corpus as it stands.** A group that loses its link then has "
                   "nobody to act"], "accent": "grey"},
        {"cells": ["Each act admitted at the intent boundary", "[[grey|Not taken.]] It is HITL for every act, and "
                   "stops with the link"], "accent": "grey"},
        {"cells": ["An intent bounded by the last intent, as ADR-0050 has a successor", "[[grey|Not taken]] ⟨Q4⟩"],
         "accent": "grey"},
        {"cells": ["Every intent by quorum", "[[grey|Not taken]] (ADR-0059 ⟨Q1⟩)"], "accent": "grey"},
        {"cells": ["\"Lite\" as a second, named profile", "[[red|Rejected]] ⟨Q2⟩. It is the ladder ADR-0023 refuses"],
         "accent": "red"},
        {"cells": ["Replicas on relay nodes only", "[[grey|Not taken]] ⟨Q3⟩. The plane would be as exposed as its "
                   "relays, and vehicles would be its clients"], "accent": "grey"},
        {"cells": ["Agents only in orchestrator seats", "[[grey|Not taken]] ⟨Q10⟩"], "accent": "grey"},
    ], size=14, accent="grey") + 22
    yl = stack(c, X0, yl, wl, [
        ("ADR-0060 Consequences: positive", [
            "**Tempo.** Between votes, one commander issues the next intent.",
            "**Narrowing is not a one-way door**, so commanders can narrow.",
            "**A plane with no person cannot add authority**, by having no path for it.",
        ], "green", {}),
        ("ADR-0060 Consequences: negative", [
            "**Nobody at the intent boundary sees the individual act.** The envelope is what was authorized.",
            "**Unattended operation**, which the corpus had left unmodelled.",
            "**It rests on three records that are not settled**: ADR-0050, ADR-0054 and ADR-0055.",
            "**One author, one day.**",
        ], "red", {"tint": False}),
        ("ADR-0060 Open obligations", [
            "**The floor entry and the reference** (§7). **The custodian's reading of every drafter's choice.**",
            "**Where an autonomous plane's orchestrator runs**, which the NATO reading asks under N3.",
            "**Narrative**: \"intent boundary\", \"intent\", \"commanded plane\", \"autonomous plane\".",
        ], "red", {"tint": False, "status": "open"}),
    ], gap=18, size=14)

    yr = top + sub(c, xr, top, "**ADR-0062's Options considered, whole**")
    cols = [("Option", wl * 0.38, {"bold": True}), ("Disposition", wl * 0.62)]
    yr += c.table(xr, yr, cols, [
        {"cells": ["An ordered admit per entry", "[[grey|Not taken]] ⟨22⟩. It keeps void and coupling at each act, "
                   "and makes a round of the plane the tempo of every vehicle"], "accent": "grey"},
        {"cells": ["A lease usable when alone", "[[grey|Not taken]] ⟨22⟩. Its duration would rest on one clock again, "
                   "and nothing could reach it"], "accent": "grey"},
        {"cells": ["An alone alphabet with actuation entries, the first revision's `disconnected` mark",
                   "[[grey|Not taken]] ⟨14⟩"], "accent": "grey"},
        {"cells": ["A fixed class of `ordered` entries at the archetype", "[[grey|Not taken]] ⟨Q20⟩"],
         "accent": "grey"},
        {"cells": ["End the lease when an extent ends with no successor", "[[grey|Not taken]] ⟨Q14⟩. The governor "
                   "holds"], "accent": "grey"},
        {"cells": ["A vehicle that was alone stays out until the plane is linked", "[[grey|Not taken]] ⟨Q15⟩"],
         "accent": "grey"},
        {"cells": ["An Observer always on another vehicle", "[[grey|Not taken]] ⟨Q9⟩. It is declared per mission"],
         "accent": "grey"},
        {"cells": ["A governor checking `R3` at each act, against the marks in the plane's log", "[[grey|Not taken.]] "
                   "A Thinker would wait on its Observer's heartbeat, which is a round of the plane, on the path of a "
                   "pre-authorized act"], "accent": "grey"},
        {"cells": ["The radio on the stack's side", "[[red|Rejected.]] The stack would decide when its vehicle is "
                   "alone"], "accent": "red"},
    ], size=14, accent="grey") + 22
    yr = stack(c, xr, yr, wl, [
        ("ADR-0062 Consequences: positive", [
            "**A pre-authorized act waits for no round.**",
            "**The count is exact**, so what a lease can do is bounded with no clock (ADR-0063).",
            "**Being alone gains a stack nothing.**",
            "**The grain of an entry is stated**, which the swarm reading's Z1 asked for.",
        ], "green", {}),
        ("ADR-0062 Consequences: negative", [
            "**No ordered admit before every effect.** Nothing a governor permitted can be voided, and no Observer is "
            "checked in the middle of a lease.",
            "**Any act by a vehicle that is alone is given up.** An adversary that cuts one vehicle from its plane gets "
            "its terminal behaviour within a tick period.",
            "**The trusted base grows on every vehicle**, and it now makes every `local` permit.",
            "**An Observer on the same vehicle supports no claim**, and one on another vehicle can stall its Thinker "
            "by vanishing (the swarm reading, Z4).",
            "**One author, one day.**",
        ], "red", {"tint": False}),
        ("ADR-0062 Open obligations", [
            "**The floor entries and the reference** (§11).",
            "**An Observer that accuses or vanishes**, and whether a seating may name an alternate (Z4).",
            "**Values** for a lease's count and for the beacon's count, as placeholders first. **What hold is, per "
            "vehicle class**, which is the builder's.",
        ], "red", {"tint": False, "status": "open"}),
    ], gap=18, size=14)
    c.ymax = max(c.ymax, yl, yr)
    return c
