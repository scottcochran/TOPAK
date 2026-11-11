# Self review of 2026.11.11: reader E's findings in full

Reader E read the trusted base and the formal method. Annex to `derived/topak-open-findings-register-2026.11.11.md`, Part III. Each block is the finding as the reader wrote it, against the tree at `bbda621`, followed by the verdict of a verifier that did not find it. Paths are relative to the repository root. A path a finding names as absent is written without backticks. Nothing here is ratified, and every reader and verifier is of the same model lineage as the drafter of the corpus.

39 reported: 30 confirmed, 9 confirmed with a correction, 0 dropped.

### E-1: ADR-0045 §9 is marked met for "every row but T-0045-7, 21 and 26", but five rows in force (T-0045-32 to 36) are premises of no binding row, and T-0045-21 is a premise of one
- Against: decisions/ADR-0045.md:237 (and decisions/ADR-0045.md:22; spec/theorem-premise-binding.md:77; spec/theorem-premise-binding.json, `theorems[].rows`)
- Basis: in force
- Claim: "every row but T-0045-7 (the archive, whose theorems are ADR-0028's legibility classes, unmodelled), T-0045-21 and T-0045-26 is a premise of at least one row there."
- Why wrong: a script over the 43 table rows of `spec/theorem-premise-binding.md` (lines 39 to 81) and over `rows`, `rows_at_rung`, `base` and `derived` of the JSON gives, for both, "never cited: [7, 26, 32, 33, 34, 35, 36]". T-0045-32 to 36 (Annex A, decisions/ADR-0045.md:415-424, in force since B34) appear in no premise cell, and none of them says "no theorem cites it yet", which §9's third bullet requires of an uncited row. T-0045-21 is cited: spec/theorem-premise-binding.md:77 names "**T-0045-16 to 22** (confinement at the declared rung)" and the JSON row "Effect exclusivity" has `"3": ["T-0045-16", "T-0045-17", "T-0045-20", "T-0045-21"]`. The status note repeats the stale list, decisions/ADR-0045.md:22-23: "the three rows no theorem cites (T-0045-7, 21, 26)". T-0045-15 says "Cited by no theorem until ADR-0035 is ratified" (decisions/ADR-0045.md:377) while spec/theorem-premise-binding.md:78 cites "T-0045-15 (the lineage tools, for A2.2)".
- Fix belongs in: decisions/ADR-0045.md (status note, §9, the residuals of T-0045-32 to 36) or spec/theorem-premise-binding.md and .json (rows for the label, tool-list and operator properties)
- Severity: Medium
- Confidence: high
- Already on the corpus's own lists: G11 item 90 in part (it lists the modules with no binding rows, not the trusted-base rows left uncited)
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0045.md:236-239 (claim, exact), :22-23, :377, :398, :409, :415-424 (rows 32 to 36: none says 'no theorem cites it yet'); spec/theorem-premise-binding.md:77-78; spec/theorem-premise-binding.json:960-971 (rung 3 lists T-0045-21). Reran a script over table lines 39-81 and over the JSON's rows, rows_at_rung, base and derived: never cited = [7, 26, 32, 33, 34, 35, 36] in both. `grep -n 'T-0045-3[2-6]' spec/theorem-premise-binding.md` empty. ADR-0035 is Proposed (decisions/ADR-0035.md:11).

### E-2: Annex B keeps T-0045-24 "excluded until the tool host reads the entry", and the same annex says the tool host reads the entry
- Against: decisions/ADR-0045.md:482 (and decisions/ADR-0045.md:454; decisions/ADR-0033.md:1157; mechanism/GAPS-AND-ASSUMPTIONS.md:103)
- Basis: in force
- Claim: "the target is read from node configuration and not from the entry, and nothing compares the two (G19). The class here stays excluded until the tool host reads the entry"
- Why wrong: decisions/ADR-0045.md:454, in the same annex: "The allowlist data is in ADR-0049's form, and a Wasm tool's target is read from the entry (I33, I44)." decisions/ADR-0033.md:1157 (A9, ratified Batch 32, 2026.10.05): "node configuration says nothing of a Wasm tool's channel, the target is the entry's in the bundle revision the lease names". mechanism/GAPS-AND-ASSUMPTIONS.md:103 (I44): "**The target is the allowlist entry's, in the bundle revision the lease names** (2026.10.05". The condition the row names for leaving `excluded` has been met since 2026.10.05 and the class column still reads `excluded`; no history row after B30 revisits it.
- Fix belongs in: decisions/ADR-0045.md Annex B (T-0045-24), by the ADR-0033 addendum the annex says revises it
- Severity: Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed with correction
- **Verifier's correction:** The line 'Already on the corpus's own lists: no' is wrong. ADR-0033's A9 addendum body says it outright: 'The reason ADR-0045 Annex B gives for keeping T-0045-24 excluded at the reference, that it reads the target from node configuration, no longer holds; the row is ADR-0045's to move and is not moved here' (decisions/ADR-0033.md:603-605). The defect and its direction stand: ADR-0045 has not moved or reworded the row since.
- **Verifier's evidence:** decisions/ADR-0045.md:482 (claim, exact; Class cell 'excluded'), :454, :522 (B30, the last History row on T-0045-24); decisions/ADR-0033.md:1157-1158 (A9, ratified B32), :603-605; mechanism/GAPS-AND-ASSUMPTIONS.md:103, :139. `grep -n 'T-0045-24' checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md` empty.

### E-3: Annex B's T-0045-6 note says ADR-0044 is not implemented and the bundle is unsigned; ADR-0044 and Annex B's own T-0045-27 say it was built on 2026.10.01
- Against: decisions/ADR-0045.md:470 (and decisions/ADR-0045.md:485; decisions/ADR-0044.md:106)
- Basis: in force
- Claim: "Bundle unsigned: ADR-0044 not implemented, so the bundle itself is an **excluded** instance of its promotion until then"
- Why wrong: decisions/ADR-0044.md:106: "**Built 2026.10.01** (ADR-0033 A6, Batch 23): `load_dir` verifies under the rules' keys; `decide` and the grant path refuse an unverified revision". decisions/ADR-0045.md:485 (T-0045-27, same annex): "~~None: bundles are unsigned~~ The dev bundle key, generated by `dev-init.sh` into `dev/secrets/`, signing a copy of the built bundle". B23 (decisions/ADR-0045.md:516) changed T-0045-27 and left T-0045-6's note as it was.
- Fix belongs in: decisions/ADR-0045.md Annex B (T-0045-6)
- Severity: Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0045.md:470 (claim, exact, unstruck), :485 (T-0045-27 struck and rewritten at B23), :516 (B23 changes T-0045-27 only); decisions/ADR-0044.md:106, :115; decisions/ADR-0033.md:476-478.

### E-4: ADR-0046 §3 still says the prover's defects are not reported upstream; its own open obligation and ADR-0045 Annex B say they were reported on 2026.10.18
- Against: decisions/ADR-0046.md:265 (and decisions/ADR-0046.md:473; decisions/ADR-0045.md:489)
- Basis: in force
- Claim: "The defects are not reported upstream yet (the custodian's decision, 2026.10.07)."
- Why wrong: decisions/ADR-0046.md:473-475: "~~on 2026.10.07 the custodian decided not yet~~ reported 2026.10.18 by the custodian, as tlaplus/tlapm#309 ... and #310". decisions/ADR-0045.md:489: "**Both cases are reported upstream** ⟨A4⟩ ⟨B39⟩ (tlaplus/tlapm#309 and #310, 2026.10.18; ADR-0046 A3)". A3 (decisions/ADR-0046.md:513) struck the clause in Open obligations only and says "No decision text changes", so the §3 sentence, which is decision text under ⟨A2⟩, stands unstruck beside its contradiction. G11 item 104 (checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:351) also says "The defects are unreported upstream", which was true at the cut.
- Fix belongs in: decisions/ADR-0046.md §3 (the A2 text); the next checkpoint's item 104
- Severity: Medium
- Confidence: high
- Already on the corpus's own lists: G11 item 104 states the superseded position; the contradiction itself is not listed
- **Verifier:** confirmed; severity Low-Medium (reader: Medium)
- **Verifier's evidence:** decisions/ADR-0046.md:265 (claim, exact, unstruck, in the A2 text of section 3), :473-474 (struck in Open obligations only), :513 (A3: 'No decision text changes'); decisions/ADR-0045.md:489; checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:351. Severity lowered: one fact (whether the report was made) is stale in one sentence and nothing rests on it.

### E-5: "thirteen of its proof modules, including the three its A1 does not certify" miscounts against ADR-0046's own thirteen
- Against: decisions/ADR-0053.md:315 and decisions/ADR-0046.md:508 (and decisions/ADR-0046.md:178-180, 326; decisions/ADR-0053.md:464)
- Basis: in force
- Claim: "theorems of ~~twelve~~ ⟨R8⟩ thirteen of its proof modules, including the ~~two~~ ⟨R8⟩ three its A1 does not certify"
- Why wrong: "its" is ADR-0046's. ADR-0046 §4 cites thirteen proof modules, `RunCoupling_proof.tla` among them (decisions/ADR-0046.md:326), and ADR-0053 lists `RunCoupling` first among "**The modules not yet encoded**" (decisions/ADR-0053.md:464). The thirteenth module encoded is `Confinement_A1`, which ADR-0046 places "Outside the thirteen modules this record cites" (decisions/ADR-0046.md:178-180). So the Lean route covers twelve of ADR-0046's thirteen plus one module outside them, and of the thirteen ADR-0046 cites its A1 leaves two uncertified (decisions/ADR-0046.md:173-174), not three. ADR-0046's B36 row repeats it: "a second derivation of the theorems of thirteen of this record's proof modules, among them the three its A1 does not certify (`RulesFloorNV_rev5`, `Confinement`, `Confinement_A1`)" (decisions/ADR-0046.md:508). The derived-premise table agrees with the count of twelve: `invariant(RunCoupling)` has the single route T-0045-31 (spec/theorem-premise-binding.md:103).
- Fix belongs in: decisions/ADR-0053.md §6; decisions/ADR-0046.md History B36
- Severity: Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed; severity Low-Medium (reader: Medium)
- **Verifier's evidence:** decisions/ADR-0053.md:314-315 (claim, exact), :179 (the thirteen proof modules encoded: Confinement_A1 in, RunCoupling out), :464; decisions/ADR-0046.md:162-174 (A1's thirteen, two not certified), :178-180 ('Outside the thirteen modules this record cites ... Confinement_A1_proof.tla ... does not'), :315-327, :508; spec/theorem-premise-binding.md:98, :103. Severity lowered: section 4's table and the binding carry the right set; the miscount is in the dependent-entry wording and one History row.

### E-6: T-0045-37's identity and replay are claimed of "every Lean results file"; five of the sixteen, three of them cited by digest in ADR-0053 §4, print no kernel, `leanchecker` or Lake digest and carry no replay
- Against: decisions/ADR-0045.md:387 and decisions/ADR-0045.md:490 (and decisions/ADR-0053.md:136, 164, 170, 180, 182, 183, 186)
- Basis: in force
- Claim: "its digests are in every Lean results file from 2026.10.05, and `tools/lean-sync.sh` refuses a results file that names another kernel. Every results file regenerates byte for byte"
- Why wrong: `grep -c 'libleanshared (sha256'` over the sixteen `*-results-*.txt` under `spec/lean`, `mechanism/lean` and `floor/lean` gives 0 for `spec/lean/GraphCheck-results-2026.10.06.txt`, `GraphCheck-results-2026.10.07.txt`, `GraphCheckEmergency-results-2026.10.07.txt`, `mechanism/lean/SeatsReplay-results-2026.10.06.txt` and `CouplingReplay-results-2026.10.06.txt`; the same five give 0 for `leanchecker (sha256`, for `Lake version` and for `^Replay:`. Their headers name only "Lean (version 4.33.1, arm64-apple-darwin24.6.0, commit 819816b…" (spec/lean/GraphCheck-results-2026.10.06.txt:4; mechanism/lean/SeatsReplay-results-2026.10.06.txt:2). Annex A's row says the digests are "printed in every Lean results file" (decisions/ADR-0045.md:387) and ADR-0053 §2 says "every results file carries a **replay**" (decisions/ADR-0053.md:136). On byte-for-byte, ADR-0053 §4 itself says "The trace replay is not regenerated byte for byte, since its trace names carry process ids" (decisions/ADR-0053.md:186). The graph-check file is the one the binding takes `enc-faithful(Seats)` and `enc-faithful(FloorComposition)` from (spec/theorem-premise-binding.md:113, 117).
- Fix belongs in: decisions/ADR-0053.md §2, §3 and its dependent rows in decisions/ADR-0045.md (T-0045-37, Annex A and B); or the graph-check and replay drivers
- Severity: Medium
- Confidence: high on the files; medium on whether the records mean the graph-check and replay files by "Lean results file" (§4's table, headed "The Lean results are cited by digest", lists them)
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** Reran the four greps over the sixteen *-results-*.txt under spec/lean, mechanism/lean, floor/lean: 0 for 'libleanshared (sha256', 'leanchecker (sha256', 'Lake version' and '^Replay:' in GraphCheck-results-2026.10.06, -10.07, GraphCheckEmergency-results-2026.10.07, SeatsReplay-results-2026.10.06, CouplingReplay-results-2026.10.06; 1 each in the other eleven. decisions/ADR-0045.md:387, :490 (claim, exact); decisions/ADR-0053.md:136, :170, :180-183, :186 ('The trace replay is not regenerated byte for byte'); tools/lean-sync.sh:50-56 (kernel compared only for each package's newest proof results); spec/theorem-premise-binding.md:113, :117.

### E-7: ADR-0053 §4 cites the code the `mechanism/lean` results are stated from by digests the tree no longer has, and says a move is "never a silent drift"
- Against: decisions/ADR-0053.md:191 (and decisions/ADR-0053.md:181, 182)
- Basis: in force
- Claim: "they follow code and a floor that move, and a move is a regenerated results file, never a silent drift."
- Why wrong: `sha256sum` on the tree: `mechanism/crates/topak-core/src/state.rs` = `e6a927a19935e329` (cited `25eeeeb3830ee9f8`), `types.rs` = `9052f7a910657449` (cited `6524de30f4ada72a`), `rules.rs` = `2f869fec373905f7` (cited `94b543971af7b9ba`), `trace.rs` = `2b8c59b4b03e6d89` (cited `5056e2da471b18a8`), `mechanism/crates/topak-floor/src/lib.rs` = `93f01304236d3708` (cited `0f280725956a15b4`); `mechanism.rs` = `0c6ff1f0fc89c845` against `ba754394b045a1db` in mechanism/lean/Admit-results-2026.10.06c.txt:2. The newest results under `mechanism/lean` are still the 2026.10.06 files §4 cites; none was regenerated. The route `refines(Seats)` and the code-level theorems of §4 therefore describe a tree that is not the reference's. The record in force says nothing of it; only its pending A1 does (decisions/ADR-0053.md:291-292, not in force).
- Fix belongs in: decisions/ADR-0053.md §4 (or `mechanism/lean` regenerated); the binding's `model-faithful(apply/Seats)` text
- Severity: Medium
- Confidence: high
- Already on the corpus's own lists: G11 item 103; `mechanism/` I49
- **Verifier:** confirmed
- **Verifier's evidence:** sha256sum reproduced: state.rs e6a927a19935e329, types.rs 9052f7a910657449, rules.rs 2f869fec373905f7, trace.rs 2b8c59b4b03e6d89, topak-floor/src/lib.rs 93f01304236d3708, topak-node/src/mechanism.rs 0c6ff1f0fc89c845, against decisions/ADR-0053.md:181-183 and mechanism/lean/Admit-results-2026.10.06c.txt:2. decisions/ADR-0053.md:191-192 (claim, exact), :291-292 (pending A1 only). `ls mechanism/lean`: newest results are the 2026.10.06 files. checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:350 (item 103, lean-sync exits 1).

### E-8: The binding table still marks ADR-0033 A7 and ADR-0034 A2 as pending and ADR-0042 §6 as Proposed; all three were ratified on 2026.10.04
- Against: spec/theorem-premise-binding.md:62 (and :3, :58-61, :77, :81; spec/theorem-premise-binding.json `premises.run-confinement-delivered`)
- Basis: living document
- Claim: "**pending**: A2 is not ratified. The reference holds Run tools hosted as Wasm modules to their target (`mechanism/` I44) and refuses a native tool under a P4-pass Run lease (I43), uncommitted"
- Why wrong: decisions/ADR-0045.md:522: "ADR-0034 A2, ratified 2026.10.04 in Batch 30"; decisions/ADR-0045.md:521: "ADR-0033 A7, ratified 2026.10.04 in Batch 29"; decisions/ADR-0042.md:13: "**whole, §6 since 2026.10.04** ⟨B30⟩"; mechanism/GAPS-AND-ASSUMPTIONS.md:102: "**both ratified 2026.10.04 (Batch 30)**". The table's header (line 3) says "**pending** ADR-0033 A7", rows 58 to 61 and 81 end "(pending ADR-0033 A7)", row 62 is headed "(**pending** ADR-0034 A2)" and names "ADR-0042 §6 in force (Proposed)", row 77 says "(ADR-0042 §6, Proposed)", and the JSON column's text is "Run's confinement delivered, ADR-0042 §6 in force (Proposed)". The file's digest, `8fc5629220aaa173`, is the one G11 measured (checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:194), so it has not been revised since.
- Fix belongs in: spec/theorem-premise-binding.md and .json
- Severity: Medium
- Confidence: high
- Already on the corpus's own lists: no (G11 item 90 is about missing rows)
- **Verifier:** confirmed with correction
- **Verifier's correction:** One supporting quotation: row 81 does not end '(pending ADR-0033 A7)'. Its cell reads '(`Mechanism-trace-results-2026.10.02.txt`, pending ADR-0033 A7; 21 traces at A5)'. Rows 58 to 61 end as quoted. Nothing else changes.
- **Verifier's evidence:** spec/theorem-premise-binding.md:3, :58-62 (62: claim, exact), :77, :81; spec/theorem-premise-binding.json:134; decisions/ADR-0045.md:521-522; decisions/ADR-0042.md:13; decisions/ADR-0034.md:512; mechanism/GAPS-AND-ASSUMPTIONS.md:102. `sha256sum spec/theorem-premise-binding.md` = 8fc5629220aaa173, as checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:194.

### E-9: "One row per checked property" and "`invariant(M)` for every proof module" hold for 15 of the 32 proof modules in the tree
- Against: decisions/ADR-0053.md:268 and spec/theorem-premise-binding.md:5 (and decisions/ADR-0045.md:144; spec/README.md:233-234; decisions/ADR-0046.md:315)
- Basis: in force (ADR-0053 §5, ADR-0045 §3) and living document
- Claim: "`invariant(M)` for every proof module: T-0045-31, or T-0045-37 and `enc-faithful(M)`, the latter for the thirteen encoded modules."
- Why wrong: `ls spec/*_proof.tla | wc -l` gives 32. `grep -c <Module>_proof.tla spec/theorem-premise-binding.md` gives 0 for `Alone`, `BreakGlass_A1`, `Correlator`, `Coupling_live`, `Emergency`, `Emergency_live`, `Federation`, `Intent`, `Labels`, `Membership`, `NonComposition_A1`, `Operators`, `Outstanding`, `Peer`, `PlaneClock`, `Release` and `ToolList`. The derived table (spec/theorem-premise-binding.md:90-104) defines `invariant(M)` for fifteen modules; seven proof modules that existed when ADR-0053 was ratified on 2026.10.06 (`Labels`, `ToolList`, `Operators`, `Correlator`, `Emergency`, `BreakGlass_A1`, `NonComposition_A1`, all in decisions/ADR-0053.md:464-465) have none. spec/README.md:233-234 says the table is "for every property above". One theorem ADR-0046 §4 cites as proved, "`EpochMonotone` unconditionally" (decisions/ADR-0046.md:315), has no row (`grep -c EpochMonotone` = 0 in the table and the JSON). ADR-0045 §3 says "one row per checked property" (decisions/ADR-0045.md:144).
- Fix belongs in: spec/theorem-premise-binding.md and .json; the sentence in decisions/ADR-0053.md §5; spec/README.md
- Severity: Medium
- Confidence: high
- Already on the corpus's own lists: G11 item 90 in part (it names ten modules; `Correlator`, the eight modules of 2026.11.10 and `EpochMonotone` are not on it)
- **Verifier:** confirmed
- **Verifier's evidence:** `ls spec/*_proof.tla | wc -l` = 32. `grep -c <M>_proof.tla` in the binding .md and .json is 0 for the seventeen modules named (Alone, BreakGlass_A1, Correlator, Coupling_live, Emergency, Emergency_live, Federation, Intent, Labels, Membership, NonComposition_A1, Operators, Outstanding, Peer, PlaneClock, Release, ToolList). `grep -c EpochMonotone` = 0 in both. spec/theorem-premise-binding.md:5, :90-104 (fifteen invariant(M)); decisions/ADR-0053.md:268-269 (claim, exact), :464-465; decisions/ADR-0045.md:144; decisions/ADR-0046.md:315; spec/README.md:233; G11:338 (item 90).

### E-10: The binding's inventory paragraph says the bundle's revision is a file name; its own row says the revision is verified
- Against: spec/theorem-premise-binding.md:131 (and :45)
- Basis: living document
- Claim: "the bundle's revision is a file name; the reach bound is declared and not enforced."
- Why wrong: spec/theorem-premise-binding.md:45, last column of `BundleRefusalHonored`: "**holds**; the revision is verified under the dev bundle key since 2026.10.01 (ADR-0033 A6)". decisions/ADR-0045.md:516 (B23): "`BundleRefusalHonored`'s revision is now verified rather than a file name (binding table)". The paragraph ends "That is ADR-0045 Annex B's inventory sentence, computed", so the stale clause is presented as the computed inventory.
- Fix belongs in: spec/theorem-premise-binding.md
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** spec/theorem-premise-binding.md:131 (claim, exact), :45 (last cell: 'the revision is verified under the dev bundle key since 2026.10.01'), :134; decisions/ADR-0045.md:516.

### E-11: Annex B is headed "at `fb40db1`", its ratification row says it was written against `8cf9bd1`, and its rows describe trees up to 2026.10.05; the reference is at A17
- Against: decisions/ADR-0045.md:441 (and decisions/ADR-0045.md:514, 479, 447, 456; decisions/ADR-0033.md:1144, 1146, 1170)
- Basis: in force
- Claim: "## Annex B : The reference's declaration, at `fb40db1`"
- Why wrong: decisions/ADR-0045.md:514 (B22): "Annex B is written against `8cf9bd1` (ADR-0033 A5)". `fb40db1` is A4's tree and `8cf9bd1` A5's (decisions/ADR-0033.md:1144, 1146). Inside the annex, line 479 speaks of "the reference at `c536e21` and after", and lines 447 and 456 of instances "since 2026.10.05" (ADR-0033 A10, A11). ADR-0033's newest ratified addendum cites `749d54f` (decisions/ADR-0033.md:1170, A17, 2026.10.09). The annex says of itself "It changes with the reference, by ADR-0033 addendum" (decisions/ADR-0045.md:444-445) and the open obligation says "each ADR-0033 addendum that changes the reference's trusted base revises it" (decisions/ADR-0045.md:335); no history row records a revision for A8, A9 or A12 to A17. A reader cannot tell which tree the declaration is of.
- Fix belongs in: decisions/ADR-0045.md Annex B (heading, and the rows E-2, E-3, E-12 and E-13 name)
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: no (G11 item 56 covers trace validation being behind the tree, not the annex)
- **Verifier:** confirmed with correction
- **Verifier's correction:** A16 and A17 are Pending, not ratified (decisions/ADR-0033.md:1169-1170: 'Takes force only with ADR-0054's ... ratification'); ADR-0033's status line stops at B36. The newest ratified addendum is A15 at `075b2e7` (line 1166; B35, 2026.10.05). Read 'the reference is at A17' as 'the tree is at the commit pending A17 cites', and the unrecorded revisions as A8, A9 and A12 to A15. The heading against B22 (`fb40db1` against `8cf9bd1`) and the rows describing later trees stand.
- **Verifier's evidence:** decisions/ADR-0045.md:441 (claim, exact), :444-445, :335, :447, :456, :479, :514, :521-525 (History after B22 names A7, ADR-0034 A2, A10 to A12 only); decisions/ADR-0033.md:10, :1144, :1146, :1166-1170.

### E-12: Three layers give three counts for stage 1's evidence, and Annex B's is the oldest: 21 traces and ten pinned modules against 82 traces and nineteen
- Against: decisions/ADR-0045.md:486 (and decisions/ADR-0045.md:474; spec/theorem-premise-binding.md:81)
- Basis: in force
- Claim: "pinned to ten modules in `corpus-pins.sha256`; 55 tests restating the TLC properties; **every test's recorded behaviour replayed through `spec/Mechanism.tla`** (`Mechanism-trace-results-2026.09.30.txt`: 21 traces, 163 steps, all matching)"
- Why wrong: `grep -c "spec/.*\.tla" mechanism/corpus-pins.sha256` gives 19. spec/Mechanism-trace-results-2026.10.05.txt:97: "82 traces · 1007 steps"; spec/theorem-premise-binding.md:81 gives a third figure, "57 traces, 642 steps match" from the 2026.10.02 file, still marked "pending ADR-0033 A7". Annex B's T-0045-11 still reads "This corpus at Batch 20, pinned" (decisions/ADR-0045.md:474) with the record itself amended through Batch 39. The sentence "every test's recorded behaviour replayed" is also contradicted for the current tree by the checkpoint: "**Stage one is behind the tree**: `Mechanism.tla` does not model workflows, and trace validation was not rerun (A16, A17)" (checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:331).
- Fix belongs in: decisions/ADR-0045.md Annex B (T-0045-28, T-0045-11); spec/theorem-premise-binding.md row `TraceMatches`
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: G11 item 56 (for the rerun only)
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0045.md:486 (claim, exact), :474; spec/theorem-premise-binding.md:81. `grep -c "spec/.*\.tla" mechanism/corpus-pins.sha256` = 19. spec/Mechanism-trace-results-2026.09.30.txt:32 (21 traces, 163 steps), -2026.10.02.txt:70 (57, 642), -2026.10.05.txt:97 (82, 1007); G11:331.

### E-13: Annex B says "Every lease is rung 0" and, in the same cell, that the node launches at rung 1 and fills T-0045-19 and T-0045-20; the inventory sentence still counts 16 to 21 as excluded or absent
- Against: decisions/ADR-0045.md:479 (and decisions/ADR-0045.md:492; spec/theorem-premise-binding.md:61)
- Basis: in force
- Claim: "None. Every lease is rung 0"
- Why wrong: the same cell continues, unstruck: "**Since ADR-0033 A7 (B29), the reference at `c536e21` and after** ⟨B29⟩: the node launches at rung 1, on a host process ... filling T-0045-19 (whoever runs the node, and the node's launcher) and T-0045-20 (the image by digest and its declared profile)". The inventory paragraph (decisions/ADR-0045.md:492) was not changed: "With T-0045-13, 16 to 21, 22, 23 and 24 excluded or absent". The binding's last column already uses the rung-1 instance: `FreshAppraisal` "**holds** at rung 1, where the launcher appraises" (spec/theorem-premise-binding.md:61). The first sentence was superseded by appending, not by striking, so the cell asserts both.
- Fix belongs in: decisions/ADR-0045.md Annex B (the T-0045-16 to 21 row; the inventory paragraph)
- Severity: Low-Medium
- Confidence: medium
- Already on the corpus's own lists: no
- **Verifier:** confirmed with correction
- **Verifier's correction:** Not 'the same cell'. 'None. Every lease is rung 0' is the row's Instance cell; the 'Since ADR-0033 A7 (B29)' text is the Note cell of the same row (decisions/ADR-0045.md:479). The conflict is between two cells of one row: B29 (line 521) appended to the note and struck nothing.
- **Verifier's evidence:** decisions/ADR-0045.md:479, :492-493 ('16 to 21 ... excluded or absent'), :521; spec/theorem-premise-binding.md:59, :61.

### E-14: Annex A declares its archetype version as "the corpus at Batch 20" and carries rows added at Batches 24, 25, 34 and 36
- Against: decisions/ADR-0045.md:350 (and decisions/ADR-0045.md:168-169, 515, 517, 524, 525)
- Basis: in force
- Claim: "Archetype version: the corpus at Batch 20 (2026.09.30)."
- Why wrong: §4 makes the version load-bearing: "**Annex A carries the archetype version it belongs to**, and the non-increasing-TCB rule is checked row set against row set across versions" (decisions/ADR-0045.md:168-169). The row set under that version label has grown since: T-0045-31 at B25 (line 517), T-0045-32 to 36 at B34 (line 524), T-0045-37 at B36 (line 525), and T-0045-14 changed class at B24 (line 515). G11 counts "**In force, thirty-seven rows**, up from thirty-six" (checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:144). A row-set comparison "across versions" has one version name for at least four row sets.
- Fix belongs in: decisions/ADR-0045.md Annex A (the version line), or the archetype-evolution record the annex defers to
- Severity: Low-Medium
- Confidence: medium
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0045.md:350 (claim, exact), :168-169, :515, :517, :518, :523-525; checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:144. No other version line: `grep -n 'Archetype version' decisions/ADR-0045.md` gives line 350 only.

### E-15: T-0045-33's Layer is `policy`, which is not one of the four values §1 fixes
- Against: decisions/ADR-0045.md:416 (and decisions/ADR-0045.md:88)
- Basis: in force
- Claim: "| **T-0045-33** | The label and destination declarations in the allowlist entry and the Run root, and the task's label in the grant (ADR-0047 §1; ADR-0049 §4) | policy | Nothing | all | excluded |"
- Why wrong: decisions/ADR-0045.md:88: "| **Layer** | `mechanism-boundary`, `substrate`, `toolchain` or `people`" under "The schema is fixed so that rows are comparable across deployments and across archetype versions" (lines 82-83). A1's history row (line 518) records no schema change. T-0045-19 and T-0045-35 use "people / substrate", two listed values; `policy` is not listed at all.
- Fix belongs in: decisions/ADR-0045.md (Annex A row, or §1's Layer field)
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0045.md:416 (claim, exact), :82-83, :88, :518. Listed the Layer cell of all 37 Annex A rows with awk: `policy` occurs once, at T-0045-33; every other value is one of the four, or 'people / substrate' (T-0045-19, T-0045-35).

### E-16: ADR-0046 §3 cites three proof modules with digests that are their certified results files', not the modules'
- Against: decisions/ADR-0046.md:179 (and :180)
- Basis: in force
- Claim: "`RunConfinement_proof.tla` (`823ae3479ef38845`) and `Operators_proof.tla` (`9be0fe30c2c1cab9`, as regenerated at ADR-0050 R5;"
- Why wrong: `sha256sum spec/RunConfinement_proof.tla spec/Operators_proof.tla spec/Confinement_A1_proof.tla` gives `e8612bf4111c7599`, `226230ef1e56b413`, `63c7d90a7fc2ccf8` (the same values every results file prints on its `Modules:` line, e.g. spec/Operators-proof-cert-results-2026.10.04.txt:2). The three digests in the text are those of `spec/RunConfinement-proof-cert-results-2026.10.04.txt` (`823ae3479ef38845`), `spec/Operators-proof-cert-results-2026.10.04.txt` (`9be0fe30c2c1cab9`) and `spec/Confinement_A1-proof-cert-results-2026.10.04.txt` (`f4ffce6861f24e77`). In §4 of the same record the form "`Anchor_proof.tla` (`8a482305f19d8bbd`)" is the module's digest, so a reader checking the citation as written finds a mismatch.
- Fix belongs in: decisions/ADR-0046.md §3 (the A1 paragraph)
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** sha256sum reproduced: spec/RunConfinement_proof.tla e8612bf4111c7599, Operators_proof.tla 226230ef1e56b413, Confinement_A1_proof.tla 63c7d90a7fc2ccf8; their -proof-cert-results-2026.10.04.txt 823ae3479ef38845, 9be0fe30c2c1cab9, f4ffce6861f24e77. decisions/ADR-0046.md:179-180 (claim, exact), :315 (`Anchor_proof.tla` 8a482305f19d8bbd is the module's own digest); spec/Operators-proof-cert-results-2026.10.04.txt:2.

### E-17: ADR-0046 §3 still calls ADR-0050 Proposed
- Against: decisions/ADR-0046.md:180
- Basis: in force
- Claim: "ADR-0050, Proposed) certify"
- Why wrong: decisions/ADR-0050.md:20: "**Status:** Accepted (genesis) · provisional · 2026.10.05 · confirmation required (ADR-0029 C1, C3, C4; provisional under A4) ⟨B34⟩".
- Fix belongs in: decisions/ADR-0046.md §3
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0046.md:180 (claim, exact); decisions/ADR-0050.md:20.

### E-18: The three method documents give statuses that were true on 2026.10.04: four accepted records are "Proposed", three ratified amendments "pending"
- Against: spec/README.md:26 (and spec/README.md:27-32, 48, 138-143; spec/proof-method.md:61-65; spec/proof-certification.md:664)
- Basis: living document
- Claim: "| `Emergency.tla` | ADR-0052 §9 (Proposed) |"
- Why wrong: decisions/ADR-0052.md:18 and decisions/ADR-0050.md:20: "Accepted (genesis) · provisional · 2026.10.05"; decisions/ADR-0047.md:19 and decisions/ADR-0048.md:15: "Accepted (genesis) · 2026.10.05". spec/README.md calls ADR-0048, ADR-0050 and ADR-0047 Proposed at lines 29, 30 and 32 (and again at 141 to 143), and line 48 says "labels, operators and the emergency seating, all Proposed"; line 34 of the same file already has "ADR-0052 §9 (provisional, B34)". Lines 27-28 and 139-140 say "ADR-0026 A2 (pending)" and "ADR-0013 §4, A1 (pending)"; decisions/ADR-0026.md:13 has A2 "ratified 2026.10.05 (Batch 34) and applied inline" and decisions/ADR-0013.md:9 reads "**Pending:** none". spec/proof-method.md:61 has "ADR-0034 A2 pending" (ratified Batch 30, decisions/ADR-0045.md:522) and lines 62 to 65 "ADR-0052 Proposed", "ADR-0047 Proposed", "ADR-0048 Proposed", "ADR-0050 Proposed". spec/proof-certification.md:664: "ADR-0047, 0048, 0050, 0052 (Proposed)". ADR-0051 is Proposed (decisions/ADR-0051.md:14), so that one label is right.
- Fix belongs in: spec/README.md; spec/proof-method.md; spec/proof-certification.md
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** spec/README.md:26 (claim, exact), :27-30, :32, :34, :48, :138-143; spec/proof-method.md:61-65; spec/proof-certification.md:664; decisions/ADR-0047.md:19, ADR-0048.md:15, ADR-0050.md:20, ADR-0052.md:18, ADR-0051.md:14 (Proposed, so that label is right); decisions/ADR-0026.md:13; decisions/ADR-0013.md:9; decisions/ADR-0045.md:522.

### E-19: "Each proof module also proves `Safe`" is false of two of the thirteen
- Against: decisions/ADR-0046.md:329
- Basis: in force
- Claim: "Each proof module also proves `Safe`, the module's conjunction, under `Mut = "none"`"
- Why wrong: `grep -c "Safe" spec/Anchor_proof.tla spec/BreakGlass.tla spec/BreakGlass_proof.tla` gives 0, 0, 0; `spec/Anchor.tla` has the string once, inside the word "Safety" in a header comment (line 7), and defines no `Safe`. spec/Anchor-proof-results-2026.10.02.txt:5: "Theorems: FloorPreservedAlways · EpochMonotoneAlways". spec/BreakGlass_proof.tla:64 has one theorem, `NeverChangesAuthority`. Eleven of the thirteen prove a `SafeAlways`.
- Fix belongs in: decisions/ADR-0046.md §4
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0046.md:329 (claim, exact). `grep -c Safe spec/Anchor_proof.tla spec/BreakGlass.tla spec/BreakGlass_proof.tla` = 0, 0, 0; spec/Anchor.tla:7 ('Safety', in a comment). spec/Anchor-proof-results-2026.10.02.txt:5; spec/BreakGlass-proof-results-2026.10.02.txt:5; spec/BreakGlass_proof.tla:64. `grep -c 'THEOREM SafeAlways'` is non-zero in the other eleven.

### E-20: For `FloorRouting` the proved hypotheses are not the "Breaks under" column: both theorems are proved under `Mut = "none"` only
- Against: decisions/ADR-0046.md:340 (and spec/theorem-premise-binding.md:25, 47, 48; spec/proof-method.md:27)
- Basis: in force
- Claim: "**Every hypothesis in the last column is a floor entry, a mechanism setting or a mutation's absence**, and is the "Breaks under" column of the premise table restated as a theorem's premise. Where the two disagree, §5 corrects the table"
- Why wrong: spec/FloorRouting_proof.tla:59-60 and :64-65: `THEOREM NoWideningAlways ==` / `ASSUME Mut = "none"` and `THEOREM NeverVacuousAlways ==` / `ASSUME Mut = "none"`. The module has two mutations, `M_GATE` and `M_ROUTE`. The binding names one each: `NoWideningWithoutIssuance` "`M_ROUTE`" (spec/theorem-premise-binding.md:48) and "`M_GATE` (`FloorNeverVacuous`)" (:47), and its BASE paragraph says of a proved property "its hypotheses are the "Breaks under" column" (:25). So the table reads as if `NoWideningWithoutIssuance` were proved under `M_GATE` and `FloorNeverVacuous` under `M_ROUTE`; neither is, in TLAPS or in Lean (spec/lean/README.md:46, `FloorRouting.lean`, hypothesis `none`). §5 lists no correction for this row. spec/proof-method.md:27 states the general rule, "**Each theorem takes as hypothesis only the mutations that break it,** written `ASSUME Mut # "M_X"`", which this module does not follow. ADR-0046 §4's own row for the module (line 317) says "under `Mut = "none"`" and is accurate.
- Fix belongs in: spec/theorem-premise-binding.md (the two rows' "Breaks under" cells or a note); decisions/ADR-0046.md §4 (the sentence)
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed with correction
- **Verifier's correction:** Line number: the `FloorRouting.lean` row is spec/lean/README.md:45, not :46 (46 is `NonComposition.lean`). Nothing else changes.
- **Verifier's evidence:** spec/FloorRouting_proof.tla:59-60, :64-65 (both `ASSUME Mut = "none"`); spec/FloorRouting.tla:19-22, :41, :46 (M_ROUTE, M_GATE); spec/theorem-premise-binding.md:25, :47, :48; decisions/ADR-0046.md:317, :340-342 (claim, exact), :350-363 (section 5's four corrections: none for FloorRouting); spec/proof-method.md:27; spec/lean/README.md:45.

### E-21: ADR-0053 counts thirteen modules with a Lean route and cites results the tree has superseded; the checkpoint and the READMEs say fifteen proof modules and sixteen encodings
- Against: decisions/ADR-0053.md:179 (and decisions/ADR-0053.md:133, 164, 464-465; spec/README.md:165; checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:190)
- Basis: in force
- Claim: "Every theorem of the thirteen proof modules for these, under the same hypotheses"
- Why wrong: checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:367-368: "**Fifteen modules' invariants are also proved in Lean of a re-encoding**, on T-0045-37, where ADR-0053 counted thirteen at its ratification"; spec/README.md:165: "re-encodes sixteen of the modules above"; spec/proof-certification.md:233: "For fifteen of the proof modules". The checkpoint's verified artifact is `TopakSpec-results-2026.10.07.txt` (`d365231c3ae3dd61`), "Batch 36 cited the `-10.06b` file; `-10.07` adds `Emergency`" (G11 line 190); a search of `decisions/` for `TopakSpec-results-2026.10.07`, `GraphCheckEmergency-results` and `TopakFloor-results-2026.10.08` finds them only in ADR-0033. The record's own text was not brought along: "**The modules not yet encoded**: `RunCoupling`, ..., `Emergency`" (decisions/ADR-0053.md:464-465) with `spec/lean/TopakSpec/Emergency.lean` in the tree; "`Classical.choice` in `NonComposition` alone" (decisions/ADR-0053.md:133) with spec/lean/TopakSpec-results-2026.10.07.txt:47 reporting "'Topak.Spec.Emergency.nextL_iff_next' depends on axioms: [propext, Classical.choice, Quot.sound]"; and T-0045-37's residual naming two checked encodings (decisions/ADR-0053.md:164) where spec/README.md:187 names three. The cited `TopakSpec-results-2026.10.06b.txt`, `GraphCheck-results-2026.10.06.txt` and `TopakFloor-results-2026.10.06.txt` also no longer match their sources: their `Sources:` digests for `spec/lean/TopakSpec.lean`, `spec/lean/lakefile.toml`, `spec/lean/GraphCheck.lean`, `spec/lean/graph-check.sh`, `floor/lean/TopakFloor.lean` and `floor/lean/gen.py` differ from `sha256sum` on the tree, so §7 (a)'s "regenerates the results file §4 cites byte for byte" cannot be repeated today. The frozen encodings themselves are unchanged.
- Fix belongs in: decisions/ADR-0053.md (§2, §4, Open obligations, a history row for the 10.07 and 10.08 results)
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: G11 item 107 in part ("Nine proved modules not encoded"); G11 §8 states the count difference
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0053.md:133, :164, :179 (claim, exact), :464-465; `ls spec/lean/TopakSpec/` has Emergency.lean; spec/lean/TopakSpec-results-2026.10.07.txt:47; spec/README.md:165, :187; spec/proof-certification.md:233; G11:190, :367-368. `grep -rln 'TopakSpec-results-2026.10.07\|GraphCheckEmergency-results\|TopakFloor-results-2026.10.08' decisions/` gives ADR-0033.md only. Compared the Sources digests of the three cited files with the tree: TopakSpec.lean, lakefile.toml, GraphCheck.lean, graph-check.sh, TopakFloor.lean and gen.py differ; the newest files (10.07, 10.08) match.

### E-22: ADR-0053 says the floor in force is "the `emergency` stage the reference links" and that its digests are the ones `topak-floor` pins; the reference links and pins the `workflow` stage
- Against: decisions/ADR-0053.md:101 (and decisions/ADR-0053.md:184, 419-420)
- Basis: in force
- Claim: "for the floor in force, the `emergency` stage the reference links"
- Why wrong: mechanism/crates/topak-floor/src/lib.rs:30: `pub const FLOOR_SRC: &str = include_str!("../../../../floor/proposed/workflow-floor.cedar");` and line 49 pins `10ea6818af9b4efe…`, the digest of `floor/proposed/workflow-floor.cedar`; the record cites `15c941b9a56a09f7` among "the digests `topak-floor` pins" (decisions/ADR-0053.md:184). floor/lean/README.md:7: "**And since 2026.10.08 the floor the reference links**, which is not the floor in force". Finding 6 of the record still concludes "so the gate claims are of the floor that runs" (decisions/ADR-0053.md:419-420); since 2026.10.08 the floor that runs is stated only in `TopakFloor-results-2026.10.08.txt` (`Linked.lean`), which this record does not cite.
- Fix belongs in: decisions/ADR-0053.md §1, §4, finding 6
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: G11 item 102
- **Verifier:** confirmed with correction
- **Verifier's correction:** Line number: the quoted sentence is floor/lean/README.md:8, not :7. Nothing else changes. The direction is as the finding has it: the floor in force is still the `emergency` stage (topak-floor/src/lib.rs:28-29); what is stale in ADR-0053 is 'the reference links' and 'the digests `topak-floor` pins'.
- **Verifier's evidence:** decisions/ADR-0053.md:101 (claim, exact), :184, :419-420; mechanism/crates/topak-floor/src/lib.rs:24-30, :49; `sha256sum floor/proposed/workflow-floor.cedar` = 10ea6818af9b4efe, emergency-floor.cedar = 15c941b9a56a09f7; floor/lean/README.md:8; floor/lean/TopakFloor-results-2026.10.08.txt:2; G11:349 (item 102).

### E-23: The clearance "No result in the 24 proof modules ... rests on either case" covers 24 of the 32 proof modules; for the other eight a scan exists and no reading of its 36 listed steps is recorded
- Against: decisions/ADR-0045.md:489 (and decisions/ADR-0046.md:250-251; spec/proof-scan-results-2026.11.10.txt; spec/README.md:158)
- Basis: in force (the clause) and evidence (the 2026.11.10 scan, for Proposed records)
- Claim: "No result in the 24 proof modules, certified or not, rests on either case, so none a record cites does"
- Why wrong: the tree has 32 proof modules; the eight of 2026.11.10 are cited by digest by ADR-0059 to ADR-0066 (spec/README.md:158: "the R1 row of each of ADR-0059 to ADR-0066 (2026.11.10) cites its modules and results files by digest"), so "none a record cites" no longer follows from 24. `spec/proof-scan-results-2026.11.10.txt` reports for them "Modules run: 8, of which this run certifies: 8 · SMT queries with an opaque constant under a binder: 28 · obligations Zenon or Isabelle closed: 8", no renamed-run difference and no capture. The method says the listing does not decide: "The scan says where to look; reading the step at each line is what decides" (spec/proof-certification.md:301-302), and for the 24 that reading was a ratification condition met by the custodian over 67 lines (decisions/ADR-0046.md:296-300). `grep -n "proof-scan"` over ADR-0059 to ADR-0066 finds one mention (decisions/ADR-0059.md:245, "share `spec/proof-scan-results-2026.11.10.txt`") and no reading; spec/README.md:158 says only that the file "scans the eight proof modules" beside "Each is checked, proved and certified". ADR-0046's "`ENABLED` occurs in six proof modules" (line 237) is likewise of the 24: `spec/Alone_proof.tla` (lines 248 to 325) and `spec/Release_proof.tla` (line 685) now prove `ENABLED` steps through Isabelle.
- Fix belongs in: the R1 rows of decisions/ADR-0059.md to ADR-0066.md or spec/README.md (to record the reading or say it is owed); the next revision of T-0045-31's Annex B note
- Severity: Low-Medium
- Confidence: medium (I searched the eight records and did not read them in full)
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0045.md:489 (claim, exact); decisions/ADR-0046.md:237-238, :250-251, :296-298; `ls spec/*_proof.tla | wc -l` = 32; spec/proof-scan-results-2026.11.10.txt:176 (8 modules, 28 queries, 8 obligations), :189, :201; spec/proof-certification.md:301-302; spec/README.md:158; spec/Alone_proof.tla:248-314, spec/Release_proof.tla:685. `grep -rn 'proof-scan-results-2026.11.10' .` finds spec/README.md:158, decisions/ADR-0059.md:245 and diagram sources, none recording a reading; `grep -n 'proof-scan' decisions/ADR-0059.md decisions/ADR-006[0-6].md` gives ADR-0059.md:245 only. ADR-0059 to ADR-0066 are all Proposed, so the in-force clause is not false of anything in force; what is missing is the reading.

### E-24: `spec/proof-method.md` opens by saying nothing is ratified, no record cites a proof and the prover is undeclared, and closes with ADR-0046's ratification
- Against: spec/proof-method.md:7 (and spec/proof-method.md:13-14, 123, 338, 450-453)
- Basis: living document
- Claim: "Nothing here is ratified, no record cites a proof yet, and the TLC-versus-TLAPS declaration (MAP 2.3, open in every checkpoint's §8) remains the custodian's to make."
- Why wrong: spec/proof-method.md:450-453, the same file: "## 7. ADR-0046, ratified 2026.10.02 (Batch 25)" ... "the TLC-versus-TLAPS declaration (its §1, §2); the prover as trusted-base row T-0045-31". Lines 13-14 say the prover "is a trusted-base item the corpus has not yet declared, in the place T-0045-29 declares TLC"; decisions/ADR-0045.md:386 declares it. Line 338 says "(T-0045-37, proposed)"; decisions/ADR-0053.md:16 is "Accepted (genesis) · 2026.10.06". The file's line 123 says the hypotheses have "corrected the premise table three times" and its line 29 "four corrections".
- Fix belongs in: spec/proof-method.md
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** spec/proof-method.md:7-8 (claim, exact), :13-14, :29, :123, :338, :450-453; decisions/ADR-0045.md:386; decisions/ADR-0053.md:16.

### E-25: `spec/README.md` says thirteen modules have proofs, tabulates thirty, and the tree has thirty-two; two proof modules and three base modules have no row
- Against: spec/README.md:66 (and spec/README.md:5, 13-48, 74-75, 127-156)
- Basis: living document
- Claim: "Thirteen modules also have deductive proofs, checked with the TLA+ Proof System (2026.10.02)."
- Why wrong: `ls spec/*_proof.tla | wc -l` gives 32. The proof table (lines 127 to 156) has 30 rows: a `grep -c` for a row beginning `Confinement_A1_proof.tla` and for one beginning `RunConfinement_proof.tla` gives 0 each, though both have proof and certified results files (`spec/Confinement_A1-proof-results-2026.10.02.txt`, `spec/RunConfinement-proof-results-2026.10.02.txt`) and spec/proof-method.md §2 step 10 (line 99) requires "add the row to `spec/README.md`". The module table (lines 13 to 48) has no row for `Confinement_A1.tla`, `RunConfinement.tla` or `ConfinementRefinement.tla`, all three pinned in `mechanism/corpus-pins.sha256`. Line 5 repeats "the invariants of thirteen modules are also proved". Lines 74-75, "The checkpoints' §8 describe the formal layer as TLC-checked until the next checkpoint is cut", predate three checkpoints (G11 §8, checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:366, says "The invariants are proved").
- Fix belongs in: spec/README.md
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** spec/README.md:5, :66 (claim, exact), :74-75, :127-156 (30 rows, counted); `ls spec/*_proof.tla | wc -l` = 32; `grep -c '^| `Confinement_A1_proof.tla`' spec/README.md` = 0, same for RunConfinement_proof.tla; `grep -n 'Confinement_A1\|RunConfinement\|ConfinementRefinement' spec/README.md` gives lines 81, 173, 176 only, no table row; mechanism/corpus-pins.sha256:44, :45, :57; spec/proof-method.md:99; G11:366.

### E-26: ADR-0044's status note says the reference does not implement §2 and §3; its open obligation and its B23 row say they were built on 2026.10.01
- Against: decisions/ADR-0044.md:15 (and decisions/ADR-0044.md:106, 115)
- Basis: in force
- Claim: "The reference does not implement §2–§3; that debt is carried on the face."
- Why wrong: decisions/ADR-0044.md:106: "**Built 2026.10.01** (ADR-0033 A6, Batch 23)"; decisions/ADR-0044.md:115: "**§2 and §3 are built**: ADR-0033 A6, ratified 2026.10.01 in Batch 23. The implementation obligation is struck". mechanism/GAPS-AND-ASSUMPTIONS.md:92 (I34) and :127 (G7 retired) agree with the later text, as does mechanism/crates/topak-bundle/src/lib.rs:181-185.
- Fix belongs in: decisions/ADR-0044.md (status note)
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0044.md:15-16 (claim, exact, unstruck), :106, :115; mechanism/GAPS-AND-ASSUMPTIONS.md:92, :127; mechanism/crates/topak-bundle/src/lib.rs:181-187.

### E-27: "the thirteen invariants ADR-0046 proves": ADR-0046 proves 41 invariants of thirteen modules
- Against: decisions/ADR-0045.md:384 (and decisions/ADR-0046.md:130; decisions/ADR-0045.md:496)
- Basis: in force
- Claim: "the thirteen invariants ADR-0046 proves rest on T-0045-31"
- Why wrong: the last column of ADR-0046 §4's table (decisions/ADR-0046.md:315-327) names 41 distinct invariants (2, 1, 2, 5, 2, 6, 4, 4, 2, 2, 3, 5, 3 by row), counted by script. The same annex has it right at decisions/ADR-0045.md:496: "The invariants of the thirteen modules ADR-0046 proves". decisions/ADR-0046.md:130 has the same slip: "for the thirteen proved invariants the constants are not a premise".
- Fix belongs in: decisions/ADR-0045.md (T-0045-29 residual); decisions/ADR-0046.md §3
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0045.md:384 (claim, exact), :496-497; decisions/ADR-0046.md:130, :315-327 (recounted the last column by row: 2+1+2+5+2+6+4+4+2+2+3+5+3 = 41).

### E-28: §2 and §9 of ADR-0045 say §6 refuses one candidate; §6's table refuses two
- Against: decisions/ADR-0045.md:122 (and decisions/ADR-0045.md:203, 204, 235, 437)
- Basis: in force
- Claim: "§6 applies this to the candidates the prioritization named, and refuses one."
- Why wrong: decisions/ADR-0045.md:203: "| Trusted time for R8 (G10, item 8) | **refused** |" and :204: "| The solver (item 15) | **refused** (finding 1)"; :437: "Trusted time: refused (§6)". §9's second bullet (line 235) speaks of "the one refused row" carrying a finding; the time source's refusal carries finding 2 (lines 293-298) to ADR-0032 and ADR-0031, whose disposition is still listed open (line 329) with no state given.
- Fix belongs in: decisions/ADR-0045.md §2, §9
- Severity: Low
- Confidence: medium
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0045.md:18, :122-123 (claim, exact), :203, :204 (two Class cells read 'refused'), :235, :272, :293-298, :329, :437.

### E-29: ADR-0045's Consequences say the binding table does not exist; §3 says it exists
- Against: decisions/ADR-0045.md:276 (and decisions/ADR-0045.md:143)
- Basis: in force (Consequences, outside the Decision)
- Claim: "**The binding table does not exist** (§3), so until it does the rows are cited in prose and "computed void" is a claim about what a table would show."
- Why wrong: decisions/ADR-0045.md:143: "**exists as `spec/theorem-premise-binding.md`**". R6 revised §3, §9 and the open obligations and left this bullet.
- Fix belongs in: decisions/ADR-0045.md Consequences
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0045.md:276-277 (claim, exact, unstruck), :143-144, :324-326, :513.

### E-30: "one lemma per mutation" is not what `RunSeats_proof.tla` carries
- Against: decisions/ADR-0046.md:109 (and spec/README.md:70; spec/proof-method.md:42)
- Basis: in force
- Claim: "Each proof module instead carries one lemma per mutation stating what the mutation admits"
- Why wrong: `spec/RunSeats.tla` has three mutations (`M_KIND`, `M_DOMAIN`, `M_OBSEMIT`); spec/RunSeats-proof-results-2026.10.02.txt:6 lists two mutation lemmas, "MutKindObserverActuates · MutDomainCrosses", and `grep -n OBSEMIT spec/RunSeats_proof.tla` finds the mutation only in a header comment (line 13). Outside the thirteen, `spec/Emergency_proof.tla` has seven mutations and one lemma of that form (line 389, `MutX1AdmitsAnything`); a search for `Mut = "M_AGENT"`, `"M_NOQUORUM"` and `"M_UNCOUPLE"` as a hypothesis finds none. The check was by lemma name and by `Mut = "…"` hypothesis only.
- Fix belongs in: decisions/ADR-0046.md §2 (the sentence), or the successor proofs
- Severity: Low
- Confidence: medium
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0046.md:109-110 (claim, exact); spec/RunSeats.tla (M_KIND, M_DOMAIN, M_OBSEMIT); spec/RunSeats_proof.tla:13, :214, :219; spec/RunSeats-proof-results-2026.10.02.txt:6; spec/Emergency.tla (seven M_ values); spec/Emergency_proof.tla:389 (the only `Mut = "M_` hypothesis). Counted `^LEMMA Mut` against the module's mutations for the twelve Mut-switched modules of the thirteen: equal in eleven, 2 against 3 in RunSeats.

### E-31: ADR-0046's Context says thirteen of fourteen modules gained a proof and that `Mechanism.tla` is the one without; §4 names another, and `spec/` held more than fourteen
- Against: decisions/ADR-0046.md:60 (and decisions/ADR-0046.md:64-65, 337-338)
- Basis: in force (Context, outside the Decision)
- Claim: "On 2026.10.02 thirteen of the fourteen modules under `spec/` gained a proof module"
- Why wrong: decisions/ADR-0046.md:337-338: "`Lease.tla`, frozen and superseded by `Lease_A1.tla`, is not proved". spec/README.md:13-25 lists, with results dated before 2026.10.02, `RulesFloorBase.tla`, `RulesFloorNV.tla`, `RulesFloorNV_rev5.tla`, `NonComposition.tla`, `Anchor.tla`, `BreakGlass.tla`, `Lease.tla`, `Lease_A1.tla`, `FloorComposition.tla`, `FloorRouting.tla`, `Confinement.tla`, `Seats.tla`, `Observers.tla`, `Coupling.tla`, `RunCoupling.tla`, `RunSeats.tla`, and `Mechanism.tla` at line 48: seventeen, of which `Lease.tla`, `RulesFloorNV.tla`, `RulesFloorBase.tla` and `Mechanism.tla` have no proof module.
- Fix belongs in: decisions/ADR-0046.md Context
- Severity: Low
- Confidence: medium (the count depends on which modules the drafter meant to exclude)
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0046.md:60 (claim, exact), :64-65, :337-338; spec/README.md:13-25, :48 (seventeen modules with results dated before 2026.10.02). Also in the tree with proof results dated 2026.10.02: spec/Confinement_A1-proof-results-2026.10.02.txt, spec/RunConfinement-proof-results-2026.10.02.txt.

### E-32: ADR-0053's ratification row reports 1014 steps for both replays; the Coupling replay file has 1015
- Against: decisions/ADR-0053.md:491 (and decisions/ADR-0053.md:183)
- Basis: in force (History)
- Claim: "`seats-replay.sh` and `coupling-replay.sh` report 82 traces, 1014 steps, all matching."
- Why wrong: mechanism/lean/CouplingReplay-results-2026.10.06.txt, summary line: "82 traces · 1015 steps · 0 not matching"; §4 of the record says "82 traces, 1015 steps, every one MATCH" (decisions/ADR-0053.md:183). G11 has both figures (checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:192).
- Fix belongs in: decisions/ADR-0053.md History B36
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0053.md:491 (claim, exact), :182 (Seats replay, 1014), :183 (Coupling replay, 1015); mechanism/lean/SeatsReplay-results-2026.10.06.txt summary '82 traces · 1014 steps'; mechanism/lean/CouplingReplay-results-2026.10.06.txt summary '82 traces · 1015 steps'; G11:192.

### E-33: "74 LS4 obligations in the 10.04 run" and the sixteen-module totals behind it do not match the results files in the tree
- Against: decisions/ADR-0053.md:49 (and spec/proof-method.md:231-240; spec/README.md:178)
- Basis: in force (Context) and living document
- Claim: "74 obligations in the 10.04 run, checked by nothing."
- Why wrong: summing the route lines of the sixteen `spec/*-proof-cert-results-2026.10.04.txt` files spec/proof-method.md §5a names (the thirteen of ADR-0046, `RunConfinement`, `Operators`, `Confinement_A1`) gives 3,390 obligations: trivial 2,256, SMT 1,042, Zenon 9, Isabelle 2, LS4 75, failed 6. spec/proof-method.md:231-240 has 3,376, 2,248, 1,038, 8, 2, 74, 6. The difference is `Operators` (354 obligations, 15 LS4 in spec/Operators-proof-cert-results-2026.10.04.txt), which decisions/ADR-0046.md:179 says was "regenerated at ADR-0050 R5" under the same dated name. The other dated total, spec/proof-certification.md:558-566 (twenty modules, 5,084, LS4 115), does match the files. So "the 10.04 run" has 75 LS4 obligations over the sixteen and 115 over the twenty, and no file set in the tree gives 74.
- Fix belongs in: spec/proof-method.md §5a (or a note that it predates the `Operators` regeneration); decisions/ADR-0053.md Context; spec/README.md:178
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed with correction
- **Verifier's correction:** Scope. spec/proof-method.md section 5a says of itself that it is 'the assessment as first written, for sixteen modules; that document carries the current count' (lines 214-215), so its table is a declared first count, and the finding should say so. What stands unqualified is '74 obligations in the 10.04 run' at decisions/ADR-0053.md:49, repeated at spec/README.md:178, and that the file set 5a names by glob no longer reproduces it. The 14-obligation difference is exactly Operators moving from 340 (207 / 118 / 1 / 14 LS4) to 354 (decisions/ADR-0050.md:285, :417).
- **Verifier's evidence:** Summed the route lines of the sixteen spec/*-proof-cert-results-2026.10.04.txt: 3,390 obligations, trivial 2,256, SMT 1,042, Zenon 9, Isabelle 2, LS4 75, failed 6 (3 each in Confinement and Confinement_A1); over all twenty: 5,084, 3,330, 1,621, 10, 2, 115. spec/proof-method.md:214-215, :231-240; spec/proof-certification.md:558-566; decisions/ADR-0053.md:49; spec/README.md:178; decisions/ADR-0046.md:179.

### E-34: The binding says thirty-seven rows are also proved; thirty-eight are
- Against: spec/theorem-premise-binding.md:15
- Basis: living document
- Claim: "the invariants of thirty-seven rows"
- Why wrong: 38 of the 43 table rows (lines 39 to 76) name a proof module in "Checked in", and the JSON has `proved_in` on 38 of its 43 theorems (counted by script). Line 62, the `RunConfinement` row, is the likely uncounted one.
- Fix belongs in: spec/theorem-premise-binding.md
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** spec/theorem-premise-binding.md:15 (claim, exact). Counted rows 39-81 whose Checked-in cell names a `_proof.tla`: 38 of 43 (rows 77-81 do not). JSON: 38 of 43 theorems carry `proved_in`. decisions/ADR-0053.md:282 and :451 also say thirty-eight.

### E-35: `tools/LEAN-PIN` calls ADR-0053 Proposed
- Against: tools/LEAN-PIN:1
- Basis: evidence
- Claim: "(ADR-0053, Proposed: T-0045-37)"
- Why wrong: decisions/ADR-0053.md:16: "**Status:** Accepted (genesis) · 2026.10.06". The file's digest, `ed47ecb1eac80f8a`, is the one G11 records (checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:147), so the line has stood since before ratification. Every other field of the pin matches Annex B's T-0045-37 and the results files.
- Fix belongs in: tools/LEAN-PIN (which moves a measured digest)
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** tools/LEAN-PIN:1 (claim, exact); decisions/ADR-0053.md:16; `sha256sum tools/LEAN-PIN` = ed47ecb1eac80f8a, as G11:147.

### E-36: Two section pointers lead nowhere, and a quoted residual is not in the row it is attributed to
- Against: spec/README.md:229 (and spec/lean/README.md:27; spec/proof-certification.md:656; spec/proof-method.md:258)
- Basis: living document
- Claim: "the proof carries hypotheses the module must not (`proof-method.md` §7)"
- Why wrong: the three reasons are in spec/proof-method.md §6 (line 434, "**Why the proofs are not merged into the modules.**"); §7 (line 450) is "ADR-0046, ratified 2026.10.02 (Batch 25)". spec/lean/README.md:27 cites "(`proof-certification.md` §5a)"; `grep -n "^## " spec/proof-certification.md` shows sections 1 to 12 and no 5a (the section meant is `proof-method.md` §5a or `proof-certification.md` §9). spec/proof-certification.md:656 says of T-0045-31 "Its residual names "the SMT backends' soundness""; the row's residual (decisions/ADR-0045.md:386) reads "The prover's and each backend's soundness are unexamined here" and the quoted words occur only in ADR-0046's struck open obligation (decisions/ADR-0046.md:455).
- Fix belongs in: spec/README.md; spec/lean/README.md; spec/proof-certification.md §11
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed with correction
- **Verifier's correction:** Two details. The quoted words 'the SMT backends' soundness' also occur in ADR-0046's E2 History row, which quotes the struck sentence (decisions/ADR-0046.md:505), so 'only in the struck open obligation' should read 'only in the struck obligation and the row that quotes it'. And spec/README.md:229's pointer does not lead nowhere: section 7 exists and is the wrong section. The three defects stand.
- **Verifier's evidence:** spec/README.md:229; spec/proof-method.md:406, :434, :450; spec/lean/README.md:27; `grep -n '^## ' spec/proof-certification.md` (sections 1 to 12, no 5a); spec/proof-certification.md:656; decisions/ADR-0045.md:386; `grep -rn "SMT backends' soundness" decisions spec` gives ADR-0046.md:455, :505, spec/proof-certification.md:656, spec/proof-method.md:258.

### E-37: D-0044-1 defines its axis as "empty key set, unsigned load" and then says an empty key set is not this row
- Against: decisions/ADR-0044.md:79 (and decisions/ADR-0044.md:48-49)
- Basis: in force
- Claim: "Bundle signing → off (empty key set, unsigned load)"
- Why wrong: the same row's consequence, as annotated at B23: "with an empty key set nothing loads, which is §1 and not this row"; §1 (lines 48-49): "An empty set is a deployment whose bundle tier loads nothing, which ADR-0030 §1 turns into a deny on every request". The row's "Theorems voided" cell names an obligation, "ADR-0030 §2's "Signed"", where the binding makes D-0044-1 falsify `bundle-signed`, a premise of `BundleRefusalHonored` (spec/theorem-premise-binding.md:45). ADR-0045's T-0045-27 cites the row ("ADR-0044 D-0044-1 drops this row", decisions/ADR-0045.md:408).
- Fix belongs in: decisions/ADR-0044.md §5
- Severity: Low
- Confidence: medium
- Already on the corpus's own lists: no
- **Verifier:** confirmed with correction
- **Verifier's correction:** Scope. Read as a conjunction (no keys, and bundles loaded unsigned), the axis and the B23 annotation do not contradict each other: under section 1 an empty key set loads nothing, so an empty set alone is not the degeneracy. The defect is narrower than the title: the gloss names 'empty key set' as the degenerate value when section 1 (lines 48-49) and the row's own annotation make an empty set fail closed. It is a misleading gloss, not a self-contradiction. The 'Theorems voided' cell naming an obligation where the binding names `BundleRefusalHonored` stands as stated.
- **Verifier's evidence:** decisions/ADR-0044.md:79 (both quotations exact), :48-49, :115; spec/theorem-premise-binding.md:45; decisions/ADR-0045.md:408.

### E-38: The reference's register still maps G7 to "T-0045-27 excluded"
- Against: mechanism/GAPS-AND-ASSUMPTIONS.md:116 (and decisions/ADR-0045.md:485; mechanism/GAPS-AND-ASSUMPTIONS.md:127)
- Basis: evidence
- Claim: "G7 is T-0045-27 excluded;"
- Why wrong: decisions/ADR-0045.md:485: "~~excluded~~ trust root, degenerate: the key is a throwaway with custody (1, 0)"; and the register's own row eleven lines down, mechanism/GAPS-AND-ASSUMPTIONS.md:127, strikes G7 and reads "**Retired 2026.10.01** (I34)".
- Fix belongs in: mechanism/GAPS-AND-ASSUMPTIONS.md §3 (the opening paragraph)
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** mechanism/GAPS-AND-ASSUMPTIONS.md:116 (claim, exact), :127 (G7 struck, 'Retired 2026.10.01'); decisions/ADR-0045.md:485.

### E-39: The newest premise-routes run names ADR-0045 at a digest the tree no longer has
- Against: spec/premise-routes-results-2026.11.03.txt:2 (and decisions/ADR-0046.md:270-272; decisions/ADR-0045.md:530)
- Basis: evidence
- Claim: "decisions/ADR-0045.md (sha256 b849108f349360bf)"
- Why wrong: `sha256sum decisions/ADR-0045.md` gives `8e425f423b0b89ca` (the value `mechanism/corpus-pins.sha256` line 35 pins). ADR-0046 §3 describes the practice the earlier drafts followed: "Drafting A3, with ADR-0045 E1, moved ADR-0045's pin, which is renewed in place whenever their text changes or either is ratified, and the routes `spec/premise-routes.sh` derives with ADR-0045's digest, which a new dated run renews (`spec/premise-routes-results-2026.10.08.txt` for the text drafted)". A5 was drafted on 2026.11.07 and moved the digest; no run follows it. ADR-0057's R1 row (Proposed, decisions/ADR-0057.md:418) says so: "`premise-routes.sh` was not rerun: its newest results name ADR-0045 at its digest before A5, and are renewed at ratification".
- Fix belongs in: a new dated `spec/premise-routes-results-*.txt`, or a note in decisions/ADR-0045.md A5's row
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no checkpoint item; acknowledged in ADR-0057 R1 (Proposed)
- **Verifier:** confirmed
- **Verifier's evidence:** spec/premise-routes-results-2026.11.03.txt:2 (claim, exact); `sha256sum decisions/ADR-0045.md` = 8e425f423b0b89ca; mechanism/corpus-pins.sha256:35; `ls spec/premise-routes-results-*` (newest is 2026.11.03); decisions/ADR-0046.md:270-272; decisions/ADR-0045.md:530-531; decisions/ADR-0057.md:418 (the deferral is stated there, in a Proposed record).

