# Authoring a TOPAK family diagram

One module per diagram: `d_<id>_<slug>.py` exposing `ID`, `SLUG` and `build() -> Canvas`.
`python3 diagrams/gen-topak-family.py <ID>` writes `diagrams/topak/<ID>-<SLUG>-<DATE>.svg` and prints
any overlap warnings. A diagram is finished only when it prints no warnings and both themes have been
looked at as rendered images.

## Content rules

- **Every statement traces to a record.** Draw from the records themselves (ADRs, G8, ToO rev 12,
  `spec/`, `floor/`, `mechanism/`), not from memory. Cite the record (ADR-00nn §n, ToO §n, G8 §n) in
  the card or table and list every source in the Canvas `sources` string.
- **G8 is the state of record.** Where the narrative and the checkpoint disagree, the checkpoint wins.
- **Proved and checked are distinct words** (ADR-0046 §1). *Proved* only of an invariant a proof module
  discharged, with its hypotheses; *checked* of TLC's mutations and witnesses and of the gates. Neither of
  the running reference.
- **Status is shown, not implied.** Use `status=` pills: `accepted` (add `status_extra="C1, C4"` for
  confirmation-required markers), `proposed`, `draft`, `notbuilt`, `built`, `superseded`,
  `withdrawn`, `open`. Never present a Proposed record, a draft floor or an unbuilt mechanism as in force.
- **Full tables.** When a record has a table, draw all of it. Diagrams are read zoomed in and printed
  at poster size; width may go to 3600 px and height is computed.
- Names in code font with backticks: `Contained`, `Actuate`, `T_obs`.

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

- Solid arrows carry authority or data; dashed arrows (`dash="7 5"`) are subtraction, denial or a
  path that only removes authority.
- Boundaries are `region(...)`, with the boundary register id in the label where one exists (B1–B14).
- Body text is 13.5–15 px, card titles 16 px, section headings 19–22 px.

## Library (src/lib.py)

- `Canvas(id, title, subtitle, width, sources)`; content starts at `c.y`, between `c.x0` and `c.x1`.
- `c.card(x, y, w, title, [rich strings], accent, status=, h=, size=, bullets=, tint=, dash=, draw=)`
  returns its height; `draw=False` measures only, which is how rows of cards are given equal heights.
- `c.table(x, y, [(title, width, {mono, bold, accent})...], rows, size=, accent=)`. A row is a list of
  rich strings, `{"group": label, "accent": a}` or `{"cells": [...], "accent": a}`. Returns its height.
- `c.region(x, y, w, h, label, accent, dash=, tint=)`: a boundary container with a label tab.
- `c.arrow([(x, y), ...], accent, dash=, label=, lpos=, loff=, both=)`: an orthogonal polyline.
- `c.para`, `c.text`, `c.pill`, `c.status`, `c.label`, `c.line`, `c.legend`, `c.heading`.
- Rich text: `**bold**`, `` `code` ``, `[[red|accented bold]]`, and `\n` for a hard break.
