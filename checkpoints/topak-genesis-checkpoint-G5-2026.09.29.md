# TOPAK — Genesis Checkpoint G5

**2026.09.29** · genesis custodian: Scott, (1, 0) · supersedes G4 (`a9bea85807a722d6`) as the state of record · narrative: `topak-theory-of-operation-2026.09.29-rev9.md`, cut with this checkpoint

**What G5 is.** The state of record, as G4 was: what each record says, what was ratified and by whom, what is owed,
and what is open. Revision 9 of the Theory of Operation is cut from this checkpoint and narrates it; where the two
disagree, this document wins.

**What changed at G5.** G4 froze a corpus in which the LTRO, the one decomposition inside a principal, had no record,
the Observer's scoping was reversed in effect by a record nobody had written, and detection failed open against a
dead Observer with no record saying so. In one day three records were drafted, revised in place under the custodian's
questions, run against the floor, TLC and the reference, and ratified: **ADR-0037** (the LTRO decomposes into
principals; a principal holds one seat), **ADR-0038** (Observers are per cell, the shared group becomes the
correlator, and ADR-0008 is superseded), **ADR-0039** (Observer liveness is coupled to admission). With them
**ADR-0024 A2** re-homed the veto seats and added two tally conditions, and **ADR-0033 A2** cited the reference that
implements all of it. G5 records **five batches, 12 to 16**, all on 2026.09.29. The policy floor changed twice and
gained a third file, the values file; the reference gained seat kinds, cells, heartbeats and coverage. **Every lease
the reference issues is still rung 0. Nothing is `Contained`.** The rung-0 lease may now name a profile (ADR-0036
R1), which changes what its verdict is derived from and not the verdict. The bootstrap trigger is still unmet, and
remains optional.

---

## 1. Ratification record

All by the genesis custodian under ADR-0029 §2.

| Batch | Date | Contents | Notes |
|---|---|---|---|
| **12 · Seats** | 09.29 | 0037 (C3, C4) | Ratified at R4 after its run (R5). Reverses in effect three bullets of ADR-0018's Reader scope correction (C3); resolves ADR-0022's seat-scoping follow-up and ADR-0016's granularity item (C4). Dependent entries in 0016, 0018, 0022; 0004 and 0019 written late, with Batch 14, and labelled so |
| **13 · Observers** | 09.29 | 0038 (C3, C4) | Ratified at R3 after its run. **Supersedes ADR-0008**; discharges ADR-0023's carried-scope row for that supersession. ADR-0024 A2 was drafted as its condition required |
| **14 · Coupling** | 09.29 | 0039 (C4) | Ratified at R5, after two wording corrections the run found were applied (R5). R3 couples break-glass and is ratified as written |
| **15 · Veto seats** | 09.29 | 0024 A2 | A bootstrap record, so not confirmation-required (ADR-0029 §4). Applied inline: the veto-seat holder, an independent veto seat and coverage to the seal as tally constants, the veto-seat-outage obligation discharged. A2.2 is not built (`mechanism/` G18) |
| **16 · Reference** | 09.29 | 0033 A2 | An addendum citing the reference at `7f74c0b` by manifest `SHA256SUMS-REF-2026.09.29` (62 entries). Not confirmation-required |

### 1.1 Record status at G5

| Status | Count | Records |
|---|---|---|
| Accepted (genesis) | 18 | 0001, 0002, 0004, 0007, 0010, 0012, 0016, 0017, 0018 (in part, §1.2), 0019, 0020, 0022 (in part, §1.2), 0024, 0025, 0026, 0027, 0032, 0033 |
| Accepted (genesis) · confirmation required | 14 | 0003 (for A2 only), 0006, 0009, 0013, 0015, 0023, 0028, 0029 (for A2 only), 0030, 0031 (C2 for A1 only, beside its C1), 0034, **0037**, **0038**, **0039** |
| Proposed | 4 | 0005, 0021, 0035, 0036 |
| **Superseded** | 1 | **0008**, by 0038 (its colocation rule carried forward as 0038 §4) |
| Tombstone | 1 | 0011 |
| Reserved, no file | 1 | 0014 |

38 record files, numbered to 0039. 0014 is the only reserved number. *Superseded* is a status class G4 did not have;
the record keeps its accepted text, marked no longer in force, and its History says by what.

**One pending amendment, unchanged:** ADR-0026 A1 (R8, the break-glass TTL), drafted 2026.09.24. None of its four
conditions is met (§7, item 8). Every other `Pending:` field reads none.

### 1.2 What is ratified in part, or with a scoped marking

**ADR-0022.** Unchanged since G2 as to §6: §1–§5, §7 and §8 are Accepted, **§6 is not**. B12 records the
seat-scoping follow-up resolved for authors.

**ADR-0018 is reversed in part, not superseded.** ADR-0037 §3 (C3) reverses the three bullets of its Reader scope
correction: the Reader is a stage, carries no Persona, and leaves the distinctness predicate. The decoder/validator
split, the artifact chain and the Consequences stand. The bullets are struck inline (B12) with a note.

**ADR-0024 A2 is in force in the record and in part in the reference.** A2.1 (the veto-seat holder) and A2.3
(coverage to the seal) are implemented; **A2.2 (an independent veto seat leased for the round) is not**, since the
reference has no independence table. `mechanism/` G18 says so.

**The four markings scoped to an amendment** from G4 stand: ADR-0003 A2 (C1), ADR-0029 A2 (C3), ADR-0031 A1 (C2),
and ADR-0035 R2's custodian marking outside C1–C4 (§4).

---

## 2. The floors as ratified

### 2.1 The rules floor

Unchanged since G2 in its entries: **R1, R2, R5, R6, R7, R9**; R3 and R4 withdrawn; **R8** pending. **One check is
owed against it:** ADR-0026 §6's non-vacuity run with ADR-0024 A2.2 and A2.3 modeled as conjuncts of
`PromotionEnabled`, each with the mutation of dropping it (ADR-0024 A2, obligations).

### 2.2 The policy floor

**Changed twice since G4, and still DRAFT.** ADR-0030 is Accepted (C1); the floor text is not ratified. Two gate runs
on 2026.09.29, both passing every ADR-0030 §5 gate:

| Run | What changed | Policies | Cases | Digests |
|---|---|---|---|---|
| `genesis-gates-results-2026.09.29.txt` (ADR-0037 §4) | `Seat.kind` in S; B6 permits a vote only from a `grant` seat on the grant roster or an `observer` seat on the veto roster; **B10** forbids `Draft`, `Invoke`, `Submit` and `RunInvoke` to any seat but a `thinker` | 15 | 47 | floor `e2c28cfe1b638b36`, schema `f04bfa225f67031c` |
| `genesis-gates-results-2026.09.29-adr0039.txt` (ADR-0039 §2) | `observerLive` in RunCtx; **R3** forbids `RunInvoke` and `RunEmit` under a `thinker` seat when no cell Observer is live, break-glass included; **the values file joins the bundle** and its digest is in the gate header | 16 | 51 | floor `49a6e3140726a9a5`, schema `ac2a0accca51f5f8`, values `0d19c9e3ffa3e714` |

**The floor bundle is three files** (ADR-0039 §1 R3): the policies, schema S and `floor/genesis-values.json`, the
numbers the typed lift reads that Cedar text cannot hold. The mechanism compiles all three in and refuses any other
bytes (`topak-floor`, `PINNED_*_SHA256`). **Every number in the values file is a placeholder**: `T_obs` 5000 ms,
`K` 8, unset θ. They are deployment or rung choices, and the file says so.

### 2.3 Confinement

Unchanged in force since G4: ADR-0034 Accepted, ADR-0036 Proposed. **ADR-0036 R1** lets a rung-0 grant name a
profile, so the verdict is derived from declared clauses instead of from nothing; the words beside each clause are
*declared by the operator and verified by nobody*, the trusted base at rung 0 stays empty, and the profile is the
constant across rungs while the rung is the variable. The reference's first declared profile is the host-run
occupant's, `slm/serve/profile-host-rung0.json`, with P1, P2 and P3 failing and P5 passing. **`Contained` still has
no members at any rung**; the missing premise is still the criterion (ADR-0035, Proposed).

### 2.4 The LTRO, now three records

New at G5. **ADR-0037**: a principal holds exactly one seat; an LTRO is a *cell* of principals around one Thinker,
not a principal; the Thinker and the Observer are seats with Personas, the Listener and the Reader are stages with
none; the Reader's two admissible uses are facts the cell Observer consumes, and conformance may admit only where
inference is attested; alphabets are bounded by seat kind in the floor; seat distinctness covers one pair per cell;
raw emission is retained at the archetype for a decoder-faithfulness audit and is a declared degeneracy below it.
**ADR-0038**: one `observer` seat per cell plus a correlator, the watched-by relation `W(p)` defined by the topic ACL,
the correlator reading facts, envelopes and payloads across cells, ADR-0008's colocation rule carried forward on
fault-domain grounds alone, Observers combining by any-of with no quorum, and the veto roster holding cell Observers
and correlators. **ADR-0039**: liveness is a heartbeat carrying a watermark, timed on the mechanism's clock; every Run
admit under a Thinker needs a live cell Observer (`R3`), with the bound `seq − mark < K` and coverage carried across
rounds at the grant; Build couples the promotion to coverage of the author's round; the correlator is never coupled;
collusion is declared uncovered. Together they discharge LP-1, CR-10, CR-2 in three of its four cases, and ADR-0024's
veto-seat-outage obligation, and they name the pieces they leave: the seat-registration record, delegation, the
quarantine hold, the correlator's function.

---

## 3. Verified artifacts

G4's artifacts keep their digests. New since G4:

| Artifact | SHA-256 (16) | Records | Result |
|---|---|---|---|
| `spec/Seats.tla` | `903a1db686968df0` | ADR-0037 §9 | Nine checks. `OnlyThinkersAuthor` and `OneSeatPerPrincipal` hold over 6,656 states; `M_KIND` breaks only §4, `M_SEAT` breaks only §1; three witnesses fire. **`M_SEAT` is the reference's behaviour before 09.29** (ADR-0037 finding 1) |
| `spec/Observers.tla` | `96b0792ce948ec80` | ADR-0038 §8 | Ten checks. `DenyByAnyOf` and `ReachIsBounded` hold; `M_QUORUM` breaks only §5, its counterexample one honest finding suppressed by the other Observer's silence; `M_REACH` breaks only §1; four witnesses fire, one a refusal on a single Observer's finding |
| `spec/Coupling.tla` | `6d1e7a07f3d102ef` | ADR-0039 §8 | Fifteen checks over two rounds, K = 1, R = 3. All three properties hold over 1,124 states; `M_NOCOUPLE` breaks §2 and `UnreadBounded` with it; `M_MARK` and `M_ROUNDS` break only `UnreadBounded`, the latter with "round 2 granted while round 1 unread"; `M_CORR` breaks only §4; four witnesses fire |
| The floor, two runs | `49a6e3140726a9a5` / `ac2a0accca51f5f8` / `0d19c9e3ffa3e714` | ADR-0037 §4, ADR-0039 §2 | §2.2. All gates pass in both; every new entry total and discriminating; no entry dead |
| Reference, run 2026.09.29 | manifest `a5a89d9c824743e4` | ADR-0033 §7 A2 | `mechanism/` and `policies/` at `7f74c0b`, 62 entries; 49 tests pass across six binaries, the e2e showing every refusal ADR-0039 §8 lists and one promotion stalled for coverage and completed. Fifteen files changed since 09.28, all under ADR-0037, ADR-0038, ADR-0039 and ADR-0024 A2 |

**Frozen from G5 on.** `Seats.tla`, `Observers.tla` and `Coupling.tla` are cited by digest in accepted records.

**Results the drafting did not anticipate**, since G4:
1. **The reference enforced one live lease per seat, not per principal** (ADR-0037 finding 1). Its test passed only
   because the helper derived the principal from the seat. `M_SEAT` is that behaviour; the grant path now refuses it.
2. **The first draft of ADR-0039 bounded the wrong backlog** (finding 4, R1). Its check was scoped to the current
   round, where the round bound already limits unread emissions to `R`, and passed at the start of every new round
   because the sequence and the watermark both restart with the lease. Found by the custodian's question "isn't `K`
   bounded by the round's lease?"; `M_ROUNDS` is the first draft's text.
3. **The bound holds only in the strict form.** `seq − mark ≤ K` admits a `K+1` backlog; `Coupling.tla` found it and
   R5 rewrote condition 3.
4. **R3 as first drafted refused the heartbeat it exists to receive**, since an observer seat has no cell Observers of
   its own. Found by three e2e tests failing at the same line; the entry is scoped to `thinker` seats.
5. **`T_obs` cannot be re-checked at apply**, being a per-replica clock; only the deterministic half of `live(o)` is.
   R5 says so; ADR-0032 §2 is why it is acceptable.
6. **ADR-0023 §6's schema has no field for what these degeneracies lose** (ADR-0037 finding 6). All five write "none"
   under *theorems voided*, because the Observer is deny-only and the retained emission admits nothing, and state the
   loss in prose. A *properties lost* field is proposed (§7, item 40).
7. **Six dependent-entry rows were written outside their History tables**, after the quoted prior-title-block fence,
   in Batches 12 and 13. Repaired with Batch 14; a convention follows (§5).

**What these checks are.** Unchanged from G4: evidence, not attestation, from one hand at small constants, and now
from the same hand on the same day as the records they check (§4).

---

## 4. Genesis debt ledger (ADR-0029 §7)

**Confirmation-required count: 14 records**, up from 11.

| Record | Criterion | What the first quorum has to review |
|---|---|---|
| 0003 (A2), 0006, 0009, 0013, 0015, 0023, 0028, 0029 (A2), 0030, 0031, 0034 | as at G4 | Unchanged from G4 |
| **0037** | C3, C4 | The Reader as a stage and the reversal of ADR-0018's three bullets; one seat per principal and the cell; the per-kind alphabet bound; raw emission retention and the decoder-seat option not taken; conformance admitting only where inference is attested |
| **0038** | C3, C4 | The supersession of ADR-0008; per-cell Observers plus a correlator; any-of and the retired quorum argument; the correlator reading payloads at the archetype; the veto roster's new holder |
| **0039** | C4 | The heartbeat and watermark as facts; the strict bound and its placeholders; the cross-round grant condition; coverage at the Build tally; the correlator never coupled; break-glass coupled; collusion declared uncovered |

**Bootstrap specification: partial.** Unchanged: `Anchor` and `BreakGlass` exist. `Promotion` owes decide-then-commit
(G3), the ADR-0035 §5 tally condition, and now A2.2 and A2.3 (§2.1).

**Debts no confirmation repays.** Those of G2, G3 and G4 stand. G5's is the sharpest form of the third: three
records, two amendments, two floor revisions, three TLC modules and a reference change were drafted, checked,
revised and ratified by one person between one morning and one evening. The custodian's questions in the drafting
sessions caught three of §3's seven results before any check did, which is review of a kind, and not the
independent kind ADR-0029 A2 requires. The fourth kind (ADR-0035 R2's marking) is unchanged.

---

## 5. Conventions carried at G5

G2's, G3's and G4's conventions stand. Added since G4:

- **A History row of kind *Run*** records a ratification run's results on the record it checks, before ratification,
  with what the run left outstanding on its face (ADR-0037 R5, ADR-0038 R3, ADR-0039 R4).
- **Dependent entries go inside the History table**, above the quoted prior-title-block fence, never appended after
  it (§3, result 7). A dependent entry written after its batch is labelled with both dates.
- ***Superseded* is a status class.** The record keeps its accepted text, its status names the superseding record and
  batch, and the superseding record's B-row names what is carried forward and what is replaced (ADR-0008 B13).
- **A run finding that the text disagrees with is applied as a revision before ratification**, not carried as a debt,
  when the checked artifacts already implement the corrected form (ADR-0039 R5). Ratifying text that disagrees with
  its own evidence is not done.
- **A rung-0 profile prints *declared*.** Results at rung 0 that cite a profile print `[digest, 0]`, the word
  *declared* beside every clause, and that no participant is trusted for its truth (ADR-0036 R1).
- **Placeholders say so three times**: in the file, in the record's header and in the record's body (ADR-0039 §1 R3).
- **Degeneracy rows may carry a *properties lost* line** in prose until ADR-0023 §6 has the field (§7, item 40).

---

## 6. Records changed after their own ratification

| Record | Change | Why |
|---|---|---|
| 0004 | B12, dependent entry (written with Batch 14) | Raw emission retained at the archetype is cognitive payload (ADR-0037 §3 R2) |
| 0008 | B13, superseded | By ADR-0038; the colocation rule carried forward, the scoping replaced |
| 0016 | B12, dependent entry | Seat-binding values `thinker` and `observer`; the granularity item resolved |
| 0018 | B12, dependent entry | Three Reader bullets reversed in effect (C3); not superseded |
| 0019 | B12, dependent entry (written with Batch 14) | Conformance may admit only where inference is attested (ADR-0037 §3 R3) |
| 0022 | B12, dependent entry | The seat-scoping follow-up resolved for authors |
| 0023 | B13, dependent entry | The ADR-0008 supersession row struck as discharged; the ADR-0017 half open |
| 0024 | A2, Batch 15 | The veto-seat holder; two tally conditions; the outage obligation discharged; applied inline |
| 0033 | A2, Batch 16 | The 2026.09.29 addendum |
| 0035 | R3 (Proposed) | The values file named as the home of its θ |
| 0036 | R1 (Proposed) | A rung-0 grant may name a profile; the ladder; the host-run profile |
| 0021 | R3 (Proposed) | §5 cites ADR-0038; "replicated" becomes per-cell seats by any-of |
| 0037 | R1–R5, before B12 | Pointers to 0038/0039; emission formation and retention; the Reader's facts and the rung for conformance; the schema finding; the run |
| 0038 | R1–R3, before B13 | The correlator reads the Reader's facts; the schema pointer; the run |
| 0039 | R1–R5, before B14 | Cross-round coverage and `K < R`; the schema pointer; the values file and placeholders; the run; the two wording corrections |

---

## 7. Open list at G5

**G4's thirty-eight items, as they stand.**

| # | Item | At G5 |
|---|---|---|
| 1 | **The sandbox gap** | Unchanged in substance. ADR-0036 R1 adds the rung-0 declared profile; no rung-1 lease has been issued |
| 2 | **Floor fitness** | Open, unowned |
| 3 | The clock model | Discharged (G3) |
| 4 | **ADR-0021** | Proposed; R3 cites ADR-0038 |
| 5 | **ADR-0005** | Proposed, unchanged |
| 6 | **The ADR-0008 and ADR-0017 supersessions** | **Half discharged.** ADR-0008 is superseded by ADR-0038 (B13). The ADR-0017 ordering-primacy supersession is unwritten |
| 7 | **The archetype-evolution record** | Unwritten. The rung-DAG analysis gains the `slm/serve` ladder as a worked path (09.29) |
| 8 | **R8** | Drafted, pending; four conditions unmet |
| 9 | The per-class floor question | ADR-0014, reserved |
| 10 | **Re-genesis migration** | Open |
| 11 | **Custody** | (1, 0) |
| 12 | **Derived documents** | The glossary is regenerated at 09.29 with this checkpoint; the 09.12–09.17 set is still stale |
| 13 | **Run's alphabet** | Open. Gains dependents: R3 is written against the provisional `RunInvoke`/`RunEmit` (ADR-0039 finding 2); Run's `R` is a placeholder (64) |
| 14 | The ToO, revision 7 | Discharged; revision 9 is cut with this checkpoint (item 37) |
| 15 | **Solver trust** | Open |
| 16 | **The TCB declaration record** | Unwritten. Gains ADR-0037 §3's row: conformance, where it admits, is on the mechanism side |
| 17 | **Decoder–alphabet compatibility** | Open; ADR-0037 names it as the trigger to revisit a decoder seat |
| 18 | **Bundle signing** | Open |
| 19 | The attestation-rung record | Discharged (G4) |
| 20 | **The provenance independence criterion** | ADR-0035, Proposed at R3. `Contained` waits on it. Now also blocks ADR-0024 A2.2 in the reference (G18) |
| 21 | **Persona expiry; lineage and independence** | Expiry open |
| 22 | **Lifting a revocation** | Open |
| 23 | **Replica authentication and Byzantine replicas** | Open |
| 24 | **Finding 9**, proposer retry | Open |
| 25 | **The genesis floor text and S**, DRAFT | Open; changed twice on 09.29 (§2.2) and still unratified |
| 26 | **The Run profile** | ADR-0034 debt, blocked on item 13 |
| 27 | **The verifier key in issued rules** | Open |
| 28 | **Evidence and lineage retention** | Open; ADR-0038 finding 3 adds the correlator's derived store against the erasure unit |
| 29 | **Platform TCB updates; accelerator attestation** | Open; now also the rung at which conformance may admit (ADR-0037 §3 R3) |
| 30 | **θ values, θ<sub>gen</sub> and β; the near-duplicate tool** | Open; their home is the values file (ADR-0035 R3), where they are unset |
| 31 | **The ADR-0024 amendment** | **Discharged** as A2 (Batch 15), carrying ADR-0035 §5's, ADR-0038 §6's and ADR-0039 §3's conditions. The corpus-admission declarations and the `feedback` field remain with ADR-0035 |
| 32 | **ADR-0035 finding 1 of ADR-0036** | ADR-0035 still owes the disposition |
| 33 | **The best-practice review of ADR-0035's bound** | Open |
| 34 | **ADR-0036's ratification run** | Open. The rung-0 declared profile (R1) is written; the rung-1 launcher is not |
| 35 | **The launcher in `topak-node`** | Open |
| 36 | **A P3-passing image** | Open |
| 37 | **The ToO, revision 8** | **Discharged**; revision 9 is cut with this checkpoint |
| 38 | **The 09.26 accounting's remaining discrepancies** | Unowned; item 40 is now the first of them with an owner |

**New since G4.**

| # | Item | Where it sits |
|---|---|---|
| 39 | **ADR-0026 §6 rerun** with A2.2 and A2.3 modeled, each with its dropping mutation | ADR-0024 A2 obligations; §2.1 |
| 40 | **A *properties lost* field in ADR-0023 §6's schema**, for losses that are not safety theorems | ADR-0037 finding 6; routed to ADR-0023's scope or the parameter-enumeration record |
| 41 | **A seat-registration record**: who declares seats, and how the persons behind seats are compared, since recusal is per seat and a person may hold two | ADR-0037 finding 2; `mechanism/` I8 |
| 42 | **ADR-0037 §9's occupant steps**: raw emission beside the `Draft` with a decoder re-run, and the Reader's facts consumed by the Observer, both on the host-run occupant | ADR-0037 B12; shared with item 45 |
| 43 | **The correlator's detection function**: what it looks for, given what it reads. First input named: cross-cell distance drift | ADR-0038 finding 1 |
| 44 | **Sequence numbers on denials** (ADR-0015) and the correlator's store against the erasure unit (ADR-0006) | ADR-0038 findings 2 and 3 |
| 45 | **A scripted cell Observer beside the rehearsal**, in place of the e2e fixture | ADR-0039 B14; ADR-0033 A2 |
| 46 | **`W(p)` as a topic read ACL**; the gate-side `K < R` check; **ADR-0024 A2.2 in the reference** (G18) | ADR-0038 R3, ADR-0039 R4; `mechanism/` I8, I27, G18 |
| 47 | **Measured values for `T_obs`, `K` and Run's `R`**, replacing the placeholders | ADR-0039 §1 R3 |
| 48 | **The quarantine hold** as `K = 0` with a hold, and how Observer rounds are laid out in Run | ADR-0039 findings 1 and 3; `mechanism/` G12 |
| 49 | **Break-glass under a dead Observer**: R3 couples it, ratified as written; reopening is an amendment | ADR-0039 R4 item 4, B14 |
| 50 | **The ADR-0017 supersession**, the other half of item 6 | ADR-0023 §5 |
| 51 | **Delegation and on-behalf-of attribution; attenuation for derived principals; honeypot validation at seat admission** | ADR-0037 obligations, named so they are not lost (LP-8, LP-9, LP-4; CR-3) |
| 52 | **ADR-0033's live smoke run** against Kafka and OPA, not rerun since 09.25 | ADR-0033 A2 |

**Not on this list, deliberately:** bootstrap itself, as at G2, G3 and G4.

---

## 8. What G5 does not claim

- **Nothing here is independently reviewed.** Every record, run and ratification of 2026.09.29 was made by the person
  who drafted it, on the day of drafting. The custodian's questions during drafting changed three records; that is
  not the review ADR-0029 A2 requires, and none has begun.
- **No theorem is proved.** The TLA+ artifacts discriminate and check non-vacuity at small constants; the three new
  modules are as small as any.
- **No principal is `Contained`**, at any rung, for the reason G4 gave.
- **The values are placeholders.** `T_obs`, `K` and Run's `R` were chosen for order of magnitude so the runs had
  values; no Observer has been measured.
- **Detection still fails open against a colluding Observer**, by ADR-0039 §5's own statement, and the residual-risk
  statement that should carry the sentence is unwritten.
- **The reference is not the mechanism** (ADR-0033 §1). Its 09.29 run is evidence of the same kind as before.
- **No floor is ratified, no deployment conforms, and no deployment declaration has been written.**
- **The corpus is not closed.**

---

## 9. Manifest

`SHA256SUMS-G5` · 130 entries, cut from commit `219e104` plus this checkpoint, revision 9, the 09.29
glossary and the manifests added with them.

As at G2 to G4, the manifest's own digest cannot appear inside the file it measures, and this checkpoint is an entry
in it; both are recorded where they are cut, in the commit that adds them.

| Area | Entries |
|---|---|
| `decisions/` | 38 records |
| `checkpoints/` | 15 — six Theory of Operation cuts, the v1 corpus manifest, revisions 6 to 9, G1 to G5 |
| `derived/` | 18 dated artifacts, the 09.29 glossary among them |
| `spec/` | 38 — fourteen modules including the three new and the two successors, run scripts, dated results |
| `floor/` | 10 — the three bundle files, the generator, the gates, the tests, three dated results, the README |
| root | 11 — six process logs, four reference manifests, and the `slm/` tree manifest |

The reference trees are measured by `SHA256SUMS-REF-2026.09.24`, `-25`, `-28` and `-29`; the rehearsal tree by
`SHA256SUMS-SLM-2026.09.28`; this manifest measures those five in turn.

Verify from the repository root:

```sh
shasum -a 256 -c SHA256SUMS-G5 | grep -c ': OK$'                  # expect 130
shasum -a 256 -c SHA256SUMS-SLM-2026.09.28 | grep -c ': OK$'      # expect 40
shasum -a 256 -c SHA256SUMS-REF-2026.09.29 | grep -c ': OK$'      # expect 61 of 62; see below
```

**`SHA256SUMS-REF-2026.09.29` fails one entry, and should.** It measures `7f74c0b`. Batch 16 then re-pinned
ADR-0033 in `mechanism/corpus-pins.sha256`, as its addendum says the pin line does whenever the record moves. No code
changed.

**`SHA256SUMS-G4` fails nineteen entries**, by construction: twelve records changed after G4 (§6, and 0036 R1), the
rung-DAG analysis (the ladder), and six floor files (§2.2). G4's manifest remains the record of G4's cut.

The manifest excludes, as G4's did, everything that is not a corpus artifact: material not ours to redistribute,
the exports and archives, the tools directory and the installer, earlier manifests, working directories, `doc/` and
`sessions/`, the licence and notice files and the README. `mechanism/`, `policies/` and `slm/` are measured by their
tree manifests, not directly. `slm/serve/profile-host-rung0.json` is inside the `slm/` tree and is not yet in a
`SLM` manifest; the next rehearsal cut measures it.
