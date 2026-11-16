"""A5 — The command-chain overlay (ADR-0059 to ADR-0068, all Proposed 2026.11.10; ADR-0059 to ADR-0067 revised R1 the
same day): a tree of planes that only narrows, an intent boundary above every effect, and a vehicle that is a
governor and a stack. An orientation: the status of the ten records, one picture of the tree with every element
tagged by the record that defines it, the records in one table, the postures, what each reports upstream, and what
the overlay gives up (ADR-0068 §4)."""
from lib import Canvas, STATUS, STATE_CC, text_width

ID, SLUG = "A5", "command-chain-overlay"

W = 3600
S = 14            # body size in the picture


# -------------------------------------------------------------------------- helpers (copied from C10, extended)

def row_cards(c, x, y, w, gap, specs, size=14):
    """A row of cards of equal height, measured over every card. specs: (title, body, accent, kwargs).
    Returns (height, [x of each card], card width)."""
    n = len(specs)
    cw = (w - (n - 1) * gap) / n
    h = max(c.card(0, 0, cw, t, b, draw=False, size=size, status=k.get("status"),
                 bullets=k.get("bullets", True)) for t, b, _, k in specs)
    xs = []
    for i, (t, b, acc, k) in enumerate(specs):
        xi = x + i * (cw + gap)
        xs.append(xi)
        c.card(xi, y, cw, t, b, accent=acc, h=h, size=size, **k)
    return h, xs, cw


def measure_row(c, w, gap, specs, size=14):
    n = len(specs)
    cw = (w - (n - 1) * gap) / n
    return max(c.card(0, 0, cw, t, b, draw=False, size=size, status=k.get("status")) for t, b, _, k in specs)


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


# -------------------------------------------------------------------------- the records, as the strip and table use them

MODULES = [
    # module, rows, obligations, LS4 steps, record
    ("Federation", 41, 892, 7, "ADR-0059"),
    ("Intent", 35, 677, 5, "ADR-0060"),
    ("Membership", 28, 495, 6, "ADR-0061"),
    ("Alone", 47, 263, 6, "ADR-0062"),
    ("Outstanding", 40, 1871, 6, "ADR-0063"),
    ("PlaneClock", 38, 535, 6, "ADR-0064"),
    ("Peer", 25, 254, 6, "ADR-0065"),
    ("Release", 67, 613, 10, "ADR-0066"),
]
ROWS = sum(m[1] for m in MODULES)
OBL = sum(m[2] for m in MODULES)
LS4 = sum(m[3] for m in MODULES)


def ev(mod):
    m = next(x for x in MODULES if x[0] == mod)
    return (f"**{m[1]} rows checked**, all as expected · **{m[2]:,} obligations proved** · certified, with {m[3]} LS4 "
            f"temporal steps that no checker confirms")


def build():
    c = Canvas(
        ID, "The command-chain overlay: a tree of planes that only narrows, an intent boundary above every effect, "
            "and a vehicle that is a governor and a stack",
        "The custodian asked what follows if TOPAK is the top tier of a command chain, with control planes below it "
        "that only narrow ⟨1⟩. Ten records answer, drafted 2026.11.10: **planes are seated down a tree under "
        "charters that only narrow** (ADR-0059); **every effect's authorizing admit is ordered at the intent "
        "boundary**, the last commanded plane above a group of vehicles (ADR-0060); below it **an autonomous plane "
        "of replicas on the vehicles' governors grants leases and changes no authority** (ADR-0060, ADR-0061); "
        "**a governor permits under a lease with no further round**, and a vehicle that stops hearing its plane "
        "loses its lease (ADR-0062); revocation is **bounded in effects**, duration **in ticks** (ADR-0063, "
        "ADR-0064); stacks talk on declared topics and **nothing a peer originates enables anything** (ADR-0065); "
        "**an irreversible effect is a person's** (ADR-0066). **Every one is Proposed, and an overlay, not the "
        "archetype** ⟨Q11⟩. Nothing here is in force or built.",
        W,
        "ADR-0059 to ADR-0068: each record's Status note, Deployment position, Decision §1, overlay-position section "
        "(ADR-0059 §8, ADR-0060 §6, ADR-0061 §6, ADR-0062 §10, ADR-0063 §7, ADR-0064 §7, ADR-0065 §8, ADR-0066 §6, "
        "ADR-0068 §5), ratification condition (ADR-0059 §9, ADR-0060 §7, ADR-0061 §7, ADR-0062 §11, ADR-0063 §8, "
        "ADR-0064 §8, ADR-0065 §9, ADR-0066 §7, ADR-0067 §7, ADR-0068 §6) and History (R1); ADR-0059 §1 (its table), "
        "§2–§6, Annex A (⟨Q1⟩–⟨Q20⟩); ADR-0060 §1 (its table), §2, §3 (its table), §5; ADR-0061 §1–§4; ADR-0062 "
        "§1–§8; ADR-0063 §1–§6; ADR-0064 §1–§5; ADR-0065 §1–§4; ADR-0066 §1–§5; ADR-0067 §1–§5; ADR-0068 §1 (TM1), "
        "§2 (T-0068-5), §3 (A-0068-1), §4 in full, Findings 1, 2; spec/Federation, Intent, Membership, Alone, "
        "Outstanding, PlaneClock, Peer and Release: each module's header, its -rows.txt, and the summary lines of "
        "its -results-, -proof-results- and -proof-cert-results-2026.11.10.txt; spec/proof-scan-results-2026.11.10.txt; "
        "derived/topak-federated-c2-design-proposal-2026.11.10b.md §1 (terms and tiers), for orientation only",
        state=STATE_CC)
    X0, X1 = c.x0, c.x1
    WW = X1 - X0
    y = c.y

    # ================================================================== status strip
    c.text(X0, y + 15, "Status", 15, "faint", bold=True)
    px0 = X0 + 80
    px = px0
    items = [
        ("ADR-0059", "proposed", "C1"),
        ("ADR-0060", "proposed", "C1, C2"),
        ("ADR-0061", "proposed", "C1"),
        ("ADR-0062", "proposed", "C1, C2"),
        ("ADR-0063", "proposed", "C1"),
        ("ADR-0064", "proposed", "no criterion"),
        ("ADR-0065", "proposed", "C2"),
        ("ADR-0066", "proposed", "C1 · provisional while ADR-0052 is"),
        ("ADR-0067", "proposed", "C1"),
        ("ADR-0068", "proposed", "C2"),
        None,
        ("each record", ("An overlay, not the archetype ⟨Q11⟩", "amber", "6 4"), ""),
        ("eight TLA+ modules, 2026.11.10", ("Checked: %d TLC rows, all as expected" % ROWS, "teal", None), ""),
        ("their proofs", ("Proved: %s TLAPS obligations" % f"{OBL:,}", "teal", None), ""),
        ("each proof module", ("Certified, with %d to %d LS4 temporal steps that no checker confirms (%d in all)"
                               % (5, 10, LS4), "teal", "4 3"), ""),
        None,
        ("the `federation` floor stage, `FD1` to `FD14`", ("Not written", "red", "2 3"), ""),
        ("the reference", "notbuilt", ""),
        ("ratified", ("None of the ten", "red", "2 3"), ""),
        ("in force", ("Nothing", "red", "2 3"), ""),
    ]
    for it in items:
        if it is None:
            px = px0
            y += 34
            continue
        lab, key, extra = it
        lw = text_width(lab, 13.5, True) + 8
        if isinstance(key, tuple):
            plab = key[0]
        else:
            plab = STATUS[key][0] + (f" · {extra}" if extra else "")
        pw = text_width(plab, 11.5, True) + 18
        if px + lw + pw > X1:
            px = px0
            y += 34
        c.text(px, y + 15, lab, 13.5, "ink", bold=True)
        px += lw
        if isinstance(key, tuple):
            px += c.pill(px, y, key[0], key[1], 11.5, dash=key[2]) + 26
        else:
            px += c.status(px, y, key, extra) + 26
    y += 42
    y += c.para(X0, y, WW, "**Proposed means nothing here is in force.** The ten records were drafted in one day by one "
                "author from the custodian's decisions ⟨1⟩–⟨22⟩ and answers ⟨Q1⟩–⟨Q20⟩ (ADR-0059 Annex A), and ADR-0059 "
                "to ADR-0067 were revised R1 the same day to take the modules' findings; ADR-0068 has no R1 row. **Each is "
                "an overlay** ⟨Q11⟩: a deployment adds these nodes under ADR-0058 (Proposed) and reports them upstream "
                "as findings about the archetype, and **a deployment with one plane is the corpus as it stands and takes "
                "nothing from them** (ADR-0059, deployment position). **Checked** is said of TLC rows at small constants, "
                "**proved** of TLAPS obligations, and **certified** only with its LS4 steps named; none of the three is "
                "said of running code, and none exists. ADR-0067 has no module (no Cedar is written) and ADR-0068 is "
                "declarative. The proof scan finds no capture in any of the eight proof modules "
                "(spec/proof-scan-results-2026.11.10.txt).", 14.5, "muted") + 40

    # ================================================================== band 1: the picture
    y = band(c, X0, y, "One tree of planes, top to bottom, with every element tagged by the record that defines it",
             status="proposed", extra="nothing here is built")
    top = y + 20
    TW = 2300                      # the tree's width, fence lane included
    RX0 = X0
    RX1 = X0 + TW - 170            # the regions' right edge; the fence lane is to its right
    XF = RX1 + 85                  # the fence lane
    IX0, IX1 = RX0 + 24, RX1 - 24
    IW = IX1 - IX0
    G = 140                        # vertical gap between tiers, for arrows and their labels
    CG = 26                        # gap between cards in a tier

    def tier(ry, label, accent, specs, dash=None):
        h = measure_row(c, IW, CG, specs, S)
        rh = 46 + h + 26
        c.region(RX0, ry, RX1 - RX0, rh, label, accent, dash=dash, size=15)
        _, xs, cw = row_cards(c, IX0, ry + 46, IW, CG, specs, size=S)
        return ry + rh, ry + 46, h, xs, cw

    # ---- tier 1: the root plane
    T1 = [
        ("The anchor's key", [
            "**Resident on every verifier**, as genesis rules are (ADR-0027).",
            "A verifier checks each chain **from the anchor's key down**, with no plane in reach (ADR-0059 §5).",
        ], "blue", {}),
        ("The root's tally", [
            "**Seats each child plane by voting its charter**, as it votes any seating (ADR-0024 A3; ADR-0059 §1).",
            "**A child's `budget` is debited from its parent's**: the root's tally bounds what is allocated across the "
            "tree, and what is issued in any subtree with no captured plane ⟨R1⟩.",
        ], "blue", {}),
        ("One floor, in Cedar ⟨Q8⟩", [
            "**Every charter carries the root's floor digest.** Planes differ by bundles only (ADR-0059 §2).",
            "Its `federation` stage, `FD1` to `FD14`, is [[red|not written]] (ADR-0067 §3, §7).",
        ], "teal", {}),
        ("Anchor-issued rosters", [
            "**No plane below the root can mint a person** (ADR-0013; ADR-0066 §2).",
            "A governor checks a release key against the roster resident on the vehicle.",
        ], "brown", {}),
    ]
    t1b, t1c, t1h, xs, cw = tier(top, "The root plane · the anchor · ADR-0059 §1, §2, §5", "blue", T1)
    col = [x + cw / 2 for x in xs]

    # ---- tier 2: commanded planes
    T2 = [
        ("Grant seats: a tally", [
            "**A new issuer or a new artifact is a promotion** ⟨Q1⟩: seating a plane, or a bundle with a mission's rules "
            "(ADR-0059 §3).",
        ], "blue", {}),
        ("A commander or an operator", [
            "**Moves a value already in force down by an ordered admit**, signed by one person: a shorter `ttl`, an "
            "entry removed, a revocation, a fence (ADR-0059 §3).",
            "A release seat may sit at any commanded plane whose charter carries `release` (ADR-0066 §2).",
        ], "brown", {}),
        ("Its bundles, appended", [
            "**A lower plane's bundle can refuse and is never asked whether to grant.** \"Narrower\" holds of the "
            "composed decision, at every plane and every age (ADR-0059 §2).",
        ], "blue", {}),
        ("A person may route ⟨Q10⟩", [
            "**In an orchestrator seat** on a DAG promoted here, choosing among edges the mechanism has already "
            "enabled. `Mediated`: attributed, not contained (ADR-0060 §5).",
        ], "brown", {}),
    ]
    t2top = t1b + G
    t2b, t2c, t2h, _, _ = tier(t2top, "Commanded planes, any number: people are seated here · ADR-0059 §3; "
                                      "ADR-0060 §1, §5", "blue", T2, dash="10 6")

    # ---- tier 3: the intent boundary
    T3 = [
        ("A person at a release seat", [
            "**Activated by a roster's quorum** for one named person and one round, as an emergency seating is ⟨Q6⟩.",
            "**The person is the actor** ⟨Q5⟩ and composes and signs each irreversible act. A stack's report reaches "
            "the person as `untrusted` ingress and enables nothing (ADR-0066 §2, §3).",
        ], "brown", {}),
        ("The tally: the mission and the first intent", [
            "**One tally votes a mission's bundle, its mesh, and the charters and seatings it needs** (ADR-0060 §5).",
            "The mesh is promoted here with its budget, and **that tally grants the first charter for a round** "
            "(ADR-0060 §2; ADR-0055).",
        ], "blue", {}),
        ("The commander: each later intent", [
            "**ADR-0050's successor grant**: one operator, with a live lease and a live peer.",
            "**Every field the promoted seating's or narrower**, not the last intent's ⟨Q4⟩, so a commander who narrows "
            "can restore (ADR-0060 §2).",
        ], "brown", {}),
        ("Its mechanism: the plane's Observer", [
            "**Reads the autonomous plane's record as it is made**, archives it and runs its checks (ADR-0063 §1).",
            "**Orders each watermark, and no person signs it** ⟨Q12⟩. Its reading is a trust root for the watermark "
            "(T-0068-5).",
        ], "teal", {}),
    ]
    t3top = t2b + G
    t3b, t3c, t3h, _, _ = tier(t3top, "The intent boundary: the last commanded plane above a group of vehicles · "
                                      "ADR-0060 §1", "blue", T3)

    # ---- tier 4: the autonomous plane
    T4 = [
        ("Relays a release act", [
            "**It can refuse one and cannot originate one** (ADR-0060 §1; ADR-0066 §4).",
            "**An act is ordered only while the plane is in contact** with the intent boundary ⟨R1⟩.",
        ], "violet", {}),
        ("Its one grant: a node's lease", [
            "**Made by the mechanism under a live intent**, every field the seating's or narrower (ADR-0060 §3).",
            "**Charged in full at the grant.** No grant that would take the outstanding charge to `K_up` "
            "(ADR-0063 §3).",
            "**An honest plane's log holds no act that changes authority.** A captured plane's log is not evidence "
            "⟨R1⟩.",
        ], "violet", {}),
        ("Its clock is its ticks", [
            "**Tick τ says τ periods have passed since the charter was applied**, signed by a certificate of "
            "replicas, each on its own clock (ADR-0064 §1, §2).",
            "**Every interval is a count of ticks from a named tick** (§3).",
        ], "violet", {}),
        ("Seven replicas, Byzantine agreement", [
            "**On the vehicles' governors** ⟨Q3⟩. A declared relay node with no stack may host one (ADR-0060 §3).",
            "**A certificate of 5 tolerates 2 captured.** PBFT at the reference, signed, with a reconfiguration step; "
            "recalled, not read (ADR-0061 §1, §2).",
            "**Shrinks 7, 6, 5, 4 by voted steps** to a capture floor of one ⟨Q18⟩ (§3, §4).",
        ], "violet", {}),
    ]
    t4top = t3b + G
    t4b, t4c, t4h, _, _ = tier(t4top, "The autonomous plane · ADR-0060 §3; ADR-0061", "violet", T4)

    # ---- tier 5: the vehicles
    vtop = t4b + G + 20
    vgap = 165
    vw = [900, (RX1 - RX0 - 900 - 2 * vgap) / 2]
    vw.append(vw[1])
    vx = [RX0, RX0 + vw[0] + vgap, RX0 + vw[0] + vgap + vw[1] + vgap]
    vp = 20
    GOV1 = ("The governor · mechanism, trusted (ADR-0062 §1)", [
        "**Verifies the chain** and holds the lease and the vehicle's key. **Hosts the vehicle's replica** of the plane.",
        "**Evaluates the floor in Cedar and each bundle on the chain in Wasm** (ADR-0067 §2).",
        "**Permits each `local` entry under the lease against an exact count, with no further round**, and holds when "
        "an entry's extent ends with nothing after it ⟨Q14⟩ (ADR-0062 §2, §4).",
        "**Lifts its own facts**: elapsed time, position, the count, an entry's extent. **Holds the radio**, so a "
        "stack cannot make its own vehicle alone.",
        "**Its interlock fires a release act** only on the person's key, the commanded plane's certificate, an entry "
        "in the seat's envelope, this vehicle ⟨R1⟩, unused, and fresh in ticks ⟨Q16⟩ (ADR-0066 §4).",
        "**Keeps its own account against `K_up`** and checks each watermark itself (ADR-0063 §3).",
        "**When the next tick is overdue by its own clock, the vehicle is alone and the lease ends** (ADR-0062 §5; "
        "ADR-0064 §5).",
        "**Writes the record**: a hash-linked chain, signed, sealed at the lease's end (ADR-0062 §6).",
    ], "teal")
    STK1 = ("The stack · Byzantine", [
        "Planning, perception, any model: **the Thinker** (ADR-0062 §1; ADR-0068 TM1).",
        "Chooses among entries its lease permits: **which, never whether** (ADR-0065 §4).",
    ], "red")
    ACT1 = ("Actuators and radio", [
        "**Reached only through the governor** (A-0068-1). Any other path is D-0062-1, which voids every property for "
        "that vehicle.",
    ], "grey")
    GOV2 = ("The governor", ["Its own replica, lease, count, `K_up` account and record, as vehicle 1's."], "teal")
    STK2 = ("The stack", ["Byzantine."], "red")
    ACT2 = ("Actuators, radio", ["Through the governor only."], "grey")
    vbots = []
    govs = []
    for i in range(3):
        gv, sk, ac = (GOV1, STK1, ACT1) if i == 0 else (GOV2, STK2, ACT2)
        iw = vw[i] - 2 * vp
        gx = vx[i] + vp
        gy = vtop + 44
        gh = c.card(0, 0, iw, gv[0], gv[1], draw=False, size=S)
        sw = (iw - 30) / 2
        sh = max(c.card(0, 0, sw, sk[0], sk[1], draw=False, size=S), c.card(0, 0, sw, ac[0], ac[1], draw=False, size=S))
        sy = gy + gh + 80
        vb = sy + sh + vp
        c.region(vx[i], vtop, vw[i], vb - vtop, "Vehicle %d%s" % (i + 1, " · ADR-0062 §1" if i == 0 else ""), "grey", dash="10 6", size=15)
        c.card(gx, gy, iw, gv[0], gv[1], accent=gv[2], size=S)
        c.pill(gx + iw - 12, gy + 12, "replica", "violet", 11.5, anchor="end")
        c.card(gx, sy, sw, sk[0], sk[1], accent=sk[2], size=S, tint=False, h=sh)
        c.card(gx + sw + 30, sy, sw, ac[0], ac[1], accent=ac[2], size=S, tint=False, h=sh)
        c.arrow([(gx + sw / 2, sy), (gx + sw / 2, gy + gh)], "red", sw=2.2, label="requests", lpos=0.5)
        c.arrow([(gx + sw + 30 + sw / 2, gy + gh), (gx + sw + 30 + sw / 2, sy)], "teal", sw=2.2, label="permits",
                lpos=0.5)
        vbots.append(vb)
        govs.append((gx, gy, iw, gh))

    # ---- arrows between tiers
    gap12 = (t1b, t2top)
    gap23 = (t2b, t3top)
    gap34 = (t3b, t4top)
    # ① charters down the spine (column 1)
    c.arrow([(col[1], gap12[0]), (col[1], gap12[1])], "blue", sw=2.6, label="① charter, voted by the root's tally")
    c.arrow([(col[1], gap23[0]), (col[1], gap23[1])], "blue", sw=2.6, label="① charter, voted by a tally")
    c.arrow([(col[1], t3c + t3h), (col[1], gap34[1])], "blue", sw=2.6, label="① charter · ② the first intent",
            lpos=0.55)
    # ② later intents, from the commander
    c.arrow([(col[2], t3c + t3h), (col[2], gap34[1])], "brown", sw=2.6, label="② each later intent", lpos=0.55)
    # ⑦ the release act: person -> ordered here -> relayed -> the governor's interlock
    xr = xs[0] + cw - 70           # clear of the autonomous plane's and vehicle 1's label tabs
    c.arrow([(xr, t3c + t3h), (xr, t4c)], "brown", sw=3, label="⑦ release act, ordered here, with its "
                                                                       "certificate", lpos=0.55, lw=330)
    gx1, gy1, gw1, gh1 = govs[0]
    c.arrow([(xr, t4c + t4h), (xr, gy1)], "brown", sw=3, label="⑦ relayed to the interlock", lpos=0.5)
    # ④ the record up, the watermark down (column 3)
    c.arrow([(col[3] - 110, gap34[1]), (col[3] - 110, t3c + t3h)], "pink", sw=2.6, label="④ the record, as made",
            lpos=0.45)
    c.arrow([(col[3] + 110, t3c + t3h), (col[3] + 110, gap34[1])], "teal", sw=2.6, label="④ watermarks",
            lpos=0.45)
    # ③ leases and ⑤ ticks: a bus from the plane to every governor
    ybus = t4b + (vtop - t4b) / 2 - 6
    vcen = [vx[i] + vw[i] / 2 for i in range(3)]
    vcen[0] = vx[0] + vw[0] * 0.62
    c.arrow([(col[1], t4c + t4h), (col[1], ybus)], "violet", sw=2.4, head=False)
    c.arrow([(col[2], t4c + t4h), (col[2], ybus)], "violet", sw=2.4, head=False)
    c.arrow([(vcen[0], ybus), (vcen[2], ybus)], "violet", sw=2.4, head=False)
    for i in range(3):
        c.arrow([(vcen[i], ybus), (vcen[i], govs[i][1])], "violet", sw=2.4)
    c.label((col[1] + col[2]) / 2, ybus, "③ leases, one round each · ⑤ ticks, once per period", "violet", 13)
    # ⑥ peer topics among governors
    for i in range(2):
        yy = govs[i + 1][1] + 40
        c.arrow([(govs[i][0] + govs[i][2], yy), (govs[i + 1][0], yy)], "grey", sw=2.4, both=True)
        c.label((govs[i][0] + govs[i][2] + govs[i + 1][0]) / 2, yy + 30, "⑥ peer topic", "grey", 12.5)
    # ⑧ plane fences: dashed, pushed down the lane on the right
    ymid1 = t1c + t1h / 2
    g3x, g3y, g3w, g3h = govs[2]
    yv = g3y + g3h / 2
    c.arrow([(RX1, ymid1), (XF, ymid1), (XF, yv), (g3x + g3w, yv)], "green", dash="7 5", sw=2.6)
    for yy in (t2c + t2h / 2, t3c + t3h / 2, t4c + t4h / 2):
        c.arrow([(XF, yy), (RX1, yy)], "green", dash="7 5", sw=2.4)
    c.label(XF, (t1b + t2top) / 2, "⑧ plane fence", "green", 13)
    c.label(XF, (t3b + t4top) / 2, "⑧ pushed down", "green", 13)

    tree_bot = max(vbots)

    # ---- the key column
    KX = X0 + TW + 60
    KW = X1 - KX
    c.text(KX, top + 4, "**What each arrow is, and the record that defines it**", 17, "ink")
    ky = top + 22
    KEY = [
        ("① A charter, seated down the tree · ADR-0059 §1, §4, §5", [
            "**Seated by a promotion at the parent**: the parent's tally votes it. **Every field the parent's or "
            "narrower**, compared before the vote, when applied, and by every verifier of the chain.",
            "**Carries a commit certificate**: a quorum of the issuing plane's replicas over its digest and log index. "
            "Crash-recovery consensus cannot supply one, so an exposed plane runs Byzantine agreement ⟨Q7⟩.",
            "**A plane is a havoc issuer bounded by its charter.** The chain check bounds what each lease may carry, "
            "**and not how many a captured plane signs** ⟨R1⟩.",
        ], "blue", {}),
        ("② An intent, ordered at the intent boundary · ADR-0060 §1, §2", [
            "**A charter for one round**: a task, an envelope, an activation budget, and an `expiry` counted from a "
            "named tick (ADR-0064 §3); the first intent's from tick zero ⟨Q13⟩.",
            "**Ends** at its `expiry`, when its budget is spent, when ended or revoked, or when any plane above is "
            "fenced. **Ordered before the effect, and need not be live at it** ⟨R1⟩.",
        ], "brown", {}),
        ("③ A lease, granted by the autonomous plane · ADR-0062 §2, §5, §7", [
            "**One round of the plane per lease, and none per entry** ⟨21⟩ ⟨22⟩: the vehicle, the alphabet, the "
            "envelope, an exact count and a `ttl` in ticks.",
            "**Ends** when its count is spent and its last extent has run, at its `ttl`, on revocation or a fence, and "
            "**at once when the vehicle is alone**. An ending grants nothing.",
        ], "violet", {}),
        ("④ The record up, watermarks down · ADR-0063 §1–§5", [
            "**The log and each sealed lease record go up while the link holds.** A watermark comes down with a "
            "certificate and **carries every fence**, so a fence is pulled as well as pushed.",
            "**A watermark releases what it covers.** With the link cut the charge only grows and the plane stops "
            "before `K_up`: **a cut link fails closed**, with no premise about time.",
        ], "teal", {}),
        ("⑤ Ticks · ADR-0064 §1–§5", [
            "**Numbered from the charter, not from the tick before.** A replica signs no tick ahead of its own clock "
            "and no grant while the next tick is due.",
            "**No grant more than one tick period past an `expiry`**, under the premise that captured and slow "
            "replicas are fewer than a certificate: **a declared bound, not a safety theorem** (§4).",
        ], "violet", {}),
        ("⑥ Peer topics, among governors · ADR-0065 §1–§4", [
            "**A send is a `Report` to a declared topic**, permitted by the governor, **not ordered and not charged** "
            "to `K_up`. **Receipt is ingress**, labelled `untrusted` and by its topic ⟨Q19⟩. Nobody is addressed.",
            "**Nothing a peer originates enables anything.** A certified fact a peer relays is the plane's act.",
        ], "grey", {}),
        ("⑦ A release act · ADR-0066 §2–§4", [
            "**The person composes and signs it** ⟨Q5⟩, naming the entry, its inputs, the vehicle, the fences and a "
            "tick of the vehicle's plane. **Ordered at the commanded plane** and delivered with its certificate.",
            "**The interlock fires it once**, and only while fresh: no more than a declared number of ticks past the "
            "tick it names ⟨Q16⟩. Aged is a count of the plane's ticks ⟨R1⟩.",
        ], "brown", {}),
        ("⑧ A plane fence, pushed down · ADR-0059 §6", [
            "**Any plane that moves its epoch fences everything below it**: a subtraction, ordered, needing no "
            "quorum. A charter and a lease carry the epoch and index of every plane on the chain.",
            "**A fence travels as far as the link does**, and by relay among governors (ADR-0065 §1). What bounds a "
            "plane it cannot reach is ADR-0063.",
        ], "green", {"dash": "7 5"}),
    ]
    kb = stack(c, KX, ky, KW, KEY, gap=14, size=14)
    kb += 30
    c.text(KX, kb + 16, "**ADR-0059 §1's table, whole: the charter's closed schema**", 16, "ink")
    tk = c.table(KX, kb + 30, [("Field", 300, {"mono": False}), ("What it bounds", KW - 300)], [
        ["`plane`, `replicas`", "The child's identity: its replica keys and its quorum rule"],
        ["`kind`", "`commanded` or `autonomous` (ADR-0060)"],
        ["`parent`, `fences`", "Where it hangs, and the epoch and log index of every plane above it at the seating (§6)"],
        ["`floor`", "The floor's digest, which equals the parent's (§2)"],
        ["`bundles`", "The parent's list of bundle revisions, in order, plus any this seating adds"],
        ["`alphabet`, `labels`", "The entries and labels a lease under this charter may carry"],
        ["`ttlMax`, `countMax`", "The longest lease `ttl` the plane may grant and the largest count, per effect class"],
        ["`budget`", "The most leases the plane and every plane below it may ever issue"],
        ["`expiry`", "The charter's own life. Never later than the parent's"],
        ["`release`", "Whether a release seat may be seated at this plane (ADR-0066)"],
        {"cells": ["[[violet|Added by]]", "[[violet|ADR-0060, ADR-0061, ADR-0063 and ADR-0064: fields only an "
                   "autonomous plane carries]] (ADR-0059 §1, last bullet)"], "accent": "violet"},
        {"cells": ["`round`, `task`", "An intent's round and task (ADR-0060 §2)"], "accent": "violet"},
        {"cells": ["`membership`", "The smaller memberships the plane may fall back to, in order, and its capture "
                   "floor (ADR-0061 §3)"], "accent": "violet"},
        {"cells": ["`kUp`", "The outstanding charge the plane stays below: it grants nothing that would take it to "
                   "`K_up` (ADR-0063 §3)"], "accent": "violet"},
        {"cells": ["`tick`", "The tick period, `T_tick` (ADR-0064 §1)"], "accent": "violet"},
    ], size=14, accent="blue")
    kb = kb + 30 + tk
    c.para(KX, kb + 10, KW, "**Every field is the parent's or narrower**, field by field. A capability that is not a "
           "field is not carried (ADR-0059 §1).", 14, "muted")
    kb += 60

    pic_bot = max(tree_bot, kb) + 40
    lg = c.legend(X0, pic_bot, [
        ("arrow", "blue", "① a charter, voted by a tally"),
        ("arrow", "brown", "a person's act: ② an intent, ⑦ a release act"),
        ("arrow", "violet", "ordered by the plane: ③ leases, ⑤ ticks"),
        ("arrow", "pink", "④ the record, up"),
        ("arrow", "teal", "④ a watermark; a governor's permit"),
        ("arrow", "grey", "⑥ a peer topic, permitted and not ordered"),
        ("arrow", "green", "⑧ a fence: subtraction", "7 5"),
        ("box", "blue", "authority, issued rules"),
        ("box", "teal", "mechanism"),
        ("box", "violet", "consensus: the autonomous plane"),
        ("box", "brown", "people"),
        ("box", "red", "Byzantine"),
    ])
    y = pic_bot + lg + 80

    # ================================================================== band 2: the ten records
    y = band(c, X0, y, "The ten records, and what exists of each", status="proposed",
             extra="each an overlay, not the archetype ⟨Q11⟩")
    cols = [("Record", 120, {"bold": True}), ("Short title", 320, {"bold": True}), ("What it decides (Decision §1 "
            "and title)", 1000), ("Confirmation", 260), ("Module (one line; drawn in H8)", 560)]
    cols.append(("Evidence, 2026.11.10", WW - sum(cl[1] for cl in cols)))
    NB = "[[red|Floor entries not written · reference not built]]"
    rows = [
        ["ADR-0059", "A tree of planes, under charters that only narrow",
         "**A plane is seated by its parent's promotion under a charter it can only narrow**, is a havoc issuer "
         "bounded by that charter, carries commit certificates, and is fenced by every plane above it.",
         "[[amber|Proposed]] · C1", "`Federation`: a chain of three planes r → a → b, with four of §1's fields",
         ev("Federation") + ". `BudgetConserved` is stated for a subtree with no captured plane ⟨R1⟩. " + NB +
         " (`FD1`–`FD3`)"],
        ["ADR-0060", "The intent boundary and the autonomous plane",
         "**Every effect is admitted at the intent boundary**: a reversible one as an intent bounded by the promoted "
         "seating ⟨Q4⟩, an irreversible one singly by a person; **below it, an autonomous plane has no path that "
         "changes authority**.",
         "[[amber|Proposed]] · C1, C2", "`Intent`: the commanded plane orders intents, the autonomous plane grants "
         "leases under the live one",
         ev("Intent") + ". The module's plane is honest, and the intent was live when the effect's lease was granted "
         "⟨R1⟩. " + NB + " (`FD4`)"],
        ["ADR-0061", "Seven replicas, and a shrink schedule",
         "**An autonomous plane is seven replicas under Byzantine agreement with signed certificates**, and its "
         "membership shrinks only along a schedule its charter voted, 7, 6, 5, 4, down to a capture floor of one.",
         "[[amber|Proposed]] · C1", "`Membership`: five replicas, one plane; PBFT abstracted to its certificate",
         "**At five replicas, not §1's seven** ⟨R1⟩: " + ev("Membership") + ". [[red|PBFT not read · no "
         "measurement of a round · reference not built]]"],
        ["ADR-0062", "The lease pre-authorizes",
         "**A governor on each vehicle permits each entry under the lease against an exact count**, every entry "
         "declares an extent, and **a vehicle that stops hearing its plane loses its lease at once**.",
         "[[amber|Proposed]] · C1, C2", "`Alone`: one vehicle, one governor, one stack; the rest of §11 is in "
         "`Intent`, `PlaneClock` and `Release`",
         "Across four modules. `Alone`: " + ev("Alone") + ". " + NB + " (`FD7`, `FD8`, `FD11`, `FD14`)"],
        ["ADR-0063", "Revocation bounded in effects",
         "**The intent boundary reads a plane's record and answers with watermarks**, and a plane, and each governor "
         "for itself, **may have `K_up` effects outstanding and no more**, a bound with no premise about time.",
         "[[amber|Proposed]] · C1", "`Outstanding`: no variable or guard is a time",
         ev("Outstanding") + ". §4's argument as corrected is what is proved, **read by its author only**. " + NB +
         " (`FD10`)"],
        ["ADR-0064", "The plane's clock is its ticks",
         "**Ticks numbered from the charter, each signed by a quorum of replicas on their own clocks**, with every "
         "interval a count of ticks from a named tick; **a governor's own clock decides only that a tick is "
         "overdue**.",
         "[[amber|Proposed]] · no criterion applies", "`PlaneClock`: explicit discrete time; clocks sound, slow, fast "
         "or captured",
         "**In discrete time and under §4's premise**: " + ev("PlaneClock") + ". A declared bound, not a safety "
         "theorem. [[red|The Lean arithmetic is not met · reference not built]]"],
        ["ADR-0065", "Peer topics",
         "**Stacks report to each other on topics promoted with the mesh**: a send is permitted and never ordered, "
         "receipt is labelled ingress, and **nothing a peer originates enables anything**.",
         "[[amber|Proposed]] · C2", "`Peer`: one receiving governor; the radio belongs to the adversary",
         ev("Peer") + ". " + NB + " (`FD12`, and its monotonicity in what peers sent)"],
        ["ADR-0066", "An irreversible effect is a person's",
         "**An entry declares its effect class, and a `release` seat held by a person at a commanded plane is the "
         "only kind that reaches an irreversible entry**; each act is one admit, used once and fresh by the plane's "
         "ticks.",
         "[[amber|Proposed]] · C1 · provisional while ADR-0052 is", "`Release`: one commanded and one autonomous "
         "plane, two vehicles, one person, one agent",
         ev("Release") + ". " + NB + " (`FD5`, `FD6`, `FD9`, and `B10`'s relaxation)"],
        ["ADR-0067", "Rules of engagement in three places",
         "**Standing rules in the one Cedar floor, a mission's rules in a promoted Wasm bundle, and judgments about "
         "the world nowhere in the admit path**; the floor gains a `federation` stage of fourteen forbids.",
         "[[amber|Proposed]] · C1", "[[grey|None]]: no Cedar is written",
         "[[red|Nothing written as policy, gated, modelled or built.]] No floor is ratified, so nothing here can be in "
         "force (§5). R1 changed `FD10`'s governor clause only"],
        ["ADR-0068", "Adversaries, trusted-base rows, assumptions",
         "**The overlay declares fourteen adversaries** with what bounds each and what is left, **twelve trusted-base "
         "rows** classed by failure direction, and **ten assumptions of use**.",
         "[[amber|Proposed]] · C2", "[[grey|None]]: declarative",
         "**Its §6 reads \"Not met: no module is written\"**, and it has no R1 row, though the eight modules above "
         "exist. [[red|No row read against ADR-0045's test; four rows are trust roots nothing issues (finding 1); no "
         "row tested against a vehicle]]"],
    ]
    rows = [{"cells": r, "accent": "amber"} for r in rows]
    t = c.table(X0, y, cols, rows, size=14, accent="amber")
    y += t + 16
    y += c.para(X0, y, WW, "**Every ratification condition still owes** its floor entries (ADR-0067), the reference, "
                "and a reader who is not the drafter (ADR-0029 A2); ADR-0059's also owes ADR-0058's ratification. Each "
                "record but ADR-0059 is ratified only with or after the records it depends on. Totals over the eight "
                "modules: %d TLC rows, all as expected; %s obligations proved; %d LS4 temporal steps that no checker "
                "confirms." % (ROWS, f"{OBL:,}", LS4), 14, "muted")
    y += 80

    # ================================================================== band 3: postures
    y = band(c, X0, y, "Where each effect is admitted, and the posture it runs under (ADR-0060 §1, §3, §5; ADR-0062 "
             "§5; ADR-0066 §4)", status="proposed")
    top = y
    LW = 2050
    g = 50
    RW = WW - LW - g
    RXc = X0 + LW + g
    c.text(X0, top + 16, "**ADR-0060 §1's table, whole: every effect is admitted at the intent boundary** ⟨10⟩", 16,
           "ink")
    t1 = c.table(X0, top + 30, [("Effect", 170, {"bold": True}), ("What is admitted at the intent boundary", 680),
                                ("By whom", 420), ("What happens below", LW - 1270)], [
        {"cells": ["Reversible", "An **intent**: a task, an envelope, a budget of activations and an expiry",
                   "The commander, an operator",
                   "The autonomous plane grants each lease inside the intent (ADR-0062)"], "accent": "blue"},
        {"cells": ["Irreversible", "The effect itself, one at a time", "A person at a release seat (ADR-0066)",
                   "The plane relays it. It can refuse one and cannot originate one"], "accent": "brown"},
    ], size=14.5, accent="blue")
    py = top + 30 + t1 + 18
    py += c.para(X0, py, LW, "**This keeps ADR-0015's sentence one level up**: every effect has a consensus-ordered, "
                 "signed, authorizing predecessor, and here it is the intent. **What is admitted for a reversible "
                 "effect is an envelope, and not the act.** The predecessor is ordered before the effect and need "
                 "not be live at it ⟨R1⟩; ADR-0063 bounds how many effects follow its end.", 14, "muted") + 26
    c.text(X0, py + 16, "**The postures, by effect and by what the vehicle hears** (assembled from the records "
           "cited in each cell)", 16, "ink")
    t2 = c.table(X0, py + 30, [("Effect", 170, {"bold": True}),
                               ("Plane in contact with the intent boundary", 620),
                               ("Plane cut off from the intent boundary", 660),
                               ("Vehicle alone: no tick of its plane that is not overdue", LW - 1450)], [
        {"cells": ["Reversible",
                   "[[blue|HOTL]]. A lease under an intent, and the intent boundary reads the record as it is made "
                   "(ADR-0060 §5; ADR-0063 §1)",
                   "[[amber|Unattended]], which A5 says \"the pattern does not model\". **Nothing a cut-off plane "
                   "does may rest on a person's response**: fewer than `K_up` effects outstanding, then it stops "
                   "granting (ADR-0060 §5; ADR-0063 §5)",
                   "[[red|No actuation]]. The lease ends at once. It keeps its terminal behaviour, listening, and a "
                   "beacon within its count (ADR-0062 §5; `FD11`)"], "accent": "blue"},
        {"cells": ["Irreversible",
                   "[[brown|HITL]], and it needs the link. A person's signed act per effect, ordered at a commanded "
                   "plane, fired by the interlock (ADR-0066 §1, §4)",
                   "[[red|None is ordered]]: with no link no act is ordered. **An act that crossed the link before "
                   "the cut can still fire inside its freshness** ⟨R1⟩ (ADR-0066 §4)",
                   "[[red|No actuation]] (ADR-0062 §5). No irreversible entry is `local` (ADR-0062 §3; ADR-0066 "
                   "§1)"], "accent": "brown"},
    ], size=14.5, accent="grey")
    lb = py + 30 + t2 + 16
    lb += c.para(X0, lb, LW, "**With no link no irreversible effect can be ordered**, and an adversary who jams the "
                 "link gets that for nothing: **presented as a cost, and accepted** (ADR-0066, Consequences). An "
                 "adversary that cuts one vehicle from its plane gets its terminal behaviour within a tick period "
                 "(ADR-0062, Consequences).", 14, "muted")

    c.text(RXc, top + 16, "**ADR-0060 §3's table, whole: the autonomous plane is defined by one absence** ⟨11⟩ ⟨Q2⟩",
           16, "ink")
    t3 = c.table(RXc, top + 30, [("Absent", RW * 0.42), ("Present", RW * 0.58)], [
        ["[[red|Build]]: no authoring and no promotion",
         "The admit path, for a grant and for an `ordered` entry (ADR-0062)"],
        ["[[red|Grant seats, operators, release seats]]: no person",
         "The lease, the floor, every bundle on the chain, the fences"],
        ["[[red|Anchor issuance, new bundles, seating of planes]]",
         "The workflow interpreter: a mesh, its activations and its budget"],
        ["[[red|Any grant but one]]",
         "**One grant:** a node's lease, made by the mechanism under a live intent, \"with every field the seating's "
         "or narrower\" (ToO §2.11)"],
        ["", "Subtraction: the end of a round, a revocation, an Observer's finding, expiry"],
        ["", "A step of its charter's shrink schedule (ADR-0061)"],
    ], size=14.5, accent="violet")
    rb = top + 30 + t3 + 16
    rb += c.para(RXc, rb, RW, "**A claim about an honest plane's log** ⟨R1⟩. A captured plane is a havoc issuer: it "
                 "can sign a lease under an intent that has ended, and what bounds it is the chain check and "
                 "ADR-0063. **It is a declared degeneracy and an addition, not a second pattern** ⟨Q2⟩: it omits Build, "
                 "the people and Kafka, and its charters, commit certificates and operation with no person present "
                 "are capabilities the archetype lacks (§4).", 14, "muted")
    y = max(lb, rb) + 80

    # ================================================================== band 4: upstream
    y = band(c, X0, y, "What each record reports upstream, and what the archetype's records would owe if it takes "
             "them (each record's overlay-position section; ADR-0058 §6)", status="proposed")
    y += c.para(X0, y, WW, "**ADR-0023 §4: a variation that holds a capability the archetype lacks is not a rung, and "
                "the archetype is incomplete.** So each record is drafted as an overlay's, and what it adds is reported "
                "upstream as a finding about the archetype. **None of this is owed while it is an overlay**: every "
                "record \"carries a debt against nothing\".", 14.5, "muted") + 18
    cols = [("Record", 120, {"bold": True}), ("Reported upstream under ADR-0058 §6", 920),
            ("If the archetype takes them, its records owe", 0), ("C3 on admission (Status note)", 600)]
    cols[2] = (cols[2][0], WW - 120 - 920 - 600)
    up = [
        ["ADR-0059 §8",
         "**A mechanism that grants below itself**, bounded by a charter; **commit certificates** a third party can "
         "check with no plane in reach; **a fence that names every plane on a chain**",
         "ADR-0054's sentence on delegation and ToO §2.11, restated; ADR-0024 A3, a charter among the seatings a tally "
         "votes; ADR-0031, the lease's fence as one per plane on the chain; ADR-0045, its decision not to require "
         "Byzantine agreement, reversed for exposed planes. **A one-plane deployment would then be a declared "
         "degeneracy**",
         "[[red|C3]]: ADR-0045's decision reversed for exposed planes", "red"],
        ["ADR-0060 §6",
         "**Operation with no person seated**; **a grant by one operator bounded by a seating and not by the last "
         "lease**",
         "ADR-0050, the successor bound for intents (§2); ADR-0054, a person in an orchestrator seat; ADR-0037, the "
         "seat kinds; ADR-0055, where a mesh runs; A5 and ToO §13, restated for a plane with nobody in reach",
         "[[red|C3]]: §2 changes what bounds a successor grant under ADR-0050 (accepted, provisional)", "red"],
        ["ADR-0061 §6",
         "**A membership that changes at run time by a voted schedule**",
         "ADR-0045, the replica row for an exposed plane and the reconfiguration step with it; ADR-0024, a statement "
         "of how §3 stands beside \"a timeout is never a grant\"",
         "[[red|C3]]: ADR-0045 declined to require Byzantine agreement, and §3 strains ADR-0024's constant", "red"],
        ["ADR-0062 §10",
         "**A trusted component that permits, away from the replicas**; **an entry's extent**",
         "ADR-0015, its sentence on predecessors, and ADR-0033 §4, void, each for a `local` entry; ADR-0039 and "
         "ADR-0041, coupling at the grant; ADR-0049, the `effect` part; ADR-0031, a count in the lease and an ending "
         "when its holder stops hearing the mechanism; ADR-0034 A2, the radio as a declared channel",
         "[[red|C3]]: §2 gives up ADR-0015's ordered admit before every effect, and §6 ADR-0033 §4's void, for the "
         "entries a governor permits", "red"],
        ["ADR-0063 §7",
         "**Liveness coupled to admission between planes**; **a record read as it is made**",
         "ADR-0039, coupling restated for a plane and its parent; ADR-0031, a grant condition on what is outstanding; "
         "ADR-0005 and the archive, a record that goes up in segments with a receipt",
         "[[green|Does not apply, and this is the point]]: ADR-0032's first clause is kept (§6)", "green"],
        ["ADR-0064 §7",
         "**A clock that is a quorum's fact and a log quantity**",
         "ADR-0032, a third row beside \"local clock\" and \"trusted time\", for an interval read by a quorum of local "
         "clocks; ADR-0031, a `ttl` in ticks for a plane that has them; ADR-0045, the clock's row and finding 2, "
         "restated for §5's residual",
         "Does not apply: ADR-0032 is kept, with a residual (§5). No criterion applies", "grey"],
        ["ADR-0065 §8",
         "**An emission that is permitted and not ordered**; **ingress that arrives unasked**",
         "ADR-0055 §7, the one sentence; ADR-0015, an emission with a permit and no ordered admit; ADR-0040, a "
         "`Report` to a topic that is not the principal's own round topic; ADR-0043, a sixth item of ingress; "
         "ADR-0047, its label",
         "Does not apply while an overlay; ADR-0055, whose §7 it changes, is Proposed", "grey"],
        ["ADR-0066 §6",
         "**An effect class on an entry**; **an irreversible effect expressible by a person**",
         "ADR-0032 §4, relaxed from \"not reachable at all\" to \"reachable by a person and by nobody else\"; "
         "ADR-0037, the seat kind `release`; ADR-0049, the entry's `effect` part; the floor's "
         "`B10-only-thinkers-author`, an exception for a `release` seat's `Actuate`, as it has for an `emergency` seat",
         "[[red|C3]]: ADR-0032 §4 says such an effect \"must not be reachable from the alphabet at all\"", "red"],
        ["ADR-0067",
         "[[grey|No overlay-position section.]] Its deployment position is an overlay ⟨Q11⟩, and it carries no debt "
         "while one",
         "No list of its own. Its §4 gives `B10-only-thinkers-author` an exception for a `release` seat's `Actuate`, "
         "scopes `R3-observer-live` to admits a plane makes, and grows the schema; each relaxation routes as one "
         "(ToO §3.2)",
         "Does not apply on the drafter's reading while an overlay", "grey"],
        ["ADR-0068 §5",
         "[[grey|No list of its own.]] Finding 2: an overlay that adds twelve rows is outside ADR-0045 §4's sentence, "
         "one more reason it is reported upstream and not declared as a rung",
         "**If the archetype takes ADR-0059 to ADR-0067**: ADR-0045, these rows in its table and a declaration of "
         "them in every deployment that seats a governor; ToO §13, these assumptions beside A1 to A18",
         "Does not apply on the drafter's reading while an overlay", "grey"],
    ]
    t = c.table(X0, y, cols, [{"cells": r[:4], "accent": r[4]} for r in up], size=14, accent="amber")
    y += t + 16
    y += c.para(X0, y, WW, "**Five records would need C3 on admission** (ADR-0059, ADR-0060, ADR-0061, ADR-0062, "
                "ADR-0066): each reverses or relaxes accepted text. ADR-0068's Options keep its rows out of ADR-0045 "
                "while this is an overlay, since ADR-0045 is accepted and an annex would amend it.", 14, "muted")
    y += 80

    # ================================================================== band 5: what is given up
    y = band(c, X0, y, "What is given up, in one place (ADR-0068 §4, whole)", status="proposed")
    y += c.para(X0, y, WW, "**Each record names its own costs. Together:**", 15, "ink") + 12
    GU = [
        ("1. No delegation", ["Planes grant below themselves (ADR-0059)."]),
        ("2. A bound in seconds as a theorem", ["Revocation is bounded in effects, and the bound in duration is "
                                                "declared (ADR-0063, ADR-0064)."]),
        ("3. An ordered admit before every effect", ["For every pre-authorized entry and every report to a peer "
                                                     "(ADR-0062, ADR-0065)."]),
        ("4. A person in reach", ["For a plane that is cut off (ADR-0060)."]),
        ("5. Any act by a vehicle that is alone", ["(ADR-0062)."]),
        ("6. Inexpressibility of irreversible effects", ["(ADR-0066)."]),
        ("7. A small trusted base", ["(§2.)"]),
        ("8. A fixed capture threshold", ["(ADR-0061)."]),
        ("9. One bus", ["(ADR-0065)."]),
        ("10. \"Not autonomous.\"", ["No principal seats, delegates to or addresses another, and that stays true. "
                                     "**It is no longer true that a person is always on the plane that orders an "
                                     "effect.**"]),
    ]
    h1, _, _ = row_cards(c, X0, y, WW, 24, [(t_, b_, "red", {"tint": False, "bullets": False}) for t_, b_ in GU[:5]],
                         size=14.5)
    y += h1 + 20
    h2, _, _ = row_cards(c, X0, y, WW, 24, [(t_, b_, "red", {"tint": False, "bullets": False}) for t_, b_ in GU[5:]],
                         size=14.5)
    y += h2 + 18
    c.para(X0, y, WW, "Item 7's §2 is ADR-0068's own: twelve trusted-base rows, and \"the base still grows, on every "
           "vehicle\". For items 5, 6, 8 and 9 the record gives the title and the citation only.", 13.5, "muted")
    return c
