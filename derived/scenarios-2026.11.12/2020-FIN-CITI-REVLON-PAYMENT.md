---
id: 2020-FIN-CITI-REVLON-PAYMENT
title: Citibank and Revlon's lenders, 11 August 2020 — three approvals of a screen that did not mean what it showed
kind: incident
date: 2020-08-11
sector: fintech
setting: Citibank, N.A., administrative agent on Revlon's 2016 term loan, paying lenders through its Flexcube loan software, New York
concerns: [human-in-the-loop, quorum, interface-types, actuation, rollback, accountability]
rules_at_time:
  - document: Citibank's payment procedure, as the Second Circuit described it
    clause: maker, checker, approver
    paraphrase: a payment was prepared by a maker and reviewed by a checker, both employees of the outside firm Wipro, and released by a Citibank senior manager as approver
  - document: Flexcube, as configured at Citibank
    clause: suppressing a principal payment
    paraphrase: to route principal to an internal wash account rather than to lenders, the PRINCIPAL field and also the FRONT and FUND fields had to be set to the wash account; only PRINCIPAL was set
  - document: New York law, Banque Worms v. BankAmerica International (N.Y. 1991)
    clause: discharge for value
    paraphrase: a creditor who receives a mistaken payment may keep it if it was owed the money and had no notice of the mistake; the Second Circuit held the defence requires the debt to be presently payable
  - document: Revlon 2016 term loan agreement
    clause: maturity
    paraphrase: a seven-year loan of about $1.8 billion, not due until September 2023
analogue:
  - record: ADR-0066
    clause: "§3, §5"
    note: the person is the actor and composes the act; the mechanism checks none of the person's judgment, and "HITL is a key and not a judgment" unless the person can see what the act requires
  - record: ADR-0066
    clause: Open obligations
    note: "what a person at a release seat must be shown, which no record states"
  - record: ADR-0024
    clause: "Consequences, Negative"
    note: "Unanimous humans reading the same vacuous gate output fail together"
  - record: ADR-0049
    clause: "§3, §4"
    note: an entry's inputs are typed and each field is marked checked or claimed; what a combination of fields does is the tool's
  - record: ADR-0062
    clause: "§6"
    note: nothing a governor permitted is void; a check that fails afterwards is a finding and only subtracts
actors:
  - party: Citibank, N.A.
    role: operator
    fault: honest-error
    note: both courts treated the payment as a mistake; it recalled the funds the next day
  - party: The maker and the checker (Wipro employees)
    role: operator
    fault: honest-error
    note: believed setting PRINCIPAL alone would route principal to the wash account
  - party: The approver (a Citibank senior manager)
    role: supervisor
    fault: honest-error
    note: held the same belief and released the payment
  - party: Flexcube
    role: automation
    fault: honest
    note: did what its fields, as set, said
  - party: Lenders that kept the funds (ten advisers for 126 lenders, about $500 million)
    role: counterparty
    fault: contested
  - party: Lenders that returned the funds (about $385 million)
    role: counterparty
    fault: honest
  - party: US District Court, SDNY (Judge Jesse Furman)
    role: court
    fault: none-alleged
  - party: US Court of Appeals for the Second Circuit (Leval, Sack, Park)
    role: court
    fault: none-alleged
detection:
  means: [operator]
  latency: hours
trace:
  - step: outside:roll-up-interest-payment
    at: 11 August 2020
    note: Citibank intends to pay about $7.8 million of accrued interest to the 2016 lenders as part of a roll-up
  - step: Activate
    at: 11 August 2020
    note: read as ADR-0066, three persons hold the keys that release the payment; Release activates one seat, and here three people each sign
  - step: outside:interface-misread
    at: 11 August 2020
    note: the maker sets PRINCIPAL to the wash account and leaves FRONT and FUND; checker and approver read the screen the same way
  - step: AdmitRelease
    at: 11 August 2020
    note: the approver releases; the act is a person's, and SignedByPerson holds
  - step: Fire
    at: 11 August 2020
    note: about $894 million goes to the lenders, the interest plus the whole outstanding principal, matching the debt to the penny; the calculation statements sent to lenders mention only interest
  - step: outside:recall-notice
    at: 12 August 2020
    note: Citibank discovers the error and sends recall notices; about $385 million comes back
  - step: CheckFails
    at: August 2020 to September 2022
    note: the mistake is a finding after the effect; ConflictIsAFinding says it voids nothing, and the remedy is a lawsuit, not a void
  - step: outside:court-orders-return
    at: 8 September 2022
    note: the Second Circuit vacates the district court's judgment that the lenders may keep about $500 million
outcome:
  by: US Court of Appeals for the Second Circuit
  date: 2022-09-08
  summary: >-
    After a bench trial the district court (Judge Furman, February 2021) held that the lenders who refused to return
    about $500 million could keep it under New York's discharge-for-value defence: they were owed the money and
    were justified in believing the payment intentional, it being "borderline irrational" to think a sophisticated
    bank had made a nearly $1 billion mistake. The court called the error one of the "biggest blunders in banking
    history". The Second Circuit (Citibank, N.A. v. Brigade Capital Management, No. 21-487) vacated and remanded on
    two independent grounds: the lenders were on inquiry notice of the mistake, given no prepayment notice, Revlon's
    apparent insolvency, loan participations trading at 20 to 30 cents, and an exchange offer days earlier; and the
    defence applies only to a debt "presently payable", which a loan due in 2023 was not. It kept the injunction
    barring disposal of the funds.
  aftermath: >-
    Citigroup had said of the district ruling, "We strongly disagree with this decision and intend to appeal". The
    sources read stop at the remand, and what followed it is not in them.
  effect_reversed: partial
model:
  modules: [Release, RulesFloorNV_rev5, proposed:ActDisplay]
  properties: [IrreversibleIsAPersons, SignedByPerson, ConflictIsAFinding, P1_Unanimity, ReleaseNeverCoupled]
  mutations: [M_VOID, M_AGENTPROPOSES]
  records: [ADR-0066, ADR-0024, ADR-0049, ADR-0048, ADR-0062, ADR-0032, ADR-0037]
  findings: [TM9, TM7, CR-17]
  fault_class: a human-approval quorum, every member honest and every member wrong in the same way, about what an interface would do
sources:
  - https://caselaw.findlaw.com/us-2nd-circuit/1911624.html
  - https://abc17news.com/money/2021/02/17/citibank-cant-get-back-500-million-it-wired-by-mistake-judge-rules/
verified: 2026-11-12
---

## Summary

Citibank was administrative agent on Revlon's $1.8 billion, seven-year 2016 term loan, due in September 2023. On 11
August 2020, during a roll-up transaction, it meant to pay the lenders about $7.8 million of accrued interest. The
payment was prepared in Flexcube by a maker and a checker, both employees of the outside firm Wipro, and released by
a Citibank senior manager as approver. All three believed that setting the PRINCIPAL field to an internal wash
account would keep the principal inside Citibank. The FRONT and FUND fields also had to be set, and were not.

Flexcube paid about $894 million: the interest and the whole outstanding principal, which matched what the lenders
were owed to the penny. The calculation statements sent to lenders mentioned only interest. Citibank noticed the
next day and sent recall notices. About $385 million was returned. Ten defendants, advisers for 126 lenders
holding about $500 million, refused. Revlon was then thought deeply insolvent, and participations in the loan
traded at 20 to 30 cents on the dollar.

## Defensive position

Two dispositions are defended here, and the dispute is the second.

- **Citibank's process.** Three people, two firms, each signing. The courts treated the payment as an honest
  mistake, and Citibank moved to recover the next day.
- **The lenders who kept the funds**, as the district court accepted: under *Banque Worms* a creditor who receives
  what it is owed, without notice of a mistake, may keep it. The amount matched the debt "to the penny". Internal
  chats dated the day after showed they did not know of the mistake until Citibank's notices. Believing that a
  sophisticated bank had made a nearly $1 billion mistake that had never happened before would have been "borderline
  irrational".

## Adversarial position

- **Citibank**: "We strongly disagree with this decision and intend to appeal."
- **The Second Circuit** held the lenders on inquiry notice. There was no notice of prepayment; Revlon appeared
  insolvent; Revlon could have retired the debt more cheaply in the market; an exchange offer four days earlier had
  been made to avoid acceleration; and a call to Citibank would have revealed the error.
  Independently, a creditor "may not invoke the discharge-for-value rule unless the debt at issue is presently
  payable".

## Outcome

The district court ruled for the lenders in February 2021. On 8 September 2022 the Second Circuit vacated that
judgment and remanded, holding the defence unavailable on both grounds, and kept in place the injunction against
disposing of the funds. The effect was reversed in part: about $385 million returned voluntarily, and about $500
million made recoverable by the appeal. The sources read do not say what happened after the remand.

## Analysis

**This is ADR-0066's human-in-the-loop, run as written, and it failed.** ADR-0066 defines HITL by its enabling
condition: an irreversible effect is "enabled only by a signed act of a person, made for that one effect". Citibank
had three. In `Release` terms each step held: `SignedByPerson`, the act was a person's; `IrreversibleIsAPersons`, the
conjunction; `ReleaseNeverCoupled`, nothing waited on an agent. No mutation is needed to produce this trace. The
properties hold and the payment is still wrong, which is what ADR-0066 §5 says in advance: "Whether the act was right
is the person's judgment, and the mechanism checks none of it", and "HITL is a key and not a judgment unless a trained,
authorized person holds it and can see what the act requires." Revlon is that sentence's counterexample with names.

**What the person must be shown is the open obligation.** ADR-0066 lists "what a person at a release seat must be
shown, which no record states". Citibank's approvers saw a screen whose fields combined in a way they did not know:
PRINCIPAL without FRONT and FUND meant "pay". ADR-0066 §4 has the act name the entry, its inputs, the vehicle, the
fences and a tick of the plane. It does not have it name the effect: here, the amount each lender would receive. ADR-0049 types an
entry's inputs and marks each field checked or claimed; it says nothing about what a combination does. The
interlock checks key, certificate, vehicle, freshness and use, and every one of those passed.
`proposed:ActDisplay` would require the act to carry the effect it will produce, computed by the mechanism from the
entry and its inputs, and signed over: the person signs the outcome, not the form. That is a real addition, and it
may not be computable for every entry, which is why it is proposed and not assumed.

**Unanimity does not decorrelate.** ADR-0024's own consequences say it: "Correlated review failure is untouched.
Unanimous humans reading the same vacuous gate output fail together." `RulesFloorNV_rev5`'s `P1_Unanimity` makes every
grant seat a veto, and a veto is only as good as the voter's model. Maker, checker and approver held the same wrong
model of one form. Two firms did not make them independent. ADR-0037 §7 makes each a separate principal, which buys
attribution and nothing more here. The same mechanism that buys TOPAK protection against one Byzantine approver
buys nothing against three honest ones sharing a misconception, and the corpus says so.

**The agent-proposes design was not the fault.** ADR-0066 §3 rejects a design "in which an agent proposes and a
person approves", which `M_AGENTPROPOSES` models. Flexcube proposed nothing; the people composed the payment. The
failure was in the meaning of the interface, TM9's "deception of perception" without a deceiver: "A deceived person
at a release seat is a semantic failure. Nothing here sees it." CR-17 (operator proficiency presumed) is the matching
finding.

**Was the effect irreversible?** The district court said, in effect, yes; the Second Circuit said no. ADR-0066 §1
makes an effect class "a declaration, as a label is", and "an irreversible effect declared reversible is seen by
nothing here". This payment had no class until a court gave it one, two years later, and the two courts gave it
opposite ones. ADR-0032 §4's `T_irrev` for a wire is not a property of the wire. The corpus's position, that nothing a
governor permitted is void (ADR-0062 §6, `ConflictIsAFinding`, with `M_VOID` the mutation that breaks it), is the
right one for the mechanism: the remedy was a lawsuit, a new act by other parties, not a void. Where the pattern stops
is where the law decides what can be clawed back.
