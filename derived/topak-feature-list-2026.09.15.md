# TOPAK — Feature List

**2026.09.15 (revision 1: sweep)** · drawn from the Theory of Operation checkpoint **2026.09.12**. Superseded as basis by checkpoint 2026.09.15; rows are not re-derived here. · *The Gripping Hand*

A feature list derived from the checkpoint, grouped by core principle, with correspondence to the
National Institute of Standards and Technology (NIST) Artificial Intelligence Risk Management
Framework (AI RMF) Playbook, followed by the Playbook practices TOPAK does not address.

**Basis and limits.**

- Features come from the 09.12 checkpoint only. Sessions after it (Persona ADRs, boundary
  register, archetype degeneracy, forensic floor discussion) are not checkpointed and are not
  counted as features. §11 notes where they would change a row.
- Playbook marks reuse the 2026.09.12 delta inventory, re-verified against the Playbook text for
  MANAGE 2.4 and recounted. **The inventory's tally was wrong** — see §9.
- The eight principles are a synthesis. The checkpoint names only one of them explicitly
  (monotonicity, §3). The other seven are the organizing claims its sections already make; they
  should be ratified or rejected as a list before they appear in the article.

**Status key (features)**

| Status | Meaning |
|---|---|
| **Accepted** | Ratified Architecture Decision Record (ADR) |
| **Accepted · debt** | Ratified against an unwritten record |
| **Derived** | Stated as a consequence in the checkpoint; no ADR of its own |
| **Proposed** | Drafted, not ratified |
| **Open** | Named on the open list; no decision |

**Playbook mark key**

| Mark | Meaning |
|---|---|
| **M** | Matched — mechanism exists and is claimed |
| **P** | Partial — mechanism exists, outcome half discharged |
| **C** | Convertible — mechanism exists, never claimed against the Playbook |
| **G** | Gap — TOPAK's own argument needs it and lacks it |
| **X** | Out of scope — needs a scope declaration |
| **!** | Contradiction — ratified ADR conflicts with a suggested action |

---

## The eight principles

| # | Principle | One-line statement |
|---|---|---|
| **P1** | Verify the cage, not the occupant | Containment is proven about the mechanism under havoc semantics; the model is untrusted by assumption. |
| **P2** | Monotone authority, fail closed | Grants need consensus, denials are local; policy may only subtract; every failure lands on deny. |
| **P3** | One containment component, two domains | `Build(Contain) → Run(Contain)`; Build is where the Byzantine threat lives. |
| **P4** | Universal, evictable principals | One principal type for agents and humans; a principal is anything evictable by an authority other than itself. |
| **P5** | Oversight placed by consistency budget | Human-in-the-loop (HITL), human-on-the-loop (HOTL), and human-out-of-the-loop (HOOTL) follow from each domain's latency budget, not preference. |
| **P6** | Privileged paths are modeled events | Erasure, break-glass, and e-stop are transitions in the specification, not operational side doors. |
| **P7** | Independent observation, bounded evidence | Detection is fault-domain-independent from the thing observed; evidence is scoped for erasure. |
| **P8** | Recorded, decomposable decisions | Every design fork is an ADR; records split when clauses can be superseded independently. |

---

## 1. P1 — Verify the cage, not the occupant

| ID | Feature | Basis | Status | Playbook |
|---|---|---|---|---|
| F1.1 | **Havoc semantics.** Agents are unverifiable in principle; containment holds for any action sequence. Concordant with Moon & Varshney Theorem 3.2. | §2, glossary | Derived | MAP 2.2 **P** · MEASURE 2.5, 2.9 **X** (declared, not blank) · MANAGE 2.3 **M** |
| F1.2 | **Verified object = mechanism + version pinning + epoch fencing + minimal policy floor.** Operational bundles are parameters. | ADR-0010 | Accepted | MAP 4.2 **C** · MEASURE 2.1 **C** |
| F1.3 | **Typed action alphabet; semantic judgment is never a lift.** Finite, totally extracted vocabulary at the boundary. | ADR-0007 | Accepted | MAP 3.3 **M** |
| F1.4 | **Totality, non-vacuity, and discrimination gates, run on bundles *and* on the floor itself.** Required Build gate. | ADR-0007, §1–2 | Accepted | MEASURE 2.1 **C** · MEASURE 2.13 **G** (fourth gate) |
| F1.5 | **`Contain` scope limited to syntactic envelope enforcement.** Semantic concerns are Observer detection, not enforcement. | §4 | Derived | MEASURE 2.4 **P** |
| F1.6 | **Temporal Logic of Actions (TLA+) specification as requirements artifact;** oversight modes model-checkable. | §4 | Derived | MAP 1.6 **C** · MAP 2.3 **G** (TLC vs TLAPS undeclared) |
| F1.7 | **Decidable refinement.** `bundle ⊑ floor` checkable exhaustively or by satisfiability modulo theories (SMT) because the alphabet is finite. | §2 | Derived | MEASURE 2.1 **C** |

---

## 2. P2 — Monotone authority, fail closed

| ID | Feature | Basis | Status | Playbook |
|---|---|---|---|---|
| F2.1 | **Consensus for grants, local for denials** (decision layer). | §3 | Derived | MANAGE 2.4 **M** · reverse delta |
| F2.2 | **Floor refinement.** Bundles may only subtract authority; refinement decided at promotion time in Build. One floor shared by Build and Run. | ADR-0010 | Accepted | MANAGE 4.1 **P** (change management) · reverse delta |
| F2.3 | **Resident default-deny floor.** Pre-blessed, verified, no bundle-fetch dependency; works at cold start and under partition. | ADR-0012 | Accepted | MEASURE 2.6 **C** · MANAGE 2.3 **M** |
| F2.4 | **Stale bundles are monotone-safe.** Bounded below by the floor regardless of age; eventually-consistent (EL) zone 1 sound by construction. | §2 | Derived | MEASURE 2.6 **C** |
| F2.5 | **Lease expiry as passive e-stop.** Stop power is exercised by *not* refreshing the deadman; no deadlock under expired lease or fenced epoch. | §4–5 | Derived | MANAGE 2.4 **M** · reverse delta |
| F2.6 | **Deployment profiles as documented subtractions from an archetype** (architecture layer). | §3, §8 | Open (axis unresolved) | GOVERN 1.3 **C** · MAP 1.5 **C** |

---

## 3. P3 — One containment component, two domains

| ID | Feature | Basis | Status | Playbook |
|---|---|---|---|---|
| F3.1 | **`Build(Contain) → Run(Contain)`.** `Contain` is one component instantiated twice, not a third domain. CI renamed to `Build`. | ADR-0001, ADR-0002 | Accepted | MAP 4.2 **C** |
| F3.2 | **Build is the hostile domain.** A human signing a green pipeline is treated as the documented failure, not the safeguard. | §1–2 | Derived | reverse delta |
| F3.3 | **Build promotion gate on a human signing key, outside `Contain`.** *Proposed replacement (09.15): promotion is a quorum grant by principals with an Observer veto (ADR-0024); roster issued by the trust anchor, which is at the gate (ADR-0025).* | ADR-0002 (amendment drafted) | Accepted | MANAGE 1.1 **P** (contained ≠ should ship) · GOVERN 2.3 **G** (no named role) |
| F3.4 | **Trusting-trust regress terminates on one verified artifact** (the floor) plus a declared axiom set. Build and Run escapes collapse into one proof obligation. | §2 | Derived | GOVERN 4.2 **C** (via trusted-base enumeration) |
| F3.5 | **Build effect stream.** Build's membrane has none; round-topic reuse or a different substrate undecided. | §1, §8 | Open | MEASURE 2.4 **P** |

---

## 4. P4 — Universal, evictable principals

| ID | Feature | Basis | Status | Playbook |
|---|---|---|---|---|
| F4.1 | **Universal principal type:** identity, lease, typed alphabet, topic, epoch, eviction — for agents and humans. | §5 | Derived | GOVERN 1.6 **C** (live, self-maintaining inventory) |
| F4.2 | **Evictability test.** A principal is anything evictable by an authority other than itself; whatever is not is at the gate. | ADR-0002, §1 | Accepted | GOVERN 3.2 **M** · reverse delta |
| F4.3 | **`Contained(p)` vs `Mediated(p)`.** Effect exclusivity demoted to a per-principal predicate; humans are never `Contained`. Theorem inventory splits to match. | §5 | Open (spec change) | MANAGE 1.4 **G** (input) · reverse delta |
| F4.4 | **Attribution property.** Every exercise of authority traces to a lease-holding principal at a known epoch; holds for `Mediated` principals too. | §5 | Derived | MEASURE 2.8 **C** |
| F4.5 | **Human grants are unprivileged.** Approval is a grant needing consensus; a human "this looks wrong" is an Observer finding — admissible to deny, never to admit. | §5 | Derived | GOVERN 3.2 **M** |
| F4.6 | **Listener/Thinker/Reader/Observer (LTRO) decomposition** gives agent principals internal separation of duties; human principals are atomic (stated as a weakness). | §5 | Derived | GOVERN 2.1 **M** |
| F4.7 | **Clean principal decommissioning** via eviction, epoch fencing, lease expiry. | §5 | Derived | GOVERN 1.7 **P** |

---

## 5. P5 — Oversight placed by consistency budget

| ID | Feature | Basis | Status | Playbook |
|---|---|---|---|---|
| F5.1 | **HITL / HOTL / HOOTL defined by enabling condition:** enabling, disabling only, no channel expressible. | §4 | Derived | GOVERN 3.2 **M** · MAP 3.5 **P** · reverse delta (HOOTL) |
| F5.2 | **Placement forced by PACELC budget.** Build (PC/EC) affords HITL; Run (`W < L < D`, ~1s window) leaves HOTL. | §4 | Derived | MAP 3.5 **P** |
| F5.3 | **Admins: HOTL by default, HITL at break-glass and erasure,** quorum-witnessed in both. | §4 | Derived | GOVERN 3.2 **M** |
| F5.4 | **`D` as human-response budget,** not detection lag alone. | §4, §8 | Open | MAP 3.4 **G** |
| F5.5 | **HITL quarantine release in Run,** where the reversibility index moves the guarded unit from action to stage. | ADR-0007, §4 | Derived | MANAGE 2.3 **M** · MAP 3.4 **G** |

---

## 6. P6 — Privileged paths are modeled events

| ID | Feature | Basis | Status | Playbook |
|---|---|---|---|---|
| F6.1 | **Erasure as a modeled event;** sealed round-topic deletion (ADR-0003) plus deletion from the separately governed plaintext store (ADR-0004), with crypto-shredding rejected as primary mechanism; demand taxonomy types 1–5. | ADR-0006 | Accepted · debt (0013) | MEASURE 2.10 **C** · MANAGE 2.4 **!** |
| F6.2 | **Break-glass as a modeled, quorum-witnessed path.** | ADR-0009 | Accepted · debt (0013) | MANAGE 2.3 **M** · MANAGE 2.4 **M** |
| F6.3 | **E-stop vs break-glass asymmetry.** E-stop unilateral and subtracting; break-glass quorum-witnessed and granting. | §4 | Derived | MANAGE 2.4 **M** |
| F6.4 | **Floor exceptions.** Erasure and break-glass are verified-object exceptions at deploy cadence, not refining bundles. | §6 | Derived | MANAGE 4.1 **P** |
| F6.5 | **Exception mechanism:** one authorization model, non-composition of break-glass with erasure, bound on exception count, demand type 5. | ADR-0013 | Open · no owner | MANAGE 2.4 **!** (resolution home) |
| F6.6 | **Floor authorship and change control.** Who may *propose* a floor change, distinct from who may promote a bundle. | ADR-0014 | Open | GOVERN 1.5 **P** · GOVERN 2.3 **G** |

---

## 7. P7 — Independent observation, bounded evidence

| ID | Feature | Basis | Status | Playbook |
|---|---|---|---|---|
| F7.1 | **Observer replicas not colocated with the Thinker;** orchestrator-level shared replicated group (~9 vs ~40 instances). | ADR-0008 | Accepted | GOVERN 2.1 **M** · MEASURE 1.3 **P** |
| F7.2 | **Control-plane facts separated from cognitive payloads.** | ADR-0004 | Accepted (rationale unrecorded) | MEASURE 2.10 **C** |
| F7.3 | **Topic per principal per epoch/round, sealed on emit completion** — the unit of erasure. | ADR-0003 | Accepted · bundling check outstanding | MEASURE 2.10 **C** · GOVERN 4.3 **P** |
| F7.4 | **Kafka is durability within a window** (`acks=all`), not ordering authority, not system of record. | ADR-0005 | Held (pending Observer gate) | MEASURE 2.4 **P** |
| F7.5 | **Replay and audit** of boundary events for incident identification and root cause. | §7, glossary | Derived | GOVERN 4.3 **P** · MANAGE 4.3 **P** |
| F7.6 | **Boundary effects audit.** Effects are exactly {tool invocation, principal emission}; the admit decision is the orderable event; effect exclusivity becomes a mechanism claim. | ADR-0015 | Proposed | MEASURE 2.7 **C** · MANAGE 1.4 **G** (input) |
| F7.7 | **Monoculture declaration;** cross-family Observer required. | §8 | Open | MANAGE 3.1 **G** |
| F7.8 | **Observer quarantine gate** — modeled event or internal step. | §8–9 | Open | MEASURE 2.4 **P** · MEASURE 3.2 **G** |

---

## 8. P8 — Recorded, decomposable decisions

| ID | Feature | Basis | Status | Playbook |
|---|---|---|---|---|
| F8.1 | **ADR log** in Nygard form with explicit status and debt tracking. | §7 | Accepted practice | GOVERN 1.4 **M** · MANAGE 1.3 **P** (against design forks, not a risk register) |
| F8.2 | **No renumbering; tombstones** (ADR-0011). | §7 | Accepted practice | GOVERN 1.4 **M** |
| F8.3 | **Decomposition test** — a clause that can be superseded alone is a separate decision. | §7 | Accepted practice | GOVERN 1.4 **M** |
| F8.4 | **Theory of Operation checkpoint cadence** with ledger, open list, and next-four. | series | Practice | GOVERN 1.5 **P** (no owner for review of the process itself) |

**Work items, not counted as features:** architecture diagram, component × domain mapping table,
signed message format (protobuf vs canonical CBOR), vector clock and causal-frame design, CI →
`Build` rename sweep.

---

## 9. Correspondence summary

**Recount.** The 09.12 delta inventory stated M 5 · P 6 · C 14 · G 8 · X 38. Its own row marks
sum to **M 6 · P 12 · C 15 · G 9 · X 30 · ! 1** (72 rows). Two errors caused it: MEASURE has 22
subcategories, not 19, and MANAGE 1.4 is marked G but was dropped from the "eight G rows" list.
The numbers below use the row marks.

| Function | Rows | M | P | C | G | X | ! |
|---|---|---|---|---|---|---|---|
| GOVERN | 19 | 3 | 3 | 4 | 2 | 7 | — |
| MAP | 18 | 1 | 2 | 4 | 2 | 9 | — |
| MEASURE | 22 | 0 | 3 | 6 | 2 | 11 | — |
| MANAGE | 13 | 2 | 4 | 1 | 3 | 3 | 1 (on 2.4) |
| **Total** | **72** | **6** | **12** | **15** | **9** | **30** | **1** |

**By principle.** P2 and P6 carry nearly all of MANAGE. P4 and P5 carry GOVERN 3.2, the strongest
governance fit. P1 carries the TEVV (test, evaluation, verification, and validation) rows. P7 is
where MEASURE lands, and it is the principle with the most open features — which is why MEASURE is
the weakest function.

**Convertible rows (addressed, unclaimed).** Fifteen rows where the feature exists and only a
sentence is missing: GOVERN 1.2, 1.3, 1.6, 4.2 · MAP 1.5, 1.6, 3.2, 4.2 · MEASURE 1.1, 2.1, 2.6,
2.7, 2.8, 2.10 · MANAGE 2.1. These are not unaddressed and are excluded below. Two of them (MAP
3.2, MANAGE 2.1) depend on carried-off analyses — the per-component cost table and the
hierarchy-of-needs drop order — that exist in session history but not in any checkpoint.

---

## 10. Playbook practices not addressed

### 10.1 Gaps — TOPAK's argument needs these (9)

| Subcategory | Unaddressed practice | Why it can't be scoped away | Nearest home |
|---|---|---|---|
| **GOVERN 2.3** | Executive accountability for AI risk decisions | The Build signing key sits outside `Contain` by design and has no named role or seniority. | ADR-0014 |
| **GOVERN 6.2** | Contingency for third-party failure | Model provider unavailability or silent substitution is not a modeled event. The "army of one" degraded mode (09.10) answers it and was never filed. | New ADR; recover 09.10 |
| **MAP 2.3** | Scientific integrity and TEVV method disclosure | "Proven absolutely" is unbacked until TLC model checking vs TLAPS proof is declared. | Checkpoint §2 |
| **MAP 3.4** | Operator proficiency defined and assessed | `D`, quarantine release, and break-glass presume a present, trained, authorized human. | F5.4 |
| **MEASURE 2.13** | Evaluate the effectiveness of TEVV processes themselves | Moon & Varshney §4.6 / Appendix B: a vacuous spec passes all three gates. The fourth "floor fitness" gate is this. | F1.4; no owner |
| **MEASURE 3.2** | Risk tracking where measurement is unavailable | `W < L < D` requires `L`; Observer latency and false-negative rate are unbounded. | F7.8; rung manifest |
| **MANAGE 1.4** | Residual risk documented for acquirers and users | Trusted base, sandbox gap, `Mediated` out-of-band effects, and floor exceptions exist only in pieces. | Residual-risk statement |
| **MANAGE 3.1** | Third-party risks monitored with documented controls | One model family across LTRO seats is concentration risk with no control attached. | F7.7 |
| **MANAGE 3.2** | Pre-trained models monitored in regular maintenance | Mechanism, bundle, floor, and epoch are pinned; the model is not. | See §11 |

### 10.2 Contradiction (1)

| Subcategory | Practice | Conflict | Proposed resolution |
|---|---|---|---|
| **MANAGE 2.4** | Preserve materials for forensic, regulatory, and legal review | ADR-0006 destroys sealed round topics and ADR-0004 plaintext. *(Earlier documents said "crypto-shreds"; ADR-0003 rejected crypto-shredding as primary. The contradiction stands on the correct mechanism.)* | Forensic floor — a bounded fact set surviving erasure and break-glass — as an ADR-0013 obligation. Frame under MEASURE 2.10 as a recognized privacy-versus-forensics tradeoff. |

### 10.3 Partially addressed — the unaddressed half (12)

| Subcategory | Addressed | Not addressed |
|---|---|---|
| GOVERN 1.5 | Incident response | Periodic review of the risk process itself; review ownership and frequency |
| GOVERN 1.7 | Principal decommissioning | System decommissioning: key destruction, retention wind-down, topic disposition |
| GOVERN 4.3 | Incident identification via replay and audit | External information sharing |
| MAP 2.2 | Havoc as a stronger substitute for knowledge limits | Explicit statement of the substitution |
| MAP 3.5 | Oversight defined and documented | Oversight *assessed* — blocked on `L` |
| MEASURE 1.3 | Mechanical independence (ADR-0008) | Human independent assessors |
| MEASURE 2.3 | Deployment-like environment (compose rig) | Documented assurance criteria |
| MEASURE 2.4 | Production monitoring via Observer and effect stream | Measured detection quality |
| MANAGE 1.1 | Go/no-go on containment | Go/no-go on purpose ("should it ship") |
| MANAGE 1.3 | Documented responses to design forks | Responses traced to a mapped risk register |
| MANAGE 4.1 | Override, incident response, change management | Appeal, user input, system decommissioning |
| MANAGE 4.3 | Incident tracking and root cause | Communication to affected communities (constrained by erasure) |

### 10.4 Out of scope — need a declaration, not a design (30)

Legitimately absent, but each is still an unaddressed practice until a scope statement discharges it.

| Group | Subcategories |
|---|---|
| Legal, regulatory, third-party IP | GOVERN 1.1, 6.1 · MAP 4.1 |
| Organizational culture, training, diversity | GOVERN 2.2, 3.1, 4.1 · MAP 1.2 |
| External stakeholder feedback | GOVERN 5.1, 5.2 · MEASURE 3.3 · MANAGE 4.2 |
| Mission, purpose, value, benefits | MAP 1.1, 1.3, 1.4, 2.1, 3.1 |
| Impact likelihood and stakeholder engagement | MAP 5.1, 5.2 |
| Metrics program lifecycle | MEASURE 1.2, 3.1, 4.1, 4.2, 4.3 |
| Model- and content-level evaluation (disclaimed by havoc) | MEASURE 2.2, 2.5, 2.9, 2.11 |
| Environmental impact | MEASURE 2.12 |
| Organizational prioritization and value sustainment | MANAGE 1.2, 2.2 |

MEASURE 1.1 (convertible) is the instrument that discharges most of the metrics-lifecycle group:
it explicitly accommodates documented non-measurement.

---

## 11. Post-checkpoint movement — not yet in the series

These sessions change rows above but are not checkpointed, so they are noted rather than counted.

| Row | Movement since 09.12 |
|---|---|
| MANAGE 3.2 (G) | The MANAGE 3.2 session drafted the Persona as a verified model artifact, provenance as the deployment axis, decoder/validator split, decode observability, and boundary-only replay. Likely moves G → P or M once checkpointed. |
| GOVERN 6.2 (G) | Same session: archetype excludes external models, which narrows but does not close provider-failure contingency. |
| MANAGE 2.4 (!) | Log legibility replacing immutability, and stop attribution as non-erasable under the forensic floor, sharpen the ADR-0013 resolution. |
| GOVERN 1.3 / MAP 1.5 (C) | Degeneracy as the deployment-variation relation (ADR-0023 draft) resolves the axis question that blocked F2.6. |
| GOVERN 2.3 (G) | The boundary register found no owner column and an unowned boundary; same gap, wider. |
| Numbering | Settled in checkpoint 2026.09.15 §1: Persona series 0016–0020; Build records 0021/0022. |
