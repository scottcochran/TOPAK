---
id: 1990-TEL-ATT-4ESS-CASCADE
title: AT&T long distance, 15 January 1990 — a switch's recovery message knocked down its neighbours
kind: incident
date: 1990-01-15
sector: telecom
setting: AT&T's US long-distance network of 4ESS toll switches, linked by the CCS7 (SS7) signalling network
concerns: [deployment, cascading-failure, feedback, timing, rollback, supply-chain]
rules_at_time:
  - document: 4ESS fault-recovery procedure, as AT&T's Larry Seese described it to Telephony (22 January 1990)
    clause: corrective initialization and congestion signalling
    paraphrase: a switch that cannot correct a fault reinitializes, which takes four to six seconds, tells the switches it links with that it is taking no more traffic, and announces its return by resuming call processing
  - document: AT&T 4ESS software release, mid-December 1989 (Telephony; Sterling)
    clause: new front-end processor code
    paraphrase: new software was loaded into the front-end processors of all 114 4ESS switches; under it a switch's return to service was signalled by its first CCS7 initial address message
analogue:
  - record: ADR-0024
    clause: "§1, §2"
    note: a mechanism release crosses into Run only by a unanimous promotion, bound to its digest; the promotion applies to the whole domain at once
  - record: ADR-0065
    clause: "§1"
    note: a governor's measured fact "may refuse ... and never permits"; "a captured governor that lies can only stop others". Here an honest one stopped others
  - record: ADR-0045
    clause: "§2"
    note: a component whose failure can only subtract needs no proof, no key and no quorum
  - record: ADR-0035
    clause: "§3, §5"
    note: independence of lineage is an exclusion rule; the switches shared one lineage
actors:
  - party: AT&T (network operations and 4ESS software development)
    role: operator
    fault: honest-error
    note: Seese said "The fault was in the code"; AT&T's chairman Bob Allen apologised that the company "didn't live up to our own standards of quality" (Sterling)
  - party: The New York 4ESS switch
    role: automation
    fault: honest
    note: had a minor hardware fault and ran its normal recovery; its return message was correct
  - party: The other 4ESS switches
    role: automation
    fault: crash
    note: under the December code, a second message arriving while a switch was still resetting "confused the software", and the switch took itself out of service
  - party: Long-distance callers
    role: public
    fault: none-alleged
detection:
  means: [operator, customer]
  latency: minutes
trace:
  - step: Promote
    at: mid-December 1989
    note: new code loaded into the front-end processors of all 114 4ESS switches (Telephony); Sterling says it was a patch to speed up backup switchover. It ran for about a month before the trigger
  - step: outside:local-fault-and-self-reset
    at: about 14:25 EST, 15 January
    note: a trunk interface unit in New York develops a fault; the switch reinitializes and sends a congestion signal to its neighbours
  - step: ReceiveMeasured
    at: seconds later
    note: New York returns to service; its first call messages reach a neighbour. In Peer this is another governor's fact, which may refuse and never permits
  - step: outside:receiver-fails-on-message-timing
    at: within a hundredth of a second
    note: a second message arrives while the neighbour is still resetting; its software tries "an instruction that didn't make any sense", it reports its CCS7 processor faulty and shuts itself down
  - step: outside:recovery-message-propagates-fault
    at: afternoon
    note: each switch that recovers sends call messages that trip the next; Seese called it a chain reaction. Sterling says about seventy million calls went uncompleted
  - step: outside:signalling-load-reduced
    at: evening
    note: AT&T reduces the messaging load on the CCS7 network so the switches can settle (Telephony)
  - step: Promote
    at: by about 23:30 EST
    note: engineers replace the new software with an earlier version of System 7 (Sterling); the last switch clears by 23:30
outcome:
  by: AT&T (statements to the trade press, as reported in Telephony and RISKS); no regulator's finding in the sources read
  date: 1990-01-22
  summary: >-
    AT&T traced the outage to new software loaded in mid-December into the front-end processors of all 114 4ESS
    switches. A minor fault in a New York switch started its normal recovery; when it came back, the timing of its
    messages exposed a flaw in the new code at the switches it talked to, each of which shut itself down and, on
    recovering, did the same to others. AT&T stabilized the network by reducing CCS7 messaging load. It discounted
    intentional insertion (RISKS 9.61). Sterling records about seventy million uncompleted calls, sixty thousand
    people who lost service entirely, and the last switch clearing at about 11:30 p.m.
  aftermath: >-
    The new software was replaced by an earlier version of System 7. AT&T's chairman apologised publicly. In RISKS,
    W. H. Murray objected to AT&T's public line that the outage was "traced to a single computer program"; Jim Harkins
    replied that the statement had been simplified for a general audience.
  effect_reversed: partial
model:
  modules: [Peer, RulesFloorNV_rev5, Observers, proposed:SubtractionReach, proposed:StagedPromotion]
  properties: [PeerAddsNothing, NarrowsInReceived, P1_Unanimity, ReachIsBounded]
  mutations: []
  records: [ADR-0024, ADR-0065, ADR-0045, ADR-0035, ADR-0031, ADR-0068]
  findings: [TM10, TM13, CR-37]
  fault_class: a latent defect promoted to every node at once, triggered by an honest peer's recovery; each node's self-protection was the propagation
sources:
  - https://catless.ncl.ac.uk/Risks/9/62
  - https://catless.ncl.ac.uk/risks/9/61
  - https://web.mit.edu/hacker/part1.html
  - https://telephoneworld.org/?p=1785
verified: 2026-11-12
---

## Summary

In mid-December 1989 AT&T loaded new software into the front-end processors of all 114 of its 4ESS toll switches.
Larry Seese, AT&T's director of technology development, told Telephony that under it a switch's return to service
was signalled by its first CCS7 initial address message to its neighbours.

On the afternoon of 15 January 1990 (about 2:25 p.m. EST, by Bruce Sterling's account) a trunk interface unit in a
New York 4ESS developed a fault the switch could not correct. Its recovery code reinitialized it, which takes four to
six seconds, and it sent a congestion signal telling the switches it links with that it was taking no more traffic.
It then returned to service. A neighbouring switch received a second call-attempt message from it while still
resetting its logic. Seese said this "confused the software", which tried to execute "an instruction that didn't
make any sense". The neighbour reported its CCS7 processor faulty, shut itself down, and announced it was out of
service. When it restarted and sent call messages, the same thing happened at other switches across the country.

AT&T reduced the messaging load on the CCS7 network so that the switches could recover. Sterling writes that the
last switch cleared at about 11:30 p.m., that about seventy million calls went uncompleted, and that engineers
replaced the new software with an earlier version of System 7.

## Defensive position

**AT&T** (Seese, Allen, and statements reported in RISKS):

- The fault was in the code, not in the design of the network or the recovery procedure; the New York switch's own
  recovery was normal.
- Intentional insertion was discounted.
- Sterling reports that the System 7 software had been "extensively tested" and "was considered very stable".
- Jim Harkins, replying in RISKS, argued that "traced to a single computer program" was a fair simplification for a
  general audience.

## Adversarial position

- **W. H. Murray** (RISKS 9.61) found it alarming that one program could take down the national network.
- **Peter Neumann** (RISKS 9.61) described the event as "bogus status information" about one node's partial outage,
  "amplified in turn by each" switch, creating the "illusion" of a major outage.
- **AT&T's chairman** conceded that the company "didn't live up to our own standards of quality" (Sterling).

## Outcome

No regulator's finding appears in the sources read; the record is AT&T's own explanation, reported in Telephony on
22 January 1990 and discussed in RISKS. The software was rolled back. Calls blocked during the afternoon and evening
were not completed.

## Analysis

**Nothing was added, and everything was lost.** Every act in the cascade was a subtraction: a switch taking itself
out of service, a congestion signal, a refusal of traffic. TOPAK's safety properties are about additions. In `Peer`,
`PeerAddsNothing` and `NarrowsInReceived` hold of this trace as they hold of every trace: no message from a
neighbour enabled anything. ADR-0065 §1 goes further and says a governor's measured fact "may refuse on them and
never permits on them", with the comfort that "a captured governor that lies can only stop others". In 1990 an
honest switch, sending a correct message, stopped others, through a defect in the receiver. The corpus counts
"stopping others" as the safe residual. The 4ESS cascade is that residual at national scale.

**Self-protection was the propagation.** Each switch's fault handling did the locally correct thing: isolate,
signal, recover. The recovery message was the vector. No module has an action for "a receiver fails on the timing
of a valid message", so that step is outside. `Observers` has `ReachIsBounded` (a cell Observer's finding cannot
name a principal outside its cell; `M_REACH` breaks it), which bounds who may be stopped *by decision*. Nothing
bounds who can be stopped *by a fault in the receiver*, and nothing states how far one node's recovery may
propagate. That is the gap `proposed:SubtractionReach` would fill: a property bounding the number of cells a single
item, honest or not, can stop, with the receiving side's failure inside the model.

**Promotion to every node at once.** In TOPAK the December code is a mechanism release, and ADR-0024 §1 requires a
unanimous promotion bound to its digest (`P1_Unanimity`). That would have recorded who approved which artifact. It
would not have found a timing defect that took a month of service and a rare double message to show. The promotion
then applies to the whole domain: the corpus has no canary, no staged rollout and no fraction of the fleet left on
the old release (the external alignment of 2026.10.09 records "no SLOs, canaries, flags or Kubernetes"). Sterling's note that
some stations were still on System 6 is the nearest thing to diversity in this episode; the sources read do not say
whether it mattered. `proposed:StagedPromotion` would state promotion to a declared subset first, with the rest of
the domain on the prior digest until a declared count of rounds passes.

**Monoculture is a lineage question.** ADR-0035's independence rule applies to Personas, so that a Thinker and its
Observer do not share a lineage. All 114 switches shared one. TM10 (supply chain: "ship a bad artifact") is bounded
in the corpus by promotion by digest, which fixes *which* artifact runs, and the residual is "as the corpus states it
today". A rule that no more than some fraction of a domain runs one release would be the same exclusion rule applied
to the mechanism's own code.

**The repair was a rollback and a rate limit.** Reducing CCS7 load is a rate limit on recovery messages; the corpus
has rates on reports (ADR-0065 §2 gives a send "a count of its own per lease") but none on control traffic between
mechanism nodes. Reverting the software is a second promotion of an old digest. Both were done by people, outside
any modelled path, and the liveness work (CR-37) has nothing about how long a fleet takes to come back.
