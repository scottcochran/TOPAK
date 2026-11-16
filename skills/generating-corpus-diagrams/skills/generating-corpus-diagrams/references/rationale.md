# Rationale: why generate the diagrams, and why it pays even if nobody looks

## Contents

- [The claim](#the-claim)
- [The six ways drawing surfaces findings](#the-six-ways-drawing-surfaces-findings)
- [The worked example, 2026.11.10](#the-worked-example-20261110)
- [What it buys besides pictures](#what-it-buys-besides-pictures)
- [Where the argument stops](#where-the-argument-stops)
- [Why generated, and not drawn by hand](#why-generated-and-not-drawn-by-hand)

## The claim

A design corpus is mostly prose: records, a narrative, results files. Prose is lenient. It lets a sentence go stale
when a neighbouring record is revised, lets a count drift from the table it counts, lets a quotation lose a word,
lets one record omit a section its siblings have. Readers forgive all of these, which is why they persist.

A generated diagram is strict in exactly those places. Its generator must set every table cell, give every card a
source, pick each status from a fixed set of pills, keep *checked*, *proved* and *certified* apart, and come out
byte for byte the same when nothing it reads has moved. Writing one compiles the records into a form where those
faults show as empty cells, counts that do not match, two sentences that cannot share a page, or a diff nobody
expected. **Most of the value is in the attempt to draw, not in the picture.**

## The six ways drawing surfaces findings

1. **Full tables leave nothing unplaced.** A drawn table cannot skip a row. Setting a record's table whole put three
   cells side by side that its prose had counted wrong. Giving every ratification item a met/not-met pill showed
   that whole classes of items carried no state at all.
2. **Every statement traces to a record, by section.** A drawer must put the cited row on the page, so quotations
   get compared with their sources, and a count of "the sixth item" gets traced to an amendment that is still
   pending. A prose reader takes the citation on trust.
3. **Two records on one page.** When a sentence of one record is drawn beside a sentence of another, a revision
   that reached one and not the other shows. Two agents drawing two different records found the same split
   independently.
4. **Joins between records and their evidence.** A column relating each claim of a record to the module property
   that states it shows its empty cells. The empty cell is the finding: a decision no module states, a check a
   module abstracts away while saying it relies on no other.
5. **Generators that read the corpus, and regenerate byte for byte.** A diagram that computes digests and compares
   them with what records cite catches a stale sentence elsewhere. A whole-family regeneration that should change
   only the new diagrams shows every diagram that has fallen behind a batch, and every diagram whose input selection
   has started picking up the wrong file.
6. **Checking the drawers.** Agents' reports, and the drawer's own reading, are leads. Checking each against the
   files keeps the findings honest, and drops the ones that are not (two of twenty in the worked example).

## The worked example, 2026.11.10

Nine diagrams of the TOPAK command-chain overlay (ten Proposed records, ADR-0059 to ADR-0068, and eight TLA+
modules) were drawn by nine agents in parallel, in nine to seventeen minutes each and about 2.3 million tokens in
all. The records had been revised the same day to take the modules' findings. Drawing them found eighteen more:

| Kind | Count | Examples |
|---|---|---|
| Against the records | 10 | a record never revised when its modules arrived; a consequence counting three where its table has two; a wording split left by a revision of one record and not its neighbour; a quotation of a floor rule that drops one of its verbs; unmet conditions with no "Not met"; one record of ten missing a section the others have |
| Between records and modules | 5 | a check a record lists that its module abstracts away; a decision (hold when an extent ends) no module states; a module stating a stronger bound than its record; module headers describing records as drafted, frozen by digest |
| In other artifacts | 3 | a README sentence made false by the revision; two diagrams a batch behind; one diagram reading the newest results file by name, which had become another module set's |

Thirteen of the eighteen came from the act of drawing (mechanisms 1–4). Three came from regeneration and
build-time reads (mechanism 5). One defect was in a diagram itself: an example with numbers the record did not
state, unlabelled until review. The full write-up is
`derived/topak-command-chain-diagram-findings-2026.11.10.md` (on branch `diagrams-command-chain` when this skill was
written).

Building this skill found one more: regenerating under Python 3.14 changed 26 diagrams that Python 3.9 reproduces
byte for byte, because `sum()` over floats became compensated in 3.12. The interpreter is an input, and the
regression check now pins it.

## What it buys besides pictures

- **A consistency check over prose**, run by writing code (mechanisms 1–4).
- **A regression test over the corpus**: a whole-family regeneration after every batch, where any diff that is
  not a declared amendment is a finding (mechanism 5).
- **Gates**: a diagram that reads records or results at build time and raises on a mismatch fails the way a
  gate does. Prefer that to a hard-coded number.
- **A structured cold reading.** Each drawing agent reads its records with no draft to agree with, and must place
  every claim. That is a reading the drafter cannot give their own text.
- **Cheap repetition.** Regenerating takes seconds, and redrawing after a revision is a bounded job.

## Where the argument stops

- **A diagram decides nothing.** A finding from drawing is a lead until someone reads the record.
- **A diagram can add an error as well as find one**: an unlabelled example, a cross-reference the records do not
  make. Label both, and review for them.
- **It is not an independent reader.** Drawing agents of the same model family as the drafter share its blind
  spots. They are independent in context, not in lineage, and do not discharge a requirement for a reader who is
  not the drafter.
- **The overlap checker is a layout check with a known blind spot**, and says nothing about content.
- **Nothing here is verification.** The diagrams show where a record, a module and a file disagree. They prove
  nothing.
- **A finding not drawn is not found.** Nothing measures what a drawer read past.

## Why generated, and not drawn by hand

- **Text is measured, not placed.** The library measures every run with the font's advance widths and wraps it,
  so a card grows with its text and a layout is computed. Hand-drawn diagrams are edited until they look right and
  then drift from their records.
- **Both themes from one source.** Every colour is written once as a light presentation attribute and once as a
  CSS custom property that switches under `prefers-color-scheme` or `data-theme`.
- **Byte-for-byte regeneration** is what makes the family a regression test. A hand-drawn diagram has no "before".
- **Build-time reads** make a diagram fail when its record changes, instead of quietly going stale.
- **No dependencies.** The standard library only, so the generator runs wherever the corpus is checked out.
