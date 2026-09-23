# TOPAK — Freeze notice and Batch A ratification

**2026.09.15** · genesis custodian: Scott · under ADR-0029 (Accepted (genesis))

## 1. Freeze

Effective now. No new ADRs, no revisions to existing records, and no new checkpoint revisions until
Genesis Checkpoint G1 is cut.

**Permitted during the freeze**
- Recovery of records from session history.
- Folding already-drafted amendments, errata, and revisions into their records.
- Normalization of headers and status vocabulary.
- Cutting G1.

**The 09.15 Theory of Operation revision 4 is the last revision in that series before G1.**

## 2. Batch A: ratified (genesis), none confirmation-required

Batch A carries no decision content, so none of ADR-0029's C1–C4 apply. Ratification is recorded
here and is applied to the records when they are folded (cleanup step 3).

| Item | Result | Recovery finding |
|---|---|---|
| **0002 Amendment 2** — restated evictability test | **Ratified; form corrected** | The recovered 0002 text does **not** contain the unqualified test. That wording lived in checkpoint prose. The amendment therefore **adds** the restated test to 0002 rather than striking and replacing a sentence. The substance is unchanged. |
| **0003 clause annotation** (0003.1–0003.7) | **Ratified** | Clause list confirmed against the recovered text. Every clause is present. |
| **0007 erratum** (§4.2 → §4.6 / Appendix B) | **Withdrawn as a no-op** | The recovered 0007 text cites no section of Moon & Varshney. There is nothing to correct. |
| **0010 erratum** (§4.2 → §4.6 / Appendix B) | **Ratified** | Target confirmed in the fifth Consequences bullet and in tangential 2. |
| **0017 erratum** (SLSA / in-toto citation) | **Ratified, unapplied** | 0017 is not yet recovered (tranche 2). Apply at fold. |
| **0022 errata** (0016 → 0021; "0005's split") | **Ratified, unapplied** | 0022 is not yet recovered (tranche 2). Apply at fold. |

**New erratum found during recovery, not ratified.** It is recorded for G1. **0002's context** cites
"Moon & Varshney §4.2" for the silent-abstention / vacuous-predicate result. The correct citation is
§4.6 and Appendix B.

## 3. Finding that affects Batch B (not ratified)

**0002 Amendment 1 strikes text that is not in the record.** The struck phrase "the *promotion* gate
above them is a human signing key" comes from 09.12 checkpoint prose and the review discussion. The
accepted text reads "with Build's commit point a human signing key." Redraft A1 against that phrase
before Batch B.

**0010 Amendment 1's struck text is confirmed.** It matches the recovered Decision verbatim.
