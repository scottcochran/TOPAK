"""C3 — Lease anatomy: ADR-0031's closed twelve-field schema and the lease's life from grant to end."""
from lib import Canvas

ID, SLUG = "C3", "lease-anatomy"


def build():
    c = Canvas(ID, "The lease is the credential: twelve fields, one round, one live lease per principal",
               "ADR-0031 fixes a **closed schema**: every field is an authority claim, and a capability that is not a "
               "field is not carried; adding one is a mechanism release. The lease is granted for one round and ends "
               "with it, its fence is the Paxos log index at grant, renewal only narrows, and every way a lease ends "
               "subtracts authority.",
               3200, "ADR-0031 §1–§8 with R1–R3, C1, E1, A1, A2 and History B5, B8, B10, B17, B23; ADR-0034 §3; "
                     "ADR-0037 §1; ADR-0040 §4; ADR-0033 §4 and A6; ADR-0032; ADR-0016 §6; spec/Lease_A1.tla "
                     "(0b5eac7a7309be2f) and spec/Lease_A1-results-2026.09.28.txt; ToO rev 11 §2.5; G7 §1.1, §2.2, §2.7, "
                     "§7 items 21, 22, 62")
    X0, X1 = c.x0, c.x1
    y = c.y

    # ------------------------------------------------------------------ status strip
    sx = X0
    c.text(sx, y + 16, "ADR-0031", 16, "ink", bold=True)
    sx += 90
    sx += c.status(sx, y, "accepted", "C1 (§5 break-glass lapse) · C2 for A1 only") + 12
    c.text(sx, y + 16, "A1 renewal keeps the rung (B10) · A2 `ttl ≤ T_persona` (B17, not confirmation-required) · "
           "A2 built at the reference by ADR-0033 A6 (B23) · E1 expiry ordered (B8)", 14, "muted")
    y += 46

    # ------------------------------------------------------------------ left: the schema table
    TW = 1500
    cols = [("Field", TW * 0.12, {"mono": True}), ("Content (§1)", TW * 0.36), ("Source", TW * 0.14),
            ("At grant · for the round (§6)", TW * 0.18), ("Across renewal (§4)", TW * 0.2)]
    K = "[[green|kept]]"
    rows = [
        {"group": "Checked at grant, assumed for the round: Persona, confinement, bundle, alphabet, round, role "
                  "(§6; ToO §2.5)", "accent": "blue"},
        ["persona", "The Persona ID, attested at grant and renewal", "ADR-0016 §6", "Checked · **assumed**",
         "Re-attested at every renewal"],
        ["confinement", "`[digest, rung]`: the confinement-profile digest and its attestation rung", "§3; ADR-0034",
         "Checked (appraisal at rung ≥ 1) · **assumed**", K + ", digest and rung (A1); re-attested"],
        ["bundle", "The bundle version this principal is admitted against", "ADR-0010",
         "Checked (signed revision, G7 §2.7) · **assumed**", K + " (R2): nothing orders two bundles"],
        ["alphabet", "The action variants this seat may express", "ADR-0007, ADR-0022 §1",
         "Checked (kind's row, ADR-0037 §4) · **assumed**", "[[green|may narrow]]"],
        ["round", "The round this lease is granted for. Never reused per seat", "ADR-0003, §2",
         "Checked · **assumed**", K + " (R1)"],
        ["role", "The principal's role in that round: author or voter", "ADR-0022 §7, ADR-0024",
         "Checked · **assumed**", K + " (R1): not an order"],
        {"group": "Compared on every action, not assumed", "accent": "teal"},
        ["epoch", "The epoch this lease is valid at. Any increment fences it", "ADR-0022 §2",
         "Assigned · **compared**", "—"],
        ["fence", "**The Paxos log index at grant**: the lease's position in the consensus order", "§2",
         "Assigned · **compared**", "A renewal sits at a new fence (Options)"],
        ["rulesEpoch", "The rules epoch in force at grant", "ADR-0025, ADR-0026", "Assigned · **compared**", "—"],
        {"group": "Assigned, then assumed to be read on a sound clock", "accent": "amber"},
        ["ttl", "Expiry, as a duration on the local monotonic clock; **at most** `T_persona` (A2)", "§7; ADR-0016 §6",
         "Assigned · assumed read on a sound clock (§7)", "[[green|may shorten]]; again ≤ `T_persona`"],
        {"group": "Identity: not in §6's table; since ADR-0037 §1 the two determine each other", "accent": "grey"},
        ["principal", "The principal's identity", "ADR-0002 A2", "(not classified in §6)", "Same principal"],
        ["seat", "The LTRO seat held for this round", "ADR-0016 §5, ADR-0018", "(not classified in §6)", "—"],
    ]
    c.heading(X0, y, "ADR-0031 §1: the closed schema, with §6's trusted-base split")
    th = c.table(X0, y + 40, cols, rows, size=14, accent="blue") + 40
    left_bot = y + th

    # notes under the schema
    ny = left_bot + 24
    nw = (TW - 24) / 2
    n1 = [
        "**Round-coterminous**: no lease outlives its round, and no round outlives its lease (§2).",
        "**At most one live lease per principal; a grant requires that none is live** (§2, C1). Without it, monotone "
        "renewal guarantees nothing: take a fresh grant instead. The first model check found exactly that.",
        "**The fence is the Paxos log index at grant**: leases, admits and issuances are ordered by one log, and a "
        "stale lease is detected by comparing indices.",
    ]
    n2 = [
        "**The field list is the per-round TCB** (§6): the one slice of the trusted base that is derived rather than "
        "declared; the rest is ADR-0045's table.",
        "**Rung 0 is** `Mediated`**, always** (§3). Every lease the reference issues is rung 0 (G7).",
        "**Confinement is necessary, not sufficient** for `Contained`: the provenance axis must also clear (§3; "
        "ADR-0034 §4; ADR-0035 Proposed).",
    ]
    hn = max(c.card(0, 0, nw, "Rules the schema rests on", n1, size=14, draw=False),
             c.card(0, 0, nw, "What the schema is", n2, size=14, draw=False))
    c.card(X0, ny, nw, "Rules the schema rests on (§2)", n1, accent="blue", size=14, h=hn)
    c.card(X0 + nw + 24, ny, nw, "What the schema is (§3, §6)", n2, accent="teal", size=14, h=hn)
    left_bot = ny + hn

    # ------------------------------------------------------------------ right: the state machine
    RX0 = X0 + TW + 70
    RX1 = X1
    RW = RX1 - RX0
    pad = 30
    top = y + 10
    ix0, ix1 = RX0 + pad, RX1 - pad
    iw = ix1 - ix0
    # state: no live lease
    s0w = 620
    s0x = ix0 + 300
    s0y = top + 50
    s0h = c.card(s0x, s0y, s0w, "No live lease: the principal's slot is free", [
        "The only state from which a grant is possible: one live lease per principal, and per seat, which ADR-0037 "
        "§1 makes the same rule.",
    ], accent="grey", size=14, bullets=False)
    # grant conditions
    gy = s0y + s0h + 50
    gw = 700
    gx = s0x - 40
    grant_body = [
        "**None live** for the principal (§2); the target is **not in the revocation set** (§5).",
        "`ttl ≤ T_persona`, refused by the mechanism, not policy (A2; built, ADR-0033 A6).",
        "The `alphabet` is inside the seat kind's row and domain (ADR-0037 §4).",
        "The bundle revision verifies under the rules' `bundle_keys` (ADR-0033 A6; G7 §2.7).",
        "At rung ≥ 1: an **Attested** appraisal at the declared rung, nonce = hash(epoch, log index, principal, "
        "round); Unattestable or Contested refuses, never a lower rung (ADR-0034 §3).",
        "`fence` := the Paxos log index of the grant entry; consensus-ordered, like every authority increase.",
    ]
    gh = c.card(gx, gy, gw, "grant (§2): an admit decision at a fresh fence", grant_body, accent="blue", size=13.5)
    # live state
    s1y = gy + gh + 50
    s1w = 620
    s1x = s0x
    s1h = c.card(s1x, s1y, s1w, "Live lease", [
        "Every action carries epoch and lease; the mechanism compares `epoch`, `fence` and `rulesEpoch` on each one "
        "and assumes the six checked fields for the round.",
        "An admit decided under a lease that has since ended is **void at apply** (ADR-0033 §4).",
    ], accent="teal", size=14, bullets=False)
    c.arrow([(s0x + s0w / 2, s0y + s0h), (s0x + s0w / 2, gy)], "blue", sw=2.6)
    c.arrow([(s0x + s0w / 2, gy + gh), (s0x + s0w / 2, s1y)], "blue", sw=2.6)
    # renewal loop on the right
    rnx = s1x + s1w + 90
    rnw = ix1 - rnx
    ren_body = [
        "**May** narrow the `alphabet` or shorten the `ttl` (again ≤ `T_persona`). **Never adds authority**: "
        "lease(n+1) ⊑ lease(n).",
        "**Keeps** `bundle`, `round`, `role` and `confinement`, digest **and rung** (R1, R2, A1).",
        "**Re-attests** the Persona and confinement with a fresh nonce (ADR-0034 §3.6). Attested: same rung. "
        "Unattestable: refused, the lease lapses. Contested: never at renewal (finding 5).",
        "It measures the launch again, not the running guest.",
    ]
    rnh = c.card(rnx, s1y - 150, rnw, "renew (§4): only narrows", ren_body, accent="green", size=13.5)
    ly1 = s1y + 40
    c.arrow([(s1x + s1w, ly1), (rnx, ly1)], "green", sw=2.4)
    c.arrow([(rnx, s1y + 100), (s1x + s1w, s1y + 100)], "green", sw=2.4)
    c.label((s1x + s1w + rnx) / 2, ly1 - 22, "renew", "green", 12.5)
    c.label((s1x + s1w + rnx) / 2, s1y + 100 + 22, "same lease, new fence", "green", 12.5)

    # exits
    ey = s1y + s1h + 110
    ex_cards = [
        ("Round end", "grey", [
            "**Build**: `Submit` is terminal for the authoring round, or the operator's `end_round`.",
            "**Run**: no terminal variant; **the round ends when the lease ends** (ADR-0040 §4).",
            "The topic seals (ADR-0003). A new bundle reaches a live principal only this way: **tightening a live "
            "round ends it** (R2).",
        ]),
        ("Local expiry, then ordered (E1)", "amber", [
            "Each replica reads its own **monotonic clock** with an asymmetric margin: expired early, never late (§7).",
            "The first replica to see expiry **proposes the round's end as a log entry**, so all agree when the slot "
            "frees (ADR-0033 §4).",
            "Clocks buy liveness, never safety (ADR-0032).",
        ]),
        ("Targeted revocation (§5, R3)", "red", [
            "Target: a **principal**, a **Persona digest** or a **confinement digest**; ends every live lease it "
            "matches and nothing else.",
            "Bars later grants (the **revocation set**) and **lapses the seat's break-glass approvals** (C1).",
            "Permanent within the rules-epoch chain. A Contested verdict revokes the principal (ADR-0034 §3.7).",
        ]),
        ("Epoch fence (§5)", "red", [
            "Increments the epoch: **every lease at the old epoch is fenced**, every live round ends.",
            "Kept for e-stop, suspected compromise of mechanism or anchor, and a bundle that must reach everyone now.",
            "Rejected by the mechanism, ahead of the floor (ADR-0022 §2).",
        ]),
        ("Renewal refused", "amber", [
            "Evidence no longer reaches the lease's rung: **the lease lapses**; it is never renewed at a lower rung, "
            "which would be a silent downgrade (A1; ADR-0034 §3.4).",
            "An unreachable verifier stops grants and renewals: PC/EC (ADR-0034 §3).",
        ]),
    ]
    n = len(ex_cards)
    eg = 18
    ex0 = ix0 + 70
    ew = (ix1 - ex0 - (n - 1) * eg) / n
    eh = max(c.card(0, 0, ew, t, b, size=13.5, draw=False) for t, _, b in ex_cards)
    for i, (t, a, b) in enumerate(ex_cards):
        x = ex0 + i * (ew + eg)
        c.card(x, ey, ew, t, b, accent=a, size=13.5, h=eh, tint=False, dash="6 4")
        xm = x + ew / 2
        # from the live lease down to each exit
        busy = s1y + s1h + 50
        c.arrow([(s1x + s1w / 2, s1y + s1h), (s1x + s1w / 2, busy), (xm, busy), (xm, ey)], a, sw=2, dash="7 5")
    c.label(s1x + s1w / 2, s1y + s1h + 25, "every exit subtracts: no quorum needed, but each is ordered in the log",
            "red", 13)
    # ended state
    s2y = ey + eh + 60
    s2w = 760
    s2x = ix0 + (iw - s2w) / 2
    s2h = c.card(s2x, s2y, s2w, "Ended", [
        "The slot frees once the end is ordered. **A change of any kept field** (`bundle`, `round`, `role`, "
        "`confinement` digest or rung) **is a grant**, so it takes this path: end the round, then a fresh grant at a "
        "new fence (§4). Elevation of the rung is likewise a fresh grant (ADR-0036 R1, Proposed).",
    ], accent="grey", size=14, bullets=False)
    for i in range(n):
        xm = ex0 + i * (ew + eg) + ew / 2
        jy = s2y - 30
        c.arrow([(xm, ey + eh), (xm, jy), (s2x + s2w / 2, jy), (s2x + s2w / 2, s2y)], "grey", sw=1.8,
                head=(i == n - 1))
    # back to slot free, on the left
    bx = ix0 + 20
    c.arrow([(s2x, s2y + s2h / 2), (bx, s2y + s2h / 2), (bx, s0y + s0h / 2), (s0x, s0y + s0h / 2)], "grey", sw=2.4,
            label="slot free: a new grant may follow, unless the target is revoked", lpos=0.86, loff=(0, 0),
            lw=210)
    sm_bot = s2y + s2h + 30
    c.region(RX0, top, RW, sm_bot - top, "The lease's life (§2, §4, §5, §7; E1; A1, A2)", "teal", dash=None, sw=2.4,
             size=16)

    # §5 in the left column, under the notes
    y5 = left_bot + 40
    half = (X1 - X0 - 40) / 2
    c.heading(X0, y5, "ADR-0031 §5 (R3): revocation has two tools, chosen by scope")
    cols = [("Tool", TW * 0.16, {"bold": True}), ("Used for", TW * 0.36), ("Effect", TW * 0.48)]
    t1 = c.table(X0, y5 + 40, cols, [
        ["Targeted revocation", "Persona revocation, confinement-profile failure, operator revocation of a known "
                                "principal",
         "Ends every live lease the target matches, and bars every later grant it matches. A target is a principal, a "
         "Persona digest or a confinement digest. The epoch, and every other lease, is untouched"],
        ["Epoch fence", "Scope unknown or fleet-wide: e-stop, suspected compromise of the mechanism or anchor, a bundle "
                        "that must reach every principal now (§4)",
         "Increments the epoch. Every lease at the old epoch is fenced (ADR-0022 §2), and every live round ends"],
    ], size=14, accent="red")
    p5 = c.para(X0, y5 + 40 + t1 + 14, TW,
                "Both are enforced by the mechanism ahead of the floor; both subtract, so neither needs a quorum; both "
                "change replicated state, so both are consensus-ordered (ADR-0033 §4). **Lifting a revocation** would "
                "add authority and no record says who may (G7 item 22, open).", 14, "muted")
    left_bot = y5 + 40 + t1 + 14 + p5
    y = max(left_bot, sm_bot) + 60
    tp = [
        "A lease's `ttl`, at grant and at every renewal, is **at most** `T_persona`, a policy-floor value "
        "(`floor/genesis-values.json`): the Persona is re-attested at least that often.",
        "**Built at the reference** (ADR-0033 A6, Batch 23): refused at grant and renewal in `apply`, with a mutation "
        "test at the bound's edge; `Mechanism.tla` carries both checks.",
        "**The value is a placeholder** (one hour) and **expiry runs on the local clock**: the bound is enforced, the "
        "interval still drifts (G7 item 62; ADR-0045 finding 2).",
        "Between two re-attestations a substituted Persona is undetected for at most `T_persona` (Consequences).",
    ]
    clk = [
        "Expiry is a read of a **local monotonic clock with an asymmetric margin**: a lease is treated as expired early "
        "rather than late, so clock error subtracts authority (§7).",
        "ADR-0032 generalises the rule: an interval whose failure subtracts may use a local clock; one whose failure "
        "adds or preserves authority needs trusted time. **Clocks buy liveness, never safety**: an expired lease its "
        "holder still believes in is rejected by the epoch fence.",
        "E1 (Batch 8): expiry is read locally and then ordered, so every replica agrees when the one-live-lease slot "
        "frees.",
    ]
    c.heading(X0, y, "A2: the TTL is bounded by `T_persona`")
    c.status(X0 + half, y + 2, "accepted", "B17 · built B23", anchor="end")
    c.heading(X0 + half + 40, y, "§7: the clock assumption, stated")
    c.status(X1, y + 2, "accepted", "E1 · B8", anchor="end")
    hh = max(c.card(0, 0, half, None, tp, size=14, draw=False), c.card(0, 0, half, None, clk, size=14, draw=False))
    c.card(X0, y + 40, half, None, tp, accent="amber", size=14, h=hh)
    c.card(X0 + half + 40, y + 40, half, None, clk, accent="teal", size=14, h=hh)
    y += 40 + hh + 50

    # ------------------------------------------------------------------ §8 the property check
    c.heading(X0, y, "ADR-0031 §8: the property check, `spec/Lease_A1.tla` (digest 0b5eac7a7309be2f), A1 run "
                     "2026.09.28, rungs 0–3")
    y += 40
    TW2 = X1 - X0
    cols = [("Check", TW2 * 0.42), ("Mutation", TW2 * 0.1, {"mono": True}), ("Invariant", TW2 * 0.2, {"mono": True}),
            ("Result", TW2 * 0.28, {"bold": True})]
    H = "[[green|holds]]"
    CE = "[[red|counterexample]] ✓"
    rows = [
        ["Full mechanism", "none", "Safe (all four)", H + ": 2,136,720 distinct states (A1 run)"],
        ["Reachability: an action is admitted", "none", "NeverActed", CE],
        ["Reachability: a renewal happens", "none", "NeverRenewed", CE],
        ["Reachability: a revocation happens", "none", "NeverRevoked", CE],
        ["Reachability: **a lease outlives a revocation**", "none", "NeverStaleLease", CE],
        ["Reachability: **one principal is revoked and another's lease stays live** (R3)", "none",
         "NeverSelectiveRevoke", CE],
        ["Renewal may add authority", "M_RENEW", "LeaseAuthorityMonotone", CE],
        ["The mechanism skips the epoch check", "M_FENCE", "NoActionUnderFencedEpoch", CE],
        ["`Contained` ignores the rung", "M_RUNG", "Rung0NeverContained", CE],
        ["Renewal ignores the role (R1)", "M_ROLE", "LeaseAuthorityMonotone", CE],
        ["A grant ignores the revocation set (R3)", "M_REVOKE", "RevokedStaysStopped", CE],
        ["Reachability: **a renewal at rung ≥ 1** (A1)", "none", "NeverRenewedAbove0", CE],
        ["Renewal may lower the rung (the rule as ratified at R3) (A1)", "M_LOWER", "LeaseAuthorityMonotone", CE],
    ]
    y += c.table(X0, y, cols, rows, size=14, accent="teal") + 20
    c.para(X0, y, X1 - X0,
           "**The finding the check bought (C1):** the first run failed on the full mechanism. A `Grant` replaced a live "
           "lease with wider authority, which satisfied every clause as first written, because §4 governs renewal and "
           "this was a grant. §2 now states the one-live-lease rule. Model: two principals, a two-variant alphabet, "
           "rungs 0–3, roles author and voter; the round number and the bundle are not modelled (the reference checks "
           "the bundle: `renewal_cannot_swap_the_bundle`). Earlier runs: R1 1,605,720 states, R3 1,746,048.", 14,
           "muted")
    return c
