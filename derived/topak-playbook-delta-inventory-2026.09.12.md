<!-- RECOVERED · HISTORICAL · 2026-09-15 · tranche 3 -->
> **Recovery note.** Source: Unmatched deltas with NIST playbook session 09.12 (https://claude.ai/chat/94ed200e-086a-497d-b95b-941d41531ca7), `create_file` turn 1, file `topak-playbook-delta-inventory-2026.09.12.md`. No later edits.
>
> **Marked historical.** The stated tally (M 5 · P 6 · C 14 · G 8 · X 38 · ! 1) does not match the row marks, which sum to M 6 · P 12 · C 15 · G 9 · X 30 · ! 1; MEASURE has 22 rows, not 19. The feature list §9 carries the corrected counts. The MANAGE 2.4 row repeats the "ADR-0006 crypto-shreds" misstatement (registry finding T3-1).
>
> Text below is verbatim from session history (HTML entities normalized). **Historical artifact:**
> nothing folds into it. Later corrections live in the records and checkpoints that supersede it.

# TOPAK — NIST AI RMF Playbook Delta Inventory

**2026.09.12** · inventories the Theory of Operation checkpoint of the same date against all 72
Playbook subcategories · *The Gripping Hand*

Companion to the external assessment of the same date, which gave coverage *shape*. This gives
coverage *extent*: every subcategory in the National Institute of Standards and Technology (NIST)
Artificial Intelligence Risk Management Framework (AI RMF) Playbook, marked, with nothing dropped.

**Basis for "matched."** A subcategory is matched only where the 09.12 checkpoint contains a named
mechanism or ratified Architecture Decision Record (ADR) that discharges the outcome. Intent,
adjacency, and "the article will say this" do not count.

**Status key**

| Mark | Meaning |
|---|---|
| **M** | Matched — mechanism exists and is claimed |
| **P** | Partial — mechanism exists, outcome only half discharged |
| **C** | Convertible — mechanism already exists in TOPAK, never claimed here. Cost is a sentence, not a design |
| **G** | Gap — TOPAK's own safety argument needs this and does not have it |
| **X** | Out of scope — legitimately absent, discharged by a scope declaration |
| **!** | Contradiction — a ratified ADR conflicts with a named suggested action |

**Tally:** 72 subcategories. **M 5 · P 6 · C 14 · G 8 · X 38 · ! 1.**
Sixty-one unmatched, of which 38 are scope declarations, 14 are free, 8 are real, 1 is a conflict.

---

## 1. GOVERN (19)

| # | Outcome | | Note |
|---|---|---|---|
| 1.1 | Legal/regulatory requirements understood, managed, documented | X | Organizational. One adjacency: the erasure demand taxonomy (ADR-0006, types 1–5) is a legal-requirement artifact with no recorded legal basis behind it. |
| 1.2 | Trustworthy-AI characteristics integrated into policy | **C** | TOPAK never maps itself to the RMF's seven characteristics. It touches four (safe, secure/resilient, accountable/transparent, privacy-enhanced) and disclaims three by havoc semantics. Half a page. |
| 1.3 | Risk-management activity scaled to risk tolerance | **C** | The deployment ladder **is** this, and is currently framed as an engineering ladder. Rungs as documented subtractions from an archetype = activity level scaled to tolerance. The unresolved axis question is the only blocker. |
| 1.4 | Transparent policies, procedures, controls; documentation | **M** | The ADR log, including the 0011 tombstone convention. |
| 1.5 | Ongoing monitoring and periodic review; roles; review frequency | **P** | Incident response maps. *Periodic review of the risk process itself* has no owner; ADR-0014 (floor authorship and change control) is the nearest home and is open. |
| 1.6 | Mechanisms to inventory AI systems, resourced by risk priority | **C** | Highest-value free conversion in GOVERN. Lease registry + principal identity + epoch + rung manifest is a *live, self-maintaining* inventory, not a spreadsheet refreshed quarterly. An expired lease removes the entry by construction. Claim it. |
| 1.7 | Decommissioning and phase-out, safely | **P** | Eviction, epoch fencing and lease expiry decommission a *principal* cleanly. Decommissioning a *system* — key destruction, retention wind-down, topic disposition — is unaddressed and interacts with ADR-0003's round-topic scheme. |
| 2.1 | Roles, responsibilities, separation of development from testing | **M** | ADR-0008, fault-domain independence. Monoculture declaration answers the groupthink rationale at the model layer. |
| 2.2 | Personnel and partner risk-management training | X | Organizational — but see MAP 3.4, where the same concern is load-bearing. |
| 2.3 | Executive leadership accountable for AI risk decisions | **G** | The Build promotion signing key is an accountability locus sitting *outside* `Contain` by design (ADR-0002), held by a human with no named organizational role and no stated seniority. A governance reader will ask who holds it. ADR-0014's proper scope. |
| 3.1 | Diverse team informs lifecycle decisions | X | Organizational. The cross-family Observer requirement is the mechanical analogue, not a substitute. |
| 3.2 | Roles and responsibilities for human-AI configurations and oversight | **M** | Second-strongest fit in the document and unclaimed until now. HITL/HOTL/HOOTL defined by what the loop does when the human does not act; the evictability test separating principal from gate; admins as HOTL-by-default, HITL-at-break-glass. The Playbook asks for policies here; TOPAK has model-checkable predicates. |
| 4.1 | Critical-thinking, safety-first culture | X | Cultural. "Verify the cage, not the occupant" is a design posture, not a policy. |
| 4.2 | Teams document risks and impacts; communicate broadly | **C** | The trusted-base enumeration (assessment §I.7) discharges the documentation half once written. The communication half is out of scope. |
| 4.3 | Enable testing, incident identification, information sharing | **P** | Replay and audit identify incidents. External information sharing is absent, and the erasure conflict (§4) narrows what can be shared. |
| 5.1 | External feedback on impacts collected and integrated | X | Out of scope. |
| 5.2 | Adjudicated feedback incorporated into design | X | Out of scope. The semantic-lift rule adjudicates human input at *runtime* (a finding may deny, never admit); it says nothing about design-time feedback. |
| 6.1 | Third-party risk policies, including intellectual property | X | Untouched: model licensing, training-data provenance, Rego and broker dependencies. |
| 6.2 | Contingency for third-party failure | **G** | The model provider is a third party whose failure is not a modeled event. Under havoc a *worse* model is harmless — a real strength — but an *unavailable* or *silently substituted* one is a liveness question the series has never addressed. **The "army of one" degraded-mode pattern from the 09.10 session is exactly this contingency and appears nowhere in the checkpoint series.** See §6. |

---

## 2. MAP (18)

The checkpoint is near-silent here, which is defensible for most rows and not for three.

| # | Outcome | | Note |
|---|---|---|---|
| 1.1 | Intended purpose, context, norms, deployment settings | X | The scope-declaration paragraph does the work. |
| 1.2 | Interdisciplinary actors, demographic diversity | X | Organizational. |
| 1.3 | Mission and goals documented | X | Out of scope. |
| 1.4 | Business value defined | X | Out of scope. |
| 1.5 | Organizational risk tolerances documented | **C** | Same conversion as GOVERN 1.3, same artifact — the rung manifest. Do both in one pass. |
| 1.6 | System requirements elicited; socio-technical design decisions | **C** | A Temporal Logic of Actions (TLA+) specification **is** a requirements artifact, machine-checkable, and the Playbook's own example ("the system shall respect the privacy of its users") is the form TLA+ improves on. Cite ISO/IEC/IEEE 29148 and claim the row. |
| 2.1 | Specific task and method defined | X | The typed action alphabet defines what a principal *may* do, never what the system is *for*. Adjacent, not matching. |
| 2.2 | Knowledge limits documented; how output is overseen | **P** | Havoc semantics is a *stronger* statement than documenting knowledge limits — it assumes the worst case rather than bounding it — and should be stated as a deliberate substitution, not left as an absence. Oversight half maps to §4 of the checkpoint. |
| 2.3 | Scientific integrity and TEVV considerations | **G** | The unresolved TLC-versus-TLAPS question (assessment §I.8) is precisely a TEVV-method disclosure. Until it is declared, the checkpoint's "proven absolutely" language is unbacked and this row is a genuine gap rather than a scope call. |
| 3.1 | Potential benefits examined and documented | X | Out of scope. |
| 3.2 | Potential costs, including non-monetary | **C** | The per-component adoption-cost and omission-cost analysis planned in the 09.10 session was never carried into the checkpoint series. It is MAP 3.2 material, it was already drafted once, and NIST named it as desired information. See §6. |
| 3.3 | Targeted application scope specified | **M** | Typed action alphabet. Three-way concordance with Moon & Varshney §5 and with the Playbook's own narrow-scope rationale. |
| 3.4 | Operator and practitioner proficiency defined and assessed | **G** | Load-bearing. `D` in `W < L < D` is a human-response budget, and quarantine release and break-glass are HITL gates. Both presuppose an operator who is present, trained, and authorized. TOPAK asserts the budget and never states the competence or availability requirement that makes it real. This is the Elish crumple-zone objection returning through a different door. |
| 3.5 | Human-oversight processes defined, assessed, documented | **P** | Defined and documented: yes, §4. **Assessed:** no — assessment requires `L` and the Observer's false-negative rate. Blocked on MEASURE 3.2. |
| 4.1 | Third-party legal and IP risk mapping | X | Out of scope. |
| 4.2 | Internal risk controls for components, including third-party | **C** | The floor, bundle refinement, epoch fencing and lease expiry are internal risk controls; the third-party half is discharged by the trusted-base enumeration. Same write-up as GOVERN 4.2. |
| 5.1 | Likelihood and magnitude of each impact | X | Out of scope. |
| 5.2 | Engagement with AI actors on impacts | X | Out of scope. |

---

## 3. MEASURE (19)

Largest absence and the one most likely to be attacked. Note that MEASURE 1.1 supplies the escape
hatch: it asks organizations to document the risks that will not or cannot be measured.

| # | Outcome | | Note |
|---|---|---|---|
| 1.1 | Metrics selected for significant risks; **unmeasurable risks documented** | **C** | The single most useful row in the function. The Playbook explicitly accommodates declared non-measurement. Enumerating what TOPAK does not measure — `L`, Observer false-negative rate, bypass time, floor reviewability — converts the whole MEASURE absence from a hole into a satisfied outcome. Do this one first. |
| 1.2 | Metric appropriateness regularly reassessed | X | No metrics program to reassess. |
| 1.3 | Independent assessors, not front-line developers | **P** | ADR-0008 is the mechanical analogue (the Observer is the assessor that did not build the Thinker). Human independent assessment is absent. Worth a sentence: TOPAK mechanizes the intent one layer down. |
| 2.1 | Test sets, metrics, and TEVV tooling documented | **C** | TOPAK has TEVV tooling and does not call it that: the TLA+ configuration, the refinement checker for `bundle ⊑ floor`, and ADR-0007's totality, non-vacuity and discrimination gates. Naming the Build gates as TEVV artifacts is the cheapest credibility gain available to a NIST audience. |
| 2.2 | Human-subject evaluation requirements | X | Not applicable. |
| 2.3 | Assurance criteria demonstrated under deployment-like conditions | **P** | The compose rig is a deployment-like environment with no documented assurance criteria attached to it. Criteria would make this an M. |
| 2.4 | Production monitoring of functionality and behavior | **P** | Observer plus the effect stream. Unmeasured detection quality keeps it from M. |
| 2.5 | Validity, reliability, generalizability limits | X | Agent-level; disclaimed by havoc semantics. |
| 2.6 | Safety evaluated; **fails safely**; residual risk within tolerance | **C** | Fail-safe is TOPAK's core claim and the Playbook names it explicitly: expiry-as-default-deny, the resident floor working at cold start and under partition (ADR-0012), monotone-safe stale bundles. Two of three clauses are free. The residual-risk clause waits on MANAGE 1.4. |
| 2.7 | Security and resilience evaluated and documented | **C** | The Playbook suggests **time-to-bypass** as a metric. That is `W < L < D` in the Playbook's own vocabulary, and TOPAK is the rare architecture that can state the bound structurally. Mechanisms exist; the evaluation does not. |
| 2.8 | Transparency and accountability risks examined | **C** | The attribution property — every exercise of authority traces to a lease-holding principal at a known epoch, holding for `Mediated` principals too — is an accountability *guarantee* rather than an examination. Claim it, then note the erasure tension (§4) in the same breath rather than letting a reviewer pair them. |
| 2.9 | Model explained, validated, interpreted | X | Explicitly out of scope by havoc semantics. Say so; do not leave it blank. |
| 2.10 | Privacy risk examined and documented | **C** | ADR-0003's topic-per-principal-per-round scheme, crypto-shredding, and the erasure demand taxonomy are privacy machinery with no privacy framing. Framing them here also reclassifies the §4 contradiction as a **recognized privacy-versus-forensics tradeoff** rather than a defect — the Playbook treats that tension as normal. |
| 2.11 | Fairness and bias | X | Out of scope; content-level. |
| 2.12 | Environmental impact and sustainability | X | The control-plane cost model and the ~9-versus-~40 Observer instance argument are compute-cost analyses, adjacent at best. |
| 2.13 | **Effectiveness of TEVV metrics and processes evaluated** | **G** | This is the Playbook's name for the assessment's highest-value finding. Moon & Varshney §4.6 and Appendix B show a vacuous specification passing all three gates. ADR-0007 extends those same three gates to the floor and the checkpoint calls that extension "the only thing standing between TOPAK and its own failure." The proposed fourth gate — floor fitness — is a MEASURE 2.13 action, and framing it that way gives it the owner it currently lacks. |
| 3.1 | Track existing, unanticipated, and emergent risks | X | Out of scope, absent a metrics program. |
| 3.2 | Risk tracking where measurement techniques are unavailable | **G** | The hole that cannot be scoped away. `W < L < D` requires `L`; the Observer's false-negative rate and latency distribution are unbounded everywhere in the series. A MEASURE-shaped hole inside a MANAGE-shaped design. Minimum answer: `L` as a deployment obligation carried in the rung manifest, not an architectural property. |
| 3.3 | End-user and community feedback, problem reporting, appeal | X | Operator override is not user appeal. Keep the distinction explicit — MANAGE 4.1 makes it easy to blur. |
| 4.1 | Measurement connected to deployment context; domain experts | X | Out of scope. |
| 4.2 | Results validated by domain experts and AI actors | X | Out of scope. |
| 4.3 | Measurable improvements or declines from field data | X | Out of scope. |

---

## 4. MANAGE (13)

The home function. Also where the one conflict lives.

| # | Outcome | | Note |
|---|---|---|---|
| 1.1 | Determination that the system achieves intended purpose; proceed or not | **P** | The Build promotion gate is a genuine go/no-go, but it answers *is it contained*, never *should it ship*. State the distinction rather than let it be assumed — a governance reader will read the gate as a purpose gate. |
| 1.2 | Risk treatment prioritized by impact, likelihood, resources | X | Organizational. |
| 1.3 | Documented responses to high-priority risks | **P** | The ADR log documents responses well. It documents them against *design* forks, not against a mapped risk register — and TOPAK has no MAP function, so the antecedent is missing. Honest mark is P, not M. |
| 1.4 | **Negative residual risk documented for downstream acquirers and end users** | **G** | The Impact-Statement-shaped hole with a Playbook number on it. The residual set already exists in pieces: the trusted base (§I.7), effect exclusivity, the sandbox gap, `Mediated` principals' out-of-band effects, the two floor exceptions pending ADR-0013. Writing them as one residual-risk statement discharges this row *and* MEASURE 2.6's third clause *and* the scope declaration the article needs. Highest leverage single document in the inventory. |
| 2.1 | Resources accounted for; non-AI alternatives considered | **C** | The 09.10 hierarchy-of-needs analysis (drop order P → T → K → O, A reframed as payload) is an alternatives analysis in everything but name, and the control-plane cost model is the resource half. Both exist in session history and neither is in the checkpoint. See §6. |
| 2.2 | Mechanisms sustain the value of deployed systems | X | Weak fit in either direction. |
| 2.3 | Respond to and recover from a previously unknown risk | **M** | Quarantine, epoch fencing, break-glass, replay. Recovery from the *unknown* is what default-deny buys: the response does not require the risk to have been enumerated first. That is the strongest form of this outcome available and it should be said in exactly those terms. |
| 2.4 | Supersede, disengage, deactivate | **M !** | Closest fit in the Playbook, and the location of the one contradiction. Lease expiry is a passive e-stop requiring no human action; every Playbook suggestion here presumes someone decides to act. **Conflict:** the same subcategory suggests preserving materials for forensic, regulatory and legal review, and ADR-0006 crypto-shreds. Answer is the forensic floor — a bounded fact set surviving erasure and break-glass, monotone in the opposite direction from the policy floor. Lands in ADR-0013 as a fifth obligation. |
| 3.1 | Third-party risks monitored; controls applied and documented | **G** | Where the monoculture declaration belongs — one model family across Listener/Thinker/Reader/Observer seats is third-party concentration risk in the Playbook's vocabulary. Currently filed as a loose open-list item with no control attached. |
| 3.2 | **Pre-trained models monitored as part of regular maintenance** | **G** | Sharpest unclaimed gap in MANAGE. TOPAK pins the mechanism, pins the bundle, pins the floor, fences the epoch — and does not pin or monitor the model. Version drift beneath a stable API and silent substitution are unmodeled. Havoc semantics makes a worse model harmless *for containment*, which is worth claiming loudly, and says nothing about maintenance. The asymmetry is conspicuous: everything is pinned except the one component declared unverifiable. |
| 4.1 | Post-deployment monitoring, appeal and override, decommissioning, incident response, change management | **P** | Override, incident response and change management map. Appeal and user input do not exist; decommissioning is GOVERN 1.7's partial. |
| 4.2 | Continual improvement with interested parties | X | Out of scope. |
| 4.3 | Incidents communicated to affected communities; tracking documented | **P** | Tracking and root-cause: yes. Communication to affected communities: no, and constrained by erasure. |

---

## 5. Reverse deltas — TOPAK constructs with no Playbook home

The inventory runs both ways, and this direction is the position-paper material. These are not gaps
in TOPAK; they are gaps in the Playbook that TOPAK is positioned to name.

| TOPAK construct | Why the Playbook has no row for it |
|---|---|
| **Passive e-stop** — lease expiry as default-deny | Every MANAGE 2.4 suggestion presumes an actor who decides to act. The Playbook has no vocabulary for a control that operates when *nobody* acts. This is the single best contribution available to the Critical Infrastructure Profile. |
| **Monotonicity as one principle across three layers** | Consensus for grants and local for denials; bundles may only subtract from the floor; rungs are documented subtractions from an archetype. The Playbook treats risk controls as additive safeguards and has no notion of an authority-monotone system. |
| **Floor refinement (`bundle ⊑ floor`) at promotion time** | The Playbook's change-management language is procedural. A mechanically decidable admissibility check on policy change has no subcategory. |
| **Evictability as the principal test** | "If you can be evicted you are a principal; if you are the authority that evicts you are at the gate." GOVERN 3.2 asks for documented human-AI configurations and offers no test for drawing the line. |
| **HOOTL as a distinct state** | Not "nobody acted" but "no action was expressible." The Playbook's human-oversight material distinguishes degrees of involvement, never the absence of a channel. |
| **`Contained` versus `Mediated` principals** | Effect exclusivity as a per-principal predicate, with humans never `Contained`. The Playbook assumes the system is the machine and the human is outside it. |
| **Build as the hostile domain** | The Playbook's supply-chain material (GOVERN 6.x, MANAGE 3.1) treats third parties as the threat. TOPAK's inversion — the Byzantine threat lives in the pipeline, and a human signing a green pipeline is the documented failure — has no Playbook expression. |

---

## 6. Carried-off items — already reasoned, never filed

Four things exist in session history, would close or narrow rows above, and are absent from the
checkpoint series. Recovering them is cheaper than deriving them again.

| Item | Origin | Closes |
|---|---|---|
| **"Army of one" degraded mode** — shed coordination under total partition, run single-agent under a cached reduced-authority bundle with a durable local log for rejoin reconciliation | 09.10 NIST session | GOVERN 6.2, MANAGE 2.3 (strengthens). Also carries two requirements that were stated then and never filed: rejoin reconciliation must be specified in TLA+, and the cached bundle needs expiry or authority narrowing. The second is now subsumed by the floor. |
| **Per-component adoption-cost and omission-cost table** | 09.10 NIST session | MAP 3.2. NIST named it as desired information. |
| **Hierarchy-of-needs drop order** (P → T → K → O; A as payload) | 09.10 session | MANAGE 2.1 alternatives analysis. |
| **Control-plane cost model** | 09.11 session | MANAGE 2.1 resources; adjacent to MEASURE 2.12. |

---

## 7. What to do with this, in order

1. **MANAGE 1.4 residual-risk statement.** One document discharges MANAGE 1.4, MEASURE 2.6's third
   clause, GOVERN 4.2, MAP 4.2, and the article's scope declaration. Built from the trusted-base
   enumeration, which was already on the list.
2. **MEASURE 1.1 non-measurement declaration.** Converts the whole MEASURE absence from a hole into
   a satisfied outcome, using the Playbook's own accommodation. Half a page.
3. **The eight G rows.** GOVERN 2.3 and 6.2, MAP 2.3 and 3.4, MEASURE 2.13 and 3.2, MANAGE 3.1 and
   3.2. Three of these (MEASURE 2.13, MEASURE 3.2, MANAGE 3.2) are design work; the rest are
   declarations. Note that MEASURE 2.13 and the floor-fitness gate are the same item and it still
   has no owner.
4. **The fourteen C rows, batched.** Mostly one or two sentences each, best written as a single
   mapping appendix rather than scattered through the article.
5. **Reverse deltas into the position paper.** These are what NIST asked for — gaps in practical,
   actionable guidance — and they are the part of this inventory that is not compliance work.
