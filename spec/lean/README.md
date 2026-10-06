# The spec/ modules in Lean 4

Fourteen TLA+ modules of `spec/`, re-encoded as transition systems in Lean 4 and their TLAPS theorems proved
by induction on reachable states. The seven small finite-set modules: `Seats`, `Observers`, `RunSeats`,
`FloorRouting`, `NonComposition`, `Anchor` and `BreakGlass`, with `RulesFloorBase` as the last two's shared
base. `FloorComposition` (2026.10.06), the admit composition, which `mechanism/lean/Topak/FloorRefinement.lean`
proves the code's decision refines. `Seats` is also the target of `mechanism/lean/Topak/SeatsModel.lean`, a model
of `State::apply`'s seat and lease arms proved to refine it at the module's constants (2026.10.06). `Coupling`'s
properties are proved of `mechanism/lean/Topak/CouplingModel.lean` directly, at any size; that model does not refine
`Coupling.lean`. And the parameterized ones: `Coupling` for every `K`, `R` and `MaxRound`; `Lease_A1` for every epoch
and fence bound; `RulesFloorNV_rev5`, with its cardinalities computed over the five humans; and `Confinement`
and `Confinement_A1` as one encoding under a flag, for every rung. Each `TopakSpec/<Module>.lean` carries
the TLA+ it transcribes beside every definition and proves what `spec/<Module>_proof.tla` proves, with the
same inductive invariants and the same hypotheses on `Mut`.

## What this adds to the TLAPS proofs

`spec/proof-method.md` §5a: in the certified run, every obligation is closed by tlapm's normalization, by a
checked SMT proof, or by **LS4** for the temporal step of each theorem, "the invariant holds initially, every
step keeps it, so it holds always", which is checked by nothing. Here that step is `Prelude.invariant`,
an induction on `Reachable`, and the kernel checks it. The Lean theorems are therefore the TLAPS theorems with
the LS4 premise removed and a different one added: that the Lean encoding is the TLA+ module.

**Three of the sixteen TLAPS modules do not certify** under the checked backends (`proof-certification.md` §5a):
`RulesFloorNV_rev5`, where Isabelle refuses one of Zenon's scripts, and `Confinement` and `Confinement_A1`,
where three `TypeOK` steps each are proved by Z3 alone. All three are here, every step kernel-checked. The
arithmetic those proofs hand to SMT, and `Coupling`'s, is `omega`; `TypeOK` has no counterpart; the
`FiniteSetTheorems` facts about cardinalities are a count over five humans.

Three of the TLAPS proofs' assumptions vanish under Lean's types. `TypeOK` lemmas have no counterpart.
`Active ⊆ AllEntries` (Anchor, BreakGlass) holds because `Active` is a set of entry names. `MaxEpoch ∈ Nat`
holds because `MaxEpoch : Nat`. One stays: BreakGlass's `"R7" ∈ Active` is the hypothesis `hR7`, as it must
be, since the property is R7's claim.

## Theorems

| File | Theorems | Hypotheses |
|---|---|---|
| `Seats.lean` | `OnlyThinkersAuthorAlways`, `OneSeatPerPrincipalAlways`, `SafeAlways` | `m ≠ M_KIND`; `m ≠ M_SEAT`; `none` |
| `Observers.lean` | `DenyByAnyOfAlways`, `ReachIsBoundedAlways`, `SafeAlways` | `m ≠ M_QUORUM`; `m ≠ M_REACH`; `none` |
| `RunSeats.lean` | `OnlyThinkersActuateAlways`, `ObserversConsultAndReportAlways`, `NoNameCrossesDomainsAlways`, `SafeAlways`, `SafeUnderObsEmit` | `m ≠ M_KIND`; `m ≠ M_KIND`, `m ≠ M_DOMAIN`; `m ≠ M_DOMAIN`; `none`; `M_OBSEMIT` |
| `FloorRouting.lean` | `SafeAlways`, `NoWideningAlways`, `NeverVacuousAlways` | `none` |
| `NonComposition.lean` | `SafeAlways`, `NC1Always`, `NC2Always` | `m ≠ M1`, `m ≠ M2` |
| `Anchor.lean` | `FloorPreservedAlways`, `EpochMonotoneAlways` | `none`; any `m` |
| `BreakGlass.lean` | `NeverChangesAuthority` | `none`, `R7 ∈ Active` |
| `RulesFloorBase.lean` | `GenesisEntries`, `GenesisFloor` | the module's `ASSUME`, proved |
| `FloorComposition.lean` | `AdmitImpliesFloorPermitAlways`, `FloorErrorIsDenyAlways`, `BundleRefusalHonoredAlways`, `BundleCannotWriteFloorInputsAlways`, `EnvelopeHoldsAlways`, `SafeAlways` | `m ∉ {M_ERR, M_OVERRIDE}`; the same; `m ∉ {M_FAILOPEN, M_OVERRIDE}`; `m ≠ M_WRITE`; `m ∉ {M_WRITE, M_ERR, M_OVERRIDE}`; `none`. Its `TypeOK` is not needed: `NONE` in the truth only makes a policy "ERR", which denies |
| `Coupling.lean` | `UnreadBoundedAlways`, `NoAdmitWithoutLiveObserverAlways`, `CorrelatorNeverGatesAlways`, `SafeAlways` | `m ∉ {M_MARK, M_ROUNDS, M_NOCOUPLE}`; `m ≠ M_NOCOUPLE`; `m ≠ M_CORR`; `none`; every K, R, MaxRound |
| `Lease_A1.lean` | `LeaseAuthorityMonotoneAlways`, `NoActionUnderFencedEpochAlways`, `Rung0NeverContainedAlways`, `RevokedStaysStoppedAlways`, `SafeAlways` | `m ∉ {M_RENEW, M_ROLE, M_LOWER}`; `m ≠ M_FENCE`; `m ≠ M_RUNG`; `m ≠ M_REVOKE`; `none` |
| `RulesFloorNV_rev5.lean` | `P1Always` to `P9Always`, `SafeAlways`; `GenesisEntries`, `EntriesIndependent`, `R9IndependentUnderThreshold` | `R1 ∈ Active`; `R2`; `rev5`; `R5`; `R7`; `R2 ∧ (R1 ∨ R9)`; all entries and `rev5`; the module's three `ASSUME`s, proved |
| `Confinement.lean` | `ContainedMeansConfinedAlways`, `NoSilentDowngradeAlways`, `ContestedStoppedAlways`, `FreshAppraisalAlways`, `SafeAlways`, and the two modules by name | `m ∉ {M_HOST, M_HW, M_CONTESTED, M_UNBOUND, M_PROFILE}`; `m ∉ {M_DOWNGRADE, M_RENEWLOW}`; `m ≠ M_CONTESTED`; `m ≠ M_STALE`; `none`; every `Declared`, both `Evidence` clauses |

Each file also carries the TLAPS module's "why the mutation must fail" lemmas where they are about the
definitions rather than about a TLC run. Witnesses stay with TLC.

## How the TLA+ is encoded

`TopakSpec/Prelude.lean` states the conventions. A TLA+ set is a predicate; a string-valued constant set is an
inductive type; a BOOLEAN variable is a `Prop` and `x' = (a \/ b)` is `x' ↔ a ∨ b`; `IF` on a decidable
condition is `if`, on a set membership it is a pair of implications; `S # {}` is `NonEmpty S`;
`Cardinality` is the relation `HasCard`; stuttering steps are dropped. Two renamings: the TLA+ action
`Act(s)` is `ActStep` where `Act` names the set of acts, and `Finding(o, t)` is `FindingStep` where
`Finding` names the record. The parameterized modules add: constants bundled in a `Cfg`; TLA+'s `-` on
naturals computed in `Int`; variables only ever set to TRUE or FALSE as `Bool`; sets of humans as `Human →
Bool` with a computable `card`; a successor state written `st' = { st with ... }`, which is the primed
conjuncts and the `UNCHANGED` list at once; `IF`/`CASE` chains with different successors as disjunctions
of their branches; and `seal` renamed `seals`, since `seal` is a Lean keyword.

## What it rests on

- **The Lean 4 kernel**, toolchain `lean-toolchain` (`leanprover/lean4:v4.33.1`, the one `tools/LEAN-PIN`
  names). No Mathlib, no dependencies. `#print axioms`: `propext` and `Quot.sound` at most for thirteen modules;
  `NonComposition` also uses `Classical.choice`, because its `Erase` step cases on a set membership, as TLA+
  does. No `sorry`.
- **The replay.** Every results file ends with `leanchecker --fresh`, which replays every constant the package
  reaches, Lean's own library included, through the kernel in a fresh environment (`tools/lean-report.sh`).
  `#print axioms` alone misses a declaration added with the kernel check off; the replay refuses it
  (`spec/proof-method.md` §5b). It is the same kernel in a fresh process, not an independent checker.
- **The row.** ADR-0053 (Proposed) declares the method and proposes the kernel and toolchain as trusted-base
  row T-0045-37, pinned in `tools/LEAN-PIN`. Until it is ratified a Lean result is evidence no record cites.
- **The encoding.** A proof here is of the Lean re-encoding, not of the frozen TLA+ text, which the TLAPS
  proofs are of. The encoding is written from the module and read against it; ADR-0053 §2 names this as the
  premise the method adds. Where the encoding could be read two ways, the file says which was taken. For `Seats`
  and `FloorComposition` it is also checked, below.

## The encodings checked against TLC's state graphs (2026.10.06)

`Seats` and `FloorComposition` are the modules the code-level work in `mechanism/lean/` refines, so their encodings
carry the most. `TopakSpec/Mirror/` gives each a mirror: a concrete state with Booleans for the encoding's `Prop`s
and Boolean functions for its sets, a map into the encoding's states, and a list of successors, with these proved:

| Theorem | Claim |
|---|---|
| `next_iff` | from a mirrored state, the encoding's `Next m` reaches exactly the mirrored states in the successor list |
| `init_iff` | a state satisfies the encoding's `Init` exactly when it is the mirror's initial state |
| `eqC_iff` | the mirror's equality is equality of the encoding's states |
| one `*_iff` per property | each property, as a Boolean, equal to the encoding's |

`graph-check.sh` has TLC dump each module's whole state graph (`-dump dot`) under every `Mut`. It goes through a
wrapper module whose one derived variable carries every property's value, so the graph's shape is unchanged.
`dot2lines.py` reads the dump, and `graphcheck` (`GraphCheck.lean`) evaluates the mirror on it. It checks that every TLC edge is
a `Next` step, that every `Next` step from a TLC state is a TLC edge or a stutter, that the initial states are the
encoding's `Init`, and that every property has TLC's value in every state.

`GraphCheck-results-2026.10.06.txt`: all eight graphs MATCH, from 128 states (`FloorComposition`, `none`) to 53,248
states and 442,368 edges (`Seats`, `M_KIND`). Both encodings fix the module's constants in their types, so a graph
is every state the encoding can reach: the encoding and the module reach the same states by the same steps, with
the same property values. The mirrors are proved; the evaluation, TLC's dump and its parse are a test.

Three mutated TLA+ modules, each checked against the unchanged encoding, each failed:

| Mutant | What the check found |
|---|---|
| `Grant` without "the seat has no live lease" | 3,552 TLC edges that are not `Next` steps. Both invariants still hold of it, so no proof sees it |
| `Seal` that never fires | 64 `Next` steps that are not TLC edges |
| `OnlyThinkersAuthor` without its `Vote` clause | the property's value differs on 6,656 states |

## Mutation check

Eighteen mutated copies of the encodings were built on 2026.10.05 (`FloorComposition`'s mutations are the code's, `mechanism/lean/README.md`), each a spec mutation with its `Mut` guard
removed or a finite table widened. Each fails to build, in the lemma that carries the mutated definition
into the inductive step; the theorems proved through that lemma then rest on `sorryAx`.

| Module | Mutant | Fails in |
|---|---|---|
| Seats | the observer kind bound includes `Draft` | `KindBoundKinds` (feeds `OnlyThinkersAuthorAlways`) |
| Seats | the grant ignores `HoldsElsewhere` (M_SEAT always) | `NextInvS` (feeds `OneSeatPerPrincipalAlways`) |
| Observers | every observer reaches every thinker (M_REACH always) | `NextReach` (feeds `ReachIsBoundedAlways`) |
| Observers | the quorum rule under every `Mut` (M_QUORUM always) | `NextDeny` (feeds `DenyByAnyOfAlways`) |
| FloorRouting | every proposal routes to promotion | `PromoteNarrows` (feeds `NoWideningAlways`) |
| RunSeats | the observer kind bound includes `Actuate` | `KindActuate`, `ObserverRun` |
| NonComposition | F1 is erasable under `none` (M1 always) | `ForensicKept` (feeds `NC2Always`) |
| BreakGlass | the envelope is ignored (M_SCOPE always) | `NextInv` (feeds `NeverChangesAuthority`) |
| Anchor | the floor check is omitted (M_FLOOR always) | `NextFloor` (feeds `FloorPreservedAlways`) |
| Coupling | `LiveO` ignores the watermark (M_MARK always) | `NextInvU` (feeds `UnreadBoundedAlways`) |
| Coupling | the grant does not wait for coverage (M_ROUNDS always) | `NextInvU` |
| Lease_A1 | a renewal may lower the rung (M_LOWER always) | `RenewRefines` (feeds `LeaseAuthorityMonotoneAlways`) |
| Lease_A1 | the fence is not checked at an act (M_FENCE always) | `NextFenced` (feeds `NoActionUnderFencedEpochAlways`) |
| RulesFloorNV_rev5 | the author is a counted seat (norecuse always) | `author_not_counted` (feeds `P3Always`) |
| RulesFloorNV_rev5 | R9 accepts a threshold of 1 | `NextP9` (feeds `P9Always`), and the R9 independence witness |
| Confinement | the lease is not bound to the attested guest, at grant and at act (M_UNBOUND) | `NextInvC` (feeds `ContainedMeansConfinedAlways`) |
| Confinement | an Unattestable appraisal is recorded instead of refused (M_DOWNGRADE) | `NextInvD` (feeds `NoSilentDowngradeAlways`) |
| Confinement | an appraisal survives a fence (M_STALE always) | `NextInvF` (feeds `FreshAppraisalAlways`) |

## Run it

```sh
../../tools/install-lean.sh                       # the pinned toolchain, once, through elan; compares it with tools/LEAN-PIN
cd spec/lean
lake build                                        # the proofs; ~10 s
./results.sh > TopakSpec-results-<date>.txt       # clean build, digests, axioms, and the replay (~1 min); byte for byte
./graph-check.sh > GraphCheck-results-<date>.txt  # Seats and FloorComposition against TLC's state graphs (~2 min); byte for byte
../../tools/lean-sync.sh                          # every Lean results file against the tree and the pin
```

`TopakSpec-results-2026.10.05.txt` is the results file ADR-0053 cites. Its `Transcribes:` line binds each Lean
file to the digest of the TLA+ module it encodes, as a TLAPS results file's `Modules:` line does, and
`tools/lean-sync.sh` reads it as `spec/proof-sync.sh` reads those. When a module gets a successor, the successor's
encoding is a new file (`spec/proof-method.md` §6).
