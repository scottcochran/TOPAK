------------------------ MODULE Emergency_live_proof ------------------------
(* TLAPS proofs for Emergency_live.tla (ADR-0039 A2; ADR-0052, provisional): the *)
(* emergency call does not wait on an Observer, as two invariants over ENABLED,  *)
(* and Emergency.tla's invariants for the module's own Next. For every round     *)
(* bound:                                                                        *)
(*                                                                               *)
(*   EmergencyNeverCoupledAlways          (Mut \notin {"M_EMCOUPLE", "M_EMCOUPLE2"}) *)
(*   EmergencyCallsWithoutObserverAlways  (Mut \notin {"M_EMCOUPLE", "M_EMCOUPLE2"}) *)
(*   SpecLImpliesSpec == SpecL => Spec    (every Mut)                            *)
(*   TypeAlwaysL, LiveHasRoundAlwaysL     (every Mut)                            *)
(*   EnvelopeHasTeAlways, EnvelopeHasTeAlwaysL   (every Mut)                     *)
(*   the six invariants of Emergency_proof.tla for SpecL, each under the         *)
(*   hypothesis it has there                                                     *)
(*   SafeAlwaysL == SpecL => []Safe       (Mut \in {"none", "M_EMCOUPLE", "M_EMCOUPLE2"}) *)
(*                                                                               *)
(* EmergencyNeverCoupled holds in every state under its hypothesis: with no      *)
(* coupling, the admit asks only that the seat is live and the tool is in its    *)
(* envelope. It is a state lemma lifted by PTL, as ConsultNeverCoupled is in     *)
(* RunCoupling_proof. EmergencyCallsWithoutObserver needs one fact of the        *)
(* reachable states, that te is in every envelope the seat has had               *)
(* (EnvelopeHasTe, inductive under every Mut), with Emergency_proof's            *)
(* LiveHasRound. te is this proof's witness, not what the property rests on: t1  *)
(* would serve as well (Emergency_live.tla's header). The hypothesis of both is  *)
(* the module's two mutations, which break both (Emergency_live.tla's header);   *)
(* Emergency's own seven break neither.                                          *)
(*                                                                               *)
(* Every NextL step is a Next step of Emergency.tla, under every Mut. EmAdmit is *)
(* EmCall's admit. EmRefuse is EmCall's refusal when the tool is outside the     *)
(* envelope and X1 does not hold. Otherwise the call is refused for the          *)
(* coupling: EmCoupled holds and the Observer is not live, so Mut is one of the  *)
(* two mutations, X1 is false and R3 is in force for the Thinker, and the step   *)
(* is ThinkerCall's refusal of the same tool. So SpecL => Spec, and every        *)
(* invariant Emergency_proof proves of Spec holds of SpecL under the same        *)
(* hypothesis. Under Emergency's own mutations NextL is Next exactly             *)
(* (NextIsNextL), so the two specifications are the same.                        *)
(*                                                                               *)
(* Emergency_proof.tla records that an ENABLED lemma for the unobserved          *)
(* emergency call was dropped: only Zenon proved it, and Isabelle could not      *)
(* check Zenon's script. Both failures come from the call record the admit       *)
(* writes to calls'. tlapm encodes a set equality in a goal through an           *)
(* extensionality trigger, so cvc5 cannot eliminate calls' = {...} and has no    *)
(* term to instantiate calls' with. Zenon instantiates it with the record's      *)
(* allowlisted field rewritten to TRUE, and its script leaves the equality of    *)
(* the two records unproved (a sorry), which Isabelle refuses. Here Isabelle     *)
(* proves each property in one step from its expansion (ExpandENABLED, Isa),     *)
(* and that certifies.                                                           *)
(*                                                                               *)
(* Why one step each. tlapm 7824dab hands an unexpanded ENABLED term to its      *)
(* backends as an opaque constant, and under a binder the constant does not      *)
(* depend on the bound variable: it proves (\E t \in Tools : ENABLED EmAdmit(t)) *)
(* => (\A t \in Tools : ENABLED EmAdmit(t)), which is false, and ethos accepts   *)
(* cvc5's proof of the query. A lemma for one tool, which cvc5 does prove when   *)
(* the record is named beside the goal, reaches the properties' \A and \E over  *)
(* tools only through such a step. So no backend sees an unexpanded ENABLED      *)
(* here: each ENABLED goal is expanded in the one step that proves it, and       *)
(* elsewhere the two properties appear only by name.                             *)
(*                                                                               *)
(* Emergency.tla, Emergency_live.tla and Emergency_proof.tla are not edited;     *)
(* this module extends the last two. The mutations stay with TLC                 *)
(* (Emergency_live-results-2026.10.07.txt); the lemmas at the end say what each  *)
(* of the two adds.                                                              *)
(*                                                                               *)
(* Check with:  ../tools/tlapm Emergency_live_proof.tla   (from spec/; see       *)
(*              proof-results.sh and proof-cert.sh for the results files)        *)
EXTENDS Emergency_live, Emergency_proof, TLAPS

-----------------------------------------------------------------------------
(* Every NextL step is a Next step, under every Mut.                             *)

LEMMA EmAdmitIsEmCall ==
    ASSUME NEW t, EmAdmit(t)
    PROVE  EmCall(t)
BY DEF EmAdmit, EmCall

(* Refused outside the envelope, as EmCall refuses.                              *)
LEMMA EmRefuseIsEmCall ==
    ASSUME NEW t, EmRefuse(t), ~(t \in em.envelope \/ X1)
    PROVE  EmCall(t)
BY DEF EmRefuse, EmCall

(* Refused for the coupling: the Thinker's refusal of the same tool, since the   *)
(* Observer is not live and R3 is in force.                                      *)
LEMMA EmRefuseIsThinkerCall ==
    ASSUME NEW t, EmRefuse(t), t \in em.envelope \/ X1
    PROVE  ThinkerCall(t)
<1>1. EmCoupled /\ ~obsLive
    BY DEF EmRefuse
<1>2. Mut # "M_X1" /\ Mut # "M_UNCOUPLE"
    BY <1>1 DEF EmCoupled
<1>3. ~X1
    BY <1>2 DEF X1
<1> QED
    BY <1>1, <1>2, <1>3 DEF EmRefuse, ThinkerCall

LEMMA NextLIsNext == NextL => Next
<1> SUFFICES ASSUME NextL PROVE Next
    OBVIOUS
<1>1. CASE \E t \in Tools : EmAdmit(t) \/ EmRefuse(t) \/ ThinkerCall(t)
    <2> PICK t \in Tools : EmAdmit(t) \/ EmRefuse(t) \/ ThinkerCall(t)
        BY <1>1
    <2>1. EmCall(t) \/ ThinkerCall(t)
        BY EmAdmitIsEmCall, EmRefuseIsEmCall, EmRefuseIsThinkerCall
    <2> QED
        BY <2>1 DEF Next
<1>2. CASE ~\E t \in Tools : EmAdmit(t) \/ EmRefuse(t) \/ ThinkerCall(t)
    BY <1>2 DEF NextL, Next
<1> QED
    BY <1>1, <1>2

(* Under Emergency's own mutations the converse holds: NextL is Next.           *)
LEMMA EmCallSplits ==
    ASSUME Mut \notin {"M_EMCOUPLE", "M_EMCOUPLE2"}, NEW t, EmCall(t)
    PROVE  EmAdmit(t) \/ EmRefuse(t)
BY DEF EmCall, EmAdmit, EmRefuse, EmCoupled

LEMMA NextIsNextL ==
    ASSUME Mut \notin {"M_EMCOUPLE", "M_EMCOUPLE2"}
    PROVE  Next <=> NextL
<1>1. Next => NextL
    <2> SUFFICES ASSUME Next PROVE NextL
        OBVIOUS
    <2>1. CASE \E t \in Tools : EmCall(t) \/ ThinkerCall(t)
        <3> PICK t \in Tools : EmCall(t) \/ ThinkerCall(t)
            BY <2>1
        <3>1. EmAdmit(t) \/ EmRefuse(t) \/ ThinkerCall(t)
            BY EmCallSplits
        <3> QED
            BY <3>1 DEF NextL
    <2>2. CASE ~\E t \in Tools : EmCall(t) \/ ThinkerCall(t)
        BY <2>2 DEF NextL, Next
    <2> QED
        BY <2>1, <2>2
<1> QED
    BY <1>1, NextLIsNext

THEOREM SpecLImpliesSpec == SpecL => Spec
<1>1. [NextL]_vars => [Next]_vars
    BY NextLIsNext
<1> QED
    BY <1>1, PTL DEF SpecL, Spec

-----------------------------------------------------------------------------
(* Emergency_proof's theorems, for SpecL.                                       *)

THEOREM TypeAlwaysL == SpecL => []TypeOK
BY SpecLImpliesSpec, TypeAlways

THEOREM LiveHasRoundAlwaysL == SpecL => []LiveHasRound
BY SpecLImpliesSpec, LiveHasRoundAlways

THEOREM EmergencyLeaseHasARosterQuorumAlwaysL ==
    ASSUME Mut \notin {"M_NOQUORUM", "M_REGRANT"}
    PROVE  SpecL => []EmergencyLeaseHasARosterQuorum
BY SpecLImpliesSpec, EmergencyLeaseHasARosterQuorumAlways

THEOREM EmergencyLeaseIsOneRoundAlwaysL ==
    ASSUME Mut \notin {"M_REGRANT", "M_RENEW"}
    PROVE  SpecL => []EmergencyLeaseIsOneRound
BY SpecLImpliesSpec, EmergencyLeaseIsOneRoundAlways

THEOREM NoAgentHoldsAnEmergencySeatAlwaysL ==
    ASSUME Mut # "M_AGENT"
    PROVE  SpecL => []NoAgentHoldsAnEmergencySeat
BY SpecLImpliesSpec, NoAgentHoldsAnEmergencySeatAlways

THEOREM CallsAreAllowlistedAlwaysL ==
    ASSUME Mut # "M_X1"
    PROVE  SpecL => []CallsAreAllowlisted
BY SpecLImpliesSpec, CallsAreAllowlistedAlways

THEOREM ThinkerStillCoupledAlwaysL ==
    ASSUME Mut # "M_UNCOUPLE"
    PROVE  SpecL => []ThinkerStillCoupled
BY SpecLImpliesSpec, ThinkerStillCoupledAlways

THEOREM ActivationIsForensicAlwaysL ==
    ASSUME Mut \notin {"M_REGRANT", "M_ERASE"}
    PROVE  SpecL => []ActivationIsForensic
BY SpecLImpliesSpec, ActivationIsForensicAlways

(* The two mutations break none of the six.                                      *)
THEOREM SafeAlwaysL ==
    ASSUME Mut \in {"none", "M_EMCOUPLE", "M_EMCOUPLE2"}
    PROVE  SpecL => []Safe
<1>1. SpecL => []EmergencyLeaseHasARosterQuorum
    BY EmergencyLeaseHasARosterQuorumAlwaysL
<1>2. SpecL => []EmergencyLeaseIsOneRound
    BY EmergencyLeaseIsOneRoundAlwaysL
<1>3. SpecL => []NoAgentHoldsAnEmergencySeat
    BY NoAgentHoldsAnEmergencySeatAlwaysL
<1>4. SpecL => []CallsAreAllowlisted
    BY CallsAreAllowlistedAlwaysL
<1>5. SpecL => []ThinkerStillCoupled
    BY ThinkerStillCoupledAlwaysL
<1>6. SpecL => []ActivationIsForensic
    BY ActivationIsForensicAlwaysL
<1> QED
    BY <1>1, <1>2, <1>3, <1>4, <1>5, <1>6, PTL DEF Safe

-----------------------------------------------------------------------------
(* EmergencyNeverCoupled: valid in every state under its hypothesis. It and      *)
(* EmergencyCallsWithoutObserverHolds below are each proved in one step from     *)
(* their expansion, by Isabelle, so that no backend sees an unexpanded ENABLED   *)
(* under a binder (header).                                                      *)

LEMMA EmergencyNeverCoupledValid ==
    ASSUME Mut \notin {"M_EMCOUPLE", "M_EMCOUPLE2"}
    PROVE  EmergencyNeverCoupled
BY ExpandENABLED, Isa DEF EmergencyNeverCoupled, EmAdmit, EmCoupled

THEOREM EmergencyNeverCoupledAlways ==
    ASSUME Mut \notin {"M_EMCOUPLE", "M_EMCOUPLE2"}
    PROVE  SpecL => []EmergencyNeverCoupled
<1>1. EmergencyNeverCoupled
    BY EmergencyNeverCoupledValid
<1> QED
    BY <1>1, PTL

-----------------------------------------------------------------------------
(* EmergencyCallsWithoutObserver: te is in every envelope the seat has had.     *)

EnvelopeHasTe == em.round > 0 => "te" \in em.envelope

LEMMA EnvelopeHasTeNext == ASSUME TypeOK, EnvelopeHasTe, [Next]_vars PROVE EnvelopeHasTe'
<1> USE DEF EnvelopeHasTe
<1>1. CASE UNCHANGED vars
    BY <1>1 DEF vars
<1>2. ASSUME NEW t \in Domain, Promote(t) PROVE EnvelopeHasTe'
    BY <1>2 DEF Promote
<1>3. ASSUME NEW r \in Roster, Approve(r) PROVE EnvelopeHasTe'
    BY <1>3 DEF Approve
<1>4. ASSUME NEW h \in Holders, Activate(h) PROVE EnvelopeHasTe'
    BY <1>4 DEF Activate
<1>5. CASE EndEm
    BY <1>5 DEF EndEm, TypeOK, EmType
<1>6. CASE Regrant
    BY <1>6 DEF Regrant, TypeOK, EmType
<1>7. CASE Renew
    BY <1>7 DEF Renew, TypeOK, EmType
<1>8. CASE ObsToggle
    BY <1>8 DEF ObsToggle
<1>9. ASSUME NEW t \in Tools, EmCall(t) \/ ThinkerCall(t) PROVE EnvelopeHasTe'
    BY <1>9 DEF EmCall, ThinkerCall
<1>10. ASSUME NEW x \in records, Erase(x) PROVE EnvelopeHasTe'
    BY <1>10 DEF Erase
<1> QED
    BY <1>1, <1>2, <1>3, <1>4, <1>5, <1>6, <1>7, <1>8, <1>9, <1>10 DEF Next

THEOREM EnvelopeHasTeAlways == Spec => []EnvelopeHasTe
<1>1. Init => EnvelopeHasTe
    BY DEF Init, EnvelopeHasTe, NoEm
<1>2. TypeOK /\ EnvelopeHasTe /\ [Next]_vars => EnvelopeHasTe'
    BY EnvelopeHasTeNext
<1>3. Spec => []TypeOK
    BY TypeAlways
<1> QED
    BY <1>1, <1>2, <1>3, PTL DEF Spec

THEOREM EnvelopeHasTeAlwaysL == SpecL => []EnvelopeHasTe
BY SpecLImpliesSpec, EnvelopeHasTeAlways

(* In a live round te is in the envelope, and its call can be admitted.         *)
LEMMA EmergencyCallsWithoutObserverHolds ==
    ASSUME Mut \notin {"M_EMCOUPLE", "M_EMCOUPLE2"}, LiveHasRound, EnvelopeHasTe
    PROVE  EmergencyCallsWithoutObserver
BY ExpandENABLED, Isa DEF EmergencyCallsWithoutObserver, EmAdmit, EmCoupled, LiveHasRound,
                         EnvelopeHasTe, Tools

THEOREM EmergencyCallsWithoutObserverAlways ==
    ASSUME Mut \notin {"M_EMCOUPLE", "M_EMCOUPLE2"}
    PROVE  SpecL => []EmergencyCallsWithoutObserver
<1>1. SpecL => []LiveHasRound
    BY LiveHasRoundAlwaysL
<1>2. SpecL => []EnvelopeHasTe
    BY EnvelopeHasTeAlwaysL
<1>3. LiveHasRound /\ EnvelopeHasTe => EmergencyCallsWithoutObserver
    BY EmergencyCallsWithoutObserverHolds
<1> QED
    BY <1>1, <1>2, <1>3, PTL

-----------------------------------------------------------------------------
(* What each of the two mutations adds: the coupling, and with it a state in     *)
(* which no emergency call can be admitted. The counterexamples are TLC's.       *)

(* M_EMCOUPLE: with no live Observer, no emergency call can be admitted.         *)
LEMMA MutEmCoupleWaits ==
    ASSUME Mut = "M_EMCOUPLE", ~obsLive, NEW t
    PROVE  ~ENABLED EmAdmit(t)
BY ExpandENABLED DEF EmAdmit, EmCoupled

(* M_EMCOUPLE2: the same, from the seat's second round on.                       *)
LEMMA MutEmCouple2Waits ==
    ASSUME Mut = "M_EMCOUPLE2", em.round >= 2, ~obsLive, NEW t
    PROVE  ~ENABLED EmAdmit(t)
BY ExpandENABLED DEF EmAdmit, EmCoupled
=============================================================================
