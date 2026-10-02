------------------------- MODULE FloorRouting_proof -------------------------
(* TLAPS proof of the two invariants FloorRouting.tla states (ADR-0030 §9):      *)
(*                                                                               *)
(*   THEOREM SafeAlways == Spec => []Safe                   (Mut = "none")       *)
(*                                                                               *)
(* where Safe is NoWideningWithoutIssuance /\ FloorNeverVacuous. FloorRouting    *)
(* is cited by digest in ADR-0030 and ADR-0033 and is not edited; this module    *)
(* extends it. The mutations M_ROUTE and M_GATE and the three witnesses stay     *)
(* with TLC (FloorComposition-results-2026.09.24.txt); the two lemmas at the     *)
(* end say why each mutation must fail. The module has no constants beyond Mut,  *)
(* so the proof carries no model assumptions.                                    *)
(*                                                                               *)
(* Check with:  ../tools/tlapm FloorRouting_proof.tla   (from spec/; see         *)
(*              proof-results.sh for the results file)                           *)
EXTENDS FloorRouting, TLAPS

(* Safe is inductive by itself. The gate keeps U out, and under the specified    *)
(* routing a promotion is exactly a floor that implies the deployed one, so the  *)
(* widening flag is never raised.                                                *)

LEMMA InitSafe == Init => Safe
BY DEF Init, Safe, NoWideningWithoutIssuance, FloorNeverVacuous, Genesis, U

LEMMA PromoteNarrows ==
    ASSUME Mut = "none", NEW new, Route(new, deployed) = "promote"
    PROVE  new \subseteq deployed
BY DEF Route, NewImpliesOld

LEMMA NextSafe ==
    ASSUME Mut = "none", Safe, [Next]_vars
    PROVE  Safe'
<1>1. CASE UNCHANGED vars
    BY <1>1 DEF Safe, NoWideningWithoutIssuance, FloorNeverVacuous, vars
<1>2. ASSUME NEW new \in SUBSET U, Promote(new)
      PROVE  Safe'
    <2>1. new # U
        BY <1>2 DEF Promote, PassesGates
    <2>2. new \subseteq deployed
        BY <1>2, PromoteNarrows DEF Promote
    <2> QED
        BY <1>2, <2>1, <2>2 DEF Promote, Safe, NoWideningWithoutIssuance, FloorNeverVacuous
<1>3. ASSUME NEW new \in SUBSET U, IssueAndPromote(new)
      PROVE  Safe'
    <2>1. new # U
        BY <1>3 DEF IssueAndPromote, PassesGates
    <2> QED
        BY <1>3, <2>1 DEF IssueAndPromote, Safe, NoWideningWithoutIssuance, FloorNeverVacuous
<1> QED
    BY <1>1, <1>2, <1>3 DEF Next

THEOREM SafeAlways ==
    ASSUME Mut = "none"
    PROVE  Spec => []Safe
<1>1. Safe /\ [Next]_vars => Safe'
    BY NextSafe
<1> QED
    BY InitSafe, <1>1, PTL DEF Spec

THEOREM NoWideningAlways ==
    ASSUME Mut = "none"
    PROVE  Spec => []NoWideningWithoutIssuance
BY SafeAlways, PTL DEF Safe

THEOREM NeverVacuousAlways ==
    ASSUME Mut = "none"
    PROVE  Spec => []FloorNeverVacuous
BY SafeAlways, PTL DEF Safe

(* Why the mutations must fail. M_GATE lets the vacuous floor U through the      *)
(* gate; M_ROUTE sends an incomparable floor, which widens, down the promotion   *)
(* path. The counterexamples are TLC's.                                          *)
LEMMA MutGateAdmitsU ==
    ASSUME Mut = "M_GATE"
    PROVE  PassesGates(U)
BY DEF PassesGates

LEMMA MutRoutePromotesIncomparable ==
    ASSUME Mut = "M_ROUTE", NEW new, NEW old, Incomparable(new, old)
    PROVE  Route(new, old) = "promote"
BY DEF Route, Incomparable, NewImpliesOld, OldImpliesNew

=============================================================================
