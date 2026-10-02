# TLAPS proof method

**2026.10.02** · the method behind the `spec/*_proof.tla` modules and `spec/proof-results.sh` · DRAFT, revised with the proofs it describes

**What this is.** How the thirteen proof modules written on 2026.10.02 were made, what each claims and does not claim,
the patterns they share, the prover's habits that cost time, and a dated assessment of why they were cheap and where
that stops. It is a method note, not a record. Nothing here is ratified, no record cites a proof yet, and the
TLC-versus-TLAPS declaration (MAP 2.3, open in every checkpoint's §8) remains the custodian's to make. A later
revision adds a dated assessment under §5 rather than editing the one there.

**What this is not.** A claim that the properties hold of any deployment. A proof is bounded by its assumptions and
its prover where a TLC row is bounded by its constants; the premises in `spec/theorem-premise-binding.md` still apply
to every property, and the prover (tlapm, Z3, Zenon, Isabelle, LS4) is a trusted-base item the corpus has not yet
declared, in the place T-0045-29 declares TLC.

## 1. What a proof module claims

- **It extends a frozen module and never edits it.** A module cited by digest in an accepted record is frozen
  (`spec/README.md`), so `Anchor_proof.tla` extends `Anchor.tla` and restates nothing from it. Where a base module
  states a fact as an unnamed `ASSUME`, the proof module proves it as a named lemma (`GenesisEntries` in
  `Anchor_proof.tla` and `BreakGlass_proof.tla`), because the prover does not use an unnamed module assumption.
- **It proves the invariants the module states, as `Spec => []P`,** for every value of the constants that the
  module's named assumptions admit. The assumptions are the constraints the run scripts supplied per row: the floor
  in force is a subset of the entries the floor defines, the epoch bound is a natural, R7 is in force, the declared
  rung is in 0..3. A bound that only cuts the state space (MaxEpoch, MaxFence, MaxIdx, MaxGen) needs no assumption,
  so the theorem holds for every value of it, where TLC ran one value.
- **Each theorem takes as hypothesis only the mutations that break it,** written `ASSUME Mut # "M_X"`. A combined
  `SafeAlways` takes `Mut = "none"`. The hypotheses restate the "Breaks under" column of
  `spec/theorem-premise-binding.md`, and writing them produced four corrections to it: RunSeats' `M_OBSEMIT` breaks
  none of that module's three invariants (it narrows an observer's bound, and the invariants are upper bounds);
  Confinement's binding of a lease to a guest is enforced by Act's generation check, not by `SameGuest` at grant,
  which the proof never uses; and in FloorComposition, `M_OVERRIDE` breaks `FloorErrorIsDeny` and
  `BundleRefusalHonored` as well as `AdmitImpliesFloorPermit`, and `M_ERR` breaks `AdmitImpliesFloorPermit` as well
  as `FloorErrorIsDeny`, rows TLC did not run; and RunCoupling's `SealCountsEffects` breaks under `M_EMITSEQ`, not
  `M_ROUNDS`, which the table names and which never touches a seal. The last is a transcription error: the results
  file's own rows (`rc-emitseq-seal`, `rc-rounds-seal`) say what the proof says.
- **Mutations and reachability witnesses stay with TLC.** A counterexample and a witness are behaviours, and the
  prover proves universal statements. Each proof module instead carries one lemma per mutation stating what the
  mutation admits (the guard it removes): `MutAdmitsAll`, `MutAdmitsAuthority`, `MutRevokeGrantsAgain` and the
  like. The results file names the TLC results file the counterexamples live in.
- **The results file is the evidence.** `proof-results.sh <Module>_proof` prints the digest of every module in the
  EXTENDS chain and of the prover binary, the assumptions, the theorems and lemmas by name, and the prover's own
  obligation count, and exits non-zero if any obligation fails. It is dated and never edited, like a TLC results file.

| Proof module | Obligations | Invariants proved | Inductive invariant used |
|---|---|---|---|
| `Anchor_proof.tla` | 40 | 2 | the property itself |
| `BreakGlass_proof.tla` | 37 | 1 | the floor holding of the issued rules, plus the property |
| `FloorRouting_proof.tla` | 36 | 2 | the property itself |
| `Seats_proof.tla` | 110 | 2 | a type invariant, plus "a live alphabet is the seat's kind bound" |
| `Observers_proof.tla` | 65 | 2 | the property itself |
| `RunSeats_proof.tla` | 147 | 3 | a type invariant, plus "a live alphabet is the granted one", under every mutation |
| `Lease_A1_proof.tla` | 200 | 4 | a type invariant; one property is valid in every state and needs no induction |
| `Confinement_proof.tla` | 502 | 4 | a type invariant, plus six generation-binding clauses (§3) |
| `NonComposition_proof.tla` | 58 | 2 | NC2, plus "the records NC1 needs were created" and "only admitted effects went via break-glass" |
| `FloorComposition_proof.tla` | 171 | 5 | the flags themselves; EnvelopeHolds adds the type invariant and "the floor's inputs are the truth" |
| `Coupling_proof.tla` | 320 | 3 | a shape invariant under every mutation (future rounds zero, mark at most the sequence, an idle round's seal is its sequence), plus "past marks equal seals" and "the backlog is at most K" |
| `RunCoupling_proof.tla` | 469 | 5 | the Coupling shape with effect seals, plus "the sequence counts effects" and "past seals agree"; the `ENABLED` invariant is a state lemma |
| `RulesFloorNV_rev5_proof.tla` | 262 | 6 | "the issued rules are in the rule space and satisfy the floor"; each property is established at Promote and frozen, since Issue and Vote need `~promoted` |

## 2. Process, per module

1. **Read the module and its results file.** List the invariants, the mutations and the witnesses. For each
   invariant, find the guard its mutation removes; that guard is what the inductive step will rest on.
2. **Decide the inductive invariant before writing.** A flag that an action sets when it would violate the
   property is inductive by itself. An append-only set of records needs one state fact about what gets appended.
   Anything else has to be constructed (§3, generation binding). Decide the hypothesis per theorem from the
   mutations that touch that guard.
3. **Write the type invariant first** as functions from the principal set to record sets, with `NoLease` and its
   kin proved members. Prove it under every mutation, as its own lemma; every later lemma cites it.
4. **One Next lemma per invariant group,** with the hypotheses in its `ASSUME`, and one step per action: the
   `UNCHANGED vars` case, each top-level disjunct of `Next`, each `\E p` disjunct as `ASSUME NEW p, Action(p)`.
   Where an action is an `IF` or `CASE`, pick its outcomes as a disjunction in one step and let the backend split.
5. **The theorem** is three lines: the Next lemma restated as `Inv /\ [Next]_vars => Inv'`, the Init lemma, and
   `PTL DEF Spec`. When the invariant is a conjunction with the property, add `Inv => P`.
6. **`SafeAlways`** cites each theorem in an explicit step of the form `Spec => []P` before the PTL step; the
   backend cannot discharge a theorem's `Mut` hypothesis inside PTL.
7. **Mutation lemmas** last, one per mutation, stating what the mutation admits in the vocabulary of the module.
   An `ENABLED` statement proved `BY ExpandENABLED` is the strongest form when the mutation enables an action.
8. **Check** with `../tools/tlapm --cleanfp --strict <Module>_proof.tla` from `spec/`. `--cleanfp` discards
   fingerprints so nothing is taken from an earlier run; `--strict` makes a failed obligation a non-zero exit.
   Fix until the count reads "All N obligations proved".
9. **Check the proof's own non-vacuity.** Copy the module to scratch, flip one hypothesis to the mutation it
   excludes, and run again. The prover must report failed obligations. A proof that survives this is proving the
   wrong thing. Every module above was checked this way; the failing count is in the session, not in the corpus,
   because a mutated proof is not an artefact.
10. **Generate the results file** and add the row to `spec/README.md`. Commit the module, its results file and
    the README together.

## 3. Patterns

- **Flag invariants.** `~admittedUnlive`, `~wideNoIssue`, `~admittedOverFinding`. The action sets the flag to
  `flag \/ cond`; the proof shows `cond` is false under the hypothesis at that one action. No auxiliary invariant.
- **Append-only record sets.** `acted`, `bgDid`, `findings`. The property quantifies over the set; the auxiliary
  invariant says what the appending action can append (an alphabet, a floor entry, a reach). The auxiliary is the
  guard's precondition, written as a state fact.
- **Valid state predicates.** `Rung0NeverContained` is true of every state under its hypothesis, by definition of
  `Contained`. Prove it as a state lemma; PTL lifts a cited state-level fact to `[]`.
- **A type invariant proved once, under every mutation,** and cited by every lemma. Its job is to make `EXCEPT`
  on one principal leave the others alone; without the function's domain in scope the backend cannot say so.
- **Constant operators that carry the mutation.** RunSeats' `ByKind(s)` and `ByDomain(s)` fold the `IF Mut = ...`
  into a definition, so the auxiliary invariant "a live alphabet equals the granted one" holds under every mutation
  and the three properties split cleanly on top of it, each under its own hypothesis.
- **Generation binding** (Confinement). When the record an action appends depends on state set several actions
  earlier, the invariant must carry that history forward conditionally: a live guest carries the current
  generation; an appraisal and a lease remember a generation no later than the current one; while the guest with
  that generation stands, the asked image is the profile and was booted; the running image is the booted one. An
  act admitted against the lease's generation then runs the image the profile names. Six clauses, each a
  conditional on "same generation", each preserved because a relaunch strictly raises the generation.
- **Weakest hypothesis per theorem.** It costs nothing extra, it documents sensitivity, and it has already
  corrected the premise table three times. In `RulesFloorNV_rev5_proof.tla` the hypotheses are floor entries in
  force rather than mutations, and P9's is a formula: R2 and either R1 or R9, which is the premise table's "binds
  only with R1 relaxed" made exact.
- **Established and frozen.** When every action after a commit point needs the commit flag false (Issue and Vote
  need `~promoted`), a property of the committed values is proved once at the commit action and carried by a
  lemma that every step either is the commit or leaves the values alone.
- **Arithmetic invariants in layers.** Coupling's unread bound needed five auxiliary clauses, found by asking what
  each action needs of the state to keep the bound: future rounds untouched for the grant, the mark below the
  sequence for the heartbeat, the idle seal equal to the sequence and past marks equal to seals for the next grant.
  The clauses that hold under every mutation (`Shape`) are proved once; the two that need the coupling sit on top.
  RunCoupling adds one layer (the sequence counts effects) and reuses the rest.
- **ENABLED as an invariant.** `ConsultNeverCoupled` is `(tLive /\ acts < R) => ENABLED Consult`. Under its
  hypothesis it holds in every state, so it is a state lemma `BY ExpandENABLED` and PTL lifts it; no induction.
- **A module's unnamed ASSUMEs as theorems.** TLC evaluates an `ASSUME`; the prover can prove it. The three in
  `RulesFloorNV_rev5.tla`, that genesis satisfies the floor and that every entry is independently droppable, are
  lemmas with explicit witness records. The witnesses are the "why dropping must fail" lemmas for that module.

## 4. Prover habits that cost time

- An unnamed module-level `ASSUME` is not used unless cited; restate it as a lemma proved from definitions.
- A bounded quantifier or `PICK` whose second bound depends on the first variable, `\A s \in S, a \in F(s)`, is
  not TLA+. Nest them. The parser reports it as an unknown operator.
- A combined theorem cannot cite theorems that carry a `Mut` hypothesis directly inside a PTL step. Add one
  explicit `Spec => []P` step per theorem first.
- The `UNCHANGED vars` case needs the primed type invariant in scope and the constant operators in `DEF`, or the
  prime does not distribute through them.
- A step about `lease'[q]` for `q # p` after an `EXCEPT` needs the type invariant cited as a fact, not only in
  `DEF`; the domain has to be in the hypotheses.
- A step that bundles several primed invariants can fail where each alone proves. Split it.
- Z3 handles string-literal distinctness, `CASE`, records, `IF`, set difference and small arithmetic without
  guidance. It carries `Cardinality(S)` as a term, but to chain two inequalities through it the term must be
  known to be a natural: `FS_CardinalityType` after `FS_Subset` from a finite superset, and a literal set is
  finite `BY FS_EmptySet, FS_AddElement DEF` its name. That was the only FiniteSetTheorems use in
  `RulesFloorNV_rev5`.
- An index into a function over `1..MaxRound` needs `DEF Rounds` and the Nat assumptions in scope at every step
  that reads `mark[round]`; omitting them was the single cause of sixteen failures across Coupling and RunCoupling.
  Chaining inequalities through such a value needs an explicit "`mark[round] \in Nat`" step.
- A `WITNESS` step takes no `DEF`, so it cannot show a record is in a record set. Use `DEFINE w == ...`, prove
  `w \in S` and the property as two steps, and let the QED find the witness. `ExpandENABLED` proved an `ENABLED` goal over seven variables at the first attempt. A Zenon failure
  line is noise when the obligation count says proved; only the final count and the exit status matter.
- Cost scales with actions times invariant clauses, not with reasoning: Confinement's 502 obligations prove in
  about eleven seconds.

## 5. Assessment, 2026.10.02: why these were cheap, and where that stops

The ten modules took one session. Four causes, in descending weight, and one caveat.

**Locality, by way of monotone ghost variables.** The modules were written for mutation testing, and that style
instruments each property so TLC can flip it: a write-once flag set at the action that would violate it, or an
append-only record set. A flag invariant is inductive by itself exactly when the flag's condition is false at that
one action under the hypothesis, a propositional check against the guard. An append-only set needs one state fact
about what is appended. So the inductive invariant is almost always the guard's precondition as a state fact, and
the "Breaks under" column was in effect a list of which guard each proof would rest on. Monotonicity is the
mechanism; locality is why it helps.

**No liveness.** Every module is `Init /\ [][Next]_vars` without fairness and every property is an invariant,
which puts every theorem on the one well-worn path: Init implies the invariant, the invariant and a step imply the
primed invariant, PTL. Nothing needed WF1, a variant, or induction over naturals. The only `ENABLED` goal was a
mutation lemma.

**Finite string domains.** Two principals, three or four seats, kinds as record literals. Z3 settles these by
enumeration. No invariant proved so far involves sequences, recursion or `Cardinality`, the constructs the prover
is weak on.

**Shallow actions.** A guard, one `EXCEPT`, `UNCHANGED` for the rest; no `INSTANCE`, no refinement mapping.
Confinement's thirteen variables were mostly `UNCHANGED` bookkeeping.

**The caveat.** The hard half of the work was done or excluded. TLC had confirmed every property at small
constants, so no conjecture turned out false, which is where proof effort normally goes. The prover proves universal
statements only, and the corpus's genuinely hard questions are existential: that a mutation reaches a bad state,
that a witness is reachable. Those stayed with TLC by design, so the division of labour itself removed the
difficult part.

**Where it stopped being easy.** Confinement's `ContainedMeansConfined` is not flag-shaped: the record appended at
Act depends on state established three actions earlier, at launch, appraisal and grant, and the generation-binding
invariant had to be invented. `Coupling` and `RunCoupling` were the other place: their unread bounds are
arithmetic invariants over counters and marks (`seq - mark[round] <= K`, marks never exceeding seals, the sealed
round equal to the counter while idle) that had to be found rather than read off a guard; the invariant sketched
in the first assessment held as sketched, and the remaining cost was the prover's need to see the index domain at
every step. `RunCoupling`'s `ENABLED` invariant was a state lemma. `RulesFloorNV_rev5` was expected to need cardinality lemmas and needed one fact: `PromotionEnabled` states the
cardinalities the properties compare, so the proofs carry them as terms, and only the threshold case had to know
the term is a natural.
Every module the first assessment listed is now proved except `Mechanism`. `NonComposition` and
`FloorComposition` were flag-shaped and cheap, as expected; NonComposition's one surprise was
a missing clause, that only admitted effects are recorded as via break-glass, which the prover found and TLC could
not have. `Mechanism` is not in this class:
it is a trace replay over a concrete trace constant, and the meaningful target is a refinement from it to the
small modules, which is the gap T-0045-28 declares.

## 6. Open, for the custodian

- The TLC-versus-TLAPS declaration (MAP 2.3) and the checkpoints' §8 wording.
- A trusted-base row for the prover and its backends, in the place T-0045-29 holds TLC, and whether the premise
  table's rows for proved properties cite it.
- Whether and where a record cites a proof module by digest, which would freeze it.
- The three corrections to the "Breaks under" column in §1.
