# Brief: one new diagram in the family

Copy this file to a scratch location, fill the bracketed parts, and point each drawing agent at it. Give each agent
its own assignment in its prompt: the id, the slug, a working title, the records and modules to read, and what to
cover. The brief says how; the assignment says what; the records say what is true.

You are drawing ONE diagram. [N] other agents are drawing others at the same time, each its own id.

## Where and what you may touch

- Repository: `[absolute path to the worktree]` (branch `[branch]`). Run everything from there.
- You may create and edit exactly two files: `diagrams/topak/src/d_<id>_<slug>.py` and the SVG the generator writes
  for your id. Do NOT edit `lib.py`, `metrics.py`, `AUTHORING.md`, the family README, any other diagram, any record,
  anything in `spec/`. Do not commit, stage, switch branches or stash. If the library lacks something, copy a helper
  into your module.
- Scratch files (renders, crops) go in `[scratch dir]/<ID>/`.

## Read first

1. `diagrams/topak/src/AUTHORING.md`: the content rules and the visual language. They bind you.
2. `diagrams/topak/src/lib.py`: the drawing library.
3. `[the most recent diagram of a comparable record]` as the model to follow, and one diagram with a system picture
   drawn with regions and arrows. Start from `skills/generating-corpus-diagrams/.../assets/diagram_template.py`
   (or run `scripts/new_diagram.py`).
4. The records named in your assignment, in full. Draw from them, not from this brief.
5. Where your assignment names a module or a results file, read its header and its results summary lines.

## Footer and status

- `Canvas(ID, title, subtitle, W, sources, state=[STATE constant])`. Width 3400 is usual, up to 3600.
- `sources`: every section, table and file you drew from.
- A status strip at the top. Every record shows its status and its confirmation markers [list them per record].
- Keep *checked* (TLC, the gates), *proved* (a proof module), *certified* (every obligation accounted for, LS4 steps
  named) and *proved in Lean* distinct, and never use any of them of running code.
- What does not exist is drawn as not written or not built. Never draw a Proposed record as settled.

## Style

- Plain declarative sentences, one idea each, citing the record by section. Bold the claim, then say it.
- Full tables: every row and column of every table in your records.
- Accents per AUTHORING.md. Dashed arrows are subtraction, denial or paths that only remove authority.
- A column or a picture that relates two things the records do not relate is the diagram's: head it so.
- Numbers the record does not state (an example) are labelled illustrative.

## Pitfalls

- Compute every row's height over every card in the row (`row_cards`). The overlap checker cannot see a card that
  outgrows a height computed over others.
- rsvg drops the space where bold text meets code. That is rsvg only.
- zsh aliases `c`; don't name a shell function `c`.

## Done means

1. The generator prints your SVG path and **no WARNING lines**.
2. You have looked at it in both themes, whole and cropped at reading zoom:
   `uv run [skill]/scripts/render.py <ID>` and `... --needle "<text>" --h 900 --width 1800`. Read the PNGs and
   look: clipped text, arrows through cards, labels on lines, cards too short, contrast in dark.
3. Everything on it traces to a record or a file. Where two sources disagree, draw what each says and report it.
   Do not fix records.

## Report back (under 300 words)

File paths; sections and tables drawn; SVG size; warning count (must be 0); anything you could not place, left out
or found inconsistent, each with where; anything a reviewer should look at first.
