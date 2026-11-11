# Self review of 2026.11.11: reader L's findings in full

Reader L read the lead: the corpus's own checkers and evidence, run. Annex to `derived/topak-open-findings-register-2026.11.11.md`, Part III. Each block is the finding as the reader wrote it, against the tree at `bbda621`, followed by the verdict of a verifier that did not find it. Paths are relative to the repository root. A path a finding names as absent is written without backticks. Nothing here is ratified, and every reader and verifier is of the same model lineage as the drafter of the corpus.

11 reported: 0 confirmed, 11 confirmed with a correction, 0 dropped.

### L-1: `tools/verify-manifest.sh --all` exits 0 when a manifest fails to verify
- Against: tools/verify-manifest.sh:18 (and tools/verify-manifest.sh:22-26)
- Basis: evidence
- Claim: "if [ "$ok" -eq "$3" ]; then printf '  (expected %s)\n' "$3"; else printf '  EXPECTED %s\n' "$3";"
- Why wrong: The script reports a mismatch only as the text `EXPECTED n` and never sets a non-zero status; `one` is called from a `while` loop in a pipeline and its result is discarded. With one digest of `manifests/SHA256SUMS-G11` altered in a throwaway clone, `tools/verify-manifest.sh --all` printed "SHA256SUMS-G11 @ce8f460 603/604 OK EXPECTED 604" and exited 0 (evidence/09-checker-mutations.txt, section M10). README.md:134 and REVIEWERS_GUIDE_README.md give this command as the check of every cut; a caller that reads the status, as the other sync scripts invite (`spec/proof-sync.sh` and `tools/lean-sync.sh` exit 1), is told every manifest verified.
- Fix belongs in: tools/verify-manifest.sh
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed with correction
- **Verifier's correction:** The defect stands: on a digest mismatch `one` prints `EXPECTED n` and the non-OK lines and returns 0, so `--all` exits 0. Drop the clause "its result is discarded": under the script's `set -euo pipefail` (line 7) a non-zero return from `one` inside the `while` pipeline would end the script non-zero (probe below), so the sole cause is that the mismatch branches of lines 18-19 only print. A fix that returns 1 from `one` will, under `set -e`, also stop at the first failing manifest unless the loop collects a status. M10 was not rerun (the copy has no .git); judged on the script text and the evidence file.
- **Verifier's evidence:** tools/verify-manifest.sh:7, :18-19, :22-25; README.md:132-134; REVIEWERS_GUIDE_README.md:123; spec/proof-sync.sh:63 and tools/lean-sync.sh:80 (`exit $status`); evidence/09-checker-mutations.txt M10 ("603/604 OK  EXPECTED 604", "exit 0"); probe `bash -c 'set -euo pipefail; f(){ return 1; }; printf "a\nb\n" | while read -r x; do f; done; echo after'` exits 1 and prints nothing

### L-2: `tools/check-refs.py` does not check paths under `skills/` or `diagrams/`
- Against: tools/check-refs.py:8
- Basis: evidence
- Claim: "PATH = re.compile(r"`((?:decisions|spec|floor|policies|mechanism|slm|derived|checkpoints|narrative|process|manifests|tools)/[^`\s]+)`")"
- Why wrong: The alternation has no `skills` and no `diagrams`. A sentence citing `skills/no-such-skill/SKILL.md` and `diagrams/topak/no-such.svg`, appended to README.md in a throwaway clone, added nothing to the script's output, while a bad path under `spec/` and a bad date were each reported (evidence/09-checker-mutations.txt, sections M1 to M3). README.md:139 describes the script as "Check every path a document cites". `skills/` was added on 2026.11.10 and README.md:43 cites four paths under it.
- Fix belongs in: tools/check-refs.py
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed with correction
- **Verifier's correction:** The quoted description "Check every path a document cites" is at README.md:137; line 139 is the command. README.md:43 does not illustrate the gap: its skills paths are Markdown link targets and bare names, and the script matches only backticked `dir/...` tokens whatever the directory. What the missing alternatives leave unchecked is the 15 backticked `skills/...` and `diagrams/...` citations in the copy's .md files (e.g. narrative/architecture-description.md `diagrams/gen-topak-family.py`, checkpoints/topak-genesis-checkpoint-G8-2026.10.02.md `diagrams/README.md`). The date `skills/` was added could not be checked (no history in the copy).
- **Verifier's evidence:** tools/check-refs.py:8 (quotation exact), :29-34; README.md:137-139, :43; evidence/09-checker-mutations.txt M1 (1), M2 (0), M3 (1); the line-8 regex run on a sample sentence returns only the `spec/` path; `grep -roE --include=*.md '`(skills|diagrams)/[^` ]+`' . | wc -l` = 15; `ls -d */` shows diagrams/ and skills/ as the two top-level directories outside the alternation

### L-3: No checker binds an overlay record to its module: a changed clause of ADR-0059 to ADR-0068 is reported by nothing, and a changed overlay module by `proof-sync` alone
- Against: mechanism/corpus-pins.sha256:1 (and spec/specification-graph.json; decisions/ADR-0062.md:274; decisions/ADR-0060.md:229)
- Basis: Proposed
- Claim: ADR-0062 R2: "No module changes"; ADR-0060 R2: "No decision is made, and no module changes"
- Why wrong: Clause pins computed with `spec/clauses.py` at `baddd63` (the commit that added the eight modules and the R1 rows) and at `bbda621` differ in nine overlay clauses: ADR-0060 §5, §6, §7; ADR-0062 §3, §8, §11; ADR-0063 §3; ADR-0067 §3, §4 (evidence/06-clause-pin-diff.txt). The R2 rows say so in prose and ADR-0062 §8 says "This bound is stated and not modelled", so the drift is acknowledged. What is missing is any check that would have reported it. In a throwaway clone, an edit to ADR-0059 §1 left `spec/proof-sync.sh`, `mechanism/corpus-pins.sha256` and `spec/specification-graph.py check` unchanged, and one byte added to `spec/Federation.tla` was reported by `proof-sync` only (evidence/09-checker-mutations.txt, sections M5 and M7). The same edits to `spec/Seats.tla` and to ADR-0031 §4 were each reported by three checks (M4, M8b). `grep -c "ADR-005[9]\|ADR-006" mechanism/corpus-pins.sha256` and `grep -c "ADR-0059\|Federation" spec/specification-graph.json` return 0.
- Fix belongs in: spec/specification-graph.json (a rebuild that includes the overlay), or a pin beside each record's R1 citation
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed with correction
- **Verifier's correction:** (1) "each reported by three checks" does not match the evidence: M4 (spec/Seats.tla) moves four (proof-sync, lean-sync STALE 3 to 5, corpus-pins, spec-graph 10 to 17 stale edges) and M8b (ADR-0031 §4) two (corpus-pins FAILED, spec-graph 10 to 27). (2) One checker already prints that the overlay is unbound, though it reports no change in it: `specification-graph.py check` at bbda621 says "the sync scripts: DISAGREES", "proof-sync.sh reads [the eight overlay proof modules] that no edge does", and ends "Result: FAILED: the sync scripts"; the committed results file of 2026.11.07 says "agrees". So "reported by nothing" holds for a clause edit and "by proof-sync alone" for a module edit, and the absence of edges is visible on a rerun. (3) For M5 and M7 the evidence gives exit statuses and counts against baselines that were already 1, not output diffs; that the three checks cannot see an overlay record was confirmed from the scripts and greps. The nine-clause drift rests on evidence/06 alone (baddd63 is not in the copy). All four R2 rows (ADR-0060, 0062, 0063, 0067) carry the no-module or no-policy sentence.
- **Verifier's evidence:** decisions/ADR-0062.md:274 ("No module changes"), :168 ("This bound is stated and not modelled"); decisions/ADR-0060.md:229 ("No decision is made, and no module changes"); decisions/ADR-0063.md:203; decisions/ADR-0067.md:182; evidence/06-clause-pin-diff.txt third block (12 changed, 9 of them overlay); evidence/09-checker-mutations.txt M4, M5, M7, M8b; evidence/04-spec-graph-check.txt:98-99, :204 against spec/specification-graph-results-2026.11.07.txt:93-94, :199; `grep -c "ADR-005[9]\|ADR-006" mechanism/corpus-pins.sha256` = 0; `grep -c "ADR-0059\|Federation" spec/specification-graph.json` = 0; `grep -cE "ADR-00(59|6[0-8])|Federation|Intent\.tla|Membership|Alone|Outstanding|PlaneClock|Peer\.tla|Release\.tla" spec/specification-graph.json` = 0; spec/proof-sync.sh:19-27 (reads only *_proof.tla and *-proof-results-*.txt); decisions/README.md:10 (corpus-pins holds what the reference follows)

### L-4: 190 tracked files are measured by no manifest, among them every overlay record, module, proof and results file
- Against: manifests/index.tsv:33 (and manifests/SHA256SUMS-G11)
- Basis: evidence
- Claim: "SHA256SUMS-G11" (the last row of the index; 604 entries at `ce8f460`)
- Why wrong: `git ls-files | grep -vE -f manifests/EXCLUDE | wc -l` gives 794 at `bbda621`; the difference from G11's 604 entries is 190 files, 13 under decisions/, 86 under derived/, 70 under spec/ and 21 under skills/, and ten of G11's own entries no longer match (evidence/01-g11-at-pin.txt). So the two batches ratified after G11 (ADR-0024 E1; ADR-0046 A3 with ADR-0045 A4) changed measured records with no cut behind them, and the evidence the overlay's R1 rows cite by digest is bound only by those sixteen-hex citations. A TLC results file edited in a throwaway clone (one verdict changed in `spec/Federation-results-2026.11.10.txt`) changed the status of no script (evidence/09-checker-mutations.txt, section M11); only a recomputation of the records' cited digests shows it (evidence/05-overlay-digest-citations.txt: 56 of 56 match today).
- Fix belongs in: the next checkpoint cut (manifests/)
- Severity: Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed with correction; severity Low-Medium (reader: Medium)
- **Verifier's correction:** The G11 row is manifests/index.tsv:32; the file has 32 lines. Severity: no text claims these files are measured. Manifests are cut at checkpoints, decisions/README.md marks all thirteen new records "after G11", and nothing found requires a cut per batch, so this is a lag in measurement plus an evidence chain no script checks, not two layers disagreeing; the two batches' ratified text in ADR-0024, ADR-0045 and ADR-0046 being unmeasured keeps it above Low. Counts: 13 decisions, 70 spec and 21 skills recounted in the copy; the 86 under derived/ could not be (the copy holds one derived file), but 794 - 604 = 190 is consistent, since none of G11's entries is excluded by the current EXCLUDE and all 604 are present at the pin. M11 shows exit statuses that were already 1 at baseline; that no script reads a TLC results file's verdict lines was confirmed from the scripts.
- **Verifier's evidence:** manifests/index.tsv:32; manifests/SHA256SUMS-G11 (604 entries; `... | grep -cE -f manifests/EXCLUDE` = 0); evidence/01-g11-at-pin.txt (594 OK, 10 FAILED, none missing); `find . -type f | grep -vE -f manifests/EXCLUDE` compared with the G11 list in the copy (unmeasured: decisions 13, spec 70, skills 21, derived 1 of the copy's 1); decisions/ADR-0024.md:329 (B38, 2026.11.02); decisions/ADR-0046.md:514 and decisions/ADR-0045.md:530 (B39, 2026.11.03); `grep -rnoE "Batch 4[0-9]" .` empty; evidence/05-overlay-digest-citations.txt (TOTAL 56: OK 56); evidence/09-checker-mutations.txt M11; spec/proof-sync.sh:19-27; decisions/README.md:69-81; checkpoints/README.md:3-6

### L-5: Three living documents name the tags `ToO-rev15` and `glossary-2026.10.09`; the origin holds neither
- Against: README.md:20 (and narrative/README.md:9; narrative/glossary.md:6; narrative/glossary.md:13; checkpoints/README.md:70)
- Basis: living document
- Claim: "(revision 15, tag `ToO-rev15`)"
- Why wrong: `git ls-remote --tags origin` lists 40 tags: G3 to G11, sixteen `REF-`, `SLM-2026.09.28`, `ToO-rev7` to `ToO-rev14`, and `glossary-2026.09.30` to `glossary-2026.10.05`. There is no `ToO-rev15` and no `glossary-2026.10.09`, so `git diff glossary-2026.10.05 glossary-2026.10.09 -- narrative/glossary.md`, the command narrative/glossary.md:13 gives, fails in a clone. checkpoints/README.md:70 says the tags run "`ToO-rev7` to `ToO-rev14`", which matches the origin and contradicts the other three. `REF-2026.10.01` is also absent although manifests/index.tsv has its row.
- Fix belongs in: the origin's tags, or README.md, narrative/README.md and narrative/glossary.md
- Severity: Low
- Confidence: high (for the origin as fetched on 2026.11.10; a tag may exist in a clone that was not pushed)
- Already on the corpus's own lists: no
- **Verifier:** confirmed with correction
- **Verifier's correction:** Only the documentary half could be checked, and it stands: checkpoints/README.md:70 says the tags run "`ToO-rev7` to `ToO-rev14`" while the other documents name `ToO-rev15`. "Three living documents" is short: REVIEWERS_GUIDE_README.md:73 names both tags, and narrative/theory-of-operation.md:2506 and narrative/glossary.md:1787 name `ToO-rev15`. The origin half (40 tags, neither tag present, the failing `git diff`, `REF-2026.10.01` absent) is NOT VERIFIED: no evidence file holds the `git ls-remote` output and the copy has no .git, so which side is stale is undetermined from the files. The tally should be recounted against the saved output before it is published: 9 + 16 + 1 + 8 plus the five glossary tags narrative/README.md:13-15 gives up to 2026.10.05 is 39, not 40, and index.tsv has 18 REF rows against sixteen REF tags with one absence named.
- **Verifier's evidence:** README.md:20 (quotation exact); narrative/README.md:9, :13-15; narrative/glossary.md:6, :13, :1787; checkpoints/README.md:69-70; REVIEWERS_GUIDE_README.md:73; narrative/theory-of-operation.md:2506; manifests/index.tsv:17 (`grep -c "^SHA256SUMS-REF-" manifests/index.tsv` = 18); `grep -rl "ToO-rev\|ls-remote\|refs/tags" evidence/` empty; the copy is not a git repository

### L-6: `Outstanding.tla`'s `CountExact` is proved and is a conjunct of `Safe`, and no row or mutation targets it
- Against: spec/Outstanding.tla:261-263 (and spec/Outstanding-rows.txt:4; decisions/ADR-0063.md:98)
- Basis: Proposed
- Claim: "CountExact == \A x \in Slots : slot[x].used <= slot[x].count" and "Safe == EffectsAfterRevocationBounded /\ HavocPlaneBoundedInEffects /\ SealedIsSpent /\ CountExact"
- Why wrong: `grep -c CountExact spec/Outstanding-rows.txt` returns 0. The rows file's six mutations are expected to break `EffectsAfterHonest`, `EffectsAfterPerGovernor`, `HavocPlaneBoundedInEffects` and `SealedIsSpent` (spec/Outstanding-rows.txt:4); none is expected to break `CountExact`, and no row checks it alone. ADR-0063 §3 states the property ("A lease never permits more entries than its count", decisions/ADR-0063.md:98). `M_NOCOUNT` exists, in `spec/Intent.tla`, for a different property (`EveryEffectHasALease`). So in this module the property has a proof and no behaviour showing it can fail, which is the case the corpus's mutation discipline exists to exclude.
- Fix belongs in: spec/Outstanding-rows.txt (a successor module's rows, since this one is cited by digest)
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed with correction
- **Verifier's correction:** decisions/ADR-0063.md:98 is in §4 ("What that bounds, with no premise about time", lines 92-107), not §3; the module's header also ties `CountExact` to §4. Otherwise as written: the proof module states `CountExactAlways` with "[no hypothesis]", so no mutation of the module breaks it, and no row checks it but as a conjunct of `Safe` in HOLDS rows.
- **Verifier's evidence:** spec/Outstanding.tla:261, :263 (quotations exact), :26-28, :78-97 (six mutations, none aimed at CountExact); `grep -c CountExact spec/Outstanding-rows.txt` = 0; spec/Outstanding-rows.txt:4 and its 40 rows (every VIOLATED mutation row names one of the four other properties); spec/Outstanding_proof.tla:7, :409; spec/Outstanding-proof-results-2026.11.10.txt:5, :10; spec/Intent-rows.txt:31 (M_NOCOUNT against EveryEffectHasALease); decisions/ADR-0063.md:92, :98; evidence/22-overlay-mutation-coverage.txt (Outstanding: "conjuncts no mutation breaks: ['CountExact']"); spec/README.md:209-210 ("every mutation fails its property ... non-vacuity and discrimination")

### L-7: Two Proposed records extend the trusted base by two conventions, and neither extension is in ADR-0045, the binding or the graph
- Against: decisions/ADR-0056.md:196-198 (and decisions/ADR-0045.md:25; decisions/ADR-0068.md)
- Basis: Proposed
- Claim: "| **T-0045-38** | A subject provider | trust root |" and "| **T-0045-39** | A downstream system's authorization, and any token service that mints for it | **excluded** |"
- Why wrong: ADR-0056 numbers its two rows in ADR-0045's series. ADR-0045's Pending line (decisions/ADR-0045.md:25) names A5, for ADR-0057, and A4; it names no amendment for ADR-0056, and `grep -c "T-0045-38" decisions/ADR-0045.md` returns 0, so the rows exist only in the Proposed record that uses them. ADR-0068 takes the other course and numbers twelve rows `T-0068-1` to `T-0068-12` in a series of its own, which no other file cites (evidence/21-trusted-base-namespaces.txt). ADR-0045 Annex A stops at T-0045-37. `spec/theorem-premise-binding.json` (dated 2026.10.06) and `spec/specification-graph.json` carry neither extension.
- Fix belongs in: ADR-0056 §8 or a pending amendment to ADR-0045; ADR-0068 §2
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed with correction; severity Low (reader: Low-Medium)
- **Verifier's correction:** (1) "which no other file cites" is wrong for files: `T-0068-n` appears in three diagrams and their generators (A5, E5, G4), and T-0045-38 and -39 in C10 and its generator. No other record cites either series, which is what evidence/21 searched. (2) Both absences are stated by the records themselves, so "already on the corpus's own lists: no" should read "in part": ADR-0056 §11 makes "The dependent entries are drafted", ADR-0045's among them, a ratification condition and marks it not met; ADR-0068 says "the row and assumption ids are the drafter's", sets aside "An annex to ADR-0045" as "Not taken while this is an overlay", and says what ADR-0045 would owe. What remains is the two conventions side by side, and that ADR-0056 uses ids in ADR-0045's series before ADR-0045 allocates them while ADR-0045's Pending line carries A5 for ADR-0057 and nothing for ADR-0056. Both records are Proposed, hence Low.
- **Verifier's evidence:** decisions/ADR-0056.md:196-198 (quotations exact), :14, :227-230; decisions/ADR-0045.md:25; `grep -c "T-0045-38" decisions/ADR-0045.md` = 0 and `grep -c "ADR-0056" decisions/ADR-0045.md` = 0; highest id in ADR-0045 is T-0045-37; decisions/ADR-0068.md:8, :13, :68, :120, :139; `grep -oE "T-0068-[0-9]+" decisions/ADR-0068.md | sort -u` gives 1 to 12; `grep -rlE "T-0068-[0-9]+" .` gives ADR-0068.md and six files under diagrams/topak/; `grep -rlE "T-0045-3[89]" .` gives ADR-0056.md and two files under diagrams/topak/; `grep -c "T-0045-38\|T-0045-39\|T-0068" spec/theorem-premise-binding.json spec/specification-graph.json` = 0 and 0; spec/theorem-premise-binding.json:3 (2026.10.06); evidence/21-trusted-base-namespaces.txt

### L-8: At this tree one recorded trace does not replay through `Mechanism.tla`, and the driver exits 0 with the ERROR row
- Against: spec/mechanism-trace-run.sh:22-27 (and spec/Mechanism-trace-results-2026.10.05.txt; checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:331)
- Basis: evidence
- Claim: "else r="ERROR"; fi" ... "exit 0"
- Why wrong: `spec/mechanism-trace-results.sh`, run in a clone at `bbda621`, gives 83 traces and 1,053 steps: 82 MATCH and one ERROR, `e2e_workflow_a_workflow_is_run_by_its_promotion_2` (39 steps), and exits 0 (evidence/14-mechanism-trace-regen.txt). The committed file of 2026.10.05 has 82 traces, 1,007 steps, all MATCH. G11 item 56 says trace validation "was not rerun" because `Mechanism.tla` does not model workflows; the rerun puts a number on it and shows the driver does not fail on it. The eighteen tests of `mechanism/crates/topak-core/tests/workflow.rs` are not among the suites the driver traces (spec/mechanism-trace-results.sh:20-25).
- Fix belongs in: spec/mechanism-trace-run.sh (status); spec/Mechanism.tla or a successor (G11 item 56)
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: G11 item 56 (the gap; not the exit status)
- **Verifier:** confirmed with correction
- **Verifier's correction:** The lines that fix the traced suites are spec/mechanism-trace-results.sh:19-24 (declared at :16), not 20-25. Otherwise as written. Not rerun here (cargo and TLC are out of scope); judged on evidence/14, where TLC stops at depth 10 of the 39-step trace and prints neither "No error has been found" nor "is violated", which the driver labels ERROR.
- **Verifier's evidence:** spec/mechanism-trace-run.sh:17-22, :27 (quotations exact); spec/mechanism-trace-results.sh:16, :19-24, :27-31; evidence/14-mechanism-trace-regen.txt:25-28, :78, :113 (82 MATCH, 1 ERROR, "83 traces · 1053 steps") and 14-mechanism-trace-regen.err ("exit 0"); spec/Mechanism-trace-results-2026.10.05.txt (82 MATCH lines, "82 traces · 1007 steps"); checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:331; `grep -c "#\[test\]" mechanism/crates/topak-core/tests/workflow.rs` = 18; `grep -ci workflow spec/Mechanism.tla` = 0

### L-9: `specification-graph.py check` cannot reproduce its committed result from a clean checkout: it pins two files that are not tracked
- Against: spec/specification-graph.py:519 (and floor/proposed/.gitignore:2; spec/specification-graph-results-2026.11.07.txt:9)
- Basis: Proposed
- Claim: "== Stale edges (§3, §8): 8 of 435"
- Why wrong: In a clean clone at `bbda621` the check reports "10 of 435" (evidence/04-spec-graph-check.txt). The two extra edges are "floor/proposed/control-tests.json 4247f94588f550f1 -> gone" and "floor/proposed/labels-tests.json 9877990b5ebeb101 -> gone". floor/proposed/.gitignore:2 ignores `*-tests.json` and re-admits only the `emergency` and `workflow` files, so the graph's pins on the other two are pins on build outputs of the author's working tree. After `python3 floor/proposed/build.py` the files exist again. The results file does not say the check needs that step.
- Fix belongs in: spec/specification-graph.py (pin tracked inputs only), or the results file's header
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed with correction
- **Verifier's correction:** The two edges are as stated. Scope: the same rerun differs from the committed file in a second place the finding does not mention, with a different cause. "the sync scripts: agrees" becomes "DISAGREES" (the eight overlay proof modules no edge reads) and the Result line becomes "FAILED: the sync scripts". So running build.py, or pinning tracked inputs only, restores the 8 stale edges at most and does not reproduce the committed result at bbda621. "After build.py the files exist again" was not rerun (no builds), and whether the rebuilt files match the two pins is not shown.
- **Verifier's evidence:** spec/specification-graph.py:516-520 (line 519 pins `{s}-tests.json`); floor/proposed/.gitignore:1-6; `ls floor/proposed/*-tests.json` gives emergency and workflow only; spec/specification-graph.json:3124, :3156; spec/specification-graph-results-2026.11.07.txt:9 (quotation exact), :93-94, :199; evidence/04-spec-graph-check.txt:9-14, :98-99, :204; `diff` of the committed results and the evidence file gives exactly three hunks; `grep -n "build\.py" spec/specification-graph-results-2026.11.07.txt` empty

### L-10: Regenerating the diagram family under its pinned interpreter changes four diagrams, and one overlay diagram is behind R2
- Against: diagrams/topak/H7-lean-route-2026.10.05.svg:1 (and diagrams/topak/B10-federation-floor-stage-2026.10.05.svg:1; decisions/ADR-0067.md:182)
- Basis: evidence
- Claim: (H7 as committed prints ADR-0053's digest as `e995fb0b221a96a8`)
- Why wrong: `skills/generating-corpus-diagrams/skills/*/scripts/regen_check.py`, run in a clean clone under Python 3.9.25, reports 48 of 52 unchanged and four "UNEXPECTED": G1, G3, H6 and H7 (evidence/12-diagram-regen-check.txt). H7's only change is the digest, now `0204367335e9989a`, because `decisions/ADR-0053.md` moved when its pending A1 was added on 2026.11.07. `grep -c FD15 diagrams/topak/B10-*.svg` returns 0 and `grep -c FD15 decisions/ADR-0067.md` returns 5: B10 was drawn before ADR-0067 R2 added `FD15-unattended-declared` (decisions/ADR-0067.md:182).
- Fix belongs in: diagrams/topak/src/ (H7, B10) and the family README
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed with correction
- **Verifier's correction:** The digest is at diagrams/topak/H7-lean-route-2026.10.05.svg:829 ("Sources: decisions/ADR-0053.md (Accepted, B36; e995fb0b221a96a8)"), not line 1. That the record's digest moved on 2026.11.07 cannot be checked without history; the files show A1 "drafted 2026.11.07" and today's digest `0204367335e9989a`. Otherwise as written: B10 and its generator name ADR-0067 "(Proposed, R1)" and "fourteen forbids", FD1 to FD14. Regeneration was not rerun; judged on evidence/12, which also gives the other three causes (G1: ADR-0045 A4 text; G3: premise-routes-results-2026.11.03; H6: counts). diagrams/README.md is absent from the copy and was not used.
- **Verifier's evidence:** evidence/12-diagram-regen-check.txt (52 regenerated under Python 3.9.25, 48 unchanged, UNEXPECTED G1, G3, H6, H7; H7's diff is the digest alone); diagrams/topak/H7-lean-route-2026.10.05.svg:829; `sha256sum decisions/ADR-0053.md | cut -c1-16` = 0204367335e9989a; decisions/ADR-0053.md:24; `grep -c FD15 diagrams/topak/B10-*.svg` = 0; `grep -c FD15 decisions/ADR-0067.md` = 5; decisions/ADR-0067.md:83, :182; diagrams/topak/src/d_b10*.py:1-3, :71; `ls diagrams/topak/*.svg | wc -l` = 52

### L-11: `tools/check-refs.py` prints a count that includes duplicates above a list that does not
- Against: tools/check-refs.py:49-51
- Basis: evidence
- Claim: "print(f"{title} ({len(rows)}):")" followed by "for f, p in sorted(set(rows)): print(f"  {f}: {p}")"
- Why wrong: At `bbda621` the script prints "MISSING paths (26):" and lists 24 lines, and "date tokens not 20YY.MM.DD (7):" and lists 6 (evidence/02-check-refs.txt). The header counts every occurrence and the list is de-duplicated, so the number a reviewer quotes from the header (the 10.02 review quoted "four missing paths") is not the number of lines shown.
- Fix belongs in: tools/check-refs.py
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed with correction
- **Verifier's correction:** The two quoted lines are tools/check-refs.py:45-46; lines 49-51 are the `-v` branch, whose else at :52 does print `len(set(moved))`. The aside that the 10.02 review quoted "four missing paths" could not be checked: that review is not in the copy.
- **Verifier's evidence:** tools/check-refs.py:45-46 (quotations exact), :52; evidence/02-check-refs.txt:1 ("MISSING paths (26):", 24 lines listed), :26 ("date tokens not 20YY.MM.DD (7):", 6 listed), counted with awk; `grep -rni "four missing paths" .` empty in the copy

