---
id: 1999-SPC-MARS-CLIMATE-ORBITER
title: Mars Climate Orbiter — impulse data in pound-force seconds where the interface specified newton-seconds
kind: incident
date: 1999-09-23
sector: space
setting: Mars Climate Orbiter, NASA Jet Propulsion Laboratory (navigation, project) and Lockheed Martin Astronautics (spacecraft operations), Mars Surveyor Operations Project
concerns: [interface-types, monitoring, human-in-the-loop, deployment, accountability, sensing]
rules_at_time:
  - document: MSOP Project Software Interface Specification (SIS), as the Mishap Investigation Board describes it
    clause: format and units of the Angular Momentum Desaturation (AMD) file
    paraphrase: the AMD file's impulse-bit data, produced by ground software SM_FORCES and consumed by the navigation software, were to be in newton-seconds
  - document: Incident, Surprise, Anomaly (ISA) reporting procedure, as the Board describes it
    clause: problem reporting
    paraphrase: the formal route for raising and tracking anomalies to closure; the Board found it was not used for the navigation discrepancies
  - document: NPG 8621 (Draft 1), NASA procedures for mishap investigation
    clause: definitions of root and contributing cause
    paraphrase: the definitions the Board applied to find one root cause and eight contributing causes
analogue:
  - record: ADR-0049
    clause: "§3, §4"
    note: an input is typed only string, number or boolean, and ranges and formats are not decided; each field is marked checked or claimed
  - record: ADR-0018
    clause: Decision
    note: the validator is total over the alphabet and knows shapes, not what a number measures
  - record: ADR-0051
    clause: Decision
    note: the correlator computes named folds that a second reader can recompute; a disagreement between two derivations is a finding (Proposed)
  - record: ADR-0038
    clause: "§5"
    note: a finding from any one Observer blocks the target's next admit, and no quorum of Observers is sought
actors:
  - party: SM_FORCES ground software and its developers (Lockheed Martin Astronautics)
    role: vendor
    fault: honest-error
    note: wrote impulse bits in lbf-s to the AMD file; the Board's root cause
  - party: JPL operations navigation team
    role: operator
    fault: contested
    note: saw the discrepancies and raised them informally; the Board found the team understaffed, under-trained on the spacecraft and isolated
  - party: Spacecraft on-board AMD software
    role: automation
    fault: none-alleged
    note: computed in metric units and was correct; it also sent velocity-change data the navigators did not know about
  - party: MCO project and Mars Surveyor Operations Project management
    role: supervisor
    fault: contested
    note: the Board cited systems engineering, communications, staffing, training and verification and validation
  - party: MCO Mishap Investigation Board (chair Arthur G. Stephenson)
    role: investigator
    fault: none-alleged
detection:
  means: [investigation, operator]
  latency: days
trace:
  - step: outside:producer-emits-other-unit
    at: cruise, from December 1998
    note: SM_FORCES wrote the AMD file's impulse bits in pound-force seconds; the SIS required newton-seconds
  - step: outside:consumer-reads-declared-unit
    at: from April 1999
    note: the navigation software read the values as newton-seconds and underestimated each desaturation's effect by a factor of 4.45
  - step: outside:perturbation-repeated-more-than-modelled
    at: cruise
    note: AMD events were 10 to 14 times more frequent than the navigators expected, because of the asymmetric solar array
  - step: Finding
    at: spring and summer 1999
    note: Observers.tla's finding, read as Doppler-only solutions that consistently put the approach closer to Mars; raised by e-mail, not as an ISA, it blocked nothing
  - step: outside:independent-measurement-unused
    at: cruise
    note: the spacecraft computed and sent velocity-change data for each desaturation; the navigators did not know until long after launch
  - step: outside:contingency-manoeuvre-not-ready
    at: before Mars orbit insertion
    note: TCM-5 was discussed verbally and not executed; analysis, tests and procedures for it were not done
  - step: Effect
    at: 23 September 1999, 09:00:46 UTC
    note: Intent.tla's effect, read as the orbit insertion burn, admitted with the predicted periapsis falling toward 110 km against an 80 km survival minimum
  - step: outside:loss-of-signal
    at: 09:04:52 UTC
    note: occultation 49 seconds earlier than predicted; no signal after; the corrected estimate gave a 57 km periapsis
counterfactual:
  by: the navigation team and the spacecraft team, with the Board's recommendations in TOPAK's terms
  trace:
    - step: outside:unit-carried-in-type-and-checked
      at: the AMD file interface
      note: the unit is part of the field's type and the consumer refuses a file whose declared unit differs; the SIS already said which
    - step: Finding
      at: April 1999
      note: a second derivation (Doppler-only, or the spacecraft's own velocity-change data) disagrees with the prime solution
    - step: Refuse
      at: the next commitment
      note: one finding blocks the next admit until it is closed; under ADR-0038 §5 no quorum is sought
    - step: outside:contingency-manoeuvre-executed
      at: before orbit insertion
      note: TCM-5, prepared, raises the periapsis
  holds: [DenyByAnyOf]
outcome:
  by: NASA Mars Climate Orbiter Mishap Investigation Board (Phase I report)
  date: 1999-11-10
  summary: >-
    The Board found one root cause, "the failure to use metric units in the coding of a ground software file, Small
    Forces, used in trajectory models": SM_FORCES reported impulse in lbf-s where the SIS specified N-s, and the
    navigation software therefore underestimated the thruster firings' effect by a factor of 4.45. It found eight
    contributing causes: undetected mismodelling of velocity changes, a navigation team unfamiliar with the
    spacecraft, TCM-5 not performed, a systems engineering process that did not address the move from development to
    operations, inadequate communications, inadequate navigation staffing, inadequate training, and verification and
    validation that did not adequately address ground software.
  aftermath: >-
    The Board's Phase I recommendations were for Mars Polar Lander: verify units throughout, audit all data passed
    between JPL and Lockheed Martin for SIS compliance, validate small-forces models and compare against alternate
    navigation methods, prepare TCM-5, use the ISA process, and conduct independent reviews. NASA's press release of
    the same day listed management actions for the lander, including a fully independent red team. A Phase II report
    on broader lessons was due by 1 February 2000.
  effect_reversed: "no"
model:
  modules: [Observers, Correlator, Intent, proposed:DimensionedLift]
  properties: [DenyByAnyOf]
  mutations: [M_QUORUM]
  records: [ADR-0049, ADR-0018, ADR-0051, ADR-0038, ADR-0039, ADR-0007, ADR-0057]
  findings: [CR-2, CR-12]
  fault_class: a value whose unit was claimed at an interface and checked by nobody; the disagreement it caused was seen and had no channel that could stop anything
sources:
  - https://llis.nasa.gov/llis_lib/pdf/1009464main1_0641-mr.pdf
  - https://nssdc.gsfc.nasa.gov/planetary/text/mco_pr_19991110.txt
verified: 2026-11-12
---

## Summary

Mars Climate Orbiter launched on 11 December 1998. To keep its reaction wheels unsaturated it fired thrusters in
angular momentum desaturation (AMD) events. After each event, telemetry was processed on the ground by the
SM_FORCES software into the AMD file, which the JPL navigation team used to model the small forces on the
trajectory. The project's Software Interface Specification required the file's impulse-bit values in newton-seconds.
SM_FORCES wrote them in pound-force seconds. The spacecraft's own AMD software used metric units and was correct.

For the first four months of cruise the AMD files were unusable because of format errors, and the navigators modelled
the events from e-mail notices. From April 1999 they used the files and saw almost at once that the events'
perturbations appeared underestimated. AMD events were 10 to 14 times more frequent than expected because of the
asymmetric solar array, and most of the thrust was perpendicular to the line of sight, so Doppler tracking saw
little of it. Doppler-only solutions consistently put the approach closer to Mars than the prime solution. The
discrepancies were raised by e-mail and not resolved.

TCM-4 on 15 September targeted a first periapsis of 226 km. In the following week estimates fell to 150 to 170 km,
and about an hour before orbit insertion to as low as 110 km; 80 km was the minimum considered survivable. A
contingency TCM-5 was discussed verbally and not executed. The engine started at 09:00:46 UTC on 23 September 1999;
the signal was lost at 09:04:52, 49 seconds earlier than predicted, and never reacquired. On 29 September the factor
of 4.45 was found; the corrected estimate of the periapsis was 57 km.

## Defensive position

No party on record disputed the root cause. What the record holds in mitigation:

- **The Board** itself wrote that "mistakes occur on spacecraft projects" and that processes are normally in place to
  catch them; its finding was that MCO's did not.
- **The navigators' observability.** The Board records that the geometry gave limited observability of the thrust,
  so a systematic error "was present but undetected", and that four months of malformed files delayed their access
  to the data.
- **TCM-5.** The Board records why it was not done: no analysis, tests or procedures for it, the on-board orbit
  insertion timeline left no time to upload and verify it, and changing the orbit plan risked the aerobraking
  schedule needed to relay for Mars Polar Lander.

## Adversarial position

**The Mishap Investigation Board** placed the root cause in the ground software's failure to follow the SIS, and
the contributing causes in the organisation around it:

- The navigation team was "somewhat isolated", assumed Mars Global Surveyor heritage, and did not know until long
  after launch that the spacecraft sent velocity-change data; "an early comparison" of that data with tracking "might
  have uncovered the units problem".
- Concerns were raised by e-mail instead of through the ISA process, which let the problem slip "through the cracks".
- End-to-end testing of the small-forces software did not appear to have been done, and its independent verification
  and validation was not clearly accomplished.

The board chairman, Arthur Stephenson, summarised the root cause in NASA's release as "failed translation of English
units into metric units".

## Outcome

NASA established the Board on 15 October 1999 with Stephenson, director of Marshall Space Flight Center, as chairman.
Its Phase I report, dated 10 November 1999, gave one root cause, eight contributing causes and recommendations for
Mars Polar Lander. The spacecraft was lost; the Board wrote that it was either destroyed in the atmosphere or left it again into
heliocentric space.

## Analysis

**TOPAK's typed lift would have passed this file.** ADR-0049 §3 types an input as `string`, `number` or `boolean` and
leaves "ranges and formats" undecided; the validator (ADR-0018) is total over shapes. An impulse bit is a `number`
either way. ADR-0049 §4's honest vocabulary describes MCO exactly: the SIS made the unit a **claimed** field on both
sides, and nothing **checked** it. ADR-0007 is not the obstacle: a unit carried as a type tag is a syntactic lift,
total and mechanical, and comparing two declared tags needs no judgment. What it cannot do is check that the code
behind a declaration computes in that unit, which is what failed here. `proposed:DimensionedLift` would carry a unit
on every numeric input and output, refuse a consumer whose declared unit differs from its producer's, and be broken
by a mutation that compares the bare number; it guards the declaration, and the declaration's truth stays a
conformance test.

**The disagreement was a finding with nowhere to go.** Three orbit determinations disagreed for months, and the
spacecraft's own velocity-change data was a fourth, unused derivation. In TOPAK terms that is a correlator's fold
(ADR-0051, Proposed: folds "a second reader can recompute") and an Observer's finding. Under ADR-0038 §5 one finding
blocks the next admit with no quorum sought; `DenyByAnyOf` is the property, and `M_QUORUM`, where a finding acts only
with a majority behind it, is the mutation that breaks it. MCO's informal e-mail channel behaved worse than
`M_QUORUM`: a finding that never entered the record at all. CR-2's "detection fails open" names the class.

**What a stall would have cost.** The corpus's answer to an open finding is to refuse the next admit. Here the next
admit was orbit insertion, timed by orbital mechanics and pre-loaded on board; refusing it would have lost the
spacecraft another way. The Board's TCM-5 recommendation is the right counterfactual because it is a prepared
alternative, not a refusal. TOPAK's emergency path (ADR-0052) seats a person for one round; it does not prepare the
manoeuvre that person would need. That is where the pattern stops.

**Interfaces between organisations are a trusted-base question.** The AMD file crossed from Lockheed Martin's software
to JPL's. CR-12 found the corpus's own trusted base enumerated nowhere at the time; ADR-0057 §2 now asks every clause
to carry its givens. "The AMD file is in N-s" was a given of every navigation solution, held by a document and
discharged by nothing.
