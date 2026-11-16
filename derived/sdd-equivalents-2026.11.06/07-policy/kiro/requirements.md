<!-- Layer: policy · Amazon Kiro `.kiro/specs/floor-b4/requirements.md` (EARS) · TOPAK source: floor/genesis-floor.cedar B4; ADR-0022 §1, ADR-0030 §1 -->
<!-- EARS is a good fit for a policy entry: each conjunct of the permit's `when` is a WHEN/THEN line. What it cannot say is that this is an *upper bound* the bundle can only subtract from, or that the entry must pass gates before promotion; those are two extra requirements in prose. -->

# Requirements Document

## Introduction

The floor entry B4-emit-own-topic is the Build envelope for `Emit` (ADR-0022 §1): a seat emits
to its own round topic and nowhere else. The floor is an upper bound; a bundle can only subtract.

## Requirements

### Requirement 1 — B4-emit-own-topic

**User Story:** As the mechanism, I want the floor to permit an `Emit` only to the seat's own,
unsealed topic at the current epoch and round, so that no seat can write to another's topic or to
a sealed one.

#### Acceptance Criteria

1. WHEN a request's action is `Emit` AND the principal's domain is `build` AND the lease's
   alphabet contains `Emit` AND the topic's owner is the principal AND the topic's epoch equals
   the context's epoch AND the topic's round equals the context's round AND the topic is not
   sealed THEN the floor SHALL permit the request with reason `B4-emit-own-topic`.
2. WHEN any conjunct of 1.1 is false THEN B4 SHALL NOT be a reason for a permit.
3. WHEN the topic's owner is another seat THEN the floor SHALL deny the request.
4. WHEN the topic is sealed THEN the floor SHALL deny the request.
5. WHEN the topic's epoch is not the current epoch THEN the floor SHALL deny the request.
6. WHEN the principal's domain is `run` THEN B4 SHALL NOT apply; Run's emission variant is `Report` (ADR-0040).
7. WHEN evaluating B4 raises an error THEN the mechanism SHALL treat the decision as deny (ADR-0030 §1).

### Requirement 2 — B4 is an envelope, not the policy

1. The floor SHALL be an upper bound: a bundle MAY refuse an `Emit` B4 permits and SHALL NOT permit one it does not.
2. BEFORE promotion, B4 SHALL pass the floor gates: never errors over schema S (totality), is
   satisfiable and refutable (non-vacuity), and is the reason for some decision (discrimination).
