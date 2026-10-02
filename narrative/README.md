# Narrative

The living layer, cut with each checkpoint. Records are the decisions; checkpoints are the state of record; these
two files explain how it fits together and what the words mean.

- `theory-of-operation.md` — the head. At the 2026.09.30 cut its bytes were revision 10's; revision 11 (2026.10.01, tag
  `ToO-rev11`) is the first revision made as an edit, and revision 12 (2026.10.02, tag `ToO-rev12`) is cut
  against G8. A revision is
  an edit, a "Changes from revision N" appendix, a commit and a tag `ToO-revN`; the checkpoint cut with it measures
  the head by digest. `git diff ToO-rev9 ToO-rev10 -- narrative/theory-of-operation.md` is how two revisions are read
  side by side.
- `glossary.md` — the head. Revised in place, tagged `glossary-<date>`: 2026.09.30 against G6, 2026.10.01 against G7,
  2026.10.02 against G8.
- `revisions/` — a closed archive of the dated Theory of Operation files written before the cut (09.10 through
  revision 9), byte-identical moves. Six predate git and have no other home. Nothing is added after the cut.

Where the narrative and the current checkpoint disagree, the checkpoint wins.
