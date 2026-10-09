"""D6 — A workflow may be a mesh: a budget makes it end, the activation is the unit, and the mechanism is the bus
(ADR-0055, Proposed; it widens ADR-0054, Proposed, drawn as C9)."""
import lib
from lib import Canvas, STATUS, text_width, fs

ID, SLUG = "D6", "mesh-mechanism-bus"

W = 3200

def _row(c, x, y, w, specs, gap=24, size=14):
    """Cards of equal height side by side. specs: (title, body, accent, kw). Returns the height."""
    n = len(specs)
    cw = (w - gap * (n - 1)) / n
    hh = max(c.card(0, 0, cw, t, b, draw=False, size=size, status=k.get("status"), sub=k.get("sub"),
                    bullets=k.get("bullets", True)) for t, b, _, k in specs)
    for i, (t, b, a, k) in enumerate(specs):
        c.card(x + i * (cw + gap), y, cw, t, b, accent=a, h=hh, size=size, **k)
    return hh


def _sub(c, x, y, s, accent="amber", size=17):
    c.text(x, y + size + 1, s, size, accent, bold=True)
    return size + 14


def _circle(c, cx, cy, r, label, accent, sub=None, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    c.add(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" {fs(accent + "-t", accent)} stroke-width="1.8"{d}/>',
          cy + r)
    c.text(cx, cy + (0 if sub else 5), label, 15, accent, "middle", bold=True)
    if sub:
        c.text(cx, cy + 17, sub, 12, "muted", "middle")


def build():
    c = Canvas(
        ID, "A workflow may be a mesh: a budget makes it end, the activation is the unit, and the mechanism is "
            "the bus",
        "ADR-0055 (Proposed 2026.10.07, at R2) widens ADR-0054 (Proposed; its DAG is drawn in C9). A workflow "
        "declares its kind; a `mesh` may have cycles and does not load without an **activation budget** the "
        "promotion votes on, every lease charged to it, the orchestrator's rounds included. A node may run more than "
        "once, so the unit of attributes, routes and findings becomes the **activation**, with its causal history. "
        "The mechanism tracks the work and the orchestrator keeps nothing between rounds; the events a mesh reacts "
        "to are entries in the consensus log. **Nothing here is in force**: `spec/Mesh.tla` is checked by TLC and "
        "has no proof, and the reference follows the record under ADR-0033 A16, pending, on a floor stage that is "
        "not in force (G11 §1.1, §3, §7 items 101, 102; ToO rev 15 §2.11).",
        W, "ADR-0055 (Proposed; provenance note, status note, Context, Decision §1–§11, Options considered, "
        "Consequences, Findings 1–6, Open obligations, History R1–R2); ADR-0054 (Proposed) Context, §1–§5, §7–§9, "
        "D-0054-1; ADR-0005 (Kafka is transport); ADR-0024 §2; ADR-0031 §2, A2; ADR-0035 §5 R8 (Proposed); "
        "ADR-0043 §1; ADR-0048 §2; ADR-0046 A1; ADR-0029 A2; ADR-0033 A16 (pending), \"Addendum — workflows and "
        "meshes\"; mechanism/GAPS-AND-ASSUMPTIONS.md I49 and its record row; spec/Mesh.tla (a5bc64953c38c9a9), mechanism/crates/topak-core/src/workflow.rs (Budget), "
        "spec/Mesh-rows.txt (23 rows), spec/Mesh-results-2026.10.07.txt (c58fa4b2e8bcc555); G11 §1.1, §2.9, §3 "
        "(results 9, 10), §5, §7 items 97, 101, 102; ToO rev 15 §2.11. The unrolling to depth N in the budget "
        "section is drawn here from Mesh.tla's Grant and OrchGrant at N = 6, as an illustration of ADR-0055 §2",
        state=lib.STATE_G11)
    X0, X1 = c.x0, c.x1
    Wd = X1 - X0
    y = c.y

    # ---------------------------------------------------------------- status strip
    c.text(X0, y + 15, "Status at G11", 15, "faint", bold=True)
    px0 = X0 + 140
    px = px0
    for lab, key, extra, pill in [
            ("ADR-0055", "proposed", "C1 · R2", None),
            ("ADR-0054", "proposed", "C1–C4 · drawn in C9", None),
            ("ADR-0055's dependent entries", "open", "not drafted (§11)", None),
            ("ADR-0035 §5", "proposed", "R8; the 2-colour entry not drafted", None),
            ("spec/Mesh.tla", None, "", ("Checked by TLC · no proof", "teal")),
            ("ADR-0033 A16", "draft", "pending", None),
            ("the reference at 11aaf6a", "built", "in part · on a floor stage not in force", None),
            ("fan-out joins, pools, parity seatings, T_wf, the gate's evidence", "notbuilt", "I49", None)]:
        lw = text_width(lab, 13.5, True) + 8
        plab = pill[0] if pill else STATUS[key][0] + (f" · {extra}" if extra else "")
        pw = text_width(plab, 11.5, True) + 18
        if px + lw + pw > X1:
            px = px0
            y += 34
        c.text(px, y + 15, lab, 13.5, "ink", bold=True)
        px += lw
        if pill:
            px += c.pill(px, y, pill[0], pill[1], 11.5) + 26
        else:
            px += c.status(px, y, key, extra) + 26
    y += 42
    y += c.para(X0, y, Wd, "**Every clause subtracts except the budgeted grant**, whose authority is the promotion's, "
                "as in ADR-0054; confirmation is required under C1 because the grant path now issues leases out of a "
                "budget (status note). **One author, one day**: drafted 2026.10.07 from a design discussion in which "
                "the custodian settled five things, ⟨M1⟩ to ⟨M5⟩ (a mesh, not only a DAG; promoted to Run and run by "
                "the mechanism; workers of alternate lineage; the orchestrator tracks and routes as needed; a record "
                "of its own beside ADR-0054). Every other choice is the drafter's, and **not reviewed by a reader "
                "other than the drafter** (§11; ADR-0029 A2).", 14.5, "muted") + 30

    # ================================================================ A. the module's mesh and one run of it
    y += c.heading(X0, y, "The mesh `Mesh.tla` checks, and one run of it: four activations, two orchestrator "
                          "rounds, the budget spent exactly", "amber", 21)
    top = y + 18
    lw_ = 900
    lx = X0
    # -- the promoted graph
    S = ("`s` · the root and the decision node", [
        "Thinker lineage **A**.",
        "**Its end is a decision event**: an orchestrator round chooses `e1` or `e2` among the edges whose guards "
        "hold (§3; ADR-0054 §3).",
        "It runs once per turn of the loop: `(s, 1)`, `(s, 2)`, …",
        "`e2`'s guard reads `s`'s outcome **in the triggering activation**, so the exit is enabled only when that "
        "activation ended `ok`.",
        "It is the root: its first activation is entered by the promotion, and charged like any other."])
    Wn = ("`w` · a worker on the loop", [
        "Thinker lineage **B**: `e1` and `e3` are clear, so `s` and `w` must differ (§5).",
        "Havoc: any outcome, and it may read untrusted content at any round."])
    Xn = ("`x` · the sink, outward", [
        "Entered by a handle edge, so its lineage is not checked.",
        "It reaches an outward entry, so the routing rule closes `e2` on an untrusted label (ADR-0054 §5)."])
    sw_, ww_ = 330, 300
    gx = 210
    hS = c.card(0, 0, sw_, S[0], S[1], draw=False, size=13.5)
    hW = c.card(0, 0, ww_, Wn[0], Wn[1], draw=False, size=13.5)
    hX = c.card(0, 0, ww_, Xn[0], Xn[1], draw=False, size=13.5)
    gv = 70
    hS = max(hS, hW + gv + hX)
    ny = top + 44
    sx, wx = lx + 28, lx + 28 + sw_ + gx
    c.card(sx, ny, sw_, S[0], S[1], accent="green", h=hS, size=13.5)
    c.card(wx, ny, ww_, Wn[0], Wn[1], accent="green", h=hW, size=13.5)
    xy = ny + hS - hX
    c.card(wx, xy, ww_, Xn[0], Xn[1], accent="green", h=hX, size=13.5, tint=False)
    y1, y3 = ny + 34, ny + hW - 34
    c.arrow([(sx + sw_, y1), (wx, y1)], "green", sw=2.4, label="`e1` · chosen · clear", lpos=0.5)
    c.arrow([(wx, y3), (sx + sw_, y3)], "green", sw=2.4, label="`e3` · computed · clear", lpos=0.5)
    c.arrow([(sx + sw_, xy + hX / 2), (wx, xy + hX / 2)], "grey", sw=2.4,
            label="`e2` · chosen · handle\nguard: `s` is `ok`", lpos=0.5)
    gy = ny + hS + 22
    gh = c.card(lx + 28, gy, lw_ - 56, "Promoted with it (§1, §2; `Mesh.tla`)", [
        "Kind `mesh`; **budget `N` = 6**, \"one loop and the exit\"; lineages {A, B}; the seatings. The promotion is "
        "gated on the clear edges alternating (`Alternates`).",
        "**Read it as Context's case**, a loop whose number of turns is decided at run time: draft and review until "
        "the review passes. `s`'s outcome is `ok` or `bad`; the exit `e2` is enabled only on `ok`.",
        "Every worker is havoc, the orchestrator routes any enabled chosen edge while its lease is live, and **a "
        "finding may land on any activation that has started, at any moment** (`Mesh.tla`, header)."],
        accent="amber", size=13.5)
    lbot = gy + gh + 22
    # -- one run
    rx = X0 + lw_ + 50
    rw = X1 - rx
    n6 = 6
    bg = 62
    bw = (rw - 44 - bg * (n6 - 1)) / n6
    run = [
        ("`(s, 1)`", "green", [
            "**Trigger**: none; the root, entered by the promotion.",
            "**History** {`(s,1)`}. Lineage A.",
            "Ends with outcome `bad`: `e2`'s guard is false, `e1` is enabled. **A decision event opens.**"]),
        ("Orchestrator round 1", "grey", [
            "Granted from the budget **for that event** (§6), and told the track, never bytes.",
            "`Route(e1)` names **activation `(s,1)` and round 1**. Checked again at apply; it consumes the event and "
            "ends the round."]),
        ("`(w, 1)`", "green", [
            "**Trigger** `(s,1)`, by `e1`, clear.",
            "**History** {`(w,1)`, `(s,1)`}. Lineage B ≠ A.",
            "Ends; its attributes are lifted once, and the computed `e3` is evaluated **in that same apply.**"]),
        ("`(s, 2)`", "green", [
            "**Trigger** `(w,1)`, by `e3`, clear; label joined from `(w,1)`'s.",
            "**History** {`(s,2)`, `(w,1)`, `(s,1)`}. Lineage A ≠ B.",
            "Ends `ok`. `e2`'s guard reads **`(s,2)`, not `s`'s latest value**. A second event opens."]),
        ("Orchestrator round 2", "grey", [
            "A new round for the new event: nothing is kept from round 1 (§6).",
            "`Route(e2)` names `(s,2)` and round 2. At apply: the event open, the guard true, no finding in the "
            "history, the label not untrusted."]),
        ("`(x, 1)`", "green", [
            "**Trigger** `(s,2)`, by `e2`, a handle edge.",
            "**An activation of the sink has ended: the workflow completes** (§8).",
            "Six leases of six. A seventh grant would be refused."]),
    ]
    bh = max(c.card(0, 0, bw, t, b, draw=False, size=13, tsize=15, bullets=False) for t, _, b in run)
    by = top + 44
    bxs = [rx + 22 + i * (bw + bg) for i in range(n6)]
    for bx_, (t, acc, b) in zip(bxs, run):
        c.card(bx_, by, bw, t, b, accent=acc, h=bh, size=13, tsize=15, bullets=False, tint=acc == "green")
    alab = ["event", "`e1`", "`e3`", "event", "`e2`"]
    for i in range(n6 - 1):
        ay = by + 40
        c.arrow([(bxs[i] + bw, ay), (bxs[i + 1], ay)], "grey" if alab[i] == "event" else "green", sw=2.2,
                label=alab[i], lpos=0.5, loff=(0, 22))
    # the budget strip
    uy = by + bh + 26
    c.text(rx + 22, uy + 15, "The budget, `N` = 6 (§2):", 14, "amber", bold=True)
    for i in range(n6):
        c.pill(bxs[i] + bw / 2, uy + 26, f"unit {i + 1} of 6", "amber", 12, anchor="middle")
    uy += 62
    uy += c.para(rx + 22, uy, rw - 44, "**One unit is one cell-round**: a worker's or the orchestrator's lease, with its "
                 "cell Observer's, which rides with its cell and is not charged separately (drafter's choice). "
                 "**The orchestrator's rounds are charged**: under `M_ORCHFREE` they are not, and `BudgetBound` breaks "
                 "(row `of1`). Had `(s,1)` and `(s,2)` both ended `bad`, the loop would turn twice and `(w, 2)` take unit "
                 "6; `(s, 3)` would then be ready, **its grant refused, and the workflow failed, never completed**.",
                 13.5, "ink") + 18
    # -- four other runs of the same mesh, two by two
    uy += _sub(c, rx + 22, uy, "Four other runs of the same mesh, each a witness TLC reached (§11; `Mesh-rows.txt`)",
               "teal", 16)
    var = [
        ("A finding against `(w, 1)`", [
            "**Ordered after `(s, 2)` began**, against the worker's round. `(s, 2)` is clean, and **every edge out of "
            "it is disabled**, because the finding is in its causal history (§3).",
            "A route decided before the finding is void at apply, `history`: witness `NeverVoidedByHistory` "
            "(`w_voidhistory`).",
            "`M_SOURCEONLY`, a finding closing only its own activation, breaks `NoActivationAfterFinding` (`so1`)."],
         "pink", {}),
        ("`(w, 1)` reads untrusted content", [
            "Its label is its `clearSet`, which only grows. `e3` is clear, so **`(s, 2)` is labelled untrusted**: "
            "`NeverTaintAroundLoop` (`w_taintloop`).",
            "`e2` enters the outward sink, so the routing rule disables it **for the rest of the run**; the workflow "
            "fails: `NeverExitClosedByTaint` (`w_exitclosed`).",
            "`M_FORGETTAINT` breaks `LabelCoversTruth` and `TaintedNeverOutward` (`ft1`, `ft2`)."],
         "red", {"tint": False, "dash": "6 4"}),
        ("Round 1 lapses before `Route(e1)` commits", [
            "**The route names its activation and its round**, so it is void at apply, `lease`: the stale route, "
            "witness `NeverVoidedByLease` (`w_voidlease`).",
            "A lapsed round fails its event and takes no default edge (§6; ADR-0054 §8).",
            "`M_TRACKER`, one lease across events and a route that names its node, breaks `RouteOnItsEvent` (`tr1`)."],
         "grey", {}),
        ("Both decisions `bad`: the loop turns twice", [
            "`(s,1)`, round 1, `(w,1)`, `(s,2)`, round 2, `(w,2)`: six units. `(s, 3)` is ready and **its grant is "
            "refused**: `NeverExhausted` (`w_exhausted`).",
            "**Running out of budget fails the workflow**, never completes it, as a timeout never grants "
            "(ADR-0024 §2).",
            "`M_BUDGETDONE` breaks `CompletedOnlyBySink` (`bd1`). The loop running and completing after a loop: "
            "`w_looped`, `w_completedloop`."],
         "amber", {}),
    ]
    vg = 22
    vw = (rw - 44 - vg) / 2
    for r in range(2):
        pair = var[2 * r:2 * r + 2]
        vh = max(c.card(0, 0, vw, t, b, draw=False, size=13.5) for t, b, _, _ in pair)
        for k, (t, b, a, kw_) in enumerate(pair):
            c.card(rx + 22 + k * (vw + vg), uy, vw, t, b, accent=a, h=vh, size=13.5, **kw_)
        uy += vh + 18
    rbot = max(uy, by + bh) + 6
    bot = max(lbot, rbot)
    c.region(lx, top, lw_, bot - top, "The mesh as promoted (`Mesh.tla`'s, §11) · Proposed", "amber", size=14)
    c.region(rx, top, rw, bot - top, "One run of it, as activations in log order, each with its trigger and causal "
             "history (§3) · Proposed", "amber", size=14)
    y = bot + 70

    # ================================================================ B. the budget
    y += c.heading(X0, y, "§2 · The promotion votes on a budget, and the budget is what makes a mesh end", "amber", 21)
    # the unrolling
    uw = 1500
    ux = X0
    utop = y + 18
    c.text(ux + 24, utop + 44, "A budgeted mesh is a DAG unrolled to depth `N` (finding 1): `Mesh.tla`'s mesh at "
                               "`N` = 6, every unit counted", 14.5, "ink", bold=True)
    ky = utop + 70
    chain = [("`(s,1)`", "unit 1", "green"), ("round", "unit 2", "grey"), ("`(w,1)`", "unit 3", "green"),
             ("`(s,2)`", "unit 4", "green"), ("round", "unit 5", "grey"), ("`(w,2)`", "unit 6", "green"),
             ("`(s,3)`", "refused", "red")]
    kw, kg = 150, 54
    kx = [ux + 24 + i * (kw + kg) for i in range(len(chain))]
    kh = c.card(0, 0, kw, "x", ["y"], draw=False, size=13, tsize=15, bullets=False)
    for i, (t, u, a) in enumerate(chain):
        c.card(kx[i], ky, kw, t, [u], accent=a, h=kh, size=13, tsize=15, bullets=False,
               tint=a != "red", dash="6 4" if a == "red" else None)
    for i in range(len(chain) - 1):
        lab = ["event", "`e1`", "`e3`", "event", "`e1`", "`e3`"][i]
        acc = "red" if i == 5 else ("grey" if lab == "event" else "green")
        c.arrow([(kx[i] + kw, ky + kh / 2), (kx[i + 1], ky + kh / 2)], acc, sw=2.2, dash="7 5" if i == 5 else None,
                label=lab, loff=(0, -16))
    ey_ = ky + kh + 60
    for k, u in [(1, "unit 3"), (4, "unit 6")]:
        c.card(kx[k], ey_, kw, "`(x,1)`", [u + ": completes"], accent="green", h=kh, size=13, tsize=15,
               bullets=False, tint=False)
        c.arrow([(kx[k] + kw / 2, ky + kh), (kx[k] + kw / 2, ey_)], "grey", sw=2.2, label="`e2`", lpos=0.5,
                loff=(26, 0))
    ny_ = ey_ + kh + 18
    ny_ += c.para(ux + 24, ny_, uw - 48, "**Its behaviours are exactly those of the mesh unrolled to depth `N`**, so "
                  "ADR-0054's safety argument holds per activation; the mesh adds compactness and an iteration count "
                  "decided at run time within the bound (§2). Drawn here from `Mesh.tla`'s `Grant` and `OrchGrant`, as "
                  "an illustration: **this set of reachable activations is what the gate would show the quorum**, and "
                  "the gate's evidence is not built (I49). The cost falls on the reviewers, who approve every unrolling "
                  "at once.", 13.5, "ink") + 14
    c.region(ux, utop, uw, ny_ - utop, "The unrolling · Proposed", "amber", size=14)
    # the budget's fields, beside it
    tx = ux + uw + 40
    tw = X1 - tx
    th = _sub(c, tx, utop - 4, "What the budget bounds (§2; ADR-0054 §1)")
    th += c.table(tx, utop - 4 + th, [("Bound", tw * 0.12, {"mono": True}), ("What it bounds", tw * 0.42),
                                      ("Value", tw * 0.2), ("At the reference (I49)", tw * 0.26)], [
        ["N", "**The leases the workflow may ever issue**: workers' and the orchestrator's. The promotion grants at "
         "most `N`", "None yet: an open obligation, \"as placeholders first\"", "Charged on every grant; a refusal "
                                                                               "fails the slot"],
        ["N(v)", "Optional, per node", "None yet", "Not named in A16 or I49; `workflow.rs`'s `Budget` carries `per_node`"],
        ["T_wf", "Wall-clock for the whole workflow; ADR-0054 §1 already has it", "None yet; a placeholder and a "
                                                                                    "deployment's (ADR-0054 §1)",
         "**Not built**: no replicated clock"],
    ], size=13.5, accent="amber")
    th += 12
    th += c.para(tx, utop - 4 + th, tw, "**The quorum votes on the budget with the graph and the seatings.** Without "
                 "one, the promotion would be a standing grant of unbounded leases, which \"promotion is a grant\" "
                 "cannot mean. A time bound alone bounds wall-clock, not leases, and would make termination a "
                 "liveness property needing fairness (Options).", 13.5, "muted") + 18
    th += _row(c, tx, utop - 4 + th, tw, [
        ("A grant the budget cannot pay is refused", [
            "**The activation fails, and running out of budget fails the workflow**, never completes it, as a "
            "timeout never grants (ADR-0024 §2).",
            "A refused grant is never granted lower, and no other seating stands in (ADR-0054 §2)."],
         "red", {"tint": False, "dash": "6 4"}),
        ("\"It ends\" stays a bounded safety property", [
            "Every behaviour of a budgeted mesh issues at most `N` leases, so a model checker decides termination at "
            "small `N`, and **no property needs fairness** (§2; Consequences).",
            "That is what ADR-0054's DAG had from its shape (Context)."],
         "amber", {}),
    ], size=13.5)
    y = max(ny_, utop - 4 + th) + 30
    y += _row(c, X0, y, Wd, [
        ("The budget must charge the orchestrator (finding 2)", [
            "A bound on worker leases alone leaves **the one cell that runs at every decision** unbounded.",
            "The runs said it a second way: uncharged, or charged once, the orchestrator frees worker rounds: **2.1 "
            "million states against more than 280 million** (R1; G11 §3, result 10)."],
         "amber", {}),
        ("The gate computes, as evidence for the vote", [
            "**The activations the mesh can reach within `N`**, and **every edge whose guard is identically true** "
            "(drafter's choice). Neither refuses; both say what is being voted on.",
            "It refuses a mesh without a budget, and one whose clear edges cannot be 2-coloured (§11).",
            "**Not built** (I49); how the set is shown, and at what size it stops being readable, is open."],
         "amber", {"status": "notbuilt", "status_extra": "the evidence · I49"}),
    ], size=13.5) + 70

    # ================================================================ C. the activation is the unit
    y += c.heading(X0, y, "§3, §4 · The activation is the unit of attributes, routes and findings; joins are scoped to "
                          "a fan-out", "amber", 21)
    inh_w = 700
    tw2 = Wd - inh_w - 40
    t0 = y
    y += c.table(X0, y, [("Rule", tw2 * 0.13, {"bold": True}),
                         ("ADR-0054, a `dag` (drawn in C9)", tw2 * 0.4),
                         ("ADR-0055, a `mesh`: read per activation", tw2 * 0.47)], [
        ["Shape", "Acyclic, checked at load; a `dag` with a cycle does not load (§1)",
         "**May have cycles, self-loops included**; does not load without a budget (§1). `dag` stays the default, and a "
         "deployment may refuse the kind in its bundle's load check"],
        ["What makes it end", "Its shape: a checker reaches every path, and no liveness argument is needed (Context)",
         "**The budget**: at most `N` leases, so \"it ends\" is a bounded safety property (§2)"],
        ["The unit", "**A node is one round of one cell** (§1)",
         "**An activation, a pair (node, k)**, one round of one cell; a node may run more than once (§3)"],
        ["Attributes", "Lifted once when a node's round ends; `found` alone changes after, false to true (§4)",
         "**Per activation, written once**; `found` as before (§3)"],
        ["A trigger", "—", "**Every activation records its trigger**: the activation it was entered from, or the "
                           "fan-out it belongs to. Its **causal history** is itself and its trigger's history; the log "
                           "holds both, so the history is a fact (§3)"],
        ["A guard reads", "The source and the nodes that **dominate** it, all ended before the source is ready (§4)",
         "**The triggering activation and its causal history, never a node's latest value**, which can change between "
         "decide and apply when the node runs again. `BasisStable` carries over; `Mesh.tla` does not restate it "
         "(§3; finding 3)"],
        ["Where the choice is made", "A **decision point**, consumed once by one route (§8)",
         "A **decision event**, the activation's end, consumed by one route. An older event stays routable until it "
         "is consumed, fails, or a finding closes it (§3)"],
        ["A route names", "The decision point, with its basis (§8)",
         "**Its activation and its round**: void at apply if the activation's event was consumed or failed, or the "
         "round has moved on (§3, §6)"],
        ["A finding disables", "Edges out of its source or any ancestor (§8)",
         "**Every edge out of an activation with the finding anywhere in its causal history**. On a loop, a finding "
         "against the worker's round stops the route out of the decision node's next round, though that round is "
         "clean (§3)"],
        ["Concurrency", "Each branch runs at most once (Context)",
         "**One live activation per node** (drafter's choice): a seating names one principal, which holds one live "
         "lease (ADR-0031 §2). To run concurrently a node names a **pool** of seatings, each charged when used (§3)"],
        ["An `all` join", "Waits for its predecessors; one that can no longer fire is skipped (§1)",
         "**Waits for the branches of one fan-out activation**, matched by its identity, which every branch carries "
         "as its trigger; the skip is scoped the same way. `any` is unchanged (§4)"],
        ["Lineage", "Thinkers alternate on every clear edge, at the tally (§6)",
         "**The clear edges form a 2-colourable graph** under two lineages (§5)"],
        ["Completes", "Every sink ended or skipped, and at least one ended (§9)",
         "**An activation of a sink has ended** (§8)"],
        ["The module", "`spec/Workflow.tla`, 33 rows (G11 §3)",
         "`spec/Mesh.tla`, 23 rows. ADR-0054's one-decision properties are `Workflow.tla`'s and are not repeated"],
    ], size=13.5, accent="amber")
    # inherited card, beside the table
    ix = X0 + tw2 + 40
    ih = c.card(ix, t0, inh_w, "What a mesh inherits from ADR-0054 unchanged (drawn in C9)", [
        "**The promotion grants every lease**: a third grant path, the only clause that adds authority, and none the "
        "quorum did not vote on. No principal grants another (ADR-0054 §2).",
        "**The orchestrator only narrows**: it selects among edges whose guards hold, with `Route(edge)` and "
        "`Report`, and is delivered handles and never bytes (§3).",
        "**A route is checked again where it is applied**, and void if it fails; a lapsed orchestrator takes no "
        "default edge (§8).",
        "**Labels cross cells along the edges**: an `input` labelled by the reporter's `clearSet`, and the routing "
        "rule over labels (§5). An edge waits for its source's coverage (§7).",
        "Read **per activation where ADR-0055 says so** (§1)."],
        accent="amber", status="proposed", status_extra="ADR-0054 · see C9", size=13.5)
    ih2 = c.card(ix, t0 + ih + 20, inh_w, "§10 · The trusted base grows again", [
        "The interpreter of ADR-0054 §11 gains **activation records, causal histories, a budget counter and the "
        "orchestrator's track**, under the same mechanism row of ADR-0045: every decision they make subtracts or "
        "executes a grant the quorum made, and the budget bounds the grant.",
        "**The mechanism grows again, on the path every Run grant travels** (Consequences)."],
        accent="teal", size=13.5)
    y = max(y, t0 + ih + 20 + ih2) + 70

    # ================================================================ D. lineage and taint
    y += c.heading(X0, y, "§5 · Lineages alternate on a 2-coloured clear graph, and taint on a loop only grows",
                   "amber", 21)
    gw = (Wd - 3 * 24) / 4
    gtop = y
    sk_h = 230

    def sketch(i, title, accent, status_txt, draw_fn, note):
        x_ = X0 + i * (gw + 24)
        nh = c.para(0, 0, gw - 32, note, 13.5, draw=False)
        h_ = 70 + sk_h + 10 + nh + 14
        return x_, h_, title, accent, status_txt, draw_fn, note

    def even(x_, y_):
        a, b = (x_ + gw * 0.3, y_ + sk_h / 2), (x_ + gw * 0.7, y_ + sk_h / 2)
        _circle(c, *a, 34, "`s`", "blue", "A")
        _circle(c, *b, 34, "`w`", "green", "B")
        c.arrow([(a[0] + 30, a[1] - 16), (b[0] - 30, b[1] - 16)], "ink", sw=2, label="clear", loff=(0, -14))
        c.arrow([(b[0] - 30, b[1] + 16), (a[0] + 30, a[1] + 16)], "ink", sw=2, label="clear", loff=(0, 16))

    def odd(x_, y_):
        pa = (x_ + gw * 0.5, y_ + 44)
        pb = (x_ + gw * 0.25, y_ + sk_h - 44)
        pc = (x_ + gw * 0.75, y_ + sk_h - 44)
        _circle(c, *pa, 32, "`a`", "blue", "A")
        _circle(c, *pb, 32, "`b`", "green", "B")
        _circle(c, *pc, 32, "`c`", "red", "A or B?", dash="5 4")
        c.arrow([(pa[0] - 22, pa[1] + 24), (pb[0] + 14, pb[1] - 28)], "ink", sw=2, label="clear", lpos=0.5,
                loff=(-30, -6))
        c.arrow([(pb[0] + 34, pb[1]), (pc[0] - 34, pc[1])], "ink", sw=2, label="clear", loff=(0, 16))
        c.arrow([(pc[0] - 14, pc[1] - 28), (pa[0] + 22, pa[1] + 24)], "red", sw=2, dash="7 5")
        c.label(x_ + gw * 0.5 + 92, y_ + sk_h / 2 - 8, "make this a\nhandle edge", "red")

    def selfloop(x_, y_):
        p = (x_ + gw * 0.27, y_ + sk_h / 2)
        _circle(c, *p, 34, "`v`", "red", "A", dash="5 4")
        c.arrow([(p[0] + 20, p[1] - 28), (p[0] + 20, p[1] - 72), (p[0] - 20, p[1] - 72), (p[0] - 20, p[1] - 30)],
                "red", sw=2, dash="7 5")
        c.label(p[0], p[1] - 92, "clear self-loop", "red")
        q = (x_ + gw * 0.62, y_ + sk_h / 2)
        _circle(c, q[0], q[1] - 50, 28, "`v`¹", "blue", "A")
        _circle(c, q[0], q[1] + 50, 28, "`v`²", "green", "B")
        _circle(c, q[0] + 120, q[1] - 50, 28, "`v`³", "blue", "A")
        c.arrow([(q[0], q[1] - 22), (q[0], q[1] + 22)], "ink", sw=2)
        c.arrow([(q[0] + 24, q[1] + 36), (q[0] + 98, q[1] - 32)], "ink", sw=2)
        c.text(q[0] + 70, q[1] + 64, "by activation parity", 12.5, "muted")

    def taint(x_, y_):
        steps = [("`(s,1)`", "clean", "green", False), ("`(w,1)`", "reads untrusted", "red", True),
                 ("`(s,2)`", "untrusted", "red", True), ("`(w,2)`", "untrusted", "red", True)]
        bw_ = (gw - 32 - 3 * 18) / 4
        yy = y_ + 10
        for k, (t, s_, a, dsh) in enumerate(steps):
            bx_ = x_ + 16 + k * (bw_ + 18)
            c.card(bx_, yy, bw_, t, [s_], accent=a, h=74, size=12.5, tsize=14, bullets=False, pad=10,
                   tint=not dsh, dash="6 4" if dsh else None)
            if k:
                c.arrow([(bx_ - 18, yy + 37), (bx_, yy + 37)], "red" if k > 1 else "green", sw=2)
        c.arrow([(x_ + 16 + 2 * (bw_ + 18) + bw_ / 2, yy + 74), (x_ + 16 + 2 * (bw_ + 18) + bw_ / 2, yy + 120)],
                "red", sw=2, dash="7 5")
        c.card(x_ + 16 + 1.2 * (bw_ + 18), yy + 120, gw - 32 - 1.2 * (bw_ + 18), "`e2` into outward `x`",
               ["disabled for the rest of the run"], accent="red", h=64, size=12.5, tsize=14, bullets=False, pad=10,
               tint=False, dash="6 4")

    sks = [
        sketch(0, "An even clear cycle: two colours suffice", "green", "passes the tally",
               even, "`Mesh.tla`'s mesh: `s` and `w` alternate on `e1` and `e3`. **The runtime consequence**: every "
                     "activation entered by a clear edge differs in lineage from its trigger (`ClearHopsAlternate`; "
                     "`M_NOLINEAGE`, the gate not checking, breaks it, `nl1`)."),
        sketch(1, "An odd clear cycle cannot be seated with two lineages", "red", "fails the tally",
               odd, "**It does not pass the tally.** A workflow fixes it by making one edge of the cycle a handle "
                    "edge, which carries no bytes into its target. A third lineage is allowed where a deployment has "
                    "one, and not required (Options)."),
        sketch(2, "A clear self-loop: fixed by parity seatings", "red", "fails, unless two seatings",
               selfloop, "The node gets **two seatings of different lineages, used by activation parity** "
                         "(drafter's choice: both fixes are allowed). Parity seatings are not in the module and are "
                         "not built (§11; I49)."),
        sketch(3, "Taint on a loop only grows (finding 5)", "red", "fails in the right direction",
               taint, "An input's label is its reporter's `clearSet`, and a `clearSet` only grows, so **once untrusted "
                      "content is read on a clear cycle, every later activation on it is labelled untrusted** and the "
                      "routing rule closes the cycle's outward edges for the rest of the run. Taint cannot be laundered "
                      "round a loop."),
    ]
    sh = max(s[1] for s in sks)
    for x_, _, title, accent, st, fn, note in sks:
        c.rect(x_, gtop, gw, sh, accent if accent == "green" else "grey", tint=False)
        c.blocks.append((x_, gtop, x_ + gw, gtop + sh, "sketch " + title[:30]))
        c.text(x_ + 16, gtop + 28, title, 15.5, accent, bold=True)
        c.pill(x_ + 16, gtop + 40, st, accent, 11.5, dash=None if accent == "green" else "6 4")
        fn(x_, gtop + 70)
        c.para(x_ + 16, gtop + 70 + sk_h + 10, gw - 32, note, 13.5)
    y = gtop + sh + 24
    y += _row(c, X0, y, Wd, [
        ("The check is static", [
            "**Over the graph and the seatings**, at the promotion tally, where a refusal stalls (§5; ADR-0035 §5 R8, "
            "which already says a workflow whose clear edges are not bipartite cannot meet the rule).",
            "**ADR-0035 is Proposed**, so it is declared, not enforced (ADR-0054 D-0054-1). ADR-0055's entry in "
            "ADR-0035 §5 is not drafted (§11)."],
         "amber", {}),
        ("A cycle repeats what alternation cannot stop", [
            "Alternation keeps a trigger from crossing one clear hop into its own lineage. **It does not stop it "
            "reaching that lineage again two hops on, and a loop offers that every turn.**",
            "**Labels are what bound it** (§5): the two-hop gap is bounded because taint only grows (finding 5)."],
         "red", {"tint": False, "dash": "6 4"}),
        ("What it costs", [
            "**An honest loop that reads untrusted content once loses its outward reach for good**: ADR-0054's "
            "finding 6, made stronger (Consequences). \"That is the right direction to fail\" (§5).",
            "**Two lineages constrain the graph further**: an odd clear cycle needs a handle edge or parity "
            "seatings."],
         "grey", {}),
        ("At the reference (A16; I49 (b))", [
            "**Lineage is a tag the text declares, compared on every clear edge at load**; a clear edge with one "
            "declared lineage on both ends does not load. No independence table exists (G18).",
            "A clear input's label joins the receiver's `clearSet` at grant; an edge into an outward node is disabled "
            "by an untrusted attribute (`untrusted_content_read_on_the_loop_disables_the_exit`)."],
         "teal", {"status": "built", "status_extra": "in part · A16 pending"}),
    ], size=13.5) + 70

    # ================================================================ E. the mechanism tracks and is the bus
    y += c.heading(X0, y, "§6, §7 · The mechanism tracks; the orchestrator holds no state; event-driven means the "
                          "mechanism is the bus", "teal", 21)
    dw = 2020
    cx_ = X0
    etop = y + 18
    # cells row
    cells = [
        ("Worker cell `w`", "green", [
            "Thinker and its cell Observer. Ingress is the Listener's closed list, with ADR-0054's `input` "
            "(ADR-0043 §1).",
            "Its round ends on its outcome: the end and its attributes are one log entry."]),
        ("Worker cell `x`", "green", [
            "**Never addressed by `w`.** No variant publishes to another cell or subscribes to anything (§7).",
            "A round topic is read only by the seats in its watched-by relation."]),
        ("The orchestrator cell", "grey", [
            "**One round per decision event**, granted from the budget when the event opens; ended when its route "
            "applies or its lease lapses. Events are served in log order (drafter's choice).",
            "**It keeps nothing between rounds.** It emits `Route(edge)` naming its activation and its round."]),
    ]
    cw3 = 560
    cg = (dw - 48 - 3 * cw3) / 2
    cxs = [cx_ + 24 + i * (cw3 + cg) for i in range(3)]
    ch_ = max(c.card(0, 0, cw3, t, b, draw=False, size=13.5) for t, _, b in cells)
    cy0 = etop + 44
    for x_, (t, a, b) in zip(cxs, cells):
        c.card(x_, cy0, cw3, t, b, accent=a, h=ch_, size=13.5)
    # choreography: refused
    yc = cy0 + 50
    c.arrow([(cxs[0] + cw3, yc), (cxs[1], yc)], "red", sw=2.2, dash="7 5", both=True,
            label="✗ choreography:\nnot supported", lpos=0.5)
    # the mechanism
    my0 = cy0 + ch_ + 130
    entries = [("end of `(w,1)`", "and its attributes, lifted once"), ("a finding", "against an activation"),
               ("a lease lapse", "a round ends"), ("a fence", "an epoch moves"), ("a budget refusal", "a grant not paid"),
               ("`Route(e2)`", "committed; checked again")]
    ew = (dw - 48 - 40 - 5 * 18) / 6
    eh_ = max(c.card(0, 0, ew, a, [b], draw=False, size=12.5, tsize=14, bullets=False, pad=10) for a, b in entries)
    ly = my0 + 74
    for k, (a, b) in enumerate(entries):
        c.card(cx_ + 44 + k * (ew + 18), ly, ew, a, [b], accent="teal", h=eh_, size=12.5, tsize=14, bullets=False,
               pad=10, tint=False)
    c.text(cx_ + 44, my0 + 60, "The consensus log: **the events a mesh reacts to are entries in it** (§7), each "
                               "applied by every replica at its position", 14, "teal")
    ay2 = ly + eh_ + 26
    ah = c.card(cx_ + 44, ay2, dw - 88, "In the same apply, the mechanism evaluates what each entry enables", [
        "**What an entry enables, in the same apply** (§7): the attributes lifted, a computed edge (`e3`) evaluated, "
        "a decision event opened, every edge downstream of a finding closed, a committed route checked again and "
        "voided if it fails (§3).",
        "**Every grant is charged to the budget or refused** (§2): a ready activation's lease, and the orchestrator's "
        "round for an event that has opened (§6).",
        "**It holds the track**: activations, their triggers and causal histories, the budget counter. The log holds "
        "both trigger and history, so the history is a fact (§3, §10)."],
        accent="teal", size=13.5)
    mbot = ay2 + ah + 22
    c.region(cx_ + 20, my0, dw - 40, mbot - my0, "The mechanism, replicated · Proposed",
             "teal", dash=None, size=14)
    # Kafka
    ky0 = mbot + 70
    kh_ = c.card(cx_ + 20, ky0, dw - 40, "Kafka: round topics carry the records and order nothing (ADR-0005)", [
        "**Kafka is neither the ordering authority nor the system of record**: the causal frame is the Paxos log, and "
        "Kafka's guarantee is durability in the window (ADR-0005, R1). The delivered track is written to the "
        "orchestrator's round topic as the round's **opening record**, as ADR-0048 §2 does for the tool list, **so its "
        "Observer reads what the orchestrator was given** (§6)."],
        accent="grey", size=13.5, bullets=False)
    ebot = ky0 + kh_ + 18
    # arrows: cells to the log, the log to the orchestrator
    c.arrow([(cxs[0] + cw3 * 0.6, cy0 + ch_), (cxs[0] + cw3 * 0.6, my0)], "green", sw=2.4,
            label="its end, its `Report`s", lpos=0.45)
    c.arrow([(cxs[1] + cw3 / 2, my0), (cxs[1] + cw3 / 2, cy0 + ch_)], "teal", sw=2.4,
            label="a lease the promotion grants", lpos=0.55)
    ox = cxs[2] + cw3 * 0.3
    c.arrow([(ox, my0), (ox, cy0 + ch_)], "teal", sw=2.4, label="the track: typed facts,\nlabels, triggers, "
                                                                  "handles;\nnever bytes", lpos=0.5)
    ox2 = cxs[2] + cw3 * 0.78
    c.arrow([(ox2, cy0 + ch_), (ox2, my0)], "grey", sw=2.4, label="`Route(edge)`:\nactivation + round", lpos=0.5)
    c.arrow([(cx_ + dw * 0.5, mbot), (cx_ + dw * 0.5, ky0)], "grey", sw=2, both=True,
            label="records carried, unordered", lpos=0.5)
    c.region(cx_, etop, dw, ebot - etop, "Orchestration over a log: ADR-0054's shape, with cycles (Context) · Proposed",
             "amber", size=14)
    # cards beside: the three reasons
    sx2 = cx_ + dw + 40
    s2w = X1 - sx2
    sy = etop
    sy += c.card(sx2, sy, s2w, "\"The orchestrator tracks\" is met by the mechanism (§6) ⟨M4⟩", [
        "**The orchestrator keeps nothing between rounds. Three reasons, each sufficient:**",
        "**A lease is round-coterminous and lasts at most `T_persona`** (ADR-0031 §2, A2). A long mesh outlives any "
        "one lease, so a tracking orchestrator would need successor grants inside the workflow, which ADR-0054 §2 "
        "excludes.",
        "**State carried across rounds is persistent agent memory**, which the corpus puts outside the pattern.",
        "**A long-lived orchestrator makes routes ambiguous**: a route decided on one event and committed after the "
        "next has opened would land on the wrong activation unless it names its own."],
        accent="amber", size=13.5, status="proposed", status_extra="ADR-0055 §6") + 18
    sy += c.card(sx2, sy, s2w, "`M_TRACKER`: the tracker, as a mutation", [
        "One lease across decision events, and a route that names its node, not its activation: it applies to "
        "whichever activation of the node is open when it commits. **`RouteOnItsEvent` breaks** (`tr1`).",
        "A route here names both its activation and its round; **the module does not show which alone suffices** "
        "(finding 4)."],
        accent="grey", size=13.5) + 18
    sy += c.card(sx2, sy, s2w, "Why choreography is not supported (§7; Options; finding 6)", [
        "In choreography workers publish events and others subscribe, and **no one decides what runs next**. "
        "Rejected: no variant subscribes, a round topic is read only by its watchers, and **no component that is not "
        "a model would decide what runs next**.",
        "Every reading in which cells react to each other directly puts a model's output in charge of what runs "
        "next. **Event-driven and havoc are compatible only with the mechanism as the bus.**"],
        accent="red", size=13.5, tint=False, dash="6 4") + 18
    sy += c.card(sx2, sy, s2w, "Consequences the record states against itself", [
        "**Budget burning.** A Byzantine worker that always reports `retry`, or an orchestrator that always loops, "
        "spends the budget and fails the workflow. Safe, and paid for in principals. A correlation over it is owed to "
        "ADR-0051 (Open obligations; G11 item 97).",
        "**Many principals**: two per activation and two per orchestrator round, up to `N` of each kind of round.",
        "**Reviewers approve every unrolling at once.** The gate's evidence helps; it does not make a large mesh easy "
        "to read.",
        "**Positive**: loops whose length is decided at run time, inside a bound the quorum voted on; ADR-0054's "
        "safety argument carries over per activation; **no principal seats another**, and the budget bounds how many "
        "seatings a promotion can produce; the orchestrator is stateless and still informed."],
        accent="grey", size=13.5) + 18
    y = max(ebot, sy) + 50

    # completion and failure
    hw = (Wd - 40) / 2
    y0 = y
    h1 = _sub(c, X0, y, "§8 · Completion and failure")
    h1 += c.table(X0, y + h1, [("The mesh", hw * 0.2, {"bold": True}), ("When", hw * 0.58), ("Record", hw * 0.22)], [
        {"cells": ["Completes", "**An activation of a sink has ended.** Completion still says the graph was traversed, "
                                "and nothing about whether the work is right", "§8; ADR-0054 §9"], "accent": "green"},
        {"cells": ["Fails", "**The budget refuses a grant**: running out never completes it", "§2, §8; `M_BUDGETDONE`"],
         "accent": "red"},
        {"cells": ["Fails", "**`T_wf` passes**: a timeout is always a failure", "§8; ADR-0054 §9"], "accent": "red"},
        {"cells": ["Fails", "**It is quiescent**: no activation ready or running, no decision event open, no route in "
                            "flight, and no sink ended", "§8; `Mesh.tla` `Quiescent`"], "accent": "red"},
        {"cells": ["Fails", "**ADR-0054 §9's other failures, per activation**: a node fails, a decision event fails, a "
                            "grant is refused, the epoch is fenced", "§8; ADR-0054 §9"], "accent": "red"},
    ], size=13.5, accent="amber")
    h1 += 10 + c.para(X0, y + h1 + 10, hw, "A workflow's failure stops nothing else: every cell's lease ends by its own "
                      "path (ADR-0054 §9). `Mesh.tla` does not check deadlock: **a workflow may stall, and stalling is "
                      "safe** (header).", 13.5, "muted")
    h2 = _sub(c, X0 + hw + 40, y0, "§9 · Degeneracy on this record")
    h2 += c.card(X0 + hw + 40, y0 + h2, hw, None, [
        "**None of its own.** ADR-0054's two apply per activation: D-0054-1, lineage alternation declared and not "
        "enforced, every deployment today; D-0054-2, coverage at the edge waived (ADR-0054 §10).",
        "**A deployment that runs only `dag` workflows is not degenerate on this record**; it has not taken the "
        "widening (§9). One that wants only DAGs refuses the kind in its bundle's load check (§1), which the reference "
        "does not build (I49)."],
        accent="grey", size=13.5)
    y = y0 + max(h1, h2) + 70

    # ================================================================ F. the module
    y += c.heading(X0, y, "`spec/Mesh.tla`: checked by TLC, not proved (§11 ⟨R1⟩; G11 §2.9, §3, item 101; ADR-0046 "
                          "A1)", "teal", 21)
    y += c.para(X0, y, Wd, "TLC 2.19 on 2026.10.07. Nodes {`s`, `w`, `x`}, the clear cycle `s` → `w` → `s` (`e1` chosen, "
                "`e3` computed) and the chosen handle exit `e2` to the outward sink, guarded by `s` `ok`; budget `N` = 6; "
                "lineages {A, B}. **No proof module exists**, and `spec/proof-sync.sh` exits 1 because it records no "
                "reason for this module or `Workflow.tla` (G11 §2.9). **Checked, not proved**: these are results at "
                "small constants. No binding rows (G11 item 90).", 14, "muted") + 18
    pw_ = Wd
    y += c.table(X0, y, [("Property", pw_ * 0.14, {"mono": True}), ("What it says (`Mesh.tla`)", pw_ * 0.34),
                         ("Mutation that must break it", pw_ * 0.3), ("Row", pw_ * 0.06),
                         ("TLC", pw_ * 0.16)], [
        ["BudgetBound", "No more than `N` leases are ever granted, the orchestrator's rounds included",
         "`M_OVERRUN`: the budget checked with ≤ in place of <. `M_ORCHFREE`: the orchestrator's rounds not charged",
         "`ov1`, `of1`", "Violated, both"],
        ["CompletedOnlyBySink", "A workflow completes only when an activation of its sink has ended; running out of "
                                "budget fails it", "`M_BUDGETDONE`: running out of budget completes the workflow",
         "`bd1`", "Violated"],
        ["RouteOnItsEvent", "Every applied `Route` consumed the activation it was decided for",
         "`M_TRACKER`: one lease across decision events; a route names its node", "`tr1`", "Violated"],
        ["NoActivationAfterFinding", "No activation is created by an edge out of an activation whose causal history "
                                     "held a finding ordered before it",
         "`M_SOURCEONLY`: a finding disables only edges out of its own activation", "`so1`", "Violated"],
        ["LabelCoversTruth", "An activation that really carries untrusted content is labelled untrusted: taint is "
                             "carried round the cycle along clear edges",
         "`M_FORGETTAINT`: a clear input does not join the receiver's label", "`ft1`", "Violated"],
        ["TaintedNeverOutward", "The outward sink is never entered from an activation that really carries untrusted "
                                "content", "`M_FORGETTAINT`", "`ft2`", "Violated"],
        ["ClearHopsAlternate", "Every activation entered by a clear edge has a Thinker lineage different from its "
                               "trigger's", "`M_NOLINEAGE`: the promotion gate does not check lineages", "`nl1`",
         "Violated"],
        {"cells": ["Safe", "All seven together, no mutation", "—", "`safe`",
                   "**Holds**: 2,142,317 distinct states, 14 s"], "accent": "teal"},
    ], size=13.5, accent="teal") + 30

    y += _sub(c, X0, y, "`Mesh-rows.txt` and `Mesh-results-2026.10.07.txt`: all 23 rows", "teal")
    lw2 = Wd * 0.43
    rx2 = X0 + lw2 + 40
    rw2 = X1 - rx2
    t2y = y
    hl = _sub(c, X0, y, "The record as drafted: `Safe`, then seven witnesses, each an invariant that must be VIOLATED",
              "teal", 15)
    hl += c.table(X0, y + hl, [("Row", lw2 * 0.18, {"mono": True}), ("Checked", lw2 * 0.29, {"mono": True}),
                               ("What it shows (`Mesh.tla`)", lw2 * 0.35), ("Result", lw2 * 0.18)], [
        {"cells": ["safe", "Safe", "The seven properties hold together", "**Holds** · 2,142,317"], "accent": "teal"},
        ["w_looped", "NeverLooped", "The loop runs: the decision node is activated a second time", "Reached · 532"],
        ["w_completedloop", "NeverCompletedAfterLoop", "The workflow completes after going round the loop",
         "Reached · 60,009"],
        ["w_exhausted", "NeverExhausted", "The budget runs out", "Reached · 63,724"],
        ["w_taintloop", "NeverTaintAroundLoop", "Untrusted content read on the loop is carried back to the decision "
                                                "node", "Reached · 550"],
        ["w_exitclosed", "NeverExitClosedByTaint", "A decision that would take the exit carries an untrusted label, "
                                                   "and the workflow fails", "Reached · 417"],
        ["w_voidhistory", "NeverVoidedByHistory", "A route is void because of a finding upstream of the activation it "
                                                  "was decided for", "Reached · 21,320"],
        ["w_voidlease", "NeverVoidedByLease", "A route decided in one round is void because that round has ended: the "
                                              "stale route", "Reached · 305"],
    ], size=13, accent="teal")
    hr = _sub(c, rx2, t2y, "Each mutation breaks its property, and its remainder row shows it breaks nothing else",
              "teal", 15)
    hr += c.table(rx2, t2y + hr, [("Row", rw2 * 0.09, {"mono": True}), ("`Mut`", rw2 * 0.16, {"mono": True}),
                                  ("Checked", rw2 * 0.22), ("What it shows", rw2 * 0.22),
                                  ("Constraint", rw2 * 0.11, {"mono": True}), ("Result (distinct states)", rw2 * 0.2)], [
        ["ov1", "M_OVERRUN", "`BudgetBound`", "Breaks it", "", "Violated · 62,802"],
        ["ov_rest", "M_OVERRUN", "the other six", "Nothing else", "", "Holds · 35,179,821"],
        ["of1", "M_ORCHFREE", "`BudgetBound`", "Breaks it", "", "Violated · 59,893"],
        {"cells": ["of_rest", "M_ORCHFREE", "the other six", "Nothing else, **up to one lease past the budget**",
                   "CapOnePast", "Holds · 13,624,749 · bounded"], "accent": "amber"},
        ["bd1", "M_BUDGETDONE", "`CompletedOnlyBySink`", "Breaks it", "", "Violated · 109,369"],
        ["bd_rest", "M_BUDGETDONE", "the other six", "Nothing else", "", "Holds · 2,142,317"],
        ["tr1", "M_TRACKER", "`RouteOnItsEvent`", "Breaks it", "", "Violated · 6,808"],
        {"cells": ["tr_rest", "M_TRACKER", "the other six", "Nothing else, **up to one lease past the budget**",
                   "CapOnePast", "Holds · 452,432,065 · 59 min · bounded"], "accent": "amber"},
        ["so1", "M_SOURCEONLY", "`NoActivationAfterFinding`", "Breaks it", "", "Violated · 856"],
        ["so_rest", "M_SOURCEONLY", "the other six", "Nothing else", "", "Holds · 5,555,341"],
        ["ft1", "M_FORGETTAINT", "`LabelCoversTruth`", "Breaks it", "", "Violated · 194"],
        ["ft2", "M_FORGETTAINT", "`TaintedNeverOutward`", "Breaks it: the one mutation that breaks two", "",
         "Violated · 18,122"],
        ["ft_rest", "M_FORGETTAINT", "the other five", "Nothing else", "", "Holds · 5,135,077"],
        ["nl1", "M_NOLINEAGE", "`ClearHopsAlternate`", "Breaks it", "", "Violated · 388"],
        ["nl_rest", "M_NOLINEAGE", "the other six", "Nothing else", "", "Holds · 4,284,633"],
    ], size=13, accent="teal")
    hl += 12 + c.para(X0, y + hl + 12, lw2, "A violated row's state count is TLC's when it stopped at the first "
                      "counterexample, with states still queued. \"The other six\" are the seven properties less the one "
                      "the mutation is about. Runner `mesh-gen-results.sh`; TLC 2.19 (the results file's header).", 13, "muted")
    y = t2y + max(hl, hr) + 24
    y += _row(c, X0, y, Wd, [
        ("Two remainder rows are bounded: `CapOnePast`", [
            "`CapOnePast == nAll <= N + 1`: one lease past the budget, **the reach `M_OVERRUN`'s row has with no "
            "constraint**. Used by `of_rest` and `tr_rest` and no other row, **by the custodian's decision** (R1; G11 "
            "§5: a remainder with no bound is checked under a stated cap, and the cap is a row).",
            "Under either mutation the budget buys more worker rounds, and the state space outgrows the machine."],
         "amber", {}),
        ("The unconstrained run was stopped", [
            "**Unconstrained, `M_ORCHFREE` had reached 282 million states with 125 million still queued after eight "
            "hours, and was stopped** (§11).",
            "\"The runs say finding 2 a second way\": an uncharged orchestrator, or one charged once for the run, frees "
            "worker rounds, **the difference between 2.1 million states and more than 280 million** (R1)."],
         "red", {"tint": False, "dash": "6 4"}),
        ("Not modelled (`Mesh.tla`, header; §11 not met)", [
            "**Fan-out, scoped joins and serialisation per node** (the mesh never runs two activations at once); "
            "**pools**; **a self-loop with parity seatings**.",
            "Observer lineage; epochs and fences; **the track the orchestrator is delivered**; the gate's bipartite "
            "check, which is static, and whose runtime consequence is `ClearHopsAlternate`.",
            "**Proofs.** Deadlock is not checked."],
         "red", {"tint": False, "dash": "6 4"}),
    ], size=13.5) + 70

    # ================================================================ G. the reference
    y += c.heading(X0, y, "At the reference: ADR-0033 A16, pending, on the `workflow` floor stage, which is not in force",
                   "teal", 21)
    y += c.para(X0, y, Wd, "**§11's reference item is met in part** ⟨R2⟩: the reference at `11aaf6a` "
                "(`SHA256SUMS-REF-2026.10.08`). **One engine runs both kinds**: each node run is an activation with its "
                "trigger and causal history, and a `dag` is the case of one activation per node (I49). **The reference "
                "links a floor that is not in force**, at the custodian's direction (G11 item 102). It discharges "
                "nothing in force: on ADR-0055's ratification, every behaviour of §11 is seen, **at the replicated "
                "state and not end to end** (A16).", 14, "muted") + 18
    rw1 = Wd * 0.56
    t1y = y
    hA = c.table(X0, y, [("Behaviour (§11), each seen", rw1 * 0.42),
                         ("Test at the replicated state, named after `Mesh.tla` (A16)", rw1 * 0.58, {"mono": True})], [
        ["The loop turns twice and exits", "the_loop_turns_twice_and_exits"],
        ["The budget refuses a grant and the workflow fails", "the_budget_refuses_a_grant_and_the_workflow_fails"],
        ["An orchestrator round is charged", "an_orchestrator_round_is_charged"],
        ["A finding against the worker's round voids the decision node's next route",
         "a_finding_against_the_workers_round_voids_the_decision_nodes_next_route"],
        ["A route decided in one round and committed after it ends is void",
         "a_route_decided_in_one_round_and_committed_after_it_ends_is_void"],
        ["Untrusted content read on the loop disables the exit",
         "untrusted_content_read_on_the_loop_disables_the_exit"],
        ["A mesh loads only with a budget and two-coloured clear edges",
         "a_mesh_loads_only_with_a_budget_and_two_coloured_clear_edges"],
    ], size=13, accent="teal")
    hA += 10 + c.para(X0, y + hA + 10, rw1, "The last row is A16's load check (ADR-0055 §1), not one of §11's six. "
                      "`spec/Mesh.tla` is tied to the reference **by tests named after its properties and by no trace**: "
                      "`spec/Mechanism.tla` does not model workflows, and trace validation was not rerun. "
                      "`mechanism/lean` is stale, by the custodian's decision of 2026.10.08 (A16).", 13, "muted")
    nx = X0 + rw1 + 40
    nw = X1 - nx
    hB = c.card(nx, t1y, nw, "Not met, and not built (§11; A16; I49)", [
        "**No mesh is run end to end, and the cells are the tests'**: a test drives each session, a BOOTSTRAP standing "
        "in for a launch per slot (I49 (g)).",
        "**Fan-out-scoped joins, pools and parity seatings are not built**: **a mesh with an `all` join does not load** "
        "(I49 (d), PROVISIONAL workflow-mesh-joins).",
        "**Not built**: `T_wf` and the step bound (no replicated clock); **the gate's evidence for a mesh's vote** "
        "(reachable activations within `N`); the bundle's refusal of a `kind`; seatings above rung 0.",
        "**A finding has a form the reference chose** (I49 (a), PROVISIONAL finding-record), and only workflows read "
        "it.",
        "**A clear input is delivered only by the replica that holds the predecessor's reports** (I49 (f); "
        "`mechanism/` finding 23)."],
        accent="red", size=13.5, status="notbuilt", status_extra="I49", tint=False)
    y = t1y + max(hA, hB) + 50

    # ratification condition | findings
    y += c.heading(X0, y, "ADR-0055's tables, findings and obligations, in full", "amber", 21)
    HW = (Wd - 40) / 2
    XR = X0 + HW + 40
    ya = y
    ha = _sub(c, X0, y, "§11 · Ratification condition, at G11")
    ha += c.table(X0, y + ha, [("Condition", HW * 0.42), ("State", HW * 0.58)], [
        {"cells": ["**ADR-0054 is ratified first**, or with this record", "**Not met.** ADR-0054 is Proposed "
                   "(G11 §1.1)"], "accent": "red"},
        {"cells": ["**The dependent entries are drafted**: ADR-0054 §1, §2, §4, §8 and §9, read per activation and with "
                   "the kind and the budget; ADR-0035 §5 (the 2-colour check)", "**Not met.** \"ADR-0055's dependent "
                   "entries are not drafted\" (G11 §1.1). The twelve amendments pending are ADR-0054's ten, A16 and A17"],
         "accent": "red"},
        {"cells": ["**A module** states the properties and its mutations break them, by ADR-0046's method",
                   "**Met for TLC at drafting** ⟨R1⟩, with two remainders bounded. **Not met**: fan-out, scoped joins "
                   "and pools; serialisation per node; a self-loop with parity seatings; the static 2-colour check, "
                   "which belongs to the gate; **proofs** (G11 item 101)"], "accent": "amber"},
        {"cells": ["**The gate** computes the reachable activations within `N` and the edges with identically true "
                   "guards, as evidence; refuses a mesh without a budget, and one whose clear edges cannot be "
                   "2-coloured", "**Not met.** The evidence is not built (I49). At the reference's load, a mesh with no "
                   "budget and a clear edge with one declared lineage at both ends do not load (A16)"],
         "accent": "red"},
        {"cells": ["**The reference**, with an ADR-0033 addendum: the module's mesh run by scripted cells, six "
                   "behaviours each seen", "**Met in part** ⟨R2⟩: A16, pending. Every behaviour seen at the replicated "
                   "state; no mesh run end to end"], "accent": "amber"},
        {"cells": ["**A reader who is not the drafter** (ADR-0029 A2)", "**Not met**"], "accent": "red"},
    ], size=13.5, accent="amber")

    # findings
    hb = _sub(c, XR, ya, "Findings")
    hb += c.table(XR, ya + hb, [("#", HW * 0.05, {"bold": True}), ("Finding", HW * 0.95)], [
        ["1", "**A budgeted mesh is a DAG unrolled to depth `N`.** The budget is not an add-on to the mesh; it is what "
              "lets the DAG's argument apply to it at all"],
        ["2", "**The budget must charge the orchestrator.** A bound on worker leases alone leaves the one cell that runs "
              "at every decision unbounded (G11 §3, result 10)"],
        ["3", "**The DAG's settled guards were a property of dominators, and dominators do not survive a cycle.** Causal "
              "history is what does: the activations that led to this one, recorded by the log and immutable"],
        ["4", "**\"The orchestrator tracks\" pulls toward a long lease, and a long lease is three problems at once**: "
              "`T_persona`, memory across rounds, and routes that land on the wrong activation. Moving the tracking "
              "into the mechanism solves all three. `M_TRACKER` removes both the activation and the round from a "
              "route, and the module does not show which alone suffices"],
        ["5", "**Taint on a loop only grows.** Labels from `clearSet` make that automatic. It is the reason "
              "alternation's two-hop gap on a cycle is bounded, and the reason honest loops will find their exits "
              "closed"],
        ["6", "**Event-driven and havoc are compatible only with the mechanism as the bus.** Every reading in which "
              "cells react to each other directly puts a model's output in charge of what runs next"],
    ], size=13.5, accent="amber")
    y = ya + max(ha, hb) + 50

    # options | history and open obligations
    ya = y
    ha = _sub(c, X0, y, "Options considered")
    ha += c.table(X0, y + ha, [("Option", HW * 0.4), ("Disposition", HW * 0.6)], [
        ["**Revise ADR-0054 to a mesh**", "Not taken ⟨M5⟩. The DAG stays the default and the simpler record; the mesh "
                                          "is a widening a deployment opts into"],
        ["**Choreography**: cells publish events and subscribe to each other's", "Rejected. No variant subscribes, a "
         "round topic is read only by its watchers, and no component that is not a model would decide what runs next"],
        ["**Cycles with no budget**, bounded by `T_wf` alone", "Rejected. A time bound bounds wall-clock, not leases; "
         "the promotion would be a grant of as many leases as fit in `T_wf`, and termination would become a liveness "
         "property needing fairness"],
        ["**A budget on workers only**", "Rejected. The orchestrator's rounds would be unbounded. `M_ORCHFREE`"],
        ["**Unroll every loop into a DAG**, as ADR-0054 requires", "Kept as the default. The mesh is the same "
         "behaviours without the unrolling, and the gate's reachable-activation set restores what unrolling showed"],
        ["**Guards that read a node's latest attributes**", "Rejected. Not settled: a node that runs again changes them "
                                                            "between decide and apply"],
        ["**A finding that closes only its own activation**", "Rejected. A loop routes round a finding one hop "
                                                              "downstream. `M_SOURCEONLY`"],
        ["**A tracking orchestrator with one long lease** ⟨M4⟩ as first read", "Not taken. It outlives `T_persona`, "
         "carries memory across rounds, and makes routes ambiguous (§6). `M_TRACKER`. The tracking is kept, in the "
         "mechanism"],
        ["**Concurrent activations of one seating**", "Rejected by ADR-0031 §2. A pool of seatings is the way (§3)"],
        ["**Alternation by a third lineage on odd cycles**", "Not required. It is allowed where a deployment has one; "
         "with two, a handle edge or parity seatings fix the cycle (§5)"],
        ["**Unscoped `all` joins**", "Rejected. Not well defined when a branch can run more than once"],
        ["**Charging Observers separately**", "Not taken (drafter's choice). They ride with their cell; a deployment "
                                              "that wants principal counts multiplies by two"],
    ], size=13.5, accent="amber")

    # history
    hb = _sub(c, XR, ya, "History")
    hb += c.table(XR, ya + hb, [("Tag", HW * 0.06, {"bold": True}), ("Kind", HW * 0.14), ("Change", HW * 0.5),
                                ("Source", HW * 0.2), ("State", HW * 0.1)], [
        ["—", "—", "Initial draft. A workflow declares its kind, and a `mesh` may have cycles under an activation "
         "budget the promotion votes on, the orchestrator's rounds charged to it; the activation is the unit of "
         "attributes, routes and findings, with guards over causal history; one live activation per node; scoped "
         "joins; a 2-colourable clear graph; the mechanism tracks and the orchestrator holds no state, one round per "
         "decision event; the mechanism is the bus; completion and failure; no degeneracy of its own",
         "The custodian's decisions ⟨M1⟩ to ⟨M5⟩, 2026.10.07; the sources in the provenance note", "**Proposed**"],
        ["R1", "Revision before ratification", "**The module is run.** `spec/Mesh.tla` (`a5bc64953c38c9a9`): seven "
         "properties hold, seven witnesses reached, seven mutations each break their property and nothing else. The "
         "remainder rows for `M_ORCHFREE` and `M_TRACKER` are checked under `CapOnePast`, one lease past the budget, "
         "by the custodian's decision; unconstrained they outgrow the machine. The runs say finding 2 a second way. "
         "No decision text changes", "`spec/Mesh-results-2026.10.07.txt` (`c58fa4b2e8bcc555`); the custodian's "
                                     "decisions on the two constrained rows, 2026.10.07", "Recorded"],
        ["R2", "Revision before ratification", "**The reference is built.** §11's reference item is met in part by "
         "ADR-0033 A16 (pending): the six behaviours, seen at the replicated state on `Mesh.tla`'s mesh, with one "
         "engine for a dag and a mesh. What it does not meet is stated there and in `mechanism/` I49. No decision "
         "text changes", "ADR-0033 A16; the custodian's decisions of 2026.10.08", "Recorded"],
    ], size=13, accent="amber") + 24

    # open obligations
    hb += c.card(XR, ya + hb, HW, "Open obligations (the record's eight)", [
            "**The dependent entries, the module rows not yet run, the gate and the reference** (§11).",
            "**The custodian's reading of every drafter's choice.**",
            "**Fan-out, scoped joins, pools and parity seatings** in a module.",
            "**The gate's evidence**: how the reachable-activation set is computed and shown, and at what size it stops "
            "being readable.",
            "**Values** for `N`, `N(v)` and `T_wf`, as placeholders first.",
            "**A correlation over budget burning** for ADR-0051: a mesh that spends its budget on one loop (G11 item "
            "97).",
            "**Rows for `spec/Mesh.tla` in `spec/theorem-premise-binding.md`.**",
            "**Narrative.** ToO and the glossary owe mesh, activation, causal history, decision event, "
            "budget and track; ToO rev 15 §2.11 now tells the mesh, as Proposed (G11 item 100)."],
        accent="red", status="open", status_extra="G11 item 101", tint=False, size=13.5)
    y = ya + max(ha, hb) + 40

    c.legend(X0, y, [("box", "amber", "Proposed: ADR-0055, ADR-0054", "6 4"), ("box", "green", "an activation of a "
                                                                                             "worker or decision node"),
                     ("box", "grey", "an orchestrator round; transport"), ("box", "teal", "the mechanism; TLC checks; "
                                                                                          "built in part"),
                     ("box", "pink", "a finding"), ("box", "red", "refused, tainted, not built, open", "6 4"),
                     ("arrow", "green", "a clear edge"), ("arrow", "grey", "an event; a handle edge; a route"),
                     ("arrow", "red", "closed or not supported", "7 5")])
    return c
