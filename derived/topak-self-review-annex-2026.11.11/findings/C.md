# Self review of 2026.11.11: reader C's findings in full

Reader C read policy, lease, clock and confinement. Annex to `derived/topak-open-findings-register-2026.11.11.md`, Part III. Each block is the finding as the reader wrote it, against the tree at `bbda621`, followed by the verdict of a verifier that did not find it. Paths are relative to the repository root. A path a finding names as absent is written without backticks. Nothing here is ratified, and every reader and verifier is of the same model lineage as the drafter of the corpus.

52 reported: 32 confirmed, 17 confirmed with a correction, 3 dropped.

### C-1: ADR-0030's header says the reference links the `emergency` floor; it links `workflow`
- Against: decisions/ADR-0030.md:20-21 (and checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:118; mechanism/crates/topak-floor/src/lib.rs:30)
- Basis: in force
- Claim: "since Batch 34 that is `floor/proposed/emergency-floor.cedar` and its schema, which the reference links"
- Why wrong: G11:118 "**The reference links it** (ADR-0033 A16), at the custodian's direction. The floor the reference follows is therefore not the floor in force." (of the `workflow` stage). lib.rs:30 `pub const FLOOR_SRC: &str = include_str!("../../../../floor/proposed/workflow-floor.cedar");`. floor/proposed/README.md:3 "**the reference links the `workflow` stage** (since 2026.10.08; `emergency` from 2026.10.05)".
- Fix belongs in: decisions/ADR-0030.md header (Status note)
- Severity: Medium
- Confidence: high
- Already on the corpus's own lists: G11 item 102 lists the fact (the reference links a floor not in force); the header sentence is not listed
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0030.md:20-21 (quote exact); mechanism/crates/topak-floor/src/lib.rs:28-30 (FLOOR_SRC includes workflow-floor.cedar; 'The floor in force is still the `emergency` stage'); floor/proposed/README.md:3; checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:118 and :349 (item 102). `grep -n -i 'workflow\|A16' decisions/ADR-0030.md` returns nothing, so no later row reconciles the header.

### C-2: floor/README.md gives three answers to "which floor does the reference link"
- Against: floor/README.md:5 (and floor/README.md:15, floor/README.md:22)
- Basis: living document
- Claim: "It links the `labels` stage in `proposed/`" (line 5); "`proposed/` | **Not this floor.** … Nothing loads it" (line 15)
- Why wrong: The same file, line 22: "the `emergency` stage in force and, since 2026.10.08, the `workflow` stage the reference links (`Linked.lean`)". mechanism/crates/topak-floor/src/lib.rs:30 includes `floor/proposed/workflow-floor.cedar`; mechanism/GAPS-AND-ASSUMPTIONS.md:49 "`labels` at `c15026d`, `control` at `c7de2ba`, then `emergency`", :50 "**Linked since 2026.10.08**". Line 5 names a stage two switches old; line 15 says nothing loads a directory the reference pins by digest.
- Fix belongs in: floor/README.md
- Severity: Medium
- Confidence: high
- Already on the corpus's own lists: no (G11 items 91 and 102 concern the stage files' opening comment and the linked floor, not this README)
- **Verifier:** confirmed with correction
- **Verifier's correction:** Count: `labels` is three switches old, not two (labels -> control -> emergency -> workflow). The rest stands as written.
- **Verifier's evidence:** floor/README.md:5, :15, :22 (all three quotes exact); floor/proposed/README.md:6-8 (labels at c15026d, control at c7de2ba, emergency at 9c57221, workflow on 2026.10.08); mechanism/GAPS-AND-ASSUMPTIONS.md:49-50; mechanism/crates/topak-floor/src/lib.rs:30

### C-3: ADR-0030 still carries the ToO revision as an open debt; the ToO made all four rewrites
- Against: decisions/ADR-0030.md:23 and decisions/ADR-0030.md:497-499 (and narrative/theory-of-operation.md:73, :168, :187, :678, :1999)
- Basis: in force
- Claim: "the **ToO revision** of §1, §2.4, §3.1 and §11.3;" (face, unstruck) and "- **The ToO's next revision** rewrites §1 (O as a role), §2.4 (the retired SMT sentence, and ⟨R4⟩ the recusal sentence: relaxing recusal is a floor relaxation, not a mechanism release), §3.1 (composition), and §11.3" (Open obligations, unstruck)
- Why wrong: ToO rev 15: :73 "**The letters name roles, not products** (ADR-0030 §2, ADR-0033 §2)."; :168 "Earlier revisions said Rego predicates checked by an SMT solver; that needed a mechanized Rego semantics nobody has"; :187 "**The envelope is floor text** : forbid B7 in the policy floor (ADR-0030) : so relaxing recusal is a policy-floor"; :678 "> **admit ⟺ floor_permit ∧ ¬bundle_deny**"; :1999 "**The floor now has a non-vacuity gate; TLA+ invariants still do not.**". Appendix C (changes from revision 6), :2718, already lists "**The letters name roles** (§1)". Every other discharged debt on this face is struck with a pointer; this one is not.
- Fix belongs in: decisions/ADR-0030.md (Status note debts; Open obligations)
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed with correction
- **Verifier's correction:** The sentence 'Every other discharged debt on this face is struck with a pointer; this one is not' is wrong by the reader's own C-4: the engine-divergence residual (ADR-0030.md:24-25) is also discharged and unstruck. The defect itself stands: both ToO-revision entries are unstruck and all four rewrites are in ToO revision 15.
- **Verifier's evidence:** decisions/ADR-0030.md:23, :497-499 (quotes exact); narrative/theory-of-operation.md:3 (revision 15), :73 (in §1), :168 and :187 (in §2.4, heading at :149), :678 (in §3.1, heading at :661), :1999 (in §11.3, heading at :1992), :2718 (Appendix C). `grep -n ToO decisions/ADR-0030.md` shows no History row recording the revision.

### C-4: The engine-divergence debt is struck in Open obligations and declared discharged in History, but stands unstruck on the face
- Against: decisions/ADR-0030.md:24-25 (and decisions/ADR-0030.md:502-504, :533)
- Basis: in force
- Claim: "the **engine-divergence residual**, owed to the TCB declaration record;"
- Why wrong: :502-504 "~~**The engine-divergence residual** (§3) goes into the TCB declaration record when that record is written.~~ **ADR-0045 T-0045-3**, ratified 2026.10.01 (Batch 22)"; B22 row, :533 "the debt on the face that named the TCB declaration record is discharged in the record". The face text was not changed.
- Fix belongs in: decisions/ADR-0030.md header
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0030.md:24-25 (unstruck on the face), :502-504 (struck in Open obligations), :533 (B22: 'the debt on the face that named the TCB declaration record is discharged in the record'); contrast :530 (B17: 'The debt on the face is struck') and the struck bundle-signing debt at :25-27

### C-5: B36 says §5's totality, non-vacuity and discrimination gates are proved in Lean; the Lean theorems state less
- Against: decisions/ADR-0030.md:565 (and floor/lean/README.md:17-18, :27, :32; checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:110)
- Basis: evidence
- Claim: "names `floor/lean/` and `TopakFloor-results-2026.10.06.txt` for §5's totality, non-vacuity and discrimination gates, on the genesis floor and the floor in force"
- Why wrong: §5 defines totality as "Validation against S, and **never-errors** over the whole floor" (ADR-0030.md:205). floor/lean/README.md:17-18 "never errors on a schema-conforming input except for three runtime errors the validator cannot see"; :27 "`floor_never_errors` | … every policy evaluates to a boolean or to `entityDoesNotExist`, `extensionError` or `arithBoundsError`". On the genesis floor discrimination is proved for nine of ten actions: :32 "`not_always_denies_but_erase` | discrimination: for each action but `Erase`", whereas the SymCC gate reports "Erase      always-allows refuted  always-denies refuted  pass" (floor/genesis-gates-results-2026.10.01.txt:45). The results file lists `not_always_denies_but_erase` (floor/lean/TopakFloor-results-2026.10.06.txt:7). The checkpoint names a different trio: G11:110 "totality, validation and non-vacuity gates of each". floor/README.md:22 also says "non-vacuity and discrimination witnesses per action" without the `Erase` exception.
- Fix belongs in: decisions/ADR-0030.md History B36 (and floor/README.md:22; the checkpoint and the record should name the same gates)
- Severity: Medium
- Confidence: medium
- Already on the corpus's own lists: no (G11 item 107 lists `native_decide` in the floor package, not the gap between the gate and the theorem)
- **Verifier:** confirmed with correction; severity Low-Medium (reader: Medium)
- **Verifier's correction:** The totality limb is narrower than stated. The finding omits `floor_no_ext_no_arith` (floor/lean/README.md:29): the floor calls no extension and does no arithmetic, so of the three residual errors only `entityDoesNotExist` can occur, which the README classes as a lift fault (ADR-0030 §4); the README itself calls the result 'ADR-0030 §5's totality gate proved as a theorem' (:4) and ADR-0053.md:69 says 'except by a missing entity'. What stands: on the genesis floor discrimination is proved for nine of ten actions (`not_always_denies_but_erase`), while B36, ADR-0053.md:69 and :205 and floor/README.md:22 say discrimination 'per action' with no exception, and G11:110 names a different trio (totality, validation, non-vacuity). Fix should also name ADR-0053.md:69, :205, :317-318, which B36 echoes.
- **Verifier's evidence:** decisions/ADR-0030.md:565, :205-207; floor/lean/README.md:4, :17-19, :27, :29, :32, :47; floor/lean/TopakFloor-results-2026.10.06.txt:7; floor/genesis-gates-results-2026.10.01.txt:45; decisions/ADR-0053.md:69, :205, :317-318; checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:110; floor/README.md:22

### C-6: §4's PARC table puts `fence` in the floor's Context; schema S has no such field
- Against: decisions/ADR-0030.md:193 (and floor/genesis.cedarschema:53-94)
- Basis: in force
- Claim: "| Context | Epoch, `fence`, `rulesEpoch`, round, and the lease fields the floor needs (ADR-0031) |"
- Why wrong: genesis.cedarschema:53-56 defines `type Lease = { alphabet: Set<String>, rulesEpoch: Long, };`; BuildCtx, VoteCtx, RunCtx and EraseCtx (:58-94) carry `epoch`, `round`, `rulesEpoch`, and no `fence`. `grep -n -i fence floor/genesis.cedarschema floor/proposed/*.cedarschema` returns only the header comment ("rejects a fenced epoch before the floor is consulted"), the `Fleet` entity, the `FenceEpoch` action and a comment on `freshAssertion`.
- Fix belongs in: decisions/ADR-0030.md §4 (or schema S)
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0030.md:193 (quote exact); floor/genesis.cedarschema:53-94 (no `fence` field in Lease or any context). `grep -n -i fence floor/genesis.cedarschema floor/proposed/*.cedarschema` returns only the header comment, `entity Fleet`, the `freshAssertion` comment and `action FenceEpoch`, as the finding says.

### C-7: FloorRouting models one floor-wide non-vacuity gate and no other gate; §5 and §10 state the gates per action, and B25 misnames what the modules cover
- Against: decisions/ADR-0030.md:394-396 and :535 (and spec/FloorRouting.tla:45-46; spec/FloorComposition.tla:2)
- Basis: evidence
- Claim: §9 "**Model, routing.** A floor is its meaning, the set of requests it permits, over a three-request universe" with the row "Non-vacuity gate off | `M_GATE` | `FloorNeverVacuous`"; B25 "**The module properties of §1, §4 and §5 are proved.**"
- Why wrong: FloorRouting.tla:45-46 "\* ADR-0030 §5 non-vacuity: not always-allows." / "PassesGates(new) == IF Mut = "M_GATE" THEN TRUE ELSE new # U" is the only gate. §5 states three gates under the header "| Gate | Check over S, per action |" (ADR-0030.md:203), and §10 finding 2 says "A single floor-wide non-vacuity answer would hide which action classes a floor actually bounds" (:466-467). The module's gate is exactly that single answer; it admits the empty floor (`{}` # U), so discrimination ("not always-denies") is not modelled, nor totality. §9's Scope (:432-434) does not say so. Separately, FloorComposition.tla:2 reads "Properties for ADR-0030 §1, §3 and §4" and tags `BundleCannotWriteFloorInputs §3` (:8); B25 lists "§1, §4 and §5" and omits §3.
- Fix belongs in: decisions/ADR-0030.md §9 Scope and History B25
- Severity: Low-Medium
- Confidence: medium
- Already on the corpus's own lists: no
- **Verifier:** confirmed with correction; severity Low (reader: Low-Medium)
- **Verifier's correction:** No text claims the per-action gates are modelled, so this is an unstated abstraction and not a conflict: §9's Scope (ADR-0030.md:432-434) already limits the modules to 'a discrimination test of the composition and routing rules, not a check of Cedar, SymCC or any real floor', the §9 row names `FloorNeverVacuous` only, and B25 names the two routing properties proved. What stands: Scope does not say non-vacuity is modelled as the single floor-wide answer §10 finding 2 warns against (the module admits the empty floor), and B25's '§1, §4 and §5' omits §3, which FloorComposition.tla:2 and :8 tag.
- **Verifier's evidence:** spec/FloorRouting.tla:8-9, :27, :45-46, :75; spec/FloorComposition.tla:2, :8; decisions/ADR-0030.md:203, :394-396, :409-412, :432-434, :464-467, :535

### C-8: §5 quotes ADR-0028 §2 with a different verb
- Against: decisions/ADR-0030.md:225 (and decisions/ADR-0028.md:67)
- Basis: in force
- Claim: "That is ADR-0028 §2's rule ("bundles can only narrow erasure further")"
- Why wrong: ADR-0028.md:67 "- **Bundles may only narrow erasure further**; this is monotone."
- Fix belongs in: decisions/ADR-0030.md §5
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0030.md:225 ('bundles can only narrow erasure further'); decisions/ADR-0028.md:67 ('Bundles may only narrow erasure further'). `grep -rn -i 'only narrow erasure' decisions/ narrative/` returns only these two lines.

### C-9: The floor's B7 comment calls recusal a mechanism constant relaxed by a mechanism release; ADR-0030 says the opposite
- Against: floor/genesis-floor.cedar:81-82 (and decisions/ADR-0030.md:297, :469-470, :498)
- Basis: evidence
- Claim: "A mechanism constant, stated in the floor; relaxing it is a floor relaxation shipped as a mechanism release."
- Why wrong: ADR-0030.md:498 "relaxing recusal is a floor relaxation, not a mechanism release"; :469-470 "relaxing it becomes a floor relaxation: an anchor issuance *and* a promotion"; Options row :297 "Recusal kept out of the floor, as a mechanism constant only ⟨R4⟩ | Rejected". The comment names neither the issuance nor the promotion, and names the path the record retired.
- Fix belongs in: floor/genesis-floor.cedar (a digest-pinned file; a change is a new gate run)
- Severity: Low-Medium
- Confidence: medium
- Already on the corpus's own lists: no (G11 item 91 is about the stage files' opening comment)
- **Verifier:** confirmed with correction; severity Low (reader: Low-Medium)
- **Verifier's correction:** The title overstates: the comment does not say the opposite. It calls relaxation 'a floor relaxation', as ADR-0030 does, and ADR-0030 §3 (:141) says the floor text ships in the mechanism release, so 'shipped as a mechanism release' is true of the vehicle; 'mechanism constant' is also the corpus's word for recusal (ADR-0024.md:73), and the Options row rejects it only as 'mechanism constant only'. What stands is narrower: the comment names the release and neither the anchor issuance nor the promotion, against :498 'a floor relaxation, not a mechanism release' and ADR-0022.md:145-147. Scope is wider than cited: the same two lines are in all four stage files at :83-84, the floor in force and the linked floor among them.
- **Verifier's evidence:** floor/genesis-floor.cedar:81-82 (quote exact); floor/proposed/{labels,control,emergency,workflow}-floor.cedar:83-84; decisions/ADR-0030.md:141, :297, :468-471, :498; decisions/ADR-0022.md:144-148

### C-10: The floor text and schema S still call ADR-0040 and ADR-0041 Proposed
- Against: floor/genesis-floor.cedar:112 and floor/genesis.cedarschema:104 (and decisions/ADR-0040.md:15, decisions/ADR-0041.md:12)
- Basis: evidence
- Claim: "// Run envelopes : ADR-0040 §1, stated as ADR-0041 §1 (both Proposed)" and "// ---- Run's alphabet (ADR-0040 §1, Proposed)"
- Why wrong: ADR-0040.md:15 "**Status:** Accepted (genesis) · 2026.09.30"; ADR-0041.md:12 "**Status:** Accepted (genesis) · 2026.09.30"; floor/README.md:40-41 "both ratified 2026.09.30 (Batch 20)". floor/README.md:19 also keeps "(both Proposed)" in its table row.
- Fix belongs in: floor/genesis-floor.cedar, floor/genesis.cedarschema (digest-pinned), floor/README.md:19
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed with correction
- **Verifier's correction:** Scope is wider and one instance weaker. The same comments are in every stage file, including the floor in force and the linked floor: floor/proposed/emergency-floor.cedar:118, emergency.cedarschema:132, workflow-floor.cedar:118, workflow.cedarschema:144 (also labels and control). The stage schemas also call ADR-0050 Proposed (emergency.cedarschema:139, workflow.cedarschema:154; ADR-0050 is Accepted, provisional). floor/README.md:19 is a dated row describing the 09.29 run, when both records were Proposed, so it is the weakest instance.
- **Verifier's evidence:** floor/genesis-floor.cedar:112; floor/genesis.cedarschema:104; `grep -n Proposed floor/genesis-floor.cedar floor/genesis.cedarschema floor/proposed/*.cedar floor/proposed/*.cedarschema`; decisions/ADR-0040.md:15; decisions/ADR-0041.md:12; decisions/ADR-0050.md:20; floor/README.md:19, :40-41

### C-11: The values file and the floor README say `T_persona` is pending and not read by the reference; it is ratified and compiled in
- Against: floor/genesis-values.json:13 and :15; floor/README.md:20 and :51-52 (and decisions/ADR-0031.md:371; mechanism/crates/topak-floor/src/lib.rs:37)
- Basis: evidence
- Claim: `"_record": "ADR-0031 A2 (Pending); ADR-0016 §6"` … "Not yet read by the reference." (values file); "added on 2026.09.30 for ADR-0031 A2 (Pending) and is not yet read by the reference" (README :52)
- Why wrong: ADR-0031.md:371 "**A2**, ratified 2026.09.30 (Batch 17): `ttl ≤ T_persona`. **Built 2026.10.01** (ADR-0033 A6, Batch 23): refused at grant and at renewal in `apply`; the bound is a floor constant read from the values file". lib.rs:37 `pub const VALUES_SRC: &str = include_str!("../../../../floor/genesis-values.json");`; mechanism/GAPS-AND-ASSUMPTIONS.md:93 "`T_persona` is the values file's `persona.T_persona_ms`, compiled in with the floor". The same file's line 10 says "(ADR-0042 §2, Proposed)"; decisions/ADR-0042.md:13 is Accepted. The reference pins this file by digest (lib.rs:51), so it links a file that says of itself that it is not read.
- Fix belongs in: floor/genesis-values.json (digest-pinned: a change moves the pins) and floor/README.md
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** floor/genesis-values.json:10, :13, :15 (quotes exact); floor/README.md:20, :51-52; decisions/ADR-0031.md:371; decisions/ADR-0042.md:13; mechanism/crates/topak-floor/src/lib.rs:37, :51, :102-104, :134-135 (the `persona` block is parsed); mechanism/GAPS-AND-ASSUMPTIONS.md:93

### C-12: Policy comments call ADR-0030 and ADR-0041 Proposed, beyond the two ADR-0049 comments the list names
- Against: policies/bundle.rego:2 and policies/actuate.rego:2 (and policies/actuate.rego:15, policies/tool_schema.rego:11)
- Basis: evidence
- Claim: "# PLACEHOLDER · 2026.09.24 · not promoted · bundle tier under ADR-0030 (Proposed)"; "bundle tier under ADR-0030 · ADR-0041 §5 (Proposed)"
- Why wrong: decisions/ADR-0030.md:10 "**Status:** Accepted (genesis) · 2026.09.25"; decisions/ADR-0041.md:12 "Accepted (genesis) · 2026.09.30". actuate.rego:15 "The channel's form is ADR-0049's (Proposed)" and tool_schema.rego:11 "The entry's form is ADR-0049's (Proposed)" against decisions/ADR-0049.md:15 "Accepted (genesis) · 2026.10.05".
- Fix belongs in: policies/bundle.rego, policies/actuate.rego, policies/tool_schema.rego (a comment is part of the bundle's revision)
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: G10 item 98 (as at G11) covers the two ADR-0049 comments only; the ADR-0030 and ADR-0041 comments are not listed
- **Verifier:** confirmed
- **Verifier's evidence:** policies/bundle.rego:2; policies/actuate.rego:2, :15; policies/tool_schema.rego:11 (`grep -n Proposed policies/*.rego` returns exactly these four); decisions/ADR-0030.md:10; decisions/ADR-0041.md:12; decisions/ADR-0049.md:15; checkpoints/topak-genesis-checkpoint-G10-2026.10.05.md:375 (item 98: two ADR-0049 comments only); checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:323 ('An item not listed is as at G10')

### C-13: An in-force clause of ADR-0031 calls ADR-0050 Proposed
- Against: decisions/ADR-0031.md:84-85 (and decisions/ADR-0050.md:20; decisions/ADR-0031.md:423)
- Basis: in force
- Claim: "This record says what a grant is and never who makes one. ADR-0050 (Proposed) does."
- Why wrong: ADR-0050.md:20 "**Status:** Accepted (genesis) · provisional · 2026.10.05"; the record's own B34 row, :423, "with ADR-0050, ratified in the same batch". B34 also says "the text marked ⟨A3⟩ is in force as written", so the word is in force as written and false.
- Fix belongs in: decisions/ADR-0031.md §2
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0031.md:84-85 (quote exact), :423 (B34: 'the text marked ⟨A3⟩ is in force as written'); decisions/ADR-0050.md:20-21

### C-14: A3's History row marks ADR-0031 confirmation-required under C3; the status line, the index and G11 carry C1 and C2 only
- Against: decisions/ADR-0031.md:9 and :422 (and decisions/README.md:44; checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:50)
- Basis: in force
- Claim: "**Status:** Accepted (genesis) · 2026.09.25 · confirmation required (ADR-0029 C1; C2 for A1 only)"
- Why wrong: A3 row, :422: "**Confirmation required under C1 and C3**, as ADR-0050 is: who may put a lease on the log changes". The Status note (:10-12) names C1 and C2 only; README.md:44 "confirmation required: C1; C2 for A1 only"; G11:50 "0031 (C2 for A1 only, beside its C1)". Either the row over-claims or three places under-mark a reversal in effect.
- Fix belongs in: decisions/ADR-0031.md (status line or A3 row), then decisions/README.md and the next checkpoint
- Severity: Medium
- Confidence: medium
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0031.md:9, :10-12 (C1; C2 for A1 only), :422 ('**Confirmation required under C1 and C3**, as ADR-0050 is: who may put a lease on the log changes'), :423 (B34 says nothing on the marking); decisions/README.md:44; checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:50; decisions/ADR-0050.md:20 (C1, C3, C4)

### C-15: Two ratified amendments still read "Pending" in their own History rows
- Against: decisions/ADR-0031.md:399 and decisions/ADR-0034.md:501 (and decisions/ADR-0031.md:13, :400; decisions/ADR-0034.md:16, :502)
- Basis: in force
- Claim: ADR-0031 A2 row: "**Pending** : drafted 2026.09.30. … The reference does not yet check it"; ADR-0034 A1 row: "**Pending** : drafted 2026.09.30."
- Why wrong: ADR-0031.md:13 "A2 ratified 2026.09.30 (Batch 17)" and :371 "**Built 2026.10.01**"; ADR-0034.md:16 "A1 ratified 2026.09.30 (Batch 17)". Sibling amendment rows were rewritten on ratification (ADR-0031 A1 row, :396, "**Applied** : ratified 2026.09.28 (Batch 10)"; ADR-0030 A1 row, ADR-0030.md:532, "**Applied** ⟨B24⟩"), so the typed State column follows two conventions.
- Fix belongs in: decisions/ADR-0031.md and decisions/ADR-0034.md History
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed with correction
- **Verifier's correction:** Scope: these are not two isolated rows. The same form (amendment row left 'Pending — drafted', ratification recorded in the next B row) is at ADR-0003.md:83 and ADR-0033.md:1141, :1144, :1146, :1150, so it is a second convention across the corpus, beside the rewritten-on-ratification form (ADR-0031.md:396, ADR-0030.md:532). In both cited cases the next row gives the true state (ADR-0031.md:400-401; ADR-0034.md:502), and 'The reference does not yet check it' is answered by the B23 row at :401.
- **Verifier's evidence:** decisions/ADR-0031.md:13, :396, :399-401; decisions/ADR-0034.md:16, :501-502; decisions/ADR-0030.md:532; `grep -n '| \*\*Pending\*\* — ' decisions/ADR-003[0-6].md`

### C-16: §2 (A3) says §4 calls Persona, seat and the alphabet unordered; §4 names four other things
- Against: decisions/ADR-0031.md:95-96 (and decisions/ADR-0031.md:152-158)
- Basis: in force
- Claim: "***A change of Persona, bundle, confinement or seat, or a wider alphabet, is a first lease**, as §4 already implies by calling none of them ordered.*"
- Why wrong: §4, :153-155: "A renewal keeps `round` and `role` unchanged ⟨R1⟩, keeps `bundle` unchanged ⟨R2⟩, and keeps `confinement`, digest and rung, unchanged ⟨A1⟩. None of the ~~three~~ four is ordered in the sense renewal needs." The four are round, role, bundle and confinement. §4 says nothing of Persona or seat, and it orders the alphabet (:152 "a renewal may narrow the alphabet,"). `role`, which §4 does call unordered, is missing from A3's list, so a change of role across rounds has no stated path (it cannot be "narrower"). ADR-0050.md:107-108 repeats the attribution ("ADR-0031 §4 says none of these is ordered").
- Fix belongs in: decisions/ADR-0031.md §2 (and ADR-0050 §2)
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed with correction
- **Verifier's correction:** One sub-claim overstated: a change of role does have a stated path. ADR-0031 §4 (:158) says 'A change of any of the four is a grant' and ADR-0050.md:107 says 'Anything else is a first lease'. Only ADR-0031's own A3 list omits `role`. The misattribution stands: §4 calls round, role, bundle and confinement unordered, says nothing of Persona or seat, and orders the alphabet.
- **Verifier's evidence:** decisions/ADR-0031.md:95-96 (quote exact), :152-158; decisions/ADR-0050.md:103-109

### C-17: §5 (A3) says both revocation tools are an operator's; a Contested revocation is ordered on a verifier's verdict and is not
- Against: decisions/ADR-0031.md:198-199 (and decisions/ADR-0034.md:191, :213-218)
- Basis: in force
- Claim: "**Who denies.** Both tools are an operator's (ADR-0050 §4): signed with its Persona's key, by any operator whose Persona is in force"
- Why wrong: ADR-0034.md:191 "**Contested** | … | Refuse, and order a **targeted revocation of the principal** (ADR-0031 §5)"; :213-218 "**who may order a Contested revocation.** Only a verdict signed by a verifier whose key the issued rules carry … an operator who distrusts a principal has the plain targeted `Revoke` of ADR-0031 §5, which claims nothing about evidence and is attributed to the operator." So a targeted revocation has a second issuer, with a different signature and attribution, that "Who denies" omits; spec/Confinement.tla:149-153 revokes inside `Appraise` with no operator.
- Fix belongs in: decisions/ADR-0031.md §5
- Severity: Medium
- Confidence: medium
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0031.md:195, :198-201; decisions/ADR-0034.md:191, :213-218; spec/Confinement.tla:141-153; spec/Mechanism.tla:652-657 (`ApplyContested`: a signed verdict, checked against `verifierKeys`, no operator). `grep -n -i contested decisions/ADR-0050.md` returns nothing, and in ADR-0031 the word occurs only at :142, :365, :398, so neither 'Who denies' nor ADR-0050 §4 mentions the verifier's path.

### C-18: ADR-0031 names `T_persona` the mandatory re-attestation interval, on the local clock; ADR-0034 says no re-attestation interval exists; ADR-0032 puts such intervals on trusted time
- Against: decisions/ADR-0034.md:207-208 (and decisions/ADR-0031.md:68, :273-274; decisions/ADR-0032.md:54)
- Basis: in force
- Claim: "No re-attestation interval exists, so ADR-0032 §2's trusted-time requirement for one does not arise."
- Why wrong: ADR-0031.md:273-274 "**The Persona is re-attested at least every `T_persona`** ⟨A2⟩, which is the mandatory re-attestation interval the open obligation asked for"; :68 "`ttl` | Expiry, as a duration on the local monotonic clock; **at most `T_persona`**". ADR-0032.md:54 lists "break-glass TTL, Persona expiry, re-attestation intervals" under "**trusted time**". ADR-0045.md:293-297 says the same of the pair: "a slow clock extends the re-attestation interval past `T_persona`, which ADR-0032 §2 classes as preserving authority and assigns to trusted time … Routed to ADR-0032 and ADR-0031", and neither record's decision text took the route; ADR-0034 Options (:399) still rejects "Interval-based re-attestation" because "It needs trusted time".
- Fix belongs in: decisions/ADR-0034.md §3.6; decisions/ADR-0032.md §2; decisions/ADR-0031.md §1/§4
- Severity: Medium
- Confidence: high
- Already on the corpus's own lists: G9 item 62 "`T_persona` on a local clock" (open, as at G11) and ADR-0045 finding 2 cover the clock; the ADR-0034 §3.6 sentence is not listed
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0034.md:202-209 (quote exact at :207-208), :399; decisions/ADR-0031.md:68, :160-161, :273-274; decisions/ADR-0032.md:54; decisions/ADR-0045.md:293-298. `grep -n 'T_persona\|ADR-0045' decisions/ADR-0032.md` returns nothing, and ADR-0031 notes the clock only in its B23 History row (:401). The clock half is the corpus's open item 62 (checkpoints/topak-genesis-checkpoint-G9-2026.10.02.md:296); the ADR-0034 sentence is not listed.

### C-19: §6's table omits two of the twelve fields it says it derives
- Against: decisions/ADR-0031.md:230-234 (and decisions/ADR-0031.md:57-58, :227-228)
- Basis: in force
- Claim: "every field is either discharged by a check at grant, or it is an assumption of use."
- Why wrong: The table's three rows cover `persona`, `confinement`, `bundle`, `alphabet`, `round`, `role`; `epoch`, `fence`, `rulesEpoch`; and `ttl` : ten fields. §1 (:57-58) also lists `principal` and `seat`, and History R1 (:390) counts "twelve fields". The "TCB enumeration, serialized" does not say whether the seat and the principal's identity are checked or assumed.
- Fix belongs in: decisions/ADR-0031.md §6
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0031.md:57-68 (twelve field rows, `principal` and `seat` first), :226-228, :230-234 (ten fields in three rows), :390 ('twelve fields')

### C-20: §3 points at "(§8)" for the attestation-rung record; §8 is the property check
- Against: decisions/ADR-0031.md:143 (and decisions/ADR-0031.md:308, :365-366)
- Basis: in force
- Claim: "belong to the attestation-rung record that discharges ADR-0022 §6 (§8)."
- Why wrong: :308 "## 8. Property check : run 2026.09.23". The obligation it means is the first bullet of the unnumbered "## Open obligations" (:365-366), now struck: "~~**Rungs 1–3** …~~ **ADR-0034**, ratified 2026.09.28". The pointer survived the insertion of §7 and §8.
- Fix belongs in: decisions/ADR-0031.md §3
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed with correction
- **Verifier's correction:** Drop the causal sentence ('The pointer survived the insertion of §7 and §8'): the tree does not show what '(§8)' once pointed to; History C1 (:389) says only that §8 was added before ratification. The dangling pointer itself stands.
- **Verifier's evidence:** decisions/ADR-0031.md:143, :292 (§7 heading), :308 (§8 heading), :363-366, :389

### C-21: §8 does not say that the module's revocation set holds principals only
- Against: decisions/ADR-0031.md:316-319 (and spec/Lease_A1.tla:38-39; decisions/ADR-0031.md:195)
- Basis: evidence
- Claim: "**Model.** Two principals; … targeted revocation with a revocation set ⟨R3⟩, end-of-round. … The round number is not modeled … Nor is the bundle"
- Why wrong: §5, :195 "A target is a principal, a Persona digest or a confinement digest." Lease_A1.tla:38-39 "`revoked` holds principals; in the mechanism it holds principals, Persona digests and confinement digests, which a principal stands for here." The record lists two things not modelled and omits this one, so `RevokedStaysStopped` and the `M_REVOKE` row are evidence for one of the three target kinds. §8 also does not point to where A3's successor-grant rule is checked (spec/Operators.tla:16 `SuccessorNeverWidens`); Lease_A1.tla:78 still reads "A fresh grant: any authority".
- Fix belongs in: decisions/ADR-0031.md §8
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0031.md:195, :316-319; spec/Lease_A1.tla:38-39, :78; spec/Operators.tla:16. `sed -n '308,362p' decisions/ADR-0031.md | grep -n -i 'Persona digest\|confinement digest\|stands for\|Operators'` returns nothing. Note: the A3 History row (:422) does name `spec/Operators.tla` as its source; §8 does not.

### C-22: The R1 state count has no results file behind it
- Against: decisions/ADR-0031.md:337 (and decisions/ADR-0031.md:313-314; spec/Lease-results-2026.09.25.txt:16)
- Basis: evidence
- Claim: "The R1 rerun (2026.09.25) repeated every row; `Safe` held over 1,605,720 distinct states"
- Why wrong: :313-314 "The R1 digest, `575b3d9f51bb8f64`, was superseded the same day by R3; the results file holds the R3 run." Lease-results-2026.09.25.txt:16 reads "9698469 states generated, 1746048 distinct states found"; `grep -rl 1605720 spec/` and `grep -rl "1,605,720" spec/` return nothing.
- Fix belongs in: decisions/ADR-0031.md §8
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0031.md:313-314, :337; spec/Lease-results-2026.09.25.txt:16 (1746048); spec/Lease-results-2026.09.23.txt:13 (436512). `grep -rl 1605720 spec/` and `grep -rl '1,605,720' spec/` return nothing; outside the record the figure occurs only in diagrams/ (d_c3_lease_anatomy.py:380 and its SVG).

### C-23: ADR-0054 calls the third grant path "ADR-0031 A3"; in ADR-0031 it is A4, and A3 is another amendment, in force
- Against: decisions/ADR-0054.md:41 and :296 (and decisions/ADR-0031.md:13, :424; decisions/ADR-0054.md:301)
- Basis: pending
- Claim: "ADR-0031 A3 (a third grant path, §2)" and "ADR-0031 A3 (the third grant path)"
- Why wrong: ADR-0031.md:13 "**Pending:** **A4**, drafted 2026.10.08, dependent on ADR-0054 (Proposed): a third grant path, a workflow's node (§2)"; A3 is "who grants and who denies", ratified in Batch 34 (:422-423). ADR-0054.md:301 itself says "drafted 2026.10.08 as ADR-0015 A1, ADR-0024 A4, ADR-0031 A4".
- Fix belongs in: decisions/ADR-0054.md
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** not confirmed
- **Verifier's correction:** The texts do not conflict. Read in context, each item of ADR-0054's debt list names the existing clause the debt is against, with the change owed in parentheses, and :301 names the amendment drafted to pay it: 'ADR-0024 A3 (a workflow is a set of seatings and a graph)' is paid by ADR-0024 A4, 'ADR-0037 §4 (a sixth seat kind)' by ADR-0037 A5, and 'ADR-0031 A3 (a third grant path)' by ADR-0031 A4. ADR-0031 A3 is the in-force 'who grants' text (two paths) that a third path is added beside; ADR-0054.md:105 cites it in that sense, and :305 asks that ADR-0024 A3, the existing 'A promotion seats', be ratified first. ADR-0054 does not call the third grant path A3.
- **Verifier's evidence:** decisions/ADR-0054.md:41-46, :105, :296-305; decisions/ADR-0031.md:13, :422, :424; decisions/ADR-0024.md:325 (A3: 'A promotion seats'), :327 (A4: 'A workflow is a set of seatings and a graph')

### C-24: ADR-0032 says none of C1–C4 applies while its own header says it discharges an accepted record's open obligation
- Against: decisions/ADR-0032.md:10-11 (and decisions/ADR-0032.md:17, :180-181; decisions/ADR-0029.md:69; decisions/ADR-0024.md:286, :289)
- Basis: in force
- Claim: "Confirmation required: no. None of C1–C4 applies : no proof obligation over privileged paths, no exhaustiveness or confinement claim, no reversal of an accepted record."
- Why wrong: The sentence gives a reason for C1, C2 and C3 and none for C4. ADR-0029.md:69 "**C4** Resolves a debt owed by an accepted record". ADR-0032.md:17 "**Discharges:** ADR-0031 §7; ADR-0024's clock-model open obligation; boundary register §9.1". ADR-0024 was accepted first: ADR-0024.md:286 "**Ratified 2026.09.23** … in Batch 2 … Open obligations : clock model, independent evidence, seat diversity, the liveness assumption, veto-seat outage : are unchanged and carried", and :289 "the clock-model bullet is struck as discharged. ADR-0032 supplies the model". Other records in this scope take C4 for exactly this (ADR-0034.md:13 "**C4** (resolves ADR-0031's attestation-rung debt)"). The B5 note (:180-181) draws the consequence: "**it will never be reviewed by the first quorum either.**"
- Fix belongs in: decisions/ADR-0032.md Status and B5 (and the index and next checkpoint, which list it without a marker)
- Severity: Medium-High
- Confidence: medium
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0032.md:9-12 (quote exact; reasons given for C1, C2, C3 and none for C4), :17, :176, :179-183; decisions/ADR-0029.md:62 ('if it meets **any** of these'), :69; decisions/ADR-0024.md:286 (Batch 2: the clock-model open obligation 'unchanged and carried'), :289; checkpoints/topak-genesis-checkpoint-G2-2026.09.23.md:217-218 (ADR-0024 accepted before the cut, ADR-0032 after). Stronger than the reader's example: decisions/ADR-0039.md:14 takes C4 because 'it resolves ADR-0024's open obligation on veto-seat outage', a sibling of the clock-model bullet in the same B2 list; also ADR-0034.md:13, ADR-0031.md:12 ('The open obligations are carried as debts'). Unmarked at decisions/README.md:45 and G11:49. ADR-0031 §7 does not count: ADR-0031 was Proposed on 09.23.

### C-25: ADR-0032's trusted-time row has no surviving instance, and the record still carries R8 and Persona expiry as open
- Against: decisions/ADR-0032.md:54, :63-64, :160-162 (and decisions/ADR-0026.md:13, :291-293; decisions/ADR-0045.md:203, :437; decisions/ADR-0031.md:68)
- Basis: in force
- Claim: "| **Adds or preserves** authority | **trusted time**: a signed, attested time source outside the principal | break-glass TTL, Persona expiry, re-attestation intervals |"; "- **R8**, the break-glass grant TTL, now with its trusted-time cost named (ADR-0026 candidate entry)."; "- **Persona expiry / re-attestation interval** (ADR-0016; boundary register §8), an authority-preserving interval and therefore trusted-time."
- Why wrong: R8 is gone: ADR-0026.md:13 "A1 (R8, break-glass grant TTL), drafted 2026.09.24, was **withdrawn 2026.10.04** by the custodian and never in force"; :291-293 "a break-glass grant has no timed expiry … a TTL needs trusted time, which the corpus refuses (ADR-0032 §2; ADR-0045 §6)". ADR-0045.md:203 "Trusted time for R8 (G10, item 8) | **refused**"; :437 "Trusted time: refused (§6)." Persona expiry was built on the other row: ADR-0031.md:68 "as a duration on the local monotonic clock; **at most `T_persona`**". So of §2's three examples one is withdrawn, one runs on the clock the row forbids (C-18), and one is said not to exist (ADR-0034.md:207); ADR-0026 cites this clause as *refusing* trusted time, where the clause *requires* it. ADR-0032 has no History entry after B5 except B36, and "Relates to" (:16) still reads "ADR-0026 (R8 candidate)".
- Fix belongs in: decisions/ADR-0032.md (§2, Open obligations, Relates to)
- Severity: Medium
- Confidence: high
- Already on the corpus's own lists: G10 item 8 records R8 "Closed by withdrawal" and G9 item 62 the `T_persona` clock; ADR-0032's own text is not listed
- **Verifier:** confirmed with correction
- **Verifier's correction:** One sub-claim does not hold: ADR-0026 does not cite ADR-0032 §2 as refusing trusted time. Its sentence 'a TTL needs trusted time, which the corpus refuses (ADR-0032 §2; ADR-0045 §6)' gives one citation for each half. The Persona-expiry limb is the same conflict as C-18, read from ADR-0032's side. The rest stands: R8 is withdrawn and ADR-0032 still carries it at :16, :63-65, :160; Persona expiry is still an open obligation at :161-162.
- **Verifier's evidence:** decisions/ADR-0032.md:16, :54, :63-65, :160-162, :175-177 (History has B5 and B36 only); decisions/ADR-0026.md:13, :291-293; decisions/ADR-0045.md:203, :437; decisions/ADR-0031.md:68; decisions/ADR-0034.md:207; checkpoints/topak-genesis-checkpoint-G10-2026.10.05.md:329 (item 8)

### C-26: ADR-0032's status note rests on ADR-0021 being Proposed; it is Accepted, and still carries the chain
- Against: decisions/ADR-0032.md:11-12 (and decisions/ADR-0021.md:11, :83)
- Basis: in force
- Claim: "The `W < L < D` demotion (§4) touches ADR-0021, which is Proposed, so it is an in-place revision there rather than a reversal."
- Why wrong: ADR-0021.md:11 "**Status:** Accepted (genesis) · 2026.09.30 · confirmation required (ADR-0029 C4) ⟨B18⟩". ADR-0021.md:83 still reads "Run's `W < L < D` chain is hard: the propagation window is ~1s", and `grep -n "ADR-0032\|W + L + D" decisions/ADR-0021.md` returns nothing, so the in-place revision the note relies on is not visible in the accepted text.
- Fix belongs in: decisions/ADR-0032.md Status note (and ADR-0021, if the chain there is meant as more than description)
- Severity: Low-Medium
- Confidence: medium
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0032.md:11-12, :90-92; decisions/ADR-0021.md:11, :83, :208-215 (no revision R1 to R5 touches the chain). `grep -n 'ADR-0032\|W + L + D' decisions/ADR-0021.md` returns nothing. The note was true when written (ADR-0021 was Proposed until Batch 18, 2026.09.30); the direction is as the finding has it.

### C-27: ADR-0031 and ADR-0032 each list the other under "Depends on", and ADR-0032 was accepted two days before ADR-0031
- Against: decisions/ADR-0032.md:14 and decisions/ADR-0031.md:15-16 (and decisions/ADR-0032.md:9; decisions/ADR-0031.md:393)
- Basis: in force
- Claim: ADR-0032: "**Depends on:** ADR-0007 (placement), ADR-0022 (epoch and lease on every action), ADR-0031 (lease schema)"; ADR-0031: "every action), ADR-0026 (rules floor), ADR-0032 (clock model)"
- Why wrong: The dependency is circular. ADR-0032.md:9 "Accepted (genesis) · 2026.09.23"; ADR-0031.md:393 "**Ratified 2026.09.25** … in Batch 5 … at revision R3", and R1 to R3 changed its schema (twelve fields, two revocation tools) after ADR-0032 was accepted. ADR-0032 was therefore ratified on a Proposed record it depends on and "Discharges" §7 of (:17), and neither its Status note nor its B5 row says so.
- Fix belongs in: decisions/ADR-0032.md header (and one of the two Depends-on lines)
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0032.md:9, :14, :17, :176; decisions/ADR-0031.md:15-16, :384 ('Revised in place 2026.09.25 (R1–R3), then ratified the same day'), :390-393

### C-28: ADR-0032's ratification is tagged B5 and dated 2026.09.23; Batch 5 is 2026.09.25 and does not contain it
- Against: decisions/ADR-0032.md:9 and :176 (and decisions/ADR-0031.md:393; decisions/ADR-0003.md:82)
- Basis: in force
- Claim: "**Status:** Accepted (genesis) · 2026.09.23 ⟨B5⟩ ⟨B36⟩" and "| B5 | Ratification | **Ratified 2026.09.23** by the genesis custodian (ADR-0029 §2), as authored."
- Why wrong: ADR-0031.md:393 "| B5 | Ratification | **Ratified 2026.09.25** by the genesis custodian (ADR-0029 §2), in Batch 5 with ADR-0003 A1 and A2"; ADR-0003.md:82 "**A1 and A2 ratified 2026.09.25** by the genesis custodian (ADR-0029 §2), in Batch 5 with ADR-0031". The same tag names two ratifications two days apart.
- Fix belongs in: decisions/ADR-0032.md
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: G3's batch table says so (checkpoints/topak-genesis-checkpoint-G3-2026.09.25.md:21 "0032 carries a `B5` tag but was not a batch"); not a G11 open-list item
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0032.md:9, :176; decisions/ADR-0031.md:393; decisions/ADR-0003.md:82; checkpoints/topak-genesis-checkpoint-G3-2026.09.25.md:21-22 (the corpus's own note that the tag was not a batch)

### C-29: §4 calls the budget a form with one unknown; the ratification row calls it a form with two
- Against: decisions/ADR-0032.md:100-101 (and decisions/ADR-0032.md:176)
- Basis: in force
- Claim: "Until `L` is measured, the budget is a form with one unknown in it."
- Why wrong: B5 row, :176: "`L` remains unmeasured and no effect class has a declared `T_irrev`, so §4's budget is ratified as a form with two unknowns". Consequences (:149-150) agrees with the row: "**`T_irrev` must be declared per effect class**, and nothing in the corpus enumerates effect classes that way yet."
- Fix belongs in: decisions/ADR-0032.md §4
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0032.md:100-101 ('one unknown'), :176 ('two unknowns'), :149-150 ('`T_irrev` must be declared per effect class')

### C-30: "`W` is proven" has no artifact
- Against: decisions/ADR-0032.md:87 (and decisions/ADR-0032.md:82-83)
- Basis: in force
- Claim: "`W` is proven, `L` is measured, `D` is promised."
- Why wrong: The table (:82) says "Effect propagation window, about a second at the archetype | **Guaranteed by the mechanism**"; no module, proof or results file is cited for it, and `grep -rn -i "propagation window" spec/*.tla` returns nothing. The only other statements of the figure are prose (decisions/ADR-0021.md:83 "~1s"; floor/genesis-values.json:8 "~1 s at the archetype"). In the same sentence "`L` is measured" stands beside the table's "**unmeasured**" (:83). The corpus reserves *proved* for TLAPS.
- Fix belongs in: decisions/ADR-0032.md §4
- Severity: Low-Medium
- Confidence: medium
- Already on the corpus's own lists: no
- **Verifier:** confirmed with correction
- **Verifier's correction:** Drop the '`L` is measured' limb. The sentence names the kind of each term, not its state: it follows 'The three terms are of three different kinds', and the Options row says the chain 'mixes a proof, a measurement, and a promise'; the ToO uses the same form ('`L` is measured, not proven', theory-of-operation.md:1997-1998). On that reading it does not contradict 'unmeasured'. What stands: W is called proven and, in the table, 'Guaranteed by the mechanism', and no module, proof or results file is cited or exists for a propagation window.
- **Verifier's evidence:** decisions/ADR-0032.md:82-83, :86-88, :127 (Options row). `grep -rn -i 'propagation window' spec/*.tla` returns nothing; elsewhere only prose (ADR-0021.md:83, ADR-0039.md:126, narrative/glossary.md:1001-1002). decisions/ADR-0046.md:90 for the reservation of 'proved'.

### C-31: ADR-0034's Depends-on line, and the two modules it and ADR-0031 cite, still call ADR-0031 A1 pending
- Against: decisions/ADR-0034.md:18-19 (and decisions/ADR-0034.md:12; spec/Lease_A1.tla:2; spec/Confinement.tla:11)
- Basis: in force
- Claim: "A1, pending, for renewal ⟨R1⟩),"
- Why wrong: Six lines above, :12: "Ratified at R2, with ADR-0031 A1 (Batch 10)." decisions/ADR-0031.md:397 "**A1 ratified 2026.09.28**". Lease_A1.tla:2 "as amended by A1 (pending)" and Confinement.tla:11 "keeps the rung (ADR-0031 A1, pending)" say the same; both are cited by digest, so they cannot be corrected without a successor.
- Fix belongs in: decisions/ADR-0034.md header (the modules only at their next successor)
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0034.md:12, :18-19; decisions/ADR-0031.md:397; spec/Lease_A1.tla:2; spec/Confinement.tla:11

### C-32: In-force text of ADR-0034 says ADR-0025 has no item for the verifier key and that the TCB declaration record does not exist
- Against: decisions/ADR-0034.md:162 and :281-282 (and decisions/ADR-0034.md:27-28, :214, :469-471; decisions/ADR-0025.md:67)
- Basis: in force
- Claim: §2: "ADR-0025 §1 lists what rules contain and has no item for it. This record asks for one and carries the debt."; §6: "must be recorded in the TCB declaration record, which does not exist yet (G3 item 16). That is carried as a debt."
- Why wrong: ADR-0025.md:67 "- **(f)** The keys the mechanism accepts a signature from in place of its own check: the verifier's"; the record's own §3.7, :214, cites "(ADR-0025 §1 (f))". Open obligations strike both: :469-470 "~~**ADR-0025 §1 gains the verifier key.** …~~ **ADR-0025 A1**, ratified 2026.09.30 (Batch 17): item (f)."; :471 "~~**The TCB declaration record** must enter §6's rows.~~ **ADR-0045 T-0045-16 to T-0045-22**, ratified 2026.10.01 (Batch 22)". The face (:27-28) still lists "the TCB declaration record (§6) · ADR-0025 §1 (the verifier key, §2)" as debts with no annotation, where the Run-alphabet debt beside them is annotated as paid.
- Fix belongs in: decisions/ADR-0034.md header, §2, §6
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0034.md:27-28, :162, :214, :281-282, :469-471 (line numbers and quotes exact); decisions/ADR-0025.md:67-70

### C-33: §1's Run-profile block says the reference reads a tool's target from node configuration; ADR-0033 A9 ended that the next day, and the block still calls ADR-0049 Proposed
- Against: decisions/ADR-0034.md:100 and :139-140 (and decisions/ADR-0033.md:578; mechanism/GAPS-AND-ASSUMPTIONS.md:44; decisions/ADR-0049.md:15)
- Basis: in force
- Claim: "(the custodian's decision of 2026.10.03; ADR-0049 §5, Proposed, gives the entry's form)"; "that is the reference today (`mechanism/` I44; G19)"; "Its target is read from node configuration and not from the allowlist entry, with nothing comparing the"
- Why wrong: ADR-0033.md:578 "### Addendum : the tool host reads a Run tool's target from its allowlist entry, 2026.10.05 ⟨A9⟩" (ratified in Batch 32, :580). GAPS:44 "the Wasm tool host's target read from the entry of the lease's revision (I33, I44)"; GAPS:103 (I44) "`connect`/`send`/`recv` on the target its entry declares". ADR-0049.md:15 "**Status:** Accepted (genesis) · 2026.10.05". The block is headed "**What the reference does not do, of what this block says** ⟨B30⟩" (:138) and has no later mark, so one of its three "not discharged" items is no longer true, and the History's B30 and B31 rows (:512-513) repeat it.
- Fix belongs in: decisions/ADR-0034.md §1 (a dependent entry for ADR-0033 A9 and for ADR-0049's ratification)
- Severity: Medium
- Confidence: high
- Already on the corpus's own lists: G10 item 84 ("Closed (A9)") and item 89 record the change for ADR-0045 Annex B; ADR-0034's text is not listed
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0034.md:100, :138-141, :512-513; decisions/ADR-0033.md:578-582; mechanism/GAPS-AND-ASSUMPTIONS.md:44, :103 ('Until 2026.10.05 the target was read from node configuration ... that is closed'); decisions/ADR-0049.md:15; checkpoints/topak-genesis-checkpoint-G10-2026.10.05.md:356, :366. `grep -n 'A9\|B32' decisions/ADR-0034.md` returns nothing: no dependent entry. The stale statement understates the reference.

### C-34: §3.7 lets only a verifier-signed verdict order a Contested revocation, "at rung ≥ 2"; at rung 2 the record has no verifier
- Against: decisions/ADR-0034.md:213-215 (and decisions/ADR-0034.md:155-156; decisions/ADR-0045.md:394; spec/Confinement.tla:121)
- Basis: in force
- Claim: "whose key the issued rules carry (ADR-0025 §1 (f)), and only at rung ≥ 2, where an appraisal is a measurement."
- Why wrong: §2's table, :156, gives rung 2 as appraised by "The mechanism, against the profile's reference values", and the independent verifier only at rung 3 (:155). ADR-0045.md:394 "**T-0045-17** | The independent verifier (ADR-0034 §2) | substrate | Decides what counts as Attested at rung 3"; decisions/ADR-0025.md:230 calls (f) "the rung-3 verifier's appraisal key"; Confinement.tla:121 "The independent verifier exists only at rung 3, and may be unreachable." Yet §2 says rung 2 detects a rogue launch as "*Contested*" and §7's row "A rogue launch is detected | 2, 3" (:309) checks it. Read literally, A3 leaves a rung-2 Contested verdict with no signer and so no revocation; the reference cannot say which reading holds, since rung 2 is one "`apply_grant` refuses as a seam" (mechanism/GAPS-AND-ASSUMPTIONS.md:101).
- Fix belongs in: decisions/ADR-0034.md §3.7 (or §2's rung-2 row)
- Severity: Medium
- Confidence: medium
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0034.md:155-156, :213-215, :309, :507; decisions/ADR-0025.md:67-68, :230; decisions/ADR-0045.md:394; spec/Confinement.tla:121-123, :134-137; mechanism/GAPS-AND-ASSUMPTIONS.md:101. Further: spec/Mechanism.tla:652-657 (`ApplyContested`: 'a signed rung-3 Contested revokes the principal', and `a.rung <= 2` is rejected) and :277 ('the rung-2 seam'), so the operational model takes the rung-3 reading against the record's 'rung ≥ 2'.

### C-35: ADR-0034 and its modules have one declared rung per deployment; ADR-0023 §6c, in force, makes it per seat and "not per deployment"
- Against: decisions/ADR-0034.md:189, :228, :295 (and decisions/ADR-0023.md:51; spec/Confinement.tla:21, :273; spec/Confinement_A1.tla)
- Basis: in force
- Claim: "Grant at the deployment's declared rung"; "granted on an **Attested** verdict at the deployment's declared rung"; §7 "the declared rung is a constant"
- Why wrong: ADR-0023.md:51 "***6c. The declared rung, per seat.** … The rung is per seat and not per deployment: a deployment runs rung-0 principals beside higher ones". ADR-0034 A3 was ratified in the same batch (B29) and left the phrase. The modules check and prove the per-deployment reading only: Confinement.tla:21 "The deployment declares one confinement rung, `Declared` (ADR-0031 §3)", :273 "NoSilentDowngrade == \A p \in Principals : lease[p].live => lease[p].rung = Declared"; `diff spec/Confinement.tla spec/Confinement_A1.tla` shows the successor differs only in its header and in `Evidence`. A mixed-rung deployment, the one §6c says is normal and ADR-0036 §7 asks for, is outside what `Safe` was checked over, and §7 (:339-340) describes the property as "it declared rung 3 and is running principals below it". Neither §7 nor the B25 and B29 rows acknowledge the abstraction.
- Fix belongs in: decisions/ADR-0034.md §3, §4, §7 (and a successor module if `NoSilentDowngrade` is to cover per-seat rungs)
- Severity: Medium-High
- Confidence: medium
- Already on the corpus's own lists: no (G9 items 64 and 85 tracked moving the reference's per-seat choice into a record; mechanism/GAPS-AND-ASSUMPTIONS.md:96 I37 records it as written down; neither names ADR-0034's wording or the modules)
- **Verifier:** confirmed with correction; severity Medium (reader: Medium-High)
- **Verifier's correction:** Two statements need narrowing. (1) 'The modules check and prove the per-deployment reading only' is true of Confinement.tla, Confinement_A1.tla and Confinement_proof.tla (one constant `Declared`; the proof's one assumption is `Declared \in 0..3`), not of the spec layer: spec/ConfinementRefinement.tla:12, :17-18, :27-30 says '`Declared` is per seat in the reference ... so NoSilentDowngrade is read per seat' and checks `RNoSilentDowngrade` against each seat's rung on the reference's recorded traces, and Mechanism.tla:347 refuses a grant whose rung is not its seat's. So the per-seat reading is trace-checked, and neither model-checked nor proved over all behaviours. (2) ADR-0023 §6c does not leave the two readings side by side: it says its per-seat rung 'is ADR-0034 §3.4's "declared rung"', and A1's source column (ADR-0023.md:149) quotes ADR-0034's phrase as having 'no record saying where it is declared'. What stands: ADR-0034 still says 'the deployment's declared rung' (:189, :228; also :415 'A deployment's rung is in every lease' and :339-340) after A3 was ratified in the same batch, and §7, B25 and B29 say nothing of a mixed-rung deployment being outside the abstract module. Medium: the layers disagree, the invariants are per principal, and the reference enforces the per-seat rule.
- **Verifier's evidence:** decisions/ADR-0034.md:189, :193-196, :228, :295-296, :339-340, :415, :505, :509; decisions/ADR-0023.md:51, :149, :165; spec/Confinement.tla:6, :21, :50, :186, :273; spec/Confinement_proof.tla:15-17, :36; `diff spec/Confinement.tla spec/Confinement_A1.tla` (header and `Evidence` only, as the finding says); spec/ConfinementRefinement.tla:12, :17-18, :27-30; spec/Mechanism.tla:293, :347; decisions/ADR-0036.md:249-250; mechanism/GAPS-AND-ASSUMPTIONS.md:96. `grep -n -i 'per seat\|per-seat\|ConfinementRefinement' decisions/ADR-0034.md` returns nothing.

### C-36: §4 defines the criterion "in force" twice, and the two can differ
- Against: decisions/ADR-0034.md:233-234 (and decisions/ADR-0034.md:236-240, :14)
- Basis: in force
- Claim: "**ADR-0017's lineage-independence criterion is in force** ⟨R2⟩: ADR-0035 is ratified and its θ values are set as floor values."
- Why wrong: A3, :238-240: ""In force" is that field being set, a check of the issued rules and nothing semantic: the mechanism does not evaluate the criterion, it reads that an issuance put one in force." Under the first sentence `Contained` waits on ADR-0035's ratification and on floor values (all `null`, floor/genesis-values.json:20-24); under the second an anchor issuance that sets `Rules.criterion` suffices, whatever ADR-0035's status and whatever the θ values. A3 is headed "what "in force" means" but does not strike or restate the first definition, and the Status note (:14) keeps the first: "`Contained` has no members until ADR-0035 is in force (§4)."
- Fix belongs in: decisions/ADR-0034.md §4
- Severity: Low-Medium
- Confidence: medium
- Already on the corpus's own lists: no (G9 item 20 notes "The reference reads it as `Rules.criterion` set (I39)")
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0034.md:14, :233-234, :236-241; floor/genesis-values.json:20-24; mechanism/GAPS-AND-ASSUMPTIONS.md:122 ('an issuance that sets the field is the whole change'). The two can differ in fact: the reference's tests set the field while ADR-0035 is Proposed and every θ is null (ADR-0034.md:509, B29: 13 passing, 'among them the criterion'; :141-142: 'the one run that reaches it is the SIMULATED rung 3').

### C-37: §4 cites a constant the reference no longer has
- Against: decisions/ADR-0034.md:245-246 (and mechanism/GAPS-AND-ASSUMPTIONS.md:122)
- Basis: in force
- Claim: "This record takes both, and the reference already does (`PROVENANCE_CRITERION_DEFINED`)."
- Why wrong: GAPS:122 "`Rules.criterion`, unset in every shipped rules file (I39); the constant is gone". `grep -rn PROVENANCE_CRITERION_DEFINED mechanism/crates --include=*.rs` returns nothing; across `decisions/*.md` and `mechanism/*.md` the name occurs only on this line. The same clause's A3 paragraph names the replacement (`Rules.criterion`, :238).
- Fix belongs in: decisions/ADR-0034.md §4
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0034.md:245-246, :238; mechanism/GAPS-AND-ASSUMPTIONS.md:122. `grep -rn PROVENANCE_CRITERION_DEFINED mechanism/crates --include=*.rs` returns nothing; `grep -rln PROVENANCE_CRITERION_DEFINED .` returns only decisions/ADR-0034.md.

### C-38: Consequences still says "Run is not discharged"
- Against: decisions/ADR-0034.md:431 (and decisions/ADR-0034.md:16, :27, :512)
- Basis: in force
- Claim: "- **Run is not discharged.**"
- Why wrong: :16 "A2 ratified 2026.10.04 (Batch 30), with ADR-0042 §6, and applied inline"; :27 "Run's alphabet (the Run profile, §1; *paid by A2, ratified 2026.10.04 (Batch 30)*"; B30 row, :512, lists the dependent entry "ADR-0022 (§6's obligation, for Run)". The Status note (:12) and Closes (:25) also still read "for Build" only.
- Fix belongs in: decisions/ADR-0034.md Consequences and header
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0034.md:12, :16, :25, :27, :431, :512; decisions/ADR-0022.md:307 (B30: '§6's obligation is discharged for Run')

### C-39: The reference-launcher obligation and finding 6 are discharged in History and stand open in the text
- Against: decisions/ADR-0034.md:482-485 and :460-462 (and decisions/ADR-0034.md:510)
- Basis: in force
- Claim: "- **The reference.** A rung-1 launcher in `topak-node` is the smallest step toward `is_contained()`."; finding 6: "so it belongs in a successor module, as `Lease_A1.tla` was to `Lease.tla`, when the rung-2 record next touches this module."
- Why wrong: B29 dependent entry, :510: "this record's open obligation for a reference launcher is discharged at rung 1 on a host process and in a container … `spec/Confinement_A1.tla` is finding 6's successor module." The bullet is neither struck nor annotated, unlike its siblings; its last sentence, "then its constant becomes a check of the issued rules", describes something already done (mechanism/GAPS-AND-ASSUMPTIONS.md:98, I39). The successor exists (spec/Confinement_A1.tla, results `spec/Confinement_A1-results-2026.10.02.txt`) without a rung-2 record, and §7 cites neither the module nor its run.
- Fix belongs in: decisions/ADR-0034.md Open obligations, Findings, §7
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0034.md:457-462, :482-485, :510; mechanism/GAPS-AND-ASSUMPTIONS.md:98; spec/Confinement_A1.tla and spec/Confinement_A1-results-2026.10.02.txt exist. `grep -n 'Confinement_A1' decisions/ADR-0034.md` returns only the two B29 rows (:509, :510), so §7 cites neither.

### C-40: "the proof is certified" for RunConfinement omits the three uncertified obligations, and the record never says that `Confinement_proof` does not certify
- Against: decisions/ADR-0034.md:131-133 and :505 (and spec/RunConfinement-proof-cert-results-2026.10.04.txt:12, :14; spec/Confinement-proof-cert-results-2026.10.04.txt:15; spec/proof-certification.md:577)
- Basis: evidence
- Claim: "(`spec/RunConfinement_proof.tla`, `e8612bf4111c7599`) and the proof is certified, its results file regenerated"; B25: "**§7's ratification condition, `Safe` at every rung, is proved.**"
- Why wrong: RunConfinement cert results, :12 "LS4, temporal step, NOT certified                   3", :14 "113 of them rest on tlapm's own normalization or on a checked proof; 3 rest on LS4, whose answer no checker confirms." (`sha256sum` of that file begins `823ae3479ef38845`, so the digest the record gives for "its results file regenerated byte for byte" is the certified run's own file; `spec/RunConfinement-proof-results-2026.10.02.txt` is `f454ba1badf1cd34`.) For the module §7 rests on, Confinement cert results :15 "NOT CERTIFIED: 3 obligation(s) failed (last backend tried: isabelle)." and proof-certification.md:577 "`Confinement_proof` | Three obligations, large type-invariant steps, are proved by Z3 and by nothing else". ADR-0034 mentions non-certification only of `Confinement_A1_proof` (:509); a reader of B25 is not told the cited proof is one of the three that do not certify.
- Fix belongs in: decisions/ADR-0034.md §1 "Met at ratification" and History B25
- Severity: Low-Medium
- Confidence: medium
- Already on the corpus's own lists: G10 item 74 (as at G11: three modules do not certify) covers the fact; the record's wording is not listed
- **Verifier:** confirmed with correction; severity Low (reader: Low-Medium)
- **Verifier's correction:** The first limb does not stand. 'Certified' is a defined term that admits LS4 steps: 'A module is certified when every obligation is closed by the prover's own normalization, or has a proof a checker accepted, or is a temporal step discharged by LS4' (ADR-0046.md:144-145; spec/proof-certification.md:60-63: LS4 counts toward certification 'and reported separately as not certified'). RunConfinement's run reports 'All 116 obligations proved' with 3 on LS4, so 'the proof is certified' at ADR-0034.md:132, which cites ADR-0046 A1, is right by the corpus's definition. What stands is the second limb, an absence: B25 (:505) cites `Confinement_proof.tla` for §7's ratification condition and the record nowhere says that module does not certify, though it says so of `Confinement_A1_proof` (:509). B25's word is 'proved', which remains true of the uncertified run.
- **Verifier's evidence:** decisions/ADR-0034.md:131-133, :505, :509; spec/RunConfinement-proof-cert-results-2026.10.04.txt:12, :14; spec/Confinement-proof-cert-results-2026.10.04.txt:13, :15; spec/proof-certification.md:60-63, :577, :580-581; decisions/ADR-0046.md:144-145, :506. `sha256sum` reproduces: cert results 823ae3479ef38845, 10.02 results f454ba1badf1cd34, proof module e8612bf4111c7599, module d0c4aa37934b78b5.

### C-41: Two in-force passages of ADR-0034 lean on ADR-0036 without saying it is Proposed
- Against: decisions/ADR-0034.md:98 and :215 (and decisions/ADR-0036.md:11)
- Basis: in force
- Claim: "an admitted `Consult` delivers its object over the channel, node-side, as ADR-0036 §3 does `Read` (drafter's choice)"; "rung 1 nothing measures, so no appraisal is Contested (§7's `NeverContested` at rung 1; ADR-0036)."
- Why wrong: ADR-0036.md:11 "**Status:** Proposed · 2026.09.28". Elsewhere the record marks such dependencies (:21-22 "ADR-0035 (the independence criterion, §4; Proposed)"); here it does not, and ADR-0036 is in neither the Depends-on nor the Relates-to line (:18-24).
- Fix belongs in: decisions/ADR-0034.md §1, §3.7 and header
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no (G10 items 81 and 85 note that ADR-0036 is Proposed while A7 is ratified)
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0034.md:18-24 (ADR-0036 in neither line), :21-22, :98, :215; decisions/ADR-0036.md:11

### C-42: ADR-0035 calls three accepted records Proposed and carries a debt against a record it says is accepted
- Against: decisions/ADR-0035.md:26, :92, :109, :120 and :29 (and decisions/ADR-0047.md:19; decisions/ADR-0048.md:15; decisions/ADR-0050.md:20; decisions/ADR-0035.md:23)
- Basis: Proposed
- Claim: "ADR-0047 (Proposed: an item delivered as a handle, §1 ⟨R5⟩), ADR-0048 (Proposed: the tool list, §1 ⟨R6⟩), ADR-0050 (Proposed: an operator's lineage, §1 ⟨R7⟩)"; "**Carries a debt against:** ADR-0034, which must be in force before any lineage is better than declared"
- Why wrong: ADR-0047.md:19 and ADR-0048.md:15 "Accepted (genesis) · 2026.10.05"; ADR-0050.md:20 "Accepted (genesis) · provisional · 2026.10.05". §1 repeats the word at :92, :109 and :120. For the debt: :23 "ADR-0034 (confinement; Accepted 2026.09.28)". (ADR-0054 is correctly Proposed.)
- Fix belongs in: decisions/ADR-0035.md header and §1
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0035.md:11, :23, :26, :29, :92, :109, :120, and History :425-427 ('dependent on ADR-0047, Proposed' and so on); decisions/ADR-0047.md:19; decisions/ADR-0048.md:15; decisions/ADR-0050.md:20. Also stale in the same sense, not cited: :354 'Every lineage is declared until ADR-0034 is in force.'

### C-43: ADR-0035 says its tally rule is a debt "carried" for an ADR-0024 amendment still to come; ADR-0024 A2.2 ratified it on 2026.09.29, so a Proposed record's rule is in force and the record does not say so
- Against: decisions/ADR-0035.md:218-220, :29-30, :392 (and decisions/ADR-0024.md:240, :254-258, :70-74)
- Basis: Proposed
- Claim: "**The text belongs in ADR-0024** as an amendment. This record states the rule and carries the debt. Whether the rule lives as a mechanism constant or a floor entry is settled there."; Open obligations: "- **ADR-0024 amendment** carrying §5's tally condition, and the bootstrap `Promotion` module modeling it."
- Why wrong: ADR-0024.md:240 "## Amendment A2 (drafted 2026.09.29; ratified 2026.09.29, Batch 15) ⟨A2⟩"; :254-258 "**A2.2 : §2, an independent veto seat must be seated** (ADR-0035 §5). … **This is a mechanism constant in the tally**, as recusal is (§6) … ADR-0035 §5 left the placement to this record; this settles it." It is applied inline in ADR-0024 §2 (:70-74). So the placement is settled, the amendment exists, and an accepted bootstrap record enforces a condition "according to the promoted independence table (ADR-0035 §4)" (:255-256) while ADR-0035 is Proposed and "the independence table is not computed while any is null" (floor/genesis-values.json:19). ADR-0035 §5, changed since G9 for R8, says of R8 only that it is "declared and not enforced" until ratification, and says nothing of the Build tally's force.
- Fix belongs in: decisions/ADR-0035.md §5, header, Open obligations (and ADR-0024 §2, on what the condition means before the table exists)
- Severity: Medium
- Confidence: medium
- Already on the corpus's own lists: G9 item 31 "The ADR-0024 amendment | Discharged (G5)"; the open bullet in ADR-0035 and the force of the rule are not listed
- **Verifier:** confirmed with correction; severity Low-Medium (reader: Medium)
- **Verifier's correction:** A line number, and the force of the rule. The A2 heading is ADR-0024.md:241, not :240. ADR-0024 already says on its own face what the finding says is unsaid: the A2 History row (:290) records that 'A2.1 and A2.3 are in force ... A2.2 is not, since no independence table exists (`mechanism/` G18)', and A2's preamble (:246) says 'the ADR-0035 condition may be ratified with ADR-0035 alone'. So the open point about the condition before the table exists is recorded in ADR-0024; nothing more is owed there. What stands is ADR-0035's side: §5 (:218-220) and the header debt (:29-30) still say the amendment is to come and the placement unsettled, the first half of the open bullet (:392) is unstruck, and the record does not say its tally rule is ratified text in ADR-0024 §2. The second half of that bullet (the bootstrap `Promotion` module modelling it) may still be owed.
- **Verifier's evidence:** decisions/ADR-0035.md:29-30, :215-220, :392; decisions/ADR-0024.md:71-73, :241, :243-247, :254-258, :266-269, :290; floor/genesis-values.json:19

### C-44: R7 says E2 to E5 pass vacuously for an operator; E4 is a positive requirement and cannot
- Against: decisions/ADR-0035.md:127 (and decisions/ADR-0035.md:176, :122-123)
- Basis: Proposed
- Claim: "- **E2 to E5 and the distillation rule have nothing to measure** and pass vacuously for an operator."
- Why wrong: :176 "| **E4** Architecture | Different `family` tags and different tokenizer digests | The same design trained twice |". E2, E3 and E5 forbid something shared and are satisfied by empty sets; E4 demands two differences. An operator record "has no `ingress`, `consumed`, `tokenizer` or `trainer`" (:122-123), and `family` comes from "The trainer configuration" (:88), so two operators have no tokenizer digests and no family tags to differ. As written E4 fails, or is undefined, for every pair of operators, and A and B are independent "only if every clause holds" (:169).
- Fix belongs in: decisions/ADR-0035.md §1 (R7) or §3 (E4)
- Severity: Low-Medium
- Confidence: medium
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0035.md:87-89 (`tokenizer`, `family` from the trainer configuration, `trainer`), :120-123, :127, :169, :176; decisions/ADR-0050.md:119-122 (ADR-0050 itself says only that the corpus rules have nothing to measure and the root rule applies, and does not place E4)

### C-45: R7 gives the independence table rows for operators; the values file says no table is computed while any θ is null
- Against: decisions/ADR-0035.md:128 (and floor/genesis-values.json:19-24)
- Basis: Proposed
- Claim: "- **The independence table has rows for operators**, read where ADR-0050 §6 asks that a peer be independent."
- Why wrong: genesis-values.json:19 "null means not set, and the independence table is not computed while any is null." and :20-24 set `theta_exact`, `theta_near`, `theta_gen`, `beta`, `near_tool` to `null`; floor/genesis-gates-results-2026.10.01.txt:8 "lineage: 5 of 5 values unset". R7 itself says only E1 measures anything for an operator, yet the operator rows wait on corpus thresholds that do not concern them, and ADR-0050 (in force, provisional) is pointed at a table that does not exist.
- Fix belongs in: decisions/ADR-0035.md §1/§4 or the values file's note
- Severity: Low-Medium
- Confidence: medium
- Already on the corpus's own lists: no (G9 item 30 "θ values | Open")
- **Verifier:** confirmed with correction; severity Low (reader: Low-Medium)
- **Verifier's correction:** ADR-0050 does not itself point at the table: `grep -n -i table decisions/ADR-0050.md` returns nothing. It defines the archetype peer's independence directly as 'a different identity provider' (:201) and cites ADR-0035's rule, not its table (:119-122, :340). The pointer is ADR-0035 R7's alone, in a Proposed record, and the other side is a note in a DRAFT placeholder file. The tension the finding infers is real: operator rows, for which only E1 measures anything, wait on corpus thresholds under the values file's blanket rule.
- **Verifier's evidence:** decisions/ADR-0035.md:125-128, :193-198 (the gate emits the table at Persona promotion); floor/genesis-values.json:3, :19-24; floor/genesis-gates-results-2026.10.01.txt:8; decisions/ADR-0050.md:119-122, :201, :340

### C-46: §8's five-part ratification condition carries no state
- Against: decisions/ADR-0035.md:303-310
- Basis: Proposed
- Claim: "**Ratification condition:**" followed by five bullets (gate-suite cases; the monotonicity check; the E3 overlap measurements "reported with the θ values proposed from them"; one projected lineage; a review "recorded in this record")
- Why wrong: No bullet is marked met or unmet, and no History row records it, although evidence for some exists: slm/gate-suite-results-2026.09.28.txt:31 "monotonicity in ingress (mode bounded, 2000 random trials, seed 35)", and `slm/e3-overlap-results-2026.09.25.txt` is in the tree. Finding 5 (:382) mentions the rerun in passing; the fourth bullet is blocked by an open obligation (:409-410); the fifth is owed (:399-404). Compare ADR-0036's R5 (decisions/ADR-0036.md:352 "§7's condition is not met: …") and ADR-0034's "**Met at ratification**" (decisions/ADR-0034.md:128).
- Fix belongs in: decisions/ADR-0035.md §8 or History
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: G9 items 30 and 33 list two of the five (θ values; the best-practice review) as open; the condition's state as a whole is not recorded
- **Verifier:** confirmed with correction; severity Low (reader: Low-Medium)
- **Verifier's correction:** 'Carries no state' overstates. The list itself is unannotated and no History row tallies it, but the record gives the state of four of the five items in prose: the second in finding 5 (:378-382, the 2026.09.28 rerun holds) and :265; the θ half of the third in Open obligations (:390, unset); the fourth in §8 (:297-300) and :409-410 (needs an in-guest trainer image); the fifth in :399-404 (owed). Only the first has no statement. The record is Proposed, so no 'Met at ratification' is yet due; the comparison with ADR-0036 R5 is fair.
- **Verifier's evidence:** decisions/ADR-0035.md:265, :297-300, :303-310, :378-382, :390, :399-404, :409-410, :420-428; slm/gate-suite-results-2026.09.28.txt:29-35; slm/e3-overlap-results-2026.09.25.txt exists; decisions/ADR-0036.md:352; decisions/ADR-0034.md:128

### C-47: §3 puts a from-scratch distillation at ADR-0017's rung 1 under a quoted description that is not ADR-0017's
- Against: decisions/ADR-0035.md:180-181 (and decisions/ADR-0017.md:45)
- Basis: Proposed
- Claim: "On ADR-0017's axis it sits at rung 1, "in-house weights, external content", and carries a content-lineage debt alongside rung 1's weight-lineage debt."
- Why wrong: ADR-0017.md:45 "| 1 | In-house fine-tune on external base | `Contained`, with a lineage debt stated |". `grep -n -i "in-house weights\|external content" decisions/ADR-0017.md` returns nothing. ADR-0017's rung 1 has external weights; the case placed there has in-house weights. Finding 2 (:368-370) concedes the mismatch ("ADR-0017 may want to split them"), but §3 states the placement as if the accepted table already held it, and decisions/ADR-0034.md:249 says "ADR-0017's table is unchanged".
- Fix belongs in: decisions/ADR-0035.md §3 (or an amendment to ADR-0017)
- Severity: Low
- Confidence: medium
- Already on the corpus's own lists: no (G9 item 6, "The ADR-0017 supersession | Unwritten", is adjacent)
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0035.md:180-182, :368-370 (finding 2 concedes the second way into rung 1); decisions/ADR-0017.md:45; decisions/ADR-0034.md:249. `grep -n -i 'in-house weights\|external content' decisions/ADR-0017.md` returns nothing; the phrase occurs only at ADR-0035.md:180.

### C-48: §5 says "Run has no tally" and, one paragraph on, names one
- Against: decisions/ADR-0035.md:226-227 (and decisions/ADR-0035.md:229-230, :358)
- Basis: Proposed
- Claim: "**Run has no tally.** Observer independence in Run is enforced only through the declaration until something in Run can stall on it. That is stated as a limit, not deferred."
- Why wrong: R8, :229-230: "**A workflow's promotion is such a place** ⟨R8⟩. ADR-0054 (Proposed) seats every cell of a workflow by one promotion, so its tally is where a refusal of a Run seating stalls." R8's rule also covers "within every cell the Thinker and the Observer" (:231-232). The earlier paragraph was not qualified, and Consequences (:358) still reads "**Run is enforced only by declaration** (§5)."
- Fix belongs in: decisions/ADR-0035.md §5 and Consequences
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** not confirmed
- **Verifier's correction:** The texts do not conflict. 'The earlier paragraph was not qualified' is not so: it reads 'enforced only through the declaration until something in Run can stall on it', and R8 opens 'A workflow's promotion is such a place', taking up that qualifier. R8's rule rests on ADR-0054, which is Proposed, and says of itself 'Until this record is ratified the rule is declared and not enforced', so Consequences' 'Run is enforced only by declaration' is still accurate.
- **Verifier's evidence:** decisions/ADR-0035.md:226-235, :358, :428

### C-49: ADR-0036's face still carries three debts its own rows discharge, and a "Closes" that another record has already closed
- Against: decisions/ADR-0036.md:24-27 and :216 (and decisions/ADR-0036.md:326, :330, :352; decisions/ADR-0034.md:510)
- Basis: Proposed
- Claim: "**Closes:** nothing yet. On ratification, the first half of ADR-0034's reference obligation: a launcher, a profile,"; "and needs an addendum) · ADR-0035 (finding 1) · the TCB declaration record (§5's rows)"; §5 "These are D-0034-2's type changes made concrete, and they are owed to the TCB declaration record (G3 item 16)."
- Why wrong: :326 "~~**The TCB declaration record** takes §5's rows.~~ ADR-0045 Annex B instantiates them"; :330 "~~**ADR-0035 finding 1's disposition**, in that record.~~ **Disposed by ADR-0035 R4**"; R5, :352, "ADR-0033 A7, ratified 2026.10.04 in Batch 29, records the launcher in the node". And decisions/ADR-0034.md:510 "this record's open obligation for a reference launcher is discharged at rung 1" by ADR-0033 A7, so nothing remains for ADR-0036's ratification to close under that heading.
- Fix belongs in: decisions/ADR-0036.md header and §5
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: G10 items 35 and 81 (as at G11) record that A7 was ratified ahead of ADR-0036; the header is not listed
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0036.md:13-14 (its C4 ground is the same obligation), :24-27, :216, :326, :330, :352; decisions/ADR-0034.md:510

### C-50: §6 describes a launcher script beside the rehearsal and a move into the node still to come; R5 says the move is done, R6 says §6 "describes the launcher as it is", and no such script is in `slm/`
- Against: decisions/ADR-0036.md:220-221, :324, :353 (and decisions/ADR-0036.md:352)
- Basis: Proposed
- Claim: §6: "This record's launcher is a script beside the rehearsal, holding the operator socket. That is the honest place for"; Open obligations: "- **§6: the launcher in `topak-node`**, with ADR-0033's addendum and a promoted profile."; R6: "§6 here describes the launcher as it is; nothing in it changes until ADR-0050 is in force and the reference follows."
- Why wrong: R5, :352: "**§6's step is carried out, and this record is still Proposed.** ADR-0033 A7, ratified 2026.10.04 in Batch 29, records the launcher in the node". The two pointer rows, written the same day, disagree on whether §6 is current. `grep -rln -i -E "AgentOp|bridge|operator socket|launcher" slm/` returns only `slm/serve/README.md` and `slm/serve/profile-host-rung0.json`; `slm/serve/run.sh` (line 2) is "# Run a trained checkpoint in the sandbox. stdio is the only channel." and makes no grant. R6's condition has also passed: decisions/ADR-0050.md:20 is "Accepted (genesis) · provisional · 2026.10.05", not "(Proposed)" as R6 calls it. The open obligation (:324) is not struck, though §7's first and last bullets (the profile file, the `slm/` results file) remain unmet per R5.
- Fix belongs in: decisions/ADR-0036.md §6, Open obligations, R6
- Severity: Medium
- Confidence: medium
- Already on the corpus's own lists: G10 items 34, 35 and 81 (as at G11) list the ratification run as open and the launcher as built; the conflict between §6, R5 and R6 is not listed
- **Verifier:** confirmed with correction; severity Low-Medium (reader: Medium)
- **Verifier's correction:** Two sub-claims need changing. (1) R5 and R6 need not disagree. R6 is about `Launch` as an operator's request, which is §6's second step, the launcher in the node; read so, '§6 here describes the launcher as it is' agrees with R5's '§6's step is carried out'. (2) R6's condition has passed by half only: ADR-0050 is in force, so R6's '(Proposed)' is stale, but the reference has not followed for `Launch` (mechanism/GAPS-AND-ASSUMPTIONS.md:106: '`Launch` and `RegisterProfile` are still unsigned requests', and a `Regrant` at rung 1 or above is 'Not built'), so §6's '`launch` operator request' still describes the reference. What stands: §6's first sentence still says the launcher is a script 'today' (:220-221) and the open obligation at :324 is unstruck, against R5; R6 miscalls ADR-0050's status; and no launcher script is under slm/. Both rows are pointers in a Proposed record, and R5 tells the reader the state, hence the lower severity.
- **Verifier's evidence:** decisions/ADR-0036.md:218-223, :324, :352-353; decisions/ADR-0050.md:20; mechanism/GAPS-AND-ASSUMPTIONS.md:106; decisions/ADR-0033.md:499. `grep -rln -i -E 'AgentOp|bridge|operator socket|launcher' slm/` returns only slm/serve/README.md and slm/serve/profile-host-rung0.json; slm/serve/run.sh:2; slm/rehearsal holds drive.py, init.py, slm_tool.py.

### C-51: ADR-0023 §6c, in force, cites ADR-0036 §7's ratification run as a fact; the run has not happened, and §7 names no Observer
- Against: decisions/ADR-0023.md:51 (and decisions/ADR-0036.md:249-250, :352)
- Basis: in force
- Claim: "a deployment runs rung-0 principals beside higher ones (ADR-0036 §7's ratification run grants a rung-0 Observer beside a rung-1 occupant)"
- Why wrong: ADR-0036.md:249 "- A rung-0 principal run beside the rung-1 one, so that the two verdicts differ in the lease and in the profile," (no Observer is named; the rung-0 profile of §1, :109, is "for the host-run occupant"). R5, :352: "§7's condition is not met: there is no profile file for `slm/serve`'s image, no round whose drafted content is the Persona's output, and no results file under `slm/`". An accepted clause's worked example is a Proposed record's unrun condition, stated in the present tense.
- Fix belongs in: decisions/ADR-0023.md §6c (or ADR-0036 §7)
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0023.md:51; decisions/ADR-0036.md:249-250, :352. `grep -n -i observer decisions/ADR-0036.md` returns nothing: the record names no Observer anywhere.

### C-52: ADR-0036 finding 1 quotes ADR-0035's ingress-bounded round in words the record no longer has
- Against: decisions/ADR-0036.md:305-306 (and decisions/ADR-0035.md:156-157)
- Basis: Proposed
- Claim: "Its ingress-bounded round says "a native tool (P4) or a shell (P3) inside such a guest reads only what the guest mounts.""
- Why wrong: ADR-0035.md:156-157 "A shell (P3) or a native tool (P4) *inside* the guest reads only what the guest mounts; a tool that `Invoke` runs *outside* the guest". The bullet was "restated" by ADR-0035 R4 (decisions/ADR-0035.md:424), which disposed of this finding; the finding still presents the superseded sentence as what ADR-0035 "says", and the earlier wording is not kept anywhere in the blind copy to compare.
- Fix belongs in: decisions/ADR-0036.md Findings (mark the quotation as R1's text)
- Severity: Low
- Confidence: medium
- Already on the corpus's own lists: G9 item 32 ("ADR-0035 finding 1 of ADR-0036 | Discharged (G6)") covers the disposition, not the quotation
- **Verifier:** not confirmed
- **Verifier's correction:** The finding already attributes the sentence to the superseded revision: it is headed 'ADR-0035 R1 assumes tools run inside the guest' and 'Its ingress-bounded round says' refers to R1. The record also carries the disposition: its Open obligations strike 'ADR-0035 finding 1's disposition' as 'Disposed by ADR-0035 R4 (2026.09.30)'. Nothing presents the quotation as ADR-0035's current text, and the fix asked for (mark it as R1's) is what the finding's first words do. R1's wording is not in this tree, so the quotation cannot be checked either way.
- **Verifier's evidence:** decisions/ADR-0036.md:305-310, :330; decisions/ADR-0035.md:153-159, :421, :424

