# TOPAK — One spec layer per ADR-0057 layer, rendered in each of Piskala's alternatives

**2026.11.06** · derived · an exercise, not a record · **uncommitted** · prepared by Claude at the custodian's request

**The exercise.** ADR-0057 §1 opens the corpus with ten specification layers. D. B. Piskala's
*Spec-Driven Development: From Code to Contract in the Age of AI Coding Assistants*
(arXiv:2602.00180v1) lists, in its Table I, six categories of tool that practise spec-driven
development: BDD frameworks (Cucumber, SpecFlow, Behave), TDD frameworks (RSpec, JUnit, pytest),
API specification (OpenAPI, GraphQL SDL, Protocol Buffers), contract testing (Pact, Specmatic),
AI-assisted SDD (GitHub Spec Kit, Amazon Kiro, Tessl) and model-based design (Simulink, SCADE).
For each layer, one representative TOPAK artifact was chosen and its equivalent written in every
category that can carry it. Where a category has no slot for a layer, no file was written and the
matrix says why.

**The thread.** Every layer is cut through the **lease** (ADR-0031): the premise it rests on, its
glossary entries, §4 and §5 of its record, its two binding-table rows, `Lease_A1.tla`, its
twelve-field schema, the floor entry that reads it (B4), `lease.rs::check_renewal` and
`State::apply_renew`, its recorded traces, and the reference's overlay for it. One thread makes the
alternatives comparable across layers, which a different representative per layer would not.

**What this is not.** Nothing here runs against the tree: the Python imports a `topak` package that
does not exist, the Pact tests a client that does not exist, the Simulink scripts a model nobody
built. Each file is the *shape* an alternative gives the layer, written as that tool's users write
it, with a header naming the TOPAK source and the ADR-0057 §3 edge type the artifact would carry.
Tessl's exact grammar is approximated from its published examples. The author is the same assistant
that drafted ADR-0057, so the reading of what each tool "cannot say" is one reader's.

---

## 1. The matrix

Rows are ADR-0057 §1's layers; columns are Table I's categories. A cell names the file, in bold
where the category is the layer's natural home. *none* means no file: the category has no slot
for the layer, and §2 says what the nearest thing is.

| Layer (ADR-0057 §1) | TOPAK representative | BDD | TDD | API spec | Contract testing | AI-assisted SDD | Model-based design |
|---|---|---|---|---|---|---|---|
| **intent** | ToO §1 "the premise"; ADR-0007; ADR-0025's axiom | `01/bdd/byzantine-agent.feature` (narrative + threat cases) | `01/tdd/test_intent.py` (adversary drawn by Hypothesis) | *none* | *none* | **`01/spec-kit/constitution.md`**, `01/kiro/steering/threat-model.md` | `01/simulink/requirements-table.md` (Informational reqs) |
| **vocabulary** | `narrative/glossary.md` §4, the lease terms | `02/bdd/vocabulary.feature` (`Rule:` per term) | `02/tdd/conftest.py` (fixture per term) | **`02/api/vocabulary.graphqls`** (docstrings, enums) | *none* | `02/kiro/steering/glossary.md` | `02/scade/lease_types.lus` (shared types) |
| **record** | ADR-0031 §4, §5 (`03/topak-clause-ADR-0031-s4-s5.md`, in §2's four-part form) | **`03/bdd/lease.feature`** | `03/tdd/test_lease_record.py` | `03/api/lease.openapi.yaml` (`x-guarantee`) | `03/contract/renew.consumer.pact.spec.js`; `03/contract/specmatic/` | **`03/spec-kit/spec.md`** (FR-nnn), **`03/kiro/requirements.md`** (EARS), `03/tessl/lease.spec.md` | `03/scade/lease_contract.lus` (assume/guarantee) |
| **assurance** | binding rows `LeaseAuthorityMonotone`, `NoActionUnderFencedEpoch`; Annex A | `04/bdd/lease.premises.feature` (tags as premises) | `04/tdd/conftest.py` + `test_lease_assurance.py` (markers; void = skip) | *none* | **`04/contract/renew.provider.verify.spec.js`** (provider states as givens) | `04/spec-kit/plan.md` (Constitution Check) | **`04/simulink/requirements-links.md`** (links, DV status, `sldv.assume`) |
| **model** | `spec/Lease_A1.tla`, mutations, witnesses | `05/bdd/lease-model.feature` (results file as scenarios) | `05/tdd/test_lease_statemachine.py` (stateful property test) | *none* | *none* | `05/kiro/design.md` (Mermaid + invariants in prose) | **`05/scade/lease.lus`** (Kind 2 / SCADE DV properties) |
| **interface** | ADR-0031 §1, the twelve fields; `lease.rs::Lease` | `06/bdd/lease-schema.feature` | `06/tdd/test_lease_schema.py` (pydantic, closed) | **`06/api/lease.schema.json`**, `lease.graphqls`, `lease.proto` | **`06/contract/specmatic/`** | `06/kiro/design-data-models.md` | `06/simulink/lease_bus.m` (Bus object) |
| **policy** | `floor/genesis-floor.cedar` B4; `genesis-tests.json` | **`07/bdd/floor-B4-emit-own-topic.feature`** (the 62 cases' shape) | `07/tdd/test_floor_b4.py` (drives `cedar authorize`) | `07/api/authzen.openapi.yaml` (the PDP, not the policy) | `07/contract/pdp.consumer.pact.spec.js` | `07/kiro/requirements.md` (EARS per conjunct) | **`07/simulink/b4_truth_table.md`** (truth table + Lustre) |
| **implementation** | `lease.rs::check_renewal`, `state.rs::apply_renew` | `08/bdd/steps/lease_steps.py` (step definitions) | **`08/tdd/topak/lease.py`** + `test_lease_unit.py` | `08/api/build.rs` + `generated/` + `operator_service.rs` (generated stub) | `08/contract/provider-verify.md` | `08/spec-kit/tasks.md`; **`08/tessl/`** (spec + generated module) | **`08/simulink/Lease_Renew.c`** (Embedded Coder / KCG output) |
| **runtime** | `trace.rs` traces replayed through `Mechanism.tla`; the results file | `09/bdd/trace-e2e_expiry.feature` (feature generated from a trace) | **`09/tdd/test_replay.py`** (replay through the model) | `09/api/runtime-validation.md` (middleware; Schemathesis) | `09/contract/runtime.md` (Specmatic proxy; Pact results) | `09/kiro/hooks/replay-on-apply-change.kiro.hook` | **`09/simulink/sil_equivalence_test.m`** (back-to-back SIL) |
| **deployment** | ADR-0058 §9, the reference's overlay (`10/topak-overlay.reference.yaml`) | `10/bdd/cucumber.yml` (profiles) | `10/tdd/declaration.yaml` + `conftest.py` | **`10/api/overlay.yaml`** (OpenAPI Overlay 1.0) | `10/contract/pact-broker.sh` (environments, can-i-deploy) | `10/spec-kit/plan.technical-context.md` | `10/simulink/variants.m` (variant configurations) |

Directory prefixes `01`…`10` are `01-intent` … `10-deployment`.

## 2. Where a category has no slot, and what the nearest thing is

| Layer | Category | Why there is no file | Nearest thing in the category |
|---|---|---|---|
| intent | API spec | An API document describes messages; `info.description` is prose nobody checks | `info.description`; `x-` extensions |
| intent | Contract testing | A contract is an exchange; it has no place for a principle | A provider state named after the principle |
| intent | Tessl | A Tessl spec describes one module's capabilities | The capabilities' prose |
| vocabulary | Contract testing | Vocabulary is the OpenAPI's (Specmatic) or the matcher names' (Pact) | The OpenAPI in `03/api` |
| assurance | API spec | No construct names what a response rests on | `x-` extensions, unread by any tool |
| model | API spec, contract testing | Both state properties of one message; a model is a relation over states | Schemathesis's stateful phase (09) follows `links`, which is a workflow, not an invariant |
| model | Spec Kit, Tessl | A plan or spec has no machine-checked model | `plan.md` "data model" prose, as Kiro's `design.md` |
| assurance, runtime, deployment | Kiro, Tessl | No premises, no runtime, no per-deployment declaration | A hook (09), a steering file (10) |

## 3. What the exercise shows, read against ADR-0057

1. **Each category is the natural home of one or two layers, and no category covers the stack.**
   BDD: record and policy cases. TDD: implementation and runtime replay. API spec and contract
   testing: interface. The AI-assisted tools: intent and record. Model-based design: model, policy
   and implementation by generation. The corpus has every layer because it uses a different
   instrument per layer, which is what ADR-0057 §10 says and the paper's Table I shows without
   saying.

2. **The assurance layer is the one the paper's tools barely have** (the derived note's §5.1, now
   demonstrated). Two categories carry a given at all: Pact's provider states, where a state the
   provider cannot establish voids the interactions that rest on it, and Simulink Requirements'
   links with Design Verifier's Proof Assumption blocks, where a requirement with no verifying link
   shows as unverified. Neither computes what a lost premise voids across a deployment; both are a
   per-item, hand-linked version of what `inventory.py` computes from the binding table. The
   pytest rendering (`04/tdd`) had to be invented to get "void" as an outcome, and it still cannot grade.

3. **Grades (ADR-0057 §5) have at most two values anywhere in the paper's set.** Pact's
   *verified* / *pending*, ADR-0049 §4's *checked* / *claimed*, Simulink's *Proven* / *Falsified* /
   *Undecided* on a single objective. No tool computes "holds at *tested*, void at *proved*", because
   no tool keeps more than one kind of edge per artifact. ADR-0057's eight types are a statement
   about a corpus that keeps TLC, TLAPS, Lean, replay, tests and pins on the same clause at once.

4. **The edge types line up with the categories, which is why the paper's three levels felt like
   edge types in the first place** (ADR-0057 finding 1). *Generated*: protoc, Embedded Coder, KCG,
   Tessl in form. *Executed*: a Cedar floor; a Stateflow truth table under its interpreter.
   *Proved*: Kind 2 / SCADE DV / Simulink DV, of the model only. *Replayed*: Simulink Test
   back-to-back, `test_replay.py`. *Tested*: everything BDD, TDD and contract testing produce. *Read*:
   Spec Kit, Kiro and Tessl's edge from code to spec, whatever the tool's marketing says. *Trusted*:
   the gap every category leaves between its model and its running code, which only model-based
   design closes, by a certified generator, for the parts of a system a block diagram can hold.

5. **Where a tool is strongest, it is strongest at the layer the corpus is weakest.** Specmatic and
   JSON Schema make the interface layer cheap and checked; the corpus has it in prose and schema S
   (ADR-0057 §9, "a format gains a schema node when a record next touches it"). The OpenAPI Overlay
   specification is a published overlay format of exactly ADR-0058 §1's shape (keep by default,
   `update` for replace and add, `remove` for omit), minus types on edges and minus any inventory.
   Schemathesis's stateful mode and Simulink's model coverage both report the paths no run reached,
   which is what the *replayed* edge leaves to a person, as a tool output.

6. **The twice-stated guarantee (ADR-0057 §6) appears in every category as a feature, not a
   finding.** The same renewal rule is written here in Gherkin, Python, OpenAPI's `Refusal.reason`
   enum, a Pact interaction, EARS, Lustre and C, and no tool lists the pairs or types the edges
   between them. The corpus's I47 (e) is one such pair; this directory is thirty.

## 4. How to read a file

Every file opens with a header line: `Layer: <layer> · <category and tool> · TOPAK source: <path or
clause>`, then one or two sentences on what the category can and cannot carry at that layer, and
where it helps, the ADR-0057 §3 edge type the artifact would contribute. The code is written as the
tool's users write it; the comments are the exercise's.
