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

(The custodian's three prompts of 2026.11.10, with spelling and punctuation normalized. CP is a control plane.)

**Date:** 2026.11.10 · **Against:** the tree at `a157659`, Genesis Checkpoint G11 and Theory of Operation revision 15
(cited below as ToO) · **Status:** design proposal. **Nothing here is a decision, and nothing here is modelled,
checked, built or reviewed.** · **Drafted by the assistant** at the custodian's request, from a discussion of
2026.11.09 and 2026.11.10. **Revised once, on the day it was written and before anything cited it**, to take in the
third prompt; §15 lists what changed.

**What the custodian settled.** The seven items of the second prompt are marked ⟨1⟩ to ⟨7⟩ where each is used, and
the four of the third ⟨8⟩ to ⟨11⟩. ⟨9⟩ and ⟨10⟩ are statements and are taken as settled. ⟨8⟩ and ⟨11⟩ were asked as
questions: §2.3 and §3.3 answer them, and the answers are the drafter's until the custodian takes them. Every
other choice is the drafter's, marked *(drafter's choice)* where the alternative was live. §13 lists eleven
questions, each with a recommended answer.

**It rests on text that is not settled.** ADR-0054 and ADR-0055 (workflows) are Proposed. ADR-0050 (the operator)
and ADR-0052 (the emergency seating) are provisional, and §3.2 leans on ADR-0050 hard. No floor is ratified. Under
A17 nothing should be built on this that could not be rebuilt. ADR-0056 to ADR-0058 were read by title only, except
ADR-0058 §1, §5 and §6.

**Scope.** This is about authority: who may cause which effect, for how long, under whose rules, and what record it
leaves. It is not a design of a vehicle, a sensor or an effector, and it says nothing about how a person decides
that an irreversible act is right.

**The proposal in brief.** A deployment becomes a tree of control planes. Each plane is seated by a promotion at
the plane above it and can hand down only what it was handed, or less. The last plane where a person commands is
the **intent boundary**. Below it sits one **autonomous plane** per group of vehicles, with no person on it and no
way to add authority: the custodian's "TOPAK lite". Every effect is admitted at the intent boundary. A reversible
effect is admitted there as an **intent**, a task with an envelope, a budget and an expiry, and the autonomous
plane orders each act inside it. An irreversible effect is admitted there one at a time, by a person. Each vehicle
carries a small trusted component, the **governor**, between its autonomy software and its actuators. A vehicle
that loses even its own plane falls back on the governor and the lease's TTL, and then does one thing fixed in
advance.

**What it changes in the corpus**, each named where it is used and again in §12:

- **Reversed:** no principal grants another (ToO §2.11). Planes grant below themselves.
- **Reversed below the intent boundary:** clocks buy liveness, never safety (ADR-0032; ToO §10).
- **Given up for a vehicle that is alone:** an ordered admit before every effect (ADR-0015; ToO §4.1). It is kept
  wherever a plane is in reach.
- **Relaxed:** an effect with no timing budget must not be reachable from the alphabet at all (ADR-0032 §4). It
  becomes reachable by a person and by nobody else.
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
| **Governor** | The trusted component on a vehicle. It verifies the chain, holds the lease, evaluates the floor and the bundles, measures time and position itself, and is the only path to the actuators. It is mechanism, not a principal |
| **Stack** | The autonomy software on a vehicle: planning, perception, any model. It is the Thinker, and it is Byzantine |
| **Linked, meshed, alone** | What a vehicle can reach: the intent boundary through its plane; a quorum of its plane and nothing above; no quorum of any plane (§4.1) |
| **Terminal behaviour** | What the governor does when a lease ends with no successor. It is fixed at seating (§5.5) |
| **Effect class** | `reversible` or `irreversible`, declared per allowlist entry with its `T_irrev` (§5.3) |
| **Release seat** | A seat held by a person, the only kind whose alphabet reaches an irreversible entry (§6) |

"Gate" is not used for the vehicle's component because the corpus already uses it three ways.

**The tiers**, with the custodian's mapping:

| Tier | The custodian's words | In this proposal |
|---|---|---|
| Root plane | "TOPAK as the top tier" | Holds the anchor's rules, the floor and the rosters. Seats the planes below it |
| Commanded planes | "DAG workflows are cells of command chains" | Each promotes missions and charters for the planes below (§7.1, §8) |
| Intent boundary | "Mesh workflows are lowest level of field command autonomy", at brigade level; "last commander's intent boundary" | The last commanded plane. It promotes the mesh, its commander issues intents, and release seats are here or above |
| Autonomous plane | "Last autonomous CP"; "TOPAK lite"; company, troop or battery level | Runs the mesh under an intent and orders the vehicles' admits. No person, no promotion |
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
| `ttlMax` | The longest lease `ttl` the plane may grant, per effect class (§4.3) |
| `budget` | The most leases the plane and every plane below it may ever issue |
| `expiry` | The charter's own life, on the clock of whoever checks it. Never later than the parent's |
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
| **A value already in force, moved down** | A shorter `ttl`, a smaller area or budget, an entry removed, a round ended, a revocation, a fence, `deny=all` | An ordered admit. "Runtime subtraction is not promotion", needs no quorum and is attributed (ToO §7.1) | One operator, or the mechanism |

**The rule:** a narrowing is a promotion when it brings a new issuer or a new artifact into force. Otherwise it is
an admit ordered by the plane's consensus and signed by one person or by the mechanism. "Quorum" in the second
case means the replicas' agreement on the order, and no vote.

**At an autonomous plane only the last row exists**, since it has no people and no promotion path (§3.3).

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
is always such a plane.**

### 2.6 The mesh fence is the planes ⟨9⟩

Read as: what fences the mesh is every plane above it. A charter and a lease carry the epoch and log index of each
plane on the chain, not only of the plane that granted them. An admit, at a plane or a governor, compares each
against the latest the verifier has heard. **Any plane on the chain that moves its epoch fences everything below
it.** That act is a **plane fence**. It is a subtraction, so it needs no quorum and is ordered (ToO §4.1).

A fence travels only as far as the link does. Below a broken link, and below a captured plane that does not pass
it on, what ends authority is an `expiry` or a `ttl` read on a local clock. That is §4.

---

## 3. The intent boundary and the autonomous plane ⟨10⟩ ⟨11⟩

### 3.1 Every effect is admitted at the intent boundary ⟨10⟩

Read as: the authorizing admit of every effect is ordered at the last plane where a person commands.

| Effect | What is admitted at the intent boundary | By whom | What the autonomous plane then does |
|---|---|---|---|
| Reversible | An **intent**: a task, an envelope, a budget of activations and an expiry | The commander, an operator. The first intent is the promotion's own (§3.2) | Orders each admit inside the intent, before its effect |
| Irreversible | The effect itself, one at a time | A person at a release seat (§6) | Relays it. It can refuse one and cannot originate one |

**This restores ADR-0015's sentence.** "Every effect therefore has a consensus-ordered, signed, authorizing
predecessor" (ToO §4.1), and the predecessor is ordered at a commanded plane. While a quorum of the autonomous
plane is in reach, the act's own admit is ordered before its effect as well.

**What is admitted for a reversible effect is an envelope, not the act.** Nobody at the intent boundary sees the
individual act before it happens. The commander voted for, or signed, everything the envelope allows.

### 3.2 An intent

**An intent is a charter for one round of an autonomous plane.** It names the round's task, an envelope, an
activation budget and an `expiry`, and every field is the promoted seating's or narrower.

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
  plane above is fenced. Expiry is local and then ordered, as a lease's is (ADR-0031 E1): the first replica to see
  it proposes the round's end.

### 3.3 What "lite" means ⟨11⟩

The custodian asked whether the last autonomous plane is a TOPAK lite. **Yes, and it should be defined by one
absence: it has no path that changes authority.** ADR-0015 enumerates authority changes as exactly promotion and
anchor issuance. An autonomous plane has neither.

| Absent | Present |
|---|---|
| Build: no authoring and no promotion | The admit path: decided, ordered, checked again at apply, void if it fails (ADR-0033 §4) |
| Grant seats, operators, release seats: no person | The lease, the floor, every bundle on the chain, the fences |
| Anchor issuance, new bundles, seating of planes | The workflow interpreter: a mesh, its activations and its budget |
| Any grant but one | **One grant:** a node's lease, made by the mechanism under a live intent, "with every field the seating's or narrower" (ToO §2.11) |
| | Subtraction: the end of a round, a revocation, an Observer's finding, expiry |

By role:

| Role | At a commanded plane | At the autonomous plane |
|---|---|---|
| **T** | The modules and their proofs | The same modules. Nothing of T runs on a vehicle |
| **O** | The Cedar floor; the bundle through a sidecar, with Wasm as the fallback | The same floor, linked in. Bundles in Wasm only (§7.1) |
| **P** | Consensus, Byzantine where replicas are exposed | Byzantine agreement among replicas on the vehicles, with membership fixed by the charter *(drafter's assumption; question 3)* |
| **A** | Agents and people | Stacks only |
| **K** | Kafka as transport, with the archive as system of record (ToO §4.2) | No Kafka. The plane's log is carried and handed up on contact. The archive stays above |

### 3.4 It is a declared degeneracy and an addition, not a second pattern

The corpus refuses ladders: "degeneracy, not a ladder", and "theorems are present or absent" (ADR-0023; ToO §8.1).
"Lite" is therefore a nickname. In the corpus's terms the autonomous plane is two things:

- **A degenerate plane.** It omits Build, the people and K. A deployment declares that as an overlay under
  ADR-0058 (Proposed), and `spec/inventory.py` computes which theorems the declaration keeps.
- **An addition.** Charters, commit certificates and operation with no person present are capabilities the
  archetype lacks. ADR-0023's admission test says what that means: the archetype is incomplete, and the report is
  a finding about it.

---

## 4. Three states of a vehicle, and the TTL as a safety parameter ⟨2⟩

### 4.1 Linked, meshed, alone

| State | The vehicle can reach | Who admits | Ordered before the effect | What ends authority |
|---|---|---|---|---|
| **Linked** | Its plane, and through it the intent boundary | The autonomous plane; a person, for an irreversible effect | Yes | Anything a plane above orders: a fence, a revocation, a narrower intent |
| **Meshed** | A quorum of its plane, and nothing above | The autonomous plane | Yes | The plane's own subtractions and findings; the intent's `expiry` and budget |
| **Alone** | No quorum of any plane | The governor | No | The lease's `ttl` and action count |

### 4.2 What changes for the clock rule

"Clocks buy liveness, never safety. Epoch fencing carries safety without reading a clock, so an expired lease its
holder still believes in is not a containment violation" (ToO §10). That holds because the admit path is outside
the holder and compares the epoch on every action.

- **Linked**, it still holds.
- **Meshed**, no fence from above arrives. The intent's `expiry`, read on the replicas' clocks, is what ends the
  plane's authority.
- **Alone**, the admit path is the governor and it travels with the holder. The lease's `ttl`, read on the
  governor's clock, is the only thing that ends authority.

### 4.3 Two declared bounds

`T_intent` is the longest an intent may live. `T_alone` is the longest lease `ttl`, per effect class. A lease's
life is nested inside its intent's, and an intent's inside every charter above it.

| Property | Statement |
|---|---|
| **Revocation is bounded** | Authority revoked or fenced at a commanded plane at time *t* produces no effect after *t* + `T_intent`. A vehicle revoked by its own plane produces none after *t* + `T_alone` |
| **Stale rules are bounded** | A narrower intent or a tightened bundle cannot reach a meshed plane before it is linked again, so superseded rules stay in effect there until its intent expires, at most `T_intent` |
| **Exposure is bounded** | An intent never puts out more leases than its budget, each of at most `T_alone` |

**The two bounds pull apart, which is the gain over the first draft.** `T_alone` can be short, because a meshed
plane goes on granting node leases while the link above is jammed. `T_intent` is the long one, and it is the
commander's to set per intent.

### 4.4 The clock

A governor reads its own monotonic clock and stops admitting at `ttl` less a margin, which errs early as ADR-0031
E1 requires. If the clock runs slow by at most a fraction ρ and the margin is at least ρ × `ttl`, real elapsed
time never exceeds `ttl`. The same holds of each replica and an intent's `expiry`. Three rules keep that honest:

- **No external time is read.** A time signal from outside is content, as a timestamp in a payload is (ADR-0032
  §3).
- **A governor cannot renew its own lease, and a plane cannot extend its own intent.**
- **The clock is a trust root in the slow direction.** A slow clock preserves authority, which is ADR-0032's test
  for an interval that needs trusted time. Here the trust is in a component outside the principal, the stack, and
  inside the vehicle.

### 4.5 The trade is declared, not designed away

A short `T_intent` sends a meshed plane to its terminal behaviour while the link above is jammed. A long one is
how long a revoked or captured plane keeps acting. Both bounds are declared in the floor's values, as `T_irrev`
is. Like every number in the corpus they are placeholders until something is measured.

### 4.6 Postures

The glossary defines the postures by enabling condition, and says Run's window leaves HOTL.

| Effect | State | Posture | Enabled by |
|---|---|---|---|
| Irreversible | Linked only | HITL | A person's signed act, one per effect, ordered at the intent boundary (§6) |
| Reversible | Linked | HOTL, as Run today | The plane's admit under an intent. A person can stop it |
| Reversible | Meshed | Unattended. Observers still read and their findings still subtract | The plane's admit under an intent |
| Reversible | Alone | Unattended, and nothing reads | The governor's admit under a live lease |

**The last two rows are new.** A5 says unattended operation is something "the pattern does not model". Meshed,
ADR-0032 §4's budget has no `D`, since no person can respond. Alone, it has no `L` either. **Nothing in the
disconnected alphabet may rest on detection.** What an entry can do at worst, inside its envelope, is what the
tally voted to accept, and nothing checks that the vote was right. It is the floor-fitness problem again (ToO §12
item 2).

---

## 5. The vehicle: a governor, a stack and three alphabets ⟨6⟩

### 5.1 What is Byzantine and what is trusted

The custodian's "fully Byzantine" holds of the stack. It cannot hold of the whole vehicle: something on board must
check a chain and gate the actuators, and that part is trusted. The governor:

- verifies the chain and holds the lease and the vehicle's key;
- hosts the vehicle's replica of the autonomous plane *(drafter's assumption; question 3)*;
- evaluates the floor in Cedar and each bundle on the chain as a Wasm module (§7.1);
- **lifts its own facts**: elapsed time, position, the lease's action count. No safety decision reads a clock a
  principal supplies (ADR-0032 §3), and by the same rule none reads a position the stack supplies;
- hosts each tool as a Wasm component with one capability, its declared channel, which for a vehicle is an
  actuator interface. This is channel fidelity as ADR-0034 A2 has it for Run, and the reference's `wasmtool` is
  its start (`mechanism/README.md`);
- records every admit and denial it makes alone (§5.4), and carries out the terminal behaviour (§5.5).

Models stay out of the trusted base. The trusted base still grows, on every vehicle (§11).

### 5.2 Three alphabets

| Alphabet | Admitted by | Ordered | Holds |
|---|---|---|---|
| **Plane** | The autonomous plane, linked or meshed | Before the effect | Every entry in the lease's alphabet, inside the intent |
| **Disconnected** | The governor, when the vehicle is alone | After, at reconciliation | Entries the bundle marks `disconnected`, inside the envelope, the `ttl` and the action count |
| **Terminal** | Nobody. It is fixed at seating | The expiry is ordered when a plane learns of it | One behaviour per vehicle class: hold, return on a voted route, land or stop |

No agent seat's alphabet holds an irreversible entry, in any state (§6).

### 5.3 Where "disconnected" is declared

The allowlist entry has five parts (ADR-0049). It gains a sixth, `effect`: the class, its `T_irrev`, and whether
the entry may be admitted by a governor alone. It is promoted with the bundle and voted like any entry. **An
effect class is a declaration**, as a label is (A15): an irreversible effect declared reversible is seen by
nothing here.

### 5.4 The record, and two reconciliations

- **Alone to meshed.** The governor writes each admit and denial it makes alone to a chain on the vehicle:
  hash-linked, signed with the vehicle's key, and numbered by the per-lease sequence the lease already carries
  (ToO §4.2). On rejoining, the plane orders the chain as one entry and runs the mechanism checks at that position.
- **Meshed to linked.** The autonomous plane's log is the record while it is meshed. On contact the intent
  boundary orders the segment as one entry, checks it against what it ordered meanwhile, and archives it.
- **Inside a plane, void works as written.** An admit that fails at apply is "ordered, recorded, without effect"
  (ADR-0033 §4).
- **Across a reconciliation, nothing is void.** The effect has happened. A check that fails there is a **finding**
  against the lease or the intent, and it can only subtract.
- **A captured vehicle's chain, or a captured plane's log, is not evidence.** It says what its captor signed.

### 5.5 Terminal behaviour, and why expiry grants nothing

"A timeout is never a grant" is a mechanism constant (ADR-0024), and a lapsed orchestrator "takes no default edge,
because an edge taken on a timeout would be a grant made by a timeout" (ToO §2.11). A body in motion still has to
do something when its lease ends. The proposal keeps the rule this way:

- The terminal behaviour is part of the seating, voted with it. Its envelope is the lease's, or a route the tally
  voted.
- The stack does not choose it and does not carry it out. A recovery function in the governor's trust domain does.
- Where a class has more than one terminal behaviour, a fixed rule over facts the governor measures selects one.

Expiry ends the stack's authority and selects nothing the promotion did not already fix.

**The corpus's answer to failure is to stall, and "a stall that never ends is safe"** (ToO §12 item 21). That is
false of a vehicle in flight. Each vehicle class therefore declares a safe state, and reaching it in bounded time
is an obligation on whoever builds the vehicle. No module here can prove it. It is an assumption of use with an
owner (§11).

### 5.6 Coupling

`R3-observer-live` refuses `Actuate` under a `thinker` seat with no live cell Observer (ADR-0041).

- **Linked or meshed, it applies.** A cell's Observer is seated on another vehicle of the same plane *(drafter's
  choice; question 9)*, so it does not share hardware with the Thinker it watches.
- **Alone, the disconnected alphabet is exempt**, for the reason §4.6 gives: nothing in it rests on detection. An
  Observer on the same vehicle is allowed and declared. It shares the vehicle's hardware and fate with its
  Thinker, so no claim rests on it.

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
  unused, and that the entry is in the seat's envelope. **The vehicle must be linked.**

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
| `FD4-autonomous-adds-nothing` | forbid | At an autonomous plane: no promotion, no seating, no operator's request, no bundle change, and no grant but a node's lease under a live intent |
| `FD5-irreversible-release-only` | forbid | No `Actuate` of an irreversible entry under a seat whose kind is not `release` |
| `FD6-irreversible-from-commanded` | forbid | No admit of an irreversible entry without a commanded plane's commit certificate for that act |
| `FD7-disconnected-marked` | forbid | No admit by a governor alone of an entry its bundle revision does not mark `disconnected` |
| `FD8-disconnected-bounds` | forbid | No admit by a governor alone at or past `ttl` less the margin, or with the lease's action count spent |
| `FD9-release-seating` | forbid | No `release` seating of a key that is not on the anchor-issued roster, none at an autonomous plane, and none at a plane whose charter lacks `release` |

**Every new entry subtracts. Two existing entries are relaxed**, and each relaxation routes as one (ToO §3.2):
`B10-only-thinkers-author` gains an exception for a `release` seat's `Actuate`, as it has for an `emergency` seat,
and `R3-observer-live` is scoped to admits a plane makes (§5.6).

**The schema gains** the kind `release`; the entity `Plane` with its charter and kind; `effect` on an entry; and,
in the Run context, who is admitting, whether the `ttl` bound is passed and whether the count is spent. The lift
supplies these and the floor trusts its inputs, as the README already says of every stage.

### 7.3 What no policy here expresses

Identification, intent, necessity and proportion are judgments about the world. A classifier's output enters the
system only as a finding, and a finding may subtract authority and never add it (ADR-0007; ToO §2.2). So these
parts of a mission's rules are enforced by nothing in this design. For an irreversible effect they are the
judgment of the person at the release seat. For everything else they are, at most, something an Observer may
object to after the fact.

---

## 8. Missions as workflows

- **A DAG is a plan with branches**, promoted at a commanded plane. At a decision point an orchestrator chooses
  among edges the mechanism has already enabled, so it "decides how good the work is and never whether it is safe"
  (ToO §2.11). A person may hold an orchestrator seat at a commanded plane *(drafter's suggestion; question 10)*.
- **A mesh is promoted at the intent boundary and runs at the autonomous plane.** A node is one round of one
  cell, and a cell is a vehicle's stack with its Observer. Loops are allowed, the number of turns is decided at
  run time, and the activation budget is the intent's. That is the "field command autonomy" of the custodian's
  mapping: choice among enabled edges, bounded in count, with no person present.
- **Vehicles coordinate through their plane, and only that way.** In a mesh "the mechanism is the bus", and cells
  reacting to each other with nobody deciding what runs next "is not supported" (ADR-0055). Meshed, the bus is in
  the field with them. Vehicles still do not address each other. **Alone, a vehicle coordinates with nobody**: the
  disconnected alphabet holds no action on another vehicle.

---

## 9. Threat model ⟨3⟩

The corpus's adversary is the agent. A deployment of this kind adds an adversary that attacks links, hardware and
planes. Each row says what bounds the adversary and what is left.

| # | Adversary | What it can do | What bounds it | What is left |
|---|---|---|---|---|
| TM1 | **The stack**, Byzantine as ADR-0007 has it | Request anything, at any time | The governor, the alphabet, the envelope | Anything inside the envelope was voted acceptable. What the vehicle's body does that no entry names is outside the alphabet |
| TM2 | **The link adversary**: jams, drops, delays, replays, injects | Cut the link above a plane, making it meshed; cut vehicles from their plane, making them alone; delay a revocation; block every irreversible effect | Certificates stop forgery. Fences and sequence numbers stop replay. `T_intent` and `T_alone` bound the delay | Denial is always available to it, and the response is predictable: meshed, the plane works its intent to its expiry; alone, a vehicle has `T_alone` and then its terminal behaviour |
| TM3 | **A captured vehicle** | Extract the key and the lease; act as that principal and as one replica; sign any local record | The lease's envelope and its remaining `ttl`. Revocation, once its plane knows. One replica is within what Byzantine agreement tolerates | The interlock is moot when the effector itself is captured. Resistance to tampering is the builder's, and is a trust-root residual |
| TM4 | **Compromised replicas, fewer than a third** of a plane | Lie to the others | Byzantine agreement and commit certificates (§2.5) | Under crash-recovery consensus one such replica can propose an admit no floor evaluated (A9). That is why §2.5 asks for more |
| TM5 | **A captured plane**: a quorum of its replicas, which for an autonomous plane means that share of its vehicles | Issue any lease within its charter, to anyone; ignore fences; falsify its log | The charter or the intent, checked by every governor, and its `expiry`. An autonomous plane adds nothing: it cannot seat, promote or release | Everything within the intent until it expires |
| TM6 | **A partitioned mesh** | Leave two groups of vehicles each believing it is the plane | Agreement needs 2f + 1 replicas, so at most one side admits. The other side's vehicles are alone | A mesh split into pieces all too small admits nothing, and every vehicle is alone |
| TM7 | **An insider with a key**: an operator or a release person | Whatever that seat may do | Attribution. An operator's add needs a live peer (ADR-0050) | The mechanism cannot tell a person from a program holding the key. A wrong act by a release person is recorded and not prevented |
| TM8 | **Navigation deception** | Move the envelope in the world by falsifying a governor's position | Nothing in this design | The navigation source is a trust root with this residual. Time is not exposed the same way, since no external time is read |
| TM9 | **Deception of perception**, the stack's or a person's | Make the stack or the person wrong about the world | For the stack, the premise already assumes it. Perception never adds authority | A deceived person at a release seat is a semantic failure. Nothing here sees it |
| TM10 | **Supply chain**: weights, tools, bundles | Ship a bad artifact | Promotion by digest. Lineage independence, which is Proposed (ADR-0035) | As the corpus states it today |
| TM11 | **A colluding Observer** | Stay silent | Nothing. Coupling cannot see collusion (A13). Seating it on another vehicle removes shared hardware, not shared lineage | As the corpus states it today |

**Out of scope**: physical destruction of vehicles or planes; attacks on sensors other than as TM8 and TM9; what
an adversary learns by watching which planes and vehicles talk; and the security of the anchor's custody, which
ADR-0025 declares per deployment.

---

## 10. What would be checked

By ADR-0046's method each property ships with a mutation that breaks it and nothing else, and a witness that the
behaviour it constrains is reachable. **None of this is written.** The modules would be drafted by
`skills/writing-tla-specs-and-proofs/`.

| Module | Property | A mutation that must break it |
|---|---|---|
| `Federation` | `CharterNarrows`: every seated plane's charter is its parent's or narrower, field by field | `M_WIDEN`: a seating that widens one field |
| | `LeaseWithinChain`: every lease a governor accepts is within every charter on its chain | `M_LASTLINK`: the governor checks only the granting plane's charter |
| | `HavocPlaneBounded`: with one plane signing anything its key can sign, no governor admits outside what the root's tally voted | `M_TRUSTPLANE`: the governor takes a plane's word for its own charter |
| | `BudgetConserved`: leases issued under a charter, and under every charter below it, never exceed its budget | `M_NODEBIT`: a child's budget is not debited from its parent's |
| | `AnyPlaneFences`: after any plane on a chain moves its epoch, no linked admit under a lease below it | `M_STALEEPOCH`: an admit compares only the granting plane's epoch |
| `Intent` | `EveryEffectHasAnIntent`: every effect has an intent, or a person's act, ordered at a commanded plane before it | `M_NOINTENT`: the autonomous plane grants a node's lease with no live intent |
| | `IntentNarrows`: every intent is within its promoted seating | `M_WIDEINTENT`: a successor that widens one field |
| | `AutonomousAddsNothing`: an autonomous plane's log holds no promotion, seating, issuance, bundle change or operator's grant | `M_LITEPROMOTES`: it orders one |
| `Disconnected`, with explicit time | `NoEffectPastTtl`, under a named assumption on drift | `M_NOMARGIN`: a slow clock and no margin. `M_SELFRENEW`: the governor renews its own lease |
| | `RevocationBounded`: the two bounds of §4.3 | `M_LONGTTL`: a grant above `ttlMax`. `M_SELFEXTEND`: a plane extends its own intent |
| | `IrreversibleIsAPersons`: every irreversible effect has a person-signed predecessor ordered at a commanded plane, used once | `M_AGENTRELEASE`, `M_LITERELEASE`, `M_REPLAY` |
| | `ExpiryGrantsNothing`: after expiry the only effects are the seating's terminal behaviour | `M_STACKCHOOSES`: the stack selects it |
| | `ConflictIsAFinding`: a check failing at either reconciliation subtracts and voids nothing | `M_VOID`: reconciliation voids an effect that happened |

**Two liveness statements belong at Tier 0** of the liveness plan (`derived/topak-liveness-2026.10.07.md`), as
invariants over `ENABLED` in the shape of `Emergency_live.tla`: with a lease lapsed, the terminal behaviour is
enabled whatever the stack does; and while a release lease is live and the vehicle is linked, a release call can
be admitted whatever any agent or Observer is doing.

**What the modules could not show.** The timing budget is only partly expressible in TLA+ (ToO §11.3). That a
vehicle reaches its safe state is physics. That the governor is the only path to the actuators is a claim about
hardware. And a proof of these modules would be of the modules: no refinement to running code exists anywhere in
the corpus (G11 §8).

---

## 11. The trusted base, and assumptions of use

**New rows for ADR-0045's table**, each classed by failure direction as that record requires:

| Row | Class | If it fails |
|---|---|---|
| The governor's admit path | Trust root | Anything the stack requests may reach an actuator |
| The governor's clock | Trust root, slow direction | Authority outlives `ttl` or an intent's `expiry` |
| The governor's key store | Trust root | The vehicle's principal, and its replica, are whoever holds the key |
| The navigation source | Trust root for area checks | The envelope is somewhere else |
| The effector interlock | Trust root | An irreversible effect without a person's act |
| The recovery function | Trust root for the terminal behaviour | Expiry with no safe state |
| Cedar and the Wasm engine on the vehicle | Existing rows, instantiated on every vehicle | As those rows say |
| The link | Delegated | Loss only subtracts: the plane is meshed, or the vehicle is alone |
| Byzantine agreement at an exposed plane | Trust root, in place of the replica row there | A forged certificate |

**New assumptions of use.** A deployment that does not meet them does not inherit anything §10 would prove.

| Assumption | If it does not hold |
|---|---|
| The governor is separate from the stack and is the only path to the actuators | The stack is `Mediated`, and every property here is void. This is A1 for a vehicle |
| Each clock is slow by at most ρ, and the margin is at least ρ times the interval | `NoEffectPastTtl` and `RevocationBounded` are void |
| Effect classes are declared as what they are | An irreversible effect is reachable by an agent, or by a governor alone |
| Each vehicle class has a declared safe state, and its recovery function reaches it in bounded time | The terminal behaviour is a stall, which for a body in motion is not safe |
| A trained, authorized person is at each release seat and can see what the act requires | HITL is a key and not a judgment |
| Fewer than a third of any exposed plane's replicas are captured | That plane is captured. It is bounded by its charter or intent, and by nothing else |
| What a vehicle does to the world other than through its entries is declared as outside the alphabet | Effect exclusivity is claimed for a body, and is false |

---

## 12. What this gives up

1. **No delegation.** Planes grant below themselves. It attenuates, it is a mechanism's and it is budgeted, and
   it is still delegation.
2. **Safety without clocks, below the intent boundary.** Meshed, an intent's `expiry` ends authority. Alone, a
   lease's `ttl` does. Neither value has been measured.
3. **An ordered admit before every effect, for a vehicle that is alone.** There the ordered predecessor is the
   intent and the grant, and no admit can be voided.
4. **A person in reach.** Meshed, findings still subtract and nobody can respond. Alone, nothing reads.
5. **Inexpressibility of irreversible effects.** They are expressible by a person. ADR-0032 §4 is relaxed.
6. **A small trusted base.** Every vehicle carries one, and every exposed plane needs Byzantine agreement.
7. **"Not autonomous."** The corpus dropped the word because no principal seats, delegates to or addresses
   another. That stays true of every principal. It is no longer true that a person is always on the plane that
   orders an effect.

**What the third prompt bought back.** The first draft gave up tempo, and left coordination among cut-off vehicles
out. An intent is one commander's act inside a quorum's vote (§3.2), and meshed vehicles coordinate through their
own plane (§8).

---

## 13. Questions for the custodian

| # | Question | Recommended |
|---|---|---|
| 1 | Is §2.3's rule right: a promotion for a new issuer or artifact, an ordered admit otherwise? ⟨8⟩ | Yes |
| 2 | Is "lite" defined by having no path that changes authority, and declared as a degenerate plane with its additions reported upstream (§3.3, §3.4)? ⟨11⟩ | Yes |
| 3 | Do an autonomous plane's replicas run on the vehicles themselves? | Yes. Relay nodes are allowed and declared |
| 4 | Is an intent bounded by the last intent, as ADR-0050 bounds a successor grant, or by the promoted seating (§3.2)? | The seating. Otherwise a commander who narrows cannot restore, and will not narrow |
| 5 | Is the person the actor, or do they countersign an agent's proposal (§6)? | The actor |
| 6 | Is `release` a new seat kind, or the `emergency` kind reused? | A new kind with the same activation. An emergency envelope is the domain's whole allowlist. A release envelope is the opposite: irreversible entries only |
| 7 | Is Byzantine agreement required at a plane whose replicas can be captured (§2.5)? | Yes, declared per plane, and always at an autonomous one. It reverses ADR-0045 for those planes only |
| 8 | One floor for the federation, or one per plane? | One |
| 9 | Is a cell's Observer seated on another vehicle, and is a vehicle alone exempt from coupling (§5.6)? | Yes to both |
| 10 | May a person hold an orchestrator seat at a commanded plane (§8)? | Yes |
| 11 | Is this a change to the archetype, or one deployment's overlay under ADR-0058 (Proposed)? | An overlay first, reported upstream under its §6. Every item in §12 is a cost to a deployment that never loses its link |

**Settled since the first draft:** the reading of "mesh fence" ⟨9⟩, and where an effect is admitted ⟨10⟩.

---

## 14. The records this would become

Unnumbered, since nothing is decided. In dependency order:

1. **Planes and charters** (§2). Confirmation-required at least under C1, since every grant below the root
   travels the path it opens, and C3, since it reverses ADR-0045 on Byzantine agreement. It also contradicts
   ADR-0054's sentence on delegation, and that record is Proposed. Amends ADR-0024, ADR-0031 and ADR-0045.
2. **The intent and the autonomous plane** (§3). Rests on ADR-0050 and ADR-0055, so it is provisional while the
   first is and cannot be ratified before the second. Under C1 and C2.
3. **The vehicle alone** (§4, §5). Amends ADR-0032's first clause, ADR-0015's sentence on predecessors and
   ADR-0033 §4's void. Under C2 and C3.
4. **Effect classes and the release seat** (§6). Amends ADR-0032 §4, ADR-0037's seat kinds and ADR-0049's entry
   schema, beside ADR-0052. Provisional while ADR-0052 is.
5. **The `federation` floor stage** (§7.2), gated as each stage is, and in force only with a ratified floor.
6. **The threat model** (§9), as an annex to ADR-0045 or a record of its own.

**What this does not claim.** It does not make an act lawful or right. It does not judge identification, intent or
proportion. It does not show that any vehicle is confined: no real principal is `Contained` at the reference
today, for software agents either (G11 §8). `T_intent`, `T_alone`, ρ and the Observer's latency are placeholders.
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
