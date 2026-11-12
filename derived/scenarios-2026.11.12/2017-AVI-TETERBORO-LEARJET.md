---
id: 2017-AVI-TETERBORO-LEARJET
title: Learjet 35A N452DA, Teterboro, 15 May 2017 — an unapproved first officer flying, a late handover, and no go-around
kind: incident
date: 2017-05-15
sector: aviation
setting: Trans-Pacific Air Charter Learjet 35A N452DA, Part 91 positioning flight Philadelphia to Teterboro, ILS runway 6 circle to runway 1, Teterboro, New Jersey
concerns: [authority, delegation, human-in-the-loop, monitoring, emergency-path, actuation, accountability]
rules_at_time:
  - document: Trans-Pacific General Operations Manual
    clause: "11.3.3, SIC positions"
    paraphrase: a newly hired second-in-command is SIC-0 and may act only as pilot monitoring; acting as pilot flying needs SIC-1 or higher, first under a check airman or management pilot on non-revenue flights
  - document: Trans-Pacific standard operating procedures
    clause: "6.1.1, stabilized approach"
    paraphrase: stabilized by 1,000 ft above the airport (on path, within 10 kt of target speed, configured, briefed); aligned with the runway by 500 ft; otherwise go around
  - document: Trans-Pacific standard operating procedures
    clause: "5.1.7, approach speeds"
    paraphrase: on a visual approach fly VREF + 20 kt until established on final, then VREF + 10 kt
  - document: 14 CFR 135.330
    clause: crew resource management training
    paraphrase: Part 135 operators must train crews in eight CRM topics, including the authority of the pilot-in-command, with no further detail
analogue:
  - record: ADR-0043
    clause: "§2"
    note: only a thinker seat holds Actuate; an observer seat holds Consult and Report; the grant path and the floor each refuse an alphabet outside the kind
  - record: ADR-0050
    clause: "§4"
    note: a successor grant must be the last lease's width or narrower
  - record: ADR-0052
    clause: "§1, §2"
    note: the only path that seats a person to act at once is an emergency seating, activated by a roster's quorum for one round
  - record: ADR-0062
    clause: "§7"
    note: the terminal behaviour, including return on a voted route, is part of the seating; the stack does not choose it
  - record: ADR-0038
    clause: "§5"
    note: a finding from any Observer takes effect; no agreement is sought
actors:
  - party: Pilot-in-command
    role: supervisor
    fault: byzantine
    note: in the schema's sense of acting outside the rules; the NTSB found his decision to let the SIC fly "improper and contrary to company standard operating procedures" and his decision to continue the approach "inappropriate"; no finding of intent
  - party: Second-in-command
    role: operator
    fault: honest-error
    note: SIC-0, authorized as pilot monitoring only; struggled with airspeed and control, asked twice to hand over control, called "airspeed" repeatedly, and did not call a go-around
  - party: Trans-Pacific Air Charter (Trans-Pacific Jets)
    role: supervisor
    fault: omission
    note: no safety programs to find procedural non-compliance; did not monitor two pilots who had needed extra simulator sessions; no Learjet check airman for SIC upgrades
  - party: Federal Aviation Administration
    role: regulator
    fault: omission
    note: its principal operations inspector had never done a Part 135 en route inspection; the NTSB found its oversight procedures ineffective
  - party: Enhanced ground proximity warning system
    role: monitor
    fault: none-alleged
    note: called "five hundred" and "sink rate, pull up"; the PIC told the SIC to disregard the first
detection:
  means: [investigation]
  latency: months
trace:
  - step: outside:pilots-paired-after-training-difficulties
    at: 2016-2017
    note: both pilots had needed additional simulator sessions; neither was monitored afterwards; the company's other Learjet SIC-0 had flown five or six positioning legs as PF
  - step: Grant
    at: PHL, about 4 minutes before takeoff
    note: RunSeats under M_KIND; "hand on your yoke" issues Actuate (pilot flying) to a seat whose kind (SIC-0) allows Consult and Report; OnlyThinkersActuate fails
  - step: Act
    at: PHL to TEB
    note: the SIC flies with continuous coaching; the PIC, coaching, misses checklists and approach setup that are his PM duties
  - step: outside:no-approach-briefing
    at: en route
    note: weather not rechecked within 3 hours; flight plan altitude and time incompatible; no briefing; navigation not set for the cleared approach
  - step: outside:fixes-crossed-high
    at: DANDY and the final approach fix
    note: hundreds of feet above the published altitudes
  - step: outside:circle-begun-late
    at: "1529:07"
    note: 1 nm from the runway 6 threshold, 2.8 nm past the final approach fix, too late to align with runway 1 stabilized
  - step: outside:control-transfer-unacknowledged
    at: "1529:15"
    note: the SIC says "your flight controls"; the PIC does not answer; no record of who held the controls until 1529:26
  - step: Finding
    at: "1529:18 and 1529:21"
    note: Observers.tla's finding; EGPWS "five hundred", which the PIC told the SIC to disregard, then "sink rate, pull up"; below 500 ft and not aligned, which the SOPs made a go-around
  - step: outside:control-transfer-to-pic
    at: "1529:26"
    note: '"I''m gonna give ya your controls, okay?" / "alright. my controls"; about 17 seconds before the end of the recording'
  - step: Act
    at: "1529:26 to 1529:39"
    note: the PIC turns left toward runway 1 at 450 ft; 35 degrees of bank, 111 kt against a SOP target of 139 kt, wind 360 at 16 gusting 32 kt; the admit continues over the finding, breaking DenyByAnyOf
  - step: Finding
    at: "1529:35 to 1529:43"
    note: the SIC, now PM, calls "V-ref", "add airspeed", and "airspeed" five times
  - step: outside:aerodynamic-stall-at-low-altitude
    at: "1529:40 to 1529:44"
    note: the PIC says "stall"; the airplane rolls nearly inverted and strikes a building and parking lot half a mile south of runway 1
counterfactual:
  by: the PIC, flying the leg himself as the SOPs required, and either pilot calling a go-around when the approach failed the stabilized criteria
  trace:
    - step: Grant
      at: PHL, before takeoff
      note: the PIC holds pilot flying; the SIC-0 holds pilot monitoring; RunSeats without M_KIND
    - step: Finding
      at: "1529:07, or at the latest 1529:18"
      note: '"go around": circling 1 nm from runway 6, or below 500 ft and not aligned; under ADR-0038 §5 the PM''s call takes effect without the PF''s agreement'
    - step: EndLease
      at: same
      note: the clearance to land ends when the gate fails; nothing is granted by the ending
    - step: Recover
      at: same
      note: the terminal behaviour fixed in advance, "return on a voted route", which here is the published missed approach; the PF does not choose it
  holds: [OnlyThinkersActuate, DenyByAnyOf, ExpiryGrantsNothing, TerminalNeverWaits]
outcome:
  by: National Transportation Safety Board (AAR-19/02)
  date: 2019-03-12
  summary: >-
    The NTSB determined the probable cause to be "the pilot-in-command's (PIC) attempt to salvage an unstabilized
    visual approach, which resulted in an aerodynamic stall at low altitude". Contributing were the PIC's decision
    to allow an unapproved SIC to act as pilot flying, his inadequate preflight planning, and the crew's lack of an
    approach briefing; and Trans-Pacific's lack of safety programs to identify and correct poor performance and
    non-compliance, and the FAA's ineffective Safety Assurance System procedures. It found the PIC's coaching
    distracted him from his monitoring duties, and that his focus on aligning with the runway distracted him from
    "multiple indications of decreasing stall margin". Both pilots died; no one on the ground was injured.
  aftermath: >-
    The NTSB recommended that the FAA require Part 135 operators to monitor pilots with training deficiencies,
    issue CRM guidance for Part 135, and review Learjet 35A manuals for gust wind additives, and reiterated earlier
    recommendations for flight data monitoring and safety management systems for Part 135 operators. Trans-Pacific
    reported 6-monthly route checks, training on intentional non-compliance, a planned SMS, and a third-party auditor.
  effect_reversed: "no"
model:
  modules: [RunSeats, Operators, Observers, Alone, Emergency, proposed:SeatHandover]
  properties: [OnlyThinkersActuate, SuccessorNeverWidens, LeaseWithinSeating, DenyByAnyOf, ExpiryGrantsNothing, TerminalNeverWaits, EmergencyLeaseHasARosterQuorum]
  mutations: [M_KIND, M_WIDEN, M_STACKCHOOSES]
  records: [ADR-0043, ADR-0037, ADR-0050, ADR-0052, ADR-0062, ADR-0038, ADR-0028, ADR-0068]
  findings: [TM7, CR-2]
  fault_class: a senior principal granting a junior an alphabet its seating forbids, a handover with no instant, and monitors whose findings the actor could overrule
sources:
  - https://www.ntsb.gov/investigations/AccidentReports/Reports/AAR1902.pdf
  - https://planeandpilotmag.com/learjet-stall-on-short-final-to-teterboro/
  - https://avweb.com/flight-safety/ntsb-unstabilized-approach-caused-teterboro-crash/
verified: 2026-11-12
---

## Summary

*Note on scope.* This entry was first written as the best match for a YouTube video, "How the Best Captain Would
Have Saved This Learjet" (channel "Unfolded"), while its transcript could not be retrieved. The transcript, supplied
later the same day, shows the video is about a different accident, the Learjet 60 lost over South Florida on
1 November 2026 ([2026-AVI-LEARJET-60-STORM-UPSET](2026-AVI-LEARJET-60-STORM-UPSET.md)), and its thought experiment
([2026-AVI-CAPTAIN-HAIL-THOUGHT-EXPERIMENT](2026-AVI-CAPTAIN-HAIL-THOUGHT-EXPERIMENT.md)). This entry is kept on its
own merits, for its seat-handover question, and nothing here is attributed to the video. It is written from the NTSB
record.

On 15 May 2017, about 15:29 EDT, a Learjet 35A operated by Trans-Pacific Air Charter departed controlled flight on a
circling approach to runway 1 at Teterboro and struck a commercial building and parking lot. Both pilots died. It was
the crew's third flight of the day, a positioning flight from Philadelphia under Part 91.

The second-in-command (SIC) was SIC-0 under company policy, authorized as pilot monitoring only. About four minutes
before takeoff the pilot-in-command (PIC) told him "hand on your yoke", and the SIC flew the leg while the PIC
coached him on checklists, airspeed and nearly every turn and altitude change. The crew did not brief the approach,
did not set the navigation equipment for it, and crossed the approach fixes hundreds of feet high. They began the
circle at 15:29:07, 1 nm from the runway 6 threshold. At 15:29:15 the SIC said "your flight controls"; the PIC did
not answer. At 15:29:18 the EGPWS called "five hundred", which the PIC told the SIC to disregard, then "sink rate,
pull up". Below 500 ft and not aligned with the runway, the approach met the SOPs' criteria for a go-around; neither
pilot called one.

At 15:29:26 the SIC said "I'm gonna give ya your controls, okay?" and the PIC replied "alright. my controls". He
turned left toward runway 1 at about 450 ft, reaching 35 degrees of bank and about 111 kt, against a SOP target of
139 kt and a wind of 16 kt gusting 32. The SIC called "add airspeed" and "airspeed" repeatedly. At 15:29:40 the PIC
said "stall". The last recorded sound was at 15:29:43.9.

## Defensive position

No party defended the conduct on record. **Trans-Pacific's director of operations** said the graduated SIC policy,
adopted from a previous employer, was meant to ensure SICs had acceptable skills before more responsibility, that
readiness was assessed about monthly, and that the accident SIC was not yet ready to act as pilot flying but was
improving. The company's CRM training had been approved by the FAA and covered every topic 14 CFR 135.330 requires.

## Adversarial position

**The NTSB** (board, 12 March 2019):

- The PIC's decision to let the SIC fly was "improper and contrary to company standard operating procedures", and put
  both pilots in roles they did not routinely perform; his coaching "degraded the flight crew's overall performance".
- The decision to continue was "inappropriate"; the rapid left turn "was likely the PIC's attempt to continue the
  approach to landing".
- The SIC did not apply the company's own CRM guidance that "good followership skills allow for the follower to step
  up to leader when necessary" and call a go-around.
- Without flight data monitoring, Trans-Pacific "would not have had a way to identify the flight crew's deviations".
  The FAA inspector had never conducted a Part 135 en route inspection.

**Peter Katz** (Plane & Pilot) writes that the PIC would have been better served to abandon the approach, fly the
missed approach and start over.

## Outcome

The NTSB adopted AAR-19/02 on 12 March 2019. Its probable cause is "the pilot-in-command's (PIC) attempt to salvage an
unstabilized visual approach, which resulted in an aerodynamic stall at low altitude"; it names the unapproved SIC
as pilot flying, the planning and briefing, Trans-Pacific's lack of safety programs and the FAA's oversight as
contributing. It made new recommendations on monitoring pilots with training deficiencies, Part 135 CRM guidance and
Learjet 35A wind additives, and reiterated those for flight data monitoring and SMS in Part 135. Trans-Pacific reported
added route checks, training, plans for an SMS and an outside auditor.

## Analysis

**The cockpit is a cell with two seats, and the junior seat was given the wrong alphabet.** Pilot flying is a
`thinker` seat: in Run only it holds `Actuate` (ADR-0043 §2). Pilot monitoring is an `observer` seat: `Consult` and
`Report`. The SIC's seating, SIC-0, was observer-only. "Hand on your yoke" issued `Actuate` to it, which is RunSeats'
`M_KIND` and breaks `OnlyThinkersActuate`; read with the PIC as an operator regranting within his domain, it is
Operators' `M_WIDEN`, breaking `SuccessorNeverWidens` and `LeaseWithinSeating`. TOPAK refuses that grant twice, at the
grant path and at the floor. Trans-Pacific's only enforcement was the PIC, and the record shows a second PIC doing the
same five or six times. The NTSB's FDM recommendation is the record TOPAK would have had: every admit on the floor
(ADR-0028 F1) and an Observer reading every record (ADR-0043 §4).

**TOPAK has no answer to "when must the senior seat take over".** The SIC tried to hand over at 15:29:15 and the PIC
did not answer for eleven seconds. A lease is not ended by its holder saying so, and "a timeout is never a grant"
(ADR-0062 §7): in TOPAK, for those seconds, nobody holds `Actuate`, while the airplane flies on. The only record that
seats a person to act at once is ADR-0052, an emergency seating activated by a roster's quorum for one round
(`EmergencyLeaseHasARosterQuorum`), and a person holds one seat in a round (ADR-0037 §7). Two people with seconds to
spare cannot form a quorum, and the PIC was already seated as the monitor. The seat model says who may act; it does
not say who may take over. `proposed:SeatHandover` would declare a pair of seats with a seniority, let the senior take
the thinker seat by one attributed act with no quorum, demote the other to observer in the same step, and state that
exactly one holder of `Actuate` exists at every instant. Command authority is a rule about people TOPAK would have to
write; 14 CFR 135.330 names it and gives it no content.

**The findings were advisory, and the actor overruled them.** The EGPWS call, "sink rate, pull up", and the SIC's
airspeed calls were findings; in Observers.tla any one of them blocks the next admit (`DenyByAnyOf`, ADR-0038 §5) and
needs nobody's agreement. In the cockpit the pilot flying told the monitor to disregard it. That is the CR-2 shape:
a monitor that is live, reports, and stops nothing.

**The go-around is the terminal behaviour, and the stack chose not to fly it.** A body in flight cannot stop. ADR-0062
§7 fixes in advance what happens when a lease ends: "hold, return on a voted route, land or stop", and "the stack
does not choose it". A published missed approach is exactly a voted route, and the stabilized-approach gate is the
lease's end. What the NTSB found, the PIC's "attempt to salvage", is `M_STACKCHOOSES`: the actor decided whether to
take the terminal behaviour. The counterfactual is the run in which the gate's failure ends the clearance
(`ExpiryGrantsNothing`) and the missed approach is enabled whatever the pilot flying does (`TerminalNeverWaits`).
TOPAK puts the recovery function in a trusted domain apart from the stack (T-0068-9). In a two-pilot jet it is the
same person.

**Where the pattern stops.** Stall margin, gusts and a 35-degree turn at 450 ft are physics; no module has them. TM7
fits the PIC exactly: an insider with a key who does what the seat may do, "recorded and not prevented". TOPAK's claim
here is narrower and real: it would not have let the SIC's seat fly, and it would not let the actor decide whether
the go-around happens.

**Outside steps.** `pilots-paired-after-training-difficulties`, `no-approach-briefing`, `fixes-crossed-high`,
`circle-begun-late`, `control-transfer-unacknowledged`, `control-transfer-to-pic`,
`aerodynamic-stall-at-low-altitude`. The two control-transfer steps are what `SeatHandover` would make expressible.
