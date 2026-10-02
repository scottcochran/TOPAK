-------------------------- MODULE NonComposition_proof --------------------------
(* TLAPS proofs of the two invariants NonComposition.tla states (ADR-0013 §4):   *)
(*                                                                               *)
(*   THEOREM SafeAlways == Spec => []Safe        (Mut \notin {"M1", "M2"})       *)
(*   THEOREM NC1Always  == Spec => []NC1         (same)                          *)
(*   THEOREM NC2Always  == Spec => []NC2         (same)                          *)
(*                                                                               *)
(* Both mutations break both invariants (NonComposition-results-2026.09.23.txt,  *)
(* rows m1, m1x, m2, m2x), so the hypotheses are the same for each. The          *)
(* inductive invariant adds to NC2 that the records NC1 needs were created: an   *)
(* admit record for every admitted effect, the break-glass record once           *)
(* break-glass is active, and that only admitted effects went via break-glass.   *)
(* NC2 then keeps them retained, because a forensic record is never erasable     *)
(* under the specified rule.                                                     *)
(*                                                                               *)
(* NonComposition.tla is cited by digest in ADR-0013 and is not edited; this     *)
(* module extends it. The mutations and the three witnesses stay with TLC; the   *)
(* two lemmas at the end say why each mutation must fail. No constants beyond    *)
(* Mut, so no model assumptions.                                                 *)
(*                                                                               *)
(* Check with:  ../tools/tlapm NonComposition_proof.tla   (from spec/; see       *)
(*              proof-results.sh for the results file)                           *)
EXTENDS NonComposition, TLAPS

BGCreated     == bgActive => BGRecord \in created
ViaBGAdmitted == viaBG \subseteq admitted
AdmitCreated  == \A e \in admitted : /\ AdmitRec(e) \in created
                                     /\ e \in viaBG => BGRecord \in created
Inv == NC2 /\ BGCreated /\ ViaBGAdmitted /\ AdmitCreated

(* Under the specified rule, a forensic record is not erasable.                  *)
LEMMA ForensicKept ==
    ASSUME Mut # "M1", Mut # "M2", NEW r, r.kind \in ForensicKinds
    PROVE  ~Erasable(r)
BY DEF Erasable

LEMMA InitInv == Init => Inv
BY DEF Init, Inv, NC2, BGCreated, ViaBGAdmitted, AdmitCreated

LEMMA NextInv ==
    ASSUME Mut # "M1", Mut # "M2", Inv, [Next]_vars
    PROVE  Inv'
<1>1. CASE UNCHANGED vars
    BY <1>1 DEF Inv, NC2, BGCreated, ViaBGAdmitted, AdmitCreated, vars
<1>2. CASE InvokeBG
    BY <1>2 DEF InvokeBG, Inv, NC2, BGCreated, ViaBGAdmitted, AdmitCreated, BGRecord, ForensicKinds
<1>3. ASSUME NEW e \in Effects, Admit(e) PROVE Inv'
    <2>1. /\ admitted' = admitted \cup {e}
          /\ viaBG'    = IF bgActive THEN viaBG \cup {e} ELSE viaBG
          /\ created'  = created  \cup {AdmitRec(e), PayRec(e)}
          /\ retained' = retained \cup {AdmitRec(e), PayRec(e)}
          /\ UNCHANGED bgActive
        BY <1>3 DEF Admit
    <2>2. NC2'
        BY <2>1 DEF Inv, NC2
    <2>3. BGCreated'
        BY <2>1 DEF Inv, BGCreated
    <2>4. ViaBGAdmitted'
        BY <2>1 DEF Inv, ViaBGAdmitted
    <2>5. AdmitCreated'
        BY <2>1 DEF Inv, BGCreated, ViaBGAdmitted, AdmitCreated, AdmitRec, PayRec, BGRecord
    <2> QED
        BY <2>2, <2>3, <2>4, <2>5 DEF Inv
<1>4. CASE Erase
    <2>1. PICK S \in SUBSET retained :
            /\ S # {}
            /\ \A r \in S : Erasable(r)
            /\ created'  = created \cup {EraseRecord}
            /\ retained' = IF EraseRecord \in created
                           THEN retained \ S
                           ELSE (retained \ S) \cup {EraseRecord}
        BY <1>4 DEF Erase
    <2>2. \A r \in S : r.kind \notin ForensicKinds
        BY <2>1, ForensicKept
    <2>3. NC2'
        BY <2>1, <2>2 DEF Inv, NC2, EraseRecord, ForensicKinds
    <2> QED
        BY <1>4, <2>1, <2>3 DEF Erase, Inv, BGCreated, ViaBGAdmitted, AdmitCreated
<1> QED
    BY <1>1, <1>2, <1>3, <1>4 DEF Next

(* NC1 follows: the records it needs were created, and NC2 keeps them.           *)
LEMMA InvSafe == Inv => Safe
BY DEF Inv, Safe, NC1, NC2, Attributable, AdmitCreated, AdmitRec, BGRecord, ForensicKinds

THEOREM SafeAlways ==
    ASSUME Mut # "M1", Mut # "M2"
    PROVE  Spec => []Safe
<1>1. Inv /\ [Next]_vars => Inv'
    BY NextInv
<1> QED
    BY InitInv, <1>1, InvSafe, PTL DEF Spec

THEOREM NC1Always ==
    ASSUME Mut # "M1", Mut # "M2"
    PROVE  Spec => []NC1
<1>1. Spec => []Safe
    BY SafeAlways
<1> QED
    BY <1>1, PTL DEF Safe

THEOREM NC2Always ==
    ASSUME Mut # "M1", Mut # "M2"
    PROVE  Spec => []NC2
<1>1. Spec => []Safe
    BY SafeAlways
<1> QED
    BY <1>1, PTL DEF Safe

-----------------------------------------------------------------------------
(* Why the mutations must fail. M1 makes the admit record erasable, so an        *)
(* admitted effect can lose its attribution; M2 makes everything erasable while  *)
(* break-glass is active. The counterexamples are TLC's.                         *)
LEMMA MutM1ErasesAdmitRecord ==
    ASSUME Mut = "M1", NEW e
    PROVE  Erasable(AdmitRec(e))
BY DEF Erasable, AdmitRec, ForensicKinds

LEMMA MutM2ErasesAllUnderBreakGlass ==
    ASSUME Mut = "M2", bgActive, NEW r
    PROVE  Erasable(r)
BY DEF Erasable

=============================================================================
