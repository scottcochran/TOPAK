# The mechanism's code in Lean 4

`Topak/Admit.lean` transcribes `crates/topak-core/src/admit.rs` (ADR-0030 §1: `floor_gate`, `compose`, and the
types they take and return) and the call site in `crates/topak-node/src/mechanism.rs` (steps 5 and 6) into Lean 4,
and proves of the transcription what `spec/FloorComposition.tla` states of its model. TLAPS proves those
properties of the TLA+ module (`spec/FloorComposition_proof.tla`, T-0045-31). This proves them of the code's
composition: a first piece of the step from module to code that ADR-0045 T-0045-28 says the corpus lacks.
Since 2026.10.06 it also holds a model of `State::apply`'s seat and lease arms, refining `Seats.tla` and replayed
against the reference's recorded traces, and a second model on it for what `Coupling.tla` is about (below).

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

## A Seats-shaped model of `apply` (`Topak/SeatsModel.lean`, 2026.10.06)

`State::apply` in [state.rs](../crates/topak-core/src/state.rs) is too long to transcribe whole. This file **models**
the part of it `spec/Seats.tla` (ADR-0037) is about: which seats hold a live lease, for which principal, under which
alphabet, and what was admitted under them. Each arm keeps its checks and its effects on those fields: grant on every
path (unsigned, an operator's `Regrant`, an activation), renewal, admit (with `Submit` and `Vote` ending the lease),
end of round on both paths, revocation and Contested, the fleet fence, issuance. Every other check the arm makes is
one Boolean, `ok`, that can only refuse. So the model's steps include every step the code takes, whatever the
checks it leaves out decide. An admitted act is recorded with its seat's kind in `acted`, a history variable; the
code keeps none, and the log does.

| Theorem | Claim |
|---|---|
| `model_inv` | on every state the model reaches, at any number of seats and principals: `live_by_seat` indexes exactly the live leases, each at its seat; no fence is past `last_applied`; every live alphabet is within its seat's kind; every admitted act was within the kind of the seat it was admitted under; two live leases are two principals |
| `model_one_seat_per_principal`, `model_acted_within_kind` | ADR-0037 §1 and §4 of the code's `apply`, read off the invariant |
| `step_refines` | at `Seats.tla`'s constants, every model step is a `Seats.Next` step at `Mut = "none"`, a run of `EndRound`s (a revocation, a fence, an issuance), an `Act` and an `EndRound` (a terminal act), or a stutter. The code's nine action kinds are read as the module's four, and under that reading each kind's `allows` is exactly `KindBound` (`allows_bound`, `allows_image`) |
| `model_refines_seats`, `model_seats_safe` | every state the model reaches there maps to one `Seats.tla` reaches, so `Seats_proof.tla`'s `SafeAlways` holds of it |

**What it premises.**
- **The log** delivers increasing indices. `apply_inner` records any index as `last_applied` and inserts a granted
  lease under it, so a fence's freshness is the consensus layer's (ADR-0053 finding 9).
- **The model is the code**, on its fields. Each arm carries the Rust it models, and the trace replay below checks it.
- **Where the model reads the state differently.** The Rust finds live leases through `live_by_seat`'s values. The
  model finds them as live records indexed at their own seat. The two sets are equal wherever `model_inv` holds.
- **At the module's constants, no issuance changes a seat's kind** (`INext`). The code allows one:
  `validate_issuance` does not compare the issued seats with the current ones. `model_inv` needs no such premise,
  because an issuance ends every live lease (ADR-0053 finding 8).
- It is not a stage of T-0045-28's chain (ADR-0053 §5, R1 and R4): the oracle stands for most of `apply`, and the
  refinement is of one module at its constants.

**The trace replay** (`SeatsReplay.lean`, `seats-replay.sh`). `trace.rs` records every applied entry of the
reference's suites, with its result and a projection of the state after it, for `spec/Mechanism.tla`'s trace
validation. `seats-replay.sh` runs the same six suites and passes every trace to `SeatsReplay.lean`. That program
applies each recorded entry with the model's own `apply`, the function the proofs are about, with `ok` set to whether
the reference applied it. After each step it compares the result, the leases (seat, principal, Persona, confinement
digest, alphabet, ended), `live_by_seat`, the seat kinds and `last_applied` with the projection. That is the
direction the proofs need: every recorded code step is a model step. `SeatsReplay-results-2026.10.06.txt` reports
82 traces and 1014 steps, all MATCH. It is a test over the traces the suites record, not a proof.

The first replay failed 25 of 58 traces. The model left out that an admitted `Submit` or `Vote` ends the lease, and
every proof held without it, since ending a lease breaks no safety invariant. The replay is what found it (ADR-0053
finding 7).

## A Coupling-shaped model on it (`Topak/CouplingModel.lean`, 2026.10.06)

The Seats-shaped model leaves every check outside its fields to `ok`. This file narrows that where
`spec/Coupling.tla` (ADR-0039, ADR-0042) is about: what an Observer has read of a Thinker's round. Its state adds each
lease's epoch, round, sequence number and action count, the seats' domains and cells, the fleet epoch, the
watermarks, the seals and each seat's last round. Its checks add, at grant, the alphabet within the seat's domain,
the cross-round condition and round numbers never reused; at admit, the round bound, a heartbeat's validity
(`check_heartbeat`) and a Thinker's coupling to a cell Observer (`observer_covers`). Its `apply` is the Seats-shaped
step with those checks folded into `ok`, then the new fields updated, so every step is a Seats-shaped step and
every theorem there holds here (`base_reach`).

| Theorem | Claim |
|---|---|
| `xstep_inv`, `model_xinv` | every step keeps the invariant: live alphabets within their seat's domain, and the two below |
| `model_unread_bounded` | at any number of seats: a Run Thinker's live round has at most `K` effects unread by some cell Observer |
| `model_prior_read` | and its last round was read to the seal by some cell Observer before this one was granted, and stays so |
| `model_unread_bounded_one` | with one Observer in the cell, `Coupling.tla`'s `Unread + PriorUnread <= K` |
| `admit_coupled` | an admitted `Actuate` or `Report` of a Thinker had a covering cell Observer |

These are proved of the model directly, at any size; the model is **not** proved to refine `Coupling`'s encoding.
The module counts one Thinker's rounds, keeps a seal per round and has a freshness flag; the code keeps the last
seal only and reads freshness from a clock at decide (`observer_covers(.., &|_| true)` at apply). A refinement would
need history the code does not keep.

**With more than one Observer in a cell** the two halves have their own witnesses: one Observer may have read the
last round to its seal and another be within `K` of the live one. What no Observer has read is at most `K`; what one
has not read is not bounded (ADR-0053 finding 10).

**The trace replay** (`CouplingReplay.lean`, `coupling-replay.sh`) runs the same six suites through the model's
`rapply` and also compares each lease's epoch, round, sequence number and action count, the epoch, every watermark,
every seal and every last round. `CouplingReplay-results-2026.10.06.txt`: 82 traces, 1015 steps, all MATCH, with 51
coupled admits, 34 heartbeats and 7 cross-round grants among them. It matched on its first run; a model whose
sequence number did not count `Actuate` failed four traces at the first `Actuate`.

## What it rests on

- **The Lean 4 kernel**, toolchain `lean-toolchain` (`leanprover/lean4:v4.33.1`, the one `tools/LEAN-PIN`
  names), installed by `tools/install-lean.sh`. No Mathlib; one dependency, `spec/lean`, by path. `#print axioms` on
  every theorem: `propext` and `Quot.sound` at most, Lean's own; no `Classical.choice`, no `sorry`.
- **The replay.** Every results file ends with `leanchecker --fresh`, which replays every constant the package
  reaches, Lean's own library included, through the kernel in a fresh environment (`tools/lean-report.sh`).
  `#print axioms` alone misses a declaration added with the kernel check off; the replay refuses it
  (`spec/proof-method.md` §5b). It is the same kernel in a fresh process, not an independent checker.
- **The row.** ADR-0053, ratified 2026.10.06 (Batch 36), declares the method and makes the kernel and toolchain
  trusted-base row T-0045-37, pinned in `tools/LEAN-PIN`. A Lean result is cited by the results file ADR-0053 §4 names.
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

Four more on 2026.10.06, against the model of `apply`. Each drops one check, with the case lemma stating the arm
revised to match, as an honest revision of the proof would be:

| Mutant | What changes | Fails |
|---|---|---|
| `M_SEAT`, the reference before 2026.09.29 | a grant does not refuse a principal holding a live lease elsewhere | `grant_inv`, `step_refines` |
| `M_KIND` | a grant does not bound the alphabet by the seat's kind | `grant_inv` |
| Widening renewal | a renewal's alphabet need not be within the old one | `renew_inv` |
| Issuance that leaves leases live | new seat kinds, no `end_all_live` | `issue_inv`, `step_refines` |

Five more against the coupling model, each a check made always true:

| Mutant | What changes | Fails |
|---|---|---|
| `M_ROUNDS` | no cross-round condition at grant | `xstep_inv`, its grant arm |
| `M_NOCOUPLE` | a Thinker's effect is not coupled | `xstep_inv`, its admit arm; `admit_coupled` |
| `M_MARK` | coupling ignores the backlog | `xstep_inv`, its admit arm |
| Domain | a grant's alphabet need not be its seat's domain | `xstep_inv`, its grant arm |
| Lowering | a heartbeat may lower a watermark | `xstep_inv`, its admit arm |

And one against the Rust: a copy of `state.rs` without ADR-0037 §1's check, its `mutations` suite traced. The replay
fails `one_seat_per_principal_and_m_seat_is_refused` at step 2, where the reference grants a held principal a second
seat and the model refuses it. A model without the check fails the proofs, and code without it fails the replay.

## Run it

```sh
cd mechanism/lean
lake build                                   # the proofs; ~1 s
./results.sh > Admit-results-<date>.txt      # clean build, digests, axioms, and the replay (~30 s); byte for byte
./seats-replay.sh > SeatsReplay-results-<date>.txt         # the six suites replayed through the Seats model
./coupling-replay.sh > CouplingReplay-results-<date>.txt   # and through the Coupling model
../../tools/lean-sync.sh                     # STALE when admit.rs, mechanism.rs, clock.rs, topak-floor, state.rs,
                                             # types.rs, lease.rs, rules.rs, trace.rs, or a module, moved
```

`Admit-results-2026.10.06c.txt`, `SeatsReplay-results-2026.10.06.txt` and `CouplingReplay-results-2026.10.06.txt`
are the results files ADR-0053 cites since R5. The 2026.10.05 file and the 2026.10.06 and 06b files R2 and R4 cited
stay beside them, unchanged. The replay is not regenerated
byte for byte, since the e2e traces are named after their process ids; it is rerun, and every trace must match. The
transcriptions are pinned, not frozen: when `tools/lean-sync.sh` reports a Rust file moved, re-read the Lean against
the new Rust, change it if the meaning changed, and regenerate the results file. `lake update` regenerates
`lake-manifest.json` if the path to `spec/lean` changes.
