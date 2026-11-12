---
id: 1975-GAM-TWO-GENERALS
title: The coordinated attack problem — no finite exchange of acknowledgements over a channel that can lose any message
kind: canonical
date: "1975"
sector: game-theory
setting: Two parties that must act together and can talk only over a channel that may lose any message; first published in network-communications design (Akkoyunlu, Ekanadham and Huber, SOSP 1975), named by Gray (1978), formalised by Halpern and Moses
concerns: [partition, timing, expiry, revocation, actuation, consensus]
rules_at_time:
  - document: Halpern and Moses, "Knowledge and common knowledge in a distributed environment" (JACM 1990)
    clause: "§8, NG1 and NG2"
    paraphrase: communication is not guaranteed when, from any point, it is possible that no further message is received, and a processor that has heard nothing considers it possible that none of its messages arrived
analogue:
  - record: ADR-0062
    clause: "§5"
    note: going alone ends the lease where it stands, and the plane orders the end when it learns of it, "as ADR-0031 E1 has expiry, local, and then ordered"
  - record: ADR-0063
    clause: "Context, §3–§5"
    note: '"a plane that is cut off cannot tell ''not revoked'' from ''revoked, and not yet heard''"; revocation is bounded by a count of the plane''s own acts, and a cut link fails closed'
  - record: ADR-0066
    clause: "§4"
    note: an act is ordered only in contact; one that crossed the link before it was cut can still fire, "and a governor cannot tell that the link is cut"
  - record: ADR-0032
    clause: "§1, §2"
    note: an interval whose failure subtracts may use a local clock; clocks buy liveness, never safety
  - record: ADR-0065
    clause: "§6"
    note: talk settles nothing, and agreement is an ordered entry
actors:
  - party: General A, commander of the first division
    role: controller
    fault: honest
    note: proposes "attack at dawn" and will not attack without knowing B will
  - party: General B, commander of the second division
    role: controller
    fault: honest
  - party: The messenger, through enemy ground
    role: peer
    fault: omission
    note: may get lost or be captured; in the canonical telling, on this night, every message is delivered
  - party: E. A. Akkoyunlu, K. Ekanadham and R. V. Huber; Jim Gray; Y. Yemini and D. Cohen; J. Y. Halpern and Y. Moses
    role: investigator
    fault: none-alleged
    note: first publication (1975, framed around two groups of gangsters), the name (1978), an impossibility proof (1979), and the knowledge-based proof (1990)
detection:
  means: [researcher]
  latency: not-applicable
trace:
  - step: AdmitRelease
    at: General A's "let's attack at dawn"
    note: Release.tla; a person at a release seat signs an act, ordered at the commanded plane while it is in contact (OrderedInContact)
  - step: Relay
    at: the messenger, one hour each way
    note: Release.tla; the act crosses the link toward the vehicle's governor
  - step: LinkToggle
    at: the messenger is captured
    note: Release.tla; the link is cut after the act crossed it. In the canonical telling nothing is lost, and the generals still cannot attack
  - step: Fire
    at: General B acts
    note: Release.tla; the governor fires within the act's freshness and cannot tell the link is cut. The witness NeverFiredAfterCut is violated
  - step: outside:acknowledge-receipt
    at: B's messenger back to A
    note: no module carries an acknowledgement of an act to its signer; the fire is recorded on the vehicle's chain and read at the seal (ADR-0062 §6)
  - step: outside:acknowledge-the-acknowledgement
    at: the regress
    note: '"for no k does a k-round handshake protocol guarantee that the generals be able to coordinate an attack"'
  - step: outside:joint-effect-both-or-neither
    at: the attack
    note: two divisions acting together; no module states an effect that must occur on two vehicles or on neither
counterfactual:
  by: the corpus's alternative to common knowledge, in which each side acts on what it alone knows and only in the direction that subtracts
  trace:
    - step: GoAlone
      at: a vehicle stops hearing its plane
      note: Alone.tla; the governor ends the lease itself and does not wait to learn whether the plane knows (ADR-0062 §5)
    - step: Revoke
      at: the intent boundary revokes
      note: Outstanding.tla; the boundary does not wait for an acknowledgement, and no clock is read
    - step: Effect
      at: governors that have not heard
      note: Outstanding.tla; fewer than K_up further effects in all, whenever or whether the revocation is heard
    - step: Mark
      at: a watermark, the boundary's acknowledgement of the plane's record
      note: Outstanding.tla; withheld or late, it only lowers what is released
  holds: [AlonePermitsNothing, ExpiryGrantsNothing, EffectsAfterRevocationBounded, HavocPlaneBoundedInEffects, OrderedInContact]
outcome:
  by: Akkoyunlu, Ekanadham and Huber (1975), as reported by later literature; Halpern and Moses (1990)
  date: "1990"
  summary: >-
    No protocol over a channel that can lose messages guarantees a coordinated attack. Halpern and Moses prove that
    a simultaneous coordinated attack requires common knowledge of it (Proposition 4); that where communication is
    not guaranteed nothing becomes common knowledge unless it would be so with no communication at all (Theorem 5);
    and hence that any correct protocol guarantees that neither general ever attacks (Corollary 6). The same holds of
    a protocol that only guarantees that if one attacks the other eventually will (Proposition 10), and a similar
    result holds when delivery is guaranteed but its time is unbounded. A global clock makes "it is 5 o'clock" common
    knowledge, and an attack with high probability is achievable under probabilistic assumptions about delivery.
  aftermath: >-
    The problem became, in Wikipedia's words, "the first computer communication problem to be proven to be
    unsolvable", and is taught to show that TCP "cannot guarantee state consistency between endpoints". Engineering
    practice accepts the uncertainty and reduces it: many messengers, streams of acknowledgements, numbered messages.
    Halpern and Moses define weaker states (eventual, epsilon and timestamped common knowledge) that are attainable.
  effect_reversed: not-applicable
model:
  modules: [Release, Alone, Outstanding, PlaneClock, proposed:JointEffect]
  properties: [OrderedInContact, IrreversibleIsAPersons, NoOlderThanDeclared, AlonePermitsNothing, EffectsAfterRevocationBounded, EntryEndsAtExtent]
  mutations: [M_NOCONTACT, M_LATEFIRST, M_ALONEACTS, M_NOSTOP, M_EARLYRELEASE, M_RECEIPT]
  records: [ADR-0032, ADR-0031, ADR-0062, ADR-0063, ADR-0064, ADR-0065, ADR-0066, ADR-0068]
  findings: [TM2, TM6]
  fault_class: omission by the channel with every party honest; what is missing is knowledge, not honesty
sources:
  - https://arxiv.org/abs/cs/0006009
  - https://arxiv.org/pdf/cs/0006009
  - https://en.wikipedia.org/wiki/Two_Generals%27_Problem
verified: 2026-11-12
---

## Summary

Two divisions on two hilltops can beat the enemy in the valley only by attacking together; one alone is defeated.
They talk only by messenger, who takes an hour each way and may be lost or captured. Neither general attacks unless
sure the other will. On the night of Halpern and Moses's telling, every messenger arrives.

A sends "attack at dawn". B will not attack unless A knows B received it, so B sends an acknowledgement. Now B does
not know whether that arrived, so A must acknowledge the acknowledgement, and so on. The proof is an induction on the
messages delivered: if k + 1 messages sufficed, the sender of the last attacks without knowing it arrived, so its
receiver must attack whether it arrives or not, and k sufficed.

According to Wikipedia, the problem and an impossibility proof were first published by Akkoyunlu, Ekanadham and Huber
in 1975, framed as two groups of gangsters, and Gray named it the "Two Generals Paradox" in 1978. Neither original
was read for this entry. Halpern and Moses credit the problem to Gray and the detailed proof to Yemini and Cohen
(1979).

## Defensive position

**What can be done, as the literature puts it.**

- **Halpern and Moses**: simultaneity is "a very strong" requirement that real generals probably do not need. An
  attack where the other attacks "with high probability" is achievable under probabilistic delivery assumptions, and
  eventual, epsilon and timestamped common knowledge are attainable "in practice".
- **A clock helps**: with a global clock that every processor reads, "at 5 o'clock it becomes common knowledge that
  it is 5 o'clock".
- **Engineering practice**, as Wikipedia summarises it: send many messengers, stream and number acknowledgements, and
  treat a long silence as confirmation. Each lowers the risk, and none removes it.

## Adversarial position

**The impossibility, in its authors' terms.**

- No finite number of acknowledgements suffices: the generals can reach "E^k" (everyone knows, k levels deep) for any
  k if the first k messages arrive, but coordinated attack needs common knowledge, "and nothing less will do".
- The result does not depend on a message actually being lost. In the telling, every message arrives, and still "no
  agreement can be reached and no general can decide to attack".
- Weakening simultaneity to "eventually" does not escape it (Proposition 10); neither does guaranteed delivery with
  unbounded delay.

## Outcome

Settled as impossibility: over a channel that can lose messages, any correct protocol for coordinated attack is one
in which no one attacks. Halpern and Moses (JACM 1990) generalised it into the statement that common knowledge cannot
be attained by communication that is not guaranteed, and gave attainable weaker states. There is no effect to reverse.

## Analysis

**TOPAK has no rule that needs common knowledge, and that is a design choice.** Every safety rule in the overlay is
one-sided and acts in the direction that subtracts.

- **Expiry and going alone are local, then ordered.** ADR-0031 E1 has the first replica that observes an expiry
  propose the round's end. ADR-0062 §5 has a governor end its lease the moment it stops hearing its plane, before the
  plane knows. Neither side waits to learn what the other knows. Alone.tla's `AlonePermitsNothing` is the property,
  and `M_ALONEACTS` is the general who waits for an acknowledgement before standing down.
- **Revocation does not wait for an acknowledgement.** ADR-0063 states the Two Generals in its own words: a cut-off
  plane "cannot tell 'not revoked' from 'revoked, and not yet heard'". Its answer is not a handshake but a count of
  the plane's own acts. Outstanding.tla bounds effects after a revocation at fewer than `K_up`, with no clock in the
  module. The watermark is an acknowledgement running the other way, and the record makes its loss safe: "An
  adversary can deliver such a watermark late or not at all, which only lowers what is released." `M_NOSTOP` and
  `M_EARLYRELEASE` are the two ways that acknowledgement would start to carry authority.

**The coordinated attack is ADR-0066's release, and the corpus says so without the name.** A person signs an
irreversible act, it is relayed over a link, and a governor fires it. Release.tla's second finding is the impossibility
in one sentence: "with no link there is no irreversible effect" is true of the order and not of the effect. An act
that crossed before the cut still fires inside its freshness, and the governor "has no way to know the link is cut"
(`NeverFiredAfterCut`, violated). The signer is General A: when the act is signed, nothing tells the person that it
will fire, and nothing needs to. `OrderedInContact` (broken by `M_NOCONTACT`) bounds when an act can be ordered, and
`NoOlderThanDeclared` (broken by `M_LATEFIRST`) bounds how late, in ticks, it can fire. Both bound the uncertainty
and neither removes it.

**The closest the corpus comes to Halpern and Moses's escape is ticks.** ADR-0064 counts every interval in ticks from
a named tick, and an act names one. That is close to what Halpern and Moses call timestamped common knowledge, with
the plane's certificates in place of a global clock. `M_RECEIPT`, which starts an interval at receipt rather than at the
named tick, is the mutation that loses it. The residual is a governor's own slow clock, which ADR-0064 §5 declares.

**What the corpus cannot express: an effect on two bodies that must be both or neither.** ADR-0065 §6 says
coordination that must be exact is an ordered entry: "every vehicle sees the same outcome". That orders the decision.
It does not make two governors fire together over links that can fail, and by Corollary 6 nothing can. A-0068-9 comes
closest, assuming budgets "voted against what every stack could do together", but it is about permitted acts adding
up, not about one act needing another. `proposed:JointEffect` would state what can be had: for a declared pair of
effects, each fires only within a declared window of the other's tick, and a pair half-fired is a finding. It would
also carry a lint the records could adopt, that no safety property may require two effects to co-occur. The outside
steps (`acknowledge-receipt`, `acknowledge-the-acknowledgement`, `joint-effect-both-or-neither`) mark where the
corpus has deliberately nothing. Only the last is a gap.

**The cost is TM2's.** A design that never waits for an acknowledgement stops when it hears nothing. TM2 says
"denial is always available" to a link adversary, including blocking every irreversible effect, and ADR-0066 says
that an adversary who jams the link "gets that for nothing". That is the price of refusing the generals' problem
rather than solving it.
