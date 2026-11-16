---
id: 1993-CTL-GRIPEN-PIO
title: JAS 39 Gripen 39.102 at the Stockholm Water Festival — a pilot-induced oscillation through a rate-limited control system
kind: incident
date: 1993-08-08
sector: control
setting: production JAS 39 Gripen 39.102 (F 7/FMV:PROV), flown by a Saab test pilot in a display over Riddarfjärden, Stockholm; crashed on Långholmen
concerns: [human-in-the-loop, feedback, actuation, interlock, deployment, configuration-change, monitoring]
rules_at_time:
  - document: Flight test programme for the display, with its annex (as SHK describes it)
    clause: limits for the display
    paraphrase: the annex set limits on height and angle of attack for the display and allowed exceptions from the pilot's flight manual (SFI); SHK found the limits did not match the display's aim and the exceptions not justified
  - document: Swedish Air Force airworthiness and validation process for JAS 39 (CFV, FMV)
    clause: validation of the flight control system edition
    paraphrase: a control-law edition was validated on test aircraft and in simulators; no limits had been set on how far a production aircraft's configuration could differ from the validated one before further validation was required (SHK finding 26)
analogue:
  - record: ADR-0023
    clause: "§2, §7a"
    note: a variation's effect is premise loss, and above one parameter a composition note must name the theorems lost only to the parameters jointly
  - record: ADR-0058
    clause: "§2"
    note: a replaced node re-establishes every edge at a declared type; an edge not mentioned is absent and its premise false (Proposed)
  - record: ADR-0045
    clause: "§2, §3"
    note: a component relied on is a declared row with its failure named, and a theorem premised on a row trusted for nothing is computed void rather than assumed
  - record: ADR-0062
    clause: "§7"
    note: '"A stall that never ends is safe" is false of a vehicle in flight; reaching a safe state is an obligation on whoever builds the vehicle'
actors:
  - party: Display pilot (Saab test pilot)
    role: operator
    fault: contested
    note: SHK found he did not keep to the display's height and angle-of-attack limits, that his roll-out input matched his rehearsal, and that his decision to eject was right
  - party: JAS 39 flight control system (control laws, stick, rudder actuation)
    role: automation
    fault: contested
    note: SHK found an imbalance between pilot command, stick, control-law sizing and actuator rate limits, built into every JAS 39
  - party: Saab and FMV (developers and procuring authority)
    role: vendor
    fault: contested
    note: had found the aircraft could be stalled and judged the margin enough; the property was not put in the flight manual
  - party: STYRSÄK warning
    role: monitor
    fault: omission
    note: shown to the pilot only after the aircraft was uncontrollable (SHK finding 17)
  - party: Statens haverikommission (SHK)
    role: investigator
    fault: none-alleged
detection:
  means: [operator, investigation]
  latency: seconds
trace:
  - step: Promote
    at: June 1993
    note: RulesFloorNV_rev5's promotion, read as 39.102's delivery to FMV with a control-law edition validated on test aircraft of different mass, stick force and roll deflection
  - step: outside:display-envelope-exceeded
    at: 8 August 1993, from 13.51
    note: a left 360-degree turn at 275 to 300 km/h with afterburner, mean angle of attack 21.7 degrees, about 2 G; outside the display limits
  - step: outside:autotrim-disengages-by-design
    at: during the turn
    note: roll autotrim cuts out above 20 degrees angle of attack, so the pilot held about 2 degrees of right stick
  - step: outside:command-exceeds-actuator-rate
    at: roll-out
    note: full right stick from 2 degrees right of neutral gave a far higher roll rate than in rehearsal; surfaces reached their maximum rate and delays grew
  - step: outside:pilot-in-loop-oscillation
    at: next seconds
    note: about 20 degrees of overroll, an unexpected nose-up, then a combined roll and pitch oscillation; divergent in pitch within about 2.5 seconds
  - step: outside:saturation-not-annunciated
    at: same
    note: the control system did not limit the commands and told the pilot nothing of its saturation; STYRSÄK came after control was lost
  - step: outside:pilot-ejects
    at: at very high nose attitude and low speed
    note: the aircraft stalled at low height; the pilot ejected and landed in the water east of Pålsundsbron
  - step: outside:impact-in-populated-area
    at: Långholmen, east of the southern abutment of Västerbron
    note: impact roughly wings level on a cycle path; fire out after about eight minutes; about 15 people reported injuries, one woman burned
outcome:
  by: Statens haverikommission (SHK), report ML 1993:3
  date: 1993-12-06
  summary: >-
    SHK found the aircraft airworthy and the cause an imbalance in the control system that let the pilot give
    commands the control surfaces could not answer in time. The resulting delays produced a combined pilot-induced
    oscillation in roll and pitch; the system could not limit the command signals, and the pitch oscillation grew
    until the aircraft stalled at a height that left no recovery. Every JAS 39 had the same built-in imperfection, and
    what was needed for an accident was a trigger. SHK also found that the display limits were not followed, that the
    consequences of rate and deflection limits had not been analysed over the whole opened envelope, that validation
    had not identified the PIO properties, and that pilots moved the stick less in the simulator than in flight.
  aftermath: >-
    SHK recommended that the Air Force ensure a deeper analysis of every part of the control system toward a balanced
    system, more tactical flying to judge the aircraft and pilot together, the planned quality-assurance changes, and
    the technical report's proposals for the escape system. Display flying over built-up areas was left to a later SHK
    report. Wikipedia's account says the flight-control software problem was corrected as late as 1995.
  effect_reversed: "no"
model:
  modules: [RulesFloorNV_rev5, proposed:PilotInLoop]
  properties: []
  mutations: []
  records: [ADR-0023, ADR-0058, ADR-0057, ADR-0045, ADR-0062, ADR-0046, ADR-0033]
  findings: [CR-17, CR-36]
  fault_class: a person and a rate-limited actuator in one loop, with the saturation unannounced; a known margin judged enough and left out of the manual
sources:
  - https://shk.se/download/18.2d6f089b18faca29dc815cfb/1698927104735/RM-1993_3-JAS-39-F-7.pdf
  - https://en.wikipedia.org/wiki/Accidents_and_incidents_involving_the_JAS_39_Gripen
verified: 2026-11-12
---

## Summary

On 8 August 1993 the production JAS 39 Gripen 39.102 took off at 13.51 from Saab's field and flew a display over
Riddarfjärden for the Stockholm Water Festival. After two passes and a right 360-degree turn that briefly reached
7.2 G, the pilot flew a slow left 360-degree turn with afterburner, accelerating from 275 to 300 km/h, at a mean angle
of attack of 21.7 degrees and about 2 G. The roll autotrim disengages above 20 degrees angle of attack, so he was
holding about 2 degrees of right stick.

Rolling out at about 300 km/h he briefly gave full right stick while pushing forward for level flight. The aircraft
overrolled level by about 20 degrees despite opposite stick. Correcting, he felt an unexpected nose-up, pushed
forward, and the aircraft entered an oscillation in roll and pitch. After two cycles it was 7 degrees nose-down and
35 degrees right bank; he pulled back and it stalled into a very high nose attitude at low speed. He ejected and
came down in the water. The aircraft struck Långholmen near the southern end of Västerbron, roughly wings level, and
burned for about eight minutes.

About fifteen people reported injuries, mostly light; one woman was burned and spent about three weeks in hospital.
The pilot was unhurt. He had been the pilot of the prototype JAS 39-1 when it crashed in 1989; Wikipedia's account
attributes that accident too to a pilot-induced oscillation.

## Defensive position

SHK's report is the only account on record read for this entry, and the defences below are the ones it records.

**For the pilot**, SHK found him fit, qualified and correctly equipped, and his roll-out stick input about the same
size as in his rehearsal. The difference was where it started: from 2 degrees right of neutral, so the stick briefly
reached full deflection. His decision to eject was "riktigt" (correct), since the height left no way to recover.

**For the developers**, SHK records that during work on the control-law edition in 39.102 they had found the
aircraft could be stalled and judged the margin sufficient, on the reasoning that a pilot does not fly so as to
combine the factors that lead to it. SHK called that judgment "rimlig" (reasonable). It also notes that a PIO
normally needs a trigger and a demanding precision task, and that a display cannot be simulated.

## Adversarial position

**SHK's own findings** run the other way on several points:

- The pilot did not keep to the height and angle-of-attack limits the flight test programme set for the display;
  the limits themselves did not match the display's aim.
- Given what was known of PIO at rate and deflection limits, the stall property "should have prompted a deeper
  analysis"; the landing case had shown rate limiting raised PIO tendency. The property was not in the manual.
- 39.102 differed from the test aircraft: lower mass, lower stick force, a larger roll deflection. SHK could not
  fix the effect of each but held that together they contributed. No limit set when a deviation forces revalidation.
- The control laws were complex enough to be hard to review in full; transfer of knowledge between and within
  groups, and deviation reporting, were deficient.

## Outcome

SHK delivered report ML 1993:3 to the Air Force on 6 December 1993. Its cause statement: an imbalance in the control
system let the pilot command more than the control surfaces could answer in time; the delays led to a combined PIO
in roll and pitch; the system could not limit the command signals, and the summed pilot and stabilisation commands
made the pitch oscillation grow, within about 2.5 seconds, past recovery. It made four recommendations to the Air
Force. The aircraft was destroyed and nothing was reversed.

## Analysis

**This is a control loop with the person inside it, and TOPAK has no module for one.** SHK's own definition is the
point: in a PIO the pilot "becomes only a machine element in the control system", and the one thing he can do is let
go of the stick. TOPAK's modules check discrete admits, leases and rounds; none has a rate, a phase lag or an
actuator limit. Every step after `Promote` is therefore `outside:`, and the properties and mutations lists are empty
by honesty, not oversight. Alone.tla's header says the same of its own scope: "Reaching a safe state is physics, and
is not here."

**The saturation was unannounced, and that is the corpus's shape.** SHK's "cliff effect": the control system was
saturated and "no information reached the pilot" until STYRSÄK, after control was lost. CR-2's dead Observer and
ADR-0039's liveness-as-progress are about a monitor that is silent when it should speak; here the monitor existed
and spoke too late. A refusal model cannot help directly: refusing the pilot's command would itself be an input the
pilot did not expect. The candidate is `proposed:PilotInLoop`, a module with an actuator rate bound and a person's
gain, whose property says no command beyond the actuator's rate is accepted without an annunciation in the same
step; a mutation drops the annunciation.

**The production aircraft was a degeneracy nobody declared.** SHK finding 26 (no limit on deviation from the validated
configuration before revalidation) and its sentence that the deviations' effects could not be fixed one by one but
"sammantagna" (together) contributed are ADR-0023 §2 and §7a almost word for word: a variation loses premises, and
above one parameter the composition note must name what is lost only jointly. ADR-0058 §2 says a replaced node
re-establishes every edge or the edge is absent. Under that discipline, 39.102's lower mass, lighter stick force and
larger roll deflection would each be a declared parameter with the validation results it voids.

**A known residual left out of the manual.** The developers knew the aircraft could be stalled and judged the margin
enough; SHK called that reasonable but faulted that it was not in the flight manual and not analysed further. ADR-0045
§2 and §3 are the corpus's answer in its own domain: what a deployment relies on is a declared row with its failure
named, so a theorem premised on it is computed void, not silently assumed. CR-17 notes the corpus presumes a trained human; here the trained human was not
told.

**The simulator understated the pilot.** Stick activity was consistently lower in the simulator than in flight, so
validation measured a gentler pilot than the one who flew. ADR-0033 and ADR-0046 hold that a model's results are
evidence, not the verified object, and CR-36 notes the corpus's own numbers are unmeasured placeholders. The lesson
transfers as a method point, not a mechanism.
