# Forms

Angle brackets are placeholders. For anything not covered, read the nearest precedent: ADR-0054 and ADR-0059 for a new
record, ADR-0060 R2 for a revision, ADR-0024 at `ed3d98d` for a drafted erratum, `0068b55` for dependent amendments.

## A new record

```text
<!-- AUTHORED · 2026-11-11 · DRAFT for the custodian -->
> **Provenance note.** Drafted 2026.11.11 by the assistant at the custodian's request, not recovered. Sources: <the
> discussion, derived documents and records used>. **The custodian settled <n> things**, each marked ⟨K1⟩ to ⟨Kn⟩ where
> it is used: <each one>. Every other choice is the drafter's, marked *(drafter's choice)* where the alternative was
> live. <Records cited> were not re-read for this draft and are taken as <what gave them>.

# ADR-NNNN — <A title that states the decision, not the topic>

**Status:** Proposed · 2026.11.11
**Status note:** <Confirmation: which of C1 to C4 would attach, why, and why not the others, on the drafter's reading.
What exists and what does not: modelled, checked, proved, built.>
**Pending:** none.
**Deployment position:** <Archetype, or an overlay>
**Depends on:** ...
**Relates to:** ...
**Closes:** nothing.
**Carries a debt against:** nothing.

---

## Context
## Decision
### 1. <A clause that states what is decided> ⟨K1⟩
...
### n. Ratification condition
## Options considered
| Option | Disposition |
## Consequences
**Positive** / **Negative**
## Open obligations
---
## History
| Tag | Kind | Change | Source | State |
|---|---|---|---|---|
```

**Header fields**, in this order, only those that apply: Status · Status note · Pending · Ratification phase ·
Deployment position · Scope · Owner · Supersedes · Split from · Amends · Amends in effect · Revises · Narrows ·
Depends on · Depended on by · Companions · Precedent · Relates to · Resolves · Resolves debts of · Closes · Unblocks ·
Blocked on · Blocks · Creates a debt against · Carries scope into · Note.

The Status line holds the class, the date and any confirmation marker only. Relationship fields name records. A status
in one, "(Proposed)", is allowed for a record not yet ratified and goes stale at ratification, so the ratification
sweep picks it up.

**Index row** in `decisions/README.md`:

```text
| [ADR-NNNN](ADR-NNNN.md) | <title> | Proposed (drafted 2026.11.11, after G11) | |
```

## Ratification condition

```markdown
### 7. Ratification condition

- **A module states the properties and its mutations break them**, by ADR-0046's method. At least `P1`, `P2`, with
  `M_X`. **Met for TLC and TLAPS** ⟨R1⟩: `spec/X.tla` (`<16 hex>`), results `spec/X-results-<date>.txt` (`<16 hex>`).
- **The floor carries `F1` to `F3`** (ADR-0067). **Not met: no entry is written.**
- **The reference shows <behaviour>.** **Not met: nothing is built.**
- **A reader who is not the drafter** (ADR-0029 A2). **Not met.**
- **The custodian's reading of every drafter's choice.** **Not met.**
```

## R-revision on a Proposed record

Mark the change at the place it happens, keep what it replaces:

```text
~~and no premise changes~~ ⟨R8⟩ as derived premises
⟨R8⟩ **The row premises change only as the derived premises below say** (R7).
```

Add `**Modelled, checked and proved in TLA+ ⟨R1⟩ (§7); nothing is built.**` to the Status note when that changes.

```text
| R2 | Revision before ratification | **<What changed, in a bold line.>** <Clause by clause.> | <What caused it: a results file, the custodian's instruction> | Drafted 2026.11.11 by the assistant at the custodian's direction, not reviewed |
```

If it touches an item another record relies on, name the knock-ons in the row. A revision of a dependent drafted for
another record uses kind `Revision (dependent on ADR-0054, Proposed)`.

## A pending erratum

Leave the wrong sentence exactly as it is. Below it:

```text
  *Pending ⟨E1⟩, not applied. **The citation and the gate's state.** The bullet above is to read: <the corrected
  text>. <What this was found against.>*
```

History row, appended:

```text
| E1 | Erratum | **<Title.>** <Where>: ~~"<old>"~~ → <new>. No decision text changes. Marked inline and not applied | <Evidence> | **Pending** — drafted 2026.11.02 by the assistant at the custodian's direction, not reviewed |
```

Pending line. New items go first and in bold, existing text stays:

```text
**Pending:** **E1**, drafted 2026.11.02: <what>; marked inline and not applied. <what was there>
```

If the Pending line said `none.`, it becomes `**Pending:** **E1**, drafted ...`, followed by whatever came after
`none.`. The Status line is not touched: no ⟨Bnn⟩ yet.

## A pending amendment

As an erratum, at the clause, `*Pending ⟨A5⟩, not applied. <The new text.>*`, and the condition if it has one.

**A clause inside a table row gets its note below the table**, naming the row, and the row's own text is not edited.
ADR-0045 did this for T-0045-31: `*Pending ⟨A3⟩, not applied. **T-0045-31's residual gains a clause at its end** ...*`.

```text
| A5 | Amendment (dependent) | **<Title.>** <The change.> Marked inline and not applied | ADR-0054 §3 | **Pending** — drafted 2026.10.08 by the assistant at the custodian's direction, not reviewed. Takes force only with ADR-0054's ratification |
```

Pending line: `**A5**, drafted 2026.10.08, dependent on ADR-0054 (Proposed): <what>, marked inline and not applied.`

Kind is `Amendment` when it stands alone, and `Amendment (dependent)` with "Takes force only with" when it rides on
another record. Say what class of thing changes. "No row changes class and no decision text changes" is a claim, make
it only if true.

## Digests

A pinned record's digest moves as soon as a pending row is added. Update the line in `mechanism/corpus-pins.sha256` to
the new digest, and run the drift test from `mechanism/`:
`cargo test -p topak-core --release --test drift`.

A pending note also moves the digest of the clause it sits in, which `spec/specification-graph.json` pins. Read edges
to that clause go stale (eight of them, for a note in ADR-0045 Annex B). Report it and leave it: `build --repin <ids>`
is the review's step.

The first 16 hex of a sha256 cite a file. Compute them, do not copy from another record:
`shasum -a 256 <file> | cut -c1-16`.
