"""B3 — Floor-change routing, the proof-carrying gate, and the 2026.10.01 gate run."""
from lib import Canvas

ID, SLUG = "B3", "floor-change-routing"

HOLDS_C = "[[teal|holds°]]"
HOLDS_K = "[[blue|holds✓]]"


def build():
    c = Canvas(ID, "Changing the floor: the route is computed, every solver `holds` carries a checked proof, and "
               "the floor in force was built in three gated stages",
               "A candidate floor F′ is compared with the deployed floor F in both directions; the answer, not the "
               "author, picks the authority path. A Build author is Byzantine by premise and cannot relabel a "
               "relaxation as a tightening; a wrong solver could, until ADR-0030 A1 made the solver trusted for "
               "nothing. The same gate run checks the three floor gates. The floor in force is the proposed floor's "
               "`emergency` stage, built from the genesis draft through `labels` and `control`, each stage gated; it "
               "is **genesis-provisional**: gated, pinned and enforced, and ratified only when the bootstrap reviewer "
               "establishes that it is fit (ADR-0030 A3).",
               3200, "ToO rev 14 §2.10, §3.1, §3.2, §3.3, §7.3, §7.9, §7.10, §15; G10 §1 (Batches 28, 34), §2.2, "
               "§2.8, §3, §8, §7 items 2, 25, 57, 87, 91, and items 68, 69 as at G9; G7 §2.8, §3 (results 1–6); "
               "ADR-0007; ADR-0025 §1 (d), (h) with A2; ADR-0026 §4, §5, A2; ADR-0029 §5 with A4; ADR-0030 §4 with A2, "
               "§5 with A1, §8 (D-0030-2), §10, header with A3; ADR-0041 A1, A2, A3, R2; ADR-0047 R16; ADR-0049 §6; "
               "ADR-0050 §4, R8; ADR-0052 §2, §9 (R4); ADR-0045 T-0045-3, T-0045-14; floor/README.md; "
               "floor/proposed/README.md; floor/proposed/labels-, control- and "
               "emergency-gates-results-2026.10.04.txt; floor/genesis-gates-results-2026.10.01.txt; ADR-0053 (Proposed) §2, "
               "§5, R3; floor/lean/README.md and floor/lean/TopakFloor-results-2026.10.06.txt")
    X0, X1 = c.x0, c.x1
    y = c.y
    y += c.legend(X0, y, [
        ("box", "blue", "ordinary promotion; checked proof"), ("box", "brown", "anchor issuance needed"),
        ("box", "teal", "verified object; cedar"), ("box", "red", "refused, failure, residual"),
        ("box", "violet", "draft"), ("arrow", "blue", "decision flow"),
        ("arrow", "red", "fails closed", "7 5"),
    ], title="Read as") + 34

    LW = 1880
    RX = X0 + LW + 80
    RW = X1 - RX

    # ================================================================ left: the decision flow
    c.text(X0, y + 22, "The routing decision (ToO §3.2; ADR-0030 §5)", 22, "ink", bold=True)
    fy = y + 46
    cw = 560
    h1 = c.card(X0, fy, cw, "Deployed floor F", [
        "In the mechanism release, resident. At the reference since 2026.10.05: the `emergency` stage, "
        "`15c941b9a56a09f7`, 28 policies, built from the genesis draft `28ec0e4552c6a915`.",
    ], accent="teal", size=14.5, status="genprov")
    c.card(X0 + LW - cw, fy, cw, "Candidate floor F′", [
        "A Build artifact, authored by a principal who is **Byzantine by premise** (ToO §1).",
    ], accent="violet", size=14.5, h=h1)
    qx = X0 + LW / 2 - 330
    qy = fy + h1 + 40
    qh = c.card(qx, qy, 660, "Does it change the rules floor?", [
        "The rules floor bounds issuances, not admits, and stays mechanism-checked (ADR-0030 §7).",
    ], accent="grey", size=14.5)
    c.arrow([(X0 + cw / 2, fy + h1), (X0 + cw / 2, qy + 40), (qx, qy + 40)], "blue", sw=2.4)
    c.arrow([(X0 + LW - cw / 2, fy + h1), (X0 + LW - cw / 2, qy + 40), (qx + 660, qy + 40)], "blue", sw=2.4)
    # yes branch: rules floor
    rfx = X0 + LW - 520
    rfy = qy + qh + 60
    rfh = c.card(rfx, rfy, 520, "Rules floor: two keys, both directions", [
        "Any change, tighter or looser: **an anchor issuance and a promotion** under the rules being replaced "
        "(ADR-0026 §4).",
        "Tightening needs both too: a tighter rules floor constrains the anchor, which must consent.",
    ], accent="brown", size=14.5)
    c.arrow([(qx + 580, qy + qh), (qx + 580, qy + qh + 28), (rfx + 260, qy + qh + 28), (rfx + 260, rfy)],
            "brown", sw=2.4, label="yes", lpos=0.45)
    # no branch: the analyzer
    ay = qy + qh + 60
    ax = X0
    aw = rfx - 60 - X0
    ah = c.card(ax, ay, aw, "Policy floor: the analyzer decides `F′ ⇒ F` and `F ⇒ F′`", [
        "`cedar symcc`, Cedar's symbolic compiler, encodes both floors over **schema S** into SMT queries; the "
        "encoding is sound by proof (ADR-0030 §3). A `holds` is an UNSAT from the solver, so it passes the "
        "**proof-carrying gate** (right) before it counts.",
        "The analysis results join the **gate-evidence digest** that every promotion vote binds to (ADR-0024 §3).",
    ], accent="teal", size=14.5)
    c.arrow([(qx + 200, qy + qh), (qx + 200, ay)], "blue", sw=2.4, label="no: policy floor", lpos=0.5)
    # the 2x2 outcome grid
    gy = ay + ah + 60
    lab_w = 190
    routew = 470
    cellw = (aw - lab_w - routew - 70) / 2
    rx_ = ax + lab_w + 2 * cellw + 70
    routes = [("Ordinary promotion (ADR-0024)", "blue", [
        "Every counted grant seat grants; votes bind to (artifact, gate evidence, rules epoch).",
        "Tightening the **policy** floor is not a rules change (ADR-0025 §1).",
    ]), ("Anchor issuance and promotion (ADR-0025 §1 (d))", "brown", [
        "Relaxing the policy floor, or adding an exception, is a rules change. Incomparable goes the expensive way "
        "**by default**.",
    ])]
    chh = max(c.card(0, 0, routew, t, b, size=14.5, draw=False) for t, a_, b in routes)
    c.text(ax + lab_w + cellw / 2, gy - 12, "`F ⇒ F′` holds", 16, "ink", bold=True, anchor="middle")
    c.text(ax + lab_w + cellw * 1.5, gy - 12, "`F ⇒ F′` fails", 16, "ink", bold=True, anchor="middle")
    c.text(rx_ + routew / 2, gy - 12, "Authority path", 16, "ink", bold=True, anchor="middle")
    cells = [
        [("Equivalent", "both implications hold", "blue"), ("Tightening", "F′ admits less than F", "blue")],
        [("Relaxation", "F′ admits more than F", "brown"),
         ("Incomparable: **routed as a relaxation**", "neither contains the other", "brown")],
    ]
    rowlab = ["`F′ ⇒ F` holds", "`F′ ⇒ F` fails"]
    for r in range(2):
        yy = gy + r * (chh + 14)
        c.para(ax, yy + chh / 2 - 22, lab_w - 16, rowlab[r], 16, "ink", bold=True)
        for k in range(2):
            t, d, acc = cells[r][k]
            c.card(ax + lab_w + k * (cellw + 8), yy, cellw - 8, t, [d], accent=acc, size=14.5, bullets=False, h=chh)
        t, acc, b = routes[r]
        c.card(rx_, yy, routew, t, b, accent=acc, size=14.5, h=chh)
        c.arrow([(ax + lab_w + 2 * cellw + 8, yy + chh / 2), (rx_, yy + chh / 2)], acc, sw=2.6)
    c.arrow([(ax + aw / 2, ay + ah), (ax + aw / 2, gy - 34)], "blue", sw=2.4)
    rh = 0
    ry = gy + 2 * chh + 14
    c.card(rfx, rfy + rfh + 30, 520, "Why compute it", [
        "It removes a reviewer's assertion from the one spot where Build principals choose the authority path for "
        "their own change (ADR-0030 §5).",
        "Every envelope and carve-out stated in the floor is floor text, recusal (B7) included: relaxing one is a "
        "floor relaxation, routed here (ADR-0030 §10 finding 3; ADR-0022 A1).",
    ], accent="grey", size=14.5)
    # ================================================================ the routing tables in full
    ty = ry + 50
    c.text(X0, ty + 22, "The two routing tables, in full", 20, "ink", bold=True)
    ty += 40
    w2 = LW
    h1 = c.table(X0, ty, [("Change (ToO §3.2)", w2 * 0.55), ("Authority", w2 * 0.45)], [
        {"cells": ["Tighten the policy floor", "An ordinary promotion"], "accent": "blue"},
        {"cells": ["Relax the policy floor, or add an exception", "An anchor issuance **and** a promotion"],
         "accent": "brown"},
        {"cells": ["A revision that is neither tighter nor looser", "**Routed as a relaxation**: an anchor issuance "
                   "and a promotion"], "accent": "brown"},
        {"cells": ["Any change to the rules floor", "An anchor issuance **and** a promotion"], "accent": "brown"},
    ], size=15, accent="ink")
    h1 += 24
    h1 += c.table(X0, ty + h1, [("`F′ ⇒ F`", 150), ("`F ⇒ F′`", 150), ("Classification (ADR-0030 §5)", w2 - 300 - 330),
                              ("Authority (ToO §3.2)", 330)], [
        {"cells": ["holds", "holds", "Equivalent", "Ordinary promotion"], "accent": "blue"},
        {"cells": ["holds", "fails", "Tightening", "Ordinary promotion"], "accent": "blue"},
        {"cells": ["fails", "holds", "Relaxation", "Anchor issuance **and** promotion"], "accent": "brown"},
        {"cells": ["fails", "fails", "**Incomparable: routed as a relaxation**", "Anchor issuance **and** promotion"],
         "accent": "brown"},
    ], size=15, accent="ink")
    left_bot = ty + h1


    # ================================================================ right: the proof-carrying gate
    c.text(RX, y + 22, "The proof-carrying gate (ADR-0030 §5 with A1; G7 §2.8)", 22, "ink", bold=True)
    py = y + 46
    steps = [
        ("`cedar symcc`", "teal", "Runs the analysis; reads only the verdict from the solver path it is given, so a "
         "wrapper needs no change to cedar. `cedar-policy-cli` 4.13.0."),
        ("`floor/cvc5-checked`: the wrapper", "blue", "Keeps every query; runs cvc5 with proof production on; "
         "**discards the solver's restatement** of the query; prefixes the proof with declarations derived from the "
         "query's own text; requires every assumption in the proof to be one of the query's assertions verbatim; "
         "refuses a restatement that disagrees. sha256 `dfe159e9c21a549e`."),
        ("cvc5 1.4.0, proofs on", "grey", "The solver: **trusted for nothing**. Proof format: cvc5's Cooperating "
         "Proof Calculus (CPC); Alethe was tried and refused for the queries' set theory. Binary "
         "`a4ce24a176532209`."),
        ("`ethos` 8dc85c4: the pinned checker", "blue", "Checks the proof of `false` against the CPC signature "
         "vendored unchanged from cvc5 1.4.0 (`tools/cpc/`, tree `6d7e8d208d223985`; binary `4eb41c1f1f9fce88`). "
         "Independent in code, **not in authorship**. Trust root T-0045-14."),
    ]
    ys = []
    for t, a, b in steps:
        h = c.card(RX, py, RW, t, [b], accent=a, size=14.5, bullets=False)
        ys.append((py, py + h))
        py += h + 46
    for (a0, a1), (b0, b1) in zip(ys, ys[1:]):
        c.arrow([(RX + RW / 2, a1), (RX + RW / 2, b0)], "blue", sw=2.4)
    vy = py
    vw = (RW - 30) / 2
    vh = c.card(RX, vy, vw, "Accepted: `unsat` forwarded", [
        "→ `holds✓`: the query's declarations and assertions entail false; the query, proof and verdict digests "
        "join the gate evidence.",
    ], accent="blue", size=14.5)
    c.card(RX + vw + 30, vy, vw, "Anything else: `unknown`", [
        "→ cedar reports an **analysis failure**, never a `holds`. Fails closed.",
    ], accent="red", size=14.5, h=vh)
    c.arrow([(RX + RW / 2, ys[-1][1]), (RX + RW / 2, vy - 22), (RX + vw / 2, vy - 22), (RX + vw / 2, vy)], "blue",
            sw=2.4)
    c.arrow([(RX + RW / 2, vy - 22), (RX + vw * 1.5 + 30, vy - 22), (RX + vw * 1.5 + 30, vy)], "red", sw=2.4,
            dash="7 5")
    py = vy + vh + 30
    notes = [
        ("A `refuted` needs no certificate", "blue", [
            "It routes a change to more consent or fails a gate, so a wrong one can only subtract (ADR-0030 §5).",
        ], None, ""),
        ("`holds°`: what the checker does not reach", "amber", [
            "cedar decides some analyses with **no solver query at all**, by folding the authorizer term: every "
            "never-errors check on the floor, and a permit-all under always-allows. They rest on the Cedar "
            "engine's row, **T-0045-3**, not on a proof: 25 of 29 `holds` in the genesis run of 2026.10.01 (G7 §3, "
            "result 4; item 69, as at G9), **41 of 56** in the run of the floor in force (below).",
            "The checker certifies that the query entails false, **not that cedar's encoding of the floor is "
            "faithful**; that is T-0045-3 and ADR-0030 §3's soundness argument. The signature's rules are trusted as "
            "cvc5's authors wrote them.",
            "[[amber|Proposed (ADR-0053)]]: the genesis floor's 23 totality rows, and since R3 the floor in force's 41, "
            "are proved in Lean under cedar-spec `v4.13.0`'s model, by its proved validator soundness (`floor/lean`; "
            "H7). They would then rest on the Lean kernel (T-0045-37) and on T-0045-3's own premise, the engine's "
            "fidelity to that model, and no longer on cedar's folding code. The `labels` and `control` stages are "
            "not stated in Lean; the reference links neither.",
        ], "open", ""),
        ("D-0030-2: routing verdicts unchecked", "red", [
            "Declared by a deployment that runs the gates without the checker, and the position of **every gate run "
            "before 2026.10.01**: a wrong `holds` lets a relaxation reach a promotion without an issuance.",
            "Subtractive mitigation: make every floor change two-key, tightening included (ADR-0030 §8).",
        ], None, ""),
        ("Not yet in a release", "grey", [
            "The checker is pinned by three digests in the gate header; no mechanism release exists to carry them "
            "(T-0045-30; item 68, as at G9). Gate evidence is now recorded by an operator's signed `AttestGates`: "
            "**attributed, and still an assertion** (ADR-0024 A3; G10 item 57).",
        ], None, ""),
        ("Since Batch 34: what S and a bundle's load gain (ADR-0030 A2)", "teal", [
            "**S gains what the label forbids read**: `clearSet` and `inputLabels` in Run's context; on the tool, "
            "whether it is outward and which destination inputs are literals or labelled handles. The mechanism "
            "computes them; history enters S only as named attributes a mechanism release adds.",
            "**A bundle whose allowlist data fails ADR-0049 §6's W1 to W10 does not load**, a mechanism constant "
            "checked after the signature. W7 and W8 read **the two lists the issued rules carry** (ADR-0025 A2): "
            "adding to either is an issuance, routed like any rules change.",
        ], "accepted", "ADR-0030 · C1"),
        ("The floor in force is genesis-provisional (ADR-0030 A3)", "violet", [
            "Not ratified by any batch; ratified when **the bootstrap reviewer establishes that it is fit** "
            "(ADR-0029 §5, step 6). That gives floor fitness an owner and a time, and **no test** (G10 items 2, 87).",
            "Routing still applies to it: a change is classified against it, and removing X1 was a tightening, a "
            "floor change with the gates run (ADR-0052 §9).",
        ], "genprov", ""),
    ]
    for t, a, b, s_, e in notes:
        h = c.card(RX, py, RW, t, b, accent=a, size=14, status=s_, status_extra=e,
                   dash="6 4" if a == "red" else None)
        py += h + 16
    y = max(left_bot, py) + 70

    # ================================================================ the three gates
    c.text(X0, y + 22, "The three floor gates (ADR-0007, decidable on the floor since ADR-0030 §5)", 22, "ink",
           bold=True)
    y += 44
    gw = (X1 - X0 - 2 * 30) / 3
    gates = [
        ("Totality", "Validation against S, and **never-errors** over the whole floor, per policy per action it "
         "covers.", "Any evaluation error is a deny, so an erroring `forbid` cannot be skipped into an allow."),
        ("Non-vacuity", "**Not always-allows**: the floor refuses some conforming request, per action.",
         "A floor that permits everything admits every bundle and discharges every property over nothing: the widest "
         "silent failure in the system (ToO §3.1)."),
        ("Discrimination", "Non-vacuity **and not always-denies**: the floor both admits and refuses, per action.",
         "An action class the floor always denies is declared as such, never left implicit."),
    ]
    gh = max(c.card(0, 0, gw, t, [a, b], size=15, draw=False) for t, a, b in gates)
    for i, (t, a, b) in enumerate(gates):
        c.card(X0 + i * (gw + 30), y, gw, t, [a, b], accent="teal", size=15, h=gh)
    y += gh + 20
    y += c.para(X0, y, X1 - X0,
                "A failing check returns a counterexample request. The gate run adds **every entry matters** (the floor "
                "minus any one policy is not equivalent to it), routing controls and negative controls. Three gates are "
                "not enough: a fourth, **floor fitness**, is **owned and timed since Batch 34 and has no test**: the "
                "bootstrap reviewer establishes it, and with that the floor is ratified (ADR-0029 A4; ADR-0030 A3; G10 "
                "items 2, 87). The gates say the text is well-formed, non-vacuous and minimal, not that it is the right "
                "floor.", 15, "muted") + 50

    # ================================================================ the staged build
    c.text(X0, y + 22, "The floor in force, built in three gated stages (`floor/proposed/`; ADR-0041 A1 to A3, R2)",
           22, "ink", bold=True)
    y += 46
    stages = [
        ("Genesis floor", "violet", "draft", "", [
            "`floor/genesis-floor.cedar` `28ec0e4552c6a915` · 17 policies · 62 cases.",
            "**DRAFT, unchanged**: the text every stage is built from (G10 §2.2, item 25). Gates all pass, "
            "2026.10.01.",
        ]),
        ("`labels` · intermediate", "teal", None, "", [
            "+ ADR-0047, with ADR-0048 and ADR-0049 (ADR-0030 A2). **Three forbids on** `Actuate`: `R5`, `R6`, `R7`; "
            "the entries are ADR-0041 A1, [[blue|accepted]].",
            "`9aab481d02414de2` · **20** policies · **74** cases · results `3579b95a42573958`.",
            "Reference at `c15026d` (A10).",
        ]),
        ("`control` · intermediate", "teal", None, "", [
            "+ ADR-0050. **Six actions and nine entries** for an `operator` seat: `C1` to `C9`; the entries are "
            "ADR-0041 A3, [[blue|accepted · provisional]] with ADR-0050.",
            "`4341ede9e26419cc` · **29** policies · **106** cases · results `aa96c96916a87c05`.",
            "Reference at `c7de2ba` (A11).",
        ]),
        ("`emergency` · in force", "teal", "genprov", "", [
            "+ ADR-0052. `X1-break-glass` **removed**; `B10` admits the `emergency` kind for `Actuate`.",
            "`15c941b9a56a09f7` · schema `d3c8145c6af2d9a3` · **28** policies · **107** cases · results "
            "`7deaf26c1dc49422`.",
            "Reference at `9c57221` (A12) and since.",
        ]),
    ]
    sg = 70
    sw_ = (X1 - X0 - 3 * sg) / 4
    shh = max(c.card(0, 0, sw_, t, b, size=14, status=st, status_extra=se, draw=False) for t, a, st, se, b in stages)
    for i_, (t, a, st, se, b) in enumerate(stages):
        sx_ = X0 + i_ * (sw_ + sg)
        c.card(sx_, y, sw_, t, b, accent=a, size=14, status=st, status_extra=se, h=shh)
        if i_ < 3:
            c.arrow([(sx_ + sw_, y + shh / 2), (sx_ + sw_ + sg, y + shh / 2)], "teal", sw=2.4)
    y += shh + 20
    stw = 1900
    sth = c.table(X0, y, [("Stage", 170, {"mono": True}), ("Records", 560), ("Change to the floor", 760),
                          ("Policies", 120), ("Cases", 110), ("Gates", stw - 1720)], [
        ["labels", "ADR-0047, with ADR-0048 and ADR-0049 (ADR-0041 A1; ADR-0030 A2)",
         "Three forbids on `Actuate`: `R5`, `R6`, `R7`", "20", "74", "all pass"],
        ["control", "+ ADR-0050 (ADR-0041 A3)", "Six actions and nine entries for an `operator` seat: `C1` to `C9`",
         "29", "106", "all pass"],
        ["emergency", "+ ADR-0052 (ADR-0041 A2)", "`X1-break-glass` removed; `B10` admits the `emergency` kind for "
         "`Actuate`", "28", "107", "all pass"],
    ], size=14, accent="teal")
    c.para(X0, y + sth + 10, stw, "The table of `floor/proposed/README.md`, in full. The genesis floor has 17 "
           "policies and 62 cases. Each stage passes the genesis gates as they stand, plus routing candidates for "
           "its new entries (four for `labels`, nine by `control`, eleven by `emergency`); no `holds` in any run is "
           "without a checked proof. A rerun reproduces each results file byte for byte (G10 §3).", 14, "muted")
    nx_ = X0 + stw + 40
    nh_ = c.card(nx_, y, X1 - nx_, "What the stages do not show", [
        "**The admit-time half only**: ADR-0047's F4 to F6 are load checks on bundle data (W7 to W9), made by the "
        "mechanism, not Cedar.",
        "**The floor trusts its inputs**: `clearSet`, `peerLive` and the rest are facts the lift supplies; "
        "`Labels.tla` and `Operators.tla` model them. The floor's decision on an operator's request is not in the "
        "trace model (G10 §3).",
        "[[red|The stage files open with a wrong comment]], \"not what the reference follows\"; the bytes are kept "
        "as gated so cited digests stay pinned. Correcting it is a gate rerun and new digests (item 91).",
    ], accent="red", size=14, tint=False, dash="6 4")
    y += max(sth + 80, nh_) + 70

    # ================================================================ the floor in force: its gate run, every line
    c.text(X0, y + 22, "The gate run of the floor in force, every line "
           "(`floor/proposed/emergency-gates-results-2026.10.04.txt`)", 22, "ink", bold=True)
    c.pill(X1, y + 4, "RESULT: all gates pass", "teal", size=14, solid=True, anchor="end")
    y += 44
    hh = c.card(X0, y, X1 - X0, "Header: what ran, pinned by digest", [
        "Floor `emergency-floor.cedar` sha256 `15c941b9a56a09f7` · 28 policies · schema `emergency.cedarschema` "
        "`d3c8145c6af2d9a3` · values `genesis-values.json` `85ab6fefb66f0316`. Built by `floor/proposed/build.py` "
        "from the genesis floor. **Genesis-provisional** (ADR-0030 A3); the file's own line \"Not ratified, and not "
        "what the reference follows\" is half wrong since 2026.10.05 (item 91).",
        "`cedar-policy-cli` 4.13.0 · cvc5 1.4.0 [git b432cd7] (binary `a4ce24a176532209`) · checker `ethos` 8dc85c4 "
        "(binary `4eb41c1f1f9fce88`) · CPC signature `tools/cpc` from cvc5-1.4.0 (tree `6d7e8d208d223985`) · wrapper "
        "`cvc5-checked` (`dfe159e9c21a549e`).",
        "Values (placeholders; ADR-0039 §1): `observer.K` = 8, `observer.T_obs_ms` = 5000, pass (`K < R` is checked by "
        "the mechanism at startup); lineage: 5 of 5 values unset (ADR-0035; G4 item 30): theta_exact, theta_near, "
        "theta_gen, beta, near_tool.",
    ], accent="violet", size=14.5, status="genprov", status_extra="the floor under test")
    y += hh + 24
    cw3 = (X1 - X0 - 2 * 30) / 3
    tot = [
        ("B1-read-corpus", "Read"), ("B2-draft-workspace", "Draft"), ("B3-invoke-allowlisted", "Invoke"),
        ("B4-emit-own-topic", "Emit"), ("B5-submit-own-artifact", "Submit"), ("B6-vote-seated", "Vote"),
        ("B7-author-recused", "Vote"), ("B8-grant-only-from-grant-seat", "Vote"),
        ("B9-voters-do-not-author", "Draft"), ("B9-voters-do-not-author", "Invoke"),
        ("B9-voters-do-not-author", "Submit"), ("B10-only-thinkers-author", "Actuate"),
        ("B10-only-thinkers-author", "Draft"), ("B10-only-thinkers-author", "Invoke"),
        ("B10-only-thinkers-author", "Submit"), ("B10-only-thinkers-author", "Actuate"),
        ("R1-actuate-allowlisted", "Actuate"), ("R2-report-own-topic", "Report"), ("R4-consult-pinned", "Consult"),
        ("R3-observer-live", "Actuate"), ("R3-observer-live", "Report"), ("R5-no-read-then-send", "Actuate"),
        ("R6-no-steered-destination", "Actuate"), ("R7-no-replayed-destination", "Actuate"),
        ("X2-erasure", "Erase"), ("F-forensic-classes", "Erase"),
        ("C1-regrant-successor", "Regrant"), ("C2-renew", "Renew"), ("C3-attest-gates", "AttestGates"),
        ("C4-deny", "EndRound"), ("C4-deny", "Revoke"), ("C4-deny", "FenceEpoch"),
        ("C5-add-needs-lease-and-peer", "Regrant"), ("C5-add-needs-lease-and-peer", "Renew"),
        ("C5-add-needs-lease-and-peer", "AttestGates"), ("C6-no-self", "Regrant"), ("C6-no-self", "Renew"),
        ("C7-fence-needs-lease", "FenceEpoch"), ("C8-task-label-in-bounds", "Regrant"),
        ("C9-stop-in-own-domain", "EndRound"), ("C9-stop-in-own-domain", "Revoke"),
    ]
    c.text(X0, y + 18, f"Totality: never-errors, per policy per applicable action ({len(tot)})", 17, "teal",
           bold=True)
    t1 = c.table(X0, y + 30, [("Policy", cw3 - 330, {"mono": True}), ("Action", 150, {"mono": True}),
                              ("Verdict", 100), ("Result", 80)],
                 [[p_, a_, HOLDS_C, "pass"] for p_, a_ in tot], size=13.5, accent="teal")
    x2 = X0 + cw3 + 30
    acts = ["Read", "Draft", "Invoke", "Emit", "Submit", "Vote", "Consult", "Actuate", "Report", "Erase",
            "Regrant", "Renew", "AttestGates", "EndRound", "Revoke", "FenceEpoch"]
    c.text(x2, y + 18, f"Non-vacuity and discrimination, per action ({len(acts)})", 17, "teal", bold=True)
    t2 = c.table(x2, y + 30, [("Action", 150, {"mono": True}), ("always-allows", (cw3 - 230) / 2),
                              ("always-denies", (cw3 - 230) / 2), ("Result", 80)],
                 [[a_, "refuted", "refuted", "pass"] for a_ in acts], size=13.5, accent="teal")
    yy = y + 30 + t2 + 24
    rh_ = c.card(x2, yy, cw3, "Reading these two", [
        "`holds°`: decided by cedar's term folding, no solver query; rests on T-0045-3, not on a proof. In this run "
        "**41 of 56** `holds` are `holds°`: the 39 totality rows and two negative controls (G7 §3, result 4, for "
        "the kind).",
        "`refuted`: the solver returned `sat` with a counterexample request; needs no certificate.",
        "Sixteen actions: the nine of the two alphabets, `Erase`, and **the six of the control alphabet** "
        "(ADR-0050 §4). An `emergency` seat adds no action: it uses Run's `Consult`, `Actuate`, `Report`.",
    ], accent="grey", size=14)
    x3 = X0 + 2 * (cw3 + 30)
    em = [("B1-read-corpus", "Read"), ("B2-draft-workspace", "Draft"), ("B3-invoke-allowlisted", "Invoke"),
          ("B4-emit-own-topic", "Emit"), ("B5-submit-own-artifact", "Submit"), ("B6-vote-seated", "Vote"),
          ("B7-author-recused", "Vote"), ("B8-grant-only-from-grant-seat", "Vote"),
          ("B9-voters-do-not-author", "Draft, Invoke, Submit"),
          ("B10-only-thinkers-author", "Actuate, Draft, Invoke, Submit, Actuate"),
          ("R1-actuate-allowlisted", "Actuate"), ("R2-report-own-topic", "Report"), ("R4-consult-pinned", "Consult"),
          ("R3-observer-live", "Actuate, Report"), ("R5-no-read-then-send", "Actuate"),
          ("R6-no-steered-destination", "Actuate"), ("R7-no-replayed-destination", "Actuate"),
          ("X2-erasure", "Erase"), ("F-forensic-classes", "Erase"), ("C1-regrant-successor", "Regrant"),
          ("C2-renew", "Renew"), ("C3-attest-gates", "AttestGates"), ("C4-deny", "EndRound, Revoke, FenceEpoch"),
          ("C5-add-needs-lease-and-peer", "Regrant, Renew, AttestGates"), ("C6-no-self", "Regrant, Renew"),
          ("C7-fence-needs-lease", "FenceEpoch"), ("C8-task-label-in-bounds", "Regrant"),
          ("C9-stop-in-own-domain", "EndRound, Revoke")]
    c.text(x3, y + 18, f"Every entry matters: floor minus one is not equivalent ({len(em)})", 17, "teal", bold=True)
    t3 = c.table(x3, y + 30, [("Policy", cw3 - 80 - 330, {"mono": True}), ("Differs on", 330), ("Result", 80)],
                 [[p_, a_, "pass"] for p_, a_ in em], size=13.5, accent="teal")
    y += 30 + max(t1, t3, t2 + 24 + rh_) + 40

    c.text(X0, y + 18, "Routing: candidate revisions classified by implies both ways", 17, "blue", bold=True)
    rw_ = 1700
    rcols = [("Candidate", 600), ("`F′ ⇒ F`", 150), ("`F ⇒ F′`", 150), ("Class", 170), ("Route", 550),
             ("Result", rw_ - 1620)]
    T, R_ = "tightening", "relaxation"
    OP, AI = "ordinary promotion", "anchor issuance + promotion"

    def rrow(cand, a_, b_, cls, route):
        return {"cells": [cand, a_, b_, cls, route, "pass"], "accent": "blue" if route == OP else "brown"}
    rt = c.table(X0, y + 30, rcols, [
        {"group": "The four genesis candidates", "accent": "grey"},
        rrow("tighten: voters may not Read", HOLDS_K, "refuted", T, OP),
        rrow("relax: F1 removed from the forensic floor", "refuted", HOLDS_K, R_, AI),
        rrow("incomparable: F1 erasable, payload not", "refuted", "refuted", "incomparable", AI),
        rrow("relax: R4 without the Run-root condition", "refuted", HOLDS_K, R_, AI),
        {"group": "New entries: a weakened entry is a relaxation, a strengthened one a tightening (11)",
         "accent": "grey"},
        rrow("relax: R6 removed", "refuted", HOLDS_K, R_, AI),
        rrow("relax: R5 reads only what was read in the clear", "refuted", HOLDS_K, R_, AI),
        rrow("tighten: R6 without the untrusted-read condition", HOLDS_K, "refuted", T, OP),
        rrow("relax: R7 removed", "refuted", HOLDS_K, R_, AI),
        rrow("relax: C5 without the peer condition", "refuted", HOLDS_K, R_, AI),
        rrow("relax: C7 removed, a lapsed operator may fence", "refuted", HOLDS_K, R_, AI),
        rrow("tighten: C4 needs a live lease", HOLDS_K, "refuted", T, OP),
        rrow("relax: C1 without the alphabet comparison", "refuted", HOLDS_K, R_, AI),
        rrow("relax: C8 removed, an unlabelled task", "refuted", HOLDS_K, R_, AI),
        rrow("tighten: B10 as at genesis, no emergency seat", HOLDS_K, "refuted", T, OP),
        rrow("relax: B10 admits every kind for Actuate", "refuted", HOLDS_K, R_, AI),
    ], size=14, accent="blue")
    nx = X0 + rw_ + 40
    c.text(nx, y + 18, "Negative controls: each gate must catch a defective floor", 17, "red", bold=True)
    nt = c.table(nx, y + 30, [("Defective floor", X1 - nx - 160 - 120 - 100), ("Gate", 160), ("Verdict", 120),
                              ("", 100)], [
        ["vacuous floor: permit-all added (Read)", "always-allows", HOLDS_C, "caught"],
        ["vacuous floor: permit-all added (Consult)", "always-allows", HOLDS_C, "caught"],
        ["erroring policy: Long overflow", "never-errors", "refuted", "caught"],
        ["dead entry: forbid F1 duplicated", "equivalent", HOLDS_K, "caught"],
    ], size=14, accent="red")
    cy_ = y + 30 + nt + 40
    c.text(nx, cy_ + 18, "Checker controls: a solver that lies must not produce a `holds` (ADR-0030 §5 A1)", 17,
           "red", bold=True)
    ct = c.table(nx, cy_ + 30, [("The lying solver", 420), ("Query", 110), ("Outcome", 170),
                                ("Why it was refused", X1 - nx - 700)], [
        ["answers unsat with no proof", "`F=>F'`", "ERROR → caught", "proof dump has an unexpected shape"],
        ["answers unsat with a proof of another query", "`F=>F'`", "ERROR → caught",
         "assume @p1 is not one of the query's assertions"],
        ["answers unsat with a proof missing a step", "`F=>F'`", "ERROR → caught",
         "checker refused: Error: q-0.cpc:107.42: Could not find symbol @p55"],
        {"cells": ["holds without a checked proof, whole run", "", "**0** → none", ""], "accent": "blue"},
        {"cells": ["holds without a checked proof, new-entry routing", "", "**0** → none", ""], "accent": "blue"},
    ], size=14, accent="red")
    ey = cy_ + 30 + ct + 24
    c.card(nx, ey, X1 - nx, "Evidence (every solver query, its proof and the checker's verdict)", [
        "**151** cedar calls · **108** solver queries · **15** `unsat` with a checked proof (routing's fourteen "
        "`holds✓` and the dead-entry control) · **90** `sat` (counterexample) · **3** `unknown`/unchecked (the three "
        "checker controls).",
        "Evidence tree sha256 `974f339662a5289d`, **not copied**; a rerun reproduces it. What the checker controls "
        "test is the wrapper's refusals, not the signature's rules, and wrapper, controls and gates are the same "
        "hand's work (G10 §8).",
    ], accent="blue", size=14.5)
    return c
