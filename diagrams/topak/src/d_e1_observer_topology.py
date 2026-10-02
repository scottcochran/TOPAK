"""E1 — Observer topology: a cell Observer per cell, a correlator across cells, the watched-by relation is the ACL."""
import re

import lib
from lib import Canvas

ID, SLUG = "E1", "observer-topology"


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


def _build():
    c = Canvas(ID, "Observer topology: one `observer` seat per cell, a correlator across cells, and `W(p)` is the ACL",
               "ADR-0038 (Accepted (genesis) 2026.09.29, Batch 13, confirmation required C3 and C4) supersedes ADR-0008: "
               "the shared Observer group becomes the correlator with a narrower job, each cell gets its own Observer, "
               "placement keeps ADR-0008's colocation rule on fault-domain grounds, and Observers combine by any-of with "
               "no quorum. Every finding is still deny-only (ADR-0007): nothing here touches the admit path.",
               3000, "ADR-0038 §1–§8, Options, Consequences, Findings 1–4, History R1–R3, B13, B18; ADR-0008 (Superseded); "
               "ADR-0007; ADR-0016 §5; ADR-0024 §2, §5 and A2; ADR-0035 §5; ADR-0037 §1–§3; ADR-0039 §4; "
               "spec/Observers.tla and Observers-results-2026.09.29.txt; spec/Observers_proof.tla and "
               "Observers-proof-results-2026.10.02.txt; ADR-0038 B25; mechanism/GAPS-AND-ASSUMPTIONS.md I8; "
               "ToO rev 11 §5.1; G7 §1.1, §7 items 43, 44, 46")
    X0, X1 = c.x0, c.x1
    y = c.y
    sx = X0
    sx += c.status(sx, y, "accepted", "C3, C4 · Batch 13") + 10
    sx += c.status(sx, y, "superseded", "ADR-0008, by this record") + 14
    c.text(sx, y + 16, "ADR-0008's colocation rule is carried forward (§4); its scoping and its instance economics "
                       "(about 9 shared instances against about 40 per-agent) are replaced.", 14.5, "muted")
    y += 54

    # ======================================================================== the domain
    top = y + 14
    pad = 34
    gap = 46
    ix0, ix1 = X0 + pad, X1 - pad
    CW = (ix1 - ix0 - 2 * gap) / 3
    dpad = 20
    DW = (CW - 2 * dpad - 26) / 2

    def thinker_body(i):
        return [f"Thinker `t{i}`, a `thinker` seat: a principal with its own lease, round topic and Persona "
                f"(ADR-0037 §1).",
                "Reaches the world only through admits."]

    reader_body = ["**Reader stage**: not a seat, no Persona (ADR-0037 §2). Its two facts, conformance verdict and "
                   "distributional distance, go to every seat in `W(p)` (R1). **May colocate** (§4)."]

    def obs_body(i):
        return [f"Cell Observer `o{i}`: an `observer` seat with `cell = t{i}` (`SeatDecl.cell`).",
                f"Reads `t{i}`'s round topic in full, payloads included, under the ACL.",
                "Compromise costs **one cell's detection**.",
                "Lineage from a different model family than `t" + str(i) + "` (monoculture rule)."]

    th = c.card(0, 0, DW - 2 * 16, "Thinker", thinker_body(1), "green", draw=False, size=13.5)
    rh = c.card(0, 0, DW - 2 * 16, "", reader_body, "teal", draw=False, size=13.5, bullets=False)
    oh = c.card(0, 0, DW - 2 * 16, "Cell Observer", obs_body(1), "pink", draw=False, size=13.5)
    devA_h = 30 + th + 14 + rh + 18
    devB_h = max(devA_h, 30 + oh + 18)
    devA_h = devB_h
    cell_y = top + 46
    dev_y = cell_y + 40
    topic_y = dev_y + devB_h + 74
    tph = c.card(0, 0, CW - 2 * dpad, "Round topic of t1 · read ACL (0003.3)", [
        "`W(t1)` = the `observer` seats whose lease holds a read authorization on this topic = { `o1`, `corr` }."],
        "teal", draw=False, size=13.5, bullets=False)
    cell_h = (topic_y + tph + 22) - cell_y

    topics = []
    for i in range(3):
        cx = ix0 + i * (CW + gap)
        n = i + 1
        c.region(cx, cell_y, CW, cell_h, f"cell {n} (ADR-0037): t{n} + its observer seat", "green", dash=None,
                 sw=1.8, tint=False, size=13.5)
        ax = cx + dpad
        bx = cx + dpad + DW + 26
        c.region(ax, dev_y, DW, devA_h, f"device A{n}", "grey", dash="5 4", sw=1.5, size=12.5)
        c.region(bx, dev_y, DW, devB_h, f"device B{n}", "grey", dash="5 4", sw=1.5, size=12.5)
        c.card(ax + 16, dev_y + 30, DW - 32, f"Thinker t{n}", thinker_body(n), "green", size=13.5, h=th)
        c.card(ax + 16, dev_y + 30 + th + 14, DW - 32, "", reader_body, "teal", size=13.5, bullets=False, h=rh)
        c.card(bx + 16, dev_y + 30, DW - 32, f"Cell Observer o{n}", obs_body(n), "pink", size=13.5, h=oh)
        tx = cx + dpad
        tw = CW - 2 * dpad
        c.card(tx, topic_y, tw, f"Round topic of t{n} · read ACL (0003.3)", [
            f"`W(t{n})` = the `observer` seats whose lease holds a read authorization on this topic = "
            f"{{ `o{n}`, `corr` }}."], "teal", size=13.5, bullets=False, h=tph)
        # emissions down, read edge up
        tcx = ax + DW / 2
        c.arrow([(tcx, dev_y + devA_h), (tcx, topic_y)], "green", label="admits: Emit / Report", lpos=0.5)
        ocx = bx + DW / 2
        c.arrow([(ocx, topic_y), (ocx, dev_y + devB_h)], "pink", sw=2.4, label="read (ACL)", lpos=0.5)
        topics.append((tx + tw / 2, topic_y + tph))

    # -- correlator
    cy0 = cell_y + cell_h + 120
    corr_w = 760
    corr_x = (ix0 + ix1) / 2 - corr_w / 2
    corr_body = [
        "One or more `observer` seats that **belong to no cell** (`SeatDecl.cell` empty). ADR-0008's shared group "
        "under a new name, with a narrower job: cross-cell detection only.",
        "Its round is a **correlation window** the deployment declares, leased and topic-scoped; its state across "
        "windows is its own derived store (finding 3).",
        "**A finding may name any principal in its domain**: the one thing a cell Observer cannot do. Still deny-only.",
        "Compromise costs **cross-cell detection only**; every cell Observer still works. It reads every cell's "
        "payloads, so it is the one place an injection in any cell can arrive.",
    ]
    ch = c.card(0, 0, corr_w - 40, "Correlator corr", corr_body, "pink", draw=False, size=14)
    c.region(corr_x, cy0, corr_w, ch + 54, "device C (not shared with any member of W(p))", "grey", dash="5 4",
             sw=1.5, size=12.5)
    c.card(corr_x + 20, cy0 + 30, corr_w - 40, "Correlator corr", corr_body, "pink", size=14)
    ent = [corr_x + 400, corr_x + 540, corr_x + 680]
    mid_y = cell_y + cell_h + 56
    for (tx, ty), ex, lp in zip(topics, ent, (0.75, 0.5, 0.75)):
        if abs(tx - ex) < 1:
            c.arrow([(tx, ty), (tx, cy0)], "pink", sw=2.4, label="read (ACL)", lpos=0.62)
        else:
            c.arrow([(tx, ty), (tx, mid_y), (ex, mid_y), (ex, cy0 + 30)], "pink", sw=2.4)
    c.label((topics[0][0] + ent[0]) / 2, mid_y, "read every cell's topic (ACL)", "pink")
    c.label((topics[2][0] + ent[2]) / 2, mid_y, "read every cell's topic (ACL)", "pink")

    # -- left and right of the correlator, inside the domain
    sidew = corr_x - 60 - ix0
    lh = c.card(ix0, cy0, sidew, "§2 · The watched-by relation is the ACL", [
        "For a principal `p`, `W(p)` is the set of `observer` seats whose lease holds a read authorization on "
        "`p`'s current round topic: `p`'s cell Observer and the correlators of `p`'s domain.",
        "A **fact in the mechanism's state**, evaluated by lookup, syntactic in ADR-0007's sense.",
        "ADR-0039 coupling is written against the relation, not against how it is populated, so either record can be "
        "superseded alone.",
        "[[red|Not realized at the reference]]: no per-topic read authorization exists, so cells are declared and not "
        "enforced (`mechanism/` I8; G7 item 46).",
    ], "teal", size=14)
    rx = corr_x + corr_w + 60
    rh2 = c.card(rx, cy0, ix1 - rx, "§4 · Placement: ADR-0008's rule, carried forward for seats", [
        "**No** `observer` **seat shares a device with a Thinker it watches.**",
        "**No two** `observer` **seats in** `W(p)` **share a device.**",
        "**The Reader stage may still colocate**: it was never an independent fault domain and is no longer a seat.",
        "The reason no longer rests on a quorum. A shared device means shared driver, firmware, memory error domain, "
        "thermal and power events and host kernel: **correlated failure plus an effect path through device memory** "
        "the model does not include.",
    ], "grey", size=14)
    dom_bottom = max(cy0 + ch + 54, cy0 + lh, cy0 + rh2) + 36
    c.region(X0, top, X1 - X0, dom_bottom - top, "One domain (Build or Run) · B2 Contain · ADR-0038 §1", "blue",
             dash=None, sw=2.6, tint=False, size=16)

    # ======================================================================== where findings go
    fy = dom_bottom + 80
    mw = 1300
    mx = X0
    mh = c.card(mx, fy, mw, "Contain: a finding becomes a deny, a quarantine or an eviction (ADR-0007)", [
        "**Findings are deny-only.** No Observer output admits anything; a deny needs no quorum: \"consensus for grants, "
        "local for denials\".",
        "**Any-of (§5).** A finding from any member of `W(p)` takes effect, and no agreement is sought. `Observers.tla` "
        "`DenyByAnyOf` holds; mutation `M_QUORUM` (a finding counts only with a majority of `W(p)`) gives a "
        "counterexample: one honest finding suppressed by the other Observer's silence.",
        "**Reach is bounded (§1).** A cell Observer's finding never blocks an admit outside its cell: "
        "`ReachIsBounded` holds; `M_REACH` (domain-wide reach for cell Observers) breaks it. Reach is declared "
        "and not enforced at the reference (I8).",
        "**Both proved** since 2026.10.02 (ADR-0038 B25): `Observers_proof.tla`, 65 obligations, `DenyByAnyOf` "
        "not under `M_QUORUM` and `ReachIsBounded` not under `M_REACH`. A proof of the module: reach stays declared, "
        "not enforced, at the reference.",
        "**More Observers never lower safety and may lower availability**: the monotone direction. Each added seat "
        "can raise detection if its lineage is independent, and adds a way to raise a false denial.",
    ], "red", size=14, tint=False, dash="6 4")
    vx = mx + mw + 60
    vw = X1 - vx
    vh = c.card(vx, fy, vw, "§6 · The veto roster holds cell Observers and correlators (Build)", [
        "ADR-0024 §5's veto-seat holder becomes every cell Observer seat and every correlator seat in the Build domain "
        "(ADR-0024 A2, in force; ToO §5.1). The reference seats `o1` in `a1`'s cell and `corr`, both on the roster.",
        "A veto seat's alphabet is unchanged: `Vote(deny)` **only**. A correlator's `Vote(grant)` is refused; its "
        "silence is not a veto (ADR-0024 §2).",
        "ADR-0035 §5's tally condition (a veto seat with a Persona independent of the author's) is met by the author's "
        "cell Observer by construction under seat distinctness, or by an independent correlator. A2.2 is not checked "
        "by the reference (G18).",
        "\"One compromised seat is a veto until the anchor reissues the roster\" applies to a correlator as written.",
    ], "blue", size=14)
    # arrows from domain to the findings box and the roster
    c.arrow([(mx + mw / 2, dom_bottom), (mx + mw / 2, fy)], "red", dash="7 5", sw=2.4,
            label="findings from any member of W(p): deny-only", lpos=0.5)
    c.arrow([(vx + vw / 2, dom_bottom), (vx + vw / 2, fy)], "blue", sw=2.4,
            label="Vote(deny) from veto seats (Build)", lpos=0.5)
    y = fy + max(mh, vh) + 60

    # ======================================================================== §1 table and degeneracies
    y += c.heading(X0, y, "§1 · The archetype has an Observer per cell and a correlator across cells", "pink")
    W = X1 - X0
    y += c.table(X0, y, [("Observer", 230, {"bold": True}), ("Seat", 640), ("Watches", 420),
                         ("Reads", 900), ("Scope of a compromise", W - 2190)], [
        ["Cell Observer", "One `observer` seat per cell (ADR-0037 §2)", "Its cell's Thinker",
         "The Thinker's round topic, payloads included, under the ACL (0003.3)", "One cell's detection"],
        ["Correlator", "One or more `observer` seats that belong to no cell", "Every cell in its domain",
         "§3: facts, typed envelopes and payloads (below)", "Cross-cell detection only; every cell Observer still works"],
    ], size=14, accent="pink") + 40

    w2 = (W - 30) / 2
    reads = [
        "**Facts** from every cell: admits and denials with principal, lease, epoch and per-principal sequence number "
        "(`topak-seq`, extended to denials: finding 2, G7 item 44); cell Observers' findings as control-plane facts; "
        "the Reader stage's facts for every Persona declaring `topk_logprobs` (R1); lease grants, renewals, revocations "
        "and seals. A cross-cell drift in distance is a substitution signal no single cell can see.",
        "**Typed action envelopes**: variant, reference, target or tool, principal. Which `Draft` and `Invoke` fields "
        "are control-plane is ADR-0022's open follow-up.",
        "**Payloads** of every cell's round topics, under the ACL.",
    ]
    narrow = [
        "**Facts only**: a permitted narrowing, recorded as the **mitigation on D-0038-2's declaration** "
        "(ADR-0023 §6).",
        "**Gives up** cross-cell semantic detection: the fragmentation case of Makins et al. (09.16 review CR-3).",
        "**Gains**: an injection in one cell's content reaches the correlator only through a fixed-schema fact.",
        "The archetype does not take the trade: it does not give up capability (ADR-0023 §3).",
    ]
    h1 = c.card(0, 0, w2, "§3 · What the correlator reads at the archetype: everything the shared group could", reads,
                "pink", draw=False, size=14)
    h2 = c.card(0, 0, w2, "Facts-only correlator: a deployment's narrowing, not the archetype", narrow, "amber",
                draw=False, size=14)
    hh = max(h1, h2)
    c.card(X0, y, w2, "§3 · What the correlator reads at the archetype: everything the shared group could", reads,
           "pink", size=14, h=hh)
    c.card(X0 + w2 + 30, y, w2, "Facts-only correlator: a deployment's narrowing, not the archetype", narrow, "grey",
           size=14, h=hh, dash="6 4")
    c.arrow([(X0 + w2, y + hh / 2), (X0 + w2 + 30, y + hh / 2)], "grey", dash="7 5")
    y += hh + 40

    y += c.heading(X0, y, "§7 · Degeneracies on this record (declaration kind; both ratify as record-level entries)",
                   "pink")
    y += c.table(X0, y, [("Id", 140, {"bold": True}), ("Kind", 130), ("Parameter → deployed value", 560),
                         ("Premises falsified", 440), ("Theorems voided", W - 140 - 130 - 560 - 440 - 330),
                         ("Type changes (ADR-0023 §6b)", 330)], [
        ["D-0038-1", "Declaration", "Cell Observers: one per cell → none, with the correlator kept. **This is ADR-0008 "
         "as ratified**", "Every cell has an Observer (ADR-0037 D-0037-1, fleet-wide)",
         "**No safety theorem.** Each cell's detection falls to the correlator, so one compromised correlator blinds "
         "every cell; the bounded injection blast radius is lost. Under ADR-0039, coupling has nothing per cell to "
         "couple to", "No participant changes type"],
        ["D-0038-2", "Declaration", "Correlators: 1 or more → 0", "Some Observer reads across cells",
         "**No safety theorem.** Cross-principal detection is lost: the fragmentation and multi-agent coordination "
         "cases (CR-3)", "No participant changes type"],
    ], size=14, accent="pink") + 12
    y += c.para(X0, y, W, "**Composition note (§7a).** D-0038-1 with D-0038-2 leaves no Observer at all: no theorem lost "
                "beyond the union, every detection claim lost, and in Build nothing promotes (ADR-0035 §5). In Run, "
                "D-0038-1 is usable only together with ADR-0039 D-0039-1, since §4 there forbids coupling to the "
                "correlator. **On the schema (R2):** \"none\" under theorems voided with the loss in prose, because "
                "ADR-0023 §6 has no properties-lost field (ADR-0037 finding 6; G7 item 40).", 14, "ink") + 40

    # ======================================================================== bottom cards
    w4 = (W - 3 * 24) / 4
    cards = [
        ("Monoculture (ToO §5.1; ADR-0016 §5)", [
            "An Observer should come from a **different model family** than the agents it watches; sharing a family is a "
            "shared blind spot.",
            "Since ADR-0037 the predicate has **one pair per cell** to cover: (`thinker`, `observer`).",
            "Seat distinctness is enforced where refusal stalls, at the tally and the declaration, never at grant "
            "(ADR-0035 §5, Proposed).",
        ], "pink", None, False),
        ("Cost of compromise, per seat", [
            "**Cell Observer**: deny, quarantine or evict inside one cell; one cell's detection lost.",
            "**Correlator**: deny, quarantine or evict inside its domain, attributed; cross-cell detection lost.",
            "**Any Observer**: a false denial costs availability, never safety. Any-of raises the false-denial rate with "
            "every Observer added.",
            "Collusion (an Observer that finds nothing) is not covered by any of this: ADR-0039 §5.",
        ], "red", None, False),
        ("Finding 1 · The correlator has inputs but no function", [
            "This record says what it reads and what it may do, **not what it looks for**: the probe-then-exploit "
            "signature, fragmented intent, a chain-depth term (CR-3).",
            "Detection engineering, deny-only, so it can be specified later without changing anything here.",
            "Open: G7 item 43. Its derived store crosses erasure units (finding 3, routed to ADR-0006).",
        ], "red", "open", True),
        ("Options not taken (ADR-0038 Options)", [
            "**An Observer quorum, each seat a BFT group**: rejected. A quorum is for grants; for denials it can only "
            "suppress an honest finding, and costs the most instances.",
            "**The correlator as a new seat kind**: rejected; its reach is the ACL.",
            "**The correlator as the only veto holder**: not taken; the cell Observer read the author's round in full.",
            "**Coupling decided here**: split to ADR-0039 (custodian, 09.28).",
        ], "grey", None, False),
    ]
    hs = [c.card(0, 0, w4, t, b, accent=a, status=s, draw=False, size=14) for t, b, a, s, _ in cards]
    hh = max(hs)
    for i, (t, b, a, s, dsh) in enumerate(cards):
        c.card(X0 + i * (w4 + 24), y, w4, t, b, accent=a, status=s, h=hh, size=14)
    y += hh + 30
    c.legend(X0, y, [("arrow", "pink", "read edge: a read authorization on the round topic (the ACL)"),
                     ("arrow", "green", "admits written to the round topic"),
                     ("line", "grey", "device boundary (fault domain)", "5 4"),
                     ("arrow", "red", "finding → deny, quarantine or evict", "7 5"),
                     ("arrow", "blue", "Vote(deny) on the veto roster")])
    return c
