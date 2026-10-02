"""B3 — Floor-change routing, the proof-carrying gate, and the 2026.10.01 gate run."""
from lib import Canvas

ID, SLUG = "B3", "floor-change-routing"

HOLDS_C = "[[teal|holds°]]"
HOLDS_K = "[[blue|holds✓]]"


def build():
    c = Canvas(ID, "Changing the floor: the route is computed, and since 2026.10.01 every solver `holds` carries a "
               "checked proof",
               "A candidate floor F′ is compared with the deployed floor F in both directions; the answer, not the "
               "author, picks the authority path. A Build author is Byzantine by premise and cannot relabel a "
               "relaxation as a tightening; a wrong solver could, until ADR-0030 A1 made the solver trusted for "
               "nothing. The same gate run checks the three floor gates. The floor it ran on is a DRAFT.",
               3200, "ToO rev 11 §2.2, §3.1, §3.2, §3.3, §7.3, §7.9; G7 §1 (Batch 24), §2.2, §2.8, §3 (results 1–6), "
               "§5, §7 items 25, 68, 69; ADR-0007; ADR-0025 §1; ADR-0026 §4, §5; ADR-0030 §4, §5 with A1, §8 "
               "(D-0030-2), §10; ADR-0045 T-0045-3, T-0045-14; floor/README.md; "
               "floor/genesis-gates-results-2026.10.01.txt")
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
        "In the mechanism release, resident; the genesis text is the draft `28ec0e4552c6a915`.",
    ], accent="teal", size=14.5, status="draft")
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
            "never-errors check on the genesis floor, and a permit-all under always-allows. They rest on the Cedar "
            "engine's row, **T-0045-3**, not on a proof: 25 of the run's 29 `holds` (G7 §3, result 4; item 69).",
            "The checker certifies that the query entails false, **not that cedar's encoding of the floor is "
            "faithful**; that is T-0045-3 and ADR-0030 §3's soundness argument. The signature's rules are trusted as "
            "cvc5's authors wrote them.",
        ], "open", ""),
        ("D-0030-2: routing verdicts unchecked", "red", [
            "Declared by a deployment that runs the gates without the checker, and the position of **every gate run "
            "before 2026.10.01**: a wrong `holds` lets a relaxation reach a promotion without an issuance.",
            "Subtractive mitigation: make every floor change two-key, tightening included (ADR-0030 §8).",
        ], None, ""),
        ("Not yet in a release", "grey", [
            "The checker is pinned by three digests in the gate header; no mechanism release exists to carry them "
            "(T-0045-30; G7 item 68). The gate evidence is still unsigned (G7 item 57).",
        ], None, ""),
    ]
    for t, a, b, s, e in notes:
        h = c.card(RX, py, RW, t, b, accent=a, size=14, status=s, status_extra=e, dash="6 4" if a == "red" else None)
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
                "not enough by Moon & Varshney's own result: a fourth, **floor fitness**, is required and unowned "
                "(ToO §11.1; G7 item 2). The gates say the text is well-formed, non-vacuous and minimal, not that it is "
                "the right floor.", 15, "muted") + 50

    # ================================================================ the 2026.10.01 run, every line
    c.text(X0, y + 22, "The gate run of 2026.10.01, every line (`floor/genesis-gates-results-2026.10.01.txt`)", 22,
           "ink", bold=True)
    c.pill(X1, y + 4, "RESULT: all gates pass", "teal", size=14, solid=True, anchor="end")
    y += 44
    hh = c.card(X0, y, X1 - X0, "Header: what ran, pinned by digest", [
        "Floor `genesis-floor.cedar` sha256 `28ec0e4552c6a915` · 17 policies · schema `0ec2fa215eefe136` · values "
        "`85ab6fefb66f0316`: unchanged from 2026.09.30, and **DRAFT**.",
        "`cedar-policy-cli` 4.13.0 · cvc5 1.4.0 [git b432cd7] (binary `a4ce24a176532209`) · checker `ethos` 8dc85c4 "
        "(binary `4eb41c1f1f9fce88`) · CPC signature `tools/cpc` from cvc5-1.4.0 (tree `6d7e8d208d223985`) · wrapper "
        "`cvc5-checked` (`dfe159e9c21a549e`).",
        "Values (placeholders; ADR-0039 §1): `observer.K` = 8, `observer.T_obs_ms` = 5000, pass (`K < R` is checked by "
        "the mechanism at startup); lineage: 5 of 5 values unset (ADR-0035; G4 item 30): theta_exact, theta_near, "
        "theta_gen, beta, near_tool.",
    ], accent="violet", size=14.5, status="draft", status_extra="the floor under test")
    y += hh + 24
    cw3 = (X1 - X0 - 2 * 30) / 3
    tot = [
        ("B1-read-corpus", "Read"), ("B2-draft-workspace", "Draft"), ("B3-invoke-allowlisted", "Invoke"),
        ("B4-emit-own-topic", "Emit"), ("B5-submit-own-artifact", "Submit"), ("B6-vote-seated", "Vote"),
        ("B7-author-recused", "Vote"), ("B8-grant-only-from-grant-seat", "Vote"),
        ("B9-voters-do-not-author", "Draft"), ("B9-voters-do-not-author", "Invoke"),
        ("B9-voters-do-not-author", "Submit"), ("B10-only-thinkers-author", "Draft"),
        ("B10-only-thinkers-author", "Invoke"), ("B10-only-thinkers-author", "Submit"),
        ("B10-only-thinkers-author", "Actuate"), ("R1-actuate-allowlisted", "Actuate"),
        ("R2-report-own-topic", "Report"), ("R4-consult-pinned", "Consult"), ("R3-observer-live", "Actuate"),
        ("R3-observer-live", "Report"), ("X1-break-glass", "Actuate"), ("X2-erasure", "Erase"),
        ("F-forensic-classes", "Erase"),
    ]
    c.text(X0, y + 18, "Totality: never-errors, per policy per applicable action (23)", 17, "teal", bold=True)
    t1 = c.table(X0, y + 30, [("Policy", cw3 - 330, {"mono": True}), ("Action", 130, {"mono": True}),
                              ("Verdict", 110), ("Result", 90)],
                 [[p, a, HOLDS_C, "pass"] for p, a in tot], size=13.5, accent="teal")
    x2 = X0 + cw3 + 30
    c.text(x2, y + 18, "Non-vacuity and discrimination, per action (10)", 17, "teal", bold=True)
    acts = ["Read", "Draft", "Invoke", "Emit", "Submit", "Vote", "Consult", "Actuate", "Report", "Erase"]
    t2 = c.table(x2, y + 30, [("Action", 130, {"mono": True}), ("always-allows", (cw3 - 220) / 2),
                              ("always-denies", (cw3 - 220) / 2), ("Result", 90)],
                 [[a, "refuted", "refuted", "pass"] for a in acts], size=13.5, accent="teal")
    yy = y + 30 + t2 + 24
    c.card(x2, yy, cw3, "Reading these two", [
        "`holds°`: decided by cedar's term folding, no solver query; rests on T-0045-3.",
        "`refuted`: the solver returned `sat` with a counterexample request; needs no certificate.",
        "The nine actions of the two alphabets plus `Erase`; ToO §3.1 counts \"every action of the nine\".",
    ], accent="grey", size=14)
    x3 = X0 + 2 * (cw3 + 30)
    c.text(x3, y + 18, "Every entry matters: floor minus one is not equivalent (17)", 17, "teal", bold=True)
    em = [("B1-read-corpus", "Read"), ("B2-draft-workspace", "Draft"), ("B3-invoke-allowlisted", "Invoke"),
          ("B4-emit-own-topic", "Emit"), ("B5-submit-own-artifact", "Submit"), ("B6-vote-seated", "Vote"),
          ("B7-author-recused", "Vote"), ("B8-grant-only-from-grant-seat", "Vote"),
          ("B9-voters-do-not-author", "Draft, Invoke, Submit"),
          ("B10-only-thinkers-author", "Draft, Invoke, Submit, Actuate"), ("R1-actuate-allowlisted", "Actuate"),
          ("R2-report-own-topic", "Report"), ("R4-consult-pinned", "Consult"),
          ("R3-observer-live", "Actuate, Report"), ("X1-break-glass", "Actuate"), ("X2-erasure", "Erase"),
          ("F-forensic-classes", "Erase")]
    t3 = c.table(x3, y + 30, [("Policy", cw3 - 90 - 290, {"mono": True}), ("Differs on", 290), ("Result", 90)],
                 [[p, a, "pass"] for p, a in em], size=13.5, accent="teal")
    y += 30 + max(t1, t3, t2 + 24 + 200) + 40

    c.text(X0, y + 18, "Routing: candidate revisions classified by implies both ways", 17, "blue", bold=True)
    rt = c.table(X0, y + 30, [("Candidate", 520), ("`F′ ⇒ F`", 170), ("`F ⇒ F′`", 170), ("Class", 200),
                              ("Route", 430), ("Result", 90)], [
        {"cells": ["tighten: voters may not Read", HOLDS_K, "refuted", "tightening", "ordinary promotion", "pass"],
         "accent": "blue"},
        {"cells": ["relax: F1 removed from the forensic floor", "refuted", HOLDS_K, "relaxation",
                   "anchor issuance + promotion", "pass"], "accent": "brown"},
        {"cells": ["incomparable: F1 erasable, payload not", "refuted", "refuted", "incomparable",
                   "anchor issuance + promotion", "pass"], "accent": "brown"},
        {"cells": ["relax: R4 without the Run-root condition", "refuted", HOLDS_K, "relaxation",
                   "anchor issuance + promotion", "pass"], "accent": "brown"},
    ], size=14, accent="blue")
    nx = X0 + 1580 + 40
    c.text(nx, y + 18, "Negative controls: each gate must catch a defective floor", 17, "red", bold=True)
    nt = c.table(nx, y + 30, [("Defective floor", X1 - nx - 160 - 120 - 100), ("Gate", 160), ("Verdict", 120),
                              ("", 100)], [
        ["vacuous floor: permit-all added (Read)", "always-allows", HOLDS_C, "caught"],
        ["vacuous floor: permit-all added (Consult)", "always-allows", HOLDS_C, "caught"],
        ["erroring policy: Long overflow", "never-errors", "refuted", "caught"],
        ["dead entry: forbid F1 duplicated", "equivalent", HOLDS_K, "caught"],
    ], size=14, accent="red")
    y += 30 + max(rt, nt) + 40

    c.text(X0, y + 18, "Checker controls: a solver that lies must not produce a `holds` (ADR-0030 §5 A1)", 17, "red",
           bold=True)
    ct = c.table(X0, y + 30, [("The lying solver", 560), ("Query", 140), ("Outcome", 180),
                              ("Why it was refused", 700)], [
        ["answers unsat with no proof", "`F=>F'`", "ERROR → caught", "proof dump has an unexpected shape"],
        ["answers unsat with a proof of another query", "`F=>F'`", "ERROR → caught",
         "assume @p1 is not one of the query's assertions"],
        ["answers unsat with a proof missing a step", "`F=>F'`", "ERROR → caught",
         "checker refused: Error: q-0.cpc:108.42: Could not find symbol @p55"],
        {"cells": ["holds without a checked proof, whole run", "", "**0** → none", ""], "accent": "blue"},
    ], size=14, accent="red")
    ex = X0 + 1580 + 40
    c.card(ex, y + 30, X1 - ex, "Evidence (every solver query, its proof and the checker's verdict)", [
        "**81** cedar calls · **56** solver queries · **4** `unsat` with a checked proof (routing's three `holds` and "
        "the dead-entry control) · **49** `sat` (counterexample) · **3** `unknown`/unchecked (the three controls) · "
        "**25** `holds°` without a query.",
        "Evidence tree sha256 `f8b1196a427a35ed`, copied to `floor/genesis-gates-evidence-2026.10.01/`, reproducible "
        "run to run. What three controls test is the wrapper's refusals, not the signature's rules, and the wrapper "
        "and controls are the same hand's work as the gates (G7 §4, §8).",
    ], accent="blue", size=14.5)
    return c
