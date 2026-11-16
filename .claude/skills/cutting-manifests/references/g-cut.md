# A Genesis Checkpoint cut

G11 is the model: the cut is `ce8f460`, the index row `9212952`, the narrative commit `a77d226`.
`git show --stat <commit>` for any of them shows what a cut touches.

## The cut commit

| File | Change |
|---|---|
| `checkpoints/topak-genesis-checkpoint-G<n>-<date>.md` | New. Nine sections, below |
| `README.md` | The "State of record" pointer |
| `checkpoints/README.md` | Current state, a G<n> paragraph on what is first at this cut, the tags line |
| `decisions/README.md` | Line 4, "Status is as of Genesis Checkpoint G<n>" |
| `mechanism/GAPS-AND-ASSUMPTIONS.md` | The register header |
| `manifests/EXCLUDE` | Only if the cut decides it, and the G<n> paragraph says so |
| `manifests/SHA256SUMS-G<n>` | **Last**, by `tools/cut-manifest.sh` |

Check the working tree first: `scripts/precut_check.sh`. A checkpoint is never revised after this commit. Corrections
go in the next one's §6.

## The checkpoint's nine sections

1. Ratification record
2. The floors as ratified
3. Verified artifacts
4. Genesis debt ledger (ADR-0029 §7): the confirmation-required set, whether the bootstrap specification exists, the
   reviewer line of A2.5
5. Conventions carried at this cut
6. Records changed after their own ratification
7. Open list, continuing the previous checkpoint's numbering
8. What this checkpoint does not claim. Batches owe sentences here; each ratification's report names what is owed
9. Manifest: the name, the entry count, what it was cut from, a table of entries by area, which reference manifests it
   measures, the two commands to verify it, and any manifest that fails at today's tree and why

The manifest's own digest cannot appear inside the file it measures, and the checkpoint is an entry in it. Both go in
the commit that adds them, and `index.tsv` names that commit.

## After the cut

The index row names the commit of the cut, which is why it is not in that commit. Its columns, tab-separated:
name, kind, cut date, commit (7 hex), entries, expected, note. The note says what is first at this cut.

The narrative commit: the Theory of Operation revision, `narrative/glossary.md`, `narrative/architecture-description.md`,
`narrative/README.md`, `REVIEWERS_GUIDE_README.md`, top-level `README.md` where a pointer moves, and the row in
`manifests/index.tsv` if it was not its own commit. G10's index row landed with its narrative, G11's just before.

Checks: `shasum -a 256 -c manifests/SHA256SUMS-G<n>`, `tools/verify-manifest.sh --all`, `python3 tools/check-refs.py`.
G11's check-refs reported eleven in-repo MISSING that predate it, and twelve at the cut, since its own open list cites a
file the cut removed. Compare with the previous count rather than expecting zero. In a clone, or a worktree, paths under
`tools/`, `slm/` and `spec/.tlacache` also show as missing because they are not tracked, so count only the in-repo ones.

Tags (`G<n>`, `ToO-rev<k>`, `glossary-<date>`, `REF-<date>`) are the custodian's.

## Gotchas

- `git stash` and `git stash pop` unstage a staged deletion. Re-stage with `git rm`, or the cut fails on the missing file.
- In a worktree the untracked `tools/` binaries are absent, and a checkpoint's rerun evidence needs the main checkout's.
- A stale reference: if `mechanism/` moved since the last reference manifest, say so, or cut one first. G11's §9 states
  which reference manifest measures the code at the cut.
