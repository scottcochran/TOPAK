# Proof style: the TLAPS proof module

How a proof module is laid out and why each piece is where it is. The
module proves the invariants its base module states, as `Spec => []P`, for
every value of the constants the named assumptions admit, under the
hypothesis that the mutations which break `P` are absent.

## Contents

- [What a proof module claims](#what-a-proof-module-claims)
- [Layout](#layout)
- [The type invariant lemma](#the-type-invariant-lemma)
- [The Next lemma](#the-next-lemma)
- [The theorem](#the-theorem)
- [SafeAlways](#safealways)
- [Mutation lemmas](#mutation-lemmas)
- [The inductive-invariant patterns](#the-inductive-invariant-patterns)
- [Step hygiene](#step-hygiene)

## What a proof module claims

- **It extends a frozen module and never edits it.** `EXTENDS Coupling,
  TLAPS`. Nothing from the base is restated. If the base states a fact as
  an unnamed `ASSUME`, the proof proves it as a named lemma, because the
  prover does not use an unnamed module assumption.
- **It proves `Spec => []P` for each invariant** the base states, under
  named constant assumptions (`ASSUME KNat == K \in Nat`) that are the
  constraints the run scripts supplied per row, and no more. A bound that
  only cuts the state space is not assumed, so the theorem covers every
  value of it.
- **Each theorem takes as hypothesis only the mutations that break it**,
  `ASSUME Mut # "M_X"`. A combined `SafeAlways` takes `Mut = "none"`.
- **Mutations and witnesses stay with TLC.** The proof carries one lemma per
  mutation saying what the mutation admits; the counterexample is in the
  TLC results file the proof's results file names.
- **The results file is the evidence**: the digests of every module in the
  `EXTENDS` chain and of the prover, the assumptions, the theorems and
  lemmas by name, the prover's obligation count, non-zero exit on any
  failure. Dated, never edited.

## Layout

In this order, each section separated by a rule:

```tla
---------------------------- MODULE Coupling_proof ----------------------------
(* Header: each THEOREM with its hypothesis in brackets; the inductive          *)
(* strengthening in prose; "the base is cited by digest and not edited"; how    *)
(* to check.                                                                    *)
EXTENDS Coupling, TLAPS

ASSUME KNat == K \in Nat
ASSUME RNat == R \in Nat
ASSUME MaxRoundNat == MaxRound \in Nat

TypeOK == ...                 \* functions over the principal set; counters in Nat
Shape  == TypeOK /\ Future /\ MarkLeSeq /\ SealedIdle    \* holds under every mutation
InvU   == Shape /\ Past /\ Bound                          \* needs the coupling
-----------------------------------------------------------------------------
LEMMA InitShape == Init => Shape
LEMMA QuietActions == ...     \* the actions that touch none of the variables in question
LEMMA NextShape == Shape /\ [Next]_vars => Shape'
-----------------------------------------------------------------------------
(* One section per property: Init lemma, Next lemma, Inv => P, THEOREM.         *)
-----------------------------------------------------------------------------
THEOREM SafeAlways == ASSUME Mut = "none" PROVE Spec => []Safe
-----------------------------------------------------------------------------
(* Why the mutations must fail. The counterexamples are TLC's.                  *)
LEMMA MutNoCoupleAllowsAll == ASSUME Mut = "M_NOCOUPLE" PROVE Allowed
=============================================================================
```

Write the definitions of the inductive invariant **before** any lemma, and
write the header's prose description of the strengthening **before** the
definitions. If the prose cannot be written, the invariant is not yet
understood and the `Next` lemma will fail in uninformative places.

## The type invariant lemma

First, under every mutation, as its own `Init` and `Next` lemma:

```tla
LEMMA NextTypeOK == TypeOK /\ [Next]_vars => TypeOK'
<1> SUFFICES ASSUME TypeOK, [Next]_vars PROVE TypeOK' OBVIOUS
<1>1. CASE UNCHANGED vars
    BY <1>1 DEF TypeOK, vars
<1>2. ASSUME NEW s \in Seats, NEW p \in Principals, Grant(p, s) PROVE TypeOK'
    BY <1>2 DEF Grant, TypeOK, LeaseRec, KindBound
...
<1> QED
    BY <1>1, <1>2, <1>3, <1>4 DEF Next
```

Every later lemma cites it as a fact (`BY <1>0, ...` where `<1>0. TypeOK`),
not only in `DEF`: a step about `lease'[q]` for `q # p` after an `EXCEPT`
needs the function's domain among the hypotheses.

For a module whose shared strengthening holds under every mutation,
bundle it with the type invariant (`Shape` above) and prove it once; the
clauses that need the mechanism sit on top in a second invariant, each
under its own hypothesis.

## The Next lemma

One per invariant group, hypotheses in its `ASSUME`, one step per action:

```tla
LEMMA NextInvU ==
    ASSUME Mut # "M_MARK", Mut # "M_ROUNDS", Mut # "M_NOCOUPLE", InvU, [Next]_vars
    PROVE  InvU'
<1>0. Shape /\ Shape'
    BY NextShape, KNat, RNat, MaxRoundNat DEF InvU, Rounds
<1>1. CASE UNCHANGED vars
    BY <1>0, <1>1, KNat, RNat, MaxRoundNat DEF InvU, Past, Bound, vars, Rounds
<1>2. CASE GrantT
    <2>1. /\ round < MaxRound /\ round' = round + 1 /\ tLive' = TRUE /\ seq' = 0 /\ ~tLive
          /\ (round >= 1 => mark[round] >= seal[round])
          /\ UNCHANGED <<mark, seal>>
        BY <1>2, KNat, RNat, MaxRoundNat DEF GrantT, Rounds
    <2>2. round >= 1 => mark[round] = seal[round]
        BY <1>0, <2>1, KNat, RNat, MaxRoundNat DEF Shape, TypeOK, MarkLeSeq, SealedIdle, Rounds
    <2>3. Past'
        BY <1>0, <2>1, <2>2, KNat, RNat, MaxRoundNat DEF Shape, TypeOK, InvU, Past, Rounds
    <2>4. Bound'
        BY <1>0, <2>1, KNat, MaxRoundNat, RNat DEF Shape, TypeOK, Future, Bound, Rounds
    <2> QED
        BY <1>0, <2>3, <2>4, KNat, RNat, MaxRoundNat DEF InvU, Rounds
<1>5. ASSUME NEW r \in Rounds, NEW w \in 0..R, Heartbeat(r, w) PROVE InvU'
    ...
<1>6. CASE Refuse \/ GrantO \/ EndO \/ Stale
    <2>1. UNCHANGED <<round, tLive, seq, mark, seal>>
        BY <1>6, QuietActions
    <2> QED
        BY <1>0, <2>1, KNat, RNat, MaxRoundNat DEF InvU, Past, Bound, Rounds
<1> QED
    BY <1>1, <1>2, <1>3, <1>4, <1>5, <1>6, KNat, RNat, MaxRoundNat DEF Next, Rounds
```

The shape of each action step:

1. **Name what the action does** as a `<2>1` conjunction of its primed
   equalities and `UNCHANGED`s, proved `BY <1>k DEF Action`. This is the
   only step that expands the action; every later step uses the named
   facts. It is also where a large action's `LET` gets named part by part.
2. **State the intermediate fact** the clause needs (`<2>2`), from the
   current invariant and the action's facts.
3. **One step per clause of the primed invariant** (`Past'`, `Bound'`),
   then QED from them. A step that bundles several primed clauses can fail
   where each alone proves.
4. **Group the quiet actions**: one `QuietActions` lemma that the actions
   which touch none of the relevant variables leave them `UNCHANGED`, cited
   by one `CASE A \/ B \/ C` step.

Where an action is an `IF` or `CASE` with different successors, state its
outcomes as a disjunction in one step and let the backend split.

## The theorem

Three lines, always the same:

```tla
THEOREM UnreadBoundedAlways ==
    ASSUME Mut # "M_MARK", Mut # "M_ROUNDS", Mut # "M_NOCOUPLE"
    PROVE  Spec => []UnreadBounded
<1>1. InvU /\ [Next]_vars => InvU'
    BY NextInvU
<1> QED
    BY InitInvU, <1>1, InvUBounded, PTL, KNat, RNat, MaxRoundNat DEF Spec, Rounds
```

`InvUBounded == InvU => UnreadBounded` is a state lemma proved separately,
with the arithmetic (`mark[round] \in Nat`) spelled out as steps. When the
invariant is the property itself, the lemma is not needed.

A property that is **valid in every state** under its hypothesis (an
`ENABLED` invariant, or `Rung0NeverContained`, true by the definition of
`Contained`) needs no induction: prove it as a state lemma and the
theorem is `BY TheLemma, PTL DEF Spec`.

## SafeAlways

```tla
THEOREM SafeAlways ==
    ASSUME Mut = "none"
    PROVE  Spec => []Safe
<1>1. Spec => []NoAdmitWithoutLiveObserver
    BY NoAdmitWithoutLiveObserverAlways
<1>2. Spec => []UnreadBounded
    BY UnreadBoundedAlways
<1> QED
    BY <1>1, <1>2, PTL DEF Safe
```

One explicit `Spec => []P` step per theorem, **before** the `PTL` step. The
backend cannot discharge a theorem's `Mut` hypothesis inside `PTL`; citing
`UnreadBoundedAlways` directly in the QED fails.

## Mutation lemmas

Last, one per mutation, stating in the module's vocabulary what the
mutation admits. The strongest form, when the mutation enables an action,
is an `ENABLED` statement:

```tla
LEMMA MutRoundsGrantsUncovered ==
    ASSUME Mut = "M_ROUNDS", TypeOK, ~tLive, round < MaxRound
    PROVE  ENABLED GrantT
BY ExpandENABLED DEF GrantT, TypeOK

LEMMA MutMarkIgnoresBacklog ==
    ASSUME Mut = "M_MARK", oLease, fresh
    PROVE  LiveO
BY DEF LiveO
```

They are not the counterexample; TLC's results file holds that. They make
the proof's hypothesis and TLC's counterexample name the same guard, so a
reader can see that `Mut # "M_ROUNDS"` in the theorem and
`c-rounds-unread | COUNTEREXAMPLE` in the results file are about one check.

A module's unnamed `ASSUME`s (that genesis satisfies the floor; that every
entry is independently droppable) belong here too, as lemmas with explicit
witness records: they are the "why dropping must fail" lemmas for that
module.

## The inductive-invariant patterns

In the order to try them:

- **Flag invariants.** `~admittedUnlive`. The action sets the flag to
  `flag \/ cond`; show `cond` is false under the hypothesis at that one
  action. No auxiliary invariant.
- **Append-only record sets.** The property quantifies over the set; the
  auxiliary says what the appending action can append, as a state fact
  that is the guard's precondition ("a live lease's alphabet is within its
  seat's kind bound"). Prove the auxiliary with `TypeOK`, under every
  mutation where it holds (fold the mutation into a constant operator so it
  does), and split each property on top.
- **Valid state predicates.** True of every state under the hypothesis by
  definition. State lemma; `PTL` lifts it.
- **A type invariant proved once, under every mutation,** cited by every
  lemma.
- **Constant operators that carry the mutation** (`ByKind(s)`), so the
  shared auxiliary holds under every mutation.
- **Weakest hypothesis per theorem.** Hypotheses may be floor entries in
  force rather than mutations, and may be a formula: "R2 and either R1 or
  R9" is the premise table's "binds only with R1 relaxed" made exact.
- **Established and frozen.** When every action after a commit needs the
  commit flag false, prove the property at the commit action and carry it
  with "every step is the commit or leaves the values alone".
- **Arithmetic invariants in layers.** Ask what each action needs of the
  state to keep the bound; the clauses that hold under every mutation go in
  `Shape`, the rest on top. A successor module that adds one counter adds
  one layer and reuses the rest.
- **ENABLED as an invariant.** `(tLive /\ acts < R) => ENABLED Consult`
  holds in every state under its hypothesis: a state lemma `BY
  ExpandENABLED DEF Consult`, lifted by `PTL`. See the translation rules in
  [prover-habits.md](prover-habits.md) before carrying such a fact across a
  quantifier.
- **Generation binding.** When the record appended depends on state set
  several actions earlier (launch, appraisal, grant, then act), the
  invariant carries the history forward conditionally on "same
  generation": a live guest carries the current generation; an appraisal
  and a lease remember a generation no later than the current one; while
  the guest with that generation stands, the asked image is the profile's
  and was booted. Each clause is preserved because a relaunch strictly
  raises the generation. Six such clauses were needed once; budget for
  inventing them.
- **A property over every record, not only live ones.** When a regrant
  revives a lease the stated property is silent about, prove the stronger
  invariant over every lease the seat has had, and derive the stated
  property from it.

## Step hygiene

- Every step that reads an indexed value (`mark[round]`) needs the index
  domain (`DEF Rounds`) and the `Nat` assumptions in scope. Omitting them
  was the single most common failure across two arithmetic modules.
- Chaining inequalities through such a value needs an explicit
  `mark[round] \in Nat` step.
- A `WITNESS` step takes no `DEF`, so it cannot show a record is in a
  record set. `DEFINE w == ...`, prove `w \in S` and the property as two
  steps, and let QED find the witness.
- Keep each `BY` list honest: cite the facts the step uses and the
  definitions it must see, no more. A step that cites every lemma in the
  module proves slowly and tells the next reader nothing about why it
  holds.
- Comment the strengthening at the definitions and the reason at the step,
  not the mechanics. The header's prose should let a reader predict which
  steps exist.
