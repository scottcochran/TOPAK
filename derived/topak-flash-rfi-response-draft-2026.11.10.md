# TOPAK — Draft response to DARPA-SN-27-17, the FLASH request for information

> Submit TOPAK?
>
> Draft the five pages assume 0035, 0054 will be ratified and that layered c2 cp will have ADR, modelled, and
> checked.
>
> Assume 0055 ratified too, add the mesh to §1. Also, assume any pending lineage ADRs are ratified.

(The custodian's three prompts of 2026.11.10, the third with its line break closed. "Layered c2 cp" is the
command-chain proposal's tree of control planes.)

**2026.11.10** · derived · **a draft, not sent, and not true of the tree it is committed to** · prepared by Claude at
the custodian's request · **revised once, on the day it was written and before anything cited it**, to take in the
third prompt; the first draft is commit `1f78b7f`, and the last paragraph before the response lists what changed ·
read against the tree at `e79ae6d`, Genesis Checkpoint G11
(`checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md`), Theory of Operation revision 15
(`narrative/theory-of-operation.md`, cited below as ToO), the command-chain proposal
(`derived/topak-federated-c2-design-proposal-2026.11.10.md`) and its two readings, cited as the NATO reading
(`derived/topak-federated-c2-proposal-assessment-2026.11.10.md`) and the swarm reading
(`derived/topak-federated-c2-swarm-trust-assessment-2026.11.10.md`)

**What this is.** The five-page narrative that DARPA Special Notice DARPA-SN-27-17 (Formal Learning and Abstractions
for System Heterogeneity, issued 2026.11.03) encourages, written as of the day it would be sent. The notice is a
request for information, not a solicitation, and says a proposal sent against it is disregarded, so this is an
answer to its two questions and asks for nothing. Responses are due **2026.11.30 at 5:00 PM Eastern**, by email to
FLASH@darpa.mil, as an unprotected Word or PDF file on letter paper with 1-inch margins and type no smaller than 12
point (8 or 10 point allowed in tables), with the respondent's organization and a technical contact's name, email
address and phone number.

**It is written on five assumptions the custodian set, and none holds at this commit.**

1. **ADR-0035 is ratified.** It is Proposed. Its ratification condition (§8) includes a review of the bounded-share
   construction by someone other than its author.
2. **ADR-0054 is ratified**, and with it the ten dependent amendments G11 §1.1 lists as pending. It is Proposed.
3. **ADR-0055 is ratified.** It is Proposed. Its condition (§11) asks that ADR-0054 be ratified first or with it and
   that its dependent entries be drafted, and G11 §1.1 says they are not.
4. **Every pending lineage text is ratified.** No record but ADR-0035 is pending on lineage, so this is read as
   three things. ADR-0035 with its R8, which alternates lineages on a workflow's clear edges at its tally. The
   two-colour check ADR-0055 §11 owes to ADR-0035 §5, which is not drafted. And ADR-0024 A2.2, an independent veto
   seat must be seated, which was ratified in Batch 15 and waits on ADR-0035. With these D-0054-1 stops being every
   deployment's declaration. It is not read as covering the supersession of ADR-0017's ordering-primacy clause,
   which is unwritten, or ADR-0036, which is about confinement and whose launcher a projected lineage needs.
5. **The tree of control planes has a decision record, is modelled, and is checked.** Today it is a proposal in
   which "nothing here is a decision, and nothing here is modelled, checked, built or reviewed". The response
   writes the record as **[ADR-0059]** and the modules as `Federation`, `Intent` and `Disconnected`, the names the
   proposal's §10 gives. It claims *checked* and never *proved*, and it does not say the record is ratified.

**What to check before it is sent.** Each row is a sentence of the response that is false today, or that a later
change could make false.

| In the response | It rests on | Check |
|---|---|---|
| §1 (i), first paragraph, the design as described | Assumption 5 | The record's number and status. That the record as written still has a charter with a closed schema, an intent boundary, an autonomous plane, a governor and three states |
| §1 (i), second paragraph; §1 (iv), *Free* and *Where diversity stops*; §1 (v), third row; §2.3, *Many agents*; §2.4, "meshes" | Assumption 3 | The status of ADR-0055. Its seven properties hold today at one mesh of three nodes and a budget of six (`spec/Mesh-results-2026.10.07.txt`); fan-out, scoped joins, pools and proofs are not met (ADR-0055 §11) |
| §1 (i), "the vote that admits a mesh at the intent boundary" and "goes on running the mesh"; §1 (ii), the partitioned plane | Assumption 5, from the proposal's §8, §4.1 and TM6 | That the record still promotes the mesh at the intent boundary, and still asks Byzantine agreement of an autonomous plane's replicas |
| §1 (iv), *Required*, "a mesh is admitted only if those edges can be two-coloured" | Assumptions 1, 3 and 4 | That ADR-0035 §5 carries the check. It is the gate's and is static: `spec/Mesh.tla` checks its runtime consequence, `ClearHopsAlternate`, and not the check |
| §1 (v), every other invariant row; §2.4, the second row; §3, "checked at small constants" | Assumption 5 | That each row names a property the cut results file shows holding, with a mutation that breaks it. The modules' names and the results file's date |
| §1 (v), "a revocation takes hold within" | Assumption 5, and the NATO reading's F1 | That the record gives every interval an origin the link adversary cannot move. Until it does, a withheld intent delivered late defeats this row |
| §1 (iv), "one commander varies an intent's area, budget and expiry" | The proposal's question 4, answered as recommended | That an intent is bounded by the promoted seating and not by the last intent |
| §1 (iv), *Limitations*, "a false finding stops a vehicle and nobody restores it" | The swarm reading's Z3 | Whether the record now says what a finding does to a vehicle in flight, and whether its cell may be leased again under the same intent |
| §2.1, measure 1; §2.3, "at least one veto seat is of lineage independent of the author's" | Assumptions 1 and 4 | The status of ADR-0035 and of ADR-0024 A2.2's condition, and whether the θ values are still placeholders |
| §2.3, *Many agents*, the workflow | Assumption 2 | The status of ADR-0054 and of ADR-0041 A4 |
| §2.1, **[43]** and **[34]**; §2.4, **[24]** and **[21]**; "sixteen modules"; the summary's "nearly sixty" | The tree at `e79ae6d` | Recount at the cut. `spec/theorem-premise-binding.json` gives the first pair; ToO §11.1 item 7 and §7.11 the others |
| §3, "no agent is yet confined" | G11 §8. ADR-0035 in force supplies the fourth conjunct of `Contained`, and every real guest's profile still fails P3 | That this is still so |
| §3, "it counts as declared" | ADR-0035 §2 and §8: the trainer runs in the node's toolhost, outside the guest | That no in-guest trainer image exists. If one does, strike the sentence |

**Placeholders** are in bold square brackets: the respondent's name as an organization, the contact's email address
and phone number, the date, the record's number, the results file's date and the four counts.

**What in it is not from the corpus.** DoD Directive 3000.09 and Knight and Leveson's 1986 experiment are recalled,
not sourced; the corpus names the second only in passing. §1 (iii) is the drafter's general account of current
practice, not a survey. §1 (iv)'s three positions (free, priced, required) and its paragraph on dynamic
heterogeneity are this draft's reading of the records for the notice's question: no record says a variant is issued
with an intent. *Where diversity stops* is the draft's heading over ADR-0055 §5's argument. §2.1's fourth measure
and its suggested definition of equivalence are proposals made here, and the text says so. The account of Moon and
Varshney is ToO §1's and §11.1's.

**What it leaves out.** ADR-0057 and ADR-0058 (the specification graph), Proposed. The proposal's release seat by
name, its floor stage, and five of its eleven adversaries as rows of the table, three of which are named under
*Limitations*. The NATO reading's N1 to N3 and F2 to F4, except that F3, a captured vehicle discloses the rules, is
used as an argument for variation. The swarm reading's Z1, Z2 and Z4: the log between vehicles has no stated rate,
a vehicle found captured goes on voting in its plane, and an Observer on another vehicle can accuse or vanish.

**Status words.** ToO A8 requires a publication to cite confirmation-required records as author-ratified, and ToO §0
requires "author-ratified, provisional" of anything resting on ADR-0050 or ADR-0052. §3 of the response says both
once, for everything in it.

**Format.** The response is everything between the two marker comments below. Rendered on 2026.11.10 through pandoc
and LibreOffice at 12-point Times-metric type, 10 point in tables, on letter paper with 1-inch margins, it is five
pages with about six lines to spare on the fifth. It has no header or footer, so nothing sits in a margin. The Word
and PDF renderings are not tracked (`.gitignore` excludes PDFs); the placeholders are highlighted in both.

**Changes from the first draft** (`1f78b7f`), all for the third prompt.

- **Assumptions 3 and 4 are new**, and the check table gains the rows that rest on them.
- **§1 (i) gains its second paragraph**, the mesh. **§1 (ii) gains the partitioned plane**, and its supply-chain row
  now states a residual where it pointed at a list §2.1 does not give.
- **§1 (iv)** restates *Free* and *Required* for a mesh, and gains *Where diversity stops* and a limitation from the
  swarm reading's Z3.
- **§1 (v)** gains a row for the mesh, joins an intent's values to the mission's row, and adds terminal behaviour per
  vehicle class as a degree of freedom.
- **§2.3 and §2.4 name the mesh. §3 says a lineage record at the reference counts as declared.**
- **Cut, to stay at five pages:** the notice's name from the title; from §2.1, the policy floor's three gates and "no
  weaker version of a theorem"; from §2.4, the row for the method, which §2.2 names, and the trusted-base table;
  from §3, "no vehicle exists" and the closing invitation; and words in the summary, §1 (iii), §2.2 and §2.3.
- **This branch now holds main at `e79ae6d`**, merged for the swarm reading.

---

<!-- BEGIN RESPONSE -->

# Response to DARPA-SN-27-17, the FLASH Request for Information

**TOPAK: an authority layer that holds still while the system behind it varies**

| | |
|---|---|
| **Respondent** | **[William Scott Cochran, an individual respondent, or an organization's name]** |
| **Technical contact** | William Scott Cochran · **[email address]** · **[phone number]** |
| **Marking** | UNCLASSIFIED. No proprietary information. **[2026.11.30]** |
| **Source material** | github.com/scottcochran/TOPAK: Apache-2.0 code and specifications, CC BY 4.0 documents |

**Summary.** TOPAK is an open design corpus for a control plane that governs AI agents: nearly sixty decision
records (ADRs), a TLA+ layer that is model-checked and in part proved, a draft policy *floor* in Cedar (the standing
rules that no later policy can weaken), and a Rust reference of the path that admits every effect an agent causes. Its premise is that an agent is Byzantine wherever
it sits. No guarantee rests on what a model means or intends, and each is stated against the agent's *action
alphabet*, the closed set of typed actions it can request. Three consequences are offered to FLASH. An invariant stated against an alphabet is untouched by variation behind it, so a new variant needs no new
proof. Where variation does reach the trusted part, instances are related by a computed inventory of theorems kept
and lost, in place of functional equivalence. And generated variants share their generator, so diversity is a
premise to be checked, and there is a rule for checking it. Section 1 works them on one application. Section 3
says how far each claim is checked: this is one person's design, not a fielded system.

## 1. Application: authority over uncrewed vehicles on a contested link (RFI item 1)

**(i) Domain.** The target is the authority layer of a fleet of uncrewed vehicles under a chain of command: who may
cause which effect, for how long, under whose rules, and what record it leaves. It is not the design of a vehicle, a
sensor or an effector. The design (**[ADR-0059]**) is a tree of control planes. A *plane* is one replicated log with
one set of rules in force. Each plane is seated by a vote at the plane above it, under a *charter* with a closed
schema, and can hand down only what it was handed, or less. The last plane where a person commands is the *intent
boundary*. Its commander issues *intents*: a task, bounds, a budget and an expiry. Below it one *autonomous plane*
runs among each group of vehicles, with no person seated at it and no path that adds authority. Each vehicle carries
a small trusted *governor* between its autonomy software, the *stack*, and its actuators, and every action carries a
*lease*, a credential for one round whose fields bound what its holder may request.

What an autonomous plane runs is a *mesh* (ADR-0055): the mission's plan as a graph that may loop, each node one
vehicle's stack, run a round at a time. The vote that admits a mesh at the intent boundary fixes an *activation budget*, the
most rounds it may ever grant, so the number of turns is decided in the field and the end is still bounded. Vehicles
never address each other. The plane's log is the bus, and one vehicle's output reaches another only as labelled
input. A vehicle is *linked* when it reaches the intent boundary, *meshed* when it reaches only a quorum of its own
plane, which goes on running the mesh, and *alone* when it reaches neither.

**(ii) Rationale and threat.** A fleet is bought as one design. Every vehicle runs the same stack under the same
mission rules, so an exploit developed against one vehicle, a trigger planted in one model, or the rules read out of
one captured vehicle is good against all of them. The adversary contests the link, captures vehicles, and can now
develop exploits with agents faster than a fleet is patched. Through all of it people must keep judgment over
irreversible effects (DoD Directive 3000.09), including while the link is jammed.

| Adversary | What bounds it | What is left |
|---|---|---|
| The stack: Byzantine, may request anything | The governor, the alphabet and the lease's bounds | Whatever the bounds allow, which a quorum voted acceptable |
| The link: jams, delays, replays, injects | Quorum certificates stop forgery, epoch numbers stop replay, and two declared time bounds cap delay | It can always deny, and denial blocks every irreversible effect |
| A captured vehicle | Its lease's bounds and remaining life | It discloses the rules and routes the vehicle holds |
| A captured plane | Its charter, checked by every governor, and its expiry | Everything inside the current intent, until that expires |
| A partitioned plane | Agreement needs more than two thirds of its replicas, so at most one part goes on running the mesh | The vehicles of every other part are alone |
| The supply chain: weights, tools, rules | Admission by vote on a digest; lineage independence (§2.1) | What the rule cannot see: unlabelled model text, shared annotators |

**(iii) State of the art and its limits.** Current practice hardens one instance: signed mission loads,
authenticated links, geofences, and run-time assurance in which a verified monitor overrides an unverified
controller. Three limits remain. The fleet is a monoculture, so what an adversary learns is durable and transfers.
Authority and its revocation ride a link the adversary can cut, and what a vehicle does without it is designed per
platform, not derived from who authorized what. Assurance is argued per configuration, largely by test, so each
variant is a new certification. N-version programming assumed that independently developed versions fail
independently. Knight and Leveson (1986) refuted it by experiment, and versions written by coding agents reopen the
question (Ron, Baudry and Monperrus, arXiv:2606.20158).

**(iv) What heterogeneity and the FLASH thrusts add.** The design puts every part of the system in one of three
positions with respect to variation.

- *Free.* No theorem rests on the stack, so any generated planner, perception chain or model may be admitted to any
  vehicle, by a vote on its digest, and no proof reopens. A mission's rules are a bundle that can only refuse. Its
  mesh may differ in graph, loops, seatings and budget, and its orchestrator chooses only among steps the mechanism
  has already enabled and keeps no state between rounds (ADR-0054, ADR-0055). Within what a quorum voted, one
  commander varies an intent's area, budget and expiry by one signed act.
- *Priced.* The governor, the consensus protocol, the policy evaluator and the clocks are trust roots. Changing one
  is a declared variation, and a tool computes which theorems the instance keeps (§2.1).
- *Required.* Each stack is coupled to an Observer, a second agent that reads its record and may deny and never
  admit. The two must be of independent lineage. So must any two stacks where one reads the other's output in the
  clear: a mesh is admitted only if those edges can be two-coloured by the deployment's two lineages (ADR-0035,
  ADR-0055).

*Dynamic* heterogeneity then bounds what adversary knowledge is worth. An intent lives at most `T_intent`, and a
vehicle alone acts for at most `T_alone`, so a variant issued with an intent is exposed for a declared time. A
captured vehicle discloses its own plane's rules. Where each plane runs a different variant under the same charter,
it discloses one instance.

*Where diversity stops.* Alternation keeps a trigger from crossing one hop into its own lineage, and a loop offers
the second hop on every turn. Labels bound what alternation cannot: once a round on a loop reads untrusted content
in the clear, every later round on that loop is labelled untrusted and its outward steps stay closed.

*Assumptions.* The governor is the only path to the actuators. Each clock runs slow by at most a declared fraction.
Fewer than a third of an exposed plane's replicas are captured. Effects are declared reversible or irreversible as
they are. *Limitations.* Nothing here bounds a deceived navigation source, a deceived person or a colluding
Observer. On a plane with no person a false finding stops a vehicle and nobody restores it, so the false-finding
rate of whatever watches is an availability parameter, to be declared. The governor and the floor are the same on every vehicle by design: that common mode is declared and kept
small, not removed. *Evaluation.* The experiments of §2.1, with exploit-developing agents seated as stacks.

**(v) Invariants and degrees of freedom.** Each invariant is a property of the model, checked with a seeded break
that must violate it (§2.1, §3). No performance property is invariant: time bounds and budgets are declared per
deployment.

| Invariant across every instance | Kind | Free to vary |
|---|---|---|
| Authority only narrows down the tree, and a captured plane issues nothing the root did not vote | Security | The stack on each vehicle: models, planner, perception |
| Every effect has an authorizing act ordered beforehand at a plane where a person commands | Functional | A mission's rules, and an intent's values inside what was voted |
| A mesh grants at most the rounds its admission voted, and a finding against one round closes every step downstream of it | Functional | A mesh's graph, loops, seatings and budget |
| An irreversible effect is one person's signed act, used once, and no agent's alphabet reaches it | Safety | The tree: planes, replicas per plane, quorum rule |
| No effect after a lease's life, and a revocation takes hold within `T_intent`, or `T_alone` for a vehicle alone | Timing | The product in each role (consensus, policy evaluator, transport), against a stated obligation |
| When authority expires a vehicle does only the terminal behaviour fixed when it was seated | Safety | Terminal behaviour per vehicle class, among those voted |
| One closed schema for charter and lease, one floor, and typed tool interfaces | Interoperability | Declared values: time bounds, budgets, custody of the root key |

## 2. Framework, architecture and evaluation (RFI item 2)

**2.1 Metrics, invariance and experiments (i).** *Invariance as an inventory.* Instances with different failure
modes are not behaviourally equivalent, and are not meant to be. What must be equal is what is guaranteed. In the
corpus a deployment is a tuple of positions on a lattice of named parameters, and the theorems are stated at its
maximum, the *archetype* (ADR-0023). Moving a parameter falsifies named premises, and each theorem resting on one is
absent for that instance. A table binds **[43]** theorems to **[34]**
premises, and a tool computes an instance's inventory from its declaration. Building it produced three findings
FLASH will meet.

- Composition is not monotone. Two variations can jointly void a theorem that neither voids alone, so an instance
  that moves two parameters declares the difference.
- A variation can void no theorem and still change who is trusted. The declaration lists those changes beside the
  theorems.
- A variant with a capability the maximum lacks is not a variant. It shows that the specification is incomplete.

The suggestion to FLASH is to call two generated instances equivalent when they hold the same inventory on the same
trusted base, and otherwise to require the generator to state what each instance loses.

*Collateral.* An instance's assurance artifact is its declaration: the parameters it moved, the premises those
moves falsify, the theorems voided and the trust roots it stands on. One binding computes it for every instance.

*Heterogeneity, measured against what an adversary can reuse.* Four measures, the cheapest first.

1. *Lineage independence* (ADR-0035). A model's lineage record is computed from the build log, not written by
   whoever trained it. Two lineages are independent only if five exclusions hold: different weight roots, no shared
   generator of training content, corpus overlap under a threshold, different architecture family and tokenizer, and
   no shared curator. Each share is an upper bound, so uncertainty can only fail a pair, and the relation is not
   transitive, so every pair is checked. In a rehearsal on public corpora the overlap measure gave 1.0 for a
   filtered crawl inside its parent and 0 against public-domain books.
2. *Shared trust roots.* The trusted base is a table of rows, each classed by whether its failure can add authority
   (ADR-0045). The rows two instances share are their common-mode surface, and variation elsewhere does not shrink
   it.
3. *Correlated misses.* On planted defects held out from both lineages, a pair fails when its joint miss rate
   exceeds a set multiple of the product of the two rates. A failure removes the pair. A pass grants nothing.
4. *Transfer under adaptive attack* (proposed here, and not run). Seat exploit-developing agents as stacks, with the
   alphabet and the specification in hand. Count effects outside the lease's bounds: the design says there are none,
   and one counterexample refutes it. Of attacks that succeed inside the bounds on one instance, measure the share
   that succeed unchanged on another, and how long they stay useful against reissued variants.

*Vacuity.* A generator can satisfy a specification that constrains nothing. Moon and Varshney (arXiv:2605.09045)
report that failure with every gate green. Each property in the corpus therefore ships with a *mutation*, a seeded
break that the check must catch and that breaks nothing else, and a *witness* that the behaviour it constrains is
reachable (ADR-0046).

**2.2 Induction and deduction (ii).** The corpus was produced by the loop the notice describes. An AI assistant
drafts a record, a module, its mutations and its proof. The oracles are the TLC model checker, the TLA+ Proof System
(a solver's answer counts only with a certificate a proof checker accepts) and the Lean 4 kernel. One person
decides. Four lessons:

- *Counterexamples change the design.* The first check of the credential model showed that renewal which only
  narrows guarantees nothing while a holder may take a fresh grant. A soundness claim in the lineage rule was false,
  and 2,000 random trials showed it.
- *The oracle has a trusted base.* This work found two cases in which the prover's translation of an obligation is
  unsound, reported upstream as tlaplus/tlapm issues 309 and 310. A second method re-proves sixteen modules in Lean,
  and three of those encodings are compared with the model checker's state graphs.
- *Evidence is regenerated, never edited.* Each results file names the digests of module, checker and prover, a
  script reports what is stale, and claims use fixed words: *checked*, *proved*, *certified*.
- *Structure makes induction tractable.* Properties are local: a flag the violating action would set, shallow
  actions over finite domains, one constant that selects a mutation. The method is packaged as an agent skill.

**2.3 Agent architectures (iii).** A generated design entering service is a grant of authority, and the architecture
treats it as one. The Byzantine threat sits at design time, because design agents write the specifications and
policies the running system is later judged against.

- *One agent.* A design agent has six typed actions (read from a pinned corpus, draft, invoke an allowlisted tool,
  emit, submit, vote), no shell and no network, and an Observer whose findings subtract authority and never add it.
- *Admission.* An artifact leaves design only by *promotion*: a vote on its digest in which the author cannot vote
  and at least one veto seat is of lineage independent of the author's.
- *Many agents.* A workflow is a promoted graph (ADR-0054), and a mesh is one that may loop under a voted budget
  (ADR-0055). Its promotion seats every agent in it, and no agent grants another. The mechanism routes on typed attributes. An orchestrating agent chooses only among steps whose
  guards already hold, so it affects how good the work is and never whether it is safe.

**2.4 Reusable libraries (iv).** All of it is public under the licences above.

| Library | Form | Standing |
|---|---|---|
| Credential, seats, confinement attestation, Observer coupling, policy composition, emergency seating, workflows, meshes | TLA+ modules with mutations and witnesses; **[24]** proof modules, about 3,000 obligations | Checked. Proved where a proof module exists; **[21]** certify |
| Layered planes: `Federation`, `Intent`, `Disconnected` | TLA+ modules, by the same method | Checked **[date]**. Not proved |
| A second route | Lean 4 encodings of sixteen modules and of the admit decision | Proved in Lean, of the encodings |
| Policy floor | Cedar, with schema, tests and non-vacuity gates | Draft |
| Theorem-to-premise binding | JSON, with the inventory tool | Kept by hand |
| Lineage gate | Log projector and exclusion-rule suite | Rehearsed |

## 3. Standing of these claims

Everything above, this response included, is the work of one person with an AI assistant, and no reader independent
of the author has reviewed any of it. Each decision record is ratified by its author alone and should be read as
*author-ratified*; two that §1 leans on are also provisional. The theorems are of the design. No refinement to the
running code exists: the reference is tied to the model by replayed traces and by two functions proved in Lean. At
the reference no agent is yet confined, and one that can reach a shell is outside every guarantee. A lineage record
there is computed from the log, but training runs outside confinement, so it counts as declared. The layered-plane
design is checked at small constants, not proved and not built. Its time bounds are placeholders. The prover's two unsound cases are kept out of the proofs by a writing rule and a scan, not by a
check.

<!-- END RESPONSE -->
