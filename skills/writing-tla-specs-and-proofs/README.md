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
known unsound cases in the prover's translation (tlaplus/tlapm#309 and
#310) and the writing rules that avoid the first and a capture in the
second; the vocabulary of claims (checked, proved, certified, sampled)
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
  under checked backends; the two unsound translation cases, the rules
  that avoid the first and a capture in the second, and what stays
  unprotected (a hash collision; the scan is described, not bundled); the
  cost model
- `references/anti-patterns.md` — what goes wrong in specs, runs, proofs
  and evidence, why, and what catches it
- `references/evidence.md` — results files, digests and pins, freezing
  and successor modules, the sync script, the vocabulary of claims, what
  each tool leaves trusted, certification, a second route
- `scripts/setup_check.py` — is this machine and project ready: Python,
  Java, the pinned `tla2tools.jar` (`--fetch-jar` downloads it), TLC run
  on a bundled fixture, and with `--proofs` tlapm, the fixture's proof and
  its flip test; `--write-pins` records the tools found
- `scripts/tlc_run.py` — one TLC run of one property, printed as one row;
  the run script of the method, for any module
- `scripts/tlc_rows.py` — a row list to a dated, digest-stamped results
  file, written only when every row is as expected
- `scripts/proof_results.py` — `tlapm --cleanfp --strict` to a dated proof
  results file, written only when every obligation is proved
- `scripts/flip_test.py` — the flip-one-hypothesis check
- `scripts/proof_sync.py` — the sync script: `IN SYNC`, `STALE`, `MISSING`
- `scripts/tla_common.py`, `scripts/TLC-PIN` — what the scripts share:
  where modules, tools, pins and results are looked for, and the default
  pin for the model checker
- `assets/selftest/` — the fixture the setup check runs (`Counter.tla`,
  its row list and its proof)

The scripts are Python 3.9, standard library only. They are generalized
from the generators of `gov-tla`, a development written with this skill,
and were run against it before being bundled: one row list in full (208
rows, each as its committed results file has it, but for the state counts
of four liveness counterexamples, which differ from run to run and from
machine to machine and which `tlc_rows.py` does not print), one row in
eight of the other three (166
rows), one proof module (814 obligations) and two flip tests.

## The MCP server

`.mcp.json`, at the root of this plugin, declares the `tla-kit` server
([scottcochran/tla-kit](https://github.com/scottcochran/tla-kit)): TLC,
SANY and tlapm in one container image named by digest, with the scripts
above inside, offered as fourteen tools. Claude Code starts it with the
session through `sh` and `docker run`, with the repository's root mounted
as the project. It needs Docker and a POSIX shell; without them the server
fails to start, and the skill says to run the scripts on the machine as
before. `SKILL.md`'s "The tla-kit server" says which tool answers which
step. A new tla-kit release reaches the plugin by a change to the digest
in `.mcp.json`.

## Status

A draft. The scripts are tested against the bundled fixture, TOPAK's
`Coupling` and `Coupling_live` modules and `gov-tla`, with TLA+ tools v1.7.4
and a tlapm 1.6.0 pre-release, on Linux; other versions and platforms are
untried. It has no eval suite yet; the natural first suite is a review
flow over small TLA+ fixtures with planted flaws (a property that carries
its check, a module without witnesses, a `Mut = "none"` theorem, a
hand-edited results file) and known non-flaws (an unconstrained constant,
a `-deadlock` flag with an audit on record).

## When not to use

PlusCal-first developments, Apalache-specific checking, refinement
mappings between large and small modules as the main activity, or a
project with its own conventions for module layout and results (defer to
its README).
