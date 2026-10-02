"""H5 — Proof anatomy: how a proof module is built, the four shapes its inductive invariant took, and the loop that
keeps each proof the proof of its specification. The mechanism only: which modules are proved, and their counts,
are H3's; each property's hypotheses are G3's "Breaks under" column."""
from lib import Canvas

ID, SLUG = "H5", "proof-anatomy"


def build():
    c = Canvas(ID, "How a proof is built and kept in step",
               "Thirteen of the fourteen modules under `spec/` have a **proof module** (ADR-0046, Batch 25). This "
               "diagram is the mechanism, not the inventory: one proof module part by part, the four shapes its "
               "inductive invariants took, and the loop that keeps each proof the proof of its specification. TLC "
               "**checks** the mutations and witnesses, which are existential claims; the prover **proves** the "
               "invariants, which are universal, under named hypotheses (ADR-0046 §1). Neither is a claim about the "
               "running reference (T-0045-28). Which modules are proved, with their counts, is H3; each property's "
               "hypotheses are G3's \"Breaks under\" column.",
               3200, "spec/proof-method.md §2, §3, §5, §6; spec/README.md, practice items 6 to 8; "
                     "spec/Lease_A1_proof.tla (6f39c7711252c8de) and spec/Lease_A1-proof-results-2026.10.02.txt "
                     "(d4b39bd7094c38d1) over spec/Lease_A1.tla (0b5eac7a7309be2f); spec/Observers_proof.tla, "
                     "spec/Seats_proof.tla, spec/Confinement_proof.tla, spec/Coupling_proof.tla, "
                     "spec/RunCoupling_proof.tla, spec/Anchor_proof.tla; spec/proof-results.sh; spec/proof-sync.sh; "
                     "tools/tlapm; ADR-0046 §1 to §5, §7, R2, B25 and E1 (Batch 26); ADR-0045 T-0045-28, T-0045-31; "
                     "spec/RulesFloorBase.tla; ADR-0026 A1 note; G8 §2.9, §3, §5, §7 items 73, 74")
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
            "`Active \\subseteq AllEntries` in `Anchor`, `Declared \\in 0..3` in `Confinement`. `Lease_A1` needs "
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
        "A proof of the module, not of the reference's grant path (T-0045-28).",
    ]
    hh = max(c.card(0, 0, lw, "5 · One lemma per mutation, saying what it admits", l_body, "teal", size=14,
                    draw=False),
             c.card(0, 0, rw, "6 · Checked by the prover, measured by digest", r_body, "teal", size=14,
                    draw=False))
    c.card(X0, y, lw, "5 · One lemma per mutation, saying what it admits", l_body, "teal", size=14, h=hh)
    c.card(X0 + lw + gap, y, rw, "6 · Checked by the prover, measured by digest", r_body, "teal", size=14, h=hh,
           status="accepted", status_extra="T-0045-31 · ADR-0046 B25")
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
            "admitted effects went via break-glass).",
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
            "lease's, the check `M_UNBOUND` removes. 502 obligations, every rung at once.",
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
    y += shh + 56

    # ================================================================== 3 · the sync loop
    y += c.heading(X0, y, "3 · The loop that keeps a proof the proof of its specification", "teal", 22)
    y += c.para(X0, y, W,
                "A proof module extends the module it proves, so the two can drift in exactly one way: the base "
                "module changes. The binding is the `Modules:` line of the results file; the repair is the "
                "successor discipline the corpus already has for modules (proof-method §6).",
                size=15, color="muted") + 30
    lg = 120
    bw = (W - 4 * lg) / 5
    xs = [X0 + i * (bw + lg) for i in range(5)]
    lane1 = [
        ("Base module, frozen by digest", "blue", [
            "`Lease_A1.tla`, cited by ADR-0031. A change is a successor module, never an edit.",
        ]),
        ("Proof module", "teal", [
            "`Lease_A1_proof.tla`: `EXTENDS Lease_A1, TLAPS`, with the hypotheses the base module must not carry.",
        ]),
        ("The prover, T-0045-31", "grey", [
            "`tools/tlapm --cleanfp --strict`; binary `e150fb793fb28592`, not tracked (G8 item 73). Its SMT proofs "
            "are not rechecked by Isabelle (item 74).",
        ]),
        ("Results file, dated, never edited", "teal", [
            "`Modules:` names the digest of every module in the `EXTENDS` chain as proved, then the prover's "
            "digest and \"All N obligations proved\".",
        ]),
        ("Cited by digest, so frozen", "blue", [
            "ADR-0046 §4 cites base, proof and results digests; the proof and its results file are frozen from "
            "Batch 25.",
        ]),
    ]
    l1h = max(c.card(0, 0, bw, t, b, a, size=14, draw=False) for t, a, b in lane1)
    L1 = y
    for i, (t, a, b) in enumerate(lane1):
        c.card(xs[i], L1, bw, t, b, a, size=14, h=l1h)
    ay = L1 + 40
    for i, lab in enumerate(["EXTENDS", "checked", "printed", "cited"]):
        c.arrow([(xs[i] + bw + 6, ay), (xs[i + 1] - 6, ay)], "teal", label=lab, lsize=12.5)

    L2 = L1 + l1h + 100
    sync_w = xs[4] + bw - xs[3]
    succ_w = xs[1] + bw - xs[0]
    lane2 = [
        (xs[3], sync_w, "`proof-sync.sh`: is every proof in step?", "teal", [
            "For each `<M>_proof.tla`, the newest results file's digests against the tree: **IN SYNC**, or "
            "**STALE** naming the module that moved, or **MISSING RESULTS**.",
            "Then every base module without a proof, with the reason recorded: `Mechanism` (a trace replay), "
            "`Lease` and `RulesFloorNV` (superseded), `RulesFloorBase` (definitions). Exits 1 on a stale proof, a "
            "missing results file, or a proofless module with no reason.",
        ]),
        (xs[2], bw, "`--run`: did the drift break the proof?", "red", [
            "Re-checks each stale proof. A changed guard fails at its action's step, a changed property at `Init` "
            "or `Next`, a changed mutation at a hypothesis that no longer discharges.",
        ]),
        (xs[0], succ_w, "A successor, never an edit", "teal", [
            "Write the successor module (`Lease.tla` to `Lease_A1.tla`), copy the proof to "
            "`<Successor>_proof.tla`, point its `EXTENDS` at the successor, and re-prove.",
            "Generate its results file with `proof-results.sh`; commit the successor, its TLC results, the "
            "successor proof and its results together. The record that cites the successor cites its proof by "
            "digest. The frozen pair stays as it was.",
        ]),
    ]
    l2h = max(c.card(0, 0, w_, t, b, a, size=14, draw=False) for _, w_, t, a, b in lane2)
    for x, w_, t, a, b in lane2:
        c.card(x, L2, w_, t, b, a, size=14, h=l2h)
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
            "`Anchor` and `BreakGlass` extend it. It is the live definition of the floor by its own header, and "
            "ADR-0026's A1 note says it changes with R8.",
            "The results files record the digest proved (`cf2351de2b39cccf`), so a change shows as **STALE** for "
            "both proofs and each needs a successor proof.",
            "ADR-0046 §4 called it frozen; erratum E1, ratified in Batch 26, corrected that.",
        ]),
    ]
    sh = max(c.card(0, 0, tw3, t, b, a, status=s, status_extra=e, size=14, draw=False) for t, a, s, e, b in side)
    for i, (t, a, s, e, b) in enumerate(side):
        c.card(X0 + i * (tw3 + tg), y, tw3, t, b, a, status=s, status_extra=e, size=14, h=sh)
    return c
