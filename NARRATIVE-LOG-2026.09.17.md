# TOPAK — Narrative log (deferred boundaries)

**2026.09.17** · written against ToO rev 5 (`topak-theory-of-operation-2026.09.15-rev5.md`) and G1 · follows `NARRATIVE-LOG-2026.09.15.md`

This log records the custodian's reflection on three items deferred since before G1: the clock model, the
trusted computing base (TCB) enumeration, and container vacuity. It also records what the 09.16–09.17 design
sessions found when those items were finally opened. **Nothing here is applied or ratified.** The session
outputs cited below are analyses and proposals. None has become decision text. Entries are tagged N17-n.

---

## 1. The custodian's account

In Scott's words, lightly edited:

> The three things deferred until now — the clock, the trusted computing base, and container vacuity — were
> deferred first because of laziness, then subconscious procrastination, and then curiosity about what leaving
> them undefined would mean for the spec and the design. I think it was worth leaving them open, because it
> exposed things I wouldn't have thought of otherwise: specifically, the decomposition of features at those
> boundaries.

The three phases are worth keeping apart. The first two explain why the items stayed open. Only the third
explains why the openness was useful. An undefined term forces every feature that touches it to state what it
needs from that term. When those needs disagree, the disagreement shows where the feature boundaries actually
are.

---

## 2. How long each was open

| Item | Where it was carried | Opened in |
|---|---|---|
| Clock model | Boundary register §9.1; carried as "cheap to close" across three checkpoints | *Clock solution practices* (09.17); *W<L<D discussion* (09.17) |
| Container vacuity | ADR-0022 §6, an obligation nothing discharges; ToO rev 5 §2.4 sandbox gap; CR-1 | *Container vacuity gap solutions* (09.16); *Container vacuity options* (09.17) |
| TCB enumeration | Never enumerated; external assessment I.7 (09.12); CR-12 (09.16) | *NIST Measurement and TOPAK TCB gaps* (09.17); *TCB enumeration* (09.17) |

---

## 3. What the openness exposed

### N17-1. The clock: one missing model became four separations

**Before.** "The clock model" was one unwritten item standing behind leases, epoch fencing, vote timeouts, and
`W < L < D`.

**Opened, it split along four lines.**

- **Safety versus liveness.** Epoch fencing already carries safety without reading a clock. Clocks buy only
  liveness. An expired lease that its holder still believes in is not a containment violation, because the fence
  rejects the stale epoch. Clock misbehavior costs availability or detection lag, never containment.
- **Causality versus timing.** ADR-0005's vector clock orders events but bounds no interval, so `W < L < D`
  cannot be discharged from it. The 09.15 Paxos-plus-vector-clock session had already placed the causal frame in
  the Paxos log rather than in agent metadata.
- **Intervals by failure direction.** When an interval's failure *subtracts* authority (lease expiry, passive
  e-stop), it can use a cheap local monotonic clock. When its failure *adds or preserves* authority (break-glass
  time-to-live, Persona expiry), it needs trusted time. This is the monotonicity principle again, now on the
  temporal axis.
- **Placement.** No safety decision reads a clock supplied by a principal. This follows the same placement rule
  as everything else under ADR-0007.

**`W < L < D` split further.** The session offered a choice between "specification invariant" and "deployment
obligation." Scott rejected that as a false dichotomy. The three terms are of three different kinds:

- `W` is guaranteed by the mechanism.
- `L` is an emergent property of a component.
- `D` is an organizational commitment.

The same session found two more things. The letters `L` and `D` were silently reassigned between the 09.11 and
09.12 material. And the property that matters may be a sum measured against time-to-irreversibility, not an
ordering.

**Status.** A clock-model record with three clauses was offered and not taken up. The option of a UPPAAL timed
automaton for the lease module is unaddressed.

### N17-2. Container vacuity: one gap became two problems and two axes

**Before.** One gap: `Contained` is vacuous because ADR-0022 §6 discharges nothing.

**Opened, it split along six lines.**

- **Mechanism versus instant.** Sandbox mechanisms are commodity in 2026. The hard part is the *instant*: the
  moment `Contain` knows it is running inside the mechanism it assumed. That instant is register B12's empty
  cell.
- **Provenance versus effect bound.** The 09.16 three-class taxonomy bundled these two properties. As separate
  ADR-0023 axes, both must clear. An attested external model is still `Mediated` because of prompt egress. An
  in-house Persona on a shared host is still `Mediated` because of its substrate.
- **Rungs, not classes.** Confinement is ordered by attestation strength:
  - rung 0: none declared;
  - rung 1: asserted by the launcher;
  - rung 2: measured boot;
  - rung 3: confidential VM with an independent verifier.
- **A borrowed instant.** Lease grant is already the instant for B6 and B13, so B12 can inherit it. No new
  boundary is needed.
- **Evidence of discrepancy versus absence of evidence.** Sokolov (arXiv:2608.00801) defines a *Contested*
  verdict: signature valid, measurements diverge. TOPAK has no vocabulary for this distinction.
- **Capability versus hermeticity.** If the sandbox enforces the effect boundary, a shell whose only reachable
  effects are workspace writes is observationally `Draft`. ADR-0022's no-shell prohibition could then shrink to a
  hermeticity obligation on the sandbox.

**The gap is on two axes, not one.** The provenance independence criterion is also unwritten. So even a
perfectly attested substrate leaves the archetype's `Contained` set unreachable.

**Status.** An ADR discharging ADR-0022 §6 was offered and not drafted. It would contain the rung table, the
declaration schema, and a TLC reachability witness. The minimal solution, rung 1 alone, was sized at one record
plus one model-checking run.

### N17-3. The TCB: one list became three columns and a ledger

**Before.** One missing list.

**Opened, it split along six lines.**

- **Named versus trusted.** Naming an item costs a sentence. Declaring it trusted costs about six obligations:
  a measurement, a minimum version, a re-attestation trigger, a residual, an assumption of use, and a gate check.
  A declared-untrusted item costs about two.
- **Trusted, explicitly not trusted, and residual.** The not-trusted column is where TOPAK is unusual. It is
  long, and its length is the asset.
- **Authored versus derived.** A proposed derivation rule makes the list mechanical: every `CONSTANT`,
  `ASSUME`, unrefined module, environment step, and floor entry is an entry. This approximates a proof
  assistant's `#print axioms`, so the list can be regenerated per archetype version instead of rewritten.
- **"Zero assumptions" fails in two different ways.**
  - *Mechanically, it relocates.* Verifying the compiler means trusting the verifier; verifying the verifier
    means trusting the hardware.
  - *Formally, it hits ADR-0025's intent axiom.*

  What the hard path actually produces is a monotone ledger whose only permitted moves are discharges.
- **Substrate versus implementation.** The largest residual may be the unverified implementation (CR-4), not the
  sandbox. Stating that would reorder the open list and move CR-1 down.
- **Genesis versus later cost.** Generous enumeration at genesis is cheap now. It weakens the non-increasing-TCB
  rule later (ADR-0029).

**Status.** The session's closing question is unanswered: should the residual column name the unverified
implementation as item one?

---

## 4. The pattern

These are readings, not decisions.

1. **Each item was treated as one feature and turned out to be a seam.** Several features met at each one. None
   could be closed as a single thing, because the features on either side needed different things from it.
2. **All three converge on the lease.**
   - Clock: lease expiry runs on a local monotonic clock with an asymmetric margin.
   - Container vacuity: the lease binds the confinement-profile digest.
   - TCB: the lease's field list is the enumeration, serialized.

   The NIST measurement session reached the lease from a fourth direction, since the identity gaps converge on
   the lease schema. The lease schema is the likeliest next record.
3. **One decomposition shape keeps recurring:** guaranteed by mechanism, measured, or declared. It appears in
   `W`/`L`/`D`, in the TCB's three bins, and approximately in the attestation rungs. ADR-0025's three-way split
   of "infallible" was an earlier instance, and it was available before the `W < L < D` session reached for a
   binary instead.

---

## 5. What deferral cost

The account would be incomplete without this section.

- **Asymmetry with Moon & Varshney.** They enumerate their trusted base in one paragraph (§3.4). TOPAK claims a
  stronger position and has no such section. I.7 and CR-12 both carry this.
- **The exclusivity claim stayed conditional.** Under CR-1, TOPAK cannot say "strictly stronger" until ADR-0022
  §6 is discharged by a mechanism.
- **Letter drift.** `L` and `D` were reassigned while the terms had no home record. The log does not claim the
  deferral caused the drift, only that the drift happened during it.
- **A stale label.** "Cheap to close" was carried across three checkpoints.

None of these is fatal. Each is a sentence a reviewer would otherwise have written.

---

## 6. Carried forward, undecided

| Item | State |
|---|---|
| Clock-model record: principals never read clocks; safety clock-free; named trusted-time intervals | Offered, not started |
| UPPAAL timed automaton for the lease module | Unaddressed |
| Direction for `W < L < D` after the false-dichotomy correction | No direction given |
| ADR discharging ADR-0022 §6 (rungs, declaration schema, witness) | Offered, not drafted |
| Provenance independence criterion for two lineages | Unwritten |
| TCB declaration record with derivation rule and discharge ledger | Offered; blocked on the ordering question in N17-3 |
| Lease schema as the convergence record | Not yet proposed as a record |

---

## Session references

- *Container vacuity gap solutions* (09.16) — https://claude.ai/chat/f2a3e5c2-c36c-4b73-972b-896be44bf376
- *W<L<D discussion* (09.17) — https://claude.ai/chat/33af7e50-7130-44c4-b41b-a53dc5061521
- *Clock solution practices* (09.17) — https://claude.ai/chat/c2090c3b-48ac-4cc0-80ff-9e0bb0ec9bac
- *Container vacuity options* (09.17) — https://claude.ai/chat/eb50f031-7acc-40ca-88ab-318089ea9be2
- *NIST Measurement and TOPAK TCB gaps* (09.17) — https://claude.ai/chat/1cefd439-3f3f-457d-93ca-275f25fbce45
- *TCB enumeration* (09.17) — https://claude.ai/chat/855b9e6d-fdda-4643-9506-d07e014618f9
- *Paxos-plus-vector-clock model-level clock* (09.15) — https://claude.ai/chat/233dfd9a-d41a-4b13-9f77-4faec6b70e24

Corpus: ToO rev 5 §2.4, §8.2, §9.1, §12; G1; ADR-0005, 0007, 0015, 0022 §6, 0023, 0025, 0029; boundary register
B6, B12, B13, §9.1; external assessment I.7; critical review 2026.09.16 CR-1, CR-4, CR-12. External: Moon &
Varshney, arXiv:2605.09045v2; Sokolov, arXiv:2608.00801.
