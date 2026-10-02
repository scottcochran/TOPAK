"""A3 — Boundary register map: B1–B14 on one system picture, with the register in full."""
from lib import Canvas, text_width

ID, SLUG = "A3", "boundary-register-map"


def btag(c, x, y, bid, accent="ink", size=14):
    """A solid boundary-id badge; returns its width."""
    return c.pill(x, y, bid, accent, size=size, solid=True)


def build():
    c = Canvas(ID, "Fourteen boundaries on one picture: the boundary register mapped",
               "Every boundary the 2026.09.13 register names, placed on the system it divides and tagged with its id. "
               "The register is dated: it was written against the 09.12 checkpoint, nothing in it is a ratified "
               "decision, and rows marked † are analysis with no record behind them. Where a later record has since "
               "changed a boundary, the change is stated as G9 and ToO rev 13 have it, in the last column of the "
               "register below.",
               3200, "derived/topak-boundary-register-2026.09.13.md §0–§2, §6; ToO rev 13 §1, §2.3–§2.9, §3.1, §4.1, "
               "§4.3–§4.4, §5.4, §6, §7.5, §8.1, §10, §15; G9 §1.1, §2.3, §2.5, §8, §7 items 1, 17, 21, 36, 62, 64, 85; "
               "mechanism/GAPS-AND-ASSUMPTIONS.md G1, G19, I43, I44; ADR-0002 A2, ADR-0003 A1–A3, "
               "ADR-0004, ADR-0015, ADR-0023, ADR-0024, ADR-0025, ADR-0028, ADR-0030 §1, §3, ADR-0031 §3, A2, ADR-0032, "
               "ADR-0034, A2 (pending), ADR-0035, ADR-0036, ADR-0037, ADR-0039, ADR-0042 §6 (Proposed), ADR-0044; "
               "ADR-0033 A6, A7 and A8 (pending)")
    X0, X1 = c.x0, c.x1
    y = c.y

    # legend
    y += c.legend(X0, y, [
        ("box", "brown", "the gate, humans"), ("box", "blue", "Build, promotion"), ("box", "green", "Run"),
        ("box", "teal", "membrane, verified object"), ("box", "grey", "outside the system"),
        ("box", "red", "empty cell in the register (B8, B12, B14)", "6 4"),
        ("arrow", "blue", "authority or data crosses"), ("arrow", "green", "subtraction only", "7 5"),
    ], title="Read as") + 30

    # ------------------------------------------------------------------ row G: the gate and humans
    gw = 1250
    g_top = y
    inner_y = g_top + 34
    hk = c.card(X0 + 24, inner_y, gw - 48, "Trust anchor key-holders", [
        "At **archetype custody** removable only with their own consent, so **at the gate**: attributable "
        "non-principals, `Mediated` as attribution only (ADR-0002 A2, ToO §7.5). At degenerate custody they become "
        "principals and the gate moves to the eviction or recovery rule.",
        "`Issue` and `Resign` are environment events no principal can express. **Intent is the sole axiom** "
        "(ADR-0025): no theorem covers it.",
    ], accent="brown", size=14.5)
    c.region(X0, g_top, gw, hk + 58, "B14 · Gate approver: outside every theorem", "red", dash="10 6", sw=2.4)
    btag(c, X0 + gw - 72, g_top - 14, "B14", "red")
    hx = X0 + gw + 40
    hw = X1 - hx
    hh = c.card(hx, inner_y - 34, hw, "Human authority: HITL / HOTL / HOOTL", [
        "**Build: constitutive (HITL).** Promotion needs every counted grant seat; grant-seat humans are principals, "
        "evictable by the anchor (ADR-0024, ToO §7.5). If they never show up, Build **stalls**.",
        "**Run: supervisory (HOTL).** The window `W` is about a second; no human fits inside it. If the human never "
        "shows up, Run **proceeds**: HOTL is disabling only.",
        "**HOOTL: absent.** The interval `D` was named and unbudgeted (†); ADR-0032 gives it a form, "
        "`W + L + D < T_irrev`, with `L` unmeasured.",
    ], accent="brown", size=15, h=hk + 58)
    btag(c, X1 - 72, inner_y - 48, "B10", "brown")
    y = g_top + hk + 58 + 60

    # ------------------------------------------------------------------ row M: provider | Build | B1 | Run | world
    pw, ww = 300, 300
    mid = 360
    dom_w = (X1 - X0 - pw - ww - mid - 2 * 60) / 2
    bx = X0 + pw + 60
    mx = bx + dom_w
    rx = mx + mid
    wx = rx + dom_w + 60
    top = y + 14
    pad = 26
    iw = dom_w - 2 * pad - 40

    def domain_inner(x, acc, name, alphabet, cell_lines):
        cy = top + 42
        c.text(x + pad, cy + 6, name, 24, acc, bold=True)
        cy += 30
        mem_top = cy
        ix = x + pad + 20
        cy += 34
        # the cell
        ch = c.card(ix, cy, iw, "A cell: `thinker` seat + `observer` seat", cell_lines, accent=acc, size=14)
        btag(c, ix + iw - 64, cy - 14, "B7", acc)
        cy += ch + 20
        ah = c.card(ix, cy, iw, "Typed alphabet: the only way out", [alphabet], accent="teal", size=14,
                    bullets=False)
        cy += ah + 28
        return mem_top, cy, ix

    b_mem, b_end, b_ix = domain_inner(bx, "blue", "Build", "`Read` `Draft` `Invoke` `Emit` `Submit` `Vote`: egress only "
                                      "(ADR-0022). `Invoke` is the whole attack surface.", [
        "One principal holds exactly one seat; the agent is a cell of them (ADR-0037).",
        "The Thinker holds a **Persona**: model, prompt, decoding, decoder, seat, pinned (ADR-0016).",
        "Principal type: `Contained` or `Mediated`; **rung 0 is** `Mediated`**, always**.",
    ])
    r_mem, r_end, r_ix = domain_inner(rx, "green", "Run", "`Consult` (ingress, no effect), `Actuate`, `Report` "
                                      "(ADR-0040). No name is shared with Build.", [
        "One principal holds exactly one seat; the agent is a cell of them (ADR-0037).",
        "The Thinker holds a **Persona**: model, prompt, decoding, decoder, seat, pinned (ADR-0016).",
        "Principal type: `Contained` or `Mediated`; **rung 0 is** `Mediated`**, always**.",
    ])
    mem_bot = max(b_end, r_end)
    for x, lab in ((bx, "B2 · Membrane `Contain`"), (rx, "B2 · Membrane, the same component")):
        c.region(x + pad, b_mem, dom_w - 2 * pad, mem_bot - b_mem, lab, "teal", sw=2.2)
    # B6 tags beside the cells' principal-type line
    for ix in (b_ix, r_ix):
        btag(c, ix + iw + 8, b_mem + 34 + 128, "B6", "amber", size=13)
        btag(c, ix + iw + 8, b_mem + 34 + 72, "B8", "red", size=13)
    dom_bot = mem_bot + 26
    c.region(bx, top, dom_w, dom_bot - top, "Build(Contain)", "blue", dash=None, sw=2.6, size=16)
    c.region(rx, top, dom_w, dom_bot - top, "Run(Contain)", "green", dash=None, sw=2.6, size=16)

    # B1 promotion crossing
    py = top + 150
    ph = c.card(mx + 24, py, mid - 48, "Promotion", [
        "The **only** crossing: one signed, promoted artifact (bundle, mechanism release, Persona).",
        "A unanimous quorum grant since ADR-0024; votes bind to (artifact, gate evidence, rules epoch).",
    ], accent="blue", size=14)
    btag(c, mx + 24, py - 16, "B1", "blue")
    ay = py + ph + 34
    c.arrow([(bx + dom_w, ay), (rx, ay)], "blue", sw=2.6, label="Submit → promoted", lpos=0.5)
    c.line(mx + mid / 2, ay + 18, mx + mid / 2, dom_bot, "blue", sw=2, dash="3 5")

    # provider (B8) and the world (B3)
    prov_y = b_mem + 34 + 40
    p_h = c.card(X0, prov_y, pw, "Model provider", [
        "Weights, tokenizer and endpoint change at a cadence TOPAK **does not control**.",
        "Crosses into the Persona by **promotion only**; silent substitution has no instant (†).",
    ], accent="grey", size=14, dash="6 4")
    btag(c, X0 + pw - 60, prov_y - 14, "B8", "red")
    c.arrow([(X0 + pw, prov_y + 60), (b_ix, prov_y + 60)], "red", dash="7 5", label="promotion only", lpos=0.45)

    w_h = c.card(wx, prov_y, ww, "External state", [
        "The world a tool acts on and a reader reads.",
        "Effects reach it as exactly **{tool invocation, principal emission}** (ADR-0015, C2).",
        "**B3**: admissibility is validated, total over the floor alphabet; the decoder's fidelity is unbounded (†).",
    ], accent="grey", size=14, dash="6 4")
    btag(c, wx + ww - 60, prov_y - 14, "B3", "teal")
    ey = prov_y + w_h - 40
    c.arrow([(r_ix + iw, ey), (wx, ey)], "teal", sw=2.6)
    # B3 note beneath the world box
    c.card(X0, prov_y + p_h + 26, pw, "B8 · Persona / occupant", [
        "The largest empty cell in the grid (register §8).",
    ], accent="red", size=13.5, tint=False, dash="6 4")

    y = dom_bot + 60

    # ------------------------------------------------------------------ row V: verified object | edge (B4), B13
    vw = 1700
    v_top = y
    cy = v_top + 36
    vo_w = vw - 48
    cw3 = (vo_w - 2 * 18) / 3
    items = [
        ("Enforcement mechanism", "The admit path: epoch fence → lease → syntactic lift → floor → bundle → "
         "consensus-ordered admit (ToO §15)."),
        ("Version pinning", "The mechanism release, its floor text, schema S and engine, pinned by digest."),
        ("Epoch fencing", "Actions under a fenced epoch are rejected by mechanism, not policy: the cheapest check."),
        ("Policy floor", "Cedar, linked into the mechanism, resident (ADR-0012, ADR-0030). The genesis text is "
         "**DRAFT**."),
        ("Rules floor", "R1, R2, R5, R6, R7, R9 bound every anchor issuance (ADR-0026)."),
        ("Floor exceptions", "Break-glass and erasure, plus the six forensic classes, as floor entries."),
    ]
    hmax = max(c.card(0, 0, cw3, t, [b], accent="teal", bullets=False, size=14, draw=False,
                      status="draft" if t == "Policy floor" else None) for t, b in items)
    v_bot = cy + 2 * hmax + 16 + 24
    c.region(X0, v_top, vw, v_bot - v_top, "Verified object: what is proved once, with the mechanism", "teal",
             dash=None, sw=2.4, tint=True)
    for i, (t, b) in enumerate(items):
        xx = X0 + 24 + (i % 3) * (cw3 + 18)
        yy = cy + (i // 3) * (hmax + 16)
        c.card(xx, yy, cw3, t, [b], accent="teal", bullets=False, size=14, h=hmax,
               status="draft" if t == "Policy floor" else None)
    # B13 tag on the epoch fencing card
    btag(c, X0 + 24 + 2 * (cw3 + 18) + cw3 - 70, cy - 14, "B13", "violet")

    ex = X0 + vw + 150
    ew = X1 - ex
    e_items = [
        ("Operational bundles", "OPA/Rego, signed (ADR-0044), versioned; may subtract, never add. Change at "
         "incident cadence.", "B4"),
        ("Personas", "Promoted parameters; the decoder ships in the Persona, the validator in the mechanism "
         "(ADR-0018).", "B8"),
        ("Deployment rungs", "Per-axis declarations under ADR-0023: degenerate forms lose theorems, never gain "
         "capability.", "B11"),
    ]
    eh = max(c.card(0, 0, ew - 48, t, [b], bullets=False, size=14, draw=False) for t, b, _ in e_items)
    v_bot = max(v_bot, v_top + 36 + 3 * eh + 2 * 14 + 24)
    for i, (t, b, tg) in enumerate(e_items):
        yy = v_top + 36 + i * (eh + 14)
        c.card(ex + 24, yy, ew - 48, t, [b], accent="grey", bullets=False, size=14, h=eh)
        btag(c, ex + ew - 24 - 70, yy - 13, tg, {"B4": "teal", "B8": "red", "B11": "grey"}[tg], size=13)
    c.region(ex, v_top, ew, v_bot - v_top, "Parameterized edge", "grey", sw=2.2)
    # B4: the boundary between them
    bx4 = X0 + vw + 75
    c.line(bx4, v_top, bx4, v_bot, "teal", sw=3, dash="10 6")
    btag(c, bx4 - 24, v_top + (v_bot - v_top) * 0.62, "B4", "teal", size=15)
    c.arrow([(ex, v_top + 36 + eh / 2), (X0 + vw, v_top + 36 + eh / 2)], "green", dash="7 5",
            label="refinements only:\nsubtraction", lpos=0.5, lw=140)
    # membranes instantiate the mechanism
    mv = (dom_bot + v_top) / 2
    c.arrow([(bx + dom_w / 2, dom_bot), (bx + dom_w / 2, v_top)], "teal")
    c.arrow([(rx + 240, dom_bot), (rx + 240, mv), (X0 + vw - 120, mv), (X0 + vw - 120, v_top)], "teal")
    c.label((bx + dom_w / 2 + X0 + vw - 120) / 2, mv, "`Contain` is one component, instantiated twice: both "
            "membranes run this mechanism", "teal", 13.5)
    y = v_bot + 60

    # ------------------------------------------------------------------ row R: planes, retention, stack
    colw = (X1 - X0 - 2 * 40) / 3
    # B5 planes
    r_top = y
    p1 = c.card(X0 + 20, r_top + 34, colw - 40, "Control-plane facts", [
        "Admits, denials, votes, issuances, heartbeats: actions, identities, ordering.",
        "The archive keeps a **hash and a pointer** for each payload (ADR-0004).",
    ], accent="violet", size=14)
    p2 = c.card(X0 + 20, r_top + 34 + p1 + 50, colw - 40, "Cognitive payloads", [
        "Prompt text, commentary, raw emission: in a separately governed store built for deletion.",
    ], accent="grey", size=14)
    c.arrow([(X0 + colw / 2, r_top + 34 + p1 + 50), (X0 + colw / 2, r_top + 34 + p1)], "violet",
            label="facts cross; payloads do not", lpos=0.5)
    r_h = 34 + p1 + 50 + p2 + 24
    # B9 retention
    x2 = X0 + colw + 40
    q1 = c.card(x2 + 20, r_top + 34, colw - 40, "Round topics: one per principal per round", [
        "**Sealed** on emit completion (Build: at `Submit`); the topic is the **unit of erasure** (ADR-0003).",
        "Erasure deletes sealed topics; crypto-shredding was rejected (ToO §4.3).",
    ], accent="green", size=14)
    q2 = c.card(x2 + 20, r_top + 34 + q1 + 22, colw - 40, "Forensic floor F1–F6: never erasable", [
        "Admits, stop attribution, votes, issuances, break-glass, erasure events (ADR-0028, C1).",
    ], accent="teal", size=14)
    r_h = max(r_h, 34 + q1 + 22 + q2 + 24)
    # B12 deployment stack + B11
    x3 = X0 + 2 * (colw + 40)
    layers = [("Containment layer: `Contain`", "teal", None), ("Sandbox", "red", "6 4"),
              ("Host kernel", "red", "6 4"), ("Hardware", "red", "6 4")]
    ly = r_top + 34
    lh = 44
    for i, (lab, acc, d) in enumerate(layers):
        c.rect(x3 + 20, ly, colw - 40 - 150, lh, acc, tint=True, dash=d, rx=6)
        c.text(x3 + 36, ly + 28, lab, 15, acc, bold=True)
        ly += lh + 8
    # side labels: the deployment-stack vocabulary (register §10.1)
    c.text(x3 + colw - 160, r_top + 34 + 20, "formally", 12.5, "teal", bold=True)
    c.text(x3 + colw - 160, r_top + 34 + 36, "verified", 12.5, "teal", bold=True)
    for i in (1, 2, 3):
        c.text(x3 + colw - 160, r_top + 34 + i * (lh + 8) + 20, "operationally", 12.5, "red", bold=True)
        c.text(x3 + colw - 160, r_top + 34 + i * (lh + 8) + 36, "audited", 12.5, "red", bold=True)
    c.text(x3 + 20, ly + 8, "Deployment-stack vocabulary (register §10.1)", 12.5, "faint")
    ly += 14
    sh = c.card(x3 + 20, ly + 10, colw - 40, "Below the membrane", [
        "**Effect exclusivity is assumed, not enforced** (register §10.1). ADR-0034 now designs the discharge: "
        "rungs 0–3 and profile clauses P1–P7, attested at lease grant. **Narrowed, not closed**: the node's launcher issues rung 1 on profiles that declare "
        "P3 `fail`, rung 3 only SIMULATED (ADR-0033 A7, pending); **no real principal is** `Contained`.",
    ], accent="red", size=14, tint=False, dash="6 4")
    r_h = max(r_h, ly + 10 + sh + 24 - r_top)
    c.region(X0, r_top, colw, r_h, "B5 · Plane: control plane / cognitive", "violet")
    c.region(x2, r_top, colw, r_h, "B9 · Retention / erasure", "green")
    c.region(x3, r_top, colw, r_h, "B12 · Deployment stack: sandbox and below", "red", sw=2.4)
    btag(c, x3 + colw - 130, r_top - 14, "B11", "grey", size=13)
    y = r_top + r_h + 70

    # ------------------------------------------------------------------ the register itself
    c.text(X0, y + 22, "The register, 2026.09.13, in full", 22, "ink", bold=True)
    c.pill(X0 + text_width("The register, 2026.09.13, in full", 22, True) + 20, y + 2,
           "dated: written against the 09.12 checkpoint; nothing in it is ratified", "grey", size=12.5)
    y += 40
    y += c.para(X0, y, X1 - X0,
                "The first five columns are the register's §1 verbatim. **†** marks a row the register says is "
                "analysis with no ADR behind it; [[red|red]] marks the empty or undefined cells. The last column is "
                "this diagram's, drawn from G9 and ToO rev 13: what a later record changed at that boundary.",
                14.5, "muted") + 14
    T = "red"
    cols = [("Boundary", 250, {"bold": True}), ("Cadence (outer / inner)", 270), ("Instant", 310),
            ("Interval of untruth", 300), ("If the check is unavailable", 400),
            ("Since the register (state per G9, narrative per ToO rev 13)", X1 - X0 - 1530)]
    rows = [
        ["B1 Domain `Build | Run`", "Release / incident", "**Promotion**: signature over provenance",
         "None claimed; `Submit` is sole egress", "Fail-closed. Pipeline stalls; PC/EC makes this affordable (ADR-0002)",
         "The single signing key is gone: promotion is a **unanimous quorum grant** of grant seats, votes bound to "
         "(artifact, gate-evidence, rules epoch) (ADR-0024). A promotion also stalls without the author's cell "
         "Observer's coverage to the seal (ADR-0024 A2, ADR-0039 §3, C4)."],
        ["B2 Membrane `Contain`", "Release / per-action", "**Admit decision**", "None; rejection is synchronous",
         "Fail-closed. Resident default-deny floor, no fetch dependency (ADR-0012)",
         "The floor is a Cedar library **linked** into the mechanism: no process, socket or fetch; "
         "`admit ⟺ floor_permit ∧ ¬bundle_deny`, any floor error a deny (ADR-0030 §1, §3, C1)."],
        ["B3 Typed effect", "Release (validator) / Persona (decoder)", "**Validate**: total over floor alphabet",
         "None for admissibility; [[red|unbounded for fidelity †]]", "Fail-closed. Parse failure is a local deny, "
         "monotone (ADR-0018)",
         "Raw emission is retained at the archetype so the decoder can be re-run and compared: recovers "
         "faithfulness, not intent (ADR-0037 §3; D-0037-2 if not retained). Decoder–alphabet compatibility is "
         "still open (G9 item 17)."],
        ["B4 Verified / parameterized", "Release / deploy / incident", "**Promotion**: `bundle ⊑ floor`",
         "Bundle staleness, **unbounded but floor-bounded below**", "Fail-closed and safe while stalled. The "
         "model case (ADR-0010)",
         "The instant moved: `bundle ⊑ floor` now holds **by composition at every admit**, for every bundle at "
         "every age, and nobody decides it at promotion (ADR-0030 §1). A bundle loads only under an issued key's "
         "signature (ADR-0044, C1; built, ADR-0033 A6)."],
        ["B5 Plane control-plane / cognitive", "Release / per-emission", "**Fact construction** at Observer finding",
         "None claimed", "Fail-closed; no payload crosses by default (ADR-0004)",
         "Unchanged in principle. Raw emission joins the payload side, beside the typed action (ADR-0004 B12, "
         "ADR-0037); the Reader stage's results cross as facts for the cell Observer (ToO §2.8)."],
        ["B6 Principal type `Contained` / `Mediated`", "Per-principal, static", "**Lease grant**",
         "Whole lease, for `Mediated`", "N/A: predicate, not a runtime check (09.12 §5)",
         "The lease carries `[profile digest, rung]` (ADR-0031 §3). `Contained` has four conjuncts (ADR-0034 §4); "
         "the fourth, lineage independence, is ADR-0035, **Proposed**, so **no real principal is** `Contained`. The "
         "reference's lookup answers yes only for a **SIMULATED** rung-3 lease under a test-issued criterion: a "
         "witness, not a claim (G9 §2.3; ADR-0033 A7, pending)."],
        ["B7 Seat LTRO separation of duties", "Release / Persona", "**Seat binding** in Persona", "None claimed",
         "Fail-closed if binding is verified; [[red|unstated †]] (ADR-0016)",
         "Seats are principals: **a principal holds exactly one seat**, the LTRO is a cell; Thinker and Observer are "
         "seats, Listener and Reader are stages (ADR-0037, C3, C4). Alphabets bounded by seat kind in floor text, "
         "forbid B10 and a tightened B6, checked at the grant path first."],
        {"cells": ["B8 Persona / occupant identity", "Provider ([[red|uncontrolled]]) / Persona promotion",
                   "**Persona promotion only**", "[[red|Unbounded: no expiry, no re-attestation †]]",
                   "[[red|Undefined.]] Largest empty cell in the grid (§8)",
                   "Persona expiry now has a **bound, not a clock**: `ttl ≤ T_persona` at grant and every renewal "
                   "(ADR-0031 A2; built, ADR-0033 A6), still read on the local clock (G9 item 62). A revoked Persona "
                   "is a targeted revocation (ToO §6). ToO §10 still calls B8 the most critical boundary."],
         "accent": "red"},
        ["B9 Retention / erasure", "Deploy / per-round", "**Seal** on emit completion", "Between emit and seal",
         "Fail-closed on replay; [[red|fail-open on forensics †]] (ADR-0003, 0006, 0020)",
         "Forensic floor: six classes non-erasable for the declared horizon (ADR-0028, C1). Crypto-shredding "
         "rejected. Topic identity carries the rules-epoch chain (A1) and a denials-only `after` companion (A2, "
         "C1). Genesis issues no erasure roster, so erasure is disabled from epoch 0."],
        {"cells": ["B10 Human authority HITL / HOTL / HOOTL", "Constitutive / supervisory / absent",
                   "**Gate** (HITL) or **non-refresh** (passive e-stop)", "`D`: [[red|unbudgeted †]]",
                   "Build: stalls. Run: **proceeds**: HOTL is disabling only (09.12 §4)",
                   "The timing property is a budget, `W + L + D < T_irrev` per effect class (ADR-0032 §4); `L` is "
                   "unmeasured and no effect class declares `T_irrev`. Run effect admits stall on a dead cell "
                   "Observer, floor entry R3 (ADR-0039, C4)."],
         "accent": "amber"},
        ["B11 Deployment rung archetype / profile", "Release / per-deployment", "**Rung manifest**", "None claimed",
         "Fail-closed by subtraction; monotone (open: axis question)",
         "The axis question is answered: degeneracy, not a ladder; rungs are per axis and every degeneracy carries a "
         "declaration record (ADR-0023, C3). No deployment declaration has been written (G9 §8); the reference "
         "declares a rung per seat meanwhile, accepted in conversation and owed to a record (G9 items 64, 85)."],
        {"cells": ["B12 Deployment stack sandbox and below", "—", "[[red|None: no mechanism exists]]",
                   "[[red|Permanent]]", "[[red|Undefined.]] Effect exclusivity is assumed, not enforced (§10.1)",
                   "The instant now exists: **lease grant**, the confinement field (ADR-0031 §3). The design exists: "
                   "attestation rungs 0–3 and profile clauses P1–P7 (ADR-0034, C2, C4); the rung-1 launcher is "
                   "ADR-0036, **Proposed**. The mechanism is **narrowed, not closed** (G9 item 1, the sandbox gap): "
                   "the node's launcher issues rung 1 on profiles that declare P3 `fail`, rung 3 only SIMULATED, "
                   "rung 2 a seam (ADR-0033 A7, pending); no image passes P3 (item 36). For Run, P4 becomes "
                   "**channel fidelity** (ADR-0034 A2, pending; ADR-0042 §6, Proposed), built for Wasm-hosted "
                   "tools (ADR-0033 A8, pending) and checked for no native one (`mechanism/` G19)."],
         "accent": "red"},
        ["B13 Epoch / lease temporal fence", "Deploy / per-round", "**Fence** / **expiry**", "≤ TTL for passive stop",
         "Fail-closed. Expiry is a local clock read: [[red|but see §9.1 †]]",
         "§9.1 is discharged: **clocks buy liveness, never safety** (ADR-0032). Expiry is read locally and then "
         "ordered (ADR-0031 E1); the fence is the Paxos log index at grant; revocation is targeted or an epoch "
         "fence (ADR-0031, C1)."],
        {"cells": ["B14 Gate approver", "—", "[[red|None: outside every theorem]]", "[[red|Permanent]]",
                   "[[red|Undefined.]] Approver is not evictable, therefore unmodeled (§10.2)",
                   "The promotion approver is now a principal (ADR-0024), so what sits at the gate is the anchor's "
                   "key-holders at archetype custody (ADR-0002 A2, ToO §7.5). Still outside every theorem: anchor "
                   "intent is the sole axiom, and anchor capture heads the residual risks (ADR-0025)."],
         "accent": "red"},
    ]
    y += c.table(X0, y, cols, rows, size=14, accent="ink") + 50

    # ---- empty cells (§2) and the structural companion (§6)
    lw = 1180
    c.text(X0, y + 20, "§2 · The empty cells are the finding", 20, "red", bold=True)
    c.text(X0 + lw + 50, y + 20, "§6 · Structural companion: what crosses", 20, "ink", bold=True)
    y += 36
    h1 = c.table(X0, y, [("Row", 200, {"bold": True}), ("Missing", 450), ("Consequence", lw - 650)], [
        {"cells": ["B8 Persona", "No instant for provider-side change; no interval bound",
                   "Silent substitution breaks the pin with **no event anywhere in the system**"], "accent": "red"},
        {"cells": ["B12 Sandbox", "No instant, no mechanism, permanent interval",
                   "Every containment theorem is conditional on an undischarged assumption"], "accent": "red"},
        {"cells": ["B14 Gate approver", "No instant, no mechanism, permanent interval",
                   "The one authority in the design that no theorem constrains"], "accent": "red"},
        {"cells": ["B10 Human", "Interval `D` named but never budgeted",
                   "HOTL without a response budget reproduces the ignored-warning failure"], "accent": "amber"},
    ], size=14, accent="red")
    h1b = c.card(X0, y + h1 + 20, lw, "What the register said to act on, and where it stands", [
        "**B12 and B14 are structural and known**; **B8 is the one to act on**: the only row whose outer side "
        "changes at a cadence TOPAK does not control, does not observe by default, and cannot fence (§2).",
        "Since: B12 has an instant, a design and, at the reference, a rung-1 launcher and a SIMULATED rung 3, "
        "pending, with no real principal `Contained`; B8 has a bound, `T_persona`, on a local clock, "
        "and a lineage criterion that is Proposed; B14 is narrowed to the anchor and stays axiomatic.",
    ], accent="grey", size=14)
    cx = X0 + lw + 50
    h2 = c.table(cx, y, [("Boundary", 120, {"bold": True}), ("Inside / above", 330), ("Outside / below", 300),
                         ("What legitimately crosses", X1 - cx - 120 - 330 - 300 - 150), ("ADR", 150)], [
        ["B1", "`Build`", "`Run`", "One signed, promoted artifact", "0001, 0002"],
        ["B2", "Principals (evictable)", "Gate approvers (not evictable)", "Typed actions in; admit/deny out", "0002"],
        ["B3", "Cognition", "External state", "`{tool invocation, principal emission}`", "0007, 0015, 0018"],
        ["B4", "Mechanism + pinning + fencing + floor", "Bundles, Personas, rungs", "Refinements only: subtraction",
         "0010, 0012"],
        ["B5", "Control-plane facts", "Cognitive payloads", "Facts cross; payloads do not", "0004"],
        ["B6", "`Contained(p)`", "`Mediated(p)`", "Safety theorems quantify inside only", "09.12 §5"],
        ["B7", "Listener / Thinker / Reader / Observer", "—", "Seat-scoped alphabet subsets (open)", "0008, 0016"],
        {"cells": ["B8", "Pinned Persona", "Provider-side model", "Promotion only", "0016, 0017"], "accent": "red"},
    ], size=14, accent="ink")
    y2 = y + h2 + 20
    c.card(cx, y2, X1 - cx, "Read with the companion", [
        "**The criterion for B2 is evictability, not location**: if you can be evicted you are a principal; if you "
        "are the authority that evicts you are at the gate. That is exactly why B14 exists (§6).",
        "B7's row names four seats and ADR-0008, both since overtaken: two are seats, two are stages (ADR-0037), and "
        "ADR-0008 is superseded by ADR-0038. B6 and B11 to B14 have no companion row in the register.",
    ], accent="grey", size=14)
    return c
