# Self review of 2026.11.11: reader D's findings in full

Reader D read Run and detection. Annex to `derived/topak-open-findings-register-2026.11.11.md`, Part III. Each block is the finding as the reader wrote it, against the tree at `bbda621`, followed by the verdict of a verifier that did not find it. Paths are relative to the repository root. A path a finding names as absent is written without backticks. Nothing here is ratified, and every reader and verifier is of the same model lineage as the drafter of the corpus.

39 reported: 29 confirmed, 10 confirmed with a correction, 0 dropped.

### D-1: ADR-0043 §2 still says only a `thinker` seat holds `Actuate`, and its table has three kinds; the text in force elsewhere gives an `emergency` seat `Actuate`
- Against: decisions/ADR-0043.md:104 (and decisions/ADR-0037.md:236 for the other side)
- Basis: in force
- Claim: "**Only a `thinker` seat holds `Actuate`.** It is Run's one variant that runs anything, and it joins `Draft`, `Invoke`"
- Why wrong: decisions/ADR-0037.md:236-238, applied at B34: "The table gains a kind: **`emergency`**, Run only, `Consult`, `Actuate`, `Report`" and "The sentence below then reads "only a `thinker` seat, or in Run an `emergency` seat for `Actuate`"; B10 names both." decisions/ADR-0041.md:162, applied at B34: "`B10-only-thinkers-author` reads "the seat's kind is not `thinker`, and, for `Actuate`, not `emergency`"." The floor in force agrees with those two: floor/proposed/emergency-floor.cedar:112-115 `principal.kind != "thinker" && !(principal.kind == "emergency" && action == Topak::Action::"Actuate")`. ADR-0043 §2's table (decisions/ADR-0043.md:92-96) lists `thinker`, `observer`, `grant` and nothing else, although decisions/ADR-0043.md:108 says "This table replaces the Run column of ADR-0037 §4" and ADR-0037 §4 now has `emergency` and `operator` rows. ADR-0043 carries a pending row for `orchestrator` (lines 98-102) but no amendment for the two kinds already in force; `grep -n "ADR-0043" decisions/ADR-0052.md` returns nothing. The proved invariant cited for this clause, `OnlyThinkersActuate` (spec/RunSeats.tla:82; decisions/ADR-0043.md:266), is marked "**holds**" against "ADR-0043 §2" in spec/theorem-premise-binding.md:75, and is false of the design in force.
- Fix belongs in: decisions/ADR-0043.md §2 (a dependent amendment, as ADR-0052 and ADR-0050 wrote into ADR-0037 §4), and the `OnlyThinkersActuate` row of spec/theorem-premise-binding.md
- Severity: Medium-High
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0043.md:92-96 (three kinds), :104 (quotation exact), :108; `grep -n -i emergency decisions/ADR-0043.md` empty, so no amendment carries the kind; decisions/ADR-0037.md:232-238 (A4, A3, applied B34); decisions/ADR-0041.md:162; floor/proposed/emergency-floor.cedar:112-115; checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:105 (that stage is in force); spec/RunSeats.tla:39, :45-48 (kinds thinker and observer only), :82; spec/theorem-premise-binding.md:75 (**holds**, against ADR-0043 §2; `grep -n -i emergency spec/theorem-premise-binding.md` empty); decisions/ADR-0043.md:266; `grep -n "ADR-0043" decisions/ADR-0052.md` empty. Wording only: in ADR-0037 §4 the two kinds are applied paragraphs under the table ("The table gains a kind"), not table rows.

### D-2: ADR-0041 §1 labels entries that are in force as "pending"
- Against: decisions/ADR-0041.md:62 (and decisions/ADR-0041.md:74, decisions/ADR-0041.md:83)
- Basis: in force
- Claim: "`X1-break-glass` *(pending ⟨A2⟩, not applied: retired)*" · "Id ⟨A1, pending⟩" · "Id ⟨A3, pending⟩"
- Why wrong: The same record's header, decisions/ADR-0041.md:19-21, says of A1, A2 and A3 each "ratified 2026.10.05 (Batch 34) and applied inline ⟨B34⟩", and its B34 row (decisions/ADR-0041.md:318) says "the text marked ⟨A1⟩, ⟨A2⟩, ⟨A3⟩ is in force as written". checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:105 reads "**The entries in force are G10's**: the `emergency` stage, `floor/proposed/emergency-floor.cedar`", and that stage has R5 to R7, C1 to C9 and no X1. A reader of §1 alone sees one amendment that really is pending (A4) marked the same way as three that are in force, and sees X1 as still a row of the floor. decisions/ADR-0041.md:52 also still reads "The Run half of the floor is six entries."
- Fix belongs in: decisions/ADR-0041.md §1
- Severity: Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed; severity Low-Medium (reader: Medium)
- **Verifier's evidence:** decisions/ADR-0041.md:52, :62, :74, :83 (quotations exact) against :19-21 and :318; floor/proposed/emergency-floor.cedar:170-190 (R5 to R7), :228-290 (C1 to C9), :201 (X1 only as a comment that it is retired); checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:105. Severity: the paragraphs directly above the two tables are already tagged ⟨A1⟩ ⟨B34⟩ (:67) and ⟨A3⟩ ⟨B34⟩ (:80), and §3 has ⟨A2⟩ ⟨B34⟩ "X1 is retired" (:154), so the stale markers are answered inside the record; the X1 row has no such tag beside it.

### D-3: Three status notes say C3 does not apply, while amendments applied at B34 say on their face that C3 is required; nothing resolves it
- Against: decisions/ADR-0043.md:14 (and decisions/ADR-0043.md:267; decisions/ADR-0042.md:17 and :333; decisions/ADR-0041.md:15 and :315)
- Basis: in force
- Claim: "C3 does not apply: §2 replaces a column ADR-0037 marked provisional" (ADR-0043) · "C3 does not apply: §2 tightens ADR-0039 §1 and reverses nothing" (ADR-0042) · "**C3 does not apply, by the custodian's decision at B20.**" (ADR-0041)
- Why wrong: decisions/ADR-0043.md:267, state of A1, Applied ⟨B34⟩: "**Confirmation required under C3** on the drafter's reading for §1: "nothing else reaches the Thinker" is ratified text and a fourth item changes it". decisions/ADR-0042.md:333, state of A1, Applied ⟨B34⟩: "**Confirmation required under C3** on the drafter's reading for §4, as ADR-0043 A1 is". decisions/ADR-0041.md:315, state of A2, Applied ⟨B34⟩: "**Confirmation required under C1 and C3**, as ADR-0052 is". The status lines were not changed (ADR-0043.md:11 "confirmation required (ADR-0029 C4)"; ADR-0042.md:13 "(ADR-0029 C4; C2 for §6)"; ADR-0041.md:12 "(ADR-0029 C1, C4)"). The three B34 rows (ADR-0041.md:318, ADR-0042.md:337, ADR-0043.md:269) say nothing on the criterion, and the debt ledger of the checkpoint that recorded Batch 34 adds no criterion for these three records (checkpoints/topak-genesis-checkpoint-G10-2026.10.05.md:237-245). A reader cannot tell whether the drafter's C3 reading was accepted, overruled or lost.
- Fix belongs in: the status lines and B34 rows of decisions/ADR-0041.md, ADR-0042.md and ADR-0043.md, and the next checkpoint's debt ledger
- Severity: Medium
- Confidence: medium
- Already on the corpus's own lists: no
- **Verifier:** confirmed with correction; severity Low-Medium (reader: Medium)
- **Verifier's correction:** The quotations and the unchanged status lines stand, but "nothing resolves it" and "accepted, overruled or lost" overstate. The drafter's C3 reading is carried on the parent records for the same reversals: ADR-0048's status line has C3 because "ADR-0043 §1 and ADR-0042 §4 call Run's ingress a closed list of three, and §2 makes it four", and ADR-0052's has C3 because "ADR-0041 §1 and §3 state X1; both are reversed"; G10's ledger rows for 0048 (C4, C3) and 0052 (C1, C3, C4) put both before the first quorum. What is missing is narrower: ADR-0041, ADR-0042 and ADR-0043 still say flatly "C3 does not apply" and do not carry "C3 for A1 (A2) only" on their own status lines, the form ADR-0029 uses for its A2.
- **Verifier's evidence:** decisions/ADR-0043.md:11, :14, :267, :269; decisions/ADR-0042.md:13, :17, :333, :337; decisions/ADR-0041.md:12, :15, :315, :318; decisions/ADR-0048.md:15-18; decisions/ADR-0052.md:18-20; checkpoints/topak-genesis-checkpoint-G10-2026.10.05.md:237-245 (rows 0048 at :242, 0052 at :245; no row for 0041 to 0043); decisions/ADR-0029.md:9 ("for A2 only (C3)").

### D-4: ADR-0051 rests "C3 does not apply" on the claim that a per-principal sequence number on denials was never decision text; ADR-0038 §3 is decision text and says it
- Against: decisions/ADR-0051.md:18 (and decisions/ADR-0038.md:105)
- Basis: Proposed
- Claim: "ADR-0038 finding 2's "a per-principal sequence number on denials is enough" was a finding and not decision text"
- Why wrong: decisions/ADR-0038.md:105-106, inside Decision §3, in force: "**Facts** from every cell in its domain: admits and denials with their principal, lease, epoch and per-principal sequence number (`mechanism/` G15's `topak-seq`, extended to denials, finding 2)". ADR-0042's Context quotes that sentence as what ADR-0038 §3 says (decisions/ADR-0042.md:53-54). ADR-0051 §5 then decides the opposite, decisions/ADR-0051.md:218: "**No sequence number is added**". So ADR-0051 changes a clause of an accepted record's read set, and its status note argues the criterion away on a reading of ADR-0038 that the text does not support. ADR-0038 carries no pending amendment for it (decisions/ADR-0038.md:19 "**Pending:** none.").
- Fix belongs in: decisions/ADR-0051.md status note and its debt against ADR-0038
- Severity: Medium
- Confidence: high
- Already on the corpus's own lists: no (G5 to G10 item 44 names the subject, not this reading)
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0051.md:17-19 (quotation exact), :218; decisions/ADR-0038.md:100 (§3 heading: the sentence is Decision text), :105-106, :240 (finding 2's own sentence), :19; decisions/ADR-0042.md:53-54; `grep -n 0051 decisions/ADR-0038.md` empty.

### D-5: ADR-0051 makes two correlators the archetype; ADR-0038, in force, makes it one or more, and ADR-0051 names no change to ADR-0038 for it
- Against: decisions/ADR-0051.md:287 (and decisions/ADR-0038.md:76)
- Basis: Proposed
- Claim: "| **D-0051-2** | Deployment | Correlators in a domain: two or more → one |"
- Why wrong: decisions/ADR-0038.md:76: "| **Correlator** | One or more `observer` seats that belong to no cell |", and decisions/ADR-0038.md:165: "| **D-0038-2** | Declaration | Correlators: 1 or more → 0 |". Under ADR-0038 a domain with one correlator is at the archetype; under ADR-0051 it is a declared degeneracy, and decisions/ADR-0051.md:393 says so: "**Two correlators are the archetype**". ADR-0051's debt against ADR-0038 is only "findings 1 to 3 answered, a dependent entry" (decisions/ADR-0051.md:33), and its status note says "**Every clause subtracts.**" and that C3 does not apply (decisions/ADR-0051.md:17-19). Raising an accepted record's archetype value is named nowhere in the record's header.
- Fix belongs in: decisions/ADR-0051.md (header, §9, §10's list of dependent entries) and a dependent entry in decisions/ADR-0038.md §1 and §7
- Severity: Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0051.md:287, :393, :33, :17-20, :293 (§10's dependent entries name findings 1 to 3 only); decisions/ADR-0038.md:76, :165; `grep -n 0051 decisions/ADR-0038.md` empty. ADR-0051's Deployment-position line (:22-23) does call "a single correlator" a degeneracy; it names no change to ADR-0038 §1 or D-0038-2, which is the finding.

### D-6: `FindingHasEvidence` and `HonestNeverCharged` hold in `Correlator.tla` because no correlator, honest or not, can report a finding whose condition is false; ADR-0051 §3 says the mechanism does not check findings
- Against: decisions/ADR-0051.md:314 (and spec/Correlator.tla:223)
- Basis: Proposed
- Claim: "Eight properties hold (2,285,708 states with"
- Why wrong: spec/Correlator.tla:221-224: `Report(c, s) == /\ s \in sends /\ s \notin marked[c]  /\ s.eff \/ Mut = "M_BARE"`. Every correlator in `Corrs`, including the one outside `Honest`, can report only when the fold fired. `Honest` restricts only `Pass` (spec/Correlator.tla:237). A false correlation finding exists in the module only as the mutation `M_BARE`, which spec/Correlator.tla:58-59 says "Must break FindingHasEvidence and HonestNeverCharged". The record specifies the opposite of that guard: decisions/ADR-0051.md:188 "**The mechanism does not check it before it takes effect**", and decisions/ADR-0051.md:388-389 "**`marked-past` counts misses against findings that may be false.** A Byzantine watcher can manufacture misses for the others in `W(p)`." So in the system the record describes, a dishonest correlator's bare finding charges an honest one, which is the trace `M_BARE` produces. §10's "Not met" paragraph (decisions/ADR-0051.md:327-330) lists what the module leaves out and does not list this assumption. The two properties are proved (lines 322-326) under a hypothesis, the absence of `M_BARE`, that the record's own §3 declines to enforce.
- Fix belongs in: decisions/ADR-0051.md §10 (what is met and not met) and the "Declared premises, not modelled" paragraph of a successor to spec/Correlator.tla
- Severity: Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** spec/Correlator.tla:223 (Report), :247 (Propagate), :259 (Name): every finding action is guarded by its condition "\/ Mut = "M_BARE"" for every c in Corrs; `Honest` appears in an action only at :237 (Pass) and the header defines honesty as silence only (:46-47); :58-59. spec/Correlator_proof.tla:8, :12 (FindingHasEvidenceAlways under Mut # "M_BARE"; HonestNeverChargedAlways under Mut \notin {"M_BARE", "M_TIERLESS"}), :29 and :62 (CitedFired, "every finding cites a send the fold fired on", over all of carriedF). spec/Correlator-results-2026.10.04.txt:351, :415 (both break under M_BARE with Honest = {c1}). decisions/ADR-0051.md:314 (quotation exact), :151 ("another watcher's finding may be false"), :188, :279-280, :388-391, :322-330 ("Not met" omits it). `grep -c "Correlator.tla" spec/theorem-premise-binding.md` is 0, so no premise is declared in the binding table either. Precision, not a correction: HonestNeverCharged's hypothesis is the absence of both M_BARE and M_TIERLESS.

### D-7: ADR-0051 §10 states `SilenceIsCounted` over every Observer; the module states it over correlators and `carried-label` findings only
- Against: decisions/ADR-0051.md:307 (and spec/Correlator.tla:289)
- Basis: Proposed
- Claim: "**`SilenceIsCounted`**: an Observer whose mark passed a cited record without a finding has a miss, a correlator"
- Why wrong: spec/Correlator.tla:20-22 states it as "a correlator whose mark passed a send another correlator found, and which found nothing, has a miss", and the formula at spec/Correlator.tla:289-292 quantifies `\A c \in Corrs : \A s \in marked[c]` over `Has(q, s)`, which reads `carriedF` only (line 126). No cell Observer has a mark or a miss in the module: `ObsFind` (lines 208-215) adds a miss only under `M_TIERLESS`, and `Name` (lines 257-262) names only `q \in Corrs`. So the half of `marked-past` that §2 states for cell Observers (decisions/ADR-0051.md:141-142, "A judgment finding charges the watchers that read the payload it judged: cell Observers") has no property and no row. The record says "**Met for TLC at R2**" (line 312) for the property as worded at line 307; its "Not met" list says only "the judgment tier is one action" (line 328).
- Fix belongs in: decisions/ADR-0051.md §10
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0051.md:307-308 (quotation exact), :140-142, :312, :328; spec/Correlator.tla:20-22, :126 (Has reads carriedF only), :208-215 (ObsFind adds a miss only under M_TIERLESS), :257-262 (Name over Corrs), :289-292.

### D-8: The three placeholders were chosen "so that §10's module … have a value"; the module runs `m_miss` at 1, not 2, and has no constant for the other two
- Against: decisions/ADR-0051.md:167 (and spec/Correlator-results-2026.10.04.txt:5)
- Basis: Proposed
- Claim: "below is a **placeholder**, chosen on 2026.10.04 so that §10's module and the scripted correlator have a value."
- Why wrong: The record's table gives `m_miss` "**2** (PLACEHOLDER)" (decisions/ADR-0051.md:174). spec/Correlator-results-2026.10.04.txt:5: "=== none-safe · Stores=1 · MaxSends=1 · MMiss=1 · Mut=none · INVARIANT Safe"; `grep -n "^===" spec/Correlator-results-2026.10.04.txt` shows `MMiss=1` on 21 of the 22 rows and `MMiss=2` on one witness row, `w-named2` (line 1845). `n_probe` and `θ_drift` are not constants of the module at all: spec/Correlator.tla:73 declares `Mut, Thinkers, Stores, Corrs, Honest, MaxRound, MaxSends, MMiss`, and the record itself says `probe-then-use` and `distance-drift` "are not in the module" (line 327). The same reason is given again in Options (decisions/ADR-0051.md:358: "A table with no numbers leaves §10's module and the scripted correlator nothing to run at"). No scripted correlator exists (lines 22-23: "a correlator that computes nothing, which is the reference today").
- Fix belongs in: decisions/ADR-0051.md §2 and its Options row
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed with correction; severity Low (reader: Low-Medium)
- **Verifier's correction:** The title's "runs m_miss at 1, not 2" is too strong, as the finding's own count shows: one row, the witness w-named2, runs MMiss=2, and Correlator_proof.tla proves the invariants for any MMiss. What stands: 21 of 22 rows, every safety and mutation row among them, run MMiss=1; n_probe and θ_drift are not constants of the module; no scripted correlator exists. It is a rationale sentence on which no claim rests, so Low.
- **Verifier's evidence:** decisions/ADR-0051.md:166-167 (quotation exact), :174, :327, :358, :22-23; spec/Correlator.tla:73; spec/Correlator-results-2026.10.04.txt:5, :1845; `grep "^===" spec/Correlator-results-2026.10.04.txt` gives 22 rows, 21 with MMiss=1 and 1 with MMiss=2; spec/Correlator_proof.tla:19-22.

### D-9: ADR-0051 still calls ADR-0047, ADR-0048 and ADR-0049 Proposed
- Against: decisions/ADR-0051.md:97 (and decisions/ADR-0051.md:3, decisions/ADR-0051.md:394)
- Basis: Proposed
- Claim: "ADR-0047, ADR-0049 (Proposed)" · "ADR-0047 §4, §5 and §7 (Proposed); ADR-0048 §2" · "**`carried-label` rests on three Proposed records**"
- Why wrong: decisions/ADR-0047.md:19 "**Status:** Accepted (genesis) · 2026.10.05"; decisions/ADR-0048.md:15 and decisions/ADR-0049.md:15 the same date. checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:50 lists 0047, 0048 and 0049 as accepted, confirmation required. ADR-0051's own condition at decisions/ADR-0051.md:296, "**ADR-0047 and ADR-0049 are ratified first, or `carried-label` is left out**", has therefore been met since the day after the record was last revised, and the record does not say so. (Its fourth "(Proposed)", for ADR-0035 §6 at line 4, is still correct.)
- Fix belongs in: decisions/ADR-0051.md (provenance note, §2 table, §10, Consequences)
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: no (G10 item 98 is the same staleness in two comments under `policies/` only; G11 item 97 says of ADR-0051 only "As at G10")
- **Verifier:** confirmed with correction
- **Verifier's correction:** Of the three places cited, :3-4 is the provenance note, a dated list of sources as read when the record was authored on 2026.10.04, and is not stale. The stale statements are the §2 table (:97), Consequences (:394) and the condition at :296-297, which has been met since Batch 34 without the record saying so.
- **Verifier's evidence:** decisions/ADR-0051.md:2-4, :97, :296-297, :394; History :464-467 (last revision R3, 2026.10.04); decisions/ADR-0047.md:19; decisions/ADR-0048.md:15; decisions/ADR-0049.md:15; checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:50, :340.

### D-10: ADR-0051 §10 gives a state for the module and none for its other conditions; the dependent entries it requires are drafted nowhere, and its obligations still list the module as owed
- Against: decisions/ADR-0051.md:293 (and decisions/ADR-0051.md:434)
- Basis: Proposed
- Claim: "**The dependent entries are drafted**: ADR-0038 (findings 1 to 3), ADR-0043 §4 (a finding cites records),"
- Why wrong: §10 marks the module bullet "**Met for TLC at R2**", "**Proved at R3**", "**Not met:**" and "**Certified run**" (lines 312-334) and gives no state for the dependent entries (lines 293-295), for ADR-0047 and ADR-0049 being ratified first (line 296), for the reference (line 335) or for the reader (line 341). Command run: `grep -n "ADR-0051" decisions/ADR-0038.md decisions/ADR-0043.md decisions/ADR-0015.md decisions/ADR-0020.md decisions/ADR-0006.md decisions/ADR-0049.md decisions/ADR-0035.md decisions/ADR-0016.md decisions/ADR-0033.md` returns no line, so none of the entries is drafted; decisions/ADR-0038.md:19 reads "**Pending:** none." and decisions/ADR-0043.md:17 names A3 as its only pending amendment. Open obligations, decisions/ADR-0051.md:434, still reads "**The dependent entries, the module and the reference** (§10)", though §10 says the module is written, checked, proved and certified.
- Fix belongs in: decisions/ADR-0051.md §10 and Open obligations
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: G11 item 97 (ADR-0051 as a whole, "As at G10"); the missing states are not on it
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0051.md:293-297, :312-334, :335-341, :434; the finding's grep rerun over the nine records returns no line (exit 1); decisions/ADR-0038.md:19; decisions/ADR-0043.md:17. The quoted sentence is a condition and not an assertion; the defect is that its state is not given and the entries do not exist, as the finding says.

### D-11: ADR-0037's B36 row says "§2 says a kind is never changed"; §2 says no such thing
- Against: decisions/ADR-0037.md:501
- Basis: in force
- Claim: "ADR-0053 finding 8 is a question for §2: an issuance may change a seat's kind, which `rules::validate_issuance` does not refuse, though §2 says a kind is never changed."
- Why wrong: Command run: `grep -n -i "never changed\|kind is\|fixed when\|fixed at" decisions/ADR-0037.md` returns two lines: line 103, in §1, "exactly one seat, fixed when the seat is declared.**", which is about a principal's seat and not a seat's kind, and line 501 itself. §2 (lines 115-148) has no sentence on whether a kind can change. The source the row paraphrases attributes the words to the code: decisions/ADR-0053.md:425-426, "though `types.rs` says a kind is "never changed" (ADR-0037 §2)". spec/Seats.tla:8 has the same unsupported pointer: "Seats have a kind fixed at declaration (§2)". The question G11 item 106 puts to ADR-0037 §2 is therefore put to a clause that is silent, and the History row tells a reader the clause has already answered it.
- Fix belongs in: decisions/ADR-0037.md (History B36, and §1 or §2 if the rule is meant)
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: G11 item 106 lists the question; the misattribution is not on it
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0037.md:501 (quotation exact), :103, :115-148 (§2); the finding's grep rerun returns :103 and :501 only, and a wider grep for kind with chang/fixed/immutable adds nothing; decisions/ADR-0053.md:425-426; mechanism/crates/topak-core/src/types.rs:179 (where "never changed" is written); spec/Seats.tla:8; checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:353.

### D-12: ADR-0037 §4 still states B10 over `RunInvoke`, ten lines after it says B10 names `Actuate`
- Against: decisions/ADR-0037.md:256 (and decisions/ADR-0037.md:246)
- Basis: in force
- Claim: "A new forbid, **`B10-only-thinkers-author`**: `Draft`, `Invoke`, `Submit` and `RunInvoke` are refused when"
- Why wrong: decisions/ADR-0037.md:246-247: "`Draft`, `Invoke`, `Submit` and ~~`RunInvoke`~~ `Actuate` ⟨A1⟩, and B10 names it." floor/genesis-floor.cedar:106 names `Topak::Action::"Actuate"` in B10, and decisions/ADR-0040.md:92 says "**The provisional names are retired.**" The bullet also still gives the condition as `principal.kind != "thinker"` alone (line 257), where line 238 says "B10 names both" kinds. A1 and A3 were applied to the sentence and not to the bullet that states the entry.
- Fix belongs in: decisions/ADR-0037.md §4
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0037.md:256-257 (quotation exact), :246-247, :236-238; `grep -n RunInvoke decisions/ADR-0037.md` shows it struck at :228 and :246 and unstruck at :256; floor/genesis-floor.cedar:106; floor/proposed/emergency-floor.cedar:112-115; decisions/ADR-0040.md:92.

### D-13: Three clauses in force place enforcement in ADR-0035 §5 and do not say ADR-0035 is Proposed
- Against: decisions/ADR-0037.md:268 (and decisions/ADR-0038.md:154, decisions/ADR-0039.md:204)
- Basis: in force
- Claim: "Its enforcement is ADR-0035 §5's, at the promotion tally and the deployment declaration and never at grant, and this record does not change it."
- Why wrong: decisions/ADR-0035.md:11: "**Status:** Proposed · 2026.09.25", and checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:52 lists 0035 as Proposed. ADR-0037 §5 names a Proposed record as where seat distinctness is enforced; ADR-0038 §6 says "**ADR-0035 §5's tally condition**" "is met by the author's cell Observer, by construction under seat distinctness"; ADR-0039 §3 says coverage "is added to ADR-0035 §5's tally condition". None of the three says the record is not in force. A sibling record does: decisions/ADR-0043.md:226-227, "its criterion is not in force (ADR-0035, Proposed)". The tally conditions themselves reached force through ADR-0024 A2 (decisions/ADR-0024.md:290), which these clauses do not cite; the deployment-declaration half of ADR-0035 §5 has no home in force.
- Fix belongs in: decisions/ADR-0037.md §5, decisions/ADR-0038.md §6, decisions/ADR-0039.md §3
- Severity: Low-Medium
- Confidence: medium
- Already on the corpus's own lists: G11 item 20 lists the criterion as Proposed; the unflagged dependence is not on it
- **Verifier:** confirmed with correction
- **Verifier's correction:** "which these clauses do not cite" holds of ADR-0037 §5 only. ADR-0038 §6 (:150-151) and ADR-0039 §3 (:203-205) both say the condition belongs in ADR-0024 as an amendment carried as a debt; neither names A2 or its ratification. The rest stands: none of the three says ADR-0035 is Proposed.
- **Verifier's evidence:** decisions/ADR-0037.md:268-271; decisions/ADR-0038.md:150-156; decisions/ADR-0039.md:202-205; decisions/ADR-0035.md:11, :221-227; decisions/ADR-0043.md:226-227; decisions/ADR-0024.md:290; `grep -n -o "0035.\{0,80\}Proposed\|Proposed.\{0,80\}0035\|0035.\{0,60\}not in force" decisions/ADR-0037.md decisions/ADR-0038.md decisions/ADR-0039.md` returns one line, ADR-0039:408, where "Proposed" is that row's own state.

### D-14: ADR-0038 §8 states `ReachIsBounded` as "never blocks an admit outside its cell"; the module checks whom a finding names, and its mutation never blocks an admit outside the cell
- Against: decisions/ADR-0038.md:184 (and spec/Observers.tla:79)
- Basis: in force
- Claim: "**`ReachIsBounded`**: a cell Observer's finding never blocks an admit outside its cell. Mutation `M_REACH`: cell"
- Why wrong: spec/Observers.tla:79-80: `ReachIsBounded == \A f \in findings : CellOf[f.obs] = "none" \/ CellOf[f.obs] = CellOf[f.target]`, a statement about the `findings` set. Blocking is defined separately, spec/Observers.tla:51-53, as `Found(t) \cap W(t) # {}`, and `W(t)` (line 29) holds only the Observer of `t`'s cell and the correlator. Under `M_REACH` the cell Observer `o1` may record a finding against `t2` (lines 32-33), but `o1` is not in `W("t2")`, so `Blocked("t2")` stays false: the property as the record words it holds under the mutation the record says "must fail" (line 185). What the module shows broken (spec/Observers-results-2026.09.29.txt:8) is the naming invariant. The record states one property and cites evidence for another.
- Fix belongs in: decisions/ADR-0038.md §8 (the wording), or a successor module if the blocking form is the one meant
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: no (`mechanism/GAPS-AND-ASSUMPTIONS.md` §6 notes only that reach is "**not enforced**" at the reference)
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0038.md:184-185 (quotation exact); spec/Observers.tla:29 (W), :32-33 (Reach), :51-53 (Blocked), :79-80. Under M_REACH o1 may find against t2, and W("t2") is {o2, corr}, so Blocked("t2") is unchanged. spec/Observers-results-2026.09.29.txt:8.

### D-15: Two modules assume a finding clears when the round ends, one of them attributing that to "the records"; no record decides it, and ADR-0051 §3 says it is open
- Against: spec/Correlator.tla:46 (and spec/Observers.tla:12)
- Basis: evidence
- Claim: "records clear it at the round's end." · "Findings clear when the round ends."
- Why wrong: decisions/ADR-0051.md:193-194: "**What a finding does after it blocks the next admit is not decided here**: the quarantine hold (G9 item 48) and lifting (item 22) are open". Command run: `grep -rn -i "finding[s]\? \(clear\|lift\|expire\)\|clear[s]\? \(when\|at\|with\) the round" decisions/*.md narrative/theory-of-operation.md narrative/glossary.md` returns no record that clears a finding at a round's end. ADR-0038 §5 and §8 do not say it either, yet `Observers.tla` models it (`EndRound`, lines 66-68, drops every finding against `t`, with no guard), so in that module `DenyByAnyOf` is about a finding that any step may erase. ADR-0038's R3 and B25 rows (decisions/ADR-0038.md:275, :278) cite the module without naming the assumption.
- Fix belongs in: decisions/ADR-0038.md §8 or its History (to name the abstraction), and the header of any successor to spec/Correlator.tla
- Severity: Low-Medium
- Confidence: medium
- Already on the corpus's own lists: G9 items 22 and 48 list the open questions; the modules' assumption is not on a list
- **Verifier:** confirmed with correction
- **Verifier's correction:** Only Observers.tla models the clearing (EndRound, :66-68). Correlator.tla does the opposite: a finding blocks "for good" in the module, and clearing at the round's end is listed among the premises not modelled and attributed to "the records" (:45-46); ADR-0051 §10 says "a finding never clears" (:328-329). The title should read: one module models the clearing and the other asserts it as the records' rule. That no record states it stands.
- **Verifier's evidence:** spec/Correlator.tla:45-46; spec/Observers.tla:12, :66-68, :70; decisions/ADR-0051.md:193-194, :328-329; decisions/ADR-0038.md:132-145 (§5), :176-191 (§8), :275, :278; the finding's grep rerun over decisions/*.md, narrative/theory-of-operation.md and narrative/glossary.md returns no line.

### D-16: ADR-0039 §8 calls `CorrelatorNeverGates` "a state predicate using `ENABLED`"; the module's is a history flag
- Against: decisions/ADR-0039.md:301 (and spec/Coupling.tla:117)
- Basis: in force
- Claim: "**`CorrelatorNeverGates`**: a state predicate using `ENABLED`. With a live cell Observer, the Thinker's admit"
- Why wrong: spec/Coupling.tla:117: `CorrelatorNeverGates == ~refusedForCorr`, where `refusedForCorr` is set by the `Refuse` action (line 72). Command run: `grep -c ENABLED spec/Coupling.tla` gives 0. The module's own header words it as a refusal property, lines 9-10: "the Thinker is never refused for the correlator's state". The run and proof rows (decisions/ADR-0039.md:416, :429) report the property as met and proved without saying its form changed. The later modules that do use `ENABLED` say so (`ConsultNeverCoupled`, `LagNeverGates`).
- Fix belongs in: decisions/ADR-0039.md §8 or its R4 row
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0039.md:301-302 (quotation exact; the only ENABLED in the record), :416, :429; spec/Coupling.tla:9-10, :72, :117; `grep -c ENABLED spec/Coupling.tla` gives 0.

### D-17: ADR-0039 has no entry for the liveness module written against its §2, and §2 states that admits resume without the conditions that module needed
- Against: decisions/ADR-0039.md:173 (and spec/Coupling_live.tla:23)
- Basis: in force
- Claim: "When the Observer catches up, admits"
- Why wrong: spec/Coupling_live.tla:2 is headed "Liveness for ADR-0039 §2: the stall that coupling chooses ends." and quotes the sentence at decisions/ADR-0039.md:173-174 (module lines 4-5). It finds the claim holds only under fairness the record does not state: lines 23-41 (A12 as weak fairness on `GrantO` and strong fairness on `KeepUp`), lines 52-67 (`ThinkerAsks`, `GrantsMade`), and lines 70-72, "The two admit properties also need K >= 1". Lines 59-61 add a consequence for cells: "Rounds that overlap need two cell Observers". Command run: `grep -n "Coupling_live" decisions/*.md` returns lines of ADR-0046 only; ADR-0039's History has dependent entries for the safety proof (B25) and the Lean model (B36) and none for this module, though the checkpoint files it under "ADR-0039 §2" (checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:196). The record's own text is the one place a reader of §2 will not learn that the stall is shown to end only under assumptions, and is checked and not proved.
- Fix belongs in: decisions/ADR-0039.md (a dependent entry in History, and §2's bullet)
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: G11 item 105 lists the fairness conditions and that the properties are not proved; the missing entry in ADR-0039 is not on it
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0039.md:173-174; History rows :416-432 (B25 and B36 present, none for the liveness module); spec/Coupling_live.tla:2-5, :23-41, :52-67, :59-61, :70-72; `grep -n "Coupling_live" decisions/*.md` returns ADR-0046 only (:239, :263, :301-303); checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:196, :352.

### D-18: Open-obligation lists in five records carry items their own History, or another record, shows discharged
- Against: decisions/ADR-0038.md:255 (and decisions/ADR-0039.md:375, decisions/ADR-0037.md:439, decisions/ADR-0040.md:238, decisions/ADR-0042.md:314)
- Basis: in force
- Claim: "**The ADR-0024 amendment** (§6), together with ADR-0035 §5's." · "**The ADR-0024 amendment** carrying §3's coverage condition, together with ADR-0035 §5's and ADR-0038 §6's." · "**The ratification run** (§9): floor results, the TLC module and its results, and the reference change." · "**The renames** in `floor/`, `policies/` and `mechanism/`, with an ADR-0033 addendum." · "**The Run profile** (G5 item 26), and an owner for channel fidelity (§6)."
- Why wrong: decisions/ADR-0024.md:290 (A2): "**ratified 2026.09.29** by the genesis custodian in Batch 15, after ADR-0038 (Batch 13) and ADR-0039 (Batch 14), and applied inline". Neither ADR-0038 nor ADR-0039 has an entry for Batch 15; the last word in each is that the amendment "stays pending" (decisions/ADR-0038.md:276) and "is not ratified by this batch" (decisions/ADR-0039.md:427). ADR-0037's run is its own R5 row (line 484) and its B12 row says the condition "is met in its floor, TLC and reference parts" (line 493); ADR-0038:258 and ADR-0039:376 list "**The ratification run**" the same way after R3 and R4 recorded it. ADR-0040's B20 row (line 252) says "the floor names the three actions and passes every gate" and cites ADR-0033 A3 for the reference. ADR-0042's own §6 note says "Since B30 the Run profile is written and in force" and "Channel fidelity has an owner" (lines 205-206), and checkpoints/topak-genesis-checkpoint-G10-2026.10.05.md:334 and :344 mark both "**Discharged**". ADR-0040 to ADR-0043 strike other discharged items in the same lists (for example decisions/ADR-0042.md:310-312), so an unstruck item reads as open.
- Fix belongs in: the Open obligations sections of decisions/ADR-0037.md, ADR-0038.md, ADR-0039.md, ADR-0040.md and ADR-0042.md, and a Batch 15 entry in ADR-0038 and ADR-0039
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0038.md:255, :258, :276 ("stays pending"), History :272-278 (no Batch 15 entry); decisions/ADR-0039.md:375-376, :427 ("is not ratified by this batch"); decisions/ADR-0024.md:290; decisions/ADR-0037.md:439, :484, :493; decisions/ADR-0040.md:238, :252 (the renames are not among the debts B20 leaves; `grep -rn RunInvoke floor policies mechanism/crates` finds only two tests that the retired names are refused); decisions/ADR-0042.md:205-206, :310-315, :334; checkpoints/topak-genesis-checkpoint-G10-2026.10.05.md:334, :344.

### D-19: ADR-0042's header says D-0042-1 "is the reference's behaviour today"; its own History says the reference changed before ratification
- Against: decisions/ADR-0042.md:21 (and decisions/ADR-0042.md:217)
- Basis: in force
- Claim: "**Deployment position:** Archetype. One degeneracy (§7), which is the reference's behaviour today."
- Why wrong: decisions/ADR-0042.md:329 (B20): "D-0042-1 ratifies as the name of the reference before 09.29". decisions/ADR-0042.md:31: "closed in the reference at `1e6c0c4`, ADR-0033 A3". decisions/ADR-0042.md:312: "~~**The reference changes**, with an ADR-0033 addendum.~~ ADR-0033 A3 (Batch 17)". §7 at line 217 gives a third reading of the same fact: "**D-0042-1 is the reference as it stands on 2026.09.29.**", against B20's "before 09.29" and the register's "**the reference's behaviour before 2026.09.29**" (mechanism/GAPS-AND-ASSUMPTIONS.md:332).
- Fix belongs in: decisions/ADR-0042.md header and §7
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0042.md:21 (quotation exact), :31, :217, :312, :329 ("D-0042-1 ratifies as the name of the reference before 09.29"; the reference at `1e6c0c4` shows the three behaviours); mechanism/GAPS-AND-ASSUMPTIONS.md:332.

### D-20: ADR-0042 §6's note says the reference reads a tool's target from node configuration; an addendum ratified the next day says it does not
- Against: decisions/ADR-0042.md:208
- Basis: in force
- Claim: "not: the target is read from node configuration, and every Run principal is still `Mediated`, since the criterion of"
- Why wrong: decisions/ADR-0033.md:1157 (A9, ratified 2026.10.05, Batch 32): "node configuration says nothing of a Wasm tool's channel, the target is the entry's in the bundle revision the lease names". The narrative has it the new way (narrative/theory-of-operation.md:469, "**The target is read from the tool's allowlist entry**"). ADR-0042 has dependent entries for B30 and B31 and none for Batch 32, so the first reason the note gives for the obligation being undischarged at the reference is one the corpus has since removed; the conclusion (still `Mediated`) now rests only on the second half of the sentence.
- Fix belongs in: decisions/ADR-0042.md §6 note and History
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: no for ADR-0042 (G10 item 89 lists the same stale reason in ADR-0045 Annex B)
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0042.md:207-209 (quotation exact); decisions/ADR-0033.md:1157-1158 (A9, ratified 2026.10.05 in Batch 32: "It closes what A8 listed as not discharged on this point"); narrative/theory-of-operation.md:469-472; ADR-0042 History :328-338 has B30, B31 and B34 and no Batch 32 entry; checkpoints/topak-genesis-checkpoint-G10-2026.10.05.md:366 (item 89, the same stale reason in ADR-0045 Annex B).

### D-21: ADR-0042's status note says both that C2 attaches to §6 and that §6 "stays Proposed … C2 therefore does not attach"
- Against: decisions/ADR-0042.md:14
- Basis: in force
- Claim: "Ratified at R1, in Batch 20 with ADR-0040, **without §6**, which stays Proposed as ADR-0022 §6 did until ADR-0034; C2 therefore does not attach."
- Why wrong: The sentence before it in the same note: "**§6 ratified 2026.10.04 (Batch 30), with ADR-0034 A2, and C2 attaches to it** ⟨B30⟩." The status line above it (line 13) strikes the old wording and says "**whole, §6 since 2026.10.04**"; the note keeps the old sentence unstruck and in the present tense, and continues (line 16) "**§6 is written to be left out of a ratification**". The two sentences cannot both hold today.
- Fix belongs in: decisions/ADR-0042.md status note
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed; severity Low (reader: Low-Medium)
- **Verifier's evidence:** decisions/ADR-0042.md:13-16 (quotations exact). Severity: the status line (:13) and the note's first sentence, tagged ⟨B30⟩, state the position in force, so the unstruck sentence is a stale one with no consequence for which criterion attaches.

### D-22: In ADR-0042 §5 one paragraph of the pending amendment A3 carries no pending marker and reads as present fact
- Against: decisions/ADR-0042.md:176
- Basis: pending
- Claim: "*The first bullet below is narrowed: at a workflow node, a worker's report of its outcome ends its round, the early"
- Why wrong: The pending marker at decisions/ADR-0042.md:169 covers the table only: "*Pending ⟨A3⟩, not applied. The table gains two rows (ADR-0054 §3, §4, Proposed):*". The paragraph at lines 176-178 follows the table with no tag, in the same italics the record uses for amendments in force (lines 102, 122, 139, each tagged "⟨A…⟩ ⟨B34⟩"), and says in the present tense that the bullet "is narrowed". The bullet it narrows, line 180, is in force as written: "**The principal cannot end its own round.**" A3's History row (line 338) says the amendment "reverses in effect "the principal cannot end its own round" at a workflow node", so this is the sentence of A3 that bears on C3, and it is the one left unmarked.
- Fix belongs in: decisions/ADR-0042.md §5
- Severity: Low
- Confidence: medium
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0042.md:169 (the marker names the table only), :176-178 (no tag), :180, :338 ("Bears on C3"); compare :102, :122, :139, each tagged, and decisions/ADR-0041.md:106, :110, :115, where the paragraph, the table and the paragraph after it each carry the pending marker.

### D-23: ADR-0041 §4 says `breakGlass` stays in `RunCtx`; the schema of the floor in force has removed it
- Against: decisions/ADR-0041.md:183 (and floor/proposed/emergency.cedarschema:91)
- Basis: in force
- Claim: "`toolAllowlist`, `breakGlass` and `observerLive` stay as they are."
- Why wrong: floor/proposed/emergency.cedarschema:91: "// ADR-0052 §2: no break-glass fields. An emergency seat's envelope is its `toolAllowlist`,", and `grep -n breakGlass floor/proposed/emergency.cedarschema` returns nothing (the field survives only in floor/genesis.cedarschema:85). floor/proposed/README.md:99 says "the `breakGlass` fields leave the schema" and line 110 "`RunCtx` loses `breakGlass`". A2's History row (decisions/ADR-0041.md:315) lists changes to §1 and §3 only, and §4 carries no ⟨A2⟩ note, although §4 has notes for A1 and A4.
- Fix belongs in: decisions/ADR-0041.md §4 (A2's sites)
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed with correction
- **Verifier's correction:** The parenthesis is wrong: `breakGlass` also survives in the two earlier proposed stages, floor/proposed/labels.cedarschema:89 and floor/proposed/control.cedarschema:91, not only in floor/genesis.cedarschema:85. It is absent from the stage in force (`emergency`) and from `workflow`, which is all the finding needs.
- **Verifier's evidence:** decisions/ADR-0041.md:182-183 (quotation exact), :186-193 (§4 has notes for A1 and A4 only), :315; floor/proposed/emergency.cedarschema:91; `grep -c breakGlass floor/proposed/*.cedarschema floor/*.cedarschema` gives control 1, emergency 0, labels 1, workflow 0, genesis 1; floor/proposed/README.md:99, :110.

### D-24: ADR-0041's status note says the floor "stays DRAFT, as ADR-0030 left it"; ADR-0030 A3 has since changed what the floor's status is and which text it is
- Against: decisions/ADR-0041.md:18
- Basis: in force
- Claim: "Run floor must contain. It does not ratify a floor**; `floor/` stays DRAFT, as ADR-0030 left it."
- Why wrong: decisions/ADR-0030.md:563 (A3, Batch 34): "**The floor is genesis-provisional, and is ratified at bootstrap.**" and "It names the floor in question as the one the entries in force describe, which since Batch 34 is the `emergency` stage under `floor/proposed/`." checkpoints/topak-genesis-checkpoint-G10-2026.10.05.md:333 (item 25): "**Changed**: the floor in question is the `emergency` stage, genesis-provisional". The status note still points a reader at `floor/` and at the status ADR-0030 gave before A3, in the record whose amendments changed the entries.
- Fix belongs in: decisions/ADR-0041.md status note
- Severity: Low
- Confidence: medium
- Already on the corpus's own lists: no (G10 and G11 item 25 state the new position; the stale note is not listed)
- **Verifier:** confirmed with correction
- **Verifier's correction:** The note is stale by omission and is not contradicted. ADR-0030's own header still says the genesis floor text and schema S (`floor/`) "stay **DRAFT**" beside A3's paragraph, and the stage in force is itself headed "DRAFT ... not ratified". What the note lacks is what A3 added: that the floor in question is the `emergency` stage under `floor/proposed/`, genesis-provisional, ratified at bootstrap. "Changed what the floor's status is" should read "added a status and named the text".
- **Verifier's evidence:** decisions/ADR-0041.md:17-18; decisions/ADR-0030.md:13-14 ("stay **DRAFT**"), :15-20 (A3 in the header), :563; floor/proposed/emergency-floor.cedar:4; floor/proposed/README.md:3; checkpoints/topak-genesis-checkpoint-G10-2026.10.05.md:333 ("The genesis text stays a draft").

### D-25: The floor in force says in its own text that R3 "applies to break-glass too", and that the label forbids deny "a break-glass permit"; the records in force say an emergency seat is not coupled and that there is no break-glass permit
- Against: floor/proposed/emergency-floor.cedar:156 (and decisions/ADR-0039.md:157)
- Basis: evidence
- Claim: "// applies to break-glass too: a dead, partitioned or starved Observer stops its own cell and nothing"
- Why wrong: decisions/ADR-0039.md:157-159, applied at B34: "**An emergency seat is not coupled, and the rule above does not change.**" and "a person seated by the break-glass roster's quorum for one round does not wait on an Observer." decisions/ADR-0041.md:160: "`R3-observer-live` is unchanged, and does not reach an emergency seat". The same file agrees with the records forty lines later (floor/proposed/emergency-floor.cedar:201, "// X1 break-glass is retired (ADR-0052 §2).") and contradicts them here and at line 166, "// they deny whatever permit is satisfied, a break-glass permit included.", when decisions/ADR-0041.md:155 says "There is no break-glass permit". The comments were inherited from floor/genesis-floor.cedar:150, where they were true, and the stage's build did not touch them. This is the text the checkpoint names as in force (checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:105) and the text a bootstrap reviewer is asked to find fit.
- Fix belongs in: floor/proposed/build.py (the comment edits for the `emergency` stage), at the stage's next gate run
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: no (G10 and G11 item 91 covers only the stage files' opening comment)
- **Verifier:** confirmed with correction
- **Verifier's correction:** Only the first comment is inherited from the genesis floor (floor/genesis-floor.cedar:150). The second, "a break-glass permit included", is not in the genesis floor: it enters with the `labels` stage (floor/proposed/labels-floor.cedar:162), where X1 still existed, and the `emergency` build left it. Both also stand in floor/proposed/workflow-floor.cedar:156 and :172, the stage the reference links.
- **Verifier's evidence:** floor/proposed/emergency-floor.cedar:155-156, :161 (the policy itself names `thinker` only, so the comments and not the entry are wrong), :166, :201; `grep -n "break-glass permit included\|applies to break-glass too" floor/*.cedar floor/proposed/*.cedar`; decisions/ADR-0039.md:157-159; decisions/ADR-0041.md:155, :160; checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:105, :339.

### D-26: Frozen artifacts in this scope still call accepted text Proposed or pending
- Against: floor/genesis-floor.cedar:112 (and floor/proposed/emergency.cedarschema:132, floor/genesis-values.json:10, spec/RunSeats.tla:2, spec/RunCoupling.tla:2, spec/RunConfinement.tla:2)
- Basis: evidence
- Claim: "// Run envelopes : ADR-0040 §1, stated as ADR-0041 §1 (both Proposed)" · "(ADR-0040 §1, Proposed)" · "(ADR-0042 §2, Proposed)" · "Properties for ADR-0043 §2 (Proposed)" · "Properties for ADR-0042 (Proposed)" · "ADR-0034 A2 (pending)"
- Why wrong: ADR-0040 to ADR-0043 were ratified 2026.09.30 in Batch 20 (decisions/ADR-0040.md:15, ADR-0041.md:12, ADR-0042.md:13, ADR-0043.md:11); ADR-0034 A2 was ratified 2026.10.04 in Batch 30 (decisions/ADR-0042.md:334). The same line recurs in the floor in force, floor/proposed/emergency-floor.cedar:118, whose schema also says "(ADR-0050 §4, Proposed)" at floor/proposed/emergency.cedarschema:139. floor/genesis-values.json:13 says "ADR-0031 A2 (Pending); ADR-0016 §6" while decisions/ADR-0031.md:68 carries A2 inline as applied. The results headers repeat the labels (spec/RunSeats-results-2026.09.29.txt:1, spec/RunCoupling-results-2026.09.29.txt:1, spec/RunConfinement-results-2026.10.02.txt:1). Each file is frozen by digest, so the labels cannot be corrected in place; no record or index says they are to be read as of the artifact's date.
- Fix belongs in: spec/README.md and floor/README.md (a note on how to read status words in frozen files), and the floor text at its next gate run
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no (adjacent: G10 and G11 item 91, the stage files' opening comment only; G10 item 98, two comments under `policies/` only)
- **Verifier:** confirmed
- **Verifier's evidence:** floor/genesis-floor.cedar:112; floor/proposed/emergency-floor.cedar:118; floor/proposed/emergency.cedarschema:132, :139; floor/genesis-values.json:10, :13; spec/RunSeats.tla:2; spec/RunCoupling.tla:2; spec/RunConfinement.tla:2; the three results headers at line 1; decisions/ADR-0040.md:15, ADR-0041.md:12, ADR-0042.md:13, :334, ADR-0043.md:11; decisions/ADR-0031.md:13, :68, :400 (A2 ratified in Batch 17); spec/README.md:1-9 and floor/README.md carry no note on reading status words in frozen files (`grep -n -i "frozen\|as of the\|at the time" spec/README.md floor/README.md floor/proposed/README.md` finds none on the point).

### D-27: The two floor READMEs describe the proposed stages as not in force and the reference as not supplying their inputs; both statements are out of date, and the two READMEs disagree on which stage the reference links
- Against: floor/proposed/README.md:5 (and floor/proposed/README.md:125, floor/README.md:5)
- Basis: living document
- Claim: "This directory holds the floor as it would read if the records drafted on 2026.10.03 and 2026.10.04 were in force." · "The reference's lift supplies none of them today." · "It links the `labels` stage in `proposed/`"
- Why wrong: Those records are in force: checkpoints/topak-genesis-checkpoint-G10-2026.10.05.md:111-117, "**The entries in force changed for the first time since G7**" and "**The text is `floor/proposed/emergency-floor.cedar`**". The reference's lift does supply the label facts: mechanism/GAPS-AND-ASSUMPTIONS.md:105 (I46), "The lift hands them to the floor, the admit carries them, and `apply` folds them on every replica", and the same README says at line 6 "**Since 2026.10.05 the reference links, pins and replays a stage from here**". floor/README.md:5 names the `labels` stage as what the reference links, while floor/proposed/README.md:3 says "**the reference links the `workflow` stage** (since 2026.10.08; `emergency` from 2026.10.05)". ADR-0041 points readers at this README for the control entries (decisions/ADR-0041.md:95-96).
- Fix belongs in: floor/proposed/README.md and floor/README.md
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: no (item 91 concerns the stage files, not the READMEs)
- **Verifier:** confirmed
- **Verifier's evidence:** floor/proposed/README.md:3, :5, :6-10, :125 (quotations exact); floor/README.md:5; checkpoints/topak-genesis-checkpoint-G10-2026.10.05.md:111-117; mechanism/GAPS-AND-ASSUMPTIONS.md:105 (I46); decisions/ADR-0041.md:95-96.

### D-28: ADR-0038 §6 gives ADR-0035 §5's tally condition in quotation marks, and the words are not ADR-0035's
- Against: decisions/ADR-0038.md:154 (and decisions/ADR-0035.md:215)
- Basis: in force
- Claim: "("at least one veto seat leased for the round with a Persona independent of the"
- Why wrong: decisions/ADR-0035.md:215-216: "A promotion round completes only if at least one veto seat was leased for the round with a Persona whose lineage is independent of the author's, according to the table." The quotation drops "was", "whose lineage is" and the qualifier "according to the table", which is the part that makes the condition computable. ADR-0035 is Proposed and revised in place, so the quotation may have matched an earlier text; it does not match the file.
- Fix belongs in: decisions/ADR-0038.md §6
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0038.md:154-155; decisions/ADR-0035.md:215-216.

### D-29: The schema notes say every degeneracy row writes "none" under theorems voided, and that D-0037-1 coined "properties lost"; four of the five rows write something else, and D-0037-1 does not contain the phrase
- Against: decisions/ADR-0037.md:423 (and decisions/ADR-0038.md:172, decisions/ADR-0037.md:313)
- Basis: in force
- Claim: "Every degeneracy in this record and in ADR-0038 and ADR-0039 writes "none" in" · "D-0039-1 R1) coined "properties lost" to carry it." · "Every row above writes "none" under *theorems voided*"
- Why wrong: The rows read "**No safety theorem**, because the Observer is never in the admit path" (decisions/ADR-0037.md:313, D-0037-1), "**No safety theorem**" (line 314, D-0037-2), "**No safety theorem.**" (decisions/ADR-0038.md:164 and :165). Only D-0039-1 writes "**None.**" (decisions/ADR-0039.md:262). "No safety theorem" is weaker than "none": it leaves room for a voided theorem that is not a safety theorem, which is the distinction finding 6 is about. The phrase "properties lost" is in D-0039-1 ("**Properties lost:**") and, in the singular, in D-0037-2 ("**Property lost:**", line 314); D-0037-1's row, which lines 425-426 name as one of the two that coined it, has neither.
- Fix belongs in: decisions/ADR-0037.md finding 6 and decisions/ADR-0038.md §7's note
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0037.md:423-426, :313, :314; decisions/ADR-0038.md:164, :165, :172; decisions/ADR-0039.md:262. Five rows: four write "No safety theorem", one "None."; D-0037-1's row has neither "properties lost" nor "property lost".

### D-30: ADR-0038's header points to "§5 here" for the veto seats; they are in §6
- Against: decisions/ADR-0038.md:26
- Basis: in force
- Claim: "**Relates to:** ADR-0024 §5 (veto seats; §5 here)"
- Why wrong: decisions/ADR-0038.md:147: "### 6. The veto roster holds cell Observers and correlators", and line 149 "**ADR-0024 §5's veto-seat holder becomes: every cell Observer seat and every correlator seat in the Build domain.**" §5 (line 132) is "Observers combine by any-of, and there is no Observer quorum" and does not re-home the veto seats.
- Fix belongs in: decisions/ADR-0038.md header
- Severity: Low
- Confidence: medium
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0038.md:26, :132 (§5), :147-149 (§6); the same record's Open obligations (:255) and B13 row (:276) both say "The ADR-0024 amendment (§6)".

### D-31: A facts-only correlator is called a declared narrowing, but the only row it is hung on is the one for having no correlator, and no row exists for the read set
- Against: decisions/ADR-0038.md:116 (and decisions/ADR-0038.md:165)
- Basis: in force
- Claim: "**A facts-only correlator is a permitted narrowing**, recorded as the mitigation on D-0038-2's declaration (ADR-0023"
- Why wrong: decisions/ADR-0038.md:165: "| **D-0038-2** | Declaration | Correlators: 1 or more → 0 | Some Observer reads across cells |". A deployment with a facts-only correlator has one correlator, and some Observer does read across cells, so D-0038-2's parameter and its falsified premise are both untrue of it; it cannot declare D-0038-2 and has no other row to declare. The degeneracy table (lines 162-165) has no mitigation column and no entry for the read set. Later text in force relies on such a declaration existing: decisions/ADR-0043.md:155-156, "has made that Observer a facts-only reader for the item (ADR-0038 §3), and declares it", and decisions/ADR-0042.md:108 "ADR-0038 §3's permitted narrowing". ADR-0051 leans on it again (decisions/ADR-0051.md:80-81) and describes D-0051-1 as "D-0038-2 with a seat filled" (line 286).
- Fix belongs in: decisions/ADR-0038.md §3 and §7
- Severity: Low-Medium
- Confidence: medium
- Already on the corpus's own lists: no
- **Verifier:** confirmed with correction
- **Verifier's correction:** The missing mitigation column is not itself a gap: ADR-0023 §6 makes mitigation an optional field of a deployment's declaration record, which is what ADR-0038:116 cites, and no degeneracy table in these records has such a column. The defect is the narrower one the finding also states: a deployment that seats a facts-only correlator has a deployed value of 1 and an Observer that reads across cells, so D-0038-2's parameter and falsified premise do not describe it, and no row takes the read set as its parameter.
- **Verifier's evidence:** decisions/ADR-0038.md:116-119, :162-165, :199; decisions/ADR-0023.md:45; decisions/ADR-0037.md:311 (the same columns, no mitigation); decisions/ADR-0043.md:154-156; decisions/ADR-0042.md:108; decisions/ADR-0051.md:80-81, :286.

### D-32: ADR-0039's R5 row counts "two wording findings" and cites three
- Against: decisions/ADR-0039.md:417
- Basis: in force
- Claim: "The run's two wording findings (R4 items 1 to 3) applied before ratification."
- Why wrong: R4 (decisions/ADR-0039.md:416) numbers "**Four findings for the record:** (1) … (2) … (3) … (4)", and R5 goes on to describe three changes (condition 3's strict form; the entry scoped to `thinker` seats; the apply-time re-check) and then says "Both were already what the floor and the reference implement". The count and the range disagree in one sentence, so a reader cannot tell whether item 3 was applied as a wording finding or as something else.
- Fix belongs in: decisions/ADR-0039.md History R5
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0039.md:416 ("Four findings for the record: (1) ... (2) ... (3) ... (4)"), :417 ("two wording findings (R4 items 1 to 3)", three changes, then "Both").

### D-33: ADR-0039 §6 says `K` "cannot exceed" `R`; §1 requires `K` strictly below `R`
- Against: decisions/ADR-0039.md:250 (and decisions/ADR-0039.md:136)
- Basis: in force
- Claim: "`K` cannot exceed `R` (§1), so the in-round slack is at most a round."
- Why wrong: decisions/ADR-0039.md:136-139: "**`K` must be below the round bound `R`** ⟨R1⟩. With `K ≥ R`, condition 3 can never refuse an admit that the round bound has not already refused." and "The mechanism refuses at startup a floor whose `K ≥ R`". "Cannot exceed" admits `K = R`, which §1 refuses and calls vacuous. §6 cites §1 for a weaker bound than §1 states.
- Fix belongs in: decisions/ADR-0039.md §6
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0039.md:250, :136-139.

### D-34: ADR-0042 §8 pairs `SealCountsEffects` with the mutation `M_ROUNDS`; the run shows the property holds under it
- Against: decisions/ADR-0042.md:236 (and spec/RunCoupling-results-2026.09.29.txt:20)
- Basis: in force
- Claim: "**`SealCountsEffects`**: at the end of a round the seal equals the number of effect-bearing admits in it. Mutation"
- Why wrong: The clause continues at line 237: "`M_ROUNDS`, carried over from `Coupling.tla`, must still fail." spec/RunCoupling-results-2026.09.29.txt:20: "rc-rounds-seal | Mut=M_ROUNDS | SealCountsEffects | HOLDS | 28370 distinct states found". What `M_ROUNDS` breaks is `UnreadEffectsBounded` (line 18). The mutation that breaks `SealCountsEffects` is `M_EMITSEQ` (line 10), which the B20 and B25 rows say (decisions/ADR-0042.md:329, :332: "`SealCountsEffects` unless `M_EMITSEQ` (the premise table had named `M_ROUNDS`; ADR-0046 §5)"). The premise table was corrected; the clause the table copied from was not. §8 also names no mutation for `RoundBoundCountsAll`, for which the module has `M_BOUNDEFF` (spec/RunCoupling.tla:45-46).
- Fix belongs in: decisions/ADR-0042.md §8, or a note under it
- Severity: Low
- Confidence: medium
- Already on the corpus's own lists: in part: ADR-0046 §5 corrected the premise table, as ADR-0042's B25 row records; §8's wording is not listed
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0042.md:236-238, :332; spec/RunCoupling-results-2026.09.29.txt:10 (rc-emitseq-seal, COUNTEREXAMPLE), :18, :20 (rc-rounds-seal, HOLDS); spec/RunCoupling.tla:39, :45-46; decisions/ADR-0046.md:359-360 ("`SealCountsEffects` breaks under `M_EMITSEQ`, not `M_ROUNDS`, which never touches a seal"); spec/theorem-premise-binding.md:72.

### D-35: `Seats.tla` checks `OnlyThinkersAuthor` over one authoring variant; ADR-0037 states it over four, and the run row does not say the model was cut down
- Against: decisions/ADR-0037.md:330 (and spec/Seats.tla:26)
- Basis: in force
- Claim: "**`OnlyThinkersAuthor`**: no non-`thinker` seat has an admitted authoring variant. Mutation `M_KIND`: the grant"
- Why wrong: spec/Seats.tla:25-26: `Acts == {"Read", "Draft", "Emit", "Vote"}` and `Authoring == {"Draft"}`. §4 names the authoring variants as "`Draft`, `Invoke`, `Submit` and ~~`RunInvoke`~~ `Actuate`" (decisions/ADR-0037.md:246-247), and the R5 row reports the floor's B10 as "total and discriminating on `Draft`, `Invoke`, `Submit`, `RunInvoke`" (line 484) beside the TLC result, with no note that the module has one of the four. The module also has three kinds where five are in force since B34; ADR-0039's A2 says of its own modules that they "need no successor on this account" (decisions/ADR-0039.md:160-161), and ADR-0037's A3 and A4 say nothing either way about `Seats.tla`.
- Fix belongs in: decisions/ADR-0037.md History (R5 or B34)
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0037.md:330-331, :246-247, :484, :498-499 (A3 and A4 do not mention the module); spec/Seats.tla:25-26, :29; decisions/ADR-0039.md:160-161.

### D-36: ADR-0043 §8 requires a `grant` seat in Run to be refused `Actuate`; `RunSeats.tla`, cited as meeting it, has no `grant` seat
- Against: decisions/ADR-0043.md:192 (and spec/RunSeats.tla:39)
- Basis: in force
- Claim: "**The grant path and the floor refuse the same thing**: an `observer` or `grant` seat in Run is refused `Actuate` at"
- Why wrong: spec/RunSeats.tla:39: `KindOf == [rt |-> "thinker", ro |-> "observer", bt |-> "thinker", bo |-> "observer"]`, and `KindBound` (lines 45-48) has cases for `thinker` and `observer` only. The results header says the same (spec/RunSeats-results-2026.09.29.txt:2, "4 seats (a thinker and an observer in each domain)"). The B20 row (decisions/ADR-0043.md:264) says the condition "is met in three parts and carried in one", the first part being "`spec/RunSeats.tla` (run 2026.09.29)". The `grant` half of the clause is checked by no row of the module.
- Fix belongs in: decisions/ADR-0043.md History (B20), or §8
- Severity: Low-Medium
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0043.md:192-194, :264; spec/RunSeats.tla:39, :45-48; spec/RunSeats-results-2026.09.29.txt:2; the reference test B20 cites, mechanism/crates/topak-core/tests/mutations.rs:814-830, grants to observer and thinker seats only.

### D-37: ADR-0046 gives `RunConfinement_proof.tla` a digest that is the digest of its certified-results file
- Against: decisions/ADR-0046.md:179
- Basis: in force
- Claim: "`RunConfinement_proof.tla` (`823ae3479ef38845`)"
- Why wrong: Command run: `sha256sum spec/RunConfinement_proof.tla spec/RunConfinement-proof-cert-results-2026.10.04.txt | cut -c1-16` gives `e8612bf4111c7599` for the module and `823ae3479ef38845` for the results file. decisions/ADR-0034.md:132-133 has them the right way round: "(`spec/RunConfinement_proof.tla`, `e8612bf4111c7599`) and the proof is certified, its results file regenerated byte for byte (`823ae3479ef38845`; ADR-0046 A1)". The proof results header agrees (spec/RunConfinement-proof-results-2026.10.02.txt:2). ADR-0046 is outside this reader's primary scope; the artifact is inside it.
- Fix belongs in: decisions/ADR-0046.md (an erratum)
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed with correction
- **Verifier's correction:** Not a slip peculiar to this module. All three digests in the sentence are those of the certified results files, following the table above it, whose columns are "Module | Certified results file": `9be0fe30c2c1cab9` is Operators-proof-cert-results-2026.10.04.txt (Operators_proof.tla is `226230ef1e56b413`) and `f4ffce6861f24e77` is Confinement_A1-proof-cert-results-2026.10.04.txt (Confinement_A1_proof.tla is `63c7d90a7fc2ccf8`). The defect is that the sentence sets each beside the module's name without naming the results file, and the fix covers all three.
- **Verifier's evidence:** decisions/ADR-0046.md:160-174 (the table), :178-180; `sha256sum spec/RunConfinement_proof.tla spec/RunConfinement-proof-cert-results-2026.10.04.txt spec/Operators_proof.tla spec/Operators-proof-cert-results-2026.10.04.txt spec/Confinement_A1_proof.tla spec/Confinement_A1-proof-cert-results-2026.10.04.txt | cut -c1-16` gives e8612bf4111c7599, 823ae3479ef38845, 226230ef1e56b413, 9be0fe30c2c1cab9, 63c7d90a7fc2ccf8, f4ffce6861f24e77; decisions/ADR-0034.md:132-133; spec/RunConfinement-proof-results-2026.10.02.txt:2.

### D-38: G11's open item on modules with no binding rows omits `Correlator.tla`
- Against: checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:338
- Basis: in force
- Claim: "The binding table has no rows for `Labels`, `ToolList`, `Operators`, `Emergency`, `BreakGlass_A1` or `NonComposition_A1`, nor now for `Emergency_live`, `Coupling_live`, `Workflow` or `Mesh`."
- Why wrong: Command run: `grep -c "Correlator.tla" spec/theorem-premise-binding.md spec/theorem-premise-binding.json` gives 0 and 0, and `grep -c CarriedCoversSplitPath` on the same two files gives 0 and 0; the one line of the table that contains "Correlator" is the row for `CorrelatorNeverGates` in `Coupling.tla` (spec/theorem-premise-binding.md:69). ADR-0051 lists the rows as owed (decisions/ADR-0051.md:450). The module is proved and certified, so the item's list is one short.
- Fix belongs in: the next checkpoint's open list (item 90)
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: G11 item 90 is the list in question; `Correlator` is the member it omits
- **Verifier:** confirmed
- **Verifier's evidence:** checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:338; `grep -c "Correlator.tla" spec/theorem-premise-binding.md spec/theorem-premise-binding.json` gives 0 and 0, and `grep -c CarriedCoversSplitPath` on the same files 0 and 0; spec/theorem-premise-binding.md:69 is the only line with "Correlator"; decisions/ADR-0051.md:450. The item does list modules of Proposed records (`Workflow`, `Mesh`), so the omission has no ground in status.

### D-39: ADR-0051 says `shared-ingress` stands on "Accepted text"; its own §3 says it needs an obligation this Proposed record creates
- Against: decisions/ADR-0051.md:98 (and decisions/ADR-0051.md:190)
- Basis: Proposed
- Claim: "| **`shared-ingress`** | An item one watcher found against, delivered to other cells | Accepted text |"
- Why wrong: decisions/ADR-0051.md:190-192: "**`shared-ingress` and `marked-past` need every Observer's finding to cite records.**" and "This is an obligation on every `observer` seat, and it is owed to ADR-0043 §4 as a dependent entry." The sibling row says so (line 100: "Accepted text, and §3"); this one does not. §10 repeats the stronger claim, lines 296-297: "The other four stand on accepted text." Finding 4 of the same record (lines 411-413) says "**No finding has a schema.**", so the accepted text gives `shared-ingress` nothing to read a citation from.
- Fix belongs in: decisions/ADR-0051.md §2 table and §10
- Severity: Low
- Confidence: high
- Already on the corpus's own lists: no
- **Verifier:** confirmed
- **Verifier's evidence:** decisions/ADR-0051.md:98, :100, :123 (the definition itself begins from a finding that "cites the records it is about (§3)"), :190-192, :296-297, :411-413.

