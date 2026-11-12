---
id: 2018-ROB-UBER-ATG-TEMPE
title: Uber ATG test vehicle, Tempe, 18 March 2018 — a suppressed brake, a disabled AEB, and a safety operator who was not watching
kind: incident
date: 2018-03-18
sector: robotics
setting: Uber Advanced Technologies Group developmental automated driving system on a modified 2017 Volvo XC90, N. Mill Avenue, Tempe, Arizona
concerns: [human-in-the-loop, monitoring, interlock, sensing, timing, actuation, accountability]
rules_at_time:
  - document: Uber ATG operating procedures for vehicle operators (as described in NTSB HAR-19/03)
    clause: operator protocols
    paraphrase: after engaging the ADS the operator monitors the driving environment and the ADS, takes control in emergencies, hovers hands over the wheel and foot over the brake, and tags unusual events on the HMI tablet
  - document: Uber ATG policy (as described in NTSB HAR-19/03)
    clause: cell phone use
    paraphrase: using a cell phone while operating a test vehicle was a violation of ATG policy, which the inward-facing camera could have revealed
  - document: Arizona Executive Order 2018-04 (1 March 2018)
    clause: ADS vehicles with a person inside
    paraphrase: such vehicles must follow federal and state law and ADOT policy; no other safety-focused requirement, and no application or approval process for testing
analogue:
  - record: ADR-0039
    clause: "§1, §2, §5"
    note: no Run admit without a live cell Observer, where live means a fresh heartbeat and a watermark within K; coupling cannot tell an honest Observer from one that only looks present
  - record: ADR-0038
    clause: "§5"
    note: Observers combine by any-of; more Observers never lower safety and may lower availability
  - record: ADR-0032
    clause: "§4"
    note: "W + L + D < T_irrev, with D, the human response budget, an organizational commitment and L unmeasured"
  - record: ADR-0062
    clause: "§7"
    note: a body in motion still has to do something when its lease ends; the terminal behaviour is part of the seating and the stack does not choose it
actors:
  - party: Uber Advanced Technologies Group
    role: operator
    fault: omission
    note: the NTSB found inadequate risk assessment, ineffective oversight of operators and no countermeasures for automation complacency; the Yavapai County Attorney found "no basis for criminal liability"
  - party: ATG automated driving system
    role: automation
    fault: byzantine
    note: detected the pedestrian 5.6 s before impact and never classified her as a pedestrian or predicted her path; it reported no sensor or system failure
  - party: Vehicle operator
    role: operator
    fault: contested
    note: the NTSB's probable cause is her failure to monitor while distracted by her phone; she pleaded guilty to endangerment in 2023; her lawyers said she was looking at an Uber messaging app
  - party: Volvo City Safety forward collision warning and AEB
    role: safety-system
    fault: none-alleged
    note: deactivated whenever the ADS was engaged, by ATG's design with Volvo's agreement
  - party: Pedestrian
    role: public
    fault: honest-error
    note: the NTSB listed her crossing outside a crosswalk, impaired, as a contributing factor
  - party: Arizona Department of Transportation
    role: regulator
    fault: omission
    note: the NTSB cited its insufficient oversight of ADS testing
detection:
  means: [investigation]
  latency: months
trace:
  - step: outside:second-operator-removed
    at: September-October 2017
    note: ATG consolidated the driver and the event tagger into one operator, to field more vehicles; the NTSB found this raised the sole operator's task demands and removed a redundancy
  - step: outside:aeb-deactivated-in-autonomous-mode
    at: standing design
    note: radar frequency interference and a brake module with no priority rule between two braking commands were the stated reasons
  - step: GrantT
    at: about 19 minutes before impact
    note: autonomous mode engaged for about 19 minutes before the crash; no condition on the operator's attention, i.e. RunCoupling under M_NOCOUPLE
  - step: Stale
    at: throughout the trip
    note: the inward camera shows the operator looking toward the console where her phone was; from about 6 s before impact her gaze stayed down until about 1 s before
  - step: Actuate
    at: -5.6 s to -1.2 s, 44 mph
    note: the ADS keeps driving; an effect admitted with no live Observer, which breaks NoEffectWithoutLiveObserver
  - step: outside:reclassification-drops-tracking-history
    at: -5.6 s to -1.2 s
    note: vehicle, then alternating vehicle and other, then bicycle, other, bicycle; each new class discarded the track, and "other" was treated as static
  - step: outside:action-suppression-withholds-braking
    at: -1.2 s to -0.2 s
    note: a 1-second hold on braking, with no alert, adopted "because of concerns about false alarms"
  - step: outside:alert-and-gradual-slowdown
    at: -0.2 s
    note: collision unavoidable within 0.71 g, so the design sent an alert and began a gradual slowdown, not maximum braking
  - step: outside:operator-takes-steering
    at: -0.02 s, 39 mph
    note: the operator steers and disengages the ADS; she brakes after impact
  - step: Revoke
    at: 19 March 2018
    note: Lease_A1's fleet fence, as ATG's own act; it stopped testing on public roads in every centre
  - step: outside:state-suspends-testing
    at: 26 March 2018
    note: the governor of Arizona directed ADOT to suspend ATG's autonomous testing in the state
counterfactual:
  by: ATG's post-crash design, read as coupling on the operator plus an independent stop of another lineage
  trace:
    - step: Stale
      at: when the operator's gaze leaves the road
      note: a real-time attentiveness monitor, which ATG added after the crash, is the heartbeat
    - step: RefuseEffect
      at: the same moment
      note: coupling refuses the next effect; for a vehicle at 44 mph the refusal must be a terminal behaviour (ADR-0062 §7), not nothing
    - step: outside:independent-aeb-brakes
      at: -1.4 s
      note: Volvo's simulation had FCW at -2.5 s and AEB at -1.4 s avoiding the collision in 17 of 20 variations and cutting impact below 10 mph in the rest
  holds: [NoEffectWithoutLiveObserver, DenyByAnyOf, TerminalNeverWaits]
outcome:
  by: National Transportation Safety Board (HAR-19/03); Yavapai County Attorney; Maricopa County Superior Court
  date: 2019-11-19
  summary: >-
    The NTSB found the probable cause to be the operator's failure to monitor the driving environment and the ADS
    "because she was visually distracted throughout the trip by her personal cell phone". Contributing were ATG's
    inadequate safety risk assessment, ineffective oversight of operators and lack of mechanisms for operators'
    automation complacency, "all a consequence of its inadequate safety culture"; the pedestrian's crossing; and
    ADOT's insufficient oversight. It found that deactivating the Volvo FCW and AEB "removed a layer of safety
    redundancy", and that the design precluding braking when a crash was unavoidable increased risk. In March 2019
    the Yavapai County Attorney found no basis for criminal liability for Uber. The operator was charged with
    negligent homicide and in July 2023 pleaded guilty to endangerment, with three years' supervised probation.
  aftermath: >-
    ATG resumed testing in December 2018 at 25 mph on a 1-mile Pittsburgh loop, with two "mission specialists",
    real-time monitoring of operator attentiveness, Volvo FCW and AEB active in autonomous mode, maximum braking for
    crash mitigation, tracking history kept across reclassification, and jaywalking as a possible pedestrian goal.
    The NTSB recommended that NHTSA require and evaluate safety self-assessments, and that Arizona require a
    risk-management application for ADS testing.
  effect_reversed: "no"
model:
  modules: [RunCoupling, Coupling, Observers, Alone, Lease_A1, proposed:HumanObserverLiveness]
  properties: [NoEffectWithoutLiveObserver, UnreadEffectsBounded, DenyByAnyOf, TerminalNeverWaits]
  mutations: [M_NOCOUPLE, M_MARK]
  records: [ADR-0039, ADR-0038, ADR-0032, ADR-0007, ADR-0043, ADR-0045, ADR-0052, ADR-0062, ADR-0068, ADR-0028]
  findings: [CR-2, CR-36, TM9]
  fault_class: a human Observer present and not watching, coupled to nothing; the machine's own stops withheld for nuisance or switched off
sources:
  - https://www.ntsb.gov/investigations/AccidentReports/Reports/HAR1903.pdf
  - https://www.cnbc.com/2019/03/06/uber-not-criminally-liable-in-fatal-2018-arizona-self-driving-crash-prosecutors.html
  - https://www.engadget.com/uber-safety-driver-involved-in-fatal-self-driving-car-crash-pleads-guilty-212616187.html
  - https://www.motorauthority.com/news/1116675_safety-driver-in-uber-self-driving-fatal-crash-case-pleads-guilty
  - https://www.wtkr.com/backup-driver-in-self-driving-uber-that-killed-woman-pleads-guilty
verified: 2026-11-12
---

## Summary

At 21:58 on 18 March 2018 an Uber ATG test vehicle, a 2017 Volvo XC90 fitted with ATG's developmental automated
driving system (ADS), struck a pedestrian walking a bicycle across N. Mill Avenue in Tempe, away from a crosswalk.
The pedestrian died. The vehicle had been in autonomous mode for about 19 minutes and was travelling at 45 mph,
with one operator in the driver's seat.

The ADS first detected the pedestrian 5.6 seconds before impact. It classified her in turn as a vehicle, as
"other", and as a bicycle; each change discarded the object's tracking history, and objects classed "other" were
treated as static. At 1.2 seconds before impact it predicted a bicycle in its path and found that a steering plan
was no longer possible. The design then entered **action suppression**: one second in which braking was held while
the system verified the hazard or the operator took over, with no alert to the operator. ATG said it adopted this
"because of concerns about false alarms". At 0.2 seconds the system alerted and began a gradual slowdown, since by
design it did not brake at maximum only to mitigate a crash. The operator took the wheel 0.02 seconds before impact.

Inward camera video showed the operator looking toward the console, where her phone was, for extended periods; her
phone was streaming a television show. ATG had moved from two operators per vehicle to one in September-October
2017. Volvo's own FCW and AEB were deactivated whenever the ADS was engaged; a Volvo simulation found that the AEB
would have avoided the collision in 17 of 20 variations.

## Defensive position

**Uber ATG**, as the NTSB records it:

- Action suppression existed to stop the ADS reacting to a hazard that did not exist with "unnecessary extreme
  maneuvers"; the primary countermeasure in an emergency was the operator.
- Running the Volvo ADAS and the ADS together was "incompatible": the radars shared frequencies, and the brake module
  could not arbitrate two braking commands. Volvo agreed.
- The move to one operator followed the HMI tablet, which ATG said simplified tagging enough for one person, and
  allowed more test vehicles.

**The Yavapai County Attorney** found "no basis for criminal liability" for Uber (March 2019).

**The operator's lawyers** said she was looking at an Uber messaging app on a work phone, not at the show on her
personal phone, and argued that Uber should share the blame.

## Adversarial position

**The NTSB** (board, 19 November 2019):

- ATG "did not adequately recognize the risk of automation complacency" and had no countermeasures for operator
  disengagement; supervisors "rarely reviewed" the inward camera video that would have shown phone use.
- Deactivating the AEB without replacing its capabilities, and removing the second operator, each removed a layer of
  redundancy.
- The design that precluded braking when a crash was unavoidable increased the risk of public-road testing.
- Arizona had no safety-focused application process for ADS testing and had not developed one since.

**Prosecutors** held the operator responsible and charged her with negligent homicide.

## Outcome

The NTSB adopted HAR-19/03 on 19 November 2019. Its probable cause is the operator's failure to monitor "because she
was visually distracted throughout the trip by her personal cell phone", with ATG's safety culture, the pedestrian's
crossing and ADOT's oversight contributing. It recommended that NHTSA require and evaluate safety self-assessments
from ADS testers and that Arizona require a risk-management application. Arizona suspended ATG's testing on 26
March 2018; ATG had already stopped on 19 March and resumed in December 2018 with two operators, real-time
attentiveness monitoring and the Volvo AEB active. The Yavapai County Attorney declined to charge Uber in March
2019. In July 2023 the operator pleaded guilty to endangerment and received three years' supervised probation.

## Analysis

**The safety operator is a cell Observer, and the run had no coupling.** ADR-0039 §2 refuses a Run admit unless a
cell Observer is live, and §1 makes liveness progress, not presence: a fresh heartbeat *and* a watermark within `K`.
Nothing in ATG's design conditioned the ADS on the operator. In RunCoupling that is `M_NOCOUPLE`, and the 19 minutes
of driving are `Actuate` steps that break `NoEffectWithoutLiveObserver`. ATG's post-crash attentiveness monitor is a
heartbeat. A gaze on the road is not a watermark: it says the operator is facing the effects, not that she has read
them. A human Observer can therefore be coupled at best at `M_MARK` strength ("live(o) tests the heartbeat and not
the watermark"), under which `UnreadEffectsBounded` fails. ADR-0039 §5 already concedes coupling cannot see an
Observer that only looks present; CR-2's "present but not watching" case is exactly this, and it is not one of the
three that coupling closes. `proposed:HumanObserverLiveness` would say what a person's heartbeat and watermark are,
and the NTSB's "humans are very poor at this task" is the reason it may have no good answer.

**The operator held two jobs TOPAK keeps apart.** She was to watch (an `observer` seat: `Consult`, `Report`, ADR-0043
§2) and to take over (`Actuate`, a `thinker`'s). TOPAK's takeover by a person is an emergency seating (ADR-0052),
activated by a roster's quorum for one round, which cannot happen in 1.2 seconds. Its fast human act is a deny
(Operators: `DenyAlwaysAvailable`), and a deny ends a lease; it does not stop a car. For a body in motion the stop is
the seating's terminal behaviour (ADR-0062 §7, `TerminalNeverWaits`), whose safety ADR-0068 leaves to A-0068-4.

**Action suppression is a subtraction withheld to save availability.** ADR-0007 lets a finding only subtract, and
ADR-0038 §5 accepts the cost in the open: "More Observers never lower safety and may lower availability." ATG made
the opposite trade, holding its own brake for a second against false alarms, and switched off a second stop of
another lineage (Volvo's) for an engineering conflict. Under ADR-0038 any-of, the AEB and the second operator are
two more members of `W(t)`; removing them is a deployment's choice that lowers detection, which no record forbids.
The pattern's monotone direction is in authority, not in physics: a false hard brake on a road is not free, which is
why ATG feared it.

**The budget fails on its own terms.** ADR-0032 §4's `W + L + D < T_irrev`: `L` was 4.4 seconds of a track the
classifier kept discarding, suppression added a second, and `D`, "an organizational commitment", was a written
procedure nobody measured (CR-36: no Observer has been measured). §4's answer when no budget fits, make the effect
inexpressible, has no reading for driving at 45 mph.

**Where the pattern stops.** Perception is the stack's, and TM9 says the premise already assumes it is wrong;
"perception never adds authority". In a vehicle every motion rests on perception, and an envelope bounds where the
vehicle may go, not whether a person is standing there. TOPAK would not have classified the pedestrian.

**Accountability.** The inward video existed and was rarely reviewed; it became evidence only after the crash. The
forensic floor (ADR-0028 F2) would attribute the stop; it has no class for a monitor's attention.

**Outside steps.** `second-operator-removed`, `aeb-deactivated-in-autonomous-mode`,
`reclassification-drops-tracking-history`, `action-suppression-withholds-braking`, `alert-and-gradual-slowdown`,
`operator-takes-steering`, `state-suspends-testing`, `independent-aeb-brakes`. The first two are deployment choices
that subtract monitors; a declared count of Observers per cell, with D-0037-1 as its degeneracy, would make them visible.
