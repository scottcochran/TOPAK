---
id: 1986-MED-THERAC-25
title: Therac-25, 1985-1987 — software checks in place of hardware interlocks, a race on fast edits, and six overdoses
kind: incident
date: "1986"
sector: medical
setting: AECL Therac-25 dual-mode medical linear accelerator, PDP-11 control software; clinics in Marietta (Georgia), Hamilton (Ontario), Yakima (Washington) and Tyler (Texas)
concerns: [interlock, timing, monitoring, human-in-the-loop, accountability, interface-types, supply-chain]
rules_at_time:
  - document: US FDA device classification (as described by Leveson and Turner)
    clause: pre-market notification
    paraphrase: medical accelerators needed only a pre-market notification showing substantial equivalence to a device already on the market; the FDA required no more for the Therac-25
  - document: US medical device reporting regulations of the time
    clause: reporting duties
    paraphrase: manufacturers and importers had to report deaths, serious injuries and malfunctions that could cause them; hospitals and health professionals had no duty to report (amended in 1990)
  - document: Radiation Control for Health and Safety Act
    clause: defect and corrective action
    paraphrase: once a radiation-emitting product is found defective the FDA orders the firm to notify purchasers and approves its corrective action plan (CAP)
analogue:
  - record: ADR-0045
    clause: "§2"
    note: a component enters the trusted base only if its failure can only subtract or its identity is issued; otherwise the design changes until its failure only subtracts
  - record: ADR-0068
    clause: "§2 T-0068-8; Findings 1"
    note: the effector interlock is a trust root that nothing issues; if it fails, an irreversible effect happens without a person's act
  - record: ADR-0033
    clause: "§4"
    note: admits are decided, then ordered, then re-checked against the state at the entry's log position; an admit that fails the second run is void
  - record: ADR-0051
    clause: "§3, §7"
    note: the correlator reads across cells and its findings carry their evidence; what it does for collusion is limited
actors:
  - party: Atomic Energy of Canada Limited (AECL)
    role: vendor
    fault: omission
    note: told users overdoses were not possible and that it knew of no other accidents; claimed a five-orders-of-magnitude improvement on a cause it "cannot be firm" about
  - party: Therac-25 control software
    role: automation
    fault: byzantine
    note: delivered unscanned high-energy beams while the display showed an underdose or no dose; two race conditions are established, others are not ruled out
  - party: Radiation therapy operators
    role: operator
    fault: honest
    note: followed standard practice, including pressing P to proceed after a treatment pause, on a machine that paused often without consequence
  - party: Fritz Hager, physicist, East Texas Cancer Center
    role: investigator
    fault: honest
    note: with the operator, reproduced Malfunction 54 and showed that editing speed was the key factor
  - party: FDA (CDRH) and the Canadian Radiation Protection Bureau
    role: regulator
    fault: none-alleged
detection:
  means: [customer, regulator]
  latency: months
trace:
  - step: outside:hardware-interlocks-not-carried-over
    at: design, 1976-1982
    note: the Therac-20 kept independent protective circuits and mechanical interlocks; the Therac-25 relied on software for them
  - step: outside:safety-analysis-excludes-software
    at: March 1983
    note: AECL's fault tree assumed residual software errors away and gave "computer selects wrong mode" a probability of 4 x 10^-9 without justification
  - step: outside:overdose-reported-and-denied
    at: 3 June 1985, Marietta
    note: the patient said "You burned me"; AECL told the physicist improper scanning was not possible; the treatment printout feature was disabled, so no record of the delivered beam existed
  - step: outside:cause-asserted-without-reproduction
    at: July-September 1985, Hamilton
    note: AECL could not reproduce the fault, suspected a turntable microswitch, fixed that, and claimed an improvement of at least five orders of magnitude
  - step: outside:fast-edit-race
    at: 21 March and 11 April 1986, Tyler
    note: mode changed from X-ray to electron within about 8 s of entry; the magnet routine had stopped looking for edits, and data entry never saw the change
  - step: Finding
    at: seconds after beam-on
    note: Observers.tla's finding, here the dose monitor's Malfunction 54 ("dose input 2"), raised after the dose was delivered; the display showed 6 of 202 monitor units
  - step: outside:proceed-key-clears-pause
    at: same treatment
    note: a treatment pause needed one key, P, up to five times before a suspend; the operator pressed it, as standard practice was
  - step: outside:user-reproduces-fault
    at: April 1986
    note: AECL first said it could not reproduce Malfunction 54; it did so once told the edit had to be fast, and measured about 25,000 rads
  - step: Promote
    at: 15 April 1986
    note: FloorRouting's route for a change that only narrows; AECL told users to remove the cursor-up key cap and tape the contacts open
  - step: outside:counter-overflow-skips-check
    at: 17 January 1987, Yakima
    note: a one-byte flag incremented on every pass of Set-Up Test read zero on every 256th; "set" pressed at that moment skipped the collimator check and the beam came on with no target in place
  - step: outside:regulator-declares-defective
    at: 2 May 1986 and 10 February 1987
    note: the FDA declared the machine defective and, after Yakima, asked AECL to tell users to stop routine use until the CAP was in place
  - step: outside:hardware-interlocks-added
    at: CAP revision 5, 21 July 1987
    note: a hardware single-pulse shutdown, a hardware turntable interlock, interlocking with the 270-degree bending magnet, edit keys reduced to three
outcome:
  by: US FDA (CDRH); Leveson and Turner's investigation (IEEE Computer, July 1993)
  date: 1987-07-21
  summary: >-
    Six known massive overdoses occurred between June 1985 and January 1987; Leveson and Turner call them "the
    worst series of radiation accidents in the 35-year history of medical accelerators". The FDA declared the
    Therac-25 defective on 2 May 1986 and demanded a corrective action plan; after the second Yakima accident it
    concluded that software alone could not be relied on and required hardware interlocking. AECL's fifth and final
    CAP (21 July 1987) added hardware safeguards against software errors and fixed the known faults. Leveson and
    Turner list as contributing factors management's lack of follow-through on reported incidents, overconfidence in
    software and the removal of hardware interlocks ("making the software into a single point of failure"),
    presumably poor software engineering, and unrealistic risk assessments.
  aftermath: >-
    The machine was recalled for design changes including hardware safeguards. Lawsuits followed and were settled.
    The reporting law was amended in 1990 to require health-care facilities to report incidents to manufacturers
    and the FDA.
  effect_reversed: "no"
model:
  modules: [Release, Observers, Correlator, FloorRouting, proposed:InterlockIndependence]
  properties: [DenyByAnyOf, ConflictIsAFinding, SilenceIsCounted, NoWideningWithoutIssuance]
  mutations: []
  records: [ADR-0045, ADR-0068, ADR-0033, ADR-0030, ADR-0038, ADR-0051, ADR-0028, ADR-0007]
  findings: [TM11, TM9, CR-2]
  fault_class: a check whose failure adds, sharing state with what it checks; findings after the effect; one interested party as the only correlator across sites
sources:
  - https://web.mit.edu/6.033/2004/wwwdocs/papers/Therac_1.html
  - https://web.mit.edu/6.033/2004/wwwdocs/papers/Therac_2.html
  - https://web.mit.edu/6.033/2004/wwwdocs/papers/Therac_3.html
  - https://web.mit.edu/6.033/2004/wwwdocs/papers/Therac_4.html
  - https://web.mit.edu/6.033/2004/wwwdocs/papers/Side_bar_Y.html
  - https://en.wikipedia.org/wiki/Therac-25
verified: 2026-11-12
---

## Summary

The Therac-25, a dual-mode linear accelerator from Atomic Energy of Canada Limited (AECL), was designed around
computer control. Its predecessors, the Therac-6 and Therac-20, had independent protective circuits and mechanical
interlocks, with software as a convenience; the Therac-25 relied on software for those functions and reused code
from both. Eleven were installed. Between June 1985 and January 1987 six massive overdoses are known, at Marietta,
Hamilton, Yakima (twice) and Tyler (twice).

At Tyler on 21 March 1986 an experienced operator typed "x" for X-ray, corrected it to "e" with the cursor-up key,
and pressed return through the remaining fields to "beam ready" within about eight seconds. The machine stopped with
"Malfunction 54", a "treatment pause", and showed 6 of 202 monitor units delivered. The manual said only that
Malfunction 54 was a "dose input 2" error. A pause needed one key, P, to resume; she pressed it and the machine
stopped again. The patient felt what he described as an electric shock. AECL engineers could not reproduce the fault
and said the machine could not overdose. After a second Tyler accident on 11 April, the hospital physicist and the
operator reproduced it: if the prescription was edited fast, the overdose occurred. The fault was a race between
the data-entry and magnet-setting tasks. Both Tyler patients died.

On 17 January 1987 at Yakima a different fault appeared: a one-byte variable incremented on each pass of a set-up
routine read zero on every 256th pass, and an operator pressing "set" at that moment skipped the check that the
upper collimator was in place. The full-energy electron beam came on with no target and no scanning.

## Defensive position

**AECL**, as Leveson and Turner record it:

- After Hamilton, it could not reproduce the fault, attributed it to a turntable microswitch, made the position
  code tolerate one failed switch, and stated that analysis "indicates an improvement over the old system by at
  least five orders of magnitude".
- Its quality-assurance manager said the software had been tested for 2,700 hours, clarified under questioning as
  "2,700 hours of use"; the March 1983 safety analysis assumed residual software errors away.
- After Tyler it issued an immediate workaround (remove the cursor-up key) and a corrective action plan, revised
  five times with FDA and user input.

**Leveson and Turner** themselves write that their aim is "not to criticize the equipment's manufacturer or anyone
else": the mistakes "are not unique to this manufacturer".

## Adversarial position

**The FDA** (February 1987): "It is impossible for CDRH to find all potential failure modes and conditions of the
software"; the accidents showed software alone could not be relied on, and hardware interlocking of the turntable
was required. An FDA reviewer found that AECL's test data for the edit fix showed "the exact opposite result".

**The users**, through their user group, pressed for hardware changes AECL had not proposed.

**Leveson and Turner**: AECL told the Tyler physicist it knew of no other overdoses when it knew at least of
Hamilton; it had no mechanism to follow up reported accidents; the software was "a single point of failure"; and
"concluding that an accident was the result of human error is not very helpful or meaningful".

## Outcome

The FDA declared the Therac-25 defective on 2 May 1986 and required a corrective action plan. After the second
Yakima accident it issued a Notice of Adverse Findings (10 February 1987) and asked AECL to tell users to stop routine
use until the plan was in place. AECL's fifth and final CAP (21 July 1987) added a hardware single-pulse shutdown, a
hardware turntable interlock and interlocking with the bending magnet, limited editing keys, and fixed the known
faults; full implementation took more than two years from Tyler. Three of the injured patients later died. Lawsuits
were settled. In 1990 reporting duties were extended to health-care facilities.

## Analysis

**This is ADR-0045's rule, shown by a pair of machines.** The Therac-20 ran related software with the same class of
fault; at the University of Chicago new students kept tripping its fuses and breakers. There the fault was "just a
nuisance" because independent circuits would not let the beam on: its failure could only subtract. The Therac-25
let the same kind of software decide and check, and its failure added a 25 MeV unscanned beam. Under ADR-0045 §2 the
Therac-25 software would be at best a trust root whose residual is the overdose, or "the design is changed until its
failure can only subtract", which is what the FDA required. TOPAK's own command-chain overlay makes the admission in
the same words: ADR-0068 T-0068-8, "the effector interlock", is a trust root, and its Finding 1 says nothing issues
it. Release.tla is explicit that "the interlock is the only check this module relies on". Therac-25's interlocks
shared variables with the code they checked: `Class3` was written by the set-up task and read by the housekeeping
task that did the checking. `proposed:InterlockIndependence` would state that the interlock reads the effector's
state through a path the deciding software cannot write, and a mutation that lets it share one.

**The race is a missing re-check at apply.** ADR-0033 §4 runs the mechanism's checks twice, once at decision and
again on the state at the entry's log position, and voids an admit that fails the second. The Therac-25 displayed
"verified" for a prescription its magnets were not set to and turned the beam on without checking again. TOPAK's
version binds a decision to the digest of its frozen input (ADR-0030 §4); the Therac's input changed under its
decision. No module models an input edited between decide and apply, so the step stays outside.

**Findings came after the effect, and one key cleared them.** Malfunction 54 was raised after the dose, as an
Observers.tla `Finding` that blocks only the next admit. Release.tla's `ConflictIsAFinding` states the same limit for
a check that fails after an irreversible effect: it subtracts, and it voids nothing. The operator could clear the
pause with P five times, and the display told her almost nothing had been delivered. That is TM9's residual for a
person, "a deceived person ... is a semantic failure. Nothing here sees it", and ADR-0068 A-0068-5's assumption that
the person "can see what the act requires" failing on the screen itself. No record says that repeated refusals of one
principal escalate.

**One correlator, and it was an interested party.** Six accidents at four sites were connected by users'
"personal communication" and lawsuits, not by the manufacturer, which told Tyler it knew of none. ADR-0051's
correlator is the cross-cell reader, and Correlator.tla's `SilenceIsCounted` charges a miss only to a correlator whose
silence another correlator's finding exposes. With a single correlator, silence is TM11's row, bounded by "nothing";
the user group was the second correlator that eventually existed.

**The cheap fix went in the cheap direction.** Removing the cursor-up key narrowed the alphabet, which in TOPAK any
promotion may do without issuance (`NoWideningWithoutIssuance` in FloorRouting). It closed one path and left the
Yakima fault.

**The record.** At Marietta the treatment printout was disabled, so nothing showed what was delivered. ADR-0028's
F1, admit decisions with their inputs, is the class that was missing.

**Outside steps.** `hardware-interlocks-not-carried-over`, `safety-analysis-excludes-software`,
`overdose-reported-and-denied`, `cause-asserted-without-reproduction`, `fast-edit-race`, `proceed-key-clears-pause`,
`user-reproduces-fault`, `counter-overflow-skips-check`, `regulator-declares-defective`, `hardware-interlocks-added`.
`fast-edit-race` and `counter-overflow-skips-check` are what an interlock-independence module would have to rule out.
