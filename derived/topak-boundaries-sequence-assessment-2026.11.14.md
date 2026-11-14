# TOPAK — Read Against Critch's «Boundaries» Sequence

**2026.11.14** · derived · a reading, not a record · basis: the sixty-eight record files under `decisions/` at commit
`bb76b46` (2026.11.12), nineteen of them Proposed, with Theory of Operation revision 15
(`narrative/theory-of-operation.md`) and `derived/topak-boundary-register-2026.09.13.md` · read against Andrew
Critch's «Boundaries» sequence on LessWrong (four posts, 2022.07.26 to 2022.12.14;
<https://www.lesswrong.com/s/LWJsgNYE8wzv49yEc>) · the state of record is Genesis Checkpoint G11, and this document
reads the whole tree, Proposed text included, and says of each row which it rests on · prepared by the assistant at
the custodian's request

Nothing here is ratified, and this document proposes no decision text. Where it suggests an entry, none is made.

**Sources.** The sequence was read through a fetch, not from bytes held in the tree, and no digest of it is recorded
here. Parts 1, 2 and 3b came from lesswrong.com; Part 3a did not render there and was read from the GreaterWrong
mirror. The post bodies were read in full; the comment threads only in summary, so nothing below rests on a comment.
The sequence promises a part on existential risk that had not been posted when it was read. The corpus does not cite
the sequence, Critch, Markov blankets or corrigibility anywhere in its Markdown, by a search of the tree.

**Method.** Six readers, each a fresh context with a fixed brief, read the sixty-eight record files in full in six
tranches and reported against eight claims and seven claimed correspondences, with quotations. The lead wrote this
document from their reports. **Every quotation of a record below was then checked mechanically against the record
file it is cited to**, whitespace and emphasis markers aside. The quotations of the sequence could not be checked
that way and are the fetch's. `spec/`, `floor/`, `policies/` and `mechanism/` were not read for this document:
where it says *built* or *not built*, that is what ADR-0033 and its addenda say of the reference, not a run.

**What the full read corrected.** A first pass over the Theory of Operation and the boundary register alone got four
things wrong: that parties outside the deployment have no standing, that nothing bounds how much an agent does, that
same-lineage principals are counted as separate, and that an agent has no interior the design leaves alone. Each is
answered by a record. Two of the answers were in force all along, in records the first pass did not open (ADR-0016,
ADR-0020). Two rest on Proposed records, most of them drafted after revision 15 was cut (ADR-0055, ADR-0056,
ADR-0062, ADR-0063). The narrative under-reports the corpus by its Proposed set, which is the 11.11 review's
finding in another form.

**Not independent.** This is the drafter's reading of the drafter's work, by readers of the drafter's lineage. It
does not count under ADR-0029 A2, gives no verdict on floor fitness and dispositions nothing.

---

## 0. Verdict

The sequence argues that a living system is constituted by a boundary it maintains, that the boundary is best
defined by information flow and not by anyone's preferences, and that several alignment problems are questions about
which boundaries are respected and how one is opened. **TOPAK is an independent and unusually complete answer to
the half of that argument that concerns the boundary around an AI system, and a partial, mostly Proposed answer to
the half that concerns everyone else's.**

Three things hold across the whole corpus.

1. **On definition the corpus agrees with the sequence and is stricter.** Its premise, that an agent is Byzantine and
   that no guarantee may rest on what a model means, is the sequence's "define boundaries in terms of information
   flow, not preferences" taken as an engineering rule. It also has things the sequence does not: a temporal account
   of each boundary, a rule for what may sit inside the trusted base by the direction its failure takes, and a
   distinction between a boundary that is checked and one that is claimed (§4).
2. **The boundary is a design and not yet a fact.** The sequence's test is whether separation actually holds. By the
   corpus's own text no real principal is `Contained` (§3, BD-1).
3. **The boundaries of people are where the corpus is thinnest, and it says so.** It bounds what a person in a seat
   can do. It does not protect what that person comes to believe, and the sequence's most-asked-for problem,
   preference plasticity, has no record (§3, BD-2). The corpus's consent rules protect human key-holders and nobody
   else (§5).

---

## 1. The sequence, as seven tests

The sequence is four posts. Part 1 argues that bargaining theory lacks a canonical disagreement point and that a
protected boundary supplies one. Part 2 reads seven trends in a community as failures to establish, respect or
properly cross boundaries. Part 3a defines a boundary as an "approximate directed (dynamic) Markov blanket": a
world factored into environment, viscera, and a boundary with an active side the viscera control and a passive side
the environment controls, with *infiltration* and *exfiltration* measured as conditional mutual information. Part 3b
restates eight alignment problems in those terms. Read for what a design could be held to, it asks seven things.

| | Test | Where the sequence says it |
|---|---|---|
| **S1** | A boundary is defined by information flow, not by what the bounded system prefers | Part 3b, boxing |
| **S2** | The boundary is directed, with an active and a passive side, and separation is approximate and measured | Part 3a |
| **S3** | Authority is scoped: a goal and a scope, the scope a constraint on the process and not a term in the objective; "enough" sustains a system and "too much" crosses another's boundary | Part 3b, scoped consequentialism, mild optimization |
| **S4** | A corrigible system opens its boundary to correction and does not interfere with the corrector's own decision; a person's preferences change under influence, and that needs an account | Part 3b, corrigibility and preference plasticity |
| **S5** | A party has a protected place to walk away to, so that disagreement has a defined outcome | Part 1 |
| **S6** | Other systems' boundaries are established where warranted and crossed by a good procedure; distributed processes are preferred to unilateral acts; deciders that decide alike share one boundary | Part 2; Part 3b, counterfactuals |
| **S7** | An optimizer that does not specifically respect a boundary will tend to violate it; an abstraction is a boundary feature and can be broken | Part 3b, mesa-optimizers |

---

## 2. Where the corpus meets the sequence

*In force* means Accepted (genesis); every such record was ratified by one person, most carry a
confirmation-required marker, and ADR-0050 and ADR-0052 are provisional. *Proposed* is not in force. *Overlay* is ADR-0059 to ADR-0068, Proposed, the
command-chain overlay and not the archetype.

| Test | What the records say | Record · standing |
|---|---|---|
| **S1** | ADR-0007's title is the rule: "Semantic judgment is never a lift". The design is to "verify the cage, not the occupant", and "A passing evaluation can never admit a Persona". Reading a confinement clause as intent is rejected: "The clause is about reachability" | ADR-0007, ADR-0016 in force; ADR-0036 Proposed |
| **S1** | A label is computed from a source and "No model computes one". An Observer's judgment is deny-only: "No Observer judgment enters the admit path" | ADR-0047, ADR-0039 in force |
| **S2**, active side | Build's alphabet is "Egress only"; Run has "exactly three variants". A request for live state is an effect "because the request itself leaves the membrane" | ADR-0022, ADR-0040 in force |
| **S2**, passive side | The Listener's delivery is closed: "That list is the Thinker's whole ingress". Since Batch 34 it is filtered as well: an item arrives clear or as a handle, and the agent is told, because otherwise "The Thinker cannot tell a withheld item from a missing one" | ADR-0043, ADR-0047 in force |
| **S2**, crossing without reading | "The Thinker routes content it cannot read": a handle passes through the agent to a tool. It is the nearest thing in the corpus to the sequence's non-violent crossing (the lead's reading) | ADR-0047 in force |
| **S3** | The lease: "Every field is an authority claim, and the set is closed". A bundle can only narrow: "A bundle is never asked whether to grant, only whether to refuse" | ADR-0031, ADR-0030 in force |
| **S3**, quantity | A workflow's promotion "grants at most `N` leases". Under the overlay "The count is exact", and "Without an extent a count bounds nothing" | ADR-0055 Proposed; ADR-0062 overlay |
| **S4**, first half | A principal is what can be evicted, and "Resignation is not eviction". Granting takes a quorum and denying does not: "Consensus for grants, local for denials". The stop is itself guarded: "No operator can undo a peer's deny" | ADR-0002, ADR-0010 in force; ADR-0050 provisional |
| **S4**, the corrector's record | The agent does not write the record its overseer reads: "The principal does not write it and cannot" | ADR-0042 in force |
| **S5** | The floor is resident, with "No process, no socket, no fetch", and "Anchor unavailability blocks change, never operation". A refused agent keeps its place: "The Thinker waits; it is not evicted" | ADR-0030, ADR-0027, ADR-0039 in force |
| **S6**, procedure for crossing | A floor change that cannot be classified is treated as the stricter kind: "Incomparable: routed as a relaxation". One crossing is refused outright, ADR-0013's "Demand type 5" | ADR-0030, ADR-0013 in force |
| **S6**, distributed authority | "No strict subset of grant seats can promote", and "This quorum cannot change its own rules" | ADR-0024 in force |
| **S6**, like deciders | A cell's Observer "must differ from the Thinker's by lineage, not merely by configuration". The proposed relation is not reflexive: "nothing is independent of itself" | ADR-0016 in force; ADR-0035 Proposed |
| **S6**, peers | "Nothing a peer originates is ever an enabling condition", and "A stack reports to a topic and names no recipient" | ADR-0065 overlay |
| **S7** | The threat is placed in Build, where the rules are written (the narrative's inversion, revision 15 §1). The orchestrator "affects how good the work is and never whether it is safe". A deployed system's output returns only through intake: "Run does not adapt" | ADR-0054, ADR-0069 Proposed |

Three corrections to how the correspondence is usually put, each from the records.

- **A denial is not local.** It needs no quorum, and ADR-0010's phrase is still quoted, but ADR-0031 strikes "local,
  no consensus" and says of both revocation tools that "both are consensus-ordered".
- **The cell is not the organism.** The bounded unit is the principal. The Thinker and its Observer are two of
  them, and the passive side of the Thinker's boundary is the mechanism's, which is where the sequence puts it.
- **The stall is not always the safe fallback.** ADR-0062 says that the sentence "A stall that never ends is safe"
  "is false of a vehicle in flight", and replaces it there with a voted terminal behaviour.

---

## 3. Where the sequence asks for something the corpus lacks

Eight items, in the order the lead would weigh them. Each says whether a record already names the gap. **BD** is
this document's tag and no other document's.

**BD-1. The boundary is specified and not real (S2).** ADR-0034: "`Contained` has no members at any rung". ADR-0036:
"Nothing is `Contained`". At the reference "`contained = true` is reached only in a SIMULATED rung-3 run, under test
keys", "whoever reaches the socket can seat", and "cells are declared, not enforced". The corpus names all of this.
In the sequence's terms infiltration and exfiltration are nonzero and unmeasured for every real principal.

**BD-2. Nothing protects what a person in a seat comes to believe (S4).** No record treats persuasion or a change of
preference. For voters: "Correlated review failure is untouched" (ADR-0024), and under workflows "The `Report` gap carries
weight" (ADR-0054). For operators the open item is "What a peer must have read
before an add proceeds" (ADR-0050), and what is trusted of them is "nothing of their judgment" (ADR-0045). `Report`
is unconstrained: "`Report` takes `clearSet` and no entry reads it yet" (ADR-0041), and ADR-0047 "does not cover an
injection that changes what a Thinker says in a `Report`". The overlay goes furthest and then stops: an agent's
report to a release seat "is ingress to the person, labelled `untrusted`, and it enables nothing", countersigning
was not taken because "approval can become a click", and the record still owes "What a person at a release seat must
be shown". ADR-0068 states the residual: "A deceived person at a release seat is a semantic failure. Nothing here
sees it". Named in every case; owned in none.

**BD-3. The second half of corrigibility is met only by structure (S4).** An agent cannot reach the control
alphabet, cannot write its own record, and cannot turn its revocation into work for the mechanism. Nothing addresses
an agent shaping the decision to correct it through what the corrector reads. ADR-0052 declines to model a reason at
all: "The reason is unknown to the mechanism, by construction". One mitigation is structural and real: denials
combine by any-of, so influence has to succeed against every denier (the lead's inference). ADR-0069 names the
long loop, an agent shaping its successors: "What it adds is a path for influence".

**BD-4. Bystanders have no boundary the records see (S3, S6).** Confinement checks the channel and not its use:
"Channel fidelity is about which channel, not what is said on it". The floor "bounds which tools. It does not bound
their arguments". For the overlay, "the charter has no field for an envelope in the world", identification, necessity
and proportion are "enforced by nothing in this set of records", and "What the vehicle's body does that no entry
names is outside the alphabet". The sequence's "too much", crossing an existing system's boundary, has no
counterpart for a party that is neither a user, a downstream system nor a data subject (§5).

**BD-5. Information flow is bounded per round and declared, not measured (S2).** `clearSet` is "a bound on the
round, not a trace of a value", and "Across rounds it is not a bound at all" (ADR-0051, finding 2): a tainted cell
writes to an inside store and a clean one reads it. "Seven of the entry's fields are claims" (ADR-0049). Side
channels are residual by name in ADR-0034. Nothing in the corpus is stated in information terms; the only measured
fit between a rule and what runs is trace validation, and "A matching trace is not a refinement".

**BD-6. Collusion between like deciders is open (S6).** Coupling "cannot separate an honest Observer from a
colluding one" (ADR-0039), and the overlay repeats it: "Coupling cannot see collusion". The cover is ADR-0035, which
is Proposed, unmeasured, and modest about itself: "structural independence does not imply uncorrelated failures",
and "A pass grants nothing". Across cells the corpus counts like deciders separately on purpose: "Two `thinker`
seats on one Persona are two principals in two cells, and this is permitted".

**BD-7. The caps are ceilings and say nothing of sufficiency (S3).** The activation budget, the charter's budget,
the exact count and extent, and the bound on outstanding effects are all Proposed, and each is an exposure limit
voted in advance. None is tied to what the task needs, so none is mild optimization in the sequence's sense (the
lead's reading). In force there is less: the round bound, the count `K`, and a timing budget of which ADR-0032 says
"`L` is unmeasured" and "nothing in the corpus enumerates effect classes that way yet". ADR-0039 on its own
constants: "None is measured".

**BD-8. An agent has no say over its own boundary (S4).** It cannot refuse eviction and cannot leave: "The principal
cannot end its own round" (ADR-0042). A guest "is launched for the grant and destroyed when the round ends"
(ADR-0034). This is the Byzantine premise doing its work and not an oversight. It is recorded here because the
sequence's subject is boundaries that systems maintain for themselves and open by their own decision rule, and the
corpus gives that to people in authority and to no agent (§5).

---

## 4. Where the corpus holds something the sequence lacks

- **Time is an axis across every boundary.** The boundary register gives each boundary a cadence, an instant at
  which it is checked, an interval during which it is untrue, and a behaviour when the check cannot run. The
  sequence allows that boundaries are permeable over time and gives no account of when one is true.
- **Failure direction decides what may sit inside.** "A component is a row only if its failure can only subtract, or
  its identity is issued" (ADR-0045). It is a rule for admitting something to the trusted side of a boundary without
  trusting its intent, and the sequence has no counterpart. ADR-0034 uses it as "Delegate by failure direction".
- **Checked and claimed are told apart.** ADR-0049 marks each field of a tool's entry as one or the other. The
  sequence's boundary is either a good fit or not; the corpus says which parts of the fit rest on a declaration.
- **Permeability is paid for.** A table that delivers more to the agent in the clear "buys a narrower round":
  what comes in is traded against what may go out, per round. The sequence describes boundaries opening and closing
  and gives no exchange rate.
- **Changing a boundary has a direction and a price.** Tightening is an ordinary promotion and relaxing takes two
  keys; a confinement change is refused if it would be a "silent downgrade". This answers a criticism raised under
  Part 1, that some boundaries are spurious and need a way to be moved.
- **The boundary's own evidence is kept.** Replay "reconstructs what crossed the membrane, not what happened inside
  it", and denials are retained as events. The limit is stated with it: the record shows "what a principal did and
  never why".
- **The overseer is bounded too.** "A Byzantine Observer can deny, quarantine or evict inside its reach and nothing
  more" (ADR-0038).

---

## 5. Whose boundary

The sequence treats boundaries as belonging to living systems on both sides of an interaction. Read party by party,
the corpus protects some boundaries by mechanism, some by consent, and some not at all.

| Party | What the records give it | What they do not | Standing |
|---|---|---|---|
| **Agent** (Thinker) | An interior nobody records (ADR-0020); a filtered and honestly described passive side (ADR-0047); at rung 3, integrity against the host by design (ADR-0034) | Refusing eviction; ending its own round; surviving the round | In force; rung 3 simulated |
| **Observer** | Bounded reach; a facts-only narrowing for the correlator | Protection from what it must read: "Suppressed to the Thinker is not suppressed to the Observer", and "An injection that turns a Thinker may turn its Observer" | In force |
| **Operator** | A stop no peer can undo; peers who observe each other | Anything about what it reads; the peer check "reads presence and not progress". It is treated as havoc: "Nothing below rests on an operator being honest" | Provisional |
| **Person in an emergency seat** | Labelled ingress, and the label forbids bind the person, who "takes a destination from a handle like anyone else"; "The person acts, and no agent does" | An Observer of their own; a model of why they act | Provisional |
| **Person in a release seat** | An agent's report arrives labelled `untrusted` and "enables nothing" | What they must be shown; detection of deception | Overlay |
| **Grant-seat voter** | Gates that run first, "Gates enable voting; they do not vote"; a vote bound to an evidence digest | Independence of the evidence from the author; anything on persuasion | In force |
| **Anchor key-holder** | Consent to being constrained, "so the anchor must consent to it" (ADR-0026); and to removal, "No key-holder is removed without their own consent" (ADR-0025) | A bound on intent: "No safety theorem covers anchor intent" | In force |
| **User** (a call's subject) | "A user who is not present at grant cannot be acted for", and "an operator cannot act as an arbitrary user" | "A subject's consent", beyond a provider's signed assertion | Proposed |
| **Downstream system** | Its own authorization, left to it: the row is "excluded, and that is the position, not a gap" | Any check on what a call does once it is admitted there | Proposed |
| **Data subject** | Erasure "per subject, at arbitrary times, provably" (ADR-0003); "Erasure follows the data" into promoted artifacts (ADR-0069) | A say before the content is read | In force; ADR-0069 Proposed |
| **Peer stack** | Nothing a peer sends can enable anything | A boundary of its own against a peer's reports, beyond the label | Overlay |
| **Bystander, and the world** | A record that an effect happened | Everything else (BD-4). "The effect may still have happened" (ADR-0042) | In force |

Two patterns stand out. **Consent to one's own constraint or removal belongs, in the records, to one kind of
party: an anchor key-holder** (ADR-0025, ADR-0026; by a search for the word, which otherwise finds only ADR-0056
naming a subject's consent as not covered). And **the two parties with the least protection are the ones farthest from the mechanism in opposite
directions**: the person whose judgment the design finally rests on, and the bystander it never names.

---

## 6. Suggested entries, none made

Offered in the order of §3. Each is a place where a record already names the gap, so each is a matter of ownership
before it is a matter of design.

1. **A display record for human seats (BD-2).** ADR-0066 owes what a release seat must be shown. The same question
   stands for grant seats and operators, and one record could state it for all three: what a person is shown, with
   what label, from which author, before an act of theirs counts. The label machinery of ADR-0047 already reaches a
   person in an emergency seat.
2. **A floor entry that reads `clearSet` on `Report` (BD-2, BD-3).** ADR-0041 says the attribute is delivered and
   unread, and ADR-0047 lists it as open. Whether an entry should exist is the custodian's.
3. **An envelope in the world as a charter field, and its archetype counterpart (BD-4).** ADR-0059 names the missing
   field. In the archetype the nearest hook is that a bundle's label vocabulary is its own, so a deployment could
   declare whose system a channel reaches; nothing asks it to.
4. **The cross-round path (BD-5).** ADR-0051 finding 2 is covered only by detection that is Proposed and
   after the fact. A label on an inside store's contents, joined from its writers, would make it a bound.
5. **A sentence in the residual-risk statement for BD-2 and BD-4**, when it is next regenerated: that the design
   bounds what a person in a seat may do and not what they are led to believe, and that a party outside the
   deployment who is not a user, a downstream system or a data subject appears in no record.

Not suggested: anything for BD-8. Whether an agent should hold any boundary of its own is outside the premise, and
the sequence's own author treats too-well-defended boundaries around an AI system as the failure.

---

## 7. What this reading does not show

- **It is a reading against one author's early programme.** The sequence calls itself incomplete, its formal part
  gives no way to estimate the quantities it defines, and by the fetch's summary a commenter on Part 3a disputes
  the active and passive factorization itself. A design that met all seven tests would not thereby be safe.
- **The correspondence is the lead's.** No record was written with the sequence in view, and every mapping in §2 is
  an interpretation. Where a mapping is an inference and not a quotation, the text says so.
- **The records were read, and the artifacts were not.** Nothing here checks that a module, a floor entry or the
  reference does what its record says. The 11.11 review is the document that ran things.
- **Six readers of one lineage read it.** A claim that all six missed is missed here.
- **The standing of a row is as the record files state it at `bb76b46`.** The state of record is G11, which predates
  fourteen of the nineteen Proposed records; where the two differ, the checkpoint wins for what is in force.
