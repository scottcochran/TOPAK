"""C3 — Lease anatomy: ADR-0031's closed twelve-field schema and the lease's life from grant to end."""
from lib import Canvas

ID, SLUG = "C3", "lease-anatomy"


def build():
    c = Canvas(ID, "The lease is the credential: twelve fields, one round, one live lease per principal",
               "ADR-0031 fixes a **closed schema**: every field is an authority claim, and a capability that is not a "
               "field is not carried; adding one is a mechanism release. The lease is granted for one round and ends "
               "with it, its fence is the Paxos log index at grant, renewal only narrows, and every way a lease ends "
               "subtracts authority. Since Batch 34 the record also says **who grants and who denies** (A3, provisional): a "
               "first lease from a quorum, the next round and every stop from an operator.",
               3400, "ADR-0031 §1–§8 with R1–R3, C1, E1, A1, A2, A3 and History B5, B8, B10, B17, B23, B29, B34; ADR-0034 §3, "
                     "§3.2 (A3, B29); ADR-0037 §1; ADR-0040 §4; ADR-0033 §4, A6, A7 (B29), A11, A12, A13 (B33); ADR-0032; "
                     "ADR-0016 §6; ADR-0026 W1; ADR-0047 §1, §4; ADR-0048 R6, §8; ADR-0050 §2–§6, §10; ADR-0052 §1–§3; "
                     "ADR-0041 A3 (`C1`–`C9`); spec/Lease_A1.tla (0b5eac7a7309be2f) and spec/Lease_A1-results-2026.09.28.txt; "
                     "spec/Lease_A1_proof.tla (6f39c7711252c8de), Lease_A1-proof-results-2026.10.02.txt and "
                     "Lease_A1-proof-cert-results-2026.10.04.txt; ADR-0046 §4, A1; mechanism topak-core lease.rs (`Lease`), "
                     "state.rs (`EndReason`, `LeaseRecord`, `apply_issue`; git diff 7075169..HEAD), control.rs; topak-node "
                     "mechanism.rs (`apply_committed`); GAPS I39, I41, I47; ToO rev 14 §2.5, §3.3, §7.10; G10 §1, §2.1, "
                     "§2.3, §3 (result 2, result 4), §7 items 21, 22, 62, 95, 96; ADR-0022 §1; ADR-0042 §5; ADR-0024 §3; "
                     "derived/topak-format-and-schema-inventory-2026.10.03.md §1.1")
    X0, X1 = c.x0, c.x1
    y = c.y

    # ------------------------------------------------------------------ status strip
    sx = X0
    c.text(sx, y + 16, "ADR-0031", 16, "ink", bold=True)
    sx += 90
    sx += c.status(sx, y, "accepted", "C1 (§5 break-glass lapse) · C2 for A1 only") + 12
    sx += c.status(sx, y, "provisional", "A3 · C1, C3") + 12
    c.text(sx, y + 16, "A1 renewal keeps the rung (B10) · A2 `ttl ≤ T_persona` (B17, built by ADR-0033 A6, B23) · "
           "E1 expiry ordered (B8) · A3 who grants and who denies (B34, with ADR-0050)", 14, "muted")
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
         "Checked (signed revision, G10 §2.7) · **assumed**", K + " (R2): nothing orders two bundles"],
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
        {"group": "Beside the lease, not in it: §1's set stays closed (A3; ADR-0034 §3.2)", "accent": "violet"},
        ["task", "The round's task by digest, and its label: on the log with a seating or a `Regrant`, its bytes in the "
                 "round's opening record", "A3; ADR-0050 §5; ADR-0047 §1",
         "The operator's signed declaration; refused outside the seating's labels (`C8`)", "—"],
        ["(appraisal)", "The confinement appraisal the lease was granted on", "ADR-0034 §3.2 (A3, B29)",
         "Re-checked at apply on every replica (ADR-0033 A7)", "Re-attested"],
        ["(no tool set)", "**A lease cannot be narrowed to a tool**: no field carries one, so a round's tool list is "
                          "narrowed only by the `alphabet` and the issued allowlist", "ADR-0048 R6",
         "G10 §3 result 4", "Open: G10 item 95"],
    ]
    c.heading(X0, y, "ADR-0031 §1: the closed schema, with §6's trusted-base split")
    th = c.table(X0, y + 40, cols, rows, size=14, accent="blue") + 40
    left_bot = y + th

    # notes under the schema
    ny = left_bot + 24
    nw = (TW - 48) / 3
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
        "**Rung 0 is** `Mediated`**, always** (§3). The reference grants rung 0 and, through its launcher, rung 1 and "
        "a **SIMULATED** rung 3 (ADR-0033 A7, B29; G10 §2.3): no real principal is `Contained`, and an operator or "
        "an emergency seat is `Mediated` by design.",
        "**The appraisal is not a field** (ADR-0034 §3.2, A3, B29): the reference keeps it beside the lease on its "
        "`LeaseRecord`, with `ended`, the action count, the sequence number and the session counter (I39, I41), and "
        "since 2026.10.05 the round's labels and, on an emergency lease, the person's key and the envelope.",
        "**Confinement is necessary, not sufficient** for `Contained`: the provenance axis must also clear (§3; "
        "ADR-0034 §4; ADR-0035 Proposed).",
    ]
    n3 = [
        "Nine reasons, serialized snake_case: `submitted`, `abstained`, `voted`, `expired`, `fenced`, `revoked`, "
        "`rules_changed`, `operator`, `renewed`.",
        "`renewed` **is an end**: a renewal closes the old record and opens a narrower one at the new fence, so "
        "\"same lease, new fence\" is two records in state and one lease in the record's sense (§4).",
        "ADR-0042 §5's seal table has every one a Run lease can have except `renewed`; `submitted`, `abstained` and "
        "`voted` are Build's. `rules_changed` and `voted` are ends ADR-0031 does not name (right).",
        "Unchanged by the rebuild. An operator's signed `EndRound` ends as `operator`, its `Revoke` as `revoked`, its "
        "`FenceEpoch` as `fenced` (ADR-0033 A11).",
    ]
    hn = max(c.card(0, 0, nw, "Rules the schema rests on", n1, size=14, draw=False),
             c.card(0, 0, nw, "What the schema is", n2, size=14, draw=False),
             c.card(0, 0, nw, "How a lease ends at the reference", n3, size=14, draw=False))
    c.card(X0, ny, nw, "Rules the schema rests on (§2)", n1, accent="blue", size=14, h=hn)
    c.card(X0 + nw + 24, ny, nw, "What the schema is (§3, §6)", n2, accent="teal", size=14, h=hn)
    c.card(X0 + 2 * (nw + 24), ny, nw, "How a lease ends at the reference (`EndReason`, state.rs)", n3,
           accent="grey", size=14, h=hn, tint=False)
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
        "The bundle revision verifies under the rules' `bundle_keys` (ADR-0033 A6; G10 §2.7).",
        "At rung ≥ 1: an **Attested** appraisal at the declared rung, nonce = hash(epoch, log index, principal, "
        "round); Unattestable or Contested refuses, never a lower rung (ADR-0034 §3). At the reference it is "
        "re-checked at apply on every replica (ADR-0033 A7, B29).",
        "`fence` := the Paxos log index of the grant entry; consensus-ordered, like every authority increase.",
    ]
    gh = c.card(gx, gy, gw, "grant (§2): an admit decision at a fresh fence", grant_body, accent="blue", size=13.5)
    # who grants (A3), to the right of the free slot and the grant
    rnx = s0x + 620 + 90
    rnw = ix1 - rnx
    who_body = [
        "**A first lease**: granted by the mechanism when a quorum completes, an anchor issuance (rostered seats, the "
        "first operators) or a promotion's tally on a seating. No request. [[red|Not built]]: at the reference the "
        "unsigned socket seats, a **BOOTSTRAP** path, and whoever reaches it can seat (ADR-0050 §10; G10 §8).",
        "**A successor grant** (`Regrant`, `C1`): the next round, every field the last lease's or narrower, only "
        "`round` advancing; by an operator with a live lease and a live peer (`C5`), never itself (`C6`), with a task "
        "label the seating allows (`C8`).",
        "**Anything wider** (Persona, bundle, confinement, seat, a wider alphabet) is a first lease and needs a quorum.",
        "**An emergency lease** is activated by the break-glass roster's quorum for one person and one round "
        "(ADR-0052 §2).",
    ]
    wh = c.card(rnx, s0y, rnw, "Who grants (A3, from ADR-0050 §2)", who_body, accent="blue", size=13.5,
                status="provisional")
    # live state
    s1y = max(gy + gh + 50, s0y + wh + 190)
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
    ren_body = [
        "**May** narrow the `alphabet` or shorten the `ttl` (again ≤ `T_persona`). **Never adds authority**: "
        "lease(n+1) ⊑ lease(n).",
        "**Keeps** `bundle`, `round`, `role` and `confinement`, digest **and rung** (R1, R2, A1).",
        "**Re-attests** the Persona and confinement with a fresh nonce (ADR-0034 §3.6). Attested: same rung. "
        "Unattestable: refused, the lease lapses. Contested: never at renewal (finding 5).",
        "It measures the launch again, not the running guest.",
        "**By an operator** (`Renew`, `C2`), on the successor's terms (`C5`, `C6`). **An emergency lease is never "
        "renewed** (ADR-0052 §3).",
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
            "**Build**: `Submit` is terminal for the authoring round, or an operator's signed `EndRound` in its own "
            "domain (`C4`, `C9`).",
            "**Build**: `Vote` is terminal for the voter's promotion round, and `Submit(⊥)` abstains (ADR-0022 §1; "
            "`voted`, `abstained` at the reference).",
            "**Run**: no terminal variant; **the round ends when the lease ends** (ADR-0040 §4).",
            "The topic seals (ADR-0003). A new bundle reaches a live principal only this way: **tightening a live "
            "round ends it** (R2).",
        ]),
        ("Local expiry, then ordered (E1)", "amber", [
            "Each replica reads its own **monotonic clock** with an asymmetric margin: expired early, never late (§7).",
            "The first replica to see expiry **proposes the round's end as a log entry**, so all agree when the slot "
            "frees (ADR-0033 §4).",
            "Clocks buy liveness, never safety (ADR-0032).",
            "**A race, fixed** (ADR-0033 A13, B33): a lease just granted could be ended as expired, since a replica "
            "recorded seeing the grant after releasing the state lock. Found by a trace run, by no proof.",
        ]),
        ("Targeted revocation (§5, R3)", "red", [
            "Target: a **principal**, a **Persona digest** or a **confinement digest**; ends every live lease it "
            "matches and nothing else.",
            "Bars later grants (the **revocation set**). The text still lapses the seat's break-glass approvals "
            "(C1); X1 is retired and they no longer exist (ToO §2.5).",
            "**An operator's** `Revoke`, in its own domain: a live lease or a fresh sign-on assertion (A3; `C4`, `C9`).",
            "Permanent within the rules-epoch chain. A Contested verdict revokes the principal (ADR-0034 §3.7).",
        ]),
        ("Epoch fence (§5)", "red", [
            "Increments the epoch: **every lease at the old epoch is fenced**, every live round ends.",
            "Kept for e-stop, suspected compromise of mechanism or anchor, and a bundle that must reach everyone now.",
            "Rejected by the mechanism, ahead of the floor (ADR-0022 §2).",
            "**An operator's** `FenceEpoch`, which needs a **live lease** (A3; `C4`, `C7`).",
        ]),
        ("New rules epoch (ADR-0042 §5)", "red", [
            "An admitted issuance moves the rules epoch; the reference ends **every** live lease (`rules_changed`, "
            "`state.rs`), since each names the old `rulesEpoch`.",
            "ADR-0042 §5's seal table lists it for Run; **ADR-0031 does not name it.** In-flight votes are voided the "
            "same way (ADR-0024 §3).",
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
                "add authority and no record says who may (G10 item 22, as at G9). **Who denies** (A3, provisional): both "
                "tools are an operator's, signed with its Persona's key, with no quorum and no peer; the epoch fence "
                "needs a live lease, the others a live lease or a fresh sign-on assertion. The signature is the "
                "attribution F2 asks for (ADR-0028).", 14, "muted")
    left_bot = y5 + 40 + t1 + 14 + p5
    y = max(left_bot, sm_bot) + 60
    tp = [
        "A lease's `ttl`, at grant and at every renewal, is **at most** `T_persona`, a policy-floor value "
        "(`floor/genesis-values.json`): the Persona is re-attested at least that often.",
        "**Built at the reference** (ADR-0033 A6, Batch 23): refused at grant and renewal in `apply`, with a mutation "
        "test at the bound's edge; `Mechanism.tla` carries both checks.",
        "**The value is a placeholder** (one hour) and **expiry runs on the local clock**: the bound is enforced, the "
        "interval still drifts (G10 item 62, as at G9; ADR-0045 finding 2).",
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
        "**ADR-0033 A13** (B33): the reference could order `EndRound(Expired)` for a lease just granted; the "
        "observation is now recorded before the lock is released. The clock is outside every module, so no proof "
        "could find it; whether any other fact kept beside the state is recorded late is not audited (G10 item 96).",
    ]
    em = [
        "**An emergency lease ends with its round**: at the round bound `R`, at its `ttl`, which is at most "
        "`T_persona` like any lease's, or when the person ends it; sooner at a fence or a revocation, which any "
        "operator of the domain may make (ADR-0052 §3).",
        "**No successor and no renewal**: an operator's `Regrant` or `Renew` naming the seat is refused, and another "
        "round is another quorum.",
        "**No issued TTL.** R8, the break-glass TTL, was withdrawn (ADR-0026 W1, 2026.10.04): it would have needed "
        "trusted time. The time box is the round, on the clock the corpus already accepts for a lease.",
    ]
    th3 = (X1 - X0 - 2 * 40) / 3
    c.heading(X0, y, "A2: the TTL is bounded by `T_persona`")
    c.status(X0 + th3, y + 2, "accepted", "B17 · built B23", anchor="end")
    c.heading(X0 + th3 + 40, y, "§7: the clock assumption, stated")
    c.status(X0 + 2 * th3 + 40, y + 2, "accepted", "E1 · B8", anchor="end")
    c.heading(X0 + 2 * (th3 + 40), y, "An emergency lease: one round")
    c.status(X1, y + 2, "provisional", "ADR-0052", anchor="end")
    hh = max(c.card(0, 0, th3, None, b, size=14, draw=False) for b in (tp, clk, em))
    c.card(X0, y + 40, th3, None, tp, accent="amber", size=14, h=hh)
    c.card(X0 + th3 + 40, y + 40, th3, None, clk, accent="teal", size=14, h=hh)
    c.card(X0 + 2 * (th3 + 40), y + 40, th3, None, em, accent="brown", size=14, h=hh, dash="4 3")
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
    y += c.para(X0, y, X1 - X0,
           "**The finding the check bought (C1):** the first run failed on the full mechanism. A `Grant` replaced a live "
           "lease with wider authority, which satisfied every clause as first written, because §4 governs renewal and "
           "this was a grant. §2 now states the one-live-lease rule. Model: two principals, a two-variant alphabet, "
           "rungs 0–3, roles author and voter; the round number and the bundle are not modelled (the reference checks "
           "the bundle: `renewal_cannot_swap_the_bundle`). Earlier runs: R1 1,605,720 states, R3 1,746,048.", 14,
           "muted") + 16
    c.card(X0, y, X1 - X0, "Since 2026.10.02: the four invariants are proved (ADR-0031 B25; ADR-0046 §4); since "
           "2026.10.04 the proof is certified (ADR-0046 A1)", [
        "`spec/Lease_A1_proof.tla` (`6f39c7711252c8de`) proves, for every behaviour and every epoch and fence bound: "
        "`LeaseAuthorityMonotone` not under `M_RENEW`, `M_ROLE`, `M_LOWER`; `NoActionUnderFencedEpoch` not under "
        "`M_FENCE`; `Rung0NeverContained` not under `M_RUNG`; `RevokedStaysStopped` not under `M_REVOKE`. 200 "
        "obligations, by the prover T-0045-31. **Certified**: 121 closed by the prover's normalization, 73 by SMT with "
        "a proof the `ethos` checker accepted, 1 by Isabelle, and 5 temporal steps by LS4, which no checker confirms.",
        "The frozen `Lease.tla` is not separately proved: its invariants are `Lease_A1`'s at rungs 0..2. The rows "
        "above stay with TLC; the proof is of the module, not of the reference's grant path (T-0045-28). Who grants "
        "(A3) is not in this module: `Operators.tla` checks it (ADR-0050 §10).",
    ], accent="teal", size=14, status="accepted", status_extra="ADR-0046 · C2, C4 · B25")
    return c
