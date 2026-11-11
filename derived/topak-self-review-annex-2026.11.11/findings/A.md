# Self review of 2026.11.11: reader A's findings in full

Reader A read ADR-0001 to ADR-0023. Annex to `derived/topak-open-findings-register-2026.11.11.md`, Part III. Each block is the finding as the reader wrote it, against the tree at `bbda621`, followed by the verdict of a verifier that did not find it. Paths are relative to the repository root. A path a finding names as absent is written without backticks. Nothing here is ratified, and every reader and verifier is of the same model lineage as the drafter of the corpus.

41 reported: 30 confirmed, 11 confirmed with a correction, 0 dropped.

### A-1: ADR-0015 still classifies break-glass as an admit against a floor-exception entry that ADR-0013 A1 retired; the narrative restates a classification the record does not contain
- Against: decisions/ADR-0015.md:44 (and decisions/ADR-0013.md:83, narrative/theory-of-operation.md:910)
- Basis: in force
- Claim: "Each is invoked as an admit decision against its declared floor-exception entry (ADR-0013 §2), so both are already effects under the set above."
- Why wrong: decisions/ADR-0013.md:83-84, in force since Batch 34: "with X1 retired (ADR-0052 §2), the count is 1, erasure. §2's three items still describe it. Break-glass stays under §1: a quorum on an anchor-issued roster. It stops being an entry under §2." The narrative gives a different classification under the heading it takes from this record, narrative/theory-of-operation.md:911-912: "Break-glass is a lease: its calls are admits like any other, and its activation is a grant made by a roster's quorum, as a promotion is a grant made by another." ADR-0015 has no Batch 34 amendment: decisions/ADR-0052.md:341 lists "its eight dependent amendments (ADR-0009 A1, ADR-0013 A1, ADR-0016 A2, ADR-0026 A2, ADR-0037 A3, ADR-0039 A2, ADR-0041 A2, ADR-0042 A2)", and `grep -n 'ADR-0015' decisions/ADR-0052.md` returns nothing. ADR-0013's own header still reads (decisions/ADR-0013.md:21-22) "ADR-0015, whose C2 exhaustiveness claim classifies break-glass and erasure as admit decisions against §2's exception entries". The sentence at issue is part of the exhaustiveness claim ADR-0015's C2 marking exists for.
- Fix belongs in: decisions/ADR-0015.md (a dependent amendment for ADR-0052), decisions/ADR-0013.md header ("Depended on by")
- Severity: Medium-High
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0015.md:44-46 (quotation exact); decisions/ADR-0013.md:21-22, 83-84; narrative/theory-of-operation.md:910-916; decisions/ADR-0052.md:341. Absence: `grep -n 'ADR-0015' decisions/ADR-0052.md` empty; `grep -n -i '0052\|B34\|emergency\|seating\|X1' decisions/ADR-0015.md` empty. Direction right: ADR-0013 A1 is in force (B34), ADR-0015 is the stale side.

### A-2: ADR-0009 and ADR-0013 status lines omit the C3 criterion their own A1 rows declare, and the index copies the omission
- Against: decisions/ADR-0009.md:10 (and decisions/ADR-0009.md:62; decisions/ADR-0013.md:8 and decisions/ADR-0013.md:249)
- Basis: in force
- Claim: "**Status:** Accepted (genesis) · 2026.09.12 · confirmation required (ADR-0029 C1, C4 via 0013) ⟨S1⟩ ⟨B34⟩"
- Why wrong: the A1 row of the same record, decisions/ADR-0009.md:62: "**Confirmation required under C1 and C3**, as ADR-0052 is". The same sentence closes ADR-0013's A1 row (decisions/ADR-0013.md:249), whose status line (decisions/ADR-0013.md:8) reads "confirmation required (ADR-0029 C1, C4)". decisions/ADR-0052.md:20 confirms the parent: "confirmation required (ADR-0029 C1, C3, C4; provisional under A4)". Where a criterion attaches to one amendment the corpus marks the status line, as decisions/ADR-0003.md:10 does: "confirmation required (ADR-0029 C1, for A2 only)". decisions/README.md:22 and :26 repeat the status lines without C3.
- Fix belongs in: decisions/ADR-0009.md and decisions/ADR-0013.md status lines; decisions/README.md
- Severity: Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed with correction
- **Verifier's correction:** Line number: the ADR-0052 status line quoted is at decisions/ADR-0052.md:18, not :20 (line 20 is inside the Status note). Nothing else changes.
- **Verifier's evidence:** decisions/ADR-0009.md:10, 62 (A1 row read in full: "Confirmation required under C1 and C3, as ADR-0052 is"); decisions/ADR-0013.md:8, 11-16, 249; decisions/ADR-0052.md:18; decisions/ADR-0003.md:10; decisions/README.md:22, 26.

### A-3: ADR-0022 A2 is ratified "confirmation-required under C3", but the record's status line, the index and G11 §1.1 count ADR-0022 as carrying no confirmation marker
- Against: decisions/ADR-0022.md:11 (and decisions/ADR-0022.md:282, checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:49)
- Basis: in force
- Claim: "**Status:** Accepted (genesis) · 2026.09.23 : **§1–§5, §7, §8 only** ⟨B2⟩ ⟨B20⟩ ⟨B30⟩ ⟨B34⟩"
- Why wrong: decisions/ADR-0022.md:282 (B20): "**A2 ratified 2026.09.30** ... **Confirmation-required under C3**: it reverses an accepted clause." The narrative agrees with the row, narrative/theory-of-operation.md:483: "ADR-0040 and ADR-0022 A2 carry C3". G11 §1.1 line 49 lists "0022 (in part: §6 is Proposed)" among the 18 records with no confirmation marker, and line 59 says the counts are read "from each record's status line and status note together", so the count of 27 (and the narrative's 29, narrative/theory-of-operation.md:27) leaves this marking out. decisions/README.md:35 has "Accepted (genesis) : §1–§5, §7, §8 only". Compare ADR-0003 and ADR-0031, which G11 line 50 lists as "0003 (for A2 only)" and "0031 (C2 for A1 only, beside its C1)".
- Fix belongs in: decisions/ADR-0022.md status line; then decisions/README.md and the next checkpoint's §1.1
- Severity: Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0022.md:11-20 (status line, Status note and Pending carry no criterion), 282; `grep -n 'C3' decisions/ADR-0022.md` hits only History rows and notes (246, 264, 281, 282, 288); checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:49-50, 59; narrative/theory-of-operation.md:27, 483; decisions/README.md:35. The batch's own checkpoint did record it: checkpoints/topak-genesis-checkpoint-G6-2026.09.30.md:34, 56 ("0022 A2 (C3)").

### A-4: ADR-0016 §7 says Persona revocation is "Local, no consensus"; ADR-0031 §5 struck those words and says revocation is consensus-ordered
- Against: decisions/ADR-0016.md:148 (and decisions/ADR-0031.md:217)
- Basis: in force
- Claim: "Persona revocation : evaluation regression, provider disclosure, discovered lineage defect : is a denial. Local, no consensus, no floor exception."
- Why wrong: decisions/ADR-0031.md:217-218: "**Revocation is still a deny** (ADR-0016 §7): monotone, and it needs no quorum, because both tools subtract authority. ~~local, no consensus,~~ Both change replicated state, so both are consensus-ordered (ADR-0033 §4) ⟨R3⟩." The narrative follows ADR-0031, narrative/theory-of-operation.md:235-236: "Both are ordered, neither needs a quorum, and a revocation is permanent within the chain." ADR-0015 was given a pointer for the same correction (decisions/ADR-0015.md:66-68, E1); ADR-0016 §7 has no erratum, pointer or dependent entry, and its ⟨A1⟩ text (decisions/ADR-0016.md:82) leans on §7 as written: "§7 holds of it: revoking it is an ordinary deny".
- Fix belongs in: decisions/ADR-0016.md (§7, by erratum or dependent entry)
- Severity: Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0016.md:148-149, 82; decisions/ADR-0031.md:185 (the §5 heading), 217-218; narrative/theory-of-operation.md:235-236; decisions/ADR-0015.md:66-68. Absence: `grep -n '0031\|0033\|consensus' decisions/ADR-0016.md` finds line 149 only; ADR-0016's History (231-250) holds N1, B12, A1, A2, B34 and none touches §7's sentence.

### A-5: The Batch 34 rows say "The reference follows the text", and the reference's own register says it does not for three of the amended texts
- Against: decisions/ADR-0016.md:250 (and mechanism/GAPS-AND-ASSUMPTIONS.md:106; decisions/ADR-0009.md:63 with mechanism/GAPS-AND-ASSUMPTIONS.md:107; decisions/ADR-0022.md:308 with mechanism/GAPS-AND-ASSUMPTIONS.md:74)
- Basis: evidence
- Claim: "The reference follows the text (ADR-0033 A10 to A12, ratified with it)."
- Why wrong: (a) ADR-0016 A1 (decisions/ADR-0016.md:77-78) says a person "has a Persona record too (ADR-0050 §3): a signing key, a role, a domain, a lineage, a Persona ID and a sequence number". Register row I47, mechanism/GAPS-AND-ASSUMPTIONS.md:106: "**(c) An operator's Persona is its seat's key.** There is no Persona record for a person, no lineage, and nothing compares two operators' providers." (b) ADR-0009 A1 (decisions/ADR-0009.md:39-40) seats the person "on an envelope prepared by promotion". Register row I48, line 107: "**(a) the seating is prepared by the BOOTSTRAP path** (`prepare_emergency`, unsigned), which stands in for a promotion." (c) ADR-0022 A3 (decisions/ADR-0022.md:92-93): "the digest is the artifact's digest joined with the canonical inputs (ADR-0049 §2)". Register row I13, line 74: "with one difference the reference has not closed (2026.10.05): the record's digest covers the canonical form of the *entry's* inputs part, and the reference digests the schema the tool's own MCP server reports." The identical sentence stands in decisions/ADR-0013.md:250.
- Fix belongs in: the B34 rows of decisions/ADR-0009.md, ADR-0013.md, ADR-0016.md and ADR-0022.md (a later typed row; the sentence should name what is not followed)
- Severity: Medium
- Confidence: high
- Already on the corpus's own lists: G11 open list items 88, 92 and 94 (as at G10); mechanism/GAPS-AND-ASSUMPTIONS.md rows I13, I47, I48. The lists carry the gaps, not the rows' claim.
- **Verifier:** confirmed
- **Verifier's evidence:** The sentence is in all four rows, read in full: decisions/ADR-0009.md:63, decisions/ADR-0013.md:250, decisions/ADR-0016.md:250, decisions/ADR-0022.md:308. Register, read in full: mechanism/GAPS-AND-ASSUMPTIONS.md:74 (I13), 106 (I47 (c)), 107 (I48 (a)). Amended texts: decisions/ADR-0016.md:77-78, decisions/ADR-0009.md:39-40, decisions/ADR-0022.md:92-93. The addenda the sentence cites say what they leave undischarged (decisions/ADR-0033.md:1159-1161, 1165); the four rows do not.

### A-6: Three in-force texts in ADR-0016 and ADR-0022 rest on clauses of ADR-0035, which is Proposed, without saying so
- Against: decisions/ADR-0016.md:80 (and decisions/ADR-0022.md:95, decisions/ADR-0016.md:232, decisions/ADR-0035.md:11)
- Basis: in force
- Claim: "Its lineage is declared and its root is the identity provider that vouches for the person (ADR-0035 §1)."
- Why wrong: decisions/ADR-0035.md:11: "**Status:** Proposed · 2026.09.25". The cited rule is ADR-0035's R7, which that record marks as dependent on a Proposed record (decisions/ADR-0035.md:120-122). The same pattern is in ADR-0022 A3, decisions/ADR-0022.md:95: "and that list is `ingress` and `consumed` for lineage (ADR-0035 §1)", and in ADR-0016's B12 row, decisions/ADR-0016.md:232: "§5's seat-distinctness predicate now covers one pair per cell, (`thinker`, `observer`), and its enforcement is ADR-0035 §5's. No decision text changes". Each amendment's History row says it "Takes force only with" ADR-0050, ADR-0052, or the record it depends on; none names ADR-0035, and none marks the cited clause as not in force. A reader cannot tell whether "its root is the identity provider" and "`ingress` and `consumed`" are in force with A1 and A3 or wait on ADR-0035.
- Fix belongs in: decisions/ADR-0016.md (A1, B12) and decisions/ADR-0022.md (A3)
- Severity: Medium
- Confidence: high
- Already on the corpus's own lists: G11 open list item 20 covers ADR-0035 being Proposed; the three citations are not listed.
- **Verifier:** confirmed with correction; severity Low-Medium (reader: Medium)
- **Verifier's correction:** "None names ADR-0035" is too wide: ADR-0022 A3's Source cell cites "ADR-0035 R6" (decisions/ADR-0022.md:306). What no row does is name ADR-0035 as a condition of force, or mark the cited clause Proposed. No two texts disagree here; the defect is a dependency on a Proposed record that is not flagged, where the corpus elsewhere writes "(Proposed)" beside such a citation.
- **Verifier's evidence:** decisions/ADR-0016.md:79-80, 232, 248; decisions/ADR-0022.md:95, 306; decisions/ADR-0035.md:11, 109-123; `grep -n '0035' decisions/ADR-0016.md decisions/ADR-0022.md` finds only 0016:80, 232 and 0022:95, 255, 306.

### A-7: ADR-0016 §5 claims seat distinctness is a policy predicate that makes the Observer requirement "enforceable rather than advisory"; the record it now delegates enforcement to says that cannot be delivered and is not in force
- Against: decisions/ADR-0016.md:131 (and decisions/ADR-0035.md:211)
- Basis: in force
- Claim: "Expressed as a policy predicate over Persona provenance, which makes the cross-family Observer requirement enforceable rather than advisory and closes the monoculture open item."
- Why wrong: decisions/ADR-0035.md:209-211: "**Not at grant.** ... ADR-0016 §5's "enforceable rather than advisory" cannot be delivered at grant." ADR-0035 moves enforcement to the promotion tally and the deployment declaration (from line 213), which is neither a bundle decision "bounded by the floor" (decisions/ADR-0016.md:124) nor in force (decisions/ADR-0035.md:11, Proposed). ADR-0016's own B12 row accepts the move and says "No decision text changes" (decisions/ADR-0016.md:232). The narrative states the result, narrative/theory-of-operation.md:136-137: "The fourth is ADR-0035, which is Proposed, so **`Contained` is still unreachable at every rung today**". ADR-0016's Positive consequence "Cross-family Observer independence becomes machine-checkable" (decisions/ADR-0016.md:181) has no in-force mechanism behind it.
- Fix belongs in: decisions/ADR-0016.md (§5; the B12 row)
- Severity: Medium
- Confidence: medium
- Already on the corpus's own lists: G11 open list item 20 (the criterion); the §5 wording is not listed.
- **Verifier:** confirmed with correction
- **Verifier's correction:** Scope of the headline: ADR-0035 §5 says the claim "cannot be delivered at grant" and moves enforcement to the promotion tally and the deployment declaration (decisions/ADR-0035.md:213-224); it does not say it cannot be delivered. The defect as it stands: ADR-0016 §5's in-force claim has its enforcement handed by its own B12 row to a Proposed record, so nothing in force delivers "enforceable rather than advisory".
- **Verifier's evidence:** decisions/ADR-0016.md:122-133, 181, 232; decisions/ADR-0035.md:11-14, 207-224; narrative/theory-of-operation.md:136-137. Absence of an in-force predicate: `grep -n -i 'lineage\|distinct' floor/*.cedar floor/proposed/*.cedar` empty.

### A-8: ADR-0023 §6c, in force, cites as fact a ratification run of a Proposed record that has not been performed, and misstates what that run is to contain
- Against: decisions/ADR-0023.md:51 (and decisions/ADR-0036.md:352, decisions/ADR-0036.md:249)
- Basis: in force
- Claim: "(ADR-0036 §7's ratification run grants a rung-0 Observer beside a rung-1 occupant)"
- Why wrong: decisions/ADR-0036.md:352, written the day §6c was ratified: "§7's condition is not met: there is no profile file for `slm/serve`'s image, no round whose drafted content is the Persona's output, and no results file under `slm/`". decisions/ADR-0036.md:323 still lists "**The ratification run** (§7), and the `slm/` results file" as an open obligation, and ADR-0036 is Proposed (decisions/ADR-0036.md:11). §7's condition itself (decisions/ADR-0036.md:249) asks for "A rung-0 principal run beside the rung-1 one", not an Observer. The parenthesis is the only support §6c gives for "a deployment runs rung-0 principals beside higher ones".
- Fix belongs in: decisions/ADR-0023.md (§6c)
- Severity: Medium
- Confidence: high
- Already on the corpus's own lists: G11 open list item 34 (ADR-0036's ratification run, open as at G10); the citation in §6c is not listed.
- **Verifier:** confirmed; severity Low-Medium (reader: Medium)
- **Verifier's evidence:** decisions/ADR-0023.md:51 (line read in full), 165; decisions/ADR-0036.md:11, 249, 323, 352. `grep -n -i 'observer' decisions/ADR-0036.md` empty: the word is not in that record at all. Severity: the parenthesis is an illustration, and §6c's rule does not rest on it (the B29 row at 165 rests on the reference's suites).

### A-9: ADR-0017's ordering-primacy clause is reversed in effect by an accepted record, and neither ADR-0017's header nor the index says so
- Against: decisions/ADR-0017.md:37 (and decisions/ADR-0023.md:12, decisions/README.md:30)
- Basis: in force
- Claim: "The deployment axis is Persona provenance, and every external model is a documented subtraction at a lower rung."
- Why wrong: decisions/ADR-0023.md:12-14: "§5 reverses ADR-0008's Observer scoping and ADR-0017's ordering-primacy clause in effect, and ... *the ADR-0008 supersession is ADR-0038 (ratified 2026.09.29); the ADR-0017 one is unwritten*". decisions/ADR-0023.md:79: "The ADR-0017 half stays open". ADR-0017's status line is plain "Accepted (genesis) · 2026.09.12" (line 11), its only mention is a History footnote in the present tense of 09.15 (decisions/ADR-0017.md:154): "**Not touched:** the separately pending supersession of the ordering-primacy clause (ADR-0023 §5)", and decisions/README.md:30 lists it as "Accepted (genesis)". ADR-0008 and ADR-0018, reversed the same way, carry a status change (decisions/ADR-0008.md:10) and an inline note (decisions/ADR-0018.md:83-86). A reader of ADR-0017 alone cannot tell which sentence of its Decision is not in force.
- Fix belongs in: the unwritten superseding record; meanwhile decisions/ADR-0017.md (a dependent entry and status note) and decisions/README.md
- Severity: Medium
- Confidence: high
- Already on the corpus's own lists: G11 open list items 6 and 50 ("The ADR-0017 supersession", unwritten, as at G9)
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0017.md:11-13, 37-38, 154; decisions/ADR-0023.md:12-14, 79, 148; decisions/README.md:30; decisions/ADR-0008.md:10; decisions/ADR-0018.md:83-86. `grep -n '0023\|primacy\|revers' decisions/ADR-0017.md` finds line 154 only. The unwritten supersession is on the open list, as the reader says (checkpoints/topak-genesis-checkpoint-G9-2026.10.02.md:240, 284); the part not listed is the missing mark on ADR-0017's header and in the index.

### A-10: ADR-0022 says §6's confinement obligation is both "undelivered" and "discharged", so the condition ADR-0015 hangs its strongest claim on has no readable state
- Against: decisions/ADR-0022.md:12 (and decisions/ADR-0022.md:247, decisions/ADR-0022.md:307, decisions/ADR-0015.md:80)
- Basis: in force
- Claim: "**§6 is not ratified and remains Proposed.** The confinement obligation is undelivered, so every Build containment theorem stays conditional on it and Build principals are `Mediated`, not `Contained`."
- Why wrong: decisions/ADR-0022.md:247 (B10): "ADR-0034 also discharges **§6's obligation for Build**". decisions/ADR-0022.md:307 (B30): "**§6's obligation is discharged for Run**, as B10 discharged it for Build." §6's own text, Proposed and revised in place, says both at once (lines 125-133): "**As a specification it is discharged** ... **No lease has met it.**", and still says of Run (lines 122-123) "until it is paid Run principals are `Mediated` at every rung", which B30 says has been paid. The bottom Status note says (lines 224-225) "§6 owes its debt to a mechanism that does not exist, and no record can discharge it; only a sandbox can." ADR-0015's in-force consequence is conditional on exactly this (decisions/ADR-0015.md:80-82): "Once the confinement obligation (ADR-0022 §6) is discharged, that position is stronger than Moon & Varshney's ...; until then the two are identical in strength". Read with B10 and B30 the antecedent holds; read with the Status note and "No lease has met it" it does not. The narrative has to supply the reading (narrative/theory-of-operation.md:925-926).
- Fix belongs in: decisions/ADR-0022.md (header Status note; §6, which is Proposed text); decisions/ADR-0015.md if "discharged" there means the mechanism half
- Severity: Medium
- Confidence: high
- Already on the corpus's own lists: G11 open list item 1 (the sandbox gap); the conflicting wording is not listed.
- **Verifier:** confirmed with correction
- **Verifier's correction:** §6 does not say both at once. Its R3 paragraph (decisions/ADR-0022.md:125-133) separates a specification half, discharged, from a mechanism half, "No lease has met it", so a state is readable there and it is the one the narrative gives. That paragraph is Proposed text. The conflict is among the in-force texts: the header's "undelivered" (12-14) and the bottom note's "no record can discharge it; only a sandbox can" (224-225) against B10 (247), B30 (307) and decisions/ADR-0034.md:82-83, "this record discharges §6 for it". §6's Run sentence (122-123) is stale since B30.
- **Verifier's evidence:** decisions/ADR-0022.md:12-17, 111-133, 217-225, 247-248, 307; decisions/ADR-0034.md:82-83; decisions/ADR-0015.md:79-84; narrative/theory-of-operation.md:923-927.

### A-11: ADR-0022 §6 says its discharge (clauses P1, P2, P3, P6) is necessary for `Contained`, but ADR-0034 §4 defines `Contained` over P3 to P5 only
- Against: decisions/ADR-0022.md:131 (and decisions/ADR-0034.md:229)
- Basis: Proposed
- Claim: "Discharge is necessary for `Contained` and not sufficient: ADR-0034 §4 adds the provenance conjuncts, which this section does not state."
- Why wrong: §6 defines discharge by four clauses (decisions/ADR-0022.md:126-128): "egress by P1, the filesystem by P2, the shell by P3, and every path to the artifactory but `Submit` by P6", for a principal "under a profile that meets those clauses". decisions/ADR-0034.md:229, in force: "the lease's profile meets **P3–P5**: no launcher, Wasm tools only, inference inside". The reference computes the same thing (mechanism/GAPS-AND-ASSUMPTIONS.md:98: "a registered profile meeting P3–P5 for the alphabet"). A profile may declare any clause `fail` (decisions/ADR-0036.md:75), so by ADR-0034's text a lease whose profile fails P1, P2 or P6 and passes P3 to P5 satisfies the profile conjunct of `Contained` without §6's discharge. Either `Contained` omits the egress and filesystem clauses, or "necessary" is unsupported. The R3 note concedes the map is the drafter's (decisions/ADR-0022.md:253-254): "ADR-0034 does not state it as a map."
- Fix belongs in: decisions/ADR-0034.md §4 or decisions/ADR-0022.md §6, whichever the custodian reads as right
- Severity: Medium
- Confidence: medium
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0022.md:125-133, 253-254; decisions/ADR-0034.md:70-80 (seven clauses), 224-234 (§4 names P3-P5 only); `grep -n 'P3–P5\|P1–P\|P1, P2' decisions/ADR-0034.md` finds no sentence making P1, P2 or P6 a condition of `Contained`; mechanism/GAPS-AND-ASSUMPTIONS.md:98; decisions/ADR-0036.md:75, 189-197.

### A-12: ADR-0010's decision sentence on refinement is contradicted by ADR-0030 and by the narrative, and those two disagree about whether it "stays true"
- Against: decisions/ADR-0010.md:25 (and decisions/ADR-0030.md:116, narrative/theory-of-operation.md:691)
- Basis: in force
- Claim: "Operational bundles remain versioned parameters, admissible only if they refine the floor : they may subtract authority, never add it. Refinement (`bundle ⊑ floor`) is decided at promotion time as a Build obligation."
- Why wrong: decisions/ADR-0030.md:116-117: "A bundle whose text permits more than the floor is inert there, not inadmissible. ADR-0010's decision text stays true: refinement is still discharged at promotion, now by construction." narrative/theory-of-operation.md:691-692: "it is no longer something a bundle can fail, and nobody has to decide it at promotion." "Not inadmissible" contradicts "admissible only if they refine the floor"; "nobody has to decide it at promotion" contradicts "decided at promotion time" and also ADR-0030's "still discharged at promotion". The narrative's own amendment test (lines 792-794) is that a record changes "only where its decision becomes false". ADR-0010's History still lists as unchanged (decisions/ADR-0010.md:93-94) "refinement is decided at promotion". ADR-0016 §5 inherits the superseded mechanism by name (decisions/ADR-0016.md:126): "inherits refinement-at-promotion".
- Fix belongs in: decisions/ADR-0010.md (a dependent entry for ADR-0030) or narrative/theory-of-operation.md §3.1, depending on which statement stands
- Severity: Medium
- Confidence: medium
- Already on the corpus's own lists: no (S6-16 in narrative §14 disposes of the stale consequences, not of this decision sentence)
- **Verifier:** confirmed with correction; severity Low (reader: Medium)
- **Verifier's correction:** ADR-0010 against ADR-0030 is not an open conflict. ADR-0030 (decisions/ADR-0030.md:115-119, in force) rules on this decision sentence: "ADR-0010's decision text stays true ... neither record changes". It reads ⊑ of the composed decision, under which every bundle refines and none is inadmissible. So "contradicted by ADR-0030" and "on the corpus's own lists: no" do not stand. What stands is narrower: the narrative's "nobody has to decide it at promotion" (691-692) is worded against ADR-0010's "decided at promotion time" (25-27) and ADR-0030's "still discharged at promotion" (117), while the narrative elsewhere keeps the decision text true (792-794, 2257). A wording matter in the living document.
- **Verifier's evidence:** decisions/ADR-0010.md:25-27, 93-94; decisions/ADR-0030.md:115-119; narrative/theory-of-operation.md:691-692, 697-698, 792-794, 2257; process/NARRATIVE-LOG-2026.09.15.md:39 (S6-16 is the "verified rather than promoted" consequence, as the reader says).

### A-13: ADR-0022 §4 prescribes a refinement procedure that ADR-0030 says does not exist and the narrative says was retired, with no amendment
- Against: decisions/ADR-0022.md:100 (and decisions/ADR-0030.md:49, narrative/theory-of-operation.md:168)
- Basis: in force
- Claim: "Refinement under ADR-0010 must therefore be decided over **variants with symbolic parameters** : Rego predicates on action type plus reference prefix, checked by SMT : not by enumerating instances."
- Why wrong: decisions/ADR-0030.md:47-49 quotes the same procedure and says "**That tool does not exist, and cannot be built cheaply.**" narrative/theory-of-operation.md:168-169: "Earlier revisions said Rego predicates checked by an SMT solver; that needed a mechanized Rego semantics nobody has, and ADR-0030 retired it." ADR-0022's only amendment from ADR-0030 is A1, which changes §7 (decisions/ADR-0022.md:245); `grep -n '0022' decisions/ADR-0030.md` shows no reference to §4. §4 is Accepted text (status line: "§1–§5, §7, §8 only").
- Fix belongs in: decisions/ADR-0022.md (§4, by amendment or dependent entry)
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0022.md:100-103; decisions/ADR-0030.md:47-49; narrative/theory-of-operation.md:166-169. `grep -n '0022' decisions/ADR-0030.md` has no reference to §4; `grep -n -i 'SMT\|Rego\|0030' decisions/ADR-0022.md` shows no mark at §4 (only 101-102 themselves, and A1 at §7). ADR-0030:115-119 disposes ADR-0010 and ADR-0024, not ADR-0022.

### A-14: The narrative says erasure's quorum predicate is "checked in TLA+"; no module states one
- Against: narrative/theory-of-operation.md:799 (and spec/NonComposition.tla:64)
- Basis: living document
- Claim: "**Erasure** (ADR-0006) destroys authority-bearing evidence, and stays a **floor exception**: a carve-out inside the verified object, with a quorum predicate checked in TLA+."
- Why wrong: `grep -l -i 'eras' spec/*.tla` returns Correlator, Coupling_live, Emergency, Emergency_live, NonComposition, NonComposition_A1, RulesFloorBase and Workflow (with their proof modules). In the module that models the erasure event for ADR-0013 the action is guarded only by the envelope, with no roster or quorum conjunct: spec/NonComposition.tla:64 "Erase == /\ \E S \in SUBSET retained :", and lines 65-66 hold only "/\ S # {}" and "/\ \A r \in S : Erasable(r)". `grep -n -i 'X2\|eraseRoster\|erasureRoster\|eraseQuorum' spec/*.tla` returns nothing. The quorum appears only as an input the floor reads, floor/proposed/emergency-floor.cedar:210: "when { context.erasureQuorum };". What is checked is non-composition (NC-1, NC-2), which ADR-0013 §6 scopes itself (decisions/ADR-0013.md:166-167): "This is non-composition and reachability, not proof". ADR-0010's tangential 3 asked for "their quorum predicates proven" (decisions/ADR-0010.md:65); for erasure nothing delivers it, and the reference does not implement erasure at all (mechanism/GAPS-AND-ASSUMPTIONS.md:131).
- Fix belongs in: narrative/theory-of-operation.md §3.3 (or a module, if the predicate is to be checked)
- Severity: Medium
- Confidence: medium
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** narrative/theory-of-operation.md:799-800. Absence: `grep -n -i 'X2\|eraseRoster\|erasureRoster\|eraseQuorum' spec/*.tla` empty; `grep -n -i 'eras' spec/*.tla | grep -i 'quorum\|roster'` finds only spec/Emergency_proof.tla:138, a break-glass invariant. spec/NonComposition.tla:64-71 and spec/NonComposition_A1.tla:89-96 guard Erase by the envelope alone; in spec/Emergency.tla:165-169 Erase is a mutation. floor/proposed/emergency-floor.cedar:208-210; decisions/ADR-0013.md:72-75, 166-168; decisions/ADR-0010.md:63-66; mechanism/GAPS-AND-ASSUMPTIONS.md:131.

### A-15: ADR-0018 and ADR-0020 still list raw-emission retention as unassigned, and ADR-0020 still says cognitive payload stays out of round topics, after ADR-0037 §3 decided both
- Against: decisions/ADR-0020.md:115 (and decisions/ADR-0018.md:126, decisions/ADR-0037.md:165)
- Basis: in force
- Claim: "**Raw emission retention** (shared with ADR-0018). Retaining it allows after-the-fact verification that the typed lift was faithful; not retaining it shrinks the erasure surface. Between ADR-0003 and ADR-0006, and still unassigned."
- Why wrong: decisions/ADR-0037.md:165-166, in force since Batch 12: "**Raw emission is retained at the archetype** ⟨R2⟩. At the archetype, the Thinker's raw emission is written to its round topic beside the typed action it decoded to, as cognitive payload under the same ACL (0003.3)". ADR-0004 received the dependent entry (decisions/ADR-0004.md:50); ADR-0020 has none, and ADR-0018's B12 row (decisions/ADR-0018.md:151) covers the Reader bullets only and leaves its own open item (lines 126-128, "currently unassigned"). ADR-0020's third property (decisions/ADR-0020.md:65-66) "Less cognitive payload in round topics means ... ADR-0006's obligations get smaller" now runs against a decision that adds cognitive payload to every archetype round topic; ADR-0042 says so of its own records (decisions/ADR-0042.md:280: "Payloads on the topic enlarge the erasure surface").
- Fix belongs in: decisions/ADR-0020.md and decisions/ADR-0018.md (dependent entries for ADR-0037 §3)
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed with correction
- **Verifier's correction:** Two points. ADR-0020 does not say cognitive payload stays out of round topics: it bars "cognitive intermediate state" (decisions/ADR-0020.md:48-49) and says "less cognitive payload" shrinks the blast radius (65-66). Raw emission is not barred, so that half is a strain on a consequence, not a contradiction. And the ADR-0018 entry is on a list of the corpus's own: ADR-0037's Open obligations name it as owed (decisions/ADR-0037.md:447; also :39). The two stale "unassigned" items stand.
- **Verifier's evidence:** decisions/ADR-0020.md:48-49, 65-66, 115-117, 127-128 (History: N1, E1); decisions/ADR-0018.md:126-128, 151; decisions/ADR-0037.md:39, 165-167, 447; decisions/ADR-0004.md:50. `grep -n '0037\|B12' decisions/ADR-0020.md` empty.

### A-16: ADR-0019's Decision still says decoding conformance is "legitimately a precondition"; the narrowing that makes it deny-only today sits in a History row that says no decision text changes, and uses "rung 1" unqualified on a different axis
- Against: decisions/ADR-0019.md:42 (and decisions/ADR-0019.md:123, decisions/ADR-0037.md:207)
- Basis: in force
- Claim: "makes conformance a decidable predicate over a signed artifact : legitimately a precondition, not merely evidence. This is the only new *admitting* check in the recent set."
- Why wrong: decisions/ADR-0037.md:207-208: "Until a rung attests inference, ADR-0019's "legitimately a precondition" has no rung to be one at, and the Persona field's admitting use is dormant." ADR-0019 records this only in its B12 row (line 123): "at rung 1 the logprobs are the guest's own report and the use-1 check may only deny ... No decision text changes", with no inline mark at use 1, where ADR-0018 got one for the same ratification (decisions/ADR-0018.md:79-81). ADR-0018's chain table still reads "Decoding attestation : may admit (ADR-0019)" (decisions/ADR-0018.md:64). The row's "rung 1" is ADR-0034's confinement rung, while the record's own "rung-gated" (line 37) and "ADR-0017's rung ordering" (line 67) are the provenance axis, where rung 1 is `Contained` (decisions/ADR-0017.md:45); decisions/ADR-0023.md:43 requires that ""Rung" is always qualified by its parameter", and the narrative warns the two are "numbered in opposite directions" (narrative/theory-of-operation.md:1724-1725).
- Fix belongs in: decisions/ADR-0019.md (inline annotation at use 1; the B12 row's wording)
- Severity: Low-Medium
- Confidence: medium
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0019.md:37, 42-44, 67, 123 (the file's only mention of B12 or ADR-0037: `grep -n 'B12\|0037' decisions/ADR-0019.md`); decisions/ADR-0037.md:203-208; decisions/ADR-0018.md:64, 79-81; decisions/ADR-0017.md:42-47; decisions/ADR-0023.md:43; narrative/theory-of-operation.md:1724-1725. The History row does carry the narrowing, and the finding says so; what it reports is the missing inline mark and the unqualified rung.

### A-17: ADR-0017 and ADR-0019 still depend on ADR-0008, which is superseded and not in force, and carry no dependent entry
- Against: decisions/ADR-0017.md:13 (and decisions/ADR-0019.md:14, decisions/ADR-0019.md:103, decisions/ADR-0008.md:14)
- Basis: in force
- Claim: "**Depends on:** ADR-0016 (Persona), ADR-0008 (Observer fault-domain independence)"
- Why wrong: decisions/ADR-0008.md:10 and :14: "**Status:** Superseded by ADR-0038 · 2026.09.29 ⟨B13⟩" and "The text below is kept as accepted; it is no longer in force." ADR-0017's text argues from it twice (lines 72 and 96: "the model-layer analogue of ADR-0008's fault-domain independence"; "Its defense is ADR-0008's, restated"). ADR-0019 lists it under Depends on (line 14) and keeps an open item about a quantity ADR-0038 retired (decisions/ADR-0019.md:103-104): "what an Observer on the logprob stream does to ADR-0008's replica count", against decisions/ADR-0038.md:132 "there is no Observer quorum". ADR-0021, Proposed at the time, was given the read-through (decisions/ADR-0021.md:214, R5); the two accepted records were not, and `grep -n 'ADR-0017\|ADR-0019' decisions/ADR-0038.md` finds no dependent entry for either.
- Fix belongs in: decisions/ADR-0017.md and decisions/ADR-0019.md (B13 dependent entries)
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0017.md:13, 72, 96; decisions/ADR-0019.md:14, 103-104; decisions/ADR-0008.md:10-14; decisions/ADR-0038.md:132, 256; decisions/ADR-0021.md:211, 214. `grep -n 'ADR-0017\|ADR-0019' decisions/ADR-0038.md` finds 244 and 276, neither a dependent entry; `grep -n '0008\|0038' decisions/ADR-0017.md decisions/ADR-0019.md` finds no ADR-0038.

### A-18: When a Run topic seals is stated three ways: on emit completion, when the principal finishes emitting, and when the lease ends
- Against: decisions/ADR-0021.md:101 (and decisions/ADR-0003.md:22, decisions/ADR-0042.md:157, narrative/theory-of-operation.md:946)
- Basis: in force
- Claim: "Run seals a topic when the principal finishes emitting."
- Why wrong: decisions/ADR-0042.md:157 and :180: "**A Run round ends when its lease ends, and the topic seals at the final sequence number.** The ordinary end is expiry." and "**The principal cannot end its own round.** There is no terminal variant (ADR-0040 §4) and no release." ADR-0003's clause, marked not supersedable alone (decisions/ADR-0003.md:52), still reads "locked on emit completion **[0003.2]**" (lines 22-23), and ADR-0003 has no dependent entry from ADR-0042 (its History holds C1, N1, A1, A2, B5, A3, B17 only). The narrative carries both: line 946 "sealed on emit completion" and lines 443-444 "**a Run round ends when its lease ends**, and a Run seat cannot abstain (ADR-0042 §5)". ADR-0021 and ADR-0042 were both ratified on 2026.09.30.
- Fix belongs in: decisions/ADR-0003.md (a dependent entry reading 0003.2 for Run) and decisions/ADR-0021.md §3; narrative §4.3
- Severity: Low-Medium
- Confidence: medium
- Already on the corpus's own lists: G11 open list item 108 touches the seal's order against the ending admit's record, not this wording.
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0021.md:101-103; decisions/ADR-0003.md:22-23, 52, 78-84 (History tags C1, N1, A1, A2, B5, A3, B17); decisions/ADR-0042.md:157-158, 180, 278; narrative/theory-of-operation.md:443-444, 946. `grep -n '0042\|0040' decisions/ADR-0003.md decisions/ADR-0021.md` empty; ADR-0042 cites 0003.2 as a source (line 3) and does not restate it.

### A-19: ADR-0015 says in its Consequences that ADR-0013 is Proposed and unratified, and in its Status note that ADR-0013 §2 was ratified the same day
- Against: decisions/ADR-0015.md:92 (and decisions/ADR-0015.md:13)
- Basis: in force
- Claim: "ADR-0013 is Proposed and, since 2026.09.23, ratifiable in genesis with a confirmation-required marker"
- Why wrong: decisions/ADR-0015.md:12-13: "The classification of break-glass and erasure rests on ADR-0013 §2, ratified in Batch 4 the same day." decisions/ADR-0013.md:8: "**Status:** Accepted (genesis) · 2026.09.23". The bullet is headed (line 92) "**The privileged paths are classified against an unratified record**" and concludes that the C2 claim "is conditional on a record that can now be ratified alongside it", a state that ended on the day ADR-0015 was itself ratified.
- Fix belongs in: decisions/ADR-0015.md (an annotation on the consequence, as open item 1 received at B27)
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0015.md:92-97 (the quoted sentence is at 94-95, in the bullet that opens at the cited 92), 11-13; decisions/ADR-0013.md:8.

### A-20: ADR-0009's Status note still calls it an instance of the exception mechanism, which its own in-force A1 denies
- Against: decisions/ADR-0009.md:11 (and decisions/ADR-0009.md:39)
- Basis: in force
- Claim: "**Status note:** As an instance of the exception mechanism (ADR-0013)."
- Why wrong: decisions/ADR-0009.md:39-41: "It is no longer a verified-object exception: a quorum on the break-glass roster seats a named person on an emergency seat for one round, on an envelope prepared by promotion, and the floor carries no exception for it (ADR-0052)." decisions/ADR-0013.md:84: "It stops being an entry under §2." The status line's "C4 via 0013" rests on the same relation. ADR-0013's Context (decisions/ADR-0013.md:46-47, "Both are floor exceptions") and ADR-0010's tangential 3 (decisions/ADR-0010.md:63, "ADR-0009 and ADR-0006 become floor exceptions") are unannotated too; ADR-0010 has no Batch 34 entry.
- Fix belongs in: decisions/ADR-0009.md header
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0009.md:10-13, 38-43; decisions/ADR-0013.md:45-47, 83-84; decisions/ADR-0010.md:63-66. `grep -n 'B34\|0052' decisions/ADR-0010.md` empty.

### A-21: ADR-0023's A1 row says the amendment is not confirmation-required and, in the same sentence, that it carries C4; the status line shows C3 only
- Against: decisions/ADR-0023.md:149 (and decisions/ADR-0023.md:11)
- Basis: in force
- Claim: "Not confirmation-required on its own account: §6's schema gains a field and nothing accepted is reversed; C4 by the custodian's ratification, for the debt ADR-0034 §3.4 carried"
- Why wrong: decisions/ADR-0023.md:11: "**Status:** Accepted (genesis) · 2026.09.23 · confirmation required (ADR-0029 C3) ⟨B3⟩ ⟨B29⟩". The B29 row (line 165) names no criterion. If A1 carries C4, the status line and decisions/README.md:36 ("confirmation required: C3") omit it; if it does not, the row's second clause is wrong. A first quorum reading the status line would not review §6c under C4.
- Fix belongs in: decisions/ADR-0023.md (the A1 or B29 row, and the status line if C4 applies)
- Severity: Low-Medium
- Confidence: medium
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0023.md:11, 149 (row read in full), 165 (names no criterion); decisions/README.md:36. checkpoints/topak-genesis-checkpoint-G10-2026.10.05.md:239 counts A1 only as "added to records already marked" and names no criterion either.

### A-22: The index omits the confirmation-required marking for six accepted records whose status lines or the checkpoint carry it
- Against: decisions/README.md:60 (and decisions/README.md:42, :61, :62, :63, :65; checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:50)
- Basis: living document
- Claim: "Accepted (genesis) · Batch 34, 2026.10.05 (drafted 2026.10.03, after G9)"
- Why wrong: decisions/ADR-0047.md:19: "confirmation required (ADR-0029 C4; C2 for §3)". decisions/ADR-0048.md:15: "confirmation required (ADR-0029 C4, C3)". decisions/ADR-0049.md:15: "confirmation required (ADR-0029 C4; C2 for §5)". decisions/ADR-0050.md:20 and decisions/ADR-0052.md:20: "confirmation required (ADR-0029 C1, C3, C4; provisional under A4)". G11 line 50 lists 0047, 0048, 0049 and "0029 (for A2 and A4 only)" as confirmation-required and line 51 lists 0050 and 0052 as "provisional (confirmation required)"; README line 42 gives ADR-0029 as plain "Accepted (genesis)". Every other marked record in the index carries "confirmation required: …", and README lines 6-8 tell the reader that marked records "await the first post-bootstrap quorum". These rows are outside my primary range; they are reported because the index is my comparison text and it claims to give status as of G11.
- Fix belongs in: decisions/README.md
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed with correction
- **Verifier's correction:** Line number: ADR-0052's status line is at decisions/ADR-0052.md:18, not :20. For ADR-0029 the marking is in its Status note (decisions/ADR-0029.md:9, "for A2 only (C3)"), not on its status line (8).
- **Verifier's evidence:** decisions/README.md:6-8, 42, 60-63, 65 against decisions/ADR-0047.md:19, decisions/ADR-0048.md:15, decisions/ADR-0049.md:15, decisions/ADR-0050.md:20, decisions/ADR-0052.md:18, decisions/ADR-0029.md:8-9; checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:50-51. decisions/README.md:66 shows the index does carry the marker for ADR-0053, the next record.

### A-23: The index says its statuses are as of G11 and heads the column "Status at G8"
- Against: decisions/README.md:12 (and decisions/README.md:3)
- Basis: living document
- Claim: "| Record | Title | Status at G8 | Superseded by |"
- Why wrong: decisions/README.md:3-4: "**Status is as of Genesis Checkpoint G11 (2026.10.09)**". The column holds statuses that did not exist at G8 (2026.10.02), for example line 18 "Batch 27, 2026.10.04, after G9" and lines 69-81 "after G11".
- Fix belongs in: decisions/README.md
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/README.md:3-4, 12, 18, 66-81.

### A-24: G11 counts ADR-0018 as accepted "in part"; the record's status line and the index say nothing of the kind
- Against: checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:49 (and decisions/ADR-0018.md:11, decisions/README.md:31)
- Basis: in force
- Claim: "0018 (in part)"
- Why wrong: decisions/ADR-0018.md:11: "**Status:** Accepted (genesis) · 2026.09.12", with no Status note. decisions/README.md:31: "Accepted (genesis)". G11 line 59 says the counts are read "from each record's status line and status note together", and neither carries a partial marking; the reversal is recorded only in the body (decisions/ADR-0018.md:83-86) and the B12 row (line 151: "this record is not superseded"). The narrative repeats the checkpoint (narrative/theory-of-operation.md:26-27: "two of them in part"). "In part" also means two different things in the same table cell: for 0022 a section never ratified, for 0018 a clause reversed in effect.
- Fix belongs in: decisions/ADR-0018.md header (a status note), or the next checkpoint's §1.1
- Severity: Low
- Confidence: medium
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:49, 59, 70-92 (§1.2 does not explain the mark); decisions/ADR-0018.md:11-14, 83-86, 151; decisions/README.md:31; narrative/theory-of-operation.md:26-27. The mark dates from G5 (checkpoints/topak-genesis-checkpoint-G5-2026.09.29.md:40, 58: "reversed in part, not superseded"); G10:57 and G11:49 dropped the pointer to that explanation.

### A-25: ADR-0020 hands its forensic-floor constraint and a revisit trigger to ADR-0013, which gave the forensic floor to ADR-0028
- Against: decisions/ADR-0020.md:109 (and decisions/ADR-0020.md:85, decisions/ADR-0013.md:35)
- Basis: in force
- Claim: "ADR-0013 producing a forensic floor that cannot be discharged without reasoning."
- Why wrong: decisions/ADR-0013.md:35: "| Forensic floor (stop attribution, votes, issuances, legibility horizon) | **ADR-0028**: supersedable alone, and it is the MANAGE 2.4 resolution in its own right |". ADR-0013 will produce no forensic floor, so the trigger as written cannot fire, and the instruction at decisions/ADR-0020.md:85-86 ("This must be carried into ADR-0013 as a constraint on any forensic floor, not discovered there") names the wrong record. ADR-0028 depends on ADR-0020 (decisions/ADR-0028.md:18), so the substance may be carried; the pointers in ADR-0020 are not corrected by any History row.
- Fix belongs in: decisions/ADR-0020.md (erratum)
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0020.md:85-86, 109, 127-128 (History: N1, E1); decisions/ADR-0013.md:35; decisions/ADR-0028.md:17-18.

### A-26: ADR-0022's resolved follow-up names a variant that no longer exists and an exclusivity the floor no longer states
- Against: decisions/ADR-0022.md:206 (and floor/proposed/emergency-floor.cedar:105)
- Basis: in force
- Claim: "only a `thinker` seat holds `Draft`, `Invoke`, `Submit` or `RunInvoke`"
- Why wrong: the floor in force, floor/proposed/emergency-floor.cedar:105-115, has `@id("B10-only-thinkers-author")` forbid the actions "[Topak::Action::"Draft", Topak::Action::"Invoke", Topak::Action::"Submit", Topak::Action::"Actuate"]" when "principal.kind != "thinker" &&" and "!(principal.kind == "emergency" && action == Topak::Action::"Actuate")". `grep -rn 'RunInvoke' floor --include=*.cedar` returns nothing. `RunInvoke` was struck in ADR-0037 at B20 and the exclusivity was widened to the `emergency` seat at B34; the narrative has both (narrative/theory-of-operation.md:177-181). The same line's "(B10, B6)" are floor policy ids in a record whose History uses B6 and B10 as batch tags.
- Fix belongs in: decisions/ADR-0022.md (the B12 annotation in Requires follow-up)
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0022.md:204-207; floor/proposed/emergency-floor.cedar:103-115; `grep -rn 'RunInvoke' floor --include=*.cedar` empty; decisions/ADR-0037.md:226-228, 236-238, 246-247; checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:105-106 (the `emergency` stage is the floor in force); narrative/theory-of-operation.md:176-183.

### A-27: Amendment rows for ratified amendments still read "Pending" or "Marked inline and not applied"
- Against: decisions/ADR-0003.md:83 (and decisions/ADR-0003.md:12; decisions/ADR-0022.md:281)
- Basis: in force
- Claim: "**Pending** : drafted 2026.09.30."
- Why wrong: decisions/ADR-0003.md:12: "**Pending:** none. A1 and A2 ratified 2026.09.25 (Batch 5); A3 ratified 2026.09.30 (Batch 17)." The A1 and A2 rows of the same table were updated to "**Applied** : ratified 2026.09.25 (Batch 5)" (lines 80-81); A3's was not, and its row still says "Ratifies in one batch with ADR-0021", which B17 says did not happen. ADR-0022's A2 row (line 281) likewise reads "**Pending** : drafted 2026.09.29; ratifies with ADR-0040, or not at all" against the header's "A2 ratified 2026.09.30 (Batch 20)" (lines 19-20). The Batch 34 rows in ADR-0009 (line 62), ADR-0013 (line 249), ADR-0016 (lines 248-249) and ADR-0022 (line 306) each end their Change cell "Marked inline and not applied" and open their State cell "**Applied** ⟨B34⟩". A reader scanning State columns for what is pending gets two wrong answers; a reader of Change cells gets five.
- Fix belongs in: the History tables of decisions/ADR-0003.md, ADR-0009.md, ADR-0013.md, ADR-0016.md, ADR-0022.md
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** State cells read in full: decisions/ADR-0003.md:12, 80-84; decisions/ADR-0022.md:19-20, 281-282, 306; decisions/ADR-0009.md:62; decisions/ADR-0013.md:249; decisions/ADR-0016.md:248-249. Counts reproduce: two State cells read Pending, five Change cells end "Marked inline and not applied" beside an Applied state.

### A-28: ADR-0013's decomposition says six obligations and tabulates seven dispositions
- Against: decisions/ADR-0013.md:29
- Basis: in force
- Claim: "Since 09.12, this record had accumulated six obligations. The decomposition test split them:"
- Why wrong: the table that follows (decisions/ADR-0013.md:31-39) has seven rows: grant-authorization model with exception mechanism and count bound; non-composition properties; forensic floor; degeneracy composition; break-glass grant TTL; break-glass × promotion and × issuance; demand type 5. Its first row bundles three items, so no reading of the rows gives six. One row is also stale against §1's A1: "Break-glass grant TTL | **ADR-0026 R8 (candidate).**" (line 37) against "ADR-0026's R8 is withdrawn (ADR-0026 W1)" (lines 65-66).
- Fix belongs in: decisions/ADR-0013.md
- Severity: Low
- Confidence: medium
- Already on the corpus's own lists: no
- **Verifier:** confirmed with correction
- **Verifier's correction:** "No reading of the rows gives six" is too strong. The first row is the record's own subject ("Stays (§1-§3)"), and the six rows after it are six obligations added to it, which is one reading of "accumulated six". Six against seven rows is an unexplained count, not a miscount that can be shown. The stale row stands: line 37, "ADR-0026 R8 (candidate)", against 65-66, "R8 is withdrawn".
- **Verifier's evidence:** decisions/ADR-0013.md:29-39 (seven rows), 65-66. `grep -rn -i 'six obligations' --include=*.md .` finds this line and no list of the six anywhere.

### A-29: ADR-0013's A1 History row and open obligations describe a state its applied A1 text has left, and the record's evidence claims are all of the predecessor model
- Against: decisions/ADR-0013.md:249 (and decisions/ADR-0013.md:66, decisions/ADR-0013.md:192)
- Basis: in force
- Claim: "NC-1 and NC-2 are unchanged in what they require; `spec/NonComposition.tla`, cited by digest, owes a successor where it models X1."
- Why wrong: the applied text, decisions/ADR-0013.md:66-68: "§4's NC-1 and NC-2 are restated for a record per activation in `spec/NonComposition_A1.tla` (2026.10.05; ADR-0052 R5), with a third mutation". The row was not brought to the text it describes. Open obligations still carry (line 192) "Confirm that R6 = 2 is not already at its bound for known future exceptions" against §3's "the count is 1" (line 83). §4's status "**Drafted and checked**", §6's run and digest (`119f9a7e878f8929`, which `sha256sum spec/NonComposition.tla` confirms) and B25's 58 proved obligations (confirmed at spec/NonComposition-proof-results-2026.10.02.txt:10, "All 58 obligations proved.") are all of the module in which break-glass is one invocation that stays active for ever (spec/NonComposition.tla:47-51), the X1 shape A1 retires. The record gives no digest, results file or outcome for the successor; those are in decisions/ADR-0052.md:212-217 only.
- Fix belongs in: decisions/ADR-0013.md (History row, open obligations, a pointer to the successor's results)
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: G11 open list item 90 (no binding-table row for `NonComposition_A1`)
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0013.md:66-68, 83, 135, 192, 223, 249. `sha256sum spec/NonComposition.tla` gives 119f9a7e878f8929..., as §6 cites; spec/NonComposition-proof-results-2026.10.02.txt:10; spec/NonComposition.tla:47-71 (`bgActive` is set once and never reset: `grep -n bgActive`). `grep -n 'NonComposition_A1\|d1e9113480d016bb' decisions/ADR-0013.md` finds line 67 only; decisions/ADR-0052.md:212-219.

### A-30: ADR-0005 still lists the narrative as an open obligation and points at a section that now holds something else
- Against: decisions/ADR-0005.md:111 (and decisions/ADR-0005.md:106, narrative/theory-of-operation.md:938)
- Basis: in force
- Claim: "**The narrative.** The Theory of Operation §5 still says the quarantine-gate question gates this record and that it is Proposed. It is frozen between checkpoints and takes this record's state at the next one."
- Why wrong: narrative/theory-of-operation.md:937-940: "Revision 13 said the residual waited on whether the Observer's quarantine gate is a modeled event, and that the question gated ADR-0005. **It no longer does**: ... **ratified 2026.10.04 (Batch 27, C4)**." Two checkpoints have passed. The passage is in §4.2 "What Kafka is" (line 929); §5 is "Detection" (line 1028). The same stale pointer is in the obligation above it (decisions/ADR-0005.md:106-107): "The Theory of Operation §5 already does", where what K means is now at narrative lines 71-73 and §4.2. The header's Status note (line 11) also still reads "pending the Observer quarantine-gate question".
- Fix belongs in: decisions/ADR-0005.md (a dependent entry closing the obligation)
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no (G10 item 5 records ADR-0005 as discharged)
- **Verifier:** confirmed with correction
- **Verifier's correction:** Drop the remark on the header. The Status note's "pending the Observer quarantine-gate question" (decisions/ADR-0005.md:11) is followed at 12-14 by "R1 (2026.10.04) answers the hold ... the question no longer gates this record", so it is reconciled in place. The two open obligations (106-107, 111-112) stand as stale, with the wrong section number.
- **Verifier's evidence:** decisions/ADR-0005.md:10-14, 106-112; narrative/theory-of-operation.md:929, 936-942, 1028; checkpoints/topak-genesis-checkpoint-G10-2026.10.05.md:327.

### A-31: ADR-0021 calls ADR-0043 Proposed and says in its header that it is still waiting, though both were settled on its ratification day
- Against: decisions/ADR-0021.md:176 (and decisions/README.md:56; decisions/ADR-0021.md:25)
- Basis: in force
- Claim: "Run's Observer has its own reads under ADR-0043 (Proposed)."
- Why wrong: decisions/README.md:56 gives ADR-0043 as "Accepted (genesis); confirmation required: C4", and G11 line 50 lists 0043 as accepted. In the header's Blocked on field (decisions/ADR-0021.md:25): "this record waits on the ADR-0008 read-through its Status note names ⟨B17⟩", against the status line (line 11) "Accepted (genesis) · 2026.09.30" and R5, which is that read-through.
- Fix belongs in: decisions/ADR-0021.md (dependent entry for ADR-0043's ratification; the Blocked on field)
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0021.md:11-12, 22-26, 175-177, 213-215; decisions/ADR-0043.md:11; decisions/README.md:56. `grep -n '0043' decisions/ADR-0021.md` finds line 177 only.

### A-32: A sentence of ADR-0024 is given in quotation marks twice without a word the source has
- Against: decisions/ADR-0023.md:139 (and narrative/theory-of-operation.md:1706, decisions/ADR-0024.md:160)
- Basis: in force
- Claim: ""a promotion degeneracy is a mechanism release, an anchor degeneracy is a declaration""
- Why wrong: decisions/ADR-0024.md:160: "**a promotion degeneracy is a mechanism release, and an anchor degeneracy is a". ADR-0023's own §6a quotes it with the "and" (decisions/ADR-0023.md:47); its R4 note (line 139) and the narrative (lines 1706-1707) drop it inside the quotation marks. The meaning is unchanged.
- Fix belongs in: decisions/ADR-0023.md (R4 note) and narrative/theory-of-operation.md §8.1
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0024.md:160-161; decisions/ADR-0023.md:47 (with "and"), 139 (without); narrative/theory-of-operation.md:1706-1707 (without).

### A-33: ADR-0023 §6c says the declared rung is "per seat and not per deployment"; the clause it cites, ADR-0022 §6 and the narrative say "the deployment's declared rung", and narrative §8 does not carry §6c at all
- Against: decisions/ADR-0023.md:51 (and decisions/ADR-0034.md:228, decisions/ADR-0022.md:129, narrative/theory-of-operation.md:134)
- Basis: in force
- Claim: "The rung is per seat and not per deployment"
- Why wrong: decisions/ADR-0034.md:228, in force and not amended at B29: "`p` holds a live lease at rung ≥ 1, granted on an **Attested** verdict at the deployment's declared rung;". decisions/ADR-0022.md:129: "granted on an Attested verdict at the deployment's declared rung". narrative/theory-of-operation.md:134-135: "granted on an Attested verdict at the deployment's declared rung". §6c says its rung "is ADR-0034 §3.4's "declared rung"", so the same quantity is per deployment in three texts and per seat in one. The narrative's restatement of ADR-0023's schema (lines 1701-1703) lists kind, parameter, values, premises, theorems, type changes, mitigation and composition note and has no mention of §6c, in force since Batch 29; `grep -n '6c' narrative/theory-of-operation.md` returns nothing.
- Fix belongs in: decisions/ADR-0034.md §3 and §4 (a dependent entry) and narrative/theory-of-operation.md §2.3, §8.1
- Severity: Low
- Confidence: medium
- Already on the corpus's own lists: G11 open list item 64 (the deployment declaration template is open; §6c in force)
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0023.md:51, 149 (A1's Source cell quotes "the deployment's declared rung" and says no record said where it is declared); decisions/ADR-0034.md:189, 228; decisions/ADR-0022.md:129; narrative/theory-of-operation.md:134-135, 1701-1703. `grep -n '6c\|0023 A1' narrative/theory-of-operation.md` empty; narrative:2058 is the one place that says "the declared rung per seat".

### A-34: Accepted records hand open questions to ADR-0014 under a description the index does not give it
- Against: decisions/README.md:27 (and decisions/ADR-0016.md:220, decisions/ADR-0017.md:138, decisions/ADR-0021.md:148, decisions/ADR-0022.md:181, decisions/ADR-0012.md:30)
- Basis: in force
- Claim: "| ADR-0014 | : | Reserved, no file (the per-class floor question) | |"
- Why wrong: decisions/ADR-0016.md:220-221: "Who may propose a Persona is the same shape of question as ADR-0014's floor authorship, and probably belongs to it rather than here." decisions/ADR-0017.md:138-139: "**Rung declaration authority** : who may declare a deployment at a given rung. Same shape as ADR-0014." decisions/ADR-0021.md:148-149: "Gives ADR-0014 a provenance object to reason about: "who may propose a floor change"". decisions/ADR-0022.md:181-182: "The per-tool hermeticity obligation is currently unowned, and it wants either an owner in ADR-0014 or a gate alongside floor fitness." decisions/ADR-0012.md:30-31: "see the floor-authorship record (item 4 under ADR-0010)". decisions/ADR-0024.md:14: "**Narrows:** ADR-0014, to proposal eligibility". The index and the open list (G9 item 9) reserve the number for the per-class question, ADR-0010's tangential 5; the records address tangential 4, floor authorship and proposal authority, which no file holds. Registry authority and rung-declaration authority are thereby filed against a record that does not exist and is not reserved for them.
- Fix belongs in: decisions/README.md (what ADR-0014 is reserved for), or dependent entries re-homing each open item
- Severity: Low
- Confidence: medium
- Already on the corpus's own lists: G11 open list item 9 (the per-class floor question only)
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/README.md:27; decisions/ADR-0010.md:67-72 (tangentials 4 and 5); decisions/ADR-0012.md:30-31; decisions/ADR-0016.md:220-221; decisions/ADR-0017.md:138-139; decisions/ADR-0021.md:148-149; decisions/ADR-0022.md:181-182; decisions/ADR-0024.md:14. The description moved: checkpoints/topak-genesis-checkpoint-G1-2026.09.15.md:63, 257 has 0014 as "Floor authorship and change control"; from checkpoints/topak-genesis-checkpoint-G2-2026.09.23.md:176 to G9:243 it is the per-class question.

### A-35: ADR-0002's decision and ADR-0010's consequence give opposite ends to Build's trust regress
- Against: decisions/ADR-0002.md:38 (and decisions/ADR-0010.md:51)
- Basis: in force
- Claim: "and the trusting-trust regress terminating at a declared axiom set rather than a proof."
- Why wrong: decisions/ADR-0010.md:51-52: "Build's regress terminates on a verified artifact rather than a declared axiom set : the floor is the one artifact verified rather than promoted." Both were accepted on 2026.09.12 and both are in force; ADR-0002's sentence is Decision text and was left standing by A1, which rewrote the clause before it. The narrative presents them as "stages of one argument" (narrative/theory-of-operation.md:1425-1434) and S6-16 left ADR-0010 unamended; neither record points at the other on this.
- Fix belongs in: decisions/ADR-0002.md or decisions/ADR-0010.md (a dependent entry naming ADR-0025 and ADR-0026 as the present terminus)
- Severity: Low
- Confidence: medium
- Already on the corpus's own lists: no (narrative §7.6 acknowledges it)
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0002.md:36-39; decisions/ADR-0010.md:51-53; narrative/theory-of-operation.md:1425-1434 (reconciles them as stages, in the living layer only, as the reader says). `grep -n '0010' decisions/ADR-0002.md` empty; decisions/ADR-0010.md:28 is its one mention of ADR-0002 and is not on this point.

### A-36: ADR-0016 and ADR-0017 still state that Build's membrane has no effect stream, which ADR-0021 closed
- Against: decisions/ADR-0016.md:206 (and decisions/ADR-0017.md:106, decisions/ADR-0021.md:21)
- Basis: in force
- Claim: "and Build's membrane has no effect stream (09.12 checkpoint §1). This ADR does not create that open item but materially increases its weight."
- Why wrong: decisions/ADR-0021.md:21: "**Closes:** the open item "Build's membrane has no effect stream," raised in the 2026.09.12 Theory of Operation checkpoint §1." ADR-0021 has been Accepted since 2026.09.30 (line 11). ADR-0017 says the same in the present tense (lines 106-109: "Build's membrane has no effect stream (checkpoint §1). The archetype makes that open item substantially heavier"). Neither record has a B18 dependent entry, where the index (decisions/README.md:5-6) says a record gains one "when another record's ratification touches it".
- Fix belongs in: decisions/ADR-0016.md and decisions/ADR-0017.md (dependent entries)
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0016.md:205-207, 231-250; decisions/ADR-0017.md:106-109, 151-152; decisions/ADR-0021.md:11, 21; decisions/README.md:5-6. `grep -n '0021\|B18' decisions/ADR-0016.md decisions/ADR-0017.md` empty.

### A-37: ADR-0003 flags clause 0003.5 for resolution in ADR-0020; ADR-0020 does not take it up and the open list dropped it
- Against: decisions/ADR-0003.md:55 (and checkpoints/topak-genesis-checkpoint-G1-2026.09.15.md:255)
- Basis: in force
- Claim: "Authorization *to* replay and the scope *of* replay are different decisions; neither currently says which one governs. Flag for 0020."
- Why wrong: ADR-0020's Decision, properties, revisit triggers and Open section (decisions/ADR-0020.md:37-117) say nothing about replay authorization or 0003.5. G1 carried the item (line 255: "Replay authorization vs replay scope (clause 0003.5 overlaps 0020)"); `grep -n -i 'replay authoriz' checkpoints/*.md` finds it in G1 only, and G9's numbered list (checkpoints/topak-genesis-checkpoint-G9-2026.10.02.md:233-324) has no such item. The flag is still standing in an accepted record with nothing tracking it.
- Fix belongs in: decisions/ADR-0020.md or the next checkpoint's open list
- Severity: Low
- Confidence: medium
- Already on the corpus's own lists: no (on G1's list, absent from G9 to G11)
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0003.md:30, 55; checkpoints/topak-genesis-checkpoint-G1-2026.09.15.md:255. Absence: `grep -n -i 'replay authoriz' checkpoints/*.md` finds G1:255 only; `grep -n -i 'authori\|0003\.5' decisions/ADR-0020.md` empty; `grep -rn '0003\.5' decisions checkpoints narrative/theory-of-operation.md narrative/glossary.md` finds ADR-0003 and G1 only.

### A-38: The narrative says ADR-0003 A2 carries the only amendment-scoped marking in the corpus, and elsewhere names three more
- Against: narrative/theory-of-operation.md:962 (and narrative/theory-of-operation.md:27)
- Basis: living document
- Claim: "A2 is confirmation-required under C1, the only marking in the corpus scoped to one amendment."
- Why wrong: narrative/theory-of-operation.md:27-28: "four of them for a part only: ADR-0003, ADR-0029 and ADR-0031's C2 for particular amendments, and ADR-0053 for one route." Lines 257-258: "under C2 for A1 only." G11 line 50: "0029 (for A2 and A4 only)", "0031 (C2 for A1 only, beside its C1)".
- Fix belongs in: narrative/theory-of-operation.md §4.3
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed with correction
- **Verifier's correction:** The count. The narrative names two more records marked for particular amendments, ADR-0029 and ADR-0031 (27-28, 257-258, 1805). The third part-only marking it names, ADR-0053's, is for a route and not for an amendment.
- **Verifier's evidence:** narrative/theory-of-operation.md:27-28, 257-258, 962-963, 1805; decisions/ADR-0031.md:9; checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:50.

### A-39: ADR-0023 says the TLA+ theorems "are proved" about the archetype; the narrative's restatement says "checked"
- Against: decisions/ADR-0023.md:72 (and narrative/theory-of-operation.md:1713)
- Basis: in force
- Claim: "Nobody ships the archetype; every real deployment is degenerate, so the TLA+ theorems are proved about an unshipped configuration."
- Why wrong: narrative/theory-of-operation.md:1713: "**Nobody ships the archetype.** The TLA+ properties are checked against an unshipped configuration." The corpus reserves *proved* for TLAPS (narrative lines 50-52), and the sentence was ratified on 2026.09.23, before any proof module existed (the earliest proof results under `spec/` are dated 2026.10.02, for example spec/NonComposition-proof-results-2026.10.02.txt). The two layers use two of the four evidence words for one claim.
- Fix belongs in: decisions/ADR-0023.md (erratum) or narrative/theory-of-operation.md §8.1
- Severity: Low
- Confidence: medium
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0023.md:11, 72; narrative/theory-of-operation.md:50-53, 1713. The earliest `spec/*-proof-results-*` files are dated 2026.10.02 (`ls spec | grep proof-results`).

### A-40: The narrative says three bullets of ADR-0018's Reader scope correction are reversed; the records say two are struck and the third survives
- Against: narrative/theory-of-operation.md:1764 (and decisions/ADR-0018.md:151, decisions/ADR-0037.md:219)
- Basis: living document
- Claim: "**ADR-0018's Reader scope correction**, three bullets, reversed by ADR-0037 §3 (§2.8)."
- Why wrong: decisions/ADR-0018.md:151: "the first two bullets struck, the third annotated, a note added". decisions/ADR-0037.md:219-221: "The first (the Reader carries its own Persona) is reversed. The second (distinctness applies to it) no longer has anything to apply to. The third (Reader output is deny-only) survives for substitution detection".
- Fix belongs in: narrative/theory-of-operation.md §8.3
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** narrative/theory-of-operation.md:1764-1765; decisions/ADR-0018.md:76-81, 151; decisions/ADR-0037.md:219-222. The same loose count is in checkpoints/topak-genesis-checkpoint-G5-2026.09.29.md:30, 58.

### A-41: ADR-0015's erratum E2 is marked ratified with no batch or ratification row, and the header's list of ratified errata omits it
- Against: decisions/ADR-0015.md:129 (and decisions/ADR-0015.md:15, decisions/ADR-0015.md:128)
- Basis: in force
- Claim: "**Applied** : ratified 2026.09.25"
- Why wrong: the header (line 15) accounts for one erratum: "E1 ratified 2026.09.25 (Batch 8)." The B8 row (line 128) says "**E1 ratified 2026.09.25** ... in Batch 8 with ADR-0031 E1" and "E1 adds nothing to be confirmed"; it does not name E2. E2 changes a Consequences sentence about the record's strongest claim on the authority of a "custodian scrub instruction 2026.09.25" and has no batch, no B row and no header mention, where the other applied errata in ADR-0002, ADR-0018, ADR-0019 and ADR-0020 each name their batch.
- Fix belongs in: decisions/ADR-0015.md (header Pending line; a ratification row for E2)
- Severity: Low
- Confidence: medium
- Already on the corpus's own lists: no
- **Verifier:** confirmed with correction
- **Verifier's correction:** The missing batch is recorded and explained by the checkpoint: G4 lists "0015 E2 · 0029 A2" as ratified "After G3", 09.25, after G3's cut and in no batch (checkpoints/topak-genesis-checkpoint-G4-2026.09.28.md:26, 173, 285). So "no batch" is the state of record and not an omission. What stands is inside the record: its Pending line (decisions/ADR-0015.md:15) names E1 only, and no ratification row covers E2.
- **Verifier's evidence:** decisions/ADR-0015.md:15, 82, 128-129; checkpoints/topak-genesis-checkpoint-G3-2026.09.25.md:25, 166; checkpoints/topak-genesis-checkpoint-G4-2026.09.28.md:26, 173, 285.

