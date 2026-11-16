# The command-chain proposal and its NATO reading, read against Sophia et al. (2026) on Byzantine drone swarms

> Summarize and assess vs TOPAK's federated c2 plan and nato c2 assessment.
>
> put it on ccr-ef00d918-hbicyo

(The custodian's two prompts of 2026.11.10. The first came with the paper attached.)

**2026.11.10** · derived · a reading, not a record · prepared by Claude at the custodian's request · read against
`derived/topak-federated-c2-design-proposal-2026.11.10.md` at `845f95c`, cited below as **the proposal**, and
`derived/topak-federated-c2-proposal-assessment-2026.11.10.md` at `f8a2c38`, cited as **the NATO reading**, each by
its own section numbers, and against parts of Theory of Operation revision 15 (ToO; §5 says which parts)

**The paper.** S. Sophia, P. Getzi Jeba Leelipushpam, Immanuel JohnRaja Jebadurai and V. Ebenezer, *Zero-trust
graph-attentive intelligence for Byzantine-resilient UAV swarms under communication constraints*, Discover
Electronics 3:154 (2026), doi:10.1007/s44291-026-00305-9, published 2026.11.01, open access under CC BY 4.0. All 31
pages were read. Its framework is called ZT-GAT, and the paper's section numbers are cited as "paper §".

**Four words collide with the corpus.**

- **Byzantine.** In the paper a whole drone is honest or Byzantine. In the proposal every stack is Byzantine always
  and the governor is trusted (§2.1 below).
- **Consensus.** The paper uses it for a filtered mean. It defines no agreement protocol (§1.3 item 4).
- **Zero trust.** In the paper it is a score compared with a threshold.
- **Federated.** The paper's keyword is "Federated consensus", in the sense of federated learning, which its own
  method does not use. It is a third sense beside NATO's and the proposal's (the NATO reading §2.1).

**Sources, and what was not read.** None of the paper's 32 references was read, including the six §6 names as
worth reading. The UAVSwarm dataset was not opened: what is said of it is the paper's Table 1 and §4.1. ADR-0051
was read for §4, §7 and §8 only. ADR-0039, ADR-0041 and ADR-0055 were not re-read and are taken as ToO gives them.

**Not independent.** The proposal and the NATO reading were drafted by the assistant in other sessions, and this
reading is by the same assistant. All three have been read by nobody independent of their author. Nothing here is
modelled or checked. The figures quoted from the paper in §4 are a private simulation's (§1.3 item 1) and show an
order of magnitude at most.

**Verdict.** The paper is a detector for drones that lie, tested on a simulation its authors have not released, and
several of its tables disagree with each other and with its own equations (§1.3). It is not a consensus protocol and
not a design for authority, so it competes with nothing in the proposal. Where the two meet, the paper's central
move is the one the corpus prohibits: a trust score that admits (§2.2). Its three signals are three different
things in the corpus's terms, and only one is a judgment (§2.3). **It is about the one axis both earlier documents
left thin**, what vehicles tell each other and how far to believe it, and reading the proposal with that in mind
finds four things the NATO reading did not (§4). The first matters most: the proposal gives one path for
information between vehicles, a Byzantine-ordered log, and no rate for it, and its own Observer needs that path.

---

## 1. The paper

### 1.1 What it claims

Six contributions, of which the first carries the rest: graph attention, a trust assessment, compressed messages and
trust-weighted aggregation run in one decision cycle. The authors say where the novelty is and is not: "The
contribution lies in the information flow among these components rather than in the individual use of GAT, trust
fusion, or weighted aggregation." The headline is a Byzantine F1-score of 96.8%, a trust accuracy of 97.9%, a
consensus latency of 134.6 ms and a packet delivery ratio of 93.7%, for swarms of up to 50.

### 1.2 What it contains

| Part | Content |
|---|---|
| Paper §3.1, §3.2 | The swarm as a directed graph, updated at 10 Hz. A node's state is its position, its velocity and its trust score from the last cycle. An 8-head graph attention network, 256 dimensions per head, gives each node a 2048-dimension representation |
| Paper §3.3 | A learned linear projection to 256 dimensions before transmission, and a linear decoder at the receiver |
| Paper §3.4 | Three scores per node. **Behavioural**: its reported position against a Kalman prediction from its recent trajectory. **Cryptographic**: the outcome of an ECDSA P-256 signature check, smoothed over rounds with λ = 0.85. **Graph**: the mean attention its neighbours give it. They are summed with weights 0.35, 0.40 and 0.25 and compared with a threshold of 0.75 |
| Paper §3.5, §3.6 | A node at or above the threshold is admitted to a mean of the reconstructed representations, weighted by score. The Byzantine decision is the admission mask. The loss is a regression on the trust score plus the reconstruction error |
| Paper §3.7, §3.8 | Every message is signed and carries an identifier, a timestamp and a sequence number. The threat model lists colluding nodes, nodes that behave well before turning, and stolen keys, and says the mean is "an aggregation rule rather than … a formal proof of Byzantine consensus safety" |
| Paper §4.1 to §4.3 | The data: UAVSwarm, a public set of 72 video sequences with 3 to 23 drones each, and over it a private overlay of 4,800 simulated episodes with 5 to 50 drones and packet loss of 2% to 35%. Three swarm sizes (10, 25, 50) at 2.0 Mbps. Five baselines |
| Paper §4.4 to §4.16 | The results, below |
| Paper §5, §6 | A discussion and a conclusion that restate the limits |

| Result | Figures |
|---|---|
| Model-level, 50 drones | F1 96.8%, trust accuracy 97.9%, consensus latency 134.6 ms, delivery 93.7%. The closest baseline, attention-based federated learning, has F1 90.7% |
| By attack and corruption level, 12 conditions | Macro F1 92.83%. From 97.8% (Sybil, 10% corrupt) to 85.4% (gradient poisoning, 33%). False-positive rate 1.4% to 7.2% |
| Mixed and adaptive attacks, 20% to 50% corrupt | F1 from 93.6% to 79.6% (mixed) and from 91.8% to 75.3% (adaptive). False-positive rate up to 10.8% |
| Swarm size | At 100 drones: F1 90.4%, delivery 87.9%, consensus success 87.6%, consensus latency 218.9 ms |
| Bandwidth | At 0.5 Mbps: delivery 71.3%, consensus success 78.4%. At 8.0 Mbps: 98.9% and 99.0% |

### 1.3 Assessment

**What is good.** The paper is candid about its scope. It says the contribution is a coupling of known parts, that
the mean is not a safety proof, that the evaluation is a simulation, and that the baseline comparison is one of "the
reported configurations within a common experimental framework, rather than … a fully matched same-protocol
evaluation". It reports the cases that go badly: 40% and 50% corruption, 75 and 100 drones, 0.5 Mbps. Table 3's
averages and Table 9's confidence intervals recompute from their own rows (§5). Its threat model names the hard
adversaries, the stolen key and the node that behaves until it does not.

**What does not hold**, most serious first.

1. **Every evaluated quantity comes from a simulation nobody else can run.** The public dataset "was designed for
   visual detection and tracking and does not contain inter-UAV communication records, wireless link measurements,
   trust information, or Byzantine labels". The overlay supplies the state vectors, the links, the delivery
   figures, the trust values and the labels, and takes the swarm from the dataset's 3 to 23 drones to 50 and then
   100. "The overlay data, generation code, random seeds, and configuration files are maintained privately". The
   simulator, the channel model and the attacks' parameters are not described. So the detector is trained and tested
   on attacks from one generator, written by its authors, whose own flags are the ground truth. What the dataset
   contributes to any number, beyond a split of its sequences, is not said.
2. **The headline does not follow from the table beside it.** Table 3 gives F1 for four attacks at three corruption
   levels. Only two of the twelve reach 96.8%, spoofing and Sybil at 10%. The mean of the four 10% rows is 96.08%,
   and the macro-average is 92.83%. The paper says the two figures are "distinct" and "should not be interpreted as
   the same aggregate measure", and never says under what conditions 96.8% was measured. The abstract and paper §4.1
   list a 5% corruption level. No result at 5% appears.
3. **The ablations contradict the method, and each other.** Table 13's largest effect is from removing the
   aggregation step: detection F1 falls from 96.8% to 78.4%. By the paper's Eq. 17 to 21 and Algorithm 1 the
   aggregate is computed after the decision, enters no loss and is fed back nowhere, so removing it cannot change a
   detection. Table 4 has the zero-trust layer adding 1.1 points of trust accuracy (96.8% to 97.9%). Table 13 has
   its removal costing 13.3 (97.9% to 84.6%).
4. **There is no protocol.** "Consensus rounds per decision", "consensus success" and "revocation success" are
   tabulated and defined nowhere. No rule says which node computes another's score, whether two nodes can hold
   different scores for a third, or how the swarm agrees on an exclusion. The paper does not say where the network
   runs: its cost figures are for a whole 50-drone swarm on hardware it does not name. At that size the consensus
   latency, 134.6 ms, is longer than the 100 ms cycle of its Fig. 1, and the conclusion leaves "sub-100 ms
   decision-making" to future work.
5. **The threshold leaves no margin, and the one learned signal is a fixed budget** (the drafter's derivation, from
   the paper's Eq. 4 and 12 to 17; §5).
   - The threshold, 0.75, equals the behavioural and cryptographic weights together. A node perfect on both passes
     whatever attention it gets. Any shortfall must be made up by 0.25 times its graph score.
   - Attention is normalized per receiver, so across the swarm the graph scores share a fixed total. Their
     degree-weighted mean is one over the mean degree: 0.31, 0.17 and 0.11 at Table 2's degrees of 3.2, 5.8 and
     9.4. That is worth 0.078, 0.043 and 0.027 of trust.
   - At the 50-drone degree, a node with average attention and a clean signature record is excluded when its
     reported position is more than 7.6% of the tolerance from the prediction. One with a perfect position is
     excluded by a single failed signature check: its score falls to 0.717. Both hold of an honest node.
   - A node whose neighbours give it all their attention stays admitted with a position 71% of the tolerance away,
     or, with a perfect position, through six failed signature checks in a row. Evidence that adds can be supplied
     by whoever controls the neighbours.
   - The behavioural score compares a node's reported position with a prediction from its own reported trajectory.
     It checks that a node is consistent with itself, not that it is where it says.
6. **The attacks are named and not defined.** Paper §3.8's list is the only gloss: a Byzantine drone "may transmit
   falsified states, replay valid messages, fabricate identities, poison exchanged representations". The fourth
   attack is called gradient poisoning, and ZT-GAT's drones exchange no gradients. Replay is classified
   statistically, with a false-positive rate of 2.1% to 5.8%, although paper §3.7 discards a repeated sequence
   number outright. "Adaptive" means changing attack type between rounds. No experiment has an attacker who knows the
   detector, holds a stolen key, behaves well first, or colludes over attention. Loss and bandwidth are conditions,
   never an adversary's choice.
7. **The baselines are not comparable**, which the paper says. They run at 20, 30, 25, 40 and 45 participants
   against 50, and the outcomes of PBFT, of federated averaging and of a ledger are mapped to "detections" by a rule
   the authors chose. A "Max UAVs" column reports each method's configured size as a result.
8. **The editing is unfinished** (the table below).

| Where | As printed | Against |
|---|---|---|
| Abstract; paper §4.1; Table 1 | Corruption levels "of 5%, 10%, 20%, and 33%" | Paper §4.2, §4.4 and the conclusion say 10%, 20% and 33%. No table has a 5% row |
| Tables 8 and 11 | F1 96.8% at 50 drones. Table 2 gives 10%, 20% and 33% as the fractions tested at that size | Table 3 over those fractions: 92.83% |
| Table 4 | The 8-head, 256-dimension network without the zero-trust layer: accuracy 96.8% | Table 13: without the zero-trust layer, trust accuracy 84.6%; "GAT Only", 76.4% |
| Table 4, rows 1 to 5 | Accuracy and AUC-ROC for a network with no zero-trust layer | Paper §3.6: the decision comes "from the trust-threshold decision rather than from a separate probability-producing classification head". Without the layer, no decision rule is defined |
| Table 13 | Without Byzantine aggregation: F1 78.4%, trust accuracy 73.8% | Item 3 |
| Fig. 6 | False-negative rates of 3.2%, 1.8%, 2.4%, 0.9% and 0.6% | Table 12 and the text: 5.3%, 2.8%, 3.7%, 1.4% and 0.9%. The text says the two rates sum to 100%; the figure's do not |
| Table 2 | 4, 7 and 12 "consensus rounds per decision" | Algorithm 1 takes one mean per cycle. No rule defines a round |
| Table 9 | A standard deviation over ten seeds for PBFT | The seeds vary "stochastic initialization", with attacks and network settings held fixed. What they vary for PBFT is not said |
| Table 5 | The F1 column of the five weight rows is overprinted and unreadable | — |

**How to use it.** As a description of what a swarm's members send each other, how often and how large, and as an
honest list of the adversaries a detector has to face. Not as evidence that this detector reaches its figures, and
not as a consensus protocol.

---

## 2. The paper against the proposal

### 2.1 Different objects

The paper decides which data enter a shared estimate. The proposal decides who may cause which effect, for how long
and under whose rules (its Scope). The paper has no person, no effect, no lease, no expiry, no hierarchy and no rule
of engagement, and its aggregate has no stated consumer.

**"Byzantine" names two different things.** In the paper a drone is honest or Byzantine as a whole, and 5% to 50%
of them are. In the proposal the stack is Byzantine on every vehicle at all times (TM1), and a separate governor
holds the key, lifts time and position itself and is the only path to the actuators (§5.1). The share that matters
is of governors: fewer than a third of an exposed plane's replicas captured (§11). So the paper's corruption
fraction is the proposal's TM3 and nothing else. For the proposal's authority properties, a swarm in which every
stack lies is the base case and not the stress test.

### 2.2 Concept by concept

| The paper | In the proposal | Reading |
|---|---|---|
| Identity: a key pair per drone, "generated during initialization". No issuer and no roster | The anchor's key resident on every vehicle; a chain of charters with commit certificates; `replicas` fixed by the charter (§2.1, §2.5) | A fabricated identity holds no lease and no place in `replicas`. The paper's Sybil class has nothing to detect |
| Replay: classified, F1 88.2% to 95.7% | Fences and per-lease sequence numbers (TM2; §5.4) | A repeated sequence number is a replay with certainty, and the check has no false-positive rate |
| Falsified state and poisoned representations from a node whose signature verifies | A stack's report is content, and no safety decision reads "a position the stack supplies" (§5.1). A captured vehicle's chain "says what its captor signed" (§5.4) | The two classes no certificate stops. They are the paper's hardest, and the proposal rests nothing on detecting them (§4.6) |
| **A score admits**: a node joins the mean when its score reaches 0.75, and is scored again each cycle | "every finding is **deny-only** … never an admit precondition" (ToO §5.1; ADR-0007) | The paper's central mechanism is what the corpus prohibits. Re-admission by score is a grant made by a classifier. The exclusion half is admissible, as a finding |
| Evidence is summed, and neighbours' attention adds | An admit is the floor's permit and no refusal from any bundle (§2.2). Observers "combine by any-of, and there is no Observer quorum" (ToO §5.1) | §1.3 item 5 is `Observers.tla`'s `M_QUORUM` in the paper's own arithmetic: a majority that can add can outvote an honest signal |
| A failed signature lowers a score | A certificate that does not verify is not a message (§2.5) | A weight where the proposal has a gate |
| Freshness: the sender's timestamp, with no clock model | "No external time is read" (§4.4) | §3.2, F1 |
| Revocation: "marking the identity as inactive", with no agreement on it stated. Nothing expires | Ordered subtraction, fences, a lease's `ttl`, an intent's `expiry` (§2.6, §4) | The paper bounds no authority in time because it grants none |
| The channel: loss and bandwidth as conditions | TM2 "jams, drops, delays, replays, injects" | The paper has no link adversary |
| Past a third corrupt: tested to 50%, F1 75% to 86% from 40% up, and no "formal consensus-safety guarantee" | The plane is captured, and "bounded by its charter or intent, and by nothing else" (§11) | A measured decline with no bound, against a bound with no measurement |
| People: none | The intent boundary and the release seat (§3, §6) | Nothing to compare. An aggregate that a stack reports to a release person is "ingress to the person, labelled as untrusted, and it enables nothing" (§6) |

### 2.3 Three signals, three different things

The paper sums three scores. In the corpus's terms they are not the same kind of thing, and summing them loses what
two of them are.

| Signal | In the corpus's terms | Where it belongs |
|---|---|---|
| Signature and sequence checks | Mechanical, with a yes or no | The admit path, each as a conjunct. Smoothed into a score, a certain answer becomes a weight |
| Position against a prediction | A fold over facts, if the positions are ones a governor lifts and a plane records. As the paper has it they are the node's own reports | The kind of thing ADR-0051 (Proposed) puts in its first tier, a named fold "a second reader can recompute". It is not one of that record's five |
| Attention from neighbours | A learned judgment about a node, made by its neighbours' models | ADR-0051 §4's judgment tier: "deny-only, attributed", and "**Nothing rests on it.**" |

### 2.4 Where a detector like it could sit

- **Inside the stack.** A stack may filter what other stacks tell it however it likes. The stack is Byzantine by
  premise and no property rests on what it believes, so this costs the design nothing and claims nothing.
- **As a correlator's judgment.** The detector reads a whole neighbourhood, which is the correlator's job, "watching
  every cell in its domain for what no single cell can see" (ToO §5.1), and not a cell Observer's. Its output could
  only deny. Z2 and Z3 say what that would need.
- **Not in the admit path**, at a plane or a governor, in any form that adds.
- **One narrow use at a governor.** TM8's row for navigation deception reads "Nothing in this design". A governor
  could refuse when its own position disagrees with ranges it measures to its peers. That is one more refusal, a
  comparison of measured facts, and it cannot correct the position: a peer's word is content. It also gives a lying
  peer a way to stop an honest vehicle (Z4). The paper's reference 32 is on this subject and was not read.

---

## 3. The paper against the NATO reading

### 3.1 The axis it is on

NATO's third axis is the distribution of information. The NATO reading's §2.2 says of it: "The paper sets this axis
aside. The proposal says little more." Sophia et al. is about that axis and no other. It allocates no decision
rights, because its drones take no decisions.

By interaction pattern alone, its swarm is the Edge class within radio range: every drone exchanges with every
neighbour and there is no leader. That is the class the proposal excludes (the NATO reading §2.3).

### 3.2 Finding by finding

| The NATO reading's finding | What this paper adds |
|---|---|
| **F1.** No interval has a stated origin | It shows the hole from the other side. The paper's freshness is a sender's timestamp, with no clock model and no stated window, and "clock drift" is left to future work. A sender's timestamp is content by the rule the proposal keeps (§4.4). The paper tests no message withheld and delivered late: its replay is a repeat. Nothing in it helps F1's construction |
| **F2.** A stack may choose to be alone | Nothing directly: the paper's drone has no governor. Z4 sharpens F2 from the proposal's own text. The paper's figures suggest how often a vehicle would be alone with no adversary at all: a round completes 78.4% of the time at 0.5 Mbps and 87.6% at 100 drones |
| **F3.** A captured vehicle discloses the rules | It extends F3. A detector carried on every vehicle is disclosed with them: its weights, its threshold and its fusion weights. §1.3 item 5 is what an adversary computes from those |
| **F4.** The envelope has no field | Nothing |
| **N1.** Sibling planes cannot deconflict | Nothing. The paper has one flat swarm |
| **N2.** A second anchor | A lead only: the paper's reference 17, Lassfolk and Kari on onboarding coalition drone swarms |
| **N3.** Attrition under a fixed membership | The contrast. The paper's swarm needs no quorum, so a loss costs it a contributor and nothing stops. Nothing it produces is guaranteed either. And one limit on detection as a remedy: a finding can revoke a lease and cannot remove a replica (Z2) |

---

## 4. What reading it shows about the proposal

### Z1. One path for information between vehicles, and no rate for it

"Vehicles coordinate through their plane, and only that way" (§8). In a mesh "the mechanism is the bus", and one
cell's output reaches another as an `input` item along an edge (ToO §2.11). So everything one vehicle's stack gets
from another is an entry in a log whose order is fixed by Byzantine agreement among replicas on the vehicles (§2.5,
§3.3).

**The proposal's own detection needs that path, at rate.** A cell's Observer is seated on another vehicle (§5.6).
It "reads its round topic in full" (ToO §5.1) and reports a watermark, and "heartbeats are admits on the consensus
log" (ToO §5.4). R3 refuses `Actuate` once `K` effects are unread. The autonomous plane has no K: "No Kafka. The
plane's log is carried and handed up on contact" (§3.3). What carries a round's payloads from the Thinker's vehicle
to the Observer's is not stated.

**The paper describes the traffic.** Its drones exchange state with their neighbours at 10 Hz, 256 numbers a message
after compression, over 0.5 to 8.0 Mbps with 2% to 35% loss. In its simulation the filtered mean among 50 has a
consensus latency of 134.6 ms, and its PBFT baseline among 20 one of 412.3 ms.

The proposal owes three statements:

- **The grain of an entry** for a vehicle: a control step, a manoeuvre or a route segment. It sets how many ordered
  admits a plane must carry.
- **Whether stacks may exchange data on a declared peer channel**, each transmission inside an admitted entry and
  everything received labelled untrusted. That is where a filter like the paper's would run. It would carry content
  between cells off the workflow's edges, which is where labels are followed (ToO §2.11), so it changes "only that
  way" and does not clarify it.
- **What an Observer on another vehicle reads, and over what.**

### Z2. "Revocation, once its plane knows" names no way of knowing

TM3 bounds a captured vehicle by "The lease's envelope and its remaining `ttl`. Revocation, once its plane knows."
No mechanism check can tell the plane: a captured vehicle acts inside its lease under a key that verifies, and its
chain "is not evidence" (§5.4). So the knowledge has to be a finding, from another vehicle's Observer or from a
correlator, that what the vehicle signs disagrees with what others measure. That is the paper's subject. Its figures
are the only ones any of the three documents has for it: 73% to 98% of Byzantine nodes caught, and 1.4% to 10.8% of
honest ones flagged.

Two limits follow from the proposal's own text.

- **A finding revokes the lease and leaves the replica.** Changing `replicas` is a promotion (§2.3; the NATO
  reading N3), and `FD4-autonomous-adds-nothing` forbids one below the intent boundary. A vehicle found captured
  goes on voting in its plane, and counts against f, until the link returns.
- **A captured plane orders no finding against itself.** It may "falsify its log" (TM5). A finding against it comes
  from the intent boundary, at reconciliation, or not at all.

### Z3. A false finding where nobody can respond

Meshed, a plane is "Unattended. Observers still read and their findings still subtract", and ADR-0032 §4's budget
"has no `D`, since no person can respond" (§4.6). At a commanded plane a finding is "a block, a quarantine trigger,
or an eviction" (ToO §5.1), and a person is in reach for what follows. At an autonomous plane nobody is. The
proposal does not say:

- **what a finding does to a vehicle in flight**: whether it ends the lease and sends the vehicle to its terminal
  behaviour (§5.5);
- **whether the cell may be leased again** under the same intent, which is the plane's "one grant" (§3.3), or
  whether a finding stands until the plane is linked. In a mesh, "a finding against any activation in the history
  closes every edge downstream" (ToO §2.11);
- **what rate of false findings a plane can bear.**

The corpus's rules make the rate additive. Findings combine by any-of, and "More Observers never lower safety and
may lower availability" (ToO §5.1). ADR-0051 §8 says a second correlator "bounds its silence on correlations and
not its false findings". The paper's detector, at the best its authors report, flags 1.4% to 10.8% of honest nodes
per decision, and more as the adversary's share grows. The paper recovers by scoring again each cycle, and the
corpus cannot: a score that restores is a grant.

**So the false-finding rate of whatever is seated to watch is an availability parameter of an unattended plane**,
to be declared as `T_intent` is. It is not a safety parameter, since a false finding only subtracts. §5.5 already
says why that is not enough for a body in motion.

### Z4. An Observer can accuse or vanish, and TM11 names only silence

TM11's colluding Observer can "Stay silent". With A's Observer seated on vehicle B (§5.6), B can do two other things
to A:

- **Accuse.** A captured B reports a false finding against A. It takes effect alone, by any-of.
- **Vanish.** B is destroyed, out of range, or captured and quiet. R3 then refuses A's `Actuate`: "A dead or slow
  Observer stops its own Thinker and nothing else; the Thinker waits" (ToO §5.4).

Either way A, linked or meshed, cannot act. Two of the NATO reading's findings get sharper.

- **N3 counts replicas, and coupling adds a second count.** With one Observer per cell, each vehicle lost stops the
  vehicle whose Observer it hosts, without drawing on f at all. The NATO reading asked where an autonomous plane's
  orchestrator runs. The same question holds for every Observer, and for whether a promoted seating may name an
  alternate.
- **F2 gains a motive.** Alone, the disconnected alphabet is exempt from coupling (§5.6). A vehicle whose Observer
  is gone can do nothing while meshed and its `disconnected` entries when alone. If the radio is on the stack's side
  of the governor, a stack in that position gains by cutting it.

The paper has the same dependency in the other direction, a node's standing is its neighbours' attention, and does
not test a neighbour that lies about it.

---

## 5. What was verified, and how

- **Table 3's averages.** Recomputed from its twelve rows: 93.59, 92.16, 92.83, 3.55 and 60.3, as printed. Each
  row's F1 agrees with its precision and recall.
- **Table 9's intervals.** Recomputed as the mean ± 2.262 × SD/√10. All six match as printed.
- **§1.3 item 5's identity.** With attention normalized per receiver and links symmetric, the sum over nodes of
  degree times graph score is the number of nodes, so the degree-weighted mean is one over the mean degree. Checked
  by algebra, and on three random graphs with arbitrary normalized attention, where the two agree to four places and
  the plain mean differs slightly. The paper's links are by range and so symmetric, apart from link failures.
- **§1.3 item 5's figures.** By arithmetic from the paper's Eq. 12 to 17 and Table 2's degrees. Six consecutive
  failed checks leave a score of 0.7509 against 0.75; the seventh excludes.
- **Fig. 6.** Read from a render of page 25 at 220 dpi, against Table 12 on the same page.
- **The paper's quotations.** Each was found in the PDF's extracted text. Two sentences of paper §3.7 are
  interleaved in the extraction and were read from the page.
- **The corpus's quotations.** The proposal and the NATO reading were read in full at `f8a2c38`. ToO §2.2, §2.11
  and §5.1 to §5.5 were read, and ADR-0051 §4, §7 and §8.
- **`tools/check-refs.py`** gives the same output with this file added as without it.

**Not verified.** That UAVSwarm is as the paper describes it. Anything in the paper's references. Whether the
attention behind the graph score is the mean over heads or one head's: the paper does not say, and the identity holds
for either.

---

## 6. Suggested entries, none made

Each is a change to the proposal or to the records it would become (its §14).

1. **State the grain of an entry for a vehicle, and what carries a round's payloads to an Observer on another
   vehicle** (Z1). Decide whether a declared peer channel between stacks is allowed. If it is, §8's "only that way"
   changes and the channel needs a label rule. If it is not, name the rate the log can carry as a cost in §12.
2. **Say in TM3 how a plane comes to know** (Z2), and that a finding revokes a lease and leaves the replica voting.
3. **Declare a false-finding rate for an unattended plane**, beside `T_intent` and `T_alone`. Say what a finding
   does to a vehicle in flight and whether its cell may be leased again without the link (Z3).
4. **Add to TM11 an Observer that accuses and one that vanishes.** Say in §5.6 whether a seating may name an
   alternate Observer, and add to N3's cost the vehicles a lost Observer host stops (Z4).
5. **Keep signature and sequence checks as gates** wherever a detector is seated, and never as inputs to a score
   (§2.3).
6. **Consider a refusal for TM8** when a governor's position disagrees with ranges it measures to its peers, as a
   further conjunct and never as a correction (§2.4).
7. **Read before a record rests on any of this:** the paper's reference 17 for N2; 28, 29 and 30, on Byzantine
   agreement for drone swarms, for the proposal's question 7; 32 for entry 6; and 5, a review of hardware-rooted
   trust, for §11's trust-root rows.

---

## 7. What this does not claim

- **Not that the paper's figures are wrong.** They cannot be checked, and several disagree with each other. Which
  of two disagreeing figures is the error is not known.
- **Not that a graph-attention detector cannot work**, here or anywhere.
- **Not that the proposal is unsound.** Z1 may be a change to it. Z2 to Z4 are statements it owes and costs it has.
- **Not that the paper's latencies and rates would hold of any real radio.** They are quoted for their order of
  magnitude, from a simulation that is not described.
- **Nothing about ADR-0039, ADR-0041 or ADR-0055**, which were not re-read, or about the rest of ADR-0051.
- **Nothing about the paper's related-work survey** or the studies in its Table 14.
