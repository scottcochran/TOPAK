# Self review of 2026.11.11: reader J's findings in full

Reader J read the reference against its records. Annex to `derived/topak-open-findings-register-2026.11.11.md`, Part III. Each block is the finding as the reader wrote it, against the tree at `bbda621`, followed by the verdict of a verifier that did not find it. Paths are relative to the repository root. A path a finding names as absent is written without backticks. Nothing here is ratified, and every reader and verifier is of the same model lineage as the drafter of the corpus.

30 reported: 22 confirmed, 7 confirmed with a correction, 1 dropped.

### J-1: The reference tree at this commit is not the tree any reference manifest measures: two build inputs changed after the last manifest, and no addendum records it
- Against: decisions/ADR-0033.md:955-957 and :962-963 (and checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:412, :423 for the other side)
- Basis: pending
- Claim: "It measures the tree that A16 says moved after its manifest was cut, so that the reference as it stands is measured by a manifest." and "`shasum -c` on the manifest reports 115 of 116 at the commit that carries the addendum and the pin file."
- Why wrong: `sha256sum -c manifests/SHA256SUMS-REF-2026.10.09` at this tree reports four failures, not one: `mechanism/Cargo.lock: FAILED`, `mechanism/GAPS-AND-ASSUMPTIONS.md: FAILED`, `mechanism/corpus-pins.sha256: FAILED`, `mechanism/crates/topak-contain/Cargo.toml: FAILED`. G11 says of the same manifest "**`SHA256SUMS-REF-2026.10.09` fails two**: the pin file, re-pinned with A17, and the register" (G11:423) and "The reference's code at this cut is the code it measures" (G11:412). The current `Cargo.lock` (sha256 `0b95fdabe402bd6c…`) appears in none of the eighteen `manifests/SHA256SUMS-REF-*` (every one from 2026.10.05 on carries `465f8d3d4a45e6da`), and the current `topak-contain/Cargo.toml` (`aa57b6213d22528d`) in none either (`95e122d5ff0b9678` at -10.09). ADR-0033 has no addendum or History row after A17 that names either file; A18 "records no run" (ADR-0033.md:982). A1's own standard treats a `Cargo.toml` metadata edit as a change that needs an addendum (ADR-0033.md:1128-1130). The 155-test run (A16, A17, mechanism/README.md:39) is therefore evidence for a dependency set the tree no longer has; decisions/ADR-0045.md:488 instantiates T-0045-30 as "`Cargo.lock` in the reference manifests".
- Fix belongs in: decisions/ADR-0033.md (a further addendum with a manifest for the tree as it stands) and the next checkpoint's manifest note
- Severity: Medium-High
- Confidence: high
- Already on the corpus's own lists: no (G11 §9 lists two failing entries, not these two)
- **Verifier:** confirmed with correction
- **Verifier's correction:** Scope. Both quoted sentences are dated to their own commits (A17: "at the commit that carries the addendum and the pin file"; G11: "at this cut") and are not false of them, so "four failures, not one" should read: four at this tree, against the two G11 already expects (the pin file and the register). The defect is the other two, Cargo.lock and topak-contain/Cargo.toml, which no manifest, addendum or checkpoint records. That the dependency set differs is inferred from the moved lock digest; the tree carries no history to show what moved.
- **Verifier's evidence:** `sha256sum -c manifests/SHA256SUMS-REF-2026.10.09` -> 4 FAILED (mechanism/Cargo.lock, mechanism/GAPS-AND-ASSUMPTIONS.md, mechanism/corpus-pins.sha256, mechanism/crates/topak-contain/Cargo.toml), 112 of 116 OK; `grep -rl 0b95fdabe402bd6c manifests/` and `grep -rl aa57b6213d22528d manifests/` both empty; 18 files match manifests/SHA256SUMS-REF-*, Cargo.lock is 465f8d3d4a45e6da in every one from -2026.10.05 on and Cargo.toml 95e122d5ff0b9678 from -2026.10.02b on; decisions/ADR-0033.md:955-957, :962-963, :982, :1128-1132; `grep -n Cargo decisions/ADR-0033.md` -> :258 and :1130 only; checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:412, :421-424; decisions/ADR-0045.md:488; mechanism/README.md:39

### J-2: The reference's rules floor still implements R6 and R7 as they read before ADR-0026 A2, which is in force and pinned; the register does not record the divergence and says the field R7 reads "is read by nothing"
- Against: mechanism/GAPS-AND-ASSUMPTIONS.md:107 (and mechanism/crates/topak-core/src/rules.rs:192, :223-229; decisions/ADR-0026.md:52-59)
- Basis: living document
- Claim: "**(e)** `BreakGlassRules.tools` and `.actions` are read by nothing now; the roster and its quorum are what an activation uses"
- Why wrong: rules.rs:224-227 reads it on every issuance and at genesis: "if let Some(bg) = &r.break_glass { for a in R7_FORBIDDEN { if bg.actions.contains(a) {". ADR-0026 §2 as amended by A2 (ratified Batch 34, ADR-0026.md:13) says "R6 still bounds the number of floor exceptions; the count it bounds is 1, erasure", that R7 is "read as "no activation of an emergency seating grants a lease whose alphabet holds an authority act"", and "What the rules carry for break-glass is the roster and its quorum" (ADR-0026.md:52-57). The code keeps `pub const EXCEPTION_BOUND: usize = 2;` (rules.rs:192), tests R6 with three exceptions and R7 with `actions: ["Actuate", "Vote"]` (tests/mutations.rs:365-374), and hard-codes the emergency alphabet at state.rs:1288, so R7 as coded bounds a rules field no mechanism path reads, which rules.rs:4-6 itself calls vacuous ("every value an entry bounds is read by the mechanism from the issued rules, never hard-coded, or the entry would be vacuous"). `decisions/ADR-0026.md` is pinned and was re-pinned at A14 (ADR-0033.md:819); mechanism/README.md:126-127 says a re-pin follows bringing the code into line or registering the divergence. No register row names R6 or R7 after A2 (`grep -n 'R6\|R7' GAPS-AND-ASSUMPTIONS.md` finds only I9's older text).
- Fix belongs in: mechanism/GAPS-AND-ASSUMPTIONS.md (I48, I9) or mechanism/crates/topak-core/src/rules.rs, with an ADR-0033 addendum
- Severity: Medium
- Confidence: medium (the code facts are certain; whether A2 lowers R6's bound or only its count is the record's wording)
- Already on the corpus's own lists: no (G10 item 90 lists the same stale bound for `RulesFloorBase.tla` only)
- **Verifier:** confirmed with correction
- **Verifier's correction:** The grep as given returns six lines (46, 49, 70, 104, 106, 270), not I9 alone; only :70 (I9) is about the rules floor's R7, the rest are the Cedar floor's `R5` to `R7` or record revisions named R6, so the absence stands and the command's stated output does not. R7 and clause (e) are firm: `bg.actions` is read at rules.rs:226, on every issuance (rules.rs:350) and at genesis (state.rs:717); `.tools` is read by nothing. R6 is weaker than the title says: the count followed A2 (topak-floor/tests/floor.rs:50-55 asserts one exception) and only the constant bound stayed 2, which ADR-0026 A2's text ("the count it bounds is 1") does not plainly lower; G10 item 90 does call "R6's bound of two" stale in RulesFloorBase.tla.
- **Verifier's evidence:** mechanism/GAPS-AND-ASSUMPTIONS.md:107, :70; mechanism/crates/topak-core/src/rules.rs:4-6, :192, :195, :219-229, :350; mechanism/crates/topak-core/src/state.rs:717, :1288; mechanism/crates/topak-core/tests/mutations.rs:365-374; mechanism/crates/topak-floor/tests/floor.rs:50-55; decisions/ADR-0026.md:13, :48, :52-59, :343; decisions/ADR-0033.md:818-819; mechanism/corpus-pins.sha256:16 (matches sha256sum of ADR-0026.md); mechanism/README.md:123-128; checkpoints/topak-genesis-checkpoint-G10-2026.10.05.md:367; `grep -n 'R6\|R7' mechanism/GAPS-AND-ASSUMPTIONS.md`

### J-3: `scripts/smoke.py`, which the README gives as the live run, cannot complete against this tree
- Against: mechanism/README.md:52 and :56 (and mechanism/scripts/smoke.py:75; mechanism/crates/topak-node/src/mechanism.rs:1139-1143)
- Basis: living document
- Claim: "python3 scripts/smoke.py                   # live: processes, TCP, operator CLI, MCP client"
- Why wrong: smoke.py:75 reads `g['note']` from the operator `grant` reply: "print(f"grant a1: fence {g['fence']}, contained={g['contained']} ({g['note']})")". The reply the node builds has no such key: "json!({ "ok": true, "fence": fence, "token": token, "lease": lease, "contained": containment.contained, "because": containment.because, "tool_list": tool_list, })" (mechanism.rs:1139-1143); `grep -rn '"note"' crates/topak-node/src crates/topak-mcp/src crates/topak-core/src` returns nothing. The script would stop with a `KeyError` at its first print, before any MCP call. ADR-0033 §7's "Live" row (ADR-0033.md:174) is the only evidence of that kind, and every later addendum says "Not rerun" or is silent; the corpus lists the run as not repeated, not as no longer runnable.
- Fix belongs in: mechanism/scripts/smoke.py, or mechanism/README.md and the register's Evidence row
- Severity: Medium
- Confidence: high (read, not run)
- Already on the corpus's own lists: G5 item 52 covers "not rerun" only
- **Verifier:** confirmed
- **Verifier's evidence:** mechanism/scripts/smoke.py:74-75 (first print in main, reads g['note']); mechanism/crates/topak-node/src/mechanism.rs:1139-1143 (no such key); mechanism/crates/topak-node/src/main.rs:110-114 (`topak op` prints the reply unchanged); `grep -rn '"note"' crates/topak-node/src crates/topak-mcp/src crates/topak-core/src` in mechanism/ -> empty; mechanism/README.md:52, :56; decisions/ADR-0033.md:174, :234, :272, :313, :373, :521; mechanism/GAPS-AND-ASSUMPTIONS.md:20 ("has not been repeated", nothing on whether it still runs). Read, not run.

### J-4: §2's floor row, in force, names the genesis floor as the linked instrument; the reference has linked a proposed stage since `c15026d` and a stage not in force since `11aaf6a`
- Against: decisions/ADR-0033.md:92 (and mechanism/crates/topak-floor/src/lib.rs:30, :34; mechanism/README.md:29)
- Basis: in force
- Claim: "`floor/genesis-floor.cedar` and `floor/genesis.cedarschema` compiled in **by path** and refused at startup unless their bytes match the gated digests"
- Why wrong: lib.rs:30 "pub const FLOOR_SRC: &str = include_str!("../../../../floor/proposed/workflow-floor.cedar");" and lib.rs:34 "pub const SCHEMA_SRC: &str = include_str!("../../../../floor/proposed/workflow.cedarschema");", with a third compiled-in file the row does not name (lib.rs:37, the values). README.md:29: "since 2026.10.05 a proposed stage is linked in place of the genesis floor, and since 2026.10.08 this one, which is not in force". §2's substitution rule (ADR-0033.md:98-100) allows the change without amending the record, but the row still states the old instrument, the skeleton marks §2 changed since G9 (the K row was annotated at B27 and this row was not), and Consequences still says "**The enforced floor is the gated floor**" (ADR-0033.md:1030) without saying which.
- Fix belongs in: decisions/ADR-0033.md §2
- Severity: Medium
- Confidence: high
- Already on the corpus's own lists: G11 item 102 lists the linkage; the §2 row's wording: no
- **Verifier:** confirmed with correction; severity Low-Medium (reader: Medium)
- **Verifier's correction:** The row is stale, not in breach. §2's own rule (:98-100) lets a row change without amending the record provided the register records it, and the register does (rows at :49-50), as do A10's History row (:1159) and topak-floor/src/lib.rs:22-29; the stage linked is gated (lib.rs:39-41), so Consequences' "the enforced floor is the gated floor" still holds and only omits which floor. "The skeleton marks §2 changed since G9" names nothing in the corpus (`grep -rli skeleton` finds only ADR-0013, ADR-0023, ADR-0029 and 2026.09.15 process and checkpoint files) and could not be checked; the K-row comparison stands (⟨B27⟩ at :96).
- **Verifier's evidence:** decisions/ADR-0033.md:92, :96, :98-100, :1030, :1159; mechanism/crates/topak-floor/src/lib.rs:22-41; mechanism/README.md:29; mechanism/GAPS-AND-ASSUMPTIONS.md:49-50; checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:349

### J-5: §5 and the Open obligations say bundle signing is not implemented and still owed; A6 and the code implement it
- Against: decisions/ADR-0033.md:145-146 and :1053 (and :467; mechanism/GAPS-AND-ASSUMPTIONS.md:127; mechanism/crates/topak-bundle/src/lib.rs:181-191)
- Basis: in force
- Claim: "Bundle signing (ADR-0030 §2) is **not implemented** (§8)." and "the reference still owes the implementation (`mechanism/` G7) ⟨B17⟩."
- Why wrong: A6, ratified in Batch 23: "`LocalBundles::load_dir` takes the rules' `bundle_keys` and loads only what verifies under one of them ... (I34; G7 retired)" (ADR-0033.md:467). Register: "~~**G7**~~ ... **Retired 2026.10.01** (I34): a bundle loads only under a signature" (GAPS:127). Code: lib.rs:181-191 refuses a tarball with no `.sig`, a key the rules do not carry, or a signature that does not verify. §5 is a clause in force (pin `998eddcc5213ae2c`), so the stale sentence is decision text.
- Fix belongs in: decisions/ADR-0033.md §5 and Open obligations
- Severity: Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0033.md:145-146, :1053 (struck obligation still ends "the reference still owes the implementation (`mechanism/` G7)"), :452, :467; mechanism/GAPS-AND-ASSUMPTIONS.md:127; mechanism/crates/topak-bundle/src/lib.rs:181-191; `python3 spec/clauses.py decisions/ADR-0033.md` -> §5 998eddcc5213ae2c

### J-6: "§8" is cited three times and ADR-0033 has no §8
- Against: decisions/ADR-0033.md:117, :146, :1116
- Basis: in force
- Claim: "both out of scope and both open (§8)." and "is **not implemented** (§8)."
- Why wrong: the record's numbered clauses are §1 to §7 (`python3 spec/clauses.py decisions/ADR-0033.md` prints seven lines, §1 to §7); the sections after `## 7. Evidence` are unnumbered (`## Options considered` :1007, `## Consequences` :1023, `## Open obligations` :1047, `## History` :1076).
- Fix belongs in: decisions/ADR-0033.md §3, §5
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed; severity Low (reader: Low-Medium)
- **Verifier's evidence:** `python3 spec/clauses.py decisions/ADR-0033.md` -> seven lines, §1 to §7; `grep -n '^## \|^### [0-9]' decisions/ADR-0033.md` -> numbered headings :67 to :161, then :1007, :1023, :1047, :1076 unnumbered; `grep -n '§8' decisions/ADR-0033.md` -> bare §8 at :117, :146, :1116 (the third is History's quotation of the pre-R13 §5 text, so two live citations). Severity: a dangling pointer whose target, Open obligations, is plain; no claim turns on it.

### J-7: §1, in force, says the reference covers "two provisional Run actions" and that every lease is rung 0 and every principal Mediated; the record's own addenda and the code say otherwise
- Against: decisions/ADR-0033.md:70 and :77-79 (and :346, :503, :531-532; mechanism/crates/topak-core/src/types.rs:140; mechanism/crates/topak-core/src/state.rs:1109-1130)
- Basis: in force
- Claim: "for Build's six actions and two provisional Run actions." and "Every lease it issues is rung 0, so every principal it serves is `Mediated` (ADR-0031 §3)"
- Why wrong: A3: "`ActionKind::{Consult, Actuate, Report}` replace the provisional pair" (ADR-0033.md:346); types.rs:140 "pub const RUN: [ActionKind; 4] = [ActionKind::Consult, ActionKind::Actuate, ActionKind::Report, ActionKind::Route];". A7: "Backends: a host process (rung 1, which confines nothing and whose profile says so), ADR-0036 §4's container (rung 1), and a **SIMULATED** rung 3" (:503) and "**`contained = true` is reached only in a SIMULATED rung-3 run" (:531); state.rs:1109-1130 grants at rung 1 and 3 on an appraisal. Consequences repeats §1: "every lease reports `Mediated`" (:1037).
- Fix belongs in: decisions/ADR-0033.md §1 (and Consequences)
- Severity: Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0033.md:70, :77-78, :346, :503, :531-532, :1037; mechanism/crates/topak-core/src/types.rs:140; mechanism/crates/topak-core/src/state.rs:1109-1130

### J-8: The History table's State column still says "Pending" for A3, A4, A5 and A6, which were ratified
- Against: decisions/ADR-0033.md:1141, :1144, :1146, :1150 (and :1143, :1145, :1147, :1151, :26-28)
- Basis: in force
- Claim: "**Pending** : drafted 2026.09.29." (A3), "**Pending** : drafted 2026.09.30." (A4, A5), "**Pending** : drafted 2026.10.01." (A6)
- Why wrong: the rows beside them say "**A3 ratified 2026.09.30**" (:1143, B17), "**A4 ratified 2026.09.30**" (:1145, B19), "**A5 ratified 2026.09.30**" (:1147, B21), "**A6 ratified 2026.10.01**" (:1151, B23), and the header says "A6 ratified 2026.10.01 (Batch 23). ... A3 ratified 2026.09.30 (Batch 17) ...; A4 and A5 ratified 2026.09.30 (Batches 19, 21)" (:26-28). A1, A2 and A7 to A15 carry "**Applied** : ratified …" in the same column, so a reader, or a tool, taking state from the typed rows reads four addenda in force as pending. The A3 row also still says "(all Proposed)" of ADR-0040 to ADR-0043.
- Fix belongs in: decisions/ADR-0033.md History
- Severity: Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0033.md:1141, :1144, :1146, :1150 (State cell "**Pending** — drafted ...") against :1143, :1145, :1147, :1151 and the header :26-28; :1125, :1140, :1152, :1153, :1157, :1159-1162, :1164, :1166 read "**Applied** ... ratified"; :1141 "(all Proposed)"

### J-9: The register's Evidence row stops at 2026.10.02 and calls ratified addenda pending, under a header that says the register is current
- Against: mechanism/GAPS-AND-ASSUMPTIONS.md:20 (and :3; mechanism/README.md:39; decisions/ADR-0033.md:324, :485, :825)
- Basis: living document
- Claim: "**55 tests and 31 Rego cases**, the run ADR-0033 A3 (pending) and `mechanism/README.md` cite"; "The replayed gate suite is 51 cases since ADR-0039's floor run."; "**On 2026.10.02, 96 tests** (pending ADR-0033 A7)"; "trace validation at 57 traces and 642 steps"
- Why wrong: header (GAPS:3): "register brought current 2026.10.05, and for workflows 2026.10.08". A3 was "Ratified 2026.09.30 (Batch 17)" (ADR-0033.md:324); A7 "Ratified 2026.10.04 (Batch 29)" (:485), which the same register says at GAPS:121. README.md:39 cites "155 tests (2026.10.08)", not 55. The row has nothing for 103, 116, 119, 126, 131, 132, 133 or 155 tests, the 38 Rego tests, the 123-case replay (`assert_eq!(cases.len(), 123)`, topak-floor/tests/floor.rs:26) or the 82 traces and 1007 steps (ADR-0033.md:825). The same "pending A7" survives at GAPS:41, :75 (I14) and :94 (I36).
- Fix belongs in: mechanism/GAPS-AND-ASSUMPTIONS.md §1
- Severity: Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed; severity Low-Medium (reader: Medium)
- **Verifier's evidence:** mechanism/GAPS-AND-ASSUMPTIONS.md:20 (whole row read; ends at 2026.10.02), :3, :121, :41, :75, :94; decisions/ADR-0033.md:324, :485, :825; mechanism/README.md:39; mechanism/crates/topak-floor/tests/floor.rs:26; `sed -n 20p mechanism/GAPS-AND-ASSUMPTIONS.md | grep -o -w '103\|116\|119\|126\|131\|132\|133\|155\|123\|1007'` -> empty. Severity: stale counts and two stale statuses in one row of a register that is not a corpus record; the same file gives A7's ratification at :121 and ADR-0033 holds every run, so no claim rests on the row.

### J-10: The register gives statuses that were superseded: ADR-0042 §6 "stays Proposed", ADR-0040 "Proposed", G3 still open, and a status column dated G5
- Against: mechanism/GAPS-AND-ASSUMPTIONS.md:39, :17, :123, :27 (and :102; decisions/ADR-0042.md:13; decisions/ADR-0040.md:15; decisions/ADR-0033.md:1148)
- Basis: living document
- Claim: "**ADR-0042 §6 stays Proposed**"; "Build's six actions and Run's three (ADR-0040 §1, Proposed)"; G3: "The Run half follows records the custodian has not ratified."; column head "Status (G5, 2026.09.29)"
- Why wrong: the same register, I43: "ADR-0034 A2 and ADR-0042 §6 were not in force when this was built; **both ratified 2026.10.04 (Batch 30)**" (GAPS:102). ADR-0042.md:13: "**whole, §6 since 2026.10.04** ⟨B30⟩". ADR-0040.md:15: "**Status:** Accepted (genesis) · 2026.09.30". ADR-0033 B20: "`mechanism/` G3 closes" (ADR-0033.md:1148), yet G3 is an open row whose consequence is the pre-ratification one. The column says G5 while the header says "state of record is G11 (2026.10.09)" and the cells cite Batches 27 to 34.
- Fix belongs in: mechanism/GAPS-AND-ASSUMPTIONS.md §1, §1.1, §3
- Severity: Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed; severity Low-Medium (reader: Medium)
- **Verifier's evidence:** mechanism/GAPS-AND-ASSUMPTIONS.md:17, :27, :39, :123, :102, :3, :32, :34; decisions/ADR-0042.md:13; decisions/ADR-0040.md:15; decisions/ADR-0033.md:1148. Severity: stale statuses that the same register corrects (I43 at :102; G3's own middle cell), all in the direction of understating; the reader gives Low-Medium to J-17 and J-18, which are the same class.

### J-11: Register row I39 describes `Contained` with a Build-seat conjunct and "no Run profile registrable"; the code has neither
- Against: mechanism/GAPS-AND-ASSUMPTIONS.md:98 (and :102; mechanism/crates/topak-core/src/state.rs:1863-1882, :1936-1943)
- Basis: living document
- Claim: "`Rules.criterion` set, a Build seat." and "with no Run profile registrable, a Run seat is granted at rung 0 only and the Build-seat conjunct is a second guard"
- Why wrong: I43 in the same table: "**Run profiles register" (GAPS:102). `State::contained` has no Build-seat conjunct; its last conjunct is the domain match, and the comment says "A Run seat on a Run profile is `Contained` on the same conjuncts as a Build seat" (state.rs:1936-1943). `apply_profile_register` registers any well-formed promoted profile (state.rs:1863-1882), and the test `a_run_seat_on_a_run_profile_is_contained_with_p4_as_channel_fidelity` exists (tests/confinement.rs). I39 is A7's wording (ADR-0033.md:509) and was not carried through A8 (:558). Two doc comments in the code are stale the same way: state.rs:1861-1862 "A Run profile is refused while ADR-0042 §6 is Proposed" and state.rs:1769 "no Run profile exists to register".
- Fix belongs in: mechanism/GAPS-AND-ASSUMPTIONS.md I39 (and the two comments)
- Severity: Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** mechanism/GAPS-AND-ASSUMPTIONS.md:98, :102; mechanism/crates/topak-core/src/state.rs:1907-1946 (conjuncts; the last is the domain match; comment :1936-1938), :1863-1882, :1861-1862, :1768-1769; mechanism/crates/topak-core/tests/confinement.rs:715; decisions/ADR-0033.md:509, :558

### J-12: The register says the handle form, the `accepts` check and the label delivery table and root are "unbuilt"; the same register and the code say they are built
- Against: mechanism/GAPS-AND-ASSUMPTIONS.md:95 and :44 (and :105, :46; mechanism/crates/topak-core/src/labels.rs:42-61; mechanism/crates/topak-core/src/lift.rs:314-327)
- Basis: living document
- Claim: I33: "The handle form (§3), the `accepts` check at admit, `labels.delivery` and `labels.root` (§7) are ADR-0047's and unbuilt"; ADR-0049 row: "Not followed: §2's digest over the entry's inputs (I13); the handle form"
- Why wrong: I46: "A handle among an `Actuate`'s inputs is checked against the input's `accepts` by the bundle tier and resolved by the tool host" and "**(c)** `labels.root` is `{label, objects}`, a label for the root and one per named object; the delivery table must have a row for `thinker` and for `observer`" (GAPS:105); ADR-0047 row: "clear and handle delivery; a handle as an argument, resolved by the tool host" (GAPS:46). Code: labels.rs:42-43 "A handle names an item by its place in the record (ADR-0047 §2), in ADR-0049 §3's one form"; lift.rs:314-327 lifts each handle with its label for the bundle tier; `topak-bundle/tests/allowlist.rs` has `the_root_is_labelled_and_the_delivery_table_is_total`. I33 and the ADR-0049 row describe `7764e52`, before `c15026d`.
- Fix belongs in: mechanism/GAPS-AND-ASSUMPTIONS.md I33, §1.1
- Severity: Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed; severity Low-Medium (reader: Medium)
- **Verifier's evidence:** mechanism/GAPS-AND-ASSUMPTIONS.md:95, :44, :105, :46; mechanism/crates/topak-core/src/labels.rs:42-61; mechanism/crates/topak-core/src/lift.rs:314-327; policies/tool_schema.rego:18, :58, :71; mechanism/crates/topak-bundle/src/allowlist.rs:84-85, :250, :275; mechanism/crates/topak-bundle/tests/allowlist.rs:164. Severity: the stale cells understate what is built and I46 in the same table states it.

### J-13: The register's §6 says the restatement is "checked, not asserted, on every path a test takes"; since `11aaf6a` it is not, and its list of trusted trace inputs stops at 2026.10.02
- Against: mechanism/GAPS-AND-ASSUMPTIONS.md:296-305 (and :108; decisions/ADR-0033.md:845-847, :926-927; mechanism/crates/topak-core/src/trace.rs:16-18, :486-489)
- Basis: living document
- Claim: "**Since 2026.09.30 the restatement is checked, not asserted, on every path a test takes**" and "Facts the model takes from the trace and does not compute: whether an issuance passed `validate_issuance`, whether a break-glass approval's signature verified, whether an admit's parameter digest matched; and since 2026.10.02 whether an appraisal's signature verified and under which key, whether a session proof verified, and what a registered profile parses to."
- Why wrong: I49: "**`spec/Mechanism.tla` does not model workflows**: `WorkflowLoad` and `WorkflowGrant` are projected by name, and trace validation was not rerun" (GAPS:108); A16: "a traced run that loads one would not match it" (ADR-0033.md:926-927); trace.rs:486-489 projects the two entries by name only. So the eighteen `workflow.rs` tests and the e2e workflow test are asserted, not checked ("checked" is the corpus's word for TLC). The trusted-input list omits what A14 added: "whether a request's signature is its seat's, whether a sign-on assertion verifies, the roster keys that approved an activation, and which of several seats a revocation was lifted on" (ADR-0033.md:845-847; trace.rs:16-18; spec/Mechanism.tla:32-44).
- Fix belongs in: mechanism/GAPS-AND-ASSUMPTIONS.md §6
- Severity: Medium
- Confidence: high
- Already on the corpus's own lists: G11 item 56 and I49 carry the fact; the §6 sentence that contradicts them: no
- **Verifier:** confirmed
- **Verifier's evidence:** mechanism/GAPS-AND-ASSUMPTIONS.md:296-305, :108; decisions/ADR-0033.md:925-927, :845-847; mechanism/crates/topak-core/src/trace.rs:16-18, :486-489; spec/Mechanism.tla:32-44; 18 `#[test]` in mechanism/crates/topak-core/tests/workflow.rs; mechanism/crates/topak-node/tests/e2e.rs:1916; checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:331

### J-14: The register's table of TLA+ properties and their tests has no row for six pinned modules, and one row carries a superseded case count
- Against: mechanism/GAPS-AND-ASSUMPTIONS.md:309-351 and :324 (and mechanism/corpus-pins.sha256:47, :49, :53, :55, :57, :61; decisions/ADR-0033.md:691, :747, :927)
- Basis: living document
- Claim: section title "TLA+ properties and the tests that restate them"; "`floor.rs` replays B10 and the tightened B6 (47 cases)"
- Why wrong: the pin file holds `spec/Emergency.tla`, `spec/Labels.tla`, `spec/Mesh.tla`, `spec/Operators.tla`, `spec/RunConfinement.tla` and `spec/Workflow.tla` as modules the reference follows, and ADR-0033 says the tests are "named for `spec/Operators.tla`'s properties" (:691), "named for `spec/Emergency.tla`'s properties" (:747) and "tied to the reference by tests named after their properties" (:927-928). `grep -n` for `Emergency.tla`, `Labels.tla`, `Workflow.tla`, `Mesh.tla` and `RunConfinement.tla` in the register returns nothing; `Operators.tla` appears once, in I47, not in §6. The replay is of 123 cases (topak-floor/tests/floor.rs:26), not 47.
- Fix belongs in: mechanism/GAPS-AND-ASSUMPTIONS.md §6
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: no (G11 item 90 is about `spec/`'s binding table, not this table)
- **Verifier:** confirmed
- **Verifier's evidence:** mechanism/corpus-pins.sha256:47, :49, :53, :55, :57, :61; `grep -n` for Emergency.tla, Labels.tla, Workflow.tla, Mesh.tla, RunConfinement.tla in mechanism/GAPS-AND-ASSUMPTIONS.md -> empty each, Operators.tla -> :106 only; mechanism/GAPS-AND-ASSUMPTIONS.md:309-351, :324; mechanism/crates/topak-floor/tests/floor.rs:26; decisions/ADR-0033.md:691, :747, :926-927

### J-15: The header, the README and the register say the reference runs the archetype value on every axis; A11, the README and the register also say it runs D-0050-1 and D-0054-1
- Against: decisions/ADR-0033.md:29-30, mechanism/README.md:4-5, mechanism/GAPS-AND-ASSUMPTIONS.md:289 (and decisions/ADR-0033.md:711-712; mechanism/README.md:144-145; mechanism/GAPS-AND-ASSUMPTIONS.md:106, :108)
- Basis: in force
- Claim: "It runs the archetype value on every axis it implements" (ADR-0033); "It runs the archetype values and nobody ships the archetype." (README); "The baseline declares none; it runs the archetype values (quorum all, minGrant 2, unanimity custody)" (register §5 A7)
- Why wrong: A11: "The launcher's tests, the core's older tests and the shipped dev rules declare no operator and run as D-0050-1." (ADR-0033.md:711-712); README.md:144-145: "Rules that declare no operator seat leave the socket as it was (D-0050-1); `scripts/dev-init.sh` writes such rules."; I47 (b) "**(b) A deployment whose rules declare no operator is D-0050-1**" (GAPS:106) and I49 (b) "(D-0054-1)" (GAPS:108). decisions/ADR-0050.md:239 defines D-0050-1 as a degeneracy on the Mechanism axis: "Operator requests → unsigned, from whoever reaches the socket" … "The reference today".
- Fix belongs in: decisions/ADR-0033.md header (Deployment position), mechanism/README.md, mechanism/GAPS-AND-ASSUMPTIONS.md §5
- Severity: Low-Medium
- Confidence: medium (the header may mean the axes of 2026.09.24; it does not say so)
- Already on the corpus's own lists: I47 (b) states the degeneracy; the contradiction: no
- **Verifier:** confirmed with correction
- **Verifier's correction:** Scope. The register's §5 A7 cell does not say "every axis": it names three values (quorum all, minGrant 2, unanimity custody), and the dev rules still carry them (dev-init.sh:51), so that cell is not contradicted on what it names. The contradiction is with the ADR header (:29-30) and the README (:4-5); the register's part is only its bare "declares none" beside I47 (b).
- **Verifier's evidence:** decisions/ADR-0033.md:29-30, :711-712; mechanism/README.md:4-5, :144-145; mechanism/GAPS-AND-ASSUMPTIONS.md:289, :106, :108; decisions/ADR-0050.md:239; decisions/ADR-0054.md:282; mechanism/scripts/dev-init.sh:51

### J-16: §6, in force, says nothing about the Observer or Persona attestation is built; A2 and A7 built parts of both
- Against: decisions/ADR-0033.md:155 (and :292, :505; mechanism/crates/topak-core/src/observer.rs:48-67; mechanism/crates/topak-core/src/state.rs:767-773, :1778-1781)
- Basis: in force
- Claim: "**Anything about the Observer, the archive, erasure, masking, Persona attestation, or bootstrap.** None is built."
- Why wrong: A2: "Heartbeats as control-plane facts (`Admitted::Heartbeat`); `marks` and `seals` replicated; `live(o)` in the lift as `observerLive`, its deterministic half re-checked at apply" (:292); A7: "one Persona digest across lease, profile and statement" re-checked at apply (:505). Code: observer.rs `Heartbeat`, state.rs `observer_covers`, and state.rs:1778 "F26: one Persona digest across the lease, the profile and the statement". The register distinguishes what is and is not built (I27, G12, G13); §6 does not.
- Fix belongs in: decisions/ADR-0033.md §6
- Severity: Low-Medium
- Confidence: medium
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0033.md:155, :292, :505; mechanism/crates/topak-core/src/observer.rs:48-67; mechanism/crates/topak-core/src/state.rs:767-773, :1778-1781; mechanism/GAPS-AND-ASSUMPTIONS.md:82, :132, :133

### J-17: Register rows I9 and §5 A5 describe X1 break-glass approvals as the working mechanism; the entry is refused at apply
- Against: mechanism/GAPS-AND-ASSUMPTIONS.md:70 and :287 (and :107; mechanism/crates/topak-core/src/state.rs:1044-1046)
- Basis: living document
- Claim: I9: "**Break-glass**: roster keys sign approvals scoped to (seat, epoch); quorum *k* is issued; approvals lapse at the next epoch. Rules carry `actions` so R7 has a value to bound"; A5: "Not addressed; break-glass approvals are signatures from the operator channel"
- Why wrong: state.rs:1044-1046: "Entry::BreakGlassApprove { .. } => Applied::Rejected( "X1 break-glass is retired: the roster activates an emergency seating (ADR-0052 §2)".into(), )". I48 in the same table: "**X1 is retired**: the linked floor has no such entry, and a `BreakGlassApprove` is refused at apply" (GAPS:107). I9 carries no retirement note, unlike G7 and G10.
- Fix belongs in: mechanism/GAPS-AND-ASSUMPTIONS.md I9, §5
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: I48 states the retirement; I9 and A5 unchanged: no
- **Verifier:** confirmed
- **Verifier's evidence:** mechanism/GAPS-AND-ASSUMPTIONS.md:70, :287, :107, :130; mechanism/crates/topak-core/src/state.rs:1044-1046

### J-18: The register's ADR-0022 §6 row says "Nothing is enforced; every lease is rung 0"; G1 and I37 in the same file say otherwise
- Against: mechanism/GAPS-AND-ASSUMPTIONS.md:35 (and :96, :121, :19)
- Basis: living document
- Claim: "Nothing is enforced; every lease is rung 0"
- Why wrong: I37: "**The declared rung is per seat** (`SeatDecl.rung`, default 0). A grant is at the seat's rung or refused; rung 3 needs an issued verifier key" (GAPS:96); G1: "the rung-1 launcher in the node, on a host process (which confines nothing, and its profile says so) or ADR-0036 §4's container; rung 3 SIMULATED (I42)" (GAPS:121). The "Not in scope" cell (GAPS:19) still lists "confinement" beside the same G1.
- Fix belongs in: mechanism/GAPS-AND-ASSUMPTIONS.md §1, §1.1
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** mechanism/GAPS-AND-ASSUMPTIONS.md:35, :96, :121, :19

### J-19: G6 says the dev rules have one veto seat; `dev-init.sh` writes two
- Against: mechanism/GAPS-AND-ASSUMPTIONS.md:126 (and mechanism/scripts/dev-init.sh:60; decisions/ADR-0033.md:291)
- Basis: living document
- Claim: "`dev/rules.json` from `scripts/dev-init.sh` (3 anchor keys, 3 grant seats, 1 veto seat)"
- Why wrong: dev-init.sh:60: "grant_roster: ["g1", "g2", "g3"], veto_roster: ["o1", "corr"],"; A2: "dev rules seat `o1` in `a1`'s cell and a correlator `corr`, both on the veto roster" (ADR-0033.md:291).
- Fix belongs in: mechanism/GAPS-AND-ASSUMPTIONS.md G6
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** mechanism/GAPS-AND-ASSUMPTIONS.md:126; mechanism/scripts/dev-init.sh:60 (the only `veto` line in the script); decisions/ADR-0033.md:291

### J-20: The register and README say every item is marked in the code as `PROVISIONAL (<tag>)`; two tags the register names are in no crate, and one it strikes is still in the code
- Against: mechanism/GAPS-AND-ASSUMPTIONS.md:6-7, :99, :100, :102 and mechanism/README.md:107 (and mechanism/crates/topak-core/src/state.rs:1872-1873)
- Basis: living document
- Claim: "Each item is also marked in the code as `PROVISIONAL (<tag>)`, so `grep -rn PROVISIONAL crates/` and this file should stay in step."; "PROVISIONAL (evidence-retention)" (I40); "PROVISIONAL (session-proof)" (I41); "~~PROVISIONAL (run-profile): A2's ratification, with ADR-0042 §6~~ Follows the records since Batch 30" (I43); README: "`PROVISIONAL (<tag>)` in the code marks every place a gap or assumption lives."
- Why wrong: `grep -rn 'evidence-retention' crates scripts` returns nothing; `grep -rn 'session-proof' crates` returns one line that is not a marker (state.rs:128, "The last session-proof counter"). The struck tag is still there: state.rs:1872-1873 "// PROVISIONAL (run-profile): Run profiles register under ADR-0034 A2, which is pending, and // ADR-0042 §6, which is Proposed." `grep -rn 'PROVISIONAL *(' crates --include=*.rs` finds 20 markers with 19 distinct tags for a register of 47 assumption rows and 19 gap rows; one code tag, "PROVISIONAL (wasm-tools)" (state.rs:47), is named in no register row. ADR-0033's Consequences foresees it ("The floor pin fails loudly; the `PROVISIONAL` tags do not.", :1042-1043); the register's and README's sentences assert the opposite.
- Fix belongs in: mechanism/GAPS-AND-ASSUMPTIONS.md (header, I40, I41, I43) and the code markers
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed with correction
- **Verifier's correction:** "One code tag ... is named in no register row" holds under neither reading. By tag text, seven code tags are absent from the register (`wasm-tools`, `gate runner`, `dedupe growth`, `inputs-in-workspace lift`, `seat registry`, `session binding`, `replica authentication`); by topic, `wasm-tools` is covered by I43 and I44, which name `Params::wasm_tools`. The other counts reproduce: 20 markers, 19 distinct tags, 47 assumption rows, 19 gap rows, and the two register tags with no marker.
- **Verifier's evidence:** in mechanism/: `grep -rn 'evidence-retention' crates scripts` -> empty; `grep -rn 'session-proof' crates` -> state.rs:128 only, a field comment; `grep -rn 'PROVISIONAL *(' crates --include=*.rs` -> 20 lines, 19 distinct tags; `grep -c '^| \*\*I[0-9]*\*\*'` -> 47, gap rows 19; `grep -c -i` of each code tag in the register; mechanism/GAPS-AND-ASSUMPTIONS.md:6-7, :99, :100, :102; mechanism/README.md:107; mechanism/crates/topak-core/src/state.rs:47, :1872-1873; decisions/ADR-0033.md:1042-1043

### J-21: The register calls ADR-0025 A2 "pending" in one row and "ratified in Batch 34" in another
- Against: mechanism/GAPS-AND-ASSUMPTIONS.md:105 (and :95; decisions/ADR-0025.md:11; mechanism/crates/topak-core/src/rules.rs:114, :118, :122)
- Basis: living document
- Claim: I46: "**The two issued lists** (`inside_targets`, `releasers`; ADR-0025 A2, pending) are fields of the rules"
- Why wrong: I33: "The two lists W7 to W9 read are fields of the issued rules (ADR-0025 A2, ratified in Batch 34)" (GAPS:95); ADR-0025.md:11: "A2, drafted 2026.10.03, with ADR-0047: two lists the load checks read (§1 (h)), ratified 2026.10.05 (Batch 34)". The code comments say the same stale thing of A2 and of A3: rules.rs:114 "ADR-0025 A3 (pending)", :118 and :122 "ADR-0025 A2 (pending)".
- Fix belongs in: mechanism/GAPS-AND-ASSUMPTIONS.md I46 (and rules.rs comments)
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** mechanism/GAPS-AND-ASSUMPTIONS.md:105, :95; decisions/ADR-0025.md:11; mechanism/crates/topak-core/src/rules.rs:114, :118, :122

### J-22: The README's crate table and the title of register row I43 call ADR-0034 A2 pending; both documents say elsewhere that it is in force
- Against: mechanism/README.md:33 and mechanism/GAPS-AND-ASSUMPTIONS.md:102 (and mechanism/README.md:176, :186; decisions/ADR-0033.md:595)
- Basis: living document
- Claim: README: "And the Run tool host, `wasmtool` (ADR-0034 A2, pending)"; I43: "**Run profiles register, and are read under ADR-0034 A2, which is pending.**"
- Why wrong: the same I43 row: "**both ratified 2026.10.04 (Batch 30)**"; README.md:176 heads the section "## Run tools held to their channel (ADR-0034 A2)" with no qualifier; A9: "**ADR-0034 A2 (R4), in force since Batch 30**" (ADR-0033.md:595).
- Fix belongs in: mechanism/README.md, mechanism/GAPS-AND-ASSUMPTIONS.md I43
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed with correction
- **Verifier's correction:** Line number: the README's second unqualified mention is at mechanism/README.md:185 ("(ADR-0049 §5; ADR-0034 A2):"); :186 is blank.
- **Verifier's evidence:** mechanism/README.md:33, :176, :185; mechanism/GAPS-AND-ASSUMPTIONS.md:102; decisions/ADR-0033.md:595; decisions/ADR-0034.md:16

### J-23: A15 says the source comments no longer call ratified records Proposed; comments in the crates still call ADR-0040, ADR-0034 A2, ADR-0042 §6, ADR-0024 A2.3 and ADR-0025 A2 and A3 Proposed or pending
- Against: decisions/ADR-0033.md:872 (and mechanism/crates/topak-core/src/types.rs:113; action.rs:1; state.rs:46, :775, :1620, :1862, :1873, :1884, :1938; confine.rs:150; rules.rs:114, :118, :122; mechanism/crates/topak-contain/src/wasmtool.rs:1; topak-contain/src/lib.rs:19; mechanism/crates/topak-node/src/config.rs:50)
- Basis: in force
- Claim: "Comments that called five records Proposed | Batch 34 | Eight source files: the comments name the records without that word, or as provisional"
- Why wrong: A15's row is true of its five records and leaves a reader to infer the comments are current. They are not: types.rs:113 "Run's three are ADR-0040 §1 (Proposed)" (ADR-0040 Accepted, Batch 20); state.rs:775 "ADR-0024 A2.3, pending" (ratified Batch 15, GAPS:38); state.rs:1873 "ADR-0042 §6, which is Proposed" (ratified Batch 30); wasmtool.rs:1 "ADR-0034 A2, pending"; rules.rs:118 "ADR-0025 A2 (pending)" (ratified Batch 34). Each of these records is pinned, so the drift review passed over them.
- Fix belongs in: the named source files (a code change, so an addendum), or a register note
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no (G10 item 98 covers two comments under `policies/` only)
- **Verifier:** confirmed with correction
- **Verifier's correction:** Direction and scope. A15's row is about the five records ratified in Batch 34 (History :1166: "comments no longer call five ratified records Proposed") and is true of them: no comment under crates/ calls ADR-0047, 0048, 0049, 0050 or 0052 Proposed. ADR-0033.md:872 is therefore not wrong; the defect is the comments on other ratified records, which nothing records. The list is also short: add topak-transport/src/lib.rs:1 ("ADR-0005, Proposed"; Accepted in Batch 27) and :12, topak-mcp/src/lib.rs:4, topak-bundle/src/allowlist.rs:10 and :38, topak-node/src/lib.rs:61, topak-node/src/mechanism.rs:140, :221 and :730.
- **Verifier's evidence:** `grep -rn 'Proposed\|pending' crates --include=*.rs` in mechanism/ (every cited site found: types.rs:113; action.rs:1; state.rs:46, :775, :1620, :1862, :1873, :1884, :1938; confine.rs:150; rules.rs:114, :118, :122; wasmtool.rs:1; topak-contain/src/lib.rs:19; config.rs:50); `grep -rn 'ADR-00\(47\|48\|49\|50\|52\)[^;.]*Proposed' mechanism/crates --include=*.rs` -> empty; decisions/ADR-0033.md:872, :1166; decisions/ADR-0040.md:15; decisions/ADR-0042.md:13; decisions/ADR-0034.md:16; decisions/ADR-0025.md:11; mechanism/GAPS-AND-ASSUMPTIONS.md:32, :38

### J-24: The prefaces of A9 and A13 still say A10 and A14 are pending
- Against: decisions/ADR-0033.md:582 and :786 (and :613, :815)
- Basis: in force
- Claim: "The rest is A10, pending." and "The other is A14, pending."
- Why wrong: A10's preface: "Ratified 2026.10.05 (Batch 34)" (:613); A14's: "Ratified 2026.10.05 (Batch 34)" (:815). A10 to A12 carry a sentence that their bodies speak as of drafting; the A9 and A13 prefaces were written at ratification and carry none.
- Fix belongs in: decisions/ADR-0033.md §7 (A9, A13 prefaces)
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0033.md:582, :786 against :613, :815; the "speaks as of its drafting" sentence is at :614-615, :671-672, :725-726 and in neither A9's nor A13's preface

### J-25: The README says the bundle entrypoint composes `tool_invocation.rego`; since A3 it composes two modules
- Against: mechanism/README.md:105-106 (and policies/bundle.rego:26-27, :41-44; decisions/ADR-0033.md:352)
- Basis: living document
- Claim: "The bundle entrypoint is `policies/bundle.rego` (`data.topak.bundle.allow`), which composes `policies/tool_invocation.rego`."
- Why wrong: bundle.rego imports both: "import data.topak.bundle.actuate" (:26) and "import data.topak.bundle.tool_invocation" (:27), and refuses an `Actuate` when "not actuate.allow" (:43); A3: "The bundle tier split by domain: `tool_schema.rego` shared, `tool_invocation.rego` for `Invoke`, `actuate.rego` for `Actuate`" (ADR-0033.md:352).
- Fix belongs in: mechanism/README.md
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** mechanism/README.md:105-106; policies/bundle.rego:26-27, :41-44; decisions/ADR-0033.md:352

### J-26: `mechanism/lean/README.md` and the mechanism README present the Lean results as current; they are stale, and two pointers in the Lean README no longer land
- Against: mechanism/lean/README.md:25 and :88, mechanism/README.md:108, :113-118 (and mechanism/crates/topak-node/src/mechanism.rs:791-796; mechanism/crates/topak-core/src/types.rs:118-129)
- Basis: evidence
- Claim: "`callSite_eq_compose` | the node's own gate check before the bundle call is `compose` | `mechanism.rs` 765-771"; "The code's nine action kinds are read as the module's four"; README: "**One function is proved, not only tested.**" and "on 2026.10.06 all 82 traces matched"
- Why wrong: at this tree mechanism.rs:765-771 is the `LeaseExpired` branch that proposes `EndRound`; the gate check is at :791-796 (`floor_gate(&floor_out)`, `compose(&floor_out, &bundle_out)`). `ActionKind` has ten variants (types.rs:118-129, with `Route`). `mechanism/lean/Admit-results-2026.10.06c.txt` line 2 transcribes `mechanism.rs (sha256 ba754394b045a1db)`, `state.rs (sha256 25eeeeb3830ee9f8)`, `types.rs (sha256 6524de30f4ada72a)`, `rules.rs (sha256 94b543971af7b9ba)`, `topak-floor/src/lib.rs (sha256 0f280725956a15b4)`; `sha256sum` now gives `0c6ff1f0fc89c845`, `e6a927a19935e329`, `9052f7a910657449`, `2f869fec373905f7`, `93f01304236d3708`. Neither README says the results are stale; A16 and I49 do.
- Fix belongs in: mechanism/lean/README.md, mechanism/README.md
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: G11 item 103; mechanism/GAPS-AND-ASSUMPTIONS.md I49 (the staleness, not the READMEs' silence)
- **Verifier:** confirmed
- **Verifier's evidence:** mechanism/lean/README.md:25, :88; mechanism/crates/topak-node/src/mechanism.rs:762-771 (the LeaseExpired branch), :791-796 (the gate check); mechanism/crates/topak-core/src/types.rs:118-129 (ten variants); mechanism/lean/Admit-results-2026.10.06c.txt line 2 against `sha256sum`: mechanism.rs, state.rs, types.rs, rules.rs and topak-floor/src/lib.rs moved as stated, while admit.rs (88181d094da7a8b6) and clock.rs (684599e3b20f7495) still match; `grep -n -i stale` in the two READMEs -> only the lean-sync usage lines (mechanism/README.md:50, mechanism/lean/README.md:220); mechanism/README.md:108, :118; checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:350

### J-27: `spec/Mechanism.tla`'s header says three facts are taken from the trace and then lists eight rows of them, and calls three ratified records Proposed
- Against: spec/Mechanism.tla:19-20 and :45-46 (and :21-44; decisions/ADR-0033.md:444-446, :845-847)
- Basis: evidence
- Claim: "Three facts are taken from the trace rather than computed here, and are the trace's trusted inputs (an `ok` field on the entry):" and "Labels (ADR-0047), operators (ADR-0050) and the emergency seating (ADR-0052), all Proposed"
- Why wrong: the list that follows has rows for `Issue`, `BreakGlassApprove`, `Admit`, `Grant Renew Contested`, `ProfileRegister`, `Grant`, `Control` and `Activate` (Mechanism.tla:21-44), carrying `ok`, `proofOk`, `sigOk`, `sigKey`, `signOnOk`, `freshOk`, `targetSignOnOk` and `approvers`. "Three" is A5's count (ADR-0033.md:444-446); A14 says the set "has grown" (:845). ADR-0047 is Accepted and ADR-0050 and ADR-0052 Accepted provisional since Batch 34 (decisions/ADR-0047.md:19, ADR-0050.md:20, ADR-0052.md:18). The module is pinned at `e29dbaf0936dbae1`, so correcting the comment moves the pin and the digest the trace results cite.
- Fix belongs in: spec/Mechanism.tla (at its next revision)
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** spec/Mechanism.tla:19-20, :21-44 (eight rows: Issue, BreakGlassApprove, Admit, Grant Renew Contested, ProfileRegister, Grant, Control, Activate), :45-46; decisions/ADR-0033.md:444-446, :845; decisions/ADR-0047.md:19; decisions/ADR-0050.md:20; decisions/ADR-0052.md:18; mechanism/corpus-pins.sha256:52 (e29dbaf0936dbae1, matches sha256sum)

### J-28: The register and the checkpoints date the last live smoke run to 2026.09.25; ADR-0033 says it was not rerun that day
- Against: mechanism/GAPS-AND-ASSUMPTIONS.md:20 (and decisions/ADR-0033.md:174, :234; checkpoints/topak-genesis-checkpoint-G5-2026.09.29.md:286)
- Basis: living document
- Claim: "The live smoke run has not been repeated since 2026.09.25 (G5 item 52)."
- Why wrong: ADR-0033's addendum for the run of 2026.09.25: "**Not rerun:** the live smoke run against Kafka and an OPA sidecar." (:234). The only live run in the record is the "Live" row of "## 7. Evidence : run 2026.09.24" (:161, :174). G5 item 52 has the same date ("not rerun since 09.25"), so checkpoint and decision disagree by a day on when the only live evidence was taken, and so on which tree (`4fd9677`, not `453801c`).
- Fix belongs in: mechanism/GAPS-AND-ASSUMPTIONS.md §1 (and the next checkpoint's item 52)
- Severity: Low
- Confidence: medium (the phrase can be read as "since we first noted it")
- Already on the corpus's own lists: G5 item 52 (carries the date in question)
- **Verifier:** not confirmed
- **Verifier's correction:** The texts do not conflict. The same Evidence row dates the live smoke run to commit `4fd9677` (2026.09.24) and gives `453801c` (2026.09.25) 44 tests and no live run, and G3 says the same of the two runs ("the live smoke run not repeated" on 09.25). "Not repeated since 2026.09.25" is true of the interval that begins that day and agrees with ADR-0033's "Not rerun" in the 09.25 addendum and "as at 2026.09.25" in the next. No text places a live run on 09.25 or on `453801c`; at most the phrase is loose.
- **Verifier's evidence:** mechanism/GAPS-AND-ASSUMPTIONS.md:20 (first and second sentences of the row); decisions/ADR-0033.md:161, :174, :204, :234, :272; checkpoints/topak-genesis-checkpoint-G3-2026.09.25.md:90-91; checkpoints/topak-genesis-checkpoint-G5-2026.09.29.md:286

### J-29: The open obligation requires each addendum to say which of the three refinement-chain items it discharges; A18 does not
- Against: decisions/ADR-0033.md:1071-1072 (and :1001-1003, :977-978)
- Basis: pending
- Claim: "Each addendum from here on says which of the three it discharges, and the rows leave Annex A only on that addendum."
- Why wrong: A6 to A16 each carry the sentence (for example :853 "Of the refinement chain's three items, none is discharged; stage 1 is current with the tree again."). A17 says it only by reference ("Everything A16 leaves undischarged stays undischarged.", :978). A18's "What it discharges, and what it does not" (:1001-1003) says "Nothing in force" and does not mention the three items.
- Fix belongs in: decisions/ADR-0033.md A18
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0033.md:1071-1072; A18 at :980-1003 ("Nothing in force", no mention of the three items); A17 at :977-978 (by reference only); the sentence in A6 to A16 at :481, :536, :576, :609, :666, :719, :779, :811, :853, :883, :950

### J-30: The register's assumption ids skip I25 and I26 with no note
- Against: mechanism/GAPS-AND-ASSUMPTIONS.md:81-87 (rows I20, I27, I21 to I24, I28)
- Basis: living document
- Claim: rows "**I24**" then "**I28**", with "**I27**" placed after "**I20**"
- Why wrong: `grep -o '^| \*\*I[0-9]*\*\*' GAPS-AND-ASSUMPTIONS.md` lists I1 to I24 and I27 to I49, 47 rows; `grep -rn 'I25\|I26' mechanism decisions/ADR-0033.md` returns nothing. ADR-0033 counts "24 assumptions" at A1 (:257) and then adds "I27 (liveness)" at A2 (:296), so two ids were never used or two rows were removed, and the register does not say which. Retired rows elsewhere are kept struck (G7).
- Fix belongs in: mechanism/GAPS-AND-ASSUMPTIONS.md §2
- Severity: Low
- Confidence: medium (may be deliberate; nothing says so)
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** `grep -o '^| \*\*I[0-9]*\*\*' mechanism/GAPS-AND-ASSUMPTIONS.md` -> I1 to I24 and I27 to I49, 47 rows, in the order I20, I27, I21; `grep -rn 'I25\|I26' mechanism decisions/ADR-0033.md` -> empty; decisions/ADR-0033.md:257, :296; mechanism/GAPS-AND-ASSUMPTIONS.md:81-87, :127

