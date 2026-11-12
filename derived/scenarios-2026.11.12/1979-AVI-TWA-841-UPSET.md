---
id: 1979-AVI-TWA-841-UPSET
title: TWA 841, Boeing 727 N840TW, 4 April 1979 — a slat that would not retract, a 34,000 ft spiral, landing gear lowered in the dive, and a probable cause the crew contested for sixteen years
kind: incident
date: 1979-04-04
sector: aviation
setting: Trans World Airlines Flight 841, Boeing 727-31 N840TW, New York JFK to Minneapolis-St. Paul, cruising at FL390 near Saginaw, Michigan; emergency landing at Detroit Metropolitan
concerns: [emergency-path, interlock, actuation, human-in-the-loop, accountability]
rules_at_time:
  - document: Boeing 727 flap and leading-edge device system, as NTSB AAR-81-8 §1.17.1 describes it
    clause: normal extension schedule
    paraphrase: slats 2, 3, 6 and 7 extend with 2 degrees of trailing-edge flap and retract in reverse order, initiated by the outboard flap follow-up; the flap lever must be lifted over a gate; the alternate system extends every leading-edge device at random over about 40 seconds
  - document: Boeing Operations Manual Bulletin 75-7 (revised 10 March 1976), AAR-81-8 appendix E
    clause: leading edge slat actuator lock rings
    paraphrase: a retracted slat is held by its lock ring, "A" system pressure and air loads; losing "A" pressure with a broken lock ring, then speed brakes above Mach 0.80, may extend slats and need significant lateral control; the double failure was called extremely remote; crews were to log in-transit light symptoms
  - document: Fairchild A-100 cockpit voice recorder installation, as AAR-81-8 §1.11 describes it
    clause: bulk erase
    paraphrase: the 30-minute tape can be bulk-erased from the cockpit panel, only on the ground with the parking brake set
  - document: 49 CFR 845.41, as quoted in ALPA's 1990 petition
    clause: petitions for reconsideration
    paraphrase: the Board entertains a petition to reconsider its findings or probable cause only on new evidence or a showing that its findings are erroneous
analogue:
  - record: ADR-0042
    clause: "§3"
    note: every admitted Actuate leaves a record the mechanism writes and the principal cannot; its digests survive erasure
  - record: ADR-0028
    clause: "§1, §2"
    note: authority facts F1 to F6, erasure events included, are non-erasable; cognitive payload stays erasable; each class is a floor denial on the erasure action's envelope
  - record: ADR-0052
    clause: "§2, §5, §7"
    note: an emergency seat gets the domain's entries and emergency-only tools promoted in advance, with no floor exception (X1 retired); the reason is unknown to the mechanism; a person acting outside the mechanism is not covered
  - record: ADR-0037
    clause: "§7"
    note: a person holds one seat in a round, so the pilot flying cannot also hold an emergency seat
actors:
  - party: Captain (pilot flying)
    role: operator
    fault: contested
    note: the NTSB found "untimely flight control inputs" and attributed the slat extension to the crew's handling of the flap/slat controls; he denied moving them; Board member McAdams found he "acted expeditiously and reasonably"
  - party: First officer and second officer
    role: operator
    fault: contested
    note: both said they moved no flap or slat control and did not see the CVR erased; the NTSB's finding names "the flightcrew's manipulation"
  - party: No. 7 leading edge slat and its actuator
    role: actuator
    fault: contested
    note: NTSB, preexisting misalignment kept it from retracting and an inboard T-bolt had failed in fatigue; ALPA 1983, an actuator failure extended it uncommanded; ALPA 1990, it extended as a result of the dive
  - party: Right outboard aileron hinge bolt, lower yaw damper and lower rudder
    role: actuator
    fault: contested
    note: the bolt had failed predominantly in fatigue at an undetermined time; ALPA's 1990 petition put the upset on the bolt and a rudder malfunction, and the NTSB found no evidence for the rudder
  - party: Cockpit voice recorder
    role: monitor
    fault: contested
    note: 21 of 30 minutes blank; the 1981 Board spoke of "the captain's erasure"; the captain could not recall erasing it; ALPA said no check-out of the installation was documented
  - party: National Transportation Safety Board
    role: investigator
    fault: contested
    note: Gibson's 1991 petition alleged that Boeing wrote the probable cause and that evidence was destroyed; the Board answered that adopting a party's wording is normal and the parts were disposed of as excess, with no evidence of intent
detection:
  means: [operator, investigation]
  latency: seconds
  note: a buzz and light buffet felt within seconds; the probable cause was adopted 26 months later and never accepted by the crew
trace:
  - step: outside:flaps-split-from-slats
    at: "about 21:47:32"
    note: the NTSB's reconstruction, not on any record; "an attempt was made to extend 2 degrees of trailing edge flaps independently of the leading edge slats", slats 2, 3, 6 and 7 extending; the crew denied it
  - step: outside:slat-isolated-extended
    at: "21:47:32 to 21:47:47"
    note: slats 2, 3 and 6 retract; No. 7 stays extended; the aircraft rolls right to about 35 degrees
  - step: EndLease
    at: "about 21:47:45"
    note: Alone.tla's ending, by the person; the captain disconnects the autopilot and rolls nearly level
  - step: outside:lateral-control-margin-exhausted
    at: "21:47:51 to 21:48:07"
    note: right roll resumes; Mach, angle of attack and sideslip bring the lateral control margin to zero or less; uncontrollable below about 36,500 ft
  - step: outside:speed-brakes-without-effect
    at: during the first roll
    note: throttles to idle; the captain extends the speed brakes, feels no reaction, retracts them
  - step: outside:gear-extended-in-the-dive
    at: "after 21:48:25, the captain estimated near 15,000 ft"
    note: an entry in every crew's alphabet used far outside its range; both main gear damaged, right side brace broken, an "A" system line ruptured
  - step: outside:slat-separates
    at: during the second roll
    note: NTSB, the slat tore away and lateral control returned; ALPA 1990, its inboard half tore away as the right gear swung down
  - step: outside:pull-out-at-six-g
    at: "21:48:58, about 8,000 ft"
    note: minimum altitude on the FDR about 5,000 ft; peak about 470 kt and Mach 0.96; about 6.0 g in the recovery
  - step: outside:flapless-landing
    at: "22:31"
    note: alternate flap extension rolls the aircraft sharply left; flaps retracted; landed on runway 3
  - step: outside:cvr-bulk-erased-unrecorded
    at: on the ground at Detroit
    note: the erasure, if it was one, left no record of who or when; Emergency.tla's Erase is the forensic-floor contrast, and it needs M_ERASE
  - step: outside:probable-cause-disputed-without-review
    at: "1981-06-09 to 1997-07-07"
    note: AAR-81-8; petitions denied in 1983 and 1995; the Ninth Circuit held the 1995 denial unreviewable
outcome:
  by: National Transportation Safety Board (AAR-81-8); its responses to petitions; US Court of Appeals for the Ninth Circuit
  date: 1981-06-09
  summary: >-
    The Board found the probable cause to be the isolation of the No. 7 slat extended after slats 2, 3, 6 and 7 had
    extended and 2, 3 and 6 had retracted, and "the captain's untimely flight control inputs"; contributing were the
    slat's preexisting misalignment and the captain's distraction. "After eliminating all probable individual or
    combined mechanical failures", it found the extension "the result of the flightcrew's manipulation of the
    flap/slat controls". Three members voted; McAdams concurred and dissented. ALPA's 1983 petition was denied
    unanimously on 15 December 1983. Captain Gibson's petition of 2 May 1991 was denied on 4 May 1995; ALPA's 1990
    and TWA's 1991 petitions were handled separately. On 7 July 1997 the Ninth Circuit dismissed Gibson's petition for
    review: a denial of reconsideration is not an "order" and is within the Board's "unreviewable discretion".
  aftermath: >-
    TWA issued Flight Operations Safety Bulletin 79-3 on 6 August 1979 on flying with an extended No. 7 slat. The NTSB
    recommended on 21 January 1980 that the FAA disseminate that information to all 727 operators (A-80-8); the FAA
    declined, then deferred pending the October 1980 flight tests and the report. The aircraft was repaired and back
    in service in late May 1979. The sources read record no change to the probable cause.
  effect_reversed: "no"
model:
  modules: [RunSeats, Emergency, Alone, proposed:RangeExcursion]
  properties: [CallsAreAllowlisted, EmergencyLeaseHasARosterQuorum, ActivationIsForensic, OnlyThinkersActuate, TerminalNeverWaits]
  mutations: [M_X1, M_ERASE]
  records: [ADR-0042, ADR-0028, ADR-0052, ADR-0037, ADR-0049, ADR-0062, ADR-0007, ADR-0068]
  findings: [CR-38, CR-17, TM7, A-0068-7]
  fault_class: a contested act at the controls against a contested component failure, an improvised act outside an entry's range during the recovery, and a recorder a party could erase
sources:
  - https://libraryonline.erau.edu/online-full-text/ntsb/aircraft-accident-reports/AAR81-08.pdf
  - https://web.archive.org/web/20071106215527/http://www.iprr.org//comps/pet727/PFR2.html
  - https://web.archive.org/web/20071029090350/http://www.iprr.org//comps/pet727/B727_7840.html
  - https://caselaw.findlaw.com/us-9th-circuit/1188440.html
  - https://code7700.com/case_study_twa_841.htm
  - https://www.youtube.com/watch?v=FjK1Klk7liY
verified: 2026-11-12
---

## Summary

TWA 841 left JFK for Minneapolis-St. Paul at 20:25 EST on 4 April 1979 with 82 passengers and 7 crew. Reporting a
headwind of 100 kt or more, the crew asked for FL390 and reached it at 21:38:44; the captain levelled at Mach 0.80
with the autopilot in altitude hold. The night was clear and smooth at that level.

About 21:47, near Saginaw, the captain, sorting charts, felt a buzz that became a light buffet. The attitude indicator
showed 20 to 30 degrees of right bank with the autopilot commanding left. He disconnected it and applied left aileron,
then left rudder; by his account the roll continued against nearly full deflection, and he said "we're going over".
He retarded the throttles and extended the speed brakes, felt no effect, and retracted them. The aircraft rolled
through 360 degrees and into a second roll. The captain then called for the landing gear; the first officer selected
it down and the crew heard a sound like an explosion. The FDR shows a descent from about 39,000 ft to about 5,000 ft
in about 63 seconds, a peak of 470 kt, Mach 0.96 at 31,800 ft and about 6.0 g in the recovery. Control was regained
about 21:48:58 near 8,000 ft; the aircraft pitched up, and by the captain's account he levelled it near 13,000 ft.

The No. 7 leading edge slat on the right wing was missing; the No. 10 spoiler was largely gone; the right outboard
aileron hinge bolt had failed predominantly in fatigue; both main gear assemblies were damaged, the right side brace
and actuator support beam broken and an "A" system line ruptured. Alternate flap extension rolled the aircraft sharply
left, so the crew landed without flaps on runway 3 at Detroit at 22:31, after a low pass to check gear the indicators
called unsafe. Eight passengers had minor injuries from the g loads.

The FDR recorded four parameters. The CVR was undamaged, but 21 of its 30 minutes were blank and the rest postdated
the landing. Bulk erase works only on the ground with the parking brake set. The captain said he usually erased the
tape after each flight to prevent inappropriate use of recordings and could not recall doing so this time; the other
two officers said they did not erase it or see him do so. The video that cites this flight as a comparison says the
gear "adds drag" and the captain "pulls out"; the NTSB credits the slat's separation with restoring control.

## Defensive position

**The crew** told the Board they moved no control that could extend flaps or slats and saw no warning light before the
buzz. **Board member Francis McAdams** concurred reluctantly: the Board "categorically rejected the crew's sworn
testimony" without confronting them with the FDR analysis and tests, and the captain "acted expeditiously and
reasonably" against the roll.

**ALPA**, petitioning in 1983, argued that a mechanical failure of the No. 7 actuator extended the slat uncommanded. Its
1990 petition changed the premise:

- The slat was not extended at FL390; it was pulled out late in the dive, near the gear extension, and the upset had
  another cause.
- The fatigued aileron bolt let the aileron float and caused the buzz; a malfunction in the lower rudder and yaw damper
  added yaw and sideslip. The crew saw a lower yaw damper fail flag, and "the NTSB never determined why".
- Recovery came "only after hydraulic power to the lower rudder failed", when the over-extending right gear ruptured
  the "A" line. The Board relied on circumstantial evidence the manufacturer developed at its own facilities.
- No check-out of the CVR installation is in the docket, and a fault could have left a blank tape.

**Captain Gibson's** 1991 petition raised fifteen issues, among them eight unscheduled 727 slat deployments between 1978
and 1989, a 1977 control problem on a TWA 727 he said was concealed, Boeing wording in the probable cause, evidence
disposed of, and "crew participation frustrated".

## Adversarial position

**The NTSB** (1981) found no failure or combination of failures that would extend the slat unscheduled:

- A retracted slat is held by 3,000 psi of "A" pressure and a mechanical lock, so, barring a broken piston or rod, at
  least two failures must precede an unscheduled extension. "A" pressure was intact: it unlocked and extended the
  gear about 72 seconds after the buzz.
- Fracture of the piston had margins of safety in the thousands of percent. The flap lever is gated, so an accidental
  move was unlikely, and the alternate system extends devices at random, not slats 2, 3, 6 and 7 together.
- In the October 1980 flight tests, extending those slats with 2 degrees of flap gave the same 6-cycle g-trace buffet
  as the accident FDR. An extended slat alone was controllable with about half the lateral authority.
- Loss of control followed a sideslip the captain probably induced with rapid, full aileron and rudder, after a
  distraction let the roll resume. Gear extension "significantly reduced the aircraft's speed", but recovery "would
  have been doubtful without loss of the slat".
- On the CVR: "a factor we cannot ignore and cannot sanction".

In 1995 it answered Gibson issue by issue. The CVR held nothing contemporaneous and was "largely irrelevant". The other
slat events were known and controlled by their crews. "A" pressure lasts minutes after a breach, and the 1977 event
was not similar. **James Albright** (Code 7700) sides with the NTSB and Boeing and reads the episode as a lapse of
flight discipline.

## Outcome

The Board adopted AAR-81-8 on 9 June 1981, Driver, McAdams and Bursley voting and King and Goldman not participating.
Its probable cause named the isolated No. 7 slat and the captain's untimely inputs, with the slat's misalignment and
the captain's distraction contributing, and attributed the extension to the crew. It denied ALPA's petition on 15
December 1983 and Gibson's on 4 May 1995. The Ninth Circuit dismissed his petition for review on 7 July 1997 for want
of jurisdiction. The finding was never changed in the sources read, and nothing was reversed.

## Analysis

**TOPAK keeps the record that would have settled what happened, and not why.** The question the Board could not close
was whether a person moved the flap lever. Under ADR-0042 §3 every admitted `Actuate` leaves a record the mechanism
writes and "the principal does not write ... and cannot", and its digests survive erasure (ADR-0028 F1). A cell whose
flap selector is an allowlist entry has the act on its log or does not. Two limits apply:

- **Not the reason.** ADR-0052 §5 keeps the reason "unknown to the mechanism, by construction" (ADR-0007). The Board's
  "probably in an effort to improve aircraft performance" is the kind of claim TOPAK refuses to record.
- **Not the components.** ALPA's case was a fatigued bolt and a rudder that moved on its own. Those are acts no entry
  names, outside the alphabet (A-0068-7), and leave no `Actuate` record.

**The recorder was erasable by the party whose conduct was in question.** The ground-and-parking-brake interlock
narrowed the erase action's envelope, which is ADR-0028 §2's shape. But a cockpit conversation is cognitive payload,
which ADR-0028 §1 leaves erasable, so TOPAK would have let it go too. What it adds is F6, the erasure event itself,
which would have answered "could not recall". `Emergency`'s `M_ERASE`, breaking `ActivationIsForensic`, is the
forensic floor failing; here the floor held nothing, and that is the step `outside:cvr-bulk-erased-unrecorded`. The
1981 Board and the 1995 Board disagreed about what the tape was worth, which is CR-38's tension in one case.

**The gear was an entry, used far outside its range, and TOPAK has no fast path to that.** Lowering the gear in the dive
was what the Ninth Circuit called a "radical maneuver", and it broke the gear. Read against the records:

- **As written, it would be admitted.** ADR-0049 §3 decides no ranges, so a gear entry carries no speed bound.
- **With SF-9's fix, it would not.** A range made a checked field becomes a refusal. ADR-0052 retired X1, so no seat,
  emergency included, has an exception (`CallsAreAllowlisted`; `M_X1` is the exception's shape).
- **The emergency path would not reach it.** ADR-0052 §2 lets "gear at any speed" be prepared as an emergency-only
  entry. Reaching it needs a roster's quorum (`EmergencyLeaseHasARosterQuorum`), and the captain, already in the
  thinker seat, cannot hold a second seat in the round (ADR-0037 §7). The whole descent took 63 seconds.
- **What is left is ADR-0052 §7's exclusion,** "a person acting outside the mechanism", and §7's "Whether the reason
  was good ... is the review after the round, by people".

TWA 841 is that review, and it did not close. Whether the out-of-range act was even the rescue is disputed: the NTSB
credits the slat tearing away, ALPA the hydraulic rupture the gear caused. `proposed:RangeExcursion` would state an
entry's range and an excursion beyond it, prepared at promotion, which the seated person may take alone and on the
record. SF-3's `ManualReversion` puts the same question to the custodian.

**A finding no one can correct.** The investigation is the outcome, and a party contested it for sixteen years. To the
charge that a party wrote its probable cause, the Board answered that its rules invite proposed findings and it may
adopt similar wording. A member dissented on process, and a court held the denial beyond review. The overlay's rule
that "nothing a governor permitted is void" (ADR-0062 §6, Proposed) would make a correction a new record, never an
edit. SF-14's point that people compose the report to an overseer applies here to the overseer's own report.

**Where the pattern stops.** Lateral control margin, sideslip and Mach number are physics. TOPAK would not have kept a
misaligned slat retracted or decided between the Board and ALPA. TM7 fits the NTSB's reading of the captain: an insider
whose act is "recorded and not prevented". On ALPA's reading the fault is a component's, outside the alphabet.
CR-17's present, trained person was present, and his training was the dispute.
