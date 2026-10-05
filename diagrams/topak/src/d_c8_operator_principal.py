"""C8 — The operator is a principal: ADR-0050 (provisional). A seat, a Persona, a lease and a floor for the actor who
issues every lease; the intended path beside the reference's; the control entries; and what is checked."""
from lib import Canvas

ID, SLUG = "C8", "operator-principal"

Y = "[[green|permit]]"
F = "[[red|forbid]]"


def build():
    c = Canvas(ID, "The operator is a principal: seated by a quorum, renewing under a lease, denying without one",
               "Every authority in the corpus had a model except the one that issues every lease: **the operator was "
               "whoever could reach a socket** (CR-34). ADR-0050 applies the pattern's oldest rule to it: **adding "
               "takes a quorum, and denying is local.** It is in force and **provisional** (ADR-0029 A4): its centre, "
               "a first lease from a quorum, is **not built**, and no reader other than the drafter has reviewed it. "
               "At the reference the unsigned socket stands in as a **BOOTSTRAP** path that seats and does nothing "
               "else (ToO §7.10; G10 §1.2, §8).",
               3400, "ADR-0050 Context, §1–§10, Options, Findings, History R1–R10, B34; ADR-0041 A3 (`C1`–`C9`); ADR-0031 "
                     "A3; ADR-0037 A4, §7; ADR-0016 A1; ADR-0025 A3 (§1 (a), (f)); ADR-0029 A3, A4; ADR-0045 A2 "
                     "(T-0045-35, T-0045-36, Annex B); ADR-0028 F2; ADR-0035 §1, D-0035-1; ADR-0039 §2; ADR-0038 §2; "
                     "ADR-0047 §1; ADR-0052 §2, §3 (R6); ADR-0033 A11, A13, A14; floor/proposed/control-floor.cedar "
                     "(4341ede9e26419cc; 29 policies, 106 cases) and emergency-floor.cedar (15c941b9a56a09f7; the "
                     "`C` entries identical); spec/Operators.tla (a465d7af62becd03), "
                     "spec/Operators-results-2026.10.04.txt, spec/Operators_proof.tla (226230ef1e56b413), "
                     "Operators-proof-results-2026.10.04.txt, Operators-proof-cert-results-2026.10.04.txt; "
                     "spec/Mechanism.tla (e29dbaf0936dbae1), spec/Mechanism-trace-results-2026.10.05.txt; mechanism "
                     "topak-core src/control.rs (`ControlAction`, `ControlRequest`, `ControlFacts::permitted`, "
                     "`sign_on_verifies`, `Seating`), src/types.rs (`SeatKind`), tests/operators.rs; topak-node "
                     "src/ops.rs (`OperatorOp`), tests/e2e.rs; mechanism/GAPS-AND-ASSUMPTIONS.md I47; ToO rev 14 §2.5, "
                     "§2.8, §7.10; glossary (operator, seating, successor grant, control alphabet); G10 §1.1, §1.2, "
                     "§2.2, §2.3, §2.6, §3, §4, §8, §7 items 41, 46, 57, 88, 90, 96")
    X0, X1 = c.x0, c.x1
    W = X1 - X0
    y = c.y

    # ------------------------------------------------------------------ status strip
    sx = X0
    c.text(sx, y + 16, "ADR-0050", 16, "ink", bold=True)
    sx += 90
    sx += c.status(sx, y, "provisional", "C1, C3, C4 · Batch 34 at R10") + 12
    c.text(sx, y + 16, "Drafted 2026.10.04, ratified 2026.10.05 with nine dependent amendments (ADR-0016 A1, ADR-0024 "
           "A3, ADR-0025 A3, ADR-0029 A3, ADR-0031 A3, ADR-0037 A4, ADR-0041 A3, ADR-0043 A2, ADR-0045 A2), each in "
           "force and subject to redesign with it", 14, "muted")
    y += 52

    # ------------------------------------------------------------------ band 1: before, the seat, the person
    g = 40
    w3 = (W - 2 * g) / 3
    xa, xb, xc = X0, X0 + w3 + g, X0 + 2 * (w3 + g)

    # col 1: the Context table
    c.heading(xa, y, "Before: the requests that make leases (Context)")
    cols = [("Request", w3 * 0.24, {"mono": False}), ("Effect on authority", w3 * 0.25), ("Signed", w3 * 0.15),
            ("What stands behind it", w3 * 0.36)]
    rows = [
        ["`Issue`", "Adds", "By anchors", "The rules floor"],
        ["`BreakGlassApprove`", "Adds", "By the roster", "The replicated state machine"],
        {"cells": ["`Grant`, `Launch`, `Renew`", "Adds: a lease, or more of one", "[[red|No]]", "Apply-time checks"],
         "accent": "red"},
        {"cells": ["`GatesPassed`", "Adds: unlocks votes", "[[red|No]]", "Nothing (G8)"], "accent": "red"},
        {"cells": ["`RegisterProfile`", "Adds: a profile a lease may name", "[[red|No]]",
                   "That the profile was promoted"], "accent": "red"},
        {"cells": ["`Revoke`, `FenceEpoch`, `EndRound`", "Subtracts", "[[red|No]]",
                   "Nothing; the attribution is free text"], "accent": "red"},
    ]
    ty = y + 40
    t1 = c.table(xa, ty, cols, rows, size=13.5, accent="grey")
    p1 = c.para(xa, ty + t1 + 14, w3,
                "`ops.rs` as read on 2026.10.04. **Five requests added authority on a file's permission bits; a stop "
                "was unattributed** (ADR-0028 F2 asks for a signature, and got a string); **the task was not on the "
                "channel**, so ADR-0043 §1's first item of ingress had no record (findings 1, 2).", 13.5, "muted")
    col1_bot = ty + t1 + 14 + p1

    # col 2: the seat, and where first leases come from
    b1 = [
        "**A fourth seat kind**, declared in the issued rules with a domain; its alphabet is the control alphabet and "
        "nothing else: an operator does not author, vote or actuate (ADR-0037 A4).",
        "**Only a person holds one**, a rule about what may be promoted to the seat; the mechanism cannot tell a "
        "person from a program holding the person's key (§8).",
        "**A person holds one seat**: one who operates and votes is two principals (ADR-0037 §7).",
        "`Mediated`: a person cannot be confined; what the record gives is attribution and authorization.",
        "**Treated as havoc**, like every principal. Nothing rests on an operator's honesty: it rests on a quorum "
        "having seated it, a peer being present, and the envelope of §4.",
    ]
    h1 = c.card(xb, y, w3, "§1 An operator holds a seat of kind `operator`", b1, accent="brown", size=13.5,
                status="provisional")
    cols = [("First lease of", w3 * 0.38), ("Comes from", w3 * 0.3), ("Why", w3 * 0.32)]
    ty2 = y + h1 + 18
    c.text(xb, ty2 + 16, "**§2 First leases come from a quorum, never from an operator**", 15, "ink")
    t2 = c.table(xb, ty2 + 30, cols, [
        ["A seat on a roster the rules name (grant, veto, anchor) at genesis, and the first operators",
         "An anchor issuance (ADR-0025 A3 (a); ADR-0029 §5, A3)", "Something must be seated before anything can be "
                                                                  "promoted"],
        ["Every other principal, operators included", "A promotion (ADR-0024, A3)", "\"Promotion is a grant\""],
    ], size=13.5, accent="blue")
    p2 = c.para(xb, ty2 + 30 + t2 + 12, w3,
                "**What is promoted is a seating**: the principal, seat, Persona, bundle revision, confinement profile "
                "and rung, alphabet, and the labels a task for it may carry. When the tally completes the mechanism "
                "grants the first lease at a fresh fence. A quorum acts once per seating; round by round one operator "
                "acts.", 13.5, "ink")
    col2_bot = ty2 + 30 + t2 + 12 + p2

    # col 3: the person, the provider, the key
    b3 = [
        "**A Persona record** binds a signing key, a role, a domain and a lineage, with a sequence number; no weights, "
        "prompt or decoder (ADR-0016 A1).",
        "**Its lineage's root is the identity provider** that vouches for the person, declared and not projected "
        "(ADR-0035 D-0035-1). **Two operators behind one provider are not independent.**",
        "**The sign-on assertion**, signed by the provider, names the Persona's key and the fence the mechanism asked "
        "it to name. **Read only at a lease boundary**, and for a deny with no live lease (§4). **No wall clock is "
        "read**: it is fresh because of what it names.",
        "**Between boundaries a request is signed with the Persona's key**, which the mechanism checks itself.",
        "**The provider's key is issued** (ADR-0025 A3 (f), provisional, in the bootstrap set): a trust root for the "
        "operators it vouches for and no others.",
    ]
    h3 = c.card(xc, y, w3, "§3 A Persona, a lineage, and sign-on at the lease boundary", b3, accent="brown",
                size=13.5, status="provisional", tint=False)
    cols = [("Row", w3 * 0.14, {"bold": True}), ("Trusted for", w3 * 0.3), ("Failure can produce", w3 * 0.28),
            ("Identity fixed by; residual", w3 * 0.28)]
    ty3 = y + h3 + 18
    c.text(xc, ty3 + 16, "**ADR-0045 A2: two rows in the people table, both trust roots**", 15, "ink")
    t3 = c.table(xc, ty3 + 30, cols, [
        ["T-0045-35 · an operator's identity provider", "Vouches, at a lease boundary, only for the person it "
                                                        "enrolled, and names the key and the fence it was asked to",
         "A forged operator: its adds within §4's envelope, its denies anywhere in its domain",
         "Issuance of the provider's key. Bounded by the peer rule only if peers have different providers "
         "(D-0050-2); a provider that is down silences operators whose leases have lapsed"],
        ["T-0045-36 · an operator's custody of its key", "The key is used by the person and nobody else",
         "Whatever that operator may do, done by another",
         "Promotion of the operator's Persona. \"Only a person\" is a rule about what is seated"],
    ], size=13.5, accent="brown")
    p3 = c.para(xc, ty3 + 30 + t3 + 12, w3,
                "**At the reference, in part** (Annex B, A2): a provider's key is in the issued rules and its assertion "
                "is read at the lease boundary; nothing compares two operators' providers; **an operator's Persona is "
                "its seat's key**, with no record behind it (I47).", 13.5, "muted")
    col3_bot = ty3 + 30 + t3 + 12 + p3
    y = max(col1_bot, col2_bot, col3_bot) + 70

    # ------------------------------------------------------------------ band 2: two paths to a first lease
    rtop = y
    iy = rtop + 56
    pad = 30
    wl = 900
    wm = 640
    wr = W - 2 * pad - wl - wm - 2 * 140
    xl = X0 + pad
    xm = xl + wl + 140
    xr = xm + wm + 140
    bq = [
        "**A promotion's tally on a seating** (ADR-0024 A3): every principal, operators included.",
        "**An anchor issuance** (ADR-0025 A3 (a)): the rostered seats and, at bootstrap, **the first operators, at "
        "least three in each domain** at the archetype (ADR-0029 A3, provisional).",
        "No operator's request is involved. **Not built**: neither a promoted seating nor an issuance that seats "
        "(G10 item 88; ADR-0033 A11).",
    ]
    bb = [
        "**Kept by the custodian's decision** (ADR-0050 R9), for first seating only: the unsigned `Grant` and `Launch` "
        "seat, standing in for the quorum. **Whoever reaches the socket can seat**: D-0050-1 for that one step.",
        "Where the rules declare an operator, the unsigned `Renew`, `EndRound`, `Revoke`, `FenceEpoch` and "
        "`GatesPassed` are **refused at apply** (`the_unsigned_path_seats_and_does_nothing_else`). It refuses a grant "
        "that keeps a seated binding while two operators of the domain are live: that is their successor to make.",
        "`Launch` and `RegisterProfile` are still unsigned; a deployment that declares no operator is D-0050-1 whole "
        "(I47 (a), (b)).",
    ]
    hq = c.card(xl, iy, wl, "The intended path (§2): a quorum completes", bq, accent="blue", size=13.5,
                status="notbuilt", dash="7 5")
    hb = c.card(xl, iy + hq + 40, wl, "The reference's path: the unsigned socket, a BOOTSTRAP path", bb, accent="red",
                size=13.5, status="built")
    bf = [
        "The mechanism grants it at a fresh fence and records the **seating** with it (`State.seatings`): the binding "
        "every successor keeps and may not widen, and the labels a task may carry.",
        "**An operator's first lease needs a sign-on assertion** under a provider key the rules issue, naming the "
        "seat's key and its current fence (A11; I47 (d)).",
        "A seating is a thing of record (G10 item 41); at the reference the BOOTSTRAP path makes it.",
    ]
    mid_top = iy + 30
    hf = c.card(xm, mid_top, wm, "A first lease, and a seating", bf, accent="teal", size=13.5)
    bo = [
        "**Each holds a live lease** in its domain, at rung 0: a person is `Mediated` (G10 §2.3).",
        "**Each is in the others'** `W(p)`: every control action is written to the operator's round topic, or to the "
        "`after` companion of its last round when it holds no lease (§6; A11).",
        "**An add needs a live peer** (`C5`): presence, as R3 couples a Thinker to its Observer (ADR-0039 §2), and "
        "nothing the peer has read; there is no watermark (finding 6).",
        "**Three at the archetype** (R5). With two, either can keep the other seated by renewal and **neither can "
        "recover the other's lapse**: an operator's next round granted by a peer is unreachable with two and reached "
        "with three (`Operators.tla` w8, w9). Two is D-0050-3.",
        "**When none holds a live lease, nothing in the domain can be regranted**: it stalls until a quorum seats an "
        "operator again. Stall, not proceed.",
    ]
    ho = c.card(xr, iy, wr, "Seated operators: at least three per domain", bo, accent="brown", size=13.5)
    bs = [
        "**A successor grant** (`Regrant`): the principal's next round, every field the last lease's or narrower, only "
        "`round` advancing. **A renewal** (`Renew`) keeps the round (ADR-0031 §4). Both are monotone: an operator can "
        "keep a quorum's grant going and narrow it, never widen it.",
        "**Anything else is a first lease**: a different Persona, bundle, confinement profile or seat, or an alphabet "
        "with a variant the last lease lacked, needs a seating and a quorum.",
        "**An emergency seating is one of these** (R6; ADR-0052 §2, §3): activated for one round by the break-glass "
        "roster's quorum; an operator's `Regrant` or `Renew` naming it is refused.",
        "The cost, on purpose: changing a principal's Persona or bundle rides a tally, not an operator's quick regrant "
        "(Consequences).",
    ]
    sy = iy + ho + 50
    hs = c.card(xr, sy, wr, "Then, round by round: one operator acts (§2; ADR-0031 A3)", bs, accent="blue",
                size=13.5, status="provisional")
    c.arrow([(xr + 120, iy + ho), (xr + 120, sy)], "brown", sw=2.2, label="`Regrant`, `Renew`", lpos=0.5,
            loff=(80, 0), lsize=12.5)
    rbot = max(iy + hq + 40 + hb, mid_top + hf, sy + hs) + 34
    c.region(X0, rtop, W, rbot - rtop, "How a principal comes to hold a lease (§2, §6; ADR-0031 A3)", "teal",
             dash=None, sw=2.4, size=16)
    ya = mid_top + 50
    c.arrow([(xl + wl, iy + hq / 2), (xl + wl + 75, iy + hq / 2), (xl + wl + 75, ya), (xm, ya)], "red",
            dash="7 5", sw=2.2, label="not built", lpos=0.12, lsize=12.5)
    yb = mid_top + hf - 50
    c.arrow([(xl + wl, iy + hq + 40 + hb / 2), (xl + wl + 75, iy + hq + 40 + hb / 2), (xl + wl + 75, yb), (xm, yb)],
            "red", sw=2.4, label="BOOTSTRAP", lpos=0.1, lsize=12.5)
    c.arrow([(xm + wm, mid_top + hf / 2), (xr, mid_top + hf / 2)], "teal", sw=2.4, label="seats", lpos=0.5,
            lsize=12.5)
    y = rbot + 60

    # ------------------------------------------------------------------ band 3: the signed request, end to end
    c.heading(y=y, x=X0, s="The signed request, end to end (§3, §4; ADR-0033 A11; `control.rs`, `ops.rs`)", size=20)
    pw_ = c.status(X1, y + 2, "built", "A11 · 126 tests then, 133 at G10", anchor="end")
    y += 44
    n = 6
    gap = 46
    pwid = (W - (n - 1) * gap) / n
    steps = [
        ("1 · The identity provider", "brown", [
            "Signs an assertion (purpose `sign-on`) naming the operator's key, the fleet epoch and the fence of the "
            "seat's last lease (`sign_on_body`).",
            "Accepted only under a key the rules issue (`sign_on_verifies`).",
            "**T-0045-35.** An assertion is good for one lease boundary, or, with no lease, for every deny until the "
            "operator is seated again or the fleet is fenced (I47 (d)).",
        ]),
        ("2 · The operator signs a request", "brown", [
            "`ControlRequest { operator, epoch, ctr, action }`, signed with the seat's key (purpose `control`); "
            "`epoch` fences it, `ctr` orders it so it cannot be replayed.",
            "A deny with no live lease carries the operator's own assertion; a `Regrant` carries the task's digest and "
            "label, its bytes beside the request.",
            "**T-0045-36**: the key is the person's.",
        ]),
        ("3 · The deciding replica decides", "teal", [
            "Computes **thirteen facts** about the operator, the target and the request (`ControlFacts`); **the "
            "operator supplies none**.",
            "Lifts them into schema S's `ControlCtx` and asks the floor: `C1` to `C9` decide. **There is no bundle "
            "tier.**",
            "The floor is the `emergency` stage, **genesis-provisional** (G10 §2.2).",
        ]),
        ("4 · Ordered on the log", "teal", [
            "The entry carries the request, its signature, the assertion where one was given, and the facts "
            "(`Control`).",
            "A deny is consensus-ordered like every revocation, and needs no quorum and no peer (§4).",
            "**The signature is the stop's attribution** (ADR-0028 F2).",
        ]),
        ("5 · Every replica, at apply", "teal", [
            "Verifies the signature is the seat's; refuses a replayed counter.",
            "**Recomputes the facts** against its own state at that log position and **refuses the entry if they "
            "differ**.",
            "**Restates the envelope** (`ControlFacts::permitted`), returning the entry that refuses, then does what "
            "the request says.",
            "The envelope is stated twice, Cedar and Rust; only the tests hold them together (I47 (e)).",
        ]),
        ("6 · Written to the operator's topic", "pink", [
            "Each ordered request goes to the operator's round topic, or the `after` companion of its last round.",
            "Every other operator in the domain is in its `W(p)`. **A finding is a deny**, made under the finder's own "
            "signature; no operator can undo a peer's deny (§6).",
        ]),
    ]
    sh = max(c.card(0, 0, pwid, t, b, size=13.5, draw=False) for t, _, b in steps)
    for i, (t, a, b) in enumerate(steps):
        x = X0 + i * (pwid + gap)
        c.card(x, y, pwid, t, b, accent=a, size=13.5, h=sh, tint=(a != "pink"))
        if i < n - 1:
            c.arrow([(x + pwid, y + 60), (x + pwid + gap, y + 60)], a if a != "brown" else "brown", sw=2.4)
    y += sh + 66

    # ------------------------------------------------------------------ band 4: the mapping, six actions to nine entries
    c.heading(X0, y, "§4 The control alphabet, and the floor entries that decide each request (ADR-0041 A3)", size=20)
    pw_ = c.status(X1, y + 2, "genprov", "the floor · G10 §2.2", anchor="end")
    c.status(X1 - pw_ - 10, y + 2, "provisional", "ADR-0041 A3 · C1", anchor="end")
    y += 44
    ce = ["C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9"]
    cw_ = 168
    lead = [("Variant", 140, {}), ("Kind", 70, {"bold": True}), ("What it does (§4)", 420), ("Needs (§4)", 520)]
    rest = W - sum(x[1] for x in lead) - 9 * cw_
    lead[2] = ("What it does (§4)", 420 + rest / 2)
    lead[3] = ("Needs (§4)", 520 + rest / 2)
    cols = lead + [(f"`{e}`", cw_) for e in ce]
    D = "—"
    rows = [
        {"cells": ["`Regrant`", "[[blue|Add]]", "A successor grant to a principal in the operator's domain, with the "
                                                "round's task (§5)",
                   "A live lease; a live peer (§6); the target seated and not revoked; every field the last lease's or "
                   "narrower",
                   Y + ": operator, own domain, seated, not live, same binding, next round, alphabet within the last",
                   D, D, D, F + " with no live lease or no live peer", F + " if the target is itself", D,
                   F + " a task unlabelled, or labelled outside the seating's", D], "accent": "blue"},
        {"cells": ["`Renew`", "[[blue|Add]]", "A renewal of a live lease in the domain (ADR-0031 §4)", "The same",
                   D, Y + ": operator, own domain, target live", D, D, F + " with no live lease or no live peer",
                   F + " if the target is itself", D, D, D], "accent": "blue"},
        {"cells": ["`AttestGates`", "[[blue|Add]]", "Records that the gates ran on an artifact, with the evidence's "
                                                    "digest; attributed and still an assertion (G10 item 57)",
                   "A live lease in Build; a live peer", D, D, Y + ": operator, in Build", D,
                   F + " with no live lease or no live peer", D, D, D, D], "accent": "blue"},
        {"cells": ["`EndRound`", "[[red|Deny]]", "Ends one principal's round",
                   "An operator Persona in force, and either a live lease or a fresh sign-on assertion (R1)",
                   D, D, D, Y + ": operator, Persona in force, live lease or fresh assertion", D, D, D, D,
                   F + " a target in another domain"], "accent": "red"},
        {"cells": ["`Revoke`", "[[red|Deny]]", "A targeted revocation (ADR-0031 §5)", "The same",
                   D, D, D, Y + ": the same", D, D, D, D, F + " a target in another domain"], "accent": "red"},
        {"cells": ["`FenceEpoch`", "[[red|Deny]]", "The fleet fence", "An operator Persona in force **and a live "
                                                                       "lease** (R5)",
                   D, D, D, Y + ": the same; reads no property of its target", D, D,
                   F + " with no live lease", D, D], "accent": "red"},
    ]
    y += c.table(X0, y, cols, rows, size=13.5, accent="brown") + 30

    # the entries' table and the facts side by side
    lw = W * 0.56
    rw = W - lw - 40
    c.text(X0, y + 16, "**ADR-0041 A3: the nine entries, as ratified**", 15, "ink")
    c.text(X0 + lw + 40, y + 16, "**The thirteen facts the mechanism computes, and who reads them** (`ControlFacts`)",
           15, "ink")
    y += 30
    cols = [("Id", lw * 0.2, {"mono": True}), ("Kind", lw * 0.07, {"bold": True}), ("Action", lw * 0.14),
            ("Holds when", lw * 0.43), ("From", lw * 0.16)]
    te = c.table(X0, y, cols, [
        ["C1-regrant-successor", Y, "`Regrant`", "the seat's kind is `operator`, the target is in its domain, was "
                                                  "seated by a quorum and is not revoked, has no live lease, and every "
                                                  "field of the new lease is the last lease's or narrower, with `round` "
                                                  "advanced by one", "ADR-0050 §2, §4"],
        ["C2-renew", Y, "`Renew`", "the seat's kind is `operator`, and the target holds a live lease in its domain",
         "ADR-0050 §4; ADR-0031 §4"],
        ["C3-attest-gates", Y, "`AttestGates`", "the seat's kind is `operator`, in Build", "ADR-0050 §4"],
        ["C4-deny", Y, "`EndRound`, `Revoke`, `FenceEpoch`", "the seat's kind is `operator`, its Persona is in force, "
                                                              "and it holds a live lease or presents a fresh sign-on "
                                                              "assertion", "ADR-0050 §4 (R1)"],
        ["C5-add-needs-lease-and-peer", F, "`Regrant`, `Renew`, `AttestGates`", "the operator holds no live lease, or "
                                                                                 "no other operator in the domain does",
         "ADR-0050 §4, §6"],
        ["C6-no-self", F, "`Regrant`, `Renew`", "the target is the operator itself", "ADR-0050 §4"],
        ["C7-fence-needs-lease", F, "`FenceEpoch`", "the operator holds no live lease", "ADR-0050 §4 (R5)"],
        ["C8-task-label-in-bounds", F, "`Regrant`", "the task carries no label, or one outside those its seating "
                                                    "allows", "ADR-0050 §5; ADR-0047 §1"],
        ["C9-stop-in-own-domain", F, "`EndRound`, `Revoke`", "the target is in another domain",
         "ADR-0050 §4 (R5), for every operator and not only a lapsed one; confirmed by the custodian (R9)"],
    ], size=13.5, accent="brown")
    cols = [("Fact (`ControlCtx`)", rw * 0.3, {"mono": True}), ("What it says", rw * 0.5), ("Read by", rw * 0.2)]
    tf = c.table(X0 + lw + 40, y, cols, [
        ["personaInForce", "The operator's Persona is promoted and not revoked", "`C4`"],
        ["hasLease", "The operator holds a live lease", "`C4`, `C5`, `C7`"],
        ["peerLive", "Another operator in the domain holds a live lease", "`C5`"],
        ["freshAssertion", "An assertion under an issued provider key names the operator's key and the current "
                           "fence", "`C4`"],
        ["targetSeated", "The target was seated, and nothing it was seated with is revoked", "`C1`"],
        ["targetLive", "The target holds a live lease", "`C1` (must not), `C2`"],
        ["sameBinding", "The new lease keeps the seating's binding (computed by the lift)", "`C1`"],
        ["nextRound", "`round` advances by one (computed by the lift: a round comparison in Cedar can overflow, which "
                      "the totality gate refuses)", "`C1`"],
        ["lastAlphabet", "The last lease's alphabet", "`C1`"],
        ["newAlphabet", "The requested alphabet; `C1` asks that the last contains all of it", "`C1`"],
        ["taskLabelled", "The task carries a label", "`C8`"],
        ["taskLabel", "The operator's signed label for the task", "`C8`"],
        ["taskLabelsAllowed", "The labels the seating allows", "`C8`"],
        {"cells": ["kind, domain, resource", "Lifted as attributes: `principal.kind`, `principal.domain`, "
                                             "`resource.domain`, and the target as the resource", "`C1`–`C4`, `C6`, "
                                                                                                  "`C9`"],
         "accent": "grey"},
    ], size=13.5, accent="teal")
    y += max(te, tf) + 20
    y += c.para(X0, y, W,
                "**A first lease is not here**: it is not an action and has no entry; the mechanism grants one when a "
                "quorum completes (§2). `B10-only-thinkers-author` is unchanged: an operator holds no authoring variant. "
                "Gated on 2026.10.04 in the `control` stage (29 policies, 106 cases, each new entry total and "
                "mattering, weakened ones classed relaxations) and carried unchanged into the `emergency` stage the "
                "reference links (28, 107). **Nine entries and not eight**: `C9` was found missing when \"own domain\" "
                "had to be written as a rule (R8). An operator may not regrant or renew itself; `Issue` and "
                "`BreakGlassApprove` are not operator variants; `RegisterProfile` stops being a request (§4).",
                14, "muted") + 50

    # ------------------------------------------------------------------ band 5: denies, observing, what nothing gates
    w4 = (W - 3 * 30) / 4
    cols = [("The operator's state", w4 * 0.5), ("It denies by", w4 * 0.5)]
    c.text(X0, y + 16, "**§4 A deny needs no lease, and a fresh credential** (R1)", 15, "ink")
    tdy = y + 30
    td = c.table(X0, tdy, cols, [
        ["A live lease", "Its key alone. The lease was attested at its last boundary (§3)"],
        ["Lease fenced or expired, Persona in force", "Its key, and a sign-on assertion naming the key and the current "
                                                      "fence"],
        {"cells": ["Persona revoked, or the provider will not vouch", "[[red|Nothing]]"], "accent": "red"},
    ], size=13.5, accent="red")
    pd = c.para(X0, tdy + td + 12, w4,
                "**A lapsed operator stops its own domain and not the fleet** (R5): `EndRound` and `Revoke` on a fresh "
                "assertion, `FenceEpoch` only with a live lease. **A key by itself is not a standing lever**: a person "
                "removed from sign-on cannot stop anything with a key nobody revoked. A provider that is down silences "
                "the lapsed, not those who hold a lease.", 13.5, "ink")
    col_a = tdy + td + 12 + pd
    cards5 = [
        ("Operators observe each other, by presence only", "pink", None, [
            "Every control action is on the operator's round topic and **every other operator in the domain reads "
            "it** (`W(p)`, ADR-0038 §2). A finding is a deny.",
            "**The peer rule reads presence and not progress**: a live lease, and nothing the peer has read. It is "
            "weaker than Observer coupling, which ADR-0039 replaced presence with for Thinkers; people do not emit "
            "heartbeats with watermarks (finding 6, open).",
            "At the archetype a peer's lineage is independent: a different identity provider. One provider is "
            "D-0050-2, and the rule then holds in letter only.",
        ]),
        ("What nothing gates", "red", "open", [
            "**Operators are readers with no read path.** They are put in each other's and the emergency seat's "
            "`W(p)`, and the mechanism has no read path for topics: **nothing gates what they read** (G10 item 46, "
            "with `W(p)` as an ACL and the gate-side `K < R` check).",
            "**What a peer must have read before an add** is outside the record (§8) and the model (`Operators.tla` "
            "header).",
            "So the record's \"operators observe each other\" is, at G10, **observation by presence**: \"operators "
            "observe each other by presence, not by anything read\" (G10 §8).",
        ]),
        ("§8 What this record does not cover", "grey", None, [
            "**That an operator is a person**: a key can be handed to a program.",
            "**A person outside the mechanism**: physical access, the host's root account, the replicas' own traffic "
            "(`mechanism/` G5, mutual authentication, unbuilt).",
            "**A compromised provider**: it can vouch for anyone it serves; independence bounds it to one operator of "
            "a pair, a single provider bounds nothing.",
            "**Gate evidence** (row 1.7), beyond attributing who asserted it; **break-glass and issuance**, which keep "
            "their own rosters; **what a peer must have read**.",
        ]),
    ]
    h5 = max(c.card(0, 0, w4, t, b, size=13.5, status=s, draw=False) for t, _, s, b in cards5)
    h5 = max(h5, col_a - y)
    for i, (t, a, s, b) in enumerate(cards5):
        c.card(X0 + (i + 1) * (w4 + 30), y, w4, t, b, accent=a, size=13.5, status=s, h=h5,
               tint=(a == "pink"), dash=("6 4" if a == "grey" else None))
    y += h5 + 60

    # ------------------------------------------------------------------ band 6: how it changes, degeneracy
    half = (W - 40) / 2
    c.heading(X0, y, "§7 How it changes")
    c.heading(X0 + half + 40, y, "§9 Degeneracy on this record")
    y += 40
    cols = [("What changes", half * 0.55), ("By whom", half * 0.45)]
    t7 = c.table(X0, y, cols, [
        ["Who is an operator; a seating; the labels a seat's tasks may carry", "A promotion"],
        ["The first operators; the identity provider's key; the `operator` seats themselves", "An anchor issuance"],
        ["A principal's next round, and its task", "One operator with a live lease and a live peer"],
        ["A stop", "Any operator whose Persona is in force: by key under a live lease, by key and a fresh sign-on "
                   "without one"],
        ["The control variants and their floor entries", "A mechanism release and a promotion, as for any floor "
                                                         "change"],
    ], size=13.5, accent="blue")
    cols = [("Id", half * 0.1, {"bold": True}), ("Kind", half * 0.11), ("Parameter → deployed value", half * 0.22),
            ("Premises falsified", half * 0.22), ("Theorems voided", half * 0.25), ("Type changes", half * 0.1)]
    t9 = c.table(X0 + half + 40, y, cols, [
        {"cells": ["D-0050-1", "Mechanism (ADR-0023 §6a)", "Operator requests → unsigned, from whoever reaches the "
                                                           "socket; grants at any time; no task carried",
                   "Every lease on the log was put there by a quorum or by an operator inside a quorum's grant; every "
                   "stop is attributed",
                   "**None in force**: no theorem takes the operator as a premise. §10's properties are lost. **At the "
                   "reference, for a first seating** (the BOOTSTRAP path), and whole where no operator is declared",
                   "None"], "accent": "red"},
        ["D-0050-3", "Deployment", "Operators in a domain → two", "A lapsed operator's lease can be regranted by a "
                                                                  "peer",
         "None. Every safety property holds; a lapse by either stalls the domain until a quorum seats it again "
         "(`Operators.tla` w8, w9)", "None"],
        ["D-0050-2", "Deployment", "Operators' identity providers → one", "A peer is independent of the operator it "
                                                                          "watches",
         "None. The peer rule still holds in letter; one provider can produce both", "None"],
    ], size=13.5, accent="red")
    y += max(t7, t9) + 60

    # ------------------------------------------------------------------ band 7: what is checked
    c.heading(X0, y, "Checked, proved and certified: `spec/Operators.tla` (ADR-0050 §10)", size=20)
    c.status(X1, y + 2, "accepted", "ADR-0046 A1 · certified", anchor="end")
    y += 44
    lw = W * 0.5
    rw = W - lw - 40
    c.text(X0, y + 16, "**TLC, 32 rows** (`Operators-results-2026.10.04.txt`, after R5): MaxRound 2, one worker, "
           "operators {a, b} or {a, b, c}. Each mutation breaks what the module says it must; ✓ a witness reached",
           14.5, "ink")
    cols = [("Row", lw * 0.08, {"mono": True}), ("Ops", lw * 0.05), ("Mutation", lw * 0.15, {"mono": True}),
            ("Invariant", lw * 0.28, {"mono": True}), ("Result", lw * 0.18, {"bold": True}),
            ("What the row shows", lw * 0.26)]
    V, HO = "[[red|violated]]", "[[green|holds]]"
    W_ = "[[red|violated]] ✓"
    rows = [
        ["safe", "2", "none", "Safe", HO, "1,128,316 distinct states"],
        ["noseat1", "2", "M_NOSEAT", "FirstLeaseHasAQuorum", V, "an operator grants a first lease, as the socket does"],
        ["noseat2", "2", "M_NOSEAT", "LeaseWithinSeating", V, ""],
        ["widen1", "2", "M_WIDEN", "SuccessorNeverWidens", V, "a successor may be wider"],
        ["widen2", "2", "M_WIDEN", "LeaseWithinSeating", V, ""],
        ["peer1", "2", "M_PEER", "NoAddWithoutLiveLeaseAndPeer", V, "the peer rule dropped"],
        ["peer2", "2", "M_PEER", "ExpiredOperatorOnlyDenies", HO, "and only that"],
        ["lapsed1", "2", "M_LAPSEDADD", "ExpiredOperatorOnlyDenies", V, "a lapsed operator adds"],
        ["self1", "2", "M_SELF", "NoSelfRegrant", V, "an operator regrants itself"],
        ["noatt1", "2", "M_NOATTEST", "OperatorLeaseWasVouched", V, "no assertion read at the boundary"],
        ["stale1", "2", "M_STALEKEY", "NoDenyOnAStaleKey", V, "a deny by key alone: the first draft"],
        ["stale2", "2", "M_STALEKEY", "DenyAlwaysAvailable", HO, ""],
        ["denyl1", "2", "M_DENYLEASE", "DenyAlwaysAvailable", V, "a deny needs a lease; in the initial state"],
        ["denyl2", "2", "M_DENYLEASE", "NoDenyOnAStaleKey", HO, ""],
        ["anon1", "2", "M_ANON", "EveryStopIsAttributed", V, "a stop with no author, as the socket allows"],
        ["w1", "2", "none", "NeverWorkerRegrant", W_, "a worker's successor grant is reached"],
        ["w2", "2", "none", "NeverNarrowed", W_, "a narrowing is reached"],
        ["w3", "2", "none", "NeverLapsedDeny", W_, "a lapsed operator denies"],
        ["w4", "2", "none", "NeverStaleKey", W_, "a key with no lease and no vouching"],
        ["w5", "2", "none", "NeverPeerless", W_, "an operator with no live peer"],
        ["w6", "2", "none", "NeverRecovered", W_, "a lease live after a fence"],
        ["w7", "2", "none", "NeverOperatorRenewed", W_, "an operator renewed by a peer"],
        {"cells": ["w8", "2", "none", "NeverOperatorRegranted", HO, "**two cannot regrant a lapsed peer**"],
         "accent": "amber"},
        {"cells": ["w9", "3", "none", "NeverOperatorRegranted", W_, "**three can**"], "accent": "amber"},
        ["nsv", "2", "M_NOSEAT", "OperatorLeaseWasVouched", HO, "unreachable with two"],
        ["nsv3", "3", "M_NOSEAT", "OperatorLeaseWasVouched", V, "found writing the proof (R3)"],
        ["lf1", "2", "M_LAPSEDFENCE", "FleetFenceNeedsLease", V, "a lapsed fence: R1 to R4's rule"],
        ["lf2", "2", "M_LAPSEDFENCE", "NoDenyOnAStaleKey", HO, "and nothing else"],
        ["lf3", "2", "M_LAPSEDFENCE", "DenyAlwaysAvailable", HO, ""],
        ["st3", "2", "M_STALEKEY", "FleetFenceNeedsLease", HO, ""],
        ["w10", "2", "none", "NeverFenced", W_, "a fleet fence is reached"],
        ["w11", "2", "none", "NeverLapsedRevoke", W_, "a lapsed operator revokes"],
    ]
    to = c.table(X0, y + 30, cols, rows, size=13, accent="brown")
    left_bot = y + 30 + to
    # right: the invariants, the proof, the trace model, the tests
    ry = y
    c.text(X0 + lw + 40, ry + 16, "**Thirteen invariants**, each proved for every set of operators and every round "
           "bound", 14.5, "ink")
    cols = [("Invariant", rw * 0.36, {"mono": True}), ("States", rw * 0.64)]
    ti = c.table(X0 + lw + 40, ry + 30, cols, [
        ["FirstLeaseHasAQuorum", "every live lease descends from a seating"],
        ["LeaseWithinSeating", "no lease is wider than the quorum's grant"],
        ["SuccessorNeverWidens", "every successor grant is its predecessor's width or narrower"],
        ["NoAddWithoutLiveLeaseAndPeer", "every add was made under a live lease with another operator's lease live"],
        ["ExpiredOperatorOnlyDenies", "the first half of that, by itself"],
        ["NoSelfRegrant", "no operator regranted or renewed itself"],
        ["OperatorLeaseWasVouched", "a live operator lease was attested at its last boundary by a provider that "
                                    "vouched (**ghost truth**)"],
        ["NoDenyOnAStaleKey", "no deny was admitted from an operator with no live lease whose provider did not vouch "
                              "(**ghost truth**)"],
        ["NoDenyByRevoked", "no deny was admitted from a revoked Persona"],
        ["EveryStopIsAttributed", "every stop names an operator"],
        ["RevokedStaysOut", "a revoked principal holds no live lease"],
        ["FleetFenceNeedsLease", "no fleet fence from an operator with no live lease (R5)"],
        ["DenyAlwaysAvailable", "an operator whose Persona is in force and whose provider vouches can revoke any "
                                "principal in force, in every state"],
    ], size=13, accent="teal")
    ry2 = ry + 30 + ti + 18
    wq = (rw - 24) / 2
    cards7 = [
        ("Proved and certified", "teal", [
            "`Operators_proof.tla`: **354 obligations**, no assumption on the constants; each invariant under the "
            "mutations that break it as its only hypothesis (R3, R5).",
            "**Certified** (ADR-0046 A1): 215 by the prover's normalization, 122 by SMT with a proof `ethos` "
            "accepted, 2 by Zenon checked by Isabelle; **15 temporal steps by LS4, which no checker confirms**. The "
            "prover's translation stays trusted. A certified proof is not a verified one (G10 §8).",
            "**Outside the model**, by its header: the task and its label, more than one domain, a compromised "
            "provider, what a peer has read. An emergency seating is not modelled (R6).",
        ]),
        ("Tied to the reference by tests and a trace model", "grey", [
            "`tests/operators.rs` (6, named for the module's properties): a lease needs a sign-on assertion; a "
            "successor keeps the seating and never widens; the unsigned path seats and does nothing else; a lapsed "
            "operator stops its own domain and nothing else; a request is the operator's and is not replayed; three "
            "operators recover a lapse and two cannot. `e2e.rs`: `an_operator_is_a_principal_and_its_requests_are_decided`.",
            "`Mechanism.tla` **(A14)** models a seating, the gate on unsigned requests, and a control request with "
            "**its facts recomputed and the envelope restated**: 82 traces, 1,007 steps matching, **checked to "
            "discriminate** (the peer rule removed shows). It takes from the trace whether a signature is the seat's "
            "and whether an assertion verifies; **the floor's decision is not modelled**, so the trace compares two "
            "restatements, Rust and TLA+, neither with the Cedar text. A matching trace is not a refinement; "
            "`Operators.tla` has no refinement to the reference and no binding-table row (G10 item 90).",
        ]),
    ]
    h7 = max(c.card(0, 0, wq, t, b, size=13.5, draw=False) for t, _, b in cards7)
    for i, (t, a, b) in enumerate(cards7):
        c.card(X0 + lw + 40 + i * (wq + 24), ry2, wq, t, b, accent=a, size=13.5, h=h7, tint=(a == "teal"))
    y = max(left_bot, ry2 + h7) + 60

    # ------------------------------------------------------------------ band 8: the exit from provisional
    c.heading(X0, y, "Provisional, and the exit from it (§10; G10 item 88)", size=20)
    c.status(X1, y + 2, "open", "G10 item 88 · I47", anchor="end")
    y += 44
    w3b = (W - 2 * 30) / 3
    cards8 = [
        ("What the status carries (§10, R10)", "blue", "provisional", [
            "**A first lease from a quorum is not built.** §2 is the centre of the record and the reference does not "
            "show it: a promoted seating that grants a first lease, and the first operators seated by an anchor "
            "issuance. The unsigned socket stands in.",
            "**No reader other than the drafter has reviewed it** (ADR-0029 A2.5).",
            "It stops being provisional when both are met and the custodian records it. Until then a redesign is an "
            "amendment like any other, and nothing citing its guarantees says more than \"author-ratified, "
            "provisional\". Three of its amendments are in the bootstrap set, and the genesis attestation must name "
            "them as provisional (ADR-0029 A4).",
        ]),
        ("The exit, item by item (G10 item 88)", "red", "notbuilt", [
            "**A first lease from a completed tally, with a promoted seating.**",
            "**The first operators seated by an anchor issuance.**",
            "**A** `Regrant` **at rung 1 or above**, which has to launch a guest; the launcher's renewals are unsigned and "
            "carry only their appraisal.",
            "**An operator's Persona record and lineage**: today its Persona is its seat's key, and nothing compares "
            "providers.",
            "**A review** by a reader who is not the drafter.",
        ]),
        ("What else the reference leaves (ADR-0033 A11; I47)", "grey", None, [
            "**A lapsed operator's assertion is good for every deny** until it is seated again or the fleet is fenced.",
            "**The envelope is stated twice**, in Cedar and in Rust, and only the tests hold them together.",
            "`Launch` **and** `RegisterProfile` **are still unsigned requests.**",
            "**An issuance ends the operators' leases** with everyone's, after which a domain is regranted only once "
            "the BOOTSTRAP path seats two operators again.",
            "`AttestGates` is attributed and still an assertion (G10 item 57); `T_persona` for people waits for a "
            "measured value (R5).",
        ]),
    ]
    h8 = max(c.card(0, 0, w3b, t, b, size=13.5, status=s, draw=False) for t, _, s, b in cards8)
    for i, (t, a, s, b) in enumerate(cards8):
        c.card(X0 + i * (w3b + 30), y, w3b, t, b, accent=a, size=13.5, status=s, h=h8, tint=(i == 0))
    y += h8 + 24
    c.para(X0, y, W,
           "**What G10 does not claim** (§8): \"The operator design does not stand on evidence. Its centre, that a first "
           "lease comes from a quorum, is not built. At the reference whoever reaches the socket can seat. That is why "
           "the record is provisional.\" The module, its proof, the floor entries, the reference and the trace model are "
           "one hand's, drafted, built, checked and ratified in two days (G10 §4).", 14, "muted")
    return c
