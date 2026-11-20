# TOPAK — Draft response to DARPA-SN-27-17, the FLASH request for information (2026.11.20)

> Submit TOPAK?
>
> Draft the five pages assume 0035, 0054 will be ratified and that layered c2 cp will have ADR, modelled, and
> checked.
>
> Assume 0055 ratified too, add the mesh to §1. Also, assume any pending lineage ADRs are ratified.
>
> Don't the lineage, mesh edge alternation, and consensus rules limit capture impact?
>
> Update the submission based on the current state of the repo: new specs, proofs, ADRs. Assume any relevant ADRs
> will be approved as is.
>
> Has this doc already been assessed with respect to TOPAK? on any topak branch in derived?
>
> yes, bring it over and update it against main

(The custodian's five prompts of 2026.11.10, as the 11.10 draft gives them, and two of 2026.11.20. The first of
2026.11.20 came with the notice's PDF attached. The second answered the assistant's offer to bring the 11.10 draft
onto this branch and update it against main. "Layered c2 cp" is the command-chain design's tree of control planes.)

**2026.11.20** · derived · **a draft, not sent, and not true of the tree it is committed to** · prepared by Claude at
the custodian's request · **supersedes `derived/topak-flash-rfi-response-draft-2026.11.10.md`**, which is brought
onto this branch unchanged from `cbdf012`, on a branch never merged · read against main at `1722432`:
Genesis Checkpoint G12 (`checkpoints/topak-genesis-checkpoint-G12-2026.11.16.md`), Theory of Operation revision 16
(`narrative/theory-of-operation.md`, cited below as ToO), the self review of 2026.11.11 and its findings CR-40 to
CR-61 (`derived/topak-critical-review-2026.11.11.md`, cited as the review), ADR-0054 R7 and ADR-0055 R3 with their
proofs, ADR-0069 and ADR-0070, `spec/specification-graph-results-2026.11.17.txt`, and every proof module's latest
results file. The sources the 11.10 draft read have not changed on main since `bbda621`: ADR-0024, ADR-0035, ADR-0059
to ADR-0068, the eight command-chain modules and their proofs, the second command-chain proposal, its two readings and
the diagram findings. The 11.10 draft's citations of them stand.

**What this is.** The five-page narrative that DARPA Special Notice DARPA-SN-27-17 (Formal Learning and Abstractions
for System Heterogeneity, issued 2026.11.03) encourages, written as of the day it would be sent. The notice is a
request for information, not a solicitation, and says a proposal sent against it is disregarded, so this is an
answer to its two questions and asks for nothing. Responses are due **2026.11.30 at 5:00 PM Eastern**, ten days from
this draft, by email to FLASH@darpa.mil, as an unprotected Word or PDF file on letter paper with 1-inch margins and
type no smaller than 12 point (8 or 10 point allowed in tables), with the respondent's organization and a technical
contact's name, email address and phone number.

**It keeps the one assumption the custodian set, which still does not hold: every Proposed record the response rests
on is ratified as it is written.** Those are ADR-0035 (lineage), ADR-0054 and ADR-0055 (workflows and meshes),
ADR-0057 and ADR-0058 (the specification graph, and an overlay declared against it), ADR-0059 to ADR-0068 (the
command chain) and, new in this draft, ADR-0070 (lifecycle security), with the amendments that wait on them. ADR-0024
A2.2, the independent veto seat, is ratified, and the reference does not enforce it, since it reads ADR-0035's
independence table and no such table exists (ADR-0024's History; the review's CR-42). The response therefore reads
every record as *author-ratified* and none as Proposed. None of them changed status between the two drafts.

**What changed on main since the 11.10 draft** (`bbda621` to `1722432`, 123 commits):

- **G12 was cut on 2026.11.16** and is the state of record, with ToO revision 16 cut from it. **One batch was
  ratified**, Batch 40 (ADR-0033 A19 and A20, the reference measured again). It touches nothing the response cites.
- **The workflow and mesh modules are proved** (ADR-0054 R7, ADR-0055 R3): `Workflow_proof`, 1,136 obligations, and
  `Mesh_proof`, 1,470, both certified. `Mesh_proof` proves `ClearHopsAlternate`, the alternation of lineage on a clear
  edge, of the module's own fixed mesh with a budget of 6. It is not proved for every mesh.
- **The counts moved.** 76 records, up from 67. 41 TLA+ modules, up from 39: `Paxos.tla`, the consensus log at the
  message level, and `PaxosTrace.tla`, its trace validation. 34 proof modules, up from 32. 13,622 obligations, up from
  11,016. 31 certify, up from 29. G12 §2.9 gives the same figures.
- **The specification graph was rebuilt** after Batch 40 (`spec/specification-graph-results-2026.11.17.txt`). It now
  holds the command chain's modules: 529 nodes and 495 edges, 15 of the edges stale. The inventory of the reference is
  unchanged: 19 of 43 theorems, all at grade *trusted*. The theorem-to-premise binding (2026.10.06) is unchanged. It
  has no row for the command chain or the mesh, and eighteen modules have no binding row (G12 item 90).
- **Upstream fixed the prover's first unsound case, and the collision half of the second**, in `tlapm` `ff40755`:
  #309 is closed and #310 is open. The pin is still `7824dab`, with both cases. ADR-0077, Proposed, would move it.
  No check detects the first case (G12 §2.6, items 73, 104 and 117).
- **The self review of 2026.11.11 found that the command-chain records claim more than their modules state**
  (CR-48). That bears on three sentences of the 11.10 response:
  - An intent's budget starts afresh with each intent, so n intents issue up to n times the voted figure.
  - The revocation bound in `K_up` is proved of entries charged to a lease. A send, a beacon, a hold, a terminal
    behaviour and a delivered release act are classed as effects by the records, and none of them is charged.
  - Agreement takes no time in `PlaneClock`.

  The same review also finds that the overlay claims a status the process does not define (CR-40). Its 485 defects
  are not dispositioned (G12 item 121). Readers of the drafter's own lineage found them, and CR-61 grades that High.
- **Two drafted records bear on §2**: ADR-0069 (the Build-Run pipeline) and ADR-0070 (lifecycle security). ADR-0070
  §5.1 holds the drafting assistant as a havoc drafter outside the trusted base, and §6.2 projects every artifact's
  provenance from the sealed round, generalizing ADR-0035's method. The response cites ADR-0070 for both, under the
  custodian's assumption.
- **Stage one of the refinement chain is further behind**: the review's rerun matched 82 of 83 traces, and the
  end-to-end workflow trace does not replay (G12 item 56). A trained model now runs as a compiled guest at rung 1 on
  development rules. No real principal is `Contained` (G12).

**What "ratified as written" does not make true.** Each record's ratification condition says what is not met, and
the response claims none of it:

- **Nothing of the command chain is built**, and ADR-0067's floor stage has no entry written (G12 item 112).
- **ADR-0060 §5 leaves a choice among three options to the custodian**, on what ADR-0032 §4's budget means for a
  plane nobody can reach. The response is silent on it.
- **ADR-0062 §8's coupling at the grant is stated and not modelled.**
- **ADR-0061's three statements about PBFT are recalled and not read**, and its number of replicas is a placeholder.
- **ADR-0068 was not revised when the modules arrived** (the diagram findings' R-1, the review's CR-48). Its status
  note still says nothing is modelled. The response follows the modules and the R1 rows of ADR-0059 to ADR-0066.
- **Where the records and the modules differ (CR-48), the response states what the modules prove**: entries, not
  effects; a budget per intent; time only under `ClockPremise`. Ratifying the records as written would not narrow
  their text to match.
- **ADR-0070's own conditions are not met**: four gates are not run, findings F1 to F9 have no disposition, and the
  assistant's permission list is not measured (its F7). The response cites only §5.1 and §6.2.
- **No record has a reader who is not its drafter.**

**What to check before it is sent.**

| In the response | It rests on | Check |
|---|---|---|
| §1 (i), the design | ADR-0059 to ADR-0066 as written | Each record's status. That none is revised on: seven replicas and the schedule 7, 6, 5, 4 (ADR-0061); a lease's exact count and an entry's extent (ADR-0062); `K_up` and the watermark (ADR-0063); ticks (ADR-0064); topics (ADR-0065); the release seat (ADR-0066). That CR-48's disposition does not change the budget's or `K_up`'s meaning |
| §1 (ii), the six rows | ADR-0068 §1: TM1 with TM13, TM2, TM3, TM5, TM6 with TM12, and TM10 | That the rows still say this, and whether ADR-0068 has been revised |
| §1 (iv), *Required*, "a fleet of one build is one lineage" | ADR-0065 §7, D-0065-1; the two-colour check of ADR-0055 §5 | That ADR-0035 §5 carries the check, which is the gate's and is not drafted |
| §1 (iv), "proved of the mesh module" | `Mesh_proof`'s `ClearHopsAlternate`, at the module's fixed mesh | That it still certifies, and is still of one mesh |
| §1 (iv), "superseded rules govern fewer than `K_up` entries" and the three counts | ADR-0063 §4; `Outstanding`'s `EffectsAfterPerGovernor` | Unchanged |
| §1 (iv), *Limitations*, the false finding | ADR-0068's open obligations (the swarm reading's Z3) | Whether a record now closes it |
| §1 (v), each row | A theorem its proof results file of 2026.11.10 shows proved: `Federation` (row 1); `Intent` (2); `Outstanding` (3); `Release` (4); `Alone` (5, 6); `Peer` (7); `PlaneClock`, under `ClockPremise` (8). No row is the mesh's, since `Mesh_proof` is of one mesh | That each still proves. The modules are small, and §3 says so: `Federation` is a chain of three planes carrying four of the charter's fields, `Membership` has five replicas and not seven, `Intent`'s plane is honest, and `PlaneClock` is in discrete time with no clock rates, where agreement takes no time. Three results files' "Assumptions:" lines omit `ASSUME`s the proofs use (CR-48) |
| §2.1, 43 and 34; 529 and 495; 19 of 43 | `spec/theorem-premise-binding.json` of 2026.10.06 and `spec/specification-graph-results-2026.11.17.txt` | The binding still has no row for the command chain or the mesh; the response says so. Recount if either is rebuilt |
| §2.2, the three findings of the first lesson | ADR-0059 §1, ADR-0061 §3 (`M_TWOVOTES`) and ADR-0066 §4 (`M_ANYVEHICLE`), each marked R1 | Unchanged |
| §2.2, "since fixed in part" | G12 §2.6; `tools/TLAPS-PIN` | Whether #310 is closed, and whether ADR-0077 has moved the pin. If it has, §3's last sentence changes |
| §2.2 and §2.3, the drafter and provenance | ADR-0070 §5.1 and §6.2 | Its status, and that both sections stand |
| §2.4 and the summary: 76 records, 41 modules, 34 proof modules, 13,622 obligations, 31 that certify, 5,600 and 52 for the eight | A count of this tree: the files under `decisions/` and `spec/`, and each proof module's latest certified results file; G12 §2.9 | Recount at the cut |
| §2.1, measure 1; §2.3, "at least one veto seat is of lineage independent of the author's" | ADR-0035 and ADR-0024 A2.2 | Their status, and whether the θ values are still placeholders |
| §3, "485 defects", "82 of 83" | The review's CR-61; G12 items 56 and 121 | Whether either is dispositioned or rerun |
| §3, "no agent is yet confined", "counts as declared" and "the code has since moved past" | G12 (no real principal `Contained`); ADR-0035 §2 and §8; G12 item 103, and the graph's stale edges | That each is still so |
| §3, "four of its trust roots" and "its floor stage is unwritten" | ADR-0068 finding 1; ADR-0067 §7 | That each is still so |

**Placeholders** are in bold square brackets: the respondent's name as an organization, the contact's email address
and phone number, and the date. The record's number, the results' dates and the counts are filled from the tree.

**What in it is not from the corpus.** DoD Directive 3000.09 and Knight and Leveson's 1986 experiment are recalled,
not sourced; the corpus names the second only in passing. §1 (iii) is the drafter's general account of current
practice, not a survey. §1 (iv)'s three positions (free, priced, required) and its paragraph on dynamic
heterogeneity are this draft's reading of the records for the notice's question: no record says a variant is issued
with an intent. §2.1's fourth measure and its suggested definition of equivalence are proposals made here, and the
text says so. The account of Moon and Varshney is ToO §1's and §11.1's. None of this changed from the 11.10 draft.

**What it leaves out.** ADR-0056. ADR-0069 except as ADR-0070 rests on it, and ADR-0071 to ADR-0077. `Paxos.tla` and
its trace validation. ADR-0067's fifteen floor entries and ADR-0064's two rules on a replica's vote. Six of ADR-0068's
fourteen adversaries: TM4 and TM14 stand behind an assumption, TM8, TM9 and TM11 are named under *Limitations*, and
TM7, an insider with a key, is not there at all. `Membership`'s theorem, which the attrition row rests on and no row
of §1 (v) states. The NATO reading's N2, a second anchor, and the swarm reading's Z2 and Z4, which ADR-0068 keeps
open. The review's findings other than CR-40, CR-48 and CR-61, and the scenario inventory's SF-1 to SF-26.

**Status words.** ToO A8 requires a publication to cite confirmation-required records as author-ratified, and ToO §0
requires "author-ratified, provisional" of anything resting on ADR-0050 or ADR-0052. Revision 16 keeps both. §3 of
the response says both once, for everything in it.

**Format.** The response is everything between the two marker comments below. The 11.10 draft's rendering pipeline is
not in the tree, so the length was measured here by rendering both responses the same way: pandoc 3.1.3 to Word with
Liberation Serif (Times-metric) at 12 point, 10 point in tables, on letter paper with 1-inch margins, and LibreOffice
to PDF. The tables' column widths are set by their separator rows, new in this draft; with equal columns both
responses run to six pages. In that rendering this response is **five pages**, its fifth holding 45 lines of text
where a full page holds 48 or 49, and the 11.10 response is five pages with 41 on its fifth, close to the five lines
to spare that draft reported. Render it once more in the tool it will be sent from. It has no header or footer. The
Word and PDF renderings are not tracked (`.gitignore` excludes PDFs).

**Changes from the 11.10 draft** (`cbdf012`), for the prompts of 2026.11.20.

- **The summary and §2.4** take the tree's counts (76, 41, 34, 13,622, 31). The command chain's row is unchanged.
- **§1 (ii), (iv) and (v)** say *entries* where the 11.10 draft said *effects* of the revocation bound (CR-48).
  **§1 (iv)** says that alternation is proved of the mesh module.
- **§2.1** takes the rebuilt graph's 529 nodes and 495 edges, and says the binding has no row for the command chain.
- **§2.2** says the unsound cases are fixed upstream in part and not in the pinned prover, and that the assistant is
  not trusted (ADR-0070 §5.1). Its last lesson adds the review's finding that the records claimed more than their
  modules prove.
- **§2.3** computes an artifact's provenance from the round (ADR-0070 §6.2).
- **§3** adds the review and its 485 defects, the trace that no longer replays, agreement that takes no time, the
  one mesh, what the revocation bound does not count, and that each intent has its own budget (CR-48).
- **To stay at five pages**, it cuts words in §1 (iii), §1 (iv), §2.1, §2.2 and §3, and sets the tables' column
  widths. No claim is removed.

---

<!-- BEGIN RESPONSE -->

# Response to DARPA-SN-27-17, the FLASH Request for Information

**TOPAK: an authority layer that holds still while the system behind it varies**

| | |
|---|---|
| **Respondent** | **[William Scott Cochran, an individual respondent, or an organization's name]** |
| **Technical contact** | William Scott Cochran · **[email address]** · **[phone number]** |
| **Marking** | UNCLASSIFIED. No proprietary information. **[2026.11.30]** |
| **Source material** | github.com/scottcochran/TOPAK: Apache-2.0 code, CC BY 4.0 documents |

**Summary.** TOPAK is an open design corpus for a control plane that governs AI agents: seventy-six decision records
(ADRs), forty-one TLA+ modules that are model-checked, thirty-four of them with proofs, a draft policy *floor* in
Cedar (the standing rules that no later policy can weaken), and a Rust reference of the path that admits every
effect an agent causes. Its premise is that an agent is Byzantine wherever it sits. No guarantee rests on what a
model means or intends, and each is stated against the agent's *action alphabet*, the closed set of typed actions it
can request. Three consequences are offered to FLASH. An invariant stated against an alphabet is untouched by
variation behind it, so a new variant needs no new proof. Where variation does reach the trusted part, instances are
related by a computed inventory of theorems kept and lost, in place of functional equivalence. And generated
variants share their generator, so diversity is a premise to be checked, by a stated rule.
Section 1 works them on one application. Section 3 says how far each claim is established: this is one person's
design, not a fielded system.

## 1. Application: authority over uncrewed vehicles on a contested link (RFI item 1)

**(i) Domain.** The target is the authority layer of a fleet of uncrewed vehicles under a chain of command: who may
cause which effect, for how long, under whose rules, and what record it leaves. It is not a design of a vehicle, a
sensor or an effector. The design, ten records (ADR-0059 to ADR-0068), is a tree of control planes. A *plane* is
one replicated log with one set of rules in force. Each is seated by a vote at the plane above, under a *charter*
with a closed schema, and hands down only what it was handed, or less. The last plane where a person commands is
the *intent boundary*. Its commander issues *intents*: a task, bounds, a budget and an expiry. Below it an
*autonomous plane* runs among each group of vehicles: seven replicas under Byzantine agreement, hosted on the
vehicles, with no person seated and no path that adds authority.

Each vehicle carries a small trusted *governor* between its autonomy software, the *stack*, and its actuators and
radio. The plane orders one thing for a vehicle, a *lease*: an alphabet, bounds and an exact count of entries. The
governor then permits each entry under the lease with no further round, and every entry declares how far it runs.
What the plane runs is a *mesh* (ADR-0055): the mission's plan as a graph that may loop, under an activation budget
voted at the intent boundary. Stacks report to one another on topics admitted with the mesh, and nothing a peer
originates enables anything. A vehicle that stops hearing its plane loses its lease at once.

**(ii) Rationale and threat.** A fleet is bought as one design. Every vehicle runs the same stack under the same
mission rules, so an exploit developed against one vehicle, a trigger planted in one model, or the rules read out of
one captured vehicle is good against all of them. The adversary contests the link, captures vehicles, and can now
develop exploits with agents faster than a fleet is patched. Through all of it people must keep judgment over
irreversible effects (DoD Directive 3000.09), including while the link is jammed.

| Adversary | What bounds it | What is left |
|----------|-------------------|----------------|
| The stack: Byzantine, may request or report anything | The governor, the alphabet, and the lease's bounds and count. Nothing it reports to a peer enables anything | Whatever the bounds allow, which a quorum voted acceptable. A peer misled inside its own bounds |
| The link: jams, delays, replays, injects | Certificates stop forgery. A plane cut off above stops granting before `K_up` entries are outstanding, and a withheld intent arrives aged | It can always deny, and denial blocks every irreversible effect |
| A captured vehicle | The rest of its lease's count. It is one vote of seven, where two are tolerated | Its own actuators, and the rules and routes it holds |
| A captured plane | Its charter, checked by every governor; each honest governor's own tally against `K_up` | Fewer than `K_up` entries from each honest vehicle, inside the intent |
| Attrition and partition | Membership shrinks 7, 6, 5, 4 on a voted schedule, each step by a quorum of the membership it replaces, so at most one part is the plane | Silencing vehicles spends the plane down to tolerating one capture |
| The supply chain: weights, tools, rules | Admission by vote on a digest. No stack shares a lineage with its Observer, or with a stack whose output it reads in the clear | Every stack of one lineage, inside its bounds. Model text and annotators the rule cannot see |

**(iii) State of the art and its limits.** Current practice hardens one instance: signed mission loads,
authenticated links, geofences and run-time monitors. Three limits remain. The fleet is a monoculture, so what an
adversary learns is durable and transfers. Authority rides a link an adversary can cut, and what a vehicle does
without it is designed per platform. Assurance is argued per configuration, so each variant is certified anew.
N-version programming assumed independent versions fail independently. Knight and Leveson (1986) refuted it
experimentally, and agent-written versions reopen it (Ron, Baudry and Monperrus, arXiv:2606.20158).

**(iv) What heterogeneity and the FLASH thrusts add.** The design puts every part of the system in one of three
positions with respect to variation.

- *Free.* No theorem rests on the stack, so any generated planner or model may be admitted to any vehicle, by a vote
  on its digest, and no proof reopens. A mission's rules are a bundle that can only refuse. Its mesh may differ in
  graph, loops, topics and budget, and within what a quorum voted one commander varies an intent by one
  signed act.
- *Priced.* The governor, Byzantine agreement, the policy evaluator and the clocks are trust roots: the design adds
  twelve rows to the trusted base (ADR-0068). Changing one is a declared variation, and a tool computes the theorems
  kept (§2.1).
- *Required.* Each stack is coupled to an Observer, a second agent that reads its record and may deny and never
  admit. The two must be of independent lineage, as must any two stacks where one reads the other's output in the
  clear, on a mesh edge or a peer topic. A fleet of one build is one lineage: it delivers peer reports unread, as
  handles, or declares the loss (ADR-0035, ADR-0055, ADR-0065).

*Dynamic* heterogeneity then bounds what adversary knowledge is worth in acts, not seconds. Each intent grants at
most its budget of leases, a lease at most its count of entries, and an entry runs no further than its declared
extent. At a plane the commander cannot reach, superseded rules govern fewer than `K_up` entries. A captured vehicle
discloses its own plane's rules, so where planes run different variants under one charter it discloses one.

*How far a capture spreads.* Consensus holds a captured vehicle to one vote of seven. Lineage is there to keep one
trigger from taking a stack and its Observer together, and alternation, proved of the mesh module, to keep it from
the next stack. A captured vehicle's reports arrive labelled untrusted and only narrow what a reader does. None
bounds what that vehicle does or discloses.

*Assumptions.* The governor is the only path to the actuators and the radio. No more replicas are captured than the
membership tolerates. Effect classes and extents are declared as what they are. *Limitations.* Nothing here
bounds a deceived navigation source, a deceived person or a colluding Observer. On a plane with no person a false
finding stops a vehicle and nobody restores it. The governor and the floor are one design on every vehicle, a
common mode declared and kept small, not removed. *Evaluation.* §2.1's experiments, with attacking agents
seated as stacks.

**(v) Invariants and degrees of freedom.** Each invariant is a theorem of a TLA+ module, proved for every value of
its constants, with a seeded break that must violate it. The last rests on a premise about clocks, so the
records call it a declared bound: no bound in seconds is a theorem. Interoperability is by construction: one
schema for charter and lease, one floor for the tree.

| Invariant across every instance | Kind | Free to vary |
|-------------------------|------|------------------|
| Authority only narrows down the tree, and no governor accepts a lease outside what the root voted, whoever signs it | Security | The stack on each vehicle: models, planner, perception |
| Every effect has an intent and a lease ordered before it, and an autonomous plane adds no authority | Functional | A mission's rules, and an intent's values inside what was voted |
| Fewer than `K_up` entries follow a revocation, from an honest plane or each honest vehicle of a captured one | Safety | A mesh's graph, loops, seatings, topics and budget |
| An irreversible effect is one person's signed act, for one vehicle, used once and fresh. No agent's alphabet reaches it | Safety | The tree: its planes, and each plane's shrink schedule |
| A vehicle that stops hearing its plane permits no actuation, and an ended lease leaves only its voted terminal behaviour | Safety | Terminal behaviour per vehicle class, among those voted |
| An entry within a live lease's count never waits on another vehicle, an Observer or a round of the plane | Availability | Where each Observer sits, declared with the mesh |
| Nothing a peer originates enables a permit, and what is received is labelled untrusted | Security | The product in each role, against a stated obligation |
| No grant more than one tick period past an intent's expiry, while captured and slow replicas are fewer than a certificate | Timing | Declared values: `K_up`, the tick period, counts and budgets |

## 2. Framework, architecture and evaluation (RFI item 2)

**2.1 Metrics, invariance and experiments (i).** *Invariance as an inventory.* Instances with different failure
modes are not behaviourally equivalent, and are not meant to be. What must be equal is what is guaranteed. In the
corpus a deployment is a tuple of positions on a lattice of named parameters, and the theorems are stated at its
maximum, the *archetype* (ADR-0023). Moving a parameter falsifies named premises, and each theorem resting on one is
absent for that instance. A table binds 43 theorems to 34 premises, not yet the command chain's, and a tool
computes an instance's inventory. Building it produced three findings FLASH will meet.

- Composition is not monotone. Two variations can jointly void a theorem that neither voids alone, so an instance
  that moves two parameters declares the difference.
- A variation can void no theorem and still change who is trusted. The declaration lists those changes beside the
  theorems.
- A variant with a capability the maximum lacks is not a variant: it shows the specification is incomplete. The
  command-chain design is the worked case, filed as an overlay that reports what the pattern lacks.

The suggestion to FLASH is to call two generated instances equivalent when they hold the same inventory on the same
trusted base, and otherwise to have the generator state what each loses.

*Collateral.* An instance's assurance artifact is its declaration: the parameters it moved, the premises those
moves falsify, the theorems voided and the trust roots it stands on. A graph of 529 nodes and 495 typed edges
(ADR-0057) computes it and grades each theorem by its weakest edge. Of the reference it reports that 19 of the 43
theorems hold, every one at the weakest grade, because nothing yet proves the code against the model.

*Heterogeneity, measured against what an adversary can reuse.* Four measures, the cheapest first.

1. *Lineage independence* (ADR-0035). A model's lineage record is computed from the build log, not written by
   whoever trained it. Two lineages are independent only if five exclusions hold: different weight roots, no shared
   generator of training content, corpus overlap under a threshold, different architecture family and tokenizer, and
   no shared curator. Shares are upper bounds, so uncertainty can only fail a pair, and the relation is not
   transitive, so every pair is checked. In a rehearsal on public corpora the overlap measure gave 1.0 for a
   filtered crawl inside its parent and 0 against public-domain books.
2. *Shared trust roots.* The trusted base is a table of rows, each classed by whether its failure can add authority
   (ADR-0045). Rows two instances share are their common mode.
3. *Correlated misses.* On planted defects held out from both, a pair fails when its joint miss rate exceeds a set
   multiple of the product of the two. A pass grants nothing.
4. *Transfer under adaptive attack* (proposed here, and not run). Seat exploit-developing agents as stacks, with the
   alphabet and the specification in hand. Count effects outside the lease's bounds: the design says there are none,
   and one counterexample refutes it. Of attacks that succeed inside the bounds on one instance, measure the share
   that succeed unchanged on another, and how long they stay useful against reissued variants.

*Vacuity.* A generator can satisfy a specification that constrains nothing. Moon and Varshney (arXiv:2605.09045)
report that failure with every gate green. Each property in the corpus therefore ships with a *mutation*, a seeded
break that the check must catch and that breaks nothing else, and a *witness* that the behaviour it constrains is
reachable (ADR-0046).

**2.2 Induction and deduction (ii).** The corpus was made by the loop the notice describes. An AI assistant
drafts a record, a module, its mutations and its proof. The oracles are the TLC model checker, the TLA+ Proof System
(a solver's answer counts only with a checked proof) and the Lean 4 kernel. One person decides; the assistant is
not trusted (ADR-0070). Four lessons:

- *Counterexamples change the design.* The ten command-chain records were modelled and proved the day they were
  drafted, and each took what its module found. A captured plane can sign more leases than its budget. A replica
  could sign two removals, leaving two successors. One release act could fire on every vehicle.
- *The oracle has a trusted base.* This work found two cases in which the prover's translation of an obligation is
  unsound, reported upstream as tlaplus/tlapm issues 309 and 310, since fixed in part but not in the pinned
  prover. A second method re-proves sixteen modules in Lean, and three of those encodings are compared with TLC's
  state graphs.
- *Evidence is regenerated, never edited.* Each results file names the digests of module, checker and prover,
  stale ones are reported, and a claim is *checked*, *proved* or *certified*.
- *A second instrument finds what the first left.* Drawing nine diagrams of the same records found inconsistencies
  the modules could not see, and a review found the records claiming more than their modules prove. Properties are
  kept local (a flag the violating action sets, one constant that selects a mutation), so both stay cheap.

**2.3 Agent architectures (iii).** A generated design entering service is a grant of authority. The Byzantine threat
sits at design time, because design agents write the specifications and policies the running system is later judged
against.

- *One agent.* A design agent has six typed actions, no shell and no network, and an Observer whose findings
  subtract authority and never add it.
- *Admission.* An artifact leaves design only by *promotion*: a vote on its digest in which the author cannot vote
  and at least one veto seat is of lineage independent of the author's. Its provenance is computed from the round,
  not stated by its author (ADR-0070).
- *Many agents.* A workflow is a promoted graph (ADR-0054), and a mesh is one that may loop under a voted budget
  (ADR-0055). Its promotion seats every agent in it, and no agent grants another. An orchestrating agent chooses only
  among steps whose guards already hold, so it affects how good the work is and never whether it is safe.

**2.4 Reusable libraries (iv).** All of it is public under the licences above.

| Library | Form | Standing |
|------------|--------------|-----------|
| The pattern's mechanisms: credential, seats, confinement, coupling, policy, workflows, meshes, the command chain | 41 TLA+ modules with mutations and witnesses; 34 proof modules, 13,622 obligations | Checked. Proved where a proof module exists; 31 certify |
| The command chain: `Federation`, `Membership`, `Intent`, `Alone`, `Outstanding`, `PlaneClock`, `Peer`, `Release` | Eight of those modules, each with its proof: 5,600 obligations | Checked, proved and certified 2026.11.10. Not in Lean |
| A second route | Lean 4 encodings of sixteen modules and of the admit decision | Proved in Lean, of the encodings |
| Policy floor | Cedar, with schema, tests and non-vacuity gates | Draft |
| Theorem-to-premise binding; specification graph | JSON, with the tools that compute an inventory | Kept by hand |
| Lineage gate | Log projector and exclusion-rule suite | Rehearsed |

## 3. Standing of these claims

Everything above, this response included, is one person's work with an AI assistant. No reader independent of the
author has reviewed it; agents of the author's own lineage found 485 defects, not yet dispositioned. Each decision
record is ratified by its author alone and reads as *author-ratified*; some that §1 leans on are also provisional.
The theorems are of the design. No refinement to the running code exists: the reference is tied to the model by
replayed traces, 82 of 83 of which replay, and by two functions proved in Lean, which the code has since moved past.
At the reference no agent is yet confined, and one that can reach a shell is outside every guarantee. Lineage
records there count as declared, since training runs outside confinement. Of the command chain nothing is built,
and its floor stage is unwritten. Its modules are small, three planes and five replicas where the record asks
seven, and agreement in them takes no time. The mesh is proved of one graph. Its revocation bound counts entries,
not sends, beacons, terminal behaviour or release acts, and each intent has its own budget. Its numbers are
placeholders, and four of its trust roots on a vehicle have identities nothing yet issues. In its eight proofs the
temporal step, 52 obligations, rests on a backend no checker confirms. The prover's two unsound cases are kept out
of every proof by a writing rule and a scan, not by a check.

<!-- END RESPONSE -->
