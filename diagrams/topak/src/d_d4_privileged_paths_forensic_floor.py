"""D4 — Privileged paths through the floor, and the forensic floor that survives them."""
from lib import Canvas, text_width

ID, SLUG = "D4", "privileged-paths-forensic-floor"

W = 3200


def _nb(ln):
    """Keep leading indentation: the wrapper drops ordinary leading spaces."""
    n = len(ln) - len(ln.lstrip(" "))
    return "\u00a0" * n + ln.lstrip(" ")


def code(c, x, y, w, lines, accent):
    """A monospace block (Cedar or TLA+), drawn as a card with one line per body item."""
    return c.card(x, y, w, None, [f"`{_nb(ln)}`" if ln.strip() else " " for ln in lines], accent=accent,
                  bullets=False, size=13.5, lead=19, tint=False, pad=14)


def build():
    c = Canvas(ID, "Privileged paths through the floor, and the forensic floor that survives them",
               "Two paths cannot be written as subtractions: break-glass adds authority, erasure destroys "
               "authority-bearing evidence. ADR-0013 writes them once, as declared floor entries under one "
               "authorization model, bounds their number, and checks that they do not compose into an unattributable "
               "effect. ADR-0028 names six classes of authority fact that no erasure may reach.",
               W, "ADR-0006; ADR-0009; ADR-0013 §1–§6; ADR-0026 §2, A1 (R8, pending), B4; ADR-0028 §1–§4, Bootstrap note, "
               "open obligations; ADR-0029 §5; ADR-0030 §5; ADR-0039 §2; ADR-0041 §2, §3; ToO rev 11 §3.3, §4.1, §4.4; "
               "G7 §1.1, §2.1, §4, §7 items 8, 10, 49; spec/NonComposition.tla; spec/NonComposition-results-2026.09.23.txt; "
               "floor/genesis-floor.cedar (X1, X2, F-forensic-classes, R3-observer-live); mechanism/crates/topak-core/src/"
               "rules.rs, state.rs, admit.rs (`via_break_glass`); scripts/dev-init.sh; GAPS-AND-ASSUMPTIONS I9, G10, G11")
    X0, X1 = c.x0, c.x1
    y = c.y

    # ---- status strip
    c.text(X0, y + 15, "Status at G7", 15, "faint", bold=True)
    px = X0 + 130
    for lab, key, extra in [("ADR-0013 exceptions", "accepted", "C1, C4"), ("ADR-0006 erasure", "accepted", "C1, C4 via 0013"),
                            ("ADR-0009 break-glass", "accepted", "C1, C4 via 0013"),
                            ("ADR-0028 forensic floor", "accepted", "C1"), ("ADR-0030 floor entries", "accepted", "C1"),
                            ("ADR-0026 rules floor", "accepted", ""), ("R8 (ADR-0026 A1)", "draft", "pending"),
                            ("genesis floor text", "draft", "")]:
        c.text(px, y + 15, lab, 13.5, "ink", bold=True)
        px += text_width(lab, 13.5, True) + 8
        px += c.status(px, y, key, extra) + 26
    y += 40
    c.para(X0, y, X1 - X0, "**Author-ratified.** ADR-0013 and ADR-0028 were ratified in genesis on 2026.09.23 by the "
           "custodian alone; the move to genesis gave up the independent reviewer the post-bootstrap phase would have "
           "supplied, and the first post-bootstrap quorum repays it (ToO §3.3; ADR-0013 open obligations). Anything "
           "citing these guarantees says \"author-ratified\".", 14.5, "muted")
    y += 64

    # ---- three columns: break-glass | shared model | erasure
    sw = 820
    gap = 70
    ew = (X1 - X0 - sw - 2 * gap) / 2
    bx, mx, ex = X0, X0 + ew + gap, X0 + ew + gap + sw + gap
    top = y
    pad = 22
    iw = ew - 2 * pad

    # break-glass column
    cy = top + 34
    h = c.card(bx + pad, cy, iw, "X1 · Break-glass adds authority (ADR-0009)", [
        "An explicit override path, **logged, quorum-witnessed and modeled**, on the control/data plane split rather "
        "than forbidden. Because it adds authority it cannot be a refining bundle: it is a verified-object exception, "
        "changing at deploy cadence.",
        "Must never justify data-plane autonomy in irreversible domains (ADR-0009).",
        "Grants authority **within** the rules in force and cannot alter them, so it is an effect, not a third kind of "
        "authority change (ADR-0015 R2).",
    ], accent="red", size=14, status="accepted", status_extra="C1, C4 via 0013")
    cy += h + 16
    t_rows_bg = [
        ["Envelope", "`Actuate` only, by a Run seat, of a tool in the issued `breakGlass.tools`; never `Consult`, "
                     "`Report`, `Vote`, `Submit` or `Erase` (ADR-0041 §3)"],
        ["Roster", "The break-glass roster in the issued rules, with its quorum `k` (dev rules: two keys, `k` = 2)"],
        ["Non-composition", "NC-1 and NC-2, below"],
        ["Rules-floor bound", "**R7**: no break-glass grant may authorize `Issue`, `Vote` or promotion"],
        ["Bundle", "May **narrow** it, never widen it (ADR-0030 §5): a bad bundle can disable break-glass, a liveness "
                   "cost"],
        ["Observer coupling", "Floor policy `R3-observer-live` applies to break-glass too: a dead, partitioned or starved "
                              "cell Observer stops its Thinker's break-glass (ADR-0039 §2). Break-glass under a dead "
                              "Observer is open (G7 item 49)"],
        ["Forensic class", "Each invocation is **F5**; the reference flags an admit through `X1-break-glass` without "
                           "`R1-actuate-allowlisted` (`via_break_glass`)"],
        {"cells": ["Ends", "**No TTL.** R8 is drafted and pending (ADR-0026 A1, four conditions unmet). At the reference, "
                           "approvals are scoped to (seat, epoch) and lapse at the next epoch increment or a targeted "
                           "revocation of the seat (I9; G10)"], "accent": "red"},
    ]
    cy += c.table(bx + pad, cy, [("The floor entry", iw * 0.24, {"bold": True}), ("", iw * 0.76)], t_rows_bg,
                  size=13.5, accent="red") + 16
    cy += code(c, bx + pad, cy, iw, [
        '@id("X1-break-glass")',
        'permit (principal, action == Topak::Action::"Actuate", resource)',
        'when {',
        '  principal.domain == "run" &&',
        '  context.breakGlass.quorum &&',
        '  resource in context.breakGlass.tools',
        '};',
    ], "red") + 16
    bg_bot = cy

    # erasure column
    cy = top + 34
    h2 = c.card(ex + pad, cy, iw, "X2 · Erasure destroys evidence (ADR-0006)", [
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
        ["Non-composition", "NC-1 and NC-2, below"],
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
    cy += code(c, ex + pad, cy, iw, [
        '@id("X2-erasure")',
        'permit (principal, action == Topak::Action::"Erase", resource)',
        'when { context.erasureQuorum };',
        '',
        '@id("F-forensic-classes")',
        'forbid (principal, action == Topak::Action::"Erase", resource)',
        'when { ["F1", "F2", "F3", "F4", "F5", "F6"].contains(resource.class) };',
    ], "brown") + 16
    er_bot = cy

    # shared model (centre)
    cy = top + 34
    h = c.card(mx + pad, cy, sw - 2 * pad, "One authorization model (ADR-0013 §1)", [
        "Every **privileged** grant (promotion, break-glass, erasure) is a **quorum decision on an anchor-issued "
        "roster**, bounded by the rules floor. Erasure and break-glass differ only in roster and envelope.",
        "**Privileged is load-bearing**: ordinary Run admits are grants too, decided against a bundle, not a roster "
        "(S6-13).",
    ], accent="blue", size=14)
    cy += h + 30
    # anchor -> rosters -> grants mini-diagram
    iw2 = sw - 2 * pad
    ah = c.card(mx + pad, cy, iw2, "The trust anchor issues rosters", [
        "`Issue`: an environment event validated by `Authentic` and the rules floor; forensic class **F4**."],
        accent="brown", size=13.5, bullets=False)
    cy += ah + 50
    rw = (iw2 - 2 * 18) / 3
    rosters = [("grant roster", "promotion", "blue"), ("break-glass roster", "X1", "red"),
               ("erasure roster", "X2 · none at genesis", "red")]
    rh = max(c.card(0, 0, rw, a, [f"quorum → {b}"], accent=acc, draw=False, size=13.5, bullets=False)
             for a, b, acc in rosters)
    for i, (a, b, acc) in enumerate(rosters):
        rx = mx + pad + i * (rw + 18)
        c.card(rx, cy, rw, a, [f"quorum → {b}"], accent=acc, h=rh, size=13.5, bullets=False,
               dash="6 4" if i == 2 else None, tint=i != 2)
        c.arrow([(rx + rw / 2, cy - 50), (rx + rw / 2, cy)], "brown", dash="7 5" if i == 2 else None)
    c.line(mx + pad + rw / 2, cy - 50, mx + pad + 2 * (rw + 18) + rw / 2, cy - 50, "brown", sw=2)
    cy += rh + 34
    # R6 bound
    c.text(mx + pad, cy + 18, "Exception count, bounded by rules-floor R6", 17, "violet", bold=True)
    cy += 32
    slot_w = (iw2 - 20) / 2
    for i, (lab, sub) in enumerate([("X1 break-glass", "ADR-0009"), ("X2 erasure", "ADR-0006")]):
        sx = mx + pad + i * (slot_w + 20)
        c.rect(sx, cy, slot_w, 64, "violet", tint=True, sw=2)
        c.text(sx + slot_w / 2, cy + 28, lab, 16, "violet", anchor="middle", bold=True)
        c.text(sx + slot_w / 2, cy + 50, sub, 13, "muted", anchor="middle")
    cy += 64 + 12
    cy += c.para(mx + pad, cy, iw2, "**Current count 2; bound 2** (R6 effective 2026.09.23 with ADR-0013; the "
                 "reference refuses rules with more, `rules.rs`). Adding a third is a floor relaxation: an anchor "
                 "issuance and a promotion. Every carve-out works against floor minimality, which is why the count is "
                 "bounded. Open: confirm R6 = 2 is not already at its bound for known future exceptions.",
                 13.5, "ink") + 24
    h = c.card(mx + pad, cy, iw2, "Declared floor entries (ADR-0013 §2; ADR-0030 §5)", [
        "Each exception is a named, versioned entry carrying **its action envelope, its roster reference and its "
        "non-composition obligations**.",
        "Since ADR-0030 they are **Cedar policies inside the floor**, as are the six forensic classes, so composition "
        "applies uniformly: a bundle can narrow either exception and widen neither.",
    ], accent="blue", size=14)
    cy += h + 16
    mid_bot = cy

    bot = max(bg_bot, er_bot, mid_bot) + 14
    c.region(bx, top, ew, bot - top, "Adds authority", "red", size=15)
    c.region(ex, top, ew, bot - top, "Destroys evidence", "red", size=15)
    c.region(mx, top, sw, bot - top, "Inside the verified object: the policy floor (B4)", "blue", size=15)
    y = bot + 60

    # ---- rules floor table (full) | non-composition
    lw = 1460
    c.text(X0, y + 21, "The rules floor that bounds the anchor's issuances (ADR-0026 §2, as at G7 §2.1)", 21, "blue",
           bold=True)
    yy = y + 40
    cols = [("Entry", lw * 0.07, {"bold": True}), ("Rule", lw * 0.36), ("Record", lw * 0.17),
            ("State", lw * 0.4)]
    yy += c.table(X0, yy, cols, [
        ["R1", "`rules.quorum = \"all\"` (unanimity over counted grant seats)", "ADR-0024", "In force"],
        ["R2", "`rules.minGrant ≥ 2`", "ADR-0024", "In force"],
        {"cells": ["R3", "—", "—", "Withdrawn; ID reserved. Not the floor policy `R3-observer-live`, a different "
                                   "namespace"], "accent": "grey"},
        {"cells": ["R4", "—", "—", "Withdrawn; ID reserved"], "accent": "grey"},
        ["R5", "No key both in the anchor key set and on the promotion roster for the same artifact",
         "ADR-0025 / ADR-0024", "In force"],
        {"cells": ["R6", "Bound on floor-exception count (current count: 2)", "ADR-0013",
                   "In force since 2026.09.23 (B4); checked by the reference at startup"], "accent": "violet"},
        {"cells": ["R7", "No break-glass grant may authorize `Issue`, `Vote`, or promotion", "ADR-0009 / ADR-0013",
                   "In force; discharges break-glass × issuance and × promotion; the reference checks the issued "
                   "`actions`"], "accent": "red"},
        {"cells": ["R8", "`0 < rules.breakGlass.ttl ≤ T_BG`: every break-glass rule carries a finite grant TTL",
                   "ADR-0026 A1", "**Drafted 2026.09.24, pending.** Unmet: a companion mechanism clause (C1); `T_BG` "
                   "derived from `D`; the clock question (ADR-0032 §2); a non-vacuity run with `P8_BreakGlassEnds`. "
                   "Not implemented"], "accent": "amber"},
        ["R9", "`rules.quorum = \"all\" ∨ rules.quorum ≥ 2`", "ADR-0024",
         "In force; a conditional entry, binding only once R1 is relaxed"],
    ], size=13.5, accent="blue") + 10
    c.para(X0, yy, lw, "The genesis rules floor is **R1, R2, R5, R6, R7, R9**. The ADR-0026 §6 rerun with A2.2 and A2.3 "
           "is still owed (G7 item 39).", 13.5, "muted")

    rx = X0 + lw + 70
    rw_ = X1 - rx
    c.text(rx, y + 21, "Non-composition: NC-1 and NC-2, checked 2026.09.23 (ADR-0013 §4, §6)", 21, "violet", bold=True)
    yy = y + 40
    half = (rw_ - 24) / 2
    hh = c.card(rx, yy, half, "NC-1", ["Break-glass chained with erasure **never yields an effect that is authorized, "
                                       "erased, and unattributable**."], accent="violet", size=14, bullets=False)
    c.card(rx + half + 24, yy, half, "NC-2", ["Erasure **never removes a record in a forensic-floor class**, under any "
                                              "composition with break-glass."], accent="violet", size=14,
           bullets=False, h=hh)
    yy += hh + 14
    yy += code(c, rx, yy, rw_, [
        "Attributable(e) == /\\ AdmitRec(e) \\in retained",
        "                   /\\ (e \\in viaBG => BGRecord \\in retained)",
        "NC1 == \\A e \\in admitted : (PayRec(e) \\notin retained) => Attributable(e)",
        "NC2 == \\A r \\in created : r.kind \\in ForensicKinds => r \\in retained",
    ], "violet") + 14
    yy += c.para(rx, yy, rw_, "**Mutations change the mechanism, never the property.** **M1** drops F1 from the erasure "
                 "envelope's denials, so the authority trail becomes erasable. **M2** lets a break-glass grant widen the "
                 "erasure envelope instead of only narrowing it.", 14) + 12
    yy += c.table(rx, yy, [("Check", rw_ * 0.44), ("Mut", rw_ * 0.08, {"mono": True}),
                           ("Invariant", rw_ * 0.17, {"mono": True}), ("Result", rw_ * 0.15),
                           ("States (distinct)", rw_ * 0.16)], [
        {"cells": ["Full mechanism", "none", "Safe", "[[green|holds]]", "57 (34)"], "accent": "green"},
        ["Reachability: erasure happens", "none", "NeverErased", "counterexample ✓", "14 (14)"],
        ["Reachability: break-glass authorizes an effect", "none", "NeverBGEffect", "counterexample ✓", "35 (23)"],
        {"cells": ["Reachability: **the composition itself**, a break-glass-authorized effect is erased", "none",
                   "NeverBGErased", "counterexample ✓", "43 (30)"], "accent": "violet"},
        ["M1 → NC-1", "M1", "NC1", "counterexample ✓", "86 (61)"],
        ["M1 → NC-2", "M1", "NC2", "counterexample ✓", "14 (14)"],
        ["M2 → NC-2", "M2", "NC2", "counterexample ✓", "32 (27)"],
        ["M2 → NC-1", "M2", "NC1", "counterexample ✓", "77 (54)"],
    ], size=13.5, accent="violet") + 10
    c.para(rx, yy, rw_, "`NonComposition.tla` (`119f9a7e878f8929`), TLC2 2.19. The third witness matters: without it NC-1 "
           "could hold because the two paths never meet. **Scope**: two effects, one break-glass invocation, small "
           "constants; `ForensicKinds` = {F1, F5, F6}, three of six classes. Non-composition and reachability, **not "
           "proof**, run by the author: evidence, not attestation.", 13.5, "muted")
    y = c.ymax + 70

    # ---- the forensic floor
    c.text(X0, y + 22, "The forensic floor (ADR-0028): authority facts survive erasure and break-glass", 22, "brown",
           bold=True)
    c.status(X0 + 860, y + 4, "accepted", "C1")
    y += 46
    fw = 1460
    fy = y
    y += c.table(X0, y, [("Class", fw * 0.07, {"bold": True}), ("Non-erasable for the declared horizon", fw * 0.4),
                         ("Source", fw * 0.18), ("In the NC model", fw * 0.13), ("Where it lives", fw * 0.22)], [
        ["F1", "Admit decisions (grants), with bundle version and epoch", "ADR-0015", "yes", "The `Admit` log entry"],
        ["F2", "Stop attribution: e-stop, lease-expiry eviction, `deny=all`", "Floor-rollout session", "same shape, omitted",
         "`EndRound`, `Revoke`, `EpochIncrement`"],
        ["F3", "Promotion votes", "ADR-0024", "same shape, omitted", "The vote's admit, not its topic emission"],
        ["F4", "Anchor issuances, including genesis (epoch 0)", "ADR-0025, ADR-0027", "same shape, omitted",
         "The `Issue` log entry"],
        ["F5", "Break-glass invocations", "ADR-0009", "yes", "The admit through `X1-break-glass`"],
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

    # ---- bottom row: genesis, horizon seam, break-glass TTL
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
        "**open** (G7 item 10), to be settled before ADR-0028's confirmation. ADR-0003 A1 lets a successor tell its topics "
        "apart, and settles nothing else.",
    ], accent="amber", size=14, status="open")
    tx = sx + w3 + 30
    c.card(tx, y, w3, "Break-glass has no TTL", [
        "No clause ends an approved break-glass grant: the gap R8 would close (ADR-0026 A1 note; ToO rev 6 §10).",
        "R8 is vacuous until the mechanism reads the TTL; its companion clause would touch a privileged path and carry C1; "
        "`T_BG` has no archetype value; ADR-0032 §2 puts a break-glass TTL in the trusted-time row.",
        "Reference: approvals lapse at the next epoch increment, so break-glass is **time-unbounded within an epoch** (G10).",
    ], accent="amber", size=14, status="draft", status_extra="R8 pending", h=max(h1, hz))
    # seam timeline drawn under the middle card
    ty = y + max(h1, hz) + 60
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
        ("box", "red", "privileged path, gap"), ("box", "blue", "floor, authority"), ("box", "violet", "TLA+ check"),
        ("box", "brown", "forensic floor, anchor"), ("box", "amber", "pending, open"),
        ("arrow", "brown", "issues"), ("arrow", "red", "declined / not issued", "7 5"),
    ])
    return c
