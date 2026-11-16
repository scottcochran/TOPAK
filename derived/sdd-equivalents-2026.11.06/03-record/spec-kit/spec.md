<!-- Layer: record · GitHub Spec Kit `specs/031-lease-renewal/spec.md` (output of /specify) · TOPAK source: ADR-0031 §4, §5 -->
<!-- Spec Kit's spec is the "what", written for a stakeholder and an AI; the "how" goes to plan.md. Its FR-nnn numbering is the counterpart of ADR-0057 §2's numbered guarantees; it has no slot for givens. -->

# Feature Specification: Lease renewal and revocation

**Feature Branch**: `031-lease-renewal`
**Created**: 2026-11-06
**Status**: Draft
**Input**: ADR-0031 §4 "Authority is monotone across renewal" and §5 "Revocation ends the revoked principal's lease; the epoch fences the fleet"

## User Scenarios & Testing

### User Story 1 - An operator narrows a running principal (Priority: P1)

An operator holding a live lease narrows what a principal in its domain may do, mid-round,
without ending the round, and without any possibility of widening it by the same path.

**Why this priority**: Renewal is the high-frequency path. If it could add authority, every
other authority increase being consensus-ordered would mean nothing.

**Acceptance Scenarios**:
1. **Given** seat a1 holds a live lease with alphabet {Read, Emit} and ttl 1000 ms, **When** the
   operator renews it with alphabet {Read} and ttl 500 ms, **Then** the lease is replaced at a new
   log index and the old one stops being live.
2. **Given** the same lease, **When** the operator renews it with alphabet {Read, Emit, Draft},
   **Then** the renewal is refused with "renewal widens the alphabet" and the live lease is unchanged.
3. **Given** the same lease, **When** the renewal changes the round, role, bundle, confinement digest
   or rung, **Then** it is refused naming the field; such a change is a grant.
4. **Given** T_persona is 1 h, **When** a renewal asks for a ttl of 1 h + 1 ms, **Then** it is refused
   by the mechanism, not by policy.

### User Story 2 - An operator stops one principal (Priority: P1)

**Acceptance Scenarios**:
1. **Given** seats a1 and a2 hold live leases, **When** principal a1 is revoked, **Then** a1 holds no
   live lease, a2's lease is untouched, and the epoch is unchanged.
2. **Given** a1 was revoked, **When** a grant for a1 is applied later in the same rules-epoch chain,
   **Then** it is refused.

### User Story 3 - An operator stops the fleet (Priority: P2)

**Acceptance Scenarios**:
1. **Given** any number of live leases at epoch 3, **When** the epoch is incremented, **Then** every
   live round ends and any action naming a lease at epoch 3 is refused before the floor is consulted.

### Edge Cases
- A renewal naming a lease that is not the seat's live lease: refused.
- A renewal of an attested lease with no fresh appraisal: refused; the lease lapses. Never renewed lower.
- An emergency seat's lease: not renewable (ADR-0052 §3).

## Requirements

### Functional Requirements
- **FR-001**: A renewal MUST produce a lease whose alphabet is a subset of, and whose ttl is no
  longer than, the lease it renews. *(ADR-0031 §4.1)*
- **FR-002**: A renewal MUST keep principal, seat, persona, epoch, rulesEpoch, bundle, confinement
  digest, confinement rung, round and role unchanged. *(§4.2)*
- **FR-003**: A renewal whose ttl exceeds T_persona MUST be refused by the mechanism. *(§4.4)*
- **FR-004**: A refused renewal MUST leave the live lease exactly as it was.
- **FR-005**: A targeted revocation MUST end every live lease matching its target and bar every
  later grant matching it, and MUST NOT change the epoch or any other lease. *(§5.1, §5.5)*
- **FR-006**: An epoch increment MUST end every live lease at the old epoch. *(§5.2)*
- **FR-007**: An action under a lease whose epoch is not current MUST be refused before the floor or
  bundle is consulted. *(§5.3)*
- **FR-008**: Revocation and the epoch fence MUST be consensus-ordered log entries that need no quorum. *(§5.4)*

### Key Entities
- **Lease**: twelve fields, closed schema (see 06-interface). Identified by its fence.
- **Revocation set**: replicated; principals, Persona digests and confinement digests barred from grants.
- **Epoch**: a fleet-wide counter; any increment fences every lease below it.

## Success Criteria
- **SC-001**: No sequence of renewals, from any grant, ever yields a lease with wider authority than the grant.
- **SC-002**: A targeted revocation stops exactly the matching principals, verified on a two-seat deployment.
- **SC-003**: After an epoch fence, 100% of in-flight actions under old-epoch leases are refused without a floor call.
