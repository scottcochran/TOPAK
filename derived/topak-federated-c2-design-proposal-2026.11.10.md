# TOPAK as the authority tier of a command chain: federated planes that only narrow, a lease that outlasts its link, and irreversible effects held by people

> What if TOPAK is treated as the top tier of a command and control chain? Missions are promoted bundles. DAG
> workflows are cells of command chains. Mesh workflows are lowest level of field command autonomy: Brigade Combat
> Team (BCT) (Army) / Marine Expeditionary Unit (MEU) or Regimental Combat Team (RCT) (Marines), commanded by an O-6
> (Colonel). The Robots/Drones are Company / Troop / Battery level: WASM bundles with ROE, fully Byzantine, fence
> bounded.
>
> Draft a design proposal: 1. Federated control planes that only narrow. 2. TTL as safety, bounded by mesh fence.
> 3. Threat model. 4. Irreversible effects are human (HITL?). 5. ROE as promoted WASM bundle. 6. Robot/drones have
> disconnected alphabet. 7. Cedar floor in force with ROE. All the rest as you say.

(The custodian's two prompts of 2026.11.10, with spelling and punctuation normalized.)

**Date:** 2026.11.10 · **Against:** the tree at `a157659`, Genesis Checkpoint G11 and Theory of Operation revision 15
(cited below as ToO) · **Status:** design proposal. **Nothing here is a decision, and nothing here is modelled,
checked, built or reviewed.** · **Drafted by the assistant** at the custodian's request, from a discussion of
2026.11.09 and 2026.11.10. The custodian settled the seven items above, marked ⟨1⟩ to ⟨7⟩ where each is used, and
the tier mapping in §1. Every other choice is the drafter's, marked *(drafter's choice)* where the alternative was
live. §12 lists nine questions for the custodian, each with a recommended answer.

**It rests on text that is not settled.** ADR-0054 and ADR-0055 (workflows) are Proposed. ADR-0050 (the operator)
and ADR-0052 (the emergency seating) are provisional. No floor is ratified. Under A17 nothing should be built on
this that could not be rebuilt. ADR-0056 to ADR-0058 were read by title only, except ADR-0058 §1, §5 and §6.

**Scope.** This is about authority: who may cause which effect, for how long, under whose rules, and what record it
leaves. It is not a design of a vehicle, a sensor or an effector, and it says nothing about how a person decides
that an irreversible act is right.

**The proposal in brief.** A deployment becomes a tree of control planes. Each plane is seated by a promotion at
the plane above it and can hand down only what it was handed, or less. A vehicle carries the last link of that
tree with it: a small trusted component, here called the **governor**, which holds the vehicle's lease and stands
between the vehicle's autonomy software and its actuators. While the link to a plane is up, the vehicle works as a
Run principal does today. While it is down, the governor admits a marked subset of actions for at most the lease's
TTL, and then does one thing that was fixed in advance. An effect that cannot be undone is in no agent's alphabet
and is never admitted without a link: a person holds the seat that reaches it.

**It reverses three positions the corpus holds, and relaxes a fourth.** Each is named where it is used and again
in §11:

- No principal grants another (ToO §2.11).
- Clocks buy liveness, never safety (ADR-0032; ToO §10).
- Every effect has a consensus-ordered admit before it (ADR-0015; ToO §4.1).
- An effect with no timing budget must not be reachable from the alphabet at all (ADR-0032 §4). Relaxed, not
  reversed: it becomes reachable by a person and by nobody else.

---

## 1. Terms and tiers

| Term | Meaning here |
|---|---|
| **Plane** | One replica set with one log, one epoch and one set of rules in force. Every deployment the corpus describes today is one plane |
| **Charter** | The artifact that seats a plane at its parent: the child's replica keys, the bundle revisions it runs under, and its bounds (§2.1) |
| **Chain** | The charters from the root plane down to a granting plane, with a lease at the end |
| **Governor** | The admit path on a vehicle. It verifies the chain, holds the lease, evaluates the floor and the bundles, measures time and position itself, and is the only path to the actuators. It is mechanism, not a principal |
| **Stack** | The autonomy software on a vehicle: planning, perception, any model. It is the Thinker, and it is Byzantine |
| **Connected admit** | An admit decided and ordered at a plane before the effect, as every admit is today |
| **Disconnected admit** | An admit decided by the governor under a live lease, recorded on the vehicle, and ordered later (§4.4) |
| **Terminal behaviour** | What the governor does when a lease ends with no successor. It is fixed at seating (§4.5) |
| **Effect class** | `reversible` or `irreversible`, declared per allowlist entry with its `T_irrev` (§4.3) |
| **Release seat** | A seat held by a person, the only kind whose alphabet reaches an irreversible entry (§5) |

"Gate" is not used for the vehicle's component because the corpus already uses it three ways.

**The tiers**, with the custodian's mapping:

| Tier | The custodian's words | In this proposal |
|---|---|---|
| Root plane | "TOPAK as the top tier" | Holds the anchor's rules, the floor and the rosters. Seats the planes below it |
| Intermediate planes | "DAG workflows are cells of command chains" | Each promotes missions: a bundle revision, a DAG workflow and the charters of the planes below (§6.1, §7) |
| Field plane | "Mesh workflows are lowest level of field command autonomy", at brigade level | The lowest plane. Runs mesh workflows under a budget and grants the vehicles' leases |
| Vehicle | "Company / Troop / Battery level: WASM bundles with ROE, fully Byzantine, fence bounded" | A governor and a stack. It holds a lease and never grants one |

---

## 2. Federated planes that only narrow ⟨1⟩

### 2.1 A plane is seated by a promotion at its parent

The parent's quorum votes on a **charter**, as it votes on any seating (ADR-0024 A3). The charter has a closed
schema, as the lease has (ADR-0031), and a capability that is not a field is not carried:

| Field | What it bounds |
|---|---|
| `plane`, `replicas` | The child's identity: its replica keys and its quorum rule |
| `parent`, `parentEpoch`, `parentFence` | Where it hangs: the parent's epoch, and the parent's log index at the seating |
| `floor` | The floor's digest. It equals the parent's: one floor for the federation *(drafter's choice; question 5)* |
| `bundles` | The parent's list of bundle revisions, in order, plus any this seating adds |
| `alphabet`, `labels` | The entries and labels a lease under this charter may carry |
| `ttlMax` | The longest lease `ttl` the plane may grant, per effect class. This is `T_disc` for everything below it (§3) |
| `budget` | The most leases the plane and every plane below it may ever issue |
| `expiry` | The charter's own life, on the clock of whoever checks it. Never later than the parent's |
| `release` | Whether a release seat may be seated at this plane (§5) |

**Every field is the parent's or narrower.** A child's `budget` is debited from its parent's when it is seated, so
the root's tally bounds the whole tree. ADR-0055's activation budget is the same object for one mesh.

### 2.2 Policy narrows by composition, and nothing compares two policies

At any admit, at any plane or governor, the decision is the floor's permit and no refusal from any bundle on the
chain. A lower plane may promote a bundle of its own. It is appended, it can refuse, and it is never asked whether
to grant (ToO §3.1). So "narrower than the parent" holds of the composed decision for every bundle, at every plane,
at every age. This is ADR-0030's argument applied once per link, and it needs no cross-plane check.

The other fields are sets and numbers. They narrow by a field-wise comparison, made three times: before the vote,
when the seating is applied, and by every verifier of the chain. That is ADR-0033 §4's rule: checked again where
it is applied.

### 2.3 A plane is a havoc issuer, bounded by its charter

ADR-0025 treats the anchor as a havoc issuer bounded by the rules floor: safety must hold for every issuance it
could make (ToO §7.2). **A plane gets the same treatment, bounded by its charter.** Whatever a plane signs, a
governor accepts only what every charter on the chain allows. A captured plane therefore chooses among leases its
parent's quorum already voted acceptable. That is the orchestrator's position in ADR-0054, one level up: it decides
which, never whether.

**This is delegation, and the corpus excluded it.** "No principal grants another, so there is no chain of
delegation to attenuate" (ToO §2.11), and the 2026.10.12 edit dropped "autonomous" from the pattern's description
for that reason. The proposal's answer is that the grantor is a mechanism and not a model, the delegation only
attenuates, and it is budgeted. The sentence is still reversed in letter. The 11.05 lattice analysis left "a
federated authority" as an axis it did not place (`derived/topak-safety-liveness-quorum-lattice-2026.11.05.md`).

### 2.4 The chain is verified where there is no link

A governor must check a lease with no plane in reach. So every charter and every lease carries a **commit
certificate**: signatures from a quorum of the issuing plane's replicas over the entry's digest and log index. The
governor verifies from the anchor's key down. That key is resident on the vehicle, as genesis rules are resident
in a mechanism release (ADR-0027; ToO §7.4).

**A crash-recovery protocol cannot supply that certificate.** One lying replica can obtain a majority's signatures
for two different entries at one index, in two ballots. A plane whose replicas can be captured therefore needs
Byzantine agreement, with n ≥ 3f + 1 replicas and certificates of 2f + 1 signatures. The letters name roles and an
instrument may be substituted (ToO §1), so this is a change to the P role's obligation at such a plane, not to the
pattern. It does reverse ADR-0045's decision not to require it (ToO §12 item 9; question 4).

### 2.5 Ending a plane

A parent ends a child with a **plane fence**: the parent's epoch moves, and every charter and lease below is
stale. It is a subtraction, so it needs no quorum and is ordered (ToO §4.1). Connected holders learn of it at
their next admit. **A captured plane does not pass it on**, and a governor that can reach only that plane learns
nothing. For those governors the bound is the lease's `ttl`, and for the plane it is the charter's `expiry`. Both
are clocks, which is §3.

---

## 3. The TTL is a safety parameter ⟨2⟩

### 3.1 What changes

"Clocks buy liveness, never safety. Epoch fencing carries safety without reading a clock, so an expired lease its
holder still believes in is not a containment violation" (ToO §10). That holds because the admit path is outside
the holder and compares the epoch on every action. **On a disconnected vehicle the admit path is the governor, and
it travels with the holder.** No fence reaches it. The lease's `ttl`, read on the governor's clock, is then the
only thing that ends authority.

### 3.2 The bound, and the reading of "mesh fence"

*(Drafter's reading; question 1.)* A vehicle's lease is granted at the field plane, the tier the custodian maps to
the mesh. It carries that plane's fence, the log index at grant, as every lease does (ToO §2.5), and its life is
nested inside that plane's charter:

- `ttl` is at most the charter's `ttlMax` for the widest effect class in the lease's disconnected alphabet.
- The lease expires no later than the charter does, and the charter no later than its parent's.

Three properties follow, and §9 names each:

| Property | Statement |
|---|---|
| **Revocation is bounded** | A vehicle revoked or fenced at time *t* has no effect under that lease after *t* + `T_disc` |
| **Stale rules are bounded** | A tightened bundle reaches a principal at its next grant (ToO §2.5), so superseded rules stay in effect on a disconnected vehicle for at most `T_disc` |
| **Exposure is bounded** | A charter can never put out more lease-time than `budget` × `T_disc` |

If "mesh fence" meant an area on the ground, that is a bundle value checked against the governor's own position
(§4.1). It bounds where, not how long.

### 3.3 The clock

The governor reads its own monotonic clock and stops admitting at `ttl` less a margin, which errs early as
ADR-0031 E1 requires. If the clock runs slow by at most a fraction ρ and the margin is at least ρ × `ttl`, real
elapsed time never exceeds `ttl`. Three rules keep that honest:

- **The governor reads no external time.** A time signal from outside is content, as a timestamp in a payload is
  (ADR-0032 §3).
- **The governor cannot renew its own lease.** A renewal is a plane's act and needs a link.
- **The clock is a trust root in the slow direction.** A slow clock preserves authority, which is ADR-0032's test
  for an interval that needs trusted time. Here the trust is in a component outside the principal, the stack, and
  inside the vehicle.

### 3.4 The trade is declared, not designed away

A short `T_disc` sends a jammed vehicle to its terminal behaviour early. A long one is how long a revoked or
captured vehicle keeps acting. `T_disc` is declared per effect class, as `T_irrev` is, in the floor's values.
Like every number in the corpus it is a placeholder until something is measured.

### 3.5 Three postures

The glossary defines the postures by enabling condition, and says Run's window leaves HOTL.

| Effect | Posture | Enabled by | Ended by |
|---|---|---|---|
| Irreversible | HITL | A person's signed act, one per effect, ordered at a plane (§5) | The act is single |
| Reversible, connected | HOTL, as Run today | A plane's admit | Revocation, a fence, expiry, a finding |
| Reversible, disconnected | Unattended, and bounded | The governor's admit under a live lease | `ttl` and the lease's action count |

**The third row is new.** A5 says unattended operation is something "the pattern does not model". This proposal
models it and does not pretend detection covers it: while the record is on the vehicle no Observer reads it, so
ADR-0032 §4's budget has no meaning there. **Nothing in the disconnected alphabet may rest on detection.** What an
entry can do at worst, inside its envelope, for `T_disc`, is what the tally voted to accept. Nothing checks that
the vote was right. It is the floor-fitness problem again (ToO §12 item 2).

---

## 4. The vehicle: a governor, a stack and three alphabets ⟨6⟩

### 4.1 What is Byzantine and what is trusted

The custodian's "fully Byzantine" holds of the stack. It cannot hold of the whole vehicle: something on board must
decide admits when no plane can, and that part is trusted. The governor:

- verifies the chain and holds the lease and the vehicle's key;
- evaluates the floor in Cedar and each bundle on the chain as a Wasm module (§6.1);
- **lifts its own facts**: elapsed time, position, the lease's action count. No safety decision reads a clock a
  principal supplies (ADR-0032 §3), and by the same rule none reads a position the stack supplies;
- hosts each tool as a Wasm component with one capability, its declared channel, which for a vehicle is an
  actuator interface. This is channel fidelity as ADR-0034 A2 has it for Run, and the reference's `wasmtool` is
  its start (`mechanism/README.md`);
- records every admit and denial (§4.4), and carries out the terminal behaviour (§4.5).

Models stay out of the trusted base. The trusted base still grows, on every vehicle (§10).

### 4.2 Three alphabets

| Alphabet | Admitted by | Ordered | Holds |
|---|---|---|---|
| **Connected** | A plane, as today | Before the effect | Every entry in the lease's alphabet |
| **Disconnected** | The governor, under the lease | After, at reconciliation | Entries the bundle marks `disconnected`, inside the envelope, the `ttl` and the action count |
| **Terminal** | Nobody. It is fixed at seating | The expiry is ordered when a plane learns of it | One behaviour per vehicle class: hold, return on a voted route, land or stop |

No agent seat's alphabet holds an irreversible entry, connected or not (§5).

### 4.3 Where "disconnected" is declared

The allowlist entry has five parts (ADR-0049). It gains a sixth, `effect`: the class, its `T_irrev`, and whether
the entry may be admitted disconnected. It is promoted with the bundle and voted like any entry. **An effect class
is a declaration**, as a label is (A15): an irreversible effect declared reversible is seen by nothing here.

### 4.4 The record, and reconciliation

The governor writes each disconnected admit and each denial to a chain on the vehicle. Entries are hash-linked,
signed with the vehicle's key, and numbered by the per-lease sequence the lease already carries (ToO §4.2). On
contact, a plane orders the chain as one entry and runs the mechanism checks at that position.

- **A disconnected admit is never void.** ADR-0033 §4 voids an admit that fails at apply, "ordered, recorded,
  without effect". Here the effect has happened. A check that fails at reconciliation is a **finding against the
  lease**, and it can only subtract.
- **ADR-0015's sentence changes.** Every effect still has a consensus-ordered, signed, authorizing predecessor,
  and it is the lease's grant. The admit itself is ordered first only when connected. The audit chain gains a
  link that is trusted and not proved: the governor.
- **A captured vehicle's chain is not evidence.** It says what its captor signed.

### 4.5 Terminal behaviour, and why expiry grants nothing

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
owner (§10).

### 4.6 Coupling

`R3-observer-live` refuses `Actuate` under a `thinker` seat with no live cell Observer (ADR-0041). No Observer off
the vehicle can keep up with a disconnected one. *(Drafter's choice; question 6.)* Coupling applies to connected
admits, and the disconnected alphabet is exempt, for the reason §3.5 gives: nothing in it rests on detection. An
Observer on the vehicle, of a second lineage and able only to end the round early, is allowed and declared. It
shares the vehicle's hardware and fate with its Thinker, so no claim rests on it.

---

## 5. An irreversible effect is a person's ⟨4⟩

**The custodian asked whether this is HITL. It is**, in the glossary's sense of a posture defined by its enabling
condition: an irreversible effect is enabled only by a signed act of a person, made for that one effect.

**What the corpus says today.** For an effect irreversible on emission, "the effect must not be reachable from the
alphabet at all" (ADR-0032 §4; A10). The budget `W + L + D < T_irrev` is HOTL's: it buys time to detect and stop
after emission. Under HITL the judgment comes before the emission and no budget is needed. The proposal therefore
narrows the reach where ADR-0032 removes it: not reachable from any agent's alphabet, not reachable disconnected,
and reachable from one seat kind that a person holds. **That relaxes ADR-0032 §4 as written.** The precedent is
the `emergency` seat, whose actor is a person (ADR-0052; ToO §3.3).

**The `release` seat.**

- **A person holds it**, with a key, and nobody else in the round. No model's Persona binds to the kind.
- **A roster's quorum activates it** for one named person and one round, as an emergency seating is activated
  *(drafter's choice; question 3)*. The roster is anchor-issued (ADR-0013), so no plane below the root can mint a
  person, and a governor checks the key against the roster resident on the vehicle.
- **Its alphabet is `Actuate` on irreversible entries in its envelope, and `Report`.** It is seated only at a
  plane whose charter carries `release`.
- **The person is the actor, not a countersigner** *(drafter's choice; question 2)*. The stack may `Report` what
  it perceives. That report is ingress to the person, labelled as untrusted, and it enables nothing. A design in
  which an agent proposes and a person approves would put the agent's output on the path to the effect.
- **Each act is one admit.** It names the entry, its inputs, the vehicle and the lease's fence. It is ordered at a
  plane and delivered with its commit certificate. The governor's interlock checks the person's key, the
  certificate, that the act is fresh and unused, and that the entry is in the seat's envelope. It is never
  admitted disconnected.

**What the mechanism records, and what it cannot judge.** It records who acted, on what, through which vehicle and
when. It does not record why: "the reason is unknown to the mechanism, by construction" (ADR-0052). Whether the act
was right is the person's judgment, and the mechanism checks none of it. It also "cannot tell a person from a
program holding the person's key" (ToO §3.3). A5 applies in full: a trained, authorized person is present, and
this proposal adds that they can see what the act requires them to see.

**The cost.** With no link there is no irreversible effect, and an adversary who jams the link gets that for
nothing. The boundary register already criticizes "fail-closed uniformity presented as costless" (ToO §10). Here
it is presented as a cost, and accepted.

---

## 6. Rules of engagement live in three places ⟨5⟩ ⟨7⟩

| Part of the rules | Where it lives | Why there |
|---|---|---|
| Standing rules that hold for every mission | The Cedar floor, in force at every plane and every governor | It is the verified object, and no bundle can weaken it |
| A mission's rules that can be lifted mechanically | A promoted bundle, compiled to Wasm | Voted by digest, able only to refuse, and evaluated the same way at a plane and on a vehicle |
| Rules that need a judgment about the world | Nowhere in the admit path | ADR-0007: no semantic judgment is an enabling condition |

### 6.1 The mission's rules are a promoted Wasm bundle

A bundle can express what a mechanical lift can supply: areas, time windows, which entries a seat kind may use,
counts, a declared control mode per effect class, and lists that come from a declared source and carry its label.
A lower plane tightens by appending a bundle (§2.2). Loosening needs a promotion at a plane whose charter allows
it, and otherwise goes up the tree. That asymmetry is the one the corpus already has between subtraction and grant.

**The Wasm path exists at the reference.** `topak-bundle` loads a signed bundle into an in-process engine bound to
the lease's revision, as the fallback when the sidecar cannot answer (`mechanism/README.md`; ToO §15). On a
governor that engine is the only one. Stale bundles are monotone-safe (ToO §3.1), which is what makes local
evaluation sound: an old bundle on a vehicle can refuse too much and cannot allow what the floor refuses.

**"Missions are promoted bundles"** is read as: one tally votes a mission's bundle revision, its workflow and the
charters and seatings it needs, together (ADR-0024 A4, pending). The bundle is the mission's rules. The workflow is
its plan (§7).

### 6.2 The floor, with a `federation` stage

**"In force" is a precondition this proposal cannot meet.** No floor text is ratified. The floor is ratified when
a bootstrap reviewer finds it fit, and no test for fitness is written (G11 §2.2 and item 87; ADR-0029 A4). For
this floor, whether the standing rules are the right ones is a legal judgment as much as a technical one. A grant
seat with that named role is suggested *(drafter's suggestion)*.

The stage would follow `workflow` in `floor/proposed/README.md`. The ids are placeholders.

| Id | Kind | Says |
|---|---|---|
| `FD1-charter-narrows` | forbid | No seating of a plane whose charter exceeds the seating plane's own in any field |
| `FD2-lease-within-charter` | forbid | No grant whose lease exceeds the granting plane's charter: an entry outside its alphabet, a `ttl` above its `ttlMax`, an expiry after its own |
| `FD3-budget-spent` | forbid | No grant, and no seating of a plane, once the charter's budget is spent |
| `FD4-irreversible-release-only` | forbid | No `Actuate` of an irreversible entry under a seat whose kind is not `release` |
| `FD5-irreversible-connected` | forbid | No disconnected admit of an irreversible entry, whatever the seat |
| `FD6-disconnected-marked` | forbid | No disconnected admit of an entry its bundle revision does not mark `disconnected` |
| `FD7-disconnected-bounds` | forbid | No disconnected admit at or past `ttl` less the margin, or with the lease's action count spent |
| `FD8-release-seating` | forbid | No `release` seating of a key that is not on the anchor-issued roster, and none at a plane whose charter lacks `release` |

**Every new entry subtracts. Two existing entries are relaxed**, and each relaxation routes as one (ToO §3.2):
`B10-only-thinkers-author` gains an exception for a `release` seat's `Actuate`, as it has for an `emergency` seat,
and `R3-observer-live` is scoped to connected admits (§4.6).

**The schema gains** the kind `release`; the entity `Plane` with its charter; `effect` on an entry; and, in the
Run context, whether the admit is connected, whether the `ttl` bound is passed and whether the count is spent. The
lift supplies these and the floor trusts its inputs, as the README already says of every stage.

### 6.3 What no policy here expresses

Identification, intent, necessity and proportion are judgments about the world. A classifier's output enters the
system only as a finding, and a finding may subtract authority and never add it (ADR-0007; ToO §2.2). So these
parts of a mission's rules are enforced by nothing in this design. For an irreversible effect they are the
judgment of the person at the release seat. For everything else they are, at most, something an Observer may
object to after the fact.

---

## 7. Missions as workflows

- **A DAG is a plan with branches**, promoted at an intermediate plane. A node is one round of one cell, and a cell
  here is a vehicle's stack with its Observer. At a decision point an orchestrator chooses among edges the
  mechanism has already enabled, so it "decides how good the work is and never whether it is safe" (ToO §2.11).
  A person may hold an orchestrator seat *(drafter's suggestion; question 7)*.
- **A mesh is the field plane's kind.** Loops are allowed, the number of turns is decided at run time, and the
  activation budget is the charter's `budget`. That is the "field command autonomy" of the custodian's mapping:
  choice among enabled edges, bounded in count.
- **It is still not choreography.** In a mesh "the mechanism is the bus", and cells reacting to each other with
  nobody deciding what runs next "is not supported" (ADR-0055). Vehicles do not address each other. **While disconnected
  they do not coordinate through the mechanism at all**: the disconnected alphabet holds no action on another
  vehicle. Coordination among disconnected vehicles is outside this proposal (question 9), and it is the part of
  "swarm" this design does not reach.

---

## 8. Threat model ⟨3⟩

The corpus's adversary is the agent. A deployment of this kind adds an adversary that attacks links, hardware and
planes. Each row says what bounds the adversary and what is left.

| # | Adversary | What it can do | What bounds it | What is left |
|---|---|---|---|---|
| TM1 | **The stack**, Byzantine as ADR-0007 has it | Request anything, at any time | The governor, the alphabet, the envelope | Anything inside the envelope was voted acceptable. What the vehicle's body does that no entry names is outside the alphabet |
| TM2 | **The link adversary**: jams, drops, delays, replays, injects | Force disconnection; delay a revocation or a tightened bundle; block every irreversible effect | Certificates stop forgery. The fence and sequence numbers stop replay. `T_disc` bounds the delay | Denial is always available to it, and the vehicle's response is predictable: the disconnected alphabet for `T_disc`, then the terminal behaviour |
| TM3 | **A captured vehicle** | Extract the key and the lease; act as that principal; sign any local record | The lease's envelope and its remaining `ttl`. Revocation, once a plane knows | The interlock is moot when the effector itself is captured. Resistance to tampering is the builder's, and is a trust-root residual |
| TM4 | **One compromised replica** at an exposed plane | Under crash-recovery consensus, propose an admit no floor evaluated (A9) | Byzantine agreement and commit certificates (§2.4) | Holds for fewer than a third of the replicas |
| TM5 | **A captured plane**: a quorum of its replicas | Issue any lease within its charter, to anyone; withhold revocations; falsify its log | The charter, checked by every governor. The charter's `expiry`. No power to mint a person for a release seat | Everything within the charter until it expires. A captured plane with `release` can order a person's genuine act and can replay one inside its freshness window |
| TM6 | **An insider with a key**: an operator or a release person | Whatever that seat may do | Attribution. An operator's add needs a live peer (ADR-0050) | The mechanism cannot tell a person from a program holding the key. A wrong act by a release person is recorded and not prevented |
| TM7 | **Navigation deception** | Move the envelope in the world by falsifying the governor's position | Nothing in this design | The navigation source is a trust root with this residual. Time is not exposed the same way, since the governor reads no external time |
| TM8 | **Deception of perception**, the stack's or a person's | Make the stack or the person wrong about the world | For the stack, the premise already assumes it. Perception never adds authority | A deceived person at a release seat is a semantic failure. Nothing here sees it |
| TM9 | **Supply chain**: weights, tools, bundles | Ship a bad artifact | Promotion by digest. Lineage independence, which is Proposed (ADR-0035) | As the corpus states it today |
| TM10 | **A colluding Observer on the vehicle** | Stay silent | Nothing. Coupling cannot see collusion (A13) | No claim rests on that Observer (§4.6) |

**Out of scope**: physical destruction of vehicles or planes; attacks on sensors other than as TM7 and TM8; what
an adversary learns by watching which planes and vehicles talk; and the security of the anchor's custody, which
ADR-0025 declares per deployment.

---

## 9. What would be checked

By ADR-0046's method each property ships with a mutation that breaks it and nothing else, and a witness that the
behaviour it constrains is reachable. **None of this is written.** The modules would be drafted by
`skills/writing-tla-specs-and-proofs/`.

| Module | Property | A mutation that must break it |
|---|---|---|
| `Federation` | `CharterNarrows`: every seated plane's charter is its parent's or narrower, field by field | `M_WIDEN`: a seating that widens one field |
| | `LeaseWithinChain`: every lease a governor accepts is within every charter on its chain | `M_LASTLINK`: the governor checks only the granting plane's charter |
| | `HavocPlaneBounded`: with one plane signing anything its key can sign, no governor admits outside what the root's tally voted | `M_TRUSTPLANE`: the governor takes a plane's word for its own charter |
| | `BudgetConserved`: leases issued under a charter, and under every charter below it, never exceed its budget | `M_NODEBIT`: a child's budget is not debited from its parent's |
| | `PlaneFenceStopsConnected`: after a plane fence, no connected admit under any lease below it | `M_STALEEPOCH`: an admit compares only its own plane's epoch |
| `Disconnected`, with explicit time | `NoEffectPastTtl`, under a named assumption on drift | `M_NOMARGIN`: a slow clock and no margin. `M_SELFRENEW`: the governor renews its own lease |
| | `RevocationBounded`: no effect under a revoked lease later than `T_disc` after the revocation | `M_LONGTTL`: a grant above `ttlMax` |
| | `IrreversibleIsAPersons`: every irreversible effect has a person-signed, plane-ordered predecessor, used once | `M_AGENTRELEASE`, `M_OFFLINERELEASE`, `M_REPLAY` |
| | `ExpiryGrantsNothing`: after expiry the only effects are the seating's terminal behaviour | `M_STACKCHOOSES`: the stack selects it |
| | `ConflictIsAFinding`: a check failing at reconciliation subtracts and voids nothing | `M_VOID`: reconciliation voids an effect that happened |

**Two liveness statements belong at Tier 0** of the liveness plan (`derived/topak-liveness-2026.10.07.md`), as
invariants over `ENABLED` in the shape of `Emergency_live.tla`: with a lease lapsed, the terminal behaviour is
enabled whatever the stack does; and while a release lease is live and the link is up, a release call can be
admitted whatever any agent or Observer is doing.

**What the modules could not show.** The timing budget is only partly expressible in TLA+ (ToO §11.3). That a
vehicle reaches its safe state is physics. That the governor is the only path to the actuators is a claim about
hardware. And a proof of these modules would be of the modules: no refinement to running code exists anywhere in
the corpus (G11 §8).

---

## 10. The trusted base, and assumptions of use

**New rows for ADR-0045's table**, each classed by failure direction as that record requires:

| Row | Class | If it fails |
|---|---|---|
| The governor's admit path | Trust root | Anything the stack requests may reach an actuator |
| The governor's clock | Trust root, slow direction | Authority outlives `ttl` |
| The governor's key store | Trust root | The vehicle's principal is whoever holds the key |
| The navigation source | Trust root for area checks | The envelope is somewhere else |
| The effector interlock | Trust root | An irreversible effect without a person's act |
| The recovery function | Trust root for the terminal behaviour | Expiry with no safe state |
| Cedar and the Wasm engine on the vehicle | Existing rows, instantiated on every vehicle | As those rows say |
| The link | Delegated | Loss only subtracts: the vehicle is disconnected |
| Byzantine agreement at an exposed plane | Trust root, in place of the replica row there | A forged certificate |

**New assumptions of use.** A deployment that does not meet them does not inherit anything §9 would prove.

| Assumption | If it does not hold |
|---|---|
| The governor is separate from the stack and is the only path to the actuators | The stack is `Mediated`, and every property here is void. This is A1 for a vehicle |
| The governor's clock is slow by at most ρ, and the margin is at least ρ × `ttl` | `NoEffectPastTtl` is void |
| Effect classes are declared as what they are | An irreversible effect is reachable by an agent, or disconnected |
| Each vehicle class has a declared safe state, and its recovery function reaches it in bounded time | The terminal behaviour is a stall, which for a body in motion is not safe |
| A trained, authorized person is at each release seat and can see what the act requires | HITL is a key and not a judgment |
| Fewer than a third of an exposed plane's replicas are captured | Certificates can be forged at that plane |
| What a vehicle does to the world other than through its entries is declared as outside the alphabet | Effect exclusivity is claimed for a body, and is false |

---

## 11. What this gives up

1. **No delegation.** Planes grant below themselves. It attenuates, it is a mechanism's and it is budgeted, and
   it is still delegation.
2. **Safety without clocks.** On a disconnected vehicle a clock ends authority, and `T_disc` is a safety value
   nobody has measured.
3. **An ordered admit before every effect.** Disconnected, the ordered predecessor is the grant, and no admit can
   be voided.
4. **Detection.** There is none while a vehicle is disconnected. The envelope carries everything.
5. **Inexpressibility of irreversible effects.** They are expressible by a person. ADR-0032 §4 is relaxed.
6. **A small trusted base.** Every vehicle carries one, and exposed planes need Byzantine agreement.
7. **Tempo.** A promotion needs every grant seat at the archetype, and "liveness equals the availability of every
   grant seat" (ToO §7.1). A command chain decides by one commander. A deployment that needs that declares a
   threshold, and the capture it accepts with it.

---

## 12. Questions for the custodian

| # | Question | Recommended |
|---|---|---|
| 1 | Is "mesh fence" the field plane's fence with nested expiry (§3.2), or an area? | The first. The area is a bundle value and bounds where, not how long |
| 2 | Is the person the actor, or do they countersign an agent's proposal (§5)? | The actor |
| 3 | Is `release` a new seat kind, or the `emergency` kind reused? | A new kind with the same activation. An emergency envelope is the domain's whole allowlist. A release envelope is the opposite: irreversible entries only |
| 4 | Is Byzantine agreement required at a plane whose replicas can be captured (§2.4)? | Yes, declared per plane. It reverses ADR-0045 for those planes only |
| 5 | One floor for the federation, or one per plane? | One |
| 6 | Are disconnected admits exempt from coupling, or is an Observer on the vehicle required (§4.6)? | Exempt, with the Observer optional and declared |
| 7 | May a person hold an orchestrator seat at a decision point (§7)? | Yes |
| 8 | Is this a change to the archetype, or one deployment's overlay under ADR-0058 (Proposed)? | An overlay first, reported upstream under its §6. Every reversal in §11 is a cost to a deployment that is never disconnected |
| 9 | Should disconnected vehicles coordinate with each other? | Not yet. It stays out until `Federation` and `Disconnected` are checked |

---

## 13. The records this would become

Unnumbered, since nothing is decided. In dependency order:

1. **Planes and charters** (§2). Confirmation-required at least under C1, since every grant below the root
   travels the path it opens, and C3, since it reverses ADR-0045 on Byzantine agreement. It also contradicts
   ADR-0054's sentence on delegation, and that record is Proposed. Amends ADR-0024, ADR-0031 and ADR-0045.
2. **The disconnected lease** (§3, §4). Amends ADR-0032's first clause, ADR-0015's sentence on predecessors and
   ADR-0033 §4's void. Under C2 and C3.
3. **Effect classes and the release seat** (§5). Amends ADR-0032 §4, ADR-0037's seat kinds and ADR-0049's entry
   schema, beside ADR-0052. Provisional while ADR-0052 is.
4. **The `federation` floor stage** (§6.2), gated as each stage is, and in force only with a ratified floor.
5. **The threat model** (§8), as an annex to ADR-0045 or a record of its own.

**What this does not claim.** It does not make an act lawful or right. It does not judge identification, intent or
proportion. It does not show that any vehicle is confined: no real principal is `Contained` at the reference
today, for software agents either (G11 §8). `T_disc`, ρ and the Observer's latency are placeholders. Like most of
this corpus, it has been read by nobody independent of its author.
