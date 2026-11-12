---
id: 2010-FIN-FLASH-CRASH
title: The flash crash of 6 May 2010 — a volume-paced sell algorithm, hot-potato volume and a five-second pause
kind: incident
date: 2010-05-06
sector: fintech
setting: US equity index futures (CME E-Mini S&P 500) and US equity markets, including the SPY ETF and individual stocks, 2:32 to 3:00 p.m. ET
concerns: [feedback, cascading-failure, sensing, interlock, actuation, rollback]
rules_at_time:
  - document: CME Globex Stop Logic Functionality (as described in the CFTC-SEC staff report)
    clause: E-Mini stop logic
    paraphrase: a brief automatic pause in E-Mini trading, triggered to prevent a cascade of further price declines; it paused trading for five seconds at 2:45:28
  - document: Exchange and FINRA "clearly erroneous" trade rules
    clause: trade breaks
    paraphrase: the exchanges and FINRA may cancel trades executed at clearly erroneous prices; on 6 May they broke trades more than 60% from a reference price, by a process participants called opaque
  - document: Exchange market-maker quoting obligations
    clause: continuous two-sided quotes
    paraphrase: registered market makers must keep a two-sided quote, which a stub quote far from the market satisfies when a maker has withdrawn from active trading
  - document: Market-wide circuit breakers in force in 2010
    clause: cross-market halts
    paraphrase: halts that apply across all equity trading venues and the futures markets; none was triggered on 6 May
analogue:
  - record: ADR-0065
    clause: "§1, §5"
    note: nothing a peer originates is an enabling condition, and nothing may rest on a report being read; what a stack does with what it reads is not the mechanism's
  - record: ADR-0060
    clause: "§2"
    note: an intent carries an envelope, a budget and an expiry; what it does not carry, a deployment's stack is free to choose
  - record: ADR-0045
    clause: "§2"
    note: a component is trusted for nothing if its failure can only subtract; a liquidity provider's pause is a subtraction for it and not for the market
  - record: ADR-0062
    clause: "§6"
    note: nothing a governor permitted is void; a check failing afterwards is a finding and only subtracts
  - record: ADR-0055
    clause: title
    note: cycles are allowed under an activation budget the promotion votes on; the budget bounds one workflow, not the interaction of several
actors:
  - party: Large fundamental trader (a mutual fund complex) and its Sell Algorithm
    role: automation
    fault: none-alleged
    note: the algorithm executed as programmed, 9% of the previous minute's volume, without regard to price or time; the joint report alleges no rule violation
  - party: High-frequency traders and other intermediaries in the E-Mini
    role: peer
    fault: none-alleged
    note: bought early, sold about 2,000 contracts between 2:41 and 2:44, then traded over 27,000 contracts among themselves in 14 seconds while adding about 200 net
  - party: Liquidity providers and market makers in equities
    role: peer
    fault: none-alleged
    note: automated pauses on price moves; many widened spreads or withdrew; internalizers routed retail orders to the exchanges
  - party: CME Stop Logic Functionality
    role: safety-system
    fault: honest
  - party: Exchanges and FINRA
    role: regulator
    fault: none-alleged
    note: broke trades 60% or more from their 2:40 p.m. prices after the close
  - party: Navinder Singh Sarao and Nav Sarao Futures Limited PLC
    role: peer
    fault: contested
    note: charged by the CFTC in April 2015 with layering in the E-Mini on 6 May 2010; not mentioned in the 2010 report
  - party: Staffs of the CFTC and the SEC
    role: investigator
    fault: none-alleged
detection:
  means: [automated-monitor, public]
  latency: minutes
trace:
  - step: Order
    at: 2:32 p.m.
    note: the trader's program to sell 75,000 E-Mini contracts, about $4.1 billion, as a hedge; read as an intent, its envelope named a quantity and no price, no time
  - step: Effect
    at: 2:32 to 2:51 p.m.
    note: each sell order permitted within that envelope; about 35,000 contracts sold by 2:45. Every one is inside the bound, and no property fails
  - step: Deliver
    at: 2:32 to 2:45 p.m.
    note: market volume reaches the algorithm as ingress; under ADR-0065 it may not enable anything, and here it does not; it sets the rate of acts already permitted
  - step: outside:volume-paced-acceleration
    at: 2:41 to 2:45 p.m.
    note: HFT selling and hot-potato trading raise volume; the algorithm, pacing on volume, raises its selling rate
  - step: outside:venue-wide-pause
    at: 2:45:28 to 2:45:33 p.m.
    note: CME Stop Logic pauses the E-Mini for five seconds; prices stabilize and recover after
  - step: outside:liquidity-withdrawal
    at: from about 2:45 p.m.
    note: automated pauses at many liquidity providers, each a subtraction for that firm; several withdraw entirely
  - step: outside:stub-quote-execution
    at: 2:40 to 3:00 p.m.
    note: over 20,000 trades in more than 300 securities at prices 60% or more from their 2:40 values, some at a penny, some at $100,000
  - step: outside:effects-broken-by-rule
    at: after the close
    note: exchanges and FINRA cancel all such trades under the clearly-erroneous rules
counterfactual:
  by: the trader's own intent, had it carried the price and time bounds its earlier, five-hour program used; it saves only the trader's part
  trace:
    - step: Order
      at: 2:32 p.m.
      note: the same 75,000 contracts, with a price limit and an expiry in the envelope
    - step: Effect
      at: 2:32 p.m. onward
      note: sells permitted while within the price bound
    - step: RefuseEffect
      at: as the price falls through the bound
      note: the governor refuses further sells; the intent waits or expires
  holds: [IntentNarrows, EveryEffectHasALease]
outcome:
  by: Staffs of the CFTC and the SEC (report to the Joint Advisory Committee on Emerging Regulatory Issues); the SEC
  date: 2010-09-30
  summary: >-
    The joint staff report found that, against already thin liquidity, a large fundamental trader's automated sell
    program, targeting 9% of volume "without regard to price or time", sold about 35,000 of 75,000 E-Mini contracts
    between 2:32 and 2:45, that HFTs' selling and hot-potato trading raised volume and the algorithm sped up, and
    that buy-side depth in the E-Mini fell below 1% of the morning's. Stop Logic paused the E-Mini for five seconds
    at 2:45:28 and prices recovered. A second crisis followed in individual stocks as liquidity providers paused or
    withdrew, and over 20,000 trades in more than 300 securities executed 60% or more from their 2:40 prices. The
    report concluded that "high trading volume is not necessarily a reliable indicator of market liquidity" and that
    the interaction of execution programs and algorithmic strategies "can quickly erode liquidity".
  aftermath: >-
    A single-stock circuit breaker pilot (a five-minute pause after a 10% move in five minutes) was approved for S&P
    500 stocks on 10 June 2010 and extended on 10 September, with more objective trade-break standards. On 1 June 2012
    the SEC approved a limit up-limit down mechanism that "prevents trades in individual listed equity securities
    from occurring outside of a specified price band", replacing the single-stock breakers, with revised
    market-wide circuit breakers, both to be in place by 4 February 2013. In April 2015 the CFTC charged Sarao,
    alleging his layering "contributed to market conditions that led to the Flash Crash".
  effect_reversed: partial
model:
  modules: [Intent, Peer, Release, Mesh, proposed:MarketFeedback]
  properties: [PeerAddsNothing, EveryEffectHasALease, IntentNarrows, ConflictIsAFinding, BudgetBound]
  mutations: [M_PEERENABLES, M_VOID]
  records: [ADR-0065, ADR-0060, ADR-0045, ADR-0062, ADR-0055, ADR-0007, ADR-0068]
  findings: [CR-3, TM13, TM1]
  fault_class: honest automated actors, each within its own bounds, coupled through a shared market into a loop no one of them modelled
sources:
  - https://www.sec.gov/news/studies/2010/marketevents-report.pdf
  - https://www.sec.gov/news/press/2012/2012-107.htm
  - https://www.cftc.gov/PressRoom/PressReleases/pr7156-15
verified: 2026-11-12
---

## Summary

On 6 May 2010 US markets opened to news of the European debt crisis. By 2:30 p.m. the DJIA was down about 2.5%, the
VIX up 22.5%, and buy-side depth in the E-Mini S&P 500 futures had fallen from nearly $6 billion to $2.65 billion.

At 2:32 a large fundamental trader, a mutual fund complex, began selling 75,000 E-Mini contracts, about $4.1
billion, as a hedge. Its algorithm fed orders to target 9% of the previous minute's volume, without regard to price
or time. A program of that size by the same trader had earlier taken more than five hours, with algorithms that
weighed price, time and volume. HFTs and intermediaries bought first and built a net long of about 3,300 contracts.
Between 2:41 and 2:44 they sold about 2,000 to cut it, while trading nearly 140,000 contracts. The algorithm saw
volume rise and sold faster. Between 2:45:13 and 2:45:27 HFTs traded over 27,000 contracts, about 49% of volume,
buying about 200 net. E-Mini buy-side depth fell to about $58 million and the price fell 1.7% in 15 seconds. From
2:41 to 2:45:27 the E-Mini fell more than 5% and SPY more than 6%.

At 2:45:28 CME's Stop Logic paused the E-Mini for five seconds. Trading resumed at 2:45:33 and prices recovered. The
algorithm kept selling until about 2:51. In equities, liquidity providers' automated pauses tripped; many widened
spreads or withdrew. Between 2:40 and 3:00 over 20,000 trades in more than 300 securities, many ETFs, executed 60% or
more away from their 2:40 prices, some at a penny or less and some at $100,000, against stub quotes. After the
close the exchanges and FINRA broke them all. Indices closed about 3% down.

## Defensive position

**For the automated actors**, the report's own account:

- The Sell Algorithm executed as instructed. The report names the choice of a volume-only algorithm, and alleges
  no violation.
- HFTs behaved as they typically do, trading large volumes without holding more than three to four thousand
  contracts either way.
- Liquidity providers' pauses are "designed to prevent automated systems from trading when prices move beyond
  pre-defined thresholds". Each firm weighed bad data, risk limits, the chance of trades being broken and its
  systems' load, and some feared "a cataclysmic event of which they were not yet aware".
- Stub quotes met continuous-quoting obligations as the rules then allowed.

## Adversarial position

- **The report** itself: "the automated execution of a large sell order can trigger extreme price movements,
  especially if the automated execution algorithm does not take prices into account", and many simultaneous
  withdrawals turn individually sensible pauses into a liquidity crisis.
- **Market participants**, interviewed: breaking only trades over 60% away, by a process "that was not
  transparent", left them unsure which trades would stand, which itself discouraged providing liquidity.
- **The CFTC (2015)** alleged that Sarao's layering algorithm ran "continuously, for over two hours" before the
  drop, applying close to $200 million of persistent downward pressure, and "contributed to market conditions that
  led to the Flash Crash". The 2010 report does not mention him; the causal weight of the allegation is the dispute.

## Outcome

The joint staff report of 30 September 2010 set out the findings above; the Commissions expressed no view on it. The
exchanges and FINRA broke the 60%-away trades on the day; the losses inside that line stood. Single-stock circuit
breakers were piloted from June 2010, then replaced by limit up-limit down, approved on 1 June 2012 with revised
market-wide breakers, for implementation by 4 February 2013. The CFTC's 2015 action against Sarao is separate.

## Analysis

**Nothing here breaks a TOPAK property, and that is the finding.** Read as an intent (ADR-0060 §2), the trader's
program was an envelope of 75,000 contracts with no price and no expiry. Every sell was inside it. In `Intent`
every `Effect` was counted under a lease and `EveryEffectHasALease` holds; `IntentNarrows` holds. TM1's row says it:
"anything inside the envelope was voted acceptable". The bound was vacuous in the dimension that mattered, and no
gate looks for that. ADR-0007's non-vacuity gate runs on bundles and on the floor, not on the fields an intent leaves
open.

**Volume was ingress and did not enable anything.** ADR-0065 §1 says nothing a peer originates is an enabling
condition, and `Peer` proves `PeerAddsNothing`: every request permitted is still permitted with every item from peers
removed. On 6 May that held. The hot-potato volume did not permit a single sell; it changed the *rate* of sells
already permitted. `M_PEERENABLES` is not this. What the market did is TM13's residual, "an honest stack misled
inside its own envelope", and `Peer`'s own header says what a stack does with a report "is not modelled". The
volume signal was not even false. It was true and meant something else, which is the report's point that volume is
not liquidity.

**Failure that subtracts locally can add globally.** ADR-0045 §2 trusts a component whose failure can only subtract:
a denial, a lapsed lease, a stall. Every liquidity provider's pause was exactly that for its own firm, and together
they emptied the books until stub quotes filled orders at a penny. TOPAK's "fail closed" argument is made per
deployment. It has no statement about a population of deployments whose stall is someone else's harm, and ADR-0066
quotes the boundary register's criticism of "fail-closed uniformity presented as costless". Here the cost fell on
the retail stop-loss orders that executed against stub quotes.

**The venue's pause is the brake TOPAK lacks a place for.** The five-second Stop Logic pause is an interlock held by
neither party to any trade, and it worked. Limit up-limit down is the same idea made a rule. In the corpus's terms it
is a deny-only check on a shared resource, above every deployment. ADR-0065 lets peers talk and lets nothing a peer
says enable anything; it does not give a shared venue standing to refuse. `Mesh`'s `BudgetBound` caps activations
within one workflow, and its cycles are the workflow's own. CR-3 says the corpus has no model of coupling between
principals, and the 10.02 review, citing a draft profile's reviewer note that the multi-agent feedback-loop case is
"still an open research topic", says TOPAK "still has only a noun". `proposed:MarketFeedback` would put several deployments, each safe in its own module, on one
shared book with a venue-level interlock, and state a property that no single deployment's invariants imply.

**Breaking trades is voiding effects, by rule, after the fact.** In TOPAK nothing a governor permitted is void
(ADR-0062 §6), and `Release` checks it as `ConflictIsAFinding`: a check failing above a seal is a finding and voids
nothing; `M_VOID` voids an effect that happened and must fail. The clearly-erroneous rules are an `M_VOID` operated
by a third party, under a threshold participants could not predict. TOPAK's position is coherent for effects on the
world, and silent on effects a venue can rewrite. That makes the 60% line the trace's most interesting step:
`outside:effects-broken-by-rule`.

**The counterfactual saves only the trader.** A price bound in the envelope would have made `RefuseEffect` fire as
the market fell, and the trader's earlier five-hour execution suggests that is what a person would have chosen. It
does not save the market. HFTs, providers and stub quotes are other deployments.
