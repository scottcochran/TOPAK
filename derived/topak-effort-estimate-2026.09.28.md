I'll look at the repository to find how debt is tracked, then produce an estimate.

The README points to Genesis Checkpoint G4 as the state of record for what is "owed and open". I'll read that plus the mechanism gaps document and search the corpus for debt tracking.

Now that I have the state-of-record ledger, I'll pull the underlying definitions to size each item: ADR-0029's debt ledger rules, the referenced G2/G3 entries, ADR-0035/0036's owed work, R8's conditions, the rung-DAG sketch, and the reference code's size and provisional markers.

I've got most of the ledger, but some sections didn't print due to heading formatting differences. I'll now pull ADR-0036's launcher scope, ADR-0029's ledger rules, ADR-0034's TCB rows, and ADR-0035's ratification conditions in one pass.

I have enough data to size each item. Next, I'll check an existing derived document's header format and the repo's Claude settings so the new deliverable matches the corpus style.

Analysis is complete. The repository's own settings deny file writes, commits and pushes in this repo (`.claude/settings.json`), and the earlier analyses in `derived/` are pasted chat answers, so the estimate is delivered here rather than committed to the branch.

## What counts as debt at G4

The state of record is Genesis Checkpoint G4 (2026.09.28). It carries four debt registers, which overlap:

- **Open list, §7:** 34 items still open out of 38 (items 3, 14, 19 and 37 are discharged).
- **Debt ledger, §4:** 11 confirmation-required records, a bootstrap specification with 3 of 5 TLA+ modules unwritten, and four kinds of debt no confirmation repays.
- **Reference gaps:** G1 to G17 in the mechanism's gaps file, with 17 `PROVISIONAL` sites in the Rust crates.
- **Record-level obligations:** ADR-0034 (6), ADR-0035 (9) and ADR-0036 (7), plus six unresolved discrepancies from the 09.26 accounting.

Deduplicated, that is about 55 units of work. They split three ways: work only other people can do, work the custodian can do, and work blocked on measurements that do not exist yet.

**Calibration.** The git history covers 09.23 to 09.28. In those six days one person produced ADR-0030 through 0036, the 6.5k-line Rust reference, the 1.5k-line SLM tree, five TLA+ modules, three checkpoints and three Theory of Operation revisions. A "custodian-day" below means one day at that cadence, with the same tooling. The remaining items are the hard tail that was deferred, so extrapolating the genesis pace understates them. Ranges are deliberate.

## Effort by group

**Group A: not repayable by the custodian.** These gate bootstrap and `Contained`, and no amount of custodian effort clears them.

| Debt | Who | Effort | Custodian follow-up |
|---|---|---|---|
| Independent full-corpus review (ADR-0029 A2; G4 §8 says none has begun) | A reviewer who is not the author | 15–25 reviewer-days for ~6.5k lines of records, 13 checkpoints, 14 derived docs, 1.4k lines TLA+, 6.5k Rust, 1.5k Python, the floor | 5–10 days to disposition findings, judging by the 09.16 and 09.25 reviews |
| Best-practice review of ADR-0035's bounded-share rule (item 33) | Someone other than the author | 1–3 reviewer-days | 1–2 days for an R3 |
| Confirmation of 11 records by the first quorum | Post-bootstrap quorum | Not estimable before bootstrap | None until then |
| θ values, θgen and β (item 30) | Training-scale measurement | Needs corpora and compute; not estimable here | 1–2 days to pick and pin the near-duplicate tool |
| Custody at (1, 0) (item 11) | Key-holder recruitment | Not effort | None |
| Four debts no confirmation repays (§4) | Structural | Only mitigated by the review above | None |

**Group B: records to write or amend.** Custodian design work.

| Item | Work | Custodian-days |
|---|---|---|
| 13 Run's alphabet | New record, ADR-0022's twin for Run. Unblocks 26, ADR-0022 §6 for Run, G3, the floor's Run half and three provisional code sites | 3–5 |
| 26 Run profile | ADR-0034 amendment, after 13 | 1–2 |
| 6 ADR-0008 and ADR-0017 supersessions | Two records; 0017 gains ADR-0035 finding 2's dimension | 3–5 |
| 7 Archetype-evolution record | Theorem-to-premise binding table first, then the record with bottom, index and movement rule | 5–8 |
| 16 TCB declaration record | Rows owed by ADR-0030, ADR-0033 §3, ADR-0034 §6 and ADR-0036 §5 | 2–3 |
| 27 Verifier key | ADR-0025 §1 amendment plus the rules schema | 1–2 |
| 28 Evidence and lineage retention | Archive design record; code is in group D | 2–3 |
| 29 Platform TCB updates; accelerator attestation | ADR-0034 amendments; accelerator part is partly research | 2–4 |
| 31 ADR-0024 amendment, admission declarations, `feedback` field | ADR-0035 obligations | 2–3 |
| 32 ADR-0035 R3 for ADR-0036 finding 1 | | 0.5–1 |
| 8 R8 break-glass TTL | ADR-0013 companion (C1), a `T_BG` derived from `D`, the clock decision, a new non-vacuity artifact | 2–3 |
| 4 ADR-0021 | Reconcile ADR-0003's no-tiered-storage clause, then ratify | 1–2 |
| 5 ADR-0005 and the K row | Needs the Observer quarantine-gate question settled | 2–3 |
| 9 Per-class floor (ADR-0014) | Reserved, scope unknown | 1–3 |
| 10 Re-genesis migration | Inherited forensic read access | 2–4 |
| 2 Floor fitness (MEASURE 2.13) | Unowned; an open research question | 3–5, low confidence |
| 15 Solver trust | | 1–2 |
| 17 Decoder and alphabet compatibility | | 1–2 |
| 18 Bundle signing record | | 0.5–1 |
| 21 Persona expiry | | 1 |
| 22 Lifting a revocation | | 1–2 |
| 23 Replica fault model | Record only; BFT consensus itself would be weeks and is out of scope | 2–3 |
| 25 Genesis floor text and S | Review pass and a ratification batch | 1–2 |
| 36 Hermetic-shell record | Named in ADR-0034's Options | 2–3 |
| **Subtotal** | | **42–72** |

**Group C: TLA+ work.**

| Item | Work | Custodian-days |
|---|---|---|
| Bootstrap spec: `Genesis`, `RulesFloor`, `Promotion` | Including decide-then-commit and ADR-0035's tally condition | 3–5 |
| 24 Paxos module with proposer retry | The module the Theory of Operation calls for | 2–3 |
| Discrepancy 8 | A rung-0 row in `Confinement.tla` | 0.5 |
| **Subtotal** | | **5.5–8.5** |

**Group D: reference mechanism.** Code work, most of it waiting on a record above.

| Item | Work | Custodian-days |
|---|---|---|
| 34 ADR-0036 ratification run | Profile file, one honest round, three refusals, a rung-0 principal beside it, dated results | 1–2 |
| 35 Launcher in `topak-node` | Plus ADR-0033 addendum, promoted profile, renewal, profile schema | 3–5 |
| 36 P3-passing image | Compiled occupant on a scratch base | 2–4 |
| G2 Provenance constant | Becomes a check of issued rules once ADR-0035 is in force | 1 |
| G3 Run actions | After item 13 | 1–2 |
| G4 Wasm tool host (P4) | | 3–5 |
| G5 Authentication | mTLS between replicas, operator and principal identity | 2–4 |
| G6 Genesis rules and anchor ceremony tooling | | 3–5 |
| G7 Bundle signing | | 1–2 |
| G8 Gate runner and evidence attestation | | 2–3 |
| G9 Archive, plaintext store, horizon, audit read path | | 5–10 |
| G10 R8 TTL | After item 8 | 1 |
| G11 Erasure | Nothing to exercise at genesis; deferrable | 3–5 |
| G12 Observer, quarantine gate, correlator | After ADR-0005 and ADR-0021 | 5–10 |
| G13 Persona attestation | | 1–2 |
| G14 Log compaction and snapshots | | 2–3 |
| G15 Per-principal ordering | After ADR-0005 | 1–2 |
| **Subtotal** | | **37–66** |
| Rung 2 launcher (Firecracker or Kata, launch measurement) and its record | Beyond ADR-0036's first step | 5–10 |
| Rung 3 (confidential VM, independent verifier) and its record | The archetype; needs hardware access | 10–20 |

**Group E: housekeeping.**

| Item | Work | Custodian-days |
|---|---|---|
| 12 Stale derived set (09.12 to 09.17) | Regenerate or retire six documents | 2–3 |
| 38 Accounting discrepancies 4, 5, 6, 7, 9, 10 | Schema tables, the two meanings of "declaration", the corpus's own custody row, stale vocabulary | 2–3 |
| Checkpoint and Theory of Operation cuts | Three to five more cuts along this path | 4–8 |
| **Subtotal** | | **8–14** |

## Totals and critical path

| Scope | Custodian-days |
|---|---|
| Groups B to E plus review disposition | 100–170 |
| Adding rungs 2 and 3 | 115–200 |
| Reviewer-days, separately | 16–28 |

At the observed pace that is five to eight months of continuous single-person work. The number matters less than its shape, because ADR-0029 §7 says genesis may continue indefinitely and the debt is visible, not bounded. Three subsets have different gates:

1. **Bootstrap-eligible** needs only the three missing TLA+ modules and the independent review, so about 3–5 custodian-days plus 15–25 reviewer-days plus 5–10 days of dispositions. Under A2.1, every other finding may be carried as named debt. Nothing here has started, and the blocker is recruiting a reviewer, not effort.
2. **A first `Contained` principal** needs ADR-0035 ratified, which waits on θ values from training-scale measurement and the outside review of its bound. It also needs items 34 to 36. Custodian effort is about 10–18 days. The measurement is the blocker.
3. **The archetype at rung 3** is the long pole: 15–30 further custodian-days, hardware access, and a rung-2 record on the way.

Everything else is long tail. The single largest custodian item is the archetype-evolution record, because it needs a binding table across roughly 30 records before any of it can be written. The largest code item is the archive, which three separate debts (items 28, G9, and ADR-0035's retention obligation) resolve to.

If you want this in the repo, it fits the `derived/` convention as a dated analysis. I could not write or push it: this repository's Claude settings deny writes, commits and pushes.
