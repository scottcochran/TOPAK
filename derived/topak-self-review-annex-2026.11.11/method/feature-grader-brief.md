# The grader brief (feature rows)

The brief of the first of five feature-row graders; the others differ only in "Your rows".

---

A self review of the TOPAK corpus is under way at commit `bbda621` (2026.11.10). The current feature list is
`derived/topak-feature-list-2026.11.05.md`, drawn at the tree after `147bc72`. It will be regenerated. Your job is
to check, row by row, whether each feature row in your section is still true **at this tree**, so that no status
is carried forward by copying.

## Where you work

- Read under `/home/user/TOPAK` only. It is at the pinned commit. **Change nothing there.** Read-only commands only
  (`grep`, `sed -n`, `git log`, `git diff --stat 147bc72 bbda621 -- <path>`, `git show`, `wc`). No builds or tests.
- Write only under `<scratch>/graders/FL1`.
- Read the list's lines 1 to 66 first: its basis, its limits and its **status key**. Use that vocabulary exactly.
  *Proved*, *proved in Lean*, *certified* and *checked* are different words and are never interchanged.

## What moved between the list's tree and this one

- ADR-0056 (user scope), ADR-0057 and ADR-0058 (the specification graph; deployment overlays) were drafted,
  Proposed. ADR-0057's R1 put three pending amendments into accepted records: ADR-0033 A18, ADR-0045 A5, ADR-0053 A1.
  So there are now fifteen pending amendments, and not every one depends on ADR-0054 or ADR-0055.
- ADR-0059 to ADR-0068, the command-chain overlay, were drafted, Proposed, **as an overlay and not as part of the
  archetype**. Eight TLA+ modules came with them (`Federation`, `Intent`, `Membership`, `Alone`, `Outstanding`,
  `PlaneClock`, `Peer`, `Release`), each checked by TLC, proved by TLAPS and run through certification on
  2026.11.10. So `spec/` now holds thirty-two proof modules.
- `spec/specification-graph.json`, `spec/specification-graph.py` and `spec/clauses.py` were added; nine diagrams and
  two skills were added; `mechanism/corpus-pins.sha256` was re-pinned.
- No checkpoint was cut and no batch was ratified. G11 is still the state of record.
- Checks run at this tree for this review, which you may cite: `<scratch>/evidence/03-proof-sync.txt` (32 proofs in sync;
  `Workflow` and `Mesh` have no proof and no recorded reason), `<scratch>/evidence/03-lean-sync.txt` (`mechanism/lean` stale;
  `spec/lean` and `floor/lean` in sync), `<scratch>/evidence/04-spec-graph-check.txt`, `<scratch>/evidence/04-inventory-check.txt`,
  `<scratch>/evidence/02-check-refs.txt`, `<scratch>/evidence/gates/` (all five floor gate runs reproduce their committed verdicts),
  `<scratch>/evidence/07-opa-test.txt` (38 of 38).

## Your rows

`derived/topak-feature-list-2026.11.05.md` §1, principle P1 (lines 150 to 324): 124 rows, F1.1 onward, including the new rows under their group headings.

## What to check for each row

1. **The record's standing.** The Status cell leads with it. Open each record the Basis names and read its
   `**Status:**` line and its History rows dated after 2026.11.03.
2. **Evidence words.** Where the cell says Proved, Certified, Checked, Stated or Built, confirm the artifact exists
   at this tree and still says so (the proof-results or results file; the code path). A sample is not enough for
   Proved and Certified: open the file.
3. **Open items.** Where it says `Open (item N)`, read G11 §7 (and the earlier checkpoint if G11 does not restate
   the item) and say whether the tree has since discharged it.
4. **Numbers and names in the feature's first sentence.** Counts of modules, obligations, rows, policies, tests,
   records and amendments; file names; "twelve pending amendments"; "twenty-four proof modules". Recount at this tree.
5. **What the overlay would do to it.** If ADR-0059 to ADR-0068 name this feature's record or clause as something
   they relax, reverse, extend or leave owing (each overlay record has a section on what the archetype's records
   "would owe"), say which record and section, and the verb.

## What to produce

### `<scratch>/graders/FL1/restatus.tsv`

Tab-separated, this header, one row per feature id in your section, in the list's order:

`id	status_at_pin	new_status	new_first_sentence	new_basis	evidence	reason	overlay_touches`

- `status_at_pin`: `same` (every part of the row is still true), `moved` (something changed after the list's
  tree), or `was wrong` (the row was already untrue at the list's own tree).
- `new_status`, `new_first_sentence`, `new_basis`: the replacement text for that cell, in the list's own style, only
  where it must change. Leave blank otherwise.
- `evidence`: `file:line` for what you opened. Every row needs at least one.
- `reason`: a few words; blank for `same`.
- `overlay_touches`: `ADR-00NN §n: relaxes | reverses | extends | owes`, or blank.

### `<scratch>/graders/FL1/notes.md`

Under 300 words: rows you could not check, patterns, and any feature you think the section is missing for records
that existed at the list's tree.

### Your final message

Under 120 words: rows checked, counts by `status_at_pin`, count with `overlay_touches`.
