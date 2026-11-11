# The grader brief (register)

The brief of the first of five register graders; the other four differ only in the section "Your sources".

---

A self review of the TOPAK corpus is under way at commit `bbda621` (2026.11.10). The corpus has reviewed itself
before, in dated documents under `derived/`, and most of what those documents found was never dispositioned. Your
job is to gather the items in your assigned sources into one table and say, for each, how it stands **at this
tree**.

## Where you work

- Read under `/home/user/TOPAK` only. It is at the pinned commit. **Change nothing there.** Run only read-only
  commands (`grep`, `sed -n`, `git log`, `git diff --stat`, `git show`, `wc`, `sha256sum`). No builds or tests.
- Write only under `<scratch>/graders/R1`.
- State of record: checkpoint G11 (`checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md`, commit `ce8f460`),
  whose §7 is the open list (items 1 to 108, cumulative; earlier checkpoints hold the items G11 does not restate).
  Batches 38 and 39 came after it and are recorded only in History rows of ADR-0024, ADR-0045 and ADR-0046.
  `decisions/README.md` is the record index. `mechanism/GAPS-AND-ASSUMPTIONS.md` is the reference's own register.
  `derived/README.md` indexes the derived documents.

## Your sources

The three critical reviews. Their findings are tagged CR-1 to CR-39.

- `derived/topak-critical-review-2026.09.16.md` (CR-1 to CR-20)
- `derived/topak-critical-review-2026.09.25.md` (CR-21 to CR-26; its §5 re-grades CR-1 to CR-20; §8 has same-day dispositions)
- `derived/topak-critical-review-2026.10.02.md` (CR-27 to CR-39 in §6; its §5 re-grades CR-1 to CR-26; §8 lists seven asks)

One row per CR, CR-1 to CR-39, graded at this tree, starting from the 10.02 review's own re-grade where it has one and checking what has moved since (G10, G11, Batches 38 and 39, ADR-0047 to ADR-0068, `spec/`, `mechanism/`). Also one row for each of the seven asks in the 10.02 review's §8. In `evidence`, give the 10.02 status in a few words and then what you confirmed at the pin.

## What to produce

### `<scratch>/graders/R1/register.tsv`

Tab-separated, with this header row and one row per item:

`source_file	source_id	source_line	kind	statement	against	basis	status_at_pin	evidence	carried_by	seed	cluster`

- `source_id`: the source's own identifier (CR-27, R-3, F2, "finding 17", "§16 row 4", "suggested entry 3"). **Mint
  no identifiers.** Where the source gives none, use its section and ordinal.
- `source_line`: the line in the source file where the item is stated.
- `kind`: finding | suggested entry | stale sentence | gap | exposure | open obligation | pending amendment | question.
- `statement`: one line, at most 220 characters, in the source's own terms.
- `against`: the file, record or clause the item is about.
- `basis`: in force | Proposed | pending | living document | evidence | process.
- `status_at_pin`: exactly one of
  - `open` (still true of the tree; you confirmed it),
  - `appears addressed` (the tree now holds a change that answers it; do not write "closed"),
  - `superseded` (what it was about is gone or replaced),
  - `partly addressed`,
  - `cannot tell` (say why in evidence).
- `evidence`: `file:line` for what you checked at the pin, and a few words. Every row needs one. Check the tree; do
  not take a later document's word for it where the tree can be read.
- `carried_by`: where the corpus itself now tracks it: `G11 item N`, `ADR-00NN open obligations`, `GAPS <row>`,
  `<later derived file> <id>`, or `nowhere`. Grep for the identifier and for the subject.
- `seed`: `yes` if the item is a concrete defect in a specific file that someone reading that file carefully, with
  no knowledge of this list, could find and that is still `open`; else `no`.
- `cluster`: for a seed, which part of the tree holds it: A (ADR-0001 to 0023), B (0024 to 0029), C (0030 to 0032,
  0034 to 0036, floor/, policies/), D (0037 to 0043, 0051), E (0044 to 0046, 0053, spec method documents and the
  binding table), F (0047 to 0050, 0052), G (0054 to 0056), H (0057, 0058, the specification graph), I (0059 to
  0068 and their modules), J (ADR-0033, mechanism/), K1 (narrative/theory-of-operation.md), K2 (glossary,
  architecture description, guides, READMEs, indexes, pins).

### `<scratch>/graders/R1/notes.md`

Short. What you could not check and why; any source item you found to be wrong in its own terms; patterns worth
knowing (for example, items that several sources repeat). Under 400 words.

### Your final message

Under 150 words: row count, counts by `status_at_pin`, count of seeds, and anything that surprised you.
