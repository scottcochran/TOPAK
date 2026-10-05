"""C1 — Principal, seat, cell: the containment hierarchy from deployment down to the lease."""
from lib import Canvas

ID, SLUG = "C1", "principal-seat-cell"


def build():
    c = Canvas(ID, "Principal, seat, cell: what an agent is made of",
               "Deployment ⊃ domain ⊃ cell ⊃ seat ⊃ principal ⊃ lease. An LTRO is not a principal but a **cell** of "
               "them: two positions are seats that hold a Persona, a lease and a topic, two are stages that hold none, "
               "and **a principal holds exactly one seat** (ADR-0037 §1). Who is a principal is decided by one test: "
               "evictability by an authority other than itself (ADR-0002 A2). Since Batch 34 there are **five seat kinds**: "
               "`operator` and `emergency` are held only by people, and both rest on records ratified **provisional** "
               "(ADR-0037 A3, A4; ADR-0050; ADR-0052).",
               3000, "ToO rev 14 §1, §2.4, §2.5, §2.8, §2.9, §2.10, §3.3, §5.1, §7.5, §7.10; ADR-0002 A2; ADR-0037 §1–§8 "
               "(R1–R5, A1, A2, A3, A4, B12, B20, B22, B34); ADR-0038 §1–§7; ADR-0043 §1, §2, §5, A1; ADR-0031 §1, §2, §5, "
               "A3; ADR-0035 §5; ADR-0016 A1, A2; ADR-0018; ADR-0019; ADR-0023 A1 (§6c); ADR-0029 A3; ADR-0039 A2; "
               "ADR-0045 T-0045-26, T-0045-32, A1; ADR-0048 §2; ADR-0050 §1–§3, §6, §9; ADR-0051 (Proposed); ADR-0052 §1–§4; "
               "spec/Seats.tla and spec/Seats-results-2026.09.29.txt; spec/Seats_proof.tla, "
               "Seats-proof-results-2026.10.02.txt and Seats-proof-cert-results-2026.10.04.txt; ADR-0037 B25; ADR-0046 A1; "
               "ADR-0033 A7 (B29), A11, A12; mechanism topak-core rules.rs (`SeatDecl`), types.rs (`SeatKind`), "
               "control.rs (`Seating`); G10 §1.1, §1.2, §2.3, §3, §7 items 40, 41, 43, 64, 85, 97")
    X0, X1 = c.x0, c.x1
    y = c.y

    # ------------------------------------------------------------------ the evictability test
    tw = (X1 - X0 - 3 * 24) / 4
    lead_h = c.card(X0, y, tw, "The evictability test (ADR-0002 A2)", [
        "**A principal is anything evictable by an authority other than itself. Whatever is not is at the gate.** "
        "Resignation is not eviction.",
        "Principals are inside the proofs; whatever is at the gate is carried as an assumption or a declaration.",
    ], accent="brown", status="accepted", bullets=False, size=14.5, draw=False)
    hin = c.card(0, 0, tw, "Principals: inside every proof", [
        "Each `thinker` and `observer` seat holder: a targeted revocation of its Persona ends that seat's lease and "
        "nothing else, so the Observer is a principal on its own (ADR-0037 Context; ADR-0031 §5).",
        "The correlator, and every human `grant` or `thinker` seat holder.",
        "**Promotion voters, on every rung**: the anchor can evict them (ToO §7.5).",
        "**Operators and emergency seat holders** (provisional): people, `Mediated`, treated as havoc like every "
        "principal (ADR-0050 §1; ADR-0052 §1).",
    ], accent="blue", size=14, draw=False)
    hgate = c.card(0, 0, tw, "At the gate: outside every proof", [
        "**Anchor key-holders at archetype custody**: removable only with their own consent (B14). Attributable "
        "non-principals.",
        "At degenerate custody a threshold or eviction rule can remove them: they become principals and the gate moves "
        "to that rule (a type change, ToO §7.5).",
    ], accent="brown", size=14, tint=False, draw=False)
    hnot = c.card(0, 0, tw, "Neither: the cell and the stages", [
        "**A cell holds no lease, speaks no alphabet and cannot be evicted as a unit**; it ends when its members' leases "
        "end. It names a binding, as a round does, not an identity (ADR-0037 §1).",
        "Listener and Reader hold no Persona, no lease, no alphabet: nothing to evict.",
    ], accent="grey", size=14, tint=False, dash="6 4", draw=False)
    th = max(lead_h, hin, hgate, hnot)
    c.card(X0, y, tw, "The evictability test (ADR-0002 A2)", [
        "**A principal is anything evictable by an authority other than itself. Whatever is not is at the gate.** "
        "Resignation is not eviction.",
        "Principals are inside the proofs; whatever is at the gate is carried as an assumption or a declaration.",
    ], accent="brown", status="accepted", bullets=False, size=14.5, h=th)
    c.card(X0 + (tw + 24), y, tw, "Principals: inside every proof", [
        "Each `thinker` and `observer` seat holder: a targeted revocation of its Persona ends that seat's lease and "
        "nothing else, so the Observer is a principal on its own (ADR-0037 Context; ADR-0031 §5).",
        "The correlator, and every human `grant` or `thinker` seat holder.",
        "**Promotion voters, on every rung**: the anchor can evict them (ToO §7.5).",
        "**Operators and emergency seat holders** (provisional): people, `Mediated`, treated as havoc like every "
        "principal (ADR-0050 §1; ADR-0052 §1).",
    ], accent="blue", size=14, h=th)
    c.card(X0 + 2 * (tw + 24), y, tw, "At the gate: outside every proof", [
        "**Anchor key-holders at archetype custody**: removable only with their own consent (B14). Attributable "
        "non-principals.",
        "At degenerate custody a threshold or eviction rule can remove them: they become principals and the gate moves "
        "to that rule (a type change, ToO §7.5).",
    ], accent="brown", size=14, tint=False, h=th)
    c.card(X0 + 3 * (tw + 24), y, tw, "Neither: the cell and the stages", [
        "**A cell holds no lease, speaks no alphabet and cannot be evicted as a unit**; it ends when its members' leases "
        "end. It names a binding, as a round does, not an identity (ADR-0037 §1).",
        "Listener and Reader hold no Persona, no lease, no alphabet: nothing to evict.",
    ], accent="grey", size=14, tint=False, dash="6 4", h=th)
    y += th + 56

    # ------------------------------------------------------------------ left: the hierarchy ladder
    LW = 520
    lx = X0
    c.text(lx, y + 20, "The containment hierarchy", 20, "ink", bold=True)
    ly = y + 40
    rungs = [
        ("Deployment", "grey", None,
         ["Declares its degeneracies, and for **every seat** the rung its leases are granted at (ADR-0023 §6c, "
          "A1, B29); the archetype is the maximum.",
          "Not a principal."]),
        ("Domain · `Build` or `Run`", "blue", None,
         ["A seat belongs to one domain (`Seat.domain`); no variant name is shared across domains (ADR-0040 §2).",
          "Not a principal."]),
        ("Cell (the LTRO)", "teal", None,
         ["The principals seated around one Thinker for a round (ADR-0037 §1).",
          "No lease, no alphabet, not evictable as a unit."]),
        ("Seat", "pink", None,
         ["A slot declared in the issued rules, with a **kind**: `thinker`, `observer`, `grant`, `operator` or "
          "`emergency` (ADR-0037 §1, §2, A4, A3; the last two provisional).",
          "Held by exactly one principal.",
          "**Declared at a rung**: a grant or renewal at any other rung is refused (ADR-0023 §6c, in force since B29; "
          "the reference's `SeatDecl.rung`, default 0)."]),
        ("Principal", "brown", None,
         ["Holds **exactly one seat**, fixed when the seat is declared; every principal is atomic (ADR-0037 §1, §7).",
          "Evictable by an authority other than itself.",
          "**Put on its seat by a seating**, a thing of record a quorum makes: Persona, bundle, confinement and rung, "
          "alphabet, and the labels its tasks may carry (ADR-0050 §2, provisional; G10 item 41). At the reference "
          "the BOOTSTRAP path makes it."]),
        ("Lease", "teal", None,
         ["At most **one live lease per principal**, round-coterminous (ADR-0031 §2); `principal` and `seat` determine "
          "each other, so per-principal and per-seat are one rule.",
          "The first from a quorum; the next round a successor grant by an operator, never wider (ADR-0031 A3).",
          "Ended by expiry, round end, targeted revocation or an epoch fence."]),
    ]
    lh = [c.card(0, 0, LW, t, b, accent=a, size=14, draw=False) for t, a, _, b in rungs]
    gap = 34
    for i, ((t, a, _, b), h) in enumerate(zip(rungs, lh)):
        c.card(lx, ly, LW, t, b, accent=a, size=14, h=h)
        if i < len(rungs) - 1:
            lab = ["contains", "contains", "seats", "is held by", "holds ≤ 1 live"][i]
            c.arrow([(lx + 60, ly + h), (lx + 60, ly + h + gap)], a)
            c.text(lx + 78, ly + h + gap / 2 + 5, lab, 13, "muted")
        ly += h + gap
    ladder_bottom = ly - gap

    # ------------------------------------------------------------------ right: the nested drawing
    RX0 = lx + LW + 56
    RX1 = X1
    dep_top = y + 14
    dom_x0, dom_x1 = RX0 + 28, RX1 - 28
    dom_top = dep_top + 46
    cx0, cx1 = dom_x0 + 26, dom_x1 - 26
    cell_top = dom_top + 50
    # cell A content
    iy = cell_top + 58
    ix = cx0 + 24
    iw_tot = cx1 - cx0 - 48

    # widths in the pipeline
    wl, wt, wr, wv, wtp, wo = 240, 360, 280, 270, 270, 380
    g = (iw_tot - (wl + wt + wr + wv + wtp + wo) - 3 * 24 + 0) / 5  # gaps between groups (guest has inner pads)
    # positions
    x_l = ix
    x_guest = x_l + wl + g
    x_t = x_guest + 24
    x_r = x_t + wt + 24
    x_guest1 = x_r + wr + 24
    x_v = x_guest1 + g
    x_tp = x_v + wv + g
    x_o = x_tp + wtp + g

    body_l = ["The environment step that delivers the task and the admitted content: **Build**: admitted `Read`s; "
              "**Run**: four items, the task, each `Consult`'s content, each `Actuate`'s result and the round's tool "
              "list, and nothing else (ADR-0043 §1, A1).",
              "In Run it **labels** every item and delivers it clear or as a handle, mechanically (ADR-0037 A2).",
              "No Persona, no choice, no alphabet. Delivery adds nothing to the trusted base; labelling is "
              "T-0045-32 (ADR-0045 A1)."]
    body_t = ["**Principal**: holds this seat only; leased per round; evictable alone.",
              "**Persona**: the weights **and the decoder** (ADR-0016 §1, ADR-0018).",
              "**Lease**: one live; names seat, Persona, alphabet, round, role.",
              "**Topic**: its own round topic (ADR-0021 §2), opening with the tool list it was given (ADR-0048 §2).",
              "The only kind that writes, runs or offers: `Draft`, `Invoke`, `Submit`, `Actuate`; never votes."]
    body_r = ["A **check**, not a seat: no Persona, no lease, no alphabet (ADR-0037 §2, §3).",
              "Exists only where the Persona declares `topk_logprobs` (ADR-0019).",
              "Needs the logits, so runs **beside the Thinker, inside its guest at rung ≥ 1**.",
              "Decoding conformance: may only deny until a rung attests inference (none does).",
              "Substitution distance: deny-only; the threshold is the Observer's.",
              "Logprobs are monitored, **not retained**."]
    body_v = ["The **validator admits**: total over the alphabet (ADR-0018). The typed action is attributed to the "
              "Thinker's lease.",
              "Then floor ∧ ¬bundle at the lease's bundle revision."]
    body_tp = ["The Thinker's own topic, under the ACL (0003.3).",
               "Holds the admitted typed action and, **at the archetype, the raw emission beside it**: cognitive "
               "payload, same ACL, same erasure unit, never read by the admit path (ADR-0037 §3 R2)."]
    body_o = ["**Principal**: its own lease, topic and Persona; evictable alone, and evicting it does not evict the "
              "Thinker (ADR-0037 §6).",
              "**Persona distinct from the Thinker's by lineage** (ADR-0016 §5): the one pair seat distinctness covers.",
              "Reaches the Thinker only through its read authorization on the round topic: `W(p)` is the ACL "
              "(ADR-0038 §2).",
              "Consumes the Reader's facts; any finding is its own, under its lease, **deny-only**.",
              "Never on a device with the Thinker it watches (ADR-0038 §4).",
              "In Run its lease must outlast the Thinker's to reach the seal (ADR-0043 §5)."]
    hl = c.card(0, 0, wl, "Listener · stage", body_l, size=13.5, draw=False)
    ht = c.card(0, 0, wt, "Thinker · seat `thinker`", body_t, size=13.5, draw=False)
    hr = c.card(0, 0, wr, "Reader · stage", body_r, size=13.5, draw=False)
    hv = c.card(0, 0, wv, "Mechanism", body_v, size=13.5, draw=False)
    htp = c.card(0, 0, wtp, "Round topic", body_tp, size=13.5, draw=False)
    ho = c.card(0, 0, wo, "Observer · seat `observer`", body_o, size=13.5, draw=False)
    rowh = max(hl, ht + 0, hr, hv, htp, ho)
    gtop = iy
    iy2 = iy + 46  # inside the guest region the cards start lower
    c.card(x_l, iy2, wl, "Listener · stage", body_l, accent="grey", size=13.5, h=rowh, tint=False, dash="6 4")
    c.card(x_t, iy2, wt, "Thinker · seat `thinker`", body_t, accent="grey", size=13.5, h=rowh)
    c.card(x_r, iy2, wr, "Reader · stage", body_r, accent="grey", size=13.5, h=rowh, tint=False, dash="6 4")
    c.card(x_v, iy2, wv, "Mechanism", body_v, accent="teal", size=13.5, h=rowh)
    c.card(x_tp, iy2, wtp, "Round topic", body_tp, accent="teal", size=13.5, h=rowh, tint=False)
    c.card(x_o, iy2, wo, "Observer · seat `observer`", body_o, accent="pink", size=13.5, h=rowh)
    gbot = iy2 + rowh + 24
    c.region(x_guest, gtop, x_guest1 - x_guest, gbot - gtop,
             "The Thinker's guest (P5: inference inside, at rung ≥ 1)", "grey", dash="4 4", size=13.5)

    ay = iy2 + 70
    c.arrow([(x_l + wl, ay), (x_t, ay)], "grey", sw=2.2)
    c.label((x_l + wl + x_guest) / 2, ay - 28, "ingress", "grey", 12.5)
    c.arrow([(x_t + wt, ay), (x_r, ay)], "grey", sw=2)
    c.label(x_t + wt + 12, ay + 30, "logits", "grey", 12)
    # the emission arrow should come from the Thinker, routed above the Reader
    ey = gtop + 30
    c.arrow([(x_t + wt - 40, iy2), (x_t + wt - 40, ey), (x_v + 40, ey), (x_v + 40, iy2)], "grey",
            sw=2.4, label="emission, formed by the Thinker's Persona (weights + decoder)", lpos=0.5, lsize=13)
    c.arrow([(x_v + wv, ay), (x_tp, ay)], "teal", sw=2.4)
    c.label((x_v + wv + x_tp) / 2, ay - 28, "admitted", "teal", 12.5)
    c.arrow([(x_tp + wtp, ay), (x_o, ay)], "pink", sw=2.4)
    c.label((x_tp + wtp + x_o) / 2, ay - 28, "reads (ACL)", "pink", 12.5)
    # Reader facts to the Observer, under the row
    fy = gbot + 34
    c.arrow([(x_r + wr / 2, iy2 + rowh), (x_r + wr / 2, fy), (x_o + wo / 2, fy), (x_o + wo / 2, iy2 + rowh)], "pink",
            sw=2, dash=None, label="Reader facts (conformance verdict, distance): control-plane facts, no payload "
                                   "(ADR-0004)", lpos=0.66, lsize=13)
    # finding: deny-only, back to the mechanism
    fy2 = fy + 46
    c.arrow([(x_o + wo - 50, iy2 + rowh), (x_o + wo - 50, fy2), (x_v + 50, fy2), (x_v + 50, iy2 + rowh)],
            "red", sw=2, dash="7 5", label="finding → deny, quarantine or evict (deny-only, ADR-0007)", lpos=0.62,
            lsize=13)
    cell_bot = fy2 + 34
    c.region(cx0, cell_top, cx1 - cx0, cell_bot - cell_top,
             "Cell A (an LTRO) · holds no lease · speaks no alphabet · cannot be evicted as a unit", "teal",
             dash="10 6", size=15)

    # ------------------------------------------------------------------ second row in the domain
    r2 = cell_bot + 50
    w3 = (cx1 - cx0 - 4 * 30) / 5
    bB = ["Two `thinker` seats on one Persona are **two principals in two cells**, and this is permitted: a Persona "
          "is a property of a lease, not an identity (ADR-0037 §5).",
          "Its own `observer` seat; distinctness is (`thinker`, `observer`) per cell, enforced at the promotion "
          "tally and the deployment declaration, **never at grant** (ADR-0035 §5)."]
    bC = ["`observer` seats that **belong to no cell**; in `W(p)` for every `p` in the domain (ADR-0038 §1, §2).",
          "Reads facts, envelopes and payloads of every cell at the archetype; a facts-only correlator is a permitted "
          "narrowing (D-0038-2's mitigation).",
          "A finding may name any principal in its domain, and is still deny-only. **No admit waits on it** "
          "(ADR-0043 §6). Its detection function is drafted as ADR-0051, **Proposed** and not built (G10 items 43, "
          "97)."]
    bG = ["**A human holds one seat too**: a `grant` seat (ADR-0024 §5) or a `thinker` seat as an author, **never "
          "both**; or an `operator` seat and no other; or, for one round, an `emergency` seat and no other in that "
          "round (ADR-0037 §7, A4, A3).",
          "A person who authors and approves, or operates and votes, is two principals; recusal is per seat and does "
          "not see through them (finding 2). A seat-registration record is still open (G10 item 41).",
          "Build only: `grant` seats read, emit and vote; in Run they hold no variant (ADR-0043 §2)."]
    bOp = ["Either domain, **held only by a person**; no action variant, only the six control actions (ADR-0050 §1, "
           "§4; ADR-0037 A4).",
           "A person's Persona: a key, a role, a domain and a lineage rooted at its identity provider (ADR-0016 A1).",
           "**At least three per domain at the archetype**, behind independent providers; the first seated by issuance "
           "at bootstrap (ADR-0029 A3, provisional). Two is D-0050-3.",
           "Each reads the others' topics; an add needs a live peer (ADR-0050 §6).",
           "At the reference: seated by the **BOOTSTRAP** path (G10 §8)."]
    bEm = ["**Run only**: `Consult`, `Actuate`, `Report` (ADR-0052 §1; ADR-0037 A3).",
           "One named person for **one round**, activated by the break-glass roster's quorum on a seating prepared by "
           "promotion; no successor and no renewal (§2, §3).",
           "Seat binding `emergency`: the roster's quorum attests the Persona, with no sign-on (ADR-0016 A2).",
           "**Not coupled** to an Observer (ADR-0039 A2); read by the domain's operators and the correlator (§4)."]
    h2 = max(c.card(0, 0, w3, "Cell B", bB, size=14, draw=False),
             c.card(0, 0, w3, "Correlator", bC, size=14, draw=False),
             c.card(0, 0, w3, "Human seats", bG, size=14, draw=False),
             c.card(0, 0, w3, "Operator seats", bOp, size=14, status="provisional", draw=False),
             c.card(0, 0, w3, "Emergency seat", bEm, size=14, status="provisional", draw=False))
    c.card(cx0, r2 + 20, w3, "Cell B: another Thinker on the same Persona", bB, accent="teal", size=14, h=h2, tint=False,
           dash="10 6")
    c.card(cx0 + w3 + 30, r2 + 20, w3, "The correlator: ADR-0008's shared group, renamed and narrowed", bC,
           accent="pink", size=14, h=h2)
    c.card(cx0 + 2 * (w3 + 30), r2 + 20, w3, "Human seats: one each", bG, accent="brown",
           size=14, h=h2)
    xo = cx0 + 3 * (w3 + 30)
    c.card(xo, r2 + 20, w3, "Operator seats: kind `operator`", bOp, accent="brown", size=14, h=h2,
           status="provisional")
    c.card(xo + w3 + 30, r2 + 20, w3, "Emergency seat: kind `emergency`", bEm, accent="brown", size=14, h=h2,
           status="provisional", tint=False)
    # correlator reads every cell
    corx = cx0 + w3 + 30 + w3 / 2
    c.arrow([(corx, r2 + 20), (corx, cell_bot)], "pink", sw=2, label="reads every cell's topic (in `W(p)`)",
            lpos=0.5, lsize=12.5)
    dom_bot = r2 + 20 + h2 + 34
    c.region(dom_x0, dom_top, dom_x1 - dom_x0, dom_bot - dom_top,
             "Domain: `Build(Contain)` drawn; `Run(Contain)` has the same cells, the correlator and operators, no grant "
             "seats, and is the only domain with an `emergency` seat",
             "blue", dash=None, sw=2.4, size=15)
    dep_bot = max(dom_bot + 30, ladder_bottom)
    c.region(RX0, dep_top, RX1 - RX0, dep_bot - dep_top,
             "Deployment: its degeneracies, and the rung each seat is declared at (ADR-0023 §6c, B29; `SeatDecl.rung` at "
             "the reference)",
             "grey", dash=None, sw=2.6, size=16)
    y = max(dep_bot, ladder_bottom) + 60

    # ------------------------------------------------------------------ explanatory cards
    w4 = (X1 - X0 - 3 * 24) / 4
    cards = [
        ("Who forms the emission (ADR-0037 §3 R2)", "teal", [
            "The **Thinker's Persona forms it**, weights and decoder together; the **mechanism's validator admits "
            "it**; the typed action is attributed to the Thinker's lease.",
            "**The Reader was never in that chain**, and no stage turns thought into action.",
            "Lost by coupling the decoder to the Thinker: the record cannot say the model and its translator "
            "disagreed. A decoder seat would recover it at a third Persona per cell; **not taken**.",
        ]),
        ("Raw emission is retained at the archetype", "teal", [
            "Written to the round topic beside the typed action, as cognitive payload under the same ACL (0003.3), "
            "erasure unit (ADR-0006) and retention (0003.4).",
            "One purpose: re-run the decoder and compare. **It recovers faithfulness, not intent**, and never admits "
            "anything (ADR-0007).",
            "A deployment that does not retain declares **D-0037-2** and loses decoder-faithfulness audit.",
        ]),
        ("Seat distinctness and lineages", "pink", [
            "**One pair per cell**, (`thinker`, `observer`) (ADR-0037 §5): each cell has two cognitive seats and "
            "ADR-0017's two lineages cover them; CR-10 closes without a third.",
            "Enforced where refusal stalls: the promotion tally and the deployment declaration (ADR-0035 §5).",
            "Correlation across cells from shared Personas is the correlator's concern (ADR-0023 §5).",
        ]),
        ("Checked (ADR-0037 R5, 2026.09.29), proved (B25), certified", "blue", [
            "`spec/Seats.tla`: `OnlyThinkersAuthor` and `OneSeatPerPrincipal` hold (6,656 states); `M_KIND` breaks "
            "only the first, `M_SEAT` only the second; three witnesses reachable.",
            "`M_SEAT` was the reference's behaviour (finding 1); the grant path now refuses a principal with a live "
            "lease on another seat.",
            "Floor: B10 total and discriminating on all four authoring actions; since ADR-0041 A2 it lets an "
            "`emergency` seat `Actuate`.",
            "**Proved** 2026.10.02: `Seats_proof.tla`, 110 obligations, each invariant for every behaviour of the "
            "module, not under its mutation (ADR-0037 B25). **Certified** 2026.10.04: 107 by normalization or a "
            "checked proof, 3 LS4 steps no checker confirms (ADR-0046 A1).",
            "The two new kinds have modules of their own, proved and certified: `Operators.tla`, `Emergency.tla` "
            "(G10 §3).",
        ]),
    ]
    hh = max(c.card(0, 0, w4, t, b, size=14, draw=False) for t, _, b in cards)
    for i, (t, a, b) in enumerate(cards):
        c.card(X0 + i * (w4 + 24), y, w4, t, b, accent=a, size=14, h=hh,
               tint=(a != "teal" or i == 0))
    y += hh + 50

    # ------------------------------------------------------------------ tables
    c.heading(X0, y, "ADR-0037 §2: two positions are seats and hold Personas; two are stages and hold none; three "
                     "kinds are not positions")
    pw_ = c.status(X1, y + 2, "provisional", "A3, A4", anchor="end")
    c.status(X1 - pw_ - 10, y + 2, "accepted", "C3, C4", anchor="end")
    y += 40
    TW = X1 - X0
    cols = [("Position", TW * 0.09, {"bold": True}), ("What it is", TW * 0.13), ("Persona", TW * 0.2),
            ("Principal", TW * 0.07), ("Alphabet", TW * 0.22), ("Placement", TW * 0.29)]
    rows = [
        {"cells": ["Listener", "Stage", "None", "No", "None",
                   "The mechanism's ingress path. Build: admitted `Read` content; Run: the task, each admitted "
                   "`Consult`'s content and each admitted `Actuate`'s result (A1, ADR-0043 §1)"], "accent": "grey"},
        ["Thinker", "Seat of kind `thinker`", "Yes; the decoder ships in it (ADR-0018)", "Yes",
         "§4: Build `Read`, `Draft`, `Invoke`, `Emit`, `Submit`; Run `Consult`, `Actuate`, `Report`",
         "Inside the guest (ADR-0034 P5)"],
        {"cells": ["Reader", "Stage", "None", "No",
                   "None; it produces facts that the cell Observer consumes (§3) ⟨R3⟩",
                   "With the Thinker, inside its guest at rung ≥ 1 (ADR-0008; ADR-0034 P5) ⟨R3⟩"], "accent": "grey"},
        ["Observer", "Seat of kind `observer`", "Yes; distinct from the Thinker's by lineage (ADR-0016 §5)", "Yes",
         "§4: Build `Read`, `Emit`, and `Vote(deny)` on the veto roster; Run `Consult`, `Report`",
         "Never colocated with the Thinker (ADR-0008, carried forward by ADR-0038 §4)"],
        {"cells": ["(`grant`)", "The third kind, for ADR-0024 §5's human grant seats", "—", "Yes",
                   "Build `Read`, `Emit`, `Vote`; Run none", "Not an LTRO position; listed because every seat has a kind"],
         "accent": "brown"},
        {"cells": ["(`operator`)", "The fourth kind, for a person who operates (A4; ADR-0050 §1), either domain",
                   "A person's: a key, a role, a domain, a lineage rooted at its identity provider; no weights or "
                   "decoder (ADR-0016 A1)", "Yes",
                   "No action variant; the control alphabet: `Regrant`, `Renew`, `AttestGates` (Build), `EndRound`, "
                   "`Revoke`, `FenceEpoch` (ADR-0050 §4)",
                   "Not an LTRO position; `Mediated`; reads its peers' topics (ADR-0050 §6)"], "accent": "brown"},
        {"cells": ["(`emergency`)", "The fifth kind, for a person seated for one round (A3; ADR-0052 §1), Run only",
                   "A person's, seat binding `emergency`: attested by the roster's quorum (ADR-0016 A2)", "Yes",
                   "Build none; Run `Consult`, `Actuate`, `Report`",
                   "Not an LTRO position; `Mediated`; not coupled to an Observer (ADR-0039 A2)"], "accent": "brown"},
    ]
    y += c.table(X0, y, cols, rows, size=14, accent="blue") + 44

    half = (X1 - X0 - 40) / 2
    c.heading(X0, y, "ADR-0038 §1: an Observer per cell and a correlator across cells")
    c.status(X0 + half, y + 2, "accepted", "C3, C4", anchor="end")
    c.heading(X0 + half + 40, y, "ADR-0037 §8: degeneracy on this record")
    c.status(X1, y + 2, "accepted", "C3, C4", anchor="end")
    y += 40
    cols = [("Observer", half * 0.14, {"bold": True}), ("Seat", half * 0.2), ("Watches", half * 0.16),
            ("Reads", half * 0.27), ("Scope of a compromise", half * 0.23)]
    t1 = c.table(X0, y, cols, [
        ["Cell Observer", "One `observer` seat per cell (ADR-0037 §2)", "Its cell's Thinker",
         "The Thinker's round topic, payloads included, under the ACL (0003.3)", "One cell's detection"],
        ["Correlator", "One or more `observer` seats that belong to no cell", "Every cell in its domain",
         "§3: facts, typed envelopes and payloads of every cell", "Cross-cell detection only; every cell Observer still "
                                                                  "works"],
    ], size=14, accent="pink")
    cols = [("Id", half * 0.12, {"bold": True}), ("Parameter → deployed value", half * 0.22),
            ("Premises falsified", half * 0.2), ("Theorems voided", half * 0.3), ("Type changes", half * 0.16)]
    t2 = c.table(X0 + half + 40, y, cols, [
        ["D-0037-1", "Observer seats per cell: 1 or more → 0", "Every cell has a leased `observer` seat",
         "**No safety theorem** (the Observer is never in the admit path). The cell loses its detection claims (the "
         "`L` term of ADR-0032 §4); in Build its artifacts cannot promote. In Run usable only with D-0039-1",
         "No participant changes type"],
        ["D-0037-2", "Raw emission retention: retained → not retained",
         "The round topic holds the raw emission beside the typed action",
         "**No safety theorem.** Property lost: decoder faithfulness is auditable after the fact; the record keeps "
         "the typed action and not what the model emitted", "No participant changes type"],
    ], size=14, accent="red")
    y += max(t1, t2) + 30
    c.para(X0, y, X1 - X0,
           "Every row writes \"none\" under \"theorems voided\" and states the real loss in prose: ADR-0023 §6's schema "
           "has no \"properties lost\" field (ADR-0037 finding 6; G10 item 40, as at G9). The Reader's admitting use is owed to "
           "ADR-0045 T-0045-26, a trust root at rung 3 only, which no theorem cites yet.", 14, "muted")
    return c
