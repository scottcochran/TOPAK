<!-- Layer: deployment · GitHub Spec Kit `plan.md`, the Technical Context and Project Structure sections · TOPAK source: ADR-0058 §9 (the reference's overlay), ADR-0023 §6 -->
<!-- Spec Kit's deployment slot is the plan's Technical Context: the stack, targets and constraints a feature is built for. One plan per feature, not per deployment, so a second deployment is a second plan. Kiro's counterpart is a steering file per workspace; Tessl has none. Neither tool has an overlay or an inventory. -->

## Technical Context

**Language/Version**: Rust 1.82 (mechanism), Python 3.12 (spec tooling), Lean 4 (`tools/LEAN-PIN`), TLA+ (tla2tools 1.7.4 / TLC 2.19)
**Primary Dependencies**: cedar-policy 4.x (floor, linked and pinned by digest), OPA sidecar or WASM (bundle), rskafka (transport), rmcp (MCP)
**Storage**: a Paxos-ordered WAL per replica; Kafka round topics; no database
**Testing**: `cargo test --workspace --release` (155 tests), TLC on every module, TLAPS on 24 proof modules, Lean replay, trace replay through `Mechanism.tla`
**Target Platform**: three replicas in one process tree, Linux; the guest launcher at rung 1 (docker); rung 3 SIMULATED only
**Project Type**: single workspace (`mechanism/` crates) beside `spec/`, `floor/`, `policies/`
**Performance Goals**: none stated by any record; renewal is the hot path and is one `check_renewal` per apply
**Constraints**: the floor is linked, not loaded; any evaluation error is a deny; the lease schema is closed; `K < R` checked at startup
**Scale/Scope**: a reference, not a deployment; the archetype values; nobody ships it

## Deployment position (ADR-0023 §6, ADR-0058)

| Node | Operation | Edge below, as typed | Fresh |
|---|---|---|---|
| ADR-0031 §4, §5; `Lease_A1.tla`; its proof and Lean encoding | keep | as the archetype publishes | yes (pins) |
| `floor/genesis-floor.cedar` | keep; executed as the `workflow` stage | executed | yes; stage Proposed |
| `topak-core` lease arms | add | tested → `Lease_A1.tla`; replayed → `Mechanism.tla`; trusted (T-0045-28) | replay stale for workflows |
| rung-3 appraisal | omit (SIMULATED) | absent | — |

**Inventory**: the four lease theorems hold at *tested* and *replayed*; void at *proved* and above at the code.

## Project Structure

```text
mechanism/crates/topak-core/src/{lease.rs,state.rs,trace.rs}
mechanism/crates/topak-core/tests/{mutations.rs,confinement.rs,drift.rs}
spec/{Lease_A1.tla,Lease_A1_proof.tla,Mechanism.tla,trace2tla.py}
spec/lean/TopakSpec/Lease_A1.lean
```
