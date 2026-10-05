"""E3 — The correlator's detection function: five folds over facts, a judgment tier, a store keyed by round (ADR-0051,
Proposed, not built)."""
import re

import lib
from lib import Canvas, text_width

ID, SLUG = "E3", "correlator-folds"

W = 3200


def _boldfix(s):
    """Split a **bold** span that holds `code` into bold runs around the code (lib cannot nest them)."""
    segs = s.split("**")
    if len(segs) % 2 == 0:
        return s
    out = []
    for k, seg in enumerate(segs):
        if k % 2 == 0:
            out.append(seg)
        elif "`" in seg:
            parts = re.split(r"(`[^`]+`)", seg)
            out.append("".join(p if p.startswith("`") else (f"**{p}**" if p.strip() else p) for p in parts))
        else:
            out.append(f"**{seg}**")
    return "".join(out)


def build():
    orig = lib.parse
    lib.parse = lambda s: orig(_boldfix(s))
    try:
        return _build()
    finally:
        lib.parse = orig


def _row(c, x, y, w, cards, gap=24, size=14):
    """Cards of equal height side by side. cards: (title, body, accent, status, extra, kw). Returns height."""
    n = len(cards)
    cw = (w - gap * (n - 1)) / n
    hs = [c.card(0, 0, cw, t, b, accent=a, status=st, status_extra=sx, draw=False, size=size, **kw)
          for t, b, a, st, sx, kw in cards]
    hh = max(hs)
    for i, (t, b, a, st, sx, kw) in enumerate(cards):
        c.card(x + i * (cw + gap), y, cw, t, b, accent=a, status=st, status_extra=sx, h=hh, size=size, **kw)
    return hh


def _build():
    c = Canvas(ID, "The correlator's detection function: five folds over facts, a judgment tier, and a store that never "
                   "outlives its sources",
               "ADR-0051 (Proposed 2026.10.04, at R3) answers ADR-0038's finding 1, \"the correlator has inputs but no "
               "function\". It splits the function in two: five correlations, each a named fold over facts with a fixed "
               "definition that a second reader can recompute, and a judgment tier over payloads that no record can "
               "specify. Every finding only subtracts, takes effect by any-of, and waits on nothing: no admit and no "
               "promotion waits on a correlator. **Everything drawn here is Proposed and not built at the reference**, "
               "where the correlator computes nothing (D-0051-1); `spec/Correlator.tla` is proved and certified, which "
               "is a claim about the module and not about any running correlator (G10 §7 items 43, 97).",
               W, "ADR-0051 (Proposed; R1–R3: Context, §1–§10, Options, Consequences, Findings 1–8, Open obligations, "
               "History); ADR-0038 §1–§6, findings 1–3; ADR-0039 §1, §4, §5; ADR-0042 §2, §3, A1, A2; ADR-0043 §4, A1; "
               "ADR-0047 §4, §5, §9, F1–F3 (floor `R5`–`R7`, ADR-0041 A1); ADR-0048 §2; ADR-0049 §4; ADR-0035 §6 "
               "(Proposed); ADR-0037 §3; ADR-0015; ADR-0003 A2; ADR-0005 §2; ADR-0006; ADR-0007; ADR-0046 A1; "
               "spec/Correlator.tla, spec/Correlator-results-2026.10.04.txt (22 rows), spec/Correlator_proof.tla, "
               "spec/Correlator-proof-results-2026.10.04.txt, spec/Correlator-proof-cert-results-2026.10.04.txt, "
               "spec/proof-certification.md §8, §9; mechanism/crates/topak-node/src/mechanism.rs (`record_denial`); "
               "decisions/ searched for ADR-0051's dependent entries; ToO rev 14 §5.1, §5.4; G10 §1.1, §2.9, §7 items "
               "22, 43–48, 97, §8")
    X0, X1 = c.x0, c.x1
    Wd = X1 - X0
    y = c.y

    # ---- status strip
    c.text(X0, y + 15, "Status", 15, "faint", bold=True)
    px = X0 + 80
    for lab, key, extra in [("ADR-0051", "proposed", "C4 on ratification · R3"),
                            ("the correlator's folds at the reference", "notbuilt", "D-0051-1 is the reference today"),
                            ("ADR-0038", "accepted", "C3, C4"), ("ADR-0039", "accepted", "C4"),
                            ("ADR-0047, ADR-0049", "accepted", "C4 · Batch 34"),
                            ("ADR-0035 §6", "proposed", "")]:
        c.text(px, y + 15, lab, 13.5, "ink", bold=True)
        px += text_width(lab, 13.5, True) + 8
        px += c.status(px, y, key, extra) + 24
    y += 40
    c.para(X0, y, Wd, "**Checked, proved, certified, of the module only**: `Correlator.tla` 22 TLC rows (eight "
           "properties hold, eight mutations break what they must, seven witnesses reached); `Correlator_proof.tla` 455 "
           "obligations proved with no assumption on the constants; certified, 445 by normalization or a checked proof "
           "and 10 temporal steps on LS4, which no checker confirms. **One author, one day, and no options discussion** "
           "(Provenance note; Consequences).", 14, "muted")
    y += 60

    # ======================================================================== A. the function, as a flow
    y += c.heading(X0, y, "What it folds over, what it computes, what it reports, and what a report does", "amber", 21)
    top = y + 20
    gap = 110
    cw = (Wd - 2 * gap) / 3
    xa, xb, xc = X0, X0 + cw + gap, X0 + 2 * (cw + gap)

    # -- inputs
    iy = top + 40
    ins = [
        ("The log: facts", "teal", [
            "Admits with their log index; a `Consult` admit with its reference, **label and delivery mode** "
            "(ADR-0042 A1); grants, renewals, revocations and seals.",
            "Cell Observers' findings as control-plane facts (ADR-0038 §3). **A finding must cite the records it is "
            "about** (§3): an obligation on every `observer` seat, owed to ADR-0043 §4."]),
        ("Round-topic envelopes: facts", "amber", [
            "The `Actuate` record: `tool`, input and result digests, `seatKind`, and `inputLabels`, `resultLabel`, "
            "`delivery`, `clearSet` (ADR-0042 §3, A1, A2).",
            "The opening record's tool-list digest (ADR-0048 §2); heartbeats with their watermarks (ADR-0039 §1).",
            "**Denial records placed by `at`**, the log index the deciding replica had applied, and `decided_by` "
            "(§5). The reference writes both (`record_denial`); no record requires them (finding 3)."]),
        ("Bundle data and the Reader", "grey", [
            "An entry's `channel.target`: checked for a Wasm tool, **a claim for a native one** (ADR-0049 §4).",
            "The **correlation table**: each of the five `on` with its parameters, or `off`; a bundle whose table omits "
            "a name does not load (§2).",
            "The Reader's distributional distance per round, for a Persona declaring `topk_logprobs` (ADR-0037 §3)."]),
        ("Payloads, at the archetype only", "pink", [
            "Read under the ACL (ADR-0038 §3). Only the judgment tier uses them. **A facts-only correlator computes all "
            "five correlations** and gives up §4 and nothing in §2 (§1; finding 1)."]),
    ]
    for t, a, b in ins:
        h = c.card(xa + 20, iy, cw - 40, t, b, accent=a, size=13.5, tint=a != "pink",
                   dash="6 4" if a == "pink" else None)
        iy += h + 18
    in_bot = iy + 6
    c.region(xa, top, cw, in_bot - top, "Inputs: what the correlator receives under ADR-0038 §3", "teal", dash=None,
             size=14)

    # -- the correlator
    my = top + 40
    hdr = c.card(xb + 20, my, cw - 40, "An `observer` seat in no cell (ADR-0038 §1)", [
        "**The window is the correlator's round**, leased and topic-scoped; fold state carries across windows up to a "
        "**horizon**, declared in the table as a count of windows and **given no value** (§1, §6).",
        "**Not the mechanism's** (drafter's choice): cross-principal state on every admit's path is the fleet-wide "
        "coupling ADR-0039 §4 refused; thresholds would change by release; a deny may rest on a claim, mechanism state "
        "should not (§1)."], accent="amber", size=13.5, status="proposed", status_extra="ADR-0051 §1")
    my += hdr + 18
    t1 = c.card(xb + 20, my, cw - 40, "Tier 1 · Correlations (§2): specified", [
        "`carried-label`: the floor's F1 to F3 restated over the domain, labels carried across rounds and cells through "
        "shared targets.",
        "`shared-ingress`: an item one watcher found against, delivered to other cells.",
        "`probe-then-use`: a call admitted on an entry other principals were refused on.",
        "`marked-past`: an Observer whose mark passed a record another watcher found against.",
        "`distance-drift`: one cell's Reader distance departing from other cells on the same Persona.",
        "**A fold with a fixed definition**: given the same facts, every correlator computes the same result; no model "
        "is needed."], accent="amber", size=13.5, tint=False, dash="6 4")
    my += t1 + 18
    t2 = c.card(xb + 20, my, cw - 40, "Tier 2 · Judgment (§4): not specified, and no record can", [
        "Fragmented intent, a coordination signature: whatever the correlator's Persona concludes from payloads. Its "
        "form is fixed (a finding with evidence, deny-only, attributed) and **nothing rests on it**: no property in §10 "
        "mentions it.",
        "It feeds tier 1: a judgment finding cites records, so it can trigger `shared-ingress` and create misses."],
        accent="grey", size=13.5, tint=False, dash="6 4")
    my += t2 + 18
    sw2 = (cw - 40 - 18) / 2
    s1 = c.card(0, 0, sw2, "Fold state", ["Seats, rounds, log indices, `seq`, digests, labels, marks, counts. **No "
                                         "payload bytes.** A cache, never a source."], accent="amber", draw=False,
                size=13, bullets=False)
    s2 = c.card(0, 0, sw2, "Judgment state", ["What the judgment derives from payloads; dropped with the round."],
                accent="grey", draw=False, size=13, bullets=False)
    sh = max(s1, s2)
    c.card(xb + 20, my, sw2, "Fold state", ["Seats, rounds, log indices, `seq`, digests, labels, marks, counts. **No "
                                            "payload bytes.** A cache, never a source."], accent="amber", h=sh, size=13,
           bullets=False, tint=False)
    c.card(xb + 20 + sw2 + 18, my, sw2, "Judgment state", ["What the judgment derives from payloads; dropped with the "
                                                           "round."], accent="grey", h=sh, size=13, bullets=False,
           tint=False)
    my += sh + 18
    mk = c.card(xb + 20, my, cw - 40, "Its mark", [
        "The correlator's heartbeat names a watched topic and a watermark (ADR-0039 §1, §4). **For a correlator the mark "
        "asserts that every record through it has been folded.** It gates nothing; it is what `marked-past` reads (§6)."],
        accent="pink", size=13.5, bullets=False)
    my += mk + 18
    mid_bot = my + 6
    c.region(xb, top, cw, mid_bot - top, "The correlator · Proposed · not built at the reference", "amber", dash="10 6",
             size=14)

    # -- outputs
    oy = top + 40
    outs = [
        ("A finding carries its evidence (§3)", "amber", [
            "It names its **correlation**, the **principals** it is against, and the **facts** that satisfied it, each by "
            "topic and sequence number or by log index. A judgment finding names `judgment`.",
            "**Anyone who reads the same facts can recompute it**: a second correlator, an operator, an auditor. A false "
            "one is attributable (ADR-0038 §5).",
            "**The mechanism does not check it first** (drafter's choice): that would put the folds in the trusted "
            "base to save availability."], "proposed"),
        ("Misses, reported as facts (`marked-past`)", "pink", [
            "A watcher whose mark passed a cited record, that reads what the finding rests on, and that found nothing, "
            "has a **miss**; charged **within a tier** (R2). At `m_miss` misses in the window it is named.",
            "**A miss on a correlation is not a matter of judgment**: the fold is fixed, so a correlator that marked past "
            "a firing either did not compute it or did not report it."], "proposed"),
        ("What a finding does (§1; ADR-0007; ADR-0038 §5)", "red", [
            "**Deny-only, by any-of.** It may name any principal in the correlator's domain; what it stops is **the "
            "named principals' next admits**. In Build, a correlation is ground for the correlator's `Vote(deny)`; its "
            "silence is still not a veto.",
            "**Detection after the fact**: the call that completes a path was admitted. What a finding does after the "
            "next admit, the hold and the lift, is open (items 22, 48)."], None),
        ("Never on the admit path (ADR-0039 §4)", "grey", [
            "No admit and no promotion waits on a correlator. A correlation fires after the admit that completes it. "
            "The module's `LagNeverGates` (the record's `CorrelatorNeverGates`) holds with the folds present; "
            "`M_COUPLE` breaks it."], None),
    ]
    for t, a, b, st in outs:
        h = c.card(xc + 20, oy, cw - 40, t, b, accent=a, size=13.5, status=st,
                   status_extra="ADR-0051" if st else "", tint=a not in ("red",), dash="6 4" if a == "red" else None)
        oy += h + 18
    out_bot = oy + 6
    c.region(xc, top, cw, out_bot - top, "Outputs: findings and misses, deny-only", "red", dash=None, size=14)

    ay = top + 140
    c.arrow([(xa + cw, ay), (xb, ay)], "teal", sw=2.6, label="facts, folded\nin log order", lpos=0.5)
    c.arrow([(xa + cw, in_bot - 120), (xb, in_bot - 120)], "pink", sw=2, dash="7 5", label="payloads:\ntier 2 only",
            lpos=0.5)
    c.arrow([(xb + cw, ay), (xc, ay)], "amber", sw=2.6, label="findings with\nevidence", lpos=0.5)
    c.arrow([(xb + cw, mid_bot - 100), (xc, mid_bot - 100)], "pink", sw=2, label="misses as\nfacts", lpos=0.5)
    y = max(in_bot, mid_bot, out_bot) + 40

    # -- W(p), K and the mark
    y += _row(c, X0, y, Wd, [
        ("The correlator is in every `W(p)` of its domain (ADR-0038 §2)", [
            "`W(p)` is the `observer` seats whose lease holds a read authorization on `p`'s round topic: `p`'s cell "
            "Observer and the domain's correlators. So `marked-past` **covers correlators**: one that stays silent on a "
            "correlation another correlator reported has a miss.",
            "**With one watcher per principal it computes nothing** (finding 7). Two correlators are the archetype; one "
            "is D-0051-2. At the reference `W(p)` is not an ACL: nothing gates who reads (item 46)."],
         "teal", None, "", {}),
        ("`K` couples a cell Observer, never the correlator (ADR-0039 §1, §4)", [
            "`live(o)` and `seq(t) − mark(o, r) < K` are a cell Observer's. **The correlator's mark enters no "
            "`live(o)`**: its lag bounds nothing. The bound on what follows a `carried-label` path is that lag, \"which "
            "nothing couples\" (Consequences).",
            "`K` (8) and Run's `R` (64), themselves placeholders, are the yardstick `n_probe` (3) is small against (§2)."],
         "pink", None, "", {}),
        ("What the mark does not say (finding 6)", [
            "A watermark is over a round topic's sequence. `Consult` admits, grants and seals are facts in the log with "
            "**no place in any sequence**, so a correlator's mark does not say it has folded them, and "
            "`shared-ingress` reads `Consult` admits.",
            "A mark over log facts is an open obligation."],
         "grey", None, "", {}),
    ], size=14) + 70

    # ======================================================================== B. the split path
    y += c.heading(X0, y, "`carried-label`: the path the floor cannot see, split across two cells through a shared "
                          "target (§2; `M_ROUNDSCOPE` is the floor alone)", "amber", 21)
    y += c.para(X0, y, Wd, "The floor's F1 to F3 (`R5` to `R7`) refuse an outward `Actuate` over the round's own "
                "`clearSet`, which restarts with each round and belongs to one principal. A tainted cell writes to an "
                "inside store and a clean cell reads it under the store's declared label: **every declaration honest "
                "when made, and the floor admits both calls** (finding 2). The trace below is TLC's for `M_ROUNDSCOPE` "
                "(row `rs-carried`), drawn with a second Thinker in a second cell.", 14.5, "muted") + 24
    la_y = y + 30
    lw = Wd - 760
    xs = [X0 + 160, X0 + 160 + (lw - 160) * 0.36]
    sc_w = (lw - 160) * 0.30
    steps_a = [
        ("1 · delivered clear", ["`tA` is delivered an `untrusted` item clear. Its `clearSet` holds `untrusted`."]),
        ("2 · writes to `x`: admitted", ["An `Actuate` on an **inside** entry whose `channel.target` is `x`. Not "
                                         "outward, so F1 to F3 do not apply. `out(a)` ∋ `untrusted`."]),
    ]
    steps_b = [
        ("3 · reads `x`: admitted", ["Through an inside entry: the result carries `x`'s declared label, clean. "
                                     "`tB`'s `clearSet` stays clean."]),
        ("4 · sends: admitted", ["An outward `Actuate` with a literal destination. F2 (`R6`) needs `untrusted` in "
                                 "`clearSet`, and `tB`'s is clean."]),
    ]
    ha = max(c.card(0, 0, sc_w, t, b, accent="green", draw=False, size=13.5, bullets=False) for t, b in steps_a + steps_b)
    lb_y = la_y + ha + 190
    c.text(X0, la_y + 22, "cell A", 17, "green", bold=True)
    c.text(X0, la_y + 44, "Thinker `tA`", 14, "muted")
    c.text(X0, lb_y + 22, "cell B", 17, "green", bold=True)
    c.text(X0, lb_y + 44, "Thinker `tB`", 14, "muted")
    for i, (t, b) in enumerate(steps_a):
        c.card(xs[i], la_y, sc_w, t, b, accent="green", h=ha, size=13.5, bullets=False)
    for i, (t, b) in enumerate(steps_b):
        c.card(xs[i], lb_y, sc_w, t, b, accent="green" if i == 0 else "red", h=ha, size=13.5, bullets=False)
    c.arrow([(xs[0] + sc_w, la_y + ha / 2), (xs[1], la_y + ha / 2)], "green", sw=2.2)
    c.arrow([(xs[0] + sc_w, lb_y + ha / 2), (xs[1], lb_y + ha / 2)], "green", sw=2.2)
    # the shared target
    tx_w = 260
    tx = xs[1] + sc_w + 70
    ty = (la_y + ha + lb_y) / 2 - 50
    th = c.card(tx, ty, tx_w, "inside target `x`", ["Shared by both cells; declared clean. Not erased with any round."],
                accent="brown", size=13.5, bullets=False)
    c.arrow([(xs[1] + sc_w / 2, la_y + ha), (xs[1] + sc_w / 2, la_y + ha + 40), (tx + tx_w / 2, la_y + ha + 40),
             (tx + tx_w / 2, ty)], "brown", sw=2.2, label="writes", lpos=0.55)
    c.arrow([(tx + tx_w / 2, ty + th), (tx + tx_w / 2, lb_y - 40), (xs[0] + sc_w / 2, lb_y - 40),
             (xs[0] + sc_w / 2, lb_y)], "brown", sw=2.2, label="reads", lpos=0.3)
    c.region(X0 + 140, la_y - 24, lw - 140 + 330, lb_y + ha + 24 - (la_y - 24),
             "The floor sees four admits, each within one round of one principal", "blue", dash="10 6", size=13.5)
    # the correlator's fold
    fx = X0 + lw + 360
    fw = X1 - fx
    fh = c.card(fx, la_y - 24, fw, "The correlator, folding the window", [
        "`carried(x)`, the join of `out(a)` over every `Actuate` earlier in the window on an entry whose target is `x`: "
        "∋ `untrusted`.",
        "The **effective label** of `tB`'s read is its `resultLabel` joined with `carried(x)` as it stood; so `tB`'s "
        "**effective `clearSet`** ∋ `untrusted`.",
        "Step 4 meets F2's condition **over the effective values**: `carried-label` fires, naming `tB` and `tA`, whose "
        "call contributed the label. Any-of: the next admits of both are blocked.",
        "**`out(a)` is over effective values** (R2): the first draft took the mechanism's own, which carried a label "
        "one hop. `M_ONEHOP` breaks the property only with two targets.",
    ], accent="amber", size=13.5, status="proposed", status_extra="ADR-0051 §2")
    c.arrow([(xs[1] + sc_w, lb_y + ha / 2), (fx, lb_y + ha / 2)], "amber", sw=2.4, dash="7 5",
            label="the facts of all four", lpos=0.62)
    y = max(lb_y + ha + 40, la_y - 24 + fh) + 26
    y += _row(c, X0, y, Wd, [
        ("It is as coarse as `clearSet`, and coarser", [
            "Any call to `x` under a tainted `clearSet` taints `x` for the window, **whether or not the call wrote "
            "anything**: the entry does not say whether a call writes. `NeverFoundClean` is reached: the fold fires on "
            "a send whose Thinker read nothing of an attacker's. **It will fire on honest work.**"],
         "amber", None, "", {}),
        ("Erasure opens a hole (§6; R2)", [
            "Erasing `tA`'s round drops its rows, and the horizon drops old ones. **`x` is not erased with it.** A later "
            "read of `x` is clean to every fold, and nothing fires: the witness `NeverLostTaint` is reached, and is "
            "unreachable under `M_KEEP`. Stated, not closed: `carried-label` covers a path only while every fact on it "
            "is still held."],
         "red", None, "", {"tint": False, "dash": "6 4"}),
        ("What it cannot see (§8)", [
            "A wrong declaration: `channel.target` and labels are read as declared. Flows that share no target and no "
            "item. Delegation and chains. Build, whose `Read` is not labelled: there the other four apply. A `Consult` "
            "carries nothing: the Run root is pinned and no `Actuate` writes to it."],
         "grey", None, "", {}),
    ], size=14) + 70

    # ======================================================================== C. the record's tables
    y += c.heading(X0, y, "ADR-0051's tables, in full", "amber", 21)
    hw = (Wd - 40) / 2
    c.text(X0, y + 18, "§1 · The function has two tiers, and only the first is specified", 17, "amber", bold=True)
    c.text(X0 + hw + 40, y + 18, "§2 · The five correlations", 17, "amber", bold=True)
    y += 30
    h1 = c.table(X0, y, [("Tier", hw * 0.17, {"bold": True}), ("Computed from", hw * 0.33), ("By", hw * 0.27),
                         ("Can a second reader recompute it?", hw * 0.23)], [
        ["Correlations (§2)", "Facts only: the log, and the envelopes on the round topics",
         "A fold with a fixed definition", "**Yes**"],
        ["Judgment (§4)", "Facts and payloads", "Whatever the correlator's Persona is", "No"],
    ], size=13.5, accent="amber")
    h1 += 14 + c.para(X0, y + h1 + 14, hw, "Both tiers produce findings, and every finding only subtracts. Neither tier "
                      "is on the admit path. A facts-only correlator computes all five correlations; the narrowing "
                      "ADR-0038 §3 permits gives up §4 and nothing in §2.", 13.5, "muted")
    h2 = c.table(X0 + hw + 40, y, [("Name", hw * 0.2, {"mono": True}), ("What it sees", hw * 0.55),
                                   ("Stands on", hw * 0.25)], [
        ["carried-label", "The floor's F1 to F3, with labels carried across rounds and cells through shared targets",
         "ADR-0047, ADR-0049 (Proposed)"],
        ["shared-ingress", "An item one watcher found against, delivered to other cells", "Accepted text"],
        ["probe-then-use", "A call admitted on an entry other principals were refused on", "Accepted text, and §5"],
        ["marked-past", "An Observer whose mark passed a record another watcher found against", "Accepted text, and §3"],
        ["distance-drift", "One cell's Reader distance departing from other cells that hold the same Persona",
         "Accepted text"],
    ], size=13.5, accent="amber")
    h2 += 14 + c.para(X0 + hw + 40, y + h2 + 14, hw, "\"(Proposed)\" is the record's text of 2026.10.04. **ADR-0047 and "
                      "ADR-0049 were ratified in Batch 34** (G10 §1), so §10's \"ratified first, or `carried-label` is "
                      "left out\" no longer holds the correlation back.", 13.5, "muted")
    y += max(h1, h2) + 40

    # definitions of the four other folds
    y += _row(c, X0, y, Wd, [
        ("`shared-ingress`", [
            "A finding by any member of `W(p)` cites the records it is about. Where a cited record is an `Actuate` "
            "record with result digest `d`, or a `Consult` admit with reference `c`, it fires for **every other "
            "principal in the domain delivered an item with the same `d` or `c`** in the window, clear where ADR-0047 "
            "is in force.",
            "One poisoned item read by many cells is found in all of them when it is found in one. **It widens what one "
            "cell Observer can cause**: a compromised one can stall those cells through an honest correlator."],
         "amber", None, "", {"bullets": True}),
        ("`probe-then-use`", [
            "**Probes** on entry `e`: denial records in the window naming `e`, refused by policy: a forbid other than "
            "`R3-observer-live`, or no permit.",
            "Fires on an admit by `q` on `e` at log index `j` when at least `n_probe` probes on `e` by principals other "
            "than `q` have `at < j`. Names `q` and the probers: ADR-0038 finding 2's case.",
            "`at` can understate, so it fires more: availability. A missing denial is a missed probe."],
         "amber", None, "", {}),
        ("`marked-past`", [
            "When `o'` in `W(p)` reports a finding citing record `n` of `p`'s round `r`, every other `o` in `W(p)` "
            "**that reads what the finding rests on**, with `mark(o, r)` at or beyond `n`, and no finding citing `n`, "
            "has a miss. Named at `m_miss`.",
            "**ADR-0035 §6's test on live traffic**, with a difference: a planted defect is a defect, and another "
            "watcher's finding may be false. A Byzantine watcher can manufacture misses."],
         "amber", None, "", {}),
        ("`distance-drift`", [
            "For a Persona bound to two or more cells declaring `topk_logprobs`: fires, naming a cell's Thinker, when its "
            "distance is **more than `θ_drift` times the median of the others'**, and that median is not zero.",
            "**A ratio**, because no record fixes the distance's metric or unit. One-sided: a substituted model reads "
            "further away; under-reporting is collusion's shape.",
            "Not in the module."],
         "amber", None, "", {}),
    ], size=13.5) + 40

    hw3 = (Wd - 40) * 0.56
    c.text(X0, y + 18, "§2 · The placeholders (R1: the custodian's decision that there be some; the numbers are the "
                       "drafter's)", 17, "amber", bold=True)
    sx2 = X0 + hw3 + 40
    c.text(sx2, y + 18, "§6 · The store is a cache of a fold, keyed by round", 17, "amber", bold=True)
    y += 30
    h1 = c.table(X0, y, [("Value", hw3 * 0.1, {"mono": True}), ("Placeholder", hw3 * 0.15), ("Why this number",
                                                                                             hw3 * 0.48),
                         ("What a deployment sets it from", hw3 * 0.27)], [
        ["n_probe", "**3** (PLACEHOLDER)", "One refusal elsewhere is an ordinary mistake, and two can be one "
         "misconfiguration shared by two cells. Three is the smallest count that needs a third principal or a repeat. "
         "It is small against the unread bound `K` (8) and Run's round bound `R` (64), themselves placeholders",
         "The measured rate of policy refusals per entry in honest rounds"],
        ["m_miss", "**2** (PLACEHOLDER)", "One miss may be one disputed or false finding. Two in a window is a repeat. "
         "Findings are rare, so a larger number leaves a silent Observer in place for a long time",
         "The measured rate of findings, and of findings later judged false"],
        ["θ_drift", "**2.0** (PLACEHOLDER), a ratio", "A cell at twice the median of its peers on the same Persona. It "
         "has no unit, so it survives whatever metric the distance turns out to have. Whether honest cells on different "
         "tasks vary by more than that is unknown", "The measured spread of distance across cells that share a Persona"],
    ], size=13.5, accent="amber")
    h1 += 12 + c.para(X0, y + h1 + 12, hw3, "**None is measured.** Each is a deployment's choice; shipped unexamined, it "
                      "is declared, not inherited. `m_miss` at 2 lets one Byzantine watcher with two false findings name "
                      "an honest Observer. **The horizon has no placeholder.** `carried-label` and `shared-ingress` have "
                      "no parameter. The parameters are bundle data, not floor values: a correlation enables nothing.",
                      13.5, "muted")
    sw_ = Wd - hw3 - 40
    h2 = c.table(sx2, y, [("Store", sw_ * 0.2, {"bold": True}), ("Holds", sw_ * 0.45), ("Rule", sw_ * 0.35)], [
        ["Fold state", "For the window: seats, rounds, log indices, sequence numbers, digests, labels, marks, and the "
         "counts §2 defines. No payload bytes", "Every row is keyed by the round of the fact it was folded from"],
        ["Judgment state", "Whatever §4's reader derives from payloads",
         "Keyed by round, and dropped with the round (ADR-0038 finding 3, its first option)"],
    ], size=13.5, accent="amber")
    h2 += 12 + c.para(sx2, y + h2 + 12, sw_, "**The store never outlives its sources**: a row is kept only while its "
                      "fact is readable under the correlator's authorization; when a round is erased (ADR-0006) its rows "
                      "go, except what the log still holds. **It is the correlator's own**: not in the replicated state, "
                      "not in the mechanism; it sits with the seat under ADR-0038 §4's placement. Losing it costs a "
                      "recomputation.", 13.5, "muted")
    y += max(h1, h2) + 40

    c.text(X0, y + 18, "§9 · Degeneracy on this record", 17, "amber", bold=True)
    y += 30
    y += c.table(X0, y, [("Id", Wd * 0.07, {"bold": True}), ("Kind", Wd * 0.07), ("Parameter → deployed value",
                                                                                  Wd * 0.25),
                         ("Premises falsified", Wd * 0.2), ("Theorems voided", Wd * 0.25),
                         ("Type changes (ADR-0023 §6b)", Wd * 0.16)], [
        {"cells": ["D-0051-1", "Declaration", "Correlations computed: the five → none. The seat exists and reports "
                   "nothing but heartbeats. **The reference today**", "A correlator computes the correlations of its "
                   "table", "**None.** §10's properties are lost. D-0038-2 with a seat filled", "None"],
         "accent": "red"},
        ["D-0051-2", "Deployment", "Correlators in a domain: two or more → one", "A correlator's silence on a "
         "correlation is a miss some other correlator counts", "None. `marked-past` still covers cell Observers",
         "None"],
    ], size=13.5, accent="amber") + 10
    y += c.para(X0, y, Wd, "A table that turns a correlation `off` is not a degeneracy. It is declared in the bundle and "
                "visible in it.", 13.5, "muted") + 36

    c.text(X0, y + 18, "Options considered", 17, "amber", bold=True)
    y += 30
    y += c.table(X0, y, [("Option", Wd * 0.34, {"bold": False}), ("Disposition", Wd * 0.66)], [
        ["**Leave the function to the correlator's Persona**: a model reads everything and finds what it finds",
         "Not taken as the whole function. It is §4, and by itself it is the noun the 09.16 review named: nothing to "
         "check, measure or recompute"],
        ["**Compute the folds in the mechanism**, as `clearSet` is", "Not taken (drafter's choice) (§1). "
         "Cross-principal state on the admit path, thresholds by release, and a claim in mechanism state. "
         "`carried-label` could move there later as a floor entry if a deployment wants prevention and will pay the "
         "coupling"],
        ["**Extend `clearSet` across rounds in the mechanism** and leave cross-cell to the correlator", "Not taken. A "
         "principal carries nothing from round to round except through a target, so the cross-round case is the "
         "cross-cell case"],
        ["**The mechanism checks a correlation finding before acting on it**", "Not taken (drafter's choice) (§3). It "
         "removes a Byzantine correlator's false correlation findings and adds the folds to the trusted base"],
        ["**A per-principal sequence number on denials** (ADR-0038 finding 2)", "Not taken (§5). It needs agreement "
         "among replicas on something ADR-0015 leaves unordered. `at` is already written"],
        ["**Order denials in the log**", "Rejected by ADR-0015 and ADR-0003 A2, and not reopened"],
        ["**`shared-ingress` only after the correlator has read the item itself**", "Not taken (drafter's choice). A "
         "facts-only correlator could then never propagate. The cost is in Consequences"],
        ["**A store that holds facts for ever**", "Rejected. It would hold digests of erased rounds beyond what the log "
         "keeps, which is ADR-0038 finding 3's shadow"],
        ["**Thresholds in the floor's values file**, beside `T_obs` and `K`", "Not taken. Those relax an enabling "
         "condition. A correlation enables nothing"],
        ["**No values for `n_probe`, `m_miss` and `θ_drift`** until one is measured", "The first draft. Not taken at "
         "R1, by the custodian's decision. A table with no numbers leaves §10's module and the scripted correlator "
         "nothing to run at. The numbers are labelled placeholders three times, for ADR-0039's reason"],
        ["**`θ_drift` as an absolute difference**", "The first draft. Not taken at R1 (drafter's choice). No record "
         "gives the distance a metric, so a difference has no unit to be stated in"],
        ["**A new seat kind for the facts tier**", "Rejected, as ADR-0038 rejected one for the correlator. It reports "
         "findings and heartbeats, which is `observer`'s alphabet"],
        ["**Chain depth, delegation and on-behalf-of as correlations**", "Not possible yet. No record models a chain "
         "(row 1.3)"],
    ], size=13.5, accent="amber") + 36

    c.text(X0, y + 18, "History", 17, "amber", bold=True)
    y += 30
    y += c.table(X0, y, [("Tag", Wd * 0.04, {"bold": True}), ("Kind", Wd * 0.1), ("Change", Wd * 0.5),
                         ("Source", Wd * 0.2), ("State", Wd * 0.16)], [
        ["—", "—", "Initial draft. The correlator's function in two tiers: five correlations as fixed folds over facts "
         "(`carried-label`, `shared-ingress`, `probe-then-use`, `marked-past`, `distance-drift`), with their parameters "
         "in a bundle table and no values; and an unspecified judgment tier over payloads. Every finding carries its "
         "correlation and its evidence. Denials are placed against the log by `at` and `decided_by`, with no sequence "
         "number. The store is a cache of the fold, keyed by round, holding no payload and nothing the record no longer "
         "holds, with a horizon in windows. Collusion narrowed and not closed. Two degeneracies; twelve options; seven "
         "findings", "ADR-0038 findings 1 to 3; G9 items 43 and 44; design-gap rows 1.4 and 3.3; ADR-0047 §5; the "
         "reference's `record_denial`; the custodian's request 2026.10.04", "Proposed. Drafted by the assistant at the "
         "custodian's direction, not reviewed, and not preceded by a design discussion"],
        ["R1", "Revision before ratification", "**Placeholders for the three thresholds.** §2: `n_probe` 3, `m_miss` 2, "
         "`θ_drift` 2.0, each labelled a placeholder, unmeasured and a deployment's choice, with why each number and "
         "what replaces it. `distance-drift` is restated as a ratio against the peers' median, one-sided, because no "
         "record fixes the distance's metric; the first draft had an absolute difference. The horizon keeps no value. "
         "One option reversed and one added; one consequence and two open obligations changed", "The custodian's "
         "decision, 2026.10.04; ADR-0019 and ADR-0037 §3 as read for the metric", "Proposed"],
        ["R2", "Revision before ratification", "**The module is written, and it changed the record.** "
         "`spec/Correlator.tla` checks three of the five correlations with ghost truth for what is really tainted. §2: "
         "`out(a)` is over effective values, where the first draft carried a label one hop (`M_ONEHOP`); a miss is "
         "charged within a tier, where the first draft charged a facts-only correlator for every cell Observer's "
         "judgment (`M_TIERLESS`). §6: erasure and the horizon leave a tainted target no fold can see, stated and not "
         "closed. Eight properties hold, eight mutations break what they must, seven witnesses are reached. §10 records "
         "what is met and what is not; one consequence, one finding and two open obligations added",
         "`spec/Correlator.tla` (`351b4159e0e298d9`); `spec/Correlator-results-2026.10.04.txt` (`58ca6d4d27754745`); "
         "the custodian's request for the proofs, 2026.10.04", "Proposed"],
        ["R3", "Revision before ratification", "**The invariants are proved.** `spec/Correlator_proof.tla` "
         "(`5dc0e337ead963dd`, 455 obligations) proves all eight for every set of Thinkers, targets and correlators and "
         "every bound, with no assumption on the constants; results `spec/Correlator-proof-results-2026.10.04.txt` "
         "(`9f20a44f783dfd92`). The certified route passes too: 445 obligations rest on `tlapm`'s normalization or a "
         "checked proof and 10 on LS4 (`spec/Correlator-proof-cert-results-2026.10.04.txt`, `48eaeb0ed25ceb1a`). No "
         "decision text changes", "`spec/Correlator_proof.tla`; `spec/proof-cert.sh`", "Proposed"],
    ], size=13, accent="amber") + 70

    # ======================================================================== D. the module
    y += c.heading(X0, y, "`spec/Correlator.tla`: checked by TLC, proved by TLAPS, certified (ADR-0051 §10, R2, R3; "
                          "ADR-0046 A1)", "teal", 21)
    y += c.para(X0, y, Wd, "TLC constants: Thinkers `{t1, t2}`, correlators `{c1, c2}` of which `c1` is honest, two "
                "rounds, one item, one send (two in one witness row), one or two shared targets. **Every property is "
                "stated over the module's own state; `CarriedCoversSplitPath` over ghost truth**: which bytes are really "
                "an attacker's. Mutations and witnesses are behaviours and stay with TLC; the proof is over every set of "
                "Thinkers, targets and correlators and every bound.", 14, "muted") + 18
    y += c.table(X0, y, [("Property (module name)", Wd * 0.15, {"mono": True}), ("What it says", Wd * 0.33),
                         ("Mutation that must break it", Wd * 0.27), ("TLC (2026.10.04)", Wd * 0.13),
                         ("Proof", Wd * 0.12)], [
        ["CarriedCoversSplitPath", "If tainted bytes reach an outward call through any chain of shared targets across "
         "cells or rounds in the window, **by a chain whose facts are still held**, `carried-label` has fired by the "
         "time the correlator's mark passes the call", "`M_ROUNDSCOPE`: labels not carried past a round, **the floor "
         "alone**. `M_ONEHOP`: `out(a)` carries one hop", "`rs-carried` violated; `M_ONEHOP` holds with one target, "
         "violated with two", "Proved, unless either mutation"],
        ["FindingHasEvidence", "Every correlation finding's cited facts satisfy its correlation", "`M_BARE`",
         "`bare-evidence` violated", "Proved, unless `M_BARE`"],
        ["IngressReachIsShared", "`shared-ingress` names only principals that were delivered the cited item",
         "`M_DOMAIN`: it names the domain", "`domain-reach` violated", "Proved, unless `M_DOMAIN`"],
        ["SilenceIsCounted", "An Observer whose mark passed a cited record without a finding has a miss, a correlator "
         "on a correlation included", "`M_SELF`: a correlator's misses are not counted", "`self-silence` violated",
         "Proved, unless `M_SELF`"],
        ["MissIsOnACorrelation", "Every miss is charged on a correlation: the tier rule (R2)", "`M_TIERLESS`: a "
         "judgment charges every correlator", "`tier-miss` violated", "Proved, unless `M_TIERLESS`"],
        ["HonestNeverCharged", "The honest correlator is never charged a miss", "`M_BARE`; `M_TIERLESS`",
         "`bare-charged`, `tier-charged` violated", "Proved, unless either"],
        ["StoreWithinRecord", "No row is held for an erased round beyond what the log holds", "`M_KEEP`",
         "`keep-store` violated", "Proved, unless `M_KEEP`"],
        ["LagNeverGates", "A Thinker no finding blocks can always act, whatever the correlator's lag (`ENABLED`); the "
         "record's `CorrelatorNeverGates`", "`M_COUPLE`", "`couple-lag` violated", "Proved, unless `M_COUPLE`"],
        {"cells": ["Safe", "All eight together, no mutation", "—", "Holds: 2,285,708 distinct states with one target, "
                   "67,422,620 with two", "`SafeAlways`"], "accent": "teal"},
    ], size=13.5, accent="teal") + 30
    y += _row(c, X0, y, Wd, [
        ("Seven witnesses, each reached", [
            "`NeverSplitFound`: a send the floor admitted, on an attacker's bytes, is found.",
            "`NeverFoundClean`: the fold fires on a send whose Thinker read nothing of an attacker's.",
            "`NeverSharedTwo`: `shared-ingress` names a second Thinker.",
            "`NeverMiss`: a correlator's silence is counted. `NeverNamed`: `marked-past` fires, also at "
            "`m_miss` = 2 with two sends.",
            "`NeverLostTaint`: **the erasure hole**, reached; unreachable under `M_KEEP`. `NeverErasedARow`: a round is "
            "erased while a row keyed by it is held."],
         "teal", None, "", {}),
        ("Proved, and certified: what that means", [
            "**Proved**: `Correlator_proof.tla`, **455 obligations, assumptions none**; ten theorems from `TypeAlways` "
            "to `SafeAlways`, each invariant under the mutations that break it as its only hypothesis. Each hypothesis "
            "was dropped in a scratch copy and the prover failed each time.",
            "**Certified**: 286 closed by `tlapm` with no backend; 158 by cvc5 with a proof `ethos` accepted; 1 by "
            "Zenon with Isabelle checking it; **10 temporal steps on LS4, not certified**.",
            "**A certified proof is not a verified one**: the prover's translation, its normalization, LS4 and the "
            "checker are trusted (proof-certification.md §8)."],
         "teal", None, "", {}),
        ("Not met by the module (§10)", [
            "`probe-then-use` and `distance-drift` are not in it. It carries one label, so F1, F3 and handles are outside "
            "it.",
            "The horizon is modelled only as erasure is; the judgment tier is one action; a finding never clears.",
            "**It carries the fold's value in its state** and models a correlator's lag as when it reports, so **it does "
            "not show that an implementation computes the fold**. No rows for it in the binding table."],
         "red", None, "", {"tint": False, "dash": "6 4"}),
    ], size=13.5) + 70

    # ======================================================================== E. open
    y += c.heading(X0, y, "What remains open", "red", 21)
    y += _row(c, X0, y, Wd, [
        ("Collusion still fails open (§7; G10 §8)", [
            "**`marked-past` is the first place an Observer's silence is compared with anything**: a cell Observer that "
            "marks past what another watcher found is counted, and a silent correlator is caught by any other.",
            "**It needs a second opinion.** Where every member of `W(p)` colludes, or the only other watcher shares a "
            "lineage and misses the same things, there is nothing to miss against. **Detection fails open against a "
            "colluding Observer** (ADR-0039 §5); with this record, only when every watcher of the record fails together.",
            "Independence is still ADR-0035's, **Proposed**; this record does not put it in force."],
         "red", "open", "G10 §8", {"tint": False, "dash": "6 4"}),
        ("§10 · Ratification condition, at G10", [
            "**Met**: the module, checked (R2), proved and certified (R3). ADR-0047 and ADR-0049 ratified first "
            "(Batch 34).",
            "**Not met**: the dependent entries in ADR-0038, ADR-0043 §4, ADR-0015 and ADR-0020, ADR-0006 and ADR-0049 "
            "§7 (none of them cites ADR-0051 at G10); **the reference**, a scripted correlator reading facts only, "
            "showing five behaviours (G10 item 97); **a reader who is not the drafter** (ADR-0029 A2)."],
         "amber", "proposed", "not ratified", {}),
        ("Consequences the record states against itself", [
            "Detection after the fact; the bound on what follows is the correlator's lag, which nothing couples.",
            "`shared-ingress` widens what one cell Observer can cause; `carried-label` fires on honest work; "
            "`marked-past` counts misses against findings that may be false.",
            "Three of five correlations run on placeholders. **Every `observer` Persona changes**: its findings must "
            "cite records. Two correlators are the archetype. `carried-label` rests on `channel.target`, a claim for a "
            "native tool."],
         "grey", None, "", {}),
        ("Open obligations (selected; the record lists seventeen)", [
            "Measured values for the three thresholds, and a value for the horizon. **The distance's metric.**",
            "**The finding's schema** for every `observer` seat (finding 4). A mark over log facts (finding 6). A "
            "Persona for a seat that runs no model (finding 5).",
            "What a finding does after the next admit (items 22, 48). Whether `carried-label` becomes a floor entry. "
            "Whether a target's taint may be kept as a fact that names no round. A correlation over the opening record. "
            "Narrative: ToO §5.1 and the glossary owe correlation, finding evidence and miss."],
         "grey", None, "", {}),
    ], size=13.5) + 40

    c.legend(X0, y, [("box", "amber", "Proposed: ADR-0051", "6 4"), ("box", "teal", "facts; the module's checks"),
                     ("box", "pink", "payloads; marks"), ("box", "red", "deny, gap, not built", "6 4"),
                     ("box", "green", "a Thinker's admits"), ("box", "brown", "a shared inside target"),
                     ("arrow", "amber", "a fold's input, after the admit", "7 5")])
    return c
