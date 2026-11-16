"""C11 — An irreversible effect is a person's (ADR-0066, Proposed, revised R1). A `release` seat at a commanded plane,
one act per effect, checked by the vehicle's interlock and fresh by the plane's ticks; and the `Release` module that
checks and proves it."""
from lib import Canvas, STATUS, STATE_CC, text_width

ID, SLUG = "C11", "release-seat"

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


def build():
    c = Canvas(ID, "An irreversible effect is a person's: a `release` seat at a commanded plane, one act per effect, "
               "checked by the vehicle's interlock and fresh by the plane's ticks",
               "ADR-0032 §4 says an effect irreversible on emission **must not be reachable from the alphabet at all**, "
               "because no budget `W + L + D < T_irrev` fits it. ADR-0066 makes it reachable by a person and by nobody "
               "else: **an entry declares its effect class, and only a `release` seat, held by a person at a commanded "
               "plane, reaches an irreversible entry**. Each act is one admit, ordered at the commanded plane, relayed "
               "by the autonomous plane, and fired by the vehicle's governor only if its interlock passes. **ADR-0066 "
               "is Proposed, an overlay and not the archetype, and revised R1 on 2026.11.10.** Its module `Release` is "
               "checked and proved. Its floor entries are not written, the reference is not built, and nothing here "
               "is in force.",
               W, "ADR-0066 (provenance; Status note; Context; Decision §1–§7; Options, whole; Consequences; Open "
               "obligations; History, R1); ADR-0032 §4 (its table, whole; A10); ADR-0052 §1, §2, §4, §5 (provisional, "
               "B34) and D5 for how the family draws it; ADR-0059 §1 (the charter's `release` field), §5; ADR-0060 §1, "
               "§3; ADR-0062 §3 (its table, whole), §6; ADR-0064 §3, §5; ADR-0067 §3 (`FD5`, `FD6`, `FD9`), §4 (`B10`); "
               "ADR-0013; ADR-0058 §6; ADR-0029 A2; glossary (HITL / HOTL / HOOTL); ToO rev 15 §3.3, §10, A5; "
               "spec/Release.tla (header; the interlock, `Fire`, `RefuseAct`, the properties and witnesses; sha256 "
               "7a8a212d3f07956b); spec/Release-rows.txt; spec/Release-results-2026.11.10.txt; "
               "spec/Release-proof-results-2026.11.10.txt; spec/Release-proof-cert-results-2026.11.10.txt",
               state=STATE_CC)
    X0, X1 = c.x0, c.x1
    WW = X1 - X0
    y = c.y

    # ================================================================== status strip
    c.text(X0, y + 15, "Status", 15, "faint", bold=True)
    px0 = X0 + 80
    px = px0
    strip = [
        ("ADR-0066", ("status", "proposed", "C1 · 2026.11.10, revised R1")),
        ("its activation rests on ADR-0052", ("status", "provisional", "B34 · so ADR-0066 is provisional while it is")),
        ("C3", ("pill", "On admission only, not as an overlay ⟨Q11⟩", "grey", None)),
        ("deployment position", ("pill", "An overlay, not the archetype ⟨Q11⟩", "grey", None)),
        ("`Release`, TLC", ("pill", "Checked · 67 rows, all as expected", "violet", None)),
        ("`Release_proof`, TLAPS", ("pill", "Proved · 613 obligations", "violet", None)),
        ("", ("pill", "Certified, with 10 LS4 temporal steps that no checker confirms", "violet", None)),
        ("`FD5`, `FD6`, `FD9` (`federation` stage)", ("pill", "Not written", "red", "2 3")),
        ("the reference", ("status", "notbuilt", "")),
    ]
    for lab, spec in strip:
        lw = (text_width(lab, 13.5, True) + 8) if lab else 0
        if spec[0] == "status":
            pw = text_width(STATUS[spec[1]][0] + (f" · {spec[2]}" if spec[2] else ""), 11.5, True) + 18
        else:
            pw = text_width(spec[1], 11.5, True) + 18
        if px + lw + pw > X1:
            px = px0
            y += 34
        if lab:
            c.text(px, y + 15, lab, 13.5, "ink", bold=True)
        px += lw
        if spec[0] == "status":
            px += c.status(px, y, spec[1], spec[2]) + 26
        else:
            px += c.pill(px, y, spec[1], spec[2], 11.5, dash=spec[3]) + 26
    y += 42
    y += c.para(X0, y, WW, "**Proposed means nothing here is in force.** The custodian decided that irreversible effects "
                "are human ⟨4⟩, that the person acts and does not countersign ⟨Q5⟩, that `release` is a new seat kind "
                "activated as an emergency seating is ⟨Q6⟩, that freshness is a named tick and a declared number of "
                "ticks ⟨Q16⟩, and that this is an overlay ⟨Q11⟩. Every other choice is the drafter's. **C1** applies "
                "because a release act is a privileged path, as break-glass is. **C3** would apply on admission, because "
                "§1 relaxes ADR-0032 §4. **R1** (2026.11.10) took the module's findings: the interlock checks the "
                "vehicle, \"aged\" is a count of ticks, and a cut link stops the order and not an act already across "
                "it. One author, one day.", 14.5, "muted") + 34

    # ================================================================== band 1: the path of one act
    y = band(c, X0, y, "The path of one act: a person signs it, a commanded plane orders it, the autonomous plane "
             "relays it, the governor's interlock fires it or refuses it (§2–§4)", status="proposed",
             extra="nothing here is built")
    ftop = y + 40
    S = 13.5
    gaps = [130, 120, 150, 130, 110]
    cw = [370, 340, 440, 440, 500]
    cw.append(WW - sum(cw) - sum(gaps))
    cx = [X0]
    for w_, g_ in zip(cw[:-1], gaps):
        cx.append(cx[-1] + w_ + g_)

    def mh(spec, w_, **k):
        return c.card(0, 0, w_, spec[0], spec[1], draw=False, size=S, **k)

    ROST = ("A roster's quorum (§2 ⟨Q6⟩)", [
        "**Activates the seat for one named person and one round**, as an emergency seating is activated (ADR-0052 "
        "§2, provisional).",
        "**The roster is anchor-issued** (ADR-0013), so no plane below the root can mint a person.",
    ], "brown")
    PERS = ("The person at a `release` seat (§2, §3)", [
        "**Holds a key, and nobody else holds the seat in the round.** No model's Persona binds to the kind.",
        "**The person is the actor ⟨Q5⟩**: composes and signs the act.",
        "Alphabet: `Actuate` on irreversible entries in its envelope, and `Report`.",
    ], "brown")
    REP = ("A stack's `Report` (§3)", [
        "A stack may report what it perceives.",
        "**Ingress to the person, labelled `untrusted`. It enables nothing.** An agent that proposes for a person to "
        "approve would put its output on the path to the effect.",
    ], "grey")
    ACT = ("The act: one admit, one effect (§4)", [
        "**Names** the entry, its inputs, **the vehicle**, the fences, and **a tick of the vehicle's plane** "
        "(ADR-0064).",
        "Signed with the person's key.",
        "It does not say why: the reason is unknown to the mechanism, by construction (§5).",
    ], "brown")
    SEAT = ("Seated at a commanded plane only (§2)", [
        "**Only where the charter carries `release`** (ADR-0059 §1: whether a release seat may be seated at this "
        "plane).",
        "**Never at an autonomous plane**: one with no people has nobody to seat (Options).",
        "`FD9` would refuse a key not on the roster, a seating at an autonomous plane, and one where the charter lacks "
        "`release` (ADR-0067). [[red|Not written.]]",
    ], "blue")
    ORD = ("Ordered at the commanded plane (§4)", [
        "**At the intent boundary**, the last commanded plane above the vehicles, where every effect's authorizing "
        "admit is ordered (ADR-0060 §1).",
        "**Delivered with that plane's commit certificate** (ADR-0059 §5).",
        "**Ordered only while the plane is in contact with the intent boundary** ⟨R1⟩. With no link, no act is "
        "ordered: `OrderedInContact`.",
    ], "violet")
    AGT = ("An agent's signed act (`AdmitAgent`)", [
        "**The module lets it be ordered.** `FD5` would refuse it (no `Actuate` of an irreversible entry under a seat "
        "whose kind is not `release`) and is not assumed.",
        "The governor refuses it **at the key**.",
    ], "red")
    TICK = ("The plane's ticks (ADR-0064 §3)", [
        "Each signed by a quorum of replicas. **Every interval is a number of ticks from a named tick**, a release act's "
        "freshness among them.",
        "**Ticks are not a clock**: freshness is a comparison of tick numbers (`Release`'s header).",
    ], "violet")
    RELAY = ("Relayed by the autonomous plane (§4)", [
        "**It relays the act. It can refuse one, and it cannot originate one** (ADR-0060 §1).",
        "A refused relay is an act that never fires.",
    ], "violet")
    ORIG = ("A captured plane originates an act (`LiteOriginate`)", [
        "**Over any signature it holds**, with its own certificate, to either vehicle. It needs no relay: it is the "
        "relay.",
        "The governor refuses it **at the certificate**: only the commanded plane's counts.",
    ], "red")
    CUT = ("R1 ③  A cut link stops the order, not an act already across it (§4)", [
        "An act that crossed the link before it was cut **is still delivered and can still fire inside its "
        "freshness**. **A governor cannot tell that the link is cut.**",
        "The witness **`NeverFiredAfterCut` is violated**: a fire with the link cut is reachable. What bounds it is "
        "freshness.",
        "**With no link no irreversible effect can be ordered**, and an adversary who jams the link gets that for "
        "nothing. Presented as a cost, and accepted (Consequences; ToO §10).",
    ], "amber")

    CHECKS = [
        ("① The person's key", ["Against the anchor-issued roster resident on the vehicle (§2). `KeyOK`"]),
        ("② The commanded plane's certificate", ["Its commit certificate, not the autonomous plane's (ADR-0059 §5). "
                                                 "`CertOK`"]),
        ("③ The entry is in the seat's envelope", ["The release envelope: irreversible entries only (§2). "
                                                   "[[red|Not modelled]] in `Release`."]),
        ("④ The act names this vehicle  ⟨R1⟩", ["The act names one vehicle (§4), and fires only on that one. "
                                              "`VehicleOK`"]),
        ("⑤ The act is unused", ["**Each governor's own record** of the acts it fired. `UnusedOK`"]),
        ("⑥ Fresh: no more than a declared number of ticks past the tick it names ⟨Q16⟩", ["`FreshOK`: `tick ≤ "
                                                                                         "act.tick + FreshT`"]),
    ]
    REFS = [
        ("Refused: not the person's key", [
            "**An agent's signature** is refused here. Witness `NeverRefusedKey` violated: the refusal is reachable.",
        ], "red"),
        ("Refused: not the commanded certificate", [
            "**An act the autonomous plane originated** carries only its own. `NeverRefusedCert` violated.",
        ], "red"),
        ("Refused: an entry outside the envelope", [
            "**Not modelled.** `Release` abstracts an act's entry, inputs and envelope as the floor's business.",
        ], "red"),
        ("R1 ①  Without this check, one act fires once per vehicle", [
            "**Unused is each governor's own record**, so an act for one vehicle would be unused on every other. "
            "`M_ANYVEHICLE` removes the check and **`UsedOnce` fails**. `NeverRefusedVehicle` violated.",
        ], "amber"),
        ("Refused: a second use", [
            "`NeverRefusedReplay` violated. `M_REPLAY` removes the check and `UsedOnce` fails.",
        ], "red"),
        ("R1 ②  Aged is a count of the plane's ticks", [
            "**An act an adversary withholds arrives aged and is refused**: the NATO reading's F1, third case. "
            "`NeverRefusedAged` violated.",
            "**A captured plane can stop ticking, and no act then ages.** `NoOlderThanDeclared` is a statement about "
            "ticks. **Duration is the watchdog's** (ADR-0064 §5).",
        ], "amber"),
    ]
    EFF = ("The effector", [
        "**The irreversible effect, once**, fired only when every check passes (`Fire`).",
    ], "grey")
    AFTER = ("After the effect (ADR-0062 §6)", [
        "**Nothing a governor permitted is void**: the effect has happened. A check that fails at the seal or above is "
        "**a finding**: it subtracts, and ends the seat: "
        "`ConflictIsAFinding`.",
    ], "green")

    # ---- measure
    hro, hpe, hrep, hact = mh(ROST, cw[0]), mh(PERS, cw[0]), mh(REP, cw[0]), mh(ACT, cw[1])
    hse, hor, hag = mh(SEAT, cw[2]), mh(ORD, cw[2]), mh(AGT, cw[2])
    htk, hrl, hlo = mh(TICK, cw[3]), mh(RELAY, cw[3]), mh(ORIG, cw[3])
    gin = 18
    ciw = cw[4] - 2 * gin
    rows_h = []
    for (ct, cb), (rt, rb, _) in zip(CHECKS, REFS):
        rows_h.append(max(c.card(0, 0, ciw, ct, cb, draw=False, size=S, tsize=15),
                          c.card(0, 0, cw[5], rt, rb, draw=False, size=S, tsize=15)))
    hdr = 66
    cgap = 30
    vgap = 70

    lane = max(ftop + 50 + hro + vgap + hpe / 2,
               ftop + 50 + hse + vgap + hor / 2,
               ftop + 50 + htk + vgap + hrl / 2,
               ftop + 50 + hdr + rows_h[0] / 2)
    yg = lane - rows_h[0] / 2 - hdr          # top of the governor box
    ype = lane - hpe / 2
    yro = ype - vgap - hro
    yrep = ype + hpe + vgap
    yact = lane - hact / 2
    yor = lane - hor / 2
    yse = yor - vgap - hse
    yag = yor + hor + vgap
    yrl = lane - hrl / 2
    ytk = yrl - vgap - htk
    ylo = yrl + hrl + 110
    # interlock rows
    ychk = []
    yy = yg + hdr
    for h in rows_h:
        ychk.append(yy)
        yy += h + cgap
    gbot = yy - cgap + gin
    yeff = gbot + 70
    heff = max(mh(EFF, cw[4]), c.card(0, 0, cw[5], AFTER[0], AFTER[1], draw=False, size=S))
    # the cut-link card sits under both planes, centred on the link
    cut_w = 820
    cut_x = (cx[2] + cw[2] + cx[3]) / 2 - cut_w / 2
    planes_bot = max(yag + hag, ylo + hlo) + 34
    ycut = planes_bot + 60
    hcut = c.card(0, 0, cut_w, CUT[0], CUT[1], draw=False, size=S)

    # ---- regions
    c.region(cx[0] - 24, yro - 50, cw[0] + 48, yrep + hrep - yro + 50 + 30, "People: the roster and the person",
             "brown")
    reg_top = min(yse, ytk) - 50
    c.region(cx[2] - 24, reg_top, cw[2] + 48, planes_bot - reg_top, "The commanded plane: the intent boundary",
             "violet", dash=None)
    c.region(cx[3] - 24, reg_top, cw[3] + 48, planes_bot - reg_top, "The vehicle's plane: autonomous", "violet",
             dash=None)
    veh_bot = yeff + heff + 30
    c.region(cx[4] - 30, yg - 50, cw[4] + gaps[4] + cw[5] + 54, veh_bot - (yg - 50),
             "The vehicle · its governor (ADR-0062) and effector", "teal", dash=None)

    # ---- cards
    c.card(cx[0], yro, cw[0], ROST[0], ROST[1], accent=ROST[2], size=S)
    c.card(cx[0], ype, cw[0], PERS[0], PERS[1], accent=PERS[2], size=S)
    c.card(cx[0], yrep, cw[0], REP[0], REP[1], accent=REP[2], size=S, tint=False, dash="7 5")
    c.card(cx[1], yact, cw[1], ACT[0], ACT[1], accent=ACT[2], size=S)
    c.card(cx[2], yse, cw[2], SEAT[0], SEAT[1], accent=SEAT[2], size=S, tint=False)
    c.card(cx[2], yor, cw[2], ORD[0], ORD[1], accent=ORD[2], size=S)
    c.card(cx[2], yag, cw[2], AGT[0], AGT[1], accent=AGT[2], size=S, tint=False, dash="7 5")
    c.card(cx[3], ytk, cw[3], TICK[0], TICK[1], accent=TICK[2], size=S, tint=False)
    c.card(cx[3], yrl, cw[3], RELAY[0], RELAY[1], accent=RELAY[2], size=S)
    c.card(cx[3], ylo, cw[3], ORIG[0], ORIG[1], accent=ORIG[2], size=S, tint=False, dash="7 5")
    c.card(cut_x, ycut, cut_w, CUT[0], CUT[1], accent=CUT[2], size=S)
    # the governor and its interlock
    c.rect(cx[4], yg, cw[4], gbot - yg, "teal", tint=False, sw=2.2)
    c.text(cx[4] + gin, yg + 30, "**The governor's interlock (§4)**", 17, "teal")
    c.text(cx[4] + gin, yg + 52, "Every check must pass, or the act is refused", 13.5, "muted")
    for i, ((ct, cb), (rt, rb, racc)) in enumerate(zip(CHECKS, REFS)):
        c.card(cx[4] + gin, ychk[i], ciw, ct, cb, accent="teal", size=S, tsize=15, h=rows_h[i], bullets=False,
               dash="2 3" if i == 2 else None)
        c.card(cx[5], ychk[i], cw[5], rt, rb, accent=racc, size=S, tsize=15, h=rows_h[i], tint=(racc == "amber"),
               bullets=False, dash=None if racc == "amber" else "7 5")
        my = ychk[i] + rows_h[i] / 2
        c.arrow([(cx[4] + cw[4], my), (cx[5], my)], "red", dash="7 5", sw=2)
        if i < len(CHECKS) - 1:
            ax = cx[4] + gin + 60
            c.arrow([(ax, ychk[i] + rows_h[i]), (ax, ychk[i + 1])], "teal", sw=2)
    c.text(cx[4] + gin + 74, ychk[1] - cgap / 2 + 5, "and", 12.5, "teal", bold=True)
    c.card(cx[4], yeff, cw[4], EFF[0], EFF[1], accent=EFF[2], size=S, h=heff)
    c.card(cx[5], yeff, cw[5], AFTER[0], AFTER[1], accent=AFTER[2], size=S, h=heff)

    # ---- arrows
    # roster activates the seating
    rmy = yro + hro / 2
    c.arrow([(cx[0] + cw[0], rmy), (cx[2] - 60, rmy), (cx[2] - 60, yse + hse / 2), (cx[2], yse + hse / 2)], "brown",
            sw=2.4)
    c.label(cx[1] + cw[1] / 2, rmy, "activates the seat, for one named person and one round", "brown", 12.5,
            maxw=260)
    # the person's seat at that plane
    c.arrow([(cx[0] + cw[0], lane), (cx[1], lane)], "brown", sw=2.6, label="composes, signs", lpos=0.59, lw=70)
    c.arrow([(cx[1] + cw[1], lane), (cx[2], lane)], "brown", sw=2.6, label="submits", lpos=0.4)
    c.arrow([(cx[2] + cw[2], lane), (cx[3], lane)], "violet", sw=2.6, label="the link, with its certificate",
            lpos=0.5, lw=100)
    c.arrow([(cx[3] + cw[3], lane), (cx[4] + gin, lane)], "violet", sw=2.6, label="delivered", lpos=0.42)
    # report: untrusted ingress, enables nothing
    rx = cx[0] + cw[0] / 2
    c.arrow([(rx, yrep), (rx, ype + hpe)], "grey", dash="7 5", label="`untrusted`: enables nothing", lpos=0.5)
    c.arrow([(rx, yro + hro), (rx, ype)], "brown", sw=2.2, label="names the person", lpos=0.5)
    # the agent's act is ordered anyway
    ax_ = cx[2] + cw[2] / 2
    c.arrow([(ax_, yag), (ax_, yor + hor)], "red", dash="7 5", label="ordered: the floor is not assumed", lpos=0.5)
    # the relay can refuse one
    rfx = cx[3] + 90
    c.arrow([(rfx, yrl + hrl), (rfx, yrl + hrl + 62)], "red", dash="7 5")
    c.label(rfx + 120, yrl + hrl + 52, "the relay refuses one", "red", 12.5)
    # the captured plane's act reaches the governor's certificate check
    ox = cx[3] + cw[3] + gaps[3] / 2 - 4
    oy = ylo + hlo / 2
    c2y = ychk[1] + rows_h[1] / 2
    c.arrow([(cx[3] + cw[3], oy), (ox, oy), (ox, c2y), (cx[4] + gin, c2y)], "red", dash="7 5", sw=2)
    # the cut link
    lx = (cx[2] + cw[2] + cx[3]) / 2
    c.line(lx, lane + 26, lx, ycut, "amber", sw=2, dash="3 4")
    # interlock passes, the effector fires
    c.arrow([(cx[4] + cw[4] / 2, ychk[-1] + rows_h[-1]), (cx[4] + cw[4] / 2, yeff)], "teal", sw=2.6,
            label="every check passes", lpos=0.5)
    c.arrow([(cx[4] + cw[4], yeff + heff / 2), (cx[5], yeff + heff / 2)], "green", sw=2, label="a finding later",
            lpos=0.5)

    fbot = max(veh_bot, ycut + hcut, yrep + hrep + 30) + 40
    lg = c.legend(X0, fbot, [
        ("arrow", "brown", "a person acts"),
        ("arrow", "violet", "a plane orders or relays"),
        ("arrow", "teal", "the governor"),
        ("arrow", "red", "refused, or a path the interlock must refuse", "7 5"),
        ("box", "amber", "⟨R1⟩: a correction of 2026.11.10, placed where it applies"),
        ("box", "red", "an adversary's path the module allows up to the interlock", "7 5"),
    ])
    y = fbot + lg + 70

    # ================================================================== band 2: HITL, HOTL, and the two person seats
    y = band(c, X0, y, "Under HITL the judgment comes before the emission, and no budget is needed (Context; §1; §2)",
             status="proposed")
    top = y
    g = 50
    wl = 1500
    wr = WW - wl - g
    xr = X0 + wl + g
    h2 = row_cards(c, X0, top, wl, 30, [
        ("HOTL: the budget buys time to stop it after emission", [
            "**`W + L + D < T_irrev`** for each effect class (ADR-0032 §4). Detection and a human response follow the "
            "emission, and must land before it becomes irreversible.",
            "**When no budget fits**, in the limit an effect irreversible on emission, \"the effect must not be reachable "
            "from the alphabet at all\" (ADR-0032 §4; A10).",
            "Run's roughly one-second window leaves HOTL (glossary).",
        ], "grey", {"tint": False}),
        ("HITL: an irreversible effect is enabled only by a person's signed act ⟨4⟩", [
            "**A posture defined by its enabling condition** (glossary): here, a signed act of a person, made for that "
            "one effect.",
            "**The judgment comes before the emission, and no budget is needed** (Context).",
            "**So ADR-0032 §4 is relaxed**: an irreversible effect is reachable by a person and by nobody else. On "
            "admission that is **C3** (§6).",
        ], "brown", {}),
    ], size=14)
    ty = top + h2 + 30
    c.text(X0, ty + 16, "**ADR-0032 §4's table, whole** (Accepted): the three terms are of three kinds", 16, "ink")
    tw = c.table(X0, ty + 32, [("Term", 150, {"mono": True}), ("Meaning", 760), ("Kind", wl - 910)], [
        ["W", "Effect propagation window, about a second at the archetype", "**Guaranteed by the mechanism**"],
        ["L", "Observer detection latency", "**Emergent property of a component**, and **unmeasured**"],
        ["D", "Human response budget", "**Organizational commitment**"],
    ], size=14, accent="grey")
    ty2 = ty + 32 + tw + 22
    bl = stack(c, X0, ty2, wl, [
        ("§1: an entry declares its effect class, and an irreversible entry is reachable by a person only ⟨4⟩", [
            "The `effect` part of an allowlist entry (ADR-0062 §3) declares **`reversible` or `irreversible`, with its "
            "`T_irrev`**. It is promoted with the bundle and voted like any entry.",
            "**An irreversible entry is not reachable from any agent seat's alphabet, is not `local`, and is not "
            "reachable below the intent boundary.** It is reachable from one seat kind, which a person holds.",
            "**An effect class is a declaration**, as a label is (A15). **An irreversible effect declared reversible "
            "is seen by nothing here.**",
        ], "amber", {"status": "proposed"}),
    ], size=14)

    c.text(xr, top + 16, "**ADR-0062 §3's table, whole** (Proposed): the entry's sixth part, `effect`", 16, "ink")
    t3 = c.table(xr, top + 32, [("Field", wr * 0.32, {"bold": True}), ("Says", wr * 0.68)], [
        ["The class, with its `T_irrev`", "`reversible` or `irreversible` (ADR-0066)"],
        ["How it is permitted", "`local`, by the governor; or `ordered`, by the plane before the effect. **No "
                                "irreversible entry is `local`**"],
        ["Its extent", "ADR-0062 §4"],
        ["Whether it is the beacon", "ADR-0062 §5. At most one entry per seat kind"],
    ], size=14, accent="teal")
    ry = top + 32 + t3 + 30
    c.text(xr, ry + 16, "**The release seat beside the emergency seat**: the same activation, opposite envelopes (§2)",
           16, "ink")
    t4 = c.table(xr, ry + 32, [("", wr * 0.16, {"bold": True}),
                               ("`emergency` seat (ADR-0052, provisional)", wr * 0.42),
                               ("`release` seat (ADR-0066 §2, Proposed)", wr * 0.42)], [
        ["Held by", "A person with a Persona and a signing key, holding no other seat in the round (§1)",
         "A person, with a key, and nobody else in the round. No model's Persona binds to the kind"],
        ["Activated by", "A quorum on the anchor-issued break-glass roster: one lease, for one named person and one "
                         "round (§2)", "A roster's quorum, for one named person and one round, **as an emergency "
                                       "seating is** ⟨Q6⟩"],
        ["Where", "The Run domain (§1)", "**A commanded plane whose charter carries `release`**; never an autonomous "
                                         "one"],
        ["Alphabet", "`Consult`, `Actuate`, `Report` (§1)", "`Actuate` on irreversible entries in its envelope, and "
                                                           "`Report`"],
        {"cells": ["Envelope", "**Generic by default**: every Run allowlist entry in force in the domain (§2 ⟨R1⟩); a "
                               "deployment may name a narrower one",
                   "**The opposite**: irreversible entries only. **That is why the two kinds are kept apart**: reusing "
                   "`emergency` would admit irreversible entries to its envelope, which widens it everywhere (Options "
                   "⟨Q6⟩)"], "accent": "amber"},
        ["Observer", "Not coupled: `R3-observer-live` does not reach it (§4)",
         "Not coupled: while the seat is live and the plane in contact, a release can be admitted whatever any agent "
         "or Observer is doing (`ReleaseNeverCoupled`)"],
        ["`B10`", "An exception lets the seat `Actuate`", "**Gains the same exception** (ADR-0067 §4), which routes as "
                                                          "a relaxation"],
        ["The reason", "\"Unknown to the mechanism, by construction\" (§5)", "The same: ADR-0066 §5 quotes it"],
    ], size=14, accent="brown")
    y = max(bl, ry + 32 + t4) + 80

    # ================================================================== band 3: what is recorded, what is not judged
    y = band(c, X0, y, "What the mechanism records, and what it cannot judge (§5)", status="proposed")
    h5 = row_cards(c, X0, y, WW, 30, [
        ("Recorded: who, what, which vehicle, when", [
            "**Who acted, on what, through which vehicle and when.** One act, one effect, one person, on the record "
            "(Consequences).",
            "On the vehicle, the governor writes each entry it permits or refuses to its chain, sealed at the lease's "
            "end (ADR-0062 §6).",
        ], "teal", {}),
        ("Not recorded: why", [
            "**\"The reason is unknown to the mechanism, by construction\"** (ADR-0052). The act carries no field for "
            "it.",
        ], "grey", {"tint": False}),
        ("Not judged: whether the act was right", [
            "**That is the person's judgment, and the mechanism checks none of it.** It does not make an act lawful "
            "or right, and it records a wrong one without preventing it (Consequences).",
        ], "red", {"tint": False}),
        ("Not told apart: a person from a program holding the key", [
            "The mechanism \"cannot tell a person from a program holding the person's key\" (ToO §3.3). `Release` "
            "cannot either: a key and a commanded certificate are taken as unforgeable.",
        ], "red", {"tint": False}),
        ("A5 applies in full", [
            "**A trained, authorized person is present** (ToO A5), and this record adds that **they can see what the "
            "act requires them to see**. What they must be shown, no record states (Open obligations).",
            "**HITL is a key and not a judgment** unless that holds (Consequences).",
        ], "brown", {}),
    ], size=14)
    y += h5 + 80

    # ================================================================== band 4: the module
    y = band(c, X0, y, "The `Release` module: eight properties, nine mutations, ten witnesses, and the interlock as the "
             "only check it relies on (§7; spec/Release.tla)")
    top = y
    g = 50
    wl = 2000
    wr = WW - wl - g
    xr = X0 + wl + g
    c.text(X0, top + 16, "**The eight properties** (the module's header). Every one holds under `Mut = none`: "
           "**checked** by TLC and **proved** by TLAPS (`…Always` theorems)", 16, "ink")
    pcols = [("Property", 300, {"mono": True}), ("Says", 1000), ("From", 260), ("TLC, `Mut = none`", wl - 1560)]
    tp = c.table(X0, top + 32, pcols, [
        ["SignedByPerson", "Every irreversible effect has a person's key on it", "ADR-0066 §4",
         "[[teal|Holds]] in `Safe`"],
        ["OrderedAtCommand", "… and was ordered at a commanded plane", "ADR-0066 §4", "[[teal|Holds]] in `Safe`"],
        ["UsedOnce", "An act produces at most one effect, anywhere", "ADR-0066 §4", "[[teal|Holds]] in `Safe`"],
        ["NoOlderThanDeclared", "An effect is no more than `FreshT` ticks past the tick its act names. **A statement "
                                "about ticks, not duration** ⟨R1⟩", "ADR-0066 §4", "[[teal|Holds]] in `Safe`"],
        {"cells": ["IrreversibleIsAPersons", "**The conjunction of those four**: §7's named property", "ADR-0066 §7",
                   "[[teal|Holds]] in `Safe`"], "accent": "teal"},
        ["ConflictIsAFinding", "A check failing at a seal or above subtracts, and voids nothing a governor permitted",
         "ADR-0062 §6; the custodian, 2026.11.10", "[[teal|Holds]] in `Safe`"],
        ["OrderedInContact", "An act is admitted only in contact with the intent boundary", "ADR-0066 §4 ⟨R1⟩",
         "[[teal|Holds]] in `Safe`"],
        ["ReleaseNeverCoupled", "**Over `ENABLED`**, in the shape of `Emergency_live.tla`: while the seat is live, the "
                                "plane is in contact and an act id remains, a release can be admitted whatever any "
                                "agent or Observer is doing. The module's bound is in the hypothesis, as a bound and "
                                "not as a claim", "ADR-0066 §7", "[[teal|Holds]]"],
    ], size=14, accent="teal")
    my_ = top + 32 + tp + 30
    c.text(X0, my_ + 16, "**The nine mutations**: each breaks what it is listed against and nothing else (67 rows, all "
           "as expected)", 16, "ink")
    mcols = [("Mutation", 300, {"mono": True}), ("What it removes", 920), ("Breaks", 400), ("Still holds", wl - 1620)]
    tm = c.table(X0, my_ + 32, mcols, [
        ["M_AGENTRELEASE", "The interlock does not check the person's key", "`SignedByPerson`, "
         "`IrreversibleIsAPersons`", "the other six"],
        ["M_LITERELEASE", "The interlock accepts the autonomous plane's certificate", "`OrderedAtCommand`, "
         "`IrreversibleIsAPersons`", "the other six"],
        ["M_REPLAY", "The interlock does not check that the act is unused", "`UsedOnce`, `IrreversibleIsAPersons`",
         "the other six"],
        {"cells": ["M_ANYVEHICLE", "The interlock does not check the act's vehicle: **the check R1 added to §4**",
                   "`UsedOnce`, `IrreversibleIsAPersons`", "the other six"], "accent": "amber"},
        ["M_LATEFIRST", "A first delivery after the ticks have run is accepted, **as an interval from receipt would "
                        "be**", "`NoOlderThanDeclared`, `IrreversibleIsAPersons`", "the other six"],
        ["M_VOID", "A failed check voids an effect that happened", "`ConflictIsAFinding`",
         "`IrreversibleIsAPersons`, `OrderedInContact`, `ReleaseNeverCoupled`"],
        ["M_NOCONTACT", "A release is admitted with no link", "`OrderedInContact`",
         "`IrreversibleIsAPersons`, `ConflictIsAFinding`, `ReleaseNeverCoupled`"],
        ["M_OBSCOUPLE", "A release waits for a live Observer", "`ReleaseNeverCoupled`", "`Safe`: only the `ENABLED` "
                                                                                        "invariant sees it"],
        ["M_AGENTPROPOSES", "A release waits for an agent's proposal, **the design §3 rejects**",
         "`ReleaseNeverCoupled`", "`Safe`: only the `ENABLED` invariant sees it"],
    ], size=14, accent="red")
    lbot = my_ + 32 + tm

    c.text(xr, top + 16, "**Ten witnesses**, each VIOLATED as expected: each shows a behaviour is reachable", 16, "ink")
    tw_ = c.table(xr, top + 32, [("Witness", 330, {"mono": True}), ("Reachable", wr - 330)], [
        ["NeverFired", "An act fires"],
        {"cells": ["NeverFiredAfterCut", "**An act fires after the link is cut** (R1 ③): what bounds it is freshness"],
         "accent": "amber"},
        ["NeverRefusedKey", "The interlock refuses on the key"],
        ["NeverRefusedCert", "… on the certificate"],
        ["NeverRefusedVehicle", "… on the vehicle"],
        ["NeverRefusedReplay", "… on a second use"],
        ["NeverRefusedAged", "… on an aged act"],
        ["NeverRelayRefused", "The autonomous plane refuses to relay one"],
        ["NeverFinding", "A check fails after an effect: a finding"],
        ["NeverSubtraction", "A finding ends a live seat"],
    ], size=14, accent="pink")
    sy = top + 32 + tw_ + 30
    # the series: floor, then interlock
    c.text(xr, sy + 16, "**The interlock is the only check the module relies on**", 16, "ink")
    sy += 34
    fw = (wr - 60) / 2
    FLB = ["A second check in series (ADR-0067, Proposed). **Not assumed.**", "[[red|Not written.]]"]
    hfs = max(c.card(0, 0, fw, "The floor: `FD5`, `FD6`, `FD9`", FLB, draw=False, size=S),
              c.card(0, 0, fw, "The governor's interlock", ["Key, certificate, vehicle, unused, fresh. **Every "
                                                            "property rests on it alone.**"], draw=False, size=S))
    c.card(xr, sy, fw, "The floor: `FD5`, `FD6`, `FD9`", FLB, accent="red", size=S, h=hfs, tint=False, dash="2 3")
    c.card(xr + fw + 60, sy, fw, "The governor's interlock", ["Key, certificate, vehicle, unused, fresh. **Every "
                                                              "property rests on it alone.**"], accent="teal", size=S,
           h=hfs)
    c.arrow([(xr + fw, sy + hfs / 2), (xr + fw + 60, sy + hfs / 2)], "grey", sw=2)
    sy += hfs + 18
    rb = stack(c, xr, sy, wr, [
        (None, [
            "**`AdmitAgent`** lets an agent's signed act be ordered at the commanded plane, and **`LiteOriginate`** "
            "lets the autonomous plane originate any act. The floor would refuse both; the module does not assume it.",
            "**Taken as unforgeable**: a person's key and a commanded plane's certificate.",
        ], "teal", {"tint": False}),
        ("What is abstracted (the header)", [
            "**An act's entry, inputs and envelope**: the floor's business. So check ③ of the picture is not modelled.",
            "**The roster's quorum that activates the seat**: `Emergency.tla`'s shape, here one action.",
            "**An act names the latest tick** the commanded plane knows; naming an older one only ages it sooner.",
            "**A void before the effect**, which ADR-0062 §6 allows of an ordered entry: every check here fails after "
            "the effect.",
            "**Whether the act was right**: the person's judgment (§5).",
            "One commanded plane, one autonomous plane, two vehicles, one person, one agent, one irreversible entry. "
            "Deadlock is not checked: a release that is never used is safe.",
        ], "grey", {"tint": False}),
    ], size=14)
    by = max(lbot, rb) + 30
    h4 = row_cards(c, X0, by, WW, 30, [
        ("Checked: 67 rows, all as expected", [
            "`Release-rows.txt`, TLC 2.19, at `MaxActs = 2`, `MaxTick = 1`, `FreshT = 0`, with rows at `MaxActs = 3` "
            "and at `MaxTick = 2`, `FreshT = 1`. The base model: 263,936 distinct states, depth 19.",
            "`Release-results-2026.11.10.txt` (`34afe5523f488399`): as expected 67, not as expected none, ERROR none.",
        ], "violet", {"tint": False}),
        ("Proved: 613 obligations", [
            "`Release_proof.tla` (`ac1cb37282c19f5a`), tlapm 7824dab: ten theorems, `ShapeAlways` to `SafeAlways`, "
            "under `MaxActs`, `MaxTick`, `FreshT` ∈ `Nat`. **Mutations and witnesses are behaviours and stay with "
            "TLC.**",
        ], "violet", {"tint": False}),
        ("Certified, with 10 LS4 temporal steps that no checker confirms", [
            "391 trivial, closed by tlapm; 211 SMT, each with a proof ethos accepted; 1 Isabelle; **10 LS4, not "
            "certified** (`Release-proof-cert-results-2026.11.10.txt`, `5c0b3884c1381f04`).",
        ], "violet", {"tint": False}),
        ("Three findings, taken by R1", [
            "The header's three findings against ADR-0066 as drafted: **the vehicle check** (①), **a cut link** (③) "
            "and **ticks, not duration** (②). R1 wrote each into §4, so the header now describes text that has "
            "changed.",
        ], "amber", {}),
    ], size=14)
    y = by + h4 + 80

    # ================================================================== band 5: overlay, ratification, options
    y = band(c, X0, y, "Overlay position, what ratification needs, and what was weighed (§6, §7, Options, "
             "Consequences)", status="proposed")
    top = y
    g = 50
    wl = 1500
    wr = WW - wl - g
    xr = X0 + wl + g
    lb = stack(c, X0, top, wl, [
        ("§6: an overlay, reported upstream ⟨Q11⟩", [
            "**Reported under ADR-0058 §6**: an effect class on an entry, and an irreversible effect expressible by a "
            "person. **No degeneracy of its own.**",
            "**If the archetype takes them, its records owe**: ADR-0032 §4 relaxed from \"not reachable at all\" to "
            "\"reachable by a person and by nobody else\", **which is C3**; ADR-0037, the seat kind `release`; "
            "ADR-0049, the entry's `effect` part; the floor's `B10-only-thinkers-author`, an exception for a "
            "`release` seat's `Actuate`, as it has for an `emergency` seat.",
            "**Carries a debt against nothing** while it is an overlay. **Closes nothing.**",
        ], "amber", {"tint": False}),
    ], size=14)
    lb += 30
    c.text(X0, lb + 16, "**§7: the ratification condition, item by item**", 16, "ink")
    tr = c.table(X0, lb + 32, [("Item", wl * 0.66), ("State", wl * 0.34)], [
        ["**ADR-0059, ADR-0060, ADR-0062 and ADR-0064 ratified first**, or with this record, **and ADR-0052 no longer "
         "provisional**", "[[red|Not met]]: all four Proposed; ADR-0052 provisional (B34)"],
        {"cells": ["**A module `Release`**: `IrreversibleIsAPersons`; `M_AGENTRELEASE`, `M_LITERELEASE`, `M_REPLAY`, "
                   "`M_LATEFIRST`; an `ENABLED` invariant in the shape of `Emergency_live.tla`. Added: "
                   "`OrderedInContact`, `M_ANYVEHICLE`, `M_NOCONTACT`, `M_OBSCOUPLE`, `M_AGENTPROPOSES`; "
                   "`ConflictIsAFinding` with `M_VOID` (the custodian, 2026.11.10)",
                   "[[teal|Met for TLC and TLAPS]] ⟨R1⟩: checked, proved, certified with 10 LS4 steps (band 4)"],
         "accent": "teal"},
        ["**The floor** carries `FD5`, `FD6` and `FD9`, and the relaxation of `B10` routes as one (ADR-0067)",
         "[[red|Not written]]: the `federation` stage does not exist"],
        ["**The reference** shows a release act admitted; one refused under an agent's seat; one refused at an "
         "autonomous plane; a second use refused; a late first delivery refused", "[[red|Not met]]: not built"],
        ["**A reader who is not the drafter** (ADR-0029 A2)", "[[red|Not met]]"],
    ], size=14, accent="blue")
    lb = lb + 32 + tr

    c.text(xr, top + 16, "**Options considered, whole**", 16, "ink")
    to = c.table(xr, top + 32, [("Option", wr * 0.36, {"bold": True}), ("Disposition", wr * 0.64)], [
        {"cells": ["Irreversible effects inexpressible, ADR-0032 §4 as written",
                   "[[grey|Not taken ⟨4⟩.]] The deployment this set describes has them"], "accent": "grey"},
        {"cells": ["An agent's seat with a budget `W + L + D < T_irrev`",
                   "[[red|Rejected.]] For an effect irreversible on emission no budget fits, which is ADR-0032's own "
                   "conclusion"], "accent": "red"},
        {"cells": ["The person countersigns an agent's proposal",
                   "[[grey|Not taken ⟨Q5⟩.]] The agent's output would be on the path to the effect, and approval can "
                   "become a click"], "accent": "grey"},
        {"cells": ["Reuse the `emergency` kind",
                   "[[grey|Not taken ⟨Q6⟩.]] Its envelope would have to admit irreversible entries, which widens it "
                   "everywhere"], "accent": "grey"},
        {"cells": ["A release seat at an autonomous plane",
                   "[[red|Rejected.]] Every effect is admitted at the intent boundary (ADR-0060 §1), and a plane with "
                   "no people has nobody to seat"], "accent": "red"},
        {"cells": ["Freshness by a challenge from the governor",
                   "[[grey|Not taken ⟨Q16⟩.]] Stronger, at one more round trip before every irreversible effect"],
         "accent": "grey"},
        {"cells": ["A release act that works with no link",
                   "[[red|Rejected.]] It would be a standing grant of an irreversible effect"], "accent": "red"},
    ], size=14, accent="grey")
    rb = top + 32 + to + 30
    rb = stack(c, xr, rb, wr, [
        ("Open obligations", [
            "**The floor entries and the reference** (§7).",
            "**The number of ticks** for which a release act is fresh, as a placeholder first.",
            "**What a person at a release seat must be shown**, which no record states.",
            "**Enumerating effect classes and their `T_irrev`**, which ADR-0032 already owes.",
        ], "red", {"tint": False, "status": "open"}),
    ], size=14)
    y = max(lb, rb) + 40
    h6 = row_cards(c, X0, y, WW, 30, [
        ("Consequences: positive", [
            "**No agent output is on the path to an irreversible effect.**",
            "**One act, one effect, one person, on the record.**",
            "**A withheld act cannot be used late**, as the plane's ticks count it (§4).",
        ], "green", {}),
        ("Consequences: negative", [
            "**With no link no irreversible effect can be ordered** ⟨R1⟩, and an adversary who jams the link gets that "
            "for nothing. The boundary register criticizes \"fail-closed uniformity presented as costless\" (ToO "
            "§10). Here it is presented as a cost, and accepted.",
            "**ADR-0032 §4 is relaxed.** An irreversible effect is expressible.",
            "**The mechanism does not make an act lawful or right**, and it records a wrong one without preventing it.",
            "**HITL is a key and not a judgment** unless a trained, authorized person holds it and can see what the act "
            "requires.",
            "**One author, one day.**",
        ], "red", {"tint": False}),
    ], size=14)
    c.ymax = max(c.ymax, y + h6)
    return c
