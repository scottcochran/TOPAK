# Checkpoints

**Current state of record: [Genesis Checkpoint G9](topak-genesis-checkpoint-G9-2026.10.02.md)** (2026.10.02, tag
`G9`). Each checkpoint is one cut, never revised: what each record says, what was ratified and by whom, what is owed,
what is open, and the manifest that measures it. The narrative cut with it is `narrative/theory-of-operation.md`,
and where the two disagree the checkpoint wins. The v1 corpus manifest (2026.09.15) is the first cut of all.

## The 2026.09.30 layout map

The reorganization commit after G6 moved thirty-seven files and changed no bytes in any of them. Frozen records and
checkpoints that cite the old names are **not edited**, because their digests are pinned and measured; this table is
the one resolution point. Manifests cut before the move still verify at the commit they measured:
`tools/verify-manifest.sh --all`.

| Was | Is now |
|---|---|
| `SHA256SUMS*` at the root (fifteen files) | `manifests/<same name>` |
| `FOLD-LOG-2026.09.15.md`, `FREEZE-AND-BATCH-A-2026.09.15.md`, `NARRATIVE-LOG-2026.09.15.md`, `NARRATIVE-LOG-2026.09.17.md`, `NORMALIZATION-LOG-2026.09.15.md`, `RECOVERY-REGISTRY-2026.09.15.md` | `process/<same name>` |
| `tlc`, `tlc-workers`, `install-tla.sh` | `tools/<same name>`; the wrappers find the jar beside them |
| `checkpoints/topak-theory-of-operation-2026.09.30-rev10.md` | `narrative/theory-of-operation.md` (the head) |
| `checkpoints/topak-theory-of-operation-2026.09.10.md`, `-09.11.md`, `-09.12.md`, `-09.15.md`, `-09.15-rev5.md`, `-09.23-rev6.md`, `-09.25-rev7.md`, `-09.28-rev8.md`, `-09.29-rev9.md` | `narrative/revisions/<same name>` |
| `derived/topak-glossary-2026.09.29.md` | `narrative/glossary.md` (the head) |
| `derived/topak-rung-DAG-2016.09.27.md` | `derived/topak-rung-DAG-2026.09.27.md` (a year typo) |
| `derived/topak-gaps-prioritization-2026-09-28.md` | `derived/topak-gaps-prioritization-2026.09.28.md` (the dated-name convention) |

**Two citations by path are knowingly left stale** (the proposal's P2 exceptions): ADR-0031, ADR-0032 and ADR-0034
cite `NARRATIVE-LOG-2026.09.17.md` by its root name in their provenance notes, and G1 §4 cites four Theory of
Operation revisions by their `checkpoints/` path. Both resolve here. G1 and G2 predate git; after the move they
verify at 17 of 49 and 35 of 64 against today's tree, and at 29 of 49 and 60 of 64 at `8fdbe97`, the nearest tree,
which `manifests/index.tsv` records.

**G6 was cut before the move**, so its manifest measures the pre-cut paths and verifies at its own commit, `5244aab`.
**G7 (2026.10.01) is the first cut under this layout**; its manifest also measures `tools/cpc/`, the proof checker's
rule signature, beside the TLC jar, and excludes `manifests/index.tsv`, which names the commit each manifest is
verified at. **G8 (2026.10.02)** is the first cut whose trusted base names a prover (ADR-0046, T-0045-31); its
manifest excludes the TLAPS wrapper with the TLC wrappers and measures every proof module and proof results file. **G9 (2026.10.02)** is the first cut at which the reference issues a
lease above rung 0: a rung-1 launcher in the node, and rung 3 SIMULATED, under addenda still pending.

## Tags

`G3` to `G9` mark the commit that added each checkpoint; `glossary-<date>` each revision of the glossary in place;
`ToO-rev7` to `ToO-rev12` each Theory of Operation revision; `REF-<date>` the reference tree each ADR-0033 addendum cites; `SLM-2026.09.28` the rehearsal tree. G1, G2
and revisions before 7 predate git and have no tag.
