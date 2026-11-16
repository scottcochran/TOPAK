---
id: 2014-TEL-SS7-LOCATION-TRACKING
title: SS7, December 2014 — location tracking and call interception by anyone with signalling access
kind: disclosure
date: 2014-12
sector: telecom
setting: The SS7 signalling interconnect between mobile network operators worldwide (MAP and CAMEL); shown at the 31st Chaos Communication Congress, Hamburg
concerns: [identity, ingress, authority, containment, accountability]
rules_at_time:
  - document: ITU-T Q.700 series (SS7), with 3GPP MAP (TS 29.002) and CAMEL (TS 23.078), as Engel summarised them
    clause: interconnect trust
    paraphrase: designed when operators were few and state-run or large; they "trusted each other, so no authentication built in", and the mobile protocols added later carried "still no authentication"
  - document: 3GPP MAP, as Engel described anyTimeInterrogation
    clause: network-internal services
    paraphrase: some services, such as querying a subscriber's cell from the home register, are meant only for use inside a network, and external networks "should not be able to invoke" them
analogue:
  - record: ADR-0065
    clause: "§1"
    note: nothing a peer originates is ever an enabling condition; a request from another network that changes a subscriber's routing is exactly such an item
  - record: ADR-0059
    clause: "§1, §4, §6"
    note: a plane is seated by its parent under a charter, is a havoc issuer bounded by it, and every verifier checks the whole chain; SS7 has no chain and no root
  - record: ADR-0045
    clause: "§2"
    note: a component whose failure can add authority and whose identity is issued by nobody is refused
  - record: ADR-0047
    clause: "§1, §7"
    note: every item of ingress is labelled by its source, and the floor's label forbids stop restricted content leaving by an outward channel; a location answered to whoever asked is that flow
actors:
  - party: Tobias Engel (Sternraute)
    role: investigator
    fault: none-alleged
    note: '"SS7: Locate. Track. Manipulate.", 31C3, 27 December 2014; tracked consenting people hourly for about two weeks'
  - party: Karsten Nohl (Security Research Labs)
    role: investigator
    fault: none-alleged
    note: '"Mobile self-defense", 31C3, the same day; showed decryption of intercepted traffic using keys requested over SS7'
  - party: Mobile network operators answering foreign MAP requests
    role: operator
    fault: contested
    note: Engel found that most visited-network switches accepted requests "from anywhere" with "no plausibility checks"
  - party: Commercial tracking providers and other parties with SS7 access
    role: attacker
    fault: byzantine
    note: Engel cites providers claiming coverage of about 70% of mobile subscribers from a phone number alone
  - party: GSMA
    role: regulator
    fault: none-alleged
    note: an industry body, not a regulator; did not comment to the Post, and in August had said SS7 was due for replacement over the next decade
detection:
  means: [researcher]
  latency: years
trace:
  - step: outside:signalling-access-by-membership
    at: before December 2014
    note: access "can be bought from telcos or roaming hubs for a few hundred euros a month", sometimes through resold roaming agreements (Engel)
  - step: outside:query-routing-identifiers
    at: any time
    note: sendRoutingInfoForSM to the home register returns the IMSI and the address of the serving switch for a phone number
  - step: Permit
    at: any time
    note: the serving switch answers provideSubscriberInfo with the subscriber's cell from any sender; in Peer, a permit on the strength of a peer's item is what M_PEERENABLES allows and PeerAddsNothing forbids
  - step: outside:location-leaves-to-requester
    at: any time
    note: cell-level location, street-level in cities, to a party with no relation to the subscriber
  - step: outside:foreign-write-to-subscriber-record
    at: any time
    note: a forged updateLocation or insertSubscriberData redirects calls and SMS, or replaces the CAMEL gsmSCF address so that calls are routed through the attacker's recording proxy
  - step: outside:session-key-disclosed
    at: any time
    note: sendIdentification with a TMSI captured over the air returns session keys (Engel); Nohl demonstrated passive interception and decryption of 3G traffic
  - step: Refuse
    at: after reports
    note: a German operator filters network-internal messages at its border; Engel reports attack traffic fell more than 80%. Vodafone began blocking the key requests after Nohl's report (Post)
counterfactual:
  by: each network admitting a foreign request only under a credential an issuer scoped to it, and never letting a foreign item write a subscriber's routing
  trace:
    - step: Issue
      at: interconnect agreement
      note: a charter naming which services a foreign network may invoke, issued and narrowed, not implied by connection
    - step: Refuse
      at: each foreign request
      note: provideSubscriberInfo, anyTimeInterrogation and insertSubscriberData from outside the chain are refused; location is never released to a party outside the subscriber's own chain
  holds: [PeerAddsNothing, LeaseWithinChain, HavocPlaneBounded]
outcome:
  by: no competent body ruled; the record is the researchers' presentations and operators' responses as reported by the Washington Post
  date: 2014-12-27
  summary: >-
    Engel and Nohl showed, independently, that a party with SS7 access and a target's phone number can locate the
    target, intercept calls and texts, disable service and redirect calls at the target's expense. Engel's slides
    say the design assumes members trust each other, that access is purchasable, and that many switches answer
    requests from anywhere. The Post reported that thousands of companies have access, so a carrier in one country
    can be used to reach networks in another; T-Mobile was among more than 20 networks tested and said it works
    with operators, vendors and standards bodies on detection and prevention; Vodafone in Germany began blocking
    key requests after Nohl reported them.
  aftermath: >-
    Engel recommended SMS home routing and filtering at every network's border of MAP and CAP messages only needed
    internally. He noted that LTE's Diameter carries "a lot of the SS7 design ... including its flaws", and that
    GSM and UMTS would be around for about twenty years.
  effect_reversed: not-applicable
model:
  modules: [Peer, Federation, Labels, proposed:PeerFederation]
  properties: [PeerAddsNothing, NarrowsInReceived, ReceivedIsUntrusted, LeaseWithinChain, HavocPlaneBounded]
  mutations: [M_PEERENABLES, M_TRUSTPLANE, M_LASTLINK]
  records: [ADR-0065, ADR-0059, ADR-0045, ADR-0047, ADR-0025, ADR-0068]
  findings: [TM5, TM13, CR-24, CR-34]
  fault_class: a federation that authenticates membership and nothing else; any member, or anyone who rents membership, is a principal on every network
sources:
  - https://fahrplan.events.ccc.de/congress/2014/Fahrplan/events/6249.html
  - https://fahrplan.events.ccc.de/congress/2014/Fahrplan/system/attachments/2553/original/31c3-ss7-locate-track-manipulate.pdf
  - https://fahrplan.events.ccc.de/congress/2014/Fahrplan/events/6122.html
  - https://www.heraldnet.com/?p=69951
  - https://time.com/3641668/researchers-flaws-cellphone
verified: 2026-11-12
---

## Summary

SS7 is the protocol suite operators use to talk to each other. Tobias Engel's 31C3 slides (27 December 2014) say it
was standardized in the 1980s when operators were few, that they "trusted each other, so no authentication built
in", and that the mobile protocols added since (MAP, CAMEL) have "still no authentication". Access "can be bought
from telcos or roaming hubs for a few hundred euros a month".

With a phone number, Engel showed: sendRoutingInfoForSM to the home register returns the subscriber's IMSI and the
address of the serving switch; provideSubscriberInfo sent straight to that switch returns the subscriber's cell.
"Most VLR/MSC accept requests from anywhere", with "no plausibility checks". He tracked consenting people hourly for
about two weeks. The emergency location service (GMLC) requires authentication, but a location request sent directly
to the switch does not, and the MAP-layer check of the sender compares an address the sender itself supplies.

The same access writes. A forged updateLocation makes the home register route a subscriber's calls and texts to the
attacker; insertSubscriberData can replace the CAMEL gsmSCF address so that calls are set up through the attacker's
recording proxy; call forwarding and USSD can be set for another subscriber. Karsten Nohl showed, the same day, that
requesting the temporary key over SS7 lets traffic captured off the air be decrypted, and demonstrated passive
interception and decryption of 3G traffic; Engel's slides show sendIdentification returning session keys. The
Washington Post reported on 18 December that thousands of companies have
access.

## Defensive position

- **The design's original premise**, as Engel states it: a small club of state-controlled or large operators who
  trusted each other.
- **T-Mobile** told the Post it works with other operators, vendors and standards bodies to detect and prevent these
  attacks. Some carriers already blocked location requests, several since the Post's August report.
- **GSMA** did not comment to the Post; in August it had acknowledged the problems and said SS7 was due for
  replacement within the decade.
- A German operator, Engel reports, found some of the traffic it then blocked was misconfiguration or commercial use:
  a shipping company tracking its vehicles, and an SMS provider for banks checking for SIM swaps.

## Adversarial position

- **Engel**: "It's like you secure the front door of the house, but the back door is wide open" (Post). Access "is
  getting easier and easier, without the security measures keeping up" (31C3 abstract). "I doubt we are the first
  ones in the world who realize how open the SS7 network is."
- **Nohl**: "It's all automated, at the push of a button"; the decryption could be automated at scale (Post).
- Engel reports that the German operator believed attacks it saw were by "state actors or the other network's
  operators themselves", and that some originating operators "did not respond or played dumb".

## Outcome

No regulator or court acted on the disclosure in the sources read. Operators responded one by one: Vodafone in
Germany blocked key requests; a German operator filtered network-internal messages at its border with SMS home
routing and saw attack traffic fall by more than 80%. The protocol was not changed; Engel's countermeasures are
filters each network applies at its own edge.

## Analysis

**Trust by membership is the case ADR-0045 refuses.** A component "whose failure can add authority and whose identity
is fixed by neither issuance nor promotion is not a row". An SS7 peer's identity is fixed by having a connection,
which is for sale; its failure (or its customer's intent) adds authority over another network's subscribers. TOPAK's
answer is issued identity: authority starts at the anchor (ADR-0025) and reaches a plane only through a charter its
parent seated (ADR-0059 §1).

**The federation has no root.** `Federation` models a tree of planes with a root whose tally bounds the rest:
`LeaseWithinChain` and `HavocPlaneBounded` say a verifier never permits under a chain it has not checked, whatever
captured planes sign. The two mutations that matter are named for SS7's posture: `M_TRUSTPLANE` (the verifier "takes
a captured plane's word for its own chain and checks no charter") and `M_LASTLINK` (it checks only the granting
plane). An HLR answering any network's request is `M_TRUSTPLANE` with no chain at all. But SS7 is a flat federation
of peers, each its own root, bound by bilateral roaming agreements. `Federation` cannot express that: there is no
common root to bound by. `proposed:PeerFederation` would model several roots, each issuing scoped credentials to the
others for named services, and state that a foreign request is admitted only under such a credential.

**Writes are peer items enabling effects.** insertSubscriberData and updateLocation from a foreign network change how
the home network routes a subscriber's calls. In `Peer`, that is `M_PEERENABLES` ("a report enables one entry"),
which breaks `PeerAddsNothing`. ADR-0065 §1 forbids it outright: "nothing a peer originates is ever an enabling
condition". The reads are the same in the other direction: a location answered to anyone is a `restricted` item
leaving on a peer's request, the flow ADR-0047 §7's label forbids exist to refuse.

**The front door and the back door.** The GMLC authenticates; the switch answering provideSubscriberLocation directly
does not. ADR-0015 makes every boundary crossing authorized, and ADR-0054 checks a route again where it is applied.
TOPAK's design answer to Engel's metaphor is that there is one admit path, and the switch is on it.

**Where the pattern stops.** The counterfactual is a design, not a deployable fix: SS7 is shared by every operator,
and Engel's real remedy is each network filtering at its own border, a deny one party can apply without the others.
That matches ADR-0065's direction ("receipt only narrows") and needs no federation-wide agreement. CR-24 and CR-34
record the same weakness inside TOPAK's own reference: replica traffic unauthenticated, operator requests trusted by
a socket's file mode. TOPAK's design rejects trust by membership; its running code does not yet. The threat rows
bound a lying peer (TM13) by "nothing a peer originates enables anything", and a captured plane (TM5) by the
charter every governor checks. SS7 is both rows with their bounds removed.
