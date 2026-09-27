I'll survey the TOPAK repo for everything it says about rungs, axes, and degeneracies, then compare those sources against each other.

Next I'll dig into the specifics: ADR-0024's degeneracy table, ADR-0030 §8, ADR-0026's R9 finding, ADR-0029's A2 marker, why ADR-0015 and ADR-0029 fail the G3 manifest, and the mechanism's rung code.

**Summary.** Rungs, axes, and degeneracies are one framework, ratified in ADR-0023 and confirmation-required under C3. The framework is stable. Its instances are not: the axis list is unenumerated, three different rung orderings are live, no declared entry follows the ratified schema in full, and two Proposed records now contradict Accepted text on what a rung buys. Plus the corpus has drifted since the G3 cut in ways no checkpoint records. Details follow.

## Where each concept stands

**Rungs.** The word carries four orderings, and only the glossary says so.

| Ordering | Source | Status | Direction |
|---|---|---|---|
| Position on one axis; a deployment is a tuple; unqualified "rung demotion" barred | ADR-0023 §5 | Accepted (genesis), C3 | Abstract, per axis |
| Provenance: Archetype, 1 fine-tune, 2 attested external, 3 asserted external | ADR-0017 | Accepted; ordering-primacy clause reversed in effect by ADR-0023, supersession unwritten (G3 item 6) | Numbers ascend with **weakness**; archetype unnumbered |
| Confinement attestation 0 none, 1 launcher, 2 measured boot, 3 confidential VM | ADR-0031 §3 (field), ADR-0034 §2 (semantics) | Field Accepted, C1; semantics Proposed | Numbers ascend with **strength**; archetype is 3 |
| Custody "rungs" A-0025, D-0025-1, D-0025-2 | ADR-0025 annex | Accepted, bootstrap set | Ordered by capture threshold |

The confinement ordering is the one with machinery behind it. `Lease.tla` checks that rung 0 is never `Contained` and that renewal never raises the rung. `Confinement.tla` checks all four ADR-0034 properties at declared rungs 1, 2 and 3, and the `M_HOST` mutation breaks rungs 1 and 2 while leaving rung 3 intact. The reference issues only rung-0 leases, so every principal it serves is `Mediated`, and gap G1 says only a sandbox can change that.

**Axes.** ToO rev 7 §8.2 and the 09.26 glossary name eight: Persona provenance, event-log legibility, Observer scoping, effect-stream role, HITL/HOTL/HOOTL posture, approver fault tolerance, anchor recoverability, floor verification. Only the last three have declared entries. The records name more degeneracy parameters than that list admits.

| Parameter named as a degeneracy | Where | On the axis list? |
|---|---|---|
| Confinement rung, profile clauses | ADR-0034 §8, Proposed | No |
| Lineage strength, projected vs declared | ADR-0035 §9, Proposed | No |
| Forensic horizon, audit authority | ADR-0028 §3 | Folded into legibility |
| Tiered storage, clause 0003.7 | ADR-0003 | "Candidate" only |
| Clock drift bound | ADR-0032 §6 | No |
| Break-glass TTL `T_BG` | ADR-0026 A1 finding 2, pending | No |
| Floor residency | ADR-0030 composition note | No |

ADR-0023 asked for the enumeration as a table. It has not been produced. Chain finiteness is unproven, and the archetype-evolution record that would bound how the archetype grows is unwritten (G3 item 7).

**Degeneracies.** ADR-0023 defines the relation, two kinds, the admission test with the §4a type-change condition, and the §6 schema. Composition is owned there via the composition note, which the gate can check for presence but not correctness. Genesis is declared not a degeneracy. Declared entries so far:

| Entry | Axis | Kind | Status |
|---|---|---|---|
| D-0024-1 k-of-n, D-0024-2 single signer | Approver fault tolerance | Mechanism | Ratified with ADR-0024; D-0024-1 reachable since threshold `quorum` and R9 |
| A-0025, D-0025-1, D-0025-2 | Anchor recoverability | Declaration | Ratified with ADR-0025 |
| A-0030, D-0030-1 Rego floor | Floor verification | Mechanism | Ratified with ADR-0030, C1 |
| D-0034-1 through D-0034-4 | Confinement | Declaration | Proposed |
| D-0035-1 declared lineage | Lineage strength | Not stated | Proposed |

R9 is the one rules-floor entry that bounds a degeneracy rather than the archetype. Its independence is conditional on R1 being relaxed, which `RulesFloorNV_rev5` shows and ADR-0026 finding 1 records. That is consistent across records and is not a discrepancy.

## Discrepancies

1. **The glossary overwrite broke the G3 manifest.** Commit `efcb410` replaced the contents of `derived/topak-glossary-2026.09.17.md` with the 09.26 regeneration, so the filename says 09.17 and the header says 09.26. The 09.17 text survives only in git history. An identical copy sits at `derived/derived/topak-glossary-2026.09.26.md`, a doubled directory. `SHA256SUMS-G3` now fails three entries: the glossary, ADR-0015 after E2, and ADR-0029 after A2. Only the glossary failure is unrecorded anywhere. G3 §9's claim that derived artifacts are unchanged since G2 is false, and the README's vocabulary link points at the misnamed file.

2. **Two Accepted readings of what provenance `Contained` needs.** ADR-0031 §3 says an attested external model is `Mediated` because of prompt egress, which is the in-house reading. ADR-0031's open obligations, ToO rev 7 §2.3, G3 item 20, and the reference all say `Contained` needs the *independence criterion*, and `lease.rs` hard-codes that with a false constant. ADR-0034 §4 sides with the first reading, says independence is not a conjunct, and flags the ToO as stale in its finding 1. ADR-0017's own table already marks rung 1 as `Contained` with a lineage debt. The Accepted texts disagree with each other, and the code encodes the stricter one.

3. **Renewal may lower the rung, or no lease may sit below the declared rung.** ADR-0031 §4, `Lease.tla`, and `check_renewal` in the reference all allow a renewal to lower the confinement rung. ADR-0034 §3.4 refuses any grant below the declared rung, and its `NoSilentDowngrade` invariant requires every live lease to be at exactly that rung. `Confinement.tla` does not model renewal, so the conflict was never checked. Ratifying ADR-0034 as written needs an amendment to ADR-0031 §4 or a stated reconciliation.

4. **Rung numbering runs in opposite directions on two axes.** Provenance rung 1 is the strongest declared degeneracy. Confinement rung 1 is the weakest attested one. ADR-0034 §2 says the archetype is "not rung 1 as on ADR-0017's axis", but on ADR-0017's axis the archetype is unnumbered and rung 1 is a fine-tune, so the sentence misdescribes the record it cites. The SLM README uses both meanings in one file. The 09.17 glossary said "rename one". The 09.26 glossary downgraded that to "always qualify".

5. **No declared entry follows the ratified §6 schema.** ADR-0024 uses Rule / Premise / Sacrificed / Gained with no kind or type-change field. ADR-0025's annex has no kind and no theorems-voided field. ADR-0034 §8 states kind only in prose and omits mitigation. ADR-0035 never states a kind. ADR-0030 comes closest by appending the §6 fields under ADR-0024's table. The schema was ratified on 09.23, and the two records written after it still do not use it as a table.

6. **"Declaration" means two things.** ADR-0024 B2 and ADR-0030 B6 say their D-entries "ratify as declarations". G3 §8 and ToO §12 item 5 say no degeneracy declaration has been written. Both are true only if record-level entries and deployment-level declarations are different objects, and no record says so.

7. **The custody row the corpus occupies has no record.** ADR-0025's annex lists single custodian (1, 0) with a dash. ADR-0029 names it genesis custody and not a degeneracy. ADR-0025's obligation for "a custody row for the ADR corpus itself" is still open, and the 09.16 review's request for a (1, 0) deployment declaration was never actioned.

8. **Model constants lag the records.** `Lease.tla` declares rungs 0 to 2 while ADR-0031 and the reference define 0 to 3, so rung 3 is never exercised by the lease check. `Confinement.tla` checks declared rungs 1 to 3 and never the rung-0 deployment that D-0034-4 declares.

9. **Stale derived vocabulary.** The boundary register's B11, the feature list's F2.6, the playbook inventory, and the external assessment all still say the axis question is open and use "rung manifest", a term no record uses. Neither glossary retires it. G3 item 12 acknowledges the derived set is stale, but the glossary was regenerated selectively, in place, and unmanifested.

10. **ADR-0034 leans on §4a for something §4a does not say.** Its §8 says rungs 1 and 2 void no theorem and "move what the theorems rest on, which is ADR-0023 §4a's case". §4a is about participants changing type between gate and principal. A hypervisor entering the trusted base is a §6b field entry, not a type change. The stretch is small but it is the record's stated basis for calling those rungs admissible.

## What is open on these three subjects

- Enumerating the axes as a table, chain finiteness, and the archetype-evolution record (ADR-0023 obligations, G3 item 7).
- The ADR-0008 and ADR-0017 supersessions (G3 item 6), and ADR-0017's own questions: whether rung 1 is one rung or two, which ADR-0035 finding 2 makes harder, and who may declare a rung.
- Confinement rungs 1 to 3 and *Contested*, held by ADR-0034 while Proposed (G3 item 19). The Run profile is blocked on Run's alphabet.
- The independence criterion, held by ADR-0035 while Proposed (G3 item 20), with its θ values still placeholders.
- A G4 cut that records the post-G3 drift: ADR-0015 E2, ADR-0029 A2 with its C3 marker, and the glossary replacement.
