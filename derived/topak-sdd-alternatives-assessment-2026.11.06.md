# TOPAK — The spec-driven alternatives against the archetype's choice: relative strengths

**2026.11.06** · derived · an assessment of `derived/sdd-equivalents-2026.11.06/` (the exercise that rendered one
artifact per ADR-0057 layer in each category of Piskala's Table I) against the instruments the archetype chose for
the same layers · reads ADR-0057, ADR-0058 and `derived/topak-specification-graph-2026.11.06.md` · prepared by
Claude at the custodian's request

**What this is.** The exercise produced 72 artifacts in six commodity tool sets: BDD (Cucumber, Behave), TDD
(pytest, Hypothesis), API specification (OpenAPI, GraphQL SDL, protobuf, JSON Schema), contract testing (Pact,
Specmatic), AI-assisted SDD (Spec Kit, Kiro, Tessl) and model-based design (Simulink, SCADE/Lustre). This note
asks, layer by layer, where those tools are stronger than what the corpus uses and where they are weaker, and
what the corpus should take. **It decides nothing**; §4 lists suggested entries, none made. The author is the
assistant that drafted ADR-0057 and the exercise, so the reading is one reader's.

---

## 1. Verdict

The archetype wins where the property is a relation over states or an argument about what rests on what:
model, policy, assurance, and the typed graph that joins them. The alternatives win where the property is the
shape of a message, the standing of a deployment, or the cost of a reader: interface, deployment format,
runtime coverage, and anyone who is not the drafter. The exercise shows no tool that should replace a corpus
choice. It shows four layers where the corpus should import one, and ADR-0057 §10 already licenses that,
because it chooses the formalism by kind of property rather than by loyalty to a toolchain.

## 2. Layer by layer

| Layer (ADR-0057 §1) | Stronger | Why |
|---|---|---|
| intent | Even | Spec Kit's constitution reaches an AI agent on every plan; the corpus's axiom sits in ADR-0025, where an agent reads it only if pointed. The corpus's version is ratified and bound; the constitution is prose |
| vocabulary | Even | The glossary is richer; GraphQL docstrings and Kiro steering put the words where tools consume them |
| record | Archetype | A clause carries givens and discharge (ADR-0057 §2). FR-nnn and EARS carry neither, and Gherkin's "the spec is the test" is one *tested* edge at best |
| assurance | Archetype, by a wide margin | Nothing in the set computes what a lost premise voids. Pact's provider states and Simulink Requirements' links are per-item, hand-made and two-valued; `inventory.py` is computed from the binding table |
| model | Archetype | TLAPS and Lean prove for every constant the assumptions admit. Kind 2 and Design Verifier prove the model only; Hypothesis samples. The mutation-and-witness discipline (ADR-0046) has no counterpart in any category, and it is the corpus's answer to Piskala's false-confidence pitfall |
| interface | Alternatives | JSON Schema with Specmatic is checked on every build. The corpus has prose and schema S, and ADR-0057 §9 concedes it |
| policy | Archetype | A verified evaluator with a mechanized semantics (cedar-spec in Lean) and SMT gates with checked proofs. AuthZEN specifies the decision interface only; a Stateflow truth table has no semantics to prove its interpreter against |
| implementation | Split | KCG and Embedded Coder give a certified *generated* edge from model to C, which the corpus has only as a "could" (Aeneas; ADR-0057 §11). The corpus's hand Lean transcriptions and trace replay beat every test-shaped alternative |
| runtime | Alternatives on reporting | Simulink model coverage and Schemathesis print the paths no run reached. The corpus's replay is stronger evidence, but its coverage is stated by hand (G11 item 56) |
| deployment | Alternatives on format | OpenAPI Overlay 1.0 is a published keep/replace/add/omit format and the Pact Broker's `can-i-deploy` gate runs today. The corpus's declaration has no file format yet (G10 item 64) |

## 3. What the comparison turns on

**The threat model changes the golden rule.** Piskala's golden rule is the minimum rigor that removes
ambiguity. Every alternative reads it against a cooperative author. A Gherkin scenario, an EARS line or a Pact
interaction written by an adversarial Build principal passes trivially, and Cucumber cannot tell a vacuous
scenario from a real one. The floor gates can (ADR-0030 §5). For a corpus whose premise is that the author is
Byzantine (ADR-0007; ToO §1), the minimum rigor that removes ambiguity is the minimum that survives an
adversarial author, and that is most of what the archetype spends.

**The archetype's cost is real, and the exercise makes it visible.** Seventy-two files in six commodity tool
sets were written in an afternoon and would run in any CI. The archetype's chain needs TLAPS, Lean, cedar
symcc, cvc5 and ethos; has a prover known to be unsound in two ways (ADR-0046 A2); has three proof modules
that do not certify; has a stale Lean package (G11 item 103); and has one person ratifying everything. That is
Piskala's tooling-complexity pitfall, which `derived/topak-specification-graph-2026.11.06.md` §2 already names.
The alternatives' deepest strength is that a second reader is cheap, which is ADR-0057 finding 5 in another form.

**Where the corpus is honest and the alternatives are not.** Every alternative conflates "the tests pass" with
"the spec is met". The archetype names the gap as T-0045-28, grades every edge (ADR-0057 §5), and will look
worse for it. That honesty is a strength only if someone reads the grade.

**The twice-stated guarantee is a feature everywhere else.** The renewal rule of ADR-0031 §4 is written in
the exercise in Gherkin, Python, an OpenAPI enum, a Pact interaction, EARS, Lustre and C, and no tool lists
the pairs or types the edges between them. ADR-0057 §6 asks the checker to list them; the corpus has one such
pair (I47 (e)), and the exercise has thirty.

## 4. Suggested entries, none made

1. **JSON Schema nodes** for the lease, the allowlist entry and the tool result, with a Specmatic-shaped
   check in the mechanism's tests. ADR-0057 §9 says "when a record next touches it"; this gives it a date.
2. **A file format for the declaration**, shaped like OpenAPI Overlay with typed edges added. It discharges
   G10 item 64 and ADR-0058's D-g1 at once.
3. **Replay coverage as a tool output**: which `Mechanism.tla` actions no trace exercised. It turns G11 item
   56 from a line a reader writes into a line the checker of ADR-0057 §8 prints.
4. **The floor's case suite in Gherkin form**, generated from `floor/gen-tests.py` and never hand-kept, for
   the non-drafter reader ADR-0029 A2 asks for. It costs nothing and buys the bootstrap reviewer a readable surface.
5. **No edge from code to spec above *read* for the AI-assisted tools**, whatever a tool's marketing says.
   ADR-0058 §7 already imports a supplier's word at *read*; an agent's word is a supplier's.

---

## Sources

`derived/sdd-equivalents-2026.11.06/README.md` §3; ADR-0057 §1, §3, §5, §6, §9, §10, §11 and findings 1, 5;
ADR-0058 §1, §7, §9; ADR-0046; ADR-0030 §5; `derived/topak-specification-graph-2026.11.06.md` §2, §5; G10 item
64; G11 items 56, 103; D. B. Piskala, arXiv:2602.00180v1 (the golden rule and the pitfalls, §VIII and §IX).
