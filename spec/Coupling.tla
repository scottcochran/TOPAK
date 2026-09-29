----------------------------- MODULE Coupling ------------------------------
(* Properties for ADR-0039, Observer liveness coupled to admission in Run.     *)
(*                                                                             *)
(*   NoAdmitWithoutLiveObserver §2  no Run admit while live(o) is false for    *)
(*                                  every cell Observer o                       *)
(*   UnreadBounded              §2  with an honest Observer, the Thinker's     *)
(*                                  unread emissions, summed over all its      *)
(*                                  rounds, never exceed K                     *)
(*   CorrelatorNeverGates       §4  with a live cell Observer, the Thinker is  *)
(*                                  never refused for the correlator's state   *)
(*                                                                             *)
(* One Thinker t over MaxRound rounds, its cell Observer o, and a correlator   *)
(* c. Time is abstracted: a heartbeat makes an Observer fresh, and it goes     *)
(* stale nondeterministically (T_obs elapsing on the mechanism's clock). o's   *)
(* watermarks are kept per round and only rise (§1 R1); a heartbeat is honest, *)
(* never above what exists. t's sequence restarts with each round, as the      *)
(* reference's emit_seq does, and the seal is the sequence when a round ends.  *)
(*                                                                             *)
(* Mut = "none":       the mechanism as ADR-0039 specifies it.                  *)
(* Mut = "M_NOCOUPLE": R3-observer-live and the grant condition are absent.    *)
(*                     §2 must fail (and UnreadBounded with it: D-0039-1).      *)
(* Mut = "M_MARK":     live(o) tests the heartbeat and not the watermark, so a *)
(*                     fresh but starved Observer passes. UnreadBounded fails. *)
(* Mut = "M_ROUNDS":   coverage is not carried across rounds: the grant for    *)
(*                     round r+1 does not wait for round r to be read. This is *)
(*                     the record's text before R1. UnreadBounded must fail.   *)
(* Mut = "M_CORR":     the correlator is coupled too. §4 must fail.             *)
EXTENDS Naturals

CONSTANTS Mut, K, R, MaxRound     \* K < R (§1); MaxRound = 2 for PriorUnread below

Rounds == 1..MaxRound

VARIABLES round, tLive, seq, oLease, fresh, mark, seal, admittedUnlive, refusedForCorr, refused
vars == <<round, tLive, seq, oLease, fresh, mark, seal, admittedUnlive, refusedForCorr, refused>>

Init == /\ round = 0 /\ tLive = FALSE /\ seq = 0
        /\ oLease = FALSE
        /\ fresh = [o |-> FALSE, c |-> FALSE]
        /\ mark = [r \in Rounds |-> 0]
        /\ seal = [r \in Rounds |-> 0]
        /\ admittedUnlive = FALSE /\ refusedForCorr = FALSE /\ refused = FALSE

Coupled == Mut # "M_NOCOUPLE"

\* §1. live(o): a live lease, a fresh heartbeat, and a watermark within K of the sequence.
\* The strict form: the admit being decided counts, so that after it at most K are unread.
LiveO == /\ oLease
         /\ fresh.o
         /\ IF Mut = "M_MARK" \/ round = 0 THEN TRUE ELSE seq - mark[round] < K
LiveC == fresh.c

\* §2. A grant for round r+1 waits until round r was read to its seal (M_ROUNDS drops it).
GrantT ==
  /\ ~tLive /\ round < MaxRound
  /\ IF round = 0 \/ Mut = "M_ROUNDS" THEN TRUE ELSE mark[round] >= seal[round]
  /\ round' = round + 1 /\ tLive' = TRUE /\ seq' = 0
  /\ UNCHANGED <<oLease, fresh, mark, seal, admittedUnlive, refusedForCorr, refused>>

Allowed == /\ (~Coupled \/ LiveO)
           /\ (Mut # "M_CORR" \/ LiveC)

Admit ==
  /\ tLive /\ seq < R /\ Allowed
  /\ seq' = seq + 1
  /\ admittedUnlive' = (admittedUnlive \/ ~LiveO)
  /\ UNCHANGED <<round, tLive, oLease, fresh, mark, seal, refusedForCorr, refused>>

Refuse ==
  /\ tLive /\ seq < R /\ ~Allowed
  /\ refused' = TRUE
  /\ refusedForCorr' = (refusedForCorr \/ (LiveO /\ ~LiveC))
  /\ UNCHANGED <<round, tLive, seq, oLease, fresh, mark, seal, admittedUnlive>>

EndRoundT ==
  /\ tLive
  /\ tLive' = FALSE
  /\ seal' = [seal EXCEPT ![round] = seq]
  /\ UNCHANGED <<round, seq, oLease, fresh, mark, admittedUnlive, refusedForCorr, refused>>

\* An honest heartbeat from o for any round so far: the watermark rises, never above what exists.
Heartbeat(r, w) ==
  /\ oLease /\ r <= round /\ r >= 1
  /\ w >= mark[r] /\ w <= (IF r = round THEN seq ELSE seal[r])
  /\ mark' = [mark EXCEPT ![r] = w]
  /\ fresh' = [fresh EXCEPT !.o = TRUE]
  /\ UNCHANGED <<round, tLive, seq, oLease, seal, admittedUnlive, refusedForCorr, refused>>

CorrBeat == /\ fresh' = [fresh EXCEPT !.c = TRUE]
            /\ UNCHANGED <<round, tLive, seq, oLease, mark, seal, admittedUnlive, refusedForCorr, refused>>

Stale(x) == /\ fresh[x]
            /\ fresh' = [fresh EXCEPT ![x] = FALSE]
            /\ UNCHANGED <<round, tLive, seq, oLease, mark, seal, admittedUnlive, refusedForCorr, refused>>

GrantO == /\ ~oLease /\ oLease' = TRUE
          /\ UNCHANGED <<round, tLive, seq, fresh, mark, seal, admittedUnlive, refusedForCorr, refused>>
EndO   == /\ oLease /\ oLease' = FALSE
          /\ UNCHANGED <<round, tLive, seq, fresh, mark, seal, admittedUnlive, refusedForCorr, refused>>

Next == \/ GrantT \/ Admit \/ Refuse \/ EndRoundT \/ CorrBeat \/ GrantO \/ EndO
        \/ \E x \in {"o", "c"} : Stale(x)
        \/ \E r \in Rounds, w \in 0..R : Heartbeat(r, w)
Spec == Init /\ [][Next]_vars

\* --- the three properties ---------------------------------------------------

\* §2. No admit went through while no cell Observer was live.
NoAdmitWithoutLiveObserver == ~admittedUnlive

\* §2. Unread emissions, this round plus every earlier one, never exceed K.
Unread      == IF round = 0 THEN 0 ELSE seq - mark[round]
PriorUnread == IF round = 2 THEN seal[1] - mark[1] ELSE 0     \* MaxRound = 2
UnreadBounded == Unread + PriorUnread <= K

\* §4. With a live cell Observer, the correlator's state never refuses an admit.
CorrelatorNeverGates == ~refusedForCorr

Safe == NoAdmitWithoutLiveObserver /\ UnreadBounded /\ CorrelatorNeverGates

\* --- reachability witnesses: each must be VIOLATED ---------------------------
NeverRoundTwo   == round < 2                        \* a second round is granted after coverage
NeverRefused    == ~refused                         \* coupling refuses something
NeverStaleRefusal == ~(refused /\ oLease /\ ~fresh.o)
NeverBacklogRefusal == IF tLive THEN ~(refused /\ oLease /\ fresh.o /\ seq - mark[round] >= K) ELSE TRUE
=============================================================================
