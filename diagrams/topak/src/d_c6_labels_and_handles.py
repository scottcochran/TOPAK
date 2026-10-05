"""C6 — The Listener labels what it delivers: labels, handles, `clearSet` and the floor's minimum (ADR-0047)."""
from lib import Canvas, text_width

ID, SLUG = "C6", "labels-and-handles"

H = "[[green|holds]]"
CE = "[[red|counterexample]] ✓"


def build():
    c = Canvas(ID, "The Listener labels what it delivers: a label on every item, and a handle in place of what is "
                   "suppressed",
               "Run's ingress is four items, each with a label that is a **function of its source** (ADR-0047; ADR-0043 "
               "A1). The Listener delivers an item **clear with its label, or as a handle** with no bytes, by a table "
               "in bundle data per seat kind; a handle may be an argument, and the tool host resolves it. "
               "`clearSet`, the join of everything read in the clear this round, is the only history policy reads, and "
               "the floor carries a **minimum over labels** that a bundle cannot loosen: delivering more in the clear "
               "buys a narrower round. Ratified in Batch 34 with eight dependent amendments; the floor that holds the "
               "three forbids is **genesis-provisional**. `Labels.tla` found a hole in the record before ratification, "
               "closed by the join of R10 (G10 §3, result 1). **A label is a declaration and not a finding** (G10 §8).",
               3400, "ADR-0047 §1–§11, Findings 1–11, Options, R1–R17, B34; ADR-0043 §1, §3, §4, A1, A2 (provisional); "
                     "ADR-0037 §2, A2, A3, A4 (provisional); ADR-0040 §3, A1; ADR-0041 §1, §3, §4, A1, A2; ADR-0042 §3, §4, A1, A2 "
                     "(provisional); ADR-0030 §4, A2, A3; ADR-0025 §1 (h), A2; ADR-0049 §3, §4, §6, §7; ADR-0048 §2; "
                     "ADR-0035 §1, R5 (Proposed); ADR-0045 Annex A T-0045-32 to T-0045-34, Annex B, A1; ADR-0050 §5 and "
                     "ADR-0052 §9 (provisional); floor/proposed/emergency-floor.cedar (15c941b9a56a09f7), "
                     "floor/proposed/labels-floor.cedar (9aab481d02414de2), labels-gates-results-2026.10.04.txt; "
                     "spec/Labels.tla (cc124f5c406aedac), Labels-results-2026.10.04.txt (2a8c20cf62d53f49), "
                     "Labels-results-2026.10.03.txt, Labels_proof.tla (877d9361051a9fbb), "
                     "Labels-proof-results-2026.10.04.txt, Labels-proof-cert-results-2026.10.04.txt (4f79314ec7972ece); "
                     "policies/data.json; mechanism/crates/topak-core/src/labels.rs, state.rs (apply_admit), "
                     "topak-bundle/src/allowlist.rs (facts, check_labels, delivery), topak-node/src/mechanism.rs "
                     "(resolve_handles); mechanism/GAPS-AND-ASSUMPTIONS.md I46, I47, I48; ADR-0033 A10, A14, A15; "
                     "ToO rev 14 §2.9, §2.10; G10 §2.2, §2.5, §2.6, §3 (results 1, 6), §7 items 92, 93, 94, §8")
    X0, X1 = c.x0, c.x1
    TW = X1 - X0
    y = c.y

    # ------------------------------------------------------------------ status line
    sx = X0
    c.text(sx, y + 16, "ADR-0047", 16, "ink", bold=True)
    sx += 92
    sx += c.status(sx, y, "accepted", "C4; C2 for §3 · Batch 34, at R17") + 12
    sx += c.status(sx, y, "accepted", "dependent: ADR-0025 A2, 0030 A2, 0037 A2, 0040 A1, 0041 A1, 0042 A1, 0043 A1, "
                                      "0045 A1 · B34") + 12
    sx += c.status(sx, y, "genprov", "the floor holding R5–R7") + 12
    sx += c.status(sx, y, "built", "ADR-0033 A10 (B34), A15 (B35)") + 14
    c.text(sx, y + 16, "No seat gains a variant; no principal changes containment class.", 14, "muted")
    y += 56

    # ------------------------------------------------------------------ the loop
    c.heading(X0, y, "The loop: four items in, each labelled; what a Thinker sends out is decided on what it has read",
              size=21)
    y += 48
    lane = 34                       # a routing lane on the left for the return arrow
    aw, bw, cw = 640, 600, 660
    g = 90
    ax = X0 + lane
    bx = ax + aw + g
    cx = bx + bw + g
    dx = cx + cw + g
    dw = X1 - dx
    top = y

    sources = [
        ("1 · The task", "brown", ("provisional", "ADR-0043 A2"), [
            "**Source:** the grant: a seating for a first lease, an operator's `Regrant` after it, on the log by digest "
            "and label (ADR-0050 §5).",
            "**Label:** declared in the grant. **Always delivered clear.** A grant whose task has no label is refused "
            "(R9). `clearSet` starts from it.",
        ]),
        ("2 · Consulted content", "teal", None, [
            "**Source:** the Run root, by the reference the Thinker supplied.",
            "**Label:** the root's declaration, for the root or a named subset (`labels.root`; ADR-0040 A1).",
        ]),
        ("3 · Tool results", "teal", None, [
            "**Source:** the allowlist entry, by name and digest.",
            "**Label:** the entry's `result.label`, **joined** with the label of every handle among the inputs and, "
            "**where an input is a literal, with** `clearSet` (R10), less what the entry `releases`.",
        ]),
        ("4 · The tool list", "blue", None, [
            "**Source:** the bundle revision the grant names (ADR-0048 §2), as the round's opening record.",
            "**Label:** none reserved: it passed promotion. **Always delivered clear.**",
        ]),
    ]
    sg = 22
    sh = [c.card(0, 0, aw, t, b, size=13.5, status=st[0] if st else None, status_extra=st[1] if st else "",
                 draw=False) for t, _, st, b in sources]
    sy = []
    yy = top
    for (t, a, st, b), h in zip(sources, sh):
        c.card(ax, yy, aw, t, b, accent=a, size=13.5, status=st[0] if st else None,
               status_extra=st[1] if st else "", h=h)
        sy.append((yy, h))
        yy += h + sg
    src_bot = yy - sg

    # The Listener
    lh = src_bot - top
    c.card(bx, top, bw, "The Listener: a stage, not a judge", [
        "**A label is a syntactic lift** (ADR-0007): mechanical, total, read from the record of which grant, root or "
        "entry produced the item. No model computes one.",
        "**Not a judgment about content.** Whether an item is poisoned is still not the Listener's to decide "
        "(ADR-0043 §1); that is an Observer finding.",
        "**Delivery is a table in bundle data**, label → mode, **total over the vocabulary, per seat kind** (§2). "
        "Where a label has several names, any name whose mode is `handle` suppresses the item.",
        "**The label travels in the envelope**, a field the mechanism writes, never inside the content: text that "
        "imitates a label changes nothing.",
        "No Persona, no alphabet, no choice (ADR-0037 §2, A2). Delivery adds nothing to the trusted base; the join, "
        "the lookup and handle resolution are rows of their own (T-0045-32, T-0045-34).",
    ], accent="teal", size=13.5, h=lh)
    for (yy, h) in sy:
        c.arrow([(ax + aw, yy + h / 2), (bx, yy + h / 2)], "teal", sw=2.2)

    # the two modes
    modes = [
        ("`clear`: the bytes, with their label", "green", [
            "The item's bytes and its label reach the Thinker.",
            "`consumed` for lineage (ADR-0035 §1).",
            "**Its label joins** `clearSet`**.**",
        ]),
        ("`handle`: a name and the label, no bytes", "amber", [
            "`{\"handle\": {\"actuate\": <seq>}}` or `{\"handle\": {\"consult\": \"<digest>\"}}` (ADR-0049 §3): the "
            "item's place in the record, already known to the Thinker. **No digest**: low-entropy content can be "
            "guessed.",
            "`ingress`**, not** `consumed` (R3). **Adds nothing to** `clearSet`**.**",
            "Whole-item: a result is clear or a handle.",
        ]),
    ]
    mh = [c.card(0, 0, cw, t, b, size=13.5, draw=False) for t, _, b in modes]
    gap_m = max(30, lh - sum(mh))
    my = top
    mpos = []
    for (t, a, b), h in zip(modes, mh):
        c.card(cx, my, cw, t, b, accent=a, size=13.5, h=h)
        mpos.append((my, h))
        my += h + gap_m
    for (yy, h), a in zip(mpos, ("green", "amber")):
        c.arrow([(bx + bw, yy + h / 2), (cx, yy + h / 2)], a, sw=2.2)

    # the guest
    c.region(dx, top, dw, lh, "The Thinker's guest (havoc in every theorem)", "grey", dash="8 5", size=14)
    iw = dw - 40
    g1 = c.card(dx + 20, top + 28, iw, "`clearSet`: the round's memory, and the only history policy reads (§4)", [
        "The join of the labels of **every item delivered clear** to this principal this round, the task included. "
        "**It only grows.** A live round keeps the labels it started with; a new bundle relabels nothing (§8).",
        "A literal argument has no label of its own: the mechanism cannot say what a typed value derives from, and "
        "`clearSet` is the sound bound. **History reaches policy only as attributes the mechanism computes**, a "
        "small fixed set; no temporal operator enters the policy language (R13; ADR-0030 A2).",
    ], accent="green", size=13.5)
    g2 = c.card(dx + 20, top + 28 + g1 + 16, iw, "**The bytes of a suppressed item do not enter the guest** (§3, C2)", [
        "Enforced by what the node sends, not by the Thinker's cooperation; the decoder runs in the guest (ADR-0018) "
        "and has nothing to dereference. **No variant turns a handle into bytes**, and this record adds none.",
    ], accent="teal", size=13.5)
    g3y = top + 28 + g1 + 16 + g2 + 16
    c.card(dx + 20, g3y, iw, "A handle is still useful, three ways (§3)", [
        "**The Thinker knows what was withheld and why**: a handle and its label arrive where a silent drop would "
        "deliver nothing.",
        "**A handle may be an argument.** The tool host resolves it and the tool receives the bytes: the Thinker routes "
        "content it cannot read. An entry declares, per input, which labels it `accepts` by handle.",
        "**It may try again another way**: `Consult` something else, call another tool, or call a **releasing entry** "
        "that returns a narrower result the table delivers clear, the only way suppressed content becomes readable. "
        "**Each attempt is an ordinary admit**: counted against `R`, coupled under `K`, on the log.",
    ], accent="amber", size=13.5)
    for (yy, h), a in zip(mpos, ("green", "amber")):
        c.arrow([(cx + cw, yy + h / 2), (dx, yy + h / 2)], a, sw=2.2, dash=None if a == "green" else "7 5")
    row1_bot = top + lh

    # row 2: right to left, the way out and back
    r2y = row1_bot + 110
    n2 = 5
    g2w = 80
    ew = (X1 - ax - (n2 - 1) * g2w) / n2
    egress = [
        ("`Actuate(tool, inputs)`", "grey", None, [
            "An input is a **literal** (a scalar) or a **handle**, told apart by shape (ADR-0049 §3; ADR-0043 A1).",
            "A handle is admitted only where its label is within the input's `accepts`; otherwise **refused at admit**.",
        ]),
        ("The lift: facts the deciding replica computes", "teal", None, [
            "`clearSet`; `inputLabels`; `destLiteral`; `destLabels`; and `Tool.outward`, **derived, never declared**: "
            "the entry's target is not on the issued list of targets inside the deployment (ADR-0025 §1 (h)).",
            "No policy computes any of them (`labels.rs`; ADR-0030 A2).",
        ]),
        ("The floor's minimum: `R5`, `R6`, `R7`", "red", ("genprov", "floor"), [
            "Three forbids on an `Actuate` of an **outward** entry (ADR-0041 A1), table below. A forbid denies "
            "whatever permit holds, so they bind an `emergency` seat too (A2).",
            "**Monotone in** `clearSet`**.**",
        ]),
        ("`apply`, on every replica, in log order", "teal", None, [
            "**Refuses an admit decided against a** `clearSet` **the round has since grown past**: the floor's answer was "
            "about that set and no other (`state.rs`). A Run delivery with no label is refused.",
            "Folds the result's label by sequence number, and into `clearSet` when it is delivered clear.",
        ]),
        ("The tool host resolves handles", "teal", None, [
            "On the mechanism's side: **the tool receives the bytes**, the Thinker never does. Same principal, same "
            "round; the item must match the input's type, or the call is refused and recorded (ADR-0049 §3).",
            "The Thinker routes content it cannot read.",
        ]),
    ]
    eh = max(c.card(0, 0, ew, t, b, size=13.5, status=st[0] if st else None, status_extra=st[1] if st else "",
                    draw=False) for t, _, st, b in egress)
    epos = []
    for i, (t, a, st, b) in enumerate(egress):
        x = X1 - ew - i * (ew + g2w)
        c.card(x, r2y, ew, t, b, accent=a, size=13.5, status=st[0] if st else None,
               status_extra=st[1] if st else "", h=eh, tint=(a != "red"))
        epos.append(x)
    for i in range(n2 - 1):
        x = epos[i]
        lab = [None, None, "admitted", None][i]
        c.arrow([(x, r2y + eh / 2), (x - g2w, r2y + eh / 2)], "grey", sw=2.2)
    # guest → Actuate
    gx = epos[0] + ew / 2
    c.arrow([(gx, row1_bot), (gx, r2y)], "grey", sw=2.4, label="the Thinker calls out", lpos=0.5)
    # floor refusal
    c.label(epos[2] + ew / 2, r2y + eh + 26, "refused: no effect; the attempt is on the log", "red", 13)
    # tool host → tool results (the loop)
    lx = X0 + lane / 2
    ry = sy[2][0] + sy[2][1] / 2
    c.arrow([(epos[4], r2y + eh / 2), (lx, r2y + eh / 2), (lx, ry), (ax, ry)], "teal", sw=2.4)
    c.label(lx + 150, r2y - 24, "the result, recorded, is the next item of ingress", "teal", 13)
    y = r2y + eh + 70

    # ------------------------------------------------------------------ the floor's minimum and the load checks
    half = (TW - 50) / 2
    c.heading(X0, y, "§7: the floor carries a minimum, and a bundle cannot loosen it")
    c.status(X0 + half, y + 3, "genprov", "emergency-floor.cedar · 28 policies", anchor="end")
    c.heading(X0 + half + 50, y, "§4, §5: what the lift adds to schema S, and what the record's envelope says")
    y += 42
    lcols = [("Term", half * 0.2, {"bold": True}), ("What it is", half * 0.52), ("Where it is fixed", half * 0.28)]
    t1 = c.table(X0, y, lcols, [
        ["`untrusted`", "The reserved provenance name: content a party outside the deployment could have written",
         "The floor"],
        ["`restricted`", "The reserved sensitivity name: content that must not leave the deployment", "The floor"],
        ["Outward entry", "An allowlist entry whose declared channel reaches a target the issued rules do not list as "
                          "inside the deployment. **With no such list, every entry that declares a channel is "
                          "outward**", "The entry's channel (ADR-0049 §5) and the issued rules (ADR-0025 §1 (h))"],
    ], size=13.5, accent="red")
    fy = y + t1 + 18
    fcols = [("F", half * 0.06, {"bold": True}), ("Floor entry (ADR-0041 A1)", half * 0.25, {"mono": True}),
             ("Path", half * 0.17), ("Refused at admit, an `Actuate` of an outward entry, when", half * 0.52)]
    t2 = c.table(X0, fy, fcols, [
        ["F1", "R5-no-read-then-send", "**Read, then send**: untrusted content steers a call that carries private "
                                       "content out",
         "`clearSet` contains `untrusted`, and `restricted` is in `clearSet` or in any of `inputLabels`"],
        ["F2", "R6-no-steered-destination", "**Steered destination**: CR-32's `to: attacker`",
         "`clearSet` contains `untrusted`, and an input the entry marks a destination is a literal. **Kept in the "
         "floor** by the custodian's decision (R13); it will refuse honest work"],
        ["F3", "R7-no-replayed-destination", "**Replayed content** passed straight back out as a destination",
         "A destination input is a handle whose label contains `untrusted`, **whatever** `clearSet` **holds**"],
    ], size=13.5, accent="red")
    ly = fy + t2 + 18
    gcols = [("F", half * 0.06, {"bold": True}), ("Check", half * 0.12, {"bold": True}), ("Path", half * 0.24),
             ("The bundle is refused at load when (ADR-0049 §6 is the definitive form)", half * 0.58)]
    t3 = c.table(X0, ly, gcols, [
        ["F4", "W7", "An outside source passed off as inside",
         "An outward entry's `result.label` lacks `untrusted`. Whatever such a tool returns came from outside"],
        ["F5", "W8", "A laundering tool", "`result.releases` holds a reserved name and the issued rules do not name "
                                          "the entry by digest. A declassifier of a reserved name is the anchors' to "
                                          "approve, not a promotion's"],
        ["F6", "W6, W9", "A forgotten declaration", "A root or an entry declares no label; or an outward entry takes "
                                                    "inputs and marks none a destination without saying "
                                                    "`destinations: none`"],
    ], size=13.5, accent="violet")
    lefty = ly + t3 + 14
    lefty += c.para(X0, lefty, half,
                    "**F1 to F3 are Cedar forbids**, relaxed only by an issuance with the floor's gates; each is total, "
                    "matters, and is classed a relaxation when dropped. **F4 to F6 are not Cedar**: they are checks on "
                    "bundle data the mechanism makes at load (ADR-0030 A2), changed only by a release. The label itself "
                    "cannot be forged by content, so that path needs no entry. **This is a minimum and is not complete**: "
                    "an injection that changes a `Report`, acts through an entry that is not outward, or comes from a "
                    "source declared wrongly is the bundle's to narrow and the Observer's to find. The policy floor's "
                    "`R5`–`R7` are not the rules floor's R5–R7 (ADR-0026).", 13.5, "muted")
    rx = X0 + half + 50
    acols = [("Attribute", half * 0.2, {"mono": True}), ("What it is", half * 0.45), ("How it is computed", half * 0.35)]
    u1 = c.table(rx, y, acols, [
        ["inputLabels", "For each input that is a handle, the label of the item it names",
         "Read from the record the handle names"],
        ["clearSet", "The join of the labels of every item delivered clear to this principal in this round, the task "
                     "included", "A fold over the round's deliveries; it only grows"],
        ["destLiteral", "An input the entry marks a destination is a literal (the lift's, for F2)",
         "From the entry's `destination` and the input's shape"],
        ["destLabels", "The labels of the destination inputs that are handles (for F3)", "As `inputLabels`, for "
                                                                                       "destinations"],
        ["Tool.outward", "Whether the entry is outward", "From the entry's channel and the issued list"],
    ], size=13.5, accent="teal")
    ey = y + u1 + 18
    ecols = [("Field of the `Actuate` record", half * 0.27, {"mono": True}), ("What it is", half * 0.53),
             ("Side (ADR-0004)", half * 0.2)]
    u2 = c.table(rx, ey, ecols, [
        ["seat, fence", "The principal's seat and the lease's fence", "Control plane"],
        ["admit", "The log index at which the admit committed", "Control plane"],
        ["seq", "The sequence number of ADR-0042 §2", "Control plane"],
        ["tool", "Name and digest of the allowlist entry", "Control plane"],
        {"cells": ["seatKind", "The kind of the seat that called, **in place of** `breakGlass`: with X1 retired no admit "
                               "is under it (A2, provisional with ADR-0052)", "Control plane"], "accent": "blue"},
        ["inputs", "Digest of the inputs", "Control plane"],
        ["outcome", "`returned`, `failed` or `unknown`", "Control plane"],
        ["result", "Digest of what the tool returned, when it returned", "Control plane"],
        {"cells": ["inputLabels", "As §4 (A1)", "Control plane"], "accent": "green"},
        {"cells": ["resultLabel", "The label of the result, after the join of §1 (A1)", "Control plane"],
         "accent": "green"},
        {"cells": ["delivery", "`clear` or `handle` (A1)", "Control plane"], "accent": "green"},
        {"cells": ["clearSet", "As §4, as it stood when the call was admitted (A1)", "Control plane"],
         "accent": "green"},
        ["payload", "The inputs and the result themselves, **in full whatever** `delivery` **says**",
         "Cognitive payload"],
    ], size=13.5, accent="teal")
    righty = ey + u2 + 14
    righty += c.para(rx, righty, half,
                     "**Suppressed to the Thinker is not suppressed to the Observer** (§5; ADR-0043 A1): it reads the "
                     "payload in full under `W(p)`. A facts-only reader can see that an untrusted result was delivered "
                     "clear and an outward call followed, without reading either. `Consult` still writes no record; its "
                     "admit in the log gains the label and the mode. Labels tell an Observer where to look hardest; they "
                     "are not a finding and not an exemption.", 13.5, "muted")
    y = max(lefty, righty) + 60

    # ------------------------------------------------------------------ R10, stale clearSet, per-seat-kind delivery
    w3 = (TW - 2 * 40) / 3
    c.heading(X0, y, "What the module found: a literal laundered through an inside tool (R10)")
    c.heading(X0 + w3 + 40, y, "Why `apply` re-checks `clearSet`")
    c.heading(X0 + 2 * (w3 + 40), y, "The delivery table is per seat kind (§2)")
    y += 42
    steps = [
        ("1", "The Thinker reads untrusted content in the clear: `clearSet` holds `untrusted`.", "grey"),
        ("2", "It passes a **literal** to `echo`, an **inside** tool that returns what it was given. Nothing refuses: "
              "`echo` is not outward.", "grey"),
        ("3", "**As written before R10** the result's label is `echo`'s own, `{}`. Delivered or held by handle, it "
              "looks clean.", "red"),
        ("4", "It calls `send` with `to:` **a handle to that result**. F2 sees no literal; F3 sees no `untrusted`. "
              "**Admitted: a steered destination.**", "red"),
        ("✓", "**R10**: where an input is a literal the result's label also takes `clearSet`, so step 3's result is "
              "`untrusted` and `R7` **refuses step 4**. Confirmed by the custodian (R13).", "green"),
    ]
    sx0 = X0
    syy = y
    for n, txt, a in steps:
        h = c.card(sx0 + 46, syy, w3 - 46, None, [txt], accent=a, size=13.5, bullets=False, tint=(a != "grey"))
        c.pill(sx0, syy + 8, n, a, 13, solid=True)
        syy += h + 10
    syy += 6
    syy += c.para(sx0, syy, w3,
                  "`Labels.tla` has the trace under `M_LITERAL`: it breaks `LabelsCoverTruth` and "
                  "`NoSteeredDestination`, and **passes** `ResultLabelCoversInputs`, the property stated over the "
                  "mechanism's own labels. A property stated over ghost truth caught it (finding 11). The cost: after "
                  "an untrusted clear read, every result of a call with a literal input is `untrusted`, which widens "
                  "F2's.", 13.5, "muted")
    mx = X0 + w3 + 40
    mh1 = c.card(mx, y, w3, "A stale `clearSet` is refused, not re-decided", [
        "The replica that decides an admit computes its label facts, `clearSet` among them, and the floor answers "
        "about that set. Between decision and commit another delivery can grow the round's `clearSet`.",
        "**At** `apply`**, on every replica**: if the admit's `clearSet` is not the round's, it is refused: \"decided "
        "against a clearSet the round has since grown past\". A Run `Consult` or `Actuate` that carries no label "
        "facts is refused too (`state.rs`).",
        "**It is the only label fact** `apply` **re-checks**; the others are the deciding replica's, taken as the floor's "
        "reasons are (G10 item 93; `mechanism/` I46).",
        "`spec/Mechanism.tla` models the fold and the refusal; trace validation, 82 traces and 1,007 steps, every step "
        "matching (ADR-0033 A14). A matching trace is not a refinement.",
    ], accent="teal", size=13.5)
    px = X0 + 2 * (w3 + 40)
    dcols = [("Seat kind", w3 * 0.2, {"mono": True}), ("`untrusted`", w3 * 0.16), ("`restricted`", w3 * 0.16),
             ("At the reference (`policies/data.json`)", w3 * 0.48)]
    dt = c.table(px, y, dcols, [
        ["thinker", "[[green|clear]]", "[[amber|handle]]", "A row is **required at load**, total over the vocabulary"],
        ["observer", "[[green|clear]]", "[[green|clear]]", "Required. A handle to an Observer is the facts-only "
                                                            "narrowing of ADR-0038 §3, declared; its mark must not say "
                                                            "it read the item"],
        {"cells": ["emergency", "[[amber|handle]]", "[[amber|handle]]",
                   "Run only, `Consult`, `Actuate`, `Report` (ADR-0037 A3, provisional with ADR-0052). "
                   "**No row, and none required**: a kind the table does not cover is given nothing in the clear. "
                   "**A person on an emergency seat is given handles unless the bundle says otherwise** (G10 result 6; "
                   "item 92, provisional with ADR-0052)"], "accent": "amber"},
        ["operator", "—", "—", "Control actions only, no variant of either authoring alphabet (ADR-0037 A4, "
                               "provisional with ADR-0050): nothing is delivered (I47)"],
    ], size=13.5, accent="amber")
    dty = y + dt + 12
    dty += c.para(px, dty, w3,
                  "The vocabulary here is the two reserved names; the rest is the bundle's (an open obligation). The "
                  "load also refuses a root with no label (F6) and a name outside the vocabulary (W6). **A bundle may move every label to** "
                  "`clear`: it loads, and the same outward call is still refused (§11, seen at "
                  "the reference).", 13.5, "muted")
    y = max(syy, y + mh1, dty) + 60

    # ------------------------------------------------------------------ how each part changes; degeneracy
    c.heading(X0, y, "§8: how each part changes (the full table)")
    y += 42
    ccols = [("What changes", TW * 0.34), ("Where it lives", TW * 0.2), ("How it changes", TW * 0.28),
             ("When it takes effect", TW * 0.18)]
    y += c.table(X0, y, ccols, [
        ["A root's or an entry's label; the destination inputs; which labels an input accepts by handle; a release of "
         "a name the floor does not reserve", "Bundle data", "**Bundle promotion**, signed (ADR-0044)",
         "At a principal's next grant (ADR-0031 R2)"],
        ["The delivery table; the vocabulary beyond the two reserved names", "Bundle data", "**Bundle promotion**",
         "At the next grant"],
        {"cells": ["The task's label", "The grant", "Per grant, by the operator: **the weakest path**. Nothing checks "
                   "it is true; a task from outside labelled trusted switches `R5` and `R6` off until something "
                   "untrusted is read (T-0045-33)", "That round"], "accent": "red"},
        ["F1 to F3; the two reserved names", "The floor (ADR-0041 A1: `R5` to `R7`)",
         "**An issuance by the anchors** to relax (ADR-0025 §1 (d)), with the floor's gates", "By the floor's own rule"],
        ["F4 to F6", "The mechanism, at bundle load (ADR-0049 §6: W7 to W9; ADR-0030 A2)",
         "**A mechanism release.** A bundle cannot waive them and an issuance does not change them", "At deployment"],
        ["The entries allowed to release a reserved name; the targets listed as inside the deployment",
         "The issued rules (ADR-0025 §1 (h))", "**An issuance by the anchors**", "By the rules' own rule"],
        ["The join, the lookup, handle resolution; `inputLabels` and `clearSet` in schema S", "Mechanism and schema",
         "A mechanism release", "At deployment"],
    ], size=13.5, accent="blue") + 14
    y += c.para(X0, y, TW,
                "**A loosening by promotion is bounded by §7, and only by §7**: `bundle ⊑ floor` is decided over action "
                "variants and says nothing about delivery. A promoted bundle may move every label to `clear`; it cannot "
                "escape F1 to F3, which then see a larger `clearSet` and refuse more, relabel an outward entry as "
                "trusted (F4), or add a declassifier of a reserved name (F5). What it can still loosen unnoticed is the "
                "label of a source that is not outward, the Run root's included. Promotion is as strong as its gates, "
                "and gate evidence is still an assertion (G10 §8).", 13.5, "muted") + 30
    c.heading(X0, y, "§10: degeneracy on this record")
    y += 42
    gcols = [("Id", TW * 0.07, {"bold": True}), ("Kind", TW * 0.1), ("Parameter → deployed value", TW * 0.2),
             ("Premises falsified", TW * 0.22), ("Theorems voided", TW * 0.31), ("Type changes", TW * 0.1)]
    y += c.table(X0, y, gcols, [
        ["D-0047-1", "Mechanism (ADR-0023 §6a)", "Labels and delivery modes → none: every admitted item delivered "
                                                 "clear and unlabelled",
         "Every item of ingress carries a label; a suppressed item's bytes do not enter the guest",
         "**None today**: no theorem in force reads a label. Every property of §11's module is lost; F1 to F6 have "
         "nothing to read. **The reference until 2026.10.05**", "None"],
    ], size=13.5, accent="grey") + 12
    y += c.para(X0, y, TW, "A deployment whose table delivers every label clear is not degenerate: its items are "
                "labelled, its records carry the fields, and its policy can read them.", 13.5, "muted") + 50

    # ------------------------------------------------------------------ Labels.tla
    c.heading(X0, y, "§11: `spec/Labels.tla` (`cc124f5c406aedac`): 37 TLC rows at `MaxSeq = 3`; ten properties proved "
                     "for every `MaxSeq`, 651 obligations, certified", size=21)
    c.status(X1, y + 3, "accepted", "ADR-0046 · ADR-0047 R10, R12", anchor="end")
    y += 48
    pw = 0.36 * TW
    pcols = [("Property", pw * 0.42, {"mono": True}), ("Over", pw * 0.58)]
    pt = c.table(X0, y, pcols, [
        ["NoUnlabelledDelivery", "Every delivered item has a declared label"],
        ["SuppressedNeverInGuest", "The bytes of an item the table suppresses are not in the guest"],
        ["ClearSetCoversGuest", "`clearSet` holds every label read in the clear"],
        ["ClearSetOnlyGrows", "A step property: `clearSet` never shrinks"],
        ["ResultLabelCoversInputs", "A result's label holds its handle inputs' labels, less what its entry releases"],
        ["LabelsCoverTruth", "**Ghost truth**: tainted ⇒ `untrusted` in the label; secret ⇒ `restricted`"],
        ["OutsideResultIsUntrusted", "F4: an outward tool's result carries `untrusted`"],
        ["ReservedReleasedOnlyIfIssued", "F5: a reserved name is released only by an entry the issued rules name"],
        ["NoReadThenSend", "F1, **over the truth**: no outward call by a Thinker that has read tainted bytes carries "
                           "a secret out"],
        ["NoSteeredDestination", "F2 and F3, **over the truth**: no outward call's destination is tainted"],
        {"cells": ["FloorMinimumHolds", "The last two: the property ADR-0047 §11 names"], "accent": "teal"},
    ], size=13.5, accent="teal")
    py = y + pt + 14
    py += c.para(X0, py, pw,
                 "Four tools, one of each kind the rules distinguish: `fetch` outward, returning outside content; `send` "
                 "outward, with a destination; `vault` inside, declared `restricted`; `echo` inside, returning what it "
                 "was given, and optionally a releasing redactor. The bundle and the grant are chosen at `Init` every "
                 "way the load checks allow. **Not modelled**: `accepts` (every input accepts every label, the widest "
                 "case), more than one round, and a wrongly declared inside source, which the header says.", 13.5,
                 "muted") + 16
    pr = c.card(X0, py, pw, "The proof: `Labels_proof.tla` (`877d9361051a9fbb`)", [
        "All ten properties **proved for every value of** `MaxSeq`, on the one assumption that it is a natural number: "
        "651 obligations (ADR-0047 R12).",
        "**Certified** (ADR-0046 A1): 421 closed by the prover's normalization, 216 by SMT with a proof the `ethos` "
        "checker accepted, **14 temporal steps by LS4, which no checker confirms**.",
        "The proof found **no fault in the record**. It corrected the module's account of itself in four rows "
        "(`M_LOAD`, `M_RESET`, `M_DELIVER` break `LabelsCoverTruth`; `M_DELIVER` breaks `ClearSetCoversGuest`), "
        "confirmed by TLC in the 10.04 file, and needed an invariant no property names: only an item that exists is "
        "in the guest.",
        "**A certified proof is not a verified one**, and none of this is about the running reference: `Labels.tla` "
        "is tied to it by tests, by no trace (A10). The binding table has no row for it (G10 item 90).",
    ], accent="teal", size=13.5, status="accepted", status_extra="certified")
    left_bot = py + pr
    tx = X0 + pw + 40
    tw = X1 - tx
    tcols = [("Row", tw * 0.07, {"mono": True}), ("Mutation", tw * 0.13, {"mono": True}),
             ("Property", tw * 0.24, {"mono": True}), ("Result", tw * 0.17), ("What it shows", tw * 0.39)]
    rows = [
        {"group": "ADR-0047 as revised at R10", "accent": "teal"},
        ["safe", "none", "Safe", H + " (122,694 states)", "Every invariant at once; depth 7"],
        ["grow", "none", "ClearSetOnlyGrows", H, "The step property"],
        {"group": "`M_LITERAL`: a result's label does not take `clearSet` for a literal input, the record before R10",
         "accent": "red"},
        ["lit1", "M_LITERAL", "LabelsCoverTruth", CE, "A result computed from a literal is under-labelled"],
        {"cells": ["lit2", "M_LITERAL", "NoSteeredDestination", CE,
                   "**The hole**: a literal laundered through `echo`, named by handle as a destination (G10 result 1)"],
         "accent": "red"},
        ["lit3", "M_LITERAL", "NoReadThenSend", H, "F1 does not depend on the join"],
        ["lit4", "M_LITERAL", "ResultLabelCoversInputs", H,
         "**The bookkeeping property passes**: only the ghost-truth one sees it (finding 11)"],
        {"group": "`M_JOIN`: a result's label does not take its handle inputs' labels", "accent": "grey"},
        ["join1", "M_JOIN", "ResultLabelCoversInputs", CE, ""],
        ["join2", "M_JOIN", "LabelsCoverTruth", CE, ""],
        ["join3", "M_JOIN", "FloorMinimumHolds", CE, "Without the join, a tool given suppressed content returns it "
                                                     "under its own label"],
        {"group": "`M_LOAD`: the load checks F4 to F6 are dropped", "accent": "grey"},
        ["load1", "M_LOAD", "NoUnlabelledDelivery", CE, ""],
        ["load2", "M_LOAD", "OutsideResultIsUntrusted", CE, ""],
        ["load3", "M_LOAD", "ReservedReleasedOnlyIfIssued", CE, ""],
        ["load4", "M_LOAD", "FloorMinimumHolds", CE, ""],
        ["load5", "M_LOAD", "LabelsCoverTruth", CE, "Found writing the proof; in the file from 2026.10.04"],
        {"group": "`M_RESET`: a clear delivery replaces `clearSet`", "accent": "grey"},
        ["reset1", "M_RESET", "ClearSetOnlyGrows", CE, ""],
        ["reset2", "M_RESET", "ClearSetCoversGuest", CE, ""],
        ["reset3", "M_RESET", "FloorMinimumHolds", CE, "A bundle's table that resets the fold switches the forbids off"],
        ["reset4", "M_RESET", "LabelsCoverTruth", CE, "Found writing the proof"],
        {"group": "`M_DELIVER`: the Listener sends the bytes of a suppressed item", "accent": "grey"},
        ["del1", "M_DELIVER", "SuppressedNeverInGuest", CE, ""],
        ["del2", "M_DELIVER", "FloorMinimumHolds", CE, ""],
        ["del3", "M_DELIVER", "ClearSetCoversGuest", CE, "Found writing the proof"],
        ["del4", "M_DELIVER", "LabelsCoverTruth", CE, "Found writing the proof"],
        {"group": "`M_F1`, `M_F2`, `M_F3`: one forbid dropped. **Each of the three is needed on its own**",
         "accent": "red"},
        ["f1a", "M_F1", "NoReadThenSend", CE, "Without `R5`"],
        ["f1b", "M_F1", "NoSteeredDestination", H, "…and nothing else breaks"],
        ["f2a", "M_F2", "NoSteeredDestination", CE, "Without `R6`"],
        ["f2b", "M_F2", "NoReadThenSend", H, ""],
        ["f3a", "M_F3", "NoSteeredDestination", CE, "Without `R7`"],
        ["f3b", "M_F3", "NoReadThenSend", H, ""],
        {"group": "Witnesses, each of which must be violated", "accent": "green"},
        ["w1", "none", "NeverOutwardEffect", CE, "An outward call is admitted: the minimum is not vacuous"],
        ["w2", "none", "NeverTaintedOutward", CE, "A Thinker that has read tainted bytes still calls out: the forbids "
                                                  "do not simply stop a tainted round"],
        ["w3–w5", "none", "NeverF1 · NeverF2 · NeverF3", CE + " each", "Each forbid fires"],
        ["w6", "none", "NeverSuppressed", CE, "An item is delivered as a handle"],
        ["w7", "none", "NeverHandleInput", CE, "A handle is used as an input"],
        ["w8", "none", "NeverCleanLeak", CE, "A secret leaves by the call of a Thinker that read nothing tainted: F1 "
                                            "is about injection, not a ban on sending"],
        ["w9", "none", "NeverReleased", CE, "An issued releasing entry removes a reserved name"],
    ]
    tt = c.table(tx, y, tcols, rows, size=13, accent="teal")
    tcards = [
        ("At the reference: what it trusts (G10 item 93; I46)", "red", [
            "**The label facts are the deciding replica's**, and `apply` re-checks `clearSet` only; an activation's "
            "envelope is the ordering replica's too.",
            "**A failed call's error text reaches the principal unlabelled**, in the clear: a tool that puts content in "
            "its error message delivers it past the table.",
            "**A handle resolves only to a scalar**, a string, number or boolean of the input's type; a native tool's "
            "result is an MCP object, so in practice only a Wasm tool's result or a consulted object passes by handle. "
            "**Results a handle names are held in memory by one replica**, dropped at the seal; after a failover a "
            "handle to an earlier result fails its call.",
            "`clearSet` is folded at admit, not at delivery, so a call that fails still adds its label: sound, and "
            "coarser than the record's words.",
            "**The task at a first seating** is not built: the label is optional there (G10 item 94; ADR-0050).",
        ]),
        ("A label is a declaration, not a finding (G10 §8; §9)", "red", [
            "It says what a source was declared to be. **A source declared trusted that is not is seen by nothing**, "
            "and the task's label is the operator's word.",
            "Not covered: flow through the model item by item (`clearSet` bounds the round and traces no value); an "
            "injection that changes a `Report`, or acts through an entry that is not outward; Build, whose `Read` is "
            "not labelled; collusion, unchanged.",
            "Not decided: content-derived labels, field-level handles, handles in a `Report`, write-time masking "
            "against §5 (finding 4), the vocabulary.",
        ]),
        ("It stands beside a Thinker's own defences (§6)", "green", [
            "Nothing here assumes a defence inside the Thinker, and nothing disables one; a defence there is not in "
            "the trusted base and earns no rung.",
            "**The layers, in order**: the Thinker's own defence (unverified); the Listener's labels and handles "
            "(mechanical); rules over labels at the admit (policy); the Observer (semantic, deny-only, after the fact).",
            "A defence lowers how often an injection succeeds. **Labels bound what a successful one can reach.** The "
            "label delivered with clear content is an input a Persona can rely on, because the mechanism computed it.",
        ]),
    ]
    ky = left_bot + 24
    for t, a, b in tcards:
        ky += c.card(X0, ky, pw, t, b, accent=a, size=13.5, tint=(a == "green")) + 20
    left_bot = ky - 20
    y = max(left_bot, y + tt) + 60

    # ------------------------------------------------------------------ what the label machinery trusts
    c.heading(X0, y, "What the label machinery trusts: ADR-0045 A1's three rows, and the reference's instance",
              size=21)
    y += 48
    kcols = [("Id", TW * 0.065, {"bold": True}), ("Component", TW * 0.17), ("Layer", TW * 0.075),
             ("Trusted for", TW * 0.17), ("Class", TW * 0.06), ("Failure can produce", TW * 0.15),
             ("Identity fixed by", TW * 0.11), ("Residual", TW * 0.2)]
    y += c.table(X0, y, kcols, [
        ["T-0045-32", "The label computation and delivery (ADR-0047 §1, §2): the join, the table lookup, `clearSet`",
         "mechanism-boundary", "Every item carries its source's label; a suppressed item's bytes are not sent into the "
                               "guest; `clearSet` holds every label delivered clear", "trust root",
         "Bytes delivered that the table suppresses; a `clearSet` that is too small, so a label forbid does not fire",
         "Promotion: part of the release", "ADR-0047's module states the properties"],
        {"cells": ["T-0045-33", "The label and destination declarations in the entry and the Run root, and the task's "
                                "label in the grant (ADR-0047 §1; ADR-0049 §4)", "policy", "Nothing", "excluded", "—",
                   "The bundle's signature fixes what was declared and not whether it is true; bounded by W7 to W9",
                   "A source declared trusted that is not, or a destination input left unmarked, is seen by nothing. "
                   "**The task's label is the weakest**. Every label forbid is conditional on these being right"],
         "accent": "red"},
        ["T-0045-34", "Handle resolution in the tool host (ADR-0047 §3; ADR-0049 §3), and the rendering of the tool "
                      "list (ADR-0048 §2)", "mechanism-boundary",
         "A handle resolves to the item the record names, for the same principal and round, and only into a tool",
         "trust root", "Suppressed bytes reaching the wrong tool; a Thinker told of a tool it may not call",
         "Promotion: part of the release, with T-0045-25", "Purpose text is prose nothing checks (ADR-0048 §5)"],
    ], size=13, accent="blue") + 24
    c.para(X0, y, TW, "**One hand, ratified the same day it was built.** ADR-0047 was drafted on 2026.10.03 and revised "
           "seventeen times; the reference followed it on 2026.10.05 and the custodian ratified it that day, with its "
           "conditions restated to what the reference could show. **Not reviewed by a reader other than the drafter** "
           "(ADR-0029 A2.5; G10 §4, §8).", 13.5, "muted")
    return c
