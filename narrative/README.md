# Narrative

The living layer, cut with each checkpoint. Records are the decisions; checkpoints are the state of record; these
two files explain how it fits together and what the words mean.

- `theory-of-operation.md` — the head. At the 2026.09.30 cut its bytes are revision 10's. From here on a revision is
  an edit, a "Changes from revision N" appendix, a commit and a tag `ToO-revN`; the checkpoint cut with it measures
  the head by digest. `git diff ToO-rev9 ToO-rev10 -- narrative/theory-of-operation.md` is how two revisions are read
  side by side.
- `glossary.md` — the head. At the cut its bytes are the 2026.09.29 glossary's; the next revision is a commit here.
- `revisions/` — a closed archive of the dated Theory of Operation files written before the cut (09.10 through
  revision 9), byte-identical moves. Six predate git and have no other home. Nothing is added after the cut.

Where the narrative and the current checkpoint disagree, the checkpoint wins.
