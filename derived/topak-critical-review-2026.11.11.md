# TOPAK — Critical Review

**2026.11.11** · derived · review, not a record · basis: Theory of Operation revision 15 (`e737aa042625678d`), Genesis
Checkpoint G11 (`9d6f95f444455510`), the sixty-seven record files, `spec/`, `floor/`, `policies/`, `mechanism/`, the
diagrams, the skills and every document under `derived/`, all at commit `bbda621` (2026.11.10), with the 09.16, 09.25
and 10.02 critical reviews · the head of five documents written together as the self review of 2026.11.11: this review,
`topak-open-findings-register-2026.11.11.md`, `topak-feature-list-2026.11.11.md`,
`topak-residual-risk-statement-2026.11.11.md` and `topak-gaps-prioritization-2026.11.11.md`, with their annex,
`topak-self-review-annex-2026.11.11/` · the manifests, the reference checker, the sync checks, the specification graph's
check, TLC over ten modules, the reference's tests, trace validation, the Rego tests, the Cedar gates and the diagram
regeneration were **run against this tree**, in a clone, and their results are in §1 · the TLAPS proofs, their
certification, the unsound-case scan, the Lean packages and the rehearsal were **not** re-run · the external
documents were **not** re-read · prepared by the assistant at the custodian's request

Nothing here is ratified, and this document proposes no decision text. Findings continue the tags of the earlier
reviews: CR-1 to CR-20 are the 09.16 review's, CR-21 to CR-26 the 09.25 review's, CR-27 to CR-39 the 10.02 review's,
and CR-40 onward are new. The brief is the custodian's of 2026.11.10: **a comprehensive self review of TOPAK as it
stands proposed.** So the subject is the whole tree, sixty-seven records of which eighteen are Proposed, and not
only the state of record. Every finding says which it is against: text in force, Proposed text, a pending
amendment, a living document, or evidence.

**Not independent.** This is the drafter's review of the drafter's work. The corpus was drafted by this assistant
at the custodian's direction; so were this review, the thirteen readers that read the tree for it, the fourteen
verifiers that checked what the readers and the lead found, and the ten graders that re-graded the earlier findings
and the earlier feature rows. Each
reader, verifier and grader was a fresh context with a fixed brief, and the readers were not shown any earlier
review. That is independence of context. It is not independence of lineage, which is the failure ADR-0035 is
about, and it is not the reader ADR-0029 A2 asks for. This review does not count under A2.1, alters nothing in the
A2.5 line, which stays "None / None", gives no verdict on floor fitness, and dispositions nothing.

---

## 0. Verdict

Five weeks ago the 10.02 review found a corpus that measured itself harder than its design deserved and that had
never been read by anyone but its authors. Both halves still hold, and the first has come apart from the second in
a new way. **The machinery for catching drift works wherever it is run, and since G11 the corpus has mostly
stopped running it on itself.**

What holds was run, not read. Every one of the thirty dated manifests verifies at the commit it measured. All 321
TLC rows of the command-chain overlay's eight modules regenerate from their rows files with the expected outcome
and the same state counts, on a different machine and a different Java. All five floor gate runs reproduce their
committed verdicts on a second platform, differing in three lines each, which are digests. The reference's 155
tests pass on the first run. Thirty-two proof modules are in step with their modules and the prover's pin, and
every one of the fifty-six digests the overlay's records cite matches the file it names.

What does not hold is the state of record. HEAD is seventy-one commits past G11. Two batches were ratified in
November and stand only as History rows: no checkpoint, index or narrative names them, and the narrative still
says of the prover's defects what Batch 39 made false. Thirteen records were drafted after the cut, ten of them in
one day with eight modules and 5,600 proof obligations, and 190 tracked files are measured by no manifest. The
decisions index heads its status column "Status at G8". Of 460 earlier findings gathered from the corpus's own
dated documents, 252 are still open and 108 of those are carried by no list. The readers of this review reported
493 findings; 485 stood after a second agent checked each against the files.

None of the 485 shows a proved theorem to be false of its module. What they show is a corpus whose **edges
have outrun its centre**:

- **The overlay claims a status the process does not have.** Ten records say "Proposed, an overlay, not the
  archetype", and eight of them that C3 does not apply while that lasts. ADR-0029 §3 has no such class and §4 no such
  suspension; ADR-0058, itself Proposed, defines an overlay as a deployment's graph; and the admission test in
  force says the archetype is extended before a variation is admitted (CR-40).
- **Text in force rests on a record that is not.** ADR-0024 A2.2, in the bootstrap set, reads an independence table
  that only ADR-0035 defines, and ADR-0035 has been Proposed since 2026.09.25 (CR-42).
- **Seventeen ratification rows say "The reference follows the text", and for several the reference's own register
  says it does not** (CR-43).
- **Break-glass was retired as a floor exception in Batch 34, and the retirement was not carried through.** ADR-0015
  still classifies it as one; ADR-0043 §2 still says only a `thinker` seat holds `Actuate`, and an invariant proved
  against that clause is no longer a statement of the design in force; the reference's rules floor still implements
  the old R6 and R7 (CR-45).
- **What is in force cannot be read off the page in several places a reader would look first** (CR-47).
- **The overlay's records say more than their modules state**, in ways the day's two revisions did not catch
  (CR-48), and ADR-0056 contradicts itself on whether a user's signed assertion is on the record (CR-51).

| Graded | 10.02 | **2026.11.11** | In one sentence |
|---|---|---|---|
| The repository as an architecture corpus | A− | **B+** | Every check that was run held, and that is the same machinery as before; the grade falls because the corpus is no longer kept at its own standard between cuts: no cut in seventy-one commits, indexes two to three checkpoints stale, checkers that exit 0 on a failure, and a backlog nobody has dispositioned |
| The repository as evidence that the architecture works | C+ | **C+** | Unchanged in kind: no real principal is `Contained`, the reference follows two Proposed records on a floor stage not in force and one of its traces no longer replays through the operational model, nothing of the overlay is built, and no reader who is not the drafter has read any of it |
| Moon & Varshney · TACIP draft · NIST AI RMF Playbook | B+ · B+ · B | **not re-made** | The sources are not in this tree and were not re-read; §2 says which rows the two batches moved and which the Proposed records would bear on |

The pattern's most distinctive virtue is intact: almost every defect below was found by reading the corpus against
itself, with tools the corpus built for that. Its most distinctive vice has a new form. On 10.02 the vice was
proofs of the design written by the design's drafter. Today it is that **the drafter can add ten records, eight
modules and their proofs in a day, and nothing in the process slows that to the speed at which the rest of the
corpus can be kept true.**

---

## 1. What was verified, and held

Run against the tree at `bbda621`, in a clone, with nothing written to the repository. The outputs are in the
annex (`runs/`).

- **`tools/verify-manifest.sh --all`: all thirty dated manifests verify at the commit each measured**, G1 to G11,
  eighteen reference cuts and the `slm/` cut, each with its expected count. The clone was shallow at 127 commits
  and had no tags; it was unshallowed to 275 and its forty tags fetched first.
- **`shasum -a 256 -c manifests/SHA256SUMS-G11` at this tree: 594 of 604.** The ten are ADR-0024, ADR-0033,
  ADR-0045, ADR-0046 and ADR-0053, the three narrative files, `spec/deadlock-audit.sh` and
  `spec/proof-certification.md`. A cut today would measure 794 files, 190 more than G11: thirteen records,
  eighty-six derived files, seventy under `spec/` and twenty-one under `skills/`. The newest reference manifest,
  `SHA256SUMS-REF-2026.10.09`, verifies 112 of 116 at this tree (CR-55).
- **Clause pins at four commits** (`spec/clauses.py` over every record at `fccf374`, `ce8f460`, `baddd63` and
  `bbda621`): 219 clauses at the 10.02 review's commit, 306 at G11, 423 today. Since the last review 204 clauses
  are new and 51 changed. Since G11 117 are new and three changed (ADR-0045 §3 and Annex B, ADR-0053 §5). After
  the commit that froze the overlay's modules, nine overlay clauses changed (ADR-0060 §5 to §7; ADR-0062 §3, §8,
  §11; ADR-0063 §3; ADR-0067 §3, §4): the second revision, which each record says changed no module.
- **`tools/check-refs.py`: exits 1, with 24 missing paths and 6 dates.** Twelve are installs or directories the
  corpus declares untracked, three are the string "tools/call", three are a path written with a line number, five
  are "spec/theorem-premise-binding" cited without its extension by ADR-0047, 0048, 0050, 0051 and 0052, and one is
  a file G11 itself says was removed at its cut. The script's header says 26 and 7 (CR-57).
- **`spec/proof-sync.sh`: thirty-two proof modules IN SYNC**, and every results file cites the pinned prover. It
  exits 1 because `Workflow.tla` and `Mesh.tla` have no proof and no recorded reason (G11 item 101). The results
  files, read and not re-run, sum to **11,016 obligations**: 5,416 for the twenty-four modules G11 counts and 5,600
  for the overlay's eight. Twenty-nine modules certify; `Confinement`, `Confinement_A1` and `RulesFloorNV_rev5` do
  not, as at G11. 178 obligations are LS4 temporal steps that no checker confirms.
- **`tools/lean-sync.sh`: exits 1.** `spec/lean` and `floor/lean` are in sync; `mechanism/lean` is stale, by the
  custodian's decision of 2026.10.08 (G11 item 103). Seventeen proved modules have no Lean encoding, the overlay's
  eight among them.
- **`spec/specification-graph.py check`: exits 1**, where its committed results of 2026.11.07 pass. The graph
  (419 nodes, built at `9749dfa`) has no node for ADR-0059 to ADR-0068 or their modules, and ten edges are stale
  where the committed file has eight (CR-52).
- **`spec/inventory.py --check` passes** (43 rows, 34 non-row premises, 18 derived premises), and
  `spec/premise-routes.sh` reproduces its file of 2026.11.03 but for ADR-0045's digest. Twenty-one of the
  thirty-nine modules in `spec/` have no theorem row in the binding.
- **`mechanism/corpus-pins.sha256`: 61 of 61. The overlay's digest citations: 56 of 56.**
- **TLC, regenerated from rows files.** The overlay's eight modules: 321 rows, every one as expected, every state
  count identical to the committed file. `Coupling_live`: 69 rows, the same. `Workflow`: 33 sections, the same
  outcome in all 33, and the same state counts in the eleven that hold (the others stop at a counterexample, and
  were run on one worker). The deadlock audit of the eight overlay modules reproduces line for line.
- **`cargo test --workspace --release`: 155 tests pass on the first run**, the count `mechanism/README.md` states,
  the two drift tests among them, and `contain.rs` 14 of 14 in three seconds on a loaded machine (CR-39).
- **`spec/mechanism-trace-results.sh`: 83 traces, 1,053 steps; 82 MATCH and one ERROR.** The trace that does not
  replay is the end-to-end workflow test. The committed file of 2026.10.05 has 82 traces, all matching (CR-55).
- **`opa test policies/`: 38 of 38**, under OPA 1.4.2. No results file for the Rego tests is in the tree.
- **The floor gates, on a second platform.** `cedar-policy-cli` 4.13.0, cvc5 1.4.0 and the pinned ethos commit,
  built for Linux where the recorded runs are macOS. The genesis floor validates and its 62 cases pass; the four
  stages validate with 74, 106, 107 and 123 cases; `floor/proposed/build.py` regenerates the tracked stage files
  byte for byte; and each of the five gate runs differs from its committed results file in exactly three lines,
  the solver's digest, the checker's digest and the evidence tree's. Every verdict is the same.
- **The diagram family, regenerated under its pinned Python 3.9:** 48 of 52 unchanged; G1, G3, H6 and H7 change.
- **The corpus's checkers, tested with planted defects** in a throwaway clone (CR-57): a bad path under `spec/`,
  a bad date, an edited proof module, an edited proved module, a changed clause of a pinned record and a
  disagreement between the binding table and its JSON are each reported. A bad path under `skills/` or
  `diagrams/`, a changed clause of an overlay record, an edited TLC results file and a failed manifest's exit
  status are not.
- **One finding was settled by running the floor.** A reader reported that the `emergency` stage, the floor in
  force, permits an operator's `Renew` or `Regrant` of an emergency seat. Two requests built from the stage's own
  cases, with the resource changed to a seat of kind `emergency`, are decided **allow** by `C2-renew` and
  `C1-regrant-successor` (CR-46).

Not re-run: the TLAPS proofs, their certification and the scan (the prover's pin is a macOS build, and a run on
another build is not a result the corpus could cite); the three Lean packages (the same); the `slm/` rehearsal
(Apple silicon); the live smoke run (no container runtime; not repeated by anyone since 2026.09.25).

As on 09.25 and 10.02: where this review says evidence is insufficient, it does not mean it is fabricated. Nothing
that was run came back different from what the corpus recorded, except where the tree had moved.

---

## 2. The external documents: what moved, and what would

No mark is re-made. The Playbook, the TACIP draft and Moon & Varshney are not in this tree and were not re-read,
so the 10.09 alignment (`topak-external-alignment-2026.10.09.md`) stands as the reading, at M 11 · P 27 · C 3 ·
G 3 · X 28. Two things have happened under it.

**The two batches ratified since.** The 11.05 feature list (§13) said what they would move, and this tree confirms
each:

| Row | Mark at G11 | What Batch 38 or 39 changes |
|---|---|---|
| GOVERN 4.3 | P | The half held against it, "the defects reported to their maintainer", is done: tlaplus/tlapm#309 and #310, 2026.10.18 (ADR-0046 A3) |
| MANAGE 4.3 | P | The same half: communication to the maintainer of a defective component |
| MEASURE 2.7 | P | Its sharing clause |
| MANAGE 3.1 | P | "The defects unreported to the third party" no longer holds |
| Moon & Varshney | | ADR-0024's miscitation of §4.6, "blocking for any external draft" on 10.09, is corrected by ADR-0024 E1 (Batch 38) |

None of the four rows changes its mark on that alone, and none of the living documents says any of it yet (CR-41).

**The Proposed records, if they were ratified.** A reading of the records against the alignment's notes, and not
of the Playbook:

| Row | Mark at G11 | What ADR-0056 to ADR-0068 would bear on |
|---|---|---|
| MEASURE 1.3, independent assessors | G | **Larger today**, ratified or not: thirteen more records, eight modules and 5,600 obligations are one hand's |
| MAP 3.4, operator proficiency | G | Would grow: ADR-0066 has a person at a `release` seat act singly on an irreversible effect, and says nothing of that person's skill |
| MEASURE 3.2, tracking where metrics are unavailable | G | Would grow: `K_up`, the tick period, the freshness window, the capture floor, the charter's budgets and schedule are new numbers nobody has declared |
| MANAGE 2.4, supersede, disengage, deactivate | M | Would gain a plane fence and a revocation bounded in effects, and would lose "in time" below the intent boundary: after a revocation is ordered, an honest plane's vehicles may still produce fewer than `K_up` effects, with no bound on how long that takes (ADR-0063) |
| MAP 3.5, human oversight defined and assessed | P | Would gain the intent boundary and the release seat as definitions; the unattended posture is undecided (ADR-0060 §5) |
| GOVERN 1.6, inventory | P | Would gain an inventory of specifications at every grade (ADR-0057, ADR-0058); of systems, still nothing |
| MEASURE 2.10, privacy | C | ADR-0056 binds a call to a user and puts the binding inside the unit of erasure, which is the first text with a privacy framing; it contradicts itself on that point (CR-51) |
| GOVERN 6.1, MAP 4.1, third parties | X | ADR-0058 §7 would have suppliers publish subgraphs; no supplier exists |

**TACIP and Moon & Varshney.** Nothing in the Proposed set narrows the distance the 10.02 review and the 10.09
alignment measured. The paper's central artifact, a checked refinement to running code, is no nearer: stage one
of the corpus's chain now fails on one trace (§1). The profile's concern about verifiers written by the system
under review (12.2.1) applies to this review by name.

---

## 3. The earlier findings, at the pin

CR-1 to CR-39, each re-graded against this tree by a grader that opened the files. The full row, with the line
each check rests on, is in the register (§2.1 to §2.3) and its annex. Of the thirty-nine: 5 open,
17 partly addressed, 11 that appear addressed, 1 superseded
and 5 that cannot be told from the tree, each of those five written against a draft article that
is not in it. "Appears addressed" is not "closed": for most of these rows it means a record now exists, ratified
by its drafter (register, §5).

| # | Finding, in the earlier review's terms | At the pin | What was checked | Carried by |
|---|---|---|---|---|
| CR-1 | Effect exclusivity is still an assumption; 'strictly stronger than Moon & Varshney' is an overclaim until a confinement mechanism exists | **partly addressed** | 10.02: narrowed, open (derived/topak-critical-review-2026.10.02.md:377). Pin: the comparison is conditioned (decisions/ADR-0015.md:82 E2; narrative/theory-of-operation.md:923-926 'still identical in strength'); the design is in force (ADR-0034) and the mechanism is not: no real principal is Contained … | G11 item 1; G11 item 36; GAPS G1; derived/topak-residual-risk-statement-2026.10.09.md §1.2 |
| CR-2 | Detection fails open: Observer liveness is never coupled to admission; a dead, partitioned or colluding Observer looks like a clean system; no honeypots; L unmeasured | **partly addressed** | 10.02: three of four cases closed by ADR-0039; collusion open; residual-risk statement unwritten (derived/topak-critical-review-2026.10.02.md:378). Pin: ADR-0039 in force (decisions/ADR-0039.md:12); collusion declared and uncovered (narrative/theory-of-operation.md:2229 A13 … | ToO §13 A13; G11 item 51; G11 item 47; derived/topak-residual-risk-statement-2026.10.09.md §1.3 |
| CR-3 | No delegation or chain model: W < L < D is per-principal; the cross-principal correlator ADR-0023 reverses ADR-0008 toward is named but unspecified | **partly addressed** | 10.02: untouched (derived/topak-critical-review-2026.10.02.md:379). Pin: answers exist only as Proposed text: the correlator's folds (decisions/ADR-0051.md:14), delegation closed 'by position' in a workflow (decisions/ADR-0054.md:20, :70, :378), one subject per round (decisions/ADR-0056.md:30). Nothing is in force; a sequence … | G11 item 51; G11 item 44; G11 item 97; G11 item 101 |
| CR-4 | The formal layer is promissory: no Contain specification; TLC versus TLAPS undeclared; no refinement from any specification to any implementation | **partly addressed** | 10.02: substantially discharged; the refinement, the uncertified prover, practical constants and liveness remain (derived/topak-critical-review-2026.10.02.md:380). Pin: 32 proof modules, 29 certified and 3 not (spec/Confinement-proof-cert-results-2026.10.04.txt:15); still no refinement (decisions/ADR-0045.md:486 T-0045-28 … | G11 items 56, 74, 75, 105; ADR-0045 T-0045-28 |
| CR-5 | The governance process exempts the most load-bearing records from ever being reviewed: C1-C4 do not reach ADR-0007, 0010 or the Persona series; unmarked genesis records are never re-reviewed | **partly addressed** | 10.02: structurally answered by ADR-0029 A2, evidentially worse (derived/topak-critical-review-2026.10.02.md:381). Pin: every record is to be reviewed at bootstrap (decisions/ADR-0029.md:186); no reviewer is engaged and no pass has run (checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:261-262); no criterion for assisted … | G11 §4 A2.5 line; G11 item 66 |
| CR-6 | The policy layer cannot express flow constraints: a per-action envelope cannot say 'data read from X may not reach sink Y'; syntactic source labels would fix it inside ADR-0007 | **partly addressed** | 10.02: untouched as a record (derived/topak-critical-review-2026.10.02.md:382). Pin: ADR-0047 is in force for Run's ingress, labels as lifted attributes with label forbids in the floor, and says it answers CR-6 'in part' (decisions/ADR-0047.md:19-21); Build's Read is not labelled (decisions/ADR-0047.md:348, :546); the evaluator … | ADR-0047 open obligations; G11 item 93 |
| CR-7 | Ordinary denials are erasable and unordered while grants are non-erasable and ordered; consider an F7 (denied attempts, hash-and-pointer form) or state the choice | **partly addressed** | 10.02: half closed, denials reach the round topic and the `after` companion; still erasable, unordered, no F7 (derived/topak-critical-review-2026.10.02.md:383). Pin: unchanged. Six classes, F1 to F6 (decisions/ADR-0028.md:53-58); 'Denials are not ordered' (decisions/ADR-0015.md:63); a per-principal sequence number 'not taken' … | G11 item 44; derived/topak-residual-risk-statement-2026.10.09.md:239 |
| CR-8 | Rev 5 §7.5 says promotion 'enters `Build(Contain)` enforcement coverage'; ADR-0024's own negative consequence says promotion gains attribution and authorization, not safety | **appears addressed** | 10.02: open, §7.5 still says it (derived/topak-critical-review-2026.10.02.md:384). Pin: §7.5 now reads 'attribution and authorization ... It does not gain safety' (narrative/theory-of-operation.md:1412-1414; logged at :2569-2570). The sentence survives in the record's own Positive consequences (decisions/ADR-0024.md:197-198) | nowhere |
| CR-9 | The 'reversibility index' is cited by the feature list (F5.5) and the boundary register (§7.2) as ADR-0007's; it is not in ADR-0007's text. Dangling concept with no home | **superseded** | 10.02: not re-graded. Pin: the term lives only in frozen derived files (derived/topak-feature-list-2026.09.15.md:119; derived/topak-boundary-register-2026.09.13.md:207), the list superseded as basis (derived/README.md:16); absent from ADR-0007, the glossary and the 10.03 and 11.05 lists (grep); ADR-0032 §4's T_irrev rule stands … | nowhere |
| CR-10 | Seat distinctness covers Thinker, Observer and Reader with two lineages at the archetype: three seats, two lineages. Either three lineages or the Reader's exemption should be declared | **appears addressed** | 10.02: closed by ADR-0037, the Reader is a stage (derived/topak-critical-review-2026.10.02.md:385). Pin: confirmed. ADR-0037 is in force and makes Listener and Reader stages (decisions/ADR-0037.md:12, :14), closing CR-10 by name (:37, :73) | ADR-0037 |
| CR-11 | The forensic floor retains who exercised authority (F1-F5); for human principals that is personal data. ADR-0028 needs a legal-basis line per class | **open** | 10.02: open, no legal-basis line (derived/topak-critical-review-2026.10.02.md:386). Pin: confirmed. The six classes carry no legal-basis line (decisions/ADR-0028.md:47-58); the record's only legal reasoning places the exposure in payloads (decisions/ADR-0028.md:90-91); its open obligations do not list the item … | derived/topak-external-alignment-2026.10.09.md GOVERN 1.1 row (:59) |
| CR-12 | The control plane's TCB is larger than the 'verified object' (rev 5 §3.1) and is enumerated nowhere | **appears addressed** | 10.02: closed by ADR-0045, thirty-one rows (derived/topak-critical-review-2026.10.02.md:387). Pin: ADR-0045 is in force (decisions/ADR-0045.md:14) with rows T-0045-1 to T-0045-37, each with a class and a residual (decisions/ADR-0045.md:465-490; checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:144) | ADR-0045 Annex A and B |
| CR-13 | 'Almost nobody can afford the archetype' (ADR-0017) understates it; the archetype should be described as a proof reference, and rung 1 documented with the same care | **appears addressed** | 10.02: closed in register (derived/topak-critical-review-2026.10.02.md:388). Pin: the archetype is 'a reference point. Nobody ships the archetype' (narrative/glossary.md:1017; narrative/theory-of-operation.md:1692), and the rungs below it are specified (narrative/theory-of-operation.md:318-320; ADR-0034 in force, ADR-0036 … | nowhere |
| CR-14 | The Dantas survey's 'verifier tax': blocking 94% of unsafe actions can leave under 5% safe task completion. The article's capability-cost paragraph should cite the number | **cannot tell** | 10.02: not re-graded. The article is not in the tree (checkpoints/topak-genesis-checkpoint-G1-2026.09.15.md:129 lists it as Project knowledge), so it cannot be read. In the tree, the ToO's capability-cost paragraph cites no number (narrative/theory-of-operation.md:204-205), and no file outside the 09.16 review names the survey … | nowhere |
| CR-15 | ADR-0009's 'must never justify data-plane autonomy in irreversible domains' has no mechanism behind it: nothing in the alphabet types reversibility | **partly addressed** | 10.02: open; T_irrev declared for no effect class (derived/topak-critical-review-2026.10.02.md:389). Pin: the sentence stands with nothing in force behind it (decisions/ADR-0009.md:47); the entry schema in force has five parts and no effect class (decisions/ADR-0049.md:64); T_irrev is still declared for no class … | ToO §13 A10; derived/topak-residual-risk-statement-2026.10.09.md §5; ADR-0066 (Proposed) |
| CR-16 | The Claude Code sandbox documents an 'unsandboxed retry escape hatch', on by default: the shape of break-glass-without-TTL that ADR-0009/0013 forbid; a useful concrete foil for the article | **cannot tell** | 10.02: not re-graded. The article is not in the tree (checkpoints/topak-genesis-checkpoint-G1-2026.09.15.md:129 lists it as Project knowledge), so it cannot be read. In the tree the foil is not used: the one later reading of that sandbox describes its admin-required mode and draws no break-glass contrast … | nowhere |
| CR-17 | MAP 3.4 (operator proficiency) is a declared gap, and D, quarantine release and break-glass all presume a present, trained, authorized human | **open** | 10.02: open (derived/topak-critical-review-2026.10.02.md:390). Pin: confirmed. The ToO still lists MAP 3.4 as a gap: an operator as a principal 'says who acted and nothing about skill' (narrative/theory-of-operation.md:1988-1989); A5 still presumes a trained human (narrative/theory-of-operation.md:2221); no record defines one … | derived/topak-feature-list-2026.11.05.md F5.6 ('no record and no open-list item') … |
| CR-18 | Microsoft's Agent Governance Toolkit README says 'the policy engine and agents share the same process boundary'; ADR-0008's fault-domain independence is a differentiator the article can cite | **cannot tell** | 10.02: not re-graded. The article is not in the tree (checkpoints/topak-genesis-checkpoint-G1-2026.09.15.md:129 lists it as Project knowledge), so it cannot be read. The tree's own comparison carries the point with its source: 'Enforcement remains in-process' (derived/topak-external-and-competitive-assessment-2026.10.05.md:354 … | derived/topak-external-and-competitive-assessment-2026.10.05.md §3.6 |
| CR-19 | AGT's trust scoring can unlock capabilities by tier (mechanics unconfirmed); if confirmed, it is the cleanest foil for 'nothing derived from behavior can raise standing' | **cannot tell** | 10.02: not re-graded. The article is not in the tree (checkpoints/topak-genesis-checkpoint-G1-2026.09.15.md:129 lists it as Project knowledge), so it cannot be read. The mechanics are since confirmed in the tree: the score 'sets privilege rings', so 'a model's judgment can raise privilege' … | derived/topak-external-and-competitive-assessment-2026.10.05.md §3.6 |
| CR-20 | Aegis (Mazzocchetti, Mar 2026) claims 'verifiable policy enforcement' via zero-knowledge proofs; TOPAK's article should distinguish proof-of-enforcement from verified-enforcement-mechanism | **cannot tell** | 10.02: not re-graded. The article is not in the tree (checkpoints/topak-genesis-checkpoint-G1-2026.09.15.md:129 lists it as Project knowledge), so it cannot be read. In the tree Aegis is named only in the frozen 09.17 glossary (derived/topak-glossary-2026.09.17.md:848); neither competitive assessment (10.01, 10.05) names it … | nowhere |
| CR-21 | The recursion, stated as a grade: nothing in this corpus is yet evidence in the sense the external documents require; records ratified by their drafter; zero confirmations have run | **partly addressed** | 10.02: with CR-5, structurally answered, evidentially worse (derived/topak-critical-review-2026.10.02.md:381). Pin: the bootstrap set is now to be reviewed at bootstrap (decisions/ADR-0029.md:164, :186); still no reviewer and no confirmation pass (checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:261-262), with 29 records … | G11 §4 A2.5 line; G11 item 66 |
| CR-22 | `slm/` asserts outcomes with no checked-in evidence: Part B's outputs and the cited session file are gitignored; check in dated results files or strike the claims to 'run, unrecorded' | **appears addressed** | 10.02: closed on 09.25, rerun 09.28 (derived/topak-critical-review-2026.10.02.md:391). Pin: six dated results files are tracked under slm/ (slm/gate-suite-results-2026.09.25.txt; slm/rehearsal-results-2026.09.28.txt) and the README points at them (slm/README.md:181-187). The session file it names as a source is still untracked … | nowhere |
| CR-23 | No results file is reproducible end to end: hand-assembled concatenations with no driver; `spec/RulesFloorNV-run.sh` hardcodes a jar path that no longer resolves | **partly addressed** | 10.02: closed in part; older modules' files still hand-assembled (derived/topak-critical-review-2026.10.02.md:392). Pin: the jar path resolves beside tools/ (spec/RulesFloorNV-run.sh:5); ten gen-results drivers exist under spec/ and the 11.10 results name theirs (spec/Alone-results-2026.11.10.txt:3); the older TLC results still … | G11 item 78 |
| CR-24 | Unsigned trust edges under a signed corpus: bearer-token auth, no replica authentication, unsigned bundles; a swapped bundle tarball whose filename recomputes would be trusted | **partly addressed** | 10.02: half closed; bundles signed; replica auth none; gate evidence unsigned; operator socket a file mode (derived/topak-critical-review-2026.10.02.md:393). Pin: a bundle is trusted by signature, under a dev key (mechanism/GAPS-AND-ASSUMPTIONS.md:92); operator requests are now signed, with an unsigned BOOTSTRAP path left … | G11 items 23, 57, 67; GAPS G5; ADR-0045 T-0045-1, T-0045-13 |
| CR-25 | Register lag, small but persistent: `mechanism/README.md` says 44 tests where the register's evidence row describes the 38-test run; `derived/` predates two checkpoints; state of prose behind state of record | **open** | 10.02: recurs in new places (derived/topak-critical-review-2026.10.02.md:394). Pin: the 09.25 instances were fixed and the class is back, in the same row: the register's evidence stops at '96 tests (pending ADR-0033 A7)' (mechanism/GAPS-AND-ASSUMPTIONS.md:20; also :41) where the README says 155 (mechanism/README.md:39) and A7 … | derived/topak-feature-list-2026.11.05.md §16 (the index and tag instances only); G11 item 100 |
| CR-26 | A post-review commit falsified ADR-0033 E1 by enumeration: `f59941d` changed `mechanism/Cargo.toml`, a third file where E1 says later changes are the register and the pin file 'and no code' | **appears addressed** | 10.02: absorbed; expected-failure counts now verified by tooling (derived/topak-critical-review-2026.10.02.md:395). Pin: E1's sentence is struck and replaced by the A1 addendum (decisions/ADR-0033.md:209-211), whose note names `f59941d` and the licence field (decisions/ADR-0033.md:1128-1130); each manifest's expected count is … | ADR-0033 A1 |
| CR-27 | The first leases above rung 0 are a milestone of attribution, not of confinement, and the corpus should say it in those words; the P3-passing image (G9 item 36) is the smallest work with the largest effect | **partly addressed** | 10.02: new, High. Pin: the register says it: `Mediated` is 'a computed verdict' at rung 1 (narrative/theory-of-operation.md:334-337), 'Every principal a real deployment can launch is `Mediated`' (mechanism/GAPS-AND-ASSUMPTIONS.md:121), and a lying rung-1 launcher is believed (mechanism/GAPS-AND-ASSUMPTIONS.md:320). The image is … | G11 items 34, 36; GAPS G1 |
| CR-28 | The recursion, re-graded at G9: forty accepted, twenty-two confirmation-required, seven assistant-drafted texts; ADR-0046's condition met in letter not purpose; no A2.5 ledger line; no criterion for assisted … | **partly addressed** | 10.02: new, High. Pin: (ii) the A2.5 line is carried and reads None (checkpoints/README.md:54-65; checkpoints/topak-genesis-checkpoint-G10-2026.10.05.md:247; checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:257-262); (iii) still no criterion for assisted drafting … | G11 §4; G11 item 66 |
| CR-29 | Break-glass is both too hard to obtain and too easy to keep: R3 couples the emergency path to a live Observer (G9 item 49), and R8, the break-glass TTL, is pending, so an approval is time-unbounded within an … | **appears addressed** | 10.02: new, Medium-High. Pin: an emergency seat is not coupled (decisions/ADR-0039.md:430 A2); R8 is withdrawn and a grant ends with its round (decisions/ADR-0026.md:342 W1; decisions/ADR-0052.md:18); the reference follows (mechanism/GAPS-AND-ASSUMPTIONS.md:130). ADR-0052 is provisional, and 'break-glass has no settled form' … | G11 items 8, 49, 92 |
| CR-30 | The proof-checker asymmetry: the gate's verdicts are checked by a pinned proof checker, while 3,036 proof obligations are accepted on tlapm's word with no certificate; the prover binary is untracked | **appears addressed** | 10.02: new, Medium. Pin: the prover is pinned in a measured file (tools/TLAPS-PIN:6-11; its full digest still 'owed', :12); every one of the 32 proof modules has a certified run, 29 certified and 3 NOT CERTIFIED (spec/Confinement-proof-cert-results-2026.10.04.txt:15; spec/Confinement_A1-proof-cert-results-2026.10.04.txt:15 … | G11 items 73, 74, 104 |
| CR-31 | The state of record is a revision behind its own narrative, on the day both were cut: G9 says revision 12 stands and four tags do not exist; revision 13 and the tags exist; `README.md` still points at G8 | **appears addressed** | 10.02: new, Low-Medium. Pin: the G9 erratum is recorded (checkpoints/README.md:52) and G10 corrected item 79 (checkpoints/topak-genesis-checkpoint-G10-2026.10.05.md:353); README points at G11 and revision 15 (README.md:20-21). The class continues under CR-25: G11 predates Batches 38 and 39 and ADR-0056 to 0068, and the index … | checkpoints/README.md errata; G11 item 100 |
| CR-32 | Prompt injection inside the envelope has no record, and tool descriptions are unpinned; neither the provenance-label fix nor the interface-text digest has a record, an owner or a G9 item | **appears addressed** | 10.02: new, Medium-High. Pin: both halves have records in force since Batch 34: labels and label forbids, with CR-32's steered destination as F2 (decisions/ADR-0047.md:19-21, :280); the tool's interface in the signed bundle, delivered by the mechanism (decisions/ADR-0048.md:15, :89); one entry schema (decisions/ADR-0049.md:15). … | G11 items 93, 94 |
| CR-33 | Channel fidelity is narrower at the reference than in the pending text (core module, not component; protocol unenforced; channel declared twice; Build P4 unheld); A2 should not be ratified from the drafter's … | **partly addressed** | 10.02: new, Medium. Pin: A2 was ratified by the custodian from the drafter's text, the divergences recorded with it (decisions/ADR-0034.md:512); the channel is now declared once, in the entry (mechanism/GAPS-AND-ASSUMPTIONS.md:103); still a core module with the protocol unbound (mechanism/GAPS-AND-ASSUMPTIONS.md:103 … | G11 items 83, 84; GAPS I44 |
| CR-34 | The operator channel is the untyped half of the control-plane alphabet: operator requests are authenticated by a socket's file mode, replica traffic is unauthenticated, gate evidence is an operator's assertion | **partly addressed** | 10.02: new, Medium-High. Pin: an operator is a principal whose six control actions are signed, lifted and floored (decisions/ADR-0050.md:20, provisional; mechanism/GAPS-AND-ASSUMPTIONS.md:106), but the unsigned socket still seats, as a BOOTSTRAP path (mechanism/GAPS-AND-ASSUMPTIONS.md:106); replica traffic unauthenticated … | G11 items 57, 88; GAPS I47, G5; derived/topak-residual-risk-statement-2026.10.09.md §1.4 |
| CR-35 | The Playbook artifacts and the residual-risk statement are the oldest open documentation debts: the 09.12 inventory and 09.15 feature list 'due for regeneration' since revision 7; MANAGE 1.4 unwritten | **appears addressed** | 10.02: new, Medium. Pin: all three are written: the statement, now against G11 (derived/topak-residual-risk-statement-2026.10.09.md:3-7; derived/README.md:34, :43), the inventory (derived/README.md:35, :42) and the feature list (derived/README.md:37, :46). The ToO has not caught up: still 'due for regeneration' and 'unwritten' … | G11 item 12 |
| CR-36 | Every number is a placeholder and the floor is proved over them: T_obs 5000 ms, K 8, Run's R 64, T_persona one hour; no Observer has been measured (item 47); the slm/ rig could measure T_obs and K today | **open** | 10.02: new, Medium. Pin: confirmed. The values file is still 'PLACEHOLDERS · not ratified · not measured' (floor/genesis-values.json:3-4; T_obs_ms 5000 at :7, K 8 at :9); no measurement is recorded (checkpoints/topak-genesis-checkpoint-G9-2026.10.02.md:281, not restated since … | G11 item 47; derived/topak-residual-risk-statement-2026.10.09.md:208, :367 |
| CR-37 | No liveness property exists anywhere in the formal layer, for a design whose Run posture is 'stall'; one liveness property per coupling module, under weak fairness on the Observer's heartbeat, would be the … | **partly addressed** | 10.02: new, Medium. Pin: four leads-to properties are stated under fairness in an extension (spec/Coupling_live.tla:149-156), checked by TLC and not proved (checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:352; spec/README.md:33); spec/Emergency_live.tla carries two proved ENABLED invariants … | G11 item 105; derived/topak-liveness-2026.10.07.md |
| CR-38 | The forensic record and TACIP's root-cause requirement pull in opposite directions; a deployment under TACIP would need a declared position on 8.2, and ADR-0023's schema has no field for it | **open** | 10.02: new, Low-Medium. Pin: confirmed. ADR-0023 §6 has fields 6a, 6b and 6c and no such field (decisions/ADR-0023.md:47-51); no record states the position (grep 'root-cause' over decisions/ finds decisions/ADR-0020.md:80-83 and decisions/ADR-0019.md:21 only); later documents say it has no home … | derived/topak-feature-list-2026.11.05.md F2.60; derived/topak-residual-risk-statement-2026.10.09.md:242; G11 … |
| CR-39 | Three launcher tests are timing-dependent and fail under load: `contain.rs` sequences a launch, a fence or revocation and an assertion with a 500 ms sleep and a `settle` helper, not by waiting on the log index | **partly addressed** | 10.02: new, Low. Pin: the helpers now poll for a named state and treat the ceiling as a failure, citing CR-39 (mechanism/crates/topak-node/tests/contain.rs:343-354, :356-366); `settle` is gone and the three named tests carry no fixed sleep (:653, :671, :792). One fixed 500 ms sleep before a negative assertion remains in another … | nowhere |

**Three things the re-grade shows.**

- **CR-25, register lag, is open in the row it was first found in.** `mechanism/GAPS-AND-ASSUMPTIONS.md` stops at
  96 tests where `mechanism/README.md` says 155. The 09.25 review called it small and persistent; it is both.
- **CR-8's sentence was fixed in the narrative and not in the record.** The consequence the 09.16 review objected
  to is ADR-0024's own text and still stands there, in force; Batch 38's erratum corrected the bullet beside it.
- **CR-39's fix left one fixed sleep before a negative assertion** (`contain.rs:1009`), which is CR-39's class.
  The three tests passed here on a loaded machine.

**The 10.02 review's seven asks.**

| Ask of the 10.02 review, §8 | At the pin | What was checked |
|---|---|---|
| 1. Engage one reviewer who is not the author, record it on the A2.5 ledger line, and run one confirmation pass over any confirmation-required record | **open** | 10.02: first on the list, as on 09.25. Pin: confirmed. Reviewer engaged 'None', last review pass 'None' (checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:261-262; checkpoints/README.md:64-65); the two batches after G11 were again read by nobody but the drafter (decisions/ADR-0024.md:329 … |
| 2. Build the P3-passing image (item 36) and run ADR-0036's ratification run on it | **open** | 10.02: second on the list. Pin: confirmed. The only profile in the tree fails P3 and names the scratch image as the missing subtraction (slm/serve/profile-host-rung0.json:29, :38); the image builds on a Python base (slm/serve/Dockerfile:7, :20); the run is unrun and ADR-0036 Proposed … |
| 3. Write the residual-risk statement (CR-35) from the text that already exists | **appears addressed** | 10.02: third on the list. Pin: written twice, the current one against G11 (derived/topak-residual-risk-statement-2026.10.09.md:3-7; derived/README.md:34, :43). The ToO still calls it unwritten (narrative/theory-of-operation.md:1897) |
| 4. Write the provenance-label and tool-description record (CR-32) in ADR-0007's own terms | **appears addressed** | 10.02: fourth on the list. Pin: ADR-0047 (labels) and ADR-0048 (the tool interface) are in force since Batch 34 (decisions/ADR-0047.md:19; decisions/ADR-0048.md:15), with the entry's schema in ADR-0049 (decisions/ADR-0049.md:15); all three confirmation-required |
| 5. Decide break-glass against R3 and ratify R8 (CR-29) | **appears addressed** | 10.02: fifth on the list. Pin: decided: an emergency seat is not coupled (decisions/ADR-0039.md:430). R8 was withdrawn, not ratified; a grant is bounded by its round instead (decisions/ADR-0026.md:342; decisions/ADR-0052.md:18, provisional); the reference follows … |
| 6. Add one liveness property to `Coupling.tla` under weak fairness on the heartbeat (CR-37), and run the Isabelle backend once over the fifteen proofs or pin the prover in a manifest (CR-30) | **appears addressed** | 10.02: sixth on the list. Pin: four leads-to properties in an extension, TLC-checked and not proved (spec/Coupling_live.tla:149-156; checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md:352); weak fairness on the heartbeat was found not to be enough (spec/Coupling_live.tla:46); the prover is … |
| 7. Measure `T_obs` and `K` with the rehearsal rig (CR-36), and write the A2.5 line, the README repoint and the G9 erratum (CR-31) | **partly addressed** | 10.02: seventh on the list. Pin: the three writing tasks are done (checkpoints/README.md:54-65 the A2.5 line, :52 the G9 erratum; README.md:20-21); the measurement is not: the values are still 'not measured' (floor/genesis-values.json:3; checkpoints/topak-genesis-checkpoint-G9-2026.10.02.md:281) |

---

## 4. New findings

493 findings were reported and 485 stand (High 1 · Medium-High 11 · Medium 96 · Low-Medium 191 · Low 186). The
register's Part III lists every one, and the annex has each in full with its verifier's verdict. This section
gathers them into 22 findings at the size a disposition is made at, CR-40 to CR-61. A CR's severity is the review's own
judgment of the whole, and is never above the highest severity a verifier left on a finding it rests on. The two
exceptions are CR-60 and CR-61, which rest on the register's counts and on CR-28 and not on readers' findings.
"Rests on" names the readers' findings; 312 of the 485 are named by a CR, and the other 173
(Low-Medium 73 · Low 100) are in the register only: single stale sentences, miscounts and
pointers, each with its own fix.

| # | Finding | Severity | Against | Rests on |
|---|---|---|---|---|
| CR-40 | **The overlay claims a status, and a suspension of C3, that the process does not define** | High | Proposed; the process in force | I2-1, H-2, B-21, B-22, I2-21, I2-36, I2-29, I2-11, I2-16 |
| CR-41 | **The state of record is behind ratified text, and 190 files are measured by nothing** | Medium | in force; living documents; evidence | B-6, K1-2, K1-1, K2-2, K2-3, K2-4, K1-3, K1-4, K1-5, E-4, L-4, L-5, K1-26 |
| CR-42 | **Text in force rests on ADR-0035, which has been Proposed since 2026.09.25** | Medium-High | in force | B-1, C-43, A-6, F-25, B-9, B-18, A-8 |
| CR-43 | **Seventeen ratification rows say "The reference follows the text", and for several it does not** | Medium-High | in force; evidence | B-2, A-5, J-2, J-4, J-7, C-1 |
| CR-44 | **Confirmation markings are not carried to status lines, so the count of twenty-nine understates the set** | Medium | in force; living documents | K1-6, A-2, A-3, C-14, B-3, D-3, K2-5, K1-11, B-19, F-32, G-26, H-22, C-24, D-4, K1-14, K2-7, B-5, K1-12 |
| CR-45 | **Break-glass was retired as a floor exception in Batch 34, and five places still describe it as one** | Medium-High | in force; evidence | A-1, D-1, B-15, F-26, F-27, F-11, F-15, J-2, B-11, B-12, F-29 |
| CR-46 | **The emergency seat's one-round rule is held by the reference and a module, and not by the floor** | Medium | in force; evidence | F-1, F-2, F-8, F-10, F-46, F-38, F-16, F-17 |
| CR-47 | **What is in force cannot be read off the page in the places a reader would look first** | Medium | in force; living documents; evidence | F-6, D-2, F-5, F-13, F-14, G-23, C-2, K2-27, F-31, K2-23, K2-24, I1-15, B-20, K2-21, J-8, B-25, F-33, G-30, J-9, J-10, J-12, F-30, F-12, B-12, G-24, E-8, C-33, K2-29, G-33 |
| CR-48 | **The overlay's records claim more than their modules state** | Medium-High | Proposed; evidence | I2-2, I2-3, I1-1, I2-6, I1-2, I1-3, I2-7, I1-4, I1-5, I2-12, I1-6, I2-20, I1-7, I2-8, I1-9, I1-10, I2-28, I1-11, I2-25, I1-12, I1-13, I1-20, I1-21, I2-23, I2-24, I1-17, I1-18, L-6, I1-19, L-3, I2-31 |
| CR-49 | **The overlay reverses accepted text it does not name** | Medium | Proposed against text in force | I2-9, I2-5, I2-4, I2-10, I2-13, I2-14, I2-15, I2-17, I2-18, I2-19, I2-22, I2-26, I2-27, I2-30, I2-32, I2-33, I2-37, I2-41, I2-42, L-7, K1-7 |
| CR-50 | **For workflows, the record, the module and the reference disagree three ways, and the reference is running** | Medium | Proposed; evidence | G-1, G-2, G-3, G-4, G-5, G-7, G-8, G-9, G-10, G-12, G-13, G-14, G-15, G-27, G-28, G-32, G-11 |
| CR-51 | **ADR-0056 contradicts itself on whether a subject assertion is on the record, and has nothing behind it** | Medium-High | Proposed | G-6, G-18, G-19, G-20, G-21 |
| CR-52 | **The specification graph is behind the tree it describes, and does not hold what its record says it holds** | Medium-High | Proposed; evidence | H-1, H-3, H-4, H-5, H-6, H-7, H-8, H-9, H-10, H-12, H-13, H-16, H-17, H-18, H-19, H-20, H-24, H-25, L-9 |
| CR-53 | **Six properties hold by how their module is built, and say less than their records read as saying** | Medium | in force; Proposed; evidence | F-2, D-6, B-7, G-8, I1-19, L-6, C-35, B-10, B-14, B-27, F-18, F-19, F-20, F-46, A-14, C-5 |
| CR-54 | **The trusted base's own table contradicts itself, and the binding has no row for half the modules** | Medium | in force; evidence | E-1, E-2, E-3, E-5, E-6, E-7, E-9, K1-24, F-3, I1-2 |
| CR-55 | **The reference at this tree is measured by no manifest, and one of its traces no longer replays** | Medium | evidence | J-1, L-8, J-3, J-5, J-11, J-13, G-10, J-6 |
| CR-56 | **Accepted records contradict each other where one was amended and its neighbours were not** | Medium | in force | A-4, A-7, A-9, A-10, A-11, C-17, C-18, C-25, C-34, D-5, F-7, F-9, F-21, F-22, F-23, F-24, F-34, B-4, B-8, B-13, B-16, B-17, K1-8, K1-15, K1-16, K1-17, K1-18, J-14, A-13, C-50, F-41, F-45, F-47, F-43, F-44, F-4 |
| CR-57 | **Four of the corpus's checkers pass, or stay silent, on a failure** | Low-Medium | evidence | L-1, L-2, L-8, L-11, L-3, H-5, H-19, F-37 |
| CR-58 | **Both guides say they are kept current, and neither knows of anything after G11** | Medium | living documents | K2-1, K1-25, I2-39, H-23, K2-31, K2-15, K2-8, K2-9, K1-10, K1-20, K1-13, K1-19, G-22, G-31, K1-9, K1-21, K1-22, K1-23, I2-40, A-12 |
| CR-59 | **Ratification conditions and Open obligations carry no state, or a stale one** | Low-Medium | in force; Proposed | G-16, F-35, I1-24, F-36, H-26, G-19, G-13, B-34, I1-25, I1-27, I1-28, I1-23, I2-35, I2-34, I1-14, I1-22, I1-26, F-28, F-39, F-40, G-25, F-48, G-17, G-29, B-23, B-24, B-26, B-28, B-29, B-30, B-31, B-32, B-33, B-35, J-15 |
| CR-60 | **252 earlier findings are open, and 108 of them are carried by no list** | Medium | process |  |
| CR-61 | **The recursion, re-graded: the corpus can now be extended faster than it can be kept true** | High | process | K1-7 |

**CR-40. The overlay claims a status, and a suspension of C3, that the process does not define** (High; Proposed; the process in force). All ten records of the command-chain overlay give their status as "Proposed" and their position as "an overlay, not
the archetype", and all ten say they carry a debt against nothing "while this is an overlay". Eight of the ten
status notes add that "C3 does not apply while this is an overlay" (ADR-0063 and ADR-0064 give other reasons). The
position is the custodian's answer ⟨Q11⟩, "overlay first, reported upstream", and the records hang it on ADR-0023
§4 and on ADR-0058's Add operation and its §6. Neither supports it. ADR-0023 §4, in
force, says that a variation holding a capability the archetype lacks is not a demotion: the archetype "is
incomplete and must be extended before the variation is admitted". ADR-0058 is Proposed, defines an overlay as a
deployment's declaration over the archetype's graph, and heads its §5 "the admission test is unchanged". ADR-0029
§3 has four status classes and §4 four criteria, with no class for a record in `decisions/` that is not the
archetype's and no suspension of a criterion. ADR-0066 goes further and calls itself "provisional while ADR-0052
is", a word ADR-0029 defines only for a ratified record. Three readers, working apart from three directions, came
to this. It is graded High because every one of the ten records' ratification paths runs through it, and because
the records reverse accepted text in at least nine places (§5.3) that would each need C3 on their face if the
sentence does not hold. It is a finding about process and not about the design: nothing here says the overlay is
wrong.

**CR-41. The state of record is behind ratified text, and 190 files are measured by nothing** (Medium; in force; living documents; evidence). Batches 38 and 39 were ratified on 2026.11.02 and 2026.11.03, one of them on a bootstrap-set record. They stand
in History rows and in three passing mentions; no checkpoint, no row of the decisions index and no sentence of the
narrative or the glossary records them, and the glossary's count of batches stops at thirty-seven. Because a
checkpoint outranks a record where they disagree, the frozen G11 item 104 ("unreported upstream") formally
outranks the ratified amendment that says the defects were reported on 2026.10.18; the narrative says the stale
thing twice, the glossary twice and ADR-0046 §3 once. The same lag gives five Proposed records where there are
eighteen, twelve pending amendments where there are fifteen, and twenty-four proof modules where `spec/` holds
thirty-two. 190 tracked files, every overlay record, module, proof and results file among them, are measured by no
manifest. Two tags the living documents name, `ToO-rev15` and `glossary-2026.10.09`, are not on the origin. This is
CR-31 again, larger: on 10.02 the state of record was one revision behind its narrative; today it is two batches
and thirteen records behind its tree.

**CR-42. Text in force rests on ADR-0035, which has been Proposed since 2026.09.25** (Medium-High; in force). ADR-0024 A2.2 is in force inside the bootstrap set's promotion rule, and it reads an independence table that only
ADR-0035 defines. A2's own preamble made that half conditional on ADR-0035; the ratification row took the whole
amendment. The reference's register and ADR-0024's History say A2.2 is not followed "since no independence table
exists", so a clause in force is, by the corpus's own account, enforced nowhere, and the corpus says so. ADR-0035 in turn still describes
its tally rule as a debt for an ADR-0024 amendment "still to come". The same dependence runs through ADR-0016 and
ADR-0022 (three clauses), ADR-0047 §3, ADR-0048 §2 and ADR-0050 §6, which are stated over sets and a rule that only
the Proposed record defines, and two of them do not say so. A related loop: the tally that would confirm ADR-0038
and ADR-0039 after bootstrap is defined by ADR-0038 and ADR-0039, which is the circularity ADR-0029 §4 was written
to exclude; that one is an inference from texts in force and not a contradiction between two sentences. The fix is
a decision and not an edit: ratify ADR-0035, or take the clauses that need it out of force until it is.

**CR-43. Seventeen ratification rows say "The reference follows the text", and for several it does not** (Medium-High; in force; evidence). The sentence is in the Batch 34 row of seventeen records. For several of the texts those rows ratify, the
reference's own register says otherwise: a first lease from a quorum is not built (ADR-0050 §10 says so itself),
no Persona record exists for a person, an emergency seating is not prepared by promotion, and the allowlist digest
is not the record's. In the code, `rules.rs` still checks R7 over the retired break-glass envelope's actions, on
every issuance, as it read before ADR-0026 A2, which is in force and pinned, and keeps two as R6's constant bound
where the count it bounds is now one; the register does not record the divergence. ADR-0033 §1, in force, still
says every lease is rung 0 and every principal `Mediated`, against its own addenda. A ratification row is where the corpus says what was seen when a text
took force. These say something was seen that the register, the code and the record's own later sections say was
not.

**CR-44. Confirmation markings are not carried to status lines, so the count of twenty-nine understates the set** (Medium; in force; living documents). ADR-0029 §7 has every checkpoint carry the confirmation-required count, and G11 counts twenty-nine by reading
status lines. At least four records carry a C3 on a ratified amendment's own History row that never reached the
status line: ADR-0009 and ADR-0013 (their A1), ADR-0022 (A2) and ADR-0031 (A3). ADR-0041, ADR-0042 and ADR-0043 still
say flatly that C3 does not apply, beside amendments applied at Batch 34 whose parent records carry C3 for the
same reversals. ADR-0029's own marking is stated
three ways. ADR-0032 says none of C1 to C4 applies while its header says it discharges an accepted record's open
obligation, which is C4 as ADR-0029 defines it; its own note says the consequence, that it "will never be reviewed
by the first quorum". The decisions index then drops the marking for eight more records, six of them accepted, and
heads the column "Status at G8". The set the first quorum is to review is the one list in the corpus whose
completeness the genesis process rests on, and it is assembled by hand from a field that is not kept.

**CR-45. Break-glass was retired as a floor exception in Batch 34, and five places still describe it as one** (Medium-High; in force; evidence). ADR-0052 made break-glass an emergency seating and retired floor exception X1, with eight dependent amendments.
The retirement stopped short in five places. **ADR-0015**, whose C2 marking is for its exhaustive classification of
effects, still classifies break-glass as "an admit decision against its declared floor-exception entry"; it received
no amendment, and the narrative states a classification the record does not contain. **ADR-0043 §2** still says
"Only a `thinker` seat holds `Actuate`" over a table of three seat kinds, where ADR-0037 §4, ADR-0041 and the floor
in force give an `emergency` seat `Actuate`; the invariant `OnlyThinkersActuate`, proved in `RunSeats` and marked
"holds" against that clause in the binding table, is a true theorem of its module and no longer a statement of the
design in force. **ADR-0029 §5**, the bootstrap trigger, still names the module `BreakGlass` and the invariant
`BreakGlassNeverChangesAuthority`; the mechanism in force is modelled by `BreakGlass_A1` under another name.
**`RulesFloorBase.tla`** still carries `bgScope` and R6's bound of two (G11 item 90). **The reference's `rules.rs`**
implements both as they were (CR-43). The floor in force also carries comments that say R3 "applies to break-glass
too", which ADR-0052 decides the other way.

**CR-46. The emergency seat's one-round rule is held by the reference and a module, and not by the floor** (Medium; in force; evidence). ADR-0052 §3 says an operator's `Regrant` or `Renew` naming an emergency seat is refused, and ADR-0050 says "the
floor states the envelope". The floor does not state this. Run against the `emergency` stage, which G11 names as
the floor in force, an operator's `Renew` and `Regrant` of a seat of kind `emergency` in its own domain are each
decided **allow**, by `C2-renew` and `C1-regrant-successor` (annex, `runs/16-emergency-seat-probe.txt`); no entry
reads the target's kind, no gate candidate covers it and none of the stage's 107 cases tries it. The refusal is real
at the reference, as an apply-time check with a test, and in `Emergency.tla` as two mutations. So the property holds
where the reference is the mechanism and is in neither of the two things the corpus calls the verified object's
policy. Beside it: `NoAgentHoldsAnEmergencySeat` is proved, and holds because the model's activation guard reads the
person-or-agent fact that the record says the mechanism cannot see; the module declares no premise for that, where
`Operators.tla` declares its equivalent. ADR-0048's "the tool list is the allowlist of the one granted revision"
does not describe an emergency round, whose list ADR-0052 computes across revisions.

**CR-47. What is in force cannot be read off the page in the places a reader would look first** (Medium; in force; living documents; evidence). ADR-0041 §1, the record every later record cites for the floor's entries, still marks X1's retirement and the
label and control entries "pending, not applied" in its tables; its own header says all three were ratified and
applied in Batch 34. `floor/proposed/README.md` opens "DRAFT · not ratified" and describes "the floor as it would
read if" records were in force that have been since 2026.10.05; one of its stages is the floor in force. The two
floor READMEs give three answers between them to which stage the reference links. `spec/README.md` calls four
accepted records Proposed and two ratified amendments pending, and says "none yet" of modules that eight records
cite by digest. `manifests/index.tsv` calls four ratified ADR-0033 addenda pending. History tables keep "Pending" in
the State column of ratified rows. The reference's register, whose header says it was brought current, has rows
that contradict each other on what is built. None of these changes what is in force. Each is where a reader, or
the reviewer ADR-0029 A2 asks for, would go to find out.

**CR-48. The overlay's records claim more than their modules state** (Medium-High; Proposed; evidence). The eight modules are checked, proved and reproduce (§1). The records around them were revised twice in the day
and still say more than the modules do. **Budget.** ADR-0059 gives a charter's `budget` as "the most leases the
plane and every plane below it may ever issue"; an intent's budget is bounded by the seating's figure and starts
afresh with each intent, on one operator's signature, and `Intent.tla` resets `spent` to zero, so n intents issue
up to n times the figure. Under capture, nothing in `Federation.tla` bounds what is allocated across the tree.
**Effects.** ADR-0063's headline, "fewer than `K_up` further effects" after a revocation, is proved of charged
entries; the same records class sends, beacons, hold, terminal behaviour and a delivered release act as effects,
and none is charged. Under a captured plane §5 states the unread tail as fewer than `K_up` in total where the
module, and §4, bound it per honest governor. **Time.** ADR-0064's "that bounds effects too" has no model: the
module does not model a lease's `ttl`, and as §5 defines "overdue", a tick is overdue at the instant it first
becomes signable, so at least a certificate's worth of vehicles find it overdue before it can be ordered; the
module satisfies this only because agreement takes no time in it, and no record defines a grace. **The proofs' own
header.** The "Assumptions:" line of three proof-results files omits `ASSUME`s the proofs use; `Membership`'s says
"none", and `PlaneClock`'s omits the premise about time, because the script reads the proof module and not its
base. **ADR-0068** was never revised: it still says "no module is written". The `federation` floor stage's entries
lag the first revision in three places, and one conjunct of `Outstanding`'s `Safe` has a proof and no mutation.
None of this was caught by a checker, because no checker binds an overlay record to its module (CR-57).

**CR-49. The overlay reverses accepted text it does not name** (Medium; Proposed against text in force). ADR-0059's provenance note says eight accepted records "were not re-read for this draft and are taken as ToO and
the proposal give them". It shows. Requiring Byzantine agreement changes the replica fault model, which ADR-0033 §3 sets
and defers; the owed lists name ADR-0045 and not ADR-0033. A cell's Observer "on the same vehicle" contradicts the accepted
placement rule, which no overlay record cites, and the correlator is never mentioned. ADR-0062 §8 quotes
`R3-observer-live` short. The stack's containment becomes an assumption of use where accepted text requires an
appraisal at every grant. Promotions and operators at a commanded plane below the root have no source for their
seats: the charter has no field for them and accepted text reserves both to the anchor. "Every field is the
parent's or narrower" has nothing to compare for the fields only an autonomous plane carries, and the chain is
verified "from the anchor's key down" with no stated link from that key to the root plane's replicas. The
overlay's degeneracies are not in ADR-0023 §6's schema and its trusted-base rows are not in ADR-0045's. ADR-0060 §5
leaves a three-way choice open inside its Decision while ADR-0062 §3 and `FD15` are already drafted for one
answer. Each of these is a place where §5.3's table would grow.

**CR-50. For workflows, the record, the module and the reference disagree three ways, and the reference is running** (Medium; Proposed; evidence). ADR-0054 and ADR-0055 are Proposed, built, and followed by the reference on a floor stage not in force (G11 item
102). Read against each other, the three artifacts differ on what matters. What a lapsed worker lease does: a value
a guard reads in the record, a failed node in `Workflow.tla`, an ended round with attributes in `workflow.rs`.
What closes an edge on a finding: "any ancestor" in the record, the activation's causal history in the code, which
at an `any` join omits the branch that did not trigger; no graph in either module can tell the two apart. Whether
a refused grant fails a node or waits: the record says fails, the reference and ADR-0055 say waits. The routing
rule is stated over what a guard reads and applied to the source's label. `covered` changes after a round ends and
towards enabled, against §4's "only `found`". Half of `FindingPrecedesNoRoute` is vacuous in the one graph checked.
Four of ADR-0055's six ratification conditions carry no state, and the one G11 says is unmet is not marked so.
Neither module is proved (G11 item 101). The properties were checked of one thing and the reference runs another.

**CR-51. ADR-0056 contradicts itself on whether a subject assertion is on the record, and has nothing behind it** (Medium-High; Proposed). ADR-0056 §5 says of the provider-signed assertion that names a user: "They are not in the round payload a Thinker
reads, and they are not in any record's payload." §7, two sections on: "The assertion's bytes are in the round's
payload, inside the unit of erasure." Which holds decides whether evidence naming a person is erasable with the
round or is kept off the record altogether, which is the privacy question the record exists to answer. Around it:
the record bounds a subject's authority by the lease's `ttl` and says nothing is refreshed in a round, where a
round is renewable past its `ttl` at a new fence the assertion does not name; its degeneracy table and trusted-base
rows are not in the schemas ADR-0023 and ADR-0045 fix; it refers to an amendment and an "activation" ADR-0054 does
not have; and none of its six ratification conditions has a state, because no module, floor entry, reference path
or dependent entry exists. Its Open obligations list none of that.

**CR-52. The specification graph is behind the tree it describes, and does not hold what its record says it holds** (Medium-High; Proposed; evidence). ADR-0057 §14 is marked Met on a graph that reproduces "byte for byte on a rerun". At this tree the checker exits
1: sixteen `.tla` files are not nodes, and its own comparison with the sync scripts disagrees. Two of its four
*generated* edges pin files that are git-ignored, so the committed result cannot be reproduced from a checkout at
all. The grades it computes are not the grades ADR-0058 §9 states: by §4 and §5 any chain of edges from code to a
theorem's node is a route, the graph holds fresh tested and replayed edges of that shape and counts none, and every
theorem grades *trusted*. A *tested* edge is "fresh" with no evidence a test ran, and does not go stale when the
code under test changes. The type *proved* is given to relations whose own evidence calls them a test. The
exhaustiveness claim that earns the record its C2 is not what the graph holds: no Rego policy is a node and five of
ten layers are empty. "Six controls move what they should" has no artifact and describes five. ADR-0058 was not
revised after ADR-0057's first revision and still says the checker does not exist. The instrument the overlay's
position leans on (CR-40) is itself a draft that its own check fails.

**CR-53. Six properties hold by how their module is built, and say less than their records read as saying** (Medium; in force; Proposed; evidence). Each is a true result about its module. **`NoSilentDowngrade`** is checked and proved with one declared rung per
deployment; ADR-0023 §6c, in force and ratified in the same batch, makes the rung per seat "and not per deployment",
so for the mixed-rung deployment the reference runs the property is checked on the reference's recorded traces
(`ConfinementRefinement.tla`) and is neither model-checked nor proved. **`FindingHasEvidence`** and
**`HonestNeverCharged`** hold in `Correlator.tla` because no correlator in the model can report a finding whose
condition is false, where ADR-0051 §3 says the mechanism does not check findings. **`NoAgentHoldsAnEmergencySeat`**
holds by a guard that reads ghost truth (CR-46). **R6** has been in the genesis rules floor since 2026.09.23 and no
non-vacuity run covers it. **`FindingPrecedesNoRoute`** is vacuous in its ancestor half. **`CountExact`** has no
mutation. Beside these, three modules abstract more than their record's list of abstractions admits (`Labels`,
`ToolList`, `Operators`), the Lean theorems for the floor gates state less than the row that reports them, and the
narrative says erasure's quorum predicate is "checked in TLA+" where no module states one. The corpus's method
(ADR-0046) exists to exclude checks that cannot fail. These got through because the method asks that each mutation
break its property and does not ask that each property have a mutation, nor that each abstraction be listed.

**CR-54. The trusted base's own table contradicts itself, and the binding has no row for half the modules** (Medium; in force; evidence). ADR-0045 is the record the residual-risk statement and every deployment's inventory are computed from. Its §9 is
marked met for "every row but T-0045-7, 21 and 26"; in the binding table five rows in force, T-0045-32 to 36, are
premises of no theorem row, and T-0045-21 is in fact cited. Annex B keeps T-0045-24 "excluded until the tool host
reads the entry" and says elsewhere that it does; its T-0045-6 note says ADR-0044 is not implemented where its own
T-0045-27 says it was built on 2026.10.01. T-0045-37's identity is said to be "printed in every Lean results file",
each with a replay; five of the sixteen files print neither. ADR-0053 §4 cites the code its results are stated
from by digests the tree no longer has. "One row per checked property" holds for fifteen of the thirty-two proof
modules: twenty-one of the thirty-nine modules in `spec/` have no theorem row at all, so the inventory says nothing
of labels, tools, operators, the emergency seating, liveness, workflows or the overlay. G11 item 90 lists ten of
those; it omits `Correlator`, and now the overlay's eight.

**CR-55. The reference at this tree is measured by no manifest, and one of its traces no longer replays** (Medium; evidence). `SHA256SUMS-REF-2026.10.09` fails four files at this tree. Two are expected, the pin file and the register. The
other two, `Cargo.lock` and `topak-contain/Cargo.toml`, moved after the manifest was cut (a dependency update, by
the commit history of 2026.11.03) and no manifest, addendum or checkpoint records it, so the 155 tests that pass
here pass on a dependency set no record names. `spec/mechanism-trace-results.sh`, rerun here, gives 82 of 83
traces matching: the end-to-end workflow test does not replay through `Mechanism.tla`, which G11 item 56 predicted
and nobody had run. The eighteen tests of `tests/workflow.rs` are not traced at all, and the register's "checked,
not asserted, on every path a test takes" has not been true since 2026.10.08. `scripts/smoke.py`, the README's live
run, reads a key the grant reply no longer has (read, not run; the format inventory reported it on 10.03 and no
list carries it). ADR-0033 §5 and its Open obligations still say bundle signing is owed; the code implements it.
The 10.02 review gave "the repo as evidence that the architecture works" a C+ partly on stage one of the
refinement chain. Stage one is now behind the code by one trace, with a number on it.

**CR-56. Accepted records contradict each other where one was amended and its neighbours were not** (Medium; in force). The largest group, and the least dramatic. ADR-0016 §7 says Persona revocation is "Local, no consensus"; ADR-0031
§5 struck those words. ADR-0031 names `T_persona` the mandatory re-attestation interval on the local clock,
ADR-0034 says no re-attestation interval exists, and ADR-0032 puts such intervals on trusted time, whose row has
no surviving instance. ADR-0034 §3.7 lets only a verifier-signed verdict order a Contested revocation "at rung ≥
2", where rung 2 has no verifier, and ADR-0031 §5 calls both revocation tools an operator's. ADR-0022's header calls §6's
confinement obligation "undelivered" where two of its own History rows and ADR-0034 call it discharged, and says its
discharge is necessary for `Contained` over clauses ADR-0034 §4 does not use. ADR-0029 A2 is "Applied" and none of the
four clauses it changes shows the change; §6 still states the rule A2.4 struck. ADR-0024's enabling clause does not
carry the two conjuncts A2 says it has. ADR-0051 makes two correlators the archetype with no change named to
ADR-0038. The checkpoint states wider exits from provisional for ADR-0050 and ADR-0052 than the two records do. ADR-0047 gives three mappings of its load checks to ADR-0049's, and counts three kinds of ingress where
records ratified with it make four. Each is small. Together they are what a record series looks like when
amendments are applied inline to the record amended and not to the records that quote it.

**CR-57. Four of the corpus's checkers pass, or stay silent, on a failure** (Low-Medium; evidence). Found by planting defects in a throwaway clone (annex, `runs/09-checker-mutations.txt`). `tools/verify-manifest.sh
--all` prints `EXPECTED n` when a manifest fails and exits 0. `spec/mechanism-trace-run.sh` prints an ERROR row and
exits 0. `tools/check-refs.py` checks no path under `skills/` or `diagrams/`, and prints a count that includes
duplicates above a list that does not. Nothing reports a changed clause of an overlay record, and an edited TLC
results file changes the status of no script: the overlay's evidence is bound to its records only by digest
citations that one diagram's generator recomputes. Two ratification conditions cite "cases passing" from gate
results files that record no case run. The 10.02 review said the machinery for catching drift had grown faster
than the design it checks. It has, and four pieces of it report success by default.

**CR-58. Both guides say they are kept current, and neither knows of anything after G11** (Medium; living documents). `REVIEWERS_GUIDE_README.md` and `ADOPTERS_GUIDE_README.md` are excluded from every manifest as "conveniences at the
root that are kept current". Neither names ADR-0056 to ADR-0068, Batches 38 and 39, the specification graph, grades
or overlays; the adopter's guide counts fifty-four records where the tree has sixty-seven, says floor fitness has
no owner where it has had one since Batch 34, and marks an amendment pending that was ratified on 2026.10.04. The
glossary gives sixteen monotonicity layers in one section and retires
"sixteen" for eighteen in another, and sixteen policies for a floor that has seventeen. Three living documents say
the diagram family draws no workflow. The narrative presents the label forbids as a bound on what an injection can
reach without the confinement condition every principal fails today, and asks in assumption A1 for a profile
"attested, not asserted" at a rung whose evidence is an assertion. The reviewer's guide is the first thing the A2
reader would open, and it tells that reader that two records are Proposed.

**CR-59. Ratification conditions and Open obligations carry no state, or a stale one** (Low-Medium; in force; Proposed). Across the overlay, the floor item of six ratification conditions and three other items say neither "Met" nor
"Not met", though the text elsewhere says they are not met; ADR-0056's six say nothing; four of ADR-0055's six say
nothing. In the other direction, the Open obligations of ADR-0047, ADR-0048, ADR-0050, ADR-0052, ADR-0054 and
ADR-0055 still list what their own ratification conditions mark met and what the narrative has since done; the
register counts twenty-eight such bullets across the corpus. The rest of this group is single miscounts, pointers
and labels in the same sections: a count of three adversaries where the table has two, "ten or more" replicas where
the record's own rule gives eight, a History row that counts eight attributes where the text has seven. A reader
deciding whether a record is ripe to ratify reads exactly these sections.

**CR-60. 252 earlier findings are open, and 108 of them are carried by no list** (Medium; process). The register's Part I. The corpus's dated self-assessments hold 460 findings, gaps, exposures, stale sentences,
suggested entries and obligations; at this tree 252 are open, 101 partly addressed, 80 appear addressed, and 108
of the open ones appear in neither G11's open list, a record's obligations nor the reference's register. Every one
of the 11.05 feature list's twenty-two stale sentences is still there. None of the eighteen diagram findings of
2026.11.10 was taken up, including by the second revision of the same records later that day. None of the format
inventory's reference-code findings is fixed. Seventeen suggested entries from four notes are untouched. The
pattern is not neglect of any one item. It is that a derived document is frozen when written, ends "suggested
entries, none made", and has no path by which its findings enter the open list unless the custodian carries them
by hand.

**CR-61. The recursion, re-graded: the corpus can now be extended faster than it can be kept true** (High; process). CR-5, CR-21 and CR-28 said that everything here was drafted, built, proved and ratified by the same two hands and
read by nobody else. That stands, unchanged, and G11 says so on its face. What is new since 10.02 is the rate.
Between 2026.11.06 and 2026.11.10 thirteen records were drafted. Ten of them, with eight TLA+ modules, 321 TLC
rows, 5,600 proof obligations, a certification run and nine diagrams, were drafted, revised twice and committed in
one day, from a proposal written that morning, by a drafter who records that eight of the accepted records the set
rests on "were not re-read for this draft". The modules of that day are sound as far as this review could run
them. The records around them are where CR-40, CR-48 and CR-49 are, and the rest of the corpus, its indexes,
guides, graph, narrative and state of record, was left where it stood. This review is the same recursion one
level up: thirteen readers of the drafter's lineage found 485 defects the drafter had read past, which
measures how much one lineage can find in its own work, and says nothing of what it cannot. It is graded High for
the reason CR-28 was: it is the one finding no amount of further drafting answers.

---

## 5. The Proposed set as a whole

The brief is the corpus as it stands proposed, so this section reads the eighteen Proposed records together: what
ratifying them would take, in what order, and what it would reverse.

**5.1 What is proposed, and what stands behind each.**

| Record | Drafted | Module, checked by TLC | Proved by TLAPS | Floor | Reference | A reader not the drafter |
|---|---|---|---|---|---|---|
| ADR-0022 §6 | 09.23 | none | | | its obligation is ADR-0034's and ADR-0036's to discharge | none |
| ADR-0035 | 09.25, at R8 | none; a gate suite over synthetic records in `slm/` | | its θ values are unset | a rehearsal | none |
| ADR-0036 | 09.28 | none of its own | | | the rung-1 launcher is in the node | none |
| ADR-0051 | 10.04 | `Correlator` | 455 obligations, certified | | not built | none |
| ADR-0054 | 10.07 | `Workflow`, 33 rows | **not proved** | the `workflow` stage: written, gated, not in force | built, and linked | none |
| ADR-0055 | 10.07 | `Mesh`, 23 rows | **not proved** | none | built | none |
| ADR-0056 | 11.06 | none | | none | none | none |
| ADR-0057 | 11.06 | no module; a graph and a checker, which fails at this tree | | | | none |
| ADR-0058 | 11.06 | none | | | | none |
| ADR-0059 | 11.10 | `Federation`, 41 rows | 892, certified | `FD1` to `FD3`: not written | not built | none |
| ADR-0060 | 11.10 | `Intent`, 35 rows | 677, certified | not written | not built | none |
| ADR-0061 | 11.10 | `Membership`, 28 rows, at five replicas | 495, certified | not written | not built | none |
| ADR-0062 | 11.10 | `Alone`, 47 rows, with `Intent` and `PlaneClock` | 263, certified | not written | not built | none |
| ADR-0063 | 11.10 | `Outstanding`, 40 rows | 1,871, certified | not written | not built | none |
| ADR-0064 | 11.10 | `PlaneClock`, 38 rows | 535, certified | | not built | none |
| ADR-0065 | 11.10 | `Peer`, 25 rows | 254, certified | not written | not built | none |
| ADR-0066 | 11.10 | `Release`, 67 rows | 613, certified | not written | not built | none |
| ADR-0067 | 11.10 | none | | fifteen entries in prose; none written as policy | | none |
| ADR-0068 | 11.10 | none of its own | | | | none |

"Certified" is the corpus's word: every SMT proof accepted by the pinned checker, but for the LS4 temporal steps,
which no checker confirms (52 across the eight). Proof counts are read from the results files and were not re-run.

Read down the columns. Proofs exist for the overlay and for nothing else in the set drafted since October: the
workflow modules are checked and unproved, and ADR-0056 to ADR-0058 have no module. The reference follows
ADR-0054 and ADR-0055 and nothing later. No floor entry is written for any record after ADR-0054. No record has
the reader its own ratification condition asks for.

**5.2 Order.** Read from each record's "Depends on" line (annex, `runs/20-proposed-dependencies.txt`):

| Layer | Records | Rest on, among what is not in force |
|---|---|---|
| 0 | ADR-0035, ADR-0036, ADR-0051, ADR-0054, ADR-0057; ADR-0056 | Nothing Proposed. ADR-0056 rests on ADR-0050, which is provisional |
| 1 | ADR-0055 · ADR-0058 | ADR-0054 · ADR-0057 |
| 2 | ADR-0059 | ADR-0058 |
| 3 | ADR-0060 | ADR-0059, ADR-0058, **ADR-0054, ADR-0055**, and ADR-0050 (provisional) |
| 4 | ADR-0061 | ADR-0059, ADR-0060 |
| 5 | ADR-0064 | ADR-0059 to ADR-0061 |
| 6 | ADR-0062 | ADR-0059 to ADR-0061, ADR-0064 |
| 7 | ADR-0063 · ADR-0065 · ADR-0066 | ADR-0062 and below · **ADR-0055**, ADR-0062 · ADR-0062, ADR-0064 and ADR-0052 (provisional) |
| 8 | ADR-0067 | ADR-0059 to ADR-0066 |
| 9 | ADR-0068 | ADR-0059 to ADR-0067 |

So the overlay cannot be ratified ahead of **both** the specification-graph pair and the workflow pair, and two of
its records wait on the two provisional records' exits. Only ADR-0059 says it is conditional on ADR-0058, and no
overlay record mentions ADR-0057 (I2-41). ADR-0067 makes "a floor is ratified" a condition of its own
ratification, which ties it, and ADR-0068 behind it, to the bootstrap reviewer's finding of fitness at the
earliest (I2-42).

**5.3 What ratification would reverse.** The overlay records each list what "the archetype's records would owe".
Taken together, admission to the archetype would reverse or relax accepted text in at least these places, each of
which is C3:

| Accepted text | What the overlay does to it | Named by the overlay? |
|---|---|---|
| ToO §2.11 and ADR-0054's sentence: no principal grants another | Reversed in letter: a plane grants below itself (ADR-0059) | Yes |
| ADR-0045: Byzantine agreement not required | Required at every exposed plane (ADR-0059 §5, ADR-0061) | Yes |
| ADR-0033 §3: the replica fault model, with Byzantine agreement deferred | Changed with it | **No** (I2-9) |
| ADR-0015: an ordered admit before every effect; ADR-0033 §4's void | Given up for a `local` entry (ADR-0062) | Yes |
| ADR-0032 §4: an effect too fast to stop is inexpressible | Reachable by a person (ADR-0066); unmeetable while unattended, three options open (ADR-0060 §5) | Yes |
| ADR-0050: a successor is bounded by the last lease | Bounded by the promoted seating (ADR-0060 §2) | Yes |
| ADR-0038: where a cell's Observer sits | "Either, declared per mission" ⟨Q9⟩ | **No** (I2-5) |
| ADR-0034: an appraisal at every grant | The stack's containment is an assumption of use (I2-10) | **No** |
| ADR-0039, ADR-0041: coupling at the admit; R3 | Moved to the grant for a `local` entry, and R3 quoted short (I2-4) | In part |

**5.4 The status question.** Eight of the ten overlay records carry "C3 does not apply while this is an overlay",
and all ten "a debt against nothing while this is an overlay". That
position is where the set's process stands or falls, and three readers reached it independently (CR-40). If it
does not hold, the ten records are ordinary Proposed records that reverse accepted text, each needs C3 on its
face, and the question the custodian answered ⟨Q11⟩, "archetype or overlay?", has only the first answer available
until ADR-0058 is ratified and says what an overlay record is.

**5.5 Across the sets.** The Proposed sets were drafted weeks apart and meet in four places:

- **Workflows and the overlay.** ADR-0060 and ADR-0065 are written on ADR-0055's mesh, and ADR-0065 would strike
  one of its sentences. ADR-0055's own dependent entries are undrafted (G-13).
- **User scope and workflows.** ADR-0056 refers to "ADR-0054's pending amendment" and "ADR-0054's activation";
  ADR-0054 has neither (G-21).
- **Trusted-base rows.** ADR-0056 numbers its two rows in ADR-0045's series, with no amendment to ADR-0045;
  ADR-0068 numbers twelve in a series of its own, in a schema that is not ADR-0045's (L-7, I2-17).
- **The specification graph and everything after it.** ADR-0057 §2 says a record drafted after it gives each
  clause four parts. None of the eleven records drafted with or after it does (H-24), and the graph built for it
  holds none of them (H-1).

---

## 6. What the method measured

This review was built to say what it read and how well, since "a finding not drawn is not found" was the limit
the diagram exercise of 2026.11.10 named for itself.

**6.1 The coverage ledger.** A skeleton of 1,231 rows was generated before any reading: the 423 clauses
`spec/clauses.py` finds in the sixty-seven records, and, since a clause pin skips half of a record's words, a row
for each record's header, History, Open obligations and other sections, for each pending amendment, for each
trusted-base, adversary and floor-entry row of ADR-0045, ADR-0067 and ADR-0068, and for each artifact and
narrative section in a reader's scope. Each reader filled every row with one of four verdicts. The ledger is the
annex's `ledger.tsv`.

| Reader | Scope | Rows | Checked against | Finding | Read only | Not read |
|---|---|---|---|---|---|---|
| A | ADR-0001 to 0023 | 108 | 35 | 49 | 24 | 0 |
| B | ADR-0024 to 0029 | 63 | 24 | 37 | 2 | 0 |
| C | ADR-0030 to 0032, 0034 to 0036; floor; policies | 88 | 21 | 56 | 11 | 0 |
| D | ADR-0037 to 0043, 0051 | 111 | 43 | 55 | 13 | 0 |
| E | ADR-0044 to 0046, 0053; method | 98 | 37 | 56 | 5 | 0 |
| F | ADR-0047 to 0050, 0052 | 79 | 18 | 60 | 1 | 0 |
| G | ADR-0054 to 0056 | 52 | 16 | 35 | 1 | 0 |
| H | ADR-0057, 0058; the graph | 40 | 8 | 32 | 0 | 0 |
| I1 | ADR-0059 to 0068 against their modules | 211 | 157 | 43 | 11 | 0 |
| I2 | ADR-0059 to 0068 against the corpus | 204 | 70 | 121 | 13 | 0 |
| J | ADR-0033; `mechanism/` | 34 | 11 | 23 | 0 | 0 |
| K1 | the Theory of Operation | 69 | 17 | 21 | 31 | 0 |
| K2 | glossary, guides, indexes, READMEs | 74 | 22 | 42 | 10 | 0 |
| | **All** | **1231** | **479** | **630** | **122** | **0** |

"Checked against" means the reader compared the row with a named artifact. "Read only" means it was read and
compared with nothing, and is the honest weak spot: 122 rows. The two overlay readers share one set of
record rows and differ in what they compared them with.

**6.2 Were the known defects found again?** The readers were not shown the register. Of its open rows, the
graders marked 100 as concrete defects that a careful reader of the named file could find without the list.
After the readers reported, a scorer matched their standing findings against those rows.

| Where the known defect is | Seeds | In a file the readers were not given | Found again | Found in part | Not found |
|---|---|---|---|---|---|
| A: ADR-0001 to 0023 | 3 |  | 3 | 0 | 0 |
| B: ADR-0024 to 0029 | 4 |  | 3 | 0 | 1 |
| C: ADR-0030 to 0032, 0034 to 0036; floor; policies | 6 |  | 3 | 1 | 2 |
| D: ADR-0037 to 0043, 0051 | 2 |  | 2 | 0 | 0 |
| E: ADR-0044 to 0046, 0053; method | 4 |  | 4 | 0 | 0 |
| F: ADR-0047 to 0050, 0052 | 2 |  | 2 | 0 | 0 |
| I: ADR-0059 to 0068 | 15 |  | 8 | 1 | 6 |
| J: ADR-0033; `mechanism/` | 29 |  | 17 | 4 | 8 |
| K1: the Theory of Operation | 2 |  | 2 | 0 | 0 |
| K2: glossary, guides, indexes, READMEs | 33 | 11 | 16 | 1 | 5 |
| **All** | **100** | **11** | **60** | **7** | **22** |

**Eleven of the 100 should not have been seeds.** They are defects inside files under `derived/` (ten rows of the
register's Part II and G11 item 12), and `derived/` had been taken out of the readers' copy so that no reader could
see an earlier finding. The lead drew the seeds and did not exclude them. They have their own column and are in no
rate. **Of the 89 a reader could have found, 60 were found again, 7 in part and 22 not.**

Where the readers were strong is stale text in living files: twenty of the 11.05 feature list's twenty-two stale
sentences were found again without the list (the two missed are in `NOTICE` and `SECURITY.md`), and of sixteen
rows of the reference's own register eleven were found and three more in part.

Where they were weak is instructive, in two places.

- **The reference's code.** Of the format inventory's sixteen seeded findings six were found, one in part, and
  nine not. The nine are facts that only the source and the scripts show: unpinned container images, a digest
  pinned and recorded nowhere, non-canonical JSON under canonical digests, a `Debug` form where every other surface
  uses the serialised one, a function never called, a manifest script that sweeps untracked files into a cut.
  Reader J read the reference once, against its records, and a record says none of these.
- **What the diagrams found.** Of the thirteen diagram findings of 2026.11.10 that were seeded, six were found, one
  in part, and six not. Three of the four module findings were missed (a check a record lists and its module
  abstracts; hold at the end of an extent, stated by no module; losses counted at seven replicas beside a module
  checked at five), by two readers one of whom read every overlay record against its module. That is the diagram
  note's claim seen from the other side: drawing and reading find different things, and neither stands in for
  the other.

The rate is an upper bound on these readers' sensitivity to the kinds of defect this lineage has found before,
on a set the same lineage chose. No count of what remains is drawn from it.

**6.3 Verification.** Every finding went to a verifier that had not found it, with the text at each line it
cites.

| Reader | Reported | Confirmed | Confirmed with a correction | Dropped | Severity changed by the verifier |
|---|---|---|---|---|---|
| A | 41 | 30 | 11 | 0 | 3 |
| B | 35 | 23 | 12 | 0 | 0 |
| C | 52 | 32 | 17 | 3 | 9 |
| D | 39 | 29 | 10 | 0 | 4 |
| E | 39 | 30 | 9 | 0 | 2 |
| F | 48 | 42 | 5 | 1 | 2 |
| G | 33 | 26 | 7 | 0 | 3 |
| H | 26 | 17 | 9 | 0 | 0 |
| I1 | 28 | 22 | 4 | 2 | 2 |
| I2 | 42 | 30 | 12 | 0 | 2 |
| J | 30 | 22 | 7 | 1 | 5 |
| K1 | 26 | 14 | 12 | 0 | 8 |
| K2 | 43 | 31 | 11 | 1 | 7 |
| L | 11 | 0 | 11 | 0 | 2 |
| **All** | **493** | **348** | **137** | **8** | **49** |

Verification dropped 8 findings and corrected many more: a line number, a scope stated too widely or too
narrowly, a count, a quotation cut short. The verifiers lowered the severity of 49 findings and raised
0. Lowered most often: narrative text dated 2026.10.09 that is behind the tree and not contradicted by it,
which the reader had graded as a disagreement between layers. Every one of the lead's own eleven findings came
back with a correction, most often a line number or a clause stated too widely. The dropped
findings are listed in the register (§4) with the verifier's reason.

**6.4 A second reading of rows that were only read.** Of the ledger's rows, 122 are "read only": the reader read the
text and compared it with nothing. Fourteen of those were drawn, at least one from each of the eleven readers that
had any, and given to a fresh reader with one instruction the first did not have: open at least one thing the
clause cites. **Seven of the fourteen carry a finding.** The lead then checked the seven against the tree: six
stand as stated, and one (ADR-0060 §4) is a tension in terms and not a contradiction. One is Low-Medium (ADR-0035's
D-0035-1 has no kind and is cited for every operator's lineage) and six are Low: a trusted-base row that says one
crate was already listed where three were; ADR-0048's Context placing the task "on the operator channel" where
ADR-0050, ratified with it, finds it never was; the narrative's two seat-binding values where ADR-0016 has four; an
erratum in ADR-0020 that names the wrong section; and ADR-0063's title, which keeps the wording its own §3
rejects. They are AU-1 to AU-7 in the register (Part III) and in the annex (`audit.tsv`), and are not counted among
the standing findings above.

What the audit says is that **"read only" does not mean clean**. On a sample this small the rate is no estimate
of anything, and none is drawn from it. It does say where a second reader should start: the 122 rows are marked in
the ledger, and K1's and A's are nearly half of them.

**6.5 Limits.**

- **Same lineage.** A defect this model does not see, it does not see thirteen times. The re-detection rate above
  is measured against defects the same lineage found earlier, so it is an upper bound on sensitivity to that kind
  of defect and says nothing of kinds it has never found.
- **Consistency, not validity.** The readers compared text with text, model and code. Nobody asked whether the
  intent axiom is the right axiom, whether the floor is fit, or whether a bound in effects is one a person can
  rely on. §9 lists those questions for the reader who can.
- **One pass on the older half.** ADR-0001 to ADR-0046 were read once, with depth where a clause had changed since
  the 10.02 review; the records from ADR-0047 on, the bootstrap set and the overlay were read in full.
- **The proofs were not re-run**, and no reader read a proof. That a theorem's statement matches its record was
  checked for the overlay; that its proof is a proof rests on the prover, the certification and the scan, as
  recorded.
- **The graders' work was not verified by a second agent.** The lead read their notes and sampled their rows.

---

## 7. What has improved since 10.02

Stated so that §4 is read in proportion.

- **The 10.02 review's asks were mostly taken.** A record for labels and tool descriptions (ADR-0047 to ADR-0049),
  a principal for the operator (ADR-0050), break-glass decided against R3 as an emergency seating (ADR-0052), a
  residual-risk statement written twice, the Playbook re-marked twice, liveness properties checked and two
  `ENABLED` invariants proved. Four of its seven asks read `appears addressed` in the register and one `partly
  addressed`. The two that are open are the two that need a second person or a built image: a reviewer who is not
  the author, and a principal that passes the confinement profile.
- **A second deductive method.** Sixteen modules are re-encoded in Lean and three packages replay through an
  independent kernel check, with the encodings of three checked against TLC's state graphs (ADR-0053).
- **The prover's defects were found, recorded, scanned for and reported upstream.** That is the one TEVV process
  the corpus has evaluated, and it was its own.
- **Proofs are certified**, twenty-nine of thirty-two, with what does not certify named.
- **The gates reproduce on a platform the corpus never ran them on**, to the verdict (§1). So do the TLC rows of
  ten modules.
- **The corpus acquired tools that read it whole**: clause pins, a specification graph with a checker, a diagram
  family that regenerates byte for byte and found eighteen defects on the day it was extended. Each is Proposed
  or unmeasured, and each found things.
- **The overlay's modules are careful where they were checked.** All 321 rows come out as their rows files
  expect: each mutation meant to break a property breaks it, and each witness is reached. One mutation breaks
  nothing, by design and said so; one conjunct has no mutation, and that is a finding (CR-53). The first revision
  the same day narrowed claims the modules would not carry, ADR-0059 §1's among them.

---

## 8. What would change the grades

In order of leverage per unit of work. `topak-gaps-prioritization-2026.11.11.md` carries the full order, with what is
ripe to ratify.

1. **Engage one reviewer who is not the author.** It is still first, as on 09.25 and 10.02, and it is now cheaper:
   the register is a table to work from, the ledger says what has only been read, and §9 lists what a
   same-lineage review cannot answer.
2. **Cut G12 before drafting anything else.** One cut measures 190 files, puts Batches 38 and 39 in the state of
   record, and forces the narrative, the glossary, both guides and three indexes through the rewrite that is the
   only time stale sentences have ever been fixed (register, §5).
3. **Settle what an overlay record is, in ADR-0029's terms**, before any of the ten is revised again (CR-40).
4. **Carry Batch 34 through**: ADR-0015, ADR-0043 §2, ADR-0029 §5, `RulesFloorBase.tla` and the reference's
   `rules.rs` each still describe break-glass as it was (CR-45), and ADR-0041 §1 still marks in-force entries
   pending (CR-47).
5. **Ratify ADR-0035 or take A2.2 back out of force** (CR-42).
6. **Make the checkers fail when they find something** (CR-57), and rebuild the specification graph so that it
   holds the records drafted since (CR-52).
7. **Revise ADR-0068 and the overlay's edges** (CR-48, CR-49): one pass, with the eighteen diagram findings and
   this review's two overlay readers' findings side by side.
8. **Disposition the register.** 252 open rows is a week of reading for one person, and most are one line each.

---

## 9. Questions for the reader ADR-0029 A2 asks for, ungraded

A review by the drafter's lineage can find where the corpus disagrees with itself. It cannot say whether the
corpus is right. These are the questions this review met and could not put a grade on.

1. **Is the floor fit?** Every gate passes on two platforms. A gate that passes says the floor is total,
   non-vacuous and discriminating, and says nothing of whether it is the floor a deployment should run under
   (G11 item 87; ADR-0029 A4 gives the question to the bootstrap reviewer).
2. **Should a pattern whose first sentence is that no principal grants another carry an overlay in which a
   mechanism does?** ADR-0059 says of itself that it is still delegation. Whether that belongs beside the
   archetype, inside it, or in another corpus is not a consistency question.
3. **Is a revocation bounded in effects, with no bound in time, a guarantee a person can rely on?** ADR-0063
   proves that an honest vehicle produces fewer than `K_up` further effects. What a person downrange needs to
   know is how long that takes.
4. **Is the fairness the liveness results assume meetable?** Assumption A12 and two more conditions stand under
   every leads-to property that TLC checked (G11 item 105), and nobody has asked an operator.
5. **Are the principles the right ones, and should they be ratified?** They are still a synthesis, the drafter's,
   in a derived document (the feature list, Part I).
6. **Does assisted drafting need a criterion of its own?** G11 item 66 has been open since G9 and now rests on
   every text in the tree. This review is one more.
7. **Are the provisional exits the right exits?** The records and the checkpoint state different ones (F-4), and
   which is right is a judgment about what the operator design must show before it is trusted.
8. **Is a per-mission choice of where a cell's Observer sits ⟨Q9⟩ compatible with what an Observer is for?** It
   is the one answer of the twenty that was the custodian's own, and the accepted placement rule says otherwise.
9. **Is one hand, with an assistant, drafting ten records and their proofs in a day a process the corpus should
   allow itself?** Nothing forbids it. This review's verdict is that the rest of the corpus could not keep up.

---

## 10. Post-review note

No disposition was made. Nothing in the tree was changed but the five documents, their annex and the rows of
`derived/README.md` that index them. The 10.02 review is not edited: G9, G10 and G11 measure it, and the index row
says what supersedes it.

Publishing these documents makes five pointers in living files stale, and they are left as they are: the
Reviewer's Guide (three places) and the Adopter's Guide (one) link the 10.09 residual-risk statement and the 10.02
review as the documents to read, and the architecture description's table of sources names the 10.02 review as
"the current review". They belong to the next cut.

Three things in this review's own method should be read as findings against it. It cost more than its plan said,
because the plan underestimated how much each reader would read. It was interrupted once when the account's usage
ran out, and resumed with each reader's context intact. And it changed its own deliverables on the way: the
annex is a directory and not one file, because a table of five hundred rows wants to be sorted and a document
does not.

---

## Sources

**The corpus**, at commit `bbda621` (2026.11.10): `narrative/theory-of-operation.md` (`e737aa042625678d`);
`checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md` (`9d6f95f444455510`); `narrative/glossary.md`
(`69854c0e6df1d532`); the sixty-seven files of `decisions/`; `spec/`, `floor/`, `policies/`, `mechanism/`,
`diagrams/`, `skills/`, `tools/`, `manifests/`.

**Earlier reviews and standing documents**: `derived/topak-critical-review-2026.10.02.md` (`26c60fd33a632422`),
which this supersedes as the current review; `derived/topak-feature-list-2026.11.05.md` (`f2ec0d2b8697077c`);
`derived/topak-residual-risk-statement-2026.10.09.md` (`0af0a985fb418cec`);
`derived/topak-external-alignment-2026.10.09.md` (`594a480ef8b7d4a6`);
`derived/topak-command-chain-diagram-findings-2026.11.10.md`; and the other documents the register's Part II lists.

**External documents**: none re-read. Marks and grades against them are the 10.02 review's and the 10.09
alignment's.

**In-session verification**: §1, with outputs in `derived/topak-self-review-annex-2026.11.11/runs/`. Tools: OpenJDK
21.0.12 with the tracked `tla2tools.jar` (`936a262061c91469`); rustc 1.97.0; Python 3.13.18, and 3.9.25 for the
diagrams; OPA 1.4.2; `cedar-policy-cli` 4.13.0; cvc5 1.4.0 for Linux (`d4c534360e602f07`); ethos at `8dc85c4`,
built here (`b44bc80233578d83`).

**What this does not claim.** That anything it found is new to the custodian. That anything it did not find is
sound. That a finding a verifier confirmed is right. That it is a review under ADR-0029 A2.
