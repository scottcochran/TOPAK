---
id: 2005-ICS-BUNCEFIELD
title: Buncefield oil depot, 11 December 2005 — a gauge that flatlined and an independent switch left disabled by its own test
kind: incident
date: 2005-12-11
sector: industrial-control
setting: Tank 912, Hertfordshire Oil Storage Ltd (Total UK and Chevron joint venture, managed day to day by Total), Buncefield depot, Hemel Hempstead
concerns: [sensing, interlock, monitoring, emergency-path, configuration-change, supply-chain, cascading-failure]
rules_at_time:
  - document: Control of Major Accident Hazards Regulations 1999 (COMAH)
    clause: regulation 4
    paraphrase: an operator of a top-tier site must take all measures necessary to prevent major accidents and limit their consequences to persons and the environment
  - document: Health and Safety at Work etc Act 1974
    clause: sections 2 and 3
    paraphrase: duties to ensure, so far as reasonably practicable, the safety of employees and of persons not in one's employment
  - document: HOSL tank filling practice (as the Competent Authority describes it)
    clause: ATG alarms
    paraphrase: three high-level alarms ("user high", "high", "high-high") set below the IHLS; each supervisor used them in his own way, and all control-room staff could change any ATG parameter, alarm settings included
analogue:
  - record: ADR-0062
    clause: "§4"
    note: an extent that is not a count of ticks is a measurement, and the measuring source is a trust root for it
  - record: ADR-0068
    clause: "§2 (T-0068-4, T-0068-8); §6"
    note: the governor's measure of an extent and the effector interlock are trust roots whose identity nothing issues; §6 records that as a finding
  - record: ADR-0045
    clause: "§2"
    note: a component is delegated only if its failure can only subtract; a protection whose failure removes the protection fails in the other direction
  - record: ADR-0052
    clause: "§6"
    note: the emergency path is exercised, by a real activation of a drill seating, at least once per domain per epoch
  - record: ADR-0039
    clause: "§1"
    note: relaxing a monitor's thresholds is an anchor issuance and a promotion; tightening is an ordinary promotion
actors:
  - party: Hertfordshire Oil Storage Ltd (HOSL)
    role: operator
    fault: honest-error
    note: convicted of a COMAH regulation 4 offence and pleaded guilty to a pollution offence
  - party: Total UK Ltd
    role: supervisor
    fault: honest-error
    note: pleaded guilty to HSWA s.2 and s.3 and pollution offences
  - party: Automatic tank gauge (servo gauge) on Tank 912
    role: sensor
    fault: byzantine
    note: stuck 14 times between 31 August and 11 December 2005; on the night it reported a level that stopped rising while the tank filled
  - party: Independent high-level switch (IHLS), TAV Engineering
    role: safety-system
    fault: omission
    note: its check lever, without the padlock, could be left in or fall into a position that disabled the switch
  - party: TAV Engineering Ltd
    role: vendor
    fault: honest-error
    note: convicted under HSWA s.3; did not communicate the padlock's safety role
  - party: Motherwell Control Systems 2003 Ltd
    role: maintainer
    fault: honest-error
    note: convicted under HSWA s.3; installed the IHLS without the padlock, believing it an anti-tamper device
  - party: British Pipeline Agency Ltd
    role: counterparty
    fault: honest-error
    note: controlled the UKOP South line feeding the tank; pleaded guilty to COMAH and pollution offences
  - party: HOSL control-room supervisor on shift
    role: operator
    fault: none-alleged
detection:
  means: [public, operator]
  latency: minutes
trace:
  - step: outside:measure-of-extent-unreliable
    at: 31 August to 11 December 2005
    note: the servo gauge sticks 14 times; supervisors "stow" it or call Motherwell; the cause is never found and the faults are not all logged
  - step: outside:interlock-disabled-by-its-own-test
    at: from 1 July 2004
    note: new IHLS fitted without the padlock that held its check lever in the operating position; after periodic tests the lever is left where the switch cannot act
  - step: outside:upstream-flow-not-visible
    at: 18:50, 10 December
    note: unleaded petrol from the UKOP South line, controlled elsewhere, starts filling Tank 912; HOSL had no SCADA view of that line's state or rate
  - step: Heartbeat
    at: 03:05 onward
    note: the ATG "flatlines" and keeps reporting a level below every alarm; a reading present and not progressing, which Coupling's M_MARK treats as live
  - step: outside:upstream-rate-change-unannounced
    at: shortly before the explosion
    note: the UKOP South rate rises from 550 to 900 m3/h without the supervisors' knowledge
  - step: outside:interlock-does-not-trip
    at: 05:37
    note: the level passes the tank's capacity; the IHLS does not register it; petrol spills from roof vents
  - step: outside:stop-control-not-wired
    at: standing condition
    note: the red emergency "stop" on the ATG mimics had never been fitted into the system; several supervisors did not know
  - step: outside:vapour-cloud-ignites
    at: 06:01
    note: the cloud reaches about 360 m across; the fire alarm is pressed, the firewater pump starts and the cloud explodes. Over 250,000 litres had escaped
counterfactual:
  by: HOSL, with the IHLS's lever padlocked in its operating position as TAV's design required, or with the ATG's later inconsistency alarm on level against filling data
  trace:
    - step: Heartbeat
      at: 03:05
      note: the gauge still flatlines
    - step: outside:progress-checked-against-flow
      at: 03:05 onward
      note: an inconsistency between a static level and an open inlet raises an alarm; a progress check, not a presence check
    - step: outside:interlock-trips
      at: before 05:37
      note: the IHLS sounds its alarm and closes the inlet valves
  holds: [UnreadBounded]
outcome:
  by: Major Incident Investigation Board (final report 2008); COMAH Competent Authority (HSE and Environment Agency); St Albans Crown Court
  date: 2010-07-16
  summary: >-
    The Competent Authority found the immediate cause to be the failure of both the ATG and the IHLS as the level in
    Tank 912 rose: the gauge had stuck intermittently since August, and the IHLS needed a padlock to keep its check
    lever in the working position, which "the switch supplier did not communicate" to the installer or the operator.
    It found that the bunds and drainage also failed, and that keeping the process operating had become the primary
    focus over process safety. At St Albans Crown Court on 16 July 2010 Total UK was fined £3.6m on three counts, HOSL
    £1.45m on two, BPA £300,000 on two, and TAV and Motherwell £1,000 each, with £4.081m costs. The judge spoke of
    "slackness, inefficiency and a more-or-less complacent approach to matters of safety", and said cost cutting was
    not put forward as a major feature of the prosecution case.
  aftermath: >-
    The Competent Authority, industry and unions agreed improved standards for sites storing large volumes of
    gasoline, with progress monitored by the regulator, and process safety leadership principles for board-level
    engagement. TAV modified the switch with a pin that stops the lever travelling below horizontal. The fire burned
    for five days; over 40 people were injured and none died; pollutants reached the chalk aquifer.
  effect_reversed: "no"
model:
  modules: [Coupling, PlaneClock, Operators, Release, proposed:MeasuredExtent]
  properties: [UnreadBounded, EntryEndsAtExtent, WatchdogHolds, DenyAlwaysAvailable, IrreversibleIsAPersons]
  mutations: [M_MARK, M_NOWATCHDOG, M_NOEXTENT]
  records: [ADR-0062, ADR-0068, ADR-0045, ADR-0052, ADR-0039, ADR-0050, ADR-0049, ADR-0051]
  findings: [CR-2, CR-36]
  fault_class: two protection layers each failing silently and in the permissive direction, each relied on because the other was unreliable
sources:
  - https://www.icheme.org/media/10706/buncefield-report.pdf
  - https://processengineering.co.uk/article/2003068/buncefield-trio-are
  - https://processengineering.co.uk/article/2003662/buncefield-trial-end
verified: 2026-11-12
---

## Summary

From 18:50 on Saturday 10 December 2005 unleaded petrol from the UKOP South pipeline was delivered into Tank 912 at
the HOSL site, which held 6 million litres. The UKOP lines were controlled from elsewhere; HOSL supervisors had no
SCADA view of whether they were running or at what rate. The tank had an automatic tank gauging system (ATG) with
three level alarms, and an independent high-level switch (IHLS) set higher, meant to close the inlet valves and sound
an alarm.

At 03:05 on 11 December the ATG display "flatlined": the reading stopped rising while the tank filled, so none of its
three alarms could sound. The gauge had stuck 14 times since the tank returned to service on 31 August. The IHLS,
fitted on 1 July 2004, had a check lever that a padlock was meant to hold in its operating position; the padlock had
not been fitted, and after testing the lever could be left in, or fall into, a position that disabled the switch.
At 05:37 petrol began to overflow from the roof vents. A vapour cloud spread to about 360 metres across in windless
conditions. Tanker drivers and members of the public raised the alarm; the fire alarm button was pressed at 06:01,
starting the firewater pump, and the cloud exploded almost at once. More than 250,000 litres had escaped. Over 20
tanks burned for five days. More than 40 people were injured and none died.

## Defensive position

As recorded by the Competent Authority and the court:

- **Motherwell** staff believed the padlock was for security, an "anti-tamper" device, and the Authority accepted
  that they "ought to have been able to rely on TAV to tell them".
- **TAV** had designed the switch so that its function could be tested routinely.
- **HOSL's supervisors** worked under rising throughput, 12-hour shifts, no fixed breaks and no control over two
  of the three pipelines; one had asked for a back-up IHLS because the ATG was unreliable. The Authority said their
  confusion over which line was filling which tank "is easily understood".
- **On consequence:** the Authority found the explosion's severity "far greater than could reasonably have been
  anticipated based on knowledge at the time".
- **On motive:** the judge noted that cost cutting was not put forward as a major feature of the prosecution's case.

## Adversarial position

The **Competent Authority** (HSE and the Environment Agency):

- There were "clear signs that the equipment was not fit for purpose but no one questioned why"; fault logging was
  inadequate and the Operations Manager did not know how often the gauge stuck.
- "There was no tank filling system worth its name"; each supervisor used the alarms in his own way, sometimes above
  high-high.
- HOSL did not act as an "intelligent customer" of its contractors, and had no management-of-change process for the
  new switches.
- The failings of each protection layer increased reliance on the other: "the overall control of the tank filling
  process was seriously weakened".

## Outcome

Five companies were convicted or pleaded guilty, and were sentenced at St Albans Crown Court on 16 July 2010
(front matter). The Competent Authority's report, *Buncefield: Why did it happen?*, published once proceedings ended,
draws on Baker's Texas City report: protection "should not rely on operator response to alarms" and "overfill
protection should be independent of normal operational monitoring". It says the report identifies no new learning,
only principles long known.

## Analysis

**The gauge is ADR-0062 §4's measured extent.** An overlay entry declares an extent, "one act; a number of ticks;
or a distance or a region, which the governor measures", and "an extent that is not a count of ticks is a
measurement", with its source a trust root. A tank fill is an entry whose extent is a volume. ADR-0068 §2 lists the
row: T-0068-4, the governor's measure of an extent, fails as "an entry runs past what was voted". Buncefield is that
row's failure, on the record. `PlaneClock` proves `EntryEndsAtExtent` for an extent counted in ticks, and says
explicitly that "distance and region are measurements (ADR-0068)" and are not modelled. A volume is the same.
`proposed:MeasuredExtent` would model the measurement as a trust-root reading that may stick, with a property that a
measured extent is also bounded by a count the governor keeps itself (here: time at the inlet's rate).

**A flatline is presence without progress.** The ATG went on reporting a value. That is Coupling's `Heartbeat`
with the watermark not rising, and the glossary's "presence is not progress": under `M_MARK`, liveness tests the
heartbeat and not the watermark, and `UnreadBounded` fails. The ATG's later versions could alarm on an inconsistency
between level and filling data. That is the watermark test applied to a sensor: a reading that does not move while
the inlet is open is not live. The corpus applies the rule to Observers of agents, not to sensors of the world, and
its Observers watch the agent's acts, not the tank.

**The IHLS failed in the permissive direction.** ADR-0045 §2 admits a component to the trusted base only if its
failure can only subtract, or its identity is issued. A protection is a subtraction mechanism, so its own failure
adds: the shutdown it would have made is gone. ADR-0068 §6 says four of its rows, the interlock and the measure of an
extent among them, are trust roots "whose identity nothing issues", and records that as a finding. Buncefield is an
example of that finding with nothing hypothetical about it. The switch's identity was fixed by a purchase order, its
configuration by a padlock nobody knew was safety-critical, and its state after each test by where a lever happened to
rest. `Release` rests every property on its interlock ("the interlock is the only check this module relies on"), and
`IrreversibleIsAPersons` holds only while the interlock does what the model says. No module has an interlock that
can be left disarmed.

**The two layers were not independent.** The Authority's sentence, that each layer's unreliability increased
reliance on the other, is the one TOPAK should take. The corpus counts layers in series (floor and bundle, admit and
Observer) and proves each. It does not have a property that two layers' failures are uncorrelated, or a correlator
fold over a protection's own fault history. Fourteen stuck-gauge events in three months, partly logged, is what
ADR-0051's "a finding carries its evidence" would make countable if the facts were on a log at all.

**The stop button that was never wired.** `Operators` proves `DenyAlwaysAvailable`: an operator in force can always
revoke. The model's deny is an action of the mechanism. At Buncefield the deny was a red button on a mimic display,
connected to nothing, and "Motherwell staff never tested it". ADR-0052 §6 is the corpus's answer for its emergency
path: a drill is "a real activation", so the path is proved by use. It applies to emergency seatings, not to deny
controls. A deny that is drawn but not connected is a claimed field in ADR-0049's sense.

**Thresholds anyone could move.** All control-room staff could change the ATG's alarm settings, and each supervisor
used the levels his own way. ADR-0039 §1 makes `T_obs` and `K` floor values: relaxing one is an anchor issuance and
a promotion, tightening one an ordinary promotion. That is the routing a tank's alarm levels lacked. CR-36 notes that
TOPAK's own thresholds are still placeholders.

**Where the pattern stops.** TOPAK would not have measured the tank or closed a valve. The episode shows that the
overlay's trust roots (T-0068-4, T-0068-8) are exactly where a real plant failed, and that ADR-0068 §6 is right to
leave its condition "Not met".
