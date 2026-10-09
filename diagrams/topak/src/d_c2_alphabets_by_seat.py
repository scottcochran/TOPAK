"""C2 — Alphabets by seat: Build's six variants, Run's three and the control alphabet's six against the five seat
kinds that may hold them."""
from lib import AMENDED_G11, Canvas

ID, SLUG = "C2", "alphabets-by-seat"

Y = "[[green|✓]]"
N = "[[red|✗]]"


def build():
    c = Canvas(ID, "Alphabets by seat: nine variants and a control alphabet of six, two domains, five seat kinds (a "
               "sixth Proposed)",
               "Each domain has its own typed alphabet and **no variant name is shared**; only the carrier, epoch and "
               "lease on every action, is common. Which seat kind may express which variant is bounded twice: by the "
               "grant path, which refuses an alphabet outside the kind's row, and by the policy floor at admit "
               "(ADR-0037 §4, ADR-0043 §2). Since Batch 34 an `operator` seat holds **no variant at all** and speaks a "
               "control alphabet of six, and an `emergency` seat speaks Run's three; both kinds are **provisional** "
               "(ADR-0037 A3, A4). The floor cited is the proposed floor's `emergency` stage, the floor in force, "
               "**genesis-provisional**, not ratified (G11 §2.2). **Proposed with ADR-0054**: a tenth variant, "
               "`Route(edge)`, and a sixth kind, `orchestrator`, which alone holds it; the reference links the "
               "`workflow` stage that states them, which is not in force (G11 item 102; C9).",
               3400, "ADR-0022 §1–§7 (A1, A2); ADR-0040 §1–§6; ADR-0041 §1–§3, A1, A2, A3; ADR-0042 §5, §6 (B30); "
                     "ADR-0043 §1, §2, §4, A1; ADR-0037 §4, §7, A3, A4; ADR-0024 §2, §5; ADR-0038 §6; ADR-0039 A2; "
                     "ADR-0031 §4, A3; ADR-0034 P4, D-0034-3, A2 (B30: the Run profile, D-0034-5, D-0034-6); ADR-0033 A7 "
                     "(B29), A8 (B31), A9 (B32), A11, A12; ADR-0047 §7 (F1–F3); ADR-0048 R6; ADR-0049 §5; ADR-0050 §1, §2, "
                     "§4–§6; ADR-0052 §1–§5; ADR-0015; ADR-0030 A3; "
                     "floor/proposed/emergency-floor.cedar (genesis-provisional, 28 policies, 15c941b9a56a09f7; "
                     "emergency-gates-results-2026.10.04.txt) and floor/proposed/README.md; floor/genesis-floor.cedar "
                     "(DRAFT, 17 policies, unchanged); "
                     "spec/Seats-results-2026.09.29.txt; spec/RunSeats-results-2026.09.29.txt; spec/Seats_proof.tla, "
                     "spec/RunSeats_proof.tla, their 2026.10.02 proof results and 2026.10.04 certified results; "
                     "ADR-0037 B25; ADR-0043 B25; ADR-0046 §4, §5, A1; mechanism topak-core types.rs (`SeatKind`), "
                     "control.rs (`ControlAction`, `ControlFacts`); mechanism/GAPS-AND-ASSUMPTIONS.md I14, I33, I43, "
                     "I44, G19; ToO rev 15 §2.4, §2.9, §2.10, §2.11, §3.3, §4.1, §7.10; G10 §2.3, §2.5, §3, §7 items 57, "
                     "80, 83, 84, 91, 95; G11 §2.2, §2.5, item 102; ADR-0054 §3 (Proposed); ADR-0040 A2, ADR-0037 A5, "
                     "ADR-0041 A4, ADR-0015 A1 (pending); floor/proposed/workflow-floor.cedar")
    c.note = AMENDED_G11
    X0, X1 = c.x0, c.x1
    y = c.y

    # ------------------------------------------------------------------ the two alphabets over one carrier
    mid = 320
    pw = (X1 - X0 - mid) / 2
    bx, rx = X0, X1 - pw
    top = y + 14
    pad = 26
    # Build panel
    cw = (pw - 2 * pad - 2 * 18) / 3
    bvars = [
        ("`Read(ref)`", "grey", "Resolve a content-addressed object in the pinned **corpus root**"),
        ("`Draft(target, content)`", "grey", "Write a candidate into the round-scoped **workspace**"),
        ("`Invoke(tool, inputs)`", "red", "Run a tool allowlisted by name **and** digest; inputs workspace-resident. "
                                          "**The whole attack surface**"),
        ("`Emit(record)`", "teal", "Append to the principal's own round topic, current epoch (ADR-0021)"),
        ("`Submit(digest | ⊥)`", "blue", "Offer the sealed workspace for promotion, or abstain. **Terminal** for the "
                                         "authoring round"),
        ("`Vote(verdict, digest, evidence, rulesEpoch)`", "blue",
         "Cast a promotion vote. **Terminal** for the voter's promotion round; author recused"),
    ]
    rvars = [
        ("`Consult(ref)`", "grey", "**Ingress, no effect**: `ref` resolves in the pinned **Run root**"),
        ("`Actuate(tool, inputs)`", "red", "**Effect: tool invocation**. Allowlisted by name and digest; the entry "
                                          "**declares the channel it opens**. A read of live state is an `Actuate`"),
        ("`Report(record)`", "teal", "**Effect: principal emission**. Own round topic, this epoch and round, unsealed"),
    ]
    vh = max(c.card(0, 0, cw, t, [b], size=13.5, tsize=14.5, bullets=False, draw=False) for t, _, b in bvars + rvars)
    cy = top + 66
    for i, (t, a, b) in enumerate(bvars):
        r, k = divmod(i, 3)
        c.card(bx + pad + k * (cw + 18), cy + r * (vh + 16), cw, t, [b], accent=a, size=13.5, tsize=14.5,
               bullets=False, h=vh, tint=(a != "grey"))
    rcw = (pw - 2 * pad - 2 * 18) / 3
    for k, (t, a, b) in enumerate(rvars):
        c.card(rx + pad + k * (rcw + 18), cy, rcw, t, [b], accent=a, size=13.5, tsize=14.5, bullets=False, h=vh,
               tint=(a != "grey"))
    # Run: no terminal variant
    c.card(rx + pad, cy + vh + 16, pw - 2 * pad, "No terminal variant", [
        "Run offers nothing to a gate: **a Run round ends when its lease ends**, and a Run seat cannot abstain "
        "(ADR-0040 §4; ADR-0042 §5). A principal that has finished holds its lease until it lapses. An `emergency` "
        "seat speaks these three and nothing else (ADR-0052 §1).",
    ], accent="green", size=13.5, tsize=14.5, bullets=False, h=vh, tint=False, dash="6 4")
    pbot = cy + 2 * vh + 16 + 24
    c.text(bx + pad, top + 42, "Egress only: the alphabet types what a principal does, not what it receives "
           "(ADR-0022 §1)", 14, "muted")
    c.text(rx + pad, top + 42, "Three variants, nothing shared but the carrier (ADR-0040 §1, §2)", 14, "muted")
    c.region(bx, top, pw, pbot - top, "Build alphabet · ADR-0022 §1 · six variants", "blue", dash=None, sw=2.4,
             size=16)
    c.region(rx, top, pw, pbot - top, "Run alphabet · ADR-0040 §1 · three variants", "green", dash=None, sw=2.4,
             size=16)
    c.status(bx + pw - 16, top + 14, "accepted", "§1–§5, §7, §8; §6 Proposed", anchor="end")
    c.status(rx + pw - 16, top + 14, "accepted", "C3, C4", anchor="end")
    # middle: no name shared
    mx = bx + pw + 20
    c.card(mx, top + 40, mid - 40, "No name is shared", [
        "`Read` and `Emit` are Build's; Run has `Consult` and `Report` (ADR-0022 A2, C3).",
        "A name in both alphabets would have to carry the same obligations in both: `Invoke` is hermetic, `Actuate` "
        "exists to have an effect.",
        "So a floor entry, a lease's `alphabet` and a log line each name their domain by the verb.",
    ], accent="red", size=13.5, tint=False, dash="6 4")

    # carrier bar
    cy2 = pbot + 40
    ch = c.card(X0, cy2, X1 - X0, "The carrier is shared: every action carries epoch and lease (ADR-0022 §2; "
                "ADR-0040 §2)", [
        "Actions under a fenced epoch are rejected **by the mechanism, not by policy**, ahead of the floor; the floor "
        "states no epoch fence (its header). The lease (ADR-0031) carries the seat, its `alphabet` and its domain; at "
        "the reference the bearer token carries (seat, lease, epoch) into every action, and a lease the launcher "
        "issues mints none: at rung 1 the bridge is the session (`mechanism/` I14; ADR-0033 A7, B29). Under an "
        "`emergency` lease every action carries a proof signed with the person's key, and there is no bearer token "
        "(A12). An operator's request carries the fleet epoch in its signed body (A11).",
    ], accent="teal", size=14.5, bullets=False)
    for xx in (bx + pw / 2, rx + pw / 2):
        c.arrow([(xx, cy2), (xx, pbot)], "teal", sw=2.4)
    # ------------------------------------------------------------------ the control alphabet
    ctop = cy2 + ch + 56
    cpad = 26
    ccw = (X1 - X0 - 2 * cpad - 5 * 18) / 6
    cvars = [
        ("`Regrant(target, round, alphabet, ttl, task, taskLabel)`", "blue",
         "**Add.** A successor grant: the target's next round, every field the last lease's or narrower, with the "
         "round's task by digest and the operator's signed label (§2, §5)"),
        ("`Renew(target, alphabet, ttl)`", "blue",
         "**Add.** A renewal of a live lease in the domain; keeps the round and only narrows (ADR-0031 §4)"),
        ("`AttestGates(artifact, evidence)`", "blue",
         "**Add**, Build only. Records that the gates ran, with the evidence's digest: attributed, and still an "
         "assertion (G10 item 57)"),
        ("`EndRound(target)`", "red", "**Deny.** Ends one principal's round, in the operator's own domain"),
        ("`Revoke(target, reason)`", "red",
         "**Deny.** A targeted revocation (ADR-0031 §5), in the operator's own domain"),
        ("`FenceEpoch(reason)`", "red",
         "**Deny.** The fleet fence; the one deny that needs a live lease (R5)"),
    ]
    chh = max(c.card(0, 0, ccw, t, [b], size=13.5, tsize=14.5, bullets=False, draw=False) for t, _, b in cvars)
    ccy = ctop + 66
    for k, (t, a, b) in enumerate(cvars):
        c.card(X0 + cpad + k * (ccw + 18), ccy, ccw, t, [b], accent=a, size=13.5, tsize=14.5, bullets=False,
               h=chh, tint=(a == "blue"), dash=(None if a == "blue" else "6 4"))
    cnote_y = ccy + chh + 16
    cnh = c.para(X0 + cpad, cnote_y, X1 - X0 - 2 * cpad,
                 "**Not action variants.** An `operator` seat is issued none (ADR-0037 A4; `SeatKind::Operator` admits "
                 "none at the reference). Each request is signed with the seat's key, carries the fleet epoch and a "
                 "counter, and is decided by the floor's `C1` to `C9` over thirteen facts the mechanism computes; "
                 "every replica recomputes them and restates the envelope at apply (ADR-0033 A11). **First leases are "
                 "not here**: the mechanism grants one when a quorum completes (ADR-0050 §2), which is **not built**; "
                 "at the reference the unsigned socket stands in as a **BOOTSTRAP** path. `Issue` and "
                 "`BreakGlassApprove` are not operator variants.", 14, "ink")
    cbot = cnote_y + cnh + 22
    c.text(X0 + cpad, ctop + 42, "Three adds, which need a live lease and a live peer; three denies, which need no "
           "lease but a Persona in force and a fresh credential (ADR-0050 §4, §6)", 14, "muted")
    c.region(X0, ctop, X1 - X0, cbot - ctop, "Control alphabet · ADR-0050 §4 · six actions · `operator` seats, either "
             "domain", "brown", dash=None, sw=2.4, size=16)
    c.status(X1 - 16, ctop + 14, "provisional", "C1, C3, C4", anchor="end")

    y = cbot + 50

    # ------------------------------------------------------------------ mechanism parameters and the two channel rules
    w4 = (X1 - X0 - 3 * 24) / 4
    pcards = [
        ("Build: three mechanism parameters (ADR-0022 §3)", "blue", None, "", [
            "**Corpus root**: a pinned, content-addressed set; `Read` is scoped to it. Whether it is poisoned is an "
            "Observer finding, not an enforcement decision.",
            "**Tool allowlist**: name plus digest; each entry carries a **hermeticity** obligation: no network, no "
            "filesystem outside the workspace, deterministic given its inputs. A Build entry has no channel and no "
            "labels, and one that declares a channel does not load (ADR-0049).",
            "**Round bound**: maximum actions per round; termination, and it bounds the state space.",
        ]),
        ("Run: three mechanism parameters (ADR-0040 §3)", "green", None, "", [
            "**Run root**: a second pinned, content-addressed set; `Consult` is scoped to it, and declares a label "
            "(ADR-0040 A1).",
            "**Tool allowlist**: name plus digest, in ADR-0049's one form: identity, inputs, interface, labels and "
            "**channel**. A Run tool is not hermetic and is not asked to be; the channel's target is declared once, "
            "in the entry (ADR-0049 §5; ADR-0033 A9).",
            "**Round bound** `R`: admits per round over all three variants; per domain; a placeholder number.",
        ]),
        ("`Invoke` hermeticity: Wasm discharged, native unowned", "red", None, "", [
            "One allowlisted tool with a socket collapses the envelope to vacuity (ADR-0022 Negative).",
            "**Wasm components: discharged by construction**, ADR-0034 **P4**: instantiated per call, a workspace "
            "directory capability only; no sockets, no wall clock, no free entropy.",
            "**Native tools: unowned.** Using one is declared degeneracy **D-0034-3**: P4 falsified, the principals "
            "reaching it are `Mediated`.",
            "At the reference a Build profile that says P4 passes is **not yet held to Wasm tools** for `Invoke` "
            "(G10 item 83, as at G9).",
        ]),
        ("`Actuate` declares its channel: channel fidelity", "teal", "accepted", "ADR-0042 §6 B30 · C2", [
            "P4 cannot hold for a Run tool; **channel fidelity** replaces it: a tool opens the channel its entry "
            "declares and no other (ADR-0042 §6, **in force since Batch 30**).",
            "**Owner**: ADR-0034 **A2**, the Run profile (B30): the tool host's **Wasm runtime** hands a Run tool one "
            "network capability, its declared target. ADR-0033 **A8** (B31) builds it; **A9** (B32) reads the target "
            "from the entry in the revision the lease names, and from nowhere else (G10 item 84, closed).",
            "**Native Run tools**: **D-0034-6**, or **D-0034-5** behind an egress filter, a trust (G19).",
            "Run principals are still `Mediated` in fact: `Contained` has four conjuncts and the lineage criterion is "
            "not in force (ToO §2.9; G10 §2.3).",
        ]),
    ]
    ph = max(c.card(0, 0, w4, t, b, size=14, status=s, status_extra=se, draw=False) for t, _, s, se, b in pcards)
    for i, (t, a, s, se, b) in enumerate(pcards):
        c.card(X0 + i * (w4 + 24), y, w4, t, b, accent=a, size=14, status=s, status_extra=se, h=ph, tint=(i != 2))
    y += ph + 60

    # ------------------------------------------------------------------ the full matrix
    c.heading(X0, y, "The matrix: every variant and control action against every seat kind (ADR-0037 §4, A3, A4; "
                     "ADR-0043 §2; ADR-0050 §4)", size=21)
    pw_ = c.status(X1, y + 3, "provisional", "A3, A4", anchor="end")
    c.status(X1 - pw_ - 10, y + 3, "accepted", "ADR-0037 C3, C4 · ADR-0043 C4", anchor="end")
    y += 44
    TW = X1 - X0
    cols = [("Variant", TW * 0.115), ("Class (ADR-0015 effects; ADR-0040 §1; ADR-0050 §4)", TW * 0.085),
            ("Envelope constraint (record)", TW * 0.12), ("Floor entries (genesis-provisional)", TW * 0.125),
            ("`thinker` seat", TW * 0.1), ("`observer` seat", TW * 0.1), ("`grant` seat (human)", TW * 0.08),
            ("`operator` seat (human, provisional)", TW * 0.095), ("`emergency` seat (human, Run, provisional)",
                                                                   TW * 0.115),
            ("Veto roster (`observer` seats only)", TW * 0.065)]
    NV = N + " issued no action variant (A4)"
    NB = N + " no Build alphabet (A3)"
    rows = [
        {"group": "Build · ADR-0022 §1 · domain `build` · every Build permit requires `principal.domain == \"build\"` "
                  "and the variant in `context.lease.alphabet`", "accent": "blue"},
        ["`Read(ref)`", "No effect: a resolve inside the pinned set", "`ref` inside the pinned corpus root",
         "permit **B1-read-corpus**", Y, Y, Y, NV, NB, "—"],
        ["`Draft(target, content)`", "No effect (ADR-0040 §1)", "`target` inside the round-scoped workspace",
         "permit **B2**; forbid **B9** (voter role), **B10** (kind ≠ thinker)", Y + " author role only (B9)",
         N + " B10", N + " B10", N + " B10", N + " B10", "—"],
        ["`Invoke(tool, inputs)`", "**Effect**: tool invocation", "`tool` allowlisted by name and digest; `inputs` "
                                                                   "workspace-resident",
         "permit **B3-invoke-allowlisted**; forbid **B9**, **B10**", Y + " author role only (B9)", N + " B10",
         N + " B10", N + " B10", N + " B10", "—"],
        ["`Emit(record)`", "**Effect**: principal emission", "Own round topic, current epoch and round, unsealed",
         "permit **B4-emit-own-topic**", Y, Y + " heartbeats and findings", Y, NV
         + "; the mechanism writes its requests to its topic (ADR-0050 §6)", NB, "—"],
        ["`Submit(digest | ⊥)`", "**Terminal** for the authoring round; offers for promotion (an authority change, "
                                 "ADR-0024)", "Own artifact (`resource.author == principal`)",
         "permit **B5-submit-own-artifact**; forbid **B9**, **B10**", Y + " author role only (B9)", N + " B10",
         N + " B10", N + " B10", N + " B10", "—"],
        ["`Vote(verdict, digest, evidence, rulesEpoch)`", "**Vote**; terminal for the voter's promotion round",
         "Seat held at `rulesEpoch`; `grant` only from a grant seat; never the author (a mechanism constant)",
         "permit **B6-vote-seated** (tightened); forbid **B7-author-recused**, **B8-grant-only-from-grant-seat**",
         N + " never votes: B6 admits only a `grant` seat on the grant roster or an `observer` seat on the veto roster",
         "Only `Vote(deny)`, and only on the veto roster (B6, B8)", Y + " `grant` or `deny`, on the grant roster; "
                                                                        "recused if author (B7)",
         N + " B6 names neither roster for it; a person who operates and votes is two principals (ADR-0037 §7)", NB,
         "`Vote(deny)` only (ADR-0024 §5; ADR-0038 §6)"],
        {"group": "Run · ADR-0040 §1 · domain `run` · every Run permit requires `principal.domain == \"run\"`; "
                  "`grant` seats are Build seats (only Build seats vote)", "accent": "green"},
        ["`Consult(ref)`", "**Ingress**, no effect", "`ref` inside the pinned Run root",
         "permit **R4-consult-pinned**; **not** coupled (R3 names `Actuate`, `Report` only)", Y,
         Y + " reads the pinned objects its Thinker consulted (drafter's choice, kept)", N + " no Run row", NV,
         Y + " (ADR-0052 §1)", "—"],
        ["`Actuate(tool, inputs)`", "**Effect**: tool invocation",
         "Allowlisted by name and digest; entry declares its channel",
         "permit **R1-actuate-allowlisted**; forbid **B10** (except an `emergency` seat), **R3-observer-live** "
         "(`thinker` only), **R5** to **R7** (an outward entry, by labels)",
         Y + " only while its cell Observer is live (R3); R5 to R7", N + " B10", N + " B10 · no Run row", N + " B10",
         Y + " for one round, inside the envelope computed at activation, admitted by R1; **not coupled** (R3 is a "
             "`thinker`'s); R5 to R7 apply (ADR-0052 §2, §4)", "—"],
        ["`Report(record)`", "**Effect**: principal emission", "Own round topic, this epoch and round, unsealed",
         "permit **R2-report-own-topic**; **R3-observer-live** for `thinker` seats", Y + " only while its cell "
                                                                                       "Observer is live (R3)",
         Y + " heartbeats and findings; **not coupled**", N + " no Run row", NV,
         Y + " not coupled; a rationale is content and no admit turns on it (ADR-0052 §5)", "—"],
        {"cells": ["`Route(edge)` · [[amber|Proposed]]", "**Emission** (ADR-0015 A1, pending); the grant it leads to is "
                   "the workflow's promotion's", "A chosen edge out of the decision point the lease was granted for, "
                   "its guard already true; checked again at apply (ADR-0054 §3, §8)",
                   "In the `workflow` stage only, **not in force**: permit **R8-route-own-decision**; forbid "
                   "**R9-only-orchestrators-route**; **R3** covers it (ADR-0041 A4, pending)", N + " R9", N + " R9",
                   N + " no Run row", NV, N + " R9", "—"], "accent": "amber"},
        {"group": "Control · ADR-0050 §4 · either domain · signed requests, not action variants; every permit, `C1` to "
                  "`C4`, requires `principal.kind == \"operator\"` (ADR-0041 A3)", "accent": "brown"},
        ["`Regrant`", "**Add**: a successor grant (ADR-0031 A3)",
         "Target in the operator's domain, seated by a quorum, not revoked, not live; same binding; next round; "
         "alphabet within the last lease's; task label within the seating's",
         "permit **C1-regrant-successor**; forbid **C5**, **C6**, **C8**", N + " C1 to C4 name the `operator` kind",
         N, N, Y + " with a live lease and a live peer; never itself; never an `emergency` seat (ADR-0052 §3)", N,
         "—"],
        ["`Renew`", "**Add**: a renewal (ADR-0031 §4)", "Target holds a live lease in the operator's domain",
         "permit **C2-renew**; forbid **C5**, **C6**", N, N, N, Y + " live lease and live peer; never itself", N,
         "—"],
        ["`AttestGates`", "**Add**: unlocks votes", "An artifact and the evidence's digest; Build only",
         "permit **C3-attest-gates**; forbid **C5**", N, N, N, Y + " a Build seat, live lease and live peer", N, "—"],
        ["`EndRound`", "**Deny**", "Target in the operator's domain",
         "permit **C4-deny**; forbid **C9-stop-in-own-domain**", N, N, N,
         Y + " Persona in force, and a live lease **or** a fresh sign-on assertion (R1)", N, "—"],
        ["`Revoke`", "**Deny**: a targeted revocation (ADR-0031 §5)", "Target in the operator's domain",
         "permit **C4-deny**; forbid **C9-stop-in-own-domain**", N, N, N,
         Y + " Persona in force, and a live lease **or** a fresh sign-on assertion (R1)", N, "—"],
        ["`FenceEpoch`", "**Deny**: the fleet fence", "Fleet-wide; `C4` reads no property of its target",
         "permit **C4-deny**; forbid **C7-fence-needs-lease**", N, N, N,
         Y + " Persona in force **and** a live lease (R5)", N, "—"],
    ]
    y += c.table(X0, y, cols, rows, size=14) + 24
    y += c.para(X0, y, X1 - X0,
                "**Only a** `thinker` **seat, or in Run an** `emergency` **seat for** `Actuate`, **holds a variant that "
                "writes, runs or offers** (`Draft`, `Invoke`, `Submit`, `Actuate`), and B10 names both; a `thinker` "
                "seat never votes (ADR-0037 §4, A3). **An** `operator` **seat holds no action variant**, and nothing else "
                "holds the control alphabet (A4). A Reader with `Draft` authority, the failure ADR-0022's follow-up "
                "named, cannot arise: the Reader is not a principal. A narrower lease is always allowed (ADR-0031 §4), "
                "so an `observer` seat without `Consult` needs no declaration (ADR-0043 §7); **a lease cannot be "
                "narrowed to a tool**, since its schema carries no tool set (ADR-0048 R6; G10 item 95). **Pending with "
                "ADR-0054** (ADR-0037 A5): a sixth kind, `orchestrator`, Run only, issued `Route` and `Report` and "
                "nothing else; coupled to an Observer as a Thinker is (ADR-0039 A3); delivered handles and never bytes; "
                "seated only when a workflow has a chosen edge. Not in the matrix's columns because it is not in force.",
                14.5) + 46

    # ------------------------------------------------------------------ the floor, verbatim policy by policy
    c.heading(X0, y, "floor/proposed/emergency-floor.cedar: all 28 policies, the floor in force", size=21)
    c.status(X1, y + 3, "genprov", "G11 §2.2 · 107 cases, every gate passing 2026.10.04", anchor="end")
    y += 44
    cols = [("Policy id", TW * 0.14, {"mono": True}), ("Effect", TW * 0.05, {"bold": True}),
            ("Action", TW * 0.13), ("Condition (paraphrased from the Cedar text)", TW * 0.43),
            ("Record it states", TW * 0.25)]
    P, F = "[[green|permit]]", "[[red|forbid]]"
    rows = [
        {"group": "Build envelopes (ADR-0022 §1)", "accent": "blue"},
        ["B1-read-corpus", P, "`Read`", "domain build; `Read` in the lease alphabet; resource in `context.corpusRoot`",
         "ADR-0022 §1"],
        ["B2-draft-workspace", P, "`Draft`", "domain build; `Draft` in alphabet; resource in `context.workspace`",
         "ADR-0022 §1"],
        ["B3-invoke-allowlisted", P, "`Invoke`", "domain build; `Invoke` in alphabet; resource in "
                                                 "`context.toolAllowlist`; `context.inputsInWorkspace`",
         "ADR-0022 §1; hermeticity is **not** in the floor (an obligation per entry)"],
        ["B4-emit-own-topic", P, "`Emit`", "domain build; `Emit` in alphabet; topic owner is the principal; topic "
                                           "epoch and round are the context's; topic not sealed", "ADR-0022 §1"],
        ["B5-submit-own-artifact", P, "`Submit`", "domain build; `Submit` in alphabet; `resource.author == principal`",
         "ADR-0022 §1"],
        ["B6-vote-seated", P, "`Vote`", "domain build; `Vote` in alphabet; vote rules epoch is current; (on grant "
                                        "roster ∧ kind `grant`) ∨ (on veto roster ∧ kind `observer`)",
         "ADR-0022 §1, tightened by ADR-0037 §4"],
        {"group": "Carve-outs on the Build envelopes", "accent": "red"},
        ["B7-author-recused", F, "`Vote`", "`resource.author == principal`",
         "ADR-0022 §7, ADR-0024 §6; relaxing it is a floor relaxation (ADR-0022 A1)"],
        ["B8-grant-only-from-grant-seat", F, "`Vote`", "verdict `grant` and principal not on the grant roster",
         "ADR-0024 §5: a veto seat's alphabet lacks grant"],
        ["B9-voters-do-not-author", F, "`Draft`, `Invoke`, `Submit`", "`context.roundRole == \"voter\"`",
         "ADR-0022 §7"],
        ["B10-only-thinkers-author", F, "`Draft`, `Invoke`, `Submit`, `Actuate`",
         "`principal.kind != \"thinker\"`, **except** `principal.kind == \"emergency\"` with action `Actuate`",
         "ADR-0037 §4; ADR-0043 §2 adds `Actuate`; the exception is ADR-0041 A2 (ADR-0052 §1, provisional)"],
        {"group": "Run envelopes (ADR-0040 §1, stated as ADR-0041 §1)", "accent": "green"},
        ["R1-actuate-allowlisted", P, "`Actuate`", "domain run; `Actuate` in alphabet; resource in "
                                                   "`context.toolAllowlist`. Also admits an `emergency` seat's calls "
                                                   "over the envelope computed at activation",
         "ADR-0040 §1, ADR-0041 §1; ADR-0052 §2"],
        ["R2-report-own-topic", P, "`Report`", "domain run; `Report` in alphabet; own topic, current epoch and round, "
                                               "unsealed", "ADR-0040 §1, ADR-0041 §1"],
        ["R4-consult-pinned", P, "`Consult`", "domain run; `Consult` in alphabet; resource in `context.runRoot`",
         "ADR-0040 §1; ADR-0041 §1"],
        ["R3-observer-live", F, "`Actuate`, `Report`", "kind `thinker` and not `context.observerLive` (live Observer "
                                                       "lease, heartbeat within `T_obs`, watermark within `K`)",
         "ADR-0039 §2 as ADR-0041 §2 reads it; `Consult` exempt; an `emergency` seat not reached (ADR-0039 A2)"],
        {"group": "Carve-outs on Run's effects by label (ADR-0047 §7, F1 to F3, named by ADR-0041 A1)",
         "accent": "red"},
        ["R5-no-read-then-send", F, "`Actuate`", "`resource.outward`; `clearSet` holds `untrusted`; `restricted` in "
                                                 "`clearSet` or in `inputLabels`", "ADR-0047 F1"],
        ["R6-no-steered-destination", F, "`Actuate`", "`resource.outward`; `clearSet` holds `untrusted`; "
                                                      "`context.destLiteral`", "ADR-0047 F2"],
        ["R7-no-replayed-destination", F, "`Actuate`", "`resource.outward`; `destLabels` holds `untrusted`",
         "ADR-0047 F3"],
        {"group": "Floor exceptions (ADR-0013 §2; count 1, bounded by ADR-0026 R6) and the forensic floor",
         "accent": "amber"},
        {"cells": ["X1-break-glass", "—", "—", "**Retired**, not one of the 28: break-glass is an emergency seating, "
                                               "and its calls are admitted by R1 (ADR-0052 §2)",
                   "ADR-0041 A2; ADR-0013 A1; ADR-0009 A1 (provisional, with ADR-0052)"], "accent": "grey"},
        ["X2-erasure", P, "`Erase`", "`context.erasureQuorum`: false from epoch 0, since genesis issues no erasure "
                                     "roster", "ADR-0006; ADR-0029 §5"],
        ["F-forensic-classes", F, "`Erase`", "resource class in F1–F6", "ADR-0028"],
        {"group": "Control entries (ADR-0050 §4, named by ADR-0041 A3): an `operator` seat's requests; a first lease "
                  "has no entry", "accent": "brown"},
        ["C1-regrant-successor", P, "`Regrant`", "kind `operator`; target in its domain; `targetSeated`; not "
                                                 "`targetLive`; `sameBinding`; `nextRound`; `lastAlphabet` contains "
                                                 "all of `newAlphabet`", "ADR-0050 §2, §4"],
        ["C2-renew", P, "`Renew`", "kind `operator`; target in its domain; `targetLive`", "ADR-0050 §4; ADR-0031 §4"],
        ["C3-attest-gates", P, "`AttestGates`", "kind `operator`; `principal.domain == \"build\"`", "ADR-0050 §4"],
        ["C4-deny", P, "`EndRound`, `Revoke`, `FenceEpoch`", "kind `operator`; `personaInForce`; `hasLease` or "
                                                              "`freshAssertion`", "ADR-0050 §4 (R1)"],
        ["C5-add-needs-lease-and-peer", F, "`Regrant`, `Renew`, `AttestGates`", "not `hasLease`, or not `peerLive`",
         "ADR-0050 §4, §6"],
        ["C6-no-self", F, "`Regrant`, `Renew`", "`resource == principal`", "ADR-0050 §4"],
        ["C7-fence-needs-lease", F, "`FenceEpoch`", "not `hasLease`", "ADR-0050 §4 (R5)"],
        ["C8-task-label-in-bounds", F, "`Regrant`", "not `taskLabelled`, or `taskLabelsAllowed` does not contain all "
                                                    "of `taskLabel`", "ADR-0050 §5; ADR-0047 §1"],
        ["C9-stop-in-own-domain", F, "`EndRound`, `Revoke`", "`resource.domain != principal.domain`",
         "ADR-0050 §4 (R5, R9: confirmed by the custodian)"],
    ]
    y += c.table(X0, y, cols, rows, size=14) + 24
    y += c.para(X0, y, X1 - X0,
                "Evaluation: any satisfied forbid denies; else any satisfied permit allows; else deny. **Any evaluation "
                "error is a deny** (ADR-0030 §1). Not in the floor, by design: epoch fencing (the mechanism, ahead of "
                "the floor), the round bound (a count), the rules floor (bounds issuances), `Invoke` hermeticity (a "
                "property of the allowlist entry), and first leases (granted by the mechanism on a quorum). The text "
                "is built in three gated stages from `floor/genesis-floor.cedar` (17 policies, a draft, unchanged): "
                "`labels` (20), `control` (29), `emergency` (28). It is **gated, pinned and enforced, and not "
                "ratified**: the bootstrap reviewer ratifies it on finding it fit, and no test of fitness is written "
                "(ADR-0030 A3; G10 items 2, 87). Comments carried from the genesis text still call the floor DRAFT and "
                "ADR-0040 and ADR-0041 \"Proposed\", and the stage's opening comment, \"not what the reference "
                "follows\", is wrong; the bytes are kept as gated (G10 item 91).", 14, "muted") + 50

    # ------------------------------------------------------------------ checks
    half = (X1 - X0 - 40) / 2
    c.heading(X0, y, "`spec/Seats.tla` (ADR-0037 §9), TLC 2026.09.29; proved 2026.10.02; certified 2026.10.04")
    c.heading(X0 + half + 40, y, "`spec/RunSeats.tla` (ADR-0043 §8), TLC 2026.09.29; proved 2026.10.02; certified "
                                 "2026.10.04")
    y += 40
    cols = [("Mutation", half * 0.2, {"mono": True}), ("Invariant", half * 0.38, {"mono": True}),
            ("Result", half * 0.2, {"bold": True}), ("Distinct states", half * 0.22)]
    H, CE = "[[green|HOLDS]]", "[[red|COUNTEREXAMPLE]]"
    t1 = c.table(X0, y, cols, [
        ["none", "OnlyThinkersAuthor", H, "6,656"],
        ["none", "OneSeatPerPrincipal", H, "6,656"],
        ["M_KIND", "OnlyThinkersAuthor", CE, "37"],
        ["M_KIND", "OneSeatPerPrincipal", H, "53,248"],
        ["M_SEAT", "OneSeatPerPrincipal", CE, "49"],
        ["M_SEAT", "OnlyThinkersAuthor", H, "13,824"],
        ["none", "NeverActed (witness)", CE + " ✓", "25"],
        ["none", "NeverTwoLive (witness)", CE + " ✓", "45"],
        ["none", "NeverObserverVoted (witness)", CE + " ✓", "118"],
    ], size=13.5, accent="blue")
    t2 = c.table(X0 + half + 40, y, cols, [
        ["none", "OnlyThinkersActuate", H, "16,384"],
        ["none", "ObserversConsultAndReport", H, "16,384"],
        ["none", "NoNameCrossesDomains", H, "16,384"],
        ["M_KIND", "OnlyThinkersActuate", CE, "123"],
        ["M_KIND", "ObserversConsultAndReport", CE, "110"],
        ["M_KIND", "NoNameCrossesDomains", H, "65,536"],
        ["M_DOMAIN", "NoNameCrossesDomains", CE, "42"],
        ["M_DOMAIN", "OnlyThinkersActuate", H, "373"],
        ["M_DOMAIN", "ObserversConsultAndReport", CE, "154"],
        ["M_OBSEMIT", "Safe", H, "8,192"],
        ["M_OBSEMIT", "NeverObserverConsulted", H, "8,192"],
        ["none", "NeverActuated (witness)", CE + " ✓", "70"],
        ["none", "NeverObserverReported (witness)", CE + " ✓", "117"],
        ["none", "NeverObserverConsulted (witness)", CE + " ✓", "104"],
    ], size=13.5, accent="green")
    ph2 = c.para(X0, y + t1 + 18, half,
           "Constants: 2 principals, 3 seats (one per kind), 4 actions. Each mutation breaks exactly its property: "
           "`M_KIND` (the grant path ignores the kind bound) and `M_SEAT` (one-live-lease keyed by seat, the "
           "reference's behaviour before R5).", 14, "muted")
    ph3 = c.para(X0, y + t1 + 18 + ph2 + 12, half,
           "**Proved** (ADR-0037 B25; ADR-0046 §4): `Seats_proof.tla`, 110 obligations, `OnlyThinkersAuthor` not under "
           "`M_KIND` and `OneSeatPerPrincipal` not under `M_SEAT`; `RunSeats_proof.tla`, 147 obligations, "
           "`OnlyThinkersActuate` not under `M_KIND`, `ObserversConsultAndReport` not under `M_KIND`, `M_DOMAIN`, "
           "`NoNameCrossesDomains` not under `M_DOMAIN`. Of the modules, for every behaviour; the rows here stay "
           "with TLC. **Certified** (ADR-0046 A1): of 110, 107 by normalization or a checked proof and 3 LS4 steps; of "
           "147, 143 and 4. LS4's answers no checker confirms.", 14, "teal")
    ph4 = c.para(X0, y + t1 + 18 + ph2 + 12 + ph3 + 12, half,
           "**Neither module has the two new kinds.** They model three seats, one per kind of 2026.09.29. "
           "`operator` and `emergency` are checked by `Operators.tla` (32 rows, thirteen invariants, 354 "
           "obligations) and `Emergency.tla` (51 rows, six properties, 373 obligations), each proved and certified "
           "(G10 §3); the binding table has no rows for either (G10 item 90).", 14, "ink")
    c.para(X0 + half + 40, y + t2 + 18, half,
           "**The binding table now agrees with these rows** (ADR-0046 §5, correction 1): `M_OBSEMIT` breaks none of "
           "the three invariants, since it narrows an observer's bound and they are upper bounds, and `M_DOMAIN` breaks "
           "`ObserversConsultAndReport` as well as `NoNameCrossesDomains`. The table had listed `M_OBSEMIT` and missed "
           "`M_DOMAIN`.", 14, "teal")
    c.para(X0, y + t1 + 18 + ph2 + 12 + ph3 + 12 + ph4 + 12, half,
           "`M_OBSEMIT` is ADR-0037 §4's struck provisional Run column (an `observer` seat with emission only): every "
           "property holds and no Observer ever consults. The results file's header still reads \"ADR-0043 §8, "
           "Proposed\"; ADR-0043 was ratified in Batch 20.", 14, "muted")
    return c
