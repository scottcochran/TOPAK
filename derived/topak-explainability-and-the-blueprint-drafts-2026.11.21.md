# TOPAK — Explainability of the design: the two blueprint drafts, the session that produced them, and what each mechanism in the corpus explains

**2026.11.21** · derived · a reading and a summary of a discussion, not a record · basis: the tree at `20b7481` ·
at the custodian's request. It follows `topak-blueprint-Seats-2026.11.21.md` and
`topak-blueprint-Workflow-2026.11.21.md`, both drafts of the same day, and revises neither.

**What was read.** The two blueprints and what they read; `README.md`; `REVIEWERS_GUIDE_README.md` §1 to §5;
`diagrams/README.md` and the leading text of diagrams H5, G3 and C9 (the SVGs were not viewed rendered);
`decisions/README.md`; ADR-0057 §1 to §8; `checkpoints/README.md`; `narrative/README.md` and the architecture
description's §0.5, §10.1 and §10.2; the header comments of the scripts under `tools/` and `spec/` named in §3.
**What was run.** `python3 spec/specification-graph.py check` and `python3 spec/inventory.py --check`, at this
tree; their output is quoted in §5. No prover, model checker, Lean build or test suite was run. **What was not
read.** Most records, the Theory of Operation beyond its headings, and the builder half of
`specification-graph.py`. Where a mechanism is described from its own README or header, the description is that
file's, not a check of it.

## 1. Two senses of the word, and which one this note is about

The corpus already takes a position on explainability, and it is not the subject here. The architecture
description's quality table (§10.1) places *Explainable and Interpretable* as **"narrow by decision"**: a floor
deny names its reason, and decode observability is limited to conformance and substitution detection (ADR-0019,
ADR-0030). That is explainability of **the running system**: why an action was admitted or denied. It is narrow
because a model is havoc and no semantic judgment sits in the admit path. Beside it the same table has
*Transparent* (every admit ordered and recorded, denials included) and *Accountable* (the audit chain from an
effect to the intent axiom).

This note is about explainability of **the design and its assurance**: whether a reader who did not write the
corpus can find out what was meant, what is claimed, why the claim holds, what it rests on, and whether all of that
is still true of the tree in front of them. The session's question was whether decision records, and then
blueprints, help with that. The reviewer ADR-0029 A2 requires is the reader it matters most for.

## 2. The session

Six exchanges, in order. The first, second, fourth and sixth were answered in conversation and are recorded only
here.

1. **Could decision records help explain Lean-proved mathematics?** Yes, where a proof is silent. A kernel
   certifies that a statement follows from the definitions and says nothing of why those definitions, that
   statement or that route. Records fit the definition choices, the correspondence between the informal claim and
   the formal statement, rejected routes, and the trusted base. They do not fit the argument itself, and their
   prose is unchecked, so a record that names a theorem can go quietly wrong when the theorem moves.
2. **Is the Liquid Tensor Experiment's blueprint like the premise lattice?** No. A blueprint graphs how one proof
   is built: lemma on lemma, deep, converging on one theorem. The lattice graphs what each proved property
   assumes: one level deep, evaluated per deployment, never converging. The nearest thing in the corpus to a
   blueprint's "what establishes what" is the specification graph of ADR-0057, not the lattice.
3. **A blueprint for one proof module.** `Seats`, chosen because it is small, proved twice and refined by a model
   of the code. The draft is `topak-blueprint-Seats-2026.11.21.md`.
4. **The PFR project.** An aside: the 2023 Lean formalization of the polynomial Freiman–Ruzsa conjecture, where the
   blueprint served as the unit of collaboration and the work kept pace with the research. Answered from memory and
   not looked up; nothing here rests on it.
5. **A blueprint for `Workflow_proof`.** The draft is `topak-blueprint-Workflow-2026.11.21.md`.
6. **Do records still fill a gap, as an intent layer?** Yes. Every fidelity item in both blueprints came from
   reading a module against a record; without the record there is nothing for the module to be narrower than. The
   answer ended on three layers and two joins: the record for intent, the blueprint for argument, the proof for
   truth. The join from proof to blueprint can be checked by name and digest. The join from record to statement is
   a person reading both.

## 3. The questions a reader asks, and what answers each

Nine questions. The names are this note's.

| | Question |
|---|---|
| **Intent** | What was meant, and who decided it? |
| **Statement** | What exactly is claimed, formally? |
| **Fidelity** | Does the statement say what was meant? |
| **Argument** | Why is the claim true? |
| **Premises** | What does it assume, and what is trusted without proof? |
| **Evidence** | What checked it, and how strong is that? |
| **Reach** | Does it hold for this deployment, and for the running code? |
| **Currency** | Is all of that still true of this tree? |
| **Non-claims** | What is not claimed, and what is known to be wrong? |

What each mechanism contributes, read from the files named:

| Mechanism | Where | Answers | Kept honest by | Its limit |
|---|---|---|---|---|
| **Decision records** | `decisions/` | Intent; Non-claims | Append-only, with typed History rows; a provenance note that marks what the custodian settled (⟨K1⟩…) apart from the drafter's choices; a ratification condition with each item marked met or not; Options considered, Findings, Open obligations | Prose. Nothing mechanical ties a clause to the formal statement that reads it |
| **Checkpoints** | `checkpoints/` | Non-claims; Currency | Never revised; a manifest per cut; errata in the README. §8 of each is "what this does not claim" | A cut is a moment; the tree moves on |
| **Theory of Operation, glossary** | `narrative/` | Intent, as one argument; vocabulary | Revised against each checkpoint and tagged; §12 "where the argument is thin", §13 assumptions of use | Ranked below records and checkpoints; later than the manifest that measures it |
| **Architecture description** | `narrative/` | Reach; Evidence, in summary | §0.5's fifteen correspondence rules, each with the check that enforces it; §10.2's guarantee-to-evidence table | A draft; says itself which four rules do not hold at G12 |
| **TLA+ modules** | `spec/*.tla` | Statement | A header that lists each property in words and what is not modelled; frozen by digest once a record cites them | The statement is as good as the reading of the record it was written from |
| **Mutations and witnesses** | each module's `Mut`, its `Never…` properties, `*-rows.txt` | Fidelity, in part; Intent, in part | TLC: every mutation must break its property and no other; every witness must be reached | They show a module tells a clause from its negation, not that it reads the clause rightly (ADR-0057 §3) |
| **Results files** | `spec/*-results-*.txt` and their Lean and floor kin | Evidence | Dated, never edited; a header of digests for every input and tool | A results file says what was run, not why it passed |
| **Proof modules; certification; the scan** | `spec/*_proof.tla`, `proof-cert.sh`, `proof-scan.sh`, `proof-method.md`, `proof-certification.md` | Evidence; Premises (each theorem's hypotheses) | Every obligation accounted for by the route that closed it; the prover's two known unsound cases looked for | The proof text is written for the prover. It establishes; it does not explain |
| **The Lean route** | `spec/lean/`, `mechanism/lean/`, `floor/lean/` | Evidence, a second derivation | `#print axioms`, a kernel replay, mirrors checked against TLC's state graphs, mutated encodings that fail to build | Proves an encoding; the encoding's faithfulness is a premise |
| **The trusted base** | ADR-0045 Annex A and B | Premises | One row per component, admitted only if its failure can only subtract or its identity is issued | A declaration |
| **The binding table and inventory** | `spec/theorem-premise-binding.md`, `.json`, `inventory.py`, `premise-routes.sh` | Premises; Reach | `inventory.py --check` keeps table and matrix in step; an inventory is computed per declaration | Has rows for 43 properties; the checker lists 23 of 41 modules with none |
| **The specification graph** | `spec/specification-graph.json`, `specification-graph.py`, `clauses.py`; ADR-0057, Proposed | Evidence, graded; Currency; Reach | Typed edges, each pinned at both ends; a checker | §5 below |
| **Pins and sync checks** | `mechanism/corpus-pins.sha256` and `drift.rs`; `proof-sync.sh`; `tools/lean-sync.sh`; `tools/check-pins.sh` | Currency | A test or script fails when a pinned thing moves | Detects movement, not disagreement |
| **Manifests** | `manifests/`, `tools/verify-manifest.sh`, `tools/check-refs.py` | Currency | Each cut measured and verifiable at its commit; every cited path resolved | As above |
| **Trace validation and replays** | `spec/trace2tla.py`, `mechanism-trace-run.sh`; the Lean replays | Reach | Recorded behaviour of the reference replayed through a model, step by step | The paths no trace reached; the architecture description says it is behind the tree |
| **Diagrams** | `diagrams/topak/`, 58 SVGs at this tree | Intent and Statement, as pictures; Evidence, in H3, H5, H6, H7; Premises, in G1 and G3 | Generated; several read the tree at build time, and G3's build fails if the binding table moved; a fixed status vocabulary | Derived and dated: "where a diagram and a record disagree, the record wins". The reviewer's guide says several are behind G12 |
| **Derived documents** | `derived/` | Non-claims (the residual-risk statement, the reviews, the open findings register); orientation (the feature lists) | Dated and frozen; a new one is written | The drafter's own; the reviewer's guide says they do not count as review |
| **Guides** | `REVIEWERS_GUIDE_README.md`, `ADOPTERS_GUIDE_README.md` | Where to start; what to distrust | Kept current; not measured | Conveniences |
| **Skills and process logs** | `.claude/skills/`, `skills/`, `process/` | How the corpus's own procedures run: drafting, ratifying, cutting, proving, auditing claims | Text a second party can follow | Procedure, not content |
| **Blueprints** | the two drafts | Argument; Fidelity, written down | By hand, in the drafts: names, lines and digests compared with the tree | §4 and §6 below |

Two things in that table are easy to pass over and do a good deal of the work.

- **The status vocabulary.** *Proved*, *proved in Lean*, *certified* and *checked* are kept as four words, and
  *holds* and *void*, *Accepted*, *Proposed*, *provisional* and *genesis-provisional* likewise. A reader who learns
  the words can tell from one sentence how much is being claimed. The diagrams' README treats the words as part of
  the family's language.
- **Mutations as recorded alternatives.** `M_SEAT` is "the reference's behaviour before ADR-0037". `M_DEFAULT` is
  the timeout edge ADR-0054 §8 refuses because a grant made by a timeout is forbidden. A mutation is a rejected
  design kept in a form a model checker can run, which is an "options considered" section that cannot go stale
  without a row failing.

## 4. What the two blueprints add, and where they sit

**The gap they fill is the Argument row.** Nothing else in the table says, in words, why a theorem is true. The
proof module establishes it for the prover. Diagram H5 and `spec/proof-method.md` explain the *method*: how any
proof module is built, with `Lease_A1_proof` taken apart as the example. Neither says why `OnlyThinkersAuthor`
needs a strengthening and `OneSeatPerPrincipal` does not, or that three of `Workflow`'s properties hold without
the re-check at apply because what they need cannot be undone between decide and apply.

**Placed in the specification graph's terms, a blueprint does two things.**

- **It opens one *proved* edge.** The graph holds `proved: spec/Seats_proof.tla → spec/Seats.tla` as a single edge
  that leaves "T-0045-31 (the prover)". The blueprint is the inside of that edge: the definitions the proof adds,
  the lemma graph, the argument at each node.
- **It writes down a reading of the *read* edges above the module.** The graph holds
  `read: spec/Workflow.tla → ADR-0054 §5`, reader "the drafter". The blueprint's fidelity section is that reading
  made inspectable, item by item, with the places the module is narrower than the clause.

**What each draft turned up**, in one line each; the drafts carry the detail.

| | `Seats` | `Workflow` |
|---|---|---|
| The idea of the proof | One property is inductive as it stands; the other needs `Alphabets` | Facts that cannot be undone are carried from decide to apply; facts that can are re-checked |
| Where the record enters the proof | `KindBoundKinds`, the whole of ADR-0037 §4's table | `EdgeFacts`, the fixed four-node graph |
| The uncertified steps | Three LS4 steps, which the Lean route replaces | Eleven LS4 steps, with no second route |
| Narrower than the record | Five places; chiefly, two seats at once is forbidden where §1 fixes the seat | Seven places; chiefly, the taint rule is checked of an edge reading its source, not of what a guard reads |
| Other | | Five of nine mutation lemmas restate their hypotheses; the binding has no rows |

**What the form cost.** For `Seats` most of the blueprint restates the module's own comments. For `Workflow` the
graph is flat, ten theorems sharing infrastructure and none using another, so the picture carries little and the
tables carry most. The form earns its keep where an invariant's strengthening is not obvious, and on the fidelity
section in both.

## 5. What the checkers say about the same two modules today

Both commands were run at `20b7481`. The graph file says it was built at `1988f93` and the working tree.

**`inventory.py --check` passes**: 43 rows and 34 other premises agree between the table and its matrix at every
rung, and the 18 derived premises are well formed.

**`specification-graph.py check` exits 1.** Its last line: *FAILED: the sync scripts · 17 stale edges · 2
premise-route verdicts moved by stale edges*. Whether each item is already on one of the corpus's open lists was
not checked. From its report:

- **The graph is mostly readings.** 529 nodes and 495 edges; 388 edges are *read*, 46 *proved*, 21 *trusted*, 20
  *proved of a reading*, 11 *tested*, 4 *generated*, 4 *replayed*, 1 *executed*. Every one of the 41 modules has
  its edge up to its record typed *read, by the drafter*.
- **Only five layers hold nodes.** record 415, model 89, implementation 15, policy 6, assurance 4. Intent,
  vocabulary, interface, runtime and deployment hold none.
- **At the reference, nothing is inherited above the weakest grade.** Of 43 theorems 19 hold as Annex B declares,
  all at grade *trusted* and none at any stronger grade, each through the row T-0045-28.
- **`Seats`.** Both theorems hold at grade *trusted* by the row. The second route, through the model of
  `State::apply`, is reported stale: the *proved of a reading* edge from `topak-core` to `spec/Seats.tla` and the
  replay behind `model-faithful(apply/Seats)` pin a `state.rs` that has since changed. Under the declaration that
  excludes T-0045-28 the results file of 2026.11.03 has both theorems holding and the graph has neither. The
  `Seats` blueprint said the route's staleness "was not re-examined". This is the re-examination, and the checker
  agrees with the 11.11 feature list.
- **`Workflow`.** The edge `proved: spec/Workflow_proof.tla → spec/Workflow.tla` is in the graph. The edges
  `read: spec/Workflow.tla → ADR-0054` and `→ ADR-0054 §12` are stale, §12 having changed since the pin. `Workflow` is among
  the 23 modules no theorem in the binding is checked in. `Workflow_A1_proof.tla` is read by `proof-sync.sh` and by
  no edge, which is the sync-script disagreement the result line names.
- **The edge under the `Workflow` blueprint's first fidelity item is fresh.**
  `read: spec/Workflow.tla → ADR-0054 §5` is in the graph, reader the drafter, and is not among the stale edges.
  Fresh means neither end has moved since it was pinned. It does not mean the two ends agree, and here the
  blueprint reads them as differing: §5 speaks of what a guard reads, and `TaintOK` keys on the source's label.
- **`Seats` has no edge to the clause its second property cites.** The graph holds read edges from
  `spec/Seats.tla` to ADR-0037 and to ADR-0037 §4, and none to §1, which the module's header names for
  `OneSeatPerPrincipal` and which the blueprint's fourth fidelity item is about. Why was not looked into.

The checker also explains. For each theorem it prints the grade, the route that carried it and why it fails one
grade up, for instance that `LeaseAuthorityMonotone` holds at *trusted* through `invariant(Lease_A1)` by the prover
and the *proved* edge, and through the row for reaching the code. That sentence is an answer to Evidence and Reach
for one theorem, generated, and no other mechanism in §3 produces one.

## 6. The joins, and which a tool can see into

| Join | In ADR-0057's terms | Closed by | Can a tool detect that the two ends disagree? |
|---|---|---|---|
| Discussion to record | none; the provenance note | The custodian, marked ⟨K⟩ | No |
| Record clause to module | *read* | The drafter, for all 41 modules | Only that an end moved. Mutations and witnesses support the reading |
| Module to proof | *proved* | The prover, certified route by route; the kernel, for the modules proved again in Lean | Yes |
| Proof to its explanation | none yet | Whoever writes the blueprint | That a named declaration exists at a line, and that the digests are the cited ones. Not that the prose argument is the proof's |
| Module to code | *trusted*, or *proved of a reading*, *replayed*, *tested* | A row, or a model and its replay | In part, and the stronger routes are stale at this tree |
| Theorem to premises | the binding | `inventory.py` | Yes, as bookkeeping |
| Table to picture | *generated* | The diagram generator | For G3; the others are dated |
| Everything to now | pins, manifests | The sync and manifest scripts | Yes, for movement |

Two of the eight are closed by a person alone, and they are the two at the top: what was meant, and whether the
formal statement says it. The session's last answer put the errors that matter there, and the graph's own count,
388 of 495 edges, says the same in the corpus's terms.

## 7. Readings

Each is this note's reading and decides nothing.

1. **The corpus is strong on Premises, Evidence, Currency and Non-claims, and thinner on Argument and Fidelity.**
   The first four have tables, checkers and frozen files. Argument had no mechanism before the two drafts, and
   Fidelity has an edge type whose content is not written anywhere.
2. **A *read* edge names its reader and holds no reading.** ADR-0057 §3 asks that a read edge name its reader,
   because a reading by the drafter and a reading by someone else differ. The graph does so. What the reader
   concluded is nowhere. A blueprint's fidelity section is one form that conclusion could take, and a second
   reader's could take the same form beside it.
3. **Freshness is sometimes read as agreement, and is not.** §5's fifth bullet is the worked case: a fresh edge
   under a clause and a statement that the blueprint reads as differing. The corpus says this of pins in general;
   the case shows it for a clause that a reviewer would care about.
4. **Intent is not in the graph.** The intent and vocabulary layers hold no nodes, so the graph explains a theorem
   down to the code and up to a record's clause, and stops there. What the clause is for is in the record's
   Context and the Theory of Operation, joined by citation, which ADR-0057 §3 says is not an edge.
5. **The diagrams explain structure and method, not argument.** C9 draws the workflow graph and the record; H5
   draws how a proof module is built; G3 draws what every theorem assumes. A blueprint's own picture, the lemma
   graph, was useful for `Seats` and of little use for `Workflow`.
6. **The system's own explainability stays narrow, and that is consistent.** Nothing here widens what an agent's
   action can be made to explain. The design explains itself so that its narrow runtime claim, a deny names its
   reason and every admit is on the record, can be believed.

## 8. If the form is kept

Options, the drafter's, in the order they would cost. Nothing here is proposed as a record.

1. **Leave the two drafts as derived documents.** They are frozen and will fall behind their modules. Cheapest, and
   honest about what they are.
2. **Write the fidelity section alone, per module, where a reviewer will look first.** It is the part that paid in
   both drafts and it is short. The eighteen modules the reviewer's guide lists as having no binding rows are the
   ones a reader has least help with.
3. **Attach a reading to the read edge it is a reading of.** The graph's builder already keeps what is written into
   an edge by hand, a reader and a note. A blueprint's path and digest could be that note, so that a stale
   blueprint is reported with the stale edge and needs no checker of its own.
4. **Draw the lemma graph from the proof module.** The `LEMMA` and `THEOREM` names and their `BY` citations are in
   the text; a generator beside the diagram family's could draw the picture and fail when a cited name is gone,
   which is the check a blueprint's formal links need.

The first costs nothing and the third is the one that would make a blueprint part of the corpus's own account of
its evidence, and not a document beside it.
