<!-- Layer: intent · GitHub Spec Kit `.specify/memory/constitution.md` · TOPAK source: ToO §1, ADR-0007, ADR-0025, ADR-0010 -->
<!-- This is Spec Kit's natural home for intent: /constitution writes it, and every /plan runs a "Constitution Check" against it. -->

# TOPAK Constitution

## Core Principles

### I. An agent is Byzantine at every deployment position
Safety never depends on what a model means or intends. Models stay out of the trusted
computing base. Every guarantee is stated against an agent that may do anything its
alphabet allows. *Rationale: the premise under every record since ADR-0007.*

### II. Semantic judgment is never a lift (NON-NEGOTIABLE)
A field enters the admit path only by syntactic lift: mechanical, total extraction from a
constrained call interface. A classifier's output enters only as an Observer finding, and a
finding may subtract authority, never add it.

### III. The threat lives in Build
Build principals author the specifications, policy and floor that Run is judged against.
Every design choice that looks expensive in Build is paying for this inversion. Silent
abstention, a vacuously true predicate and green gates are a Build failure.

### IV. Intent is the sole axiom
An authentic issuance at the current anchor epoch is what the anchor intended. Nothing else is
assumed about the anchor; it is a havoc issuer bounded by a verified floor (ADR-0025, ADR-0026).

### V. Monotone subtraction
Bundles can only subtract from the floor. Renewal can only narrow a lease. Revocation needs
no quorum because it only subtracts. Adding authority is always consensus-ordered.

## Verified Object

The verified object is the enforcement mechanism, its epoch discipline and a minimal policy
floor (ADR-0010). Components that cannot be specified are kept outside it, and any theorem
that would need them is computed void rather than assumed.

## Governance

This constitution is ratified by the custodian under ADR-0029 and amended by a record, never
in place. Every /plan must pass the Constitution Check against Principles I to V. A plan that
needs a semantic lift in the admit path is refused, not justified.

**Version**: 1.0.0 | **Ratified**: 2026-09-23 | **Last Amended**: 2026-11-06
