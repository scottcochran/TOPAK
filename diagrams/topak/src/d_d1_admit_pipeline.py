"""D1 — The admit path: decide, then order, then effect."""
from lib import Canvas, text_width

ID, SLUG = "D1", "admit-pipeline"

W = 3200

# (number, title, accent, phase, body, deny-title, deny-body)
STEPS = [
    ("1", "Session → `ActionRequest`", "teal",
     ["The bearer token on the replica's agent socket names the **seat**, the **lease** (its fence, a log index) and "
      "the **epoch**; every action carries all three (ADR-0022 §2).",
      "`SubmitWorkspace` becomes `Submit(digest)` over the round workspace; an abstain from a Run seat is refused "
      "here, before ordering (ADR-0042 §5)."],
     "No session: `UnknownLease`",
     ["Names no principal and no round, so **there is no round record for it**: an authentication event logged at this "
      "replica's socket (ADR-0003 A2 note; register G5)."]),
    ("2", "Local expiry · **liveness**", "teal",
     ["The lease TTL runs on **this replica's monotonic clock** from when it applied the grant, read with the asymmetric "
      "margin, so it elapses early (ADR-0032 §2). No local observation of the grant counts as expired: fail closed.",
      "A liveness check only. **The fence in step 3 carries safety.**"],
     "`LeaseExpired`",
     ["The replica also proposes `EndRound(Expired)`: a subtraction, ordered so replicas agree, approved by nobody "
      "(ADR-0033 §4; ADR-0031 E1)."]),
    ("3", "Mechanism checks: epoch fence, lease, alphabet", "teal",
     ["`check_live`, in order: the lease is known and is this seat's; **lease epoch = current epoch** (the fence); "
      "request epoch = lease epoch; lease rules epoch = current rules epoch; lease not ended; action in the lease's "
      "alphabet; round bound not reached; action preconditions (`Submit` once; `Vote` only on a submitted artifact "
      "whose gates passed).",
      "**Mechanism, not policy**: the floor never decides whether an epoch is current (ADR-0030 §4)."],
     "Mechanism deny",
     ["`FencedEpoch`, `RequestEpochMismatch`, `FencedRulesEpoch`, `LeaseEnded`, `NotInAlphabet`, "
      "`RoundBoundReached`, `ArtifactNotSubmitted`, `ArtifactAlreadySubmitted`, `GatesNotPassed`, "
      "`EvidenceMismatch`, `AlreadyPromoted`."]),
    ("4", "Syntactic lift → **one frozen input**", "teal",
     ["Mechanical and total: every fact is a set membership, an equality or a path-syntax check; nothing interprets "
      "meaning (ADR-0007, ADR-0018 validator side).",
      "Principal, action, resource, context and the complete entity slice in schema S's shape, **plus the bundle's "
      "view built from the same facts**. Resolved once; the bundle may not re-fetch (ADR-0030 §4). Its digest goes "
      "into the admit.",
      "`observerLive` is `live(o)`, computed here (ADR-0039 §1)."],
     "Lift refused",
     ["A request the lift cannot build (for `Submit`, an artifact that is not the workspace digest) is a mechanism "
      "deny."]),
    ("5", "Floor: Cedar, linked · **can permit**", "blue",
     ["`floor/genesis-floor.cedar`, schema S and the values file compiled in **by path**; the replica refuses to "
      "start unless their bytes match the gated digests (ADR-0033 §2). The floor text is **DRAFT, not ratified**.",
      "S is enforced on every request: a non-conforming input is a deny (ADR-0030 §4)."],
     "Floor deny · short-circuits",
     ["`Floor([forbids that fired])`, or `FloorNoPermit`: outside every envelope (finding 10).",
      "`FloorError`: **any** evaluation error is a deny, since Cedar skips an erroring `forbid` (ADR-0030 §1).",
      "The bundle is never consulted."]),
    ("6", "Bundle: OPA sidecar | WASM · **can only refuse**", "amber",
     ["`data.topak.bundle.allow`, counted only from **the revision the lease names**, and only if that revision's "
      "signature verified under the rules' `bundle_keys` (ADR-0044; built, ADR-0033 A6).",
      "Sidecar unreachable or serving another revision → the in-process WASM engine decides **iff** it holds that "
      "revision; otherwise refuse. Every admit records which engine decided."],
     "`Bundle(reason)`",
     ["Deny, error, undefined, absent or unreachable: anything but an affirmative `true` refuses. A bundle is never "
      "asked whether to grant (ADR-0030 §1)."]),
]


def build():
    c = Canvas(ID, "The admit path: decide, then order, then effect",
               "Every effect an agent causes passes eight steps on one replica of the reference mechanism. Steps 1–6 "
               "decide against one state snapshot; step 7 orders the admit in the Paxos log and re-checks it at its log "
               "position; step 8 performs the effect, only after commit. Denials leave at every step and are recorded "
               "but never ordered. `admit ⟺ floor_permit ∧ ¬bundle_deny` (ADR-0030 §1).",
               W, "mechanism/README.md (steps 1–8); mechanism/crates/topak-node/src/mechanism.rs (`act`, `admit`, "
               "`effect`, `record_denial`, `apply_committed`); topak-core/src/admit.rs, state.rs (`check_live`, "
               "`apply_admit`, `Entry`, `MechanismDeny`), lift.rs; ToO rev 11 §4.1, §4.2, §15; ADR-0015 (with E1); "
               "ADR-0020; ADR-0003 A1, A2; ADR-0022 §2; ADR-0030 §1, §4; ADR-0031 §5, E1; ADR-0032 §2; ADR-0033 §1–§4, A6; "
               "ADR-0039 §1, §2; ADR-0041 §2; ADR-0042 §2, §3, §5; ADR-0044; ADR-0045 T-0045-1; GAPS-AND-ASSUMPTIONS "
               "G5, G8; G7 §1.1, §2.7")
    y0 = c.y
    # columns
    AX, AW = c.x0, 1180               # phase regions
    ax, aw = AX + 76, AW - 104         # step cards (badge sits left of them)
    BX, BW = AX + AW + 90, 690         # deny lane
    bx, bw = BX + 24, BW - 48
    bus = BX + BW + 34                 # denial bus
    CX = bus + 70
    CW = c.x1 - CX

    # status strip
    sy = y0
    c.text(c.x0, sy + 15, "Records this path rests on", 15, "faint", bold=True)
    px = c.x0 + 240
    for lab, key, extra in [("ADR-0015", "accepted", "C2"), ("ADR-0033 §4", "accepted", ""),
                            ("ADR-0030", "accepted", "C1"), ("ADR-0020", "accepted", ""),
                            ("ADR-0003 A2", "accepted", "C1"), ("ADR-0039", "accepted", "C4"),
                            ("ADR-0044", "accepted", "C1"), ("ADR-0005 (Kafka)", "proposed", ""),
                            ("genesis floor text", "draft", ""), ("bundle `policies/`", "draft", "placeholder"),
                            ("the reference", "built", "evidence, rung 0")]:
        c.text(px, sy + 15, lab, 13.5, "ink", bold=True)
        px += text_width(lab, 13.5, True) + 8
        px += c.status(px, sy, key, extra) + 22
    y = sy + 62

    # ---- phase 1: decide
    dec_top = y
    y += 36
    rows = []
    for (n, title, acc, body, dt, db) in STEPS:
        h1 = c.card(ax, 0, aw, title, body, accent=acc, draw=False, size=14)
        h2 = c.card(bx, 0, bw, dt, db, accent="red", draw=False, size=13.5, tint=False)
        h = max(h1, h2)
        rows.append((y, h))
        c.card(ax, y, aw, title, body, accent=acc, h=h, size=14)
        c.card(bx, y, bw, dt, db, accent="red", h=h, size=13.5, tint=False, dash="6 4")
        _badge(c, ax - 50, y + 4, n, acc)
        c.arrow([(ax + aw, y + 34), (bx, y + 34)], "red", dash="7 5", label="deny", lpos=0.5, loff=(0, -14))
        c.line(bx + bw, y + h / 2, bus, y + h / 2, "red", sw=2, dash="7 5")
        y += h + 34
    dec_bot = y - 34 + 26
    c.region(AX, dec_top, AW, dec_bot - dec_top,
             "Decide · the deciding replica, against one state snapshot (B2 membrane)", "teal", size=15)
    for (ry, rh), (ny, nh) in zip(rows, rows[1:]):
        c.arrow([(ax + 40, ry + rh), (ax + 40, ny)], "teal", sw=2.4)

    # ---- phase 2: order
    y = dec_bot + 50
    ord_top = y
    y += 36
    c.arrow([(ax + 40, rows[-1][0] + rows[-1][1]), (ax + 40, y)], "violet", sw=2.4,
            label="floor permit ∧ bundle allow", lpos=0.42, loff=(150, 0))
    s7_top = y
    h7t = c.card(ax, y, aw, "Order: propose `Admit` → Paxos → apply with re-check", [
        "Deciding and ordering are **separated in time** (ADR-0033 §4; ADR-0015 E1). The admit carries its decision, "
        "and the floor and bundle are **not re-run** at apply; the mechanism state is.",
    ], accent="violet", size=14, draw=False, bullets=False)
    sub_y = y + h7t + 4
    sw3 = (aw - 2 * 18 - 2 * 40) / 3
    subs = [
        ("propose `Entry::Admit`", ["Re-proposed under one id every 750 ms, up to a 5 s deadline; the state machine "
                                    "applies an id at most once."]),
        ("commit at slot `i`", ["Crash-recovery Multi-Paxos over 3 replicas; promises and votes fsynced to the WAL "
                                "before any reply leaves (ADR-0033 §3)."]),
        ("apply at slot `i`: re-check", ["`check_live` again at the log position; the parameter digest; for "
                                         "`Actuate`/`Report` under a Thinker, the deterministic half of `live(o)`."]),
    ]
    sh = max(c.card(0, 0, sw3, t, b, accent="violet", draw=False, size=13.5, bullets=False) for t, b in subs)
    vy = sub_y + sh + 34
    void_body = ["Fails the re-check (fenced between decision and commit; decided under other parameters; no cell "
                 "Observer covers the seat at commit): **ordered, recorded, without effect**. Returned as "
                 "`NotCommitted`, and so recorded as a denial too."]
    vh = c.card(0, 0, aw - 36, "Void", void_body, accent="red", draw=False, size=13.5, bullets=False)
    h7 = (vy + vh + 18) - y
    c.rect(ax, y, aw, h7, "violet", tint=True)
    c.blocks.append((ax, y, ax + aw, y + h7, "card step7"))
    c.text(ax + 16, y + 16 + 14, "Order: propose `Admit` → Paxos → apply with re-check", 16, "violet", bold=True)
    c.para(ax + 16, y + 40, aw - 32, "Deciding and ordering are **separated in time** (ADR-0033 §4; ADR-0015 E1). "
           "The admit carries its decision, and the floor and bundle are **not re-run** at apply; the mechanism state is.",
           14)
    for i, (t, b) in enumerate(subs):
        sx = ax + 18 + i * (sw3 + 40)
        c.card(sx, sub_y, sw3, t, b, accent="violet", h=sh, size=13.5, bullets=False, tint=False)
        if i:
            c.arrow([(sx - 40, sub_y + sh / 2), (sx, sub_y + sh / 2)], "violet", sw=2)
    c.card(ax + 18, vy, aw - 36, "Void", void_body, accent="red", h=vh, size=13.5, bullets=False, tint=False, dash="6 4")
    lx = ax + 18 + 2 * (sw3 + 40) + sw3 / 2
    c.arrow([(lx, sub_y + sh), (lx, vy)], "red", dash="7 5", label="re-check fails", lpos=0.5, loff=(-62, 0))
    _badge(c, ax - 50, y + 4, "7", "violet")
    y += h7
    # step-7 deny card
    d7 = c.card(bx, s7_top, bw, "`NotCommitted`", [
        "The admit was voided at apply, or not committed before the 5 s deadline.",
        "**Ordering is not authorization**: a void admit is in the log, and a denial still is not."],
        accent="red", size=13.5, tint=False, dash="6 4")
    c.arrow([(ax + aw, s7_top + 34), (bx, s7_top + 34)], "red", dash="7 5", label="deny", lpos=0.5, loff=(0, -14))
    c.line(bx + bw, s7_top + d7 / 2, bus, s7_top + d7 / 2, "red", sw=2, dash="7 5")
    ord_bot = y + 26
    c.region(AX, ord_top, AW, ord_bot - ord_top, "Order · the Paxos log (P), the ordering authority", "violet",
             size=15)

    # ---- phase 3: effect
    y = ord_bot + 50
    eff_top = y
    y += 36
    c.arrow([(ax + 40, s7_top + h7), (ax + 40, y)], "teal", sw=2.4, label="`Applied::Admitted { seq }`",
            lpos=0.45, loff=(130, 0))
    s8_top = y
    effects = [
        ("`Read` · `Consult`", "teal", ["Bytes from the content-addressed corpus store, checked against their address. "
                                        "`Consult` is **ingress, no effect** (ADR-0040)."]),
        ("`Draft`", "teal", ["Write into the round-scoped workspace `ws-<seat>-e<epoch>-r<round>`, on the deciding "
                             "replica only (workspaces are not replicated, G9)."]),
        ("`Invoke` · `Actuate` → downstream MCP tool", "brown",
         ["The tool host spawns `name@digest`, checks binary and schema digests, cleared environment, workspace as "
          "cwd. Hermeticity and channel fidelity are **not checked** (G4, G19).",
          "`Actuate` leaves a mechanism-written record (ADR-0042 §3): `returned`, `failed`, or `unknown` if the round "
          "sealed first."]),
        ("`Emit` · `Report` → Kafka round topic", "amber",
         ["Written only after commit, carrying the admit's **log index**, the lease **fence** and the per-lease "
          "**sequence number** (ToO §4.2).",
          "Topic `topak.<chain>.<domain>.<seat>.e<epoch>.r<round>` (ADR-0003 A1). `Submit` and `Vote` have no "
          "outside effect: the admit is the record (F3 for a vote)."]),
    ]
    ew = (aw - 18 * 2 - 24) / 2
    eh1 = max(c.card(0, 0, ew, t, b, accent=a, draw=False, size=13.5) for t, a, b in effects[:2])
    eh2 = max(c.card(0, 0, ew, t, b, accent=a, draw=False, size=13.5) for t, a, b in effects[2:])
    head = c.card(0, 0, aw - 32, "Effect: after commit, on the deciding replica only", [
        "A crash between commit and effect leaves an admit with no effect, which is safe: **absence of effect is not "
        "an event** (ADR-0015). Effects are exactly {tool invocation, principal emission}."],
        accent="teal", draw=False, bullets=False, size=14)
    h8 = head + eh1 + eh2 + 24 + 18
    c.rect(ax, y, aw, h8, "teal", tint=True)
    c.blocks.append((ax, y, ax + aw, y + h8, "card step8"))
    c.text(ax + 16, y + 30, "Effect: after commit, on the deciding replica only", 16, "teal", bold=True)
    c.para(ax + 16, y + 40, aw - 32, "A crash between commit and effect leaves an admit with no effect, which is "
           "safe: **absence of effect is not an event** (ADR-0015). Effects are exactly {tool invocation, principal "
           "emission}.", 14)
    ey = y + head
    for i, (t, a, b) in enumerate(effects):
        ex = ax + 18 + (i % 2) * (ew + 24)
        eyy = ey if i < 2 else ey + eh1 + 24
        c.card(ex, eyy, ew, t, b, accent=a, h=eh1 if i < 2 else eh2, size=13.5, tint=False)
    _badge(c, ax - 50, y + 4, "8", "teal")
    y += h8
    eff_bot = y + 26
    c.region(AX, eff_top, AW, eff_bot - eff_top, "Effect · reaches the world only as an admit (B3 typed effect)",
             "teal", size=15)

    # ---- denial sink
    sink_y = s8_top
    sh_ = c.card(bx, sink_y, bw, "Denials are not ordered, and they are recorded", [
        "A denied effect never crosses the boundary; a denial changes no state, so it is **never proposed** "
        "(ADR-0015; ADR-0033 §4).",
        "**Recorded** (ADR-0020: the replayable record includes actions attempted and denied): written unordered, by "
        "the deciding replica, content reduced to digests (ADR-0004), and logged locally with attribution.",
        "**Round open** → the principal's round topic.",
        "**Round sealed** → the round's `after` companion (ADR-0003 A2, confirmation-required C1): denials only, same "
        "subject and round, erased with it; at most `after_topic_limit` records (dev: 64), then **one overflow marker**.",
        "Finding 11: the reference first dropped this clause; review caught it (ToO §15).",
    ], accent="red", size=13.5)
    c.line(bus, rows[0][0] + rows[0][1] / 2, bus, sink_y - 40, "red", sw=2, dash="7 5")
    c.arrow([(bus, sink_y - 40), (bus, sink_y - 16), (bx + bw / 2, sink_y - 16), (bx + bw / 2, sink_y)], "red",
            dash="7 5")
    # Kafka sink below denial card
    ky = sink_y + sh_ + 70
    kh = c.card(bx, ky, bw, "Kafka · transport, `acks=all`", [
        "Neither the ordering authority (the Paxos log) nor the system of record (the archive, not built). "
        "**ADR-0005 is still Proposed**; the K row is carried as a debt (ADR-0033 §2).",
        "Kafka has no seal primitive: the mechanism refuses emission after the round ends and appends a seal marker.",
    ], accent="amber", size=13.5, status="proposed", status_extra="ADR-0005")
    c.region(BX, dec_top, BW, max(eff_bot, ky + kh + 26) - dec_top, "Denial lane · local, unordered", "red",
             size=15)
    c.arrow([(bx + bw / 2, sink_y + sh_), (bx + bw / 2, ky)], "red", dash="7 5", label="deny records",
            lpos=0.45, loff=(0, 0))
    mid = (AX + AW + BX) / 2
    e_y = ey + eh1 + 24 + 40
    c.arrow([(ax + 18 + ew + 24 + ew, e_y), (mid, e_y), (mid, ky + 40), (bx, ky + 40)], "amber", sw=2.2)
    c.label(mid, (e_y + ky + 40) / 2, "emissions,\n`Actuate` records", "amber", 12.5)

    # ---- column C: notes
    cy = dec_top
    cy += _timeline(c, CX, cy, CW) + 30
    c.text(CX, cy + 19, "What the log orders: **ordering is not authorization**", 19, "violet", bold=True)
    cy += 30
    cy += c.para(CX, cy, CW, "Subtractions need no quorum, but if they change replicated state they must be ordered, or "
                 "replicas disagree about what is live (ADR-0033 §4; finding 3). Every `Entry` kind in "
                 "`topak-core/src/state.rs`:", 14, "muted") + 8
    cols = [("`Entry`", CW * 0.17), ("Proposed by", CW * 0.27), ("What authorizes it", CW * 0.40),
            ("Forensic class", CW * 0.16)]
    rows_t = [
        {"group": "Grants and admits", "accent": "blue"},
        ["`Grant`", "operator `grant`", "Operator socket, unsigned (PROVISIONAL, G5); apply checks seat kind, one live "
         "lease per principal, `ttl ≤ T_persona`; decide refuses an unverified bundle revision", "—"],
        ["`Renew`", "operator `renew`", "As `Grant`; keeps the round and the bundle, refuses a changed rung "
         "(ADR-0031 A1)", "—"],
        ["`Admit`", "the deciding replica", "`floor_permit ∧ ¬bundle_deny` at decide; mechanism checks again at apply",
         "F1; F3 for a vote; F5 under X1"],
        {"group": "Subtractions: ordered, approved by nobody", "accent": "green"},
        {"cells": ["`EndRound`", "any replica (expiry); the seat (abstain, Build only); operator `end_round`",
                   "None needed: it removes authority", "F2 (expiry eviction, e-stop)"], "accent": "green"},
        {"cells": ["`Revoke`", "operator `revoke` (a principal, Persona or confinement digest)",
                   "None needed (ADR-0031 §5 R3)", "F2"], "accent": "green"},
        {"cells": ["`EpochIncrement`", "operator `fence_epoch`", "None needed: the fleet fence (ADR-0031 §5)", "F2"],
         "accent": "green"},
        {"group": "Authority facts", "accent": "brown"},
        ["`Issue`", "operator relays an anchor issuance", "`Authentic` signatures and the rules floor "
         "(`validate_issuance`, ADR-0026)", "F4"],
        ["`GatesPassed`", "operator `gates_passed`", "Asserted: who runs the gates is unspecified (PROVISIONAL, G8)", "—"],
        ["`BreakGlassApprove`", "operator relays a signed approval", "A break-glass roster key; quorum per (seat, epoch)",
         "F5 is the admit under it"],
    ]
    cy += c.table(CX, cy, cols, rows_t, size=13.5, accent="violet") + 34

    hh = c.card(CX, cy, CW, "Observer coupling: `live(o)` at decide and at apply (ADR-0039 §1, §2; ADR-0041 §2)", [
        "**At decide**, the lift computes `live(o)` for the seat's cell Observers: a live Observer lease, a heartbeat "
        "heard within `T_obs` **on this replica's clock**, and `seq(t) − mark(o, r) < K`. Floor entry `R3-observer-live` "
        "forbids `Actuate` and `Report` under a Thinker without it, break-glass included.",
        "**At apply**, only the deterministic half is re-checked: `T_obs` is a per-replica clock, so it cannot be "
        "(ToO §15, 2026.09.29 findings).",
        "`Consult` is not coupled; an Observer's own heartbeats are not coupled. Values are placeholders "
        "(`T_obs` 5000 ms, `K` 8; `floor/genesis-values.json`).",
    ], accent="pink", size=14)
    cy += hh + 26
    hh = c.card(CX, cy, CW, "The audit chain every effect carries (ToO §4.1; ADR-0015)", [
        "effect → admit → floor ∧ bundle, at the lease's bundle revision → rules epoch → issuance → ADR-0025's intent "
        "axiom. **No link is assumed except the last.**",
        "Each link is a field of the committed admit (below), which is forensic class F1 (ADR-0028).",
    ], accent="blue", size=14)
    cy += hh + 26
    c.text(CX, cy + 19, "The committed admit: `AdmitRecord` (mechanism.rs, step 7)", 19, "blue", bold=True)
    cy += 34
    cy += c.table(CX, cy, [("Field", CW * 0.2, {"mono": True}), ("What it holds", CW * 0.8)], [
        ["seat", "The seat the session names"],
        ["lease", "The lease's fence: the log index of its grant"],
        ["epoch", "The epoch the request carried"],
        ["action", "The admitted action with its target; for `Actuate`, the tool id, the inputs **by digest**, and "
                   "whether the floor admitted it through `X1-break-glass`"],
        ["input", "Digest of the frozen input both tiers evaluated (ADR-0030 §4)"],
        ["floor", "Digest of the linked floor text"],
        ["schema", "Digest of schema S"],
        ["floor_reasons", "The permitting policy ids"],
        ["bundle", "The bundle revision that allowed: the lease's"],
        ["engine", "Which bundle engine decided: sidecar or local WASM"],
        ["params", "Digest of the mechanism parameters; a mismatch at apply voids the admit"],
        ["decided_by", "The deciding replica, which alone performs the effect"],
    ], size=13.5, accent="blue") + 30
    c.card(CX, cy, CW, "What this path does not show (ADR-0033 §1, §3, §6)", [
        "**Confinement**: the MCP front door makes the alphabet the whole protocol, not the whole channel. Every lease "
        "is rung 0; every principal is `Mediated`.",
        "**A Byzantine replica**: replicas are crash-recovery. The apply re-check stops **stale** admits, not **forged** "
        "ones; replica authentication is unbuilt (T-0045-1).",
        "The reference is **evidence, not the verified object**: never promoted, in no TCB.",
    ], accent="red", size=14, tint=False, dash="6 4")

    # legend
    ly = c.ymax + 40
    c.legend(c.x0, ly, [
        ("box", "teal", "mechanism step"), ("box", "blue", "floor tier"), ("box", "amber", "bundle tier / Kafka"),
        ("box", "violet", "consensus (P)"), ("box", "red", "denial, void, gap"),
        ("arrow", "teal", "the admit path"), ("arrow", "red", "denial: not ordered", "7 5"),
    ])
    return c


def _badge(c, x, y, n, acc):
    c.rect(x, y, 38, 38, acc, tint=False, rx=19, sw=0, fill_token=acc)
    c.text(x + 19, y + 26, n, 20, "bg", anchor="middle", bold=True)


def _timeline(c, x, y, w):
    """Deciding vs ordering: a revocation can commit between an admit's decision and its commit."""
    c.text(x, y + 19, "Decided under epoch `e`, committed under `e+1`", 19, "violet", bold=True)
    y0 = y + 30
    h = c.para(x, y0, w, "An admit decided under epoch `e` can commit after a fence has moved the epoch on. The mechanism "
               "checks therefore run twice; the second run uses the state at the entry's log position (ADR-0033 §4).",
               14, "muted")
    ty = y0 + h + 70
    x0, x1 = x + 30, x + w - 40
    c.line(x0, ty, x1, ty, "violet", sw=2.4)
    c.arrow([(x1 - 2, ty), (x1 + 20, ty)], "violet", sw=2.4)
    c.text(x1 + 22, ty - 14, "log / time", 13, "faint", anchor="end")
    marks = [
        (0.06, "decide on replica 1", "steps 1–6 pass under epoch `e`", "teal", -1),
        (0.38, "slot `i`: `EpochIncrement`", "operator `fence_epoch`: epoch → `e+1`", "green", 1),
        (0.66, "slot `i+1`: `Admit` commits", "apply re-runs `check_live`: `FencedEpoch`", "violet", -1),
        (0.88, "void", "ordered, recorded, no effect", "red", 1),
    ]
    for f, t1, t2, acc, side in marks:
        mx = x0 + (x1 - x0) * f
        c.rect(mx - 7, ty - 7, 14, 14, acc, tint=False, rx=7, sw=0, fill_token=acc)
        if side < 0:
            c.text(mx, ty - 38, t1, 14, acc, anchor="middle", bold=True)
            c.text(mx, ty - 19, t2, 13, "muted", anchor="middle")
        else:
            c.text(mx, ty + 29, t1, 14, acc, anchor="middle", bold=True)
            c.text(mx, ty + 48, t2, 13, "muted", anchor="middle")
    return ty + 60 - y
