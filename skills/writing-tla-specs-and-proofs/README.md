# writing-tla-specs-and-proofs

Structured TLA+ specification, TLC model checking and TLAPS proof
development, for developments whose evidence has to stay honest over
months of change and whose proofs humans *and* LLMs can write, repair and
extend.

## What it does

Guides Claude (and Codex, via marketplace compatibility) through a
spec-first, check-then-prove workflow:

1. **Write the specification so its properties are local**: a flag the
   violating action would set, or an append-only set of records; every
   mechanism check as a guard on the action that needs it; one `Mut`
   constant with one guard per mutation; a `Never…` witness per
   reachability claim; a type invariant; shallow actions over finite,
   literal domains; constants bounded in the run script, not the module.
2. **Model-check at small constants**: every mutation fails the property
   it must break and no other, every witness is violated, `Safe` holds.
   One run script per module, a row list, a dated results file with the
   checker's and the module's digests, regenerated and never edited.
3. **Prove the invariants** in a proof module that extends the frozen
   spec: `TypeOK` first under every mutation, one `Next` lemma per
   invariant group with one step per action, a three-line theorem, each
   theorem under only the mutations that break it, `SafeAlways` under
   `Mut = "none"`, one lemma per mutation saying what it admits.
4. **Check the proof's non-vacuity and generate the evidence**: flip one
   hypothesis and watch it fail; a results file with every digest in the
   `EXTENDS` chain and the prover's; a sync script that reports `STALE`.

Plus: the ladder for finding an inductive invariant (flag, a record that
agrees with the derived truth, append-only set, valid state predicate,
established-and-frozen, arithmetic in layers, generation binding); the
liveness proof shape for an unquantified leads-to; the prover's habits that cost time and the fix for
each; the rules for steps that certify under checked backends; the two
known unsound cases in the prover's translation and the writing rules that
avoid them; the vocabulary of claims (checked, proved, certified, sampled)
and what each tool leaves trusted.

## Why these rules

Every rule is drawn from one design corpus, TOPAK, whose `spec/` directory
holds fifty-odd modules, twenty-four TLAPS proof modules over about three
thousand obligations, and a dated results file for every run, and whose
method notes record what made the proofs cheap and where that stopped. The
primary sources are TOPAK's `spec/README.md`, `spec/proof-method.md`,
`spec/proof-certification.md` and `spec/theorem-premise-binding.md`, with
the `Coupling` and `Seats` modules and their proofs as the worked examples.
The liveness proof shape and the named-`ASSUME` rule come from a
tic-tac-toe spec and TLAPS proof outside TOPAK (`TicTacToe.tla`,
`TicTacToe_proof.tla`, 135 obligations), the one WF1 proof in hand; the
liveness section quotes its steps.
The skill generalizes those choices; where a TOPAK-specific record or tool
name would have appeared, the skill says what the thing is for instead.

The structure of this plugin follows Trail of Bits'
`writing-lean-proofs`.

## Contents

All paths below are relative to `skills/writing-tla-specs-and-proofs/`:

- `SKILL.md` — the workflow, the inductive-invariant ladder, the
  quick-reference rules, rationalizations to reject
- `references/spec-design.md` — writing modules so properties are local;
  mutations, witnesses, type invariants, shallow actions, constants, the
  header as contract, liveness only when claimed; a worked module
- `references/model-checking.md` — run scripts, the row matrix, results
  files, row lists and generators, the deadlock flag and its audit,
  practical constants and simulation, liveness rows, reading a
  counterexample
- `references/proof-style.md` — the proof module's layout, the type
  invariant lemma, the `Next` lemma, the theorem, `SafeAlways`, mutation
  lemmas, the inductive-invariant patterns in full, the liveness proof
  shape (measure, WF1, `Nat` induction over a hidden `G(n)`), step hygiene
- `references/prover-habits.md` — running tlapm; parse, scope and
  temporal habits; what the SMT backend handles alone; steps that certify
  under checked backends; the two unsound translation cases and the rules
  that avoid them; the cost model
- `references/anti-patterns.md` — what goes wrong in specs, runs, proofs
  and evidence, why, and what catches it
- `references/evidence.md` — results files, digests and pins, freezing
  and successor modules, the sync script, the vocabulary of claims, what
  each tool leaves trusted, certification, a second route

## Status

A draft. It has no eval suite yet; the natural first suite is a review
flow over small TLA+ fixtures with planted flaws (a property that carries
its check, a module without witnesses, a `Mut = "none"` theorem, a
hand-edited results file) and known non-flaws (an unconstrained constant,
a `-deadlock` flag with an audit on record).

## When not to use

PlusCal-first developments, Apalache-specific checking, refinement
mappings between large and small modules as the main activity, or a
project with its own conventions for module layout and results (defer to
its README).
