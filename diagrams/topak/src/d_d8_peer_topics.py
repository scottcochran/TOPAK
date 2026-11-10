"""D8 — Stacks report to each other on topics promoted with the mesh: a send is permitted and never ordered, receipt is
labelled ingress, and nothing a peer originates enables anything (ADR-0065, Proposed, revised R1; an overlay, not the
archetype). `spec/Peer.tla` is checked and proved; the floor entry is not written and the reference is not built."""
from lib import Canvas, STATUS, STATE_CC, text_width

ID, SLUG = "D8", "peer-topics"

W = 3400


def row_cards(c, x, y, w, gap, specs, size=14):
    """A row of cards of equal height, measured over every card. specs: (title, body, accent, kwargs)."""
    n = len(specs)
    cw = (w - (n - 1) * gap) / n
    h = max(c.card(0, 0, cw, t, b, draw=False, size=size, status=k.get("status"), bullets=k.get("bullets", True))
            for t, b, _, k in specs)
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
    c = Canvas(ID, "Stacks report to each other on topics promoted with the mesh: a send is permitted and never "
               "ordered, receipt is labelled ingress, and nothing a peer originates enables anything",
               "ADR-0055 left one path for information between vehicles, a log ordered by Byzantine agreement, and no "
               "rate for it (Context; the swarm reading, Z1). The custodian asked whether stacks may talk in the "
               "autonomous layer ⟨15⟩. **The drafter's answer was yes, with one correction: a send still needs a "
               "permit. What it does not need is an order** (\"Ordering is not authorization\", ToO §4.1), and the "
               "custodian took both halves ⟨16⟩ ⟨17⟩. **ADR-0065 is Proposed and an overlay, not the archetype.** "
               "`spec/Peer.tla` is checked and proved (R1); the floor entry `FD12` is not written and the reference is "
               "not built, so **nothing here is in force**.",
               W, "ADR-0065 (Proposed 2026.11.10, revised R1): provenance note, Status note, Context, Decision §1–§9 "
               "(§1's table of three kinds of traffic), Options considered (the whole table), Consequences, Open "
               "obligations, History (initial draft and R1); ADR-0055 §7 (Proposed; \"the mechanism is the bus\"), as "
               "drawn in D6; ADR-0047 §1, §2, §4, §7 (labels, `clearSet`, clear and handle, F1 to F3 as `R5` to `R7`), "
               "as drawn in C6; ADR-0043 §1 with A1 and A3 (pending), the Listener's closed list; ADR-0062 §1, §3, §5, "
               "§6 (Proposed); ADR-0063 §3 (Proposed); ADR-0067 §3 (`FD12-topic-declared`) and §7 (Proposed); "
               "ADR-0058 §6 (Proposed); ADR-0040 status; spec/Peer.tla (5ee3528164cd1a35), its header comment and "
               "definitions; spec/Peer-rows.txt (25 rows); spec/Peer-results-2026.11.10.txt (d3b80c6f31ca83e8); "
               "spec/Peer_proof.tla (3c661ef57179a03c); spec/Peer-proof-results-2026.11.10.txt (f5678d36db4e1127); "
               "spec/Peer-proof-cert-results-2026.11.10.txt (12677112bade3a44). The picture's three vehicles are an "
               "illustration of §1 to §3 and §6; the module has one receiving governor and one honest sender",
               state=STATE_CC)
    X0, X1 = c.x0, c.x1
    WW = X1 - X0
    y = c.y

    # ================================================================== status strip
    c.text(X0, y + 15, "Status", 15, "faint", bold=True)
    px0 = X0 + 80
    px = px0
    for lab, key, extra, pill in [
            ("ADR-0065", "proposed", "C2 · R1 · 2026.11.10", None),
            ("deployment position", None, "", ("An overlay, not the archetype ⟨Q11⟩", "amber", "6 4")),
            ("rests on ADR-0055 §7", "proposed", "\"the mechanism is the bus\" · D6", None),
            ("ADR-0062, ADR-0063, ADR-0058", "proposed", "", None),
            ("spec/Peer.tla", None, "", ("Checked · 25 rows, all as expected", "teal", None)),
            ("spec/Peer_proof.tla", None, "", ("Proved · 254 obligations", "teal", None)),
            ("", None, "", ("Certified, with 6 LS4 temporal steps that no checker confirms", "teal", None)),
            ("`FD12-topic-declared`, and the stage shown monotone (ADR-0067)", None, "",
             ("Not written", "red", "2 3")),
            ("the reference (§9)", "notbuilt", "", None)]:
        lw = (text_width(lab, 13.5, True) + 8) if lab else 0
        plab = pill[0] if pill else STATUS[key][0] + (f" · {extra}" if extra else "")
        pw = text_width(plab, 11.5, True) + 18
        if px + lw + pw > X1:
            px = px0
            y += 34
        if lab:
            c.text(px, y + 15, f"**{lab}**", 13.5, "ink")
        px += lw
        if pill:
            px += c.pill(px, y, pill[0], pill[1], 11.5, dash=pill[2]) + 26
        else:
            px += c.status(px, y, key, extra) + 26
    y += 42
    y += c.para(X0, y, WW, "**Proposed means nothing here is in force.** Confirmation is required under **C2**: Run's "
                "ingress is a closed list and its effects are enumerated, and this record adds an item to the first and "
                "an unordered emission to the second. **C3 does not apply while this is an overlay** ⟨Q11⟩, and "
                "ADR-0055, whose §7 it changes, is Proposed; C1 and C4 do not apply (Status note). **Modelled, checked "
                "and proved in TLA+ ⟨R1⟩; nothing is built.** The custodian decided ⟨15⟩, ⟨16⟩, ⟨17⟩, ⟨21⟩ and answered "
                "⟨Q19⟩, ⟨Q11⟩; every other choice is the drafter's. **One author, one day.**", 14.5, "muted") + 40

    # ================================================================== band 1: the picture
    y = band(c, X0, y, "Three vehicles, one peer topic and the plane: what travels by talk and what by order "
             "(§1–§3, §6)", status="proposed", extra="nothing here is built")
    S = 14
    g = 192
    cw = [480, 540, 520, 540, 480]
    g = (WW - sum(cw)) / 4
    cx = [X0]
    for w_ in cw[:-1]:
        cx.append(cx[-1] + w_ + g)
    rt = y + 30
    ct = rt + 80

    A_STACK = ("Vehicle A's stack: the Thinker, Byzantine", [
        "**Reports to a topic and names no recipient** (§4): tracks, plans, bids for a task (§1).",
        "The report is a `Report` (ADR-0040) to a peer topic, which is not the principal's own round topic (§8).",
        "**It cannot make its own vehicle alone**: the radio is on the governor's side (ADR-0062 §1).",
    ], "grey")
    A_CAPT = ("If vehicle A is captured", [
        "**Its governor may write any labels on what it sends** (§3 ⟨R1⟩), and may lie about what it measures (§1).",
        "**Its chain is not evidence**: it says what its captor signed (ADR-0062 §6).",
        "The receiver's two names survive it, and its measured facts can only stop others.",
    ], "red")
    A_SEND = ("① Permits the send: an effect, not ordered (§2) ⟨16⟩", [
        "**Permitted under the floor and the bundles**, to a topic the mesh declares for the seat.",
        "**The rules of engagement can refuse it**: silence, a rate, a label.",
        "**A count of its own per lease.** Not ordered, and **not charged to `K_up`** (ADR-0063), or chatter would "
        "spend the plane's authority.",
    ], "teal")
    A_ORD = ("Or waits for a round: an `ordered` entry (§6; ADR-0062 §3)", [
        "Marked so by the bundle where the tally wants agreement across vehicles. **The archetype marks none** ⟨Q20⟩.",
    ], "teal")
    A_CHAIN = ("Records the send by digest on the vehicle's chain (§2)", [
        "**As ADR-0020 records a denial**: hash-linked, signed with the vehicle's key, numbered by the per-lease "
        "sequence (ADR-0062 §6).",
        "**Closed at the lease's end**, and the plane orders the seal as one entry.",
    ], "teal")
    TOPIC = ("② A peer topic, declared by the mesh (§4) ⟨17⟩", [
        "**Promoted with the mesh**: its schema, which seat kinds may report to it, which nodes hear it, its label and "
        "its delivery mode.",
        "**Nobody is addressed**, so \"Workers never address each other\" (ADR-0055 §7) stays true.",
        "A report on a topic a seat does not hear is not delivered to it: `Peer.tla`'s `Drop`.",
    ], "amber")
    C_GOV = ("Vehicle C's governor: in range, a relay and a witness", [
        "**Relays certified facts it heard**: fences, revocations, ticks, intents, leases, watermarks. **The peer is "
        "transport and originates nothing** (§1).",
        "**Measures facts of its own**: its position, a range. A captured governor may lie about them (§1).",
        "Its stack may report on the same topics. A vehicle that is alone keeps listening, so a relayed fence still "
        "applies (ADR-0062 §5).",
    ], "teal")
    B_DEL = ("③ Delivers the report as labelled ingress (§3) ⟨Q19⟩", [
        "**Adds `untrusted`, always, and the topic's name**, whatever the sender declared.",
        "**Clear**, it joins `clearSet`; **as a handle**, it is routed and not read.",
    ], "teal")
    B_CERT = ("Applies a certified fact on receipt (§1)", [
        "**Verifies its certificate against the chain**, and applies it. A subtraction applies before it is ordered "
        "anywhere.",
    ], "teal")
    B_MEAS = ("May refuse on a measured fact, never permits on it (§1)", [
        "**A captured governor that lies can only stop others.**",
    ], "teal")
    B_PERM = ("④ Permits an entry under its lease (§1 ⟨R1⟩)", [
        "**Still permitted with every item a peer originates removed, or any subset of them.**",
        "**A lease that reached it by relay does enable its permit**: it is the plane's act, not the peer's.",
    ], "teal")
    B_STACK = ("Vehicle B's stack: the Thinker, Byzantine", [
        "**The report is a sixth item on the Listener's closed list** (§3; ADR-0043 §1).",
        "**Chooses among entries its lease already permits: which, never whether** (§4).",
        "**Nothing rests on its reading the report** (§5). Every effect it then requests is checked without reference "
        "to the report (§1).",
    ], "grey")

    def mh(spec, w_, **k):
        return c.card(0, 0, w_, spec[0], spec[1], draw=False, size=S, **k)

    gv = 22
    # column 0
    h_as = mh(A_STACK, cw[0])
    h_ac = mh(A_CAPT, cw[0])
    y_ac = ct + h_as + 40
    # column 1: A's governor
    h_s, h_o, h_ch = mh(A_SEND, cw[1]), mh(A_ORD, cw[1]), mh(A_CHAIN, cw[1])
    y_s = ct
    y_o = y_s + h_s + gv
    y_ch = y_o + h_o + gv
    # column 2: the topic, then C
    h_t = mh(TOPIC, cw[2])
    # column 3: B's governor
    h_d, h_ce, h_m, h_p = mh(B_DEL, cw[3]), mh(B_CERT, cw[3]), mh(B_MEAS, cw[3]), mh(B_PERM, cw[3])
    y_d = ct
    y_ce = max(y_d + h_d + gv, ct + h_t + 24 + 80)
    y_m = y_ce + h_ce + gv
    y_p = y_m + h_m + gv
    h_c = max(mh(C_GOV, cw[2]), y_p + h_p - y_ce)
    y_c = y_ce
    h_bs = mh(B_STACK, cw[4])

    a_bot = max(y_ac + h_ac, y_ch + h_ch) + 30
    b_bot = max(y_p + h_p, ct + h_bs) + 30
    c_bot = y_c + h_c + 30
    # regions
    c.region(cx[0] - 24, rt, cx[1] + cw[1] + 24 - (cx[0] - 24), a_bot - rt, "Vehicle A: a stack, and a governor that "
             "holds the radio (ADR-0062 §1)", "grey", dash="10 6")
    c.region(cx[1] - 14, ct - 30, cw[1] + 28, y_ch + h_ch + 14 - (ct - 30), "A's governor · mechanism", "teal",
             dash=None, size=13)
    c.region(cx[2] - 24, rt, cw[2] + 48, ct + h_t + 24 - rt, "The mesh's peer topics", "amber", dash="6 4")
    c.region(cx[2] - 24, y_c - 46, cw[2] + 48, c_bot - (y_c - 46), "Vehicle C", "grey", dash="10 6")
    c.region(cx[3] - 24, rt, cx[4] + cw[4] + 24 - (cx[3] - 24), b_bot - rt, "Vehicle B: the receiver",
             "grey", dash="10 6")
    c.region(cx[3] - 14, ct - 30, cw[3] + 28, y_p + h_p + 14 - (ct - 30), "B's governor · mechanism", "teal",
             dash=None, size=13)

    c.card(cx[0], ct, cw[0], A_STACK[0], A_STACK[1], accent=A_STACK[2], size=S, tint=False)
    c.card(cx[0], y_ac, cw[0], A_CAPT[0], A_CAPT[1], accent=A_CAPT[2], size=S, tint=False, dash="6 4")
    c.card(cx[1], y_s, cw[1], A_SEND[0], A_SEND[1], accent="teal", size=S)
    c.card(cx[1], y_o, cw[1], A_ORD[0], A_ORD[1], accent="teal", size=S)
    c.card(cx[1], y_ch, cw[1], A_CHAIN[0], A_CHAIN[1], accent="teal", size=S)
    c.card(cx[2], ct, cw[2], TOPIC[0], TOPIC[1], accent="amber", size=S, h=h_t)
    c.card(cx[2], y_c, cw[2], C_GOV[0], C_GOV[1], accent="teal", size=S, h=h_c)
    c.card(cx[3], y_d, cw[3], B_DEL[0], B_DEL[1], accent="teal", size=S)
    c.card(cx[3], y_ce, cw[3], B_CERT[0], B_CERT[1], accent="teal", size=S)
    c.card(cx[3], y_m, cw[3], B_MEAS[0], B_MEAS[1], accent="teal", size=S)
    c.card(cx[3], y_p, cw[3], B_PERM[0], B_PERM[1], accent="teal", size=S)
    c.card(cx[4], ct, cw[4], B_STACK[0], B_STACK[1], accent="grey", size=S, tint=False)

    # the plane
    pt = max(a_bot, b_bot, c_bot) + 130
    pct = pt + 44
    pg = 30
    pw = (WW - 48 - 3 * pg) / 4
    pxs = [X0 + 24 + i * (pw + pg) for i in range(4)]
    P = [
        ("Agreement is an `ordered` entry (§6) ⟨21⟩", [
            "**One round, and every vehicle sees the same outcome.** Where the tally wants one vehicle and no more, "
            "only this will do.",
            "**Talk waits for no round, and two stacks may claim the same task.**",
        ], "violet", {}),
        ("The seal: a chain ordered as one entry (ADR-0062 §6)", [
            "The plane runs the mechanism checks at its position. **A check that fails is a finding, and it can only "
            "subtract.**",
            "**Delivery records reach the plane only at the seal** (Consequences).",
        ], "violet", {}),
        ("Certified facts are the plane's acts (§1)", [
            "Fences, revocations, ticks, intents, leases, watermarks, **verified against the chain wherever they "
            "arrive**.",
            "**A fence reaches any vehicle in range of one that heard it.**",
        ], "violet", {}),
        ("What the plane never sees in time: a send (§2, §5)", [
            "**Not ordered**: a round per message, for an effect that can enable nothing (Options).",
            "**Not charged to `K_up`**: the charge is on `local` and `ordered` entries (ADR-0063 §3).",
        ], "red", {"tint": False, "dash": "6 4"}),
    ]
    ph = row_cards(c, X0 + 24, pct, WW - 48, pg, P, size=S)
    c.region(X0, pt, WW, ph + 44 + 30, "The plane and its log (ADR-0062 §3, §6) · Proposed", "violet", dash=None)

    # ---- arrows: the report lane
    lane = ct + 46
    c.arrow([(cx[0] + cw[0], lane), (cx[1], lane)], "grey", sw=2.6, label="`Report`", lpos=0.5)
    c.arrow([(cx[1] + cw[1], lane), (cx[2], lane)], "teal", sw=2.6, label="permitted", lpos=0.5)
    c.arrow([(cx[2] + cw[2], lane), (cx[3], lane)], "amber", sw=2.6, label="heard", lpos=0.5)
    c.arrow([(cx[3] + cw[3], lane), (cx[4], lane)], "teal", sw=2.6, label="labelled", lpos=0.5)
    # C to B's governor
    for yy, acc, dash, lab in [(y_ce + h_ce / 2, "green", "7 5", "fence"),
                               (y_m + h_m / 2, "red", "7 5", "position"),
                               (y_p + h_p / 2, "violet", None, "lease")]:
        c.arrow([(cx[2] + cw[2], yy), (cx[3], yy)], acc, sw=2.4, dash=dash, label=lab, lpos=0.5)
    # B's stack requests an entry
    bsx = cx[4] + 70
    c.arrow([(bsx, ct + h_bs), (bsx, y_p + h_p / 2), (cx[3] + cw[3], y_p + h_p / 2)], "grey", sw=2.4,
            label="requests an entry", lpos=0.35)
    # the plane's paths
    ax = cx[1] - g / 2
    c.arrow([(cx[1], y_o + h_o / 2), (ax, y_o + h_o / 2), (ax, pct)], "violet", sw=2.4, both=True,
            label="one round", lpos=0.62)
    sx = cx[1] + cw[1] / 2
    c.arrow([(sx, y_ch + h_ch), (sx, pct)], "violet", sw=2.4, label="the seal, at the lease's end", lpos=0.5)
    cxu = max(cx[2] + cw[2] / 2, pxs[2] + 70)
    c.arrow([(cxu, pct), (cxu, c_bot - 30 + 0)], "violet", sw=2.4, label="certified facts", lpos=0.5)
    bx = cx[3] + cw[3] / 2
    c.arrow([(bx, pct), (bx, y_p + h_p)], "violet", sw=2.4, label="a lease, granted", lpos=0.5)

    fbot = pt + ph + 44 + 30 + 40
    lg = c.legend(X0, fbot, [
        ("arrow", "grey", "a stack's report or request"),
        ("arrow", "teal", "the governor permits or delivers"),
        ("arrow", "amber", "on a declared topic"),
        ("arrow", "violet", "the plane's act, relayed or not"),
        ("arrow", "green", "a relayed subtraction", "7 5"),
        ("arrow", "red", "a measured fact: refuses only", "7 5"),
        ("box", "red", "never ordered, never charged"),
    ])
    y = fbot + lg + 80

    # ================================================================== band 2: §1
    y = band(c, X0, y, "§1 · Nothing a peer originates is ever an enabling condition ⟨15⟩, as revised ⟨R1⟩",
             status="proposed")
    top = y
    gg = 50
    wl = 1000
    wr = WW - wl - gg
    xr = X0 + wl + gg
    bl = stack(c, X0, top, wl, [
        ("The property, as §1 states it after R1", [
            "**For every permit and every admit, at a plane or a governor, the same request with every item a peer "
            "originates removed is still permitted, and so is the same request with any subset of those items.**",
            "**A certified fact a peer relays is the plane's act and not the peer's**: a lease that reached a vehicle "
            "by relay does enable its permit, and it is not such an item.",
            "This is ADR-0047's direction, \"delivering more in the clear buys a narrower round\" (ToO §2.10), applied "
            "between vehicles.",
        ], "amber", {"status": "proposed", "status_extra": "⟨R1⟩"}),
        ("What R1 corrected: the literal reading is false", [
            "As drafted, §1 said \"every item **received from peers** removed\". **`Peer.tla`'s header finds it false "
            "read literally**: §1's table has a peer relay leases, and a vehicle whose lease reached it through a peer "
            "is permitted because of an item received from a peer.",
            "**The witness `NeverPermitUnderRelayedLease` is reached** (row `w-relayedlease`, VIOLATED as expected): "
            "a request is permitted under a lease a peer relayed. **So the literal reading is not a property of the "
            "mechanism**, and §1 now ranges over what a peer **originates** (History R1).",
        ], "red", {"tint": False}),
    ], gap=18, size=S)
    c.text(xr, top + 16, "**§1's table, whole: three kinds of traffic share the governors' radios**", 16, "ink")
    cols = [("Traffic", wr * 0.27), ("What the receiver does", wr * 0.37), ("Why it is safe", wr * 0.36)]
    t1 = c.table(xr, top + 32, cols, [
        {"cells": ["**Certified facts, relayed**: fences, revocations, ticks, intents, leases, watermarks",
                   "Its governor verifies the certificate against the chain and applies it. **A subtraction applies on "
                   "receipt, before it is ordered anywhere**",
                   "**The peer is transport and originates nothing.** A fence reaches any vehicle in range of one that "
                   "heard it"], "accent": "violet"},
        {"cells": ["**A governor's measured facts**: its position, a range",
                   "The receiving governor **may refuse on them and never permits on them**",
                   "**A captured governor that lies can only stop others**"], "accent": "red"},
        {"cells": ["**A stack's report**: tracks, plans, bids for a task",
                   "Its governor delivers it to its stack **as labelled ingress**",
                   "**The stack is Byzantine already**, and every effect it then requests is checked without reference "
                   "to the report"], "accent": "amber"},
    ], size=14.5, accent="amber")
    ty = top + 32 + t1 + 26
    c.text(xr, ty + 16, "**How `Peer.tla` states it**: a decision is a state function of the request and the items "
           "received, so it can be compared with and without them", 15, "ink")
    h2 = row_cards(c, xr, ty + 32, wr, 22, [
        ("`PeerAddsNothing`", [
            "Every request permitted is still permitted **with every item in `received` removed**.",
            "`received` holds what a peer originates and what subtracts. **A certified lease is the plane's act and "
            "sets `live`.**",
        ], "teal", {}),
        ("`NarrowsInReceived` ⟨R1⟩", [
            "Every request permitted is still permitted **with any subset of those items**: receipt only narrows.",
            "It is **added by R1** (§9), and is the monotonicity ADR-0067 §7 asks the stage to show.",
        ], "teal", {}),
        ("Under `M_PEERENABLES`", [
            "**A report enables one entry, `gated`**, which is in no alphabet.",
            "**Both properties break** (rows `m-enables-adds`, `m-enables-narrows`), and only they.",
        ], "red", {"tint": False, "dash": "6 4"}),
    ], size=S)
    y = max(bl, ty + 32 + h2) + 80

    # ================================================================== band 3: §2, §3 labels
    y = band(c, X0, y, "§2, §3 · Sending is an effect; receiving is ingress, labelled `untrusted` and by its topic "
             "⟨16⟩ ⟨Q19⟩", status="proposed")
    top = y + 30
    lc = [540, 520, 520, 560]
    lg_ = 110
    lx = [X0 + 24]
    for w_ in lc[:-1]:
        lx.append(lx[-1] + w_ + lg_)
    SH = ("An honest sender's governor", [
        "**May add names to a report's label, and removes none** ⟨R1⟩.",
    ], "teal")
    SC = ("A captured sender's governor", [
        "**May write what it likes**, `untrusted` left out included: `Peer.tla`'s witness `NeverSenderLabelledLow` "
        "(row `w-labellow`).",
    ], "red")
    RA = ("The receiver's governor adds two names", [
        "**`untrusted`, always**, which puts the report under the floor's label forbids.",
        "**The name the mesh declares for its topic**, which lets a mission's bundle refuse particular entries after "
        "particular topics.",
        "**These are the two names that survive capture.** A rule that must hold of a captured sender reads only "
        "them.",
    ], "teal")
    DL = ("The delivered label", [
        "`L ∪ {untrusted, Name[t]}`, as `Peer.tla`'s `DeliveredLabels` writes it, whatever `L` the sender declared.",
        "`ReceivedIsUntrusted` holds it of every delivered report. **`M_SENDERLABEL`, the sender's label taken as "
        "given, breaks it** (`m-label-untrusted`).",
    ], "teal")
    CL = ("Delivered clear: it joins `clearSet`", [
        "**So `R5` to `R7` follow it** (ADR-0047 §7, F1 to F3), and **listening narrows**: F1 to F3 are monotone in "
        "`clearSet`.",
        "A clear report labelled with a name a bundle forbids refuses an entry permitted without it "
        "(`NeverNarrowedByClear`, `w-narrowed`).",
    ], "green")
    HD = ("Delivered as a handle: routed, not read", [
        "**A bundle may deliver a topic as a handle to a seat kind that should route it and not read it** (§3).",
        "A handle adds nothing to `clearSet`: `egress` is still permitted after an `untrusted` report delivered as a "
        "handle (`NeverPermitAfterHandle`, `w-handle`).",
    ], "green")
    h_sh, h_sc = mh(SH, lc[0]), mh(SC, lc[0])
    h_ra, h_dl = mh(RA, lc[1]), mh(DL, lc[2])
    h_cl, h_hd = mh(CL, lc[3]), mh(HD, lc[3])
    lh = max(h_sh + 24 + h_sc, h_ra, h_dl, h_cl + 24 + h_hd)
    c.card(lx[0], top, lc[0], SH[0], SH[1], accent="teal", size=S)
    c.card(lx[0], top + lh - h_sc, lc[0], SC[0], SC[1], accent="red", size=S, tint=False, dash="6 4")
    ymid = top + lh / 2
    c.card(lx[1], ymid - h_ra / 2, lc[1], RA[0], RA[1], accent="teal", size=S)
    c.card(lx[2], ymid - h_dl / 2, lc[2], DL[0], DL[1], accent="teal", size=S)
    c.card(lx[3], top, lc[3], CL[0], CL[1], accent="green", size=S)
    c.card(lx[3], top + lh - h_hd, lc[3], HD[0], HD[1], accent="green", size=S, tint=False)
    # arrows
    ax0 = lx[0] + lc[0]
    mid01 = ax0 + lg_ / 2
    c.arrow([(ax0, top + h_sh / 2), (mid01, top + h_sh / 2), (mid01, ymid - 12), (lx[1], ymid - 12)], "teal", sw=2.4,
            label="`L`", lpos=0.3)
    c.arrow([(ax0, top + lh - h_sc / 2), (mid01, top + lh - h_sc / 2), (mid01, ymid + 12), (lx[1], ymid + 12)],
            "red", sw=2.4, dash="7 5", label="any `L`", lpos=0.3)
    c.arrow([(lx[1] + lc[1], ymid), (lx[2], ymid)], "teal", sw=2.4, label="∪", lpos=0.5)
    mid23 = lx[2] + lc[2] + lg_ / 2
    c.arrow([(lx[2] + lc[2], ymid - 12), (mid23, ymid - 12), (mid23, top + h_cl / 2), (lx[3], top + h_cl / 2)],
            "green", sw=2.4, label="clear", lpos=0.75)
    c.arrow([(lx[2] + lc[2], ymid + 12), (mid23, ymid + 12), (mid23, top + lh - h_hd / 2),
             (lx[3], top + lh - h_hd / 2)], "green", sw=2.4, label="handle", lpos=0.75)
    c.region(X0 - 0, top - 30, lx[3] + lc[3] + 24 - X0, lh + 54, "A report's label, from sender to round (§3 ⟨R1⟩; "
             "`Peer.tla`)", "teal", dash="10 6", size=13)
    # the Listener's list, and the send
    rx = lx[3] + lc[3] + 60
    rw = X1 - rx
    c.text(rx, top - 14, "**The Listener's closed list** (ADR-0043 §1), with this record's item", 15, "ink")
    tl = c.table(rx, top, [("#", 44, {"bold": True}), ("Item", rw * 0.5 - 44), ("From", rw * 0.5)], [
        ["1", "The task", "ADR-0043 §1"],
        ["2", "The content of each admitted `Consult`", "ADR-0043 §1"],
        ["3", "The result of each admitted `Actuate`", "ADR-0043 §1"],
        ["4", "The tool list, once at the start of the round", "ADR-0043 A1 (ADR-0048 §2)"],
        ["5", "`input`: a predecessor's output along an edge", "ADR-0043 A3, **pending, not applied** (ADR-0054, "
                                                                 "Proposed)"],
        {"cells": ["6", "**A report on a topic the seat is declared to hear**", "**ADR-0065 §3, Proposed**"],
         "accent": "amber"},
    ], size=13.5, accent="grey")
    c.para(rx, top + tl + 10, rw, "**No request leaves the membrane**, so receipt is not an `Actuate`, as a read of "
           "live state is (ToO §2.9). \"A sixth item, after ADR-0054's `input`\" counts an amendment that is still "
           "pending.", 13.5, "muted")
    y = top + max(lh + 30, tl + 80) + 40
    # §2 the send, as a row
    y += row_cards(c, X0, y, WW, 24, [
        ("A send is a `Report` to a declared topic, permitted by the governor (§2)", [
            "**ADR-0015 counts an emission as an effect**, and a transmission reveals the vehicle and can carry "
            "`restricted` content.",
            "Permitted under the floor and the bundles; **the rules of engagement can refuse it**: silence, a rate, a "
            "label.",
        ], "teal", {}),
        ("It is not ordered and not charged to `K_up` (§2)", [
            "**Or chatter would spend the plane's authority** (ADR-0063). It has a count of its own per lease.",
            "**It is recorded by digest** on the vehicle's chain (ADR-0062 §6), as ADR-0020 records a denial.",
        ], "teal", {}),
        ("What `Peer.tla` shows of a send", [
            "**An honest governor sends only to a topic the mesh declares for the seat**: `SendWithinTopics`. "
            "`M_ANYTOPIC` breaks it (`m-topic-send`).",
            "A send to an undeclared topic is refused (`w-refdecl`), one to a topic a bundle silences is refused "
            "(`w-refbundle`), and a send happens (`w-sent`).",
        ], "teal", {}),
        ("Not modelled", [
            "**The record by digest**, and the lease's end: `live` only rises.",
            "**Whether a report is read**, and what a stack does with it: §5 makes nothing rest on it (`Peer.tla` "
            "header).",
        ], "grey", {"tint": False}),
    ], size=S) + 80

    # ================================================================== band 4: §4 to §7
    y = band(c, X0, y, "§4–§7 · Topics are promoted with the mesh and nobody is addressed; nothing rests on a report "
             "being read; talk settles nothing", status="proposed")
    y += row_cards(c, X0, y, WW, 24, [
        ("§4 · Topics are promoted with the mesh ⟨17⟩", [
            "**The mesh declares each topic**: its schema, which seat kinds may report to it, which nodes hear it, its "
            "label and its delivery mode.",
            "**A stack reports to a topic and names no recipient.** So \"Workers never address each other\" (ADR-0055 "
            "§7) stays true.",
            "The floor entry that would hold it is `FD12-topic-declared` (ADR-0067 §3): **no report to a peer topic "
            "the promoted mesh does not declare for the seat, and none that names a recipient.** "
            "[[red|Not written.]]",
        ], "amber", {}),
        ("This is not the choreography ADR-0055 rejected (§4)", [
            "**Its objection**: \"Every reading in which cells react to each other directly puts a model's output in "
            "charge of what runs next.\"",
            "**Here the mechanism still decides what runs next**: no guard reads a peer's report, and no report causes "
            "a lease.",
            "**A stack chooses among entries its lease already permits**, which is the orchestrator's position: "
            "which, never whether.",
        ], "amber", {}),
        ("The one sentence of ADR-0055 §7 that changes (§4)", [
            "[[red|\"No variant publishes to another cell or subscribes to anything.\"]]",
            "**What stays**: \"Workers never address each other\", and \"the mechanism is the bus\" for every event a "
            "mesh reacts to (D6).",
            "**ADR-0055 is Proposed**, and C3 does not apply while this is an overlay (Status note). If the "
            "archetype takes the change, ADR-0055 §7 owes the one sentence (§8).",
        ], "red", {"tint": False, "dash": "6 4"}),
        ("§5 · Nothing may rest on a report being read", [
            "An order before an effect, and an Observer coupled to it, exist so that **what the effect can cause is "
            "bounded before it lands**.",
            "**A report can cause nothing**: §1 says so of the receiving side, and the governor's permit bounds the "
            "transmission itself. **So a send needs neither.**",
            "An Observer reads the record afterwards, and its finding subtracts.",
        ], "amber", {}),
    ], size=S) + 34
    top = y
    gg = 40
    w6 = 1500
    xd = X0 + w6 + gg
    wd = X1 - xd
    c.text(X0, top + 16, "**§6 · Vehicles coordinate in two ways, and talk settles nothing** ⟨21⟩", 16, "ink")
    t6 = c.table(X0, top + 32, [("Way", w6 * 0.22, {"bold": True}), ("How", w6 * 0.26), ("Waits for", w6 * 0.18),
                                ("Outcome", w6 * 0.34)], [
        {"cells": ["By talk", "On topics, as reports (§2–§4)", "No round of the plane",
                   "**Two stacks may claim the same task.** A stack that claims everything stalls its peers "
                   "(Consequences)"], "accent": "amber"},
        {"cells": ["By order", "An entry the bundle marks `ordered` (ADR-0062 §3)", "One round",
                   "**Every vehicle sees the same outcome.** Where the tally wants one vehicle and no more, only this "
                   "will do"], "accent": "violet"},
        {"cells": ["Alone", "A vehicle that is alone coordinates with nobody", "—",
                   "**Its beacon tells its peers where it is** (ADR-0062 §5: an effect, counted per lease)"],
         "accent": "grey"},
    ], size=14, accent="violet")
    hd = c.card(xd, top, wd, "§7 · D-0065-1: one lineage across a clear topic", [
        "**ADR-0054 §6 wants independent Thinkers at the two ends of a clear edge**, and every deployment today "
        "declares that it has them (D-0054-1).",
        "**Vehicles of one build have one lineage** and cannot declare it of a topic delivered clear.",
        "**Such a deployment delivers peer reports as handles, or declares this degeneracy.**",
    ], accent="red", size=S, tint=False, dash="6 4")
    y = top + max(32 + t6, hd) + 80

    # ================================================================== band 5: the module
    y = band(c, X0, y, "`spec/Peer.tla`: checked by TLC and proved by TLAPS (§9 ⟨R1⟩)", "teal")
    y += c.para(X0, y, WW, "**One receiving governor, its lease, and an honest sending governor. The radio belongs to the "
                "adversary**: any report on any topic, with any labels, can arrive, which is more than honest senders "
                "produce and is what a captured sender can do. The three kinds of traffic arrive as items: `certified`, a "
                "fence the plane ordered, relayed by a peer that originates nothing (the certificate taken as "
                "unforgeable, ADR-0059 §5); `measured`, which may refuse and never permits; and `report`, delivered as "
                "labelled ingress (header). TLC 2.19, `MaxDeliver` = 2, `MaxSend` = 1 unless a row says otherwise. "
                "**Checked, at small constants; proved, as the prover bounds the claim**; none of it is said of running "
                "code, which does not exist.", 14, "muted") + 18
    pw_ = WW
    y += c.table(X0, y, [("Property", pw_ * 0.13, {"mono": True}), ("What it says (`Peer.tla`)", pw_ * 0.27),
                         ("Mutation that must break it", pw_ * 0.2), ("Breaks (TLC)", pw_ * 0.13),
                         ("Holds under the other two (TLC)", pw_ * 0.15), ("Proved (TLAPS)", pw_ * 0.12)], [
        ["PeerAddsNothing", "Every request permitted is still permitted with every item received from peers removed (§1)",
         "`M_PEERENABLES`: a report enables one entry, `gated`", "`m-enables-adds`: VIOLATED, 21 states",
         "`m-label-adds`, `m-topic-adds`", "`PeerAddsNothingAlways`"],
        ["NarrowsInReceived", "Every request permitted is still permitted with any subset of those items: receipt only "
                              "narrows ⟨R1⟩", "`M_PEERENABLES`", "`m-enables-narrows`: VIOLATED, 21 states",
         "`m-label-narrows`, `m-topic-narrows`", "`NarrowsInReceivedAlways`"],
        ["ReceivedIsUntrusted", "A delivered report's label holds `untrusted` and its topic's name, whatever its sender "
                                "declared (§3)", "`M_SENDERLABEL`: the sender's label is taken as given",
         "`m-label-untrusted`: VIOLATED, 7 states", "`m-enables-untrusted`, `m-topic-untrusted`",
         "`ReceivedIsUntrustedAlways`"],
        ["SendWithinTopics", "Every report an honest governor sends is to a topic the mesh declares for the seat (§2, §4)",
         "`M_ANYTOPIC`: a governor sends a report to an undeclared topic", "`m-topic-send`: VIOLATED, 31 states",
         "`m-enables-send`, `m-label-send`", "`SendWithinTopicsAlways`"],
        {"cells": ["Safe", "All four together, no mutation", "—",
                   "**Holds**: `s-none-safe`, 17,696 distinct states; `s-none-safe-3` (`MaxDeliver` = 3), 62,480",
                   "Each mutation breaks only its own property: 12 rows", "`SafeAlways`, `TypeAlways`"],
         "accent": "teal"},
    ], size=13.5, accent="teal") + 30
    top = y
    ww_ = WW * 0.58
    xr = X0 + ww_ + 40
    wr = X1 - xr
    c.text(X0, top + 16, "**The eleven witnesses: each an invariant that must be VIOLATED, and each was** "
           "(`Peer-rows.txt`; `Peer-results-2026.11.10.txt`)", 15, "ink")
    tw = c.table(X0, top + 32, [("Row", ww_ * 0.13, {"mono": True}), ("Witness", ww_ * 0.28, {"mono": True}),
                                ("What reaching it shows (`Peer.tla`)", ww_ * 0.47),
                                ("States", ww_ * 0.12)], [
        ["w-permit", "NeverPermitted", "A request is permitted", "33"],
        ["w-narrowed", "NeverNarrowedByClear", "A clear report refuses what is permitted without it", "191"],
        ["w-handle", "NeverPermitAfterHandle", "A report delivered as a handle does not narrow: `egress` permitted after "
                                               "an `untrusted` report as a handle", "200"],
        ["w-measured", "NeverRefusedByMeasured", "A measured `near` refuses `act`", "77"],
        ["w-fence", "NeverStoppedByFence", "A relayed fence refuses", "399"],
        ["w-dropped", "NeverDroppedOffTopic", "A report on a topic the seat does not hear is dropped", "15"],
        ["w-refdecl", "NeverSendRefusedDeclared", "A send to an undeclared topic is refused", "17"],
        ["w-refbundle", "NeverSendRefusedByBundle", "A send to a topic a bundle silences is refused", "16"],
        ["w-sent", "NeverSent", "An honest governor sends", "30"],
        ["w-labellow", "NeverSenderLabelledLow", "A sender declares no `untrusted`", "7"],
        {"cells": ["w-relayedlease", "NeverPermitUnderRelayedLease", "**A request is permitted under a lease a peer "
                   "relayed: the header's finding on §1**, and why §1 ranges over what a peer originates", "49"],
         "accent": "red"},
    ], size=13.5, accent="teal")
    c.text(X0, top + 32 + tw + 26, "`Rows: 25 · as expected: 25 · not as expected: none · ERROR: none`", 14, "teal")
    bot_l = top + 32 + tw + 40
    bot_r = stack(c, xr, top, wr, [
        ("Proved: 254 obligations (`Peer-proof-results-2026.11.10.txt`)", [
            "**Theorems**: `TypeAlways`, `PeerAddsNothingAlways`, `NarrowsInReceivedAlways`, "
            "`ReceivedIsUntrustedAlways`, `SendWithinTopicsAlways`, `SafeAlways`. **Assumptions: none.**",
            "Sixteen lemmas, among them `MutPeerEnablesEnablesGated`, `MutSenderLabelTakesTheLabel` and "
            "`MutAnyTopicAdmitsAny`. **Mutations and witnesses are behaviours and stay with TLC.**",
            "tlapm 7824dab, with Z3, Zenon, Isabelle and LS4.",
        ], "teal", {}),
        ("Certified, with 6 LS4 temporal steps that no checker confirms", [
            "**151** trivial, closed by tlapm with no backend; **97** by SMT, each a proof ethos accepted; **0** Zenon; "
            "**0** Isabelle; **6** LS4 temporal steps, not certified (`Peer-proof-cert-results-2026.11.10.txt`).",
            "**248 rest on tlapm's own normalization or on a checked proof; 6 rest on LS4.**",
        ], "teal", {}),
        ("What is abstracted (header)", [
            "**Three entries**: `act`, refused after a clear report labelled `n1` and by a measured `near`; `egress`, "
            "refused after any clear `untrusted` report; `gated`, in no alphabet, reachable only under "
            "`M_PEERENABLES`.",
            "**Three topics**: `t1` delivered clear, `t2` as a handle and silenced for sending, `tx` declared for "
            "nobody. A send's count is `MaxSend`.",
            "**Not modelled**: the record by digest, the lease's end, whether a report is read. Deadlock is not "
            "checked: stopping is safe. `Mesh.tla` is not edited and not extended.",
        ], "grey", {"tint": False}),
    ], gap=16, size=13.5)
    y = max(bot_l, bot_r) + 80

    # ================================================================== band 6: §8, §9, options, consequences
    y = band(c, X0, y, "§8, §9 · An overlay that reports upstream, and what ratification needs", status="proposed")
    top = y
    w8 = 1000
    x9 = X0 + w8 + 40
    w9 = X1 - x9
    b8 = stack(c, X0, top, w8, [
        ("§8 · Reported under ADR-0058 §6 ⟨Q11⟩", [
            "**An emission that is permitted and not ordered.**",
            "**Ingress that arrives unasked.**",
            "**Carries a debt against nothing while this is an overlay.** Closes nothing.",
        ], "amber", {"status": "proposed", "status_extra": "an overlay, not the archetype"}),
        ("If the archetype takes them, its records owe", [
            "**ADR-0055 §7**: the one sentence.",
            "**ADR-0015**: an emission with a permit and no ordered admit.",
            "**ADR-0040**: a `Report` to a topic that is not the principal's own round topic.",
            "**ADR-0043**: a sixth item of ingress.",
            "**ADR-0047**: its label.",
        ], "grey", {"tint": False}),
    ], gap=18, size=S)
    c.text(x9, top + 16, "**§9 · Ratification condition, item by item**", 16, "ink")
    t9 = c.table(x9, top + 32, [("Item", w9 * 0.42), ("Where it stands", w9 * 0.58)], [
        {"cells": ["**ADR-0055 is ratified first**, and ADR-0062 first or with this record",
                   "[[red|Not met.]] Both are Proposed (2026.10.07; 2026.11.10)"], "accent": "red"},
        {"cells": ["**A module, `Peer`**, stating at least `PeerAddsNothing`, `ReceivedIsUntrusted` and "
                   "`SendWithinTopics`, with `M_PEERENABLES`, `M_SENDERLABEL` and `M_ANYTOPIC`",
                   "[[teal|Met for TLC and TLAPS ⟨R1⟩.]] `spec/Peer.tla` (`5ee3528164cd1a35`): 25 rows, all as expected "
                   "(`d3b80c6f31ca83e8`); `spec/Peer_proof.tla` (`3c661ef57179a03c`): 254 obligations proved "
                   "(`f5678d36db4e1127`), certified with 6 LS4 temporal steps that no checker confirms "
                   "(`12677112bade3a44`). `NarrowsInReceived` is added; `NeverPermitUnderRelayedLease` is reached"],
         "accent": "teal"},
        {"cells": ["**The floor carries `FD12-topic-declared`**, and is shown monotone in what was received from peers, "
                   "as the label forbids are in `clearSet` (ADR-0067)",
                   "[[red|Not written.]] ADR-0067 §7: \"no entry is written\"; the `federation` stage, `FD1` to "
                   "`FD14`, does not exist"], "accent": "red"},
        {"cells": ["**The reference** shows a report delivered clear and one as a handle; an entry refused after a "
                   "clear report that is permitted without it; and a send refused by a bundle",
                   "[[red|Not met.]] Nothing is built"], "accent": "red"},
        {"cells": ["**A reader who is not the drafter** (ADR-0029 A2)",
                   "[[red|Not met.]] One author, one day (Consequences)"], "accent": "red"},
    ], size=14, accent="blue")
    y = max(b8, top + 32 + t9) + 70

    y = band(c, X0, y, "Options considered, whole", status="proposed")
    y += c.table(X0, y, [("Option", 900, {"bold": True}), ("Disposition", WW - 900)], [
        {"cells": ["The plane's log as the only path, the first revision",
                   "[[grey|Not taken ⟨15⟩.]] It has no rate for what vehicles tell each other"], "accent": "grey"},
        {"cells": ["A send with no permit",
                   "[[grey|Not taken ⟨16⟩.]] It is a sideways effect path, which falsifies ADR-0015's enumeration"],
         "accent": "grey"},
        {"cells": ["A send ordered by the plane",
                   "[[red|Rejected.]] A round per message, for an effect that can enable nothing"], "accent": "red"},
        {"cells": ["Free addressing",
                   "[[grey|Not taken ⟨17⟩.]] A stack would name another, which the corpus excludes for every "
                   "principal"], "accent": "grey"},
        {"cells": ["A report that can enable, a trust score that admits",
                   "[[red|Rejected.]] It is what ADR-0007 prohibits (the swarm reading, §2.2)"], "accent": "red"},
        {"cells": ["`untrusted` alone as the label",
                   "[[grey|Not taken ⟨Q19⟩.]] A bundle could not tell one topic from another"], "accent": "grey"},
        {"cells": ["The sender's label taken as given", "[[red|Rejected.]] `M_SENDERLABEL`"], "accent": "red"},
    ], size=14, accent="grey") + 70

    y = band(c, X0, y, "Consequences, and what is open")
    gg = 30
    w3 = (WW - 2 * gg) / 3
    xs = [X0, X0 + w3 + gg, X0 + 2 * (w3 + gg)]
    b1 = stack(c, xs[0], y, w3, [
        ("Positive", [
            "**A path for what vehicles tell each other**, at whatever rate the radios carry.",
            "**A fence travels by relay**, to any vehicle in range of one that heard it.",
            "**No new authority.** The property is that removing every item a peer originates changes no permit.",
        ], "green", {}),
    ], size=S)
    b2 = stack(c, xs[1], y, w3, [
        ("Negative", [
            "**Talk settles nothing.** A stack that claims everything stalls its peers.",
            "**The tally votes the joint worst case.** Stacks that can talk can act together inside their envelopes. "
            "That was already the premise, since stacks of one lineage may fail alike, and ADR-0063's bound is what "
            "holds it.",
            "**A finding has further to travel.** In a mesh, \"a finding against any activation in the history closes "
            "every edge downstream\" (ToO §2.11). A report read off the edges is not on that history. The delivery "
            "records say who read what, and they reach the plane only at the seal.",
            "**Listening narrows**, so a mission's rules decide how much a stack that listens may still do.",
            "**One author, one day.**",
        ], "red", {"tint": False}),
    ], size=S)
    b3 = stack(c, xs[2], y, w3, [
        ("Open obligations", [
            "**The floor entry and the reference** (§9).",
            "**A refusal on a governor's measured facts**, for navigation deception (the swarm reading, §2.4): a "
            "design, and what a lying peer can stop with it.",
            "**A topic's schema.** Whether a topic may carry free text, or typed fields only.",
            "**A count for sends per lease**, as a placeholder first.",
        ], "red", {"tint": False, "status": "open"}),
    ], size=S)
    c.ymax = max(c.ymax, b1, b2, b3)
    return c
