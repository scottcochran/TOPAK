# TOPAK — Fit against the Foresight Institute RFP, "Coordination and accountability"

**2026.11.13** · derived · a reading, not a record · basis: the tree at `bb76b46` (`main`), read through `README.md`,
Theory of Operation revision 15 §0 to §2, the decisions index, Genesis Checkpoint G11's ADR-0029 A2.5 line,
`derived/topak-critical-review-2026.11.11.md` §0 and its finding headlines, and
`derived/scenarios-2026.11.12/FINDINGS_TOPAK.md` · the request for proposals as the custodian pasted it into the
session on 2026.11.13, **not fetched** and not checked against its publisher's page · the sixty-eight record files
were **not** read whole, and nothing was run · prepared by the assistant at the custodian's request ·
**suggested entries, none made**

**The question.** How does TOPAK stand against the request for proposals, and against each of the frames of
reference that document judges by: its three focus areas and its evaluation criteria?

**Not independent.** This is the drafter's lineage reading the drafter's work against a funder's text. It is not the
reader ADR-0029 A2 asks for, it counts for nothing under A2.1, and it grades no record.

Nothing here is ratified, and this document proposes no decision text.

---

## 0. The answer

**TOPAK is a strong fit for one half of one focus area and an indirect fit for the rest.** The half is the security
side of focus area 2: aligning agents "without relying on a single central authority", by "mutual monitoring and
cross-checking among agents" and "scalable verification and proof techniques". That is close to a description of
what the corpus builds. The other half of that area, collaboration, credit assignment and incentives, is not in the
corpus. Focus area 3 meets the pattern at one record, ADR-0066, which is Proposed. Focus area 4 meets it only
through the evidence a deployment publishes.

Against the evaluation criteria the corpus is strongest on open source and AI-first work, and weakest on capability
to execute, where its own state of record says no one but its authors has read it.

**The call is closed.** The text says so twice, with a deadline of 2026.10.31 23:59 PDT, thirteen days before this
document. This is a reading for a later round or for a submission already made; it cannot inform one to this round.

---

## 1. The frames the document judges by

The text is section II of a larger request; section I, on hardware and compute, was not supplied. It carries three
focus areas, numbered 2 to 4, and seven criteria.

| Frame | What it asks for, in its words |
|---|---|
| **2. Supercollaboration and decentralized alignment** | "coordination and credit-assignment protocols, tooling for massive human-AI collectives, and incentive designs"; and "aligning highly capable AI without relying on a single central authority" |
| 2, the named foundation | "boundaries as Schelling points for coordination", after Critch's Boundaries sequence: "agents can coordinate on which boundaries to mutually respect" |
| **3. Human Empowerment** | "Evidence, decision rules, and working tools that identify when human control genuinely empowers people or when AI delegation is preferable"; "Mechanisms to detect and fix hollow oversight" |
| **4. AI Insurance & Open Governance** | "a middle layer between labs doing self governance and governments doing regulation"; ways "for insurers to judge the risk of a frontier AI lab"; ways "for people outside a lab to assess risks" |
| Criteria | Alignment with the focus area; impact on existential risk; feasibility in one to three years; AI-first work; capability to execute; high-risk, high-reward; open source required |
| Terms | Grants of $30,000 to $100,000, smaller for areas 3 and 4; in-person contribution at the funder's Nodes strongly prioritized; for-profits must say why they need a grant |

---

## 2. Fit by focus area

| Frame | Fit | In one sentence |
|---|---|---|
| 2, security half | Strong | The pattern's premise and its instruments are what this half names |
| 2, collaboration half | Weak | No record states a credit, an incentive or a deliberation |
| 2, boundaries | Close in vocabulary, different in substance | TOPAK's boundaries are imposed by a promoting authority, not mutually respected among peers |
| 3 | Moderate | The pattern enforces an allocation of control and offers no evidence for choosing one |
| 4 | Indirect | The evidence is underwriting-grade, and it describes a deployment, not a lab |

### 2.1 Focus area 2, the security half

The premise is the fit. An agent is Byzantine at every deployment position, safety does not depend on what a model
means or intends, and models stay out of the trusted computing base (ADR-0007; ToO §1). Against the text's list:

- **Mutual monitoring and cross-checking.** Observers are per cell (ADR-0038), every Run admit is coupled to a live
  one (ADR-0039), and findings may subtract authority and never add it (ToO §2.2).
- **Checks no one party controls.** Promotion takes a unanimous quorum (ADR-0024), and the control plane is ordered
  by consensus.
- **Scalable verification and proof.** TLC checks mutations and witnesses, TLAPS proves the invariants (ADR-0046),
  and Lean 4 proves them again by a second route (ADR-0053). The floor runs on a verified evaluator (ADR-0030).

Three things qualify it, and a reviewer reading the corpus would find each.

1. **Collusion is declared open.** ADR-0039 §5: coupling "cannot separate an honest Observer from a colluding one",
   and the statement must say "detection fails open against a colluding Observer". The request names collusion as
   the risk that makes this half necessary. SF-17 item 4 adds that the overlay's permitted channels carry it.
2. **The decentralization is in fault tolerance, not in governance.** One anchor issues the rules, one custodian
   ratifies (ADR-0029 §2), and the overlay's federation "models a tree with one root" (SF-17 item 1).
3. **Much of what would be cited is not in force.** Lineage independence (ADR-0035), the correlator (ADR-0051),
   workflows (ADR-0054, ADR-0055) and the whole command-chain overlay (ADR-0059 to ADR-0068) are Proposed.

### 2.2 Focus area 2, the collaboration half

Nothing in the corpus is a coordination protocol in the request's sense. Agents are principals confined to an
alphabet, seated by promotion, and are not parties with interests the design aggregates or trades. There is no
record on credit assignment, on incentives, or on deliberation among people. ADR-0054 and ADR-0055 state how work is
routed among cells; they say nothing about why a cell would cooperate, because the premise is that it need not.

The request says the best proposals "show how the two reinforce each other". TOPAK shows one side.

### 2.3 Focus area 2, boundaries as Schelling points

The vocabulary is close enough to be mistaken for the same thing. The corpus has a membrane (`Contain`, ToO §2), a
register of fourteen boundaries (`derived/topak-boundary-register-2026.09.13.md`), and a record that says effects
are boundary crossings, each authorized, ordered and auditable (ADR-0015).

The substance differs in who draws the boundary. In the request's foundation, parties with different minds converge
on boundaries to respect, and respect gives each a protected fallback. In TOPAK a boundary is drawn by a promotion
and enforced on a principal that is assumed not to respect it. The nearest thing to the request's idea is ADR-0065,
where stacks report to each other and "nothing a peer originates is ever an enabling condition": each stack's
authority is a boundary its peers cannot move. That record is Proposed, sits under one root, and gives a peer no
standing to refuse either (SF-17 item 3).

No record cites Critch, and no module states a boundary as something two roots agree on.

### 2.4 Focus area 3, Human Empowerment

The request names three cases where control is worth keeping: where it improves outcomes, where it is intrinsically
warranted, and "where relinquishing it is irreversible". The third is ADR-0066: an irreversible effect is a
person's, reached only through a `release` seat a person holds. It is Proposed, and it says of itself that "HITL is
a key and not a judgment" unless the person can see what the act requires.

Around it:

- **A person can always subtract.** An operator is a principal and can deny without a lease (ADR-0050, provisional).
- **Hollow oversight, on the automated side.** The three gates, totality, non-vacuity and discrimination (ToO §2.2),
  exist to catch a check that passes while checking nothing, which is the Moon & Varshney failure the narrative
  builds on (ToO §1).
- **Hollow oversight, on the human side, is a finding and not a mechanism.** SF-15: no record states what a person
  at a release seat is shown, who takes over, or what a hand-back carries. Its Citibank–Revlon reading is the
  request's "oversight theatre" exactly: three approvals, every property holding, and the wrong payment.

What the request asks for first is evidence and decision rules for *when* to keep control. The corpus has
mechanism for holding an allocation once someone has chosen it. Its nearest thing to evidence is the scenario
inventory, forty-five episodes read against the records, which was not built as an evidence base for this question.

### 2.5 Focus area 4, AI Insurance & Open Governance

The corpus says nothing about insurance, liability or pricing. What it has is the material an assessor outside a
deployment would want:

- a residual-risk statement written "for an acquirer or a user" (`derived/topak-residual-risk-statement-2026.11.11.md`);
- a trusted base declared row by row, each with its failure direction (ADR-0045);
- a deployment declaration and conformance checklist (the Adopter's Guide; ADR-0058, Proposed);
- authority facts that survive erasure and break-glass (ADR-0028), kept apart from cognitive payloads (ADR-0004),
  which is one answer to assessing "without leaking lab secrets";
- digest manifests and hash-chained traces a second party can replay.

Two things keep the fit indirect. The request's subject is a frontier lab's risk, and the corpus's is one
deployment's. And insurance prices harm to third parties, where the corpus prices none: "what a stop does to the
world is priced nowhere" (SF-1), impacts on people are marked out of scope in the 2026.10.09 external alignment, and
"the people an effect lands on have no standing in the pattern" (SF-26).

---

## 3. Fit by evaluation criterion

| Criterion | Reading | Basis |
|---|---|---|
| Open source required | **Met** | Apache-2.0 for code, specifications, policies and tooling; CC BY 4.0 for documentation (`README.md`) |
| AI-first work | **Strong, and double-edged** | Assisted drafting "is now the rule and not the exception" (ToO §0); the 11.11 review ran thirteen readers, fourteen verifiers and ten graders. The same review calls this independence of context, not of lineage |
| High-risk, high-reward | **Fits** | A formally stated pattern for agent containment that assumes no alignment; unproven outside its authors' hands |
| Alignment with the focus area | **Partial** | §2 |
| Impact on existential risk | **Indirect** | The pattern bounds what agents do inside a deployment. It does not address the many-lab, many-government world the request describes |
| Feasibility in one to three years | **At risk** | "It is not a deployable system" (`README.md`); `Contained` is unreachable at every rung (ToO §2.3); "the corpus can now be extended faster than it can be kept true" (CR-61) |
| Capability to execute | **The weakest point** | G11's A2.5 line: bootstrap reviewer engaged, "None"; last completed review pass, "None". Twenty-nine accepted records wait for a confirmation quorum that does not exist, and CR-44 finds the count understated |

What holds on the other side of the last two rows was run and not asserted: at the 11.11 review every dated manifest
verified, all 321 TLC rows of the overlay regenerated, and the reference's 155 tests passed.

The request's terms raise two things this document cannot answer: whether the custodian would work in person at the
funder's Nodes, and under what legal form an application would be made.

---

## 4. Where the frames diverge

These are differences of premise. No revision of a record removes them, and a proposal would have to state them.

1. **Trust.** The request wants structures that let agents cooperate and keep cooperation beneficial. TOPAK's
   premise is that safety cannot depend on what a model means or intends. It is not an alignment method; it is
   containment that holds whether or not alignment does.
2. **Authority.** The request wants "checks and balances that no one party controls". TOPAK replicates its control
   plane and roots its governance: an anchor, a custodian, a tree of planes each seated by its parent (ADR-0059).
3. **Collusion.** The request treats it as the central hazard of cooperation. The corpus treats it as the one case
   its detection does not cover, and says so on its residual-risk statement.
4. **Whose interests.** The request speaks for the people using AI and "the wider world". The corpus is written for
   a deployer and an acquirer, and SF-26 records that the people an effect lands on are seated nowhere.
5. **Unit of analysis.** The request looks at labs, insurers and governments. The architecture description's system
   context is "one deployment".
6. **Kind of evidence.** The request asks for evidence, working tools and demonstrations among a community in the
   same rooms. The corpus offers proofs, records and a status vocabulary, all of it one hand's.
7. **Application.** The newest ten records are a command-chain overlay, worked as a reconnaissance fleet with rules
   of engagement (ADR-0067; `derived/recon-fleet-7-2026.11.10/`). A funder of existential-risk reduction may read
   that as military-adjacent. ADR-0066, which keeps every irreversible effect with a person, is the same overlay's
   answer, and is the record focus area 3 would cite.

---

## 5. What a proposal could be

Suggested, in the order this reading would weigh them. None is made, and each is the custodian's to decide.

1. **Before any submission, a reader who is not the author.** It is item one of
   `derived/topak-gaps-prioritization-2026.11.11.md` for the corpus's own reasons, and it is the fact that would
   cost most under "capability to execute". A grant could fund it directly: a paid independent confirmation pass is
   itself a deliverable under "distributed oversight ... and verification projects".
2. **Focus area 2, one narrow deliverable: a boundary two roots agree on.** State, in TLA+ and Lean, peer stacks
   under different roots that hold each other's authority as a boundary neither can move, starting from ADR-0065 and
   SF-17's `proposed:PeerFederation`. This is the request's third example deliverable, "protocols that build on the
   concept of boundaries as Schelling points", and it works on the two things §2.1 lists as qualifications instead
   of leaving them for a reviewer to find. SF-17's `proposed:CoordinationFold` and `proposed:RepeatedPairing` are
   the collusion half.
3. **Focus area 3, secondary: a "when to defer control" rule with a demonstration.** ADR-0066's effect classes as
   the decision rule, SF-15's four gaps as the hollow-oversight work, the scenario inventory as the cases, and the
   use-case simulator as the working demonstration. The grant is smaller here.
4. **Focus area 4 is not recommended as a lead.** The deployment declaration and residual-risk statement could be
   offered as an assessor's input format, and that is a contribution to someone else's proposal more than a
   proposal.

A proposal under 2 or 3 would rest on Proposed records. It should say so in the corpus's own status words.

---

## 6. What this document does not say

- It does not say the request's text is current or complete. It is the pasted text; its publisher's page was not
  read, and section I was not seen.
- It does not assess the custodian's qualifications, budget or availability, which the criteria ask about and the
  tree does not hold.
- It does not re-grade any finding. CR- and SF- identifiers are cited as their documents state them.
- It did not read ADR-0059 to ADR-0069 whole. What it says of them is from their titles, the index, ADR-0065 §1,
  ADR-0068's TM11 row and the two finding documents.
- It makes no claim about what the funder would decide.

## Sources

- `README.md`; `narrative/theory-of-operation.md` §0 to §2.3; `narrative/architecture-description.md` §3
- `decisions/README.md`; `decisions/ADR-0039.md` §5; `decisions/ADR-0050.md`; `decisions/ADR-0065.md` §1;
  `decisions/ADR-0068.md`
- `checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md`, the ADR-0029 A2.5 line
- `derived/topak-critical-review-2026.11.11.md` §0, CR-40 to CR-61 by headline
- `derived/scenarios-2026.11.12/FINDINGS_TOPAK.md`: SF-1, SF-4, SF-15, SF-17, SF-26
- `derived/topak-boundary-register-2026.09.13.md`; `derived/topak-gaps-prioritization-2026.11.11.md`;
  `derived/recon-fleet-7-2026.11.10/README.md`
- Foresight Institute, "II. Coordination and accountability — Request for Proposals", focus areas 2 to 4 and FAQ, as
  pasted by the custodian on 2026.11.13
