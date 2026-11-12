---
id: 2006-AVI-PULKOVO-612-STALL
title: Pulkovo 612, Tu-154M RA-85185, 22 August 2006 — a climb to FL390 over a storm, a stall warning answered by nobody, and a flat spin
kind: incident
date: 2006-08-22
sector: aviation
setting: Pulkovo Aviation Enterprise flight FV 612, Tupolev Tu-154M RA-85185, Anapa to St Petersburg, at FL380 to FL390 in the Kharkiv control area north of Donetsk, Ukraine
concerns: [human-in-the-loop, monitoring, authority, emergency-path, timing]
rules_at_time:
  - document: Tu-154M flight operations manual (RLE), as the MAK commission describes it
    clause: "4.4.4(1)"
    paraphrase: when the AUASP angle-of-attack and g-load warning operates, the crew takes measures to increase speed
  - document: Tu-154M flight operations manual (RLE), as the MAK commission describes it
    clause: flight in turbulence
    paraphrase: the autopilot is to be disconnected on entering severe turbulence; recommended indicated speeds and Mach numbers are to be held in the climb and in turbulence; the commission found several of these clauses, and the maximum permitted altitude, open to different readings
  - document: Tu-154M flight operations manual (RLE), as the MAK commission describes it
    clause: maximum altitude for weight
    paraphrase: at the actual weight, under 85 t, the crew was entitled to FL390 (11,900 m)
  - document: Russian rules on crew composition, as the MAK commission describes them
    clause: second pilot-trainee
    paraphrase: a second pilot-trainee may not occupy the seat for landings below ICAO Category I; no other restriction on occupying the seat
analogue:
  - record: ADR-0032
    clause: "§4"
    note: W + L + D < T_irrev; when no budget can be met, the effect must not be reachable from the alphabet at all
  - record: ADR-0038
    clause: "§5"
    note: a finding from any Observer blocks the target's next admit, with no agreement sought
  - record: ADR-0062
    clause: "§7"
    note: the terminal behaviour is voted with the seating and the stack does not choose it; "a stall that never ends is safe" is false of a vehicle in flight
  - record: ADR-0037
    clause: "§7"
    note: a principal holds one seat; who sits where is fixed at the grant, not in the round
actors:
  - party: Captain-instructor (pilot flying)
    role: operator
    fault: contested
    note: MAK found late autopilot disconnection, speeds not held, uncoordinated pitch control, and RLE 4.4.4(1) not applied; the airline said the crew broke no operating rule
  - party: Second pilot-trainee (right seat), navigator, flight engineer
    role: monitor
    fault: omission
    note: MAK found they did not monitor speed, Mach and angle of attack or tell the captain when limits were exceeded; it found the trainee's licensing simplified against ICAO Annex 1
  - party: Regular second pilot
    role: operator
    fault: none-alleged
    note: in the cockpit and not taking part in control; MAK found the captain had not seated him in place of the trainee for weather he expected
  - party: AUASP angle-of-attack and g-load warning
    role: monitor
    fault: none-alleged
    note: operated twice briefly at FL380 in gusts, again under autopilot at FL390, then repeatedly in manual flight
  - party: Autopilot and stability augmentation (ABSU, SUU)
    role: automation
    fault: none-alleged
    note: 'MAK: "worked according to their built-in logic"; altitude hold, most probably engaged with the climb still at 8-10 m/s, took the aircraft past operational angle of attack'
  - party: Kharkiv area control and meteorological services
    role: controller
    fault: omission
    note: the thunderstorm and hail situation was not passed to the crew on entry to the Kharkiv FIR; MAK names no unit, addresses its weather recommendations to Ukraerorukh and the meteorological services, and finds this and the controllers' inaccuracies not directly causal
  - party: Tupolev, the flight manual and the Tu-154 simulators
    role: vendor
    fault: contested
    note: MAK found ambiguous RLE clauses and simulators unable to reproduce critical angles of attack; the airline blamed design features; three institutes and Tupolev found control and warning margins sufficient
  - party: Pulkovo (GTK Rossiya)
    role: supervisor
    fault: contested
    note: crew composition and training; contested the commission's version
detection:
  means: [alarm, investigation]
  latency: seconds
  note: the AUASP warned in seconds; the crew reported turbulence at 15:37 Moscow time and the aircraft left radar about two minutes later; MAK announced the end of its investigation on 6 February 2007
trace:
  - step: outside:forecast-storms-briefed
    at: Anapa, before departure
    note: the crew had the forecast, including possible thunderstorms, cloud tops to 12 km and a cold front with waves
  - step: outside:storm-picture-not-relayed
    at: entry to the Kharkiv FIR
    note: the thunderstorm and hail situation was not passed to the crew; per MAK, possibly kept it from a full assessment, not causal
  - step: Finding
    at: FL380, moderate to severe turbulence
    note: Observers.tla's finding, read as the AUASP's; twice, under a second each, gusts to 7 m/s and 1.5 g
  - step: outside:finding-unwired-autopilot-kept
    at: same
    note: the RLE asks for the autopilot off in severe turbulence; it stayed on
  - step: outside:climb-at-twice-available-rate
    at: FL380 to FL390, with clearance
    note: probably to pass over the turbulence; 8-10 m/s, twice what was available; speed fell to about 420 km/h, Mach 0.74; hail in the climb
  - step: outside:altitude-hold-captured-in-the-climb
    at: FL390
    note: most probably altitude hold engaged with 8-10 m/s still on; under autopilot the aircraft passes operational angle of attack; the AUASP sounds again
  - step: EndLease
    at: after the second AUASP warning at FL390
    note: Alone.tla's ending; the crew, most probably the captain, disconnects both autopilot channels; nothing fixed follows
  - step: outside:pitch-oscillation-manual
    at: manual flight
    note: uncoordinated pitch inputs build an oscillation; trim mechanism use removes stick-force feedback; repeated AUASP warnings
  - step: outside:stall-warning-not-actioned
    at: same
    note: RLE 4.4.4(1) not applied; no crew member calls speed or angle of attack
  - step: outside:pitch-up-to-three-times-limit
    at: end of the manual phase
    note: what MAK calls "aerodynamic pick-up", at about three times the permitted angle of attack; the side engines shut down
  - step: outside:flat-spin-to-impact
    at: about 15:39 Moscow time
    note: no break-up in the air; impact at high vertical speed and almost no forward speed, about 45 km north of Donetsk; 170 killed
counterfactual:
  by: the crew under the flight manual MAK cites, with the seating MAK recommends fixed before the weather, read in TOPAK's terms
  trace:
    - step: Grant
      at: before the Kharkiv sector, with storms forecast
      note: the regular second pilot holds the right seat (MAK recommendation 5.1.3)
    - step: Finding
      at: FL380
      note: the AUASP's two warnings in gusts
    - step: EndLease
      at: same
      note: autopilot off in severe turbulence, as the RLE asks
    - step: Refuse
      at: same
      note: the climb is refused while the finding stands (DenyByAnyOf); the aircraft keeps its level
    - step: outside:turbulence-speed-held-lateral-avoidance
      at: through the cells
      note: the RLE's turbulence speed and Mach held; avoidance laterally and in time, which MAK found was decided late
    - step: outside:stall-warning-answered-by-speed
      at: on any later warning
      note: RLE 4.4.4(1), increase speed, as a fixed act the monitoring pilot calls
  holds: [DenyByAnyOf, ExpiryGrantsNothing, UnreadBounded]
outcome:
  by: Interstate Aviation Committee (MAK) technical commission; Russian government commission
  date: 2007-02-17
  summary: >-
    The commission found the cause to be bringing the aircraft, in manual flight, to supercritical angles of attack
    and a stall, then a flat spin and impact at high vertical speed. It explained this by the absence from the flight
    manual and training programmes of guidance on pitch handling and on the electric trim mechanism, and the
    impossibility of training manual flight at high altitude and angle of attack for want of suitable simulators;
    in avoiding storms and turbulence the crew let the aircraft oscillate in pitch past the operational range of angle
    of attack. Lack of speed monitoring, the manual's stall-prevention instructions not followed, and unsatisfactory
    crew interaction kept the situation from being stopped. The aircraft and engines worked until the stall; air
    traffic and weather shortcomings were not directly causal.
  aftermath: >-
    Recommendations to CIS authorities, the airline, Russian authorities, Ukrainian air navigation, the
    meteorological service and Tupolev: consider barring types without full-motion simulators matching them in every
    regime; more simulator training at high altitude and angle of attack; rules for when an inexperienced crew member
    must be replaced and how seats are changed; RLE amendments on turbulence speeds, stall, oscillation and the trim
    mechanism; simulator upgrades and training flights in the real aircraft; licensing aligned with ICAO Annex 1;
    psychological selection; SIGMET exchange between adjacent FIRs; solid-state recorders.
  effect_reversed: "no"
model:
  modules: [Observers, Coupling, Alone, RunSeats, proposed:SeatHandover, proposed:MarginEnvelope]
  properties: [DenyByAnyOf, UnreadBounded, ExpiryGrantsNothing, TerminalNeverWaits]
  mutations: [M_MARK, M_STACKGATED]
  records: [ADR-0032, ADR-0038, ADR-0039, ADR-0062, ADR-0037, ADR-0052, ADR-0007, ADR-0040, ADR-0068]
  findings: [CR-2, CR-17, TM1, A-0068-4, A-0068-7]
  fault_class: an act the envelope allowed, taken inside a margin that narrowed with it, a monitor that worked and was wired to nothing, and a monitoring seat held by the least experienced person
sources:
  - https://mak-iac.org/upload/iblock/9a7/Tu-154M_22-08-2006.pdf
  - https://news.bbc.co.uk/2/hi/europe/5276784.stm
  - https://www.theguardian.com/world/2006/aug/23/russia.theairlineindustry
  - https://www.kommersant.ru/doc/726899
  - https://lenta.ru/news/2007/02/07/final
  - https://www.newsru.co.il/world/7feb2007/donetsk_tu.html
  - https://www.youtube.com/watch?v=FjK1Klk7liY
verified: 2026-11-12
---

## Summary

Pulkovo flight FV 612, a Tu-154M, left Anapa for St Petersburg on 22 August 2006 with 160 passengers, 45 of them
children under 12 by the airline's count, and 10 crew. The crew had the forecast before departure: possible
thunderstorms, cloud tops up to 12 km, a cold front with waves. Under Rostov control they passed a storm area to the
right with clearance and without changing altitude. The thunderstorm and hail situation in the Kharkiv flight
information region had not been passed to the crew when the flight entered it.

At FL380 (11,600 m) near Donetsk, at Mach 0.80 to 0.83, the aircraft met moderate to severe turbulence. Vertical
gusts of up to 7 m/s twice set off the AUASP angle-of-attack and g-load warning for less than a second, with up to
1.5 g. The autopilot stayed on. With clearance, the captain-instructor began a climb to FL390 (11,900 m), which the
weight allowed, probably to pass over the turbulence, and turned left to avoid cells. The climb ran at 8 to 10 m/s,
twice the rate available, and the speed fell to about 420 km/h, Mach 0.74; the aircraft met hail in the climb. The
crew most probably engaged altitude hold with that climb rate still on. Under the autopilot the aircraft passed the
operational angle of attack and the AUASP sounded again.

After the second warning the crew, most probably the captain, disconnected the autopilot. In manual flight the
captain's pitch inputs built an oscillation, and his use of the electric trim-feel mechanism took away stick-force
feedback. The AUASP sounded repeatedly. The aircraft reached about three times the permitted angle of attack, pitched
up and entered a flat spin. The side engines shut down. The crew sent a distress call reporting turbulence at 15:37
Moscow time, and the aircraft left radar about two minutes later. It struck a field about 45 km north of Donetsk at
high vertical speed and almost no forward speed, intact until impact. All 170 died.

The captain-instructor flew from the left seat. The right seat was held by a second pilot-trainee, strapped in. The
regular second pilot was in the cockpit and took no active part. The video that cites this flight says the crew
"climbs to get above the weather"; MAK says the climb was probably to pass over the turbulence.

## Defensive position

**Sergei Mikhalchenko, general director of GTK Rossiya** (Pulkovo's successor), presented the airline's own
investigation on 1 December 2006, as Kommersant reported:

- The crew "did not break the operating rules"; 11,600 m was permissible for the weight and the weather.
- The cause was "a combination of factors", turbulence and the Tu-154's design: "this aircraft does not recover from a
  flat spin". The only way to avoid it would be to bar every Tu-154 from flying above 10,000 m.

In February 2007, Kommersant (via Lenta.ru) reported the airline's fuller version:

- The crew followed a corridor Ukrainian controllers had given it, and a mesocyclone forecasters had not warned of
  caught the aircraft.
- The vortex distorted the navigation instruments, which disturbed the autopilot and set the nose oscillating.
- An updraft, not the crew, threw the aircraft near-vertical at 12,800 m.

The airline held that controllers, forecasters and the type's designers should share the responsibility.

Inside the investigation, **MAK's flight subcommission** voiced the view that the Tu-154M has small stability and
control margins in turbulence at high altitude. The commission's chairman asked for further analysis.

## Adversarial position

**The MAK technical commission** found:

- **The decision.** The crew misjudged the weather at FL360 to FL380 and decided late to avoid the cells, by climbing
  to 11,900 m "without ensuring the required 500 m margin", which took it into hazardous weather.
- **The captain-instructor:**
  - did not put the experienced second pilot in the right seat for weather he expected;
  - disconnected the autopilot late in severe turbulence;
  - did not hold the manual's speeds and Mach;
  - flew pitch uncoordinatedly into the stall;
  - did not increase speed when the AUASP sounded (RLE 4.4.4(1)).
- **The crew.** Its other members did not monitor speed, Mach and angle of attack or report exceedances, "the absence
  of proper interaction in the crew".
- **The trainee.** Licensed under Russian norms with substantial simplifications against ICAO Annex 1.
- **The captain's psychological testing**, in its medical section: traits that could have slowed decisions under
  stress.

**Three state institutes** (TsAGI, LII, GosNII GA) and the Tupolev design bureau, asked by the chairman, answered that
control effectiveness in the manual's regimes is sufficient. The warning's settings leave enough margin, and the
aircraft could have been returned to operational angles of attack "at any moment ... up to the stall". **MAK's
experts**, as Kommersant reported, found the recorders showed no outside force such as an updraft, and modelled
angles of attack of 15 to 20 degrees and more against a normal 5 to 6.

## Outcome

MAK announced the end of its technical investigation on 6 February 2007. It reported the results on 17 February 2007 to
the government commission chaired by the Russian transport minister, in the presence of GTK Rossiya's management.
The cause it found is the manual flight to supercritical angles of attack, the stall and the flat spin. It explained
these by:

- the manual and training gaps;
- simulators that could not reproduce the regime;
- the pitch oscillation in avoiding the storms;
- the failure to monitor speed or follow the manual's stall instructions.

It issued recommendations on simulators, training, crew composition and seat changes, the manual, licensing,
psychological selection, weather information between control areas and recorders. Nothing was reversed.

## Analysis

**The climb was an act the envelope allowed, taken inside a margin that narrowed with it.** FL390 was permitted at the
weight, and ATC cleared it.

- **What was not bounded.** What made the climb dangerous was its rate, twice what was available, and the speed it
  cost. SF-8's point holds: the envelope did not bound the size of the act.
- **What TOPAK's floor reads.** It decides over symbolic parameters, never instances (ADR-0040 §5). It has no notion of
  a margin that shrinks with altitude, speed and gust, what the video calls the coffin corner.
- **The bound that was there.** MAK found the manual's maximum-altitude limit open to different readings. That is
  SF-8's vacuous envelope in the one dimension that mattered.
- **What would state it.** `proposed:MarginEnvelope`: an entry admissible only while a measured margin, such as speed
  above the stall warning, stays above a declared floor. The measuring source is a trust root, as T-0068-4 makes the
  measure of an extent, and a mutation admits on the stale margin.

**The warning worked, and was wired to nothing.** The AUASP fired at FL380, again under the autopilot at FL390, and
repeatedly in manual flight.

- **In TOPAK.** Any finding blocks the target's next admit (`DenyByAnyOf`, ADR-0038 §5), so the climb after the first
  two warnings is refused. That is the counterfactual's `Refuse`.
- **The limit.** A finding subtracts (ADR-0007), and the act the manual prescribed, more speed, is an act. Pulkovo is
  SF-1's case that the safe move was an act.
- **Against AF447.** There the warning was silenced by design at the extreme (SF-5.4). Here it was valid, live and
  repeated, which is SF-5's fifth shape: a finding live, reported and acting on nothing.
- **The monitoring seat.** MAK found the other crew members did not call the speed or angle of attack. That is a human
  Observer present and not progressing: `Coupling` under `M_MARK`, with `UnreadBounded` failing (SF-5.2).

**The investigator wrote SF-15's seat-handover rule, and placed it before the hazard.** MAK recommended rules for
"conditions under which an inexperienced specialist must be replaced by an experienced one" and "the order of
changing seats in the cockpit" (5.1.3, 5.3.2; in translation, as are the other quotations from Russian here).

- **The fit.** That is `proposed:SeatHandover`. Teterboro asked who takes over inside the approach. Pulkovo's answer
  is a seating rule fixed before the storm: the declared condition, forecast storms, selects who may hold the
  monitoring seat.
- **What TOPAK has.** ADR-0037 §7 seats one principal per seat, and the grant fixes it. A deployment could declare
  that rule as a narrowing at the grant (the counterfactual's `Grant`).
- **What TOPAK lacks.** Nothing says a monitoring seat needs more qualification as conditions worsen. CR-17's
  "present, trained, authorized" person was present and was the least trained person in the cockpit.

**A judgment inside the storm, where the budget could not be met.** ADR-0032 §4 sets `W + L + D < T_irrev`.

- **The terms.** `L` was under a second, the AUASP. `D`, the crew's response, was not met. For a stall into a flat spin
  at 12 km, `T_irrev` is short; the airline says the type does not recover.
- **The record's answer.** When no budget can be met, "the effect must not be reachable from the alphabet at all".
  Mikhalchenko's remedy, no Tu-154 above 10,000 m, is that sentence.
- **Where it lands.** The spin is the body's, outside the alphabet (TM1's residual; A-0068-7). What is reachable is
  the climb. So the bound belongs in the seating and the envelope, set before the flight, not in the captain's
  judgment inside the cell. MAK's "late decision" finding and its weather-information recommendations read the same
  way.

**The automation handed back, and nothing fixed followed.** Disconnecting the autopilot is an ending (`EndLease`) that
grants nothing. ADR-0062 §7 asks for a terminal behaviour voted with the seating. RLE 4.4.4(1), increase speed, is
the nearest thing to one, and it waited on the crew: `M_STACKGATED`'s shape, breaking `TerminalNeverWaits`, with a
person in the stack's place, as at AF447 (SF-16). The automation's own part is different from AF447's. There it
withdrew on a sensor finding; here it obeyed an altitude-hold capture the state could not support, "according to its
built-in logic".

**Training that could not be done.** MAK found the quarterly simulator exercise on the approach to critical angle of
attack impossible on the analogue Tu-154 trainer. Recommendation 5.4.2 asks to restore training flights in the real
aircraft. ADR-0052 §6's "a drill is a real activation" is the same instinct. Pulkovo adds to SF-3: an exercise on the
books that the device cannot perform proves only that it was scheduled.

**Where the pattern stops.** Stall angle, buffet margin, gusts and spin recovery are physics. The institutes and the
airline disagree about the type's margins, and TOPAK cannot settle that. What the corpus can say is narrower:
a finding should have stopped the climb, and the seating should have been decided before the weather.
