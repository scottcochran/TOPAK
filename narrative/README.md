# Narrative

The living layer, revised against each checkpoint. Records are the decisions; checkpoints are the state of record; these
two files explain how it fits together and what the words mean.

- `theory-of-operation.md` — the head. At the 2026.09.30 cut its bytes were revision 10's; revision 11 (2026.10.01, tag
  `ToO-rev11`) is the first revision made as an edit, revision 12 (2026.10.02, tag `ToO-rev12`) is cut
  against G8, revision 13 (2026.10.02, tag `ToO-rev13`) against G9, and revision 14 (2026.10.05, tag `ToO-rev14`)
  against G10. A revision is an edit, a "Changes from revision N" appendix, a commit and a tag `ToO-revN`. **The
  narrative is revised against a checkpoint after it is cut**, so G10's manifest measures revision 13 and the next
  cut will measure revision 14. `git diff ToO-rev9 ToO-rev10 -- narrative/theory-of-operation.md` is how two revisions are read
  side by side.
- `glossary.md` — the head. Revised in place, tagged `glossary-<date>`: 2026.09.30 against G6, 2026.10.01 against G7,
  2026.10.02 against G8, again 2026.10.02 against G9 (tag `glossary-2026.10.02b`; a second revision on one date takes a
  suffix), and 2026.10.05 against G10.
- `revisions/` — a closed archive of the dated Theory of Operation files written before the cut (09.10 through
  revision 9), byte-identical moves. Six predate git and have no other home. Nothing is added after the cut.
- `architecture-description.md` — **a draft** (revision 2, 2026.10.05, against G10; untagged; revision 1 is
  measured by G10's manifest). An arc42 architecture description written to conform to ISO/IEC/IEEE 42010, with diagrams at C4 levels:
  an index over the records, the Theory of Operation and the diagrams, with new prose only for the building blocks,
  the runtime scenarios and the guarantee-to-evidence table. It decides nothing.

Where the narrative and the current checkpoint disagree, the checkpoint wins.
