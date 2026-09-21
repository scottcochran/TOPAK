<!-- RECOVERED · HISTORICAL · 2026-09-15 · tranche 3 -->
> **Recovery note.** Source: TLA+ best practices for Paxos modeling session 09.13 (https://claude.ai/chat/566f11d6-b049-47b2-b826-a9450dfed8b4), `create_file` turn 1, file `tlaplus-paxos-cheat-sheet-2026.09.13.md`. No later edits.
>
> **Reference, not design content.** §10 maps onto the 09.12 checkpoint and predates ADR-0026's rules-floor non-vacuity check, which carries out the mutation gate §10 recommends.
>
> Text below is verbatim from session history (HTML entities normalized). **Historical artifact:**
> nothing folds into it. Later corrections live in the records and checkpoints that supersede it.

# TLA+ for Distributed Consensus — Working Cheat Sheet

**2026.09.13** · companion to the TOPAK Theory of Operation checkpoint series · *The Gripping Hand*

Scope: specifying and checking Paxos-family consensus in TLA+ (Temporal Logic of Actions).
Organized as idioms you should reach for, traps that cost days, and the specific shape the
TOPAK `Run` domain needs. Section 10 is the TOPAK-specific part; 1–9 are general.

---

## 1. Choose the right abstraction level first

The single highest-leverage decision, made before any syntax.

| Level | What it models | When |
|---|---|---|
| `Consensus` | One variable `chosen`, a set that goes from `{}` to a singleton | The property you are actually promising |
| `Voting` | Acceptors, ballots, quorums — **no messages** | Where the real argument lives |
| `Paxos` | Messages, phases, per-acceptor state | Where implementers look |

**Write all three and connect them by refinement.** This is Lamport's own layering and it is
not academic decoration: the interesting invariant (`SafeAt`) is provable at the `Voting` level
where there are no messages to reason about, and `Paxos` then inherits it for free. Going
straight to message-passing Paxos and trying to prove agreement there is the most common way to
spend a month and get nothing.

```tla
V == INSTANCE Voting WITH maxBal <- maxBal,
                         votes  <- [a \in Acceptor |->
                                      {<<m.bal, m.val>> : m \in {mm \in msgs :
                                         /\ mm.type = "2b"
                                         /\ mm.acc  = a}}]
THEOREM Spec => V!Spec
```

If the refinement mapping is hard to write, the lower spec is wrong. That difficulty is signal,
not friction.

---

## 2. Plain TLA+, not PlusCal

PlusCal's implicit program counter forces an interleaving and a control-flow shape onto a
protocol that has neither. Paxos actions are enabled by *state*, not by *position in a
procedure*. Write action-oriented TLA+:

```tla
Next == \/ \E b \in Ballot          : Phase1a(b)
        \/ \E a \in Acceptor        : Phase1b(a)
        \/ \E b \in Ballot, v \in Value : Phase2a(b, v)
        \/ \E a \in Acceptor        : Phase2b(a)
```

PlusCal is fine for algorithms with genuine sequential structure (a lock protocol, a cache
coherence client). It is the wrong tool for consensus.

---

## 3. The message-set idiom

The most important single line in a consensus spec:

```tla
VARIABLE msgs
Send(m) == msgs' = msgs \cup {m}
```

**Messages are never removed.** This one choice models, for free and with zero extra state:

- **Loss** — a message that is in `msgs` and never acted on
- **Duplication** — an action can fire on the same message any number of times
- **Reordering** — no ordering exists to violate
- **Delay** — unbounded, by construction

Consequences to internalize:

- Every receive action must be **idempotent**, or your spec is wrong. Check this deliberately.
- Actions must be **enabled by message presence, not by consumption**. `Phase1b(a)` is enabled
  whenever a suitable `1a` message exists and `a` hasn't advanced past it.
- The set is monotone, so you get no "eventually delivered" for free — see §6.
- Do **not** model a Byzantine sender by adding a `Fake` action that sends arbitrary messages
  into the same set unless you also partition `Acceptor` into honest and faulty. Refine the
  Byzantine case properly (§8).

---

## 4. Constants, quorums, and the assumption you must write down

```tla
CONSTANTS Value, Acceptor, Quorum

ASSUME QuorumAssumption ==
    /\ \A Q \in Quorum : Q \subseteq Acceptor
    /\ \A Q1, Q2 \in Quorum : Q1 \cap Q2 # {}

Ballot == Nat
None   == CHOOSE v : v \notin Value
```

Notes that matter:

- **Quorums are a constant, not a derived majority.** Parameterizing on the intersection
  property rather than on `2f+1` is what lets the same spec cover flexible quorums, grid
  quorums, and weighted configurations. Cost: nothing. Do it.
- For Byzantine variants the assumption strengthens to three-way intersection with an honest
  survivor: `\A Q1, Q2 \in Quorum : Q1 \cap Q2 \cap Honest # {}` (or `|Q1 \cap Q2| > f`).
- `ASSUME` is checked by the model checker at startup against your concrete instantiation.
  A spec whose quorum assumption is not stated will happily "verify" with a broken quorum
  system supplied in the config.
- `None` via `CHOOSE` avoids polluting `Value` with a sentinel that then shows up in your
  agreement invariant.

---

## 5. Safety: the invariant chain

Agreement is the theorem. It is never the inductive invariant. Build the chain explicitly:

```tla
VotedForIn(a, v, b) == \E m \in msgs : /\ m.type = "2b"
                                       /\ m.acc  = a
                                       /\ m.bal  = b
                                       /\ m.val  = v

ChosenIn(v, b) == \E Q \in Quorum : \A a \in Q : VotedForIn(a, v, b)
Chosen(v)      == \E b \in Ballot : ChosenIn(v, b)

Consistency == \A v1, v2 \in Value : Chosen(v1) /\ Chosen(v2) => v1 = v2
```

The load-bearing predicate is **`SafeAt`** — "no value other than `v` can ever be chosen at any
ballot below `b`":

```tla
SafeAt(v, b) ==
    \A c \in 0..(b-1) :
        \E Q \in Quorum :
            \A a \in Q : /\ maxBal[a] > c
                         /\ \A w \in Value : VotedForIn(a, w, c) => (w = v)
```

`SafeAt` is a statement about the *future* expressed entirely over the *present*. That is the
whole trick of Paxos, and it is the thing to make sure a reader of your spec sees.

**Practical discipline:**

1. Always write `TypeOK` and check it first. A failing `TypeOK` means your spec is broken, not
   your protocol; debug that before anything else.
2. Check `Consistency` as an invariant on small models to find real bugs fast.
3. Only then build `Inv == TypeOK /\ msgInv /\ accInv` for the inductive proof. Expect
   `msgInv` to be a conjunct per message type, and expect two or three rounds of strengthening.
4. TLC (the TLA+ model checker) can check inductiveness directly: model-check
   `Inv /\ [Next]_vars => Inv'` with `Inv` as the initial predicate. This finds missing
   conjuncts in seconds instead of during a TLAPS (TLA+ Proof System) proof attempt.

---

## 6. Liveness: say the quiet part out loud

FLP (Fischer–Lynch–Paterson) says you cannot have it unconditionally. So the spec must
*name its assumption* rather than quietly assume it away.

```tla
LSpec == /\ Spec
         /\ \A a \in Acceptor : WF_vars(Phase1b(a) \/ Phase2b(a))
         /\ \E b \in Ballot : <>[] (LeaderIs(b))   \* eventual stable leader
```

Points that bite:

- **Weak fairness on receive actions is the right default.** Strong fairness (`SF_vars`) on a
  Paxos action is usually a sign you are papering over a missing leader assumption — it says
  "an action enabled infinitely often but not continuously must fire," which quietly assumes a
  scheduler you do not have.
- **A monotone `msgs` set makes message loss invisible to fairness.** A message stays enabled
  forever, so `WF` on the receive gives you eventual delivery of *everything ever sent*. If you
  need to model genuine permanent loss, add an explicit `lost` set or a per-message delivery
  flag — and accept the state-space cost.
- **Dueling proposers are the liveness bug.** Without a stability assumption, TLC will find the
  infinite ballot-escalation trace immediately. That trace is correct and famous; don't "fix"
  the spec to eliminate it.
- **Liveness checking is dramatically more expensive than safety.** Check it on the smallest
  model that can exhibit the behavior (2–3 acceptors, 2 values, 2–3 ballots) and never with
  symmetry sets enabled.

---

## 7. Model checking without lying to yourself

**Finite instantiation.** `Ballot == Nat` is unmodelable. Override in the config:

```
Acceptor = {a1, a2, a3}
Value    = {v1, v2}
Ballot   <- 0..2
```

Three acceptors, two values, two or three ballots finds essentially every real Paxos bug. Going
to five acceptors buys nothing but wall-clock time.

**State constraints prune, they do not prove.**

```tla
StateConstraint == \A m \in msgs : m.bal =< MaxBallot
```

A constraint truncates the graph. Any counterexample past the boundary is invisible. Treat
constrained runs as testing, not verification, and say so when you write up results.

**Symmetry.**

```tla
Symmetry == Permutations(Acceptor)
```

Real speedup (roughly `n!`). Two rules: only on constants that appear symmetrically everywhere
(`Value` usually qualifies, `Acceptor` qualifies only if quorums are symmetric — a grid quorum
system is *not* symmetric under acceptor permutation), and **never with liveness properties**,
where TLC may report a spurious result.

**Deadlock.** Turn deadlock checking *off* for consensus specs, or add an explicit stuttering
action. A terminal state with a value chosen and nothing left to do is correct behavior, and the
default deadlock check will flag it as a violation.

**TLC vs. Apalache.** TLC: explicit-state, fast on small models, best error traces, mature.
Apalache: symbolic (SMT — satisfiability modulo theories), needs type annotations, handles much
larger constant domains and is markedly better at *inductive invariant checking*. Use TLC for
exploration and error traces; use Apalache when you want `Inv` checked at a ballot range TLC
can't reach. Writing Apalache-compatible type annotations from day one costs almost nothing and
keeps the option open.

**Read the error trace properly.** TLC's counterexample is the specification's most valuable
output. Add a `Alias` / `VIEW` definition exposing derived predicates (`Chosen`, `SafeAt`,
`maxVBal` per acceptor) so the trace shows the *reasoning state*, not just raw variables.

---

## 8. Variant-specific notes

**Multi-Paxos.** Do not naively index every variable by slot — the state space multiplies. Two
tactics:

1. Specify single-decree Paxos, prove it, then specify Multi-Paxos as a separate spec that
   *refines a per-slot instance* of it. State the slot-independence argument explicitly; it is
   an assumption about your implementation not sharing acceptor state across slots, and it is
   exactly the assumption real implementations violate (shared `maxBal` across slots is the
   normal optimization).
2. Where the optimization is real, model **two slots only**. Two is enough to expose cross-slot
   interference; three tells you nothing new and costs an order of magnitude.

The genuinely new properties in Multi-Paxos are about the *log*: no gaps in the committed
prefix, and stability of committed entries under leader change. Write those as separate
invariants; they are not implied by per-slot agreement.

**Byzantine Paxos.** Follow *Byzantizing Paxos by Refinement* rather than inventing the
structure: specify non-Byzantine Paxos, then specify the Byzantine version as a refinement where
faulty acceptors' behavior is `havoc` over the message set and the abstraction function maps
faulty behavior onto legal non-Byzantine behavior. Concretely:

```tla
CONSTANT FakeAcceptor
ASSUME FakeAcceptor \cap Acceptor = {}
FakeSend == \E m \in Message : m.acc \in FakeAcceptor /\ Send(m)
```

The `havoc` framing is the same one the containment-verification literature uses for the model
itself — an unconstrained adversary admitted at a typed boundary. That parallel is worth
drawing explicitly in the write-up.

**Raft.** If you specify Raft, you are specifying leader election, log replication, and
membership change as three interacting protocols. Diego Ongaro's spec is the reference and it is
long for a reason. Do not present a short Raft spec as complete.

---

## 9. Twelve traps, in rough order of cost

1. Proving agreement at the message level instead of the voting level.
2. No `TypeOK`, or a `TypeOK` that isn't checked first.
3. Removing messages from `msgs` on receipt — silently eliminates loss and duplication.
4. A receive action that isn't idempotent under the never-remove idiom.
5. `Quorum` defined as `{Q \in SUBSET Acceptor : |Q| * 2 > |Acceptor|}` with no `ASSUME`,
   so the intersection property is accidental rather than stated.
6. Deadlock checking left on, producing a false violation at the terminal chosen state.
7. Symmetry enabled while checking a liveness property.
8. A state constraint presented as a verification result.
9. `SF_vars` sprinkled on actions to make liveness pass, hiding a missing leader assumption.
10. Modeling crash-stop by disabling an acceptor's actions, without noticing that recovery with
    lost durable state is a *different* and much worse failure mode. If you claim durability,
    model the write explicitly.
11. Overriding `Ballot <- 0..1`, which is too small to exhibit the interesting Phase 1b
    reconciliation.
12. Treating the finished spec as covering the implementation. It covers the protocol. The
    spec-to-code gap is a separate obligation — conformance testing against the trace, a
    generated test oracle, or deductive verification of the implementation.

---

## 10. TOPAK-specific

Where this lands against the 2026.09.12 checkpoint.

**Paxos orders orchestrator decisions, not agent opinions.** The spec's `Value` domain is
control-plane decisions about principals — admit, evict, grant, rung change — not agent output.
Make this structural in the spec by typing `Value` as a decision record. Readers arrive assuming
consensus among agents; the type declaration is the cheapest correction available.

**Consensus-for-grants, local-for-denials is a checkable property, and should be checked.**
The monotonicity through-line of §3 of the checkpoint has a direct TLA+ statement:

```tla
DenialAlwaysEnabled ==
    \A a \in Principal : ENABLED Deny(a)

GrantRequiresQuorum ==
    \A v \in Value : Granted(v) => \E Q \in Quorum : \A n \in Q : Accepted(n, v)
```

The first is an invariant over `ENABLED`, which is unusual but legitimate and exactly the right
formalization of "a denial never waits on consensus." It is also the property that makes the
HOTL (human-on-the-loop) argument in §4 of the checkpoint mechanical rather than asserted: an
on-the-loop human can only take the action that is always enabled.

**`W < L < D` is a real-time property and TLA+ will not give it to you directly.** Standard
TLA+ has no clock. Three options, in increasing cost: (a) model the window as a bounded counter
of steps and prove the ordering over that discrete abstraction, (b) use the explicit-time idiom
from *Real Time is Really Simple* with a `now` variable and `RTBound`, (c) keep timing out of
the TLA+ spec entirely and discharge it as a separate operational obligation. Option (a) is
usually right, but the abstraction choice must be documented — an unstated step-to-time mapping
is a gap of exactly the kind the external assessment flagged.

**HITL / HOTL / HOOTL are already in checkable form.** The checkpoint's definitions are
enabling-condition definitions, which means they are literally `ENABLED` predicates:

- HITL: `ENABLED Advance => HumanActed`
- HOTL: `HumanActed => ~ENABLED Advance` (subtraction only), with `ENABLED Advance` independent
  of the human otherwise
- HOOTL: no `Human*` action in `Next`

That third one is the useful one — HOOTL is a *syntactic* property of the spec, checkable by
inspection, which makes "no channel exists" auditable rather than asserted.

**Refinement is doing double duty, and the two uses should be kept apart in the write-up.**
`bundle ⊑ floor` (ADR-0010) is policy refinement checked at Build by SMT over a finite action
alphabet. `Paxos ⊑ Voting ⊑ Consensus` is specification refinement checked by TLAPS or TLC.
Same word, same underlying notion of implication, entirely different artifacts and cadences.
Readers who know one will assume the other.

**The vacuity exposure applies here too.** §4.6 of Moon & Varshney is about a boundary predicate
quantifying over an always-empty field. The TLA+ analogue is an invariant whose antecedent is
never satisfied on any reachable state — it passes, permanently, and means nothing. Guard
against it the same way: seed a mutation that *should* break each invariant and confirm it does.
A "non-vacuity gate" on TLA+ invariants is the same gate as ADR-0007's, applied to the other
verification artifact, and as far as I can tell the checkpoint doesn't yet say so.

---

## 11. Specs worth reading before writing your own

- `Paxos.tla` and `Voting.tla` — Lamport, in the TLA+ examples repository. The refinement
  layering above, in its original form.
- *Byzantizing Paxos by Refinement* — Lamport, 2011. The structural template for the Byzantine
  variant.
- `raft.tla` — Ongaro. Instructive on scale and on what a complete spec costs.
- *Real Time is Really Simple* — Lamport, MSR-TR-2005-30. The `now`-variable idiom for §10's
  timing question.
- *Specifying Systems*, Part I and §8 — the model-checking chapter is the one people skip.
- AWS's *Use of Formal Methods at Amazon Web Services* — for the argument about what this buys
  in production, which you will need in the article's framing section.
