# TOPAK — Glossary

**2026.10.09** · narrative · the glossary head, revised in place · DRAFT

**Basis.** Genesis Checkpoint G11 (2026.10.09) and Theory of Operation revision 15 (`narrative/theory-of-operation.md`,
tag `ToO-rev15`), with the record files they cite. Where the two disagree, G11 wins. The five Proposed records
(ADR-0035, ADR-0036, ADR-0051, ADR-0054, ADR-0055) and the one Proposed section (ADR-0022 §6) appear under their
subjects, tagged **[P]**, and are collected in §10. **Twelve amendments are pending**, every one on a Proposed record,
and their terms are tagged **[P]** too. Two records, ADR-0050 and ADR-0052, and the amendments that depend on them are
in force and **provisional**; their terms are tagged **[A·Pv]**.

**What this supersedes.** The 2026.10.05 revision (tag `glossary-2026.10.05`), cut against G10 and revision 14;
`git diff glossary-2026.10.05 glossary-2026.10.09 -- narrative/glossary.md` reads the two side by side. The entries
G11 changed are rewritten: *checked* and *proved*, *certified*, *the prover*, which is now known to be unsound in two
ways, the trusted base's count, the binding table, the floor stages and schema S, refinement, trace validation, the
reference implementation and its findings, and the counts of batches, confirmation markers and pending amendments.
The terms the records owed are added. From ADR-0053: *proved in Lean*, *re-encoding*, *transcription*, *model*,
*statement in the model*, *replay* and *trace replay*, with *graph check*, *derived premise*, `refines(Seats)` and
*the Lean toolchain*. From ADR-0054, Proposed: *workflow*, *node*, *edge*, *guard*, *decision point*,
*orchestrator*, *input* and *route*. From ADR-0055, Proposed: *mesh*, *activation*, *causal history*, *decision
event*, *budget* and *track*. From G11: *unsound case*, *proof scan*, *liveness extension*, *leads-to* and *fairness*.
§14 lists the wording that retired. Before these, the 2026.10.02 revisions (tags `glossary-2026.10.02` and
`glossary-2026.10.02b`, against G9), the 2026.10.01 revision (tag `glossary-2026.10.01`, against G7), the 2026.09.30
revision (tag `glossary-2026.09.30`, against G6) and the 2026.09.29 glossary (`derived/topak-glossary-2026.09.29.md`
until the reorganization; `git log --follow` reads it). The glossary has no dated copies: a revision is a commit to
this file, and the checkpoint cut with it measures the head.

**This document decides nothing.** It reports what the terms mean in the corpus as it stands, including where two
sources disagree.

---

## 0. How to read

| Tag | Meaning |
|---|---|
| **[A]** | Defined by an Accepted (genesis) record |
| **[A·CR]** | Defined by an Accepted record, or amendment, marked confirmation-required. Cite as *author-ratified* |
| **[A·Pv]** | Defined by a record or amendment Accepted **provisional**: in force, confirmation-required, and subject to redesign (ADR-0029 A4; §9). Cite as *provisional* |
| **[P]** | Defined by a Proposed record, a pending amendment, or a DRAFT artifact. The wording can still move |
| **[D]** | Derived: used in the narrative, with no record of its own |
| **[C]** | Checkpoint convention, fixed by G1–G11 |
| **[R]** | The reference implementation (ADR-0033). It is evidence, not the verified object |
| **[O]** | Outstanding: the term names a hole rather than a mechanism. Numbers refer to the G11 §7 open list |
| **[X]** | Superseded: the term's record is superseded and its text is no longer in force |

Record status is G11 §1 and is not restated here except where the status changes what a term means.

---

## 1. The pattern

**TOPAK** [A/D]: a safe-by-design architecture pattern for agentic AI collaboration. The
letters name **roles, not products** (ADR-0030 §2, ADR-0033 §2). Each role carries a stated obligation, and any
instrument that meets it may be substituted.

| Letter | Role | Instrument at the reference |
|---|---|---|
| **T** | Formal specification, model checking and proof | TLA+, TLC, the TLA+ Proof System; Lean 4 as a second deductive method (ADR-0053) |
| **O** | Policy as code: a verified floor evaluator and a per-request bundle engine | Cedar (floor), OPA and Rego (bundle) |
| **P** | Consensus over the control plane | Sans-IO Multi-Paxos |
| **A** | The principals doing the work | Agents, reached through MCP |
| **K** | Event transport | Kafka |

**The premise** [A]: *an agent is Byzantine at every deployment position.* Safety never depends on what a model
means or intends, and models stay out of the TCB (ADR-0007).

**The inversion** [D]: the Byzantine threat lives in **Build**, not Run, because Build principals author the
specifications, policy and floors that Run is judged against.

**Safe by design** [D]: the project's descriptor. It means *containment checked about the mechanism*. It never means
*safe outputs*.

---

## 2. Domains, principals, the membrane

**`Build`** · **`Run`** [A]: the domain that produces artifacts, and the domain that operates them (ADR-0001).

**`Contain`** [A]: the containment component. It is one component instantiated twice, not a third domain.

**`Build(Contain) → Run(Contain)`** [A]: the structure. The arrow is authority flow. The parentheses are a
refinement boundary: specification conjunction plus existential hiding (ADR-0001, ADR-0002). The notation does not
survive being spoken, so prose has to carry the nesting.

**Boundary-enforceable containment** [A]: what `Contain` claims. It has two conjuncts: a **checked** property class
over the alphabet and its envelope, and **assumed, operationally discharged** effect exclusivity.

**Principal** [A]: *anything evictable by an authority other than itself.* Principals are inside the proofs. **A
principal holds exactly one seat** (ADR-0037 §1), so the lease's `principal` and `seat` determine each other.

**At the gate** [A]: whatever is not evictable. It sits outside the proofs and is carried as an assumption or a
declaration. **Resignation is not eviction** (ADR-0002 A2). At archetype custody the anchor key-holders are at the
gate. At degenerate custody they become principals, which is a type change (§8).

**`Contained(p)`** / **`Mediated(p)`** [A·CR]: a principal that reaches the world only through its alphabet, and one
with some effect path that no action names (a shell, egress, a git remote). Safety theorems quantify over `Contained`
principals. `Mediated` principals get attribution and authorization, not containment. **Rung 0 is `Mediated`,
always.** `Contained(p)` has **four conjuncts** (ADR-0034 §4): a live lease at rung ≥ 1 on an *Attested* verdict at
the declared rung; a profile meeting P3–P5; an in-house Persona; and the lineage-independence criterion in force.
The fourth is ADR-0035, Proposed, so **`Contained` is unreachable at every rung today.** ADR-0037, ADR-0038 and
ADR-0039 add and remove no conjunct. The reference computes the conjuncts as a lookup and names each that fails
(ADR-0033 A7); it answers yes only for a *SIMULATED* rung-3 lease under a criterion a test issued, which shows
the lookup reachable and claims nothing. For a Run principal, P4 reads as channel fidelity (ADR-0034 A2). **An
operator and an emergency seat are `Mediated` by design**: a person is not confined (ADR-0050 §1; ADR-0052 §1).

**Cell** [A·CR]: the principals seated around one Thinker for a round (ADR-0037 §1). A cell holds no lease, speaks no
alphabet and cannot be evicted as a unit; it names a binding, as a round does. **An LTRO is a cell, not a
principal.**

**Weakest-link provenance** [D]: a candidate with no record number. A provenance chain that contains a `Mediated`
principal yields attribution, not a safety property.

**Action alphabet** [A]: the finite, typed vocabulary of a principal's effects.

**Build alphabet** [A, except §6]: **egress only**, six variants: `Read(ref)` · `Draft(target, content)` ·
`Invoke(tool, inputs)` · `Emit(record)` · `Submit(digest | ⊥)` · `Vote(verdict, digest, evidence, rulesEpoch)`.
Every action carries an epoch and a lease. There are three mechanism parameters: corpus root, tool allowlist and
round bound (ADR-0022).

**Run's alphabet** [A·CR]: three variants and nothing shared with Build but the carrier (ADR-0040, Batch 20, C3 and
C4). **`Consult(ref)`** resolves a content-addressed object inside the pinned **Run root**: ingress, no effect.
**`Actuate(tool, inputs)`** invokes an allowlisted Run tool whose entry declares the **effect channel** it opens:
ADR-0015's tool-invocation class. **`Report(record)`** appends to the principal's round topic: the emission class.
**A read of live state is an `Actuate`.** There is no terminal variant: **a Run round ends when its lease ends**, and a
Run seat cannot abstain (ADR-0042 §5). The provisional pair `RunInvoke` and `RunEmit` is retired; a request naming
either fails validation against S. Its obligations are owned: policy by ADR-0041, mechanism by ADR-0042, the cell by
ADR-0043. A fourth variant, `Route(edge)`, held only by an `orchestrator` seat, is pending with ADR-0054 [P] (§2,
*Workflows*), as are two more ends of a round, on a worker's outcome and on an applied route (ADR-0042 A3).

**Run root** [A·CR]: a second pinned, content-addressed set, as Build's corpus root is; `Consult` is scoped to it
(ADR-0040 §3). What may enter it, and who admits it, is open (ADR-0041 open obligations).

**Effect channel** · **channel fidelity** [A·CR]: a Run tool's allowlist entry declares the channel the tool
opens; the tool is not hermetic and is not asked to be, only to open that channel and no other (ADR-0040 §3).
**ADR-0034 A2 (Batch 30) names its owner**: the tool host's Wasm runtime, which hands a Run tool one network
capability, a connection to its declared target, and nothing else; the target is bound and the protocol on it is
recorded, not enforced. The reference builds it (ADR-0033 A8, Batch 31), and **the entry is the channel's only
declaration**: the tool host reads the target from the entry of the lease's bundle revision, no longer from node
configuration (ADR-0033 A9). For a native Run tool nothing checks it: the declaration is a claim (`mechanism/` G19,
I33), D-0034-6.

**`Actuate` record** [A·CR]: for every admitted `Actuate` the mechanism writes one record to the principal's round
topic when the call returns: seat, fence, log index, sequence number, tool, seat kind and digests of inputs
and result as facts, the bodies as payload (ADR-0042 §3). Since Batch 34 the envelope says `seatKind` where it said
`breakGlass`, and carries four label fields: the input labels, the result's label, the delivery mode and `clearSet`
as it stood (ADR-0042 A1, A2). A call that has not returned when the round seals is written
as `unknown` ahead of the seal marker, and **a result the record does not name is not delivered** (§4).

**Recorded ingress** [A·CR]: a tool's result is ingress and is recorded by digest, so Run's ingress is a closed list
of **four items, each with a label**: the task, each admitted `Consult`'s content, each admitted `Actuate`'s result,
and the round's tool list (ADR-0042 §4; ADR-0043 §1 as amended by A1; ADR-0048). A fifth, `input`, is pending with
ADR-0054 [P].

**Label** [A·CR]: a set of names, from a vocabulary the bundle declares, attached to every item of Run's ingress. **A
label is a function of the item's source**, declared where the source is: the task's at the grant, a `Consult`'s at
the Run root, a result's in the allowlist entry (ADR-0047 §1). It is a syntactic lift: it says what a source was
declared to be and is no judgment about content. The floor reserves two names: **`untrusted`**, content a party
outside the deployment could have written, and **`restricted`**, content that must not leave it. A result's label
covers its inputs: the entry's label joined with the label of every handle among them and, where an input is a
literal, with `clearSet` (R10, the hole `Labels.tla` found). **A label is a declaration and not a finding**: a
source declared trusted that is not is seen by nothing (assumption A15). Build's `Read` is not labelled.

**Delivery** · **clear** · **handle** [A·CR]: the Listener delivers an item one of two ways, by a table in bundle data
from label to mode, per seat kind (ADR-0047 §2, §3). **Clear**: the bytes with their label. As a **handle**: a name for
the item and its label, and no bytes. **A suppressed item's bytes do not enter the guest**, by what the node sends
(the record's C2 claim). A handle may be passed as an argument; the tool host resolves it on the mechanism's side
(T-0045-34), so a Thinker routes content it cannot read. At the reference a handle resolves only to a scalar, from
results one replica holds in memory (item 93).

**Clear set**, `clearSet` [A·CR]: the join of the labels of every item delivered clear to the principal this round,
the task included (ADR-0047 §4). It only grows, and it is **the only history policy reads**: history reaches the
floor as an attribute the mechanism computes, and no temporal operator enters the policy language. A literal
argument has no label of its own, so `clearSet` is its sound bound. A request carrying a `clearSet` behind the
round's is refused at apply.

**Outward entry** [A·CR]: an allowlist entry whose channel reaches a target the issued rules do not list as inside
the deployment (ADR-0047 §7; ADR-0049 §5; ADR-0025 A2). **Derived, never declared**, so a bundle cannot mark its own
entry as inside. The label forbids apply to an `Actuate` of an outward entry.

**Releasing entry** [A·CR]: an entry that declares it **releases** named labels, which removes them from the join
its result's label would carry: a declassifier (ADR-0047 §1). It is promoted and signed like any entry, it is the only way suppressed content becomes clear, and
one that releases a reserved name loads only if the issued rules name it (W8). Each one is a hole a reviewer must
read.

**Tool list** · **interface** [A·CR]: every allowlist entry carries an **interface**, a purpose and a note per input.
At the start of a round the Listener delivers the interface of every entry the lease may call, and no other, as the
mechanism renders it: the **tool list** (ADR-0048). The mechanism writes it to the round's topic as the **opening
record**, so an Observer is given the list its Thinker was given. It cannot change inside a round, and it is **the
only description of a tool with standing**: what a Persona, a task or a consulted object says about a tool is
content. The purpose is prose that passed promotion and is still a claim. Without it: **D-0048-1**.

**Allowlist entry** [A·CR]: one schema, ADR-0049's, in five parts: identity, inputs, interface, labels and channel.
The record is the entry's one statement and says of each field whether it is **checked or claimed**: name, digest
and input types are checked on every call; purpose and notes are prose that passed promotion; a label is claimed,
and bounded; the channel's target is checked for a Wasm tool and claimed for a native one. An input may be marked a
**destination**, which is what `R6` and `R7` read. The reference does not compute §2's digest over the entry's
inputs (item 94).

**Well-formed allowlist** [A·CR]: a bundle whose allowlist fails a load check does not load (ADR-0049 §6, **W1** to
**W10**; ADR-0030 A2). Among them: an outward entry whose result is not labelled `untrusted` (W7), a release of a
reserved name the issued rules do not name (W8), and an outward entry that marks no destination without saying it
has none (W9). The checks are the mechanism's, not the bundle's, and are harder to change than the floor. They read
**the two issued lists** (ADR-0025 A2): the entries that may release a reserved name, and the channel targets inside
the deployment; with neither issued they take the conservative reading.

**Run's confinement obligation** [A·CR]: ADR-0042 §6, in force since Batch 30, which made ADR-0042 accepted whole.
The effect channels are the tools', not the principal's, so **P4 cannot hold for a Run tool** and channel fidelity
replaces it. The Run profile carries it.

**Run profile** [A·CR]: ADR-0034 A2 (Batch 30; C2, C4). The same schema with `domain: run`, appraised at the same
rungs. P2 mounts nothing: an admitted `Consult` delivers its object over the channel. P4 is channel fidelity, held
by the tool host's Wasm runtime. P6 ends with the lease. A native Run tool is **D-0034-5** behind an egress filter
(a trust, no theorem voided) or **D-0034-6** without one (Run `Contained` voided: the reference before A8).
`RunConfinement.tla` checks and proves that every effect under a contained Run lease reached its tool's declared
target. No real Run principal is `Contained`: no guest passes P3 (item 1).

**Wasm tool host** [R]: the reference's Run tool host (`topak-contain` `wasmtool`, ADR-0033 A8): a core
Wasm module instantiated per call whose only imports are its inputs, its output, and `connect`/`send`/`recv` on its
declared target, which it cannot name; any other import is refused before it runs. The target comes from the
allowlist entry, per call (A9). Narrower than the component A2 names, because the build host has no WASI component
target (`mechanism/` I44).

**Finite in variants, not in instances** [A]: the floor is analysed per action variant over schema S with symbolic
parameters. It is not analysed by enumeration.

**Seat separation** [A]: for each artifact, the author and the voters are disjoint. A voter cannot `Draft`, `Invoke`
or `Submit`.

**Alphabets bounded by seat kind** [A·CR]: only a `thinker` seat is ever issued `Draft`, `Invoke`, `Submit` or
`Actuate`; an `observer` seat reads, emits and, on the veto roster, denies, and in Run holds `Consult` and `Report`;
a `grant` seat reads, emits and votes, and holds nothing in Run (ADR-0037 §4; ADR-0043 §2 for the Run column, which
ADR-0037 A1 made in force). Stated in the floor as **forbid B10** and a tightened **B6**, and checked by the grant
path first. Two kinds were added in Batch 34, both provisional: an `emergency` seat holds `Actuate`, `Consult` and
`Report` in Run and no authority act; an `operator` seat holds the six control actions and none of the others
(ADR-0037 A3, A4).

**Confinement obligation** [O, 1]: ADR-0022 §6. No shell, no egress, no filesystem outside the workspace and corpus,
and no path to the artifactory except `Submit`. §6 is the one section of ADR-0022 that is **not ratified**. The gap
it leaves is the **sandbox gap**, now in two halves: the design half is closed by ADR-0034, the mechanism half is
open, and every reference lease is rung 0.

**`Invoke` hermeticity** [O]: the per-allowlist-entry obligation that a tool opens no unnamed effect path. **One
allowlisted tool with a socket collapses the envelope to vacuity.** It is assumption of use A2, and it has no owner.
A Build entry's form is ADR-0049's too (ADR-0022 A3), and it carries no channel (W5).

**Capability cost** [D]: no shell, no package installation, no network and no git. This is not how agents write code
today, and the article has to say so first.

**Front door** [R]: the reference exposes the six variants as MCP tools and nothing else. That makes the alphabet
the whole **protocol**, not the whole **channel**: an agent with a shell never has to ask. For a guest the node
launches, the launcher's bridge is the channel and the protocol at once (ADR-0036 §2, ADR-0033 A7).

**Workflows.** The entries below are ADR-0054's and ADR-0055's, **both Proposed**, with the ten amendments ADR-0054
drafted into accepted records **pending**. Nothing here is in force; the reference follows it (ADR-0033 A16, A17).

**Workflow** [P]: a Build artifact, promoted like any other, that lets one cell's work reach another during Run: nodes,
a task template per node whose slots only a handle can fill, edges with guards and delivery modes, a join rule
(`any` or `all`) where edges meet, and a step bound and a time bound `T_wf` (ADR-0054 §1). Its kind is `dag`, the
default, acyclic and checked at load, or `mesh` (below). **Its promotion is the grant**: the quorum votes on the graph
and its seatings together, and the mechanism grants each node's lease when the node is reached, under that authority
(§2; ADR-0024 A4, ADR-0031 A4). No principal grants another.

**Node** [P]: one seating in a workflow; **one round of one cell**. In a mesh a node may run more than once, and each
run is an *activation*.

**Edge** · **computed** · **chosen** [P]: a **computed** edge fires when its guard holds, evaluated by the mechanism in
the apply that made it evaluable, with no gap between deciding and applying. A **chosen** edge is selected by the
orchestrator from a decision point, among edges whose guards already hold. Each edge declares a delivery mode,
`clear` or `handle`, for the source's output.

**Guard** [P]: a predicate in a fixed, decidable language: equality and membership over enums and labels, bounded
counts against constants, and the connectives; no strings, arithmetic or temporal operator. **The mechanism evaluates
it; it is not policy**, so it is re-run at apply. It reads only what is settled: in a DAG, the attributes of the edge's
source and of the nodes that dominate it; in a mesh, the triggering activation and its causal history, never a node's
latest value.

**Attributes** (of a node) [P]: lifted by the mechanism once, when a node's round ends: `end`, `actuates`, `label` (the
worker's `clearSet` at its seal), `covered`, `found`, a declared `outcome` from the node's closed enum, and `output`, a
handle. **None is a literal.** All are written once except `found`, which moves only from false to true, so a guard
can change only towards disabled. A denial count was dropped: a denial is never ordered, so no replica holds a count
every replica agrees on (ADR-0054 R6). **Policy reads none of them**: a guard is a mechanism check. They are not the
attributes of a call that policy reads (*clear set*, above), though the rule that only the mechanism computes them is
the same (ADR-0047 R13).

**Decision point** · **decision event** [P]: a node with more than one chosen outgoing edge. In a mesh the end of an
activation at such a node is a **decision event**. One route consumes it.

**Orchestrator** [P]: a sixth seat kind, Run only (ADR-0037 A5): alphabet `Route` and `Report`, coupled to an
Observer as a Thinker is (ADR-0039 A3), delivered handles and never bytes, and seated only when the graph has a chosen
edge. **It may only narrow**: it cannot enable an edge, so every safety property holds whichever enabled edge it takes.
One round per decision point or event; in a mesh it holds nothing between rounds. A Byzantine orchestrator can stall
a workflow and cannot misroute it. Not ADR-0008's "orchestrator-level Observer group" (§13).

**`Route(edge)`** · **route** [P]: the orchestrator's variant (ADR-0040 A2), classed as an emission (ADR-0015 A1).
Checked at decide and **again at apply**, and void if it fails there, so a finding ordered between the two is not
overtaken. One per decision point; a second is void. It carries its **basis**, the log index of what the orchestrator
was shown. A lapsed orchestrator takes no default edge.

**`input`** [P]: a fifth item of Run's ingress (ADR-0043 A3): a predecessor's output, delivered along an edge, labelled
with the reporting worker's `clearSet`. Delivered clear it joins the receiver's `clearSet`, so **R5 to R7 follow
content from cell to cell** along the workflow.

**Routing rule** [P]: an edge whose target can reach an outward entry, or receives `restricted` input, is disabled when
any attribute its guard reads is labelled `untrusted` (ADR-0054 §5; ADR-0047 A1).

**Lineage alternation** [P]: the Thinkers at the two ends of every clear edge are independent under ADR-0035, checked
at the tally. A handle edge carries no bytes and is not checked. In a mesh the clear edges must be 2-colourable. While
ADR-0035 is Proposed, every deployment declares it instead (**D-0054-1**).

**Coverage at the edge** [P]: an edge is enabled only once its source's cell Observer has read it to the seal, so a
finding from that Observer lands before any successor runs. It does not close the race the re-check at apply closes.
Waiving it is **D-0054-2**.

**Mesh** · **budget** [P]: a workflow of kind `mesh` may have cycles, for a loop whose number of turns is decided at run
time (ADR-0055). It loads only with an **activation budget**: a bound `N` on the leases the promotion may ever issue,
the orchestrator's included, with an optional bound per node. A grant the budget cannot pay is refused, and running
out fails the workflow. **A budgeted mesh is a DAG unrolled to depth `N`**, which is what lets ADR-0054's argument
apply to it. Not the timing budget `W + L + D < T_irrev` (§8; §13).

**Activation** (of a node) [P]: a pair (node, *k*), one round of one cell in a mesh, the unit of attributes, routes and
findings. One live activation per node. Not an emergency seating's activation (§5; §13).

**Trigger** · **causal history** [P]: an activation's trigger is the activation it was entered from, or the fan-out it
belongs to; its causal history is itself and its trigger's history, recorded by the log. **A finding against any
activation in a history closes every edge downstream of it.**

**Track** [P]: what the mechanism delivers to an orchestrator's round in a mesh: the activation history that bears on
the event, as typed facts with labels and handles, written as the round's opening record. **The mechanism tracks; the
orchestrator holds no state**, because a long-lived one would need successor grants, would be persistent agent memory,
and would route onto the wrong activation.

**Completion** [P]: every sink of a DAG ended or skipped, or an activation of a mesh's sink ended. It says the graph was
traversed, **not that the work is right**. A timeout, an exhausted budget or a quiescent mesh is a failure.

**Choreography** [P/D]: cells reacting to each other's events with no one deciding what runs next. **Not supported.**
"Event-driven" in TOPAK means the mechanism is the bus: the events are log entries, and Kafka orders nothing (ADR-0055
§7).

---

## 3. The lease

**Lease** [A·CR]: **one composite credential, granted for one round, with a closed schema** of twelve fields:
principal, seat, Persona, epoch, fence, rules epoch, bundle, confinement, alphabet, round, role and TTL (ADR-0031).
A capability that is not a field is not carried.

**One live lease** [A·CR]: a principal holds at most one live lease, and a grant requires that none is live. Without
this rule, monotone renewal guarantees nothing.

**Round-coterminous** [A·CR]: a lease lives exactly as long as its round.

**Fence** [A·CR]: the Paxos log index at grant. Leases, admits and issuances are ordered by one log.

**Renewal only narrows** [A·CR]: a renewal may narrow the alphabet or shorten the TTL. It keeps the bundle, the
round, the role and, since ADR-0031 A1, **the confinement digest and rung**; changing any of them needs a grant. A
renewal that lowered the rung was a silent downgrade reachable through the renewal path, and the records never met
in a check until `Confinement.tla` modeled renewal. So **tightening a live round ends it.**

**Cross-round coverage** [A·CR]: in Run, a Thinker's lease for round *r+1* is granted only once a cell Observer has
read round *r* to its seal (ADR-0039 §2). Build needs no cross-round rule, because its only egress is promotion.

**Targeted revocation** [A·CR]: ends the leases that match a principal, a Persona or a confinement profile, and bars
later grants to it. Nothing else stops. Under X1 it also lapsed the seat's break-glass approvals, which was the C1
marker; there are no approvals to lapse now, and an emergency lease ends as any lease does. Since ADR-0031 A3
(provisional) it is an operator's signed act (§5).

**Epoch fence** [A]: ends every live round. It is kept for e-stop and for scopes nobody can name. After an epoch
increment, prior-epoch actions are rejected by the mechanism, not by policy. As a control action, `FenceEpoch`, it
is the one deny that needs a live lease (§5).

**Revocation is permanent within the chain** [A·CR]. **Lifting a revocation** [O, 22] adds authority, and no record
says who may do it.

**Expiry is local, then ordered** [A·CR]: a replica reads its own monotonic clock with a margin that errs early. The
first replica to see expiry proposes the round's end as a log entry (ADR-0031 E1).

**Per-round TCB** [A·CR]: the field list. Persona, confinement, bundle, alphabet, round and role are checked at grant
and assumed for the round. Epoch, fence and rules epoch are compared on every action. It is the one slice of the
trusted base that is derived rather than declared; the rest is ADR-0045's table (§9).

**`T_persona`** [A·CR]: the bound on a lease's `ttl`, at grant and at every renewal, so the Persona is re-attested at
least that often (ADR-0031 A2, Batch 17). A policy-floor value, placeholder one hour, read by the reference since
ADR-0033 A6 (Batch 23) and refused at apply like every mechanism condition. It bounds the declared value; expiry runs on the local clock, so the interval it bounds is `T_persona` plus drift
(ADR-0045 finding 2).

---

## 4. Policy and the floors

**Syntactic lift** [A]: mechanical, total extraction of a field from a constrained call interface. It is the only
way a field may enter the admit path.

**Semantic lift** [A]: a model's judgment entering the admit path. It is **prohibited** (ADR-0007). A classifier's
output enters only as an Observer finding, and findings subtract authority.

**Verified object** [A]: the enforcement mechanism, its version pinning, its epoch fencing, a minimal policy floor
and a minimal rules floor (ADR-0010, A1). Everything else is a versioned parameter.

**Policy floor** [A·CR]: the minimal, default-deny floor inside the verified object. Containment is checked against
it.

**Composition** [A·CR]: **admit ⟺ floor_permit ∧ ¬bundle_deny**, over one frozen input (ADR-0030 §1).
`floor_permit` requires Allow **with no evaluation error**. `bundle_deny` holds unless the bundle affirmatively
allows, so a deny, an error, an undefined result, an absent bundle and an unreachable bundle all refuse. **A bundle
is never asked whether to grant.**

**`bundle ⊑ floor`** [A·CR]: now a **property of composition**, not of the bundle. It holds for every bundle at every
age, so nobody decides it at promotion.

**Monotone-safe staleness** [D]: a stale bundle is bounded below by the floor at any age, with no refinement premise.
The lease argument has the same shape.

**Bundle revision binding** [A·CR]: a bundle decision counts only from the revision the lease names. A local
fallback engine decides only when it holds that revision. Otherwise the bundle is unreachable and refuses. **Bundle
fail-closed protects narrowings, not the floor.**

**Deny reason** [A·CR]: a floor deny names the forbids that fired, or ***no permit matched***.

**Verified evaluator** [A·CR]: the floor tier's obligation is a mechanized semantics, an implementation checked
against it, and a decidable comparison of two policy sets. Cedar meets it and Rego does not. The floor is **linked
into the mechanism as a library**, with no process, socket or fetch.

**Schema S** [A·CR / P]: the typed lift's type, enforced on every request. The analyses quantify over it. The
genesis `genesis.cedarschema` is DRAFT. The floor in force's schema is the `emergency` stage's
(`floor/proposed/emergency.cedarschema`), which adds the label attributes (ADR-0030 A2), the six control actions and
the two seat kinds. The schema the reference links since 2026.10.08 is the `workflow` stage's, which adds `Route`,
the `orchestrator` kind and the lease's decision point [P].

**Nothing translates** [A·CR]: there is no Rego → Cedar transpiler, in either direction, in the archetype.

**The gates** [A·CR]: **totality** (never-errors), **non-vacuity** (not always-allows), **discrimination** (not
always-denies), per action over S. The genesis floor also runs **every-entry-matters** and **routing**. A failing
gate returns a counterexample request. The gates are decidable checks on the floor (ADR-0030 §5).

**Floor fitness** [O, 2 · 87]: the missing gate (NIST MEASURE 2.13). The gates show that a floor is well formed and
not vacuous. They do not show that it is *right*. **Owned and timed since Batch 34, with no test**: the bootstrap
reviewer establishes it, and the floor is ratified with that (ADR-0029 A4; ADR-0030 A3). What makes a floor fit is
written nowhere.

**Genesis-provisional** [A·CR]: the policy floor's status (ADR-0030 A3). No batch ratified a floor text: ADR-0030
ratified the language and the machinery. The entries are named by text in force and gated, and the floor itself is
ratified when the bootstrap reviewer establishes that it is fit (ADR-0029 §5, step 6). Not the same word as a
*provisional* record (§9; §13).

**Genesis floor** [P, 25]: `floor/genesis-floor.cedar`, 16 Cedar policies, schema S and the values file, gated
five times, last on 2026.09.30. It is **DRAFT**, and since 2026.10.05 it is no longer the text the reference
links: it is what the stages are built from.

**Floor stages** [P / R]: four texts built from the genesis floor, each validated, tested and gated: `labels` (20
policies, 74 cases), `control` (29, 106) and `emergency` (28, 107) on 2026.10.04, and `workflow` (30, 123) on
2026.10.08. **The `emergency` stage, `floor/proposed/emergency-floor.cedar`, is the floor in force**: the text whose
entries the records in force name, and the one that is genesis-provisional. **The `workflow` stage is what the
reference links since 2026.10.08**, at the custodian's direction: `Route`, `R8-route-own-decision`,
`R9-only-orchestrators-route` and `R3` widened to the `orchestrator` kind, Proposed with ADR-0054 (ADR-0041 A4,
pending). Each stage opens with a comment that is wrong, "not what the reference follows", false of whichever stage
the reference links; the bytes are kept as gated so the digests the records cite are the ones the reference pins
(item 91).

**The floor stated in Lean** [A·CR]: `floor/lean/`, the genesis floor, the floor in force and the linked stage in
cedar-spec's abstract syntax, generated from their files, with their gates proved in Lean under the model: each
validates against S, so by cedar-spec's proved soundness never errors on a conforming request; neither always allows
nor always denies; and every test case is decided as it says (ADR-0053 §1; ADR-0030 B36). The totality claim then rests
on the model's validator and T-0045-3, not on cedar's folding. **It ratifies nothing**, and it is not floor fitness.

**Values file** [P]: `floor/genesis-values.json`, the third file of the floor bundle: the numbers the typed lift
reads that Cedar text cannot hold, `K`, `T_obs`, `T_persona` and ADR-0035's unset θ (ADR-0039 §1; ADR-0031 A2). Relaxing a value is an
issuance and a promotion. **Every number in it is a placeholder**, a deployment or rung choice, and the file says so.

**Forbid B7** [P]: the recusal forbid in the genesis floor. Recusal is floor text, so **relaxing it is a policy-floor
relaxation** (ADR-0022 A1).

**Forbid B10** · **B6** [P]: only a `thinker` seat authors, in either domain; a vote is permitted from the grant
roster only for a `grant` seat and from the veto roster only for an `observer` seat (ADR-0037 §4).

**Forbid R3** [P]: `R3-observer-live`. An `Actuate` or `Report` under a `thinker` seat is refused when no cell
Observer is live (ADR-0039 §2 as amended by A1; ADR-0041 §1). It is a Thinker's rule: **an `emergency` seat is not
coupled** (ADR-0039 A2, provisional), where under X1 the rule covered break-glass too. It does **not** name
`Consult`: a read of pinned content adds nothing to the backlog and can be reconstructed later from its digest
(ADR-0041 §2). An observer seat's own emissions, its heartbeats among them, are not coupled.

**Permit R4** [P]: `R4-consult-pinned`. A `Consult` is permitted when the seat's domain is `run`, the lease's
alphabet contains it, and the object is in the Run root (ADR-0041 §1). The exemption from R3 rests on the pinning,
and the gate run carries a control for it: R4 without its root condition is classed a relaxation by routing.

**Forbids R5, R6, R7** [A·CR]: the floor's minimum over labels, on an `Actuate` of an outward entry (ADR-0047 §7;
ADR-0041 A1). **`R5-no-read-then-send`**: refused when `clearSet` holds `untrusted` and `restricted` is in `clearSet`
or in a handle among the inputs. **`R6-no-steered-destination`**: `clearSet` holds `untrusted` and a destination
input is a literal. **`R7-no-replayed-destination`**: a destination input is a handle whose label holds `untrusted`.
All three are monotone in `clearSet`, so **delivering more in the clear buys a narrower round**; a bundle may move
every label to `clear` and cannot escape them. `Labels.tla` shows each needed alone. They are not the rules-floor
entries of the same names (§13).

**Control entries C1–C9** [A·Pv]: nine floor entries stating the envelope of an `operator` seat's six actions
(ADR-0041 A3; ADR-0050 §4), gated like any entry. They are not the confirmation criteria C1 to C4 (§13).

**Checked routing verdict** [A·CR]: ADR-0030 A1, ratified 2026.10.01 (Batch 24). A `holds` answer to `F′ ⇒ F` or
`F ⇒ F′` is an UNSAT result from the solver, and a wrong one lets a relaxation pass by promotion alone; under A1 a
`holds` verdict counts only with the query, the solver's proof and a pinned checker's acceptance, their digests in
the gate evidence. A `refuted` verdict needs none, since it can only subtract. The wrapper is `floor/cvc5-checked`
and the checker `ethos`, checking cvc5's CPC proofs against the signature in `tools/cpc/`; a `holds°` is one cedar
decided without a solver query and rests on the engine's row. A gate run without the checker is **D-0030-2**,
routing verdicts unchecked, whose subtractive mitigation is to make every floor change two-key; every run before
2026.10.01 was one.

**Evidence tree** [C]: the queries, bound proofs and verdicts of a gate run, copied beside its results file
(`floor/genesis-gates-evidence-<date>/`), with the tree's digest printed at the end of the results; that digest is
what joins the gate-evidence digest. A verdict names the query, proof, solver and checker digests. The first is the
2026.10.01 run's, reproducible run to run.

**Bundle signing** · **bundle key** [A·CR]: a bundle is trusted by its signature, not its file name (ADR-0044, Batch
17, C1). The bundle key is carried in the issued rules (ADR-0025 §1 (f)); the signature covers the content revision;
the mechanism loads a bundle only when it verifies, counts a sidecar's decision only from a verified revision, and
refuses a grant naming an unverified one; signing happens at promotion. Implemented at the reference since ADR-0033
A6 (Batch 23) under a dev key with custody (1, 0) (`mechanism/` I34); **D-0044-1** was the reference's position before
2026.10.01, and signing at promotion is a script step until a promotion pipeline exists (item 67).

**Floor-change routing** [A·CR]: the classification is **computed, not asserted**. The analyzer decides `F′ ⇒ F`
and `F ⇒ F′`:

| Change | Authority |
|---|---|
| Tighten the policy floor | An ordinary promotion |
| Relax it, or add an exception | Anchor issuance **and** promotion |
| **Incomparable** revision | Routed as a relaxation |
| Any rules-floor change, either direction | Anchor issuance **and** promotion |

**Resident floor** [A]: the default-deny floor is pre-blessed, staged and instantiated rather than fetched, so fail-closed
works at cold start (ADR-0012).

**Vacuous floor** [D]: a floor that admits everything and discharges every property over nothing, invisibly. This
is why the gates run on the floor.

**Rules floor** [A]: the verified bound on the trust anchor (ADR-0026). The mechanism rejects any issuance that
violates it.

| Entry | Bound | State |
|---|---|---|
| R1 | `quorum = "all"` over counted grant seats | In force |
| R2 | `minGrant ≥ 2` | In force |
| R3 | Recusal | **Withdrawn**: enforced by the `Vote` envelope, so there is no issued value to bound |
| R4 | A timeout never grants | **Withdrawn**: now a mechanism constant |
| R5 | No key both in the anchor key set and on the promotion roster | In force |
| R6 | Exception-count bound; **the count it bounds is one** | In force; the count by ADR-0026 A2 (provisional) |
| R7 | No activation of an emergency seating grants a lease whose alphabet holds an authority act | In force, **restated** by ADR-0026 A2 (provisional). With the `emergency` kind's alphabet as decided it has nothing to refuse |
| R8 | Break-glass grant TTL | **Withdrawn** (ADR-0026 W1, 2026.10.04): a break-glass grant ends with its round |
| R9 | `quorum = "all"` or `quorum ≥ 2` | In force. A **conditional entry** that binds only once R1 is relaxed |

`RulesFloorBase.tla` has not caught up with ADR-0026 A2: it still carries `bgScope` and a bound of two (item 90).
The rules gained three issued things the rules floor does not bound: an identity provider's key and the two lists
the load checks read (ADR-0025 A2, A3).

**Parametricity** [A]: a floor entry bounds a value only if the mechanism reads it from issued rules. **Converse:**
a value fixed as a constant cannot be bounded by an entry. Checked by `RulesFloorNV` and `RulesFloorNV_rev5`.

**Empty-roster promotion** [A]: without R2, a havoc issuance sets an empty roster, unanimity over the empty set is
vacuously true, and an artifact promotes with **zero votes**.

**Floor exception** [A·CR]: a carve-out for a path that cannot be written as a subtraction. **There is one:
erasure** (ADR-0013 as amended by A1). Until Batch 34 there were two; the other, **X1, break-glass**, is retired on
a provisional record (ADR-0052; ADR-0041 A2), and an emergency seat's calls are admitted by the ordinary allowlist
permit. An exception is a Cedar policy inside the floor, so a bundle can narrow it and nothing can widen it.

**Break-glass** [A·Pv]: the privileged path that adds authority in an emergency (ADR-0009). **Since ADR-0052 it is
an emergency seating** (§5) and no floor exception: a person, one round, an ordinary allowlist. The roster and its
quorum are unchanged. If ADR-0052 is redesigned, break-glass has no settled form until the redesign is ratified.

**Non-composition** [A·CR]: **NC-1**: break-glass chained with erasure never yields an effect that is authorized,
erased and unattributable. **NC-2**: erasure never removes a forensic-floor record. Both were checked on
2026.09.23, with a witness that the composition is reachable, and restated for the seating on 2026.10.05 in
`NonComposition_A1.tla`, proved and certified. A third mutation breaks both: an activation's record kept only while
its round is live.

**Per-class floors** [O, 9]: whether Build and Run share one floor or each have one over a shared core. Cedar can
state either answer, and ADR-0030 does not choose. ADR-0014 is reserved for it.

---

## 5. Authority

**Promotion** [A]: the crossing from Build to Run, for bundles, mechanism releases (floor changes included) and
Personas. **Promotion is a quorum grant** read from issued rules (ADR-0024). **A promotion is a round**, keyed by
artifact digest.

**`quorum`** [A]: either `"all"` or a grant-vote threshold *k*. The archetype value is `"all"`. The value `"any"` is
**withdrawn**: it is *k* = 1.

**Grant seat** / **veto seat** [A]: a grant seat is held by a human `Mediated` principal with a named role. A veto
seat is held by **every cell Observer and every correlator in Build** (ADR-0024 A2.1, from ADR-0038 §6) and its
alphabet lacks `grant`. **Veto-seat silence is not a veto**, but **an absent Observer stalls**: a promotion completes
only if a veto seat independent of the author was leased for the round (A2.2) and the author's cell Observer reported
coverage to the seal (A2.3). Both are mechanism constants in the tally, as recusal is. A2.2 is unbuilt in the
reference (`mechanism/` G18).

**Coverage** [A·CR]: a cell Observer's watermark at or beyond the seal of the watched round (ADR-0039 §3). A fact, not
a "no finding" attestation.

**A timeout is never a grant** [A]: a mechanism constant.

**Vote binding** [A]: a vote binds to (artifact digest, gate-evidence digest, rules epoch). A change of rules epoch
voids in-flight votes.

**Gates enable voting; they do not vote** [A].

**Recusal** [A]: a **mechanism constant**. The author is removed from the counted seats, and the `Vote` envelope
refuses the author's vote. If too few seats remain, promotion is denied.

**Runtime subtraction is not promotion** [A]: e-stop, expiry, revocation and `deny=all` need no quorum. They are still
**ordered** wherever they change replicated state.

**Trust anchor** [A]: the authority that defines who votes. It is modeled as a **havoc issuer**: safety holds for
every issuance it could make (ADR-0025).

**Issuance** / **`Issue`** / **`Resign`** [A]: the anchor's actions. They are environment events that no Build
principal can express. `Resign` is defined per custody rung in the ADR-0025 annex. At archetype custody it freezes
the rules. On a threshold rung the recovery rule rotates the key. Under n−1 eviction it consumes that epoch's single
eviction.

**The intent axiom** [A]: the sole axiom. *An authentic issuance at the current anchor epoch is what the anchor
intended.*

**Infallible, split three ways** [A]: **intent** is assumed, **integrity** is modeled, **custody** is declared.

**Rules** [A]: the promotion roster and its parameters, the break-glass and erasure rosters, the anchor key set, any
relaxation of the policy floor or new exception, and **any change to the rules floor in either direction**. Also
issued: the keys that vouch (the bundle key, the verifier's, and since ADR-0025 A3 an operator's identity
provider's), the seat declarations, and the two lists a bundle's load checks read (ADR-0025 A2; §2).

**Custody** [A]: the declared pair (capture threshold, loss tolerance).

| Record | Model | (capture, loss) |
|---|---|---|
| A-0025 | Strict unanimity, n ≥ 3 (the archetype) | (n, 0) |
| D-0025-2 | n−1 eviction with replacement | (n−1, 1) |
| D-0025-1 | Threshold with recovery, in the shape of the TUF root role | (k, n−k) |
| — | Single custodian: the corpus today | (1, 0) |

**Loss freezes the rules** [A]: at archetype custody the system runs and subtracts but cannot change. The only exit
is **re-genesis**.

**Anchor capture** [A]: the headline residual. A coalition at the capture threshold can issue any
rules-floor-conformant roster. **No safety theorem covers anchor intent.**

**Two keys, both directions** [A]: a rules-floor change needs an issuance and a promotion, even to tighten.

**Genesis rules** [A]: they ship with the mechanism release and are fetched from nowhere (ADR-0027). Epoch 0 is the
root of the rules-epoch chain. The epoch-0 floor check is the `GenesisSatisfiesFloor` invariant, not a promotion.

**Privileged grant** [A]: a quorum on an anchor-issued roster, bounded by the rules floor. Ordinary Run admits are
grants too, but they are decided against a bundle, not a roster.

**Operator** [A·Pv]: a principal holding a seat of kind **`operator`**, declared in the issued rules with a domain
(ADR-0050 §1; CR-34). Only a person holds one; a person who operates and also votes is two principals. An operator
is `Mediated` and is treated as havoc: nothing rests on its honesty. Before ADR-0050 the operator was whoever could
reach a socket, the one authority with no model. At the archetype a domain has **at least three**, vouched for by
independent providers; two is **D-0050-3** and one provider behind the peers is **D-0050-2**.

**Seating** [A·Pv]: the act of record that puts a principal on a seat: the principal, its Persona, its confinement,
the bundle revision and what bounds its tasks' labels (ADR-0050 §2). A seating is made by a quorum: a promotion
(ADR-0024 A3) or, for the first operators and the rostered seats, an anchor issuance (ADR-0025 A3). **Not built at
the reference**, where the BOOTSTRAP path seats (below; item 88).

**First lease** · **successor grant** [A·Pv]: a principal's first lease is granted by the mechanism when a quorum
completes. A **successor grant** is its next round, every field the last lease's or narrower, and is one operator's
act, as a renewal is (ADR-0050 §2; ADR-0031 A3). An operator can keep a quorum's grant going and can narrow it;
anything wider is a first lease. So the quorum acts once per seating and round by round one operator acts.

**Control alphabet** [A·Pv]: an operator's six actions, in schema S, decided by `C1` to `C9` (ADR-0050 §4). Three
**add**: `Regrant`, `Renew` and `AttestGates`, each needing a live lease and a **live peer**. Three **deny**:
`EndRound` and `Revoke`, needing a Persona in force and a live lease *or a fresh sign-on*, in the operator's own
domain; and `FenceEpoch`, needing a Persona in force *and* a live lease. **A deny needs no lease**, and a key by
itself is not a standing lever.

**Live peer** [A·Pv]: another operator in the domain holding a live lease (ADR-0050 §6). An add couples to a peer's
presence, the coupling rule's shape applied to people, and not to anything the peer has read. Every control action
is written to the operator's round topic and read by the domain's other operators; a finding is a deny.

**Sign-on assertion** · **identity provider** [A·Pv]: an operator's Persona binds a key, and its lineage's root is
the identity provider that vouches for the person (ADR-0050 §3; ADR-0016 A1). At a lease boundary, and for a deny
with no lease, the provider signs an assertion naming the key and **the fence the mechanism asked it to name**; no
wall clock is read. The provider's key is issued. The provider is a trust root, T-0045-35, and the operator's
custody of its key is T-0045-36.

**Task record** [A·Pv]: a seating and a `Regrant` carry the round's task: its digest and label on the log, its bytes
in the round's payload, which at the reference is the opening record's (ADR-0050 §5; ADR-0043 A2). The label is the operator's signed declaration, bounded by
the seating. The reference carries no task at a first seating (item 94).

**BOOTSTRAP path** [R / C]: the reference's unsigned operator socket, kept and marked: it seats and does nothing
else (ADR-0033 A11; `mechanism/` I47). It stands in for the quorum that should make a first lease, so at the
reference whoever reaches it can seat. That is **D-0050-1** for that one step, and it is why ADR-0050 is
provisional.

**Emergency seat** [A·Pv]: a seat of kind **`emergency`**, Run only, held by a person with a key and by nobody else
in the round (ADR-0052 §1; ADR-0037 A3). Every action under its lease is signed with that key. No model's Persona
binds to the kind (ADR-0016 A2). The mechanism cannot tell a person from a program holding the person's key.

**Emergency seating** · **envelope** [A·Pv]: a seating prepared in advance for the emergency kind, with its envelope:
by default **the domain's**, every Run allowlist entry in force, computed at activation so it cannot go stale,
together with emergency-only tools promoted ahead of time (ADR-0052 §2). The envelope is an ordinary allowlist, which
is why the floor needs no exception, and the label forbids apply under it. Preparing one by promotion is not built
(item 92).

**Activation** [A·Pv]: the break-glass roster's quorum activating an emergency seating: **one lease, for one named
person and one round**, with the round's task (ADR-0052 §2, §3). It ends with its round, with no successor and no
renewal; another round is another quorum. The activation is a forensic-floor record (F5): who approved, whom, which
seating, which round, what task. **The reason is not recorded**: it is a claim about the world. Not a mesh's
activation of a node (§2; §13).

**Drill** [A·Pv]: a real activation, by the real roster, of a seating whose envelope holds one inert tool
(ADR-0052 §6). An obligation with evidence; it gates nothing, and nothing at the reference counts it (item 92).

**Consensus for grants, local for denials** [D]: the organizing rule.

**Monotonicity, layer by layer** [D]: now sixteen layers (ToO §7.8):

| Layer | Statement |
|---|---|
| Decision | Consensus for grants, local for denials |
| Policy | Bundles only subtract, by composition |
| Change | Increases need consensus. Decreases need no quorum, but are ordered when they change state |
| Deployment | Degenerate forms lose theorems, never gain capability |
| Authority | Relaxing the rules needs the anchor |
| Evidence | Authority facts survive erasure and break-glass |
| Credential | Renewal only narrows, and keeps the rung |
| Confinement | A principal below the declared rung is refused, never granted lower |
| Lineage | The projection over-approximates, and adding to it can only fail a pair |
| Time | Intervals that subtract may use a local clock. Intervals that preserve authority need trusted time |
| Seat | Only a thinker seat is issued a variant that writes, runs or offers |
| Detection | Observers combine by any-of, and coupling only refuses: more Observers never lower safety |
| Bundle | A bundle loads only under an issued key's signature |
| Trusted base | A component enters only if its failure can only subtract, or its identity is issued |
| Ingress | Suppression only subtracts, and the label forbids are monotone in what was read |
| Operation | A quorum seats; one operator keeps a quorum's grant going and may narrow it, never widen it (provisional) |

At the pattern level it **inverts**: tightening the archetype puts every deployment into declaration debt, and
relaxing it voids published theorems.

---

## 6. The record

**Effects** [A·CR]: exactly {tool invocation, principal emission}. **Authority changes**: exactly {promotion,
anchor issuance} (ADR-0015). The qualifier that keeps the second set at two is ***change to the rules in force***.
Erasure is an admit decision against its exception entry, so it is an effect; an activation of an emergency seating
is a grant by a roster's quorum, and what the person then does is ordinary effects under a lease.

**The admit decision is the orderable event** [A·CR]: not the emission.

**Audit chain** [A·CR]: effect → admit → floor ∧ bundle at the lease's revision → rules epoch → issuance → intent
axiom. No link is assumed except the last.

**Decide, order, re-check** [A]: deciding and ordering are separated in time (ADR-0033 §4). The mechanism checks run
before the floor and again at apply time. An admit that fails the second run is **void**: ordered, recorded and
without effect. The floor and bundle are not re-run. The effect runs only after commit.

**Ordering is not authorization** [A]: subtractions need no quorum, but they must be ordered if they change
replicated state.

**Denials are recorded, not ordered** [A]: a denial is written unordered to the principal's round topic, as digests,
by the replica that decided it (ADR-0020). Without denials, the trail cannot tell *behaved* from *was prevented*.

**Effect exclusivity** [A·CR]: the principal reaches the world only through the alphabet. ADR-0015 makes it a
mechanism claim, which is **identical in strength to Moon & Varshney's assumed version until ADR-0022 §6 is
discharged** (ADR-0015 E2).

**Kafka's role** [A·CR]: neither the ordering authority nor the system of record. It is a transport with a durability
window (ADR-0005, ratified 2026.10.04, Batch 27, C4). An emission is written after commit and carries the admit's
log index, the fence and a per-lease sequence number. The ratification discharges the debt ADR-0033 §2's K row had
carried since Batch 7.

**Round** [A]: in Run, a cycle of principal activity (ADR-0003), ending when its lease ends (ADR-0042 §5). In Build,
one pipeline invocation (ADR-0021, Batch 18).

**Opening record** [A·CR]: the first record of a Run round's topic, written by the mechanism at grant, before the
session exists: the tool list the principal was given, and the task (ADR-0042 A1; ADR-0048 §2). It has no admit
and no sequence number.

**Topic per principal per round** [A]: sealed on emit completion, with per-topic ACLs, per-use-case retention,
explicit replay authorization, write-time masking and no tiered storage. **The topic is the unit of erasure.**
Since A3 (Batch 17) "no tiered storage" means one store for a topic's whole retention, never a retention length,
which is per use and per domain, and the archive is not a tier.

**Topic identity includes the rules-epoch chain** [A]: so a successor system never writes to a predecessor's sealed
topic (ADR-0003 A1).

**`after` companion topic** [A·CR]: one per round. It holds denials only, for attempts made under the round's lease
after its topic is sealed. It is bounded by a limit marker and erased with the round (ADR-0003 A2, the only
confirmation marker scoped to one amendment).

**Control-plane facts vs cognitive payloads** [A]: the archive keeps a hash and a pointer. Plaintext lives in a
separately governed store built for deletion (ADR-0004). A **heartbeat** is a fact and enters the log verbatim; a
Thinker's **raw emission** is payload.

**Raw emission retention** [A·CR]: at the archetype, the Thinker's raw emission is written to its round topic beside
the typed action it decoded to, under the same ACL and erasure unit, for one purpose: re-run the decoder and compare
(ADR-0037 §3). It recovers **decoder faithfulness**, never intent. Optional below the archetype: **D-0037-2**.

**Erasure** [A·CR]: a modeled event that is consensus-ordered and recorded in the log it modifies. Its authorization
lives in the verified object. **Genesis rules issue no erasure roster**, so erasure is disabled from epoch 0.

**Crypto-shredding** [A, rejected]: it leaves a verifying envelope over unreadable ciphertext, which no auditor can
tell from suppression.

**Replay** [A]: reconstructs what crossed the membrane, including refused attempts (ADR-0020). The Observer and
replay read the same stream.

**Legibility** [A·CR]: replaces "immutable". *Every admitted boundary event remains readable by the declared audit
authority for the declared horizon.* Compartmentation subtracts the reader set, and it is not erasure.

**Forensic floor** [A·CR]: six classes that cannot be erased for the horizon: **F1** admit decisions · **F2** stop
attribution · **F3** promotion votes · **F4** anchor issuances · **F5** break-glass invocations, which since ADR-0052
are activations · **F6** erasure events (ADR-0028). Each class is a floor denial on the erasure envelope. No cognitive payload is in the floor.

**Where a vote lives** [A]: the authoritative vote is the admit decision in the consensus log, which F3 retains. The
round-topic emission carries a pointer to its commentary, and erasure removes only the commentary.

**Demand type 5** [A·CR]: "hide that a record existed". It is **declined**, because it conflicts with NC-2 and F6.

**Forensic horizon seam** [O, 10]: the horizon is the rules-epoch chain, and re-genesis starts a new chain. The
successor's read access is carried as a re-genesis migration obligation.

---

## 7. Detection and the model

**Observer** [A]: the detection layer. Every finding is **deny-only**. Since ADR-0037 an Observer is an `observer`
**seat**: a principal with its own lease, Persona and topic, evictable alone.

**LTRO** [A·CR]: Listener / Thinker / Reader / Observer. **Not a principal**: a cell of principals (§2), in which the
Thinker and the Observer are seats and the Listener and the Reader are stages (ADR-0037 §2).

**Seat** [A]: a slot declared in the issued rules, held by one principal, with a **kind**. The binding point for a
Persona and the unit of attestation and attribution. Two senses meet here: the LTRO position (ADR-0016) and the
promotion-roster slot (ADR-0024); the kind separates them.

**Seat kind** [A·CR]: `thinker`, `observer` or `grant` (ADR-0037 §2), and since Batch 34, provisionally,
**`emergency`** and **`operator`** (ADR-0037 A3, A4; §5). Fixed at declaration; bounds the alphabet a grant may
issue (§2); carried into schema S. The last two are held only by a person. A sixth, **`orchestrator`**, is pending
with ADR-0054 [P] (ADR-0037 A5). ADR-0053 finding 8: an issuance may change a seat's kind at the reference, which
`rules::validate_issuance` does not refuse, and whether it should is ADR-0037's question (item 106).

**Stage** [A·CR]: a position in the cell that holds no Persona and no lease: the **Listener**, which delivers the task
and the admitted `Read`s and makes no choice, and the **Reader**.

**Listener** [A·CR]: in Run it delivers four items: the task, consulted content, tool results and the tool list. It
**labels** each from its source and delivers it clear or as a handle by the bundle's table (ADR-0037 A2; ADR-0043
A1; ADR-0047 §2). It still makes no choice: the label is a lookup and the mode is a table. The label computation
and delivery are trusted-base row T-0045-32; the declarations they read are T-0045-33, excluded.

**Reader** [A·CR]: a check, not a seat. Its two admissible uses (ADR-0019) produce **facts** the cell Observer
consumes: decoding conformance, which may admit only at a rung that attests inference and until then may only deny,
and substitution detection, whose threshold is the Observer's (ADR-0037 §3). The interpretation ADR-0018 gave it is
not kept. It runs beside the Thinker, inside the guest at rung ≥ 1, so everything it produces is the guest's own
report. Logprobs are monitored and not retained.

**Who forms the emission** [A·CR]: the Thinker's Persona, weights and decoder together; the mechanism's validator
admits it. The Reader was never in that chain (ADR-0037 §3, ADR-0018).

**Cell Observer** · **correlator** [A·CR]: the archetype has **one `observer` seat per cell** watching its Thinker,
plus a **correlator**, an `observer` seat with no cell that watches every cell in its domain (ADR-0038 §1). The
correlator is ADR-0008's shared group under a new name and a narrower job. A compromised cell Observer costs one
cell's detection; a compromised correlator costs cross-cell detection only.

**`W(p)`**, the watched-by relation [A·CR]: the `observer` seats holding a read authorization on `p`'s round topic,
its cell Observer and the domain's correlators (ADR-0038 §2). A fact in the mechanism's state. **Not realized as an
ACL in the reference**: cells are declared, not enforced (`mechanism/` I8).

**What the correlator reads** [A·CR]: at the archetype, every cell's admits and denials, cell Observers' findings and
the Reader's facts, the typed envelopes, and the payloads under the ACL (ADR-0038 §3). A facts-only correlator is a
permitted narrowing, declared on D-0038-2. **Its detection function is drafted and not in force** [P, 43 · 97]:
ADR-0051, Proposed (§10).

**Placement** [A·CR]: no `observer` seat shares a device with a Thinker it watches, and no two members of `W(p)` share
a device (ADR-0038 §4, carrying ADR-0008's rule forward). The reason is correlated failure and an effect path through
device memory, not quorum arithmetic. The Reader stage may colocate.

**Any-of** [A·CR]: a finding from any member of `W(p)` takes effect; **there is no Observer quorum** (ADR-0038 §5).
More Observers never lower safety and may lower availability. A quorum would let a compromised majority suppress an
honest finding (`Observers.tla` `M_QUORUM`).

**Heartbeat** · **watermark** [A·CR]: the fixed-schema fact an `observer` seat emits to report liveness: a watched
round topic and the sequence number through which it says it has read (ADR-0039 §1). Watermarks are kept per seat
and per round and only rise. A heartbeat is honest or refused: never above what exists, never falling, never from a
non-observer, never naming a round outside the observer's reach.

**`heard(o)`** · **`mark(o, r)`** [A·CR / R]: when the mechanism last admitted `o`'s heartbeat, on **this replica's**
clock, like lease expiry; and `o`'s watermark for round `r`, replicated from the log.

**`live(o)`** [A·CR]: a live lease, fewer than `T_obs` since `heard(o)` with the asymmetric margin, and
**`seq − mark < K`**, the strict form, so that after the admit being decided at most `K` are unread. The clock half is
checked at decide only; the deterministic half is re-checked at apply (ADR-0039 §1 R5).

**Coupling** [A·CR]: every Run admit under a `thinker` seat needs a live cell Observer (**R3**); a Thinker's next round
waits for coverage of its last; a Build promotion waits for coverage of the author's round; **the correlator is never
coupled** (ADR-0039 §2–§4). Coupling only refuses. A dead, partitioned or starved Observer stops its own cell and
nothing else, and the Thinker waits rather than being evicted.

**Presence is not progress** [D]: a fresh heartbeat with an unchanged watermark renews `T_obs` and nothing else; the
Thinker stays refused for its backlog. `Coupling.tla` `M_MARK` is the rule that forgets this.

**`K`** · **`T_obs`** · **`R`** [P]: the unread-emission bound and the heartbeat freshness interval, policy-floor values
in the values file; the round bound, a mechanism parameter per domain (ADR-0039 §1). `K < R` or the coupling check is
vacuous, refused at startup. **Placeholders**: `K` 8, `T_obs` 5000 ms, Run's `R` 64.

**What coupling bounds** [A·CR]: not `L`, which stays unmeasured, but the count next to it: at most `K` of a Thinker's
emissions unread by an Observer that has reported within `T_obs`, given an honest watermark.

**Collusion** [O]: the CR-2 case coupling cannot see. A colluding Observer heartbeats, reports a watermark and finds
nothing, all its own assertions. Lineage independence is the only cover, the correlated-miss test the only measure,
and **detection fails open against a colluding Observer** belongs on the residual-risk statement (ADR-0039 §5).

**Break-glass under a dead Observer** [A·Pv]: **decided: an emergency seat is not coupled** (ADR-0039 A2; ADR-0052
§4; item 49). R3 is a Thinker's rule. What goes uncoupled is a person, seated by a quorum, for one round, whose
topic the domain's operators read and any of whom can stop. Until Batch 34, R3 coupled break-glass too. Since
2026.10.07 it is a property and not only a witness: `Emergency_live.tla`'s two invariants over `ENABLED`, that while an
emergency lease is live every tool in its envelope can be admitted and that with no live Observer some call can be,
are proved, and proved in Lean of the encoding.

**Liveness extension** [C]: a module that extends a frozen one without editing it and adds what the frozen one
cannot state: fairness, leads-to properties and invariants over `ENABLED` (`Coupling_live.tla`,
`Emergency_live.tla`, 2026.10.07). Under every mutation of the base its next-state relation is the base's, so the
safety results carry over, and its proof module proves `SpecL ⇒ Spec`. Not a successor (`_A1`), which changes the
base.

**Leads-to** · **fairness** [D]: `P ~> Q`, whenever `P` holds `Q` eventually does; true only of behaviours that keep
taking the steps they can, which is what a fairness condition says (weak: a step enabled continuously is eventually
taken; strong: one enabled infinitely often is). **The stall coupling causes ends** is four leads-to properties of
`Coupling_live.tla`, under A12 and A18 (ToO §13): **checked by TLC at small constants, proved by nothing** (item 105).
Only a leads-to property sees `M_HBLIVE`, a mutation that passes every safety check and every witness.

**Liveness plan** [D]: `derived/topak-liveness-2026.10.07.md`, answering CR-37: what is already safety, invariants
over `ENABLED` (Tier 0), leads-to properties to model and prove (Tier 1), what to declare and not prove (Tier 2). Of
Tier 1 only the coupling stall is stated.

**Monoculture** [A]: an Observer should come from a different model family than the agents it watches. The predicate
now has one pair per cell to cover.

**Build has an Observer** [A·CR]: ADR-0021, ratified 2026.09.30 (Batch 18, C4) after ADR-0003 A3 scoped the storage
clause that had held it and R5 read it through for ADR-0008 vocabulary. Build emits to the effect stream, a round is
one pipeline invocation sealed at submission, the Observer follows ADR-0038 placement, and retention is per domain.
In force in the record; §5 and §6 are not exercised at the reference.

**Quarantine gate** [O, 48]: the 09.10 design's *hold*. It is `K = 0` with a hold instead of a wait, and under the
strict form `K = 0` admits nothing, so the hold needs its own mechanism.

**Persona** [A]: a signed, versioned Build artifact that binds a model to its complete runtime configuration
(ADR-0016). **TOPAK verifies Personas; it does not verify models.** The Persona is a lease field, so revoking a
Persona is a targeted revocation. Its seat-binding field takes the values `thinker` and `observer`, and since Batch 34
`operator` and `emergency`, which bind **a person's Persona**: a key, with the identity provider as its lineage's
root, and no model (ADR-0016 A1, A2).

**Verification vs suitability** [A]: signature, hash and provenance integrity are preconditions. Evaluations are
evidence. **Evaluation is deny-only.**

**Provenance degradation** [A]: **verified** → **attested** → **asserted**.

**Lineage** [A]: the archetype admits only **in-house pre-trained Personas from two independent lineages** (ADR-0017).
The admission clause stands, but its ordering-primacy clause is reversed in effect by ADR-0023, and that
supersession is unwritten (item 50).

**Seat distinctness** [A]: the Observer's Persona differs from the Thinker's **by lineage**. One pair per cell,
(`thinker`, `observer`), enforced where refusal stalls (ADR-0035 §5).

**Persona granularity** [A·CR]: two `thinker` seats on one Persona are two principals in two cells, and this is
permitted (ADR-0037 §5).

**Independence criterion** [P, 20]: ADR-0035, Proposed at R7. Until it is in force, `Contained` is unreachable at any
rung (§10). R4 says the ingress bound covers the guest's reads and not a tool's run outside it, so a training round
under ADR-0036's launcher stays declared until an in-guest trainer image exists. Three later revisions answer the
new records: an item delivered as a handle is `ingress` and not `consumed`; a round's tool list is both; an
operator's lineage is declared, with its identity provider as root.

**Typed lift split** [A]: the decoder ships in the Persona, and the validator lives in the mechanism (ADR-0018). Its
Reader scope correction is reversed in effect by ADR-0037 (C3); the split stands. **Decoder–alphabet compatibility**
under a change to S is open (item 17), and is the trigger to revisit a **decoder seat**, the option ADR-0037 did not
take.

**Decode observability** [A]: `none` is the only unconditional value. `topk_logprobs` is admissible for conformance
and substitution detection, never for claims about `L` (ADR-0019). Conformance admits only where inference is
attested (B12 dependent entry).

**Silent substitution** [D]: a provider changes weights with no event anywhere. Pinning makes it a detectable
identity mismatch. **No staleness argument covers Personas.**

---

## 8. Time, variation, boundaries

**Clock model** [A]: stated in ADR-0032. **Clocks buy liveness, never safety.** Epoch fencing carries safety.

**Trusted by failure direction** [A]: an interval whose failure **subtracts** (lease expiry, passive e-stop, vote
timeout) may use a local monotonic clock with an asymmetric margin that errs early. An interval whose failure
**adds or preserves** authority (Persona expiry, re-attestation) needs trusted time. ADR-0045 §6
refuses trusted time as a trusted-base row until a time source has an attested identity, so `T_persona` bounds a
value rather than an interval (§3). **Break-glass left this list**: R8, its TTL, was withdrawn, and an emergency
lease ends with its round on the clock a lease already uses, where failure subtracts. An operator's sign-on reads no
wall clock either: it is fresh because of the fence it names.

**No safety decision reads a principal-supplied clock** [A]: a timestamp in a payload is content, not a fact.

**`W + L + D < T_irrev`** [A]: the timing property, declared per effect class. **`W`** is the propagation window,
about a second, guaranteed by the mechanism. **`L`** is Observer detection latency, an emergent property, and
**unmeasured**. **`D`** is the human response budget, an organizational commitment. **`T_irrev`** is the time until an
effect becomes irreversible. Where no budget fits, **the effect must not be in the alphabet.**

**E-stop** [D]: **passive** (lease non-refresh, subtracts) · **active** (unilateral human stop, subtracts) ·
**break-glass** (quorum, **adds**: an activation of an emergency seating). The stops are an operator's control actions
(§5): `EndRound`, `Revoke` and `FenceEpoch`.

**HITL / HOTL / HOOTL** [D]: defined by enabling condition. Build affords HITL. Run's roughly one-second window leaves
HOTL.

**Boundary register** [D]: fourteen boundaries, each with a cadence, an instant, an interval of untruth and behavior
when unavailable. **B8** (Persona evolution) is the most critical. The **instants** are promotion, seal, fence and
revoke.

**Archetype** [A·CR]: the unique maximum of the parameter lattice. It is a reference point. **Nobody ships the
archetype** (ISO 26262 SEooC precedent).

**Degeneracy** [A·CR]: a form reached by driving named parameters to limiting values. Its **effect is premise loss,
not weakening** (ADR-0023). *Reduced* is the operational register.

**Admission test** [A·CR]: a variation is a rung only if it is reachable by parameter limit, and it must also be
checked for **type changes**. A capability the archetype lacks is a finding about the archetype.

**Rung** (degeneracy) [A·CR]: a position on one axis. A deployment is a tuple.

**Declaration record** [A·CR]: kind · parameter · archetype value · deployed value · premises falsified · theorems
voided · type changes · optional mitigation · composition note.

**Kind** [A·CR]: a **mechanism degeneracy** changes a value inside the verified object and ships as a release. A
**declaration degeneracy** changes something outside it and reopens nothing.

**Composition note** [A·CR]: required above one parameter. It names the **delta**: theorems voided jointly but not
individually. **A missing note is not an empty delta.**

**Type change** [A·CR]: a participant moving between the gate and principal. It moves the TCB.

**Declared records** [A]: D-0024-1 (k-of-n) and D-0024-2 (single signer), on approver fault tolerance. A-0025,
D-0025-1 and D-0025-2, on anchor recoverability. **A-0030** and **D-0030-1** (a Rego floor, *measured* rather than
*proven*), on floor verification. **D-0034-1** to **D-0034-4** (rung 2, rung 1, a native tool, rung 0), on
confinement. **D-0037-1** (no Observer in a cell), **D-0037-2** (no raw emission retained), **D-0038-1** (the shared
group only: ADR-0008 as ratified), **D-0038-2** (no correlator), **D-0039-1** (Run uncoupled), **D-0042-1** (effects
counted and recorded as reports only: the reference before 09.29), **D-0044-1** (bundle signing off: the reference
before 10.01), **D-0045-1** (no trusted-base declaration: the bottom of every axis), **D-0030-2** (routing verdicts
unchecked: every gate run before 10.01, and a run without the checker). Since Batch 30, **D-0034-5** and
**D-0034-6** (a native Run tool, filtered or not). Since Batch 34: **D-0047-1** (no labels: every item delivered
clear and unlabelled, the reference before 10.05), **D-0048-1** (no tool list), **D-0050-1** (operator requests
unsigned, from whoever reaches the socket: the reference before 10.05 and still its path for a first seating),
**D-0050-2** (peers behind one identity provider), **D-0050-3** (two operators in a domain) and **D-0052-1** (X1:
the reference before 10.05). In Proposed records, D-0035-1, D-0036-1, D-0051-1 and D-0051-2.
None is a deployment declaration.

**Properties lost** [O, 40]: the field ADR-0023 §6's schema lacks. The five Observer and retention degeneracies void
no safety theorem and state their losses in prose: a detection claim, an audit, a bound (ADR-0037 finding 6).

**Attestation rung** [A·CR]: **0** none · **1** asserted by the launcher · **2** measured boot · **3** confidential VM
with an independent verifier (ADR-0034, Accepted at G4). **The archetype is rung 3**; rungs 1 and 2 are declared
degeneracies, rung 0 is `Mediated` always. Attestation is a condition of the grant and lands in the lease's
`confinement` field; **no silent downgrade** at grant or renewal. **The declared rung is per seat** (ADR-0023 A1,
§6c). The reference issues rung 1 under its own assertion and rung 3 only *SIMULATED*; rung 2 is a seam it refuses
(ADR-0033 A7).

***SIMULATED*** [R]: a trust root played by test keys, at the reference: the CPU vendor's root (T-0045-16) and the
verifier (T-0045-17) in the rung-3 runs. Accepted only under a key an anchor issuance put in the rules, and said on
every surface that shows a lease resting on it. A result reached under it is a witness, not a claim.

**Session proof** [R]: at rungs 2 and 3, each action carries the attested guest's signature, under the session key
its appraisal bound, over the fence, the epoch, a counter and the action; checked at decide and, for the counter, at
apply, where it is the binding `ContainedMeansConfined` rests on (ADR-0034 §3.5; ADR-0033 A7). At rung 1 the
bridge is the session, and no token exists.

**Confinement profile** [A·CR / P]: a promoted artifact fixing seven clauses **P1–P7**: one channel, a measured
read-only root, no interpreter reachable, Wasm tools only, inference inside, one principal per guest and one guest
per round, its own reference values (ADR-0034 §1). In the reference a JSON file whose digest is the lease's
confinement digest (ADR-0036 §1, Proposed), each clause `pass`, `fail` or `vacuous` with a reason, registered only
once its one-file workspace is promoted, and confining only seats of its own domain. A Run profile is ADR-0034 A2's.

**Declared profile** [P]: a rung-0 grant may name a profile; its verdict is then derived from the declared clauses,
*declared by the operator and verified by nobody* (ADR-0036 R1). The trusted base at rung 0 stays empty: the host is
an **excluded** row (ADR-0045 T-0045-22). The profile is the constant across rungs and the rung the variable.

***Contested*** [A·CR]: signature valid, measurements diverging. Refusal plus a targeted revocation of the principal.
Rung 1 cannot produce it.

**Axes named so far** [D]: Persona provenance, event-log legibility, Observer scoping (archetype fixed: per cell plus
correlator), effect-stream role, arguably HITL/HOTL/HOOTL posture, approver fault tolerance, anchor recoverability,
floor verification, confinement rung, lineage strength, Observer coupling, emission retention, the trusted base
itself as a coordinate beside theorems held (ADR-0045), and since Batch 34 ingress labelling, the tool list, the
operator path and the emergency path. The set is not enumerated.

**Archetype-evolution record** [O, 7]: holds archetype versioning, the dominance rule and non-increasing TCB, and now
the versioning of ADR-0045's table and of the binding table (§9). Until it exists, **nothing bounds how the archetype
grows**, and "computed void" is a claim the binding table's last column makes by hand, revised with the records.

**Assumptions of use** [D]: ToO §13, framed as a SEooC. **A deployment that fails them does not inherit the
theorems.**

| # | Assumption |
|---|---|
| A1 | Effect exclusivity is enforced by a mechanism |
| A2 | Every allowlisted tool is hermetic |
| A3 | Anchor key-holders are honest at the declared capture threshold |
| A4 | Grant seats review independently |
| A5 | A trained, authorized human is present for break-glass, quarantine release and `D` |
| A6 | Trusted time exists for intervals that preserve authority |
| A7 | The deployment declares its degeneracies |
| A8 | Confirmation-required records are cited as author-ratified |
| A9 | The mechanism's replicas are not compromised |
| A10 | Each effect class declares `T_irrev`, and the budget holds |
| A11 | The lineage-independence criterion is in force before archetype provenance is declared |
| A12 | Every Run Thinker's cell Observer keeps up: heartbeats within `T_obs`, watermark within `K`, coverage to each seal |
| A13 | The cell Observer is not colluding with its Thinker |
| A14 | The deployment declares its trusted base under ADR-0045's schema |
| A15 | Sources are declared as what they are: entry and root labels, destination inputs, inside targets, each task's label |
| A16 | Operators are people, each holding their own key, and peers are vouched for by independent providers (provisional) |
| A17 | A provisional record is cited as provisional, and nothing is built on it that could not be rebuilt |

---

## 9. Genesis, process, and the corpus

**Genesis** [A]: the current process, **not a degeneracy**. Custody is declared as Scott, sole custodian, (1, 0).

**Unilateral ratification** [A]: the custodian may ratify any record that has decision text.

**Confirmation-required** [A]: a ratified record carrying a proof obligation over privileged paths (**C1**), an
exhaustiveness or confinement claim (**C2**), a reversal in effect (**C3**), or the resolution of such a debt
(**C4**). The count at G11 is **twenty-nine**: twenty-seven, and the two provisional records. **A marking may be
scoped to an amendment** (ADR-0003 A2; ADR-0029's own is in its status note, for A2 and A4 only) **or to one route**
(ADR-0053, C4 for `refines(Seats)` only), and one marking, ADR-0035 R2's, is by custodian instruction outside C1–C4.

**Provisional** [A·CR]: a status since Batch 34 (ADR-0029 A4): **Accepted (genesis) · provisional**. The record is in
force and **subject to redesign**; it was ratified without meeting its own ratification condition, and it states its
exit: the debt built and seen at the reference, and a reader who is not the drafter, after which the custodian
records it. Two records carry it, ADR-0050 and ADR-0052, and every amendment that depends on either does too.
Provisional is said wherever it applies, as *SIMULATED* is. A citation says *provisional* (assumption A17).

**Bootstrap set** [A]: ADR-0024 to ADR-0027. It **cannot carry the marker**, because confirming it under itself
would be circular. **Since ADR-0029 A2 it is reviewed at the bootstrap gate** with the rest of the corpus. Three
provisional amendments sit in it, ADR-0024 A3, ADR-0025 A3 and ADR-0026 A2; they are covered by the genesis
attestation, which must name them as provisional (ADR-0029 A4).

**Bootstrap reviewer** [A·CR]: the reader independent of the author whose review of the whole corpus at one manifest
digest is half the trigger (ADR-0029 A2). Two duties since A4: to establish that the policy floor is fit, with which
the floor is ratified; and to attest to rules that include the three provisional amendments, named as such. **None
is engaged and no pass has been run** (G11 §4).

**Bootstrap trigger** [A]: (a) a drafted TLA+ bootstrap specification of five modules (`Genesis`, `Anchor`,
`RulesFloor`, `Promotion`, `BreakGlass`), of which two exist, `Anchor` and `BreakGlass`, both checked and since
2026.10.02 proved (ADR-0029 B25), and both proved in Lean too, of their re-encodings (ADR-0053), with `BreakGlass_A1`
succeeding the second where it models X1, **and** (b) an **independent review of the entire corpus** at one manifest
digest (ADR-0029 A2). **The trigger is permission, not obligation.**

**Genesis bundle** [A]: the corpus manifest, the specification digest (checked or drafted-only), the review
attestation and the genesis rules. Every key-holder signs it, and that is issuance epoch 0. **It is the only artifact
never promoted.**

**Headcount** [A]: an archetype bootstrap needs **five** humans: three key-holders, two grant seats, and R5
disjointness. It needs six if the author holds a seat. **A solo bootstrap is not a bootstrap.** Since ADR-0029 A3
(provisional) the ceremony also seats the first operators, at least three in each domain at the archetype.

**Re-genesis** [A]: the exit from frozen rules. It creates a **successor system**. **Migration** is open (item 10).

**Genesis debt ledger** [A]: the per-checkpoint tally of the confirmation set. There is no forcing function: the debt
is visible, not bounded.

**Debts on the face** [A]: obligations an accepted record carries openly in its status note. Examples are ADR-0030's
six, ADR-0031's five, and ADR-0033's Kafka row.

**G checkpoint** [C]: the state of record. G11 (2026.10.09) is current. A cut is immutable, and corrections go to the
next one.

**Theory of Operation** [C]: the narrative. **It is not the state of record.** Revision 15 is current, cut from G11.

**Batch** [C]: a ratification group. There are thirty-seven; Batches 27 to 31 were ratified on 10.04, 32 to 35 on
10.05, 36 on 10.06 and 37 on 10.08, and the records tag them ⟨B27⟩ … ⟨B37⟩.

**Withdrawal** [C]: a History row of kind *W*: a drafted amendment withdrawn by the custodian and never ratified.
ADR-0026 W1, which withdrew R8, is the first.

**Superseded** [C]: a status class since G5. The record keeps its accepted text, marked no longer in force, and names
the superseding record. ADR-0008 is the first.

**Run row** [C]: a History row of kind *Run* recording a ratification run's results on the record, before
ratification, with what it left outstanding on its face.

**Conventions** [C]: G-C1 (files are cited by digest) · **a tree is cited by manifest** plus commit · **drift pins**
(`mechanism/corpus-pins.sha256`) · **pointer errata** (a promised pointer, no decision text) · **dependent entries**
(a ratification row with no text change, inside the History table) · **one results file per run**, never
overwritten · **a frozen module's successor carries the amendment tag**, as the suffix `_A1` · **a run finding the
text disagrees with is applied before ratification** · **placeholders say so three times** · and from G10:
**provisional is said wherever it applies** · **a record is ratified provisional only with its exit stated** · **an
addendum is split** so that what is evidence for text in force can be accepted alone · **a proof is certified or its
results file says why not** · **a model is checked to discriminate** · **a dependent amendment is applied as
marked**, beside the text it changes · **BOOTSTRAP marks the unsigned operator path** · and from G11: **a second
method proves again and certifies nothing the first did not** · **a Lean result counts with its replay** · **every
Lean results file names the digests of what it transcribes**, and `tools/lean-sync.sh` holds it to the tree · **an
encoding is checked against TLC's state graph, and a model of code against recorded traces** · **liveness is stated
in an extension, `_live`** · **a proof is written to the prover's known defects**, and the scan is run on every new
proof module · **a remainder with no bound is checked under a stated cap** · **what the custodian settled in a design
discussion is marked where it is used** (⟨K1⟩–⟨K9⟩, ⟨M1⟩–⟨M5⟩).

**Havoc semantics** [A]: modeling an agent as capable of anything its alphabet allows.

**Mutation** / **witness** [A/D]: every TLA+ property ships with a mutation that must fail and reachability witnesses
that must be violated. **The floor has a decidable non-vacuity gate. TLA+ still does not**; for TLA+ it is a
convention.

**Too-coarse model** [D]: a model can be too small to see a finding. `Lease.tla`'s single global epoch hid finding 5.
Four humans made R1's mutation hold vacuously. **A threshold needs at least three counted seats** before any
threshold property means anything.

**Checked** · **proved** [A·CR]: two methods and two words (ADR-0046 §1, Batch 25). **Checked** is TLC at small
constants: every mutation fails the property it targets, every reachability witness is violated, and the property
holds over every reachable state at those constants. It is a discrimination test, and the method for anything
existential. **Proved** is the TLA+ Proof System: an invariant holds of every behaviour of its module, for every
constant the module's named assumptions admit, under the hypothesis that the mutations which break it are absent; the
hypotheses are part of the claim and are stated with it. There are twenty-four proof modules and 5,416 obligations,
every one proved; `Mechanism.tla`, `Workflow.tla` and `Mesh.tla` are checked only. A third word, *proved in Lean*, is
ADR-0053's (below), and is never shortened to *proved*. **Neither word is used of the running reference**
(T-0045-28). From G3 to G7 the corpus said "no theorem is proved", and that was true until G8.

**Proof module** [A·CR]: `spec/<Module>_proof.tla`, which extends a frozen module without editing it and proves the
invariants it states, each theorem taking as hypothesis only the mutations that break it, with `Safe` under
`Mut = "none"` and one lemma per mutation saying what it admits. Its results file prints the digest of every module
in the EXTENDS chain and of the prover; both are frozen once a record cites them by digest (ADR-0046 §4).
`spec/proof-sync.sh` reports a proof whose specification has moved, and a changed specification is a successor module
with a successor proof (`spec/proof-method.md`).

**Certified** [A·CR]: said of a proof module in which every obligation is closed by the prover's own normalization,
or by an SMT proof the `ethos` checker accepted, or by a Zenon proof Isabelle checked, or is a temporal step
discharged by LS4, which no checker confirms (ADR-0046 A1; `spec/proof-cert.sh`, `spec/proof-certification.md`).
The certified configuration puts cvc5 behind `spec/smt-checked` in place of Z3; `tlapm -C` checks Zenon's proofs
and nothing else (E2). **Twenty-one of the twenty-four modules certify**; `RulesFloorNV_rev5`, `Confinement` and
`Confinement_A1` do not, and restructuring them is deferred (item 74); their theorems are proved in Lean too. **A
certified proof is not a verified one**: the prover's translation of an obligation into a query, its normalization,
LS4 and the checker are trusted, and the translation is **known to be unsound in two ways** (*unsound case*, below).
A certified proof is checked against the query, and the query can say something other than the obligation.

**Mutated proof** [C]: a scratch copy of a proof module with one hypothesis flipped to the mutation it excludes. The
prover must reject it, at the guard the mutation removes. It is the proof's own non-vacuity check, and is never an
artefact.

**Refinement** [D]: two senses. By composition (policy), which the corpus has. Specification-to-implementation
(formal methods), which it **does not have**: the gap is a trusted-base row (T-0045-28) and a debt ADR-0033 owns
(ADR-0045 R2). Stage 1 of the chain, trace validation, exists and is behind the tree since the workflow build; stages
2 and 3, a Lean model with differential testing and then its compilation, are the chain proper and are not begun.
ADR-0053's code-level proofs in Lean are **evidence toward** the row and not a stage, and no addendum may cite a stage
discharged through Lean until the binding table can say "either proof" (ADR-0053 §5).

**Operational model** [R / P]: `spec/Mechanism.tla`, the state machine `State::apply` and `check_live` written once,
operationally, as a function from a projected state and a log entry to the next state and the result. What the
reference's recorded behaviour is checked against; pinned, not frozen, since it moves with the code. The other
modules each check one property over their own abstraction and are not a specification of the mechanism. Since
2026.10.05 it models the label fold and the stale-`clearSet` refusal, a seating, the gate on unsigned requests, a
control request with its facts recomputed, an activation, and X1's approval rejected (ADR-0033 A14).

**Trace validation** [R]: with `TOPAK_TRACE_DIR` set, the core records every `apply` as a step; `spec/trace2tla.py`
and `mechanism-trace-run.sh` replay each recorded trace through the operational model in TLC, failing at the first
step whose projected state or result differs. Two runs: 2026.09.30, 21 traces and 163 steps (ADR-0033 A5);
2026.10.01, 22 and 168 after Batch 17's debts changed the model (A6), every step matching in both. The second caught
a test that changed a floor constant between entries, not the code. **A mechanized link and a drift harness, not a refinement and not independent evidence**: the model was
written from the code by the same hand on the same day. Three facts it takes from the trace rather than computing:
issuance validity, approval signatures, the parameter digest; since 2026.10.02 three more, for confinement: an
appraisal's signature and key, a session proof, a profile's parse. On 2026.10.02, 57 and then 62 traces, 709 steps,
every one matching (ADR-0033 A7, A8). **On 2026.10.05, 82 traces and 1,007 steps, every one matching** (A14), with
more taken from the trace: whether a request's signature is its seat's, whether a sign-on assertion verifies, which
roster keys approved an activation. The run found a race no proof had: a lease just granted could be ended as
expired (A13). The model was then broken on purpose six ways: five produced a mismatch and the sixth an evaluation
error. The floor's decision on an operator's request is not modelled. **Not rerun since**: `Mechanism.tla` does not
model workflows, and a traced run that loads one would not match it (ADR-0033 A16). Not the Lean *trace replay*
(below), which runs the same traces through a Lean model's own `apply`.

**Refinement check** [R]: `spec/ConfinementRefinement.tla`, which reads every state trace validation replays against
`Confinement_A1.tla`'s invariants: no silent downgrade (per seat), *Contested* stopped, a fresh appraisal under every
live lease, and `contained` only where its premises hold. A check on tested paths, not a refinement; it cannot check
`ContainedMeansConfined`, which is about the image the host ran.

**Reference implementation** [R]: `mechanism/`, the admit path end to end. It is **evidence, not the verified
object** (ADR-0033 §1). It is cited by manifest and commit (last `SHA256SUMS-REF-2026.10.09` at `749d54f`), it has
never been promoted, and its own trusted-base declaration is ADR-0045 Annex B. No guest it launches passes P3, so
it fails A1. **Forty-seven assumptions and eighteen gaps** are tagged in the code (`GAPS-AND-ASSUMPTIONS.md`). Since
09.29 it has seat kinds, cells, a correlator, heartbeats, marks, seals, coupling, coverage, Run's three actions, the
effect counter and the `Actuate` record; since 09.30 the trace recorder; since 10.01 signed bundles, the `ttl` bound
and the issued key fields; since 10.02 the launcher and the Wasm tool host. **On 2026.10.05 it was rebuilt in five
stages** (ADR-0033 A9 to A12): the allowlist entry and its load checks, the tool list and the opening record,
labels and handles, operators, and the emergency seating; and it was **switched outright to the `emergency` floor
stage**. 133 tests. **On 2026.10.08 it was built to ADR-0054 and ADR-0055, both Proposed**, and linked the `workflow`
floor stage, which is not in force, at the custodian's direction (A16, pending): 155 tests. On 2026.10.09 it dropped
`denials` (A17, pending). Fifteen addenda are ratified and two are pending.

**Reference findings 1–11** [R]: routed to records in ToO §15. Three needed running code to find (1, 4 and 9). Only
finding 9, proposer retry in the drafted `Paxos` module, is still open (item 24). Three more on 09.29: one live lease
had been enforced per seat, not per principal; a coupling rule refused the heartbeat it depended on; `T_obs` cannot
be re-checked at apply. Three more from the Run build (12 to 14): ADR-0041 named the wrong gate for a control; the
module and the reference counted different things; the bundle tier cannot hold a tool to its channel. Four on
10.02 and six on 10.05 (ToO §15), among the last a load check that could not be failed, a lease that cannot be
narrowed to a tool, and the lease-expiry race. Three on 10.08 (`mechanism/` findings 21 to 23): a round ending on its
own admit sealed before that admit's record; a denial count with no replicated source, dropped; and a clear input
that needs a read path the reference lacks (item 108).

**Host-run occupant** [R / P]: `serve.py` on the host with no container, the reference's first declared profile
(`slm/serve/profile-host-rung0.json`), a rung-0 principal whose `Mediated` verdict is derived rather than empty.

**Crash-recovery replicas** [A]: the consensus replicas are not Byzantine (ADR-0033 §3). This is assumption A9 and
trusted-base row **T-0045-1**: a trust root whose residual is the forged admit, with mutual authentication as its
delegated mitigation, unbuilt (item 23). BFT is not required.

**Trusted-base record** [A·CR]: ADR-0045, drafted 2026.09.30, revised six times, ratified 2026.10.01 (Batch 22, C2 and
C4). The rule for entering the trusted base, the archetype's table of **thirty-seven rows** (Annex A), and the
reference's own declaration (Annex B). Five rows came with Batch 34 (ADR-0045 A1, A2): T-0045-32 to T-0045-34, the
label computation and delivery, the declarations (excluded), and handle resolution with the list's rendering; and
T-0045-35 and T-0045-36, an operator's identity provider and its custody of its key. T-0045-24 is delegated at the
archetype since Batch 30, and Annex B still shows it excluded at the reference for a reason that ended with ADR-0033
A9 (item 89). Six records owed it rows and it carries all of them. Two Annex B rows changed class after
ratification, by dependent entry: the bundle signer, excluded to trust root under a dev key (B23), and the solver's,
refused to trust root for the proof checker (B24). A third dependent entry added a row: T-0045-31, the prover (B25).
A fourth added T-0045-37, the Lean toolchain (B36), and Batch 37 put the prover's two unsound cases into T-0045-31's
residual (A3).

**Binding table** [P]: `spec/theorem-premise-binding.md` (ADR-0045 R6), one row per checked property, with the proof
module named in each proved row, naming the trusted-base rows, the degeneracy parameters and the declared gaps it rests on; forty-two rows, DRAFT, revised with
the records it binds. Its last column computes the reference's inventory: a property holds when every row it names
is delegated or a trust root, and is void on an excluded, undeclared or refused one. Writing the proofs found five
errors in it, four in the "Breaks under" column and the `K < R` premise, corrected at Batch 25 (ADR-0046 §5). Since
Batch 36 it carries **derived premises** (below). **It has no rows for ten modules**: `Labels`, `ToolList`,
`Operators`, `Emergency`, the two successors, the two liveness extensions, `Workflow` and `Mesh` (item 90).

**Row** [A·CR]: one entry of the trusted base, `T-0045-n`, with a fixed schema: component, layer, *trusted for* (the
row's premise), rungs, class, what its failure can produce, what fixes its identity, residual (ADR-0045 §1).

**Delegated** · **trust root** · **excluded** · **refused** [A·CR]: the three row classes and the refusal (ADR-0045 §2).
A **delegated** row's failure can produce only subtractions and needs no key; a **trust root**'s failure can add
authority, and the corpus trusts it because an issuance or a promotion fixes its identity and its own record admitted
it; an **excluded** row is relied on and trusted for nothing, so the theorems on it compute void; anything whose
failure can add and whose identity nothing fixes is **refused**, inside the verified object or redesigned. "Adds
authority" is ADR-0015's: an admit the rules in force would refuse, a promotion the tally would stall, an issuance
the rules floor would reject.

**Premise node** [A·CR]: a row's *trusted for* sentence, read as a premise in the theorem DAG; **an undeclared row is
false**, and type changes are rows (ADR-0045 §3). Removing a row is a tightening; adding one is a relaxation that
needs its own record.

**The solver, refused** [A·CR]: cvc5's "implies" answers fail both admissible classes; ADR-0045 §6 refuses the row
and ADR-0030 A1 moves the trust to a proof checker (§4), which is T-0045-14's trust root since Batch 24 (2026.10.01):
the checker binary, its rule signature and the wrapper, pinned by the three digests the gate header prints.

**The prover** [A·CR]: T-0045-31, the TLA+ Proof System (`tlapm`, with Z3, Zenon, Isabelle and LS4), a toolchain trust
root beside TLC's T-0045-29 since Batch 25 (ADR-0046 §3). Trusted for: "all N obligations proved" means each is a
theorem under the module's assumptions. Pinned by `tools/TLAPS-PIN`, and the wrapper refuses another binary; the
install is not tracked. Since ADR-0046 A1 the row has a **certified configuration** (see *Certified*). Residual: its
soundness and its backends' are unexamined; the SMT proofs are checked by `ethos`, not by Isabelle, for twenty-one
modules of twenty-four (item 74); and since Batch 37 it names **two known unsound cases** in the translation, which no
result a record cites rests on, by a scan and a reading (ADR-0045 A3; ADR-0046 A2).

**Unsound case** [A·CR]: one of the two known ways `tlapm` 7824dab's translation lets a false statement prove and
certify (ADR-0046 A2, Batch 37). **A term under a binder**: an `ENABLED` or `\cdot` not expanded, or a temporal formula,
abstracted as a constant that drops any variable bound around it. **Two terms with one name**: every abstracted term,
and every atom handed to LS4, named by 20 bits of a hash the prover does not check, of a print that does not tell a
bound variable from a constant of its name, so two terms can be one by a **collision** of the hash or by a **capture**,
where expansion makes them print alike. A rule for writing proofs keeps a proof from them
(`spec/proof-certification.md` §10). **No check detects the first** (item 104). Not reported upstream, by the
custodian's decision.

**Proof scan** [C]: `spec/proof-scan.sh`, run on every new proof module: the sources' untranslated terms, the certified
runs with Isabelle's trace, a second run with every identifier renamed, and every obligation read as the prover forms
it for a capture. On 2026.10.08, 24 modules and 1,853 obligations sent to a backend, no capture. **The renamed run is a
second naming, not a proof.**

**The Lean toolchain** [A·CR]: **T-0045-37** (ADR-0053 §3, B36), a toolchain trust root beside the prover: the kernel,
the elaborator and Lake that build the terms it checks, `leanchecker` that replays them, and the compiler where
`native_decide` evaluates, with the encodings, transcriptions and statements, read against what they state. Lean
4.33.1, pinned by `tools/LEAN-PIN`, installed through elan and not tracked.

**Proved in Lean** [A·CR]: a claim the Lean kernel discharged, of the re-encoding, transcription, model or statement it
names (ADR-0053 §1). **Never written "proved" alone.** A second derivation with different premises: bounded by neither
constants nor a solver, and a claim about none of the TLA+ text, the Rust or the Cedar text. It changes no claim of a
TLAPS proof, and T-0045-31's residual does not move.

**Re-encoding** [A·CR]: a TLA+ module written as a Lean transition system, each definition beside the TLA+ it
transcribes; its theorems are the proof module's, by induction on reachable states, the step TLAPS hands to LS4.
Sixteen modules in `spec/lean/`, among them the three that do not certify. Frozen with its base module.

**Transcription** [A·CR]: a function of the reference written in Lean beside the Rust: `admit.rs`'s `compose` with the
floor wrapper, proved a `Decide` step of `FloorComposition`, and `clock.rs`'s interval. Read against the Rust; no
translator was run. Pinned, not frozen.

**Model** (of `apply`) [A·CR]: a transcription of `State::apply` that keeps the checks and effects a module is about and
makes every other check one oracle that can only refuse, so its steps include every step the code takes. The
Seats-shaped model refines `Seats` at its constants; the Coupling-shaped one keeps `Coupling`'s properties at any size.
**Stale at G11**: they transcribe the action and seat kinds, which gained `Route` and `orchestrator`, and the custodian
left them so (item 103). Not the operational model, `Mechanism.tla` (§13).

**Statement in the model** [A·CR]: a floor and its schema in cedar-spec's abstract syntax, generated from the floor's
files by `floor/lean/gen.py`; its theorems are gate claims under the model (*the floor stated in Lean*, §4).

**Replay** [A·CR]: `leanchecker --fresh`, which replays every constant a package reaches through the kernel in a fresh
environment. **`#print axioms` alone was deceived** by a declaration added with the kernel check off, and the replay
refused it, so every results file carries one. The same kernel in another process, not an independent checker.

**Trace replay** [A·CR / R]: the reference's recorded traces run through a Lean model's own `apply`, each step compared:
82 traces, 1,014 and 1,015 steps, every one matching (`seats-replay.sh`, `coupling-replay.sh`, 2026.10.06). A check
over the traces the suites record, not a proof. **Not trace validation**, which replays the same traces through
`Mechanism.tla` in TLC.

**Graph check** [A·CR]: an encoding's mirror evaluated on TLC's state graph of its module under every mutation, for
`Seats`, `FloorComposition` and `Emergency`. It sees an encoding that is too lax or too strict, which no invariant can:
a `Grant` that drops a check keeps both of `Seats`' invariants and adds 3,552 edges.

**Derived premise** · **`refines(Seats)`** [A·CR]: a premise of the binding table that is a disjunction of premise
sets, so a theorem with two derivations can be carried by either (ADR-0053 R7): `invariant(M)` for a proved row,
which rests on the prover in place of TLC, and `refines(Seats)`, the route by which `Seats`' two theorems reach the code
through the Lean model, around T-0045-28. **ADR-0053 is confirmation-required for that route alone (C4)**, and no
ADR-0033 addendum cites it as a stage.

**Lean sync** [C]: `tools/lean-sync.sh`, the Lean packages' `proof-sync.sh`: it compares every digest a newest results
file names with the tree, and every kernel and dependency with the pin, and checks that the floor the reference links
is stated in Lean. **It exits 1 at G11**, for the stale models, where Batch 36's condition had it exit 0.

**What runs is a row** [A·CR]: the implementation as a refinement of the specification, the model checker at the
constants run, the prover for the invariants it proves (T-0045-31), and the build toolchain are trust roots for every deployment until a refinement exists
(T-0045-28 to 30, ADR-0045 R1). The first draft had called them "checked, not trusted"; a comparison with Moon &
Varshney caught it (finding 7).

**Assisted drafting** · **drafter's choice** [C]: ADR-0044, ADR-0045, ADR-0030 A1 and ADR-0046 were drafted by the
assistant at the custodian's request, every choice the custodian did not settle marked *(drafter's choice)*;
ratification settles them, and all four are ratified (Batches 17, 22, 24, 25). **Nearly every text ratified since
G9 is the drafter's**: ADR-0047 to ADR-0050 and ADR-0052, the dependent amendments, the modules, the proofs and the
rebuilt reference, and since G10 ADR-0053 and its three Lean packages, Batch 37's amendments and the review runs that
found the prover's cases, and the two Proposed workflow records with their modules, floor stage and reference; each
ratification row says it was not reviewed by a reader other than the drafter. ADR-0046's condition that the
custodian regenerate its evidence was run by the drafter at the custodian's direction. One step further from review
than author-ratification, and ADR-0029 has no criterion for it (item 66).

**Scoping amendment** [C]: an amendment that narrows what an accepted clause was ever about rather than changing its
effect ratifies without C3, and its row names the reading under which C3 would attach (ADR-0003 A3, B17).

---

## 10. Proposed records

Five records and one section are Proposed at G11, and twelve amendments are pending on them. **None is in force.**
ADR-0005 left this list in Batch 27 and ADR-0042 §6 in Batch 30. ADR-0053 was drafted and ratified between G10 and
G11 and never stood here at a checkpoint.

**ADR-0022 §6** [P, 1]: Build's confinement obligation (§2), the one Proposed section, left out of Batch 2.

**ADR-0051** [P, 43 · 97]: the correlator's detection function. Two tiers, of which only the first is specified:
**five correlations**, each a named fold over facts that a second reader can recompute, and a judgment tier beside
them. A finding carries its evidence; denials are placed against the log, not numbered; the store is a cache of a
fold, keyed by round, and never outlives its sources. `Correlator.tla` is proved and certified. Not built at the
reference, which is **D-0051-1**; one correlator in a domain is **D-0051-2**. Its three thresholds are placeholders.

**Lineage projection** [P, 20]: ADR-0035 proposes that a Persona's lineage record is **projected from the Build log**,
not taken from the trainer's manifest. A lineage that can only be declared is **D-0035-1**. **Every share the gate
computes is an upper bound** (R2), after the rehearsal refuted the first draft's monotonicity claim.

**Exclusion rules E1–E5** [P]: two lineages are independent unless one of these fires: **E1** shared weights ·
**E2** shared generators · **E3** corpus overlap above θ · **E4** same architecture family and tokenizer · **E5**
shared curators. Plus the **distillation rule**. The rehearsal is in `slm/`; the θ values live in the values file
and are unset.

**Launcher** [P, 34, 35]: ADR-0036, Proposed at R6. At rung 1 the launcher is the channel: **launch, appraise, grant,
bridge**, with the token never entering the guest. Its first profile fails P3. R1 adds the rung-0 declared profile
and the ladder; R2 points finding 1 at ADR-0035 R4. Its ratification run is item 34, with five missing pieces. **The
launcher in the node**, its §6 step, is built, and its addendum was ratified ahead of the record (ADR-0033 A7, Batch
29): a `launch` operator request, a host-process, container and *SIMULATED* rung-3 backend, and no token for a
launched lease. Four of the reference's choices under it are in ADR-0034 A3, and a fifth in ADR-0023 A1; the sixth,
a profile promoted as a one-file workspace, is ADR-0036's own.

**Workflow records** [P, 101]: ADR-0054, a workflow as a promoted DAG, and ADR-0055, a workflow that may be a mesh,
both drafted 2026.10.07 and built at the reference on 2026.10.08. Their terms are under §2. `Workflow.tla` and
`Mesh.tla` are checked and have no proof. ADR-0055's dependent entries are not drafted.

**Pending amendments** [P]: twelve. Ten are ADR-0054's, drafted into accepted records and marked inline: ADR-0015 A1
(`Route` an emission), ADR-0024 A4 (a workflow is seatings and a graph; the bootstrap set), ADR-0031 A4 (a third
grant path), ADR-0037 A5 (`orchestrator`), ADR-0039 A3 (coverage at the edge; the orchestrator coupled), ADR-0040
A2 (`Route`), ADR-0041 A4 (`Route`'s envelope; R3's scope), ADR-0042 A3 (two more ends of a round), ADR-0043 A3
(`input`) and ADR-0047 A1 (the attributes and the routing rule). Two are ADR-0033's addenda for the reference, A16 and
A17. ADR-0035, itself Proposed, was revised in place (R8). ADR-0026 A1 (R8) was withdrawn, not ratified (W1).

---

## 11. Outstanding

These terms name a hole. Each one points to the G11 §7 open list.

| Term | Item |
|---|---|
| **Sandbox gap** (rung 1 built, rung 3 *SIMULATED*; no guest passes P3, so no real principal is `Contained`) | 1 |
| **Floor fitness**: owned and timed · **a test for it** | 2 · 87 |
| ADR-0017 supersession | 6 · 50 |
| Archetype-evolution record · the binding table's versioning | 7 |
| Per-class floors (ADR-0014) | 9 |
| Re-genesis migration | 10 |
| Custody beyond (1, 0) | 11 |
| The stale derived set | 12 |
| Decoder–alphabet compatibility; a decoder seat | 17 |
| Independence criterion (ADR-0035) · the in-guest trainer image | 20 |
| Lifting a revocation | 22 |
| Replica authentication (T-0045-1's mitigation) | 23 |
| Finding 9 | 24 |
| The floor in question: the `emergency` stage, genesis-provisional · the genesis text, DRAFT | 25 |
| Retention · accelerator attestation (T-0045-21) | 28 · 29 |
| θ values · best-practice review of the bound | 30 · 33 |
| ADR-0036's run and ratification · a P3-passing image | 34 · 81 · 36 |
| `Lease.tla`'s rung range | 38 |
| ADR-0026 §6 rerun with A2.2 and A2.3 | 39 |
| **Properties lost** field | 40 |
| **Seat-registration record** (a seating is now a thing of record; the reference makes one by the BOOTSTRAP path) | 41 |
| ADR-0037's occupant steps (retention audit, Reader facts) | 42 |
| **Correlator's detection function**: ADR-0051, Proposed, not built | 43 · 97 |
| Sequence numbers on denials · correlator's store vs erasure | 44 |
| A scripted cell Observer (the scripted Run cell is built, for labels) | 45 |
| `W(p)` as an ACL · gate-side `K < R` · A2.2 in the reference (G18) · readers nothing gates | 46 |
| **Measured `T_obs`, `K`, `T_persona`, Run's `R`** | 47 |
| **Quarantine gate** · Observer round layout · a round-layout record | 48 · 60 |
| **Delegation / on-behalf-of** · attenuation · honeypots | 51 |
| The live smoke run | 52 |
| **The refinement chain**, stages 2 and 3 · the reproducible build | 56 |
| **Gate evidence signed** (T-0045-13); `AttestGates` is attributed and still an assertion | 57 |
| ADR-0042's remainders: the missing record, result size, Run's TTL | 61 |
| `T_persona` on a local clock | 62 |
| A deployment declaration template | 64 |
| An ADR-0029 criterion for assisted drafting | 66 |
| Signing at promotion · the bundle key's custody row | 67 |
| The checker carried in a release | 68 |
| What `holds°` rests on: cedar's folding of the totality gate | 69 |
| The register's header | 71 |
| Three proof modules that do not certify (their theorems proved in Lean too) | 74 |
| Model checking at practical constants · simulation at large bounds | 75 |
| The diagrams, unmeasured, and behind the tree; the Lean route's omits `Emergency`'s graph check | 76 |
| One driver per TLC results file | 78 |
| A measurement cannot cover its profile's digest (ADR-0034 §2 against P7) | 82 |
| Build's P4 at the reference | 83 |
| The component tool interface · the protocol on a declared target | 84 |
| The sixth reference choice, in ADR-0036 | 85 |
| **The exit from provisional for ADR-0050**: a first lease from a completed tally; a promoted seating; a review | 88 |
| ADR-0045 Annex B, T-0045-24 at the reference | 89 |
| `spec/` behind the records: `RulesFloorBase.tla`; binding-table rows for ten modules | 90 |
| The floor stages' opening comment, false of the stage the reference links | 91 |
| **The exit from provisional for ADR-0052**: ADR-0050's; a seating prepared by promotion; two open questions; a drill counter | 92 |
| What the label machinery trusts: the deciding replica's facts; unlabelled error text; scalar handles | 93 |
| What the reference does not follow in records in force: the entry's digest; a task at a first seating; the two lists re-read | 94 |
| A lease's tool narrowing | 95 |
| Whether anything else a replica keeps is recorded after the lock is released | 96 |
| Two policy comments that call ADR-0049 Proposed | 98 |
| The reviewer's guide, excluded from the manifest and kept current | 99 |
| The narrative against G11 (discharged by revision 15 and this revision) · tags owed | 100 |
| **What the workflow records owe**: proofs, binding rows, values, parallel branches, joins and pools, ADR-0055's dependent entries | 101 |
| **The reference links a floor that is not in force** | 102 |
| **`mechanism/lean` stale**; `lean-sync.sh` exits 1 | 103 |
| **The prover's two unsound cases**: no check for the first; unreported upstream | 104 |
| **Liveness checked and not proved**; the plan's other Tier 1 items | 105 |
| Questions ADR-0053 put to records: a seat's kind changed by issuance; several Observers in a cell; `apply`'s index | 106 |
| ADR-0053's open obligations: an independent kernel, the premise table's disjunction, more graph checks, nine modules unencoded, a second platform | 107 |
| What the reference found for the corpus: the seal after an ending admit; a clear input's read path | 108 |

**Closed since G10**: the narrative against G10, and its tags (86). **Closed between G9 and G10**: ADR-0005 (5) · R8,
by withdrawal (8) · the Run profile and ADR-0042 §6 (26, 58, 80) · the launcher in the node (35) · break-glass under
a dead Observer, decided (49) · the allowlist entry's schema (59) · the prover pinned (73) · a Run tool's channel
declared twice (84) · five of the six reference choices (85).

Unowned and not numbered: **`Invoke` hermeticity** for native tools (an excluded row, T-0045-23) · **channel
fidelity** for native Run tools (T-0045-24; D-0034-6; G19) · **flow** (CR-6), which labels bound per round and trace
for no value · the **residual-risk statement**, headed by anchor capture and now carrying collusion and the wrong
declaration.

---

## 12. Adjacent vocabulary

These are carried from the 09.17 glossary §12 unchanged, with these additions: **Cedar** and its Lean-verified
semantics and **SymCC** analyses (now the floor instrument) · **MCP** (the reference's agent interface) ·
**confidential VM** and **RATS verdicts** (ADR-0034) · since G11, **Lean 4**, **cedar-spec** (Cedar's semantics,
validator and symbolic compiler formalized and proved in Lean by its authors) and **`leanchecker`** (ADR-0053) ·
**CaMeL**'s privileged planner and quarantined model, the split ADR-0054 keeps with the planner's trust removed ·
**orchestration** and **choreography** in the multi-agent sense (ADR-0055 §7) · **weak and strong fairness** and
**`~>`** in TLA+'s temporal logic (§7).

---

## 13. Terminology hazards

These collisions are live. Several are new since 09.17.

1. **"A1", "A2" and so on: four alphabets.** Amendments (ADR-0003 A1), assumptions of use (A1–A10), archetype
   declarations (A-0025, A-0030), and the readiness key. *"ADR-0003 A2"* and *"assumption A2"* are unrelated.
2. **"B" and a number: four referents.** Boundaries (B8, B12, B14), floor policy IDs (forbid **B7**), ratification
   batches (⟨B5⟩–⟨B9⟩), and ADR ratification-table rows (ADR-0026 B4, ADR-0033 B8). *"B7"* and *"B8"* each have more
   than one live meaning.
3. **"E" and a number: errata and exclusions.** ADR-0031 E1 and ADR-0015 E2 are errata. ADR-0035's E1–E5 are
   independence exclusions.
4. **"R" and a number: rules-floor entries, record revisions and floor policy IDs.** "0031 at R3" is a record
   revision. "R3" alone is a withdrawn rules entry, and `R3-observer-live` is a floor forbid. **R5, R6 and R7 are
   each a rules-floor entry and a label forbid**: rules-floor R6 bounds the exception count, and floor `R6` refuses a
   steered destination. Give the forbid its full name. The readiness key's **R** is another use.
5. **"G" and a number: checkpoints, conventions and gaps.** G1–G11 are checkpoints, **G-C1** is a convention, and
   **G1–G19** in `mechanism/` are code gaps: *G5* is both a checkpoint and a gap. Name the three floor gates;
   don't letter them.
6. **"Rung": now three orderings.** ADR-0023 degeneracy rungs (per axis), confinement attestation rungs 0–3
   (ADR-0034, Accepted), and provenance rungs on ADR-0017's axis. `slm/` says "every round runs at rung 0", meaning
   **attestation** rung. Always qualify.
7. **"Floor": now six things.** The policy floor, the rules floor, the forensic floor, floor fitness, **the genesis
   floor** (a DRAFT text, as distinct from the machinery that checks one), and **the floor stages**, of which
   `emergency` is the floor in force and `workflow`, not in force, is the text the reference links. There is also
   "floor minimum", a seat count, and "the floor's minimum over labels", three forbids.
8. **"Declared": two opposed senses.** A **declaration** degeneracy reopens nothing (ADR-0023). A **declared**
   lineage record is the *weakest* strength (ADR-0035 D-0035-1). Declared custody is a third use.
9. **"Revocation" vs "fence".** A targeted revocation ends matching leases. An epoch fence ends every round. Earlier
   text used "fence" for both.
10. **"Agent": three referents.** The A in TOPAK, the LLM inside a seat, and OPA (Open Policy *Agent*).
11. **"Epoch": four counters.** Rules epoch, anchor epoch, lease epoch, and deployment epoch. The fence is a log
    index, not an epoch.
12. **"Round": Build and Run differ.** A promotion is also a round. Always qualify.
13. **"Byzantine": agents, not replicas.** Agents are Byzantine. The control-plane replicas are crash-recovery
    (ADR-0033 §3), which is now declared.
14. **"Proved": restored, with one meaning** (ADR-0046 §1). Retired at rev 7 (CR-25) because nothing was; since
    G8 it names what the prover discharged, with its hypotheses. *Checked* is TLC's; *must hold* is a requirement.
    **Since G11, *proved in Lean* is a fourth phrase**, for what the Lean kernel discharged, and is never shortened to
    *proved*. None of them is said of the running reference.
15. **"Degenerate"** collides with TLA+'s "degenerate behavior" (the ADR-0023 obligation) and reads as pejorative.
    Use *reduced* in operational prose.
16. **"Confirmation-required" count.** G11 says **twenty-nine**: twenty-seven and the two provisional records. G10
    said twenty-eight; G8 and G9 said twenty-two; G5 and rev 9 said fourteen, and the 09.26 glossary's *nine* was G3's.
17. **"Seat": two senses, one word.** The LTRO position (ADR-0016, ADR-0037) and the promotion-roster slot
    (ADR-0024). The **kind** field separates them; an Observer holds both at once.
18. **"R": four uses.** Rules-floor entries, record revisions, the readiness key, and now the **round bound** `R`
    (ADR-0022 §3, ADR-0039 §1). "`K < R`" is the fourth.
19. **"Declared": a fourth sense.** A rung-0 **declared profile** (ADR-0036 R1): declared by the operator, verified by
    nobody. Results print the word so it is not mistaken for attestation.
20. **"Coverage" and "live" are two different facts.** Coverage is a watermark at the seal; live is a fresh heartbeat
    with a watermark within `K`. A promotion needs the first; a Run admit needs the second.
21. **"Reader" is no longer a seat.** Text that gives the Reader a Persona, a lease or a distinctness obligation is
    pre-ADR-0037.
22. **"Provisional": three senses.** A **provisional record** is in force and subject to redesign (ADR-0029 A4). The
    floor is **genesis-provisional**: not ratified, and ratified at bootstrap (ADR-0030 A3). And the reference's
    *PROVISIONAL* choices were decisions made for the code and owed to records, five of the six now paid.
23. **"C" and a number: three referents.** Confirmation criteria C1–C4, control entries `C1`–`C9` in the floor, and
    correlations in ADR-0051. "C1" on a status line is a criterion.
24. **"W": four uses.** The propagation window `W`, the watched-by relation `W(p)`, the load checks W1–W10
    (ADR-0049), and a withdrawal row (ADR-0026 W1).
25. **"Operator": a principal, and a word.** Since ADR-0050 an operator is a seat kind held by a person. Older text
    uses it for whoever runs a deployment, and "the operator's assertion" there names nobody in particular.
26. **"Seating" and "grant".** A seating puts a principal on a seat and is a quorum's; a successor grant is one
    operator's; an activation is a roster's quorum, for one round. All three put a lease on the log. A workflow's node
    grant, pending with ADR-0054, would be a fourth: the mechanism's, under a promotion's authority.
27. **"Lift": two senses.** The typed lift of a request into schema S, and lifting a revocation, which adds
    authority and has no owner.
28. **"Envelope": three things.** An action's envelope in the alphabet, a record's envelope of facts beside its
    payload, and an emergency seating's envelope, which is an allowlist.
29. **"Label" is not a classification.** It is a declared property of a source. Nothing reads content to produce one.
30. **"Clear": a delivery mode, and a verb.** An item delivered clear enters `clearSet`; nothing ever clears it.
31. **"Break-glass" still names the roster, the quorum and F5.** It no longer names a floor entry, a flag in a
    record or an approval scoped to an epoch.
32. **"Activation": two meanings, in two statuses.** An emergency seating's **activation** (ADR-0052, provisional) is a
    roster's quorum granting one round to one person. A mesh's **activation** of a node (ADR-0055, Proposed) is one
    run of that node. Say which.
33. **"Orchestrator": a retired group and a proposed seat.** ADR-0008's "orchestrator-level Observer group" is
    superseded. ADR-0054's `orchestrator` is a seat kind that only narrows. Text older than 2026.10.07 means the first.
34. **"Model": five senses.** A TLA+ module checked by TLC; the operational model `Mechanism.tla`; a Lean **model** of
    `apply` (ADR-0053); Cedar's Lean model (cedar-spec, T-0045-3's "the Lean model"); and the language model inside a
    seat. *Model checking* is the first.
35. **"Replay": three things.** Trace validation replays recorded traces through `Mechanism.tla`; a Lean **trace
    replay** runs them through a Lean model's `apply`; the Lean **replay** is `leanchecker --fresh` re-checking a
    package's terms. Forensic replay (ADR-0020) is a fourth, of the record.
36. **"Stage": three things.** The floor stages; the cell's stages (the Listener and the Reader); and the stages of the
    refinement chain. A Lean result is not a stage of the chain.
37. **"Budget": two.** The timing budget `W + L + D < T_irrev` (ADR-0032 §4) and a mesh's activation budget `N`
    (ADR-0055 §2).
38. **"Unsound": the prover's, not the design's.** The two unsound cases are of `tlapm`'s translation (T-0045-31); a
    proof is kept from them by a rule and a scan. Nothing in the term is a claim that a TLA+ module is wrong.

---

## 14. Retired wording

Rows added since 09.17 come first. The 09.17 table (CI/Orch, "semantic containment", the ladder, "immutable",
crypto-shredding as mechanism, Kafka as system of record, "strictly stronger than Moon & Varshney", the `L`/`D` swap,
§4.2 → §4.6, "Varshnay") still stands.

| Retired | Replacement | Authority |
|---|---|---|
| `bundle ⊑ floor` decided at promotion, by SMT over Rego | A property of composition, for every bundle | ADR-0030 §1 |
| O = OPA and Rego | O = a verified floor evaluator plus a bundle engine | ADR-0030 §2 |
| `quorum = "any"` | A threshold *k*, with R9 keeping *k* ≥ 2 | ADR-0024, ADR-0026 |
| Recusal as an issued value; R3 | A mechanism constant in the `Vote` envelope; R3 withdrawn | ADR-0024, ADR-0026 |
| Relaxing recusal is a mechanism release | A policy-floor relaxation: issuance and promotion | ADR-0022 A1 |
| `W < L < D` as the safety property | `W + L + D < T_irrev` per effect class; the ordering is a magnitude description | ADR-0032 §4 |
| "Proved", "proven" | "Checked", "must hold" | G3 §8; CR-25 |
| "The bootstrap set gets no independent review, ever" | Reviewed at the bootstrap gate with the whole corpus | ADR-0029 A2 |
| `Resign` "defined nowhere" | Defined per custody rung | ADR-0025 annex |
| Lease attenuation, lease rank, fence token **[S]** | Renewal only narrows; fence = Paxos log index at grant | ADR-0031 |
| Asymmetric margin **[S]** | A local monotonic clock with a margin that errs early | ADR-0032 |
| Confinement rungs, *Contested* **[S]** | Attestation rungs 0–3, *Contested* | ADR-0031 §3; ADR-0034 (Proposed) |
| One epoch fence for every revocation | Targeted revocation plus epoch fence | ADR-0031 |
| "Clock model: unstated" | Stated | ADR-0032 |
| Denials not recorded | Recorded, unordered, as digests | ADR-0020; reference finding 11 |
| Monotonicity "at five layers" | Twelve layers | ToO rev 9 §7.8 |
| "Every lease the reference issues is rung 0" | Rung 0, rung 1 under the launcher's assertion, or rung 3 *SIMULATED* | ADR-0033 A7; G9 |
| "Channel fidelity has no owner" | The tool host's Wasm runtime, for Wasm-hosted tools; nobody, for native ones | ADR-0034 A2, ADR-0033 A8 |
| "The Run profile is unwritten" | ADR-0034 A2, in force | Batch 30 |
| "The correction waits for a successor module" (finding 6) | `Confinement_A1.tla`, checked and proved | G9 §2.3 |
| "Principals are agent LTROs"; the LTRO as one principal | An LTRO is a cell of principals; a principal holds one seat | ADR-0037 §1 |
| The Reader as a cognitive seat with its own Persona | A stage producing facts for the cell Observer | ADR-0037 §3; ADR-0018 B12 |
| "Human principals are atomic", as a contrast | Every principal is atomic; a human holds one seat | ADR-0037 §7 |
| The shared, orchestrator-level Observer group (~9 vs ~40 instances) | One `observer` seat per cell plus a correlator; any-of | ADR-0038 §1, §5; ADR-0008 superseded |
| "A Byzantine quorum of co-resident replicas is arithmetic fiction" as the placement reason | Correlated failure and a device-memory effect path; there is no Observer quorum | ADR-0038 §4, §5 |
| Veto seats held by "the independent Observer replicated group" | Every cell Observer and correlator seat in Build | ADR-0024 A2.1 |
| "An unavailable Observer vetoes nothing" as the accepted state | An absent Observer stalls: coverage and an independent veto seat are tally constants | ADR-0024 A2.2, A2.3; ADR-0039 §3 |
| Detection fails open, unstated | Coupled in Run and at the Build gate; fails open against collusion only, declared | ADR-0039 |
| `seq − mark ≤ K` | `seq − mark < K`, the strict form | ADR-0039 §1 R5 |
| R3 on every uncovered Run emission | R3 under a `thinker` seat only | ADR-0039 §2 R5 |
| "The rung-0 verdict is computed from nothing" | A rung-0 grant may name a profile; the verdict is then derived, and *declared* | ADR-0036 R1 |
| The floor as two files | Three: policies, schema S, the values file | ADR-0039 §1 R3 |
| "Renewal may lower the rung" | Renewal keeps the rung | ADR-0031 A1 |
| The cross-principal correlator as "a noun" | A seat kind, a placement, a veto seat and a read set; still no detection function | ADR-0038; G5 item 43 |
| `RunInvoke`, `RunEmit` | `Consult`, `Actuate`, `Report`; no name shared between the domains | ADR-0040 §1, §2 |
| "`Read`, `Emit` and the carrier are common to Build and Run" | The carrier is common; no variant name is | ADR-0022 A2 |
| "Run's alphabet: no record defines it" | ADR-0040, with ADR-0041 to ADR-0043 for its obligations | Batch 20 |
| The sequence as the emission counter, in Run | The sequence counts effect-bearing admits; `Consult` advances nothing | ADR-0039 A1; ADR-0042 §2 |
| R3 on every Run admit | R3 on `Actuate` and `Report`; `Consult` exempt, on the pinning | ADR-0041 §2 |
| "No tiered storage" read as a retention length | One store for the topic's whole retention; length per use and per domain | ADR-0003 A3 |
| ADR-0021 "stays Proposed" | Ratified, Batch 18 | G6 §1 |
| "TCB declaration record: unwritten" | ADR-0045, in force, with an admission rule and thirty rows | ADR-0045; Batch 22 |
| "ADR-0045, Proposed" · "the binding table does not exist" | Accepted (genesis), C2 and C4; forty-two rows, DRAFT | Batch 22; ADR-0045 R6 |
| "The solver is trusted" · "every gate run is D-0030-2" | A `holds` counts only with a proof the pinned checker accepted; D-0030-2 is a run without the checker | ADR-0030 A1, Batch 24 |
| "Not yet read by the reference" (`T_persona`) | Refused at grant and renewal | ADR-0033 A6 |
| "Write the solver's row; do not try to verify cvc5" | The solver is refused; a `holds` verdict counts only with a checked proof | ADR-0045 §6; ADR-0030 A1 |
| "The admit path, the tally and the log are checked, not trusted" | True of the specification; what runs is a trust-root row | ADR-0045 R1 |
| "Persona expiry: open" | `ttl ≤ T_persona` | ADR-0031 A2 |
| "Bundle signing: open" · "the implementation owed" | A record in force and implemented at the reference under a dev key | ADR-0044; ADR-0033 A6 |
| The reference "checked only by restated tests" | Every tested behaviour replayed through the operational model | ADR-0033 A5 |
| Monotonicity "at twelve layers" | Fourteen: bundle and trusted base | ToO rev 10 §7.8 |
| Dated glossary and ToO copies after revision 9 | A head file, a commit and a tag | The 2026.09.30 reorganization |
| "No theorem is proved" | Thirteen modules' invariants proved under named hypotheses; mutations and witnesses checked | ADR-0046; Batch 25 |
| "Proved" retired; say "checked" | *Proved* for what the prover discharged, with its hypotheses; *checked* for TLC | ADR-0046 §1 |
| "MAP 2.3: TLC versus TLAPS undeclared" | Declared | ADR-0046 |
| The trusted base's "thirty rows" | Thirty-one: T-0045-31, the prover | ADR-0045 B25 |
| `SealCountsEffects` breaks under `M_ROUNDS` | Under `M_EMITSEQ` | ADR-0046 §5 |
| `K < R` as a premise of the unread bounds | Not a premise; it is what lets the bound refuse | ADR-0046 §5 |
| `M_OBSEMIT` breaks `RunSeats`' invariants | It breaks none of them | ADR-0046 §5 |
| Two bootstrap modules "drafted and checked" | Drafted, checked and proved | ADR-0029 B25 |
| Two floor exceptions: erasure and break-glass | One: erasure | ADR-0013 A1; ADR-0052 (provisional) |
| `X1-break-glass`; a break-glass approval scoped to a seat and an epoch | An emergency seating, activated for one person and one round | ADR-0052; ADR-0041 A2 |
| "A bundle can narrow break-glass" | The envelope is an ordinary allowlist; the label forbids apply under it | ADR-0052 §2 |
| R8, the break-glass TTL, "drafted, pending" | Withdrawn; the grant ends with its round | ADR-0026 W1 |
| R6 "currently two" · R7 "no break-glass grant may authorize…" | The count is one · no activation grants an alphabet holding an authority act | ADR-0026 A2 (provisional) |
| "R3 applies to break-glass too" | An emergency seat is not coupled | ADR-0039 A2 |
| The `breakGlass` flag in the `Actuate` record | `seatKind` | ADR-0042 A2 |
| "The operator" as whoever reaches the socket | A principal on an `operator` seat; the socket is the BOOTSTRAP path, for a first seating only | ADR-0050; ADR-0033 A11 |
| Three seat kinds | Five: `emergency` and `operator` added | ADR-0037 A3, A4 |
| Run's ingress as three items | Four, each with a label: the tool list added | ADR-0043 A1; ADR-0048 |
| "The Listener delivers and makes no choice", with nothing said of where content came from | It labels by source and delivers clear or as a handle, by table | ADR-0047; ADR-0037 A2 |
| A Thinker learns its tools from its Persona or its task | From the tool list, the only description with standing | ADR-0048 §3 |
| "The allowlist entry's schema: open" | ADR-0049: five parts, each field checked or claimed | Batch 34 |
| A Run tool's channel declared in the entry and in node configuration | In the entry only | ADR-0033 A9 |
| "ADR-0005, Proposed" · "Kafka is a debt against it" | Accepted (genesis), C4 | Batch 27 |
| "ADR-0042 §6, the one Proposed section of the Run records" · "the Run profile is drafted, pending" | In force; ADR-0042 accepted whole | Batch 30 |
| "(ADR-0033 A7, pending)" · "(A8, pending)" | Ratified; no amendment is pending | Batches 29, 31 |
| "The correlator's detection function is unspecified" | Drafted: ADR-0051, Proposed | G10 item 43 |
| "Floor fitness is unowned" | Owned by the bootstrap reviewer and timed at bootstrap; no test | ADR-0029 A4; ADR-0030 A3 |
| "The genesis floor … the mechanism compiles it in" | The reference links the `emergency` stage; the floor is genesis-provisional | ADR-0030 A3; G10 §2.2 |
| "Thirteen of the fourteen modules are proved" | Twenty-two proof modules, 5,225 obligations; nineteen certified | ADR-0046 A1; G10 §2.9 |
| "The SMT backends' proofs are not rechecked" | Checked by `ethos` in the certified configuration, for nineteen modules | ADR-0046 E2, A1 |
| The trusted base's "thirty-one rows" | Thirty-six | ADR-0045 A1, A2 |
| Monotonicity "at fourteen layers" | Sixteen: ingress and operation | ToO rev 14 §7.8 |
| Accepted or Proposed, and nothing between | *Accepted (genesis) · provisional*: in force and subject to redesign | ADR-0029 A4 |
| "Twenty-two proof modules, 5,225 obligations; nineteen certified" | Twenty-four, 5,416; twenty-one certified | ADR-0046; G11 §2.9 |
| The trusted base's "thirty-six rows" | Thirty-seven: T-0045-37, the Lean toolchain | ADR-0045 B36 |
| The prover's translation as merely unexamined | Known to be unsound in two ways; a rule and a scan keep a proof from them; no check for the first | ADR-0046 A2; ADR-0045 A3 |
| "Isabelle refuses one of `RulesFloorNV_rev5`'s Zenon proofs" | All five; tlapm reports the first | ADR-0046 E4; ADR-0053 E1 |
| "No module states liveness" | Two liveness extensions; coupling's leads-to properties checked by TLC and not proved | G11 §3 |
| "The `emergency` stage is the text the reference compiles in" | The floor in force; the reference links the `workflow` stage, which is not | ADR-0033 A16 |
| "No amendment is pending" | Twelve, every one on a Proposed record | G11 §1.1 |
| "Cells communicate through the record", unspecified | Along a promoted workflow's edges, Proposed; between cells no workflow joins, not at all | ADR-0054 |
| The refinement chain's Lean stage "not begun", with no Lean in the corpus | Still not begun; code-level proofs in Lean are evidence toward T-0045-28, not a stage | ADR-0053 §5 |
| A workflow node's `denials` attribute | Dropped: a denial is never ordered | ADR-0054 R6; ADR-0033 A17 |
| Monotonicity "at sixteen layers" | Eighteen: workflow (Proposed) and evidence of proof | ToO rev 15 §7.8 |

---

## Sources

**Basis.** `checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md` · `narrative/theory-of-operation.md` at tag
`ToO-rev15` · the records they cite, at their G11 digests.

**Superseded.** This file's previous revision (tag `glossary-2026.10.05`, the head `manifests/SHA256SUMS-G11`
measured), before it the second 2026.10.02 revision (tag `glossary-2026.10.02b`, measured by `manifests/SHA256SUMS-G10`),
the first 2026.10.02 revision (tag `glossary-2026.10.02`, measured by `manifests/SHA256SUMS-G9` at its commit), the
2026.10.01 revision (tag `glossary-2026.10.01`, measured by `manifests/SHA256SUMS-G8`), the 2026.09.30 revision (tag
`glossary-2026.09.30`, measured by `manifests/SHA256SUMS-G7`), the 2026.09.29 glossary
(`derived/topak-glossary-2026.09.29.md` before the reorganization, measured by `manifests/SHA256SUMS-G6`), and through
it the 09.26 and 09.17 glossaries whose §12 is carried by reference.
