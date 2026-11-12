---
id: 2023-ROB-CRUISE-PEDESTRIAN-DRAG
title: Cruise robotaxi, San Francisco, 2 October 2023 — a pullover chosen by a misread collision, and reports that left it out
kind: incident
date: 2023-10-02
sector: robotics
setting: Cruise LLC driverless AV in autonomous mode, no passenger, 5th and Market Streets, San Francisco, California
concerns: [actuation, sensing, emergency-path, accountability, revocation, authority, deployment]
rules_at_time:
  - document: NHTSA Standing General Order on crash reporting (as quoted in the Quinn Emanuel report)
    clause: 1-day, 10-day and 30-day reports; narrative
    paraphrase: a crash with the ADS in use within 30 seconds and causing injury or damage is reported within 24 hours, with updates at 10 and 30 days; the narrative describes pre-crash, crash and post-crash details
  - document: California Code of Regulations, Title 13
    clause: "§228.20(b)(3), (b)(6); §227.42(b)(5), (c)"
    paraphrase: the DMV may suspend a deployment or driverless testing permit for misrepresenting the safety of the technology, for vehicles unsafe for public operation, for an act or omission that makes testing an unreasonable risk, and at once where public safety requires it
analogue:
  - record: ADR-0062
    clause: "§7"
    note: the terminal behaviour (hold, return on a voted route, land or stop) is part of the seating and voted with it; the stack does not choose it
  - record: ADR-0007
    clause: Decision
    note: semantic lift is prohibited in the admit path; a classifier's output enters only as a finding that subtracts
  - record: ADR-0028
    clause: "§1, §3"
    note: admit decisions and stop attributions are non-erasable, read by the anchor and a declared external auditor role
  - record: ADR-0050
    clause: "§4"
    note: a deny needs no lease and no peer; any seated operator can stop its domain
actors:
  - party: Cruise ADS
    role: automation
    fault: byzantine
    note: its collision detection placed the occluded pedestrian at its side, called the impact a side collision, and chose an outermost-lane stop over an emergency stop
  - party: Cruise LLC (leadership, government affairs, legal)
    role: operator
    fault: contested
    note: Quinn Emanuel found no intent to mislead and a "fundamental misapprehension" of its obligations; Cruise later admitted a false report under a deferred prosecution agreement
  - party: Nissan Sentra driver
    role: public
    fault: byzantine
    note: struck the pedestrian, launching her into the AV's lane, and left the scene; police found this driver "most at fault"
  - party: Pedestrian
    role: public
    fault: honest-error
    note: entered the crosswalk against the signal; cited by police
  - party: California DMV
    role: regulator
    fault: none-alleged
    note: said it learned of the dragging from another government agency
  - party: NHTSA
    role: regulator
    fault: none-alleged
  - party: Quinn Emanuel Urquhart & Sullivan
    role: investigator
    fault: none-alleged
    note: retained by Cruise and GM on 25 October 2023; did not interview regulators
detection:
  means: [regulator, public]
  latency: days
trace:
  - step: outside:human-driver-launches-pedestrian-into-av-lane
    at: 21:29 PT
  - step: outside:av-brakes-and-strikes-pedestrian
    at: +0 s, 18.6 mph
    note: braking from 19.1 mph began about 0.25 s before contact; the classification of the pedestrian had been intermittent since the first impact
  - step: outside:collision-classified-as-side-impact
    at: +0 s
    note: the pedestrian was occluded from the lidar except a raised leg; the track used by collision detection did not reflect her position
  - step: Recover
    at: +1.83 s
    note: Alone.tla under M_STACKCHOOSES; the ADS's own classification selected the terminal act, an outermost-lane stop, over an emergency stop; a mislabelled lane edge in the semantic map made its first stop look unacceptable
  - step: outside:pullover-drags-pedestrian
    at: +1.83 s to +8.8 s
    note: up to 7.7 mph for about 20 feet; the legs were visible to a side camera and briefly detected, never tracked
  - step: outside:wheel-speed-fault-forces-stop
    at: +5.8 s
    note: a wheel spinning on the pedestrian produced a speed offset; the degraded state ordered an immediate stop. The AV "is programmed to move as much as 100 feet"
  - step: outside:fleet-grounding-declined
    at: 3 October, 12:00
    note: safety and engineering staff raised grounding the fleet; the CEO and COO said it was not warranted
  - step: outside:video-left-to-speak-for-itself
    at: 3 October briefings
    note: Cruise played or tried to play the full 45-second video; connectivity likely hampered three meetings, and nobody pointed out the pullover or the dragging
  - step: outside:crash-report-omits-dragging
    at: 3 October 14:37 and 11 October 12:48
    note: the 1-day and 10-day SGO reports, filed by a paralegal who had not been told; the full video had been uploaded to NHTSA at 13:40 on 3 October
  - step: outside:regulator-learns-from-another-agency
    at: 13-16 October
    note: the DMV asked for more complete video on 10 October and received the full video on 13 October
  - step: RevokeLease
    at: 24 October 2023
    note: Lease_A1's targeted revocation, read as the DMV's suspension of the deployment and driverless testing permits; testing with a safety driver was left in place, a narrowing
  - step: Promote
    at: 2 November 2023
    note: recall of 950 ADS vehicles with a remedy under which the AV would "have remained stationary"; the 30-day report described the dragging
  - step: outside:deferred-prosecution-for-false-report
    at: November 2024
counterfactual:
  by: Cruise's recall remedy, read as a post-collision behaviour fixed at seating, and a crash report generated from the record
  trace:
    - step: outside:collision-detected
      at: +0 s
      note: whatever class the ADS gives it
    - step: Recover
      at: +1.78 s
      note: the seated terminal act, hold; the stack does not select it (Alone.tla without M_STACKCHOOSES)
    - step: outside:report-projected-from-record
      at: 3 October
      note: the report lists every movement in the incident window, as the 12:00 engineering chart already did
  holds: [ExpiryGrantsNothing, TerminalNeverWaits]
outcome:
  by: California DMV; NHTSA; US Attorney's Office (N.D. Cal.); Quinn Emanuel (for the boards of Cruise and GM)
  date: 2024-11-14
  summary: >-
    The DMV suspended Cruise's deployment and driverless testing permits on 24 October 2023, citing vehicles not safe
    for public operation, misrepresentation of safety information, and an act or omission making testing an
    unreasonable risk; testing with a safety driver was not affected. The Quinn Emanuel report (24 January 2024)
    found that by the morning of 3 October leadership and more than 100 employees knew of the dragging; that Cruise
    meant to let the "video speak for itself" and did not point it out; that leadership was "fixated" on correcting
    the media narrative that the AV had caused the crash; and that the evidence "does not establish" an intent to
    mislead. Its Exponent appendix found the root cause of the movement to be the side-collision determination. In
    September 2024 NHTSA's consent order imposed a $1.5 million penalty and a corrective action plan for reports
    that omitted post-crash behaviour. On 14 November 2024 Cruise admitted a false report to federal regulators and
    agreed to a deferred prosecution agreement with a $500,000 fine.
  aftermath: >-
    Recall of 950 vehicles with a remedy to remain stationary after such a collision; the CPUC's order to show cause
    (1 December 2023) and a $75,000 settlement offer; departures of leaders and layoffs; quarterly NHTSA reviews of
    reporting under the consent order.
  effect_reversed: "no"
model:
  modules: [Alone, Lease_A1, Operators, Observers, proposed:Disclosure]
  properties: [ExpiryGrantsNothing, TerminalNeverWaits, DenyAlwaysAvailable, EveryStopIsAttributed]
  mutations: [M_STACKCHOOSES]
  records: [ADR-0062, ADR-0007, ADR-0028, ADR-0050, ADR-0059, ADR-0045, ADR-0068]
  findings: [TM9, TM7, CR-38]
  fault_class: a post-fault behaviour selected by the perception that had just failed, and a report to the overseer composed by people rather than projected from the record
sources:
  - https://assets.ctfassets.net/95kuvdv8zn1v/1mb55pLYkkXVn0nXxEXz7w/9fb0e4938a89dc5cc09bf39e86ce5b9c/2024.01.24_Quinn_Emanuel_Report_re_Cruise.pdf
  - https://www.dmv.ca.gov/portal/news-and-media/dmv-statement-on-cruise-llc/
  - https://www.cbsnews.com/sanfrancisco/news/cruise-automation-admits-false-report-sf-pedestrian-dragging/
  - https://www.repairerdrivennews.com/2024/10/03/gms-cruise-fined-1-5-million-by-nhtsa-for-failure-to-report-pedestrian-incident/
verified: 2026-11-12
---

## Summary

At about 21:29 PT on 2 October 2023 a human-driven Nissan Sentra struck a pedestrian in the crosswalk at 5th and
Market and launched her into the adjacent lane, in front of a driverless Cruise AV. The AV braked and struck her at
about 18.6 mph, coming to a first stop about 1.78 seconds later. Its collision detection, working from a track that
no longer reflected where the occluded pedestrian was, classified the impact as a side collision. That selected an
outermost-lane stop, a "minimal risk condition" pullover, rather than an emergency stop. About 1.83 seconds after
contact the AV moved again, reaching 7.7 mph and travelling about 20 feet with the pedestrian beneath it, until a
wheel-speed offset caused by a wheel spinning on her put it into a degraded state and an immediate stop. The Nissan
driver left the scene. Firefighters freed the pedestrian with heavy rescue tools.

By the morning of 3 October Cruise's leadership and more than 100 employees knew of the movement. Safety and
engineering staff raised grounding the fleet; the CEO and COO declined. Cruise briefed the mayor's office, NHTSA and
the DMV that day and played, or tried to play, the full 45-second video without pointing out the pullover. It
uploaded the full video to NHTSA at 13:40, and at 14:37 filed a 1-day crash report that did not mention the
movement; the 10-day report (11 October) did not either. The DMV received the full video on 13 October and
suspended Cruise's driverless permits on 24 October. The 30-day report (2 November) described the dragging, and Cruise
recalled 950 vehicles.

## Defensive position

**Cruise employees**, as Quinn Emanuel records them:

- Most participants said they played the full video on 3 October, intending regulators to see the pullover and ask
  about it; connectivity problems may have prevented that in all but one initial meeting.
- NHTSA received the full video within hours; the CPUC declined an offer to see it; San Francisco's transport
  agency, police and fire department saw it without difficulty and asked about the pullover.
- Some interviewees read the SGO narrative as calling for the collision itself, not what followed it.

**Quinn Emanuel** found that the evidence "does not establish that Cruise leadership or employees sought to
intentionally mislead or hide from regulators the details". **Exponent's** analysis found the first collision may
not have been avoidable, by the AV or by a reasonable human driver.

## Adversarial position

**The DMV** (24 October 2023): Cruise misrepresented information related to the safety of its technology, and its
vehicles were not safe for public operation. Its order, as Quinn Emanuel summarises it, said Cruise had not disclosed
the pullover at the 3 October meeting and that the DMV learned of it from another agency, impeding its oversight.

**NHTSA** (consent order, September 2024): the initial report "did not describe the behavior of the vehicle after
coming to the stop".

**The US Attorney's Office** (November 2024): the reports omitted the secondary movement and dragging and were
"inaccurate and incomplete"; Cruise admitted a false report. The DOT Inspector General's office spoke of the
company's "lack of candor".

**Quinn Emanuel** itself named "poor leadership, mistakes in judgment, lack of coordination, an 'us versus them'
mentality with regulators", and called the reliance on video alone "a fundamentally flawed approach".

## Outcome

The DMV suspended the deployment and driverless testing permits on 24 October 2023 with no fixed term, leaving
testing with a safety driver in place. Cruise recalled 950 ADS vehicles on 2 November 2023. The CPUC issued an order
to show cause on 1 December 2023. Quinn Emanuel's report to the boards of Cruise and GM is dated 24 January 2024.
NHTSA's consent order of September 2024 imposed $1.5 million and a corrective action plan. On 14 November 2024
Cruise entered a deferred prosecution agreement and paid a $500,000 criminal fine. The pedestrian's injuries were not
undone.

## Analysis

**The post-collision behaviour was chosen by the stack.** ADR-0062 §7 fixes the terminal behaviour at seating,
"voted with it", and says the stack "does not choose it and does not carry it out". Cruise's ADS chose between an
emergency stop and a pullover by its own classification of the collision, which is `M_STACKCHOOSES` in Alone.tla and
breaks `ExpiryGrantsNothing`. It is also a semantic lift (ADR-0007): a perception judgment, made at the moment
perception had failed (TM9), selected an effect. The recall remedy, stay stationary after such a collision, moves
toward a behaviour fixed in advance. The pattern's own residual applies: ADR-0068 A-0068-4 says a stall "for a body
in motion is not safe", and the right fixed behaviour depends on where the body is. Whoever declares it, the stack
must not pick it from what it just misperceived.

**The stop that ended it was a failure that subtracted.** A wheel-speed diagnostic, not the planner, stopped the
car; otherwise it could have gone as far as 100 feet. That is ADR-0045's delegated class doing what the trusted path
did not.

**A stop needs no permission in TOPAK, and here it waited for the CEO.** ADR-0050 §4: a deny needs no lease and no
peer; ADR-0038 §5: "consensus for grants, local for denials". Seated operators who thought the fleet should stop could have ended
its rounds (`DenyAlwaysAvailable`, `EveryStopIsAttributed`), and a fleet fence needs only a live lease. At Cruise the
grounding was a leadership decision, and it was declined.

**The record survived; the report was composed.** The full video reached NHTSA about 16 hours after the crash. What was missing
was the sentence in the 1-day and 10-day reports, written by a paralegal nobody told. ADR-0028 keeps admit decisions
and stop attributions non-erasable and readable by a declared external auditor (§3), so the pullover's admit and the
final stop would be on the floor. Nothing in the corpus makes a report to an overseer complete: TM7's residual, "a
wrong act ... is recorded and not prevented", does not even reach an omission in a narrative. `proposed:Disclosure`
would make an incident report a projection of the floor over a window, with the property that every admit and stop in
the window appears in it; a human may add context, not subtract entries. CR-38 is the same tension from the other
side.

**The regulator stood where a parent plane does.** The suspension was immediate, needed no hearing, and kept
safety-driver testing, a narrowing. ADR-0059 fences a plane from every plane above it; a permit-issuing regulator
is that relation, outside any TOPAK mechanism.

**Outside steps.** `human-driver-launches-pedestrian-into-av-lane`, `av-brakes-and-strikes-pedestrian`,
`collision-classified-as-side-impact`, `pullover-drags-pedestrian`, `wheel-speed-fault-forces-stop`,
`fleet-grounding-declined`, `video-left-to-speak-for-itself`, `crash-report-omits-dragging`,
`regulator-learns-from-another-agency`, `deferred-prosecution-for-false-report`, and in the counterfactual
`collision-detected` and `report-projected-from-record`. The disclosure steps are the to-do list TOPAK cannot yet
write: what an overseer is owed, and when.
