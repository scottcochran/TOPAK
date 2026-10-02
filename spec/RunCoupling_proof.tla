--------------------------- MODULE RunCoupling_proof ---------------------------
(* TLAPS proofs of the five invariants RunCoupling.tla states (ADR-0042 §8;      *)
(* ADR-0041 §2; ADR-0039 A1), for every K, R and MaxRound in Nat:                *)
(*                                                                               *)
(*   THEOREM NoEffectWithoutLiveObserverAlways  (Mut # "M_NOCOUPLE")             *)
(*   THEOREM UnreadEffectsBoundedAlways                                          *)
(*       (Mut \notin {"M_EMITSEQ", "M_MARK", "M_ROUNDS", "M_NOCOUPLE"})          *)
(*   THEOREM ConsultNeverCoupledAlways          (Mut # "M_COUPLEALL")            *)
(*   THEOREM SealCountsEffectsAlways            (Mut # "M_EMITSEQ")              *)
(*   THEOREM RoundBoundCountsAllAlways          (Mut # "M_BOUNDEFF")             *)
(*   THEOREM SafeAlways                         (Mut = "none")                   *)
(*                                                                               *)
(* Each theorem takes as hypothesis only the mutations that break it, as the     *)
(* TLC rows record them (RunCoupling-results-2026.09.29.txt). One differs from   *)
(* theorem-premise-binding.md: SealCountsEffects breaks under M_EMITSEQ, which   *)
(* lets an actuation count as an effect without advancing the sequence, and not  *)
(* under M_ROUNDS, which never touches a seal; the results file says the same    *)
(* (rc-emitseq-seal, rc-rounds-seal).                                            *)
(*                                                                               *)
(* The proof is Coupling_proof with effects: the sequence equals the effect      *)
(* count under the specified Actuate, so the unread-effects bound is the         *)
(* unread-sequence bound, and a sealed round's two seals agree. ConsultNever-    *)
(* Coupled is an ENABLED invariant; it holds in every state under its            *)
(* hypothesis, so it is a state lemma proved by ExpandENABLED and lifted by PTL. *)
(*                                                                               *)
(* RunCoupling.tla is cited by digest in ADR-0042 and is not edited; this        *)
(* module extends it. The mutations and the five witnesses stay with TLC; the    *)
(* lemmas at the end say why each mutation must fail.                            *)
(*                                                                               *)
(* Check with:  ../tools/tlapm RunCoupling_proof.tla   (from spec/; see          *)
(*              proof-results.sh for the results file)                           *)
EXTENDS RunCoupling, TLAPS

ASSUME KNat        == K \in Nat
ASSUME RNat        == R \in Nat
ASSUME MaxRoundNat == MaxRound \in Nat

TypeOK == /\ round \in 0..MaxRound
          /\ tLive \in BOOLEAN /\ oLease \in BOOLEAN /\ fresh \in BOOLEAN
          /\ acts \in Nat /\ seq \in Nat /\ eff \in Nat /\ rep \in Nat
          /\ mark \in [Rounds -> Nat] /\ seal \in [Rounds -> Nat] /\ effSeal \in [Rounds -> Nat]
          /\ tLive => round >= 1

(* Structure that holds under every mutation.                                    *)
Future     == \A r \in Rounds : r > round => mark[r] = 0 /\ seal[r] = 0 /\ effSeal[r] = 0
MarkLeSeq  == round >= 1 => mark[round] <= seq
SealedIdle == (round >= 1 /\ ~tLive) => seal[round] = seq /\ effSeal[round] = eff
Shape == TypeOK /\ Future /\ MarkLeSeq /\ SealedIdle

(* The seal group: the sequence counts effects.                                  *)
SeqIsEff == seq = eff
PastSeal == \A r \in Rounds : r < round => seal[r] = effSeal[r]
InvS == Shape /\ SeqIsEff /\ PastSeal

(* The bound group, on top of the seal group.                                    *)
PastMark == \A r \in Rounds : r < round => mark[r] = seal[r]
Bound    == round >= 1 => seq - mark[round] <= K
InvU == InvS /\ PastMark /\ Bound

-----------------------------------------------------------------------------
LEMMA InitShape == Init => Shape
BY MaxRoundNat DEF Init, Shape, TypeOK, Future, MarkLeSeq, SealedIdle, Rounds

(* Actions that touch none of round, tLive, seq, eff, mark, seal, effSeal.       *)
LEMMA QuietActions ==
    ASSUME Consult \/ RefuseEffect \/ Stale \/ GrantO \/ EndO
    PROVE  UNCHANGED <<round, tLive, seq, eff, mark, seal, effSeal>>
BY DEF Consult, RefuseEffect, Stale, GrantO, EndO, counters, observer, seals

LEMMA NextShape == Shape /\ [Next]_vars => Shape'
<1> SUFFICES ASSUME Shape, [Next]_vars PROVE Shape' OBVIOUS
<1>0. TypeOK
    BY DEF Shape
<1>1. CASE UNCHANGED vars
    BY <1>1, KNat, RNat, MaxRoundNat DEF Shape, TypeOK, Future, MarkLeSeq, SealedIdle, vars, Rounds
<1>2. CASE GrantT
    <2>1. /\ round < MaxRound /\ round' = round + 1 /\ tLive' = TRUE
          /\ acts' = 0 /\ seq' = 0 /\ eff' = 0 /\ rep' = 0
          /\ UNCHANGED <<oLease, fresh, mark, seal, effSeal>>
        BY <1>2, KNat, RNat, MaxRoundNat DEF GrantT, observer, seals, Rounds
    <2>2. round + 1 \in Rounds /\ mark[round + 1] = 0 /\ seal[round + 1] = 0 /\ effSeal[round + 1] = 0
        BY <1>0, <2>1, MaxRoundNat, KNat, RNat DEF TypeOK, Rounds, Shape, Future
    <2> QED
        BY <1>0, <2>1, <2>2, MaxRoundNat, KNat, RNat DEF Shape, TypeOK, Future, MarkLeSeq, SealedIdle, Rounds
<1>3. CASE Actuate \/ Report
    <2>1. /\ tLive /\ acts' = acts + 1 /\ eff' = eff + 1
          /\ seq' = seq \/ seq' = seq + 1
          /\ rep' = rep \/ rep' = rep + 1
          /\ UNCHANGED <<round, tLive, oLease, fresh, mark, seal, effSeal>>
        BY <1>3, KNat, RNat, MaxRoundNat DEF Actuate, Report, observer, seals, Rounds
    <2> QED
        BY <1>0, <2>1, KNat, RNat, MaxRoundNat DEF Shape, TypeOK, Future, MarkLeSeq, SealedIdle, Rounds
<1>4. CASE EndRoundT
    <2>1. /\ tLive /\ tLive' = FALSE
          /\ seal' = [seal EXCEPT ![round] = seq] /\ effSeal' = [effSeal EXCEPT ![round] = eff]
          /\ UNCHANGED <<round, acts, seq, eff, rep, oLease, fresh, mark>>
        BY <1>4, KNat, RNat, MaxRoundNat DEF EndRoundT, counters, observer, Rounds
    <2>2. round \in Rounds
        BY <1>0, <2>1, KNat, RNat, MaxRoundNat DEF TypeOK, Rounds
    <2> QED
        BY <1>0, <2>1, <2>2, KNat, RNat, MaxRoundNat DEF Shape, TypeOK, Future, MarkLeSeq, SealedIdle, Rounds
<1>5. ASSUME NEW r \in Rounds, NEW w \in 0..R, Heartbeat(r, w) PROVE Shape'
    <2>1. /\ r <= round /\ r >= 1 /\ w >= mark[r] /\ w <= (IF r = round THEN seq ELSE seal[r])
          /\ mark' = [mark EXCEPT ![r] = w] /\ fresh' = TRUE
          /\ UNCHANGED <<round, tLive, acts, seq, eff, rep, oLease, seal, effSeal>>
        BY <1>5, KNat, RNat, MaxRoundNat DEF Heartbeat, counters, seals, Rounds
    <2> QED
        BY <1>0, <2>1, RNat, KNat, MaxRoundNat DEF Shape, TypeOK, Future, MarkLeSeq, SealedIdle, Rounds
<1>6. CASE Consult \/ RefuseEffect \/ Stale \/ GrantO \/ EndO
    <2>1. UNCHANGED <<round, tLive, seq, eff, mark, seal, effSeal>>
        BY <1>6, QuietActions
    <2>2. TypeOK'
        BY <1>0, <1>6, KNat, RNat, MaxRoundNat DEF Consult, RefuseEffect, Stale, GrantO, EndO, counters, observer, seals, TypeOK, Rounds
    <2> QED
        BY <2>1, <2>2, KNat, RNat, MaxRoundNat DEF Shape, Future, MarkLeSeq, SealedIdle, Rounds
<1> QED
    BY <1>1, <1>2, <1>3, <1>4, <1>5, <1>6, KNat, RNat, MaxRoundNat DEF Next, Rounds

-----------------------------------------------------------------------------
(* SealCountsEffects                                                             *)

LEMMA InitInvS == Init => InvS
BY InitShape DEF Init, InvS, SeqIsEff, PastSeal, Rounds

LEMMA NextInvS ==
    ASSUME Mut # "M_EMITSEQ", InvS, [Next]_vars
    PROVE  InvS'
<1>0. Shape /\ Shape'
    BY NextShape, KNat, RNat, MaxRoundNat DEF InvS, Rounds
<1>1. CASE UNCHANGED vars
    BY <1>0, <1>1, KNat, RNat, MaxRoundNat DEF InvS, SeqIsEff, PastSeal, vars, Rounds
<1>2. CASE GrantT
    <2>1. /\ round < MaxRound /\ round' = round + 1 /\ ~tLive /\ seq' = 0 /\ eff' = 0
          /\ UNCHANGED <<seal, effSeal>>
        BY <1>2, KNat, RNat, MaxRoundNat DEF GrantT, seals, Rounds
    <2>2. round >= 1 => seal[round] = effSeal[round]
        BY <1>0, <2>1, KNat, RNat, MaxRoundNat DEF Shape, SealedIdle, InvS, SeqIsEff, Rounds
    <2> QED
        BY <1>0, <2>1, <2>2, KNat, RNat, MaxRoundNat DEF Shape, TypeOK, InvS, SeqIsEff, PastSeal, Rounds
<1>3. CASE Actuate \/ Report
    <2>1. seq' = seq + 1 /\ eff' = eff + 1 /\ UNCHANGED <<round, seal, effSeal>>
        BY <1>3, KNat, RNat, MaxRoundNat DEF Actuate, Report, seals, Rounds
    <2> QED
        BY <1>0, <2>1, KNat, RNat, MaxRoundNat DEF InvS, SeqIsEff, PastSeal, Rounds
<1>4. CASE EndRoundT
    <2>1. seal' = [seal EXCEPT ![round] = seq] /\ effSeal' = [effSeal EXCEPT ![round] = eff]
          /\ UNCHANGED <<round, seq, eff>> /\ round \in Rounds
        BY <1>0, <1>4, KNat, RNat, MaxRoundNat DEF EndRoundT, counters, Shape, TypeOK, Rounds
    <2> QED
        BY <1>0, <2>1, KNat, RNat, MaxRoundNat DEF Shape, TypeOK, InvS, SeqIsEff, PastSeal, Rounds
<1>5. ASSUME NEW r \in Rounds, NEW w \in 0..R, Heartbeat(r, w) PROVE InvS'
    <2>1. UNCHANGED <<round, seq, eff, seal, effSeal>>
        BY <1>5, KNat, RNat, MaxRoundNat DEF Heartbeat, counters, seals, Rounds
    <2> QED
        BY <1>0, <2>1, KNat, RNat, MaxRoundNat DEF InvS, SeqIsEff, PastSeal, Rounds
<1>6. CASE Consult \/ RefuseEffect \/ Stale \/ GrantO \/ EndO
    <2>1. UNCHANGED <<round, tLive, seq, eff, mark, seal, effSeal>>
        BY <1>6, QuietActions
    <2> QED
        BY <1>0, <2>1, KNat, RNat, MaxRoundNat DEF InvS, SeqIsEff, PastSeal, Rounds
<1> QED
    BY <1>1, <1>2, <1>3, <1>4, <1>5, <1>6, KNat, RNat, MaxRoundNat DEF Next, Rounds

LEMMA InvSSeals == InvS => SealCountsEffects
<1> SUFFICES ASSUME InvS, NEW r \in Rounds, r < round \/ (r = round /\ ~tLive)
             PROVE  seal[r] = effSeal[r]
    BY DEF SealCountsEffects
<1>1. CASE r < round
    BY <1>1 DEF InvS, PastSeal
<1>2. CASE r = round /\ ~tLive
    <2>1. round >= 1
        BY <1>2, MaxRoundNat DEF Rounds
    <2> QED
        BY <1>2, <2>1 DEF InvS, Shape, SealedIdle, SeqIsEff
<1> QED
    BY <1>1, <1>2

THEOREM SealCountsEffectsAlways ==
    ASSUME Mut # "M_EMITSEQ"
    PROVE  Spec => []SealCountsEffects
<1>1. InvS /\ [Next]_vars => InvS'
    BY NextInvS
<1> QED
    BY InitInvS, <1>1, InvSSeals, PTL, KNat, RNat, MaxRoundNat DEF Spec, Rounds

-----------------------------------------------------------------------------
(* UnreadEffectsBounded                                                          *)

LEMMA InitInvU == Init => InvU
BY InitInvS DEF Init, InvU, PastMark, Bound, Rounds

LEMMA NextInvU ==
    ASSUME Mut # "M_EMITSEQ", Mut # "M_MARK", Mut # "M_ROUNDS", Mut # "M_NOCOUPLE", InvU, [Next]_vars
    PROVE  InvU'
<1>0. InvS /\ InvS'
    BY NextInvS, KNat, RNat, MaxRoundNat DEF InvU, Rounds
<1>1. CASE UNCHANGED vars
    BY <1>0, <1>1, KNat, RNat, MaxRoundNat DEF InvU, PastMark, Bound, vars, Rounds
<1>2. CASE GrantT
    <2>1. /\ round < MaxRound /\ round' = round + 1 /\ ~tLive /\ seq' = 0
          /\ (round >= 1 => mark[round] >= seal[round])
          /\ UNCHANGED <<mark, seal>>
        BY <1>2, KNat, RNat, MaxRoundNat DEF GrantT, observer, seals, Rounds
    <2>2. round >= 1 => mark[round] = seal[round]
        BY <1>0, <2>1, KNat, RNat, MaxRoundNat DEF InvS, Shape, TypeOK, MarkLeSeq, SealedIdle, Rounds
    <2>3. PastMark'
        BY <1>0, <2>1, <2>2, KNat, RNat, MaxRoundNat DEF InvS, Shape, TypeOK, InvU, PastMark, Rounds
    <2>4. Bound'
        BY <1>0, <2>1, KNat, MaxRoundNat, RNat DEF InvS, Shape, TypeOK, Future, Bound, Rounds
    <2> QED
        BY <1>0, <2>3, <2>4, KNat, RNat, MaxRoundNat DEF InvU, Rounds
<1>3. CASE Actuate \/ Report
    <2>1. tLive /\ EffectAllowed /\ seq' = seq + 1 /\ UNCHANGED <<round, mark, seal>>
        BY <1>3, KNat, RNat, MaxRoundNat DEF Actuate, Report, observer, seals, Rounds
    <2>2. round >= 1 /\ seq - mark[round] < K
        BY <1>0, <2>1, KNat, RNat, MaxRoundNat DEF InvS, Shape, TypeOK, EffectAllowed, Coupled, LiveO, Rounds
    <2>3. mark[round] \in Nat /\ seq \in Nat
        BY <1>0, <2>2, MaxRoundNat DEF InvS, Shape, TypeOK, Rounds
    <2>4. PastMark'
        BY <1>0, <2>1 DEF InvU, PastMark
    <2>5. Bound'
        BY <2>1, <2>2, <2>3, KNat DEF Bound
    <2> QED
        BY <1>0, <2>4, <2>5 DEF InvU
<1>4. CASE EndRoundT
    <2>1. seal' = [seal EXCEPT ![round] = seq] /\ UNCHANGED <<round, seq, mark>> /\ round \in Rounds
        BY <1>0, <1>4, KNat, RNat, MaxRoundNat DEF EndRoundT, counters, observer, InvS, Shape, TypeOK, Rounds
    <2> QED
        BY <1>0, <2>1, KNat, RNat, MaxRoundNat DEF InvS, Shape, TypeOK, InvU, PastMark, Bound, Rounds
<1>5. ASSUME NEW r \in Rounds, NEW w \in 0..R, Heartbeat(r, w) PROVE InvU'
    <2>1. /\ r <= round /\ r >= 1 /\ w >= mark[r] /\ w <= (IF r = round THEN seq ELSE seal[r])
          /\ mark' = [mark EXCEPT ![r] = w] /\ UNCHANGED <<round, seq, seal>>
        BY <1>5, KNat, RNat, MaxRoundNat DEF Heartbeat, counters, seals, Rounds
    <2>2. PastMark'
        BY <1>0, <2>1, KNat, RNat, MaxRoundNat DEF InvS, Shape, TypeOK, InvU, PastMark, Rounds
    <2>3. Bound'
        BY <1>0, <2>1, KNat, RNat, MaxRoundNat DEF InvS, Shape, TypeOK, InvU, Bound, Rounds
    <2> QED
        BY <1>0, <2>2, <2>3, KNat, RNat, MaxRoundNat DEF InvU, Rounds
<1>6. CASE Consult \/ RefuseEffect \/ Stale \/ GrantO \/ EndO
    <2>1. UNCHANGED <<round, tLive, seq, eff, mark, seal, effSeal>>
        BY <1>6, QuietActions
    <2> QED
        BY <1>0, <2>1, KNat, RNat, MaxRoundNat DEF InvU, PastMark, Bound, Rounds
<1> QED
    BY <1>1, <1>2, <1>3, <1>4, <1>5, <1>6, KNat, RNat, MaxRoundNat DEF Next, Rounds

LEMMA InvUBounded == InvU => UnreadEffectsBounded
<1> SUFFICES ASSUME InvU PROVE UnreadEffectsBounded OBVIOUS
<1>1. round = 2 => 1 \in Rounds
    BY MaxRoundNat DEF InvU, InvS, Shape, TypeOK, Rounds
<1>2. round = 2 => mark[1] = seal[1] /\ seal[1] = effSeal[1]
    BY <1>1 DEF InvU, InvS, PastMark, PastSeal
<1>3. round >= 1 => mark[round] \in Nat
    BY MaxRoundNat DEF InvU, InvS, Shape, TypeOK, Rounds
<1> QED
    BY <1>1, <1>2, <1>3, KNat, RNat, MaxRoundNat DEF InvU, InvS, Shape, TypeOK, SeqIsEff, Bound, UnreadEffectsBounded, Unread, PriorUnread, Rounds

THEOREM UnreadEffectsBoundedAlways ==
    ASSUME Mut # "M_EMITSEQ", Mut # "M_MARK", Mut # "M_ROUNDS", Mut # "M_NOCOUPLE"
    PROVE  Spec => []UnreadEffectsBounded
<1>1. InvU /\ [Next]_vars => InvU'
    BY NextInvU
<1> QED
    BY InitInvU, <1>1, InvUBounded, PTL, KNat, RNat, MaxRoundNat DEF Spec, Rounds

-----------------------------------------------------------------------------
(* RoundBoundCountsAll                                                           *)

InvB == TypeOK /\ RoundBoundCountsAll

LEMMA NextInvB ==
    ASSUME Mut # "M_BOUNDEFF", InvB, Shape, [Next]_vars
    PROVE  InvB'
<1>0. TypeOK'
    BY NextShape, KNat, RNat, MaxRoundNat DEF Shape, Rounds
<1>1. CASE Consult \/ Actuate \/ Report
    <2>1. acts < R /\ acts' = acts + 1
        BY <1>1, KNat, RNat, MaxRoundNat DEF Consult, Actuate, Report, Rounds
    <2> QED
        BY <1>0, <2>1, KNat, RNat, MaxRoundNat DEF InvB, TypeOK, RoundBoundCountsAll, Rounds
<1>2. CASE GrantT
    BY <1>0, <1>2, RNat, KNat, MaxRoundNat DEF GrantT, InvB, RoundBoundCountsAll, Rounds
<1>3. CASE ~(Consult \/ Actuate \/ Report \/ GrantT)
    <2>1. UNCHANGED acts
        BY <1>3, KNat, RNat, MaxRoundNat DEF Next, RefuseEffect, EndRoundT, Stale, GrantO, EndO, Heartbeat, counters, vars, Rounds
    <2> QED
        BY <1>0, <2>1, KNat, RNat, MaxRoundNat DEF InvB, RoundBoundCountsAll, Rounds
<1> QED
    BY <1>1, <1>2, <1>3

THEOREM RoundBoundCountsAllAlways ==
    ASSUME Mut # "M_BOUNDEFF"
    PROVE  Spec => []RoundBoundCountsAll
<1>1. (Shape /\ InvB) /\ [Next]_vars => (Shape /\ InvB)'
    BY NextShape, NextInvB
<1>2. Init => Shape /\ InvB
    BY InitShape, RNat, KNat, MaxRoundNat DEF Init, Shape, InvB, RoundBoundCountsAll, Rounds
<1>3. Shape /\ InvB => RoundBoundCountsAll
    BY DEF InvB
<1> QED
    BY <1>1, <1>2, <1>3, PTL, KNat, RNat, MaxRoundNat DEF Spec, Rounds

-----------------------------------------------------------------------------
(* NoEffectWithoutLiveObserver                                                   *)

LEMMA NextNoEffect ==
    ASSUME Mut # "M_NOCOUPLE", NoEffectWithoutLiveObserver, [Next]_vars
    PROVE  NoEffectWithoutLiveObserver'
<1>1. CASE Actuate \/ Report
    <2>1. LiveO
        BY <1>1, KNat, RNat, MaxRoundNat DEF Actuate, Report, EffectAllowed, Coupled, Rounds
    <2> QED
        BY <1>1, <2>1, KNat, RNat, MaxRoundNat DEF Actuate, Report, NoEffectWithoutLiveObserver, Rounds
<1>2. CASE ~(Actuate \/ Report)
    BY <1>2, KNat, RNat, MaxRoundNat DEF Next, GrantT, Consult, RefuseEffect, EndRoundT, Stale, GrantO, EndO, Heartbeat, flags, vars, NoEffectWithoutLiveObserver, Rounds
<1> QED
    BY <1>1, <1>2

THEOREM NoEffectWithoutLiveObserverAlways ==
    ASSUME Mut # "M_NOCOUPLE"
    PROVE  Spec => []NoEffectWithoutLiveObserver
<1>1. NoEffectWithoutLiveObserver /\ [Next]_vars => NoEffectWithoutLiveObserver'
    BY NextNoEffect
<1>2. Init => NoEffectWithoutLiveObserver
    BY DEF Init, NoEffectWithoutLiveObserver
<1> QED
    BY <1>1, <1>2, PTL, KNat, RNat, MaxRoundNat DEF Spec, Rounds

-----------------------------------------------------------------------------
(* ConsultNeverCoupled: valid in every state under its hypothesis, since the     *)
(* specified Consult asks nothing of the observer.                               *)

LEMMA ConsultEnabled ==
    ASSUME Mut # "M_COUPLEALL", tLive, acts < R
    PROVE  ENABLED Consult
BY ExpandENABLED DEF Consult, ConsultAllowed, observer, seals

LEMMA ConsultValid ==
    ASSUME Mut # "M_COUPLEALL"
    PROVE  ConsultNeverCoupled
BY ConsultEnabled DEF ConsultNeverCoupled

THEOREM ConsultNeverCoupledAlways ==
    ASSUME Mut # "M_COUPLEALL"
    PROVE  Spec => []ConsultNeverCoupled
<1>1. ConsultNeverCoupled
    BY ConsultValid
<1> QED
    BY <1>1, PTL

-----------------------------------------------------------------------------
THEOREM SafeAlways ==
    ASSUME Mut = "none"
    PROVE  Spec => []Safe
<1>1. Spec => []NoEffectWithoutLiveObserver
    BY NoEffectWithoutLiveObserverAlways
<1>2. Spec => []UnreadEffectsBounded
    BY UnreadEffectsBoundedAlways
<1>3. Spec => []ConsultNeverCoupled
    BY ConsultNeverCoupledAlways
<1>4. Spec => []SealCountsEffects
    BY SealCountsEffectsAlways
<1>5. Spec => []RoundBoundCountsAll
    BY RoundBoundCountsAllAlways
<1> QED
    BY <1>1, <1>2, <1>3, <1>4, <1>5, PTL, KNat, RNat, MaxRoundNat DEF Safe, Rounds

-----------------------------------------------------------------------------
(* Why the mutations must fail. The counterexamples are TLC's.                   *)

LEMMA MutNoCoupleAllowsEffects ==
    ASSUME Mut = "M_NOCOUPLE"
    PROVE  EffectAllowed
BY DEF EffectAllowed, Coupled

LEMMA MutMarkIgnoresBacklog ==
    ASSUME Mut = "M_MARK", oLease, fresh
    PROVE  LiveO
BY DEF LiveO

LEMMA MutRoundsGrantsUncovered ==
    ASSUME Mut = "M_ROUNDS", TypeOK, ~tLive, round < MaxRound
    PROVE  ENABLED GrantT
BY ExpandENABLED DEF GrantT, TypeOK, observer, seals, flags

LEMMA MutCoupleAllGatesConsult ==
    ASSUME Mut = "M_COUPLEALL", ~LiveO
    PROVE  ~ConsultAllowed
BY DEF ConsultAllowed

LEMMA MutBoundEffUnboundedConsult ==
    ASSUME Mut = "M_BOUNDEFF", tLive, ConsultAllowed
    PROVE  ENABLED Consult
BY ExpandENABLED DEF Consult, observer, seals

LEMMA MutEmitSeqHidesActuate ==
    ASSUME Mut = "M_EMITSEQ", Actuate
    PROVE  seq' = seq /\ eff' = eff + 1
BY DEF Actuate

=============================================================================
