# The admit composition in Lean 4

`Topak/Admit.lean` transcribes `crates/topak-core/src/admit.rs` (ADR-0030 §1: `floor_gate`, `compose`, and the
types they take and return) and the call site in `crates/topak-node/src/mechanism.rs` (steps 5 and 6) into Lean 4,
and proves of the transcription what `spec/FloorComposition.tla` states of its model. TLAPS proves those
properties of the TLA+ module (`spec/FloorComposition_proof.tla`, T-0045-31). This proves them of the code's
composition: a first piece of the step from module to code that ADR-0045 T-0045-28 says the corpus lacks.

Each Lean definition carries the Rust it transcribes in its doc-comment, so the two can be read side by side.

## What is proved

| Theorem | Claim | Spec property; Rust test |
|---|---|---|
| `admit_witnesses` | an admit means the floor returned `Permit` with exactly the admit's reasons and the bundle returned `Allow` with exactly its engine and digest | the core of all three |
| `admit_implies_floor_permit` | no admit without a floor permit | `AdmitImpliesFloorPermit`; `admit_implies_floor_permit_and_m_override_is_refused` |
| `floor_error_is_deny` | a floor error is `Deny(FloorError)` whatever the bundle said | `FloorErrorIsDeny` |
| `bundle_refusal_honored`, `bundle_refusal_is_deny` | an admit needs an affirmative allow; a refusal on a permit is `Deny(Bundle reason)` | `BundleRefusalHonored`; `bundle_refusal_is_honored_and_m_failopen_is_refused` |
| `admit_iff` | `admit ⟺ floor_permit ∧ ¬bundle_deny`: the code's decision equals the module's `Admit` at `Mut = "none"` under the abstraction `floorPermit`, `bundleDeny` | ADR-0030 §1; `FloorComposition.tla` `Admit` |
| `gate_short_circuits` | when the gate denies, the bundle's answer cannot change the decision | `M_OVERRIDE` refused |
| `floor_deny_names_a_reason`, `compose_deny_reasons` | every floor deny names its reason; `Floor []` is never produced; the composition produces only floor and bundle reasons | ADR-0030 §1 R4; `every_floor_deny_names_a_reason` |
| `floorGate_none_iff` | the gate passes exactly the permits, so the Rust `unreachable!` is unreachable | |
| `callSite_eq_compose` | the node's own gate check before the bundle call is `compose` | `mechanism.rs` 765-771 |
| `permit_and_allow_admit` | a permit and an allow admit | `NeverAdmitted` violated |

`BundleCannotWriteFloorInputs` and `EnvelopeHolds` are about the lift and the store. The composition never
touches either, so they stay with the TLA+ module.

The seven `example`s at the end are the assertions of the Rust tests in `tests/mutations.rs`, each closed by
`rfl`: the transcription evaluates to what the tests assert.

## The clock check (`Topak/Clock.lean`)

`subtracting_interval_elapsed` in [clock.rs](../crates/topak-core/src/clock.rs) is the one arithmetic check the
mechanism's clock makes (ADR-0032 §2). Transcribed with `u64` as naturals below `2^64` and `saturating_add` as a
capped sum, and proved: where nothing saturates the check is `now + margin ≥ start + len` (`elapsed_iff`); a
larger margin elapses whenever a smaller one does, so the margin moves expiry earlier and never later
(`elapsed_mono_margin`, `elapsed_never_later`); the check is monotone in `now` (`elapsed_mono_now`); and with
a margin no larger than the length, an interval has not elapsed before it starts (`not_elapsed_before_start`).
Every proof is `omega` after unfolding. `Lease_A1.tla` abstracts time away; this is the arithmetic beneath it.

## The decision refines `FloorComposition` (`Topak/FloorRefinement.lean`, 2026.10.06)

`Admit.lean` proves the composition's properties of `compose` over abstract floor and bundle outcomes. This file
closes the gap between those outcomes and the module. It transcribes the `topak-floor` wrapper
(`Floor::evaluate` in `crates/topak-floor/src/lib.rs`), which turns the Cedar engine's response into a
`FloorOutcome`. It then proves the code's whole decision, wrapper and `compose`, a step of the module's `Decide`, against
`spec/lean`'s re-encoding of `FloorComposition.tla`, on which this package now depends by path.

| Theorem | Claim |
|---|---|
| `input_failure_is_error`, `engine_error_is_error` | an input rejected before evaluation, and any error diagnostic whatever Cedar decided, is `Error` |
| `wrapper_permit_iff` | the wrapper permits exactly when Cedar allows with no error |
| `wrapper_deny_reasons` | on Cedar's rule with no error, a deny's reasons are the satisfied forbids, so an empty one is `FloorNoPermit` |
| `engine_allow_iff`, `engine_err_iff` | the module's `EngineAllow` and `EngineErr` are Cedar's rule read over its four policies |
| `floorPermit_refines` | the wrapper's permit is the module's `FloorPermit` at `Mut = "none"` |
| `codeAdmits_iff` | the code admits exactly when the module's `Admit` does, for every slice, seat, act and bundle outcome |
| `codeDecide_refines` | **every code decision is a `Decide` step of the module**; an input rejected before evaluation is the module's refusal |
| `code_behaviours_safe` | every state reached by the module's lift and the code's decisions keeps all five of the module's invariants, `EnvelopeHolds` and `BundleCannotWriteFloorInputs` included |
| `decide_is_code` | and every `Decide` step at `Mut = "none"` is a code decision: the code can take every decision the module can |

**What it premises, and what it is not.**
- The engine is Cedar's authorization rule as cedar-spec's `isAuthorized` states it, over the module's four
  policies, or a rejection before evaluation (`EngineFaithful`). That is T-0045-3's own premise, at the module's
  size.
- The floor is the module's four policies. It is neither the genesis floor that `floor/lean/` states nor the floor in
  force that the reference links (ADR-0053 finding 6).
- The lift is the module's own `Reassign` and `Seal`; the code's lift is not transcribed.
- It is not a stage of T-0045-28's chain, and no addendum may cite it as one (ADR-0053 §5, R1 and R2).

## What it rests on

- **The Lean 4 kernel**, toolchain `lean-toolchain` (`leanprover/lean4:v4.33.1`, the one `tools/LEAN-PIN`
  names), installed by `tools/install-lean.sh`. No Mathlib; one dependency, `spec/lean`, by path. `#print axioms` on
  every theorem: `propext` and `Quot.sound` at most, Lean's own; no `Classical.choice`, no `sorry`.
- **The replay.** Every results file ends with `leanchecker --fresh`, which replays every constant the package
  reaches, Lean's own library included, through the kernel in a fresh environment (`tools/lean-report.sh`).
  `#print axioms` alone misses a declaration added with the kernel check off; the replay refuses it
  (`spec/proof-method.md` §5b). It is the same kernel in a fresh process, not an independent checker.
- **The row.** ADR-0053 (Proposed) declares the method and proposes the kernel and toolchain as trusted-base
  row T-0045-37, pinned in `tools/LEAN-PIN`. Until it is ratified a Lean result is evidence no record cites.
- **The transcription.** No Rust-to-Lean translator was run; the Lean is written from the Rust and read against
  it. That reading is the new premise. `MechanismDeny` is opaque: `compose` neither produces nor inspects one,
  and `compose_deny_reasons` says so.
- **Not the engines.** In `Admit.lean`, `FloorOutcome` and `BundleOutcome` are inputs. Since 2026.10.06 the floor
  wrapper is transcribed and proved (`FloorRefinement.lean`); the Cedar engine behind it is T-0045-3's premise. The
  bundle client's `Allow`/`Refuse` is `topak-bundle`'s and is still not proved.

## Mutation check

Three mutated copies of the transcription were built on 2026.10.05, each the code-level shape of a spec mutation.
Each fails to build: the equation lemmas and test instances that state the mutated arm fail, and every theorem
proved through them then rests on `sorryAx`.

| Mutant | What changes | Fails |
|---|---|---|
| `M_OVERRIDE` | a bundle allow admits whatever the floor said | `compose_error`, `compose_permit_allow`, `gate_short_circuits`, examples |
| `M_ERR` | a floor error passes the gate | `floorGate_error`, `floorGate_none_iff`, `compose_error`, examples |
| R4 | an empty forbid list is reported as `Floor []` | `floorGate_deny`, `floorGate_none_iff`, examples |

Three more on 2026.10.06, against the wrapper and the abstraction, each built in a scratch copy of both packages:

| Mutant | What changes | Fails |
|---|---|---|
| `M_ERR`, in the wrapper | Cedar's error diagnostics ignored | `engine_error_is_error`, `wrapper_permit_iff` |
| Fail-open input | an input rejected before evaluation becomes a `Permit` | `input_failure_is_error`, `codeAdmits_input_failure` |
| `M_OVERRIDE`, in the abstraction | a bundle refusal read as an allow | `codeAdmits_iff`, `decide_is_code` |

## Run it

```sh
cd mechanism/lean
lake build                                   # the proofs; ~1 s
./results.sh > Admit-results-<date>.txt      # clean build, digests, axioms, and the replay (~30 s); byte for byte
../../tools/lean-sync.sh                     # STALE when admit.rs, mechanism.rs, clock.rs, topak-floor or FloorComposition moved
```

`Admit-results-2026.10.06.txt` is the results file ADR-0053 cites since R2; the 2026.10.05 file stays beside it,
unchanged. The transcriptions are pinned, not frozen: when `tools/lean-sync.sh` reports a Rust file moved, re-read
the Lean against the new Rust, change it if the meaning changed, and regenerate the results file. `lake update`
regenerates `lake-manifest.json` if the path to `spec/lean` changes.
