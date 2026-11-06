# TOPAK — Spec-driven development and the specification graph

**2026.11.06** · derived · a summary of a discussion between the custodian and the assistant, which read D. B.
Piskala, *Spec-Driven Development: From Code to Contract in the Age of AI Coding Assistants* (arXiv:2602.00180v1,
2026.01.30) against the corpus at G11 and the tree at `fc25c9f`, and ended in two Proposed records, ADR-0057 and
ADR-0058 · prepared by Claude at the custodian's request

> How would you categorize TOPAK on Piskala's spec spectrum? … Hierarchical spec layers (DAG?); ADR as intent: goals,
> gates, guarantees; domain-appropriate spec frameworks; implementation-adjacent spec: spec as code, spec-code-spec.
> More layers? What standard spec frameworks fit each? How does TOPAK map? … Keep it prescriptive: what TOPAK does,
> should do, could do.

**Verdict:** on Piskala's line TOPAK is **spec-anchored**, more strongly than the paper describes, with one slice
**spec-as-source** (the floor) and one slice **spec-first for now** (workflows). But the line is the wrong shape for
it. The paper's levels are properties of the **relation between two artifacts**, and the corpus has many relations at
different strengths. Arranged as a graph of specification layers with typed edges, the levels become edge types, and
a theorem can be said to reach the code at a **grade**. ADR-0057 states that for the corpus; ADR-0058 states how a
deployment and a supplier declare their own graph against it.

---

## 1. The paper

Piskala defines three levels of specification rigor along one axis of "specification authority":

| Level | The spec | Alignment |
|---|---|---|
| **Spec-first** | Written before the code, guides the first build, may be abandoned | None after the build |
| **Spec-anchored** | Kept alongside the code for its life | Tests derived from the spec fail when they diverge (BDD, OpenAPI with contract tests) |
| **Spec-as-source** | The only artifact humans edit; code generated and never edited | By construction (OpenAPI stubs; Simulink to certified C) |

It gives a four-phase workflow (specify, plan, implement, validate), a decision tree (AI or complex requirements →
long-lived → code generation viable?), a golden rule ("the minimum level of specification rigor that removes
ambiguity"), and five pitfalls: over-specification, specification rot, specification as bureaucracy, tooling
complexity and false confidence.

## 2. Where TOPAK sits

**Spec-anchored, as the paper's definition reads**: the records and checkpoints are the state of record, the modules
are written against them and can revise them before ratification (ADR-0047 R10), and `drift.rs` fails the build when a
pinned record or module moves. The Rust is hand-written, which rules out spec-as-source for the mechanism.

**Stronger than the paper's anchoring**, which is tests derived from a behavioural spec. The corpus adds trace replay
through `spec/Mechanism.tla`, Lean proofs of transcriptions (`admit.rs` a step of `FloorComposition`'s `Decide`), a
refinement of a model of `apply` to `Seats`, and mutations that every property must catch, which answers the paper's
"false confidence" pitfall better than anything in it. It is also more candid: ADR-0045 strikes the claim that the
drift test shows the code follows the spec, and keeps T-0045-28, "no refinement exists", in every theorem's BASE.

**Different per layer**:

| Layer | Position | Basis |
|---|---|---|
| Records ↔ modules | Two-way | ADR-0047 R10 |
| Cedar floor | Spec-as-source | Linked verbatim, pinned by digest |
| Admit decision | Anchored, proved of a transcription | `mechanism/lean` |
| `State::apply` | Anchored by replay; seat arms by a refined model | Trace validation; `SeatsModel.lean` |
| Operators | Weakly anchored | Tests named after `Operators.tla`'s properties, no refinement (I47) |
| Workflows | Spec-first for now | Not modelled in `Mechanism.tla`, not replayed; `mechanism/lean` stale (G11 items 56, 103) |

**Two things the paper's frame misses.** Its spectrum puts *generation* at the top, though its abstract says code is
"generated or verified": the corpus reaches agreement by construction through proof and refinement, a position the
figure lacks. And its specs are inputs to AI coding assistants; the corpus's floor and alphabets also bind AI agents
while they run, which is spec-as-source in a sense the paper does not discuss.

**The pitfalls that apply** are tooling complexity and bureaucracy. The corpus's answer is that a safe-by-design
pattern for Byzantine agents is the safety-critical case the paper says justifies the most rigor; the stale Lean
packages and the unreplayed workflows show the cost is real.

## 3. The four ideas, and what the discussion made of them

**Hierarchical layers, as a DAG.** Yes, and not a tree: one clause is read by several modules and one module reads
several clauses. Three refinements: **type the edges**, which is where the paper's levels belong; keep **two graphs on
the same nodes**, what implements what (`corpus-pins.sha256`) and what rests on what (the binding table); and take
**feedback upward** (a module revising a record) as a new version of a node, so each version's graph is acyclic.

**ADRs as intent: goals, gates, guarantees.** Right home, with two additions: **givens**, the premises a guarantee
rests on, which the corpus keeps in the binding table and not in the record, and which make each clause an
assume-guarantee contract (Benveniste et al., *Contracts for System Design*); and **stable ids**, so that lower layers
bind to a guarantee and not a file. "Gates" collides twice in the corpus (floor gates; promotion gates), so ADR-0057
names the fourth part **discharge**, as a drafter's choice the custodian can reverse.

**Domain-appropriate frameworks.** Yes, chosen by **kind of property** rather than business domain, and with a named
category for what cannot be specified: the corpus keeps models outside the verified object (ADR-0007), and the graph
holds such components as nodes with no edge below the record, so the theorems that would need one compute void.

**Implementation-adjacent specs.** The most valuable of the four, because it addresses the weakest edge: model to
code. Spec-code-spec is round-trip checking, a model extracted from the code and checked against the specification;
the corpus does it statically (Lean transcriptions) and dynamically (trace replay), and in both the extraction is by
hand (`enc-faithful`, `model-faithful`). Automated extraction (Aeneas, Rust to Lean) would close it.

## 4. Layers and the frameworks that fit them

The set of layers is **open** (the custodian's decision); these are the ones the corpus has, with three the discussion
added: **assurance**, **interface** and **deployment**.

| Layer | Standard frameworks | In the corpus | Edge to the layer below |
|---|---|---|---|
| Intent and threat model | GSN goals, KAOS, i*, STRIDE, STPA | ToO; ADR-0025's intent axiom | Read |
| Records (goal, givens, guarantees, discharge) | ADRs (Nygard, MADR) with assume-guarantee contracts | `decisions/`, batches, checkpoints | Two-way with the models |
| Assurance argument | GSN, SACM; UL 4600 and ISO 26262 safety cases | ADR-0045 Annex A and B; the binding table; `premise-routes.sh` | Computed |
| Abstract behaviour | TLA+, Quint, P, Ivy, Alloy; Tamarin and ProVerif for security protocols | `spec/*.tla`, TLC with mutations and witnesses, TLAPS, `spec/lean` | Proved within; graph-checked against Lean |
| Interfaces and data | JSON Schema, AsyncAPI, protobuf, MCP tool schemas, Cedar schemas | Schema S; ADR-0049; otherwise prose | Weak: prose to Rust; some formats exist only in `mechanism/` |
| Executable policy | Cedar with its Lean model, Rego, Zanzibar-style models | `floor/`, `policies/` | Executed |
| Implementation | Verus, Kani, Creusot, Prusti; Aeneas, hax | `mechanism/`, `mechanism/lean` | Trusted (T-0045-28); proved of a reading for two pieces |
| Runtime | TLA+ trace validation, runtime-verification monitors, model-based testing (Quint, Apalache) | Trace replay and its results | Replayed, for tested paths |
| Deployment and evidence | in-toto and SLSA attestations; digest manifests | The Guide's declaration, Annex B, `manifests/` | Pinned |

A **vocabulary** layer (the glossary; DDD's ubiquitous language) belongs on the list too.

## 5. What the lens shows about the corpus

1. **The assurance layer is what distinguishes it.** Most spec-driven projects have none; the corpus computes which
   theorems a lost premise voids, which assurance-case tools usually leave to people.
2. **The weakest edge is model to code, and every theorem is conditional on it** (T-0045-28 in BASE).
3. **One guarantee is stated twice with only tests between**: the operator envelope, in Cedar and in Rust (I47 (e)).
4. **The edges already exist, in four places**: corpus pins, the binding JSON, manifests and the sync scripts, each
   with its own notion of stale.
5. **The labels are honest**, which is rarer than the layers. The cost of the layers is Piskala's tooling-complexity
   pitfall; the remedy is that every component has some path from intent to code, every edge on it is typed, and the
   type is true.

## 6. Does, should, could

| | Does | Should | Could |
|---|---|---|---|
| Layers | Records, models, proofs, Lean, floor, bundle, reference, manifests | Name each node's layer; add layers as needed | — |
| Guarantees | Clauses by section; premises in the binding | Goal, givens, guarantees, discharge per new clause | GSN export |
| Edges | Pins, sync scripts, derived premises, apart | Typed edges, each a premise, in one graph | Generate the four lists from it |
| Grades | Holds or void | Inventory at each grade | Per-axis grades if the order fails |
| Drift | Whole-file pins | Clause pins | — |
| Twice-stated guarantees | Tied by tests | Listed with their type | Generate one from the other, or prove them equal |
| Model to code | T-0045-28; replay; transcriptions by hand | T-0045-28 as a derived premise with every route | Aeneas extraction; Verus or Kani locally |
| Replay coverage | Tested paths; workflows not replayed | Stale and missing edges reported | Model-based test generation |
| Interfaces | Prose and schema S | A schema when a record touches a format | AsyncAPI for every topic |
| Runtime | Test traces replayed | — | Monitors from the modules' invariants |

## 7. The custodian's decisions

1. **The set of layers is open-ended.**
2. **Inheritance is graded.**
3. **No brand name.** The obvious name was taken; the graph is *the specification graph*, a description.
4. **Two records**: one for the corpus's method, one for adopters and the ecosystem.
5. **Prescriptive**: say what to produce, and what the corpus does, should do and could do.

## 8. What the two records carry

**ADR-0057, the corpus.** Artifacts are nodes with open layers. A new clause has a goal, givens, guarantees and a
discharge. Eight edge types, ordered by what each leaves to a person: *executed*, *generated*, *proved*, *proved of a
reading*, *replayed*, *tested*, *read*, *trusted*. Each edge contributes a `check` premise, false when stale or absent;
ADR-0053's derived premises are instances, and T-0045-28 becomes a derived premise. **A grade is a threshold, and the
inventory at each grade is a binary inventory**, so ADR-0023 §2's "no partial credit" holds at every grade, and the
inventory at *trusted* is the one computed today. Theorems are graded downward, to the layer that runs; each module's
reading of its record is graded once, and is *read*, by the drafter, everywhere. Twice-stated guarantees are listed;
pins move to clauses; one graph is checked against the four lists before it replaces them.

**ADR-0058, adopters and suppliers.** The archetype publishes its graph by version; a deployment's graph is an overlay
of keep, replace, add and omit. A replaced node re-establishes each edge at a declared type or declares it absent. The
method is the deployment's, and the type follows from what the edge leaves; a prover with no row is a D-row and an
upstream report. The declaration publishes its inventory at every grade, with each node's standing. A deployment can
grade above the archetype without exceeding its inventory, and reports the route upstream. Suppliers publish
subgraphs, imported at their check's type if rerun and as *read* if not: ADR-0049's *checked* and *claimed*,
generalized. The reference is the first overlay.

## 9. Open questions for review

- **Is the order of edge types total?** *Executed* against *generated*, and *proved of a reading* against *replayed*,
  are the doubtful pairs (ADR-0057 finding 4).
- **Does a grade read as partial credit** to a C3 reviewer of ADR-0023 §2 (ADR-0057 finding 3)?
- **Who reads the edges up**, from records to modules, when every reading so far is the drafter's (ADR-0029 A2)?
- **Where does the generic prover row live**: Annex A by its own record, or the archetype-evolution record (ADR-0058
  finding 2)?
