---
id: 2026-AVI-LEARJET-60-STORM-UPSET
title: Learjet 60 N722BD, Palm Beach County, 1 November 2026 — a climb approved in a storm cell, an overspeed descent, and a left elevator found miles away
kind: incident
date: 2026-11-01
sector: aviation
setting: Learjet 60 N722BD, operated by Aurora Aviation dba Upper Jet, Austin-Bergstrom to North Eleuthera, Bahamas, under Miami Center, lost near Military Trail, Greenacres area, Palm Beach County, Florida
concerns: [authority, delegation, human-in-the-loop, sensing, monitoring, actuation]
rules_at_time:
  - document: 14 CFR 91.3
    clause: "(a), (b)"
    paraphrase: the pilot in command is directly responsible for, and the final authority as to, the operation of the aircraft; in an in-flight emergency requiring immediate action may deviate from any rule of part 91 to the extent required
  - document: 14 CFR 91.123
    clause: "(a), (b)"
    paraphrase: no deviation from a clearance without an amended clearance, an emergency or a TCAS resolution advisory; except in an emergency, no one may operate contrary to an ATC instruction
  - document: Aeronautical Information Manual
    clause: "4-4-1"
    paraphrase: if a clearance would in the pilot's opinion place the aircraft in jeopardy, it is the pilot's responsibility to request an amended clearance
  - document: Aeronautical Information Manual
    clause: "7-1-6 (convective SIGMET)"
    paraphrase: any convective SIGMET implies severe or greater turbulence, severe icing and low-level wind shear
  - document: Aeronautical Information Manual
    clause: "7-1-26, 7-1-27"
    paraphrase: radar shows precipitation, not turbulence; avoid intense echoes by at least 20 miles; circumnavigate an area with 6/10 coverage; treat tops of 35,000 ft or more as extremely hazardous; if penetration cannot be avoided, hold attitude, turbulence penetration speed, altitude and speed hold off, no turning back
  - document: Convective SIGMET 45E (Aviation Weather Center, issued 1655Z, valid until 1855Z)
    clause: area 70ESE OMN-70E MIA-50E EYW-20WNW PIE
    paraphrase: an area of thunderstorms moving little over the southern Florida peninsula and coastal waters, Palm Beach County inside it, tops above FL450; earlier issues (35E, 39E, 42E) covered the peninsula from before departure
analogue:
  - record: ADR-0060
    clause: "§2"
    note: a later intent comes from one person and is checked against the promoted seating, not against what the vehicle can do now
  - record: ADR-0062
    clause: "§1, §4"
    note: the governor lifts its own facts (time, position, count, extent); a vehicle's aerodynamic margin is not among them, and an extent is a declaration
  - record: ADR-0065
    clause: "§1"
    note: a governor's measured facts may refuse and never permit; the shape a measured "unable" would have
  - record: ADR-0059
    clause: "§3"
    note: the kinds of narrowing a parent may impose; none moves a body, and none is an instruction to act
  - record: ADR-0062
    clause: "§7"
    note: the terminal behaviour is voted with the seating; each vehicle class declares a safe state reached in bounded time
actors:
  - party: Flight crew (captain and first officer)
    role: operator
    fault: none-alleged
    note: the NTSB has made no finding; commentators on record questioned the route and altitude choices (see Adversarial position)
  - party: Miami Center controller
    role: controller
    fault: none-alleged
    note: warned of the weather, instructed the descent to FL350, approved deviations and the climb; no reason for the descent has been published
  - party: Aurora Aviation dba Upper Jet
    role: supervisor
    fault: none-alleged
    note: operator of record; the NTSB will interview its officials and review maintenance and crew records
  - party: Learjet 60 airframe, left elevator
    role: actuator
    fault: none-alleged
    note: separated before impact; the NTSB has not determined whether its loss contributed or resulted from the descent
  - party: Airborne weather radar
    role: sensor
    fault: none-alleged
    note: the NTSB will check what it showed and whether the crew knew the cell was there
  - party: National Transportation Safety Board
    role: investigator
    fault: none-alleged
detection:
  means: [operator, investigation]
  latency: seconds
  note: the crew announced the descent and a mayday within about 30 seconds of the climb approval; the pre-impact separation was found by the NTSB's debris search within two days
trace:
  - step: outside:departure-under-convective-sigmet
    at: 10:37 EST, Austin
    note: convective SIGMETs 35E and 39E covered the Florida peninsula; what weather the crew reviewed is not public
  - step: outside:controller-weather-advisory
    at: about 12:31, FL410 over the Gulf
    note: Miami Center reports precipitation ahead and offers left or right; an advisory that refuses nothing
  - step: Order
    at: about 12:32
    note: a direct routing toward Freeport or the Bahamas, requested by the crew and approved with a warning of moderate to extreme precipitation; checked against the controller's airspace and traffic, as IntentNarrows checks an intent against the seating
  - step: outside:crew-revises-route
    at: about 12:35
    note: toward a southwest Florida waypoint, then the Bahamas
  - step: Order
    at: about 12:36
    note: descend from FL410 to FL350; an instruction, which TOPAK has no form for (outside:instruction-to-act in Analysis); no reason published
  - step: Order
    at: about 12:40
    note: deviations left or right approved, direct Freeport when able; tracking shows the jet heading north toward Palm Beach County
  - step: outside:cell-develops-at-cruise-level
    at: 12:40 to 12:47
    note: John Cox told AP the flight steered around a larger cell into a smaller, rapidly developing one; radar overlays show a small cell that quickly worsened near 35,000 ft
  - step: outside:crew-reports-ice-and-turbulence
    at: about 12:47, FL350
    note: light clear ice, "manageable"; moderate turbulence; altitude deviations of about 700 ft; outside air temperature minus 47 C
  - step: Order
    at: about 12:47
    note: climb to FL370 requested because of precipitation and approved; nothing in the grant reads the aircraft's margin
  - step: outside:upset-during-climb
    at: about 12:48
    note: the jet reaches about 35,450 ft and descends; less than 30 seconds after the approval the crew announces the descent and a mayday, then "overspeed condition, descending"; no cause determined
  - step: outside:altitude-at-pilot-discretion
    at: about 12:48
    note: Fox News reports the controller gave altitude at the crew's discretion and asked what they needed
  - step: outside:in-flight-separation-of-left-elevator
    at: during the descent, time not determined
    note: most of the left elevator found in three pieces 1.3 to 3.8 miles from the impact site
  - step: outside:impact
    at: about 12:49 to 12:51
    note: AP reports descent rates of 10,000 rising to 30,000 ft per minute; nine aboard killed, one person injured on the ground
outcome:
  by: National Transportation Safety Board (ERA27MA026), with the FAA
  date: 2026-11-09
  summary: >-
    The investigation is open and no cause has been determined. NTSB Member Tom Chapman said on 2 November that
    weather conditions are "a major focus", that conditions at cruise altitude are still to be determined, that the
    NTSB has not confirmed whether the jet flew through an active thunderstorm, and that there is "some indication
    that the aircraft was breaking before impact". On 3 November he said most of the left elevator had been found
    in three pieces 1.3 to 3.8 miles from the site and that "the distance from the site indicates that it separated
    before impact", without determining whether its loss contributed or was caused by the high-speed descent. On
    8 November the NTSB completed on-scene work except excavation, and on 9 November it recovered the cockpit voice
    recorder at the site of initial impact and sent it to its Vehicle Recorders Laboratory. The NTSB's case page
    lists no findings and no recommendations.
  aftermath: >-
    None yet. AP reports a preliminary report, with facts and no cause, is expected about 30 days after the crash,
    and a final report with probable cause typically 12 to 18 months after. The NTSB has asked anyone who finds
    debris to report it and not to keep or move it.
  effect_reversed: "no"
model:
  modules: [Intent, Operators, Peer, Alone, proposed:VehicleEnvelope]
  properties: [IntentNarrows, NarrowsInReceived, DenyAlwaysAvailable, TerminalNeverWaits]
  mutations: []
  records: [ADR-0059, ADR-0060, ADR-0062, ADR-0065, ADR-0050, ADR-0030, ADR-0031, ADR-0007, ADR-0045, ADR-0068]
  findings: [CR-17, TM9, A-0068-4, A-0068-8, T-0068-9]
  fault_class: an open investigation with no cause; grants checked against the grantor's rules and not the grantee's state, advisories that refuse nothing, and a sensor that reports a proxy
sources:
  - https://www.ntsb.gov/investigations/Pages/ERA27MA026.aspx
  - https://www.wptv.com/news/palm-beach-county/region-c-palm-beach-county/ntsb-news-conference-learjet-60-crash-in-palm-beach-county/11-2-26
  - https://abcnews.com/US/learjet-breaking-crashed-florida-ntsb/story?id=137781527
  - https://pilotinq.com/news/us-ntsb-learjet-60-n722bd-elevator-found-miles-from-crash-site
  - https://www.pbs.org/newshour/nation/whats-next-in-the-investigation-of-the-learjet-crash-in-florida-that-killed-9
  - https://www.nbcmiami.com/news/local/officials-respond-to-fiery-aircraft-incident-in-palm-beach-county/3881532/
  - https://www.foxnews.com/us/timeline-learjet-crash-killed-austin-family-traces-final-minutes-takeoff-florida-plunge
  - https://www.yahoo.com/news/us/article/learjet-plane-crash-in-florida-kills-all-9-on-board-what-we-know-111242550.html
  - https://milesobrien.substack.com/p/five-minutes-that-might-have-made
  - https://cbsaustin.com/news/local/former-fighter-pilot-breaks-down-ntsb-updates-in-deadly-learjet-crash
  - https://mesonet.agron.iastate.edu/cgi-bin/afos/retrieve.py?pil=SIGE&sdate=2026-11-01&edate=2026-11-02&fmt=text&limit=50
  - https://www.faa.gov/air_traffic/publications/atpubs/aim_html/chap7_section_1.html
  - https://www.faa.gov/air_traffic/publications/atpubs/aim_html/chap4_section_4.html
  - https://www.ecfr.gov/api/versioner/v1/full/2026-11-01/title-14.xml?part=91&section=91.3
  - https://www.ecfr.gov/api/versioner/v1/full/2026-11-01/title-14.xml?part=91&section=91.123
verified: 2026-11-12
---

## Summary

The investigation is open and the NTSB has not determined a cause. Times are Eastern Standard Time, which began
that morning. A 22-year-old Learjet 60, registration N722BD (reported by PilotinQ and by Miles O'Brien's embedded
Flightradar24 post; the NTSB page names the type and operator, not the registration), left Austin-Bergstrom at about
10:37 for North Eleuthera with two crew and seven passengers. It reached about 41,000 ft near 11:00. Convective
SIGMETs covered the Florida peninsula from before departure; 45E, valid 1655Z to 1855Z, put Palm Beach County inside
an area of thunderstorms moving little with tops above FL450. Yahoo's roundup reports that the FAA issued a weather
warning before departure.

Fox News's timeline, from ATC audio and tracking, and O'Brien's account agree on the sequence. About 12:31 Miami
Center reported precipitation ahead and offered left or right. The crew asked for a direct routing (O'Brien: toward
Freeport); the controller approved it and warned of moderate to extreme precipitation, saying in O'Brien's quotation
"The turn to Freeport looks pretty bad". About 12:35 the crew turned toward a southwest Florida waypoint first. About
12:36 the controller instructed a descent to 35,000 ft; no reason has been published. About 12:40 deviations left or
right were approved, direct Freeport when able, and the jet headed north toward Palm Beach County.

The NTSB's timeline (Chapman, 2 November): about 12:47 the crew reported light clear ice they considered
manageable, moderate turbulence with altitude deviations of about 700 ft, and minus 47 C. They reported
precipitation and asked to climb to 37,000 ft, and ATC approved. Less than 30 seconds later a transmission announced
the descent, followed by a mayday; about 12:48 the crew reported "an overspeed condition, descending". Fox reports
the jet reached about 35,450 ft before descending. AP reports a descent rate of 10,000 ft per minute that reached
30,000 and a sharp bank to the right. The jet struck the ground beside Military Trail between Cresthaven Boulevard
and 10th Avenue North, at about 12:51 by the NTSB's briefing (12:49 to 12:50 in other reports). All nine aboard were
killed; a man in a vehicle nearby was injured, and about 600 residents were displaced.

## Defensive position

No party has defended or criticized the crew in a finding, and the NTSB has found fault with no one. What is on
record that bears in the crew's and controller's favour:

- **NTSB (Chapman):** weather is "a major focus"; investigators have not determined conditions at 35,000 ft or
  whether the jet was in an active thunderstorm; of the elevator, "At the speed the aircraft was traveling, I'm not
  sure it would have been effective."
- **John Cox** (to AP): the pilots steered around a larger storm cell, and the smaller one they entered developed
  rapidly.
- **AccuWeather's Dan DePodwin** (via Yahoo): aircraft weather radars have limitations and may not detect the
  updrafts that intensify precipitation.
- **Alan Diehl**, former NTSB investigator (to Fox News Digital): once control was lost the pilots likely had little
  ability to recover.
- **Miles O'Brien** frames each step, the shortcut, accepting the descent and continuing, as individually defensible.

## Adversarial position

No investigator has made a case against anyone. Critics on record:

- **John Cox** (AP): "If I'm looking at thunderstorms, I'd rather be at 41 than at 35", and "I don't understand why
  they came down." AP adds that it is unclear why the pilots did not fly around the storms.
- **Miles O'Brien**, with a veteran pilot he leaves unnamed: the filed plan was a longer southern route that, he writes, kept them away from the worst
  convection; the direct request, the descent "into the clouds below" and continuing add up to plan-continuation
  bias; a wider route might have cost five to ten minutes. He states he does not establish cause.
- **Matthew "Whiz" Buckley** (CBS Austin), of the aircraft rather than the crew: Learjet "did not design that wing for
  even a little bit of ice buildup", and it is "not gonna take a lot to snap a horizontal stab off a Learjet".

## Outcome

Open. The NTSB (ERA27MA026, FAA supporting) has said weather is a major focus, that the left elevator separated
before impact, and that it has not determined whether that separation contributed to the loss or resulted from the
descent. It recovered the cockpit voice recorder on 9 November and completed excavation; its case page lists no
findings. No cause has been determined. A preliminary report is expected about 30 days after the crash (AP).

## Analysis

**Read with care: a crew is not a stack.** The overlay's vehicle is a Byzantine stack behind a trusted governor
(ADR-0062 §1); a cockpit has two people who are both, and the recovery function, a trust root in TOPAK (T-0068-9),
is the same people. Every TOPAK claim below is about the structure of the authority, not about this crew, and no
cause is implied.

**Every grant was checked against the grantor's rules.** Read Miami Center as the commanded plane and each clearance
as an intent ordered by one person (ADR-0060 §2, Intent's `Order`). `IntentNarrows` checks an intent against the
promoted seating, which here is the controller's airspace and traffic. The climb to FL370 passes that check whatever
the jet's margin is. In TOPAK the same gap is structural: the governor lifts "elapsed time, position, the lease's
count, an entry's extent" (ADR-0062 §1), and a vehicle's aerodynamic margin, narrowing with altitude and ice, is no
lifted fact. This extends SF-8: there the envelope could not see the size of an act; here it cannot see the state of
the actor. A-0068-8 ("every entry's extent is declared as what it is") is the nearest assumption.
`proposed:VehicleEnvelope` would lift a margin the vehicle measures as a governor fact and let a bundle refuse on it, deny-only
as ADR-0007 requires and ADR-0065 §1's measured-fact row already allows (`NarrowsInReceived`). Its mutation reads the
grantor's approval as sufficient. It could refuse a climb; it could not descend an aircraft.

**Declining a level is a deny; objecting to losing one is not expressible.** The descent at 12:36 was an
instruction, binding except in an emergency (14 CFR 91.123(b)). It has two halves. It offers FL350, and declining an
offered grant is a local deny that TOPAK already has: nothing obliges a principal to use a permission, and a deny
needs no quorum and no peer (ADR-0050 §4, `DenyAlwaysAvailable`). It also withdraws FL410, and in TOPAK that half
bites at once: "a subtraction applies on receipt, before it is ordered anywhere" (ADR-0065 §1), and a lease ends
"when the plane ends or revokes it" (ADR-0062 §7). The child has no interval in which to object before it does.
Aviation does not let the pilot keep FL410 by saying so either: "unable" is a request for an amended clearance (AIM
4-4-1), answered by the controller's re-plan, and only in an emergency does the pilot deviate and report afterwards
(91.3(b), 91.123(c)). The other gap is the instruction itself. A lease permits and nothing obliges a principal to
act, so ADR-0059 §3's narrowings can withdraw FL410 and none can move a body anywhere; `outside:instruction-to-act`
stands behind the 12:36 `Order`. For a body in motion, refusing a descent is staying put, an act inside someone
else's separation plan. That is SF-1 seen from the other side, and FINDINGS_TOPAK.md SF-23 develops it.

**Monitors that report a proxy.** Radar "will normally reflect the areas of moderate to heavy precipitation (radar
does not detect turbulence)" (AIM 7-1-26). The SIGMET and the controller's warnings were advisories by design: the
AIM tells pilots not to assume ATC will offer deviations, and leaves the decision with the PIC. These are SF-5's
fifth shape, findings live and wired to nothing, except that here the wiring to nothing is the rule's intent. TOPAK
would put the same facts in the same place: under ADR-0065 §5 nothing may rest on a report being read. TM9 is
deception of perception; nobody deceived anyone here, and a proxy that under-reports is TM9's shape without an
adversary.

**What happened after the upset is not expressible, and should not be.** The descent, the elevator's separation and
the impact are `outside:` steps because they are physics, and whether the elevator failed first or in the dive is
exactly what the investigation has not settled. `TerminalNeverWaits` (Alone) and A-0068-4 (a safe state reached in
bounded time) are where TOPAK would locate a recovery, and the companion entry tests that.

**Where the pattern stops.** Ice, cell growth, coffin-corner margins, flutter and structural load are in no module
(Alone's header: "Reaching a safe state is physics, and is not here"). TOPAK claims nothing about this loss. What it
shows is two questions the overlay leaves open: a grant checked only against the grantor's rules, and a parent whose
only lever is a permission while the aviation rule gives it instructions. CR-17 holds here as everywhere: every
control ends in a present, trained person.

**Outside steps.** `departure-under-convective-sigmet`, `controller-weather-advisory`, `crew-revises-route`,
`cell-develops-at-cruise-level`, `crew-reports-ice-and-turbulence`, `upset-during-climb`,
`altitude-at-pilot-discretion`, `in-flight-separation-of-left-elevator`, `impact`, and in prose
`instruction-to-act`.
