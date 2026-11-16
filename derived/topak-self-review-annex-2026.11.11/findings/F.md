# Self review of 2026.11.11: reader F's findings in full

Reader F read labels, tools, the operator and the emergency seating. Annex to `derived/topak-open-findings-register-2026.11.11.md`, Part III. Each block is the finding as the reader wrote it, against the tree at `bbda621`, followed by the verdict of a verifier that did not find it. Paths are relative to the repository root. A path a finding names as absent is written without backticks. Nothing here is ratified, and every reader and verifier is of the same model lineage as the drafter of the corpus.

48 reported: 42 confirmed, 5 confirmed with a correction, 1 dropped.

### F-1: The floor in force permits an operator's `Regrant` and `Renew` of an emergency seat; the one-round rule has no floor entry, no gate and no line in either ratification condition
- Against: decisions/ADR-0052.md:115 (and floor/proposed/emergency-floor.cedar:228 and :240; decisions/ADR-0050.md:176)
- Basis: in force
- Claim: "An operator's `Regrant` or `Renew` naming an emergency seat is refused."
- Why wrong: decisions/ADR-0050.md:176 says "**The floor states the envelope.** The control variants are actions in schema S, and the entries that permit and forbid them are floor entries with the same gates as any other." The floor does not state this refusal. floor/proposed/emergency-floor.cedar:228-238 (`C1-regrant-successor`) permits when `principal.kind == "operator" && resource.domain == principal.domain && context.targetSeated && !context.targetLive && context.sameBinding && context.nextRound && context.lastAlphabet.containsAll(context.newAlphabet)`; :240-246 (`C2-renew`) permits when `principal.kind == "operator" && resource.domain == principal.domain && context.targetLive`. Neither reads the target's kind, and no forbid does. floor/proposed/README.md:99 says "**Emergency** (ADR-0052). No new entry." decisions/ADR-0052.md:180 gives the whole floor condition as "X1 removed, B10 admitting the `emergency` kind for `Actuate`". Of the 107 cases in floor/proposed/emergency-tests.json (names listed with `python3`), none has an emergency seat as the resource of a `Regrant` or `Renew`. The refusal exists only as reference code: mechanism/GAPS-AND-ASSUMPTIONS.md:107 "An operator's `Regrant` or `Renew` naming it is refused". spec/Emergency.tla carries it only as the mutations `M_REGRANT` and `M_RENEW` (lines 41 to 45), and decisions/ADR-0050.md:419 says "`spec/Operators.tla` does not model it".
- Fix belongs in: decisions/ADR-0041.md (a control entry, or a sentence that this refusal is a mechanism check and not floor material), decisions/ADR-0052.md §3 and §9, floor/proposed/build.py
- Severity: Medium-High
- Confidence: medium
- Already on the corpus's own lists: no
- **Verifier:** confirmed with correction; severity Medium (reader: Medium-High)
- **Verifier's correction:** Scope of the title. 'No line in either ratification condition' is wrong: ADR-0052 §9 carries the one-round rule twice, as the module property `EmergencyLeaseIsOneRound` (no successor, no renewal) with the mutation 'a regrant of an emergency seat' (ADR-0052:199-201), and as a reference behaviour, 'a `Regrant` of the emergency seat refused', seen at R6 by ADR-0033 A12 (ADR-0052:222-225). What is absent is any floor entry, gate candidate or case, and any line in the floor condition of either record (ADR-0052:180; ADR-0050:250-255). 'Permits' should read 'does not refuse': C1 and C2 are satisfied by a target of kind `emergency` whenever the lifted facts hold, and no entry and no `ControlCtx` fact reads the target's kind; the reference refuses in `State::control_facts`, before the floor is asked. The module does state the property (Emergency.tla:185); the refusal itself is modelled only as the absence of an operator action outside `M_REGRANT` and `M_RENEW`. Severity lowered because the rule is held at the reference and in the module; the disagreement is between the records ('the floor states the envelope') and the floor.
- **Verifier's evidence:** floor/proposed/emergency-floor.cedar:228-246 and :266-292 (C1, C2, C5 to C9 read in full; none tests the target's kind); `grep -rn 'resource.kind' floor --include=*.cedar` empty; floor/proposed/emergency.cedarschema:20-23, :104-118, :141-142 (Seat.kind includes `emergency`; thirteen ControlCtx facts, none on the target's kind; Regrant and Renew take a Seat as resource); floor/proposed/emergency-tests.json, 107 cases enumerated with python3: the 19 Regrant and Renew cases name r1, a1, ro1, op1 or op2 as resource, never e1; workflow-tests.json likewise (19 such cases, none on an emergency seat); floor/proposed/emergency-gates-results-2026.10.04.txt:123-133 (the eleven routing candidates of the stage, listed with `grep -n 'relax:\|tighten:'`: none drops or adds a test of the target's kind on Regrant or Renew); spec/Emergency.tla:124-134, :185; spec/Emergency_proof.tla:395-396; mechanism/crates/topak-core/src/state.rs:1355-1360; decisions/ADR-0052.md:115-116, :180, :199-201, :222-225; decisions/ADR-0050.md:110-112, :176-178, :250-255; floor/proposed/README.md:99; mechanism/GAPS-AND-ASSUMPTIONS.md:107

### F-2: `NoAgentHoldsAnEmergencySeat` holds because the model's activation guard reads the ghost distinction the record says the mechanism cannot see
- Against: decisions/ADR-0052.md:199 (and spec/Emergency.tla:110)
- Basis: evidence
- Claim: "`NoAgentHoldsAnEmergencySeat` over ghost truth" (line 188 counts it among "six properties hold"; line 191 has it "**Proved**")
- Why wrong: decisions/ADR-0052.md:65 says "The mechanism cannot tell a person from a program holding the person's key; this is a rule about what is seated". spec/Emergency.tla:9 calls the person-or-agent fact "ghost state the mechanism never reads". But the mechanism action `Activate` is guarded by it, spec/Emergency.tla:110: `/\ h \in (IF Mut = "M_AGENT" THEN Holders ELSE Persons)`. Under `Mut = "none"` no agent can be activated, so the invariant at line 187 is true by construction. The one mutation that breaks it (row `agent3` of spec/Emergency-results-2026.10.04.txt) is the removal of that guard. spec/Operators.tla:39-41 declares its equivalent ("the identity provider is honest") as a premise "not modelled"; `Emergency.tla` declares no such premise, and ADR-0052 §9's "Outside it" list (lines 195 to 197) does not name it.
- Fix belongs in: decisions/ADR-0052.md §9 (say it is a declared premise, as ADR-0050 §8 does of operators); a successor header for spec/Emergency.tla
- Severity: Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** spec/Emergency.tla:8-10 (header: ghost state the mechanism never reads), :46-47, :107-110 (Activate is guarded by `h \in (IF Mut = 'M_AGENT' THEN Holders ELSE Persons)`), :187 (`em.live => em.holder \in Persons`); `grep -n -i premise spec/Emergency.tla` empty; spec/Emergency_proof.tla:315-317 (the theorem's only hypothesis is Mut # M_AGENT); spec/Emergency-results-2026.10.04.txt:656-657 (agent3 is the one violated row for this invariant, 51 rows counted); spec/Operators.tla:9-12, :39-41; decisions/ADR-0052.md:65-66, :188-191, :195-197, :199-200 (the quoted phrase runs over 199-200)

### F-3: ADR-0047 §8 says no promotion sees the task's label and the operator channel is untyped; ADR-0050 §5, ratified in the same batch, types the channel and has a promoted seating bound the label
- Against: decisions/ADR-0047.md:331 (and decisions/ADR-0050.md:187)
- Basis: in force
- Claim: "It is set by whoever issues the grant, on the operator channel, which the corpus does not type (CR-34). No promotion and no anchor sees it."
- Why wrong: decisions/ADR-0050.md:185 "**The label is the operator's signed declaration.** ADR-0047 §1 requires it to be present. It is now attributed to a principal, where it was a field on an unauthenticated request." decisions/ADR-0050.md:187 "**The seating bounds it** *(drafter's choice)*. A seating names the labels a task for that principal may carry. A `Regrant` whose task label is outside them is refused." decisions/ADR-0050.md:218 "| Who is an operator; a seating; the labels a seat's tasks may carry | A promotion |". decisions/ADR-0050.md:35 closes CR-34 on ratification. ADR-0047's own §11 (line 402) relies on `C8`. decisions/ADR-0045.md:416 (T-0045-33) repeats the older sentence: "on a channel with no signature and no promotion (CR-34)".
- Fix belongs in: decisions/ADR-0047.md §8; decisions/ADR-0045.md T-0045-33
- Severity: Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0047.md:331-335 (quote exact, over 331-332), :401-402 (C8), :535-537 and :573 (R11 is a pointer, 'No decision text changes'; no later row touches §8); decisions/ADR-0050.md:35, :185-189, :218; decisions/ADR-0045.md:416

### F-4: The checkpoint's exits from provisional are wider than the exits the two records state
- Against: checkpoints/topak-genesis-checkpoint-G10-2026.10.05.md:365 and :369, carried unchanged by checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:82 (and decisions/ADR-0050.md:298; decisions/ADR-0052.md:236)
- Basis: in force
- Claim: "**The exit from provisional for ADR-0050**: a first lease from a completed tally, with a promoted seating; the first operators seated by an anchor issuance; a `Regrant` at rung 1 or above, which has to launch a guest; an operator's Persona record and lineage; a review"
- Why wrong: decisions/ADR-0050.md:298-305 "Two things kept it from meeting this section as first written, and they are the debt its provisional status carries: ... It stops being provisional when both are met and the custodian records it." The two are a first lease from a quorum and a reader. The checkpoint's own §1.2 (G10:78) gives the same two: "ADR-0050: a first lease from a quorum is not built, and no reader other than the drafter has reviewed it." Item 88 adds a rung-1 `Regrant` and the Persona record and lineage. Likewise decisions/ADR-0052.md:236 "It stops being provisional when ADR-0050 does, the seating is prepared by promotion at the reference, the two questions are answered here, and a reader has reviewed it", where item 92 (G10:369) adds "a socket path for a person's signed action; something that counts the drill". narrative/theory-of-operation.md:35-36 follows the record ("It stops being provisional when both are met"). decisions/ADR-0029.md:58 requires that a provisional record "says on its face what it lacked: that is the debt the mark carries", so the record's list is meant to be the list.
- Fix belongs in: the next checkpoint's open list (items 88 and 92), or decisions/ADR-0050.md §10 and decisions/ADR-0052.md §9
- Severity: Medium
- Confidence: high
- Already on the corpus's own lists: G11 items 88 and 92 are one side of the disagreement; the disagreement itself is not listed
- **Verifier:** confirmed
- **Verifier's evidence:** checkpoints/topak-genesis-checkpoint-G10-2026.10.05.md:365, :369, :77-81; checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:82 (G11 restates neither item); decisions/ADR-0050.md:297-305; decisions/ADR-0052.md:226-238; decisions/ADR-0029.md:58; narrative/theory-of-operation.md:33-36; mechanism/GAPS-AND-ASSUMPTIONS.md:106 and :107 keep 'The exit from provisional' apart from 'Not built', which item 88 and item 92 merge

### F-5: `floor/proposed/README.md` presents the stages as a draft of records not yet in force; the checkpoint says the `emergency` stage is the floor in force
- Against: floor/proposed/README.md:3 and :5 (and checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:105)
- Basis: living document
- Claim: "This directory holds the floor as it would read if the records drafted on 2026.10.03 and 2026.10.04 were in force."
- Why wrong: Those records are in force since Batch 34 (decisions/ADR-0047.md:19, ADR-0050.md:20, ADR-0052.md:18). G11:105 "**The entries in force are G10's**: the `emergency` stage, `floor/proposed/emergency-floor.cedar` (`15c941b9a56a09f7`), 28 policies, 107 cases. The floor is genesis-provisional (ADR-0030 A3)." mechanism/GAPS-AND-ASSUMPTIONS.md:49 "**It is still the floor in force**". The same README at :34 says "`floor/lean` states the floor in force from it". Its headline at :3 is "DRAFT · not ratified", with no word that one stage is enforced and genesis-provisional. decisions/ADR-0052.md:182 still reads "**Met at R4** ⟨R4⟩, as proposed text", and no later row of that record says the stage took force.
- Fix belongs in: floor/proposed/README.md; decisions/ADR-0052.md §9
- Severity: Medium
- Confidence: high
- Already on the corpus's own lists: G11 item 91 covers the stage files' opening comment only, not the README
- **Verifier:** confirmed with correction
- **Verifier's correction:** The headline at :3 does say which stage the reference links (`workflow` since 2026.10.08, `emergency` from 2026.10.05), and :6 says the reference links, pins and replays a stage, so 'no word that one stage is enforced' is too strong. What the README lacks is that the `emergency` stage is the floor in force and genesis-provisional (ADR-0030 A3); :5 still words the directory as the text of records not in force. 'Not ratified' remains true of the floor text itself. The rest stands.
- **Verifier's evidence:** floor/proposed/README.md:3, :5-10, :34, :80-81; checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:105-106; mechanism/GAPS-AND-ASSUMPTIONS.md:49; decisions/ADR-0052.md:182 and History rows R5, R6, B34 (:339-341), none of which says the stage took force

### F-6: ADR-0041's own tables still mark X1's retirement and the label and control entries as pending and not applied
- Against: decisions/ADR-0041.md:62 (and :74, :83; decisions/ADR-0052.md:237)
- Basis: in force
- Claim: "`X1-break-glass` *(pending ⟨A2⟩, not applied: retired)*"
- Why wrong: decisions/ADR-0041.md:20 says A2 was "ratified 2026.10.05 (Batch 34) and applied inline ⟨B34⟩". decisions/ADR-0052.md:237 "**X1's retirement is in force on that basis**". checkpoints/topak-genesis-checkpoint-G10-2026.10.05.md:85-86 says the dependent amendments "were applied by removing the pending mark". The marks were not removed here: line 62 as quoted, line 74 "| Id ⟨A1, pending⟩ | Kind | Action | Holds when | From |" over `R5` to `R7`, and line 83 "| Id ⟨A3, pending⟩ | Kind | Action | Holds when | From |" over `C1` to `C9`. This is the record ADR-0047 §7, ADR-0050 §10 and ADR-0052 §2 cite for the floor's entries, and a reader of its §1 cannot tell which are in force.
- Fix belongs in: decisions/ADR-0041.md §1 (an erratum)
- Severity: Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0041.md:19-21, :62, :74, :83 (`grep -n pending`); the paragraphs at :67 and :80 carry ⟨A1⟩ ⟨B34⟩ and ⟨A3⟩ ⟨B34⟩ while the tables under them keep the pending mark; checkpoints/topak-genesis-checkpoint-G10-2026.10.05.md:85-87; decisions/ADR-0052.md:237

### F-7: Three artifacts give three mappings from F4 to F6 to the load checks, and the root's missing label has no check at all in "the definitive form"
- Against: decisions/ADR-0047.md:284 (and decisions/ADR-0049.md:178 and :166; spec/Labels.tla:116)
- Basis: in force
- Claim: "**The definitive form of each check is ADR-0049 §6** (W7 to W9)"
- Why wrong: F6 (decisions/ADR-0047.md:291) is "A root or an entry declares no label (§1), or an outward entry declares no destination inputs and takes any". decisions/ADR-0049.md:166 gives the entry's missing label to W6, whose own source column is "ADR-0047 §1, F6", so that half of F6 is outside "W7 to W9". No row W1 to W10 refuses a root that declares no label or a delivery table that is not total: decisions/ADR-0049.md:183-190 names `labels.root` and `labels.delivery` "without deciding their content", while decisions/ADR-0047.md:109 says "A bundle in which a root or an allowlist entry declares no label is not well-formed and does not load" and decisions/ADR-0030.md:181-182 says "The checks are ADR-0049 §6's W1 to W10". spec/Labels.tla:116 reads "F4 to F6 (ADR-0049 §6, W6 to W8)" and models F6 only as `fetchDeclared`; W9 is not in the module. The reference does check the root (decisions/ADR-0033.md:639 "A root with no label, and a delivery table that is not total, do not load"), under no W number.
- Fix belongs in: decisions/ADR-0049.md §6 (a row for the root and the table, or W6 widened), decisions/ADR-0047.md §7 and §8; a successor header for spec/Labels.tla
- Severity: Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0047.md:109-110, :283-285, :291; decisions/ADR-0049.md:159-170 (W1 to W10 read in full: no row refuses a root with no label or a delivery table that is not total), :178-179, :183-190; decisions/ADR-0030.md:181-182; spec/Labels.tla:116-121 (`grep -n 'W[0-9]' spec/Labels.tla` gives :116 only; no destination check); decisions/ADR-0033.md:639; floor/proposed/README.md:121

### F-8: ADR-0048 says a round's tool list is the allowlist of the one granted revision; ADR-0052 makes an emergency round's tool list the entries of every revision in force
- Against: decisions/ADR-0048.md:97 (and decisions/ADR-0052.md:92; spec/ToolList.tla:136)
- Basis: in force
- Claim: "The grant names the bundle revision and the lease's narrowing (ADR-0031 §4). The tool list is the allowlist of that revision, narrowed by that lease."
- Why wrong: decisions/ADR-0052.md:92 "The tool list of the round (ADR-0048 §2) is the envelope", and the default envelope (decisions/ADR-0052.md:83) is "**every Run allowlist entry in force in the domain**: the entries of every bundle revision that a seating in force in the domain names, with no lease's narrowing applied, together with the entries of the emergency seating's own bundle". For an emergency seat the list is therefore not the allowlist of the granted revision, and `ToolListIsExact` (spec/ToolList.tla:136, `lease.live => told = Allow[lease.rev] \cap lease.narrow`) does not describe it. ADR-0052's debt line (lines 33 to 36) and its "Relates to" list do not name ADR-0048. mechanism/GAPS-AND-ASSUMPTIONS.md:107 (b) has "each call decided against the revision that holds its entry", against decisions/ADR-0048.md:113 "the list a Thinker was given is the list its admits are decided against".
- Fix belongs in: decisions/ADR-0048.md §2, or decisions/ADR-0052.md §2 and its debt line
- Severity: Medium
- Confidence: medium
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0048.md:97-99, :113-114; `grep -n -i 'emergency\|ADR-0052' decisions/ADR-0048.md` empty; decisions/ADR-0052.md:82-87, :90-93; `grep -n ADR-0048 decisions/ADR-0052.md` gives :92 only, so the header and debt line (:25-36) do not name it; spec/ToolList.tla:136; mechanism/GAPS-AND-ASSUMPTIONS.md:107 (b)

### F-9: ADR-0047 §1 counts three kinds of ingress and declares a label source for three; ADR-0048 and ADR-0043 A1, ratified with it, make it four, and no record says where the tool list's label is declared
- Against: decisions/ADR-0047.md:82 (and decisions/ADR-0048.md:94; decisions/ADR-0043.md:70; narrative/theory-of-operation.md:504)
- Basis: in force
- Claim: "**Each of the three kinds of ingress has a source on the record, and the source declares the label.**"
- Why wrong: decisions/ADR-0048.md:94 "It is a fourth item of ingress, beside the task, consulted content and tool results". decisions/ADR-0043.md:70 "**Four things, each with a label, and two ways to deliver.**" with "Every item carries a label that is a function of its source". decisions/ADR-0047.md:110 "There is no unlabelled item and no default label at delivery." The table at decisions/ADR-0047.md:84-88 has no row for the tool list, decisions/ADR-0049.md:186-190 names no data for its label, and decisions/ADR-0048.md:119 says only that it "carries neither reserved name". The narrative adds the row the decision lacks, narrative/theory-of-operation.md:504 "| The tool list | The bundle | It passed promotion, and carries neither reserved name |". ADR-0047's Context (line 45) still says the three "and nothing else reaches the Thinker", and its pending A1 (line 90) calls ADR-0054's item the "fifth".
- Fix belongs in: decisions/ADR-0047.md §1 and Context, or decisions/ADR-0048.md §2
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0047.md:44-45, :82-88, :90, :110; decisions/ADR-0048.md:94-95, :119-120; decisions/ADR-0043.md:70-74; decisions/ADR-0049.md:186-190; narrative/theory-of-operation.md:504; a grep across decisions/ for a declared source of the tool list's label finds none

### F-10: ADR-0041 A2 describes the emergency envelope as the allowlist of one bundle revision; ADR-0052 §2 since its R1 computes it across revisions
- Against: decisions/ADR-0041.md:156 (and decisions/ADR-0052.md:83)
- Basis: in force
- Claim: "seats a named person on a seat of kind `emergency` for one round, on a bundle revision whose allowlist is the emergency envelope"
- Why wrong: decisions/ADR-0052.md:82-87: the envelope is "generic by default", "the entries of every bundle revision that a seating in force in the domain names ... together with the entries of the emergency seating's own bundle. The mechanism computes it from the log at the activation's index". A2's sentence matches ADR-0052 before its R1 (decisions/ADR-0052.md:335). A third reading is in ADR-0052's open obligations (lines 319 to 320): "Which revision's bundle-tier policy the emergency lease is decided against is the emergency seating's own", against mechanism/GAPS-AND-ASSUMPTIONS.md:107 "each call decided against the revision that holds its entry".
- Fix belongs in: decisions/ADR-0041.md §3 (A2's text)
- Severity: Low-Medium
- Confidence: medium
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0041.md:154-158; decisions/ADR-0052.md:82-87, :253 ('A fixed generic envelope, naming one bundle revision', not taken at R1), :317-320, :335; mechanism/GAPS-AND-ASSUMPTIONS.md:107 (b)

### F-11: ADR-0047 §7's sentence on break-glass presupposes X1 and a Thinker; under ADR-0052 there is no break-glass permit, the actor is a person, and R3 does not reach the seat
- Against: decisions/ADR-0047.md:306 (and decisions/ADR-0052.md:122)
- Basis: in force
- Claim: "**Break-glass does not reach past F1 to F3** (ADR-0041 A1, §3): a forbid denies whatever permit is satisfied, as R3 already does. An emergency is the moment an injected Thinker would most want one."
- Why wrong: decisions/ADR-0052.md:101 "`X1-break-glass` is retired"; :67 "**The person acts, and no agent does.**"; :122 "**`R3-observer-live` does not reach it.**" So "as R3 already does" is false of break-glass as ratified. decisions/ADR-0041.md:171 restates the point for the emergency seat ("R5 to R7 are forbids on `Actuate` whatever the seat's kind"); ADR-0047 §7 was left as written. The same record's status note (line 22) says "C1 does not apply: no privileged path is touched", beside this bullet on a privileged path.
- Fix belongs in: decisions/ADR-0047.md §7
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0047.md:306-307, :22; decisions/ADR-0052.md:67, :101, :122-124; decisions/ADR-0041.md:171-174

### F-12: ADR-0047 §11 still says F4 to F6 are owed and that the reference's lift supplies no label attribute, beside a later line recording the reference condition as seen
- Against: decisions/ADR-0047.md:369-371 (and :579; mechanism/GAPS-AND-ASSUMPTIONS.md:105)
- Basis: in force
- Claim: "The genesis floor is untouched, and the reference's lift does not supply the attributes they read. **F4 to F6 are not**: they are load-time checks on bundle data and are owed with the reference."
- Why wrong: decisions/ADR-0047.md:579 (R17) "**The reference condition is recorded as seen**, by ADR-0033 A10 and the addenda after it: the scripted Run cell, the load checks, the two issued lists admitted by the rules floor." mechanism/GAPS-AND-ASSUMPTIONS.md:105 "The lift hands them to the floor, the admit carries them"; :95 "`topak-bundle` `allowlist` checks W1 to W9 when a bundle loads, each seen with a bundle built to fail it". The next bullet (line 372), "**F1 to F6 are written and gated.**", carries no state of its own, so §11 as it stands reads as half unmet.
- Fix belongs in: decisions/ADR-0047.md §11
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0047.md:367-374 (the bullet is tagged ⟨R16⟩ and was not revised at R17; :372-374 carries no state), :399, :579; mechanism/GAPS-AND-ASSUMPTIONS.md:95, :105

### F-13: `floor/proposed/README.md` says the reference's lift supplies none of the label and control facts; the same file and the register say the reference has enforced these stages since 2026.10.05
- Against: floor/proposed/README.md:125 (and :6; mechanism/GAPS-AND-ASSUMPTIONS.md:106)
- Basis: living document
- Claim: "The reference's lift supplies none of them today."
- Why wrong: floor/proposed/README.md:6 "**Since 2026.10.05 the reference links, pins and replays a stage from here**". mechanism/GAPS-AND-ASSUMPTIONS.md:105 "The lift hands them to the floor"; :106 "The deciding replica computes thirteen facts about the operator, the target and the request (`State::control_facts`), lifts them into `ControlCtx`, and asks the floor".
- Fix belongs in: floor/proposed/README.md
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** floor/proposed/README.md:6, :123-125; mechanism/GAPS-AND-ASSUMPTIONS.md:105, :106

### F-14: The two floor READMEs disagree on which stage the reference links, and `floor/README.md` disagrees with itself
- Against: floor/README.md:5 and :15 (and floor/proposed/README.md:3)
- Basis: living document
- Claim: "It links the `labels` stage in `proposed/`, which is built from these files." and, of `proposed/`, "Nothing loads it; see `proposed/README.md`"
- Why wrong: floor/proposed/README.md:3 "**the reference links the `workflow` stage** (since 2026.10.08; `emergency` from 2026.10.05)". floor/README.md:22 itself says "the `emergency` stage in force and, since 2026.10.08, the `workflow` stage the reference links". G11:105 names the `emergency` stage as in force.
- Fix belongs in: floor/README.md
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: no (G11 item 102 records that the reference links `workflow`; it does not list this README)
- **Verifier:** confirmed
- **Verifier's evidence:** floor/README.md:5, :15, :22; floor/proposed/README.md:3; checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:105, :349 (item 102)

### F-15: The floor in force carries comments that contradict ADR-0052 and the file itself: R3 "applies to break-glass too", and the label forbids deny "a break-glass permit"
- Against: floor/proposed/emergency-floor.cedar:155-157 (and :166, :4; decisions/ADR-0052.md:122)
- Basis: in force
- Claim: "Deny-only, and it applies to break-glass too: a dead, partitioned or starved Observer stops its own cell and nothing else."
- Why wrong: decisions/ADR-0052.md:122 "**`R3-observer-live` does not reach it.** R3 is a forbid on a `thinker` seat (ADR-0039 §2; ADR-0041 §1), and an emergency seat is not one. The custodian's decision that break-glass does not wait on a dead Observer is kept". The same file at :201 says "X1 break-glass is retired (ADR-0052 §2)", yet :166 says the label forbids "deny whatever permit is satisfied, a break-glass permit included", and :4 names "schema: genesis.cedarschema" for a stage whose schema is `emergency.cedarschema`. narrative/glossary.md:1750 lists "R3 applies to break-glass too" as retired wording. These bytes are pinned by digest (`15c941b9a56a09f7`) as the floor G11:105 calls in force.
- Fix belongs in: floor/proposed/build.py (at the stage's next gate run)
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: no (G11 item 91 names the opening comment only)
- **Verifier:** confirmed
- **Verifier's evidence:** floor/proposed/emergency-floor.cedar:4, :155-157, :159-161 (R3 names `thinker` only), :165-166, :201-203; sha256 of the file is 15c941b9a56a09f7, the digest G11:105-106 cites; decisions/ADR-0052.md:122-124; narrative/glossary.md:1750; G11:339 (item 91) names the opening comment only

### F-16: The own-domain rule for stops (`C9`) is in ADR-0050's ratification condition and in the floor, but not in §4's decision table, and ADR-0052 §3 still says any operator may revoke
- Against: decisions/ADR-0050.md:144 (and :254; decisions/ADR-0052.md:113; floor/proposed/emergency-floor.cedar:290)
- Basis: in force
- Claim: "| `EndRound` | Deny | Ends one principal's round | An operator Persona in force, and either a live lease or a fresh sign-on assertion ⟨R1⟩ |"
- Why wrong: decisions/ADR-0050.md:254 "**`C9` is confirmed by the custodian** ⟨R9⟩ (2026.10.05): an operator ends rounds and revokes in its own domain only, whether or not its lease is live". §4's table and bullets state the domain limit only for a lapsed operator (line 158) and for adds (line 168). A decision the custodian confirmed therefore lives in §10 and in ADR-0041 A3, not in the Decision. decisions/ADR-0052.md:113 then reads "Any operator may revoke it (ADR-0050 §4)", where the floor (emergency-floor.cedar:290-292, `resource.domain != principal.domain`) and mechanism/GAPS-AND-ASSUMPTIONS.md:107 ("any operator of the domain may end or revoke it") limit it to the domain's operators.
- Fix belongs in: decisions/ADR-0050.md §4; decisions/ADR-0052.md §3
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0050.md:144-146, :158-160, :168, :254-255 (`grep -n -i 'own domain\|C9'`: for a live operator the rule appears only in §10 and the History); decisions/ADR-0052.md:113-114; floor/proposed/emergency-floor.cedar:289-292; decisions/ADR-0041.md:93; mechanism/GAPS-AND-ASSUMPTIONS.md:107

### F-17: ADR-0050 §4 gives `Renew` the same needs as `Regrant`, "every field the last lease's or narrower"; the floor's `C2-renew` states no narrowing
- Against: decisions/ADR-0050.md:142 (and floor/proposed/control-floor.cedar:245; decisions/ADR-0041.md:86)
- Basis: in force
- Claim: "| `Renew` | Add | A renewal of a live lease in the domain (ADR-0031 §4) | The same |" (the row above lists "every field the last lease's or narrower")
- Why wrong: floor/proposed/control-floor.cedar:245-251: `C2-renew` permits when `principal.kind == "operator" && resource.domain == principal.domain && context.targetLive`. `lastAlphabet` and `newAlphabet` are in `ControlCtx` for every control action, and only `C1` compares them. decisions/ADR-0041.md:86 states C2 as "the seat's kind is `operator`, and the target holds a live lease in its domain". The gates class "C1 without the alphabet comparison" a relaxation (floor/proposed/control-gates-results-2026.10.04.txt, routing rows) and have no such row for C2. With decisions/ADR-0050.md:176 ("The floor states the envelope"), a widening renewal is inside the floor's envelope and is refused, if at all, by ADR-0031's mechanism check; the record does not say so.
- Fix belongs in: decisions/ADR-0050.md §4 or decisions/ADR-0041.md §1 (A3)
- Severity: Low-Medium
- Confidence: medium
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0050.md:103-106, :141-142, :176-178; floor/proposed/control-floor.cedar:245-251, and the same entry in the stage in force, floor/proposed/emergency-floor.cedar:240-246; floor/proposed/emergency.cedarschema:113-114; decisions/ADR-0041.md:86; floor/proposed/control-gates-results-2026.10.04.txt:131 (the only alphabet candidate is C1's)

### F-18: ADR-0050 says every control entry states a guard `Operators.tla` models; the module has no `AttestGates`, no task label and one domain, and the record's list of what is outside the model omits `AttestGates`
- Against: decisions/ADR-0050.md:420 (and :281; spec/Operators.tla:42 and :212)
- Basis: evidence
- Claim: "ADR-0041 A3 names the floor's eight control entries, each stating a guard `spec/Operators.tla` models."
- Why wrong: `grep -c AttestGates spec/Operators.tla` returns 0. `Next` (spec/Operators.tla:212-218) has `Seat`, `Regrant`, `Grant`, `Renew`, `EndRound`, `Revoke`, `FenceEpoch` and the environment only, so `C3-attest-gates` and the `AttestGates` limb of `C5` have no modelled guard. spec/Operators.tla:42 lists "the task and its label (§5)" under "Declared premises, not modelled", so `C8-task-label-in-bounds` has none either; "one domain" (line 41) leaves `C9` unmodelled. decisions/ADR-0050.md:281 lists what is outside the model as "the task and its label, more than one domain, a compromised provider, and what a peer has read", without the third add variant of §4. floor/proposed/README.md:123 repeats the wider claim ("That the lift computes them correctly is what `spec/Labels.tla` and `spec/Operators.tla` model").
- Fix belongs in: decisions/ADR-0050.md §10 (and an erratum to its R7 row)
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0050.md:420 (quote exact), :281-282; `grep -c AttestGates spec/Operators.tla` gives 0; spec/Operators.tla:39-43, :212-218; decisions/ADR-0041.md:316; floor/proposed/README.md:123-125. Of the eight entries the sentence covers, C3 and C8 have no modelled guard; C9 is the ninth and outside that sentence, though unmodelled too

### F-19: `Labels.tla` makes abstractions ADR-0047 §11 does not list: no release of `untrusted`, a Run root fixed clean so that no `Consult` is ever suppressed, one delivery table, and no W9
- Against: decisions/ADR-0047.md:383 (and spec/Labels.tla:128, :166, :159, :116)
- Basis: evidence
- Claim: "`accepts`, more than one round, and a wrongly declared inside source are outside the model and say so in its header."
- Why wrong: spec/Labels.tla:128 `/\ echoReleases \in {{}, {R}}`: a release of `untrusted` is never modelled, though F5 (decisions/ADR-0047.md:290) is about an entry that "releases `untrusted` or `restricted`", and the module's premise (lines 52 to 53) covers only "an issued releasing entry really does remove the secret". spec/Labels.tla:166-172: the one consulted object is "declared with no name, and clean", its label is `{}`, and `Clear({})` (line 159) is always true, so a `Consult` delivered as a handle (decisions/ADR-0047.md:138) is unreachable and F3 over a consulted object is never exercised. The module has one `suppress` set where §2 has a table "per seat kind". `WellFormed` (lines 117 to 121) has no destination check (W9). The record names none of these as outside the model.
- Fix belongs in: decisions/ADR-0047.md §11
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0047.md:128, :290, :383-384; spec/Labels.tla:50-55, :116-121, :127-128, :159, :166-172

### F-20: `ToolList.tla` models a lease narrowed to a set of tools; since R6 the record says a lease cannot carry one, and §8 still reports the module as meeting the condition
- Against: decisions/ADR-0048.md:204 (and :187; spec/ToolList.tla:59, :79, :126)
- Basis: evidence
- Claim: "**The narrowing is what the lease carries, and today that is its alphabet** ⟨R6⟩." with "ADR-0031 §1's lease schema is closed and carries no tool set, so a lease cannot be narrowed to one tool"
- Why wrong: spec/ToolList.tla:59 `lease,           \* [live, rev, narrow]: the round's lease`; :79 `List(rv, n) == IF Mut = "M_WIDE" THEN Allow[rv] ELSE Allow[rv] \cap n`; :126 `\E n \in SUBSET Tools : Grant(n)`. The mutation `M_WIDE` ("the list ignores the lease's narrowing", line 41) and the witness `NeverNarrowed` are about a narrowing the record now says does not exist. The module (`7c0a18b897e6cb98`) predates R6 and is unchanged; §8's "**Met at R4**" and the mutation "the lease's narrowing ignored" (line 187) were not revisited, and R6's row does not mention the module.
- Fix belongs in: decisions/ADR-0048.md §8
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: G11 item 95 lists the open question (whether a lease carries a tool set), not the module's mismatch
- **Verifier:** confirmed with correction; severity Low (reader: Low-Medium)
- **Verifier's correction:** The mismatch is real: the module's lease carries a tool set (`narrow`), the record since R6 says a lease carries none, and neither R6's row nor §8 mentions the module. But the module over-approximates: every narrowing the record now allows (all or none of the revision's entries by the alphabet, a subset by the deployment's allowlist) is one of its `SUBSET Tools`, so 'Met at R4' is not falsified, and `M_WIDE` still has a referent. What is unlisted is the difference itself, and the witness `NeverNarrowed` reaches a per-lease subset the record says a lease cannot carry. No claimed property is affected, hence Low.
- **Verifier's evidence:** decisions/ADR-0048.md:97-99, :182-196, :199-208, :303; spec/ToolList.tla:12-14, :26-29, :41-42, :59, :79, :126, :155; sha256 of spec/ToolList.tla is 7c0a18b897e6cb98, the digest §8 cites at R4; mechanism/GAPS-AND-ASSUMPTIONS.md:104

### F-21: ADR-0047 §4 adds two attributes to the context and defines `inputLabels` per input; schema S adds four and carries `inputLabels` as one joined set
- Against: decisions/ADR-0047.md:187 and :192 (and floor/proposed/labels.cedarschema:96-99; decisions/ADR-0041.md:72)
- Basis: in force
- Claim: "Two attributes are added to an `Actuate`'s context, and the second to a `Report`'s" and "| **`inputLabels`** | For each input that is a handle, the label of the item it names | Read from the record the handle names |"
- Why wrong: floor/proposed/labels.cedarschema:96-99: `clearSet: Set<String>`, `inputLabels: Set<String>,             // join of the labels of the call's inputs that are handles`, `destLiteral: Bool`, `destLabels: Set<String>`, under the comment "All four are computed by the mechanism". decisions/ADR-0041.md:72 "in the context `clearSet`, `inputLabels`, `destLiteral` and `destLabels`". The record's own R16 row (line 578) says "a schema that gains `Tool.outward` and four context attributes". decisions/ADR-0030.md:173-175 places the destination facts "On the tool", a third account.
- Fix belongs in: decisions/ADR-0047.md §4 (and decisions/ADR-0030.md A2's sentence)
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0047.md:187-193, :578; floor/proposed/labels.cedarschema:94-99 and floor/proposed/emergency.cedarschema:94-99; decisions/ADR-0041.md:71-72; decisions/ADR-0030.md:173-175

### F-22: ADR-0049 says in three places that the reference still reads a Wasm tool's target from node configuration; the register says that ended on 2026.10.05
- Against: decisions/ADR-0049.md:152 (and :302, :274; mechanism/GAPS-AND-ASSUMPTIONS.md:103)
- Basis: in force
- Claim: "The reference today reads it from node configuration (I44), and is to follow."
- Why wrong: mechanism/GAPS-AND-ASSUMPTIONS.md:103 "**The target is the allowlist entry's, in the bundle revision the lease names** (2026.10.05; ADR-0034 A2 R4, ADR-0049 §5)" and "Until 2026.10.05 the target was read from node configuration, contrary to A2 as in force since Batch 30; that is closed". :139 (G19) "since 2026.10.05 the entry is the only declaration: the tool host reads the target there". decisions/ADR-0033.md:578 is the addendum titled "the tool host reads a Run tool's target from its allowlist entry, 2026.10.05 ⟨A9⟩". The record was ratified the same day with the sentence in §5, in its open obligations (line 302, "which still reads the target from node configuration") and in its consequences (line 274).
- Fix belongs in: decisions/ADR-0049.md §5, Consequences, Open obligations
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0049.md:151-153, :274-275, :302-303; mechanism/GAPS-AND-ASSUMPTIONS.md:103, :139; decisions/ADR-0033.md:578-582

### F-23: ADR-0049's header says ratification closes `mechanism/` I13; its own R4 and the register say the reference does not follow §2's digest
- Against: decisions/ADR-0049.md:29 (and :318, :92; mechanism/GAPS-AND-ASSUMPTIONS.md:74)
- Basis: in force
- Claim: "On ratification: ADR-0040's open obligation on the entry's schema; `mechanism/` I13 and I33; the two-declarations half of G19."
- Why wrong: decisions/ADR-0049.md:318 (R4) "§2's digest over the entry's inputs is not followed at the reference (`mechanism/` I13) and is carried as a debt: it is not among §9's conditions." mechanism/GAPS-AND-ASSUMPTIONS.md:74 "**ADR-0049 §2 adopts this**, with one difference the reference has not closed (2026.10.05): the record's digest covers the canonical form of the *entry's* inputs part, and the reference digests the schema the tool's own MCP server reports. A Wasm tool's digest is its module's bytes alone. Nothing compares either with the entry's `inputs`". So §2's "*(drafter's choice: this adopts the reference's I13)*" (line 92) is also not exact: the two digests cover different things.
- Fix belongs in: decisions/ADR-0049.md header and §2
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: G11 item 94 lists the digest as not followed; the "Closes" line is not listed
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0049.md:29-30, :91-92, :304, :318; mechanism/GAPS-AND-ASSUMPTIONS.md:74; checkpoints/topak-genesis-checkpoint-G10-2026.10.05.md:371 (item 94)

### F-24: ADR-0050's header says ratification closes the operator half of `mechanism/` G5; G5 is unchanged and the record's own §10 keeps an unsigned socket that seats
- Against: decisions/ADR-0050.md:35 (and :300; mechanism/GAPS-AND-ASSUMPTIONS.md:125)
- Basis: in force
- Claim: "On ratification: CR-34; the operator half of `mechanism/` G5."
- Why wrong: mechanism/GAPS-AND-ASSUMPTIONS.md:125 still reads "| **G5** | **Authentication**: principals, operators, replicas | Bearer token (principals); socket file mode 0600 (operator); none (replica TCP) | Anyone who can reach a socket can act." decisions/ADR-0050.md:300-302 "The unsigned socket stands in, and whoever reaches it can seat." The register was "brought current 2026.10.05" (its line 3) and I47 describes signed requests, but the G5 row does not reflect them, and the bootstrap path leaves the half open in any case.
- Fix belongs in: decisions/ADR-0050.md header; mechanism/GAPS-AND-ASSUMPTIONS.md G5
- Severity: Low-Medium
- Confidence: medium
- Already on the corpus's own lists: G11 item 88 covers the bootstrap path; the "Closes" line and the G5 row are not listed
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0050.md:23, :35, :292-295, :300-302; mechanism/GAPS-AND-ASSUMPTIONS.md:3, :106, :125

### F-25: Clauses in force in three of the records are stated in terms of ADR-0035, which is Proposed, and two of them do not say so
- Against: decisions/ADR-0047.md:408 (and decisions/ADR-0048.md:107; decisions/ADR-0050.md:30, :201, :340; decisions/ADR-0035.md:11)
- Basis: in force
- Claim: "**ADR-0035 carries §3's lineage rule**: done at its R5, 2026.10.03. Both records are Proposed, so whichever is ratified second confirms the other's sentence."
- Why wrong: decisions/ADR-0035.md:11 "**Status:** Proposed · 2026.09.25"; decisions/ADR-0047.md:19 is Accepted. So ADR-0047 §3's rule (line 159, "An item delivered as a handle is `ingress` and is not `consumed`") is in force over sets (`ingress`, `consumed`) that only a Proposed record defines, and line 408 is stale. decisions/ADR-0048.md:107 "**A Build round's tool list is `ingress` and `consumed`** ... ADR-0035 §1 carries the rule at its R6" has the same dependence and does not give ADR-0035's status. decisions/ADR-0050.md:30 lists "ADR-0035 (lineage; independence as an exclusion rule)" under "Depends on" with no status, where other entries are marked ("ADR-0036 (`Launch`, pending)"). Line 201 states "**At the archetype the peer's lineage is independent**" and line 340 "**ADR-0035's independence rule does the work for operators**", of a rule G11:329 lists as "ADR-0035, Proposed".
- Fix belongs in: decisions/ADR-0047.md §11, decisions/ADR-0048.md §2, decisions/ADR-0050.md header and §6
- Severity: Low-Medium
- Confidence: medium
- Already on the corpus's own lists: G11 item 20 lists ADR-0035 as Proposed; the dependence of these in-force clauses is not listed
- **Verifier:** confirmed with correction
- **Verifier's correction:** ADR-0050 does give ADR-0035's status: :248-249, 'ADR-0035 R7 and ADR-0036 R6 are applied, both being Proposed records', and its R7 row (:420). What it lacks is the mark on the Depends-on line (:30) and at the clauses (:201, :340). Only ADR-0048 gives no status anywhere, so 'two of them do not say so' should read one. ADR-0047:408 does say so, and is stale.
- **Verifier's evidence:** decisions/ADR-0047.md:19, :159-162, :408-409; decisions/ADR-0048.md:107-108 and `grep -n ADR-0035 decisions/ADR-0048.md` (six mentions, none with a status); decisions/ADR-0050.md:30, :201, :248-249, :340, :420; decisions/ADR-0035.md:11; checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:129-130, :329

### F-26: ADR-0052 writes a successor "for ADR-0029 §5's fifth invariant", but ADR-0029 §5 still names `BreakGlass` and `BreakGlassNeverChangesAuthority`, and ADR-0052 carries no debt against ADR-0029
- Against: decisions/ADR-0052.md:204 (and :33; decisions/ADR-0029.md:99; spec/BreakGlass_A1.tla:2)
- Basis: in force
- Claim: "`spec/BreakGlass_A1.tla` (`b586a6afa4fd5136`), for ADR-0029 §5's fifth invariant under ADR-0026 A2's reading of R7"
- Why wrong: decisions/ADR-0029.md:99 "| `BreakGlass` | `BreakGlassNeverChangesAuthority` |" is the bootstrap trigger's fifth module and invariant, unchanged; `grep -n BreakGlass_A1 decisions/ADR-0029.md` returns nothing. The successor's invariant is `EmergencyNeverChangesAuthority` (spec/BreakGlass_A1.tla:94), a different name over a different mechanism. ADR-0029's A3 row (line 274) says "The bootstrap modules of §5 are unchanged". ADR-0052's "Carries a debt against" (lines 33 to 36) lists nine records and not ADR-0029, so the trigger in force names a module of a path the corpus has retired, with no amendment drafted.
- Fix belongs in: decisions/ADR-0029.md §5 (a dependent amendment); decisions/ADR-0052.md debt line
- Severity: Low-Medium
- Confidence: medium
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0052.md:33-36, :204-205; decisions/ADR-0029.md:99, :274; `grep -n BreakGlass_A1 decisions/ADR-0029.md` empty; spec/BreakGlass_A1.tla:2-5, :94

### F-27: ADR-0052 says `RulesFloorBase.tla` changes when ADR-0026 A2 is ratified; A2 was ratified with ADR-0052 and the module is unchanged
- Against: decisions/ADR-0052.md:313 (and decisions/ADR-0026.md:13; spec/RulesFloorBase.tla:44)
- Basis: in force
- Claim: "`RulesFloorBase.tla` still carries `bgScope` and R6's bound of two exceptions: ADR-0026 A2 changes both, and the module changes when A2 is ratified."
- Why wrong: decisions/ADR-0026.md:13 "A2, drafted 2026.10.04, with ADR-0052: R6's count and R7's subject (§2), ratified 2026.10.05 (Batch 34) and applied inline ⟨B34⟩". spec/RulesFloorBase.tla:44 `[] e = "R6" -> r.exceptions <= 2`; :45 `[] e = "R7" -> r.bgScope \cap AuthActs = {}`; :53 "Two exceptions at genesis: erasure and break-glass (ADR-0013 §3)". spec/BreakGlass_A1.tla:13 and spec/README.md:27 also still call A2 "pending".
- Fix belongs in: spec/RulesFloorBase.tla (a successor); decisions/ADR-0052.md open obligations
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: G11 item 90
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0052.md:313-314; decisions/ADR-0026.md:13; spec/RulesFloorBase.tla:44-45, :53; spec/BreakGlass_A1.tla:13; spec/README.md:27; the module's state is already carried as open by G10:367 and G11:338 (item 90), as the reader says

### F-28: ADR-0052's ratification row says the missing review is "one of the two debts"; its §9 names three debts of its own and ADR-0050's
- Against: decisions/ADR-0052.md:341 (and :226-237)
- Basis: in force
- Claim: "**Not reviewed by a reader other than the drafter** (ADR-0029 A2.5), which is one of the two debts the provisional status carries."
- Why wrong: decisions/ADR-0052.md:227-237: "It rests on ADR-0050, which is provisional, and it carries debts of its own: - **A seating prepared by promotion is not built.** ... - **Two questions the reference raised are open.** ... - **No reader other than the drafter has reviewed it.**", and the exit names four conditions. The sentence is ADR-0050's (decisions/ADR-0050.md:424), where two is right.
- Fix belongs in: decisions/ADR-0052.md History (an erratum to the B34 row)
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0052.md:226-238, :341; the identical sentence at decisions/ADR-0050.md:424

### F-29: Both degeneracy tables still call the degenerate case "The reference today", against each record's own header
- Against: decisions/ADR-0052.md:171 and decisions/ADR-0050.md:239 (and decisions/ADR-0052.md:24; decisions/ADR-0050.md:26; decisions/ADR-0033.md:767)
- Basis: in force
- Claim: "None in force. §9's properties are lost. The reference today" (D-0052-1) and "§10's properties are lost. The reference today" (D-0050-1)
- Why wrong: decisions/ADR-0052.md:24 "One degeneracy (§8): X1 as the reference had it until 2026.10.05." decisions/ADR-0033.md:767 "D-0052-1, which was "the reference today", is no longer the reference." decisions/ADR-0050.md:26 "the socket, which was the reference until 2026.10.05 and is still its path for a first seating".
- Fix belongs in: decisions/ADR-0052.md §8; decisions/ADR-0050.md §9
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0052.md:24, :171; decisions/ADR-0050.md:26, :239, :292-295 (the socket is still the path for a first seating, so D-0050-1 is stale in part only, as the header says); decisions/ADR-0033.md:765-767

### F-30: The register's rows for these records contradict each other on what the reference has built
- Against: mechanism/GAPS-AND-ASSUMPTIONS.md:95 and :44 (and :105, :46, :106, :107)
- Basis: living document
- Claim: "The handle form (§3), the `accepts` check at admit, `labels.delivery` and `labels.root` (§7) are ADR-0047's and unbuilt" (I33) and "Not followed: §2's digest over the entry's inputs (I13); the handle form" (§1.1, ADR-0049)
- Why wrong: Row I46 (line 105) of the same file: "A handle among an `Actuate`'s inputs is checked against the input's `accepts` by the bundle tier and resolved by the tool host" and "`labels.root` is `{label, objects}`, a label for the root and one per named object; the delivery table must have a row for `thinker` and for `observer`". The code uses the record's form: mechanism/crates/topak-core/src/labels.rs:43 "`{"handle": {"actuate": <seq>}}` or `{"handle": {"consult": "<digest>"}}`". Three more pairs:
  - Line 46 "Not followed: a task, and so the refusal of one with no label" against line 106 "A `Regrant` grants the seat's next round with the seating's binding, carries the task's digest and label ... `clearSet` starts from the label" (and decisions/ADR-0033.md:694, refused by `C8`).
  - Line 105 "(`inside_targets`, `releasers`; ADR-0025 A2, pending)" against line 95 "ADR-0025 A2, ratified in Batch 34".
  - Line 106 "An emergency seating (ADR-0050 R6; ADR-0052) is not built" against line 107, which describes it built.
  
  The file's line 3 says the register was "brought current 2026.10.05".
- Fix belongs in: mechanism/GAPS-AND-ASSUMPTIONS.md (rows §1.1 ADR-0049 and ADR-0047, I33, I46, I47)
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** mechanism/GAPS-AND-ASSUMPTIONS.md:3, :44, :46, :95, :105, :106, :107 (each quoted phrase located with `grep -n -o`); mechanism/crates/topak-core/src/labels.rs:42-43; decisions/ADR-0033.md:694

### F-31: `spec/README.md` gives four of the five records as Proposed and two ratified amendments as pending, and disagrees with itself on ADR-0052
- Against: spec/README.md:26-32 and :138-143 (and :34)
- Basis: living document
- Claim: "| `Emergency.tla` | ADR-0052 §9 (Proposed) |", "| `ToolList.tla` | ADR-0048 §8 (Proposed) |", "| `Operators.tla` | ADR-0050 §10 (Proposed) |", "| `Labels.tla` | ADR-0047 §11 (Proposed) |", and for the successors "ADR-0026 A2 (pending)" and "ADR-0013 §4, A1 (pending)"
- Why wrong: decisions/ADR-0047.md:19, ADR-0048.md:15, ADR-0050.md:20 and ADR-0052.md:18 are Accepted since 2026.10.05 (two provisional). decisions/ADR-0026.md:13 and decisions/ADR-0013.md:250 give A2 and A1 as ratified in Batch 34. The same README at :34 has "ADR-0052 §9 (provisional, B34)" for `Emergency_live.tla`, eight lines below ":26 ADR-0052 §9 (Proposed)".
- Fix belongs in: spec/README.md
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: no (G11 item 90, "`spec/` behind the records", names `bgScope` and the binding table, not this index)
- **Verifier:** confirmed
- **Verifier's evidence:** spec/README.md:26-30, :32, :34, :138-143; decisions/ADR-0047.md:19; decisions/ADR-0048.md:15; decisions/ADR-0050.md:20; decisions/ADR-0052.md:18; decisions/ADR-0026.md:13; decisions/ADR-0013.md:250

### F-32: The decisions index omits the confirmation-required criteria for all five records, and its status column is headed "Status at G8"
- Against: decisions/README.md:60-63, :65 and :12
- Basis: living document
- Claim: "| [ADR-0047](ADR-0047.md) | The Listener labels what it delivers: a label on every item, and a handle in place of what is suppressed | Accepted (genesis) · Batch 34, 2026.10.05 (drafted 2026.10.03, after G9) | |"
- Why wrong: decisions/ADR-0047.md:19 "Accepted (genesis) · 2026.10.05 · confirmation required (ADR-0029 C4; C2 for §3)"; ADR-0048.md:15 "(ADR-0029 C4, C3)"; ADR-0049.md:15 "(ADR-0029 C4; C2 for §5)"; ADR-0050.md:20 and ADR-0052.md:18 "(ADR-0029 C1, C3, C4; provisional under A4)". G11:50 counts 0047 to 0049 among the 27 confirmation-required records. Sibling rows carry the marking, for example decisions/README.md:59 "Accepted (genesis); confirmation required: C2, C4" and the row for ADR-0053. The column header at :12 is "Status at G8" under an introduction (line 3) that says "**Status is as of Genesis Checkpoint G11 (2026.10.09)**".
- Fix belongs in: decisions/README.md
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/README.md:3, :12, :56-63, :65-66; decisions/ADR-0047.md:19; decisions/ADR-0048.md:15; decisions/ADR-0049.md:15; decisions/ADR-0050.md:20; decisions/ADR-0052.md:18; checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:50

### F-33: Across the five records, sibling records and dependent amendments ratified in Batch 34 are still cited as Proposed or pending
- Against: decisions/ADR-0052.md:25 (and decisions/ADR-0050.md:110; decisions/ADR-0048.md:28, :162, :175; decisions/ADR-0047.md:301, :405, :472, :536; decisions/ADR-0049.md:47-49, :230; decisions/ADR-0050.md:245; decisions/ADR-0052.md:175)
- Basis: in force
- Claim: "**Depends on:** ADR-0013 §1 (every privileged grant is a quorum decision on an anchor-issued roster), ADR-0050 (Proposed: the seating; a human principal with a Persona and a key; the control alphabet)"
- Why wrong: decisions/ADR-0050.md:20 "Accepted (genesis) · provisional · 2026.10.05". The same kind of line elsewhere:
  - decisions/ADR-0050.md:110 "(ADR-0052, Proposed 2026.10.04)".
  - decisions/ADR-0048.md:28 "(the entry's channel declaration, pending)" against its own line 80 "in force since Batch 30" (R5 says "Two mentions updated"; this is a third).
  - decisions/ADR-0048.md:162 "(ADR-0047, Proposed)".
  - decisions/ADR-0047.md:472 "(ADR-0040; ADR-0049, Proposed)" and :536 "ADR-0050, Proposed 2026.10.04".
  - decisions/ADR-0047.md:301 "F1 to F3 are named by ADR-0041 A1 ⟨R8⟩, drafted and pending" against decisions/ADR-0041.md:20.
  - decisions/ADR-0049.md:47-49, a "State" column reading "Pending", "Proposed", "Proposed".
  - Each ratification condition still says its dependent entries are "each pending and marked inline" (ADR-0047:405, ADR-0048:175, ADR-0049:230, ADR-0050:245, ADR-0052:175), where each B34 row says they were ratified with the record.
- Fix belongs in: the five records (pointer revisions)
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no (G11 item 98 lists the same fault in two policy comments only)
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0052.md:25-26, :175; decisions/ADR-0050.md:20, :110, :245; decisions/ADR-0048.md:28, :80, :162, :175, :302; decisions/ADR-0047.md:301, :405, :472, :536; decisions/ADR-0049.md:47-49, :230; decisions/ADR-0041.md:19-21

### F-34: ADR-0050 §10 contradicts itself in three places about the entries, the addendum and the reference
- Against: decisions/ADR-0050.md:247, :249 and :253 (and :252, :296, :293)
- Basis: in force
- Claim: "ADR-0041 A3 (the eight control entries)", "ADR-0033's addendum waits for the reference." and "The reference has none of the six actions."
- Why wrong: decisions/ADR-0050.md:252-253 "Nine entries and not eight: `C9-stop-in-own-domain` was added in the writing." Line 296 "**Seen at R10** ⟨R10⟩, by ADR-0033 A11: the five behaviours that remain." Lines 293-294 "Every successor grant, renewal, gate attestation, end of round, revocation and fence goes through a signed operator request decided by `C1` to `C9`." (decisions/ADR-0041.md:316, A3's History row, also still says "§1 gains eight entries" over a table of nine.)
- Fix belongs in: decisions/ADR-0050.md §10
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed with correction
- **Verifier's correction:** These are superseded dated layers, not an unresolved contradiction: :245-249 is tagged ⟨R7⟩ and :250-253 ⟨R8⟩, and later-tagged sentences in the same section supersede them (:252-253 'Nine entries and not eight' corrects the count in place; :254 ⟨R9⟩; :292-296 ⟨R9⟩ ⟨R10⟩, 'Seen at R10, by ADR-0033 A11'). The defect is that the three sentences were left standing unstruck, where the same section strikes other superseded text (:289-290, :307).
- **Verifier's evidence:** decisions/ADR-0050.md:245-255, :289-296, :307; decisions/ADR-0041.md:316

### F-35: Open obligations and consequences that the records themselves, or the checkpoint, have since discharged are still listed as open
- Against: decisions/ADR-0047.md:475, :541, :547, :550, :551, :552 (and decisions/ADR-0048.md:287; decisions/ADR-0050.md:391, :402; decisions/ADR-0052.md:285, :311, :323)
- Basis: in force
- Claim: "**One author, one day, and no module yet.**", "**The tool-description record** (CR-32's other half).", "**`ToolListIsExact`** (ADR-0048 §8) is not in `Labels.tla`.", "**The reference** (§11).", "**ADR-0042 §4's sentence** (finding 8), as a dependent entry."
- Why wrong:
  - The module is cited at decisions/ADR-0047.md:379 and proved at :385.
  - The tool-description record is ADR-0048 (decisions/ADR-0047.md:342).
  - `ToolListIsExact` has its own module since ADR-0048 R4 (spec/ToolList.tla:136).
  - The reference condition is "Seen at R17" (decisions/ADR-0047.md:399).
  - decisions/ADR-0042.md:139 carries the handle case as A1, ratified in Batch 34.
  - The narrative obligations (ADR-0047:552, ADR-0048:287, ADR-0050:402, ADR-0052:323) are met: narrative/glossary.md:155, :171, :181, :186, :652-668 and :693-709 define the terms, and G11:337 (item 86) is "Discharged".
  - decisions/ADR-0050.md:391 lists "The dependent entries, the floor's control entries, the module and the reference" and decisions/ADR-0052.md:311 "The floor changes and the reference", each recorded as met in the same record's ratification condition.
  - decisions/ADR-0052.md:285 "**Five accepted records move**" against eight dependent amendments at :175-177.
- Fix belongs in: the open-obligation and consequence sections of ADR-0047, ADR-0048, ADR-0050 and ADR-0052
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0047.md:342, :379, :385, :399, :475, :541, :547, :550-552; decisions/ADR-0048.md:287; decisions/ADR-0050.md:391, :402; decisions/ADR-0052.md:175-177, :285, :311, :323; decisions/ADR-0042.md:139-143; narrative/glossary.md:155, :171, :181, :186, :652, :658, :668, :693-709; checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:337

### F-36: ADR-0049 §9's reference condition records no state, asks for ten checks where the evidence counts nine, and lists different dependent amendments from its own ratification row
- Against: decisions/ADR-0049.md:233-235 and :230-232 (and :319; mechanism/GAPS-AND-ASSUMPTIONS.md:95; decisions/ADR-0033.md:637)
- Basis: in force
- Claim: "W1 to W10 refused at load, **each seen** with a bundle built to fail it; the tool host taking a Wasm tool's target from the entry (§5)."
- Why wrong: Unlike its siblings (ADR-0047:399 "Seen at R17", ADR-0050:296 "Seen at R10", ADR-0052:225 "Seen at R6"), §9 has no line saying the condition was seen or by which addendum. The evidence counts nine: decisions/ADR-0033.md:637 "each of W1 to W9 seen with a bundle built to fail it"; mechanism/GAPS-AND-ASSUMPTIONS.md:95 "checks W1 to W9 when a bundle loads, each seen". The restated W10 has a test (mechanism/crates/topak-bundle/tests/allowlist.rs:289), but neither text counts it. The last item is contradicted by the record's own §5 (F-22). Separately, §9 lists as dependent entries "ADR-0040 A1 and ADR-0022 A3", "ADR-0030 A2", "ADR-0025 A2" and the pointer "ADR-0034 R3" (lines 230 to 232), while the B34 row (line 319) lists "(ADR-0022 A3, ADR-0030 A2, ADR-0040 A1, ADR-0043 A1, ADR-0045 A1)": ADR-0025 A2 is dropped and two are added that §9 never names.
- Fix belongs in: decisions/ADR-0049.md §9 and its B34 row
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0049.md:230-235, :319; `grep -n 'Seen at\|Met at' decisions/ADR-0049.md` empty; decisions/ADR-0033.md:637 and `grep -n W10 decisions/ADR-0033.md` empty; mechanism/GAPS-AND-ASSUMPTIONS.md:44, :95 (both count W1 to W9, though :95 also says a field the record does not define is refused, 'W10 as restated'); mechanism/crates/topak-bundle/tests/allowlist.rs:285-293

### F-37: "74 cases passing" and "106 cases passing" cite gate results files that record no case run, for stages whose test files are not in the tree
- Against: decisions/ADR-0047.md:367-368 and decisions/ADR-0050.md:251-252 (and floor/proposed/README.md:34)
- Basis: evidence
- Claim: "74 cases passing, every gate passing (`floor/proposed/labels-gates-results-2026.10.04.txt`, `3579b95a42573958`)"
- Why wrong: `grep -n -i 'case\|tests' floor/proposed/labels-gates-results-2026.10.04.txt floor/proposed/control-gates-results-2026.10.04.txt` returns nothing. The files hold the gates (totality, non-vacuity, every-entry-matters, routing, controls) and "RESULT: all gates pass", and no behavioural case. floor/proposed/README.md:34 says of the test files "`workflow-tests.json` is tracked ... and `emergency-tests.json` ...; the other two are not (about 2 MB)", so the 74 and the 106 cases exist only as the output of `build.py`, which I did not run. The counts are consistent with the tracked `emergency-tests.json` (107 cases, which I listed), so I do not dispute the numbers; the claim that they passed has no artifact.
- Fix belongs in: floor/proposed/run-gates.py (record the case run), or the two ratification conditions
- Severity: Low
- Confidence: medium
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** `grep -n -i 'case\|tests' floor/proposed/labels-gates-results-2026.10.04.txt floor/proposed/control-gates-results-2026.10.04.txt` empty (exit 1); floor/proposed/ holds only emergency-tests.json and workflow-tests.json; floor/proposed/README.md:34; decisions/ADR-0047.md:367-368; decisions/ADR-0050.md:251-252; the two results files hash to the digests cited (3579b95a42573958, aa96c96916a87c05)

### F-38: ADR-0052 §9 says the cases show an emergency seat "refused every authoring action"; the stage has cases for `Draft` and `Submit` and none for `Invoke`
- Against: decisions/ADR-0052.md:184
- Basis: evidence
- Claim: "The cases show an emergency seat calling inside its envelope with no live Observer, refused outside it, refused every authoring action, and bound by `R6`"
- Why wrong: floor/proposed/emergency-tests.json, cases 100 to 107 (listed with `python3`): "R1 an emergency seat calls a tool in its envelope", "R3 does not couple an emergency seat: no live Observer", "R1 an emergency seat calls a tool outside its envelope", "R2 an emergency seat reports with no live Observer", "X1 is retired: a Thinker cannot reach the emergency envelope", "R6 binds the person holding an emergency seat", "B10 an emergency seat cannot draft", "B10 an emergency seat cannot submit". `B10` covers `Draft`, `Invoke` and `Submit` (floor/proposed/emergency-floor.cedar:105-115); no case has an emergency seat `Invoke`.
- Fix belongs in: decisions/ADR-0052.md §9, or floor/proposed/build.py
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0052.md:183-185; floor/proposed/emergency-tests.json cases 100 to 107 listed with python3 (seat e1: Actuate four times, Report, Draft, Submit; no Invoke by any emergency seat in the 107); floor/proposed/emergency-floor.cedar:105-115

### F-39: ADR-0047's R10 row says `Safe` holds at `MaxSeq = 4`; no results file has a row at 4
- Against: decisions/ADR-0047.md:572
- Basis: evidence
- Claim: "With that rule ten properties hold at `MaxSeq = 3` (and `Safe` at 4)"
- Why wrong: spec/Labels-results-2026.10.03.txt:3 and spec/Labels-results-2026.10.04.txt:3 both read "Runner: labels-gen-results.sh · MaxSeq = 3", and every one of their 33 and 37 rows is at that constant; `grep -rn 'MaxSeq *= *4' spec/` returns nothing. The claim is later subsumed by the proof for every `MaxSeq`, but as a checked claim it has no artifact.
- Fix belongs in: decisions/ADR-0047.md History (an erratum), or a results row
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0047.md:572; `grep -rn 'MaxSeq *= *4' spec/` empty (exit 1); spec/Labels-results-2026.10.03.txt:3 (33 rows) and spec/Labels-results-2026.10.04.txt:3 (37 rows), all at MaxSeq = 3

### F-40: ADR-0047's pending A1 row counts eight workflow attributes; its inline text, after ADR-0054 R6 struck `denials`, lists seven
- Against: decisions/ADR-0047.md:581 (and :207)
- Basis: pending
- Claim: "the fixed set of mechanism-computed attributes gains a workflow node's eight, read by guards and never by policy"
- Why wrong: decisions/ADR-0047.md:207 "`end`, `actuates`, ~~`denials`,~~ (ADR-0054 R6) `label`, `covered`, `found`, `outcome` and `output`": seven. decisions/ADR-0054.md:162-168 has the same seven rows.
- Fix belongs in: decisions/ADR-0047.md History (the A1 row)
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0047.md:206-208, :581; decisions/ADR-0054.md:162-168 (seven rows)

### F-41: ADR-0047 §2 says a handle is never a digest of the content; for a `Consult` the handle is the content address, and ADR-0049 §3 writes it as a digest
- Against: decisions/ADR-0047.md:139 (and :138; decisions/ADR-0049.md:112)
- Basis: in force
- Claim: "A digest of the content is not used: a digest of low-entropy content can be confirmed by guessing."
- Why wrong: decisions/ADR-0047.md:138 "For a `Consult` it is the reference the Thinker supplied", and finding 2 of the same record (line 485) "The Thinker supplies a content address and receives content". decisions/ADR-0049.md:112 "| A consulted object | `{"handle": {"consult": "<digest>"}}` |". The record's defence is that the Thinker already holds it, which is a reason the digest is harmless, not that it is unused. The bold rule at line 137, "names the item by its place in the record, not by its bytes", does not hold for a consulted object.
- Fix belongs in: decisions/ADR-0047.md §2
- Severity: Low
- Confidence: medium
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0047.md:137-140, :485-486; decisions/ADR-0049.md:111-112; mechanism/crates/topak-core/src/labels.rs:42-47 (`Consult(Digest)`)

### F-42: ADR-0050's provenance note counts eleven operator requests; its Context table and its own arithmetic give ten
- Against: decisions/ADR-0050.md:4 (and :49-56)
- Basis: in force
- Claim: "(eleven operator requests, two of them signed)"
- Why wrong: The table at lines 49 to 56 names `Issue`, `BreakGlassApprove`, `Grant`, `Launch`, `Renew`, `GatesPassed`, `RegisterProfile`, `Revoke`, `FenceEpoch`, `EndRound`: ten. Line 60 "**Five requests add authority on a file's permission bits.**" with two signed and three that subtract also makes ten. `ops.rs` has since changed, so the source as read on 2026.10.04 cannot be recounted here.
- Fix belongs in: decisions/ADR-0050.md Context (name the eleventh, or correct the count)
- Severity: Low
- Confidence: medium
- Already on the corpus's own lists: no
- **Verifier:** not confirmed
- **Verifier's correction:** The texts do not conflict. The note counts the requests in `ops.rs`; the Context table lists the ten that have an effect on authority (its second column) and nowhere says it is the whole list. The eleventh is `status`, a read: mechanism/README.md:67-71 lists `grant`, `renew`, `end_round`, `revoke`, `fence_epoch`, `issue`, `gates_passed`, `register_profile`, `launch` and `status`, with `break_glass_approve` retired, and names the five later additions apart. Line 60's 'Five requests add authority' counts adds, not requests. At most the record could name the eleventh.
- **Verifier's evidence:** decisions/ADR-0050.md:4, :49-56, :60; mechanism/README.md:67-71; mechanism/crates/topak-node/src/ops.rs:31-151 (sixteen variants today; without `Control`, `PrepareEmergency`, `Activate`, `LoadWorkflow` and `WorkflowStatus`, all added after 2026.10.04, eleven remain, `Status` among them)

### F-43: ADR-0049 §1 says the entry's fields are "stated here", but `destinations` appears only in a bullet under §6 and in the illustration
- Against: decisions/ADR-0049.md:74-80 (and :172, :205, :126-137)
- Basis: in force
- Claim: "| **Labels** | `result.label`, `result.releases`; for each input, `destination`, `accepts` | Run | ADR-0047 §1, §3, §7 |"
- Why wrong: decisions/ADR-0049.md:172 "an outward entry carries `destinations: none` at the entry's top level when no input is one", and the illustration at :205 has `"destinations": "none"`. The field is in neither §1's table of parts nor §4's table of checked and claimed fields (lines 126 to 137). W10 as restated (line 170) refuses "a field this record does not define", which makes the list of defined fields load-bearing.
- Fix belongs in: decisions/ADR-0049.md §1 and §4
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0049.md:64-69, :74-80, :126-137, :170, :172-173, :205

### F-44: `R6` and `R7` name two different things inside ADR-0052: the rules floor's entries and the policy floor's label forbids
- Against: decisions/ADR-0052.md:185 (and :35, :103, :208)
- Basis: in force
- Claim: "refused every authoring action, and bound by `R6`"
- Why wrong: decisions/ADR-0052.md:35 "ADR-0026 (R6's count; R7's subject)" and :208 "dropping R7 changes nothing" mean the rules floor's R6 (the bound on exceptions) and R7 (spec/RulesFloorBase.tla:44-45). decisions/ADR-0052.md:103 "ADR-0041 A1's R5 to R7" and :185 mean `R5-no-read-then-send` to `R7-no-replayed-destination` (floor/proposed/emergency-floor.cedar:170-190). ADR-0041 A1 took "the next free numbers" (decisions/ADR-0041.md:70-71) in a namespace ADR-0026 already used for R1, R2, R5, R6, R7 and R9; the same collision recurs for `R8` and `R9` in the `workflow` stage. A reader of ADR-0052 §9 cannot tell from "bound by `R6`" which floor is meant without opening the test file.
- Fix belongs in: decisions/ADR-0041.md (the ids), or a qualification wherever both are used
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0052.md:35, :102, :103, :185, :204-208; spec/RulesFloorBase.tla:44-48; floor/proposed/emergency-floor.cedar:170-195; decisions/ADR-0041.md:70-71; floor/proposed/workflow-floor.cedar:208, :218 (R8, R9)

### F-45: ADR-0047 §4 names a fixed set of history attributes that reach policy, "with the sequence number and the round count"; schema S has no sequence-number attribute, and the Consequences call `clearSet` the first
- Against: decisions/ADR-0047.md:203 (and :464; floor/proposed/labels.cedarschema:85-100)
- Basis: in force
- Claim: "`clearSet` is one of a small, fixed, named set, with the sequence number and the round count; each is a fold the mechanism defines, and adding one is a mechanism release."
- Why wrong: `RunCtx` in floor/proposed/labels.cedarschema (and in emergency.cedarschema:85-100) holds `lease`, `epoch`, `round`, `runRoot`, `toolAllowlist`, `observerLive`, `clearSet`, `inputLabels`, `destLiteral`, `destLabels`: no sequence number and no count. The round bound is "a count; mechanism-checked" and "Not in the floor" (floor/proposed/labels-floor.cedar:11-13). The same record's Consequences (line 464) say of `clearSet` "It is still the first such attribute in schema S", which cannot hold if two others already reach policy. The one history-dependent attribute S did already have is `observerLive` ("a watermark within K of the Thinker's sequence", labels-floor.cedar:150-151), which neither sentence names.
- Fix belongs in: decisions/ADR-0047.md §4
- Severity: Low
- Confidence: low
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0047.md:202-204, :463-464; floor/proposed/emergency.cedarschema:85-100 and floor/proposed/labels.cedarschema:83-100 (`grep -n -i seq` on the stage schemas empty); floor/proposed/emergency-floor.cedar:11-13, :154-155; decisions/ADR-0030.md:177-178; the corpus uses 'round count' for the per-round count of admits (decisions/ADR-0033.md:348; decisions/ADR-0039.md:71), which is not the `round` attribute, so the reader's reading holds

### F-46: `Emergency.tla` models only the default envelope and one eligible person; ADR-0052 §9's list of what is outside the model does not say so
- Against: decisions/ADR-0052.md:195 (and spec/Emergency.tla:60, :112)
- Basis: evidence
- Claim: "**Outside it**: the label forbids, the task, the drill as a distinct seating, more than one domain, and the successors `BreakGlass.tla` and `NonComposition.tla` owe."
- Why wrong: spec/Emergency.tla:112 `envelope |-> domainTools \cup {"te"}` is the only envelope; §2's "A seating that names its envelope entry by entry is given exactly that. Several seatings may exist; the roster's quorum activates one" (decisions/ADR-0052.md:90-91) is not modelled. spec/Emergency.tla:60 `Persons  == {"h"}`: the seating's "the persons who may hold it" (decisions/ADR-0052.md:79) reduces to one person, so an activation naming a person the seating does not list cannot be expressed. §1's "holds no other seat in the round" (line 65) is not modelled either. The module's header (lines 35 to 36) lists the same omissions as the record and not these.
- Fix belongs in: decisions/ADR-0052.md §9
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0052.md:65, :79, :90-91, :195-197; spec/Emergency.tla:26-36, :60, :107-113

### F-47: ADR-0050 §2 says first leases come from two quorums and tabulates two; the same section then adds a third, the break-glass roster's
- Against: decisions/ADR-0050.md:92 (and :110)
- Basis: in force
- Claim: "There are two quorums and each has its case."
- Why wrong: decisions/ADR-0050.md:110-111 "**An emergency seating is one of these** ⟨R6⟩ (ADR-0052, Proposed 2026.10.04): prepared by promotion, and activated for one round by the break-glass roster's quorum and not by a tally." The table at lines 95 to 98 has rows for an anchor issuance and a promotion only, and `FirstLeaseHasAQuorum` (spec/Operators.tla:224) knows one `root |-> "quorum"`.
- Fix belongs in: decisions/ADR-0050.md §2
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0050.md:92-98, :110-112; spec/Operators.tla:224

### F-48: `spec/README.md` binds `Emergency_live.tla` to "ADR-0052 §9"; ADR-0052 §9 names no such module and the record has no History row for it
- Against: spec/README.md:34 (and decisions/ADR-0052.md:187-221)
- Basis: living document
- Claim: "| `Emergency_live.tla` | ADR-0039 A2; ADR-0052 §9 (provisional, B34); the liveness plan, Tier 0."
- Why wrong: `grep -n Emergency_live decisions/ADR-0052.md` returns nothing. §9 cites `Emergency.tla`, `BreakGlass_A1.tla` and `NonComposition_A1.tla` only. Its R2 row (line 336) still says of the unobserved emergency call "TLC's witness carries the fact", which `Emergency_live_proof.tla` (160 obligations, spec/Emergency_live-proof-results-2026.10.07.txt:10) has since replaced with two proved `ENABLED` invariants. The module is evidence for §4 of the record, and the record does not know it exists.
- Fix belongs in: spec/README.md, or a dependent History row in decisions/ADR-0052.md
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no (G11 item 90 notes only that the binding table has no row for `Emergency_live`)
- **Verifier:** confirmed
- **Verifier's evidence:** spec/README.md:34; `grep -n Emergency_live decisions/ADR-0052.md` empty (exit 1); decisions/ADR-0052.md:187-221, :336; spec/Emergency_proof.tla:401-404 (the dropped lemma is the ENABLED lemma for the unobserved emergency call); spec/Emergency_live-proof-results-2026.10.07.txt:10

