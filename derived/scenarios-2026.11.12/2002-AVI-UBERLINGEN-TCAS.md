---
id: 2002-AVI-UBERLINGEN-TCAS
title: Überlingen mid-air collision — a TCAS resolution advisory and a controller's instruction in conflict, one crew following each
kind: incident
date: 2002-07-01
sector: aviation
setting: a Tupolev TU154M (Moscow to Barcelona) and a Boeing B757-200 freighter (Bergamo to Brussels) under ACC Zurich (Skyguide) over German territory north of Überlingen, Lake Constance
concerns: [authority, interlock, monitoring, human-in-the-loop, consensus, configuration-change, timing]
rules_at_time:
  - document: ICAO Annex 10, Attachment A, 3.5.8.10.3
    clause: contrary pilot response
    paraphrase: manoeuvres opposite to the sense of an RA may reduce vertical separation and must be avoided, particularly in a coordinated ACAS-to-ACAS encounter
  - document: ICAO PANS-OPS, Chapter 3, 3.1.2 (as the BFU quotes it)
    clause: operation of ACAS
    paraphrase: nothing in the ACAS procedures prevents pilots-in-command from using their best judgement and full authority in choosing how to resolve a conflict
  - document: ICAO Doc 4444 PANS-ATM
    clause: ACAS-equipped aircraft
    paraphrase: the procedures for ACAS-equipped aircraft are identical to those for others, including the prevention of collisions and the establishment of separation
  - document: TU154M flight operations manual, as the BFU quotes it
    clause: avoidance of in-flight collisions
    paraphrase: visual control and the correct execution of ATC instructions are the most important tool; TCAS is an additional instrument; the BFU read the wording as giving ATC the highest priority, while the same manual's TCAS section prohibited a manoeuvre contrary to an advisory
analogue:
  - record: ADR-0065
    clause: "§1, §5, §6"
    note: nothing a peer originates enables anything; a governor's measured facts may refuse and never permit; nothing rests on a report being read; agreement is an ordered entry
  - record: ADR-0054
    clause: title and Decision
    note: an orchestrator cell may only choose among edges the mechanism has already enabled (Proposed)
  - record: ADR-0030
    clause: "§1"
    note: admit is floor permit and not bundle deny; any refusal wins and no permit overrides one
  - record: ADR-0039
    clause: "§2"
    note: an admit needs a live Observer, so a monitor that is down stalls the work it watches
actors:
  - party: ACC Zurich controller (Skyguide)
    role: controller
    fault: contested
    note: alone at two workstations; instructed the TU154M to descend 43 seconds before the collision, too late for separation (BFU)
  - party: Skyguide management and quality assurance
    role: supervisor
    fault: contested
    note: the BFU found it tolerated for years one controller working alone at night, and did not assess the night's maintenance work
  - party: TU154M crew (Bashkirian Airlines)
    role: operator
    fault: contested
    note: followed the ATC instruction against a climb RA; the Russian Federation's comments disputed the BFU's account
  - party: B757-200 crew (DHL)
    role: operator
    fault: honest
    note: followed the descend RA and reported it 23 seconds later at the first opportunity
  - party: TCAS II version 7 in both aircraft
    role: safety-system
    fault: none-alleged
    note: issued simultaneous, coordinated, complementary RAs; no malfunction was found
  - party: ACC Zurich optical STCA and telephone system
    role: monitor
    fault: omission
    note: radar in fallback mode for sectorisation work, optical STCA off with no indication of it; direct lines down and the bypass defective
  - party: UAC Karlsruhe controller
    role: peer
    fault: honest
    note: his STCA alerted at 21:33:24; his calls to Zurich could not be connected
detection:
  means: [alarm, peer, investigation]
  latency: seconds
trace:
  - step: outside:monitor-off-unannounced
    at: night of 1 July 2002, from about 21:15
    note: sectorisation work put the radar in fallback mode; separation raised to 7 NM; optical STCA unavailable, and the controller did not know; one controller resting
  - step: Drop
    at: 21:33:24 to 21:35
    note: Peer.tla's dropped item, read as UAC Karlsruhe's STCA warning; its controller's calls could not get through
  - step: outside:late-instruction
    at: "21:34:49"
    note: '"descend flight level 350, expedite, I have crossing traffic"; 43 seconds before the collision'
  - step: ReceiveMeasured
    at: "21:34:56"
    note: Peer.tla's measured fact from another governor, read as the TCAS coordination; RAs in both aircraft, climb for the TU154M and descend for the B757-200
  - step: outside:order-overrides-advisory
    at: 21:34:59 to 21:35:05
    note: the TU154M copilot said TCAS said climb; the commander replied that ATC was guiding them down; descent continued
  - step: outside:second-instruction-with-wrong-bearing
    at: "21:35:03"
    note: a second expedite-descent instruction, and traffic reported at 2 o'clock; the copilot answered it was on the left
  - step: outside:own-alarm-unheard
    at: "21:35:00"
    note: Zurich's aural STCA warning sounded at the workstation and was not noticed in the control room
  - step: Deliver
    at: "21:35:19"
    note: Peer.tla's delivery, read as the B757-200's "TCAS descent" call; partly simultaneous with another transmission, and not noticed
  - step: outside:collision
    at: "21:35:32"
    note: at 34,890 ft, crossing at right angles, closure about 702 to 718 kt; 71 on board both aircraft, none survived
counterfactual:
  by: the TU154M crew, under the rule ICAO adopted afterwards that the RA prevails over a contrary ATC instruction
  trace:
    - step: ReceiveMeasured
      at: "21:34:56"
      note: the coordinated RA
    - step: Refuse
      at: "21:34:56"
      note: Peer.tla's refusal on a measured fact, read as the RA refusing the instructed descent; no permit overrides it
    - step: outside:advisory-selects-among-enabled-manoeuvres
      at: next seconds
      note: the climb is an avoidance manoeuvre already in every flight's envelope, chosen, not granted, by the advisory
  holds: [NarrowsInReceived, PeerAddsNothing]
outcome:
  by: German Federal Bureau of Aircraft Accidents Investigation (BFU), report AX001-1-2/02
  date: 2004-05
  summary: >-
    The BFU found two immediate causes: ATC did not notice the imminent separation infringement in time and instructed
    the descent when separation could no longer be ensured; and the TU154M crew followed the instruction and
    continued to descend after TCAS advised a climb. Its systemic causes were that ACAS/TCAS was insufficiently
    integrated into aviation, with ICAO, national, manufacturer and operator rules "not standardised, incomplete and
    partially contradictory"; that Skyguide's management and quality assurance did not ensure all open workstations
    were staffed at night; and that they tolerated for years one controller working while the other rested.
  aftermath: >-
    The BFU recommended to ICAO on 1 October 2002 that pilots be required to follow RAs regardless of contrary ATC
    instructions; Wikipedia reports ICAO amended its rules in November 2003, and that TCAS II was later changed to
    reverse an RA when one aircraft does not comply. The BFU made further recommendations to the Swiss FOCA on
    maintenance procedures and minimum staffing. Wikipedia reports that a Konstanz court held Germany liable in 2006,
    and that in September 2007 a Swiss court convicted four Skyguide managers, three with suspended sentences.
  effect_reversed: "no"
model:
  modules: [Peer, Coupling, FloorComposition, proposed:Precedence]
  properties: [NarrowsInReceived, PeerAddsNothing, BundleRefusalHonored, NoAdmitWithoutLiveObserver]
  mutations: [M_OVERRIDE, M_NOCOUPLE]
  records: [ADR-0065, ADR-0054, ADR-0030, ADR-0039, ADR-0038, ADR-0059, ADR-0050]
  findings: [CR-2, CR-17, TM2, TM13]
  fault_class: two authorities issuing contradictory orders with no settled precedence, one party following each; a ground monitor down without notice
sources:
  - https://skybrary.aero/sites/default/files/bookshelf/414.pdf
  - https://en.wikipedia.org/wiki/2002_%C3%9Cberlingen_mid-air_collision
verified: 2026-11-12
---

## Summary

On the night of 1 July 2002 both aircraft were at FL360 under ACC Zurich, converging at right angles over southern
Germany. ACC Zurich was re-sectorising that night: the radar ran in fallback mode, separation was raised from 5 to 7
NM, and the optical short-term conflict alert (STCA) was unavailable, which the system did not indicate. Direct
telephone lines to adjacent units were down from 21:23 to 21:34:37, and the bypass system had a defect. At about
21:15 one of the two controllers on duty went to rest, as management had tolerated for years. The remaining
controller worked two workstations on two frequencies, and in the last five minutes attended mostly to a delayed
A320 approaching Friedrichshafen.

At 21:33:24 UAC Karlsruhe's STCA showed the conflict; its controller could not get through by phone. At 21:34:42
TCAS in both aircraft gave traffic advisories. At 21:34:49 Zurich told the TU154M to "descend flight level 350,
expedite, I have crossing traffic". At 21:34:56, as its crew began to descend, TCAS issued coordinated resolution
advisories: climb for the TU154M, descend for the B757-200. The TU154M copilot said TCAS said climb; the commander
answered that ATC was guiding them down. At 21:35:03 Zurich repeated the instruction and placed the traffic at 2
o'clock; it was on the left. The B757-200, its copilot briefly away from his seat, descended on the RA and reported
"TCAS descent" at 21:35:19; the controller did not register it. Zurich's own aural STCA sounded at 21:35:00 and
was not noticed. At 21:35:24 the TU154M's TCAS called "increase climb". The aircraft collided at 21:35:32 at 34,890
ft. All 71 people on board the two aircraft died.

## Defensive position

**The TU154M's procedures**, as the BFU quotes them, made visual control and "the correct execution of all
instructions issued by ATC" the most important collision-avoidance tool and TCAS "an additional instrument".
PANS-OPS 3.1.2 left pilots-in-command their "best judgement and full authority" in resolving a conflict.

**The Russian Federation**, in comments Wikipedia summarises, said the crew could not follow the climb advisory
when it came, that the controller had misplaced the conflicting traffic, and that the B757 crew had a "real
possibility" to avoid the collision.

**The controller** was qualified and licensed; the BFU found the conflict visible only on the radar display, the
STCA off without his knowledge, the phones down, and the two aircraft and the A320 on frequencies that could not
hear each other.

## Adversarial position

**The BFU** set out the case against both the rules and their operators:

- The RA "has the highest priority" because it is issued only when other means of separation are not effective;
  coordinating with the controller after an RA would "question the purpose of TCAS". ICAO Annex 10 already said
  opposite manoeuvres "must be avoided".
- The regulations were "not standardised, incomplete and partially contradictory", and the TU154M manual's wording
  gave ATC the highest priority. Simulator training on TCAS was not possible for the TU154M crew.
- The copilot questioned the descent twice and "could not gain anybodies ear"; no one said TCAS had priority.
- Skyguide's management did not assess the maintenance work's effect on equipment, and tolerated a single controller
  at night.

**Skyguide** first blamed the Russian crew and later accepted full responsibility, Wikipedia reports.

## Outcome

The BFU published report AX001-1-2/02 in May 2004 with two immediate and three systemic causes, and recommended to
ICAO, before the report, that RAs be followed regardless of ATC. ICAO amended its rules in November 2003. The 71
deaths were not reversible; courts later assigned liability and criminal responsibility.

## Analysis

**Two authorities, two orders, no precedence: the f1-tla model entry's F-18.** That entry's point was that two race
control messages could stand in one Safety Car period "with no rule of precedence". Überlingen is the same shape with
a body count: the controller's descend and the RA's climb stood together, the rules on record pointed both ways, and
one crew followed each. `proposed:Precedence` would make a property of what the BFU asked for: in every state where
an advisory and an instruction conflict, the action taken is the advisory's, with a mutation (instruction wins) that
breaks it.

**TOPAK's composition already has a precedence, and it is the right one here.** ADR-0030 §1 composes authority as a
conjunction of permits under any refusal: no permit overrides a refusal. `BundleRefusalHonored` holds, and `M_OVERRIDE`
(an allow that grants on its own) is the mutation that breaks it. Read the RA as a refusal of the opposite sense, and
the TU154M's continued descent is an admit under `M_OVERRIDE`. ADR-0065 §1's table puts TCAS where it belongs: a
governor's measured facts about another vehicle "may refuse on them and never permits on them". `NarrowsInReceived`
says receipt only narrows. The ICAO rule adopted afterwards is that sentence.

**What the peer rule forbids, and where it needs ADR-0054.** Under ADR-0065 a peer's coordination cannot *enable* the
B757's descent or the TU154M's climb. The corpus's way out is ADR-0054's: an orchestrator may only choose among edges
the mechanism has already enabled. An avoidance manoeuvre in every flight's envelope, which the RA selects but does
not grant, is that shape. `outside:advisory-selects-among-enabled-manoeuvres` is on the to-do list because no module
has a selection made by a peer exchange. And a coordinated RA is safe only if both crews follow their halves; when one
does not, the pair is worse off than with no advisory. ADR-0065 §6 says agreement is an ordered entry; TCAS's
agreement is talk, and the later reversal logic, which Wikipedia reports, is a protocol repairing a defecting peer.

**The ground monitor was off and looked on.** The optical STCA was unavailable with no automatic indication of it, the
calls from Karlsruhe could not connect, and the aural STCA was not heard. CR-2's dead Observer that looks like a clean
system, three times over. ADR-0039 §2 would stall the work rather than let it run unwatched (`NoAdmitWithoutLiveObserver`;
`M_NOCOUPLE` is the night's configuration). ADR-0065 §5, "nothing may rest on a report being read", is borne out by
the B757's call: it was made correctly and changed nothing, and the RA downlink to ATC did not yet exist.

**Where the pattern stops.** TOPAK decides admits for principals under one chain of authority (ADR-0059's tree of
planes). Here the controller, two crews and two TCAS units were five deciders with no common record, and the RAs
were issued 35 seconds before impact. TM2 (the link adversary) and TM13 (a peer that lies) are the corpus's nearest
rows; neither covers an honest peer whose advice is ignored. CR-17 again: the rule works only if the person at the
controls has been trained to let the refusal win.
