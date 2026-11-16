---
id: 1996-SPC-ARIANE-501
title: Ariane 5 Flight 501 — reused inertial reference software, an unprotected conversion, two identical failures and a diagnostic word read as attitude
kind: incident
date: 1996-06-04
sector: space
setting: Ariane 5 maiden flight 501 from Kourou; the two inertial reference systems (SRI) and the on-board computer (OBC); ESA and CNES
concerns: [interface-types, sensing, deployment, actuation, interlock, cascading-failure, supply-chain]
rules_at_time:
  - document: SRI software specification (as the Inquiry Board reports it)
    clause: exception handling
    paraphrase: on any exception the failure is to be indicated on the databus, its context stored in EEPROM, and the SRI processor shut down
  - document: SRI requirements and specification for Ariane 5
    clause: trajectory data
    paraphrase: by joint agreement, Ariane 5 trajectory data were not included in the SRI's requirements and specification
  - document: SRI alignment function, carried over from Ariane 4
    clause: post-lift-off operation
    paraphrase: the alignment function runs for 50 seconds after the SRIs enter flight mode, a provision for a fast restart after a late hold in an Ariane 4 count-down; Ariane 5 did not need it, and it was kept for commonality
analogue:
  - record: ADR-0058
    clause: "§1, §2"
    note: a kept node keeps its edges as typed; a replaced one re-establishes each edge or the edge is absent and its premise false (Proposed)
  - record: ADR-0023
    clause: "§2, §6"
    note: a variation's effect is premise loss, and every variation carries a declaration naming the premises it falsifies
  - record: ADR-0049
    clause: "§3"
    note: a handle cannot be mistaken for a literal; the validator tells two kinds of value apart by shape, with no judgment
  - record: ADR-0035
    clause: "§3"
    note: independence is an exclusion rule over two lineage records; two components of one lineage are not independent (Proposed)
  - record: ADR-0062
    clause: "§7"
    note: '"A stall that never ends is safe" is false of a vehicle in flight (command-chain overlay, Proposed)'
actors:
  - party: Inertial reference systems SRI 1 (back-up) and SRI 2 (active)
    role: sensor
    fault: crash
    note: identical hardware and software; each raised an Operand Error on the same conversion and shut down as specified
  - party: On-board computer
    role: controller
    fault: honest-error
    note: took SRI 2's diagnostic bit pattern as flight data and commanded full nozzle deflections
  - party: SRI and Ariane 5 programme (ESA, CNES, industrial partners)
    role: vendor
    fault: contested
    note: the Board found specification and design errors and a review and test process that did not catch them
  - party: Range safety self-destruct
    role: safety-system
    fault: honest
    note: triggered correctly by the rupture of the links between the boosters and the core stage
  - party: Inquiry Board chaired by J. L. Lions
    role: investigator
    fault: none-alleged
detection:
  means: [investigation]
  latency: seconds
trace:
  - step: Promote
    at: before flight 501
    note: RulesFloorNV_rev5's promotion, read as the SRI software entering Ariane 5's flight configuration; the tally votes an artifact and states none of the trajectory premises its unprotected conversions rested on
  - step: outside:horizontal-velocity-beyond-reused-envelope
    at: from lift-off
    note: Ariane 5's early trajectory builds horizontal velocity five times more rapidly than Ariane 4's
  - step: outside:unprotected-float-to-int16-conversion
    at: about H0 + 36.7 s
    note: in the alignment function, still running in flight, the horizontal bias BH was converted from 64-bit float to 16-bit signed integer and overflowed
  - step: outside:common-mode-redundant-failure
    at: the same instant, one 72 ms cycle apart
    note: back-up SRI 1 had stopped in the previous data cycle; active SRI 2 then failed the same way, so the OBC had nothing to switch to
  - step: outside:diagnostic-word-read-as-flight-data
    at: just after
    note: SRI 2 put a diagnostic bit pattern on the databus and the OBC used it as attitude data
  - step: Actuate
    at: H0 + ~37 s
    note: the effect step (RunCoupling.tla); full deflection of both booster nozzles and then the Vulcain nozzle, a correction for a deviation that had not occurred
  - step: outside:aerodynamic-breakup
    at: about H0 + 39 s
    note: angle of attack over 20 degrees; loads separated the boosters, and the self-destruct fired as designed
counterfactual:
  by: the Inquiry Board's recommendations, read in TOPAK's terms
  trace:
    - step: outside:omit-unneeded-function-in-flight
      at: lift-off
      note: R1, switch the alignment function off immediately after lift-off; ADR-0058 §1's Omit
    - step: outside:trajectory-premises-in-specification
      at: before promotion
      note: R5 and R10, list implicit assumptions and value ranges and put the trajectory data in specifications, and R2, test in a closed loop
    - step: Promote
      at: before flight
      note: a tally on an artifact whose edges to its premises were re-established for this vehicle
    - step: outside:sensor-keeps-sending-best-effort
      at: on any exception
      note: R3, never let a sensor stop sending best-effort data; R6, confine exceptions to the task where they arise
  holds: []
outcome:
  by: Ariane 501 Inquiry Board (chair Prof. J. L. Lions), for ESA and CNES
  date: 1996-07-19
  summary: >-
    The Board found that the loss of guidance and attitude information about 37 seconds after main engine ignition
    was "due to specification and design errors in the software of the inertial reference system". The Operand Error
    arose in an alignment function that served no purpose after lift-off; the variable that overflowed had been left
    unprotected on reasoning the Board found faulty for it; Ariane 5 trajectory data were not in the SRI
    requirements, so the SRI was never tested against Ariane 5 conditions; and reviews and tests did not include
    adequate analysis and testing of the SRI. The Board did not implicate the system architecture.
  aftermath: >-
    The Board made fourteen recommendations, among them switching off the alignment function after lift-off, a
    closed-loop test facility with real equipment, never letting a sensor stop sending best-effort data, a review of
    all flight software for implicit assumptions and value ranges, confining exceptions, more telemetry on failure,
    and treating software as faulty until shown otherwise. ESA's advisory of 23 July 1996 listed correcting the SRI,
    re-examining all embedded software, more representative qualification tests and deliberate overlap between tests.
  effect_reversed: "no"
model:
  modules: [RulesFloorNV_rev5, RunCoupling, FloorComposition, Observers, proposed:EnvelopeOfReuse]
  properties: [FloorErrorIsDeny, DenyByAnyOf]
  mutations: []
  records: [ADR-0058, ADR-0057, ADR-0023, ADR-0049, ADR-0018, ADR-0035, ADR-0045, ADR-0062, ADR-0038]
  findings: [CR-42, TM10, TM11]
  fault_class: a reused component whose range premise was false on the new vehicle, failing in common mode, its fail-stop output then consumed as data
sources:
  - https://www-users.cse.umn.edu/~arnold/disasters/ariane5rep.html
  - https://www.esa.int/Newsroom/Press_Releases/Ariane_501_-_Presentation_of_Inquiry_Board_report
verified: 2026-11-12
---

## Summary

Ariane 5's first flight lifted off on 4 June 1996. Behaviour was nominal until about H0 + 36 seconds. The two
inertial reference systems carried identical hardware and software, reused from Ariane 4. In each, an alignment
function kept running after lift-off: it is operative for 50 seconds after the SRIs enter flight mode, a provision on
Ariane 4 for a quick restart after a late count-down hold, and it "was maintained for commonality reasons".

In that function the horizontal bias BH, a value tied to the launcher's horizontal velocity, was converted from a
64-bit floating-point number to a 16-bit signed integer. Ariane 5's early trajectory builds horizontal velocity
five times more rapidly than Ariane 4's, and the value no longer fitted. The conversion was not protected, an Operand
Error was raised, and each SRI shut itself down as its specification required. The back-up SRI 1 had stopped in
the previous 72-millisecond data cycle, so when the active SRI 2 failed the OBC could not switch.

SRI 2 then sent a diagnostic bit pattern, which the OBC interpreted as flight data. The OBC commanded full deflection
of the boosters' nozzles and then of the Vulcain engine's, correcting for a deviation that had not occurred. At an
angle of attack over 20 degrees the aerodynamic loads separated the boosters, the self-destruct triggered, and the
launcher disintegrated at about H0 + 39 seconds, at about 3,700 m.

## Defensive position

The positions below are the designers' reasoning as the Inquiry Board reconstructed it; no party's separate defence
was read for this entry.

- **The unprotected variables.** Seven variables were at risk of an Operand Error and four were protected. For the
  other three, "further reasoning indicated that they were either physically limited or that there was a large
  margin of safety". On Ariane 4 trajectories that held.
- **Shutting down on an exception.** The specification answered random hardware failure, which "can quite rationally
  be handled by a backup system": a failed unit stops and the other takes over.
- **Commonality.** The alignment function was not needed on Ariane 5 and was kept, unchanged, "for commonality
  reasons" with Ariane 4.
- **Trajectory data.** Not putting Ariane 5 trajectory data in the SRI specification was "jointly agreed" by the
  partners.

## Adversarial position

**The Inquiry Board** rejected each of these as applied to Ariane 5:

- The physical-limitation reasoning was wrong for BH, and with no Ariane 5 trajectory data in the requirements the SRI
  was never exercised against the conditions that broke it; the alignment function was left out of the simulations.
- Backing up against random hardware failure gives nothing against a systematic software error when both units run
  the same software. It criticised "the culture within the Ariane programme of only addressing random hardware
  failures" and said software "should be assumed to be faulty" until shown correct by accepted best practice.
- Once a processor had shut down it could not be restarted in flight, and R3 asks that a sensor never stop sending
  best-effort data.
- Equipment and system tests were not representative enough, and reviews did not analyse the SRI adequately.

## Outcome

The Board's report is dated 19 July 1996 in Paris; ESA's advisory on it is dated 23 July. It found the cause in
"specification and design errors in the software of the inertial reference system", did not implicate the system
architecture, and made fourteen recommendations. ESA's advisory listed the corrective actions. The launcher was lost;
nothing was reversed.

## Analysis

**A kept node on a new vehicle.** ADR-0058 §1 lets a deployment *Keep* an archetype node, and then "the archetype's
edges below it stand, as typed". That is exactly what Ariane 5 did with the SRI, and why it failed: the edges that
mattered were not to other artifacts but to the environment, Ariane 4's trajectory. ADR-0057 §2's *givens* would
name "BH is physically limited" as a premise; ADR-0023 §2 says a variation loses the theorems whose premises it
falsifies. The corpus can say all of this, but only for premises someone wrote down; the Board's R5, "list implicit
assumptions", is the step before. The finding against ADR-0058: *Keep* needs a clause that a kept node's
environmental givens are restated per deployment, since a new vehicle can falsify them without touching the node.
`proposed:EnvelopeOfReuse` would model a kept component with a declared input range, a deployment whose range is
wider, and a gate that refuses promotion until the edge is re-established; its mutation is Keep without restating.

**Redundancy in common mode.** The two SRIs were the same lineage, so their failures were one failure. ADR-0035 §3
(Proposed; CR-42 notes text in force already rests on it) makes independence an exclusion rule over lineage records,
and TM10 and TM11 declare the corpus's own limits: an Observer "may share its lineage", and coupling cannot see
collusion. `DenyByAnyOf` in Observers.tla buys diversity of opinion only if the opinions are independent. The
Board's sentence on random hardware failure is the corpus's premise that every agent is Byzantine, applied to a
sensor.

**"Failure can only subtract" was the design, and it was fatal.** The SRI's exception policy is fail-stop: on error,
signal and stop. `FloorErrorIsDeny` (FloorComposition.tla) is the same rule for authority, and there it is right: a
floor error refuses an admit. For a guidance sensor in flight, stopping removed the only attitude data the vehicle
had. ADR-0062 §7 already says this of vehicles ("a stall that never ends is safe" is false in flight), and the
Board's R3 says it of sensors. ADR-0045 §2's test classes components by what their failure does to *authority*; it
has no column for what a stopped component does to a control loop. That is where the pattern stops.

**The subtraction became an addition at the interface.** The fail-stop SRI still wrote to the databus, and the OBC
could not tell a diagnostic word from an attitude word, so a stopped sensor drove the nozzles hard over. ADR-0049 §3
is the corpus's rule for this shape inside the mechanism: a handle "cannot be mistaken for a literal", because the
validator (ADR-0018) tells them apart "by shape, with no judgment". A databus word typed as diagnostic or attitude,
checked at the OBC, is that rule. TOPAK types the mechanism's own interfaces; a vehicle's sensor bus would be a
deployment's, excluded from the trusted base unless declared, which is why `outside:diagnostic-word-read-as-flight-data`
is on the to-do list and no module step stands for it.

**The counterfactual holds nothing the corpus names.** Every recommendation is a premise, a range or a test, and
`holds` is empty because no module states a property about value ranges or about a sensor's output after failure.
