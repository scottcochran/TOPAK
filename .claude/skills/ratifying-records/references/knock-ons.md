# Knock-ons

What a batch moves besides its records, in the order to do it.

## Pins and the premise routes

`mechanism/corpus-pins.sha256` pins some records and modules, and not others: ADR-0045 and ADR-0024 are pinned,
ADR-0046 is not. Re-pin exactly the changed files that have a line there. A pin is the record that the reference was
reviewed against the change, so look at what moved before replacing the line.

`spec/premise-routes.sh` prints the digests of five files in its Sources line: `spec/theorem-premise-binding.json`,
`spec/theorem-premise-binding.md`, `spec/inventory.py`, `spec/premise-routes.sh` and `decisions/ADR-0045.md`. If a
batch moves any of them, the routes are renewed. ADR-0045 is the usual one.

The results file prints ADR-0045's digest, and ADR-0045's Bnn row names the results file. That circle is why the order
is fixed:

1. Choose the file name: `premise-routes-results-<date>.txt`, or with `b`, `c` if that date's file exists. A results
   file is never overwritten.
2. Write that name into every Bnn row that cites it (ADR-0045 and the lead record), and finish every other edit to
   ADR-0045.
3. Re-pin, and run the drift test from `mechanism/`: `cargo test -p topak-core --release --test drift`.
4. Generate last, from `spec/`: `./premise-routes.sh > premise-routes-results-<name>.txt`. It exits non-zero if the
   overlay is not well formed.
5. Run the drift test again.

Any later edit to ADR-0045 repeats 3 to 5 and needs a new results file. Check the file's Sources line against
`shasum -a 256 decisions/ADR-0045.md`; `scripts/batch_lint.py` does this too.

In zsh, never name a loop variable `path`: it clobbers `PATH`.

## The specification graph

`spec/specification-graph.py` postdates Batch 39, so no batch has run with it yet. ADR-0057 is Proposed, and until it
is ratified the graph is a check and not a gate. Its `check` does not pass today, for reasons that predate any batch
(stale edges including items 56 and 103, and the sync scripts disagreeing), so a failing exit status tells you
nothing.

1. Run `python3 spec/specification-graph.py check` before the batch and keep the output.
2. Run it after, and compare. Only differences this batch caused are yours.
3. Read each edge this batch made stale, then `build --repin <ids>` for those ids. Never `--repin-all`: the stale
   edges are the evidence of what has not been followed, and that command erases them.

On ratifying ADR-0057 itself, read its §14 and dependent entries: `drift.rs` moves to clause pins (ADR-0033 A18), and
the premise routes owe a renewal.

## The prose sweep

Search for the item still described as unratified:

```text
grep -rn 'ADR-<nnnn>[^|]*\(Proposed\|pending\)\|<tag>, pending' \
  README.md REVIEWERS_GUIDE_README.md ADOPTERS_GUIDE_README.md \
  spec/*.md spec/lean/README.md floor/README.md floor/lean/README.md \
  mechanism/GAPS-AND-ASSUMPTIONS.md mechanism/lean/README.md diagrams/README.md
```

Past batches changed lines like `(ADR-0053, Proposed)` to `(ADR-0053, ratified in Batch 36)`, and `to be recorded
... by ADR-0046 A2, pending` to `recorded ... by ADR-0046 A2, Batch 37`. Where a document's statement was overtaken
by the ratification, as `spec/proof-certification.md` was by Batch 39, update the sentence with the date.

On ratification of ADR-0054, ADR-0055, or exit from provisional for ADR-0050 or ADR-0052, the adopter's guide carries
⟨Proposed⟩ and ⟨provisional⟩ marks to strip, and its §3.3, §3.9 to §3.10, §4.10 to §4.11, §5.4 to §5.5, §7.5 and §7.10
to re-read.

## Diagrams

Use the `generating-corpus-diagrams` method and regenerate the family. Then:

- A generator that fails has found a corpus fact the batch changed. G1 asserted 36 Annex A rows, and G3 parsed every
  `| ` line of the binding as a 7-cell row. Fix the generator.
- Keep what this batch caused. Restore what it did not, and report it as drift: Batch 37 left H7 as drawn at Batch 36.
- Add an `**Amended <date>** for Batch <nn> (...)` note to `diagrams/README.md`, naming the diagrams and what was left
  and why.
- If nothing moves, as in Batches 38 and 39, nothing is edited.

## What must not be touched

| File | Why |
|---|---|
| A results file already written | Frozen evidence. A renewal is a new file |
| A script whose digest a results file prints | Change it only if that results file is renewed in this batch |
| `derived/`, `checkpoints/`, `process/` | Frozen. Later documents supersede them |
| An accepted record outside the batch | It changes only by a typed History row |
| Manifests, the checkpoint's §8, `narrative/glossary.md` | Owed at the next cut |
| Git tags | The custodian's |
