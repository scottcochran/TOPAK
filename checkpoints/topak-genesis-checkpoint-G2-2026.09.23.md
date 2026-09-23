# TOPAK — Genesis Checkpoint G2

**2026.09.23** · genesis custodian: Scott, (1, 0) · supersedes G1 (`f46e88dafbc38f7d04a2af8c75b0ca879748c9178186357d09fd81e6461da1f1`) as the state of record · narrative: `topak-theory-of-operation-2026.09.23-rev6.md`

**What G2 is.** The state of record: what each record says, what was ratified and by whom, what is owed, and what is
open. The narrative is rev 6; it explains the design and decides nothing. Where the two disagree, this document wins.

**What changed at G2.** G1 froze a corpus in which the bootstrap core was drafted but unratified and nine findings
sat unresolved against it. G2 records the first ratifications: **fourteen records and amendments in four batches**,
the disposition of all eighteen step-6 findings, and three checked TLA+ artifacts. Two of the five bootstrap modules
now exist. **The bootstrap trigger is still unmet, and remains optional.**

---

## 1. Ratification record

Ratified 2026.09.23 by the genesis custodian under ADR-0029 §2. Batches ran in dependency order.

| Batch | Contents | Notes |
|---|---|---|
| **1 · Errata** | 0002 E1 · 0018 E1 · 0019 E1 · 0020 E1 · 0029 S4-1 (as E1) | No decision content. Pointer and citation fixes to accepted records |
| **2 · Bootstrap core** | 0025 · 0026 · 0027 · 0024 · 0022 §1–§5, §7, §8 · 0002 A1 · 0010 A1, A2 | None may be confirmation-required (ADR-0029 §4 exception). **0022 §6 deliberately excluded** |
| **3 · Claims** | 0023 (C3) · 0015 (C2) | Both confirmation-required |
| **4 · Privileged paths** | 0028 (C1) → then 0013 (C1, C4) · R6 effective | Order forced: the forensic floor before the mechanism whose NC-2 is checked against it |
| **After** | 0029 A1 | Bootstrap invariant renamed; see §6 |

### 1.1 Record status at G2

| Status | Count | Records |
|---|---|---|
| Accepted (genesis) | 19 | 0001, 0002, 0003, 0004, 0007, 0008, 0010, 0012, 0016, 0017, 0018, 0019, 0020, **0022 (in part, §1.2)**, 0024, 0025, 0026, 0027, 0029 |
| Accepted (genesis) · confirmation required | 6 | 0006, 0009, 0013, 0015, 0023, 0028 |
| Proposed | 2 | 0005, 0021 |
| Tombstone | 1 | 0011 |
| Reserved, no file | 2 | 0014, 0030 |

28 record files; 0014 and 0030 are reserved numbers with no file, so the numbering runs to 0030 with 0011 tombstoned.

**No record carries a pending amendment or erratum.** Every `Pending:` field reads none.

### 1.2 What is ratified in part

**ADR-0022.** §1–§5, §7 and §8 are Accepted (genesis). **§6 is not**, and stays Proposed. §6 states the confinement
obligation and does not deliver it, so Build containment theorems remain conditional and Build principals are
`Mediated`, not `Contained`. Ratifying §6 would carry C2 and is therefore also barred from the bootstrap set.

The debt sits on the face of that record. It differs from the ADR-0006 and ADR-0009 debts in one way that matters:
those owed their discharge to a record that did not exist and has since been written. **§6 owes its discharge to a
mechanism that does not exist, and no record can supply it.**

---

## 2. The rules floor as ratified

Genesis contents: **R1, R2, R5, R6, R7, R9**.

| Entry | Bound | State |
|---|---|---|
| R1 | `quorum = "all"` over counted grant seats | In force |
| R2 | `minGrant ≥ 2` | In force |
| ~~R3~~ | `recuse = TRUE` | **Withdrawn 09.23.** Recusal is a mechanism constant in the `Vote` envelope; no issued value exists to bound. ID reserved |
| ~~R4~~ | Vote timeout ⇒ deny | Withdrawn 09.15. ID reserved |
| R5 | No key both in the anchor key set and on the promotion roster | In force |
| R6 | Floor-exception count ≤ 2 | **Effective 09.23** with ADR-0013 |
| R7 | No break-glass grant may authorize `Issue`, `Vote`, or promotion | In force |
| R8 | Break-glass grant TTL | **Reserved**, candidate. The cheapest outstanding monotonicity repair |
| R9 | `quorum = "all"` ∨ `quorum ≥ 2` | **Added 09.23.** Conditional entry: binds only once R1 is relaxed |

**The mechanism it bounds.** `quorum` is `"all"` or a grant-vote threshold *k*; `"any"` is withdrawn. `minGrant` is
issued. Recusal is not issued. A timeout is never a grant.

**R9 is a new kind of entry** and should be read as such: it bounds declared degeneracies rather than the archetype,
and it does not satisfy the independence test as ADR-0026 §6 states it, because every rule set R9 excludes is also
excluded by R1. Its independence is stated relative to a floor without R1 — the only case in which it binds.

---

## 3. Verified artifacts

| Artifact | SHA-256 (16) | Records | Result |
|---|---|---|---|
| `spec/RulesFloorNV.tla` | `1468d8bab89bb076` | ADR-0026 §6 | G1 artifact, frozen. Non-vacuity against ADR-0024 rev 4 |
| `spec/RulesFloorNV_rev5.tla` | `3034df144d75ec3a` | ADR-0026 §7 | Non-vacuity against ADR-0024 rev 5, with the `Vote` envelope modeled |
| `spec/NonComposition.tla` | `119f9a7e878f8929` | ADR-0013 §4, §6 | NC-1 and NC-2, two mutations, three reachability witnesses |
| `spec/RulesFloorBase.tla` | `cf2351de2b39cccf` | — | Shared floor definitions; the live definition |
| `spec/Anchor.tla` | `a70187ef43058848` | ADR-0029 §5 | `FloorPreserved` |
| `spec/BreakGlass.tla` | `2c3c3d75aba2a599` | ADR-0029 §5 | `BreakGlassNeverChangesAuthority` |

Results files are dated alongside each. Both `RulesFloorNV*` files are cited by digest in an accepted record and are
never edited; `RulesFloorBase.tla` is the live floor definition and is expected to diverge from their frozen copies.

**Two results the drafting did not anticipate**, both from the 09.23 rerun:
1. **R9's independence is conditional** (§2).
2. **The 09.15 model was too small to check R1** once `quorum` became a threshold. With four humans, R5 removes the
   anchor key-holder and recusal removes the author, leaving two counted seats — and *k* ≥ 2 over two seats **is**
   unanimity, so the R1 mutation held vacuously. Five humans fixes it. **A threshold mechanism needs at least three
   counted seats before any threshold property means anything.**

**What these checks are.** Evidence, not attestation. Small constants, single artifacts, envelopes rather than the
Rego that implements them, written and run by the author. They are discrimination tests and precursors to the
bootstrap modules, not proofs.

---

## 4. Genesis debt ledger (ADR-0029 §7)

**Confirmation-required count: 6.**

| Record | Criterion | What the first quorum has to review |
|---|---|---|
| 0006 Erasure | C1, C4 via 0013 | Privileged-path proof obligation; debt discharged pending confirmation |
| 0009 Break-glass | C1, C4 via 0013 | As above |
| 0013 Exception mechanism | C1, C4 | NC-1 and NC-2 as author-run checks; demand type 5 declined |
| 0015 Effects are boundary crossings | C2 | Two exhaustiveness claims, one unenforced while the sandbox gap stands |
| 0023 Degeneracy | C3 | Reverses ADR-0008 and ADR-0017 in effect, with no superseding record written |
| 0028 Forensic floor | C1 | Four open obligations carried into confirmation rather than cleared |

**Bootstrap specification: partial.** Two of five modules exist.

| Module | Invariant | State |
|---|---|---|
| `Genesis` | `GenesisSatisfiesFloor` | Not written — needs the genesis rules contents |
| `Anchor` | `FloorPreserved` | **Drafted and checked 09.23** |
| `RulesFloor` | `PromotionMeetsIssuedQuorum` | Not written — needs epoch, vote-triple and veto-seat modeling |
| `Promotion` | `StaleVotesNeverCount` | Not written — as above |
| `BreakGlass` | `BreakGlassNeverChangesAuthority` | **Drafted and checked 09.23** |

**Two debts that no confirmation repays.**
- **The bootstrap set (0024–0027) can never be confirmation-required**, because confirmation runs under it. Its only
  reviews are the author's passes before ratification.
- **ADR-0013 and ADR-0028 gave up a structural reviewer** when they moved from post-bootstrap into genesis. The
  post-bootstrap phase would have supplied one through ADR-0024 recusal. The confirmation promotion repays it later;
  nothing repays it in the meantime.

---

## 5. Conventions carried at G2

- **G-C1 stands.** Identity is the SHA-256 of a file's bytes.
- **G-C3 stands.** Status vocabulary and the Reserved label.
- **Dated revisions (S6-18).** When two cuts share a date, the file name carries a revision suffix. rev 5 and rev 6
  follow it. This retires the G1 collision between two 2026.09.15 Theories of Operation.
- **Corpus layout.** `decisions/`, `checkpoints/`, `derived/`, `spec/`, process logs at the root. G-C4's Project-path
  mapping is retired: corpus path is the path.
- **Frozen artifacts.** A file cited by digest in an accepted record is never edited. A correction is a new dated
  artifact, and the citation moves with a record change.

---

## 6. Records changed after their own ratification

One case, and it is the amendment test working rather than a defect.

**ADR-0029 A1**, ratified 09.23. The bootstrap trigger named the `RulesFloor` invariant
`NoPromotionWithoutAllGrantSeats`. That name was true when written and was made false the same day by ADR-0024
revision 5, which makes `quorum` an issued value. A bootstrap module carrying the old name would either check a
weaker mechanism than the one deployed or contradict its own title under any promotion degeneracy. It now reads
**`PromotionMeetsIssuedQuorum`**; unanimity remains the archetype value under R1.

---

## 7. Open list at G2

**Blocking nothing, but unresolved.**

| # | Item | Where it sits |
|---|---|---|
| 1 | **The sandbox gap.** No mechanism enforces confinement | ADR-0022 §6, unratified; ADR-0015's C2 claim rests on it |
| 2 | **Floor fitness (NIST MEASURE 2.13).** The fourth gate | Unowned. Correlated review failure is untouched without it |
| 3 | **The clock model.** Leases, fencing and vote timeouts rest on it | Open with a known answer |
| 4 | **ADR-0021.** Corrected for quorum promotion, still Proposed | Blocked on the ADR-0003 tiered-storage conflict |
| 5 | **ADR-0005.** Still Proposed | Blocked on the Observer quarantine-gate question |
| 6 | **The ADR-0008 and ADR-0017 supersessions.** Reversed in effect, never superseded | Unwritten. The 0008 record must also name the veto-seat holder |
| 7 | **The archetype-evolution record.** Versioning, dominance, non-increasing TCB | Deferred from ADR-0023. Until it exists, nothing bounds *how* the archetype grows |
| 8 | **R8**, the break-glass TTL | Candidate entry |
| 9 | **The per-class floor question** | Deferred to ADR-0014, reserved and unwritten. Now applies to two floors |
| 10 | **Re-genesis migration**, including inherited forensic read access | Required before ADR-0028's confirmation |
| 11 | **Custody.** (1, 0) today; an archetype bootstrap needs five humans | A solo bootstrap is not a bootstrap |
| 12 | **Derived documents** — glossary, feature list, boundary register — predate 09.23 | Regenerate after this checkpoint |

**Not on this list, deliberately:** bootstrap itself. The trigger is permission, not obligation, and genesis may
continue indefinitely.

---

## 8. What G2 does not claim

- **Nothing here is independently reviewed.** Twenty-two records were ratified by one person in one day.
- **No theorem is proved.** Three TLA+ artifacts discriminate and check non-vacuity at small constants.
- **No deployment conforms.** No degeneracy declaration has been written, and nobody ships the archetype.
- **The corpus is not closed.** ADR-0023's admission test grows the archetype whenever a variation fails it.

---

## 9. Manifest

`SHA256SUMS-G2` · 64 entries

The manifest's own digest cannot appear inside the file it measures, and this checkpoint is itself an entry in it,
so the two are recorded where they are cut: in the commit that adds them, and in the signed tag if one is made. A
reader verifies the tree against the manifest, then the manifest against that record.

| Area | Entries |
|---|---|
| `decisions/` | 28 records |
| `checkpoints/` | 9 — five Theory of Operation cuts, the v1 corpus manifest, G1, G2, and rev 6 |
| `derived/` | 7 dated artifacts, all predating 09.23 and due for regeneration |
| `spec/` | 14 — six modules, run scripts, dated results |
| root | 6 process logs |

Verify from the repository root:

```sh
shasum -a 256 -c SHA256SUMS-G2 | grep -c ': OK$'    # expect 64
```

The manifest excludes `references/`, which is not ours to redistribute, and the TLA+ jar, which
`install-tla.sh` fetches by version. G1's manifest remains valid at G1's paths; **it does not verify against this
tree**, because the layout convention in §5 moved the records into `decisions/` after G1 was cut.
