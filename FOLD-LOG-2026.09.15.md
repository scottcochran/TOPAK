# TOPAK — Fold log

**2026.09.15** · cleanup step 3 · under the freeze (FREEZE-AND-BATCH-A §1) · genesis custodian: Scott · **step 3 closed**

Every drafted amendment, erratum, revision, and annotation now lives in its record. The two change
files are retired.

## 1. Convention

| Case | Treatment |
|---|---|
| **Accepted record, ratified change** | Applied. Struck text inline (`~~…~~`), replacement follows, tagged ⟨A1⟩, ⟨E1⟩, and so on. |
| **Accepted record, unratified change** | **Pending.** Marked inline ⟨A1 · pending⟩ at each site, not applied. Full replacement text is in History. Accepted text stays in force until ratified. |
| **Proposed record** | Revised in place and tagged, whether or not the change was ratified; nothing in it is ratified yet. |
| **Tables** | A replaced table is shown new inline; the struck table is quoted in History. |

Every changed record ends in a **History** section: tag, kind, change, source, state. Recovery
headers now read `FOLDED`, and no record points to `../pending/`.

**Order.** Errata before revisions (0022). Where a revision's *Was* quoted less than the record
holds, the fold keeps the record's remaining text rather than dropping it (0015, 0022).

## 2. Records

| # | Folded | State after fold |
|---|---|---|
| 0002 | A2 applied (section added) · A1 marked at **two** sites · E1 (§4.2) marked | A1, E1 pending |
| 0003 | Clause annotation: status line, inline clause numbers, table | Complete · S3-2 |
| 0006 | Status mark corrected to ratified form (C1, C4 via 0013) | Complete · S3-5 |
| 0007 | History only: erratum withdrawn as a no-op | Complete |
| 0009 | As 0006 | Complete · S3-5 |
| 0010 | Erratum applied at two sites · A1, A2 marked | A1, A2 pending (trigger 0026) |
| 0015 | Revision R1 applied | Proposed · S3-3 |
| 0017 | SLSA / in-toto erratum applied, in Context (T2-4) | Complete |
| 0018 | T2-1 erratum marked (one site) | Pending |
| 0019 | T2-1 erratum marked (three sites) | Pending |
| 0022 | Errata E1 (seven sites, T2-3) and E2 applied, then R1 · title and "five-variant" normalized | Proposed · S3-6 |
| 0023 | Carried scope added as a section | Proposed · S3-4 |
| 0028 | T3-3 erratum applied (states the rule) | Proposed |
| 0001, 0004, 0005, 0008, 0011, 0012, 0016, 0020, 0021 | Header only; nothing was drafted against them | — |
| Boundary register 09.13 | Header only | — |
| 0013, 0024–0027, 0029 | Untouched; nothing drafted against them outside their own text | — |

## 3. Registry findings, disposed

| Finding | Disposition |
|---|---|
| T2-1 | Folded as a **pending** erratum on 0018 and 0019 |
| T2-3 | Location column corrected; all seven sites confirmed to mean ADR-0021; applied |
| T2-4 | Home settled as 0017 Context; applied |
| T2-5 | Not normalized. Step 4 |
| T3-3 | Applied to 0028 as a rule statement |
| Batch A §2, new 0002 erratum | Folded as **pending** |
| Batch A §3, 0002 A1 | Superseded by S3-1 below |

## 4. Findings at fold (not ratified; for G1)

- **S3-1. 0002 A1's struck phrase is in the record after all.** Batch A §3 said it was not. It is,
  verbatim, in *Rationale at review*. The Decision sentence carries a second phrasing ("with Build's
  commit point a human signing key"). A1 now has two sites. The trailing "(HITL)" at the Rationale
  site sits outside the struck phrase and needs a look at ratification.
- **S3-2. 0003's clause annotation is not exhaustive.** Two Decision sentences have no number:
  read-only audit principals, and archive as its own ETL. Batch A checked that the listed clauses
  exist, not that the list covers the record.
- **S3-3. 0015 R1's *Was* was short.** It quoted two of the Decision's three sentences, and its *Now*
  restated the third without *signed* and without *rather than reconstructed from transport
  metadata*. The fold keeps the record's sentence and adds only R1's new traceability sentence.
- **S3-4. One of 0023's "no decision change" items changes a decision.** "Degeneracy composition
  returned from ADR-0013 … owned here" reverses clause 7 and the second undischarged obligation, both
  of which assign composition to 0013. No replacement text exists, so clause 7 is marked, not edited.
  0023's next revision must rewrite both.
- **S3-5. Recovery shortened the 0006 and 0009 status marks.** They read "(ADR-0029 C1)"; the
  ratified form is "(ADR-0029 C1, C4 via 0013)". Corrected.
- **S3-6. 0022 R1 missed three spots.** Its *Was* stopped before the signature-over-provenance
  clause (kept, now citing 0021), and it changed the table without updating "five-variant" at the
  Decision lead-in or "Five variants, not four" in §1 (normalized to six).

## 5. Project changes

- **Replace** ADR-0001–0012, 0015–0023, 0028, and the boundary register with the files in this zip.
- **Delete** `topak-adr-amendments-accepted-2026_09_15.md` and `topak-adr-pending-revisions-2026_09_15.md`.
  Their content is in the records.
- **Keep** the manifest v1, freeze notice, registry, and checkpoint rev 4 as they are. The manifest's
  digests and "pending-revisions file" pointers are now stale by design; G1 replaces it.

## 6. Ratification queue created by the fold

Pending on accepted records: **0002 A1** (redrafted sites, S3-1), **0002 E1**, **0010 A1/A2** (trigger
0026), **0018/0019 E1** (T2-1). Proposed records carry their revisions and take them on ratification.

## 7. Next

**Cleanup step 4: normalize.** One status vocabulary (retire *Held* and *Draft skeleton*), one header
schema, no revision numbers in status lines, 0023 heading levels (T2-5), and draft-number residue in
0021's title. Then step 5, cut G1.
