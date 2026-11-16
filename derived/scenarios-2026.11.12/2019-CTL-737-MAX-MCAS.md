---
id: 2019-CTL-737-MAX-MCAS
title: Boeing 737 MAX, Lion Air 610 and Ethiopian 302 — a control law acting repeatedly on one angle-of-attack sensor
kind: incident
date: 2019-03-10
sector: control
setting: the MCAS function of the Boeing 737-8 (MAX) flight control computer; Lion Air PK-LQP off Karawang, Indonesia, and Ethiopian Airlines ET-AVJ near Bishoftu, Ethiopia
concerns: [sensing, authority, actuation, human-in-the-loop, monitoring, deployment, supply-chain, feedback]
rules_at_time:
  - document: FAA guidance on pilot recognition and response, as the House committee report describes it
    clause: stabilizer trim runaway
    paraphrase: guidance presumes pilots recognise a stabilizer trim runaway and complete the procedure within four seconds; Boeing assumed an erroneous MCAS activation would look and be handled the same way
  - document: Boeing coordination sheet for MCAS requirements (internal; quoted by the House committee)
    clause: MCAS design requirements
    paraphrase: MCAS should have no objectionable interaction with the piloting of the airplane and should not interfere with dive recovery
  - document: FAA type certification under the Changed Product Rule, with Organization Designation Authorization
    clause: delegation; changes during certification (JATR recommendation areas 1, 4, 5)
    paraphrase: Boeing employees acting as authorized representatives made findings for the FAA; the JATR, as the House report quotes it, found the certification plans and the preliminary system safety assessment were not updated for MCAS's expansion to low speed
analogue:
  - record: ADR-0007
    clause: Decision
    note: semantic lift is prohibited in the admit path and a classifier's output enters only as a finding that subtracts; here a sensor's reading was the enabling condition of an actuation
  - record: ADR-0045
    clause: "§2"
    note: a component whose failure can add is a row only as a trust root with an issued identity and a record of its own; otherwise it is refused, or the design changes until its failure only subtracts
  - record: ADR-0062
    clause: "§1, §2, §4"
    note: the governor lifts its own facts, permits each entry against an exact count, and every entry declares an extent (command-chain overlay, Proposed)
  - record: ADR-0039
    clause: "§2"
    note: every Run admit needs a live cell Observer, so a dead monitor stalls admits instead of looking like a clean system
  - record: ADR-0058
    clause: "§2"
    note: a replaced node re-establishes each edge at a declared type; an edge not mentioned is absent and its premise false (Proposed)
actors:
  - party: The Boeing Company
    role: vendor
    fault: contested
    note: the House committee majority found faulty design assumptions and withheld information; Boeing said it had told the FAA that MCAS's final design had changed
  - party: Federal Aviation Administration
    role: regulator
    fault: contested
    note: delegated parts of the compliance finding; its own unfinalized post-Lion Air review found no noncompliances (House report)
  - party: MCAS in the flight control computer
    role: automation
    fault: contested
    note: acted on its one sensor as designed; whether the design was adequate is the dispute
  - party: Left angle-of-attack sensor on PK-LQP
    role: sensor
    fault: byzantine
    note: read about 21 degrees high after a mis-calibration in an earlier repair (KNKT)
  - party: AOA DISAGREE alert
    role: monitor
    fault: omission
    note: tied to an optional indicator and inoperable on most of the fleet (House report; KNKT contributing factor 5)
  - party: Xtra Aerospace and Lion Air maintenance
    role: maintainer
    fault: honest-error
    note: KNKT found the mis-calibration was not detected at repair, and could not determine that the installation test was performed properly
  - party: Crew of PK-LQP, Denpasar to Jakarta, 28 October 2018
    role: operator
    fault: omission
    note: stopped MCAS with the stabilizer trim cutout on a jump-seat pilot's advice; did not log the stick shaker or the cutout (KNKT factor 8)
  - party: Crews of Lion Air 610 and Ethiopian 302
    role: operator
    fault: contested
    note: KNKT factor 9 cites crew resource management; BEA and NTSB asked the EAIB for more analysis of the ET302 crew's performance
detection:
  means: [operator, investigation]
  latency: weeks
trace:
  - step: outside:sensor-installed-with-bias
    at: 28 October 2018, Denpasar
    note: a refurbished left AOA sensor, rebuilt in 2017, replaced the original; its 21-degree bias was not detected by the installation test
  - step: outside:single-sensor-enables-actuation
    at: design, from 2016
    note: MCAS read one of the two AOA sensors; its authority was raised in March 2016 from 0.6 to 2.5 degrees of stabilizer and extended to low speed
  - step: Effect
    at: 28 October 2018, Denpasar to Jakarta
    note: Intent.tla's effect, one per MCAS stabilizer command; there was no count, which is M_NOCOUNT's run
  - step: Revoke
    at: same flight
    note: Operators.tla's deny, which needs no lease; the crew set STAB TRIM to CUT OUT on a third pilot's advice and flew on manual trim
  - step: outside:anomaly-not-recorded
    at: on landing at Jakarta
    note: the log named IAS and ALT DISAGREE and FEEL DIFF PRESS, not the stick shaker or the cutout; the AOA DISAGREE alert never appeared
  - step: Effect
    at: 29 October 2018, Lion Air 610, from 23:20 UTC
    note: AOA difference about 21 degrees from takeoff; MCAS moved the stabilizer more than 20 times (House report); 189 on board
  - step: outside:crew-counters-without-diagnosis
    at: same flight
    note: the crew started the IAS DISAGREE checklist and did not identify the runaway stabilizer (KNKT)
  - step: Effect
    at: 10 March 2019, Ethiopian 302
    note: the left AOA sensor read wrongly after a normal takeoff; MCAS triggered four times in about six minutes (House report)
  - step: FenceEpoch
    at: 13 March 2019
    note: Operators.tla's fleet fence, read as the FAA's grounding order, after China, the EU and Canada had acted
counterfactual:
  by: the design Boeing adopted afterwards (two sensors into MCAS, no repeated activation), read in TOPAK's terms
  trace:
    - step: Finding
      at: takeoff, as the vanes diverge
      note: Observers.tla; two vanes disagreeing by 21 degrees is a finding
    - step: Refuse
      at: the first MCAS demand
      note: one finding blocks the next admit with no quorum sought
    - step: Effect
      at: a genuine high-AOA event
      note: one activation, within a count and a declared extent
    - step: RefuseEffect
      at: any repeat in the same event
      note: the count is spent
    - step: Revoke
      at: any time
      note: the crew's cutout stays available whatever MCAS does
  holds: [DenyByAnyOf, EveryEffectHasALease, DenyAlwaysAvailable]
outcome:
  by: KNKT (Indonesia); EAIB (Ethiopia), with BEA and NTSB comments; the Joint Authorities Technical Review; US House Committee on Transportation and Infrastructure (majority staff)
  date: 2022-12-23
  summary: >-
    KNKT's final report (25 October 2019) found the design and certification of MCAS inadequate and listed nine
    contributing factors, among them incorrect assumptions about crew response, reliance on a single AOA sensor, an
    AOA DISAGREE alert not correctly enabled, a mis-calibrated replacement sensor, the unlogged earlier flight, and the
    accident crew's workload management. The JATR gave the FAA recommendations in twelve areas on 11 October 2019. The
    House committee majority (September 2020) found faulty design and performance assumptions, a culture of
    concealment and conflicted representation. The EAIB published its final report on 23 December 2022; the BEA said
    it shared the EAIB's conclusions on MCAS and that the crew's performance was not analysed enough.
  aftermath: >-
    The FAA grounded the 737 MAX on 13 March 2019. Boeing said MCAS would take both AOA sensors and would no longer
    activate repeatedly, and in January 2020 recommended simulator training. The FAA revoked the repair station
    certificate of Xtra Aerospace in October 2019. Lion Air reissued reporting and training instructions.
  effect_reversed: "no"
model:
  modules: [Intent, Observers, Operators, Coupling, proposed:SensedAdmit]
  properties: [EveryEffectHasALease, DenyByAnyOf, DenyAlwaysAvailable, NoAdmitWithoutLiveObserver]
  mutations: [M_NOCOUNT, M_NOCOUPLE]
  records: [ADR-0007, ADR-0045, ADR-0062, ADR-0039, ADR-0058, ADR-0057, ADR-0050, ADR-0024, ADR-0067]
  findings: [CR-2, CR-8, CR-17, TM9, TM10]
  fault_class: one sensor's arbitrary failure admitted as the enabling condition of an uncounted actuation, with the human recovery assumed rather than measured
sources:
  - https://aviation-is.better-than.tv/737%20MAX%202018%20-%20035%20-%20PK-LQP%20Final%20Report.pdf
  - https://democrats-transportation.house.gov/imo/media/doc/2020.09.15%20FINAL%20737%20MAX%20Report%20for%20Public%20Release.pdf
  - https://www.commerce.senate.gov/services/files/F56AD012-6D47-4258-BFF0-08D6F5B0A22D
  - https://bea.aero:443/fileadmin/user_upload/BEA_Press_Release_03012023.pdf
verified: 2026-11-12
---

## Summary

MCAS was added to the 737 MAX flight control computer to push the nose down in some high angle-of-attack
conditions with flaps up. It read one of the airplane's two AOA sensors. As first designed it moved the horizontal
stabilizer at most 0.6 degrees and only at higher speeds; in March 2016 Boeing redesigned it to act at low speed and
to move the stabilizer up to 2.5 degrees per activation (House report). Flight manuals and crew training did not
describe it (KNKT).

On 28 October 2018 a mechanic in Denpasar replaced PK-LQP's left AOA sensor with a refurbished unit. KNKT found it
carried a 21-degree bias that the installation test did not detect. On the flight to Jakarta the stick shaker ran
and MCAS activated; a third pilot in the jump seat advised setting STAB TRIM to CUT OUT, and the crew flew on manual
trim. The log entry named IAS DISAGREE, ALT DISAGREE and FEEL DIFF PRESS, not the stick shaker or the cutout. The
AOA DISAGREE alert was not working on that airplane, as on most of the fleet.

Lion Air 610 left Jakarta at about 23:20 UTC the next morning with the same AOA difference. MCAS moved the
stabilizer more than 20 times while the crew worked the IAS DISAGREE checklist; the airplane struck the sea and all
189 on board died. On 10 March 2019 Ethiopian 302's left AOA sensor read wrongly after a normal takeoff from Addis
Ababa; MCAS triggered four times in about six minutes and the airplane crashed near Bishoftu. The FAA grounded the
type on 13 March 2019.

## Defensive position

**Boeing**, in answers to the House committee, said that "on numerous occasions" it had told the FAA and other
regulators that MCAS's final design had changed and now covered low speed, and that FAA personnel observed the
expanded MCAS in certification flight tests. Its chief executive described MCAS to the committee as "an extension
of the pre-existing Speed Trim function".

**KNKT** recorded that the crew-response assumptions were "consistent with current industry guidelines", and that
on those assumptions the single-sensor design "met all certification requirements". The FAA's own post-Lion Air
review, in a draft the House committee saw, found gaps in what Boeing had provided and no "noncompliances".

**Christopher Hart**, chairing the JATR, told the Senate committee that the automation "usually worked but
sometimes failed", and that some crews handled the failure, including the Lion Air crew of the day before.

## Adversarial position

**The House committee majority** found that Boeing let MCAS act on a single sensor, expected pilots who were
largely unaware of it to mitigate a malfunction, did not classify it as safety-critical, and withheld that a test
pilot took more than ten seconds to respond to an uncommanded activation, a result he called "catastrophic". It
found that MCAS's operation violated Boeing's own requirement against objectionable interaction with the pilot. The
737 MAX chief project engineer told staff he had approved the 2016 redesign unaware that MCAS used one sensor or
could activate repeatedly. The committee contrasted the KC-46 tanker's MCAS: two sensors, one stabilizer movement
per activation, and override by pulling back on the column.

**KNKT** called the design and certification of MCAS inadequate. **Hart** said certification should favour
fail-safe design over "reliance on pilot action as primary means of risk mitigation". **The BEA and NTSB** argued
that the ET302 crew's actions before the first activation should have been analysed as well.

## Outcome

KNKT published its final report on 25 October 2019; the JATR submitted its observations and recommendations on 11
October 2019; the House committee majority staff reported in September 2020. The EAIB published ET302's final report
on 23 December 2022 without appending the BEA's comments as the BEA had asked; the BEA said it shared the EAIB's
analysis of MCAS's contribution. Boeing said MCAS would take both sensors and not activate repeatedly. Nothing was
reversed.

## Analysis

**The admit was a sensor's reading.** ADR-0007 keeps semantic judgment out of the admit path and lets a classifier's
output in only as a finding that subtracts. An AOA vane is not a classifier, but ADR-0067 §1 files every rule that
needs "a judgment about the world" nowhere in the admit path, and MCAS's guard was exactly that. The corpus does let
measurements in on its own vehicles: ADR-0062 §1 has the governor lift position and extent, and TM8 declares the
navigation source a trust root with its residual. So the governing clause is ADR-0045 §2: a component whose failure
can add is a row only as a declared trust root, otherwise the design changes until its failure only subtracts. The
left vane's failure added nose-down commands, and nothing classed it so. The 2014 Boeing email the House report
quotes, "With annunciation, failure is minor ... Without annunciation, failure is major", is a failure-direction
classification that rested on a person noticing.

**Four of TOPAK's rules would have bitten, and none is a guarantee of flight.**

- *Count.* Intent.tla's governor counts every effect under a lease; `M_NOCOUNT` breaks `EveryEffectHasALease`. MCAS
  on the MAX had no count; the KC-46's acted once per activation.
- *Extent.* ADR-0062 §4 makes every entry declare how far one act runs. The change from 0.6 to 2.5 degrees is an
  extent quadrupled, and §4 itself says an extent is a declaration nothing checks.
- *Agreement.* `DenyByAnyOf` in Observers.tla blocks the next admit on one finding. Two vanes 21 degrees apart is the
  plainest finding there is; the design read one vane and never looked for it.
- *The person's deny.* `DenyAlwaysAvailable` (Operators.tla) is what saved the Denpasar flight: a stop that needs no
  lease. The cutout also took the pilots' own electric trim with it, where Operators.tla revokes one principal.

**The dead monitor is `M_NOCOUPLE`'s run.** The AOA DISAGREE alert was off on most of the fleet and nobody knew,
which is CR-2's "a dead Observer looks like a clean system". ADR-0039 §2 couples every Run admit to a live Observer,
so a dead one stalls admits; `NoAdmitWithoutLiveObserver` fails only under `M_NOCOUPLE`. Here the alert was only a
display, coupled to nothing, so its absence changed nothing but what the log could say.

**The change outran its assessment.** The JATR found the preliminary system safety assessment was not updated after
the 2016 redesign. ADR-0058 §2 and ADR-0057 §2 compute this: an edge not re-established is absent and the theorem on
it void, instead of inherited. Promotion by digest (ADR-0024) would have forced a new tally on the changed function,
but CR-8 is right that a tally buys attribution and authorization, not safety.

**Where the pattern stops.** MCAS existed to add a nose-down command, so ADR-0045's subtract-only test cannot be met
by a protective control law; the most the corpus offers is a bounded addition. The person's recovery was a premise
(four seconds) that a test had already contradicted; CR-17 and TM9 say the corpus presumes a present, trained human
and sees nothing of a deceived one. `outside:single-sensor-enables-actuation` and
`outside:crew-counters-without-diagnosis` are the to-do. `proposed:SensedAdmit` would model an effect enabled by a
measured fact under a count, an extent and a cross-check whose disagreement is a finding, with three mutations (one
sensor, no count, no extent), each breaking one property.
