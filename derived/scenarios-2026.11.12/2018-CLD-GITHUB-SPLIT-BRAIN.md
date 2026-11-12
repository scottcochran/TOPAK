---
id: 2018-CLD-GITHUB-SPLIT-BRAIN
title: GitHub, 21 October 2018 — a 43-second partition, a cross-region failover by quorum, and writes on both coasts
kind: incident
date: 2018-10-21
sector: cloud
setting: GitHub's MySQL metadata clusters, managed by Orchestrator across a US East Coast data center, a US West Coast data center and an East Coast public cloud region
concerns: [quorum, partition, consensus, authority, configuration-change, rollback, cascading-failure, monitoring]
rules_at_time:
  - document: GitHub's MySQL high-availability design (as described in its post-incident analysis)
    clause: Orchestrator automated failover
    paraphrase: Orchestrator, running Raft among nodes in several locations, could detect a failed primary and promote a replica in another data center, including across regions; it did so "as configured"
  - document: GitHub's MySQL replication (as described in its post-incident analysis)
    clause: replication between coasts
    paraphrase: writes taken by a primary reached replicas in the other region by replication that could lag, so a primary could hold seconds of writes no replica had
analogue:
  - record: ADR-0062
    clause: "§5"
    note: a vehicle that stops hearing its plane loses its lease at once and permits no actuation; nothing like this bound the East Coast primary's writes
  - record: ADR-0031
    clause: "§2, §5"
    note: the fence is the consensus log's index at grant, and an action under a fenced lease is rejected by the mechanism ahead of policy
  - record: ADR-0068
    clause: "TM6"
    note: '"A certificate needs a quorum of the current membership, so at most one side grants"; the residual is a mesh split too small to admit anything'
  - record: ADR-0059
    clause: "§1"
    note: a plane is seated under a charter it can only narrow; GitHub's fix, no promotion across regions, is a narrower charter for the failover automaton
actors:
  - party: GitHub network maintenance
    role: maintainer
    fault: none-alleged
    note: replacing failing 100G optical equipment cut connectivity between the East Coast hub and the primary East Coast data center for 43 seconds
  - party: Orchestrator (Raft quorum of West Coast and East Coast public cloud nodes)
    role: automation
    fault: honest
    note: GitHub says its actions "behaved as configured, despite our application tier being unable to support this topology change"
  - party: East Coast MySQL primaries
    role: automation
    fault: none-alleged
    note: held a brief period of writes, several seconds' worth, never replicated West
  - party: GitHub engineering and incident response
    role: operator
    fault: none-alleged
    note: chose data integrity over availability, paused webhooks and Pages builds, restored from backups, failed forward and later back
detection:
  means: [automated-monitor, operator]
  latency: minutes
trace:
  - step: outside:link-cut-during-maintenance
    at: 22:52 UTC, 21 October
    note: 43 seconds without connectivity between the East Coast hub and the primary East Coast data center
  - step: GoAlone
    at: 22:52 UTC
    note: Alone.tla's step, here the East Coast data center losing its quorum; Orchestrator there began stepping down as Raft leader
  - step: Permit
    at: 22:52 UTC
    note: under M_ALONEACTS; the East Coast primaries held a brief period of writes not replicated West. The post does not say exactly when they were taken
  - step: outside:quorum-promotes-replica-missing-writes
    at: 22:52 UTC onward
    note: the West Coast and public cloud Orchestrator nodes formed a quorum and failed clusters over to West Coast primaries that lacked those writes
  - step: outside:writes-resume-on-new-primary
    at: from the restoration of connectivity, for nearly 40 minutes
    note: the application tier wrote to the West Coast primaries; the two sides had diverged
  - step: outside:lock-deployment-tooling
    at: 23:07 UTC
    note: responders manually locked internal deployment tooling; status yellow at 23:09, red shortly after
  - step: outside:pause-writes-for-integrity
    at: 23:19 UTC
    note: webhook delivery and GitHub Pages builds paused
  - step: outside:restore-from-backup-and-fail-forward
    at: 22 October, 06:51 to 16:24 UTC
    note: restored East Coast clusters from backups, caught up replication from the West Coast, failed back at 16:24
  - step: outside:reconcile-diverged-writes
    at: after 23:03 UTC, 22 October
    note: status green at 23:03 UTC; GitHub was still analysing logs to decide which writes could be reconciled automatically and which needed outreach to users
counterfactual:
  by: a write authority leased against hearing the quorum, and a failover charter that excludes another region
  trace:
    - step: GoAlone
      at: 22:52 UTC
      note: the East Coast primary loses its lease at once, as ADR-0062 §5 has a vehicle do
    - step: outside:write-refused-while-alone
      at: 22:52 UTC
      note: Alone.tla's AlonePermitsNothing, read for a database primary; what it costs is 43 seconds of refused writes
    - step: outside:promotion-only-within-region
      at: 22:52 UTC
      note: GitHub's first change; a charter narrower than the old one
  holds: [AlonePermitsNothing, CharterNarrows]
outcome:
  by: GitHub (post-incident analysis, by Jason Warner)
  date: 2018-10-30
  summary: >-
    GitHub said the 43-second loss of connectivity led to 24 hours and 11 minutes of degraded service. Orchestrator's
    quorum failed clusters over to the West Coast; several seconds of East Coast writes had not replicated, and the
    West Coast primaries then took nearly 40 minutes of writes, so the data centers could not simply be resynchronised.
    GitHub chose data integrity over availability, restored from backups, and failed back. It reported no user data
    lost, with reconciliation of a few seconds of writes still in progress. One of the busiest clusters had 954 writes
    in the affected window. More than 5 million webhook events and 80,000 Pages builds were queued; about 200,000
    webhook payloads passed an internal time-to-live and were dropped.
  aftermath: >-
    Orchestrator to be configured to prevent promoting database primaries across regional boundaries; a status page
    showing individual components; an active/active/active design that tolerates the loss of one facility; more
    systematic testing of assumptions and trade-offs; and investment in fault injection and chaos engineering.
  effect_reversed: partial
model:
  modules: [Alone, Lease_A1, Federation, proposed:ReplicatedWrite]
  properties: [AlonePermitsNothing, NoActionUnderFencedEpoch, CharterNarrows]
  mutations: [M_ALONEACTS, M_FENCE]
  records: [ADR-0062, ADR-0031, ADR-0059, ADR-0068, ADR-0005, ADR-0056, ADR-0058]
  findings: [TM6]
  fault_class: a crash-tolerant quorum chose a leader correctly while the data it led was replicated outside the quorum
sources:
  - https://github.blog/news-insights/company-news/oct21-post-incident-analysis/
  - https://www.infoq.com/news/2018/11/github-incident-analysis
verified: 2026-11-12
---

## Summary

At 22:52 UTC on 21 October 2018, maintenance to replace failing 100G optical equipment cut connectivity between
GitHub's US East Coast network hub and its primary East Coast data center. It was restored after 43 seconds.

GitHub ran its MySQL clusters under Orchestrator, which uses Raft. During the cut, Orchestrator in the East Coast data
center began stepping down. Orchestrator nodes on the West Coast and in an East Coast public cloud region formed a
quorum and failed clusters over, so that writes went to West Coast primaries. The East Coast servers held a brief
period of writes, several seconds' worth, that had not replicated West. Once connectivity returned, the application
tier wrote to the new West Coast primaries for nearly 40 minutes.

Alerts began at 22:54. At 23:02 responders found topologies that contained only West Coast servers; at 23:07 they
locked internal deployment tooling; at 23:09 the status went yellow, and red shortly after. At 23:19 GitHub stopped jobs that
write metadata and paused webhook delivery and Pages builds. The East Coast application tier could not tolerate the
cross-country latency to West Coast primaries, so GitHub restored East Coast clusters from backups (several were back by
06:51 UTC on 22 October), caught up replication, and failed back at 16:24. Status returned to green at 23:03 UTC, 24
hours and 11 minutes after the cut.

## Defensive position

**GitHub's analysis**, by Jason Warner, defends the response rather than the topology:

- Orchestrator's actions "behaved as configured". The failover was the system doing what it was set up to do.
- Once the sides had diverged, GitHub decided to protect data integrity before site usability and recovery time,
  and kept the writes the West Coast had taken rather than discard them. Pausing webhooks and Pages was part of that
  choice.
- No user data was lost. The writes in the window were being reconciled, with outreach to users where automatic
  reconciliation was not possible.

## Adversarial position

No outside party is on record against GitHub. **GitHub's own analysis** names what failed:

- Orchestrator was configured to promote across regions although the application tier was "unable to support this
  topology change". It called the cross-country latency "a major contributing factor".
- Public estimates of recovery time were wrong, because replication catch-up did not progress linearly.
- InfoQ's report quotes GitHub that "the two data centers had diverged and could not be easily synced", and GitHub's
  note that leader election within a region is generally safe.

## Outcome

GitHub's post-incident analysis (30 October 2018) is the finding. It reported no user data lost, reconciliation of a
few seconds of writes still in progress, 954 writes in the affected window on one of the busiest clusters, more than 5
million webhook events and 80,000 Pages builds queued, and about 200,000 webhook payloads dropped after passing an
internal TTL, which GitHub then raised. It committed to stop cross-region primary promotion, a component-level status
page, an active/active/active design, more systematic testing of assumptions, and chaos engineering. The divergence
was resolved by failing forward and then back; whether every diverged write was reconciled is not in the sources read.

## Analysis

**The quorum was right, and that is the lesson.** TM6 says a certificate needs a quorum of the current membership,
"so at most one side grants". Orchestrator had exactly that property: the side with the quorum promoted, the other
stepped down. The failure lay elsewhere. Raft agreed on who led; the data each primary held was replicated outside
that agreement. A leader can be chosen correctly and still lack writes the old leader acknowledged.

**In TOPAK the authority and the data are the same log.** ADR-0031 §2 makes the fence the consensus log's index at
grant, and ADR-0005 keeps ordering out of the transport. An admit takes effect at its log position and is void at
apply if its lease ended first. A write the minority side took after losing quorum would not be committed. So for the
mechanism's own state, this split brain cannot occur: `NoActionUnderFencedEpoch` (Lease_A1, broken by `M_FENCE`) is
the property. But that is the mechanism's state. A database a TOPAK tool writes to is a downstream system, and ADR-0056
§8 puts downstream authorisation in an excluded row (T-0045-39). TOPAK does not say how a downstream store replicates,
and would not have changed GitHub's MySQL topology.

**Where the analogy holds: going alone.** ADR-0062 §5 says a vehicle that stops hearing its plane loses its lease at
once and permits no actuation. Alone.tla checks it: `AlonePermitsNothing` fails under `M_ALONEACTS`, where going alone
does not end the lease. The East Coast primaries are the `M_ALONEACTS` case. Whatever they took in the window, they
took with no lease tied to hearing the quorum. ADR-0062 also states the cost: denial is always available to a link
adversary (TM2), here as 43 seconds of refused writes. GitHub's analysis does not say whether it would have paid that.

**The failover automaton had a charter, and it was too wide.** GitHub's first fix, no promotion across regions,
narrows what the automaton may do. In ADR-0059 §1 terms that is a narrower charter, and Federation.tla's
`CharterNarrows` is the property such a change keeps. TOPAK would route a narrowing as a cheap change; it is
also the change that made the system safer.

**What the corpus cannot express.** No module has a replicated write whose acknowledgment precedes its replication.
`proposed:ReplicatedWrite` would be the property GitHub lost: a promotion never makes a replica primary while a write
acknowledged by the old primary is absent from it. It is a property of a downstream system, so it belongs in a
deployment's specification graph (ADR-0058) as an added node, not in the archetype. The outside steps are the rest:
`quorum-promotes-replica-missing-writes`, `writes-resume-on-new-primary`, `reconcile-diverged-writes`, and the
response steps, which are operations and are outside the pattern by design.
