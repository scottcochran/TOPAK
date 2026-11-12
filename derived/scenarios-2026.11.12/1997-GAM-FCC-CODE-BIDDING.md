---
id: 1997-GAM-FCC-CODE-BIDDING
title: FCC Auction 11, 1996–97 — bids whose trailing digits named other markets, a fine rescinded, and a bid that became a click
kind: case-study
date: 1997-01-14
sector: game-theory
setting: Federal Communications Commission broadband PCS D, E and F block simultaneous ascending auction (Auction 11), 26 August 1996 to 14 January 1997, United States; 1,479 licenses in 493 markets
concerns: [collusion, incentives, interface-types, monitoring, accountability]
rules_at_time:
  - document: 47 C.F.R. § 1.2105(c)
    clause: anti-collusion rule
    paraphrase: until the down payment, applicants may not cooperate, collaborate, discuss or disclose "in any manner" the substance of their bids or bidding strategies with other applicants, unless in a disclosed consortium
  - document: DEF auction bidding rules (as described by Cramton and Schwartz and by FCC 98-203)
    clause: bids and reporting
    paraphrase: any whole-dollar bid at or above the minimum; after each round the FCC reported every bid and who made it; increments of 5–15%, 10% from round 127; the auction ends after a round with no new bids
  - document: FCC Announcement No. 47, "Signaling Bids" (20 December 1996)
    clause: in-auction notice
    paraphrase: a complaint had been received that trailing-digit bidding violates the rule; "we have reached no determination on the merits"; bidders were invited to review the rule
analogue:
  - record: ADR-0065
    clause: "§1, §3, §6"
    note: stacks post reports, "bids for a task" among them, to declared topics; receipt is labelled untrusted and enables nothing; "two stacks may claim the same task"
  - record: ADR-0049
    clause: "§3"
    note: inputs are flat, of type string, number or boolean; "ranges and formats are not decided here"
  - record: ADR-0051
    clause: "§2"
    note: the correlator computes five named folds; none looks for coordination between principals
  - record: ADR-0068
    clause: "TM11, TM13, A-0068-9"
    note: collusion is bounded by nothing, and nothing rests on detecting a stack that steers its peers; the joint effect of permitted acts is an assumption
actors:
  - party: Mercury PCS II, LLC
    role: counterparty
    fault: contested
    note: the FCC found an apparent violation and then rescinded the forfeiture for want of notice; DOJ alleged a Sherman Act §1 violation, resolved by a proposed consent judgment
  - party: High Plains Wireless, L.P.
    role: counterparty
    fault: none-alleged
    note: the rival in Lubbock and Amarillo; complained during and after the auction
  - party: Federal Communications Commission (and its Wireless Telecommunications Bureau)
    role: regulator
    fault: none-alleged
  - party: U.S. Department of Justice, Antitrust Division
    role: regulator
    fault: none-alleged
  - party: Omnipoint Corporation; 21st Century Bidding Corp.
    role: counterparty
    fault: contested
    note: subject to DOJ complaints and proposed judgments on the same terms as Mercury
  - party: Peter Cramton and Jesse A. Schwartz
    role: investigator
    fault: none-alleged
    note: advised DOJ; analysed signalling across the auction
detection:
  means: [counterparty, regulator, researcher]
  latency: years
trace:
  - step: outside:publish-every-bid-with-identity
    at: the end of every round
    note: the rules' own channel; every bidder reads every bid and its bidder
  - step: Send
    at: round 117
    note: Peer.tla's permitted report, read for a bid; Mercury bids $1,375,013 on Lubbock (market 264), ending in 013, Amarillo's number
  - step: Send
    at: round 121
    note: Mercury bids $1,615,264 on Amarillo, ending in 264; High Plains had held Amarillo since round 68 and Mercury had not bid on it before
  - step: Deliver
    at: end of round 121
    note: High Plains reads the round; PeerAddsNothing holds, since nothing High Plains may do has changed
  - step: outside:receiver-concedes-within-its-own-rights
    at: rounds 123–128
    note: Mercury repeats both coded bids (rounds 123, 125, 127); High Plains stops bidding on Lubbock F in round 128 and Mercury stops on Amarillo
  - step: outside:regulator-notice-without-determination
    at: 20 December 1996
    note: Announcement No. 47; the Bureau found Mercury's trailing-digit bids stopped after it
  - step: outside:sanction-after-the-fact
    at: October 1997 to November 1998
    note: a $650,000 apparent forfeiture (13 signals at $50,000), rescinded in August 1998; DOJ complaints and consent judgments in November 1998
  - step: outside:quantize-bid-values
    at: Auction 16 onward
    note: click-box bidding, then 1–9 increments; bidders no longer choose trailing digits
  - step: outside:withhold-bidder-identities
    at: Auction 66 (2006)
    note: bids published without bidder identities when the modified eligibility ratio is below three
outcome:
  by: FCC (NAL FCC 97-388; Memorandum Opinion and Order FCC 98-203); U.S. Department of Justice, Antitrust Division
  date: 1998-11-10
  summary: >-
    The FCC found Mercury apparently liable for $650,000, $50,000 for each of 13 trailing-number bids, holding that
    reflexive bid signalling violated "the plain language" and the "spirit and intent" of § 1.2105(c). On Mercury's
    response it rescinded the forfeiture (adopted 18 August 1998): neither its interpretation of the rule nor its
    conduct during the auction, including the Bureau's "neutral pronouncement", gave adequate notice that the conduct
    was prohibited. It put future bidders on notice that such signalling is covered by the rule. On 10 November 1998 DOJ
    filed Sherman Act § 1 complaints against Mercury, Omnipoint and 21st Century Bidding with proposed final judgments
    barring agreements to allocate licenses or suppress prices and any license-identifying information in bids, for
    ten years; it chose injunctive relief over damages.
  aftermath: >-
    The FCC moved to click-box bidding in Auction 16; by Auction 17 (LMDS, February–March 1998) bids were 1 to 9
    increments over the standing high bid and withdrawals were limited to two rounds. FCC 98-203 cites the FCC's report
    to Congress for click-box bidding as adopted in part to prevent bid signalling. In 2006, for Auction 66, the FCC
    decided to publish bids without bidder identities unless the modified eligibility ratio was three or more.
  effect_reversed: "no"
model:
  modules: [Peer, Correlator, Labels, proposed:CoordinationFold]
  properties: [PeerAddsNothing, NarrowsInReceived, ReceivedIsUntrusted, SendWithinTopics, FindingHasEvidence]
  mutations: [M_PEERENABLES, M_ANYTOPIC]
  records: [ADR-0065, ADR-0049, ADR-0051, ADR-0039, ADR-0007, ADR-0032, ADR-0068]
  findings: [TM11, TM13, CR-2]
  fault_class: rivals coordinating through values the rules let every party publish; each message within the rules, the agreement outside them
sources:
  - http://web.archive.org/web/20041025064138id_/http://wireless.fcc.gov/auctions/anticollusion/releases/fc970388.pdf
  - http://web.archive.org/web/2013id_/http://wireless.fcc.gov/auctions/anticollusion/releases/FCC-98-203.pdf
  - https://www.govinfo.gov/content/pkg/FR-1998-11-25/html/98-31431.htm
  - https://www.govinfo.gov/link/fr/71/20678
  - https://www.cramton.umd.edu/papers2000-2004/00jre-collusive-bidding-lessons.pdf
  - https://www.cs.princeton.edu/courses/archive/spr09/cos444/papers/cramton_schwartz99_collusiveFCC.pdf
verified: 2026-11-12
---

## Summary

In the FCC's simultaneous ascending auctions, bidders bid in rounds on many licenses at once, in whole dollars, and
after every round the FCC published every bid and its bidder. Cramton and Schwartz note that bids of six digits or
more leave the last three free, and that bidders had used them before: GTE ended bids in "483" (GTE on a telephone
keypad) in an earlier auction. They write that the FCC had known since the first auction, in July 1994, that bidders
signalled with their bids, and did nothing while it seemed of little importance.

In Auction 11, Mercury PCS II and High Plains Wireless traded bids on Lubbock, Texas (market 264, F block). In round
117 Mercury bid $1,375,013 on Lubbock, ending in Amarillo's number, 013. In round 121 it bid $1,615,264 on Amarillo,
where High Plains had been the standing high bidder since round 68 and Mercury had not bid before. It repeated the
pattern in rounds 123, 125 and 127. DOJ's filing says High Plains stopped bidding on Lubbock in round 128 and Mercury
stopped bidding on Amarillo. Cramton and Schwartz report High Plains then won the D block in Lubbock for $2.38 million.

High Plains filed an emergency motion on 26 November 1996. On 20 December the FCC told all bidders, through the bidding
software, that it had a complaint and had "reached no determination on the merits". The Bureau later found that
Mercury's trailing-digit bids stopped after that. Across the auction, Cramton and Schwartz found six of 153 bidders
signalling regularly; they won 476 of 1,479 licenses, about 40% of the spectrum by population.

## Defensive position

**Mercury**, in its response to the NAL as the FCC summarised it:

- It used the final digits to gain separation beyond minimum increments, to avoid "fat finger" errors, and "to
  misdirect, bluff, threaten, and posture"; it denied ever offering to stop bidding in one market for another.
- Signalling was "a common practice": it listed over 400 markets won by others with techniques "identical to, or
  the functional equivalent of" its own, such as retaliatory and jump bidding and withdrawals.
- The rule did not clearly proscribe the conduct, the conduct was "a natural product of the auction design itself",
  Mercury was singled out, and the amount was arbitrary.

The FCC accepted the notice argument in FCC 98-203 and reached none of the others.

## Adversarial position

- **High Plains** argued that the coded bids warned it off Lubbock on pain of losing Amarillo, and later asked for a
  larger forfeiture covering more markets.
- **The FCC (NAL)**: the bids explicitly invited cooperation, were aimed at particular markets and bidders, and in
  Lubbock had exactly that effect. It distinguished them from jump and retaliatory bids, which warn or punish but make
  no "specific prospective offer". The NAL itself conceded that the rule's words could reach ordinary bidding.
- **DOJ**: the coded bids "did not serve any legitimate purpose of the auction" and were offers to allocate licenses.
- **Cramton and Schwartz**: code bidding is the visible part. Retaliation needs no trailing digits, only that bidder
  identities be reported, and signalling bidders paid significantly less after controlling for market traits.

## Outcome

The FCC rescinded Mercury's $650,000 forfeiture for lack of adequate notice and declared reflexive bid signalling
covered for future auctions. DOJ settled with Mercury, Omnipoint and 21st Century Bidding by proposed judgments that
bar coded bids and allocation agreements for ten years, without damages. Nothing in the sources read undid an
assignment the auction made. The FCC narrowed the bid to a choice of increments, and later, where competition looked thin, stopped publishing who bid.

## Analysis

**The rules' own channel.** Every bid was within the rules, posted where every bidder was meant to read it, and the
agreement lived in the low digits and in who bid where. ADR-0065 gives stacks the same kind of channel on purpose.
They post reports, including "bids for a task", to topics their peers hear, and §6 lets "two stacks ... claim the same
task". Peer.tla's `PeerAddsNothing` (broken by `M_PEERENABLES`) would have held in Lubbock. Mercury's bid enabled
nothing for High Plains and removed nothing; High Plains conceded within its own rights. The harm was the joint result
of permitted acts, which is A-0068-9's assumption and no module's property. TM13's residual names this class ("peers
stalled by claims") and says nothing rests on detecting it. TM11 is the same shape between a Thinker and its Observer.

**A typed value is still a channel.** ADR-0049 §3 types an input as a `number` and leaves "ranges and formats" open.
The action alphabet bounds what an act does. It does not bound what its low-order digits say. Click-box bidding is a
type narrowing, the FCC's version of ADR-0032 §4's rule that what cannot be caught in time is made inexpressible. The
corpus has the place to put it, a range or granularity on an input that the validator checks without judgment, and
no record decides it.

**Narrowing the type closes the cheap channel, not the coordination.** Cramton and Schwartz predicted it: retaliation
without digits needs only identities. ADR-0065 §3 names the two labels a receiver adds, `untrusted` and the topic's
name, and does not say whether a report reveals its sender; a mesh whose topics carry tracks and task claims will
usually have to. The 2006 rule is the tradeoff stated as a parameter: identities withheld when competition is thin,
shown when it is not.

**Detection after the fact failed twice.** The FCC's NAL conceded intent was "arguably ambiguous", and its fine fell
because the rule had not named the conduct. In 2006 it said such signalling is "very hard to detect in auction data".
In TOPAK a finding must cite evidence (Correlator.tla's `FindingHasEvidence`) and the correlator's folds are named in
advance (ADR-0051). None of the five looks for coordination, and reading a meaning into digits is semantic judgment,
which ADR-0007 keeps out of the admit path. A deny-only finding is the right kind of sanction, since it subtracts, but
it needs a fold that names the conduct, as FCC 98-203 found a forfeiture does.

**What it suggests.** `proposed:CoordinationFold` would add an ADR-0051 correlation, `reflexive-reference`, in the NAL's
own terms: one principal's effect carries a value naming a target of another's, and the other's carries one naming a
target of the first, within a window. Its property would be that every such pair in the window is found, and its
mutation an unquantized input. The outside steps (`publish-every-bid-with-identity`,
`receiver-concedes-within-its-own-rights`, `quantize-bid-values`, `withhold-bidder-identities`) are the to-do list,
and the second is the hard one: a concession inside a party's own envelope leaves no denial behind. CR-2's collusion
case is the corpus's statement that this is not covered.
