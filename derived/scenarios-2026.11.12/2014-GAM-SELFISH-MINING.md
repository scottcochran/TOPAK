---
id: 2014-GAM-SELFISH-MINING
title: Selfish mining — a pool that withholds valid blocks earns more than its share, so majority is not enough
kind: disclosure
date: "2014"
sector: game-theory
setting: Bitcoin's proof-of-work blockchain and its mining pools; Eyal and Sirer, Cornell University (arXiv November 2013; Financial Cryptography 2014)
concerns: [incentives, collusion, consensus, quorum, timing, partition]
rules_at_time:
  - document: The Bitcoin protocol, as Eyal and Sirer describe it
    clause: publication and fork choice
    paraphrase: a miner publishes a block it finds at once and mines on the longest chain; with two branches of equal length, a node mines on the one it heard of first
  - document: The Bitcoin security claim, as Eyal and Sirer and Sapirshtein et al. describe it
    clause: honest majority
    paraphrase: the blockchain is secure while a majority of miners follow the protocol, and the protocol was held to be incentive-compatible, so a minority pool gains nothing by deviating
analogue:
  - record: ADR-0061
    clause: "§1, §4, Negative"
    note: '"Against an adversary that can silence vehicles, the tolerance is the floor''s from the start": control of the link lowers the capture threshold, as control of propagation lowers the selfish-mining one'
  - record: ADR-0063
    clause: "§4"
    note: '"An adversary can deliver such a watermark late or not at all, which only lowers what is released"'
  - record: ADR-0066
    clause: "§4"
    note: '"A captured plane can stop ticking, and no act then ages"; duration is the governor''s watchdog (ADR-0064 §5)'
  - record: ADR-0039
    clause: "§5"
    note: '"A Byzantine Observer can stop its own cell by withholding heartbeats. That is availability"'
  - record: ADR-0007
    clause: the premise
    note: an agent is Byzantine at every deployment position, so a rational one is a special case
actors:
  - party: Ittay Eyal and Emin Gün Sirer (Cornell University)
    role: investigator
    fault: none-alleged
  - party: A selfish mining pool (the paper's hypothetical attacker)
    role: attacker
    fault: byzantine
    note: follows no rule the network can check is broken; it publishes valid blocks late
  - party: Honest miners
    role: peer
    fault: honest
    note: a share gamma of them mine on the pool's block in a tie
  - party: Ayelet Sapirshtein, Yonatan Sompolinsky and Aviv Zohar (Hebrew University)
    role: investigator
    fault: none-alleged
    note: optimal selfish mining strategies (2015)
detection:
  means: [researcher]
  latency: not-applicable
trace:
  - step: outside:keep-block-private
    at: the pool finds a block
    note: it does not publish, and mines on its private branch
  - step: outside:extend-private-lead
    at: the pool finds another
    note: a lead of two; it keeps both private
  - step: outside:honest-block-published
    at: the others find a block
    note: honest miners publish at once, as the protocol says
  - step: outside:race-on-equal-branches
    at: lead of one, others publish
    note: the pool publishes its block; a share gamma of honest miners mine on it, and the rest on the other
  - step: outside:publish-private-branch-to-orphan
    at: lead of two, others publish
    note: the pool publishes its whole branch, which is longer, and the honest block is orphaned; honest work is wasted in proportion
  - step: outside:rational-miners-join-pool
    at: the pool above the threshold
    note: revenue per member rises with pool size above the threshold, so the pool grows until it is a majority
outcome:
  by: Eyal and Sirer (Financial Cryptography 2014); Sapirshtein, Sompolinsky and Zohar (2015)
  date: "2015"
  summary: >-
    Eyal and Sirer showed Bitcoin is not incentive-compatible. A pool of share alpha running Selfish-Mine earns more
    than alpha for (1 − gamma)/(3 − 2gamma) < alpha < 1/2, where gamma is the share of honest miners that mine on the
    pool's block in a tie. The threshold is zero at gamma = 1, 1/3 at gamma = 0 and 1/4 at gamma = 1/2. They argued
    the protocol then had gamma close to 1, so a pool of any size gained, that rational miners would join a selfish
    pool until it was a majority, and that 1/3 is an upper bound on the safe size. They proposed uniform random
    tie-breaking, which sets gamma to 1/2 and the threshold to 1/4. Sapirshtein, Sompolinsky and Zohar found optimal
    policies that dominate Selfish-Mine and lower the thresholds; that uniform tie-breaking lowers the threshold at
    gamma = 1/2 from 0.25 to 0.2321; and that in a model with propagation delay the threshold vanishes.
  aftermath: >-
    Eyal and Sirer called on miners to adopt the tie-breaking change immediately; the sources read do not say whether
    it was adopted. Their paper notes that selfish mining is easy to hide (a pool can publish from different addresses
    and IPs), so detection is no defence.
  effect_reversed: not-applicable
model:
  modules: [Outstanding, PlaneClock, Coupling, Membership, proposed:Withholding]
  properties: [EffectsAfterRevocationBounded, HavocPlaneBoundedInEffects, EntryEndsAtExtent, NoStretchUnlessSlow, NoAdmitWithoutLiveObserver, AtMostOneSuccessor]
  mutations: [M_TRUSTMARK, M_EARLYRELEASE, M_NOWATCHDOG, M_TOOSLOW, M_BELOWFLOOR]
  records: [ADR-0007, ADR-0061, ADR-0063, ADR-0064, ADR-0066, ADR-0039, ADR-0065, ADR-0068]
  findings: [TM2, TM5, TM12, TM13, TM14]
  fault_class: a rational coalition withholding valid messages and timing their release; deviation that pays, not merely deviation that is possible
sources:
  - https://arxiv.org/pdf/1311.0243
  - https://arxiv.org/pdf/1507.06183
verified: 2026-11-12
---

## Summary

Bitcoin miners compete to solve a cryptographic puzzle; the winner adds a block of transactions to a public chain
and is paid in bitcoin. Pools of miners share the work and the rewards. The protocol tells a miner to publish a block
as soon as it finds one and to mine on the longest chain, and, faced with two branches of equal length, on the one it
heard first. Its security was described as requiring an honest majority, and the protocol was held to be
incentive-compatible: a minority pool could not earn more than its share of mining power by deviating.

Eyal and Sirer (arXiv, November 2013; Financial Cryptography 2014) described Selfish-Mine. A pool keeps the blocks it
finds private and mines on its own branch. When the public chain catches up to within one block, it publishes, and
when others find a block while it leads by two, it publishes its whole branch and orphans theirs. Honest miners then
waste work on blocks that do not stay in the chain, proportionally more than the pool does. Every block the pool
publishes is valid. What departs from the protocol is when it publishes.

## Defensive position

**The conventional view the paper set out to refute**, as Eyal and Sirer state it: the protocol was "incentive-compatible
and secure against colluding minority groups"; miners are paid in proportion to their power, so pooling gives no
advantage and pool formation by honest rational miners "poses no threat to the system". Sapirshtein et al. note that
Nakamoto showed the blockchain secure while a majority follows the protocol, and that always extending the latest
block was shown to be a (weak, non-unique) Nash equilibrium in a model without block withholding.

**Eyal and Sirer's own mitigation**: a backward-compatible, progressive change, uniform random choice between equal
branches, which they say raises the threshold from near zero to 1/4.

## Adversarial position

- **Eyal and Sirer**: above the threshold a selfish pool's revenue "rises superlinearly with pool size", so rational
  miners join it until it is a majority, "at which point the pool will be the only creator of blocks". With good
  control of information flow the threshold is close to zero, and "the Bitcoin system is safe only when 100% of the
  miners are honest". Even at best the protocol "will never be safe" against a selfish pool above a third.
- **Sapirshtein, Sompolinsky and Zohar**: Selfish-Mine is not optimal, so the true thresholds are lower; the proposed
  tie-breaking rule "enhances the power of medium-sized attackers"; and with propagation delay "there is always a
  successful selfish mining strategy", whatever the attacker's size.

## Outcome

The literature settled that an honest-majority threshold is not an equilibrium. Eyal and Sirer bound the safe pool
size at 1/3 at best and near zero under the protocol as it stood, and Sapirshtein et al. lowered the thresholds
further and removed them under delay. The sources read do not report a change to Bitcoin's fork choice. No effect to
reverse.

## Analysis

**Incentive compatibility is a claim TOPAK never makes, on purpose.** Bitcoin's threshold counted miners who follow
the protocol and assumed rational ones would. Eyal and Sirer showed that the assumption failed below a half. TOPAK's
premise makes every agent Byzantine at every position (ADR-0007), so a rational agent is one case of havoc and nothing
rests on its payoff. Its replicas are mechanism, not principals: they are paid nothing, so no replica gains by timing
what it publishes. The selfish-mining mechanism, reward per block won in a race, has no counterpart in the corpus.

**What does carry over is withholding.** Selfish-Mine is an omission strategy: valid messages, released late. The
corpus answers it record by record, each time by making the withheld message one whose absence only subtracts.

- A watermark withheld or late "only lowers what is released" (ADR-0063 §4). Outstanding.tla's
  `EffectsAfterRevocationBounded` holds whatever the adversary delivers. `M_TRUSTMARK` and `M_EARLYRELEASE` are the
  two ways a watermark would start to carry authority.
- A heartbeat withheld stops the withholder's own cell (ADR-0039 §5; Coupling.tla's `NoAdmitWithoutLiveObserver`).
- **Ticks are the exception, and the corpus knows it.** A captured plane that stops ticking stops its acts from ageing
  (ADR-0066 §4; Release.tla's third finding), so there withholding preserves authority. ADR-0064 §5 closes it with
  the governor's own clock: an overdue tick makes the vehicle alone. PlaneClock.tla's `EntryEndsAtExtent` fails
  under `M_NOWATCHDOG`, and the declared residual is a slow governor clock (`NoStretchUnlessSlow`).

`proposed:Withholding` would state the rule once: for every kind of message the overlay carries, a behaviour that
delays or drops it admits nothing that prompt delivery would refuse. Today that is argued case by case, and the
tick case shows the case-by-case argument can miss one.

**Control of propagation lowers a threshold; the corpus has met this.** Eyal and Sirer's gamma is the attacker's grip
on information flow, and at gamma near 1 the threshold is near zero; Sapirshtein et al. remove it under delay.
ADR-0061's Negative states the same for capture: an adversary that can silence vehicles walks a plane down its shrink
schedule, so "two captured replicas then capture a plane that tolerated two when it was seated". TM2 plus TM12 turns
link control into capture power. A threshold stated against capture alone is overstated against an adversary who
controls the link. Membership.tla checks that a step stays at the floor (`StepAtFloor`; `M_BELOWFLOOR`). It does not
model silencing, so the walk-down is a stated Negative and not a checked behaviour.

**Ordering is where a rational actor could still gain.** ADR-0061 §2 says a Byzantine primary "chooses the order and
can stall; it cannot forge". Within safety, that is a choice of winners. Where an `ordered` entry gives one vehicle a
task and no more (ADR-0065 §6), the primary of a captured plane decides which vehicle gets it. No module has a primary,
and no record says ordering must be fair. TM13's task-claiming stack is the agent-side version, and nothing rests on
it. Both are availability, not safety. A deployment that pays per task should know it.

**Where the pattern stops.** No module has a payoff or a rational player, and the corpus has no notion of a coalition
growing because membership pays. Capture is an adversary's work. Eyal and Sirer's pool-growth step has a corpus
analogue only in common-mode capture: identical governor builds would make one exploit capture many replicas, with
no profit needed. The six outside steps are Selfish-Mine itself. None is a TOPAK gap except as a reminder that every
message whose timing a party controls needs the subtraction argument.
