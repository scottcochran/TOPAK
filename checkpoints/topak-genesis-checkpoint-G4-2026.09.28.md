# TOPAK — Genesis Checkpoint G4

**2026.09.28** · genesis custodian: Scott, (1, 0) · supersedes G3 (`2198e90059a658e7`) as the state of record · narrative: `topak-theory-of-operation-2026.09.28-rev8.md`, cut with this checkpoint

**What G4 is.** The state of record, as G3 was: what each record says, what was ratified and by whom, what is owed,
and what is open. Revision 8 of the Theory of Operation is cut from this checkpoint and narrates it; where the two
disagree, this document wins.

**What changed at G4.** G3 froze a corpus in which confinement had a field and no semantics, provenance had a
requirement and no criterion, and the reference issued every lease at rung 0. Between the cuts three records were
written and two of them revised in place, two batches ratified four items, the reference's renewal path changed to
follow one of them, and a lineage rehearsal ran end to end and refuted a soundness claim in a record two days old.
G4 records **four ratifications** in **Batches 10 and 11** on 2026.09.28, and two amendments ratified on 2026.09.25
after G3's cut that no checkpoint has carried. **Every lease the reference issues is still rung 0. Nothing is
`Contained`, and ADR-0034 in force changes the reason, not the fact.** The bootstrap trigger is still unmet, and
remains optional.

---

## 1. Ratification record

All by the genesis custodian under ADR-0029 §2.

| Batch | Date | Contents | Notes |
|---|---|---|---|
| *After G3* | 09.25 | 0015 E2 · 0029 A2 (C3, for A2 only) | Ratified the same day as G3, after its cut, so `SHA256SUMS-G3` fails both files. E2 conditions the "strictly stronger" comparison on the sandbox gap's discharge. A2 makes an independent review of the whole corpus a bootstrap precondition, and reverses the no-review consequence of its own record |
| **10 · Confinement** | 09.28 | 0031 A1 (C2, for A1 only) · 0034 (C2, C4) | Together: 0034's no-silent-downgrade rule holds at grant and was bypassable at renewal until A1 fixed the rung across renewal. 0034 ratified at R2, with the criterion a conjunct of `Contained`. The reference's `check_renewal` follows A1; the record is re-pinned |
| **11 · Reference** | 09.28 | 0033 A1 | An addendum citing the reference at `5b25245` by manifest `SHA256SUMS-REF-2026.09.28`, after Batch 10 made E1's "no code" sentence false. Not confirmation-required |

### 1.1 Record status at G4

| Status | Count | Records |
|---|---|---|
| Accepted (genesis) | 19 | 0001, 0002, 0004, 0007, 0008, 0010, 0012, 0016, 0017, 0018, 0019, 0020, 0022 (in part, §1.2), 0024, 0025, 0026, 0027, 0032, 0033 |
| Accepted (genesis) · confirmation required | 11 | 0003 (for A2 only), 0006, 0009, 0013, 0015, 0023, 0028, **0029 (for A2 only)**, 0030, 0031 (**C2 for A1 only**, beside its C1), **0034** |
| Proposed | 4 | 0005, 0021, **0035**, **0036** |
| Tombstone | 1 | 0011 |
| Reserved, no file | 1 | 0014 |

35 record files, numbered to 0036. 0014 is the only reserved number.

**One pending amendment, unchanged:** ADR-0026 A1 (R8, the break-glass TTL), drafted 2026.09.24. None of its four
conditions is met (§7, item 8). Every other `Pending:` field reads none.

### 1.2 What is ratified in part, or with a scoped marking

**ADR-0022.** Unchanged since G2: §1–§5, §7 and §8 are Accepted; **§6 is not**. ADR-0034 discharges §6's obligation
for Build and not for Run, so §6 stays Proposed. A dependent entry (B10) records that §3's hermeticity obligation is
discharged for Wasm tools; native tools stay unowned.

**Three markings scoped to an amendment.** ADR-0003 A2 (C1), from G3. **ADR-0029 A2 (C3)**, ratified 09.25 after the
cut: the amendment reverses two clauses of its own record. **ADR-0031 A1 (C2)**: it states how a confinement claim
survives renewal; the record's C1 marking is unchanged.

**One marking ADR-0029 has no criterion for.** ADR-0035 R2, a Proposed revision, is marked confirmation-required *on
its own account* by custodian instruction: its bounded-share construction is a novel measurement rule and is to be
reviewed against practice before ratification. The status note names C2 as the nearest criterion. §4 carries it as
a ledger line.

---

## 2. The floors as ratified

### 2.1 The rules floor

Unchanged since G2. Genesis contents: **R1, R2, R5, R6, R7, R9**; R3 and R4 withdrawn, IDs reserved. **R8** stays
drafted and pending (ADR-0026 A1).

### 2.2 The policy floor

Unchanged since G3. ADR-0030 is Accepted (C1). **The genesis floor text is not ratified**: `floor/genesis-floor.cedar`
(`9b6adeee0c2ae308`) and `floor/genesis.cedarschema` (`77d9b566d76134c3`) are DRAFT, at the digests G3 recorded.

### 2.3 Confinement, now ratified

New at G4. **ADR-0034 is Accepted** (Batch 10, C2 and C4): the archetype confinement rung is a confidential VM with an
independent verifier (rung 3); rungs 1 and 2 are declared degeneracies (D-0034-2, D-0034-1); a confinement profile
is a promoted artifact fixing seven clauses P1–P7; appraisal is a condition of the grant, with three verdicts and a
log-derived nonce; a principal whose evidence does not reach the declared rung is refused, **at grant and at renewal**
(ADR-0031 A1); re-attestation is event-triggered; a *Contested* verdict is a targeted revocation of the principal.

**`Contained(p)` has four conjuncts** (ADR-0034 §4 R2): a live lease at rung ≥ 1 on an Attested verdict; a profile
meeting P3–P5; an in-house Persona; and **ADR-0017's independence criterion in force**. The fourth is ADR-0035,
Proposed. Until it is ratified with its θ values set, `Contained` has no members at any rung. The custodian chose
this reading over the draft's, which made independence not a conjunct; the option is recorded.

**Confinement is a lease field with semantics** (ADR-0031 §3, ADR-0034 §2), and renewal keeps it, digest and rung
(A1). A lower rung under a live lease was a silent downgrade the records never met in a check, because
`Confinement.tla` did not model renewal until 09.28 (§3).

---

## 3. Verified artifacts

G3's artifacts keep their digests, with two exceptions below that are successors, not edits. New or changed since G3:

| Artifact | SHA-256 (16) | Records | Result |
|---|---|---|---|
| `spec/Lease_A1.tla` | `0b5eac7a7309be2f` | ADR-0031 §8 (A1) | Successor of the frozen `Lease.tla` (`7636c6c3364bca9c`), differing only where marked A1: rungs 0–3, the rung fixed across renewal, `M_LOWER`, a rung ≥ 1 renewal witness. Thirteen checks; `Safe` holds over 2,136,720 distinct states; `M_LOWER` grants at rung 1 and renews at rung 0 |
| `spec/Confinement.tla` | `d0dcf21ce9774885` | ADR-0034 §7 (R1) | Renewal modeled; evidence is the launch measurement. Thirty-eight rows: `Safe` at every rung; `M_HOST` breaks rungs 1 and 2 and not 3; `M_RENEWLOW` breaks `NoSilentDowngrade` at rung 3; `NeverRenewContested` **holds** at every rung (finding 5). The 09.25 run (`110eecdae2dd07e6`) is kept beside it |
| Reference, run 2026.09.28 | manifest `45ff610e16b1cc9c` | ADR-0033 §7 A1 | `mechanism/` and `policies/` at `5b25245`, 61 entries; 44 tests pass with the corpus at `9d42a1d`. `check_renewal` refuses any change of rung. Five files changed since 09.25, one of them not from a corpus decision (`f59941d`, the licence field) |
| `slm/`, run 2026.09.28 | manifest `SHA256SUMS-SLM-2026.09.28` | ADR-0035 §8 | Gate suite in three modes: `bounded` holds over 2,000 trials, `ratio` (as drafted) fails at E3 13/2000 and distillation 241/2000, `absolute` holds; the padding residual shown, 24/2000 and 250/2000. Rehearsal rerun under the R2 record schema: honest consistent, three tampers Contested, `consumed` populated |

**Frozen from G4 on.** `Lease_A1.tla` and `Confinement.tla` are now cited by digest in accepted records. G2's
frozen-artifact convention applies; a further change to either is a new dated successor (§5).

**Results the drafting did not anticipate**, since G3:
1. **No silent downgrade held at grant and was bypassed at renewal.** ADR-0031 §4 let a renewal lower the rung;
   ADR-0034 §3.4 refused a grant below the declared rung; `Confinement.tla` never modeled renewal, so the two records
   never met in a check. Found by the 09.26 accounting, fixed by ADR-0031 A1 and ADR-0034 R1, and `M_RENEWLOW` is the
   case.
2. **Re-attestation cannot detect a running guest being altered** (ADR-0034 finding 5). The 09.25 model read the
   running image as evidence, which no rung's measurement does. Corrected; no earlier result changed, and the rung-2
   `M_HOST` trace was restated.
3. **ADR-0035 §2's monotonicity claim was false as drafted** (ADR-0035 finding 5). Both ratios had ingress in the
   denominator, so charging a trainer with more corpus helped it pass. The rehearsal's property check found it on
   09.25; R2 bounds every share on 09.28. R1, written the same day as R2, had leaned on the false claim.
4. **ADR-0035 as drafted could not be ratified** (finding 4): a projected lineage needed a non-`Mediated` trainer, and
   nothing is non-`Mediated` until the record is in force. R1 bounds projection by the cage instead.
5. **The drift check caught a pin taken from uncommitted text.** Batch 10's commit pinned ADR-0035 at its R1 text,
   committed separately. ADR-0033 A1 records the run against the commit where the pin holds and says why.

**What these checks are.** Unchanged from G3: evidence, not attestation, from one hand at small constants.

---

## 4. Genesis debt ledger (ADR-0029 §7)

**Confirmation-required count: 11 records**, up from 9, three of them for one amendment only.

| Record | Criterion | What the first quorum has to review |
|---|---|---|
| 0003, **A2 only** | C1 | Unchanged from G3 |
| 0006 · 0009 · 0013 · 0015 · 0023 · 0028 · 0030 | as at G3 | Unchanged from G3 |
| **0029, A2 only** | C3 | The full-corpus review as a bootstrap precondition, and the reversal of §6's no-re-review clause |
| 0031 | C1; **C2 for A1** | As at G3, plus: renewal keeps the confinement rung, and the lease lapses when re-attestation fails |
| **0034** | C2, C4 | The seven profile clauses; appraisal as a grant condition; no silent downgrade; the four conjuncts of `Contained`; the trusted base per rung |

**Bootstrap specification: partial.** Unchanged: `Anchor` and `BreakGlass` exist. `Promotion` owes decide-then-commit
(G3) and, once ADR-0035 is ratified, the tally condition of its §5.

**Debts no confirmation repays.** The two from G2 stand. The third, from G3, has grown: Batches 10 and 11 and every
revision of ADR-0034, ADR-0035 and ADR-0036 were drafted, checked and ratified or revised by one person on the day
of drafting. **A fourth kind, new at G4:** ADR-0035 R2 carries a confirmation marking no ADR-0029 criterion names.
The ledger records it here; whether ADR-0029 needs a criterion for "a novel construction reviewed against practice"
is open (§7, item 33).

---

## 5. Conventions carried at G4

G2's and G3's conventions stand. Added since G3:

- **A frozen module's successor carries the amendment tag.** `Lease.tla` is frozen; A1 is checked by `Lease_A1.tla`,
  which differs only where marked, and the record's citation moves to it on ratification. A module cited only by a
  Proposed record (`Confinement.tla` before B10) may be revised in place, as the frozen-artifact rule permits.
- **A run and its manifest may name different commits.** When the suite runs at a commit whose measured trees equal
  the manifest's commit, the addendum names both and says why (ADR-0033 A1).
- **Evidence trees outside the corpus get a tree manifest.** `slm/` is cited by `SHA256SUMS-SLM-2026.09.28`, which
  this checkpoint measures, as `mechanism/` and `policies/` are cited by the `REF` manifests. Its gitignored run
  directories are represented by dated results files (09.25 review, CR-22).
- **A custodian marking outside C1–C4** goes on the record's status note, names the nearest criterion, and is a
  ledger line (§4).
- **Results files are never overwritten** (G3) is kept, and extended: a rerun that changes a model's digest writes a
  new results file and the record cites both.

---

## 6. Records changed after their own ratification

| Record | Change | Why |
|---|---|---|
| 0015 | E2, 09.25 | The "strictly stronger" comparison conditioned on ADR-0022 §6's discharge (09.16 review CR-1) |
| 0029 | A2, 09.25 | Full-corpus independent review as a bootstrap precondition; C3, scoped |
| 0031 | A1, Batch 10 | Renewal keeps the confinement rung; §4 and §8 applied inline; the check moves to `Lease_A1.tla` |
| 0031 | B10, dependent entry | The attestation-rung obligation discharged by ADR-0034; the criterion obligation annotated |
| 0022 | B10, dependent entry | §3's hermeticity obligation discharged for Wasm tools; §6 untouched |
| 0033 | A1, Batch 11 | The 2026.09.28 addendum; E1's sentence struck with a pointer |
| 0034 | R1, R2, 09.28 | **Before ratification**, while Proposed: renewal in the check; the criterion a conjunct of `Contained` |
| 0035 | R1, R2, 09.28 | While Proposed: projection bounded by the cage; every share an upper bound |

---

## 7. Open list at G4

**G3's twenty-five items, as they stand.**

| # | Item | At G4 |
|---|---|---|
| 1 | **The sandbox gap** | **Split.** The design half is discharged: ADR-0034 defines the rungs, the profile and the appraisal for Build. The mechanism half is open: every reference lease is rung 0, and ADR-0036 (Proposed) is the first step, a rung-1 launcher whose first profile declares P3 failing. ADR-0022 §6 stays Proposed until Run is covered |
| 2 | **Floor fitness** | Open, unowned |
| 3 | The clock model | Discharged (G3) |
| 4 | **ADR-0021** | Proposed, unchanged |
| 5 | **ADR-0005** | Proposed, unchanged; ADR-0033's K row still a debt against it |
| 6 | **The ADR-0008 and ADR-0017 supersessions** | Unwritten. ADR-0017's rung-1 question gains a second dimension from ADR-0035 finding 2 |
| 7 | **The archetype-evolution record** | Unwritten. The 09.27 rung-DAG analysis (`derived/`) sketches it as a lattice of order ideals over a theorem DAG, and names the binding table it needs first |
| 8 | **R8** | Drafted, pending; four conditions unmet |
| 9 | The per-class floor question | ADR-0014, reserved |
| 10 | **Re-genesis migration** | Open |
| 11 | **Custody** | (1, 0) |
| 12 | **Derived documents** | Partly regenerated: a glossary (09.26), a critical review (09.25), five analyses (09.26–27). The 09.12–09.17 set is still stale |
| 13 | **Run's alphabet** | Open. ADR-0034 carries the Run profile as a debt against it |
| 14 | The ToO, revision 7 | **Discharged** (09.25). Revision 8 is cut with this checkpoint |
| 15 | **Solver trust** | Open |
| 16 | **The TCB declaration record** | Unwritten. Now owed ADR-0034 §6's rows per rung and ADR-0036 §5's rows for the launcher |
| 17 | **Decoder–alphabet compatibility** | Open |
| 18 | **Bundle signing** | Open |
| 19 | The attestation-rung record | **Discharged** by ADR-0034 (B10) |
| 20 | **The provenance independence criterion** | **Written** as ADR-0035, Proposed at R2. `Contained` waits on it (ADR-0034 §4). Conditions 1, 2 and 4 of its §8 pass; 3 and 5 are owed (items 30, 33) |
| 21 | **Persona expiry; lineage and independence** | Lineage moved to ADR-0035. Expiry open |
| 22 | **Lifting a revocation** | Open |
| 23 | **Replica authentication and Byzantine replicas** | Open |
| 24 | **Finding 9**, proposer retry | Open |
| 25 | **The genesis floor text and S**, DRAFT | Open |

**New since G3.**

| # | Item | Where it sits |
|---|---|---|
| 26 | **The Run profile** | ADR-0034 debt, blocked on item 13 |
| 27 | **The verifier key in issued rules** | ADR-0034 debt against ADR-0025 §1 and the rules schema |
| 28 | **Evidence and lineage retention** | ADR-0034 and ADR-0035 debts against the archive (`mechanism/` G9) |
| 29 | **Platform TCB updates; accelerator attestation** | ADR-0034 open obligations |
| 30 | **θ values, θ<sub>gen</sub> and β; the near-duplicate tool** | ADR-0035: set from measurements at training scale, not before |
| 31 | **The ADR-0024 amendment** carrying ADR-0035 §5's tally condition; corpus admission declarations; a `feedback` field | ADR-0035 open obligations |
| 32 | **ADR-0035 finding 1 of ADR-0036**: tools run node-side, so a training round under the launcher is not ingress-bounded for its trainer | ADR-0035 owes an R3 |
| 33 | **The best-practice review of ADR-0035's bound**, by someone other than its author; and whether ADR-0029 needs a criterion for markings of this kind | ADR-0035 §8 condition 5; §4 here |
| 34 | **ADR-0036's ratification run**: the profile file, one honest round at rung 1, three refusals, a rung-0 principal beside it | ADR-0036 §7 |
| 35 | **The launcher in `topak-node`**, with an ADR-0033 addendum and a promoted profile | ADR-0036 §6 |
| 36 | **A P3-passing image**: no interpreter reachable from the occupant | ADR-0036 §4; the hermetic-shell record ADR-0034's Options names |
| 37 | **The ToO, revision 8** | Cut with this checkpoint; narrates through ADR-0036 |
| 38 | **The 09.26 accounting's remaining discrepancies**: no declared entry follows ADR-0023 §6's schema as a table; "declaration" means two things; the custody row for the corpus itself; stale vocabulary in the 09.13–09.17 derived set | Unowned; the accounting is in `derived/` |

**Not on this list, deliberately:** bootstrap itself, as at G2 and G3.

---

## 8. What G4 does not claim

- **Nothing here is independently reviewed.** Every ratification and revision since G3 was made by the person who
  drafted it, on the day of drafting. ADR-0029 A2 makes a full-corpus review a bootstrap precondition; none has begun.
- **No theorem is proved.** The TLA+ artifacts discriminate and check non-vacuity at small constants.
- **No principal is `Contained`.** ADR-0034 in force makes the missing premise the criterion (ADR-0035, Proposed)
  instead of the absence of rung semantics. Every reference lease is rung 0; no rung-1 lease has been issued;
  ADR-0036 is Proposed.
- **ADR-0035's measurement rule is the custodian's design**, reviewed by nobody, and the record says so.
- **The reference is not the mechanism** (ADR-0033 §1). Its 09.28 run is evidence of the same kind as before.
- **No floor is ratified, no deployment conforms, and no deployment declaration has been written.**
- **The corpus is not closed.**

---

## 9. Manifest

`SHA256SUMS-G4` · 108 entries, cut from commit `b43ce69` plus this checkpoint, revision 8 and the two manifests
added with them.

As at G2 and G3, the manifest's own digest cannot appear inside the file it measures, and this checkpoint is an
entry in it; both are recorded where they are cut, in the commit that adds them.

| Area | Entries |
|---|---|
| `decisions/` | 35 records |
| `checkpoints/` | 13 — six Theory of Operation cuts, the v1 corpus manifest, revisions 6, 7 and 8, G1, G2, G3 and G4 |
| `derived/` | 14 dated artifacts |
| `spec/` | 29 — eleven modules including the two successors, run scripts, dated results |
| `floor/` | 7 — unchanged since G3 |
| root | 10 — six process logs, three reference manifests, and the `slm/` tree manifest |

The reference trees are measured by `SHA256SUMS-REF-2026.09.24`, `-25` and `-28`; the rehearsal tree by
`SHA256SUMS-SLM-2026.09.28`; this manifest measures those four in turn.

Verify from the repository root:

```sh
shasum -a 256 -c SHA256SUMS-G4 | grep -c ': OK$'                  # expect 108
shasum -a 256 -c SHA256SUMS-SLM-2026.09.28 | grep -c ': OK$'      # expect 40
shasum -a 256 -c SHA256SUMS-REF-2026.09.28 | grep -c ': OK$'      # expect 60 of 61; see below
```

**`SHA256SUMS-REF-2026.09.28` fails one entry, and should.** It measures `5b25245`. Batch 11 then re-pinned
ADR-0033 in `mechanism/corpus-pins.sha256`, as its addendum says the pin line does whenever the record moves. No code
changed. `SHA256SUMS-REF-2026.09.25` fails five, as ADR-0033 A1 lists.

**`SHA256SUMS-G3` fails five entries**, by construction: 0015 (E2), 0029 (A2), 0022 (B10), 0031 (A1, B10) and 0033
(A1), each recorded in §1 or §6. G3's manifest remains the record of G3's cut.

The manifest excludes, as G3's did, everything that is not a corpus artifact: material not ours to redistribute,
the exports and archives, the TLA+ jar and its installer, earlier manifests, working directories (`tlc/`,
`tlc-workers/`, `diagrams/`), `doc/` and `sessions/`, the licence and notice files and the README. `mechanism/`,
`policies/` and `slm/` are measured by their tree manifests, not directly.
