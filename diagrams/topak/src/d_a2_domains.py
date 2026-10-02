"""A2 — Two domains, one membrane: Build(Contain) → Run(Contain)."""
from lib import Canvas

ID, SLUG = "A2", "two-domains-one-membrane"


def build():
    c = Canvas(ID, "Two domains, one membrane: `Build(Contain) → Run(Contain)`",
               "`Build` produces artifacts and `Run` operates them. The arrow is authority flow; the parentheses are a "
               "refinement boundary (specification conjunction plus existential hiding of internal variables). "
               "`Contain` is one component instantiated twice, not a third domain.",
               2400, "ToO rev 11 §1, §2.4, §2.9, §5.2, §5.4, §7.1; ADR-0001, ADR-0002, ADR-0021, ADR-0022, ADR-0024, "
               "ADR-0039, ADR-0040; boundary register B1, B2, B3")
    X0, X1 = c.x0, c.x1
    y = c.y + 10

    # ---- the gate (environment above both domains)
    gate_h = c.card(X0, y, X1 - X0, "At the gate: outside every proof, carried as assumption or declaration", [
        "**The trust anchor** issues rules (`Issue`, `Resign` are environment events no principal can express). At "
        "archetype custody its key-holders are removable only with their own consent, so they sit at the gate (B14).",
        "**The evictability test** (ADR-0002 A2): a principal is anything evictable by an authority other than itself; "
        "whatever is not is at the gate. Resignation is not eviction.",
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

    def domain(x, name, sub, acc):
        cy = top + 30
        c.text(x + pad, cy + 22, name, 26, acc, bold=True)
        cy += 34
        cy += c.para(x + pad, cy, dom_w - 2 * pad, sub, 14.5, "muted") + 18
        return cy

    # -------- Build
    cy = domain(bx, "Build", "Authors the specifications, policy, floors, bundles, mechanism releases and Personas "
                "that Run is later judged against. **The Byzantine threat lives here** (the inversion).", "blue")
    mem_top = cy + 14
    inner = bx + pad + 22
    iw = dom_w - 2 * pad - 44
    ccy = mem_top + 30
    h1 = c.card(inner, ccy, iw, "Principals, one seat each, leased per round", [
        "`thinker` seats author; `observer` seats read, emit and, on the veto roster, deny; `grant` seats (human, "
        "`Mediated`) read, emit and vote.",
        "Per artifact, author and voters are disjoint; the author is recused by the `Vote` envelope.",
    ], accent="blue", size=14)
    ccy += h1 + 16
    h2 = c.table(inner, ccy, [("Build alphabet (ADR-0022), egress only", iw * 0.42, {"mono": True}),
                              ("Effect", iw * 0.58)], [
        ["Read(ref)", "Resolve a content-addressed object in the pinned corpus root"],
        ["Draft(target, content)", "Write into the round-scoped workspace"],
        ["Invoke(tool, inputs)", "Run a tool allowlisted by name and digest: **the whole attack surface**"],
        ["Emit(record)", "Append to the principal's round topic"],
        ["Submit(digest | ⊥)", "Offer the sealed workspace for promotion, or abstain"],
        ["Vote(verdict, digest, evidence, rulesEpoch)", "Cast a promotion vote"],
    ], size=13.5, accent="blue")
    ccy += h2 + 16
    h3 = c.card(inner, ccy, iw, "Detection couples the gate, not each admit", [
        "Build favours consistency over latency; detection only has to finish before the gate clears (ADR-0021, "
        "ADR-0039).",
        "A promotion stalls unless the author's cell Observer reported coverage to the seal.",
    ], accent="pink", size=14)
    ccy += h3 + 26
    c.region(bx + pad, mem_top, dom_w - 2 * pad, ccy - mem_top, "Contain · the membrane (B2)", "teal")
    bottom_b = ccy + 20

    # -------- Run
    cy = domain(rx, "Run", "Operates promoted artifacts against external state. Its budget is hard: the propagation "
                "window `W` is about a second, so Run is human-on-the-loop (HOTL).", "green")
    inner = rx + pad + 22
    ccy = mem_top + 30
    h1r = c.card(inner, ccy, iw, "Principals, one seat each, leased per round", [
        "A `thinker` seat holds all three variants; an `observer` seat `Consult` and `Report` (ADR-0043).",
        "There is no terminal variant: **a Run round ends when its lease ends**; a Run seat cannot abstain.",
    ], accent="green", size=14, h=h1)
    ccy += h1 + 16
    c.table(inner, ccy, [("Run alphabet (ADR-0040)", iw * 0.42, {"mono": True}), ("Class and envelope", iw * 0.58)], [
        ["Consult(ref)", "**Ingress, no effect**: `ref` resolves in the pinned Run root"],
        ["Actuate(tool, inputs)", "**Effect**: tool allowlisted by name and digest; its entry declares the channel it "
                                  "opens. A read of live state is an `Actuate`"],
        ["Report(record)", "**Effect**: the principal's own round topic, this epoch and round, unsealed"],
        {"cells": ["(no name shared)", "No variant name is common to Build and Run (ADR-0022 A2); only the carrier is "
                   "shared"], "accent": "grey"},
    ], size=13.5, accent="green")
    ccy += h2 + 16
    c.card(inner, ccy, iw, "Detection couples every effect-bearing admit", [
        "Floor entry R3: every `Actuate` or `Report` under a Thinker needs a live cell Observer; `Consult` is exempt "
        "(ADR-0039, ADR-0041 §2).",
        "A dead or slow Observer stops its own Thinker and nothing else.",
    ], accent="pink", size=14, h=h3)
    c.region(rx + pad, mem_top, dom_w - 2 * pad, ccy + h3 + 26 - mem_top, "Contain · the same component (B2)", "teal")

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
    ny = py + ph + 40
    nh = c.card(mx, ny, mid_w, "What does not cross", [
        "No variant name.",
        "No principal: a seat belongs to one domain.",
        "Nothing unpromoted: Run never loads an artifact Build did not promote.",
    ], accent="red", size=14, tint=False, dash="6 4")
    ey = ny + nh + 40
    eh = c.card(mx, ey, mid_w, "Effects reach the world only as admits", [
        "Effects: exactly {tool invocation, principal emission} (ADR-0015).",
        "Authority changes: exactly {promotion, anchor issuance}.",
        "Denials are not ordered, and they are recorded.",
    ], accent="teal", size=14)

    bottom = max(bottom_b, ccy + h3 + 46, ey + eh + 30)
    c.region(bx, top, dom_w, bottom - top, "Build(Contain)", "blue", dash=None, sw=2.6, tint=False, size=16)
    c.region(rx, top, dom_w, bottom - top, "Run(Contain)", "green", dash=None, sw=2.6, tint=False, size=16)

    y = bottom + 40
    w3 = (X1 - X0 - 2 * 24) / 3
    hh = c.card(X0, y, w3, "The inversion", [
        "Build agents write what Run is judged against. Moon & Varshney's empirical failure, silent abstention, a "
        "vacuously true predicate and green gates, is a Build failure.",
        "Every Build choice that looks expensive pays for that.",
    ], accent="red")
    c.card(X0 + w3 + 24, y, w3, "Contain claims two conjuncts", [
        "**Proved**: a property class over the action vocabulary and its envelope, by mechanical extraction.",
        "**Assumed, operationally discharged**: effect exclusivity, the principal reaches the world only through the "
        "alphabet (ADR-0015).",
    ], accent="teal", h=hh)
    c.card(X0 + 2 * (w3 + 24), y, w3, "Contained or Mediated (B6)", [
        "Safety theorems quantify over `Contained` principals; a `Mediated` one (shell, egress, git) gets attribution "
        "and authorization, not containment.",
        "`Contained` has **no members** at any rung today; the reference issues rung 0 only.",
    ], accent="amber", h=hh)
    return c
