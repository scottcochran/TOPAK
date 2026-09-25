# TOPAK — Genesis Checkpoint G3

**2026.09.25** · genesis custodian: Scott, (1, 0) · supersedes G2 (`b1eee72a66c8255993d642bbe24199a8078d5cd03c790cb86cbedbfaae1b9fd8`) as the state of record · narrative: `topak-theory-of-operation-2026.09.23-rev6.md`, with rev 7 owed (§7)

**What G3 is.** The state of record, as G2 was: what each record says, what was ratified and by whom, what is owed,
and what is open. Rev 6 remains the narrative and now lags this document; where the two disagree, this document wins.

**What changed at G3.** G2 froze a corpus whose mechanism existed only on paper. Between the cuts, four records were
written, a reference implementation of the admit path was built and run, and its eleven findings were routed to the
records that own them. G3 records **eleven ratifications**: two on 2026.09.23 after G2's cut, and nine in **Batches 5–9**
on 2026.09.25. Ten of the eleven findings are closed. **The bootstrap trigger is still unmet, and remains optional.**

---

## 1. Ratification record

All by the genesis custodian under ADR-0029 §2.

| Batch | Date | Contents | Notes |
|---|---|---|---|
| *After G2* | 09.23 | 0032 · 0024 A1 | The clock model, ratified as authored; 0024 A1 strikes the clock obligation 0032 discharges. 0032 carries a `B5` tag but was not a batch |
| **5 · Lease and topics** | 09.25 | 0003 A1 · 0003 A2 (C1) · 0031 (C1) | 0003's amendments come from reference findings 4 and 11; 0031 at R3, after findings 2, 5 and 6 were decided |
| **6 · Floor** | 09.25 | 0030 (C1) · 0022 A1 | Together: 0030's resolution of recusal depends on 0022 A1. The genesis floor text stays DRAFT |
| **7 · Reference** | 09.25 | 0033, whole | Not confirmation-required. §2's Kafka row carried as a debt against ADR-0005 |
| **8 · Pointers** | 09.25 | 0015 E1 · 0031 E1 | Errata: pointers to ADR-0033 §4. Closes findings 3, 7 and 8. ADR-0033 takes a dependent entry (B8) |
| **9 · Erratum** | 09.25 | 0033 E1 | ADR-0033 §7's addendum sentence on later changes under `mechanism/`, found while cutting this checkpoint (§6) |

### 1.1 Record status at G3

| Status | Count | Records |
|---|---|---|
| Accepted (genesis) | 20 | 0001, 0002, 0004, 0007, 0008, 0010, 0012, 0016, 0017, 0018, 0019, 0020, **0022 (in part, §1.2)**, 0024, 0025, 0026, 0027, 0029, **0032**, **0033** |
| Accepted (genesis) · confirmation required | 9 | **0003 (for A2 only)**, 0006, 0009, 0013, 0015, 0023, 0028, **0030**, **0031** |
| Proposed | 2 | 0005, 0021 |
| Tombstone | 1 | 0011 |
| Reserved, no file | 1 | 0014 |

32 record files, numbered to 0033. 0030 was reserved at G2 and is now written; 0014 is the only reserved number.

**One pending amendment:** ADR-0026 A1 (R8, the break-glass TTL), drafted 2026.09.24. Its note sets four conditions
for ratification, and none is met (§7, item 8). Every other `Pending:` field reads none.

### 1.2 What is ratified in part, or with a scoped marking

**ADR-0022.** Unchanged from G2: §1–§5, §7 and §8 are Accepted; **§6 is not**. A1 (Batch 6) amends §7 only.

**ADR-0003.** The record is Accepted from 09.11; its confirmation marking, added at Batch 5, covers **A2 only**. A2
adds a companion topic to the unit of erasure, a claim over the erasure path. A1 carries no marking. This is the first
confirmation marking scoped to an amendment rather than a record.

---

## 2. The floors as ratified

### 2.1 The rules floor

Unchanged since G2. Genesis contents: **R1, R2, R5, R6, R7, R9**; R3 and R4 withdrawn, IDs reserved.

**R8** has moved from candidate to **drafted**: ADR-0026 A1, pending. It is vacuous until a companion mechanism clause
makes a break-glass grant end — at the earliest of its TTL, the next epoch increment, and a targeted revocation of its
seat (revised 09.25 to track ADR-0031 R3). That companion touches a privileged path and carries C1.

### 2.2 The policy floor

**ADR-0030 is Accepted** (Batch 6, C1): the floor runs on a verified evaluator (Cedar, linked), composition is
monotone (`admit ⟺ floor_permit ∧ ¬bundle_deny`), the typed lift's schema is enforced per request, the gates are
decidable checks, and a floor change is routed by analysis: tightening is a promotion, relaxation or incomparable
revision is an anchor issuance and a promotion.

**The genesis floor text is not ratified.** `floor/genesis-floor.cedar` (14 policies) and `floor/genesis.cedarschema`
are **DRAFT**, gated 09.24 and linked by the reference under digest pins. Ratifying ADR-0030 ratified the language
and the machinery, not a floor.

**Recusal lives in the floor** as forbid B7 (ADR-0030 §10 finding 3; ADR-0022 A1). Relaxing it is a floor
relaxation, which is stricter than the mechanism release ADR-0022 §7 first named. The same holds for every envelope
constraint the floor states.

---

## 3. Verified artifacts

G2's six artifacts are unchanged and keep their digests. New since G2:

| Artifact | SHA-256 (16) | Records | Result |
|---|---|---|---|
| `spec/FloorComposition.tla` | `3d30a058d8f8d9d1` | ADR-0030 §9 | Five properties hold; four mutations caught (`M_OVERRIDE`, `M_ERR`, `M_FAILOPEN`, `M_WRITE`), and `EnvelopeHolds` survives `M_FAILOPEN` |
| `spec/FloorRouting.tla` | `9d4c0f5e03defc1e` | ADR-0030 §9 | `NoWideningWithoutIssuance` and `FloorNeverVacuous` hold; two mutations caught (`M_ROUTE`, `M_GATE`) |
| `spec/Lease.tla` | `7636c6c3364bca9c` | ADR-0031 §8 | Four properties in `Safe`, five witnesses, five mutations, rerun at R3: holds over 1,746,048 distinct states |
| `floor/genesis-floor.cedar` · `floor/genesis.cedarschema` | `9b6adeee0c2ae308` · `77d9b566d76134c3` | ADR-0030 §10 | **DRAFT.** Totality, non-vacuity, discrimination, every-entry-matters and routing gates, per action; three negative controls caught |
| Reference, run 2026.09.24 | manifest `30123422a84fa64b` | ADR-0033 §7 | 38 tests at commit `4fd9677`; live smoke run against Kafka and an OPA sidecar |
| Reference, run 2026.09.25 | manifest `dcad5e8e3236cbc7` | ADR-0033 §7 addendum | 44 tests at commit `453801c`; the live smoke run not repeated |

**Frozen from G3 on.** `Lease.tla`, `FloorComposition.tla` and `FloorRouting.tla` are now cited by digest in accepted
records, so G2's frozen-artifact convention applies to them. `Lease.tla` was revised in place twice on 09.25, for
ADR-0031 R1 and R3, while that record was Proposed; the convention permitted it. **`spec/Lease-results-2026.09.25.txt`
was overwritten between the two runs**, so the R1 run survives only in git history. §5 adds the rule that prevents it.

**Results the drafting did not anticipate**, since G2:
1. **`M_ROLE`.** A renewal that changed only the round role — voter to author — passed every check that looked at
   alphabet and rung. The role was authority and was not in the lease (ADR-0031 R1).
2. **Selective revocation was unreachable.** With one global epoch, `Lease.tla` could not distinguish revoking one
   principal from revoking all, so finding 5 was invisible to the check that should have caught it (ADR-0031 R3).
3. **Bundle fail-closed protects narrowings, not the floor** (ADR-0030 §9 finding 3). The same fact decided the
   bundle-fallback rule: a fallback not bound to the lease's revision would lift every narrowing during an outage.
4. **Three findings needed running code:** a gate case that did not test what it named, a Kafka topic reused across
   re-genesis, and a Paxos backlog that doubled per term (ADR-0033 §7, findings 1, 4, 9).

**What these checks are.** Unchanged from G2: evidence, not attestation. Small constants, written and run by the
author. The reference is evidence of the same kind, restated against running code, and **is not the verified
object** (ADR-0033 §1).

---

## 4. Genesis debt ledger (ADR-0029 §7)

**Confirmation-required count: 9**, up from 6.

| Record | Criterion | What the first quorum has to review |
|---|---|---|
| 0003 Round topics, **A2 only** | C1 | The `after` companion as part of the unit of erasure |
| 0006 Erasure | C1, C4 via 0013 | Unchanged from G2 |
| 0009 Break-glass | C1, C4 via 0013 | Unchanged from G2 |
| 0013 Exception mechanism | C1, C4 | Unchanged from G2 |
| 0015 Effects are boundary crossings | C2 | Unchanged; E1 is a pointer and adds nothing to confirm |
| 0023 Degeneracy | C3 | Unchanged from G2 |
| 0028 Forensic floor | C1 | Unchanged from G2 |
| **0030** Floor language and composition | C1 | ADR-0013's exceptions and ADR-0028's forensic classes re-expressed as floor entries |
| **0031** Lease | C1 | A targeted revocation lapses the seat's break-glass approvals |

**Bootstrap specification: partial.** Unchanged: two of five modules exist (`Anchor`, `BreakGlass`). **`Promotion`
now owes one more thing**: a model of decide-then-commit, ADR-0033 finding 8's remaining half.

**Two debts no confirmation repays**, both unchanged from G2: the bootstrap set can never be confirmation-required,
and ADR-0013 and ADR-0028 gave up a structural reviewer. **A third of the same kind:** every record in Batches 5–8 was
drafted, checked, implemented and ratified by one person within two days. ADR-0033's Negative consequences name it:
agreement among records, checks and code written by one hand is not independence.

---

## 5. Conventions carried at G3

G2's conventions stand: G-C1, G-C3, dated revisions, corpus layout, frozen artifacts. Added since G2:

- **A tree is cited by manifest.** A directory tree is cited by the digest of a SHA-256 manifest of its tracked
  files, together with the commit the manifest was taken from (ADR-0033 §1). G-C1 extended from files to trees.
- **Drift pins.** The reference pins the digest of every record and TLA+ module it follows
  (`mechanism/corpus-pins.sha256`, 24 pins). A test fails when a pinned file changes, or when the code cites a record
  that is not pinned. Re-pinning is the record that the change was reviewed against the code.
- **Confirmation marking may be scoped to an amendment** (ADR-0003, "for A2 only").
- **Pointer errata.** A pointer that one record's text promises another, adding no decision text, is erratum-class
  (ADR-0015 E1, ADR-0031 E1).
- **Dependent entries.** When one record's ratification discharges something another accepted record provided for,
  the second takes a "Ratification (dependent entry)" row and no decision text changes (ADR-0026 B4; ADR-0033 B8).
- **One results file per run.** A rerun writes a new file, suffixed like revisions when two share a date, and never
  overwrites the last. New at G3, after the `Lease-results-2026.09.25.txt` overwrite (§3).

---

## 6. Records changed after their own ratification

| Record | Change | Why |
|---|---|---|
| 0024 | A1, 09.23 | Recorded in G2's manifest note; carried here for completeness |
| 0003 | A1 and A2, Batch 5 | A record ratified 09.11, amended from two reference findings. Both add a sentence and strike none |
| 0022 | A1, Batch 6 | §7's relaxation path for recusal, overtaken when ADR-0030 moved the `Vote` envelope into the floor |
| 0015 | E1, Batch 8 | Pointer to ADR-0033 §4 |
| 0031 | E1, Batch 8 | Pointer to ADR-0033 §4, the same day the record was ratified |
| 0033 | B8, dependent entry | Findings 3, 7 and 8 marked closed; no decision text |
| 0033 | E1, Batch 9 | §7's addendum sentence on later changes under `mechanism/`, below |
| 0026 | A1's note, 09.25 | **Pending text, not ratified text.** The companion clause now names targeted revocation |

**One erratum, found while cutting this checkpoint.** ADR-0033's §7 addendum said the one later change under
`mechanism/` after commit `453801c` was that record's own pin line. Batches 7 and 8 then changed
`mechanism/GAPS-AND-ASSUMPTIONS.md` and three pin lines, all bookkeeping and no code, so `SHA256SUMS-REF-2026.09.25`
fails two entries (§9). The sentence was true when written. **ADR-0033 E1, ratified in Batch 9**, now reads: *later
changes under `mechanism/` are bookkeeping only — the assumptions register and the pin file — and no code.*

---

## 7. Open list at G3

**G2's twelve items, as they stand.**

| # | Item | At G3 |
|---|---|---|
| 1 | **The sandbox gap** | Open. ADR-0022 §6 still Proposed. The reference makes it concrete: an agent with a shell bypasses the MCP front door (ADR-0033 §6) |
| 2 | **Floor fitness** (MEASURE 2.13) | Open, unowned. ADR-0030's gates show the floor well-formed and non-vacuous, not right |
| 3 | **The clock model** | **Discharged** by ADR-0032, ratified 09.23 |
| 4 | **ADR-0021** | Proposed. Still blocked on ADR-0003's no-tiered-storage clause (0003.7); its alphabet blocker was discharged 09.24 (R2) |
| 5 | **ADR-0005** | Proposed, still held on the Observer quarantine-gate question. **Now also carries ADR-0033 §2's Kafka row as a debt** |
| 6 | **The ADR-0008 and ADR-0017 supersessions** | Unwritten |
| 7 | **The archetype-evolution record** | Unwritten |
| 8 | **R8**, the break-glass TTL | **Drafted** as ADR-0026 A1, pending. Four conditions unmet: the ADR-0013 companion clause, a value for `T_BG` derived from `D`, the clock decision, a non-vacuity run |
| 9 | **The per-class floor question** | ADR-0014, reserved and unwritten |
| 10 | **Re-genesis migration** | Open. ADR-0003 A1 removes one precondition — a successor can tell its topics from its predecessor's — and discharges nothing |
| 11 | **Custody** | (1, 0) |
| 12 | **Derived documents** | Not regenerated; now predate two checkpoints |

**New since G2.**

| # | Item | Where it sits |
|---|---|---|
| 13 | **Run's alphabet.** No record defines it | ADR-0030 debt; the floor's Run half, break-glass's envelope and the reference's Run actions are provisional |
| 14 | **The ToO, revision 7** | ADR-0030 debt (§1, §2.4 including the recusal sentence, §3.1, §11.3), and everything in this checkpoint rev 6 does not narrate |
| 15 | **Solver trust** for routing's "implies" results | ADR-0030 debt |
| 16 | **The TCB declaration record.** Unwritten | Owed the engine-divergence residual (ADR-0030) and, if the crash-recovery model is kept, the Byzantine-replica residual (ADR-0033 §3) |
| 17 | **Decoder–alphabet compatibility** under a change to S | ADR-0030 debt; ADR-0018 |
| 18 | **Bundle signing** | ADR-0030 §2 requires it; not implemented. Bundle identity is a content revision until it exists |
| 19 | **The attestation-rung record**: rungs 1–3, re-attestation, *Contested* | ADR-0031 debt; the discharge of ADR-0022 §6 |
| 20 | **The provenance independence criterion** | ADR-0031 debt. Until it exists `Contained` is unreachable at any rung |
| 21 | **Persona expiry; Persona lineage and independence** | ADR-0031 debts |
| 22 | **Lifting a revocation.** A revocation is permanent within the chain | ADR-0031 debt: lifting adds authority and no record says who may |
| 23 | **Replica authentication and Byzantine replicas** | ADR-0033 §3 and open obligations |
| 24 | **Finding 9**: proposer retry in the drafted Paxos TLA+ module | ADR-0033 §7 |
| 25 | **The genesis floor text and S**, DRAFT | Ratification of a floor, as distinct from the machinery that checks one |

**Not on this list, deliberately:** bootstrap itself, as at G2.

---

## 8. What G3 does not claim

- **Nothing here is independently reviewed.** Nine items were ratified on 2026.09.25 by the person who drafted them,
  each within two days of drafting.
- **No theorem is proved.** The TLA+ artifacts discriminate and check non-vacuity at small constants.
- **The reference is not the mechanism.** It is evidence (ADR-0033 §1). It fails assumption of use A1, every lease it
  issues is rung 0, and every principal it serves is `Mediated`.
- **No floor is ratified.** The genesis floor and S are drafts that pass the gates.
- **No deployment conforms,** and no degeneracy declaration has been written.
- **The corpus is not closed.**

---

## 9. Manifest

`SHA256SUMS-G3` · 86 entries, cut from commit `aa93da4` plus Batch 9 (ADR-0033 E1 and its pin) and this checkpoint.

As at G2, the manifest's own digest cannot appear inside the file it measures, and this checkpoint is an entry in it;
both are recorded where they are cut, in the commit that adds them.

| Area | Entries |
|---|---|
| `decisions/` | 32 records |
| `checkpoints/` | 10 — five Theory of Operation cuts, the v1 corpus manifest, rev 6, G1, G2 and G3 |
| `derived/` | 7 dated artifacts, unchanged since G2 and still due for regeneration |
| `spec/` | 22 — nine modules, run scripts, dated results |
| `floor/` | 7 — the DRAFT genesis floor and schema, gate driver, tests, results, generator |
| root | 8 — six process logs and the two reference manifests |

The reference trees, `mechanism/` and `policies/`, are measured by their own manifests, `SHA256SUMS-REF-2026.09.24`
and `SHA256SUMS-REF-2026.09.25`, which this manifest measures in turn. That keeps G3's manifest to the corpus and
lets a reader verify the code at the commits ADR-0033 cites.

Verify from the repository root:

```sh
shasum -a 256 -c SHA256SUMS-G3 | grep -c ': OK$'               # expect 86
shasum -a 256 -c SHA256SUMS-REF-2026.09.25 | grep -c ': OK$'   # expect 59 of 61; see below
```

**`SHA256SUMS-REF-2026.09.25` fails two entries, and should.** It measures commit `453801c`. Batches 7 and 8 then
changed `mechanism/GAPS-AND-ASSUMPTIONS.md` (the findings summary) and `mechanism/corpus-pins.sha256` (the pins for
ADR-0015, ADR-0031 and ADR-0033). No code changed, as ADR-0033 E1 now says (§6).
`SHA256SUMS-REF-2026.09.24` fails more, as ADR-0033 R1 already notes: it measures commit `4fd9677`.

**`SHA256SUMS-G2` no longer verifies against this tree**, by construction: six records it measured have changed —
0003, 0015, 0021, 0022, 0024 and 0026 — each through a change §1 or §6 records, a revision of 0021 while Proposed, or 0026's pending A1.
G2's manifest remains the record of G2's cut.

The manifest excludes, as G2's did, everything that is not a corpus artifact: material that is not ours to
redistribute (the two PDFs at the root), the chat and project exports and their archives, the TLA+ jar and its
installer, earlier manifests (`SHA256SUMS`, `-G1`, `-G2`), and working directories (`tlc/`, `tlc-workers/`,
`diagrams/`). It also excludes `sessions/`, `doc/` and the essay file at the root, none of which is tracked.
