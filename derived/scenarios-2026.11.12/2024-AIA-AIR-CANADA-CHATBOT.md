---
id: 2024-AIA-AIR-CANADA-CHATBOT
title: Moffatt v. Air Canada, 2024 BCCRT 149 — an airline answerable for what its website chatbot told a customer
kind: incident
date: 2024-02-14
sector: ai-agents
setting: A support chatbot on Air Canada's website, a bereavement-fare query from British Columbia, and the BC Civil Resolution Tribunal
concerns: [accountability, actuation, human-in-the-loop, sensing, authority]
rules_at_time:
  - document: Air Canada "Bereavement travel" web page (as described in the decision, para 16-17)
    clause: bereavement policy
    paraphrase: the policy does not apply to requests for bereavement consideration made after travel is completed
  - document: Tort of negligent misrepresentation, Queen v. Cognos Inc., 1993 (SCC), as applied in the decision (para 25)
    clause: elements
    paraphrase: a duty of care, an untrue, inaccurate or misleading representation, made negligently, reasonably relied on, causing damage
  - document: Civil Resolution Tribunal Act (British Columbia)
    clause: s. 118
    paraphrase: the tribunal's small-claims jurisdiction; it must apply principles of law and fairness (s. 2)
analogue:
  - record: ADR-0015
    clause: Decision
    note: effects are exactly tool invocations and principal emissions; a reply to a customer crosses the boundary, so it is an effect with a signed, ordered authorizing predecessor
  - record: ADR-0024
    clause: "§1 (A3)"
    note: a promotion seats; the principal's first lease is granted when the deployer's quorum completes the tally, so an agent's authority is the deployer's decision on the record
  - record: ADR-0007
    clause: Decision
    note: semantic judgment is never a lift; whether a statement is true is not decided in the admit path
  - record: ADR-0066
    clause: "§3"
    note: a stack's report to a person is ingress to that person, labelled untrusted, and enables nothing; stated for a person inside the deployment at a release seat
  - record: ADR-0056
    clause: "§10"
    note: how a user's request becomes a task, and a subject's consent, are not covered
actors:
  - party: Jake Moffatt
    role: user
    fault: none-alleged
    note: applicant; relied on the chatbot's answer
  - party: Air Canada
    role: vendor
    fault: contested
    note: argued it was not liable for the chatbot's information; the tribunal found negligent misrepresentation
  - party: Air Canada website chatbot
    role: automation
    fault: byzantine
    note: stated that a reduced bereavement rate could be claimed within 90 days of ticketing after travel; the linked policy page said otherwise. Air Canada gave no information about its nature (para 14)
  - party: Civil Resolution Tribunal (Tribunal Member Christopher C. Rivers)
    role: court
    fault: none-alleged
detection:
  means: [customer]
  latency: months
trace:
  - step: outside:customer-asks-agent-about-terms
    at: 11 November 2022
    note: the day the applicant's grandmother died, on Air Canada's website
  - step: Report
    at: 11 November 2022
    note: RunCoupling.tla's principal emission, standing for the chatbot's reply; admitted, coupled and recorded in TOPAK, and nothing checks its content
  - step: outside:statement-contradicts-published-policy
    at: 11 November 2022
    note: the reply said a reduced bereavement rate could be claimed within 90 days of ticketing, including after travel; its own hyperlink led to a page saying it could not
  - step: outside:person-relies-and-commits
    at: 11 and 16 November 2022
    note: booked Vancouver to Toronto ($794.98) and Toronto to Vancouver ($845.38)
  - step: outside:claim-refused-downstream
    at: 17 November 2022 to February 2023
    note: applied within the 90 days; on 8 February 2023 an Air Canada representative admitted the chatbot had given "misleading words"
  - step: outside:deployer-held-to-agent-statement
    at: 14 February 2024
    note: the tribunal's decision
outcome:
  by: BC Civil Resolution Tribunal
  date: 2024-02-14
  summary: >-
    The tribunal found negligent misrepresentation. Air Canada owed a duty of care; its argument that it could not be
    liable for information from a chatbot amounted to saying the chatbot was "a separate legal entity", which the
    tribunal called "a remarkable submission" and rejected: the chatbot is "still just a part of Air Canada's website"
    (para 27). Air Canada did not explain why its bereavement page was more trustworthy than its chatbot, or why a
    customer should double-check one part of its website against another (para 28); the reliance was reasonable
    (para 29). The tariff defence failed because Air Canada did not produce the tariff (para 31).
  aftermath: >-
    Air Canada was ordered to pay $812.02 within 14 days: $650.88 in damages, $36.14 in pre-judgment interest and $125
    in tribunal fees. Its claimed $200 coupon set-off was refused. Air Canada's February 2023 email said it had noted
    the issue so that the chatbot could be updated; what was changed is not in the sources read.
  effect_reversed: partial
model:
  modules: [RunCoupling, RunSeats, Labels, proposed:Representation]
  properties: [NoEffectWithoutLiveObserver, ObserversConsultAndReport, OnlyThinkersActuate]
  mutations: []
  records: [ADR-0015, ADR-0024, ADR-0007, ADR-0066, ADR-0056, ADR-0040, ADR-0004, ADR-0047]
  findings: [TM9, CR-38]
  fault_class: an agent's statement to an outside person, admitted as an effect, false against the deployer's own published terms; liability fell on the deployer
sources:
  - https://decisions.civilresolutionbc.ca/crt/crtd/en/525448/1/document.do
  - https://globalnews.ca/news/10297307/air-canada-chatbot-error-bc-ruling/amp
verified: 2026-11-12
---

## Summary

On 11 November 2022 Jake Moffatt's grandmother died in Ontario. That day Moffatt used a support chatbot on Air
Canada's website to ask about bereavement fares. Its reply, in a screenshot before the tribunal, said that a passenger
who needed to travel immediately or had already travelled could submit the ticket for a reduced bereavement rate
within 90 days of the date it was issued. The words "bereavement fares" in the reply linked to Air Canada's
"Bereavement travel" page, which said the policy did not apply to requests made after travel was completed.

Relying on the chatbot, Moffatt booked Vancouver to Toronto on 11 November ($794.98) and Toronto to Vancouver on 16
November ($845.38). A telephone agent had said the bereavement fare would be about $380 each way. Moffatt applied for
the reduced rate on 17 November and pursued it into February 2023. On 8 February 2023 an Air Canada representative
replied that the chatbot had used "misleading words", pointed to the linked page, and said the issue had been noted
so the chatbot could be updated. Moffatt claimed $880 before the Civil Resolution Tribunal.

## Defensive position

**Air Canada's case**, as the tribunal recorded it (para 4, 27, 28, 31, 35, 41):

- Moffatt did not follow the proper procedure to request bereavement fares and could not claim them retroactively.
- It could not be held liable for information provided by one of its agents, servants or representatives, including
  a chatbot.
- The correct information was available on another part of its website, the page the chatbot linked to.
- Terms of its Domestic Tariff limited its liability.
- It had offered a $200 coupon as a goodwill gesture, which should be set off against any award.

## Adversarial position

**Moffatt's case** (para 3, 29, 30): they relied on the chatbot to give accurate information about Air Canada's own
policy, and would not have flown at the last minute at full fare had they known; Air Canada should refund the
difference between the fares paid and the bereavement fares.

## Outcome

The tribunal (Tribunal Member Christopher C. Rivers, 14 February 2024) found negligent misrepresentation. It held
that a chatbot "is still just a part of Air Canada's website" and that "it should be obvious to Air Canada that it is
responsible for all the information on its website", whether "from a static page or a chatbot" (para 27). Air Canada
had not taken reasonable care to ensure its chatbot was accurate, and there was "no reason why Mr. Moffatt should
know that one section of Air Canada's webpage is accurate, and another is not" (para 28-29). Its tariff defence
failed because it did not file the tariff. Drawing an adverse inference from Air Canada's lack of evidence, the
tribunal took $380 as the bereavement fare and awarded $650.88 in damages, $36.14 in interest and $125 in fees,
$812.02 in all, refusing the coupon set-off. Global News reported the decision on 15 February 2024. The fares were
paid; the award compensated the difference.

## Analysis

**TOPAK agrees with the tribunal by construction, and that is the first point.** Air Canada's argument, in the
tribunal's words, made the chatbot "a separate legal entity". TOPAK has no such entity. Under ADR-0024 §1 (A3) a
principal is seated by a promotion, and its first lease is granted when the deployer's quorum completes the tally.
Under ADR-0015 the reply is a principal emission or a tool invocation, an effect with a signed, consensus-ordered
authorizing predecessor. Every statement the agent makes is admitted under authority the deployer voted, and the log
shows it. TOPAK treats the agent as Byzantine toward the deployer; toward the customer, the agent is the deployer.

**What TOPAK would and would not have changed.** It would have recorded the reply (`Report`, coupled to a live
Observer by `NoEffectWithoutLiveObserver`), attributed it to a seat (`ObserversConsultAndReport` and
`OnlyThinkersActuate` in RunSeats say which seat may emit what), and kept the admit facts beyond erasure. It would
not have stopped the reply. Whether a sentence about bereavement fares is true is a semantic judgment, and ADR-0007
keeps those out of the admit path. An Observer that compared the reply with the policy page could raise a finding
afterwards; findings subtract and come too late for a customer who has already bought a ticket. No mutation applies:
nothing in any module is violated by an admitted, false statement.

**The person deceived is outside the deployment.** ADR-0066 §3 handles an agent's report to a person: it is ingress
to that person, labelled `untrusted`, and enables nothing. That protection is for a person inside the deployment at a
release seat. A customer reading a website gets no label. TM9 (deception of a person's perception) says of a
deceived person at a release seat that it "is a semantic failure. Nothing here sees it". Moffatt is the same case one
step further out, where the corpus does not reach. ADR-0056 §10 likewise leaves out how a user's request becomes a
task, and a subject's consent; no record says what a deployment owes a person it serves (FINDINGS_TOPAK.md SF-26).

**What would have made the statement checkable.** The contradiction was between two outputs of the same deployer, a
page and a chatbot. If statements of the deployer's terms were delivered as quotations by handle of a pinned
object in the Run root (ADR-0040 §1 `Consult`; ADR-0047 §2-3 handles), rather than written by the model, then "the
reply cites the policy object" is a syntactic fact the mechanism can check, and only the model's paraphrase is
untrusted. `proposed:Representation`: a reply that states a term of the deployer's own policy carries a handle to
the pinned policy object, and an outward reply that states a term without one is refused or labelled. Whether a
reply "states a term" is itself semantic, so the rule can only be a narrowing that a deployment opts into, with the
Observer finding the misses.

**The record and the claim.** The case turned on what the chatbot said, proved by the customer's screenshot. Under
ADR-0004 the text of an emission is cognitive payload, kept by hash and pointer in a store built for deletion, while
the admit facts survive. The digest on the log could confirm a screenshot as long as the payload is kept, and not
after. CR-38 notes the corpus has not said which way it leans between forensic retention and erasure; a deployer
facing liability for what its agent said has a stake in that answer.

**Outside steps.** `customer-asks-agent-about-terms`, `statement-contradicts-published-policy`,
`person-relies-and-commits`, `claim-refused-downstream`, `deployer-held-to-agent-statement`.
