---
id: 2024-CLD-CROWDSTRIKE-CHANNEL-FILE
title: CrowdStrike Falcon Channel File 291, 19 July 2024 — a content update read a 21st input the sensor never supplied
kind: incident
date: 2024-07-19
sector: cloud
setting: CrowdStrike Falcon sensor for Windows (7.11 and later), Rapid Response Content delivered worldwide from CrowdStrike's cloud
concerns: [deployment, interface-types, configuration-change, supply-chain, cascading-failure, rollback, interlock]
rules_at_time:
  - document: CrowdStrike content release process (as described in its External Technical Root Cause Analysis, 6 August 2024)
    clause: Sensor Content and Rapid Response Content
    paraphrase: Template Types are compiled into the sensor and ship with its release testing; Rapid Response Content (Template Instances in Channel Files) is configuration data, checked by a cloud Content Validator against the Template Type Definitions file and then deployed, without per-instance staged rollout
  - document: Microsoft Windows Hardware Quality Labs (WHQL) program
    clause: sensor release certification
    paraphrase: each Windows sensor release is certified through WHQL, the end of CrowdStrike's internal testing; during that testing the sensor uses the channel files current at certification
analogue:
  - record: ADR-0024
    clause: "§1, §2, §9"
    note: any artifact crossing from Build to Run, operational bundles included, needs a unanimous quorum; runtime subtraction (e-stop, deny=all) is not promotion
  - record: ADR-0030
    clause: "§1, §4"
    note: '"An incomplete slice makes attribute access error, and §1 turns that into a deny"; S is enforced at the decision point on every request, not only at build'
  - record: ADR-0045
    clause: "§2"
    note: a component is delegated if its failure can only subtract; a crash of every host adds no authority
  - record: ADR-0068
    clause: "TM10"
    note: supply chain (weights, tools, bundles) is bounded by promotion by digest
actors:
  - party: CrowdStrike
    role: vendor
    fault: honest-error
    note: its RCA lists six findings, among them a Content Validator logic error and no staged deployment of Template Instances
  - party: Content Validator
    role: safety-system
    fault: byzantine
    note: passed the new Template Instance by checking it against 21 defined inputs while the sensor supplied 20; it reported valid what was not
  - party: Falcon sensor Content Interpreter
    role: automation
    fault: crash
    note: an out-of-bounds read of the input array crashed Windows
  - party: Microsoft
    role: vendor
    fault: none-alleged
    note: estimated 8.5 million Windows devices affected and published recovery tooling
  - party: Customers' IT staff
    role: operator
    fault: none-alleged
    note: Microsoft described manual remediation documentation and scripts
detection:
  means: [customer, operator]
  latency: minutes
trace:
  - step: outside:schema-defined-twice
    at: February 2024, sensor 7.11
    note: the IPC Template Type defined 21 input fields in the Template Type Definitions file; the sensor's integration code supplied 20
  - step: outside:tests-use-wildcard-in-unused-field
    at: February to April 2024
    note: release tests, the Template Type stress test and the first IPC instances in the field all used a wildcard in field 21, so the mismatch was never exercised
  - step: outside:validator-checks-against-definition-not-code
    at: 19 July 2024
    note: two new IPC Template Instances; one used a non-wildcard criterion in field 21. The Content Validator assessed it against 21 inputs and passed it
  - step: outside:content-promoted-fleet-wide-without-staging
    at: 04:09 UTC
    note: the new Channel File 291 reached Windows hosts running sensor 7.11 or later that were online
  - step: outside:interpreter-error-crashes-host
    at: next IPC notification on each host
    note: reading the 21st value went past the end of a 20-entry array; the exception crashed Windows
  - step: outside:content-reverted
    at: 05:27 UTC
    note: hosts that came online after the revert, or were not connected in the window, were not affected
  - step: outside:manual-remediation-per-host
    at: from 19 July
    note: by 29 July about 99% of Windows sensors were online compared with before the update, by CrowdStrike's week-over-week count
counterfactual:
  by: CrowdStrike's own mitigations, read as a floor that fails closed on a missing input and a promotion in rings
  trace:
    - step: Decide
      at: next IPC notification
      note: FloorComposition.tla's decision with a slice that drops an attribute; the engine errors
    - step: outside:interpreter-error-is-refusal-not-crash
      at: same
      note: CrowdStrike's runtime bounds check; in TOPAK an error is a deny (ADR-0030 §1), on the request and not on the host
    - step: outside:ring-promotion-with-bake-in
      at: 04:09 UTC onward
      note: canary, then successive rings with bake-in time and rollback; no module has a ring
  holds: [FloorErrorIsDeny, AdmitImpliesFloorPermit]
outcome:
  by: CrowdStrike (preliminary Post Incident Review and External Technical Root Cause Analysis)
  date: 2024-08-06
  summary: >-
    CrowdStrike found that the IPC Template Type, introduced with sensor 7.11 in February 2024, defined 21 inputs
    while the code that invoked the Content Interpreter supplied 20; that tests had used wildcards in the 21st field;
    that the Content Validator assessed the new instance against 21 inputs; that the Content Interpreter had no
    runtime bounds check on the input array; and that Template Instances should have staged deployment. It says the
    bug is not an arbitrary memory write and, with a third-party review, that it is not exploitable. The content was
    released at 04:09 UTC and reverted at 05:27 UTC.
  aftermath: >-
    Compile-time validation of input counts (in production 27 July 2024); runtime bounds checks in the Content
    Interpreter (25 July) and a hotfix for sensors 7.11 and later (by 9 August); non-wildcard tests for every field
    of every Template Type; new Content Validator checks; testing of every new Template Instance; staged deployment
    of Template Instances through canary and successive rings with bake-in; customer control over where and when
    Rapid Response Content deploys, with release notes; two independent third-party code reviews and a review of the
    end-to-end quality process.
  effect_reversed: partial
model:
  modules: [FloorComposition, RulesFloorNV_rev5, FloorRouting, proposed:StagedPromotion]
  properties: [FloorErrorIsDeny, AdmitImpliesFloorPermit, P1_Unanimity, NoWideningWithoutIssuance]
  mutations: [M_ERR, M_FAILOPEN]
  records: [ADR-0024, ADR-0030, ADR-0045, ADR-0007, ADR-0050, ADR-0059, ADR-0068]
  findings: [TM10, CR-37]
  fault_class: a validator that reported valid what was not, and content promoted to every host at once; the failure was a crash, which only subtracts
sources:
  - https://www.crowdstrike.com/wp-content/uploads/2024/08/Channel-File-291-Incident-Root-Cause-Analysis-08.06.2024.pdf
  - https://www.crowdstrike.com/en-us/blog/falcon-content-update-preliminary-post-incident-report/
  - https://blogs.microsoft.com/blog/2024/07/20/helping-our-customers-through-the-crowdstrike-outage/
verified: 2026-11-12
---

## Summary

With sensor 7.11 in February 2024, CrowdStrike introduced a Template Type for detections on Windows interprocess
communication. Its definition named 21 input fields; the sensor code that invoked the Content Interpreter supplied
20. Release testing, a stress test of the Template Type, and the first IPC Template Instances in the field all used
a wildcard in the 21st field, so the difference was never exercised.

On 19 July 2024 at 04:09 UTC CrowdStrike released two new IPC Template Instances as Rapid Response Content in Channel
File 291. One used a non-wildcard criterion for the 21st field. The Content Validator assessed it on the expectation
of 21 inputs and passed it. Windows hosts running sensor 7.11 or later that were online received it; at the next IPC
notification the Content Interpreter read past the end of its 20-entry input array, and Windows crashed. CrowdStrike
reverted the content at 05:27 UTC. Mac and Linux hosts were not affected.

Microsoft estimated that 8.5 million Windows devices were affected, under one percent of all Windows machines, and
published manual remediation documentation and scripts. CrowdStrike reported that by 29 July about 99% of Windows
sensors were online compared with the week before the update.

## Defensive position

**CrowdStrike's RCA** sets out the case for the design it had:

- Rapid Response Content exists to respond to threats "at operational speed" without changing sensor code; it is
  configuration data, "not code or a kernel driver".
- The Template Type had been developed and tested under the standard Sensor Content process, and instances of it had
  been deployed successfully before. The instances were released on the strength of that testing, the Content
  Validator's checks, and prior IPC deployments (the preliminary review).
- The mismatch evaded "multiple layers" of build validation and testing; the RCA attributes the crash to the
  confluence of three issues, not to one.
- The kernel driver is standard for security products on Windows, as Microsoft's David Weston also wrote.

## Adversarial position

No adversary is involved: CrowdStrike states the bug is not exploitable, with a third-party review. The case against
the process is made in **CrowdStrike's own findings**:

- The number of fields was not validated at sensor compile time.
- The Content Interpreter had no runtime bounds check on its input array.
- The Content Validator contained a logic error.
- Template Instances were not tested within the Content Interpreter, and were not deployed in stages.

## Outcome

CrowdStrike's preliminary Post Incident Review and its External Technical Root Cause Analysis (6 August
2024) are the findings on record. The RCA lists six findings, each with mitigations: compile-time validation of input
counts, runtime bounds checks and a hotfix, wider test coverage, new validator checks, testing of every Template
Instance, and staged deployment through canary and rings with bake-in, with customer control over where and when
Rapid Response Content lands. Two independent vendors were engaged to review the sensor code and the quality process.
The content was reverted after 78 minutes. Hosts that had already crashed needed remediation, for which Microsoft published manual documentation and scripts.

## Analysis

**In TOPAK this is a floor that read an attribute the lift did not supply.** ADR-0030 §4 says the entity slice the
lift supplies is complete for every entity the floor can reference, and that an incomplete slice "makes attribute
access error, and §1 turns that into a deny". The Template Instance is a policy; the sensor's 20 inputs are the lift;
field 21 is the missing attribute. FloorComposition.tla models exactly this: the slice may drop an attribute, and
`FloorErrorIsDeny` holds unless `M_ERR` (the mechanism takes the engine's answer, ignoring the error) or `M_FAILOPEN`.
The difference is where the error lands. In TOPAK an evaluation error denies one request. In the sensor it was an
out-of-bounds read in the kernel. CrowdStrike's fix, a bounds check plus a check that the array size matches the
expected count, is ADR-0030 §1 written in C++.

**Two copies of one schema.** The Content Validator checked against the definitions file; the sensor ran on its
code. ADR-0030 §4 says S is enforced at the decision point on every request, and that "build-time use of S is not
sufficient". That is the rule this incident broke: a build-time check against one copy of the type while the run-time
used another. TOPAK ships S with the floor in a mechanism release, which keeps one copy. It would not have checked
that a bundle's validator agrees with the code that evaluates the bundle, since the validator is a Build gate, and
ADR-0050 §4 records gate evidence as an operator's assertion (`AttestGates`) whose truth is not known.

**The failure only subtracted, so TOPAK would score it as safe.** No host did anything its rules forbade; every host
did nothing. ADR-0045 §2's test, "failure can only subtract", passes. ADR-0024 §9 treats a fleet-wide
`bundle(deny=all)` as a local runtime subtraction, not a promotion. The corpus's safety properties all hold through
this incident; what failed is availability, and CR-37 notes that the formal layer has almost no liveness. This is the
honest place for the pattern to stop: TOPAK's posture under a fault is to stall, and a stall of 8.5 million hosts is
what a fail-closed design produces when the fault is everywhere at once. A kernel sensor that refused every IPC call
on a missing field might have been no better than one that crashed.

**Promotion is all at once.** Under ADR-0024 §1 Channel File 291 would be an artifact crossing into Run, promoted by
a unanimous quorum after the gates (`P1_Unanimity` in RulesFloorNV_rev5), and FloorRouting.tla would route a content
change that only narrows as an ordinary promotion. A unanimous quorum of reviewers who all trust the same validator
adds nothing here: CrowdStrike's own reviewers did. What CrowdStrike added afterwards is a ring: canary, then wider
rings, each with bake-in time and telemetry, and rollback. No record or module has one. `proposed:StagedPromotion`
would make a promotion's reach a field of the tally, advanced ring by ring, with the property that no ring is reached
before the previous one's bake-in has elapsed without a finding (ADR-0007: a finding may stop the advance, never
cause it). That also answers the customer-control mitigation: a deployment that declines a ring is a narrowing, which
ADR-0059's charters already allow.

**Supply chain, TM10.** The row's bound is "promotion by digest". A digest proves the file is the one promoted. It
says nothing about whether the file is well-typed against the code that will read it.

**Outside steps.** `schema-defined-twice`, `tests-use-wildcard-in-unused-field`,
`validator-checks-against-definition-not-code`, `content-promoted-fleet-wide-without-staging`,
`interpreter-error-crashes-host`, `content-reverted` and `manual-remediation-per-host`. The two that point at
TOPAK's own gaps are the staging step and the validator that checks a different copy of the type.
