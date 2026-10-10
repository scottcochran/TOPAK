# Checkpoints

**Current state of record: [Genesis Checkpoint G11](topak-genesis-checkpoint-G11-2026.10.09.md)** (2026.10.09, tag
`G11`). Each checkpoint is one cut, never revised: what each record says, what was ratified and by whom, what is owed,
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
lease above rung 0: a rung-1 launcher in the node, and rung 3 SIMULATED, under addenda still pending. **G10
(2026.10.05)** is the first cut that records a provisional record (ADR-0029 A4) and a genesis-provisional floor
(ADR-0030 A3), and the first at which the reference links a floor other than the genesis draft; from this cut
`manifests/EXCLUDE` lists `REVIEWERS_GUIDE_README.md` and `ADOPTERS_GUIDE_README.md`, conveniences at the root that are kept current and not measured.
**G11 (2026.10.09)** is the first cut whose trusted base names two deductive methods (ADR-0053, T-0045-37), and the
first that records known unsound cases in a trust root kept in use (ADR-0046 A2); from this cut `manifests/EXCLUDE`
also lists `tools/lean-report.sh` and `tools/lean-sync.sh` (ADR-0053 §6).

## Errata to frozen checkpoints

A checkpoint is never revised, so a mistake in one is recorded here, dated, and corrected in the next cut. This list
is the resolution point for such errors, as the layout map above is for moved paths.

| Checkpoint | Erratum | Recorded |
|---|---|---|
| **G9** | **Item 79 and the header.** Item 79 says the tags `ToO-rev12`, `glossary-2026.10.02`, `REF-2026.10.02` and `REF-2026.10.02b` do not exist; all four exist, as does `ToO-rev13`. The header says revision 12 "stands, not revised at G9"; revision 13, cut from G9, was committed after the checkpoint (`9e811bc`, tag `ToO-rev13`) and is the narrative that goes with it. Item 79's remaining content, revision 13 and the glossary against G9, is discharged by that commit. `README.md` pointed at G8 and revision 12 until 2026.10.03. The 10.02 critical review's CR-31 found all three | 2026.10.03 |

## The ADR-0029 A2.5 line

ADR-0029 A2.5 (ratified 2026.09.25) says the genesis debt ledger gains a line stating whether a bootstrap reviewer is
engaged and the manifest digest of the last completed review pass. G3 was frozen when A2 was ratified and the line
was to appear in G3's successor; G4 to G9 do not carry it (the 10.02 critical review's CR-28 (ii)). It is kept here
until the next checkpoint's §4 carries it, and is to be copied there at every cut. **G10's and G11's §4 carry it**, with
the values below unchanged.

| Field | Value at 2026.10.03 |
|---|---|
| **Bootstrap reviewer engaged** | **None.** Every record, amendment, proof, module and reference tree is one hand's, drafted or ratified by the genesis custodian with the assistant; no reviewer independent of the author has read any record |
| **Last completed review pass** | **None.** No confirmation pass has been run and no review attestation exists; the field has no manifest digest to name. The dated critical reviews under `derived/` are the drafter's own and do not count under A2.1 |

## Tags

`G3` to `G11` mark the commit that added each checkpoint; `glossary-<date>` each revision of the glossary in place;
`ToO-rev7` to `ToO-rev14` each Theory of Operation revision; `REF-<date>` the reference tree each ADR-0033 addendum cites; `SLM-2026.09.28` the rehearsal tree. G1, G2
and revisions before 7 predate git and have no tag.
