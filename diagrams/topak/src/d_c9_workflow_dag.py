"""C9 — A workflow is a promoted DAG (ADR-0054, Proposed). The promotion seats every cell, the mechanism routes on
typed attributes, an orchestrator cell may only choose among enabled edges, and a route is checked again where it is
applied. Meshes (ADR-0055) are D6's."""
from lib import Canvas, STATUS, STATE_G11, text_width

ID, SLUG = "C9", "workflow-dag"

W = 3400
BR = "[[red|breaks]]"
HO = "holds"


def _nb(ln):
    """Keep leading indentation: the wrapper drops ordinary leading spaces, so indent with no-break spaces."""
    n = len(ln) - len(ln.lstrip(" "))
    return "\u00a0" * n + ln.lstrip(" ")


def code(c, x, y, w, lines, accent, dash=None, draw=True):
    """A monospace block (Cedar), drawn as a card with one line per body item."""
    return c.card(x, y, w, None, [f"`{_nb(ln)}`" if ln.strip() else " " for ln in lines], accent=accent,
                  bullets=False, size=13.5, lead=19, tint=False, pad=14, dash=dash, draw=draw)


def row_cards(c, x, y, w, gap, specs, size=14):
    """A row of cards of equal height, measured over every card. specs: (title, body, accent, kwargs)."""
    n = len(specs)
    cw = (w - (n - 1) * gap) / n
    h = max(c.card(0, 0, cw, t, b, draw=False, size=size, status=k.get("status")) for t, b, _, k in specs)
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


def build():
    c = Canvas(ID, "A workflow is a promoted DAG: the promotion seats every cell, and the orchestrator only narrows",
               "Until ADR-0054 a Run cell's work could not reach another cell: Run's ingress is a closed list and no "
               "item on it is another cell's output (finding 1). **A workflow is a promoted graph of seatings.** Its "
               "promotion is the grant of every lease it will issue, so **no principal grants another**; the mechanism "
               "routes on typed attributes it lifts; an `orchestrator` cell **may only choose among edges the "
               "mechanism has already enabled**, and its route is checked again where it is applied. **ADR-0054 is "
               "Proposed and nothing here is in force**: its ten dependent amendments are pending and not applied. "
               "The reference was built to it anyway and links its floor stage, which is not in force either (G11 "
               "§1.1, §2.5, item 102; ToO rev 15 §2.11).",
               W, "ADR-0054 provenance (K1–K9), Context, Decision §1–§12 (the attribute table, the orchestrator table, "
               "§10's table), Options, Consequences, Findings 1–7, Open obligations, History R1–R6; the dependent "
               "amendments ADR-0015 A1, ADR-0024 A4, ADR-0031 A4, ADR-0037 A5, ADR-0039 A3, ADR-0040 A2 (§1, §3, §4, "
               "§6), ADR-0041 A4 (§1, §4, §5; R3), ADR-0042 A3 (§5), ADR-0043 A3 (§1, §2), ADR-0047 A1 (§1, §4), each "
               "with its Pending line and History row; ADR-0035 §5 R8; ADR-0024 A3 and ADR-0050 (provisional, B34); "
               "ADR-0033 §4 and its addenda A16 (`11aaf6a`, `SHA256SUMS-REF-2026.10.08`) and A17 (`749d54f`, "
               "`SHA256SUMS-REF-2026.10.09`); ADR-0055 §1 (Proposed; D6); spec/Workflow.tla (a72973b5878e9468), "
               "spec/Workflow-rows.txt, spec/Workflow-results-2026.10.08.txt (95b998f616da1875); "
               "floor/proposed/workflow-floor.cedar (10ea6818af9b4efe), workflow.cedarschema (fd394bb8c074eec2), "
               "workflow-tests.json (123 cases), workflow-gates-results-2026.10.08.txt (878d9a431fec9eb9), "
               "floor/proposed/README.md; mechanism/GAPS-AND-ASSUMPTIONS.md §1.1, I49 (a)–(i), G12, findings 21–23; "
               "G11 §1.1, §2.2, §2.4, §2.5, §3, §7 items 56, 90, 91, 101, 102, 103, 108, §8; ToO rev 15 §2.11", state=STATE_G11)
    X0, X1 = c.x0, c.x1
    WW = X1 - X0
    y = c.y

    # ================================================================== status strip
    c.text(X0, y + 15, "Status at G11", 15, "faint", bold=True)
    px0 = X0 + 140
    px = px0
    for lab, key, extra in [
            ("ADR-0054", "proposed", "C1, C2, C3, C4"),
            ("its ten dependent amendments", "proposed", "pending, not applied"),
            ("ADR-0035 R8", "proposed", "revised in place"),
            ("ADR-0033 A16, A17", "proposed", "pending addenda"),
            ("rests on ADR-0050, ADR-0024 A3", "provisional", "Batch 34"),
            ("floor stage `workflow`", "proposed", "gated · not in force"),
            ("`Workflow.tla`", "checked", ""),
            ("the reference at `11aaf6a`, `749d54f`", "built", "on a floor not in force"),
            ("ADR-0055, meshes (D6)", "proposed", "")]:
        lw = text_width(lab, 13.5, True) + 8
        if key == "checked":
            pw = text_width("Checked by TLC · no proof", 11.5, True) + 18
        else:
            pw = text_width(STATUS[key][0] + (f" · {extra}" if extra else ""), 11.5, True) + 18
        if px + lw + pw > X1:
            px = px0
            y += 34
        c.text(px, y + 15, lab, 13.5, "ink", bold=True)
        px += lw
        if key == "checked":
            # a module result, not a reference behaviour: a plain pill
            px += c.pill(px, y, "Checked by TLC · no proof", "violet", 11.5) + 26
        else:
            px += c.status(px, y, key, extra) + 26
    y += 42
    y += c.para(X0, y, WW, "**Proposed means nothing here is in force.** The run cell, the floor and the grant paths in "
                "force are G10's (G11 §2.2, §2.5). ADR-0054 was drafted on 2026.10.07 from a design discussion in which "
                "the custodian settled nine things, ⟨K1⟩ to ⟨K9⟩; every other choice is the drafter's. **One author, "
                "one day**, and the module is the drafter's as well (Consequences). Its ratification also waits on a "
                "reader who is not the drafter (§12; ADR-0029 A2).", 14.5, "muted") + 30

    # ================================================================== band 1: the example workflow
    y = band(c, X0, y, "The example: `Workflow.tla`'s four nodes, one decision point, one join (ADR-0054 §1–§3)",
             status="proposed", extra="ADR-0024 A4 · ADR-0031 A4")
    top = y
    # geometry of the diamond: orchestrator | s | (b, promotion, c) | j
    ox, ow = X0 + 30, 360
    sx, sw = ox + ow + 150, 380
    mx, mw = sx + sw + 200, 470
    jx, jw = mx + mw + 200, 380
    reg_w = jx + jw + 30 - X0
    rx = X0 + reg_w + 60
    rw = X1 - rx

    S = ("Node `s` · the decision point", [
        "One round of one cell: a seating's Thinker (lineage **A**) and its cell Observer (**B**).",
        "Two **chosen** edges leave it, so it is a decision point (§3).",
        "When it ends, the mechanism lifts its attributes once (§4).",
    ])
    B = ("Node `b`", [
        "Thinker **B**, Observer **A**: it reads `s`'s output **in the clear** (e1), so the two Thinkers alternate (§6).",
        "Its own output goes on to `j` in the clear (e3).",
    ])
    C = ("Node `c` · outward", [
        "Its lease reaches an **outward** entry (ADR-0049 §5).",
        "Takes `s`'s output **as a handle** (e2): no bytes, so no alternation is asked of it.",
        "**The routing rule**: e2 is disabled if a guard it reads is labelled `untrusted` (§5).",
    ])
    J = ("Node `j` · the sink, joined on `any`", [
        "Thinker **A**, Observer **B**: e3 is a clear edge from `b`.",
        "**The workflow completes when it ends** (§9).",
        "Under `all`, a predecessor whose every incoming edge can no longer fire is skipped, and a skip propagates "
        "(§1). **Not modelled.**",
    ])
    P = ("The workflow's promotion is the grant (§2)", [
        "The quorum votes on **the graph and its seatings together**; the tally is the authority for every lease the "
        "workflow will issue (ADR-0024 A4).",
        "**When a node becomes ready the mechanism grants its lease**, every field the seating's or narrower: a third "
        "grant path (ADR-0031 A4).",
    ])
    O = ("The `orchestrator` cell (§3)", [
        "Seated **only because** the graph has a chosen edge, checked at load.",
        "One round per decision point, **granted by the promotion** when `s` is ready; its own cell Observer, coupled "
        "by `R3`.",
        "**Reads no bytes**: the enabled edges, the attributes their guards read with their labels and the basis "
        "index, and handles.",
        "It **names an edge, and no principal, field or alphabet**.",
    ])
    hs = c.card(0, 0, sw, S[0], S[1], draw=False, size=13.5)
    hbc = max(c.card(0, 0, mw, B[0], B[1], draw=False, size=13.5),
              c.card(0, 0, mw, C[0], C[1], draw=False, size=13.5))
    hj = c.card(0, 0, jw, J[0], J[1], draw=False, size=13.5)
    hp = c.card(0, 0, mw, P[0], P[1], draw=False, size=13.5, status="proposed")
    ho = c.card(0, 0, ow, O[0], O[1], draw=False, size=13.5)
    by = top + 60
    py = by + hbc + 150
    cyy = py + hp + 150
    pc = py + hp / 2
    s_y, j_y, o_y = pc - hs / 2, pc - hj / 2, pc - ho / 2
    dag_bot = max(cyy + hbc, o_y + ho)
    c.card(sx, s_y, sw, S[0], S[1], accent="amber", size=13.5)
    c.card(mx, by, mw, B[0], B[1], accent="amber", size=13.5, h=hbc)
    c.card(mx, cyy, mw, C[0], C[1], accent="red", size=13.5, h=hbc, tint=False)
    c.card(jx, j_y, jw, J[0], J[1], accent="amber", size=13.5)
    c.card(mx, py, mw, P[0], P[1], accent="blue", size=13.5, status="proposed", status_extra="ADR-0024 A4")
    c.card(ox, o_y, ow, O[0], O[1], accent="amber", size=13.5, tint=False, dash="6 4")
    # the grants: the promotion to every node
    gx = mx + mw / 2
    c.arrow([(gx, py), (gx, by + hbc)], "blue", sw=2.4, label="grant", lpos=0.5)
    c.arrow([(gx, py + hp), (gx, cyy)], "blue", sw=2.4, label="grant", lpos=0.5)
    c.arrow([(mx, pc), (sx + sw, pc)], "blue", sw=2.4, label="grant", lpos=0.5)
    c.arrow([(mx + mw, pc), (jx, pc)], "blue", sw=2.4, label="grant", lpos=0.5)
    # the edges
    bm, cm = by + hbc / 2, cyy + hbc / 2
    scx = sx + sw / 2
    jcx = jx + jw / 2
    c.arrow([(scx, s_y), (scx, bm), (mx, bm)], "amber", sw=3)
    c.label((scx + mx) / 2 + 20, bm, "**e1 · chosen**\nguard: `outcome(s) = ok`\ndelivery: **clear**", "amber",
            12.5, 300)
    c.arrow([(scx, s_y + hs), (scx, cm), (mx, cm)], "amber", sw=3)
    c.label((scx + mx) / 2 + 20, cm, "**e2 · chosen**\nguard: `true`\ndelivery: **handle**", "amber", 12.5, 300)
    c.arrow([(mx + mw, bm), (jcx, bm), (jcx, j_y)], "teal", sw=3)
    c.label((mx + mw + jcx) / 2, bm, "**e3 · computed**\nguard: `true`\ndelivery: **clear**", "teal", 12.5, 300)
    c.arrow([(mx + mw, cm), (jcx, cm), (jcx, j_y + hj)], "teal", sw=3)
    c.label((mx + mw + jcx) / 2, cm, "**e4 · computed**\nguard: `true`\ndelivery: **handle**", "teal", 12.5, 300)
    # the route
    c.arrow([(ox + ow, pc), (sx, pc)], "amber", sw=2.4, dash="7 5")
    c.label((ox + ow + sx) / 2, pc - 52, "`Route(e1)`\nor `Route(e2)`", "amber", 12.5, 140)
    c.label((ox + ow + sx) / 2, pc + 44, "only narrows", "amber", 12.5, 140)
    ky = dag_bot + 34
    ky += c.para(X0 + 30, ky, reg_w - 60,
                 "**The module's graph, drawn as its header draws it** (`Workflow.tla`): `s` the one decision point, "
                 "`c` outward, `j` the sink joined on `any`; lineages {A, B}, one seating that `Alternates` admits. "
                 "**A node is one round of one cell**; its task is promoted text whose slots only a handle fills, so "
                 "neither the orchestrator nor a worker writes a task (§1). **Every edge** is computed or chosen, carries "
                 "a guard and declares a delivery mode, `clear` or `handle`. **The graph is acyclic, checked at load**: "
                 "a loop such as draft-and-review is unrolled into a fixed number of nodes, so termination is a property "
                 "of the shape and a checker reaches every path; a graph with a cycle does not load (§1 ⟨K1⟩). A step "
                 "bound and a time bound `T_wf` bound the whole workflow, both placeholders (§1). At the reference the "
                 "same shape runs end to end, with scripted cells (A16).", 13.5, "muted") + 10
    c.legend(X0 + 30, ky, [("arrow", "blue", "the promotion grants a lease"),
                           ("arrow", "teal", "computed edge: the mechanism fires it"),
                           ("arrow", "amber", "chosen edge: an applied Route takes it"),
                           ("arrow", "amber", "Route: selects, only narrows", "7 5"),
                           ("box", "red", "outward node", None)], title="Key", maxw=reg_w - 60)
    reg_bot = c.ymax + 30
    c.region(X0, top, reg_w, reg_bot - top, "One promoted workflow (ADR-0054 §1–§3, Proposed)", "amber", size=15)

    # right column: context, §1, §2, the mesh pointer
    rbot = stack(c, rx, top, rw, [
        ("Why: every orchestration method in use chains agents by trusting something (Context)", [
            "Pipelines, graphs, supervisors, handoffs, group chats, agent-as-tool and A2A each let one model's output "
            "steer what runs next, or hand a transcript on, or let an agent call a subordinate with its own "
            "credentials. **Against the havoc premise (ADR-0007) the survivors are those in which agents never address "
            "each other and something that is not a model decides what runs next.**",
            "**CaMeL's split is kept and its trust removed**: its planner \"is trusted to write the plan\". Here the "
            "plan is a promoted artifact, and what is left of the planner may only choose among enabled edges.",
            "**The delegation gap closes in its cheaper form** (gap row 1.3; external assessment §5 item 2), on "
            "ratification: **a deployment that needs sub-agents seats each one by promoting a workflow** (§2).",
        ], "grey", {}),
        ("§2 · No principal grants another", [
            "**The only clause that adds authority**, and it adds none the quorum did not vote on. Every other clause "
            "the mechanism applies subtracts (status note).",
            "**Each lease is still granted, not merely activated**: confinement is appraised at that grant with a "
            "nonce from the log (ADR-0034 §3), and the grant refuses as any grant does. **A refused grant fails the "
            "node**; nothing grants it lower and no other seating stands in.",
            "**Subtractions reach nodes not yet started**: a rules-epoch change voids every lease not yet issued, as "
            "it voids votes in flight (ADR-0024 §3); a revocation of a principal, Persona or profile bars the leases "
            "that name it. The node fails and the workflow fails closed (§9).",
            "**Inside a workflow no operator makes successor grants**; `EndRound`, `Revoke` and `FenceEpoch` still "
            "reach every cell (ADR-0050 §4; ADR-0031 A4). A principal seated at several nodes holds one live lease, so "
            "its rounds are granted in log order.",
        ], "blue", {"status": "proposed", "status_extra": "ADR-0031 A4 · C1"}),
        ("A mesh widens this: D6", [
            "ADR-0055 (Proposed) lets a workflow of kind `mesh` have cycles, under an **activation budget** the "
            "promotion votes on; the activation becomes the unit, and the orchestrator holds no state (ToO rev 15 "
            "§2.11). **Drawn in D6.** The default kind stays the DAG drawn here.",
        ], "grey", {"status": "proposed", "dash": "6 4", "tint": False}),
    ], size=13.5)
    y = max(reg_bot, rbot) + 70

    # ================================================================== band 2: the orchestrator
    y = band(c, X0, y, "§3 · Edges are computed or chosen, and the orchestrator only narrows (K5, K8)",
             status="proposed", extra="ADR-0037 A5 · ADR-0040 A2 · ADR-0043 A3")
    lw_ = 1880
    th = c.table(X0, y, [("The orchestrator (§3, the record's table)", lw_ * 0.17, {"bold": True}),
                         ("As drafted", lw_ * 0.83)], [
        ["Seat kind", "**`orchestrator`**, Run only. ADR-0037 §4's table gains a sixth kind (drafter's choice: a new "
                      "kind, so that B10 and the delivery table bind it by kind)"],
        ["Alphabet", "`Route(edge)` and `Report`. No `Consult`, no `Actuate`. A new floor forbid refuses `Route` from "
                     "any other kind, and B10 already refuses it every authoring variant"],
        ["`Route(edge)`", "`edge` names a chosen edge of the workflow the lease names, out of the decision point the "
                          "round was granted for. No other argument ⟨K8⟩: tasks are templates, so there is nothing to "
                          "bind"],
        ["Rounds", "One round per decision point, granted by the promotion when the decision point is ready, ended when "
                   "its `Route` applies or its lease lapses. Decision points are served in log order, since a principal "
                   "holds one live lease (ADR-0031 §2) (drafter's choice)"],
        ["Ingress", "The task, from the promotion; the decision point's enabled chosen edges, each with its target's "
                    "interface (ADR-0048, from promoted text); the attributes its guards read, with their labels and the "
                    "basis index (§8); and a handle for each output. **Never bytes.** Its Listener's delivery table is a "
                    "mechanism constant, not bundle data, so no bundle can deliver it anything in the clear"],
        ["`clearSet`", "The task's label, and nothing else can enter it. R5 to R7 never bind it, because it has no "
                       "`Actuate`"],
        ["Its `Report`s", "Are written to its round topic for its Observer, and are never an input to any node (§5)"],
    ], size=13.5, accent="amber")
    c.para(X0, y + th + 12, lw_, "A **computed** edge fires when its guard holds, evaluated by the mechanism inside the "
           "apply of the entry that made it evaluable: one evaluation, at one log position, no gap. A **chosen** edge "
           "leaves a **decision point**, a node with more than one chosen outgoing edge; when it is ready the guards of "
           "its chosen edges are evaluated, and the orchestrator selects one among those whose guards hold. ADR-0043 "
           "A3 gives §2's Run table the row `orchestrator`: `Route`, `Report`; ADR-0039 A3 couples it as a Thinker is.",
           13.5, "muted")
    rx2 = X0 + lw_ + 50
    rw2 = X1 - rx2
    stack(c, rx2, y, rw2, [
        ("It can only narrow (§3; finding 2)", [
            "**It cannot enable an edge whose guard is false**, so every safety property must already hold for every "
            "enabled edge, whichever is taken. **It affects how good the work is and never whether it is safe.**",
            "**The safety argument needs nothing from the orchestrator**: it is in the record for quality alone, which "
            "is why it is optional. A graph of computed edges is run by the mechanism alone and has one Byzantine "
            "principal fewer (drafter's choice: a load check, not a judgment of necessity).",
        ], "amber", {}),
        ("`Route` is an emission (ADR-0015 A1, pending)", [
            "A typed record on the orchestrator's round topic, admitted and ordered; **the grant it leads to is the "
            "promotion's** (§2). Effects stay {tool invocation, principal emission}; authority changes stay "
            "{promotion, anchor issuance}. ADR-0040 A2: \"exactly three variants\" reads \"exactly four\".",
            "[[red|Finding 3, the doubt]]: `Route` strains the enumeration. It is ordered and recorded like an emission, "
            "and its consequence is a grant. **A C2 reviewer may read it as a third kind**; that is ADR-0015's C2 "
            "question.",
        ], "amber", {"status": "open", "status_extra": "finding 3 · C2"}),
    ], size=13.5)
    y = c.ymax + 70

    # ================================================================== band 3: attributes and guards
    y = band(c, X0, y, "§4 · Attributes are lifts, and guards read only what is settled (K6, K7)",
             status="proposed", extra="ADR-0047 A1 · ADR-0042 A3")
    lw_ = 1680
    acols = [("Attribute (§4, the record's table)", lw_ * 0.22, {}), ("Kind", lw_ * 0.12, {"bold": True}),
             ("What it is", lw_ * 0.66)]
    arows = [
        ["`end`", "Observed", "How the round ended: `outcome`, `expired`, `fenced`, `revoked`"],
        {"cells": ["`actuates``, denials` ⟨R6⟩", "Observed", "Counts A count ⟨R6⟩, bounded by the round bound `R`"],
         "accent": "amber"},
        ["`label`", "Observed", "The worker's `clearSet` at its seal"],
        ["`covered`", "Observed", "Its cell Observer has reported coverage to the seal (§7)"],
        ["`found`", "Observed", "A finding has been ordered against the round. **The one attribute that changes after "
                                "the end, and only from false to true**"],
        {"cells": ["`outcome`", "**Declared**", "A value from the node's closed enum, declared in the workflow, taken from "
                                                "the typed `outcome` field of the worker's `Report`; `none` if none was "
                                                "made"], "accent": "red"},
        ["`output`", "Handle", "A handle on the node's `Report`s, labelled as §5 says"],
    ]
    th = c.table(X0, y, acols, arows, size=13.5, accent="amber")
    # strike ", denials" and "Counts" as the record strikes them (lib has no strikethrough markup)
    r_top = y + c.table(X0, y, acols, arows[:1], size=13.5, draw=False)
    base = r_top + 9 + 13.5 - 2 - 4.6
    wm = 0.602 * 13.5 * 0.92
    c.line(X0 + 9 + 8 * wm, base, X0 + 9 + 17 * wm, base, "ink", sw=1.5)
    x3 = X0 + acols[0][1] + acols[1][1] + 9
    c.line(x3 - 1, base, x3 + text_width("Counts", 13.5) + 1, base, "ink", sw=1.5)
    yp = y + th + 12
    yp += c.para(X0, yp, lw_, "**Struck as the record strikes them** ⟨R6⟩: **`denials` was dropped on 2026.10.09** by the "
                 "custodian's decision. It had no replicated source: a denial is written to the round topic by the "
                 "replica that refused it and is never ordered (ADR-0015; ADR-0051 §5), so no replica holds a count "
                 "every replica agrees on; `R` bounds admits, not denials; and the count was the worker's to choose, by "
                 "making requests it knew would be refused. Denials stay on the topic for the Observer and the "
                 "correlator, outside any guard. ADR-0047 A1 drops the word; **at the reference, A17** (`749d54f`; "
                 "`mechanism/` finding 22, where the reference had lifted 0).", 13.5, "ink") + 8
    c.para(X0, yp, lw_, "Lifted by the mechanism in one log entry when a node's round ends: a fixed set, "
           "**never declared by policy** (ADR-0047 R13), **none of them a literal** ⟨K6⟩. **A syntactic lift fixes an "
           "attribute's form, not its honesty**: observed attributes are facts no principal chose; `outcome` is chosen "
           "by a Byzantine worker, and §5's routing rule is what bounds that choice. Guards should prefer observed "
           "attributes. **Policy reads none of them** (ADR-0047 A1).", 13.5, "muted")
    rx3 = X0 + lw_ + 50
    rw3 = X1 - rx3
    g3 = 24
    w3 = (rw3 - g3) / 2
    specs = [
        ("The guard language (§4)", [
            "A predicate in a **fixed, decidable language**: equality and set membership over enums and labels, "
            "comparison of bounded counts with constants (after R6, `actuates` alone), and the connectives.",
            "**No strings, no arithmetic, no temporal operator.**",
            "**The mechanism evaluates guards; they are not policy** (drafter's choice), so they are among the "
            "mechanism checks ADR-0033 §4 re-runs at apply (§8). Guards as Cedar, re-checked by freezing their input, "
            "was not taken: two mechanisms where one does (Options).",
        ], "teal", {}),
        ("Settled guards: the source and its dominators (§4)", [
            "**A guard reads only the attributes of the edge's source and of the nodes that dominate it**, those on "
            "every path from the root to the source. They have all ended before the source is ready, so the set is "
            "settled when the guard is first evaluable. **A join on `any` cannot read a branch that may still be "
            "running.**",
            "Every attribute but `found` is written once, and `found` only subtracts, so **a guard's value cannot "
            "change after it is first evaluable except towards disabled. §8 rests on that** (finding 4).",
        ], "teal", {}),
    ]
    hh = max(c.card(0, 0, w3, t, b, draw=False, size=13.5) for t, b, _, _ in specs)
    for i, (t, b, acc, k) in enumerate(specs):
        c.card(rx3 + i * (w3 + g3), y, w3, t, b, accent=acc, size=13.5, h=hh, **k)
    yy = y + hh + 16
    specs = [
        ("A node's round may end on its outcome (§4; ADR-0042 A3)", [
            "Run has no terminal variant (ADR-0040 §4). Here **the admit of a `Report` carrying `outcome` ends the "
            "worker's lease**: a subtraction, ordered, needing no quorum (drafter's choice); an applied `Route` ends "
            "the orchestrator's round. Both seal; a void route ends nothing. Without it every node runs to its TTL. "
            "It reverses in effect \"the principal cannot end its own round\" at a workflow node (C3).",
        ], "amber", {}),
        ("Finding 7 · without write-once attributes, the orchestrator loops for ever", [
            "Under `M_REWRITE` a worker that flips its outcome after its node ended lets a route be **decided** while "
            "it reads `ok`, **voided** at apply when it reads `bad`, and decided again. Each void is ordered, so the log "
            "grows without bound: **an unbounded run reached depth 665 after thirteen hours** with its queue still level. "
            "Settled guards bound how much work the re-check can be made to do.",
        ], "red", {"tint": False}),
    ]
    hh2 = max(c.card(0, 0, w3, t, b, draw=False, size=13.5) for t, b, _, _ in specs)
    for i, (t, b, acc, k) in enumerate(specs):
        c.card(rx3 + i * (w3 + g3), yy, w3, t, b, accent=acc, size=13.5, h=hh2, **k)
    y = c.ymax + 70

    # ================================================================== band 4: the re-check at apply
    y = band(c, X0, y, "§8 · A route is checked again where it is applied, and §9 · completion is not success",
             status="proposed", extra="ADR-0033 §4's rule · ADR-0040 A2")
    lw_ = 1880
    # the log, with the race
    c.text(X0, y + 17, "**The race the second check closes** (§8): one replica decides, the route commits at a log "
           "position, every replica applies it there (ADR-0033 §4)", 16, "ink")
    ly = y + 40
    gap4 = 60
    cw4 = (lw_ - 2 * gap4) / 3
    steps = [
        ("Index 103 · decided", "amber", [
            "One replica decides `Route(e1)`: the orchestrator's lease live, epoch and fence current, the workflow "
            "running, the decision point not consumed, and e1 enabled.",
            "The route carries its **basis**, the log index of the attribute state the orchestrator was shown.",
        ]),
        ("Index 104 · a finding is ordered", "pink", [
            "Against `s`, from **a correlator, or the cell Observer's late one**: coverage does not stop it, because it "
            "lands after coverage (§7).",
            "`found` moves from false to true: the guard's read set has moved **towards disabled**, and only that way.",
        ]),
        ("Index 105 · applied, and void", "green", [
            "Every replica runs the mechanism checks again. **e1 is no longer enabled: a finding against its source. "
            "The route is void**: ordered, recorded, without effect.",
            "**After a void the decision point stays open**; the orchestrator may route again while its lease is "
            "live, and if no chosen edge remains enabled the decision point fails.",
        ]),
    ]
    h4 = max(c.card(0, 0, cw4, t, b, draw=False, size=13.5) for t, _, b in steps)
    for i, (t, acc, b) in enumerate(steps):
        x = X0 + i * (cw4 + gap4)
        c.card(x, ly, cw4, t, b, accent=acc, size=13.5, h=h4, tint=(acc != "green"))
        if i < 2:
            c.arrow([(x + cw4, ly + 40), (x + cw4 + gap4, ly + 40)], "grey", sw=2.2)
    tly = ly + h4 + 40
    c.line(X0, tly, X0 + lw_, tly, "grey", sw=2.4)
    for i, lab in enumerate(["103", "104", "105"]):
        tx = X0 + i * (cw4 + gap4) + cw4 / 2
        c.line(tx, ly + h4, tx, tly + 10, "grey", sw=1.6, dash="3 3")
        c.label(tx, tly + 26, f"log index {lab}", "grey", 12.5)
    c.text(X0 + lw_, tly - 10, "the log", 13, "faint", anchor="end", bold=True)
    oy = tly + 62
    wo = (lw_ - 40) / 2
    outs = [
        ("With the second check (ADR-0054 §8)", "green", [
            "The finding is not overtaken. `FindingPrecedesNoRoute` holds over all 106,199 states, and the witness "
            "`NeverVoidedByFinding` is reached **with coverage in force** (§7).",
        ]),
        ("Without it: `M_DECIDEONLY`", "red", [
            "The workflow continues past a node the finding was meant to stop: **ADR-0033 §4's revocation race**. "
            "TLC: `M_DECIDEONLY` breaks `AppliedRouteEnabled`, `FindingPrecedesNoRoute` and `OneRoutePerDecision`, "
            "and nothing else (3,237,513 states).",
        ]),
    ]
    ho4 = max(c.card(0, 0, wo, t, b, draw=False, size=13.5) for t, _, b in outs)
    for i, (t, acc, b) in enumerate(outs):
        c.card(X0 + i * (wo + 40), oy, wo, t, b, accent=acc, size=13.5, h=ho4, tint=(i == 0),
               dash=None if i == 0 else "6 4")
    left_bot = oy + ho4
    # right: what a route needs, and the rules
    rx4 = X0 + lw_ + 50
    rw4 = X1 - rx4
    ry = y
    ry += c.card(rx4, ry, rw4, "At decide, and again at apply, a route needs (§8)", [
        "the orchestrator's lease live, epoch and fence current ∧ the workflow running ∧ the decision point not "
        "consumed ∧ **the edge enabled**: its source ended and covered, its guard true, the routing rule satisfied, no "
        "finding against its source or any ancestor",
        "Because guards are settled (§4), **only subtractive events can make that false between the two**: a finding, "
        "a revocation or lapse, a fence, the workflow ending, or another `Route` consuming the decision point first.",
    ], accent="teal", size=13.5, bullets=False) + 16
    ry += c.card(rx4, ry, rw4, "The rules around it (§8)", [
        "**One route per decision point.** A Byzantine orchestrator may send two; the first to apply consumes the "
        "decision point and the second is void (`M_NOCONSUME`).",
        "**A route carries its basis.** Safety does not need it, since the choice is havoc over enabled edges; "
        "forensics does: an Observer and a replay can see what the orchestrator was shown. With settled guards, basis "
        "and apply agree on every attribute a guard reads (`BasisStable`).",
        "**Computed edges never go stale**: decided and applied in one step (§3).",
        "**A lapsed orchestrator takes no default edge.** Its lease ends with the decision point open, and the "
        "decision point fails. An edge taken on a timeout would be **a grant made by a timeout**, which ADR-0024 §2 "
        "forbids (`M_DEFAULT`). **A Byzantine orchestrator can stall a workflow and cannot misroute it.**",
    ], accent="amber", size=13.5) + 16
    ry += c.card(rx4, ry, rw4, "§9 · The mechanism decides completion, and completion is not success", [
        "**Completes** when every sink has ended or been skipped and at least one has ended. **Fails** when a node "
        "fails, a decision point fails, a grant is refused, the epoch is fenced, or `T_wf` or the step bound passes. "
        "**A timeout is always a failure** (`M_TIMEOUTDONE`).",
        "**Completion says the graph was traversed, not that the work is right.** Whether it is right is an Observer "
        "finding, deny-only, as ever. A workflow's failure stops nothing else: every lease ends by its own path, and "
        "no other workflow is touched.",
    ], accent="green", size=13.5)
    y = max(left_bot, ry) + 70

    # ================================================================== band 5: labels, lineage, coverage
    y = band(c, X0, y, "§5–§7 · Labels cross cells along the edges; lineages alternate where content is read in the "
                       "clear; an edge waits for coverage", status="proposed",
             extra="ADR-0043 A3 · ADR-0047 A1 · ADR-0035 R8 · ADR-0039 A3")
    g5 = 30
    w5 = (WW - 3 * g5) / 4
    specs = [
        ("§5 · A worker's output is the next node's input ⟨K9⟩", [
            "Run's ingress (ADR-0043 §1) gains **a fifth item, `input`**: a predecessor's output, delivered to a node "
            "along an edge. The list stays closed (ADR-0043 A3; C2).",
            "**Its label is the reporting worker's `clearSet` at the `Report`'s emit.** `clearSet` only grows, so this "
            "is the sound bound ADR-0047 §1 already uses for a literal: whatever the worker read in the clear before "
            "writing may be in what it wrote. Not declared (ADR-0047 A1).",
            "**Its delivery mode is the edge's**, and the receiving bundle's table may only narrow it, clear to handle "
            "(ADR-0041 A4 §5).",
            "**A task slot takes a handle**; the task's label is the template's joined with every handle's in it.",
        ], "amber", {}),
        ("R5 to R7 follow content across cells", [
            "**An item delivered clear joins the receiver's `clearSet`**, so the label forbids bind downstream: an "
            "untrusted read at `s` delivered clear to `b` makes `b`'s outward call face `R5` to `R7`.",
            "That is the path ADR-0051 finding 2 says the floor cannot see between two cells; **along a workflow's own "
            "edges it now can**.",
            "[[red|Not covered]]: an injection that changes what a worker says in a `Report` (ToO §2.10). The workflow "
            "makes that gap carry weight, because the `Report` now travels. **The label bounds where it can go, not "
            "what it says.**",
        ], "red", {"tint": False}),
        ("The routing rule over labels (§5)", [
            "(drafter's choice: the routing analogue of R6) **An edge whose target's lease reaches an outward entry, "
            "or receives `restricted` input, is disabled when any attribute its guard reads is labelled "
            "`untrusted`.**",
            "An attribute's label is its source's: the node's `label` for every attribute, because a declared "
            "`outcome` was chosen by a worker that read what its label says; observed ones are kept at the same label "
            "for simplicity (drafter's choice).",
            "**Finding 6**: the label of `outcome` is coarse. A workflow that touches untrusted content early may find "
            "its outward edges disabled for the rest of the graph. That is the rule working, and it will be felt.",
        ], "amber", {}),
        ("§6 · Lineages alternate on clear edges ⟨K3⟩ ⟨K4⟩", [
            "**For every `clear` edge u→v, u's and v's Thinker Personas satisfy ADR-0035's independence rule**, E1 to "
            "E5; within every cell Thinker and Observer are independent. A handle edge carries no bytes, and diversity "
            "on it buys nothing.",
            "With two lineages the Thinkers along clear edges alternate and each Observer takes the other: the "
            "archetype's two (ADR-0017), enough for any workflow whose clear edges are bipartite.",
            "**Enforced at the promotion tally**, where refusal stalls (ADR-0035 R8). **ADR-0035 is Proposed, so it "
            "cannot be enforced yet: every deployment today declares D-0054-1.**",
            "[[red|Open]] (finding 5): must parallel branches a join compares in the clear differ from each other?",
        ], "violet", {"status": "proposed", "status_extra": "ADR-0035 R8 · declared, D-0054-1"}),
    ]
    h5 = max(c.card(0, 0, w5, t, b, draw=False, size=13.5, status=k.get("status")) for t, b, _, k in specs)
    for i, (t, b, acc, k) in enumerate(specs):
        c.card(X0 + i * (w5 + g5), y, w5, t, b, accent=acc, size=13.5, h=h5, **k)
    y += h5 + 30
    lw_ = 1300
    c.card(X0, y, lw_, "§7 · An edge waits for its source's coverage (ADR-0039 A3)", [
        "ADR-0039 §2 grants a Thinker's next round only once a cell Observer has read its last round to the seal. **An "
        "edge is the workflow's next round**, so it is enabled only when its source's `covered` is true, and a cell "
        "Observer's finding lands before any successor runs.",
        "**It does not close §8's race**: a correlator's finding, or a cell Observer's late one, may still be ordered "
        "after coverage. `M_UNCOVERED` breaks only `EdgeAfterCoverage`, and `FindingPrecedesNoRoute` still holds "
        "without coverage: the re-check is what holds it.",
        "**Cost**: a node's Observer's lag, at every step of a workflow (Consequences).",
    ], accent="pink", size=13.5)
    rx5 = X0 + lw_ + 50
    rw5 = X1 - rx5
    c.text(rx5, y + 16, "**§10 · Degeneracy on this record** (the record's table)", 16, "ink")
    t10 = c.table(rx5, y + 30, [("Id", rw5 * 0.08, {"bold": True}), ("Kind", rw5 * 0.08),
                                ("Parameter → deployed value", rw5 * 0.24), ("Premises falsified", rw5 * 0.18),
                                ("Theorems voided", rw5 * 0.12), ("Type changes (ADR-0023 §6b)", rw5 * 0.30)], [
        {"cells": ["D-0054-1", "Declaration", "Lineage alternation on clear edges: enforced at the tally → declared. "
                   "**Every deployment today**, since ADR-0035 is Proposed", "A clear edge joins independent lineages",
                   "`PromotedAlternates`", "None. Alternation is not a conjunct of `Contained`"], "accent": "violet"},
        ["D-0054-2", "Deployment", "Coverage at the edge: required → waived, for a deployment whose Run budget cannot "
                                   "wait for a node's Observer to reach the seal",
         "An edge is enabled only after its source is covered", "`EdgeAfterCoverage`",
         "None. §8 still voids a route on a finding; a finding that lands after the successor starts stops only what "
         "follows"],
    ], size=13.5, accent="red")
    c.para(rx5, y + 30 + t10 + 10, rw5, "Turning every edge to `handle` is not a degeneracy: it narrows, and it makes §6 "
           "vacuous. **At the reference** lineage is a declared tag compared at load (I49 (b); no independence table, "
           "G18), and D-0054-2 is not built.", 13.5, "muted")
    y = c.ymax + 70

    # ================================================================== band 6: the floor's workflow stage
    y = band(c, X0, y, "The floor's `workflow` stage: built, gated, linked by the reference, and not in force "
                       "(ADR-0041 A4; G11 §2.2)", status="proposed", extra="not in force · G11 item 102")
    lw_ = 1100
    hc = code(c, X0, y, lw_, [
        '@id("R8-route-own-decision")',
        'permit (principal, action == Topak::Action::"Route", resource)',
        'when {',
        '  principal.domain == "run" &&',
        '  context.lease.alphabet.contains("Route") &&',
        '  resource.chosen &&',
        '  context.decisionPoint.contains(resource.source)',
        '};',
        '',
        '@id("R9-only-orchestrators-route")',
        'forbid (principal, action == Topak::Action::"Route", resource)',
        'when { principal.kind != "orchestrator" };',
        '',
        '@id("R3-observer-live")',
        'forbid (principal,',
        '  action in [Topak::Action::"Actuate", Topak::Action::"Report",',
        '             Topak::Action::"Route"],',
        '  resource)',
        'when { (principal.kind == "thinker" || principal.kind == "orchestrator")',
        '       && !context.observerLive };',
    ], "amber", dash="6 4")
    c.para(X0, y + hc + 10, lw_, "`floor/proposed/workflow-floor.cedar`, as built by `build.py`. **Whether the edge is "
           "enabled is not policy**: the floor sees only that the edge is the lease's to choose; the guard is a "
           "mechanism check, re-run at apply (ADR-0041 A4).", 13.5, "muted")
    mx6 = X0 + lw_ + 50
    mw6 = 1050
    t6 = c.table(mx6, y, [("Entry ⟨ADR-0041 A4, pending⟩", mw6 * 0.33, {"mono": True}), ("Kind", mw6 * 0.13),
                          ("Holds when", mw6 * 0.54)], [
        ["R8-route-own-decision", "permit", "the seat's domain is `run`, the lease's alphabet contains `Route`, and the "
                                            "edge is a chosen edge out of the decision point the lease was granted for "
                                            "(ADR-0054 §3)"],
        ["R9-only-orchestrators-route", "forbid", "the seat's kind is not `orchestrator` (ADR-0054 §3, §12)"],
        ["R3-observer-live", "forbid, widened", "refuses `Actuate`, `Report` **and `Route`** under a `thinker` **or "
                                                "`orchestrator`** seat with no live cell Observer (ADR-0039 A3)"],
        {"cells": ["B10-only-thinkers-author", "forbid", "**Unchanged**: already refuses an `orchestrator` seat "
                                                          "`Actuate` and every authoring variant"], "accent": "grey"},
        {"cells": ["schema S", "—", "The kind `orchestrator`; entities `WorkflowNode` and `Edge` (`source`, `chosen`); "
                   "`RunCtx.decisionPoint`, a set holding the lease's node, **empty for every other seat**; `Route` over "
                   "a `Seat` and an `Edge`. **Nothing a guard reads enters `RunCtx`** (ADR-0041 A4 §4, R3)"],
         "accent": "grey"},
    ], size=13.5, accent="amber")
    c.para(mx6, y + t6 + 12, mw6, "Floor `10ea6818af9b4efe`, schema `fd394bb8c074eec2`: **30 policies, 123 cases**, "
           "built on `emergency`, whose bytes are unchanged. Every gate passes on 2026.10.08 (`878d9a431fec9eb9`; a "
           "rerun reproduces it byte for byte): totality, non-vacuity and discrimination for `Route`, every entry "
           "matters, the routing and negative and checker controls; **22 unsat with a checked proof, no holds without "
           "one**. `floor/lean` states it under Cedar's verified model, its 123 cases (G11 §3), which ratifies "
           "nothing.", 13.5, "muted")
    rx6 = mx6 + mw6 + 50
    rw6 = X1 - rx6
    t6b = c.table(rx6, y, [("Routing control for the new entries (`run-gates.py`)", rw6 * 0.6),
                           ("Classed", rw6 * 0.4, {"bold": True})], [
        ["R9 removed: any seat with `Route` may route", "relaxation → anchor issuance + promotion"],
        ["R8 without the decision-point condition", "relaxation → anchor issuance + promotion"],
        ["R8 admits a computed edge", "relaxation → anchor issuance + promotion"],
        ["R3 couples Thinkers only, as before", "relaxation → anchor issuance + promotion"],
        ["No `Route` after reading untrusted", "tightening → ordinary promotion"],
        ["The kind test moved into R8", "equivalent → ordinary promotion: R9 is the same kind test inside R8"],
    ], size=13.5, accent="amber")
    ry6 = y + t6b + 16
    c.card(rx6, ry6, rw6, "Proposed, and linked (G11 item 102; ADR-0033 A16)", [
        "**The floor in force is `emergency`** (28 policies, 107 cases), genesis-provisional. Nothing ratified loads "
        "`workflow`: it is in force only with ADR-0054 and ADR-0041 A4.",
        "**The reference links it, at the custodian's direction** (2026.10.08), so the floor the reference follows is "
        "not the floor in force. Every Run request lifts `decisionPoint`.",
        "[[red|Wrong comment]]: the stage file opens \"not what the reference follows\", and of this stage that is now "
        "false (G11 §2.2, item 91).",
    ], accent="amber", size=13.5, status="proposed", status_extra="not in force")
    y = c.ymax + 70

    # ================================================================== band 7: Workflow.tla
    y = band(c, X0, y, "`spec/Workflow.tla`: ten properties, nine mutations, ten witnesses, checked by TLC and "
                       "not proved (ADR-0054 §12; R1, R2)", "violet")
    c.pill(X0 + text_width("`spec/Workflow.tla`: ten properties, nine mutations, ten witnesses, checked by TLC and "
                           "not proved (ADR-0054 §12; R1, R2)", 22, True) + 20, y - 50, "Checked · no proof module",
           "violet", 11.5)
    PROPS = ["AppliedRouteEnabled", "OneRoutePerDecision", "FindingPrecedesNoRoute", "ChosenOnlyByRoute",
             "EdgeAfterCoverage", "TaintedNeverOutward", "GrantUnderPromotion", "PromotedAlternates",
             "CompletedOnlyBySink", "BasisStable"]
    short = ["Applied", "OneRoute", "Finding", "Chosen", "Coverage", "Tainted", "Grant", "Alternates", "Sink", "Basis"]
    MUT = [("M_DECIDEONLY", "the checks run at decide and not again at apply", {0, 1, 2}, "3,237,513"),
           ("M_NOCONSUME", "apply does not check that the decision point is unconsumed", {0, 1}, "1,503,583"),
           ("M_DEFAULT", "a lapsed orchestrator's open decision takes the first enabled chosen edge", {3}, "145,485"),
           ("M_UNCOVERED", "an edge is enabled without its source's coverage", {4}, "935,588"),
           ("M_NOTAINT", "guards ignore the labels of what they read", {5}, "199,760"),
           ("M_GRANTANYEPOCH", "a ready node is granted under any rules epoch", {6}, "138,695"),
           ("M_NOLINEAGE", "the promotion gate does not check lineages", {7}, "212,397"),
           ("M_TIMEOUTDONE", "a failed decision completes the workflow", {8}, "106,199"),
           ("M_REWRITE", "a worker may rewrite its status attribute after its node has ended", {9},
            "5,016,678 under `CapLog`")]
    lw_ = 2280
    pcw = 118
    first = lw_ - 10 * pcw - 250
    cols = [("Mutation (one TLC run per broken property; one run of the rest)", first)] + \
        [(s_, pcw) for s_ in short] + [("Rest: distinct states", 250)]
    rows = [{"cells": ["**none** · `Safe`, the conjunction: [[green|holds]], depth 21"] + ["[[green|holds]]"] * 10 +
             ["106,199"], "accent": "green"}]
    for m, d, br, st in MUT:
        cells = [f"`{m}` · {d}"] + [BR if i in br else HO for i in range(10)] + [st]
        rows.append({"cells": cells, "accent": "amber"} if m == "M_REWRITE" else cells)
    ty7 = y
    tm = c.table(X0, ty7, cols, rows, size=13.5, accent="violet")
    yy = ty7 + tm + 10
    yy += c.para(X0, yy, lw_, "Columns, in order: " + "; ".join(f"`{p}`" for p in PROPS) + ". **Each mutation breaks "
                 "the property it is about, and every mutation is shown to break nothing else**: `M_DECIDEONLY` three, "
                 "`M_NOCONSUME` two, the rest one each. **`M_UNCOVERED` breaks only `EdgeAfterCoverage`**: without "
                 "coverage `FindingPrecedesNoRoute` still holds, which is §7's claim that coverage does not close the "
                 "race and the re-check does. **The one bounded row**: under `M_REWRITE` the log has no bound (finding "
                 "7), so its remainder is checked under the state constraint `CapLog` (`idx ≤ 6`), the furthest the "
                 "unmutated module reaches, by the custodian's decision (R2).", 13.5, "muted") + 14
    wit = [("NeverRouted", "a route is applied", "7"), ("NeverCompleted", "the workflow completes", "14"),
           ("NeverVoidedByFinding", "a route void at apply: a finding between decide and apply, after coverage", "8"),
           ("NeverVoidedByConsumed", "a route void: another consumed the decision point first", "9"),
           ("NeverVoidedByLease", "a route void: the orchestrator's lease or the epoch moved", "8"),
           ("NeverDecisionFailed", "the orchestrator lapses with the decision open, and it fails", "6"),
           ("NeverOutward", "the outward node is reached, under a trusted attribute", "7"),
           ("NeverComputed", "a computed edge fires", "11"),
           ("NeverRefusedAtGrant", "a ready node is refused at grant after a fence", "5"),
           ("NeverLogSix", "the log reaches index 6, so `CapLog` cuts nothing the module does", "18")]
    half = (lw_ - 20) / 2
    for j in range(2):
        c.table(X0 + j * (half + 20), yy, [("Witness (must be violated)", half * 0.34, {"mono": True}),
                                           ("Reached (counterexample ✓)", half * 0.54), ("TLC depth", half * 0.12)],
                [[a, b, d] for a, b, d in wit[j * 5:(j + 1) * 5]], size=13.5, accent="violet")
    yy = c.ymax + 12
    c.para(X0, yy, lw_, "**The tenth witness's partner**: `LogReach` (`idx ≤ 6`) **holds** over all 106,199 states with "
           "no mutation, so the cap's justification is in the results and not in a probe. `spec/Workflow-results-"
           "2026.10.08.txt`: **33 rows** from `Workflow-rows.txt`, TLC 2.19.", 13.5, "muted")
    rx7 = X0 + lw_ + 50
    rw7 = X1 - rx7
    ry = y
    ry += c.table(rx7, ry, [("Property (the module's header)", rw7 * 0.44, {"mono": True}),
                            ("States", rw7 * 0.56)], [
        ["AppliedRouteEnabled", "every applied Route names an edge enabled at its apply position"],
        ["OneRoutePerDecision", "a decision point is consumed at most once"],
        ["FindingPrecedesNoRoute", "no Route applies after a finding against its source or an ancestor"],
        ["ChosenOnlyByRoute", "a chosen edge's target is activated only by an applied Route: no default edge"],
        ["EdgeAfterCoverage", "no node is activated by an edge whose source's round is unread to the seal"],
        ["TaintedNeverOutward", "no outward node is activated by an edge whose guard read an untrusted attribute"],
        ["GrantUnderPromotion", "every node granted was granted under the promotion's rules epoch"],
        ["PromotedAlternates", "a promoted seating alternates lineages on every clear edge, and no cell's Observer "
                               "shares its Thinker's lineage"],
        ["CompletedOnlyBySink", "a workflow completes only when its sink has ended"],
        ["BasisStable", "what an applied Route was decided on is what holds when it applies"],
    ], size=13, accent="violet") + 16
    c.card(rx7, ry, rw7, "Checked, not proved", [
        "**There is no proof module.** Proofs of the ten properties are an open obligation (ADR-0054 §12 \"Not met\"; "
        "Open obligations), and `spec/proof-sync.sh` exits 1 for want of a reason (G11 item 101). No binding row in "
        "`theorem-premise-binding.md` (item 90).",
        "**Model**: `Nodes` = {s, b, c, j}, lineages {A, B}, one fence; orchestrator and workers havoc. **Not "
        "modelled**: more than one decision point; multi-select; `all` joins and skips; the orchestrator's own seating "
        "and rounds; Run admits inside a round; attestation at grant; the step and time bounds; erasure. Deadlock is "
        "not checked: a workflow may stall, and stalling is safe.",
        "**R1**: the module was corrected twice before the rows were kept (`M_NOCONSUME` once skipped decide too; a "
        "stale route could re-activate a node). Freezes at ADR-0054's ratification (G11 §3).",
    ], accent="violet", size=13.5)
    y = c.ymax + 70

    # ================================================================== band 8: the reference
    y = band(c, X0, y, "At the reference: built to a Proposed record, on a floor not in force (ADR-0033 A16, A17, "
                       "both pending)", "teal", status="built", extra="A16 · A17 pending")
    th = c.table(X0, y, [("Debt (A16's table, and A17's row)", WW * 0.16, {"bold": True}), ("Record", WW * 0.11),
                         ("What the reference does now", WW * 0.47), ("Checked by", WW * 0.26)], [
        ["A workflow is a promoted artifact, and a malformed one does not load", "ADR-0054 §1; ADR-0055 §1",
         "`WorkflowLoad` takes the text of a single-file workspace and loads it only if that workspace's artifact was "
         "promoted by tally, as a profile is. A `dag` with a cycle, a `mesh` with no budget, an orchestrator without a "
         "chosen edge or a chosen edge without one, a guard reading a node that does not dominate its source, a "
         "seating whose kind or alphabet is wrong, and a clear edge with one declared lineage on both ends do not load",
         "`workflow.rs` (18): `a_workflow_loads_only_promoted_and_well_formed`, `a_mesh_loads_only_with_a_budget_and_"
         "two_coloured_clear_edges`; e2e `a_workflow_is_run_by_its_promotion`, step 1"],
        ["The promotion grants every lease", "ADR-0054 §2; ADR-0024 A4; ADR-0031 A4",
         "`WorkflowGrant`: a replica's driver proposes the grant of each ready slot, a node's activation or an "
         "orchestrator's decision event, served in log order; apply rebuilds the request from the seating and requires "
         "equality, with the task's label joined with the clear inputs'. A refusal by the budget or a grant check fails "
         "the slot; a fence fails what is not yet granted", "`a_fence_fails_a_node_not_yet_granted`; e2e steps 3, 4, 6, 7"],
        ["Edges computed or chosen; `Route` checked again at apply", "ADR-0054 §3, §8; ADR-0040 A2; ADR-0015 A1",
         "An `orchestrator` seat holds `Route` and `Report`. A route is stamped with its workflow, event and basis, "
         "checked at decide and again at apply, and void if it fails: the round is the event's, the event not consumed, "
         "the edge chosen and enabled. An applied route consumes the event, enters its target and ends the round. A "
         "computed edge is evaluated once, inside the apply that makes it evaluable",
         "`a_route_applies_and_the_workflow_completes_by_its_sink`, `a_route_decided_before_a_finding_and_applied_after_"
         "is_void`, `a_second_route_to_a_consumed_decision_point_is_void`, `a_lapsed_orchestrator_fails_its_decision_"
         "point`, `a_computed_edge_fires_on_a_typed_attribute`, `only_the_orchestrator_routes_and_only_its_own_"
         "decision`; `topak-floor/tests/workflow.rs` (3); e2e step 5"],
        ["Attributes lifted at a round's end; the round ends on its outcome", "ADR-0054 §4; ADR-0042 A3; ADR-0047 A1",
         "A worker's `Report` with an `outcome` from its node's enum ends its round, and the record is the last before "
         "the seal. `end`, `actuates`, `label`, `outcome` and `output` are lifted once", "e2e step 3"],
        ["Labels cross cells; the routing rule", "ADR-0054 §5; ADR-0043 A3",
         "A clear input's label joins the receiver's `clearSet` at grant, and the floor's `R5` then binds its outward "
         "call. An edge into an outward node, or one carrying restricted content in the clear, is disabled by an "
         "untrusted attribute its guard reads",
         "`an_untrusted_attribute_disables_the_edge_into_an_outward_node`, `a_clear_input_joins_the_receivers_clear_"
         "set`; `a_clear_input_raises_the_receivers_clear_set_and_r5_then_refuses_its_outward_call`"],
        ["Coverage at the edge; the orchestrator coupled", "ADR-0054 §7; ADR-0039 A3",
         "No edge out of a round before its cell Observer has read it to the seal. An `orchestrator` seat has a cell, "
         "`R3`, a seal and the cross-round rule, as a Thinker does",
         "`an_edge_waits_for_its_sources_coverage`; `a_route_is_decided_by_r8_r9_and_r3`"],
        {"cells": ["Activations, causal history, the budget; the mechanism tracks", "ADR-0055 §2, §3, §6",
                   "One engine for both kinds: each node run is an activation with its trigger and causal history; a "
                   "guard reads the history and never a node's latest value; a finding closes every edge downstream; "
                   "every lease is charged, orchestrator rounds included; one orchestrator round per event, told the "
                   "track and never bytes (the mesh: D6)",
                   "`the_loop_turns_twice_and_exits`, `the_budget_refuses_a_grant_and_the_workflow_fails`, "
                   "`an_orchestrator_round_is_charged`, `a_finding_against_the_workers_round_voids_the_decision_nodes_"
                   "next_route`, `a_route_decided_in_one_round_and_committed_after_it_ends_is_void`, "
                   "`untrusted_content_read_on_the_loop_disables_the_exit`"], "accent": "grey"},
        ["A finding the mechanism can read", "ADR-0054 §4's `found`; G12",
         "An observer seat's `{\"finding\": {\"topic\": …}}`, read by shape as a heartbeat is, against a round in its "
         "reach", "the finding tests above"],
        {"cells": ["A17: \"`actuates` is the one count a guard compares\"", "ADR-0054 §4, R6; ADR-0047 A1",
                   "`Attributes` loses `denials` and `Counter` loses `Denials`, so a guard that names a denial count does "
                   "not parse and no attribute is lifted as 0. A denial is still written to the round topic and still "
                   "not ordered; the correlator and the Observer read it there", "`workflow.rs` (18), unchanged; the "
                                                                                 "whole suite"], "accent": "amber"},
    ], size=13.5, accent="teal")
    c.para(X0, y + th + 12, WW, "A16: `mechanism/` and `policies/` at **`11aaf6a`**, manifest `SHA256SUMS-REF-2026.10.08` "
           "(116 entries, `9357abd49333459a`), on the `workflow` stage; **155 tests across fifteen binaries**, up from "
           "133 (eighteen in `topak-core/tests/workflow.rs`, three in `topak-floor/tests/workflow.rs`, one e2e); the "
           "Rego tests A15's 38, unchanged. A17: **`749d54f`**, `SHA256SUMS-REF-2026.10.09` (`809c66beda3cdc6a`), three "
           "entries changed, 155 tests, none failing. **Seen at the replicated state, not end to end**, all but one: the "
           "e2e run shows the four-node workflow promoted, loaded and run across three replicas by scripted cells (a "
           "computed edge on a typed attribute, a route admitted by `R8`, a second route refused, completion by the "
           "sink). **Nothing in force is discharged.**", 13.5, "muted")
    y = c.ymax + 24
    g8 = 30
    w8 = (WW - 3 * g8) / 4
    specs = [
        ("What is the reference's own (`mechanism/` I49)", [
            "**(a)** PROVISIONAL (finding-record): no record fixes a finding's form; the shape is a heartbeat's, and only "
            "workflows read it.",
            "**(b)** PROVISIONAL (workflow-lineage): a tag the text declares, compared on every clear edge at load (D-0054-1).",
            "**(c)** PROVISIONAL (workflow-rung0): a seating above rung 0 does not load; the grant carries no appraisal.",
            "**(d)** PROVISIONAL (workflow-mesh-joins): an `all` join in a mesh does not load.",
            "**(e)** PROVISIONAL (workflow-handles): a handle input is labelled and recorded, and cannot be resolved by the guest.",
            "**(f)** PROVISIONAL (workflow-inputs): a clear input comes from the cache of the replica that wrote the reports; another "
            "delivers none (finding 23).",
            "**(g)** PROVISIONAL (workflow-occupant): sessions handed out by `WorkflowStatus`, a **BOOTSTRAP** standing in for a "
            "launch per slot; the cells are the tests', not ADR-0036's occupant.",
            "**(h)** an input's label is the reporter's `clearSet` at its seal, not at each emit: coarser, and sound.",
            "**(i)** `outward` is the text's declaration joined with the deciding replica's reading of the bundle.",
        ], "teal", {}),
        ("Not built at the reference (A16; I49)", [
            "`T_wf` and the step bound: no replicated clock.",
            "Pools and parity seatings; fan-out-scoped joins.",
            "**D-0054-2**: waiving coverage at the edge.",
            "The gate's evidence for a mesh's vote.",
            "The bundle's refusal of a `kind`.",
            "**The delivery table's narrowing of an edge's mode.**",
            "Seatings above rung 0.",
        ], "red", {"status": "notbuilt", "tint": False}),
        ("Findings for the corpus (`mechanism/` 21–23; G11 item 108)", [
            "**21 · A round that ends on its own admit seals after that admit's record.** The seal came before the "
            "deciding replica wrote the ending record, which was then refused as sealed; fixed (`seal_round`). ADR-0042 "
            "§5 says when a lease ends, not that the seal follows the ending admit's record, and A3 makes the case new.",
            "**22 · `denials` had no replicated source.** The reference lifted 0 at first. **Closed** by ADR-0054 R6, "
            "2026.10.09.",
            "**23 · A clear input needs a read path the reference does not have**: the transport writes topics and does "
            "not read them. The record's delivery is right; the reference needs a topic read path (ADR-0005) or a "
            "replicated store of outputs to follow it after a failover.",
        ], "amber", {"status": "open", "status_extra": "21, 23"}),
        ("What is behind the tree (A16, A17; G11 items 56, 103)", [
            "**Trace validation was not rerun**: `spec/Mechanism.tla` does not model workflows, and a traced run that "
            "loads one would not match it; `WorkflowLoad` and `WorkflowGrant` are projected by name. Stage one of the "
            "refinement chain is behind the tree.",
            "**`mechanism/lean` is stale**: `SeatsModel.lean` and `CouplingModel.lean` transcribe `ActionKind` and "
            "`SeatKind`, which gained `Route` and `orchestrator`; `tools/lean-sync.sh` exits 1. Left so by the "
            "custodian's decision of 2026.10.08.",
            "**`Workflow.tla` is tied to the reference by tests named after its properties, and by no trace.**",
        ], "red", {"tint": False, "dash": "6 4"}),
    ]
    h8 = max(c.card(0, 0, w8, t, b, draw=False, size=13.5, status=k.get("status")) for t, b, _, k in specs)
    for i, (t, b, acc, k) in enumerate(specs):
        c.card(X0 + i * (w8 + g8), y, w8, t, b, accent=acc, size=13.5, h=h8, **k)
    y += h8 + 70

    # ================================================================== band 9: the pending amendments, §12
    y = band(c, X0, y, "Ten dependent amendments, drafted 2026.10.08 and pending (ADR-0054 R3; G11 §1.1)",
             status="proposed", extra="none applied · none reviewed")
    lw_ = 2120
    P_ = "Pending"
    ta = c.table(X0, y, [("Record", lw_ * 0.1, {"bold": True}), ("Amendment", lw_ * 0.2),
                         ("What it would change", lw_ * 0.56), ("Bears on", lw_ * 0.14)], [
        ["ADR-0015 A1", "`Route` is a principal emission", "The Decision gains a paragraph: `Route(edge)` is admitted, "
         "ordered and recorded on its round topic, so it is an emission; the lease it leads to is granted under the "
         "workflow's promotion, which is the authority change. **Both sets stay at two**", "C2 marking; finding 3"],
        ["ADR-0024 A4", "A workflow is a set of seatings and a graph", "§1: the nodes are seatings voted on with the "
         "graph; the tally is the authority for every lease; the mechanism grants each **when its node becomes ready**, "
         "nothing wider than the seating; a refused grant fails the node; a rules-epoch change voids leases not yet "
         "issued; **the tally checks lineage alternation on clear edges**. §2's quorum rule and the gates unchanged", "—"],
        ["ADR-0031 A4", "A third grant path: a workflow's node", "§2: the node's lease is granted under the workflow's "
         "tally; appraised and refused as any grant; a refusal fails the node; no operator makes successor grants inside "
         "a workflow, while its denies reach every cell; one live lease per principal orders a principal's rounds. §1's "
         "field set and §4's monotonicity unchanged", "C1: every worker's grant travels it"],
        ["ADR-0037 A5", "A seat kind `orchestrator`", "§4's table gains it: Run only, `Route` and `Report`, no authoring "
         "variant; seated by a workflow's promotion, one round per decision point, coupled to its Observer. **The kinds "
         "are six.** B10 binds it by kind as written", "—"],
        ["ADR-0039 A3", "Coverage at a workflow's edge, and the orchestrator coupled", "§2: an edge out of a node is "
         "enabled only when a cell Observer has read its round to the seal; it subtracts and closes no race, which "
         "§8's re-check does; an `orchestrator` seat's admits need `live(o)`; waiving it is D-0054-2", "—"],
        ["ADR-0040 A2", "A fourth variant, `Route`, and an early end", "§1: `Route(edge)`, held only by an "
         "`orchestrator` seat, a principal emission, its envelope a chosen edge out of the lease's decision point; "
         "\"exactly three\" reads \"exactly four\". §3: `R` counts it. §4: a worker's `Report` carrying `outcome` ends "
         "its lease, and an applied `Route` ends the orchestrator's round, with no terminal variant. §6: three "
         "obligations and their owners", "C3: the alphabet gains a variant"],
        ["ADR-0041 A4", "`Route`'s envelope", "§1: `R8-route-own-decision` and `R9-only-orchestrators-route`; `R3` scoped "
         "to `thinker` and `orchestrator`, covering `Route`; B10 unchanged; enabledness stays a mechanism check. §4: S "
         "names `Route` over a `Seat` and an `Edge`. §5: an `input` in the edge's mode, which a bundle may only narrow; "
         "an orchestrator's delivery table a mechanism constant. **Its Cedar text is the `workflow` stage** (R3)", "—"],
        ["ADR-0042 A3", "Two more ends of a round", "§5's table gains the admit of a worker's `Report` carrying `outcome` "
         "at a workflow node, and the apply of an orchestrator's `Route`; both seal. \"The principal cannot end its own "
         "round\" is narrowed at a workflow node; still no terminal variant and no release",
         "C3: reverses that sentence in effect"],
        ["ADR-0043 A3", "A fifth item, `input`, and the orchestrator's Listener", "§1: a predecessor's output reaches a "
         "node along an edge, labelled by the reporter's `clearSet` at emit, in the edge's mode or narrower, joining the "
         "receiver's `clearSet` when clear; task slots take handles; **the list stays closed**. The orchestrator's own "
         "closed list, never bytes. §2: an `orchestrator` row, `Route` and `Report`", "C2: the ingress list gains an "
                                                                                      "item"],
        ["ADR-0047 A1", "The label of an `input`; the attributes; the routing rule", "§1: an `input` is labelled by the "
         "reporting worker's `clearSet` at emit, with no declaration. §4: the fixed set of mechanism-computed "
         "attributes gains a node's, **`denials` struck ⟨R6⟩**, read by guards and never by policy, each at its node's "
         "label, `outcome` declared; an edge into an outward or `restricted`-receiving node is disabled when a guard "
         "reads an `untrusted` attribute", "finding 6"],
        {"cells": ["ADR-0035 R8", "Lineages alternate at a workflow's tally", "A **revision in place** of a Proposed "
                   "record, not an amendment: for every clear edge the two Thinkers' Personas are independent by the "
                   "table, and every cell's Thinker and Observer are; handle edges are not checked; declared, not "
                   "enforced, until ADR-0035 is ratified. No exclusion rule in §3 changes", "D-0054-1; finding 5"],
         "accent": "violet"},
    ], size=13.5, accent="amber")
    c.para(X0, y + ta + 12, lw_, "Each is marked inline and not applied, with a History row in its record: **\"Pending — "
           "drafted 2026.10.08 by the assistant at the custodian's direction, not reviewed. Takes force only with "
           "ADR-0054's ratification.\"** With ADR-0033 A16 and A17 they are G11's twelve pending amendments, every one "
           "depending on a Proposed record. Two go past §12's list where the decision needs them: ADR-0043 A3's Run-table "
           "row and ADR-0039 A3's coupling (R3).", 13.5, "muted")
    rx9 = X0 + lw_ + 50
    rw9 = X1 - rx9
    ry = y
    ry += c.table(rx9, ry, [("§12 · Ratification condition", rw9 * 0.5, {"bold": True}), ("At G11", rw9 * 0.5)], [
        {"cells": ["The dependent entries drafted", "**Met** ⟨R3⟩: the ten above and ADR-0035 R8"], "accent": "green"},
        {"cells": ["ADR-0050 and ADR-0024 A3 ratified first", "Ratified, **provisional**, Batch 34: this record stands on "
                                                                "a provisional one"], "accent": "blue"},
        {"cells": ["A module states the properties, and its mutations break them", "**Met for TLC** ⟨R2⟩. **Not met**: "
                   "proofs; more than one decision point; multi-select; `all` joins and skips; the orchestrator's own "
                   "rounds; the step and time bounds"], "accent": "amber"},
        {"cells": ["The floor: `orchestrator`, `Route`, the forbid, R3 widened, gates rerun", "**Met** ⟨R4⟩: the "
                                                                                              "`workflow` stage"],
         "accent": "green"},
        {"cells": ["The reference, with an ADR-0033 addendum: nine behaviours, each seen", "**Met in part** ⟨R5⟩: A16 "
                   "(pending). Every behaviour seen; the cells are the tests', not ADR-0036's occupant; I49"],
         "accent": "amber"},
        {"cells": ["A reader who is not the drafter (ADR-0029 A2)", "[[red|Not met]]"], "accent": "red"},
    ], size=13.5, accent="amber") + 16
    c.card(rx9, ry, rw9, "§11 · The trusted base grows, accepted", [
        "The workflow interpreter, the guard evaluator and the orchestrator's Listener table are **part of the "
        "mechanism**, under ADR-0045's existing mechanism row, because every decision they make subtracts or executes "
        "a grant the quorum made. **More verified code on the path every Run grant now travels.**",
    ], accent="grey", size=13.5)
    y = c.ymax + 50

    # ---- findings and the other costs
    lw_ = 2120
    c.text(X0, y + 16, "**Findings** (ADR-0054, the record's seven)", 16, "ink")
    tf = c.table(X0, y + 30, [("#", lw_ * 0.04, {"bold": True}), ("Finding", lw_ * 0.96)], [
        ["1", "**Run had no path between cells.** ADR-0043's ingress list is closed and names no other cell; \"cells "
              "communicate through the record\" was true only of Build"],
        ["2", "**The orchestrator's safety argument needs nothing from the orchestrator.** It may only narrow, so every "
              "property is stated over enabled edges; it is in the record for quality alone, which is why it is optional"],
        {"cells": ["3", "**`Route` strains ADR-0015's enumeration**: ordered and recorded like an emission, its "
                        "consequence a grant. The record puts the grant on the promotion; **a C2 reviewer may read it as "
                        "a third kind**"], "accent": "amber"},
        ["4", "**Settled guards are what make the re-check cheap.** Write-once attributes and dominator read sets remove "
              "any difference between what the orchestrator was shown and the state at apply that no subtraction "
              "explains; `M_REWRITE` shows the difference"],
        {"cells": ["5", "**Two parallel branches of one lineage can agree by a shared blind spot.** Whether the branches "
                        "of a compare-and-merge must differ, which needs three lineages at a three-way merge, is "
                        "**open**"], "accent": "red"},
        ["6", "**The label of `outcome` is coarse.** One untrusted read labels every attribute a worker produces, so an "
              "honest workflow may lose its outward edges for the rest of the graph. The routing rule working, and it "
              "will be felt"],
        ["7", "**Without write-once attributes the orchestrator can loop for ever** ⟨R2⟩: decided, voided, decided "
              "again, each void ordered; depth 665 after thirteen hours"],
    ], size=13.5, accent="amber")
    rx10 = X0 + lw_ + 50
    rw10 = X1 - rx10
    c.card(rx10, y, rw10, "What it costs, and what is still open (Consequences; Open obligations; G11 item 101)", [
        "**Many principals**: each node is a cell with its own Observer, on its own device, of the other lineage; n "
        "nodes and an orchestrator are about 2n+2 principals.",
        "**A worker steers the routing** through its declared `outcome`, within the enabled edges.",
        "**A non-bipartite pattern of clear edges cannot be seated with two lineages**: it fails the tally at the "
        "archetype, or declares D-0054-1.",
        "**It rests on four Proposed or provisional records**: ADR-0035, ADR-0050, ADR-0024 A3 and ADR-0047's "
        "attributes.",
        "**Open**: proofs; `all` joins, skips and multi-select in the module; values for `T_wf` and the step bound; "
        "finding 5; a per-attribute label; correlations over workflows for ADR-0051 (G11 item 97); binding rows; the "
        "custodian's reading of every drafter's choice.",
    ], accent="red", size=13.5, tint=False)
    y = c.ymax + 40
    c.legend(X0, y, [
        ("box", "amber", "Proposed: ADR-0054 and its pending amendments", "6 4"),
        ("box", "blue", "the promotion, a provisional record"), ("box", "teal", "mechanism, built at reference"),
        ("box", "violet", "TLA+ module, lineage"), ("box", "pink", "detection, coverage"),
        ("box", "green", "subtraction, the safe outcome"), ("box", "red", "gap, outward, not built, open", "2 3"),
        ("box", "grey", "neutral, struck, the mesh (D6)", "6 4"),
        ("arrow", "teal", "computed edge"), ("arrow", "amber", "chosen edge"), ("arrow", "blue", "grant"),
    ])
    return c
