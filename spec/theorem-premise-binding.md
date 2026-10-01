# Theorem-to-premise binding

**2026.09.30**, revised 2026.10.01 (Batch 24: T-0045-14) · the table ADR-0045 §3 owes and ADR-0023 §2 assumes · DRAFT, revised with the records it binds

**What this is.** One row per checked property, naming what it rests on: the trusted-base rows (`T-0045-n`, ADR-0045
Annex A), the degeneracy parameters (ADR-0023 §6a values), and the gaps the corpus has declared and not closed. A
property **holds for a deployment** when every row it names is declared in that deployment's trusted-base
declaration as *delegated* or *trust root*, every parameter premise holds, and no gap premise is false for it. An
**excluded** row, an undeclared row (ADR-0045 §3, rule 1) or a refused component makes the premise false and the
property **void** for that deployment. That is ADR-0023 §2's inventory, theorems minus those whose premises are lost,
computed from this table instead of listed by hand. The last column computes it for the reference, against
ADR-0045 Annex B.

**What this is not.** A proof of anything. Every property here was checked by TLC at small constants, or restated
as a test, by the same hands that wrote the records (every checkpoint's §8). A row says what a check *assumed*; it
does not strengthen the check.

**Premises every row shares (BASE).** T-0045-1 (the replicas apply the ordered log as crash-fault machines),
T-0045-11 (the records are the records that were ratified), **T-0045-28** (the running code refines the checked
specification: no refinement exists, so for any running deployment every property below is conditional on this
row), T-0045-29 (TLC, at the constants run) and T-0045-30 (the build toolchain). They are not repeated per row.
Properties named `Never…` in the results files are reachability witnesses that must be *violated* (the non-vacuity
convention, G2 §3) and are not theorems; they are omitted here.

**Parameter premises** are written as the archetype value, with the degeneracy that falsifies them in brackets.
**Gap premises** are assumptions no row and no parameter carries: the corpus has declared them open.

| Theorem | Checked in | Record | Breaks under | Row premises | Parameter and gap premises | At the reference (Annex B) |
|---|---|---|---|---|---|---|
| `LeaseAuthorityMonotone` | `Lease.tla`, `Lease_A1.tla` | ADR-0031 §4, A1 | `M_RENEW`, `M_ROLE`, `M_LOWER` | BASE; T-0045-10 (rules issued, seats declared) | — | **holds** |
| `NoActionUnderFencedEpoch` | `Lease.tla` | ADR-0031 §5; ADR-0022 §2 | `M_FENCE` | BASE | — | **holds** |
| `Rung0NeverContained` | `Lease.tla` | ADR-0031 §3; ADR-0034 §4 | `M_RUNG` | BASE | — (true whatever the rung declaration) | **holds** |
| `RevokedStaysStopped` | `Lease.tla` | ADR-0031 §5 R3 | `M_REVOKE` | BASE; T-0045-10 | — | **holds** |
| `AdmitImpliesFloorPermit` | `FloorComposition.tla` | ADR-0030 §1 | `M_OVERRIDE` | BASE; T-0045-3 (the engine returns the semantics' decision) | floor verified [D-0030-1 drops the *proven* status]; the floor text is DRAFT, so the envelope it permits is the draft's | **holds**, of the draft floor |
| `FloorErrorIsDeny` | `FloorComposition.tla` | ADR-0030 §1 | `M_ERR` | BASE; T-0045-3 | floor verified [D-0030-1] | **holds** |
| `BundleRefusalHonored` | `FloorComposition.tla` | ADR-0030 §1 R4 | `M_FAILOPEN` | BASE; T-0045-6 (any bundle answer but an affirmative allow from the lease's revision is a deny); T-0045-27 (the bundle signer signs only what promotion admitted) | bundle signed [D-0044-1]: with an unsigned bundle the *revision* the lease names is a file name | **holds**; the revision is verified under the dev bundle key since 2026.10.01 (ADR-0033 A6) |
| `BundleCannotWriteFloorInputs` | `FloorComposition.tla` | ADR-0030 §4 | `M_WRITE` | BASE; T-0045-3 | — | **holds** |
| `EnvelopeHolds`, `FloorNeverVacuous` | `FloorComposition.tla`, `FloorRouting.tla` | ADR-0030 §5 | the non-vacuity controls | BASE; T-0045-3 | floor verified [D-0030-1]; the floor text is DRAFT | **holds**, of the draft floor |
| `NoWideningWithoutIssuance` | `FloorRouting.tla` | ADR-0030 §5 | `r-reach-incomp` and the routing controls | BASE; T-0045-3; T-0045-14 (the proof checker behind a `holds`; trust root since Batch 24) | **routing checked** (ADR-0030 §5 A1): a `holds` counts only with a proof the checker accepted; D-0030-2 where the gates run without it | **holds** at the reference since 2026.10.01: every routing `holds` in `floor/genesis-gates-results-2026.10.01.txt` carries a checked proof; the five earlier runs were D-0030-2 runs |
| `NC1`, `NC2` | `NonComposition.tla` | ADR-0013 §4 | the composition mutations | BASE; T-0045-2 (approval signatures); T-0045-12 (break-glass approvers); T-0045-3 (the exception and forensic entries as floor text) | rules floor R6, R7 in force | **holds** |
| `P1_Unanimity` | `RulesFloorNV_rev5.tla` | ADR-0026 R1; ADR-0024 | drop R1 | BASE; T-0045-10 (genesis rules satisfy the floor); T-0045-2; T-0045-9 (key-holders honest at threshold, for the issuance) | `quorum = "all"` [D-0024-1 voids it; R9 keeps D-0024-2 out] | **holds** at the dev rules; the dev rules are not genesis rules (G6) |
| `P2_TwoSeatsCounted` | `RulesFloorNV_rev5.tla` | ADR-0026 R2 | drop R2 | BASE; T-0045-10 | `minGrant ≥ 2` | **holds** |
| `P3_AuthorNotCounted` | `RulesFloorNV_rev5.tla` | ADR-0024 §6 | drop recusal | BASE | — (a mechanism constant) | **holds** |
| `P5_AnchorNotApprover` | `RulesFloorNV_rev5.tla` | ADR-0026 R5 | drop R5 | BASE; T-0045-9; T-0045-10 | — | **holds** |
| `P7_BGNoAuthority` | `RulesFloorNV_rev5.tla` | ADR-0026 R7 | drop R7 | BASE; T-0045-12 | — | **holds** |
| `P9_NoSoloGrant` | `RulesFloorNV_rev5.tla` | ADR-0026 R9 | drop R9 (binds only with R1 relaxed) | BASE; T-0045-10 | `quorum ≥ 2` when a threshold | **holds** |
| `FloorPreserved` | `Anchor.tla` | ADR-0029 §5 | `M_FLOOR` | BASE; T-0045-2; T-0045-8 (anchor keys secret); T-0045-9; T-0045-10 | — | **holds** |
| `BreakGlassNeverChangesAuthority` | `BreakGlass.tla` | ADR-0029 §5; ADR-0026 R7 | `M_SCOPE` | BASE; T-0045-2; T-0045-12 | — | **holds** |
| `ContainedMeansConfined` | `Confinement.tla` | ADR-0034 §4 | `M_HOST` (rungs 1, 2), `M_HW` (3), `M_CONTESTED`, `M_UNBOUND`, `M_PROFILE` | BASE; **T-0045-20** (the promoted image and profile); **T-0045-25** (the tool host, for P4); at rung 3 T-0045-16, T-0045-17; at rung 2 T-0045-18; at rung 1 T-0045-19 | confinement ≥ 1 [D-0034-1, -2 lower it; D-0034-4 is rung 0]; **the independence criterion in force** (ADR-0035, Proposed) | **void**: T-0045-16 to 21 absent, T-0045-22 excluded, the criterion not in force. `Contained` is empty |
| `NoSilentDowngrade` | `Confinement.tla` | ADR-0034 §3; ADR-0031 A1 | `M_DOWNGRADE`, `M_RENEWLOW` | BASE; the verdict's source at the declared rung (T-0045-17 at 3, T-0045-18 at 2, T-0045-19 at 1) | — (at rung 0 it holds trivially: ADR-0034 A1) | **holds trivially**, rung 0 being the declared rung |
| `ContestedStopped` | `Confinement.tla` | ADR-0034 §3 | `M_CONTESTED` | BASE; a measurement: T-0045-16 (3) or T-0045-18 (2) | confinement ≥ 2 (rungs 0 and 1 cannot produce *Contested*) | **void**: no measurement exists |
| `FreshAppraisal` | `Confinement.tla` | ADR-0034 §3 | `M_STALE` | BASE | confinement ≥ 1 | **void**: no appraisal exists |
| `OnlyThinkersAuthor` | `Seats.tla` | ADR-0037 §4 | `M_KIND` | BASE; T-0045-10 (seat kinds declared); T-0045-3 (B10, B6) | — | **holds** |
| `OneSeatPerPrincipal` | `Seats.tla` | ADR-0037 §1 | `M_SEAT` | BASE; T-0045-10 | — | **holds** |
| `DenyByAnyOf` | `Observers.tla` | ADR-0038 §5 | `M_QUORUM` | BASE | an Observer per cell [D-0037-1: no Observer; D-0038-1: the shared group only] | **holds** of the tally; the Observer is an e2e fixture |
| `ReachIsBounded` | `Observers.tla` | ADR-0038 §1 | `M_REACH` | BASE; T-0045-5 (the transport enforces the topic ACL `W(p)`) | — | **declared, not enforced**: no topic read ACL at the reference (G5 item 46) |
| `NoAdmitWithoutLiveObserver` | `Coupling.tla` | ADR-0039 §2 | `M_NOCOUPLE` | BASE; T-0045-4 (the clock, for the `T_obs` half); T-0045-3 (R3 as floor text; the values file) | coupling on [D-0039-1]; **gap:** the watermark is honest (ADR-0039 §5, collusion uncovered; A13) | **holds**, modulo the gap |
| `UnreadBounded` | `Coupling.tla` | ADR-0039 §1, §2 | `M_MARK`, `M_ROUNDS`, `M_NOCOUPLE` | BASE; T-0045-4; T-0045-3 | coupling on [D-0039-1]; `K < R`; **gap:** honest watermark | **holds**, modulo the gap; the values are placeholders |
| `CorrelatorNeverGates` | `Coupling.tla` | ADR-0039 §4 | `M_CORR` | BASE; T-0045-10 (a correlator declared with no cell) | a correlator exists [D-0038-2] | **holds** |
| `UnreadEffectsBounded` | `RunCoupling.tla` | ADR-0042 §2; ADR-0039 A1 | `M_EMITSEQ`, `M_MARK`, `M_ROUNDS`, `M_NOCOUPLE` | BASE; T-0045-4; T-0045-3; **T-0045-25** (the tool host, which the mechanism counts and records) | effects counted [D-0042-1]; coupling on [D-0039-1]; `K < R`; **gap:** honest watermark | **holds**, modulo the gap |
| `ConsultNeverCoupled` | `RunCoupling.tla` | ADR-0041 §2 | `M_COUPLEALL` | BASE; T-0045-3 (R3 names effects only) | the Run root is pinned (ADR-0040 §3): a live `Consult` would be egress | **holds** |
| `SealCountsEffects` | `RunCoupling.tla` | ADR-0042 §5 | `M_ROUNDS` | BASE; T-0045-25 | effects counted [D-0042-1] | **holds** |
| `RoundBoundCountsAll` | `RunCoupling.tla` | ADR-0042 §2 | `M_BOUNDEFF` | BASE | — | **holds** |
| `NoEffectWithoutLiveObserver` | `RunCoupling.tla` | ADR-0041 §2; ADR-0039 §2 | `M_NOCOUPLE` | BASE; T-0045-4; T-0045-3 | coupling on [D-0039-1]; **gap:** honest watermark | **holds**, modulo the gap |
| `OnlyThinkersActuate`, `ObserversConsultAndReport` | `RunSeats.tla` | ADR-0043 §2 | `M_KIND`, `M_OBSEMIT` | BASE; T-0045-10; T-0045-3 (B10 over `Actuate`) | — | **holds** |
| `NoNameCrossesDomains` | `RunSeats.tla` | ADR-0040 §2 | `M_DOMAIN` | BASE; T-0045-10 | — | **holds** |
| **Effect exclusivity** (no module) | restated as a claim | ADR-0015 E2; ADR-0022 §6; ADR-0042 §6 | — | BASE; **T-0045-16 to 22** (confinement at the declared rung); **T-0045-23** (native tools); **T-0045-24** (Run tools' channels); **T-0045-25** | confinement ≥ 1; Run's confinement delivered (ADR-0042 §6, Proposed) | **void**: A1 fails, T-0045-22 to 24 are excluded rows. Identical in strength to Moon & Varshney's assumed version (ADR-0015 E2) |
| **`PromotionMeetsIssuedQuorum`** (the `Promotion` module, owed) | `promotion.rs` tests only | ADR-0024; ADR-0029 §5 | — | BASE; T-0045-2; T-0045-9; T-0045-10; **T-0045-13** (gate evidence: excluded) ; T-0045-15 (the lineage tools, for A2.2) | A2.2 and A2.3 as tally constants; **gap:** no independence table (G18) | **gate evidence is an operator's assertion** (T-0045-13 excluded); A2.2 not built; the module is unwritten |
| `OneValuePerBallot`, chosen-unique, agreement | `topak-paxos` `sim.rs` (the `Voting` ghost) | ADR-0033 §2 | both simulated mutations | T-0045-1; T-0045-28 to 30 | — | **holds** of the simulation; the `Paxos` module the ToO calls for is unwritten (finding 9) |
| **The floor gates**: totality, non-vacuity, discrimination, entry matters, routing | `floor/run-gates.py` through `floor/cvc5-checked` | ADR-0030 §5 | the four negative controls and the three lying-solver controls | T-0045-3; T-0045-14 (trust root since Batch 24) | **routing checked** (ADR-0030 §5 A1): a `holds` from a solver query counts only with a checked proof; a `refuted` can only subtract | **pass** (2026.10.01): 4 `holds` on checked proofs, 25 `holds°` by cedar's own folding (T-0045-3), none unchecked; evidence tree `f8b1196a427a35ed` |
| **Trace validation** `TraceMatches` | `Mechanism.tla` over recorded traces | ADR-0033 A5; ADR-0045 T-0045-28 | a step that differs | T-0045-29; the three oracles (issuance validity, approval signatures, the parameter digest) | — | **21 traces match**; a harness, not a theorem; it is what makes T-0045-28's residual "every untested path" rather than "everything" |

**Reading the last column as an inventory.** At the reference, every theorem premised on confinement, gate evidence,
hermeticity or channel fidelity is void; the routing theorem and the gate verdicts rest on checked proofs since
2026.10.01, where before they were the solver's assertion; the bundle's revision is a file name; the reach bound is declared and not enforced. What remains holds of
the modules and, by trace validation, of the running code on every tested path: the lease, the fence, revocation,
composition, the rules floor, the bootstrap pair, seats, any-of, coupling with its collusion gap, Run's counters and
seal. That is ADR-0045 Annex B's inventory sentence, computed.

**Keeping it current.** A new property adds a row; a new T-row or degeneracy adds a premise; an ADR-0033 addendum
that changes a row's class at the reference changes the last column. `tools/check-refs.py` does not read this file;
the archetype-evolution record (G6 item 7) owns its versioning and the rule for a premise edge added into an existing
theorem, which weakens the theorem and needs its own record (ADR-0023 carried scope).
