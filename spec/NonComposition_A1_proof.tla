------------------------ MODULE NonComposition_A1_proof ------------------------
(* TLAPS proofs of the two invariants NonComposition_A1.tla states (ADR-0013     *)
(* §4, with break-glass as ADR-0052's emergency seating):                        *)
(*                                                                               *)
(*   THEOREM SafeAlways == Spec => []Safe   (Mut \notin {"M1", "M2", "M3"})      *)
(*   THEOREM NC1Always  == Spec => []NC1    (same)                               *)
(*   THEOREM NC2Always  == Spec => []NC2    (same)                               *)
(*                                                                               *)
(* Each of the three mutations breaks both invariants                            *)
(* (NonComposition_A1-results, rows m1 to m3x), so the hypotheses are the same   *)
(* for each. The inductive invariant adds to NC2 that the records NC1 needs      *)
(* were created: an admit record for every admitted effect, and, for every       *)
(* effect admitted under an activation, that activation's record. NC2 then       *)
(* keeps them retained, because a forensic record is never erasable under the    *)
(* specified rule, whether or not its round is still live.                       *)
(*                                                                               *)
(* Nothing is assumed of MaxRound. The witnesses stay with TLC; the lemmas at    *)
(* the end say why each mutation must fail.                                      *)
(*                                                                               *)
(* Check with:  ../tools/tlapm NonComposition_A1_proof.tla   (from spec/; see    *)
(*              proof-results.sh and proof-cert.sh for the results files)        *)
EXTENDS NonComposition_A1, TLAPS

LiveCreated  == live # 0 => ActRecord(live) \in created
ViaCreated   == \A e, r : <<e, r>> \in via => e \in admitted /\ ActRecord(r) \in created
AdmitCreated == \A e \in admitted : AdmitRec(e) \in created
Inv == NC2 /\ LiveCreated /\ ViaCreated /\ AdmitCreated

(* Under the specified rule, a forensic record is not erasable.                  *)
LEMMA ForensicKept ==
    ASSUME Mut # "M1", Mut # "M2", Mut # "M3", NEW r, r.kind \in ForensicKinds
    PROVE  ~Erasable(r)
BY DEF Erasable

LEMMA InitInv == Init => Inv
BY DEF Init, Inv, NC2, LiveCreated, ViaCreated, AdmitCreated

LEMMA NextInv ==
    ASSUME Mut # "M1", Mut # "M2", Mut # "M3", Inv, [Next]_vars
    PROVE  Inv'
<1>1. CASE UNCHANGED vars
    BY <1>1 DEF Inv, NC2, LiveCreated, ViaCreated, AdmitCreated, vars
<1>2. CASE Activate
    <2>1. /\ live' = last + 1
          /\ created'  = created \cup {ActRecord(last + 1)}
          /\ retained' = retained \cup {ActRecord(last + 1)}
          /\ UNCHANGED <<admitted, via>>
        BY <1>2 DEF Activate
    <2>2. NC2'
        BY <2>1 DEF Inv, NC2
    <2>3. LiveCreated'
        BY <2>1 DEF LiveCreated
    <2>4. ViaCreated' /\ AdmitCreated'
        BY <2>1 DEF Inv, ViaCreated, AdmitCreated
    <2> QED
        BY <2>2, <2>3, <2>4 DEF Inv
<1>3. CASE EndRound
    BY <1>3 DEF EndRound, Inv, NC2, LiveCreated, ViaCreated, AdmitCreated
<1>4. ASSUME NEW e \in Effects, Admit(e) PROVE Inv'
    <2>1. /\ admitted' = admitted \cup {e}
          /\ via'      = IF live # 0 THEN via \cup {<<e, live>>} ELSE via
          /\ created'  = created  \cup {AdmitRec(e), PayRec(e)}
          /\ retained' = retained \cup {AdmitRec(e), PayRec(e)}
          /\ UNCHANGED <<live, last>>
        BY <1>4 DEF Admit
    <2>2. NC2'
        BY <2>1 DEF Inv, NC2
    <2>3. LiveCreated'
        BY <2>1 DEF Inv, LiveCreated
    <2>4. AdmitCreated'
        BY <2>1 DEF Inv, AdmitCreated
    <2>5. ViaCreated'
        <3>1. SUFFICES ASSUME NEW e2, NEW r2, <<e2, r2>> \in via'
                       PROVE  e2 \in admitted' /\ ActRecord(r2) \in created'
            BY DEF ViaCreated
        <3>2. CASE <<e2, r2>> \in via
            BY <3>2, <2>1 DEF Inv, ViaCreated
        <3>3. CASE <<e2, r2>> \notin via
            <4>1. live # 0 /\ <<e2, r2>> = <<e, live>>
                BY <3>1, <3>3, <2>1
            <4>2. e2 = e /\ r2 = live
                BY <4>1
            <4> QED
                BY <4>1, <4>2, <2>1 DEF Inv, LiveCreated
        <3> QED
            BY <3>2, <3>3
    <2> QED
        BY <2>2, <2>3, <2>4, <2>5 DEF Inv
<1>5. CASE Erase
    <2>1. PICK S \in SUBSET retained :
            /\ S # {}
            /\ \A r \in S : Erasable(r)
            /\ created'  = created \cup {EraseRecord}
            /\ retained' = IF EraseRecord \in created
                           THEN retained \ S
                           ELSE (retained \ S) \cup {EraseRecord}
        BY <1>5 DEF Erase
    <2>2. \A r \in S : r.kind \notin ForensicKinds
        BY <2>1, ForensicKept
    <2>3. NC2'
        BY <2>1, <2>2 DEF Inv, NC2, EraseRecord, ForensicKinds
    <2>4. UNCHANGED <<admitted, via, live, last>>
        BY <1>5 DEF Erase
    <2> QED
        BY <2>1, <2>3, <2>4 DEF Inv, LiveCreated, ViaCreated, AdmitCreated
<1> QED
    BY <1>1, <1>2, <1>3, <1>4, <1>5 DEF Next

(* NC1 follows: the records it needs were created, and NC2 keeps them.           *)
LEMMA InvSafe == Inv => Safe
<1>1. SUFFICES ASSUME Inv PROVE NC1
    BY DEF Inv, Safe
<1>2. \A e \in admitted : AdmitRec(e) \in retained
    BY <1>1 DEF Inv, NC2, AdmitCreated, AdmitRec, ForensicKinds
<1>3. \A e, r : <<e, r>> \in via => ActRecord(r) \in retained
    BY <1>1 DEF Inv, NC2, ViaCreated, ActRecord, ForensicKinds
<1> QED
    BY <1>2, <1>3 DEF NC1, Attributable

THEOREM SafeAlways ==
    ASSUME Mut # "M1", Mut # "M2", Mut # "M3"
    PROVE  Spec => []Safe
<1>1. Inv /\ [Next]_vars => Inv'
    BY NextInv
<1> QED
    BY InitInv, <1>1, InvSafe, PTL DEF Spec

THEOREM NC1Always ==
    ASSUME Mut # "M1", Mut # "M2", Mut # "M3"
    PROVE  Spec => []NC1
<1>1. Spec => []Safe
    BY SafeAlways
<1> QED
    BY <1>1, PTL DEF Safe

THEOREM NC2Always ==
    ASSUME Mut # "M1", Mut # "M2", Mut # "M3"
    PROVE  Spec => []NC2
<1>1. Spec => []Safe
    BY SafeAlways
<1> QED
    BY <1>1, PTL DEF Safe

-----------------------------------------------------------------------------
(* Why the mutations must fail. M1 makes the admit record erasable. M2 makes     *)
(* everything erasable while an emergency lease is live. M3 makes an             *)
(* activation's record erasable once its round is no longer the live one, which  *)
(* is every activation's record in the end. The counterexamples are TLC's.       *)
LEMMA MutM1ErasesAdmitRecord ==
    ASSUME Mut = "M1", NEW e
    PROVE  Erasable(AdmitRec(e))
BY DEF Erasable, AdmitRec, ForensicKinds

LEMMA MutM2ErasesAllUnderALiveLease ==
    ASSUME Mut = "M2", live # 0, NEW r
    PROVE  Erasable(r)
BY DEF Erasable

LEMMA MutM3ErasesAnEndedRoundsRecord ==
    ASSUME Mut = "M3", NEW r, r # live
    PROVE  Erasable(ActRecord(r))
BY DEF Erasable, ActRecord

=============================================================================
