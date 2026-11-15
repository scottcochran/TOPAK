--------------------------- MODULE Counter_proof ---------------------------
(* Proof of Counter's one property, in the shape the skill describes: the type invariant under every mutation,
   one Next lemma under the hypothesis, a three-line theorem, SafeAlways, and one lemma for the mutation. *)
EXTENDS Counter, TLAPS

LEMMA TypeInit == Init => TypeOK
  BY DEF Init, TypeOK

LEMMA TypeNext == TypeOK /\ [Next]_vars => TypeOK'
  BY DEF TypeOK, Next, Step, vars

LEMMA NextBounded ==
    ASSUME Mut # "M_NOLIMIT"
    PROVE  TypeOK /\ Bounded /\ [Next]_vars => Bounded'
  BY LimitNat DEF TypeOK, Bounded, Next, Step, vars

THEOREM BoundedAlways ==
    ASSUME Mut # "M_NOLIMIT"
    PROVE  Spec => []Bounded
<1>1. (TypeOK /\ Bounded) /\ [Next]_vars => (TypeOK /\ Bounded)'
    BY TypeNext, NextBounded
<1>2. Init => TypeOK /\ Bounded
    BY TypeInit DEF Init, Bounded
<1> QED
    BY <1>1, <1>2, PTL DEF Spec

THEOREM SafeAlways ==
    ASSUME Mut = "none"
    PROVE  Spec => []Bounded
<1>1. Spec => []Bounded
    BY BoundedAlways
<1> QED
    BY <1>1

LEMMA MutNoLimitAllowsStep ==
    ASSUME Mut = "M_NOLIMIT", TypeOK
    PROVE  ENABLED Step
  BY ExpandENABLED DEF Step, TypeOK
=============================================================================
