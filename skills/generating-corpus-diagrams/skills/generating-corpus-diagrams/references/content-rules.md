# Content rules

What may go on a diagram, and how it is said. In TOPAK the binding text is `diagrams/topak/src/AUTHORING.md`; this
file says the same rules with the reason for each, and adds what the 2026.11.10 drawing taught.

## Contents

- [Sources](#sources)
- [The vocabulary of claims](#the-vocabulary-of-claims)
- [Status is shown, not implied](#status-is-shown-not-implied)
- [Full tables](#full-tables)
- [The diagram's own claims](#the-diagrams-own-claims)
- [Footers, dates and amendments](#footers-dates-and-amendments)
- [The README](#the-readme)
- [Visual language](#visual-language)

## Sources

- **Every statement traces to a record**, cited by section on the card or in the table (`ADR-0063 §3`), and every
  source is listed in the Canvas `sources` string. *Why:* a diagram that says something its records do not is a
  second, unreviewed record.
- **Draw from the records, not from memory, a brief or a summary**, and from the records as revised (read the
  History rows). *Why:* the summary is where drift starts.
- **The checkpoint is the state of record.** Where the narrative and the checkpoint disagree, the checkpoint wins,
  and the footer names the checkpoint drawn against.
- **Where two sources disagree, draw what each says and report it.** Do not reconcile them on the diagram.

## The vocabulary of claims

Keep these words distinct, and use none of them of running code:

| Word | Said of |
|---|---|
| *checked* | TLC's rows (mutations, witnesses) at small constants; the floor's gates; trace validation |
| *proved* | an invariant a proof module discharged, with its hypotheses |
| *certified* | a proof module whose every obligation is accounted for by a route an independent checker accepted, or by normalization or LS4, said as such ("certified, with 7 LS4 temporal steps that no checker confirms") |
| *proved in Lean* | an encoding, a transcription or a statement in Lean; never "proved" alone |

*Why:* each word is a different claim with a different trusted base. Blurring them is the commonest way a diagram
overstates its records.

## Status is shown, not implied

- A **status strip** at the top of every diagram of a record: each record with its status pill and confirmation
  markers, and what exists and what does not (module, floor stage, reference).
- Use the library's statuses (`accepted`, `proposed`, `draft`, `notbuilt`, `built`, `superseded`, `withdrawn`,
  `open`, `provisional`, `genprov`) and custom dashed pills for what the library lacks ("Not written").
- **Never draw** a Proposed record as settled, a provisional one as final, a draft or genesis-provisional floor as
  ratified, or an unbuilt mechanism as in force. Mark stand-ins (BOOTSTRAP, SIMULATED) where they stand.
- **Every ratification condition item by item**, each with met or not met. If a record leaves an item unmarked,
  draw it as the files show and report the gap.

## Full tables

When a record has a table, draw all of it: every row, every column. Diagrams are read zoomed in and printed at
poster size, so width may go to 3600 px and height is computed. *Why:* full tables are what make drawing an audit.
The row a summary skips is the one that disagrees with the prose.

## The diagram's own claims

- **A cross-reference the records do not make** (a module property beside a floor entry or an adversary; a matrix
  assembled from several records' sentences) is allowed when it helps, and is headed as the diagram's own, in the
  column or card title. Leave a cell empty where nothing supports it, and state a premise where one applies.
- **A number no record states** (an example budget, a timeline's positions) is labelled illustrative on the
  diagram.
- **A paraphrase is not a quotation.** Quote exactly, or say "in effect".

## Footers, dates and amendments

- The family shares one `DATE` constant in the library, so an amended diagram overwrites its same-dated file and
  the README carries an "Amended <date>" note. An untouched diagram regenerates byte for byte.
- The footer names the state of record. A diagram drawn after the family's cut passes `state=` (a library constant
  or a string naming the checkpoint, batches and records). An amended one passes `note=` (for example
  `AMENDED_G11`). An unstamped diagram keeps the cut's footer and its bytes.
- Amend on purpose. A diagram that changes on regeneration because its input moved is a finding until someone
  decides to amend it, and the amendment gets its own note.

## The README

- One row per diagram in the family README's table, under its group: id, linked title, what it shows (what it
  draws, the records and their status, anything notable it does not claim).
- One dated paragraph per drawing or amendment: what was drawn or amended, against what state, which statuses are
  new to the family's language, and which diagrams were deliberately **not** amended and why.

## Visual language

| Accent | Meaning |
|---|---|
| `blue` | authority, issued rules, promotion, ratified records |
| `teal` | the mechanism and the verified object |
| `green` | Run; subtraction; the safe direction |
| `amber` | Proposed |
| `violet` | draft, not ratified; consensus (P) |
| `red` | gaps, denials, refusals, not built, residual risk |
| `brown` | humans, custody, the gate |
| `pink` | detection, Observers |
| `grey` | neutral, external, withdrawn |

Solid arrows carry authority or data; dashed arrows (`dash="7 5"`) are subtraction, denial, or a path that only
removes authority. Boundaries are regions, labelled with the boundary register id where one exists. Body text
13.5–15 px, card titles 16 px, section headings 19–22 px. Names in code font.
