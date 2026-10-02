--------------------------- MODULE Observers_proof ---------------------------
(* TLAPS proofs of the two invariants Observers.tla states (ADR-0038 §8):       *)
(*                                                                               *)
(*   THEOREM DenyByAnyOfAlways    == Spec => []DenyByAnyOf    (Mut # "M_QUORUM") *)
(*   THEOREM ReachIsBoundedAlways == Spec => []ReachIsBounded (Mut # "M_REACH")  *)
(*   THEOREM SafeAlways           == Spec => []Safe           (Mut = "none")     *)
(*                                                                               *)
(* Each theorem takes as hypothesis only the mutation that breaks it. Both       *)
(* invariants are inductive by themselves: an admit is refused by any finding    *)
(* from a watcher, and a finding is only recorded within the observer's reach.   *)
(* Observers.tla is cited by digest in ADR-0038 and is not edited; this module   *)
(* extends it. The mutations and the four witnesses stay with TLC                *)
(* (Observers-results-2026.09.29.txt). No constants beyond Mut, so no model      *)
(* assumptions.                                                                  *)
(*                                                                               *)
(* Check with:  ../tools/tlapm Observers_proof.tla   (from spec/; see            *)
(*              proof-results.sh for the results file)                           *)
EXTENDS Observers, TLAPS

LEMMA InitSafe == Init => Safe
BY DEF Init, Safe, DenyByAnyOf, ReachIsBounded

-----------------------------------------------------------------------------
LEMMA NextDeny ==
    ASSUME Mut # "M_QUORUM", DenyByAnyOf, [Next]_vars
    PROVE  DenyByAnyOf'
<1>1. CASE UNCHANGED vars
    BY <1>1 DEF DenyByAnyOf, vars
<1>2. ASSUME NEW t \in Thinkers, Admit(t) PROVE DenyByAnyOf'
    <2>1. Found(t) \cap W(t) = {}
        BY <1>2 DEF Admit, Blocked
    <2> QED
        BY <1>2, <2>1 DEF Admit, DenyByAnyOf
<1>3. ASSUME NEW t \in Thinkers, Refuse(t) PROVE DenyByAnyOf'
    BY <1>3 DEF Refuse, DenyByAnyOf
<1>4. ASSUME NEW t \in Thinkers, EndRound(t) PROVE DenyByAnyOf'
    BY <1>4 DEF EndRound, DenyByAnyOf
<1>5. ASSUME NEW t \in Thinkers, NEW o \in Observers, Finding(o, t) PROVE DenyByAnyOf'
    BY <1>5 DEF Finding, DenyByAnyOf
<1> QED
    BY <1>1, <1>2, <1>3, <1>4, <1>5 DEF Next

THEOREM DenyByAnyOfAlways ==
    ASSUME Mut # "M_QUORUM"
    PROVE  Spec => []DenyByAnyOf
<1>1. DenyByAnyOf /\ [Next]_vars => DenyByAnyOf'
    BY NextDeny
<1>2. Init => DenyByAnyOf
    BY InitSafe DEF Safe
<1> QED
    BY <1>1, <1>2, PTL DEF Spec

-----------------------------------------------------------------------------
LEMMA NextReach ==
    ASSUME Mut # "M_REACH", ReachIsBounded, [Next]_vars
    PROVE  ReachIsBounded'
<1>1. CASE UNCHANGED vars
    BY <1>1 DEF ReachIsBounded, vars
<1>2. ASSUME NEW t \in Thinkers, Admit(t) PROVE ReachIsBounded'
    BY <1>2 DEF Admit, ReachIsBounded
<1>3. ASSUME NEW t \in Thinkers, Refuse(t) PROVE ReachIsBounded'
    BY <1>3 DEF Refuse, ReachIsBounded
<1>4. ASSUME NEW t \in Thinkers, EndRound(t) PROVE ReachIsBounded'
    BY <1>4 DEF EndRound, ReachIsBounded
<1>5. ASSUME NEW t \in Thinkers, NEW o \in Observers, Finding(o, t) PROVE ReachIsBounded'
    <2>1. CellOf[o] = "none" \/ CellOf[t] = CellOf[o]
        BY <1>5 DEF Finding, Reach
    <2> QED
        BY <1>5, <2>1 DEF Finding, ReachIsBounded
<1> QED
    BY <1>1, <1>2, <1>3, <1>4, <1>5 DEF Next

THEOREM ReachIsBoundedAlways ==
    ASSUME Mut # "M_REACH"
    PROVE  Spec => []ReachIsBounded
<1>1. ReachIsBounded /\ [Next]_vars => ReachIsBounded'
    BY NextReach
<1>2. Init => ReachIsBounded
    BY InitSafe DEF Safe
<1> QED
    BY <1>1, <1>2, PTL DEF Spec

THEOREM SafeAlways ==
    ASSUME Mut = "none"
    PROVE  Spec => []Safe
<1>1. Spec => []DenyByAnyOf
    BY DenyByAnyOfAlways
<1>2. Spec => []ReachIsBounded
    BY ReachIsBoundedAlways
<1> QED
    BY <1>1, <1>2, PTL DEF Safe

-----------------------------------------------------------------------------
(* Why the mutations must fail. M_REACH lets every observer reach every          *)
(* thinker, across cells; M_QUORUM lets one finding of two watchers through.     *)
(* The counterexamples are TLC's.                                                *)
LEMMA MutReachIsEverything ==
    ASSUME Mut = "M_REACH", NEW o \in Observers
    PROVE  Reach(o) = Thinkers
BY DEF Reach

LEMMA MutQuorumAdmitsOneOfTwo ==
    ASSUME Mut = "M_QUORUM", NEW t \in Thinkers,
           Cardinality(Found(t) \cap W(t)) = 1, Cardinality(W(t)) = 2
    PROVE  ~Blocked(t)
BY DEF Blocked

=============================================================================
