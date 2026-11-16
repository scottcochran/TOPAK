---
id: 2023-TEL-OPTUS-OUTAGE
title: Optus, 8 November 2023 — routers that disconnected themselves at their vendor's default limits, and the 000 calls that failed
kind: incident
date: 2023-11-08
sector: telecom
setting: Optus' national IP core and provider-edge routers, Australia, taking routing information through Singtel's international exchange (STiX)
concerns: [monitoring, interlock, cascading-failure, emergency-path, configuration-change, accountability]
rules_at_time:
  - document: Australian emergency call rules enforced by the ACMA (as reported by iTnews, November 2024)
    clause: access to the emergency call service; welfare checks
    paraphrase: a carrier must give its customers access to 000, and must check on the welfare of people whose emergency calls failed
  - document: Cisco default self-protection limits on the provider-edge routers (Optus' submission to the Senate, as reported by iTnews)
    clause: routing-information overload protection
    paraphrase: a router receiving more routing information than a preset limit isolates itself from the network to protect itself; Optus said the limits were the vendor's defaults
analogue:
  - record: ADR-0065
    clause: "§1"
    note: a governor's measured facts "may refuse ... and never permits", and "a captured governor that lies can only stop others"; a peer's routing information stopping Optus is the residual this accepts
  - record: ADR-0038
    clause: "§5"
    note: '"More Observers never lower safety and may lower availability"; a deny-only monitor costs availability, never safety'
  - record: ADR-0039
    clause: "§5, §6"
    note: a Byzantine Observer can stop its own cell; "the cell's availability is the product of its Thinker's and its Observer's"
  - record: ADR-0052
    clause: "§1"
    note: an emergency path that needs a provider fails when the provider does
actors:
  - party: Optus (Singtel Optus)
    role: operator
    fault: contested
    note: the ACMA found the outage preventable and fined Optus subsidiaries more than $12 million; Optus attributed the trigger to routing information from a peer and its routers' default limits
  - party: About 90 Optus provider-edge routers
    role: safety-system
    fault: honest
    note: self-isolated as designed when routing information exceeded their limits (Optus)
  - party: Singtel (STiX)
    role: peer
    fault: contested
    note: Optus said the routing information came through an alternate Singtel peering router during an upgrade at a STiX site in North America; Singtel disputed that the upgrade was the cause
  - party: Cisco
    role: vendor
    fault: none-alleged
    note: supplier of the default limits
  - party: ACMA
    role: regulator
    fault: none-alleged
detection:
  means: [customer, operator]
  latency: minutes
trace:
  - step: outside:peer-maintenance-reroutes-updates
    at: before 04:05 AEDT
    note: Optus' usual Singtel source router is under planned maintenance; routing information arrives through an alternate Singtel peering router while a software upgrade is under way at a STiX site in North America (Optus, per iTnews)
  - step: ReceiveMeasured
    at: about 04:05 AEDT
    note: the routing changes "propagated through multiple layers in our network". In Peer, another network's fact may refuse and never permit; here receiving it is what refuses
  - step: outside:self-protection-limit-trips
    at: about 04:05 AEDT
    note: routing information "exceeded preset safety levels on key routers", which disconnected from the IP core "to protect themselves"; about 90 PE routers self-isolated, at Cisco's default limits (Optus)
  - step: outside:emergency-calls-fail
    at: through the day
    note: Optus landlines could not reach 000; Optus mobiles could only when the call went over Telstra or Vodafone (The Conversation). The ACMA later counted 2,145 people who could not reach emergency services
  - step: outside:physical-reboot-of-network-elements
    at: morning onward
    note: Optus described "physically rebooting and reconnecting some network elements"; the ACMA found it lacked sufficient out-of-band capability for diagnosis during an outage
  - step: outside:welfare-checks-missed
    at: after the outage
    note: the ACMA found Optus did not carry out welfare checks on 369 people whose emergency calls failed
counterfactual:
  by: limits set for the surge an upstream can send, with an out-of-band path to the routers, as the ACMA said Optus should have had
  trace:
    - step: ReceiveMeasured
      at: 04:05 AEDT
      note: the same surge of routing information
    - step: outside:limit-sized-to-upstream-surge
      at: 04:05 AEDT
      note: no module has a limit, a surge, or a property saying what a tripped limit must leave running
    - step: outside:independent-management-path
      at: if needed
      note: diagnosis and restarts over a path that does not depend on the IP core
  holds: [PeerAddsNothing, NarrowsInReceived]
outcome:
  by: Australian Communications and Media Authority; the Senate Environment and Communications References Committee heard Optus; a government post-incident review
  date: 2024-11
  summary: >-
    Optus said, in a statement quoted on 13 November 2023, that routing changes "exceeded preset
    safety levels on key routers", which disconnected from its IP core to protect themselves. Its Senate submission
    of 16 November named about 90 provider-edge routers, said the limits were "default settings provided by the
    relevant global equipment vendor (Cisco)", and that the information came through an alternate Singtel peering
    router. At the Senate hearing on 17 November Optus' chief executive disclosed 228 failed triple-zero calls. The
    ACMA's investigation found that 2,145 people could not reach emergency services and 369 did not get welfare
    checks, that the outage should have been preventable, that Optus should have configured its core routers for
    an unexpected surge of routing data from upstream rather than relying on defaults, and that it lacked sufficient
    out-of-band capability; Optus subsidiaries paid penalties of more than $12 million.
  aftermath: >-
    Chief executive Kelly Bayer Rosmarin resigned on 20 November 2023. The Communications Minister announced a
    review, and the Senate held an inquiry. Optus offered affected customers extra data.
  effect_reversed: partial
model:
  modules: [Peer, Observers, Coupling, Alone, proposed:SubtractionReach, proposed:RecoveryPath]
  properties: [PeerAddsNothing, NarrowsInReceived, ReachIsBounded, AlonePermitsNothing]
  mutations: []
  records: [ADR-0065, ADR-0038, ADR-0039, ADR-0052, ADR-0045, ADR-0062, ADR-0068]
  findings: [TM2, TM13, CR-36, CR-37]
  fault_class: a correctly working safety limit, at an unexamined default, tripped on every edge router at once by a peer's input; emergency calling depended on the network that stopped
sources:
  - https://theconversation.com/optus-has-revealed-the-cause-of-the-major-outage-could-it-happen-again-217564
  - https://www.itnews.com.au/news/optus-outage-blamed-on-edge-router-default-settings-602442
  - https://www.canberratimes.com.au/story/8426886/hundreds-of-emergency-calls-failed-during-optus-outage/
  - https://www.itnews.com.au/news/optus-penalised-12m-for-triple-zero-failures-612931
  - https://en.wikipedia.org/wiki/2023_Optus_outage
verified: 2026-11-12
---

## Summary

At about 4:05 a.m. AEDT on Wednesday 8 November 2023 Optus' mobile, fixed and internet services failed nationally,
and stayed down well into the evening. More than 10 million customers were affected. Optus said a "routine software
upgrade" set it off: routing information changes "propagated through multiple layers in our network and exceeded
preset safety levels on key routers which could not handle these", and those routers disconnected from the Optus IP
core "to protect themselves".

Optus' submission to the Senate on 16 November added that about 90 provider-edge routers had self-isolated "to
protect themselves from an overload of IP routing information"; that "these self-protection limits are default
settings provided by the relevant global equipment vendor (Cisco)"; and that the information arrived through "an
alternate Singtel peering router" because the usual one was under planned maintenance, while "an unspecified software
upgrade was being performed at one STiX location in North America". Optus said the upgrade was not the cause of the
Australian incident; Singtel had disputed that it was. Recovery involved "physically rebooting and reconnecting some
network elements".

Optus landlines could not call 000; Optus mobiles could only where the call was carried by Telstra or Vodafone. At
the Senate on 17 November the chief executive disclosed 228 failed triple-zero calls. The ACMA later found that
2,145 people had been unable to reach emergency services.

## Defensive position

**Optus** (its statements and Senate submission):

- The routers did what they were designed to do: protect themselves from an overload.
- The limits were the vendor's defaults, and the routing information came from outside Optus, through Singtel's
  exchange.
- It was not a cyberattack.
- Asked why the 000 calls failed, the chief executive said "It's too early to tell where the issue actually
  occurred" (Canberra Times).

## Adversarial position

- **The ACMA**: the outage should have been preventable; Optus should have configured its core routers to handle an
  unexpected surge of routing data from upstream rather than rely on default settings, and lacked sufficient
  out-of-band capability for diagnosis and administration during an outage. The penalty, its chair said, reflected
  "the critical nature of the breaches".
- **Mark Gregory** (RMIT, The Conversation): the explanation "points to human error" and "leaves many questions
  unanswered"; upgrades should go through modelling, testing and several layers of sign-off, and redundant systems
  should come into service within minutes.
- **Singtel** disputed that the North American upgrade caused the outage.

## Outcome

The ACMA's investigation concluded with penalties of more than $12 million paid by Optus subsidiaries, announced in
November 2024, for breaches of the emergency call rules: 2,145 people unable to reach emergency services and 369
without the welfare checks the rules require. The chief executive resigned on 20 November 2023. Service was restored
the same day; the failed emergency calls were not.

## Analysis

**Rogers in reverse.** Rogers' core had no overload limit, and a flood of routes took it down (2022-TEL-ROGERS-OUTAGE).
Optus' edge had limits, and the limits took it down. Both are national outages, so the lesson is not "add a limit".
A limit is a monitor with an actuator, and what matters is what it does when it trips and how many of them trip
together. No module in the corpus has a limit, a surge, or a property about what a tripped limit leaves running.

**TOPAK would class the limit as safe, and it was.** Every router that disconnected subtracted. Under ADR-0045 §2 a
component whose failure "can only subtract" is delegated and needs "no proof, no key and no quorum". ADR-0038 §5
puts it as a principle: "More Observers never lower safety and may lower availability." ADR-0039 §6 prices it:
"the cell's availability is the product of its Thinker's and its Observer's". Optus is that product with ninety
factors, every one tripped by the same input. Safety held. The network did not.

**A peer's fact stopped the network, which ADR-0065 accepts.** ADR-0065 §1 lets a governor refuse on another's
measured facts and never permit on them, and comforts itself that "a captured governor that lies can only stop
others". In `Peer`, `PeerAddsNothing` and `NarrowsInReceived` hold here; nothing Singtel's exchange sent added
authority. TM2 gives the link adversary "denial is always available" and calls the response "predictable", and
TM13's residual includes "peers stalled by claims". The corpus names this residual and leaves it there. Optus
measures it: one upstream, by honest routing updates, stopped ten million customers for most of a day.

**One input, ninety identical responses.** The routers shared a vendor, a default and an upstream. `Observers` bounds
how far a finding may reach (`ReachIsBounded`); nothing bounds how many independent monitors one shared input can
trip at once. In ADR-0062 §5 a vehicle that stops hearing its plane goes alone, and `Alone` proves
`AlonePermitsNothing`; a fleet whose every vehicle goes alone on one event permits nothing anywhere, which is safe
and is this outage. `proposed:SubtractionReach` would state a bound: no single item, from a peer or from one shared
dependency, takes more than a declared fraction of a domain's cells out of service.

**Defaults are placeholders.** The ACMA's finding is that Optus relied on a vendor's default where the surge an
upstream can send should have set the number. CR-36 says the same of TOPAK: "every number is a placeholder and the
floor is proved over them". A limit nobody measured is a claim, in ADR-0049's sense, about the traffic it will see.

**Emergency calls rode on the failed network.** 000 from an Optus landline had no other path; from a mobile it worked
only where another carrier's network carried it. ADR-0052 §1 makes the emergency seat's key independent of the
identity provider because "an emergency path that needs the identity provider fails when the provider does". The
same sentence about the network is not in the corpus, and TOPAK's emergency seat is for repairing a deployment, not
for the public's emergency calls, which are outside the pattern entirely. Where the pattern does reach is the
ACMA's other finding: out-of-band access for diagnosis. `proposed:RecoveryPath` would require the emergency seating
to declare its channel and its independence from what it repairs.

**Where the pattern stops.** The 2,145 people who could not reach 000 and the 369 missed welfare checks are a
carrier's duties to the public. Nothing in TOPAK models callers, and no admit rule would have connected their calls.
