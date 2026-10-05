"""A2 — Two domains, one membrane: Build(Contain) → Run(Contain)."""
from lib import Canvas

ID, SLUG = "A2", "two-domains-one-membrane"


def build():
    c = Canvas(ID, "Two domains, one membrane: `Build(Contain) → Run(Contain)`",
               "`Build` produces artifacts and `Run` operates them. The arrow is authority flow; the parentheses are a "
               "refinement boundary (specification conjunction plus existential hiding of internal variables). "
               "`Contain` is one component instantiated twice, not a third domain.",
               2400, "ToO rev 14 §1, §2.3, §2.4, §2.8, §2.9, §2.10, §3.3, §4.1, §5.4, §7.1, §7.10; ADR-0001, ADR-0002, "
               "ADR-0015, ADR-0021, ADR-0022, A3, ADR-0024, A3 (provisional), ADR-0034 §4, A2, ADR-0035 (Proposed), "
               "ADR-0037 §4, §7, A2, A3, A4, ADR-0039 §2, A2, ADR-0040, ADR-0041 §2, ADR-0042 §5, §6, A1, ADR-0043 §1, A1, "
               "ADR-0047, ADR-0048, ADR-0049 §5, ADR-0050 §1, §4 (provisional), ADR-0052 §1, §2 (provisional); "
               "ADR-0033 A7, A8, A11; G10 §1, §2.3, §2.5, §8; boundary register B1, B2, B3")
    X0, X1 = c.x0, c.x1
    y = c.y + 10

    # ---- the gate (environment above both domains)
    gate_h = c.card(X0, y, X1 - X0, "At the gate: outside every proof, carried as assumption or declaration", [
        "**The trust anchor** issues rules (`Issue`, `Resign` are environment events no principal can express). At "
        "archetype custody its key-holders are removable only with their own consent, so they sit at the gate (B14).",
        "**The evictability test** (ADR-0002 A2): a principal is anything evictable by an authority other than itself; "
        "whatever is not is at the gate. Resignation is not eviction.",
        "**The operator is no longer at the gate**: it holds a seat of kind `operator` and is a principal, its first "
        "lease from a quorum (ADR-0050, provisional). At the reference a [[red|BOOTSTRAP]] socket seats in place of "
        "the quorum, and whoever reaches it can seat (ToO §7.10; G10 §8).",
    ], accent="brown", size=14.5)
    y += gate_h + 30
    c.arrow([(X0 + 300, y - 30), (X0 + 300, y + 22)], "brown", label="issued rules: rosters, quorum, keys",
            lpos=0.5)
    c.arrow([(X1 - 300, y - 30), (X1 - 300, y + 22)], "brown", label="same rules epoch fences both domains",
            lpos=0.5)
    y += 40

    mid_w = 330
    gapm = 120
    dom_w = (X1 - X0 - mid_w - 2 * gapm) / 2
    bx, rx = X0, X1 - dom_w
    mx = X0 + dom_w + gapm
    top = y
    pad = 28
    inner_b, inner_r = bx + pad + 22, rx + pad + 22
    iw = dom_w - 2 * pad - 44

    def domain(x, name, sub, acc):
        cy = top + 30
        c.text(x + pad, cy + 22, name, 26, acc, bold=True)
        cy += 34
        cy += c.para(x + pad, cy, dom_w - 2 * pad, sub, 14.5, "muted") + 18
        return cy

    cy = domain(bx, "Build", "Authors the specifications, policy, floors, bundles, mechanism releases and Personas "
                "that Run is later judged against. **The Byzantine threat lives here** (the inversion).", "blue")
    domain(rx, "Run", "Operates promoted artifacts against external state. Its budget is hard: the propagation "
           "window `W` is about a second, so Run is human-on-the-loop (HOTL).", "green")
    mem_top = cy + 14

    # ---- paired blocks, Build | Run, equal heights per pair
    seats_b = [
        "`thinker` seats author; `observer` seats read, emit and, on the veto roster, deny; `grant` seats (human, "
        "`Mediated`) read, emit and vote.",
        "Per artifact, author and voters are disjoint; the author is recused by the `Vote` envelope.",
    ]
    seats_r = [
        "A `thinker` seat holds all three variants; an `observer` seat `Consult` and `Report` (ADR-0043 §2).",
        "There is no terminal variant: **a Run round ends when its lease ends**; a Run seat cannot abstain.",
    ]
    ppl_b = [
        "`operator`, either domain, a person and no other seat: `Regrant`, `Renew`, `AttestGates`, `EndRound`, "
        "`Revoke`, `FenceEpoch`, and no authoring variant (ADR-0037 A4; ADR-0050 §4).",
        "Adds need a live lease and a live peer; `EndRound` and `Revoke` a live lease or a fresh sign-on; `FenceEpoch` a "
        "live lease (ToO §7.10).",
    ]
    ppl_r = [
        "`operator`, as in Build; `AttestGates` is Build's (ADR-0037 A4).",
        "`emergency`, Run only, a person for one round: `Consult`, `Actuate`, `Report`, each action signed "
        "with the person's key; activated by the break-glass roster's quorum, no successor, no renewal (ADR-0037 A3; "
        "ADR-0052 §1, §2).",
    ]
    ing_b = [
        "The Listener delivers the task, each admitted `Read`, and the round's **tool list**, rendered by the "
        "mechanism from the entries the lease may call (ADR-0037 A2; ADR-0048).",
        "`Read` is not labelled (ToO §2.10). Each entry has ADR-0049's one form (ADR-0022 A3).",
    ]
    ing_r = [
        "**Four items and nothing else**: the task, each `Consult`'s content, each `Actuate`'s result, the tool list "
        "(ADR-0043 A1). Each carries a **label**, a function of its source.",
        "Delivered **clear** with its label or as a **handle**, a name and no bytes; a handle may be an argument the "
        "tool host resolves (ADR-0047). `R5`–`R7` forbid an outward `Actuate` over `clearSet` (ADR-0041 A1).",
        "The round's topic **opens with the tool list**, so the Observer is given what its Thinker was (ADR-0042 A1).",
    ]
    det_b = [
        "Build favours consistency over latency; detection only has to finish before the gate clears (ADR-0021, "
        "ADR-0039).",
        "A promotion stalls unless the author's cell Observer reported coverage to the seal.",
    ]
    det_r = [
        "Floor entry R3: every `Actuate` or `Report` under a Thinker needs a live cell Observer; `Consult` is exempt "
        "(ADR-0039, ADR-0041 §2). A dead or slow Observer stops its own Thinker and nothing else.",
        "**An emergency seat is not coupled**: it is not a `thinker` seat (ADR-0039 A2, provisional with ADR-0052).",
    ]
    b_tab = [("Build alphabet (ADR-0022), egress only", iw * 0.42, {"mono": True}), ("Effect", iw * 0.58)]
    b_rows = [
        ["Read(ref)", "Resolve a content-addressed object in the pinned corpus root"],
        ["Draft(target, content)", "Write into the round-scoped workspace"],
        ["Invoke(tool, inputs)", "Run a tool allowlisted by name and digest: **the whole attack surface**"],
        ["Emit(record)", "Append to the principal's round topic"],
        ["Submit(digest | ⊥)", "Offer the sealed workspace for promotion, or abstain"],
        ["Vote(verdict, digest, evidence, rulesEpoch)", "Cast a promotion vote"],
    ]
    r_tab = [("Run alphabet (ADR-0040)", iw * 0.42, {"mono": True}), ("Class and envelope", iw * 0.58)]
    r_rows = [
        ["Consult(ref)", "**Ingress, no effect**: `ref` resolves in the pinned Run root"],
        ["Actuate(tool, inputs)", "**Effect**: tool allowlisted by name and digest; its entry declares the channel it "
                                  "opens, and the tool host reads the target from that entry (ADR-0049 §5). A read "
                                  "of live state is an `Actuate`"],
        ["Report(record)", "**Effect**: the principal's own round topic, this epoch and round, unsealed"],
        {"cells": ["(no name shared)", "No variant name is common to Build and Run (ADR-0022 A2); only the carrier is "
                   "shared"], "accent": "grey"},
    ]

    pairs = [
        ("card", "Principals, one seat each, leased per round", seats_b, seats_r, ("blue", "green"), None),
        ("card", "People in seats: `Mediated`, a person is not confined", ppl_b, ppl_r, ("brown", "brown"),
         "provisional"),
        ("table", None, (b_tab, b_rows), (r_tab, r_rows), ("blue", "green"), None),
        ("card", "Ingress: what reaches the Thinker", ing_b, ing_r, ("teal", "teal"), None),
        ("card", "Detection", det_b, det_r, ("pink", "pink"), None),
    ]
    det_titles = ("Detection couples the gate, not each admit", "Detection couples every effect-bearing admit")
    ccy = mem_top + 30
    for kind, title, lb, rb, (ab, ar), st in pairs:
        if kind == "table":
            hb = c.table(inner_b, ccy, lb[0], lb[1], size=13.5, accent=ab)
            hr = c.table(inner_r, ccy, rb[0], rb[1], size=13.5, accent=ar)
            ccy += max(hb, hr) + 16
            continue
        tb, tr = (det_titles if title == "Detection" else (title, title))
        if title.startswith("Ingress"):
            tb, tr = "Build's ingress: what reaches the Thinker", "Run's ingress: four labelled items"
        hh = max(c.card(0, 0, iw, tb, lb, size=14, status=st, draw=False),
                 c.card(0, 0, iw, tr, rb, size=14, status=st, draw=False))
        c.card(inner_b, ccy, iw, tb, lb, accent=ab, size=14, h=hh, status=st,
               status_extra="ADR-0050" if st else "")
        c.card(inner_r, ccy, iw, tr, rb, accent=ar, size=14, h=hh, status=st,
               status_extra="ADR-0050, ADR-0052" if st else "")
        ccy += hh + 16
    ccy += 10
    c.region(bx + pad, mem_top, dom_w - 2 * pad, ccy - mem_top, "Contain · the membrane (B2)", "teal")
    c.region(rx + pad, mem_top, dom_w - 2 * pad, ccy - mem_top, "Contain · the same component (B2)", "teal")

    # -------- the promotion crossing (B1)
    py = top + 200
    ph = c.card(mx, py, mid_w, "Promotion (B1)", [
        "The **only** crossing: one signed, promoted artifact: a bundle, a mechanism release (including floor "
        "changes) or a Persona.",
        "A quorum grant (ADR-0024): every counted grant seat must grant; a timeout is never a grant.",
        "Votes bind to (artifact digest, gate-evidence digest, rules epoch).",
        "Gates enable voting; they do not vote.",
    ], accent="blue", size=14)
    ay = py + 60
    c.arrow([(bx + dom_w - pad, ay), (mx, ay)], "blue", sw=2.6, label="Submit(digest)", lpos=0.5, loff=(0, -22))
    c.arrow([(mx + mid_w, ay), (rx + pad, ay)], "blue", sw=2.6, label="promoted", lpos=0.5, loff=(0, -22))
    sy = py + ph + 24
    sh = c.card(mx, sy, mid_w, "A promotion seats", [
        "What is promoted may be a **seating**: principal, seat, Persona, bundle revision, confinement, alphabet. When "
        "the tally completes, the mechanism grants the first lease (ADR-0024 A3).",
        "[[red|Not built]] at the reference (ToO §7.1, §7.10).",
    ], accent="blue", size=14, status="provisional", status_extra="bootstrap set")
    ny = sy + sh + 40
    nh = c.card(mx, ny, mid_w, "What does not cross", [
        "No variant name.",
        "No principal: a seat belongs to one domain.",
        "Nothing unpromoted: Run never loads an artifact Build did not promote.",
    ], accent="red", size=14, tint=False, dash="6 4")
    ey = ny + nh + 40
    eh = c.card(mx, ey, mid_w, "Effects reach the world only as admits", [
        "Effects: exactly {tool invocation, principal emission} (ADR-0015).",
        "Authority changes: exactly {promotion, anchor issuance}.",
        "Break-glass is not a third kind: a lease whose activation is a grant by a roster's quorum (ToO §4.1; "
        "ADR-0052, provisional).",
        "Denials are not ordered, and they are recorded.",
    ], accent="teal", size=14)

    bottom = max(ccy + 30, ey + eh + 30)
    c.region(bx, top, dom_w, bottom - top, "Build(Contain)", "blue", dash=None, sw=2.6, tint=False, size=16)
    c.region(rx, top, dom_w, bottom - top, "Run(Contain)", "green", dash=None, sw=2.6, tint=False, size=16)

    y = bottom + 40
    w3 = (X1 - X0 - 2 * 24) / 3
    contain_body = [
        "**Proved**: a property class over the action vocabulary and its envelope, by mechanical extraction.",
        "**Assumed, operationally discharged**: effect exclusivity, the principal reaches the world only through the "
        "alphabet (ADR-0015).",
    ]
    cm_body = [
        "Safety theorems quantify over `Contained` principals; a `Mediated` one (shell, egress, git) gets attribution "
        "and authorization, not containment.",
        "**No real principal is** `Contained`: the reference's lookup has members only in a **SIMULATED** rung-3 run "
        "under a test-issued criterion, a witness and not a claim (G10 §2.3; ADR-0033 A7).",
        "**The Run profile is in force** (ADR-0034 A2 with ADR-0042 §6, Batch 30): P4 replaced by channel fidelity, "
        "owned by the tool host's Wasm runtime. Run principals are still `Mediated` in fact: the fourth conjunct, "
        "ADR-0035, is Proposed (ToO §2.3, §2.9).",
        "An operator and an emergency seat are `Mediated` **by design** (ADR-0050 §1; ADR-0052 §1).",
    ]
    inv_body = [
        "Build agents write what Run is judged against. The failure that matters, silent abstention, a vacuously "
        "true predicate and green gates, is a Build failure.",
        "Every Build choice that looks expensive pays for that.",
    ]
    hh = max(c.card(0, 0, w3, "Contain claims two conjuncts", contain_body, draw=False),
             c.card(0, 0, w3, "Contained or Mediated (B6)", cm_body, draw=False))
    c.card(X0, y, w3, "The inversion", inv_body, accent="red", h=hh)
    c.card(X0 + w3 + 24, y, w3, "Contain claims two conjuncts", contain_body, accent="teal", h=hh)
    c.card(X0 + 2 * (w3 + 24), y, w3, "Contained or Mediated (B6)", cm_body, accent="amber", h=hh)
    return c
