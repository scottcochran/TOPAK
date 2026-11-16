# generating-corpus-diagrams

Generated SVG diagrams of a design corpus, held to the corpus's own standard of evidence, and used as a check on
it whether or not anyone looks at the pictures.

## What it does

Guides Claude through drawing, reviewing and maintaining a diagram family like TOPAK's (`diagrams/topak/`):

1. **Draw from the records**: one dependency-free Python module per diagram on a shared library that measures and
   wraps text, adapts to light and dark themes, and warns on overlap. Every statement cites a record by section,
   every table is drawn whole, status is shown and never implied, and the words *checked*, *proved* and *certified*
   stay distinct.
2. **Look at it**: render both themes whole and cropped at reading zoom, and read the images, because the overlap
   checker sees text on text and nothing else.
3. **Verify the content** against the records, and label anything the diagram adds (a cross-reference, an
   illustrative number).
4. **Regenerate the family** under a pinned interpreter and treat any change that is not a declared amendment as a
   finding: a record, a results file or a pin has moved under a diagram.
5. **Draw in parallel** with one agent per diagram, from a shared brief, and check their reports before believing
   them.

## Why

Drawing is a strict second reading of the records. Prose tolerates a stale sentence, a miscounted list or a
drifted quotation; a generator that must set every table cell and cite every card does not. On 2026.11.10, drawing
nine diagrams of ten freshly revised records surfaced eighteen findings, thirteen from the attempt to draw alone,
and three from regenerating the family. Building this skill found one more: the family is reproducible only under
the Python it was generated with, because `sum()` over floats changed in 3.12.
[`references/rationale.md`](skills/generating-corpus-diagrams/references/rationale.md) has the argument and where it
stops.

## Layout

All paths below are relative to `skills/generating-corpus-diagrams/`:

```
.claude-plugin/plugin.json
skills/generating-corpus-diagrams/
  SKILL.md                    the workflow, parallel drawing, the regression check, quick reference
  references/
    rationale.md              why generate; the six ways drawing finds things; the worked example; limits
    content-rules.md          sources, vocabulary, status, full tables, the diagram's own claims, footers, README
    drawing.md                the library, layout patterns, build-time reads, determinism, pitfalls
    review.md                 rendering and looking, the checklist, checking agents, triaging a diff
  scripts/                    each runs with `uv run`; inline metadata, no packages
    new_diagram.py            next free ids; scaffold a module from the template
    render.py                 light (rsvg) and dark (headless Chrome), whole or cropped by needle or coordinates
    regen_check.py            regenerate everything under a pinned Python; new / expected / UNEXPECTED; --restore
  assets/
    diagram_template.py       the module new_diagram.py fills in; builds as it stands
    agent-brief.md            the brief for parallel drawing agents
```

## Requirements

- `uv` (runs the scripts and provides the pinned interpreter for regeneration)
- `rsvg-convert` (light renders; macOS `brew install librsvg`)
- Google Chrome or Chromium (dark renders; set `CHROME=` if it is not found)
- `git` (the scripts find the repository root with it)
