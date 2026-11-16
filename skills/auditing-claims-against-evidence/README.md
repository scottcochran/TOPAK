# auditing-claims-against-evidence

Reads a technical document as a set of checkable statements and compares each with the thing it is about.

## What it does

1. **Gets an independent reader**, who has not seen the drafter's conclusions.
2. **Lists the claims**, including those in tables, status notes and asides.
3. **Checks each by its class**: numbers, digests, results, universal claims, status, citations, quotations, scope.
4. **Puts things side by side**, since most inconsistencies appear only when two things are read together.
5. **Re-checks every finding** before reporting it.
6. **Reports a verdict per claim**, and what was not checked.

## Contents

All paths are relative to `skills/auditing-claims-against-evidence/`:

- `SKILL.md`: the workflow, verdicts, the report form, rationalizations to reject
- `references/claim-classes.md`: how to check each kind of claim
- `references/this-repository.md`: where the evidence is in TOPAK; the only TOPAK-specific file
- `assets/reader-brief.md`: the brief for a fresh reader
- `scripts/check_citations.py`: digest and path citations

## Why these rules

From TOPAK's critical reviews, its errata, and `derived/topak-command-chain-diagram-findings-2026.11.10.md`. An audit by
an agent does not meet a requirement for a reader who is not the drafter.

## Status

A draft.
