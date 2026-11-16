---
id: 2009-AVI-AIR-FRANCE-447
title: Air France 447 — iced Pitot probes, an autopilot that handed back control without saying why, and a stall the crew never identified
kind: incident
date: 2009-06-01
sector: aviation
setting: Airbus A330-203 F-GZCP, Air France flight AF 447 Rio de Janeiro to Paris, at FL350 over the Atlantic near the TASIL point
concerns: [human-in-the-loop, sensing, authority, monitoring, emergency-path, interlock, feedback]
rules_at_time:
  - document: Air France procedure "Vol avec IAS douteuse" (unreliable airspeed), as the BEA describes it
    clause: loss of airspeed information
    paraphrase: after initial airmanship reactions, the crew is expected to diagnose the loss and hold precautionary pitch attitude and thrust
  - document: Airbus A330 flight control laws and stall warning design, as the BEA describes them
    clause: alternate law; stall warning validity
    paraphrase: on detecting inconsistent airspeeds the flight controls reconfigure to alternate law, with no angle-of-attack protection; measured angle of attack is invalidated below 60 kt of measured speed, and the stall warning stops when it is invalid
  - document: Certification safety model, as the BEA describes it
    clause: classification of total loss of airspeed information
    paraphrase: the failure was classified as major on the assumption that crews would rapidly diagnose it and apply the procedure
analogue:
  - record: ADR-0062
    clause: "§7"
    note: an ending grants nothing; the terminal behaviour is voted with the seating, the stack does not choose it, and reaching a safe state in bounded time is an obligation on the builder
  - record: ADR-0052
    clause: "§1, §4"
    note: an emergency seat is held by a person and is not coupled to an Observer (provisional)
  - record: ADR-0039
    clause: "title; §1"
    note: Observer liveness is progress, not presence; a silent monitor is not a clean one
  - record: ADR-0047
    clause: Decision
    note: the Listener labels every item it delivers, so what the reader receives says what it was derived from
actors:
  - party: Pitot probes (model C16195AA)
    role: sensor
    fault: byzantine
    note: likely obstructed by ice crystals; airspeeds inconsistent for up to about a minute
  - party: Autopilot, autothrust and flight control computers
    role: automation
    fault: none-alleged
    note: detected the inconsistency, disconnected, and reconfigured to alternate 2B as designed; no ECAM message clearly said why
  - party: Stall warning
    role: monitor
    fault: contested
    note: sounded continuously for 54 seconds; stopped by design whenever angle of attack was invalid
  - party: Flight crew (two copilots, then the Captain)
    role: operator
    fault: contested
    note: the BEA found inappropriate inputs and no diagnosis of the stall, and explained them by training, ergonomics, startle and the safety model
  - party: Air France, Airbus, EASA
    role: vendor
    fault: contested
    note: probe replacement had begun on 30 May 2009; EASA had decided not to make it mandatory
  - party: ATLANTICO and DAKAR Oceanic control
    role: monitor
    fault: omission
    note: the flight was not transferred; with ADS-C connected the loss of altitude would have alerted a controller
  - party: BEA
    role: investigator
    fault: none-alleged
detection:
  means: [alarm, investigation]
  latency: seconds
trace:
  - step: outside:pitot-obstruction
    at: 2 h 10 min 05 UTC
    note: likely ice crystals at the upper limit of a slightly turbulent cloud layer; the Captain was resting
  - step: Finding
    at: 2 h 10 min 05
    note: Observers.tla's finding, read as the systems' own detection of inconsistent airspeeds; it subtracts
  - step: EndLease
    at: 2 h 10 min 05
    note: Alone.tla's ending; autopilot then autothrust disconnect and the law becomes alternate 2B, which grants the automation nothing and leaves the flight path to the copilots
  - step: outside:hand-back-without-reason
    at: same
    note: no ECAM message clearly indicated that the system had detected an airspeed inconsistency; the crew learned of an anomaly from the autopilot disconnection warning
  - step: outside:guidance-after-withdrawal
    at: following minute
    note: the flight directors did not disconnect; their crossbars disappeared and reappeared, changing mode several times
  - step: outside:destabilising-manual-inputs
    at: within one minute
    note: excessive roll inputs and a sharp nose-up input; the aeroplane left its flight envelope in less than a minute
  - step: outside:stall-warning-unheeded
    at: after the envelope exit began
    note: it sounded continuously for 54 seconds; neither pilot referred to it; TO/GA thrust and a nose-up input followed it
  - step: outside:monitor-invalidated-at-extreme
    at: during the stall
    note: below 60 kt measured speed angle of attack is invalidated and the warning stops, by design
  - step: outside:captain-returns
    at: about 1 min 30 after 2 h 10 min 05
    note: about 1 min 30 after the disconnection, with the aeroplane already stalled
  - step: outside:impact
    at: 2 h 14 min 28
    note: pitch 16.2 degrees nose-up, vertical speed -10,912 ft/min; 228 on board
  - step: outside:ground-monitor-lapse
    at: until 8 h 22
    note: no transfer between the Brazilian and Senegalese centres; the first alert messages came from Madrid and Brest between 8 h 22 and 9 h 09
counterfactual:
  by: the crew, under the procedure the BEA found was not called, read in TOPAK's terms
  trace:
    - step: Finding
      at: 2 h 10 min 05
      note: the systems detect the inconsistency
    - step: EndLease
      at: 2 h 10 min 05
      note: the automation withdraws
    - step: outside:reason-annunciated
      at: same
      note: the BEA's call for a clear cockpit display of the inconsistencies the computers identified
    - step: outside:fixed-pitch-and-thrust-held
      at: the next minute
      note: the procedure's precautionary pitch attitude and thrust, held until the speeds return (left PFD wrong for 29 s, ISIS 54 s, right PFD at most 61 s)
  holds: [TerminalNeverWaits]
outcome:
  by: Bureau d'Enquêtes et d'Analyses pour la sécurité de l'aviation civile (BEA)
  date: 2012-07-05
  summary: >-
    The BEA found the accident resulted from a temporary inconsistency between measured airspeeds, likely from ice
    crystals obstructing the Pitot probes, which led to autopilot disconnection and alternate law; inappropriate
    control inputs that destabilised the flight path; the crew not linking the loss of indicated speeds to the
    procedure; the late identification and insufficient correction of the flight path deviation; the crew not
    identifying the approach to stall and leaving the flight envelope; and the failure to diagnose the stall. It
    explained these by feedback mechanisms that never surfaced repeated non-application of the procedure, no
    high-altitude manual handling training, task-sharing weakened by startle and incomprehension, no clear display of
    the airspeed inconsistencies, and the crew not taking the stall warning into account.
  aftermath: >-
    The BEA issued 41 safety recommendations to the DGAC, EASA, the FAA, ICAO and the Brazilian and Senegalese
    authorities, on flight recorders, certification, initial and recurrent pilot training, relief of the Captain,
    search and rescue, ATC, simulators, cockpit ergonomics, operational feedback and operator oversight. Airbus and
    Air France had begun replacing the C16195AA probes with the C16195BA model on 30 May 2009.
  effect_reversed: "no"
model:
  modules: [Alone, Observers, Coupling, proposed:HandBack]
  properties: [TerminalNeverWaits, ExpiryGrantsNothing, DenyByAnyOf, NoAdmitWithoutLiveObserver]
  mutations: [M_STACKGATED]
  records: [ADR-0062, ADR-0052, ADR-0039, ADR-0047, ADR-0065, ADR-0045, ADR-0066]
  findings: [CR-2, CR-17, TM9]
  fault_class: a sensor failure the automation answered correctly by withdrawing, with the recovery left to a person whose diagnosis the safety model assumed
sources:
  - https://www.faa.gov/sites/faa.gov/files/f-cp090601.en_.pdf
  - https://bea.aero:443/fileadmin/uploads/tx_elyextendttnews/presentation.rapport.final.05juillet2012.en_04.pdf
verified: 2026-11-12
---

## Summary

AF 447 left Rio de Janeiro on 31 May 2009 for Paris with 216 passengers and 12 crew. At about 2 h 02 UTC the
Captain left the cockpit for his rest, leaving no specific instructions for crossing the inter-tropical convergence
zone, with two copilots at the controls. At about 2 h 08 the crew turned 12 degrees left to avoid weather returns.

At 2 h 10 min 05, likely after ice crystals obstructed the Pitot probes, the measured airspeeds became inconsistent.
The autopilot, then the autothrust, disconnected, and the flight control law reconfigured to alternate 2B. No ECAM
message clearly indicated that the systems had detected an airspeed inconsistency; the pilots learned of an anomaly
from the autopilot disconnection warning. They called out the loss of speed indications and did not call the
unreliable-airspeed procedure. The flight directors stayed on, their crossbars disappearing and reappearing.

Excessive roll inputs and a sharp nose-up input followed, and in less than a minute the aeroplane left its flight
envelope. The stall warning sounded continuously for 54 seconds; neither pilot referred to it. Shortly after it
triggered, the pilot flying selected TO/GA thrust and made a nose-up input. The displayed speeds were wrong for 29
seconds on the left PFD, 54 on the standby instrument and at most 61 on the right PFD. The Captain returned about 1
min 30 after the disconnection, with the aeroplane already stalled. The stall lasted until impact with the sea at 2 h
14 min 28. All 228 on board died. The flight had not been transferred to Dakar, and the first alerts were sent
between 8 h 22 and 9 h 09; the recorders were recovered 23 months later.

## Defensive position

No party's own statement was read for this entry; the case for the design and its certification is the one the
BEA records.

- **The safety model.** Loss of airspeed information was a known, classified failure. After initial airmanship
  reactions, the crew was expected to diagnose it rapidly and hold pitch and thrust, as the procedure said.
- **The aeroplane did what it was told.** Throughout the flight the control surfaces followed the pilots' inputs, and
  until the envelope exit the aeroplane followed its surfaces. The engines responded normally.
- **The probes.** Those fitted met requirements stricter than certification; Airbus and Air France had started
  replacing them, the first aircraft on 30 May 2009; EASA had analysed probe icing events and decided not to make the
  change mandatory.

## Adversarial position

**The BEA** found the safety model's behavioural hypotheses "not validated in the context of this accident":

- The crew "likely never understood" it faced a "simple" loss of three airspeed sources; no clear display told it so.
- The stall warning lacked "legitimacy" for a crew with little exposure to stalls; it had no visual confirmation
  once the limit speeds disappeared; buffet was taught as a symptom of overspeed too; the flight directors may have
  suggested the inputs were right; and alternate law with no angle-of-attack protection was hard to recognise.
- When the assumed initial control and diagnosis are lost, "the safety model is then in 'common failure mode'".
- Feedback across the industry had not surfaced repeated non-application of the procedure, and the copilots had no
  high-altitude training in manual handling or in the procedure.

## Outcome

The BEA presented its final report on 5 July 2012, the English text a translation of the French reference. It set
out the six-step chain and its associated factors, and addressed 41 safety recommendations to six authorities and
bodies. Nothing was reversed.

## Analysis

**The automation subtracted, as TOPAK would have it.** Faced with inconsistent inputs, the systems withdrew their own
authority: autopilot, autothrust, the normal law's protections. In the corpus's vocabulary that is a finding that
subtracts (ADR-0007, Observers.tla's `Finding`) and a lease that ends and grants nothing (Alone.tla's `EndLease`,
`ExpiryGrantsNothing`). By ADR-0045 §2's test it was the safe direction. AF 447 shows the limit of that direction
in flight, which ADR-0062 §7 already concedes: "A stall that never ends is safe" is false of a vehicle in flight, and
a subtraction hands the problem to whoever is next.

**What ADR-0062 §7 asks, and the A330 did not have.** §7 makes the terminal behaviour part of the seating, voted with
it, not chosen by the stack, carried out by a recovery function, and reaching a safe state in bounded time. The
A330's terminal behaviour after disconnection was "the crew flies", which is not a fixed act but a diagnosis. The
procedure's fixed pitch and thrust is the nearest thing to a voted terminal act, and the counterfactual is that act
held. `TerminalNeverWaits` (Alone.tla) says the terminal behaviour is enabled whatever the stack does; under
`M_STACKGATED` it waits on the stack and fails. AF 447 is that mutation's shape with a person in the stack's place:
the safe behaviour waited on a diagnosis by the people the failure had just surprised. The BEA's "common failure
mode" of the safety model is the same observation in its own words.

**The hand-back carried no reason.** The computers knew why they had withdrawn and the cockpit did not say so clearly.
Operators.tla's `EveryStopIsAttributed` records who stopped, not why; ADR-0047 labels every item with what it was
derived from, and ADR-0065 §3 delivers a report as labelled ingress. A flight director drawing bars from the same
suspect data after the autopilot had withdrawn is an unlabelled item in that sense. `outside:hand-back-without-reason`
and `outside:guidance-after-withdrawal` are on the to-do list: a hand-back record should carry the finding that caused
it, and guidance derived from an input under a finding should be labelled or withdrawn with it.
`proposed:HandBack` would model an automation that withdraws on a finding, a person seated in its place, and the
record handed across, with a mutation that drops the finding from the record.

**A monitor that went quiet at the worst moment.** By design the stall warning stopped whenever angle of attack was
invalid, which happens below 60 kt of measured speed, deep in the stall. CR-2's "a dead Observer looks like a clean
system" and ADR-0039's "progress, not presence" are about exactly this: silence read as safety.
`NoAdmitWithoutLiveObserver` couples admits to a live Observer in the corpus; nothing couples a person's reading of
the cockpit to whether the warning is valid. The ground side has the same shape: the flight was never transferred and
the first alert went out some six hours after impact.

**Where the pattern stops.** The person in the seat is the corpus's last resort everywhere (ADR-0052's emergency seat,
ADR-0066's release seat), and CR-17 notes that every such path presumes a present, trained human. TM9 names a
deceived person as a semantic failure "nothing here sees". AF 447 is that row in a cockpit. TOPAK would not have
recovered the aeroplane; it would have asked, before service, what the terminal act is and who carries it out.
