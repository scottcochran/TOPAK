"""B10 — Rules of engagement live in three places (ADR-0067, Proposed, revised R1): standing rules in the one Cedar
floor, a mission's rules in a promoted Wasm bundle, and judgments about the world nowhere in the admit path; and the
floor gains a `federation` stage of fourteen forbids, none of them written."""
from lib import Canvas, STATUS, STATE_CC, text_width, wrap

ID, SLUG = "B10", "federation-floor-stage"

W = 3400


def row_cards(c, x, y, w, gap, specs, size=14):
    """A row of cards of equal height, measured over every card. specs: (title, body, accent, kwargs)."""
    n = len(specs)
    cw = (w - (n - 1) * gap) / n
    h = max(c.card(0, 0, cw, t, b, draw=False, size=size, status=k.get("status"), sub=k.get("sub"))
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


# custom pills: key -> (label, accent, dash)
CUSTOM = {
    "notwritten": ("Not written", "red", "2 3"),
    "notrouted": ("Not routed", "red", "2 3"),
    "nofloor": ("None: nothing here can be in force (§5)", "red", "2 3"),
    "overlay": ("An overlay, not the archetype ⟨Q11⟩", "grey", None),
}


def pill_w(key, extra=""):
    if key in CUSTOM:
        return text_width(CUSTOM[key][0], 11.5, True) + 18
    return text_width(STATUS[key][0] + (f" · {extra}" if extra else ""), 11.5, True) + 18


def draw_pill(c, x, y, key, extra=""):
    if key in CUSTOM:
        lab, acc, dash = CUSTOM[key]
        return c.pill(x, y, lab, acc, 11.5, dash=dash)
    return c.status(x, y, key, extra)


NW = "[[red|Not written]]"


def build():
    c = Canvas(ID, "Rules of engagement live in three places, and the floor gains a `federation` stage of fourteen "
               "forbids, none written",
               "ADR-0067 puts a mission's rules of engagement in three places: **standing rules in the one Cedar "
               "floor**, the same at every plane and every governor; **a mission's mechanical rules in a promoted "
               "bundle compiled to Wasm**, which can only refuse; and **judgments about the world nowhere in the admit "
               "path** (ADR-0007). The floor gains a stage, `federation`, after `workflow`: fourteen forbids, FD1 to "
               "FD14, each from the record it enforces, and two existing entries relaxed. **ADR-0067 is Proposed, an "
               "overlay and not the archetype. No entry is written as Cedar, gated or built, and since no floor is "
               "ratified, nothing here can be in force** (§5).",
               W, "ADR-0067 (Proposed, R1): provenance note, Status note, Decision §1–§7 (§1's table, §3's table), "
               "Options (the table), Consequences, Open obligations, History (R1); ADR-0059 §1, §2, §3 (its table), "
               "R1; ADR-0060 §2, §3; ADR-0062 §1, §2, §3 (its table), §5, §8; ADR-0063 §3, R1; ADR-0065 §1 (R1), §4; "
               "ADR-0066 §1, §2, §4, §5, §6; ADR-0007 (09.11 text, 09.12 acceptance); ADR-0030 §1 (its engine table); ToO rev 15 §3.1, "
               "§3.2, §7.10 (as ADR-0059 §3 quotes it); floor/proposed/README.md (Stages, The entries, What the schema "
               "gains, What the gates show); diagram B8 (the stages, the `emergency` and `workflow` conditions of "
               "`B10` and `R3`); mechanism/README.md (`topak-bundle`); the headers of spec/Federation.tla, "
               "Membership.tla, Intent.tla, Alone.tla, Outstanding.tla, PlaneClock.tla, Peer.tla and Release.tla, "
               "and the summary lines of each one's -results-, -proof-results- and -proof-cert-results-2026.11.10.txt",
               state=STATE_CC)
    X0, X1 = c.x0, c.x1
    WW = X1 - X0
    y = c.y

    # ================================================================== status strip
    c.text(X0, y + 15, "Status", 15, "faint", bold=True)
    px0 = X0 + 80
    px = px0
    for lab, key, extra in [
            ("ADR-0067", "proposed", "C1 · drafted 2026.11.10 · revised R1"),
            ("position", "overlay", ""),
            ("its sources, ADR-0059 to ADR-0066", "proposed", ""),
            ("stage `federation`, FD1 to FD14", "notwritten", ""),
            ("the relaxations of `B10` and `R3` (§4)", "notrouted", ""),
            ("a ratified floor", "nofloor", ""),
            ("the floor enforced today, `emergency`", "genprov", "ratified by no batch"),
            ("stage `workflow`, which it would follow", "proposed", "ADR-0054"),
            ("the stage at the reference", "notbuilt", "")]:
        lw = text_width(lab, 13.5, True) + 8
        pw = pill_w(key, extra)
        if px + lw + pw > X1:
            px = px0
            y += 34
        c.text(px, y + 15, lab, 13.5, "ink", bold=True)
        px += lw
        px += draw_pill(c, px, y, key, extra) + 26
    y += 42
    y += c.para(X0, y, WW, "**Proposed means nothing here is in force.** The custodian put two things: **rules of "
                "engagement as a promoted Wasm bundle ⟨5⟩**, and **the Cedar floor in force with them ⟨7⟩**; and "
                "answered that **one floor serves the whole tree ⟨Q8⟩** and that this is **an overlay ⟨Q11⟩**. Every "
                "other choice is the drafter's, and **the entry ids are placeholders**. **C1** applies: the entries "
                "are forbids on privileged paths, and two existing entries are relaxed, each of which routes as a "
                "relaxation (ToO §3.2). C2, C3 and C4 do not apply on the drafter's reading while this is an overlay. "
                "**R1** (2026.11.10) changed one entry, `FD10`, to follow ADR-0063 R1. One author, one day, and no "
                "policy text.", 14.5, "muted") + 34

    # ================================================================== band 1: three places
    y = band(c, X0, y, "Three places, and how two of them compose (§1)", status="proposed")
    top = y
    wl = 1960
    gl = 60
    wr = WW - wl - gl
    xr = X0 + wl + gl

    c.text(X0, top + 22, "admit ⟺ `floor_permit` ∧ ¬`bundle_deny`", 22, "teal", bold=True)
    c.para(X0 + 520, top + 2, wl - 520, "ADR-0030 §1, the mechanism constant. ADR-0059 §2 applies it at **every "
           "admit or permit, at any plane**: the floor's permit and no refusal from **any bundle on the chain**. "
           "A bundle is never asked whether to grant.", 14, "muted")
    ptop = top + 70
    S = 13.5
    cs, cf, cb = 330, 440, 440
    gp = 125
    co = wl - cs - cf - cb - 3 * gp
    xs_ = X0
    xf = xs_ + cs + gp
    xb = xf + cf + gp
    xo = xb + cb + gp

    SRC1 = ("At a plane: an admit", [
        "**At any plane**, commanded or autonomous, ordered by its replicas (ADR-0059 §2).",
        "An `ordered` entry is admitted here, before its effect (ADR-0062 §3).",
    ], "violet")
    SRC2 = ("On a vehicle: a governor's permit", [
        "**The stack asks; the governor permits** each `local` entry under the lease, and counts it, with no "
        "further round (ADR-0062 §1, §2).",
        "The stack is Byzantine. The governor is mechanism.",
    ], "teal")
    FL = ("The Cedar floor: one for the whole tree ⟨Q8⟩", [
        "**Standing rules that hold for every mission** (§1).",
        "**Every charter carries the root's floor digest**; planes differ by bundles only (ADR-0059 §2).",
        "**It is the verified object, and no bundle can weaken it** (§1).",
        "**Evaluated in Cedar** at every plane and on every governor (ADR-0062 §1).",
        "`floor_permit` **holds only on Allow with no evaluation error**; any error is a deny (ADR-0030 §1).",
        "**A floor deny short-circuits**: the bundles are consulted only on a floor permit (ADR-0030 §1).",
    ], "teal")
    BU = ("A mission's rules: promoted bundles on the chain, in Wasm ⟨5⟩", [
        "**Voted by digest**: a bundle is a new artifact, so bringing one into force is a promotion (ADR-0059 §3).",
        "**Appended by each plane that adds one**, never asked whether to grant (ADR-0059 §2).",
        "**Able only to refuse**: `bundle_deny` holds when it denies, errs, is absent or cannot be reached "
        "(ADR-0030 §1).",
        "**Counts only from the revision the lease names** (ADR-0030 §1).",
        "**Evaluated the same way at a plane and on a vehicle** (§1).",
    ], "amber")
    OUT1 = ("Admitted", ["The effect follows the admit (ADR-0062 §3)."], "teal")
    OUT2 = ("Permitted, and counted", ["Against the lease's exact count: the governor's own arithmetic over its "
                                       "own acts (ADR-0062 §2)."], "teal")

    hs1 = c.card(0, 0, cs, SRC1[0], SRC1[1], size=S, draw=False)
    hs2 = c.card(0, 0, cs, SRC2[0], SRC2[1], size=S, draw=False)
    hf = c.card(0, 0, cf, FL[0], FL[1], size=S, draw=False)
    hb = c.card(0, 0, cb, BU[0], BU[1], size=S, draw=False, status="proposed")
    ho1 = c.card(0, 0, co, OUT1[0], OUT1[1], size=S, draw=False)
    ho2 = c.card(0, 0, co, OUT2[0], OUT2[1], size=S, draw=False)
    H = max(hf, hb, hs1 + hs2 + 120, ho1 + ho2 + 120)
    lane1 = ptop + H * 0.27
    lane2 = ptop + H * 0.75
    c.card(xs_, lane1 - hs1 / 2, cs, SRC1[0], SRC1[1], accent=SRC1[2], size=S, tint=False)
    c.card(xs_, lane2 - hs2 / 2, cs, SRC2[0], SRC2[1], accent=SRC2[2], size=S, tint=False)
    c.card(xf, ptop, cf, FL[0], FL[1], accent="teal", size=S, h=H)
    c.card(xb, ptop, cb, BU[0], BU[1], accent="amber", size=S, h=H, status="proposed", status_extra="§2")
    c.card(xo, lane1 - ho1 / 2, co, OUT1[0], OUT1[1], accent="teal", size=S, tint=False)
    c.card(xo, lane2 - ho2 / 2, co, OUT2[0], OUT2[1], accent="teal", size=S, tint=False)
    for ly, acc in ((lane1, "violet"), (lane2, "teal")):
        c.arrow([(xs_ + cs, ly), (xf, ly)], acc, sw=2.4, label="request", lpos=0.5)
        c.arrow([(xf + cf, ly), (xb, ly)], "teal", sw=2.4, label="`floor_permit`", lpos=0.5)
        c.arrow([(xb + cb, ly), (xo, ly)], "teal", sw=2.4, label="¬`bundle_deny`", lpos=0.5)

    # refusals
    yref = ptop + H + 90
    REF = ("Refused", [
        "**By the floor**: any `forbid` satisfied, no `permit` matched, or any evaluation error (ADR-0030 §1). "
        "FD1 to FD14 would refuse here.",
        "**Or by any bundle on the chain**: it denies, errs, returns undefined, is absent or cannot be reached "
        "(ADR-0030 §1).",
    ], "red")
    wref = xb + cb - xf
    href = c.card(xf, yref, wref, REF[0], REF[1], accent="red", size=S, tint=False, dash="6 4")
    c.arrow([(xf + cf / 2, ptop + H), (xf + cf / 2, yref)], "red", dash="7 5", label="deny", lpos=0.5)
    c.arrow([(xb + cb / 2, ptop + H), (xb + cb / 2, yref)], "red", dash="7 5", label="refuse", lpos=0.5)

    # the third place: nowhere in the admit path
    rtop = yref + href + 80
    rpad = 30
    CL = ("A classifier: identification, intent, necessity, proportion", [
        "**A judgment about the world** (§6).",
        "**Rejected in the admit path** (Options; ADR-0007).",
    ], "grey")
    OB = ("An Observer's finding", [
        "**Classifier output enters only as a finding, and a finding may only subtract**: a trigger for deny, "
        "quarantine or eviction (ADR-0007).",
    ], "pink")
    NO = (None, [
        "**No arrow from here enters the admit path.** \"Some genuinely desirable policies become unexpressible at "
        "admit time and must be restated as detections\" (ADR-0007).",
        "**What these judgments decide is enforced by nothing in this set of records** (§6, band 6).",
    ], "red")
    wcl = 420
    wob = 470
    gx3 = 120
    wno = wl - 2 * rpad - wcl - wob - gx3 - 60
    hcl = c.card(0, 0, wcl, CL[0], CL[1], size=S, draw=False)
    hob = c.card(0, 0, wob, OB[0], OB[1], size=S, draw=False)
    hno = c.card(0, 0, wno, NO[0], NO[1], size=S, draw=False, bullets=True)
    hr = max(hcl, hob, hno)
    c.region(X0, rtop, wl, hr + 2 * rpad + 20, "Rules that need a judgment about the world: nowhere in the admit "
             "path (§1)", "grey", dash="10 6")
    ry = rtop + rpad + 10
    xcl = X0 + rpad
    xob = xcl + wcl + gx3
    xno = xob + wob + 60
    c.card(xcl, ry, wcl, CL[0], CL[1], accent="grey", size=S, h=hr, tint=False)
    c.card(xob, ry, wob, OB[0], OB[1], accent="pink", size=S, h=hr)
    c.card(xno, ry, wno, NO[0], NO[1], accent="red", size=S, h=hr, tint=False, dash="6 4")
    c.arrow([(xcl + wcl, ry + hr / 2), (xob, ry + hr / 2)], "pink", dash="7 5", label="a finding", lpos=0.5)
    # the finding may only subtract: up to the refusal
    fx = xob + wob / 2
    if fx < xf + 20:
        fx = xf + 40
    c.arrow([(fx, ry), (fx, yref + href)], "pink", dash="7 5", label="may only subtract", lpos=0.75)
    bot_l = rtop + hr + 2 * rpad + 20

    # right: §1's table and ADR-0007
    c.text(xr, top + 16, "**§1's table, whole**", 16, "ink")
    cols = [("Part of the rules", wr * 0.30, {"bold": True}), ("Where it lives", wr * 0.36),
            ("Why there", wr * 0.34)]
    t1 = c.table(xr, top + 32, cols, [
        {"cells": ["Standing rules that hold for every mission",
                   "**The Cedar floor**, the same at every plane and every governor (ADR-0059 §2) ⟨Q8⟩",
                   "It is the verified object, and no bundle can weaken it"], "accent": "teal"},
        {"cells": ["A mission's rules that can be lifted mechanically", "**A promoted bundle, compiled to Wasm**",
                   "Voted by digest, able only to refuse, and evaluated the same way at a plane and on a vehicle"],
         "accent": "amber"},
        {"cells": ["Rules that need a judgment about the world", "**Nowhere in the admit path**",
                   "ADR-0007: no semantic judgment is an enabling condition"], "accent": "grey"},
    ], size=14.5, accent="teal")
    ty = top + 32 + t1 + 26
    br = stack(c, xr, ty, wr, [
        ("ADR-0007, as accepted (genesis, 2026.09.12)", [
            "\"**Syntactic lift** (mechanical, total extraction from a constrained call interface) **is permitted in "
            "any zone. Semantic lift is prohibited in the admit path.** Classifier output enters as an Observer "
            "finding, and findings may only subtract authority, never add it.\"",
            "\"A classifier is usable as a trigger for deny, quarantine, or eviction.\"",
            "Extension (09.12): totality, non-vacuity and discrimination gates **run on the floor itself**, not only "
            "on operational bundles. §7 asks them of this stage.",
            "ADR-0067 states the rule as \"no semantic judgment is an enabling condition\", and its provenance note "
            "says ADR-0007 was taken as ToO and the proposal give it, not re-read.",
        ], "blue", {"status": "accepted"}),
        ("Why the floor does not carry a mission's rules (Options)", [
            "**The floor would change with every mission**, and it is the one artifact that is verified.",
            "**Rules enforced by the stack are not rules.** The stack is Byzantine.",
        ], "grey", {"tint": False}),
    ], gap=18, size=14)
    c.text(xr, br + 40, "**ADR-0030 §1's engine table, whole**: where the bundle tier runs a sidecar and a local "
           "engine", 15, "ink")
    he = c.table(xr, br + 54, [("The sidecar…", wr * 0.62), ("Result", wr * 0.38)], [
        ["returns `true` from the lease's revision", "[[teal|Allow]]"],
        ["returns anything else from the lease's revision", "[[red|Refuse.]] Authoritative: no fallback"],
        ["is unreachable, errors, times out, or serves another revision",
         "The local engine decides **iff** it holds the lease's revision"],
        ["— and the local engine holds no such revision", "[[red|Refuse]]: the bundle \"cannot be reached\""],
    ], size=14, accent="grey")
    hn = c.para(xr, br + 54 + he + 10, wr, "**At an autonomous plane and on a governor, §2 leaves only the local "
                "engine.** On this diagram's reading, the last two rows are then the whole tier: the local engine "
                "decides iff it holds the lease's revision, and otherwise the bundle refuses. Every admit records "
                "which engine decided (ADR-0030 §1).", 14, "muted")
    br = br + 54 + he + 10 + hn
    y = max(bot_l, br) + 80

    # ================================================================== band 2: §2
    y = band(c, X0, y, "A mission's rules are a promoted Wasm bundle ⟨5⟩ (§2)", status="proposed")
    wexp = 1080
    gx = 50
    EXP = ("A bundle can express what a mechanical lift can supply", [
        "**Areas.**",
        "**Time windows**, as ranges of the plane's ticks (ADR-0064).",
        "**Which entries a seat kind may use.**",
        "**Counts**, within a vehicle or across vehicles.",
        "**Which entries are `ordered`** (ADR-0062 §3): the bundle marks an entry `ordered` where the tally wants "
        "agreement across vehicles, and the archetype marks none ⟨Q20⟩.",
        "**A refusal of a report to a peer topic**, by seat kind, rate or label.",
        "**A refusal of an entry once the stack has read a peer's report in the clear** (ADR-0065 §3).",
        "**Lists that come from a declared source and carry its label.**",
    ], "amber")
    hexp = c.card(X0, y, wexp, EXP[0], EXP[1], accent="amber", size=14, status="proposed", status_extra="§2")
    xr2 = X0 + wexp + gx
    wr2 = X1 - xr2
    h2a = row_cards(c, xr2, y, wr2, 24, [
        ("Tightening: by promotion, or faster by a narrower intent", [
            "**A commanded plane tightens by promoting a bundle**, which is appended (ADR-0059 §2).",
            "**A commander tightens faster** by narrowing a value in the next intent (ADR-0060 §2): an ordered admit "
            "signed by one operator, which adds nothing the tally did not vote (ADR-0059 §3's table).",
        ], "green", {}),
        ("Loosening needs a promotion", [
            "**At a plane whose charter allows it**, and otherwise it goes up the tree.",
            "**That asymmetry is the one the corpus already has between subtraction and grant**: \"adding takes a "
            "quorum, and denying is local\" (ToO §7.10, as ADR-0059 §3 quotes it).",
        ], "blue", {}),
    ], size=14)
    h2b = row_cards(c, xr2, y + h2a + 24, wr2, 24, [
        ("At an autonomous plane and on a governor, the Wasm engine is the only one", [
            "**The reference has the path**: `topak-bundle` loads a signed bundle into an in-process engine bound "
            "to the lease's revision, as the fallback when the sidecar cannot answer (`mechanism/README.md`: \"local "
            "OPA WASM fallback bound to the lease's bundle\").",
            "**Not taken: a sidecar on the vehicle** (Options). Nothing of this record is built on a vehicle.",
        ], "teal", {"tint": False}),
        ("A stale bundle on a vehicle is safe in the direction that matters", [
            "**It can refuse too much, and cannot allow what the floor refuses** (ToO §3.1: stale bundles are "
            "monotone-safe).",
            "The floor is consulted first, and a floor deny is never sent to a bundle (ADR-0030 §1).",
        ], "green", {}),
    ], size=14)
    y = max(y + hexp, y + h2a + 24 + h2b) + 80

    # ================================================================== band 3: §3's table
    y = band(c, X0, y, "The floor gains a `federation` stage ⟨7⟩: fourteen forbids, none written (§3)",
             status="proposed", extra="every entry: not written")
    mono = {"mono": True}
    wt = 2420
    cols = [("Id (a placeholder)", 330, mono), ("Kind", 86), ("Says", 900), ("From", 170), ("State", 140),
            ("A module property for the same section: this diagram's cross-reference, not the floor", wt - 1626)]
    F = "[[red|forbid]]"
    rows = [
        ["FD1-charter-narrows", F, "No seating of a plane, and no intent, whose charter exceeds its bound in any "
         "field", "ADR-0059 §1", NW, "`CharterNarrows` · Federation (§1)"],
        ["FD2-lease-within-charter", F, "No grant whose lease exceeds the granting plane's charter: an entry outside "
         "its alphabet, a `ttl` above its `ttlMax`, a count above its `countMax`, an expiry after its own",
         "ADR-0059 §1", NW, ""],
        ["FD3-budget-spent", F, "No grant, and no seating of a plane, once the charter's budget is spent",
         "ADR-0059 §1", NW, "`BudgetConserved` · Federation (§1), stated for a subtree with no captured plane"],
        ["FD4-autonomous-adds-nothing", F, "At an autonomous plane: no promotion, no seating, no operator's request, "
         "no bundle change, no grant but a node's lease under a live intent, and no change of membership but a step "
         "of its charter's schedule", "ADR-0060 §3", NW, "`AutonomousAddsNothing` · Intent (§3)"],
        ["FD5-irreversible-release-only", F, "No `Actuate` of an irreversible entry under a seat whose kind is not "
         "`release`", "ADR-0066 §1", NW, ""],
        ["FD6-irreversible-from-commanded", F, "No admit of an irreversible entry without a commanded plane's commit "
         "certificate for that act, unused and fresh", "ADR-0066 §4", NW,
         "`OrderedAtCommand`, `UsedOnce`, `NoOlderThanDeclared`, `OrderedInContact` · Release (§4)"],
        ["FD7-local-marked", F, "No permit by a governor of an entry its bundle revision does not mark `local`, and "
         "none of an irreversible entry", "ADR-0062 §3", NW, ""],
        ["FD8-local-bounds", F, "No permit by a governor with the lease's count spent, past its `ttl` in ticks, or "
         "under a lease that has ended", "ADR-0062 §2, §7", NW,
         "`EveryEffectHasALease` · Intent (ADR-0062 §2); `ExpiryGrantsNothing` · Alone (§7)"],
        ["FD9-release-seating", F, "No `release` seating of a key that is not on the anchor-issued roster, none at an "
         "autonomous plane, and none at a plane whose charter lacks `release`", "ADR-0066 §2", NW, ""],
        {"cells": ["FD10-outstanding-bound", F, "At an autonomous plane: no grant and no `ordered` admit that would "
                   "take the outstanding charge to `K_up`. At a governor: no lease accepted, **and no `ordered` entry "
                   "carried out ⟨R1⟩**, that would take its own to `K_up`", "ADR-0063 §3", NW,
                   "`HavocPlaneBoundedInEffects` · Outstanding (§3)"], "accent": "amber"},
        ["FD11-alone-permits-nothing", F, "No permit by a governor whose vehicle is alone, but the beacon within its "
         "count", "ADR-0062 §5", NW, "`AlonePermitsNothing` · Alone (§5)"],
        ["FD12-topic-declared", F, "No report to a peer topic the promoted mesh does not declare for the seat, and "
         "none that names a recipient", "ADR-0065 §4", NW, "`SendWithinTopics` · Peer (§2, §4)"],
        ["FD13-step-in-schedule", F, "No step of membership that the charter's schedule does not hold, and none below "
         "its capture floor", "ADR-0061 §3", NW, "`StepInSchedule`, `StepAtFloor` · Membership (its header covers "
         "§1, §3, §4; the properties name no section)"],
        ["FD14-count-within-K", F, "No lease whose count exceeds `K`, or its charter's `countMax`", "ADR-0062 §8",
         NW, ""],
    ]
    ht = c.table(X0, y, cols, rows, size=14, accent="red")
    c.para(X0, y + ht + 12, wt, "**Every new entry subtracts** (§3). The stage would follow `workflow` in "
           "`floor/proposed/README.md`. The amber row is the one R1 changed: `FD10`'s governor clause follows ADR-0063 "
           "R1, which charges an `ordered` entry to the governor's own account as a lease is (Outstanding.tla's "
           "finding 1, `M_ORDEREDFREE`). No other entry changed (History).", 14, "muted")
    tb = y + ht + 12 + 60
    xm = X0 + wt + 50
    wm = X1 - xm
    bm = stack(c, xm, y, wm, [
        ("How to read the last column", [
            "**A module is not the floor.** Each states a property of a model of its own record, at small constants. "
            "None reads Cedar text, and none shows that an entry, once written, says what its row says. **It proves "
            "nothing about the stage.**",
            "**Matched by section only**: a cell is filled where the property's header names the record and section "
            "in \"From\". It is empty where no module's property does.",
            "**FD2**: `LeaseWithinChain` (Federation) is about the same check, and states ADR-0059 §4, §5, not §1, "
            "so it is not listed.",
            "**Release.tla assumes no floor**: \"the floor's refusals (FD5, FD6 and FD9, ADR-0067) are a second check "
            "in series that is not assumed here\", so its properties rest on the interlock alone.",
        ], "grey", {"tint": False}),
    ], size=13.5)
    c.text(xm, bm + 30, "**The eight modules, as their 2026.11.10 result files give them**", 15, "ink")
    mcols = [("Module", wm * 0.2, mono), ("Record", wm * 0.17), ("TLC rows checked", wm * 0.2),
             ("TLAPS obligations proved", wm * 0.2),
             ("Certified, with this many LS4 temporal steps that no checker confirms", wm * 0.23)]
    mrows = [
        ["Federation", "ADR-0059", "41, all as expected", "892", "7"],
        ["Membership", "ADR-0061", "28, all as expected", "495", "6"],
        ["Intent", "ADR-0060", "35, all as expected", "677", "5"],
        ["Alone", "ADR-0062", "47, all as expected", "263", "6"],
        ["Outstanding", "ADR-0063", "40, all as expected", "1871", "6"],
        ["PlaneClock", "ADR-0064", "38, all as expected", "535", "6"],
        ["Peer", "ADR-0065", "25, all as expected", "254", "6"],
        ["Release", "ADR-0066", "67, all as expected", "613", "10"],
    ]
    hm = c.table(xm, bm + 44, mcols, mrows, size=13.5, accent="grey")
    y = max(tb, bm + 44 + hm) + 80

    # ================================================================== band 4: the stage order
    y = band(c, X0, y, "Where the stage would sit: genesis draft → `labels` → `control` → `emergency` → `workflow` → "
             "`federation` (§3; `floor/proposed/README.md`)", status="proposed")
    ag = 120
    cw = (WW - 5 * ag) / 6
    xs = [X0 + i * (cw + ag) for i in range(6)]
    stages = [
        ("`floor/genesis-floor.cedar`", "violet", "draft", "", "the text the stages are built from", [
            "**17 policies · 62 cases.**",
            "Not edited by the build.",
        ]),
        ("Stage `labels`", "teal", None, "", "gated 2026.10.04", [
            "**Records:** ADR-0047, with ADR-0048 and ADR-0049 (ADR-0041 A1; ADR-0030 A2).",
            "**Adds** `R5`, `R6`, `R7`: three forbids on `Actuate`.",
            "**20 policies · 74 cases.**",
        ]),
        ("Stage `control`", "blue", None, "", "gated 2026.10.04", [
            "**Records:** + ADR-0050 (ADR-0041 A3).",
            "**Adds** six actions and `C1` to `C9` for an `operator` seat.",
            "**29 policies · 106 cases.**",
        ]),
        ("Stage `emergency`: the floor enforced today", "green", "genprov", "", "gated 2026.10.04", [
            "**Records:** + ADR-0052 (ADR-0041 A2).",
            "**Removes** `X1-break-glass`; `B10` admits the `emergency` kind for `Actuate`.",
            "**28 policies · 107 cases.** Ratified by no batch (B8).",
        ]),
        ("Stage `workflow`: not in force", "amber", "proposed", "ADR-0054", "gated 2026.10.08", [
            "**Records:** + ADR-0054 (ADR-0041 A4; Proposed).",
            "**Adds** `Route`, `R8`, `R9`; `R3` couples the `orchestrator` kind and covers `Route`.",
            "**30 policies · 123 cases.** The reference links it since 2026.10.08.",
        ]),
        ("Stage `federation`: not written", "amber", "proposed", "ADR-0067", "no build, no gate run, no cases", [
            "**Records:** + ADR-0067, with ADR-0059 to ADR-0066 as the sources of its entries (all Proposed).",
            "**Would add** FD1 to FD14, fourteen forbids, and **relax** `B10` and `R3` (§4).",
            "**Policies · cases: none.** No Cedar is written (provenance note).",
        ]),
    ]
    hs = max(c.card(0, 0, cw, t, b, size=14, status=s, status_extra=e, sub=sub, draw=False)
             for t, a, s, e, sub, b in stages)
    for i, (x, (t, a, s, e, sub, b)) in enumerate(zip(xs, stages)):
        last = i == 5
        c.card(x, y, cw, t, b, accent=a, size=14, status=s, status_extra=e, sub=sub, h=hs,
               tint=not last, dash="2 3" if last else None)
        if last:
            nt = len(wrap(t, cw - 32, 16, bold=True))
            nsub = len(wrap(sub, cw - 32, 13))
            py = y + 16 + nt * 22 + nsub * round(13 * 1.4, 1) + 2 + 2
            c.pill(x + 16 + pill_w(s, e) + 10, py, "Not written", "red", 11.5, dash="2 3")
    ay = y + 70
    steps = [("+3 forbids\n(ADR-0041 A1)", "teal"), ("+9 control entries\n(ADR-0041 A3)", "blue"),
             ("−1 permit, `B10` amended\n(ADR-0041 A2)", "green"), ("`Route`, `R8`, `R9`;\n`R3` widened (A4)", "amber"),
             ("+14 forbids;\n`B10`, `R3` relaxed", "amber")]
    for i, (lab, acc) in enumerate(steps):
        c.arrow([(xs[i] + cw, ay), (xs[i + 1], ay)], acc, sw=2.6)
        c.label(xs[i] + cw + ag / 2, ay + 56, lab, acc, 12.5, maxw=ag - 4)
    y += hs + 20
    y += c.para(X0, y, WW, "**Each stage is the previous one plus the entries one batch of records asks for**, so a "
                "stage can be adopted without the ones after it (`floor/proposed/README.md`). **How a stage is made "
                "and gated**: `build.py` writes the stage's schema, floor and cases; `cedar validate` and `cedar "
                "run-tests`; then `run-gates.py` drives the genesis gate runner unchanged and adds routing controls for "
                "the new entries, each weakened candidate classed a relaxation and each strengthened one a tightening. "
                "**For `federation` none of this has run.** The README also says of every stage: **the floor trusts "
                "its inputs**, the facts the lift supplies.", 14.5, "muted") + 80

    # ================================================================== band 5: §4
    y = band(c, X0, y, "Two existing entries are relaxed, and the schema grows (§4)", status="proposed",
             extra="both relaxations not routed")
    wa = 1900
    gx = 50
    xb5 = X0 + wa + gx
    wb5 = X1 - xb5
    c.text(X0, y + 16, "**The two relaxations**: each routes as one, an anchor issuance **and** a promotion (ToO §3.2)",
           16, "ink")
    rcols = [("Entry", 250, mono), ("As the `emergency` stage has it (enforced today)", 400),
             ("`workflow` (Proposed)", 270), ("As ADR-0067 §4 relaxes it", 400), ("Why", 380),
             ("Routed", wa - 1700)]
    hr5 = c.table(X0, y + 32, rcols, [
        {"cells": ["B10-only-thinkers-author", "forbid `Draft` `Invoke` `Submit` `Actuate` · `principal.kind != "
                   "\"thinker\"` ∧ `!(principal.kind == \"emergency\" && action == Actuate)`", "unchanged",
                   "**Gains an exception for a `release` seat's `Actuate`**, as it has for an `emergency` seat",
                   "A `release` seat, held by a person at a commanded plane, is the only kind that reaches an "
                   "irreversible entry (ADR-0066 §1, §2, §6)", "[[red|Not routed]]"], "accent": "red"},
        {"cells": ["R3-observer-live", "forbid `Actuate` `Report` · `principal.kind == \"thinker\"` ∧ "
                   "`!context.observerLive`", "covers `Route`, and couples the `orchestrator` kind",
                   "**Scoped to admits a plane makes**, with a `local` entry covered at its lease's grant",
                   "ADR-0062 §8: a lease's count is at most `K`, and the next lease waits for the Observer to read "
                   "the last to its seal. The refusal mid-lease is given up", "[[red|Not routed]]"], "accent": "red"},
    ], size=14, accent="red")
    pn = c.para(X0, y + 32 + hr5 + 12, wa, "The `emergency` and `workflow` conditions are as B8 draws them from the "
                "stage files. ADR-0067 states each relaxation in words; neither is written as Cedar. \"**Two "
                "relaxations** of entries the floor already has\" is among its Negative consequences.", 14, "muted")
    c.text(xb5, y + 16, "**The schema gains** (§4)", 16, "ink")
    scols = [("Addition", wb5 * 0.42), ("Entries that read it (this diagram's reading of §3)", wb5 * 0.58)]
    hsch = c.table(xb5, y + 32, scols, [
        ["the seat kind `release`", "`FD5`, `FD9`; `B10`'s exception"],
        ["the entity `Plane`, with its charter and kind", "`FD1`–`FD4`, `FD9`, `FD10`, `FD13`, `FD14`"],
        ["the entity `Topic`", "`FD12`"],
        ["`effect` on an entry: class, `local` or `ordered`, extent, beacon (ADR-0062 §3)",
         "`FD5`–`FD7`, `FD10`, `FD11`"],
        ["Run context: who is permitting", "`FD7`, `FD8`, `FD10`, `FD11`; `R3` as relaxed"],
        ["Run context: whether the vehicle hears its plane", "`FD11`"],
        ["Run context: whether the count is spent", "`FD8`"],
        ["Run context: the outstanding charge", "`FD10`"],
        ["Run context: the tick", "`FD6` (fresh), `FD8` (`ttl` in ticks)"],
    ], size=14, accent="amber")
    la = y + 32 + hsch
    sy = y + 32 + hr5 + 12 + pn + 24
    hl = row_cards(c, X0, sy, wa, 24, [
        ("The lift supplies these, and the floor trusts its inputs", [
            "As `floor/proposed/README.md` says of every stage: the facts are the lift's, and no policy computes "
            "them.",
        ], "teal", {}),
        ("On a vehicle the lift is the governor's", [
            "It **lifts its own facts**: elapsed time, position, the lease's count, an entry's extent (ADR-0062 §1). "
            "**So the floor there trusts what one component measures** (Consequences).",
        ], "red", {"tint": False}),
    ], size=14)
    y = max(la, sy + hl) + 80

    # ================================================================== band 6: §5, §6
    y = band(c, X0, y, "\"In force\" is a precondition no record here can meet (§5), and four judgments no policy "
             "expresses (§6)", status="proposed")
    w5 = 1060
    g6 = 50
    b5 = stack(c, X0, y, w5, [
        ("No floor text is ratified (§5)", [
            "**The floor is ratified when a bootstrap reviewer finds it fit, and no test for fitness is written** "
            "(G11 §2.2 and item 87; ADR-0029 A4, as §5 cites them).",
            "**So nothing ADR-0067 adds can be in force until a floor is ratified**, whatever is written or gated of it (Consequences).",
            "**For this stage, whether the standing rules are the right ones is a legal judgment as much as a "
            "technical one.**",
            "**A grant seat with that named role** is suggested (drafter's suggestion).",
            "The floor enforced today, `emergency`, is genesis-provisional: gated, pinned and enforced, ratified by "
            "no batch (ADR-0030 A3; B8).",
        ], "red", {"tint": False, "dash": "6 4"}),
    ], size=14)
    x6 = X0 + w5 + g6
    w6 = X1 - x6
    c.text(x6, y + 16, "**Identification, intent, necessity and proportion are judgments about the world** (§6). "
           "Each is enforced by nothing in this set of records.", 16, "ink")
    jy = y + 34
    hj = row_cards(c, x6, jy, w6, 20, [
        (j, ["A judgment about the world. **No policy here expresses it.**"], "red", {"tint": False, "dash": "6 4"})
        for j in ("Identification", "Intent", "Necessity", "Proportion")], size=14)
    jy2 = jy + hj + 24
    hj2 = row_cards(c, x6, jy2, w6, 24, [
        ("For an irreversible effect: the person at the `release` seat", [
            "**Their judgment** (ADR-0066 §5). The mechanism records who acted, on what, through which vehicle and "
            "when; **not why, and it checks none of it**.",
            "It \"cannot tell a person from a program holding the person's key\" (ToO §3.3, as ADR-0066 §5 quotes "
            "it).",
        ], "brown", {}),
        ("For everything else: at most an Observer's objection, after the fact", [
            "**A classifier's output enters the system only as a finding, and a finding may subtract authority and "
            "never add it** (ADR-0007; ToO §2.2).",
            "**Negative consequence**: the parts of a mission's rules that matter most are enforced by nothing here.",
        ], "pink", {}),
    ], size=14)
    y = max(b5, jy2 + hj2) + 80

    # ================================================================== band 7: ratification, options
    y = band(c, X0, y, "Ratification condition, item by item (§7): none met", status="proposed")
    wq = 2000
    qcols = [("Condition (§7)", 700, {"bold": False}), ("State", 150), ("What stands today", wq - 850)]
    NM = "[[red|Not met]]"
    hq = c.table(X0, y, qcols, [
        ["**ADR-0059 to ADR-0066 are ratified first**, or with this record, each for the entries it is the source of",
         NM, "All eight are Proposed, 2026.11.10, revised R1. Each has a module and proof module of its own (band 3)"],
        ["**The entries are written in Cedar and pass the three gates**: totality, non-vacuity and discrimination, as "
         "every stage does", NM, "**The record's own words: \"Not met: no entry is written.\"** No build, no "
         "validation, no cases, no gate run"],
        ["**The stage is shown monotone in what a vehicle has received from its peers** (ADR-0065 §1), as the label "
         "forbids are in `clearSet`", NM, "No stage to show it of. Peer.tla's `NarrowsInReceived` states \"the "
         "monotonicity ADR-0067 §7 asks the stage to show\" **of a model, not of Cedar**. ADR-0065 §1 ⟨R1⟩ now "
         "ranges over items a peer **originates**, since a relayed lease does enable a permit; §7's wording is the "
         "unrevised one"],
        ["**The two relaxations are routed** as ToO §3.2 has a relaxation routed", NM,
         "Neither is written, so neither has been classed by the routing analysis or routed"],
        ["**A floor is ratified**, which is ADR-0029 A4's and not this record's", NM,
         "No floor text is ratified, and floor fitness has no test (§5)"],
        ["**A reader who is not the drafter** (ADR-0029 A2)", NM, "\"One author, one day, and no policy text\" "
                                                                   "(Consequences)"],
    ], size=14, accent="red")
    xo7 = X0 + wq + 50
    wo7 = X1 - xo7
    c.text(xo7, y - 8, "**Options considered, whole**", 16, "ink")
    ho7 = c.table(xo7, y + 8, [("Option", wo7 * 0.38, {"bold": True}), ("Disposition", wo7 * 0.62)], [
        {"cells": ["All of a mission's rules in the floor", "[[red|Rejected.]] The floor would change with every "
                   "mission, and it is the one artifact that is verified"], "accent": "red"},
        {"cells": ["A mission's rules through a sidecar on the vehicle", "[[grey|Not taken.]] The in-process Wasm "
                   "engine is the reference's fallback and the only engine a vehicle needs"], "accent": "grey"},
        {"cells": ["A classifier in the admit path, for identification or proportion", "[[red|Rejected]] by "
                   "ADR-0007"], "accent": "red"},
        {"cells": ["A floor per plane", "[[grey|Not taken]] ⟨Q8⟩ (ADR-0059 §2)"], "accent": "grey"},
        {"cells": ["Rules enforced by the stack", "[[red|Not a rule.]] The stack is Byzantine"], "accent": "red"},
    ], size=14, accent="grey")
    y = max(y + hq, y + 8 + ho7) + 60

    g8 = 40
    w8 = (WW - 2 * g8) / 3
    x8 = [X0 + i * (w8 + g8) for i in range(3)]
    h8 = max(c.card(0, 0, w8, t, b, size=14, draw=False, status=st)
             for t, b, st in [
                 ("Consequences: positive", [
                     "**A mission's rules are voted by digest and can only refuse**, on a vehicle as at a plane.",
                     "**Fourteen entries, all forbids.**",
                     "**What cannot be enforced is said**, and not left to be assumed."], None),
                 ("Consequences: negative", [
                     "**The parts of a mission's rules that matter most are enforced by nothing here** (§6).",
                     "**Nothing is in force** until a floor is, and floor fitness has no test (§5).",
                     "**Two relaxations** of entries the floor already has.",
                     "**The governor is the lift on a vehicle**, so the floor there trusts what one component "
                     "measures.",
                     "**One author, one day, and no policy text.**"], None),
                 ("Open obligations", [
                     "**The entries in Cedar, the gates, and the monotonicity check** (§7).",
                     "**A captured vehicle discloses the rules it carries** (the NATO reading, F3), and nothing says "
                     "whether a bundle or an envelope carries `restricted`.",
                     "**Sibling planes under one parent**: a forbid that their envelopes are disjoint, or the overlap "
                     "declared (the NATO reading, N1).",
                     "**Who judges that the standing rules are the right ones** (§5)."], "open")])
    c.card(x8[0], y, w8, "Consequences: positive", [
        "**A mission's rules are voted by digest and can only refuse**, on a vehicle as at a plane.",
        "**Fourteen entries, all forbids.**",
        "**What cannot be enforced is said**, and not left to be assumed."], accent="green", size=14, h=h8)
    c.card(x8[1], y, w8, "Consequences: negative", [
        "**The parts of a mission's rules that matter most are enforced by nothing here** (§6).",
        "**Nothing is in force** until a floor is, and floor fitness has no test (§5).",
        "**Two relaxations** of entries the floor already has.",
        "**The governor is the lift on a vehicle**, so the floor there trusts what one component measures.",
        "**One author, one day, and no policy text.**"], accent="red", size=14, h=h8, tint=False)
    c.card(x8[2], y, w8, "Open obligations", [
        "**The entries in Cedar, the gates, and the monotonicity check** (§7).",
        "**A captured vehicle discloses the rules it carries** (the NATO reading, F3), and nothing says whether a "
        "bundle or an envelope carries `restricted`.",
        "**Sibling planes under one parent**: a forbid that their envelopes are disjoint, or the overlap declared "
        "(the NATO reading, N1).",
        "**Who judges that the standing rules are the right ones** (§5)."], accent="red", size=14, h=h8,
        status="open", tint=False)
    y += h8 + 24
    c.para(X0, y, WW, "**Closes: nothing. Carries a debt against: nothing while this is an overlay.** Depends on "
           "ADR-0059 to ADR-0066 (what the entries forbid), ADR-0030 (bundles cannot add authority; the floor on a "
           "verified evaluator), ADR-0007 (no semantic judgment is a lift) and ADR-0058 (overlays; Proposed).", 14,
           "muted")
    return c
