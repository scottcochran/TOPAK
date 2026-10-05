"""C4 — Confinement rungs: ADR-0034's profile, rungs, verdicts and the four conjuncts of `Contained`."""
from lib import Canvas

ID, SLUG = "C4", "confinement-rungs"

H = "[[green|holds]]"
CE = "[[red|counterexample]] ✓"


def build():
    c = Canvas(ID, "Confinement is attested at lease grant, and the archetype rung is a confidential VM",
               "ADR-0034 gives the lease's `confinement: [digest, rung]` field its meaning: a promoted profile of seven "
               "clauses, four rungs that say how the belief in the profile was established, an appraisal folded into "
               "the grant, and the four conjuncts of `Contained(p)`. One test decides the archetype: **delegate by "
               "failure direction**. **Since G9 two amendments are in force**: A2, the **Run profile**, in which P4 is "
               "**channel fidelity** (Batch 30, with ADR-0042 §6), and A3, four of the reference's choices (Batch 29); "
               "the declared rung is **per seat** (ADR-0023 A1). The reference grants rung 0, launches rung 1 under its "
               "own assertion and rung 3 only SIMULATED (ADR-0033 A7, ratified Batch 29 ahead of ADR-0036, which is "
               "Proposed). **No guest passes P3, so no real principal is** `Contained` (G10 §2.3, item 1); an operator and "
               "an emergency seat are `Mediated` by design. The module's four invariants are **proved** for every rung at "
               "once (B25), and finding 6's successor `Confinement_A1` is checked and proved; **neither proof certifies** "
               "(G10 §2.9), and neither adds confinement to the reference.",
               3200, "ADR-0034 §1–§8, Findings, R1–R4, A1, A2, A3, B10, B17, B20, B22, B25, B29, B30, B31; ADR-0046 §2, "
                     "§4, §5, E2, A1; ADR-0031 §3, §4 (A1), §5; ADR-0023 §6c (A1, B29); ADR-0036 §1 (R1), §2, R4–R6 "
                     "(Proposed); ADR-0035 (Proposed, R4–R7); ADR-0022 §6 (Proposed), B10, R3; ADR-0042 §6 (accepted, "
                     "B30); ADR-0040 §3; ADR-0049 §5; ADR-0050 §1 and ADR-0052 §1 (provisional); ADR-0025 §1 (f), (g); "
                     "ADR-0045 T-0045-16 to T-0045-25, Annex B; spec/Confinement.tla (d0dcf21ce9774885), "
                     "Confinement-results-2026.09.28.txt and -2026.09.30.txt; boundary register (2026.09.13) B6, B12; "
                     "spec/Confinement_proof.tla (2f4b4bb96d1f83f3), Confinement-proof-results-2026.10.02.txt; "
                     "spec/theorem-premise-binding.md; spec/Confinement_A1.tla (715b1c291771c527), "
                     "Confinement_A1-results-2026.10.02.txt, Confinement_A1-proof-results-2026.10.02.txt; "
                     "Confinement-proof-cert-results-2026.10.04.txt, Confinement_A1-proof-cert-results-2026.10.04.txt; "
                     "spec/proof-certification.md; spec/RunConfinement.tla (d0c4aa37934b78b5), "
                     "RunConfinement-results-2026.10.02.txt, RunConfinement_proof.tla (e8612bf4111c7599), "
                     "RunConfinement-proof-cert-results-2026.10.04.txt; ADR-0033 A7, A8, A9, A14; mechanism/ "
                     "GAPS-AND-ASSUMPTIONS.md G1, G19, I37, I39, I43, I44, I47; ToO rev 14 §2.3, §2.6, §2.7, §2.9, "
                     "§7.10; G10 §1, §2.3, §2.5, §2.9, §7 items 1, 74, 88, 89, §8")
    X0, X1 = c.x0, c.x1
    y = c.y
    sx = X0
    c.text(sx, y + 16, "ADR-0034", 16, "ink", bold=True)
    sx += 92
    sx += c.status(sx, y, "accepted", "C2, C4 · ratified 2026.09.28, Batch 10 · A2 (B30), A3 (B29) applied") + 14
    c.text(sx, y + 16, "Discharges ADR-0022 §6 for Build, and with A2 the Run profile. ADR-0035 (the fourth conjunct) "
           "and ADR-0036 (the rung-1 launcher; the rung-0 declared profile, R1) are", 14, "muted")
    from lib import text_width
    sx2 = sx + text_width("Discharges ADR-0022 §6 for Build, and with A2 the Run profile. ADR-0035 (the fourth "
                          "conjunct) and ADR-0036 (the rung-1 launcher; the rung-0 declared profile, R1) are", 14) + 10
    c.status(sx2, y, "proposed")
    y += 52

    # ------------------------------------------------------------------ row A: delegate test + the ladder
    lw = 760
    dt = c.card(X0, y, lw, "Delegate by failure direction (ADR-0034 Context)", [
        "The substrate may carry a mechanism **whose failure only subtracts authority**. A mechanism whose failure "
        "could add or preserve authority is authored by TOPAK and consensus-backed.",
        "**Rung 1**: a faulty or hostile launcher produces a valid-looking lease for a guest it did not confine: a "
        "failure that **adds** authority.",
        "**Rung 2**: the hypervisor can alter a running guest after its launch measurement: the same failure one "
        "layer down.",
        "**Rung 3**: every residual host power is subtractive (§5), met by construction rather than by trusting the "
        "host. Hence the archetype.",
        "With **consensus for grants, local for denials**, the core is PC/EC: an unreachable verifier stops grants; "
        "live leases run to renewal; every refusal, expiry and revocation takes the path that needs no quorum.",
    ], accent="blue", size=14.5)
    # the ladder (staircase)
    lx0 = X0 + lw + 60
    lx1 = X1
    stepw = (lx1 - lx0 - 3 * 20) / 4
    rise = 56
    steph = max(150, dt - 3 * rise - 40)
    ladder = [
        (0, "grey", "declared", "by the operator, verified by nobody", "D-0034-4",
         ["Evidence: none. `Mediated`, always (ADR-0031 §3).", "A rung-0 grant **may name a profile**: its verdict "
          "is then derived from declared clauses (ADR-0036 R1).", "The reference: a seat declared at rung 0 (ADR-0023 §6c)."]),
        (1, "amber", "asserted", "by the launcher", "D-0034-2",
         ["Evidence: the launcher's assertion; appraised by nobody.", "Adds the host operator and orchestrator.",
          "Contested unreachable. The launcher binds the session (ADR-0036).",
          "The reference: the node's launcher (A7, ratified B29)."]),
        (2, "violet", "measured", "launch measurement", "D-0034-1",
         ["Evidence: a measured-boot TPM quote.", "Adds host firmware and the hypervisor.",
          "Detects a rogue launch; not an altered running guest."]),
        (3, "teal", "attested", "hardware, independent verifier", "archetype",
         ["Evidence: a confidential-VM hardware report.", "Adds the CPU vendor's root of trust, the verifier, the "
          "promoted image.", "Every residual host power subtracts.", "The reference: SIMULATED, test keys."]),
    ]
    base = y + 3 * rise + 70
    for i, (r, a, word, how, dk, body) in enumerate(ladder):
        x = lx0 + i * (stepw + 20)
        ty = base - i * rise
        hh = steph + i * rise
        c.rect(x, ty, stepw, hh, a, tint=True, rx=10, sw=2 if r < 3 else 3)
        c.text(x + 16, ty + 54, f"{r}", 50, a, bold=True)
        c.text(x + 62, ty + 30, f"Rung {r} · {word}", 17, a, bold=True)
        c.text(x + 62, ty + 52, how, 13.5, "muted")
        c.pill(x + stepw - 14, ty + 12, dk, a, 12, anchor="end", solid=(r == 3))
        c.para(x + 16, ty + 76, stepw - 32, " ".join(body), 15)
    lad_bot = base + steph
    c.text(lx0, y + 22, "The rung ladder: how the belief in the profile was established", 19, "ink", bold=True)
    c.text(lx0, y + 48, "Words per rung from ADR-0036 R1 (Proposed); rungs, evidence and trusted base from ADR-0034 §2, "
           "§6; degeneracy ids from §8", 14, "muted")
    ay = lad_bot + 28
    c.arrow([(lx0 + 20, ay), (lx1 - 20, ay)], "teal", sw=2.6,
            label="the profile is the constant, the rung the variable: elevation is a fresh grant naming the same digest "
                  "(ADR-0036 R1, Proposed; ADR-0031 A1). Each step changes one thing: a clause verdict or the rung",
            lpos=0.5, lsize=13.5)
    y = max(y + dt, ay + 20) + 40

    # ------------------------------------------------------------------ row B: the rung table and the profile table
    TW = X1 - X0
    c.heading(X0, y, "§2: the rungs, defined (the full table; numbers ascend with strength)")
    y += 40
    cols = [("Rung", TW * 0.07, {"bold": True}), ("Evidence", TW * 0.23), ("Appraised by", TW * 0.16),
            ("Trusted for integrity of the guest", TW * 0.2), ("An untrusted host can", TW * 0.2),
            ("Degeneracy (§8)", TW * 0.14)]
    y += c.table(X0, y, cols, [
        {"cells": ["3 · archetype", "Confidential-VM hardware report (the SEV-SNP or TDX class), with the launch "
                   "measurement covering firmware, kernel, initrd, root hash, profile digest and Persona digest",
                   "An **independent verifier**: not the host operator, not the mechanism (RFC 9334 roles)",
                   "The CPU vendor's root of trust and firmware, the verifier, and the promoted image",
                   "**Only subtract** (§5)", "None: the archetype"], "accent": "teal"},
        ["2", "Measured-boot TPM quote over the same values", "The mechanism, against the profile's reference values",
         "Also the host firmware and hypervisor", "Launch a rogue image (detected: Contested). The hypervisor is "
                                                  "trusted not to alter a running guest", "**D-0034-1**"],
        ["1", "The launcher's assertion of the profile it launched", "Nobody. The orchestrator is the attester by "
                                                                     "construction",
         "Also the host operator and orchestrator", "Nothing, by assumption. The assumption is the trusted-base entry",
         "**D-0034-2**"],
        {"cells": ["0", "None", "—", "—", "`Mediated`, always (ADR-0031 §3)", "**D-0034-4**"], "accent": "red"},
    ], size=14, accent="teal") + 14
    c.para(X0, y, TW, "**The verifier is a trust root**: replacing it adds authority, so its appraisal key is in the "
           "issued rules (ADR-0025 A1, item (f)) and replacing it is an issuance. **Rung 1 cannot produce Contested**: "
           "with no measurement there is nothing to diverge (`NeverContested` holds at rung 1, and at rung 0).", 14,
           "muted")
    y += 64

    c.heading(X0, y, "§1: the confinement profile is a promoted Build artifact, and fixes seven clauses")
    y += 40
    cols = [("#", TW * 0.05, {"bold": True}), ("Clause", TW * 0.64), ("What it removes", TW * 0.31)]
    y += c.table(X0, y, cols, [
        ["P1", "**One channel.** The guest's only I/O device is a single host–guest channel, such as vsock, to the "
               "mechanism's front door (ADR-0033 §2). There is no network device",
         "Egress. The protocol and the channel become the same thing"],
        ["P2", "**Filesystem.** A measured read-only root, the round's workspace read-write, and the pinned corpus root "
               "read-only and content-addressed. Nothing else is mounted", "Reads and writes outside workspace and "
                                                                           "corpus"],
        ["P3", "**No launcher for the principal.** The only code the principal can cause to run is its own inference "
               "and `Invoke` of an allowlisted tool. The image has no shell, package manager or interpreter reachable "
               "from the principal", "Effects that no action names"],
        ["P4", "**Tools are Wasm components**, instantiated per call and handed only a workspace directory capability. "
               "No sockets, no wall clock, and no entropy source not derived from the inputs",
         "ADR-0022 §3's hermeticity obligation, discharged by construction rather than by review (finding 2)"],
        ["P5", "**Inference is inside.** The Persona's weights are in the guest, and their digest is part of the launch "
               "measurement (ADR-0016 §6). An accelerator, if used, runs in confidential-compute mode, and its "
               "attestation is part of the evidence", "Prompt egress (ADR-0017) and device-memory paths"],
        ["P6", "**One principal per guest, one guest per round.** A guest is launched for the grant and destroyed when "
               "the round ends. Nothing survives except through `Submit` and `Emit`",
         "Cross-round and cross-principal state (ADR-0008 placement)"],
        ["P7", "**The profile carries its reference values.** These are the launch measurement it expects and the "
               "minimum platform TCB version it accepts. Changing either is a new profile, and so a promotion",
         "Reference values that move without review"],
    ], size=14, accent="blue") + 14
    y += c.para(X0, y, TW, "**A digest nobody promoted is not a reference value**, so it cannot be attested. **Build "
                "and Run share the schema, not the profile**: Build's is fully determined by ADR-0022's alphabet; Run's "
                "is **ADR-0034 A2**, below.", 14, "muted") + 40

    # ------------------------------------------------------------------ the Run profile (A2, in force since B30)
    c.heading(X0, y, "§1, A2: the Run profile, in force since Batch 30 with ADR-0042 §6: the same schema with "
                     "`domain: run`, and P4 replaced by channel fidelity")
    c.status(X1, y + 3, "accepted", "C2, C4 · A2 at R4, Batch 30", anchor="end")
    y += 44
    cols = [("#", TW * 0.05, {"bold": True}), ("Run clause (ADR-0034 A2 §1)", TW * 0.64),
            ("What it removes", TW * 0.31)]
    y += c.table(X0, y, cols, [
        ["P1", "One channel, to the front door; no network device. Unchanged",
         "Egress from the guest. A Run principal's only route to an effect is an `Actuate` admitted at the front door"],
        ["P2", "A measured read-only root and nothing else mounted. Run has no workspace (it has no `Draft`) and the Run "
               "root is not mounted: an admitted `Consult` delivers its object over the channel, node-side, as ADR-0036 "
               "§3 does `Read` (drafter's choice)", "Reads outside the Run root, and a second, unrecorded ingress path"],
        ["P3", "No launcher for the principal. The only code the principal can cause to run is its own inference and "
               "`Actuate` of an allowlisted tool", "Effects that no action names"],
        {"cells": ["P4", "**Channel fidelity.** Every Run tool is a Wasm component, instantiated per call by the tool host, "
                   "handed a working-directory capability for the round and **one network capability: a connection to "
                   "the target its allowlist entry declares**, and no other socket. **The tool host reads that target "
                   "from the entry of the bundle revision the lease names, and from nowhere else** (R4; ADR-0049 §5). "
                   "It may read a clock and draw entropy: a Run tool is not hermetic. The capability binds the target; "
                   "the declared `kind` (the protocol) is recorded with the call and is not enforced",
                   "An effect on a channel nobody declared. Fidelity holds by construction, a check and not a trust, as "
                   "P4 makes hermeticity one in Build"], "accent": "green"},
        ["P5", "Inference is inside. Unchanged", "Prompt egress and device-memory paths"],
        ["P6", "One principal per guest, one guest per round, and the guest is destroyed when the round ends, which in "
               "Run is when the lease ends (ADR-0042 §5). Nothing survives except through `Actuate` and `Report`",
         "Cross-round and cross-principal state"],
        ["P7", "Unchanged. The tool host is not in the guest's measurement: its identity is fixed by the release "
               "(ADR-0045 T-0045-25)", "Reference values that move without review"],
    ], size=14, accent="green") + 16
    rw = (TW - 2 * 30) / 3
    rcards = [
        ("Who checks it: the tool host's Wasm runtime", "green", "accepted", "B30", [
            "**Channel fidelity is about which channel, not what is said on it**: an `Actuate` that drives the declared "
            "valve the wrong way is an admitted effect with a record, for the floor, the bundle and the Observer.",
            "ADR-0045 **T-0045-24** moves from excluded to **delegated to T-0045-25** for a Wasm tool at the archetype; "
            "excluded for a native one (D-0034-5, D-0034-6). A Run seat without `Actuate` meets P4 vacuously.",
        ]),
        ("Met at ratification (B30), and at the reference since", "teal", "built", "A8 (B31), A9 (B32)", [
            "`spec/RunConfinement.tla`: `Safe` holds with and without the filter; `M_CHANNEL`, `M_NATIVE` and "
            "`M_FILTER` break what they must (13 rows, below); both invariants **proved and certified** (116 "
            "obligations).",
            "The reference: a Run tool hosted as a Wasm module reaches its declared target and nothing else; a lease "
            "whose Run profile claims P4 is held to such tools at decide and at apply (A8). **Since A9 the target is "
            "read from the entry** of the lease's revision; node configuration states no channel (G10 item 84).",
        ]),
        ("What the reference still does not do (A8, A9; G10 item 89)", "red", None, "", [
            "A Run tool is a Wasm **core module**, not a component (PROVISIONAL tool-abi, `mechanism/` I44).",
            "The protocol on the target is not enforced; a **native** tool's target stays an assertion (G19).",
            "Build's P4 is not held to Wasm tools for `Invoke`. Annex B keeps T-0045-24 excluded at the reference, "
            "for a reason A9 ended (item 89).",
            "**No Run principal is** `Contained`: the criterion is set nowhere; Run's `contained = true` is reached "
            "only in a SIMULATED rung-3 run.",
        ]),
    ]
    rh = max(c.card(0, 0, rw, t, b, size=14, status=st, status_extra=se, draw=False) for t, _, st, se, b in rcards)
    for i, (t, a, st, se, b) in enumerate(rcards):
        c.card(X0 + i * (rw + 30), y, rw, t, b, accent=a, size=14, status=st, status_extra=se, h=rh,
               tint=(a != "red"))
    y += rh + 70

    # ------------------------------------------------------------------ row C: appraisal flow + Contained(p)
    half = (TW - 50) / 2
    c.heading(X0, y, "§3: appraisal is a condition of the grant, not a protocol of its own")
    c.heading(X0 + half + 50, y, "§4: `Contained(p)` holds when all four hold")
    y += 44
    fy = y
    # appraisal flow (left half)
    gw = 300
    g1 = c.card(X0, fy, gw, "1 · Nonce from the log", [
        "hash(epoch, committed log index, principal, round). The guest makes a session key pair; evidence binds nonce "
        "and public key. Freshness from log position, not a clock.",
    ], accent="teal", size=13.5, bullets=False)
    g2 = c.card(X0, fy + g1 + 40, gw, "2 · One replica appraises", [
        "It obtains the evidence and the verifier's signed result and proposes a grant entry carrying profile digest, "
        "rung, verdict, nonce, evidence digest and session key. Replicas do not appraise again; at apply each checks "
        "the signature and that the nonce's epoch is current. **The appraisal is kept beside the lease, not in it** "
        "(A3, §3.2): ADR-0031 §1's twelve fields stay closed.",
    ], accent="teal", size=13.5, bullets=False)
    c.arrow([(X0 + gw / 2, fy + g1), (X0 + gw / 2, fy + g1 + 40)], "teal", sw=2.4)
    vx = X0 + gw + 110
    vw = half - gw - 110
    verdicts = [
        ("Attested", "green", "Signature valid, measurements match the profile",
         "**Grant at the seat's declared rung**, which is per seat and changed only by an issuance (ADR-0023 §6c, "
         "A1)"),
        ("Unattestable", "amber", "No evidence, stale nonce, expired endorsement, or verifier unreachable",
         "**Refuse.** No grant, and not a grant at a lower rung"),
        ("Contested", "red", "Signature valid, measurements diverge (Sokolov, arXiv:2608.00801)",
         "Refuse, and order a **targeted revocation of the principal** (ADR-0031 §5), attributed under F2 with the "
         "evidence; not the profile, so one hostile host cannot deny every principal sharing it. **Only a verdict "
         "signed under an issued verifier key, at rung ≥ 2** (A3, §3.7); plain `Revoke` stays an operator's"),
    ]
    vh = [c.card(0, 0, vw, t, [m, "→ " + r], size=13.5, bullets=False, draw=False) for t, _, m, r in verdicts]
    vy = fy
    src_y = fy + g1 + 40 + g2 / 2
    for (t, a, m, r), h in zip(verdicts, vh):
        c.card(vx, vy, vw, t, [m, "→ " + r], accent=a, size=13.5, bullets=False, h=h)
        c.arrow([(X0 + gw, src_y), (X0 + gw + 50, src_y), (X0 + gw + 50, vy + 26), (vx, vy + 26)], a, sw=2.2,
                dash=None if a == "green" else "7 5")
        vy += h + 18
    flow_bot = max(vy - 18, fy + g1 + 40 + g2)
    ny = flow_bot + 24
    nd = c.card(X0, ny, half, "No silent downgrade, at grant and at renewal (§3.4, §3.6; ADR-0031 A1)", [
        "A principal whose evidence does not reach the declared rung is **refused, not granted as** `Mediated`: "
        "downgrading would turn a declared vacuity back into a silent one.",
        "**Renewal re-attests with a fresh nonce and keeps the rung**: Attested renews at the same rung, Unattestable "
        "lets the lease lapse, Contested is a targeted revocation. It re-measures **the launch, not the running "
        "guest**, so it never turns Contested (finding 5). An epoch fence invalidates every pending appraisal.",
        "**The session is the attested guest's** (§3.5): at rungs 2 and 3 the attested session key replaces the "
        "reference's bearer token; at rung 1 the launcher binds the session and is trusted to.",
    ], accent="red", size=14, tint=False)
    left_bot = ny + nd

    # Contained(p) on the right half
    rx0 = X0 + half + 50
    cw = (half - 3 * 16) / 4
    conj = [
        ("1 · Attested lease", "teal", "A live lease at **rung ≥ 1**, granted on an **Attested** verdict at the "
                                       "deployment's declared rung, per seat (ADR-0023 §6c)",
         "The reference launches rung 1 under its own assertion and rung 3 only SIMULATED (A7, ratified B29)"),
        ("2 · Profile meets P3–P5", "teal", "No launcher, Wasm tools only, inference inside; **for a Run principal P4 "
                                            "is channel fidelity** (A2)",
         "Every real profile at the reference declares P3 `fail` (ADR-0036 §4): **no guest passes P3** (G10 item 1)"),
        ("3 · In-house Persona", "teal", "On ADR-0017's axis, at the archetype or its rung 1: weights possessed, no "
                                         "prompt leaves the guest", "A property of the Persona"),
        ("4 · Independence criterion in force", "red", "ADR-0017's lineage-independence criterion: **ADR-0035 "
                                                       "ratified and its θ values set** as floor values (R2)",
         "**ADR-0035 is Proposed** (R4–R7 since G9): this conjunct is false, so `Contained` is empty at every rung. "
         "\"In force\" is the issued rules carrying it, ADR-0025 §1 (g) (A3)"),
    ]
    chh = max(c.card(0, 0, cw, t, [b, "Today: " + s], size=13.5, bullets=False, draw=False,
                     status=("proposed" if a == "red" else None)) for t, a, b, s in conj)
    for i, (t, a, b, s) in enumerate(conj):
        x = rx0 + i * (cw + 16)
        c.card(x, fy, cw, t, [b, "[[" + ("red" if a == "red" else "grey") + "|Today:]] " + s], accent=a, size=13.5,
               bullets=False, h=chh, status=("proposed" if a == "red" else None), tint=(a != "red"))
    jy = fy + chh + 34
    for i in range(4):
        x = rx0 + i * (cw + 16) + cw / 2
        c.arrow([(x, fy + chh), (x, jy), (rx0 + half / 2, jy)], "teal" if i < 3 else "red", sw=2,
                head=False, dash=None if i < 3 else "7 5")
    c.arrow([(rx0 + half / 2, jy), (rx0 + half / 2, jy + 40)], "teal", sw=2.6)
    c.label(rx0 + half / 2, jy - 2, "∧", "teal", 15)
    kw = 520
    kh = c.card(rx0 + (half - kw) / 2, jy + 40, kw, "`Contained(p)`: no members at any rung today", [
        "Before ADR-0034 the reason was that no rung had semantics; now **the criterion is the only missing premise** "
        "(finding 1). The custodian kept ADR-0031's stricter reading: the draft had left independence out (R2).",
        "The reference computes the four as a lookup and names each that fails; it answers yes only for a "
        "**SIMULATED** rung-3 lease under a criterion a test issued, Build or Run: a witness, not a claim (G10 §2.3).",
        "**An operator and an emergency seat are** `Mediated` **by design**: a person is not confined (ADR-0050 §1; "
        "ADR-0052 §1, both provisional).",
    ], accent="red", size=14, bullets=False)
    cy2 = jy + 40 + kh + 24
    bh = c.card(rx0, cy2, half, "Boundary register: B6 and B12 (2026.09.13)", [
        "**B6, principal type** `Contained` / `Mediated`: safety theorems quantify inside only; fixed at **lease grant**. "
        "Rung 0 is `Mediated`, always.",
        "**B12, deployment stack** (sandbox and below): the register's empty cell, \"no mechanism exists\". ADR-0031 §3 "
        "gave it its instant, the grant; ADR-0034 gives the rungs; the mechanism half is narrowed, not closed: a rung-1 "
        "launcher and a simulated rung 3 (`mechanism/` G1; A7, ratified B29). ToO A1 is not met.",
    ], accent="grey", size=14)
    right_bot = cy2 + bh
    y = max(left_bot, right_bot) + 60

    # ------------------------------------------------------------------ row D: host powers + trusted base + degeneracies
    c.heading(X0, y, "§5: what an untrusted host can still do, at rung 3")
    c.heading(X0 + half + 50, y, "§6: the trusted base, per rung (now ADR-0045 T-0045-16 to 22)")
    y += 40
    cols = [("Host power", half * 0.42), ("At rung 3", half * 0.38), ("Direction", half * 0.2, {"bold": True})]
    t1 = c.table(X0, y, cols, [
        ["Refuse to launch, kill, pause, starve CPU or memory", "Round ends, or its lease expires",
         "[[green|Subtracts]] (availability)"],
        ["Withhold or delay the channel", "Actions do not arrive", "[[green|Subtracts]]"],
        ["Launch an image other than the one asked for", "Measurement diverges: Contested, principal revoked",
         "[[green|Subtracts]]"],
        ["Alter a running guest", "The hardware's integrity protection makes this the guest's death",
         "[[green|Subtracts]], **assumed** (§6)"],
        ["Attach a device, such as a network card", "Changes the measurement at the next attestation; P1's image "
                                                    "brings up no other device", "[[green|Subtracts]]"],
        {"cells": ["Side channels, physical memory interposers", "Not prevented", "[[red|Residual]] (§6)"],
         "accent": "red"},
    ], size=14, accent="teal")
    cols = [("Rung", half * 0.1, {"bold": True}), ("Enters the trusted base", half * 0.5),
            ("Leaves it, compared with rung 1", half * 0.4)]
    t2 = c.table(X0 + half + 50, y, cols, [
        ["3", "CPU vendor root of trust and firmware (T-0045-16); the independent verifier (T-0045-17); the promoted "
              "image, including the Wasm runtime (T-0045-20)", "Host operator, orchestrator, hypervisor and host kernel, "
                                                              "for guest integrity. They keep availability"],
        ["2", "Also host firmware and hypervisor (T-0045-18)", "Host operator, for launch integrity only"],
        ["1", "Also host operator and orchestrator (T-0045-19)", "—"],
        {"cells": ["0", "Nothing: the host at rung 0 is an **excluded** row (T-0045-22); a declared profile is "
                        "verified by nobody (T-0045-20 at rung 0)", "—"], "accent": "grey"},
    ], size=14, accent="blue")
    y += max(t1, t2) + 14
    c.para(X0 + half + 50, y, half, "**This trades an assumption for a mechanism**: A1 conditioned on nothing becomes a "
           "claim resting on named, audited components with a published attack history, which is still strictly more. "
           "The hardware is in the \"operationally audited\" layer, not proved. T-0045-21 (inference attestation) is "
           "reserved.", 14, "muted")
    y += 90

    c.heading(X0, y, "§8: degeneracies on this axis (declaration degeneracies; ratified as record-level entries)")
    y += 40
    cols = [("Id", TW * 0.08, {"bold": True}), ("Parameter → deployed value", TW * 0.2), ("Premises falsified",
                                                                                       TW * 0.12),
            ("Theorems voided", TW * 0.28), ("Type changes (ADR-0023 §6b)", TW * 0.32)]
    y += c.table(X0, y, cols, [
        ["D-0034-1", "Confinement rung → 2", "None", "None",
         "The hypervisor and host firmware enter the trusted base"],
        ["D-0034-2", "Confinement rung → 1", "None", "None",
         "The host operator and orchestrator enter the trusted base; Contested becomes unreachable"],
        ["D-0034-3", "Profile admits a native tool", "P4", "Every `Contained` theorem, for principals whose alphabet "
                                                           "reaches that tool", "Those principals become `Mediated`"],
        {"cells": ["D-0034-4", "Confinement rung → 0", "A1", "Every `Contained` theorem",
                   "Every principal becomes `Mediated`. **The reference's position** for a seat declared at rung 0"],
         "accent": "red"},
        {"cells": ["D-0034-5 (A2)", "A Run tool is native, under an egress filter in the tool host that admits only "
                   "its declared target", "P4 (Run), as stated; channel fidelity moves from a check to a trust", "None",
                   "The tool host enters the trusted base for channel fidelity: T-0045-25 widens, and T-0045-24 is "
                   "delegated to it on trust rather than by construction"], "accent": "green"},
        {"cells": ["D-0034-6 (A2)", "A Run tool is native and unfiltered: **the reference today for a native tool**, "
                   "T-0045-24 excluded for it", "P4 (Run)",
                   "Every `Contained` theorem, for Run principals whose alphabet reaches that tool",
                   "Those principals become `Mediated`. The Run counterpart of D-0034-3"], "accent": "green"},
    ], size=14, accent="blue") + 14
    c.para(X0, y, TW, "Rungs 1 and 2 void no theorem; they move what the theorems rest on (ADR-0023 §4a). ADR-0036 adds "
           "D-0036-1 (an interpreter reachable from the principal: P3 falsified), the same kind of entry as D-0034-3; "
           "ADR-0036 is Proposed. D-0034-5 and D-0034-6 are A2's, in force since Batch 30.", 14, "muted")
    y += 64

    # ------------------------------------------------------------------ row E: Confinement.tla
    c.heading(X0, y, "§7: `spec/Confinement.tla` (digest d0dcf21ce9774885), runs of 2026.09.28 (R1) and the rung-0 "
                     "addendum of 2026.09.30 (A1)")
    y += 40
    cols = [("Check", TW * 0.36), ("Rung / filter", TW * 0.07), ("Mutation", TW * 0.11, {"mono": True}),
            ("Invariant", TW * 0.2, {"mono": True}), ("Result", TW * 0.26)]
    rows = [
        {"group": "Rungs 1–3 (2026.09.28, `Confinement-results-2026.09.28.txt`)", "accent": "teal"},
        ["Full mechanism", "1, 2, 3", "none", "Safe (all four)", H + " (64,562 · 118,042 · 1,594,644 states)"],
        ["**Ratification witness: a** `Contained` **principal takes an admitted effect**", "1, 2, 3", "none",
         "NeverContainedEffect", CE + " at each (conditional on the criterion conjunct, not modelled)"],
        ["Discrimination: a `Mediated` principal also acts", "1, 2, 3", "none", "NeverMediatedEffect", CE + " at each"],
        ["A rogue launch is detected", "2, 3", "none", "NeverContested", CE],
        ["Rung 1 cannot detect one", "1", "none", "NeverContested", H + ", as §2 says"],
        ["An unreachable verifier refuses", "3", "none", "NeverRefused", CE],
        ["Tampering becomes a subtraction", "3", "none", "NeverTamperKilled", CE],
        ["The host is untrusted where the rung trusts it", "1", "M_HOST", "ContainedMeansConfined", CE],
        ["″", "2", "M_HOST", "ContainedMeansConfined", CE + ": launch, tamper, appraise, grant, act"],
        {"cells": ["″", "**3**", "M_HOST", "Safe", H + ": **nothing at rung 3 trusts the host**"], "accent": "teal"},
        ["The hardware does not protect a running guest", "3", "M_HW", "ContainedMeansConfined", CE],
        ["Contested treated as Attested", "2 · 3", "M_CONTESTED", "ContestedStopped · ContainedMeansConfined", CE],
        ["Lease not bound to the attested guest", "1 · 3", "M_UNBOUND", "ContainedMeansConfined", CE],
        ["An appraisal survives a fence", "3", "M_STALE", "FreshAppraisal", CE],
        ["Unattestable granted at rung 0", "3", "M_DOWNGRADE", "NoSilentDowngrade", CE],
        ["`Contained` ignores the profile", "3", "M_PROFILE", "ContainedMeansConfined", CE],
        ["A renewal re-attests and keeps the lease (R1)", "1, 2, 3", "none", "NeverRenewed", CE + " at each"],
        ["An unreachable verifier at renewal lets the lease lapse (R1)", "3", "none", "NeverLapsed", CE],
        ["A renewal never turns Contested (R1)", "1, 2, 3", "none", "NeverRenewContested", H + " at each (finding 5)"],
        ["Unattestable renewal renewed at rung 0 (R1)", "3", "M_RENEWLOW", "NoSilentDowngrade", CE],
        ["″", "1 · 2", "M_RENEWLOW", "NoSilentDowngrade", H + ": no verifier, so nothing to fail at renewal"],
        {"group": "Rung 0, `Declared = 0` (2026.09.30, `Confinement-results-2026.09.30.txt`): D-0034-4's deployment",
         "accent": "grey"},
        ["Full mechanism", "0", "none", "Safe", H + " (64,562 states)"],
        ["**D-0034-4, checked: no effect is ever counted** `Contained`", "0", "none", "NeverContainedEffect",
         H + ": the declared vacuity"],
        ["A `Mediated` principal acts", "0", "none", "NeverMediatedEffect", CE],
        ["Rung 0 cannot detect a rogue launch", "0", "none", "NeverContested", H + ", as at rung 1"],
        ["A renewal keeps the lease", "0", "none", "NeverRenewed", CE],
        ["A renewal never turns Contested", "0", "none", "NeverRenewContested", H],
        ["Unattestable renewal renewed at rung 0", "0", "M_RENEWLOW", "NoSilentDowngrade",
         H + " trivially: rung 0 is the declared rung"],
        ["Lease not bound to the guest", "0", "M_UNBOUND", "ContainedMeansConfined",
         H + ": nothing is `Contained` to mis-attribute"],
        ["The host is untrusted", "0", "M_HOST", "Safe", H + " (646,635 states)"],
        {"group": "`Confinement_A1.tla`, finding 6's successor (2026.10.02, `Confinement_A1-results-2026.10.02.txt`, 24 rows)",
         "accent": "teal"},
        ["Full mechanism", "0, 1, 2, 3", "none", "Safe", H + " at each"],
        ["A `Contained` effect is reachable", "0 · 1, 3", "none", "NeverContainedEffect",
         H + " at 0; " + CE + " at 1 and 3"],
        {"cells": ["**Finding 6, corrected: rung 0 cannot reach Contested**", "0", "M_HOST", "NeverContested · Safe",
                   H + " (the row `Confinement.tla` fails)"], "accent": "teal"},
        ["The host is untrusted where the rung trusts it", "1, 2 · 3", "M_HOST", "ContainedMeansConfined · Safe",
         CE + " at 1, 2; " + H + " at 3"],
        ["Each §7 mutation at rung 3", "3", "M_HW … M_RENEWLOW", "its target", CE + " at each"],
        {"group": "`RunConfinement.tla` (`d0c4aa37934b78b5`), ADR-0034 A2's condition (ii): channel fidelity for Run "
                  "(2026.10.02, `RunConfinement-results-2026.10.02.txt`, 13 rows; a Wasm, a filtered and a native tool)",
         "accent": "green"},
        ["Full mechanism", "no filter", "none", "Safe", H],
        ["Full mechanism, D-0034-5 declared", "filter", "none", "Safe", H],
        ["The Wasm runtime does not bind the target", "no filter", "M_CHANNEL", "EffectsOnDeclaredChannels", CE],
        ["″", "no filter", "M_CHANNEL", "ContainedEffectsUseHeldTools", H + ": the tool is still a held one"],
        ["The mechanism's check dropped: a native tool under a P4-pass lease", "no filter", "M_NATIVE",
         "EffectsOnDeclaredChannels", CE],
        ["″", "no filter", "M_NATIVE", "ContainedEffectsUseHeldTools", CE],
        ["The egress filter does not bind", "filter", "M_FILTER", "EffectsOnDeclaredChannels",
         CE + ": the filter is load-bearing where D-0034-5 is declared"],
        ["″", "no filter", "M_FILTER", "Safe", H + ": and changes nothing where it is not"],
        ["Witness: a `Contained` Run principal acts", "no filter", "none", "NeverContainedEffect", CE],
        ["Witness: a `Mediated` Run principal acts too", "no filter", "none", "NeverMediatedEffect", CE],
        ["Witness: the check fires (a native tool under a P4-pass lease refused)", "no filter · filter", "none",
         "NeverRefused", CE + " at each"],
        ["Witness: a `Mediated` principal's native tool reaches an undeclared target", "no filter", "none",
         "NeverUndeclaredTarget", CE + ": the model lets a tool misbehave"],
    ]
    y += c.table(X0, y, cols, rows, size=13.5, accent="teal") + 14
    y += c.para(X0, y, TW, "**The** `M_HOST` **rows are the rung ladder, checked**: the same mutation breaks containment at rungs "
           "1 and 2 and changes nothing at rung 3; `M_HW` shows rung 3 rests on the hardware assumption. Under "
           "`M_STALE`, `M_DOWNGRADE` and `M_RENEWLOW`, `ContainedMeansConfined` still holds: those clauses are about "
           "honest declaration, not containment. **Finding 6**: under `M_HOST` at rung 0 the module reaches Contested "
           "(it reads a launch measurement rung 0 does not have). This table carries only the rung-0 rows the defect "
           "does not affect; **the successor module carries the correction** (the last group).", 14, "muted")
    y += 30
    pr = [
        "`spec/Confinement_proof.tla` (`2f4b4bb96d1f83f3`) extends the frozen module and proves its four invariants "
        "**for every declared rung in 0..3 at once**, assuming `Declared ∈ 0..3`: 502 obligations, every one proved "
        "by the prover T-0045-31 (ADR-0046 §4). That is §7's ratification condition, `Safe` at every rung, stated as "
        "a theorem (ADR-0034 B25).",
        "Each theorem takes as hypothesis only the mutations that break it: `ContainedMeansConfined` not under "
        "`M_HOST`, `M_HW`, `M_CONTESTED`, `M_UNBOUND`, `M_PROFILE`; `NoSilentDowngrade` not under `M_DOWNGRADE`, "
        "`M_RENEWLOW`; `ContestedStopped` not under `M_CONTESTED`; `FreshAppraisal` not under `M_STALE`. The rows "
        "above stay with TLC: that a mutation reaches a bad state is existential (ADR-0046 §2).",
        "**Correction 4** (ADR-0046 §5): a lease is bound to its guest by `Act`'s generation check, which `M_UNBOUND` "
        "removes, **not by** `SameGuest` **at grant**, which the proof never uses. The proof needed an invariant of six "
        "clauses binding a lease to the guest generation it was granted against (G8 §3, result 1).",
        "**The successor's proof**, `Confinement_A1_proof.tla`: 503 obligations, the same proof with one case split "
        "moved, so that rung 0 joins rung 1 under the low-rung invariant.",
        "[[red|Neither proof certifies]] (ADR-0046 A1; G10 §2.9, item 74): of each, 3 obligations, large type-invariant "
        "steps, are proved by Z3 and by nothing else, since cvc5 does not prove them; 337 or 338 are closed by "
        "normalization, 157 by SMT with a proof the checker accepted, 5 temporal steps by LS4. Restructuring is "
        "deferred by the custodian. `RunConfinement_proof.tla` **is certified**: 116 obligations, 71 trivial, 42 "
        "checked SMT, 3 LS4.",
        "**A proof of the module adds nothing at the reference**: for a real deployment `ContainedMeansConfined` and "
        "`ContestedStopped` stay void; `NoSilentDowngrade` and `FreshAppraisal` hold at the reference's apply-time "
        "checks, on every traced state (binding table; trace validation at 82 traces, ADR-0033 A14). `Contained` has "
        "no members in any real run (G10 §2.3, §8).",
    ]
    c.card(X0, y, TW, "Since 2026.10.02: the four invariants are proved, every rung at once (ADR-0034 B25); proved, "
           "and not certified", pr, accent="teal", size=14, status="accepted", status_extra="ADR-0046 · C2, C4 · B25")
    return c
