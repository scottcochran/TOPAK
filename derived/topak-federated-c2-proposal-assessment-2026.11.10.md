# The command-chain proposal read against NATO C2 and Amrani & Ouared (2026)

> Summarize and assess. How does the NATO C2 inform vs TOPAK federated CP? Check branch `ccr-89afd041-l2ii5m` in
> derived. Write a derived doc with this assessment on the branch.

(The custodian's four prompts of 2026.11.10, with spelling normalized. The first came with the paper attached. CP
is a control plane.)

**2026.11.10** · derived · a reading, not a record · prepared by Claude at the custodian's request · read against
`derived/topak-federated-c2-design-proposal-2026.11.10.md` at `845f95c`, cited below as **the proposal** and by its
own section numbers, and against parts of Theory of Operation revision 15 (ToO; §5 says which parts)

**The paper.** M. Amrani and A. Ouared, *Using command & control for coordinating UAV fleets for missions with
changing contexts*, Innovations in Systems and Software Engineering 22:4 (2026), doi:10.1007/s11334-026-00625-9,
published 2026.04.24, open access under CC BY 4.0. It extends the authors' VECoS 2023 paper. All 23 pages were read.

**Two words collide with the corpus.** "C2" here is command and control, not the confirmation class C2 of ADR-0029.
The paper abbreviates allocation of decision rights as "ADR"; this reading spells it out.

**Sources, and what was not read.** NATO's own reports (SAS-050, SAS-065, SAS-085) were not read. What is said of
them is the paper's account, or, where marked *(recalled)*, the drafter's memory of NATO doctrine, checked against
nothing in this session. The paper's experiments are reported in two earlier papers by the authors' collaborators
(its references 9 and 10), which were not read. The second prompt was first answered against `main`, where the word
"federated" occurs once, in `derived/topak-safety-liveness-quorum-lattice-2026.11.05.md`; N2 below keeps what that
answer found.

**Not independent.** The proposal was drafted by the assistant in another session, and this reading is by the same
assistant. It is not an independent review, and the proposal has still been read by nobody independent of its
author. Nothing here is modelled or checked: F1's scenario is an argument, not a trace.

**It cites the proposal.** The proposal was revised in place once because it was unmerged and uncited. This file
cites it by section number at `845f95c`.

**Verdict.** The paper is a vocabulary. It gives NATO's five C2 Approach classes a topology each and a metamodel to
hold them, and its formal core does not define the agility it is about (§1.3). Where the two documents meet, the
proposal is the stronger: people command, nothing selects an approach at run time, and every state's authority is
voted before it is needed (§2). **In NATO's terms the proposal is not a federation.** It is one chain of command
under one anchor, run on mission command. NATO's model describes lateral relations among entities that each keep
their own command, so it confirms the vertical design and shows three things missing sideways (§3). Reading the
proposal on its own text found four more (§4). The first matters most: no interval has a stated origin, so a
signed intent, lease or release act that is withheld and delivered late defeats `RevocationBounded` and leaves
"fresh" undefined for an irreversible effect.

---

## 1. The paper

### 1.1 What it claims

Three contributions: a refined, formal account of C2 Systems, C2 Approaches and C2 Agility for drone fleets; a
behavioural specification of how drones perform tasks and adapt "through agility manoeuvres"; and a tool to create,
deploy and simulate such a system. The abstract calls the work preliminary and aims at "adaptive, reliable, and
verifiable behaviour".

### 1.2 What it contains

| Part | Content |
|---|---|
| §2, background | NATO's definitions. A C2 Approach is a point on three axes: allocation of decision rights, patterns of interaction, distribution of information. Five classes name regions of that space: Conflicted, Deconflicted, Coordinated, Collaborative, Edge. C2 Agility is the ability to detect a change, select a better approach and make the transition, over an "endeavour space" of self, mission and environment |
| §3, scenario | A mountain rescue with search, monitor, support and relay teams. Table 1 gives each class a topology: Conflicted none, Deconflicted a ring, Coordinated a star, Collaborative a clustered star, Edge a full graph |
| §4, structure | An Ecore metamodel: teams nested in teams, each under its own approach; members with features drawn from a feature model; a mission of independent, atomic tasks, each handled by exactly one drone. Definition 1 restates it as a tuple. The information axis is "abstract[ed] away for now" |
| §5 and §6, behaviour | Three roles: task-performing entities, a Task Allocator and a C2 Approach Selector. Twelve events (Table 2). A structural operational semantics over a state (E, TA, C2AS, c2a), with the functions `allocate`, `extract` and `evaluate` left abstract |
| §7, simulation | A simulator on Repast Symphony. Five members, thirty tasks, Deconflicted at the start, ten scripted sequences of member failure, sensor failure and context change. With agility (S1) against a baseline that never adapts (S0): time on mission 10% to 60% higher, tasks completed 25% to 40% higher, "statistically significant with a 95% level" |
| §8 to §10 | A discussion of the modelling choices, related work and a conclusion. Appendix A repeats §6.3's rules |

### 1.3 Assessment

**What is good.** The mapping from NATO's classes to concrete topologies is clear and reusable, and the composite
metamodel carries NATO's "fractal" point, that an approach applies at every level of a team. Separating the
operational, tactical and strategic roles is a clean cut. The authors say plainly that the task model is simplistic
and the work preliminary.

**What does not hold**, most serious first.

1. **Agility is not formalized.** The selector's rule for a manoeuvre has no premise and changes no state. No rule
   changes the system's approach after initialization. `evaluate` is an uninterpreted predicate, and the paper's
   own implementation "simply decides to seek a new C2 Approach when a Task can no longer find a host". Topology
   and channels appear in no rule, so an event reaches its consumer whatever the approach: Conflicted, with no
   links, and Edge, with all of them, behave identically. The semantics has one approach for the whole system,
   where the metamodel and Definition 1 have one per team.
2. **The rules have defects as printed** (§6.3 and Appendix A; the table below).
3. **The evaluation cannot carry the claim.** It gives no table, run count, variance or named test. The baseline
   allocates at random and never adapts, so the gain cannot be attributed to changing approach rather than to
   reallocating at all. Communication costs nothing in the model, so nothing in it could favour a less connected
   approach, which is the trade NATO's classes exist to describe. Staying longer on the mission is counted as good
   in a scenario whose first objective is speed. One result is unexplained: approaches "were progressively
   escalated until reaching Edge, which then reverted to Conflicted when nothing else could work".
4. **Nothing is verified.** No property is stated, checked or proved, and the semantics is not mechanized. The
   claimed equivalence between the metamodel and Definition 1 is asserted; the tuple has no leaders, points of
   contact, task locations or durations.
5. **Every drone is honest.** Members report their own failures truthfully, and the allocator and the selector are
   single drones with no protection and no successor. The paper cites the doctrine that "only humans are capable
   of exercising command" and then gives a drone "the authority to change the C2 Approach".
6. **The editing is unfinished.** §5.1 has one paragraph twice, §7 ends a sentence in an ellipsis, and Table 1
   gives Edge no leader where the text says "a leader is still designated".

| Rule | As printed | Consequence |
|---|---|---|
| Selector, `Manœuver(S, T)` | No premise; the state (e, _, _) is unchanged | A manoeuvre does nothing |
| Allocator, `Evaluate` | `evaluate(S)` implies the emission of `Manœuver(S, T)`; `T` is bound by nothing | Selection is not defined |
| Entity, `Failed`, a configuration exists | `cfg' = extract(F, t)`, and `t` is retried under `cfg'` | `extract` does not read the current configuration. A task that fails again with the same features is retried under the same `cfg'`, without end and without a report |
| Entity, `Failed`, none exists | Reports `TaskFailed` and moves to the next task with `cfg'`, which is ⊥ | The entity carries on with no configuration |
| Entity, `SensorFailed(f)` | The queue `t::t'::T` becomes `t'::T`; only `SensorFailed(e, f)` is emitted | The current task is dropped with no `TaskFailed`, and the allocator still holds it as assigned |
| Entity, `Allocate(e, t::T)` | The task list becomes `t::T` | An allocation replaces the queue instead of extending it |
| Allocator, `Reschedule` | `allocate(E, R)`; `R` is the same after the step | Every task in `R` is allocated again at each period |
| Allocator, `newTask` and `Mission` | `α'` appears in the result and no premise defines it | The assignment map is undefined |
| Absent | No rule for the loss of an entity | §7.2.2 simulates member failure, and §8.5 says the semantics "includes rules for entity failure and recovery" |
| Absent | No rule lifts a component's step to the system, or says how an emitted event is delivered | The system relation that rule (1) announces is not defined |

**How to use it.** As a statement of NATO's vocabulary with a worked mapping to topologies. Not as evidence that
changing approach helps, and not as a semantics to build on.

---

## 2. NATO C2 against the proposal

### 2.1 A chain of command, not a federation

The proposal's "federated planes" are a tree under one root. One anchor key is resident on every vehicle (§2.5).
The charter's `floor` "equals the parent's: one floor for the federation" (§2.1; question 8). The release roster is
anchor-issued (§6). Authority only moves down and only narrows (§2.1, §2.2).

NATO's first axis is the "Allocation of Decision Rights to the Collective" (the paper's Fig. 1, reproduced from
SAS-085). The collective is a set of entities that each keep their own command, and the five classes say how much
each gives to the whole. A tree with one root has no such collective. The proposal's "federated" means delegated.

### 2.2 Concept by concept

| NATO C2, as the paper gives it | In the proposal | Reading |
|---|---|---|
| Command is a person's (paper §2.1, after Pigeau and McCann) | No person and no path that changes authority below the intent boundary (§3.3). An irreversible effect only from a `release` seat a person holds (§6) | The proposal keeps the rule. The paper cites it and breaks it (§1.3 item 5) |
| Control is "bounds for decisions", in four functions: establish intent; determine roles, responsibilities and relationships; establish rules and constraints; monitor and assess (paper §2.2) | The intent (§3.2); charters and seatings (§2.1); the floor and the bundles (§7); Observers, findings and the record (§5.4, §5.6) | One to one. The fourth is the weak one below the boundary: meshed, nobody can respond, and alone, nothing reads (§4.6) |
| Allocation of decision rights | Charter fields that only narrow, with a budget debited up the tree (§2.1) | NATO describes a position. The proposal makes it a checked quantity that moves one way |
| Patterns of interaction | A tree of planes. Inside a plane "the mechanism is the bus" and vehicles never address each other (§8) | §2.3. There is no lateral pattern (N1) |
| Distribution of information | Labels. A log carried and handed up on contact (§3.3, §5.4). A stack's report is untrusted ingress to a person (§6) | The paper sets this axis aside. The proposal says little more |
| C2 Agility: detect, select, transition | A vehicle's state is what it can reach (§4.1). Each state's alphabet and the terminal behaviour are voted at seating (§5.2, §5.5). A move down needs nobody | **There is no selector.** That is the proposal's answer to the paper's `evaluate`, and it is the corpus's rule that expiry grants nothing |
| The endeavour space: self, mission, environment | Environment: the three states. Mission: a new intent, which needs the link (§4.3). Self: reallocation inside a mesh (§8), and nothing for a plane's own membership | N3 |
| Rules of engagement (the custodian's term; the paper has none) | The floor, a promoted bundle, and judgment kept out of the admit path (§7) | Standing rules against a mission's own. A bundle can only restrict, so loosening goes up the tree |

### 2.3 The three states are three of the five classes

| State (§4.1) | By the paper's topology (Table 1) | By decision rights |
|---|---|---|
| Linked | Coordinated, nested: a star at each plane, whose centre is the mechanism and not a leader vehicle | Held above, lent down as an intent |
| Meshed | The same star inside the plane, and no link above it | One intent and one shared plan, the mesh, among the vehicles: NATO's Collaborative *(recalled)*, inside the plane only |
| Alone | Conflicted: no communication | Each vehicle on its own lease, then its terminal behaviour |
| Never | Edge: every member addresses every other | Excluded. Cells reacting to each other with nobody deciding what runs next "is not supported" (ToO §2.11) |
| Unstated | Deconflicted | What two meshed sibling planes would be to each other, if their envelopes were voted disjoint (N1) |

**The direction is the opposite of the paper's.** The paper escalates toward Edge as things fail and falls to
Conflicted last. The proposal's states are forced by the link and not chosen, a vehicle only moves down without
help, and the last state is fixed in advance.

---

## 3. What NATO's model shows is missing

### N1. Sibling planes cannot deconflict

The intent boundary seats "one autonomous plane per group of vehicles", so it may seat several. Meshed, two
siblings cannot reach their common parent, and vehicles coordinate "through their plane, and only that way" (§8).
None of §7.2's nine forbids and none of §10's properties compares one intent's envelope with a sibling's.

Doctrine's answer for units that cannot talk is a boundary drawn in advance, which is NATO's Deconflicted class
*(recalled; the paper renders it as a ring)*. Once the envelope is a field (F4), a child's being inside its
parent's and two siblings' being disjoint are the same kind of comparison, made at the same three moments (§2.2).

### N2. A second anchor is out of the design

A partner's vehicles under one's own plane, or one's own under a partner's, have no place in a tree with one
resident anchor key. This is the case NATO's model was built for.

*(Recalled.)* A nation does not hand over full command. It lends a bounded, revocable control of its forces,
attaches national caveats, and keeps a veto over each use. The proposal's machinery would carry that with no new
kind of rule:

- **A caveat is a bundle on the chain.** It can refuse and is never asked whether to grant (§2.2).
- **The lender's veto is a plane fence.** It subtracts, so it needs no quorum (§2.6).
- **A governor would verify two chains** and admit only what both floors permit.

The cost is in §2.4's terms: a second havoc issuer, a second intent axiom beside ADR-0025's, and a capture
threshold that is the weaker anchor's. NATO's own consensus practice does not transfer. A proposal adopted because
nobody objected by a deadline *(recalled)* is a grant made by a timeout, which ToO §7.1 forbids as a mechanism
constant.

Read as designs for two anchors, the five classes come out as follows.

| Class | Two anchors | Standing |
|---|---|---|
| Conflicted | Independent deployments. A peer's output is content "a party outside the deployment could have written" and is labelled `untrusted` (ToO §2.10) | The corpus today |
| Deconflicted | Each anchor declares targets and effects disjoint from the other's. Nothing is shared | A declaration. It extends effect exclusivity across deployments as an assumption |
| Coordinated | Each keeps its own log and floor, and accepts the other's signed record as input | Accepting a foreign key is already an anchor issuance: it is one of "the keys the mechanism accepts a signature from in place of its own check" (ToO §7.2) |
| Collaborative | One jointly promoted workflow. The tally spans both rosters and both floors apply | New: an order across two logs, a joint tally, and fences across two epoch chains |
| Edge | Agents of both address each other | Excluded by premise (ToO §2.11) |

### N3. Attrition, under a membership fixed by the charter

An autonomous plane's replicas run on its vehicles, with "membership fixed by the charter" (§3.3; question 3). It
needs n ≥ 3f + 1 replicas and certificates of 2f + 1 signatures (§2.5). So it tolerates f replicas missing for any
reason. A vehicle destroyed, out of range or captured each draws on the same f.

| Vehicles in the plane | Losses it survives |
|---|---|
| 4 | 1 |
| 7 | 2 |
| 10 | 3 |

**One loss more, and no certificate can ever form again.** Every survivor is alone, has at most `T_alone`, and
then does its terminal behaviour. TM6 says this of a partition, which may heal. §9 puts "physical destruction of
vehicles or planes" out of scope, and for this consequence it cannot be: the loss is permanent, and it is the
ordinary case for the deployment the proposal describes.

Three things stand in the way of a repair in the field:

- **Changing `replicas` brings a new issuer into force**, so by §2.3 it is a promotion at a commanded plane, which
  a meshed plane cannot reach, and `FD4-autonomous-adds-nothing` forbids it below.
- **Removing a replica is not a pure narrowing.** It lowers the number of vehicles an adversary must capture.
- **Loss and partition look the same from inside.** A smaller roster adopted on a timeout could leave two groups
  each admitting, which is what TM6 rules out.

**The orchestrator is the same question in small.** A decision point needs an orchestrator's `Route`, and a lapsed
orchestrator "takes no default edge" (ToO §2.11). The proposal does not say where an autonomous plane's
orchestrator cell runs. If it runs on one vehicle, the loss of that vehicle stalls every decision point until the
intent expires.

This is the paper's whole subject, treated there with every member trusted. Reallocating tasks among surviving
vehicles is what a mesh does. Re-forming the plane has no counterpart in the proposal.

---

## 4. Findings from the proposal's own text

### F1. No interval has a stated origin

**Today the question does not arise.** A lease's `ttl` is "a duration on the local monotonic clock" (ADR-0031 §1).
The mechanism that grants a lease is the mechanism that checks it at every admit, so the duration starts at the
grant, on the checker's own clock.

**In the proposal the checker is somewhere else.** A governor checks a lease, and an autonomous plane's replicas
check an intent, each on its own clock (§4.2, §4.4). A charter's `expiry` is "on the clock of whoever checks it"
(§2.1), and "no external time is read" (§4.4). A remote checker can start an interval only at something it
observes. The proposal does not say what that is.

**If it is receipt, the link adversary moves the window.** TM2 "jams, drops, delays, replays, injects".

1. At t₀ the commander orders an intent. The adversary withholds it.
2. At t₁ the commander revokes it. The adversary withholds the fence.
3. At t₂, as late as it likes, the adversary delivers the intent. It is authentic, its certificate verifies, it is
   not a replay, and its fences match the latest the plane has heard.
4. The plane works the intent until t₂ + `T_intent`.

`RevocationBounded` (§4.3) promises no effect after t₁ + `T_intent`. The same holds of a lease pushed to a governor
and `T_alone`. TM2's row says "`T_intent` and `T_alone` bound the delay". They do so only from an origin the
adversary cannot move.

**The release act is the worst case.** The interlock checks "that the act is fresh and unused" and "the vehicle
must be linked" (§6), and the proposal gives a test for neither. A person's act for one irreversible effect, held
back and delivered after the situation has changed, passes every check §6 names. `M_REPLAY` (§10) is a second use,
not a late first one.

**The usual construction** is to let the holder start the clock. The holder sends a request that carries a nonce
and starts its timer when it sends. The grant returns the nonce. Real time since the grant is then no more than
the holder's measured time since the request, and §4.4's margin covers the drift. For an intent, which is pushed,
the plane would hand up a nonce or its own log index while linked, and the next intent would name it. A release
act would answer a challenge the governor issued, so that its age is read on the governor's clock.

### F2. "Loss only subtracts" is inexact, and a stack may choose to be alone

§11's row for the link reads "Loss only subtracts: the plane is meshed, or the vehicle is alone". Being alone does
remove entries: only those marked `disconnected` stay (§5.2). For the entries that stay it also removes checks:

- the order before the effect, and with it void (§5.4);
- `R3-observer-live` (§5.6);
- coordination through the plane's log (§8);
- any finding or revocation the plane has ordered since the grant.

**Nothing says which side of the governor the radio is on.** §5.1 lists the governor's duties, and the link's
endpoint is not among them. If the radio and its software belong to the stack, the stack decides when the vehicle
is alone. That is TM1 acting as TM2 against its own vehicle.

The bound is not wrong: a vehicle "revoked by its own plane produces none after *t* + `T_alone`" (§4.3), and a new
lease needs the plane. What is missing is the statement. The disconnected alphabet is what a Byzantine stack can
have on demand for one lease, with no Observer, and each `disconnected` mark should be voted as that.

### F3. A captured vehicle discloses the rules

TM3's row begins "Extract the key and the lease". The vehicle also holds every bundle on the chain, which is
the mission's rules (§7.1); the charters; the intent's task and envelope; the release roster (§6); and the terminal
behaviour, which may be to "return on a voted route" (§5.2). §9's out-of-scope list covers what an adversary learns
from traffic, not from a vehicle in its hands.

An adversary that holds the rules knows what the vehicles will not do. One that holds the return route knows where
a jammed vehicle goes, and TM2 lets it choose when. The floor reserves `restricted` for "content that must not
leave" the deployment (the glossary), and nothing says whether a bundle or an envelope carries it.

### F4. The envelope has no field

The charter has "a closed schema", and "a capability that is not a field is not carried" (§2.1). An intent "names
the round's task, an envelope, an activation budget and an `expiry`" (§3.2). The schema has `round`, `task`,
`budget` and `expiry`, and no field for an envelope.

The word is used in two senses. One is a seat's set of entries (§6; question 6), which `alphabet` carries. The
other is a region of the world: TM8 moves "the envelope in the world", and §11 speaks of "area checks". Nothing
carries that one. §7.1 puts areas in a bundle. §2.3's fourth row and §7.1 let one commander narrow "a smaller
area" in the next intent, and a bundle cannot change without a promotion.

So either the charter gains fields for an area and a window, or "area" leaves §2.3's fourth row.

---

## 5. What was verified, and how

- **The proposal's quotations.** Eighteen quoted sentences were searched for in ToO, the glossary and the decision
  records, with line breaks removed. All are present. Two differ only in capitalization: "Degeneracy, not a
  ladder", a heading, and "The reason is unknown to the mechanism, by construction".
- **The rows it cites.** Assumptions A1, A5, A9, A10, A13, A15 and A17, and ToO §12 items 2, 9 and 21, say what the
  proposal uses them for.
- **`tools/check-refs.py`** gives identical output on the proposal's tree and on `a157659`, all of it about older
  files. With this file added it gives the same again.
- **§2.5's argument** was checked by hand. Under a crash-recovery protocol an acceptor accepts any proposal at a
  ballot it has not promised against, so one lying proposer can collect a majority's signatures for two values at
  one index in two ballots.
- **§4.4's arithmetic** holds. A clock slow by a fraction ρ reads (1 − ρ) of real time. Stopping at `ttl` less a
  margin of ρ × `ttl` stops at real time `ttl`.
- **The paper's rules** in §1.3 were read twice, in §6.3 and in Appendix A, which agree.

**Read in ToO:** §1, §2.10 (labels, in part), §2.11, §4.1, §4.2, §5.4 (in part), §7.1, §7.2, §8.1, §10 and the
rows of §12 and §13 named above. ADR-0031 §1 and ADR-0051 §8 were read for one line each.

---

## 6. Suggested entries, none made

Each is a change to the proposal or to the records it would become (its §14).

1. **State each interval's origin** (F1): a holder's request with a nonce for a lease, a handed-up nonce or log
   index for an intent, a governor's challenge for a release act. Reword TM2's bound to match.
2. **Add three mutations to §10** (F1): a late first delivery of an intent, of a lease and of a release act, each
   of which must break its property and nothing else.
3. **Give the envelope a field**, or take "area" out of §2.3's fourth row (F4).
4. **A forbid and a `Federation` property for siblings** (N1): the envelopes of two planes under one parent are
   disjoint, or the overlap is declared.
5. **Name attrition as a cost in §12 and a row in §9** (N3), with the numbers. Ask the custodian whether a charter
   may carry a voted membership schedule, and say where an autonomous plane's orchestrator runs.
6. **Say in TM1 that a stack may make its own vehicle alone**, and say in §11 which side of the governor the
   link's endpoint is on (F2).
7. **Add disclosure to TM3**, and say whether a bundle and an envelope carry `restricted` (F3).
8. **Ask whether a second anchor is in scope** (N2). If it is, it is a record of its own. If it is not, "federated"
   in the proposal's title means delegated, and the proposal should say so.

---

## 7. What this does not claim

- **Not that the proposal is unsound.** F1 is a missing definition with a known construction. F2 to F4 and N1 are
  statements the proposal owes. N2 is a question of scope. N3 is a cost the proposal has and does not name.
- **Not that NATO doctrine says what is marked *(recalled)*.** Those sentences want a source before a record
  rests on them.
- **Nothing about ADR-0050, ADR-0052, ADR-0054, ADR-0055 or ADR-0058.** They were not re-read, and the proposal's
  use of them is taken as given outside the sentences §5 checked.
- **Nothing about the first draft** (`7155ad9`), which was not compared with the revision.
- **No judgment of the paper's experiments** beyond what its own §7 reports.
