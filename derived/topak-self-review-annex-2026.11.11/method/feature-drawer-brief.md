# The drawer brief (new feature rows)

The brief of the overlay drawer; the other differs only in "Your records".

---

A self review of the TOPAK corpus is under way at commit `bbda621` (2026.11.10). The feature list
`derived/topak-feature-list-2026.11.05.md` will be regenerated. It has 607 rows and none for the records drafted
after it. Your job is to draw the rows for those records, in the list's own form.

## Where you work

- Read under `/home/user/TOPAK` only. It is at the pinned commit. **Change nothing there.** Read-only commands only.
- Write only under `<scratch>/graders/FL7`.
- Read the list's lines 1 to 149 first (basis, limits, status key, the principles P1 to P11 and P8.1 to P8.9), and
  then twenty rows of §10 (lines 917 to 969) as the model for rows drawn from Proposed records.

## Your records

`decisions/ADR-0059.md` to `decisions/ADR-0068.md`, the command-chain overlay, all Proposed and all drafted as an overlay's and not the archetype's. With them the eight modules `spec/Federation.tla`, `Intent.tla`, `Membership.tla`, `Alone.tla`, `Outstanding.tla`, `PlaneClock.tla`, `Peer.tla`, `Release.tla`, their `-results-2026.11.10.txt`, `-proof-results-2026.11.10.txt` and `-proof-cert-results-2026.11.10.txt` files, and `spec/proof-scan-results-2026.11.10.txt`. Read each record's History rows (R1, and R2 where there is one): R2 changed ADR-0060, 0062, 0063 and 0067 after the modules were written. Include a row for each of ADR-0068's adversaries, trusted-base rows and assumptions of use, and for each `FD` entry of ADR-0067.

## How to draw a row

- **One row per distinct thing the record decides, builds, checks or declines**: a mechanism, a field, a rule, a
  property with its mutation, a trusted-base row, an assumption of use, a position, a finding the record states
  about itself. The list averages about ten rows a record. Do not draw a row for a section heading.
- **Feature**: a bold first sentence that states the feature, then one or two sentences of what it is. Quote
  exactly where you quote. No sentence may say more than the record says.
- **Basis**: record and section; module and results file where there is one.
- **Status**, in the list's vocabulary and order: the record's standing first (`Proposed`, and for the overlay
  `Proposed (overlay)`), then the evidence, each only if you opened the artifact: `Checked (TLC)`, `Proved (TLAPS)`,
  `Certified` / `not certified`, `Built` / `not built`, `Declared`, `Practice`, `Open` (name the record's own open
  obligation or unmet ratification condition). Never write *proved* of something only TLC checked. Never write
  *proved* of the code.
- **Principle**: which of P1 to P11 or P8.1 to P8.9 the feature answers to; and, where it **strains or would
  reverse** one, say so and cite the record's own words (the overlay records each list what the archetype's records
  would owe).
- **Not the archetype's.** Where a record says it is an overlay's and not the archetype's, the row says so.
- **Record against module.** Where a record states a property and its module states it differently, or not at all,
  or at different constants, draw the row from the record and put the difference in `note`.

## What to produce

### `<scratch>/graders/FL7/rows.tsv`

Tab-separated, this header:

`record	section	principle	feature	basis	status	note`

### `<scratch>/graders/FL7/notes.md`

Under 300 words: what you could not place, and which existing principle statements (list lines 86 to 113) these
records would change if they were in force.

### Your final message

Under 120 words: rows drawn per record, and how many rows carry a note.
