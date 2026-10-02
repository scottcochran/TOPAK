---------------------------- MODULE RunSeats_proof ----------------------------
(* TLAPS proofs of the three invariants RunSeats.tla states (ADR-0043 §8):      *)
(*                                                                               *)
(*   THEOREM OnlyThinkersActuateAlways       == Spec => []OnlyThinkersActuate    *)
(*                                                        (Mut # "M_KIND")       *)
(*   THEOREM ObserversConsultAndReportAlways == Spec => []ObserversConsultAndReport *)
(*                                                        (Mut \notin {"M_KIND", "M_DOMAIN"}) *)
(*   THEOREM NoNameCrossesDomainsAlways      == Spec => []NoNameCrossesDomains   *)
(*                                                        (Mut # "M_DOMAIN")     *)
(*   THEOREM SafeAlways                      == Spec => []Safe   (Mut = "none")  *)
(*                                                                               *)
(* Each theorem takes as hypothesis only the mutations that break it. The        *)
(* fourth mutation, M_OBSEMIT, breaks none of the three invariants: it narrows   *)
(* an observer's bound, and the invariants are upper bounds on what a seat       *)
(* does. RunSeats.tla is cited by digest in ADR-0043 and is not edited; this     *)
(* module extends it. The mutations and the three witnesses stay with TLC        *)
(* (RunSeats-results-2026.09.29.txt). No constants beyond Mut, so no model       *)
(* assumptions.                                                                  *)
(*                                                                               *)
(* Check with:  ../tools/tlapm RunSeats_proof.tla   (from spec/; see             *)
(*              proof-results.sh for the results file)                           *)
EXTENDS RunSeats, TLAPS

LeaseRec == [live : BOOLEAN, alphabet : SUBSET Acts]
TypeOK   == lease \in [Seats -> LeaseRec]

(* The alphabet a seat is granted under the specified mechanism: its kind bound  *)
(* cut to its domain. Each invariant needs one of the two cuts.                  *)
ByKind(s)   == IF Mut = "M_KIND"   THEN Acts ELSE KindBound(KindOf[s])
ByDomain(s) == IF Mut = "M_DOMAIN" THEN Acts ELSE DomainActs(DomainOf[s])

LEMMA GrantAlphabet ==
    ASSUME NEW s \in Seats, Grant(s)
    PROVE  lease' = [lease EXCEPT ![s] = [live |-> TRUE, alphabet |-> ByKind(s) \cap ByDomain(s)]]
BY DEF Grant, ByKind, ByDomain

LEMMA BoundsInActs == \A s \in Seats : ByKind(s) \cap ByDomain(s) \subseteq Acts
BY DEF Seats, KindOf, DomainOf, KindBound, DomainActs, ByKind, ByDomain, Acts, BuildActs, RunActs

(* The three facts the invariants rest on, one per invariant.                    *)
LEMMA KindActuate ==
    ASSUME Mut # "M_KIND", NEW s \in Seats, NEW a \in ByKind(s), a = "Actuate"
    PROVE  KindOf[s] = "thinker"
BY DEF Seats, KindOf, KindBound, ByKind

LEMMA ObserverRun ==
    ASSUME Mut # "M_KIND", Mut # "M_DOMAIN", NEW s \in Seats,
           NEW a \in ByKind(s) \cap ByDomain(s), KindOf[s] = "observer", DomainOf[s] = "run"
    PROVE  a \in {"Consult", "Report"}
BY DEF Seats, KindOf, DomainOf, KindBound, DomainActs, ByKind, ByDomain, RunActs

LEMMA DomainNames ==
    ASSUME Mut # "M_DOMAIN", NEW s \in Seats, NEW a \in ByDomain(s)
    PROVE  (a \in RunActs) <=> (DomainOf[s] = "run")
BY DEF Seats, DomainOf, DomainActs, ByDomain, RunActs, BuildActs

-----------------------------------------------------------------------------
LEMMA InitTypeOK == Init => TypeOK
BY DEF Init, TypeOK, LeaseRec, NoLease

LEMMA NextTypeOK == TypeOK /\ [Next]_vars => TypeOK'
<1> SUFFICES ASSUME TypeOK, [Next]_vars PROVE TypeOK' OBVIOUS
<1>1. CASE UNCHANGED vars
    BY <1>1 DEF TypeOK, vars
<1>2. ASSUME NEW s \in Seats, Grant(s) PROVE TypeOK'
    BY <1>2, GrantAlphabet, BoundsInActs DEF Grant, TypeOK, LeaseRec
<1>3. ASSUME NEW s \in Seats, Act(s) PROVE TypeOK'
    BY <1>3 DEF Act, TypeOK
<1>4. ASSUME NEW s \in Seats, EndRound(s) PROVE TypeOK'
    BY <1>4 DEF EndRound, TypeOK, LeaseRec, NoLease
<1> QED
    BY <1>1, <1>2, <1>3, <1>4 DEF Next

(* Every live alphabet is the granted one. This holds under every mutation,      *)
(* since ByKind and ByDomain carry the mutation inside them.                     *)
Alphabets == \A s \in Seats : lease[s].live => lease[s].alphabet = ByKind(s) \cap ByDomain(s)
Inv == TypeOK /\ Alphabets

LEMMA InitInv == Init => Inv
BY InitTypeOK DEF Init, Inv, Alphabets, NoLease

LEMMA NextInv == Inv /\ [Next]_vars => Inv'
<1> SUFFICES ASSUME Inv, [Next]_vars PROVE Inv' OBVIOUS
<1>0. TypeOK'
    BY NextTypeOK DEF Inv
<1>1. CASE UNCHANGED vars
    BY <1>0, <1>1 DEF Inv, Alphabets, ByKind, ByDomain, vars
<1>2. ASSUME NEW s \in Seats, Grant(s) PROVE Inv'
    BY <1>0, <1>2, GrantAlphabet DEF Inv, TypeOK, Alphabets, ByKind, ByDomain
<1>3. ASSUME NEW s \in Seats, Act(s) PROVE Inv'
    BY <1>0, <1>3 DEF Act, Inv, Alphabets, ByKind, ByDomain
<1>4. ASSUME NEW s \in Seats, EndRound(s) PROVE Inv'
    BY <1>0, <1>4 DEF EndRound, Inv, TypeOK, Alphabets, ByKind, ByDomain, NoLease
<1> QED
    BY <1>1, <1>2, <1>3, <1>4 DEF Next

(* An act records an element of the granted alphabet with the seat's tables.    *)
LEMMA ActRecord ==
    ASSUME Inv, NEW s \in Seats, Act(s)
    PROVE  \E a \in ByKind(s) \cap ByDomain(s) :
             acted' = acted \cup {[act |-> a, kind |-> KindOf[s], domain |-> DomainOf[s]]}
BY DEF Act, Inv, Alphabets

(* The three invariants, each inductive together with Inv under its hypothesis. *)
LEMMA NextActuate ==
    ASSUME Mut # "M_KIND", Inv, OnlyThinkersActuate, [Next]_vars
    PROVE  OnlyThinkersActuate'
<1>1. CASE UNCHANGED vars
    BY <1>1 DEF OnlyThinkersActuate, vars
<1>2. ASSUME NEW s \in Seats, Grant(s) PROVE OnlyThinkersActuate'
    BY <1>2 DEF Grant, OnlyThinkersActuate
<1>3. ASSUME NEW s \in Seats, Act(s) PROVE OnlyThinkersActuate'
    <2>1. PICK a \in ByKind(s) \cap ByDomain(s) :
            acted' = acted \cup {[act |-> a, kind |-> KindOf[s], domain |-> DomainOf[s]]}
        BY <1>3, ActRecord
    <2>2. a = "Actuate" => KindOf[s] = "thinker"
        BY KindActuate
    <2> QED
        BY <2>1, <2>2 DEF OnlyThinkersActuate
<1>4. ASSUME NEW s \in Seats, EndRound(s) PROVE OnlyThinkersActuate'
    BY <1>4 DEF EndRound, OnlyThinkersActuate
<1> QED
    BY <1>1, <1>2, <1>3, <1>4 DEF Next

LEMMA NextObservers ==
    ASSUME Mut # "M_KIND", Mut # "M_DOMAIN", Inv, ObserversConsultAndReport, [Next]_vars
    PROVE  ObserversConsultAndReport'
<1>1. CASE UNCHANGED vars
    BY <1>1 DEF ObserversConsultAndReport, vars
<1>2. ASSUME NEW s \in Seats, Grant(s) PROVE ObserversConsultAndReport'
    BY <1>2 DEF Grant, ObserversConsultAndReport
<1>3. ASSUME NEW s \in Seats, Act(s) PROVE ObserversConsultAndReport'
    <2>1. PICK a \in ByKind(s) \cap ByDomain(s) :
            acted' = acted \cup {[act |-> a, kind |-> KindOf[s], domain |-> DomainOf[s]]}
        BY <1>3, ActRecord
    <2>2. (KindOf[s] = "observer" /\ DomainOf[s] = "run") => a \in {"Consult", "Report"}
        BY ObserverRun
    <2> QED
        BY <2>1, <2>2 DEF ObserversConsultAndReport
<1>4. ASSUME NEW s \in Seats, EndRound(s) PROVE ObserversConsultAndReport'
    BY <1>4 DEF EndRound, ObserversConsultAndReport
<1> QED
    BY <1>1, <1>2, <1>3, <1>4 DEF Next

LEMMA NextDomains ==
    ASSUME Mut # "M_DOMAIN", Inv, NoNameCrossesDomains, [Next]_vars
    PROVE  NoNameCrossesDomains'
<1>1. CASE UNCHANGED vars
    BY <1>1 DEF NoNameCrossesDomains, vars
<1>2. ASSUME NEW s \in Seats, Grant(s) PROVE NoNameCrossesDomains'
    BY <1>2 DEF Grant, NoNameCrossesDomains
<1>3. ASSUME NEW s \in Seats, Act(s) PROVE NoNameCrossesDomains'
    <2>1. PICK a \in ByKind(s) \cap ByDomain(s) :
            acted' = acted \cup {[act |-> a, kind |-> KindOf[s], domain |-> DomainOf[s]]}
        BY <1>3, ActRecord
    <2>2. (a \in RunActs) <=> (DomainOf[s] = "run")
        BY DomainNames
    <2> QED
        BY <2>1, <2>2 DEF NoNameCrossesDomains
<1>4. ASSUME NEW s \in Seats, EndRound(s) PROVE NoNameCrossesDomains'
    BY <1>4 DEF EndRound, NoNameCrossesDomains
<1> QED
    BY <1>1, <1>2, <1>3, <1>4 DEF Next

-----------------------------------------------------------------------------
LEMMA InitAll == Init => OnlyThinkersActuate /\ ObserversConsultAndReport /\ NoNameCrossesDomains
BY DEF Init, OnlyThinkersActuate, ObserversConsultAndReport, NoNameCrossesDomains

THEOREM OnlyThinkersActuateAlways ==
    ASSUME Mut # "M_KIND"
    PROVE  Spec => []OnlyThinkersActuate
<1>1. (Inv /\ OnlyThinkersActuate) /\ [Next]_vars => (Inv /\ OnlyThinkersActuate)'
    BY NextInv, NextActuate
<1>2. Init => Inv /\ OnlyThinkersActuate
    BY InitInv, InitAll
<1> QED
    BY <1>1, <1>2, PTL DEF Spec

THEOREM ObserversConsultAndReportAlways ==
    ASSUME Mut # "M_KIND", Mut # "M_DOMAIN"
    PROVE  Spec => []ObserversConsultAndReport
<1>1. (Inv /\ ObserversConsultAndReport) /\ [Next]_vars => (Inv /\ ObserversConsultAndReport)'
    BY NextInv, NextObservers
<1>2. Init => Inv /\ ObserversConsultAndReport
    BY InitInv, InitAll
<1> QED
    BY <1>1, <1>2, PTL DEF Spec

THEOREM NoNameCrossesDomainsAlways ==
    ASSUME Mut # "M_DOMAIN"
    PROVE  Spec => []NoNameCrossesDomains
<1>1. (Inv /\ NoNameCrossesDomains) /\ [Next]_vars => (Inv /\ NoNameCrossesDomains)'
    BY NextInv, NextDomains
<1>2. Init => Inv /\ NoNameCrossesDomains
    BY InitInv, InitAll
<1> QED
    BY <1>1, <1>2, PTL DEF Spec

THEOREM SafeAlways ==
    ASSUME Mut = "none"
    PROVE  Spec => []Safe
<1>1. Spec => []OnlyThinkersActuate
    BY OnlyThinkersActuateAlways
<1>2. Spec => []ObserversConsultAndReport
    BY ObserversConsultAndReportAlways
<1>3. Spec => []NoNameCrossesDomains
    BY NoNameCrossesDomainsAlways
<1> QED
    BY <1>1, <1>2, <1>3, PTL DEF Safe

-----------------------------------------------------------------------------
(* Why the mutations must fail. M_KIND grants a run observer Actuate; M_DOMAIN   *)
(* grants a build seat the run acts. The counterexamples are TLC's.              *)
LEMMA MutKindObserverActuates ==
    ASSUME Mut = "M_KIND"
    PROVE  "Actuate" \in ByKind("ro") \cap ByDomain("ro")
BY DEF ByKind, ByDomain, DomainOf, DomainActs, Acts, RunActs

LEMMA MutDomainCrosses ==
    ASSUME Mut = "M_DOMAIN"
    PROVE  "Actuate" \in ByKind("bt") \cap ByDomain("bt")
BY DEF ByKind, ByDomain, KindOf, KindBound, Acts, RunActs

=============================================================================
