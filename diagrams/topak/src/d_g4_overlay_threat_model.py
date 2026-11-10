"""G4 — The command-chain overlay declares its adversaries, its trusted-base rows and its assumptions of use
(ADR-0068, Proposed, not revised). Fourteen adversaries placed on the overlay's structure, twelve rows by class as G1
draws them, ten assumptions, what is given up, and what ratification needs. ADR-0068 has no R1: what this diagram
says of the modules of ADR-0059 to ADR-0066 is its own cross-reference, and is marked so."""
from lib import Canvas, STATUS, STATE_CC, text_width

ID, SLUG = "G4", "overlay-threat-model"

W = 3400
S = 14          # body text in the picture


def row_cards(c, x, y, w, gap, specs, size=14):
    """A row of cards of equal height, measured over every card. specs: (title, body, accent, kwargs)."""
    n = len(specs)
    cw = (w - (n - 1) * gap) / n
    h = max(c.card(0, 0, cw, t, b, draw=False, size=size, status=k.get("status"),
                   bullets=k.get("bullets", True)) for t, b, _, k in specs)
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


def xref_frame(c, x, y, w, h, label):
    """A dashed teal frame around a column the diagram adds, with a tab saying it is not the record's."""
    c.rect(x - 3, y - 3, w + 6, h + 6, "teal", tint=False, dash="7 5", sw=2.2, rx=4,
           fill_token=None)
    c.out[-1] = c.out[-1].replace('fill="#ffffff" ', 'fill="none" ').replace("f-bg ", "")
    c.pill(x + w, y - 34, label, "teal", 12, dash="7 5", anchor="end")


def build():
    c = Canvas(
        ID, "The command-chain overlay declares its adversaries, its trusted-base rows and its assumptions of use",
        "ADR-0068 is the overlay's declaration of what it trusts and assumes, as ADR-0045's Annex B is the "
        "reference's: **fourteen adversaries** with what bounds each and what is left, **twelve trusted-base rows** "
        "classed by failure direction, **ten assumptions of use**, and what the nine records beside it give up. "
        "**The corpus's adversary is the agent**; this deployment adds adversaries that attack links, hardware and "
        "planes, and puts a trusted component on every vehicle (Context). **ADR-0068 is Proposed and has not been "
        "revised**: its Status note still says \"nothing here is modelled, checked or built\" and its §6 says \"no "
        "module is written\", while the TLA+ modules of ADR-0059 to ADR-0066 were written, checked and proved on "
        "2026.11.10 and those records' R1 rows cite them. Where this diagram names a module property, that is its "
        "own cross-reference, marked as such, and not the record's text.",
        W, "ADR-0068 provenance note (⟨3⟩, ⟨Q9⟩, ⟨Q11⟩), Status note, Context, Decision §1 (the table of fourteen "
        "adversaries; Out of scope), §2 (the table of twelve rows), §3 (the table of ten assumptions), §4, §5, §6, "
        "Options considered (its table), Consequences, Findings 1–3, Open obligations, History; ADR-0045 §2 (three "
        "classes and a refusal), Findings 2, Annex A T-0045-1, T-0045-3, T-0045-4, T-0045-6; ADR-0059 §1, §4, §5, §6, "
        "R1; ADR-0060 §1–§3, R1; ADR-0061 §1, §3, §4, R1; ADR-0062 §1, §7, §8, R1; ADR-0063 §2, §3, R1; ADR-0064 "
        "§1–§3, §5, R1; ADR-0065 §1, §3, R1; ADR-0066 §1–§4, R1; ADR-0067 §3 (the `federation` stage); ToO rev 15 "
        "§13 (A1, A9, A13), as ADR-0068 cites it; module headers (everything before EXTENDS) of spec/Federation.tla, "
        "Membership.tla, Intent.tla, Alone.tla, Outstanding.tla, PlaneClock.tla, Peer.tla, Release.tla; their "
        "results, proof-results and proof-cert-results files of 2026.11.10 (summary lines); spec/Membership-rows.txt "
        "(header); diagrams/topak/src/d_g1_trusted_base.py (classes drawn by tint)",
        state=STATE_CC)
    X0, X1 = c.x0, c.x1
    WW = X1 - X0
    y = c.y

    # ================================================================== status strip
    c.text(X0, y + 15, "Status", 15, "faint", bold=True)
    px0 = X0 + 80
    px = px0
    for lab, key, extra, pill in [
            ("ADR-0068", "proposed", "C2 · drafted 2026.11.10", None),
            ("deployment position", None, "", ("An overlay, not the archetype ⟨Q11⟩", "amber", "6 4")),
            ("row and assumption ids", None, "", ("The drafter's", "grey", None)),
            ("rows tested against a vehicle", None, "", ("None", "red", "2 3")),
            ("the modules of ADR-0059 to ADR-0066", None, "", ("Checked and proved 2026.11.10", "teal", None)),
            ("ADR-0068 revised to say so", None, "", ("Not revised: no R1", "red", "6 4")),
            ("ADR-0059 to ADR-0067", "proposed", "each revised R1 2026.11.10", None),
            ("floor stage `federation`, FD1–FD14", None, "", ("Not written", "red", "2 3")),
            ("the reference", "notbuilt", "", None)]:
        lw = text_width(lab, 13.5, True) + 8
        plab = pill[0] if pill else STATUS[key][0] + (f" · {extra}" if extra else "")
        pw = text_width(plab, 11.5, True) + 18
        if px + lw + pw > X1:
            px = px0
            y += 34
        c.text(px, y + 15, lab, 13.5, "ink", bold=True)
        px += lw
        if pill:
            px += c.pill(px, y, pill[0], pill[1], 11.5, dash=pill[2]) + 26
        else:
            px += c.status(px, y, key, extra) + 26
    y += 42
    y += c.para(X0, y, WW, "**Proposed means nothing here is in force**, and no record of the overlay is ratified. "
                "**C2** applies: ADR-0045 holds that an undeclared row is false, so §2 is a claim that these rows are "
                "all the overlay adds to the trusted base. C1, C3 and C4 do not apply on the drafter's reading while "
                "this is an overlay ⟨Q11⟩. The custodian asked for a threat model ⟨3⟩ and answered ⟨Q9⟩ and ⟨Q11⟩; "
                "**every other choice is the drafter's, and so are the row and assumption ids**. ADR-0045 was not "
                "re-read beyond its refused rows and finding 2 (provenance note). **No row has been tested against "
                "a vehicle** (Status note). One author, one day, and no vehicle (Consequences).", 14.5,
                "muted") + 34

    # ================================================================== band 0: what exists that the record does not say
    y = band(c, X0, y, "What exists that ADR-0068 does not say: the modules of ADR-0059 to ADR-0066 (the diagram's "
             "note, not the record's text)", "teal")
    top = y
    wl = 1080
    g = 50
    xr = X0 + wl + g
    wr = WW - wl - g
    hl = c.card(X0, top, wl, "ADR-0068 has not been revised to say the modules exist", [
        "**The record as it stands**: its Status note says **\"Nothing here is modelled, checked or built\"**, and §6 "
        "says of its third condition **\"Not met: no module is written.\"** Its History has one row, the initial "
        "draft, Proposed.",
        "**Since then, the same day**: TLA+ modules for ADR-0059 to ADR-0066 were written, **checked** by TLC and "
        "**proved** with TLAPS, and each of those records gained an **R1** row citing its module (ADR-0067's R1 "
        "follows ADR-0063's; it has no module). **ADR-0068 has no R1.**",
        "**So this diagram draws the record as it stands**, with its words \"not met\" and \"no module is written\", "
        "and says beside them, in teal and dashed, what the modules now state. **Nothing in a teal dashed frame is "
        "ADR-0068's.**",
        "**The modules are of the specification.** None of these words is said of running code: the floor stage "
        "`federation` is not written and the reference is not built. ADR-0068 itself, a declaration, has no module.",
    ], accent="red", size=14.5, tint=False, dash="6 4")
    c.text(xr, top + 16, "**Eight modules, 2026.11.10** (summary lines of each results, proof-results and "
           "proof-cert-results file)", 16, "ink")
    mods = [
        ("Federation", "ADR-0059", "41", "892", "7"),
        ("Intent", "ADR-0060, with ADR-0062 §2", "35", "677", "5"),
        ("Membership", "ADR-0061, at five replicas (not seven, ADR-0061 R1)", "28", "495", "6"),
        ("Alone", "ADR-0062 §5, §7, §11", "47", "263", "6"),
        ("Outstanding", "ADR-0063", "40", "1,871", "6"),
        ("PlaneClock", "ADR-0064, with ADR-0062 §4", "38", "535", "6"),
        ("Peer", "ADR-0065", "25", "254", "6"),
        ("Release", "ADR-0066, with ADR-0062 §6", "67", "613", "10"),
    ]
    rows = [[f"`{m}`", r, f"**{n}** rows, all as expected", f"**{o}** obligations proved",
             f"certified, with **{l}** LS4 temporal steps that no checker confirms"] for m, r, n, o, l in mods]
    rows.append({"cells": ["**All eight**", "", "**321** rows, all as expected", "**5,600** obligations proved",
                           "certified, with **52** LS4 temporal steps that no checker confirms"], "accent": "teal"})
    cols = [("Module", 200), ("For", 560), ("Checked (TLC, small constants)", 420),
            ("Proved (TLAPS)", 330)]
    cols.append(("Certified", wr - sum(cc[1] for cc in cols)))
    tm = c.table(xr, top + 32, cols, rows, size=13.5, accent="teal")
    yb = top + 32 + tm + 14
    yb += c.para(xr, yb, wr, "Each proof module: \"a proved obligation is a theorem of the module under its "
                 "assumptions and the hypotheses the statement names\"; mutations and witnesses stay with TLC. The "
                 "module headers name findings against their records, and the R1 revisions took them. **A property "
                 "under a premise is drawn with its premise** (the last column of §1's table, below).", 14, "muted")
    y = max(top + hl, yb) + 80

    # ================================================================== band 1: the picture
    y = band(c, X0, y, "Where each adversary attacks (§1), placed on the structure ADR-0059 to ADR-0066 describe",
             status="proposed")
    y += c.legend(X0, y, [("box", "red", "an adversary (TM1–TM14) and what it attacks"),
                          ("box", "blue", "a trust-root row (T-0068-n) on that component"),
                          ("box", "violet", "consensus: the plane's replicas"),
                          ("box", "teal", "mechanism: the governor"),
                          ("box", "brown", "people"),
                          ("box", "pink", "an Observer"),
                          ("arrow", "blue", "authority, ordered above"),
                          ("arrow", "violet", "what the plane grants")],
                  title="Accents") + 24

    # ---- top row: artifacts -> planes above -> commanded plane <- people
    ytop = y + 10
    wA, wB, wC = 500, 680, 900
    gx = 140
    wD = WW - wA - wB - wC - 3 * gx
    xA = X0
    xB = xA + wA + gx
    xC = xB + wB + gx
    xD = xC + wC + gx
    A = ("Artifacts: weights, tools, bundles", [
        "They enter a plane only by promotion, named by digest.",
        "[[red|TM10 · supply chain]]: ships a bad artifact. Bounded by promotion by digest, and by lineage "
        "independence, which is Proposed (ADR-0035).",
    ], "grey")
    B = ("The planes above, to the root", [
        "Each plane is seated by its parent's promotion under a charter it can only narrow, and is fenced by every "
        "plane above it (ADR-0059 §1, §6).",
        "A plane is a havoc issuer, bounded by its charter (ADR-0059 §4).",
        "The anchor's custody is declared per deployment (ADR-0025) and is out of scope (§1).",
    ], "blue")
    C = ("A commanded plane: the intent boundary", [
        "**People are seated at it.** The last commanded plane above a group of vehicles orders the authorizing "
        "admit of every effect (ADR-0060 §1).",
        "A reversible effect is admitted as an **intent**, a charter for one round. An irreversible one is admitted "
        "itself, one at a time.",
        "It reads the autonomous plane's record and answers with **watermarks**; a plane may have `K_up` effects "
        "outstanding and no more (ADR-0063 §2, §3).",
        "[[blue|T-0068-5]] the intent boundary's reading: trust root for the watermark.",
    ], "blue")
    D = ("Commander and operators", [
        "Order intents: the first by the tally that promoted the mesh, each later one by one operator (ADR-0060 §2).",
        "[[red|TM7 · an insider with a key]]: whatever that seat may do. Bounded by attribution; an operator's add "
        "needs a live peer (ADR-0050).",
    ], "brown")
    E = ("A person at a `release` seat", [
        "Composes and signs each irreversible act: the only seat that reaches an irreversible entry (ADR-0066 "
        "§1–§3).",
        "[[red|TM7]]: a wrong act by a release person is recorded and not prevented.",
        "[[red|TM9 · deception of perception]]: a deceived person at a release seat is a semantic failure. Nothing "
        "here sees it.",
    ], "brown")

    def mh(spec, w_, **k):
        return c.card(0, 0, w_, spec[0], spec[1], draw=False, size=S, **k)

    hA, hB, hC0, hD, hE = mh(A, wA), mh(B, wB), mh(C, wC), mh(D, wD), mh(E, wD)
    gDE = 40
    hC = max(hC0, hD + gDE + hE)
    c.card(xA, ytop, wA, A[0], A[1], accent=A[2], size=S, tint=False)
    c.card(xB, ytop, wB, B[0], B[1], accent=B[2], size=S)
    c.card(xC, ytop, wC, C[0], C[1], accent=C[2], size=S, h=hC)
    c.card(xD, ytop, wD, D[0], D[1], accent=D[2], size=S)
    yE = ytop + hD + gDE
    c.card(xD, yE, wD, E[0], E[1], accent=E[2], size=S)
    ya = ytop + 70
    c.arrow([(xA + wA, ya), (xB, ya)], "blue", label="promotion, by digest", lw=110)
    c.arrow([(xB + wB, ya), (xC, ya)], "blue", label="seats it, under a charter", lw=110)
    c.arrow([(xD, ytop + hD / 2), (xC + wC, ytop + hD / 2)], "brown", label="intents", lw=110)
    c.arrow([(xD, yE + hE / 2), (xC + wC, yE + hE / 2)], "brown", label="a signed act", lw=110)
    top_bot = ytop + max(hA, hB, hC, hD + gDE + hE)

    # ---- the link
    L = ("The link adversary · TM2", [
        "**Jams, drops, delays, replays, injects.** Cuts the link above a plane; cuts vehicles from their plane, "
        "making them alone; delays a revocation; blocks every irreversible effect.",
        "Certificates stop forgery. Fences and sequence numbers stop replay. `K_up` bounds what a delay buys, in "
        "effects, and an intent's named tick stops a withheld one from starting late (ADR-0063, ADR-0064).",
        "[[green|Loss only subtracts]] ([[green|T-0068-11, delegated]]): a plane cut off above stops granting "
        "before `K_up`, and a vehicle cut off from its plane loses its lease.",
    ], "red")
    wL = xC - X0 - 30 - 90
    hL = mh(L, wL)
    ylink = top_bot + 70
    hlink = hL + 70
    c.region(X0, ylink, WW, hlink, "The link above the plane, and the radios", "grey", dash="10 6")
    c.card(X0 + 30, ylink + 38, wL, L[0], L[1], accent=L[2], size=S, tint=False)

    # ---- the autonomous plane
    yplane = ylink + hlink + 70
    ax1, ax2 = xC + 260, xC + 640
    c.arrow([(ax1, ytop + hC), (ax1, yplane)], "blue", sw=2.4, label="intents, release acts, fences, watermarks",
            lpos=0.48, lw=230)
    c.arrow([(ax2, yplane), (ax2, ytop + hC)], "violet", sw=2.4, label="the plane's record, and seals",
            lpos=0.52, lw=200)

    pin = 30
    pw = WW - 2 * pin
    P = [
        ("Replicas and commit certificates", [
            "**Byzantine agreement with signed certificates**, seven replicas tolerating two captured (ADR-0061 §1). "
            "[[blue|T-0068-12]] stands in place of the replica row there.",
            "**Defined by one absence**: its log takes nothing that changes authority. It cannot seat, promote or "
            "release (ADR-0060 §3).",
            "[[red|TM4 · compromised replicas, fewer than a third]]: lie to the others.",
            "[[red|TM5 · a captured plane]]: a quorum of its replicas, which here means that share of its vehicles. "
            "Issues any lease within its charter, ignores fences, falsifies its log.",
        ], "violet", {}),
        ("Membership and its shrink schedule", [
            "**Shrinks only along a schedule its charter voted, down to a capture floor**, each step ordered by a "
            "certificate of the membership it replaces (ADR-0061 §3, §4).",
            "[[red|TM6 · a partitioned mesh]]: two groups each believing it is the plane. A certificate needs a "
            "quorum of the current membership, so at most one side grants.",
            "[[red|TM12 · attrition]]: vehicles destroyed, or silenced until their replicas are dropped. At the "
            "archetype's size, four losses one at a time or two at once.",
        ], "violet", {}),
        ("Ticks: the plane's clock", [
            "**Ticks numbered from the charter**, each signed by a certificate of replicas on their own clocks; every "
            "interval is a count of ticks from a named tick (ADR-0064 §1–§3).",
            "[[blue|T-0068-3]] the plane's clocks, taken together: trust root for the duration bound only.",
            "[[red|TM14 · clock faults among the replicas]]: a slow clock holds an intent open, and a fast one ends "
            "it early.",
        ], "violet", {}),
    ]
    yP = yplane + 44
    hP = row_cards(c, X0 + pin, yP, pw, 40, P, size=S)

    # ---- vehicles
    yv = yP + hP + 90
    gv = 110
    w1 = 1180
    wo = (pw - w1 - 3 * gv) / 3
    xv = [X0 + pin]
    for w_ in (w1, wo, wo):
        xv.append(xv[-1] + w_ + gv)
    vin = 24
    ST = ("The stack: the Thinker", [
        "Planning, perception, any model. **Byzantine**, as ADR-0007 has it (ADR-0062 §1).",
        "[[red|TM1 · the stack]]: requests anything, at any time.",
        "[[red|TM9]]: made wrong about the world. The premise already assumes it; perception never adds authority.",
    ], "grey")
    GV = ("The governor: mechanism, not a principal", [
        "Verifies the chain, holds the lease, the key and the radio, hosts its replica, **permits each `local` "
        "entry and counts it**, lifts its own facts (ADR-0062 §1).",
        "[[blue|T-0068-1]] its admit path, which now makes every `local` permit",
        "[[red|T-0068-2]] its clock: a residual, in the slow direction",
        "[[blue|T-0068-4]] its measure of an extent · [[red|Findings 1]]",
        "[[blue|T-0068-6]] its key store",
        "[[blue|T-0068-9]] its recovery function · [[red|Findings 1]]",
        "[[teal|T-0068-10]] Cedar and the Wasm engine on the vehicle",
    ], "teal")
    NV = ("The navigation source", [
        "[[blue|T-0068-7]] trust root for area checks · [[red|Findings 1]]",
        "[[red|TM8 · navigation deception]]: moves the envelope in the world by falsifying the governor's "
        "position. **Bounded by nothing in this design.**",
        "Time is not exposed the same way: no external time is read.",
    ], "blue")
    EF = ("Actuators, and the effector interlock", [
        "[[blue|T-0068-8]] the interlock: an irreversible effect only on a person's act (ADR-0066 §4) · "
        "[[red|Findings 1]]",
        "Hold, and the terminal behaviour by the recovery function, are carried out by the governor (ADR-0062 §7).",
    ], "grey")
    iw = w1 - 2 * vin
    gw = (iw - 90) * 0.6
    nw = iw - 90 - gw
    hST, hGV, hNV, hEF = mh(ST, iw), mh(GV, gw), mh(NV, nw), mh(EF, gw)
    hV1 = 44 + hST + 70 + max(hGV, hNV) + 70 + hEF + vin
    V2 = ("A captured vehicle · TM3", [
        "Extracts the key and the lease; acts as that principal and as one replica; signs any local record; "
        "reports anything to its peers.",
        "Bounded by the lease's envelope and what is left of its count, and by revocation once its plane knows.",
        "[[red|The interlock is moot when the effector itself is captured.]] Resistance to tampering is the "
        "builder's, a trust-root residual.",
    ], "red")
    V3 = ("A stack that lies to its peers · TM13", [
        "Under a signature that verifies: reports false tracks, claims every task, sends another stack text meant "
        "to steer it.",
        "Its reports are `untrusted` and enable nothing; listening narrows (ADR-0065).",
        "Left: an honest stack misled inside its own envelope, and peers stalled by claims.",
    ], "red")
    V4 = ("An Observer · TM11", [
        "Declared on another vehicle, it shares no hardware with its Thinker and may share its lineage. Declared on "
        "the same vehicle, no claim rests on it (ADR-0062 §8).",
        "[[red|TM11 · a colluding Observer]]: stays silent. Bounded by nothing: coupling cannot see collusion "
        "(ToO §13 A13).",
    ], "pink")
    ow = wo - 2 * vin
    V5 = ("Vehicles destroyed, or silenced · TM12", [
        "Each loss is one replica fewer, and the plane walks down the schedule its charter voted (ADR-0061 §3).",
        "Below the capture floor the plane ends and every survivor is alone. An adversary that can silence "
        "vehicles gets the floor's tolerance from the start.",
    ], "red")
    hv2, hv3, hv4 = (44 + mh(v, ow) + vin for v in (V2, V3, V4))
    hv5 = 44 + mh(V5, ow) + vin
    y5 = yv + hv4 + 60
    hV = max(hV1, hv2, hv3, hv4 + 60 + hv5)
    c.region(xv[0], yv, w1, hV1, "A vehicle: a governor and a stack (ADR-0062 §1)", "teal", dash=None)
    c.region(xv[1], yv, wo, hv2, "A captured vehicle", "red", dash="7 5")
    c.region(xv[2], yv, wo, hv3, "A peer", "teal", dash=None)
    c.region(xv[3], yv, wo, hv4, "An Observer, where declared", "pink", dash="10 6")
    c.region(xv[3], y5, wo, hv5, "Attrition", "grey", dash="10 6")
    c.card(xv[3] + vin, y5 + 44, ow, V5[0], V5[1], accent=V5[2], size=S, tint=False, dash="6 4")
    # vehicle 1 inside
    vx = xv[0] + vin
    ys = yv + 44
    c.card(vx, ys, iw, ST[0], ST[1], accent=ST[2], size=S, tint=False)
    yg = ys + hST + 70
    c.card(vx, yg, gw, GV[0], GV[1], accent=GV[2], size=S)
    c.card(vx + gw + 90, yg, nw, NV[0], NV[1], accent=NV[2], size=S, tint=False)
    ye = yg + max(hGV, hNV) + 70
    c.card(vx, ye, gw, EF[0], EF[1], accent=EF[2], size=S, tint=False)
    c.arrow([(vx + gw / 2, ys + hST), (vx + gw / 2, yg)], "grey", label="requests", lpos=0.5)
    c.arrow([(vx + gw + 90, yg + 60), (vx + gw, yg + 60)], "blue", label="position", lpos=0.5, lw=80)
    c.arrow([(vx + gw / 2, yg + hGV), (vx + gw / 2, ye)], "teal", label="permitted entries", lpos=0.5)
    for k, spec in ((1, V2), (2, V3), (3, V4)):
        c.card(xv[k] + vin, yv + 44, ow, spec[0], spec[1], accent=spec[2], size=S, tint=False,
               dash="6 4" if spec[2] == "red" else None)
    # TM6: a partition between the two groups
    px_ = xv[2] - gv / 2
    hpart = max(hv2, hv3)
    c.line(px_, yv - 30, px_, yv + hpart + 30, "red", sw=2.4, dash="9 6")
    c.label(px_, yv + hpart / 2, "TM6 · a partition", "red", 12.5, 80)
    # leases from the plane to the vehicles
    c.arrow([(xv[0] + w1 / 2, yP + hP), (xv[0] + w1 / 2, yv)], "violet", sw=2.4,
            label="a lease per vehicle, under the live intent; ticks; fences", lpos=0.5)

    # ---- peer topics
    BUS = ("Peer topics, promoted with the mesh (ADR-0065 §1–§4)", [
        "**A send is an effect, permitted and never ordered. Receipt is ingress, labelled `untrusted` and by its "
        "topic. Nobody is addressed, and nothing a peer originates is ever an enabling condition.** The governor "
        "holds the radio, so a stack cannot make its own vehicle alone (ADR-0062 §1).",
    ], "grey")
    ybus = yv + hV + 80
    hBus = c.card(X0 + pin, ybus, pw, BUS[0], BUS[1], accent=BUS[2], size=S, tint=False, bullets=False)
    for k, (w_, hh_) in enumerate(((w1, hV1), (wo, hv2), (wo, hv3))):
        cxv = xv[k] + w_ / 2
        c.arrow([(cxv, yv + hh_), (cxv, ybus)], "grey", both=True)
    yplane_bot = ybus + hBus + 30
    c.region(X0, yplane, WW, yplane_bot - yplane, "An autonomous plane: seven replicas under Byzantine agreement, "
             "one on each vehicle's governor, below the intent boundary (ADR-0060 §3, ADR-0061 §1)", "violet",
             dash=None)
    y = yplane_bot + 30
    y += c.para(X0, y, WW, "**The picture is the diagram's placement of §1's rows**, not a figure in the record. Each "
                "adversary sits on what it attacks; the table below has every column. Out of scope (§1): destruction "
                "other than its effect on a quorum, which is TM12; attacks on sensors other than TM8 and TM9; traffic "
                "analysis; and the anchor's custody, which ADR-0025 declares per deployment.", 14, "muted") + 80

    # ================================================================== band 2: §1's table
    y = band(c, X0, y, "§1 · Fourteen adversaries, each with what bounds it and what is left ⟨3⟩", status="proposed")
    t1 = [
        ["TM1", "**The stack**, Byzantine as ADR-0007 has it", "Request anything, at any time",
         "The governor, the alphabet, the envelope",
         "Anything inside the envelope was voted acceptable. What the vehicle's body does that no entry names is "
         "outside the alphabet",
         "Intent `EveryEffectHasALease`: each reversible effect has a lease and is within its count. Alone "
         "`ExpiryGrantsNothing`, `TerminalNeverWaits`: the stack neither selects nor gates the terminal act. Release "
         "`SignedByPerson`. The modules take the governor as honest (A-0068-1)"],
        ["TM2", "**The link adversary**: jams, drops, delays, replays, injects",
         "Cut the link above a plane; cut vehicles from their plane, making them alone; delay a revocation; block "
         "every irreversible effect",
         "Certificates stop forgery. Fences and sequence numbers stop replay. `K_up` bounds what a delay buys, in "
         "effects, and an intent's named tick stops a withheld one from starting late (ADR-0063, ADR-0064)",
         "Denial is always available to it, and the response is predictable: a plane cut off above stops granting "
         "before `K_up`, and a vehicle cut off from its plane loses its lease within a tick period and does its "
         "terminal behaviour. Silencing vehicles also walks a plane down its shrink schedule (TM12)",
         "Federation `AnyPlaneFences`. Release `UsedOnce`, and `NoOlderThanDeclared`, in ticks and not duration. "
         "Outstanding `EffectsAfterRevocationBounded`, with no clock in the module. PlaneClock `NoGrantPastExpiry`, "
         "**under its premise** `ClockPremise`. Alone `AlonePermitsNothing`. Release's finding 2: an act already "
         "across a cut link still fires inside `FreshT`; `OrderedInContact` is what holds"],
        ["TM3", "**A captured vehicle**",
         "Extract the key and the lease; act as that principal and as one replica; sign any local record; report "
         "anything to its peers",
         "The lease's envelope and what is left of its count. Revocation, once its plane knows. One replica is "
         "within what Byzantine agreement tolerates. Its reports are `untrusted` and enable nothing, and its "
         "governor's facts can only make others refuse (ADR-0065)",
         "The interlock is moot when the effector itself is captured. Resistance to tampering is the builder's, and "
         "is a trust-root residual",
         "Outstanding `CountExact`. Peer `PeerAddsNothing` (a measured fact may refuse and never permits) and "
         "`ReceivedIsUntrusted`: the receiver's `untrusted` and topic name survive a captured sender, a name the "
         "sender added does not. \"Once its plane knows\": none"],
        ["TM4", "**Compromised replicas, fewer than a third** of a plane", "Lie to the others",
         "Byzantine agreement and commit certificates (ADR-0059 §5)",
         "Under crash-recovery consensus one such replica can propose an admit no floor evaluated (A9). That is why "
         "ADR-0059 §5 asks for more", ""],
        ["TM5", "**A captured plane**: a quorum of its replicas, which for an autonomous plane means that share of "
         "its vehicles", "Issue any lease within its charter, to anyone; ignore fences; falsify its log",
         "The charter or the intent, checked by every governor. Each honest governor keeps its own account against "
         "`K_up` and checks every watermark itself (ADR-0063 §3). An autonomous plane adds nothing: it cannot seat, "
         "promote or release",
         "Fewer than `K_up` effects from each honest vehicle, within the intent. Its ticks are the captor's, so the "
         "duration bound there rests on each honest governor's own clock, which treats a lagging tick as overdue",
         "Outstanding `EffectsAfterPerGovernor`, `HavocPlaneBoundedInEffects`, the plane signing anything. "
         "Federation `HavocPlaneBounded`. Release `OrderedAtCommand`. PlaneClock `EntryEndsAtExtent`, "
         "`NoStretchUnlessSlow`, on the governor's own clock. **Not under capture**: Federation `BudgetConserved` "
         "(an honest subtree only, a finding) and Intent `AutonomousAddsNothing` (an honest plane's log)"],
        ["TM6", "**A partitioned mesh**", "Leave two groups of vehicles each believing it is the plane",
         "A certificate needs a quorum of the current membership, so at most one side grants and at most one side "
         "can order a step of the schedule. The other side's vehicles are alone",
         "A mesh split into pieces all too small admits nothing, and every vehicle is alone",
         "Membership `StepByQuorum`, `AtMostOneSuccessor`, at five replicas, **under its premise** "
         "`CapturedWithinFloor`. Alone `AlonePermitsNothing`. That at most one side grants rests on the certificate, "
         "which every module takes as unforgeable"],
        ["TM7", "**An insider with a key**: an operator or a release person", "Whatever that seat may do",
         "Attribution. An operator's add needs a live peer (ADR-0050)",
         "The mechanism cannot tell a person from a program holding the key. A wrong act by a release person is "
         "recorded and not prevented", ""],
        ["TM8", "**Navigation deception**", "Move the envelope in the world by falsifying a governor's position",
         "Nothing in this design",
         "The navigation source is a trust root with this residual. Time is not exposed the same way, since no "
         "external time is read", ""],
        ["TM9", "**Deception of perception**, the stack's or a person's", "Make the stack or the person wrong about "
         "the world", "For the stack, the premise already assumes it. Perception never adds authority",
         "A deceived person at a release seat is a semantic failure. Nothing here sees it", ""],
        ["TM10", "**Supply chain**: weights, tools, bundles", "Ship a bad artifact",
         "Promotion by digest. Lineage independence, which is Proposed (ADR-0035)", "As the corpus states it today",
         ""],
        ["TM11", "**A colluding Observer**", "Stay silent",
         "Nothing. Coupling cannot see collusion (A13). Declared on another vehicle, it shares no hardware with its "
         "Thinker and may share its lineage. Declared on the same vehicle, no claim rests on it (ADR-0062 §8)",
         "As the corpus states it today", ""],
        ["TM12", "**Attrition**: vehicles destroyed, or silenced until their replicas are dropped",
         "Take a plane below a quorum of its membership",
         "The shrink schedule (ADR-0061 §3): at the archetype's size, four losses one at a time or two at once",
         "Below the capture floor the plane ends and every survivor is alone. An adversary that can silence "
         "vehicles gets the floor's tolerance from the start",
         "Membership `StepInSchedule`, `StepAtFloor`, `StepByQuorum`, `AtMostOneSuccessor` (together "
         "`OneSuccessor`), **at five replicas and not at seven** (ADR-0061 R1), **under** `CapturedWithinFloor`; at "
         "the archetype's schedule the floor is redundant (a finding). Alone `AlonePermitsNothing`, for the "
         "survivors"],
        ["TM13", "**A stack that lies to its peers**, under a signature that verifies",
         "Report false tracks, claim every task, send another stack text meant to steer it",
         "Nothing a peer originates enables anything. Its reports are `untrusted`, and listening narrows (ADR-0065)",
         "An honest stack misled inside its own envelope, and peers stalled by claims. These are the swarm "
         "reading's two hardest classes, and nothing here rests on detecting them",
         "Peer `PeerAddsNothing`, `NarrowsInReceived`, `ReceivedIsUntrusted`, ranging over what a peer "
         "originates: a relayed lease does enable (a finding). What a stack does with a report is not modelled"],
        ["TM14", "**Clock faults** among a plane's replicas", "A slow clock holds an intent open, and a fast one "
         "ends it early",
         "Captured and slow replicas together fewer than a certificate (ADR-0064). A fast clock only subtracts",
         "Past that, the duration bound is void. The bound in effects still holds",
         "PlaneClock `NoGrantPastExpiry`, **under its premise** `ClockPremise`, captured and slow fewer than a "
         "certificate (`M_TOOSLOW` waives it and the bound fails), in discrete time; `NoStretchUnlessSlow`. The bound "
         "in effects: Outstanding `EffectsAfterRevocationBounded`, with no clock"],
    ]
    cols = [("#", 82, {"bold": True}), ("Adversary", 330), ("What it can do", 470), ("What bounds it", 650),
            ("What is left", 700)]
    xw = WW - sum(cc[1] for cc in cols)
    cols.append(("Module property that now states the bound", xw))
    rows = []
    for r in t1:
        rows.append({"cells": r[:5] + [r[5] if r[5] else ""], "accent": "red"})
    ty = y + 40
    th = c.table(X0, ty, cols, rows, size=13.5, accent="red")
    xref_frame(c, X0 + WW - xw, ty, xw, th, "The diagram's cross-reference, not ADR-0068's: a module header "
               "names the property; checked and proved 2026.11.10")
    y = ty + th + 16
    y += c.para(X0, y, WW, "**Out of scope** (§1): the destruction of vehicles or planes, other than its effect on a "
                "quorum, which is TM12; attacks on sensors other than as TM8 and TM9; what an adversary learns by "
                "watching which planes and vehicles talk; and the security of the anchor's custody, which ADR-0025 "
                "declares per deployment.", 14.5, "ink")
    y += 8
    y += c.para(X0, y, WW, "[[teal|The last column is the diagram's.]] A cell is empty where no module header names "
                "a property for that bound: TM4 (every module takes a commit certificate as unforgeable, and "
                "Membership abstracts PBFT to its certificate, so ADR-0061's \"PBFT is read\" is not met), TM7, TM8, "
                "TM9, TM10, and TM11 (Alone's `LocalNeverWaits` and Release's `ReleaseNeverCoupled` say nothing waits "
                "on an Observer, which bounds no collusion). **A property stated under a premise says so.** The "
                "Consequences say three adversaries have \"nothing\" in the bounding column; two are bounded by "
                "nothing (TM8, TM11), and TM13's cell begins \"Nothing a peer originates enables anything\", which is "
                "a bound.", 14,
                "muted") + 80

    # ================================================================== band 3: §2's rows
    y = band(c, X0, y, "§2 · Twelve rows for the trusted base, classed by failure direction, drawn by class as G1 "
             "draws ADR-0045's", status="proposed")
    y += c.legend(X0, y, [("box", "blue", "trust root (failure can add; trusted anyway)"),
                          ("box", "red", "a residual, in the slow direction (residual risk)"),
                          ("box", "green", "delegated (failure only subtracts)"),
                          ("box", "teal", "existing rows, instantiated on every vehicle")],
                  title="Row tint = class") + 8
    y += c.legend(X0, y, [("line", "red", "Findings 1: trust roots that meet neither half of ADR-0045's test as "
                                          "they stand")], title="Heavy red frame") + 18
    t2 = {
        "1": ["The governor's admit path, which now makes every `local` permit", "Trust root",
              "Anything the stack requests may reach an actuator"],
        "2": ["The governor's clock", "A residual, in the slow direction",
              "It finds a tick overdue late. An entry in progress runs on, and only when the plane's ticks have also "
              "stopped reaching it (ADR-0064)"],
        "3": ["A plane's clocks, taken together", "Trust root for the duration bound only",
              "With captured and slow replicas at a certificate or more, an intent outlives its `expiry`. The bound "
              "in effects still holds"],
        "4": ["The governor's measure of an extent", "Trust root for an entry whose extent is a distance or a region",
              "An entry runs past what was voted"],
        "5": ["The intent boundary's reading", "Trust root for the watermark",
              "A watermark for a record nobody checked releases a charge nobody read"],
        "6": ["The governor's key store", "Trust root",
              "The vehicle's principal, and its replica, are whoever holds the key"],
        "7": ["The navigation source", "Trust root for area checks", "The envelope is somewhere else"],
        "8": ["The effector interlock", "Trust root", "An irreversible effect without a person's act"],
        "9": ["The recovery function", "Trust root for the terminal behaviour", "Expiry with no safe state"],
        "10": ["Cedar and the Wasm engine on the vehicle", "Existing rows, instantiated on every vehicle",
               "As those rows say"],
        "11": ["The link and the radios", "Delegated",
               "Loss only subtracts: a plane cut off above stops granting before `K_up`, and a vehicle cut off from "
               "its plane loses its lease. The NATO reading's F2 found this inexact of the proposal's first revision, "
               "where a vehicle alone kept entries and lost checks"],
        "12": ["Byzantine agreement at an exposed plane, with its reconfiguration step (ADR-0061)",
               "Trust root, in place of the replica row there", "A forged certificate, or two successors to one "
               "membership"],
    }
    owed = "Not yet read against the test: that reading is §6's second condition, and an open obligation"
    gov = (" It rests on **what attests a governor at seating**, as ADR-0034 attests a guest, which no record of "
           "this set says (Open obligations)")
    f1 = ("[[red|Meets neither half as it stands]]: its failure can add, and nothing issues its identity. Either an "
          "attested identity is declared per vehicle class, as ADR-0034 does for a guest, or it becomes an "
          "assumption of use with an owner (Findings 1)")
    note = {
        "1": owed + "." + gov + ". Federation and Outstanding state their governors honest",
        "2": "The shape of ADR-0045's finding 2, as ADR-0064 §5 says; Annex A's local clock T-0045-4 is delegated, "
             "with that finding as its residual. PlaneClock: `NoStretchUnlessSlow`, and the witness `NeverStretched` shows the "
             "residual reachable",
        "3": owed + ". PlaneClock's `ClockPremise` is this row's premise, and A-0068-2's",
        "4": f1 + ". PlaneClock counts an extent in ticks: \"distance and region are measurements (ADR-0068)\"",
        "5": owed + ". Outstanding takes the boundary's truth as the record's: \"a watermark exists only if the "
             "boundary ordered it\"",
        "6": owed + "." + gov,
        "7": f1 + ". No module models a position",
        "8": f1 + ". Release relies on the interlock's checks alone, so it takes this row as its premise and does "
             "not discharge it",
        "9": f1 + ". Alone: \"reaching a safe state is physics, and is not here\"",
        "10": "The record names no ids. In ADR-0045's Annex A the Cedar engine is T-0045-3, a trust root, and the "
              "bundle-tier engines T-0045-6, delegated",
        "11": "Delegated is admitted by the first half: its failure can only subtract",
        "12": owed + ". It stands in place of T-0045-1 at an exposed plane; Membership's `AtMostOneSuccessor` states its "
              "second failure absent, at five replicas under `CapturedWithinFloor`, the certificate taken as unforgeable",
    }
    groups = [
        ("Trust root · five rows", "blue", [("1", "blue"), ("3", "blue"), ("5", "blue"), ("6", "blue"),
                                            ("12", "blue")]),
        ("Trust root, and neither half of ADR-0045's test met as they stand · four rows (Findings 1; §6)", "red",
         [("4", "blue"), ("7", "blue"), ("8", "blue"), ("9", "blue")]),
        ("A residual, in the slow direction · one row", "red", [("2", "red")]),
        ("Delegated · one row", "green", [("11", "green")]),
        ("Existing rows, instantiated on every vehicle · one row", "teal", [("10", "teal")]),
    ]
    rows = []
    n = 0
    for gi, (gt, ga, members) in enumerate(groups):
        if gi == 1:
            n_before = len(rows)
        if gi == 2:
            n_f1 = len(rows) - n_before
        rows.append({"group": gt, "accent": ga})
        for k, acc in members:
            r = t2[k]
            rows.append({"cells": [f"**T-0068-{k}**", r[0], r[1], r[2], note[k]], "accent": acc})
            n += 1
    assert n == 12
    cols = [("Id", 150), ("Row", 560), ("Class", 400), ("If it fails", 900)]
    xw2 = WW - sum(cc[1] for cc in cols)
    cols.append(("Against ADR-0045's test, and what the modules take", xw2))
    ty = y + 40
    th = c.table(X0, ty, cols, rows, size=13.5, accent="blue")
    h_pre = c.table(X0, ty, cols, rows[:n_before], size=13.5, accent="blue", draw=False)
    h_f1 = c.table(X0, ty, cols, rows[n_before:n_before + n_f1], size=13.5, accent="blue", draw=False,
                   header=False)
    c.rect(X0 - 4, ty + h_pre - 2, WW + 8, h_f1 + 4, "red", tint=False, sw=4, rx=3)
    c.out[-1] = c.out[-1].replace('fill="#ffffff" ', 'fill="none" ').replace("f-bg ", "")
    xref_frame(c, X0 + WW - xw2, ty, xw2, th, "The diagram's reading of §6, Findings 1 and the Open obligations, "
               "with the module headers; not ADR-0068's column")
    y = ty + th + 18
    y += c.para(X0, y, WW, "**Models stay out of the trusted base. The base still grows, on every vehicle** (§2). "
                "Grouping is the diagram's; the record lists the rows T-0068-1 to 12 in order.", 14.5, "ink") + 26

    # ADR-0045's test, and Findings 1
    hT = row_cards(c, X0, y, WW, 30, [
        ("ADR-0045 §2: a component is a row only if its failure can only subtract, or its identity is issued", [
            "**Delegated**: its failure can produce only subtractions. No proof, no key, no quorum; declared per "
            "deployment.",
            "**Trust root**: its failure can add, and it is admissible only if **both** hold: its identity is fixed "
            "by an anchor issuance or a promotion, **and** it entered by a record of its own.",
            "**Refused**: a component whose failure can add and whose identity neither issuance nor promotion fixes "
            "is not a row. It moves inside the verified object, or the design changes until its failure only "
            "subtracts.",
        ], "blue", {}),
        ("Findings 1: four rows meet neither half", [
            "**T-0068-4** a vehicle's measure of an extent, **T-0068-7** its position source, **T-0068-8** its "
            "interlock, **T-0068-9** its recovery function.",
            "Their failure can add (an entry past what was voted, an envelope elsewhere, an irreversible effect "
            "without a person, expiry with no safe state), and **nothing issues their identity**: they are trusted "
            "for what their builder says of them (Consequences).",
            "**Either an attested identity for each is declared per vehicle class**, as ADR-0034 does for a guest, "
            "**or they are assumptions of use with an owner.** The record lists them as rows and says so.",
        ], "red", {"tint": False, "dash": "6 4"}),
        ("Finding 2, and where the rows would go (§5)", [
            "ADR-0045 §4: a deployment \"instantiates rows and adds none that is not a degeneracy\". **An overlay that "
            "adds twelve is outside that sentence**, one more reason this is reported upstream and not declared as a "
            "rung.",
            "**If the archetype takes ADR-0059 to ADR-0067**, ADR-0045 owes these rows in its table and a declaration "
            "of them in every deployment that seats a governor.",
            "**Not an annex to ADR-0045** while this is an overlay ⟨Q11⟩: ADR-0045 is accepted, and an annex would "
            "amend it (Options).",
        ], "amber", {"tint": False}),
    ], size=14)
    y += hT + 80

    # ================================================================== band 4: §3's assumptions
    y = band(c, X0, y, "§3 · Ten assumptions of use", status="proposed")
    y += c.para(X0, y, WW, "**A deployment that does not meet one does not inherit what the modules of ADR-0059 to "
                "ADR-0066 would prove** (§3). The sentence was written before the modules; they now exist, and the "
                "cross-reference below says where a module carries an assumption as its premise.", 14.5, "ink") + 14
    t3 = [
        ["A-0068-1", "The governor is separate from the stack and is the only path to the actuators and the radio",
         "The stack is `Mediated`, and every property here is void. This is A1 for a vehicle"],
        ["A-0068-2", "Captured and slow replicas together are fewer than a certificate, and each sound clock's margin "
         "covers its drift", "`NoGrantPastExpiry` is void. `EffectsAfterRevocationBounded` is not"],
        ["A-0068-3", "Effect classes are declared as what they are",
         "An irreversible effect is reachable by an agent, or by a governor alone"],
        ["A-0068-4", "Each vehicle class has a declared safe state, and its recovery function reaches it in bounded "
         "time", "The terminal behaviour is a stall, which for a body in motion is not safe"],
        ["A-0068-5", "A trained, authorized person is at each release seat and can see what the act requires",
         "HITL is a key and not a judgment"],
        ["A-0068-6", "No more replicas of an exposed plane are captured than its current membership tolerates, at "
         "every step of its schedule", "That plane is captured. It is bounded by its charter or intent, and by each "
         "honest governor's account against `K_up`"],
        ["A-0068-7", "What a vehicle does to the world other than through its entries is declared as outside the "
         "alphabet", "Effect exclusivity is claimed for a body, and is false"],
        ["A-0068-8", "Every entry's extent is declared as what it is",
         "A count bounds how many acts and not what they do"],
        ["A-0068-9", "Envelopes, counts and budgets are voted against what every stack could do together",
         "The joint effect of permitted acts is one no tally weighed"],
        ["A-0068-10", "`T_tick` is long against a round of the plane over its radios",
         "Ticks fall behind and leases end, with no adversary present"],
    ]
    xr3 = {
        "A-0068-1": "Federation (`Verifiers` are honest) and Outstanding (two governors, honest) say so in their "
                    "headers",
        "A-0068-2": "The first half is PlaneClock's `ClockPremise`. The second is folded into a clock's class there "
                    "(\"margins are folded into a clock's class\"); the module says nothing of a real clock's drift. "
                    "Outstanding has no clock",
        "A-0068-6": "Membership's `CapturedWithinFloor`, with `StepAtFloor` keeping the tolerance at or above it, at "
                    "five replicas",
        "A-0068-8": "PlaneClock models an extent as a number of ticks only",
    }
    cols = [("Id", 150, {"bold": True}), ("Assumption", 960), ("If it does not hold", 900)]
    xw3 = WW - sum(cc[1] for cc in cols)
    cols.append(("Where a module takes it as a premise", xw3))
    rows = [{"cells": r + [xr3.get(r[0], "")], "accent": "amber"} for r in t3]
    ty = y + 40
    th = c.table(X0, ty, cols, rows, size=13.5, accent="amber")
    xref_frame(c, X0 + WW - xw3, ty, xw3, th, "The diagram's cross-reference to the module headers, not ADR-0068's")
    y = ty + th + 22
    hT = row_cards(c, X0, y, WW, 30, [
        ("ToO rev 15 §13, as ADR-0068 cites it", [
            "**A1**: effect exclusivity is enforced by a declared, attested confinement profile. A-0068-1 is \"A1 for "
            "a vehicle\".",
            "**A9**: the mechanism's replicas are not compromised, crash-recovery. TM4: under crash-recovery "
            "consensus one such replica can propose an admit no floor evaluated, which is why ADR-0059 §5 asks for "
            "Byzantine agreement.",
            "**A13**: the cell Observer is not colluding with its Thinker. TM11: coupling cannot see collusion.",
        ], "grey", {"tint": False}),
        ("§5 · Overlay position ⟨Q11⟩", [
            "**If the archetype takes ADR-0059 to ADR-0067, its records owe:** ADR-0045, these rows in its table and a "
            "declaration of them in every deployment that seats a governor; **ToO §13, these assumptions beside A1 "
            "to A18.**",
            "Until then the overlay declares them here, as ADR-0045's Annex B is the reference's declaration. "
            "**Carries a debt against**: nothing while this is an overlay.",
        ], "amber", {"tint": False}),
    ], size=14)
    y += hT + 80

    # ================================================================== band 5: §4
    y = band(c, X0, y, "§4 · What is given up, in one place: each record names its own costs, and together",
             status="proposed")
    gu = [
        ("1", "**No delegation.** Planes grant below themselves", "ADR-0059"),
        ("2", "**A bound in seconds as a theorem.** Revocation is bounded in effects, and the bound in duration is "
              "declared", "ADR-0063, ADR-0064"),
        ("3", "**An ordered admit before every effect**, for every pre-authorized entry and every report to a peer",
         "ADR-0062, ADR-0065"),
        ("4", "**A person in reach**, for a plane that is cut off", "ADR-0060"),
        ("5", "**Any act by a vehicle that is alone**", "ADR-0062"),
        ("6", "**Inexpressibility of irreversible effects**", "ADR-0066"),
        ("7", "**A small trusted base**", "§2"),
        ("8", "**A fixed capture threshold**", "ADR-0061"),
        ("9", "**One bus**", "ADR-0065"),
        ("10", "**\"Not autonomous.\"** No principal seats, delegates to or addresses another, and that stays true. "
               "It is no longer true that a person is always on the plane that orders an effect", ""),
    ]
    half = (WW - 40) / 2
    cols = [("#", 70, {"bold": True}), ("Given up", half - 70 - 260), ("Where", 260)]
    ta = c.table(X0, y, cols, [[a, b, cc] for a, b, cc in gu[:5]], size=14, accent="grey")
    tb = c.table(X0 + half + 40, y, cols, [[a, b, cc] for a, b, cc in gu[5:]], size=14, accent="grey")
    y += max(ta, tb) + 80

    # ================================================================== band 6: §6, options, consequences
    y = band(c, X0, y, "§6 · Ratification condition, item by item, with the diagram's note on each",
             status="proposed")
    cols = [("Condition (§6)", 620, {"bold": True}), ("As the record states it", 1180)]
    xw6 = WW - sum(cc[1] for cc in cols)
    cols.append(("The diagram's note, 2026.11.10", xw6))
    rows = [
        {"cells": ["ADR-0059 to ADR-0067 are ratified first, or with this record",
                   "A row for a record that is not ratified is withdrawn with it",
                   "None is ratified. All nine are Proposed; ADR-0059 to ADR-0067 were each revised R1 on 2026.11.10"],
         "accent": "amber"},
        {"cells": ["Each row is read against ADR-0045's test: its failure can only subtract, or its identity is issued",
                   "[[red|Not met.]] Four rows here are trust roots whose identity nothing issues: a vehicle's measure "
                   "of an extent, its position source, its interlock and its recovery function. That is a finding "
                   "(Findings, 1)",
                   "Unchanged by the modules. None models these four: PlaneClock counts an extent in ticks, no module "
                   "has a position, Release relies on the interlock's checks, and Alone leaves the safe state to "
                   "physics"], "accent": "red"},
        {"cells": ["Each bound in §1 names a property of a module that exists",
                   "[[red|Not met: no module is written.]]",
                   "[[red|Out of date, and not revised.]] The modules of ADR-0059 to ADR-0066 were written, checked "
                   "and proved on 2026.11.10 (the modules table at the top). The cross-reference column of §1's table finds a property in a "
                   "module header for TM1–TM3, TM5, TM6 and TM12–TM14, several under a premise, and none for TM4 and "
                   "TM7–TM11. ADR-0068 names none of them, so as written the condition is still not met"],
         "accent": "red"},
        {"cells": ["A reader who is not the drafter (ADR-0029 A2)", "And for this record, one who knows vehicles",
                   "No reading is recorded: the History has one row, the initial draft"], "accent": "amber"},
    ]
    ty = y + 40
    th = c.table(X0, ty, cols, rows, size=14, accent="amber")
    xref_frame(c, X0 + WW - xw6, ty, xw6, th, "The diagram's note, not ADR-0068's text")
    y = ty + th + 70

    y = band(c, X0, y, "Options considered, whole")
    cols = [("Option", 900, {"bold": True}), ("Disposition", WW - 900)]
    th = c.table(X0, y, cols, [
        {"cells": ["An annex to ADR-0045", "[[grey|Not taken]] while this is an overlay ⟨Q11⟩. ADR-0045 is accepted, "
                   "and an annex would amend it"], "accent": "grey"},
        {"cells": ["The rows spread over the records they belong to", "[[grey|Not taken.]] ADR-0045's rule is one "
                   "table, so that an undeclared row can be seen to be missing"], "accent": "grey"},
        {"cells": ["The corpus's adversary alone, the agent", "[[red|Rejected ⟨3⟩.]] A link adversary and a captured "
                   "vehicle are the ordinary case for this deployment"], "accent": "red"},
        {"cells": ["Physical destruction out of scope, as the proposal's first revision had it", "[[grey|Not "
                   "taken.]] Its effect on a quorum is TM12"], "accent": "grey"},
    ], size=14, accent="grey")
    y += th + 70

    y = band(c, X0, y, "Consequences, Findings and Open obligations")
    g = 36
    w3 = (WW - 2 * g) / 3
    xs = [X0, X0 + w3 + g, X0 + 2 * (w3 + g)]
    b1 = stack(c, xs[0], y, w3, [
        ("Positive", [
            "**One table of what the overlay trusts**, and one of what it assumes.",
            "**Each adversary has a stated residual**, and three of them have \"nothing\" in the bounding column where "
            "that is the truth.",
        ], "green", {}),
        ("Negative", [
            "**Trust roots nothing issues.** A vehicle's position source, its measure of an extent, its interlock and "
            "its recovery function are trusted for what their builder says of them.",
            "**Navigation deception is bounded by nothing here** (TM8).",
            "**Collusion is unseen**, as the corpus states it today (TM11).",
            "**One author, one day, and no vehicle.**",
        ], "red", {"tint": False}),
    ], gap=18, size=14)
    b2 = stack(c, xs[1], y, w3, [
        ("Findings", [
            "**1. ADR-0045 admits a component only if its failure can only subtract, or its identity is issued.** "
            "Four rows here meet neither as they stand: T-0068-4, T-0068-7, T-0068-8 and T-0068-9, a vehicle's "
            "measure of an extent, its position source, its interlock and its recovery function. Either an attested "
            "identity for each is declared per vehicle class, as ADR-0034 does for a guest, or they are assumptions "
            "of use with an owner. The record lists them as rows and says so.",
            "**2. A deployment \"instantiates rows and adds none that is not a degeneracy\"** (ADR-0045 §4, in the "
            "words of ADR-0058's header). An overlay that adds twelve is outside that sentence, which is one more "
            "reason this is reported upstream and not declared as a rung.",
            "**3. Two readings found gaps this record leaves open**: a captured vehicle discloses the rules it "
            "carries (the NATO reading, F3), and TM3's \"once its plane knows\" names no way of knowing (the swarm "
            "reading, Z2).",
        ], "red", {"tint": False}),
    ], size=14)
    b3 = stack(c, xs[2], y, w3, [
        ("Open obligations", [
            "**The reading of each row against ADR-0045** (§6), and the disposition of finding 1.",
            "**What attests a governor at seating**, as ADR-0034 attests a guest. T-0068-1 and T-0068-6 rest on it, "
            "and no record of this set says.",
            "**A false-finding rate for a plane with nobody in reach**, as an availability parameter (the swarm "
            "reading, Z3).",
            "**An Observer that accuses or vanishes**, beside TM11's silent one (the swarm reading, Z4).",
            "**A second anchor**, for a coalition, which is out of this design (the NATO reading, N2).",
            "**Disclosure on capture**, as a row or as an adversary's capability in TM3 (the NATO reading, F3).",
        ], "red", {"tint": False, "status": "open"}),
        ("The diagram's note: what would meet §6's third condition", [
            "Not listed by the record. **An R1 revision of ADR-0068** naming, for each bound in §1, the module "
            "property that states it, as the R1 rows of ADR-0059 to ADR-0066 cite their modules, with its Status "
            "note brought up to date. Until then the condition reads \"not met\".",
        ], "teal", {"tint": False, "dash": "7 5"}),
    ], gap=18, size=14)
    c.ymax = max(c.ymax, b1, b2, b3)
    return c
