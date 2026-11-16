# ADR-0031 §4 and §5 in ADR-0057 §2's four-part form

The TOPAK side of this layer, as a record drafted after ADR-0057 would state it. ADR-0031 was
ratified before ADR-0057, so its clauses are not rewritten; this is what a reader derives from
the binding table and the graph today. Every alternative in this directory is a translation of it.

## §4 — Authority is monotone across renewal

**Goal.** Keep the one authority-increasing operation, the grant, off the high-frequency path, so
that every authority increase in the corpus is consensus-ordered.

**Givens.** BASE (T-0045-1, T-0045-11, T-0045-28, T-0045-29 as `invariant(Lease_A1)`, T-0045-30);
T-0045-10 (rules issued, seats declared); §2's one-live-lease rule ⟨C1⟩, without which §4
guarantees nothing; `T_persona` as a floor value (A2).

**Guarantees.**
- §4.1 For successive leases on one principal, lease(n+1) ⊑ lease(n): the alphabet is a subset and
  the TTL is no longer. A renewal never adds authority.
- §4.2 A renewal keeps `round` and `role` ⟨R1⟩, `bundle` ⟨R2⟩ and `confinement` digest and rung ⟨A1⟩
  unchanged. A change of any of them is a grant.
- §4.3 A renewal re-attests the Persona and confinement; one whose evidence no longer reaches the
  rung is refused and the lease lapses. It is never renewed at a lower rung.
- §4.4 A renewal's `ttl` is at most `T_persona` ⟨A2⟩.

**Discharge.**
| Guarantee | Edge | Type (ADR-0057 §3) |
|---|---|---|
| §4.1, §4.2 | `spec/Lease_A1.tla` → this clause, read by the drafter | read |
| §4.1, §4.2 | `Lease_A1_proof.tla` → `Lease_A1.tla` (`LeaseAuthorityMonotone`; T-0045-31) | proved |
| §4.1, §4.2 | `spec/lean/TopakSpec/Lease_A1.lean` → `Lease_A1.tla` (T-0045-37; `enc-faithful`) | proved of a reading |
| §4.1–§4.4 | `topak-core` `lease.rs::check_renewal`, `state.rs::apply_renew` → `Lease_A1.tla`: `tests/mutations.rs` (M_RENEW, M_ROLE), `tests/confinement.rs` (M_LOWER, M_RENEWLOW) | tested |
| §4.1–§4.4 | `State::apply` → `Mechanism.tla`, 57 traces | replayed |
| all | every theorem's route to the code | trusted (T-0045-28) |

## §5 — Revocation ends the revoked principal's lease; the epoch fences the fleet ⟨R3⟩

**Goal.** Stop one principal without stopping the fleet, and stop the fleet when the scope is unknown.

**Givens.** BASE; T-0045-10; the revocation set as replicated state; an operator's signature (A3,
provisional; ADR-0050).

**Guarantees.**
- §5.1 A targeted revocation ends every live lease matching its target (principal, Persona digest or
  confinement digest) and bars every later grant it matches. The epoch and every other lease are untouched.
- §5.2 An epoch fence increments the epoch; every lease at the old epoch is fenced and every live round ends.
- §5.3 Both are enforced by the mechanism ahead of the floor: no action is admitted under a lease
  whose epoch is fenced.
- §5.4 Both take effect at their log position, need no quorum, and are attributed under F2.
- §5.5 A revocation is permanent within the rules-epoch chain.

**Discharge.** `NoActionUnderFencedEpoch` (§5.2, §5.3) and `RevokedStaysStopped` (§5.1, §5.5): proved
in `Lease_A1_proof.tla`, proved of a reading in Lean, tested in `mutations.rs` (M_FENCE, M_REVOKE),
replayed through `Mechanism.tla`, and trusted at the code (T-0045-28). §5.4's attribution: read.
