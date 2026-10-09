"""D1 — The admit path: decide, then order, then effect."""
import re

import lib
from lib import AMENDED_G11, STATUS, Canvas, text_width

ID, SLUG = "D1", "admit-pipeline"

W = 3200

# (number, title, accent, body, deny-title, deny-body, status)
STEPS = [
    ("1", "Session → `ActionRequest`", "teal",
     ["The bearer token on the replica's agent socket names the **seat**, the **lease** (its fence, a log index) and "
      "the **epoch**; every action carries all three (ADR-0022 §2).",
      "A launched guest has no token: at rung 1 the launcher's bridge is its session; under an attested session key "
      "each action carries the guest's **session proof**, checked here against the action (I14, I41; ADR-0033 A7, "
      "ratified Batch 29).",
      "**An emergency seat has no token path** (ADR-0052 §1, provisional): every action under its lease carries a proof "
      "signed with the person's key, checked here and at apply. The agent socket's protocol carries no proof, so at "
      "the reference the person acts in-process (I48; G10 item 92).",
      "`SubmitWorkspace` becomes `Submit(digest)` over the round workspace; an abstain from a Run seat is refused "
      "here, before ordering (ADR-0042 §5)."],
     "No session: `UnknownLease`",
     ["Names no principal and no round, so **there is no round record for it**: an authentication event logged at this "
      "replica's socket (ADR-0003 A2 note; register G5).",
      "`Other`: a bearer token used on an emergency seat's lease (ADR-0052 §1)."], None),
    ("2", "Local expiry · **liveness**", "teal",
     ["The lease TTL runs on **this replica's monotonic clock** from when it applied the grant, read with the asymmetric "
      "margin, so it elapses early (ADR-0032 §2). No local observation of the grant counts as expired: fail closed.",
      "**A race, fixed** (ADR-0033 A13, Batch 33): the observation was recorded after the state lock was released, so a "
      "lease just granted could be ended as expired. It is now recorded before (G10 §3, result 2).",
      "A liveness check only. **The fence in step 3 carries safety.**"],
     "`LeaseExpired`",
     ["The replica also proposes `EndRound(Expired)`: a subtraction, ordered so replicas agree, approved by nobody "
      "(ADR-0033 §4; ADR-0031 E1)."], None),
    ("3", "Mechanism checks: epoch fence, lease, alphabet", "teal",
     ["`check_live`, in order: the lease is known and is this seat's; **lease epoch = current epoch** (the fence); "
      "request epoch = lease epoch; lease rules epoch = current rules epoch; lease not ended; action in the lease's "
      "alphabet; round bound not reached; action preconditions (`Submit` once; `Vote` only on a submitted artifact "
      "whose gates passed).",
      "Then **channel fidelity**: under an attested lease whose Run profile says P4 passes, an `Actuate` naming a "
      "tool not hosted as Wasm is refused (`channel_fidelity`; ADR-0034 A2, ratified Batch 30; ADR-0033 A8, Batch 31).",
      "**Mechanism, not policy**: the floor never decides whether an epoch is current (ADR-0030 §4)."],
     "Mechanism deny",
     ["`FencedEpoch`, `RequestEpochMismatch`, `FencedRulesEpoch`, `LeaseEnded`, `NotInAlphabet`, "
      "`RoundBoundReached`, `ArtifactNotSubmitted`, `ArtifactAlreadySubmitted`, `GatesNotPassed`, "
      "`EvidenceMismatch`, `AlreadyPromoted`; `WrongSeat` (the token's lease is another seat's); `BadHeartbeat` "
      "(a heartbeat from a non-observer, naming no round it watches, above what exists or below its last "
      "watermark); `Other`, for a Run tool not held to its channel.",
      "With steps 1, 2 and 4, **sixteen `MechanismDeny` variants, unchanged by the 10.05 rebuild**: its new refusals "
      "are `Other` with a reason (`state.rs`)."], None),
    ("4", "Syntactic lift → **one frozen input**", "teal",
     ["Mechanical and total: every fact is a set membership, an equality or a path-syntax check; nothing interprets "
      "meaning (ADR-0007, ADR-0018 validator side).",
      "Principal, action, resource, context and the complete entity slice in schema S's shape, **plus the bundle's "
      "view built from the same facts**. Resolved once; the bundle may not re-fetch (ADR-0030 §4). Its digest goes "
      "into the admit.",
      "**Label facts** (ADR-0047 §4): for a `Consult` or `Actuate` the deciding replica computes, from the allowlist "
      "entry of the lease's revision and the round's labels, the round's `clearSet`, the handles' labels, whether a "
      "destination is a literal, whether the entry is `outward` (derived, never declared: ADR-0049 §4), the result's "
      "label and its delivery mode. They enter S as attributes; no policy computes one, and the admit carries them.",
      "An emergency seat's call is decided against the revision that holds its entry in the envelope (ADR-0052 §2).",
      "`observerLive` is `live(o)`, computed here (ADR-0039 §1)."],
     "Lift refused",
     ["A request the lift cannot build is a mechanism deny: for `Submit`, an artifact that is not the workspace digest.",
      "`Other`: a handle that names nothing in this round for this principal (ADR-0049 §3); an `Actuate` with no "
      "label facts, which is refused and not lifted as inside (ADR-0047 §4)."], None),
    ("5", "Floor: Cedar, linked · **can permit**", "blue",
     ["`floor/proposed/workflow-floor.cedar` (30 policies, 123 cases), its schema and `floor/genesis-values.json`, "
      "compiled in **by path**; the replica refuses to start unless their bytes match the gated digests (ADR-0033 §2). "
      "**Since 2026.10.08 the reference links the `workflow` stage, which is [[amber|Proposed]] and not in force**; "
      "the floor in force is the `emergency` stage, 28 policies (G11 §2.2, item 102). `workflow` adds `Route`, `R8`, "
      "`R9`, and `R3` over the `orchestrator` kind (ADR-0041 A4, pending).",
      "New entries: `R5` to `R7` forbid an outward `Actuate` over labels (read then send, steered destination, "
      "replayed content); `B10` lets an `emergency` seat `Actuate`, admitted by `R1` over its envelope. "
      "**`X1-break-glass` is retired**: one exception, `X2` (ADR-0041 A1 to A3; ADR-0052).",
      "S is enforced on every request: a non-conforming input is a deny (ADR-0030 §4)."],
     "Floor deny · short-circuits",
     ["`Floor([forbids that fired])`, or `FloorNoPermit`: outside every envelope (finding 10).",
      "`FloorError`: **any** evaluation error is a deny, since Cedar skips an erroring `forbid` (ADR-0030 §1).",
      "The bundle is never consulted."], "genprov"),
    ("6", "Bundle: OPA sidecar | WASM · **can only refuse**", "amber",
     ["`data.topak.bundle.allow`, counted only from **the revision the lease names**, and only if that revision's "
      "signature verified under the rules' `bundle_keys` (ADR-0044; built, ADR-0033 A6).",
      "**A bundle loads only if its allowlist is well-formed** (ADR-0049, W1 to W9 checked at load; I33); the bundle "
      "tier checks each handle among an `Actuate`'s inputs against the entry's `accepts` (ADR-0047 §3).",
      "Sidecar unreachable or serving another revision → the in-process WASM engine decides **iff** it holds that "
      "revision; otherwise refuse. Every admit records which engine decided."],
     "`Bundle(reason)`",
     ["Deny, error, undefined, absent or unreachable: anything but an affirmative `true` refuses. A bundle is never "
      "asked whether to grant (ADR-0030 §1)."], None),
]


def _boldfix(s):
    """Split a **bold** span that holds `code` into bold runs around the code (lib cannot nest them)."""
    segs = s.split("**")
    if len(segs) % 2 == 0:
        return s
    out = []
    for k, seg in enumerate(segs):
        if k % 2 == 0:
            out.append(seg)
        elif "`" in seg:
            parts = re.split(r"(`[^`]+`)", seg)
            out.append("".join(p if p.startswith("`") else (f"**{p}**" if p.strip() else p) for p in parts))
        else:
            out.append(f"**{seg}**")
    return "".join(out)


def build():
    orig = lib.parse
    lib.parse = lambda s: orig(_boldfix(s))
    try:
        return _build()
    finally:
        lib.parse = orig


def _build():
    c = Canvas(ID, "The admit path: decide, then order, then effect",
               "Every effect an agent causes passes eight steps on one replica of the reference mechanism. Steps 1–6 "
               "decide against one state snapshot; step 7 orders the admit in the Paxos log and re-checks it at its log "
               "position; step 8 performs the effect, only after commit. Denials leave at every step and are recorded "
               "but never ordered. `admit ⟺ floor_permit ∧ ¬bundle_deny` (ADR-0030 §1). An operator's signed request "
               "and an emergency activation reach the log by the same decide, order and re-check, with no bundle tier "
               "(below the effect; ADR-0050 and ADR-0052, provisional).",
               W, "mechanism/README.md (steps 1–8, Operators, Break-glass); mechanism/crates/topak-node/src/mechanism.rs "
               "(`act`, `admit`, `effect`, `record_denial`, `apply_committed`, `control`, `record_control`, `activate`, "
               "`open_round`, `resolve_handles`, `InFlight::record`); topak-core/src/admit.rs (`DenyReason`), state.rs "
               "(`check_live`, `apply_admit`, `apply_grant`, `apply_activate`, `control_facts`, `not_a_first_seating`, "
               "`channel_fidelity`, `Entry`, `Applied`, `AdmitRecord`, `MechanismDeny`, `State`), control.rs "
               "(`ControlFacts::permitted`), labels.rs, lift.rs (`lift`, `lift_control`), types.rs (`SeatKind`); "
               "git diff 7075169..HEAD of those files; mechanism/launch.rs; floor/proposed/emergency-floor.cedar, "
               "workflow-floor.cedar; state.rs `WorkflowLoad`, `WorkflowGrant`, `WorkflowLoaded`, `WorkflowFailed`; "
               "ADR-0054 §1, §2, §8 and ADR-0055 §1, §2 (Proposed); ADR-0033 A16, A17 (pending); ADR-0041 A4; I49; "
               "G11 §2.2, item 102; ToO rev 15 §2.10, §2.11, §3.3, §4.1, §4.2, §7.10, §15; ADR-0005 (B27); ADR-0015 (with E1); ADR-0020; "
               "ADR-0003 A1, A2; ADR-0022 §2; ADR-0030 §1, §4, A3; ADR-0031 §5, E1; ADR-0032 §2; ADR-0033 §1–§4, A6, "
               "A7, A8, A9, A10–A15; ADR-0034 §1, §3, A2; ADR-0039 §1, §2, A2; ADR-0041 §2, A1–A3; ADR-0042 §2, §3, §5, "
               "A1, A2; ADR-0044; ADR-0045 T-0045-1, T-0045-28; ADR-0047 §1–§5; ADR-0048 §2; ADR-0049 §3–§5; "
               "ADR-0050 §2–§6; ADR-0052 §1–§5; spec/Mechanism.tla, spec/Mechanism-trace-results-2026.10.05.txt; "
               "GAPS-AND-ASSUMPTIONS G4, G5, G8, G14, G19, I14, I23, I33, I41, I44–I48, finding 19; G10 §2.2, §2.5, "
               "§3 (results 2, 8), §7 items 46, 92, 93; derived/topak-format-and-schema-inventory-2026.10.03.md §5.1, "
               "§5.2, findings 12, 29")
    c.note = AMENDED_G11
    y0 = c.y
    # columns
    AX, AW = c.x0, 1180               # phase regions
    ax, aw = AX + 76, AW - 104         # step cards (badge sits left of them)
    BX, BW = AX + AW + 90, 690         # deny lane
    bx, bw = BX + 24, BW - 48
    bus = BX + BW + 34                 # denial bus
    CX = bus + 70
    CW = c.x1 - CX

    # status strip, wrapped
    sy = y0
    c.text(c.x0, sy + 15, "Records this path rests on", 15, "faint", bold=True)
    px0 = c.x0 + 240
    px = px0
    for lab, key, extra in [("ADR-0015", "accepted", "C2"), ("ADR-0033 §4", "accepted", ""),
                            ("ADR-0030", "accepted", "C1"), ("ADR-0020", "accepted", ""),
                            ("ADR-0003 A2", "accepted", "C1"), ("ADR-0039", "accepted", "C4"),
                            ("ADR-0044", "accepted", "C1"), ("ADR-0005 (Kafka)", "accepted", "C4 · Batch 27"),
                            ("ADR-0047, 0048, 0049", "accepted", "C4 · Batch 34"),
                            ("ADR-0050, ADR-0052", "provisional", "C1, C3, C4"),
                            ("the floor's `emergency` stage", "genprov", "ADR-0030 A3"),
                            ("bundle `policies/`", "draft", "placeholder"),
                            ("the reference", "built", "evidence · rung 0 as deployed")]:
        wl = text_width(lab, 13.5, True) + 8
        wp = text_width(STATUS[key][0] + (f" · {extra}" if extra else ""), 11.5, True) + 18
        if px + wl + wp > c.x1:
            px = px0
            sy += 34
        c.text(px, sy + 15, lab, 13.5, "ink", bold=True)
        px += wl
        px += c.status(px, sy, key, extra) + 22
    y = sy + 62

    # ---- phase 1: decide
    dec_top = y
    y += 36
    rows = []
    for (n, title, acc, body, dt, db, st) in STEPS:
        h1 = c.card(ax, 0, aw, title, body, accent=acc, draw=False, size=14, status=st)
        h2 = c.card(bx, 0, bw, dt, db, accent="red", draw=False, size=13.5, tint=False)
        h = max(h1, h2)
        rows.append((y, h))
        c.card(ax, y, aw, title, body, accent=acc, h=h, size=14, status=st)
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
                                         "`Actuate`/`Report` under a Thinker, the deterministic half of `live(o)`; "
                                         "channel fidelity; for a `Consult` or `Actuate`, that it carries label facts "
                                         "and that the round's `clearSet` is still the one the floor was asked about; "
                                         "under a session key, or an emergency seat's person key, the proof with a "
                                         "fresh counter."]),
    ]
    sh = max(c.card(0, 0, sw3, t, b, accent="violet", draw=False, size=13.5, bullets=False) for t, b in subs)
    vy = sub_y + sh + 34
    void_body = ["Fails the re-check (fenced between decision and commit; decided under other parameters; no cell "
                 "Observer covers the seat at commit; a Run tool not held to its channel; **decided against a "
                 "`clearSet` the round has since grown past**, refused and not re-decided (ADR-0047 §4); a Run "
                 "delivery with no label; a proof that is not the attested guest's or the person's, or a replayed "
                 "counter): **ordered, recorded, without effect**. `Applied::Rejected`, returned as `NotCommitted`, "
                 "and so recorded as a denial too."]
    vh = c.card(0, 0, aw - 36, "Void", void_body, accent="red", draw=False, size=13.5, bullets=False)
    fold_body = ["An admit that applies **folds its labels on every replica, in log order**: an `Actuate` result's "
                 "label by its `seq`, a `Consult`'s by its reference, and either into `clearSet` when it is delivered "
                 "clear. `clearSet` only grows, and a reader with the log can recompute it (ADR-0047 §4). The fold is "
                 "at admit, before the call returns: a failed call still adds its label, which is sound and coarser "
                 "than the record (I46 (b)). Apply re-checks `clearSet` and takes the other facts as the deciding "
                 "replica's (G10 item 93)."]
    fh = c.card(0, 0, aw - 36, "The label fold (ADR-0047 §4; I46)", fold_body, accent="teal", draw=False, size=13.5,
                bullets=False)
    fy_ = vy + vh + 18
    h7 = (fy_ + fh + 18) - y
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
    c.card(ax + 18, fy_, aw - 36, "The label fold (ADR-0047 §4; I46)", fold_body, accent="teal", h=fh, size=13.5,
           bullets=False, tint=False)
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
    c.arrow([(ax + 40, s7_top + h7), (ax + 40, y)], "teal", sw=2.4, label="`Applied::Admitted { seq, promoted }`",
            lpos=0.45, loff=(130, 0))
    s8_top = y
    effects = [
        ("`Read` · `Consult`", "teal", ["Bytes from the content-addressed corpus store, checked against their address. "
                                        "`Consult` is **ingress, no effect** (ADR-0040).",
                                        "A `Consult`'s content is delivered **clear with its label, or as a handle** "
                                        "with no bytes, by the delivery table for the seat's kind (ADR-0047 §2)."]),
        ("`Draft`", "teal", ["Write into the round-scoped workspace `ws-<seat>-e<epoch>-r<round>`, on the deciding "
                             "replica only (workspaces are not replicated, register G9)."]),
        ("`Invoke` · `Actuate` → downstream MCP tool", "brown",
         ["A native tool: the tool host spawns `name@digest`, checks binary and schema digests, cleared environment, "
          "workspace as cwd. Hermeticity is **not checked** (G4), nor a native Run tool's channel (G19).",
          "A hosted Wasm tool's one network capability is the target **its allowlist entry declares in the lease's "
          "revision**, not node configuration (ADR-0033 A9; ADR-0049 §5; I44).",
          "**A handle among the inputs is resolved here**, on the mechanism's side: the tool receives the bytes, the "
          "principal never does (ADR-0047 §3). Only a scalar resolves (I46 (d)).",
          "The result goes back clear with its label, or as a handle with no bytes and no digest. The `Actuate` record "
          "(ADR-0042 §3): `returned`, `failed` or `unknown`; `seatKind` where it said `breakGlass` (A2); four label "
          "fields (A1)."]),
        ("`Emit` · `Report` → Kafka round topic", "amber",
         ["Written only after commit, carrying the admit's **log index**, the lease **fence** and the per-lease "
          "**sequence number** (ToO §4.2).",
          "**The round opens with the tool list**: at grant, before the session exists, the mechanism writes an "
          "opening record with no admit and no sequence number (ADR-0048 §2; ADR-0042 A1).",
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

    # ---- the other two paths into the log: an operator's request, an activation
    y = eff_bot + 60
    op_top = y
    y += 40
    op_top_inner = y
    op_steps = [
        ("Signed request", ["One of six control actions: `Regrant`, `Renew`, `AttestGates` add; `EndRound`, `Revoke`, "
                            "`FenceEpoch` deny. Signed with the operator seat's key, with the fleet epoch and a counter "
                            "(ADR-0050 §3, §4). Checked here, so a forgery is not ordered."]),
        ("Facts → `ControlCtx`", ["The replica computes **thirteen facts** about the operator, the target and the "
                                  "request (`control_facts`): Persona in force, a live lease, a live peer, a fresh "
                                  "sign-on, the target seated and live, the binding, the round, the alphabets, the "
                                  "task's label. The operator supplies none. `lift_control` into S."]),
        ("Floor `C1` to `C9`", ["**No bundle tier**: the nine control entries are the whole envelope. A deny is "
                                "returned to the operator with the floor's reasons and the facts. A `Regrant` at rung 1 "
                                "or above is refused: it would launch a guest, not built (G10 item 88)."]),
        ("`Entry::Control`, re-checked", ["**Every replica** verifies the signature against the seat's key, refuses a "
                                          "replayed counter, **recomputes the facts and refuses if they differ**, and "
                                          "**restates the envelope** (`ControlFacts::permitted`). Then it is written to "
                                          "the operator's round topic, where its peers read it (§6)."]),
    ]
    act_steps = [
        ("Roster signatures", ["One activation: one named person, one round, the round's task by digest and label. "
                               "Members of the break-glass roster sign exactly that (ADR-0052 §2). No reason field: "
                               "why the quorum acted is unknown to the mechanism (§5)."]),
        ("Envelope computed", ["The deciding replica computes what the seat may call: by default every Run entry of "
                               "every revision a seating in force in the domain names, operators' included (I48 (b); "
                               "G10 §3 result 5, item 92). Others take it as given, except a named envelope."]),
        ("`Entry::Activate`, re-checked", ["Every replica counts **distinct roster keys against the issued quorum**, "
                                           "checks the seating is prepared, the person is one it names, the epoch is "
                                           "current and the task's label is within the seating's; then grants one "
                                           "lease and keeps the activation as the F5 record."]),
        ("One round, then nothing", ["No successor and no renewal: an operator's `Regrant` or `Renew` naming it is "
                                     "refused, and any operator of the domain may end or revoke it (ADR-0052 §3). "
                                     "**`BreakGlassApprove` is refused at apply**: X1 is retired."]),
    ]
    gw = 30
    sw4 = (aw - 2 * 18 - 3 * gw) / 4
    oh = max(c.card(0, 0, sw4, t, b, accent="brown", draw=False, size=13.5, bullets=False) for t, b in op_steps)
    ah = max(c.card(0, 0, sw4, t, b, accent="brown", draw=False, size=13.5, bullets=False) for t, b in act_steps)
    c.text(ax + 18, y + 18, "An operator's request (ADR-0050 §4; I47)", 17, "brown", bold=True)
    c.status(ax + 18 + text_width("An operator's request (ADR-0050 §4; I47)", 17, True) + 14, y + 1, "provisional",
             "ADR-0050")
    y += 34
    for i, (t, b) in enumerate(op_steps):
        sx = ax + 18 + i * (sw4 + gw)
        c.card(sx, y, sw4, t, b, accent="brown", h=oh, size=13.5, bullets=False, tint=False)
        if i:
            c.arrow([(sx - gw, y + 30), (sx, y + 30)], "brown", sw=2)
    y += oh + 30
    c.text(ax + 18, y + 18, "An emergency activation (ADR-0052 §2, §3; I48)", 17, "brown", bold=True)
    c.status(ax + 18 + text_width("An emergency activation (ADR-0052 §2, §3; I48)", 17, True) + 14, y + 1,
             "provisional", "ADR-0052")
    y += 34
    for i, (t, b) in enumerate(act_steps):
        sx = ax + 18 + i * (sw4 + gw)
        c.card(sx, y, sw4, t, b, accent="brown", h=ah, size=13.5, bullets=False, tint=False)
        if i:
            c.arrow([(sx - gw, y + 30), (sx, y + 30)], "brown", sw=2)
    y += ah + 30
    boot = ["**Where the rules declare an operator, the unsigned socket is a BOOTSTRAP path that seats and does nothing "
            "else**: an unsigned `Grant` or `Launch` is a first seating; an unsigned renewal, operator end of round, "
            "revocation, fleet fence or gate attestation is refused at apply. A grant that keeps a seat's seated "
            "binding while two operators of its domain are live is a successor, and theirs to make. `prepare_emergency` "
            "stands in for the promotion that prepares an emergency seating. **A first lease from a quorum is not "
            "built**: whoever reaches the socket can seat (ADR-0050 §2; G10 §8). Rules that declare no operator leave "
            "the socket as it was: D-0050-1."]
    bh = c.card(ax + 18, y, aw - 36, "BOOTSTRAP: the unsigned socket stands in for the quorum", boot, accent="red",
                size=13.5, bullets=False, tint=False, dash="6 4")
    y += bh + 18
    op_bot = y + 8
    c.region(AX, op_top, AW, op_bot - op_top, "Two more paths into the log · decided, ordered, re-checked · no bundle "
             "tier", "brown", size=15)

    # ---- denial sink
    sink_y = s8_top
    sh_ = c.card(bx, sink_y, bw, "Denials are not ordered, and they are recorded", [
        "A denied effect never crosses the boundary; a denial changes no state, so it is **never proposed** "
        "(ADR-0015; ADR-0033 §4).",
        "**Recorded** (ADR-0020: the replayable record includes actions attempted and denied): written unordered, by "
        "the deciding replica, content reduced to digests (ADR-0004), carrying `at` (the log index the replica had "
        "applied) and `decided_by`, and logged locally with attribution.",
        "**Round open** → the principal's round topic.",
        "**Round sealed** → the round's `after` companion (ADR-0003 A2, confirmation-required C1): denials only, same "
        "subject and round, erased with it; at most `after_topic_limit` records (dev: 64) **per deciding replica**, the "
        "counter not being replicated (I23), then **one overflow marker**.",
        "Finding 11: the reference first dropped this clause; review caught it (ToO §15).",
    ], accent="red", size=13.5)
    c.line(bus, rows[0][0] + rows[0][1] / 2, bus, sink_y - 40, "red", sw=2, dash="7 5")
    c.arrow([(bus, sink_y - 40), (bus, sink_y - 16), (bx + bw / 2, sink_y - 16), (bx + bw / 2, sink_y)], "red",
            dash="7 5")
    # Kafka sink below denial card
    ky = sink_y + sh_ + 70
    kh = c.card(bx, ky, bw, "Kafka · transport, `acks=all`", [
        "Neither the ordering authority (the Paxos log) nor the system of record (the archive, not built). "
        "**ADR-0005 was ratified 2026.10.04** (Batch 27, C4): the debt ADR-0033 §2's K row carried is discharged.",
        "A reader orders a topic by the log index and sequence number its records carry, not by offsets (ADR-0005 §2).",
        "Kafka has no seal primitive: the mechanism refuses emission after the round ends and appends a seal marker.",
        "**Readers nothing gates**: the mechanism has no read path for topics, so who reads one is the transport's "
        "configuration (G10 item 46).",
    ], accent="amber", size=13.5, status="accepted", status_extra="ADR-0005 · C4")
    c.region(BX, dec_top, BW, max(eff_bot, ky + kh + 26) - dec_top, "Denial lane · local, unordered", "red",
             size=15)
    c.arrow([(bx + bw / 2, sink_y + sh_), (bx + bw / 2, ky)], "red", dash="7 5", label="deny records",
            lpos=0.45, loff=(0, 0))
    mid = (AX + AW + BX) / 2
    e_y = ey + eh1 + 24 + 40
    c.arrow([(ax + 18 + ew + 24 + ew, e_y), (mid, e_y), (mid, ky + 40), (bx, ky + 40)], "amber", sw=2.2)
    c.label(mid, (e_y + ky + 40) / 2, "emissions,\n`Actuate` records,\nopening record", "amber", 12.5)

    # ---- column C: notes
    cy = dec_top
    cy += _timeline(c, CX, cy, CW) + 30
    c.text(CX, cy + 19, "What the log orders: **ordering is not authorization**", 19, "violet", bold=True)
    cy += 30
    cy += c.para(CX, cy, CW, "Subtractions need no quorum, but if they change replicated state they must be ordered, or "
                 "replicas disagree about what is live (ADR-0033 §4; finding 3). Every `Entry` kind in "
                 "`topak-core/src/state.rs`, **sixteen, one of them retired and two for records that are Proposed**. Where the rules declare an operator, "
                 "the unsigned operator requests marked † are refused at apply and the operator's signed `Control` "
                 "carries them (ADR-0050 §4):", 14, "muted") + 8
    cols = [("`Entry`", CW * 0.17), ("Proposed by", CW * 0.27), ("What authorizes it", CW * 0.40),
            ("Forensic class", CW * 0.16)]
    rows_t = [
        {"group": "Grants and admits", "accent": "blue"},
        ["`Grant`", "operator socket `grant` (rung 0); the launcher, on `launch` (rung ≥ 1)",
         "Unsigned. Where the rules declare an operator, a **BOOTSTRAP** first seating, refused for a successor while "
         "two operators of the domain are live. Apply checks seat kind, one live lease per principal, the seat's "
         "declared rung, `ttl ≤ T_persona`, an operator's sign-on, and at rung ≥ 1 **the appraisal, re-checked on "
         "every replica** (A7); never an emergency seat's lease", "—"],
        ["`Renew`", "the launcher, for a guest it launched; operator `renew` †", "As `Grant`; keeps the round and the "
         "bundle, refuses a changed rung (ADR-0031 A1); an attested lease renews only on a fresh appraisal of the "
         "same guest", "—"],
        {"cells": ["`Control`", "an operator's signed request (six actions)",
                   "Floor `C1` to `C9` at decide; at apply the signature, the counter, the facts recomputed and the "
                   "envelope restated. A `Regrant` carries its grant, a `Renew` its renewal (ADR-0050 §4)",
                   "F2 for the three denies"], "accent": "brown"},
        ["`Admit`", "the deciding replica", "`floor_permit ∧ ¬bundle_deny` at decide; mechanism checks and the "
         "`clearSet` again at apply", "F1; F3 for a vote; **F5 for an emergency seat's call**"],
        {"cells": ["`Activate`", "operator socket `activate`, with the roster's signatures",
                   "A quorum of distinct break-glass roster keys over one person, one round and the task, on a prepared "
                   "seating (ADR-0052 §2)", "F5: the activation record"], "accent": "brown"},
        {"cells": ["`WorkflowGrant`", "a replica's driver, for each ready slot of a loaded workflow, in log order",
                   "The workflow's promotion: the request is rebuilt at apply and must be the seating's, with the "
                   "task's label joined with the clear inputs'; the budget charges it ([[amber|Proposed]], ADR-0054 §2; "
                   "ADR-0055 §2; I49)", "—"], "accent": "amber"},
        {"group": "Subtractions: ordered, approved by nobody", "accent": "green"},
        {"cells": ["`EndRound`", "any replica (expiry); the seat (abstain, Build only); operator `end_round` †",
                   "None needed: it removes authority", "F2 (expiry eviction, e-stop)"], "accent": "green"},
        {"cells": ["`Revoke`", "operator `revoke` † (a principal, Persona or confinement digest)",
                   "None needed (ADR-0031 §5 R3)", "F2"], "accent": "green"},
        {"cells": ["`EpochIncrement`", "operator `fence_epoch` †", "None needed: the fleet fence (ADR-0031 §5)", "F2"],
         "accent": "green"},
        {"cells": ["`Contested`", "the launcher, on a Contested verdict at launch or renewal",
                   "Revokes the principal, with its evidence by digest; apply refuses all but a rung-3 statement "
                   "signed by an issued verifier key (ADR-0034 §3.7; SIMULATED at the reference)", "F2"],
         "accent": "green"},
        {"group": "Authority facts", "accent": "brown"},
        ["`Issue`", "operator relays an anchor issuance", "`Authentic` signatures and the rules floor "
         "(`validate_issuance`, ADR-0026)", "F4"],
        ["`GatesPassed`", "operator `gates_passed` †", "Asserted: who runs the gates is unspecified (PROVISIONAL, G8); "
         "an operator's `AttestGates` attributes it and is still an assertion (G10 item 57)", "—"],
        ["`ProfileRegister`", "operator `register_profile`", "The profile's one-file workspace is promoted (ADR-0034 "
         "§1); a Run profile registers under A2 (Batch 30)", "—"],
        {"cells": ["`EmergencySeating`", "operator socket `prepare_emergency`", "**BOOTSTRAP**: unsigned, standing in "
                   "for the promotion that prepares a seating (ADR-0052 §2)", "—"], "accent": "red"},
        {"cells": ["`WorkflowLoad`", "operator socket `load_workflow`", "Unsigned; loaded only if the workflow's "
                   "single-file workspace was promoted by tally and the text is well formed ([[amber|Proposed]], "
                   "ADR-0054 §1; ADR-0055 §1)", "—"], "accent": "amber"},
        {"cells": ["`BreakGlassApprove`", "nobody, since 2026.10.05", "**Retired: refused at apply.** It was a roster "
                   "approval for X1, which the floor no longer has (ADR-0052 §2)", "—"], "accent": "grey"},
    ]
    cy += c.table(CX, cy, cols, rows_t, size=13.5, accent="violet") + 14
    cy += c.para(CX, cy, CW, "**No entry records a promotion.** There is no `Promote` entry and no `promote` op: "
                 "promotion happens inside `apply` when a `Vote` or `Heartbeat` admit completes the tally "
                 "(`Applied::Admitted { promoted }`), and `Candidate.promoted_at` in state is derived from that admit. "
                 "F3 retains the vote; the promotion itself is a derived fact the archive would have to recompute "
                 "(inventory finding 29). **`Applied` has sixteen results**; the rebuild added `EmergencyPrepared`, the "
                 "workflow build `WorkflowLoaded` and `WorkflowFailed`, and `BreakGlassApproved` is no longer reachable. "
                 "`Route`, an orchestrator's choice, is an `Admit` like any other, checked again at apply (ADR-0054 §8; "
                 "C9).", 13.5, "muted") + 26

    hh = c.card(CX, cy, CW, "Observer coupling: `live(o)` at decide and at apply (ADR-0039 §1, §2, A2; ADR-0041 §2)", [
        "**At decide**, the lift computes `live(o)` for the seat's cell Observers: a live Observer lease, a heartbeat "
        "heard within `T_obs` **on this replica's clock**, and `seq(t) − mark(o, r) < K`. Floor entry `R3-observer-live` "
        "forbids `Actuate` and `Report` under a Thinker without it.",
        "**`R3` is a Thinker's.** An `emergency` seat is not a `thinker` and is not coupled: no exemption is written "
        "(ADR-0039 A2, provisional with ADR-0052).",
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
    c.text(CX, cy + 19, "The committed admit: `AdmitRecord` (state.rs, step 7)", 19, "blue", bold=True)
    cy += 34
    cy += c.table(CX, cy, [("Field", CW * 0.2, {"mono": True}), ("What it holds", CW * 0.8)], [
        ["seat", "The seat the session names"],
        ["lease", "The lease's fence: the log index of its grant"],
        ["epoch", "The epoch the request carried"],
        ["action", "The admitted action with its target; for `Actuate`, the tool id, the inputs **by digest**, and "
                   "whether the call is an **emergency seat's** (`emergency`, F5), where it said whether the floor "
                   "admitted it through `X1-break-glass`"],
        ["input", "Digest of the frozen input both tiers evaluated (ADR-0030 §4)"],
        ["floor", "Digest of the linked floor text"],
        ["schema", "Digest of schema S"],
        {"cells": ["(values file)", "**Not recorded.** The values file is pinned at startup beside the floor and schema "
                   "(step 5), but no admit and no `status` reply carries its digest (inventory finding 12)"],
         "accent": "red"},
        ["floor_reasons", "The permitting policy ids"],
        ["bundle", "The bundle revision that allowed: the lease's, or for an emergency seat the one holding the entry"],
        ["engine", "Which bundle engine decided: sidecar or local WASM"],
        ["params", "Digest of the mechanism parameters; a mismatch at apply voids the admit"],
        ["decided_by", "The deciding replica, which alone performs the effect"],
        ["session", "Under an attested session key (rungs 2 and 3), the guest's proof that it sent this action; under "
                    "an emergency seat's lease, the person's (ADR-0034 §3.5; ADR-0052 §1; I41)"],
        {"cells": ["labels", "For a `Consult` or `Actuate`, the label facts the deciding replica computed (ADR-0047 "
                   "§4, §5); folded at apply. Apply re-checks `clearSet` only and takes the rest as the replica's "
                   "(I46 (a); G10 item 93)"], "accent": "teal"},
    ], size=13.5, accent="blue") + 30
    hh = c.card(CX, cy, CW, "Mechanism state: what the log rebuilds, and what each replica keeps alone (`State`, "
                            "state.rs)", [
        "**Replicated, rebuilt by replaying the log, never snapshotted**: `chain`, `epoch`, `rules`, `floor_exceptions`, "
        "`leases` (by fence, each with its round's **labels**, and for an emergency seat the person's key and the "
        "envelope), `live_by_seat`, `last_round`, `candidates`, `gates`, `revoked`, `applied_ids` (PROVISIONAL, G14), "
        "`last_applied`, the floor's `observer` and `persona` values, `marks`, `seals`, `profiles`, `contested`; since "
        "2026.10.05 `seatings`, `last_lease`, `control_ctr`, `emergency_seatings` and `activations`. The `break_glass` "
        "approvals map is dead: no entry can add to it (I48).",
        "**Per replica, not replicated**: `sessions` (the bearer tokens, I14), `observed` (recorded under the state "
        "lock since A13), `heard(o)` (ADR-0032 §3), `after_written` (I23), `in_flight` `Actuate` calls, `launched` "
        "guests, and **`results`**, what a handle can name, held in memory and dropped at the seal (I46 (e)). A replica "
        "that dies takes these with it; after a failover a handle to an earlier result fails its call.",
    ], accent="violet", size=14)
    cy += hh + 26
    hh = c.card(CX, cy, CW, "Checked against `spec/Mechanism.tla` (ADR-0033 A14; G10 §3)", [
        "**82 traces, 1,007 steps, every step matching**, and every state keeping `ConfinementRefinement.tla`'s "
        "invariants (`spec/Mechanism-trace-results-2026.10.05.txt`).",
        "**The model's scope at A14**: the label fold and the stale-`clearSet` refusal, a seating, the gate on unsigned "
        "requests, a control request with its facts recomputed and the envelope restated, an activation, and X1's "
        "approval rejected. Five edits that each removed one modelled thing produced a mismatch; a sixth is caught as "
        "an evaluation error.",
        "**Taken from the trace, not computed**: whether a request's signature is its seat's, whether a sign-on "
        "assertion verifies, which roster keys approved an activation, which seat a revocation was lifted on, and the "
        "label facts themselves.",
        "**The floor's decision on an operator's request is not modelled**: the trace compares two restatements of the "
        "envelope, in Rust and in TLA+, and neither with the Cedar text. A matching trace is drift detection on tested "
        "paths, **not a refinement**; T-0045-28 stands.",
    ], accent="teal", size=14)
    cy += hh + 26
    c.card(CX, cy, CW, "What this path does not show (ADR-0033 §1, §3, §6; G10 §8)", [
        "**Confinement**: for an operator grant the MCP front door makes the alphabet the whole protocol, not the "
        "whole channel. The launcher (A7, ratified Batch 29) makes it the whole channel for a guest it starts, at "
        "rung 1 on profiles that declare P3 `fail`, or at rung 3 only SIMULATED: **no real principal is `Contained`**.",
        "**A first lease from a quorum**: seatings are made by the BOOTSTRAP path (G10 item 88).",
        "**That a label is true**: the facts are one replica's computation, a failed call's error text reaches the "
        "principal unlabelled, and only a scalar can be passed by handle (G10 item 93).",
        "**A person's signed action on a socket**: an emergency seat is exercised in-process (G10 item 92).",
        "**A Byzantine replica**: replicas are crash-recovery. The apply re-check stops **stale** admits, not **forged** "
        "ones; replica authentication is unbuilt (T-0045-1).",
        "The reference is **evidence, not the verified object**: never promoted, in no TCB.",
    ], accent="red", size=14, tint=False, dash="6 4")

    # legend
    ly = c.ymax + 40
    c.legend(c.x0, ly, [
        ("box", "teal", "mechanism step"), ("box", "blue", "floor tier"), ("box", "amber", "bundle tier / Kafka"),
        ("box", "violet", "consensus (P)"), ("box", "brown", "operator and roster paths"),
        ("box", "red", "denial, void, gap, BOOTSTRAP"),
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
        (0.38, "slot `i`: the fleet fence", "`FenceEpoch`: epoch → `e+1`", "green", 1),
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
