---
name: cutting-manifests
description: "Cuts and verifies TOPAK digest manifests: a reference manifest (SHA256SUMS-REF-<date>) over mechanism/ and policies/ at a commit, and a Genesis Checkpoint manifest (SHA256SUMS-G<n>) over the corpus, with the pointer edits, the two-commit sequence, the index.tsv row, and the numbers an ADR-0033 addendum cites. Use whenever the custodian asks to cut, recut or verify a manifest, to cut a checkpoint or G-number, to measure the reference, to add a row to manifests/index.tsv, to get the digest and entry delta for an addendum, or to find out why a manifest stopped verifying. Not for ratifying records (ratifying-records) and not for drafting an addendum's decision text (drafting-records)."
---

# Cutting Manifests

## Contents

- [When to Use](#when-to-use)
- [When NOT to Use](#when-not-to-use)
- [Which manifest](#which-manifest)
- [A reference manifest](#a-reference-manifest)
- [A checkpoint manifest](#a-checkpoint-manifest)
- [Reading a verification](#reading-a-verification)
- [Quick reference](#quick-reference)
- [Rationalizations to reject](#rationalizations-to-reject)
- [References](#references)

How TOPAK measures a tree and records that it did, distilled from eighteen reference manifests and the checkpoints G1
to G11.

**Core principle: a manifest is a statement about one tree, and it is only worth what a later check can confirm.** So
it has to measure exactly the tree it names. Two tools measure two different things: a reference manifest measures a
commit, and a checkpoint manifest measures the working tree, including anything untracked that nobody meant to include.
Most of what goes wrong here is one of those two facts being forgotten.

## When to Use

- Cutting a reference manifest after code lands
- Cutting a checkpoint manifest, or recutting after a late edit
- Adding or checking a row of `manifests/index.tsv`
- Producing the digest and entry delta an ADR-0033 addendum cites
- Explaining why a manifest fails today

## When NOT to Use

- Writing the checkpoint's nine sections or the addendum's text beyond the numbers: the facts come from the records.
  An addendum is a record change; `drafting-records` has its forms
- Ratifying what a manifest supports
- Git tags, which are the custodian's

## Which manifest

| Kind | Name | Measures | Tool | Input |
|---|---|---|---|---|
| Reference | `SHA256SUMS-REF-<yyyy.mm.dd>[b…]` | `mechanism/`, `policies/` | `scripts/cut_ref_manifest.sh` | A **commit** |
| Checkpoint | `SHA256SUMS-G<n>` | The corpus minus `manifests/EXCLUDE` | `tools/cut-manifest.sh` | The **working tree**, tracked and untracked |
| Rehearsal | `SHA256SUMS-SLM-<date>` | The `slm/` tree ADR-0035 §8 cites | By hand; read how the last was cut | |

`tools/cut-manifest.sh` excludes `mechanism/` and `policies/`, so it cannot produce a reference manifest. A checkpoint
measures those trees through the reference manifests, so **any reference manifest the checkpoint relies on is cut
first**.

## A reference manifest

The code lands in commit X. The manifest, the addendum and the record's "Met" mark land in X+1, citing X. That order
exists because the addendum moves ADR-0033's digest and with it the pin file, which is under `mechanism/`, so a manifest
of X+1 could never name itself.

1. **Cut it.** `scripts/cut_ref_manifest.sh SHA256SUMS-REF-<date>[suffix] <X> <cut-date>`. It reads the commit, never
   the working tree, so an uncommitted edit or stray file cannot enter it. A date already used takes the next letter,
   `b`, `c`, because manifests are never overwritten.
2. **Add its row** to `manifests/index.tsv`, using the row the script printed, with the note filled in: which addendum
   and what it measures.
3. **Give the addendum its numbers.** The script prints the first 16 hex of the manifest's digest and the delta from
   the previous reference manifest. The citation form is
   ``manifest `SHA256SUMS-REF-2026.10.08` (116 entries: A15's 90, twenty-six added, none removed, nineteen changed,
   none under `policies/`) · digest `9357abd49333459a` ``. That is only part of the addendum's **Artifacts** line. Also
   give the floor and schema digests of the linked stage, the values and bundle revision or "unchanged", the pin-file
   delta, the test count from a real run, and whether trace validation was rerun. A16's Artifacts line is the model.
4. **Verify.** `tools/verify-manifest.sh <name> <X>`, expecting every entry OK.
5. **Re-pin** what the addendum moved, and run the drift test from `mechanism/`.

Addendum wording says what no longer verifies at X+1 and why. A16 said "113 of 116 at the commit that carries the
addendum and the pin file". Record that rather than leaving it to be rediscovered.

## A checkpoint manifest

Two commits. **The cut**: the checkpoint, its pointers and the manifest. **The narrative commit after it**: the Theory
of Operation revision, glossary, architecture description, reviewer's guide, and the index row, which can name the cut's
commit only once that commit exists.

1. **Everything else first.** Reference manifests, the checkpoint document, the pointer edits and any `manifests/EXCLUDE`
   change. See [g-cut.md](references/g-cut.md) for what is touched.
2. **Run `scripts/precut_check.sh`.** `cut-manifest.sh` uses `git ls-files -co --exclude-standard`, so an untracked file
   that is not ignored is hashed silently. It has happened (a symlink and a local runs directory before G11). A tracked
   file deleted without `git rm` stops the cut. Do not remove a stray file or add it to `EXCLUDE` on your own: it is
   someone's, and `EXCLUDE` is a corpus decision a checkpoint records. Ask. If nobody can answer and the checkpoint's own
   §9 count and area table show the file is outside the cut, cut with an ignore that lasts one run, leave the file
   alone, and report it. If §9 does not settle it, stop and report it.

   ```sh
   printf '%s\n' <path> > "$SCRATCH/one-run-ignore"
   GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.excludesFile GIT_CONFIG_VALUE_0="$SCRATCH/one-run-ignore" \
     tools/cut-manifest.sh SHA256SUMS-G<n>
   ```
3. **Cut last.** `tools/cut-manifest.sh SHA256SUMS-G<n>`. The checkpoint is an entry in its own manifest, so **any edit
   after this means cutting again**, with the old file removed first. Do not hand-edit a line.
   Use the real name: `EXCLUDE` only skips names of the form `SHA256SUMS-G[0-9]+`, so any other name hashes itself.
4. **Verify**: `shasum -a 256 -c manifests/SHA256SUMS-G<n> | grep -c ': OK$'` equals the entry count, and §9 of the
   checkpoint states that count. `python3 tools/check-refs.py`, comparing with the known-missing count from the last cut.
5. **Hand over.** The custodian commits the cut. Then, in the narrative commit, the index row. The printed row is a
   template: its date is today's, and the row wants the date of the cut, and the commit of the cut.

## Reading a verification

`tools/verify-manifest.sh --all` extracts each row's commit and checks it there, so it is the check that means something.
`shasum -c` from the root checks today's tree, and an older manifest failing there is expected and often documented.
G11 §9 records two.

A row's `entries` and `expected` columns differ when a known failure is recorded. `SHA256SUMS-REF-2026.09.29b` is 65
and 64, "pin file moved after the manifest was taken". `EXPECTED` in the output means the count differs from the row,
which is the thing to investigate.

## Quick reference

| Task | Command |
|---|---|
| Reference manifest | `scripts/cut_ref_manifest.sh SHA256SUMS-REF-<date> <commit> <cut-date>` |
| Pre-cut check | `scripts/precut_check.sh` |
| Checkpoint manifest | `tools/cut-manifest.sh SHA256SUMS-G<n>`, last |
| One manifest at its commit | `tools/verify-manifest.sh <name> <commit>` |
| All of them | `tools/verify-manifest.sh --all` |
| Citation digest | `shasum -a 256 manifests/<name> \| cut -c1-16` |

## Rationalizations to reject

| Rationalization | Reality |
|---|---|
| "The working tree is close enough to the commit." | Then the manifest is of neither. Measure the commit. |
| "`cut-manifest.sh` is the manifest tool." | It excludes the reference. A file from it for `mechanism/` would be empty of what you want. |
| "It's one stray notes file; it won't matter." | It is now in the state of record, and the next verification depends on it. |
| "I'll delete the stray file so the cut is clean." | It is someone's work. Report it, and use a one-run ignore only if §9 settles it. |
| "I'll add it to EXCLUDE." | That is a corpus decision a checkpoint records, not a way to tidy. |
| "It was only a typo after the cut; patch the one line." | Cut again. A hand-edited line claims a run that did not happen. |
| "The row the tool printed is right." | Its date is today's and its commit is a placeholder. |
| "An old manifest fails, so something's broken." | Check it at its commit. Today's tree is not what it measured. |
| "I'll tag it while I'm here." | Tags are the custodian's. |

## References

- [g-cut.md](references/g-cut.md): the checkpoint document's sections, every file a cut touches, and the narrative commit.
- `scripts/cut_ref_manifest.sh`, `scripts/precut_check.sh`.
- `manifests/README.md`, `tools/cut-manifest.sh`, `tools/verify-manifest.sh`.
