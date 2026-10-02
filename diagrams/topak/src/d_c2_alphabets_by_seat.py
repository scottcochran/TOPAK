"""C2 — Alphabets by seat: Build's six variants and Run's three against the seat kinds that may hold them."""
from lib import Canvas

ID, SLUG = "C2", "alphabets-by-seat"

Y = "[[green|✓]]"
N = "[[red|✗]]"


def build():
    c = Canvas(ID, "Alphabets by seat: nine variants, two domains, three seat kinds",
               "Each domain has its own typed alphabet and **no variant name is shared**; only the carrier, epoch and "
               "lease on every action, is common. Which seat kind may express which variant is bounded twice: by the "
               "grant path, which refuses an alphabet outside the kind's row, and by the policy floor at admit "
               "(ADR-0037 §4, ADR-0043 §2). The floor text cited here is **DRAFT, not ratified** (G7 §2.2).",
               3000, "ADR-0022 §1–§7 (A1, A2); ADR-0040 §1–§6; ADR-0041 §1–§3; ADR-0042 §1–§6; ADR-0043 §1, §2, §4; "
                     "ADR-0037 §4; ADR-0024 §2, §5; ADR-0038 §6; ADR-0034 P4, D-0034-3; ADR-0015; "
                     "floor/genesis-floor.cedar (DRAFT, 17 policies; digest 28ec0e4552c6a915 per G7 §2.2); "
                     "spec/Seats-results-2026.09.29.txt; spec/RunSeats-results-2026.09.29.txt; spec/Seats_proof.tla, "
                     "spec/RunSeats_proof.tla and their 2026.10.02 proof results; ADR-0037 B25; ADR-0043 B25; "
                     "ADR-0046 §4, §5; mechanism/"
                     "GAPS-AND-ASSUMPTIONS.md I14, I33, G19; ToO rev 11 §2.4, §2.9, §4.1; G7 §1.1, §2.2, §7")
    X0, X1 = c.x0, c.x1
    y = c.y

    # ------------------------------------------------------------------ the two alphabets over one carrier
    mid = 300
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
        "(ADR-0040 §4; ADR-0042 §5). A principal that has finished holds its lease until it lapses.",
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
    mh = c.card(mx, top + 40, mid - 40, "No name is shared", [
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
        "states no epoch fence (genesis-floor.cedar header). The lease (ADR-0031) carries the seat, its `alphabet` "
        "and its domain; at the reference the bearer token carries (seat, lease, epoch) into every action "
        "(`mechanism/` I14).",
    ], accent="teal", size=14.5, bullets=False)
    for xx in (bx + pw / 2, rx + pw / 2):
        c.arrow([(xx, cy2), (xx, pbot)], "teal", sw=2.4)
    y = cy2 + ch + 50

    # ------------------------------------------------------------------ mechanism parameters and the two channel rules
    w4 = (X1 - X0 - 3 * 24) / 4
    pcards = [
        ("Build: three mechanism parameters (ADR-0022 §3)", "blue", None, [
            "**Corpus root**: a pinned, content-addressed set; `Read` is scoped to it. Whether it is poisoned is an "
            "Observer finding, not an enforcement decision.",
            "**Tool allowlist**: name plus digest; each entry carries a **hermeticity** obligation: no network, no "
            "filesystem outside the workspace, deterministic given its inputs.",
            "**Round bound**: maximum actions per round; termination, and it bounds the state space.",
        ]),
        ("Run: three mechanism parameters (ADR-0040 §3)", "green", None, [
            "**Run root**: a second pinned, content-addressed set; `Consult` is scoped to it.",
            "**Tool allowlist**: name plus digest and, per entry, **the effect channel it opens**, declared. A Run tool "
            "is not hermetic and is not asked to be.",
            "**Round bound** `R`: admits per round over all three variants; per domain; a placeholder number.",
        ]),
        ("`Invoke` hermeticity: Wasm discharged, native unowned", "red", None, [
            "One allowlisted tool with a socket collapses the envelope to vacuity (ADR-0022 Negative).",
            "**Wasm components: discharged by construction**, ADR-0034 **P4**: instantiated per call, a workspace "
            "directory capability only; no sockets, no wall clock, no free entropy.",
            "**Native tools: unowned.** Using one is declared degeneracy **D-0034-3**: P4 falsified, the principals "
            "reaching it are `Mediated`.",
        ]),
        ("`Actuate` declares its channel: channel fidelity", "amber", "proposed", [
            "P4 cannot hold for a Run tool; **channel fidelity** replaces it: a tool opens the channel its entry "
            "declares and no other (ADR-0042 §6, **Proposed**).",
            "**Nothing checks it** (`mechanism/` G19): the bundle checks only that `channel: {kind, target}` is "
            "present and well-shaped (I33, a schema invented at the reference).",
            "The Run profile that would carry it is unwritten (G7 items 26, 58).",
        ]),
    ]
    ph = max(c.card(0, 0, w4, t, b, size=14, status=s, draw=False) for t, _, s, b in pcards)
    for i, (t, a, s, b) in enumerate(pcards):
        c.card(X0 + i * (w4 + 24), y, w4, t, b, accent=a, size=14, status=s, h=ph, tint=(i < 2))
    y += ph + 60

    # ------------------------------------------------------------------ the full matrix
    c.heading(X0, y, "The matrix: every variant against every seat kind (ADR-0037 §4 Build column; ADR-0043 §2 Run "
                     "column)", size=21)
    c.status(X1, y + 3, "accepted", "ADR-0037 C3, C4 · ADR-0043 C4", anchor="end")
    y += 44
    TW = X1 - X0
    cols = [("Variant", TW * 0.13, {"bold": False}), ("Class (ADR-0015 effects; ADR-0040 §1)", TW * 0.11),
            ("Envelope constraint (record)", TW * 0.17), ("Floor entries (DRAFT)", TW * 0.135),
            ("`thinker` seat", TW * 0.11), ("`observer` seat", TW * 0.13), ("`grant` seat (human)", TW * 0.115),
            ("Veto roster (`observer` seats only)", TW * 0.1)]
    rows = [
        {"group": "Build · ADR-0022 §1 · domain `build` · every Build permit requires `principal.domain == \"build\"` "
                  "and the variant in `context.lease.alphabet`", "accent": "blue"},
        ["`Read(ref)`", "No effect: a resolve inside the pinned set", "`ref` inside the pinned corpus root",
         "permit **B1-read-corpus**", Y, Y, Y, "—"],
        ["`Draft(target, content)`", "No effect (ADR-0040 §1)", "`target` inside the round-scoped workspace",
         "permit **B2**; forbid **B9** (voter role), **B10** (kind ≠ thinker)", Y + " author role only (B9)",
         N + " B10", N + " B10", "—"],
        ["`Invoke(tool, inputs)`", "**Effect**: tool invocation", "`tool` allowlisted by name and digest; `inputs` "
                                                                   "workspace-resident",
         "permit **B3-invoke-allowlisted**; forbid **B9**, **B10**", Y + " author role only (B9)", N + " B10",
         N + " B10", "—"],
        ["`Emit(record)`", "**Effect**: principal emission", "Own round topic, current epoch and round, unsealed",
         "permit **B4-emit-own-topic**", Y, Y + " heartbeats and findings", Y, "—"],
        ["`Submit(digest | ⊥)`", "**Terminal** for the authoring round; offers for promotion (an authority change, "
                                 "ADR-0024)", "Own artifact (`resource.author == principal`)",
         "permit **B5-submit-own-artifact**; forbid **B9**, **B10**", Y + " author role only (B9)", N + " B10",
         N + " B10", "—"],
        ["`Vote(verdict, digest, evidence, rulesEpoch)`", "**Vote**; terminal for the voter's promotion round",
         "Seat held at `rulesEpoch`; `grant` only from a grant seat; never the author (a mechanism constant)",
         "permit **B6-vote-seated** (tightened); forbid **B7-author-recused**, **B8-grant-only-from-grant-seat**",
         N + " never votes: B6 admits only a `grant` seat on the grant roster or an `observer` seat on the veto roster",
         "Only `Vote(deny)`, and only on the veto roster (B6, B8)", Y + " `grant` or `deny`, on the grant roster; "
                                                                        "recused if author (B7)",
         "`Vote(deny)` only (ADR-0024 §5; ADR-0038 §6)"],
        {"group": "Run · ADR-0040 §1 · domain `run` · every Run permit requires `principal.domain == \"run\"`; "
                  "`grant` seats are Build seats (only Build seats vote)", "accent": "green"},
        ["`Consult(ref)`", "**Ingress**, no effect", "`ref` inside the pinned Run root",
         "permit **R4-consult-pinned**; **not** coupled (R3 names `Actuate`, `Report` only)", Y,
         Y + " reads the pinned objects its Thinker consulted (drafter's choice, kept)", N + " no Run row", "—"],
        ["`Actuate(tool, inputs)`", "**Effect**: tool invocation",
         "Allowlisted by name and digest; entry declares its channel",
         "permit **R1-actuate-allowlisted**, **X1-break-glass** (quorum); forbid **B10**; **R3-observer-live**",
         Y + " only while its cell Observer is live (R3)", N + " B10", N + " B10 · no Run row", "—"],
        ["`Report(record)`", "**Effect**: principal emission", "Own round topic, this epoch and round, unsealed",
         "permit **R2-report-own-topic**; **R3-observer-live** for `thinker` seats", Y + " only while its cell "
                                                                                       "Observer is live (R3)",
         Y + " heartbeats and findings; **not coupled**", N + " no Run row", "—"],
    ]
    y += c.table(X0, y, cols, rows, size=14) + 24
    c.para(X0, y, X1 - X0,
           "**Only a** `thinker` **seat holds a variant that writes, runs or offers** (`Draft`, `Invoke`, `Submit`, "
           "`Actuate`), and a `thinker` seat never votes (ADR-0037 §4). A Reader with `Draft` authority, the failure "
           "ADR-0022's follow-up named, cannot arise: the Reader is not a principal. A narrower lease is always "
           "allowed (ADR-0031 §4), so an `observer` seat without `Consult` needs no declaration (ADR-0043 §7).",
           14.5)
    y += 70

    # ------------------------------------------------------------------ the floor, verbatim policy by policy
    c.heading(X0, y, "floor/genesis-floor.cedar: all 17 policies, as the draft states them", size=21)
    c.status(X1, y + 3, "draft", "G7 §2.2 · gates pass, 2026.10.01", anchor="end")
    y += 44
    cols = [("Policy id", TW * 0.14, {"mono": True}), ("Effect", TW * 0.05, {"bold": True}),
            ("Action", TW * 0.12), ("Condition (paraphrased from the Cedar text)", TW * 0.47),
            ("Record it states", TW * 0.22)]
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
        ["B10-only-thinkers-author", F, "`Draft`, `Invoke`, `Submit`, `Actuate`", "`principal.kind != \"thinker\"`",
         "ADR-0037 §4; ADR-0043 §2 adds `Actuate`"],
        {"group": "Run envelopes (ADR-0040 §1, stated as ADR-0041 §1)", "accent": "green"},
        ["R1-actuate-allowlisted", P, "`Actuate`", "domain run; `Actuate` in alphabet; resource in "
                                                   "`context.toolAllowlist`", "ADR-0040 §1, ADR-0041 §1"],
        ["R2-report-own-topic", P, "`Report`", "domain run; `Report` in alphabet; own topic, current epoch and round, "
                                               "unsealed", "ADR-0040 §1, ADR-0041 §1"],
        ["R4-consult-pinned", P, "`Consult`", "domain run; `Consult` in alphabet; resource in `context.runRoot`",
         "ADR-0040 §1; ADR-0041 §1 (new)"],
        ["R3-observer-live", F, "`Actuate`, `Report`", "kind `thinker` and not `context.observerLive` (live Observer "
                                                       "lease, heartbeat within `T_obs`, watermark within `K`)",
         "ADR-0039 §2 as ADR-0041 §2 reads it; `Consult` exempt"],
        {"group": "Floor exceptions (ADR-0013 §2; count 2, bounded by ADR-0026 R6) and the forensic floor", "accent":
            "amber"},
        ["X1-break-glass", P, "`Actuate`", "domain run; `context.breakGlass.quorum`; resource in "
                                           "`context.breakGlass.tools`. Reaches `Actuate` and nothing else",
         "ADR-0009; ADR-0026 R7; ADR-0041 §3"],
        ["X2-erasure", P, "`Erase`", "`context.erasureQuorum`: false from epoch 0, since genesis issues no erasure "
                                     "roster", "ADR-0006; ADR-0029 §5"],
        ["F-forensic-classes", F, "`Erase`", "resource class in F1–F6", "ADR-0028"],
    ]
    y += c.table(X0, y, cols, rows, size=14) + 24
    c.para(X0, y, X1 - X0,
           "Evaluation: any satisfied forbid denies; else any satisfied permit allows; else deny. **Any evaluation "
           "error is a deny** (ADR-0030 §1). Not in the floor, by design: epoch fencing (the mechanism, ahead of the "
           "floor), the round bound (a count), the rules floor (bounds issuances), `Invoke` hermeticity (a property of "
           "the allowlist entry). The draft's own comment still calls ADR-0040 and ADR-0041 \"Proposed\"; both were "
           "ratified in Batch 20 (G7 §1.1).", 14, "muted")
    y += 76

    # ------------------------------------------------------------------ checks
    half = (X1 - X0 - 40) / 2
    c.heading(X0, y, "`spec/Seats.tla` (ADR-0037 §9), TLC 2026.09.29; proved 2026.10.02")
    c.heading(X0 + half + 40, y, "`spec/RunSeats.tla` (ADR-0043 §8), TLC 2026.09.29; proved 2026.10.02")
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
           "with TLC.", 14, "teal")
    c.para(X0 + half + 40, y + t2 + 18, half,
           "**The binding table now agrees with these rows** (ADR-0046 §5, correction 1): `M_OBSEMIT` breaks none of "
           "the three invariants, since it narrows an observer's bound and they are upper bounds, and `M_DOMAIN` breaks "
           "`ObserversConsultAndReport` as well as `NoNameCrossesDomains`. The table had listed `M_OBSEMIT` and missed "
           "`M_DOMAIN`.", 14, "teal")
    c.para(X0, y + t1 + 18 + ph2 + 12 + ph3 + 12, half,
           "`M_OBSEMIT` is ADR-0037 §4's struck provisional Run column (an `observer` seat with emission only): every "
           "property holds and no Observer ever consults. The results file's header still reads \"ADR-0043 §8, "
           "Proposed\"; ADR-0043 was ratified in Batch 20.", 14, "muted")
    return c
