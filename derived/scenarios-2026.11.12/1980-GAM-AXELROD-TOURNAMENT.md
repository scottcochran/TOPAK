---
id: 1980-GAM-AXELROD-TOURNAMENT
title: Axelrod's iterated Prisoner's Dilemma tournaments — tit for tat, and cooperation that holds only while the future is long enough
kind: canonical
date: "1980"
sector: game-theory
setting: Two computer tournaments of the iterated Prisoner's Dilemma run by Robert Axelrod, entries from game theorists and others, reported in the Journal of Conflict Resolution (1980) and with W. D. Hamilton in Science (1981)
concerns: [incentives, collusion, revocation, expiry, monitoring, accountability]
rules_at_time:
  - document: Axelrod and Hamilton (1981), citing Axelrod (1980)
    clause: first tournament
    paraphrase: 14 entries and a random strategy, paired round robin, games of 200 moves, with the payoffs T > R > P > S of the one-shot dilemma
  - document: Axelrod and Hamilton (1981), note 23
    clause: second tournament
    paraphrase: 62 entries; the length of a game was uncertain, each move having probability w = .99654 of not being the last, for an expected 200 moves; five games per pair
analogue:
  - record: ADR-0031
    clause: "§2 (successor grant), §4, §5"
    note: '"across rounds, as within one, authority never grows without a quorum"; renewal never adds authority; a revocation is permanent, and "a re-admitted Persona is a new Persona"'
  - record: ADR-0038
    clause: "§1, §2"
    note: one Observer per cell, watching its cell's Thinker round after round
  - record: ADR-0039
    clause: "§5"
    note: coupling cannot tell an honest Observer from a colluding one; collusion is covered only by lineage independence, and the residual-risk statement says detection fails open against it
  - record: ADR-0062
    clause: "§2, §8"
    note: a lease has an exact count, and a vehicle's next lease waits until its Observer has read the last one to its seal
actors:
  - party: Robert Axelrod
    role: investigator
    fault: none-alleged
    note: ran both tournaments; with W. D. Hamilton, gave the evolutionary analysis
  - party: Anatol Rapoport
    role: peer
    fault: none-alleged
    note: submitted TIT FOR TAT to both rounds
  - party: The entrants (game theorists in five disciplines in round one; computer hobbyists and professors in round two)
    role: peer
    fault: none-alleged
detection:
  means: [researcher]
  latency: not-applicable
trace:
  - step: outside:cooperate-on-first-move
    at: every pairing
    note: TIT FOR TAT's opening; "never the first to defect"
  - step: outside:copy-opponents-last-move
    at: every later move
    note: retaliates after a defection, and forgives after one act of retaliation
  - step: outside:publish-results-and-rerun
    at: second round
    note: entrants knew TIT FOR TAT had won; it won again, with game length now uncertain
  - step: outside:ecological-rerun
    at: hypothetical later rounds
    note: each rule entered in proportion to its last score; TIT FOR TAT went to fixation
  - step: Renew
    at: the mechanism's reply to a cooperative round, in Lease_A1's terms
    note: renewal keeps or narrows authority (LeaseAuthorityMonotone; M_RENEW lets it grow). Cooperation earns the agent nothing
  - step: RevokeLease
    at: the mechanism's reply to a detected defection
    note: ends the lease and bars later grants (RevokedStaysStopped; M_REVOKE grants a revoked principal again). No record says who may lift it, so it does not forgive
outcome:
  by: Axelrod (1980); Axelrod and Hamilton (1981); the later literature as the Stanford Encyclopedia of Philosophy surveys it
  date: 1981-03-27
  summary: >-
    TIT FOR TAT, the simplest entry, had the highest average score in the first tournament and won the second. In the
    analysis of the second round its robustness rested on three features: it was never the first to defect, it was
    provocable into retaliation, and it forgave after one retaliation. Axelrod and Hamilton showed that with a known
    number of interactions always defecting is the only evolutionarily stable strategy, by backward induction; that
    for any w ALL D is stable; and that TIT FOR TAT resists invasion if and only if w ≥ (T − R)/(T − P) and
    w ≥ (T − R)/(R − S).
  aftermath: >-
    The Stanford Encyclopedia names the continuation probability "the shadow of the future" and records the
    qualifications: Axelrod's criteria do not prove TIT FOR TAT best; it is not in general subgame perfect; under
    errors two TIT FOR TATs fall to the payoff of random play; Generous TIT FOR TAT and Pavlov did better under
    evolution with noise; success depends on the field of entrants (a 2004–2005 replication placed TIT FOR TAT
    fourteenth of fifty); and other authors proved no strategy in the evolutionary dilemma is evolutionarily stable.
  effect_reversed: not-applicable
model:
  modules: [Lease_A1, Coupling, Observers, Correlator, proposed:RepeatedPairing]
  properties: [LeaseAuthorityMonotone, RevokedStaysStopped, NoAdmitWithoutLiveObserver, UnreadBounded, DenyByAnyOf]
  mutations: [M_RENEW, M_REVOKE, M_NOCOUPLE]
  records: [ADR-0031, ADR-0038, ADR-0039, ADR-0035, ADR-0062, ADR-0063, ADR-0045, ADR-0007, ADR-0032, ADR-0068]
  findings: [TM11, CR-2]
  fault_class: self-interested players whose cooperation is held up by repetition; seen from above them, the same mechanism holds up collusion
sources:
  - https://public.websites.umich.edu/~axe/research/Axelrod%20and%20Hamilton%20EC%201981.pdf
  - https://plato.stanford.edu/entries/prisoner-dilemma/
verified: 2026-11-12
---

## Summary

In the Prisoner's Dilemma each player cooperates or defects. Defecting pays more whatever the other does (T > R and
P > S), yet two defectors each get P, less than the R two cooperators get. Robert Axelrod invited strategies for the
repeated game and played them against each other.

The first tournament had 14 entries and a random rule, round robin, 200 moves a game. The highest average score went
to the simplest entry, Anatol Rapoport's TIT FOR TAT: cooperate on the first move, then do what the other player did
on the move before. Results were circulated and a second round drew 62 entries from six countries, with the game's
length made uncertain (probability w = .99654 that a move is not the last). Rapoport entered TIT FOR TAT again, and it
won again. In an ecological rerun, each rule entered in proportion to its previous success, it displaced the others.

Axelrod and Hamilton (Science, 1981) set the result in evolutionary terms. With a known number of rounds both sides
defect on the last, hence on the one before, back to the first. With a probability w of meeting again, cooperation by
reciprocity can be stable.

## Defensive position

**Axelrod and Hamilton's case for reciprocity:**

- TIT FOR TAT's success came from being nice, provocable and forgiving, and it did well in "a variegated environment"
  of more and less sophisticated rules.
- Once established, it resists invasion by any mutant if and only if w is large enough: neither ALL D nor alternating
  D and C can do better against it, and if neither can, no strategy can.
- Cooperation based on reciprocity "can get started in an asocial world, can thrive while interacting with a wide
  range of other strategies, and can resist invasion once fully established", given a probabilistic chance of
  meeting again.

## Adversarial position

**The limits, as the Stanford Encyclopedia collects them:**

- Axelrod's criteria are "not precise enough" for a proof that TIT FOR TAT is best; it is one Nash equilibrium among
  many, and not in general subgame perfect.
- It is fragile to error: two imperfect TIT FOR TATs approach the average payoff of random play, and forgiving
  variants (Generous TIT FOR TAT, Pavlov) predominate in evolutionary runs with mistakes.
- Rankings depend on the field of entrants and on the payoff values; Binmore is cited as sceptical.
- **Axelrod and Hamilton themselves**: ALL D is evolutionarily stable for every w, and with a known end it is the only
  stable strategy. Reciprocity needs a future of uncertain length.

## Outcome

The tournaments established TIT FOR TAT's robustness in their fields and the condition on w under which reciprocity is
stable. Later work kept the shadow of the future as the variable that matters and dropped any claim that TIT FOR TAT
is best, especially with noise. No effect to reverse.

## Analysis

**Does a one-round lease turn every interaction into a one-shot game?** No. The lease is per round (ADR-0031 §2), but
the principal persists. A successor grant leases it again next round, its Persona stays, its cell has one Observer
seat (ADR-0038 §1), and its record survives in the log. The probability of meeting again is high. What the one-round
lease removes is **the mechanism's reciprocity**. "Across rounds, as within one, authority never grows without a
quorum." A cooperative round earns nothing (Lease_A1's `LeaseAuthorityMonotone`, broken by `M_RENEW`). A defection
that draws a targeted revocation ends the lease and bars the principal for good (`RevokedStaysStopped`, broken by
`M_REVOKE`; ADR-0031 §5: "a re-admitted Persona is a new Persona"). In Axelrod's terms the mechanism plays a fixed
envelope plus a grim trigger, not TIT FOR TAT: never nicer, never forgiving.

**That is what the design wants, for safety.** Axelrod and Hamilton's own result is that ALL D is stable for every w.
A design that counted on the shadow of the future to keep agents in line would fail against the one strategy the
premise assumes (ADR-0007). The envelope holds whatever the agent's payoffs. The known last move confirms it. A lease's
count is exact (ADR-0062 §2) and an intent grants at most its budget of leases (ADR-0063 §4), so a mission has a known
last round. There, by backward induction, deterrence is worth nothing, and nothing a governor permitted can be void
(ADR-0062 §6). The defence at the end is the timing budget and inexpressibility (ADR-0032 §4), not the threat of a
next round.

**The grim trigger has a price under noise.** The tournaments' sequel shows deterministic retaliation collapsing
under error. A false finding in TOPAK that leads to a targeted revocation bars an honest principal permanently.
Revocation subtracts (ADR-0031 §5), so that is a loss of availability only. But ADR-0068 leaves open a false-finding
rate for a plane with nobody in reach (Z3) and an Observer that accuses (Z4), and under a grim rule every false
positive is a seat lost until a new promotion seats a new Persona. Lifting a revocation would add authority, and no
record says who may, so the corpus has chosen the grim side without stating it as a choice.

**Where the shadow of the future works against TOPAK: the pairs that are supposed to be adversaries.** A Thinker and
its cell Observer meet every round, in the same cell, with no known last round. That is the condition under which
Axelrod and Hamilton show reciprocity is stable. Seen from the mechanism, their "cooperation" is TM11's colluding
Observer: silent for a Thinker that, in exchange, does something the Observer's side values, or simply leaves it be.
It needs no message, only memory of the other's past moves, as the retaliating bids in 1997-GAM-FCC-CODE-BIDDING
needed no code.
Coupling cannot see it (ADR-0039 §5; `NoAdmitWithoutLiveObserver` holds of a colluding Observer, and `UnreadBounded`
is "empty" under collusion because the watermark is its own assertion). Lineage independence (ADR-0035) addresses
common origin, not repeated-game incentives. CR-2's collusion case is still open.

**What it suggests.** Axelrod's lever is w, and the corpus could lower it where it wants no cooperation:
`proposed:RepeatedPairing` would assign a Thinker's watchers from a pool, per round, so that a pair's chance of meeting
again is a declared parameter. Its property would be that no Observer watches the same Thinker in more than a declared
share of a window, and its mutation a fixed pairing. It would not touch `DenyByAnyOf` (Observers.tla), since any of
the round's watchers may still deny. The second question is memory. TIT FOR TAT needs the last move. The correlator
keeps a store across windows (ADR-0038 §1); this entry did not find a record that says what a cell Observer may carry
from one round to the next, and that is what decides whether it can play TIT FOR TAT with its Thinker. The outside
steps are the tournament's own moves: no module has a payoff, a strategy conditioned on history, or a pairing that
repeats by design.
