# TOPAK mapped to TOGAF: a reference architecture a TOGAF practice would consume, and where the two do not meet

> explain TOGAF

> how does TOPAK map to TOGAF

> write that up as a derived doc

(The custodian's prompts of 2026.11.27, in order. The first two were answered in the session, and this document
is the third.)

**2026.11.27** · derived · a reading, not a record · prepared by Claude at the custodian's request · basis: the tree
at `231ca68` (`main` after pull request #109), with `README.md`, the Adopter's Guide whole
(`ADOPTERS_GUIDE_README.md`, a draft of 2026.10.09 against G11) and the Theory of Operation revision 16, §1, §8 and
§9 (`narrative/theory-of-operation.md`); no decision record was opened, and every record cited is cited as the
guide or the narrative cites it · TOGAF from general knowledge, with what could be confirmed on 2026.11.27 stated
in §1; **the TOGAF Standard itself was not read** · nothing was run

Nothing here is ratified, and this document proposes no decision text. The corpus does not mention TOGAF, on
`main` or on any branch, so every row below is this document's reading. Each lead in §8 is for the custodian, and
no entry is made.

---

## 0. Verdict

1. **The two are different kinds of thing.** TOGAF is a method for running an enterprise architecture practice.
   TOPAK is one architecture pattern. So TOPAK maps into TOGAF as something a practice consumes, and not as a
   rival or a profile of it. §2.
2. **The closest fit is the building-block split.** TOGAF separates what a block must do from the product that
   does it, and TOPAK's name is built on that separation: the letters name roles, not products. §3.
3. **The second fit is governance, and TOPAK's is the stricter.** A deployment's declaration and conformance
   checklist stand where TOGAF puts the architecture contract and the compliance review, and the promotion
   pipeline stands where TOGAF puts implementation governance. In TOPAK a gap from the reference is declared and
   costs named theorems. It is not graded and it is not waived. §5.
4. **TOPAK covers two of TOGAF's four domains well and two thinly.** Application and technology are its subject.
   Data is covered where the record is concerned. Business is covered only where a person holds a seat. §4.
5. **Each has a large part with no counterpart in the other.** TOGAF has nothing like a trusted base, an adversary
   or a theorem inventory. TOPAK has nothing like a business architecture, a portfolio or a migration plan. §6.
6. **Three statements of the session's answer are corrected and one is narrowed.** §7.

---

## 1. What was confirmed about TOGAF, and what was not

The Open Group's online text of the standard sits behind a sign-in, and a fetch agent was turned away from it. Two
public pages were read through the agent.

| Statement | Basis |
|---|---|
| The current edition is "The TOGAF® Standard, 10th Edition", divided into the TOGAF Fundamental Content and the TOGAF Series Guides | The Open Group's public TOGAF page |
| First published 1995, based on the US Department of Defense's TAFIM; the 10th Edition launched 2022.04.25 | Wikipedia's TOGAF article, as last edited 2026.06.24: a secondary source |
| Four architecture domains: business, data, applications, technology | The same article |
| The Architecture Development Method is the core, iterative and cyclic, with each step checked against requirements | The same article |
| The Enterprise Continuum classifies assets from generic foundation architectures to organization-specific ones; the Solutions Continuum defines reusable Solution Building Blocks | The same article |

Everything else this document says about TOGAF is from general knowledge and was confirmed against nothing: the
names of the ADM's phases, the definition of an Architecture Building Block, the stages of the Architecture
Continuum by name, the parts of the Architecture Repository, the Architecture Board, the architecture contract,
the compliance review and its named levels, dispensations, the named deliverables, and the Series Guide on risk
and security. A reader with the standard open should check each against it (L-1).

---

## 2. Where TOPAK sits

A TOGAF practice keeps reusable architectures on a continuum from the generic to the organization-specific and
draws on them when it designs. TOPAK belongs on the generic side of that continuum, as a reference architecture
for one concern: agents and people acting through a control plane in which "policy can only refuse" (Adopter's
Guide §1).

Three of TOPAK's own statements fix the position.

- **The archetype is a reference point.** It is "the unique maximum of the parameter lattice: a reference point,
  not a shippable configuration", and "Nobody ships the archetype" (ToO §8.1). The narrative gives ISO 26262's
  safety element out of context as its precedent.
- **A deployment is derived from it by declaration.** "You do not install TOPAK; you **declare a position**
  against its archetype" (Adopter's Guide §1). That is the step TOGAF calls making an architecture
  organization-specific.
- **The guide's reader is a builder.** It addresses "a platform engineer, or the team of them" (Adopter's Guide
  §1), and not an enterprise architect. Nothing in the corpus is written for the person who runs the ADM.

One difference from TOGAF's continuum matters. TOGAF expects a generic architecture to be tailored in either
direction. TOPAK allows movement in one direction only: a deployment may drive named parameters to limiting
values, and a deployment that needs a capability the archetype lacks has found that "the archetype is incomplete"
(Adopter's Guide §2.1). It reports that as a finding and does not declare it as a variation.

---

## 3. Building blocks

In TOGAF an Architecture Building Block states a required capability, and a Solution Building Block is the product
or component chosen to supply it. TOPAK's five letters are stated the same way: "Each role carries a stated
obligation, and an instrument that meets it may be substituted" (ToO §1).

| Role, as an architecture building block | Instrument at the reference, as a solution building block |
|---|---|
| **T**: formal specification, model checking and proof | TLA+ and TLC, with Lean 4 as a second method |
| **O**: policy as code, a verified floor and a per-request bundle | Cedar for the floor, OPA with Rego for the bundle |
| **P**: consensus over the control plane | Multi-Paxos |
| **A**: agents, the principals doing the work | MCP-connected agents |
| **K**: event transport | Kafka |

The mapping holds one level down as well. The guide's fourteen integration points (§5) each name a boundary and
then the reference's instrument for it, for example "The agent front door (MCP at the reference)".

It is tighter than TOGAF's split in one respect. A role's obligation can exclude a product: the floor tier "needs
an evaluator with a mechanized semantics and decidable policy comparison, which Rego does not have and Cedar does"
(ToO §1). TOGAF leaves the fitness of a solution block to the practice.

---

## 4. The four domains

| TOGAF domain | Coverage | What TOPAK has there |
|---|---|---|
| **Business** | Thin | People as seat-holders: operators "as people, each with their own key", grant seats, an emergency seating for "one named person and one round" (Adopter's Guide §4.10, §4.11). A headcount for bootstrap of "no fewer than five humans" (ToO §9). The human budget `D`, which is "an organizational commitment and no term of the mechanism" (Adopter's Guide §7.9). No process model, no capability map, no strategy |
| **Data** | Partial | The record and its custody: a topic per principal per round as the unit of erasure, control-plane facts kept apart from payloads, a forensic floor of six non-erasable classes, labels on every delivered item (Adopter's Guide §3.5, §3.6, §3.8). No enterprise data model, and the archive itself is supplied by no record (§5.13) |
| **Application** | Strong | The admit path, the two policy tiers, the tool host, the promotion pipeline, the workflow engine (Adopter's Guide §5) |
| **Technology** | Strong | Replicas and consensus, the transport, the confinement rungs and their profiles, the attestation verifier, the launcher (Adopter's Guide §3.7, §4.4, §5.6 to §5.9) |

Security is a cross-cutting concern in TOGAF and is TOPAK's whole subject, so TOPAK does not sit inside one
domain. It cuts across the last two and reaches into the first two only where a guarantee needs it.

---

## 5. The method and its governance

TOPAK has no method for developing an enterprise's architecture. It meets the ADM as an input at some phases and
as a counterpart at two.

| ADM phase | Relation | What stands there in TOPAK |
|---|---|---|
| Preliminary | Input | The premise, adopted as principles: an agent "is Byzantine at every deployment position", and models "stay out of the trusted computing base" (ToO §1) |
| A. Architecture Vision | None | No stakeholder or vision material |
| B. Business Architecture | Input, thin | The seats a person must hold, and the staffing they imply (§4) |
| C. Information Systems Architectures | Input | The pattern as a reference model, with the guide's compartmentation and integration tables (§3, §5) |
| D. Technology Architecture | Input | The same, with the trusted base declared "row by row" (Adopter's Guide §4.1) |
| E. Opportunities and Solutions | Partial | The declaration is a gap analysis of a kind (§5.1 below). There are no work packages |
| F. Migration Planning | None | Migration between chains is one of the things "the deployment writes" (Adopter's Guide §5, §7.12) |
| G. Implementation Governance | Counterpart | The declaration, the conformance checklist and the promotion pipeline (§5.2 below) |
| H. Architecture Change Management | Counterpart, for the pattern | Ratification by numbered batch and the checkpoints with their debt ledger (ToO §9). This governs the corpus and not an adopter's enterprise |
| Requirements Management | Partial | The eighteen assumptions of use, A1 to A18 (Adopter's Guide §9.1) |

### 5.1 The declaration as a gap analysis

TOGAF's gap analysis sets a baseline beside a target and lists what must change. TOPAK's declaration sets the
archetype's value beside the deployed value, one row per parameter, and lists what is lost: "Premises falsified"
and "Theorems voided" (Adopter's Guide §2.2). The form is alike and the use is opposite. TOGAF's gap is a list of
work. TOPAK's is a list of guarantees the deployment does not hold, and "a declaration is **mandatory**;
mitigation is not."

### 5.2 Governance

| TOGAF concept | Closest in TOPAK | How it differs |
|---|---|---|
| Architecture contract | The deployment declaration (ADR-0023 §6, as the guide gives it in §2.2) | The declaration is read by a gate: a missing composition note "fails at the promotion gate". No file format or path is fixed yet (§2.2, *Where the declaration lives*) |
| Compliance review | The conformance checklist (Adopter's Guide §9) | It is filled in by the deployment. No reviewer is named for it |
| Levels of compliance | The theorem inventory | There are no levels. "A theorem is present in your inventory or absent from it. There is no 'weaker version'" (§2.1). A deployment's position is a tuple, one coordinate per parameter |
| Dispensation | A degeneracy declaration | A dispensation excuses a departure. A degeneracy records one and voids the theorems that rested on it |
| Implementation governance | The promotion pipeline: every artifact into Run passes a tally with "unanimity of the counted grant seats, author recusal" (Adopter's Guide §5.10) | It is a mechanism and not a review meeting, and it runs for every bundle, profile, Persona and workflow |
| Architecture Board | In genesis, the custodian alone, at custody (1, 0). After bootstrap, the anchor's key-holders and the grant seats (ToO §9) | TOGAF assumes a standing board. The corpus has one person today and says so: "A solo bootstrap is not a bootstrap" |

### 5.3 Artifacts

| TOGAF concept | Closest in TOPAK |
|---|---|
| Architecture Definition Document | The Theory of Operation |
| Architecture decisions and their log | The records in `decisions/`: forty-seven Accepted (genesis), one superseded and twenty-seven Proposed at G12 (ToO §9) |
| Architecture Repository | The corpus as a whole |
| Governance log | The checkpoints, the batches and the process logs |
| Reference library | `derived/`, and the reference implementation under `mechanism/` |
| Glossary | `narrative/glossary.md` |

---

## 6. What does not map

**TOPAK has and TOGAF, as far as this reading knows it, lacks:**

- A stated adversary. Every agent, model and Persona is treated as Byzantine.
- A trusted base declared row by row, each row classed by whether its failure can add authority (Adopter's Guide
  §4.1).
- Guarantees stated as theorems, with a rule for which ones a deployment keeps.
- A formal layer that is checked and partly proved, and a requirement that a role's instrument meet a stated
  obligation.
- A list of what the pattern will not do, kept apart from what is merely unbuilt (Adopter's Guide §8).

**TOGAF has and TOPAK lacks:**

- A business architecture, and any account of stakeholders, capabilities or value.
- A method that starts from where an enterprise is. TOPAK starts from the archetype.
- Portfolio, sequencing and migration planning.
- An organization for the practice: roles, skills, a board that meets.
- Breadth. TOGAF addresses a whole enterprise, and TOPAK addresses one control plane.

So a TOGAF practice adopting TOPAK would bring it in at phases C and D as a reference model, carry its assumptions
of use into requirements, and put its declaration under implementation governance. It would still owe everything
in the second list from its own practice.

---

## 7. Corrections to the session's answer

- **C-1. The Architecture Board.** The session mapped it to the genesis custodian. That holds in genesis only.
  After bootstrap the counterpart is the anchor's key-holders and the grant seats, at no fewer than five people
  (§5.2).
- **C-2. Gap analysis.** The session said TOPAK has no baseline-to-target gap analysis. It has a gap analysis of
  another kind, against the archetype, in the declaration (§5.1).
- **C-3. Implementation governance.** The session named the declaration and the conformance checklist and left
  out the promotion pipeline, which is the stronger counterpart. It also did not say that the checklist is
  self-assessed and that the declaration has no fixed format.
- **Narrowed: the session's account of TOGAF.** Both answers stated TOGAF's parts as fact. §1 says how little of
  that was confirmed. Two statements had no source at all when they were made: that TOGAF's common criticisms are
  weight and documentation, which the Wikipedia article does not report, and that its nearest security material
  is a guide on risk and security.

---

## 8. Leads for the custodian

- **L-1.** The TOGAF side rests on general knowledge. A reader with the standard could check §1's unconfirmed
  list in an hour, and §5.2's rows on compliance levels and dispensations are the ones most likely to move.
- **L-2.** The Adopter's Guide was read as the corpus's account of a deployment. It is a draft of 2026.10.09
  against G11, and G12 has since added twenty-two Proposed records. No decision record was opened for this
  document, so a mapping read from the records could differ.
- **L-3.** Whether the corpus should say where it sits against enterprise-architecture practice is the
  custodian's to decide. If it should, the narrative's §11 on external alignment is where the other alignments
  are kept.
- **L-4.** The guide addresses a platform engineer. If an enterprise architect is ever a reader, §4's thin rows
  are what that reader will ask for first: who holds which seat, and what it costs to staff.
