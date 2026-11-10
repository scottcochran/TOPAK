"""B9 — A tree of planes (ADR-0059, Proposed) and the shrinking membership of an autonomous plane (ADR-0061,
Proposed), both revised R1 after spec/Federation.tla and spec/Membership.tla were checked and proved. Each plane is
seated under a charter it can only narrow, is a havoc issuer bounded by that charter, is fenced by every plane above
it, and is run by replicas whose membership shrinks only by a voted schedule."""
from lib import Canvas, STATUS, STATE_CC, text_width

ID, SLUG = "B9", "planes-and-charters"

W = 3400
S = 14


def row_cards(c, x, y, w, gap, specs, size=S):
    """A row of cards of equal height, measured over every card. specs: (title, body, accent, kwargs)."""
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
    c.text(x, y + 22, title, 22, accent, bold=True)
    if status:
        c.status(x + text_width(title, 22, True) + 20, y + 4, status, extra)
    return y + 54


def sub(c, x, y, s, size=16):
    c.text(x, y + size, s, size, "ink")
    return size + 16


BR = "[[red|breaks]]"
HO = "[[green|holds]]"


def build():
    c = Canvas(
        ID, "A tree of planes: each seated under a charter it can only narrow, bounded as a havoc issuer, fenced by "
            "every plane above, and run by replicas whose membership shrinks only by a voted schedule",
        "\"No principal grants another, so there is no chain of delegation to attenuate\" (ToO §2.11). The custodian "
        "asked what follows if TOPAK is the top tier of a command chain, with control planes below it that only "
        "narrow ⟨1⟩. **ADR-0059 places it**: the grantor is a mechanism and not a model, the delegation only "
        "attenuates, and it is budgeted. **ADR-0061** gives an autonomous plane seven replicas under Byzantine "
        "agreement and a membership that shrinks only along a schedule its charter voted, down to a capture floor. "
        "**Both are Proposed overlays, revised R1 on 2026.11.10** after their modules were checked and proved: R1 "
        "narrowed what the budget bounds, and added the one-vote rule. **Nothing here is in force and nothing is "
        "built.**",
        W, "ADR-0059 (Proposed, R1): provenance note, Status note, Context, Decision §1–§9 (§1's table, §3's table), "
        "Options considered, Consequences, Open obligations, Annex A (⟨Q1⟩, ⟨Q7⟩, ⟨Q8⟩, ⟨Q11⟩), History (R1); "
        "ADR-0061 (Proposed, R1): provenance note, Status note, Context, Decision §1–§7 (§1's table, §4's table), "
        "Options considered, Consequences, Open obligations, History (R1); ADR-0067 §3 (`FD1`–`FD4`, `FD13`; "
        "Proposed); ADR-0058, ADR-0060 (Status lines); floor/proposed/ (no `federation` stage); "
        "spec/Federation.tla (03e0bbb28b5e9a1d: header, actions, properties, witnesses), spec/Federation-rows.txt, "
        "spec/Federation-results-2026.11.10.txt (7e8e63ddd7fc4475), spec/Federation_proof.tla (cb0264730a865d32: "
        "`Account`), spec/Federation-proof-results-2026.11.10.txt (8976255e169de16e), "
        "spec/Federation-proof-cert-results-2026.11.10.txt (5f19d7acc5ad3c70); spec/Membership.tla "
        "(bcf3c5d151488133: header, actions, properties, witnesses), spec/Membership-rows.txt, "
        "spec/Membership-results-2026.11.10.txt (6974af8a38a4b879), spec/Membership_proof.tla (c88b8ed201aa5448), "
        "spec/Membership-proof-results-2026.11.10.txt (adb21d8a7708d041), "
        "spec/Membership-proof-cert-results-2026.11.10.txt (7b58fb5eb2bbf25d)",
        state=STATE_CC)
    X0, X1 = c.x0, c.x1
    WW = X1 - X0
    y = c.y

    # ================================================================== status strip
    c.text(X0, y + 15, "Status", 15, "faint", bold=True)
    px0 = X0 + 80
    px = px0
    PROP = STATUS["proposed"]
    strip = [
        ("ADR-0059", [("proposed", "C1 · an overlay, not the archetype")]),
        ("ADR-0061", [("proposed", "C1 · an overlay, not the archetype")]),
        ("`spec/Federation.tla`", [("Checked · 41 rows, all as expected", "teal", None),
                                   ("Proved · 892 obligations", "teal", None)]),
        ("`spec/Membership.tla`", [("Checked · 28 rows, all as expected", "teal", None),
                                   ("Proved · 495 obligations · at five replicas, not seven", "teal", None)]),
        ("floor stage `federation`: `FD1`–`FD3`, `FD13`", [("Not written", "red", "2 3")]),
        ("the reference", [("notbuilt", "")]),
        ("PBFT (ADR-0061 §7)", [("Not read", "red", "2 3")]),
    ]
    for lab, pills in strip:
        lw = text_width(lab, 13.5, True) + 8
        pw = 0
        for p in pills:
            txt = (STATUS[p[0]][0] + (f" · {p[1]}" if p[1] else "")) if len(p) == 2 else p[0]
            pw += text_width(txt, 11.5, True) + 18 + 8
        if px + lw + pw > X1:
            px = px0
            y += 34
        c.text(px, y + 15, lab, 13.5, "ink", bold=True)
        px += lw
        for p in pills:
            if len(p) == 2:
                px += c.status(px, y, p[0], p[1]) + 8
            else:
                px += c.pill(px, y, p[0], p[1], 11.5, dash=p[2]) + 8
        px += 20
    y += 42
    y += c.para(X0, y, WW, "**Proposed means nothing here is in force.** **C1** applies to ADR-0059 because every "
                "grant below the root travels the path it opens, and to ADR-0061 because who may form a certificate "
                "is who may grant, and its §3 changes that at run time. **C3** applies to neither while each is an "
                "overlay ⟨Q11⟩, and would apply on admission to the archetype. **What exists is two models**: TLC "
                "rows are checked at small constants, TLAPS obligations are proved, and each proof module is "
                "**certified, with 7 (Federation) and 6 (Membership) LS4 temporal steps that no checker confirms**. "
                "Membership is checked and proved at five replicas, not at §1's seven. One author, one day.",
                14.5, "muted") + 34

    # ================================================================== band 1: the chain, and the charter
    y = band(c, X0, y, "A chain, from the root to a lease, with a charter on each link (ADR-0059 §1–§6)",
             status="proposed", extra="nothing here is built")
    top = y + 30
    xf = X0 + 120            # the fence lane
    chx = X0 + 270           # the chain's cards
    chw = 820
    chr_ = chx + chw
    xl = chr_ + 100          # the certificate lane
    xr = X0 + 1640           # the right column
    wr = X1 - xr

    ROOT = ("Plane r · the root", [
        "**One replica set, one log, one epoch, one set of rules in force** (§1).",
        "**Its tally is honest**: ADR-0025 bounds the anchor by the floor, which is another module's question "
        "(Federation.tla's header).",
        "**The anchor's key is resident at every verifier**, as genesis rules are (§5; ADR-0027).",
    ], "violet")
    CHA = ("Charter a · seated by a promotion at r (§1, §3)", [
        "**Every field r's or narrower**: an `alphabet` that is a subset, a `budget` no larger, an `expiry` no "
        "later.",
        "**Its `budget` is debited from r's** when a is seated.",
        "**A commit certificate**: a quorum of r's replicas over its digest and log index (§5).",
        "**`fences`**: r's epoch and log index at the seating (§6).",
    ], "amber")
    PLA = ("Plane a", [
        "**A havoc issuer, bounded by its charter** (§4).",
        "**Runs Byzantine agreement if its replicas can be captured**, and declares it (§5 ⟨Q7⟩).",
        "**The bundles it adds are appended**: they can refuse, and are never asked whether to grant (§2).",
    ], "violet")
    CHB = ("Charter b · seated by a promotion at a", [
        "**a's or narrower, field by field**, and so r's or narrower.",
        "**Its `budget` is debited from a's.**",
        "**Certified by a quorum of a's replicas.** Its `fences` carry r's and a's epochs.",
    ], "amber")
    PLB = ("Plane b · the granting plane", [
        "**Orders a lease and spends a unit of its budget** (Federation.tla, `Issue`).",
        "**If captured, it decides which lease, never whether** (§4).",
    ], "violet")
    LEA = ("The lease (ADR-0031)", [
        "**Within every charter on its chain**, not only b's (§4).",
        "**A commit certificate** from a quorum of b's replicas (§5).",
        "**The epoch and log index of r, a and b** (§6).",
    ], "teal")
    VER = ("A verifier · a governor, or a plane's admit path", [
        "[[green|③]] **Compares the lease with every charter on the chain**, field by field (§1; ADR-0033 §4).",
        "**Checks every commit certificate from the anchor's key down** (§5).",
        "**Compares each plane's epoch with the latest it has heard** (§6).",
        "**Needs no plane in reach**: the chain is verified where there is no link (§5).",
    ], "teal")
    chain = [ROOT, CHA, PLA, CHB, PLB, LEA, VER]
    hs = [c.card(0, 0, chw, t, b, draw=False, size=S) for t, b, _ in chain]
    gap = 96
    ys = []
    yy = top + 40
    for h in hs:
        ys.append(yy)
        yy += h + gap
    chain_bot = ys[-1] + hs[-1]

    # region: the chain (charters from the root to the granting plane, and the lease)
    c.region(chx - 30, ys[0] - 40, chw + 60, ys[5] + hs[5] - ys[0] + 70,
             "A chain (§1): the charters from the root down to a granting plane, with a lease at the end", "blue",
             dash="10 6")
    for (t, b, acc), yy_ in zip(chain, ys):
        c.card(chx, yy_, chw, t, b, accent=acc, size=S, tint=acc != "teal" or t.startswith("The lease"))
    mx = chx + chw / 2
    labels = ["[[green|①]] checked, then voted by r's grant seats' tally",
              "[[green|②]] checked again when the seating is applied",
              "[[green|①]] checked, then voted by a's grant seats' tally",
              "[[green|②]] checked again when applied",
              "orders and signs",
              "presented, with its chain"]
    accs = ["blue", "blue", "blue", "blue", "violet", "teal"]
    for i in range(6):
        c.arrow([(mx, ys[i] + hs[i]), (mx, ys[i + 1])], accs[i], sw=2.4, label=labels[i], lpos=0.5, lw=440)

    # the certificate lane: from the anchor's key down to the verifier
    r_mid = ys[0] + hs[0] / 2
    v_mid = ys[6] + hs[6] / 2
    c.arrow([(chr_, r_mid), (xl, r_mid), (xl, v_mid), (chr_, v_mid)], "teal", sw=2.4)
    for i in (1, 3, 5):
        c.line(chr_, ys[i] + hs[i] / 2, xl, ys[i] + hs[i] / 2, "teal", sw=1.6, dash="2 3")
    c.label(xl, (ys[2] + ys[3] + hs[2]) / 2 + 40, "[[green|③]] every commit certificate, checked from the "
            "anchor's key down (§5)", "teal", 12.5, 220)

    # the plane fence: a moves its epoch, and everything below it is fenced
    a_mid = ys[2] + hs[2] / 2
    c.arrow([(chx, a_mid), (xf, a_mid), (xf, v_mid), (chx, v_mid)], "green", dash="7 5", sw=2.4)
    for i in (4, 5):
        c.arrow([(xf, ys[i] + hs[i] / 2), (chx, ys[i] + hs[i] / 2)], "green", dash="7 5", sw=2)
    c.label(xf, (ys[3] + ys[4]) / 2 + 60, "plane fence: a moves its epoch, and everything below it is fenced "
            "(§6)", "green", 12.5, 200)

    # refusal at the verifier
    c.arrow([(mx, chain_bot), (mx, chain_bot + 70)], "red", dash="7 5", sw=2.2)
    c.label(mx, chain_bot + 96, "[[red|refused]]: outside a charter on the chain, a certificate that does not "
            "verify from the anchor down, or an older epoch of any plane", "red", 12.5, 520)
    pic_bot = chain_bot + 140

    lg = c.legend(X0, pic_bot, [
        ("box", "violet", "a plane's replicas (consensus)"),
        ("box", "amber", "a charter (Proposed)"),
        ("arrow", "blue", "a seating: a promotion"),
        ("arrow", "teal", "the verifier's check"),
        ("arrow", "green", "a plane fence: subtraction", "7 5"),
        ("arrow", "red", "refused", "7 5"),
    ], maxw=xr - X0 - 60)
    left_bot = pic_bot + lg

    # ---- right column: §1's table, its bullets, and §3's table
    ry = top
    ry += sub(c, xr, ry, "**§1's charter, whole.** A closed schema, as the lease has (ADR-0031): a capability that "
              "is not a field is not carried")
    cols = [("Field", wr * 0.2), ("What it bounds (§1)", wr * 0.5), ("In `Federation.tla` (its header)", wr * 0.3)]
    rows = [
        ["`plane`, `replicas`", "The child's identity: its replica keys and its quorum rule",
         "Not modelled: `seated` stands for it; membership is `Membership.tla`'s"],
        ["`kind`", "`commanded` or `autonomous` (ADR-0060)", "Not modelled"],
        ["`parent`, `fences`", "Where it hangs, and the epoch and log index of every plane above it at the seating "
         "(§6)", "**`fence`**: the parent's epoch at the seating, the one value in `fences` the plane above has "
         "signed"],
        ["`floor`", "The floor's digest, which equals the parent's (§2)", "Not modelled"],
        ["`bundles`", "The parent's list of bundle revisions, in order, plus any this seating adds",
         "Not modelled: the shape of `alphabet`"],
        ["`alphabet`, `labels`", "The entries and labels a lease under this charter may carry",
         "**`alphabet`**: a set, narrowed by subset. `labels` has its shape, not repeated"],
        ["`ttlMax`, `countMax`", "The longest lease `ttl` the plane may grant and the largest count, per effect "
         "class", "Not modelled: the shape of the first two"],
        ["`budget`", "The most leases the plane and every plane below it may ever issue",
         "**`budget`**: a number, narrowed by ≤ and debited"],
        ["`expiry`", "The charter's own life. Never later than the parent's", "Not modelled: the shape of the first two"],
        ["`release`", "Whether a release seat may be seated at this plane (ADR-0066)", "Not modelled"],
    ]
    ry += c.table(xr, ry, cols, rows, size=14, accent="amber") + 22
    ry = stack(c, xr, ry, wr, [
        ("Field by field, three times (§1)", [
            "**Every field is the parent's or narrower.** The comparison is field by field, and it is made three "
            "times: [[green|①]] **before the vote**, [[green|②]] **when the seating is applied**, and [[green|③]] "
            "**by every verifier of the chain** (ADR-0033 §4).",
            "**A plane** is one replica set with one log, one epoch and one set of rules in force. Its parent seats "
            "it by voting on a charter, as it votes on any seating (ADR-0024 A3).",
            "**A child's `budget` is debited from its parent's** when it is seated. What the debit bounds, and what "
            "it does not, is R1's finding (the next band).",
            "**ADR-0060, ADR-0061, ADR-0063 and ADR-0064 add fields that only an autonomous plane carries.** "
            "ADR-0061's is `membership` (the band on ADR-0061).",
        ], "amber", {}),
    ]) + 34
    ry += sub(c, xr, ry, "**§3's table, whole: what kind of act a narrowing is** ⟨8⟩ ⟨Q1⟩. \"Adding takes a quorum, "
              "and denying is local\" (ToO §7.10)")
    cols = [("Narrowing", wr * 0.17, {"bold": True}), ("Example", wr * 0.22), ("What it is", wr * 0.37),
            ("Who acts", wr * 0.24)]
    rows = [
        {"cells": ["A new issuer", "Seating a plane under a charter", "**A promotion.** The charter is narrower than "
                   "its parent's, and it still creates something that can grant", "The parent's grant seats, by tally"],
         "accent": "blue"},
        {"cells": ["A new artifact", "A bundle with a mission's rules", "**A promotion.** \"Everything crossing from "
                   "Build to Run is promoted\" (ToO §7.1)", "The grant seats, by tally"], "accent": "blue"},
        {"cells": ["A round inside a promoted seating", "A commander's next intent (ADR-0060)", "**An ordered admit, "
                   "signed by one operator.** It adds nothing the tally did not vote",
                   "One operator, with a live lease and a live peer (ADR-0050)"], "accent": "brown"},
        {"cells": ["A step of a voted schedule", "Dropping a silent replica (ADR-0061)", "**An ordered admit by the "
                   "mechanism.** The schedule was the promotion's", "A quorum of the membership being replaced"],
         "accent": "violet"},
        {"cells": ["A value already in force, moved down", "A shorter `ttl`, a smaller budget, an entry removed, a "
                   "revocation, a fence", "**An ordered admit.** \"Runtime subtraction is not promotion\" (ToO §7.1)",
                   "One operator, or the mechanism"], "accent": "green"},
    ]
    ry += c.table(xr, ry, cols, rows, size=14, accent="blue") + 14
    ry += c.para(xr, ry, wr, "**A narrowing is a promotion when it brings a new issuer or a new artifact into force.** "
                 "Otherwise it is an admit, ordered by the plane's consensus and signed by one person or by the "
                 "mechanism ⟨Q1⟩. \"Quorum\" in the last three rows means the replicas' agreement on the order, and no "
                 "vote.", 14, "muted")
    ry += 34
    ry = stack(c, xr, ry, wr, [
        ("§2 · Policy narrows by composition, and there is one floor ⟨Q8⟩", [
            "**At any admit or permit, at any plane, the decision is the floor's permit and no refusal from any "
            "bundle on the chain.**",
            "**A bundle a lower plane adds is appended, can refuse, and is never asked whether to grant** "
            "(ToO §3.1).",
            "So \"narrower than the parent\" holds of the composed decision **for every bundle, at every plane, at "
            "every age**. This is ADR-0030's argument applied once per link, and **nothing compares two policies**.",
            "**One floor serves the whole tree** ⟨Q8⟩. Every charter carries the root's floor digest. Planes differ "
            "by bundles only.",
        ], "blue", {}),
        ("§4 · A plane is a havoc issuer, bounded by its charter", [
            "ADR-0025 treats the anchor as a havoc issuer bounded by the rules floor. **A plane gets the same "
            "treatment, bounded by its charter.**",
            "**Whatever a plane signs, a verifier accepts only what every charter on the chain allows.**",
            "A captured plane therefore chooses among leases its parent's quorum already voted acceptable: **it "
            "decides which, never whether.**",
            "⟨R1⟩ **The chain check bounds what each lease may carry, and not how many a captured plane signs** "
            "(§1).",
        ], "red", {"tint": False}),
        ("§5 · Why crash-recovery cannot supply a certificate ⟨Q7⟩", [
            "**Every charter and every lease carries a commit certificate**: signatures from a quorum of the "
            "issuing plane's replicas over the entry's digest and log index.",
            "**A crash-recovery protocol cannot supply that certificate**: one lying replica can obtain a "
            "majority's signatures for two entries at one index, in two ballots.",
            "**A plane whose replicas can be captured declares it, and runs Byzantine agreement** ⟨Q7⟩. An "
            "autonomous plane is always such a plane (ADR-0061).",
            "**A plane that declares its replicas unexposed keeps the corpus's consensus**, and its certificates "
            "are trusted on that declaration.",
        ], "violet", {}),
    ], gap=20)
    y = max(left_bot, ry) + 80

    # ================================================================== band 2: R1 on the budget
    y = band(c, X0, y, "R1: the debit bounds what is allocated, and what is issued only where no plane is captured "
             "(§1, §4, Consequences)", status="proposed", extra="revised R1")
    top = y + 10
    pw_, gx, gw = 470, X0 + 700, 460
    PA = ("Plane a · honest", [
        "**An example: the numbers are illustrative, not the record's.** Seats b under a charter whose `budget` "
        "is 2, and debits 2 from its own (§1).",
        "**Its account survives capture below it**: `left` + `issued` + its children's budgets equals its own "
        "`budget` (`Account`, Federation_proof.tla).",
    ], "violet")
    PB = ("Plane b · captured", [
        "**Its charter's `budget` is 2.**",
        "**It signs three leases**, each within every charter on the chain, **each to a different vehicle**.",
        "**It decides which, never whether** (§4): every lease is one its parent's quorum voted acceptable.",
    ], "red")
    ha = c.card(0, 0, pw_, PA[0], PA[1], draw=False, size=S)
    hb = c.card(0, 0, pw_, PB[0], PB[1], draw=False, size=S)
    c.card(X0, top, pw_, PA[0], PA[1], accent="violet", size=S)
    yb = top + ha + 90
    c.card(X0, yb, pw_, PB[0], PB[1], accent="red", size=S, tint=False, dash="6 4")
    c.arrow([(X0 + pw_ / 2, top + ha), (X0 + pw_ / 2, yb)], "blue", sw=2.4, label="seats b; debits 2",
            lpos=0.5)
    GOV = [("Governor of vehicle 1", ["Sees one lease, within every charter: **permitted**."]),
           ("Governor of vehicle 2", ["Sees one lease, within every charter: **permitted**."]),
           ("Governor of vehicle 3", ["Sees one lease, within every charter: **permitted**. **It is the third on a "
                                      "budget of 2, and no single verifier sees more than its own.**"])]
    hg = [c.card(0, 0, gw, t, b, draw=False, size=S) for t, b in GOV]
    gtot = sum(hg) + 2 * 30
    gy = top + (ha + 90 + hb) / 2 - gtot / 2 + 40
    gy = max(gy, top)
    bmid = yb + hb / 2
    bx = X0 + pw_
    jx = bx + 90
    for (t, b), h in zip(GOV, hg):
        c.card(gx, gy, gw, t, b, accent="teal", size=S, tint=False)
        c.arrow([(bx, bmid), (jx, bmid), (jx, gy + h / 2), (gx, gy + h / 2)], "red", sw=2)
        c.label((jx + gx) / 2 + 4, gy + h / 2, f"lease {t[-1]}", "red", 12.5)
        gy += h + 30
    left_bot = max(gy - 30, yb + hb)
    left_bot += 24
    left_bot += c.para(X0, left_bot, gx + gw - X0, "**What survives capture is the honest parent's account and each "
                       "honest governor's bound** (ADR-0063 §3). Nothing in the chain check can refuse the third "
                       "lease.", 14, "muted")

    xr2 = gx + gw + 70
    wr2 = X1 - xr2
    hrow = row_cards(c, xr2, top, wr2, 24, [
        ("As drafted: \"the root's tally bounds the whole tree\"", [
            "**It fails under capture** (History, R1; Federation.tla's header). The debit bounds what is allocated.",
            "A captured plane can sign more leases than its budget, each to a different vehicle, and no single "
            "verifier sees more than its own, **so nothing in the model can refuse them**.",
        ], "red", {"tint": False}),
        ("As revised ⟨R1⟩ (§1)", [
            "**A child's `budget` is debited from its parent's when it is seated, so the root's tally bounds what is "
            "allocated across the whole tree, and what is issued in any subtree with no captured plane.**",
            "**What survives capture is the honest parent's account and each honest governor's bound** "
            "(ADR-0063 §3).",
        ], "amber", {}),
    ])
    y2 = top + hrow + 24
    hrow2 = row_cards(c, xr2, y2, wr2, 24, [
        ("§4 and the Consequences say the same ⟨R1⟩", [
            "§4: **the chain check bounds what each lease may carry, and not how many a captured plane signs.**",
            "Positive: **what a captured plane's lease may carry is bounded by its charter**, and the bound is "
            "checked by whoever receives the lease. **How many it signs is not.**",
        ], "amber", {}),
        ("`BudgetConserved`, stated for an honest subtree", [
            "`\\A p \\in Planes : (Below(p) \\cap Captured = {}) => TreeIssued(p) <= charter[p].budget`",
            "**Leases issued under a charter and under every charter below it never exceed its budget, for a "
            "subtree with no captured plane.** That it is stated so is a finding (the module's header).",
            "**Checked** in every budget row with `Captured={}`, and broken by `M_NODEBIT` alone. **Proved** as "
            "`BudgetConservedAlways`, resting on `Account`.",
        ], "teal", {}),
    ])
    y = max(left_bot, y2 + hrow2) + 80

    # ================================================================== band 3: §2, §4–§8
    y = band(c, X0, y, "Any plane fences everything below it, the trusted base, and the overlay (ADR-0059 §6–§8)",
             status="proposed")
    h = row_cards(c, X0, y, WW, 30, [
        ("§6 · Any plane on the chain fences everything below it ⟨9⟩", [
            "**A charter and a lease carry the epoch and log index of each plane on the chain**, not only the "
            "granting plane's. An admit or a permit compares each against the latest its verifier has heard.",
            "**A plane that moves its epoch fences everything below it.** That act is a **plane fence**: a "
            "subtraction, ordered, needing no quorum (ToO §4.1).",
            "**A fence travels as far as the link does.** What bounds a plane the fence cannot reach is ADR-0063.",
        ], "green", {}),
        ("§7 · The trusted base", [
            "**Each plane's replicas are a row of the kind T-0045-1, per plane.**",
            "**Where §5 applies, Byzantine agreement replaces that row, and a forged certificate is its failure.** "
            "ADR-0068 carries the rows.",
            "Negative: **a deeper trusted base**, a replica row per plane, and a chain every verifier must walk.",
        ], "grey", {"tint": False}),
        ("§8 · An overlay, and what is reported upstream ⟨Q11⟩", [
            "ADR-0023 §4: a variation that holds a capability the archetype lacks is not a rung. **So this is an "
            "overlay's record**, and reports under ADR-0058 §6: **a mechanism that grants below itself**, bounded by "
            "a charter; **commit certificates** a third party can check with no plane in reach; **a fence that "
            "names every plane on a chain.**",
            "**If the archetype takes them, its records owe**: ADR-0054's sentence on delegation and ToO §2.11, "
            "restated; ADR-0024 A3; ADR-0031, the lease's fence one per plane; **ADR-0045's decision not to require "
            "Byzantine agreement, reversed for exposed planes, which is C3.** A one-plane deployment would then be a "
            "declared degeneracy.",
        ], "amber", {"tint": False}),
    ])
    y += h + 18
    y += c.para(X0, y, WW, "**Negative (Consequences): delegation.** It attenuates, it is a mechanism's and it is "
                "budgeted, and it is still delegation. Byzantine agreement is required wherever replicas are exposed, "
                "which the corpus had declined to require.", 14, "muted")
    y += 80

    # ================================================================== band 4: ADR-0061
    y = band(c, X0, y, "An autonomous plane: seven replicas, and a membership that shrinks only along a voted schedule "
             "(ADR-0061)", status="proposed", extra="C1 · revised R1")
    top = y
    wl = 1660
    xr3 = X0 + wl + 50
    wr3 = X1 - xr3
    ty = top + sub(c, X0, top, "**§1's table, whole: seven replicas, tolerating two captured** ⟨20⟩")
    cols = [("Replicas", 150, {"bold": True}), ("Captured tolerated (f)", 240), ("Certificate", 200),
            ("Silent tolerated", 220)]
    cols.append(("Captured or slow tolerated, for the duration bound (ADR-0064)", wl - sum(cl[1] for cl in cols)))
    t = c.table(X0, ty, cols, [
        {"cells": ["7", "2", "5", "2", "4"], "accent": "violet"},
        ["6", "1", "4", "2", "3"],
        ["5", "1", "4", "1", "3"],
        ["4", "1", "3", "1", "2"],
    ], size=14.5, accent="violet")
    ty += t + 14
    ty += c.para(X0, ty, wl, "**A certificate for n replicas tolerating f captured is the least whole number above "
                 "(n + f) / 2, so that any two certificates share an honest signer.** **Why seven and not four**: four "
                 "replicas tolerate one capture or one loss, and have no smaller membership to fall back to that "
                 "tolerates any capture. Seven tolerate two of either at once, and have three steps of the schedule "
                 "above a floor of one. **The number is a placeholder**, as every number in the corpus is until "
                 "something is measured.", 14, "muted")
    rb = stack(c, xr3, top, wr3, [
        ("§2 · The instrument is PBFT at the reference, on two conditions ⟨20⟩", [
            "The letters name roles, not products (ToO §1). What the pattern asks of P at an exposed plane is "
            "**Byzantine agreement whose certificates a third party can check** (ADR-0059 §5). PBFT (Castro and "
            "Liskov, 1999) gives agreement at n = 3f + 1 with certificates of 2f + 1 [[red|(recalled, not re-read)]].",
            "**1. Its messages must be signed.** A governor verifies a certificate with no plane in reach. A later "
            "form of PBFT replaced signatures with message authentication codes, which convince only the replica "
            "they were made for [[red|(recalled)]]. That form cannot supply a commit certificate.",
            "**2. It needs a reconfiguration step.** PBFT as published has a fixed membership [[red|(recalled)]]. §3 "
            "adds a step that changes it, and **that step is where an error would be an error about authority.**",
            "**Three things fit as they are**: ADR-0064's rules are conditions on a replica's vote; the view change "
            "runs on timeouts, which is liveness; a Byzantine primary chooses the order and can stall, and cannot "
            "forge, so **it decides which and never whether**.",
        ], "violet", {}),
    ])
    y = max(ty, rb) + 50

    # ---- the schedule
    y += sub(c, X0, y, "**§3: the membership shrinks along a schedule voted in the charter** ⟨19⟩, here §4's "
             "archetype: **7, 6, 5, 4, with a capture floor of one** ⟨Q18⟩")
    sy = y + 40
    bw = 420
    sgap = (WW - 24 - 5 * bw) / 4
    MEM = [("7 replicas", ["f = 2 · certificate 5", "**As seated.** Tolerates two captured, or two silent."], "violet"),
           ("6 replicas", ["f = 1 · certificate 4", "Silent tolerated: 2."], "violet"),
           ("5 replicas", ["f = 1 · certificate 4", "Silent tolerated: 1."], "violet"),
           ("4 replicas", ["f = 1 · certificate 3", "**The schedule's last size**: the last that tolerates one "
                           "capture."], "violet"),
           ("3 replicas", ["f = 0 by §1's rule: **below the capture floor of one**, and not in the schedule. "
                           "**No step takes the plane below the floor** (`FD13`, `FD4`)."], "red")]
    hm = max(c.card(0, 0, bw, t, b, draw=False, size=S) for t, b, _ in MEM)
    c.region(X0, sy - 30, 4 * bw + 3 * sgap + 48, hm + 60, "The charter's `membership`: the schedule, at or "
             "above its capture floor", "violet", dash="10 6")
    for i, (t, b, acc) in enumerate(MEM):
        xx = X0 + 24 + i * (bw + sgap)
        c.card(xx, sy, bw, t, b, accent=acc, size=S, h=hm, tint=acc != "red", dash="2 3" if acc == "red" else None)
        if i < 4:
            mid = sy + hm / 2
            if i < 3:
                c.arrow([(xx + bw, mid), (xx + bw + sgap, mid)], "violet", sw=2.4,
                        label="a step: drop one, ordered by a certificate of the membership it replaces",
                        lpos=0.5, lw=sgap - 40)
            else:
                c.arrow([(xx + bw + 20, mid), (xx + bw + sgap, mid)], "red", dash="7 5", sw=2.4,
                        label="[[red|refused]]: below the floor", lpos=0.45, lw=sgap - 60)
    y = sy + hm + 60
    h = row_cards(c, X0, y, WW, 30, [
        ("§3's rules on a step", [
            "**A step drops one replica.** Any replica may propose to drop one it has not heard for a declared "
            "number of ticks (ADR-0064). A replica signs the proposal only if it has not heard that replica either.",
            "**The membership being replaced orders the step, by its own certificate.** So a membership has at "
            "most one successor, and **a minority cut off by a partition cannot make itself a plane.**",
            "**A dropped replica does not return below the intent boundary.** Adding a replica brings an issuer into "
            "force, which is a promotion (ADR-0059 §3). Its vehicle may still hold a lease if it hears the plane "
            "again (drafter's choice).",
            "**No step takes the plane below the floor, and no other change of membership is allowed** (`FD13`, "
            "`FD4`).",
        ], "violet", {}),
        ("⟨R1⟩ One vote per membership, and the split vote that stalls", [
            "**An honest replica signs at most one step of a membership.** The first rule does not give this: a "
            "replica that has heard neither of two others could sign both drops, and two successors follow "
            "(`M_TWOVOTES`).",
            "**§2's agreement gives it**: one entry at one log index, with a step that names the membership it "
            "replaces.",
            "**Read as one vote per membership with no second ballot, a vote that splits stalls the schedule for "
            "good: safe, and not live.** The plane keeps its size, and a further loss may end it (Negative).",
            "Open: **whether a split vote may be retried.** `Membership.tla` has no ballot and no view change, so a "
            "retry that keeps `AtMostOneSuccessor` is neither designed nor checked.",
        ], "amber", {}),
        ("Negative: it strains a mechanism constant, \"a timeout is never a grant\" (ADR-0024)", [
            "**A step adds nothing to the charter**: no entry, no budget, no longer life. **But silence is what "
            "triggers it, and what it preserves is a plane's ability to grant.**",
            "The record accepts that **because the schedule and the floor were voted, because the step is ordered "
            "by a quorum and not taken by default**, and because the alternative is that one loss beyond what the "
            "plane tolerates leaves no certificate ever again (Context; the NATO reading's N3).",
            "**If the archetype takes it, ADR-0024 owes a statement of how §3 stands beside the constant**, and "
            "ADR-0045 the replica row with the reconfiguration step, which is C3 (§6).",
        ], "red", {"tint": False}),
    ])
    y += h + 40

    # ---- §4
    top = y
    wt = 1180
    ty = top + sub(c, X0, top, "**§4's table, whole** ⟨Q18⟩")
    cols = [("", 420, {"bold": True}), ("Fixed at 7", 330), ("Schedule 7, 6, 5, 4", wt - 750)]
    t = c.table(X0, ty, cols, [
        ["Losses survived, one at a time", "2", "[[green|4]]"],
        ["Losses survived at once", "2", "2"],
        ["Captures tolerated before any loss", "2", "2"],
        ["Captures tolerated after one loss", "2", "[[red|1]]"],
    ], size=14.5, accent="violet")
    ty += t
    xr4 = X0 + wt + 40
    wr4 = X1 - xr4
    h = row_cards(c, xr4, top, wr4, 24, [
        ("At this schedule the floor adds nothing ⟨R1⟩", [
            "**The schedule is 7, 6, 5, 4 and the capture floor is one.** Four is the last size that tolerates one "
            "capture, so the floor adds nothing the schedule does not.",
            "**The floor binds a charter whose schedule runs past it.** In the model, `m-below-archetype` holds.",
        ], "violet", {}),
        ("A smaller membership may carry a smaller budget ⟨Q17⟩", [
            "**A charter may give each membership its own budget.** Where the tally states one, a step narrows what "
            "the plane holds as well as lowering what it takes to capture it. Where it states none, the budget is "
            "unchanged.",
        ], "green", {}),
        ("What a step spends", [
            "**The quorum dial of the lattice analysis**: capture is how many captured holders it takes to grant; "
            "loss is how many silent holders still let a grant happen.",
            "At an autonomous plane the replicas are exposed and nobody else grants, so the pair applies to them. "
            "**A step spends the first to restore the second.**",
        ], "violet", {"tint": False}),
        ("§5 · D-0061-1: a plane of four", [
            "**It keeps agreement and tolerates one capture. It has no schedule, and one loss beyond the first ends "
            "it.**",
        ], "grey", {"tint": False}),
    ])
    y = max(ty, top + h) + 24
    y += c.para(X0, y, WW, "**Other Negatives.** Against an adversary that can silence vehicles, **the tolerance is "
                "the floor's from the start**: jamming honest vehicles until their replicas are dropped walks the plane "
                "down its schedule, and two captured replicas then capture a plane that tolerated two when it was "
                "seated. **A reconfiguration step no published PBFT has**, in the trusted base. **Cost unmeasured**: "
                "PBFT's messages grow with the square of the membership. **One author, one day, and an instrument "
                "described from memory.** Positive: a plane outlives its first losses, four one at a time where a "
                "fixed seven survives two, and a partition still leaves at most one plane.", 14, "muted")
    y += 80

    # ================================================================== band 5: the modules
    y = band(c, X0, y, "The two modules: what is checked, what is proved, and what is abstracted (ADR-0059 §9, "
             "ADR-0061 §7)")
    g = 60
    wm = (WW - g) / 2
    xa, xb = X0, X0 + wm + g

    def module_col(x, specs):
        yy = y
        for kind, payload in specs:
            if kind == "card":
                t_, b_, acc, k = payload
                yy += c.card(x, yy, wm, t_, b_, accent=acc, size=S, **k) + 20
            elif kind == "sub":
                yy += sub(c, x, yy, payload)
            elif kind == "table":
                cols_, rows_, acc = payload
                yy += c.table(x, yy, cols_, rows_, size=13.5, accent=acc) + 22
        return yy

    fprops = [("Property", 0.27, {"bold": False}), ("What it says (the module's header)", 0.73)]
    fprop_rows = [
        ["`CharterNarrows`", "A charter seated by an honest parent is the parent's or narrower, field by field (§1)"],
        ["`LeaseWithinChain`", "Every lease a verifier accepts is within every charter on its chain (§4, §5)"],
        ["`HavocPlaneBounded`", "Whatever the captured planes sign, no verifier permits an entry the root's tally "
         "did not vote (§4)"],
        ["`BudgetConserved`", "Leases issued under a charter and under every charter below it never exceed its "
         "budget, **for a subtree with no captured plane** (§1)"],
        ["`AnyPlaneFences`", "No verifier that has heard an epoch permits under a chain that carries an older epoch "
         "of that plane (§6)"],
    ]
    fm_w = [0.17, 0.28] + [0.11] * 5
    fm_cols = [("Mutation", fm_w[0]), ("What it does", fm_w[1]), ("`CharterNarrows`", fm_w[2]),
               ("`LeaseWithinChain`", fm_w[3]), ("`HavocPlaneBounded`", fm_w[4]), ("`BudgetConserved`", fm_w[5]),
               ("`AnyPlaneFences`", fm_w[6])]
    fm_rows = [
        ["`M_WIDEN`", "A seating by an honest parent may widen the alphabet", BR, HO, HO, HO, HO],
        ["`M_LASTLINK`", "A verifier checks only the granting plane's charter", HO, BR, BR, HO, HO],
        ["`M_TRUSTPLANE`", "A verifier takes a captured plane's word for its own chain and checks no charter", HO, BR,
         BR, HO, HO],
        ["`M_NODEBIT`", "A child's budget is not debited from its parent's", HO, HO, HO, BR, HO],
        ["`M_STALEEPOCH`", "A check compares only the granting plane's epoch", HO, HO, HO, HO, BR],
    ]
    fw_rows = [
        ["`w-permit`", "a verifier permits a lease"],
        ["`w-deep`", "a lease granted by b, at the end of the chain, is permitted"],
        ["`w-afterfence`", "a verifier that has heard r's epoch move still permits a current lease"],
        ["`w-refchain`", "a lease outside a charter on the chain is refused"],
        ["`w-reffence`", "a lease carrying an older epoch is refused"],
        ["`w-havocwide`", "a captured parent seats a child with a wider charter"],
        ["`w-debited`", "a's budget is debited from r's"],
        ["`w-spent`", "an honest plane spends its budget to zero"],
    ]

    def cols_of(spec):
        return [(t_, wm * f, *(rest)) for t_, f, *rest in spec]

    bot_a = module_col(xa, [
        ("card", ("`spec/Federation.tla` · ADR-0059 §9's module", [
            "**Checked**: 41 rows from `spec/Federation-rows.txt`, **all as expected** (TLC, at `MaxEpoch` 0 or 1, "
            "`RootBudget` 0 to 2, `Captured` one of {}, {a}, {b}, {a, b}, one or two verifiers).",
            "**Proved**: 892 obligations, by tlapm 7824dab: `CharterNarrowsAlways`, `LeaseWithinChainAlways`, "
            "`HavocPlaneBoundedAlways`, `BudgetConservedAlways`, `AnyPlaneFencesAlways`, `SafeAlways`.",
            "**Certified, with 7 LS4 temporal steps that no checker confirms**: 602 closed by tlapm with no backend, "
            "283 by SMT proofs ethos accepted.",
        ], "teal", {})),
        ("sub", "**Five properties**, `Safe` their conjunction"),
        ("table", (cols_of(fprops), fprop_rows, "teal")),
        ("sub", "**Five mutations, and what each breaks** (every cell a row, checked)"),
        ("table", (cols_of(fm_cols), fm_rows, "red")),
        ("card", ("Two mutations break two properties each", [
            "**`M_LASTLINK` and `M_TRUSTPLANE` each break `LeaseWithinChain` and `HavocPlaneBounded`**: under "
            "capture, a lease outside the chain is, or can be, outside what the root voted. Proposal §10 asked for "
            "one property each. With no plane captured, both hold `LeaseWithinChain` (`m-last-honest`, "
            "`m-trust-honest`).",
        ], "red", {"tint": False})),
        ("sub", "**Eight witnesses**, each violated, so each constrained behaviour is reachable"),
        ("table", (cols_of([("Row", 0.22), ("Reachable", 0.78)]), fw_rows, "green")),
        ("card", ("What it abstracts (its header)", [
            "**A chain of three planes**, r → a → b, with r the root. A sibling would only be a second debit against "
            "the same `left`.",
            "**Four of §1's fields**: `seated`, `alphabet`, `budget` and `fence`. `labels`, `bundles`, `ttlMax`, "
            "`countMax` and `expiry` have the shape of the first two.",
            "**A commit certificate is taken as unforgeable.** A presented lease is any entry and epoch, under any "
            "plane, so a property that holds rests on the verifier's checks alone. Verifiers are honest.",
            "**The root's tally is honest.** A plane is not re-seated. Membership is `Membership.tla`'s. Deadlock is "
            "not checked: a chain that is seated and spent is safe.",
        ], "grey", {"tint": False})),
    ])

    mprop_rows = [
        ["`StepInSchedule`", "Every step is to a size the charter's schedule names"],
        ["`StepAtFloor`", "Every step leaves at least the capture floor tolerated"],
        ["`StepByQuorum`", "Every step is signed by a certificate of the membership it replaces"],
        ["`AtMostOneSuccessor`", "No membership has two successors: quorum intersection, resting on the floor and "
         "on the one-vote rule"],
        ["`OneSuccessor`", "The four together: **ADR-0061 §7's property**, and `Safe`"],
    ]
    mm_w = [0.17, 0.27, 0.13, 0.13, 0.13, 0.17]
    mm_cols = [("Mutation", mm_w[0]), ("What it does", mm_w[1]), ("`StepInSchedule`", mm_w[2]),
               ("`StepAtFloor`", mm_w[3]), ("`StepByQuorum`", mm_w[4]), ("`AtMostOneSuccessor`", mm_w[5])]
    mm_rows = [
        ["`M_MINORITYSTEP` (§7)", "A step is ordered by one signer fewer than a certificate", HO, HO, BR, BR],
        ["`M_BELOWFLOOR` (§7)", "A step may go below the capture floor. **At the archetype schedule {5, 4}, `Safe` "
         "holds** (`m-below-archetype`)", f"{HO} at {{5,4,3}}", f"{BR} at {{5,4,3}}", f"{HO} at {{5,4,3}}",
         f"{HO} at {{5,4,3}}; {BR} at {{5,4,3,2}}"],
        ["`M_OFFSCHEDULE` (added)", "A step need not be in the schedule. At {5, 4}, `Safe` holds", f"{BR} at {{5}}",
         f"{HO} at {{5}}", f"{HO} at {{5}}", f"{HO} at {{5}}"],
        ["`M_TWOVOTES` (added)", "An honest replica may sign several steps of one membership: §3's signing rule with "
         "no agreement behind it", HO, HO, HO, f"{BR} (`MaxBallots`=6)"],
    ]
    mw_rows = [
        ["`w-stepped`", "a step is ordered"],
        ["`w-atfour`", "the plane reaches four replicas"],
        ["`w-splitvote`", "honest votes of one membership split between two drops"],
        ["`w-capturedsigner`", "a certificate that orders a step includes a captured replica"],
    ]
    bot_b = module_col(xb, [
        ("card", ("`spec/Membership.tla` · ADR-0061 §7's module", [
            "**Checked**: 28 rows from `spec/Membership-rows.txt`, **all as expected** (TLC, five replicas, `Floor` "
            "0 or 1, `Captured` {} or {r1}, the schedule {5}, {5, 4}, {5, 4, 3} or {5, 4, 3, 2}).",
            "**Proved**: 495 obligations, by tlapm 7824dab: `StepInScheduleAlways`, `StepAtFloorAlways`, "
            "`StepByQuorumAlways`, `AtMostOneSuccessorAlways`, `SafeAlways`.",
            "**Certified, with 6 LS4 temporal steps that no checker confirms**: 306 closed by tlapm with no backend, "
            "182 by SMT proofs ethos accepted, 1 by Zenon checked by Isabelle.",
            "**At five replicas, and not at §1's seven** ⟨R1⟩. {5, 4} is §4's schedule cut to five: it ends where f "
            "is still one.",
        ], "teal", {})),
        ("sub", "**Four properties**, and `OneSuccessor` their conjunction"),
        ("table", (cols_of(fprops[:1] + [("What it says (the module's header)", 0.73)]), mprop_rows, "teal")),
        ("sub", "**Four mutations, and what each breaks** (at the schedule each row names)"),
        ("table", (cols_of(mm_cols), mm_rows, "red")),
        ("card", ("Two findings, both taken into the record by R1", [
            "**The one-vote rule was not in §3.** `M_TWOVOTES` shows two successors follow without it. The module "
            "takes it as the honest replica's rule; §3 now says so.",
            "**At the archetype the floor is redundant with the schedule**: `m-below-archetype` holds. "
            "`M_BELOWFLOOR`'s breaking rows run with a schedule that passes the floor. §4 now says so.",
        ], "amber", {})),
        ("sub", "**Four witnesses**, each violated, so each constrained behaviour is reachable"),
        ("table", (cols_of([("Row", 0.22), ("Reachable", 0.78)]), mw_rows, "green")),
        ("card", ("What it abstracts (its header)", [
            "**Five replicas, one plane.** §1's seven is not modelled.",
            "**PBFT is abstracted to its certificate**: no primary, no view change, no message delivery, **no "
            "ballot**. §7's \"PBFT is read\" is not met by this module, nor the measurement.",
            "**\"Not heard\" is not modelled**: an honest replica may sign any drop but its own, which is more than "
            "§3 allows. A step's ticks (ADR-0064) and a smaller membership's budget (§4) are not modelled.",
            "**A step only removes**: no action adds a replica, since that is a promotion. Deadlock is not checked: "
            "a plane at its floor with every vote cast is safe.",
        ], "grey", {"tint": False})),
    ])
    y = max(bot_a, bot_b) + 60

    # ================================================================== band 6: ratification and options
    y = band(c, X0, y, "Ratification conditions, item by item, and the options considered, whole")
    top = y
    g = 60
    wh = (WW - g) / 2
    xa, xb = X0, X0 + wh + g
    MET = "[[green|Met for TLC and TLAPS]]"
    NOT = "[[red|Not met]]"
    rcols = [("Condition", wh * 0.5), ("State", wh * 0.17), ("From the record", wh * 0.33)]
    ya_ = top + sub(c, xa, top, "**ADR-0059 §9**")
    ya_ += c.table(xa, ya_, rcols, [
        ["**ADR-0058 is ratified**, or the custodian takes this record into the archetype by the route §8 names",
         NOT, "ADR-0058 is Proposed (2026.11.06)"],
        ["**A module states the properties and its mutations break them** (ADR-0046's method): `CharterNarrows`, "
         "`LeaseWithinChain`, `HavocPlaneBounded`, `BudgetConserved`, `AnyPlaneFences`; `M_WIDEN`, `M_LASTLINK`, "
         "`M_TRUSTPLANE`, `M_NODEBIT`, `M_STALEEPOCH`; a witness for each constrained behaviour", MET + " ⟨R1⟩",
         "`spec/Federation.tla`: 41 rows, 892 obligations. `BudgetConserved` is stated for an honest subtree"],
        ["**The floor's `federation` stage carries `FD1` to `FD3`** (ADR-0067)", NOT,
         "Not written: no `federation` stage in `floor/proposed/`. ADR-0067 is Proposed"],
        ["**The reference** shows a charter seated, a widening refused, and a lease refused by a verifier that "
         "checks the whole chain", NOT, "\"Nothing is built\""],
        ["**A reader who is not the drafter** (ADR-0029 A2)", NOT, "One author, one day"],
    ], size=14, accent="blue") + 40
    yb_ = top + sub(c, xb, top, "**ADR-0061 §7**")
    yb_ += c.table(xb, yb_, rcols, [
        ["**ADR-0059 and ADR-0060 are ratified first**, or with this record", NOT, "Both Proposed (2026.11.10)"],
        ["**A module** states at least `OneSuccessor`: every step in the charter's schedule, at or above its floor, "
         "and ordered by a quorum of the membership it replaces. Mutations `M_MINORITYSTEP` and `M_BELOWFLOOR`",
         MET + ", at five replicas, not at seven ⟨R1⟩", "`spec/Membership.tla`: 28 rows, 495 obligations. "
         "`M_OFFSCHEDULE` and `M_TWOVOTES` added. `m-below-archetype` holds"],
        ["**PBFT is read**, and the three recalled statements in §2 are sourced or corrected", NOT,
         "The record's own words: \"PBFT is not read\""],
        ["**A measurement** of a round among seven over the radios a deployment would use", NOT,
         "The only figure is a simulated 412.3 ms for a round among 20, quoted by the swarm reading as an order of "
         "magnitude"],
        ["**The reference** shows a step ordered, a step by a minority refused, and a step below the floor refused",
         NOT, "\"Not met\""],
        ["**A reader who is not the drafter** (ADR-0029 A2)", NOT, "One author, one day"],
    ], size=14, accent="blue") + 40
    y = max(ya_, yb_)
    ocols = [("Option", wh * 0.36, {"bold": True}), ("Disposition", wh * 0.64)]
    ya_ = y + sub(c, xa, y, "**ADR-0059's Options considered, whole**")
    ya_ += c.table(xa, ya_, ocols, [
        {"cells": ["One plane, larger", "The corpus as it stands. It cannot hand authority to a group that loses its "
                   "link"], "accent": "grey"},
        {"cells": ["Principals that delegate, an agent granting an agent", "[[red|Rejected]], as ToO §2.11 rejects it. "
                   "The grantor here is a mechanism"], "accent": "red"},
        {"cells": ["Every narrowing is a promotion", "[[grey|Not taken]] ⟨Q1⟩. A command chain could no longer decide "
                   "by one commander between votes"], "accent": "grey"},
        {"cells": ["A floor per plane", "[[grey|Not taken]] ⟨Q8⟩. Each would be a verified object of its own, and "
                   "narrowing between floors needs a cross-floor check"], "accent": "grey"},
        {"cells": ["Trust a plane for its own charter", "[[red|Rejected]]. `M_TRUSTPLANE`. A captured plane would name "
                   "its own bounds"], "accent": "red"},
        {"cells": ["Crash-fault consensus with certificates", "[[red|Rejected]] for an exposed plane (§5)"],
         "accent": "red"},
        {"cells": ["Byzantine agreement at every plane", "[[grey|Not taken]] ⟨Q7⟩. It is declared where replicas are "
                   "exposed"], "accent": "grey"},
        {"cells": ["Extend the archetype now", "[[grey|Not taken]] ⟨Q11⟩. A deployment that never loses its link would "
                   "pay for what it does not use"], "accent": "grey"},
    ], size=14, accent="grey")
    yb_ = y + sub(c, xb, y, "**ADR-0061's Options considered, whole**")
    yb_ += c.table(xb, yb_, ocols, [
        {"cells": ["Four replicas", "A declared degeneracy (§5). No room to shrink"], "accent": "grey"},
        {"cells": ["A fixed membership of seven", "[[grey|Not taken]] ⟨19⟩. It survives two losses and then ends, in "
                   "the deployment where losses are ordinary"], "accent": "grey"},
        {"cells": ["A capture floor of two", "[[grey|Not taken at the archetype]] ⟨Q18⟩. A plane of seven then has no "
                   "schedule; one needs ten or more. A deployment that faces an adversary who can silence vehicles "
                   "takes it"], "accent": "grey"},
        {"cells": ["A budget that always shrinks with the membership, by a fixed rule", "[[grey|Not taken]] ⟨Q17⟩. The "
                   "tally states one where it can"], "accent": "grey"},
        {"cells": ["A smaller membership adopted by the survivors on a timeout", "[[red|Rejected]]. Loss and partition "
                   "look the same from inside, and two groups could each admit"], "accent": "red"},
        {"cells": ["Replicas re-admitted in the field", "[[red|Rejected]]. It adds an issuer, which is a promotion"],
         "accent": "red"},
        {"cells": ["Message authentication codes in place of signatures", "[[red|Rejected]] (§2)"], "accent": "red"},
    ], size=14, accent="grey")
    y = max(ya_, yb_) + 30
    y += c.para(X0, y, WW, "**Open obligations.** ADR-0059: the floor stage and the reference; the custodian's reading "
                "of every drafter's choice; the findings of the two readings this set does not answer (F3, F4, N1, N2, "
                "Z2, Z3 and the rest of Z4; F4 bears on §1: the charter has no field for an envelope in the world); "
                "ToO and the glossary owe \"plane\", \"charter\", \"chain\", \"commit certificate\" and \"plane fence\" if the "
                "archetype takes this. ADR-0061: the reading of PBFT, the measurement and the reference; whether a "
                "split vote may be retried; where an autonomous plane's orchestrator runs (if on one vehicle, its loss "
                "stalls every decision point: N3); the number of silent ticks before a replica may be dropped; whether "
                "a dropped replica's vehicle may hold a lease.", 14, "muted")
    return c
