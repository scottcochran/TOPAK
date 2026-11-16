<!-- Layer: implementation · GitHub Spec Kit `tasks.md` (output of /tasks; /implement executes it) · TOPAK source: the lease arms of topak-core as the spec in 03-record/spec-kit would have them built -->
<!-- In Spec Kit, Kiro and Tessl the implementation layer is a task list the agent executes against the spec, plus the code it writes. The edge from the code to spec.md is *read*: the agent read the spec and a person reviews the diff. Nothing generates and nothing proves. -->

# Tasks: Lease renewal and revocation

**Input**: spec.md (FR-001 to FR-008), plan.md, contracts/lease.openapi.yaml, data-model.md

## Phase 1: Setup
- [ ] T001 Create `crates/topak-core/src/lease.rs` with the twelve-field `Lease` struct per data-model.md
- [ ] T002 [P] Create `crates/topak-core/tests/mutations.rs` scaffold with `state()` and `params()` helpers

## Phase 2: Tests first (TDD; must fail before Phase 3)
- [ ] T003 [P] `lease_renewal_is_monotone_and_m_renew_is_refused` covering FR-001, FR-004 (US1 scenarios 1, 2)
- [ ] T004 [P] `renewal_cannot_change_round_or_role_and_m_role_is_refused` covering FR-002 (US1 scenario 3)
- [ ] T005 [P] `renewal_cannot_swap_the_bundle` covering FR-002
- [ ] T006 [P] `a_ttl_over_t_persona_is_refused_at_grant_and_at_renewal` covering FR-003 (US1 scenario 4)
- [ ] T007 [P] `no_action_under_a_fenced_epoch_and_m_fence_is_refused` covering FR-006, FR-007 (US3)
- [ ] T008 [P] `a_revoked_principal_persona_or_profile_is_not_granted_again_and_m_revoke_is_refused` covering FR-005 (US2)
- [ ] T009 [P] `one_live_lease_per_principal` covering the Constitution Check's §2 dependency

## Phase 3: Core implementation
- [ ] T010 Implement `Lease::check_renewal` in `lease.rs` (FR-001, FR-002), reason strings as in contracts/lease.openapi.yaml `Refusal.reason`
- [ ] T011 Implement `State::apply_renew` in `state.rs`: live-lease lookup, epoch and rules-epoch fence, T_persona (FR-003), `check_renewal`, old lease ended `Renewed`, `live_by_seat` updated
- [ ] T012 Implement `State::apply` arm `EpochIncrement`: `epoch += 1; end_all_live(Fenced)` (FR-006)
- [ ] T013 Implement `State::check_live`: `FencedEpoch`, `RequestEpochMismatch`, `FencedRulesEpoch` before any floor call (FR-007)
- [ ] T014 Implement `Revoke` entry: revocation set, `end_lease` for matches, grant refused on match (FR-005)

## Phase 4: Integration
- [ ] T015 Expose `renew`, `fence_epoch`, `revoke` on the operator socket per contracts/lease.openapi.yaml (FR-008)
- [ ] T016 Record every `apply` to `TOPAK_TRACE_DIR` (trace.rs) so 09-runtime can replay it
- [ ] T017 Pin `decisions/ADR-0031.md` and `spec/Lease_A1.tla` in `mechanism/corpus-pins.sha256`

## Dependencies
T001 → T003..T009 → T010..T014 → T015..T017. Tasks marked [P] touch different files and may run in parallel.
