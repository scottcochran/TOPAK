# Record forms

Every line a batch writes, in the form Batches 34 and 36 to 39 used. Angle brackets are placeholders. Read the
nearest real precedent with `git show <commit> -- decisions/<record>.md` when a case is not covered:

| Batch | Commit | Shape |
|---|---|---|
| 34 | `075b2e7` | Provisional records and many dependent amendments |
| 36 | `15ae7f1` | One whole record, dependent entries in seven others |
| 37 | `848aed5` | Amendments and errata across three records, a custodian's reading, premise routes |
| 38 | `d4eeb0d` | One erratum, alone |
| 39 | `7719a2c` | An amendment and its dependent, an external fact checked |

## A whole record, Proposed to Accepted

**Header comment.** Drop ` · DRAFT for the custodian` from the `<!-- AUTHORED ... -->` line.

**Provenance note.** Replace "the custodian has settled nothing" with what was settled:

```text
**The custodian settled, at ratification (Batch 36):** the drafter's choices as written; the derived premises of R7,
`refines(Seats)` included; C4 for that route only; and, by reading one transcription against its source, that it is
faithful.
```

**Status line.** The date is the ratification date. Omit the confirmation clause when none attaches.

```text
**Status:** Accepted (genesis) · 2026.10.06 · confirmation required (ADR-0029 C4, for `refines(Seats)` only) ⟨B36⟩
**Status:** Accepted (genesis) · provisional · 2026.10.05 · confirmation required (ADR-0029 C1, C3, C4; provisional under A4) ⟨B34⟩
```

**Status note.** Say where it was ratified, then each criterion that attaches and why, then why each other does not:

```text
**Status note:** Ratified 2026.10.06 (Batch 36) at R8; Proposed 2026.10.05, revised eight times on 2026.10.06.
Confirmation required under **C4** for one thing: ... Nothing else attaches: no privileged path gains an obligation
(C1); no claim is made that some set is exhaustive ... (C2); no accepted clause is reversed (C3) ...
```

**Pending line.** `**Pending:** none.`

**Ratification condition.** Each line says how it was met. A provisional record says what it lacked.

**History.** A Bnn row whose state is **Accepted (genesis)**:

```text
| B36 | Ratification | **Ratified 2026.10.06** by the genesis custodian (ADR-0029 §2), in Batch 36, alone, at R8, with its drafter's choices as written; **confirmation required under C4 for `refines(Seats)` only**. The §7 condition is met. (a) On the custodian's machine, <what ran and what it reported> ... **Not reviewed by a reader other than the drafter** (ADR-0029 A2.5). | <custodian's decisions> | **Accepted (genesis)** |
```

**Index.** The row in `decisions/README.md` becomes:

```text
| [ADR-0053](ADR-0053.md) | <title> | Accepted (genesis) · Batch 36, 2026.10.06 (drafted 2026.10.05, after G10); confirmation required: C4, for `refines(Seats)` only | |
```

## An amendment or erratum on an accepted record

**Status line.** Append ⟨Bnn⟩ after the existing marks.

**Status note.** Only when a criterion newly attaches: `C4 attaches also to A3 (Batch 39): it discharges the upstream
clause A2 deferred ⟨B39⟩.`

**Pending line.** Items still pending stay first and bold. The ratified item moves after them, with its drafted date:

```text
**Pending:** none. A3, drafted 2026.11.03: the upstream report of A2's two cases is made (Open obligations), ratified
2026.11.03 (Batch 39) and applied inline ⟨B39⟩. <older entries as they stood>
**Pending:** **A4**, drafted 2026.10.08, dependent on ADR-0054 (Proposed): ..., marked inline and not applied. E1, drafted 2026.11.02: ..., ratified 2026.11.02 (Batch 38) and applied inline ⟨B38⟩. <older entries>
```

**Erratum, inline.** The sentence itself is corrected and the italic pending note below it is removed:

```text
fail together ~~(Moon & Varshney §4.6; Knight & Leveson)~~ *(Knight & Leveson; the vacuous gate output is Moon &
Varshney §4.6 and Appendix B ...)* ⟨E1⟩ ⟨B38⟩.
```

**Amendment, inline.** A pending heading becomes the applied heading, and "Met at ratification" follows the condition:

```text
**The upstream report is made** ⟨A3⟩ ⟨B39⟩. **Ratification condition:** (1) ...; (2) ... **Met at ratification** ⟨B39⟩:
on 2026.11.03. (1) Checked by the assistant through the GitHub API: ... (2) The custodian read the issues against §8
and confirmed both, in session.
```

Where the amendment says a sentence above "becomes" or "gains" something, the text marked ⟨An⟩ is in force as
written and the Bnn row says so. A dependent amendment drafted as a quoted clause goes into its row's cell (B28) and
its pending note is removed. An annex row is inserted with ⟨Bnn⟩.

**The item's own History row.** Edit it in place. The change cell ends `Applied inline`. The state cell keeps the
drafting provenance after the new mark:

```text
**Applied** ⟨B39⟩ — ratified 2026.11.03 (Batch 39), with ADR-0046 A3; drafted 2026.11.03 by the assistant at the custodian's direction
```

**The Bnn row, lead record.** State is `Ratified`:

```text
| B39 | Ratification | **A3 ratified 2026.11.03** by the genesis custodian (ADR-0029 §2), in Batch 39, with ADR-0045 A4, its dependent entry, ratified in the same batch, and applied inline: <what the text now says>. No decision text changes. **Confirmation required under C4 for A3**, the custodian's decision: <why; which others do not apply>. **A3's condition is met** (Open obligations, "Met at ratification" ⟨B39⟩): (1) by the assistant through the GitHub API; (2) by the custodian's reading, in session. ADR-0045's pin moves, and the premise routes are renewed (`spec/premise-routes-results-2026.11.03.txt`). **Not reviewed by a reader other than the drafter** (ADR-0029 A2.5) | Custodian's instruction and decisions, 2026.11.03: ratify A3 with ADR-0045 A4 as Batch 39; C4 on A3 | Ratified |
```

For several items: `**A2, E3 and E4 ratified 2026.10.08** ..., together, with ADR-0045 A3 and E1 and ADR-0053 E1,
ratified in the same batch`. Alone: `in Batch 38, alone`.

**The erratum row question.** Batch 26 gave an erratum alone no Bnn row, Batch 37 gave ADR-0053 E1 none (its
lead's row names it), and Batch 38 gave one. Write the row: it is the latest practice, and it is where the A2.5
sentence goes.

## Dependent entries

**An amendment ratified with its lead.** Kind `Ratification (dependent entry)`, state `Ratified`, source naming the
lead's row:

```text
| B39 | Ratification (dependent entry) | **A4 ratified 2026.11.03** by the genesis custodian (ADR-0029 §2), in Batch 39, with ADR-0046 A3, ratified in the same batch, and applied inline: ... ADR-0046 A3's condition is met (ADR-0046, Open obligations, B39). The pin moves, and the premise routes are renewed (`...`). **Not reviewed by a reader other than the drafter** (ADR-0029 A2.5) | Custodian's instruction, 2026.11.03; ADR-0046 B39 | Ratified |
```

**A note another record's ratification adds**, where no amendment was drafted. State is `**Applied**`:

```text
| B36 | Ratification (dependent entry) | **§5's gates and §1's composition proved in Lean.** ADR-0053, ratified 2026.10.06 in Batch 36, names ... No decision text changes | ADR-0053 B36 | **Applied** — with ADR-0053's ratification |
```

Word it as the lead's dependent-entries section words it. It is the lead's text being carried out, so a dependent
entry that needs improving is a finding to raise with the custodian.

## A dependent amendment on a provisional record

The Bnn row says so: `**A3 depends on a record ratified provisional** (ADR-0050 or ADR-0052): the text is in force
and subject to redesign with that record (ADR-0029 A4).` In the bootstrap set it is not confirmation-required and the
genesis attestation names it as provisional.
