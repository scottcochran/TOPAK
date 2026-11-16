# writing-lean-encodings-and-proofs

Lean 4 developments that are a second derivation of something already stated elsewhere: a specification proved by
another tool, code that runs, a policy evaluated by an engine.

## What it does

Guides Claude through naming the premise each kind of Lean artifact adds, and keeping that premise honest:

1. **Name the use and its premise**: a re-encoding, a transcription, a model, or a statement in a verified semantics.
2. **Encode beside the source**, with the source text on every definition and one shared prelude of conventions.
3. **Prove with the invariants another prover already found**, by induction on reachable states.
4. **Run mutants** in scratch copies, and check the premise where it carries weight, with a mirror against the model
   checker's state graph or a replay of the code's recorded traces.
5. **Generate the evidence**: digests of everything transcribed, every theorem's axioms, and a kernel replay.
6. **Stay in step** when a source moves, and say only what the result shows.

## Contents

All paths are relative to `skills/writing-lean-encodings-and-proofs/`:

- `SKILL.md`: the workflow, what to do when a source moves, rationalizations to reject
- `references/encoding.md`: TLA+ to Lean conventions, transcriptions, models, statements
- `references/proving.md`: the proof shape, the prover's habits, axioms
- `references/checking-the-premise.md`: mutants, mirrors, trace replay
- `references/evidence.md`: results files, the replay, sync, the vocabulary of claims
- `references/this-repository.md`: where these things are in TOPAK; the only TOPAK-specific file
- `scripts/lean_lint.py`: forbidden constructs and coverage against a TLA+ module

## Why these rules

Every rule comes from TOPAK's three Lean packages, `spec/lean`, `mechanism/lean` and `floor/lean`, and the record that
declares the method, ADR-0053. The companion for the TLA+ side is `writing-tla-specs-and-proofs`.

Leads-to proofs are not yet done in Lean in that corpus. The skill's liveness section is a plan.

## Status

A draft.
