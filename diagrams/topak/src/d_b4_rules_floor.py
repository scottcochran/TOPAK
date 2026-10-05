"""B4 — The rules floor: what bounds the anchor, entry by entry, the two runs that checked it, and the proof."""
from lib import Canvas

ID, SLUG = "B4", "rules-floor"


def build():
    c = Canvas(ID, "The rules floor bounds every anchor issuance",
               "ADR-0010's move applied one layer up: the anchor is a havoc issuer (ADR-0025), and the rules floor "
               "(ADR-0026) joins the verified object so the mechanism rejects any issuance that violates it. Genesis "
               "rules floor at G10: **R1, R2, R5, R6, R7, R9** in force; R3, R4 and **R8 withdrawn**; R6 and R7 "
               "**change subject** with break-glass re-homed (ADR-0026 A2, provisional). Since 2026.10.02 its "
               "properties are proved, each under the entry it rests on; `RulesFloorBase.tla` has not caught up.",
               2800, "ADR-0026 §1–§7, History A1, W1, A2, B2, B4, B25, B34, R1–R3 and the A1 note; ADR-0025 §1 (a)–(h) "
               "with A1, A2, A3 and B29; ADR-0046 §4, §5, A1; ADR-0029 §4 with A4, §5, B25; ADR-0052 §1, §3, §9 (R5); "
               "ADR-0013 §3 with A1; ADR-0024 §2, §6, A2 and Degeneracies; ADR-0032 §2; ToO rev 14 §3.3, §7.2, §7.3, "
               "§7.7, §9; G10 §1, §1.2, §2.1, §2.9, §3, §7 items 8, 39 (as at G9), 90; spec/RulesFloorNV.tla, "
               "RulesFloorNV-results-2026.09.15.txt, RulesFloorNV_rev5.tla, RulesFloorNV-rev5-results-2026.09.23.txt, "
               "bootstrap-results-2026.09.23.txt, RulesFloorNV_rev5_proof.tla, "
               "RulesFloorNV_rev5-proof-results-2026.10.02.txt, RulesFloorNV_rev5-proof-cert-results-2026.10.04.txt, "
               "RulesFloorBase.tla, Anchor-proof-results-2026.10.02.txt, BreakGlass-proof-results-2026.10.02.txt, "
               "BreakGlass_A1-results-2026.10.05.txt, NonComposition_A1-rows.txt")
    X0, X1 = c.x0, c.x1
    W = X1 - X0
    gap = 28
    y = c.y + 14

    # ------------------------------------------------------------------ row 1: the issuance path
    w_anchor, w_floor = 560, 640
    w_rules = W - w_anchor - w_floor - 2 * 110
    xa, xf = X0, X0 + w_anchor + 110
    xr = xf + w_floor + 110
    anchor_body = [
        "Any authentic issuance, bounded only by `Authentic`, an epoch increment and the rules floor. "
        "`Issue` is an environment action (ADR-0025 §2).",
        "**Intent is the sole axiom**: an authentic issuance at the current anchor epoch is what the anchor "
        "intended. No safety theorem covers it.",
    ]
    floor_body = [
        "The mechanism **rejects** any issuance that violates the floor; proofs quantify over every "
        "floor-conformant issuance sequence (ADR-0026 §1).",
        "ADR-0007's totality, non-vacuity and discrimination gates run on it: a vacuous rules floor admits a "
        "roster of none (§3).",
        "Kept minimal, for ADR-0010's reviewability argument.",
    ]
    rules_body = [
        "**(a)** the promotion roster and its parameters (`quorum`, `minGrant`; ADR-0024); read since A3 to include "
        "the `operator` seats and, at genesis, the first operators' seatings",
        "**(b)** the break-glass and erasure quorum rosters; for break-glass the rules now carry the roster and its "
        "quorum only (ADR-0026 A2)",
        "**(c)** the anchor's own key set",
        "**(d)** any change that relaxes the policy floor or adds a floor exception",
        "**(e)** any change to the rules floor, **in either direction**",
        "**(f)** keys accepted in place of the mechanism's own check: the rung-3 verifier's appraisal key and "
        "the bundle-signing key (A1, Batch 17), and **an identity provider's key** (A3, Batch 34, provisional)",
        "**(g)** the independence criterion in force (B29) · **(h)** the **two lists** a bundle's load checks read: "
        "entries that may release a reserved label, and the channel targets inside the deployment (A2, Batch 34)",
        "Tightening the **policy** floor is not a rules change: it is an ordinary promotion.",
    ]
    h1 = max(c.card(0, 0, w_anchor, "Trust anchor · havoc issuer", anchor_body, draw=False, sub="ADR-0025"),
             c.card(0, 0, w_floor, "Rules floor · inside the verified object", floor_body, draw=False,
                    sub="ADR-0026 §1, §3"),
             c.card(0, 0, w_rules, "Rules: the authority-defining set", rules_body, draw=False,
                    sub="ADR-0025 §1 with A1 · what an issuance carries"))
    c.card(xa, y, w_anchor, "Trust anchor · havoc issuer", anchor_body, accent="brown", h=h1, sub="ADR-0025")
    c.card(xf, y, w_floor, "Rules floor · inside the verified object", floor_body, accent="teal", h=h1,
           sub="ADR-0026 §1, §3")
    c.card(xr, y, w_rules, "Rules: the authority-defining set", rules_body, accent="blue", h=h1,
           sub="ADR-0025 §1 with A1 · what an issuance carries")
    ay = y + 70
    c.arrow([(xa + w_anchor, ay), (xf, ay)], "brown", sw=2.4, label="Issue(rules)", loff=(0, -20))
    c.arrow([(xf + w_floor, ay), (xr, ay)], "blue", sw=2.4, label="admitted", loff=(0, -20))
    c.label(xf + w_floor + 55, ay + 34, "epoch e+1", "blue", 12)
    # rejection path
    ry = y + h1
    c.arrow([(xf + w_floor / 2, ry), (xf + w_floor / 2, ry + 64)], "red", dash="7 5", sw=2.2)
    c.label(xf + w_floor / 2, ry + 82, "violating issuance: **rejected**, epoch unchanged", "red", 13)
    c.text(xr, ry + 30, "Every admitted issuance is persisted with genesis residency (ADR-0027 §3); epoch 0 is "
           "the genesis rules.", 13.5, "muted")
    y = ry + 120

    # ------------------------------------------------------------------ row 2: the full floor table + side cards
    tw = 1800
    cols = [("Entry", 70, {"bold": True}),
            ("Bound (ADR-0026 §2)", 430),
            ("Bounds", 200),
            ("State at G10", 330),
            ("Why, and what it protects", tw - 70 - 430 - 200 - 330)]
    rows = [
        {"cells": ["R1", "`rules.quorum = \"all\"`: unanimity over counted grant seats", "ADR-0024 §2 quorum",
                   "[[blue|In force]] · ratified 09.23 (B2)",
                   "Archetype value. Relaxing R1 alone yields a threshold k: D-0024-1, k-of-n grant seats. "
                   "Dropping it fails `P1_Unanimity` (09.23 run)."], "accent": "blue"},
        {"cells": ["R2", "`rules.minGrant ≥ 2`", "ADR-0024 roster minimum",
                   "[[blue|In force]] · ratified 09.23 (B2)",
                   "Without it a havoc issuance sets an empty roster with `minGrant = 0`; unanimity over the empty "
                   "set is vacuously true and the artifact **promotes with zero votes** (09.15 finding 3). "
                   "R1 alone does not protect against an empty roster."], "accent": "blue"},
        {"cells": ["R3", "`rules.recuse = TRUE` (author recusal)", "—",
                   "[[grey|Withdrawn 09.23]] (revision R1) · ID reserved, not reused",
                   "Vacuous: recusal is a mechanism constant (ADR-0024 §6) enforced by the ADR-0022 `Vote` "
                   "envelope, so no issued value exists to bound. Safe on evidence: remove recusal from the "
                   "mechanism and the author self-grants (09.23 finding 2)."], "accent": "grey"},
        {"cells": ["R4", "Vote timeout ⇒ deny", "—",
                   "[[grey|Withdrawn 09.15]] · ID reserved, not reused",
                   "Vacuous in any design anyone would choose; \"a timeout is never a grant\" became an ADR-0024 "
                   "mechanism constant. `P4` holds with an empty floor (09.15 finding 2)."], "accent": "grey"},
        {"cells": ["R5", "No key both in the anchor key set and on the promotion roster for the same artifact",
                   "ADR-0025 / ADR-0024", "[[blue|In force]] · ratified 09.23 (B2)",
                   "Keeps anchor key-holders and grant seats disjoint (with R2, the headcount of five). An (f) key is "
                   "not a seat and casts no vote, so A1 leaves R5 unchanged."], "accent": "blue"},
        {"cells": ["R6", "Bound on the floor-exception count. **The count it bounds is 1, erasure** (A2); it was 2, "
                   "erasure and break-glass", "ADR-0013",
                   "[[blue|In force]] · effective 2026.09.23 (B4) · [[blue|count 1 since B34, provisional]] (A2)",
                   "X1 is retired: break-glass is an emergency seating and needs no exception (ADR-0052 §2; ADR-0013 "
                   "A1). A second exception is a policy-floor relaxation: an anchor issuance plus a promotion (§4)."],
         "accent": "blue"},
        {"cells": ["R7", "**No activation of an emergency seating grants a lease whose alphabet holds an authority "
                   "act** (A2). It read: no break-glass grant may authorize `Issue`, `Vote`, or promotion",
                   "ADR-0052 / ADR-0013", "[[blue|In force]] · ratified 09.23 (B2) · "
                   "[[blue|subject changed B34, provisional]] (A2)",
                   "The `emergency` kind's alphabet is `Consult`, `Actuate`, `Report`, so R7 **has nothing left to "
                   "refuse**; it is kept for the day the kind changes. `BreakGlass_A1`: dropping R7 changes nothing; "
                   "a kind given an authority act is refused at activation while R7 is in the floor."],
         "accent": "blue"},
        {"cells": ["R8", "`0 < rules.breakGlass.ttl ≤ T_BG`: a finite break-glass grant TTL",
                   "ADR-0009 / ADR-0013",
                   "[[grey|Withdrawn 2026.10.04]] (W1) before it was ever in force · ID reserved",
                   "A TTL needs trusted time, which the corpus refuses (ADR-0032 §2; ADR-0045 §6). A break-glass "
                   "grant is an emergency seating's one lease and **ends with its round** (ADR-0052 §3), on the "
                   "lease's own clock. Not coming back as a TTL (G10 §1)."], "accent": "grey"},
        {"cells": ["R9", "`rules.quorum = \"all\" ∨ rules.quorum ≥ 2`", "ADR-0024",
                   "[[blue|In force]] · **conditional entry**: binds only once R1 is relaxed",
                   "Keeps D-0024-1 (k-of-n) from being D-0024-2 (single signer) wearing a threshold. The corpus's "
                   "first entry that bounds degeneracies rather than the archetype; independent only relative to a "
                   "floor without R1."], "accent": "blue"},
    ]
    c.heading(X0, y, "The archetype rules floor, every entry (ADR-0026 §2; ToO §7.3)", "ink", 21)
    y += 40
    th = c.table(X0, y, cols, rows, size=14)

    sx = X0 + tw + gap + 12
    sw = X1 - sx
    sy = y
    hh = c.card(sx, sy, sw, "The genesis rules floor today", [
        "**R1, R2, R5, R6, R7, R9** in force (G10 §2.1); the entry set unchanged since G6.",
        "R3, R4 and R8 withdrawn; their IDs stay reserved. **No amendment is pending** anywhere in the corpus "
        "(G10 §1.1).",
        "`RulesFloorNV_rev5`'s six properties are **proved**, each under the entry it rests on; P9's premise is "
        "exact: R2, and R1 or R9 (ADR-0026 B25).",
        "The rules gain three issued things: the provider's key (ADR-0025 A3) and the two lists (A2). **The rules "
        "floor bounds none of them**; whether an entry should bound the lists is not decided (G10 §2.1).",
    ], accent="blue", status="accepted", status_extra="bootstrap set · no confirmation marker")
    sy += hh + 22
    hh = c.card(sx, sy, sw, "R6 and R7 change subject (ADR-0026 A2)", [
        "Ratified in Batch 34 with ADR-0052 and **provisional with it**: in force, and subject to redesign "
        "(ADR-0029 A4).",
        "In the bootstrap set, so **not confirmation-required**; covered by the genesis attestation, which must "
        "**name it as provisional** (ADR-0029 §4 with A4).",
        "`RulesFloorBase.tla` [[red|has not caught up]]: it still carries `bgScope` and R6's bound of two "
        "(G10 item 90). The non-vacuity artifacts, which model a break-glass grant, owe a rerun (A2).",
    ], accent="blue", status="provisional", status_extra="bootstrap set")
    sy += hh + 22
    hh = c.card(sx, sy, sw, "Parametricity is load-bearing", [
        "A floor entry bounds something **only if the mechanism reads that value from issued rules**.",
        "Against ADR-0024 revision 3, which hard-coded unanimity, recusal and a minimum of 2, R1–R3 constrained "
        "nothing (09.15 finding 1): **fix ADR-0024, not the floor**.",
    ], accent="teal")
    sy += hh + 22
    hh = c.card(sx, sy, sw, "…and so is its converse", [
        "A value the mechanism fixes as a **constant** cannot be bounded by a floor entry at all.",
        "That is why R4 (timeout) and R3 (recusal) are withdrawn: both are mechanism constants now, beside "
        "ADR-0024 A2's two tally conditions.",
    ], accent="teal")
    sy += hh + 22
    c.card(sx, sy, sw, "Modeled, not declared (ToO §7.7)", [
        "The quorum's archetype values live inside the rules floor, so **a promotion degeneracy is a mechanism "
        "release** and reopens the promotion theorem; anchor custody is a declaration and reopens nothing.",
    ], accent="violet", h=max(0, y + th - sy))
    hh = c.card(sx, sy, sw, "Modeled, not declared (ToO §7.7)", [
        "The quorum's archetype values live inside the rules floor, so **a promotion degeneracy is a mechanism "
        "release** and reopens the promotion theorem; anchor custody is a declaration and reopens nothing.",
    ], accent="violet", h=max(0, y + th - sy), draw=False)
    y = max(y + th, sy + hh) + 60

    # ------------------------------------------------------------------ row 3: two keys, both directions
    c.heading(X0, y, "Two keys, both directions (ADR-0026 §4, §5; ADR-0025 §1 (d), (e))", "ink", 21)
    y += 46
    lab_w = 560
    kx1 = X0 + lab_w + 120
    kw = 520
    kx2 = kx1 + kw + 60
    rx = kx2 + kw + 120
    rw = X1 - rx
    lanes = [
        ("**Rules floor: tighten**", "brown", True, "under the rules **being replaced** (§4)",
         "A tightened rules floor constrains the anchor itself, so **the anchor must consent**. This is where the "
         "rules floor differs from the policy floor."),
        ("**Rules floor: relax**", "brown", True, "under the rules **being replaced** (§4)",
         "Relaxing any entry is a degeneracy (D-0024-1: relax R1; D-0024-2: relax R1, R9 and R2) and ships as a "
         "mechanism release."),
        ("**Policy floor: relax, or add an exception**", "brown", True, "plus the issuance (§5)",
         "A rules change (ADR-0025 §1 (d)); R6 bounds the exception count, which is one."),
        ("**Policy floor: tighten**", "green", False, "an ordinary promotion (§5)",
         "Not a rules change: **an ordinary promotion**, no anchor issuance."),
    ]
    lh = 76
    for i, (lab, acc, k1, k2, note) in enumerate(lanes):
        ly = y + i * (lh + 18)
        c.card(X0, ly, lab_w, None, [lab], accent="grey", bullets=False, h=lh, size=15)
        mid = ly + lh / 2
        if k1:
            c.card(kx1, ly, kw, "Key 1 · anchor issuance", ["ADR-0025 · signed under custody's `Authentic`"],
                   accent="brown", bullets=False, h=lh, size=13.5)
        else:
            c.card(kx1, ly, kw, "No issuance needed", ["The anchor is not consulted"], accent="grey",
                   bullets=False, h=lh, size=13.5, tint=False, dash="6 4")
        c.card(kx2, ly, kw, "Key 2 · promotion (ADR-0024)",
               [k2],
               accent="blue", bullets=False, h=lh, size=13.5)
        c.arrow([(X0 + lab_w, mid), (kx1, mid)], "grey", sw=2)
        c.text(kx1 + kw + 30, mid + 8, "+", 24, "ink", bold=True, anchor="middle")
        c.arrow([(kx2 + kw, mid), (rx, mid)], acc if acc != "brown" else "blue", sw=2)
        c.card(rx, ly, rw, None, [note], accent="grey", bullets=False, h=lh, size=14, tint=False)
    y += 4 * (lh + 18) + 40
    c.para(X0, y, W, "Both directions are slow on purpose: \"that is the right price, and it needs stating\" "
           "(ADR-0026 Consequences). Runtime subtraction (e-stop, lease expiry, revocation, `deny=all`) needs "
           "neither key (ADR-0024 §9).", 14.5, "muted")
    y += 60

    # ------------------------------------------------------------------ row 4: the two TLC runs
    c.heading(X0, y, "Two TLC runs: non-vacuity and discrimination at small constants, not proof", "ink", 21)
    y += 46
    hw = (W - 40) / 2
    lx, rx2 = X0, X0 + hw + 40

    m1 = [
        "`RulesFloorNV.tla` · digest `1468d8bab89bb076` · TLC 1.8.0 · ADR-0026 §6.",
        "Humans {h1, h2, h3, h4}; author h1; anchor key-holder h4; one artifact; one havoc issuance, which "
        "fences in-flight votes. Three mechanism variants: `param` (reads `quorum`, `minGrant`, `recuse`, an "
        "invented `timeoutGrant`), `as0024` (ADR-0024 rev 3's snippet), `rev4` (rev 4's snippet; floor R1–R3, R5, "
        "R7).",
        "**Superseded in part 09.23**: `rev4` reads `recuse` and states the non-unanimous case as `Granted # {}`; "
        "no column covers R9.",
    ]
    m2 = [
        "`RulesFloorNV_rev5.tla` · digest `3034df144d75ec3a` · TLC2 2.19 · ADR-0026 §7.",
        "Mechanism is ADR-0024 revision 5 (`quorum` is `\"all\"` or k; `recuse` not issued) and the ADR-0022 "
        "`Vote` envelope **is modeled for the first time**. Five humans; author h1; anchor key-holder h4; one havoc "
        "issuance; recusal enforced at both sites. Floor R1, R2, R5, R7, R9.",
        "**Scope:** no veto seats. The rerun with A2.2 and A2.3 as conjuncts of `PromotionEnabled` is owed "
        "(item 39, as at G9). Both runs model break-glass by `bgScope`, R7's reading before A2.",
    ]
    mh = max(c.card(0, 0, hw, "Run 1 · 2026.09.15 · RulesFloorNV", m1, draw=False),
             c.card(0, 0, hw, "Run 2 · 2026.09.23 · RulesFloorNV_rev5", m2, draw=False))
    c.card(lx, y, hw, "Run 1 · 2026.09.15 · RulesFloorNV", m1, accent="grey", h=mh, size=14)
    c.card(rx2, y, hw, "Run 2 · 2026.09.23 · RulesFloorNV_rev5", m2, accent="teal", h=mh, size=14)
    y += mh + 18

    ok = "[[green|counterexample ✓]]"
    vac = "[[red|holds ✗ vacuous]]"
    t1cols = [("Check (09.15)", hw * 0.40), ("`param`", hw * 0.20), ("`as0024`", hw * 0.18),
              ("`rev4`", hw * 0.22)]
    t1 = [
        ["Satisfiability and independence (ASSUME)", "pass", "pass", "pass"],
        ["Full floor, all properties", "holds", "holds", "**holds**"],
        ["Reachability (`NeverPromoted` must fail)", ok, ok, ok],
        ["Drop R1 → P1 every counted seat granted", ok, vac, ok],
        ["Drop R2 → P2 at least two approvers", ok, vac, ok],
        ["Drop R3 → P3 author not counted", ok, vac, ok],
        ["R4 → P4 no timeout counted as grant", ok + " (invented `timeoutGrant` only)", vac,
         "**holds with an empty floor**: a mechanism property, as intended"],
        ["Drop R5 → P5 no anchor key-holder approves", ok, ok, ok],
        ["Drop R7 → P7 break-glass never changes authority", ok, ok, ok],
    ]
    t2cols = [("Check (09.23)", hw * 0.32), ("Active floor", hw * 0.20), ("Invariant", hw * 0.26),
              ("Result", hw * 0.22)]
    t2 = [
        ["Satisfiability, independence (ASSUME)", "—", "—", "pass"],
        ["Full floor", "R1 R2 R5 R7 R9", "`Safe`", "**holds**"],
        ["Reachability", "R1 R2 R5 R7 R9", "`NeverPromoted`", ok],
        ["Drop R1", "R2 R5 R7 R9", "`P1_Unanimity`", ok],
        ["Drop R1 **and** R9", "R2 R5 R7", "`P9_NoSoloGrant`", ok],
        ["Drop R2", "R1 R5 R7 R9", "`P2_TwoSeatsCounted`", ok],
        ["Recusal removed from the mechanism", "R1 R2 R5 R7 R9", "`P3_AuthorNotCounted`", ok],
        ["Drop R5", "R1 R2 R7 R9", "`P5_AnchorNotApprover`", ok],
        ["Drop R7", "R1 R2 R5 R9", "`P7_BGNoAuthority`", ok],
    ]
    th1 = c.table(lx, y, t1cols, t1, size=13.5, draw=False)
    th2 = c.table(rx2, y, t2cols, t2, size=13.5, draw=False)
    c.table(lx, y, t1cols, t1, size=13.5, accent="grey")
    c.table(rx2, y, t2cols, t2, size=13.5, accent="teal")
    y += max(th1, th2) + 18

    f1 = [
        "**R1–R3 vacuous against ADR-0024 as written**: its snippet hard-coded the values. Parametricity, shown.",
        "**R4 withdrawn**: non-vacuous only if issued rules could make a timeout a grant.",
        "[[red|Drop R2 → promotes with zero votes.]] A havoc issuance sets an empty roster with "
        "`minGrant = 0`; unanimity over ∅ is vacuously true.",
        "**R5, R7** non-vacuous in every variant: roster membership and break-glass scope are genuinely issued.",
        "**Smallest satisfying model: four humans.** A property of the model (custody (1, 0) for the anchor), not "
        "a headcount; the archetype figure is five (R2's two seats + A-0025's three key-holders, disjoint by R5).",
    ]
    f2 = [
        "**R9 is a conditional entry**: every rule set it excludes (`quorum` 0 or 1) R1 already excludes; its "
        "independence is a separate ASSUME relative to a floor without R1.",
        "**Withdrawing R3 is safe**: with recusal removed at both sites the author self-grants and P3 fails.",
        "[[red|Four humans were too few to check R1.]] R5 removes the key-holder, recusal the author: two "
        "counted seats, and k ≥ 2 over two seats **is** unanimity, so the drop-R1 mutation held vacuously. "
        "**Five humans fix it**: a threshold mechanism needs at least three counted seats.",
        "**R2's empty-roster result survives** the change to thresholds.",
        "Verdict: every entry non-vacuous (R9 conditionally), promotion reachable, all six properties hold.",
    ]
    fh = max(c.card(0, 0, hw, "Findings, 09.15 (ADR-0026 §6)", f1, draw=False),
             c.card(0, 0, hw, "Findings, 09.23 (ADR-0026 §7)", f2, draw=False))
    c.card(lx, y, hw, "Findings, 09.15 (ADR-0026 §6)", f1, accent="grey", h=fh, size=14)
    c.card(rx2, y, hw, "Findings, 09.23 (ADR-0026 §7)", f2, accent="teal", h=fh, size=14)
    y += fh + 30
    pr = [
        "`spec/RulesFloorNV_rev5_proof.tla` (`8ecd73b3451018c5`) extends the frozen rev 5 module without editing it "
        "and proves, for every behaviour and every floor subset (`Active ⊆ AllEntries`): **P1** with R1 in force, "
        "**P2** with R2, **P3** with recusal, **P5** with R5, **P7** with R7, and **P9** with R2 and either R1 or R9. "
        "262 obligations, every one proved, by the prover T-0045-31 (ADR-0046); results "
        "`RulesFloorNV_rev5-proof-results-2026.10.02.txt` (`131804673137f4fd`).",
        "The module's three `ASSUME`s (genesis satisfies the floor; each entry independently droppable) were not "
        "premises the prover could use; each is now a **lemma proved from the definitions, with witness records** "
        "(G8 §3, result 4).",
        "P9's hypothesis corrected the binding table: it rests on **R2 and (R1 or R9)**, so dropping R2 breaks it too "
        "(ADR-0046 §5). The TLC row above, drop R1 and R9, is one of the two ways.",
        "ADR-0026 §6 and §7's \"non-vacuity and discrimination, not proof\" stands of the TLC runs and no longer of "
        "the properties. **The dropped-entry rows stay with TLC**: that a mutation reaches a bad state is an "
        "existential claim (ADR-0046 §2). The rerun with A2.2 and A2.3 is still owed (item 39, as at G9).",
        "[[red|This proof does not certify]] (ADR-0046 A1; G10 §2.9): of 262 obligations, 165 trivial, 84 by SMT "
        "with a proof `ethos` accepted, 7 LS4 steps no checker confirms, and **Isabelle rejected one of Zenon's "
        "proofs** (obligation 55). It is one of the three of twenty-two modules that do not certify; restructuring "
        "them is deferred by the custodian (item 74). Proved is not certified, and certified is not verified.",
    ]
    ph = c.card(X0, y, W, "Since 2026.10.02: the six properties are proved (ADR-0026 B25; ADR-0046 §4)", pr,
                accent="teal", size=14, status="accepted", status_extra="ADR-0046 · C2, C4 · B25")
    y += ph + 30
    sw2 = (W - 30) / 2
    s1 = [
        "`spec/BreakGlass_A1.tla` (`b586a6afa4fd5136`) succeeds `BreakGlass.tla` where it models X1, for ADR-0029 "
        "§5's fifth invariant under A2's reading of R7: `EmergencyNeverChangesAuthority` holds (8 rows).",
        "**With the kind's alphabet as decided, dropping R7 changes nothing**; a later change that gives the kind an "
        "authority act is refused at activation while R7 is in the floor, and breaks the invariant with R7 dropped.",
        "Proved, 45 obligations, nothing assumed, and **unlike its predecessor's proof it does not assume R7**. "
        "Certified (ADR-0052 §9, R5; G10 §3).",
    ]
    s2 = [
        "`spec/NonComposition_A1.tla` (`d1e9113480d016bb`) restates ADR-0013 §4's NC-1 and NC-2 with an activation's "
        "record as the F5 record and a round that ends (14 rows).",
        "Both hold; the predecessor's two mutations each break both; **a third breaks both: an activation's record "
        "kept only while its round is live**. Under X1 there was no \"after the round\" in which to lose it.",
        "Proved, 96 obligations, nothing assumed. Certified. `BreakGlass.tla` and `NonComposition.tla` stay frozen "
        "and are cited by digest (G10 §3).",
    ]
    sh2 = max(c.card(0, 0, sw2, "Successor: `BreakGlass_A1` (2026.10.05)", s1, size=14, draw=False),
              c.card(0, 0, sw2, "Successor: `NonComposition_A1` (2026.10.05)", s2, size=14, draw=False))
    c.card(X0, y, sw2, "Successor: `BreakGlass_A1` (2026.10.05)", s1, accent="teal", size=14, h=sh2)
    c.card(X0 + sw2 + 30, y, sw2, "Successor: `NonComposition_A1` (2026.10.05)", s2, accent="teal", size=14, h=sh2)
    y += sh2 + 30
    c.para(X0, y, W, "Both runs are precursors to the `RulesFloor` and `Promotion` bootstrap modules (ADR-0029 §5, "
           "invariant `PromotionMeetsIssuedQuorum` since A1), not substitutes; neither module is drafted yet. "
           "The `Anchor` module (`FloorPreserved`) was drafted and checked 2026.09.23 against the floor as ratified "
           "(R1, R2, R5, R6, R7, R9), and proved 2026.10.02 for every floor subset and epoch bound "
           "(`Anchor_proof.tla`, 40 obligations; ADR-0029 B25). Both still extend `RulesFloorBase.tla`, which is "
           "behind ADR-0026 A2 (G10 item 90).", 14.5, "muted")
    return c
