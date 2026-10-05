--------------------------- MODULE Emergency_proof ---------------------------
(* TLAPS proofs of the six invariants Emergency.tla states (ADR-0052, Proposed:  *)
(* break-glass as an emergency seating), for every round bound:                  *)
(*                                                                               *)
(*   EmergencyLeaseHasARosterQuorumAlways  (Mut \notin {"M_NOQUORUM", "M_REGRANT"}) *)
(*   EmergencyLeaseIsOneRoundAlways        (Mut \notin {"M_REGRANT", "M_RENEW"}) *)
(*   NoAgentHoldsAnEmergencySeatAlways     (Mut # "M_AGENT")                     *)
(*   CallsAreAllowlistedAlways             (Mut # "M_X1")                        *)
(*   ThinkerStillCoupledAlways             (Mut # "M_UNCOUPLE")                  *)
(*   ActivationIsForensicAlways            (Mut \notin {"M_REGRANT", "M_ERASE"}) *)
(*   SafeAlways == Spec => []Safe          (Mut = "none")                        *)
(*                                                                               *)
(* Each theorem takes as hypothesis only the mutations that break it, which is   *)
(* the full table TLC ran: seven mutations against six properties                *)
(* (Emergency-results-2026.10.04.txt). Five properties are inductive as stated,  *)
(* with a type invariant for the lease record. NoAgentHoldsAnEmergencySeat is    *)
(* proved from a statement over every lease the seat has had, since an           *)
(* operator's regrant, where a mutation allows one, revives a lease whose holder *)
(* the property as stated says nothing about. Nothing is assumed of MaxRound.    *)
(*                                                                               *)
(* Emergency.tla is not edited; this module extends it. The mutations and the    *)
(* witnesses stay with TLC; the lemmas at the end say what each mutation admits. *)
(*                                                                               *)
(* Check with:  ../tools/tlapm Emergency_proof.tla   (from spec/; see            *)
(*              proof-results.sh and proof-cert.sh for the results files)        *)
EXTENDS Emergency, TLAPS

EmType == [live : BOOLEAN, round : Nat, holder : Holders \cup {"none"}, envelope : SUBSET Tools,
           quorate : BOOLEAN, by : {"none", "roster", "operator"}, renewed : BOOLEAN]

TypeOK == em \in EmType /\ domainTools \subseteq Domain

\* Every holder the seat has had is a person: the property over every lease and not only a live one.
HolderIsPerson == em.round > 0 => em.holder \in Persons

LEMMA TypeInit == Init => TypeOK
BY DEF Init, TypeOK, EmType, NoEm, Domain

LEMMA TypeNext == ASSUME TypeOK, [Next]_vars PROVE TypeOK'
<1>1. CASE UNCHANGED vars
    BY <1>1 DEF vars, TypeOK
<1>2. ASSUME NEW t \in Domain, Promote(t) PROVE TypeOK'
    BY <1>2 DEF Promote, TypeOK
<1>3. ASSUME NEW r \in Roster, Approve(r) PROVE TypeOK'
    BY <1>3 DEF Approve, TypeOK
<1>4. ASSUME NEW h \in Holders, Activate(h) PROVE TypeOK'
    <2>1. Quorate(approvals) \in BOOLEAN
        BY DEF Quorate
    <2>2. domainTools \cup {"te"} \in SUBSET Tools
        BY DEF TypeOK, Tools
    <2> QED
        BY <1>4, <2>1, <2>2 DEF Activate, TypeOK, EmType, Holders, Persons, Agents
<1>5. CASE EndEm
    BY <1>5 DEF EndEm, TypeOK, EmType
<1>6. CASE Regrant
    BY <1>6 DEF Regrant, TypeOK, EmType
<1>7. CASE Renew
    BY <1>7 DEF Renew, TypeOK, EmType
<1>8. CASE ObsToggle
    BY <1>8 DEF ObsToggle, TypeOK
<1>9. ASSUME NEW t \in Tools, EmCall(t) \/ ThinkerCall(t) PROVE TypeOK'
    BY <1>9 DEF EmCall, ThinkerCall, TypeOK
<1>10. ASSUME NEW x \in records, Erase(x) PROVE TypeOK'
    BY <1>10 DEF Erase, TypeOK
<1> QED
    BY <1>1, <1>2, <1>3, <1>4, <1>5, <1>6, <1>7, <1>8, <1>9, <1>10 DEF Next

THEOREM TypeAlways == Spec => []TypeOK
<1>1. TypeOK /\ [Next]_vars => TypeOK'
    BY TypeNext
<1> QED
    BY <1>1, TypeInit, PTL DEF Spec

\* A live lease has had a round.
LiveHasRound == em.live => em.round > 0

LEMMA LiveHasRoundNext == ASSUME TypeOK, LiveHasRound, [Next]_vars PROVE LiveHasRound'
<1> USE DEF LiveHasRound
<1>1. CASE UNCHANGED vars
    BY <1>1 DEF vars
<1>2. ASSUME NEW t \in Domain, Promote(t) PROVE LiveHasRound'
    BY <1>2 DEF Promote
<1>3. ASSUME NEW r \in Roster, Approve(r) PROVE LiveHasRound'
    BY <1>3 DEF Approve
<1>4. ASSUME NEW h \in Holders, Activate(h) PROVE LiveHasRound'
    BY <1>4 DEF Activate, TypeOK, EmType
<1>5. CASE EndEm
    BY <1>5 DEF EndEm, TypeOK, EmType
<1>6. CASE Regrant
    BY <1>6 DEF Regrant, TypeOK, EmType
<1>7. CASE Renew
    BY <1>7 DEF Renew, TypeOK, EmType
<1>8. CASE ObsToggle
    BY <1>8 DEF ObsToggle
<1>9. ASSUME NEW t \in Tools, EmCall(t) \/ ThinkerCall(t) PROVE LiveHasRound'
    BY <1>9 DEF EmCall, ThinkerCall
<1>10. ASSUME NEW x \in records, Erase(x) PROVE LiveHasRound'
    BY <1>10 DEF Erase
<1> QED
    BY <1>1, <1>2, <1>3, <1>4, <1>5, <1>6, <1>7, <1>8, <1>9, <1>10 DEF Next

THEOREM LiveHasRoundAlways == Spec => []LiveHasRound
<1>1. Init => LiveHasRound
    BY DEF Init, LiveHasRound, NoEm
<1>2. TypeOK /\ LiveHasRound /\ [Next]_vars => LiveHasRound'
    BY LiveHasRoundNext
<1>3. Spec => []TypeOK
    BY TypeAlways
<1> QED
    BY <1>1, <1>2, <1>3, PTL DEF Spec

-----------------------------------------------------------------------------
(* Each property is inductive, as stated or, for the holder, over every lease    *)
(* the seat has had: one lemma each, action by action.                           *)

LEMMA EmergencyLeaseHasARosterQuorumNext ==
    ASSUME Mut \notin {"M_NOQUORUM", "M_REGRANT"}, TypeOK, EmergencyLeaseHasARosterQuorum, [Next]_vars
    PROVE  EmergencyLeaseHasARosterQuorum'
<1> USE DEF EmergencyLeaseHasARosterQuorum
<1>1. CASE UNCHANGED vars
    BY <1>1 DEF vars
<1>2. ASSUME NEW t \in Domain, Promote(t) PROVE EmergencyLeaseHasARosterQuorum'
    BY <1>2 DEF Promote
<1>3. ASSUME NEW r \in Roster, Approve(r) PROVE EmergencyLeaseHasARosterQuorum'
    BY <1>3 DEF Approve
<1>4. ASSUME NEW h \in Holders, Activate(h) PROVE EmergencyLeaseHasARosterQuorum'
    BY <1>4 DEF Activate, TypeOK, EmType
<1>5. CASE EndEm
    BY <1>5 DEF EndEm, TypeOK, EmType
<1>6. CASE Regrant
    BY <1>6 DEF Regrant, TypeOK, EmType
<1>7. CASE Renew
    BY <1>7 DEF Renew, TypeOK, EmType
<1>8. CASE ObsToggle
    BY <1>8 DEF ObsToggle
<1>9. ASSUME NEW t \in Tools, EmCall(t) \/ ThinkerCall(t) PROVE EmergencyLeaseHasARosterQuorum'
    BY <1>9 DEF EmCall, ThinkerCall, X1
<1>10. ASSUME NEW x \in records, Erase(x) PROVE EmergencyLeaseHasARosterQuorum'
    BY <1>10 DEF Erase
<1> QED
    BY <1>1, <1>2, <1>3, <1>4, <1>5, <1>6, <1>7, <1>8, <1>9, <1>10 DEF Next

LEMMA EmergencyLeaseIsOneRoundNext ==
    ASSUME Mut \notin {"M_REGRANT", "M_RENEW"}, TypeOK, EmergencyLeaseIsOneRound, [Next]_vars
    PROVE  EmergencyLeaseIsOneRound'
<1> USE DEF EmergencyLeaseIsOneRound
<1>1. CASE UNCHANGED vars
    BY <1>1 DEF vars
<1>2. ASSUME NEW t \in Domain, Promote(t) PROVE EmergencyLeaseIsOneRound'
    BY <1>2 DEF Promote
<1>3. ASSUME NEW r \in Roster, Approve(r) PROVE EmergencyLeaseIsOneRound'
    BY <1>3 DEF Approve
<1>4. ASSUME NEW h \in Holders, Activate(h) PROVE EmergencyLeaseIsOneRound'
    BY <1>4 DEF Activate, TypeOK, EmType
<1>5. CASE EndEm
    BY <1>5 DEF EndEm, TypeOK, EmType
<1>6. CASE Regrant
    BY <1>6 DEF Regrant, TypeOK, EmType
<1>7. CASE Renew
    BY <1>7 DEF Renew, TypeOK, EmType
<1>8. CASE ObsToggle
    BY <1>8 DEF ObsToggle
<1>9. ASSUME NEW t \in Tools, EmCall(t) \/ ThinkerCall(t) PROVE EmergencyLeaseIsOneRound'
    BY <1>9 DEF EmCall, ThinkerCall, X1
<1>10. ASSUME NEW x \in records, Erase(x) PROVE EmergencyLeaseIsOneRound'
    BY <1>10 DEF Erase
<1> QED
    BY <1>1, <1>2, <1>3, <1>4, <1>5, <1>6, <1>7, <1>8, <1>9, <1>10 DEF Next

LEMMA HolderIsPersonNext ==
    ASSUME Mut # "M_AGENT", TypeOK, HolderIsPerson, [Next]_vars
    PROVE  HolderIsPerson'
<1> USE DEF HolderIsPerson
<1>1. CASE UNCHANGED vars
    BY <1>1 DEF vars
<1>2. ASSUME NEW t \in Domain, Promote(t) PROVE HolderIsPerson'
    BY <1>2 DEF Promote
<1>3. ASSUME NEW r \in Roster, Approve(r) PROVE HolderIsPerson'
    BY <1>3 DEF Approve
<1>4. ASSUME NEW h \in Holders, Activate(h) PROVE HolderIsPerson'
    BY <1>4 DEF Activate, TypeOK, EmType
<1>5. CASE EndEm
    BY <1>5 DEF EndEm, TypeOK, EmType
<1>6. CASE Regrant
    BY <1>6 DEF Regrant, TypeOK, EmType
<1>7. CASE Renew
    BY <1>7 DEF Renew, TypeOK, EmType
<1>8. CASE ObsToggle
    BY <1>8 DEF ObsToggle
<1>9. ASSUME NEW t \in Tools, EmCall(t) \/ ThinkerCall(t) PROVE HolderIsPerson'
    BY <1>9 DEF EmCall, ThinkerCall, X1
<1>10. ASSUME NEW x \in records, Erase(x) PROVE HolderIsPerson'
    BY <1>10 DEF Erase
<1> QED
    BY <1>1, <1>2, <1>3, <1>4, <1>5, <1>6, <1>7, <1>8, <1>9, <1>10 DEF Next

LEMMA CallsAreAllowlistedNext ==
    ASSUME Mut # "M_X1", TypeOK, CallsAreAllowlisted, [Next]_vars
    PROVE  CallsAreAllowlisted'
<1> USE DEF CallsAreAllowlisted
<1>1. CASE UNCHANGED vars
    BY <1>1 DEF vars
<1>2. ASSUME NEW t \in Domain, Promote(t) PROVE CallsAreAllowlisted'
    BY <1>2 DEF Promote
<1>3. ASSUME NEW r \in Roster, Approve(r) PROVE CallsAreAllowlisted'
    BY <1>3 DEF Approve
<1>4. ASSUME NEW h \in Holders, Activate(h) PROVE CallsAreAllowlisted'
    BY <1>4 DEF Activate, TypeOK, EmType
<1>5. CASE EndEm
    BY <1>5 DEF EndEm, TypeOK, EmType
<1>6. CASE Regrant
    BY <1>6 DEF Regrant, TypeOK, EmType
<1>7. CASE Renew
    BY <1>7 DEF Renew, TypeOK, EmType
<1>8. CASE ObsToggle
    BY <1>8 DEF ObsToggle
<1>9. ASSUME NEW t \in Tools, EmCall(t) \/ ThinkerCall(t) PROVE CallsAreAllowlisted'
    BY <1>9 DEF EmCall, ThinkerCall, X1
<1>10. ASSUME NEW x \in records, Erase(x) PROVE CallsAreAllowlisted'
    BY <1>10 DEF Erase
<1> QED
    BY <1>1, <1>2, <1>3, <1>4, <1>5, <1>6, <1>7, <1>8, <1>9, <1>10 DEF Next

LEMMA ThinkerStillCoupledNext ==
    ASSUME Mut # "M_UNCOUPLE", TypeOK, ThinkerStillCoupled, [Next]_vars
    PROVE  ThinkerStillCoupled'
<1> USE DEF ThinkerStillCoupled
<1>1. CASE UNCHANGED vars
    BY <1>1 DEF vars
<1>2. ASSUME NEW t \in Domain, Promote(t) PROVE ThinkerStillCoupled'
    BY <1>2 DEF Promote
<1>3. ASSUME NEW r \in Roster, Approve(r) PROVE ThinkerStillCoupled'
    BY <1>3 DEF Approve
<1>4. ASSUME NEW h \in Holders, Activate(h) PROVE ThinkerStillCoupled'
    BY <1>4 DEF Activate, TypeOK, EmType
<1>5. CASE EndEm
    BY <1>5 DEF EndEm, TypeOK, EmType
<1>6. CASE Regrant
    BY <1>6 DEF Regrant, TypeOK, EmType
<1>7. CASE Renew
    BY <1>7 DEF Renew, TypeOK, EmType
<1>8. CASE ObsToggle
    BY <1>8 DEF ObsToggle
<1>9. ASSUME NEW t \in Tools, EmCall(t) \/ ThinkerCall(t) PROVE ThinkerStillCoupled'
    BY <1>9 DEF EmCall, ThinkerCall, X1
<1>10. ASSUME NEW x \in records, Erase(x) PROVE ThinkerStillCoupled'
    BY <1>10 DEF Erase
<1> QED
    BY <1>1, <1>2, <1>3, <1>4, <1>5, <1>6, <1>7, <1>8, <1>9, <1>10 DEF Next

LEMMA ActivationIsForensicNext ==
    ASSUME Mut \notin {"M_REGRANT", "M_ERASE"}, TypeOK, ActivationIsForensic, [Next]_vars
    PROVE  ActivationIsForensic'
<1> USE DEF ActivationIsForensic
<1>1. CASE UNCHANGED vars
    BY <1>1 DEF vars
<1>2. ASSUME NEW t \in Domain, Promote(t) PROVE ActivationIsForensic'
    BY <1>2 DEF Promote
<1>3. ASSUME NEW r \in Roster, Approve(r) PROVE ActivationIsForensic'
    BY <1>3 DEF Approve
<1>4. ASSUME NEW h \in Holders, Activate(h) PROVE ActivationIsForensic'
    <2>1. em.round \in Nat /\ em'.round = em.round + 1
        BY <1>4 DEF Activate, TypeOK, EmType
    <2>2. records' = records \cup {[round |-> em.round + 1, holder |-> h, approvers |-> approvals]}
        BY <1>4 DEF Activate
    <2>3. ASSUME NEW n \in 1..(em.round + 1) PROVE \E x \in records' : x.round = n
        <3>1. CASE n \in 1..em.round
            BY <3>1, <2>2
        <3>2. CASE n = em.round + 1
            BY <3>2, <2>2
        <3> QED
            BY <3>1, <3>2, <2>1
    <2> QED
        BY <2>1, <2>3
<1>5. CASE EndEm
    BY <1>5 DEF EndEm, TypeOK, EmType
<1>6. CASE Regrant
    BY <1>6 DEF Regrant, TypeOK, EmType
<1>7. CASE Renew
    BY <1>7 DEF Renew, TypeOK, EmType
<1>8. CASE ObsToggle
    BY <1>8 DEF ObsToggle
<1>9. ASSUME NEW t \in Tools, EmCall(t) \/ ThinkerCall(t) PROVE ActivationIsForensic'
    BY <1>9 DEF EmCall, ThinkerCall, X1
<1>10. ASSUME NEW x \in records, Erase(x) PROVE ActivationIsForensic'
    BY <1>10 DEF Erase
<1> QED
    BY <1>1, <1>2, <1>3, <1>4, <1>5, <1>6, <1>7, <1>8, <1>9, <1>10 DEF Next

-----------------------------------------------------------------------------
THEOREM EmergencyLeaseHasARosterQuorumAlways ==
    ASSUME Mut \notin {"M_NOQUORUM", "M_REGRANT"}
    PROVE  Spec => []EmergencyLeaseHasARosterQuorum
<1>1. Init => EmergencyLeaseHasARosterQuorum
    BY DEF Init, EmergencyLeaseHasARosterQuorum, NoEm
<1>2. TypeOK /\ EmergencyLeaseHasARosterQuorum /\ [Next]_vars => EmergencyLeaseHasARosterQuorum'
    BY EmergencyLeaseHasARosterQuorumNext
<1>3. Spec => []TypeOK
    BY TypeAlways
<1> QED
    BY <1>1, <1>2, <1>3, PTL DEF Spec

THEOREM EmergencyLeaseIsOneRoundAlways ==
    ASSUME Mut \notin {"M_REGRANT", "M_RENEW"}
    PROVE  Spec => []EmergencyLeaseIsOneRound
<1>1. Init => EmergencyLeaseIsOneRound
    BY DEF Init, EmergencyLeaseIsOneRound, NoEm
<1>2. TypeOK /\ EmergencyLeaseIsOneRound /\ [Next]_vars => EmergencyLeaseIsOneRound'
    BY EmergencyLeaseIsOneRoundNext
<1>3. Spec => []TypeOK
    BY TypeAlways
<1> QED
    BY <1>1, <1>2, <1>3, PTL DEF Spec

THEOREM NoAgentHoldsAnEmergencySeatAlways ==
    ASSUME Mut # "M_AGENT"
    PROVE  Spec => []NoAgentHoldsAnEmergencySeat
<1>1. Init => HolderIsPerson
    BY DEF Init, HolderIsPerson, NoEm
<1>2. TypeOK /\ HolderIsPerson /\ [Next]_vars => HolderIsPerson'
    BY HolderIsPersonNext
<1>3. Spec => []TypeOK
    BY TypeAlways
<1>4. TypeOK /\ LiveHasRound /\ HolderIsPerson => NoAgentHoldsAnEmergencySeat
    BY DEF TypeOK, EmType, LiveHasRound, HolderIsPerson, NoAgentHoldsAnEmergencySeat
<1>5. Spec => []LiveHasRound
    BY LiveHasRoundAlways
<1> QED
    BY <1>1, <1>2, <1>3, <1>4, <1>5, PTL DEF Spec

THEOREM CallsAreAllowlistedAlways ==
    ASSUME Mut # "M_X1"
    PROVE  Spec => []CallsAreAllowlisted
<1>1. Init => CallsAreAllowlisted
    BY DEF Init, CallsAreAllowlisted, NoEm
<1>2. TypeOK /\ CallsAreAllowlisted /\ [Next]_vars => CallsAreAllowlisted'
    BY CallsAreAllowlistedNext
<1>3. Spec => []TypeOK
    BY TypeAlways
<1> QED
    BY <1>1, <1>2, <1>3, PTL DEF Spec

THEOREM ThinkerStillCoupledAlways ==
    ASSUME Mut # "M_UNCOUPLE"
    PROVE  Spec => []ThinkerStillCoupled
<1>1. Init => ThinkerStillCoupled
    BY DEF Init, ThinkerStillCoupled, NoEm
<1>2. TypeOK /\ ThinkerStillCoupled /\ [Next]_vars => ThinkerStillCoupled'
    BY ThinkerStillCoupledNext
<1>3. Spec => []TypeOK
    BY TypeAlways
<1> QED
    BY <1>1, <1>2, <1>3, PTL DEF Spec

THEOREM ActivationIsForensicAlways ==
    ASSUME Mut \notin {"M_REGRANT", "M_ERASE"}
    PROVE  Spec => []ActivationIsForensic
<1>1. Init => ActivationIsForensic
    BY DEF Init, ActivationIsForensic, NoEm
<1>2. TypeOK /\ ActivationIsForensic /\ [Next]_vars => ActivationIsForensic'
    BY ActivationIsForensicNext
<1>3. Spec => []TypeOK
    BY TypeAlways
<1> QED
    BY <1>1, <1>2, <1>3, PTL DEF Spec

THEOREM SafeAlways ==
    ASSUME Mut = "none"
    PROVE  Spec => []Safe
<1>1. Spec => []EmergencyLeaseHasARosterQuorum
    BY EmergencyLeaseHasARosterQuorumAlways
<1>2. Spec => []EmergencyLeaseIsOneRound
    BY EmergencyLeaseIsOneRoundAlways
<1>3. Spec => []NoAgentHoldsAnEmergencySeat
    BY NoAgentHoldsAnEmergencySeatAlways
<1>4. Spec => []CallsAreAllowlisted
    BY CallsAreAllowlistedAlways
<1>5. Spec => []ThinkerStillCoupled
    BY ThinkerStillCoupledAlways
<1>6. Spec => []ActivationIsForensic
    BY ActivationIsForensicAlways
<1> QED
    BY <1>1, <1>2, <1>3, <1>4, <1>5, <1>6, PTL DEF Safe

-----------------------------------------------------------------------------
(* What each mutation admits: the guard it removes. Their counterexamples are    *)
(* TLC's (Emergency-results-2026.10.04.txt).                                     *)

LEMMA MutX1AdmitsAnything == (Mut = "M_X1" /\ Quorate(approvals)) => X1
BY DEF X1

LEMMA NoneHasNoException == Mut # "M_X1" => ~X1
BY DEF X1

LEMMA NoneNeverContinues == Mut \notin {"M_REGRANT", "M_RENEW"} => ~Regrant /\ ~Renew
BY DEF Regrant, Renew

LEMMA NoneNeverErases == Mut # "M_ERASE" => \A x \in records : ~Erase(x)
BY DEF Erase

(* That an emergency call is admitted with no live Observer is a behaviour, and  *)
(* is TLC's witness w3. An ENABLED lemma for it was dropped: only Zenon proved   *)
(* it, and Isabelle could not check Zenon's script, so it could not be           *)
(* certified. No theorem used it.                                                *)
=============================================================================
