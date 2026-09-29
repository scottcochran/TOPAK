------------------------------- MODULE Seats -------------------------------
(* Properties for ADR-0037, the LTRO decomposition into principals.           *)
(*                                                                             *)
(*   OnlyThinkersAuthor   §4  no non-thinker seat holds an authoring variant,   *)
(*                            and no thinker seat votes                         *)
(*   OneSeatPerPrincipal  §1  no principal holds live leases on two seats       *)
(*                                                                             *)
(* Seats have a kind fixed at declaration (§2): thinker, observer or grant.     *)
(* A grant names a principal and a seat; the alphabet it issues is bounded by  *)
(* the seat's kind (§4), and the grant path refuses a principal that already   *)
(* holds a live lease on another seat (§1, §9). Every admitted action records  *)
(* the kind of the seat it was admitted under.                                 *)
(*                                                                             *)
(* Mut = "none":   the mechanism as ADR-0037 specifies it.                      *)
(* Mut = "M_KIND": the grant path ignores the kind bound. §4 must fail.         *)
(* Mut = "M_SEAT": the one-live-lease rule is keyed by seat only, so the same  *)
(*                 principal may be granted a second seat. §1 must fail. This   *)
(*                 is the reference's behavior before ADR-0037 (finding 1).     *)
EXTENDS FiniteSets

CONSTANTS Mut

Principals == {"p1", "p2"}
Seats      == {"s1", "s2", "s3"}
Acts       == {"Read", "Draft", "Emit", "Vote"}
Authoring  == {"Draft"}

\* Kinds are declared with the seat (§2); one seat of each kind is enough.
KindOf == [s1 |-> "thinker", s2 |-> "observer", s3 |-> "grant"]

\* ADR-0037 §4, Build column. Vote stands for Vote(deny) on an observer seat.
KindBound(k) ==
  CASE k = "thinker"  -> {"Read", "Draft", "Emit"}
    [] k = "observer" -> {"Read", "Emit", "Vote"}
    [] k = "grant"    -> {"Read", "Emit", "Vote"}

NoLease == [live |-> FALSE, principal |-> "none", alphabet |-> {}]

VARIABLES lease, acted
vars == <<lease, acted>>

Init == /\ lease = [s \in Seats |-> NoLease]
        /\ acted = {}

\* §1, §9: refuse a principal that holds a live lease on another seat.
HoldsElsewhere(p, s) == \E t \in Seats : t # s /\ lease[t].live /\ lease[t].principal = p

Grant(p, s) ==
  /\ ~lease[s].live
  /\ Mut = "M_SEAT" \/ ~HoldsElsewhere(p, s)
  \* The grant asks for the whole alphabet; the mechanism issues what the kind allows.
  \* Under M_KIND it issues everything asked for.
  /\ LET a == IF Mut = "M_KIND" THEN Acts ELSE KindBound(KindOf[s])
     IN lease' = [lease EXCEPT ![s] = [live |-> TRUE, principal |-> p, alphabet |-> a]]
  /\ UNCHANGED acted

Act(s) ==
  /\ lease[s].live
  /\ \E a \in lease[s].alphabet :
       acted' = acted \cup {[act |-> a, kind |-> KindOf[s]]}
  /\ UNCHANGED lease

EndRound(s) ==
  /\ lease[s].live
  /\ lease' = [lease EXCEPT ![s] = NoLease]
  /\ UNCHANGED acted

Next == \E s \in Seats : Act(s) \/ EndRound(s) \/ \E p \in Principals : Grant(p, s)
Spec == Init /\ [][Next]_vars

\* --- the two properties -----------------------------------------------------

\* §4. Only a thinker seat writes, runs or offers; a thinker seat never votes.
OnlyThinkersAuthor ==
  \A r \in acted : /\ r.act \in Authoring => r.kind = "thinker"
                   /\ r.act = "Vote"      => r.kind # "thinker"

\* §1. Two live leases never belong to one principal.
OneSeatPerPrincipal ==
  \A s, t \in Seats : (s # t /\ lease[s].live /\ lease[t].live) => lease[s].principal # lease[t].principal

Safe == OnlyThinkersAuthor /\ OneSeatPerPrincipal

\* --- reachability witnesses: each must be VIOLATED ---------------------------
NeverActed   == acted = {}
NeverTwoLive == ~\E s, t \in Seats : s # t /\ lease[s].live /\ lease[t].live
NeverObserverVoted == ~\E r \in acted : r.act = "Vote" /\ r.kind = "observer"
=============================================================================
