---
id: 1979-ICS-THREE-MILE-ISLAND
title: Three Mile Island Unit 2, 28 March 1979 — a relief-valve light that showed the command, not the valve
kind: incident
date: 1979-03-28
sector: industrial-control
setting: Three Mile Island Unit 2 pressurized-water reactor (Babcock & Wilcox design), operated by Metropolitan Edison for GPU, Middletown, Pennsylvania
concerns: [sensing, monitoring, actuation, human-in-the-loop, feedback, accountability]
rules_at_time:
  - document: NRC quality assurance requirements, as applied by Metropolitan Edison (Kemeny Commission findings)
    clause: scope of "safety-related" equipment
    paraphrase: Met Ed's QA plan met NRC requirements but covered only equipment classed safety-related; the PORV and the condensate polishers were outside it
  - document: TMI-2 emergency procedure for a loss-of-coolant accident (Kemeny Commission findings)
    clause: LOCA procedure
    paraphrase: Met Ed's misreading of a 1978 B&W analysis was built into the procedure; the Commission called the applicable procedures "at least very confusing"
analogue:
  - record: ADR-0042
    clause: "§3"
    note: every Actuate leaves a record with an outcome of returned, failed or unknown; it records the call and the tool's return, not the state of the world
  - record: ADR-0049
    clause: "§4"
    note: each allowlist field is marked checked or claimed; a tool's result label is claimed. "Valve closed" would be a claimed field
  - record: ADR-0015
    clause: title
    note: effects are boundary crossings, authorized, ordered and auditable; the crossing is what is audited
  - record: ADR-0068
    clause: "TM9"
    note: deception of a person's perception; "a deceived person at a release seat is a semantic failure. Nothing here sees it"
actors:
  - party: Pilot-operated relief valve (PORV) and its control-room indicator
    role: sensor
    fault: byzantine
    note: the valve stuck open; the light showed that the close signal had been sent, and operators read it as the valve's position
  - party: TMI-2 control-room operators
    role: operator
    fault: contested
    note: the Commission called inappropriate operator action the major factor, and said "operator error" did not capture the fundamental causes
  - party: Metropolitan Edison / GPU
    role: operator
    fault: contested
    note: NRC Notice of Violation and maximum fine; Met Ed denied the charges and paid
  - party: Babcock & Wilcox
    role: vendor
    fault: omission
    note: the Commission found it had not told customers of nine earlier stuck-open PORV failures; a senior engineer's warning after Davis-Besse "fell between the cracks"
  - party: Leland Rogers (B&W)
    role: peer
    fault: honest
    note: asked on a 6:00 a.m. call whether the block valve under the PORV had been shut
  - party: President's Commission on the Accident at Three Mile Island (Kemeny)
    role: investigator
    fault: none-alleged
detection:
  means: [peer, operator]
  latency: hours
trace:
  - step: outside:feedwater-trip
    at: 04:00:36
    note: feedwater pumps trip; the turbine trips; the plant was at 97% power
  - step: outside:relief-opens-on-pressure
    at: within 13 s
    note: coolant pressure reaches 2,255 psi and the PORV opens as designed; the reactor scrams at 8 s
  - step: Actuate
    at: about 13 s
    note: the close signal at about 2,205 psi; the valve does not close. In RunCoupling's terms the call is admitted and recorded, and nothing records that the effect failed
  - step: outside:indicator-reports-command-not-effect
    at: 04:00 to 06:22
    note: the light shows that power to the valve has gone off; the valve stays open 2 h 22 min, and about 32,000 gallons escape in the first 100 minutes
  - step: Actuate
    at: about 4.5 min
    note: high-pressure injection cut from about 1,000 to under 100 gpm, consistent with a model in which the valve was shut
  - step: outside:alarm-flood
    at: first minutes
    note: more than 100 alarms, "no system for suppressing the unimportant signals", and no direct indication that coolant was turning to steam
  - step: Actuate
    at: 05:14 and about 05:41
    note: reactor coolant pumps shut down for vibration; forced flow through the core stops
  - step: outside:peer-asks-about-block-valve
    at: about 06:00
    note: B&W's Leland Rogers asks on a conference call whether the block valve has been shut
  - step: Actuate
    at: 06:22
    note: block valve shut; the Commission records Frederick's testimony that it was at a shift supervisor's suggestion
  - step: outside:core-uncovery-and-damage
    at: from about 06:00
    note: cladding failed on about 90% of the fuel rods; HPI restored and kept high from 08:26
counterfactual:
  by: an instrument indicating the valve's actual position, read against the command; at Davis-Besse in 1977 the block valve was shut about 20 minutes after the PORV stuck
  trace:
    - step: Actuate
      at: about 13 s
      note: the same close command
    - step: outside:effect-sensed-independently
      at: seconds after
      note: a second channel reports the valve still open; the command and the effect disagree
    - step: outside:disagreement-raised-as-finding
      at: seconds after
      note: no module has an effect confirmation or a command-effect comparison
    - step: Actuate
      at: minutes, not hours
      note: block valve shut and HPI left on
  holds: []
outcome:
  by: President's Commission on the Accident at Three Mile Island (Kemeny Commission); US Nuclear Regulatory Commission
  date: 1979-10-30
  summary: >-
    The Commission found that the PORV opened as designed and failed to close, creating a small-break LOCA that
    "continued for over 2 hours", and that the control-room light "showed only that the signal had been sent to close
    the PORV rather than the fact that the PORV remained open". It found that operators cut HPI to under 100 gpm and
    called inappropriate operator action the major factor in turning the incident into a serious accident, while
    finding training "greatly deficient", procedures confusing, the control room "seriously deficient under accident
    conditions", and a "lack of attention to the human factor" at the NRC, the utility and its suppliers. It found
    B&W had not passed on nine earlier PORV failures, and that a warning issued 13 months before "if heeded, could
    have prevented the accident". The NRC issued Met Ed a Notice of Violation on 25 October 1979 with the maximum
    fine of $155,000; Met Ed denied the charges and paid.
  aftermath: >-
    INPO was formed in 1979; operator training moved towards a symptom-based approach that first keeps the core
    covered. GPU sued B&W for $500 million in March 1980 and settled out of court on 24 January 1983. Clean-up took
    nearly twelve years; defuelling ran from 1985 to 1990. The Commission estimated releases of 13 to 17 curies of
    iodine and 2.4 to 13 million curies of noble gases.
  effect_reversed: "no"
model:
  modules: [RunCoupling, Labels, Mechanism, proposed:EffectConfirmation]
  properties: [OutsideResultIsUntrusted, NoEffectWithoutLiveObserver, ChannelFidelity]
  mutations: []
  records: [ADR-0042, ADR-0049, ADR-0015, ADR-0051, ADR-0052, ADR-0068]
  findings: [TM9, CR-17]
  fault_class: an actuator that did not do what it was told, and an indicator wired to the command; people acted correctly on a false model of the world
sources:
  - https://pddoc.com/tmi2/kemeny/assessment_of_sinificant_events.htm
  - https://pddoc.com/tmi2/kemeny/wednesday_march_28_1979.htm
  - https://pddoc.com/tmi2/kemeny/causes_of_the_accident.htm
  - https://pddoc.com/tmi2/kemeny/utility_and_its_suppliers.htm
  - https://world-nuclear.org/information-library/safety-and-security/safety-of-plants/three-mile-island-accident
  - https://www.tmia.com/old-website/history/tmilegalhistory.html
verified: 2026-11-12
---

## Summary

At 4:00:36 a.m. on 28 March 1979 the feedwater pumps at TMI-2 tripped, at 97% power. The turbine tripped, coolant
pressure rose to 2,255 psi, and the pilot-operated relief valve (PORV) on the pressurizer opened as designed. The
reactor scrammed eight seconds after the trip. At about 2,205 psi the valve should have closed, and it did not. A
control-room light showed that power to the valve's solenoid had gone off. Operators took it that the valve had
shut. It stayed open for 2 hours and 22 minutes.

High-pressure injection started automatically at about two minutes. About two and a half minutes later an operator
shut one HPI pump and cut the other to under 100 gallons a minute. More than 100 alarms sounded in the first minutes.
The emergency feedwater "twelve-valves" had been left closed after a test on 26 March and were opened at eight
minutes. Reactor coolant pumps were shut down for vibration at 5:14 and about 5:41. On a conference call at about
6:00, Leland Rogers of B&W asked whether the block valve beneath the PORV had been shut; it was shut at 6:22. Water
had been below the top of the core from about 6:15. A site emergency was declared shortly before 7:00 and a general
emergency at 7:24. HPI was kept high from 8:26. A hydrogen burn in containment at 1:50 p.m. registered 28 psi.

## Defensive position

**For the operators**, the Commission itself said that "operator error" does not capture the fundamental causes:

- Training was "greatly deficient" for serious accidents; procedures were "at least very confusing".
- The control room was "seriously deficient under accident conditions", with more than 100 alarms and no
  suppression, and no direct indication that coolant was boiling.
- Warnings from earlier incidents, including Davis-Besse in 1977, had produced no new instructions.

**Met Ed** denied the NRC's charges in its Notice of Violation, while paying the fine. **GPU** sued B&W, the plant's
designer, for $500 million, blaming it for the accident.

## Adversarial position

- **The Commission** called inappropriate operator action "the major factor that turned this incident into a
  serious accident", the cutting of HPI in particular, since falling pressure with steady temperature indicated a
  LOCA.
- **On the vendor:** B&W had not told customers of nine earlier stuck-open PORV failures; a TVA engineer's 1978
  report waited nine months for a reply; a senior B&W engineer's warning after Davis-Besse "fell between the cracks".
- **On the utility:** Met Ed lacked sufficient knowledge, expertise and personnel, and its QA did not reach the PORV,
  which was not classed safety-related.
- **The NRC**'s Notice of Violation held Met Ed responsible for causing the accident.

## Outcome

The Kemeny Commission reported on 30 October 1979. Its findings are in the front matter. It concluded that, given
the deficiencies, it was "convinced that an accident like Three Mile Island was eventually inevitable". The NRC fined
Met Ed $155,000, the maximum. INPO was formed the same year. GPU's suit against B&W settled mid-trial in January
1983. The core was not recovered; clean-up took nearly twelve years.

## Analysis

**The light is an `Actuate` record.** ADR-0042 §3 has the mechanism write one record per admitted `Actuate`:
seat, fence, tool, inputs, and `outcome`, one of `returned`, `failed` or `unknown`. That is the TMI light, done more
honestly: it says the call was made and what the tool reported back. It does not say what the world did. A tool
that drives a valve and returns `returned` has reported that it sent the command. Whether the valve moved is the
tool's claim, and ADR-0049 §4 is the right frame: its table marks each field **checked** or **claimed**, and a
result's label is claimed. The PORV light was a claimed field displayed as a checked one. The World Nuclear
Association's summary puts it in one line: operators "did not have an instrument indicating the valve's actual
position". That is ADR-0049's distinction, applied to hardware.

**Nothing in the corpus checks an effect.** ADR-0015 makes every effect an ordered, audited boundary crossing; the
crossing is what is audited. `RunCoupling` guarantees `NoEffectWithoutLiveObserver`: someone watches every
effect-bearing admit. The Observer reads the round topic, which holds the same record. It would have seen "close
valve, returned" and found nothing. `Labels` has `OutsideResultIsUntrusted`, which marks what an outward tool returns
as untrusted ingress. That protects the Thinker from being instructed by a result; it does not tell anyone the result
is false. `ChannelFidelity` (`Mechanism`) is about where a tool may connect, not whether its effect happened. So
TOPAK would have recorded TMI faithfully and changed nothing.

**What the corpus would need.** An `Actuate` whose effect matters needs a second channel: a reading taken
independently of the command, compared with the command. `proposed:EffectConfirmation` would give an allowlist entry
an optional confirming probe (a `Consult` on a distinct entry), and a property that an effect whose confirmation
disagrees, or is missing past a bound, is a finding raised to everyone who reads the topic. The disagreement must
come from a different channel from the command; a probe that reads the solenoid's own state is the TMI light again.
The finding is deny-only, as every Observer finding is. That fits a valve badly: stopping the next admit does not
close a stuck valve. What saved the core was a person shutting a block valve, which is the emergency path's job
(ADR-0052), and that path was not missing at TMI. The people did not know they needed it.

**The people were the Thinker.** TOPAK's premise is that the agent is Byzantine and the person is the backstop. At
TMI the people were honest, the indicator lied, and the persons acted on it. ADR-0068's TM9 names this exactly:
"a deceived person at a release seat is a semantic failure. Nothing here sees it." CR-17 says the same of operator
proficiency: every control that ends in a person presumes a trained person with a true picture. TMI is evidence that
the presumption fails when the picture is generated by the system the person is meant to check.

**The alarm flood is the other half.** More than 100 alarms with no suppression is a monitor that reports everything
and so tells nothing. TOPAK's Observer findings are deny-only and its correlator (ADR-0051) computes named folds, so
the corpus has no alarm prioritisation to get wrong. It also has none to get right.

**The 1977 warning.** Davis-Besse's PORV stuck open eighteen months earlier, and the block valve was shut in about
20 minutes. The Commission's finding that the warning "fell between the cracks" is a correlation across sites that
nobody computed. ADR-0051's correlator is per domain and does not reach another operator's plant.
