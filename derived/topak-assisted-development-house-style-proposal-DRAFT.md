# TOPAK's assisted-development house style: a design proposal

> I think there are three core components. the ADR skills, the formal modeling skills and the cicd skills. I'm
> constrained by the mechanism and some defining the mechanism and some implementing the mechanism.
>
> so the intent is two-part:
> 1. to formalize the house style for topak
> 2. to provide external skills which are transferable yet still harmonize
>
> here's a quick sketch:
> 1 the process starts with research and debate and analysis in AI sessions.
> 2 Once a design coalesces drafting of adrs can be done.
> 3. The full life cycle of the ADR should be well defined.
> 4. Reproducible Gates should be identified and honored, ideally enforced by the mechanism.
> 5. The chain of spec authority should flow from ADR to formal model to generated artifacts

> specifically about the cicd and the mechanism.
> concern earlier about conflating lineage between Claude and the custodian since the controls around claude's use
> of get and GitHub are not well constrained. this needs to be investigated separate from this session in detail.
> but for the purposes of this document, I think it is addressed by the controls that can be put in place. Branch
> protection, different signings. The pr review process The requirement for a second reader the requirement for
> specific reading at bootstrap.

(The custodian's two prompts in the session of 2026.11.18, as typed. "get" is read as git.)

**UNDATED DRAFT** · derived · a proposal, not a record · prepared by Claude at the custodian's request · basis: the
tree at `34e610c`, on branch `ccr-ded60498-y9i27e` · the custodian asked for it undated, committed and pushed, with
no pull request. It has no row in `derived/README.md`. It takes its date, its row and its freeze when the custodian
says it has settled, and until then it may change.

Nothing here is ratified, nothing here is a decision, and nothing here has been done. §2 is the custodian's. §4 is
the drafter's. §6 is the questions a record would be drafted from.

---

## 0. In one paragraph

The custodian's sketch is right, and most of it is already written down, in three Proposed records that the sketch
does not name: ADR-0057 for the chain of authority, ADR-0069 for gates and carriers, and ADR-0070 §5 for the two
halves of the developer. What the sketch adds is the skills as the place the style lives, and the second intent, that
some of them travel. What is missing is small and specific. No skill covers step 1. No skill covers gates or CI.
Nothing says where each gate is enforced. The seven skills agree on most conventions and disagree on eleven things
a reader can list. And the method has no record in force: G12 carries "An ADR-0029 criterion for assisted drafting"
as open item 66. The proposal is to consolidate and not to add: one short entry in ADR-0029, a conventions file the
skills share, two new skills, and each gate marked with what enforces it. The largest risk is the one the
11.11 prioritization opens with: "The corpus does not need more text."

---

## 1. Sources and method

**Read by the drafter, in full:** ADR-0029 (`a77e9b33163a67d5`); ADR-0057 (`31ca7e50eadb7363`); the three record
skills' `SKILL.md`, read earlier in the session; `derived/topak-sdd-alternatives-assessment-2026.11.06.md`
(`c85f4ba4f55399c8`); `.github/CONTRIBUTING.md`.

**Read by the drafter, in part:**
- ADR-0069 (`ea9d5c2e9c150387`): the provenance note, header, Context, §1 to §3a, §6 to §12. Not §4, §5, Options,
  Consequences, Open obligations, the Annexes or History.
- ADR-0070 (`353df070bfb2091d`): the provenance note, header, Context, §1, §5, §9 to §13, and the rows B15 to B29 of
  §2. Not §3, §4, §6 to §8, Options, Consequences, Open obligations, the Annex or History.
- `derived/topak-gaps-prioritization-2026.11.11.md` (`18ff8d26e9e3d740`): §0, §1 and the start of §2.
- `derived/topak-critical-review-2026.11.11.md` (`a2d52bc55a3f0852`): CR-61 only.
- G12 (`8a75e5240fed6db3`): the A2.5 line of §4, and items 66, 113, 114 and 115 of §7.
- `.github/rulesets/README.md`, its first sixty lines; `tools/ratchet.py`, its header; the step names of
  `.github/workflows/checks.yml`; ADR-0046 §1.

Long lines in ADR-0057, ADR-0069 and ADR-0070 were read cut at 1,100 to 2,600 characters, so the end of a long table
cell may not have been seen.

**Read by two delegated readers**, sessions of the same model as the drafter, which returned clause summaries and
quotations with line numbers: ADR-0046, ADR-0053 and ADR-0077, each reported as read in full; and the four portable
skills under `skills/`, with every reference file, reported as read in full, without their scripts, assets or evals.
The drafter checked twenty-seven of their quotations against the files and found all twenty-seven. What is taken
from those passes is marked *(reader)*.

**Not read:** ADR-0058, ADR-0022, ADR-0024 and ADR-0045 beyond one row; the Theory of Operation;
`derived/topak-specification-graph-2026.11.06.md`; the skills' scripts and evals; the ruleset JSON; GitHub's own
copy of the rules. Nothing was run for this document.

**Carried from the session:** `derived/topak-adr-skills-comparison-2026.11.18.md` (`bbe7205a5f0b4bc6`), written
earlier the same day, on this branch and not merged. Its SK-1 to SK-7 are cited below by id.

---

## 2. What the custodian said

Each is marked where §4 uses it.

| Mark | The custodian's statement |
|---|---|
| ⟨K1⟩ | There are three core components: the ADR skills, the formal modeling skills and the CI/CD skills |
| ⟨K2⟩ | "I'm constrained by the mechanism and some defining the mechanism and some implementing the mechanism" |
| ⟨K3⟩ | First intent: to formalize the house style for TOPAK |
| ⟨K4⟩ | Second intent: to provide external skills which are transferable yet still harmonize |
| ⟨K5⟩ | Step 1: the process starts with research, debate and analysis in AI sessions |
| ⟨K6⟩ | Step 2: once a design coalesces, drafting of ADRs can be done |
| ⟨K7⟩ | Step 3: the full life cycle of the ADR should be well defined |
| ⟨K8⟩ | Step 4: reproducible gates should be identified and honored, ideally enforced by the mechanism |
| ⟨K9⟩ | Step 5: the chain of spec authority should flow from ADR to formal model to generated artifacts |
| ⟨K10⟩ | The controls around the assistant's use of git and GitHub are not well constrained, and the conflation of lineage between the assistant and the custodian is to be investigated in detail, apart from this session |
| ⟨K11⟩ | For this document, that concern is addressed by controls that can be put in place: branch protection, different signings, the pull-request review process, the requirement for a second reader, and the requirement for specific reading at bootstrap |

**The drafter's reading of ⟨K2⟩**, for the custodian to correct (Q2): the mechanism that would enforce the gates
of ⟨K8⟩ is the thing the corpus is designing. Some of the three components define it, which is what the records
and the modules do, and some implement it, which is what the reference and the CI do. So the development process
cannot yet be held by the mechanism it describes, and has to say what holds it meanwhile.

---

## 3. What the corpus already holds

### 3.1 By step

| Step | Records | Skills | Checks | What is missing |
|---|---|---|---|---|
| 1. Research ⟨K5⟩ | None governs it. `derived/README.md` gives the form: "each dated and frozen: a derived document is never revised, a new one is written". ADR-0070 §9 (Proposed) has Detect and Register: "A finding without a row is lost" | **None.** The audit skill is "Not for … writing or fixing the document" | The frozen-files check, rule F2 | A skill; a rule for what ends the step |
| 2. Drafting ⟨K6⟩ | ADR-0029 §2: a record needs decision text. ADR-0057 §2 (Proposed) gives a clause four parts: Goal, Givens, Guarantees, Discharge | `drafting-records` | The record lint, ratcheted | What entitles a design to a number (SK-2). ADR-0057 §2 is adopted by no record, and the skill says not to adopt it unasked |
| 3. Life cycle ⟨K7⟩ | ADR-0029 §2 to §7, A2, A4: the statuses, the criteria C1 to C4, the reviewer, the provisional status. ADR-0070 §9 (Proposed): eight steps from Detect to re-reading the boundaries | `ratifying-records`, `cutting-manifests` | `batch_lint.py`, which "sees form only"; the manifests | An act for "the evidence arrived"; confirmation after bootstrap, which `ratifying-records` says has "no procedure here" |
| 4. Gates ⟨K8⟩ | ADR-0069 §6, §9, §10 and ADR-0070 §5.3 (both Proposed). ADR-0046 and ADR-0053 (Accepted) for the formal layer's own. ADR-0077 (Proposed) for the proofs in CI | **None** for CI. The formal skills carry their own gates | `checks`, `frozen-files`, `results`; five rulesets | Which gate is enforced by what (§4.3). The required-checks ruleset is disabled (G12 item 114) |
| 5. Chain ⟨K9⟩ | ADR-0057 (Proposed): the specification graph. ADR-0046 §2: "A proof is of the module" *(reader)*. ADR-0053 §1: "The TLA+ module, its TLAPS proof and the Rust stay canonical" *(reader)* | `writing-tla-specs-and-proofs`, `writing-lean-encodings-and-proofs` | `spec/proof-sync.sh`, `tools/lean-sync.sh`, the drift test, `spec/specification-graph.py` | A reader for the edges up (§4.4) |

### 3.2 Three Proposed records already say most of it

**ADR-0057 says the chain is a graph, and grades it.** Nodes are artifacts in open layers. Every edge has one of
eight types "ordered by what the edge leaves to a person": executed, generated, proved, proved of a reading,
replayed, tested, read, trusted. "A citation is not an edge." Its finding 5 is the sentence step 5 has to live
with: "The proofs are of the modules; the modules' fidelity to the records is read, and read by the hand that wrote
both." Of the 435 edges its §14 counts, 340 are read. The 11.11 prioritization says the graph needs rebuilding
before the record can be ratified.

**ADR-0069 says what a gate is, and what a carrier may do.** "A gate is a program in the repository, named by
digest, and it runs the same way by hand and on a carrier" (G-1). Its evidence counts "as more than an assertion
once a gate-evidence key, carried in the issued rules, signs it" (G-2). Git, GitHub and a CI runner are carriers:
"A carrier's approval is not a vote, and its merge is not a promotion" (C-1), and "A carrier's checks may refuse and
never admit" (C-2). For this repository, §10.3: "During genesis they promote nothing." Its degeneracy D-0069-2,
evidence attributed and not signed, says of itself "**This is today's position**".

**ADR-0070 §5 says who the developer is.** "The developer is two parties." The assistant "is to the corpus what a
Thinker is to the mechanism", excluded from the trusted base, and "**The assistant never votes**". The custodian
"is at the gate", and what the record asks is that the gate "be attributable and hard to steal". Its Status note
lists G11 item 66, "the criterion for assisted drafting", among the debts it would resolve, and its §11 owes
ADR-0029 an amendment for it. Its §9 has a closing rule the skills do not: "**A finding closes only when such a
check exists**".

None of the three is in force. ADR-0057's condition is marked met and no longer holds at the tree, by the 11.11
prioritization. ADR-0069 and ADR-0070 each list most of their conditions as not met.

### 3.3 The skills as they stand

| Skill | Where | Version, status | Evals | Repository-specific file |
|---|---|---|---|---|
| `drafting-records` | `.claude/skills/` | — | 3 | The whole skill |
| `ratifying-records` | `.claude/skills/` | — | 4 | The whole skill |
| `cutting-manifests` | `.claude/skills/` | — | 3 | The whole skill |
| `use-case-simulator` | `.claude/skills/` | — | 3 | Not read for this document |
| `writing-tla-specs-and-proofs` | `skills/` | 0.3.1, "A draft." | None: "It has no eval suite yet" | None. Its README says TOPAK's names were written out of it *(reader)* |
| `writing-lean-encodings-and-proofs` | `skills/` | 0.1.0, "A draft." | 3 | `this-repository.md` |
| `auditing-claims-against-evidence` | `skills/` | 0.1.0, "A draft." | 3 | `this-repository.md` |
| `generating-corpus-diagrams` | `skills/` | 0.1.0 | None | None, and its general files name TOPAK's paths *(reader)* |

Against ⟨K1⟩: the ADR skills are three and local. The formal modeling skills are two and portable. **There is no
CI/CD skill.** The only mention of CI in the seven skills read is one clause of the TLA+ skill *(reader)*. Two
skills fit none of the three: the audit and the diagrams, which are instruments for reading.

**What the seven share** *(reader)*: one layout (When to Use, When NOT to Use, Quick reference, Rationalizations to
reject, References); a "distilled from" sentence and a core principle; dotted dates; sixteen-hex digests; evidence
files that are regenerated and never edited; findings reported and not fixed; and the words for a result, as
`drafting-records` has them, "Proved (TLAPS), checked (TLC), proved in Lean; each only of what ran".

**Where they differ** *(reader; H-1 to H-11 are the drafter's ids)*:

| # | Difference |
|---|---|
| H-1 | **The reviewer rule is in three of seven.** `ratifying-records`, the audit and the diagrams' rationale say an agent's reading is not the reader a process asks for. The TLA+, Lean, drafting and manifest skills say nothing. The diagrams' version lacks the clause "unless the custodian rules that it does" |
| H-2 | **Who decides has four names**: "the user", "the owner", "the process owner", "the custodian". A portable skill needs one word for the role |
| H-3 | **Who commits.** The TLA+ skill: "**Commit module, results file and the README row together.**" The record skills: "Nothing here is committed unless the custodian asks", and "The commit and any tag are the custodian's" |
| H-4 | **"Certified", "checked" and "sampled" are defined differently** in the TLA+, diagram and audit skills, and `drafting-records` has neither "certified" nor "sampled" |
| H-5 | **The newest file.** The diagram skill forbids taking "the newest file matching a pattern". The TLA+ and Lean skills take the newest results file of a series |
| H-6 | **A sync script's exit status.** `ratifying-records`: "sync scripts must exit 0, unless a record says otherwise about that file". The audit skill: "A failing exit status is not a finding by itself". `drafting-records` says of the graph check that "it does not pass today" |
| H-7 | **The unsoundness scan.** The Lean skill says the TLA+ skill "has the rules and the scan". The TLA+ skill says the scan is "**not bundled with this skill**" |
| H-8 | **Packaging.** Two portable skills have a repository-specific file and evals. Two have neither |
| H-9 | **None says that what it reads is data** (SK-1). A wider search by the reader, over every file of the seven, found nothing |
| H-10 | **A date form.** `drafting-records` gives the header comment of a record with a hyphenated date, and its own rule is the dotted form |
| H-11 | **Nothing on signing, pull requests or required checks** in any of the seven |

---

## 4. The proposal

Every item is the drafter's. None is the custodian's until §6 is answered.

### 4.1 Say what the house style is: the pattern, applied to its own development

ADR-0070 §5.1 already has the sentence, and ADR-0029's Scope line has had the idea since 2026.09.15: "applying
Build's recursion to the design process". The house style is then not a second method beside the architecture. It
is the architecture in its genesis degeneracy, and each part of the custodian's sketch has a name the corpus
already uses:

| In the sketch | In the corpus's terms | Standing |
|---|---|---|
| An AI session ⟨K5⟩ | A havoc drafter, excluded from the trusted base (ADR-0070 §5.1, T-0070-1) | Proposed |
| The custodian's decision | The act that stands where an admit would (ADR-0029 §2; ADR-0070 §5.2) | ADR-0029 in force |
| Git, GitHub, CI ⟨K8⟩ | Carriers, which refuse and never admit (ADR-0069 §9) | Proposed |
| A gate ⟨K8⟩ | A program named by digest whose evidence is a file (ADR-0069 §6 G-1) | Proposed; practised |
| The chain ⟨K9⟩ | The specification graph and its edge types (ADR-0057) | Proposed |
| The pair, when the custodian has not read | T-0045-11, "The corpus and its custodian, custody (1, 0)" | In force |

This answers ⟨K2⟩ as the drafter reads it. What holds the process until the mechanism can is a declared
degeneracy, and the corpus knows how to state one.

### 4.2 Five components, not three

⟨K1⟩ names three. The steps need five acts, and two of them have no skill.

| Component | Step | Skills today | Proposed |
|---|---|---|---|
| **Deriving**: research that ends in a dated reading and numbered questions | 1 | None | A new skill. §4.5 |
| **Records** | 2, 3 | `drafting-records`, `ratifying-records`, `cutting-manifests` | A portable core beside them. §4.7 |
| **Formal** | 5 | The TLA+ and Lean skills | Brought into step. §4.7 |
| **Gates** | 4 | None | A new skill, last. §4.3 |
| **Reading**: the audit, the diagrams | every step | The audit and diagram skills | Kept as instruments. Not a reviewer, and they say so |

*(Drafter's choice: Reading is a component and not a part of each of the others. The alternative is live, Q1.)*

### 4.3 Every gate says what enforces it

⟨K8⟩ asks that gates be "ideally enforced by the mechanism". The corpus's records already separate four things
that can enforce a rule, and today's gates sit at the first three.

| Tier | What enforces | The corpus's words | Weakness |
|---|---|---|---|
| **Prose** | A skill's text, followed by the assistant | "The rest is skill prose" (ADR-0070, Context) | Nothing checks it |
| **Harness** | The session's permission list | `.claude/settings.json`: a deny, two asks, plan mode | The assistant can write `.claude/`, and no manifest measures it (ADR-0070 F7) |
| **Carrier** | CI and the rulesets | "may refuse and never admit" (ADR-0069 C-2) | Evidence is attributed, not signed (D-0069-2) |
| **Mechanism** | A fact in the log, or an object signed under an issued key | ADR-0069 P-2, G-2 | Does not exist during genesis |

Where today's gates are, as the files read say:

| Gate | Tier | Note |
|---|---|---|
| Accepted text changes only by a typed row | Prose | ADR-0029; the record skills. The frozen-files check covers files, and leaves a record's content to what "the custodian checks at review" |
| Every Met carries its evidence | Prose | ADR-0070 §5.1 (Proposed) adds that CI re-runs it |
| Ask before a commit or a push; plan mode | Harness | |
| The pins, `spec/proof-sync.sh`, every manifest at its commit | Carrier, strict | Not required: ruleset 03 is disabled |
| The corpus pins, `tools/lean-sync.sh`, path citations, the record lint | Carrier, ratcheted | The ratchet ignores a checker's exit status (ADR-0070 F6; `tools/ratchet.py` says so of itself) |
| The frozen-files check | Carrier | Named for ruleset 03, disabled |
| TLC, the reference's tests, the Lean builds, the floor's gates | Carrier | "read at review"; never required |
| Signed commits, a pull request for every change, merge commits only | Carrier, active | Ruleset 01 |
| A code owner's approval | Carrier, active | Ruleset 02, with the custodian's bypass |
| Tags: the custodian creates, nobody moves | Carrier, active | Rulesets 04 and 05 |
| Ratification | The custodian's act | ADR-0029 §2. Not a carrier's (ADR-0069 §10.3) |
| Anything at the mechanism tier | — | None |

**The proposal:**

1. **Each gate carries its tier on its face**, in the skill that names it and in the record that owns it, as a
   ratification condition carries Met or Not met. A gate at the prose tier says so.
2. **A gate moves up without its skill changing.** The skill names the gate and what it asks. A table, kept in one
   place, says what enforces it today.
3. **The portable contract stops at the carrier.** An adopter has no mechanism. What a transferable skill may
   promise is G-1, a program that runs the same by hand and on a carrier, with ADR-0070 §5.3's two rules: it fails
   closed, and a change is graded by the base's copy of the checker.
4. **A gates skill is written last** *(drafter's recommendation)*, after ADR-0069's four open questions and F6 are
   settled. A skill distilled from two Proposed records that conflict (ADR-0070's Context table says "They
   conflict") would freeze the conflict.

### 4.4 The chain is ADR-0057's graph, with findings flowing up

1. **Step 5 is ADR-0057, and the proposal adds nothing to it.** "From ADR to formal model to generated artifacts"
   is the graph read downward. ADR-0057 itself rejects a tree: "One clause is read by several modules and one module
   reads several clauses".
2. **Authority flows down and findings flow up.** ADR-0046 §5 corrects a premise table from a proof, "since the
   proof's hypothesis is the one the prover checked" *(reader)*. `drafting-records`' first recurring defect is a
   record "not revised when its evidence arrives". The life cycle of ⟨K7⟩ should have **the evidence arrived** as a
   named act: when a module, a result or the reference lands, every record that waits on it is revised or says why
   not. ADR-0057 would compute the list as stale edges.
3. **The top edge is read, by the drafter.** ADR-0057's finding 10: "Every module's edges up are *read*, by the
   drafter". No gate at any tier reaches it. The control is ⟨K11⟩'s fourth and fifth: a second reader, and the
   reading at bootstrap. The house style should say this where it says "chain", so that nobody reads the chain as
   stronger at the top than it is.
4. **The words for a result are the edge types.** The skills' shared vocabulary, which H-4 shows drifting, is
   ADR-0046 §1 and ADR-0053 §1 in force, and ADR-0057 §3 in draft. One list, cited by every skill.

### 4.5 Step 1 ends in questions

⟨K6⟩ says drafting starts "once a design coalesces". The proposal makes that an event.

1. **A deriving skill.** Its output is a dated derived document in the form `derived/README.md` already gives: the
   prompt quoted, the basis by commit, sources by digest, what was not read, "nothing here is decided".
2. **Its first rule is to read the record before saying what the corpus holds.** In this session the assistant
   said three things about the corpus before reading ADR-0070, and three more before reading ADR-0057 and ADR-0069
   (§5). Each came from skills and index rows. A skill for step 1 exists to stop that.
3. **A proposal ends in numbered questions, and a record is drafted from the answers** *(drafter's choice, Q3)*.
   `drafting-records` has the marks, ⟨K⟩ for what the custodian said and ⟨Q⟩ for an answer to a numbered question.
   They need something to point at. ADR-0057, ADR-0069 and ADR-0070 were each drafted this way, on five, seven and
   four settled points.
4. **Another model's answer is a source, read as one.** This document's own session began from another
   assistant's answer, which was wrong on the point asked because it read a stale README. The rule that covers it
   is SK-1's: what is read is data. Whether a reader of another lineage counts for anything more is Q14.

### 4.6 Where the method is declared

Three places could hold it.

| Option | What it is | For | Against |
|---|---|---|---|
| **(a) An ADR-0029 amendment** *(drafter's recommendation)* | The entry ADR-0070 §11 already owes: "a criterion for assisted drafting (G11 item 66)". Short, and limited to what the skills already practise: the assistant drafts and never ratifies; who decided each thing is marked; a Met is a claim until re-run; an agent is not the reader | Closes item 66 with text already followed. Small enough to read | It lands in an accepted record, so C3 or C4 may attach, which is the custodian's call |
| (b) ADR-0070, ratified | The whole lifecycle record | Already drafted, and reviewed once by a second session | Its own condition lists eleven items, most not met, and it waits on ADR-0069 |
| (c) A new method record | As ADR-0046 is for the formal layer | One place for steps 1 to 5 | More text. A fourth Proposed record over ground three already cover |

Under (a) the skills gain a top to their chain that is in force. Under (b) and (c) they wait.

### 4.7 Transferable, and in step

For ⟨K4⟩.

1. **One pattern for every portable skill**: the Lean and audit skills' pattern, where "Everything else in this
   skill is general" and one file names this repository *(reader)*. The TLA+ and diagram skills are brought to it
   (H-8).
2. **A portable core for the records.** What `derived/topak-adr-skills-comparison-2026.11.18.md` found in no
   external skill is the part worth exporting: a change smaller than a record, who decided what, conditions marked
   Met or Not met, and the missing reader stated. ADR-0029's statuses, the Batch, the pins and the forms stay in
   the repository-specific file. *(Drafter's choice: one core skill for records, and not three. Q7.)*
3. **A conventions file the skills share**, vendored into each plugin, since a plugin is installed alone. It holds
   what §3.3 lists as shared, and settles H-1 to H-7 and H-9 to H-10 once: the reviewer rule with its clause; one
   word for who decides; who commits; the words for a result; the newest-file rule; what a sync script's exit
   status means; and the sentence that what is read is data.
4. **A check that the copies agree**, at the carrier tier. That is what "harmonize" means when it is checked.
5. **The portable words for the roles.** In a portable skill the custodian is "the owner of the decision", and the
   repository-specific file says who that is. *(Drafter's choice of the word. Q7.)*
6. **Skills are artifacts in the chain.** A skill is distilled from a record, and its evals are its planted-defect
   tests: `stop-on-unmet-condition` is a prompt built to make the skill do the wrong thing. So a skill has a
   source it cites, a version, and evals that run. Under ADR-0070 §5.1 ⟨R1⟩ a change to `.claude/` is "drafted
   alone" and "read as a change to a floor". Whether `.claude/` and `skills/` enter the manifests is a change to
   `manifests/EXCLUDE`, which `cutting-manifests` calls "a corpus decision a checkpoint records" (Q9).

### 4.8 The gate and who stands at it

For ⟨K10⟩ and ⟨K11⟩. The investigation ⟨K10⟩ asks for is not done here.

| Control ⟨K11⟩ | Where the corpus has it | Tier | Standing | What it answers |
|---|---|---|---|---|
| Branch protection | Rulesets 01, 02, 04, 05; ADR-0070 §5.2 | Carrier | Active, by the export of 2026.11.16. Ruleset 03 disabled | Whether a change reached `main` without a pull request |
| Different signings | ADR-0070 §5.2: a hardware-held key, a tracked allowed-signers file, a ratification as a signed tag; T-0070-3 | Carrier, then issued | Proposed, not built. G12 item 115 lists signed tags as open | Who performed the act |
| The pull-request review | Ruleset 02; `.github/CONTRIBUTING.md`'s lanes; ADR-0070 §5.1: "A session's pull request touches one record" | Carrier, and the custodian's act | Active. The bound on what a merge reads is Proposed | Whether the custodian saw it |
| A second reader | ADR-0029 A2 and A2.5; the last item of every ratification condition; `ratifying-records` | A person | None engaged (G12 §4) | Whether what is in force was read by someone who did not write it |
| Specific reading at bootstrap | ADR-0029 A2.1: "an **independent review of the entire corpus**", at "one named manifest digest". A2.2: its attestation in the genesis bundle. §5 step 6: floor fitness | The ceremony | In force, not yet due | The same, for everything, before epoch 0 |

**The five are two kinds, and the house style needs both.** The first three are about the act: who did it, and
whether it could have been done unseen. They are carrier controls, so by C-2 they can refuse and cannot admit. The
last two are about the content: whoever typed it, did a second person read it. Those two do not depend on telling
the assistant from the custodian, which is why ⟨K11⟩ holds for this document.

**What the worst case is called.** ADR-0070 §5.1 ⟨R1⟩: "Where A-0070-1 does not hold, the assistant and the
custodian together are T-0045-11's identity." The conflation of ⟨K10⟩ is that row, already a trust root every
theorem rests on, and the bootstrap review is what the corpus has set against it.

**What stays owed, outside this document:** A-0070-2, "No credential that can write the default branch or a tag is
reachable from an assistant session", which ADR-0070 says "was not checked"; SK-4 to SK-7 of the comparison; and
the freshness gap ADR-0070 §10 names, that a signed tag is "necessary … and not sufficient".

### 4.9 Budget the custodian's reading

CR-61: "the corpus can now be extended faster than it can be kept true". Every tier of §4.3 below the mechanism
ends in the custodian reading something. A house style that makes drafting easier and leaves reading where it is
makes CR-61 worse. Three rules, each already drafted somewhere:

1. **One thing per pull request** (ADR-0070 §5.1 ⟨R1⟩, a drafter's recommendation there).
2. **Drafting waits while reading is behind** (ADR-0070 §5.3: "new drafting waits"). The number is the
   custodian's (Q11).
3. **Step 1 is where volume belongs.** A derived document binds nothing and freezes. Ten of them cost the
   custodian less than one record ratified unread.

### 4.10 An order, offered

1. The investigation of ⟨K10⟩, which is the custodian's to commission.
2. The answers to §6.
3. The ADR-0029 entry of §4.6 (a), drafted from them.
4. The conventions file, and the seven skills brought into step with it. No new skill yet.
5. The deriving skill.
6. The portable core for records.
7. The gates skill, after ADR-0069 and ADR-0070 have been read by the custodian.

Items 3 to 6 add about one page of record text and no new record. That is deliberate.

---

## 5. Corrections to what the assistant said in the session

Said before the close reading, and not stood behind:

1. **"Assisted development has no such record", and the skills "are currently the top of their own chain".**
   Short. ADR-0070 §5 is that record in draft, and its §11 owes the ADR-0029 entry. The skills sit under a
   Proposed record, which is not the same as under none.
2. **Three tiers of enforcement, offered as the assistant's idea.** They are ADR-0069's: C-2 for the carrier, P-2
   and G-2 for the mechanism. §4.3 adds only the split of the bottom tier into prose and harness.
3. **"The method record is the place to start."** Revised to §4.6 (a), after reading the prioritization's §0.
4. **That step 5 "is a graph", as an adjustment to the sketch.** It is ADR-0057's decision, with the custodian's
   own ⟨K1⟩ to ⟨K5⟩ of 2026.11.06 behind it. The sketch's "chain" and the record do not disagree.

---

## 6. Questions for the custodian

A record or an amendment would be drafted from the answers, each marked ⟨Q⟩.

1. **Components.** Five, as §4.2, or three as ⟨K1⟩ with deriving and reading folded in?
2. **The constraint.** Is §2's reading of ⟨K2⟩ what was meant?
3. **The handoff.** Must a record be drafted only from answered, numbered questions, as §4.5 item 3?
4. **Where the method lives.** §4.6's (a), (b) or (c)? If (a), does C3 or C4 attach?
5. **Tiers.** Are the four tiers of §4.3 adopted, and does each gate state its own? Is ruleset 03 to be enabled now,
   which G12 item 114 says waits on an import?
6. **The four-part clause.** ADR-0057 §2 asks records drafted after it for Goal, Givens, Guarantees, Discharge. Is
   that adopted for new records before ADR-0057 is ratified, or not until?
7. **Portability.** One portable records skill or three? Which skill goes first? Is "the owner of the decision" the
   portable word for the custodian?
8. **The conventions file.** Wanted? If so, how is each of H-1 to H-7 settled: above all H-3, who commits, and
   H-6, what a failing sync script means?
9. **Measuring the skills.** Do `.claude/` and `skills/` enter the manifests? Do the evals run in CI, and at what
   tier?
10. **The identity investigation.** Who does it, against what list (A-0070-2 and SK-4 to SK-7 are a start), and
    where does its result land: an R-revision of ADR-0070, or a derived finding first?
11. **The pace bound.** Is there a number of records that may stand Proposed and unread before drafting waits?
12. **The gates skill.** One skill, or a section in each? Before or after ADR-0069's four open questions?
13. **The evidence arrived.** Is it a named act of the life cycle, and what triggers it: the drafter, or a stale
    edge a check reports?
14. **A reader of another lineage.** ADR-0070 §5.1 says a second session of the same model gives "independence of
    context and not of lineage". Does a model from another maker count for more, and for what? It is not ADR-0029's
    reader unless the custodian rules that it is.

---

## 7. What this does not show

- **That any of it works.** Nothing was built or run. The skills' behaviour was not tested, and their evals were
  counted and not run.
- **Anything from a section §1 lists as unread**, ADR-0058 above all, which is the record for adopters and bears
  on ⟨K4⟩.
- **Independence.** The drafter and both delegated readers are one lineage, the one that drafted the skills and
  most of the records read. This is a reading in a fresh context, and it is not ADR-0029's reader.
- **GitHub's rules in force**, which were read from an export.
- **The custodian's view** beyond the two prompts quoted at the top.
