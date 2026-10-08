--------------------------- MODULE Coupling_live ----------------------------
(* Liveness for ADR-0039 §2: the stall that coupling chooses ends.             *)
(*                                                                             *)
(* §2: "The Thinker waits; it is not evicted. ... When the Observer catches    *)
(* up, admits resume within the same round, or the next round is granted."     *)
(* Coupling.tla checks the safety half. Its Spec has no fairness and every     *)
(* property is an invariant, so it cannot tell a stall that ends from one that *)
(* does not (critical review 10.02, CR-37). Nor can TLC's deadlock check: in   *)
(* this model every state has a successor (the Observer's lease, granted or    *)
(* ended, and the correlator always step), so a Thinker stalled for good is a  *)
(* livelock, which only a leads-to property sees. Coupling.tla is cited by     *)
(* digest; this module extends it, as a proof module does, and never edits     *)
(* it. It adds fairness and four leads-to properties:                          *)
(*                                                                             *)
(*   AdmitStallEnds    a live Thinker below its round bound is eventually      *)
(*                     admissible, unless it ends its round first              *)
(*   GrantStallEnds    once a round has ended, a grant for the next eventually *)
(*                     becomes possible: coverage reaches the seal             *)
(*   AdmitsResume      the first as progress: the Thinker is admitted again,   *)
(*                     unless it ends its round first                          *)
(*   NextRoundGranted  the second as progress: the next round is granted       *)
(*                                                                             *)
(* The first two need A12 (Theory of Operation §13): "every Run Thinker's cell *)
(* Observer keeps up: heartbeats within T_obs, watermark within K, coverage to *)
(* each seal". A lease is granted for one round (ADR-0031 §2), so a cell's     *)
(* Observer is without a lease between its rounds, and its heartbeats stop     *)
(* there (ADR-0039 finding 3). This module reads A12 as fairness on two of the *)
(* Observer's actions:                                                         *)
(*   ObserverRegranted  weak fairness on GrantO: an Observer without a lease   *)
(*                      is granted its next round. The first grant is the      *)
(*                      mechanism's, on its seating's tally; every later one   *)
(*                      is an operator's successor grant, made with a live     *)
(*                      lease and a live peer (ADR-0031 A3; ADR-0050 §2, §4).  *)
(*                      In part an assumption about operators.                 *)
(*   ObserverKeepsUp    strong fairness on KeepUp, the heartbeat that reports  *)
(*                      a watermark within K of the Thinker's sequence while   *)
(*                      its round is live, and the seal once the round has     *)
(*                      ended: in some tenure, the Observer keeps up. Strong,  *)
(*                      because its lease may end first, so KeepUp is enabled  *)
(*                      only intermittently and weak fairness on it is not     *)
(*                      enough (SpecWFKeepUp).                                 *)
(* Both are fairness on actions of NextL, so no choice of them can leave a     *)
(* spec with no behaviour; NoBehaviour's rows check it of each fair spec under *)
(* which a row holds. "The lease is eventually held for good" would be         *)
(* simpler, and no one-Observer cell meets it. Fairness on any heartbeat,      *)
(* which CR-37 proposed weak, is not enough even strong: a heartbeat that      *)
(* repeats an old watermark keeps the Observer fresh and never covers the      *)
(* backlog (SpecAnyBeat).                                                      *)
(*                                                                             *)
(* Each progress property needs one more condition, and neither is the         *)
(* Observer's alone:                                                           *)
(*   ThinkerAsks  strong fairness on Admit, for AdmitsResume: the Thinker      *)
(*                keeps asking, and not only while its Observer is stale or    *)
(*                without a lease. Strong, because Stale or EndO may follow    *)
(*                every heartbeat that keeps up, so Admit is enabled only      *)
(*                intermittently (SpecWFAdmit). It is met jointly, by the      *)
(*                Thinker's asking, by heartbeats within T_obs, and by how the *)
(*                operators lay out the Observer's rounds against the          *)
(*                Thinker's (ADR-0039 finding 3). Rounds that overlap need two *)
(*                cell Observers, since a principal holds one lease at a time  *)
(*                (ADR-0031 §2).                                               *)
(*   GrantsMade   weak fairness on GrantT, for NextRoundGranted: a grant that  *)
(*                can be made is made. The Thinker asks for none: its first    *)
(*                round is granted by the mechanism when its seating's tally   *)
(*                completes, and every later round by an operator with a live  *)
(*                lease and a live peer (ADR-0031 A3; ADR-0050 §2, §4). An     *)
(*                assumption about people, declared as one (SpecNoGrant).      *)
(* Every step these conditions name is one the mechanism decides and orders    *)
(* (ADR-0033 §4), so each also assumes that the ordering makes progress, which *)
(* the liveness plan declares (Tier 2) and nothing here models. The two admit  *)
(* properties also need K >= 1: K = 0 is the quarantine hold, which admits     *)
(* nothing (ADR-0039 §1). The two grant properties hold at K = 0 as well.      *)
(*                                                                             *)
(* Next is Coupling's, with the heartbeat open to two liveness mutations.      *)
(* Under every other Mut, NextL is Coupling's Next exactly, so every behaviour *)
(* of SpecL is a behaviour of Coupling's Spec, and Coupling's invariants hold  *)
(* of it. Under the two, NextL is a restriction of Next and they hold too.     *)
(*                                                                             *)
(* Mut = "M_HBLIVE":    an Observer may heartbeat only while its Thinker's     *)
(*                      lease is live. It reaches all of Coupling's states, so *)
(*                      no invariant tells it from none: every safety property *)
(*                      holds and every witness is reached, a round read to    *)
(*                      its seal before it ends among them                     *)
(*                      (NeverRoundTwoAfterReading). In a run where a round    *)
(*                      ends unread, the next is never granted. Must break     *)
(*                      GrantStallEnds and NextRoundGranted, not               *)
(*                      AdmitStallEnds or AdmitsResume.                        *)
(* Mut = "M_HBCOUPLED": the Observer's own heartbeat needs live(o), as if      *)
(*                      R3-observer-live covered the observer seat. §2 says    *)
(*                      why it does not: it would refuse the report it exists  *)
(*                      to receive. Safety holds. Must break AdmitStallEnds.   *)
(*                      An Observer that starts stale stays stale, so the      *)
(*                      Thinker is never admitted (NeverAdmitted): the grant   *)
(*                      properties hold because no round ends with anything    *)
(*                      unread, and no refusal for the backlog is reached      *)
(*                      (NeverBacklogRefusalStep), so Coupling's own witness   *)
(*                      run catches this mutation too.                         *)
(* Of Coupling's own mutations, M_CORR must break AdmitStallEnds: the stall    *)
(* then waits on the correlator as well, which A12 does not cover (§4).        *)
(* M_NOCOUPLE removes the stall AdmitStallEnds is about, and M_ROUNDS the one  *)
(* GrantStallEnds is about; each holds with no fairness at all.                *)
EXTENDS Coupling

\* The heartbeat, open to the two liveness mutations.
HeartbeatL(r, w) == /\ Heartbeat(r, w)
                    /\ (Mut # "M_HBLIVE" \/ tLive)
                    /\ (Mut # "M_HBCOUPLED" \/ LiveO)

NextL == \/ GrantT \/ Admit \/ Refuse \/ EndRoundT \/ CorrBeat \/ GrantO \/ EndO
         \/ \E x \in {"o", "c"} : Stale(x)
         \/ \E r \in Rounds, w \in 0..R : HeartbeatL(r, w)

\* The heartbeat that keeps up (A12): in the current round, a watermark within K of the
\* Thinker's sequence while the round is live (§1, condition 3), and the seal once it has
\* ended (§2, coverage). A heartbeat's watermark is never above the sequence, nor above the
\* seal in an ended round, so in an ended round it is the seal.
KeepUp == \E w \in 0..R : /\ HeartbeatL(round, w)
                          /\ IF tLive THEN seq - w < K ELSE w >= seal[round]

\* --- fairness ---------------------------------------------------------------

\* A12: the Observer is granted its next round, and keeps up in some tenure.
ObserverRegranted == WF_vars(GrantO)
ObserverKeepsUp   == SF_vars(KeepUp)
A12               == ObserverRegranted /\ ObserverKeepsUp

\* The Thinker keeps asking; the grants are made.
ThinkerAsks == SF_vars(Admit)
GrantsMade  == WF_vars(GrantT)

SpecL      == Init /\ [][NextL]_vars                    \* no fairness: Coupling's Spec, open to the two mutations
SpecA12    == SpecL /\ A12                              \* AdmitStallEnds, GrantStallEnds
SpecResume == SpecA12 /\ ThinkerAsks                    \* AdmitsResume
SpecNext   == SpecA12 /\ GrantsMade                     \* NextRoundGranted
SpecFull   == SpecA12 /\ ThinkerAsks /\ GrantsMade      \* every condition: for the rows that must break, and NoBehaviour

\* Each condition dropped or weakened in turn, the others kept. Each must break a property.
SpecNoRegrant == SpecL /\ ObserverKeepsUp /\ ThinkerAsks /\ GrantsMade
SpecNoKeepUp  == SpecL /\ ObserverRegranted /\ ThinkerAsks /\ GrantsMade
SpecWFKeepUp  == SpecL /\ ObserverRegranted /\ WF_vars(KeepUp) /\ ThinkerAsks /\ GrantsMade
SpecAnyBeat   == SpecL /\ ObserverRegranted /\ ThinkerAsks /\ GrantsMade
                 /\ SF_vars(\E r \in Rounds, w \in 0..R : HeartbeatL(r, w))
SpecWFAdmit   == SpecA12 /\ WF_vars(Admit) /\ GrantsMade
SpecNoGrant   == SpecA12 /\ ThinkerAsks

\* --- the four properties ----------------------------------------------------

\* §2. The stall in a round ends: a live Thinker below its bound is eventually admissible, or ends its round.
AdmitStallEnds == (tLive /\ seq < R) ~> (~tLive \/ ENABLED Admit)

\* §2 R1. The stall across rounds ends: once a round has ended, a grant for the next eventually becomes possible.
GrantStallEnds == (~tLive /\ round < MaxRound) ~> ENABLED GrantT

\* The same as progress: the Thinker is admitted again, or ends its round; the next round is granted.
AdmitsResume     == \A n \in 0..R : (tLive /\ seq = n /\ n < R) ~> (~tLive \/ seq > n)
NextRoundGranted == \A r \in 0..MaxRound : (~tLive /\ round = r /\ r < MaxRound) ~> (round > r)

\* --- witnesses: each must be VIOLATED where its row says so ------------------

\* A round that admitted something is read to its seal and followed (MaxRound = 2).
NeverRoundTwoAfterReading == ~(round = 2 /\ seal[1] > 0)

\* A refusal for the backlog, as a step: the Observer leased and fresh, and the Thinker K or
\* more ahead of it. Coupling's NeverBacklogRefusal reads the flag refused, which an earlier
\* refusal of another kind may have set.
NeverBacklogRefusalStep == [][~(Refuse /\ oLease /\ fresh.o /\ seq - mark[round] >= K)]_vars

\* Nothing is admitted in any round.
NeverAdmitted == seq = 0

\* The spec has a behaviour: violated exactly when its fairness leaves one.
NoBehaviour == <>FALSE
=============================================================================
