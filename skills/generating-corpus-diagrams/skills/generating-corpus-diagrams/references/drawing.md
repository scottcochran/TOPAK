# Drawing: the library, layout, build-time reads, determinism, pitfalls

## Contents

- [The library](#the-library)
- [Layout patterns](#layout-patterns)
- [The picture of the mechanism](#the-picture-of-the-mechanism)
- [Build-time reads](#build-time-reads)
- [Determinism](#determinism)
- [Pitfalls that cost time](#pitfalls-that-cost-time)

## The library

`diagrams/topak/src/lib.py`, standard library only. Every primitive measures its text with the font's advance
widths (`metrics.py`, metric-compatible with Arial/Helvetica), wraps it, and returns the height it used.

| Call | Does |
|---|---|
| `Canvas(id, title, subtitle, width, sources, note=None, state=None)` | one diagram; content starts at `c.y`, between `c.x0` and `c.x1` |
| `c.card(x, y, w, title, [rich], accent, status=, h=, size=, bullets=, tint=, dash=, draw=)` | a titled box; returns its height; `draw=False` measures only |
| `c.table(x, y, [(title, width, {mono, bold, accent})], rows, size=, accent=)` | a table; a row is a list of rich strings, `{"group": label}` or `{"cells": [...], "accent": a}`; returns height |
| `c.region(x, y, w, h, label, accent, dash=, tint=)` | a boundary container with a label tab |
| `c.arrow([(x, y), ...], accent, dash=, label=, lpos=, loff=, both=)` | an orthogonal polyline with an optional label |
| `c.para`, `c.text`, `c.pill`, `c.status`, `c.label`, `c.line`, `c.legend`, `c.heading` | the rest |

Rich text: `**bold**`, `` `code` ``, `[[red|accented bold]]`, `\n` for a hard break.

The generator, `diagrams/gen-topak-family.py [IDS]`, imports every `d_<id>_<slug>.py` in `src/`, calls `build()`,
writes `<ID>-<SLUG>-<DATE>.svg`, and prints each path followed by any `WARNING` (overlap) lines. A module that
fails to import prints `ERROR` and the rest still build.

## Layout patterns

The template (`assets/diagram_template.py`) carries these helpers. Copy them into a module rather than editing the
library, so the library's output stays fixed for every other diagram.

- **Status strip**: the label, then pills that wrap at the right margin.
- **Band**: a 22 px heading with an optional status pill; content starts 54 px below.
- **Row of cards** (`row_cards`): measure every card in the row with `draw=False`, then draw them all at the
  maximum height. This is the only safe way: see the first pitfall.
- **Stack**: cards one under another with a fixed gap; returns the bottom.
- **Two columns**: a left stack and a right stack from the same top; continue from `max(bottom_left,
  bottom_right)`.
- **Tables whole**: give the table the full width when it has many columns; let the library wrap cells.
- **Matrix of mutations by properties**: one row per mutation, one column per property, cells "breaks" or "holds",
  read from the rows file where you can.

## The picture of the mechanism

Most diagrams of a record open with a picture: planes, components or principals as regions or cards, and arrows
for what moves between them. Keep the arrows orthogonal and route them through gaps you have reserved. The overlap
checker cannot see an arrow crossing a card, so look. Number the arrows (①–⑧) and explain them in a key beside
the picture when there are more than four. Put each element's citation on it.

## Build-time reads

A diagram that draws a record's table, a results file's counts or a pin's value can read it at build time instead
of copying it. When that file changes, the diagram follows, or fails.

- **Parse strictly and raise.** A missing file, a number that does not parse, or a table whose shape is not the
  expected one is an exception, so the generator prints `ERROR` and the build fails, like a gate.
- **Compare as well as read.** Computing the digests of the files a record cites and comparing them with the
  citation turns a diagram into a check on the record.
- **Name the file, or select by what the diagram draws.** Never take "the newest file matching a pattern": when a
  results file of another kind arrives under the same pattern, the diagram silently draws the wrong thing. (In
  TOPAK, H6 reads the newest `proof-scan-results-*.txt`, which since 2026.11.10 is an overlay's eight-module scan.)
- **Strip what must not be drawn** at read time (TOPAK's `strip_external`), rather than by hand afterwards.

## Determinism

The family is a regression test only if an unchanged input gives unchanged bytes.

- **Pin the interpreter.** Python 3.12 changed `sum()` over floats to compensated summation, which moves
  coordinates in the last digits. Generate under the interpreter the family was generated with
  (`uv run --no-project --python 3.9 python diagrams/gen-topak-family.py`); `regen_check.py` does this. Moving the
  pin is a whole-family regeneration committed on its own.
- **No clocks, randomness or environment** in a diagram. The date is the library's constant.
- **Sorted iteration.** Sort globs and dictionary keys before drawing them.
- **No hidden state between modules.** The library's `TEXT_BOXES` is cleared per diagram by `Canvas.svg()`. Do not
  add module-level state that another diagram could see.

## Pitfalls that cost time

- **A card that outgrows its row.** The checker compares text boxes and blocks, and a card drawn at an `h=`
  computed over other cards can be taller than that if its own text needs more room. Compute every row's height
  over every card in the row.
- **rsvg drops the space where bold text meets code.** It renders "the`federation`stage". That is rsvg only:
  browsers render it correctly. Check dark renders (Chrome) before "fixing" it.
- **A needle must lie in one text element.** `render.py --needle` matches the text content of one `<text>` with
  tags stripped. A phrase broken across a wrap or a card is two elements.
- **`sips --cropOffset` may center-crop** instead of cropping at the offset. `render.py` crops by rewriting the
  viewBox, which is exact in both themes.
- **zsh aliases `c`**, so a shell function named `c` misbehaves.
- **Arrows are hand-routed** and invisible to the overlap checker. Every picture needs a look.
