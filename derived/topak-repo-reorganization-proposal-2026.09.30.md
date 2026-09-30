# TOPAK — Repository reorganization proposal

**2026.09.30** · proposal, not a corpus record · written against `main` at `9e9cea2` (after G5; G5's manifest already fails 11 entries at HEAD) · nothing here is applied · revised 2026.09.30 after a read-through against the tree (§0 item 1 and item 5, P2, P5, §3, §4, §5, §7, §8; every §4 count re-run and reproduced)

**Point of execution.** Not date-bound; sequenced. The reorganization is one commit on `main` whose parent is the last pre-G6 content batch. The next commit adds the G6 checkpoint and its manifest and carries the `G6` tag, as G3–G5's tags sit on the commit that added each checkpoint (§6, §7). Nothing in §2–§7 is applied before every pre-requisite below holds.

**Pre-requisites.**

1. **In-flight content landed.** At `9e9cea2` four records (ADR-0022, 0033, 0037, 0039) and seven `floor/` files already differ from G5's cut, and ADR-0033 A3 is pending. Every batch the custodian intends before G6 is committed first, so the reorganization commit contains no content change to a corpus artifact and G6's "what changed" is honest (§7 step 1).
2. **Green at the parent commit.** `mechanism/corpus-pins.sha256` re-pinned; `cd mechanism && cargo test --workspace --release` passes; `floor/run-gates.py` passes. The same commands prove the cut afterwards (§7 step 4), so they must pass before it.
3. **The three tools exist and run against the pre-cut tree.** `verify-manifest.sh` takes the manifest directory as a parameter (root today, `manifests/` after), so it reproduces the §4 table on the parent commit before anything moves.
4. **Two custodian decisions taken and written down:** the manifest exclusion rule (§5, now stated, not a question) and whether the one-line Basis edit to the glossary head is made in the cut or left stale until the next glossary revision (§3, §7 step 3).
5. **Working tree clean.** `doc/` is untracked and not ignored today; the `.gitignore` change (§7 step 3) is part of the cut, so nothing under `doc/` or `tools/cvc5-*/` may be staged by `git add -A` when the cut is made.

---

## 0. What constrains the design

Five facts about the repository as it stands decide what can move and what cannot.

1. **Paths are load-bearing in four places.**
   - The digest manifests (`SHA256SUMS-*`) list root-relative paths, and `shasum -a 256 -c` from the root is the checkpoint verification procedure (G5 §9).
   - `mechanism/corpus-pins.sha256` pins `decisions/ADR-*.md` and `spec/*.tla` by root-relative path. `mechanism/crates/topak-core/tests/drift.rs` resolves them from the repository root (three levels up from its crate) and fails the suite on a miss.
   - Code reads sibling trees by relative path: `topak-floor` does `include_str!("../../../../floor/…")` three times (and `floor/genesis-tests.json` once in its tests); `mechanism/scripts/dev-init.sh` reads `../spec/*.tla`; `build-bundle.sh` reads `../policies`; every `spec/*-run.sh` reads `../tools/tla2tools.jar`.
   - **Accepted records cite evidence by path.** ADR-0013, 0026, 0030, 0031, 0034 cite `spec/<Module>-results-<date>.txt`; ADR-0030 and 0033 cite `floor/genesis-gates-results-*.txt`; ADR-0035 cites `slm/*-results-*.txt`; ten ADR provenance notes cite `derived/<name>-<date>.md`. **A root file's name is a root-relative path**: ADR-0031, 0032 and 0034 cite `NARRATIVE-LOG-2026.09.17.md` in their provenance notes, and G1 §4 cites four process logs and four ToO revisions (`checkpoints/topak-theory-of-operation-2026.09.10.md`, `-09.11`, `-09.12`, `-09.15`) by full path. §3 treats these as the two places P2 is bent, not as basename citations. Editing an accepted record to fix a path changes its digest, which means an erratum, a moved pin line and a manifest entry that fails "by construction". That cost is never worth a tidier path.

2. **Digests are path-independent.** Moving a file never changes its digest. Every citation by digest (46 truncated digests in `decisions/`, the "frozen from G5 on, cited by digest" rule for `Seats.tla`, `Observers.tla`, `Coupling.tla`) survives any move. Only path lookups break.

3. **Git history starts on 2026-09-25** (`8fdbe97`, an import of 155 files). G1, G2, the v1 corpus manifest and Theory of Operation (ToO) revisions 09.10 through rev 6 have no per-commit history; they exist only as files. Every commit a record cites (`aa93da4`, `4fd9677`, `453801c`, `5b25245`, `7f74c0b`, `1e6c0c4`, `219e104`) is in history and can carry a tag. **No tags exist today.**

4. **"The current manifest verifies at HEAD" is already false.** `SHA256SUMS-G5` passes 119 of 130 at `9e9cea2` (four records and seven floor files changed after the cut). Each checkpoint currently explains its predecessors' failure counts in prose ("expect 61 of 62; see below"). The right fix is a tool that verifies a manifest against the commit it measures, which makes every manifest in history pass cleanly (§4, verified).

5. **Small hygiene, found on the way.** `derived/topak-rung-DAG-2016.09.27.md` has a year typo and `derived/topak-gaps-prioritization-2026-09-28.md` uses hyphens where every other file uses dots; neither is cited by path anywhere, so both are safe to rename. `.gitignore` refers to `references/` and `REFERENCES.md`, which do not exist; third-party material actually lives in an untracked `doc/` that is not ignored (only `*.pdf` is, so the NIST `.md` in `doc/` would be picked up by `git add -A`). `tools/` is ignored as a whole directory and holds two untracked things: the TLC jar and the static cvc5 build that `floor/run-gates.py` needs (`floor/README.md` points `CVC5` at it); narrowing the ignore to the jar alone would expose the cvc5 directory. `install-tla.sh` rewrites the tracked `tlc` and `tlc-workers` on every run. The 09.29 glossary's Basis line cites the rev9 ToO by its `checkpoints/` path, which the cut removes. `spec/` is the only artifact directory without a README. The root holds 33 files, 16 of them manifests.

---

## 1. Principles

| | Principle | Consequence |
|---|---|---|
| **P1** | **A move is a cut.** | Do the reorganization in one commit with no content changes, tag it, and cut G6 from it with a fresh manifest. The G6 manifest is what makes the new layout the state of record. |
| **P2** | **Never rename what an accepted record cites by path; never move what code resolves by path.** | `decisions/`, `spec/`, `floor/`, `policies/`, `mechanism/`, `slm/` and the dated results files inside them stay exactly where they are. Bent in exactly two places, both stated in §3: the six root process logs (cited by root name in three ADRs and G1) and the four earliest ToO revisions (cited by full path in G1 §4). Both are resolved by the G6 path map and verify-at-commit, never by editing a record. |
| **P3** | **Move only what is cited by basename, by revision number, or not at all.** | Root manifests, root process logs, root scripts, the ToO revisions, the glossary head. |
| **P4** | **Verify historical manifests at the commit they measure, by tool.** | Replaces the "expect N of M" prose. Every manifest with a commit passes (§4). |
| **P5** | **Living documents get a head file and a tag per revision.** | Superseded dated copies made before the cut stay as a closed archive (git cannot reproduce pre-09.25 revisions, and a tarball reader has no git). From the cut on, no new dated copies: a revision is a commit, a tag and a manifest entry. Consequence stated plainly: from G6 on, cross-checkpoint history of a living document is a git-only feature. A tarball taken at any checkpoint still carries the head that checkpoint cites, and the checkpoint cites it by digest, so a tarball reader can verify the revision in front of them but cannot read an earlier one. |
| **P6** | **Frozen evidence keeps its dated name forever.** | Dated names are the right convention for one-shot artifacts (TLC results, gate runs, reviews, assessments). They are the wrong convention for a document that has a current version. |

---

## 2. Target tree

```text
TOPAK/
├── README.md  LICENSE  LICENSE-DOCS  NOTICE  SECURITY.md  CODEOWNERS  .gitignore  .claude/
│
├── decisions/                 UNCHANGED (path-pinned by corpus-pins.sha256 and every manifest)
│   └── README.md              NEW  index: number · title · status at last checkpoint · superseded by
│
├── checkpoints/               G1…G5 and the v1 corpus manifest only: the state of record
│   └── README.md              NEW  which checkpoint is current; the layout map from the G6 cut (§6)
│
├── narrative/                 NEW  the living layer, cut with each checkpoint; "narrative" is the corpus's own word
│   ├── theory-of-operation.md          head; at the cut its bytes are rev 9's
│   ├── glossary.md                     head; at the cut its bytes are the 09.29 glossary's, plus the one Basis-line edit if
│   │                                   the custodian permits it (§3, §7 step 3)
│   └── revisions/                      closed archive, byte-identical moves: ToO 09.10, 09.11, 09.12, 09.15,
│                                       09.15-rev5, 09.23-rev6, 09.25-rev7, 09.28-rev8. Nothing is added after the cut.
│
├── derived/                   UNCHANGED names (cited by path in ten ADRs); two typo renames; + README index
├── spec/                      UNCHANGED (path-pinned) + README.md NEW: module → record → run script → results → frozen?
├── floor/  policies/  mechanism/  slm/  diagrams/     UNCHANGED
│
├── process/                   NEW  FOLD-LOG, FREEZE-AND-BATCH-A, NARRATIVE-LOG ×2, NORMALIZATION-LOG,
│   └── README.md                   RECOVERY-REGISTRY: moved, same names. One-time genesis cleanup events.
│
├── manifests/                 NEW  all 16 SHA256SUMS-* moved, SAME BASENAMES (prose cites them by basename)
│   ├── README.md                   what each measures and how to verify
│   └── index.tsv                   name · kind · cut date · commit measured · entries · expected OK · note
│
└── tools/                     NEW tracked directory (today it is only the gitignored jar target)
    ├── tlc  tlc-workers  install-tla.sh    moved; wrapper jar path fixed; installer no longer rewrites wrappers
    ├── verify-manifest.sh                  NEW  §4
    ├── cut-manifest.sh                     NEW  §5
    ├── check-refs.py                       NEW  §5
    ├── tla2tools.jar                       gitignored, same path as today so spec/*-run.sh is untouched
    └── cvc5-*/                             gitignored, same path as today so floor/README.md's CVC5 export is untouched
```

Root goes from 33 files to 8. Four things become one-line lookups that today need a search: where the manifests are, where the process logs are, which ToO is current, and which glossary is current.

---

## 3. Disposition of every file

| Today | Proposed | Cited by path? | Risk and handling |
|---|---|---|---|
| `SHA256SUMS`, `-G1`…`-G5`, `-REF-*` ×5, `-SLM-*` (16 at root) | `manifests/<same basename>` | Basename only, in G2–G5 §9 and ADR-0033 §7 | G5 measures five of them (the REF and SLM manifests) at root paths. Handled by verify-at-commit (§4). `shasum -c manifests/SHA256SUMS-G5` from the root still works, because entries are root-relative. |
| `FOLD-LOG`, `FREEZE-AND-BATCH-A`, `NARRATIVE-LOG` ×2, `NORMALIZATION-LOG`, `RECOVERY-REGISTRY` | `process/<same name>` | **Yes.** A root name is a root-relative path: `NARRATIVE-LOG-2026.09.17.md` in the provenance notes of ADR-0031, 0032 and 0034; all four 09.15 logs in G1 §4; the 09.15 narrative log in the rev5 ToO header and the 09.17 log's header | **P2 exception (a).** The citations stay greppable by name; the G6 path map and `checkpoints/README.md` resolve them. G5 measures six root entries; verify-at-commit. |
| `tlc`, `tlc-workers`, `install-tla.sh` | `tools/` | README only (and `./install-tla.sh` in G2 §, historical) | Not measured (G5 excludes "the tools directory and the installer"). Wrapper becomes `$(dirname "$0")/tla2tools.jar`; installer stops regenerating wrappers. `spec/*-run.sh` are measured and cite `../tools/tla2tools.jar`; the jar stays there, so they do not change. `.gitignore` goes from `tools/` to `tools/tla2tools.jar` **and** `tools/cvc5-*/`, so the untracked cvc5 build the floor gates use stays untracked. |
| `checkpoints/topak-theory-of-operation-2026.09.29-rev9.md` | `narrative/theory-of-operation.md` (head) | Basename in README, G5 header, glossary header | Records cite "ToO rev N §x", never a path. Tag `ToO-rev9` on `64e5413` resolves the old name. |
| `checkpoints/topak-theory-of-operation-*` (the other eight) | `narrative/revisions/<same name>` | **Partly.** G1 §4 cites 09.10, 09.11, 09.12 and 09.15 by full `checkpoints/` path; rev5 onward by basename in critical reviews and checkpoint headers, by `ToO rev N §x` in records | **P2 exception (b).** Byte-identical moves. G1 is pre-git, so its manifest cannot be rescued by verify-at-commit: those four files and the four 09.15 process logs pass G1 today and will not after the move, so G1 at HEAD goes from 26 to 18 of 49, and G2 at HEAD from 51 to 39 of 64 (six logs, six ToO revisions). The index rows (§4) record it; at `8fdbe97` both counts are unchanged. G5 measures all nine ToO files; verify-at-commit. |
| `derived/topak-glossary-2026.09.29.md` | `narrative/glossary.md` (head) | README only | Same as the ToO head, with one wrinkle: its Basis line cites `checkpoints/topak-theory-of-operation-2026.09.29-rev9.md`, a path the cut removes. The head is a living document, so the fix is a one-line edit to `narrative/theory-of-operation.md`. That is the only content edit to a moved corpus artifact the cut would make; the custodian decides (pre-requisite 4) whether it goes in the cut or waits for the next glossary revision. Either way G5 still measures the 09.29 bytes at its own commit. |
| `derived/topak-glossary-2026.09.17.md`, `-2026.09.26.md` | **stay** | 09.17 by ADR-0032 and ADR-0037; 09.26 by the 09.29 glossary's supersession line | Frozen. |
| `derived/topak-rung-DAG-2016.09.27.md` | `derived/topak-rung-DAG-2026.09.27.md` | No | Typo fix. G5 measures it under the typo; verify-at-commit. |
| `derived/topak-gaps-prioritization-2026-09-28.md` | `derived/topak-gaps-prioritization-2026.09.28.md` | No | Convention fix. Same. |
| everything else in `derived/` | **stay** | Yes, ten ADR provenance notes | Frozen archive of one-shot analyses. New analyses still land here, dated. |
| `checkpoints/topak-genesis-checkpoint-G*`, `topak-genesis-corpus-manifest-v1-*` | **stay** | Yes | State of record; each is one cut, never revised. Dated names are right here. |
| `decisions/`, `spec/`, `floor/`, `policies/`, `mechanism/`, `slm/`, `diagrams/` | **stay** | Yes, and code paths | P2. |
| `spec/*-results-*.txt`, `floor/genesis-gates-results-*.txt`, `slm/*-results-*.txt` | **stay beside their modules** | Yes, five ADRs / two ADRs / one ADR | A `spec/results/` split would split old from new and strand five records' paths. Not worth it. |
| `spec/RulesFloorNV.tla` + `_rev5.tla`, `Lease.tla` + `Lease_A1.tla` | **stay** | By digest | Frozen successors by design (ADR-0026 §, ADR-0031 §). This is the one place versioned filenames are correct: both versions are live citation targets. |

---

## 4. `tools/verify-manifest.sh`, and what it found

The script extracts the tree at a commit into a temporary directory and runs `shasum -c` there, so a manifest is checked against the tree it measured, not against whatever HEAD is today. Prototype (run in this session, read-only):

```bash
#!/usr/bin/env bash
# verify-manifest.sh MANIFEST COMMIT     — verify MANIFEST against the tree at COMMIT
set -euo pipefail
repo="$(git rev-parse --show-toplevel)"; m="$1"; c="$2"
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
git -C "$repo" archive "$c" | tar -x -C "$tmp"
total=$(grep -cvE '^\s*(#|$)' "$repo/manifests/$m")
out=$(cd "$tmp" && shasum -a 256 -c "$repo/manifests/$m" 2>/dev/null || true)
ok=$(printf '%s\n' "$out" | grep -c ': OK$' || true)
printf '%-28s @%s  %3d/%-3d OK\n' "$m" "$c" "$ok" "$total"
[ "$ok" -eq "$total" ] || printf '%s\n' "$out" | grep -v ': OK$'
```

With `--all` it reads `manifests/index.tsv` and checks every row. Results today, against the commits the checkpoints and ADR-0033 name:

| Manifest | Commit measured | Result | Matches the record? |
|---|---|---|---|
| `SHA256SUMS-G3` | `27ea3ff` | **86/86** | Yes (G3 §9: expect 86) |
| `SHA256SUMS-G4` | `7542730` | **108/108** | Yes |
| `SHA256SUMS-G5` | `64e5413` | **130/130** | Yes (G5 §9: expect 130). At HEAD it is 119/130. |
| `SHA256SUMS-REF-2026.09.24` | `4fd9677` | **59/59** | Yes (ADR-0033 §7) |
| `SHA256SUMS-REF-2026.09.25` | `453801c` | **61/61** | Yes; G3's "59 of 61" was measured at G3's tree, not at `453801c` |
| `SHA256SUMS-REF-2026.09.28` | `5b25245` | **61/61** | Yes |
| `SHA256SUMS-REF-2026.09.29` | `7f74c0b` | **62/62** | Yes; G5's "61 of 62" was measured after Batch 16 moved the pin |
| `SHA256SUMS-REF-2026.09.29b` | `1e6c0c4` | **64/65**, `corpus-pins.sha256` | Yes, exactly as ADR-0033 A3 says: taken on the working tree before the pin moved |
| `SHA256SUMS-SLM-2026.09.28` | `7542730` | **40/40** | Yes (G5 §9: expect 40) |
| `SHA256SUMS-G2` | pre-git; `8fdbe97` is the nearest | 60/64 at `8fdbe97`, 51/64 at HEAD | Not verifiable at its own tree; the four failures at `8fdbe97` are records changed 09.23–09.25. After the cut, twelve more miss at HEAD (six logs, six ToO revisions), giving 39/64; stable at `8fdbe97` |
| `SHA256SUMS-G1` | pre-git; `8fdbe97` is the nearest | 29/49 at `8fdbe97`, 26/49 at HEAD | Same; the record of its cut, as G1 says. After the cut, eight more miss at HEAD (four ToO revisions and four process logs moved, §3), giving 18/49; `8fdbe97` predates the move, so the 29/49 at that commit is stable |
| `SHA256SUMS` | pre-git, flat paths | 7/60 | Historical, as its header says |

So every manifest that has a commit passes at that commit, and the one expected miss is the one its record predicts. That is the argument for `index.tsv`: one row per manifest with the commit and expected count, and the "see below" paragraphs in future checkpoints shrink to a table reference.

`manifests/index.tsv` (initial contents, from the table above):

```text
name	kind	cut	commit	entries	expected_ok	note
SHA256SUMS	historical	2026.09.15	-	60	-	pre-layout flat paths; the record of its cut
SHA256SUMS-G1	checkpoint	2026.09.15	8fdbe97	49	29	pre-git; 29/49 at 8fdbe97 (nearest tree); 26/49 at 9e9cea2, 18/49 after the G6 cut
SHA256SUMS-G2	checkpoint	2026.09.23	8fdbe97	64	60	pre-git; 60/64 at 8fdbe97 (nearest tree); the four misses are records changed 09.23–09.25; 51/64 at 9e9cea2, 39/64 after the G6 cut
SHA256SUMS-G3	checkpoint	2026.09.25	27ea3ff	86	86
SHA256SUMS-G4	checkpoint	2026.09.28	7542730	108	108
SHA256SUMS-G5	checkpoint	2026.09.29	64e5413	130	130
SHA256SUMS-REF-2026.09.24	reference	2026.09.24	4fd9677	59	59	ADR-0033 §7
SHA256SUMS-REF-2026.09.25	reference	2026.09.25	453801c	61	61	ADR-0033 §7 R13
SHA256SUMS-REF-2026.09.28	reference	2026.09.28	5b25245	61	61	ADR-0033 A1
SHA256SUMS-REF-2026.09.29	reference	2026.09.29	7f74c0b	62	62	ADR-0033 A2
SHA256SUMS-REF-2026.09.29b	reference	2026.09.29	1e6c0c4	65	64	ADR-0033 A3; pin file moved after the manifest was taken
SHA256SUMS-SLM-2026.09.28	rehearsal	2026.09.28	7542730	40	40	ADR-0035 §8
```

---

## 5. The other two tools

**`tools/cut-manifest.sh <name> [paths…]`.** Deterministic manifest generation: `LC_ALL=C` sorted, root-relative, excluding what G5 §9 excludes, written once into `manifests/EXCLUDE`. G5's actual rule, read from its §9: exclude the licence and notice files, the README, `tools/` and the installer, `doc/`, `sessions/`, exports and archives, and **earlier checkpoint manifests**; but **measure** the reference and rehearsal manifests (G5 lists the five `REF` and `SLM` manifests as entries), and measure `mechanism/`, `policies/` and `slm/` through their tree manifests rather than file by file. Carried into the new layout: `manifests/SHA256SUMS-REF-*`, `manifests/SHA256SUMS-SLM-*` and `manifests/index.tsv` are measured; `manifests/SHA256SUMS`, `manifests/SHA256SUMS-G*` and `manifests/README.md` are not; `process/` is measured, as the six root logs are today. Today each manifest is cut by hand and the exclusion list is prose that has drifted between G3 and G5. A script makes the next cut a one-liner and appends the `index.tsv` row.

**`tools/check-refs.py`.** Walks every `.md` and checks that every backticked root-relative path (`decisions/ADR-0037.md`, `spec/Lease_A1-results-2026.09.28.txt`, `floor/run-gates.py`) exists; flags date tokens that are not `20YY.MM.DD`. It would have caught the `derived/derived/` doubling (`f160660`), the 2016 typo and the hyphenated date. Run it at every cut; after the G6 move it reports the stale basename citations in G5 and the critical reviews once, as information, and `checkpoints/README.md` carries the map.

---

## 6. Tags

Annotated tags change no bytes and no digests. They give the "git versions" the dated filenames were standing in for, and they make every commit a record cites resolvable by name.

| Tag | Commit | What it marks |
|---|---|---|
| `G3`, `G4`, `G5` | `27ea3ff`, `7542730`, `64e5413` | The commit that added each checkpoint and its manifest |
| `ToO-rev7`, `ToO-rev8`, `ToO-rev9` | `91f393a`, `7542730`, `64e5413` | The commit that added each revision |
| `REF-2026.09.24` … `REF-2026.09.29b` | `4fd9677`, `453801c`, `5b25245`, `7f74c0b`, `1e6c0c4` | The reference tree each ADR-0033 addendum cites |
| `SLM-2026.09.28` | `7542730` | The rehearsal tree ADR-0035 §8 cites |
| `G6` | the commit that adds the G6 checkpoint and manifest, whose parent is the reorganization commit | First cut under the new layout; same convention as G3–G5 |

G1, G2 and revisions 09.10 through rev 6 predate git and get no tag; their files in `checkpoints/` and `narrative/revisions/` are their only home, which is why the archive stays in the tree (P5).

From G6 on, a ToO revision is: edit `narrative/theory-of-operation.md`, append its "Changes from revision N" appendix as today, commit, tag `ToO-revN`, and let the checkpoint's manifest measure the head. Citing it stays as the corpus already does: "rev 10 (`<digest16>`)". `git diff ToO-rev9 ToO-rev10 -- narrative/theory-of-operation.md` replaces reading two 1,500-line files side by side.

---

## 7. Sequencing the cut

1. **Land any in-flight content first** (post-G5 batches; pre-requisite 1). The reorganization commit contains only moves, the three tools, the five READMEs, `.gitignore`, `index.tsv`, the README's Layout table and Start-here links, the wrapper and installer fixes, and at most one content edit to a moved corpus artifact (the glossary Basis line, if permitted). Keeping content out keeps `git log --follow` clean and G6's "what changed" honest.
2. **`git mv` everything in §3.** History follows each file.
3. **Fix the wrappers and the installer**; `.gitignore`: `tools/` → `tools/tla2tools.jar` and `tools/cvc5-*/`, add `doc/`, drop the dead `references/` and `REFERENCES.md` lines. Make the glossary Basis-line edit here if pre-requisite 4 permits it; otherwise leave the line and list it in `check-refs.py`'s known-stale set until the next glossary revision.
4. **Prove nothing broke**, in this order:
   - `tools/verify-manifest.sh --all` — every row of `index.tsv` at its expected count (§4).
   - `cd mechanism && cargo test --workspace --release` — `drift.rs` and the `include_str!` paths are untouched because `decisions/`, `spec/` and `floor/` did not move; this run proves it. This is the proof that matters most: it exercises every path the code resolves.
   - `floor/run-gates.py` with `CVC5` exported as `floor/README.md` says — proves the cvc5 directory is still where the ignore change left it.
   - `cd spec && ./coupling-run.sh c-none-noadmit none NoAdmitWithoutLiveObserver` — proves the jar path.
   - `tools/check-refs.py` — expect only the known stale basenames.
5. **Cut G6** as the next commit. Its §9 uses `cut-manifest.sh`; a new short section states the path map once (old → new for the 33 moved files) so every stale name in G1–G5, ADR-0031, 0032, 0034, ADR-0033 and the critical reviews has one resolution point, and names the two P2 exceptions from §3. Tag `G6` on this commit, and `ToO-rev10` if a revision is cut with it.

---

## 8. What is deliberately not proposed

- **Moving `decisions/`, `spec/`, `floor/`, `policies/`.** Code paths, pins and accepted records all resolve them by path.
- **A `spec/results/` or `floor/results/` split.** Five accepted ADRs cite `spec/<Module>-results-<date>.txt`; results stay beside the module they measure.
- **Renaming manifests to `G5.sha256`.** G2–G5 and ADR-0033 cite them by basename; keeping basenames keeps every citation greppable. Directory, not name, is what was missing.
- **Dropping the dated ToO revisions from the tree.** Six of nine predate git and have no other home; a tarball reader has no `git show`. The archive is closed at rev 8 and never grows.
- **Rewriting or squashing history.** Seven cited commits must stay resolvable.
- **Editing any accepted record to fix a path.** Digest change → erratum → pin → manifest churn. The path map in G6 and `checkpoints/README.md` does the same job at zero digest cost. This covers the two P2 exceptions too: ADR-0031, 0032 and 0034 keep their `NARRATIVE-LOG-2026.09.17.md` line and G1 keeps its `checkpoints/` ToO paths, stale, resolved by the map.
- **Keeping dated copies of the ToO after rev 9 for tarball readers.** P5 states the consequence: from G6 on, earlier revisions of a living document are reachable by git only. A tarball at any checkpoint still carries the revision that checkpoint cites, by digest.
- **Ignoring `tools/` wholesale.** The wrappers move in and must be tracked, so the ignore narrows to the jar and the cvc5 build, the two untracked things that live there today.
- **CI.** A GitHub Action running `verify-manifest.sh --all`, `check-refs.py`, `cargo test` and `opa test policies/` would be natural and is one file under `.github/workflows/`. It is a separate decision from layout and is left out here.
