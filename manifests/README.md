# Manifests

Every `SHA256SUMS-*` file is a digest manifest cut at one commit, with root-relative paths as they stood at that
commit. **Verify a manifest against the tree it measured, not against today's**: `tools/verify-manifest.sh --all`
reads `index.tsv` and checks every row at its commit; `tools/verify-manifest.sh SHA256SUMS-G6 5244aab` checks one.
`shasum -a 256 -c manifests/SHA256SUMS-G8` from the repository root still works for the newest cut, until the next
move. From G7 on a checkpoint manifest measures `tools/tla2tools.jar` and `tools/cpc/` and not `index.tsv`.

| Kind | Files | What they measure |
|---|---|---|
| checkpoint | `SHA256SUMS-G1` … `-G8` | The corpus at each genesis checkpoint: records, checkpoints, derived analyses, specs and results, the floor, the process logs, the reference and rehearsal manifests. Each checkpoint's §9 says what it excludes; `EXCLUDE` states the rule once for `tools/cut-manifest.sh` |
| reference | `SHA256SUMS-REF-<date>` | `mechanism/` and `policies/` at the commit an ADR-0033 addendum cites |
| rehearsal | `SHA256SUMS-SLM-<date>` | The `slm/` tree ADR-0035 §8 cites |
| historical | `SHA256SUMS` | The 2026.09.15 flat layout; the record of its cut and nothing else |

`index.tsv` is one row per manifest: name, kind, cut date, the commit measured, entry count, the count expected to
verify at that commit, and why it differs when it does. G1 and G2 predate git and are checked at the nearest tree.
Earlier checkpoint manifests are not themselves measured by later ones; reference and rehearsal manifests are.
