# Review: looking, checking content, checking agents, triaging regeneration

## Contents

- [Rendering and looking](#rendering-and-looking)
- [The review checklist](#the-review-checklist)
- [Checking a drawing agent's work](#checking-a-drawing-agents-work)
- [Triaging a regeneration diff](#triaging-a-regeneration-diff)

## Rendering and looking

`scripts/render.py` renders light with `rsvg-convert` (which reads the light presentation attributes) and dark
with headless Chrome (it inserts `data-theme="dark"` and screenshots an HTML wrapper, since rsvg ignores the CSS
custom properties that carry the dark theme).

1. **Whole page, both themes**, at about 1300 px wide: `uv run scripts/render.py <ID>`. This shows layout: bands,
   columns, empty space, whether the picture reads.
2. **Each region at reading zoom**, cropped by a text needle or coordinates, at about 1800 px:
   `--needle "<text in the region>" --h 900 --width 1800`. This shows text, arrows and contrast.
3. **Dark crops of the picture and of any red, amber or violet text.** Contrast fails there first.

Read the PNGs with the image reader. Do not stop at the generator's "no warnings".

## The review checklist

Layout:
- [ ] No text clipped at a card edge or the canvas edge
- [ ] No card shorter than its text; rows of equal height
- [ ] No arrow through a card or a label; no label sitting on a line it does not belong to
- [ ] Legends match what is drawn
- [ ] Dark theme legible everywhere, including tinted rows and pills

Content:
- [ ] The status strip shows every record's status and markers, and what is not written or built
- [ ] Every table of the records is there, whole
- [ ] Every card cites a section; `sources` lists everything drawn from
- [ ] *checked*, *proved*, *certified* used as defined, never of running code
- [ ] Every count and quotation matches its source (spot-check the ones an agent flagged, and any you would not
      bet on)
- [ ] Every claim the records do not make is headed as the diagram's; every unstated number is labelled
      illustrative
- [ ] Ratification conditions item by item, met or not met
- [ ] The footer names the right state; an amendment carries its note

## Checking a drawing agent's work

- **Verify each reported inconsistency in the files** before passing it on. In the worked example, two of twenty
  reported items did not hold up: one was two true statements about different things, the other a module that
  covers two records.
- **Look at what the agent says to look at first**, and then at the picture regardless.
- **Check the agent's own additions**: cross-reference columns, assembled matrices, examples. They are where a
  diagram adds an error.
- **Confirm it touched only its files** (`git status`), and that the library and other diagrams are unchanged.
- **Run the regression check** after all agents finish.

## Triaging a regeneration diff

For each unexpected file from `regen_check.py`:

1. Read the change as text:
   `git diff --word-diff=porcelain <svg> | grep -E '^[-+][^-+]' | sed 's/<[^>]*>//g'`.
2. Classify it:
   - **Coordinates only, in the last digits, across many diagrams**: the interpreter changed. Regenerate under the
     pin.
   - **New or changed text that matches a record's newer revision**: the diagram has fallen behind a batch. It is
     owed an amendment, done on purpose with its own note.
   - **Counts that changed to another module set's**: the diagram's input selection picked up the wrong file. Fix
     the selection (name the file), not the drawing.
   - **Everything shifted after a library edit**: the library change was not neutral. Revert it, or regenerate and
     amend the family deliberately.
3. Report it as a finding, then restore (`--restore`) or amend. Never fold an unexpected change into an unrelated
   commit.
