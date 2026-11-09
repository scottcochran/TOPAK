# Specification design: write for the proof you will want

How to write a TLA+ module so that TLC can flip every claim and the prover
can discharge every invariant cheaply. The two goals coincide: a module
written for mutation testing instruments each property at the one action
that could violate it, and that instrumentation is what makes the
invariant inductive.

## Contents

- [Locality](#locality)
- [The three devices](#the-three-devices)
- [Mutations](#mutations)
- [Reachability witnesses](#reachability-witnesses)
- [The type invariant](#the-type-invariant)
- [Shallow actions and literal domains](#shallow-actions-and-literal-domains)
- [Constants](#constants)
- [The header is the contract](#the-header-is-the-contract)
- [Liveness, only when claimed](#liveness-only-when-claimed)
- [A worked module](#a-worked-module)

## Locality

A property is local when it can be violated by exactly one action and that
action's guard decides, in the current state, whether it would. The
inductive step for a local property is a propositional check of the
guard. Properties that are not local need history carried in the state,
and the invariant that carries it has to be invented.

Monotonicity is the mechanism that buys locality: a flag that only rises
and a set that only grows cannot be un-violated, so the proof never has to
reason about what happened before. The results file's "Breaks under"
column, which says which mutation breaks which property, becomes a list
of which guard each proof will rest on.

## The three devices

**A write-once flag at the violating action.**

```tla
Admit ==
  /\ tLive /\ seq < R /\ Allowed
  /\ seq' = seq + 1
  /\ admittedUnlive' = (admittedUnlive \/ ~LiveO)
  /\ UNCHANGED <<round, tLive, oLease, fresh, mark, seal, refusedForCorr, refused>>

NoAdmitWithoutLiveObserver == ~admittedUnlive
```

The flag's condition (`~LiveO`) is exactly the guard the mutation removes
(`Allowed` requires `LiveO` unless `Mut = "M_NOCOUPLE"`). The proof of the
`Admit` case is: under `Mut # "M_NOCOUPLE"`, `Allowed` implies `LiveO`, so
the flag stays false.

**An append-only set of records the property quantifies over.**

```tla
Act(s) ==
  /\ lease[s].live
  /\ \E a \in lease[s].alphabet :
       acted' = acted \cup {[seat |-> s, kind |-> KindOf[s], act |-> a]}
  /\ UNCHANGED lease

OnlyThinkersAuthor ==
  \A x \in acted : x.act \in Authoring => x.kind = "thinker"
```

The property is over `acted`; the inductive strengthening is the state
fact "a live lease's alphabet is within its seat's kind bound", which is
`Grant`'s guard written over the state. Prove that fact once; each
property then follows at `Act` from it.

**Every mechanism check as a guard on the action that needs it.** Put
`mark[round] >= seal[round]` in `GrantT`, not in a property about rounds.
A check in a guard is something a mutation can remove; a check inside a
property cannot be flipped and will not be found missing.

## Mutations

One constant `Mut`, a string. `Mut = "none"` is the mechanism as the
design specifies it. Each `Mut = "M_X"` removes one guard or weakens one
check, and the header says which property it must break:

```tla
(* Mut = "M_MARK":   live(o) tests the heartbeat and not the watermark, so a *)
(*                   fresh but starved Observer passes. UnreadBounded fails.  *)
```

Rules:

- **One guard per mutation.** A mutation that removes two guards cannot say
  which one the property rested on.
- **Write the mutation where the guard is**, as `IF Mut = "M_X" THEN TRUE
  ELSE guard`, or fold it into a constant operator:

  ```tla
  Coupled == Mut # "M_NOCOUPLE"
  Allowed == (~Coupled \/ LiveO) /\ (Mut # "M_CORR" \/ LiveC)
  ```

  A constant operator that carries the mutation keeps the actions uniform
  and lets the type invariant and the shared strengthening hold under every
  mutation, with each property splitting on top under its own hypothesis.
- **Name the design text the mutation reverts to** when there is one ("the
  record's text before R1"). A mutation that is a real earlier design is
  the most valuable kind: it shows the current text was a correction.
- **A mutation that reaches every state of the unmutated module** breaks no
  invariant and no witness. Only a liveness property can see it. Say so in
  the header and state the liveness property (see below).

## Reachability witnesses

For every claim that something can happen, a `Never…` property that must be
**violated**:

```tla
NeverRoundTwo       == round < 2              \* a second round is granted after coverage
NeverRefused        == ~refused               \* coupling refuses something
NeverBacklogRefusal == IF tLive THEN ~(refused /\ oLease /\ fresh.o /\ seq - mark[round] >= K) ELSE TRUE
```

A witness is a reachability check with the sign flipped, so one run script
and one results-file format serve both. Without witnesses a property can
hold because the state it forbids is unreachable for a reason the design
never intended, and nothing would say so. Witnesses stay with TLC forever:
the prover cannot prove that a state is reachable.

Keep a witness's flag (`refused`) distinct from the property's flag
(`refusedForCorr`): a witness that reads a flag an earlier, unrelated event
may have set is weaker than it looks, and a later module may need the
sharper form (`NeverBacklogRefusalStep`, the refusal for the backlog
itself).

## The type invariant

Functions from the principal or seat set to record sets, with the empty
record a named constant:

```tla
NoLease == [live |-> FALSE, principal |-> "none", alphabet |-> {}]
LeaseRec == [live : BOOLEAN, principal : Principals \cup {"none"}, alphabet : SUBSET Acts]
TypeOK == lease \in [Seats -> LeaseRec] /\ acted \in SUBSET ActRec
```

Its job in the proof is to put the function's domain in scope, so that
after `lease' = [lease EXCEPT ![s] = ...]` the backend can say
`lease'[q] = lease[q]` for `q # s`. Without it, every step that reads
another principal's record fails. For a module with counters and marks,
`TypeOK` also carries `seq \in Nat`, `mark \in [Rounds -> Nat]` and the
relation between the control variable and the counter (`tLive => round >= 1`),
because arithmetic steps need to know their terms are naturals.

## Shallow actions and literal domains

- **A guard, one `EXCEPT`, `UNCHANGED` for the rest.** Thirteen variables
  that are mostly `UNCHANGED` bookkeeping cost the prover nothing.
- **No `INSTANCE`, no refinement mapping** in a module whose invariants
  will be proved. Refinement is a different job, and the cheap proofs this
  method produces come from modules without it.
- **Finite, literal domains.** `Principals == {"p1", "p2"}`,
  `Seats == {"s1", "s2", "s3"}`, kinds as string literals in a record
  (`KindOf == [s1 |-> "thinker", ...]`). Two principals suffice to show
  that a rule keyed by one of them is wrong; three seats, one per kind,
  suffice to show that kinds matter. The SMT backend handles string-literal
  distinctness, `CASE`, records, `IF`, set difference and small arithmetic
  by enumeration without guidance.
- **No sequences, no recursion, no `Cardinality` in an invariant unless the
  design is about counting.** Those are the constructs the prover is weak
  on. Where a count is unavoidable, state the cardinalities the properties
  compare as terms in one guard (`PromotionEnabled`), so the proof carries
  them as terms and only the threshold case needs to know the term is a
  natural.
- **Abstract time as nondeterminism.** A heartbeat makes an observer fresh;
  it goes stale by a `Stale(x)` action that may fire at any time. No clocks,
  no timeouts in the state.

## Constants

- **Leave constants unconstrained in the module.** `CONSTANTS Mut, K, R,
  MaxRound` with a comment on what the design needs of them, nothing more.
  The run script supplies the values per row.
- **Bound in the run script, assume in the proof.** A constraint the design
  needs (`Active \subseteq AllEntries`, `MaxEpoch \in Nat`) becomes a named
  `ASSUME` in the proof module. A bound that only cuts the state space
  (`MaxRound`, `MaxEpoch` as a ceiling) needs no assumption, and the
  theorem then holds for every value of it where TLC ran one.
- **Do not put an ordering the design needs for non-vacuity into the
  proof.** `K < R` is what lets the bound refuse at all; the invariant holds
  for every `K` and `R`. The ordering is TLC's business, as a witness.
- **A module-level `ASSUME` is evaluated by TLC and ignored by the prover
  unless named.** Where a module states a fact as an unnamed `ASSUME` (that
  genesis satisfies the floor), the proof module proves it as a named lemma
  with explicit witnesses.

## The header is the contract

The module's comment block, before `EXTENDS`, carries:

1. The design document and section each property states, one line per
   property, with a one-line gloss.
2. What is modelled and what is abstracted: how many principals, how time
   and identity are treated, what the reference implementation does that
   the model mirrors (a sequence that restarts each round; a seal that is
   the sequence when the round ends).
3. One line per mutation: what it removes, what design text it reverts to,
   and which property must fail.
4. For a proof module: each theorem with its hypothesis in brackets, the
   inductive strengthening in prose, that the base module is cited by
   digest and not edited, and how to check it.

The header is what a reviewer reads instead of the state machine, and what
the results file's expected line is checked against.

## Liveness, only when claimed

State no liveness unless the design claims progress, and then:

- **Fairness as `WF_vars(A)` or `SF_vars(A)` on actions of `Next`**, never
  as a condition on states. A state condition is not machine-closed and,
  under a mutation that blocks the action, can leave a spec with no
  behaviour, under which every property holds.
- **Each fairness condition named for whose obligation it is**
  (`ObserverKeepsUp == SF_vars(KeepUp)`, `ThinkerAsks == SF_vars(Admit)`),
  with a comment saying why weak or strong: strong when the action is
  enabled only intermittently because another action may disable it first.
- **One spec per combination the properties need** (`SpecA12`,
  `SpecResume`), and one spec per condition dropped or weakened
  (`SpecNoKeepUp`, `SpecWFKeepUp`), so that a row can show each condition
  is needed and each weaker form fails.
- **A `NoBehaviour` property** (`FALSE`, or a property no behaviour
  satisfies) that must be **violated** under every fair spec a `HOLDS` row
  uses, to show the fair spec has a behaviour at all.
- **Extend the safety module rather than edit it**, with `NextL` equal to
  the base `Next` under every base mutation and a restriction of it only
  under the liveness module's own mutations, so the safety proofs carry
  over by one lemma, `SpecL => Spec`.

## A worked module

The shape, end to end, for a mechanism in which a thinker's admissions are
coupled to an observer's liveness. Properties, mutations, witnesses, type
invariant and shallow actions are all present; the proof module for it is
the worked example in [proof-style.md](proof-style.md).

```tla
----------------------------- MODULE Coupling ------------------------------
(* Properties for <design doc>, Observer liveness coupled to admission.        *)
(*   NoAdmitWithoutLiveObserver  no admit while no observer is live             *)
(*   UnreadBounded               unread emissions never exceed K                *)
(* Mut = "none":       the mechanism as specified.                              *)
(* Mut = "M_NOCOUPLE": the coupling guard is absent. The first must fail.       *)
(* Mut = "M_MARK":     live(o) ignores the watermark. UnreadBounded must fail.  *)
EXTENDS Naturals
CONSTANTS Mut, K, R, MaxRound
Rounds == 1..MaxRound
VARIABLES round, tLive, seq, oLease, fresh, mark, seal, admittedUnlive, refused
vars == <<round, tLive, seq, oLease, fresh, mark, seal, admittedUnlive, refused>>

Init == /\ round = 0 /\ tLive = FALSE /\ seq = 0 /\ oLease = FALSE /\ fresh = FALSE
        /\ mark = [r \in Rounds |-> 0] /\ seal = [r \in Rounds |-> 0]
        /\ admittedUnlive = FALSE /\ refused = FALSE

Coupled == Mut # "M_NOCOUPLE"
LiveO   == oLease /\ fresh /\ (IF Mut = "M_MARK" \/ round = 0 THEN TRUE ELSE seq - mark[round] < K)
Allowed == ~Coupled \/ LiveO

GrantT == /\ ~tLive /\ round < MaxRound
          /\ round = 0 \/ mark[round] >= seal[round]
          /\ round' = round + 1 /\ tLive' = TRUE /\ seq' = 0
          /\ UNCHANGED <<oLease, fresh, mark, seal, admittedUnlive, refused>>
Admit  == /\ tLive /\ seq < R /\ Allowed
          /\ seq' = seq + 1 /\ admittedUnlive' = (admittedUnlive \/ ~LiveO)
          /\ UNCHANGED <<round, tLive, oLease, fresh, mark, seal, refused>>
Refuse == /\ tLive /\ seq < R /\ ~Allowed /\ refused' = TRUE
          /\ UNCHANGED <<round, tLive, seq, oLease, fresh, mark, seal, admittedUnlive>>
EndRoundT == /\ tLive /\ tLive' = FALSE /\ seal' = [seal EXCEPT ![round] = seq]
             /\ UNCHANGED <<round, seq, oLease, fresh, mark, admittedUnlive, refused>>
Heartbeat(r, w) == /\ oLease /\ r <= round /\ r >= 1
                   /\ w >= mark[r] /\ w <= (IF r = round THEN seq ELSE seal[r])
                   /\ mark' = [mark EXCEPT ![r] = w] /\ fresh' = TRUE
                   /\ UNCHANGED <<round, tLive, seq, oLease, seal, admittedUnlive, refused>>
Stale  == fresh /\ fresh' = FALSE /\ UNCHANGED <<round, tLive, seq, oLease, mark, seal, admittedUnlive, refused>>
GrantO == ~oLease /\ oLease' = TRUE /\ UNCHANGED <<round, tLive, seq, fresh, mark, seal, admittedUnlive, refused>>
EndO   == oLease /\ oLease' = FALSE /\ UNCHANGED <<round, tLive, seq, fresh, mark, seal, admittedUnlive, refused>>

Next == \/ GrantT \/ Admit \/ Refuse \/ EndRoundT \/ Stale \/ GrantO \/ EndO
        \/ \E r \in Rounds, w \in 0..R : Heartbeat(r, w)
Spec == Init /\ [][Next]_vars

NoAdmitWithoutLiveObserver == ~admittedUnlive
Unread        == IF round = 0 THEN 0 ELSE seq - mark[round]
UnreadBounded == Unread <= K
Safe == NoAdmitWithoutLiveObserver /\ UnreadBounded

NeverRefused == ~refused                 \* must be VIOLATED: coupling refuses something
NeverRoundTwo == round < 2               \* must be VIOLATED: a second round is granted
=============================================================================
```

What to notice: the flag `admittedUnlive` is set only in `Admit` and only
against `LiveO`; the mutation `M_NOCOUPLE` is one constant operator;
`M_MARK` is one `IF` at the guard it weakens; `Heartbeat` is honest by its
guard (`w <= seq` or the seal), which is the fact `UnreadBounded`'s proof
will need; every action is a guard, one or two primes, and `UNCHANGED`;
the constants are unconstrained; the two witnesses show the refusal and
the second round are reachable.
