# TOPAK — External Alignment at G11: the NIST AI RMF Playbook, TACIP, Moon & Varshney, and IBM's MCP guide

**2026.10.09** · derived · inventories Genesis Checkpoint G11 (2026.10.09, `ce8f460`) and Theory of Operation
revision 15 against all 72 Playbook subcategories, the TACIP discussion draft of 2026.09.13(b), Moon & Varshney
arXiv:2605.09045v2, and IBM's *Architecting secure enterprise AI agents with MCP* (October 2025) · read at the tree
after `3e34d67` · regenerates `topak-playbook-delta-inventory-2026.10.03.md`, which it supersedes as basis for the
Playbook marks, and updates Part II of `topak-external-and-competitive-assessment-2026.10.05.md` (§7, §8.1, §8.2),
which stands for everything else · prepared by Claude at the custodian's request

**Sources, by digest.** The Playbook from the structured JSON export the custodian supplied (`aecbee3d3c882081…`, 72
entries, the key set the 10.02 review's §4 describes); TACIP 09.13(b) (`1a37852f316e819e…`, the same bytes the 10.02
review read); Moon & Varshney v2 (`06e699209e2bd6ba…`, the same bytes the 10.02 review and the 10.05 assessment
read); the IBM guide (`65ea5d824c221334…`, 24 pages, new to the corpus). The TACIP 09.28(a) draft the 10.05
assessment read is one draft later than the one read here; §2 says where that matters.

**Why now.** The 10.03 inventory marked G9. The 10.05 assessment read twelve rows against G10 and said "the next
inventory should carry it." G11 has since added a second deductive method (ADR-0053), recorded two known unsound
cases in the prover (ADR-0046 A2), checked liveness for the first time, and built workflows under two Proposed
records. Every mark below is read against G11 §1 to §8; where G11 and the narrative disagree, G11 wins. Nothing here
is ratified; a mark is a reading of the records, not a claim in one.

**Basis for "matched"**, as on 09.12 and 10.03: a subcategory is **M** only where a ratified record or a named
mechanism at G11 discharges the outcome. Intent, adjacency, Proposed records and pending amendments do not count. A
record that is Accepted but confirmation-required counts, and the mark is read as author-ratified (ToO §0, A8). A
record that is Accepted and **provisional** (ADR-0050, ADR-0052) counts, and the mark says so (A17).

**Status key**

| Mark | Meaning |
|---|---|
| **M** | Matched — mechanism or record exists and discharges the outcome |
| **P** | Partial — mechanism exists, outcome only half discharged |
| **C** | Convertible — mechanism exists in TOPAK, never claimed against the row; cost is a sentence |
| **G** | Gap — TOPAK's own safety argument needs this and does not have it |
| **X** | Out of scope — legitimately absent, discharged by a scope declaration |
| **!** | Contradiction — a ratified record conflicts with a named suggested action |

---

# Part I — The Playbook at G11

**Tally at G11: M 11 · P 27 · C 3 · G 3 · X 28 · ! 0** (72). At G9 it was M 11 · P 24 · C 4 · G 5 · X 28. Three
rows moved, all up, and each to a document or a record that did not exist on 10.02: GOVERN 1.2 (C → P), MEASURE 2.13
(G → P) and MANAGE 1.4 (G → P). No row moved down. Eleven rows kept their mark and gained evidence; §1.5 lists them.
The twelve-row reading the 10.05 assessment made against G10 is confirmed at G11 in every direction it named.

| Function | Rows | M | P | C | G | X | ! |
|---|---|---|---|---|---|---|---|
| GOVERN | 19 | 3 | 9 | 0 | 0 | 7 | — |
| MAP | 18 | 4 | 3 | 1 | 1 | 9 | — |
| MEASURE | 22 | 2 | 7 | 1 | 2 | 10 | — |
| MANAGE | 13 | 2 | 8 | 1 | 0 | 2 | — |
| **Total** | **72** | **11** | **27** | **3** | **3** | **28** | **0** |

## 1.1 GOVERN (19)

| # | Outcome (Core wording, abridged) | G9 | G11 | Note |
|---|---|---|---|---|
| 1.1 | Legal and regulatory requirements understood, managed, documented | X | X | Unchanged. CR-11 (no legal-basis line per forensic class) still open |
| 1.2 | Trustworthy-AI characteristics integrated into policy | C | **P** | **Moved.** `narrative/architecture-description.md` §10.1 places every quality goal under TACIP Table 2's thirteen characteristics, with TOPAK's position on each and where the evidence is; its Appendix B item 4 asks the custodian whether that is the mapping this row wants. A draft narrative, not a record, and it maps goals, not policies: P |
| 1.3 | Risk-management activity scaled to risk tolerance | P | P | The instrument (ADR-0023 §6, ADR-0045 §1, `spec/inventory.py`) is in force; "no deployment declaration has been written" (G11 §8) |
| 1.4 | Transparent policies, procedures, controls, documentation | M | **M** | The record corpus; since G10 also `REVIEWERS_GUIDE_README.md` (draft, unmeasured) |
| 1.5 | Ongoing monitoring and periodic review of the risk process; roles; frequency | P | P | Eleven checkpoints in twenty-four days is a cadence; the only role is the custodian's; the process's own criterion for assisted drafting is still open (G11 item 66) |
| 1.6 | Inventory of AI systems, resourced by priority | P | P | Principals, Personas and now promoted workflow graphs are inventoried by the mechanism (ADR-0054 §2, Proposed); systems are not |
| 1.7 | Decommissioning safely | P | P | A principal: revocation, fence, expiry, and since ADR-0052 an emergency seating that ends with its round. A system: re-genesis migration still open (item 10) |
| 2.1 | Roles, responsibilities, separation of development from testing | M | **M** | Seats, cells, recusal (ADR-0024 §5, ADR-0037); since G10 operators are principals who observe each other, "a person who operates and also votes is two principals" (ADR-0050, **provisional**) |
| 2.2 | Personnel and partner training | X | X | — |
| 2.3 | Executive leadership accountable for AI risk decisions | P | P | Custody declared (1, 0); approvers and key-holders are rows; no organizational role is named |
| 3.1 | Decisions informed by a diverse team | X | X | One person and one assistant; the evidential consequence is MEASURE 1.3 |
| 3.2 | Roles for human-AI configurations and oversight | M | **M** | As above, plus the `operator` and `emergency` seat kinds (ADR-0050, ADR-0052, provisional) and HITL/HOTL/HOOTL as `ENABLED` predicates |
| 4.1 | Critical-thinking, safety-first culture | X | X | — |
| 4.2 | Teams document risks and impacts; communicate broadly | P | P | ADR-0045's thirty-seven rows and the residual-risk statement exist; **the statement is stale against G11** (§1.6 below); nothing is communicated outside the repository |
| 4.3 | Enable testing, incident identification, information sharing | P | P | `SECURITY.md`; the prover's two unsound cases were found by the corpus's own review runs and recorded (ADR-0046 A2), which is incident identification working. **They were not reported upstream, by the custodian's decision** (G11 item 104): the one information-sharing event the corpus has had went the other way |
| 5.1 | External feedback collected and integrated | X | X | — |
| 5.2 | Adjudicated feedback incorporated | X | X | — |
| 6.1 | Third-party risk policies, including IP | X | X | `NOTICE` and `LICENSE-DOCS` settle the corpus's own licensing; no third-party risk policy |
| 6.2 | Contingency for third-party failure | P | P | A domain without a live operator stalls until a quorum seats one (ADR-0050); a defective prover was kept in use under a rule and a scan rather than replaced (ADR-0046 A2), a contingency exercised once; the "army of one" degraded mode is still unfiled |

## 1.2 MAP (18)

| # | Outcome (Core wording, abridged) | G9 | G11 | Note |
|---|---|---|---|---|
| 1.1 | Intended purpose, context, settings | X | X | ToO §13 (A1 to A18) covers the limitations half; `architecture-description.md` §3 carries an "out of scope by position" line |
| 1.2 | Interdisciplinary, diverse actors | X | X | — |
| 1.3 | Mission and goals | X | X | — |
| 1.4 | Business value | X | X | — |
| 1.5 | Risk tolerances documented | P | P | Same instrument and blocker as GOVERN 1.3 |
| 1.6 | System requirements elicited; socio-technical design decisions | M | **M** | Twenty-four proof modules, 5,416 obligations, fifteen re-proved in Lean; `Workflow.tla` and `Mesh.tla` TLC-only under Proposed records |
| 2.1 | Task and methods defined | X | X | — |
| 2.2 | Knowledge limits; how output is overseen | P | P | Havoc as the deliberate substitution (ToO §2.3); oversight documented; assessed, no |
| 2.3 | Scientific integrity and TEVV considerations | M | **M** | ADR-0046 declares what TLC checks and what TLAPS proves; since Batch 37 it also declares what the prover is known to get wrong (A2), and G11 §8 says "a certified proof is not a verified one." The mark holds on the candour, not despite it |
| 3.1 | Benefits documented | X | X | — |
| 3.2 | Costs, including non-monetary | C | **C** | The capability cost stated; the durability cost (a crashed round loses its work) still unstated (10.05 open item) |
| 3.3 | Targeted application scope specified | M | **M** | Both alphabets typed; a fourth Run variant, `Route`, is pending on ADR-0054 and not in force |
| 3.4 | Operator and practitioner proficiency | G | **G** | Unchanged. An operator is a principal with a key, a Persona and a provider (ADR-0050), and nothing about skill; A5 presumes a trained person |
| 3.5 | Human-oversight processes defined, assessed, documented | P | P | Defined and documented; `Emergency_live` proves an emergency call cannot be blocked by an Observer; `L` unmeasured and no Observer exists to measure it |
| 4.1 | Third-party legal and IP mapping | X | X | — |
| 4.2 | Internal risk controls per component, incl. third-party | M | **M** | Thirty-seven rows; T-0045-37 added; T-0045-31's residual names its two defects. This is the row's outcome done to the letter |
| 5.1 | Likelihood and magnitude of impacts | X | X | The residual-risk statement orders residuals by severity for the corpus; impacts on people are outside the premise |
| 5.2 | Engagement with AI actors | X | X | — |

## 1.3 MEASURE (22)

| # | Outcome (Core wording, abridged) | G9 | G11 | Note |
|---|---|---|---|---|
| 1.1 | Metrics selected; **unmeasured risks documented** | P | P | The non-measurement declaration is §4 of the residual-risk statement, stale on two rows (floor fitness now owned; the correlator's function drafted) and missing the workflow placeholders `T_wf`, the step bound and `N` (G11 item 101) |
| 1.2 | Metrics reassessed | X | X | — |
| 1.3 | Independent assessors | G | **G** | **Larger.** Twenty-nine confirmation-required records; "every text ratified since G10 is the drafter's" (G11 §1.2); reviewer engaged: none. A reviewer's guide now exists, which is a means and not a reviewer |
| 2.1 | TEVV tooling documented | M | **M** | Plus `spec/proof-certification.md` §8 to §12, `proof-scan.sh`, the Lean results files with their digests, `lean-sync.sh`, the graph checks and the deadlock audit |
| 2.2 | Human-subject evaluation | X | X | — |
| 2.3 | Assurance criteria under deployment-like conditions | P | P | The compose rig and 155 tests; the live smoke run still not repeated since 09.25 |
| 2.4 | Production monitoring | P | P | Liveness coupled and, since G11, the coupling stall shown to end (TLC); the detection function is ADR-0051, Proposed; no Observer is built |
| 2.5 | Validity, reliability, generalizability | X | X | — |
| 2.6 | Safety; **fails safely**; residual within tolerance | P | P | Every refusal path exercised; "fails safely" now has liveness evidence beside safety (`Coupling_live`, `Emergency_live`); residual stated and stale; the tolerance is still the deployment's |
| 2.7 | Security and resilience evaluated | P | P | Mutation discipline, negative controls, and now the review runs that found the prover's defects and the custodian's three mutations at Batch 36. Time-to-bypass unmeasured; no adversarial exercise against the system has been run; nothing shared with incident databases |
| 2.8 | Transparency and accountability risks | M | **M** | Attribution guarantee; confirmation markers; the debt ledger; the A2.5 line now carried in the checkpoint itself |
| 2.9 | Model explained, validated | X | X | Declared out by havoc |
| 2.10 | Privacy risk | C | **C** | Unchanged: erasure machinery, no privacy framing |
| 2.11 | Fairness and bias | X | X | — |
| 2.12 | Environmental impact | X | X | — |
| 2.13 | **Effectiveness of TEVV** | G | **P** | **Moved.** The row asks that the effectiveness of the TEVV processes themselves be evaluated and documented. Batch 37 did exactly that for one process: the prover was found to prove `FALSE` in two ways, the finding was recorded against its row (ADR-0045 A3), a rule and a scan were adopted (`proof-certification.md` §10, §12), and a second method was added (ADR-0053). The other half is unchanged: floor fitness is owned (ADR-0029 A4, ADR-0030 A3) and nothing names what the test is (item 87). P, with the floor-fitness half carried in §1.7 as the debt it was |
| 3.1 | Track unanticipated and emergent risks | P | P | G11 §3 lists twelve "results the drafting did not anticipate"; for the corpus, not a deployment |
| 3.2 | Tracking where metrics are unavailable | G | **G** | **Larger.** `L`, `T_obs`, `K`, `R`, `T_persona` as before; `T_wf`, the step bound and `N` added by the workflow records; "the values are placeholders" (G11 §8) |
| 3.3 | End-user feedback and appeal | X | X | — |
| 4.1 | Measurement connected to context | X | X | — |
| 4.2 | Results validated by domain experts | X | X | — |
| 4.3 | Improvements or declines from field data | X | X | — |

## 1.4 MANAGE (13)

| # | Outcome (Core wording, abridged) | G9 | G11 | Note |
|---|---|---|---|---|
| 1.1 | Determination that the system achieves purpose; proceed or not | P | P | Promotion is a containment gate, not a purpose gate; a workflow's promotion seats every cell and votes the budget (ADR-0054, ADR-0055, Proposed) |
| 1.2 | Treatment prioritized | P | P | The 09.28 prioritization and now the liveness plan's tiers (`topak-liveness-2026.10.07.md`); for the corpus |
| 1.3 | Documented responses to high-priority risks | P | P | G11 §7's open list names where each item sits; against design forks, not a mapped risk register |
| 1.4 | **Residual risk documented for acquirers and users** | G | **P** | **Moved**, as the 10.03 inventory said it would. `topak-residual-risk-statement-2026.10.03.md` exists and its numbers are undeclared; it is also stale against G11 (§1.6). P until a statement is written against the current checkpoint with a deployment's numbers in it |
| 2.1 | Resources; non-AI alternatives | C | **C** | Unchanged |
| 2.2 | Sustain value | X | X | — |
| 2.3 | Respond to and recover from an unknown risk | M | **M** | Default deny, quarantine, fence, targeted revocation, replay; and now a precedent: an unknown defect in a trust root met with a rule, a scan, three errata and a second method within two days |
| 2.4 | Supersede, disengage, deactivate | M | **M** | Strengthened in both directions CR-29 named: `EmergencyNeverCoupled` and `EmergencyCallsWithoutObserver` are proved, so the emergency path no longer waits on a dead Observer; R8 is withdrawn and a break-glass grant ends with its round, so it is no longer time-unbounded. Both rest on ADR-0052, **provisional**, with "no settled form" (G11 §8) |
| 3.1 | Third-party risks monitored, controls documented | P | P | Components are rows; a third-party component (`tlapm` 7824dab) was found defective and the control documented against its row; a second toolchain (Lean 4.33.1) and cedar-spec v4.13.0 are new rows. No monitoring program; the defects unreported to the third party |
| 3.2 | Pre-trained models monitored | P | P | Pins and lineage projection; ADR-0035 gained R8 (a workflow's tally needs independent Thinkers at the ends of every clear edge) and is still Proposed; behaviour not monitored, by design |
| 4.1 | Post-deployment monitoring, appeal, override, decommissioning, incident response, change management | P | P | Override, incident response and change management map; appeal and user input do not |
| 4.2 | Continual improvement with interested parties | X | X | — |
| 4.3 | Incidents communicated; tracking documented | P | P | Tracking: `checkpoints/README.md`'s errata table, G11 §3's unanticipated results, and the ADR History rows are the database the row asks for. Communication: the prover's defects are the first error the corpus found in someone else's component, and they are not communicated (item 104) |

## 1.5 What moved since G9, and what gained evidence without moving

| Row | G9 → G11 | What moved it |
|---|---|---|
| GOVERN 1.2 | C → P | `architecture-description.md` §10.1: goals placed under TACIP's Table 2 characteristics, a draft the custodian has not settled (its Appendix B item 4) |
| MEASURE 2.13 | G → P | ADR-0046 A2 and ADR-0045 A3: a TEVV process evaluated, found defective, and the finding documented with a rule, a scan and a second method; floor fitness still untested |
| MANAGE 1.4 | G → P | The residual-risk statement of 2026.10.03, with undeclared numbers, now stale against G11 |

**Kept their mark and gained evidence** (the 10.05 §8.1 reading, confirmed, with G11's additions): GOVERN 1.7
(the emergency seating ends with its round), GOVERN 2.1 and 3.2 (operators as principals, provisional), MAP 1.6 and
MEASURE 2.1 (the Lean route and its checks), MAP 2.3 (the prover's defects declared), MAP 4.2 (thirty-seven rows),
MEASURE 2.4 and 2.6 (the coupling stall shown to end), MEASURE 2.7 (the review runs), MANAGE 2.3 (the defect
precedent), MANAGE 2.4 (the emergency call proved unblockable; the grant bounded), MANAGE 3.1 (a third-party
component's defect recorded against its row).

**Two gaps grew while keeping their mark.** MEASURE 1.3: twenty-nine records and two Proposed ones, every text since
G10 assistant-drafted, no reviewer. MEASURE 3.2: three placeholders added to the list.

## 1.6 The residual-risk statement is stale, on these facts

The statement that discharges MANAGE 1.4 was written against G9. A reader using it at G11 would be wrong about:

| Statement says | G11 says |
|---|---|
| §1.9: break-glass is coupled to Observer liveness (too hard) and has no TTL (too easy) | `EmergencyNeverCoupled` proved; R8 withdrawn; the grant is one lease that ends with its round (ADR-0052, provisional) |
| §1.11: the verifiers are trusted as written | T-0045-31 has two known unsound cases, kept in use under a rule and a scan; fifteen modules have a kernel-checked second route (ADR-0053, T-0045-37) |
| §1.6: what runs is not what is proved; trace replay is the only link | Two functions transcribed and proved, two models of `apply` replayed; "a Lean proof of the code is not a proof of the code," and the package is stale |
| §1.4: the operator channel is the untyped half of the control plane | Operators are principals with keys, seated by promotion, able to deny without a lease (ADR-0050, provisional) |
| §2: thirty-six rows | Thirty-seven |
| §4: floor fitness "no owner, open since G1" | Owned by the bootstrap reviewer, timed, untested (item 87) |
| §4: the correlator's detection function "does not exist" | Drafted as ADR-0051, Proposed, with `Correlator.tla` proved |
| §4: the placeholders listed | Plus `T_wf`, the step bound and `N`; `denials` dropped as an attribute (ADR-0054 R6) |
| Nothing on workflows or liveness | Two Proposed records built at the reference on a floor not in force; four leads-to properties checked and not proved; the orchestrator a Byzantine principal of its own |

A new statement against G11 is the cheapest move on this list after §1.9 and the one that keeps MANAGE 1.4 at P
rather than letting it drift back.

## 1.7 The three gaps (G), and the debt carried beside them

| Row | Unaddressed practice | Why it cannot be scoped away | Where it sits |
|---|---|---|---|
| **MAP 3.4** | Operator and practitioner proficiency | A5 presumes a trained, authorized human for the emergency seat, quarantine release and `D`; ADR-0050 says who acted and nothing about skill | No record; the deployment declaration would carry it |
| **MEASURE 1.3** | Independent assessors | ADR-0029 A2 makes a review a bootstrap precondition; none is engaged; the guide to the review is written and the review is not | G11 §4, the A2.5 line |
| **MEASURE 3.2** | Risk tracking where metrics are unavailable | `L` unmeasured; eight placeholders; `slm/` could measure two today | G11 item 101; CR-36 |

**Carried beside them, no longer a G row:** floor fitness, MEASURE 2.13's other half. It moved out of G only because
the row's outcome was discharged on a different process. It is the fourth gate Moon & Varshney's result requires, it
has had an owner since Batch 34 and no definition since G1, and it stays on this list under its own name.

## 1.8 The three convertible rows (C)

| Row | What exists | What is missing |
|---|---|---|
| MAP 3.2 | The capability cost (no shell); the durability cost found on 10.01 | The durability cost stated in ToO §2.4; an adoption-cost table |
| MEASURE 2.10 | Erasure as a modeled event, the topic as its unit, the plaintext store kept apart | A privacy framing of machinery built for deletion |
| MANAGE 2.1 | The hierarchy-of-needs drop order and the control-plane cost model (09.10, 09.11) | Filing them; a non-AI-alternatives paragraph |

GOVERN 1.2 left this list; its sentence was written in the architecture description.

## 1.9 The twenty-seven partial rows: the unaddressed half

| Row | Addressed | Not addressed |
|---|---|---|
| GOVERN 1.2 | A characteristics mapping, drafted | Settled as the mapping; policies and procedures, not goals |
| GOVERN 1.3, MAP 1.5 | The instrument | A written deployment declaration |
| GOVERN 1.5 | A cadence | A role other than the custodian's; a criterion for assisted drafting (item 66) |
| GOVERN 1.6 | Principals, Personas, workflow graphs | Systems |
| GOVERN 1.7 | A principal, including an emergency seat | A system: re-genesis migration (item 10) |
| GOVERN 2.3 | Custody and approver rows | An organizational role |
| GOVERN 4.2 | Rows and a residual-risk statement | A current statement; communication outside the repository |
| GOVERN 4.3 | `SECURITY.md`; defects found and recorded | The defects reported to their maintainer |
| GOVERN 6.2 | Stall by mechanism; a defective trust root kept under a rule | The degraded mode, unfiled |
| MAP 2.2 | Havoc stated as the substitution | Assessment |
| MAP 3.5 | Oversight defined; the emergency call proved unblockable | `L`; an Observer that exists |
| MEASURE 1.1 | The non-measurement declaration | Current; the workflow placeholders |
| MEASURE 2.3 | The compose rig; 155 tests | A smoke run since 09.25 |
| MEASURE 2.4 | Coupling; the stall shown to end | The detection function (ADR-0051, Proposed); an Observer |
| MEASURE 2.6 | Refusal paths; liveness evidence; a residual statement | A declared tolerance; a current statement |
| MEASURE 2.7 | Mutations, negative controls, review runs | Time-to-bypass; an adversarial exercise; sharing |
| MEASURE 2.13 | One TEVV process evaluated and found wanting | Floor fitness |
| MEASURE 3.1 | Unanticipated-results sections | Tracking for a deployment |
| MANAGE 1.1 | A containment gate | A purpose gate |
| MANAGE 1.2 | Two prioritizations | A treatment plan for a deployment |
| MANAGE 1.3 | Responses to design forks | A mapped risk register |
| MANAGE 1.4 | A statement with undeclared numbers | Numbers; currency |
| MANAGE 3.1 | Components as rows; one defect recorded | Monitoring; reporting |
| MANAGE 3.2 | Pins; lineage projection (Proposed) | Behaviour monitoring (declined by design) |
| MANAGE 4.1 | Override, incident response, change management | Appeal; user input |
| MANAGE 4.3 | Tracking | Communication, to affected communities and to the maintainer of a defective component |

## 1.10 Out of scope (X), by group (28)

Unchanged from 10.03, and the scope declaration the 10.03 inventory said each needs now has a start:
`architecture-description.md` §3's "out of scope by position" line and §10.1's three characteristics marked out of
scope by premise. ToO §13 is still where a full declaration would land.

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

## 1.11 Reverse deltas: TOPAK constructs with no Playbook home

The 10.03 list of eight stands. G11 adds three.

| TOPAK construct | Why the Playbook has no row for it |
|---|---|
| **A trust root kept in use with a recorded defect** | MAP 4.2 asks for controls per component and MANAGE 3.1 for monitoring; no row asks an organization to state what its verifier is known to prove falsely, the rule that keeps a proof from it, and which results were re-read against it (ADR-0046 A2; ADR-0045 A3). The Playbook treats TEVV tooling as sound |
| **Liveness stated as an extension of a frozen module** | MEASURE 2.6's "fails safely" has no vocabulary for the difference between a stall that is safe and a stall that ends; `Coupling_live` states it, TLC checks it, and the corpus says it is not proved |
| **A second method that proves again and certifies nothing new** | MEASURE 2.13 asks whether TEVV is effective; no row contemplates a second TEVV route whose only purpose is to not share the first route's trusted base (ADR-0053 §5, R7: the derived premise) |

## 1.12 What to do with this, in order

1. **MEASURE 1.3.** Engage a reviewer. The guide to the review exists since this cut; nothing else moves three
   grades.
2. **GOVERN 4.3, MANAGE 4.3, MEASURE 2.7's sharing clause.** Report the prover's two cases upstream. Three rows ask
   for it in as many words, it costs one message, and it is the one item here the custodian has decided against
   (item 104). This inventory records the reading and not the decision.
3. **MANAGE 1.4, MEASURE 1.1, GOVERN 4.2.** A residual-risk statement against G11 (§1.6).
4. **MEASURE 2.13's other half, MEASURE 3.2, MAP 3.4.** Floor fitness defined; a measurement program the rehearsal
   rig can start; a proficiency declaration.
5. **The three C rows**, as one appendix.
6. **ADR-0024's miscitation** (Part III, item 6): blocking for any external draft, as the 10.05 assessment said, and
   still live.

---

# Part II — TACIP, the 2026.09.13(b) draft, at G11

The 10.02 review graded this draft B+ against G9 (its §3) and the 10.05 assessment read the 09.28(a) draft's six
deltas against G10 (its §8.2). Both stand and are not repeated. This section re-reads the 09.13(b) draft, the one
attached, against G11, and reads Appendix B, which neither earlier pass did. TACIP's thirteen Practices are cited by
their Task and Implementation numbers; the draft's own line prefixed ">" are reviewer notes and were not read as
guidance.

**The grade stays at B+, with the sign changed on three cells.** Practices 3 and 13 improve (liveness checked; the
delegation position stated, Proposed). Practice 12 worsens on the corpus (more assistant-drafted material, a trust
root known to be unsound, still no second reader). And 3.9.5's *Verifiable* is further from passing than on 10.02,
because the corpus now says of itself that "a certified proof is not a verified one" (G11 §8).

## 2.1 By Practice

| Practice | G11 | Basis, and what moved |
|---|---|---|
| **1** Requirements for success | X on the model; P on the mechanism | TEVV of model behaviour is outside the pattern by premise (ADR-0007). 1.3.4's audit-ready evidence exists for the mechanism: twenty-four proof modules, the scan, the Lean route. 1.4.4, requirements for AI-generated artifacts, lands on the corpus (Practice 12) |
| **2** Robustness, resilience, QoS | P | 2.1.1 rate control: the Run sequence counts effects (ADR-0042) and ADR-0055's activation budget bounds every lease, the orchestrator's included (its finding 2), a rate limit the quorum votes on, Proposed. 2.2.2's watchdog is the Observer; "a watchdog may itself be part of the attack surface" is A13, and collusion still fails open |
| **3** Agentic behaviour | P | §2.2 |
| **4** Override, recovery, awareness | P | 4.1: an emergency seating by roster quorum for one round, no renewal, not coupled to an Observer, drilled once per domain per epoch (ADR-0052 §4, §6; provisional). **CR-29's two halves are closed by construction**: R3 is a forbid on `thinker` seats and an emergency seat is not one, and the time box is the round. 4.4 attention governance: nothing notifies a person; the correlator is Proposed. 4.5.1: `T_irrev` undeclared for every effect class (A10) |
| **5** IdAM for agents | M / P | 5.1.1, 5.2.2, 5.3.2, 5.3.3 as on 10.02, and now re-checked at apply for `Route` (ADR-0054 §8, Proposed). **5.3.2's delegation clause has an answer**: a workflow's promotion is the grant of every cell lease; no principal seats another (ADR-0054 §2, §3, Proposed). 5.1.3 mutual authentication between replicas: still absent (A9). 5.4.1: operators observe each other (ADR-0050 §6, provisional) |
| **6** External supply chain | X / P | AIBOM and procurement out of scope. 6.1.5 hazard reachability: `spec/inventory.py` computes which theorems a declared trusted base voids, and G11 §3 result 5 says it misreported the prover's row once; do not offer it as 6.1.5 evidence until that is fixed. 6.2.2 silent vendor update: a model provider is a row, not an event; detecting a silent weight change is what rung 3 would attest, and rung 3 is simulated |
| **7** Internal provenance | M / P | 7.3.2 policy-as-code: Cedar with totality, validation and non-vacuity gates, now also stated under cedar-spec's verified model; a bundle loads only under a key in the issued rules (ADR-0044), still a throwaway key; 123 regression cases per stage, rerun byte for byte. 7.3.3 policy locks: the floor is resident and promoted, a fence voids every lease and vote in flight, nothing adapts at run time. 7.4.1: the History rows and batch tables record what, who and on what evidence; the approver is the author. 7.5.1: the Persona pins prompt and decoder. 7.3.1's registry: four floor stages, and the stage the reference links is not in force |
| **8** Incident analysis | P / C | §2.3 |
| **9** Training | X | MAP 3.4 remains the only place skill could sit |
| **10** Logging and audit | M / P | 10.1.2 the inference receipt: the `Actuate` record with tool digest, input and result digests, labels, delivery mode and `clearSet` (ADR-0042 §3); the opening record carries the tool list and bundle revision (ADR-0048). 10.1.3 partitioning: ADR-0004 and ADR-0020 are TACIP's "raw text into separate storage" done as deletion. 10.3 trend analysis: the correlator, Proposed; `denials` dropped as an attribute because no replica holds a count every replica agrees on (ADR-0054 R6) |
| **11** Mission continuity | X / P | 11.2.4 controlled isolation: fence, expiry and the resident default-deny floor. Manual procedures, drills and re-commissioning out of scope |
| **12** Verify AI-generated artifacts | **G** on the corpus; P on the mechanism | §2.4 |
| **13** Retiring and withdrawing authority | P | 13.2.1: targeted revocation and the fence; "confirm each revocation" is the apply-time re-check and the ordered record. **13.2.2's cascade now has a stated position**, Proposed: no principal creates a subordinate, so there is nothing to cascade through, and a fence reaches workflow nodes not yet started (ADR-0054 §2). 13.2.3 orphaned credentials: at rung 1 no token enters the guest (ADR-0036, Proposed). 13.3.1 volatile state: deliberately not retained (ADR-0020), a C. 13.1.2, 13.1.3: out of scope |

## 2.2 Practice 3 at G11

- **3.2.1, 3.2.2 intercept points; constraints applied uniformly to every command source.** M. The admit path is the
  intercept; the floor applies to every principal, operators and emergency seats included, all `Mediated` by design.
- **3.2.3 fail-safe states.** P, moved. On 10.05 "the formal layer has no liveness property to say whether stall is
  the fail-safe state or a deadlock." G11 has `Coupling_live`'s four leads-to properties, TLC-checked and not proved,
  under A12 and the new A18, and the deadlock audit. TACIP's "whether an overridden agent resumes with its last context
  window or resets to baseline" has a structural answer: a round is the unit, a lease has no successor inside a
  workflow (ADR-0055 §6), persistent memory is outside the pattern. ADR-0023's declaration schema still has no field
  for a per-effect-class fail-safe (the 10.05 open item).
- **3.2.4, 3.3.1 notification; an unacknowledged loud failure forces fallback.** G, unchanged. Default deny is the
  fallback; nothing alerts a person. Denials placed against the log (ADR-0051, Proposed) are the cheapest input an
  alarm would need.
- **3.3.3 "immediate emergency override" on any output that intersects the wrappers.** C, deliberate. A deny is
  evidence, not an event: TOPAK refuses, records, and the round continues to its bound.
- **3.4.3 monitor the integrity of the validation controls.** P. Coupling makes an absent Observer loud and cannot
  see a colluding one (A13); operators are observed by peers (ADR-0050 §6).
- **3.5.3, 3.5.4 sandboxing and resource limits.** P. Rung 1 real, rung 3 simulated; no real principal `Contained`.
  The activation budget charges the orchestrator's rounds too (ADR-0055 §2); "notifications when limits are
  approached" absent.
- **3.8.3 multi-agent coupling analysis.** P, moved. ADR-0054 and ADR-0055 are the first records that model chaining;
  the re-evaluation TACIP wants when the risk surface changes is a promotion in TOPAK, the graph and its seatings
  voted together. Lineage alternation on clear edges (ADR-0035 R8) is a structural answer to the feedback-loop case
  TACIP 4.4.2's reviewer note calls open research, and it is declared, not enforced, until ADR-0035 is in force
  (D-0054-1).
- **3.9.5 the enforceability pentad.** *Effective* ✓, *Durable* ✓, *Sufficient in scope* ✓, as on 10.02. *Timely*
  ✗: `L` unmeasured, `T_irrev` undeclared. ***Verifiable* ✗, and worse**: 3.9.5(c) excludes "the capability's
  self-attestation"; the corpus is one hand's, a trust root is known to prove false statements with no check for the
  first case, and the second method "certifies nothing the first did not" (G11 §5). A second self-attestation is not
  an independent one.

## 2.3 Practice 8 at G11

- **8.1.2 systems that cannot satisfy root-cause analysis; 8.2 compensating controls.** TOPAK is self-declared in
  the class: boundary events only, cognitive state never written (ADR-0020). C, deliberate, and CR-38 still has no
  record saying so; ADR-0023's schema has no RCA field.
- **8.1.5 reconstructing a multi-agent cascade.** P, moved. For workflows: `Route` carries its basis, the log index
  of what the orchestrator was shown (ADR-0054 §8); the orchestrator's delivered track is the round's opening record,
  so its Observer reads what it was given (ADR-0055 §6); the activation's causal history is the unit of findings
  (ADR-0055 §3). Inter-agent communications do not exist to log: cells never address each other. Cascade
  reconstruction by construction, Proposed.
- **8.1.6 attack versus risk triage.** X by premise: "the reason for an emergency is unknown to the mechanism, by
  construction" (ADR-0052 §5). Havoc does not distinguish compromised from wrong.
- **8.1.3 the state at the time.** M: the lease names bundle revision, fence and Persona digest; F2 and F5 survive
  erasure (ADR-0028).
- **8.6.1 separate benefit-claiming from risk-reporting.** Reads straight onto the corpus: the custodian is author,
  ratifier and only reviewer.

## 2.4 Practice 12 at G11: the profile's concern applies to the corpus by name

- **12.1.1, 12.1.2 classification and provenance to model version, prompt and context.** Every record's provenance
  note names its sources and the custodian's settled points (⟨K1⟩ to ⟨K9⟩, ⟨M1⟩ to ⟨M5⟩, G11 §5), which is a
  legible answer to 12.2.3's "tacit requirements" and unusual. No record names the model version or the prompt. G.
- **12.1.3 authorization to promote.** The custodian ratifies unilaterally (ADR-0029 §2). M for the role, G for
  independence.
- **12.2.1 meta-safeguards when the deterministic verifiers are themselves AI-written.** The 10.02 review flagged
  this as CR-28. At G11 it is heavier: `spec/lean/`, `floor/lean/`, `mechanism/lean/`, both liveness modules,
  `Workflow.tla`, `Mesh.tla`, the `workflow` floor stage and the rebuilt reference were drafted by the assistant in
  five days with no second reader (G11 §1.2, §4). The prover's two unsound cases were found by the drafter while
  writing a proof (G11 §3 result 1): 12.2.1's correlated-failure concern in reverse, the AI-written verifier finding
  the defect in the human-built one. ADR-0029 A2 requires a full-corpus independent review before bootstrap; the
  A2.5 line reads "None / None"; item 66, a criterion for assisted drafting, is open and "resting on more". **G.**
- **3.2.5 and 1.4.4, "the presence of a reviewer is not by itself verification."** The custodian's reading of one
  transcription and 67 steps (G11 §1, §8) is exactly the case the profile names.
- **12.3.1 sandboxed testing of generated logic.** M for the mechanism: TLC mutations and witnesses, the graph checks
  against TLC's state graphs, trace replay; G11 §3 results 3 and 4 are this working. **12.3.2 rollback to a
  known-good, human-verified configuration.** Frozen modules by digest and a manifest per checkpoint; but the
  reference follows text not in force, so no known-good configuration of the whole exists.

## 2.5 What TOPAK could offer the profile

The 10.02 review's two offers stand (the passive e-stop; the computed theorem inventory as a stronger 6.1.5). G11
adds seven, each a construct the draft has no Implementation for:

1. **Labels as declarations delivered by the mechanism** (ADR-0047, ADR-0048). TACIP has provenance only as logging
   after the fact (10.1.2, 12.1.2); no Implementation says the guardrail layer should *tell the agent* what it is
   reading and what tools it has. A candidate under 3.2.2 or 5.2.2: the wrapper labels ingress and withholds by
   handle, rather than only blocking egress. With TOPAK's own caveat: a label is a declaration, not a finding.
2. **Deny-only findings that need no lease** (ADR-0050 §4: a lapsed operator can still stop its domain). 3.3.3's
   escalation tiers assume a judgment that can also approve; 13.2.1's "confirm each revocation" and 4.3's
   out-of-band control are answered by a deny that needs no channel to be granted.
3. **Declared workflows in place of delegation** (ADR-0054 §2, Proposed). 5.3.2 and 13.2.2 presuppose delegation
   chains and ask for cascade revocation; a quorum voting the whole graph, with the mechanism granting each node,
   gives 13.2.2 nothing to cascade through. A candidate Implementation under 5.3.
4. **A route checked again where it is applied** (ADR-0054 §8). 5.2.2 says prior authorization grants no blanket
   permission, and has no notion of a decision invalidated between decision and effect.
5. **A budget that charges the orchestrator** (ADR-0055 finding 2): a concrete lesson for 2.1.1 and 3.5.4.
6. **A drill as a real activation with a tool that can do nothing** (ADR-0052 §6). 4.1.3 asks for tabletop
   exercises; this one is on the log and countable.
7. **A verification tool with a known unsound case, kept in use under a usage rule** (ADR-0046 A2). 6.1.5 and 7.4.2
   have no language for it; neither does the Playbook (Part I, §1.11). Worth raising as a gap in the profile.

And one counter-position: **the reason is unknown by construction** (ADR-0052 §5) against 8.1.6's triage expectation.

## 2.6 Appendix B: would the mechanism have helped?

TACIP's Appendix B maps thirty-two historic incidents to Practices. Where TOPAK's mechanism applies at all, an agent
holding a lease over a typed alphabet, it addresses authority and reachability and not correctness. Read against the
draft's incident list:

- **Prevented or bounded by construction.** Water-dosing and dam set-point changes (i14, i25): an outward `Actuate`
  needs an allowlist entry, a live lease and a live Observer (R3), and a remote operator session is a principal under
  the same floor (3.2.2). Breaker commands (i16, i17): the same, with the epoch fence as the fleet stop and the
  passive e-stop under partition. Standing privilege across tenants (i11): leases are round-coterminous, no standing
  privilege exists. Payment orders with suppressed confirmations (i27): the `Actuate` record is written by the
  mechanism, not the principal, so an agent cannot hide its own confirmation, and denials are recorded. Silent
  exfiltration and a monitor that silently stopped (i26, i31): a dead Observer stalls its Thinker, and the label
  forbids refuse an outward call after an untrusted clear read (ADR-0047).
- **Partially.** A poisoned update through a signed channel (i9): bundles signed, Personas pinned, artifacts promoted
  by tally; a throwaway key, gate evidence an assertion, and a poisoned *model* is a trusted-base row, not something
  detected. Persistent unauthorized agent code (i10, i19, i21, i22): no lease, no action; but no real principal is
  `Contained`, so "persists after remediation" is answered by authority and not by eviction from the host.
  Credentials and unauthenticated APIs (i8, i13, i28): at rung 1 no token enters the guest (Proposed); replica mutual
  authentication absent.
- **Not addressed, by premise.** Wrong predictions, biased classifiers, hallucinated policy (i1, i2, i4, i5, i6):
  TOPAK bounds what a wrong Thinker can reach, not whether it is wrong; a deny-only Observer of independent lineage
  is the only cover, and ADR-0035 is Proposed. Perception and control failures in vehicles (i3, i7, i32): outside the
  alphabet, and TACIP's 3.2.3 reading of i3 is the case where "stall" is not a safe state, which is why A10 requires
  `T_irrev` per effect class and an effect irreversible on emission out of the alphabet. Ransomware, wipers and
  bricked fleets (i12, i18, i23, i24): continuity is out of scope. Social engineering of help desks (i29, i30): a
  provider that lies is T-0045-35.
- **The honest residual.** Automatic benefit discontinuation on a flag (i6, mapped to P3) is under TOPAK an outward
  `Actuate` needing a live Observer of independent lineage, and it still happens if the Observer does not deny. The
  mechanism supplies no judgment, and the Appendix B cases where judgment failed are the majority.

---

# Part III — Moon & Varshney, arXiv:2605.09045v2, at G11

The 10.02 review graded the paper B+ against G9 and the 10.05 assessment verified every section pointer against the
text and dispositioned the 09.12 exposures at G10. Both stand. This section records what G11 changes, read against
the attached PDF (the same bytes), and nothing else.

**The paper, in one paragraph, as read.** Containment verification: the AI is a havoc oracle (Listing 1), the
containment layer is verified by forward-simulation refinement between an abstract boundary specification and the
concrete operational state machine (Definition 3.1, Theorem 3.2, Corollary 3.3), the guarantee is universal over the
typed action space and therefore independent of alignment (§2, Table 1). The trusted base is five items, the Dafny
verifier and compiler among them (§3.4). A deployed failure can come from three places: a failed refinement proof,
an effect-faithfulness gap, a property-completeness gap (§3.5, last paragraph). The PocketFlow witness has four
action variants (§4.1); an agentic pipeline synthesizes the artifacts under an information barrier (§4.2, §4.3);
three gates reject vacuous and non-discriminating specifications (§4.4); and the gates are necessary and not
sufficient, because silent abstention passes all three (§4.6, Appendix B). Five limitations (§5.1); the Impact
Statement is the scope declaration.

## 3.1 What G11 changes in the comparison

| Paper | At G10 (10.05 assessment) | At G11 |
|---|---|---|
| **The chain to code** (Theorem 3.2's (A2); §3.5 "failed refinement proof") | Absent; trace replay the only link; T-0045-28 the debt | Still absent. Two functions of the reference transcribed and proved in Lean, two models of `apply` replayed against 82 traces (ADR-0053); "a Lean proof of the code is not a proof of the code," and the package is stale (G11 §8, item 103). The paper's defining artifact is still the one TOPAK lacks; the grade does not move |
| **The verifier in the trusted base** (§3.4 names the Dafny verifier and compiler and trusts them) | T-0045-31 named, pinned, nineteen modules certified through an independent checker | **Extended past the paper.** T-0045-31 is now known to prove `FALSE` in two ways, kept in use under a rule and a scan, with a second kernel-checked route for fifteen modules (T-0045-37). The paper's §3.5 says a failed refinement is one "which Dafny detects by refusing"; TOPAK's record is that the detector is itself a row that can fail, and says what it does when it does |
| **The three failure sources** (§3.5) | Named as a taxonomy by the 09.12 assessment, which the 10.05 assessment corrected | **Each has a TOPAK instance at G11**, found by TOPAK's own checks (G11 §3, results 3, 4, 12). A model of `apply` left out the end of a lease and every proof held: a property-completeness gap, caught by trace replay, not by proof. A `Grant` that drops a check keeps both of `Seats`' invariants: an encoding too lax, invisible to the invariants, caught by the graph check against TLC's state graph. Neither check is in the paper; both are answers to §4.6's lesson that gates audit the proof and not the surface |
| **Template fitness** (§5.1: "validating that every safety corollary is reachable-non-empty") | The fourth gate, floor fitness, owned and undefined in TOPAK; built by neither | Unchanged for the floor. For the modules, TLC's witness discipline (every witness reached, every mutation breaking its property) is reachable-non-emptiness per property, as before; `M_HBLIVE` is the first mutation that passes every safety check and every witness and is caught only by a leads-to property (G11 §3, result 8), which is a fitness failure of a kind the paper's safety-only frame cannot state |
| **Witness scope** (§5.1: wider interfaces need more proof cases) | Nine variants, six operator requests, nine control entries, 28 policies | Wider again: `Route`, the `orchestrator` kind, a workflow interpreter, 30 policies and 123 cases. **`Workflow.tla` and `Mesh.tla` have no proof** (G11 item 101). The paper's caution lands exactly here |
| **Safety only; rejected actions as stutter** (§3.5) | — | TOPAK now checks four leads-to properties and proves two `ENABLED` invariants. The paper's frame cannot say whether a refused action leaves the flow able to continue; PocketFlow's step bound halts it. TACIP 3.2.3 asks the question the paper's frame cannot answer, and TOPAK can now answer part of it (Part II) |
| **The information barrier** (§4.3) | No analogue | No analogue, and the gap is sharper: every module, proof and Lean package since G10 was drafted by the assistant with the code in view (G11 §1.2). The paper's MI(P; I \| R, θ) = 0 is a construction TOPAK does not have, and TACIP 12.2.1 asks for one by another name |
| **Scope declaration** (Impact Statement) | Not written | Not written; `architecture-description.md` §3 and §10.1 are a start (Part I, §1.10) |

## 3.2 Residue the 10.05 assessment named, checked at this tree

- **ADR-0024's Consequences still read "fail together (Moon & Varshney §4.6; Knight & Leveson)"** (`ADR-0024.md`
  line 205). §4.6 and Appendix B say nothing about human reviewers; the 10.05 assessment called this blocking for
  any external draft. Still live. An erratum is the fix.
- **"Failure taxonomy §3.5"** survives only in the frozen 09.12 assessment. No live text uses it.
- **Varshney** is spelled correctly in every live text checked.

## 3.3 Where the comparison stands

Concordant, as before. Extended, now also on the verifier's own failure, liveness, and labels at ingress. Behind,
still, on the one artifact that defines the paper. The two still agree on the open problem, the fourth gate, and
TOPAK now has an instance of the paper's §4.6 lesson in its own tooling: a theorem that holds of a wrong model.
What the paper does with the lesson is a check it recommends and did not build; what TOPAK does with it is two checks
it built, neither of which is the fourth gate.

---

# Part IV — IBM, *Architecting secure enterprise AI agents with MCP*, October 2025

New to the corpus. Twenty-four pages, read whole. It is an enterprise lifecycle guide: an agent development
lifecycle (ADLC) of six DevSecOps phases, an MCP gateway pattern, a set of checklists for MCP servers, and a
reference architecture with non-functional and functional requirement tables. It names no formal method, no
threat model beyond a list of agent-specific risks, and no governance of who may change policy. It is the kind of
document a buyer of TOPAK would hold beside it, so the comparison is worth one table.

**Where the guide and TOPAK disagree on principle, and TOPAK knows it.** The guide puts probabilistic controls in
the enforcement path: guardrail models, LLM-as-a-judge, evaluation thresholds as release gates, "guardrail models to
check for bias in the LLM input and output" (p. 5), gateway plugins that filter prompts for injections (p. 11, p. 14).
ADR-0007 forbids every one of these as a lift; ADR-0016 §3 says a passing evaluation can never admit a Persona;
ADR-0051's judgment tier is deny-only and Proposed. Where the table below marks ⇄, the low score is a position, not an
omission. Evaluations and red-team results are admitted as *evidence* (ADR-0016 §2), and the corpus has none, so part
of the gap is real.

**Marks.** ● meets or exceeds · ◐ partial · ○ absent · ⇄ deliberate disagreement. Two columns, since the guide asks
about a running system: the design, and the reference as built.

| Guide area (page) | Design | Built | At G11 |
|---|---|---|---|
| Acceptable agency; authority boundaries (pp. 4–5, 12) | ● | ● | Closed typed alphabets (ADR-0022, ADR-0040); effects are exactly tool invocation and emission (ADR-0015); an effect irreversible on emission must leave the alphabet (ADR-0032 §4). Stronger than "approvals for high-impact actions" |
| MCP gateway pattern (pp. 13–15) | ● | ◐ | The mechanism is the gateway: `admit ⟺ floor_permit ∧ ¬bundle_deny`, ordered through Paxos, tools pinned by `name@digest`, descriptions rendered only from the signed entry (ADR-0048: "the rug-pull cannot happen here"). Absent: per-tool rate limits and kill switch, HTTP transport, multi-tenancy (the word appears nowhere in the records) |
| Agent identity and access (pp. 11, 15) | ● | ◐ | One key per seat; the lease is the credential for one round (ADR-0031); revocation and fence subtract without a quorum. The session is a bearer token on a socket (`mechanism/` G5); no OAuth; replicas unauthenticated |
| Prompt injection and data leakage (pp. 6, 11) | ● ⇄ | ◐ | Labels on every ingress item, handles for what is suppressed, forbids R5 to R7 (ADR-0047 to 0049). Output sanitization and guardrail models excluded from the admit path by ADR-0007. A label is a declaration, not a finding (G11 §8) |
| Sandboxing as baseline control (pp. 5–6, 15) | ● | ○ | ADR-0034's profile clauses and attested rungs exceed the guide's list; "no real principal is `Contained`" (G11 §8): rung 1 trusts the host, rung 2 a seam, rung 3 simulated. The guide's Firecracker/gVisor/seccomp list is the rung-1 and rung-2 work the corpus has not done |
| Kill switch; break-glass (pp. 6, 12, 14) | ● | ◐ | Targeted revocation and the epoch fence; an emergency seating for one round (ADR-0052, provisional, "no settled form") |
| Audit trail; immutable logs (pp. 12, 16) | ● | ◐ | Every effect and denial consensus-ordered with a signed predecessor; six forensic classes survive erasure (ADR-0028). "Legibility replaces immutability" (ToO §4.4). No correlation IDs; no governed archive; replay says what, never why (ADR-0020) |
| Governed catalog; certification workflow (pp. 11–12) | ◐ | ◐ | Promotion by unanimous quorum, votes bound to digests, author recusal (ADR-0024); a workflow's promotion seats every cell (ADR-0054, Proposed). No owner, purpose, environment or classification fields; no semver, deprecation, retirement or champion–challenger |
| Supply chain: SBOM, signing, pinning, scanning (pp. 11, 17) | ◐ | ◐ | Bundle signing (ADR-0044, under a throwaway key); `Cargo.lock`; corpus pins and manifests pin records and trees, not dependencies. No SBOM, no scanning, no CI; `mechanism/docker-compose.yml` pulls `:latest` for Kafka and OPA. T-0045-30: no reproducible build declared |
| Secrets and transport (pp. 15, 17) | ○ | ○ | Replica frames "unauthenticated JSON over plain TCP" (`topak-node/src/net.rs`); Kafka without TLS or SASL; `dev/secrets/` in the clear (G6). The design has Ed25519 for every authority key and nothing for transport |
| Evaluation: offline, online, LLM-as-judge, red teaming (pp. 5, 9) | ⇄ | ○ | Evidence, never a precondition (ADR-0016 §2–3); the correlator's judgment tier deny-only and Proposed. No evaluation and no red-team exercise exists even as evidence; the floor gates (ADR-0030 §5) are the only stand-in |
| Observability: OpenTelemetry, metrics, cost, drift (pp. 9–10) | ◐ | ○ | The Observer and correlator are designed, deny-only, and not built (G12). No telemetry, metrics, dashboards or token accounting; `tracing` to stdout. Decode observability (ADR-0019) is for substitution detection, "not introspection" |
| Operations: SLOs, circuit breakers, rollout, scale (pp. 6, 16–17) | ○ | ○ | Crash-fault Paxos with a WAL and at-most-once apply; no SLOs, canaries, flags or Kubernetes; one global log; every value a placeholder |
| Plan phase: KPIs, use-case fit, "when to build agents" (pp. 4, 7–8) | ○ | ○ | Out of scope by premise (`architecture-description.md` §10.1: Valid, Accurate, Fair) |
| Data handling and compliance (pp. 12, 16, 19) | ◐ | ○ | Erasure designed (ADR-0003, ADR-0006), not built; no PII handling, consent, tenancy, or mapping to HIPAA, SOC 2 or ISO. The AI RMF is the one framework mapped |
| Memory and state (pp. 6, 19) | ⇄ | ● | Persistent agent memory is outside the pattern; the round topic sealed on emit is the unit; `clearSet` is the only memory policy reads. The guide's "memory poisoning" has no surface here |
| Multi-agent orchestration; A2A (pp. 6, 19–20) | ◐ | ◐ | A promoted DAG or mesh under a voted budget, an orchestrator that only narrows (ADR-0054, ADR-0055, Proposed, built); handoffs, group chat, agent-as-tool and A2A rejected by name in ADR-0054's options table |
| Production-readiness checklist (p. 18, seven items) | — | ◐ | Met as built: least-privilege authorization; input validation. Not met: output sanitization, secret manager, metrics and alerts, signed non-root containers, SLOs and runbooks. `slm/serve/` alone is hardened to the guide's container standard |

**What the guide has that the corpus should take.** Two things, neither a design change. The guide's catalog
fields (owner, purpose, environment, data classification, security review date, risk level, p. 16) are what
GOVERN 1.6's "systems" half and MAP 3.4's declaration would carry, and ADR-0049's entry schema has no field for any
of them. And the guide's packaging checklist (p. 17) is the shape of the reproducible build T-0045-30 says is not
declared.

**What the corpus has that the guide does not ask for.** Who may change the policy the gateway enforces, and how
many must agree (the 10.05 assessment's §8.5 closing question, which this guide also does not answer); a verifier
behind the floor; denials recorded; a stall as the failure mode in place of a graded response; and the premise that
the agent is Byzantine rather than "a legitimate, uncompromised AI system that is not behaving as intended."

---

## Sources

- The four attached documents, by digest in the header. The Playbook JSON's 72 entries carry `title`, `description`,
  `section_about`, `section_actions`, `section_doc`, `section_ref`, `AI Actors` and `Topic`; the outcome wording in
  Part I is the Core's, abridged, as on 10.03.
- G11 (`checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md`, tag `G11`); ToO revision 15 (tag `ToO-rev15`);
  `narrative/architecture-description.md` revision 3; `REVIEWERS_GUIDE_README.md` (2026.10.09, draft, unmeasured).
- `derived/topak-playbook-delta-inventory-2026.10.03.md`; `derived/topak-critical-review-2026.10.02.md` §3, §4 and
  Table 1; `derived/topak-external-and-competitive-assessment-2026.10.05.md` §7, §8;
  `derived/topak-residual-risk-statement-2026.10.03.md`; `derived/topak-liveness-2026.10.07.md`.
- Records cited by number; `mechanism/GAPS-AND-ASSUMPTIONS.md` by its gap and item numbers (G5, G6, G12, I34, I45
  to I49); `mechanism/crates/topak-node/src/net.rs`; `mechanism/docker-compose.yml`.
- Nothing was run. Marks are readings of the texts named; every path cited resolves at the tree named in the header.
