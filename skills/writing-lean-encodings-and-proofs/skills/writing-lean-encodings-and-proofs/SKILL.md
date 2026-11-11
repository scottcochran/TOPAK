---
name: writing-lean-encodings-and-proofs
description: "Writes and maintains Lean 4 proofs that stand beside a formal specification, code or a policy language: re-encodings of TLA+ modules, transcriptions and models of functions, statements in a verified semantics, and refinements between them. Names the premise each one adds, checks that premise where it carries weight (mutants, a mirror against the model checker's state graph, trace replay), and keeps dated results files with axioms and a kernel replay. Use when re-encoding a TLA+ module in Lean, transcribing or modelling Rust or other code in Lean, proving a refinement, diagnosing a failed Lean proof in such a development, bringing a Lean package back in step after its source moved, a sync script reporting STALE, regenerating Lean results, or deciding what a Lean result lets you claim, even if the request only says 'the Lean is stale' or 'prove this in Lean too'."
---

# Writing Lean Encodings and Proofs

## Contents

- [When to Use](#when-to-use)
- [When NOT to Use](#when-not-to-use)
- [The workflow](#the-workflow)
- [When the source moves](#when-the-source-moves)
- [Liveness](#liveness)
- [Quick reference](#quick-reference)
- [Rationalizations to reject](#rationalizations-to-reject)
- [References](#references)

A method for Lean 4 developments that are a second derivation of something already stated elsewhere: a specification
proved by another tool, code that runs, a policy evaluated by an engine. It is distilled from a design corpus with
three Lean packages, covering sixteen re-encoded TLA+ modules, transcriptions and models of a Rust reference, and a
policy floor stated in a verified Cedar semantics.

**Core principle: a Lean theorem is about the Lean.** The kernel settles whether the theorem follows. It says nothing
about whether the Lean is the module, the function or the policy you care about. That connection is a premise, and
most of the method exists to name it, shrink it, and check it where a wrong encoding would do damage. The cautionary
case: a model of a state machine was first written without one effect of a real step, every proof held because the
missing effect broke no safety invariant, and only replaying recorded traces through the model showed that 25 of 58
disagreed.

## When to Use

- Re-encoding a TLA+ module, or another formal specification, as a Lean transition system
- Transcribing a function of real code into Lean, or modelling a larger one
- Stating a policy or configuration in a verified semantics and proving gate claims of it
- Proving that code, or a model of it, refines an encoding
- Diagnosing a Lean proof that fails, or a theorem that resists proof
- Checking an encoding against its source: mutants, a mirror, a replay
- Generating a results file, or bringing a package back in step after its source moved
- Deciding what a Lean result lets a document say

## When NOT to Use

- Writing the TLA+ module or its TLAPS proof. That is `writing-tla-specs-and-proofs`; mutations and reachability
  witnesses stay with TLC
- General Lean or Mathlib development with no external source to stay faithful to
- Machine-translated verification (Aeneas, Verus and the like), where the translator replaces the reading

## The workflow

**1. Name the use and the premise it adds.** Write this in the file header before writing a definition.

| Use | What the Lean states | Premise added | How it can be checked |
|---|---|---|---|
| Re-encoding | The module's constants, `Init`, `Next`, properties | The Lean system is the module | Read; a mirror against the checker's state graph |
| Transcription | A function's types and body | The Lean function is the code | Read; the code's test assertions as `example`s |
| Model | The arms a property is about; every other check is one oracle that can only refuse | Every step the code takes is a model step | Trace replay |
| Statement | A policy in a verified semantics, generated from its own files | The parser and generator are faithful | Generated, digests in the header |
| Refinement | A step of one is a step of the other | Inherits both sides' premises | Proved, given those |

**2. Set up the package to be replayable.** Pin one toolchain by digest and name it in `lean-toolchain`, because a tag
floats. Depend on as little as possible: with no Mathlib the replay covers every constant quickly. Keep packages
apart by what they state.

**3. Encode beside the source.** Each definition carries the text it transcribes in its doc-comment, so a reader can
check it without opening two files. Put the conventions in one shared prelude, and put each place a reading was chosen
in the file's header. Keep the source's names, and say so when one has to change. See
[encoding.md](references/encoding.md).

**4. Prove with the invariants you already have.** A proof from another tool has already found the inductive
strengthening, and reusing it is why this is cheap. One `Init` lemma and one `Next` lemma per invariant group, cases
in the order of the actions, a one-line theorem through the shared `invariant` rule. Each theorem takes only the
hypotheses that its mutations break. End the file with `#print axioms` for every headline theorem. See
[proving.md](references/proving.md).

**5. Run the mutants, in scratch copies.** Break one guard at a time and record which lemma fails. If everything still
proves, the theorem is not using that guard, and that is a finding. Mutants are not committed. The table of what
failed goes in the package README.

**6. Check the premise where it carries weight.** Reading is the default and is sometimes not enough. Check more when
code-level work refines this encoding, when a theorem claims a step *exists* (an `ENABLED` over a laxer encoding can
be proved and false), or when the Lean is a model of running code. See
[checking-the-premise.md](references/checking-the-premise.md).

**7. Generate the evidence.** One script per package does a clean build, prints digests of everything transcribed and
every source, every theorem's axioms, and ends with a kernel replay in a fresh environment. Dated file, regenerated,
never edited. A sync script compares it to the tree. See [evidence.md](references/evidence.md).

**8. Claim only what it shows.** "Proved in Lean, of the encoding", with the premise named. A Lean result is a second
derivation beside the original proof. It replaces neither the proof, nor the source text, nor a mutation run.

## When the source moves

A STALE row means the thing transcribed changed. Regenerating the results file would turn that row green without
anyone having looked.

1. Diff the source against the digest the results file recorded.
2. Re-read the Lean against the new source, every file the row names and not only the one you were told about. A
   results file stamps every source it lists, so regenerating it after re-reading one file re-blesses all the others.
   If you will not re-read them, do not regenerate that series, and say so.
3. If the meaning changed, try the updated Lean outside the tree first (`lake env lean --stdin`, or a scratch copy) and
   see what still proves. If a documented property is lost, stop there: leave the tree building, and report the
   theorem and a counterexample. Otherwise change the Lean to match the source.
4. **A theorem that stops proving after a faithful update is the most useful output this process has.** Do not weaken
   it, delete it, or change the transcription until it passes. Report which property the new source no longer has,
   and let the owner decide whether the code or the claim is wrong before anything in the tree changes.
5. Regenerate only once every listed source has been read and the build is clean.

A frozen specification does not move. Its successor gets a new encoding file, or, where it extends the old module
without replacing it, joins the same file with both digests on the `Transcribes:` line.

## Liveness

In this corpus only `ENABLED` is encoded so far: an availability invariant is still a `[]P`, proved by `invariant`.
Behaviours, weak and strong fairness, and leads-to have no Lean proof yet, so treat what follows as a plan. It comes
to Lean first when the TLA+ prover cannot be trusted with the step, as where a temporal definition may be expanded
only in steps of one backend and no route for a measure-based leads-to is known. It needs behaviours as functions
from `Nat`, `WF` and `SF` over the actions, proofs of the WF1 and SF1 rules, and the fairness conditions named for
whose obligation each is.

## Quick reference

| Rule | Why |
|---|---|
| Source text beside every definition | The fidelity premise is read, so it has to be readable |
| Weakest hypothesis on each theorem | It documents which mutation breaks what |
| `#print axioms` for each headline theorem, and a replay | Axioms alone miss a declaration added past the kernel |
| No `sorry`, no new `axiom` | Either one makes the file a claim about nothing |
| `Classical.choice` and `native_decide` only where explained | Each widens what is trusted, and a reader should find out why |
| Mutants in scratch copies, table in the README | Proves the theorems depend on the guards |
| `scripts/lean_lint.py <dir>`, and `<file> --module M.tla --proof P.tla` | Fails on forbidden constructs; lists coverage gaps to look at |
| A results file stamps every source it lists | Read them all before regenerating |
| "Proved in Lean, of the encoding" | Never "proved" alone, and never "verified" |

## Rationalizations to reject

| Rationalization | Reality |
|---|---|
| "Every proof holds, so the encoding is right." | Proofs say nothing about fidelity. An encoding too lax or too strict can prove every invariant. |
| "The sync script is green after regenerating." | Regenerating stamps the current digests. Green shows only that it ran. |
| "Only one file changed, so I'll regenerate." | The file stamps all its sources, including ones that moved earlier and nobody re-read. |
| "The theorem fails after the change; I'll weaken it to match." | Then the claim has been changed to fit the code without anyone deciding that. Report it. |
| "I'll keep the old transcription so the proofs still pass." | A proof about code that no longer exists, stamped as current. |
| "`#print axioms` shows nothing, so it's clean." | A declaration added with the kernel check off reports no axioms. Only the replay refuses it. |
| "It's proved in two provers, so the premise is gone." | It is a different premise. The second route rests on the encoding. |
| "A quick `sorry` while I finish the rest." | It propagates silently through everything downstream. Use `lean_lint` before you claim anything. |
| "The model is proved, so the code is safe." | The model is proved. That the code is the model is a separate, tested premise, at the constants it was tested at. |
| "`decide` failed, so `native_decide`." | That trusts the compiler. Try `simp` or a smaller statement first, and name the use if it stays. |
| "I'll make this hypothesis stronger so the proof goes through." | It is now a theorem about fewer behaviours. Say which, or find the missing invariant. |

## References

- [encoding.md](references/encoding.md): TLA+ to Lean conventions, parameterized modules, transcriptions, models,
  statements. Read before step 3.
- [proving.md](references/proving.md): proof shape with a worked example, the prover's habits, axioms. Read at step 4
  or when a proof fails.
- [checking-the-premise.md](references/checking-the-premise.md): mutants, mirrors, trace replay. Read at steps 5 and 6.
- [evidence.md](references/evidence.md): results files, the replay, sync, and vocabulary. Read at steps 7 and 8.
- [this-repository.md](references/this-repository.md): where these things are in TOPAK, and its current known-stale
  state. Read first when working in that repository.
