# Prover habits: tlapm, its backends, and what costs time

Each entry: the symptom, the cause, the fix. Then the rules for steps that
survive checked backends, and the two known unsound cases in the prover's
translation with the writing rules that avoid them.

## Contents

- [Running the prover](#running-the-prover)
- [Parse and front-end habits](#parse-and-front-end-habits)
- [Steps that fail for want of scope](#steps-that-fail-for-want-of-scope)
- [Temporal steps](#temporal-steps)
- [What the SMT backend handles alone](#what-the-smt-backend-handles-alone)
- [Steps that certify under checked backends](#steps-that-certify-under-checked-backends)
- [Two unsound cases in the translation](#two-unsound-cases-in-the-translation)
- [Cost model](#cost-model)

## Running the prover

```sh
tlapm --cleanfp --strict <Module>_proof.tla
```

- `--cleanfp` discards the fingerprint cache so no obligation is taken as
  proved from an earlier run. Without it, a proof edited to be wrong can
  still report "proved" from a stale fingerprint.
- `--strict` makes a failed obligation a non-zero exit, which is what a
  results-file generator and a sync script need.
- Point `--cache-dir` at a temp directory and remove it after; nothing is
  written beside the module.
- **Read only the final count and the exit status.** tlapm tries backends
  in turn and prints each failure; a Zenon failure line is noise when the
  obligation count says proved.
- **Pin the binary.** A pin file names the version, commit and binary
  digest; the wrapper refuses a binary that does not match unless an
  explicit override is set; every results file prints the digest. A
  pre-release tag can be rebuilt upstream under the same name, so the tag
  is not the pin.
- `--toolbox 0 0` prints each obligation with the backend that closed it;
  use it to find which route a step takes when certification is in
  question.

## Parse and front-end habits

- **An unnamed module-level `ASSUME` is not used unless cited.** Restate it
  in the proof module as a named `ASSUME` or prove it as a lemma.
- **A bounded quantifier whose second bound depends on the first variable
  is not TLA+**: `\A s \in S, a \in F(s)` is reported as an unknown
  operator. Nest the quantifiers.
- **tlapm accepts a binder that shadows a constant and SANY refuses it.**
  Rename; a module the model checker cannot parse has no TLC rows.
- **The `UNCHANGED vars` case needs the primed type invariant in scope and
  the constant operators in `DEF`**, or the prime does not distribute
  through them.

## Steps that fail for want of scope

- **`f'[q]` for `q # p` after `[f EXCEPT ![p] = ...]`** needs the type
  invariant cited as a fact, not only in `DEF`; the function's domain must
  be among the hypotheses.
- **Any step that reads `mark[round]`** needs `DEF Rounds` (the index
  domain) and the `Nat` assumptions on the constants. This was the single
  cause of sixteen failures across two arithmetic modules.
- **Chaining inequalities through an indexed value** needs an explicit
  `mark[round] \in Nat` step first.
- **A step that bundles several primed clauses** can fail where each alone
  proves. Split by clause.
- **A `WITNESS` step takes no `DEF`**, so it cannot show a record is in a
  record set. `DEFINE w == ...`, prove `w \in S` and the property as two
  steps, and let QED find the witness.

## Temporal steps

- **A combined theorem cannot cite theorems that carry a `Mut` hypothesis
  inside a `PTL` step.** Add one explicit `Spec => []P` step per theorem
  before the `PTL` step.
- **`ExpandENABLED`** proves an `ENABLED` goal over seven variables at the
  first attempt, given the action's definition in `DEF`. Prove the
  `ENABLED` fact in the step that states it; do not carry it by name across
  a quantifier (see the unsound cases).
- **A `PTL` step may be discharged by LS4 and by nothing else.** It is the
  one route no checker confirms; keep it to the fixed shape "holds
  initially, every step keeps it, so always".

## What the SMT backend handles alone

Without guidance: string-literal distinctness, `CASE`, records, `IF`, set
difference, small arithmetic, `EXCEPT` on functions with the domain in
scope.

With one fact: `Cardinality(S)` is carried as a term; to chain two
inequalities through it the term must be known to be a natural
(`FS_CardinalityType` after `FS_Subset` from a finite superset; a literal
set is finite `BY FS_EmptySet, FS_AddElement DEF` its name). That was the
only `FiniteSetTheorems` use in a module about voting thresholds.

Not well: sequences, recursion, `Cardinality` in an invariant. Design the
module to avoid them (see [spec-design.md](spec-design.md)).

## Steps that certify under checked backends

A **certified run** replaces the default SMT solver by a wrapper that runs a
proof-producing solver and forwards `unsat` only when an independent
checker accepts the proof, and has Isabelle check every Zenon script.
Most proofs certify unchanged; the ones that do not teach the following.

- **Run the plain prover first**, then the certified run. The plain run is
  faster and finds real proof failures.
- **The checked solver is weaker on very large single steps.** A `TypeOK`
  step that expands a type invariant with many record fields in one `BY`
  may prove under Z3 and not under cvc5. Split by field or by action.
- **Name the parts of a large action.** One lemma on the shapes a step can
  have, with the action's `LET` named part by part, then each invariant
  from the shape. A module written this way certified all of its SMT
  obligations at the default timeout.
- **Give the case split explicitly** when an obligation quantifies over a
  set that has just grown: "an old member, or the new one". Each such
  failure met so far was a real gap in the argument, not solver weakness.
- **An `ENABLED` goal may go to Zenon, and Zenon's script may not
  reconstruct in Isabelle.** A lemma that cannot be certified should not
  sit in a certified module: prove it `BY ExpandENABLED, Isa` so Isabelle
  proves the expanded goal itself, or remove it and leave the fact to a
  TLC witness.
- **A longer timeout rarely helps.** Ten times the timeout recovered one
  obligation out of six across twenty modules. Restructure the step.
- **A refused reconstruction and an unproved obligation are missing
  checks, not counterexamples.** Record them as such; do not read a solver
  failure as a refutation.

## Two unsound cases in the translation

Both are in the pinned prover build this method was developed against and
are reported upstream. Until a release fixes them, the writing rules below
are mandatory, and a scan over every new proof module is part of
generating its results.

**The first: a term under a binder.** The prover hands SMT, Zenon and
Isabelle, as an opaque constant, any term it does not translate: an
`ENABLED` or `\cdot` it has not expanded, or a temporal formula (`[]`,
`<>`, `~>`). That constant does not depend on any variable bound around
it. Before abstracting, the prover also distributes `[]` over `/\` and `<>`
over `\/` and moves a `\A` at the head of a `[]` body (or a conjunct) and an
`\E` at the head of a `<>` body (or a disjunct) outward, so a closed
temporal theorem whose expanded body has such a quantifier is the case
too. The result: `(\E t \in Tools : ENABLED A(t)) => (\A t \in Tools :
ENABLED A(t))` proves `OBVIOUS` and certifies, and TLC finds it false
three steps from `Init`. LS4 is not affected, so `PTL` steps are free of
this case.

Rules:

- **Keep untranslated terms behind hidden definitions** in every step SMT,
  Zenon or Isabelle discharges. Name a temporal property of a parameter by
  a definition, `LT(n) == Spec => (P(n) ~> Q(n))`, and keep it hidden there;
  it is then an uninterpreted function of `n`, and quantifying over `n` is
  sound. Expand it only in a `PTL` step. Expanded in an SMT step, even at
  constant arguments, a body whose `[]` heads a `\A` is the case again.
- **Prove an `ENABLED` or `\cdot` goal `BY ExpandENABLED` (`ExpandCdot`)
  with the action's definition, in the step that proves it**, and do not
  carry the fact across a quantifier by name.
- **Cite a theorem `Spec => []P` in such a step only with `P` hidden and
  applied to no variable bound in the obligation.** Prove an implication
  between invariants as a state-level step and leave the temporal step to
  `PTL`.
- **Do not cite an instance theorem** `ASSUME NEW n \in D PROVE F(n)` whose
  `F` holds an untranslated term over `n` in such a step: at a constant of
  the same name it proves `F` outside `D`. Its exact closure is sound, and
  so is `TAKE` over it; the hidden definition makes both unnecessary.

**The second: two terms with one name.** The prover names each term it
abstracts, and each atom it hands LS4, by the first five hex digits of a
hash of the term as it prints, and does not check that two terms of one
obligation get distinct names. The print shows a bound variable as it
shows a constant of its name, and an expansion, `TAKE` or `WITNESS` that
puts a constant under a binder of its name does not rename the binder. So
two terms can be one symbol to every backend, `PTL` included: by a
collision of the hash (about k(k-1)/2^21 for k names, and findable
offline), or by a **capture**, which recurs under every consistent
renaming.

Rules:

- **Expand no definition at an argument that names one of its bound
  variables**, in the obligation as tlapm forms it: `TAKE x \in S` on
  `\A z \in S : F(z)` leaves `F(x)`; `WITNESS e \in S` leaves `F(e)`; a
  definition named in an argument, an operator passed as one and an infix
  operator are expanded as well. Rename the bound variable; take, witness
  and name nothing a definition binds; write no binder that shadows a
  constant.
- **Run the scan on every new proof module.** No writing rule avoids a
  hash collision. A scan runs the module again over renamed sources and
  reports every input whose names differ and every obligation whose route
  differs between the runs; a step at such an input rests on a collision
  until a reading shows otherwise. The scan also reads every obligation as
  the prover prints it and lists each capture, and every module the model
  checker's parser refuses.
- **A false statement that certifies is a reproducer, not a result.** Keep
  reproducer modules in a directory of their own, extended by nothing,
  with a driver that reruns them and compares each outcome with the
  record; exclude that directory from the sync and the scan.

What these cases cost a method: of four leads-to properties stated in one
liveness module, two are quantified and all four have `ENABLED` premises,
and a `WF1` or `SF1` argument over a measure needs a quantified leads-to
hypothesis inside the proof, which `PTL` cannot combine from instances. In
the pinned prover no route for that step under the rules is known; a
second derivation in a kernel-checked prover is the route taken.

## Cost model

Cost scales with **actions times invariant clauses**, not with the
difficulty of the reasoning: a module with thirteen variables and six
generation-binding clauses proves five hundred obligations in about eleven
seconds. About two obligations in three are closed by the prover's own
normalization with no backend. The expensive part is finding the inductive
invariant, and that is done before the first `BY` is written.
