# The reader brief

The fixed template every reader was given. `{SCOPE}`, `{DEPTH}` and `{PUSH}` were filled per reader; `reader-scopes.md` has the thirteen fillings. The readers worked on a copy of the tree at `bbda621` from which `derived/` (but for the 11.10b proposal) and `diagrams/README.md` had been removed.

---

You are one of thirteen readers of a design corpus called TOPAK. You did not write it. You are reading it cold, and
your job is to find where it is wrong, inconsistent, stale or unsupported, and to record exactly what you read.

## Where you work

- Read **only** under `<the blind copy>`. It is a copy of the corpus at commit `bbda621` (2026.11.10).
- Do **not** open `/home/user/TOPAK` or any other copy of the corpus, and do not use the web. Other copies hold
  earlier reviews that you must not see.
- Change nothing under `<the blind copy>`. Write only the two output files named below.
- You may run read-only commands (`grep`, `sed -n`, `wc`, `sha256sum`, `python3 spec/clauses.py <record>`). Do not
  run builds, model checkers, provers or tests.

## What the corpus is, in five lines

- `decisions/` holds architecture decision records (ADR-0001 onward). Each has a status: Accepted (genesis),
  Accepted with confirmation required, Accepted · provisional, or Proposed. A pending amendment is drafted and not
  in force.
- `checkpoints/` holds frozen checkpoints. G11 (2026.10.09) is the state of record.
- `narrative/` is the living explanation (Theory of Operation, glossary). `spec/` holds TLA+ modules, TLC results,
  TLAPS proofs and Lean. `floor/` is Cedar policy, `policies/` is Rego, `mechanism/` is a Rust reference.
- Precedence when two layers disagree: checkpoint, then decisions, then narrative, then evidence. **A disagreement
  between layers is a finding, whichever side is right.**
- The corpus uses four evidence words with distinct meanings and never interchanges them: *checked* (TLC),
  *proved* (TLAPS), *certified* (a second run with checked backends), *proved in Lean*.

## Your scope

{SCOPE}

## What to look for

Report what you can cite. Do not pad, and do not report style.

1. **Contradiction.** Two statements that cannot both hold: within a record, between records, or between a record
   and a module, a policy, the code, an index, a README or the narrative.
2. **Staleness.** A statement that was true and is not: a status, a count, "not yet", "pending", "nothing is built",
   a pointer to a file or section that has moved or says something else.
3. **Unsupported evidence claims.** "Checked", "proved", "certified", "built", "Met" with no artifact behind it, with
   a different artifact, or with an artifact that states something weaker or stronger than the claim.
4. **Model against prose.** A property a record states that its module does not state, or states differently; a
   constant, bound or count that differs between record and module; an abstraction the module makes that the record
   does not acknowledge.
5. **Quotation.** Text given as a quotation that does not match its source.
6. **Dangling or circular reference.** A cited clause, row, finding or file that does not exist; a record that depends
   on something not in force without saying so.
7. **Unclear force.** A place where a reader cannot tell what is in force, what is proposed and what is pending.
8. **Internal gaps.** A ratification condition with no state, a table whose count disagrees with its prose, a list
   that omits a member its siblings have.

{PUSH}

## Depth

{DEPTH}

## Output: two files, then a short message

Write both under `<the output directory>`.

### 1. `<the output directory>/findings.md`

One block per finding, in this exact shape:

```
### {ID}-<n>: <one-line statement>
- Against: <file>:<line> (and <file>:<line> for the other side, where there is one)
- Basis: in force | Proposed | pending | living document | evidence
- Claim: "<the exact words you are disputing>"
- Why wrong: <the conflicting text, quoted with file:line, or the command you ran and its output>
- Fix belongs in: <which file or record would have to change; do not write the fix>
- Severity: High | Medium-High | Medium | Low-Medium | Low
- Confidence: high | medium | low
- Already on the corpus's own lists: <G11 open-list item number, or a row of mechanism/GAPS-AND-ASSUMPTIONS.md, or "no">
```

Number findings from 1. Quote exactly. Every finding needs at least one `file:line` you opened yourself.

### 2. `<the output directory>/ledger.tsv`

Copy `<the output directory>/skeleton.tsv` to `<the output directory>/ledger.tsv` and fill four columns on **every** row. Keep the other columns and
the row order unchanged.

- `verdict`: exactly one of
  - `checked against` (you compared the row with another artifact; name it in `against`),
  - `read only` (you read it and compared it with nothing),
  - `finding` (it has at least one finding; give ids in `finding_ids`; also fill `against` if you compared),
  - `not read`.
- `against`: the artifact(s) you compared with, as paths with a section or line.
- `finding_ids`: comma-separated.
- `note`: optional, one short phrase.

Be honest in the ledger. `not read` is an acceptable verdict and a false `checked against` is not. The ledger will
be sampled and audited by another reader.

### 3. Your final message

Under 200 words: how many findings by severity, how many ledger rows by verdict, and the three findings you think
matter most. Do not paste the files.
