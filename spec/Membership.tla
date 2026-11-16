------------------------------ MODULE Membership ------------------------------
(* The shrink schedule of an autonomous plane: ADR-0061 (Proposed), §1, §3 and *)
(* §4, its ratification condition (§7), and the OneSuccessor row of proposal   *)
(* §10 of derived/topak-federated-c2-design-proposal-2026.11.10b.md. Proposal  *)
(* §10 puts OneSuccessor in Federation; it is a module of its own because it   *)
(* rests on quorum intersection and shares no state with the charter chain.    *)
(*                                                                             *)
(* Five replicas, one plane. A step drops one replica, and the membership      *)
(* being replaced orders it by its own certificate. The memberships form a     *)
(* tree that can only branch if two steps from one membership are certified:   *)
(* `Reached` is every membership some certified path leads to, so a minority   *)
(* that certified a step of its own would show as a second branch.             *)
(*                                                                             *)
(*   StepInSchedule     every step is to a size the charter's schedule names   *)
(*   StepAtFloor        every step leaves at least the capture floor tolerated *)
(*   StepByQuorum       every step is signed by a certificate of the           *)
(*                      membership it replaces                                 *)
(*   AtMostOneSuccessor no membership has two successors                       *)
(*   OneSuccessor       the four together: ADR-0061 §7                         *)
(*                                                                             *)
(* A certificate for n replicas tolerating f captured is the least whole       *)
(* number above (n + f) / 2 (§1), with f = (n - 1) \div 3, which gives §1's    *)
(* table. Captured replicas sign anything; an honest replica signs at most one *)
(* step per membership. AtMostOneSuccessor is quorum intersection: two         *)
(* certificates of one membership share more replicas than can be captured,    *)
(* so they share an honest one, and it signed one step. The capture floor is   *)
(* what makes that true at every membership: the assumption CapturedWithinFloor*)
(* bounds the captured by the floor, and StepAtFloor keeps f at or above it.   *)
(*                                                                             *)
(* FINDING: THE ONE-VOTE RULE IS NOT IN §3. §3's only rule on signing is that  *)
(* a replica signs a drop only if it has not heard that replica either. An     *)
(* honest replica that has heard neither of two others could sign both drops   *)
(* by that rule, and M_TWOVOTES shows two successors follow. What forbids it   *)
(* is §2's agreement: one entry at one log index, and a step that names the    *)
(* membership it replaces. This module takes that as the honest replica's      *)
(* rule, and §3 should say so.                                                 *)
(*                                                                             *)
(* FINDING: AT THE ARCHETYPE THE FLOOR IS REDUNDANT WITH THE SCHEDULE. §4's    *)
(* schedule (7, 6, 5, 4) ends at the last size whose f is one, so removing the *)
(* floor's guard changes nothing while the schedule stands: the row            *)
(* m-below-archetype HOLDS. The floor binds a charter whose schedule runs      *)
(* past it, so M_BELOWFLOOR's breaking rows run with such a schedule.          *)
(*                                                                             *)
(* What is abstracted. PBFT is abstracted to its certificate: ADR-0061 §7's    *)
(* condition "PBFT is read" is not met by this module, and neither is the      *)
(* measurement of a round. The view change, the primary and message delivery   *)
(* are not modelled. Whether a replica has "not heard" another is not          *)
(* modelled: an honest replica may sign any drop but its own, which is more    *)
(* than §3 allows. A step's ticks (ADR-0064) are not modelled, nor a smaller   *)
(* membership's budget (§4). A step only removes: no action adds a replica,    *)
(* since that is a promotion (ADR-0059 §3).                                    *)
(*                                                                             *)
(* Mut = "none":           ADR-0061 as drafted.                                *)
(* Mut = "M_MINORITYSTEP": a step is ordered by one signer fewer than a        *)
(*                         certificate. StepByQuorum and AtMostOneSuccessor    *)
(*                         must fail.                                          *)
(* Mut = "M_BELOWFLOOR":   a step may go below the capture floor. StepAtFloor  *)
(*                         must fail, and AtMostOneSuccessor must fail once    *)
(*                         the schedule reaches two steps past the floor.      *)
(* Mut = "M_OFFSCHEDULE":  a step need not be in the schedule. StepInSchedule  *)
(*                         must fail. Added here beyond §7's two.              *)
(* Mut = "M_TWOVOTES":     an honest replica may sign several steps of one     *)
(*                         membership: §3's signing rule with no agreement     *)
(*                         behind it. AtMostOneSuccessor must fail. Added here *)
(*                         beyond §7's two.                                    *)
(*                                                                             *)
(* Deadlock is not checked: a plane at its floor with every vote cast is safe. *)
EXTENDS Naturals, FiniteSets

\* MaxBallots only cuts TLC's state space: M_TWOVOTES lets an honest replica sign every drop, and
\* its HOLDS rows do not finish without a bound. The proof assumes nothing of it.
CONSTANTS Mut, Floor, Schedule, Captured, MaxBallots

Replicas == {"r1", "r2", "r3", "r4", "r5"}

\* The captured replicas a certificate must tolerate, for a membership of n.
FOf(n)  == (n - 1) \div 3
\* The least whole number above (n + f) / 2.
Cert(n) == (n + FOf(n)) \div 2 + 1

ASSUME CapturedWithinFloor == Captured \subseteq Replicas /\ Cardinality(Captured) <= Floor
ASSUME FloorAtStart        == Floor \in Nat /\ FOf(Cardinality(Replicas)) >= Floor

VARIABLES votes, steps
vars == <<votes, steps>>

Reached == {Replicas} \cup {t.from \ {t.drop} : t \in steps}

Ballot(r, m, d) == [voter |-> r, from |-> m, drop |-> d]

Init == votes = {} /\ steps = {}

\* The mechanism's guards, each open to one mutation.
InSchedule(m)  == Mut = "M_OFFSCHEDULE" \/ Cardinality(m) - 1 \in Schedule
AtFloor(m)     == Mut = "M_BELOWFLOOR" \/ FOf(Cardinality(m) - 1) >= Floor
Enough(m, A)   == Cardinality(A) >= Cert(Cardinality(m)) - (IF Mut = "M_MINORITYSTEP" THEN 1 ELSE 0)
FirstVote(r, m) == Mut = "M_TWOVOTES" \/ ~\E b \in votes : b.voter = r /\ b.from = m

\* An honest replica signs a drop of one other replica of a membership it is in.
Sign(r, m, d) ==
  /\ r \notin Captured
  /\ r \in m
  /\ d # r
  /\ FirstVote(r, m)
  /\ Cardinality(votes) < MaxBallots
  /\ votes' = votes \cup {Ballot(r, m, d)}
  /\ UNCHANGED steps

\* The membership being replaced orders the step: A is the certificate, and each of its
\* honest members has signed this step. A captured replica signs whatever is wanted of it.
Order(m, d, A) ==
  /\ ~\E t \in steps : t.from = m /\ t.drop = d
  /\ InSchedule(m)
  /\ AtFloor(m)
  /\ Enough(m, A)
  /\ \A y \in A \ Captured : Ballot(y, m, d) \in votes
  /\ steps' = steps \cup {[from |-> m, drop |-> d, signers |-> A]}
  /\ UNCHANGED votes

Next ==
  \E m \in Reached :
    \E d \in m :
      \/ \E r \in Replicas : Sign(r, m, d)
      \/ \E A \in SUBSET m : Order(m, d, A)

Spec == Init /\ [][Next]_vars

\* --- the properties -----------------------------------------------------------

StepInSchedule == \A s \in steps : Cardinality(s.from) - 1 \in Schedule
StepAtFloor    == \A s \in steps : FOf(Cardinality(s.from) - 1) >= Floor
StepByQuorum   == \A s \in steps : Cardinality(s.signers) >= Cert(Cardinality(s.from))
AtMostOneSuccessor == \A s1, s2 \in steps : s1.from = s2.from => s1.drop = s2.drop

OneSuccessor == StepInSchedule /\ StepAtFloor /\ StepByQuorum /\ AtMostOneSuccessor
Safe == OneSuccessor

\* --- witnesses: each must be VIOLATED ------------------------------------------

NeverStepped        == steps = {}
NeverAtFourReplicas == \A m \in Reached : Cardinality(m) # 4
NeverSplitVote      == ~\E b1, b2 \in votes : b1.from = b2.from /\ b1.drop # b2.drop
NeverCapturedSigner == ~\E s \in steps : s.signers \cap Captured # {}
=============================================================================
