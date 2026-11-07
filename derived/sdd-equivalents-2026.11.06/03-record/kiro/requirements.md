<!-- Layer: record · Amazon Kiro `.kiro/specs/lease-renewal/requirements.md` · TOPAK source: ADR-0031 §4, §5 -->
<!-- Kiro writes acceptance criteria in EARS ("WHEN ... THEN the system SHALL ..."), which is the closest any of the paper's tools comes to a numbered guarantee. Numbering `n.m` is what design.md and tasks.md trace to. -->

# Requirements Document

## Introduction

The lease is the composite credential a principal acts under (ADR-0031). This feature covers
its renewal, which may only narrow, and the two tools that end it: targeted revocation and the
epoch fence. Both are the mechanism's, ahead of the floor.

## Requirements

### Requirement 1

**User Story:** As an operator, I want to narrow a running principal's lease without ending its
round, so that tightening is cheap and widening is impossible on that path.

#### Acceptance Criteria

1. WHEN a renewal names an alphabet that is not a subset of the live lease's alphabet THEN the
   mechanism SHALL reject it with "renewal widens the alphabet" and SHALL leave the live lease unchanged.
2. WHEN a renewal names a ttl longer than the live lease's THEN the mechanism SHALL reject it with
   "renewal lengthens the TTL".
3. WHEN a renewal changes the round, role, bundle, confinement digest or confinement rung THEN
   the mechanism SHALL reject it naming the field.
4. WHEN a renewal narrows or keeps the alphabet and ttl and changes nothing else THEN the mechanism
   SHALL apply it at the current log index, mark the old lease ended with reason `renewed`, and make
   the new index the seat's live lease.
5. WHEN a renewal names a ttl greater than T_persona THEN the mechanism SHALL reject it, whatever the floor says.
6. IF the live lease was granted on an appraisal THEN a renewal SHALL carry a fresh appraisal of the
   same guest, and WHEN it does not THEN the mechanism SHALL reject it and SHALL NOT renew at a lower rung.

### Requirement 2

**User Story:** As an operator, I want to stop one principal, so that a revoked Persona or
profile stops without stopping the fleet.

#### Acceptance Criteria

1. WHEN a targeted revocation names a principal, Persona digest or confinement digest THEN the
   mechanism SHALL end every live lease matching it and SHALL add the target to the revocation set.
2. WHEN a grant matches a target in the revocation set THEN the mechanism SHALL reject it.
3. WHEN a targeted revocation is applied THEN the epoch and every non-matching lease SHALL be unchanged.
4. The mechanism SHALL apply a targeted revocation at its log position without a quorum.

### Requirement 3

**User Story:** As an operator, I want an e-stop, so that when the scope is unknown everything stops.

#### Acceptance Criteria

1. WHEN the epoch is incremented THEN the mechanism SHALL end every live lease with reason `fenced`.
2. WHEN an action names a lease whose epoch is not the current epoch THEN the mechanism SHALL
   reject it with `FencedEpoch` before the floor or the bundle is consulted.
3. WHEN an action's own epoch differs from its lease's THEN the mechanism SHALL reject it with `RequestEpochMismatch`.
