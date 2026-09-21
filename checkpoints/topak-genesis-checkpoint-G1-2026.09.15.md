# TOPAK — Genesis Checkpoint G1

**2026.09.15** · cleanup step 5 · genesis custodian: Scott, sole, (1, 0) · under ADR-0029 (Accepted (genesis)) · supersedes corpus manifest v1

G1 is the corpus's state of record. It lists every file by digest, every record's status and
readiness, the findings from cleanup, the ratification queue, the genesis debt ledger, and the open
list. **It ratifies nothing,** and it adds no decision text.

**G1 is immutable once cut.** Corrections go into G2. The freeze (FREEZE-AND-BATCH-A §1) ends at the cut, so
ratification and revision resume against the digests below.

**What G1 supersedes.** Manifest v1 in full. As state of record, the 09.15 Theory of Operation rev 4 §0 (ledger),
§8 (ADR log), §9 (open list), §10 (genesis plan table and debt ledger), and §11 (next). Rev 4 stays in
force as narrative until the next Theory of Operation (cleanup step 6).

---

## 1. Conventions fixed at G1

These govern checkpoint format only. None is a design decision.

- **G-C1. Digests.** A file is identified by the full SHA-256 of its bytes (Appendix A). Tables show the first 16
  hex characters for display only.
- **G-C2. Revision identity (settles S4-2).** A record's revision is identified by its digest at a genesis
  checkpoint. History narrates revisions; it does not identify them. A revision from before G1 whose text is not in
  the corpus is identified by the corpus artifact that encodes it, if one exists, and otherwise is marked
  *not in corpus*.
  - **ADR-0024 revision 3** is not in corpus as text. Its `PromotionEnabled` snippet is encoded as mechanism
    `as0024` in `spec/RulesFloorNV.tla`. That artifact plus that label is ADR-0026 §6's non-vacuity baseline.
    The revision 3 text remains recoverable from session history (feature-list session, 09.15) if G2 wants it.
  - **ADR-0024 revision 4** is the text of `decisions/ADR-0024.md` at the G1 digest, and is also encoded as
    `rev4`.
- **G-C3. Reserved (settles S4-3).** A number that is assigned but has no record is *Reserved*. Reserved is a
  checkpoint label, not a status class: it has no file, no digest, and cannot be ratified.
- **G-C4. File names.** Corpus paths use dotted dates, as in the cleanup zips. The Project flattens them to
  underscores and drops directories. Content digests are unaffected.
- **G-C5. Custodian calls.** A call applied during cleanup and marked reversible is confirmed by this cut.
  Reversing one after G1 is a change recorded in G2.

---

## 2. Records

Readiness key, unchanged from manifest v1: **R** ratifiable now · **R·CR** ratifiable, confirmation required on
ratification · **N** not ratifiable (no decision text) · **BS** bootstrap set, cannot be confirmation-required ·
**—** already accepted, or tombstone. *CR* = confirmation required (ADR-0029 §4).

| # | Title | Status | Pending | Readiness | Digest |
|---|---|---|---|---|---|
| 0001 | Rename CI domain to `Build` | Accepted (genesis) |  | — | `3ce1bcf7e397b324` |
| 0002 | Apply `Contain` in Build as well | Accepted (genesis) | A1, E1 | A1: **R** · BS group · E1: **R** | `6ff6b77b7cb970ca` |
| 0003 | Topic per principal per round | Accepted (genesis) |  | — (S3-2 extension: **N**) | `a72a3716dc3e3dd1` |
| 0004 | Separate control-plane facts from cognitive payloads | Accepted (genesis) |  | — | `25dc46f47d302d33` |
| 0005 | Kafka is neither ordering authority nor system of record | Proposed |  | **R** | `b2fb45dcf09f7463` |
| 0006 | Erasure is a modeled event | Accepted (genesis) · CR (C1, C4 via 0013) |  | — | `c02c7e34927af5d4` |
| 0007 | Semantic judgment is never a lift | Accepted (genesis) |  | — | `e00717a28bfe001e` |
| 0008 | Observer replicas not colocated with the Thinker | Accepted (genesis) |  | — (supersession: **N**, CR when written) | `0a7dd249d3af7edf` |
| 0009 | Break-glass is modeled, quorum-witnessed | Accepted (genesis) · CR (C1, C4 via 0013) |  | — | `11056665d09940f2` |
| 0010 | Verified object = mechanism + minimal policy floor | Accepted (genesis) | A1, A2 | A1, A2: **R** · BS group | `64a59970c4356dbe` |
| 0011 | Observer placement | Tombstone |  | — | `c5af8fd5a66dbb31` |
| 0012 | Default-deny bundle is the policy floor | Accepted (genesis) |  | — | `fbbb75a2db48516a` |
| 0013 | Exception mechanism for privileged paths | Draft |  | **N** (CR when written) · post-bootstrap | `59073dea085cb1f0` |
| 0014 | Floor authorship and change control | *Reserved* | | **N** | no file |
| 0015 | Boundary effects audit | Proposed |  | **R·CR** (C2) | `a3d05ccbf175d977` |
| 0016 | Persona | Accepted (genesis) |  | — | `549ff926bf2d16d6` |
| 0017 | Archetype admits only in-house pre-trained Personas | Accepted (genesis) |  | — (supersession: **N**, CR when written) | `95bb1aa1bab4cb9d` |
| 0018 | Typed lift splits | Accepted (genesis) | E1 | E1: **R** | `99c36e193cef8b46` |
| 0019 | Optional decode observability | Accepted (genesis) | E1 | E1: **R** | `82ab9ab05ec69c44` |
| 0020 | Replay scope is boundary events only | Accepted (genesis) |  | — | `5c6e9729126ec7e5` |
| 0021 | Build effect stream | Proposed |  | **R** (after 0022 §1–5) | `4d64f1ed9c2a4dbb` |
| 0022 | Build action alphabet | Proposed |  | §1–5, §7, §8: **R** · BS · §6: **R·CR** (C2) | `7761b7e8c8a0a77b` |
| 0023 | Degeneracy as the deployment-variation relation | Proposed |  | decision: **R·CR** (C3) · carried scope: **N** | `9a2b1ea842fb836e` |
| 0024 | Promotion requires a unanimous quorum | Proposed |  | **R** · BS | `31fa5769ad55779e` |
| 0025 | Trust anchor is a havoc issuer | Proposed |  | **R** · BS (with annex) | `dfdf837de65395c7` |
| 0026 | The rules floor | Proposed |  | R1–R3, R5, R7: **R** · BS · R6, R8: **N** | `1013fa455479928c` |
| 0027 | Genesis rules are resident | Proposed |  | **R** · BS | `d1e13fbfb806eba7` |
| 0028 | Forensic floor | Proposed |  | **R·CR** (C1) · post-bootstrap | `23fdb309a48357d8` |
| 0029 | Genesis; unilateral ratification; bootstrap | Accepted (genesis) |  | — · S4-1 erratum: **R** | `582562c3753010b9` |

**Count.** 29 numbers: 16 Accepted (genesis), 2 of them confirmation-required · 10 Proposed · 1 Draft (0013) ·
1 Tombstone (0011) · 1 Reserved (0014).

**Reversed in effect** (accepted text still in force): 0008 and the 0017 ordering-primacy clause, both by 0023 §5.

**Unnumbered, no decision text:** 0008 supersession (per-principal Observers + correlator) · 0017 ordering-clause
supersession · weakest-link provenance rule · the provenance, legibility, and Observer-scoping declaration records
(blocked by 0023).

## 3. Declaration records

All are sections inside a record. They carry no digest of their own and ratify with their parent.

| Record | Kind | Axis position | Home |
|---|---|---|---|
| A-0025 | Archetype custody, strict unanimity | (n, 0) | 0025 annex |
| D-0025-1 | TUF-style threshold with recovery | (k, n−k) | 0025 annex |
| D-0025-2 | n−1 eviction with replacement | (n−1, 1) | 0025 annex |
| D-0024-1 | k-of-n grant seats (rules-floor degeneracy: relaxes 0026 R1, R2) | approver fault tolerance | 0024 Degeneracies |
| D-0024-2 | Single signer (rules-floor degeneracy: relaxes 0026 R1, R2) | approver fault tolerance | 0024 Degeneracies |

## 4. Other corpus files

| Corpus path | State | Digest |
|---|---|---|
| `checkpoints/topak-theory-of-operation-2026.09.15.md` | Theory of Operation rev 4. Narrative in force; §0, §8–§11 superseded as state of record by G1 | `b1a740bce9534268` |
| `checkpoints/topak-genesis-corpus-manifest-v1-2026.09.15.md` | **Superseded by G1.** Historical; digests stale by design | `ff8b996b5f44cfa2` |
| `checkpoints/topak-theory-of-operation-2026.09.12.md` | Historical | `ae2bb1ee6243ed6f` |
| `checkpoints/topak-theory-of-operation-2026.09.11.md` | Historical | `9443b8f5692105e1` |
| `checkpoints/topak-theory-of-operation-2026.09.10.md` | Historical; recovered from an inline reply (T3-4) | `2e2540837f0257de` |
| `FREEZE-AND-BATCH-A-2026.09.15.md` | Freeze notice; Batch A ratification. Freeze ends at this cut | `52e8d709229fcf01` |
| `RECOVERY-REGISTRY-2026.09.15.md` | Cleanup step 2, closed | `6062cd82e2d94dac` |
| `FOLD-LOG-2026.09.15.md` | Cleanup step 3, closed | `68a2e48165409cb1` |
| `NORMALIZATION-LOG-2026.09.15.md` | Cleanup step 4, closed (G1-1 correction recorded here, not there) | `5e27249e5753af47` |
| `spec/RulesFloorNV.tla` | Non-vacuity spec; encodes 0024 rev 3 (`as0024`) and rev 4 (`rev4`) | `1468d8bab89bb076` |
| `spec/RulesFloorNV-results-2026.09.15.txt` | TLC results | `2130c84486e96765` |
| `spec/RulesFloorNV-run.sh` | Runner | `13cf8291fd56a62c` |
| `derived/topak-boundary-register-2026.09.13.md` | Current | `5cd08136cc979239` |
| `derived/topak-feature-list-2026.09.15.md` | Current until regenerated (step 7) | `514f3ca733bbc886` |
| `derived/topak-external-assessment-2026.09.12.md` | Historical (0006 mechanism misstated) | `6ffcca96e4c8942b` |
| `derived/topak-playbook-delta-inventory-2026.09.12.md` | Historical (tally error T3-2; 0006 mechanism T3-1) | `7c2f27504d7caa1c` |
| `derived/tlaplus-paxos-cheat-sheet-2026.09.13.md` | Reference | `d91dcaaf1137d405` |

**References** (not genesis content; digested so citations are pinned)

| File | What | Digest |
|---|---|---|
| `2605_09045v2.pdf` | Moon & Varshney, arXiv:2605.09045v2 | `221f538c881540c2` |
| `AI_RMF_Playbook.pdf` | NIST AI RMF Playbook | `b8186ddbfaf66c0d` |
| `TOPAK__An_Architecture_Pattern_for_Multi-Agent_Collaboration` | Draft article (Project knowledge) | `996924f199631247` |

**Not in corpus, by registry decision:** the 09.11 glossary (stale; regenerate in step 7), and the pre-corpus SVG
diagrams and PDFs.

---

## 5. Changes made at the cut

- **G1-1. ADR-0022 History tag collision (normalization; applied).** Step 4 logged its title-block row as N2, but
  the fold had already used N2 for the six-variant fix (S3-6). The step 4 row had also been appended inside
  the quoted §1 table that R1 struck, where it rendered as a sixth row of the old table. It is now **N3** in the
  History table, and the prior-title-block heading reads N3. The quoted table is restored. Body and inline markers
  are unchanged; the inline ⟨N2⟩ markers still mean the fold's N2. Every other record was checked: no tag
  collisions, no rows inside quoted tables, and every inline marker resolves to a History row.

**Custodian calls confirmed by the cut** (G-C5): **N-1** (09.11 and 09.12 acceptances are Accepted (genesis)) ·
**N-2** (0005 Held → Proposed) · **N-3** (0021 Blocked on names ADR-0022).

---

## 6. Findings ledger

Every cleanup finding, with its disposition at G1.

| Finding | Subject | Disposition at G1 |
|---|---|---|
| Batch A §2 | 0002 Context §4.2 citation | Folded as **0002 E1, pending** → queue E |
| T2-1 | 0018, 0019 cite ADR-0016 §8 | Folded as **E1, pending** on both → queue E |
| T2-2 | Replay of 0016–0020 edits | Closed; no action |
| T2-3 | 0022 erratum locations | Closed at fold (E1 applied, seven sites) |
| T2-4 | 0017 erratum home | Closed at fold (Context) |
| T2-5 | 0023 heading levels | Closed at step 4 |
| T3-1 | Delta inventory repeats 0006 misstatement | Closed; file marked historical |
| T3-2 | Delta inventory tally and knock-ons | Closed; file marked historical; feature list §9 carries the correction |
| T3-3 | 0028 "opposite direction" | Applied at fold on a Proposed record; ratifies with 0028 |
| T3-4 | 09.10 checkpoint was inline | Closed; recorded in its header |
| S3-1 | 0002 A1 has two sites | Folded; **ratification must review the trailing "(HITL)"** at the Rationale site → queue B |
| S3-2 | 0003 clause annotation not exhaustive | **Open.** Two Decision sentences unnumbered (read-only audit principals; archive as its own ETL). Needs drafted annotation text → queue F |
| S3-3 | 0015 R1 *Was* was short | Closed at fold (record sentence kept). Confirm at 0015 ratification |
| S3-4 | 0023 carried scope reverses clause 7 | **Open.** Next 0023 revision rewrites clause 7 and obligation 2 → queue F |
| S3-5 | 0006, 0009 status marks shortened | Closed at fold |
| S3-6 | 0022 R1 missed three sites | Closed at fold |
| N-1, N-2, N-3 | Custodian calls | **Confirmed by the cut** (§5) |
| S4-1 | 0029 body points to the retired amendments file | **Candidate erratum** → queue E. Target: History S1 in 0006 and 0009 |
| S4-2 | Revision identity | **Settled** by G-C2 |
| S4-3 | Label for 0014 | **Settled** by G-C3 |
| S4-4 | 0013 heading "Decision (skeleton)" | Body text; resolves when 0013 gets decision text |
| G1-1 | 0022 N2 collision | **Applied at the cut** (§5) |
| G1-2 | 0023 obligation 2 says 0013 "still has no owner" | **Open.** 0013 is owned (Scott). Same site as S3-4; the same revision fixes both → queue F |
| G1-3 | Debt ledger undercount | **Corrected in §8.** The feature-list session (09.15) found 0023 confirmation-required under C3 and raised the count from +3 to +4. Manifest v1 and rev 4 §10 never carried it |
| G1-4 | Rev 4 §9 stale items | **Corrected in §9.** Rev 4 §9 still lists the rules-floor non-vacuity check as ratification-blocking (§11 marks it done) and says the delta inventory is not on disk (recovered in tranche 3) |

---

## 7. Ratification queue

All at the custodian's discretion (ADR-0029 §2). Batches are in dependency order. Batch A is done (FREEZE-AND-BATCH-A §2), so the letters continue from B.

**B. Bootstrap core** (ratify together; none may be confirmation-required)
- 0025 with annex (A-0025, D-0025-1, D-0025-2)
- 0026 R1–R3, R5, R7
- 0027
- 0022 §1–5, §7, §8 (§6 stays unratified; note it on the face)
- 0024, with D-0024-1 and D-0024-2
- 0002 A1: two sites; review "(HITL)" (S3-1). Triggered by 0024 and 0025.
- 0010 A1 and A2. Triggered by 0026.

**C. Confirmation required on ratification**
- 0015 (C2 exhaustiveness)
- 0022 §6 (C2 confinement)
- 0028 (C1 privileged paths; ratification phase post-bootstrap)
- 0023 decision text (C3; reverses 0008 and 0017's ordering clause in effect)

**D. Plain**
- 0021, after 0022 §1–5
- 0005, carrying the Observer-gate debt

**E. Errata** (no decision content; Batch A-like)
- 0002 E1 (§4.2 → §4.6 and Appendix B)
- 0018 E1 and 0019 E1 (ADR-0016 §8 → ADR-0020)
- 0029 S4-1 (dangling pointer)

**F. Needs text before it can be queued**
- 0003 annotation extension (S3-2)
- 0023 revision: clause 7, obligation 2, the owner sentence (S3-4, G1-2), and the carried-scope table
- 0013 decision text: NC-1, NC-2, demand type 5
- 0026 R6 (waits on 0013) and R8 (candidate)
- The unnumbered records in §2

---

## 8. Genesis debt ledger (ADR-0029 §7)

| Measure | At G1 |
|---|---|
| Confirmation-required records ratified | **2** (0006, 0009) |
| Confirmation-required on ratification of queue C | **+4** (0015, 0022 §6, 0028, 0023). Corrected from +3 (G1-3) |
| Confirmation-required when written | **+3** (0013, 0008 supersession, 0017 supersession) |
| Total confirmation set if everything above is ratified or written | **9** |
| Records not on disk | **0** (was 20 at manifest v1) |
| Bootstrap specification | **Not drafted.** `RulesFloorNV` is a precursor to `RulesFloor` and `Promotion` |
| Forcing function | **None**, by decision |

---

## 9. Open list

**Genesis-blocking**
- Bootstrap specification: five modules, five invariants, a mutation each (0029 §5).
- Signed message format (protobuf vs canonical CBOR). The genesis bundle needs it.
- Genesis bundle and manifest format (0029 open obligation, gated on the message format).
- Key-holders and grant seats (≥ 5 humans at the archetype), or a declared degenerate bootstrap custody.

**Highest risk**
- **ADR-0013.** Owned (Scott); decision text for NC-1, NC-2, and demand type 5. Post-bootstrap under recusal.
- **Sandbox gap.** Blocks 0022 §6 and 0015 exhaustiveness; decides whether `Contained` has members. No mechanism,
  no owner.

**Decisions without text**
- Observer: quarantine gate as modeled event or internal step (unblocks 0005); 0008 scoping supersession;
  veto-seat liveness heartbeat (0024).
- Floor fitness, the fourth gate (MEASURE 2.13), and a TLA+ invariant non-vacuity gate of the same shape.
- Global vs per-class floor, for both floors (0022 is evidence for per-class).
- 0017 independent-lineage criterion.
- Raw-emission retention, between 0003 and 0006.
- Replay authorization vs replay scope (clause 0003.5 overlaps 0020).
- Subtractive promotion fast path (0024, deferred).
- 0014 floor authorship, narrowed to proposal eligibility.

**Declarations unwritten**
- Clock model · assumptions of use · liveness assumptions about humans (weak fairness on `Vote`; anchor custody) ·
  monoculture (cross-family Observer) · `L` as a rung-tuple obligation and the MEASURE 1.1 non-measurement
  declaration · MANAGE 1.4 residual risk, headed by anchor capture · `D` as human-response budget · owner column
  and per-boundary adversary for the boundary register.

**Work items**
- Theory of Operation, narrative only, cut from G1 (step 6).
- Regenerate glossary, feature list, and NIST inventory against it (step 7).
- Diagrams (Build and Run) · component × domain table · vector clock or per-principal sequence (contingent on the
  Observer gate) · genesis and key ceremony; re-genesis migration.
- From the 09.10 session: per-component cost table (MAP 3.2), hierarchy-of-needs drop order (MANAGE 2.1),
  control-plane cost model.

**Closed since rev 4:** rules-floor non-vacuity check (0026 §6; all entries non-vacuous against 0024 rev 4) ·
record recovery · fold · normalization.

---

## 10. Known unrecorded decisions

These were stated as decisions in session but never recorded. Under ADR-0029 they are **not genesis content.**
Their absence from §2 does not mean they were rejected. Source: recovery registry §3.

| Content | Session | Likely home |
|---|---|---|
| Sealing certificate, Merkle root over round envelopes, HMAC-base32 topic names | 8b4223ef | 0003 clauses or a companion record |
| "Army of one" degraded mode | a7fad171 | GOVERN 6.2 record |
| DAG reversibility: compensable prefix, pivot, retriable suffix; lease TTL < compensator window | 8cdaf02d | New record |
| Deadman e-stop; halt ≠ purge; e-stop clearance voids leases; `W < L < D` | d6490a01 | New records |
| Paxos over Kafka, not KRaft; three consensus groups | 0c95e28a | New records |
| Signed message format analysis (protobuf/CBOR; sign received bytes) | 711cd4f7 | Genesis-blocking open decision (§9) |
| Policy within an epoch, boundary between epochs; Rust and OPA sidecars; repo layout | cadc11aa | New records |
| Bundle deployment modes (forcing / eventual / decomposed) | 7d8a1f1b | New record; may predate the floor model |

---

## 11. Next

1. **Step 6.** Write the next Theory of Operation from G1, narrative only. It references G1 for status, ledger, and
   plan.
2. **Step 7.** Regenerate the glossary, feature list, and NIST inventory against it.
3. **Ratify from §7** whenever you choose. Each ratified batch cuts a genesis checkpoint (G2, …).

---

## Appendix A. Full digests

G1's own digest cannot appear inside G1. It is in `SHA256SUMS-G1`, and G2 records it.

```text
3ce1bcf7e397b3246d9756aa1e87762bdb11cd4ada306f7a913973098e4325a2  decisions/ADR-0001.md
6ff6b77b7cb970ca867061560fd96ff7abc1a41b2960a57bde3db92af062a1db  decisions/ADR-0002.md
a72a3716dc3e3dd1f79c7c9b4084b6b18ba46e51af37c62b3151c25e4977b7ea  decisions/ADR-0003.md
25dc46f47d302d33172f2b766dde1e3c0eda2b6b803ac708d03fd59186ab3136  decisions/ADR-0004.md
b2fb45dcf09f746310f14eb6b8a59d3947c93fcb2cf90e2618790ee969d6dc1a  decisions/ADR-0005.md
c02c7e34927af5d45a92a133b39045cd13a766d083645862e032254778e21a84  decisions/ADR-0006.md
e00717a28bfe001e660746bc381216575bd024e6ee191e1895c08f4a4535f8b9  decisions/ADR-0007.md
0a7dd249d3af7edf675b48463a9c6ee8f93867373f0c9ceb5a5b8eb8706147ec  decisions/ADR-0008.md
11056665d09940f27437313e6db80bfc5511509e0bbf7e6751ca3e800b6f0e41  decisions/ADR-0009.md
64a59970c4356dbe22428f5f05e38716c9888231ca0c5e50c4dedc13e8c53ba9  decisions/ADR-0010.md
c5af8fd5a66dbb318053d3c94e6686dd981c572ea8d9367ea1a939f19e99b186  decisions/ADR-0011.md
fbbb75a2db48516a732dd53860dd78b77272253aba1cd358ab3d7728a4cc21c1  decisions/ADR-0012.md
59073dea085cb1f0b48c109ce1a3077e3f0550447250a46a5615f9ecbc4f5931  decisions/ADR-0013.md
a3d05ccbf175d977ebb346cdde470860ca4fdc16ea2d81e1b2beffd0739c5869  decisions/ADR-0015.md
549ff926bf2d16d61bda8a956ea05e9813a7d79580acf33ad5493da138a035d8  decisions/ADR-0016.md
95bb1aa1bab4cb9dfcca18e51cdcda6acbc08b617fb1a6357f923cca25a53bf0  decisions/ADR-0017.md
99c36e193cef8b46510736882545c3bb554a77eb26705c4d1e598931d615a804  decisions/ADR-0018.md
82ab9ab05ec69c44d4b32d0566e17befd2ce4f6159cd30fadb251108a4cd7354  decisions/ADR-0019.md
5c6e9729126ec7e54673c17e6cd439624a0a07e978841479ccce55494e147c03  decisions/ADR-0020.md
4d64f1ed9c2a4dbbcfecf789effe13ac359a1c8ddd1ea6e6acff89aaeb967383  decisions/ADR-0021.md
7761b7e8c8a0a77b8f7e8b81904b8284189750999e056316c0ec99071e7b510f  decisions/ADR-0022.md
9a2b1ea842fb836e4ee79e61a7d59b9332415e76168ccecd51a26abdc7b7ba6f  decisions/ADR-0023.md
31fa5769ad55779e6b3a2a6a7acc567ee241333af6cf8f4fd4ec1973fb90d245  decisions/ADR-0024.md
dfdf837de65395c78e6d7d743e0ca1422e586a9651703e1ef496f51352a377ee  decisions/ADR-0025.md
1013fa455479928c18d0695971dc9aa9045df3c12de805d59d3f6cbf5f34b8ff  decisions/ADR-0026.md
d1e13fbfb806eba7e2be64d711650e0fac01cf7a9c3e5e6860292ba0cb677fba  decisions/ADR-0027.md
23fdb309a48357d81360ecb0c19457cbea8f4ee16408844c953f070d0f4dffb9  decisions/ADR-0028.md
582562c3753010b9435382226cf19d7339f973709d801e21e341190922a637d1  decisions/ADR-0029.md
b1a740bce95342684933c2253937e1ac0cb446cd3e9b523c92b0e5d8bca746f7  checkpoints/topak-theory-of-operation-2026.09.15.md
ff8b996b5f44cfa2495d4cd9e124290290a67104d9742595fc191ef1f11d9f44  checkpoints/topak-genesis-corpus-manifest-v1-2026.09.15.md
ae2bb1ee6243ed6f325a1f2043442f36b7306eafe9fb82facb979cab85ef933e  checkpoints/topak-theory-of-operation-2026.09.12.md
9443b8f5692105e196a82e1609555d82c927fe9a58c5ee2f65eecf3d508cb6e6  checkpoints/topak-theory-of-operation-2026.09.11.md
2e2540837f0257de59130242fc4fc782fece11c24ad6cd3d3efa72d7fb2d90fd  checkpoints/topak-theory-of-operation-2026.09.10.md
52e8d709229fcf01d751557a673f905dcc19ad19039431a701f7fa3fd1555739  FREEZE-AND-BATCH-A-2026.09.15.md
6062cd82e2d94dacc72b2aa747e0bdd3328297a8860ab67061ac98120351d7e5  RECOVERY-REGISTRY-2026.09.15.md
68a2e48165409cb1833b31bb4111f2e666da8e45c25142420938a7d32525ac5d  FOLD-LOG-2026.09.15.md
5e27249e5753af47316723aa061980d4da1582695a28799bcbe158205507b48c  NORMALIZATION-LOG-2026.09.15.md
1468d8bab89bb076ab79db69f633f8a03b3c2283b3241f07184cf39081631e65  spec/RulesFloorNV.tla
2130c84486e967654340a54abc5a26304b9e35b6eff41b5b45fe8a26bb0b7e97  spec/RulesFloorNV-results-2026.09.15.txt
13cf8291fd56a62c5f3eb603de2ce737a8504661fcfec4a0caec68dab1424a0d  spec/RulesFloorNV-run.sh
5cd08136cc9792392f518751df9ecad0f6cf534af467389d7af330e778e67ce4  derived/topak-boundary-register-2026.09.13.md
514f3ca733bbc8865e07a206d50c1a7372155b32e37952dff36899af389b642a  derived/topak-feature-list-2026.09.15.md
6ffcca96e4c8942b7a9ff9dee5a683feeb3f740969ee7cb3ebfeeddbce62b71c  derived/topak-external-assessment-2026.09.12.md
7c2f27504d7caa1cc4f0f4da408008a741e40d2052942f9fb08ee372ee84d2fd  derived/topak-playbook-delta-inventory-2026.09.12.md
d91dcaaf1137d40552fe1029c61d3f654b32facc86cf256acd98465945b71fbc  derived/tlaplus-paxos-cheat-sheet-2026.09.13.md
221f538c881540c20e335125d9d219b14ce7710506b55a38f111fce2ef925675  references/2605_09045v2.pdf
b8186ddbfaf66c0d5b01c0eb91b9ff92d1e1c1d82cb8584b0e96b0b5884f12f2  references/AI_RMF_Playbook.pdf
996924f199631247825008ce9dd15b8a7ff13f23165063d353d80a3133544714  references/TOPAK__An_Architecture_Pattern_for_Multi-Agent_Collaboration
```
