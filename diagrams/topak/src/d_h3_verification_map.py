"""H3 — Verification map: every check the corpus runs, what it checks, what must fail, where its result lives, and
what none of it claims."""
from lib import Canvas

ID, SLUG = "H3", "verification-map"


def lane(c, x0, y, w, cards, gap=56, size=14, label_fn=None):
    """A row of cards joined by arrows. cards: (title, body, accent, status, status_extra, dash, arrow_label).
    Returns the height used."""
    n = len(cards)
    cw = (w - gap * (n - 1)) / n
    h = max(c.card(0, 0, cw, t, b, accent=a, status=s, status_extra=se, draw=False, size=size, bullets=False)
            for t, b, a, s, se, d, al in cards)
    for i, (t, b, a, s, se, d, al) in enumerate(cards):
        x = x0 + i * (cw + gap)
        c.card(x, y, cw, t, b, accent=a, status=s, status_extra=se, dash=d, h=h, size=size, bullets=False)
        if i < n - 1:
            nxt = cards[i + 1]
            acc = nxt[2] if nxt[2] in ("red",) else "grey"
            dash = "7 5" if nxt[2] == "red" or (nxt[3] in ("notbuilt",)) else None
            c.arrow([(x + cw + 2, y + 40), (x + cw + gap - 3, y + 40)], acc, dash=dash)
    return h


def build():
    c = Canvas(ID, "Verification map: what is checked, what is proved, what must fail, and what neither claims",
               "Every check and proof in the corpus. Two methods, two words (ADR-0046 §1): TLC **checks** twenty "
               "TLA+ modules at small constants, each mutation failing the property it targets and each reachability "
               "witness violated; the TLA+ Proof System **proves** the invariants of fifteen of them, 3,036 "
               "obligations, under named assumptions and the absence of the mutations that break each. Then the "
               "policy floor's gates with a pinned proof checker; the reference's tests restating the properties; the "
               "trace harness that replays those tests through an operational model and reads every state against the "
               "abstract confinement invariants; the drift pins; and the lineage "
               "gate suite. Then the honesty layer: a proof is of the module, and what runs is neither checked nor "
               "proved.",
               3400,
               "spec/README.md and every spec/*.tla header and results file; spec/<Module>_proof.tla and "
               "spec/<Module>-proof-results-2026.10.02.txt (15 each); spec/Confinement_A1-results-2026.10.02.txt, "
               "spec/RunConfinement-results-2026.10.02.txt, spec/ConfinementRefinement.tla, "
               "spec/Mechanism-trace-results-2026.10.02.txt and -2026.10.02b.txt; spec/proof-method.md; "
               "spec/proof-results.sh, proof-sync.sh, simulate-run.sh, confinement-run.sh, confinement-gen-results.sh, "
               "runconfinement-run.sh, runconfinement-gen-results.sh, premise-corrections-results.sh and its results "
               "file; spec/theorem-premise-binding.md; ADR-0046 §1–§5, §7, E1, open obligations; "
               "floor/README.md, floor/run-gates.py, floor/genesis-gates-results-2026.10.01.txt; "
               "mechanism/README.md, mechanism/GAPS-AND-ASSUMPTIONS.md §6, mechanism/corpus-pins.sha256; "
               "slm/README.md Part B, slm/gate-suite-results-2026.09.28.txt; ADR-0029 §5 (A1); ADR-0030 §5 A1; "
               "ADR-0033 A5, A6, A7 and A8 (pending), open obligations; ADR-0034 finding 6, A2 (pending); "
               "ADR-0045 §5, T-0045-14, T-0045-28 to 31; G5 §4; G7 §2.2, §2.8, §3; G8 §1, §3, §4, §5, §8, §9; "
               "G9 §2.2, §2.3, §2.5, §2.9, §3, §4, §5, §7 items 56, 69, 73–75, 78, §8, §9")
    X0, X1 = c.x0, c.x1
    W = X1 - X0
    y = c.y

    # ================================================================ 1. the chains
    y += c.heading(X0, y, "1 · Five chains of evidence, from the record to the running code", size=22)
    y += 14
    LP = 30

    # lane A: protocol properties
    top = y
    y += 40
    hA = lane(c, X0 + LP, y, W - 2 * LP, [
        ("Records", ["The ADRs state each property against what an agent's alphabet allows. A module is cited by "
                     "digest in the accepted record it checks; a change is a successor module (`Lease_A1`, "
                     "`RulesFloorNV_rev5`)."], "blue", None, "", None, None),
        ("20 TLA+ modules, TLC", ["Each property with a **mutation that must fail** and a `Never…` "
                                  "**witness that must be violated** (non-vacuity, G2 §3): existential claims, "
                                  "**checked**. Small constants; `tools/tla2tools.jar` 1.7.4, TLC 2.19, tracked for "
                                  "its digest (T-0045-29). The invariants of 15 are also proved (lane 2)."],
         "teal", None, "", None, None),
        ("Rust tests restate them", ["`mechanism/`: **103 tests** across ten binaries (2026.10.02b, ADR-0033 A8, "
                                     "pending; 96 at A7, 61 at A6), each named for the property and the mutation it "
                                     "refuses (GAPS §6). Discrimination tests, not proofs, by the same hand."],
         "teal", "built", "", None, None),
        ("Trace validation: stage 1", ["Tests record every `apply`; `trace2tla.py` converts; `Mechanism.tla` "
                                       "replays and checks `TraceMatches`. **21 traces, 163 steps** (09.30); "
                                       "**22 traces, 168 steps** (10.01); "
                                       "**62 traces, 709 steps** (10.02b), every step matching and every state "
                                       "also read against `ConfinementRefinement.tla`."],
         "teal", "built", "", None, None),
        ("Tested paths only (T-0045-28)", ["What no test reaches is asserted, and six facts come from the trace "
                                           "(issuance validity, approval signatures, the parameter digest; an "
                                           "appraisal's signature, a session proof, a profile's parse). "
                                           "T-0045-28 stays a **trust root** for every deployment."], "red", "open",
         "", "6 4", None),
        ("Stage 2: a Lean model", ["With differential testing against the code (ADR-0033 open obligations; G9 "
                                   "item 56). **Not begun.** The proofs make its target precise and do nothing "
                                   "else for it (ADR-0046 §2)."], "red", "notbuilt", "", None, None),
        ("Stage 3: compilation", ["The Lean model compiled; with a reproducible build (T-0045-30), the rows "
                                  "leave Annex A only on the addendum that cites the chain. **Not begun.**"],
         "red", "notbuilt", "", None, None),
    ], size=14)
    y += hA + 26
    c.region(X0, top, W, y - top, "Protocol properties: spec/ → mechanism/", "teal", dash=None, sw=2, size=15)
    y += 44

    # lane P: the proofs (ADR-0046)
    top = y
    y += 40
    hP = lane(c, X0 + LP, y, W - 2 * LP, [
        ("A frozen module", ["Cited by digest in a record. Fifteen have a proof: every module but "
                             "`Mechanism.tla` (a trace replay), `ConfinementRefinement.tla` (predicates over its "
                             "replayed states), `Lease.tla` (its invariants are `Lease_A1`'s), `RulesFloorNV.tla` "
                             "(superseded by rev 5) and `RulesFloorBase.tla` (definitions)."],
         "blue", None, "", None, None),
        ("`spec/<Module>_proof.tla`", ["**Extends the module without editing it.** Each invariant as `Spec => []P`; "
                                       "its hypothesis is only the mutations that break it; a combined `Safe` under "
                                       "`Mut = \"none\"`; one lemma per mutation saying what it admits."],
         "teal", None, "", None, None),
        ("The prover (T-0045-31)", ["`tlapm` 1.6.0-pre at `7824dab` (binary `e150fb793fb28592…`) with Z3 4.8.9, "
                                    "Zenon 0.8.4, Isabelle2025; installed by `tools/install-tlaps.sh`, **not "
                                    "tracked**, run through `tools/tlapm`."], "blue", "accepted", "C2, C4 · B25",
         None, None),
        ("`*-proof-results-2026.10.02.txt`", ["`proof-results.sh` regenerates each, printing the digest of every "
                                              "module in the EXTENDS chain and of the prover. **3,036 obligations, "
                                              "every one proved**; Batch 25's thirteen regenerated byte for byte at "
                                              "ratification; G9's two (503, 116) are not ratified."],
         "teal", None, "", None, None),
        ("Frozen; kept in step", ["Thirteen cited by digest in ADR-0046 §4, two frozen from G9 on (G9 §3): a change "
                                  "is a successor module with a successor proof. `proof-sync.sh` reports any proof "
                                  "whose specification moved, and every proof is in sync."],
         "teal", None, "", None, None),
        ("Of the module only", ["**Proved** holds of every behaviour of the module, for every constant its "
                                "assumptions admit. It is not a claim about `mechanism/` (T-0045-28) and replaces "
                                "no mutation row (ADR-0046 §2)."], "red", None, "", "6 4", None),
    ], size=14)
    y += hP + 26
    c.region(X0, top, W, y - top, "Proofs (ADR-0046, Batch 25): spec/<Module>.tla → spec/<Module>_proof.tla → TLAPS",
             "teal", dash=None, sw=2, size=15)
    y += 44

    # lane B: the floor
    top = y
    y += 40
    hB = lane(c, X0 + LP, y, W - 2 * LP, [
        ("The floor bundle", ["`genesis-floor.cedar` (17 policies), `genesis.cedarschema`, `genesis-values.json` "
                              "(placeholders). **DRAFT, not ratified.**"], "violet", "draft", "", None, None),
        ("`run-gates.py`, `cedar symcc`", ["Totality, non-vacuity, discrimination, every entry matters, routing, "
                                          "four negative controls, three checker controls (ADR-0030 §5)."],
         "blue", None, "", None, None),
        ("`floor/cvc5-checked`", ["Keeps each query, runs cvc5 with proofs, binds the proof to the query's own "
                                  "declarations and assertions; forwards `unsat` only once the checker accepts. "
                                  "Anything else is `unknown`, a failure."], "blue", None, "", None, None),
        ("The checker (T-0045-14)", ["`ethos` 8dc85c4 against the CPC signature in `tools/cpc/` (from cvc5 1.4.0). "
                                     "**The solver is trusted for nothing** (ADR-0030 A1, Batch 24)."], "blue",
         "accepted", "C1", None, None),
        ("Results 2026.10.01", ["**RESULT: all gates pass.** 4 `holds✓` on checked proofs, 25 `holds°` by cedar's "
                                "folding (T-0045-3), none unchecked. Evidence tree `f8b1196a427a35ed`."], "teal",
         None, "", None, None),
        ("`topak-floor` pins it", ["The floor text is compiled in **by path** and refused at startup unless its "
                                   "bytes match the gated digests; a floor change is a mechanism release."],
         "teal", "built", "", None, None),
    ], size=14)
    y += hB + 26
    c.region(X0, top, W, y - top, "Policy floor: floor/ → topak-floor", "blue", dash=None, sw=2, size=15)
    y += 44

    # lanes C and D side by side
    half = (W - 40) / 2
    top = y
    yy = y + 40
    hC = lane(c, X0 + LP, yy, half - 2 * LP, [
        ("Lineage records", ["`slm/` pipeline at rung 0: every record is **declared** (D-0035-1)."], "grey", None,
         "", None, None),
        ("`gate_suite.py`", ["E1–E5 and distillation cases each seen to fire alone; the §2 monotonicity check: "
                             "**holds** in `bounded` mode, 2,000 trials (09.28)."], "grey", None, "", None, None),
        ("ADR-0035", ["The independence criterion these test. **Not in force**; its §8 item 5 review is owed."],
         "amber", "proposed", "", None, None),
    ], size=14)
    hD = lane(c, X0 + half + 40 + LP, yy, half - 2 * LP, [
        ("`corpus-pins.sha256`", ["The whole-file digest of every record (35) and TLA+ module (14) the reference "
                                  "follows, as it last followed them."], "grey", None, "", None, None),
        ("`cargo test -p topak-core --test drift`", ["Fails when a pinned file changes, or when the code cites a "
                                                      "record that is not pinned."], "teal", "built", "", None, None),
        ("Clearing it", ["Review the change against the code; bring the code into line or register the divergence "
                         "in GAPS; replace the pin line. Whole-file pins trip on History-only edits."], "grey", None,
         "", None, None),
    ], size=14)
    hh = max(hC, hD) + 66
    c.region(X0, top, half, hh, "Lineage gate suite: slm/ (ADR-0035 §8 rehearsal)", "amber", dash="10 6", sw=2,
             size=15)
    c.region(X0 + half + 40, top, half, hh, "Drift: records and modules pinned by the reference", "grey",
             dash=None, sw=2, size=15)
    y = top + hh + 60

    # ================================================================ 2. the module table
    y += c.heading(X0, y, "2 · Every TLA+ module in `spec/`: what it checks, what must fail, what is proved, and "
                          "where its result is", size=22)
    y += c.para(X0, y, W, "Twenty modules and fifteen proof modules (G9 §9: G8's seventeen and thirteen, "
                "with `Confinement_A1`, `RunConfinement` and `ConfinementRefinement`, and two proofs). Properties are invariants checked under "
                "`Mut = \"none\"`; each mutation changes the mechanism, never the property, and must produce a "
                "counterexample; each `Never…` witness must be violated, which shows the behaviour it names is "
                "reachable. The proof column gives each proof module and its obligations (ADR-0046 §4); its results "
                "file is `<Module>-proof-results-2026.10.02.txt`. Results files are dated and never change; every "
                "proof results file, three TLC results files at G8 and the two new modules' since regenerate from a "
                "script, the rest are hand-assembled (G9 item 78). **Pinned** means listed in `mechanism/corpus-pins.sha256`.", 15, "muted") + 14
    cols = [("Module", 230, {"mono": False}), ("Record it checks", 240), ("Properties (invariants)", 420),
            ("Mutations that must fail", 400), ("Witnesses that must be violated", 380),
            ("Driver", 232), ("Results file, constants", 500), ("Proved in (ADR-0046 §4)", 448),
            ("Cited by digest in · status", 438)]
    rows = [
        {"group": "The rules floor and the bootstrap modules", "accent": "blue"},
        ["`RulesFloorBase.tla`", "ADR-0029 §5 shared definitions; the floor as ratified 2026.09.23 (R1, R2, R5, "
         "R6, R7, R9)", "— (the live definition of the floor; no property of its own)", "—", "—",
         "via `bootstrap-run.sh`", "—", "— (extended by `Anchor` and `BreakGlass` and their proofs)",
         "ADR-0026; **live**: ADR-0046 §4 cites the digest proved (`cf2351de2b39cccf`) and does not freeze it "
         "(E1, Batch 26)"],
        ["`RulesFloorNV.tla`", "ADR-0026 §6", "`P1_AllSeatsGranted`, `P2_AtLeastTwo`, `P3_AuthorNotCounted`, "
         "`P4_NoTimeoutGrant`, `P5_AnchorNotApprover`, `P7_BGNoAuthority` (in `Safe`)",
         "drop R1, R2, R3, R4, R5, R7, under `Mech` = `param`, `as0024`, `rev4`", "`NeverPromoted`",
         "`RulesFloorNV-run.sh`", "`RulesFloorNV-results-2026.09.15.txt` (26 runs)", "[[grey|not proved]]",
         "ADR-0026 · frozen (G1)"],
        ["`RulesFloorNV_rev5.tla`", "ADR-0026 R1; ADR-0024 rev 5", "`P1_Unanimity`, `P2_TwoSeatsCounted`, "
         "`P3_AuthorNotCounted`, `P5_AnchorNotApprover`, `P7_BGNoAuthority`, `P9_NoSoloGrant`",
         "drop R1; drop R1 and R9; drop R2; `Mech = \"norecuse\"` (withdrawn R3); drop R5; drop R7",
         "`NeverPromoted`", "`RulesFloorNV_rev5-run.sh`", "`RulesFloorNV-rev5-results-2026.09.23.txt`; five humans "
         "(at four, threshold equals unanimity)", "`RulesFloorNV_rev5_proof.tla` · **262**: each property under "
         "the entry it rests on, `P9` under R2 and (R1 or R9); the three `ASSUME`s proved as lemmas",
         "ADR-0026, ADR-0033, ADR-0046 · **pinned**"],
        ["`NonComposition.tla`", "ADR-0013 §4 (erasure, ADR-0006, with break-glass, ADR-0009, against ADR-0028)",
         "`NC1`, `NC2`", "`M1` (F1 decisions erasable), `M2` (break-glass widens erasure)",
         "`NeverErased`, `NeverBGEffect`, `NeverBGErased`", "`NonComposition-run.sh`",
         "`NonComposition-results-2026.09.23.txt`", "`NonComposition_proof.tla` · **58**: `NC1`, `NC2` not "
         "under `M1`, `M2`", "ADR-0013, ADR-0046"],
        ["`Anchor.tla`", "ADR-0029 §5, bootstrap module 2 of 5; ADR-0025, ADR-0026 §1", "`FloorPreserved`",
         "`M_FLOOR` (issuance accepted without the floor check)", "`NeverIssued`", "`bootstrap-run.sh`",
         "`bootstrap-results-2026.09.23.txt`", "`Anchor_proof.tla` · **40**: `FloorPreserved` under `Mut = "
         "\"none\"`, for every floor subset and epoch bound; `EpochMonotone`", "ADR-0029, ADR-0046 · checked and "
         "**proved**"],
        ["`BreakGlass.tla`", "ADR-0029 §5, bootstrap module 5 of 5; ADR-0009, ADR-0026 R7",
         "`BreakGlassNeverChangesAuthority`", "`M_SCOPE` (mechanism ignores `bgScope`); R7 dropped from `Active`",
         "`NeverBreakGlass`", "`bootstrap-run.sh`", "`bootstrap-results-2026.09.23.txt`",
         "`BreakGlass_proof.tla` · **37**: under `Mut = \"none\"`, assuming `\"R7\" ∈ Active`",
         "ADR-0029, ADR-0046 · checked and **proved**"],
        {"group": "The policy floor's composition and routing", "accent": "blue"},
        ["`FloorComposition.tla`", "ADR-0030 §1, §3, §4 (§9)", "`AdmitImpliesFloorPermit`, `FloorErrorIsDeny`, "
         "`BundleRefusalHonored`, `BundleCannotWriteFloorInputs`, `EnvelopeHolds`",
         "`M_OVERRIDE`, `M_ERR`, `M_FAILOPEN`, `M_WRITE` (each also breaks `EnvelopeHolds`, except `M_FAILOPEN`); "
         "`M_OVERRIDE` also breaks `FloorErrorIsDeny` and `BundleRefusalHonored`, `M_ERR` also "
         "`AdmitImpliesFloorPermit` (ADR-0046 §5; three new TLC rows)",
         "`NeverAdmitted`, `NeverNarrowed`, `NeverFloorError`", "`floor-run.sh`",
         "`FloorComposition-results-2026.09.24.txt`; `premise-corrections-results-2026.10.02.txt`",
         "`FloorComposition_proof.tla` · **171**: each property not under the mutations that break it",
         "ADR-0030, ADR-0033, ADR-0046 · **pinned**"],
        ["`FloorRouting.tla`", "ADR-0030 §5", "`NoWideningWithoutIssuance`, `FloorNeverVacuous`",
         "`M_ROUTE` (only a strict superset is a relaxation), `M_GATE` (non-vacuity off)",
         "`NeverIncomparable`, `NeverRelaxIssued`, `NeverTightened`", "`floor-run.sh`",
         "same file as above. Checks the routing logic, not the analyzer: it assumes the implies answers",
         "`FloorRouting_proof.tla` · **36**: both under `Mut = \"none\"`; a proof of the routing model, not "
         "of the floor's Cedar text", "ADR-0030, ADR-0033, ADR-0046"],
        {"group": "The lease and confinement", "accent": "teal"},
        ["`Lease.tla`", "ADR-0031 §8", "`LeaseAuthorityMonotone`, `NoActionUnderFencedEpoch`, "
         "`Rung0NeverContained`, `RevokedStaysStopped`", "`M_RENEW`, `M_FENCE`, `M_RUNG`, `M_ROLE`, `M_REVOKE`",
         "`NeverActed`, `NeverRenewed`, `NeverRevoked`, `NeverStaleLease`, `NeverSelectiveRevoke`", "`lease-run.sh`",
         "`Lease-results-2026.09.23.txt`, `-25.txt`; `MaxEpoch = 2`, `MaxFence = 3`",
         "[[grey|not proved]]: its invariants are `Lease_A1`'s at rungs 0..2",
         "ADR-0031 · frozen at `7636c6c3364bca9c` · **pinned**"],
        ["`Lease_A1.tla`", "ADR-0031 A1 (renewal keeps the rung)", "as `Lease.tla`, rungs 0..3",
         "as `Lease.tla`, and `M_LOWER` (renewal may lower the rung)", "as `Lease.tla`, and `NeverRenewedAbove0`",
         "`Lease_A1-run.sh`", "`Lease_A1-results-2026.09.28.txt`; `MaxEpoch = 2`, `MaxFence = 3`",
         "`Lease_A1_proof.tla` · **200**: each property not under its mutations",
         "ADR-0031, ADR-0046 · successor of the frozen module · **pinned**"],
        ["`Confinement.tla`", "ADR-0034 §7, A1", "`ContainedMeansConfined`, `NoSilentDowngrade`, `ContestedStopped`, "
         "`FreshAppraisal`", "`M_HOST` (rungs 1, 2), `M_HW` (3), `M_CONTESTED`, `M_UNBOUND`, `M_STALE`, "
         "`M_DOWNGRADE`, `M_PROFILE`, `M_RENEWLOW`", "`NeverContainedEffect`, `NeverMediatedEffect`, "
         "`NeverContested`, `NeverRefused`, `NeverTamperKilled`, `NeverRenewed`, `NeverLapsed`, per declared rung",
         "`confinement-run.sh`; `confinement-gen-results.sh`", "`Confinement-results-2026.09.25.txt`, `-28.txt`, "
         "`-30.txt` (the rung-0 row, D-0034-4); `MaxEpoch = 1`, `MaxIdx = 4`, `MaxGen = 2`, two principals",
         "`Confinement_proof.tla` · **502**: every rung at once, assuming `Declared ∈ 0..3`; `SameGuest` at "
         "grant is not load-bearing", "ADR-0034, ADR-0046 · frozen; succeeded by `Confinement_A1` (finding 6) · "
         "**pinned**"],
        ["`Confinement_A1.tla`", "ADR-0034 finding 6's successor: `Evidence` reads no measurement at rung 0 "
         "(ADR-0033 A7, pending)", "as `Confinement.tla`; `Safe` holds at every rung",
         "as `Confinement.tla`; `M_HOST` breaks rungs 1 and 2 and changes nothing at 0 and 3",
         "`NeverContainedEffect` (holds at rung 0, violated at 1 and 3), `NeverMediatedEffect`, `NeverContested` "
         "(3); the rung-0 row that reached Contested under `M_HOST` now holds",
         "`confinement-run.sh`; `confinement-gen-results.sh` over `confinement-A1-rows-2026.10.02.txt`",
         "`Confinement_A1-results-2026.10.02.txt` (24 rows, rungs 0–3); constants as `Confinement.tla`",
         "`Confinement_A1_proof.tla` · **503**: `Confinement_proof` with one case split changed, `Declared <= 1`: "
         "rung 0 joins rung 1 under the low-rung invariant",
         "ADR-0033 A7 (pending) · frozen from G9 (G9 §3) · **pinned**"],
        {"group": "Seats, Observers and coupling (Build cells)", "accent": "pink"},
        ["`Seats.tla`", "ADR-0037 §9", "`OnlyThinkersAuthor`, `OneSeatPerPrincipal`", "`M_KIND`, `M_SEAT` (the "
         "reference before ADR-0037)", "`NeverActed`, `NeverTwoLive`, `NeverObserverVoted`", "`seats-run.sh`",
         "`Seats-results-2026.09.29.txt`; 2 principals, 3 seats, 4 actions", "`Seats_proof.tla` · **110**",
         "ADR-0037, ADR-0046 · **pinned**"],
        ["`Observers.tla`", "ADR-0038 §8", "`DenyByAnyOf`, `ReachIsBounded`", "`M_QUORUM`, `M_REACH`",
         "`NeverFound`, `NeverRefused`, `CorrelatorNeverFinds`", "`observers-run.sh`",
         "`Observers-results-2026.09.29.txt`; 2 cells, 1 correlator", "`Observers_proof.tla` · **65**",
         "ADR-0038, ADR-0046 · **pinned**"],
        ["`Coupling.tla`", "ADR-0039 §8", "`NoAdmitWithoutLiveObserver`, `UnreadBounded`, `CorrelatorNeverGates`",
         "`M_NOCOUPLE`, `M_MARK`, `M_ROUNDS`, `M_CORR`", "`NeverRoundTwo`, `NeverRefused`, `NeverStaleRefusal`, "
         "`NeverBacklogRefusal`", "`coupling-run.sh`", "`Coupling-results-2026.09.29.txt`; `K = 1`, `R = 3`, "
         "`MaxRound = 2`", "`Coupling_proof.tla` · **320**: for every K, R and MaxRound; `K < R` is not a "
         "premise of `UnreadBounded` (ADR-0046 §5)", "ADR-0039, ADR-0046 · **pinned**"],
        {"group": "Run", "accent": "green"},
        ["`RunCoupling.tla`", "ADR-0042 §8; ADR-0039 §2 as ADR-0041 §2 reads it", "`NoEffectWithoutLiveObserver`, "
         "`UnreadEffectsBounded`, `ConsultNeverCoupled`, `SealCountsEffects`, `RoundBoundCountsAll`",
         "`M_EMITSEQ` (the reference before ADR-0042), `M_COUPLEALL`, `M_ROUNDS`, `M_MARK`, `M_NOCOUPLE`, "
         "`M_BOUNDEFF`", "`NeverRoundTwo`, `NeverRefused`, `NeverRefusedOnActuates`, `NeverConsultedWhileStalled`, "
         "`NeverSealedOnActuates`", "`runcoupling-run.sh`", "`RunCoupling-results-2026.09.29.txt`; `K = 1`, `R = 4`, "
         "`MaxRound = 2`", "`RunCoupling_proof.tla` · **469**: for every K, R and MaxRound; "
         "`SealCountsEffects` not under `M_EMITSEQ` (the table said `M_ROUNDS`)", "ADR-0042, ADR-0046 · **pinned**"],
        ["`RunSeats.tla`", "ADR-0043 §8; ADR-0040 §2", "`OnlyThinkersActuate`, `ObserversConsultAndReport`, "
         "`NoNameCrossesDomains`", "`M_KIND`, `M_DOMAIN` (which also breaks `ObserversConsultAndReport`); "
         "`M_OBSEMIT` is the provisional column, under which every property holds",
         "`NeverActuated`, `NeverObserverReported`, `NeverObserverConsulted`", "`runseats-run.sh`",
         "`RunSeats-results-2026.09.29.txt`; 4 seats, 6 actions", "`RunSeats_proof.tla` · **147**",
         "ADR-0043, ADR-0046 · **pinned**"],
        ["`RunConfinement.tla`", "ADR-0034 A2 (pending), condition (ii): P4 for Run is channel fidelity",
         "`EffectsOnDeclaredChannels`, `ContainedEffectsUseHeldTools`; both also hold under D-0034-5's filter",
         "`M_CHANNEL` (the runtime does not bind the target), `M_NATIVE` (breaks both), `M_FILTER` (only where "
         "D-0034-5 is declared)", "`NeverContainedEffect`, `NeverMediatedEffect`, `NeverRefused` (with and "
         "without the filter), `NeverUndeclaredTarget`: five rows", "`runconfinement-run.sh`; "
         "`runconfinement-gen-results.sh`", "`RunConfinement-results-2026.10.02.txt` (13 rows); 2 principals; "
         "a Wasm, a filtered and a native tool; 3 targets", "`RunConfinement_proof.tla` · **116**: both invariants "
         "inductive on their own; one `ASSUME`, `FilteredBool`",
         "ADR-0034 A2, ADR-0033 A8 (both pending) · frozen from G9 (G9 §3) · **pinned**"],
        {"group": "The operational model of the reference", "accent": "teal"},
        ["`Mechanism.tla`", "ADR-0045 T-0045-28; ADR-0033 A5, A6", "`TraceMatches` (each recorded step's projected "
         "state and result equal the model's)", "a step that differs (the first `ttl` test was caught this way: the "
         "test was wrong, G7 §3)", "—", "`mechanism-trace-run.sh`; `mechanism-trace-results.sh`; `trace2tla.py`",
         "`Mechanism-trace-results-2026.09.30.txt` (21 traces, 163 steps); `-2026.10.01.txt` (22, 168); "
         "`-2026.10.02.txt` (57, 642); `-2026.10.02b.txt` (62 traces, 709 steps); module `73e03ad487c5e4ff`, "
         "`3bfbc88be6cf7fe7` at G8", "[[grey|no proof]]: a trace replay states no invariants; its target is "
         "the refinement (T-0045-28)", "pinned, **not frozen**: moves with the code"],
        ["`ConfinementRefinement.tla`", "ADR-0045 T-0045-28, stage one; ADR-0034 §3, §4 as `Confinement_A1` "
         "states them (ADR-0033 A7, pending)", "`ConfinementRefined`: `RNoSilentDowngrade` (per seat), "
         "`RContestedStopped`, `RFreshAppraisal`, `RContainedAttested` (`Contained`'s premises; "
         "`ContainedMeansConfined` is not checkable here)", "a negative control, a broken invariant, must fire",
         "—", "`mechanism-trace-run.sh`, on every replayed state", "the trace results files from "
         "`-2026.10.02.txt` on: every state keeps the invariants", "[[grey|no proof]]: predicates over replayed "
         "trace states, not a specification (`proof-sync.sh`)", "pinned"],
    ]
    y += c.table(X0, y, cols, rows, size=13.5) + 50

    # ================================================================ 3. gates + bootstrap
    y += c.heading(X0, y, "3 · The floor gates, and the bootstrap specification", size=22)
    wl = W * 0.56
    wr = W - wl - 40
    gy = y
    h1 = c.table(X0, gy, [("Gate (ADR-0030 §5)", 300), ("What it checks", wl * 0.42 - 0), ("2026.10.01", wl - 300 -
                                                                                             wl * 0.42)], [
        ["**Totality**", "never-errors, per policy per applicable action (23 checks)", "all `holds°`: cedar folds "
         "them without a solver query; pass"],
        ["**Non-vacuity**", "always-allows refuted, per action (10 actions)", "pass"],
        ["**Discrimination**", "always-denies refuted, per action", "pass"],
        ["**Every entry matters**", "the floor minus one policy is not equivalent to the floor (17 policies)",
         "pass, each differs"],
        ["**Routing**", "candidate revisions classified by implies both ways (ToO §3.2): tightening, two relaxations, "
         "an incomparable", "pass; the three `holds✓` rest on checked proofs"],
        ["**Negative controls**", "vacuous floor (Read, Consult), erroring policy, dead entry: each gate must catch a "
         "defective floor", "all four caught"],
        ["**Checker controls**", "a solver that answers `unsat` with no proof, a proof of another query, a proof "
         "missing a step", "all three caught; `holds` without a checked proof, whole run: 0"],
        ["**Evidence**", "every solver query, its proof and the checker's verdict", "81 cedar calls, 56 queries, 4 "
         "`unsat` checked, 49 `sat`, 3 `unknown` (the controls); tree `f8b1196a427a35ed`"],
        {"group": "Gate runs: every run before 2026.10.01 is a D-0030-2 run (no checked proofs)", "accent": "grey"},
        ["09.24", "before ADR-0037", "—"],
        ["09.29", "after ADR-0037 §4: `Seat.kind`, B6 tightened, B10", "all pass; 47/47 cases"],
        ["09.29-adr0039", "`observerLive`, R3-observer-live, the values file digested", "all pass; 51/51 cases"],
        ["09.29-adr0041", "`Consult`, `Actuate`, `Report`; R4-consult-pinned; R3 over effects only",
         "all pass; 62/62; **the digests the mechanism pins**"],
        ["09.30", "`persona.T_persona_ms` joins the values file", "identical to 09.29-adr0041"],
        ["10.01", "**proof-carrying** (ADR-0030 A1, Batch 24); floor, schema, values unchanged",
         "all pass; header names checker, signature, wrapper"],
    ], size=13.5, accent="blue")
    h2 = c.table(X0 + wl + 40, gy, [("Bootstrap module (ADR-0029 §5)", wr * 0.3), ("Invariant", wr * 0.36),
                                    ("Status", wr * 0.34)], [
        ["`Genesis`", "`GenesisSatisfiesFloor`", "[[red|not drafted]]; the reference checks genesis rules at "
         "startup instead (T-0045-10). Its shape is a lemma in both proofs below, proved of the floor's definition "
         "and not of genesis contents, which are unwritten"],
        ["`Anchor`", "`FloorPreserved`", "[[teal|drafted and checked]] 2026.09.23; [[teal|proved]] 2026.10.02 "
         "(`Anchor_proof.tla`, 40 obligations)"],
        ["`RulesFloor`", "`PromotionMeetsIssuedQuorum` (A1, replacing `NoPromotionWithoutAllGrantSeats`)",
         "[[red|not drafted]]"],
        ["`Promotion`", "`StaleVotesNeverCount`", "[[red|not drafted]]; owes decide-then-commit (G3), the ADR-0035 "
         "§5 tally condition, A2.2 and A2.3"],
        ["`BreakGlass`", "`BreakGlassNeverChangesAuthority`", "[[teal|drafted and checked]] 2026.09.23; "
         "[[teal|proved]] 2026.10.02 (`BreakGlass_proof.tla`, 37 obligations)"],
    ], size=13.5, accent="brown")
    hb = c.card(X0 + wl + 40, gy + h2 + 24, wr, "Bootstrap specification: partial (G5 §4; G9 §4)", [
        "The anchor **may** bootstrap once a drafted TLA+ bootstrap specification exists: five modules, five "
        "invariants, each with a mutation that must fail. TLC checking is recommended, not required.",
        "Two of five exist, `Anchor` and `BreakGlass`, and are now **proved and not only checked** (ADR-0046 §4; "
        "ADR-0029 B25). `Genesis`, `RulesFloor` and `Promotion` are still owed. The trigger is unmet and remains "
        "optional; bootstrap itself is deliberately not on the open list (G9 §7).",
    ], accent="brown", size=14)
    hs = c.card(X0 + wl + 40, gy + h2 + 24 + hb + 24, wr, "Lineage gate suite: ADR-0035 §8's ratification items", [
        "1 · cases for E1–E5 and distillation, each seen to fire: **passes**.",
        "2 · monotonicity property check: **holds** in `bounded` (ADR-0035 R2, 09.28); failed as first drafted "
        "(`ratio`, E3 13/2000, distillation 241/2000).",
        "3 · E3 overlap: tool ready; first measurements at 20 MB; θ needs slices at training size.",
        "4 · a lineage projected from the reference's log matches its manifest: **done**; three tampers Contested.",
        "5 · an outside review of the bounded-share construction: [[red|owed]].",
    ], accent="amber", status="proposed", status_extra="ADR-0035", size=14)
    y = gy + max(h1, h2 + 24 + hb + 24 + hs) + 50

    # ================================================================ 4. the restatements
    y += c.heading(X0, y, "4 · The Rust tests that restate each property (`mechanism/GAPS-AND-ASSUMPTIONS.md` §6, "
                          "in full)", size=22)
    y += c.para(X0, y, W, "Since 2026.09.30 the restatement is checked, not asserted, on every path a test takes: "
                "each state these tests build records its applied entries and `spec/mechanism-trace-run.sh` replays "
                "them through `Mechanism.tla`, and since 2026.10.02 every traced state is also read against `Confinement_A1.tla`'s "
                "invariants (`ConfinementRefinement.tla`). Nothing a test does not reach is checked. The same kind of evidence the "
                "TLC runs are, by the same hand. Row `SealCountsEffects, and M_ROUNDS carried over` is GAPS §6's "
                "text; the binding table now says the seal breaks under `M_EMITSEQ`, not `M_ROUNDS` (ADR-0046 §5).",
                15, "muted") + 14
    t = [
        ["`Lease.tla`", "`LeaseAuthorityMonotone` / `M_RENEW`", "`mutations.rs` `lease_renewal_is_monotone_and_m_renew_is_refused`"],
        ["`Lease.tla`", "C1 one live lease", "`one_live_lease_per_principal`"],
        ["`Lease.tla`", "`NoActionUnderFencedEpoch` / `M_FENCE`", "`no_action_under_a_fenced_epoch_and_m_fence_is_refused`; e2e `FencedEpoch`"],
        ["`Lease.tla`", "`Rung0NeverContained` / `M_RUNG`", "`rung_zero_is_never_contained_and_says_why`; `confinement.rs` `contained_is_a_lookup_and_each_conjunct_matters`"],
        ["`Confinement.tla`", "`ContestedStopped` / `M_CONTESTED`; `NeverContested` at rung 1", "`confinement.rs` `a_contested_verdict_never_grants_and_revokes_the_principal`, `a_contested_verdict_ends_a_live_lease`; e2e `contain.rs` rogue image"],
        ["`Confinement.tla`", "`ContainedMeansConfined` / `M_UNBOUND` (at `Act`)", "`the_session_is_the_attested_guests_and_m_unbound_is_refused`, `renewal_re_attests_the_same_guest`; `contain.rs` `the_session_is_the_attested_guests`"],
        ["`Confinement.tla`", "`FreshAppraisal` / `M_STALE`", "`an_epoch_fence_invalidates_a_pending_appraisal`; `contain.rs` with the verifier held"],
        ["`Confinement.tla`", "`NoSilentDowngrade` / `M_DOWNGRADE`, `M_RENEWLOW`; `Lease_A1.tla` `M_LOWER`", "`no_silent_downgrade_at_grant`, `m_lower_and_m_renewlow_are_refused`; `contain.rs` renewal lapses"],
        ["`Confinement.tla`", "`ContainedMeansConfined` / `M_PROFILE`", "`contained_is_a_lookup_and_each_conjunct_matters`"],
        ["`Confinement.tla`", "`ContainedMeansConfined` / `M_HOST` at rung 1", "`contain.rs` `every_host_power_subtracts`: a lying rung-1 launcher is believed (T-0045-19)"],
        ["`Lease.tla`", "`LeaseAuthorityMonotone` / `M_ROLE` (ADR-0031 R1)", "`renewal_cannot_change_round_or_role_and_m_role_is_refused`"],
        ["`Lease.tla`", "`NeverSelectiveRevoke` witness (ADR-0031 R3)", "`a_targeted_revocation_ends_one_round_and_not_the_fleet`; e2e targeted revocation leaves a bystander live"],
        ["`Lease.tla`", "`RevokedStaysStopped` / `M_REVOKE` (ADR-0031 R3)", "`a_revoked_principal_persona_or_profile_is_not_granted_again_and_m_revoke_is_refused`"],
        ["`Seats.tla`", "`OnlyThinkersAuthor` / `M_KIND` (ADR-0037 §4)", "`alphabets_are_bounded_by_seat_kind_and_m_kind_is_refused`; `floor.rs` replays B10 and the tightened B6 (47 cases); e2e: the author's voter grant is refused"],
        ["`Seats.tla`", "`OneSeatPerPrincipal` / `M_SEAT` (ADR-0037 §1; finding 1: the reference's behavior before 2026.09.29)", "`one_seat_per_principal_and_m_seat_is_refused`"],
        ["`Observers.tla`", "`DenyByAnyOf` / `M_QUORUM` (ADR-0038 §5)", "`a_correlator_on_the_veto_roster_vetoes_and_its_silence_does_not` (the tally is any-of over the veto roster); e2e: two veto seats silent, promotion completes"],
        ["`Observers.tla`", "`ReachIsBounded` / `M_REACH` (ADR-0038 §1)", "`a_cell_names_a_thinker_seat_in_its_domain_and_only_observers_have_one` (declared reach); **not enforced**: no topic read ACL (I8)"],
        ["`Coupling.tla`", "`NoAdmitWithoutLiveObserver` / `M_NOCOUPLE` (ADR-0039 §2)", "e2e `observer_liveness_couples_run_admits`: refused with no Observer lease, no heartbeat, and after `T_obs` (floor R3); `floor.rs` replays R3"],
        ["`Coupling.tla`", "`UnreadBounded` / `M_MARK`, `M_ROUNDS` (ADR-0039 §2)", "same e2e: refused at a backlog of `K`, refused on a fresh heartbeat with an unchanged watermark, refused a round-2 grant while round 1 is unread (`apply_grant`); `State::observer_covers` is the strict form"],
        ["`RunCoupling.tla`", "`UnreadEffectsBounded` / `M_EMITSEQ` (ADR-0042 §2; **the reference's behaviour before 2026.09.29**, D-0042-1)", "`mutations.rs` `the_sequence_counts_effects_and_m_emitseq_is_refused`; e2e `actuate_is_counted_recorded_and_sealed`: `K` invocations and no report, the next refused by R3"],
        ["`RunCoupling.tla`", "`ConsultNeverCoupled` / `M_COUPLEALL` (ADR-0041 §2)", "same two tests: a `Consult` admitted with no heartbeat at all, and again while `Actuate` and `Report` are refused for the backlog; `floor.rs` replays \"R3 does not couple Consult\""],
        ["`RunCoupling.tla`", "`SealCountsEffects`, and `M_ROUNDS` carried over (ADR-0042 §5)", "`a_run_round_seals_with_its_lease_and_a_run_seat_cannot_abstain`: a renewal does not seal, the seal is 3 after three invocations, and the round-2 grant waits on it; e2e: the grant refused with one invocation unread"],
        ["`RunCoupling.tla`", "`RoundBoundCountsAll` / `M_BOUNDEFF` (ADR-0042 §2)", "`the_round_bound_counts_consult`"],
        ["`RunSeats.tla`", "`OnlyThinkersActuate`, `ObserversConsultAndReport` / `M_KIND`; `NoNameCrossesDomains` / `M_DOMAIN` (ADR-0043 §2; ADR-0040 §2)", "`run_alphabets_are_bounded_by_seat_kind_and_domain`; `floor.rs` replays B10 over `Actuate` and R4 for an observer seat"],
        ["ADR-0042 §3, §4", "the `Actuate` record; `unknown` ahead of the seal; the late result withheld", "e2e `actuate_is_counted_recorded_and_sealed`. **Not modeled in TLA+**: `RunCoupling.tla` assumes a record at every sequence number"],
        ["ADR-0040 §1, ADR-0041 §4", "a retired name is an error, and an error is a deny", "`floor.rs` `a_retired_run_action_is_an_error_not_a_decision`"],
        ["`Coupling.tla`", "`CorrelatorNeverGates` / `M_CORR` (ADR-0039 §4)", "`Rules::cell_observers` excludes correlators from `live(o)`; e2e: the correlator is never granted a Run lease and Run admits proceed"],
        ["ADR-0039 §3 (ADR-0024 A2.3)", "coverage to the seal completes a promotion", "e2e `build_round_promotion_and_fencing`: every grant seat granted, `Tally::Stalled` until `o1` heartbeats `a1`'s seal"],
        ["`FloorComposition.tla`", "`AdmitImpliesFloorPermit` / `M_OVERRIDE`", "`admit_implies_floor_permit_and_m_override_is_refused`; e2e allow-all bundle still floor-bounded"],
        ["`FloorComposition.tla`", "`FloorErrorIsDeny` / `M_ERR`", "same test; `floor.rs` `an_incomplete_slice_is_a_deny_not_a_skipped_forbid`"],
        ["`FloorComposition.tla`", "`BundleRefusalHonored` / `M_FAILOPEN`", "`bundle_refusal_is_honored…`; `fallback.rs` (6 cases)"],
        ["`FloorComposition.tla`", "narrowing witness", "e2e: `Invoke` floor-permitted, bundle-refused"],
        ["`RulesFloorNV_rev5.tla`", "each entry's mutation fails", "`every_rules_floor_entry_has_a_violation_it_catches`; e2e issuance rejections (R1+R9, R2, Authentic)"],
        ["`RulesFloorNV.tla`", "dropping R2 promotes with zero votes", "`without_r2_an_empty_roster_promotes_with_zero_votes`"],
        ["G2 §3", "a threshold needs ≥ 3 counted seats", "`a_threshold_needs_three_counted_seats_to_differ_from_unanimity`"],
        ["ADR-0024", "recusal, timeout ≠ grant, stale votes, veto", "four `tally` tests; e2e promotion"],
        ["`Voting` (cheat sheet)", "`OneValuePerBallot`, chosen-unique, agreement", "`topak-paxos/tests/sim.rs`, both mutations caught"],
    ]
    y += c.table(X0, y, [("Artifact", 330), ("Property / mutation", 1000), ("Rust test", W - 1330)], t,
                 size=13.5, accent="teal") + 50

    # ================================================================ 5. honesty layer
    y += c.heading(X0, y, "5 · The honesty layer: what none of the above claims", "red", size=22)
    y += 6
    y += c.para(X0, y, W, "G7 said, as every checkpoint since G3 had: \"no theorem is proved\". G8 is the first "
                "checkpoint under which a property of the corpus is **proved**, in ADR-0046 §1's sense; MAP 2.3, "
                "the undeclared TLC-versus-TLAPS method, is closed (G8 §1).", 15, "muted")
    y += 6
    g = 24
    w3 = (W - 2 * g) / 3
    cards = [
        ("Proved and checked: two words", [
            "**Proved** names a claim TLAPS discharged and the hypotheses it was discharged under: fifteen modules' "
            "invariants. **Checked** names TLC's evidence: the mutations and witnesses at small constants. Neither is "
            "used of the running reference (ADR-0046 §1; G8 §5).",
            "The trace validation is drift detection against a model of the code, and its refinement check reads "
            "tested paths only and cannot check `ContainedMeansConfined` (G9 §3); a checked gate proof certifies an "
            "implication between two Cedar encodings, not the encoding (G8 §8). The theorem-to-premise table says "
            "what each property **assumed**; it does not strengthen it."], "red"),
        ("Small constants; the prover as written", [
            "\"A property that holds at two principals and one epoch is evidence, not a proof\" (T-0045-29, G5 §8): "
            "since B25 that residual bounds the mutations and witnesses only. Model checking at practical constants: "
            "none yet (G9 item 75).",
            "TLC and the prover are trust-root rows (T-0045-29, T-0045-31), trusted as written: no mutation of either "
            "is run, and the SMT backends' proofs are not rechecked by Isabelle, `tlapm -C` (G9 item 74; §8)."], "red"),
        ("The same hand", [
            "Batch 25's proofs were drafted, checked, mutation-tested and regenerated by the assistant and ratified by "
            "the custodian on the day; the condition meant to make the cited digests someone else's was run by the "
            "drafter (G8 §4, §8). G9's two proofs, their modules and the code under A7 and A8 are one hand's, in "
            "one day, with no second reader (G9 §4, §8).",
            "The operational model was written from the code by the same hand on the same day: the link is "
            "mechanized, not independent (ADR-0033 A5)."], "red"),
        ("What runs is neither checked nor proved", [
            "\"Fifteen modules' invariants are proved, and nothing about the running reference is. The refinement "
            "check covers tested paths; T-0045-28 stands\" (G9 §8). "
            "\"What runs is not the specification\" (ADR-0045 §5, R1): no refinement from the modules to the Rust "
            "exists and the build is asserted, not reproduced: trust-root rows T-0045-28 to 30, for every deployment.",
            "\"The gap is a debt, not a residual the archetype keeps\" (R2): its owner is ADR-0033."], "red"),
        ("What the checker does not cover", [
            "A `holds°` is cedar's own term folding with no query to check: 25 of the run's 29 `holds` rest on the "
            "engine's row (T-0045-3), not the checker's (G9 item 69).",
            "The CPC signature is cvc5's own formalization, trusted as written; the three lying-solver controls test "
            "the wrapper's refusals, not the signature's rules (G7 §4)."], "red"),
        ("The chain still owed (ADR-0033)", [
            "Stage 1, trace validation: A5 (Batch 21), rerun at A6, widened at A7 and A8 (pending) to launch, "
            "appraise, grant and revoke. Stage 2, a Lean model with differential testing, "
            "and stage 3, its compilation: \"the chain proper\", **not begun**. The proofs make stage 2's target "
            "precise and do nothing else for it (ADR-0046 §2; G9 item 56).",
            "The reproducible build (T-0045-30) is untouched. Each addendum says which stage it discharges, and the "
            "rows leave Annex A only on that addendum."], "red"),
    ]
    hh = max(c.card(0, 0, w3, t_, b, accent=a, draw=False, size=14.5) for t_, b, a in cards)
    for i, (t_, b, a) in enumerate(cards):
        cx = X0 + (i % 3) * (w3 + g)
        cy = y + (i // 3) * (hh + g)
        c.card(cx, cy, w3, t_, b, accent=a, h=hh, size=14.5, tint=(i % 2 == 0), dash=None if i % 2 == 0 else "6 4")
    y += 2 * hh + g
    return c
