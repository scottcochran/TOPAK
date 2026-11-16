# TOPAK — An Outside Reading of the Documentation Design, Checked and Carried to Recommendations

**2026.11.16** · derived · a reading of a reading, not a record · subject: a session in which Kimi K3.1 Pro, asked by
the custodian for "your independent, objective, assessment of TOPAK's documentation design" after "a thorough
reading of the ADRs", read the tree at commit `b4a25a7` · checked against the tree at `51d7f5b`, which is Genesis
Checkpoint G12 (cut the same day) with nothing after it · the session is kept verbatim in
`topak-documentation-design-assessment-2026.11.16/session.md` · prepared by the assistant at the custodian's
request

Nothing here is ratified, and this document proposes no decision text. Where it suggests an entry, none is made.

**Sources.** The session as the custodian pasted it (the annex), with no transcript of its tool calls; the 76 record
files under `decisions/`; `decisions/README.md`; G12; `README.md`; `REVIEWERS_GUIDE_README.md`; `narrative/README.md`
and the Theory of Operation revision 15 at the one passage quoted; `spec/clauses.py`; the 11.11 critical review and
gaps prioritization. Of the records, ADR-0003, ADR-0015 to ADR-0018, ADR-0020, ADR-0029 A2, ADR-0070, ADR-0071,
ADR-0072 and ADR-0073 were read at the passages each check below cites, and ADR-0072's Options considered in full.
No record was read end to end for this document.

**Method.** Every factual claim in the session that can be checked against the tree was checked, by search and by
reading the passage, and is listed in §2 with what was found. Four measurements were made over all 76 record files
by a script run for this document and not kept in the tree: total size, the share in struck text (`~~…~~`), the
share before the first level-two heading (the header block) and the share by level-two section. The session's
judgments (that something is "outstanding" or "weak") are not checked; §3 says where this document agrees and why.

**Not independent.** The session is the first reading in the corpus by a model of a lineage other than the
drafter's, as far as `derived/` records: the 09.12 "external" assessment was a claude.ai session. **This document is
not.** It is the drafter's lineage grading an outside reader's view of the drafter's work, and a reader should
weigh every place where it corrects the session with that in mind. It does not count under ADR-0029 A2 and
dispositions nothing.

---

## 0. Verdict

**The session is accurate, mostly unoriginal against the 11.11 self review, and useful for three things the
self review does not say.** Of twenty checkable claims, fifteen hold; two held at `b4a25a7` and the G12 cut has
since fixed them (one of them already CR-44); one is misattributed; one misreads a record's scope; and one is
overstated by measurement (§2). Its central judgment, that the corpus is built to show every statement's lineage
and not to bring a reader to what is in force, is the 11.11 review's CR-47 in other words, and its call for an
independent reader is gaps item 1.

What it adds:

1. **Record scope as a finding of its own.** The self review counts what is stale, unbound and Proposed. It does not
   say that a record has become a programme. The measurement bears the session out: the `## Decision` sections hold
   40% of the corpus's 2.0 MB of records, eleven files exceed 50 KB, and ADR-0033's 151 KB parses into seven
   clauses (§2, C20).
2. **Status as orthogonal fields.** CR-44 found the confirmation set assembled by hand from a field that is not
   kept; the session proposes the field structure that would fix the class and not the instances.
3. **Role documents before the documentation platform.** The custodian's request of 2026.11.16 set ADR-0072's
   store and interfaces (K5 to K7). The session is the first reader to ask that they be staged behind a test of
   ADR-0071's information architecture with real readers.

Where it is wrong matters for the recommendations: **history is not what makes the records long.** Struck text is
1.0% of the bytes, the header block 10.9% and `## History` 18.6%. A generated in-force view (R2) is worth building,
but it will not make ADR-0033 short. Scope is the problem, and the session says so in its own point 1.

---

## 1. The session

**What was asked.** One prompt, quoted in full in the annex. It asked for an independent and objective assessment
and a thorough reading of the ADRs.

**What was read.** By the session's own account: the root README, the reviewer's guide, the narrative README, G11
material, the decisions index, ADR-0001 to ADR-0021 in full where files exist, and ADR-0029, ADR-0033, ADR-0045,
ADR-0050, ADR-0052, ADR-0054, ADR-0069 to ADR-0073, ADR-0076 and ADR-0077 in "substantial close readings". It says
the longest records "could only be partially rendered". That is thirty-three of the 76 files, and none of
ADR-0022 to ADR-0028, ADR-0030 to ADR-0032, ADR-0034 to ADR-0044, ADR-0046 to ADR-0049, ADR-0051, ADR-0053,
ADR-0055 to ADR-0068, ADR-0074 or ADR-0075 is named. Every link it gives is a raw GitHub URL at `b4a25a7`, which is
no manifest cut.

**What it found**, in its own table: provenance and traceability outstanding; uncertainty and non-claims
outstanding; rationale strong; ADR atomicity weak to mixed; current-state readability weak; navigation mixed;
independent validation not established; role documentation proposed and not built. Seven weaknesses, an assessment
of ADR-0071 to ADR-0073, and seven improvements.

**What it did not see.** That every record from ADR-0056 to ADR-0077 is Proposed (G12 §1: 27 Proposed of 76 files),
so the documentation records it assesses sit in a corpus where a third of the records are not in force. That
`spec/clauses.py` already splits a record into clauses and leaves out its header and History (ADR-0057 §2, §7,
Proposed), which is most of an in-force view. That ADR-0072's store and interfaces were the custodian's, not the
drafter's. That ADR-0072 weighed a static site and did not take it.

---

## 2. The claims, checked

Result: **Holds**; **Holds, already found** (with the finding); **Overtaken** (true at `b4a25a7`, not at G12);
**Misattributed**; **Misread**; **Overstated**.

| | Claim | What was found | Result |
|---|---|---|---|
| C1 | 76 record files, numbered to 0077, 0014 absent | 76 files; the index gives 0014 as "Reserved, no file"; G12 §1 says the same | Holds |
| C2 | ADR-0033 is about 149 KB and several others exceed 50 KB | 154,540 bytes; eleven files exceed 50,000 bytes and 26 exceed 30,000 | Holds |
| C3 | Checkpoint, records, narrative, evidence, derived, in that order of authority; the narrative README says the checkpoint wins | `narrative/README.md` line 23; `README.md`; the reviewer's guide's line 4 and its table at line 61 | Holds |
| C4 | "Accepted" in genesis is the sole custodian's ratification; 29 of 47 accepted need confirmation; Proposed records are built and a floor stage not in force is linked | Reviewer's guide lines 39 to 42; G12 §1, 18 + 27 + 2 = 47 accepted | Holds, already found: CR-44 shows that 29 understates the set |
| C5 | The index says status at G11 and heads its column "Status at G8" | So at `b4a25a7`; at G12 the index says G12 in both places | Overtaken; already found (CR-44) |
| C6 | The root names G11 while records dated 11.16 are present | So at `b4a25a7`; `README.md` names G12 at `51d7f5b` | Overtaken. But the reviewer's guide, which says it "is kept current", still says "currently G11" and "Two records are Proposed and already built" (lines 42, 61). Twenty-seven are Proposed at G12 |
| C7 | ADR-0003 records rejected alternatives for post-seal denials | ADR-0003 line 117 | Holds |
| C8 | "ADR-0003 itself diagnoses this bundling problem" | ADR-0003 records that the bundling check was run on 2026.09.15 and that it led to **no split**. The record that names a bundle and splits it is ADR-0025 ("Revision 2 bundled eight clauses") | Misattributed. The substance stands: bundling was a named concern of the 09.15 cleanup and has had no check since |
| C9 | ADR-0017 admits the archetype is expensive and out of most adopters' reach | ADR-0017, Negative: "Almost nobody can afford the archetype" | Holds |
| C10 | ADR-0020 gives revisit triggers | ADR-0020 "Revisit triggers" | Holds |
| C11 | ADR-0018 separates admissibility from fidelity | ADR-0018: "The validator guarantees admissibility, not fidelity" | Holds |
| C12 | ADR-0015's comparison with prior work was later qualified | ADR-0015 E2 conditions "strictly stronger"; ToO rev 15 carries the conditioned form | Holds |
| C13 | "structurally embarrassing", "the sharpest differentiation available" | ADR-0016 line 29; ADR-0015 line 81 (struck by E2 in the consequence it stood in) | Holds |
| C14 | ADR-0070 separates an adversarial second-context review from an independent one | ADR-0070 ⟨R1⟩ note: "independence of context and not of lineage", "not ADR-0029 A2's reader" | Holds |
| C15 | ADR-0077 separates upstream results from checks reproduced | ADR-0077 provenance: "were not reproduced for this draft" | Holds |
| C16 | ADR-0071 risks over-binding; bind normative claims, guarantees, prerequisites and steps, not every explanatory sentence | B-1 binds "each statement of what the system does, requires or guarantees"; B-2 binds every must, cannot and never at SI; B-3 binds guarantees and limits at MI. Explanatory sentences are not bound. The binding requirement is the custodian's ⟨K4⟩ | Misread. The session's proposed limit is close to what the record already says. The real cost it points at stands: B-1 asks for five relations per statement and writes every absence |
| C17 | ADR-0072 prescribes a DynamoDB-compatible single table with GraphQL and REST before a consumer need is shown | §5 to §7 do. The provenance note gives all three as the custodian's (⟨K5⟩, ⟨K6⟩, ⟨K7⟩). Options considered rejects "a site generated per version" because "every checkpoint and every revision is not a few, and a copy per view shares nothing" | Holds as a description. As a criticism it is addressed to the custodian's requirement, and it does not answer the record's stated reason for rejecting a static site |
| C18 | ADR-0073: complete HTML, a no-script path, forced colours, WCAG 2.2 AA as a signed human audit | Title and §7. The custodian asked for "WCAG Compliance"; version and level are the drafter's | Holds. The session does not assess the record's choice of React and Material UI |
| C19 | Early records cite chat-session URLs | 21 record files cite a claude.ai chat URL | Holds |
| C20 | Struck text, replacements, markers, pending amendments and batch notes interleave so that "the historical view often functions as the primary view" | Over all 76 files: struck text 1.0% of bytes; header block 10.9%; `## History` 18.6%; `## Decision` 40.0%; Context 4.9%, Options 4.6%, Evidence 4.4%, Consequences 4.2%. 2,087 short ⟨…⟩ markers, about one per kilobyte. ADR-0033: 5 KB header, 2 KB struck, 38 KB History, the rest decision and evidence | Overstated as a share. History and header are under a third of the bytes; most of the length is decision text. The reading cost is real, and it is mostly the scope of C8 and the session's own first weakness |

---

## 3. Where this document agrees, and where it adds a qualification

**Provenance and non-claims.** Agreed, and the session's examples are well chosen. The one qualification is that
provenance discloses the gap it does not close: a record that says its sources were "read through an inventory"
is honest and is still a record whose sources were read through an inventory. The session's fifth weakness says
this. The register of what was read at what depth exists only record by record.

**Scope.** Agreed, and this is the session's most useful finding. The corpus's own check for it, the bundling check of
2026.09.15, is recorded on the recovered records (ADR-0003's status note) and nowhere after them. ADR-0029 has no
step that asks whether a record is one decision, by a search of it for bundling and splitting. ADR-0033 is the
extreme case, and it is accepted, so its text cannot be split. The next four by size are ADR-0045, ADR-0070,
ADR-0046 and ADR-0053; ADR-0070 is Proposed, and so are twelve records over 30,000 bytes in all. The 11.11
review's question "what is an overlay record?" (CR-40, gaps item 3) is a scope question for ten records; the session
asks it of all of them.

**Status vocabulary.** Agreed in part. The session reads "Accepted (genesis); confirmation required" as ambiguous to
an outside reader. It is ambiguous only to a reader who has not read ADR-0029 §3 and §4, and the reviewer's guide
puts that sentence near the top. The stronger argument for the session's fix is CR-44's: the confirmation set is the
list the genesis process rests on, and it is assembled by hand from status lines that are not kept. Separate
fields would let a checker assemble it.

**Independent review.** Agreed, and nothing is added: gaps item 1 says it first. The session's own standing is
taken up in §4.

**Prose.** Agreed that a few evaluative words survive in accepted text, and that the qualification of ADR-0015
shows the cost. The session's second sentence, "information density without sufficient separation by reader task",
is ADR-0071's own premise and the better statement of the problem. Evaluative words in accepted records cannot be
edited and are not worth an erratum each.

**ADR-0072.** Partly agreed. The projection decision (§1 to §4) is sound and the session says so. On the store and
interfaces the session's challenge is fair, but it is the custodian's to answer, since K5 to K7 are the custodian's;
and the record's argument against a static site is about storage per view, which a generator that addresses units
by digest and shares them across views would answer. That generator is also the cheapest way to put ADR-0071's
levels in front of a reader.

---

## 4. The session's standing

**It is not ADR-0029 A2's review.** A2.1 asks for a review of "the entire corpus" at "one named manifest digest" by
"at least one reviewer who is not the author", complete when "every finding is dispositioned". The session read
thirty-three record files, some of them only in part, at a commit that is no manifest cut, and nothing it found
is dispositioned.

**It is the first reader of another lineage.** ADR-0070's ⟨R1⟩ note separates independence of context from
independence of lineage and says a second assistant session has only the first. Kimi K3.1 Pro has both, as far as a
reader of the corpus can tell. That is worth recording. Whether a model's reading may ever count toward A2 is not
settled anywhere in the corpus; ADR-0070 leaves it to the custodian ("unless the custodian rules that it does"), and
so does this document.

**Its prompt shaped it.** "Your independent, objective, assessment" and "a thorough reading of the ADRs" asked for a
verdict on documentation design, and the session gave one. It did not read the specifications, floors, policies or
mechanism, and does not claim to.

---

## 5. Recommendations

In order of leverage. Each says what it joins in the 11.11 gaps prioritization (*gaps*) or review (*CR*), who would
do it, and roughly how much. The custodian decides all of them.

| | Recommendation | Why | Joins | Who | Size |
|---|---|---|---|---|---|
| **R1** | **Bring the reviewer's guide to G12** before anyone else is pointed at it: the checkpoint it names, the Proposed count (27, not two), the sync-check lines, and the confirmation count with CR-44's caveat | It is the first document an A2 reviewer opens and it says it "is kept current". It is the one place C6 still holds | gaps 5; CR-47 | Drafter | Hours |
| **R2** | **Generate an in-force view of each record** from `spec/clauses.py`: the Decision clauses only, struck text dropped, replacement text kept, ⟨…⟩ markers dropped, pending subsections listed as pending and not merged, with the status line and a link to the full file. Write it beside the records as generated output, never edited, with a check that it regenerates. It decides nothing (ADR-0071 §1 applies to it) | It answers CR-47 for the records, it is what the session's first improvement asks, and most of it exists. It will not make the long records short: §2 C20 | gaps 5, 9; CR-47 | Drafter | A day |
| **R3** | **Put status in fields**: design status (ADR-0029 §3), confirmation criteria with the amendment that carries each, implementation (from ADR-0033's addenda and `corpus-pins.sha256`), evidence (checked, proved, reproduced), review (none, second context, other lineage, A2). Generate the index and each checkpoint's confirmation count from them | CR-44's finding is a class: the set is hand-assembled from a field that is not kept. The session's third improvement is the shape of the fix | CR-44; gaps 5 | Drafter drafts an ADR-0029 amendment; custodian decides | Days |
| **R4** | **Restore a scope check.** Before a record goes Proposed, the drafter answers in its Status note: how many decisions does it make, and could any be ratified or reversed alone? Where the answer is more than one, say why they travel together. Run the check now on the twelve Proposed records over 30,000 bytes (ADR-0070, ADR-0069 and ADR-0075 the largest), not on accepted ones | The 09.15 bundling check was not repeated, and the records grew. A Proposed record can still be split; an accepted one cannot | gaps 3 (the overlay question is this one for ten records); CR-40 | Custodian decides; drafter adds the step to the drafting procedure | Hours for the rule; a day for the sweep |
| **R5** | **Record the session as an outside-lineage reading** in the next checkpoint's debt ledger, beside the A2.5 line, without counting it as A2. Offer this document and its annex to the A2 reader as a starting brief, with the warning in §0 that this document is of the drafter's lineage | It is evidence of a kind the corpus has not had, and it is easy to lose | gaps 1; ADR-0029 A2.5 | Custodian | Minutes |
| **R6** | **Stage ADR-0071 before ADR-0072.** Write the five role units the session names (anchor or bootstrap key-holder, promotion voter, operator, emergency participant, auditor) at MI and SI against G12, render them with the simplest generator that keeps one copy per digest, and test them on readers who did not draft them, with fixed questions: what is in force, what is guaranteed, what is assumed, what is built, what is undecided. Reconsider K5 to K7 with the results | ADR-0071's levels and bindings are untested on any reader. ADR-0072's store and two interfaces are the largest cost in the three records and have no consumer yet. The answer to ADR-0072's objection to a static site is a generator that shares units across views | gaps 1 (the same readers serve both) | Custodian decides whether to revisit K5 to K7; drafter drafts the units | A week for the units; the test depends on readers |
| **R7** | **Generate topic views** (bootstrap, admission, leases, confinement, emergency action, erasure, workflows, proofs, trusted-base rows) from the specification graph and the records' Depends-on and Superseded-by fields | The chronological index is the only way in. The graph has the edges, once it is rebuilt | gaps 9 | Drafter | Days, after gaps 9 |
| **R8** | **Add a register rule for new drafts**: no evaluative adjective where a claim and its condition will do; a comparison with prior work states its condition in the sentence that makes it. Put the rule in the drafting procedure. Do not raise errata for accepted text | ADR-0015 E2 is the cost of not having it. Accepted text is not worth an erratum per word | — | Drafter | An hour |

**What not to do yet.** Do not build ADR-0072's service before R6 has put a unit in front of a reader. Do not raise
errata on accepted records for length, history or tone; R2 and R3 address what a reader sees without touching
ratified text. Do not treat the session's grades ("outstanding", "weak") as findings; they are one reader's
judgment, and the claims under them are what §2 checked.

---

## Sources

- The session, verbatim: `derived/topak-documentation-design-assessment-2026.11.16/session.md`.
- `decisions/README.md`; `decisions/ADR-0003.md`, `ADR-0015.md`, `ADR-0016.md`, `ADR-0017.md`, `ADR-0018.md`,
  `ADR-0020.md`, `ADR-0025.md`, `ADR-0029.md` (A2), `ADR-0070.md`, `ADR-0071.md`, `ADR-0072.md`, `ADR-0073.md`,
  `ADR-0077.md`, at the passages cited, at `51d7f5b`; the same files at `b4a25a7` for C5 and C6.
- `checkpoints/topak-genesis-checkpoint-G12-2026.11.16.md` §1.
- `README.md`; `REVIEWERS_GUIDE_README.md`; `narrative/README.md`; `narrative/theory-of-operation.md` (revision 15),
  the passage on effect exclusivity.
- `spec/clauses.py`, its docstring, and its output for ADR-0033 (seven clauses).
- `derived/topak-critical-review-2026.11.11.md` (CR-40, CR-44, CR-47) and
  `derived/topak-gaps-prioritization-2026.11.11.md` (§1, items 1, 3, 5, 9).
- `derived/topak-external-assessment-2026.09.12.md`, its recovery note, for the claim in "Not independent".
