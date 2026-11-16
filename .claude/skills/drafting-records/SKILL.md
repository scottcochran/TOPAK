---
name: drafting-records
description: "Drafts and revises TOPAK decision records in decisions/: a new Proposed ADR, a revision before ratification, a pending amendment or erratum on an accepted record, and the dependent entries a record owes other records. Keeps who decided what visible, leaves accepted text unedited, marks every ratification-condition line Met or Not met, and sweeps a revision through its own text and its siblings. Use whenever the custodian asks to write, draft, propose, revise, amend, correct or fix an ADR or decision record, to bring a record up to date with a module or result, to record a decision from a discussion, or to fix a wrong citation or count in decisions/, even if the request only says 'fix it'. Not for ratifying (that is ratifying-records), and not for derived documents."
---

# Drafting Records

## Contents

- [When to Use](#when-to-use)
- [When NOT to Use](#when-not-to-use)
- [Which act is this](#which-act-is-this)
- [The workflow](#the-workflow)
- [Who decided what](#who-decided-what)
- [Quick reference](#quick-reference)
- [Rationalizations to reject](#rationalizations-to-reject)
- [References](#references)

How a TOPAK record comes to exist and changes before it is settled, distilled from ADR-0053 to ADR-0068 and the
findings against them.

**Core principle: a record has to tell a later reader who decided each thing, what has been checked, and what has
not.** Its text will be read long after this session, by a reviewer who was not in it, and once ratified it changes
only by typed History row. A sentence that overstates what was settled, or still says what a later revision overtook,
gets pinned along with the rest. Ten records drafted in one day were then revised against their modules, and drawing
them still found eighteen inconsistencies. Most were the same few mistakes, listed in
[recurring-defects.md](references/recurring-defects.md).

## When to Use

- A new record, from a discussion, a derived proposal, or the custodian's decisions
- Revising a Proposed record, including bringing it in line with a module or result
- Drafting an amendment or erratum on an accepted record, left pending
- Drafting the dependent entries a record owes others
- Correcting a wrong citation, count or quotation anywhere in `decisions/`

## When NOT to Use

- Ratifying anything, or applying a pending row: `ratifying-records`
- A derived document. Those are dated, frozen, and superseded by new ones, and carry no History
- Theorem or module work, except for citing its result

## Which act is this

Check the record's **Status** line first. It decides what you may do, and "fix it" does not change that.

| Record's state | What is wrong or wanted | The act | Result |
|---|---|---|---|
| Does not exist | A new decision | New record | `Proposed`, next free number |
| Proposed | Anything | **R-revision** in place | Struck text kept, ⟨Rn⟩ marks, a `Revision before ratification` row |
| Accepted | A wrong fact, citation or count; no decision text changes | **Erratum**, pending | Text unchanged, note below it, a `Pending` row |
| Accepted | What the record decides or claims | **Amendment**, pending | Text unchanged, note at the clause, a `Pending` row |
| Accepted | Another record's ratification will change it | **Dependent amendment**, pending | As above, "Takes force only with ..." |
| Proposed | Another record needs a change in it | R-revision, kind `Revision (dependent on ...)` | In place |
| Pending on an accepted record | The draft needs changing | `Revision (to pending An)` row | Edit the pending note |

**An accepted record's own text is not edited by a draft**, however obviously wrong it is. The correction sits beside
it, marked, until a batch applies it. That is what makes the digest pin mean anything.

## The workflow

Work in a worktree on its own branch. Nothing here is committed unless the custodian asks.

1. **Choose the act**, from the table above.

2. **Find the numbers.** `scripts/record_lint.py --next` prints the next free ADR and T-0045 numbers. Then check open
   branches and worktrees, since records have been renumbered when two were in flight:
   `git branch -a --list '*adr*'`, `git worktree list`. A tag is the next unused one in that record's History,
   pending rows included.

3. **Read what you cite, and say what you did not.** Quote a clause from its record, not from memory or a derived
   summary. The provenance note names the sources, and names each cited record you did not re-read and what you took
   instead, as ADR-0059 to 0068 do. Check whether a clause you rely on is in force: a pending amendment is not, and
   the Pending line tells you.

4. **Separate who decided what**, as [below](#who-decided-what).

5. **Write it** in the forms of [forms.md](references/forms.md).

6. **Write the Ratification condition as a checklist of what would have to be true**, with one item for each kind of
   artifact the decision names: a module, floor entries, the reference, dependent entries, a reader. Every item says
   **Met** with its evidence and digest, or **Not met**, because an unmarked item reads as met. See
   [forms.md](references/forms.md#ratification-condition).

7. **Draft the dependent entries**, or list them as owed. Each accepted record it changes gets a pending amendment,
   each Proposed record an R-revision. A pinned record's drafted entry moves its pin, so re-pin. The premise routes
   are renewed at ratification, not at drafting.

8. **Sweep.** A revision changes a claim, and the old claim is usually stated in more than one place. See
   [recurring-defects.md](references/recurring-defects.md#the-sweep): the record's own status note, conditions,
   consequences and counts, then every sibling and module header that cites it.

9. **Register and check.** A new record gets an index row in `decisions/README.md`. Run `scripts/record_lint.py` on
   each record you touched and `python3 tools/check-refs.py`. For a pinned record, the drift test from `mechanism/`.
   Run `python3 spec/specification-graph.py check` before and after if the graph covers the record, and compare, since
   it does not pass today.

10. **Report**: what you drafted, which choices are the custodian's to make, what you did not read, and what you
    found but did not change. Leave findings about other records as findings.

## Who decided what

The corpus's reader needs to tell these apart at the point of use.

| Whose | Mark | Example |
|---|---|---|
| The custodian said it in the discussion | ⟨K1⟩, ⟨K2⟩, declared in the provenance note | "the workflow is a DAG ⟨K1⟩" |
| The custodian answered a numbered question from a proposal | ⟨Q1⟩, or ⟨1⟩ for a proposal's item, declared likewise | "⟨Q11⟩" |
| The drafter picked, and an alternative was live | *(drafter's choice)*, with the alternative in Options considered | "a join rule *(drafter's choice)*" |
| The drafter recommends among options left open | *(drafter's recommendation)*, the options set out | ADR-0060 R2 |

Mark only what was said. A provenance note claiming every choice is marked needs the marks to exist. If there are
none, either add them or say so plainly. The confirmation criteria in the Status note are the drafter's reading ("on
the drafter's reading"), since C1 to C4 are decided at ratification.

**ADR-0057 §2** asks records drafted after it to give each clause four parts (Goal, Givens, Guarantees, Discharge).
ADR-0057 is Proposed and no later record has done so. Do not adopt it on your own. Raise it if the record is one where
it would matter.

## Quick reference

| Task | Form |
|---|---|
| Numbers | `scripts/record_lint.py --next` |
| Lint | `scripts/record_lint.py decisions/ADR-nnnn.md ...` |
| Status of a new record | `**Status:** Proposed · 2026.11.11`, no revision prose on that line |
| Header comment | `<!-- AUTHORED · 2026-11-11 · DRAFT for the custodian -->` |
| Revise in place | `~~old~~ *new* ⟨R2⟩` or `⟨R2⟩ new sentence` |
| Pending erratum or amendment | `*Pending ⟨E1⟩, not applied. ...*` |
| Digest citation | `` `spec/Intent.tla` (`0c90ea5004c4f127`) ``, first 16 hex |
| Dates | `2026.11.11` |
| The word for a TLA+ result | Proved (TLAPS), checked (TLC), proved in Lean; each only of what ran |

## Rationalizations to reject

| Rationalization | Reality |
|---|---|
| "It's an obvious typo in an accepted record; I'll just fix it." | Accepted text changes only by a typed row. The pin is on those bytes. Draft the erratum. |
| "They said fix it, so they've authorized the edit." | They asked for the correction. How it lands is set by the record's status. Say which act you took and why. |
| "The custodian obviously wants this, so ⟨K3⟩." | ⟨K⟩ means they said it. Otherwise it is the drafter's choice, and the record should say so. |
| "The floor item is plainly not done; no need to say." | Unmarked reads as met. Write "Not met". |
| "I updated the section that changed." | The status note, the condition, the consequences and a count elsewhere usually state it too. Sweep. |
| "ADR-X says this" (from a summary) | Read ADR-X. A paraphrase in quotation marks is a misquotation, and paraphrases drift. |
| "That amendment covers it." | Check whether it is pending. A pending amendment is not in force. |
| "The module proves it." | At which constants? A record's numbers and a module's are not automatically the same. |
| "I'll tidy the other records I noticed." | Report them. Each is its own act with its own row. |
| "I'll mark the condition Met since it's nearly there." | That is a statement a reviewer will rely on. Write what is true. |
| "I'll drop the old sentence; the History row explains it." | Struck text stays so the record shows what changed at the place it changed. |

## References

- [forms.md](references/forms.md): the exact form of every part of a record. Read before step 5.
- [recurring-defects.md](references/recurring-defects.md): the mistakes that recur, and the sweep. Read before step 8.
- `scripts/record_lint.py`: next numbers, and the mechanical parts of the above.
- `decisions/ADR-0029.md`, status classes and criteria. `process/NORMALIZATION-LOG-2026.09.15.md` §2, the header schema.
