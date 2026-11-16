# Anti-patterns

Each entry: what it is, why it is harmful, and what catches it. The
meta-lesson: review alone does not catch these. A results-file generator
that compares each row to its expectation, a flip-one-hypothesis run, a
sync script and a scan catch them deterministically; a reader catches them
sometimes.

## Contents

- [Specification](#specification)
- [Model checking](#model-checking)
- [Proof](#proof)
- [Evidence and vocabulary](#evidence-and-vocabulary)
- [Claims to avoid making](#claims-to-avoid-making)

## Specification

### A property that carries the check

`\A x \in acted : x.act \in KindBound(KindOf[x.seat]) \/ Mut = "M_KIND"`,
or a property with a side condition the guard should have had. Harmful
because the check cannot be removed by a mutation and so cannot be found
missing; and because the proof of the property is then not a proof about
the mechanism. Caught by: a mutation row that reads `HOLDS` where the
header says `COUNTEREXAMPLE`. Fix: the check is a guard on the action;
the property is a flag or a quantifier over records.

### A mutation that removes two guards

Harmful because the counterexample and the proof's hypothesis cannot say
which guard the property rested on, and a design record that cites the row
inherits the ambiguity. Caught by: review of the header; a proof whose
flip test fails for a reason unrelated to the property. Fix: one `Mut`
value per guard.

### No witnesses

A module whose every property `HOLDS` and which never shows that the
forbidden state's neighbours are reachable. Harmful because a property can
hold vacuously: the refusal is never reached, the second round never
granted, the bound never tested. Caught by: nothing, which is the point.
Fix: a `Never…` property per reachability claim, each `VIOLATED` in the
results file.

### A witness that reads the property's flag

`NeverBacklogRefusal` reading `refused`, which an earlier refusal for a
different reason may have set. Harmful because the witness is reached for
the wrong reason and says less than it appears to. Caught by: a liveness
or successor module that needs the sharper witness and finds the old one
does not say what it needs. Fix: distinct flags, or a witness over the
step itself.

### A state condition as fairness

`<>[](oLease)` or "the lease is eventually held for good" as a fairness
assumption. Harmful because a state condition is not machine-closed: under
a mutation that blocks the grant, the spec may have no behaviour and every
property holds. Caught by: the `NoBehaviour` row, which fails to be
violated. Fix: `WF_vars(A)` or `SF_vars(A)` on actions of `Next`, each
named for whose obligation it is.

### Constants constrained in the module

`ASSUME K < R` in the base module, or `MaxRound = 2` baked into a property.
Harmful because TLC evaluates the `ASSUME` and the prover ignores it
unnamed, so the two tools run different modules; and because a bound that
only cuts the state space becomes a premise the theorem does not need.
Caught by: a theorem that holds for every `K` and `R` where the premise
table listed `K < R`. Fix: constants unconstrained; bounds in the run
script; named assumptions in the proof for what the proof actually uses.
The exception is a well-formedness condition on the constants themselves
(`ASSUME Distinct == X # O /\ ...`): that one is a *named* `ASSUME` in the
module, so TLC checks the config and the proof cites it, and it narrows
nothing.

### Terminal states hidden by the deadlock flag

A terminating system run with `-deadlock` and no named terminal predicate.
Harmful because "the game ends" and "no stray stuck state" become one
unchecked thing. Caught by: the deadlock audit, if it has an `AtBound` to
check against. Fix: name the terminal predicate (`GameOver`), make it the
audit's bound, and check `<>GameOver` under the fairness as a liveness
row.

### Deep actions

Nested `IF`/`CASE` with several successors, `INSTANCE`, a refinement
mapping, sequences in the state. Harmful because each multiplies the
obligations and moves the proof onto the constructs the prover is weak
on. Caught by: an obligation count out of proportion to the module; steps
that time out. Fix: a guard, one `EXCEPT`, `UNCHANGED`; outcomes as a
disjunction of branches; a constant operator for the mutation.

## Model checking

### Hand-edited results file

Harmful because the file is the evidence and now says something no run
said. Caught by: regeneration from the row list, which differs; the digest
a record cites, which no longer matches. Fix: regenerate, always; a new
dated file for a changed result.

### Missing "must not break" rows

Only the (mutation, property it breaks) rows run. Harmful because the
"Breaks under" column is then a guess, and the proof's weakest hypothesis
will disagree with it. Caught by: the proof, which proves a theorem under a
hypothesis the results file never tested. Fix: run every mutation against
every property.

### `ERROR` read as `HOLDS`

A run script that treats any output without "is violated" as a pass.
Harmful because a parse error, a missing constant or an exception becomes
evidence. Caught by: a row whose state count is empty. Fix: three verdicts,
the third loud, with TLC's output tail printed.

### A generator that passes on zero rows

Harmful because an empty or misnamed row list produces a green results
file. Caught by: the generator's own exit code, if it has the check. Fix:
exit non-zero when no row was processed, and when any row is `ERROR` or
not as expected.

### Simulation cited as a check

"TLC found no error at `K = 8`" when the run was `-simulate`. Harmful
because a sample is not an exhaustive search and the word "no error"
invites the misreading. Caught by: the row format, if the script prints
`NO ERROR SAMPLED` and the depth, trace count and seed. Fix: a distinct
verdict and a distinct word.

### `-deadlock` without an audit

Harmful because the flag hides real terminal states as well as the
expected ones at the bound. Caught by: a separate deadlock audit, a dated
results file of its own. Fix: run the audit; and know that a stall in a
module with always-enabled actions is a livelock the flag never saw.

### Liveness rows with random fingerprints

Harmful because the counterexample differs from run to run and the results
file is not reproducible. Caught by: a second run that differs. Fix:
`-workers 1 -fp 0` on every `PROPERTY` row.

## Proof

### Editing the base module to carry the proof

Adding `EXTENDS TLAPS`, hypotheses or lemmas to the module TLC runs.
Harmful three ways: the module is frozen by the digest a record cites;
TLC would carry the prover's library into every run; and the proof's
hypotheses (`Mut # "M_X"`) are what the module must not have, since the
module exists so TLC can flip them. Caught by: the sync script (`STALE`);
the digest in the record. Fix: a separate `<Module>_proof.tla` that
`EXTENDS` the base.

### `Mut = "none"` on every theorem

Harmful because the theorem then says nothing about which guard the
property rests on, and the premise table's "Breaks under" column goes
uncorrected. Caught by: the flip test, which fails for every mutation
rather than the right ones. Fix: each theorem under only the mutations
that break it; `Mut = "none"` for `SafeAlways` alone.

### Skipping the flip test

A proof whose hypothesis was never shown to be load-bearing. Harmful
because a proof that still proves with the hypothesis flipped to the
mutation it excludes is proving something the mutation does not break: the
invariant is too weak, the theorem is vacuous, or the hypothesis is
decorative. Caught by: the scratch run. Fix: flip one hypothesis, see
obligations fail, discard the scratch module.

### Writing the Next lemma before the invariant

Harmful because the failing step says only that something is missing. The
sixteen `mark[round]` failures and the six generation-binding clauses were
found faster once the invariant was written in prose first. Caught by:
time. Fix: the header's prose description of the strengthening before any
definition; the definitions before any lemma.

### Citing a `Mut` theorem inside `PTL`

`BY ThmA, ThmB, PTL DEF Safe` where `ThmA` carries `ASSUME Mut # "M_X"`.
Harmful because the obligation fails and the failure looks like a temporal
problem. Caught by: the prover. Fix: an explicit `Spec => []P` step per
theorem first.

### An `ENABLED` or temporal fact carried by name across a quantifier

`\A t \in Tools : ENABLED A(t)` derived from an instance, or a theorem
`Spec => []P(t)` cited inside a step SMT discharges. Harmful because the
prover abstracts the untranslated term to a constant that forgets `t`, and
the step proves and certifies while false. Caught by: the scan, by
reading; TLC, which finds the statement violated. Fix: the rules in
[prover-habits.md](prover-habits.md): hidden definitions, `ExpandENABLED`
in the step that proves, expansion only in `PTL`.

### A definition expanded at an argument it binds

`TAKE k \in D` on a goal whose body binds `k`; a `WITNESS` of a name a
definition binds. Harmful because the expansion prints as another term
and is named as it, so two terms are one symbol. Caught by: the scan's
capture reading. Fix: rename; take, witness and name nothing a definition
binds.

### An uncertifiable lemma in a certified module

A lemma Zenon proved whose script Isabelle refuses, kept because no
theorem uses it. Harmful because the module's certified status then rests
on an obligation no checker accepted. Caught by: the certified run's
route counts. Fix: `BY ExpandENABLED, Isa`, or remove it and leave the fact
to a TLC witness.

### Raising the timeout

Harmful because it almost never recovers the step and always hides which
step was oversized. Caught by: the certified run, where the checked solver
is weaker than the default. Fix: split by clause, by field or by action;
state the case split; name the `LET` parts.

## Evidence and vocabulary

### "Proved" of a TLC result, "holds" of running code

Harmful because each word names what bounds the claim, and a design record
that uses the wrong one has made a claim its evidence does not support.
Caught by: review of every record that uses the words; a premise table that
names the trusted-base row each result rests on. Fix: **checked** for TLC at
constants; **proved** for the prover under named hypotheses; **sampled**
for simulation; and a standing statement that none of them is a claim
about what runs until a refinement exists.

### A results file without digests

Harmful because the file cannot say which module text or which checker
build produced it, so a module edit or a tool upgrade is invisible. Caught
by: the sync script, which has nothing to compare. Fix: the module's digest
and the tool's digest in every header; the proof's results file names
every module in the `EXTENDS` chain.

### An unpinned prover

A pre-release tag that upstream rebuilds under the same name. Harmful
because a fresh install yields a different binary and the results files
now cite a tool nobody can reinstall. Caught by: the pin file compared at
install and at every run. Fix: pin version, commit and binary digest; the
wrapper refuses a mismatch without an explicit override; the sync script
reports a results file that cites another prover.

### A proof merged into its module's successor

The successor edited to carry the proof, or the old proof left pointing at
the frozen module while the record cites the successor. Harmful because
the proof is now a proof of the wrong text. Caught by: the sync script.
Fix: copy the proof module, point `EXTENDS` at the successor, re-prove,
regenerate, commit with the successor and its TLC results in one commit.

### A base module without a proof and without a reason

Harmful because the gap is invisible in a table of what is proved. Caught
by: the sync script, if it fails on a proofless module with no recorded
reason. Fix: write the proof, or record why not (shared definitions with
no `Spec`; superseded by a successor that is proved; a trace replay whose
target is a refinement).

## Claims to avoid making

- "TLC at larger constants would be a stronger proof." It would be a
  stronger check. The prover's theorem already covers every constant the
  assumptions admit; what TLC adds at larger constants is a bigger
  non-vacuity witness.
- "All N obligations proved means the theorem is true." It means every
  obligation is a theorem under the module's assumptions and the prover.
  Say which prover, which backends, and what they leave trusted (see
  [evidence.md](evidence.md)).
- "A certified proof is fully checked." Certification removes the SMT
  solver and Zenon from the trusted base. The prover's translation and
  normalization, Isabelle, and the temporal backend remain trusted.
- "The mechanism never deadlocks, TLC said so." TLC with `-deadlock` said
  nothing; without it, it said no reachable state is terminal, which in a
  module with always-enabled actions is true of a mechanism stalled
  forever.
