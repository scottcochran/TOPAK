------------------------ MODULE BreakGlass_A1_proof ------------------------
(* TLAPS proof of the invariant BreakGlass_A1.tla states, for every floor      *)
(* subset, epoch bound and round bound:                                         *)
(*                                                                              *)
(*   THEOREM NeverChangesAuthority ==                                           *)
(*     Spec => []EmergencyNeverChangesAuthority                                 *)
(*       (Mut # "M_SCOPE", and Mut = "M_KIND" => "R7" \in Active)               *)
(*                                                                              *)
(* The hypotheses are exactly the two rows TLC breaks the invariant on          *)
(* (BreakGlass_A1-results): the mechanism ignoring the lease's alphabet, and    *)
(* the kind's alphabet widened with R7 dropped. Unlike its predecessor's proof, *)
(* this one does not assume R7 is in force: under the kind's alphabet as        *)
(* decided, R7 has nothing to refuse (ADR-0026 A2), and the theorem holds       *)
(* without it. R7 is needed only under M_KIND, and the hypothesis says so.      *)
(*                                                                              *)
(* Nothing is assumed of Active, MaxEpoch or MaxRound. The witnesses stay with  *)
(* TLC; the two lemmas at the end say why each mutation must fail.              *)
(*                                                                              *)
(* Check with:  ../tools/tlapm BreakGlass_A1_proof.tla   (from spec/; see       *)
(*              proof-results.sh and proof-cert.sh for the results files)       *)
EXTENDS BreakGlass_A1, TLAPS

(* The inductive invariant: nothing done from the seat changes authority, and   *)
(* the lease it holds, if any, has no authority act in its alphabet.            *)
LeaseClean == lease.alphabet \cap AuthActs = {}
Inv == EmergencyNeverChangesAuthority /\ LeaseClean

LEMMA InitInv == Init => Inv
BY DEF Init, Inv, EmergencyNeverChangesAuthority, LeaseClean, NoLease

(* The alphabet an activation grants holds no authority act: by the kind where  *)
(* the kind is as decided, and by R7 where it is not.                           *)
LEMMA ActivationClean ==
    ASSUME Mut = "M_KIND" => "R7" \in Active, R7Admits(KindAlphabet)
    PROVE  KindAlphabet \cap AuthActs = {}
BY DEF R7Admits, KindAlphabet, AuthActs

LEMMA NextInv ==
    ASSUME Mut # "M_SCOPE", Mut = "M_KIND" => "R7" \in Active, Inv, [Next]_vars
    PROVE  Inv'
<1>1. CASE UNCHANGED vars
    BY <1>1 DEF Inv, EmergencyNeverChangesAuthority, LeaseClean, vars
<1>2. CASE Issue
    BY <1>2 DEF Issue, Inv, EmergencyNeverChangesAuthority, LeaseClean, NoLease
<1>3. CASE Activate
    <2>1. KindAlphabet \cap AuthActs = {}
        BY <1>3, ActivationClean DEF Activate
    <2>2. lease'.alphabet = KindAlphabet
        BY <1>3 DEF Activate
    <2> QED
        BY <1>3, <2>1, <2>2 DEF Activate, Inv, EmergencyNeverChangesAuthority, LeaseClean
<1>4. CASE Act
    <2>1. PICK x \in BGActs : Admits(x) /\ emDid' = emDid \cup {x}
        BY <1>4 DEF Act
    <2>2. x \in lease.alphabet
        BY <2>1 DEF Admits
    <2>3. x \notin AuthActs
        BY <2>2 DEF Inv, LeaseClean
    <2>4. (emDid \cup {x}) \cap AuthActs = {}
        BY <2>3 DEF Inv, EmergencyNeverChangesAuthority
    <2> QED
        BY <1>4, <2>1, <2>4 DEF Act, Inv, EmergencyNeverChangesAuthority, LeaseClean
<1>5. CASE EndRound
    BY <1>5 DEF EndRound, Inv, EmergencyNeverChangesAuthority, LeaseClean, NoLease
<1> QED
    BY <1>1, <1>2, <1>3, <1>4, <1>5 DEF Next

THEOREM NeverChangesAuthority ==
    ASSUME Mut # "M_SCOPE", Mut = "M_KIND" => "R7" \in Active
    PROVE  Spec => []EmergencyNeverChangesAuthority
<1>1. Inv /\ [Next]_vars => Inv'
    BY NextInv
<1>2. Inv => EmergencyNeverChangesAuthority
    BY DEF Inv
<1> QED
    BY InitInv, <1>1, <1>2, PTL DEF Spec

-----------------------------------------------------------------------------
(* Why the mutations must fail. With the lease's alphabet ignored, every        *)
(* action is admitted from the seat. With the kind's alphabet widened and R7    *)
(* dropped, the activation is admitted and grants an authority act. The         *)
(* counterexamples themselves are TLC's (rows a1-scope and a1-kindr7).          *)
LEMMA MutScopeAdmitsAuthority ==
    ASSUME Mut = "M_SCOPE"
    PROVE  \A x \in AuthActs : x \in BGActs /\ Admits(x)
BY DEF Admits, BGActs

LEMMA MutKindGrantsAuthority ==
    ASSUME Mut = "M_KIND", "R7" \notin Active
    PROVE  R7Admits(KindAlphabet) /\ AuthActs \subseteq KindAlphabet
BY DEF R7Admits, KindAlphabet, BGActs

=============================================================================
