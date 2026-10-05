"""D4 — Privileged paths through the floor, and the forensic floor that survives them."""
from lib import Canvas, STATUS, text_width

ID, SLUG = "D4", "privileged-paths-forensic-floor"

W = 3200


def _nb(ln):
    """Keep leading indentation: the wrapper drops ordinary leading spaces."""
    n = len(ln) - len(ln.lstrip(" "))
    return " " * n + ln.lstrip(" ")


def code(c, x, y, w, lines, accent, dash=None):
    """A monospace block (Cedar or TLA+), drawn as a card with one line per body item."""
    return c.card(x, y, w, None, [f"`{_nb(ln)}`" if ln.strip() else " " for ln in lines], accent=accent,
                  bullets=False, size=13.5, lead=19, tint=False, pad=14, dash=dash)


def build():
    c = Canvas(ID, "Privileged paths through the floor, and the forensic floor that survives them",
               "One privileged path cannot be written as a subtraction, and it is the floor's one exception: erasure "
               "destroys authority-bearing evidence. Break-glass, which adds authority, was the second, X1, until "
               "Batch 34; X1 is retired and break-glass is an emergency seating (ADR-0052, provisional; drawn in D5). "
               "ADR-0013 writes the exception mechanism once, bounds the count (R6: one), and checks that break-glass "
               "and erasure do not compose into an unattributable effect. ADR-0028 names six classes of authority "
               "fact that no erasure may reach.",
               W, "ADR-0006; ADR-0009 09.12 acceptance, A1; ADR-0013 §1–§6, A1, B25; ADR-0026 §2, A2, W1 (A1, R8, "
               "withdrawn); ADR-0028 §1–§4, Bootstrap note, open obligations; ADR-0029 §5, A4; ADR-0030 §5, A3; "
               "ADR-0031 §2, A2; ADR-0032 §2; ADR-0039 A2; ADR-0041 §1, §3, A1, A2; ADR-0045 §6; ADR-0046 §4, A1; "
               "ADR-0050 §4; ADR-0052 Context, §1–§5, §8, §9, Findings; G10 §1, §1.2, §2.1, §2.2, §2.9, §3, §6, "
               "§7 items 8, 49, 90, 91, §8; ToO rev 14 §3.3, §4.3, §4.4; spec/NonComposition.tla (frozen) and "
               "spec/NonComposition_A1.tla, its rows, results, proof and certified results (2026.10.05); "
               "spec/BreakGlass_A1-results-2026.10.05.txt; floor/genesis-floor.cedar (X1, unchanged); "
               "floor/proposed/emergency-floor.cedar (X2, F-forensic-classes, R1-actuate-allowlisted, B10); "
               "mechanism/crates/topak-core/src/rules.rs (`EXCEPTION_BOUND`), state.rs; "
               "mechanism/GAPS-AND-ASSUMPTIONS.md I48, G10, G11")
    X0, X1 = c.x0, c.x1
    y = c.y

    # ---- status strip (wraps)
    c.text(X0, y + 15, "Status at G10", 15, "faint", bold=True)
    px0 = X0 + 140
    px = px0
    for lab, key, extra in [
            ("ADR-0013 exceptions", "accepted", "C1, C4"), ("ADR-0013 A1", "provisional", "with ADR-0052"),
            ("ADR-0006 erasure", "accepted", "C1, C4 via 0013"),
            ("ADR-0009 break-glass", "accepted", "C1, C4 via 0013"), ("ADR-0009 A1", "provisional", "C1, C3"),
            ("ADR-0052 emergency seating", "provisional", "C1, C3, C4"),
            ("ADR-0028 forensic floor", "accepted", "C1"), ("ADR-0030 floor entries", "accepted", "C1"),
            ("ADR-0026 rules floor", "accepted", "bootstrap set"), ("ADR-0026 A2 (R6, R7)", "provisional", ""),
            ("R8 (ADR-0026 A1)", "withdrawn", "W1"), ("X1-break-glass", "superseded", "retired"),
            ("floor in force", "genprov", "emergency stage")]:
        lw = text_width(lab, 13.5, True) + 8
        pw = text_width(STATUS[key][0] + (f" · {extra}" if extra else ""), 11.5, True) + 18
        if px + lw + pw > X1:
            px = px0
            y += 34
        c.text(px, y + 15, lab, 13.5, "ink", bold=True)
        px += lw
        px += c.status(px, y, key, extra) + 26
    y += 40
    y += c.para(X0, y, X1 - X0, "**Author-ratified, and in part provisional.** ADR-0013 and ADR-0028 were ratified in "
                "genesis on 2026.09.23 by the custodian alone; the first post-bootstrap quorum repays the independent "
                "reviewer that was given up. **X1's retirement is in force on a record subject to redesign**: ADR-0052 "
                "and the amendments that follow it (ADR-0009 A1, ADR-0013 A1, ADR-0026 A2, ADR-0041 A2) were ratified "
                "provisional on 2026.10.05 (Batch 34). If ADR-0052 is redesigned, break-glass has no settled form until "
                "the redesign is ratified (G10 §1.2, §8; ToO §3.3).", 14.5, "muted") + 20

    # ---- three columns: break-glass (retired) | shared model | erasure
    sw = 820
    gap = 70
    ew = (X1 - X0 - sw - 2 * gap) / 2
    bx, mx, ex = X0, X0 + ew + gap, X0 + ew + gap + sw + gap
    top = y
    pad = 22
    iw = ew - 2 * pad

    # break-glass column: X1 as it was, and what replaced it
    cy = top + 34
    h = c.card(bx + pad, cy, iw, "X1 · Break-glass as a floor exception (ADR-0009, 09.12 acceptance) · retired", [
        "Under a quorum of the break-glass roster, **a Run seat, an agent's included**, could `Actuate` a tool outside "
        "its allowlist and inside the issued envelope. The approval was scoped to (seat, epoch): **time-unbounded "
        "within an epoch** (ADR-0052 Context; D-0052-1).",
        "**Why it went** (ADR-0052 Findings): of what was asked of it, the stop is done by revocation, the addition by "
        "promotion, the record by the forensic floor; what was left was speed. It elevated the agent; it had no bound "
        "in time; and it was **the second carve-out** against the floor's minimality, as ADR-0009 itself noted.",
        "**ADR-0009 A1: the path stays, its home changes.** Still logged, quorum-witnessed and modeled; no longer a "
        "verified-object exception. What adds the authority is a seating, as for every principal.",
    ], accent="grey", size=14, status="superseded", status_extra="removed by ADR-0041 A2, Batch 34", tint=False)
    cy += h + 16
    t_rows_bg = [
        {"cells": ["", "**X1, as it was**", "**Since Batch 34 (ADR-0052, provisional)**"], "accent": "grey"},
        ["Actor", "Any Run seat the roster approved", "A **person** on a seat of kind `emergency`, every action "
                                                      "signed with the person's key (§1)"],
        ["Envelope", "`Actuate` of a tool in the issued `breakGlass.tools`, admitted by the X1 permit",
         "An **ordinary allowlist**, by default the domain's, computed at activation; admitted by "
         "`R1-actuate-allowlisted` (§2; ADR-0041 A2)"],
        ["Roster", "The break-glass roster and its quorum `k`", "Unchanged: the roster's quorum **activates** a "
                                                               "seating (ADR-0013 §1, A1)"],
        ["Ends", "Next epoch increment or a targeted revocation; no TTL. R8 drafted, never in force",
         "**With its round**: the round bound, the lease's `ttl`, an epoch increment or a revocation; no successor, "
         "no renewal. **R8 withdrawn** (ADR-0026 W1; ADR-0013 A1)"],
        ["Rules-floor bound", "**R7**: no break-glass grant may authorize `Issue`, `Vote` or promotion",
         "R7 read over an activation; with the kind's alphabet it has nothing to refuse (ADR-0026 A2)"],
        ["Observer", "`R3-observer-live` coupled break-glass (ADR-0039 B14)",
         "Not coupled: R3 is a forbid on `thinker` seats (ADR-0039 A2)"],
        ["Label forbids", "R5 to R7 applied to X1 (ADR-0041 A1)", "Apply to the person (ADR-0041 A2)"],
        ["Forensic class", "**F5**: the admit through `X1-break-glass` (`via_break_glass`)",
         "**F5**: the activation record; the admit is marked `emergency` (§5; I48)"],
        ["Exception count", "2 of R6's bound", "**1**: X1 retired (ADR-0013 A1 §3)"],
        {"cells": ["At the reference", "Followed until 2026.10.05",
                   "The linked floor has no X1; a `BreakGlassApprove` is refused at apply: \"X1 break-glass is "
                   "retired\" (I48; `state.rs`)"], "accent": "teal"},
    ]
    cy += c.table(bx + pad, cy, [("Row", iw * 0.18, {"bold": True}), ("Then", iw * 0.33), ("Now", iw * 0.49)],
                  t_rows_bg, size=13.5, accent="grey") + 16
    cy += c.para(bx + pad, cy, iw, "The permit as it stood. **Removed from the floor in force** "
                 "(`floor/proposed/emergency-floor.cedar`); still in `floor/genesis-floor.cedar`, which is unchanged "
                 "and is what the stages are built from (G10 §2.2).", 13.5, "muted") + 8
    cy += code(c, bx + pad, cy, iw, [
        '@id("X1-break-glass")   // retired',
        'permit (principal, action == Topak::Action::"Actuate", resource)',
        'when {',
        '  principal.domain == "run" &&',
        '  context.breakGlass.quorum &&',
        '  resource in context.breakGlass.tools',
        '};',
    ], "grey", dash="6 4") + 16
    h = c.card(bx + pad, cy, iw, "→ D5 · Break-glass is an emergency seating", [
        "The `emergency` seat kind and its alphabet; a seating prepared in advance and **activated by the roster's "
        "quorum** for one named person and one round; the domain's envelope; `Emergency.tla` and the `_A1` "
        "successors; the reference; and the exit from provisional (ADR-0052 §9; G10 item 92).",
    ], accent="blue", size=14, bullets=False, status="provisional", status_extra="ADR-0052")
    cy += h + 16
    bg_bot = cy

    # erasure column
    cy = top + 34
    h2 = c.card(ex + pad, cy, iw, "X2 · Erasure destroys evidence (ADR-0006): the floor's one exception", [
        "**An event**: consensus-ordered, modeled in TLA+, recorded in the log it modifies. Deletion cannot be an "
        "out-of-band operator action, because that is the capability to rewrite history.",
        "Its **authorization predicate lives in the verified object**, not in a bundle: erasure operates outside the "
        "refinement lattice (09.12 acceptance).",
        "Mechanism: deletion of sealed round topics and of plaintext-store entries; crypto-shredding rejected.",
    ], accent="red", size=14, status="accepted", status_extra="C1, C4 via 0013")
    cy += h2 + 16
    t_rows_er = [
        ["Envelope", "`Erase` of an `ArchiveRecord`, under an erasure quorum (`context.erasureQuorum`)"],
        ["Roster", "The erasure roster in the issued rules"],
        ["Non-composition", "NC-1 and NC-2, below, now against an emergency seating's activations"],
        ["Forensic denials", "`F-forensic-classes` forbids `Erase` of any record of class F1–F6: **bundles may only "
                             "narrow erasure further**; removing a class is a floor relaxation (ADR-0028 §2)"],
        ["Spec obligation", "A safety property that separates lawful erasure from history rewriting (ToO §4.3)"],
        ["Forensic class", "Every erasure event is itself **F6**, which is why demand type 5 is declined"],
        {"cells": ["At genesis", "**No erasure roster is issued** (ADR-0029 §5, ceremony step 5), so `erasureQuorum` is "
                                 "FALSE from epoch 0 and X2 admits nothing. The first roster comes after bootstrap under "
                                 "the two-key rule (ADR-0026 §4)"], "accent": "red"},
        {"cells": ["At the reference", "**Not built** (G11): nothing to exercise, matching the corpus position"],
         "accent": "red"},
    ]
    cy += c.table(ex + pad, cy, [("The floor entry", iw * 0.24, {"bold": True}), ("", iw * 0.76)], t_rows_er,
                  size=13.5, accent="red") + 16
    cy += c.para(ex + pad, cy, iw, "As linked by the reference, in the floor's emergency stage, which is "
                 "**genesis-provisional** (ADR-0030 A3; G10 §2.2):", 13.5, "muted") + 8
    cy += code(c, ex + pad, cy, iw, [
        '// Floor exceptions — ADR-0013 §2. Count: 1, bounded by ADR-0026 R6.',
        '@id("X2-erasure")',
        'permit (principal, action == Topak::Action::"Erase", resource)',
        'when { context.erasureQuorum };',
        '',
        '@id("F-forensic-classes")',
        'forbid (principal, action == Topak::Action::"Erase", resource)',
        'when { ["F1", "F2", "F3", "F4", "F5", "F6"].contains(resource.class) };',
    ], "brown") + 16
    cy += c.card(ex + pad, cy, iw, "Erasure beside an emergency seating", [
        "**Erasure stays a floor exception with its own roster**; the seating does not touch it (ADR-0052 §7).",
        "**An activation is an F5 record** (ADR-0052 §5): who approved, whom, on which seating, for which round, with "
        "the task's digest and label. Erasure does not remove it (ADR-0013 NC-2).",
        "**Its record must outlive its round.** That is a way to fail X1 did not have, since an X1 approval lasted "
        "until the epoch ended; `NonComposition_A1.tla`'s mutation **M3** shows it, and breaks both NC-1 and NC-2 "
        "(ADR-0052 R5).",
        "**A live emergency lease leaves the erasure envelope alone**: mutation **M2**, which lets it widen the "
        "envelope, breaks both.",
    ], accent="red", size=14) + 16
    er_bot = cy

    # shared model (centre)
    cy = top + 34
    h = c.card(mx + pad, cy, sw - 2 * pad, "One authorization model (ADR-0013 §1)", [
        "Every **privileged** grant (promotion, break-glass, erasure) is a **quorum decision on an anchor-issued "
        "roster**, bounded by the rules floor. **Break-glass stays under §1** and stops being an entry under §2 "
        "(A1): its quorum seats a person, where it used to approve a seat.",
        "**Privileged is load-bearing**: ordinary Run admits are grants too, decided against a bundle, not a roster "
        "(S6-13). An emergency seat's calls are such admits.",
    ], accent="blue", size=14)
    cy += h + 30
    # anchor -> rosters -> grants mini-diagram
    iw2 = sw - 2 * pad
    ah = c.card(mx + pad, cy, iw2, "The trust anchor issues rosters", [
        "`Issue`: an environment event validated by `Authentic` and the rules floor; forensic class **F4**."],
        accent="brown", size=13.5, bullets=False)
    cy += ah + 50
    rw = (iw2 - 2 * 18) / 3
    rosters = [("grant roster", "quorum → promotion (B5)", "blue", None, True),
               ("break-glass roster", "quorum → activation of an emergency seating (D5)", "blue", "4 3", True),
               ("erasure roster", "quorum → X2 · none at genesis", "red", "6 4", False)]
    rh = max(c.card(0, 0, rw, a, [b], accent=acc, draw=False, size=13.5, bullets=False)
             for a, b, acc, _, _ in rosters)
    for i, (a, b, acc, dsh, tnt) in enumerate(rosters):
        rx = mx + pad + i * (rw + 18)
        c.card(rx, cy, rw, a, [b], accent=acc, h=rh, size=13.5, bullets=False, dash=dsh, tint=tnt)
        c.arrow([(rx + rw / 2, cy - 50), (rx + rw / 2, cy)], "brown", dash="7 5" if i == 2 else None)
    c.line(mx + pad + rw / 2, cy - 50, mx + pad + 2 * (rw + 18) + rw / 2, cy - 50, "brown", sw=2)
    cy += rh + 34
    # R6 bound
    c.text(mx + pad, cy + 18, "Exception count, bounded by rules-floor R6", 17, "violet", bold=True)
    cy += 32
    slot_w = (iw2 - 20) / 2
    for i, (lab, sub) in enumerate([("X1 break-glass · retired", "ADR-0009; ADR-0041 A2"),
                                    ("X2 erasure", "ADR-0006")]):
        sx = mx + pad + i * (slot_w + 20)
        if i == 0:
            c.rect(sx, cy, slot_w, 64, "grey", tint=False, sw=2, dash="6 4")
            c.text(sx + slot_w / 2, cy + 28, lab, 16, "grey", anchor="middle", bold=True)
            c.line(sx + 24, cy + 22, sx + slot_w - 24, cy + 22, "grey", sw=1.6)
        else:
            c.rect(sx, cy, slot_w, 64, "violet", tint=True, sw=2)
            c.text(sx + slot_w / 2, cy + 28, lab, 16, "violet", anchor="middle", bold=True)
        c.text(sx + slot_w / 2, cy + 50, sub, 13, "muted", anchor="middle")
    cy += 64 + 12
    cy += c.para(mx + pad, cy, iw2, "**Count 1, erasure** (ADR-0013 A1 §3; ADR-0026 A2, provisional with ADR-0052). "
                 "Adding an exception is a floor relaxation: an anchor issuance and a promotion. Every carve-out works "
                 "against floor minimality, which is why the count is bounded, and **one fewer is the direction it "
                 "should move** (ToO §3.3). **Behind the records**: `RulesFloorBase.tla` still carries R6's bound of "
                 "two and `bgScope` (G10 §2.1, item 90), and the reference's rules check keeps `EXCEPTION_BOUND = 2` "
                 "(`rules.rs`).", 13.5, "ink") + 24
    h = c.card(mx + pad, cy, iw2, "Declared floor entries (ADR-0013 §2; ADR-0030 §5)", [
        "An exception is a named, versioned entry carrying **its action envelope, its roster reference and its "
        "non-composition obligations**. §2's three items now describe one entry, X2.",
        "Since ADR-0030 it is a **Cedar policy inside the floor**, as are the six forensic classes, so composition "
        "applies uniformly: a bundle can narrow the exception and cannot widen it.",
        "**The floor is genesis-provisional** (ADR-0030 A3): gated, pinned and enforced; ratified when the bootstrap "
        "reviewer establishes that it is fit (ADR-0029 A4).",
    ], accent="blue", size=14)
    cy += h + 16
    mid_bot = cy

    bot = max(bg_bot, er_bot, mid_bot) + 14
    c.region(bx, top, ew, bot - top, "Adds authority · no longer a floor exception (ADR-0052)", "grey", size=15)
    c.region(ex, top, ew, bot - top, "Destroys evidence · the one exception", "red", size=15)
    c.region(mx, top, sw, bot - top, "Inside the verified object: the policy floor (B4)", "blue", size=15)
    y = bot + 60

    # ---- rules floor table (full) | non-composition
    lw = 1460
    c.text(X0, y + 21, "The rules floor that bounds the anchor's issuances (ADR-0026 §2, as at G10 §2.1)", 21, "blue",
           bold=True)
    yy = y + 40
    cols = [("Entry", lw * 0.07, {"bold": True}), ("Rule", lw * 0.34), ("Record", lw * 0.15),
            ("State", lw * 0.44)]
    yy += c.table(X0, yy, cols, [
        ["R1", "`rules.quorum = \"all\"` (unanimity over counted grant seats)", "ADR-0024", "In force"],
        ["R2", "`rules.minGrant ≥ 2`", "ADR-0024", "In force"],
        {"cells": ["R3", "—", "—", "Withdrawn; ID reserved. Not the floor policy `R3-observer-live`, a different "
                                   "namespace"], "accent": "grey"},
        {"cells": ["R4", "—", "—", "Withdrawn; ID reserved"], "accent": "grey"},
        ["R5", "No key both in the anchor key set and on the promotion roster for the same artifact",
         "ADR-0025 / ADR-0024", "In force"],
        {"cells": ["R6", "Bound on floor-exception count. **The count it bounds is 1, erasure** (A2)",
                   "ADR-0013; ADR-0026 A2", "In force; A2 **provisional** with ADR-0052 (B34). `RulesFloorBase.tla` "
                   "and the reference's check still say two (G10 item 90; `rules.rs`)"], "accent": "violet"},
        {"cells": ["R7", "No break-glass grant may authorize `Issue`, `Vote`, or promotion; **read since A2 as** \"no "
                         "activation of an emergency seating grants a lease whose alphabet holds an authority act\"",
                   "ADR-0009 / ADR-0013; ADR-0026 A2",
                   "In force; A2 provisional. With the `emergency` kind's alphabet (`Consult`, `Actuate`, `Report`) R7 "
                   "has nothing left to refuse, and is kept for the day the kind changes: `BreakGlass_A1.tla` rows "
                   "`a1-nor7` (dropping R7 changes nothing) and `a1-kindr7` (with an authority act in the kind, "
                   "dropping R7 breaks the invariant)"], "accent": "blue"},
        {"cells": ["R8", "`0 < rules.breakGlass.ttl ≤ T_BG` (the break-glass TTL candidate)", "ADR-0026 A1",
                   "**Withdrawn 2026.10.04** (W1), never in force: a TTL needs trusted time, which the corpus refuses "
                   "(ADR-0032 §2; ADR-0045 §6). A grant ends with its round instead (ADR-0052 §3)"], "accent": "grey"},
        ["R9", "`rules.quorum = \"all\" ∨ rules.quorum ≥ 2`", "ADR-0024",
         "In force; a conditional entry, binding only once R1 is relaxed"],
    ], size=13.5, accent="blue") + 10
    c.para(X0, yy, lw, "The genesis rules floor is **R1, R2, R5, R6, R7, R9** (G10 §2.1). What the rules carry for "
           "break-glass is the roster and its quorum (A2). The ADR-0026 §6 rerun is still owed, and the non-vacuity "
           "artifacts, which model a break-glass grant, owe one for A2.", 13.5, "muted")

    rx = X0 + lw + 70
    rw_ = X1 - rx
    c.text(rx, y + 21, "Non-composition: NC-1 and NC-2 (ADR-0013 §4, §6, A1; ADR-0052 R5)", 21, "violet", bold=True)
    yy = y + 40
    yy += c.para(rx, yy, rw_, "Checked 2026.09.23 and proved 2026.10.02 in `NonComposition.tla`, which modeled X1, "
                 "**frozen and not edited**. **Restated for the seating** on 2026.10.05 in its successor, "
                 "`NonComposition_A1.tla` (`d1e9113480d016bb`): the activation's record is the F5 record, the round "
                 "ends, and another round is another activation with its own record.", 14) + 10
    half = (rw_ - 24) / 2
    hh = c.card(rx, yy, half, "NC-1", ["Break-glass chained with erasure **never yields an effect that is authorized, "
                                       "erased, and unattributable**."], accent="violet", size=14, bullets=False)
    c.card(rx + half + 24, yy, half, "NC-2", ["Erasure **never removes a record in a forensic-floor class**, under any "
                                              "composition with break-glass."], accent="violet", size=14,
           bullets=False, h=hh)
    yy += hh + 14
    yy += code(c, rx, yy, rw_, [
        "Attributable(e) == /\\ AdmitRec(e) \\in retained",
        "                   /\\ \\A r \\in Rounds : <<e, r>> \\in via => ActRecord(r) \\in retained",
        "NC1 == \\A e \\in admitted : (PayRec(e) \\notin retained) => Attributable(e)",
        "NC2 == \\A r \\in created : r.kind \\in ForensicKinds => r \\in retained",
    ], "violet") + 14
    yy += c.para(rx, yy, rw_, "**Mutations change the mechanism, never the property.** **M1** drops F1 from the erasure "
                 "envelope's denials, so the authority trail becomes erasable. **M2** lets a live emergency lease widen "
                 "the erasure envelope to every class. **M3, new with the seating**: an activation's record is kept "
                 "only while its round is live. Under X1 there was no \"after the round\" in which to lose it.", 14) + 12
    yy += c.table(rx, yy, [("Row", rw_ * 0.1, {"mono": True}), ("Check", rw_ * 0.38), ("Mut", rw_ * 0.07,
                                                                                         {"mono": True}),
                           ("Invariant", rw_ * 0.2, {"mono": True}), ("Result", rw_ * 0.13),
                           ("States (distinct)", rw_ * 0.12)], [
        {"cells": ["base", "Full mechanism", "none", "Safe", "[[green|holds]]", "320 (157)"], "accent": "green"},
        {"cells": ["nc1", "NC-1 alone", "none", "NC1", "[[green|holds]]", "320 (157)"], "accent": "green"},
        {"cells": ["nc2", "NC-2 alone", "none", "NC2", "[[green|holds]]", "320 (157)"], "accent": "green"},
        ["erased", "Reachability: erasure happens", "none", "NeverErased", "counterexample ✓", "37 (33)"],
        ["emeffect", "Reachability: an emergency seat's effect", "none", "NeverEmEffect", "counterexample ✓",
         "77 (52)"],
        {"cells": ["emerased", "Reachability: **the composition itself**, an effect under an activation is erased",
                   "none", "NeverEmErased", "counterexample ✓", "102 (76)"], "accent": "violet"},
        {"cells": ["after", "Reachability: **that erasure after the round has ended**, the case the seating adds",
                   "none", "NeverErasedAfterRound", "counterexample ✓", "140 (97)"], "accent": "violet"},
        ["second", "Reachability: a second activation, with a record of its own", "none", "NeverSecondActivation",
         "counterexample ✓", "71 (55)"],
        ["m1", "M1 → NC-1", "M1", "NC1", "counterexample ✓", "67 (60)"],
        ["m1x", "M1 → NC-2", "M1", "NC2", "counterexample ✓", "38 (35)"],
        ["m2", "M2 → NC-2", "M2", "NC2", "counterexample ✓", "65 (49)"],
        ["m2x", "M2 → NC-1", "M2", "NC1", "counterexample ✓", "160 (127)"],
        {"cells": ["m3", "M3 → NC-1 (new)", "M3", "NC1", "counterexample ✓", "218 (129)"], "accent": "red"},
        {"cells": ["m3x", "M3 → NC-2 (new)", "M3", "NC2", "counterexample ✓", "61 (53)"], "accent": "red"},
    ], size=13.5, accent="violet") + 10
    c.para(rx, yy, rw_, "`spec/NonComposition_A1-results-2026.10.05.txt` (`fd39b1ac98780e47`), TLC2 2.19, 14 rows, "
           "`MaxRound` = 2. Without the reachability rows NC-1 could hold because the two paths never meet. **Scope**: "
           "two effects, small constants; `ForensicKinds` = {F1, F5, F6}, three of six classes. **Proved** "
           "(`NonComposition_A1_proof.tla`, 96 obligations, nothing assumed) and **certified** (57 trivial, 36 by SMT "
           "with a proof the checker accepted, 3 LS4 steps, which no checker confirms; ADR-0046 A1). A certified "
           "proof is not a verified one, and nothing here is about the running reference. Neither successor found a "
           "fault in ADR-0052. Run by the author: evidence, not attestation.", 13.5, "muted")
    y = c.ymax + 70

    # ---- the forensic floor
    c.text(X0, y + 22, "The forensic floor (ADR-0028): authority facts survive erasure and break-glass", 22, "brown",
           bold=True)
    c.status(X0 + 860, y + 4, "accepted", "C1")
    y += 46
    fw = 1460
    fy = y
    y += c.table(X0, y, [("Class", fw * 0.07, {"bold": True}), ("Non-erasable for the declared horizon", fw * 0.36),
                         ("Source", fw * 0.15), ("In the NC model", fw * 0.14), ("Where it lives", fw * 0.28)], [
        ["F1", "Admit decisions (grants), with bundle version and epoch", "ADR-0015", "yes", "The `Admit` log entry"],
        ["F2", "Stop attribution: e-stop, lease-expiry eviction, `deny=all`", "Floor-rollout session",
         "same shape, omitted",
         "An operator's signed `EndRound`, `Revoke`, `FenceEpoch`: the signature is the attribution (ADR-0050 §4)"],
        ["F3", "Promotion votes", "ADR-0024", "same shape, omitted", "The vote's admit, not its topic emission"],
        ["F4", "Anchor issuances, including genesis (epoch 0)", "ADR-0025, ADR-0027", "same shape, omitted",
         "The `Issue` log entry"],
        {"cells": ["F5", "Break-glass invocations: **since ADR-0052, the activation of an emergency seating** and the "
                         "calls made under it", "ADR-0009; ADR-0052 §5", "yes, one record per activation",
                   "The activation record: approvers, person, seating, round, task digest and label, envelope, drill "
                   "mark; **no reason** (ADR-0052 §5; I48)"], "accent": "blue"},
        ["F6", "Erasure events themselves", "ADR-0006", "yes", "The erasure event (unbuilt)"],
    ], size=13.5, accent="brown") + 14
    for b in [
        "All six are **control-plane facts** (ADR-0004) and **boundary events** (ADR-0020). **No cognitive payload is in "
        "the floor**: prompts, reasoning and review commentary remain erasable.",
        "**No new primitive**: each class is a policy-floor denial on the erasure envelope, so bundles can only narrow "
        "erasure further; removing a class or shortening the horizon is a floor relaxation (§2).",
        "**Stop attribution is a feedback path, not just evidence**: in STPA terms the Observer is a controller, not a "
        "probe (ToO §4.4).",
        "Same monotone shape as the policy floor, in the other direction: the policy floor caps authority, the forensic "
        "floor guarantees retention; exceptions may preserve more, never less (Context, E1).",
    ]:
        y += c.para(X0 + 18, y, fw - 18, "• " + b, 14) + 6
    left_bot = y

    # legibility diagram
    rx = X0 + fw + 70
    rw_ = X1 - rx
    ly = fy - 10
    lh = c.card(rx, ly, rw_, "Legibility replaces immutability (ToO §4.4; ADR-0028 §3, §4)", [
        "\"Immutable\" lets a deployment claim conformance after erasing evidence. The archetype property: **every "
        "admitted boundary event remains readable by the declared audit authority for the declared horizon.**",
        "Archetype horizon: the lifetime of the rules-epoch chain. Audit authority: the anchor plus a declared "
        "external auditor role (still to define). Shortening either is a legibility degeneracy.",
    ], accent="brown", size=14)
    ly += lh + 40
    pw = (rw_ - 40) / 3
    big = c.card(rx + pw + 20, ly, pw, "The archetype log", ["The **maximum projection** each regime derives from."],
                 accent="blue", size=13.5, bullets=False)
    ly2 = ly + big + 60
    proj = [
        ("HIPAA-style", "green", ["Subtracts the **record**: erasure of payloads, never of F1–F6.",
                                  "Six-year retention and disclosure accounting are additive and not expressed."]),
        ("SCI-style", "green", ["Subtracts the **reader set**: compartmentation is not erasure while the audit "
                                "authority stays a reader.",
                                "Conformant except at spill remediation."]),
        ("Demand type 5", "red", ["\"Hide that a record ever existed\": **declined**. It conflicts with NC-2, since the "
                                  "erasure event is F6.",
                                  "A deployment needing it is outside the archetype's declared demands."]),
    ]
    ph = max(c.card(0, 0, pw, t, b, accent=a, draw=False, size=13.5) for t, a, b in proj)
    for i, (t, a, b) in enumerate(proj):
        px_ = rx + i * (pw + 20)
        c.card(px_, ly2, pw, t, b, accent=a, h=ph, size=13.5, tint=i != 2, dash="6 4" if i == 2 else None)
        sx = rx + pw + 20 + pw / 2
        c.arrow([(sx, ly + big), (sx, ly + big + 30), (px_ + pw / 2, ly + big + 30), (px_ + pw / 2, ly2)],
                a, dash="7 5" if i == 2 else None)
    right_bot = ly2 + ph
    y = max(left_bot, right_bot) + 50

    # ---- bottom row: genesis, horizon seam, break-glass bound
    w3 = (X1 - X0 - 2 * 30) / 3
    h1 = c.card(X0, y, w3, "Genesis issues no erasure roster", [
        "The roster is withheld by the ceremony itself (ADR-0029 §5, step 5), not by either record's status. Erasure is "
        "**disabled from epoch 0**: fail-closed, and it costs nothing, since there is nothing to erase yet.",
        "ADR-0006 therefore stands ratified with **no path to exercise it** until a roster is issued after bootstrap under "
        "the two-key rule, by which point ADR-0013 and ADR-0028 have been through confirmation.",
    ], accent="red", size=14, tint=False, dash="6 4")
    # horizon seam timeline card
    sx = X0 + w3 + 30
    hz = c.card(sx, y, w3, "The forensic horizon has a seam at re-genesis", [
        "The horizon is the lifetime of the rules-epoch chain, and re-genesis starts a new chain, which follows anchor loss "
        "or capture: **the authority record lapses exactly when it matters most**.",
        "That a successor inherits read access to its predecessor's forensic classes is a re-genesis migration obligation, "
        "**open**, to be settled before ADR-0028's confirmation (ToO §4.4). ADR-0003 A1 lets a successor tell its topics "
        "apart, and settles nothing else.",
    ], accent="amber", size=14, status="open")
    tx = sx + w3 + 30
    tb = ["**R8 is withdrawn** (ADR-0026 W1, 2026.10.04): a timed expiry needs trusted time (ADR-0032 §2). "
          "Item 8 is closed by the withdrawal, and item 49 decided: an emergency seat is not coupled (G10 §7).",
          "**The round is the time box** (ADR-0052 Finding 3): the activation's lease ends at the round bound `R`, at "
          "its `ttl` (at most `T_persona` on the local monotonic clock, ADR-0031 A2), at an epoch increment or at a "
          "targeted revocation, and has no successor and no renewal (ADR-0013 A1).",
          "The reference follows it since 2026.10.05: its old stand-in, an approval lapsing only at the next epoch, "
          "no longer exists there (`mechanism/` register rows G10, I48)."]
    hb = c.card(0, 0, w3, "A break-glass grant ends with its round", tb, draw=False, size=14, status="provisional")
    c.card(tx, y, w3, "A break-glass grant ends with its round", tb, accent="blue", size=14, status="provisional",
           status_extra="ADR-0052 §3; ADR-0013 A1", h=max(h1, hz, hb))
    # seam timeline drawn under the middle card
    ty = y + max(h1, hz, hb) + 60
    x0, x1 = sx + 20, sx + w3 - 20
    mid = (x0 + x1) / 2
    c.line(x0, ty, mid - 30, ty, "brown", sw=3)
    c.line(mid + 30, ty, x1, ty, "blue", sw=3)
    c.arrow([(x1 - 4, ty), (x1 + 14, ty)], "blue", sw=3)
    c.text(x0, ty - 14, "chain 1 · epochs 0…n · forensic horizon", 13.5, "brown", bold=True)
    c.text(x1, ty + 26, "chain 2 · epoch 0 · new horizon", 13.5, "blue", anchor="end", bold=True)
    c.rect(mid - 30, ty - 16, 60, 32, "red", tint=True, rx=6, sw=1.6)
    c.text(mid, ty + 5, "seam", 13.5, "red", anchor="middle", bold=True)
    c.text(mid, ty + 46, "anchor loss or capture → re-genesis; inherited read access: open", 13.5, "red",
           anchor="middle")

    ly = c.ymax + 40
    c.legend(c.x0, ly, [
        ("box", "red", "privileged path, gap"), ("box", "blue", "floor, authority, provisional record"),
        ("box", "violet", "TLA+ check, rules-floor bound"), ("box", "brown", "forensic floor, anchor"),
        ("box", "grey", "retired or withdrawn", "6 4"), ("box", "amber", "open"),
        ("arrow", "brown", "issues"), ("arrow", "red", "declined / not issued", "7 5"),
    ])
    return c
