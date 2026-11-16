---
id: 2026-AVI-CAPTAIN-HAIL-THOUGHT-EXPERIMENT
title: '"Captain Hail" — the Unfolded video''s hypothetical captain replayed at each decision point of the Learjet 60 loss, with and without hindsight'
kind: thought-experiment
date: "2026-11"
sector: aviation
setting: A constructed case in the YouTube video "How the Best Captain Would Have Saved This Learjet" (channel Unfolded), built on the 1 November 2026 Learjet 60 loss over Palm Beach County, Florida
concerns: [authority, delegation, human-in-the-loop, sensing, emergency-path, actuation, timing]
rules_at_time:
  - document: 14 CFR 91.3
    clause: "(a), (b)"
    paraphrase: the pilot in command is the final authority as to the operation of the aircraft, and in an emergency may deviate from any rule of part 91 to the extent required
  - document: Aeronautical Information Manual
    clause: "4-4-1"
    paraphrase: a pilot who judges a clearance would place the aircraft in jeopardy must request an amended clearance; 14 CFR 91.123(b) bars operating contrary to an ATC instruction except in an emergency
  - document: Aeronautical Information Manual
    clause: "7-1-27, thunderstorm avoidance"
    paraphrase: avoid by at least 20 miles a severe storm or intense echo; circumnavigate the entire area at 6/10 coverage; treat tops of 35,000 ft or more as extremely hazardous; do not trust visual appearance; divert and wait on the ground if unable to go around
  - document: Aeronautical Information Manual
    clause: "7-1-27, before and during penetration"
    paraphrase: belts tight, pitot heat and engine anti-ice on, turbulence penetration speed, autopilot altitude and speed hold off, tilt the radar antenna up and down; hold attitude and let altitude and airspeed vary; hold course and do not turn back
  - document: Airplane Upset Recovery Training Aid, Revision 2 (2008)
    clause: "2.5.5.11.2.6, 2.5.5.11.7, 2.5.5.11.9, 2.6.3.5"
    paraphrase: manoeuvre margin shrinks near maximum altitude; ice can bring a stall before the stick shaker, and autopilots can mask icing until they disconnect; when thrust cannot hold speed the only option is to descend; nose-low recovery is recognize, autopilot and autothrottle off, recover from stall if needed, roll the shortest way to wings level, then recover
  - document: FAA AC 120-111, Upset Prevention and Recovery Training (change 1, 2017)
    clause: "Chapter 4, Table 2"
    paraphrase: the nose-low template, from recognize and announce through roll, thrust and drag, recover; the manufacturer's procedures take precedence
analogue:
  - record: ADR-0032
    clause: "§4"
    note: when a budget cannot be met, the effect must not be reachable from the alphabet; deciding before the round where the aircraft will not go
  - record: ADR-0060
    clause: "§2"
    note: an intent is a charter for one round, every field the promoted seating's or narrower
  - record: ADR-0050
    clause: "§4"
    note: a deny needs no lease, quorum or peer, and declining the offered level is one; objecting to the level withdrawn is not, and has no channel
  - record: ADR-0030
    clause: "§1"
    note: no permit overrides a refusal; the 20-mile rule as a bundle deny on a measured fact
  - record: ADR-0062
    clause: "§7"
    note: the terminal behaviour is voted with the seating and not chosen by the stack; the upset recovery template is that shape, carried out by the person
  - record: ADR-0066
    clause: "§5"
    note: whether an act was right is the person's judgment, and the mechanism checks none of it
actors:
  - party: Captain Hail (hypothetical)
    role: operator
    fault: none-alleged
    note: the video's invention; 30 years in business jets, an upset-recovery instructor, flies by the FAA's guidance, and in the first run knows how the afternoon ended
  - party: The real flight crew
    role: operator
    fault: none-alleged
    note: the video states that nothing in it says what the real crew did or did not do, and that the NTSB has found fault with no one
  - party: Miami Center controller
    role: controller
    fault: none-alleged
  - party: Airborne weather radar
    role: sensor
    fault: none-alleged
    note: in the video's account it sees water, not wind, and a cell growing from below can hide under the beam
  - party: Unfolded (the video)
    role: public
    fault: none-alleged
    note: author of the thought experiment
detection:
  means: [none]
  latency: not-applicable
  note: a constructed case; the hindsight run's knowledge is the video's premise, which the video says no real pilot has
trace:
  - step: outside:preflight-go-decision
    at: decision point 1, Austin, before 10:37 EST
    note: convective SIGMETs over the Florida peninsula from before departure; what weather the real crew reviewed has not been made public
  - step: Order
    at: decision point 2, about 12:32, FL410
    note: the direct route, requested and approved with a warning of moderate to extreme precipitation (the video adds an area about 100 miles across)
  - step: Order
    at: decision point 3, about 12:36
    note: the instruction to descend to FL350, accepted; why it was given has not been explained
  - step: Order
    at: decision point 4, about 12:40
    note: deviations approved; the real crew turns left; the video cites MyRadar's analysis of a cell top rising from about 33,000 to more than 48,000 ft between 12:36 and 12:56
  - step: outside:cell-penetration-at-fl350
    at: decision point 5, about 12:47
    note: moderate turbulence, about 700 ft swings, light clear ice, minus 47 C; how the jet was flown is not public
  - step: Order
    at: decision point 6, about 12:47
    note: the climb to FL370, requested because of precipitation and approved; the jet reaches about 35,450 ft
  - step: outside:nose-low-upset
    at: decision point 7, about 12:48
    note: descent, mayday and "overspeed condition, descending"; what the crew did in the recovery is not public
  - step: outside:structural-limit
    at: the tail, time not determined
    note: the left elevator separated before impact; whether before or during the dive is the open question the video names
counterfactual:
  by: the video's Captain Hail, flying with knowledge of the ending, at each decision point in turn
  trace:
    - step: Order
      at: decision point 1, Austin
      note: the round's intent excludes the convective area before departure (south over the Keys or north of the system, more fuel, or an hour's wait); the in-flight judgment can then only narrow it (IntentNarrows; ADR-0032 §4's "not reachable from the alphabet")
    - step: outside:circumnavigate-entire-area
      at: decision point 2
      note: asks to go around the whole system rather than direct (AIM 7-1-27, 6/10 coverage)
    - step: outside:unable-to-instruction
      at: decision point 3
      note: '"unable" to the descent; under AIM 4-4-1 a request for an amended clearance, and the controller works out something else'
    - step: Decide
      at: decision point 4
      note: radar tilted up and down; any heading within 20 miles of an intense echo refused, as a bundle deny on a measured fact (BundleRefusalHonored); no threading between cells
    - step: EndRound
      at: decision point 5
      note: autopilot altitude and speed hold off and hand-flying in ice, read as the crew ending the automation's round, a deny that needs no peer (DenyAlwaysAvailable); attitude held, penetration speed, straight through
    - step: outside:request-lower-not-higher
      at: decision point 6
      note: does not ask the wing for more near the ceiling with ice; holds speed and attitude toward the thinnest side and, if he must change altitude, asks to go down
    - step: EndLease
      at: decision point 7
      note: the upset ends the cruise envelope; nothing is granted by the ending (ExpiryGrantsNothing)
    - step: Recover
      at: decision point 7, first seconds
      note: the nose-low template fixed in advance (recognize, autopilot off, unload if stalled, roll the shortest way to wings level, thrust idle and speedbrakes, a smooth pull within the structure); TerminalNeverWaits only if nothing gates it
    - step: outside:structural-limit
      at: the tail
      note: the video's own limit; if the elevator goes, "it is no longer a test of skill"
  holds: [IntentNarrows, BundleRefusalHonored, DenyAlwaysAvailable, ExpiryGrantsNothing, TerminalNeverWaits]
outcome:
  by: n/a (a constructed case); the real accident is under NTSB investigation (ERA27MA026)
  date: n/a
  summary: >-
    The video concludes that with hindsight a single different decision, on the ground in Austin, over the Gulf or
    at 41,000 ft, keeps everyone alive; that without it a recovery was possible only if the upset was recognized in
    the first second or two, the wings rolled level before the pull, the pull was gentle enough and the tail held;
    and that if the tail failed first it may not have mattered who was in the seat. It names three things that will
    tell which version is real: the elevator fractures, the rest of the tail, and the cockpit voice recorder. The
    NTSB recovered the recorder on 9 November and has determined no cause.
  aftermath: >-
    None. The video expects the NTSB preliminary report around the start of December and a probable cause more than
    a year away; AP reports the same timing.
  effect_reversed: not-applicable
model:
  modules: [Intent, FloorComposition, Operators, Alone, proposed:Instruction, proposed:MeasuredTrigger, proposed:VehicleEnvelope]
  properties: [IntentNarrows, BundleRefusalHonored, DenyAlwaysAvailable, ExpiryGrantsNothing, TerminalNeverWaits]
  mutations: [M_STACKGATED, M_STACKCHOOSES]
  records: [ADR-0032, ADR-0059, ADR-0060, ADR-0050, ADR-0030, ADR-0065, ADR-0062, ADR-0066, ADR-0031, ADR-0007, ADR-0068]
  findings: [CR-17, TM9, A-0068-4, A-0068-5, T-0068-9]
  fault_class: a safety argument that rests on a person's judgment at the moment, tested by replaying the moment with knowledge the person could not have
sources:
  - https://www.youtube.com/watch?v=FjK1Klk7liY
  - https://www.faa.gov/air_traffic/publications/atpubs/aim_html/chap7_section_1.html
  - https://www.faa.gov/air_traffic/publications/atpubs/aim_html/chap4_section_4.html
  - https://www.ecfr.gov/api/versioner/v1/full/2026-11-01/title-14.xml?part=91&section=91.3
  - https://www.ecfr.gov/api/versioner/v1/full/2026-11-01/title-14.xml?part=91&section=91.123
  - https://www.faa.gov/sites/faa.gov/files/other_visit/aviation_industry/airline_operators/training/AP_UpsetRecovery_Book.pdf
  - https://www.faa.gov/documentLibrary/media/Advisory_Circular/AC_120-111_CHG_1.pdf
  - https://www.ntsb.gov/investigations/Pages/ERA27MA026.aspx
  - https://www.pbs.org/newshour/nation/whats-next-in-the-investigation-of-the-learjet-crash-in-florida-that-killed-9
  - https://milesobrien.substack.com/p/five-minutes-that-might-have-made
  - https://cbsaustin.com/news/local/former-fighter-pilot-breaks-down-ntsb-updates-in-deadly-learjet-crash
verified: 2026-11-12
---

## Summary

The video *How the Best Captain Would Have Saved This Learjet* (channel Unfolded) puts an invented captain, "Captain
Hail", in the left seat of the Learjet 60 lost on 1 November 2026 ([2026-AVI-LEARJET-60-STORM-UPSET](2026-AVI-LEARJET-60-STORM-UPSET.md)),
same jet, storm and afternoon. He has 30 years in business jets, has taught upset recovery, flies "exactly the way
the FAA's own manuals say", and knows how the afternoon ended. The video calls it "a theory, not a reconstruction",
says the NTSB has determined no cause and found fault with no one, and says nothing in it describes what the real
crew did or did not do. It stops at seven decision points and asks what he would do, then reruns him without the
ending.

The seven points are preflight, the route, the descent, radar and avoidance, the penetration, the climb and the
upset, then the tail; they are in `trace`, and his answers in `counterfactual`, as the video lays them out. Without
hindsight, the video concludes, "the best captain in the world may well end up in the very same place".

Where the video differs from the sources for the real flight, this entry follows the sources: the NTSB timeline puts
the ice report and the climb request at about 12:47, not 12:45 and 12:48; the convective SIGMET text reads "area TS,
tops above FL450", and the severe turbulence and icing the video lists are what the AIM says any convective SIGMET
implies (hail is not in the text); and the cockpit voice recorder, whose survival the video treats as unknown, was
recovered on 9 November. The video's "77 seconds" to transponder loss, its MyRadar cell-top figures and its account
of former NTSB investigator Jeff Guzzetti's view were not confirmed and are attributed to the video.

## Defensive position

The case that each real decision was ordinary is the video's own second run. Without the ending, it says, Captain
Hail sees a charter to the Bahamas, a flood watch and storms in the forecast, "ordinary for Florida". He plans around
the weather he can see; the controller warns and approves a turn; the descent to 35,000 ft is routine; light ice
forms with ice protection on and working; he reports light ice and moderate turbulence and asks for a smoother ride;
higher looks smoother, so he asks to climb, and it is approved. "Would Captain Hail have made those same calls
without knowing the ending? Nobody can say."

Others on record point the same way. **John Cox** (AP) says the pilots steered around the larger cell, and the one
they entered developed rapidly. **Miles O'Brien** calls each step individually defensible. And the video's
conclusion places the last word with the structure: if the tail failed first, "it may not have mattered who was in
the seat".

## Adversarial position

The case from the guidance, as the video quotes it, checked here against the primary text:

1. **Preflight.** "The skill is in deciding where you will not go before you leave." The AIM: "Do divert and wait out
   the thunderstorms on the ground if unable to navigate around an area of thunderstorms." The upset aid lists
   thunderstorms and icing as weather "pilots should take into consideration in flight planning".
2. **Route.** AIM 7-1-27: "Do circumnavigate the entire area if the area has 6/10 thunderstorm coverage."
3. **Descent.** 14 CFR 91.3(a) makes the captain the final authority; AIM 4-4-1 makes it the pilot's responsibility
   to request an amended clearance when one would place the aircraft in jeopardy. Cox (AP): "I'd rather be at 41
   than at 35."
4. **Radar and avoidance.** The AIM: radar "does not detect turbulence"; "Do avoid by at least 20 miles" a severe
   storm or intense echo; tops of 35,000 ft or more are "extremely hazardous"; "tilt the antenna up and down
   occasionally". The tilt line is among the AIM's steps before a penetration; the video uses it for avoidance.
5. **Penetration.** The AIM's list: belts, anti-ice, penetration speed, altitude and speed hold off, "maintain constant
   attitude", "Don't turn back". The upset aid: "Autopilots and autothrottles can mask the effects of airframe
   icing", and autopilots have disconnected "with the airplane on the brink of a stall".
6. **Climb.** The upset aid: manoeuvre margin "decreases significantly" near maximum altitude; with ice an airplane may
   show stall onset "before stick shaker activation"; when thrust cannot hold the speed, "the only option is to descend".
   **Matthew Buckley** (CBS Austin): Learjet "did not design that wing for even a little bit of ice buildup". The
   video sets Pulkovo 612 (2006), a climb over storms that ended in a stall, against this decision.
7. **Upset.** AC 120-111's nose-low template and the aid's summary: recognize and confirm, autopilot and autothrottle
   off, recover from the stall if needed, roll the shortest way to wings level (unloading first), thrust and drag,
   then recover, avoiding "excessive G loading". The aid gives 2.5 g in cruise for jet transports; no source read
   here gives the Learjet 60's limits.

**O'Brien** makes the cumulative form: small defensible choices add up, and a wider route might have cost five to ten
minutes.

## Outcome

None for the thought experiment, which claims nothing happened. The video says three things will decide which
version is real (the elevator fractures, the rest of the tail, the voice recorder). The NTSB has recovered the
recorder, says the left elevator separated before impact, and has determined no cause.

## Analysis

**The hindsight run is a run TOPAK can mostly write; the second run is the finding.** Captain Hail's first run uses
existing actions: an intent fixed before the round (`Order`, `IntentNarrows`), a bundle refusal on a measured fact
(`Decide`, `BundleRefusalHonored`), the crew ending the automation's round (`EndRound`, `DenyAlwaysAvailable`), and a
recovery after the envelope ends (`EndLease`, `Recover`, `ExpiryGrantsNothing`, `TerminalNeverWaits`). Every one of
them is fired by a person who already knows which cell will grow. The video's rerun removes that knowledge and gets
back the real trace, every step of which passes the same checks. That is ADR-0066 §5 exactly: "Whether the act was
right is the person's judgment, and the mechanism checks none of it", and A-0068-5's trained, authorized person
"can see what the act requires". CR-17 and TM9 meet here: nobody is deceived, and a present, trained person cannot
see what the act requires because it is in the future. The counterfactual's `holds` list is true of the replay and
says nothing about whether a crew can be expected to produce it.

**"Decide where you will not go before you leave" is ADR-0032 §4's answer.** When no budget can be met, "the effect
must not be reachable from the alphabet at all". An envelope fixed at Austin (ADR-0060 §2, an intent "bounded by the
promoted seating") turns decision points 2 to 6 from judgments inside a storm into refusals of what the intent never
held. That is the strongest thing TOPAK says here, and the video says it first. Its limit: the envelope is drawn from
the forecast, and a cell that grows from 33,000 to 48,000 ft in twenty minutes is outside any forecast polygon.

**"Unable" has two halves, and TOPAK states one.** The descent offers FL350 and withdraws FL410. Declining the
offer is a local deny that TOPAK already has: nothing obliges a principal to use a permission, "consensus for grants,
local for denials" (ADR-0038 §5), and a deny needs no quorum (ADR-0050 §4). Objecting to the withdrawal is what
TOPAK cannot state. A parent's subtraction "applies on receipt, before it is ordered anywhere" (ADR-0065 §1), so
there is no interval in which the child's objection is raised and heard, and holding FL410 anyway would keep
authority the parent withdrew. Aviation does not grant that either: outside an emergency "unable" is a request for an
amended clearance (AIM 4-4-1) under an instruction that binds (91.123(b)), answered by the controller's re-plan; in
an emergency the captain deviates and reports (91.3(b)). In Überlingen
([2002-AVI-UBERLINGEN-TCAS](2002-AVI-UBERLINGEN-TCAS.md)) the question was which of two authorities wins; here it is
what a seated principal may do when it judges its parent's instruction unsafe. TOPAK's on-receipt rule is right
under its premise, since a captured child that could decline narrowings would decline every revocation. What
survives the premise is `proposed:Instruction`, narrowed: a parent's instruction to act as an obligation with a
deadline; the child's objection as an attributed report that triggers re-planning, reaching the parent as labelled
ingress and retaining nothing; an emergency deviation recorded and reported after. Its mutation is an objection that
retains the withdrawn authority. This extends SF-1: refusing the descent is the safe direction for the jet and an act
inside the controller's plan.

**Coffin corner is an envelope narrowing inside the round.** ADR-0031 §4 makes authority narrow across renewal; the
jet's physical envelope narrowed by itself, with altitude and ice, while the request asked for more. The video's
"does not ask the wing for more" is a bundle deny on the jet's own margin, which only `proposed:VehicleEnvelope` (the
companion entry) would lift. The guidance pulls both ways, which matters for any rule fixed in advance: the AIM's
-15 C penetration altitude was met at minus 47 C, and the same upset aid that warns of autopilots masking ice says
"There is no need to take quick drastic action or immediately disconnect a correctly functioning autopilot."

**The recovery template is a terminal behaviour, gated on recognition.** ADR-0062 §7 votes the terminal behaviour
with the seating and keeps it from the stack; AC 120-111's template is fixed in advance, and "the manufacturer's
procedures take precedence". That is SF-16's shape. But the template's first line is "Recognize and confirm the
developing situation", so the terminal behaviour waits on the person's diagnosis by design: Alone's `M_STACKGATED`,
breaking `TerminalNeverWaits`, with the person in the stack's place, as in AF447
([2009-AVI-AIR-FRANCE-447](2009-AVI-AIR-FRANCE-447.md)). At 30,000 ft per minute the video prices each second at
about 500 ft. `proposed:MeasuredTrigger` would fire the terminal behaviour on a fact the governor measures (pitch,
bank, speed past a bound) and not on recognition; whether any mechanism should fly that recovery in a Learjet is a
question for its manufacturer, not for TOPAK. Choosing which recovery to fly is `M_STACKCHOOSES`.

**Where the pattern stops.** The structural limit. If the elevator fails, the video says, "it is no longer a test of
skill", and no module has flutter, load factor or an elevator. T-0068-9 and A-0068-4 assume a recovery function that
reaches a safe state in bounded time; a separated control surface is that assumption false, with no fault anywhere
in the authority. ADR-0045's "can only subtract" has no column for a body that keeps falling (SF-1).

**Outside steps.** `preflight-go-decision`, `cell-penetration-at-fl350`, `nose-low-upset`, `structural-limit`; in
the counterfactual `circumnavigate-entire-area`, `unable-to-instruction`, `request-lower-not-higher`.
