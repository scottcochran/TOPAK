----------------------------- MODULE Seats_proof -----------------------------
(* TLAPS proofs of the two invariants Seats.tla states (ADR-0037 §9):           *)
(*                                                                               *)
(*   THEOREM OnlyThinkersAuthorAlways  == Spec => []OnlyThinkersAuthor           *)
(*                                                            (Mut # "M_KIND")   *)
(*   THEOREM OneSeatPerPrincipalAlways == Spec => []OneSeatPerPrincipal          *)
(*                                                            (Mut # "M_SEAT")   *)
(*   THEOREM SafeAlways                == Spec => []Safe      (Mut = "none")      *)
(*                                                                               *)
(* Each theorem takes as hypothesis only the mutation that breaks it, so the     *)
(* hypotheses are the "Breaks under" column of theorem-premise-binding.md.       *)
(* Seats.tla is cited by digest in ADR-0037 and is not edited; this module       *)
(* extends it. The mutations and the three witnesses stay with TLC              *)
(* (Seats-results-2026.09.29.txt). The module has no constants beyond Mut, so    *)
(* the proof carries no model assumptions.                                       *)
(*                                                                               *)
(* Check with:  ../tools/tlapm Seats_proof.tla   (from spec/; see                *)
(*              proof-results.sh for the results file)                           *)
EXTENDS Seats, TLAPS

LeaseRec == [live : BOOLEAN, principal : Principals \cup {"none"}, alphabet : SUBSET Acts]
TypeOK   == lease \in [Seats -> LeaseRec]

(* Facts about the finite tables: every kind bound is within Acts, and a kind    *)
(* bound admits an authoring act only for a thinker and Vote only for others.    *)
LEMMA KindBoundActs == \A s \in Seats : KindBound(KindOf[s]) \subseteq Acts
BY DEF Seats, KindOf, KindBound, Acts

LEMMA KindBoundKinds ==
    \A s \in Seats : \A a \in KindBound(KindOf[s]) :
        /\ a \in Authoring => KindOf[s] = "thinker"
        /\ a = "Vote"      => KindOf[s] # "thinker"
BY DEF Seats, KindOf, KindBound, Authoring

-----------------------------------------------------------------------------
(* The type invariant holds under every mutation.                                *)

LEMMA InitTypeOK == Init => TypeOK
BY DEF Init, TypeOK, LeaseRec, NoLease, Principals, Acts

LEMMA NextTypeOK == TypeOK /\ [Next]_vars => TypeOK'
<1> SUFFICES ASSUME TypeOK, [Next]_vars PROVE TypeOK' OBVIOUS
<1>1. CASE UNCHANGED vars
    BY <1>1 DEF TypeOK, vars
<1>2. ASSUME NEW s \in Seats, NEW p \in Principals, Grant(p, s) PROVE TypeOK'
    <2>1. KindBound(KindOf[s]) \subseteq Acts
        BY KindBoundActs
    <2> QED
        BY <1>2, <2>1 DEF Grant, TypeOK, LeaseRec
<1>3. ASSUME NEW s \in Seats, Act(s) PROVE TypeOK'
    BY <1>3 DEF Act, TypeOK
<1>4. ASSUME NEW s \in Seats, EndRound(s) PROVE TypeOK'
    BY <1>4 DEF EndRound, TypeOK, LeaseRec, NoLease
<1> QED
    BY <1>1, <1>2, <1>3, <1>4 DEF Next

-----------------------------------------------------------------------------
(* OnlyThinkersAuthor. The acted set only records acts from a live alphabet,     *)
(* and under the specified grant a live alphabet is the seat's kind bound.       *)

Alphabets == \A s \in Seats : lease[s].live => lease[s].alphabet = KindBound(KindOf[s])
InvA == TypeOK /\ Alphabets /\ OnlyThinkersAuthor

LEMMA InitInvA == Init => InvA
BY InitTypeOK DEF Init, InvA, Alphabets, OnlyThinkersAuthor, NoLease

LEMMA NextInvA ==
    ASSUME Mut # "M_KIND", InvA, [Next]_vars
    PROVE  InvA'
<1>0. TypeOK'
    BY NextTypeOK DEF InvA
<1>1. CASE UNCHANGED vars
    BY <1>0, <1>1 DEF InvA, TypeOK, Alphabets, OnlyThinkersAuthor, KindBound, KindOf, vars
<1>2. ASSUME NEW s \in Seats, NEW p \in Principals, Grant(p, s) PROVE InvA'
    <2>1. lease' = [lease EXCEPT ![s] = [live |-> TRUE, principal |-> p, alphabet |-> KindBound(KindOf[s])]]
        BY <1>2 DEF Grant
    <2>2. Alphabets'
        BY <2>1 DEF InvA, TypeOK, Alphabets
    <2> QED
        BY <1>0, <1>2, <2>2 DEF Grant, InvA, OnlyThinkersAuthor
<1>3. ASSUME NEW s \in Seats, Act(s) PROVE InvA'
    <2>1. PICK a \in lease[s].alphabet : acted' = acted \cup {[act |-> a, kind |-> KindOf[s]]}
        BY <1>3 DEF Act
    <2>2. a \in KindBound(KindOf[s])
        BY <1>3, <2>1 DEF Act, InvA, Alphabets
    <2>3. /\ a \in Authoring => KindOf[s] = "thinker"
          /\ a = "Vote"      => KindOf[s] # "thinker"
        BY <2>2, KindBoundKinds
    <2> QED
        BY <1>0, <1>3, <2>1, <2>3 DEF Act, InvA, Alphabets, OnlyThinkersAuthor
<1>4. ASSUME NEW s \in Seats, EndRound(s) PROVE InvA'
    BY <1>0, <1>4 DEF EndRound, InvA, TypeOK, Alphabets, OnlyThinkersAuthor, NoLease
<1> QED
    BY <1>1, <1>2, <1>3, <1>4 DEF Next

THEOREM OnlyThinkersAuthorAlways ==
    ASSUME Mut # "M_KIND"
    PROVE  Spec => []OnlyThinkersAuthor
<1>1. InvA /\ [Next]_vars => InvA'
    BY NextInvA
<1>2. InvA => OnlyThinkersAuthor
    BY DEF InvA
<1> QED
    BY InitInvA, <1>1, <1>2, PTL DEF Spec

-----------------------------------------------------------------------------
(* OneSeatPerPrincipal is inductive with the type invariant: a grant refuses a   *)
(* principal that holds another live seat.                                       *)

InvS == TypeOK /\ OneSeatPerPrincipal

LEMMA InitInvS == Init => InvS
BY InitTypeOK DEF Init, InvS, OneSeatPerPrincipal, NoLease

LEMMA NextInvS ==
    ASSUME Mut # "M_SEAT", InvS, [Next]_vars
    PROVE  InvS'
<1>0. TypeOK'
    BY NextTypeOK DEF InvS
<1>1. CASE UNCHANGED vars
    BY <1>0, <1>1 DEF InvS, TypeOK, OneSeatPerPrincipal, vars
<1>2. ASSUME NEW s \in Seats, NEW p \in Principals, Grant(p, s) PROVE InvS'
    <2>1. ~HoldsElsewhere(p, s)
        BY <1>2 DEF Grant
    <2>2. \A t \in Seats : t # s => (lease[t].live => lease[t].principal # p)
        BY <2>1 DEF HoldsElsewhere
    <2>3. \A t \in Seats : lease'[t] = IF t = s THEN [live |-> TRUE, principal |-> p,
                                                        alphabet |-> IF Mut = "M_KIND" THEN Acts ELSE KindBound(KindOf[s])]
                                                   ELSE lease[t]
        BY <1>2 DEF Grant, InvS, TypeOK
    <2> QED
        BY <1>0, <2>2, <2>3 DEF InvS, OneSeatPerPrincipal
<1>3. ASSUME NEW s \in Seats, Act(s) PROVE InvS'
    BY <1>0, <1>3 DEF Act, InvS, OneSeatPerPrincipal
<1>4. ASSUME NEW s \in Seats, EndRound(s) PROVE InvS'
    BY <1>0, <1>4 DEF EndRound, InvS, TypeOK, OneSeatPerPrincipal, NoLease
<1> QED
    BY <1>1, <1>2, <1>3, <1>4 DEF Next

THEOREM OneSeatPerPrincipalAlways ==
    ASSUME Mut # "M_SEAT"
    PROVE  Spec => []OneSeatPerPrincipal
<1>1. InvS /\ [Next]_vars => InvS'
    BY NextInvS
<1>2. InvS => OneSeatPerPrincipal
    BY DEF InvS
<1> QED
    BY InitInvS, <1>1, <1>2, PTL DEF Spec

THEOREM SafeAlways ==
    ASSUME Mut = "none"
    PROVE  Spec => []Safe
<1>1. Spec => []OnlyThinkersAuthor
    BY OnlyThinkersAuthorAlways
<1>2. Spec => []OneSeatPerPrincipal
    BY OneSeatPerPrincipalAlways
<1> QED
    BY <1>1, <1>2, PTL DEF Safe

-----------------------------------------------------------------------------
(* Why the mutations must fail. M_KIND grants every act to every seat, so an     *)
(* observer may Draft; M_SEAT drops the only guard against a second live seat.   *)
(* The counterexamples are TLC's.                                                *)
LEMMA MutKindGrantsAll ==
    ASSUME Mut = "M_KIND", TypeOK, NEW s \in Seats, NEW p \in Principals, Grant(p, s)
    PROVE  lease'[s].alphabet = Acts
BY DEF Grant, TypeOK

LEMMA MutSeatIgnoresHolder ==
    ASSUME Mut = "M_SEAT", TypeOK, NEW s \in Seats, NEW p \in Principals, ~lease[s].live
    PROVE  \E a : Grant(p, s) <=> (lease' = [lease EXCEPT ![s] = [live |-> TRUE, principal |-> p, alphabet |-> a]]
                                   /\ UNCHANGED acted)
BY DEF Grant

=============================================================================
