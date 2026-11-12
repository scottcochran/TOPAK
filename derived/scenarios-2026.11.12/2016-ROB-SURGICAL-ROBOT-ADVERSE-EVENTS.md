---
id: 2016-ROB-SURGICAL-ROBOT-ADVERSE-EVENTS
title: Surgical robots in FDA data, 2000-2013 — uncommanded motion, halts mid-procedure, and counts that depend on who reports
kind: case-study
date: 2016-04-20
sector: robotics
setting: teleoperated robotic surgical systems in US hospitals (Intuitive Surgical, maker of the da Vinci, the only active FDA-approved maker by a 2014 account), as reported to the FDA's MAUDE database, 2000-2013
concerns: [human-in-the-loop, actuation, interlock, emergency-path, monitoring, accountability]
rules_at_time:
  - document: FDA medical device reporting (MAUDE), as described by Alemzadeh et al.
    clause: mandatory and voluntary reporters
    paraphrase: user facilities, manufacturers and distributors must report suspected device-related adverse events; health professionals, patients and customers may; reports carry an event type and free-text narratives
  - document: FDA enforcement of reporting duties (as described by its spokeswoman, 2013)
    clause: failure to report
    paraphrase: the FDA issues warning letters to manufacturers that fail to report and can seek seizures or injunctions; it says reports alone cannot establish or compare event rates
analogue:
  - record: ADR-0028
    clause: "§1"
    note: admit decisions and stop attributions are written by the mechanism and cannot be erased; no class rests on a party's later account
  - record: ADR-0066
    clause: "§1, §3"
    note: an effect class is a declaration, and a misdeclared one "is seen by nothing here"; the person is the actor, and a stack's report to the person is untrusted ingress
  - record: ADR-0045
    clause: "§2"
    note: a component whose failure can only subtract is delegated; a halt subtracts authority whatever it costs the patient
  - record: ADR-0068
    clause: "A-0068-4, A-0068-7"
    note: each body declares a safe state its recovery reaches; what a body does other than through its entries is outside the alphabet
actors:
  - party: Robotic surgical systems
    role: automation
    fault: contested
    note: 8,061 reported malfunctions, including 1,078 events of unintended instrument operation; the authors could not establish in most reports whether the device or the team caused an injury
  - party: Intuitive Surgical
    role: vendor
    fault: contested
    note: about 98% of reports came from manufacturers and distributors; it changed its reporting practice in September 2012 and disputed a 2013 study's account of under-reporting
  - party: Surgical teams
    role: operator
    fault: honest-error
    note: reporters attributed 7.1% of injury events and 7% of deaths to operator or staff mistakes; the authors list flawed practices such as inadequate troubleshooting of technical problems
  - party: Alemzadeh, Raman, Leveson, Kalbarczyk and Iyer
    role: investigator
    fault: none-alleged
  - party: Makary and co-authors (Journal for Healthcare Quality, 2013)
    role: investigator
    fault: none-alleged
  - party: US FDA
    role: regulator
    fault: none-alleged
detection:
  means: [researcher, audit]
  latency: years
trace:
  - step: outside:fault-found-before-procedure
    at: set-up
    note: 1,019 malfunctions (10.9% of malfunctions) were caught before the procedure began
  - step: outside:uncommanded-instrument-motion
    at: during procedures
    note: 1,078 events of uncontrolled movement or spontaneous powering on or off, with 52 injuries and 2 deaths
  - step: outside:fragment-falls-into-patient
    at: during procedures
    note: 1,557 events of burnt or broken pieces falling into the patient, 119 with injury and one death; the team then searched for and retrieved them
  - step: outside:instrument-arcing
    at: during procedures
    note: 1,111 events of arcing, sparking or charring, with about 193 injuries
  - step: EndRound
    at: on a system error
    note: Lease_A1's end of round, read as the robot's own safety mechanism halting on a fault it cannot recover from; recoverable errors need a manual reset, others end robotic operation
  - step: outside:conversion-to-manual-technique
    at: after the halt
    note: 1,104 procedures were interrupted; 274 system resets, 462 conversions and 221 aborted or rescheduled procedures followed system or video errors
  - step: outside:manufacturer-files-narrative-report
    at: after the event
    note: free-text narratives; many death reports had little or no information on cause
  - step: outside:reporting-practice-reclassified
    at: September 2012
    note: Intuitive revised its MDR practice, raising instrument malfunction reports and moving some events from "other" to "serious injury"
  - step: outside:researchers-mine-narratives
    at: 2014-2016
    note: natural-language processing over 10,624 reports, with estimated procedure counts as the denominator
outcome:
  by: Alemzadeh et al., PLOS ONE (the literature; no regulator ruled)
  date: 2016-04-20
  summary: >-
    Over 2000-2013, about 1.75 million robotic procedures were performed in the US and 10,624 adverse event reports
    were filed: 144 deaths, 1,391 injuries and 8,061 device malfunctions. Injury and death events per procedure stayed
    roughly constant (mean 83.4 per 100,000). Death rates in cardiothoracic and head and neck surgery were 52.2 per
    100,000 procedures against 5.7 in gynecology, urology and general surgery (2007-2013). About 62% of injury events
    involved device malfunctions. Reported malfunctions per procedure (0.46%) were about six times lower than the 3%
    published by surgical institutions, which the authors read as under-reporting; MAUDE rates are lower bounds. The
    authors recommend better interfaces and simulator training for technical problems, safety barriers on the
    instrument workspace, monitoring engines that guide troubleshooting, and better incident logging.
  aftermath: >-
    The FDA and the manufacturer contacted the researchers after an earlier version of the study (2014). No rule
    change is attributed to the study in the sources read.
  effect_reversed: not-applicable
model:
  modules: [Release, Lease_A1, Correlator, Operators, proposed:Teleoperation, proposed:Disclosure]
  properties: [SignedByPerson, ConflictIsAFinding, EveryStopIsAttributed, SilenceIsCounted, FindingHasEvidence]
  mutations: [M_AGENTRELEASE]
  records: [ADR-0028, ADR-0066, ADR-0045, ADR-0051, ADR-0052, ADR-0062, ADR-0068]
  findings: [CR-38, TM3]
  fault_class: an effector that moves without its person's command, halts that subtract at a cost, and an incident record written later by the interested party
sources:
  - https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0151470
  - https://www.pbs.org/newshour/health/mishaps-and-deaths-caused-by-surgical-robots-going-underreported-to-fda
  - https://urologytimes.com/view/robot-maker-addresses-recent-medical-device-reports
  - https://ece.illinois.edu/news/3204
verified: 2026-11-12
---

## Summary

Alemzadeh, Raman, Leveson, Kalbarczyk and Iyer analysed every adverse event report on robotic surgical systems
posted to the FDA's MAUDE database from January 2000 to December 2013: 10,624 reports, against an estimated 1.75
million US robotic procedures. Reporters classed 144 as deaths, 1,391 as injuries and 8,061 as malfunctions. About 98%
came from manufacturers and distributors.

The study grouped malfunctions in five categories: burnt or broken pieces falling into the patient (1,557), arcing,
sparking or charring of instruments (1,111), unintended operation of instruments, such as uncontrolled movement or
spontaneous powering on or off (1,078, with 52 injuries and 2 deaths), and system errors and video or imaging
problems (787). System errors "are raised by the existing safety mechanisms of the robot" on faults it cannot recover
from, and need either a manual reset or an end to robotic operation. In 1,104 events the procedure was interrupted
for troubleshooting, a reset, conversion to an open or laparoscopic technique, or rescheduling; system and video
errors accounted for 82% of resets, 59.2% of conversions and 81.8% of aborted procedures. One reported case combined
an electronic failure, a non-recoverable error, troubleshooting and a surgeon's decision to work the camera by hand,
leading to a long procedure, loss of insufflation and injury.

Earlier, in 2013, Makary and co-authors found eight cases of inadequate reporting of da Vinci incidents, five with
no FDA report at all, and Intuitive Surgical said a rise in reports reflected its September 2012 change in reporting
practice.

## Defensive position

**Intuitive Surgical** (March and October 2013):

- The rise in reports reflected "a change in MDR reporting practices", not "a change in product performance"; the
  increase was mostly instrument malfunctions, chiefly cable breaks that need only a quick instrument change, and
  none of those reports involved reportable injuries or deaths. "We self-identified the reporting issue, notified
  the FDA and revised our practices" (Dave Rosa).
- The 2013 study gave "the misleading impression that Intuitive Surgical has systematically failed"; it "can only
  report adverse events after it becomes aware of them". It agreed a "more robust and standardized system" was needed.

**The FDA** (2013): "adverse event reports alone cannot be used to establish or compare rates of event occurrence",
and a complaint does not necessarily indicate a faulty device.

**The 2016 authors** themselves: "the vast majority of procedures were successful and did not involve any problems",
and injury and death events per procedure stayed relatively constant.

## Adversarial position

**Alemzadeh et al.**: device and instrument malfunctions "affected thousands of patients and surgical teams";
MAUDE "suffers from underreporting and inconsistencies"; narratives often do not allow contributing causes to be
identified. Ravishankar Iyer (2014): "when the malfunctions occur, the surgeon and the people around it have little
control".

**Makary** (2013): "We rely on a haphazard reporting system that uses immature data"; it is "essential that device
related complications be uniformly captured, reported and evaluated".

## Outcome

No regulator ruled. The study, published in PLOS ONE on 20 April 2016, concluded that injury and death events per
procedure had been constant, that complex specialties carried higher risk, and that malfunctions caused
complications and prolonged procedures for thousands of patients. Its rates are lower bounds. It recommended better
human-machine interfaces and simulators, workspace safety barriers, monitoring engines, and better incident logging
and investigation. The FDA and the manufacturer contacted the researchers after the 2014 version. Nothing was reversed;
nothing in the record says it could be.

## Analysis

**A teleoperated robot is the corpus's HITL taken to the limit, and the model does not reach it.** ADR-0066 makes an
irreversible effect a person's: one signed act, one effect, fresh by the plane's ticks (`SignedByPerson` in Release).
A surgeon's console streams commands continuously, every motion is meant to be the person's, and an incision is
irreversible. An instrument that moves with no command (1,078 events) is not an agent passing the interlock, which is
what `M_AGENTRELEASE` breaks; it is the effector acting by itself, which ADR-0068 places outside the alphabet
(A-0068-7) and TM3 calls the case where "the interlock is moot". `proposed:Teleoperation` would state, for a stream,
that no actuation occurs without a person's command within a declared interval before it, and that an uncommanded
actuation is a finding that halts.

**The robot's own halts are the delegated class, and they are not free.** System errors are a safety mechanism whose
failure direction is subtraction, which ADR-0045 §2 admits with no proof. The record shows what a subtraction costs a
patient on the table: 274 resets, 462 conversions, 221 aborted procedures, and a case where the long interruption was
itself the injury. ADR-0062 §7 and A-0068-4 ask each body to declare a safe state; for an open abdomen there is no
"stop", only conversion to another technique. That conversion is the emergency path, and it leaves the robot
entirely: ADR-0052 §1's "nothing here bounds what a person does elsewhere".

**The dispute is over the record, and TOPAK's floor answers half of it.** Every number here is a count of narratives
filed later, 98% by the manufacturer, whose classification changed in 2012 (Intuitive) and whose completeness was
disputed in 2013 (Makary). ADR-0028 writes admit decisions and stop attributions at the instant, by the mechanism, and
`EveryStopIsAttributed` (Operators) holds of every stop. A system error halting the robot is that class of fact. What
the floor does not fix is classification: whether an event was a "malfunction" or an "injury" is, like ADR-0066 §1's
effect class, "a declaration", and "an irreversible effect declared reversible is seen by nothing here". The same
`proposed:Disclosure` that Cruise's reports call for would make an incident report a projection of the floor, so that
the counts stop depending on who files.

**MAUDE is a correlator with one dominant reporter.** ADR-0051 §3 says a finding carries its evidence
(`FindingHasEvidence`); many death reports carried "little or no information". `SilenceIsCounted` charges a miss to a
correlator only when another correlator's finding exposes it; the institutional rate six times higher than MAUDE's is
the nearest thing to that second correlator here.

**Where the pattern stops.** TOPAK says nothing about whether robotic surgery is safer than open or laparoscopic
surgery, which this data cannot show either. Its bearing is the effector, the halt and the record.

**Outside steps.** `fault-found-before-procedure`, `uncommanded-instrument-motion`, `fragment-falls-into-patient`,
`instrument-arcing`, `conversion-to-manual-technique`, `manufacturer-files-narrative-report`,
`reporting-practice-reclassified`, `researchers-mine-narratives`. The second is `Teleoperation`'s; the last three are
`Disclosure`'s.
