---------------------------- MODULE Coupling_proof ----------------------------
(* TLAPS proofs of the three invariants Coupling.tla states (ADR-0039 §8), for  *)
(* every K, R and MaxRound in Nat:                                               *)
(*                                                                               *)
(*   THEOREM NoAdmitWithoutLiveObserverAlways   (Mut # "M_NOCOUPLE")             *)
(*   THEOREM UnreadBoundedAlways                (Mut \notin {"M_MARK", "M_ROUNDS", "M_NOCOUPLE"}) *)
(*   THEOREM CorrelatorNeverGatesAlways         (Mut # "M_CORR")                 *)
(*   THEOREM SafeAlways                         (Mut = "none")                   *)
(*                                                                               *)
(* Each theorem takes as hypothesis only the mutations that break it             *)
(* (Coupling-results-2026.09.29.txt). The constraint K < R the module notes is   *)
(* not needed for safety and is not assumed; MaxRound = 2, which the module      *)
(* notes for PriorUnread, is not needed either: PriorUnread is zero in every     *)
(* round, because a round is granted only once the previous one is read to its  *)
(* seal, and a mark never passes a seal.                                         *)
(*                                                                               *)
(* UnreadBounded is the one arithmetic invariant. Its inductive strengthening:   *)
(* a live round is at least 1; future rounds have zero marks and seals; the      *)
(* current mark never exceeds the sequence; an idle round's seal is its          *)
(* sequence; every past round's mark equals its seal; and the current backlog    *)
(* is at most K. The last clause is preserved because an admit requires a live   *)
(* observer, whose backlog is below K.                                           *)
(*                                                                               *)
(* Coupling.tla is cited by digest in ADR-0039 and is not edited; this module    *)
(* extends it. The mutations and the four witnesses stay with TLC; the lemmas    *)
(* at the end say why each mutation must fail.                                   *)
(*                                                                               *)
(* Check with:  ../tools/tlapm Coupling_proof.tla   (from spec/; see             *)
(*              proof-results.sh for the results file)                           *)
EXTENDS Coupling, TLAPS

ASSUME KNat        == K \in Nat
ASSUME RNat        == R \in Nat
ASSUME MaxRoundNat == MaxRound \in Nat

TypeOK == /\ round \in 0..MaxRound
          /\ tLive \in BOOLEAN /\ oLease \in BOOLEAN
          /\ seq \in Nat
          /\ fresh \in [o : BOOLEAN, c : BOOLEAN]
          /\ mark \in [Rounds -> Nat] /\ seal \in [Rounds -> Nat]
          /\ tLive => round >= 1

(* Structure that holds under every mutation.                                    *)
Future     == \A r \in Rounds : r > round => mark[r] = 0 /\ seal[r] = 0
MarkLeSeq  == round >= 1 => mark[round] <= seq
SealedIdle == (round >= 1 /\ ~tLive) => seal[round] = seq
Shape == TypeOK /\ Future /\ MarkLeSeq /\ SealedIdle

(* The two clauses that need the specified coupling.                             *)
Past  == \A r \in Rounds : r < round => mark[r] = seal[r]
Bound == round >= 1 => seq - mark[round] <= K
InvU  == Shape /\ Past /\ Bound

-----------------------------------------------------------------------------
LEMMA InitShape == Init => Shape
BY MaxRoundNat DEF Init, Shape, TypeOK, Future, MarkLeSeq, SealedIdle, Rounds

(* The actions that touch none of round, tLive, seq, mark, seal.                 *)
LEMMA QuietActions ==
    ASSUME Refuse \/ CorrBeat \/ GrantO \/ EndO \/ \E x \in {"o", "c"} : Stale(x)
    PROVE  UNCHANGED <<round, tLive, seq, mark, seal>>
BY DEF Refuse, CorrBeat, GrantO, EndO, Stale

LEMMA NextShape == Shape /\ [Next]_vars => Shape'
<1> SUFFICES ASSUME Shape, [Next]_vars PROVE Shape' OBVIOUS
<1>0. TypeOK
    BY DEF Shape
<1>1. CASE UNCHANGED vars
    BY <1>1, KNat, RNat, MaxRoundNat DEF Shape, TypeOK, Future, MarkLeSeq, SealedIdle, vars, Rounds
<1>2. CASE GrantT
    <2>1. /\ round < MaxRound /\ round' = round + 1 /\ tLive' = TRUE /\ seq' = 0
          /\ UNCHANGED <<oLease, fresh, mark, seal>>
        BY <1>2, KNat, RNat, MaxRoundNat DEF GrantT, Rounds
    <2>2. round + 1 \in Rounds /\ mark[round + 1] = 0 /\ seal[round + 1] = 0
        BY <1>0, <2>1, MaxRoundNat, KNat, RNat DEF TypeOK, Rounds, Shape, Future
    <2> QED
        BY <1>0, <2>1, <2>2, MaxRoundNat, KNat, RNat DEF Shape, TypeOK, Future, MarkLeSeq, SealedIdle, Rounds
<1>3. CASE Admit
    <2>1. tLive /\ seq' = seq + 1 /\ UNCHANGED <<round, tLive, oLease, fresh, mark, seal>>
        BY <1>3, KNat, RNat, MaxRoundNat DEF Admit, Rounds
    <2> QED
        BY <1>0, <2>1, KNat, RNat, MaxRoundNat DEF Shape, TypeOK, Future, MarkLeSeq, SealedIdle, Rounds
<1>4. CASE EndRoundT
    <2>1. tLive /\ tLive' = FALSE /\ seal' = [seal EXCEPT ![round] = seq]
          /\ UNCHANGED <<round, seq, oLease, fresh, mark>>
        BY <1>4, KNat, RNat, MaxRoundNat DEF EndRoundT, Rounds
    <2>2. round \in Rounds
        BY <1>0, <2>1, KNat, RNat, MaxRoundNat DEF TypeOK, Rounds
    <2> QED
        BY <1>0, <2>1, <2>2, KNat, RNat, MaxRoundNat DEF Shape, TypeOK, Future, MarkLeSeq, SealedIdle, Rounds
<1>5. ASSUME NEW r \in Rounds, NEW w \in 0..R, Heartbeat(r, w) PROVE Shape'
    <2>1. /\ r <= round /\ r >= 1 /\ w >= mark[r] /\ w <= (IF r = round THEN seq ELSE seal[r])
          /\ mark' = [mark EXCEPT ![r] = w] /\ fresh' = [fresh EXCEPT !.o = TRUE]
          /\ UNCHANGED <<round, tLive, seq, oLease, seal>>
        BY <1>5, KNat, RNat, MaxRoundNat DEF Heartbeat, Rounds
    <2> QED
        BY <1>0, <2>1, RNat, KNat, MaxRoundNat DEF Shape, TypeOK, Future, MarkLeSeq, SealedIdle, Rounds
<1>6. CASE Refuse \/ CorrBeat \/ GrantO \/ EndO \/ \E x \in {"o", "c"} : Stale(x)
    <2>1. UNCHANGED <<round, tLive, seq, mark, seal>>
        BY <1>6, QuietActions
    <2>2. TypeOK'
        BY <1>0, <1>6, KNat, RNat, MaxRoundNat DEF Refuse, CorrBeat, GrantO, EndO, Stale, TypeOK, Rounds
    <2> QED
        BY <2>1, <2>2, KNat, RNat, MaxRoundNat DEF Shape, Future, MarkLeSeq, SealedIdle, Rounds
<1> QED
    BY <1>1, <1>2, <1>3, <1>4, <1>5, <1>6, KNat, RNat, MaxRoundNat DEF Next, Rounds

-----------------------------------------------------------------------------
(* UnreadBounded                                                                 *)

LEMMA InitInvU == Init => InvU
BY InitShape DEF Init, InvU, Past, Bound, Rounds

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
<1>3. CASE Admit
    <2>1. tLive /\ Allowed /\ seq' = seq + 1 /\ UNCHANGED <<round, mark, seal>>
        BY <1>3, KNat, RNat, MaxRoundNat DEF Admit, Rounds
    <2>2. round >= 1 /\ seq - mark[round] < K
        BY <1>0, <2>1, KNat, RNat, MaxRoundNat DEF Shape, TypeOK, Allowed, Coupled, LiveO, Rounds
    <2>3. mark[round] \in Nat /\ seq \in Nat
        BY <1>0, <2>2, MaxRoundNat DEF Shape, TypeOK, Rounds
    <2>4. Past'
        BY <1>0, <2>1 DEF InvU, Past
    <2>5. Bound'
        BY <2>1, <2>2, <2>3, KNat DEF Bound
    <2> QED
        BY <1>0, <2>4, <2>5 DEF InvU
<1>4. CASE EndRoundT
    <2>1. seal' = [seal EXCEPT ![round] = seq] /\ UNCHANGED <<round, seq, mark>> /\ round \in Rounds
        BY <1>0, <1>4, KNat, RNat, MaxRoundNat DEF EndRoundT, Shape, TypeOK, Rounds
    <2> QED
        BY <1>0, <2>1, KNat, RNat, MaxRoundNat DEF Shape, TypeOK, InvU, Past, Bound, Rounds
<1>5. ASSUME NEW r \in Rounds, NEW w \in 0..R, Heartbeat(r, w) PROVE InvU'
    <2>1. /\ r <= round /\ r >= 1 /\ w >= mark[r] /\ w <= (IF r = round THEN seq ELSE seal[r])
          /\ mark' = [mark EXCEPT ![r] = w] /\ UNCHANGED <<round, seq, seal>>
        BY <1>5, KNat, RNat, MaxRoundNat DEF Heartbeat, Rounds
    <2>2. Past'
        BY <1>0, <2>1, KNat, RNat, MaxRoundNat DEF Shape, TypeOK, InvU, Past, Rounds
    <2>3. Bound'
        BY <1>0, <2>1, KNat, RNat, MaxRoundNat DEF Shape, TypeOK, InvU, Bound, Rounds
    <2> QED
        BY <1>0, <2>2, <2>3, KNat, RNat, MaxRoundNat DEF InvU, Rounds
<1>6. CASE Refuse \/ CorrBeat \/ GrantO \/ EndO \/ \E x \in {"o", "c"} : Stale(x)
    <2>1. UNCHANGED <<round, tLive, seq, mark, seal>>
        BY <1>6, QuietActions
    <2> QED
        BY <1>0, <2>1, KNat, RNat, MaxRoundNat DEF InvU, Past, Bound, Rounds
<1> QED
    BY <1>1, <1>2, <1>3, <1>4, <1>5, <1>6, KNat, RNat, MaxRoundNat DEF Next, Rounds

LEMMA InvUBounded == InvU => UnreadBounded
<1> SUFFICES ASSUME InvU PROVE UnreadBounded OBVIOUS
<1>1. round = 2 => 1 \in Rounds
    BY MaxRoundNat DEF InvU, Shape, TypeOK, Rounds
<1>2. round = 2 => mark[1] = seal[1]
    BY <1>1 DEF InvU, Past
<1>3. round >= 1 => mark[round] \in Nat
    BY MaxRoundNat DEF InvU, Shape, TypeOK, Rounds
<1> QED
    BY <1>1, <1>2, <1>3, KNat, RNat, MaxRoundNat DEF InvU, Shape, TypeOK, Bound, UnreadBounded, Unread, PriorUnread, Rounds

THEOREM UnreadBoundedAlways ==
    ASSUME Mut # "M_MARK", Mut # "M_ROUNDS", Mut # "M_NOCOUPLE"
    PROVE  Spec => []UnreadBounded
<1>1. InvU /\ [Next]_vars => InvU'
    BY NextInvU
<1> QED
    BY InitInvU, <1>1, InvUBounded, PTL, KNat, RNat, MaxRoundNat DEF Spec, Rounds

-----------------------------------------------------------------------------
(* The two flags.                                                                *)

LEMMA NextNoAdmit ==
    ASSUME Mut # "M_NOCOUPLE", NoAdmitWithoutLiveObserver, [Next]_vars
    PROVE  NoAdmitWithoutLiveObserver'
<1>1. CASE Admit
    <2>1. LiveO
        BY <1>1, KNat, RNat, MaxRoundNat DEF Admit, Allowed, Coupled, Rounds
    <2> QED
        BY <1>1, <2>1, KNat, RNat, MaxRoundNat DEF Admit, NoAdmitWithoutLiveObserver, Rounds
<1>2. CASE ~Admit
    BY <1>2, KNat, RNat, MaxRoundNat DEF Next, GrantT, Refuse, EndRoundT, CorrBeat, GrantO, EndO, Stale, Heartbeat, vars, NoAdmitWithoutLiveObserver, Rounds
<1> QED
    BY <1>1, <1>2

THEOREM NoAdmitWithoutLiveObserverAlways ==
    ASSUME Mut # "M_NOCOUPLE"
    PROVE  Spec => []NoAdmitWithoutLiveObserver
<1>1. NoAdmitWithoutLiveObserver /\ [Next]_vars => NoAdmitWithoutLiveObserver'
    BY NextNoAdmit
<1>2. Init => NoAdmitWithoutLiveObserver
    BY DEF Init, NoAdmitWithoutLiveObserver
<1> QED
    BY <1>1, <1>2, PTL, KNat, RNat, MaxRoundNat DEF Spec, Rounds

LEMMA NextCorr ==
    ASSUME Mut # "M_CORR", CorrelatorNeverGates, [Next]_vars
    PROVE  CorrelatorNeverGates'
<1>1. CASE Refuse
    <2>1. ~LiveO
        BY <1>1, KNat, RNat, MaxRoundNat DEF Refuse, Allowed, Rounds
    <2> QED
        BY <1>1, <2>1, KNat, RNat, MaxRoundNat DEF Refuse, CorrelatorNeverGates, Rounds
<1>2. CASE ~Refuse
    BY <1>2, KNat, RNat, MaxRoundNat DEF Next, GrantT, Admit, EndRoundT, CorrBeat, GrantO, EndO, Stale, Heartbeat, vars, CorrelatorNeverGates, Rounds
<1> QED
    BY <1>1, <1>2

THEOREM CorrelatorNeverGatesAlways ==
    ASSUME Mut # "M_CORR"
    PROVE  Spec => []CorrelatorNeverGates
<1>1. CorrelatorNeverGates /\ [Next]_vars => CorrelatorNeverGates'
    BY NextCorr
<1>2. Init => CorrelatorNeverGates
    BY DEF Init, CorrelatorNeverGates
<1> QED
    BY <1>1, <1>2, PTL, KNat, RNat, MaxRoundNat DEF Spec, Rounds

THEOREM SafeAlways ==
    ASSUME Mut = "none"
    PROVE  Spec => []Safe
<1>1. Spec => []NoAdmitWithoutLiveObserver
    BY NoAdmitWithoutLiveObserverAlways
<1>2. Spec => []UnreadBounded
    BY UnreadBoundedAlways
<1>3. Spec => []CorrelatorNeverGates
    BY CorrelatorNeverGatesAlways
<1> QED
    BY <1>1, <1>2, <1>3, PTL, KNat, RNat, MaxRoundNat DEF Safe, Rounds

-----------------------------------------------------------------------------
(* Why the mutations must fail. The counterexamples are TLC's.                   *)

(* M_NOCOUPLE: every admit is allowed, observer or not.                          *)
LEMMA MutNoCoupleAllowsAll ==
    ASSUME Mut = "M_NOCOUPLE"
    PROVE  Allowed
BY DEF Allowed, Coupled

(* M_MARK: a fresh observer is live whatever its backlog.                        *)
LEMMA MutMarkIgnoresBacklog ==
    ASSUME Mut = "M_MARK", oLease, fresh.o
    PROVE  LiveO
BY DEF LiveO

(* M_ROUNDS: a round is granted without the previous one read to its seal.      *)
LEMMA MutRoundsGrantsUncovered ==
    ASSUME Mut = "M_ROUNDS", TypeOK, ~tLive, round < MaxRound
    PROVE  ENABLED GrantT
BY ExpandENABLED DEF GrantT, TypeOK

(* M_CORR: a stale correlator refuses.                                           *)
LEMMA MutCorrGates ==
    ASSUME Mut = "M_CORR", ~LiveC
    PROVE  ~Allowed
BY DEF Allowed

=============================================================================
