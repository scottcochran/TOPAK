---
id: 2016-FIN-DAO-REENTRANCY
title: The DAO, 17 June 2016 — a recursive split under code-as-contract, and the hard fork that undid it
kind: incident
date: 2016-06-17
sector: fintech
setting: The DAO, a smart contract on the Ethereum blockchain described in a White Paper by Slock.it's CTO, and the Ethereum network that forked to reverse its drain
concerns: [authority, actuation, rollback, consensus, configuration-change, timing]
rules_at_time:
  - document: The DAO's code and White Paper (as the SEC described them)
    clause: split
    paraphrase: a token holder could split from The DAO into a child DAO; ether moved by a split could not leave the child's address for 27 days
  - document: The DAO's code and White Paper (as the SEC described them)
    clause: Curators
    paraphrase: Curators chosen by Slock.it kept the whitelist of proposals that could be voted on and could halve the voting quorum
  - document: Ethereum protocol and clients, 2016
    clause: state transitions
    paraphrase: a valid transaction's effect stands; changing it needs a client change that the network adopts, either a soft fork rejecting some transactions or a hard fork with an irregular state change
  - document: US Securities Act of 1933 and Securities Exchange Act of 1934
    clause: registration
    paraphrase: offers and sales of securities must be registered or exempt; the SEC later applied this to DAO Tokens
analogue:
  - record: ADR-0025
    clause: "§2"
    note: "intent is the sole axiom: an authentic issuance at the current anchor epoch is what the anchor intended"
  - record: ADR-0025
    clause: Annex, A-0025 and D-0025-1
    note: under strict unanimity any loss freezes the rules and the exit is re-genesis; under k of n "a k-coalition can issue rules over n−k objections"
  - record: ADR-0028
    clause: "§1"
    note: admit decisions and anchor issuances are non-erasable forensic classes; the history is kept whatever later rules say
  - record: ADR-0031
    clause: "§5"
    note: "a revocation is permanent within the rules-epoch chain; lifting one would add authority, and no record says who may"
  - record: ADR-0055
    clause: title
    note: a cycle in a workflow is allowed only under an activation budget the promotion votes on
  - record: ADR-0062
    clause: "§6"
    note: nothing a governor permitted is void; a check failing afterwards is a finding and only subtracts
actors:
  - party: The "Attacker" (the SEC's term, in quotation marks), an unknown individual or group
    role: attacker
    fault: contested
    note: used the split function recursively; whether that was theft or a use of the contract as written is the dispute the fork answered one way and Ethereum Classic the other
  - party: Slock.it and its co-founders
    role: vendor
    fault: none-alleged
    note: authors of the White Paper; proposed security work and a moratorium before the drain; endorsed the hard fork
  - party: The DAO's Curators
    role: supervisor
    fault: none-alleged
  - party: Ethereum Foundation (Vitalik Buterin)
    role: maintainer
    fault: none-alleged
    note: proposed a soft fork on 17 June; announced the completed hard fork on 20 July
  - party: Miners and node operators adopting the fork
    role: peer
    fault: none-alleged
    note: about 85% of miners on the fork chain at the EF's count
  - party: Ethereum Classic community
    role: peer
    fault: none-alleged
    note: the minority that kept the unforked chain, on immutability
  - party: US Securities and Exchange Commission
    role: regulator
    fault: none-alleged
detection:
  means: [public]
  latency: hours
trace:
  - step: outside:token-offering
    at: 30 April to 28 May 2016
    note: about 1.15 billion DAO Tokens for about 12 million ETH, about $150 million at the close
  - step: outside:security-warning
    at: 26 May and 3 June 2016
    note: Slock.it proposes a security update and expert, then a moratorium on proposals until code vulnerabilities are fixed
  - step: outside:reentrant-split
    at: 17 June 2016
    note: split is called again from within split, collecting ether several times in one transaction; about 3.6 million ETH, a third of the offering, moves to a child DAO the attacker controls
  - step: outside:hold-window
    at: 17 June to mid-July
    note: the DAO's own code bars the ether from leaving the child for 27 days; the window is the drain's T_irrev
  - step: outside:soft-fork-proposed
    at: 17 June 2016
    note: a client rule making invalid any transaction that reduces the balance of The DAO or its children, from a block to be set; it "does not roll back any transactions or blocks"
  - step: Issue
    at: 20 July 2016, block 1,920,000
    note: the hard fork as an issuance; it carries an irregular state change moving the DAO's ether, the attacker's included, to a refund contract, and Anchor's Issue changes rules only
  - step: outside:state-rewritten
    at: 20 July 2016
    note: token holders on the forked chain can exchange DAO Tokens for ETH; no record lets an issuance move balances
  - step: outside:chain-split
    at: from 20 July 2016
    note: a minority keeps the former chain, now Ethereum Classic; on it the drain stands
outcome:
  by: Ethereum network (hard fork); US Securities and Exchange Commission (Section 21(a) report)
  date: 2016-07-20
  summary: >-
    On 20 July 2016, "after a majority of the Ethereum network adopted the necessary software updates", the forked
    chain went live at block 1,920,000 with an irregular state change that transferred all funds raised by The DAO,
    including those held by the Attacker, to a recovery address, where DAO Token holders could exchange tokens for
    ETH. The EF reported about 85% of miners on the fork. A minority kept the former chain, Ethereum Classic, "because
    to do so would run counter to the concept that a blockchain is immutable". On 25 July 2017 the SEC reported that
    DAO Tokens were securities, that "automation of certain functions" by smart contracts does not remove conduct
    from the securities laws, and that it would not pursue an enforcement action.
  aftermath: >-
    Two chains with a shared history up to block 1,920,000. The EF advised users of the unforked chain to guard
    against transaction replay between them. Buterin's 17 June post urged contract authors to guard against
    recursive-call bugs and asked for higher-level tools that make safe contracts easier to write.
  effect_reversed: partial
model:
  modules: [Anchor, Mesh, Release, Lease_A1, NonComposition, proposed:Restitution]
  properties: [FloorPreserved, EpochMonotone, BudgetBound, ConflictIsAFinding, RevokedStaysStopped, NC2]
  mutations: [M_VOID, M_OVERRUN]
  records: [ADR-0025, ADR-0028, ADR-0031, ADR-0055, ADR-0062, ADR-0066, ADR-0032, ADR-0026]
  findings: [TM1, CR-15]
  fault_class: an actor inside the rules as written, an effect the rules made final, and a majority that changed the rules to reverse it over a minority's objection
sources:
  - https://www.sec.gov/litigation/investreport/34-81207.pdf
  - https://blog.ethereum.org/2016/06/17/critical-update-re-dao-vulnerability
  - https://blog.ethereum.org/2016/07/20/hard-fork-completed
  - https://ethereumclassic.org/blog/2016-07-11-manifesto
verified: 2026-11-12
---

## Summary

The DAO was a contract on Ethereum, described in a White Paper by Slock.it's CTO. From 30 April to 28 May 2016 it
sold about 1.15 billion DAO Tokens for about 12 million ETH, then about $150 million. Holders could vote on proposals
that Curators, chosen by Slock.it, put on a whitelist. A holder could also split into a child DAO, and ether moved by
a split could not leave the child for 27 days. In late May concerns about vulnerabilities surfaced. On 26 May
Slock.it proposed a security update and a security expert, and on 3 June a moratorium on proposals until the code was
fixed.

On 17 June an unknown party used the split function recursively, calling split from within split so that it
collected ether several times in one transaction. About 3.6 million ETH, a third of what the offering raised, moved to
a child DAO it controlled, where The DAO's own code held it for 27 days. The same day Vitalik Buterin posted that the
flaw "affects the DAO specifically" and "Ethereum itself is perfectly safe", and proposed a soft fork: from a block to
be set, any transaction reducing the balance of The DAO or its children would be invalid, which "does not roll back
any transactions or blocks" and would hold the ether past the window while further steps were discussed.

On 20 July the network adopted a hard fork at block 1,920,000. Its irregular state change moved the ether of The DAO
and its children, the child holding the drained ether included, to a refund contract from which token holders could take ETH for
their tokens. The EF counted about 85% of miners on the fork. A minority kept the old chain, Ethereum Classic.

## Defensive position

The conduct in dispute is the fork.

- **Slock.it's co-founders and others** endorsed it, the SEC records, "to secure the diverted ETH and return it to DAO
  Token holders", restoring investments "as if the Attack had not occurred".
- **The Ethereum Foundation (Buterin, 17 June)** framed the first step as the smallest possible: a soft fork that
  rolls nothing back and only stops the ether from leaving the attacker's child DAO, buying time to discuss further
  steps, including letting token holders recover their ether. The flaw was The DAO's and not the protocol's.
- **The network**: a majority adopted the software, about 85% of miners by the EF's count, and every token holder who
  followed the fork could recover what they had put in.

## Adversarial position

- **The Ethereum Classic community**, which kept the old chain, did so, the SEC records, because adopting the fork
  "would run counter to the concept that a blockchain is immutable".
- **"A Crypto-Decentralist Manifesto"** (Ethereum Classic blog, 11 July 2016, before the fork) argued that a chain
  must keep one history no interest can rewrite, that to "rewrite the history of events (such as by confiscating or
  'redistributing' funds)" violates immutability, and that rule changes need consent "not subject to change other
  than with 100% consensus".
- **The SEC's report** keeps "Attack" in quotation marks. The contract's split worked as written; the dispute is
  whether "as written" was the contract.

## Outcome

The fork took effect on 20 July 2016 and the drain was reversed on the forked chain, by rule change. On Ethereum
Classic it stands. Two chains share the history up to block 1,920,000. The SEC's Section 21(a) report of 25 July
2017 found DAO Tokens to be securities, made no findings of violation against any person, and brought no action.

## Analysis

**TOPAK's axiom is The DAO's.** ADR-0025 §2: "An authentic issuance at the current anchor epoch is what the anchor
intended." Intent is assumed and never checked; the proofs hold for every issuance sequence the floor admits. The DAO's
code was its issued rules, and the recursive split was inside them. In ADR-0068's words for TM1, "anything inside the
envelope was voted acceptable". The corpus therefore takes the attacker's side of the first question: an act the
rules permit is not a violation of the rules. TOPAK only differs in what it does next.

**The re-entrancy is a cycle with no budget.** Split called split, and each call read a balance the earlier call had
not yet charged. ADR-0055 allows a cycle in a workflow only "under an activation budget the promotion votes on", and
`Mesh` checks `BudgetBound` (no more than `N` leases, every lease charged to the budget); `M_OVERRUN` lets one past.
`Intent`'s governor checks and charges a count in one step. Neither is the contract's semantics. TOPAK would not have
made the split function correct; it would have bounded how many times it could re-enter, if the split had been
promoted as a workflow. The analogy is loose, and it is the honest limit: the corpus types effects and budgets, not
the internal ordering of a contract's reads and writes.

**The 27-day hold is a T_irrev the contract declared.** ADR-0032 §4's budget, `W + L + D < T_irrev`, was met: the
drain was seen within the day, and the ether could not move for 27 days. That window is what made a reversal
possible at all, and it was The DAO's own rule. CR-15 says nothing in TOPAK's alphabet types reversibility; ADR-0066
§1 now lets an entry declare its class. A split with a 27-day hold is an effect reversible for 27 days, which neither
class names.

**The fork is a void, ordered by the rule-maker.** In TOPAK nothing a governor permitted is void (ADR-0062 §6), and
`Release`'s `ConflictIsAFinding` holds unless `M_VOID` lets a later check void an effect that happened. A revocation
"is permanent within the rules-epoch chain", and lifting one "would add authority, and no record says who may"
(ADR-0031 §5). The hard fork did what those sentences forbid at the mechanism level: it moved balances by issuance.
`Anchor`'s `Issue` changes rules, checked by `FloorPreserved` and `EpochMonotone`; there is no action by which an
issuance rewrites an effect, and ADR-0028 keeps admit decisions (F1) and issuances (F4) whatever later rules say
(`NonComposition`'s `NC2`). A TOPAK deployment wanting the fork's outcome would have to order a new effect, a payment
back, under a new issuance, with the drain still on the record. That is `proposed:Restitution`: compensation as a
new, attributed, consensus-ordered act, never a rewrite. Whether that is better than a fork is a question of who may
issue it, which is custody.

**Custody decides whether the dissent is a veto or an exit.** ADR-0025's annex declares the choice the Ethereum
network faced. Under A-0025, strict unanimity, any key-holder's objection freezes the rules, and "Exit" is
"Re-genesis. A successor system, not a continuation." Under D-0025-1, k of n, "a k-coalition can issue rules over n−k
objections". Ethereum ran D-0025-1 with miners and node operators as the keys. The Classic community did what A-0025
calls re-genesis in reverse: it kept the old system and let the majority become the successor. Both chains claim to be
the continuation, and TOPAK's annex says neither can be both. The Manifesto's "100% consensus" is A-0025's pair (n, 0).

**What the corpus cannot express.** Re-entrancy inside a single effect, a reversibility window, an issuance that moves
state, and a chain split are all `outside:` steps. The last is the deepest: the corpus has one anchor and one
rules-epoch chain, and no notion of two continuations from a shared history. Federation (ADR-0059) has a tree of
planes under one root, not two roots.
