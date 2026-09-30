---------------------------- MODULE RunCoupling ----------------------------
(* Properties for ADR-0042 (Proposed), Run's mechanism obligations, with the   *)
(* coupling of ADR-0039 §2 read as ADR-0041 §2 reads it: over effects only.    *)
(*                                                                             *)
(*   NoEffectWithoutLiveObserver  0039 §2  no Actuate or Report is admitted    *)
(*                                         while live(o) is false              *)
(*   UnreadEffectsBounded         0042 §2  with an honest Observer, the        *)
(*                                         Thinker's unread effect-bearing     *)
(*                                         admits, summed over all its rounds, *)
(*                                         never exceed K                      *)
(*   ConsultNeverCoupled          0041 §2  with a live lease and the round     *)
(*                                         bound not reached, Consult is       *)
(*                                         enabled whatever the Observer does  *)
(*   SealCountsEffects            0042 §5  a round's seal is the number of     *)
(*                                         effect-bearing admits in it         *)
(*   RoundBoundCountsAll          0042 §2  no round admits more than R actions *)
(*                                         of any kind                         *)
(*                                                                             *)
(* Coupling.tla has one Admit action, which advances one counter and tests it  *)
(* against both K and R: every admit is an emission. It is frozen by digest    *)
(* and is not changed. This module separates what that one conflated:          *)
(*                                                                             *)
(*   acts  every admit in the round, of any kind; what R bounds                *)
(*   seq   what the mechanism counts, and what the watermark is over           *)
(*   eff   a ghost: the true number of effect-bearing admits in the round      *)
(*                                                                             *)
(* One Thinker t over MaxRound rounds and its cell Observer o. The correlator  *)
(* is Coupling.tla's and is not modeled. Time is abstracted: a heartbeat makes *)
(* the Observer fresh, and it goes stale nondeterministically. The Observer is *)
(* honest: its watermark is never above what the mechanism's sequence says     *)
(* exists, because a record exists for each number and for nothing else.       *)
(*                                                                             *)
(* Mut = "none":        the mechanism as ADR-0042 specifies it.                 *)
(* Mut = "M_EMITSEQ":   only Report advances the sequence, and an Actuate      *)
(*                      leaves no record. UnreadEffectsBounded and             *)
(*                      SealCountsEffects must fail. THIS IS THE REFERENCE     *)
(*                      BEFORE ADR-0042, and it is declared there as D-0042-1. *)
(* Mut = "M_COUPLEALL": Consult is coupled too. ConsultNeverCoupled must fail. *)
(* Mut = "M_ROUNDS":    coverage is not carried across rounds. Carried over    *)
(*                      from Coupling.tla. UnreadEffectsBounded must fail.     *)
(* Mut = "M_MARK":      live(o) tests the heartbeat and not the watermark.     *)
(*                      Carried over. UnreadEffectsBounded must fail.          *)
(* Mut = "M_NOCOUPLE":  R3-observer-live and the grant condition are absent    *)
(*                      (D-0039-1). NoEffectWithoutLiveObserver must fail.     *)
(* Mut = "M_BOUNDEFF":  the round bound counts effects and not reads, so       *)
(*                      Consult is unbounded. RoundBoundCountsAll must fail.   *)
EXTENDS Naturals

CONSTANTS Mut, K, R, MaxRound     \* K < R (ADR-0039 §1); MaxRound = 2 for the sums below

Rounds == 1..MaxRound

VARIABLES round, tLive, acts, seq, eff, rep, oLease, fresh, mark, seal, effSeal,
          admittedUnlive, refused, refusedOnActuates, consultedWhileStalled
vars == <<round, tLive, acts, seq, eff, rep, oLease, fresh, mark, seal, effSeal,
          admittedUnlive, refused, refusedOnActuates, consultedWhileStalled>>

counters == <<acts, seq, eff, rep>>
observer == <<oLease, fresh, mark>>
seals    == <<seal, effSeal>>
flags    == <<admittedUnlive, refused, refusedOnActuates, consultedWhileStalled>>

Init == /\ round = 0 /\ tLive = FALSE
        /\ acts = 0 /\ seq = 0 /\ eff = 0 /\ rep = 0
        /\ oLease = FALSE /\ fresh = FALSE
        /\ mark = [r \in Rounds |-> 0]
        /\ seal = [r \in Rounds |-> 0]
        /\ effSeal = [r \in Rounds |-> 0]
        /\ admittedUnlive = FALSE /\ refused = FALSE
        /\ refusedOnActuates = FALSE /\ consultedWhileStalled = FALSE

Coupled == Mut # "M_NOCOUPLE"

\* ADR-0039 §1. live(o): a live lease, a fresh heartbeat, and a watermark within K of the
\* sequence. The strict form: the admit being decided counts.
LiveO == /\ oLease
         /\ fresh
         /\ IF Mut = "M_MARK" \/ round = 0 THEN TRUE ELSE seq - mark[round] < K

EffectAllowed  == ~Coupled \/ LiveO
ConsultAllowed == Mut # "M_COUPLEALL" \/ LiveO

\* ADR-0039 §2. A grant for round r+1 waits until round r was read to its seal.
GrantT ==
  /\ ~tLive /\ round < MaxRound
  /\ IF round = 0 \/ Mut \in {"M_ROUNDS", "M_NOCOUPLE"} THEN TRUE ELSE mark[round] >= seal[round]
  /\ round' = round + 1 /\ tLive' = TRUE
  /\ acts' = 0 /\ seq' = 0 /\ eff' = 0 /\ rep' = 0
  /\ UNCHANGED <<observer, seals, flags>>

\* ADR-0040 §1. Ingress over the pinned Run root. A step, and not an effect.
Consult ==
  /\ tLive /\ ConsultAllowed
  /\ Mut = "M_BOUNDEFF" \/ acts < R
  /\ acts' = acts + 1
  /\ consultedWhileStalled' = (consultedWhileStalled \/ (Coupled /\ ~LiveO))
  /\ UNCHANGED <<round, tLive, seq, eff, rep, observer, seals, admittedUnlive, refused, refusedOnActuates>>

\* ADR-0042 §2, §3. An invocation advances the sequence and leaves a record at that number.
Actuate ==
  /\ tLive /\ acts < R /\ EffectAllowed
  /\ acts' = acts + 1 /\ eff' = eff + 1
  /\ seq' = IF Mut = "M_EMITSEQ" THEN seq ELSE seq + 1
  /\ admittedUnlive' = (admittedUnlive \/ ~LiveO)
  /\ UNCHANGED <<round, tLive, rep, observer, seals, refused, refusedOnActuates, consultedWhileStalled>>

Report ==
  /\ tLive /\ acts < R /\ EffectAllowed
  /\ acts' = acts + 1 /\ eff' = eff + 1 /\ rep' = rep + 1
  /\ seq' = seq + 1
  /\ admittedUnlive' = (admittedUnlive \/ ~LiveO)
  /\ UNCHANGED <<round, tLive, observer, seals, refused, refusedOnActuates, consultedWhileStalled>>

\* An effect the coupling refuses. The second flag is the refusal ADR-0042 §8 asks to see:
\* a fresh Observer, and a backlog over K made of invocations alone.
RefuseEffect ==
  /\ tLive /\ acts < R /\ ~EffectAllowed
  /\ refused' = TRUE
  /\ refusedOnActuates' = (refusedOnActuates \/ (oLease /\ fresh /\ rep = 0 /\ seq - mark[round] >= K))
  /\ UNCHANGED <<round, tLive, counters, observer, seals, admittedUnlive, consultedWhileStalled>>

\* ADR-0042 §5. The round ends when the lease ends, and seals at the final sequence.
EndRoundT ==
  /\ tLive
  /\ tLive' = FALSE
  /\ seal' = [seal EXCEPT ![round] = seq]
  /\ effSeal' = [effSeal EXCEPT ![round] = eff]
  /\ UNCHANGED <<round, counters, observer, flags>>

\* An honest heartbeat for any round so far: the watermark rises, never above what exists.
Heartbeat(r, w) ==
  /\ oLease /\ r <= round /\ r >= 1
  /\ w >= mark[r] /\ w <= (IF r = round THEN seq ELSE seal[r])
  /\ mark' = [mark EXCEPT ![r] = w]
  /\ fresh' = TRUE
  /\ UNCHANGED <<round, tLive, counters, oLease, seals, flags>>

Stale  == /\ fresh /\ fresh' = FALSE
          /\ UNCHANGED <<round, tLive, counters, oLease, mark, seals, flags>>
GrantO == /\ ~oLease /\ oLease' = TRUE
          /\ UNCHANGED <<round, tLive, counters, fresh, mark, seals, flags>>
EndO   == /\ oLease /\ oLease' = FALSE
          /\ UNCHANGED <<round, tLive, counters, fresh, mark, seals, flags>>

Next == \/ GrantT \/ Consult \/ Actuate \/ Report \/ RefuseEffect \/ EndRoundT
        \/ Stale \/ GrantO \/ EndO
        \/ \E r \in Rounds, w \in 0..R : Heartbeat(r, w)
Spec == Init /\ [][Next]_vars

\* --- the five properties ----------------------------------------------------

\* ADR-0039 §2, over effects. No Actuate or Report went through while no cell Observer was live.
NoEffectWithoutLiveObserver == ~admittedUnlive

\* ADR-0042 §2. Unread effects, this round plus every earlier one, never exceed K. The count
\* is over the ghost: what happened, not what the mechanism numbered.
Unread      == IF round = 0 THEN 0 ELSE eff - mark[round]
PriorUnread == IF round = 2 THEN effSeal[1] - mark[1] ELSE 0     \* MaxRound = 2
UnreadEffectsBounded == Unread + PriorUnread <= K

\* ADR-0041 §2. A Thinker whose Observer lags can read and cannot act.
ConsultNeverCoupled == (tLive /\ acts < R) => ENABLED Consult

\* ADR-0042 §5. The seal counts the round's effects, so coverage to the seal covers them.
SealCountsEffects ==
  \A r \in Rounds : (r < round \/ (r = round /\ ~tLive)) => seal[r] = effSeal[r]

\* ADR-0042 §2. R is a termination bound and a read is a step.
RoundBoundCountsAll == acts <= R

Safe == /\ NoEffectWithoutLiveObserver /\ UnreadEffectsBounded /\ ConsultNeverCoupled
        /\ SealCountsEffects /\ RoundBoundCountsAll

\* --- reachability witnesses: each must be VIOLATED ---------------------------
NeverRoundTwo               == round < 2                 \* a second round is granted after coverage
NeverRefused                == ~refused                  \* the coupling refuses an effect
NeverRefusedOnActuates      == ~refusedOnActuates        \* ... for a backlog of invocations alone
NeverConsultedWhileStalled  == ~consultedWhileStalled    \* a read is admitted while effects are refused
NeverSealedOnActuates       == ~(round >= 1 /\ ~tLive /\ rep = 0 /\ seal[round] > 0)
=============================================================================
