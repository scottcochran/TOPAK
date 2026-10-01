# TOPAK — Normalization log

**2026.09.15** · cleanup step 4 · under the freeze (FREEZE-AND-BATCH-A §1) · genesis custodian: Scott · **step 4 closed**

Every ADR record now uses one status vocabulary and one header schema. No decision text changed.
A check confirmed that each record's body (everything outside the title block, the provenance note, and
History) is byte-identical to the step 3 file. 0023 differs only in heading levels (T2-5). The
boundary register is not an ADR and is untouched.

## 1. Status vocabulary

The status line takes exactly one class from ADR-0029 §3, plus Tombstone.

| Class | Meaning | Records |
|---|---|---|
| **Accepted (genesis)** | Ratified by the custodian | 0001–0004, 0007, 0008, 0010, 0012, 0016–0020, 0029 |
| **Accepted (genesis) · confirmation required (ADR-0029 C…)** | As above, plus confirmation promotion after bootstrap | 0006, 0009 |
| **Proposed** | Unratified; decision text exists | 0005, 0015, 0021–0028 |
| **Draft** | Unratified; no decision text, so not ratifiable (ADR-0029 §2) | 0013 |
| **Tombstone** | Number used; no decision content | 0011 |

**Retired:** *Held* (0005 → Proposed), *Draft skeleton* (0013 → Draft), bare *Accepted* (→ Accepted
(genesis)). ADR-0029 §3 reads "Proposed / Draft" as a single row. This log splits it on decision
text, which keeps the manifest's R/N readiness distinction visible on the record itself.

## 2. Header schema

```text
<!-- RECOVERED · tranche N · FOLDED · NORMALIZED · 2026-09-15 -->   or   <!-- ON DISK [· FOLDED] · NORMALIZED · 2026-09-15 -->
> **Recovery note.** …   or   > **Provenance note.** …
>
> Cleanup step 4 (2026.09.15) normalized the title block …

# ADR-NNNN — Title

**Status:** <class> · <YYYY.MM.DD> [· confirmation required (ADR-0029 C…)]
**<field>:** …            (optional fields, in the order below; absent means none)

---
```

**Status line rules.** It holds the class, the date the record entered that class, and the confirmation
marker only. Revision numbers, revision descriptions, blog tags, and prose do not belong on it. Prose
moves verbatim to **Status note**. Revision events live in History.

**Field order.** Status · Status note · Pending · Ratification phase · Deployment position · Scope ·
Owner · Supersedes · Split from · Amends · Amends in effect · Revises · Narrows · Depends on · Depended on
by · Companions · Precedent · Relates to · Resolves · Resolves debts of · Closes · Unblocks · Blocked on ·
Blocks · Creates a debt against · Carries scope into · Note

**Field rules.**
- **Pending** appears only on accepted records with unratified folded changes. It is derived from
  History: 0002 (A1, E1), 0010 (A1, A2), 0018 (E1), 0019 (E1).
- Relationship fields name records, not their status. Status annotations such as "(accepted)",
  "(held)", and "(open)" are stripped because they go stale. Inline fold markers (⟨E1⟩, ⟨E1 · pending⟩,
  ⟨S1⟩) are kept at their sites.
- Empty fields ("Supersedes: nothing") are dropped.
- Field values carry no bold, except where the body's own wording is quoted.

**Provenance.** Records that were on disk before recovery (0013, 0024–0029) now carry a provenance
note citing their manifest v1 digest. Those digests matched for 0013, 0024–0027, and 0029. 0028's digest
predates its step 3 erratum.

**History.** Every record gets an N row. Records that had no History section get one. The prior title
block is quoted verbatim, so every removed revision annotation is still recoverable. 0022's title was
already normalized at fold (N1), so its step 4 row is N2.

## 3. Registry and fold items disposed

| Item | Disposition |
|---|---|
| T2-5 (0023 heading levels) | Title H2 → H1; drafted sections H3 → H2; History stays H2. The step 3 "Not normalized" note is struck. |
| 0021 title draft number | `~~ADR-0016~~ ADR-0021 ⟨N1⟩`, the same form as 0022 N1. The stale recovery-note sentence is struck. |
| 0022, 0023 stale recovery-note sentences | Struck and replaced |
| Revision numbers in status lines | Removed from 0015, 0022, 0024–0027, 0029; quoted in History |
| "See the amendments file" (0024, 0026 headers) | Replaced with the History location in 0002 and 0010 |

## 4. Calls for the custodian (applied, reversible from History quotes)

- **N-1. Bare *Accepted* → *Accepted (genesis)* for every acceptance from 09.11 and 09.12.** Basis:
  ADR-0029 §1 declares the current design process genesis, and §4 marks 0006 and 0009
  retroactively, which presumes they are genesis-ratified. §6's "not re-reviewed" guarantee only
  covers them under this reading. The alternative is a separate pre-genesis class, which the
  vocabulary would then need to add.
- **N-2. 0005 *Held* → *Proposed*.** The 09.12 review did not ratify it, and manifest v1 rates it **R**.
  The hold reason is kept in Status note.
- **N-3. 0021 *Blocked on* now names ADR-0022.** This adds no new relation: 0022's header already
  records the inverse edge ("Unblocks: ADR-0021"). The "(unwritten)" annotation is dropped.

## 5. Findings (not applied; for G1)

- **S4-1. Dangling pointer in 0029's body.** Open obligations ends "see the amendments file," which is
  now retired. The target is History S1 in 0006 and 0009. This is a body edit on an accepted record,
  so it is a candidate erratum.
- **S4-2. Revision identity now lives only in History and bodies.** 0026 cites "ADR-0024 revision 3"
  and "revision 4"; 0025 and 0029 narrate their own revisions. Revision 4 resolves through 0024's
  quoted prior header. **Revision 3's text is not in the corpus.** G1 should decide whether a revision
  is identified by digest, and record 0026's non-vacuity baseline accordingly.
- **S4-3. 0014 has no record, so it has no status.** The 09.15 checkpoint's "Open" is not a class. The
  G1 log needs a non-status label for reserved, unwritten numbers.
- **S4-4. 0013's body heading still reads "Decision (skeleton)."** It is body text and left as is.

## 6. Project changes

- **Replace** ADR-0001–0013 and ADR-0015–0029 (28 files) with the files in this zip.
- **Delete** `topak-adr-amendments-accepted-2026_09_15.md` and `topak-adr-pending-revisions-2026_09_15.md`
  if they are still present. They are still in the Project; fold log §5 retired them.
- **Keep** the registry, freeze notice, fold log, manifest v1, checkpoint rev 4, and boundary register as
  they are. Manifest v1's digests are now stale for every record. G1 replaces the manifest.

## 7. Next

**Cleanup step 5: cut G1.** Inputs: the normalized records, the ratification queue from fold log §6,
calls N-1–N-3, and findings S3-1–S3-6 and S4-1–S4-4. Section 3 of the registry (unrecorded decisions)
also feeds in.
