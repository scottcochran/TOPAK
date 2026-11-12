---
id: 2022-TEL-ROGERS-OUTAGE
title: Rogers, 8 July 2022 — a filter removed in phase six of seven, a core with no overload limit, and a management network on the same core
kind: incident
date: 2022-07-08
sector: telecom
setting: Rogers Communications' shared IP core (wireless and wireline), Canada; reviewed for the CRTC by Xona Partners
concerns: [configuration-change, deployment, interlock, emergency-path, cascading-failure, human-in-the-loop]
rules_at_time:
  - document: Rogers' change-management process, as the Xona Partners review describes it (executive summary, July 2024)
    clause: risk rating of a change
    paraphrase: a change rated high-risk gets extra checks such as lab testing and higher-level approvals; a risk algorithm may lower the rating, and a low rating removes them
  - document: Rogers' IP core upgrade plan (Rogers' submission to the CRTC, July 2022)
    clause: seven phases over several weeks
    paraphrase: the core upgrade was done in seven phases; the change that failed was the sixth, to three distribution routers
analogue:
  - record: ADR-0030
    clause: "§5"
    note: floor revisions are classified mechanically; a relaxation or an incomparable change needs anchor issuance as well as promotion, so the author does not choose the authority path
  - record: ADR-0024
    clause: "§2"
    note: the quorum rule is a mechanism constant; "this quorum cannot change its own rules", and nothing in it decays with a run of successes
  - record: ADR-0052
    clause: "§1, §6"
    note: an emergency path that needs a provider fails when the provider does; drills prove the path
  - record: ADR-0045
    clause: "§2"
    note: a delegated component's failure can only subtract; the missing overload limit was a subtraction nobody had configured
actors:
  - party: Rogers Communications (network engineering and operations)
    role: operator
    fault: honest-error
    note: Xona attributes the outage to an error in configuring the distribution routers; staff removed an ACL policy filter "to clean up" files
  - party: Rogers' change-management risk algorithm
    role: automation
    fault: contested
    note: downgraded the upgrade from high to low risk after the earlier phases succeeded; Xona says the resulting lack of scrutiny contravened industry norms
  - party: Rogers' core routers
    role: automation
    fault: crash
    note: flooded with routing information and stopped processing traffic; no overload protection was configured
  - party: Xona Partners
    role: investigator
    fault: none-alleged
    note: commissioned by the CRTC in September 2023
  - party: CRTC
    role: regulator
    fault: none-alleged
detection:
  means: [automated-monitor, customer, operator]
  latency: minutes
trace:
  - step: Promote
    at: weeks before 8 July
    note: phases one to five of the core upgrade succeed; the risk algorithm lowers the change's rating from high to low (Xona)
  - step: outside:risk-rating-decays-with-success
    at: before phase six
    note: a low rating means no lab testing and no higher-level approval; the change's authority path is chosen by its history, not its content
  - step: Promote
    at: 04:43 EDT, 8 July
    note: the phase-six change to three distribution routers removes a routing filter, "and allowed for all possible routes to the Internet" to pass (Rogers to the CRTC). Read as a floor revision this is a relaxation, which FloorRouting routes to issuance
  - step: outside:route-flood-overloads-core
    at: 04:45 EDT
    note: the distribution routers propagate abnormal volumes of routes; the core routers, with no overload limit, stop processing traffic. Wireless, wireline, Interac and 9-1-1 calling are affected
  - step: outside:management-network-on-failed-core
    at: from 04:45
    note: the management network depended on the IP core; staff could not reach it remotely, critical sites had no third-party connectivity, and staff used Rogers' own phones (Xona)
  - step: outside:root-cause-unknown-14-hours
    at: until afternoon
    note: without router logs staff "could not pinpoint the root cause for about 14 hours" (Xona)
  - step: outside:controlled-router-restarts
    at: afternoon and evening
    note: gateway, core and distribution routers restarted in a controlled order to restore wireless, including 9-1-1, enterprise and cable (Rogers)
counterfactual:
  by: a change process that classifies each change by what it permits, not by the record of the change before it, and a core limit that does not live in a removable filter
  trace:
    - step: Route
      at: before phase six
      note: the new configuration permits routes the old did not; it is a relaxation and goes to the stronger authority path with its tests
    - step: IssueAndPromote
      at: after review
      note: the change proceeds only with the extra authority, or is rewritten as a tightening
    - step: outside:overload-limit-in-core
      at: always
      note: a protection in the core that no edge change removes; Xona says an overload limit could have prevented the failure
  holds: [NoWideningWithoutIssuance, FloorNeverVacuous]
outcome:
  by: CRTC, on the Xona Partners assessment; Rogers' own submission to the CRTC
  date: 2024-07-04
  summary: >-
    Rogers told the CRTC in July 2022 that a configuration change, phase six of seven of a core upgrade, deleted a
    routing filter on three distribution routers, flooding the core with routes until it stopped processing traffic.
    Xona's review, published as an executive summary in July 2024, found that staff removed an ACL policy filter, that
    the change-management process had downgraded the change's risk after earlier phases succeeded so that it got
    insufficient scrutiny and testing, that the core routers had no overload protection, that the management network
    depended on the failed core, and that the root cause took about 14 hours to find. It said the outage "was not the
    result of a design flaw in the Rogers core network architecture". The CRTC wrote on 4 July 2024 that, based on
    Xona's findings, "the measures taken by Rogers have addressed the cause of the outage".
  aftermath: >-
    Rogers corrected router configurations, added overload safeguards, built a separate management network, added
    third-party connectivity at critical sites, introduced validation tools and a new risk-assessment algorithm, and
    began separating its wireless and wireline cores, which Xona called a work in progress. Ottawa required carriers to
    agree on mutual assistance and emergency roaming, and a memorandum of understanding followed in September 2022.
    Rogers replaced its chief technology officer on 21 July 2022 and credited customers five days of service.
  effect_reversed: partial
model:
  modules: [FloorRouting, RulesFloorNV_rev5, Emergency, Operators, proposed:StagedPromotion, proposed:RecoveryPath]
  properties: [NoWideningWithoutIssuance, FloorNeverVacuous, P1_Unanimity, EmergencyNeverCoupled]
  mutations: [M_ROUTE]
  records: [ADR-0030, ADR-0024, ADR-0052, ADR-0045, ADR-0050, ADR-0012]
  findings: [CR-36, CR-37, CR-17]
  fault_class: a change routed to a lighter approval path by the success of its predecessors; a protection that was one removable filter; operations tooling that shared the failed core
sources:
  - https://www.theregister.com/2022/07/25/canadian_isp_rogers_outage/
  - https://mobilesyrup.com/2024/07/05/july-2022-rogers-outage-report-crtc/
  - https://www.iphoneincanada.ca/2024/07/05/2022-rogers-outage-14-hours-find-root-cause-crtc/
  - https://globalnews.ca/news/9960209/rogers-outage-crtc-xonapartners-investigation
  - https://en.wikipedia.org/wiki/2022_Rogers_Communications_outage
verified: 2026-11-12
---

## Summary

Rogers was upgrading its shared IP core in seven phases over several weeks. Rogers told the CRTC that at 4:43 a.m.
EDT on 8 July 2022 the sixth phase changed three distribution routers and "deleted a routing filter and allowed for
all possible routes to the Internet" to pass. The routers propagated abnormal volumes of routes through the core,
which flooded and, from 4:45 a.m., stopped processing traffic. More than 12 million customers lost wireless and
wireline service. Interac's debit network went down with it, and mobile 9-1-1 calls on the network failed.

Xona Partners' review for the CRTC adds that the filter was an ACL policy filter, removed "to clean up" files; that
the upgrade had been rated high-risk and was downgraded to low by Rogers' risk algorithm after the first five phases
succeeded, so that lab testing and higher-level approvals were not required; that the core routers had no overload
limit, leaving the filter as the only protection; and that the management network depended on the IP core, so staff
could not reach it remotely, critical sites had no backup connectivity from other providers, and staff relied on
Rogers' own failed phones. It took about 14 hours to identify the root cause. Engineers restored service by
restarting gateway, core and distribution routers in a controlled order, from the afternoon into the evening.

## Defensive position

**Rogers** (its submission to the CRTC, and statements reported by Global News):

- The change was one phase of a planned, weeks-long upgrade, and the earlier phases had gone well.
- It had completed "a full review of our network", implemented "several enhancements and safeguards", partnered
  with Cisco, and introduced predictive simulation for testing.

**Xona**, on the architecture: the outage "was not the result of a design flaw in the Rogers core network
architecture"; a shared core for wireless and wireline is common practice, though it widened the outage's scope.

## Adversarial position

**Xona Partners**, for the CRTC:

- Downgrading the risk rating after successful phases led to insufficient scrutiny and testing, contrary to industry
  norms.
- Change management, including audits of the change's parameters, did not catch the faulty configuration.
- "The July 2022 outage exposed the absence of overload protection on the core network routers."
- The management network's dependence on the core, and the lack of redundant connectivity, prolonged the outage and
  contributed to misdiagnosis in its first hours.

## Outcome

The CRTC commissioned Xona in September 2023 and published its executive summary in July 2024. On 4 July 2024 it
wrote that Rogers' measures "have addressed the cause of the outage", and asked Rogers to report on separating its
wireless and wireline cores. Rogers said it had implemented all of Xona's recommendations. Service was restored; the
hours without 9-1-1 and payments were not.

## Analysis

**The risk algorithm chose the authority path, and ADR-0030 §5 exists to stop that.** In TOPAK a floor revision is
classified mechanically: equivalent or tightening goes by ordinary promotion; relaxation, or incomparable, needs an
anchor issuance as well. The record's reason is exactly Rogers' failure: it "removes a reviewer's assertion from a
spot where Build principals ... choose the authority path for their own change". `FloorRouting` checks it:
`NoWideningWithoutIssuance` says a floor permitting anything its predecessor did not is never deployed without
issuance, and `M_ROUTE`, which lets an incomparable revision "ride an ordinary promotion", breaks it. Rogers' change
permitted "all possible routes" where the old configuration permitted fewer. Classified by content it is a
relaxation; classified by the history of phases one to five it was low risk. ADR-0024 §2 adds that the quorum rule
"cannot change its own rules": nothing in TOPAK's promotion decays with a record of successes.

**But the analogy needs care.** `FloorRouting` classifies floor revisions over a model of their meaning, and assumes
the implication check is right. A router's route filter is closer to a bundle than to the floor, and bundles narrow
by promotion alone; removing a bundle's deny widens towards the floor and needs only ADR-0024's ordinary promotion. So
TOPAK would have caught this only if the protection lived in the floor. That is the second lesson.

**One filter was the only protection.** Xona says the core had no overload limit; the policy filter at the edge was
the whole defence. TOPAK's answer to "a protection one ordinary change can remove" is to put it where removal needs
the expensive path: the floor, resident and verified (ADR-0012), with `FloorNeverVacuous` keeping it from becoming
always-allow. Read the other way, a core overload limit is a subtraction, and under ADR-0045 a component whose failure
can only subtract is delegated and needs nothing. The corpus would have classed the absent limit as harmless. CR-36,
"every number is a placeholder", is the same point from inside: TOPAK's own limits are placeholders, never measured.

**Optus is the mirror.** Sixteen months later, Optus' routers did have overload limits, and those limits are what
took the network down (2023-TEL-OPTUS-OUTAGE). A safety limit absent and a safety limit present both ended in a
national outage. No module states what a limit must preserve when it trips.

**Staged in time, not in space.** The upgrade was staged by phase, each applied to the whole core. Phase six went to
three distribution routers that fed every core router; there was no subset of the core to fail first.
`proposed:StagedPromotion` would state promotion to a declared fraction first, with the rest on the prior digest.

**The repair path ran over the failure.** The management network depended on the IP core, and staff depended on
Rogers' own phones. ADR-0052 §1 makes the emergency key independent of single sign-on for this reason, and says no
more; nothing in the corpus requires the emergency seat's channel to be independent of what it repairs. Rogers
answered with a separate management network and third-party connectivity, and Ottawa with emergency roaming between
carriers: both are the independence `proposed:RecoveryPath` would state. CR-17's point, that every control ending in
a person presumes a present and equipped person, is the 14 hours spent without logs.
