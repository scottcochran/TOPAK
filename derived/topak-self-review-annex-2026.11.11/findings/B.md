# Self review of 2026.11.11: reader B's findings in full

Reader B read the bootstrap set and genesis, ADR-0024 to ADR-0029. Annex to `derived/topak-open-findings-register-2026.11.11.md`, Part III. Each block is the finding as the reader wrote it, against the tree at `bbda621`, followed by the verdict of a verifier that did not find it. Paths are relative to the repository root. A path a finding names as absent is written without backticks. Nothing here is ratified, and every reader and verifier is of the same model lineage as the drafter of the corpus.

35 reported: 23 confirmed, 12 confirmed with a correction, 0 dropped.

### B-1: ADR-0024 A2.2 is in force although the record it rests on, ADR-0035, is Proposed, and A2's own text made that half conditional on ADR-0035
- Against: decisions/ADR-0024.md:71 (and decisions/ADR-0024.md:245, decisions/ADR-0024.md:290, decisions/ADR-0035.md:11)
- Basis: in force
- Claim: "*A promotion round completes only if a veto seat was leased for it with a Persona independent of the author's (ADR-0035 §5) and the author's cell Observer has reported coverage to the seal of the author's round (ADR-0039 §3); otherwise it stalls." and, in the A2 History row, "**ratified 2026.09.29** by the genesis custodian in Batch 15, after ADR-0038 (Batch 13) and ADR-0039 (Batch 14), and applied inline."
- Why wrong: A2's own preamble says "Ratifying A2 is conditional on ratifying ADR-0038 and ADR-0039; the ADR-0035 condition may be ratified with ADR-0035 alone" (decisions/ADR-0024.md:245-246). ADR-0035 has never been ratified: "**Status:** Proposed · 2026.09.25" (decisions/ADR-0035.md:11); G11 lists 0035 as Proposed (checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:52). A2.2 reads independence "according to the promoted independence table (ADR-0035 §4)" (decisions/ADR-0024.md:255-256), a table only a Proposed record defines. The whole of A2 was nevertheless ratified and applied in Batch 15 with no carve-out for A2.2, and the Depends-on line (decisions/ADR-0024.md:15-16) does not name ADR-0035. The same record treats its other amendment that rests on a Proposed record the opposite way: A4 is "**Pending** ... Takes force only with ADR-0054's ratification" (decisions/ADR-0024.md:327). G11 says of ADR-0035's later rule "Until ADR-0035 is in force that is declared and not enforced" (checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:130-131); nothing says the same of A2.2, so a reader cannot tell whether the bootstrap-set promotion rule stalls every promotion (no table exists) or silently omits the condition. ADR-0035's own open obligation still lists "**ADR-0024 amendment** carrying §5's tally condition" as owed (decisions/ADR-0035.md:392).
- Fix belongs in: decisions/ADR-0024.md (A2's History row and §2, stating the force of A2.2), and the next checkpoint's ratification record
- Severity: Medium-High
- Confidence: high
- Already on the corpus's own lists: partly. mechanism/GAPS-AND-ASSUMPTIONS.md G18 (the reference does not build A2.2) and G11 item 20 (ADR-0035 is Proposed). Neither says that in-force text depends on a Proposed record.
- **Verifier:** confirmed with correction
- **Verifier's correction:** The defect stands: A2 was ratified whole in Batch 15, A2.2 with it, while ADR-0035 is Proposed, against A2's own preamble. Two statements need changing. (1) 'Nothing says the same of A2.2' is too wide. A2's History row says 'In the reference, A2.1 and A2.3 are in force ...; **A2.2 is not**, since no independence table exists' (decisions/ADR-0024.md:290), and G18 says 'A promotion completes with a correlated veto seat; the independence half of the veto-seat-outage discharge is declared and not enforced' (mechanism/GAPS-AND-ASSUMPTIONS.md:138). What the reference does is therefore stated: it omits the condition. What no text states is the force of A2.2 in the record while ADR-0035 is Proposed. (2) The title's 'made that half conditional on ADR-0035' is stronger than the sentence, which is permissive: 'the ADR-0035 condition may be ratified with ADR-0035 alone'.
- **Verifier's evidence:** decisions/ADR-0024.md:15-16, 71-73, 245-246, 254-258, 290, 327; decisions/ADR-0035.md:11, 392; checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:52, 129-131; mechanism/GAPS-AND-ASSUMPTIONS.md:138; `grep -rn 'A2\.2' .` read in full: no record or checkpoint line gives A2.2's force in the record, only its state in the reference

### B-2: Four B34 rows say "The reference follows the text", and the reference does not follow the text those rows ratify
- Against: decisions/ADR-0024.md:326, decisions/ADR-0025.md:261, decisions/ADR-0026.md:344, decisions/ADR-0029.md:276 (and decisions/ADR-0050.md:300, mechanism/crates/topak-core/src/rules.rs:192)
- Basis: in force
- Claim: "The reference follows the text (ADR-0033 A10 to A12, ratified with it)."
- Why wrong: (a) ADR-0024 A3's text is "when the tally completes the mechanism grants the principal's first lease at a fresh fence, with no request from anyone" (decisions/ADR-0024.md:46-47), and ADR-0025 A3 and ADR-0029 A3 seat the first operators by issuance (decisions/ADR-0025.md:82-84, decisions/ADR-0029.md:114-116). ADR-0050 §10 says: "**A first lease from a quorum is not built.** §2 is the centre of this record, and the reference does not show it: a promoted seating that grants a first lease, and the first operators seated by an anchor issuance. The unsigned socket stands in, and whoever reaches it can seat." (decisions/ADR-0050.md:300-302). ADR-0033 A11, one of the three addenda the rows cite, "states that a first lease from a quorum is not built" (decisions/ADR-0033.md:1160). (b) ADR-0026 A2's text is "the count it bounds is 1, erasure" and R7 "read as "no activation of an emergency seating grants a lease whose alphabet holds an authority act"" (decisions/ADR-0026.md:53-56). The reference has `pub const EXCEPTION_BOUND: usize = 2;` (mechanism/crates/topak-core/src/rules.rs:192) and still checks R7 against the retired envelope: "// R7 : no break-glass grant may authorize Issue, Vote, or promotion." over `bg.actions` (mechanism/crates/topak-core/src/rules.rs:223-226). The same sentence stands in other Batch 34 dependent rows (decisions/ADR-0016.md:250, decisions/ADR-0031.md:423), which reads as template text.
- Fix belongs in: the B34 History rows of ADR-0024, ADR-0025, ADR-0026 and ADR-0029
- Severity: Medium-High
- Confidence: high
- Already on the corpus's own lists: the debts are (G11 items 88, 90 and 92); the four rows' claim is not.
- **Verifier:** confirmed with correction
- **Verifier's correction:** Scope. The sentence is in 17 B34 rows, not four plus two: `grep -rn 'The reference follows the text' decisions` returns ADR-0009:63, 0013:250, 0016:250, 0022:308, 0024:326, 0025:261, 0026:344, 0029:276, 0030:564, 0031:423, 0037:500, 0039:431, 0040:256, 0041:318, 0042:337, 0043:269, 0045:524. The four named rows conflict as stated. ADR-0031:423 has conflict (a) as well, since its A3 says a first lease is granted 'on a quorum, an issuance or a promotion's tally' (decisions/ADR-0031.md:422). The other twelve were not checked here, so the fix reaches past the four rows named.
- **Verifier's evidence:** decisions/ADR-0024.md:46-47, 326; decisions/ADR-0025.md:82-84, 261; decisions/ADR-0026.md:52-56, 344; decisions/ADR-0029.md:114-116, 276; decisions/ADR-0050.md:300-302; decisions/ADR-0033.md:1160 ('It states that a first lease from a quorum is not built'); mechanism/crates/topak-core/src/rules.rs:192, 219-229

### B-3: ADR-0029's own confirmation marking is stated three ways: A2 only, A2 and A4, and not at all
- Against: decisions/ADR-0029.md:9 (and decisions/ADR-0029.md:275, checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:50, decisions/README.md:42, narrative/glossary.md:1130)
- Basis: in force
- Claim: "**Status note:** Confirmation required: **for A2 only (C3)**. The record otherwise defines the phase and carries no marker."
- Why wrong: The record's own A4 row says "Confirmation-required under C3 with A2: it adds a way to ratify a record that the phase as defined did not have" (decisions/ADR-0029.md:275). G11 §1.1 counts "0029 (for A2 and A4 only)" among the 27 (checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:50). The glossary says "ADR-0029's own is in its status note, for A2 and A4 only" (narrative/glossary.md:1130), which the status note does not say. The index gives ADR-0029 as plain "Accepted (genesis)" (decisions/README.md:42), while its siblings with a scoped marking carry it there ("confirmation required: C1, for A2 only", decisions/README.md:16; "C2 for A1 only", decisions/README.md:44). The status line (decisions/ADR-0029.md:8) carries no marking at all, unlike ADR-0003's.
- Fix belongs in: decisions/ADR-0029.md (Status line and Status note); decisions/README.md
- Severity: Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0029.md:8-9, 257 ('carries C3, scoped to A2'), 275 ('Confirmation-required under C3 with A2'); checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:50; narrative/glossary.md:1129-1130; decisions/README.md:16, 42, 44; decisions/ADR-0003.md:10 (a sibling's status line carries its scoped marking)

### B-4: ADR-0029 A2 is "Applied" and none of the four clauses it changes shows the change; §6 still states the rule A2.4 struck
- Against: decisions/ADR-0029.md:140 (and decisions/ADR-0029.md:185, decisions/ADR-0029.md:257)
- Basis: in force
- Claim: "Genesis-ratified records without the marker are **not** re-reviewed. The confirmation set is the whole of the deferred-review debt."
- Why wrong: A2.4 says ""Genesis-ratified records without the marker are not re-reviewed" is replaced: every record is reviewed at bootstrap under A2.1" and that the closing sentence "is struck as false under this amendment" (decisions/ADR-0029.md:185-190), and the History row gives A2 as "**Applied** : ratified 2026.09.25 by the genesis custodian" (decisions/ADR-0029.md:257). Neither sentence is struck in §6. The same holds for the other three clauses. §4 still reads "Those records are covered by the genesis attestation (§5) and ADR-0025's intent axiom" (decisions/ADR-0029.md:78) though A2.3 says "The sentence that follows it is struck" (decisions/ADR-0029.md:179-180); it is also not the sentence that follows the one A2.3 quotes, since two others intervene. §5 still opens "The trigger and the ceremony are unchanged from revision 1" with a one-condition trigger and a three-item bundle (decisions/ADR-0029.md:88-91, 117-120) though A2.1 adds a second condition and A2.2 "a fourth content". §7's ledger list has three lines (decisions/ADR-0029.md:148-151) though A2.5 adds one. The corpus's stated convention is "**Applied** changes show struck text inline" (decisions/ADR-0028.md:144), and ADR-0024 A2, ratified four days later, was applied that way (decisions/ADR-0024.md:94, 228-232). A reader of §6 alone gets the reversed rule.
- Fix belongs in: decisions/ADR-0029.md §4, §5, §6, §7
- Severity: Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0029.md:76-78, 88-91, 97 (A1's strike is shown inline in the same record), 117-120, 140-141, 148-151, 164-194, 257; decisions/ADR-0028.md:144; decisions/ADR-0024.md:94, 228-232

### B-5: Amendments that depend on a provisional record and land outside the bootstrap set have no confirmation state; ADR-0029's own A3 is one
- Against: decisions/ADR-0029.md:58 and decisions/ADR-0029.md:81 (and decisions/ADR-0029.md:276, decisions/ADR-0016.md:250, narrative/glossary.md:39)
- Basis: in force
- Claim: "It is confirmation-required, whatever §4 says of its content." and "They are not confirmation-required, for the reason above: confirmation runs under the bootstrap set."
- Why wrong: §3 makes a provisional record confirmation-required; §4's A4 paragraph exempts a provisional record's dependent amendments only when they "land in the bootstrap set" (decisions/ADR-0029.md:80-82). Nothing states the case of a dependent amendment that lands elsewhere. ADR-0029 A3 is one: "**A3 depends on a record ratified provisional** (ADR-0050 or ADR-0052): the text is in force and subject to redesign with that record (ADR-0029 A4)" (decisions/ADR-0029.md:276), with no word on confirmation, while the Status note says "for A2 only" and G11 says "for A2 and A4 only" (B-3). ADR-0016 A1 and A2 are two more: the same row text (decisions/ADR-0016.md:250), and the record stays in G11's unmarked eighteen (checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:49; decisions/ADR-0016.md:8). The glossary reads the rule as covering them: "Defined by a record or amendment Accepted **provisional**: in force, confirmation-required, and subject to redesign" (narrative/glossary.md:39) and "Two records carry it, ADR-0050 and ADR-0052, and every amendment that depends on either does too" (narrative/glossary.md:1136). If that reading holds, the ledger's count of 29 (checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:248) omits every record whose only marking would come from such an amendment.
- Fix belongs in: decisions/ADR-0029.md §3 or §4 (the rule), then the status notes it reaches and the next checkpoint's ledger
- Severity: Medium
- Confidence: medium
- Already on the corpus's own lists: no
- **Verifier:** confirmed with correction
- **Verifier's correction:** Line number only: ADR-0016's status line is decisions/ADR-0016.md:11, not :8, which is a blank line. The gap is real: no text gives the confirmation state of a provisional record's dependent amendment that lands outside the bootstrap set, and ADR-0029 A3 and ADR-0016 A1 and A2 are such amendments in records with no marking for them.
- **Verifier's evidence:** decisions/ADR-0029.md:9, 58, 80-84, 276; decisions/ADR-0016.md:11, 250; narrative/glossary.md:39, 1136; checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:49-51, 248; `grep -n -i 'dependent amendment\|dependent entr' decisions/ADR-0029.md decisions/ADR-0050.md decisions/ADR-0052.md`: the only rule is ADR-0029:80, for the bootstrap set

### B-6: Two batches were ratified after the state of record, one of them on a bootstrap-set record, and no checkpoint, index or narrative records them
- Against: checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:9 and checkpoints/README.md:3 (and decisions/ADR-0024.md:329, decisions/ADR-0046.md:514, narrative/glossary.md:1176)
- Basis: in force
- Claim: "**What changed at G11.** Two batches were ratified, **36 and 37**, where G10 had nine." ; "**Current state of record: [Genesis Checkpoint G11](topak-genesis-checkpoint-G11-2026.10.09.md)**" ; and in the glossary "**Batch** [C]: a ratification group. There are thirty-seven"
- Why wrong: ADR-0024 carries "**E1 ratified 2026.11.02** by the genesis custodian (ADR-0029 §2), in Batch 38, alone, and applied inline" and "The pin moves." (decisions/ADR-0024.md:329). ADR-0046 carries "**A3 ratified 2026.11.03** by the genesis custodian (ADR-0029 §2), in Batch 39, with ADR-0045 A4" and "**Confirmation required under C4 for A3**" (decisions/ADR-0046.md:514). Command, run at the root of the copy: `grep -rl -E 'Batch (38|39|40)' . --include=*.md`. Output: `spec/proof-certification.md`, `spec/README.md`, `decisions/ADR-0045.md`, `decisions/ADR-0046.md`, `decisions/ADR-0024.md`. No checkpoint, `checkpoints/README.md`, `decisions/README.md`, root `README.md` or narrative file names either batch. The precedence rule puts the checkpoint above the decisions, and the checkpoint is where "what was ratified and by whom" is kept (checkpoints/README.md:4), so two ratifications have no standing in the layer that wins. Consequences already visible: G11 and the glossary still say the prover's defects are not reported upstream (checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:15; narrative/glossary.md:1554), where ADR-0046 A3 says they were reported 2026.10.18 (decisions/ADR-0046.md:513); a new C4 marking is in no ledger; ADR-0024's pin moved after the cut that measures it.
- Fix belongs in: a checkpoint after G11, or a dated note in checkpoints/README.md as its errata table does for G9; narrative/glossary.md
- Severity: Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** `grep -rl -E 'Batch (38|39|40)' . --include=*.md` rerun: spec/proof-certification.md, spec/README.md, decisions/ADR-0045.md, decisions/ADR-0046.md, decisions/ADR-0024.md and no other file; decisions/ADR-0024.md:329; decisions/ADR-0046.md:513-514; checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:9, 15; checkpoints/README.md:3-6, 52 (the errata table has one row, for G9); narrative/glossary.md:1176-1177, 1554; REVIEWERS_GUIDE_README.md:61-62 (state of record ranked above decisions)

### B-7: R6 has been in the genesis rules floor since 2026.09.23 and no non-vacuity run covers it; the module treats its subject as issued and the reference as a constant
- Against: decisions/ADR-0026.md:124 and decisions/ADR-0026.md:264 (and decisions/ADR-0026.md:225, spec/RulesFloorBase.tla:38, mechanism/crates/topak-core/src/rules.rs:190)
- Basis: in force
- Claim: "The genesis rules floor is now **R1, R2, R5, R6, R7, R9**." beside "**Verdict for ADR-0024 revision 5 with floor R1, R2, R5, R7, R9:** every entry is non-vacuous"
- Why wrong: §7's model states "The floor is R1, R2, R5, R7, R9." (decisions/ADR-0026.md:225), and the module has `AllEntries == {"R1", "R2", "R5", "R7", "R9"}` (spec/RulesFloorNV_rev5.tla:51) and no `exceptions` field (spec/RulesFloorNV_rev5.tla:41-42). §6 covers "R1–R5 and R7" (decisions/ADR-0026.md:118). Command: `grep -rn -E 'dropR6|[Dd]rop R6|P6_' spec decisions` prints nothing; in every results row where "R6" appears it is a member of `Active` and is never the entry dropped (spec/bootstrap-results-2026.09.23.txt:5, 142). No property names what R6 protects and no mutation drops it, although §3 says "ADR-0007's totality, non-vacuity, and discrimination gates apply here" (decisions/ADR-0026.md:74) and the record's own A1 note required exactly that of R8: "a mutation dropping R8 that must break `P8_BreakGlassEnds`" (decisions/ADR-0026.md:315-316). The record's test for vacuity is "a value the mechanism fixes as a constant cannot be bounded by a floor entry" (decisions/ADR-0026.md:69-70). spec/RulesFloorBase.tla:38 models the count as an issued field (`exceptions  : 0..3`). The reference takes it from the loaded policy floor: "The exceptions live in the policy floor, so this is checked against the floor text the mechanism loaded" (mechanism/crates/topak-core/src/rules.rs:190-191); `Rules` has no such field (mechanism/crates/topak-core/src/rules.rs:92-132); and `validate_issuance` passes the state's `floor_exceptions` for every issuance (mechanism/crates/topak-core/src/rules.rs:336, 350). At the reference no issuance can violate R6, which is the record's own description of a vacuous entry.
- Fix belongs in: decisions/ADR-0026.md (§2 or a new non-vacuity section) and a dated successor to the non-vacuity module
- Severity: Medium
- Confidence: high on the missing run; medium on the vacuity conclusion
- Already on the corpus's own lists: partly. G11 §2.1 says "The ADR-0026 §6 rerun is still owed" and the glossary's item 39 gives its subject as A2.2 and A2.3; neither names R6.
- **Verifier:** confirmed
- **Verifier's evidence:** `grep -rn -E 'dropR6|[Dd]rop R6|P6_' spec decisions` rerun: no output, exit 1; decisions/ADR-0026.md:69-70, 74, 118, 123-126, 225, 264, 314-316; spec/RulesFloorNV_rev5.tla:41-42, 51; spec/RulesFloorBase.tla:38, 44; spec/bootstrap-results-2026.09.23.txt:5, 17, 40, 63, 75, 101, 142 and spec/BreakGlass_A1-rows.txt:2, 8 (R6 is in every Active set; the only entry ever dropped is R7); mechanism/crates/topak-core/src/rules.rs:92-132, 190-192, 220, 336, 350; mechanism/crates/topak-core/src/state.rs:618, 715-725 (the count is set once at genesis)

### B-8: The Enabling condition clause does not carry the two conjuncts ADR-0024 A2 says it has
- Against: decisions/ADR-0024.md:136 (and decisions/ADR-0024.md:272, mechanism/crates/topak-core/src/promotion.rs:1)
- Basis: in force
- Claim: the `PromotionEnabled(a)` block at decisions/ADR-0024.md:136-143, which ends "/\ \A s \in r.vetoSeats : votes[a][s] # <<"deny", a.digest, a.evidence, rulesEpoch>>"
- Why wrong: A2 says the tally gained two conditions and that "each is a new conjunct of `PromotionEnabled`" (decisions/ADR-0024.md:272-273); §2 calls both "mechanism constants in the tally" (decisions/ADR-0024.md:73). The clause printed under "### Enabling condition" has neither, and its closing note still describes it only as the replacement of the revision-4 snippet (decisions/ADR-0024.md:149-150). A2's list of what it "does not touch" (decisions/ADR-0024.md:271) omits this clause, so it is neither amended nor declared untouched. The reference shows the drift: its header says "The tally follows the `PromotionEnabled` snippet in ADR-0024 line for line" (mechanism/crates/topak-core/src/promotion.rs:1-2) and then adds a `covered` condition and a `Tally::Stalled` outcome that the snippet lacks (mechanism/crates/topak-core/src/promotion.rs:36-38, 94-95).
- Fix belongs in: decisions/ADR-0024.md, Enabling condition
- Severity: Medium
- Confidence: high
- Already on the corpus's own lists: partly. The rerun is owed (decisions/ADR-0024.md:235-237; G11 §2.1; glossary item 39). The stale clause is not listed.
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0024.md:71-73, 133-150, 235-237, 271-274; mechanism/crates/topak-core/src/promotion.rs:1-2, 36-38, 49-53, 94-96

### B-9: The circularity ADR-0029 §4 forbids is back: the tally that would confirm ADR-0038 and ADR-0039 is defined by ADR-0038 and ADR-0039
- Against: decisions/ADR-0029.md:76 (and decisions/ADR-0024.md:94, decisions/ADR-0038.md:12, decisions/ADR-0039.md:12)
- Basis: in force
- Claim: "The confirmation promotion runs under 0024, 0025, 0026, and 0027. Confirming the rules that confirmation runs under would be circular."
- Why wrong: Since A2, ADR-0024's in-force veto roster is "*Every cell Observer seat and every correlator seat in the Build domain (ADR-0038 §6)*" (decisions/ADR-0024.md:94) and its tally stalls without coverage "(ADR-0039 §3)" (decisions/ADR-0024.md:72-73). ADR-0038 is "confirmation required (ADR-0029 C3, C4)" (decisions/ADR-0038.md:12) and ADR-0039 "confirmation required (ADR-0029 C4)" (decisions/ADR-0039.md:12). Their confirmation promotions therefore run under rules whose content they supply, which is the case §4 calls circular. A2's row disposes of it in one clause, "Not confirmation-required: a bootstrap record (ADR-0029 §4)" (decisions/ADR-0024.md:290), and does not say what becomes of ADR-0024 §5 if ADR-0038's confirmation is "**Rejected**" and "A superseding record is required" (decisions/ADR-0029.md:138). ADR-0029 A4 sees the problem for provisional dependents only: "so that what the bootstrap reviewer attests to includes the fact that part of the rules it runs under is expected to change" (decisions/ADR-0029.md:83-84). ADR-0024 A2's dependents predate A4 and carry no such statement.
- Fix belongs in: decisions/ADR-0029.md §4 (the exception's reach) and decisions/ADR-0024.md A2
- Severity: Medium
- Confidence: medium
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0029.md:76-84, 138; decisions/ADR-0024.md:71-73, 94, 290; decisions/ADR-0038.md:12; decisions/ADR-0039.md:12; `grep -n -i circular decisions/ADR-0024.md decisions/ADR-0038.md decisions/ADR-0039.md checkpoints/*.md` returns nothing, and the hits in ADR-0029 (78, 157-159, 183, 198, 204), the glossary (1140) and the Theory of Operation (1290, 1787) speak only of the bootstrap set under itself

### B-10: ADR-0024 says the 2026.09.23 rerun checks "the enabling condition above"; the module checks two of its conjuncts
- Against: decisions/ADR-0024.md:310 (and spec/RulesFloorNV_rev5.tla:88, decisions/ADR-0026.md:268)
- Basis: evidence
- Claim: "**the rerun against this revision is ADR-0026 §7, run 2026.09.23** : the enabling condition above is the one it checks, with the ADR-0022 `Vote` envelope modeled alongside it."
- Why wrong: The module's condition is `PromotionEnabled == /\ Cardinality(Counted) >= rules.minGrant /\ IF rules.quorum.mode = "all" THEN Recorded = Counted ELSE Cardinality(Recorded) >= rules.quorum.k` (spec/RulesFloorNV_rev5.tla:88-92). It has no `GatesPass(a)`, no `Refines(a.bundle, PolicyFloor)` and no veto-seat conjunct (the rule space has no veto roster, spec/RulesFloorNV_rev5.tla:41-42), and votes are the strings "grant" and "deny" with no (digest, evidence, epoch) triple (spec/RulesFloorNV_rev5.tla:78, 102-104). ADR-0026 §7 admits one of these, "no veto seats" (decisions/ADR-0026.md:268). ADR-0024 admits none.
- Fix belongs in: decisions/ADR-0024.md, History ("Unchanged by R1 and R2")
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed with correction
- **Verifier's correction:** ADR-0026 §7's Scope admits more than one of the omissions: 'Small constants, a single artifact, a single issuance, no veto seats' (decisions/ADR-0026.md:268) covers the veto conjunct and also the digest and epoch parts of the vote triple, since the model has one artifact and Issue resets every vote (spec/RulesFloorNV_rev5.tla:95-98). `GatesPass`, `Refines` and the evidence component are admitted nowhere. The defect stands: ADR-0024 says the enabling condition 'is the one it checks' and states none of these abstractions.
- **Verifier's evidence:** decisions/ADR-0024.md:136-143, 308-311; spec/RulesFloorNV_rev5.tla:41-42, 78, 88-92, 95-104; `grep -n 'GatesPass\|Refines\|veto' spec/RulesFloorNV_rev5.tla` returns nothing; decisions/ADR-0026.md:268

### B-11: ADR-0026 gives R6's count as 2 in two places and as 1 in a third, all in text in force
- Against: decisions/ADR-0026.md:48 and decisions/ADR-0026.md:125 (and decisions/ADR-0026.md:53)
- Basis: in force
- Claim: "| **R6** Bound on floor-exception count (current count: 2) | ADR-0013 |" and "R6 bounds the floor-exception count, currently 2 : erasure and break-glass"
- Why wrong: A2, ratified in Batch 34 and applied inline, says "R6 still bounds the number of floor exceptions; the count it bounds is 1, erasure" (decisions/ADR-0026.md:52-53). The table row and the open-obligation bullet were not struck. A2 also does not say whether the bound moved or only the count. G10 reads it as the bound: "`RulesFloorBase.tla` still carries `bgScope` and R6's bound of two (ADR-0026 A2)" (checkpoints/topak-genesis-checkpoint-G10-2026.10.05.md:367). The module and the reference both still bound at two: `[] e = "R6" -> r.exceptions <= 2` (spec/RulesFloorBase.tla:44) and `EXCEPTION_BOUND: usize = 2` (mechanism/crates/topak-core/src/rules.rs:192).
- Fix belongs in: decisions/ADR-0026.md §2 and Open obligations
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: partly. G11 item 90 covers `RulesFloorBase.tla`; the record's own two stale places and the reference's constant are not listed.
- **Verifier:** confirmed with correction
- **Verifier's correction:** Leaving the §2 table row unstruck is the corpus's stated practice for dependent amendments, which 'were applied by removing the pending mark, not by rewriting the sentences above them' (checkpoints/topak-genesis-checkpoint-G10-2026.10.05.md:85-87), and A2's paragraph stands directly under that row. The convention does not reach the Open-obligations bullet (decisions/ADR-0026.md:124-126), which has no A2 text beside it, and it does not settle whether the bound moved: A2 says 'the count it bounds is 1', G10 item 90 treats 'R6's bound of two' as stale, and the module and the reference still bound at 2. The defect stands on those two points.
- **Verifier's evidence:** decisions/ADR-0026.md:48, 52-53, 124-126, 343; checkpoints/topak-genesis-checkpoint-G10-2026.10.05.md:85-87, 367; spec/RulesFloorBase.tla:44, 58; mechanism/crates/topak-core/src/rules.rs:192; narrative/glossary.md:544

### B-12: ADR-0026 A1 was withdrawn on 2026.10.04 and the record still marks it pending in four places
- Against: decisions/ADR-0026.md:61, decisions/ADR-0026.md:130, decisions/ADR-0026.md:282, decisions/ADR-0026.md:297 (and decisions/ADR-0026.md:13, decisions/ADR-0026.md:342)
- Basis: in force
- Claim: "*Pending ⟨A1⟩, not applied:* R8 would enter this table as `0 < rules.breakGlass.ttl ≤ T_BG`." ; "*Drafted as A1, pending* ⟨A1⟩." ; "**Pending** : drafted 2026.09.24, not ratified. Four conditions in the A1 note" ; "**A1 note (pending).**"
- Why wrong: The header says A1 "was **withdrawn 2026.10.04** by the custodian and never in force" (decisions/ADR-0026.md:13), and W1 says "The R8 candidate in the open obligations is closed as not taken" (decisions/ADR-0026.md:342). The candidate bullet is not struck, the inline marker in §2 (inside the pinned clause) still says pending, and the R9 row still says "R8 remains reserved for the break-glass TTL candidate" (decisions/ADR-0026.md:50). Downstream artifacts repeat it: "R8 reserved, candidate (break-glass grant TTL)" (spec/RulesFloorBase.tla:14) and "R8 is reserved and not implemented" (mechanism/crates/topak-core/src/rules.rs:199).
- Fix belongs in: decisions/ADR-0026.md §2, Open obligations and the A1 History row
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed with correction
- **Verifier's correction:** Of the four places, the 'A1 note (pending)' heading at :297 is reconciled where it stands: the paragraph above it says '**A1 is withdrawn** (W1, 2026.10.04) ... The note is kept as written' (decisions/ADR-0026.md:291-295). The other three are stale as stated: the inline marker at :61, the candidate bullet at :130, which W1 says 'is closed as not taken' (:342) and which is not struck, and the A1 row's State at :282. The R9 row's 'R8 remains reserved for the break-glass TTL candidate' (:50) is a fourth.
- **Verifier's evidence:** decisions/ADR-0026.md:13, 50, 61, 130, 282, 291-297, 342; spec/RulesFloorBase.tla:14; mechanism/crates/topak-core/src/rules.rs:199

### B-13: ADR-0024 §7 says the record does not depend on ADR-0021; A2.3, in force, defines its stall condition by ADR-0021 §3, and the Depends-on line names none of A2's or A3's sources
- Against: decisions/ADR-0024.md:109 (and decisions/ADR-0024.md:261, decisions/ADR-0024.md:15, decisions/ADR-0024.md:271)
- Basis: in force
- Claim: "**this record does not depend on that**, and nothing here requires ADR-0021 to be ratified first ⟨R2⟩"
- Why wrong: A2.3: "A promotion round completes only if the author's cell Observer has reported a watermark at or beyond the seal of the author's round topic set (ADR-0021 §3; ADR-0039 §1)" (decisions/ADR-0024.md:260-261). ADR-0021 §3 is the clause that defines that seal: "**Sealing moves from emit completion to gate submission.**" (decisions/ADR-0021.md:101). When A2 was ratified (Batch 15, 2026.09.29) ADR-0021 was still Proposed; its status line dates acceptance 2026.09.30 (decisions/ADR-0021.md:11). That is the dependency R2 was written to remove. A2 lists §7 among what it "does not touch" (decisions/ADR-0024.md:271). The header still reads "**Depends on:** ADR-0025 (roster issuance), ADR-0026 (bounds R1, R2, R9 on quorum parameters) ⟨R1⟩, ADR-0010 (policy floor), ADR-0007 (gates), ADR-0022 (`Vote`)" (decisions/ADR-0024.md:15-16), with no ADR-0021, ADR-0035, ADR-0038, ADR-0039 or ADR-0050, each of which in-force text cites as its source.
- Fix belongs in: decisions/ADR-0024.md §7 and header
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0024.md:15-16, 108-112, 260-261, 271; decisions/ADR-0021.md:11-13 (accepted 2026.09.30; its note says ADR-0039 §3 cited its §3 while Proposed), 101-103

### B-14: R5 is stated three ways: "for the same artifact" in the record, against a constant one-member anchor set in the modules, and over grant and veto rosters against the issued anchor keys in the reference
- Against: decisions/ADR-0026.md:47 (and spec/RulesFloorBase.tla:21, spec/RulesFloorBase.tla:43, spec/RulesFloorNV_rev5.tla:27, mechanism/crates/topak-core/src/rules.rs:212, decisions/ADR-0025.md:64)
- Basis: in force
- Claim: "| **R5** No key both in the anchor key set and on the promotion roster for the same artifact | ADR-0025 / ADR-0024 |"
- Why wrong: Both modules write `[] e = "R5" -> r.grant \cap AnchorKeys = {}` (spec/RulesFloorBase.tla:43; spec/RulesFloorNV_rev5.tla:47), with no artifact in it, and the record's own derivation reads the entry unconditionally: "R5 keeps the two sets disjoint" (decisions/ADR-0026.md:195). The qualifier "for the same artifact" is modelled nowhere. Second, `AnchorKeys == {"h4"}` is a constant (spec/RulesFloorBase.tla:21; spec/RulesFloorNV_rev5.tla:27) and the rule space has no anchor-key field (spec/RulesFloorBase.tla:34-38), while ADR-0025 §1 makes "**(c)** The anchor's own key set." an issued rule (decisions/ADR-0025.md:64) and the reference carries `anchor_keys` in `Rules` (mechanism/crates/topak-core/src/rules.rs:99). So `FloorPreserved`, P5 and R5's dropped-entry row quantify over issuances that change the roster and never over issuances that change the anchor set; neither §7 nor the B25 row says so. Third, the reference's R5 reads `r.grant_roster.iter().chain(&r.veto_roster)` (mechanism/crates/topak-core/src/rules.rs:212), which is wider than both. One anchor key-holder is also custody (1, 0), which §6's note flags for the 09.15 model (decisions/ADR-0026.md:207-208) and §7 repeats without the flag ("anchor key-holder h4", decisions/ADR-0026.md:224).
- Fix belongs in: decisions/ADR-0026.md §2 (R5's wording) and §7 (the abstraction); a successor module if (c) is to be modelled
- Severity: Low-Medium
- Confidence: high on the three texts; medium on which is intended
- Already on the corpus's own lists: no. G11 item 106 is a different issuance question.
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0026.md:47, 195, 207-208, 224-225, 268, 289; spec/RulesFloorBase.tla:21, 34-38, 43; spec/RulesFloorNV_rev5.tla:27, 41-42, 47; decisions/ADR-0025.md:64; mechanism/crates/topak-core/src/rules.rs:99, 211-216

### B-15: ADR-0029 §5 still names `BreakGlass` and `BreakGlassNeverChangesAuthority`; the mechanism in force is modelled by `BreakGlass_A1` under a different invariant, and ADR-0029 has no entry for it
- Against: decisions/ADR-0029.md:99 and decisions/ADR-0029.md:260 (and spec/BreakGlass_A1.tla:5, decisions/ADR-0052.md:204, spec/BreakGlass.tla:40)
- Basis: in force
- Claim: "| `BreakGlass` | `BreakGlassNeverChangesAuthority` |" and "**Two of §5's five bootstrap invariants are proved.**"
- Why wrong: `spec/BreakGlass.tla` models an issued envelope: `Admits(x) == IF Mut = "M_SCOPE" THEN x \in BGActs ... ELSE x \in rules.bgScope` (spec/BreakGlass.tla:40-41). ADR-0026 A2, in force, says "R7 has nothing left to refuse" and "What the rules carry for break-glass is the roster and its quorum" (decisions/ADR-0026.md:55-57). ADR-0052 §9 says the successor is "`spec/BreakGlass_A1.tla` (`b586a6afa4fd5136`), for ADR-0029 §5's fifth invariant under ADR-0026 A2's reading of R7" (decisions/ADR-0052.md:204), and that module's invariant is `EmergencyNeverChangesAuthority` (spec/BreakGlass_A1.tla:5, 94), proved without assuming R7 (decisions/ADR-0052.md:209-210). ADR-0029 changed an invariant's name by amendment once for this very reason: a module under the old name "would either check a weaker mechanism than the one deployed or contradict its own title" (decisions/ADR-0029.md:106-107). No row in ADR-0029 records the second case, so "two of five proved" counts a proof of a mechanism since retired, and the fifth invariant's name in §5 matches no module of the mechanism in force.
- Fix belongs in: decisions/ADR-0029.md (§5 table or a dependent History row)
- Severity: Low-Medium
- Confidence: medium
- Already on the corpus's own lists: partly. G11 item 90 (`spec/` behind the records); the glossary's Bootstrap trigger entry notes the succession (narrative/glossary.md:1150-1151). ADR-0029 does not.
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0029.md:99, 103-110, 260; `grep -n 'BreakGlass_A1\|EmergencyNeverChangesAuthority' decisions/ADR-0029.md` returns nothing; spec/BreakGlass_A1.tla:2-5, 94; spec/BreakGlass.tla:40-41; decisions/ADR-0052.md:204-211; decisions/ADR-0026.md:55-59; narrative/glossary.md:1149-1152

### B-16: "The genesis attestation" is cited to §5, which defines no such thing, and A4 uses it for what the reviewer signs
- Against: decisions/ADR-0029.md:78 (and decisions/ADR-0029.md:82, decisions/ADR-0029.md:173)
- Basis: in force
- Claim: "Those records are covered by the genesis attestation (§5) and ADR-0025's intent axiom."
- Why wrong: Command: `grep -n -i 'genesis attestation' decisions/ADR-0029.md` returns lines 78, 82, 180, 181 and 275. None is in §5 (decisions/ADR-0029.md:86-128), which says only "Every key-holder signs the bundle digest" (decisions/ADR-0029.md:121). The only attestation §5 gains is A2.2's "review attestation : reviewer identities, the manifest digest reviewed, the scope, and the findings disposition" (decisions/ADR-0029.md:173-174), and A2.3 lists "the bootstrap review (A2.1), the genesis attestation, and the intent axiom" as three things (decisions/ADR-0029.md:181). A4 then writes "They are covered by the genesis attestation like the rest of it, and **the attestation names them as provisional**, so that what the bootstrap reviewer attests to includes the fact that part of the rules it runs under is expected to change" (decisions/ADR-0029.md:82-84): the attestation that must name the provisional amendments is the genesis attestation in the first half of the sentence and the reviewer's in the second. Which document must carry the names, and who signs it, cannot be read from the record.
- Fix belongs in: decisions/ADR-0029.md §4 and §5
- Severity: Low-Medium
- Confidence: medium
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** `grep -n -i 'genesis attestation' decisions/ADR-0029.md` rerun: lines 78, 82, 180, 181, 275, none inside §5 (86-128); decisions/ADR-0029.md:121, 173-176, 181; `grep -rn -i 'genesis attestation' --include=*.md .` finds no definition, only uses (narrative/theory-of-operation.md:1293, 1625; checkpoints/topak-genesis-checkpoint-G10-2026.10.05.md:47, 83; the B34 rows of ADR-0024, ADR-0025 and ADR-0026)

### B-17: The provisional exit turns on "a reader who is not the drafter", a role ADR-0029 never defines, and the ratification rows cite A2.5 for it
- Against: decisions/ADR-0029.md:58 (and decisions/ADR-0029.md:168, decisions/ADR-0029.md:193, decisions/ADR-0024.md:326)
- Basis: in force
- Claim: "It stops being provisional when the debt is built and seen at the reference **and** a reader who is not the drafter has reviewed the record" and, in each B34 row, "**Not reviewed by a reader other than the drafter** (ADR-0029 A2.5)."
- Why wrong: ADR-0029 names one person, "Scott, sole custodian" (decisions/ADR-0029.md:39), and A2.1 requires "at least one reviewer who is not the author" (decisions/ADR-0029.md:168). "Drafter" appears only in A4's text. Since the History rows say the text was "drafted 2026.10.04 by the assistant at the custodian's direction" (decisions/ADR-0024.md:325), the custodian is a reader who is not the drafter, and G11 writes as if that counts: each row says it was not reviewed by another reader "beyond the custodian's reading of one transcription (B36) and of 67 steps (B37)" (checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:84-85), while the same checkpoint says of those readings "none counts under A2.1" (checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:262). So the exit condition can be read as met by the ratifier's own reading. The citation is also to the wrong clause: A2.5 is "the debt ledger names the reviewer" (decisions/ADR-0029.md:193-194) and says nothing about a reader or a drafter; ADR-0050 and ADR-0052 cite "(ADR-0029 A2)" for the same phrase (decisions/ADR-0050.md:307, decisions/ADR-0052.md:239).
- Fix belongs in: decisions/ADR-0029.md §3 (define the role) and the B34 row text
- Severity: Low-Medium
- Confidence: medium
- Already on the corpus's own lists: G11 item 66 ("An ADR-0029 criterion for assisted drafting", open). The A2.5 citation is not listed.
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0029.md:39, 58, 168, 193-194, 275-276 (`grep -n -i drafter decisions/ADR-0029.md` finds the word at 58, 275 and 276 only); decisions/ADR-0024.md:325-326; checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:83-85, 262, 332 (item 66, open); decisions/ADR-0050.md:307; decisions/ADR-0052.md:239

### B-18: ADR-0029 §6 runs confirmation "under ADR-0024", and ADR-0024's tally now needs an author's round, cell Observer and Persona lineage that a genesis-ratified record does not have
- Against: decisions/ADR-0029.md:132 (and decisions/ADR-0024.md:71)
- Basis: in force
- Claim: "Every confirmation-required record goes through a **confirmation promotion**, in dependency order, under ADR-0024 with author recusal:"
- Why wrong: Since A2, "A promotion round completes only if a veto seat was leased for it with a Persona independent of the author's (ADR-0035 §5) and the author's cell Observer has reported coverage to the seal of the author's round (ADR-0039 §3); otherwise it stalls" (decisions/ADR-0024.md:71-73). The confirmation set was written outside any Build round: "Every ADR so far was drafted, reviewed, and ratified by one person" (decisions/ADR-0029.md:20), and "**Every text ratified since G10 is the drafter's**, the assistant's at the custodian's direction" (checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:83). No record says what the author's round, its seal, its cell Observer or the author's Persona are for a confirmation promotion, so on the text as written each one stalls. §6 predates A2 and was not revisited when A2 was ratified.
- Fix belongs in: decisions/ADR-0029.md §6, or decisions/ADR-0024.md §2 saying how the two conditions apply to a record
- Severity: Low-Medium
- Confidence: low
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0029.md:20, 132-133, 187-188; decisions/ADR-0024.md:40-41 (promotion covers bundles, mechanism releases and Personas; a record is not named), 71-73; checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:83; `grep -rn -i 'confirmation promotion' --include=*.md .` read in full: no hit says what the author's round, its seal, its cell Observer or the author's Persona are for one; narrative/architecture-description.md:47 only asks 'What does a confirmation promotion confirm?'

### B-19: The decisions index says its statuses are as of G11, heads the column "Status at G8", and omits the confirmation marking of three records G11 counts as marked
- Against: decisions/README.md:3 and decisions/README.md:12 (and decisions/README.md:60, checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:50, decisions/ADR-0047.md:19)
- Basis: living document
- Claim: "**Status is as of Genesis Checkpoint G11 (2026.10.09)**" and "| Record | Title | Status at G8 | Superseded by |"
- Why wrong: The two statements name different cuts, and neither is true of the table: it lists thirteen records each marked "after G11" (decisions/README.md:69-81). For ADR-0047, ADR-0048 and ADR-0049 it gives "Accepted (genesis) · Batch 34, 2026.10.05 (drafted 2026.10.03, after G9)" (decisions/README.md:60-62) with no marking. Their status lines read "confirmation required (ADR-0029 C4; C2 for §3)", "confirmation required (ADR-0029 C4, C3)" and "confirmation required (ADR-0029 C4; C2 for §5)" (decisions/ADR-0047.md:19, decisions/ADR-0048.md:15, decisions/ADR-0049.md:15), and G11 counts all three in the 27 (checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:50). ADR-0029's row omits its marking too (B-3).
- Fix belongs in: decisions/README.md
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/README.md:3-4, 12, 42, 60-62, 69-81 (thirteen rows, ADR-0056 to ADR-0068, each 'after G11'); decisions/ADR-0047.md:19; decisions/ADR-0048.md:15; decisions/ADR-0049.md:15; checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:50

### B-20: `spec/README.md` still calls ADR-0026 A2 and ADR-0013 A1 pending and ADR-0052 Proposed
- Against: spec/README.md:27, spec/README.md:28, spec/README.md:139, spec/README.md:140 (and decisions/ADR-0026.md:13, decisions/ADR-0052.md:18)
- Basis: living document
- Claim: "| `BreakGlass_A1.tla` | ADR-0029 §5; ADR-0026 A2 (pending); ADR-0052 §9 (Proposed). Successor to `BreakGlass.tla` where it models X1 |" with last column "none yet", and "| `NonComposition_A1.tla` | ADR-0013 §4, A1 (pending); ADR-0052 §9 (Proposed)."
- Why wrong: ADR-0026 A2 was "ratified 2026.10.05 (Batch 34) and applied inline" (decisions/ADR-0026.md:13). ADR-0052 is "Accepted (genesis) · provisional · 2026.10.05" (decisions/ADR-0052.md:18) and was ratified with "its eight dependent amendments", ADR-0013 A1 among them (decisions/ADR-0052.md:341). The last column says "none yet" although ADR-0026 §2, in force, cites `spec/BreakGlass_A1.tla` (decisions/ADR-0026.md:57-58) and ADR-0052 §9 cites it by digest (decisions/ADR-0052.md:204).
- Fix belongs in: spec/README.md
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no. G11 item 90 covers the binding table and `RulesFloorBase.tla`, not these rows.
- **Verifier:** confirmed with correction
- **Verifier's correction:** Scope. The same stale label stands on eight more rows of the two tables: ADR-0052 '(Proposed)' at spec/README.md:26 and :138, ADR-0048 at :29 and :142, ADR-0050 at :30 and :143, ADR-0047 at :32 and :141. All four records were ratified in Batch 34 (decisions/ADR-0047.md:19, decisions/ADR-0048.md:15, decisions/ADR-0050.md:20, decisions/ADR-0052.md:18). The four rows named are as quoted.
- **Verifier's evidence:** `grep -n '(Proposed)\|(pending)' spec/README.md`; spec/README.md:11 (the last column is 'Cited by digest in'), 27-28, 139-140; decisions/ADR-0026.md:13, 57-58; decisions/ADR-0052.md:18, 204, 341; decisions/ADR-0013.md:8

### B-21: Proposed overlay records exempt themselves from C3 "while this is an overlay", a condition ADR-0029 §4 does not have
- Against: decisions/ADR-0059.md:15 (and decisions/ADR-0060.md:14, decisions/ADR-0061.md:13, decisions/ADR-0062.md:14, decisions/ADR-0065.md:15, decisions/ADR-0066.md:13, decisions/ADR-0067.md:14, decisions/ADR-0068.md:16; decisions/ADR-0029.md:62)
- Basis: Proposed
- Claim: "**C3** does not apply while this is an overlay ⟨Q11⟩ and would apply on admission to the archetype; §8 lists the accepted text it would reverse."
- Why wrong: §4's rule is "On ratification, a record is marked confirmation-required if it meets **any** of these", with "**C3** Supersedes, or reverses in effect, an accepted record" (decisions/ADR-0029.md:62, 68). It has no overlay case, and "overlay" is defined only by ADR-0058, itself Proposed: "Under ADR-0058 (Proposed) a deployment adds the nodes this record describes" (decisions/ADR-0059.md:19). Each status note concedes the reversal and names the accepted text: "§2 gives up ADR-0015's ordered admit before every effect" (decisions/ADR-0062.md:15); "§3 strains ADR-0024's constant that a timeout is never a grant" (decisions/ADR-0061.md:14). A deployment that adopts a ratified overlay runs the reversal in effect, which is C3's wording. The carve-out rests on a rule that is not in force and is written as each record's status.
- Fix belongs in: decisions/ADR-0029.md §4 if overlays are to be a case, or the status notes of ADR-0059 to ADR-0068
- Severity: Low-Medium
- Confidence: medium
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0059.md:15-16, 19; decisions/ADR-0060.md:14; decisions/ADR-0061.md:13-14; decisions/ADR-0062.md:14-16; decisions/ADR-0065.md:14-15; decisions/ADR-0066.md:12-13; decisions/ADR-0067.md:13-14; decisions/ADR-0068.md:15-16; decisions/ADR-0029.md:62-69; `grep -n -i overlay decisions/ADR-0029.md decisions/ADR-0023.md` returns nothing; decisions/ADR-0058.md:11 (Proposed), 50-53 (where an overlay is defined)

### B-22: ADR-0066, a Proposed record, is given the status word "provisional", which ADR-0029 §3 defines only for a ratified record
- Against: decisions/ADR-0066.md:15 and decisions/README.md:79 (and decisions/ADR-0029.md:58)
- Basis: Proposed
- Claim: "It is provisional while ADR-0052 is, whose activation it reuses." (the sentence runs over decisions/ADR-0066.md:14-15) and, in the index, "confirmation required: C1; provisional while ADR-0052 is"
- Why wrong: §3: "**Accepted (genesis) · provisional** | Ratified by the custodian, in force, and **subject to redesign**. The record did not meet its own ratification condition, and says on its face what it lacked" (decisions/ADR-0029.md:58). A Proposed record is neither ratified nor in force, and §3 has no rule by which a record becomes provisional through a dependency; A4's only dependency rule is for amendments landing in the bootstrap set (decisions/ADR-0029.md:80-84). The glossary warns that the word is reserved: "Not the same word as a *provisional* record" (narrative/glossary.md:443-444).
- Fix belongs in: decisions/ADR-0066.md Status note; decisions/README.md:79
- Severity: Low
- Confidence: medium
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0066.md:11, 14-15; decisions/README.md:79; decisions/ADR-0029.md:58, 80-84; narrative/glossary.md:441-444

### B-23: ADR-0024 "narrows" ADR-0014, which has no file and which the index reserves for a different question
- Against: decisions/ADR-0024.md:14 (and decisions/README.md:27)
- Basis: in force
- Claim: "**Narrows:** ADR-0014, to proposal eligibility"
- Why wrong: The index has "| ADR-0014 | : | Reserved, no file (the per-class floor question) | |" (decisions/README.md:27), and ADR-0041 says "ADR-0014, reserved (one floor or one per class)" (decisions/ADR-0041.md:28). G1 gave the number to "Floor authorship and change control" (checkpoints/topak-genesis-checkpoint-G1-2026.09.15.md:63), which is what "proposal eligibility" narrows. The header field points at a record that does not exist, under a subject the current index does not give it.
- Fix belongs in: decisions/ADR-0024.md header, or decisions/README.md:27
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: G11 item 9 names per-class floors (ADR-0014). The conflict of subjects is not listed.
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0024.md:14, 323; decisions/README.md:27; decisions/ADR-0041.md:28; checkpoints/topak-genesis-checkpoint-G1-2026.09.15.md:63, 257 ('0014 floor authorship, narrowed to proposal eligibility'); `ls decisions` shows no ADR-0014.md

### B-24: ADR-0025's decomposition note says four clauses moved out and tabulates five rows
- Against: decisions/ADR-0025.md:19
- Basis: in force
- Claim: "Revision 2 bundled eight clauses. Four were independently supersedable and moved out:"
- Why wrong: The table that follows has five rows (decisions/ADR-0025.md:24-28): evictability test; rules floor; genesis rules resident; issuance ordering and non-erasure; archetype dominance rule and non-increasing TCB. Two of the rows name two clauses each, so six or seven moved, and two remain (§1, §2); no reading gives eight with four moved.
- Fix belongs in: decisions/ADR-0025.md
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0025.md:19-30 (five table rows at 24-28, two of them naming two clauses; 'either half' at 30), 58, 90 (two decision sections remain)

### B-25: History rows of ratified amendments still say "Pending" or "Marked inline and not applied"
- Against: decisions/ADR-0025.md:230 (and decisions/ADR-0024.md:325, decisions/ADR-0025.md:258, decisions/ADR-0025.md:260, decisions/ADR-0026.md:343, decisions/ADR-0029.md:274)
- Basis: in force
- Claim: "**Pending** : drafted 2026.09.30." (ADR-0025 A1, State column) and "Marked inline and not applied" (the Change column of ADR-0024 A3, ADR-0025 A2 and A3, ADR-0026 A2, ADR-0029 A3)
- Why wrong: ADR-0025 A1 was "**A1 ratified 2026.09.30** by the genesis custodian (ADR-0029 §2), in Batch 17" (decisions/ADR-0025.md:231), and the header says "A1 ratified 2026.09.30 (Batch 17)" (decisions/ADR-0025.md:11); its own row's State was never moved, unlike the Batch 34 rows, whose State reads "**Applied** ⟨B34⟩". Those five rows in turn keep "Marked inline and not applied" and "Takes force only with ADR-0050's ratification" beside "Applied".
- Fix belongs in: the named History rows
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed with correction
- **Verifier's correction:** Scope. ADR-0025 A1 is not the only ratified amendment whose own row still reads 'Pending': the same holds at decisions/ADR-0003.md:83 (A3, ratified in Batch 17 per :12) and decisions/ADR-0034.md:501 (A1, ratified in Batch 17 per :16), and decisions/ADR-0031.md:399 and decisions/ADR-0039.md:418 read the same against headers that give them as ratified. 'Marked inline and not applied' stands beside '**Applied**' in 33 rows of 19 records, not five rows (`grep -n 'Marked inline and not applied' decisions/*.md | grep -c '\*\*Applied\*\*'`). The rows named are as quoted.
- **Verifier's evidence:** decisions/ADR-0025.md:11, 230-231, 258, 260; decisions/ADR-0024.md:325; decisions/ADR-0026.md:343; decisions/ADR-0029.md:274; `grep -n '\*\*Pending\*\* —' decisions/*.md`

### B-26: ADR-0028's bootstrap note says erasure is disabled until two records are ratified, and two paragraphs later that ratifying them does not enable it
- Against: decisions/ADR-0028.md:114 (and decisions/ADR-0028.md:122)
- Basis: in force
- Claim: "Erasure is therefore disabled from epoch 0 until this record and ADR-0013 are ratified."
- Why wrong: "**Ratifying them does not by itself enable erasure** ⟨R3⟩. The genesis rules issue no erasure roster because ADR-0029 §5, ceremony step 5, says so" (decisions/ADR-0028.md:122-123). Both records were ratified on 2026.09.23 (decisions/ADR-0028.md:150), before any epoch 0, so the first sentence's condition is already met and the state it implies does not follow.
- Fix belongs in: decisions/ADR-0028.md, Bootstrap note
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0028.md:114-116, 122-127, 150, 154 (R3 rewrote the note and left the first sentence); decisions/ADR-0013.md:8 (2026.09.23); decisions/ADR-0029.md:123

### B-27: ADR-0028 says NC-2 is checked against the class list in §1; the module carries three of the six classes
- Against: decisions/ADR-0028.md:10 (and spec/NonComposition.tla:22)
- Basis: evidence
- Claim: "NC-2 (ADR-0013 §4) is checked against the class list in §1."
- Why wrong: "The ADR-0028 classes this model carries. F1 admit decisions, F5 break-glass invocations, F6 erasure events. F2, F3 and F4 have the same shape as F5 here and are omitted to keep the state space small." with `ForensicKinds == {"F1", "F5", "F6"}` (spec/NonComposition.tla:22-25). ADR-0013 says so: "NC-2 is checked against a three-class model of its class list" (decisions/ADR-0013.md:189). ADR-0028, the record that owns the list, does not, and it has no dependent entry for the 2026.10.02 proof as ADR-0013, ADR-0026 and ADR-0029 have. The policy side does carry all six (floor/genesis-floor.cedar:186-188).
- Fix belongs in: decisions/ADR-0028.md Status note
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no (acknowledged in ADR-0013 only)
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0028.md:8-10, 53-58 (six classes, F1 to F6); spec/NonComposition.tla:22-25; decisions/ADR-0013.md:188-190, 223; floor/genesis-floor.cedar:186-188; `grep -n 'B25\|three-class\|NonComposition' decisions/ADR-0028.md` returns nothing

### B-28: Two B25 rows say a TLAPS result was "checked by" the prover row, using the word the corpus keeps for TLC
- Against: decisions/ADR-0026.md:289 and decisions/ADR-0029.md:260
- Basis: evidence
- Claim: "262 obligations, results `spec/RulesFloorNV_rev5-proof-results-2026.10.02.txt` (`131804673137f4fd`), checked by T-0045-31 (ADR-0046)." and "results `spec/Anchor-proof-results-2026.10.02.txt` (`ccb1f3526acb951e`) and `spec/BreakGlass-proof-results-2026.10.02.txt` (`c40000dd946541b0`), checked by T-0045-31 (ADR-0046)."
- Why wrong: T-0045-31 is the prover: "`tlapm` 7824dab, T-0045-31" (checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:12). The corpus keeps *checked* for TLC and *proved* for TLAPS, and both rows use "proved" correctly a sentence earlier. For `RulesFloorNV_rev5` the looser word sits beside a difference that matters: that proof does not certify, "NOT CERTIFIED: Isabelle rejected 1 of Zenon's proofs." (spec/RulesFloorNV_rev5-proof-cert-results-2026.10.04.txt:14). Everything else in the two rows holds: I recomputed the six digests with `sha256sum` and they match, and the results files report 262, 40 and 37 obligations.
- Fix belongs in: the two B25 rows
- Severity: Low
- Confidence: medium
- Already on the corpus's own lists: no
- **Verifier:** confirmed with correction
- **Verifier's correction:** Scope. 'checked by T-0045-31' stands in twelve B25 rows, not two: `grep -rn 'checked by T-0045-31' decisions` returns ADR-0013:223, 0026:289, 0029:260, 0030:535, 0031:402, 0034:505, 0037:496, 0038:278, 0039:429, 0041:313, 0042:332, 0043:266. The word rule the finding relies on is in force and should be cited: 'The word **proved** is henceforth used in the corpus only of a claim the second method has discharged ... **Checked** is used of the first' (decisions/ADR-0046.md:90-91; narrative/glossary.md:1214-1217). The two rows quoted are exact.
- **Verifier's evidence:** decisions/ADR-0026.md:289; decisions/ADR-0029.md:260; decisions/ADR-0046.md:90-91; spec/RulesFloorNV_rev5-proof-cert-results-2026.10.04.txt:10, 14; `sha256sum` of spec/RulesFloorNV_rev5_proof.tla, spec/Anchor_proof.tla, spec/BreakGlass_proof.tla and their three 2026.10.02 results files matches the six prefixes in the rows; the results files report 'All 262 / 40 / 37 obligations proved'

### B-29: ADR-0024 §2 and ADR-0026 §2 cite the 2026.09.15 check for R9's vacuity; that check had no R9
- Against: decisions/ADR-0024.md:68 and decisions/ADR-0026.md:68
- Basis: evidence
- Claim: "ADR-0026 R1, R2 and R9 vacuous (non-vacuity check, 09.15)." and "If the mechanism hard-codes these values, R1, R2 and R9 constrain nothing and are vacuous (§6)."
- Why wrong: §6's own note: "no column covers R9, which did not exist" (decisions/ADR-0026.md:207). The 09.15 results file has rows for R1 to R5 and R7 only (spec/RulesFloorNV-results-2026.09.15.txt:1-26), and the finding it supports is "**R1–R3 are vacuous against ADR-0024 as written.**" (decisions/ADR-0026.md:178). R9 was added by revision R1 on 2026.09.23 (decisions/ADR-0026.md:286).
- Fix belongs in: decisions/ADR-0024.md §2; decisions/ADR-0026.md §2
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0024.md:67-68; decisions/ADR-0026.md:68-69, 178, 206-207, 286; spec/RulesFloorNV-results-2026.09.15.txt:1-26 (rows for R1, R2, R3, R4, R5 and R7 only)

### B-30: ADR-0026 §6's "superseded in part" note is itself stale in two places
- Against: decisions/ADR-0026.md:208 and decisions/ADR-0026.md:209
- Basis: in force
- Claim: "(S6-10, open)" and "The `rev5` rerun in Open obligations replaces this section when it is run."
- Why wrong: R2, the same day, records S6-10 as dispositioned: "resolving the four-versus-five conflict with ADR-0029" with source "Narrative log 09.15, S6-10; disposition taken 2026.09.23" (decisions/ADR-0026.md:287). The rerun was run and did not replace §6: "§6 stays as the record of the 09.15 run" (decisions/ADR-0026.md:217) and "§6 is not struck" (decisions/ADR-0026.md:318). The one-key-holder point the note raises is, however, still true of §7's model and is not repeated there (B-14).
- Fix belongs in: decisions/ADR-0026.md §6
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0026.md:208-209, 216-217, 287, 318

### B-31: ADR-0026 §3 gives "admits a roster of none" as the mark of a vacuous floor; the ratified floor admits one
- Against: decisions/ADR-0026.md:74 (and spec/bootstrap-results-2026.09.23.txt:31)
- Basis: evidence
- Claim: "A vacuous rules floor admits a roster of none."
- Why wrong: In the `anchor-reach` row, with `Mut=none` and `Active={"R1","R2","R5","R6","R7","R9"}`, the issuance at epoch 1 is `rules = [ grant |-> {}, quorum |-> [mode |-> "all", k |-> 0], minGrant |-> 2, bgScope |-> {}, exceptions |-> 0 ]` (spec/bootstrap-results-2026.09.23.txt:17, 30-35). R2 bounds `minGrant` and not the roster (spec/RulesFloorBase.tla:42), so the full floor admits an empty roster; what it prevents is a promotion on one. §6 finding 3's "R1 alone does not protect against an empty roster; R2 is what does" (decisions/ADR-0026.md:187-188) overstates in the same way.
- Fix belongs in: decisions/ADR-0026.md §3 and §6 finding 3 (wording)
- Severity: Low
- Confidence: medium
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0026.md:74-75, 185-188; spec/bootstrap-results-2026.09.23.txt:17, 29-35 (full floor, `grant |-> {}` issued at epoch 1); spec/RulesFloorBase.tla:42-43

### B-32: G11 §8 says "No floor is ratified" under a §2 headed "The floors as ratified" whose first subsection is the ratified rules floor
- Against: checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:378 (and checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:94, decisions/ADR-0026.md:124)
- Basis: in force
- Claim: "**No floor is ratified.** A floor stated in Lean is not a floor found fit."
- Why wrong: G11 §2 is "## 2. The floors as ratified" with "### 2.1 The rules floor" (checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:94-96), and ADR-0026 records "The genesis rules floor is now **R1, R2, R5, R6, R7, R9**" by ratification (decisions/ADR-0026.md:123-124, with its B2 and B4 rows at 283-284). The sentence is true of the policy floor's text only (decisions/ADR-0029.md:124-125). ADR-0067 already reuses it unqualified as a premise: "**No floor is ratified, so nothing here can be in force**" (decisions/ADR-0067.md:14).
- Fix belongs in: the next checkpoint's §8; G11 is frozen, so an erratum row in checkpoints/README.md
- Severity: Low
- Confidence: medium
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:94-96, 103-106, 378; decisions/ADR-0026.md:123-124, 283-284; decisions/ADR-0029.md:124-127; decisions/ADR-0067.md:14, 109; the same four words recur at checkpoints/topak-genesis-checkpoint-G10-2026.10.05.md:390 and REVIEWERS_GUIDE_README.md:45, each followed by text about the policy floor only

### B-33: ADR-0054 names ADR-0024 A3 as the amendment that makes a workflow "a set of seatings and a graph"; in ADR-0024 that is A4
- Against: decisions/ADR-0054.md:41 (and decisions/ADR-0024.md:327, decisions/ADR-0024.md:325)
- Basis: Proposed
- Claim: "**Carries a debt against:** ADR-0024 A3 (a workflow is a set of seatings and a graph, §2)"
- Why wrong: ADR-0024's rows are "| A3 | Amendment (dependent) | **A promotion seats.**" (decisions/ADR-0024.md:325) and "| A4 | Amendment (dependent) | **A workflow is a set of seatings and a graph.**" (decisions/ADR-0024.md:327). ADR-0054's own ratification condition corrects itself further down, "drafted 2026.10.08 as ADR-0015 A1, ADR-0024 A4" (decisions/ADR-0054.md:301), so its header and the first sentence of that condition (decisions/ADR-0054.md:296) disagree with the record they cite. The content of ADR-0024's pending A4 does match ADR-0054 §2 (decisions/ADR-0054.md:102-116).
- Fix belongs in: decisions/ADR-0054.md header and §12
- Severity: Low
- Confidence: medium
- Already on the corpus's own lists: no
- **Verifier:** confirmed with correction
- **Verifier's correction:** Scope. The same two places carry a second wrong number: 'ADR-0031 A3 (a third grant path, §2)' at decisions/ADR-0054.md:41-42 and 'ADR-0031 A3 (the third grant path)' at :296. ADR-0031's third grant path is A4 (decisions/ADR-0031.md:424); its A3 is 'Who grants, and who denies' (:422). Line 301 has both right, 'ADR-0024 A4, ADR-0031 A4'. The 'ADR-0024 A3' at :305 is correct, since it means the promotion that seats.
- **Verifier's evidence:** decisions/ADR-0054.md:41-42, 296, 301, 305; decisions/ADR-0024.md:325, 327; decisions/ADR-0031.md:422, 424

### B-34: ADR-0025 still carries the corpus's custody row as an open obligation; ADR-0029 §1 declared it
- Against: decisions/ADR-0025.md:142 (and decisions/ADR-0029.md:39)
- Basis: in force
- Claim: "**A custody row for the ADR corpus itself.** Currently (1, 0), from solo authorship."
- Why wrong: "Genesis custody is declared: **Scott, sole custodian, (1, 0).** This is genesis custody, not a degeneracy." (decisions/ADR-0029.md:39-40). ADR-0029 was accepted on 2026.09.15, and ADR-0025 was revised and ratified on 2026.09.23 with "every consequence and open obligation" unchanged (decisions/ADR-0025.md:244-245). ADR-0025's axis table also files ": (single custodian) | (1, 0)" beside the degeneracies (decisions/ADR-0025.md:215), the reading ADR-0029's Context calls wrong (decisions/ADR-0029.md:20-22).
- Fix belongs in: decisions/ADR-0025.md, Open obligations
- Severity: Low
- Confidence: medium
- Already on the corpus's own lists: no. G11 item 11 ("Custody beyond (1, 0)") is a different matter.
- **Verifier:** confirmed with correction
- **Verifier's correction:** The other side is wider than ADR-0029 §1. ADR-0045 says 'The custody row for the corpus itself, which G4 item 38 asked for, is T-0045-11' (decisions/ADR-0045.md:220-221), its header claims to close that row 'in part' (:41), and T-0045-11 is 'The corpus and its custodian, custody (1, 0)' (:368). So the row is declared by ADR-0029 §1 and supplied in part by ADR-0045, and decisions/ADR-0025.md:142 records neither. 'In part' means the bullet is unannotated, not wholly discharged.
- **Verifier's evidence:** decisions/ADR-0025.md:142, 215, 244-245; decisions/ADR-0029.md:8, 20-22, 39-40; decisions/ADR-0045.md:41, 220-221, 368

### B-35: Every ratification row cites a numbered batch, and the record that defines the process does not define one
- Against: decisions/ADR-0029.md:44 (and narrative/glossary.md:1176)
- Basis: in force
- Claim: "During genesis, the custodian may ratify any record that has decision text, at their discretion and at any time."
- Why wrong: Command: `grep -n -i 'batch' decisions/ADR-0029.md` returns only the Pending line and four History rows (lines 10, 259, 274, 275, 276). ADR-0029 says who ratifies and not what a batch is, how it is numbered, what "ratified with" or "in the same batch" binds, or where the register of batches is kept, although A4 leans on it: dependent amendments "are ratified with the record they depend on" (decisions/ADR-0029.md:80-81). The only definition is a checkpoint convention in the glossary, "**Batch** [C]: a ratification group. There are thirty-seven" (narrative/glossary.md:1176), and its count is two behind (B-6).
- Fix belongs in: decisions/ADR-0029.md §2
- Severity: Low
- Confidence: medium
- Already on the corpus's own lists: no
- **Verifier:** confirmed with correction
- **Verifier's correction:** 'Every ratification row cites a numbered batch' is too wide. Early rows cite none: ADR-0029 A1, 'ratified 2026.09.23, with the ADR-0024 revision 5' (decisions/ADR-0029.md:256); ADR-0029 A2, 'ratified 2026.09.25 by the genesis custodian' (:257); ADR-0024 A1, 'ratified 2026.09.23, with ADR-0032' (decisions/ADR-0024.md:289). The absence in ADR-0029 is real and the command reproduces.
- **Verifier's evidence:** `grep -n -i batch decisions/ADR-0029.md` rerun: lines 10, 259, 274, 275, 276; decisions/ADR-0029.md:44-46, 80-81; narrative/glossary.md:1176-1177 (the only definition found)

