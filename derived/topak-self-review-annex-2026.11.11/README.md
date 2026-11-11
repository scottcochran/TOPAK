# TOPAK — Annex to the self review of 2026.11.11

**2026.11.11** · derived · working papers, not a record · basis: the tree at commit `bbda621` (2026.11.10) · prepared by
the assistant at the custodian's request

The working papers behind five documents in `derived/`, written together: `topak-critical-review-2026.11.11.md`,
`topak-open-findings-register-2026.11.11.md`, `topak-feature-list-2026.11.11.md`,
`topak-residual-risk-statement-2026.11.11.md` and `topak-gaps-prioritization-2026.11.11.md`. Each of those cites this
directory for what would not fit on its page. Nothing here is ratified, nothing here is a decision, and every
reader, verifier, grader, scorer and auditor named below is a fresh context of the same model lineage that drafted
the corpus. This is not the review ADR-0029 A2 asks for.

Like every derived document, this directory is frozen: it is not revised, and a later review writes its own.

## What is here

| Path | Rows or files | What it is |
|---|---|---|
| `findings/` | 14 files, 493 findings | Every finding as its reader wrote it, one file per reader (A to K2, and L for the lead), each followed by the verdict, correction and evidence of a verifier that did not find it. 485 stand |
| `findings.tsv` | 493 | One row per finding: reader's and final severity, verdict, basis, title, what it is against, where the fix belongs |
| `ledger.tsv` | 1231 | The coverage ledger: one row per clause, pending amendment, open-obligations section, status header and trusted-base or declaration row a reader was given, with what the reader did (checked against an artifact, read only, finding) |
| `register.tsv` | 507 | The register's Parts I and II in full: every earlier finding, suggested entry, open obligation and pending amendment, with its status at the pin and the evidence for that status |
| `feature-rows-rechecked.tsv` | 648 | The 11.05 feature list's rows, each with its status re-checked at the pin and what ADR-0056 to ADR-0068 would do to it |
| `feature-rows-new.tsv` | 356 | The feature rows drawn for ADR-0056 to ADR-0068, in full; the feature list shortens some cells |
| `seeds-scored.tsv` | 100 | The known open defects the readers were not shown, whether each was in a file the readers had, and whether a reader found it again |
| `audit-sample.tsv`, `audit.tsv` | 14 | The sample of "read only" ledger rows read a second time, what the second reading found, and the lead's check of each finding |
| `method/` | 8 files | The briefs as given: reader, verifier, grader, feature grader, feature drawer, scorer, auditor, and the thirteen readers' scopes |
| `runs/` | 34 files | The output of each command the review ran, numbered in the order of the review's §2. Scratch paths are replaced by `<scratch>` and build noise is dropped; nothing else is edited |

## Reading it

- Paths inside these files are relative to the repository root at `bbda621`. Line numbers are that commit's.
- A path a finding names as absent from the tree is written without backticks, so that `tools/check-refs.py` does
  not read it as a citation.
- A verifier's verdict is one of *confirmed*, *confirmed with correction*, *not confirmed* and *duplicate*. A
  correction replaces what it corrects: where a finding and its correction differ, the correction is what stands.
- The readers worked on a copy of the tree with `derived/` removed (but for the 11.10b proposal) and
  `diagrams/README.md` removed, so that they could not see earlier findings. The graders, the scorer's seeds and the
  lead saw everything.

## What is not here

The transcripts of the readers, verifiers and graders; the two copies of the tree they worked on; the build
outputs of the reference and of the policy tools. All were in a scratch directory that does not outlive the
session. The `runs/` files and the briefs in `method/` are what a rerun needs.
