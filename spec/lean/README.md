# The spec/ modules in Lean 4

Sixteen TLA+ modules of `spec/`, re-encoded as transition systems in Lean 4 and their TLAPS theorems proved
by induction on reachable states. The seven small finite-set modules: `Seats`, `Observers`, `RunSeats`,
`FloorRouting`, `NonComposition`, `Anchor` and `BreakGlass`, with `RulesFloorBase` as the last two's shared
base. `FloorComposition` (2026.10.06), the admit composition, which `mechanism/lean/Topak/FloorRefinement.lean`
proves the code's decision refines. `Seats` is also the target of `mechanism/lean/Topak/SeatsModel.lean`, a model
of `State::apply`'s seat and lease arms proved to refine it at the module's constants (2026.10.06). `Coupling`'s
properties are proved of `mechanism/lean/Topak/CouplingModel.lean` directly, at any size; that model does not refine
`Coupling.lean`. And the parameterized ones: `Coupling` for every `K`, `R` and `MaxRound`; `Lease_A1` for every epoch
and fence bound; `RulesFloorNV_rev5`, with its cardinalities computed over the five humans; and `Confinement`
and `Confinement_A1` as one encoding under a flag, for every rung. And `Emergency` with `Emergency_live`, which
extends it, as one encoding for every `MaxRound` (2026.10.07): the invariants of `Emergency_proof.tla` and
`Emergency_live_proof.tla`, two invariants over `ENABLED` among them, and in place of the lemma `Emergency_proof.tla`
dropped, `UnobservedEmergencyCallEnabledAlways`, of the frozen module's own `Next`. Each `TopakSpec/<Module>.lean` carries
the TLA+ it transcribes beside every definition and proves what `spec/<Module>_proof.tla` proves, with the
same inductive invariants and the same hypotheses on `Mut`.

## What this adds to the TLAPS proofs

`spec/proof-method.md` §5a: in the certified run, every obligation is closed by tlapm's normalization, by a
checked SMT proof, or by **LS4** for the temporal step of each theorem, "the invariant holds initially, every
step keeps it, so it holds always", which is checked by nothing. Here that step is `Prelude.invariant`,
an induction on `Reachable`, and the kernel checks it. The Lean theorems are therefore the TLAPS theorems with
the LS4 premise removed and a different one added: that the Lean encoding is the TLA+ module.

**Three of the sixteen TLAPS modules do not certify** under the checked backends (`proof-certification.md` §5a):
`RulesFloorNV_rev5`, where Isabelle refuses all five of Zenon's scripts (tlapm reports one; ADR-0053 E1, pending),
and `Confinement` and `Confinement_A1`, where three `TypeOK` steps each are proved by Z3 alone. All three are here,
every step kernel-checked. The arithmetic those proofs hand to SMT, and `Coupling`'s, is `omega`; `TypeOK` has no
counterpart; the `FiniteSetTheorems` facts about cardinalities are a count over five humans.

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
| `Emergency.lean` | `LiveHasRoundAlways`, `EmergencyLeaseHasARosterQuorumAlways`, `EmergencyLeaseIsOneRoundAlways`, `NoAgentHoldsAnEmergencySeatAlways`, `CallsAreAllowlistedAlways`, `ThinkerStillCoupledAlways`, `ActivationIsForensicAlways`, `SafeAlways`; `UnobservedEmergencyCallEnabledAlways`; of `Emergency_live.tla`: `nextL_next`, `SafeLAlways`, `nextL_iff_next`, `reachL_iff`, `EmergencyNeverCoupledValid`, `EmergencyNeverCoupledAlways`, `EmergencyCallsWithoutObserverAlways`, `EmergencyNeverCoupledIff`, `EmergencyCallsWithoutObserverIff` | any `m`; `m ∉ {M_NOQUORUM, M_REGRANT}`; `m ∉ {M_REGRANT, M_RENEW}`; `m ≠ M_AGENT`; `m ≠ M_X1`; `m ≠ M_UNCOUPLE`; `m ∉ {M_REGRANT, M_ERASE}`; `none`; any `m`; any `m`; `none`, `M_EMCOUPLE` or `M_EMCOUPLE2`; `m ∉ {M_EMCOUPLE, M_EMCOUPLE2}` (three times); `NoCoupledRound`, that no round in which the seat can be live is coupled (`MaxRound = 0` under `M_EMCOUPLE`, `MaxRound ≤ 1` under `M_EMCOUPLE2`), twice; each `…Iff` says its property holds exactly when `NoCoupledRound` does. Every `MaxRound` |

Each file also carries the TLAPS module's "why the mutation must fail" lemmas where they are about the
definitions rather than about a TLC run. Witnesses stay with TLC.

`Emergency.lean` departs from the rule that the inductive invariants are the TLAPS proof's in two places, each the
encoding's own: `Decided`, that membership in the tool sets and in the approvals is decided, so that
`CallsAreAllowlisted`'s step cases on `EmCall`'s `IF` without `Classical.choice`; and `RoundBounded`, for the
`ENABLED` theorems. Their other invariant, `EnvelopeHasTe`, is `Emergency_live_proof.tla`'s. Its two `ENABLED` theorems take `NoCoupledRound`, weaker than excluding
the two coupling mutations, and the `…Iff` theorems prove it is exactly what they need. Where `Emergency_live_proof.tla`
says `…AlwaysL`, the file proves the `Spec` theorem and carries it to `SpecL` by `reachL_reach` (`SafeLAlways` is
`SafeAlwaysL`; `results.sh` lists theorems ending in `Always`).

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
of their branches; and `seal` renamed `seals`, since `seal` is a Lean keyword. `TopakSpec/Temporal.lean` gives
`Enabled A s := ∃ s', A s s'`, TLA+'s `ENABLED A`, which an invariant over `ENABLED` asks of an action; such an
invariant is still proved by `invariant`. Behaviours and fairness come with the leads-to proofs.

## What it rests on

- **The Lean 4 kernel**, toolchain `lean-toolchain` (`leanprover/lean4:v4.33.1`, the one `tools/LEAN-PIN`
  names). No Mathlib, no dependencies. `#print axioms`: `propext` and `Quot.sound` at most for fourteen modules;
  `NonComposition` also uses `Classical.choice`, because its `Erase` step cases on a set membership, as TLA+
  does, and so does `Emergency`'s `nextL_iff_next`: stated over every pair of states, `Emergency_live`'s `NextL`
  being `Next` implies excluded middle (`nextL_iff_next_needs_em`, which uses no axioms), and `reachL_iff` states it
  over the reachable states without it. No `sorry`.
- **The replay.** Every results file ends with `leanchecker --fresh`, which replays every constant the package
  reaches, Lean's own library included, through the kernel in a fresh environment (`tools/lean-report.sh`).
  `#print axioms` alone misses a declaration added with the kernel check off; the replay refuses it
  (`spec/proof-method.md` §5b). It is the same kernel in a fresh process, not an independent checker.
- **The row.** ADR-0053, ratified 2026.10.06 (Batch 36), declares the method and makes the kernel and toolchain
  trusted-base row T-0045-37, pinned in `tools/LEAN-PIN`. A Lean result is cited by the results file ADR-0053 §4 names.
- **The encoding.** A proof here is of the Lean re-encoding, not of the frozen TLA+ text, which the TLAPS
  proofs are of. The encoding is written from the module and read against it; ADR-0053 §2 names this as the
  premise the method adds. Where the encoding could be read two ways, the file says which was taken. For `Seats`,
  `FloorComposition` and `Emergency` with `Emergency_live` it is also checked, below.

## The encodings checked against TLC's state graphs (2026.10.06)

`Seats` and `FloorComposition` are the modules the code-level work in `mechanism/lean/` refines, so their encodings
carry the most. `Emergency`, with `Emergency_live`, is checked because its `ENABLED` theorems claim that a step
exists: an encoding laxer than the module could prove one the module does not satisfy (2026.10.07). `TopakSpec/Mirror/` gives each a mirror: a concrete state with Booleans for the encoding's `Prop`s
and Boolean functions for its sets, a map into the encoding's states, and a list of successors, with these proved:

| Theorem | Claim |
|---|---|
| `next_iff` | from a mirrored state, the encoding's `Next m` reaches exactly the mirrored states in the successor list |
| `init_iff` | a state satisfies the encoding's `Init` exactly when it is the mirror's initial state |
| `eqC_iff` | the mirror's equality is equality of the encoding's states |
| one `*_iff` per property | each property, as a Boolean, equal to the encoding's |
| `nextL_iff` | the same as `next_iff`, of `Emergency_live`'s `NextL` (`Mirror/Emergency.lean`) |
| `enabled_iff` | `ENABLED EmAdmit(t)` at a mirrored state is a Boolean, the action's guard (`Mirror/Emergency.lean`) |

`graph-check.sh` has TLC dump the whole state graph (`-dump dot`) of `Seats` and of `FloorComposition` under every
`Mut`, and `graph-check-emergency.sh` that of `Emergency` under every `Mut` and of `Emergency_live` under `none` and
its own two. Each goes through a wrapper module whose one derived variable carries every property's value, so the
graph's shape is unchanged. `dot2lines.py` reads the dump, and `graphcheck` (`GraphCheck.lean`) or
`graphcheck-emergency` (`GraphCheckEmergency.lean`) evaluates the mirror on it, through the reading and the check the
two share (`GraphCheckCore.lean`). It checks that every TLC edge is a `Next` step, that every `Next` step from a TLC
state is a TLC edge or a stutter, that the initial states are the encoding's `Init`, and that every property has
TLC's value in every state. `Emergency_live`'s two properties over `ENABLED` ride in that variable like the others,
and its rows are of its `SpecL`, so the relation checked there is `NextL`.

Since 2026.10.07 `Emergency`'s check has a results series of its own, `GraphCheckEmergency-results-*.txt`. The
premise binding takes `enc-faithful(Seats)` and `enc-faithful(FloorComposition)` from the newest
`GraphCheck-results-*.txt`, and only while every file it names is as the tree has it, so a file that also named
`Emergency`'s files would make those two premises false whenever one of them changed. The two series still share
`Prelude.lean`, `GraphCheckCore.lean`, `dot2lines.py`, `lakefile.toml` and `lean-toolchain`, and an edit to any of
them stales both; `lakefile.toml` holds both checkers' stanzas, since one Lake package builds them.

`GraphCheck-results-2026.10.06.txt`: all eight graphs MATCH, from 128 states (`FloorComposition`, `none`) to 53,248
states and 442,368 edges (`Seats`, `M_KIND`). Both encodings fix the module's constants in their types, so a graph
is every state the encoding can reach: the encoding and the module reach the same states by the same steps, with
the same property values. The mirrors are proved; the evaluation, TLC's dump and its parse are a test.

`GraphCheck-results-2026.10.07.txt` checks the same eight graphs, every row line for line as in 2026.10.06's; its
`Sources:` line adds `Prelude.lean`, `GraphCheckCore.lean` and `lean-toolchain`, and it names no `Emergency` file.
`GraphCheckEmergency-results-2026.10.07.txt` checks `Emergency` and `Emergency_live`: eleven graphs, all MATCH, up
to 92,288 states and 873,728 edges (`Emergency`, `M_AGENT`). `Emergency` under its eight values of `Mut` has the state counts
of `Emergency-results-2026.10.04.txt`, 25,728 under `none`. `Emergency_live` is checked under `none` (25,728 states,
`Emergency`'s), `M_EMCOUPLE` (16,768) and `M_EMCOUPLE2` (25,728). Under the two coupling mutations `NextL` is not
`Next`, and its two properties over `ENABLED` are false in 4,160 and 5,120 states, each with TLC's value. Under
Emergency.tla's seven mutations `NextL` is `Next` (`nextL_iff_next`, `reachL_iff`) and both properties hold in every
state, so those rows would repeat `Emergency`'s. The `Emergency` mirror fixes `MaxRound = 2`, the value the TLC
results use: the encoding's theorems are for every `MaxRound`, and the check covers `MaxRound = 2` only.

Three mutated TLA+ modules, each checked against the unchanged encoding, each failed:

| Mutant | What the check found |
|---|---|
| `Grant` without "the seat has no live lease" | 3,552 TLC edges that are not `Next` steps. Both invariants still hold of it, so no proof sees it |
| `Seal` that never fires | 64 `Next` steps that are not TLC edges |
| `OnlyThinkersAuthor` without its `Vote` clause | the property's value differs on 6,656 states |

Three mutated copies of the `Emergency` encoding, each with its mirror changed to match and re-proved against it,
checked against the kept graphs (`GRAPHS_KEEP`, `GRAPHCHECK`) in scratch copies, each failed:

| Mutant | What the check found |
|---|---|
| `Activate` without `~em.live` (laxer) | `Next` steps that are not TLC edges on all eleven graphs: 1,280 under `none`, up to 5,120 under `M_NOQUORUM` and `M_AGENT`. Every theorem of `Emergency.lean` still proves, so no proof sees it |
| `EmCoupled` read as false: `EmAdmit` ignores the coupling (laxer) | under `M_EMCOUPLE`, 9,920 `NextL` steps that are not TLC edges, and both `ENABLED` properties differ from TLC's on 4,160 states; under `M_EMCOUPLE2`, 10,496 and 5,120. The `none` rows and `Emergency`'s eight MATCH |
| `Activate`'s holder bound `Persons` under every `Mut` (stricter) | under `M_AGENT`, 7,872 TLC edges that are not `Next` steps, the activations that seat the agent. No proof sees it |

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

Eleven more were built for `Emergency` (2026.10.06), in scratch copies, as all the mutants above were; none is
committed. A lemma whose proof fails although its statement still holds in the mutant, because its proof names the
mutated guard, is not listed.

| Module | Mutant | Fails in |
|---|---|---|
| Emergency | `EmAdmit` needs a live Observer under every `Mut` (M_EMCOUPLE always) | `EmergencyNeverCoupledValid`; `uncoupled_live` (feeds `EmergencyNeverCoupledAlways`, `EmergencyCallsWithoutObserverAlways` and both `…Iff`); `emCall_split` (feeds `nextL_iff_next`, `reachL_iff`); `nextL_next`. `UnobservedEmergencyCallEnabledAlways` still holds: it is of Emergency.tla's own `EmCall` |
| Emergency | coupled from the second round under every `Mut` (M_EMCOUPLE2 always) | the same lemmas |
| Emergency | Emergency.tla's `EmCall` needs a live Observer | `UnobservedEmergencyCallEnabledAlways`; `nextL_next` (Emergency_live's `EmAdmit` is then no longer an `EmCall`) |
| Emergency | `Activate` ignores the quorum (M_NOQUORUM always) | `NextQuorum` (feeds `EmergencyLeaseHasARosterQuorumAlways`) |
| Emergency | `Activate`'s envelope without te | `NextSeatInv` (feeds `UnobservedEmergencyCallEnabledAlways` and the two `ENABLED` theorems). All three still hold, re-proved from t1, which is in force from `Init` on and so in every envelope; TLC agrees (18,048 states). Only Emergency.tla's witness `NeverEmergencyOnlyTool` catches it |
| Emergency | an agent may be seated (M_AGENT always) | `NextHolder` (feeds `NoAgentHoldsAnEmergencySeatAlways`) |
| Emergency | R3 dropped for the Thinker (M_UNCOUPLE always) | `NextCoupled` (feeds `ThinkerStillCoupledAlways`); `nextL_next`, whose held-back emergency refusal is matched by the Thinker's R3 refusal |
| Emergency | an activation record erasable under `none` (M_ERASE always) | `NextForensic` (feeds `ActivationIsForensicAlways`) |
| Emergency | a renewal under `none` (M_RENEW always) | `NextOneRound` (feeds `EmergencyLeaseIsOneRoundAlways`) |
| Emergency | an operator's regrant under `none` (M_REGRANT always) | `NextQuorum`, `NextOneRound`, `NextForensic`: the three Emergency.tla says M_REGRANT must break |
| Emergency | X1 left in the floor (M_X1 always) | `NextAllowlisted` (feeds `CallsAreAllowlistedAlways`) |

## Run it

```sh
../../tools/install-lean.sh                       # the pinned toolchain, once, through elan; compares it with tools/LEAN-PIN
cd spec/lean
lake build                                        # the proofs; ~10 s
./results.sh > TopakSpec-results-<date>.txt       # clean build, digests, axioms, and the replay (~1 min); byte for byte
./graph-check.sh > GraphCheck-results-<date>.txt  # Seats and FloorComposition against TLC's state graphs (~2 min); byte for byte
./graph-check-emergency.sh > GraphCheckEmergency-results-<date>.txt  # Emergency and Emergency_live, the same (~4 min); byte for byte
../../tools/lean-sync.sh                          # every Lean results file against the tree and the pin
```

`TopakSpec-results-2026.10.06b.txt` is the results file ADR-0053 §4 cites (2026.10.05's was the first it cited);
newer ones add `Emergency`. Its `Transcribes:` line binds each Lean
file to the digest of the TLA+ module it encodes, as a TLAPS results file's `Modules:` line does, and
`tools/lean-sync.sh` reads it as `spec/proof-sync.sh` reads those. When a module gets a successor, the successor's
encoding is a new file (`spec/proof-method.md` §6). A module that extends a frozen one without replacing it, as
`Emergency_live.tla` extends `Emergency.tla`, is encoded in the same file, and the `Transcribes:` line names both.
