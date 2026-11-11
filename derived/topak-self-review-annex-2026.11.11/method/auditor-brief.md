# The auditor brief

How a sample of rows the readers marked "read only" was read a second time.

---

Readers of a design corpus kept a ledger: for each clause or section they read, whether they compared it with
another artifact, found something, or **only read it**. You are auditing a sample of the "read only" rows. For each
row in your sample you read the same text cold, compare it with whatever it cites, and report any defect.

## Where you work

- The corpus is at `` (commit `bbda621`). Read only there. Do not open `/home/user/TOPAK` or any other
  copy, and do not use the web. Change nothing. Read-only commands only; no builds, model checkers or tests.
- Your sample is `<scratch>/audit/sample.tsv`: `reader`, `record`, `row`, `kind`, `heading`. For a `clause` row, the
  record is `decisions/<record>.md` and the row is the clause (`§3`, `Decision`, `Annex A`, or a heading). For a
  `section` row the record is a file path and the row is a heading in it. Other kinds name themselves.

## What to do for each row

1. Read the whole clause or section.
2. Open at least one thing it cites or depends on (a record, a module, a policy, a results file, the code, an
   index) and compare.
3. Report a finding only for one of these: two statements that cannot both hold; a statement that was true and is
   not (a status, a count, "not yet", "pending"); a claim of "checked", "proved", "built" or "Met" with no artifact
   or a different one; a property or number that differs between a record and its module; a quotation that does not
   match its source; a reference to something that does not exist; a place where a reader cannot tell what is in
   force. Do not report style.

## Output

Write `<scratch>/audit/audit.tsv` (through the shell if the Write tool refuses), tab-separated, this header, one row per
sample row, in order:

`reader	record	row	compared_with	result	finding	evidence`

- `compared_with`: what you opened to compare, as `file:line` or `file §n`.
- `result`: `nothing found` or `finding`.
- `finding`: one sentence, with the exact words disputed in quotation marks; blank if nothing found.
- `evidence`: the `file:line` on each side; blank if nothing found.

Then end with a message under 120 words: rows audited, rows with a finding, and which.
