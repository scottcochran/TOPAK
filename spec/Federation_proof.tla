--------------------------- MODULE Federation_proof ---------------------------
(* TLAPS proof of the invariants of Federation.tla (ADR-0059 §9), for every    *)
(* value of the constants the assumptions below admit: every budget, every     *)
(* epoch bound, every set of captured planes that leaves the root honest, and  *)
(* every set of verifiers. Federation.tla is not edited.                       *)
(*                                                                             *)
(*   THEOREM CharterNarrowsAlways    [Mut # "M_WIDEN"]                         *)
(*   THEOREM LeaseWithinChainAlways  [Mut # "M_LASTLINK", Mut # "M_TRUSTPLANE"]*)
(*   THEOREM HavocPlaneBoundedAlways [Mut # "M_LASTLINK", Mut # "M_TRUSTPLANE"]*)
(*   THEOREM BudgetConservedAlways   [Mut # "M_NODEBIT"]                       *)
(*   THEOREM AnyPlaneFencesAlways    [Mut # "M_STALEEPOCH"]                    *)
(*   THEOREM SafeAlways              [Mut = "none"]                            *)
(*                                                                             *)
(* The strengthening. `Shape` holds under every mutation: the type invariant;  *)
(* the root's charter never changes; a plane is seated only below a seated     *)
(* parent; what is left of a budget is at most the budget; and an unseated     *)
(* plane has the empty charter and has spent nothing. The three flags are      *)
(* inductive alone, each at Permit against the guard its mutation removes.     *)
(* CharterNarrows needs Shape: the budget guard reads `left`, and a later      *)
(* seating of a parent cannot disturb a child because no child is seated       *)
(* first. BudgetConserved rests on `Account`: an honest plane's budget is      *)
(* exactly what is left of it, what it issued, and what it debited to its      *)
(* child. The tree's sum follows from one account per plane.                   *)
(*                                                                             *)
(* Mutations and witnesses are behaviours and stay with TLC                    *)
(* (Federation-results-*.txt). Check: tools/tlapm --cleanfp --strict.          *)
EXTENDS Federation, TLAPS

ASSUME RootBudgetNat == RootBudget \in Nat
ASSUME MaxEpochNat   == MaxEpoch \in Nat

CharterRec == [seated : BOOLEAN, alphabet : SUBSET Entries, budget : Nat, fence : Nat]
Tags       == {"permit", "deep", "afterFence", "refChain", "refFence"}

TypeOK ==
  /\ charter \in [Planes -> CharterRec]
  /\ left \in [Planes -> Nat]
  /\ issued \in [Planes -> Nat]
  /\ epoch \in [Planes -> Nat]
  /\ heard \in [Verifiers -> [Planes -> Nat]]
  /\ outsideChain \in BOOLEAN
  /\ outsideRoot \in BOOLEAN
  /\ fenced \in BOOLEAN
  /\ seen \subseteq Tags

RootFixed == charter["r"] = RootCharter
SeatOrder == charter["b"].seated => charter["a"].seated
LeftLe    == \A x \in Planes : left[x] <= charter[x].budget
Unseated  == \A x \in Planes : ~charter[x].seated => (charter[x] = NoCharter /\ left[x] = 0 /\ issued[x] = 0)

Shape == TypeOK /\ RootFixed /\ SeatOrder /\ LeftLe /\ Unseated

ChildBudget(x) == IF x = "r" THEN charter["a"].budget ELSE IF x = "a" THEN charter["b"].budget ELSE 0
Account == \A x \in Planes : x \notin Captured => left[x] + issued[x] + ChildBudget(x) = charter[x].budget
-----------------------------------------------------------------------------
LEMMA OfferedFacts ==
  ASSUME NEW c \in Offered
  PROVE  /\ c \in CharterRec
         /\ c.seated = TRUE
         /\ c.budget \in Nat
         /\ c.alphabet \subseteq Entries
  BY RootBudgetNat, MaxEpochNat DEF Offered, CharterRec

LEMMA RootCharterFacts == RootCharter \in CharterRec /\ RootCharter.seated
  BY RootBudgetNat DEF RootCharter, CharterRec, RootAlphabet, Entries

LEMMA NoCharterFacts == NoCharter \in CharterRec /\ ~NoCharter.seated /\ NoCharter.budget = 0
  BY DEF NoCharter, CharterRec

LEMMA ParentFacts ==
  /\ Parent["a"] = "r" /\ Parent["b"] = "a"
  /\ Children \subseteq Planes
  /\ \A x \in Children : Parent[x] \in Planes /\ Parent[x] # x
  /\ "r" \in Planes /\ "a" \in Planes /\ "b" \in Planes
  BY DEF Parent, Children, Planes

LEMMA InitShape == Init => Shape
<1> SUFFICES ASSUME Init PROVE Shape OBVIOUS
<1>1. TypeOK
  BY RootBudgetNat, RootCharterFacts, NoCharterFacts DEF Init, TypeOK, Planes
<1>2. RootFixed
  BY DEF Init, RootFixed, Planes
<1>3. SeatOrder
  BY NoCharterFacts DEF Init, SeatOrder, Planes
<1>4. LeftLe
  BY RootBudgetNat, RootCharterFacts, NoCharterFacts DEF Init, LeftLe, Planes, RootCharter
<1>5. Unseated
  BY RootCharterFacts, NoCharterFacts DEF Init, Unseated, Planes
<1> QED
  BY <1>1, <1>2, <1>3, <1>4, <1>5 DEF Shape

LEMMA NextTypeOK == TypeOK /\ Shape /\ [Next]_vars => TypeOK'
<1> SUFFICES ASSUME TypeOK, Shape, [Next]_vars PROVE TypeOK' OBVIOUS
<1>1. CASE UNCHANGED vars
  BY <1>1 DEF TypeOK, vars
<1>2. ASSUME NEW p \in Children, NEW c \in Offered, SeatHonest(p, c) PROVE TypeOK'
  <2>1. /\ Parent[p] \in Planes /\ p \in Planes /\ Parent[p] # p
    BY ParentFacts
  <2>2. /\ c \in CharterRec /\ c.budget \in Nat
    BY OfferedFacts
  <2>3. c.budget <= left[Parent[p]]
    BY <1>2 DEF SeatHonest
  <2>4. Debit(c) \in 0..c.budget
    BY <2>2 DEF Debit
  <2>5. left[Parent[p]] - Debit(c) \in Nat
    BY <2>1, <2>2, <2>3, <2>4 DEF TypeOK
  <2>6. charter' \in [Planes -> CharterRec]
    BY <1>2, <2>1, <2>2 DEF SeatHonest, TypeOK
  <2>7. left' \in [Planes -> Nat]
    BY <1>2, <2>1, <2>2, <2>5 DEF SeatHonest, TypeOK
  <2> QED
    BY <1>2, <2>6, <2>7 DEF SeatHonest, TypeOK
<1>3. ASSUME NEW p \in Children, NEW c \in Offered, SeatCaptured(p, c) PROVE TypeOK'
  <2>1. p \in Planes /\ c \in CharterRec /\ c.budget \in Nat
    BY ParentFacts, OfferedFacts
  <2> QED
    BY <1>3, <2>1 DEF SeatCaptured, TypeOK
<1>4. ASSUME NEW p \in Planes, Issue(p) PROVE TypeOK'
  BY <1>4 DEF Issue, TypeOK
<1>5. ASSUME NEW p \in Planes, MoveEpoch(p) PROVE TypeOK'
  BY <1>5 DEF MoveEpoch, TypeOK
<1>6. ASSUME NEW v \in Verifiers, NEW r \in Planes, Hear(v, r) PROVE TypeOK'
  BY <1>6 DEF Hear, TypeOK
<1>7. ASSUME NEW v \in Verifiers, NEW p \in Planes, NEW e \in Entries, NEW ep \in 0..MaxEpoch,
             Permit(v, p, e, ep)
      PROVE TypeOK'
  <2> DEFINE S == {"permit"} \cup (IF p = "b" THEN {"deep"} ELSE {})
                  \cup (IF heard[v]["r"] >= 1 THEN {"afterFence"} ELSE {})
  <2>1. S \subseteq Tags
    BY DEF Tags
  <2>2. seen' = seen \cup S
    BY <1>7 DEF Permit
  <2>3. seen' \subseteq Tags
    BY <2>1, <2>2 DEF TypeOK
  <2>4. /\ outsideChain' \in BOOLEAN /\ outsideRoot' \in BOOLEAN /\ fenced' \in BOOLEAN
    BY <1>7 DEF Permit, TypeOK
  <2>5. UNCHANGED <<charter, left, issued, epoch, heard>>
    BY <1>7 DEF Permit
  <2> QED
    BY <2>3, <2>4, <2>5 DEF TypeOK
<1>8. ASSUME NEW v \in Verifiers, NEW p \in Planes, NEW e \in Entries, NEW ep \in 0..MaxEpoch,
             Refuse(v, p, e, ep)
      PROVE TypeOK'
  <2> DEFINE S == (IF ChainChecked(p, e) THEN {} ELSE {"refChain"})
                  \cup (IF FenceOK(v, p, ep) THEN {} ELSE {"refFence"})
  <2> HIDE DEF ChainChecked, FenceOK
  <2>1. S \subseteq Tags
    BY DEF Tags
  <2>2. seen' = seen \cup S
    BY <1>8 DEF Refuse
  <2>3. seen' \subseteq Tags
    BY <2>1, <2>2 DEF TypeOK
  <2>4. UNCHANGED <<charter, left, issued, epoch, heard, outsideChain, outsideRoot, fenced>>
    BY <1>8 DEF Refuse
  <2> QED
    BY <2>3, <2>4 DEF TypeOK
<1> QED
  BY <1>1, <1>2, <1>3, <1>4, <1>5, <1>6, <1>7, <1>8 DEF Next

LEMMA NextShape == Shape /\ [Next]_vars => Shape'
<1> SUFFICES ASSUME Shape, [Next]_vars PROVE Shape' OBVIOUS
<1>0. TypeOK /\ TypeOK'
  BY NextTypeOK DEF Shape
<1>1. CASE UNCHANGED vars
  BY <1>0, <1>1 DEF Shape, RootFixed, SeatOrder, LeftLe, Unseated, vars
<1>2. ASSUME NEW p \in Children, NEW c \in Offered, SeatHonest(p, c) PROVE Shape'
  <2>1. /\ Parent[p] \in Planes /\ p \in Planes /\ Parent[p] # p /\ p # "r"
    BY ParentFacts DEF Children
  <2>2. /\ c \in CharterRec /\ c.budget \in Nat /\ c.seated
    BY OfferedFacts
  <2>3. /\ charter[Parent[p]].seated
        /\ c.budget <= left[Parent[p]]
        /\ charter' = [charter EXCEPT ![p] = c]
        /\ left' = [left EXCEPT ![p] = c.budget, ![Parent[p]] = left[Parent[p]] - Debit(c)]
        /\ UNCHANGED issued
    BY <1>2 DEF SeatHonest
  <2>4. Debit(c) \in 0..c.budget
    BY <2>2 DEF Debit
  <2>5. RootFixed'
    BY <1>0, <2>1, <2>3, ParentFacts DEF RootFixed, Shape, TypeOK
  <2>6. SeatOrder'
    BY <1>0, <2>1, <2>2, <2>3, ParentFacts DEF SeatOrder, Shape, TypeOK, Children
  <2>7. LeftLe'
    <3> SUFFICES ASSUME NEW x \in Planes PROVE left'[x] <= charter'[x].budget
      BY DEF LeftLe
    <3>1. CASE x = p
      BY <1>0, <2>1, <2>2, <2>3, <3>1 DEF TypeOK
    <3>2. CASE x = Parent[p]
      <4>1. left'[x] = left[x] - Debit(c) /\ charter'[x] = charter[x]
        BY <1>0, <2>1, <2>3, <3>2 DEF TypeOK
      <4>2. left[x] <= charter[x].budget
        BY DEF Shape, LeftLe
      <4>3. left[x] \in Nat /\ charter[x].budget \in Nat
        BY <1>0 DEF TypeOK, CharterRec
      <4> QED
        BY <2>4, <4>1, <4>2, <4>3
    <3>3. CASE x # p /\ x # Parent[p]
      BY <1>0, <2>1, <2>3, <3>3 DEF Shape, LeftLe, TypeOK
    <3> QED
      BY <3>1, <3>2, <3>3
  <2>8. Unseated'
    <3> SUFFICES ASSUME NEW x \in Planes, ~charter'[x].seated
                 PROVE charter'[x] = NoCharter /\ left'[x] = 0 /\ issued'[x] = 0
      BY DEF Unseated
    <3>1. x # p
      BY <1>0, <2>1, <2>2, <2>3 DEF TypeOK
    <3>2. x # Parent[p]
      BY <1>0, <2>1, <2>3, <3>1 DEF TypeOK
    <3>3. ~charter[x].seated /\ charter'[x] = charter[x]
      BY <1>0, <2>1, <2>3, <3>1 DEF TypeOK
    <3>4. left'[x] = left[x]
      BY <1>0, <2>1, <2>3, <3>1, <3>2 DEF TypeOK
    <3> QED
      BY <2>3, <3>3, <3>4 DEF Shape, Unseated
  <2> QED
    BY <1>0, <2>5, <2>6, <2>7, <2>8 DEF Shape
<1>3. ASSUME NEW p \in Children, NEW c \in Offered, SeatCaptured(p, c) PROVE Shape'
  <2>1. /\ Parent[p] \in Planes /\ p \in Planes /\ p # "r"
    BY ParentFacts DEF Children
  <2>2. /\ c \in CharterRec /\ c.budget \in Nat /\ c.seated
    BY OfferedFacts
  <2>3. /\ charter[Parent[p]].seated
        /\ charter' = [charter EXCEPT ![p] = c]
        /\ left' = [left EXCEPT ![p] = c.budget]
        /\ UNCHANGED issued
    BY <1>3 DEF SeatCaptured
  <2>5. RootFixed'
    BY <1>0, <2>1, <2>3, ParentFacts DEF RootFixed, Shape, TypeOK
  <2>6. SeatOrder'
    BY <1>0, <2>1, <2>2, <2>3, ParentFacts DEF SeatOrder, Shape, TypeOK, Children
  <2>7. LeftLe'
    <3> SUFFICES ASSUME NEW x \in Planes PROVE left'[x] <= charter'[x].budget
      BY DEF LeftLe
    <3>1. CASE x = p
      BY <1>0, <2>1, <2>2, <2>3, <3>1 DEF TypeOK
    <3>2. CASE x # p
      BY <1>0, <2>1, <2>3, <3>2 DEF Shape, LeftLe, TypeOK
    <3> QED
      BY <3>1, <3>2
  <2>8. Unseated'
    <3> SUFFICES ASSUME NEW x \in Planes, ~charter'[x].seated
                 PROVE charter'[x] = NoCharter /\ left'[x] = 0 /\ issued'[x] = 0
      BY DEF Unseated
    <3>1. x # p
      BY <1>0, <2>1, <2>2, <2>3 DEF TypeOK
    <3>2. ~charter[x].seated /\ charter'[x] = charter[x] /\ left'[x] = left[x]
      BY <1>0, <2>1, <2>3, <3>1 DEF TypeOK
    <3> QED
      BY <2>3, <3>2 DEF Shape, Unseated
  <2> QED
    BY <1>0, <2>5, <2>6, <2>7, <2>8 DEF Shape
<1>4. ASSUME NEW p \in Planes, Issue(p) PROVE Shape'
  <2>1. /\ charter[p].seated /\ left[p] >= 1
        /\ left' = [left EXCEPT ![p] = left[p] - 1]
        /\ issued' = [issued EXCEPT ![p] = issued[p] + 1]
        /\ UNCHANGED charter
    BY <1>4 DEF Issue
  <2>2. RootFixed' /\ SeatOrder'
    BY <2>1 DEF RootFixed, SeatOrder, Shape
  <2>3. LeftLe'
    <3> SUFFICES ASSUME NEW x \in Planes PROVE left'[x] <= charter'[x].budget
      BY DEF LeftLe
    <3>1. left[x] <= charter[x].budget /\ left[x] \in Nat /\ charter[x].budget \in Nat
      BY <1>0 DEF Shape, LeftLe, TypeOK, CharterRec
    <3> QED
      BY <1>0, <2>1, <3>1 DEF TypeOK
  <2>4. Unseated'
    <3> SUFFICES ASSUME NEW x \in Planes, ~charter'[x].seated
                 PROVE charter'[x] = NoCharter /\ left'[x] = 0 /\ issued'[x] = 0
      BY DEF Unseated
    <3>1. x # p
      BY <2>1
    <3> QED
      BY <1>0, <2>1, <3>1 DEF Shape, Unseated, TypeOK
  <2> QED
    BY <1>0, <2>2, <2>3, <2>4 DEF Shape
<1> QED
  <2>1. ASSUME Next PROVE Shape'
    <3>1. CASE \E p \in Children, c \in Offered : SeatHonest(p, c) \/ SeatCaptured(p, c)
      BY <3>1, <1>2, <1>3
    <3>2. CASE \E p \in Planes : Issue(p) \/ MoveEpoch(p)
      <4>1. PICK p \in Planes : Issue(p) \/ MoveEpoch(p)
        BY <3>2
      <4>2. CASE Issue(p)
        BY <4>2, <1>4
      <4>3. CASE MoveEpoch(p)
        <5>1. UNCHANGED <<charter, left, issued>>
          BY <4>3 DEF MoveEpoch
        <5> QED
          BY <1>0, <5>1 DEF Shape, RootFixed, SeatOrder, LeftLe, Unseated
      <4> QED
        BY <4>1, <4>2, <4>3
    <3>3. CASE \E v2 \in Verifiers, r \in Planes : Hear(v2, r)
      <4>1. PICK v2 \in Verifiers, r \in Planes : Hear(v2, r)
        BY <3>3
      <4>2. UNCHANGED <<charter, left, issued>>
        BY <4>1 DEF Hear
      <4> QED
        BY <1>0, <4>2 DEF Shape, RootFixed, SeatOrder, LeftLe, Unseated
    <3>4. CASE \E v2 \in Verifiers, p \in Planes, e \in Entries, ep \in 0..MaxEpoch :
                 Permit(v2, p, e, ep) \/ Refuse(v2, p, e, ep)
      <4>1. PICK v2 \in Verifiers, p \in Planes, e \in Entries, ep \in 0..MaxEpoch :
                 Permit(v2, p, e, ep) \/ Refuse(v2, p, e, ep)
        BY <3>4
      <4>2. UNCHANGED <<charter, left, issued>>
        BY <4>1 DEF Permit, Refuse
      <4> QED
        BY <1>0, <4>2 DEF Shape, RootFixed, SeatOrder, LeftLe, Unseated
    <3> QED
      BY <2>1, <3>1, <3>2, <3>3, <3>4 DEF Next
  <2> QED
    BY <1>1, <2>1 DEF vars
-----------------------------------------------------------------------------
THEOREM ShapeAlways == Spec => []Shape
<1>1. Shape /\ [Next]_vars => Shape'
  BY NextShape
<1> QED
  BY InitShape, <1>1, PTL DEF Spec
-----------------------------------------------------------------------------
(* The three flags: each is inductive alone, at Permit, against one guard.     *)

LEMMA PermitFlags ==
  ASSUME NEW v \in Verifiers, NEW p \in Planes, NEW e \in Entries, NEW ep \in 0..MaxEpoch,
         Permit(v, p, e, ep)
  PROVE  /\ (Mut # "M_LASTLINK" /\ Mut # "M_TRUSTPLANE") => WithinChain(p, e)
         /\ Mut # "M_STALEEPOCH" => FenceTrue(v, p, ep)
  BY DEF Permit, ChainChecked, FenceOK

\* Every action but Permit leaves the three flags alone.
LEMMA FlagsFrame ==
  ASSUME [Next]_vars
  PROVE  \/ UNCHANGED <<outsideChain, outsideRoot, fenced>>
         \/ \E v \in Verifiers, p \in Planes, e \in Entries, ep \in 0..MaxEpoch : Permit(v, p, e, ep)
<1> SUFFICES ASSUME Next, ~UNCHANGED <<outsideChain, outsideRoot, fenced>>
             PROVE  \E v \in Verifiers, p \in Planes, e \in Entries, ep \in 0..MaxEpoch : Permit(v, p, e, ep)
  BY DEF vars
<1>1. \A p \in Children, c \in Offered : ~(SeatHonest(p, c) \/ SeatCaptured(p, c))
  BY DEF SeatHonest, SeatCaptured
<1>2. \A p \in Planes : ~(Issue(p) \/ MoveEpoch(p))
  BY DEF Issue, MoveEpoch
<1>3. \A v \in Verifiers, r \in Planes : ~Hear(v, r)
  BY DEF Hear
<1>4. \A v \in Verifiers, p \in Planes, e \in Entries, ep \in 0..MaxEpoch : ~Refuse(v, p, e, ep)
  BY DEF Refuse
<1> QED
  BY <1>1, <1>2, <1>3, <1>4 DEF Next

LEMMA NextLeaseWithinChain ==
  ASSUME Mut # "M_LASTLINK", Mut # "M_TRUSTPLANE", LeaseWithinChain, [Next]_vars
  PROVE  LeaseWithinChain'
<1>1. CASE UNCHANGED <<outsideChain, outsideRoot, fenced>>
  BY <1>1 DEF LeaseWithinChain
<1>2. CASE \E v \in Verifiers, p \in Planes, e \in Entries, ep \in 0..MaxEpoch : Permit(v, p, e, ep)
  <2>1. PICK v \in Verifiers, p \in Planes, e \in Entries, ep \in 0..MaxEpoch : Permit(v, p, e, ep)
    BY <1>2
  <2>2. WithinChain(p, e)
    BY <2>1, PermitFlags
  <2> QED
    BY <2>1, <2>2 DEF Permit, LeaseWithinChain
<1> QED
  BY <1>1, <1>2, FlagsFrame

THEOREM LeaseWithinChainAlways ==
  ASSUME Mut # "M_LASTLINK", Mut # "M_TRUSTPLANE"
  PROVE  Spec => []LeaseWithinChain
<1>1. LeaseWithinChain /\ [Next]_vars => LeaseWithinChain'
  BY NextLeaseWithinChain
<1>2. Init => LeaseWithinChain
  BY DEF Init, LeaseWithinChain
<1> QED
  BY <1>1, <1>2, PTL DEF Spec

LEMMA NextAnyPlaneFences ==
  ASSUME Mut # "M_STALEEPOCH", AnyPlaneFences, [Next]_vars
  PROVE  AnyPlaneFences'
<1>1. CASE UNCHANGED <<outsideChain, outsideRoot, fenced>>
  BY <1>1 DEF AnyPlaneFences
<1>2. CASE \E v \in Verifiers, p \in Planes, e \in Entries, ep \in 0..MaxEpoch : Permit(v, p, e, ep)
  <2>1. PICK v \in Verifiers, p \in Planes, e \in Entries, ep \in 0..MaxEpoch : Permit(v, p, e, ep)
    BY <1>2
  <2>2. FenceTrue(v, p, ep)
    BY <2>1, PermitFlags
  <2> QED
    BY <2>1, <2>2 DEF Permit, AnyPlaneFences
<1> QED
  BY <1>1, <1>2, FlagsFrame

THEOREM AnyPlaneFencesAlways ==
  ASSUME Mut # "M_STALEEPOCH"
  PROVE  Spec => []AnyPlaneFences
<1>1. AnyPlaneFences /\ [Next]_vars => AnyPlaneFences'
  BY NextAnyPlaneFences
<1>2. Init => AnyPlaneFences
  BY DEF Init, AnyPlaneFences
<1> QED
  BY <1>1, <1>2, PTL DEF Spec

\* The root is on every chain, and its charter is the one the tally voted.
LEMMA RootOnChain == \A x \in Planes : "r" \in ChainOf(x)
  BY DEF Planes, ChainOf

InvRoot == Shape /\ HavocPlaneBounded

LEMMA NextHavocPlaneBounded ==
  ASSUME Mut # "M_LASTLINK", Mut # "M_TRUSTPLANE", InvRoot, [Next]_vars
  PROVE  InvRoot'
<1>0. Shape /\ Shape'
  BY NextShape DEF InvRoot
<1>1. CASE UNCHANGED <<outsideChain, outsideRoot, fenced>>
  BY <1>0, <1>1 DEF InvRoot, HavocPlaneBounded
<1>2. CASE \E v \in Verifiers, p \in Planes, e \in Entries, ep \in 0..MaxEpoch : Permit(v, p, e, ep)
  <2>1. PICK v \in Verifiers, p \in Planes, e \in Entries, ep \in 0..MaxEpoch : Permit(v, p, e, ep)
    BY <1>2
  <2>2. WithinChain(p, e)
    BY <2>1, PermitFlags
  <2>3. e \in charter["r"].alphabet
    BY <2>2, RootOnChain DEF WithinChain
  <2>4. e \in RootAlphabet
    BY <1>0, <2>3 DEF Shape, RootFixed, RootCharter
  <2> QED
    BY <1>0, <2>1, <2>4 DEF Permit, InvRoot, HavocPlaneBounded
<1> QED
  BY <1>1, <1>2, FlagsFrame

THEOREM HavocPlaneBoundedAlways ==
  ASSUME Mut # "M_LASTLINK", Mut # "M_TRUSTPLANE"
  PROVE  Spec => []HavocPlaneBounded
<1>1. InvRoot /\ [Next]_vars => InvRoot'
  BY NextHavocPlaneBounded
<1>2. Init => InvRoot
  BY InitShape DEF Init, InvRoot, HavocPlaneBounded
<1>3. InvRoot => HavocPlaneBounded
  BY DEF InvRoot
<1> QED
  BY <1>1, <1>2, <1>3, PTL DEF Spec
-----------------------------------------------------------------------------
(* CharterNarrows: at the seating, against the guard M_WIDEN removes.          *)

InvNarrow == Shape /\ CharterNarrows

LEMMA NextCharterNarrows ==
  ASSUME Mut # "M_WIDEN", InvNarrow, [Next]_vars
  PROVE  InvNarrow'
<1>0. Shape /\ Shape' /\ CharterNarrows
  BY NextShape DEF InvNarrow
<1>a. TypeOK /\ TypeOK'
  BY <1>0 DEF Shape
<1>1. CASE UNCHANGED charter
  <2>1. CharterNarrows'
    BY <1>0, <1>1 DEF CharterNarrows
  <2> QED
    BY <1>0, <2>1 DEF InvNarrow
<1>2. ASSUME NEW p \in Children, NEW c \in Offered, SeatHonest(p, c) PROVE InvNarrow'
  <2>1. /\ c.alphabet \subseteq charter[Parent[p]].alphabet
        /\ c.budget <= left[Parent[p]]
        /\ charter' = [charter EXCEPT ![p] = c]
        /\ c.seated
        /\ ~charter[p].seated
    BY <1>2, OfferedFacts DEF SeatHonest, Narrows
  <2>2. Parent[p] \in Planes /\ p \in Planes /\ Parent[p] # p
    BY ParentFacts
  <2>3. left[Parent[p]] <= charter[Parent[p]].budget
    BY <1>0, <2>2 DEF Shape, LeftLe
  <2>4. /\ c.budget \in Nat /\ left[Parent[p]] \in Nat /\ charter[Parent[p]].budget \in Nat
    BY <1>a, <2>2, OfferedFacts DEF TypeOK, CharterRec
  <2>5. c.budget <= charter[Parent[p]].budget
    BY <2>1, <2>3, <2>4
  <2>6. CharterNarrows'
    <3> SUFFICES ASSUME NEW x \in Children, charter'[x].seated, Parent[x] \notin Captured
                 PROVE /\ charter'[x].alphabet \subseteq charter'[Parent[x]].alphabet
                       /\ charter'[x].budget <= charter'[Parent[x]].budget
      BY DEF CharterNarrows
    <3>1. CASE x = p
      <4>1. charter'[x] = c /\ charter'[Parent[x]] = charter[Parent[x]]
        BY <1>a, <2>1, <2>2, <3>1 DEF TypeOK
      <4> QED
        BY <2>1, <2>5, <3>1, <4>1
    <3>2. CASE x # p
      <4>1. x \in Planes /\ Parent[x] \in Planes
        BY ParentFacts
      <4>2. charter'[x] = charter[x]
        BY <1>a, <2>1, <2>2, <3>2, <4>1 DEF TypeOK
      <4>3. charter[x].seated
        BY <4>2
      <4>4. Parent[x] # p
        \* p is the child being seated, so it is unseated, and a plane is seated only below a seated parent.
        <5>1. SUFFICES ASSUME Parent[x] = p PROVE FALSE
          OBVIOUS
        <5>2. x = "b" /\ p = "a"
          BY <5>1, <3>2 DEF Parent, Children
        <5> QED
          BY <1>0, <2>1, <4>3, <5>2 DEF Shape, SeatOrder
      <4>5. charter'[Parent[x]] = charter[Parent[x]]
        BY <1>a, <2>1, <2>2, <4>1, <4>4 DEF TypeOK
      <4> QED
        BY <1>0, <4>2, <4>3, <4>5 DEF CharterNarrows
    <3> QED
      BY <3>1, <3>2
  <2> QED
    BY <1>0, <2>6 DEF InvNarrow
<1>3. ASSUME NEW p \in Children, NEW c \in Offered, SeatCaptured(p, c) PROVE InvNarrow'
  <2>1. /\ Parent[p] \in Captured
        /\ charter' = [charter EXCEPT ![p] = c]
        /\ c.seated
        /\ ~charter[p].seated
    BY <1>3, OfferedFacts DEF SeatCaptured
  <2>2. Parent[p] \in Planes /\ p \in Planes /\ Parent[p] # p
    BY ParentFacts
  <2>6. CharterNarrows'
    <3> SUFFICES ASSUME NEW x \in Children, charter'[x].seated, Parent[x] \notin Captured
                 PROVE /\ charter'[x].alphabet \subseteq charter'[Parent[x]].alphabet
                       /\ charter'[x].budget <= charter'[Parent[x]].budget
      BY DEF CharterNarrows
    <3>1. x # p
      BY <2>1
    <3>2. x \in Planes /\ Parent[x] \in Planes
      BY ParentFacts
    <3>3. charter'[x] = charter[x] /\ charter[x].seated
      BY <1>a, <2>1, <2>2, <3>1, <3>2 DEF TypeOK
    <3>4. Parent[x] # p
      <4>1. SUFFICES ASSUME Parent[x] = p PROVE FALSE
        OBVIOUS
      <4>2. x = "b" /\ p = "a"
        BY <4>1, <3>1 DEF Parent, Children
      <4> QED
        BY <1>0, <2>1, <3>3, <4>2 DEF Shape, SeatOrder
    <3>5. charter'[Parent[x]] = charter[Parent[x]]
      BY <1>a, <2>1, <2>2, <3>2, <3>4 DEF TypeOK
    <3> QED
      BY <1>0, <3>3, <3>5 DEF CharterNarrows
  <2> QED
    BY <1>0, <2>6 DEF InvNarrow
<1>4. QED
  <2>1. CASE \E p \in Children, c \in Offered : SeatHonest(p, c) \/ SeatCaptured(p, c)
    BY <2>1, <1>2, <1>3
  <2>2. CASE ~\E p \in Children, c \in Offered : SeatHonest(p, c) \/ SeatCaptured(p, c)
    <3>1. UNCHANGED charter
      BY <2>2 DEF Next, vars, Issue, MoveEpoch, Hear, Permit, Refuse
    <3> QED
      BY <3>1, <1>1
  <2> QED
    BY <2>1, <2>2

THEOREM CharterNarrowsAlways ==
  ASSUME Mut # "M_WIDEN"
  PROVE  Spec => []CharterNarrows
<1>1. InvNarrow /\ [Next]_vars => InvNarrow'
  BY NextCharterNarrows
<1>2. Init => CharterNarrows
  BY NoCharterFacts DEF Init, CharterNarrows, Planes, Children
<1>3. Init => InvNarrow
  BY <1>2, InitShape DEF InvNarrow
<1>4. InvNarrow => CharterNarrows
  BY DEF InvNarrow
<1> QED
  BY <1>1, <1>3, <1>4, PTL DEF Spec
-----------------------------------------------------------------------------
(* BudgetConserved: one account per honest plane, and their sum.               *)

InvBudget == Shape /\ Account

LEMMA InitAccount == Init => InvBudget
<1> SUFFICES ASSUME Init PROVE InvBudget OBVIOUS
<1>1. Shape
  BY InitShape
<1>2. Account
  BY RootBudgetNat, NoCharterFacts DEF Init, Account, ChildBudget, Planes, RootCharter
<1> QED
  BY <1>1, <1>2 DEF InvBudget

LEMMA NextAccount ==
  ASSUME Mut # "M_NODEBIT", InvBudget, [Next]_vars
  PROVE  InvBudget'
<1>0. Shape /\ Shape' /\ Account
  BY NextShape DEF InvBudget
<1>a. TypeOK /\ TypeOK'
  BY <1>0 DEF Shape
<1>1. CASE UNCHANGED <<charter, left, issued>>
  <2>1. Account'
    BY <1>0, <1>1 DEF Account, ChildBudget
  <2> QED
    BY <1>0, <2>1 DEF InvBudget
<1>2. ASSUME NEW p \in Children, NEW c \in Offered, SeatHonest(p, c) PROVE InvBudget'
  <2>1. /\ charter' = [charter EXCEPT ![p] = c]
        /\ left' = [left EXCEPT ![p] = c.budget, ![Parent[p]] = left[Parent[p]] - c.budget]
        /\ issued' = issued
        /\ c.seated /\ c.budget \in Nat
        /\ ~charter[p].seated
        /\ c.budget <= left[Parent[p]]
    BY <1>2, OfferedFacts DEF SeatHonest, Debit
  <2>2. /\ p \in Planes /\ Parent[p] \in Planes /\ Parent[p] # p
    BY ParentFacts
  <2>3. /\ charter[p] = NoCharter /\ left[p] = 0 /\ issued[p] = 0
    BY <1>0, <2>1, <2>2 DEF Shape, Unseated
  <2>4. Account'
    <3> SUFFICES ASSUME NEW x \in Planes, x \notin Captured
                 PROVE left'[x] + issued'[x] + ChildBudget(x)' = charter'[x].budget
      BY DEF Account
    <3>0. /\ left[x] \in Nat /\ issued[x] \in Nat /\ charter[x].budget \in Nat
      BY <1>a DEF TypeOK, CharterRec
    <3>1. left[x] + issued[x] + ChildBudget(x) = charter[x].budget
      BY <1>0 DEF Account
    <3>2. CASE x = p
      \* A new plane has no child yet.
      <4>1. ChildBudget(x)' = 0
        <5>1. CASE p = "a"
          <6>1. ~charter["b"].seated
            BY <1>0, <2>3, <5>1, NoCharterFacts DEF Shape, SeatOrder
          <6>2. charter["b"] = NoCharter
            BY <1>0, <6>1, ParentFacts DEF Shape, Unseated
          <6>3. charter'["b"] = charter["b"]
            BY <1>a, <2>1, <2>2, <5>1, ParentFacts DEF TypeOK
          <6> QED
            BY <3>2, <5>1, <6>2, <6>3, NoCharterFacts DEF ChildBudget
        <5>2. CASE p = "b"
          BY <3>2, <5>2 DEF ChildBudget
        <5> QED
          BY <5>1, <5>2 DEF Children
      <4>2. left'[x] = c.budget /\ issued'[x] = 0 /\ charter'[x] = c
        BY <1>a, <2>1, <2>2, <2>3, <3>2 DEF TypeOK
      <4> QED
        BY <2>1, <4>1, <4>2
    <3>3. CASE x = Parent[p]
      <4>1. left'[x] = left[x] - c.budget /\ issued'[x] = issued[x] /\ charter'[x] = charter[x]
        BY <1>a, <2>1, <2>2, <3>3 DEF TypeOK
      <4>2. ChildBudget(x) = 0 /\ ChildBudget(x)' = c.budget
        <5>1. CASE p = "a"
          <6>1. x = "r"
            BY <3>3, <5>1 DEF Parent
          <6>2. charter["a"] = NoCharter /\ charter'["a"] = c
            BY <1>a, <2>1, <2>2, <2>3, <5>1 DEF TypeOK
          <6> QED
            BY <5>1, <6>1, <6>2, NoCharterFacts DEF ChildBudget
        <5>2. CASE p = "b"
          <6>1. x = "a"
            BY <3>3, <5>2 DEF Parent
          <6>2. charter["b"] = NoCharter /\ charter'["b"] = c
            BY <1>a, <2>1, <2>2, <2>3, <5>2 DEF TypeOK
          <6> QED
            BY <5>2, <6>1, <6>2, NoCharterFacts DEF ChildBudget
        <5> QED
          BY <5>1, <5>2 DEF Children
      <4>3. c.budget <= left[x]
        BY <2>1, <3>3
      <4> QED
        BY <2>1, <3>0, <3>1, <4>1, <4>2, <4>3
    <3>4. CASE x # p /\ x # Parent[p]
      <4>1. left'[x] = left[x] /\ issued'[x] = issued[x] /\ charter'[x] = charter[x]
        BY <1>a, <2>1, <2>2, <3>4 DEF TypeOK
      <4>2. ChildBudget(x)' = ChildBudget(x)
        \* Only p's parent has p as its child.
        <5>1. CASE x = "r"
          <6>1. p # "a"
            BY <3>4, <5>1 DEF Parent
          <6>2. p = "b"
            BY <6>1 DEF Children
          <6>3. charter'["a"] = charter["a"]
            BY <1>a, <2>1, <2>2, <6>2, ParentFacts DEF TypeOK
          <6> QED
            BY <5>1, <6>3 DEF ChildBudget
        <5>2. CASE x = "a"
          <6>1. p # "b"
            BY <3>4, <5>2 DEF Parent
          <6>2. p = "a"
            BY <6>1 DEF Children
          <6> QED
            BY <3>4, <5>2, <6>2
        <5>3. CASE x = "b"
          BY <5>3 DEF ChildBudget
        <5> QED
          BY <5>1, <5>2, <5>3 DEF Planes
      <4> QED
        BY <3>1, <4>1, <4>2
    <3> QED
      BY <3>2, <3>3, <3>4
  <2> QED
    BY <1>0, <2>4 DEF InvBudget
<1>3. ASSUME NEW p \in Children, NEW c \in Offered, SeatCaptured(p, c) PROVE InvBudget'
  <2>1. /\ charter' = [charter EXCEPT ![p] = c]
        /\ left' = [left EXCEPT ![p] = c.budget]
        /\ issued' = issued
        /\ c.seated /\ c.budget \in Nat
        /\ ~charter[p].seated
        /\ Parent[p] \in Captured
    BY <1>3, OfferedFacts DEF SeatCaptured
  <2>2. /\ p \in Planes /\ Parent[p] \in Planes /\ Parent[p] # p
    BY ParentFacts
  <2>3. /\ charter[p] = NoCharter /\ left[p] = 0 /\ issued[p] = 0
    BY <1>0, <2>1, <2>2 DEF Shape, Unseated
  <2>4. Account'
    <3> SUFFICES ASSUME NEW x \in Planes, x \notin Captured
                 PROVE left'[x] + issued'[x] + ChildBudget(x)' = charter'[x].budget
      BY DEF Account
    <3>1. left[x] + issued[x] + ChildBudget(x) = charter[x].budget
      BY <1>0 DEF Account
    <3>2. x # Parent[p]
      BY <2>1
    <3>3. CASE x = p
      <4>1. ChildBudget(x)' = 0
        <5>1. CASE p = "a"
          <6>1. ~charter["b"].seated
            BY <1>0, <2>3, <5>1, NoCharterFacts DEF Shape, SeatOrder
          <6>2. charter["b"] = NoCharter
            BY <1>0, <6>1, ParentFacts DEF Shape, Unseated
          <6>3. charter'["b"] = charter["b"]
            BY <1>a, <2>1, <2>2, <5>1, ParentFacts DEF TypeOK
          <6> QED
            BY <3>3, <5>1, <6>2, <6>3, NoCharterFacts DEF ChildBudget
        <5>2. CASE p = "b"
          BY <3>3, <5>2 DEF ChildBudget
        <5> QED
          BY <5>1, <5>2 DEF Children
      <4>2. left'[x] = c.budget /\ issued'[x] = 0 /\ charter'[x] = c
        BY <1>a, <2>1, <2>2, <2>3, <3>3 DEF TypeOK
      <4> QED
        BY <2>1, <4>1, <4>2
    <3>4. CASE x # p
      <4>1. left'[x] = left[x] /\ issued'[x] = issued[x] /\ charter'[x] = charter[x]
        BY <1>a, <2>1, <2>2, <3>4 DEF TypeOK
      <4>2. ChildBudget(x)' = ChildBudget(x)
        <5>1. CASE p = "a"
          <6>1. x # "r"
            BY <2>1, <3>2, <5>1 DEF Parent
          <6>2. x = "b"
            BY <3>4, <5>1, <6>1 DEF Planes
          <6> QED
            BY <6>2 DEF ChildBudget
        <5>2. CASE p = "b"
          <6>1. x # "a"
            BY <3>2, <5>2 DEF Parent
          <6>2. charter'["a"] = charter["a"]
            BY <1>a, <2>1, <2>2, <5>2, ParentFacts DEF TypeOK
          <6> QED
            BY <6>1, <6>2 DEF ChildBudget
        <5> QED
          BY <5>1, <5>2 DEF Children
      <4> QED
        BY <3>1, <4>1, <4>2
    <3> QED
      BY <3>3, <3>4
  <2> QED
    BY <1>0, <2>4 DEF InvBudget
<1>4. ASSUME NEW p \in Planes, Issue(p) PROVE InvBudget'
  <2>1. /\ left[p] >= 1 /\ charter' = charter
        /\ left' = [left EXCEPT ![p] = left[p] - 1]
        /\ issued' = [issued EXCEPT ![p] = issued[p] + 1]
    BY <1>4 DEF Issue
  <2>2. Account'
    <3> SUFFICES ASSUME NEW x \in Planes, x \notin Captured
                 PROVE left'[x] + issued'[x] + ChildBudget(x)' = charter'[x].budget
      BY DEF Account
    <3>0. /\ left[x] \in Nat /\ issued[x] \in Nat /\ left[p] \in Nat /\ issued[p] \in Nat
      BY <1>a DEF TypeOK
    <3>1. left[x] + issued[x] + ChildBudget(x) = charter[x].budget
      BY <1>0 DEF Account
    <3>2. ChildBudget(x)' = ChildBudget(x)
      BY <2>1 DEF ChildBudget
    <3>3. CASE x = p
      BY <1>a, <2>1, <3>0, <3>1, <3>2, <3>3 DEF TypeOK
    <3>4. CASE x # p
      BY <1>a, <2>1, <3>1, <3>2, <3>4 DEF TypeOK
    <3> QED
      BY <3>3, <3>4
  <2> QED
    BY <1>0, <2>2 DEF InvBudget
<1>5. QED
  <2>1. CASE \E p \in Children, c \in Offered : SeatHonest(p, c) \/ SeatCaptured(p, c)
    BY <2>1, <1>2, <1>3
  <2>2. CASE \E p \in Planes : Issue(p)
    BY <2>2, <1>4
  <2>3. CASE /\ ~\E p \in Children, c \in Offered : SeatHonest(p, c) \/ SeatCaptured(p, c)
             /\ ~\E p \in Planes : Issue(p)
    <3>1. UNCHANGED <<charter, left, issued>>
      BY <2>3 DEF Next, vars, MoveEpoch, Hear, Permit, Refuse
    <3> QED
      BY <3>1, <1>1
  <2> QED
    BY <2>1, <2>2, <2>3

LEMMA AccountBounds == InvBudget => BudgetConserved
<1> SUFFICES ASSUME InvBudget, NEW x \in Planes, Below(x) \cap Captured = {}
             PROVE  TreeIssued(x) <= charter[x].budget
  BY DEF BudgetConserved
<1>0. TypeOK
  BY DEF InvBudget, Shape
<1>1. /\ left \in [Planes -> Nat] /\ issued \in [Planes -> Nat]
      /\ charter["r"].budget \in Nat /\ charter["a"].budget \in Nat /\ charter["b"].budget \in Nat
  BY <1>0 DEF TypeOK, CharterRec, Planes
<1>2. CASE x = "b"
  <2>1. "b" \notin Captured
    BY <1>2 DEF Below
  <2>2. left["b"] + issued["b"] + 0 = charter["b"].budget
    BY <2>1 DEF InvBudget, Account, ChildBudget, Planes
  <2> QED
    BY <1>1, <1>2, <2>2 DEF TreeIssued, Planes
<1>3. CASE x = "a"
  <2>1. "a" \notin Captured /\ "b" \notin Captured
    BY <1>3 DEF Below
  <2>2. /\ left["b"] + issued["b"] + 0 = charter["b"].budget
        /\ left["a"] + issued["a"] + charter["b"].budget = charter["a"].budget
    BY <2>1 DEF InvBudget, Account, ChildBudget, Planes
  <2> QED
    BY <1>1, <1>3, <2>2 DEF TreeIssued, Planes
<1>4. CASE x = "r"
  <2>1. "r" \notin Captured /\ "a" \notin Captured /\ "b" \notin Captured
    BY <1>4 DEF Below, Planes
  <2>2. /\ left["b"] + issued["b"] + 0 = charter["b"].budget
        /\ left["a"] + issued["a"] + charter["b"].budget = charter["a"].budget
        /\ left["r"] + issued["r"] + charter["a"].budget = charter["r"].budget
    BY <2>1 DEF InvBudget, Account, ChildBudget, Planes
  <2> QED
    BY <1>1, <1>4, <2>2 DEF TreeIssued, Planes
<1> QED
  BY <1>2, <1>3, <1>4 DEF Planes

THEOREM BudgetConservedAlways ==
  ASSUME Mut # "M_NODEBIT"
  PROVE  Spec => []BudgetConserved
<1>1. InvBudget /\ [Next]_vars => InvBudget'
  BY NextAccount
<1> QED
  BY InitAccount, <1>1, AccountBounds, PTL DEF Spec
-----------------------------------------------------------------------------
THEOREM SafeAlways ==
  ASSUME Mut = "none"
  PROVE  Spec => []Safe
<1>1. Spec => []CharterNarrows
  BY CharterNarrowsAlways
<1>2. Spec => []LeaseWithinChain
  BY LeaseWithinChainAlways
<1>3. Spec => []HavocPlaneBounded
  BY HavocPlaneBoundedAlways
<1>4. Spec => []BudgetConserved
  BY BudgetConservedAlways
<1>5. Spec => []AnyPlaneFences
  BY AnyPlaneFencesAlways
<1> QED
  BY <1>1, <1>2, <1>3, <1>4, <1>5, PTL DEF Safe
-----------------------------------------------------------------------------
(* Why the mutations must fail. The counterexamples are TLC's.                 *)

LEMMA MutWidenAdmitsAny ==
  ASSUME Mut = "M_WIDEN", NEW c, NEW par
  PROVE  Narrows(c, par)
  BY DEF Narrows

LEMMA MutLastLinkReadsOneCharter ==
  ASSUME Mut = "M_LASTLINK", NEW p, NEW e, e \in charter[p].alphabet
  PROVE  ChainChecked(p, e)
  BY DEF ChainChecked

LEMMA MutTrustPlaneChecksNothing ==
  ASSUME Mut = "M_TRUSTPLANE", NEW p \in Captured, NEW e
  PROVE  ChainChecked(p, e)
  BY DEF ChainChecked

LEMMA MutNoDebitDebitsNothing ==
  ASSUME Mut = "M_NODEBIT", NEW c
  PROVE  Debit(c) = 0
  BY DEF Debit

LEMMA MutStaleEpochReadsOneEpoch ==
  ASSUME Mut = "M_STALEEPOCH", NEW v, NEW p, NEW ep, ep >= heard[v][p]
  PROVE  FenceOK(v, p, ep)
  BY DEF FenceOK
=============================================================================
