# TOPAK — NIST AI RMF Playbook Delta Inventory

**2026.10.03** · derived · inventories Genesis Checkpoint G9 (2026.10.02) and Theory of Operation revision 13 against
all 72 Playbook subcategories · regenerates `topak-playbook-delta-inventory-2026.09.12.md`, which it supersedes as
basis · the row marks are Table 1 of `topak-critical-review-2026.10.02.md`, re-marked there against G9 and carried
here unchanged, with the 09.12 mark beside each · prepared by Claude at the custodian's request

**Why regenerated now.** The 09.12 inventory has been "due for regeneration" in every Theory of Operation since revision
7 (CR-35), and the 10.02 review did the re-marking as a table inside a review. This document is that table as the
standing inventory, in the 09.12 inventory's form, so that `topak-feature-list-2026.10.03.md` and the next review can
cite one artifact. Nothing here is ratified; a mark is a reading of the records, not a claim in one.

**The Playbook as read.** The AI RMF 1.0 Playbook, 72 subcategories under 19 categories, read from NIST's structured
JSON export as mirrored on 2026.10.02 (the 10.02 review's §4 says why the mirror and what it checked); outcome text is
the AI RMF Core's wording, abridged, where the Playbook's export drifts from it.

**Basis for "matched."** As on 09.12: a subcategory is **M** only where a ratified record or a named mechanism at G9
discharges the outcome. Intent, adjacency and pending texts do not count. A record that is Accepted but
confirmation-required counts, and the mark is read as author-ratified (ToO §0).

**Status key**

| Mark | Meaning |
|---|---|
| **M** | Matched — mechanism or record exists and discharges the outcome |
| **P** | Partial — mechanism exists, outcome only half discharged |
| **C** | Convertible — mechanism exists in TOPAK, never claimed against the row; cost is a sentence |
| **G** | Gap — TOPAK's own safety argument needs this and does not have it |
| **X** | Out of scope — legitimately absent, discharged by a scope declaration |
| **!** | Contradiction — a ratified record conflicts with a named suggested action |

**Tally at G9: M 11 · P 24 · C 4 · G 5 · X 28 · ! 0** (72). The 09.12 inventory's corrected tally was M 6 · P 12 ·
C 15 · G 9 · X 30 · ! 1. Nineteen rows moved; §5 lists them. The one contradiction is gone. The five gaps left are the
five the corpus names on its own open list.

| Function | Rows | M | P | C | G | X | ! |
|---|---|---|---|---|---|---|---|
| GOVERN | 19 | 3 | 8 | 1 | 0 | 7 | — |
| MAP | 18 | 4 | 3 | 1 | 1 | 9 | — |
| MEASURE | 22 | 2 | 6 | 1 | 3 | 10 | — |
| MANAGE | 13 | 2 | 7 | 1 | 1 | 2 | — |
| **Total** | **72** | **11** | **24** | **4** | **5** | **28** | **0** |

---

## 1. GOVERN (19)

| # | Outcome (Core wording, abridged) | 09.12 | G9 | Note |
|---|---|---|---|---|
| 1.1 | Legal and regulatory requirements understood, managed, documented | X | X | Unchanged. The forensic floor retains identifiers of human principals with no legal-basis line per class (CR-11, still open) |
| 1.2 | Trustworthy-AI characteristics integrated into policy | C | **C** | Still never mapped to the seven characteristics; TACIP's Table 2 regrouping would be the cheaper target |
| 1.3 | Risk-management activity scaled to risk tolerance | C | P | ADR-0023's declaration schema and ADR-0045's rows are the instrument; no deployment declaration has been written (G9 item 64) |
| 1.4 | Transparent policies, procedures, controls, documentation | M | **M** | The record corpus |
| 1.5 | Ongoing monitoring and periodic review of the risk process; roles; frequency | P | P | Nine checkpoints in seventeen days is a review cadence; the only role is the custodian's |
| 1.6 | Inventory of AI systems, resourced by priority | C | P | The lease registry is a live inventory of principals; Personas are pinned; the reference has no inventory of *systems* |
| 1.7 | Decommissioning safely | P | P | A principal: revocation, fence, expiry, break-glass lapse. A system: re-genesis migration open (item 10); TACIP P13 is the better rubric |
| 2.1 | Roles, responsibilities, separation of development from testing | M | **M** | Seats, cells, recusal, fault-domain placement (ADR-0037, 0038) |
| 2.2 | Personnel and partner training | X | X | — |
| 2.3 | Executive leadership accountable for AI risk decisions | G | P | Custody declared (1, 0); key-holders and approvers are trusted-base rows (T-0045-9, 12); no organizational role named |
| 3.1 | Decisions informed by a diverse team | X | X | One person and one assistant. Marked X as organizational; the evidential consequence is MEASURE 1.3 |
| 3.2 | Roles for human-AI configurations and oversight | M | **M** | See above |
| 4.1 | Critical-thinking, safety-first culture | X | X | — |
| 4.2 | Teams document risks and impacts; communicate broadly | C | P | ADR-0045 enumerates the base; the residual-risk statement is unwritten; nothing is communicated outside the repository |
| 4.3 | Enable testing, incident identification, information sharing | P | P | `SECURITY.md` defines a safety finding and a private route; replay and recorded denials identify; external sharing absent |
| 5.1 | External feedback collected and integrated | X | X | — |
| 5.2 | Adjudicated feedback incorporated | X | X | — |
| 6.1 | Third-party risk policies, including IP | X | X | Model licensing, corpus licensing untouched |
| 6.2 | Contingency for third-party failure | G | P | An unavailable model or Observer now stalls by mechanism (ADR-0039) rather than being unmodeled; the "army of one" degraded mode of 09.10 is still unfiled |

## 2. MAP (18)

| # | Outcome (Core wording, abridged) | 09.12 | G9 | Note |
|---|---|---|---|---|
| 1.1 | Intended purpose, context, settings | X | X | ToO §13's assumptions of use cover the limitations half |
| 1.2 | Interdisciplinary, diverse actors | X | X | — |
| 1.3 | Mission and goals | X | X | — |
| 1.4 | Business value | X | X | — |
| 1.5 | Risk tolerances documented | C | P | Same instrument and same blocker as GOVERN 1.3 |
| 1.6 | System requirements elicited; socio-technical design decisions | C | **M** | Fifteen proved, mutation-tested TLA+ modules are requirements artifacts of the kind the Playbook's example only gestures at |
| 2.1 | Task and methods defined | X | X | — |
| 2.2 | Knowledge limits; how output is overseen | P | P | Havoc as a deliberate substitution is now stated (ToO §2.3); oversight documented; assessed, no |
| 2.3 | Scientific integrity and TEVV considerations | G | **M** | ADR-0046; drivers and digests; one corroboration in §1 |
| 3.1 | Benefits documented | X | X | — |
| 3.2 | Costs, including non-monetary | C | **C** | The capability cost (no shell) is stated; the durability cost (a crashed round loses its work) is not (10.01 assessment §7); no adoption-cost table |
| 3.3 | Targeted application scope specified | M | **M** | Both alphabets typed since ADR-0040 |
| 3.4 | Operator and practitioner proficiency | G | **G** | A5 presumes it; nothing defines it |
| 3.5 | Human-oversight processes defined, assessed, documented | P | P | Defined and documented; assessment needs `L` and an Observer that exists |
| 4.1 | Third-party legal and IP mapping | X | X | — |
| 4.2 | Internal risk controls per component, incl. third-party | C | **M** | ADR-0045 Annex A and B: one row per component, class, residual, and the theorems that rest on it |
| 5.1 | Likelihood and magnitude of impacts | X | X | — |
| 5.2 | Engagement with AI actors | X | X | — |

## 3. MEASURE (22)

| # | Outcome (Core wording, abridged) | 09.12 | G9 | Note |
|---|---|---|---|---|
| 1.1 | Metrics selected; **unmeasured risks documented** | C | P | ToO §12 and §13 list what is not measured; it is not written as the non-measurement declaration the row accommodates |
| 1.2 | Metrics reassessed | X | X | — |
| 1.3 | Independent assessors | P | **G** | Zero. The 09.12 P credited the Observer; it does not exist |
| 2.1 | TEVV tooling documented | C | **M** | See above |
| 2.2 | Human-subject evaluation | X | X | — |
| 2.3 | Assurance criteria under deployment-like conditions | P | P | The compose rig exists; the smoke run has not been repeated since 09.25 (item 52) |
| 2.4 | Production monitoring | P | P | Liveness coupled; detection function absent |
| 2.5 | Validity, reliability, generalizability | X | X | — |
| 2.6 | Safety; **fails safely**; residual within tolerance | C | P | Every refusal path exercised and recorded; residual risk unstated (MANAGE 1.4) |
| 2.7 | Security and resilience evaluated | C | P | Mutation discipline and negative controls are the structural evaluation; time-to-bypass unmeasured; no adversarial exercise has been run |
| 2.8 | Transparency and accountability risks | C | **M** | Attribution guarantee; confirmation markers; the debt ledger |
| 2.9 | Model explained, validated | X | X | Declared out by havoc, in writing |
| 2.10 | Privacy risk | C | **C** | Erasure machinery without a privacy framing, unchanged |
| 2.11 | Fairness and bias | X | X | — |
| 2.12 | Environmental impact | X | X | — |
| 2.13 | **Effectiveness of TEVV** | G | **G** | Floor fitness, unowned (item 2) |
| 3.1 | Track unanticipated and emergent risks | X | P | Every checkpoint's "results the drafting did not anticipate" is this, for the corpus |
| 3.2 | Tracking where metrics are unavailable | G | **G** | `L`; placeholders (CR-36) |
| 3.3 | End-user feedback and appeal | X | X | — |
| 4.1 | Measurement connected to context | X | X | — |
| 4.2 | Results validated by domain experts | X | X | — |
| 4.3 | Improvements or declines from field data | X | X | — |

## 4. MANAGE (13)

| # | Outcome (Core wording, abridged) | 09.12 | G9 | Note |
|---|---|---|---|---|
| 1.1 | Determination that the system achieves purpose; proceed or not | P | P | Promotion is a containment gate, not a purpose gate; now stated in the record's consequences |
| 1.2 | Treatment prioritized | X | P | The 09.28 prioritization is this, for the corpus |
| 1.3 | Documented responses to high-priority risks | P | P | Against design forks, not a mapped risk register |
| 1.4 | **Residual risk documented for acquirers and users** | G | **G** | Unwritten (see above) |
| 2.1 | Resources; non-AI alternatives | C | **C** | Unchanged |
| 2.2 | Sustain value | X | X | — |
| 2.3 | Respond to and recover from an unknown risk | M | **M** | Default deny; quarantine; fence; targeted revocation; replay |
| 2.4 | Supersede, disengage, deactivate | M ! | **M** | The contradiction is gone: ADR-0003 and ADR-0028 say legibility, not shredding, and NC-2 is proved |
| 3.1 | Third-party risks monitored, controls documented | G | P | Monoculture is now one pair per cell (ADR-0037); third-party components are rows (Cedar, Kafka, OPA, TLC, tlapm); no monitoring |
| 3.2 | Pre-trained models monitored | G | P | The Persona pins weights, prompt and decoder; lineage is projected from the log (ADR-0035, Proposed); behaviour is not monitored, by design |
| 4.1 | Post-deployment monitoring, appeal, override, decommissioning, incident response, change management | P | P | Override, incident response and change management map; appeal and user input do not |
| 4.2 | Continual improvement with interested parties | X | X | — |
| 4.3 | Incidents communicated; tracking documented | P | P | Tracking: a model answer. Communication: none |

---

## 5. What moved since 09.12, and why

Nineteen rows changed mark. Every move is to a record or a mechanism that did not exist on 09.12; none is a re-reading
of the same evidence.

| Row | 09.12 → G9 | What moved it |
|---|---|---|
| GOVERN 1.3 | C → P | ADR-0023's declaration schema and ADR-0045's rows exist; no deployment declaration is written (G9 item 64), so P and not M |
| GOVERN 1.6 | C → P | The lease registry is a live inventory of principals and Personas are pinned (ADR-0016, ADR-0031); systems are not inventoried |
| GOVERN 2.3 | G → P | Custody declared (1, 0); key-holders and approvers are trusted-base rows (ADR-0045 T-0045-9, 12); no organizational role is named |
| GOVERN 4.2 | C → P | ADR-0045 enumerates the trusted base; the residual-risk statement now exists as a derived document (`topak-residual-risk-statement-2026.10.03.md`); nothing is communicated outside the repository |
| GOVERN 6.2 | G → P | An unavailable model or Observer stalls by mechanism (ADR-0039); the "army of one" degraded mode is still unfiled |
| MAP 1.5 | C → P | Same instrument and blocker as GOVERN 1.3 |
| MAP 1.6 | C → M | Fifteen proved, mutation-tested TLA+ modules (ADR-0046) are requirements artifacts of the kind the row asks for |
| MAP 2.3 | G → M | ADR-0046 declares TLC versus TLAPS; drivers and digests make corroboration possible; one corroboration ran (the 10.02 review §1) |
| MAP 4.2 | C → M | ADR-0045 Annex A and B: one row per component with class, residual and the theorems that rest on it |
| MEASURE 1.1 | C → P | ToO §12 and §13 list what is not measured; the non-measurement declaration is now §4 of the residual-risk statement |
| MEASURE 1.3 | P → G | **Down**: the 09.12 P credited the Observer as a mechanical assessor; it is an e2e fixture, and no human assessor exists |
| MEASURE 2.1 | C → M | `spec/README.md`, `spec/proof-method.md`, every results-file header with tool digests, `mechanism/GAPS-AND-ASSUMPTIONS.md` §6 |
| MEASURE 2.6 | C → P | Every refusal path exercised and recorded; residual risk now stated (MANAGE 1.4), tolerance still the deployment's |
| MEASURE 2.7 | C → P | Mutation discipline and negative controls are a structural evaluation; time-to-bypass unmeasured, no adversarial exercise run |
| MEASURE 2.8 | C → M | The attribution guarantee (ADR-0031), confirmation markers and the debt ledger |
| MEASURE 3.1 | X → P | Every checkpoint's "results the drafting did not anticipate" tracks emergent findings, for the corpus |
| MANAGE 1.2 | X → P | The 09.28 prioritization is a treatment ordering, for the corpus |
| MANAGE 2.4 | M ! → M | The contradiction is gone: ADR-0003 and ADR-0028 say legibility, not shredding; NC-2 is proved (`NonComposition_proof.tla`) |
| MANAGE 3.1 | G → P | Monoculture is one pair per cell (ADR-0037); third-party components are trusted-base rows; no monitoring |
| MANAGE 3.2 | G → P | The Persona pins weights, prompt and decoder (ADR-0016); lineage is projected from the log (ADR-0035, Proposed); behaviour is not monitored, by design |

---

## 6. The five gaps (G)

TOPAK's own argument needs each of these and does not have it. All five are on G9's open list under their own names.

| Row | Unaddressed practice | Why it cannot be scoped away | Where it sits |
|---|---|---|---|
| **MAP 3.4** | Operator and practitioner proficiency defined and assessed | ToO A5 presumes a trained, authorized human for break-glass, quarantine release and `D`; nothing defines or assesses one | No record; the deployment declaration would carry it |
| **MEASURE 1.3** | Independent assessors | Zero. Every record, proof and run is the author's; ADR-0029 A2 makes a review a bootstrap precondition and none is engaged | `checkpoints/README.md`, the A2.5 line; CR-28 |
| **MEASURE 2.13** | Effectiveness of TEVV processes themselves | Moon & Varshney §4.6 and Appendix B: a vacuous specification passes all three gates; the fourth gate, floor fitness, is unowned since G1 | G9 item 2 |
| **MEASURE 3.2** | Risk tracking where metrics are unavailable | `L` is unmeasured; `T_obs`, `K`, `R` are placeholders; the `slm/` rig could measure two of them today | G9 item 47; CR-36 |
| **MANAGE 1.4** | Residual risk documented for acquirers and users | **Discharged as a document on 2026.10.03** (`topak-residual-risk-statement-2026.10.03.md`); the mark moves to P at the next re-marking, since the numbers in it are undeclared | CR-35 |

## 7. The four convertible rows (C)

Each is a sentence or a table the corpus could write without a design decision.

| Row | What exists | What is missing |
|---|---|---|
| GOVERN 1.2 | Four of the seven trustworthy-AI characteristics touched, three disclaimed by havoc | A mapping to the seven, or to TACIP's Table 2 regrouping |
| MAP 3.2 | The capability cost (no shell) stated in ADR-0022; the durability cost (a crashed round loses its work) found by the 10.01 assessment | An adoption-cost table per component (the 09.10 session's, never filed) |
| MEASURE 2.10 | Erasure as a modeled event (ADR-0006), topic-per-round as the unit of erasure (ADR-0003), the plaintext store (ADR-0004) | A privacy framing of machinery built for deletion |
| MANAGE 2.1 | The hierarchy-of-needs drop order and control-plane cost model (09.10 and 09.11 sessions) | Filing them; a non-AI alternatives paragraph |

## 8. The twenty-four partial rows: the unaddressed half

| Row | Addressed | Not addressed |
|---|---|---|
| GOVERN 1.3, MAP 1.5 | The instrument: ADR-0023 §6 and ADR-0045 §1 | A written deployment declaration (G9 item 64) |
| GOVERN 1.5 | Nine checkpoints in seventeen days as a review cadence | A role other than the custodian's; review of the process itself |
| GOVERN 1.6 | Principals and Personas | Systems |
| GOVERN 1.7 | A principal: revocation, fence, expiry, break-glass lapse | A system: re-genesis migration (G9 item 10) |
| GOVERN 2.3 | Custody and approver rows | An organizational role |
| GOVERN 4.2 | ADR-0045; the residual-risk statement | Communication outside the repository |
| GOVERN 4.3 | `SECURITY.md`; replay and recorded denials | External sharing |
| GOVERN 6.2 | Stall by mechanism | The degraded mode, unfiled |
| MAP 2.2 | Havoc as the substitution, stated | Assessment |
| MAP 3.5 | Oversight defined and documented | Assessed: needs `L` and an Observer that exists |
| MEASURE 1.1 | The non-measurement declaration (residual-risk statement §4) | A metrics program |
| MEASURE 2.3 | The compose rig | A smoke run since 09.25 (G9 item 52) |
| MEASURE 2.4 | Liveness coupled | A detection function (item 43) |
| MEASURE 2.6 | Every refusal path exercised; residual stated | A declared tolerance |
| MEASURE 2.7 | Mutation discipline and negative controls | Time-to-bypass; an adversarial exercise |
| MEASURE 3.1 | The checkpoints' unanticipated-results sections | Tracking for a deployment rather than the corpus |
| MANAGE 1.1 | A containment gate | A purpose gate |
| MANAGE 1.2 | The 09.28 prioritization | A treatment plan for a deployment |
| MANAGE 1.3 | Responses to design forks | A mapped risk register |
| MANAGE 3.1 | One pair per cell; components as rows | Monitoring |
| MANAGE 3.2 | Pins and lineage projection | Behaviour monitoring (declined by design) |
| MANAGE 4.1 | Override, incident response, change management | Appeal; user input |
| MANAGE 4.3 | Tracking, a model answer | Communication to affected communities |

## 9. Out of scope (X), by group (28)

Legitimately absent; each still needs a scope declaration, and ToO §13 is where most would land.

| Group | Subcategories |
|---|---|
| Legal, regulatory, third-party IP | GOVERN 1.1, 6.1 · MAP 4.1 |
| Organizational culture, training, diversity | GOVERN 2.2, 3.1, 4.1 · MAP 1.2 |
| External stakeholder feedback | GOVERN 5.1, 5.2 · MEASURE 3.3 · MANAGE 4.2 |
| Mission, purpose, value, benefits | MAP 1.1, 1.3, 1.4, 2.1, 3.1 |
| Impact likelihood and stakeholder engagement | MAP 5.1, 5.2 |
| Metrics program lifecycle | MEASURE 1.2, 4.1, 4.2, 4.3 |
| Model- and content-level evaluation, disclaimed by havoc | MEASURE 2.2, 2.5, 2.9, 2.11 |
| Environmental impact | MEASURE 2.12 |
| Value sustainment | MANAGE 2.2 |

GOVERN 3.1 is marked X as organizational; its evidential consequence is MEASURE 1.3, which is a G.

## 10. Reverse deltas: TOPAK constructs with no Playbook home

The 09.12 list stands, and two entries are sharper at G9.

| TOPAK construct | Why the Playbook has no row for it |
|---|---|
| **Passive e-stop**: lease expiry as default deny | Every MANAGE 2.4 suggestion presumes an actor who decides to act; the Playbook has no vocabulary for a control that operates when nobody acts. Still the single construct the Critical Infrastructure profile has no word for (10.02 review §3) |
| **Monotonicity as one principle across layers** | Consensus for grants and local for denials (ADR-0031 §5); bundles only subtract (ADR-0030); rungs are subtractions from an archetype (ADR-0023); the trusted base admits a component only if its failure can only subtract (ADR-0045 §2). The Playbook treats controls as additive |
| **Floor refinement at promotion time** | A mechanically decidable admissibility check on policy change, with routing and a proof checker behind it (ADR-0030 §5 A1) |
| **Evictability as the principal test** | GOVERN 3.2 asks for configurations and offers no test for the line between principal and gate (ADR-0002) |
| **HOOTL as a distinct state** | "No action was expressible", not "nobody acted" |
| **`Contained` versus `Mediated`** | Effect exclusivity as a per-principal predicate; humans never `Contained`; the lookup names each failing conjunct (ADR-0034 §4) |
| **Build as the hostile domain** | The Byzantine threat lives in the pipeline; a human signing a green pipeline is the documented failure (ADR-0002) |
| **A computed theorem inventory** | `spec/inventory.py` says which guarantees are void for a declared trusted base: a stronger form than any self-attestation the Playbook or TACIP 6.1.5 asks for (new since 10.02) |

## 11. What to do with this, in order

1. ~~MANAGE 1.4 residual-risk statement.~~ Written 2026.10.03; its numbers are the deployment's to fill in.
2. ~~MEASURE 1.1 non-measurement declaration.~~ §4 of the same document.
3. **MEASURE 1.3.** Engage a reviewer. Nothing else on this list moves three grades.
4. **MEASURE 2.13, MEASURE 3.2, MAP 3.4.** One is design work with no owner since G1 (floor fitness); one is a
   measurement the rehearsal rig can run; one is a declaration.
5. **The four C rows**, as one mapping appendix.
6. **The reverse deltas** into the position paper, with the computed inventory added.
