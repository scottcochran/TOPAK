---
id: 2012-FIN-KNIGHT-CAPITAL
title: Knight Capital, 1 August 2012 — new code on seven of eight routers, and a repurposed flag that woke Power Peg
kind: incident
date: 2012-08-01
sector: fintech
setting: SMARS, Knight Capital Americas LLC's automated equity order router (eight servers), Jersey City, at the NYSE open
concerns: [deployment, configuration-change, interface-types, interlock, monitoring, rollback, emergency-path]
rules_at_time:
  - document: SEC Exchange Act Rule 15c3-5 (the market access rule, adopted November 2010)
    clause: "(b)"
    paraphrase: a broker-dealer with market access must establish, document and maintain risk controls and supervisory procedures reasonably designed to manage the risks of that access, and keep a written description of them
  - document: SEC Exchange Act Rule 15c3-5
    clause: "(c)(1)(i), (c)(1)(ii)"
    paraphrase: the controls must systematically prevent orders that exceed pre-set credit or capital thresholds in the aggregate, and prevent erroneous orders
  - document: SEC Exchange Act Rule 15c3-5
    clause: "(e)"
    paraphrase: the firm must regularly review the controls' effectiveness, and the CEO must certify annually that they comply with (b) and (c)
analogue:
  - record: ADR-0031
    clause: "§4"
    note: the lease names its bundle revision, and a new bundle reaches a live principal only by ending its round; which revision each principal runs is therefore on the record
  - record: ADR-0044
    clause: "§3"
    note: a sidecar's decision counts only if its revision is in the mechanism's set of verified revisions; nothing read here removes a revision from that set when a later one is promoted
  - record: ADR-0062
    clause: "§1, §2"
    note: the governor, which is mechanism and not the application, permits each entry under a lease and counts it against the lease's count
  - record: ADR-0050
    clause: "§4"
    note: an operator's deny needs neither a quorum nor a peer; a stop is always available and always attributed
  - record: ADR-0024
    clause: "Consequences, Negative"
    note: promotion gains attribution and authorization properties, not safety properties
actors:
  - party: Knight Capital Americas LLC
    role: operator
    fault: contested
    note: settled with the SEC without admitting or denying the findings
  - party: Knight technician deploying the RLP code
    role: maintainer
    fault: honest-error
    note: did not copy the new code to one of the eight servers; no second technician reviewed the deployment, and no written procedure required one
  - party: The eighth SMARS server
    role: automation
    fault: byzantine
    note: an arbitrary failure; old Power Peg code, its fill count moved away in 2005, ran on orders carrying the repurposed flag
  - party: BNET reject e-mails and PMON
    role: monitor
    fault: omission
    note: 97 e-mails naming "Power Peg disabled" before the open were not designed as alerts and not read; PMON was post-execution, human-watched and lagged
  - party: NYSE
    role: counterparty
    fault: none-alleged
    note: cancelled trades in six stocks, per Reuters
  - party: US Securities and Exchange Commission
    role: regulator
    fault: none-alleged
detection:
  means: [operator]
  latency: minutes
trace:
  - step: outside:dead-code-left-callable
    at: 2003 to 2005
    note: Power Peg unused from 2003; in 2005 its cumulative-quantity check was moved earlier in the code and Power Peg was not retested
  - step: outside:partial-promotion
    at: from 27 July 2012
    note: RLP code placed on servers on successive days; seven of eight received it, and no one noticed the eighth
  - step: outside:flag-meaning-changed
    at: 27 July to 1 August
    note: the RLP code reused the flag that had activated Power Peg; on the eighth server the flag still meant Power Peg
  - step: outside:alert-not-read
    at: 08:01 to 09:30
    note: 97 BNET e-mails referencing SMARS and "Power Peg disabled", sent to a group of staff
  - step: Effect
    at: 09:30 onward
    note: for 212 parent orders the eighth server sends child orders without regard to fills; Intent's governor counts each entry, and with the count gone this is M_NOCOUNT, which breaks EveryEffectHasALease
  - step: outside:rollback-widens-fault
    at: during the 45 minutes
    note: Knight uninstalled the new code from the seven correct servers, and incoming parent orders then activated Power Peg there too
  - step: outside:orders-stopped
    at: about 45 minutes after the open
    note: over 4 million executions in 154 stocks, more than 397 million shares; net long about $3.5 billion in 80 stocks, net short about $3.15 billion in 74
  - step: outside:trades-cancelled
    at: 1 August
    note: NYSE cancelled trades in six stocks executed 30% or more from the opening price, per Reuters, and none in the others
counterfactual:
  by: the count held by the governor rather than by SMARS, and a Knight operator seated under ADR-0050 who fences at the first sign
  trace:
    - step: Grant
      at: 09:30
      note: each parent order a lease under an intent, with a count equal to its shares
    - step: Effect
      at: 09:30
      note: child orders permitted and counted by the governor
    - step: RefuseEffect
      at: when the count is spent
      note: the next child order is refused whatever the router's own code believes about fills
    - step: FenceEpoch
      at: minutes after the open
      note: an operator ends every live lease at once; it subtracts, so it needs no quorum and no peer
  holds: [EveryEffectHasALease, DenyAlwaysAvailable, EveryStopIsAttributed]
outcome:
  by: US Securities and Exchange Commission
  date: 2013-10-16
  summary: >-
    The SEC found that Knight violated Rule 15c3-5 and Section 15(c)(3) of the Exchange Act, and Rules 200(g) and
    203(b) of Regulation SHO. Among the findings: no controls reasonably designed to prevent erroneous orders at the
    point just before SMARS sent them, such as a comparison of orders leaving SMARS with those entering it; no
    pre-set firm-wide capital thresholds linked to order entry; no technology governance sufficient to ensure
    orderly deployment or to prevent activation of code no longer intended for use; no written incident-response
    procedures; and a 2012 CEO certification that certified "processes" rather than compliance. Knight was censured,
    paid a $12 million civil penalty and undertook to retain an independent consultant. The SEC called it its first
    enforcement action under the market access rule.
  aftermath: >-
    The consultant's review was to cover Knight's software development lifecycle, code deployment, order routers,
    the automated pre-trade linkage of firm-wide capital thresholds to order entry, and incident response. By the
    order's date Knight had combined with GETCO to form KCG Holdings (1 July 2013).
  effect_reversed: partial
model:
  modules: [Intent, Operators, RunCoupling, Lease_A1, proposed:Rollout]
  properties: [EveryEffectHasALease, DenyAlwaysAvailable, EveryStopIsAttributed, UnreadEffectsBounded, LeaseAuthorityMonotone]
  mutations: [M_NOCOUNT]
  records: [ADR-0031, ADR-0044, ADR-0062, ADR-0050, ADR-0024, ADR-0039, ADR-0042, ADR-0060, ADR-0034]
  findings: [TM10, CR-2]
  fault_class: a partial promotion left one replica on old code whose meaning for a shared flag had changed; the fill count lived in the code that failed, and no stop was wired to anything
sources:
  - https://www.sec.gov/litigation/admin/2013/34-70694.pdf
  - https://www.sec.gov/news/press-release/2013-222
  - https://www.dailymaverick.co.za/article/2012-08-02-error-by-knight-capital-rips-through-us-stock-market/
verified: 2026-11-12
---

## Summary

To let customers take part in the NYSE's Retail Liquidity Program, which began on 1 August 2012, Knight wrote new
code for SMARS, its high-speed router that splits "parent" orders into "child" orders sent to trading venues. The
new code replaced unused code for a function called Power Peg, which Knight had stopped using in 2003. It also reused
the flag that used to switch Power Peg on. In 2005 Knight had moved Power Peg's cumulative-quantity function, which
stopped child orders once a parent was filled, to an earlier point in the code, and had not retested Power Peg.

From 27 July Knight put the new code on SMARS servers on successive days. One technician did not copy it to one of
the eight. From 8:01 a.m. on 1 August an internal system sent 97 e-mails, "BNET rejects", naming SMARS and "Power Peg
disabled"; they were not designed as alerts and were not acted on. At the 9:30 open, the seven updated servers
handled RLP orders correctly. On the eighth, the flag triggered Power Peg, which sent child orders for each parent
without regard to fills. Another part of Knight's system knew the parents were filled and did not tell SMARS.

For 212 parent orders SMARS sent millions of child orders in about 45 minutes: over 4 million executions in 154 stocks
for more than 397 million shares. Staff saw positions build in the "33 Account" at the open. In one attempt to fix it,
Knight uninstalled the new code from the seven good servers, which made those servers run Power Peg as well. When the
orders stopped Knight was net long about $3.5 billion and net short about $3.15 billion. It lost more than $460
million. Knight said in a statement that "a technology issue occurred" and told clients to route orders elsewhere.

## Defensive position

**Knight**, in the SEC's account and its own statement:

- It had controls before SMARS: its customer interface, order management system and internal execution system each
  screened for erroneous orders. A price-collar control capped child orders at 9.5% from the national best bid or
  offer, and some strategies of one trading group shut down automatically on P&L limits.
- Its compliance department assessed its controls before the rule's compliance date, and the participants concluded
  they satisfied Rule 15c3-5. The eight senior employees who sub-certified, and the CEO, believed Knight complied;
  the SEC accepted that the certification's wording error was not intentional.
- It settled without admitting or denying the findings, and the SEC took account of its remedial acts and cooperation.

## Adversarial position

**The SEC** (Andrew Ceresney and Daniel Hawke for the Division of Enforcement):

- The controls sat upstream of the component that failed. Nothing compared what left SMARS with what entered it,
  and nothing halted SMARS on its own aberrant activity.
- The 9.5% collar did not bind when prices moved less than that, and did not apply to the 212 orders, received
  before the open for the opening auction.
- The 33 Account had a $2 million gross limit linked to no automated control; PMON displayed no limits, raised no
  alerts and lagged under load.
- No written deployment procedure for SMARS, no second-technician review, and no protocol for unused code on
  production servers. Its reviews inventoried controls and did not ask what a malfunctioning router could do. "Knight
  Capital's failure to ask these questions had catastrophic consequences" (Hawke).

## Outcome

The SEC's order of 16 October 2013, on Knight's offer of settlement, found violations of Rule 15c3-5 under subsections
(b), (c)(1)(i), (c)(1)(ii), (e)(1) and (e)(2), and of Regulation SHO's marking and locate rules for the short sales
SMARS sent. Knight was censured, fined $12 million and required to retain an independent consultant. The positions
were closed at a loss of more than $460 million. NYSE cancelled trades in six stocks and let the rest stand, per
Reuters, so the market effect was undone only in part.

## Analysis

**The count was in the code that failed.** Power Peg's cumulative-quantity function was the only thing that stopped
child orders once a parent was filled, and it lived in the application. Moving it in 2005 removed the interlock without
anyone deciding to. In the overlay's `Intent` module the count is the governor's: `Effect` increments it in the same
step that permits the entry, and `RefuseEffect` fires when it is spent, whatever the stack believes. ADR-0062 §1 puts
that governor on the mechanism side. `M_NOCOUNT`, "the governor does not count", is exactly Knight's state on the eighth
server, and it breaks `EveryEffectHasALease`. This is a good fit with one caveat: `Intent` and ADR-0062 are the
command-chain overlay, Proposed, and the archetype's Run has no per-lease count of effects. Its nearest brake is
coupling: `RunCoupling`'s `UnreadEffectsBounded` holds a Thinker to at most `K` effect-bearing admits its Observer
has not read (ADR-0039 §2, ADR-0042 §2). That throttles a runaway router to its Observer's reading pace. It does not stop it unless the Observer
finds something, and an Observer that reads "child order, admitted" four million times has nothing to find.

**Partial promotion is visible, and not forbidden.** In TOPAK each lease names its bundle revision and a decision
counts only from that revision (ADR-0031 §4). A fleet in which seven principals run revision N+1 and one runs N is
therefore on the record, lease by lease, which is more than Knight had: nobody knew. But nothing in the records read
here says that every live lease in a domain must name the same revision, or that promoting N+1 retires N. ADR-0044 §3
checks a revision against the set of revisions whose signatures the mechanism has verified, and a revision signed
years ago is still in it. Power Peg was "present and callable" for nine years; TOPAK's equivalent, a promoted revision
nobody uses, would be too. `proposed:Rollout` would state two properties: every live lease in a domain names a
revision in the current promoted set, and a superseded revision is retired by an ordered act, after which no grant
names it.

**The repurposed flag is an interface-type fault.** The same bit meant RLP on seven servers and Power Peg on one. In
TOPAK a decision counts only from the revision the lease names (ADR-0031 §4, citing ADR-0033 §5), so the meaning of
a field is per revision, and a mixed fleet gives one field two meanings. ADR-0049's entry has a digest over its
interface; nothing compares the interfaces of the revisions live at once. That is `outside:flag-meaning-changed`.

**The stop existed nowhere.** The SEC found no procedure to halt SMARS on its own aberrant activity and no incident
procedure, and the attempted remedy, uninstalling the new code, spread the fault to seven more servers. Under ADR-0050
§4 a deny needs no quorum and no peer, and `Operators` proves `DenyAlwaysAvailable`: an operator whose Persona is in
force can revoke any principal in every state. `FenceEpoch` ends every live lease at once, attributed
(`EveryStopIsAttributed`). The counterfactual is that stop, made in the first minutes. What it shows is that TOPAK
makes the stop cheap and attributed, not that anyone would have pressed it: the corpus says nothing about when an
operator should, and Knight's staff spent 45 minutes diagnosing rather than stopping. The rollback is the more
interesting step. In TOPAK reverting to revision N is a grant naming N, which adds authority and goes through the
same promotion as any other; a fence subtracts and does not. The corpus's monotonicity makes "stop first" the
cheaper move by construction.

**The 97 e-mails are CR-2's case.** A monitor that reported the fault in real time, to people who did not read it,
before any harm. Coupling would not have helped: the e-mails were findings in all but name, and ADR-0007 lets a
finding subtract only if something acts on it. No record says who reads findings that are not wired to a deny.

**Where the pattern stops.** The SEC's central finding is about pre-trade capital thresholds linked to order entry,
which is a policy-floor question (a bundle's deny on an aggregate) that TOPAK can express only as a count per lease
or a budget per intent (ADR-0060 §2), not as a firm-wide position computed from fills. Fills are ingress. Promotion, as
ADR-0024 says of itself, gains attribution and authorization, not safety (TM10's row: "promotion by digest"). A
host that launches the old image where the new one was asked for is a launcher fault: at rung 1 the evidence is what
the launcher was asked to run (`Confinement`'s `Evidence`), and at rungs 2 and 3 it is the launched image, measured. Measurement would
name the old image. Whether the grant is then refused turns on whether the old image is still promoted, which is the
`Rollout` gap again, since Power Peg's code had once been in service.
