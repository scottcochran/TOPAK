# TOPAK as the authority tier of a command chain: federated planes that only narrow, an autonomous last plane under a commander's intent, and irreversible effects held by people

> What if TOPAK is treated as the top tier of a command and control chain? Missions are promoted bundles. DAG
> workflows are cells of command chains. Mesh workflows are lowest level of field command autonomy: Brigade Combat
> Team (BCT) (Army) / Marine Expeditionary Unit (MEU) or Regimental Combat Team (RCT) (Marines), commanded by an O-6
> (Colonel). The Robots/Drones are Company / Troop / Battery level: WASM bundles with ROE, fully Byzantine, fence
> bounded.
>
> Draft a design proposal: 1. Federated control planes that only narrow. 2. TTL as safety, bounded by mesh fence.
> 3. Threat model. 4. Irreversible effects are human (HITL?). 5. ROE as promoted WASM bundle. 6. Robot/drones have
> disconnected alphabet. 7. Cedar floor in force with ROE. All the rest as you say.
>
> Proposals: 1. Each CP narrowing is a quorum admit or even a promotion? 2. The mesh fence is the planes. 3. Each
> effect is admitted at last commander's intent boundary before last autonomous CP. 4. Last autonomous CP is TOPAK
> lite?
>
> Let's discuss the autonomous layer below C2. Corpus flavored solutions for the clock? Can't the governors or
> mechanisms maintain quorum? Can't monotonicity in the quorum log be sufficient? And the layer's epoch fence?
>
> Yes, bounded in effects as safety, quorum clock second duration, shrink alone alphabet. What about inter-agent
> comms in the autonomous layer? No admit, deny only, coordination/collaboration within ROE?
>
> Agree on 1 & 2.
>
> Agree on 1, 2 and 3. Fold into the proposal. Quorum is PBFT 3f+1 with f = 2 for archetype?
>
> Time cost of BFT is only for elective coordination. Pre-authed effects are always available. Yes?

(The custodian's eight prompts of 2026.11.10, with spelling and punctuation normalized. CP is a control plane. The
last five are from a discussion with the assistant that day. The numbers in the sixth and seventh are choices the
assistant had put, which the table below spells out. After the eighth the custodian chose one of three options.)

**Date:** 2026.11.10 · **Against:** the tree at `a157659`, Genesis Checkpoint G11 and Theory of Operation revision 15
(cited below as ToO); for the second revision, the tree at `e79ae6d` · **Status:** design proposal. **Nothing here
is a decision, and nothing here is modelled, checked, built or reviewed.** · **Drafted by the assistant** at the
custodian's request, from discussions of 2026.11.09 and 2026.11.10. **Revised twice on the day it was written.** The
first revision took in the third prompt (§15). The second took in the last five, a discussion of the plane below the
intent boundary (§16).

**Two readings cite the first revision** at `845f95c`, by section number:
`derived/topak-federated-c2-proposal-assessment-2026.11.10.md`, cited below as **the NATO reading**, and
`derived/topak-federated-c2-swarm-trust-assessment-2026.11.10.md`, **the swarm reading**. Their citations are to that
commit and still resolve there. This revision keeps every section number and adds subsections, and §16 says which of
their findings it answers. `derived/README.md` says a derived document is never revised. The custodian asked for the
discussion to be folded into this one.

**What the custodian settled.** The seven items of the second prompt are marked ⟨1⟩ to ⟨7⟩ where each is used, and
the four of the third ⟨8⟩ to ⟨11⟩. ⟨9⟩ and ⟨10⟩ are statements and are taken as settled. ⟨8⟩ and ⟨11⟩ were asked as
questions: §2.3 and §3.3 answer them, and the answers are the drafter's until the custodian takes them. The
discussion settled eleven more:

| Mark | What was settled | How |
|---|---|---|
| ⟨12⟩ | Revocation is bounded in effects, and that is the safety property (§4.3) | Recommended by the drafter in answer to the fourth prompt, and taken in the fifth |
| ⟨13⟩ | A clock held by a quorum is the second bound, for duration (§4.4) | The same |
| ⟨14⟩ | The alone alphabet shrinks, to the terminal behaviour, listening and a counted beacon (§5.2) | Taken in the fifth prompt, and its content in the seventh, item 2 |
| ⟨15⟩ | Stacks may talk to each other: no admit, deny only, within the rules of engagement (§8.1) | Asked in the fifth prompt. The drafter's answer is yes, with one correction |
| ⟨16⟩ | A send takes a local permit under the rules of engagement, and no order | The sixth prompt, item 1 |
| ⟨17⟩ | Stacks report to topics promoted with the mesh, and name no recipient | The sixth prompt, item 2 |
| ⟨18⟩ | Every entry declares an extent. A duration is counted in ticks the plane orders, and a governor's own clock is a watchdog (§5.3, §4.4) | The seventh prompt, item 1 |
| ⟨19⟩ | A plane's membership may shrink along a schedule voted in its charter, down to a capture floor (§3.6) | The seventh prompt, item 3 |
| ⟨20⟩ | PBFT at 3f + 1, with f = 2 at the archetype | Asked in the seventh prompt. §3.5 answers it |
| ⟨21⟩ | The time cost of Byzantine agreement is paid only for coordination, and a pre-authorized effect is always available | Asked in the eighth prompt. As the first revision stood the answer was no, and §3.7 says what makes it yes |
| ⟨22⟩ | The lease pre-authorizes: one round of the plane per lease, and the governor permits each entry under it. Going alone ends the lease at once | The custodian's choice among three, after the eighth prompt. It keeps ⟨14⟩ |

Every other choice is the drafter's, marked *(drafter's choice)* where the alternative was live. §13 lists twenty
questions, each with a recommended answer.

**It rests on text that is not settled.** ADR-0054 and ADR-0055 (workflows) are Proposed. ADR-0050 (the operator)
and ADR-0052 (the emergency seating) are provisional, and §3.2 leans on ADR-0050 hard. No floor is ratified. Under
A17 nothing should be built on this that could not be rebuilt. ADR-0056 to ADR-0058 were read by title only, except
ADR-0058 §1, §5 and §6.

**Read for the second revision:** ADR-0032 in full; ToO §2.5, §2.6, §2.9 to §2.11, §3.3, §4.1, §5.4, §5.5, §7.10 and
§10; ADR-0055 §7 and its options; ADR-0045's row for trusted time and its finding 2;
`mechanism/lean/Topak/Clock.lean`; `derived/topak-safety-liveness-quorum-lattice-2026.11.05.md`; and both readings.
ADR-0020, ADR-0039, ADR-0041 to ADR-0043, ADR-0047 and ADR-0049 were not re-read and are taken as ToO gives them.
What is said of PBFT is recalled and marked so.

**Scope.** This is about authority: who may cause which effect, for how long, under whose rules, and what record it
leaves. It is not a design of a vehicle, a sensor or an effector, and it says nothing about how a person decides
that an irreversible act is right.

**The proposal in brief.** A deployment becomes a tree of control planes. Each plane is seated by a promotion at
the plane above it and can hand down only what it was handed, or less. The last plane where a person commands is
the **intent boundary**. Below it sits one **autonomous plane** per group of vehicles, with no person on it and no
way to add authority: the custodian's "TOPAK lite". Every effect is admitted at the intent boundary. A reversible
effect is admitted there as an **intent**, a task with an envelope, a budget and an expiry. An irreversible effect
is admitted there one at a time, by a person. Each vehicle carries a small trusted component, the **governor**,
between its autonomy software and its actuators and radio.

Below the intent boundary, the plane's agreement is paid for once per lease. The plane grants a lease with an exact
count of entries, and the governor permits each entry under it with no further round, for as long as it hears its
plane. **What bounds a revoked or cut-off plane is a count of effects, and no clock**: a plane may have a declared
number of effects outstanding beyond what the intent boundary has read, and no more. A second bound, in duration,
runs on a clock the plane's replicas hold together. Stacks may talk to each other on declared topics, and nothing
one says can enable anything. A vehicle that stops hearing its plane loses its lease at once and does one thing
fixed in advance.

**What it changes in the corpus**, each named where it is used and again in §12:

- **Reversed:** no principal grants another (ToO §2.11). Planes grant below themselves.
- **Kept, where the first revision reversed it:** clocks buy liveness, never safety (ADR-0032; ToO §10). The safety
  bound below the intent boundary is a count ⟨12⟩. The residual is one entry in progress, which a slow governor
  clock can stretch (§4.4).
- **Given up for every pre-authorized entry and every report to a peer:** an ordered admit before every effect
  (ADR-0015; ToO §4.1). The ordered predecessors are the intent and the lease ⟨22⟩. It is kept for an entry the
  bundle marks `ordered`, and for every irreversible effect.
- **Relaxed:** an effect with no timing budget must not be reachable from the alphabet at all (ADR-0032 §4). It
  becomes reachable by a person and by nobody else.
- **Amended:** no variant publishes to another cell or subscribes to anything (ADR-0055 §7, Proposed). A stack
  reports to declared topics and a governor delivers them ⟨15⟩. Workers still never address each other, and nothing
  but the mechanism decides what runs next.
- **Strained:** a timeout is never a grant (ADR-0024). A plane drops a replica that has been silent, by a schedule
  its charter voted ⟨19⟩.
- **Brought back:** the word the 2026.10.12 edit dropped. The last plane is autonomous in one sense only: no
  person is seated at it.

---

## 1. Terms and tiers

| Term | Meaning here |
|---|---|
| **Plane** | One replica set with one log, one epoch and one set of rules in force. Every deployment the corpus describes today is one plane |
| **Charter** | The artifact that seats a plane at its parent: the child's replica keys, the bundle revisions it runs under, and its bounds (§2.1) |
| **Chain** | The charters from the root plane down to a granting plane, with a lease at the end |
| **Commanded plane** | A plane with people seated at it: grant seats, operators and, where its charter allows, release seats |
| **Intent boundary** | The last commanded plane above a group of vehicles |
| **Autonomous plane** | The plane below the intent boundary. No person holds a seat at it, and it has no path that adds authority (§3.3) |
| **Intent** | A commander's grant of one round to an autonomous plane: a task, an envelope, a budget and an expiry (§3.2) |
| **Governor** | The trusted component on a vehicle. It verifies the chain, holds the lease, evaluates the floor and the bundles, permits each pre-authorized entry, measures time and position itself, and is the only path to the actuators and the radio. It is mechanism, not a principal |
| **Stack** | The autonomy software on a vehicle: planning, perception, any model. It is the Thinker, and it is Byzantine |
| **Linked, meshed, alone** | What a vehicle hears: its plane, which is in contact with the intent boundary; its plane, which hears nothing from above; no tick of its plane that is not overdue (§4.1) |
| **Terminal behaviour** | What the governor does when a lease ends with no successor. It is fixed at seating (§5.5) |
| **Effect class** | `reversible` or `irreversible`, declared per allowlist entry with its `T_irrev` (§5.3) |
| **Release seat** | A seat held by a person, the only kind whose alphabet reaches an irreversible entry (§6) |
| **Count** | The most entries a governor may permit under one lease. It is exact. It is the round bound the corpus already has (`R`, ToO §5.4), held here to at most `K` (§5.6) |
| **Extent** | How far one entry runs: one act, a number of ticks, or a distance or region the governor measures (§5.3) |
| **Watermark** | The intent boundary's signed statement of how much of a plane's record it has read (§4.3) |
| **`K_up`** | The most effects a plane may have outstanding beyond the last watermark (§4.3) |
| **Tick** | A numbered entry the plane orders once per period `T_tick`. The plane's ticks are its clock (§4.4) |
| **Peer topic** | A named channel, declared by the promoted mesh, on which stacks report to each other (§8.1) |
| **Beacon** | The one report a governor may send when its vehicle is alone (§5.2) |
| **Shrink schedule, capture floor** | The smaller memberships a charter lets a plane fall back to, and the least number of captured replicas it must still tolerate (§3.6) |

"Gate" is not used for the vehicle's component because the corpus already uses it three ways.

**The tiers**, with the custodian's mapping:

| Tier | The custodian's words | In this proposal |
|---|---|---|
| Root plane | "TOPAK as the top tier" | Holds the anchor's rules, the floor and the rosters. Seats the planes below it |
| Commanded planes | "DAG workflows are cells of command chains" | Each promotes missions and charters for the planes below (§7.1, §8) |
| Intent boundary | "Mesh workflows are lowest level of field command autonomy", at brigade level; "last commander's intent boundary" | The last commanded plane. It promotes the mesh, its commander issues intents, and release seats are here or above. It reads the autonomous plane's record and answers with watermarks (§4.3) |
| Autonomous plane | "Last autonomous CP"; "TOPAK lite"; company, troop or battery level | Runs the mesh under an intent and grants the vehicles' leases. No person, no promotion |
| Vehicle | "WASM bundles with ROE, fully Byzantine, fence bounded" | A governor and a stack. It holds a lease and never grants one |

---

## 2. Federated planes that only narrow ⟨1⟩

### 2.1 A plane is seated by a promotion at its parent

The parent's quorum votes on a **charter**, as it votes on any seating (ADR-0024 A3). The charter has a closed
schema, as the lease has (ADR-0031), and a capability that is not a field is not carried:

| Field | What it bounds |
|---|---|
| `plane`, `replicas` | The child's identity: its replica keys and its quorum rule |
| `kind` | `commanded` or `autonomous` |
| `parent`, `fences` | Where it hangs, and the epoch and log index of every plane above it at the seating (§2.6) |
| `floor` | The floor's digest. It equals the parent's: one floor for the federation *(drafter's choice; question 8)* |
| `bundles` | The parent's list of bundle revisions, in order, plus any this seating adds |
| `alphabet`, `labels` | The entries and labels a lease under this charter may carry |
| `ttlMax`, `countMax` | The longest lease `ttl` the plane may grant, and the largest count, per effect class (§4.3, §4.4) |
| `budget` | The most leases the plane and every plane below it may ever issue |
| `kUp` | For an autonomous plane: the most effects it may have outstanding beyond its parent's last watermark (§4.3) |
| `expiry` | The charter's own life. For an autonomous plane it is a number of ticks from a tick it names (§4.4). Elsewhere it is on the clock of whoever checks it. Never later than the parent's |
| `membership`, `tick` | For an autonomous plane: the shrink schedule with its capture floor (§3.6), and the tick period `T_tick` (§4.4) |
| `release` | Whether a release seat may be seated at this plane. Never set for an autonomous plane (§6) |
| `round`, `task` | For an autonomous plane only: the intent this charter is for (§3.2) |

**Every field is the parent's or narrower.** A child's `budget` is debited from its parent's when it is seated, so
the root's tally bounds the whole tree. ADR-0055's activation budget is the same object for one mesh.

### 2.2 Policy narrows by composition, and nothing compares two policies

At any admit, at any plane or governor, the decision is the floor's permit and no refusal from any bundle on the
chain. A bundle a lower plane adds is appended, can refuse, and is never asked whether to grant (ToO §3.1). So
"narrower than the parent" holds of the composed decision for every bundle, at every plane, at every age. This is
ADR-0030's argument applied once per link, and it needs no cross-plane check.

The other fields are sets and numbers. They narrow by a field-wise comparison, made three times: before the vote,
when the seating is applied, and by every verifier of the chain. That is ADR-0033 §4's rule: checked again where
it is applied.

### 2.3 What kind of act a narrowing is ⟨8⟩

The custodian asked whether each plane's narrowing is a quorum admit or a promotion. **It depends on what the
narrowing brings into force**, and the corpus already has the rule: "adding takes a quorum, and denying is local"
(ToO §7.10).

| Narrowing | Example | What it is | Who acts |
|---|---|---|---|
| **A new issuer** | Seating a plane under a charter | A promotion. The charter is narrower than its parent's and it still creates something that can grant | The parent's grant seats, by tally (ADR-0024 A3) |
| **A new artifact** | A bundle with a mission's rules | A promotion. "Everything crossing from Build to Run is promoted" (ToO §7.1), and a bundle that can only refuse still has to pass the gates | The grant seats, by tally |
| **A round inside a promoted seating** | A commander's next intent (§3.2) | An ordered admit, signed by one operator. It is a grant, and it adds nothing the tally did not vote | One operator, with a live lease and a live peer (ADR-0050) |
| **A step of a voted schedule** | Dropping a silent replica from an autonomous plane (§3.6) | An ordered admit by the mechanism. The schedule and its floor were the promotion's. It is not a pure narrowing, and §3.6 says why it is allowed | The plane's replicas, by a quorum of the membership being replaced |
| **A value already in force, moved down** | A shorter `ttl`, a smaller area or budget, an entry removed, a round ended, a revocation, a fence, `deny=all` | An ordered admit. "Runtime subtraction is not promotion", needs no quorum and is attributed (ToO §7.1) | One operator, or the mechanism |

**The rule:** a narrowing is a promotion when it brings a new issuer or a new artifact into force. Otherwise it is
an admit ordered by the plane's consensus and signed by one person or by the mechanism. "Quorum" in the second
case means the replicas' agreement on the order, and no vote.

**At an autonomous plane only the last row exists, and the step of a schedule** ⟨19⟩, since it has no people and
no promotion path (§3.3).

### 2.4 A plane is a havoc issuer, bounded by its charter

ADR-0025 treats the anchor as a havoc issuer bounded by the rules floor: safety must hold for every issuance it
could make (ToO §7.2). **A plane gets the same treatment, bounded by its charter.** Whatever a plane signs, a
verifier accepts only what every charter on the chain allows. A captured plane therefore chooses among leases its
parent's quorum already voted acceptable. That is the orchestrator's position in ADR-0054, one level up: it decides
which, never whether.

**This is delegation, and the corpus excluded it.** "No principal grants another, so there is no chain of
delegation to attenuate" (ToO §2.11). The proposal's answer is that the grantor is a mechanism and not a model,
the delegation only attenuates, and it is budgeted. The sentence is still reversed in letter. The 11.05 lattice
analysis left "a federated authority" as an axis it did not place
(`derived/topak-safety-liveness-quorum-lattice-2026.11.05.md`).

### 2.5 The chain is verified where there is no link

A governor must check a lease with no commanded plane in reach. So every charter and every lease carries a
**commit certificate**: signatures from a quorum of the issuing plane's replicas over the entry's digest and log
index. The governor verifies from the anchor's key down. That key is resident on the vehicle, as genesis rules are
resident in a mechanism release (ADR-0027; ToO §7.4).

**A crash-recovery protocol cannot supply that certificate.** One lying replica can obtain a majority's signatures
for two different entries at one index, in two ballots. A plane whose replicas can be captured therefore needs
Byzantine agreement, with n ≥ 3f + 1 replicas and certificates of 2f + 1 signatures. The letters name roles and an
instrument may be substituted (ToO §1), so this is a change to the P role's obligation at such a plane, not to the
pattern. It does reverse ADR-0045's decision not to require it (ToO §12 item 9; question 7). **An autonomous plane
is always such a plane.** §3.5 gives its size and its instrument ⟨20⟩.

### 2.6 The mesh fence is the planes ⟨9⟩

Read as: what fences the mesh is every plane above it. A charter and a lease carry the epoch and log index of each
plane on the chain, not only of the plane that granted them. An admit, at a plane or a governor, compares each
against the latest the verifier has heard. **Any plane on the chain that moves its epoch fences everything below
it.** That act is a **plane fence**. It is a subtraction, so it needs no quorum and is ordered (ToO §4.1).

**A pushed fence travels only as far as the link does, so the fence is also pulled** ⟨12⟩. A plane may have `K_up`
effects outstanding beyond the last watermark from above, and every watermark carries the fences of the planes
above it. Below a broken link, and below a captured plane that passes nothing on, what ends authority is that
count (§4.3). Any vehicle that has heard a fence relays it (§8.1).

---

## 3. The intent boundary and the autonomous plane ⟨10⟩ ⟨11⟩

### 3.1 Every effect is admitted at the intent boundary ⟨10⟩

Read as: the authorizing admit of every effect is ordered at the last plane where a person commands.

| Effect | What is admitted at the intent boundary | By whom | What happens below |
|---|---|---|---|
| Reversible | An **intent**: a task, an envelope, a budget of activations and an expiry | The commander, an operator. The first intent is the promotion's own (§3.2) | The autonomous plane grants each lease inside the intent, in order. The vehicle's governor permits each entry under the lease (§3.7) |
| Irreversible | The effect itself, one at a time | A person at a release seat (§6) | The plane relays it. It can refuse one and cannot originate one |

**This keeps ADR-0015's sentence one level up.** "Every effect therefore has a consensus-ordered, signed,
authorizing predecessor" (ToO §4.1). Here an effect has two: the intent, ordered at a commanded plane, and the
lease, ordered at the autonomous plane. The act's own admit is ordered before its effect only where the bundle
marks the entry `ordered` (§5.3) ⟨22⟩.

**What is admitted for a reversible effect is an envelope, not the act.** Nobody at the intent boundary sees the
individual act before it happens. The commander voted for, or signed, everything the envelope allows.

### 3.2 An intent

**An intent is a charter for one round of an autonomous plane.** It names the round's task, an envelope, an
activation budget and an `expiry`, and every field is the promoted seating's or narrower. It also names the tick
its `expiry` counts from, one the plane has handed up (§4.4).

- **The first intent comes from a quorum.** The mesh is promoted at the intent boundary with its seatings and its
  budget (ADR-0055; ADR-0024 A4, pending), and that tally grants the first charter.
- **Later intents come from one person.** This is ADR-0050's successor grant: "the quorum acts once per seating,
  and round by round one operator acts" (ToO §7.10). A command chain decides by one commander, and this is where
  that enters: inside what a quorum voted, and not above it. The request is an add, so it needs a live lease and a
  live peer.
- **ADR-0050 bounds a successor by the last lease, not by the seating.** A commander who narrows an intent for one
  phase then cannot restore the mission's bounds without a quorum. That discourages narrowing. *(Question 4: the
  drafter recommends bounding an intent by the promoted seating, which amends ADR-0050 for charters only.)*
- **An intent ends** at its `expiry`, when its budget is spent, when the commander ends or revokes it, or when any
  plane above is fenced. Its `expiry` is a tick number, so the end is a comparison in the plane's log on which
  every replica agrees (§4.4). A plane with `K_up` effects outstanding stops granting before any of these (§4.3).

### 3.3 What "lite" means ⟨11⟩

The custodian asked whether the last autonomous plane is a TOPAK lite. **Yes, and it should be defined by one
absence: it has no path that changes authority.** ADR-0015 enumerates authority changes as exactly promotion and
anchor issuance. An autonomous plane has neither.

| Absent | Present |
|---|---|
| Build: no authoring and no promotion | The admit path, for a grant and for an `ordered` entry: decided, ordered, checked again at apply, void if it fails (ADR-0033 §4) |
| Grant seats, operators, release seats: no person | The lease, the floor, every bundle on the chain, the fences |
| Anchor issuance, new bundles, seating of planes | The workflow interpreter: a mesh, its activations and its budget |
| Any grant but one | **One grant:** a node's lease, made by the mechanism under a live intent, "with every field the seating's or narrower" (ToO §2.11) |
| | Subtraction: the end of a round, a revocation, an Observer's finding, expiry |
| | A step of its charter's shrink schedule (§3.6) |

By role:

| Role | At a commanded plane | At the autonomous plane |
|---|---|---|
| **T** | The modules and their proofs | The same modules. Nothing of T runs on a vehicle |
| **O** | The Cedar floor; the bundle through a sidecar, with Wasm as the fallback | The same floor, linked in. Bundles in Wasm only (§7.1) |
| **P** | Consensus, Byzantine where replicas are exposed | Byzantine agreement among replicas on the vehicles *(drafter's assumption; question 3)*, PBFT at the reference (§3.5), with membership following the charter's shrink schedule (§3.6) |
| **A** | Agents and people | Stacks only |
| **K** | Kafka as transport, with the archive as system of record (ToO §4.2) | No Kafka. The governors' radios are the transport: for the plane's own messages, for round payloads and for peer topics (§8.1). The intent boundary reads the plane's record as it is made and archives it (§4.3) |

### 3.4 It is a declared degeneracy and an addition, not a second pattern

The corpus refuses ladders: "degeneracy, not a ladder", and "theorems are present or absent" (ADR-0023; ToO §8.1).
"Lite" is therefore a nickname. In the corpus's terms the autonomous plane is two things:

- **A degenerate plane.** It omits Build, the people and K. A deployment declares that as an overlay under
  ADR-0058 (Proposed), and `spec/inventory.py` computes which theorems the declaration keeps.
- **An addition.** Charters, commit certificates and operation with no person present are capabilities the
  archetype lacks. ADR-0023's admission test says what that means: the archetype is incomplete, and the report is
  a finding about it.

### 3.5 Size and instrument ⟨20⟩

The custodian asked whether the quorum is PBFT at 3f + 1 with f = 2 for the archetype. **Yes to the size. Yes to
PBFT as the instrument at the reference, on two conditions.**

**Seven replicas, tolerating two captured.** A certificate is five signatures. The smaller memberships are the
ones §3.6's schedule falls back to.

| Replicas | Captured tolerated (f) | Certificate | Silent tolerated | Captured or slow tolerated, for the duration bound (§4.4) |
|---|---|---|---|---|
| 7 | 2 | 5 | 2 | 4 |
| 6 | 1 | 4 | 2 | 3 |
| 5 | 1 | 4 | 1 | 3 |
| 4 | 1 | 3 | 1 | 2 |

A certificate for n replicas tolerating f is the least whole number above (n + f) / 2, so that any two
certificates share an honest signer. The last column is one fewer than a certificate.

**Why seven and not four.** Four replicas tolerate one capture or one loss, and have no smaller membership to fall
back to that tolerates any capture. Seven tolerate two of either at once, and have three steps of the schedule
above a floor of one.

**The number is a placeholder**, as every number in the corpus is until something is measured. A plane of four is
a declared degeneracy (ADR-0023): it keeps agreement and has no schedule.

**PBFT as the instrument.** The letters name roles, not products (ToO §1), so what the pattern asks of P at an
exposed plane is Byzantine agreement whose certificates a third party can check (§2.5). PBFT (Castro and Liskov,
1999) gives agreement at n = 3f + 1 with certificates of 2f + 1 *(recalled, not re-read)*. The two conditions:

- **Its messages must be signed.** A governor verifies a certificate with no plane in reach. A later form of PBFT
  replaced signatures with message authentication codes, which convince only the replica they were made for
  *(recalled)*. That form cannot supply a commit certificate.
- **It needs a reconfiguration step.** PBFT as published has a fixed membership *(recalled)*. The shrink schedule
  adds a step that changes it, and that step is where an error would be an error about authority.

Three things fit as they are. The quorum clock's rules are conditions on a replica's vote (§4.4), and PBFT has a
place for a check before a replica prepares. Its view change runs on timeouts, which is liveness. A Byzantine
primary chooses the order and can stall. It cannot forge, so it decides which and never whether.

**Its cost is not measured.** PBFT's messages grow with the square of the membership. The swarm reading quotes one
simulated figure, 412.3 ms for a round among 20, as an order of magnitude at most. §3.7 says which acts wait for a
round.

### 3.6 Attrition: a shrink schedule voted in the charter ⟨19⟩

**The problem is the NATO reading's N3.** With a fixed membership, one loss beyond what the plane tolerates and no
certificate can ever form again. Under ⟨14⟩ every survivor then loses its lease at once.

**The charter carries a schedule and a floor.** `membership` lists the smaller memberships the plane may fall back
to, in order, and a **capture floor**, the least number of captured replicas it must still tolerate. At the
archetype the schedule is 7, 6, 5, 4 and the floor is one.

**A step drops one replica, and the membership being replaced orders it.**

- Any replica may propose to drop a replica it has not heard for a declared number of ticks. A replica signs the
  proposal only if it has not heard that replica either.
- The step takes a certificate of the current membership. So a membership has at most one successor, and a
  minority cut off by a partition cannot make itself a plane (TM6).
- A dropped replica does not return below the intent boundary. Adding a replica brings an issuer into force, which
  is a promotion (§2.3). Its vehicle may still hold a lease if it hears the plane again *(drafter's choice)*.
- No step takes the plane below the floor, and `FD4` forbids every other change of membership (§7.2).

**What it buys and what it spends.** This is the quorum dial of the lattice analysis: capture is how many captured
holders it takes to grant, and loss is how many silent holders still let a grant happen
(`derived/topak-safety-liveness-quorum-lattice-2026.11.05.md`). That analysis draws the dial for grant seats and
keeps consensus quorums out of it, because at a commanded plane consensus is crash-fault. At an autonomous plane
the replicas are exposed and nobody else grants, so the pair applies to them. A step spends the first to restore
the second.

| | Fixed at 7 | Schedule 7, 6, 5, 4 |
|---|---|---|
| Losses survived, one at a time | 2 | 4 |
| Losses survived at once | 2 | 2 |
| Captures tolerated before any loss | 2 | 2 |
| Captures tolerated after one loss | 2 | 1 |

**Against an adversary that can silence vehicles, the tolerance is the floor's from the start.** Jamming honest
vehicles until their replicas are dropped walks the plane down its schedule. Two captured replicas then capture a
plane that tolerated two when it was seated. A deployment that will not accept that seats a larger plane with a
floor of two (question 18).

**It strains a mechanism constant.** "A timeout is never a grant" (ADR-0024). A step adds nothing to the charter:
no entry, no budget, no longer life. But silence is what triggers it, and what it preserves is a plane's ability
to grant. The proposal accepts that because the schedule and the floor were voted, because the step is ordered by
a quorum and not taken by default, and because the alternative is this section's first paragraph. §12 names it.

**Not answered here:** where an autonomous plane's orchestrator runs, which the NATO reading asks under N3; and
whether a smaller membership should carry a smaller budget, so that a step also narrows *(drafter's suggestion;
question 17)*.

### 3.7 What waits for a round of the plane ⟨21⟩ ⟨22⟩

The custodian asked whether the time cost of Byzantine agreement is paid only for elective coordination, with
pre-authorized effects always available. **As the first revision stood, no:** the autonomous plane ordered every
admit before its effect, so every act waited for a round. The custodian then chose, among three, that **the lease
pre-authorizes** ⟨22⟩.

- **One round per lease.** The plane orders the grant: the vehicle, the alphabet, the envelope, a count of entries
  and a `ttl` in ticks.
- **The governor permits each entry under the lease**, against the floor, the bundles, the envelope and the count,
  with no further round. This is the first revision's `disconnected` mark, now read as `local` and in use whenever
  the vehicle hears its plane (§5.2).
- **The bundle marks an entry `ordered` where the tally wants agreement across vehicles**: a count that spans
  vehicles, an admit that can be void, an Observer checked at each act (§8.2). That entry waits for a round. This
  is the custodian's "elective coordination", and the election is the tally's.
- **Going alone ends the lease at once** ⟨14⟩. A pre-authorized entry is available while the vehicle hears its
  plane, and not after.

| Waits for a round | Waits for none |
|---|---|
| A lease, once | A `local` entry under a live lease |
| An entry marked `ordered` | A report to a peer topic (§8.1) |
| A tick, once per period | Listening, and applying a relayed fence or revocation |
| A seal, a heartbeat, a finding or a revocation, for the record | Any refusal |
| A step of the shrink schedule | Hold, and the terminal behaviour |

**Two things still depend on the plane completing rounds.** A lease is usable only while ticks are heard, so the
plane must order one tick per period, and `T_tick` has to be long against a round over the radios. And a vehicle's
next lease is a round. Neither is on the path of a pre-authorized act.

**What the choice costs** is in §12: for a `local` entry, no void and no Observer checked in the middle of a lease.

---

## 4. Three states of a vehicle, and what ends authority ⟨2⟩ ⟨12⟩ ⟨13⟩

**⟨12⟩ and ⟨13⟩ replace the first revision's reading of ⟨2⟩.** There the TTL was the safety parameter. Here a count
is, and the TTL is the second bound.

### 4.1 Linked, meshed, alone

A vehicle's state is what it hears. It **hears its plane** when it has applied the plane's log up to a tick that,
by its own clock, is not yet overdue (§4.4).

| State | The vehicle hears | Who permits an entry | What ends authority |
|---|---|---|---|
| **Linked** | Its plane, and the plane is in contact with the intent boundary | The governor, for a `local` entry under its lease. The plane, for an `ordered` one. A person, for an irreversible one | Anything a plane above orders: a fence, a revocation, a narrower intent. And everything in the next row |
| **Meshed** | Its plane, and the plane hears nothing from above | The governor and the plane, as above. Nobody, for an irreversible entry | The plane's own subtractions and findings; the lease's count; `K_up`; the intent's budget and its `expiry` |
| **Alone** | No tick that is not overdue | Nobody | Nothing is left to end. The lease ended when the vehicle became alone ⟨14⟩ |

### 4.2 What the clock was asked to do, and what the corpus does instead

The first revision reversed ADR-0032 §1 below the intent boundary: an intent's `expiry` and a lease's `ttl`, each
read on a local clock, were what ended authority. The custodian asked whether a quorum of governors, a monotone
log and each layer's fence could do it instead. **They can, for a bound in effects.** The corpus has met a clock
problem four times and has not once answered with a better clock:

| Precedent | What it did | Used here |
|---|---|---|
| ADR-0034's nonce is a hash of epoch and log index, "so freshness comes from the log and not a clock" (ToO §2.6). ADR-0050's sign-on is fresh "because of what it names" (ToO §7.10) | Took an interval's origin from the log | §4.4: an intent names a tick |
| ADR-0039's bound on unread effects is "a count, not a time" (ToO §5.4). The round bound and ADR-0055's activation budget are counts | Counted the mechanism's own acts, which have no drift | §4.3: the lease's count and `K_up` |
| ADR-0039 coupled liveness to admission, so that a dead Observer stops its Thinker | Made silence fail closed | §4.3: the intent boundary is the plane's Observer |
| R8, the break-glass TTL, was withdrawn because it needed trusted time, and ADR-0045 refused a time source (ToO §10) | Withdrew the interval | §5.2: a vehicle alone holds no lease |

**A log orders and does not measure.** ADR-0032 rejected deriving timing from the causal frame: "Causality orders
events and bounds no interval." A fence is a message, and a plane that is cut off cannot tell "not revoked" from
"revoked, and not yet heard". So it has to stop on something of its own. A count of its own acts is exact, and
that is ⟨12⟩. A count says nothing about a plane that waits a week and then acts, and that is why ⟨13⟩ keeps a
bound in duration.

### 4.3 The bound in effects ⟨12⟩

**The intent boundary is the plane's Observer.** This is `R3-observer-live`'s shape (ToO §5.4), pointed upward.

- **The plane's record goes up as it is made.** The plane's log, with each lease's sealed record (§5.4), is handed
  to the intent boundary while the link holds. The first revision reconciled once, on contact.
- **The intent boundary answers with a watermark.** When its mechanism has archived a segment and run its checks,
  it orders a watermark: the plane index it has read through, the digests of the lease records sealed in that
  segment, and the fences of every plane above. The watermark comes down with a commit certificate. *(Drafter's
  assumption: it is the mechanism's act and no person's. Question 12.)*
- **The plane charges what is outstanding.** A lease's whole count is charged when the lease is granted, and an
  `ordered` entry when it is admitted. A charge is released when a watermark covers it.
- **The rule.** The plane grants no lease, and admits no `ordered` entry, that would take the outstanding charge
  to `K_up`. That is the strict form: "at most `K_up`" lets one more through, which ADR-0039's model found of `K`.
- **Each governor keeps the same account for itself.** It accepts a lease only if the counts of its own leases
  that no watermark covers, with this one, stay under `K_up`, and it checks each watermark's certificate against
  the chain. A plane is a havoc issuer (§2.4), so a governor does not take its plane's word for what has been
  read.

What is charged is an effect: a `local` entry and an `ordered` one, as ADR-0042 §2 counts effects for an Observer.
A report to a peer topic is not charged (§8.1), and a tick is not an effect.

| Property | Statement |
|---|---|
| **Effects after a revocation are bounded** | After the intent boundary orders a revocation or a fence, the vehicles of an honest plane produce fewer than `K_up` further effects. Under a captured plane, each honest vehicle produces fewer than `K_up`. A vehicle revoked by its own plane produces at most what is left of its lease's count. No clock is read |
| **Stale rules are bounded** | A narrower intent or a tightened bundle cannot reach a plane that is cut off. Superseded rules govern fewer than `K_up` effects there |
| **Exposure is bounded** | An intent never grants more leases than its budget. A lease never permits more entries than its count. An entry never runs past its extent (§5.3) |

**The argument for the first row.** Let *w* be the last watermark ordered before the revocation. Every later
watermark carries the moved fence, and a plane or a governor that hears one stops. Every lease *w* covers is
sealed and produces nothing more. So every effect after the revocation is charged to a lease or an entry that *w*
does not cover, and those charges together stay under `K_up`. An adversary can deliver *w* late or not at all,
which only lowers what is released.

**What it does to a jammed plane.** With the link above cut, no watermark arrives, the charge only grows, and the
plane stops granting before `K_up`. Vehicles spend the leases they hold and then hold. That is the fence failing
closed. The first revision's pushed fence failed open: no news meant carry on until `T_intent`.

**What reading buys besides.** What the intent boundary has read is archived above. "A captured plane's log is
not evidence" (§5.4) now holds of the unread tail only, fewer than `K_up` effects.

### 4.4 The bound in duration: a clock the replicas hold together ⟨13⟩

**Why duration still matters.** A count does not stop a plane that idles and then acts on an old intent. The
world an envelope was voted for changes with time. And a bundle's time windows (§7.1) need a clock under any
design.

**The plane's clock is its ticks.** Each replica keeps one reading of its own monotonic clock, taken when it
applied the plane's charter. Everything else is in the log.

- **A tick is a numbered entry.** Tick *τ* says that *τ* periods of `T_tick` have passed since the charter was
  applied. The numbers need not be consecutive.
- **A replica never signs a tick ahead of its own clock.** It signs tick *τ* only when its own elapsed time has
  reached *τ* periods.
- **A replica never signs a grant behind its own clock.** It signs no lease and no `ordered` admit while, by its
  own clock read with the early margin (ADR-0031 E1), the next tick is due.
- **Every interval is a number of ticks from a named tick.** An intent's `expiry`, a lease's `ttl` and an entry's
  duration are tick numbers, so each end is a comparison in the log. It is the same on every replica, and it can
  be checked again at apply, which a per-replica clock cannot (ToO §15 found that of `T_obs`).

**What that gives.** While captured and slow replicas together are fewer than a certificate, at most four of
seven (§3.5), every certificate includes a replica that is neither. That replica signed only because, by a sound
clock, the latest tick was current. So at every grant the plane's tick count is less than one period behind real
time, and **no grant is made under an intent more than one tick period past its `expiry`**. A lease's `ttl` ends
no later than its intent's `expiry`, and an intent's no later than any charter's above it, so the bound on grants
bounds effects too, up to the governor's residual below. The first revision asked that every clock be sound. This
asks it of enough of them.

**Ticks are numbered from the charter and not from the tick before.** *(Found while this section was drafted.)* If
a replica measured each period from the last tick, an adversary that stalled the plane for a week and then let
one tick through would have hidden the week: the count would have moved by one. Numbered from the charter, the
first tick after a stall carries the week.

**The origin answers the NATO reading's F1.** The first revision did not say when an interval starts, and an
interval that starts at receipt can be started late by whoever holds the message. Now an intent names a tick the
plane has handed up, and its `expiry` is a count from that tick. A lease's `ttl` counts from the tick at which
the plane ordered the grant. Either, withheld for a day, arrives a day old. *(The first intent is the promotion's
and is granted before the plane has ticked. It would count from the charter, tick zero. Question 13.)*

**No time crosses a boundary.** A replica reads its own clock and signs or does not. No timestamp is exchanged and
no external time is read, so ADR-0032 §3 holds as written: no safety decision reads a clock a principal supplies.

**A governor's own clock decides one thing: that the next tick is overdue** ⟨18⟩. It counts an entry's duration in
ticks. When a tick is overdue it treats the vehicle as alone and ends the lease (§5.5). So a slow governor clock
stretches at most the entry in progress, and only when the plane's ticks have also stopped reaching it. That is
the residual. It has the shape of ADR-0045's finding 2: a bound on a declared value, plus drift.

### 4.5 The trades are declared, not designed away

| Value | Small | Large |
|---|---|---|
| `K_up` | A jammed plane stops after few effects | More effects under a revoked intent or superseded rules |
| A lease's count | More rounds of the plane, and a vehicle more often between leases | More effects with no order, no void and no Observer in between (§5.6) |
| `T_tick` | A short loss of signal ends a lease | A longer stretch for an entry in progress when the plane is gone |
| `T_intent` | A plane stopped at `K_up` gives up waiting for the link sooner | An idle plane may act on an older intent |

All four are declared in the floor's values, as `T_irrev` is. Like every number in the corpus they are
placeholders until something is measured. The first revision's `T_alone` is gone: a vehicle alone holds no lease.

### 4.6 Postures

The glossary defines the postures by enabling condition, and says Run's window leaves HOTL.

| Effect | State | Posture | Enabled by |
|---|---|---|---|
| Irreversible | Linked only | HITL | A person's signed act, one per effect, ordered at the intent boundary (§6) |
| Reversible | Linked | HOTL, as Run today, with the intent boundary reading as the plane works | A lease under an intent. A person can stop it |
| Reversible | Meshed | Unattended. Observers still read and their findings still subtract. Fewer than `K_up` effects are unread above | A lease under an intent |
| Any | Alone | None. Nothing is enabled | Nothing |

**The meshed row is new to the corpus.** A5 says unattended operation is something "the pattern does not model".
Meshed, ADR-0032 §4's budget has no `D`, since no person can respond. **Nothing a meshed plane does may rest on a
person's response.** What bounds it is `K_up` and the envelope. What an entry can do at worst, inside its
envelope, is what the tally voted to accept, and nothing checks that the vote was right. It is the floor-fitness
problem again (ToO §12 item 2).

---

## 5. The vehicle: a governor, a stack and three kinds of entry ⟨6⟩ ⟨14⟩

### 5.1 What is Byzantine and what is trusted

The custodian's "fully Byzantine" holds of the stack. It cannot hold of the whole vehicle: something on board must
check a chain and gate the actuators, and that part is trusted. The governor:

- verifies the chain and holds the lease and the vehicle's key;
- hosts the vehicle's replica of the autonomous plane *(drafter's assumption; question 3)*;
- evaluates the floor in Cedar and each bundle on the chain as a Wasm module (§7.1);
- **permits each `local` entry under the lease, and counts it** ⟨22⟩;
- **lifts its own facts**: elapsed time, position, the lease's count, an entry's extent. No safety decision reads
  a clock a principal supplies (ADR-0032 §3), and by the same rule none reads a position the stack supplies;
- hosts each tool as a Wasm component with one capability, its declared channel, which for a vehicle is an
  actuator interface. This is channel fidelity as ADR-0034 A2 has it for Run, and the reference's `wasmtool` is
  its start (`mechanism/README.md`);
- **holds the radio.** The link to the plane and the peer topics are both on its side (§8.1). So a stack cannot
  make its own vehicle alone, which the NATO reading's F2 asked;
- records every entry it permits or refuses and every report it sends or delivers (§5.4), and carries out hold
  and the terminal behaviour (§5.5).

Models stay out of the trusted base. The trusted base still grows, on every vehicle (§11).

### 5.2 Three kinds of entry

⟨6⟩ gave the vehicles a disconnected alphabet. Read with ⟨22⟩ and ⟨14⟩, it is the set of entries a governor may
permit without the plane's order. It is in use whenever the vehicle hears its plane, and nearly empty when the
vehicle is alone.

| Entry | Permitted by | Ordered | Available |
|---|---|---|---|
| **`local`**: an actuation, or a report to the round topic | The governor, under the lease, the floor, the bundles, the envelope and the count | Not before the effect. The lease's record is sealed and ordered when the lease ends | While the vehicle hears its plane |
| **`ordered`** | The autonomous plane | Before the effect | While the vehicle can reach a quorum |
| **A report to a peer topic** (§8.1) | The governor, under the floor and the bundles | Never. Recorded by digest | While the vehicle hears its plane. Alone, the beacon only |

**A vehicle that is alone keeps three things** ⟨14⟩:

- **its terminal behaviour** (§5.5), which nobody permits because it was fixed at seating;
- **listening**: a relayed fence or revocation still applies, and a tick heard again ends the state;
- **a beacon**, where the rules of engagement permit one: a report of fixed schema, of facts the governor
  measures, counted per lease.

It permits no actuation. So a stack gains nothing by being alone, which removes the motive the swarm reading's Z4
found.

No agent seat's alphabet holds an irreversible entry, in any state, and no irreversible entry is marked `local`
(§6).

### 5.3 What an entry declares

The allowlist entry has five parts (ADR-0049). It gains a sixth, `effect`:

| Field | Says |
|---|---|
| The class, with its `T_irrev` | `reversible` or `irreversible` |
| How it is permitted | `local` or `ordered` (§3.7) |
| **Its extent** ⟨18⟩ | How far one entry runs: one act; a number of ticks; or a distance or a region, which the governor measures |
| Whether it is the beacon | At most one entry per seat kind |

It is promoted with the bundle and voted like any entry.

- **An entry with no extent does not load**, as a bundle whose allowlist is not well-formed does not (ToO §2.10).
  Without an extent a count bounds nothing: one entry could run for ever. This is the grain the swarm reading's
  Z1 asked for.
- **When an extent ends and no entry follows, the governor holds.** Hold is fixed at seating, as the terminal
  behaviour is, and the stack does not choose it *(drafter's choice; question 14)*.
- **An extent that is not a count of ticks is a measurement.** The governor's position source is already a trust
  root for area checks (§11).
- **An effect class is a declaration**, as a label is (A15): an irreversible effect declared reversible is seen by
  nothing here. The same holds of an extent declared shorter than the act.

### 5.4 The record

- **Under a lease.** The governor writes each entry it permits or refuses, and each report it sends or delivers,
  to a chain on the vehicle: hash-linked, signed with the vehicle's key, and numbered by the per-lease sequence
  the lease already carries (ToO §4.2). A send and a delivery are recorded by digest, as ADR-0020 records a denial.
- **At the lease's end, the seal.** The governor closes the chain and the plane orders it as one entry, running
  the mechanism checks at that position. A vehicle that became alone hands its chain up when it hears its plane
  again.
- **From the plane to the intent boundary.** The plane's log and its sealed records go up while the link holds,
  and the watermark comes back (§4.3). After a cut, the intent boundary reads the backlog and checks it against
  what it ordered meanwhile.
- **Void works for an `ordered` entry.** An admit that fails at apply is "ordered, recorded, without effect"
  (ADR-0033 §4).
- **Nothing a governor permitted is void.** The effect has happened. A check that fails at the seal, or above, is
  a **finding** against the lease or the intent, and it can only subtract.
- **A captured vehicle's chain, or a captured plane's log, is not evidence.** It says what its captor signed.

### 5.5 Hold, terminal behaviour, and why an ending grants nothing

"A timeout is never a grant" is a mechanism constant (ADR-0024), and a lapsed orchestrator "takes no default edge,
because an edge taken on a timeout would be a grant made by a timeout" (ToO §2.11). A body in motion still has to
do something when its lease ends. The proposal keeps the rule this way:

- The terminal behaviour is part of the seating, voted with it. Its envelope is the lease's, or a route the tally
  voted. Hold is fixed the same way.
- The stack does not choose either and does not carry them out. A recovery function in the governor's trust
  domain does.
- Where a class has more than one terminal behaviour, a fixed rule over facts the governor measures selects one.

**A lease ends** when its count is spent and its last entry's extent has run, at its `ttl`, when the plane ends or
revokes it, when a fence arrives, and **at once when the vehicle becomes alone** ⟨22⟩. The governor ends it where
it stands, and the plane orders the end when it learns of it, as ADR-0031 E1 has expiry: local, and then ordered.
A vehicle that hears its plane again may be granted a new lease, charged to the intent's budget *(drafter's
choice; question 15)*.

An ending ends the stack's authority and selects nothing the promotion did not already fix.

**The corpus's answer to failure is to stall, and "a stall that never ends is safe"** (ToO §12 item 21). That is
false of a vehicle in flight. Each vehicle class therefore declares a safe state, and reaching it in bounded time
is an obligation on whoever builds the vehicle. No module here can prove it. It is an assumption of use with an
owner (§11).

### 5.6 Coupling

`R3-observer-live` refuses `Actuate` under a `thinker` seat with no live cell Observer (ADR-0041).

- **For an `ordered` entry it applies as written**, at the plane's admit.
- **For a `local` entry it applies at the grant** ⟨22⟩. A lease's count is at most `K`, and a vehicle's next lease
  is granted only once its cell Observer has read the last one to its seal, which is ADR-0039's rule across
  rounds (ToO §5.4). So at any moment at most `K` of a Thinker's effects are unread by its Observer, which is the
  bound ADR-0039 states. What is given up is the refusal in the middle of a lease.
- **A cell's Observer is seated on another vehicle** of the same plane *(drafter's choice; question 9)*, so it
  does not share hardware with the Thinker it watches. The governors' radios carry the round's payloads to it,
  and the digests are in the sealed record *(drafter's choice; the swarm reading's Z1 asked what carries them)*.
- **Alone, there is nothing to couple.** The vehicle permits no actuation.

*(Not taken: a governor checking `R3` at each act against the marks it has applied from the plane's log. A Thinker
would then wait on its Observer's heartbeat, which is a round of the plane, on the path of a pre-authorized act.)*

---

## 6. An irreversible effect is a person's ⟨4⟩

**The custodian asked whether this is HITL. It is**, in the glossary's sense of a posture defined by its enabling
condition: an irreversible effect is enabled only by a signed act of a person, made for that one effect.

**What the corpus says today.** For an effect irreversible on emission, "the effect must not be reachable from the
alphabet at all" (ADR-0032 §4; A10). The budget `W + L + D < T_irrev` is HOTL's: it buys time to detect and stop
after emission. Under HITL the judgment comes before the emission and no budget is needed. The proposal therefore
narrows the reach where ADR-0032 removes it: not reachable from any agent's alphabet, not reachable below the
intent boundary, and reachable from one seat kind that a person holds. **That relaxes ADR-0032 §4 as written.** The
precedent is the `emergency` seat, whose actor is a person (ADR-0052; ToO §3.3).

**The `release` seat.**

- **A person holds it**, with a key, and nobody else in the round. No model's Persona binds to the kind.
- **It is seated at a commanded plane and never at an autonomous one** ⟨10⟩, and only where the charter carries
  `release`.
- **A roster's quorum activates it** for one named person and one round, as an emergency seating is activated
  *(drafter's choice; question 6)*. The roster is anchor-issued (ADR-0013), so no plane below the root can mint a
  person, and a governor checks the key against the roster resident on the vehicle.
- **Its alphabet is `Actuate` on irreversible entries in its envelope, and `Report`.**
- **The person is the actor, not a countersigner** *(drafter's choice; question 5)*. The stack may `Report` what
  it perceives. That report is ingress to the person, labelled as untrusted, and it enables nothing. A design in
  which an agent proposes and a person approves would put the agent's output on the path to the effect.
- **Each act is one admit.** It names the entry, its inputs, the vehicle and the fences. It is ordered at the
  commanded plane and delivered with that plane's commit certificate. The autonomous plane relays it. The
  governor's interlock checks the person's key, the commanded plane's certificate, that the act is fresh and
  unused, and that the entry is in the seat's envelope. **The vehicle must be linked.** **Fresh** has the meaning
  §4.4 gives every interval: the act names a tick of the vehicle's plane, and the interlock refuses it more than a
  declared number of ticks later *(drafter's choice; question 16. This is the third case of the NATO reading's
  F1)*.

**What the mechanism records, and what it cannot judge.** It records who acted, on what, through which vehicle and
when. It does not record why: "the reason is unknown to the mechanism, by construction" (ADR-0052). Whether the act
was right is the person's judgment, and the mechanism checks none of it. It also "cannot tell a person from a
program holding the person's key" (ToO §3.3). A5 applies in full: a trained, authorized person is present, and
this proposal adds that they can see what the act requires them to see.

**The cost.** With no link to the intent boundary there is no irreversible effect, and an adversary who jams that
link gets this for nothing. The boundary register already criticizes "fail-closed uniformity presented as
costless" (ToO §10). Here it is presented as a cost, and accepted.

---

## 7. Rules of engagement live in three places ⟨5⟩ ⟨7⟩

| Part of the rules | Where it lives | Why there |
|---|---|---|
| Standing rules that hold for every mission | The Cedar floor, in force at every plane and every governor | It is the verified object, and no bundle can weaken it |
| A mission's rules that can be lifted mechanically | A promoted bundle, compiled to Wasm | Voted by digest, able only to refuse, and evaluated the same way at a plane and on a vehicle |
| Rules that need a judgment about the world | Nowhere in the admit path | ADR-0007: no semantic judgment is an enabling condition |

### 7.1 The mission's rules are a promoted Wasm bundle

A bundle can express what a mechanical lift can supply: areas, time windows, which entries a seat kind may use,
counts, a declared control mode per effect class, and lists that come from a declared source and carry its label.
A time window is a range of the plane's ticks (§4.4). A bundle may also refuse a report to a peer topic, by seat
kind, rate or label, and may refuse an entry once the stack has read a peer's report in the clear (§8.1).
A commanded plane tightens by promoting a bundle, which is appended (§2.2). A commander tightens faster by
narrowing a value in the next intent (§2.3). Loosening needs a promotion at a plane whose charter allows it, and
otherwise goes up the tree. That asymmetry is the one the corpus already has between subtraction and grant.

**The Wasm path exists at the reference.** `topak-bundle` loads a signed bundle into an in-process engine bound to
the lease's revision, as the fallback when the sidecar cannot answer (`mechanism/README.md`; ToO §15). At an
autonomous plane and on a governor that engine is the only one. Stale bundles are monotone-safe (ToO §3.1), which
is what makes local evaluation sound: an old bundle on a vehicle can refuse too much and cannot allow what the
floor refuses.

**"Missions are promoted bundles"** is read as: one tally votes a mission's bundle revision, its mesh and the
charters and seatings it needs, together (ADR-0024 A4, pending). The bundle is the mission's rules. The workflow is
its plan (§8).

### 7.2 The floor, with a `federation` stage

**"In force" is a precondition this proposal cannot meet.** No floor text is ratified. The floor is ratified when
a bootstrap reviewer finds it fit, and no test for fitness is written (G11 §2.2 and item 87; ADR-0029 A4). For
this floor, whether the standing rules are the right ones is a legal judgment as much as a technical one. A grant
seat with that named role is suggested *(drafter's suggestion)*.

The stage would follow `workflow` in `floor/proposed/README.md`. The ids are placeholders.

| Id | Kind | Says |
|---|---|---|
| `FD1-charter-narrows` | forbid | No seating of a plane, and no intent, whose charter exceeds its bound in any field |
| `FD2-lease-within-charter` | forbid | No grant whose lease exceeds the granting plane's charter: an entry outside its alphabet, a `ttl` above its `ttlMax`, an expiry after its own |
| `FD3-budget-spent` | forbid | No grant, and no seating of a plane, once the charter's budget is spent |
| `FD4-autonomous-adds-nothing` | forbid | At an autonomous plane: no promotion, no seating, no operator's request, no bundle change, no grant but a node's lease under a live intent, and no change of membership but a step of its charter's schedule |
| `FD5-irreversible-release-only` | forbid | No `Actuate` of an irreversible entry under a seat whose kind is not `release` |
| `FD6-irreversible-from-commanded` | forbid | No admit of an irreversible entry without a commanded plane's commit certificate for that act |
| `FD7-local-marked` | forbid | No permit by a governor of an entry its bundle revision does not mark `local`, and none of an irreversible entry |
| `FD8-local-bounds` | forbid | No permit by a governor with the lease's count spent, past its `ttl` in ticks, or under a lease that has ended |
| `FD9-release-seating` | forbid | No `release` seating of a key that is not on the anchor-issued roster, none at an autonomous plane, and none at a plane whose charter lacks `release` |
| `FD10-outstanding-bound` | forbid | At an autonomous plane: no grant and no `ordered` admit that would take the outstanding charge to `K_up`. At a governor: no lease accepted that would take its own to `K_up` |
| `FD11-alone-permits-nothing` | forbid | No permit by a governor whose vehicle is alone, but the beacon within its count |
| `FD12-topic-declared` | forbid | No report to a peer topic the promoted mesh does not declare for the seat, and none that names a recipient |
| `FD13-step-in-schedule` | forbid | No step of membership that the charter's schedule does not hold, and none below its capture floor |
| `FD14-count-within-K` | forbid | No lease whose count exceeds `K`, or its charter's `countMax` |

**Every new entry subtracts. Two existing entries are relaxed**, and each relaxation routes as one (ToO §3.2):
`B10-only-thinkers-author` gains an exception for a `release` seat's `Actuate`, as it has for an `emergency` seat,
and `R3-observer-live` is scoped to admits a plane makes, with a `local` entry covered at its lease's grant (§5.6).

**The schema gains** the kind `release`; the entities `Plane`, with its charter and kind, and `Topic`; `effect` on
an entry; and, in the Run context, who is permitting, whether the vehicle hears its plane, whether the count is
spent, the outstanding charge and the tick. The lift
supplies these and the floor trusts its inputs, as the README already says of every stage.

### 7.3 What no policy here expresses

Identification, intent, necessity and proportion are judgments about the world. A classifier's output enters the
system only as a finding, and a finding may subtract authority and never add it (ADR-0007; ToO §2.2). So these
parts of a mission's rules are enforced by nothing in this design. For an irreversible effect they are the
judgment of the person at the release seat. For everything else they are, at most, something an Observer may
object to after the fact.

---

## 8. Missions as workflows, and how vehicles coordinate

- **A DAG is a plan with branches**, promoted at a commanded plane. At a decision point an orchestrator chooses
  among edges the mechanism has already enabled, so it "decides how good the work is and never whether it is safe"
  (ToO §2.11). A person may hold an orchestrator seat at a commanded plane *(drafter's suggestion; question 10)*.
- **A mesh is promoted at the intent boundary and runs at the autonomous plane.** A node is one round of one
  cell, and a cell is a vehicle's stack with its Observer. Loops are allowed, the number of turns is decided at
  run time, and the activation budget is the intent's. That is the "field command autonomy" of the custodian's
  mapping: choice among enabled edges, bounded in count, with no person present.
- **Vehicles coordinate in two ways** ⟨21⟩. By talk, on peer topics: it waits for no round of the plane, and it
  settles nothing (§8.1). By order, through an entry the bundle marks `ordered`: one round, and every vehicle sees
  the same outcome (§8.2). The first revision had only the second, "the mechanism is the bus" (ADR-0055), and its
  "only that way" is withdrawn.

### 8.1 Stacks talk on declared topics, and nothing they say enables anything ⟨15⟩ ⟨16⟩ ⟨17⟩

The custodian asked: no admit, deny only, coordination within the rules of engagement? **Yes, with one
correction: a send still needs a permit. What it does not need is an order.** The corpus already separates the
two: "Ordering is not authorization" (ToO §4.1).

**The rule.** Nothing a peer originates is ever an enabling condition. For every permit and every admit, at a
plane or a governor, the same request with every item received from peers removed is still permitted. This is
ADR-0047's direction, "delivering more in the clear buys a narrower round" (ToO §2.10), applied between vehicles.

**Three kinds of traffic share the governors' radios.**

| Traffic | What the receiver does | Why it is safe |
|---|---|---|
| **Certified facts, relayed**: fences, revocations, ticks, intents, leases, watermarks | Its governor verifies the certificate against the chain and applies it. A subtraction applies on receipt, before it is ordered anywhere | The peer is transport and originates nothing. A fence reaches any vehicle in range of one that heard it |
| **A governor's measured facts**: its position, a range | The receiving governor may refuse on them and never permits on them | A captured governor that lies can only stop others |
| **A stack's report**: tracks, plans, bids for a task | Its governor delivers it to its stack as labelled ingress | The stack is Byzantine already, and every effect it then requests is checked without reference to the report |

**Sending is an effect, permitted and not ordered** ⟨16⟩. ADR-0015 counts an emission as an effect, and a
transmission reveals the vehicle and can carry `restricted` content. So:

- a send is a `Report` to a declared topic, permitted by the governor under the floor and the bundles. The rules
  of engagement can refuse it: silence, a rate, a label;
- it is not ordered, and it is not charged to `K_up`, or chatter would spend the plane's authority. It has a count
  of its own per lease;
- it is recorded by digest on the vehicle's chain (§5.4).

**Receiving is ingress, and no effect.** The corpus makes a read of live state an `Actuate` "because the request
itself leaves the membrane" (ToO §2.9). Here no request leaves: the governor delivers what arrives on the topics
its seat is declared to hear. It is a sixth item on the Listener's list, after ADR-0054's `input`.

- **Its label is the topic's declaration, and never less than `untrusted`.** A sender's governor may add names. A
  captured one may lie, and a label that can only be raised makes the lie harmless (question 19).
- **Delivered clear, it joins `clearSet`**, so `R5` to `R7` follow it, and a bundle may refuse further entries
  after it (§7.1). **Listening narrows.** A bundle may deliver a topic as a handle to a seat kind that should
  route it and not read it.

**Topics are promoted with the mesh, and nobody is addressed** ⟨17⟩. The mesh declares each topic: its schema,
which seat kinds may report to it, which nodes hear it, its label and its delivery mode. A stack reports to a
topic and names no recipient. So "Workers never address each other" (ADR-0055 §7) stays true.

**Why this is not the choreography ADR-0055 rejected.** Its objection is: "Every reading in which cells react to
each other directly puts a model's output in charge of what runs next." Here the mechanism still decides what
runs next: no guard reads a peer's report, and no report causes a lease. A stack chooses among entries its lease
already permits, which is the orchestrator's position: which, never whether. What changes in ADR-0055 §7 is one
sentence, "No variant publishes to another cell or subscribes to anything."

**Why no order is needed.** An order before an effect, and an Observer coupled to it, exist so that what the
effect can cause is bounded before it lands. A report can cause nothing: the rule above says so of the receiving
side, and the governor's permit bounds the transmission itself. **So nothing may rest on a report being read.** An
Observer reads the record afterwards, and its finding subtracts.

**What it costs.**

- **Talk settles nothing.** A stack may claim a task, and two may claim the same one. A claim that others honour
  makes them refrain, which only subtracts, and a stack that claims everything stalls its peers. Where the tally
  wants one vehicle and no more, that is §8.2.
- **The tally votes the joint worst case.** Stacks that can talk can act together inside their envelopes. That
  was already the premise, since stacks of one lineage may fail alike, and the budget in effects is what bounds
  it (§4.3).
- **A swarm of one model cannot alternate lineages.** ADR-0054 wants independent Thinkers at the two ends of a
  clear edge, and every deployment today declares that it has them (D-0054-1). Vehicles of one build have one
  lineage and cannot declare it of a topic delivered clear. They deliver peer reports as handles, or the gap is a
  declaration of its own.
- **A finding has further to travel.** In a mesh, "a finding against any activation in the history closes every
  edge downstream" (ToO §2.11). A report read off the edges is not on that history. The delivery records on each
  vehicle's chain say who read what, and they reach the plane only at the seal.

### 8.2 Agreement is an ordered entry ⟨21⟩

Where an outcome must be the same for every vehicle, the stacks ask the plane. The bundle marks such an entry
`ordered`, and the plane admits it before its effect, in one round (§3.7).

- **A count across vehicles**: one vehicle per task, or at most three in an area. A bundle can express counts
  (§7.1), and only the plane's order makes a count the same for everyone.
- **An admit that can be void**, where a finding or a revocation must be able to overtake the act (§5.4).
- **An Observer checked at each act**, where a lease's worth of unread effects is too many (§5.6).

Which entries a mission marks is the tally's choice, and the archetype marks none (question 20). Stacks negotiate
by talk and commit by order. **Alone, a vehicle coordinates with nobody**: it permits no
actuation, and its beacon tells its peers where it is.

---

## 9. Threat model ⟨3⟩

The corpus's adversary is the agent. A deployment of this kind adds an adversary that attacks links, hardware and
planes. Each row says what bounds the adversary and what is left.

| # | Adversary | What it can do | What bounds it | What is left |
|---|---|---|---|---|
| TM1 | **The stack**, Byzantine as ADR-0007 has it | Request anything, at any time | The governor, the alphabet, the envelope | Anything inside the envelope was voted acceptable. What the vehicle's body does that no entry names is outside the alphabet |
| TM2 | **The link adversary**: jams, drops, delays, replays, injects | Cut the link above a plane, making it meshed; cut vehicles from their plane, making them alone; delay a revocation; block every irreversible effect | Certificates stop forgery. Fences and sequence numbers stop replay. `K_up` bounds what a delay buys, in effects, and an intent's named tick stops a withheld one from starting late (§4.3, §4.4) | Denial is always available to it, and the response is predictable: a plane cut off above stops granting before `K_up`, and a vehicle cut off from its plane loses its lease within a tick period and does its terminal behaviour. Silencing vehicles also walks a plane down its shrink schedule (TM12) |
| TM3 | **A captured vehicle** | Extract the key and the lease; act as that principal and as one replica; sign any local record; report anything to its peers | The lease's envelope and what is left of its count. Revocation, once its plane knows. One replica is within what Byzantine agreement tolerates. Its reports are `untrusted` and enable nothing, and its governor's facts can only make others refuse (§8.1) | The interlock is moot when the effector itself is captured. Resistance to tampering is the builder's, and is a trust-root residual |
| TM4 | **Compromised replicas, fewer than a third** of a plane | Lie to the others | Byzantine agreement and commit certificates (§2.5) | Under crash-recovery consensus one such replica can propose an admit no floor evaluated (A9). That is why §2.5 asks for more |
| TM5 | **A captured plane**: a quorum of its replicas, which for an autonomous plane means that share of its vehicles | Issue any lease within its charter, to anyone; ignore fences; falsify its log | The charter or the intent, checked by every governor. Each honest governor keeps its own account against `K_up` and checks every watermark itself (§4.3). An autonomous plane adds nothing: it cannot seat, promote or release | Fewer than `K_up` effects from each honest vehicle, within the intent. Its ticks are the captor's, so the duration bound there rests on each honest governor's own clock, which treats a lagging tick as overdue |
| TM6 | **A partitioned mesh** | Leave two groups of vehicles each believing it is the plane | A certificate needs a quorum of the current membership, so at most one side grants and at most one side can order a step of the schedule. The other side's vehicles are alone | A mesh split into pieces all too small admits nothing, and every vehicle is alone |
| TM7 | **An insider with a key**: an operator or a release person | Whatever that seat may do | Attribution. An operator's add needs a live peer (ADR-0050) | The mechanism cannot tell a person from a program holding the key. A wrong act by a release person is recorded and not prevented |
| TM8 | **Navigation deception** | Move the envelope in the world by falsifying a governor's position | Nothing in this design | The navigation source is a trust root with this residual. Time is not exposed the same way, since no external time is read |
| TM9 | **Deception of perception**, the stack's or a person's | Make the stack or the person wrong about the world | For the stack, the premise already assumes it. Perception never adds authority | A deceived person at a release seat is a semantic failure. Nothing here sees it |
| TM10 | **Supply chain**: weights, tools, bundles | Ship a bad artifact | Promotion by digest. Lineage independence, which is Proposed (ADR-0035) | As the corpus states it today |
| TM11 | **A colluding Observer** | Stay silent | Nothing. Coupling cannot see collusion (A13). Seating it on another vehicle removes shared hardware, not shared lineage | As the corpus states it today |
| TM12 | **Attrition**: vehicles destroyed, or silenced until their replicas are dropped | Take a plane below a quorum of its membership | The shrink schedule (§3.6): at the archetype, four losses one at a time or two at once | Below the capture floor the plane ends and every survivor is alone. An adversary that can silence vehicles gets the floor's tolerance from the start |
| TM13 | **A stack that lies to its peers**, under a signature that verifies | Report false tracks, claim every task, send another stack text meant to steer it | Nothing a peer originates enables anything. Its reports are `untrusted`, and listening narrows (§8.1) | An honest stack misled inside its own envelope, and peers stalled by claims. These are the swarm reading's two hardest classes, and nothing here rests on detecting them |
| TM14 | **Clock faults** among a plane's replicas | A slow clock holds an intent open, and a fast one ends it early | Captured and slow replicas together fewer than a certificate (§4.4). A fast clock only subtracts | Past that, the duration bound is void. The bound in effects still holds |

**Out of scope**: the destruction of vehicles or planes, other than its effect on a quorum, which is TM12; attacks
on sensors other than as TM8 and TM9; what an adversary learns by watching which planes and vehicles talk; and the
security of the anchor's custody, which ADR-0025 declares per deployment.

---

## 10. What would be checked

By ADR-0046's method each property ships with a mutation that breaks it and nothing else, and a witness that the
behaviour it constrains is reachable. **None of this is written.** The modules would be drafted by
`skills/writing-tla-specs-and-proofs/`.

| Module | Property | A mutation that must break it |
|---|---|---|
| `Federation` | `CharterNarrows`: every seated plane's charter is its parent's or narrower, field by field | `M_WIDEN`: a seating that widens one field |
| | `LeaseWithinChain`: every lease a governor accepts is within every charter on its chain | `M_LASTLINK`: the governor checks only the granting plane's charter |
| | `HavocPlaneBounded`: with one plane signing anything its key can sign, no governor permits outside what the root's tally voted | `M_TRUSTPLANE`: the governor takes a plane's word for its own charter |
| | `BudgetConserved`: leases issued under a charter, and under every charter below it, never exceed its budget | `M_NODEBIT`: a child's budget is not debited from its parent's |
| | `AnyPlaneFences`: after any plane on a chain moves its epoch, no plane or governor that has heard it permits or admits under a lease below it | `M_STALEEPOCH`: a check compares only the granting plane's epoch |
| | `OneSuccessor`: every step of membership is in the charter's schedule, at or above its floor, and ordered by a quorum of the membership it replaces, so a membership has at most one successor | `M_MINORITYSTEP`: a step ordered by fewer. `M_BELOWFLOOR`: a step past the floor |
| `Intent` | `EveryEffectHasAnIntent`: every effect has an intent, or a person's act, ordered at a commanded plane before it | `M_NOINTENT`: the autonomous plane grants a node's lease with no live intent |
| | `EveryEffectHasALease`: every reversible effect below the intent boundary has a lease ordered at its plane before it, and is within that lease's count | `M_NOCOUNT`: the governor does not count |
| | `IntentNarrows`: every intent is within its promoted seating | `M_WIDEINTENT`: a successor that widens one field |
| | `AutonomousAddsNothing`: an autonomous plane's log holds no promotion, seating, issuance, bundle change or operator's grant, and no change of membership off its schedule | `M_LITEPROMOTES`: it orders one |
| `Outstanding` | `EffectsAfterRevocationBounded`: the first row of §4.3, with no premise about time | `M_NOCHARGE`: a lease is granted without charging its count. `M_ATMOST`: the bound is "at most `K_up`", which lets one more through |
| | `HavocPlaneBoundedInEffects`: with the plane signing anything, each honest governor permits fewer than `K_up` effects that no watermark covers | `M_TRUSTMARK`: a governor takes its plane's word for what has been read |
| | `SealedIsSpent`: a lease a watermark covers produces no further effect | `M_EARLYRELEASE`: a charge is released before the seal |
| `PlaneClock`, with explicit time | `NoGrantPastExpiry`: no grant under an intent more than one tick period past its `expiry`, under a named premise that captured and slow replicas are fewer than a certificate | `M_ONECLOCK`: one replica's clock decides. `M_RECEIPT`: an interval starts at receipt, which is the NATO reading's F1. `M_RELATIVETICK`: a tick is measured from the tick before, so a stall hides its length |
| | `EntryEndsAtExtent`: no entry runs past its extent while ticks reach the governor, and none past one overdue tick when they do not | `M_NOEXTENT`: an entry with none loads. `M_NOWATCHDOG`: an overdue tick ends nothing |
| `Alone` | `AlonePermitsNothing`: a governor whose vehicle is alone permits nothing but the beacon, within its count | `M_ALONEACTS`: it permits one `local` entry |
| | `ExpiryGrantsNothing`: after a lease ends the only effects are hold and the seating's terminal behaviour | `M_STACKCHOOSES`: the stack selects it |
| `Peer` | `PeerAddsNothing`: every request that is permitted or admitted is still permitted or admitted with every item received from peers removed | `M_PEERENABLES`: a report enables one entry |
| | `ReceivedIsUntrusted`: a delivered report's label holds `untrusted`, whatever its sender declared | `M_SENDERLABEL`: the sender's label is taken as given |
| | `SendWithinTopics`: every report sent is to a topic the mesh declares for the seat | `M_ANYTOPIC`: a report to an undeclared topic is sent |
| `Release` | `IrreversibleIsAPersons`: every irreversible effect has a person-signed predecessor ordered at a commanded plane, used once and no older than its declared ticks | `M_AGENTRELEASE`, `M_LITERELEASE`, `M_REPLAY`, and `M_LATEFIRST`: a first delivery after the ticks have run |
| | `ConflictIsAFinding`: a check failing at a seal or above subtracts, and voids nothing a governor permitted | `M_VOID`: it voids an effect that happened |

**One bound has a premise about time and the other has none, and they are kept apart.** The lattice analysis
proposes that no safety theorem have a timing premise among its ancestors, so that ADR-0032 §1 is computed and
not only stated (`derived/topak-safety-liveness-quorum-lattice-2026.11.05.md`). `Outstanding` meets that.
`PlaneClock` does not and cannot: it is a statement about duration, and its premise would be a named `ASSUME`. The
first revision's `NoEffectPastTtl` and `RevocationBounded` put a premise about drift under the safety bound
itself.

**Three liveness statements belong at Tier 0** of the liveness plan (`derived/topak-liveness-2026.10.07.md`), as
invariants over `ENABLED` in the shape of `Emergency_live.tla`:

- with a lease ended, the terminal behaviour is enabled whatever the stack does;
- while a release lease is live and the vehicle is linked, a release call can be admitted whatever any agent or
  Observer is doing;
- while a lease is live and its vehicle hears its plane, a `local` entry within its count can be permitted
  whatever the plane's primary, any other vehicle or any Observer is doing. That is ⟨21⟩ as a property.

**What the modules could not show.** The timing budget is only partly expressible in TLA+ (ToO §11.3). That a
vehicle reaches its safe state is physics. That the governor is the only path to the actuators and the radio is
a claim about hardware. That an entry's extent is what the entry declares is a claim about the vehicle. And a
proof of these modules would be of the modules: no refinement to running code exists anywhere in the corpus
(G11 §8).

---

## 11. The trusted base, and assumptions of use

**New rows for ADR-0045's table**, each classed by failure direction as that record requires:

| Row | Class | If it fails |
|---|---|---|
| The governor's admit path, which now makes every `local` permit | Trust root | Anything the stack requests may reach an actuator |
| The governor's clock | A residual, in the slow direction | It finds a tick overdue late. An entry in progress runs on, and only when the plane's ticks have also stopped reaching it (§4.4) |
| A plane's clocks, taken together | Trust root for the duration bound only | With captured and slow replicas at a certificate or more, an intent outlives its `expiry`. The bound in effects still holds |
| The governor's measure of an extent | Trust root for an entry whose extent is a distance or a region | An entry runs past what was voted |
| The intent boundary's reading | Trust root for the watermark | A watermark for a record nobody checked releases a charge nobody read |
| The governor's key store | Trust root | The vehicle's principal, and its replica, are whoever holds the key |
| The navigation source | Trust root for area checks | The envelope is somewhere else |
| The effector interlock | Trust root | An irreversible effect without a person's act |
| The recovery function | Trust root for the terminal behaviour | Expiry with no safe state |
| Cedar and the Wasm engine on the vehicle | Existing rows, instantiated on every vehicle | As those rows say |
| The link and the radios | Delegated | Loss only subtracts: a plane cut off above stops granting before `K_up`, and a vehicle cut off from its plane loses its lease. The NATO reading's F2 found this inexact of the first revision, where a vehicle alone kept entries and lost checks |
| Byzantine agreement at an exposed plane, with its reconfiguration step (§3.5, §3.6) | Trust root, in place of the replica row there | A forged certificate, or two successors to one membership |

**New assumptions of use.** A deployment that does not meet them does not inherit anything §10 would prove.

| Assumption | If it does not hold |
|---|---|
| The governor is separate from the stack and is the only path to the actuators and the radio | The stack is `Mediated`, and every property here is void. This is A1 for a vehicle |
| Captured and slow replicas together are fewer than a certificate, and each sound clock's margin covers its drift | `NoGrantPastExpiry` is void. `EffectsAfterRevocationBounded` is not |
| Effect classes are declared as what they are | An irreversible effect is reachable by an agent, or by a governor alone |
| Each vehicle class has a declared safe state, and its recovery function reaches it in bounded time | The terminal behaviour is a stall, which for a body in motion is not safe |
| A trained, authorized person is at each release seat and can see what the act requires | HITL is a key and not a judgment |
| No more replicas of an exposed plane are captured than its current membership tolerates, at every step of its schedule | That plane is captured. It is bounded by its charter or intent, and by each honest governor's account against `K_up` |
| What a vehicle does to the world other than through its entries is declared as outside the alphabet | Effect exclusivity is claimed for a body, and is false |
| Every entry's extent is declared as what it is | A count bounds how many acts and not what they do |
| Envelopes, counts and budgets are voted against what every stack could do together | The joint effect of permitted acts is one no tally weighed |
| `T_tick` is long against a round of the plane over its radios | Ticks fall behind and leases end, with no adversary present |

---

## 12. What this gives up

1. **No delegation.** Planes grant below themselves. It attenuates, it is a mechanism's and it is budgeted, and
   it is still delegation.
2. **A bound in seconds as a theorem.** Revocation is bounded in effects, with no premise about time ⟨12⟩. The
   bound in duration is declared, and rests on enough of a plane's clocks being sound ⟨13⟩. The first revision
   gave up ADR-0032's first clause here. This one keeps it, with a residual of one entry in progress.
3. **An ordered admit before every effect, for every pre-authorized entry and every report to a peer** ⟨22⟩ ⟨16⟩.
   The ordered predecessors are the intent and the lease. Nothing a governor permitted can be voided, and no
   Observer is checked in the middle of a lease.
4. **A person in reach.** Meshed, findings still subtract and nobody can respond.
5. **Any act by a vehicle that is alone** ⟨14⟩. An adversary that cuts one vehicle from its plane gets its
   terminal behaviour within a tick period.
6. **Inexpressibility of irreversible effects.** They are expressible by a person. ADR-0032 §4 is relaxed.
7. **A small trusted base.** Every vehicle carries one, and it now makes every `local` permit. Every exposed plane
   needs Byzantine agreement, with a reconfiguration step that PBFT as published does not have.
8. **A fixed capture threshold** ⟨19⟩. A schedule spends it to survive losses, silence triggers each step, and "a
   timeout is never a grant" is strained (§3.6).
9. **One bus.** Stacks report to each other off the workflow's edges, where no guard reads and a finding has
   further to travel ⟨15⟩.
10. **"Not autonomous."** The corpus dropped the word because no principal seats, delegates to or addresses
    another. That stays true of every principal. It is no longer true that a person is always on the plane that
    orders an effect.

**What the third prompt bought back.** The first draft gave up tempo, and left coordination among cut-off vehicles
out. An intent is one commander's act inside a quorum's vote (§3.2), and meshed vehicles coordinate through their
own plane (§8).

**What the discussion bought back.**

- **ADR-0032's first clause**, in exchange for a bound stated in effects (§4.3).
- **Tempo below the intent boundary.** A pre-authorized act waits for no round (§3.7).
- **A path for what vehicles tell each other**, at whatever rate the radios carry, which the swarm reading's Z1
  found missing (§8.1).
- **A plane that outlives its first losses** (§3.6).

---

## 13. Questions for the custodian

| # | Question | Recommended |
|---|---|---|
| 1 | Is §2.3's rule right: a promotion for a new issuer or artifact, an ordered admit otherwise? ⟨8⟩ | Yes |
| 2 | Is "lite" defined by having no path that changes authority, and declared as a degenerate plane with its additions reported upstream (§3.3, §3.4)? ⟨11⟩ | Yes |
| 3 | Do an autonomous plane's replicas run on the vehicles themselves? | Yes. Relay nodes are allowed and declared. The fourth prompt, on governors keeping quorum, reads as taking this |
| 4 | Is an intent bounded by the last intent, as ADR-0050 bounds a successor grant, or by the promoted seating (§3.2)? | The seating. Otherwise a commander who narrows cannot restore, and will not narrow |
| 5 | Is the person the actor, or do they countersign an agent's proposal (§6)? | The actor |
| 6 | Is `release` a new seat kind, or the `emergency` kind reused? | A new kind with the same activation. An emergency envelope is the domain's whole allowlist. A release envelope is the opposite: irreversible entries only |
| 7 | Is Byzantine agreement required at a plane whose replicas can be captured (§2.5)? | Yes, declared per plane, and always at an autonomous one. It reverses ADR-0045 for those planes only. ⟨20⟩ reads as taking this for an autonomous plane |
| 8 | One floor for the federation, or one per plane? | One |
| 9 | Is a cell's Observer seated on another vehicle (§5.6)? The first revision also asked whether a vehicle alone is exempt from coupling, which ⟨14⟩ removes: it permits no actuation | Yes |
| 10 | May a person hold an orchestrator seat at a commanded plane (§8)? | Yes |
| 11 | Is this a change to the archetype, or one deployment's overlay under ADR-0058 (Proposed)? | An overlay first, reported upstream under its §6. Every item in §12 is a cost to a deployment that never loses its link |
| 12 | Is a watermark the mechanism's act, ordered when the record is archived and checked, or a person's (§4.3)? | The mechanism's. A person's would put a commander's attention on the path of every lease |
| 13 | What does the first intent's `expiry` count from, before the plane has ticked (§4.4)? | The charter's application, which is tick zero |
| 14 | Does the governor hold, by a behaviour fixed at seating, when an entry's extent ends and none follows (§5.3)? | Yes |
| 15 | May a vehicle that was alone be leased again under the same intent when it hears its plane (§5.5)? | Yes, charged to the budget |
| 16 | Is a release act's freshness a number of ticks of the vehicle's plane (§6)? | Yes |
| 17 | Does a smaller membership carry a smaller budget, so that a step of the schedule also narrows (§3.6)? | Yes, where the tally can state one |
| 18 | Is the capture floor one at the archetype, given that silencing vehicles reaches it (§3.6)? | One, and declared. A deployment facing that adversary seats a larger plane with a floor of two |
| 19 | What label does a peer's report carry: `untrusted` alone, or also a name a bundle can key on (§8.1)? | Both: `untrusted` always, and a name the mesh declares per topic |
| 20 | Which entries does the archetype mark `ordered` (§8.2)? | None by default. The tally marks them per mission |

**Settled since the first draft:** the reading of "mesh fence" ⟨9⟩, and where an effect is admitted ⟨10⟩.

**Settled in the discussion:** ⟨12⟩ to ⟨22⟩, as the head of this document lists them. Questions 12 to 20 are what
those leave open.

---

## 14. The records this would become

Unnumbered, since nothing is decided. In dependency order:

1. **Planes and charters** (§2). Confirmation-required at least under C1, since every grant below the root
   travels the path it opens, and C3, since it reverses ADR-0045 on Byzantine agreement. It also contradicts
   ADR-0054's sentence on delegation, and that record is Proposed. Amends ADR-0024, ADR-0031 and ADR-0045.
2. **The intent and the autonomous plane** (§3). Rests on ADR-0050 and ADR-0055, so it is provisional while the
   first is and cannot be ratified before the second. Under C1 and C2.
3. **The lease as pre-authorization, and the bounds below the intent boundary** (§3.7, §4, §5). Amends ADR-0015's
   sentence on predecessors, ADR-0033 §4's void, ADR-0039 and ADR-0041 (coupling at the grant, and pointed
   upward), and ADR-0032 by a residual and not in its first clause. Under C2 and C3.
4. **Effect classes and the release seat** (§6). Amends ADR-0032 §4, ADR-0037's seat kinds and ADR-0049's entry
   schema, beside ADR-0052. Provisional while ADR-0052 is.
5. **The `federation` floor stage** (§7.2), gated as each stage is, and in force only with a ratified floor.
6. **The threat model** (§9), as an annex to ADR-0045 or a record of its own.
7. **Peer topics** (§8.1). Amends ADR-0055 §7, ADR-0015 (an emission permitted and not ordered), ADR-0043 (a
   sixth item of ingress) and ADR-0047 (its label). It cannot be ratified before ADR-0055.
8. **The size, the instrument and the shrink schedule** (§3.5, §3.6). Amends ADR-0045 and strains a constant of
   ADR-0024. Under C3.

**What this does not claim.** It does not make an act lawful or right. It does not judge identification, intent or
proportion. It does not show that any vehicle is confined: no real principal is `Contained` at the reference
today, for software agents either (G11 §8). `K_up`, a lease's count, `T_tick`, `T_intent`, a plane's size and the Observer's latency are placeholders.
Like most of this corpus, it has been read by nobody independent of its author.

---

## 15. Changes from the first draft

The first draft is commit `7155ad9`. It had two states, connected and disconnected, and one bound, `T_disc`.

- **§2.3 is new** ⟨8⟩: the four kinds of narrowing and which are promotions.
- **§2.6 replaces "Ending a plane"** ⟨9⟩. A lease carries every plane's fence, and the first draft's question on
  the reading of "mesh fence" is closed.
- **§3 is new** ⟨10⟩ ⟨11⟩: the intent boundary, the intent, the autonomous plane and what "lite" means.
- **§4 has three states where the first draft had two**, and `T_disc` splits into `T_intent` and `T_alone`.
- **The governor admits by itself only when the vehicle is alone.** Meshed, the autonomous plane orders admits
  before their effects, void works, coupling applies and vehicles coordinate through the plane's log.
- **The release seat is at a commanded plane and never below.**
- **The floor stage gains `FD4-autonomous-adds-nothing`**, and its irreversible and disconnected entries are
  restated for the three states.
- **The threat model gains the partitioned mesh**, and restates jamming and capture for an autonomous plane.
- **§12 no longer lists tempo as a cost**, and names the word "autonomous" as one.
- **§13's questions change**: one is settled, four are new (1 to 4), and the first draft's question on
  coordination among disconnected vehicles is answered by §8.

---

## 16. Changes from the first revision

The first revision is commit `845f95c`. In it the autonomous plane ordered every act while a vehicle was meshed, a
governor admitted by itself when alone, and two clock bounds, `T_intent` and `T_alone`, were the safety
parameters.

- **§3.5 to §3.7 are new** ⟨19⟩ ⟨20⟩ ⟨21⟩ ⟨22⟩: the size and instrument of an autonomous plane, the shrink
  schedule, and what waits for a round.
- **§3.1 changes** ⟨22⟩. The plane grants leases, and the governor permits each pre-authorized entry.
- **§4 is rewritten** ⟨12⟩ ⟨13⟩. The safety bound is a count, `K_up`, with the intent boundary as the plane's
  Observer. The duration bound runs on ticks the plane's replicas order. `T_alone` is gone and `T_tick` is new.
- **§5 changes throughout.** Three kinds of entry replace three alphabets. A vehicle alone keeps its terminal
  behaviour, listening and a beacon ⟨14⟩. Every entry declares an extent ⟨18⟩. The radio is on the governor's
  side. Coupling for a `local` entry moves to the grant.
- **§8.1 and §8.2 are new** ⟨15⟩ ⟨16⟩ ⟨17⟩ ⟨21⟩: peer topics, and agreement as an ordered entry.
- **§2.1 gains fields, §2.3 a row and §2.6 the pulled fence.** §6 says what "fresh" means. §7.2's stage goes from
  nine forbids to fourteen, with three reworded.
- **The threat model gains three rows**, attrition, a stack that lies to its peers and clock faults, and restates
  four.
- **§10 is regrouped.** `Outstanding`, `PlaneClock`, `Alone`, `Peer` and `Release` replace `Disconnected`.
- **§12 no longer lists safety without clocks as given up**, and lists four new costs.
- **§13 gains nine questions**, 12 to 20.

**Findings of the two readings that this answers**, each by a design and none by a check:

| Finding | Answered by |
|---|---|
| F1, no interval has a stated origin | §4.4 for an intent and a lease, and §6 for a release act |
| F2, a stack may choose to be alone | §5.1, the radio is the governor's, and §5.2, a vehicle alone permits no actuation |
| N3, attrition under a fixed membership | §3.6. Where the orchestrator runs is not answered |
| Z1, one path for information between vehicles and no rate for it | §8.1; §5.6 for an Observer's payloads; §5.3's extent for the grain of an entry |
| Z4, the motive a vanished Observer gives a stack | §5.2 removes the motive. An Observer that accuses or vanishes is not answered |

**Not taken in:** F3 (a captured vehicle discloses the rules), F4 (the envelope has no field), N1 (sibling
planes cannot deconflict), N2 (a second anchor), Z2 (how a plane comes to know of a capture), Z3 (the
false-finding rate of an unattended plane), and the rest of Z4.

**Not independent, as before.** The discussion was between the custodian and the drafter. §4.3's argument and
§4.4's are prose, and the second changed once while it was being written down.
