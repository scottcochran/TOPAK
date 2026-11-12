---
id: 2016-FIN-BANGLADESH-SWIFT
title: Bangladesh Bank, February 2016 — authenticated SWIFT instructions from a captured host, and a printer that went quiet
kind: incident
date: 2016-02-04
sector: fintech
setting: Bangladesh Bank's SWIFT Alliance Access server and confirmation printer, Dhaka, and its dollar account at the Federal Reserve Bank of New York
concerns: [identity, monitoring, actuation, timing, containment, rollback]
rules_at_time:
  - document: Federal Reserve Bank of New York, statement of 9 March 2016
    clause: payment instructions
    paraphrase: the instructions it acted on were "fully authenticated by the SWIFT messaging system in accordance with standard authentication protocols"
  - document: Bangladesh Bank's SWIFT Alliance Access environment (BAE Systems' reconstruction)
    clause: confirmations
    paraphrase: SWIFT confirmation messages were printed for staff by the Alliance software's own print path, which the malware intercepted
analogue:
  - record: ADR-0039
    clause: "§2, §5"
    note: every effect-bearing Run admit needs a live cell Observer; coupling closes the dead, partitioned and starved cases and "cannot separate an honest Observer from a colluding one"
  - record: ADR-0038
    clause: "§4"
    note: no observer seat shares a device with a Thinker it watches
  - record: ADR-0028
    clause: "§1"
    note: admit decisions (F1) are control-plane facts, non-erasable; the record is the consensus log, not a host's database
  - record: ADR-0032
    clause: "§4"
    note: "W + L + D < T_irrev: propagation, detection latency and the human response budget must sum to less than the time to irreversibility"
  - record: ADR-0063
    clause: "§3, §4"
    note: a plane may have K_up effects outstanding and no more, so effects after a revocation are bounded in number, with no premise about time
  - record: ADR-0068
    clause: "TM3, TM7"
    note: a captured holder of a key can sign anything; "the mechanism cannot tell a person from a program holding the key"
actors:
  - party: The attackers
    role: attacker
    fault: byzantine
    note: unidentified at the time; BAE did not attribute; later attributed to North Korean actors by US prosecutors, per the secondary record
  - party: Malware on the SWIFT Alliance Access server
    role: automation
    fault: byzantine
    note: patched a two-byte check in liboradb.dll, deleted messages from the local database, rewrote balances and doctored printed confirmations (BAE)
  - party: Confirmation printer and its print path
    role: monitor
    fault: byzantine
    note: under the attacker's control; staff found it not working, took it for a routine fault, and it was not fixed until 6 February
  - party: Bangladesh Bank
    role: operator
    fault: contested
    note: its governor and two deputy governors lost their posts; it called the New York Fed's handling "a major lapse"
  - party: Federal Reserve Bank of New York
    role: counterparty
    fault: contested
    note: blocked 30 instructions, about $850 million, and paid five, about $101 million; says the instructions were fully authenticated
  - party: Deutsche Bank and a Sri Lankan bank
    role: counterparty
    fault: honest
    note: accounts differ; a misspelled beneficiary name raised suspicion at Deutsche Bank (Wikipedia), and a Sri Lankan bank halted the transfer at Bangladesh Bank's request (AFP); the $20 million was recovered
  - party: RCBC branch manager in Manila
    role: counterparty
    fault: byzantine
    note: convicted of money laundering in January 2019, per Wikipedia; the Philippine central bank fined RCBC
  - party: SWIFT
    role: vendor
    fault: none-alleged
detection:
  means: [counterparty, operator]
  latency: days
trace:
  - step: outside:host-captured
    at: before 4 February 2016
    note: the attackers controlled the server running SWIFT Alliance Access; how they got in was unknown to BAE in April 2016
  - step: outside:local-check-patched
    at: until 6 February
    note: malware replaces a conditional jump with two no-ops in liboradb.dll, so a failed check is treated as passed
  - step: Actuate
    at: 4 to 5 February
    note: 35 instructions, close to $951 million, sent under Bangladesh Bank's SWIFT credentials while its offices were closed for the weekend; each verifies, as a captured key's signature does (TM3)
  - step: outside:local-record-erased
    at: 4 to 6 February
    note: the malware deletes the transactions from the Alliance database tables and rewrites reported balances
  - step: outside:monitor-silence-read-as-routine
    at: before 6 February
    note: the printer is not producing confirmations; staff assume "a common problem just like any other day"; under ADR-0039 a silent Observer stalls its Thinker, and here nothing waited on it
  - step: outside:counterparty-screen
    at: 4 to 5 February
    note: the New York Fed blocks 30 instructions over questions about the recipients and pays five, $81 million to the Philippines and $20 million to Sri Lanka
  - step: outside:stop-request-unanswered
    at: 6 February, 1:30 p.m.
    note: after the printer is fixed and Fed queries are seen, the bank e-mails, faxes and phones the New York Fed, which is closed for the weekend
  - step: outside:stop-request-too-late
    at: 8 February
    note: formal stop requests to six banks; RCBC receives its request a day late, during the Chinese New Year holiday, after about $58.15 million has been withdrawn
  - step: outside:partial-recovery
    at: 2016 onward
    note: the Sri Lankan $20 million recovered; of the $81 million, about $15 million recovered as of 2025, per Wikipedia
counterfactual:
  by: an Observer seated on another device, reading the mechanism's own record of each Actuate, with the bank's SWIFT instructions as effect-bearing admits coupled to it
  trace:
    - step: Actuate
      at: 4 February
      note: the first instructions are admitted and recorded in the consensus log, beyond the host's reach
    - step: RefuseEffect
      at: 4 February
      note: if the Observer goes silent or falls K behind, further instructions are refused; nothing waits for staff to notice a printer
  holds: [NoEffectWithoutLiveObserver, UnreadEffectsBounded]
outcome:
  by: Federal Reserve Bank of New York (statement); Bangko Sentral ng Pilipinas; Philippine courts; US and New York courts (pending)
  date: 2016-03-09
  summary: >-
    No official investigation report is in what was read. The New York Fed said on 9 March 2016 that it had found no
    evidence of any attempt to penetrate Federal Reserve systems and that the instructions were fully authenticated
    by SWIFT. BAE Systems' analysis of April 2016 described malware built for that SWIFT Alliance Access deployment:
    it patched a check, deleted messages, altered balances and replaced printed confirmations, and BAE declined to
    attribute it. Bangladesh Bank's governor and two deputy governors lost their posts. The Philippine central bank
    fined RCBC PHP 1 billion on 5 August 2016, and a former RCBC branch manager was convicted of money laundering on
    10 January 2019, upheld on appeal in 2023, per Wikipedia. Bangladesh Bank sued RCBC in US federal court in 2019
    and in New York state court in 2020.
  aftermath: >-
    SWIFT created its Customer Security Programme and controls framework. In February 2019 the Federal Reserve
    pledged to help Bangladesh Bank recover the money and SWIFT agreed to help rebuild its infrastructure, per
    Wikipedia, which also records that the US charged a North Korean programmer over the theft.
  effect_reversed: partial
model:
  modules: [RunCoupling, Coupling, Observers, Outstanding, NonComposition, proposed:CounterpartyScreen]
  properties: [NoEffectWithoutLiveObserver, UnreadEffectsBounded, EffectsAfterRevocationBounded, NC2]
  mutations: [M_NOCOUPLE, M1]
  records: [ADR-0039, ADR-0038, ADR-0028, ADR-0032, ADR-0063, ADR-0050, ADR-0065, ADR-0068]
  findings: [TM3, TM7, TM11, CR-2]
  fault_class: a captured host holding a valid credential, with the monitor on the same host and fed by it; detection by a counterparty, a misspelling and a printer fault
sources:
  - https://baesystemsai.blogspot.com/2016/04/two-bytes-to-951m.html
  - https://www.newyorkfed.org/newsevents/statements/2016/0311-2016
  - https://www.securityweek.com/faulty-printer-implicated-81-million-bangladesh-bank-heist/
  - https://fortune.com/2016/03/22/bangladesh-bank-new-york-fed-major-lapse/
  - https://en.wikipedia.org/wiki/Bangladesh_Bank_robbery
verified: 2026-11-12
---

## Summary

Between 4 and 5 February 2016, while Bangladesh Bank's offices were closed for the weekend, 35 SWIFT payment
instructions for close to $951 million were sent from the bank's SWIFT Alliance Access system to the Federal Reserve
Bank of New York, which holds its dollar account. The New York Fed blocked 30, worth about $850 million, over
questions about the recipients, and paid five: $81 million to accounts at RCBC in the Philippines and $20 million to
Sri Lanka. The Sri Lankan transfer was halted, after a misspelled beneficiary name raised suspicion at Deutsche Bank
(per Wikipedia) and at Bangladesh Bank's request (per AFP), and the money was recovered.

BAE Systems later analysed malware it believed was used. It registered as a service on the SWIFT server, replaced a
two-byte conditional jump in `liboradb.dll` so that a failed check passed, watched for login events, deleted the
transactions from the Alliance database, rewrote reported balances, and intercepted confirmation messages
to print doctored versions, overwriting the print files afterwards. It ran until 6 a.m. on 6 February.

Staff found the confirmation printer not working. Bangladesh Bank's joint director later told police: "Since such
glitches happened before, we thought it was a common problem just like any other day." Engineers could not fix it
until 6 February, a day after the New York Fed had sent queries about four transactions. The bank tried to reach the Fed by
e-mail, fax and phone; it was closed for the weekend. On Monday 8 February formal stop requests went to six banks.
RCBC got its request a day late, during the Chinese New Year holiday, by when about $58.15 million had been withdrawn.
The funds moved on through Philippine accounts to casinos, per the Philippine anti-money-laundering council as
reported by AFP.

## Defensive position

- **The New York Fed** (statement of 9 March 2016): no evidence of any attempt to penetrate Fed systems; the
  instructions were "fully authenticated by the SWIFT messaging system in accordance with standard authentication
  protocols"; it had been working with the bank since. It blocked 30 of 35 and, Fortune reported, maintained it
  was not guilty of wrongdoing.
- **Bangladesh Bank's staff** (the joint director's police complaint, reported by AFP): printer faults were common,
  the SWIFT system's failure was recognized on 6 February, and the bank then tried every channel to reach a Fed that
  was closed.

## Adversarial position

- **Bangladesh Bank**, in an internal document of 13 March reported by Bloomberg and cited by Fortune: "We view this
  as a major lapse on the part of" the New York Fed, and it sought grounds for recompense. Bangladesh's finance
  minister threatened to sue the Fed, per AFP.
- **Against the bank**: its governor and two deputy governors lost their posts, and the government removed a senior
  banking official, per AFP. Bangladesh Bank in turn sued RCBC in the US, alleging "a massive conspiracy", per
  Wikipedia.

## Outcome

There is no official report in what was read; the outcome is a set of separate acts. The New York Fed stood by its
processing. The Philippine central bank fined RCBC, and a former RCBC branch manager was convicted of money laundering
in 2019. Bangladesh Bank's suits against RCBC in New York were proceeding at Wikipedia's last account. SWIFT launched
its Customer Security Programme. Of the $101 million paid, the $20 million to Sri Lanka was recovered, and of the $81
million about $15 million had been recovered as of 2025, per Wikipedia.

## Analysis

**A valid signature from a captured host is TM3 and TM7.** The instructions verified because they were signed with
the bank's own credentials. ADR-0068's TM3 is a captured holder that can "sign any local record", and TM7 says "the
mechanism cannot tell a person from a program holding the key". TOPAK does not claim to see this. What it bounds is
how much a key can do: a lease has an alphabet and a count, and an intent a budget (ADR-0060 §2). Under ADR-0050 §4 an
operator's add needs a live peer, a second principal. Whether Bangladesh Bank's instructions needed two people is not
in what was read, so the entry claims nothing about it.

**The printer is a coupled Observer in all but the coupling.** Its job was to show staff each confirmation. When it
stopped, nothing else stopped: the system kept sending and the silence was read as routine. ADR-0039 §2 makes every
effect-bearing Run admit wait on a live cell Observer, and `RunCoupling` proves `NoEffectWithoutLiveObserver`; the
trace is `M_NOCOUPLE`, which breaks it. Under coupling a dead or starved printer is a stall, and a stall is noticed
because work stops, not because someone checks a tray. That is CR-2's "detection fails open", closed in three of four
cases by ADR-0039.

**The fourth case is the one that happened.** The malware did not only silence the printer; BAE found it sending
doctored confirmations. An Observer that reports false clean output is a colluding Observer, TM11, and ADR-0039 §5
says coupling "cannot separate an honest Observer from a colluding one". What the corpus does have is placement and
source. ADR-0038 §4 forbids an observer seat on a device with the Thinker it watches; the printer's input came from
the very server the attacker held. And a TOPAK Observer reads the round topic and the mechanism's record, not the
Thinker's database. The malware's deletion of rows from the Alliance tables is, in TOPAK, the erasure of F1 admit
decisions, which ADR-0028 §1 makes a policy-floor denial; `NonComposition`'s `NC2`, which `M1` breaks, is the shape. Deleting a
host's copy is not erasing the log. The counterfactual rests on both: an Observer elsewhere, reading a record the
host cannot rewrite. It does not survive an attacker who also holds the Observer.

**The weekend is ADR-0032 §4's budget, failed.** `W + L + D < T_irrev`. Here `L`, detection, was about a day
(the printer not fixed, and the SWIFT failure not understood, until the 6th); `D`, the response, was two more days because the counterparty
was closed and the stop reached RCBC during a holiday; `T_irrev` for the Philippine funds was the time to
withdrawal, under four days. ADR-0032 §4's answer when the budget cannot be met is that the effect "must not be
reachable from the alphabet at all", or, in the overlay, that a person releases it (ADR-0066). A $951 million
transfer is the case that sentence is for. ADR-0063's `K_up` offers the other answer: a bound in effects, not time
(`Outstanding`'s `EffectsAfterRevocationBounded`). It needs a revocation, and none was ordered until the 8th.

**The Fed's screen is the control that worked, and TOPAK has no place for it.** Thirty of 35 were stopped by a
counterparty applying its own judgment to authenticated instructions, and a Sri Lankan bank stopped another on a
spelling. In TOPAK terms these are deny-only semantic judgments, admissible as a deny (ADR-0007), held by a party
outside the deployment. ADR-0065 lets another stack's word enable nothing and gives it no standing to refuse either.
`proposed:CounterpartyScreen` would model a receiving party whose refusal subtracts from the sender's effects, and
state what the sender may assume about it: nothing, which is what the Bangladesh Bank-Fed dispute was about.
