---
id: 2020-NET-CENTURYLINK-FLOWSPEC
title: CenturyLink/Level 3, 30 August 2020 — a Flowspec rule meant to block one address that stopped BGP across the network
kind: incident
date: 2020-08-30
sector: networking
setting: CenturyLink/Level 3 (AS3356) global IP backbone; the rule was entered at its data centre in Mississauga, Ontario, by its status page's account
concerns: [configuration-change, deployment, revocation, cascading-failure, rollback, accountability]
rules_at_time:
  - document: BGP Flowspec, as Cloudflare described it
    clause: distribution of filtering rules by BGP
    paraphrase: a BGP extension that distributes firewall rules quickly across every router of a network; useful against attacks, and dangerous when a rule is wrong
  - document: CenturyLink/Level 3 Reason For Outage, as MacStadium summarised it
    clause: the rule's intended scope
    paraphrase: the rule was meant to block a single IP address; wildcards introduced unintentionally widened its match
analogue:
  - record: ADR-0050
    clause: "§4"
    note: a deny needs no quorum and no peer; a targeted Revoke names one principal, and the fleet fence is a different variant that needs a live lease; "any one operator can stop a domain"
  - record: ADR-0031
    clause: "Consequences"
    note: '"A fence storm is an availability event"; tightening a live round ends it, and fleet-wide that is an epoch fence'
  - record: ADR-0065
    clause: "§1"
    note: a subtraction applies on receipt, before it is ordered anywhere; a relayed fence is certified by the plane, and a peer's measured fact may refuse and never permit
  - record: ADR-0028
    clause: "F2"
    note: stop attribution; every stop records who made it
actors:
  - party: CenturyLink/Level 3 network operations
    role: operator
    fault: honest-error
    note: the Reason For Outage attributes the rule to "the unintentional introduction of wildcards into an attempt to block a single IP" (MacStadium's summary)
  - party: CenturyLink/Level 3 routers
    role: automation
    fault: byzantine
    note: Cloudflare observed the network go on advertising routes that had been withdrawn
  - party: Cloudflare
    role: peer
    fault: none-alleged
    note: detected 522 errors at 10:03 UTC and moved traffic to other carriers; published an analysis the same day
  - party: Other tier-1 providers
    role: peer
    fault: none-alleged
    note: de-peered from CenturyLink/Level 3, "it appears at CenturyLink/Level(3)'s request" (Cloudflare)
  - party: Customers single-homed on CenturyLink/Level 3
    role: user
    fault: none-alleged
detection:
  means: [automated-monitor, peer, customer]
  latency: seconds
trace:
  - step: outside:flowspec-rule-entered
    at: about 10:04 UTC, 30 August
    note: a rule meant to block one IP address, with wildcards in its match, is announced (RFO via MacStadium); the status page placed its origin at the Mississauga data centre (Telecompaper)
  - step: FenceEpoch
    at: 10:04 UTC onward
    note: in effect a fleet-wide deny. In Operators the fleet fence is its own variant and needs a live lease; Flowspec has one kind of rule whose scope is whatever its match fields say
  - step: outside:deny-cuts-own-control-plane
    at: 10:04 UTC onward
    note: the "offending flowspec announcement ... prevented Border Gateway Protocol (BGP) from establishing across multiple elements" (CenturyLink); Cloudflare suspected routers dropping and relearning the rule, with BGP updates above 26 MB per 15 minutes against a usual 1.5 to 2 MB
  - step: outside:withdrawals-not-honoured
    at: during the outage
    note: AS3356 kept advertising routes that had been withdrawn, so traffic kept arriving where it could not be delivered (Cloudflare)
  - step: outside:peers-depeer-on-request
    at: during the outage
    note: other tier-1 providers de-peered to reduce the load on CenturyLink's routers (Cloudflare)
  - step: outside:global-config-blocks-rule
    at: by about 15:10 UTC
    note: '"CenturyLink deployed a global configuration change to block the problematic Flowspec announcement", and BGP established again (RFO via MacStadium)'
counterfactual:
  by: a deny whose scope is part of its type, so that a rule written to stop one address cannot stop the network, and whose author is on the record
  trace:
    - step: Revoke
      at: 10:04 UTC
      note: a targeted deny naming one target; its scope is the variant, not a pattern in its arguments
    - step: outside:scope-checked-against-variant
      at: 10:04 UTC
      note: no module checks that a deny's match is no wider than its declared target; Operators types scope by variant only
  holds: [EveryStopIsAttributed, DenyAlwaysAvailable]
outcome:
  by: CenturyLink/Level 3 (status updates and Reason For Outage, as reported); no regulator's report on this outage was found
  date: 2020-09
  summary: >-
    CenturyLink said an "offending flowspec announcement" had "prevented Border Gateway Protocol (BGP) from
    establishing across multiple elements throughout the CenturyLink network", and that it blocked the announcement by
    a global configuration change. MacStadium's summary of the Reason For Outage gives 10:04 to 15:10 GMT and the
    rule's origin as wildcards introduced into an attempt to block a single IP. Cloudflare measured a 3.5% drop in
    global internet traffic; Tech Monitor reported restoration by 11:12 a.m. ET, and Telecompaper about seven hours to
    fix, which shows the sources' clocks do not agree.
  aftermath: >-
    The sources read report no preventive measures and no regulator's action. Cloudflare noted it had had its own
    Flowspec-related outage more than seven years earlier.
  effect_reversed: partial
model:
  modules: [Operators, Lease_A1, Peer, Observers, proposed:SubtractionReach, proposed:StagedPromotion]
  properties: [EveryStopIsAttributed, DenyAlwaysAvailable, RevokedStaysStopped, NoActionUnderFencedEpoch, ReachIsBounded]
  mutations: [M_ANON, M_REACH]
  records: [ADR-0050, ADR-0031, ADR-0065, ADR-0028, ADR-0045, ADR-0030]
  findings: [TM7, CR-34, CR-37]
  fault_class: an honest operator's deny, distributed instantly to every router, whose scope came from its pattern and whose effect cut the channel needed to remove it
sources:
  - https://blog.cloudflare.com/analysis-of-todays-centurylink-level-3-outage/
  - https://status.macstadium.com/incidents/q4qfhq90ppr8
  - https://www.techmonitor.ai/?p=346878
  - https://www.telecompaper.com/news/centurylink-network-problems-hit-internet-services-worldwide--1351978
  - https://www.theregister.com/2020/08/31/centurylink_outage/
verified: 2026-11-12
---

## Summary

At 10:03 UTC on Sunday 30 August 2020 Cloudflare's monitoring saw a sharp rise in 522 errors, meaning it could not
reach customers' servers, and its systems began moving traffic off CenturyLink/Level 3 within seconds. Between 10:03
and 10:11 it disabled CenturyLink/Level 3 in the 48 cities where it connected to it. BGP update volume rose from a
normal 1.5 to 2 MB per 15 minutes to more than 26 MB from 10:04, and stayed there.

CenturyLink's status update blamed an "offending flowspec announcement" that "prevented Border Gateway Protocol (BGP)
from establishing across multiple elements throughout the CenturyLink network". Flowspec distributes firewall rules
across a network by BGP. Per MacStadium's summary of the Reason For Outage, the rule came from "the unintentional
introduction of wildcards into an attempt to block a single IP"; Telecompaper reported that the status page placed
the problem at the Mississauga data centre. Cloudflare observed CenturyLink/Level 3 continuing to advertise routes that
had been withdrawn, so traffic kept arriving where it could not be delivered. Other tier-1 providers de-peered from
it, "it appears at CenturyLink/Level(3)'s request". CenturyLink "deployed a global configuration change to block the
problematic Flowspec announcement", and BGP came back. Cloudflare measured a 3.5% fall in global internet traffic.

## Defensive position

- **CenturyLink** apologised and said "Ensuring the reliability of our services is our top priority" (The Register).
  Its account is that the rule was an unintended error in an attempt to block one address.
- **Cloudflare** described Flowspec as genuinely useful for responding to attacks, noted its own Flowspec-related
  outage years before; its analysis was written the same day, before CenturyLink's own postmortem.

## Adversarial position

No regulator, court or claimant on record in the sources read. Against the conduct:

- **Cloudflare**: CenturyLink/Level 3 "was not honoring route withdrawals"; and if, as it suspected, the rule blocked
  BGP itself, routers would drop and relearn it repeatedly, which fits the sustained update volume and may have made it
  hard for engineers to log in to their own routers.
- **Cloudflare** also noted that many hosting providers had CenturyLink/Level 3 as their only upstream, so no
  rerouting reached them.

## Outcome

The record is the carrier's own: status updates on the day and a Reason For Outage that customers summarised. No
FCC report on this outage was found in this session. Service was restored the same day; the hours of lost
connectivity were not undone.

## Analysis

**A subtraction, made fast on purpose.** Flowspec exists to push a deny everywhere quickly, and TOPAK makes the same
choice. ADR-0050 §4: "A deny is local and attributed. It needs no quorum and no peer." ADR-0065 §1 applies a
subtraction "on receipt, before it is ordered anywhere". `Operators` proves `DenyAlwaysAvailable`. ADR-0031 already
prices the cost: "A fence storm is an availability event." ADR-0050's consequences say it outright: "Any one operator
can stop a domain, and any one with a live lease the fleet." CenturyLink is that sentence carried out by accident.

**Where TOPAK differs: scope is a type.** In `Operators`, `Revoke(o, p)` names one principal; `FenceEpoch(o)` is the
fleet fence, a separate variant that needs a live lease ("the widest stop is therefore held only by people attested
within their last lease"). A rule meant for one target cannot become the fleet fence by a wildcard in its argument,
because the variant fixes the scope. Flowspec has one kind of rule, and its reach is whatever its match fields say.
That is real protection, but narrow: TOPAK's targets are principals the mechanism issued, so a pattern over them is not
expressible. A deployment whose denies match on traffic, as a network's must, would reintroduce the pattern. No module
checks that a deny's match is no wider than its declared target; that step is outside.

**The deny cut its own off-switch.** If Cloudflare's reading is right, the rule blocked the BGP sessions that would
carry its withdrawal, and the routers flapped. CenturyLink removed it by a global configuration change, over
whatever management path still worked. The pattern is the Facebook one (2021-NET-FACEBOOK-BACKBONE): a fault in the
data plane disables the control plane needed to repair it. In TOPAK a fence travels on the plane's log and a relayed
fence is certified (ADR-0065 §1); nothing states that the channel which carries the *undoing* of a deny survives the
deny. A fleet fence in TOPAK is undone by new grants, which ADR-0050 says is "a quorum's work ... the safe direction
and ... the slow one".

**Attribution.** Every stop in TOPAK carries its author (`EveryStopIsAttributed`; ADR-0028 F2). `M_ANON`, "a stop with
no author, as the socket allows today", breaks it, and CR-34 records that the reference's operator channel is still a
socket trusted by its file mode. Cloudflare could only guess whether the rule came from CenturyLink staff or a
customer's Flowspec peering. The status page's attribution to a data centre is the nearest the public record comes.
TM7 bounds an insider with a key by attribution alone; for a release person, "a wrong act ... is recorded and not
prevented". An operator's mistaken deny is in the same position.

**Withdrawals not honoured.** Advertising withdrawn routes is a stale grant, the thing `NoActionUnderFencedEpoch` (a
fleet fence: no action at a stale epoch) and `RevokedStaysStopped` exist to forbid. Here the stale state pointed
traffic into a black hole rather than granting authority, so it is a liveness harm under a safety property's shape.

**What it suggests.** `proposed:SubtractionReach`: a bound on how many cells one deny can stop, stated by its declared
target and checked against its effect, the deny-side twin of `ReachIsBounded` in `Observers`. And a staged path even
for denies: a rule applied to a fraction of routers first. TOPAK deliberately has none, because a deny is never
supposed to need one.
