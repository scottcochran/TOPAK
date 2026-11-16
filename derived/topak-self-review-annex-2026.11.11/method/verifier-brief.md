# The verifier brief

The fixed template every verifier was given, with a pack holding each finding and the text at the lines it cites.

---

A reader has reported findings against a design corpus called TOPAK. You did not write the corpus and you did not
find these. Your job is to check each finding against the files and say whether it stands. A finding that does not
survive your check is dropped, so be strict in both directions: do not wave a finding through, and do not drop one
because it is small.

## Where you work

- The findings and the text at the lines they cite are in one file: `<the pack>`. Read it first, in full.
- The corpus is at `<the blind copy>` (commit `bbda621`). Open files there whenever the pack's excerpt is not enough to
  decide: a quotation cut short, a claim about what a file does *not* say, a count, a comparison of two sections.
- Do **not** open `/home/user/TOPAK` or any other copy, and do not use the web. Change nothing. Read-only commands
  only (`grep`, `sed -n`, `wc`, `sha256sum`, `python3 spec/clauses.py`). No builds, model checkers or tests.

## What to check, for each finding

1. **The claim is quoted exactly**, and is at the cited place. A paraphrase offered as a quotation is a correction.
2. **The other side is what the finding says it is**: the conflicting text exists at its cited place and says that,
   or the absence the finding asserts is real (search for it; an absence needs a `grep` that came back empty).
3. **The two really conflict**, read in context. Check the surrounding lines for a qualifier, a History row, a
   status note or a later sentence that reconciles them. Check that the finding has the direction right: which side
   is stale, which is in force.
4. **Counts and commands reproduce.** Recount; rerun the command.
5. **Severity is defensible** on this scale: High (a guarantee, a ratification or a safety claim is wrong or
   unsupported), Medium-High, Medium (two layers disagree on substance), Low-Medium, Low (a stale sentence or count
   with no consequence for a claim).

## Output

Write `<the output directory>/verdicts.tsv`, tab-separated, this header, one row per finding in the pack, in order:

`id	verdict	severity	correction	evidence`

- `verdict`: exactly one of
  - `confirmed` (stands as written),
  - `confirmed with correction` (the defect is real; the statement, a quotation, a line number, the direction or
    the scope needs the change you give in `correction`),
  - `not confirmed` (the texts do not conflict, the claim is not in the file, or the absence is not real; say which
    in `correction`),
  - `duplicate of <id>` (the same defect as an earlier finding in this pack).
- `severity`: the reader's, or yours if you would change it, as `Medium (reader: High)`.
- `correction`: blank for `confirmed`.
- `evidence`: the `file:line` you relied on and, for an absence, the command you ran.

Then end with a message under 120 words: counts by verdict, and the ids of findings you could not decide.
