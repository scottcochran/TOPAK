---
id: 2003-NRG-NORTHEAST-BLACKOUT
title: The 14 August 2003 blackout — an alarm processor that stalled silently, and a control room that did not know it was blind
kind: incident
date: 2003-08-14
sector: energy
setting: FirstEnergy's control room and GE XA/21 energy management system, Akron, Ohio; MISO as reliability coordinator; the Eastern Interconnection of the US and Ontario
concerns: [monitoring, timing, cascading-failure, human-in-the-loop, sensing, feedback, accountability]
rules_at_time:
  - document: NERC Operating Policy 2 (as the Task Force cites it)
    clause: Section A
    paraphrase: after a contingency a system has 30 minutes to re-adjust so that it can withstand the next contingency
  - document: NERC operating requirements on monitoring equipment (Task Force, violation 7)
    clause: operational monitoring
    paraphrase: a control area's monitoring equipment must be adequate to alert operators to important deviations in operating conditions and the need for corrective action
analogue:
  - record: ADR-0039
    clause: "§1, §4, §5"
    note: liveness is a heartbeat with a watermark; a fresh heartbeat with an unchanged watermark is presence, not progress; the correlator is never coupled
  - record: ADR-0051
    clause: "§3"
    note: a correlator computes named folds over facts, and a finding carries its evidence, so a second reader can recompute it
  - record: ADR-0065
    clause: title
    note: a peer's report is labelled ingress, and nothing a peer originates enables anything
  - record: ADR-0045
    clause: "§2"
    note: the posture is that failure only subtracts; here the subtracting direction (doing nothing) was the dangerous one
actors:
  - party: GE XA/21 alarm and event processing routine at FirstEnergy
    role: monitor
    fault: omission
    note: stalled at about 14:14 on a race condition and stopped producing alarms, while the rest of the EMS kept collecting and forwarding valid data
  - party: FirstEnergy control-room operators
    role: operator
    fault: contested
    note: the Task Force found they did not know they were working without alarms and used outdated information to discount warnings from others
  - party: FirstEnergy IT/EMS support staff
    role: maintainer
    fault: omission
    note: paged on each server failure; did not tell the operators; restarted the primary server without confirming that alarms worked
  - party: FirstEnergy
    role: operator
    fault: contested
    note: the Task Force's first three groups of causes, tree growth in rights-of-way among them
  - party: MISO
    role: supervisor
    fault: honest-error
    note: its state estimator lacked a line outage's data and did not solve; cause 4
  - party: AEP, PJM and MISO operators
    role: peer
    fault: honest
    note: called FirstEnergy with information that conflicted with its operators' picture
  - party: GE Energy
    role: vendor
    fault: contested
    note: found and patched the race condition; disputed that its software caused the blackout
  - party: US-Canada Power System Outage Task Force
    role: investigator
    fault: none-alleged
detection:
  means: [peer, operator]
  latency: hours
trace:
  - step: outside:peer-monitor-blind
    at: from about 12:15 EDT
    note: MISO's state estimator cannot assess conditions for most of 12:15 to 15:34; a line's status was not linked to it, its five-minute trigger was turned off for troubleshooting and not re-enabled, and Stuart-Atlanta's loss at 14:02 was missing
  - step: outside:generator-trip
    at: 13:31 EDT
    note: Eastlake 5 trips
  - step: Heartbeat
    at: about 14:14 EDT
    note: the alarm process stalls on a race condition and stops completing alarms; the EMS stays up and its inputs queue. Presence without progress, live under M_MARK
  - step: outside:failover-carries-the-stall
    at: 14:41 and 14:54 EDT
    note: the primary server fails; the stalled alarm application moves intact to the backup, which fails 13 minutes later
  - step: outside:restart-checks-presence-not-function
    at: 15:08 EDT
    note: warm reboot; diagnostics show the computer and all expected processes running; the alarm system stays frozen and nobody confirms it with the operators
  - step: outside:strip-charts-flatline
    at: during the server outages
    note: chart pens show the last valid value; the Task Force found no indication any operator noticed
  - step: outside:line-contacts-tree
    at: 15:05:41, 15:32:03, 15:41:35 EDT
    note: Harding-Chamberlin, Hanna-Juniper and Star-South Canton 345 kV lines trip at or below their emergency ratings
  - step: outside:peer-reports-discounted
    at: 14:32 to 15:45 EDT
    note: AEP, MISO and PJM call; FE operators were not aware of line outages until about 15:45
  - step: outside:no-load-shed
    at: by 15:46 EDT
    note: at least 1,500 MW around Cleveland and Akron would have had to be dropped; none was
  - step: outside:cascade
    at: 16:05:57 to 16:13 EDT
    note: Sammis-Star trips; within seven minutes the cascade spreads; by 16:13 more than 508 generating units at 265 plants are lost
counterfactual:
  by: FirstEnergy's EMS with an alarm on its own alarm processor's progress, which the Task Force says an EMS "can also be set up" to raise and FE's did not have
  trace:
    - step: Heartbeat
      at: 14:14 EDT
      note: the processor is present and its backlog grows
    - step: Refuse
      at: within T_obs of 14:14
      note: in Coupling the backlog refuses the next admit; read for a control room, the stall is announced instead of hidden
    - step: outside:manual-scanning-and-peer-check
      at: from 14:14 EDT
      note: operators know to scan SCADA points by hand and to believe AEP's 14:32 call
    - step: outside:load-shed-before-cascade
      at: before 15:46 EDT
      note: the act the Task Force names; an effect, not a refusal
  holds: [UnreadBounded, NoAdmitWithoutLiveObserver]
outcome:
  by: US-Canada Power System Outage Task Force (final report); NERC
  date: 2004-04
  summary: >-
    The Task Force found four groups of causes: FirstEnergy and ECAR failed to assess and understand the inadequacies
    of FE's system, particularly voltage instability around Cleveland-Akron; inadequate situational awareness at
    FirstEnergy; FE's failure to manage tree growth in its rights-of-way; and the failure of reliability organisations
    to provide effective real-time diagnostic support. It found that FE's alarm and logging software failed shortly
    after 14:14, that "neither FE's control room operators nor FE's IT EMS support personnel were aware", that FE's
    EMS had no notification of its own alarm failure, and that operators "did not know that they were operating
    without alarms". It found FE lacked procedures to keep operators aware of the functional state of their
    monitoring tools and to test them after repairs. NERC identified violations including that FE's monitoring
    equipment was not adequate to alert operators. The blackout affected an estimated 50 million people and 61,800 MW
    of load; US cost estimates ran from $4 to $10 billion.
  aftermath: >-
    The Task Force's first recommendation was to make reliability standards mandatory and enforceable, with penalties;
    its twenty-second, better real-time tools for operators and reliability coordinators, with annual independent
    testing and certification of EMS and SCADA systems. GE sent every XA/21 customer, more than 100 utilities, a patch
    and a utility to repair corrupted alarm logs. Power was not restored for four days in some parts of the US, and
    parts of Ontario had rolling blackouts for more than a week.
  effect_reversed: partial
model:
  modules: [Coupling, Coupling_live, Correlator, Peer, Alone, proposed:MonitorOfMonitor]
  properties: [UnreadBounded, NoAdmitWithoutLiveObserver, AdmitStallEnds, LagNeverGates, SilenceIsCounted, PeerAddsNothing, AlonePermitsNothing]
  mutations: [M_MARK]
  records: [ADR-0039, ADR-0051, ADR-0065, ADR-0045, ADR-0062, ADR-0050]
  findings: [CR-2, CR-37, CR-57, TM13]
  fault_class: a monitor that crashed silently while appearing up, an operator that read its silence as health, and a failure whose safe response was an act, not a stop
sources:
  - https://www.energy.gov/sites/prod/files/oeprod/DocumentsandMedia/BlackoutFinal-Web.pdf
  - https://www.theregister.com/2004/04/08/blackout_bug_report/
  - https://www.ge.com/news/press-releases/ge-energy-disputes-recent-blackout-accounts
verified: 2026-11-12
---

## Summary

On 14 August 2003 MISO's state estimator, the reliability coordinator's model of the grid, could not assess system
conditions for most of the period from 12:15 to 15:34 EDT: a line's status was not linked to it, its analyst turned
off its five-minute trigger to troubleshoot and forgot to re-enable it, and it lacked the status of the Stuart-Atlanta
line, which tripped on a tree at 14:02. At 13:31 EDT FirstEnergy's Eastlake 5 unit
tripped. Shortly after 14:14 the alarm and logging function of FE's GE XA/21 energy management system stopped
producing alarms. The rest of the EMS kept collecting valid data and passing it to MISO and AEP. At 14:41 the
primary server hosting the alarm application failed, the application moved, still stalled, to the backup, and the
backup failed at 14:54. FE's IT staff were paged at each failure and did not tell the operators. At 15:08 they
restarted the primary server; its diagnostics showed every expected process running, and the alarm system remained
frozen. Strip charts driven by the EMS went on scrolling the last valid value.

Between 15:05:41 and 15:41:35 three FE 345 kV lines touched trees grown into their clearances and tripped, each at or
below its emergency rating. AEP, MISO and PJM called FE about trips that FE's operators did not see; the operators
were not aware of line outages until about 15:45. By 15:46 the Task Force judged that only dropping at least 1,500 MW
of load around Cleveland and Akron might have averted the blackout, and no such effort was made. Sammis-Star tripped
at 16:05:57. Within seven minutes the cascade spread across much of the northeastern US and Ontario; by 16:13 more
than 508 generating units at 265 plants had been lost. The outage affected an estimated 50 million people.

## Defensive position

- **GE Energy** (13 February 2004): "We take strong exception to recent claims that imply our software was the cause
  of the blackout"; operators at monitoring points "had access to the accurate information the system was designed to
  deliver".
- **On the bug:** GE's Mike Unum said XA/21 had run "in excess of three million online operational hours in which
  nothing had ever exercised that bug"; its window was "measured in milliseconds" (The Register). FirstEnergy's
  spokesman said "This fault was so deeply embedded."
- **For the operators**, the Task Force itself places the cause in the tools and procedures: FE had no back-up
  visualisation, no procedure to keep operators aware of their tools' state, and no EMS alarm on the alarm system's
  failure.

## Adversarial position

- **The Task Force:** inadequate situational awareness was "a principal cause"; operators "used the outdated system
  condition information they did have to discount information from others"; IT staff "did not confirm that the alarm
  system was again working properly with the control room operators".
- **NERC** identified violations, among them that FE's monitoring equipment was not adequate to alert its operators.
- **On vegetation and planning**, the Task Force found tree contact the common cause of the line outages, and FE's
  voltage criteria and planning studies inadequate.

## Outcome

The Task Force's final report (April 2004) is the finding on record (front matter). GE and a contractor found the
race condition in a code audit about eight weeks after the event and reproduced the failure in GE's laboratory; two
processes could gain write access to a shared structure at once, and the alarm application looped while its input
queue grew (The Register). GE patched every XA/21 customer. Power was restored over hours to days.

## Analysis

**The alarm processor is ADR-0039's Observer, and the failure is `M_MARK`.** ADR-0039 §1 defines liveness as a
heartbeat *and* a watermark: `live(o)` needs a fresh heartbeat and `seq − mark < K`. FE's alarm process was present
(the server ran, the console was up, the reboot's diagnostics passed) and made no progress (events queued unread
until the buffers overflowed). The glossary's line is exact: "a fresh heartbeat with an unchanged watermark renews
`T_obs` and nothing else". `Coupling` under `M_MARK`, where liveness tests the heartbeat and not the watermark, is the
rule FE's EMS and its IT staff applied at 15:08, and `UnreadBounded` is the property that fails under it. TOPAK's
design would have caught this stall. It is the one fault in this inventory the corpus's own mutation names.

**But TOPAK's response is the wrong direction for a grid.** Coupling refuses the Thinker's next admit when its
Observer stalls (`NoAdmitWithoutLiveObserver`), and `Coupling_live` proves the stall ends when the Observer catches up
(`AdmitStallEnds`). Read literally, FE's operators would have been refused switching actions from 14:14. What the
grid needed by 15:46 was an act: shedding 1,500 MW. ADR-0045's posture, "failure can only subtract", assumes that
doing less is safe. In an interconnected grid under voltage collapse, doing nothing is what fails. The useful part of
coupling is that the refusal is visible: the operator learns at once that the monitor has stalled. The counterfactual
keeps that half and discards the refusal. `proposed:MonitorOfMonitor` would state it as its own property: a monitor's
loss of progress is announced to every person who relies on it within a bound, as a fact on the log, whatever else
follows. The Task Force's own words are the spec: an EMS "can also be set up to alarm them if the alarm system itself
fails".

**Three readers had the truth.** The EMS went on sending accurate data to MISO and AEP, who called. That is a
correlator: a second reader of the same facts (ADR-0051 §3: a finding "carries its evidence" so another reader can
recompute it). In TOPAK the correlator is never coupled (ADR-0039 §4; `LagNeverGates` in `Correlator`), so it never
blocks anything; its findings are denies. FE's operators discounted the calls because their own (stale) picture
disagreed. `Peer` proves `PeerAddsNothing`: a peer's report can only narrow what a stack decides. That is the right
rule against a lying peer (TM13). Here the peers were right and the subject was blind, and the act the peers' reports
should have prompted was an addition. No record says what a principal should do when its own monitor and an honest
peer disagree, and `SilenceIsCounted` charges a miss to a correlator, not to a monitor that went quiet.

**Alone without knowing it.** In the overlay a vehicle that stops hearing its plane is *alone* and loses its lease
"at once" (ADR-0062 §5); `Alone` proves `AlonePermitsNothing`. The test is the vehicle's own clock against ticks it has
applied: progress, not presence. FE's control room had stopped hearing its grid at 14:14 and had no such test. The
overlay's answer, permit nothing, is again the subtractive one; for a control room it would have meant handing
control to someone who could see.

**The corpus has the same disease in places.** CR-57 records that four of the corpus's checkers "pass, or stay
silent, on a failure", and CR-37 that until Coupling_live no liveness property existed. CR-2's original phrasing,
"detection fails open", is the blackout's Group 2 cause in one line. ADR-0039 closed three of CR-2's four cases for
Observers. It did not close them for the corpus's own tooling.

**A reboot that checked the wrong thing.** IT restarted the server and checked that processes ran. ADR-0050 §4
requires a live peer for an operator's add; nothing in the corpus requires that a repaired monitor be shown to make
progress before it is trusted again. The Task Force's cause 2D, that FE "lacked procedures to test
effectively the functional state of its monitoring tools after repairs were made", is a property no module states.
MISO's analyst turning off the state estimator's trigger to troubleshoot, and not turning it back on, is the same
failure as Buncefield's check lever: a monitor disabled by its own maintenance.
