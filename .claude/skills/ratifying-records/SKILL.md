---
name: ratifying-records
description: "Ratifies TOPAK decision records as a numbered Batch under ADR-0029 §2: checks each ratification condition, separates what the assistant may run from what only the genesis custodian can decide, applies status lines, Pending notes, History rows, inline amendments and errata and dependent entries, re-pins, renews the premise routes in the right order, and handles the diagram and prose knock-ons. Use whenever the custodian says to ratify, accept or apply a record, amendment or erratum, asks for the next Batch, asks whether a record is ready to ratify or what ratifying it would touch, or asks to apply a pending History row, even if the word Batch is not used. Not for drafting or revising a record that stays Proposed, and not for cutting a checkpoint."
---

# Ratifying Records

## Contents

- [When to Use](#when-to-use)
- [When NOT to Use](#when-not-to-use)
- [The workflow](#the-workflow)
- [Who decides what](#who-decides-what)
- [When a condition is not met](#when-a-condition-is-not-met)
- [Quick reference](#quick-reference)
- [Rationalizations to reject](#rationalizations-to-reject)
- [References](#references)

The procedure by which a TOPAK record, amendment or erratum becomes accepted text, distilled from Batches 34 and 36 to
39.

**Core principle: ratification is the custodian's act, and the record's face has to say exactly what was done, by
whom, and what was not.** The assistant can run a gate, write a row and move a pin. It cannot supply a decision, and
a record that says "the custodian read this" when no one did is worse than a record left Proposed, because accepted
text changes only by History row from then on and the false sentence is pinned with the rest.

## When to Use

- The custodian says to ratify, accept or apply a record, an amendment or an erratum
- Applying a History row whose state is **Pending**
- Working out whether a record is ready, and what its ratification would touch, before deciding
- Writing the dependent entries another record's ratification owes
- Checking a batch already applied (`scripts/batch_lint.py`)

## When NOT to Use

- Drafting a new record, or revising one that stays Proposed. An R-revision made as step 3 below is the exception
- Drafting an amendment or erratum to be left Pending
- Cutting a checkpoint or a reference manifest. What a batch owes the next cut is listed in step 11 and left there
- Confirmation promotions after bootstrap (ADR-0029 §6), which run under ADR-0024 and have no procedure here

## The workflow

Work in a worktree on branch `batch-<nn>`. In a worktree the untracked `tools/` binaries are absent, so use the main
checkout's `tools/...` for anything that needs them.

1. **Number the batch and scope it.** `scripts/batch_lint.py --next` prints the number. Take the items the custodian
   named, then find what has to travel with them, because a dependent amendment left behind reads as in force on one
   record and pending on another:
   - `grep -n 'Takes force only with\|dependent on ADR-<nnnn>' decisions/*.md`
   - the item's own dependent-entries section, and its **Depends on** line for anything still Proposed
   - other Proposed records its condition names ("ADR-0058 is ratified")
   - circular conditions: a record whose condition needs another record, whose own condition needs this one, as
     ADR-0059 §9 and ADR-0067 §7 do. Those can only be ratified in one batch, or after the custodian changes one

   A record without decision text cannot be ratified (ADR-0029 §2).

2. **Read every ratification condition and classify each line**, as [Who decides what](#who-decides-what) does. Run
   what is yours and keep the output. Results must regenerate byte for byte and sync scripts must exit 0, unless a
   record says otherwise about that file.

3. **Reconcile stale text before ratifying.** Read a Proposed record through for sentences its later revisions
   overtook, and bring them in line as a last revision on the Proposed record (struck text kept, ⟨Rn⟩ markers, an Rn
   History row). After ratification the same fix is an amendment with its own batch. ADR-0053 needed R8 for this; it
   had said "no premise changes" after R7 changed them. Accepted records take no R-revision.

4. **Ask the custodian, once, for everything still open**, with AskUserQuestion when it is available. Use a preview
   for anything to be read side by side. A condition worded "the custodian reads" needs something to read: build a
   reading sheet in the scratchpad (B37: each listed step, opaque names resolved by hash). If the session cannot ask,
   stop here and hand back the list of questions with nothing applied.

5. **Apply the lead item or record** in the exact forms of [record-forms.md](references/record-forms.md): status line,
   status note, Pending line, inline text, condition marked "Met at ratification", History rows, and the
   `decisions/README.md` index row for a whole record.

6. **Apply the dependent entries** exactly as the lead's dependent-entries section words them. Each changed record
   gets ⟨Bnn⟩ on its status line and a Bnn row.

7. **Re-pin, and renew the premise routes if owed.** The order matters and is in
   [knock-ons.md](references/knock-ons.md): names into rows, pin, generate last, drift again.

8. **Check the specification graph** before and after, and review only the edges this batch moved
   ([knock-ons.md](references/knock-ons.md)).

9. **Sweep the prose** for the item still described as Proposed or pending.

10. **Regenerate the diagram family** and keep only what this batch caused. Generators assert corpus facts, so a
    batch can break one, and that is a finding to fix rather than a failure to route around.

11. **Lint and report.** Run `scripts/batch_lint.py <nn>` and the drift test. Report what was run, what the custodian
    decided, what changed, and what is owed at the next cut: the checkpoint's §8 sentence, `narrative/glossary.md`, the
    manifests. The commit and any tag are the custodian's. The usual subject is `Batch <nn> is ratified: ADR-0046 A3,
    ADR-0045 A4`.

## Who decides what

| Line in the condition, or question | Who | How it appears on the record |
|---|---|---|
| Results regenerate, sync scripts exit 0, replays MATCH, an external fact checked through an API | Assistant, at the custodian's direction | "(1) by the assistant"; say what was run and on whose machine |
| "The custodian reads / chooses / confirms" | Custodian only | "(2) by the custodian's reading, in session" |
| Whether to ratify at all, and what goes in the batch | Custodian only | Source cell: "Custodian's instruction, <date>" |
| Every *(drafter's choice)* | Custodian. Ratifying adopts them, so they must be put to the custodian, and the provenance note says what was settled | Provenance note |
| Which of C1 to C4 attach | Custodian. The drafter's reading is advice. The bootstrap set, ADR-0024 to 0027, cannot carry the marker (ADR-0029 §4) | Status line, status note, Bnn row: "the custodian's decision" |
| Provisional status | Custodian only | See below |
| "A reader who is not the drafter" | A person who did not draft it. A subagent or another model session does not satisfy this unless the custodian rules that it does | Otherwise: **Not reviewed by a reader other than the drafter** (ADR-0029 A2.5) |

An inference is not a decision. If the custodian said "ratify A3", that settles A3, and does not settle C4 on A3.

## When a condition is not met

Say so plainly and offer the choices. Which is taken is the custodian's:

1. **Build what is missing**, then ratify.
2. **Leave it Proposed.** ADR-0029 §2: "a record may remain Proposed indefinitely".
3. **Amend the condition** by an R-revision and ratify. Batch 34 did this.
4. **Ratify provisional** (ADR-0029 §3, A4): in force, subject to redesign, confirmation-required whatever §4 says of
   its content, and saying on its face what it lacked.

Do not mark a line met because it is nearly met, or because the batch is otherwise ready.

## Quick reference

| Task | Command or form |
|---|---|
| Next batch number | `scripts/batch_lint.py --next` |
| Check a batch | `scripts/batch_lint.py <nn>` |
| Drift test | `cargo test -p topak-core --release --test drift`, from `mechanism/` |
| Premise routes | `./premise-routes.sh > premise-routes-results-<date>[b].txt`, from `spec/`; never overwrite one |
| Graph | `python3 spec/specification-graph.py check`; `build --repin <ids>`, never `--repin-all` |
| Dates | `2026.11.03`, always the date the custodian ratified |
| Erratum applied | `~~old~~ *new* ⟨En⟩ ⟨Bnn⟩`, pending note removed |
| Amendment applied | `**Title** ⟨An⟩ ⟨Bnn⟩.`, then `**Met at ratification** ⟨Bnn⟩:` after its condition |
| Every lead row ends | `**Not reviewed by a reader other than the drafter** (ADR-0029 A2.5)` |

## Rationalizations to reject

| Rationalization | Reality |
|---|---|
| "They said ratify, so the drafter's choices and C-criteria are settled." | Those are separate decisions. Ask. Batch 36's custodian settled four things by name, and the record lists them. |
| "The criterion plainly applies, so I'll write it in." | The drafter's reading is advice. Write it after the custodian decides it, and say so on the row. |
| "An agent read it independently, so A2.5 is met." | The sentence is about a reader who is not the drafter, and it is what a bootstrap reviewer will rely on. Keep it. |
| "The condition is almost met; the last line is only the reference." | "Almost" is the provisional status, and that is the custodian's to choose. |
| "I'll generate the premise routes now and fix the rows after." | The results file prints ADR-0045's digest. Editing the row afterwards makes it stale on arrival. |
| "`--repin-all` clears the stale edges." | It erases the evidence of what is actually stale. Items 56 and 103 are named by those edges. |
| "Regeneration changed four other diagrams too; commit them." | Keep what this batch caused, restore the rest, and say which in the Amended note. |
| "I'll tidy this other sentence in the accepted record while it is open." | Accepted text changes only by a typed History row. Note it for a later erratum. |
| "The old results file is out of date, so I'll update it." | Results files are frozen evidence. A renewal is a new file with a new name. |
| "It's only an erratum; it needs no row." | Batches 26 and 37 wrote none and Batch 38, the latest, did. Write the row. |

## References

- [record-forms.md](references/record-forms.md): the exact form of every line a batch writes, with real examples.
  Read before step 5.
- [knock-ons.md](references/knock-ons.md): pins, premise routes, the graph, the prose sweep, diagrams, and what must
  not be touched. Read before step 7.
- `scripts/batch_lint.py`: next number, and a mechanical check of an applied batch. It sees form only: it cannot tell
  whether a decision was really made.
- `decisions/ADR-0029.md`: the governing record. §2 to §4 and A2, A4.
