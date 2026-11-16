---
inclusion: always
---
<!-- Layer: intent · Amazon Kiro steering file `.kiro/steering/threat-model.md` · TOPAK source: ToO §1, ADR-0007 -->
<!-- Kiro's home for intent is steering: always-included context the agent reads before every spec and task. -->

# Threat model and premise

**The premise.** An agent is Byzantine at every deployment position. Never generate code that
relies on what a Persona means or intends. Models are outside the trusted computing base.

**The inversion.** The Byzantine threat lives in Build. When you write a floor entry, a gate
predicate or a test, assume its author is adversarial: the predicate must be total, non-vacuous
and discriminating, and the gates check that before anything is promoted.

**Syntactic lift only.** Fields reach the admit path by mechanical, total extraction from a
constrained call interface. Do not add a classifier, an LLM judgment or a heuristic to the admit
path. A classifier's output is an Observer finding and may only subtract authority.

**Monotone subtraction.** Renewal narrows. Bundles subtract from the floor. Revocation needs no
quorum. Any operation that adds authority must be consensus-ordered at a fresh fence.

**When unsure**, refuse: an evaluation error is a deny, an undeclared rung is rung 0, an
undeclared trusted-base row is false.
