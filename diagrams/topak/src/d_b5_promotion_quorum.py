"""B5 — Promotion is a quorum grant, run as a round, and a promotion seats (ADR-0024 with A2 and A3)."""
from lib import Canvas, text_width

ID, SLUG = "B5", "promotion-quorum"


def build():
    c = Canvas(ID, "Promotion is a quorum grant, run as a round, and a promotion seats",
               "ADR-0024 replaces the single promotion signing key, the last privileged human grant. Everything that "
               "crosses from `Build` to `Run` (boundary B1) is promoted by a round keyed by artifact digest: gates "
               "enable voting, grant seats vote, veto seats can only deny, the author is recused, and the tally reads "
               "its quorum from the issued rules. Since Batch 34 **a promotion seats** (ADR-0024 A3, provisional with "
               "ADR-0050): when the tally on a seating completes, the mechanism grants the principal's first lease. "
               "That is not built at the reference, where an unsigned BOOTSTRAP socket seats instead.",
               3200, "ADR-0024 §1–§9, enabling condition, Degeneracies, Consequences, Open obligations, A1, A2 "
               "(A2.1–A2.4), A3, History B2, B34; ADR-0026 §2 R1, R2, R5, R9, §7; ADR-0022 §1 `Vote` row, §7; "
               "ADR-0025 §1 (a), (f), A3; ADR-0029 §4, §5 (bootstrap modules, ceremony), A3, A4; ADR-0030 A3; "
               "ADR-0031 §4; ADR-0035 §4, §5 (Proposed); ADR-0037 §7, A4; ADR-0038 §6; ADR-0039 §3; ADR-0032 §2; "
               "ADR-0041 A3 (`C1`, `C2`, `C3`, `C5`); ADR-0050 §1, §2, §4, §5, §6, §10, History R6, R9, R10; ADR-0052 §2; "
               "ToO rev 14 §7.1, §7.7, §7.10, §9; G10 §1, §1.2, §4, §6, §7 items 2, 41, 57, 87, 88, §8; "
               "mechanism/GAPS-AND-ASSUMPTIONS.md I47, G8, G18; mechanism/crates/topak-core/src/control.rs, "
               "state.rs (`not_a_first_seating`)")
    X0, X1 = c.x0, c.x1
    W = X1 - X0
    y = c.y + 18

    # ------------------------------------------------------------------ the anchor band above the round
    ah = c.card(X0, y, W, "Issued rules at rules epoch e (anchor issuance, ADR-0025 §1 (a))", [
        "The promotion roster and its parameters: `grantSeats`, `vetoSeats`, `quorum` (`\"all\"` or a threshold k) "
        "and `minGrant`, bounded by the rules floor (R1 unanimity, R2 `minGrant ≥ 2`, R5 no anchor key on the "
        "roster, R9 `quorum = \"all\" ∨ quorum ≥ 2`). **This quorum cannot change its own rules** (§2).",
    ], accent="brown", bullets=False, size=14.5)
    abot = y + ah
    y = abot + 90

    # ------------------------------------------------------------------ the round, left to right
    gapx = 80
    wa, wg, ws, wt = 330, 380, 860, 760
    wo = W - wa - wg - ws - wt - 4 * gapx
    xa = X0
    xg = xa + wa + gapx
    xs = xg + wg + gapx
    xt = xs + ws + gapx
    xo = xt + wt + gapx
    top = y

    tally_body = [
        "`GatesPass(a) ∧ Refines(a.bundle, PolicyFloor)`",
        "`G = grantSeats \\ {Author(a)}`: recusal is a **mechanism constant**, not an issued value (§6)",
        "`|G| ≥ minGrant`, else **denied** (R2)",
        "`quorum = \"all\"`: every counted grant seat granted (archetype, R1); otherwise `|Granted| ≥ k` with k ≥ 2 "
        "(R9)",
        "A vote counts only as the triple `⟨grant, digest, evidence, rulesEpoch⟩`; only recorded votes count",
        "No veto seat has cast `⟨deny, digest, evidence, rulesEpoch⟩`",
        "**A2.2** a veto seat with a Persona independent of the author's (ADR-0035 §5) was leased for the round, "
        "else **stalls**",
        "**A2.3** the author's cell Observer reported coverage to the seal of the author's round (ADR-0039 §3), "
        "else **stalls**",
        "The veto check is any-of over the veto roster: one deny suffices, and adding veto seats never lowers "
        "safety (ADR-0038 §5)",
        "A rules change needs an anchor issuance plus a promotion (ADR-0026 §4): **this quorum cannot change its "
        "own rules**",
    ]
    tsub = "ADR-0024 enabling condition with A2; every conjunct must hold"
    th = c.card(0, 0, wt, "Tally: `PromotionEnabled(a)`", tally_body, draw=False, sub=tsub)
    sw = ws - 48
    G_T, G_B = ("Grant seats · human, `Mediated`, named organizational role", [
        "Alphabet `Vote(grant)`, `Vote(deny)`.",
        "Under `\"all\"`, **any grant-seat deny or abstention is a denial**; under unanimity every seat is a veto.",
        "Voters are principals on every custody rung, because the anchor can evict them.",
        "A person who operates and also votes holds two seats and is two principals (ADR-0037 §7, A4).",
    ])
    V_T, V_B = ("Veto seats · every cell Observer and every correlator in Build", [
        "Alphabet `Vote(deny)` only: a seat whose alphabet lacks `grant`. Never an agent in the author's fault "
        "domain. A2.1 replaced \"the independent Observer replicated group (ADR-0008)\".",
        "**A veto-seat deny is a denial; veto-seat silence is not.** A \"no finding\" attestation would make "
        "semantic judgment an enabling condition (ADR-0007).",
    ])
    R_T, R_B = ("Author: recused", [
        "Removed from the counted seats, and the ADR-0022 `Vote` envelope refuses its vote: no issuance can admit "
        "one.",
    ])
    h1 = c.card(0, 0, sw, G_T, G_B, draw=False)
    h2 = c.card(0, 0, sw, V_T, V_B, draw=False)
    h3 = c.card(0, 0, sw, R_T, R_B, draw=False)
    seats_total = 20 + h1 + 18 + h2 + 18 + h3 + 20
    OUT = [("Promoted", ["One signed artifact crosses B1 into Run.",
                         "No strict subset of grant seats can promote (at `\"all\"`)."], "green"),
           ("Denied", ["A grant-seat deny or abstention; a veto-seat deny; recusal leaves fewer seats than "
                       "`minGrant`.",
                       "**A timeout is never a grant**: a mechanism constant (ex-R4)."], "red"),
           ("Stalled", ["No independent veto seat leased (A2.2), or no coverage to the seal (A2.3): an absent "
                        "Observer **stalls** promotion instead of vetoing nothing."], "amber")]
    ohs = [c.card(0, 0, wo, t, b, draw=False, size=14) for t, b, _ in OUT]
    seat_h = max(th, seats_total, sum(ohs) + 2 * 22)
    oh = (seat_h - 2 * 22) / 3
    # author
    c.card(xa, top, wa, "Author · `thinker` seat", [
        "Drafts the artifact in its round workspace.",
        "Ends with `Submit(digest)`, or abstains with `Submit` of ⊥ (ADR-0022 §1).",
        "Holds **no seat** for its own artifact.",
    ], accent="blue", h=260, size=14)
    # gates
    c.card(xg, top, wg, "Gates enable voting; they do not vote", [
        "ADR-0007 totality, non-vacuity and discrimination gates.",
        "`bundle ⊑ floor` (ADR-0010; listed in §4). By ADR-0030 composition it holds for every bundle, so ToO §7.1 "
        "says it no longer needs checking here.",
        "`Vote` is **enabled only after** the gates pass.",
        "**Recorded by an operator's signed** `AttestGates` (A3; ADR-0050 §4; floor `C3`): who asserted it is known, "
        "whether it is true is not (G10 item 57).",
    ], accent="teal", h=260, size=14)
    # seats region
    c.region(xs, top - 20, ws, seat_h + 40, "The round's seats (ADR-0024 §5, A2.1)", "blue", dash="10 6")
    sx = xs + 24
    sy = top + 20
    c.card(sx, sy, sw, G_T, G_B, accent="brown")
    sy += h1 + 18
    c.card(sx, sy, sw, V_T, V_B, accent="pink")
    sy += h2 + 18
    c.card(sx, sy, sw, R_T, R_B, accent="red", tint=False, dash="6 4", h=top + seat_h - sy)
    # tally
    c.card(xt, top, wt, "Tally: `PromotionEnabled(a)`", tally_body, accent="teal", h=seat_h, sub=tsub)
    # outcomes
    oy = top
    for i, (t, b, acc) in enumerate(OUT):
        c.card(xo, oy + i * (oh + 22), wo, t, b, accent=acc, h=oh, size=14)

    # flow arrows
    my = top + 110
    c.arrow([(xa + wa, my), (xg, my)], "blue", sw=2.4, label="Submit(digest)", loff=(0, -20))
    c.arrow([(xg + wg, my), (xs, my)], "teal", sw=2.4, label="Vote enabled", loff=(0, -20))
    c.arrow([(xs + ws, my), (xt, my)], "blue", sw=2.4, label="votes", loff=(0, -20))
    for i, acc in enumerate(["green", "red", "amber"]):
        yy = oy + i * (oh + 22) + oh / 2
        c.arrow([(xt + wt, yy), (xo, yy)], acc, sw=2.2, dash=None if acc == "green" else "7 5")
    # rules into seats and tally
    c.arrow([(xs + ws / 2, abot), (xs + ws / 2, top - 20)], "brown", sw=2.2, label="roster at epoch e",
            lpos=0.5)
    c.arrow([(xt + wt / 2 - 120, abot), (xt + wt / 2 - 120, top)], "brown", sw=2.2, label="quorum, minGrant",
            lpos=0.5)
    c.arrow([(xt + wt / 2 + 160, abot), (xt + wt / 2 + 160, top)], "red", sw=2.2, dash="7 5",
            label="new epoch voids in-flight votes", lpos=0.5)
    y = top + seat_h + 70

    # ------------------------------------------------------------------ binding and fencing strip
    w3 = (W - 2 * 28) / 3
    b1 = ["A vote binds to **(artifact digest, gate-evidence digest, rules epoch)** (§3).",
          "Any rules-epoch change voids in-flight votes: fencing, the same shape as leases. A vote on other evidence "
          "or an older epoch is not in `Granted`.",
          "`Vote(verdict, digest, evidence, rulesEpoch)`: seat held at `rulesEpoch`; `grant` only from a grant seat; "
          "terminal for the voter's round (ADR-0022 §1)."]
    b2 = ["**The authoritative vote is the admit decision in the consensus log** (ADR-0015), retained as ADR-0028 F3.",
          "A voter's round-topic emission carries the vote with a hash-and-pointer to its commentary in the "
          "ADR-0004 store; commentary is payload and erasable, the vote is not.",
          "So the round needs no effect-stream scheme: §7 does not rest on ADR-0021.",
          "At the reference there is **no promotion entry and no** `promote` **op**: the admit that completes the tally is "
          "the event, and `promoted_at` in state is derived from it. F3 retains the vote; what the archive says of the "
          "promotion is open (inventory finding 29)."]
    b3 = ["**Promotion is a grant** (§1): operational **bundles**, **mechanism releases** (including policy-floor "
          "and rules-floor changes) and **Personas**; since A3, **seatings** (below), and a confinement profile, "
          "which the mechanism registers when the tally completes (ADR-0050 §4).",
          "**Runtime subtraction is not promotion** (§9): e-stop, lease expiry, revocation and `bundle(deny=all)` "
          "need no quorum, are attributed, and are ordered when they change replicated state. An operator's stop is "
          "a signed `EndRound`, `Revoke` or `FenceEpoch` (ADR-0050 §4).",
          "Fast path for strictly subtractive bundles: **deferred**."]
    bh = max(c.card(0, 0, w3, "Votes bind to a triple", b1, draw=False),
             c.card(0, 0, w3, "Votes are non-erasable (§8)", b2, draw=False),
             c.card(0, 0, w3, "What promotes, and what does not", b3, draw=False))
    c.card(X0, y, w3, "Votes bind to a triple", b1, accent="blue", h=bh)
    c.card(X0 + w3 + 28, y, w3, "Votes are non-erasable (§8)", b2, accent="teal", h=bh)
    c.card(X0 + 2 * (w3 + 28), y, w3, "What promotes, and what does not", b3, accent="green", h=bh)
    y += bh + 60

    # ------------------------------------------------------------------ a promotion seats (A3)
    t = "A promotion seats: the seating, the first lease, and who continues it (ADR-0024 A3; ADR-0050 §2)"
    c.text(X0, y + 22, t, 22, "blue", bold=True)
    c.status(X0 + text_width(t, 22, True) + 20, y + 4, "provisional", "with ADR-0050 · bootstrap set")
    y += 50
    y += c.para(X0, y, W, "**\"Promotion is a grant\" taken literally** (ToO §7.1). A principal's first lease is "
                "granted by the mechanism when a quorum completes, **never by an operator**; round by round, one "
                "operator continues what the quorum granted. So the quorum acts once per seating (ADR-0050 §2).",
                15) + 22
    gap4 = 80
    w4f = (W - 3 * gap4) / 4
    FLOW = [
        ("1 · A seating is promoted", "blue", [
            "An artifact naming **the principal, its seat, its Persona, its bundle revision, its confinement profile "
            "and rung, its alphabet, and the labels a task for it may carry** (A3; ADR-0050 §2).",
            "Promoted like any other artifact, by the round above. An operator's Persona is promoted so, and an "
            "operator is seated so.",
            "Its schema, and whether it is one artifact or rides the Persona's and the bundle's promotions, is open "
            "(ADR-0050 Open obligations).",
        ]),
        ("2 · The tally completes", "teal", [
            "`PromotionEnabled` as above: **§2's quorum rule and §5's seat classes are unchanged** by A3.",
            "The gates were recorded by an operator's signed `AttestGates`.",
            "A2.2 and A2.3 still apply: a veto seat independent of the author leased for the round, and coverage to "
            "the seal, or the round stalls.",
            "A confinement profile promoted the same way is registered by the mechanism when the tally completes; it "
            "is no longer an operator's request (ADR-0050 §4).",
        ]),
        ("3 · The mechanism grants the first lease", "teal", [
            "**At a fresh fence, with no request from anyone** (ADR-0050 §2).",
            "First leases are not actions and have **no floor entry**: the mechanism grants one when a quorum "
            "completes (ADR-0041 A3).",
            "The seating carries the round's task, by digest with its label on the log; the label must be one the "
            "seating allows (ADR-0050 §5).",
        ]),
        ("4 · An operator continues it", "brown", [
            "**Successor grant** (`Regrant`): the next round, every field the last lease's or narrower, only `round` "
            "advancing. **Renewal** (`Renew`) keeps the round (ADR-0031 §4).",
            "Needs a live lease **and a live peer** in the domain (`C1`, `C2`, `C5`); never itself (`C6`); the "
            "task's label in the seating's bounds (`C8`).",
            "**Monotone**: it can keep a quorum's grant going and narrow it, and cannot widen it.",
        ]),
    ]
    fh = max(c.card(0, 0, w4f, tt, bb, draw=False, size=14) for tt, _, bb in FLOW)
    fy = y
    for i, (tt, acc, bb) in enumerate(FLOW):
        fx = X0 + i * (w4f + gap4)
        c.card(fx, fy, w4f, tt, bb, accent=acc, h=fh, size=14)
        if i:
            c.arrow([(fx - gap4, fy + 60), (fx, fy + 60)], "blue" if i < 3 else "brown", sw=2.4)
    # anything wider loops back to a new seating
    ly_ = fy + fh + 44
    x4 = X0 + 3 * (w4f + gap4) + w4f / 2
    x1_ = X0 + w4f / 2
    c.arrow([(x4, fy + fh), (x4, ly_), (x1_, ly_), (x1_, fy + fh)], "red", dash="7 5", sw=2,
            label="Anything wider is a first lease: a different Persona, bundle, profile or seat, or a new variant "
                  "in the alphabet needs a new seating and a quorum (ADR-0050 §2)", lpos=0.5)
    y = ly_ + 50

    # the ADR-0050 §2 table, and the bootstrap, the emergency case and the reference
    tw2 = 1180
    c.text(X0, y + 18, "Who grants a first lease (ADR-0050 §2, the record's table)", 18, "blue", bold=True)
    th2 = c.table(X0, y + 34, [("First lease of", 430, {"bold": True}), ("Comes from", 330), ("Why", tw2 - 760)], [
        ["A seat on a roster the rules name (grant, veto, anchor) at genesis, and the first operators",
         "An anchor issuance (ADR-0025; ADR-0029 §5)", "Something must be seated before anything can be promoted"],
        ["Every other principal, operators included", "A promotion (ADR-0024)", "\"Promotion is a grant\""],
    ], size=14, accent="blue")
    c.para(X0, y + 34 + th2 + 12, tw2, "An **emergency seating** is one of these too: prepared by promotion, and "
           "activated for one round by the break-glass roster's quorum and **not by a tally**; an operator's "
           "`Regrant` or `Renew` naming an emergency seat is refused (ADR-0050 §2 R6; ADR-0052 §2). Drawn in D5.",
           14, "ink")
    rx = X0 + tw2 + 40
    w3b = (X1 - rx - 2 * 28) / 3
    C3 = [
        ("The first operators, at bootstrap", "blue", "provisional", "ADR-0029 A3", [
            "The ceremony's first step **seats the first operators by issuance, at least three in each domain** at "
            "the archetype, each with a Persona and a key, with the identity providers' keys in the issued rules "
            "(ADR-0029 A3; ADR-0025 A3 (a), (f)).",
            "**Until an operator is seated nothing can be regranted, and a promotion needs Build leases.**",
            "Whether a bootstrap module is owed for the genesis seating is not decided (ADR-0029 A3).",
        ]),
        ("At the reference: a BOOTSTRAP socket seats", "red", "notbuilt", "first lease from a quorum", [
            "**A promoted seating that grants a first lease, and the first operators seated by an anchor issuance, "
            "are not built** (ADR-0050 §10, R10; G10 §1.2, §8).",
            "The unsigned operator socket is kept as a marked **BOOTSTRAP** path that seats and does nothing else: "
            "**whoever reaches it can seat** (D-0050-1 for that one step; I47 (a)).",
            "It refuses a grant that keeps a seat's seated binding while two operators of its domain are live: that "
            "is a successor, and theirs to make (`not_a_first_seating`).",
            "Every successor grant, renewal, gate attestation and stop is a signed request decided by `C1` to `C9` "
            "(ADR-0050 R9).",
        ]),
        ("The exit from provisional", "amber", "open", "G10 item 88", [
            "**ADR-0050 stops being provisional** when its debts are met and the custodian records it: a first lease "
            "from a completed tally, with a promoted seating; the first operators seated by an anchor issuance; a "
            "`Regrant` at rung 1 or above, which has to launch a guest; an operator's Persona record and lineage; "
            "and **a review by a reader who is not the drafter** (ADR-0050 §10; G10 item 88).",
            "Until then, A3 is subject to redesign with it, and anything citing it says \"author-ratified, "
            "provisional\" (ADR-0029 A4).",
        ]),
    ]
    ch3 = max(c.card(0, 0, w3b, tt, bb, draw=False, size=14, status=st) for tt, _, st, _, bb in C3)
    for i, (tt, acc, st, ex_, bb) in enumerate(C3):
        c.card(rx + i * (w3b + 28), y, w3b, tt, bb, accent=acc, h=ch3, size=14, status=st, status_extra=ex_,
               tint=st != "notbuilt")
    y = max(y + ch3, c.ymax) + 60

    # ------------------------------------------------------------------ tables: seat classes, quorum values
    c.heading(X0, y, "Quorum: archetype \"all\" versus a threshold k, and the two declared degeneracies", "ink", 21)
    y += 46
    lw = 1250
    qcols = [("`quorum`", 220, {"bold": True}), ("Meaning", 520), ("Rules-floor position", lw - 740)]
    qrows = [
        {"cells": ["\"all\"", "Every counted grant seat must grant; a grant-seat deny or abstention denies. "
                   "**Archetype value.**", "Required by **R1**"], "accent": "blue"},
        {"cells": ["k, 1 < k < |G|", "A grant-vote threshold over the counted seats: **D-0024-1**, k-of-n",
                   "Relaxes R1; **R9** keeps k ≥ 2"], "accent": "amber"},
        {"cells": ["1 (single-seat roster)", "One signer: **D-0024-2**, the pre-0024 status quo",
                   "Relaxes R1, R9 and R2"], "accent": "red"},
        {"cells": ["\"any\"", "**Withdrawn** (rev 5): it is k = 1 and tolerates no Byzantine approver, never the "
                   "k-of-n degeneracy it appeared to be", "—"], "accent": "grey"},
    ]
    qh = c.table(X0, y, qcols, qrows, size=14, accent="blue")
    c.para(X0, y + qh + 14, lw, "A threshold means something only with at least three counted seats: at two, k ≥ 2 "
           "**is** unanimity (ADR-0026 §7 finding 3).", 14, "muted")

    dx = X0 + lw + 40
    dw = X1 - dx
    dcols = [("Record", 140, {"bold": True}), ("Rule", 230), ("Premise falsified", 300), ("Sacrificed", 0),
             ("Gained", 0)]
    rest = dw - 140 - 230 - 300
    dcols[3] = ("Sacrificed", rest * 0.58)
    dcols[4] = ("Gained", rest * 0.42)
    drows = [
        ["D-0024-1", "k-of-n grant seats", "No promotion without every grant seat",
         "Tolerance of n−k Byzantine approvers", "Liveness under n−k absent approvers"],
        ["D-0024-2", "Single signer (the pre-0024 status quo)", "Grants need consensus",
         "All approver fault tolerance; reintroduces a privileged human grant", "Throughput"],
    ]
    dh = c.table(dx, y, dcols, drows, size=14, accent="amber")
    c.para(dx, y + dh + 14, dw, "Both ratified with ADR-0024 as declarations (B2). Each is a change to issued "
           "`quorum` and `minGrant`, so it relaxes ADR-0026 entries, not this record, and needs an anchor issuance "
           "plus a promotion under the rule being replaced. **A promotion degeneracy is a mechanism release**; "
           "approver fault tolerance and anchor recoverability are declared independently (ToO §7.7).", 14, "ink")
    y += max(qh + 60, dh + 120) + 30

    # ------------------------------------------------------------------ costs and status
    c.heading(X0, y, "Stated costs, and where the record stands", "ink", 21)
    y += 46
    w4 = (W - 3 * 28) / 4
    k1 = ["**Liveness equals the availability of every grant seat**, Persona and incident-driven bundle promotions "
          "included.",
          "Liveness assumption: weak fairness on `Vote` for grant seats, an assumption about people.",
          "**A2 adds a second**: weak fairness on an independent Observer's lease and its coverage, an assumption "
          "about a deployment."]
    k2 = ["**Correlated review failure is untouched**: unanimous humans reading the same vacuous gate output fail "
          "together (Knight & Leveson).",
          "Floor fitness, a fourth gate (NIST MEASURE 2.13), **now has an owner and a time**, the bootstrap reviewer "
          "at bootstrap (ADR-0029 A4; ADR-0030 A3), **and no test** (G10 items 2, 87).",
          "**One compromised seat is a veto** until the anchor reissues the roster.",
          "Voters are `Mediated`: promotion gains attribution and authorization, not safety properties."]
    k3 = ["ADR-0024 is **Accepted (genesis), 2026.09.23**, at revision 5, in Batch 2.",
          "**No confirmation marker**: a bootstrap record (ADR-0029 §4); confirmation runs under it. "
          "ADR-0029 A2's full-corpus review reaches it before bootstrap: a reader, not a confirmation promotion.",
          "A2 ratified 2026.09.29 (Batch 15), in genesis for the same reason.",
          "**A3 ratified 2026.10.05 (Batch 34), provisional** with ADR-0050: in force and subject to redesign. In the "
          "bootstrap set, so not confirmation-required; **the genesis attestation must name it as provisional** "
          "(ADR-0029 A4). Not reviewed by a reader other than the drafter."]
    k4 = ["**In the reference**: A2.1 (veto roster kinds) and A2.3 (`Tally::Stalled` until coverage) are in force; "
          "**A2.2 is not** (G18): no independence table exists, since ADR-0035 is Proposed and §4 is unbuilt.",
          "**A3 is not built**: no promoted seating grants a first lease; the BOOTSTRAP socket seats (below; I47).",
          "**Owed**: the ADR-0026 §6 non-vacuity rerun with A2.2 and A2.3 as conjuncts (G10 §2.1); the `Promotion` "
          "bootstrap module (`StaleVotesNeverCount`), not drafted, which also owes a model of deciding before "
          "committing (ToO §9); independent evidence and seat diversity, candidate floor entries."]
    kh = max(c.card(0, 0, w4, "Liveness", k1, draw=False), c.card(0, 0, w4, "Safety it does not buy", k2, draw=False),
             c.card(0, 0, w4, "Status", k3, draw=False, status="accepted"),
             c.card(0, 0, w4, "Built, and owed", k4, draw=False))
    c.card(X0, y, w4, "Liveness", k1, accent="amber", h=kh)
    c.card(X0 + (w4 + 28), y, w4, "Safety it does not buy", k2, accent="red", h=kh, tint=False, dash="6 4")
    c.card(X0 + 2 * (w4 + 28), y, w4, "Status", k3, accent="blue", h=kh, status="accepted",
           status_extra="bootstrap set · A2 in force · A3 provisional")
    c.card(X0 + 3 * (w4 + 28), y, w4, "Built, and owed", k4, accent="red", h=kh)
    return c
