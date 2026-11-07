<!-- Layer: assurance · GitHub Spec Kit `plan.md`, the Constitution Check section · TOPAK source: the binding table's premise column -->
<!-- Spec Kit's only assurance construct is the Constitution Check: a gate table the plan must pass before Phase 0, and re-pass after design. It can name what a plan rests on; it cannot compute what is lost when a premise fails. Kiro and Tessl have no slot at all. -->

# Implementation Plan: Lease renewal and revocation

**Branch**: `031-lease-renewal` | **Spec**: [spec.md](../03-record/spec-kit/spec.md)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | How this plan honours it, and what it rests on |
|---|---|---|
| I. Byzantine agent | PASS | Renewal and revocation are operator paths; the Persona never requests them. Rests on T-0045-10 (seats declared) and ADR-0050's operator seating (provisional). |
| II. Syntactic lift only | PASS | `RenewRequest` is a closed JSON object validated by shape; no field is interpreted. |
| III. Threat in Build | PASS | The renewal check is a mechanism constant, not policy: a bundle cannot widen it. Rests on ADR-0030 §1 (`FloorComposition`, T-0045-3). |
| IV. Intent is the sole axiom | PASS | No new issuance kind. T_persona is a floor value, changed by issuance and promotion. |
| V. Monotone subtraction | PASS | §4.1 is the clause. **Rests on §2's one-live-lease rule**: if a grant may replace a live lease, this gate is vacuous (ADR-0031 ⟨C1⟩). Checked by `Lease_A1.tla`, proved by `Lease_A1_proof.tla` (T-0045-31). |

**Premises this plan does not discharge and inherits as trust roots**: T-0045-28 (the code
refines the modules; no refinement exists), T-0045-29/31 (TLC and the prover). **Premises void at
the reference**: none for this feature. Rung-3 renewal re-attestation (§4.3) rests on T-0045-16
and T-0045-17, SIMULATED only; the plan implements it and marks the test void.

## Complexity Tracking
| Violation | Why needed | Simpler alternative rejected because |
|---|---|---|
| none | | |
