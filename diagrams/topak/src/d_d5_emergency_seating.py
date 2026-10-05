"""D5 — Break-glass is an emergency seating (ADR-0052, provisional)."""
from lib import Canvas, STATUS, text_width

ID, SLUG = "D5", "emergency-seating"

W = 3200


def _nb(ln):
    """Keep leading indentation: the wrapper drops ordinary leading spaces."""
    n = len(ln) - len(ln.lstrip(" "))
    return " " * n + ln.lstrip(" ")


def code(c, x, y, w, lines, accent, dash=None):
    """A monospace block (Cedar), drawn as a card with one line per body item."""
    return c.card(x, y, w, None, [f"`{_nb(ln)}`" if ln.strip() else " " for ln in lines], accent=accent,
                  bullets=False, size=13.5, lead=19, tint=False, pad=14, dash=dash)


def row_cards(c, x, y, w, gap, specs, size=14):
    """Draw a row of cards of equal height. specs: (title, body, accent, kwargs). Returns the height."""
    n = len(specs)
    cw = (w - (n - 1) * gap) / n
    h = max(c.card(0, 0, cw, t, b, draw=False, size=size, status=k.get("status")) for t, b, _, k in specs)
    for i, (t, b, acc, k) in enumerate(specs):
        c.card(x + i * (cw + gap), y, cw, t, b, accent=acc, h=h, size=size, **k)
    return h


def build():
    c = Canvas(ID, "Break-glass is an emergency seating",
               "ADR-0052 retires the floor's break-glass exception, X1. The break-glass roster's quorum now seats a "
               "named **person** on a seat of kind `emergency` for **one round**, on an envelope prepared in advance by "
               "promotion; the seat's calls are admitted by the ordinary allowlist permit, it is not coupled to an "
               "Observer, its activation is a forensic-floor record, and the path is drilled. Ratified **provisional** "
               "on 2026.10.05 (Batch 34): in force and subject to redesign, resting on ADR-0050, with its exit stated.",
               W, "ADR-0052 Context, §1–§9 (R1–R6), Options, Consequences, Findings, Open obligations, History B34; "
               "ADR-0009 A1; ADR-0013 §1, A1; ADR-0016 A2; ADR-0024 A3; ADR-0026 §2 R6, R7, A2, W1; ADR-0028 F5; "
               "ADR-0029 A4; ADR-0030 A3; ADR-0031 §2, §4, §5, A2; ADR-0032 §2; ADR-0033 A12, A14; ADR-0037 §4, §7, "
               "A3, A4; ADR-0039 §2, A2; ADR-0041 §1, §3, A1, A2; ADR-0042 §3, A2; ADR-0045 §6; ADR-0046 A1; "
               "ADR-0007; ADR-0023 §6a; ADR-0040 §3; ADR-0047 F1–F3; ADR-0048 §2; ADR-0049 §5; ADR-0051 (Proposed); ADR-0050 §2, §4, §6, §10; G10 §1, §1.1, §1.2, §2.1–§2.3, "
               "§2.5, §2.9, §3 (results 5, 6), §4, §6, §7 items 8, 46, 49, 88, 90–92, §8; ToO rev 14 §3.3, §4.4, §5.4; "
               "glossary (emergency seat, emergency seating, activation, drill); floor/proposed/emergency-floor.cedar "
               "(B10, R1, R3, R5–R7, X2) and its gates results; spec/Emergency.tla, results, proof and certified "
               "results; spec/BreakGlass_A1.tla and spec/NonComposition_A1.tla, rows, results, proofs and certified "
               "results; spec/Mechanism.tla; mechanism/crates/topak-core/src/control.rs, state.rs, rules.rs; "
               "mechanism/crates/topak-core/tests/emergency.rs; mechanism/GAPS-AND-ASSUMPTIONS.md I47, I48, G10")
    X0, X1 = c.x0, c.x1
    WW = X1 - X0
    y = c.y

    # ---- status strip (wraps)
    c.text(X0, y + 15, "Status at G10", 15, "faint", bold=True)
    px0 = X0 + 140
    px = px0
    for lab, key, extra in [
            ("ADR-0052", "provisional", "C1, C3, C4"), ("rests on ADR-0050", "provisional", "C1, C3, C4"),
            ("ADR-0009 A1, ADR-0013 A1, ADR-0016 A2, ADR-0037 A3, ADR-0039 A2, ADR-0041 A2, ADR-0042 A2",
             "provisional", "with ADR-0052"),
            ("ADR-0026 A2 (R6, R7)", "provisional", "bootstrap set"), ("R8 (ADR-0026 A1)", "withdrawn", "W1"),
            ("X1-break-glass", "superseded", "retired"), ("floor in force", "genprov", "emergency stage"),
            ("Emergency.tla", "built", "proved · certified"),
            ("seating prepared by promotion", "notbuilt", "BOOTSTRAP at the reference")]:
        lw = text_width(lab, 13.5, True) + 8
        pw = text_width(STATUS[key][0] + (f" · {extra}" if extra else ""), 11.5, True) + 18
        if px + lw + pw > X1:
            px = px0
            y += 34
        c.text(px, y + 15, lab, 13.5, "ink", bold=True)
        px += lw
        if key == "built":
            # a module result, not a reference behaviour: a plain pill, not the "Built at reference" status
            px += c.pill(px, y, "Proved · certified (ADR-0046 A1)", "violet", 11.5) + 26
        else:
            px += c.status(px, y, key, extra) + 26
    y += 42
    y += c.para(X0, y, WW, "**Provisional means**: ratified, in force, subject to redesign, for a record that did not "
                "meet its own ratification condition and says on its face what it lacked (ADR-0029 A4). **X1's "
                "retirement is in force on that basis**: if ADR-0052 is redesigned, break-glass has no settled form "
                "until the redesign is ratified (ADR-0052 §9; G10 §1.2, §8). Everything here is one hand's: not "
                "reviewed by a reader other than the drafter. Anything citing it says \"author-ratified, provisional\".",
                14.5, "muted") + 30

    # ================================================================== the path, left to right
    c.text(X0, y + 22, "The path: prepared by promotion, activated by the roster's quorum, one lease for one round "
                       "(ADR-0052 §2, §3)", 22, "ink", bold=True)
    y += 56
    g = 80
    cw = [470, 560, 600, 600]
    cw.append(WW - sum(cw) - 4 * g)
    cx = [X0]
    for w_ in cw[:-1]:
        cx.append(cx[-1] + w_ + g)
    top = y

    PROM = ("Promotion prepares it (ADR-0024 A3)", [
        "**In advance**: an emergency seating is promoted like any other seating, by the quorum of B5.",
        "**Emergency-only tools** (to isolate, to roll back) are promoted ahead of time, in the seating's own bundle.",
        "**Not built**: at the reference the unsigned BOOTSTRAP path prepares it (`prepare_emergency`).",
    ])
    ROST = ("The break-glass roster, issued by the anchors", [
        "The roster and its quorum `k` are what the rules carry for break-glass (ADR-0013 §1; ADR-0026 A2).",
        "Whether the rules floor bounds `k` for activation, as R9 bounds a promotion's, is open.",
    ])
    SEAT = ("The emergency seating", [
        "**The seat**, of kind `emergency`, in Run; **the persons** who may hold it, by key; **its envelope**: "
        "\"the domain's\" by default, or named entry by entry; **the labels** a task for it may carry; a **drill** "
        "mark (ADR-0052 §2, §6; `EmergencySeating`).",
        "Several may exist; the roster's quorum activates one.",
    ])
    ACT = ("Activation: the roster's act alone", [
        "**One lease, for one named person and one round**, with the round's task by digest and label. The roster "
        "members sign exactly that; every replica counts distinct roster keys against the issued quorum.",
        "**No operator's request, no promotion's unanimity, no gate.** That is the speed break-glass exists for.",
        "**No field for the reason**: it is unknown to the mechanism by construction (§5).",
    ])
    LEASE = ("One lease, one round", [
        "Alphabet `Consult`, `Actuate`, `Report`, the kind's; the **person's key** is in the lease.",
        "**The envelope is fixed for the round**: computed from the log at the activation's index. A promotion "
        "during the round does not reach it; the next activation sees it.",
    ])
    TOOLS = ("The person is told what is in it", [
        "The round's **tool list is the envelope**, delivered at the start of the round and written to the topic as "
        "its opening record (ADR-0048 §2).",
        "What is delivered in the clear follows the bundle's delivery table, per seat kind: with no row for "
        "`emergency`, **the person is given handles** (result 6, below).",
    ])
    CALL = ("Each call", [
        "**Signed with the person's key**, as a proof checked at decide and at apply; no bearer token (§1; I48).",
        "Admitted by `R1-actuate-allowlisted` over the envelope, an ordinary allowlist of ADR-0049 entries: "
        "**no exception** (§2). `B10` lets an `emergency` seat `Actuate` and author nothing else.",
        "`R3-observer-live` **does not reach it**: a `thinker` rule (§4).",
        "Recorded on the round topic with `seatKind`, where the record said `breakGlass` (ADR-0042 A2).",
    ])
    LABELS = ("The label forbids bind the person", [
        "`R5` to `R7` (ADR-0047 F1 to F3) are forbids on `Actuate` whatever the seat's kind (ADR-0041 A1, A2).",
        "A person holding the seat who has read untrusted content in the clear takes a destination from a handle, "
        "like anyone else (§2). **In an emergency that will be felt** (Consequences).",
    ])
    READ = ("Read by everyone who can stop it (§4)", [
        "**The domain's operators**, in its `W(p)`; a cell Observer if one is seated and live; the correlator.",
        "**A finding is a deny** any of them can make. At the reference the operators read only in that nothing "
        "stops them: there is no read path (I48).",
    ])
    END = ("It ends with its round (§3)", [
        "At the round bound `R`; at the lease's `ttl`, at most `T_persona` on the local monotonic clock (ADR-0031 "
        "A2); when the person ends it.",
        "**Sooner**: at an epoch increment, or a targeted revocation **by any operator of the domain** (ADR-0050 §4).",
        "**No successor, no renewal**: an operator's `Regrant` or `Renew` naming the seat is refused. **Another round "
        "is another quorum.**",
        "**This is the time box**, on the clock the corpus already accepts for a lease. **R8 stays withdrawn**: no TTL "
        "is issued or read (ADR-0026 W1).",
    ])

    def ch(spec, w_, **k):
        return c.card(0, 0, w_, spec[0], spec[1], draw=False, size=14, **k)

    hp, hr = ch(PROM, cw[0], status="notbuilt"), ch(ROST, cw[0])
    hs, ha = ch(SEAT, cw[1]), ch(ACT, cw[1])
    hl, hc = ch(LEASE, cw[2]), ch(CALL, cw[3])
    ht, hb = ch(TOOLS, cw[2]), ch(LABELS, cw[3])
    hrd, he = ch(READ, cw[4]), ch(END, cw[4])
    vgap = 90
    row1 = max(hp, hs, ht, hb, hrd)
    row2 = max(hr, ha, hl, hc, he)
    r2 = top + row1 + vgap
    c.card(cx[0], top, cw[0], PROM[0], PROM[1], accent="blue", h=row1, size=14, status="notbuilt",
           status_extra="BOOTSTRAP stands in", tint=False)
    c.card(cx[0], r2, cw[0], ROST[0], ROST[1], accent="brown", h=row2, size=14)
    c.card(cx[1], top, cw[1], SEAT[0], SEAT[1], accent="blue", h=row1, size=14)
    c.card(cx[1], r2, cw[1], ACT[0], ACT[1], accent="teal", h=row2, size=14)
    c.card(cx[2], top, cw[2], TOOLS[0], TOOLS[1], accent="teal", h=row1, size=14)
    c.card(cx[2], r2, cw[2], LEASE[0], LEASE[1], accent="teal", h=row2, size=14)
    c.card(cx[3], top, cw[3], LABELS[0], LABELS[1], accent="red", h=row1, size=14, tint=False)
    c.card(cx[3], r2, cw[3], CALL[0], CALL[1], accent="green", h=row2, size=14)
    c.card(cx[4], top, cw[4], READ[0], READ[1], accent="pink", h=row1, size=14)
    c.card(cx[4], r2, cw[4], END[0], END[1], accent="green", h=row2, size=14, dash="6 4")
    mid_h = row1 + vgap + row2
    # arrows
    ya = top + 70
    yb = r2 + 70
    c.arrow([(cx[0] + cw[0], ya), (cx[1], ya)], "red", dash="7 5", sw=2.2, label="prepare", loff=(0, -18))
    c.arrow([(cx[0] + cw[0], yb), (cx[1], yb)], "brown", sw=2.4, label="quorum signs", loff=(0, -18))
    for k, lab, acc in [(1, "names one seating", "blue"), (2, "tool list = envelope", "teal")]:
        c.arrow([(cx[k] + cw[k] / 2, r2), (cx[k] + cw[k] / 2, top + row1)] if k == 2 else
                [(cx[k] + cw[k] / 2, top + row1), (cx[k] + cw[k] / 2, r2)], acc, sw=2.2, label=lab, lpos=0.5)
    c.arrow([(cx[3] + cw[3] / 2, top + row1), (cx[3] + cw[3] / 2, r2)], "red", sw=2.2, dash="7 5",
            label="forbid on Actuate", lpos=0.5)
    c.arrow([(cx[1] + cw[1], yb), (cx[2], yb)], "teal", sw=2.4, label="grants", loff=(0, -18))
    c.arrow([(cx[2] + cw[2], yb), (cx[3], yb)], "teal", sw=2.4, label="calls", loff=(0, -18))
    c.arrow([(cx[3] + cw[3], yb + 60), (cx[4], yb + 60)], "green", sw=2.2, dash="7 5", label="ends", loff=(0, -18))
    xm = cx[4] - g / 2
    c.arrow([(cx[3] + cw[3], r2 + 24), (xm, r2 + 24), (xm, ya), (cx[4], ya)], "pink", sw=2.2, dash="7 5")
    c.label(xm, (ya + r2) / 2, "read,\ndeny", "pink")
    y = top + mid_h + 40
    # forensic strip under the path
    fh = c.card(cx[1], y, cx[3] + cw[3] - cx[1], "Recorded (§5): the activation is a forensic-floor record, F5", [
        "**Who approved, whom, on which seating, for which round, with the task's digest and label**, and at the "
        "reference the envelope as computed and the drill mark. Erasure does not remove it (ADR-0028 F5; ADR-0013 "
        "NC-2), and it must outlive its round (`NonComposition_A1.tla`, M3). **Every call** leaves its record on the "
        "round topic. **The reason is unknown to the mechanism, by construction**: why the quorum acted is a claim "
        "about the world, and a field for it would be prose nothing checks (ADR-0007). The person may `Report` a "
        "rationale; that is content, and no admit turns on it.",
    ], accent="brown", size=14, bullets=False)
    c.arrow([(cx[1] + cw[1] / 2 - 120, top + mid_h), (cx[1] + cw[1] / 2 - 120, y)], "brown", sw=2,
            label="F5", lpos=0.5)
    y += fh + 70

    # ================================================================== detail: seat | envelope | round
    c.text(X0, y + 22, "The seat, the envelope, and two questions the reference raised", 22, "ink", bold=True)
    y += 56
    g3 = 60
    w3 = (WW - 2 * g3) / 3
    xa, xb, xc = X0, X0 + w3 + g3, X0 + 2 * (w3 + g3)
    dtop = y

    # -- column A: the seat and the kinds table
    cy = dtop
    cy += c.card(xa, cy, w3, "§1 · An emergency seat is held by a person, and its kind is `emergency`", [
        "**A fifth seat kind**, declared in the issued rules, Run only. It does not vote, draft or submit "
        "(ADR-0037 A3).",
        "**Only a person holds one**, with a Persona record and a signing key, and **no other seat in that round** "
        "(ADR-0037 §7, A3). No model's Persona binds to the kind: the seat binding `emergency` is for a person's "
        "Persona whose attestation is the roster's quorum (ADR-0016 A2).",
        "**The person acts, and no agent does.** The mechanism cannot tell a person from a program holding the "
        "person's key; this is a rule about what is seated, as for operators.",
        "`Mediated`: a person is not confined (G10 §2.3). The envelope bounds the front door, and nothing here "
        "bounds what a person does elsewhere.",
        "**Its key does not depend on single sign-on** (drafter's choice): an emergency path that needs the "
        "identity provider fails when the provider does.",
    ], accent="blue", size=14) + 16
    cy += c.para(xa, cy, w3, "**Alphabets by seat kind** (ADR-0037 §4 with A3 and A4; the struck provisional Run "
                 "column omitted):", 14) + 6
    cy += c.table(xa, cy, [("Kind", w3 * 0.17, {"mono": True}), ("Build", w3 * 0.36), ("Run", w3 * 0.47)], [
        ["thinker", "`Read`, `Draft`, `Invoke`, `Emit`, `Submit`", "`Consult`, `Actuate`, `Report`"],
        ["observer", "`Read`, `Emit`; `Vote(deny)` when on the veto roster",
         "`Consult`, `Report` (heartbeats and findings)"],
        ["grant", "`Read`, `Emit`, `Vote`", "None; only Build seats vote"],
        {"cells": ["operator", "`Regrant`, `Renew`, `AttestGates`, `EndRound`, `Revoke`, `FenceEpoch` (A4)",
                   "`Regrant`, `Renew`, `EndRound`, `Revoke`, `FenceEpoch`; no authoring variant (A4)"],
         "accent": "brown"},
        {"cells": ["emergency", "**None**: no emergency seat in Build; a promotion is Build's way to add authority "
                                "(§7)", "`Consult`, `Actuate`, `Report` (A3)"], "accent": "blue"},
    ], size=13.5, accent="blue") + 14
    cy += c.para(xa, cy, w3, "`B10` as linked by the reference: an `emergency` seat may `Actuate` and nothing else "
                 "here (ADR-0041 A2; ADR-0037 A3):", 13.5, "muted") + 6
    cy += code(c, xa, cy, w3, [
        '@id("B10-only-thinkers-author")',
        'forbid (principal,',
        '  action in [Topak::Action::"Draft", Topak::Action::"Invoke",',
        '             Topak::Action::"Submit", Topak::Action::"Actuate"],',
        '  resource)',
        'when {',
        '  principal.kind != "thinker" &&',
        '  !(principal.kind == "emergency" && action == Topak::Action::"Actuate")',
        '};',
    ], "blue")
    a_bot = cy

    # -- column B: §2's table and the domain's envelope
    cy = dtop
    cy += c.para(xb, cy, w3, "**§2 · The envelope is prepared by promotion, and activated by the roster's quorum** "
                 "(the record's table):", 15) + 8
    cy += c.table(xb, cy, [("Step", w3 * 0.14, {"bold": True}), ("What", w3 * 0.46), ("By whom", w3 * 0.26),
                           ("When", w3 * 0.14)], [
        ["Prepare", "An **emergency seating**: the seat, the persons who may hold it, its envelope (by default the "
                    "domain's), and the labels a task for it may carry (ADR-0050 §2, §5)", "A promotion",
         "In advance"],
        ["Activate", "One lease on that seating, for one named person and one round, with the round's task",
         "A quorum on the break-glass roster the anchors issued (ADR-0013 §1)", "At the emergency"],
    ], size=13.5, accent="blue") + 18
    # domain envelope mini-diagram
    c.text(xb, cy + 17, "The domain's envelope, computed at activation (§2, R1)", 17, "teal", bold=True)
    cy += 34
    bw = (w3 - 2 * 20) / 3
    revs = [("`thinker` seating", "names revision A", "teal", None, "Run entries t1, t2"),
            ("`operator` seating", "names revision B", "amber", "6 4", "Run entries: in the envelope? (result 5)"),
            ("emergency seating", "its own bundle", "blue", None, "emergency-only tools, e.g. isolate, roll back")]
    rh = max(c.card(0, 0, bw, a, [b, d], draw=False, size=13.5, bullets=False) for a, b, _, _, d in revs)
    for i, (a, b, acc, dsh, d) in enumerate(revs):
        c.card(xb + i * (bw + 20), cy, bw, a, [b, d], accent=acc, h=rh, size=13.5, bullets=False, dash=dsh,
               tint=dsh is None)
    ey = cy + rh + 50
    for i in range(3):
        bx_ = xb + i * (bw + 20) + bw / 2
        c.arrow([(bx_, cy + rh), (bx_, ey)], "amber" if i == 1 else "teal", dash="7 5" if i == 1 else None)
    eh = c.card(xb, ey, w3, "Envelope = every Run allowlist entry of every revision a seating in force in the "
                            "domain names, un-narrowed, with the seating's own bundle", [
        "Computed from the log at the activation's index and **fixed for the round**. It cannot go stale: a tool "
        "promoted yesterday is in it today, and nobody has to keep an emergency envelope in step.",
        "**No entry is general-purpose**: each tool is held to the channel its entry declares; a shell, or a client "
        "for any address, is admitted nowhere (ADR-0049 §5; ADR-0040 §3).",
        "**A deployment may prepare a narrower seating**, named entry by entry, and is given exactly that.",
        "**Open**: where two revisions in force declare one tool differently, which entry governs (the drafter's "
        "reading: the later promotion's).",
        "At the reference **the ordering replica computes it**; the others take it, and only a named envelope is "
        "checked against the seating (I48 (b)).",
    ], accent="teal", size=13.5)
    cy = ey + eh + 18
    q = [
        ("Result 5 · Does an operator's seating count?", "amber", [
            "**An operator's seating feeds the emergency envelope.** An operator calls no tool, and its seating still "
            "names a revision; **at the reference it counts**, so that revision's Run entries are in the envelope "
            "(G10 §3, result 5; I48 (b)).",
            "ADR-0052 does not say whether it should. **Open** (G10 item 92).",
        ]),
        ("Result 6 · Handles by default for a person", "amber", [
            "**A person on an emergency seat is given handles unless the bundle says otherwise.** The delivery table "
            "is per seat kind, and the load check asks for rows for `thinker` and `observer` only (G10 §3, result 6; "
            "I48 (d)).",
            "Without an `emergency` row the person gets handles and no bytes, and nothing refuses such a bundle. "
            "Whether a table must have the row is **open** (G10 item 92).",
        ]),
    ]
    qh = max(c.card(0, 0, (w3 - 20) / 2, t, b, draw=False, size=13.5, status="open") for t, _, b in q)
    for i, (t, acc, b) in enumerate(q):
        c.card(xb + i * ((w3 - 20) / 2 + 20), cy, (w3 - 20) / 2, t, b, accent=acc, h=qh, size=13.5,
               status="open", status_extra="item 92")
    cy += qh
    b_bot = cy

    # -- column C: §3 to §6
    cy = dtop
    for t, acc, b, k in [
        ("§3 · One round, and nothing after it", "green", [
            "**An activation is scoped to the round** (the custodian's decision). The lease is round-coterminous, as "
            "every lease is (ADR-0031 §2).",
            "**No successor and no renewal** (drafter's choice on renewal). Another round is another quorum.",
            "**Why the round**: R8 looked for a second clock because the approval was scoped to the epoch and not to "
            "a lease. **The round was the time box all along** (Finding 3). R8, which needed trusted time, was "
            "withdrawn (ADR-0026 W1; ADR-0032 §2; ADR-0045 §6).",
        ], {}),
        ("§4 · Not coupled to an Observer (ADR-0039 A2)", "pink", [
            "`R3-observer-live` **is a forbid on a** `thinker` **seat**, and an emergency seat is not one, so it does not "
            "wait on a dead Observer, and **no exemption is written into R3** (Finding 4).",
            "`NoAdmitWithoutLiveObserver` and `UnreadBounded` stay statements about Thinkers; their modules owe "
            "nothing. G9 item 49 is decided (G10 §7).",
            "**Nothing acts unobserved on an agent's judgment**: what goes uncoupled is a person, seated by a quorum, "
            "for one round.",
        ], {}),
        ("§6 · The path is exercised", "violet", [
            "**At least once in each domain in each epoch, and periodically after that** (the custodian's decision). "
            "A new epoch asks for a new drill: it fences every lease.",
            "**A drill is a real activation**: the real roster, a real quorum, a real lease for one round, on a "
            "**drill seating** whose envelope holds one tool with no outward channel. It proves the roster, the keys "
            "and the path, and can do nothing.",
            "The period is counted in rounds of the domain, not in time (drafter's choice). **An obligation with "
            "evidence that gates nothing**: an emergency early in an epoch is still an emergency.",
            "**Nothing at the reference counts it**; the log can show it (I48; G10 item 92).",
        ], {}),
        ("§7 · What it does not cover", "grey", [
            "**Stopping**: `Revoke`, `EndRound` and the fence are ADR-0050's and need no emergency seat. **Erasure**, "
            "which stays the floor's one exception (D4). **A person acting outside the mechanism. Build. Whether the "
            "reason was good**: the review after the round, by people.",
        ], {"tint": False, "dash": "6 4"}),
    ]:
        cy += c.card(xc, cy, w3, t, b, accent=acc, size=14, **k) + 16
    c_bot = cy - 16
    y = max(a_bot, b_bot, c_bot) + 70

    # ================================================================== the floor and the rules floor
    c.text(X0, y + 22, "What moved in the floors (ADR-0041 A2; ADR-0026 A2, W1; ADR-0013 A1)", 22, "ink", bold=True)
    c.status(X0 + text_width("What moved in the floors (ADR-0041 A2; ADR-0026 A2, W1; ADR-0013 A1)", 22, True) + 20,
             y + 4, "genprov", "the policy floor, emergency stage")
    y += 50
    lw_ = 1640
    th = c.table(X0, y, [("Entry", lw_ * 0.2, {"mono": True}), ("Kind", lw_ * 0.08), ("Since Batch 34", lw_ * 0.72)], [
        {"cells": ["X1-break-glass", "permit", "**Removed.** The floor's exceptions are one, erasure; the count R6 "
                                               "bounds is 1 (ADR-0013 A1; ADR-0026 A2). Still in "
                                               "`floor/genesis-floor.cedar`, which is unchanged (D4)"],
         "accent": "grey"},
        ["B10-only-thinkers-author", "forbid", "Reads \"the seat's kind is not `thinker`, and, for `Actuate`, not "
                                               "`emergency`\""],
        ["R1-actuate-allowlisted", "permit", "Admits the emergency seat's calls, over the envelope, **like any other**"],
        ["R3-observer-live", "forbid", "**Unchanged**; does not reach the seat, which is not a `thinker`"],
        ["R5 to R7 (label forbids)", "forbid", "Bind the person: forbids on `Actuate` whatever the seat's kind "
                                               "(ADR-0041 A1, A2; ADR-0047 F1–F3)"],
        ["X2-erasure, F-forensic-classes", "permit, forbid", "Unchanged; the activation is F5"],
        {"cells": ["schema S", "—", "The `breakGlass` fields are gone from Run's context"], "accent": "grey"},
    ], size=13.5, accent="blue")
    c.para(X0, y + th + 12, lw_, "`floor/proposed/emergency-floor.cedar` (`15c941b9a56a09f7`): 28 policies, 107 cases, "
           "every gate passing (2026.10.04). The cases show an emergency seat calling inside its envelope with no live "
           "Observer, refused outside it, refused every authoring action, and bound by `R6`; and a Thinker unable to "
           "reach the emergency envelope. **Genesis-provisional** (ADR-0030 A3). The stage file's opening comment, "
           "\"not what the reference follows\", is wrong (G10 item 91).", 13.5, "muted")
    rx = X0 + lw_ + 50
    rw = X1 - rx
    rth = c.table(rx, y, [("Rules-floor entry", rw * 0.2, {"bold": True}), ("At G10 (§2.1)", rw * 0.8)], [
        {"cells": ["R6", "Still bounds the number of floor exceptions; **the count it bounds is 1**, erasure "
                         "(ADR-0026 A2, provisional)"], "accent": "violet"},
        {"cells": ["R7", "Read as **\"no activation of an emergency seating grants a lease whose alphabet holds an "
                         "authority act\"**. With the kind's alphabet it has nothing left to refuse, and is kept for "
                         "the day the kind changes (A2)"], "accent": "blue"},
        {"cells": ["R8", "**Withdrawn** 2026.10.04 (ADR-0026 W1), never in force. Not coming back as a TTL (G10)"],
         "accent": "grey"},
        {"cells": ["Behind", "`RulesFloorBase.tla` still carries `bgScope` and R6's bound of two (G10 item 90); "
                             "`BreakGlass_A1.tla` reads neither"], "accent": "red"},
    ], size=13.5, accent="violet")
    dh = c.para(rx, y + rth + 14, rw, "**D-0052-1** (§8), the record's one degeneracy:", 14) + 6
    c.table(rx, y + rth + 14 + dh, [("Id", rw * 0.12, {"bold": True}), ("Kind", rw * 0.14),
                                    ("Parameter → deployed value", rw * 0.34), ("Premises falsified", rw * 0.2),
                                    ("Theorems voided", rw * 0.2)], [
        ["D-0052-1", "Mechanism (ADR-0023 §6a)", "The emergency path → `X1-break-glass`: an approval scoped to a seat "
         "and an epoch lets that seat, an agent's included, `Actuate` inside an issued envelope until the epoch ends",
         "A break-glass grant ends with its round; the actor under it is a person",
         "None in force; §9's properties are lost. Type changes: none"],
    ], size=13.5, accent="amber")
    y = c.ymax + 70

    # ================================================================== verification
    c.text(X0, y + 22, "Checked, proved and certified: `Emergency.tla` and the two successors (ADR-0052 §9, R2, R5; "
                       "G10 §3)", 22, "violet", bold=True)
    y += 50
    lw_ = 1640
    PROPS = ["EmergencyLeaseHasARosterQuorum", "EmergencyLeaseIsOneRound", "NoAgentHoldsAnEmergencySeat",
             "CallsAreAllowlisted", "ThinkerStillCoupled", "ActivationIsForensic"]
    short = ["Quorum", "OneRound", "NoAgent", "Allowlisted", "Coupled", "Forensic"]
    MUT = [("M_NOQUORUM", "an activation with fewer approvals than the quorum", {0}),
           ("M_REGRANT", "an operator grants the emergency seat its next round", {0, 1, 5}),
           ("M_RENEW", "an operator renews a live emergency lease", {1}),
           ("M_AGENT", "an agent may be seated", {2}),
           ("M_X1", "X1 left in the floor: under a quorum's approvals any seat may call any tool", {3}),
           ("M_UNCOUPLE", "R3 dropped for the Thinker", {4}),
           ("M_ERASE", "erasure may remove an activation record", {5})]
    yy = y
    yy += c.para(X0, yy, lw_, "**Six properties**, two over ghost truth the mechanism never reads (whether the holder "
                 "is a person; whether a quorum stood behind a lease): every emergency lease had a roster quorum; none "
                 "was granted by anyone but the roster, or renewed; its holder is a person; **no call by either seat is "
                 "admitted outside its seat's allowlist**, so no admit is by an exception; no Thinker's call without a "
                 "live Observer (R3 untouched); every round the seat has had has its activation record.", 14) + 10
    pcw = (lw_ * 0.5) / 6
    cols = [("Mutation (one TLC run per cell; the first row is one run of `Safe`)", lw_ * 0.5)] + [(s_, pcw) for s_ in short]
    rows = [{"cells": ["**none** · `Safe`, the conjunction: [[green|holds]], 25,728 distinct states"] +
             ["[[green|holds]]"] * 6, "accent": "green"}]
    for m, d, br in MUT:
        cells = [f"`{m}` · {d}"] + ["[[red|breaks]]" if i in br else "holds" for i in range(6)]
        rows.append({"cells": cells, "accent": "grey"} if m == "M_X1" else cells)
    yy += c.table(X0, yy, cols, rows, size=13.5, accent="violet") + 10
    yy += c.para(X0, yy, lw_, "Columns, in order: " + "; ".join(f"`{p}`" for p in PROPS) + ". **Each mutation breaks "
                 "exactly the properties the module says and no other**: 1 + 7 × 6 = 43 rows. `M_X1` is X1 as the "
                 "reference had it until 2026.10.05, caught by `CallsAreAllowlisted` whichever seat uses it.",
                 13.5, "muted") + 12
    wit = [("NeverActivated", "the seat is activated"), ("NeverSecondRound", "a second round, on a second quorum"),
           ("NeverUnobservedEmergencyCall", "an emergency call with no live Observer"),
           ("NeverEmergencyOnlyTool", "a call of the emergency-only tool"),
           ("NeverNewToolInEnvelope", "a tool promoted since the last activation, in the envelope"),
           ("NeverStaleEnvelope", "a promotion during a live round does not reach its envelope"),
           ("NeverRefused", "a call outside the envelope is refused, a tool in no bundle among them"),
           ("NeverThinkerCall", "the Thinker is refused what the emergency seat may do")]
    half = (lw_ - 20) / 2
    wy = yy
    for j in range(2):
        c.table(X0 + j * (half + 20), wy, [("Witness (must be violated)", half * 0.5, {"mono": True}),
                                            ("Reached (counterexample ✓)", half * 0.5)],
                [[a, b] for a, b in wit[j * 4:(j + 1) * 4]], size=13.5, accent="violet")
    yy = c.ymax + 12
    c.para(X0, yy, lw_, "`spec/Emergency-results-2026.10.04.txt`: **51 rows** (43 above and 8 witnesses), TLC 2.19, "
           "`MaxRound` = 2, a roster of three with quorum two, one person, one agent. **Proved**: "
           "`Emergency_proof.tla`, **373 obligations**, nothing assumed. **Certified** (ADR-0046 A1): 234 trivial, 130 by "
           "SMT with a proof the checker accepted, 9 LS4 steps, which no checker confirms. **Not modelled**: the label "
           "forbids, the task, the drill as a distinct seating, more than one domain. Tied to the reference by tests "
           "and no refinement (G10 item 90). A certified proof is not a verified one.", 13.5, "muted")

    # successors on the right
    rx = X0 + lw_ + 50
    rw = X1 - rx
    ry = y
    ry += c.card(rx, ry, rw, "Successor modules (the `_A1` convention; predecessors frozen, cited by digest)", [
        "`BreakGlass_A1.tla` (`b586a6afa4fd5136`), for ADR-0029 §5's fifth bootstrap invariant under ADR-0026 A2's "
        "reading of R7. Its proof (45 obligations) **does not assume R7 is in force**, unlike its predecessor's.",
        "`NonComposition_A1.tla` (`d1e9113480d016bb`), for NC-1 and NC-2 with the activation's record as F5 and a "
        "round that ends; 14 rows, 96 obligations; all 14 rows are drawn in D4.",
        "Both: nothing assumed, certified, and **neither found a fault in ADR-0052**.",
    ], accent="violet", size=14) + 14
    ry += c.table(rx, ry, [("Row", rw * 0.15, {"mono": True}), ("Mut", rw * 0.12, {"mono": True}),
                           ("R7", rw * 0.08), ("Invariant", rw * 0.33, {"mono": True}), ("Result", rw * 0.32)], [
        {"cells": ["a1-base", "none", "in", "EmergencyNeverChangesAuthority", "[[green|holds]] (8,649)"],
         "accent": "green"},
        {"cells": ["a1-nor7", "none", "out", "EmergencyNeverChangesAuthority",
                   "[[green|holds]]: **dropping R7 changes nothing** (69,129)"], "accent": "green"},
        ["a1-reach", "none", "in", "NeverEmergencyAct", "counterexample ✓ (2,894)"],
        ["a1-second", "none", "in", "NeverSecondRound", "counterexample ✓ (3,846)"],
        {"cells": ["a1-scope", "M_SCOPE", "in", "EmergencyNeverChangesAuthority",
                   "[[red|breaks]]: the mechanism ignores the lease's alphabet (2,388)"], "accent": "red"},
        ["a1-kind", "M_KIND", "in", "EmergencyNeverChangesAuthority",
         "holds: an authority act in the kind is refused at activation (961)"],
        ["a1-kindx", "M_KIND", "in", "NeverEmergencyAct", "holds: nothing is activated (961)"],
        {"cells": ["a1-kindr7", "M_KIND", "out", "EmergencyNeverChangesAuthority",
                   "[[red|breaks]]: R7 is what refuses it (18,763)"], "accent": "red"},
    ], size=13.5, accent="violet") + 10
    ry += c.para(rx, ry, rw, "`BreakGlass_A1-results-2026.10.05.txt`, 8 rows, distinct states in brackets. Certified: "
                 "26 trivial, 18 by SMT, 1 LS4 step. **NonComposition_A1**'s three mutations: **M1** F1 dropped from "
                 "erasure's denials; **M2** a live emergency lease widens the erasure envelope; **M3, new with the "
                 "seating**, an activation's record kept only while its round is live. Each breaks both NC-1 and "
                 "NC-2. Certified: 57 trivial, 36 by SMT, 3 LS4 steps.", 13.5, "muted")
    y = c.ymax + 70

    # ================================================================== the reference
    c.text(X0, y + 22, "At the reference: the `emergency` stage, since `9c57221` (ADR-0033 A12)", 22, "teal",
           bold=True)
    c.status(X0 + text_width("At the reference: the `emergency` stage, since `9c57221` (ADR-0033 A12)", 22, True)
             + 20, y + 4, "built", "five §9 behaviours seen")
    y += 50
    lw_ = 1900
    th = c.table(X0, y, [("Debt", lw_ * 0.2, {"bold": True}), ("Record", lw_ * 0.12),
                         ("What the reference does now", lw_ * 0.46), ("Checked by", lw_ * 0.22)], [
        ["An activation by the roster's quorum, with no operator request", "ADR-0052 §1, §2",
         "A seat of kind `emergency`, a Run seat issued `Consult`, `Actuate` and `Report`. An emergency seating names the "
         "persons who may hold it, its bundle, its envelope and the labels a task may carry. An activation names one "
         "person, one round and the task, and carries the roster members' signatures over exactly that; every replica "
         "counts distinct roster keys against the issued quorum and grants one lease. The unsigned grant does not "
         "lease the seat", "`emergency.rs`: `an_emergency_lease_has_a_roster_quorum`; `e2e.rs`: "
                            "`break_glass_is_an_emergency_seating`, step 1"],
        ["The envelope, and the person told what is in it", "§2; ADR-0048 §2",
         "By default every Run entry of the seating's own bundle and of every revision a seating in force in the domain "
         "names, computed at activation and fixed for the round; or the entries a seating names. It is the round's tool "
         "list and its opening record. A call is decided against the revision that holds its entry, and is admitted by "
         "`R1`, with no Observer live", "steps 1 and 2; `floor.rs`: the stage's 107 cases"],
        ["The person acts, and no agent does", "§1",
         "The lease holds the person's key. Every action under it carries a proof signed with that key, checked at "
         "decide and at apply; there is no bearer token to it", "`the_actions_are_the_persons`; step 2"],
        ["One round, and nothing after it", "§3",
         "An operator's `Regrant` or `Renew` naming the seat is refused, and so is an unsigned renewal. Another round "
         "is another quorum. Any operator of the domain ends or revokes it; a fence ends it",
         "`an_emergency_lease_is_one_round`; `an_operator_ends_it_and_x1_is_retired`; step 3"],
        ["What is recorded, and the drill", "§5, §6",
         "Each activation is in the replicated state with its approvers, its seating's drill mark and its envelope, and "
         "has no field for a reason. The `Actuate` record says `seatKind`; the admit is marked `emergency`. A drill "
         "seating takes the real quorum and admits its one inert tool",
         "`a_drill_is_a_real_activation_on_the_log`; step 4"],
        {"cells": ["X1 retired", "§2; ADR-0013 §2",
                   "The linked floor has no `X1-break-glass`. A `BreakGlassApprove` is refused at apply, and a quorum "
                   "of such approvals admits nothing", "`exception_count_is_one_under_r6`; "
                                                       "`tools_break_glass_issuance_and_partition`"],
         "accent": "grey"},
    ], size=13.5, accent="teal")
    c.para(X0, y + th + 12, lw_, "ADR-0033 A12's table, as ratified (its \"Proposed\" speaks as of its drafting). "
           "**131 tests** at `9c57221`, five added in `emergency.rs`; **133** at `075b2e7` (A15). Trace validation was "
           "behind at A12 and **was rerun at A14**: `spec/Mechanism.tla` models an activation and rejects X1's approval, "
           "82 traces matching (G10 §3). A matching trace is drift detection on tested paths, not a refinement. Code: "
           "`control.rs` (`EmergencySeating`, `Activation`, `ActivationRecord`, `Envelope::Domain | Named`), "
           "`state.rs` (`apply_activate`), `tests/emergency.rs`.", 13.5, "muted")
    rx = X0 + lw_ + 50
    rw = X1 - rx
    ry = y
    ry += c.card(rx, ry, rw, "What is the reference's own (I48)", [
        "**(a) The seating is prepared by the BOOTSTRAP path** (`prepare_emergency`, unsigned), which stands in for a "
        "promotion.",
        "**(b) The ordering replica computes the envelope**; operators' seatings count (result 5).",
        "**(c) The person's Persona is the digest of the key**, and the lease's principal is the key.",
        "**(d) A delivery table needs a row for** `emergency` or the person gets handles (result 6).",
        "**(e)** `BreakGlassRules.tools` and `.actions` are read by nothing now; the roster and its quorum are what "
        "an activation uses.",
    ], accent="teal", size=14) + 16
    ry += c.card(rx, ry, rw, "Not built at the reference", [
        "**A seating prepared by promotion** (ADR-0052 §9).",
        "**A socket path for a person's signed action**: the agent socket's protocol carries no proof, so the person "
        "acts in-process, as the tests do (I48).",
        "**Anything that counts the drill**: activations with the drill mark are on the log, by epoch; nothing "
        "counts them or reports them.",
        "**A read path for topics**: operators read the emergency seat's topic only in that nothing stops them "
        "(G10 item 46).",
    ], accent="red", size=14, status="notbuilt", tint=False)
    y = c.ymax + 70

    # ================================================================== exit from provisional, and options
    c.text(X0, y + 22, "The exit from provisional (ADR-0052 §9, R6; G10 item 92)", 22, "amber", bold=True)
    c.status(X0 + text_width("The exit from provisional (ADR-0052 §9, R6; G10 item 92)", 22, True) + 20, y + 4,
             "open", "item 92")
    y += 50
    ex_w = 1300
    ey0 = y
    for t, acc, st, ext, b in [
        ("1 · ADR-0050 stops being provisional", "blue", "provisional", "item 88", [
            "The seating, a person's Persona and the operators who read the topic are ADR-0050's. Its exit: a first "
            "lease from a completed tally with a promoted seating; the first operators seated by an anchor issuance; "
            "a `Regrant` at rung 1 or above; an operator's Persona record and lineage; a review (B5)."]),
        ("2 · The seating is prepared by promotion at the reference", "red", "notbuilt", "BOOTSTRAP stands in", [
            "§2's first step is made today by the unsigned socket, as ADR-0050's first seating is."]),
        ("3 · The two questions are answered in the record", "amber", "open", "results 5, 6", [
            "Whether an operator's seating is \"a seating in force in the domain\" for the envelope; whether a "
            "delivery table must have a row for the `emergency` kind."]),
        ("4 · A reader who is not the drafter has reviewed it", "amber", "open", "ADR-0029 A2.5", [
            "No reader other than the drafter has. The custodian then records the exit by a History row (ADR-0029 A4)."]),
        ("G10 item 92 also lists", "amber", "open", "", [
            "**A socket path for a person's signed action**, and **something that counts the drill**."]),
    ]:
        y += c.card(X0, y, ex_w, t, b, accent=acc, size=14, status=st, status_extra=ext,
                    tint=st != "notbuilt") + 12
    y += c.para(X0, y, ex_w, "**Also open** (Open obligations): the roster's `k`, and whether the rules floor bounds it "
                "for activation as R9 bounds a promotion's; how many persons a seating names, and whether the person "
                "seated may be on the roster that seats them; the drill period's value, and the correlator fold that "
                "counts epochs without a drill (ADR-0051, Proposed); rows for the three modules in the binding table "
                "(G10 item 90).", 13.5, "muted")
    rx = X0 + ex_w + 50
    rw = X1 - rx
    c.text(rx, ey0 + 16, "Options considered (ADR-0052, the record's table)", 17, "ink", bold=True)
    c.table(rx, ey0 + 30, [("Option", rw * 0.38, {"bold": True}), ("Disposition", rw * 0.62)], [
        ["Keep X1, and scope its approval to the round", "Not taken, by the custodian's decision to take both changes. "
         "It would bound the grant in time and leave an agent's seat elevated and a second floor exception in place"],
        {"cells": ["Keep X1, exempt from R3, with no bound", "Superseded. It was the position earlier on 2026.10.04: "
                   "an approved seat could actuate with no Observer for as long as the epoch lasted"], "accent": "grey"},
        {"cells": ["A timed expiry (R8)", "Withdrawn earlier the same day: it needs trusted time. The round's lease "
                   "gives the bound without it (§3)"], "accent": "grey"},
        ["A count of admits", "Declined earlier the same day, and now given by the round bound `R`"],
        ["The emergency seat as a `thinker` seat with a flag", "Not taken (drafter's choice). The lease's field set "
         "is closed (ADR-0031 §1), and R3 and B10 are written over kinds. A kind says it in the place the floor reads"],
        ["One envelope for each foreseen emergency", "Not required ⟨R1⟩. A deployment may prepare narrower seatings; "
         "the default is the domain's envelope, which needs no foresight about the emergency"],
        ["A fixed generic envelope, naming one bundle revision", "Not taken ⟨R1⟩. It goes stale at the next "
         "promotion, and an emergency path that is out of date is found to be so during an emergency"],
        {"cells": ["A general-purpose tool in the envelope: a shell, or a client for any address", "Rejected. A tool "
                   "is held to the channel it declares, in an emergency as at any other time (ADR-0040 §3)"],
         "accent": "red"},
        {"cells": ["Activation by an operator's regrant of a prepared seating", "Rejected. One operator would then "
                   "add authority alone"], "accent": "red"},
        {"cells": ["Activation by a promotion", "Rejected. It is the path break-glass exists to be faster than, and a "
                   "veto-seat outage blocks it"], "accent": "red"},
        {"cells": ["A reason field on the activation", "Rejected, by the custodian's decision. The mechanism does not "
                   "know the reason, and a field would say it did"], "accent": "red"},
        ["A drill as a precondition of a real activation", "Not taken (drafter's choice). It would refuse an "
         "emergency for want of a rehearsal. The custodian may prefer it; §6 is the only section that changes"],
        ["The emergency Persona attested by single sign-on", "Not taken (drafter's choice). The path would fail with "
         "the provider"],
    ], size=13.5, accent="grey")
    y = c.ymax + 40

    # costs strip
    y += c.para(X0, y, WW, "**Costs the record states** (Consequences): the person holds **the widest authority in the "
                "domain for the round** under the default envelope, bounded by the quorum that seated them, the one "
                "round, any operator's revocation and the label forbids; an emergency that needs a capability no tool "
                "in the domain has takes a promotion, as it did under X1; a person who holds the key, and the roster's "
                "quorum, must be available; **an agent cannot be given more in an emergency**; the label forbids bind "
                "the person; a drill is a real quorum, every epoch in every domain; five accepted records moved, two by "
                "reversal; **one author, one day**.", 14, "ink") + 30
    c.legend(X0, y, [
        ("box", "blue", "authority, provisional record", "4 3"), ("box", "teal", "mechanism, built at reference"),
        ("box", "green", "a lease's end, the safe direction"), ("box", "brown", "roster, forensic record"),
        ("box", "pink", "readers who can stop it"), ("box", "violet", "TLA+ module, drill"),
        ("box", "amber", "open question"), ("box", "red", "not built, refused", "2 3"),
        ("box", "grey", "retired, withdrawn", "6 4"),
        ("arrow", "red", "not built at the reference", "7 5"), ("arrow", "green", "subtracts", "7 5"),
    ])
    return c
