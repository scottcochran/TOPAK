
TOPAK's formal layer has no liveness property at all. Every module is `Init /\ [][Next]_vars` with no fairness, and every property is an invariant (`spec/proof-method.md` §5, "No liveness"). The 10.02 critical review flags this as CR-37 (`derived/topak-critical-review-2026.10.02.md:413`). The cost is that the design's answer to most failures is to stall, and the model can't tell a stall that ends from a deadlock. So the liveness that matters is not "a bad principal eventually stops". It is "the stalls TOPAK chooses do end" and "the emergency paths stay open while everything else is stalled".

## Already safety: withdrawing authority

Revocation, expiry and e-stop look like liveness questions, but the corpus has made them safety:
- Expiry is checked at decide time on a local clock whose error margin ends the lease early.
- The epoch fence and the lease are re-checked at apply.
- Effects need an ordered admit, so during a partition nothing commits.

`RevokedStaysStopped`, `NoActionUnderFencedEpoch` and ADR-0032 §1 ("clocks buy liveness, never safety") already cover this. Don't spend a liveness proof here. Only the replicated bookkeeping (freeing the slot, writing the seal) depends on progress.

## Tier 0: "X can't block Y". Prove all of these; it's cheap.

Several claims are really about whether an action is available, and they can be stated as invariants over `ENABLED`. The existing inductive machinery proves those. The corpus already has some: `ConsultNeverCoupled`, `LagNeverGates` (`Correlator.tla:302`) and `DenyAlwaysAvailable` (`Operators.tla:248`).

**The gap:** "an emergency call is admitted with no live Observer" (ADR-0039 A2). It is the one escape hatch from the coupling stall, and it rests only on a TLC reachability witness. Its `ENABLED` lemma was dropped because only Zenon proved it and Isabelle couldn't check Zenon's script (`Emergency_proof.tla:401`). Restore it, by a route Isabelle can check or in Lean. A reachability witness shows the call can happen in some run. The claim needs it to be possible in every state where the Observer is dead.

## Tier 1: real leads-to properties to model and prove (in priority order)

1. **The Run coupling stall resolves** (ADR-0039 §2, assumption A12). If the cell Observer eventually holds its lease and keeps up, then:
   - every Thinker refused for its backlog is eventually admitted again;
   - round `r+1` is eventually granted once round `r` is sealed.

   Roughly `(tLive /\ ~LiveO) ~> (LiveO \/ ~tLive)` and `(~tLive /\ round = r < MaxRound) ~> round = r+1`. Repeat it for `Actuate`/`Report` in `RunCoupling`.
   - **Fairness pitfall:** in `Coupling.tla:92` an Observer can go stale (`Stale`) at any moment, so `Admit` is only intermittently enabled. Weak fairness on the heartbeat, which is what CR-37 proposes, is not enough. You need either strong fairness on `Admit`, or `Stale` restricted to "no heartbeat since". The assumption should be A12 written as a fairness condition, so the proof says exactly what a deployment must guarantee.
   - `Coupling.tla` is frozen by digest, so this goes in a successor module, as `Lease_A1` did.

2. **The Build promotion stall resolves** (ADR-0024 §2, A2.3). Under the two weak-fairness assumptions ADR-0024 already states (on `Vote`, and on the Observer's lease and coverage; `ADR-0024.md:214-222`), a gated round that no seat denies eventually promotes.
   - A proof will force a missing premise: the rules epoch must eventually stop changing. Every epoch change voids votes in flight, so repeated fences can starve a promotion forever.
   - This belongs in the still-owed bootstrap `Promotion` module.

3. **Every ended lease eventually yields a seal.** This covers expiry (I15, proposed as `EndRound(Expired)` and ordered), revocation and fence. The grant guard in item 1 reads `seal[r]` (`Coupling.tla:54`), so a seal that never lands is a silent deadlock of the next round. It assumes consensus progress (see Tier 2).

4. **A lapsed operator is eventually re-seated by a quorum** (`ADR-0050.md:240`). Lower priority: the stall is declared, and resolving it rests on people.

5. **Detection eventually happens.** Under fairness on the correlator's fold, each correlator's watermark eventually passes every send, so `CarriedCoversSplitPath` eventually applies. It's useful but advisory, since detection can only subtract.

## Tier 2: declare as assumptions, don't prove

- **Paxos liveness** (an eventually stable leader under partial synchrony). It's textbook, and the reference already tests "liveness after healing" (`ADR-0033.md:170`). Model it as fairness on an abstract ordering action in the modules above.
- **Timing budgets** (`W + L + D < T_irrev`, `T_obs`, `K`). These are measurements, not theorems. ADR-0032 rightly defers UPPAAL, so measure them with the rehearsal rig (CR-36).
- **Human responsiveness** (weak fairness on `Vote`). It's an assumption about people, as ADR-0024 says.
- **Kafka delivery.** Lost records leave the Observer short of the seal, which shows up as a stall under A12. It doesn't need its own property.

## Why it's worth the cost

Here is a mutation that the current method would miss: an Observer may heartbeat only while the Thinker's lease is live. Some behaviours read round 1 before it ends, so the `NeverRoundTwo` witness is still reached. In any behaviour where round 1 ends unread, round 2 can never be granted. Every safety property passes. Several run scripts also pass `-deadlock`, which turns TLC's deadlock check off. Only a leads-to property catches this.

The method should stay as it is, with a mutation that must break each liveness property, just as with the invariants.

**Suggested route:** TLC liveness checking at small constants on a Coupling successor module. Then a TLAPS WF1/SF1 proof using a decreasing measure such as `seal[r] − mark[r]` or `seq − mark`. Lean comes later, because its packages would first need a model of infinite behaviours and fairness.

I can draft the Coupling successor module with the fairness conditions, the two leads-to properties and the deadlocking mutation if you want.
