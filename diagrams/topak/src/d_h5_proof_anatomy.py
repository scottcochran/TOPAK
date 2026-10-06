"""H5 — Proof anatomy: how a proof module is built, the four shapes its inductive invariant took, and the loop that
keeps each proof the proof of its specification, with the certified run beside it. The mechanism only: which modules
are proved, and their counts, are H3's; certification route by route is H6's; each property's hypotheses are G3's
"Breaks under" column."""
from lib import Canvas

ID, SLUG = "H5", "proof-anatomy"


def build():
    c = Canvas(ID, "How a proof is built and kept in step",
               "Twenty-two of the twenty-seven modules under `spec/` have a **proof module** (ADR-0046, Batch 25; "
               "G10 §2.9), and `spec/proof-sync.sh` records why each of the other five has none. This "
               "diagram is the mechanism, not the inventory: one proof module part by part, the four shapes its "
               "inductive invariants took and what the proofs of 2026.10.04 and 10.05 added, and the loop that keeps "
               "each proof the proof of its specification, now with a **certified** run beside it (ADR-0046 A1, Batch "
               "28). TLC **checks** the mutations and witnesses, which are existential claims; the prover **proves** "
               "the invariants, which are universal, under named hypotheses (ADR-0046 §1); a proof is **certified** "
               "when every obligation is closed by the prover's normalization, a checked proof, or LS4. None is a "
               "claim about the running reference (T-0045-28). Which modules are proved, with their counts, is H3; "
               "certification route by route is H6; each property's hypotheses are G3's \"Breaks under\" column. Section 4 "
               "sets beside the loop the same loop for a **Lean re-encoding** (ADR-0053, **Proposed**; H7), which "
               "proves the same theorems again, of an encoding, and is kept in step the same way.",
               3200, "spec/proof-method.md §1 (its table, with the five rows of 2026.10.04), §2, §3, §5, §5a, §6 "
                     "(as revised since 7075169); spec/proof-certification.md §2, §4, §9, §10; spec/proof-cert.sh; "
                     "spec/Lease_A1-proof-cert-results-2026.10.04.txt (a9e59ca0937e3fed); spec/README.md, TLAPS proofs "
                     "and practice items 6 to 8; spec/Labels_proof.tla, spec/Emergency_proof.tla, "
                     "spec/Operators_proof.tla, spec/BreakGlass_A1_proof.tla, spec/NonComposition_A1_proof.tla and "
                     "their results files; tools/TLAPS-PIN; "
                     "spec/Lease_A1_proof.tla (6f39c7711252c8de) and spec/Lease_A1-proof-results-2026.10.02.txt "
                     "(d4b39bd7094c38d1) over spec/Lease_A1.tla (0b5eac7a7309be2f); spec/Observers_proof.tla, "
                     "spec/Seats_proof.tla, spec/Confinement_proof.tla, spec/Confinement_A1_proof.tla and its results file, "
                     "spec/RunConfinement_proof.tla and its results file, spec/Coupling_proof.tla, "
                     "spec/RunCoupling_proof.tla, spec/Anchor_proof.tla; spec/proof-results.sh; spec/proof-sync.sh; "
                     "tools/tlapm; ADR-0046 §1 to §5, §7, R2, B25 and E1 (Batch 26); ADR-0045 T-0045-28, T-0045-31; "
                     "spec/RulesFloorBase.tla; ADR-0026 A1 note, A2; ADR-0046 A1, E2 (Batch 28); G8 §5; G9 §3 "
                     "(finding 5); G10 §2.1, §2.9, §3, §5, §7 items 73, 74, 90; ToO rev 14 §11.3; ADR-0053 (Proposed) §1, §2, "
                     "§4; spec/proof-method.md §5b and §6 (2026.10.05); tools/LEAN-PIN, tools/install-lean.sh, "
                     "tools/lean-report.sh, tools/lean-sync.sh; spec/lean/results.sh and its results file; "
                     "spec/lean/README.md (mutation check)")
    X0, X1 = c.x0, c.x1
    W = X1 - X0
    y = c.y

    # ================================================================== 1 · anatomy
    y += c.heading(X0, y, "1 · One proof module, part by part: `Lease_A1_proof.tla` (200 obligations)", "teal", 22)
    y += 4
    gap = 60
    cw = (W - 3 * gap) / 4
    parts = [
        ("1 · Extend the frozen module; never edit it", "teal", [
            "`EXTENDS Lease_A1, TLAPS`. `Lease_A1.tla` (`0b5eac7a7309be2f`) is frozen by the records that cite it; "
            "the proof restates nothing from it (ADR-0046 §4).",
            "A constant a run script set per row becomes a named `ASSUME` where a proof needs it: "
            "`Active \\subseteq AllEntries` in `Anchor`, `Declared \\in 0..3` in `Confinement`, `Filtered \\in "
            "BOOLEAN` in `RunConfinement` (`FilteredBool`). `Lease_A1` needs "
            "none: `MaxEpoch` and `MaxFence` only cut the state space, so its theorems hold for every value.",
            "An unnamed `ASSUME` in a base module is a fact to TLC and nothing to the prover; it is restated as a "
            "lemma proved from the definitions (`GenesisEntries` in `Anchor_proof`).",
        ]),
        ("2 · A type invariant, proved under every mutation", "teal", [
            "`TypeOK`: `lease` and `prev` in `[Principals -> LeaseRec]`, `epoch` and `fence` naturals, "
            "`revoked \\subseteq Principals`.",
            "`InitTypeOK` and `NextTypeOK`, one step per action, with **no hypothesis on** `Mut`.",
            "Its job: an `EXCEPT` on one principal leaves the others alone, which the prover cannot see unless the "
            "function's domain is in scope (proof-method §3, §4).",
        ]),
        ("3 · One inductive step per invariant, under its hypothesis", "teal", [
            "Each theorem takes as hypothesis **only the mutations that break it**, e.g. `ASSUME Mut # \"M_FENCE\"`. "
            "The hypotheses restate the binding table's \"Breaks under\" column (ADR-0046 §4, §5).",
            "The `Next` lemma has one step per action: `UNCHANGED vars`, `Revoke`, `Grant(p)`, `Renew(p)`, "
            "`Act(p)`, `EndRound(p)`, `RevokeLease(p)`. A failed step names the action.",
            "The inductive invariant is the property alone, the property with `TypeOK`, or more (section 2).",
        ]),
        ("4 · Lift to always, then combine", "teal", [
            "`Init => Inv` and `Inv /\\ [Next]_vars => Inv'`, then `PTL DEF Spec`: three lines per theorem.",
            "`SafeAlways` under `Mut = \"none\"` cites one `Spec => []P` step per theorem before its `PTL` step: the "
            "prover cannot discharge a theorem's hypothesis inside `PTL` (proof-method §4).",
            "A property true in every state needs no induction: `Rung0NeverContained` is a state lemma, "
            "`Rung0Valid`, lifted by `PTL`.",
        ]),
    ]
    ph = max(c.card(0, 0, cw, t, b, a, size=14, draw=False) for t, a, b in parts)
    for i, (t, a, b) in enumerate(parts):
        x = X0 + i * (cw + gap)
        c.card(x, y, cw, t, b, a, size=14, h=ph)
        if i < 3:
            c.arrow([(x + cw + 6, y + ph / 2), (x + cw + gap - 6, y + ph / 2)], "teal")
    y += ph + 36

    # the five theorems, in full
    y += c.heading(X0, y, "Its five theorems", "ink", 19)
    cols = [("Theorem", W * 0.17, {"mono": True}), ("Hypothesis (the mutations it excludes)", W * 0.2),
            ("Inductive invariant", W * 0.17), ("The steps", W * 0.28), ("Shape (section 2)", W * 0.18)]
    rows = [
        ["LeaseAuthorityMonotoneAlways", "`Mut # \"M_RENEW\"`, `Mut # \"M_ROLE\"`, `Mut # \"M_LOWER\"`",
         "`TypeOK` and the property",
         "`RenewRefines`: under the hypothesis a renewal refines its predecessor; `NextMonotone`: seven cases",
         "A relation between `lease` and `prev`, kept per principal"],
        ["NoActionUnderFencedEpochAlways", "`Mut # \"M_FENCE\"`", "The property alone",
         "`NextFenced`: the work is in `Act`, whose epoch check makes both epochs equal",
         "A flag (`staleAdmitted`) and an append-only set (`acted`)"],
        ["Rung0NeverContainedAlways", "`Mut # \"M_RUNG\"`", "None: true in every state",
         "`Rung0Valid`, by the definition of `Contained`; then `PTL`", "A valid state predicate"],
        ["RevokedStaysStoppedAlways", "`Mut # \"M_REVOKE\"`", "`TypeOK` and the property",
         "`NextRevoked`: the grant guard refuses a revoked principal; a renewal needs a live lease",
         "A set the property quantifies over"],
        {"cells": ["SafeAlways", "`Mut = \"none\"`", "—",
                   "One `Spec => []P` step per theorem, then `PTL DEF Safe`", "The conjunction"], "accent": "teal"},
    ]
    y += c.table(X0, y, cols, rows, size=14, accent="teal") + 28

    lw = (W - gap) * 0.55
    rw = W - gap - lw
    l_body = [
        "`MutRenewAllowsAll`, `MutRoleIgnored`, `MutLowerAccepted`: under each, `RenewalAllowed` admits a renewal "
        "that does not refine its predecessor.",
        "`MutFenceIgnoresEpoch`: `EpochOK(p)` holds at any epoch. `MutRungContainsAll`: every live lease is "
        "`Contained`, rung 0 included.",
        "`MutRevokeGrantsAgain`: `ENABLED Grant(p)` for a revoked principal with no live lease and fence room, "
        "proved `BY ExpandENABLED`.",
        "Each names the guard the mutation removes, which is the guard the theorem's hypothesis keeps. **The "
        "counterexample itself stays TLC's**: that a mutation reaches a bad state is existential (ADR-0046 §2).",
    ]
    r_body = [
        "`tools/tlapm --cleanfp --strict Lease_A1_proof.tla`: `--cleanfp` takes nothing from an earlier run; "
        "`--strict` makes a failed obligation a non-zero exit.",
        "`proof-results.sh` prints the results file: the `Modules:` line with `Lease_A1.tla` "
        "(`0b5eac7a7309be2f`) and `Lease_A1_proof.tla` (`6f39c7711252c8de`), the prover binary "
        "(`e150fb793fb28592`, T-0045-31), the assumptions, theorems and lemmas, and \"All 200 obligations "
        "proved\". The file is `d4b39bd7094c38d1`.",
        "**Then certified** (ADR-0046 A1): `proof-cert.sh Lease_A1_proof` reruns it with cvc5 behind `smt-checked` "
        "in place of Z3 and Isabelle checking Zenon. `Lease_A1-proof-cert-results-2026.10.04.txt` "
        "(`a9e59ca0937e3fed`): 121 trivial, 73 SMT with a proof `ethos` accepted, 0 Zenon, 1 Isabelle, 5 LS4. "
        "Certified: 195 rest on normalization or a checked proof, 5 on LS4 (H6).",
        "A proof of the module, not of the reference's grant path (T-0045-28).",
    ]
    hh = max(c.card(0, 0, lw, "5 · One lemma per mutation, saying what it admits", l_body, "teal", size=14,
                    draw=False),
             c.card(0, 0, rw, "6 · Checked by the prover, measured by digest", r_body, "teal", size=14,
                    draw=False))
    c.card(X0, y, lw, "5 · One lemma per mutation, saying what it admits", l_body, "teal", size=14, h=hh)
    c.card(X0 + lw + gap, y, rw, "6 · Checked by the prover, measured by digest", r_body, "teal", size=14, h=hh,
           status="accepted", status_extra="T-0045-31 · ADR-0046 B25, A1 B28")
    y += hh + 56

    # ================================================================== 2 · four shapes
    y += c.heading(X0, y, "2 · The four shapes the inductive invariants took", "teal", 22)
    y += c.para(X0, y, W,
                "The modules were written for mutation testing, so each property was instrumented for TLC to flip, "
                "and that made it local to the guard a mutation removes: the \"Breaks under\" column was in effect "
                "a list of which guard each proof would rest on (proof-method §5). Two forms needed no inductive "
                "invariant of their own: a predicate true in every state (`Rung0NeverContained`), and a property "
                "set once at a commit action and frozen after it (`RulesFloorNV_rev5`, at `Promote`).",
                size=15, color="muted") + 18
    sg = 50
    sw = (W - 3 * sg) / 4
    shapes = [
        ("A flag set at the violating action", [
            "`DenyByAnyOf == ~admittedOverFinding`. `Admit(t)`, guarded by `~Blocked(t)`, sets "
            "`admittedOverFinding' = admittedOverFinding \\/ (Found(t) \\cap W(t) # {})`.",
            "**Inductive by itself.** Under the hypothesis the condition is false at the one action that can set "
            "the flag: a propositional check against that action's guard.",
            "Where: `FloorRouting`, `FloorComposition`'s four flags, `Observers`, the coupling flags in `Coupling` "
            "and `RunCoupling`, `Lease_A1`'s `staleAdmitted`.",
        ]),
        ("An append-only set, and what may be appended", [
            "`acted' = acted \\cup {[act |-> a, kind |-> KindOf[s]]}`, with the auxiliary "
            "`Alphabets == \\A s \\in Seats : lease[s].live => lease[s].alphabet = KindBound(KindOf[s])`.",
            "**One state fact about what the appending action can append**: the guard's precondition, written as "
            "an invariant.",
            "Where: `Seats` and `RunSeats` (the alphabet), `BreakGlass` (`bgDid`; the floor holds of the issued "
            "rules), `NonComposition` (`created` and `retained`; the records NC1 needs were created, and only "
            "admitted effects went via break-glass). `RunConfinement`'s `effects` needs no auxiliary: both "
            "invariants are inductive on their own (116 obligations).",
        ]),
        ("Generation binding: the one that was invented", [
            "`ContainedMeansConfined`: the record `Act` appends depends on state set three actions earlier, at "
            "launch, appraisal and grant.",
            "Six clauses with `TypeOK`: `GuestImg` (the running image is the booted one), `GuestGen` (a live "
            "guest carries the current generation), `LowRungHonest` (below rung 2 the booted image is the asked "
            "one), `PendingBinds` and `LeaseBinds` (an attested appraisal and a lease above rung 0 remember a "
            "generation, and while that guest stands its asked image is the profile and was booted), and the "
            "property.",
            "**Preserved because a relaunch strictly raises the generation**, and `Act` admits only against the "
            "lease's, the check `M_UNBOUND` removes. 502 obligations, every rung at once; the successor "
            "`Confinement_A1_proof`, 503, changes one case split to `Declared <= 1`: rung 0 joins rung 1 under "
            "`LowRungHonest`.",
        ]),
        ("Arithmetic in layers", [
            "`UnreadBounded`: what the Observer has not read stays within `K`.",
            "`Shape` holds under every mutation: `Future` (later rounds are zero), `MarkLeSeq` (the mark is at "
            "most the sequence), `SealedIdle` (an idle round's seal is its sequence). On it, the two layers the "
            "coupling needs: `Past` (earlier marks equal their seals) and `Bound` (`seq - mark[round] <= K`).",
            "**Each clause answers what one action needs to keep the bound.** `RunCoupling` adds `SeqIsEff` and "
            "`PastSeal`. Holds for every `K`, `R` and `MaxRound`: `K < R` is not a premise (ADR-0046 §5).",
        ]),
    ]
    shh = max(c.card(0, 0, sw, t, b, "teal", size=14, draw=False) for t, b in shapes)
    for i, (t, b) in enumerate(shapes):
        c.card(X0 + i * (sw + sg), y, sw, t, b, "teal", size=14, h=shh)
    y += shh + 36

    # what the proofs written since G9 added (proof-method.md §1's five new rows; ToO rev 14 §11.3)
    y += c.heading(X0, y, "What the seven proofs written since G9 added to the four shapes", "teal", 19)
    y += c.para(X0, y, W, "`Emergency`, `Labels`, `ToolList`, `Operators` and `Correlator` on 2026.10.04; the "
                "successors `BreakGlass_A1` and `NonComposition_A1` on 2026.10.05; each is proved and certified (G10 "
                "§3). The method did not change; these are the habits proof-method.md §1 and ToO §11.3 record.", size=15, color="muted") + 14
    nw = (W - 3 * sg) / 4
    news = [
        ("One lemma on the shapes a step can have", [
            "`Labels_proof` (651 obligations, ten invariants): one lemma on the three shapes a step has, with "
            "`Actuate`'s `LET` named part by part; then \"labels cover the truth\", from which the floor's minimum "
            "follows by the forbid that would have fired.",
            "All 216 of its SMT obligations certified at the default timeout (proof-certification.md §10).",
        ]),
        ("An invariant no property names", [
            "`Labels` needed that only an item that exists is in the guest; `Emergency` that every lease's holder is a "
            "person, not only the emergency seat's (ToO §11.3).",
            "`Operators` and `Emergency` state the lease properties over **every lease, not only live ones**: \"every "
            "granted lease has a quorum at its root\", \"no lease is wider than its seating\", since a regrant revives "
            "a lease the stated property is silent about (proof-method.md §1).",
        ]),
        ("An `ENABLED` invariant as a state lemma", [
            "`Operators`' `DenyAlwaysAvailable` and `Correlator`'s `LagNeverGates` are state lemmas, as "
            "`RunCoupling`'s `ConsultNeverCoupled` was.",
            "An `ENABLED` goal may go to Zenon, whose script then has to reconstruct in Isabelle to certify. "
            "`Operators_proof` has two that Isabelle accepted; `Emergency_proof` had one, in a lemma no theorem used, "
            "that it could not check, and the lemma was removed and its fact left to a TLC witness.",
        ]),
        ("A successor can drop an assumption", [
            "`BreakGlass_proof` assumes `\"R7\" \\in Active`. `BreakGlass_A1_proof` (45 obligations) does not: under the "
            "kind's alphabet as decided R7 has nothing to refuse (ADR-0026 A2), so it takes R7 only as a hypothesis "
            "under one mutation, `Mut = \"M_KIND\" => \"R7\" \\in Active`, beside `Mut # \"M_SCOPE\"`.",
            "`NonComposition_A1_proof` (96) proves `NC1` and `NC2` with none of its three mutations on, since each "
            "breaks both; the third, `M3`, is new with the seating: an activation's record kept only while its round "
            "is live.",
        ]),
    ]
    nh = max(c.card(0, 0, nw, t, b, "teal", size=14, draw=False) for t, b in news)
    for i, (t, b) in enumerate(news):
        c.card(X0 + i * (nw + sg), y, nw, t, b, "teal", size=14, h=nh, tint=False)
    y += nh + 56

    # ================================================================== 3 · the sync loop
    y += c.heading(X0, y, "3 · The loop that keeps a proof the proof of its specification", "teal", 22)
    y += c.para(X0, y, W,
                "A proof module extends the module it proves, so the two can drift in exactly one way: the base "
                "module changes. The binding is the `Modules:` line of the results file; the repair is the "
                "successor discipline the corpus already has for modules (proof-method §6).",
                size=15, color="muted") + 30
    lg = 90
    bw = (W - 5 * lg) / 6
    xs = [X0 + i * (bw + lg) for i in range(6)]
    lane1 = [
        ("Base module, frozen by digest", "blue", [
            "`Lease_A1.tla`, cited by ADR-0031. A change is a successor module, never an edit.",
        ]),
        ("Proof module", "teal", [
            "`Lease_A1_proof.tla`: `EXTENDS Lease_A1, TLAPS`, with the hypotheses the base module must not carry.",
        ]),
        ("The prover, T-0045-31", "grey", [
            "`tools/tlapm --cleanfp --strict`; binary `e150fb793fb28592`, not tracked, named in the corpus since "
            "2026.10.03 by `tools/TLAPS-PIN` (version, commit `7824dab`, the digest's first sixteen hex, backends). The "
            "wrapper refuses another binary unless `TLAPM_UNPINNED=1`; `proof-sync.sh` reports a results file citing "
            "another prover. G10 item 73: **discharged**; the full digest is still owed.",
        ]),
        ("Results file, dated, never edited", "teal", [
            "`proof-results.sh`: `Modules:` names the digest of every module in the `EXTENDS` chain as proved, then "
            "the prover's digest and \"All N obligations proved\".",
        ]),
        ("A certified run beside it", "teal", [
            "`proof-cert.sh <M>_proof` reruns the same proof with Z3 replaced by cvc5 behind `smt-checked` and Zenon "
            "checked by Isabelle, and prints `<M>-proof-cert-results-<date>.txt`: every obligation by route, and "
            "\"All N obligations proved…\" or `NOT CERTIFIED: <reason>`.",
            "Run `proof-results.sh` first: faster, and it finds real failures (proof-certification.md §10). **G10 "
            "§5: a proof is certified or its results file says why not.** Route by route: H6.",
        ]),
        ("Cited by digest, so frozen", "blue", [
            "ADR-0046 §4 cites base, proof and results digests, frozen from Batch 25; A1 cites the certified results "
            "files (B28). G9's two are frozen from G9, and the six new modules of G10, their proofs and results files "
            "from G10 (G10 §3).",
        ]),
    ]
    l1h = max(c.card(0, 0, bw, t, b, a, size=14, draw=False) for t, a, b in lane1)
    L1 = y
    for i, (t, a, b) in enumerate(lane1):
        c.card(xs[i], L1, bw, t, b, a, size=14, h=l1h, tint=(i != 4), dash="6 4" if i == 4 else None)
    ay = L1 + 40
    for i, lab in enumerate(["EXTENDS", "checked", "printed", "rerun", "cited"]):
        c.arrow([(xs[i] + bw + 6, ay), (xs[i + 1] - 6, ay)], "teal", label=lab, lsize=12.5)

    L2 = L1 + l1h + 100
    sync_w = xs[4] + bw - xs[3]
    succ_w = xs[1] + bw - xs[0]
    lane2 = [
        (xs[3], sync_w, "`proof-sync.sh`: is every proof in step?", "teal", [
            "For each `<M>_proof.tla`, the newest results file's digests against the tree: **IN SYNC**, or "
            "**STALE** naming the module that moved, or **MISSING RESULTS**; and every results file's prover against "
            "`tools/TLAPS-PIN`.",
            "Then every base module without a proof, with the reason recorded: `Mechanism` (a trace replay), "
            "`ConfinementRefinement` (predicates over replayed trace states), `Lease` and `RulesFloorNV` "
            "(superseded), `RulesFloorBase` (definitions). Exits 1 on a stale proof, a missing results file, a "
            "prover other than the pin's, or a proofless module with no reason.",
        ]),
        (xs[2], bw, "`--run`: did the drift break the proof?", "red", [
            "Re-checks each stale proof. A changed guard fails at its action's step, a changed property at `Init` "
            "or `Next`, a changed mutation at a hypothesis that no longer discharges.",
        ]),
        (xs[0], succ_w, "A successor, never an edit", "teal", [
            "Write the successor module, **suffix `_A1`**, its predecessor cited by digest and not edited (G10 §5): "
            "`Lease` to `Lease_A1`, `Confinement` to `Confinement_A1`, and since 2026.10.05 `BreakGlass` and "
            "`NonComposition` to `BreakGlass_A1` and `NonComposition_A1`, where the predecessors model X1 (ADR-0052 "
            "R5). Copy the proof to `<Successor>_proof.tla`, point its `EXTENDS` at the successor, and re-prove.",
            "Generate its results file with `proof-results.sh`, then its certified run; commit them with the "
            "successor and its TLC results. The record that cites the successor cites its proof by digest; the frozen "
            "pair stays as it was.",
            "`Confinement_A1`'s proof needed one case split changed, `Declared = 1` to `Declared <= 1`, not unchanged "
            "as the drafter first wrote (G9 §3, finding 5).",
        ]),
        (xs[5], bw, "What `proof-sync.sh` does not read", "grey", [
            "It reads the `-proof-results-` files only. A certified results file binds itself to its modules the same "
            "way, by its `Modules:` line, and nothing compares that line with the tree.",
            "Nothing here reports a change to the wrapper, the solver or the checker: their digests are in each "
            "certified file's header, and a rerun that differs is a different certification (proof-certification.md "
            "§5).",
        ]),
    ]
    l2h = max(c.card(0, 0, w_, t, b, a, size=14, draw=False) for _, w_, t, a, b in lane2)
    for x, w_, t, a, b in lane2:
        c.card(x, L2, w_, t, b, a, size=14, h=l2h, tint=a != "grey", dash="6 4" if a == "grey" else None)
    # results file down into the check
    dx = xs[3] + bw / 2
    c.arrow([(dx, L1 + l1h + 6), (dx, L2 - 6)], "teal", label="its digests", lpos=0.5)
    by = L2 + 40
    c.arrow([(xs[3] - 6, by), (xs[2] + bw + 6, by)], "red", label="STALE")
    c.arrow([(xs[2] - 6, by), (xs[1] + bw + 6, by)], "red", label="repair")
    for i, lab in [(0, "new digest"), (1, "successor proof")]:
        ux = xs[i] + bw / 2
        c.arrow([(ux, L2 - 6), (ux, L1 + l1h + 6)], "teal", label=lab, lpos=0.5)
    y = L2 + l2h + 50

    # side cards
    tg = 50
    tw3 = (W - 2 * tg) / 3
    side = [
        ("The proof's own non-vacuity check", "teal", None, "", [
            "Copy the proof module to scratch, flip one hypothesis to the mutation it excludes, and run the prover. "
            "**It must reject the proof, at the guard the mutation removes.**",
            "`Anchor_proof` with `Mut = \"M_FLOOR\"`: 1 of 40 obligations fails, at `Floor(r)` in the `Issue` case "
            "(ADR-0046 B25). A proof that survives the flip is proving the wrong thing.",
            "A mutated proof is not an artefact: it leaves no file (G8 §5).",
        ]),
        ("Why the proofs are not merged into the modules", "teal", None, "", [
            "A base module is frozen by digest; adding a proof would make it a successor of itself.",
            "TLC runs the base module through `tools/tla2tools.jar` without the prover's library; a merged module "
            "would carry `EXTENDS TLAPS` into every TLC run.",
            "The proof carries hypotheses (`Mut # \"M_X\"`, `\"R7\" \\in Active`) that the module must not: the "
            "module is written so TLC can flip each mutation. Each reason is sufficient (proof-method §6).",
        ]),
        ("A live module in the chain: `RulesFloorBase.tla`", "teal", "accepted", "ADR-0046 E1 · Batch 26", [
            "`Anchor`, `BreakGlass` and now `BreakGlass_A1` extend it. It is the live definition of the floor by its "
            "own header; ADR-0046 §4 called it frozen, and erratum E1 (Batch 26) corrected that.",
            "The results files record the digest proved (`cf2351de2b39cccf`, unchanged at G10), so a change shows as "
            "**STALE** for each proof whose `Modules:` line names it, and each needs a successor proof.",
            "**It is behind the records**: it still carries `bgScope` and R6's bound of two, where ADR-0026 A2 "
            "(provisional, Batch 34) makes the count one (G10 §2.1; item 90).",
        ]),
    ]
    sh = max(c.card(0, 0, tw3, t, b, a, status=s, status_extra=e, size=14, draw=False) for t, a, s, e, b in side)
    for i, (t, a, s, e, b) in enumerate(side):
        c.card(X0 + i * (tw3 + tg), y, tw3, t, b, a, status=s, status_extra=e, size=14, h=sh)
    y += sh + 56

    # ================================================================== 4 · the same loop, in Lean
    y += c.heading(X0, y, "4 · The same loop, for a Lean re-encoding (ADR-0053, Proposed)", "amber", 22)
    y += c.para(X0, y, W,
                "A re-encoding does not extend its module: it is a second statement of it, in Lean, beside it under "
                "`spec/lean/`, and the base module does not know it exists. So it drifts the way a proof does, when "
                "the base module changes, and one more way a proof cannot: the Lean can say something other than the "
                "module, which is read and not checked. Every row below is the TLAPS loop's, matched (proof-method "
                "§5b, §6).", size=15, color="muted") + 18
    tw4 = W * 0.66
    t4 = c.table(X0, y, [("", tw4 * 0.17, {"bold": True}), ("A TLAPS proof", tw4 * 0.38),
                         ("A Lean re-encoding (ADR-0053, Proposed)", tw4 * 0.45)], [
        ["Relation to the module", "`EXTENDS` it: the proof is of the frozen text itself",
         "Restates it beside the text: the theorems are of the encoding, read against the module"],
        ["What binds the result to the text", "The `Modules:` line: every module of the `EXTENDS` chain by digest",
         "The `Transcribes:` line: every TLA+ module encoded, by repository path and digest; the `Sources:` line: "
         "every Lean file"],
        ["The driver", "`spec/proof-results.sh <M>_proof`", "`spec/lean/results.sh`, through `tools/lean-report.sh`: a "
                                                            "clean build, `#print axioms` sorted, and the replay"],
        ["What says \"proved\"", "\"All N obligations proved\" (T-0045-31)", "\"Build completed\" and "
         "`leanchecker --fresh`: every constant replayed through the kernel in a fresh environment (T-0045-37, "
         "proposed)"],
        ["The sync check", "`spec/proof-sync.sh`: `IN SYNC`, `STALE`, `MISSING RESULTS`",
         "`tools/lean-sync.sh`: the same three, for `spec/lean`, `mechanism/lean` and `floor/lean`"],
        ["The pin", "`tools/TLAPS-PIN`; `tools/tlapm` refuses another binary", "`tools/LEAN-PIN`; `lean-sync.sh` refuses "
                                                                               "a results file naming another kernel"],
        ["The install", "`tools/install-tlaps.sh`, 1.9 GB, not tracked", "`tools/install-lean.sh` through elan, about "
                                                                         "2 GB, not tracked"],
        ["When the module changes", "A successor module and a successor proof; the frozen pair stays",
         "A successor encoding, a new Lean file; the old one stays as the encoding of the frozen module"],
        ["Frozen when", "Cited by digest in a ratified record (ADR-0046 §4)", "With its base module, on ADR-0053's "
                                                                              "ratification; until then cited by none"],
        ["Its non-vacuity check", "Flip one hypothesis in a scratch copy: the prover must reject the proof at the guard",
         "Mutate one definition in a scratch copy: the build must fail in the theorem the mutation breaks (eighteen "
         "for `spec/lean`, 2026.10.05)"],
        ["Not read by the sync", "The certified results file's `Modules:` line", "Whether the encoding says what the "
                                                                              "module says: that is the reading"],
    ], size=13.5, accent="amber")
    c.card(X0 + tw4 + 40, y, W - tw4 - 40, "Why keep both", [
        "**They fail in different places.** The TLAPS proof trusts LS4 for the temporal step and the prover's front "
        "end; the Lean proof trusts the encoding. A theorem proved by both is wrong only if both fail.",
        "**The Lean proof is not a successor of the TLAPS proof**, and neither replaces the other: the TLA+ module, "
        "its proof and its certified run stay canonical (ADR-0053 §1).",
        "**The same strengthenings carried over.** Every Lean proof reuses the inductive invariant its TLAPS proof "
        "found, which is why thirteen modules took a day; what TLAPS proves as `TypeOK`, Lean's types carry.",
        "**One more drift than a proof has**: an encoding can be wrong where a proof extending the text cannot. The "
        "header of each Lean file names where a reading was chosen.",
    ], accent="amber", status="proposed", status_extra="ADR-0053", size=14)
    y += t4
    return c
