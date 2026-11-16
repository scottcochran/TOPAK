---
id: 2008-NET-YOUTUBE-BGP-HIJACK
title: Pakistan Telecom and YouTube, 24 February 2008 — a domestic block announced to the world, and an upstream that passed it on
kind: incident
date: 2008-02-24
sector: networking
setting: Inter-domain routing (BGP) between Pakistan Telecom (AS17557), its upstream PCCW Global (AS3491) and YouTube (AS36561)
concerns: [identity, authority, containment, ingress, configuration-change, rollback]
rules_at_time:
  - document: Pakistan Telecommunication Authority order to Pakistani internet providers (February 2008, as Dawn reported it)
    clause: block YouTube
    paraphrase: providers were told to block YouTube over a video the PTA called "highly provocative and blasphemous"
  - document: BGP route selection, as RIPE NCC and Renesys describe it
    clause: longest-prefix match
    paraphrase: a router forwards on the most specific prefix it has heard, whoever announced it; a provider decides for itself what it accepts from a customer
analogue:
  - record: ADR-0059
    clause: "§1, §4, §6"
    note: a plane is seated under a charter by its parent, is a havoc issuer bounded by it, and every verifier checks every charter on the chain, not only the last link
  - record: ADR-0065
    clause: "§1"
    note: nothing a peer originates is an enabling condition; a certified fact a peer relays is the issuer's act, not the peer's
  - record: ADR-0045
    clause: "§2"
    note: a component that can add authority and whose identity is issued by nobody is refused
  - record: ADR-0030
    clause: "§1"
    note: a bundle cannot add authority; Pakistan Telecom's block was meant as a local subtraction and travelled as a global addition
actors:
  - party: Pakistan Telecom (AS17557)
    role: operator
    fault: contested
    note: announced 208.65.153.0/24 to comply with a government order to block YouTube (Renesys); the BBC asked whether it was "a mistake or a deliberate attempt" (Dawn)
  - party: PCCW Global (AS3491)
    role: peer
    fault: omission
    note: accepted its customer's announcement without validating it and passed it to its peers and providers (Renesys); withdrew it about two hours later
  - party: YouTube (AS36561)
    role: counterparty
    fault: none-alleged
    note: announced the same /24 and then two /25s to win its traffic back
  - party: Pakistan Telecommunication Authority
    role: regulator
    fault: none-alleged
    note: ordered the domestic block
  - party: RIPE NCC
    role: investigator
    fault: none-alleged
    note: published a case study from its Routing Information Service data
detection:
  means: [counterparty, peer, researcher]
  latency: minutes
trace:
  - step: outside:domestic-block-order
    at: February 2008
    note: the PTA orders Pakistani providers to block YouTube (Dawn)
  - step: outside:more-specific-prefix-originated
    at: 18:47 UTC, 24 February
    note: Pakistan Telecom announces 208.65.153.0/24, inside YouTube's 208.65.152.0/22 and covering youtube.com's addresses
  - step: Permit
    at: about 18:48 UTC
    note: PCCW accepts the announcement and readvertises it; in Federation terms its check is M_TRUSTPLANE, a captured or mistaken plane's word for its own authority
  - step: outside:global-propagation
    at: 18:48 to 18:49:30 UTC
    note: nine networks carry the route within a minute; 97 within about ninety seconds (Renesys). Longest-prefix match sends YouTube's traffic to Pakistan
  - step: outside:victim-announces-more-specifics
    at: 20:07 and 20:18 UTC
    note: YouTube announces the same /24, then 208.65.153.0/25 and 208.65.153.128/25, which win wherever they are heard
  - step: outside:upstream-withdraws-customer-routes
    at: about 21:00 UTC
    note: PCCW withdraws the prefixes Pakistan Telecom originated; RIPE NCC gives 21:01, Renesys 20:59:39 and says PCCW disconnected AS17557
counterfactual:
  by: PCCW, checking its customer's announcement against what the customer had been issued authority to originate, as Renesys said a provider "can and should"
  trace:
    - step: Issue
      at: before 24 February
      note: authority to originate 208.65.152.0/22 belongs to YouTube; Pakistan Telecom's charter at PCCW lists its own fewer than 1,000 prefixes (Renesys)
    - step: Refuse
      at: 18:47 UTC
      note: the /24 is outside Pakistan Telecom's charter and goes no further than its own network; the domestic block is a local subtraction, as the PTA intended
  holds: [LeaseWithinChain, HavocPlaneBounded, PeerAddsNothing]
outcome:
  by: no competent body ruled; RIPE NCC's case study and Renesys' analysis are the record
  date: 2008-02
  summary: >-
    RIPE NCC's Routing Information Service data show Pakistan Telecom announcing 208.65.153.0/24 from 18:47 UTC,
    PCCW propagating it, YouTube announcing the /24 at 20:07 and two /25s at 20:18, Pakistan Telecom's announcement
    seen with a prepended AS path at 20:51, and PCCW withdrawing all prefixes Pakistan Telecom originated at 21:01.
    Renesys found PCCW had accepted and readvertised the route without validation, that 97 networks carried it, and
    that the outage lasted about an hour and forty minutes for some users and a little over two hours at most.
    Dawn reported that Google attributed the nearly two-hour blackout to "erroneous internet protocols" from Pakistan.
  aftermath: >-
    Renesys argued that a provider "can and should limit the advertisements it will accept from a customer", noting
    that Pakistan Telecom originated or transited fewer than 1,000 prefixes. The sources read do not report a rule
    change or sanction.
  effect_reversed: "yes"
model:
  modules: [Federation, Peer, proposed:PeerFederation]
  properties: [LeaseWithinChain, HavocPlaneBounded, PeerAddsNothing]
  mutations: [M_TRUSTPLANE, M_LASTLINK, M_PEERENABLES]
  records: [ADR-0059, ADR-0065, ADR-0045, ADR-0030, ADR-0025]
  findings: [TM5, TM13]
  fault_class: an origin claim admitted on membership, by an upstream that checked nothing, propagated by peers who could not check
sources:
  - https://www.ripe.net/publications/news/industry-developments/youtube-hijacking-a-ripe-ncc-ris-case-study
  - https://crysp.uwaterloo.ca/courses/cs458/F08-lectures/local/www.renesys.com/blog/2008/02/pakistan_hijacks_youtube_1.shtml.html
  - https://www.dawn.com/news/amp/291075
verified: 2026-11-12
---

## Summary

In February 2008 the Pakistan Telecommunication Authority told the country's internet providers to block YouTube
over a video it called "highly provocative and blasphemous" (Dawn). youtube.com resolved to addresses inside
208.65.153.0/24, part of the 208.65.152.0/22 that YouTube announced.

At 18:47 UTC on Sunday 24 February Pakistan Telecom (AS17557) began announcing 208.65.153.0/24 to its provider, PCCW
Global (AS3491). PCCW passed it on. Because routers forward on the most specific prefix, networks that heard the /24
sent YouTube's traffic to Pakistan Telecom. Renesys counted nine networks carrying the route by 18:48 and 97 by
18:49:30.

YouTube announced the same /24 at 20:07, and 208.65.153.0/25 and 208.65.153.128/25 at 20:18; the /25s won wherever
they were heard. At 20:51 Pakistan Telecom's announcement was seen with an extra 17557 prepended. PCCW withdrew all
the prefixes Pakistan Telecom originated at 21:01 by RIPE NCC's data (20:59:39 by Renesys', which says PCCW also
disconnected AS17557). Renesys put the outage at about an hour and forty minutes for some users and a little over two
hours at most.

## Defensive position

- **Pakistan Telecom** was, in Renesys' words, attempting "to comply with a government order to block YouTube". The
  PTA's press release, as Dawn reported it, said such content undermined religious tolerance and could spark unrest
  and loss of life or property.
- **BGP** carried the more specific route exactly as designed: the protocol prefers it whoever announces it.

## Adversarial position

- **Renesys (Martin Brown)**: PCCW accepted the announcement without validating it and passed it to its peers and
  providers; "a provider can and should limit the advertisements it will accept from a customer", which was
  practical for a customer with fewer than 1,000 prefixes.
- **BBC**, as Dawn reported it: the question was "whether this was a mistake or a deliberate attempt by Pakistan to
  disrupt YouTube".
- **Google**, per Dawn, attributed the blackout to "erroneous internet protocols" originating in Pakistan.

## Outcome

No regulator or court acted in the sources read. YouTube's more specific announcements and PCCW's withdrawal ended
the episode within about two hours, and RIPE NCC's case study and Renesys' analysis are the record of it. The routes
were restored; the hijacked route was withdrawn.

## Analysis

**Trust by membership, again.** Any network in the routing system could announce any prefix. The only check was what
its neighbour chose to accept, and PCCW chose to accept everything. ADR-0045 §2 refuses a component "whose failure
can add authority and whose identity is fixed by neither issuance nor promotion". An origin announcement adds
authority over where traffic goes, and nothing issued it.

**`Federation` has the check PCCW skipped.** ADR-0059 §4 makes every plane a "havoc issuer, bounded by its charter":
it may sign anything, and a verifier accepts only what lies within every charter on the chain. `LeaseWithinChain`
and `HavocPlaneBounded` hold in `Federation` because the verifier checks; under `M_TRUSTPLANE` ("takes a captured
plane's word for its own chain and checks no charter") and `M_LASTLINK` (checks only the granting plane) both fail.
PCCW's acceptance is `M_TRUSTPLANE` with Pakistan Telecom as the plane. The counterfactual is the module's run with
`Mut = "none"`: the announcement is outside the customer's charter, and `Refuse` ends it at the first hop.

**What `Federation` cannot say.** It models one tree with one root whose tally bounds everything below. Address
authority on the internet is a federation of peers: YouTube's authority over its prefix was not issued by PCCW, and
the 97 networks that carried the route were not PCCW's children. A peer two hops away could not check Pakistan
Telecom's charter at PCCW even if one existed. ADR-0065 §1's distinction is the right one: "a certified fact a peer
relays is the plane's act and not the peer's". A route is safe to relay when it carries a certificate from whoever
holds authority over the prefix, and the relaying peer adds nothing. `proposed:PeerFederation` would model several
roots, credentials one root issues for another's use, and a property that a relayed claim is admitted only with its
issuer's certificate, whatever path it took.

**A subtraction that left home as an addition.** The PTA's order was a deny, and inside Pakistan the route did what a
deny should. ADR-0030 holds that a bundle cannot add authority: whatever a local rule says, it narrows the local
admit and nothing else. In BGP, the same artifact expressed the local deny and claimed the address globally, so the
block reached the world. TOPAK keeps those two apart by construction: a deny is not an announcement, and nothing a
deny contains travels as authority to anyone else.

**The remedy used the flaw.** YouTube won its traffic back by announcing more specific prefixes, which is the same
unauthenticated longest-prefix rule that let it be taken. That worked because the victim was well connected and fast.
In TOPAK terms recovery was a race between havoc issuers, and nothing bounded who would win. TM5, a captured plane,
is bounded by "the charter or the intent, checked by every governor"; here nobody checked, and the outcome turned on
who announced last and most specifically.
