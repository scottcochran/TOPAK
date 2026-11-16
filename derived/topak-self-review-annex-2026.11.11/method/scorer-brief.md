# The scorer brief

How the readers' findings were matched against the known open defects they had not been shown.

---

A review of a design corpus used two groups that did not see each other's work. **Graders** gathered defects that
earlier documents had already reported and confirmed which are still open in the tree. **Readers** read the tree
cold, without those documents, and reported findings. Your job is to say, for each known open defect (a "seed"),
whether any reader's finding is the same defect. You judge identity only. You do not judge whether a defect is real.

## Inputs (read both in full; change nothing)

- `<scratch>/score/seeds.tsv`: one seed per row: `seed_id`, `cluster`, `source`, `statement`, `against`, `evidence`.
- `<scratch>/score/findings.tsv`: every reader finding that survived verification: `id`, `reader`, `severity`, `title`,
  `against`, `claim`.

You may open files of the corpus under `` to settle a doubtful match (for example, to see whether two line
references are the same sentence). Do not open any other copy. Read-only commands only.

## The rule

A finding **matches** a seed when it reports the same defect: the same sentence, cell, count, omission or
disagreement, in the same file or record. It need not use the same words, cite the same line, or give the same
severity. A finding that reports a wider defect of which the seed is one named instance matches. A finding about
the same file but a different sentence does not. A finding about the same topic in a different file matches only
if the seed's own statement covers that file.

Use three values:

- `found`: at least one finding matches. Give the ids.
- `found in part`: a finding reports part of the seed (one of several instances the seed lists), or the same defect
  in a neighbouring place without naming this one. Give the ids and say which part.
- `not found`: no finding matches.

Be strict. When in doubt between `found in part` and `not found`, open the files.

## Output

Write `<scratch>/score/scored.tsv` (through the shell if the Write tool refuses), tab-separated, this header, one row per
seed in the order given:

`seed_id	cluster	result	finding_ids	note`

Then end with a message under 150 words: counts by result, and counts by cluster.
