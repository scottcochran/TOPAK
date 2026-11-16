---
id: 1982-GAM-BYZANTINE-GENERALS
title: The Byzantine Generals Problem — more than two-thirds loyal with oral messages, any number with signatures
kind: canonical
date: 1982-07
sector: game-theory
setting: Agreement among replicated processors some of which are faulty, posed as generals of the Byzantine army communicating by messenger; Lamport, Shostak and Pease, SRI International, ACM TOPLAS 4(3)
concerns: [consensus, quorum, timing, identity, collusion, sensing]
rules_at_time:
  - document: Lamport, Shostak and Pease (1982)
    clause: "§3, A1–A3"
    paraphrase: every message sent is delivered correctly; the receiver knows who sent it; the absence of a message can be detected
  - document: Lamport, Shostak and Pease (1982)
    clause: "§4, A4"
    paraphrase: a loyal general's signature cannot be forged and any alteration is detectable, and anyone can verify it; a traitor's signature may be forged by another traitor, so traitors may collude
analogue:
  - record: ADR-0061
    clause: "§1, §2"
    note: seven replicas tolerating two captured, certificate five; PBFT named as the instrument, with three statements about it "recalled, not re-read"
  - record: ADR-0059
    clause: "§5"
    note: a crash-recovery protocol cannot supply a certificate a third party checks, so a plane whose replicas can be captured runs Byzantine agreement
  - record: ADR-0045
    clause: "T-0045-1"
    note: the archetype's replicas are crash-fault only, a trust root whose residual is the forged admit; "BFT is not required by this record"
  - record: ADR-0065
    clause: "§1"
    note: a stack's report is delivered as untrusted ingress and enables nothing; a certified fact relayed by a peer is the plane's act, and the peer originates nothing
actors:
  - party: Leslie Lamport, Robert Shostak and Marshall Pease (SRI International)
    role: investigator
    fault: none-alleged
    note: authors
  - party: The traitorous commander (Fig. 2)
    role: controller
    fault: byzantine
    note: sends "attack" to Lieutenant 1 and "retreat" to Lieutenant 2
  - party: The traitorous lieutenant (Fig. 1)
    role: peer
    fault: byzantine
    note: tells Lieutenant 1 that the loyal commander said "retreat"
  - party: The loyal lieutenants
    role: peer
    fault: honest
  - party: Miguel Castro and Barbara Liskov (MIT)
    role: investigator
    fault: none-alleged
    note: PBFT (OSDI 1999), the form ADR-0061 names
detection:
  means: [researcher]
  latency: not-applicable
trace:
  - step: outside:commander-equivocates
    at: Fig. 2, three generals, one traitor
    note: the commander sends "attack" to Lieutenant 1 and "retreat" to Lieutenant 2
  - step: outside:lieutenant-relays-oral-report
    at: Fig. 1 and Fig. 2
    note: an oral message is "completely under the control of the sender"; Lieutenant 1 cannot tell Fig. 1 (traitorous lieutenant) from Fig. 2 (traitorous commander)
  - step: outside:loyal-lieutenants-diverge
    at: Fig. 2
    note: Lieutenant 1 attacks and Lieutenant 2 retreats, violating IC1; no three-general solution tolerates one traitor, and none with fewer than 3m + 1 generals tolerates m
  - step: Deliver
    at: the same relay in ADR-0065's terms
    note: Peer.tla; a stack's report arrives labelled untrusted (ReceivedIsUntrusted) and PeerAddsNothing says it enables nothing. The overlay does not ask a governor to decide on what a peer says
  - step: RelayFence
    at: SM(m)'s relay in ADR-0065's terms
    note: Peer.tla; a peer forwards a certified item it cannot alter, as a lieutenant countersigns and forwards a signed order under A4
  - step: Sign
    at: a step of an autonomous plane's membership
    note: Membership.tla; an honest replica signs at most one step per membership. Without that rule (M_TWOVOTES) an honest replica equivocates as LSP's traitor does, and two successors follow
  - step: Order
    at: the step's certificate
    note: Membership.tla, at five replicas (f = 1, certificate 4); captured replicas sign anything, and AtMostOneSuccessor holds because two certificates share an honest signer
outcome:
  by: Lamport, Shostak and Pease (1982); Castro and Liskov (1999) for the asynchronous form
  date: 1982-07
  summary: >-
    With oral messages the problem is solvable if and only if more than two-thirds of the generals are loyal: no
    solution with fewer than 3m + 1 generals copes with m traitors, and OM(m) solves it with more than 3m. With
    unforgeable signed messages SM(m) solves it for any number of traitors (vacuous below m + 2 generals). Where not
    every general can reach every other, OM(m, 3m) works on a 3m-regular graph, and SM(m + d - 1) works if the loyal
    generals form a connected subgraph of diameter d. Both algorithms need message paths of length up to m + 1, which
    the paper attributes to Fischer and Lynch as optimal, and up to (n-1)(n-2)...(n-m-1) messages. A3 can be met only
    by a time-out, which needs a bounded delay and clocks synchronized within a fixed error; the paper states that no
    algorithm without an equivalent assumption can solve the problem, even if traitors can only fail to send.
  aftermath: >-
    Lamport's commentary says the paper's main purpose was to give the problem a new name, and, of the 1980 paper it
    builds on, that because the signatures were read as cryptographic the cheaper signed solutions were dismissed and
    3n+1 solutions stayed in use. Castro and Liskov (1999) give state machine replication that does not rely on synchrony for safety, with 3f+1
    replicas as the minimum for an asynchronous system to provide safety and liveness, independent node failures as
    an assumption, view changes that never select a different set of replicas, and signatures in the implementation
    only on view-change and new-view messages, with MACs elsewhere.
  effect_reversed: not-applicable
model:
  modules: [Membership, Peer, PlaneClock, Federation, proposed:ByzantineAgreement]
  properties: [AtMostOneSuccessor, StepByQuorum, OneSuccessor, PeerAddsNothing, ReceivedIsUntrusted, NoGrantPastExpiry]
  mutations: [M_TWOVOTES, M_MINORITYSTEP, M_PEERENABLES, M_SENDERLABEL, M_ONECLOCK]
  records: [ADR-0061, ADR-0059, ADR-0045, ADR-0065, ADR-0032, ADR-0064, ADR-0062, ADR-0024, ADR-0007, ADR-0068]
  findings: [TM3, TM4, TM5, TM8, TM12]
  fault_class: arbitrary faults among parties that must agree; one traitor confounds two loyal generals under oral messages
sources:
  - https://lamport.azurewebsites.net/pubs/byz.pdf
  - https://lamport.azurewebsites.net/pubs/pubs.html
  - https://www.read.seas.harvard.edu/~kohler/class/cs239-w08/castro99practical.pdf
verified: 2026-11-12
---

## Summary

Lamport, Shostak and Pease posed reliable computing as generals agreeing on a plan by messenger, some of whom are
traitors. A commanding general sends an order to n − 1 lieutenants, and an algorithm must give IC1 (every loyal
lieutenant obeys the same order) and IC2 (if the commander is loyal, every loyal lieutenant obeys his order).

In the paper's first scenario, with three generals, Fig. 1 has a loyal commander order "attack" and a traitorous
Lieutenant 2 tell Lieutenant 1 the order was "retreat". In Fig. 2 the commander is the traitor and sends "attack" to
Lieutenant 1 and "retreat" to Lieutenant 2. The runs look the same to Lieutenant 1, so a rule that satisfies IC2 in
Fig. 1 splits the lieutenants in Fig. 2. The authors call the argument informal: "we have seen equally plausible
'proofs' of invalid results". Messages are oral (A1–A3) or signed (A4). §6 applies the result to majority voting,
where a faulty input unit can give different values to different processors.

## Defensive position

**The authors' case for the algorithms:**

- OM(m) solves the problem with more than 3m generals, and that is the least number with oral messages.
- Signatures change the bound. "It is the traitors' ability to lie that makes the Byzantine Generals Problem so
  difficult", and SM(m) copes with any number of traitors. A4 lets traitors forge each other's signatures, so
  collusion among traitors is assumed, not excluded.
- A failed communication line can be counted as a failed processor; under A4, SM(m) is insensitive to line failure.
- The same message must never be signed twice, so sequence numbers should be appended.

**Castro and Liskov** argue that a protocol whose safety does not depend on synchrony is practical: their BFT file
service ran about 3% slower than an unreplicated one, and 3f + 1 is optimal for an asynchronous system.

## Adversarial position

**The paper's own limits**, stated by its authors:

- A3 is met only by a time-out, which needs a maximum message delay and clocks synchronized within a fixed error.
  Keeping clocks synchronized when some processors are faulty "is as difficult a problem as the Byzantine Generals
  Problem itself".
- The algorithms are "expensive in both the amount of time and the number of messages required".
- Agreement is on the input, not its truth; redundant inputs "cannot achieve reliability" on their own.

**Lamport, in his commentary on the 1980 paper**, says the cheaper signed solutions were dismissed because the signatures were read as
cryptographic, so the 3n+1 solutions stayed in use. **Castro and Liskov** list what PBFT does not give: fault-tolerant
privacy, a membership that changes, and safety without the assumption that nodes fail independently, for which they
suggest different implementations, root passwords and administrators per node.

## Outcome

The literature settled the bounds as the paper gave them: more than 3m generals for m traitors with oral messages, any
number with unforgeable signatures under synchrony, connectivity conditions for incomplete graphs, and message paths
of m + 1. Castro and Liskov (1999) settled the asynchronous case used in practice: safety with no timing premise, 3f + 1
replicas, and liveness only under a weak synchrony assumption, since otherwise "it could be used to implement
consensus in an asynchronous system, which is not possible". No effect to reverse.

## Analysis

**TOPAK put the generals in one place and the traitors in another.** The premise makes every agent Byzantine, but
the archetype never asks agents to agree with each other. Agreement is the mechanism's log, kept by replicas declared
crash-recovery (glossary item 13; ADR-0045 T-0045-1, "BFT is not required"). No agent relays an order another obeys.
ADR-0024's unanimity is the opposite end of LSP's dial: one honest grant seat blocks a promotion, and one absent seat
stalls it. LSP's problem arises only where replicas can lie. That is ADR-0059 §5's exposed plane, which ADR-0061 makes
seven replicas tolerating two.

**Why seven and not four, given signatures.** ADR-0061 uses certificates, which are LSP's signed messages, yet keeps
n > 3f. SM(m) needs no such bound, but it rests on A3, and A3 rests on synchronized clocks. ADR-0032 §1 refuses clocks
as a premise of safety, and PBFT's safety has no timing premise; at that price 3f + 1 is the minimum. So the 3f + 1
in ADR-0061 follows from refusing A3, not from oral messages. ADR-0061 does not say so, and it should. ADR-0064 then
makes the plane's clock a quorum's ticks, with captured and slow replicas fewer than a certificate (TM14,
`NoGrantPastExpiry`, broken by `M_ONECLOCK`). That is LSP's remark about clocks, which the overlay takes on directly.

**ADR-0061 §2's three recalled statements, against the paper read here.** This is a reading for the record, not the
record's own reading, which §7 still owes.

- *3f + 1*: confirmed (PBFT §3).
- *"A later form ... replaced signatures with message authentication codes"*: the OSDI 1999 paper's own
  implementation already uses signatures only on view-change and new-view messages, with MACs on every other
  message, and says MACs cannot prove authenticity "to a third party". A governor checking a commit certificate with
  no plane in reach is that third party. So the signed variant ADR-0061 needs is §4 of the paper, not what §5 built.
- *A fixed membership*: confirmed. View changes "never select a different set of replicas".

**Independence is the premise the count rests on.** PBFT assumes independent node failures. ADR-0061 puts a replica
on every governor (ADR-0062 §1), presumably one governor build per vehicle class. A flaw common to that build makes f
a statement about a single exploit, not about two captures (TM3, TM4). ADR-0035's lineage independence is about
Personas and says nothing of governors. A-0068-6 assumes the capture count; no row or assumption says how
independence is obtained.

**The traitor's move is equivocation, and the module found it in an honest rule.** Membership.tla's `M_TWOVOTES`
lets an honest replica sign two drops of one membership, which ADR-0061 §3 as first drafted allowed. Two successors
follow and `AtMostOneSuccessor` fails. R1 added the one-vote rule. LSP's warning about informal proofs is the reason the
module existed.

**Oral and signed messages are ADR-0065's two kinds of traffic.** A stack's report is an oral message: Byzantine,
labelled `untrusted` on receipt (`ReceivedIsUntrusted`; `M_SENDERLABEL` takes the sender's label instead) and enabling
nothing (`PeerAddsNothing`; `M_PEERENABLES`). A certified fence relayed by a peer is SM(m)'s countersigned relay. Fig.
1 against Fig. 2 is the reason a report cannot enable: the receiver cannot tell a lying relay from a lying source.

**Agreement on a lie.** LSP §6 is TM8 and TM9 in 1982 words. Seven replicas that agree on a governor's position
agree on whatever the position source said (T-0068-7), and ADR-0007 keeps that judgment out of the admit path.

**What the corpus cannot express.** Membership.tla abstracts PBFT to its certificate: no primary, view change or
message delivery, five replicas and not seven. The three outside steps are LSP's run itself. `proposed:ByzantineAgreement`
would carry a primary that equivocates, a view change, signed messages and partial synchrony. It would check
`AtMostOneSuccessor` at seven with the schedule, and show liveness only after a global stabilisation time, so that
ADR-0061 §7's "PBFT is read" has a module to point at.
