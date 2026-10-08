# Specifications

TLA+ modules checked in TLC at small constants, each with the mutations that must fail and the reachability
witnesses that must be violated. **TLC's results are evidence, not proofs** (every checkpoint's §8); since G8 the
invariants of thirteen modules are also proved, under named hypotheses, by the proof modules below (ADR-0046), and
neither is a claim about the running reference. A module cited by digest
in an accepted record is frozen; a change is a successor module (`RulesFloorNV_rev5`, `Lease_A1`). Results files are
hand-assembled TLC output with a dated name and never change; the two generators regenerate one from a row list.
`tools/tla2tools.jar` is the checker, tracked for its digest, which results files print from 2026.09.30 on.

| Module | Record | Driver | Results | Cited by digest in |
|---|---|---|---|---|
| `RulesFloorBase.tla`, `RulesFloorNV.tla` | ADR-0026 §6 | `RulesFloorNV-run.sh` | `RulesFloorNV-results-2026.09.15.txt` | ADR-0026 |
| `RulesFloorNV_rev5.tla` | ADR-0026 R1; ADR-0024 rev 5 | `RulesFloorNV_rev5-run.sh` | `RulesFloorNV-rev5-results-2026.09.23.txt` | ADR-0026, ADR-0033 |
| `NonComposition.tla` | ADR-0013 §4 | `NonComposition-run.sh` | `NonComposition-results-2026.09.23.txt` | ADR-0013 |
| `Anchor.tla`, `BreakGlass.tla` | ADR-0029 §5 (two of the five bootstrap modules) | `bootstrap-run.sh` | `bootstrap-results-2026.09.23.txt` | ADR-0029 |
| `Lease.tla` | ADR-0031 §8 | `lease-run.sh` | `Lease-results-2026.09.23.txt`, `-25.txt` | ADR-0031 |
| `Lease_A1.tla` | ADR-0031 A1 | `Lease_A1-run.sh` | `Lease_A1-results-2026.09.28.txt` | ADR-0031 |
| `FloorComposition.tla`, `FloorRouting.tla` | ADR-0030 §9 | `floor-run.sh` | `FloorComposition-results-2026.09.24.txt` | ADR-0030, ADR-0033 |
| `Confinement.tla` | ADR-0034 §7, A1 | `confinement-run.sh`; `confinement-gen-results.sh` with a row list | `Confinement-results-2026.09.25.txt`, `-28.txt`, `-30.txt` | ADR-0034 |
| `Seats.tla` | ADR-0037 §9 | `seats-run.sh` | `Seats-results-2026.09.29.txt` | ADR-0037 |
| `Observers.tla` | ADR-0038 §8 | `observers-run.sh` | `Observers-results-2026.09.29.txt` | ADR-0038 |
| `Coupling.tla` | ADR-0039 §8 | `coupling-run.sh` | `Coupling-results-2026.09.29.txt` | ADR-0039 |
| `RunCoupling.tla` | ADR-0042 §8 | `runcoupling-run.sh` | `RunCoupling-results-2026.09.29.txt` | ADR-0042 |
| `RunSeats.tla` | ADR-0043 §8 | `runseats-run.sh` | `RunSeats-results-2026.09.29.txt` | ADR-0043 |
| `Emergency.tla` | ADR-0052 §9 (Proposed) | `emergency-run.sh`; `emergency-gen-results.sh` with a row list | `Emergency-results-2026.10.04.txt` | ADR-0052 |
| `BreakGlass_A1.tla` | ADR-0029 §5; ADR-0026 A2 (pending); ADR-0052 §9 (Proposed). Successor to `BreakGlass.tla` where it models X1 | `a1-run.sh` with `BreakGlass_A1-rows.txt` | `BreakGlass_A1-results-2026.10.05.txt` | none yet |
| `NonComposition_A1.tla` | ADR-0013 §4, A1 (pending); ADR-0052 §9 (Proposed). Successor to `NonComposition.tla` where it models X1 | `a1-run.sh` with `NonComposition_A1-rows.txt` | `NonComposition_A1-results-2026.10.05.txt` | none yet |
| `ToolList.tla` | ADR-0048 §8 (Proposed) | `toollist-run.sh`; `toollist-gen-results.sh` with a row list | `ToolList-results-2026.10.04.txt` | ADR-0048 |
| `Operators.tla` | ADR-0050 §10 (Proposed) | `operators-run.sh`; `operators-gen-results.sh` with a row list | `Operators-results-2026.10.04.txt` | ADR-0050 |
| `Correlator.tla` | ADR-0051 §10 (Proposed) | `correlator-run.sh`; `correlator-gen-results.sh` with a row list | `Correlator-results-2026.10.04.txt` | ADR-0051 |
| `Labels.tla` | ADR-0047 §11 (Proposed) | `labels-run.sh`; `labels-gen-results.sh` with a row list | `Labels-results-2026.10.03.txt`, `-2026.10.04.txt` | ADR-0047 |
| `Coupling_live.tla` | ADR-0039 §2; A12 (Theory of Operation §13); the liveness plan, Tier 1 item 1 (CR-37). Extends `Coupling.tla` without editing it: four leads-to properties, under fairness on the Observer's actions (A12), on the Thinker's `Admit` and on the grants, and two liveness mutations | `live-gen-results.sh` with `Coupling_live-rows.txt` | `Coupling_live-results-2026.10.07.txt` | none yet |
| `Emergency_live.tla` | ADR-0039 A2; ADR-0052 §9 (provisional, B34); the liveness plan, Tier 0. Extends `Emergency.tla` without editing it: the emergency call split into its admit and its refusal, two `ENABLED` invariants, two mutations | `live-gen-results.sh` with `Emergency_live-rows.txt` | `Emergency_live-results-2026.10.07.txt` | none yet |
| every module a `-deadlock` script checks, unmutated, at its results files' constants (`Operators` at two operators only) | the liveness plan's note on TLC's `-deadlock` flag ("Why it's worth the cost") | `deadlock-audit.sh` | `deadlock-audit-results-2026.10.07.txt` | none yet |
| `FloorComposition.tla`, `Coupling.tla`, `RunCoupling.tla` | ADR-0046 §5 (the premise-table corrections) | `premise-corrections-results.sh` | `premise-corrections-results-2026.10.02.txt` | ADR-0046 |
| `Mechanism.tla` | ADR-0045 T-0045-28; ADR-0033 A5 | `mechanism-trace-run.sh` on traces the reference records; `mechanism-trace-results.sh` regenerates the file; `trace2tla.py` converts | `Mechanism-trace-results-2026.09.30.txt`, `-2026.10.01.txt`, `-2026.10.02.txt`, `-2026.10.02b.txt`, `-2026.10.05.txt` (labels, operators and the emergency seating, all Proposed; X1 retired) | Pinned, not frozen: the operational model moves with the code |

**Liveness (2026.10.07).** `Coupling_live.tla` and `Emergency_live.tla` extend frozen modules, as a proof module does,
and add what they cannot state: fairness, leads-to properties, and invariants over `ENABLED`. Under every `Mut` of
the module it extends, each one's `NextL` is that module's `Next`, and under its own mutations a restriction of it,
so the state graphs and the safety results carry over (the proof modules below prove it). `live-gen-results.sh
<Module> <rows> "<title>"` regenerates either results file from a row list: a row is `name mut spec kind property
expected [CONST=value ...] [states=N]`, `kind` being `INVARIANT`, `PROPERTY` (TLC's liveness checker) or `DEADLOCK`
(the deadlock check on); each section ends with its verdict and whether it is the expected one, and the driver exits
non-zero otherwise. It runs TLC on one worker with a fixed fingerprint function, so that a liveness counterexample
is the same on every run. TLC's deadlock check is not a liveness check: in both modules every state has a
successor, so it reports nothing even under the mutation that stalls the next round for good. `deadlock-audit.sh`
asks the converse question of every module a `-deadlock` script checks: at the constants its results files use
(`Operators` at two operators only; three are beyond TLC), unmutated, every state with no successor is at a bound the
module imposes, and 28 of its 48 lines have none. No stray deadlock was found.

## TLAPS proofs

Thirteen modules also have deductive proofs, checked with the TLA+ Proof System (2026.10.02). Each proof module
extends a frozen module without editing it and proves the invariants that module states, for every value of its
constants that the named assumptions admit. A proof is bounded by its assumptions and the prover rather than by
constants, so it is a different kind of evidence from a TLC row. Mutations and reachability witnesses are
behaviours and stay with TLC; each proof module instead carries a lemma per mutation saying why it must fail. Where
a module has several mutations, each theorem takes as hypothesis only the mutations that break it, so the hypotheses
restate the "Breaks under" column of `theorem-premise-binding.md`, and a combined `SafeAlways` takes `Mut = "none"`.
ADR-0046 (Accepted 2026.10.02, Batch 25) declares the method, names the prover a trusted-base row (T-0045-31) and
cites every proof module and results file by digest; those are frozen from its ratification. The checkpoints' §8
describe the formal layer as TLC-checked until the next checkpoint is cut.

**Certified runs (2026.10.04).** `proof-cert.sh <Module>_proof > <Module>-proof-cert-results-<date>.txt` reruns a
proof module with Z3 replaced by `smt-checked` (cvc5 with proof production, each proof accepted by the ethos checker
the floor gates use before `unsat` is forwarded) and with Zenon's proofs checked by Isabelle, and accounts for every
obligation by the route that discharged it. Seventeen of the first twenty proof modules certify; `RulesFloorNV_rev5`,
`Confinement` and `Confinement_A1` do not, and their results files say why. The two added on 2026.10.05,
`BreakGlass_A1_proof` and `NonComposition_A1_proof`, certify (`-proof-cert-results-2026.10.05.txt`), which makes
nineteen of twenty-two. The two added on 2026.10.07, `Emergency_live_proof` and `Coupling_live_proof`, certify
(`Emergency_live-proof-cert-results-2026.10.07.txt`, `Coupling_live-proof-cert-results-2026.10.08.txt`), which makes
twenty-one of twenty-four; the first proves both its `ENABLED` invariants through Isabelle. Writing it found a defect in the prover's translation, and a review of the record a second: a term the prover does
not translate, an `ENABLED` or `\cdot` not expanded or a temporal formula, becomes a constant that drops any
variable bound around it, quantifiers being moved out of temporal bodies first; and every term it abstracts, and
every atom it hands LS4, is named by 20 bits of a hash it does not check, of a print that does not tell a bound
variable from a constant of its name, so that two terms can be one. Either way a false statement can prove and
certify, by the second through `PTL` too (`proof-certification.md` §8). `proof-scan.sh` says where to look for the
first in every proof module, checks every module for a collision of the hash by a run over renamed sources, and
reads every obligation as tlapm prints it for a capture (`proof-scan-results-2026.10.08.txt`); with a reading of
each step it lists, no proof module rests on either. §10 has the rules that avoid the first and a capture:
untranslated terms behind hidden definitions, and no definition expanded at an argument that names one of its bound
variables. Both are recorded against T-0045-31 (ADR-0046 A2, with ADR-0045 A3, ratified in Batch 37). `smt-checked-selftest.sh` checks the
wrapper against a dishonest solver. **`proof-certification.md` is the method**: what is checked and by what, how the
wrapper binds a proof to its query, how to read and reproduce a results file, what stays trusted, and how to write
proofs that certify. `proof-method.md` §5a has the first assessment.

`tools/tlapm` wraps the prover, which `tools/install-tlaps.sh` installs beside it (not tracked). `proof-results.sh
<Module>_proof` checks one proof module and prints its results file, with the digest of every module in the EXTENDS
chain and of the prover binary; `$TLAPM` overrides the binary, and the proof cache is removed when it finishes.
**The prover is pinned in `tools/TLAPS-PIN`** (2026.10.03, G9 item 73): the commit and binary digest every results
file cites, measured by the checkpoint manifests where the binary cannot be. The wrapper refuses a binary that does
not match it unless `TLAPM_UNPINNED=1` is set, and `proof-sync.sh` reports a results file that cites another prover.
The `1.6.0-pre` release tag is rebuilt by its upstream: on 2026.10.03 both assets carried commit `bfa9468`, not the
`7824dab` the results cite, so a fresh install does not yield the pinned prover; the pin file records both.

| Proof module | Over | Record | Theorems | Assumptions | Results |
|---|---|---|---|---|---|
| `RulesFloorNV_rev5_proof.tla` | `RulesFloorNV_rev5.tla` | ADR-0026 R1, R2, R5, R7, R9; ADR-0024 rev 5 | `P1_Unanimity` to `P9_NoSoloGrant`, each under the entry it rests on; the module's three ASSUMEs as theorems | `Active ⊆ AllEntries` | `RulesFloorNV_rev5-proof-results-2026.10.02.txt` |
| `NonComposition_proof.tla` | `NonComposition.tla` | ADR-0013 §4 | `NC1`, `NC2` | none | `NonComposition-proof-results-2026.10.02.txt` |
| `Anchor_proof.tla` | `Anchor.tla` | ADR-0029 §5 | `FloorPreserved`, `EpochMonotone` | `Active ⊆ AllEntries`, `MaxEpoch ∈ Nat` | `Anchor-proof-results-2026.10.02.txt` |
| `BreakGlass_proof.tla` | `BreakGlass.tla` | ADR-0029 §5; ADR-0026 R7 | `BreakGlassNeverChangesAuthority` | `Active ⊆ AllEntries`, `"R7" ∈ Active` | `BreakGlass-proof-results-2026.10.02.txt` |
| `FloorRouting_proof.tla` | `FloorRouting.tla` | ADR-0030 §9 | `NoWideningWithoutIssuance`, `FloorNeverVacuous` | none | `FloorRouting-proof-results-2026.10.02.txt` |
| `FloorComposition_proof.tla` | `FloorComposition.tla` | ADR-0030 §1, §4, §5 | all five: `AdmitImpliesFloorPermit`, `FloorErrorIsDeny`, `BundleRefusalHonored`, `BundleCannotWriteFloorInputs`, `EnvelopeHolds` | none | `FloorComposition-proof-results-2026.10.02.txt` |
| `Seats_proof.tla` | `Seats.tla` | ADR-0037 §9 | `OnlyThinkersAuthor`, `OneSeatPerPrincipal` | none | `Seats-proof-results-2026.10.02.txt` |
| `Observers_proof.tla` | `Observers.tla` | ADR-0038 §8 | `DenyByAnyOf`, `ReachIsBounded` | none | `Observers-proof-results-2026.10.02.txt` |
| `RunSeats_proof.tla` | `RunSeats.tla` | ADR-0043 §8 | `OnlyThinkersActuate`, `ObserversConsultAndReport`, `NoNameCrossesDomains` | none | `RunSeats-proof-results-2026.10.02.txt` |
| `Coupling_proof.tla` | `Coupling.tla` | ADR-0039 §8 | `NoAdmitWithoutLiveObserver`, `UnreadBounded`, `CorrelatorNeverGates`, for every K, R and MaxRound | `K, R, MaxRound ∈ Nat` | `Coupling-proof-results-2026.10.02.txt` |
| `RunCoupling_proof.tla` | `RunCoupling.tla` | ADR-0042 §8; ADR-0041 §2 | all five, including the `ENABLED` invariant `ConsultNeverCoupled`, for every K, R and MaxRound | `K, R, MaxRound ∈ Nat` | `RunCoupling-proof-results-2026.10.02.txt` |
| `Emergency_proof.tla` | `Emergency.tla` | ADR-0052 §9 (Proposed) | all six: a roster quorum behind every emergency lease, one round, a person as holder, no admit by an exception, the Thinker still coupled, every activation recorded | none | `Emergency-proof-results-2026.10.04.txt` |
| `BreakGlass_A1_proof.tla` | `BreakGlass_A1.tla` | ADR-0029 §5; ADR-0026 A2 (pending) | `EmergencyNeverChangesAuthority`, under `Mut # "M_SCOPE"` and `Mut = "M_KIND" => "R7" \in Active` | none: unlike its predecessor's, it does not assume R7 is in force | `BreakGlass_A1-proof-results-2026.10.05.txt` |
| `NonComposition_A1_proof.tla` | `NonComposition_A1.tla` | ADR-0013 §4, A1 (pending) | `NC1`, `NC2`, under none of the three mutations | none | `NonComposition_A1-proof-results-2026.10.05.txt` |
| `Labels_proof.tla` | `Labels.tla` | ADR-0047 §11 (Proposed) | all ten, the floor's minimum (`NoReadThenSend`, `NoSteeredDestination`) among them, and the step property `ClearSetOnlyGrows`, for every `MaxSeq` | `MaxSeq ∈ Nat` | `Labels-proof-results-2026.10.04.txt` |
| `ToolList_proof.tla` | `ToolList.tla` | ADR-0048 §8 (Proposed) | all five: `ToolListIsExact`, `ToldMatchesDecided`, `ListFixedForRound`, `OpeningRecordFirst`, `OpenedListIsTold` | none | `ToolList-proof-results-2026.10.04.txt` |
| `Operators_proof.tla` | `Operators.tla` | ADR-0050 §10 (Proposed) | all thirteen, including the `ENABLED` invariant `DenyAlwaysAvailable`, for every set of operators and every round bound | none | `Operators-proof-results-2026.10.04.txt` |
| `Correlator_proof.tla` | `Correlator.tla` | ADR-0051 §10 (Proposed) | all eight, including the `ENABLED` invariant `LagNeverGates`, for every set of Thinkers, shared targets and correlators and every bound | none | `Correlator-proof-results-2026.10.04.txt` |
| `Lease_A1_proof.tla` | `Lease_A1.tla` | ADR-0031 §4, A1 | all four: `LeaseAuthorityMonotone`, `NoActionUnderFencedEpoch`, `Rung0NeverContained`, `RevokedStaysStopped` | none | `Lease_A1-proof-results-2026.10.02.txt` |
| `Confinement_proof.tla` | `Confinement.tla` | ADR-0034 §7, A1 | all four: `ContainedMeansConfined`, `NoSilentDowngrade`, `ContestedStopped`, `FreshAppraisal`, for every rung at once | `Declared ∈ 0..3` | `Confinement-proof-results-2026.10.02.txt` |
| `Emergency_live_proof.tla` | `Emergency_live.tla`, extending `Emergency_proof.tla` | ADR-0039 A2; ADR-0052 (provisional, B34) | the two `ENABLED` invariants `EmergencyNeverCoupled` and `EmergencyCallsWithoutObserver`, under `Mut \notin {"M_EMCOUPLE", "M_EMCOUPLE2"}`; `SpecL => Spec` under every `Mut`, and with it `Emergency_proof`'s six for `SpecL`, each under its own hypothesis, and `SafeAlwaysL` under `Mut \in {"none", "M_EMCOUPLE", "M_EMCOUPLE2"}`; for every round bound | none | `Emergency_live-proof-results-2026.10.07.txt` |
| `Coupling_live_proof.tla` | `Coupling_live.tla`, extending `Coupling_proof.tla` | ADR-0039 §2 | `SpecL => Spec` under every `Mut`, and with it `Coupling_proof`'s three for `SpecL`, each under its own hypothesis, and `SafeAlwaysL` under `Mut \in {"none", "M_HBLIVE", "M_HBCOUPLED"}`, for every K, R and MaxRound. Not the four leads-to properties: they are owed, and TLC checks them (`Coupling_live-results-2026.10.07.txt`) | `K, R, MaxRound ∈ Nat` (`Coupling_proof`'s, restated) | `Coupling_live-proof-results-2026.10.08.txt` |

The thirteen of 2026.10.02 are cited by digest in ADR-0046, and frozen. **`proof-method.md`** records how they were written, the patterns they
share, the prover's habits, and a dated assessment of why they were cheap and where that stops.

### The modules in Lean 4

`lean/` (2026.10.05) re-encodes sixteen of the modules above as transition systems in Lean 4 and proves their
`*_proof.tla` theorems by induction on reachable states: `Seats`, `Observers`, `RunSeats`, `FloorRouting`,
`NonComposition`, `Anchor` and `BreakGlass`, with `RulesFloorBase`; `FloorComposition` (2026.10.06), which
`mechanism/lean/` proves the code's admit decision refines, step for step; `Seats`, which a model of
`State::apply`'s seat and lease arms in `mechanism/lean/` is proved to refine at the module's constants, with the
reference's recorded traces replayed through that model; `Coupling`, whose `UnreadBounded` is proved of a second
model of `apply` on the first, directly and not by refinement; and the parameterized ones, `Coupling` for
every K, R and MaxRound, `Lease_A1` for every epoch and fence bound, `RulesFloorNV_rev5` with its cardinalities
computed, and `Confinement` and `Confinement_A1` as one encoding under a flag, for every rung; and `Emergency`
with `Emergency_live` as one encoding (2026.10.06), for every `MaxRound`, with the unobserved emergency call that
`Emergency_proof` dropped proved of the frozen module's `Next`. `RulesFloorNV_rev5`, `Confinement` and
`Confinement_A1` are the modules the certified TLAPS run does not certify (`proof-certification.md`); in Lean every step of
them is kernel-checked, and the arithmetic the TLAPS proofs hand to SMT is `omega`. What this adds to the TLAPS proofs is the
temporal step: proof-method.md §5a counts 74 LS4 obligations, "holds initially, every step keeps it, so it
holds always", that the certified run checks with nothing; in Lean that step is an induction the kernel checks.
What it costs is a new premise, that the Lean encoding is the TLA+ module; a Lean theorem is of the encoding,
not of the frozen text, and the newest `lean/TopakSpec-results-<date>.txt` binds each encoding to the digest of the
module it transcribes. ADR-0053 (Batch 36) declares the method and makes the Lean kernel trusted-base row
T-0045-37, pinned in `tools/LEAN-PIN`. Every results file ends with a kernel replay (`tools/lean-report.sh`), because
`#print axioms` alone misses a declaration added past the kernel (`proof-method.md` §5b). `lean/README.md` has the
theorem table, the encoding conventions, and a mutation check; `lean/results.sh` regenerates the results file, byte
for byte; `tools/lean-sync.sh` is this package's `proof-sync.sh`, and covers `mechanism/lean/` and `floor/lean/` too.
Three encodings, `Seats`, `FloorComposition` and `Emergency` (with `Emergency_live`, at `MaxRound = 2`), are also
checked rather than only read: `lean/graph-check.sh` (`Seats`, `FloorComposition`) and `lean/graph-check-emergency.sh`
(`Emergency`, `Emergency_live`) have TLC dump each module's whole state graph under every `Mut` (`Emergency_live` under
`none` and its own two) and check, through a mirror proved equal to the encoding, that the two reach the same states
by the same steps with the same property values (ADR-0053 R6). Each writes its own results series,
`lean/GraphCheck-results-<date>.txt` and `lean/GraphCheckEmergency-results-<date>.txt`.

## Practice

What the modules, the runs and the proofs are expected to do, in the order a property passes through them. The
first item is what made the proofs cheap (`proof-method.md` §5); the rest are the checks, from the cheapest to the
most expensive, each with the kind of evidence it gives.

1. **Write the specification so its properties are local.** State a property as a flag the violating action would
   set, or as an append-only set of records the property quantifies over; put every mechanism check as a guard on
   the action that needs it. Keep domains finite and literal (two principals, three seats, kinds as record
   literals). Give each module one `Mut` switch, one guard per mutation, and a `Never…` witness for every claim that
   something is reachable. Carry a type invariant. Keep actions shallow: a guard, one `EXCEPT`, `UNCHANGED` for the
   rest. Leave constants unconstrained in the module and bound them in the run script. State no liveness unless the
   record claims it, and then write its fairness as conditions on actions, each named for whose obligation it is,
   with a row that drops each one: `Coupling_live.tla` does so for ADR-0039 §2's claim that the stall ends
   (2026.10.07). A liveness property also needs a variant and a WF1-shaped proof; for `Coupling_live` it is owed.
2. **Model-check at small constants** (every `*-run.sh`): every mutation fails its property, every witness is
   violated, `Safe` holds. This is non-vacuity and discrimination (ADR-0026 §6). The results file is dated, prints
   the jar's digest, and is regenerated by a generator script where one exists; it is never edited.
3. **Model-check separately at practical constants**: the same scripts with the values the records name as
   placeholders (ADR-0039 §1's table: `K = 8`, `R = 64`; three rounds; two epochs), into a results file suffixed
   `-medium`. A row that does not finish is recorded as such, with the time allowed. Not yet done for any module;
   the small-constant rows are the only exhaustive evidence so far.
4. **Simulate at large bounds, as time allows** (`simulate-run.sh`): TLC in `-simulate` mode, random behaviours to
   a depth, at constants exhaustive checking cannot reach. "No error sampled" is not a check and is never cited as
   one; the results file says `simulate` in its header with the depth, trace count and seed.
5. **Validate the reference's traces** (`Mechanism.tla`, `mechanism-trace-run.sh`): every recorded behaviour of the
   running code replayed through an operational model of `apply`, step for step. Drift detection, not a refinement
   (ADR-0045 T-0045-28).
6. **Prove the invariants** (`*_proof.tla`, `proof-results.sh`): each under the mutations that break it and the
   module's named assumptions, for every constant those admit. `proof-method.md` is the method; ADR-0046
   is the declaration. A proof replaces no mutation row: the existential claims stay with TLC.
7. **Keep the proofs in step** (`proof-sync.sh`): a proof results file names the digest of every module in the
   proof's EXTENDS chain as proved; the script compares them with the tree and lists base modules without a proof.
   A frozen module changes only as a successor module, and a successor gets its proof in the same commit. Proofs
   are not merged into the modules they prove: a base module is frozen by digest, TLC runs it without the prover's
   library, and the proof carries hypotheses the module must not (`proof-method.md` §7).
8. **Regenerate, never hand-edit.** Every results file comes from a script with the digests it prints; a hand
   edit is the one change a results file never takes.

**`theorem-premise-binding.md`** is the table ADR-0045 §3 owes: for every property above, the trusted-base rows,
degeneracy parameters and declared gaps it rests on, with the reference's inventory computed in its last column. **`theorem-premise-binding.json`** is the same table as a Boolean matrix with the parameter and gap
premises as columns; `inventory.py` evaluates a declaration against either, and `inventory.py --check` keeps the two in
step. Since 2026.10.06 `inventory.py` also evaluates **derived premises**, a named OR of premise sets, so that a theorem
proved twice is voided only when both routes are lost (ADR-0053 R7). The binding has carried them since ADR-0053's
ratification (Batch 36), which merged `theorem-premise-binding-ADR-0053.json` into it; `premise-routes.sh` shows what
they change for five declarations (`premise-routes-results-2026.10.06b.txt`; the 2026.10.06 file is the run before
the merge; `-2026.10.08.txt` is the same run, with the same verdicts, against `lean/GraphCheck-results-2026.10.07.txt`,
which names no `Emergency` file, since `Emergency`'s graph check has its own series; it also names `ADR-0045.md` at
the digest its A3 and E1 gave it as drafted, and `-2026.10.08b.txt` is the same again at their ratification in Batch
37).

Every `*-run.sh` and `simulate-run.sh` finds the jar at `../tools/tla2tools.jar` or `$TLA_JAR`; from `spec/` no
export is needed. TLC writes its metadata under `/tmp/tlc_<name>`.
