# TOPAK — Genesis Checkpoint G6

**2026.09.30** · genesis custodian: Scott, (1, 0) · supersedes G5 (`19383cbbc6c191d1`) as the state of record · narrative: `topak-theory-of-operation-2026.09.30-rev10.md`, cut with this checkpoint

**What G6 is.** The state of record, as G5 was: what each record says, what was ratified and by whom, what is owed,
and what is open. Revision 10 of the Theory of Operation is cut from this checkpoint and narrates it; where the two
disagree, this document wins.

**What changed at G6.** G5 froze a corpus whose Run half followed two provisional names, whose trusted base was owed
rows by six records and enumerated by none, and whose solver, bundles and gate evidence were trusted by habit. In
one day, five batches: the seven easy wins of the 09.28 prioritization taken as amendments and ratified with a new
record for bundle signing (**Batch 17**); ADR-0021 ratified after eighteen days Proposed (**18**); two reference
addenda (**19**, **21**); and **Run's alphabet in force**, ADR-0040 to ADR-0043 with the three amendments they
needed (**20**). **The trusted base has a record** (ADR-0045, Proposed): an admission rule, thirty rows for the
archetype, and the reference's own declaration, which when applied to the corpus's own gate refused the solver
(ADR-0030 A1, pending). **The first mechanized link between `spec/` and `mechanism/` exists**: every behaviour the
reference's tests exercise, replayed through an operational model of its state machine, 21 traces and 163 steps
matching (ADR-0033 A5). Two things are new in kind: three records were drafted by the assistant at the custodian's
request and settled by the custodian's ratification or revision, and a record caught its own first draft claiming
proof where the corpus claims evidence. **Every lease the reference issues is still rung 0. Nothing is
`Contained`.** The bootstrap trigger is still unmet, and remains optional.

---

## 1. Ratification record

All by the genesis custodian under ADR-0029 §2.

| Batch | Date | Contents | Notes |
|---|---|---|---|
| **17 · Easy wins** | 09.30 | ADR-0034 A1 · ADR-0025 A1 · ADR-0031 A2 · ADR-0003 A3 · ADR-0033 A3 · **ADR-0044** (C1) | A1 of 0034: the rung-0 row of the property check. A1 of 0025: §1 item (f), the keys that vouch for artifacts. A2 of 0031: `ttl ≤ T_persona`. A3 of 0003: 0003.7 scoped to the store, not the length, **ratified as a scoping and not a reversal** (the row says where C3 would go). A3 of 0033: the second 09.29 run, ratified while every record it followed was Proposed. ADR-0044, bundle signing, drafted by the assistant; every drafter's choice settled by ratification |
| **18 · ADR-0021** | 09.30 | 0021 at R5 (C4) | Build emits to the effect stream; Build has an Observer. R5 is the read-through for ADR-0008 vocabulary its Status note required. C4 because ADR-0039 §3 rests on its §3 seal. ADR-0038 finding 4 closed (dependent entry) |
| **19 · Reference** | 09.30 | 0033 A4 | The tree after Batches 17 and 18: the values pin, the register, the README, no behaviour change. Cited commit amended for its message before ratification; the row says so |
| **20 · Run** | 09.30 | **0040** (C3, C4) · **0041** at R1 (C1, C4) · **0042 §1–§5, §7, §8** (C4) · **0043** (C4) · 0022 A2 (C3) · 0037 A1 · 0039 A1 | As drafted. Four custodian decisions recorded in the rows: no C3 on ADR-0041 or ADR-0039 A1; ADR-0042 §6 left Proposed, as ADR-0022 §6 was at B2; `Consult` kept on the observer seat; ADR-0043's scripted Run cell carried as a debt, the e2e fixture being the evidence, as at B14. ADR-0033 A3's revision clause not triggered. Dependent entries in 0030, 0033, 0034 |
| **21 · Reference** | 09.30 | 0033 A5 | Trace validation. The first addendum to discharge any part of the refinement debt ADR-0045 assigns the record, and only stage 1 of it |

### 1.1 Record status at G6

| Status | Count | Records |
|---|---|---|
| Accepted (genesis) | 18 | 0001, 0002, 0004, 0007, 0010, 0012, 0016, 0017, 0018 (in part, §1.2), 0019, 0020, 0022 (in part, §1.2), 0024, 0025, 0026, 0027, 0032, 0033 |
| Accepted (genesis) · confirmation required | **20** | 0003 (for A2 only), 0006, 0009, 0013, 0015, **0021**, 0023, 0028, 0029 (for A2 only), 0030, 0031 (C2 for A1 only, beside its C1), 0034, 0037, 0038, 0039, **0040, 0041, 0042 (in part, §1.2), 0043, 0044** |
| Proposed | 4 | 0005, 0035, 0036, **0045**; and ADR-0042 §6 |
| Superseded | 1 | 0008, by 0038 |
| Tombstone | 1 | 0011 |
| Reserved, no file | 1 | 0014 |

44 record files, numbered to 0045. 0014 is the only reserved number.

**Two pending amendments.** ADR-0026 A1 (R8, the break-glass TTL), drafted 2026.09.24, none of its four conditions
met (§7, item 8). **ADR-0030 A1** (a routing verdict counts only with a checked proof; D-0030-2), drafted 2026.09.30
for ADR-0045 finding 1 (§7, item 54). Every other `Pending:` field reads none.

### 1.2 What is ratified in part, or with a scoped marking

**ADR-0022.** §1–§5, §7 and §8 are Accepted, **§6 is not**. A2 (Batch 20, C3) applied inline in §5: the carrier is
common, no variant name is.

**ADR-0042.** §1–§5, §7 and §8 are Accepted, **§6 is not**: Run's confinement obligation, stated and not delivered,
left out by the custodian as ADR-0022 §6 was. C2 would attach to §6 only. It waits on the Run profile (item 26) and
an owner for channel fidelity (G19).

**ADR-0018 is reversed in part, not superseded** (ADR-0037 §3), unchanged since G5.

**ADR-0024 A2 is in force in the record and in part in the reference**: A2.2 is still G18, unchanged since G5.

**The four markings scoped to an amendment** stand: ADR-0003 A2 (C1), ADR-0029 A2 (C3), ADR-0031 A1 (C2), ADR-0035
R2's custodian marking. **ADR-0003 A3 carries none**, on the custodian's reading that it scopes 0003.7 and reverses
nothing; its B17 row names the alternative.

**Three records were drafted by the assistant**, at the custodian's request, each marking every choice as the
drafter's: ADR-0044 (ratified, Batch 17), ADR-0045 (Proposed, revised four times on the day) and ADR-0030 A1
(pending). The custodian settled ADR-0044's choices by ratifying the text. ADR-0029 has no criterion for this kind
of authorship; §4 carries it as a ledger line beside ADR-0035 R2's.

---

## 2. The floors as ratified

### 2.1 The rules floor

Unchanged since G2 in its entries: **R1, R2, R5, R6, R7, R9**; R3 and R4 withdrawn; **R8** pending. The check owed
against it at G5, ADR-0026 §6's non-vacuity run with A2.2 and A2.3 modeled, is still owed (§7, item 39). ADR-0025 §1
gained item (f) in Batch 17, the keys that vouch for artifacts; the floor is unchanged by it, since an (f) key is not
a seat and casts no vote.

### 2.2 The policy floor

**Changed three times since G5, and still DRAFT.** Three gate runs, every ADR-0030 §5 gate passing in each:

| Run | What changed | Policies | Cases | Digests |
|---|---|---|---|---|
| `genesis-gates-results-2026.09.29-adr0041.txt` (ADR-0040 §7, ADR-0041 §7; then Proposed, ratified Batch 20) | `Consult`, `Actuate`, `Report` in S; `RunCtx.corpusRoot` becomes `runRoot`; **R4-consult-pinned** new; R1, R2, R3, B10 and X1 restated over the new names; two controls added, a permit-all on `Consult` and R4 without its root condition, the second caught by routing and not by non-vacuity (ADR-0041 R1) | 17 | 62 | floor `28ec0e4552c6a915`, schema `0ec2fa215eefe136`, values `468992e45b1d7d04` |
| `genesis-gates-results-2026.09.30.txt` (ADR-0031 A2) | `persona.T_persona_ms` joins the values file. Floor and schema unchanged; every result identical below the header | 17 | 62 | values `85ab6fefb66f0316` |

**The floor bundle is three files**, as at G5. **Every number in the values file is a placeholder**: `T_obs` 5000 ms,
`K` 8, `T_persona` one hour, unset θ. `T_persona` is not yet read by the reference (item 55).

### 2.3 Confinement

Unchanged in force since G4: ADR-0034 Accepted, ADR-0036 Proposed. **ADR-0034 A1** (Batch 17) adds the rung-0 row
to §7: the deployment D-0034-4 declares produces no `Contained` effect, checked rather than declared; finding 6
records that the module reads a launch measurement at rung 0 under `M_HOST`, which waits for a successor module.
**ADR-0036 R2** points finding 1 at ADR-0035 R4: the ingress bound covers the guest's reads and not a tool's, so a
training round under the launcher stays declared until an in-guest trainer image exists. **Run's half of the
obligation now has a record and no mechanism**: ADR-0042 §6 (Proposed) says P4 cannot hold for a Run tool and channel
fidelity replaces it; nothing checks it (G19). **`Contained` still has no members at any rung.**

### 2.4 The LTRO

Unchanged in substance since G5. **ADR-0037 A1** (Batch 20) strikes the provisional Run column: a `thinker` seat holds
`Consult`, `Actuate` and `Report`, an `observer` seat `Consult` and `Report`, and the Listener's Run list is the task,
each admitted `Consult`'s content and each admitted `Actuate`'s result. **ADR-0039 A1** (Batch 20): in Run the
sequence counts effect-bearing admits and the coupling is over them; `Consult` is not coupled; `UnreadEffectsBounded`
joins D-0039-1's properties lost.

### 2.5 Run

New at G6. **ADR-0040**: three variants, `Consult` as ingress over a pinned Run root, `Actuate` and `Report` as
ADR-0015's two effect classes, no name shared with Build, no terminal variant, fourteen obligations assigned by
owner; ADR-0022 A2 is its reversal. **ADR-0041**: one envelope per variant, R4 new, R3 restated over effects and not
extended to `Consult`, break-glass reaching `Actuate` only, argument constraints in the bundle tier; its finding-12
revision applied before ratification. **ADR-0042 §1–§5**: the effect counter, the mechanism-written `Actuate` record
with its `unknown` outcome ahead of the seal, a tool's result as recorded ingress, the round sealing when the lease
ends and a Run seat refused abstention; D-0042-1 is the reference before 09.29. **ADR-0043**: the Listener's three
deliveries, alphabets by seat kind, the decoder's target, the Observer's mark over the effect sequence, the Observer's
lease reaching the seal, the correlator uncoupled. The reference implemented all of it on 09.29 under ADR-0033 A3,
before the records were ratified, and the addendum needed no revision when they were.

### 2.6 The trusted base

New at G6, and **Proposed**. ADR-0045 writes the rule for entering the trusted base and the archetype's table. The
rule is the corpus's delegation test stated once, in ADR-0015's terms: a component is a row only if its failure can
produce only subtractions (**delegated**), or its failure can add authority and an issuance or a promotion fixes its
identity and its own record admitted it (**trust root**); a component relied on and trusted for nothing is an
**excluded** row, so the theorems on it compute void; anything else is **refused**. Rows are premise nodes in the
theorem DAG, an undeclared row is false, and removing a row is a tightening while adding one needs its own record.
Annex A has thirty rows in five groups; Annex B is the reference's own declaration and ends with the inventory that
leaves it. Applied to the 09.28 prioritization's eight delegations: two trust roots, two delegated, two excluded,
one not a row, **and the solver refused** (finding 1, routed to ADR-0030 as A1). R1 took the TCB comparison's
correction, that what runs is a row: the implementation as a refinement of the specification, the model checker and
the build toolchain, T-0045-28 to 30. R2 made the refinement gap a debt ADR-0033 owns. R3 recorded the TLC jar's
digest. R4 recorded stage 1 of the chain.

### 2.7 Bundle signing

New at G6. **ADR-0044** (Batch 17, C1): a bundle is trusted by its signature, not its file name; the key is carried
in the issued rules under ADR-0025 §1 (f); the signature covers the content revision; the mechanism loads a bundle
only when it verifies, counts a sidecar's decision only from a verified revision, and refuses a grant naming an
unverified one; signing happens at promotion. D-0044-1 is the reference today: the implementation is owed (item 55).

---

## 3. Verified artifacts

G5's artifacts keep their digests. New since G5:

| Artifact | SHA-256 (16) | Records | Result |
|---|---|---|---|
| `spec/RunCoupling.tla` | `781fdbc135f37491` | ADR-0042 §8 | Five properties over three actions. `UnreadEffectsBounded`, `ConsultNeverCoupled`, `SealCountsEffects`, `RoundBoundCountsAll` and `NoEffectWithoutLiveObserver` hold; **`M_EMITSEQ` breaks the first and the third only, and is the reference before 09.29**; `M_COUPLEALL` breaks only the exemption; `M_ROUNDS` and `M_MARK` carried over; three witnesses fire |
| `spec/RunSeats.tla` | `1bb49475ab59f6de` | ADR-0043 §8, ADR-0040 §2 | `OnlyThinkersActuate`, `ObserversConsultAndReport`, `NoNameCrossesDomains` hold; `M_KIND`, `M_DOMAIN` break what they should; `M_OBSEMIT` is the provisional column |
| `spec/Confinement.tla` at `Declared = 0` | `d0dcf21ce9774885` (unchanged) | ADR-0034 A1 | `Safe` and `NeverContainedEffect` hold, `NeverContested` holds as at rung 1; finding 6 under `M_HOST` |
| **`spec/Mechanism.tla`** | `73e1ceecff13437d` | ADR-0045 T-0045-28; ADR-0033 A5 | An operational model of `State::apply` and `check_live`. **Trace validation, 2026.09.30: 21 traces, 163 applied entries, every step's projected state and result matching** (`Mechanism-trace-results-2026.09.30.txt`). Pinned, not frozen: it changes with the code |
| The floor, two runs | `28ec0e4552c6a915` / `0ec2fa215eefe136` / `468992e45b1d7d04`, then values `85ab6fefb66f0316` | ADR-0041 §7; ADR-0031 A2 | §2.2. All gates pass in both |
| Reference, three runs | manifests `8409d2365589ada1` (`1e6c0c4`, 65 entries), `edb5fe3851c26c4c` (`fb40db1`, 65), `944fffcee2fac170` (`8cf9bd1`, 66) | ADR-0033 A3, A4, A5 | 55 tests across six binaries in each; 31 Rego cases at the first. Twenty-four files changed under ADR-0040 to ADR-0043; four under Batch 17 with no behaviour change; eight for the trace recorder |

**Frozen from G6 on.** `RunCoupling.tla` and `RunSeats.tla` are cited by digest in accepted records (B20).
`Mechanism.tla` is **not** frozen: it is the model the code is checked against and moves with the code, by addendum.

**Results the drafting did not anticipate**, since G5:
1. **ADR-0041 §7 named the wrong gate for its negative control.** R4 without its root condition is caught by routing,
   which classes it a relaxation, and not by non-vacuity. Found building the floor; applied as R1 before ratification.
2. **`Coupling.tla` and the reference counted different things** (ADR-0042 finding 1). The module's one `Admit`
   advanced the sequence; the reference advanced it on emissions only, so invocations were bounded by `R` and not `K`.
   `RunCoupling.tla` separates the counters and `M_EMITSEQ` is the old behaviour.
3. **`Confinement.tla` reads a launch measurement at rung 0** under `M_HOST` (ADR-0034 finding 6), which rung 0 has no
   more than rung 1. Faithful with no mutation; a successor module owes the one-line correction.
4. **The solver fails the trusted-base rule** (ADR-0045 finding 1). A wrong `holds` lets a relaxation pass by promotion
   alone, and no issuance fixes a solver's honesty. ADR-0030 A1 moves the trust to a pinned proof checker.
5. **`T_persona` is a bound on a declared value, measured on a local clock** (ADR-0045 finding 2). ADR-0032 §2 classes
   the interval as needing trusted time; A2 is honest as a bound and the interval is `T_persona` plus drift.
6. **Gate evidence is unsigned** (ADR-0045 finding 3). ADR-0024 §3 binds every vote to a digest the operator asserts.
7. **ADR-0045's first draft claimed proof where the corpus claims evidence** (finding 7), calling the admit path
   "checked, not trusted". The comparison with Moon & Varshney caught it; R1 added the three rows.
8. **TLC's equality is typed.** Two failures on the way to the first validating trace run were a sentinel sharing a
   field with a number; neither was a divergence between the code and the model. **No divergence was found**, which
   a model written from the code by the same hand on the same day predicts.

**What these checks are.** Unchanged from G5, with one addition: the trace validation is a mechanized link and a
drift harness, not a refinement and not independent evidence; ADR-0033 A5 and ADR-0045 T-0045-28 say so.

---

## 4. Genesis debt ledger (ADR-0029 §7)

**Confirmation-required count: 20 records**, up from 14.

| Record | Criterion | What the first quorum has to review |
|---|---|---|
| 0003 (A2), 0006, 0009, 0013, 0015, 0023, 0028, 0029 (A2), 0030, 0031, 0034, 0037, 0038, 0039 | as at G5 | Unchanged from G5 |
| **0021** | C4 | Build's effect stream under ADR-0003's scheme; sealing at submission; the veto seat and the coverage stall under A2 and ADR-0039 §3; retention per domain under ADR-0003 A3; the ADR-0008 read-through |
| **0040** | C3, C4 | The reversal of ADR-0022 §5; the three names and that none is shared; `Consult` as ingress and a live read as `Actuate`; no terminal variant; the obligations assigned by owner |
| **0041** | C1, C4 | Break-glass restated over `Actuate` and coupled; the `Consult` exemption and its pinning; R4 as a new permit; argument constraints in the bundle tier; the custodian's decision that C3 does not apply |
| **0042** (§1–§5, §7, §8) | C4 | The effect counter; the `Actuate` record, `unknown` ahead of the seal, the late result withheld; the seal at lease end and no abstention; D-0042-1; §6 left out |
| **0043** | C4 | The Listener's closed list; `Consult` on the observer seat; the mark over the effect sequence; the lease to the seal; the scripted Run cell carried as a debt |
| **0044** | C1 | The bundle key as an issued key; the signature over the content revision; refusal at load, at the sidecar and at grant; signing at promotion; that every drafter's choice was settled by ratification |

**Bootstrap specification: partial.** Unchanged since G5: `Anchor` and `BreakGlass` exist; `Genesis`, `RulesFloor`
and `Promotion` do not; `Promotion` owes decide-then-commit, ADR-0035 §5's tally condition, A2.2 and A2.3.

**Debts no confirmation repays.** Those of G2 to G5 stand. G6 adds two kinds. **Assisted drafting**: ADR-0044,
ADR-0045 and ADR-0030 A1 were drafted by the assistant at the custodian's request, with every choice marked as the
drafter's, and settled by the custodian ratifying or revising the text; that is a step further from review than
author-ratification, and ADR-0029 has no criterion for it. **A model written from the code**: `Mechanism.tla` was
written from `state.rs` by the same hand on the same day, so the 21 matching traces are what agreement predicts and
not evidence that the code is right; what they buy is drift detection at the exact step.

---

## 5. Conventions carried at G6

G2 to G5's conventions stand. Added since G5:

- **A pending addendum ratifies in a batch of its own** and is not confirmation-required (B19, B21), as B11 and B16.
- **An addendum may be ratified while the records it follows are Proposed**, bound to revision before any of them
  changes in ratification (ADR-0033 A3, B17). When they ratify as drafted, the dependent entry says the clause was
  not triggered (B20).
- **A scoping amendment is not a reversal.** When an amendment narrows what an accepted clause was ever about rather
  than changing its effect, it ratifies without C3, and its row names the reading under which C3 would attach
  (ADR-0003 A3, B17).
- **Drafter's choice.** A record drafted by someone other than the custodian marks every choice the custodian did not
  settle as *(drafter's choice)*; ratification settles them, and the Status note says so (ADR-0044 B17).
- **A debt owed to an accepted record lands as a dependent entry on ratification of the owing record, not before**
  (ADR-0045 R2 for ADR-0033).
- **One generator per results file** (the 09.25 review's CR-23): `spec/confinement-gen-results.sh`,
  `spec/mechanism-trace-results.sh`. Results headers print the TLC jar's digest from 2026.09.30 on; the jar is
  tracked (ADR-0045 T-0045-29).
- **A trace-validation results line** reads `name | steps | MATCH`, and means every recorded step's projected state
  and result equal the model's; a mismatch names the step.
- **The trusted base is read as rows** (ADR-0045 §1), and a degeneracy's type-change field will cite row ids once
  ADR-0023 §6b is amended.

---

## 6. Records changed after their own ratification

| Record | Change | Why |
|---|---|---|
| 0003 | A3, Batch 17 | 0003.7 scoped to the store; ADR-0021's blocker |
| 0021 | R4, R5; B17 (dependent); B18 | Blocked on discharged; the ADR-0008 read-through; ratified |
| 0022 | A2, Batch 20 | The carrier is shared, no variant name is |
| 0025 | A1, Batch 17 | §1 item (f) |
| 0030 | B17, B20 (dependent); A1 (pending) | Bundle-signing and Run-alphabet debts struck; the solver |
| 0031 | A2, Batch 17 | `ttl ≤ T_persona`; the Persona-expiry obligation struck |
| 0033 | A3, A4, A5; B17, B19, B20, B21 | Three addenda; the Run-alphabet obligation struck; the bundle-signing obligation struck |
| 0034 | A1, Batch 17; B20 (dependent) | The rung-0 row; the verifier-key obligation struck; the Run profile unblocked |
| 0035 | R4 (Proposed) | The ingress bound covers the guest's reads; the in-guest trainer image |
| 0036 | R2 (Proposed) | Finding 1 disposed |
| 0037 | A1, Batch 20 | The Run column; the Listener's list |
| 0038 | B18 (dependent) | Finding 4 closed |
| 0039 | A1, Batch 20 | The sequence counts effects; `Consult` uncoupled; D-0039-1 restated |
| 0041 | R1, before B20 | The wrong gate for the negative control |
| 0042 | R1, before B20 | A late result delivers nothing |
| 0044 | B17 | Ratified as drafted |
| 0045 | R1–R4 (Proposed) | What runs is a row; the debt's owner; the jar; stage 1 |

---

## 7. Open list at G6

**G5's fifty-two items, as they stand.**

| # | Item | At G6 |
|---|---|---|
| 1 | **The sandbox gap** | Unchanged in substance for Build. Run's half has a record and no mechanism: ADR-0042 §6, Proposed; channel fidelity has no owner (G19) |
| 2 | **Floor fitness** | Open, unowned |
| 3 | The clock model | Discharged (G3) |
| 4 | **ADR-0021** | **Discharged**: ratified in Batch 18 (C4) after ADR-0003 A3 and the R5 read-through |
| 5 | **ADR-0005** | Proposed, unchanged |
| 6 | **The ADR-0017 supersession** | Unwritten (the ADR-0008 half was discharged at G5) |
| 7 | **The archetype-evolution record** | Unwritten. Now also owed the versioning of ADR-0045's table and, with it, the theorem-to-premise binding table (ADR-0045 §3) |
| 8 | **R8** | Drafted, pending; four conditions unmet. ADR-0045 §6 refuses trusted time as a row, so the epoch-lapse stand-in is the honest answer until a time source has an attested identity |
| 9 | The per-class floor question | ADR-0014, reserved |
| 10 | **Re-genesis migration** | Open |
| 11 | **Custody** | (1, 0). The corpus's own row is T-0045-11 (Proposed) |
| 12 | **Derived documents** | The 09.12–09.17 set carries supersession notes (two added 09.30); **the glossary is not regenerated at G6** and still names `RunInvoke` and `RunEmit` (item 63) |
| 13 | **Run's alphabet** | **Discharged**: ADR-0040, Batch 20. Dependents: the allowlist entry's schema (item 59), decoder–alphabet compatibility (item 17) |
| 14 | The ToO | Revision 10 is cut with this checkpoint |
| 15 | **Solver trust** | **Moved**: ADR-0045 §6 refuses the solver's row; ADR-0030 A1 (pending) moves the trust to a proof checker (item 54) |
| 16 | **The TCB declaration record** | **Written** as ADR-0045, Proposed at R4 (item 53) |
| 17 | **Decoder–alphabet compatibility** | Open; the rename triggers it for every Run Persona (ADR-0043 §3) |
| 18 | **Bundle signing** | **Discharged in the record**: ADR-0044, Batch 17. The implementation is item 55 |
| 19 | The attestation-rung record | Discharged (G4) |
| 20 | **The provenance independence criterion** | ADR-0035, Proposed at R4; now also owes an in-guest trainer image for its fourth condition |
| 21 | **Persona expiry** | **Discharged in the record**: ADR-0031 A2, Batch 17; the `ttl` check is item 55 and the clock residual item 62 |
| 22 | **Lifting a revocation** | Open |
| 23 | **Replica authentication and Byzantine replicas** | **Sorted**: T-0045-1 is a trust root with the forged admit as its residual; mutual authentication is its delegated mitigation and is unbuilt; BFT is not required |
| 24 | **Finding 9**, proposer retry | Open |
| 25 | **The genesis floor text and S**, DRAFT | Open; changed three times since G5 (§2.2) |
| 26 | **The Run profile** | **Unblocked** by ADR-0040 and shaped by ADR-0042 §6; unwritten |
| 27 | **The verifier key in issued rules** | **Discharged in the record**: ADR-0025 A1, Batch 17; the schema field is item 55 |
| 28 | **Evidence and lineage retention** | Open; T-0045-7 is the archive's row |
| 29 | **Platform TCB updates; accelerator attestation** | Open; T-0045-21 is reserved for whatever attests inference |
| 30 | **θ values** | Open |
| 31 | The ADR-0024 amendment | Discharged (G5) |
| 32 | **ADR-0035 finding 1 of ADR-0036** | **Discharged**: ADR-0035 R4, ADR-0036 R2 |
| 33 | **The best-practice review of ADR-0035's bound** | Open |
| 34 | **ADR-0036's ratification run** | Open; the five missing pieces are listed in the 09.30 package's assessment |
| 35 | **The launcher in `topak-node`** | Open |
| 36 | **A P3-passing image** | Open |
| 37 | The ToO, revision 8 | Discharged |
| 38 | **The 09.26 accounting's discrepancies** | Discrepancy 8 half discharged (the Confinement rung-0 row); the `Lease.tla` half open; the corpus custody row is T-0045-11 |
| 39 | **ADR-0026 §6 rerun** with A2.2 and A2.3 | Open |
| 40 | **A *properties lost* field** | Open; D-0042-1 and D-0045-1 use the prose form too |
| 41 | **A seat-registration record** | Open |
| 42 | **ADR-0037 §9's occupant steps** | Open |
| 43 | **The correlator's detection function** | Open |
| 44 | **Sequence numbers on denials; the correlator's store** | Open |
| 45 | **A scripted cell Observer** | Open; joined by the scripted Run cell ADR-0043 B20 carries |
| 46 | **`W(p)` as an ACL; the gate-side `K < R` check; A2.2 in the reference** | Open |
| 47 | **Measured values** for `T_obs`, `K`, Run's `R` | Open; `T_persona` joins the placeholders |
| 48 | **The quarantine hold** | Open |
| 49 | **Break-glass under a dead Observer** | Open |
| 50 | **The ADR-0017 supersession** | Open (item 6) |
| 51 | **Delegation; attenuation; honeypot validation** | Open |
| 52 | **ADR-0033's live smoke run** | Open; not rerun since 09.25 |

**New since G5.**

| # | Item | Where it sits |
|---|---|---|
| 53 | **ADR-0045's ratification.** Its §9 condition is met except for the theorem-to-premise binding table, shared with item 7; and the ADR-0030 disposition of the solver is drafted | ADR-0045 §9 |
| 54 | **ADR-0030 A1**: the solver wrapper in `floor/run-gates.py`, a pinned proof checker, their digests in the gate header; until then every gate run is D-0030-2 | ADR-0030 A1, Open obligations |
| 55 | **Batch 17's reference debts**: `ttl ≤ T_persona` at grant and renewal; `verifier_keys` and `bundle_keys` in the rules schema; bundle signing in `topak-bundle` and `build-bundle.sh`. One change, one addendum; retires G7 | ADR-0031 B17, ADR-0025 B17, ADR-0044 B17; ADR-0033 A4 |
| 56 | **The refinement chain, stages 2 and 3**: a Lean model with differential testing, then its compilation; the reproducible build (T-0045-30) | ADR-0033 (owner, ADR-0045 R2); ADR-0045 open obligations |
| 57 | **Gate evidence signed** under a key carried by ADR-0025 §1 (f), and the reference verifying it (I18); T-0045-13 changes class | ADR-0045 finding 3 |
| 58 | **ADR-0042 §6, the Run profile and an owner for channel fidelity** (G19) | ADR-0042 B20; ADR-0034 B20 |
| 59 | **The allowlist entry's schema**: how an effect channel is declared | ADR-0040 open obligations; `mechanism/` I33 |
| 60 | **A record that lays out rounds** | ADR-0043 finding 1 |
| 61 | **ADR-0042's remainders**: the missing record after a replica failure (finding 2); a bound on result size; Run's TTL | ADR-0042 open obligations |
| 62 | **`T_persona` on a local clock**: the row says the residual, or `T_persona` waits for a time-source row | ADR-0045 finding 2; ADR-0031, ADR-0032 |
| 63 | **The glossary**, regenerated with the three Run names and the trusted base | ADR-0040 open obligations; item 12 |
| 64 | **ADR-0023 §6b amendment** citing row ids; a deployment declaration template | ADR-0045 open obligations |
| 65 | **The repository reorganization** (the 09.30 proposal), sequenced after this checkpoint | `derived/` |
| 66 | **An ADR-0029 criterion for assisted drafting**, beside the one G4 asked for ADR-0035 R2's marking | §1.2, §4 |

**Not on this list, deliberately:** bootstrap itself, as at G2 to G5.

---

## 8. What G6 does not claim

- **Nothing here is independently reviewed.** Every record, run and ratification of 2026.09.30 was made by the
  person who ratified it or drafted at that person's request, on the day. Three records had a second drafter and no
  reviewer, which is further from review, not closer.
- **No theorem is proved.** The TLA+ artifacts discriminate and check non-vacuity at small constants. The trace
  validation shows the code agreed with a model of the code on every tested path; it is not a refinement, and the
  model is the same hand's.
- **No principal is `Contained`**, at any rung, for the reasons G4 and G5 gave; and Run's confinement is a Proposed
  section with no mechanism behind it.
- **The values are placeholders**, `T_persona` among them, and `T_persona` is not read by the reference.
- **The solver is trusted** on every gate run to date (D-0030-2), bundles are unsigned at the reference (D-0044-1),
  and gate evidence is an operator's assertion.
- **The trusted base is declared in a Proposed record**, and the binding table that would make its rows computable
  does not exist.
- **Detection still fails open against a colluding Observer**, and the residual-risk statement is unwritten.
- **The reference is not the mechanism** (ADR-0033 §1). Its three runs since G5 are evidence of the same kind as before.
- **No floor is ratified, no deployment conforms, and no deployment declaration has been written.**
- **The corpus is not closed.**

---

## 9. Manifest

`SHA256SUMS-G6` · 159 entries, cut from commit `4c2e2f1` plus this checkpoint and revision 10.

As at G2 to G5, the manifest's own digest cannot appear inside the file it measures, and this checkpoint is an entry
in it; both are recorded where they are cut, in the commit that adds them.

| Area | Entries |
|---|---|
| `decisions/` | 44 records |
| `checkpoints/` | 17 — six Theory of Operation cuts, the v1 corpus manifest, revisions 6 to 10, G1 to G6 |
| `derived/` | 19 dated artifacts, the 09.30 reorganization proposal among them |
| `spec/` | 52 — seventeen modules including the operational model and the two successors, run scripts, the two generators, the converter and driver, dated results |
| `floor/` | 12 — the three bundle files, the generator, the gates, the tests, five dated results, the README |
| root | 14 — six process logs, seven reference manifests, and the `slm/` tree manifest |
| `tools/` | 1 — `tla2tools.jar`, included deliberately for ADR-0045 T-0045-29 |

The reference trees are measured by `SHA256SUMS-REF-2026.09.24`, `-25`, `-28`, `-29`, `-29b`, `-30` and `-30b`; the
rehearsal tree by `SHA256SUMS-SLM-2026.09.28`; this manifest measures those eight in turn.

Verify from the repository root:

```sh
shasum -a 256 -c SHA256SUMS-G6 | grep -c ': OK$'                  # expect 159
shasum -a 256 -c SHA256SUMS-SLM-2026.09.28 | grep -c ': OK$'      # expect 40
shasum -a 256 -c SHA256SUMS-REF-2026.09.30b | grep -c ': OK$'     # expect 65 of 66; see below
```

**`SHA256SUMS-REF-2026.09.30b` fails one entry, and should.** It measures `8cf9bd1`. Batch 21 then re-pinned
ADR-0033 in `mechanism/corpus-pins.sha256`, as its addenda say the pin line does whenever the record moves. No code
changed.

**`SHA256SUMS-G5` fails 23 entries**, by construction: every record changed in Batches 17 to 21 and the revisions
of 09.30 (§6), the register and the floor files. G5's manifest remains the record of G5's cut.

The manifest excludes, as G5's did, everything that is not a corpus artifact: material not ours to redistribute, the
exports and archives, the installer and the rest of `tools/`, earlier checkpoint manifests, working directories,
`doc/` and `sessions/`, the licence and notice files and the README. `mechanism/`, `policies/` and `slm/` are measured
by their tree manifests, not directly. `slm/serve/profile-host-rung0.json` is still not in an `SLM` manifest; the
next rehearsal cut measures it. **The glossary is not regenerated at G6** (item 63); the 09.29 glossary stands as the
last cut and predates Run's names.
