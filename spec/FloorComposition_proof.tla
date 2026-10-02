------------------------- MODULE FloorComposition_proof -------------------------
(* TLAPS proofs of the five invariants FloorComposition.tla states (ADR-0030     *)
(* §1, §4, §5):                                                                  *)
(*                                                                               *)
(*   THEOREM AdmitImpliesFloorPermitAlways      (Mut \notin {"M_ERR", "M_OVERRIDE"}) *)
(*   THEOREM FloorErrorIsDenyAlways             (Mut \notin {"M_ERR", "M_OVERRIDE"}) *)
(*   THEOREM BundleRefusalHonoredAlways         (Mut \notin {"M_FAILOPEN", "M_OVERRIDE"}) *)
(*   THEOREM BundleCannotWriteFloorInputsAlways (Mut # "M_WRITE")                *)
(*   THEOREM EnvelopeHoldsAlways                (Mut \notin {"M_WRITE", "M_ERR", "M_OVERRIDE"}) *)
(*   THEOREM SafeAlways                         (Mut = "none")                   *)
(*                                                                               *)
(* Each theorem takes as hypothesis the mutations that break it. Three of these  *)
(* hypotheses are wider than the rows TLC ran (FloorComposition-results-         *)
(* 2026.09.24.txt) and the "Breaks under" column of theorem-premise-binding.md:  *)
(* M_OVERRIDE admits on a bundle allow whatever the floor said, so it breaks     *)
(* FloorErrorIsDeny and BundleRefusalHonored as well as AdmitImpliesFloorPermit;  *)
(* M_ERR admits on an engine error, so it breaks AdmitImpliesFloorPermit as well  *)
(* as FloorErrorIsDeny. TLC did not run those rows; the proofs need the          *)
(* hypotheses, which is the same finding.                                        *)
(*                                                                               *)
(* The four flag invariants are inductive by themselves: under the specified     *)
(* Admit, an admit is a floor permit without engine error and a bundle allow.    *)
(* EnvelopeHolds needs the floor's inputs to be the truth (BundleCannotWrite-     *)
(* FloorInputs) and one lemma: a floor permit without error on a possibly        *)
(* dropped entry lies within the envelope the truth defines.                     *)
(*                                                                               *)
(* FloorComposition.tla is cited by digest in ADR-0030 and ADR-0033 and is not   *)
(* edited; this module extends it. The mutations and the three witnesses stay    *)
(* with TLC; the lemmas at the end say why each mutation must fail. No           *)
(* constants beyond Mut, so no model assumptions.                                *)
(*                                                                               *)
(* Check with:  ../tools/tlapm FloorComposition_proof.tla   (from spec/; see     *)
(*              proof-results.sh for the results file)                           *)
EXTENDS FloorComposition, TLAPS

Entry  == [owner : Seats, sealed : {"yes", "no"}]
TypeOK == truth \in [Targets -> Entry] /\ fstore \in [Targets -> Entry]

(* The entry the floor evaluates: the stored one, with one attribute possibly    *)
(* dropped. This is the LET in Decide, named so lemmas can speak of it.          *)
Dropped(e0, drop) ==
  CASE drop = "owner"  -> [e0 EXCEPT !.owner = NONE]
    [] drop = "sealed" -> [e0 EXCEPT !.sealed = NONE]
    [] OTHER           -> e0

LEMMA DecideFlags ==
    ASSUME NEW p \in Seats, NEW a \in Acts, NEW r \in Targets, Decide(p, a, r)
    PROVE  \E b \in BundleOutcomes, drop \in {"no", "owner", "sealed"} :
             LET e  == Dropped(fstore[r], drop)
                 ok == Admit(e, p, a, b)
             IN /\ admitNoFloor'  = (admitNoFloor  \/ (ok /\ ~(EngineAllow(e, p, a) /\ ~EngineErr(e, p, a))))
                /\ admitWithErr'  = (admitWithErr  \/ (ok /\ EngineErr(e, p, a)))
                /\ admitNoBundle' = (admitNoBundle \/ (ok /\ b # "allow"))
                /\ admitOutside'  = (admitOutside  \/ (ok /\ ~Envelope(p, a, r)))
                /\ UNCHANGED <<truth, fstore>>
BY DEF Decide, Dropped

-----------------------------------------------------------------------------
(* The type invariant holds under every mutation.                                *)

LEMMA InitTypeOK == Init => TypeOK
BY DEF Init, TypeOK, Entry, Rec, Seats, Targets

LEMMA NextTypeOK == TypeOK /\ [Next]_vars => TypeOK'
<1> SUFFICES ASSUME TypeOK, [Next]_vars PROVE TypeOK' OBVIOUS
<1>1. CASE UNCHANGED vars
    BY <1>1 DEF TypeOK, vars
<1>2. ASSUME NEW t \in Targets, NEW s \in Seats, Reassign(t, s) PROVE TypeOK'
    BY <1>2 DEF Reassign, TypeOK, Entry
<1>3. ASSUME NEW t \in Targets, NEW s \in Seats, BundleWrite(t, s) PROVE TypeOK'
    BY <1>3 DEF BundleWrite, TypeOK, Entry
<1>4. ASSUME NEW t \in Targets, Seal(t) PROVE TypeOK'
    BY <1>4 DEF Seal, TypeOK, Entry
<1>5. ASSUME NEW p \in Seats, NEW a \in Acts, NEW r \in Targets, Decide(p, a, r) PROVE TypeOK'
    BY <1>5 DEF Decide, TypeOK
<1> QED
    BY <1>1, <1>2, <1>3, <1>4, <1>5 DEF Next

-----------------------------------------------------------------------------
(* What an admit implies under the specified Admit.                              *)

LEMMA AdmitIsFloorPermit ==
    ASSUME Mut # "M_ERR", Mut # "M_OVERRIDE", NEW e, NEW p, NEW a, NEW b, Admit(e, p, a, b)
    PROVE  EngineAllow(e, p, a) /\ ~EngineErr(e, p, a)
BY DEF Admit, FloorPermit

LEMMA AdmitIsBundleAllow ==
    ASSUME Mut # "M_FAILOPEN", Mut # "M_OVERRIDE", NEW e, NEW p, NEW a, NEW b, Admit(e, p, a, b)
    PROVE  b = "allow"
BY DEF Admit, BundleDeny

(* A floor permit without error, on the truth with at most one attribute         *)
(* dropped, lies within the envelope: a dropped attribute the act needs is an    *)
(* error, so the permit was decided on the true owner and seal.                  *)
LEMMA PermitWithinEnvelope ==
    ASSUME TypeOK, fstore = truth,
           NEW p \in Seats, NEW a \in Acts, NEW r \in Targets, NEW drop \in {"no", "owner", "sealed"},
           EngineAllow(Dropped(fstore[r], drop), p, a), ~EngineErr(Dropped(fstore[r], drop), p, a)
    PROVE  Envelope(p, a, r)
<1>1. CASE a = "Read"
    BY <1>1 DEF Envelope
<1>2. CASE a = "Draft"
    BY <1>2 DEF EngineAllow, EngineErr, Permits, Forbids, OwnerIs, SealedIs, Dropped, Envelope, TypeOK, Entry, NONE
<1>3. CASE a = "Emit"
    BY <1>3 DEF EngineAllow, EngineErr, Permits, Forbids, OwnerIs, SealedIs, Dropped, Envelope, TypeOK, Entry, NONE
<1> QED
    BY <1>1, <1>2, <1>3 DEF Acts

-----------------------------------------------------------------------------
(* The four flag invariants. Only Decide touches a flag.                         *)

LEMMA FlagsUnchanged ==
    ASSUME [Next]_vars, ~(\E p \in Seats, a \in Acts, r \in Targets : Decide(p, a, r))
    PROVE  UNCHANGED Flags
BY DEF Next, Reassign, BundleWrite, Seal, Flags, vars

LEMMA NextFloorFlags ==
    ASSUME Mut # "M_ERR", Mut # "M_OVERRIDE",
           AdmitImpliesFloorPermit, FloorErrorIsDeny, [Next]_vars
    PROVE  AdmitImpliesFloorPermit' /\ FloorErrorIsDeny'
<1>1. CASE \E p \in Seats, a \in Acts, r \in Targets : Decide(p, a, r)
    <2>1. PICK p \in Seats, a \in Acts, r \in Targets : Decide(p, a, r)
        BY <1>1
    <2>2. PICK b \in BundleOutcomes, drop \in {"no", "owner", "sealed"} :
             LET e  == Dropped(fstore[r], drop)
                 ok == Admit(e, p, a, b)
             IN /\ admitNoFloor'  = (admitNoFloor  \/ (ok /\ ~(EngineAllow(e, p, a) /\ ~EngineErr(e, p, a))))
                /\ admitWithErr'  = (admitWithErr  \/ (ok /\ EngineErr(e, p, a)))
        BY <2>1, DecideFlags
    <2>3. Admit(Dropped(fstore[r], drop), p, a, b)
            => EngineAllow(Dropped(fstore[r], drop), p, a) /\ ~EngineErr(Dropped(fstore[r], drop), p, a)
        BY AdmitIsFloorPermit
    <2> QED
        BY <2>2, <2>3 DEF AdmitImpliesFloorPermit, FloorErrorIsDeny
<1>2. CASE ~(\E p \in Seats, a \in Acts, r \in Targets : Decide(p, a, r))
    BY <1>2, FlagsUnchanged DEF Flags, AdmitImpliesFloorPermit, FloorErrorIsDeny
<1> QED
    BY <1>1, <1>2

LEMMA NextBundleFlag ==
    ASSUME Mut # "M_FAILOPEN", Mut # "M_OVERRIDE", BundleRefusalHonored, [Next]_vars
    PROVE  BundleRefusalHonored'
<1>1. CASE \E p \in Seats, a \in Acts, r \in Targets : Decide(p, a, r)
    <2>1. PICK p \in Seats, a \in Acts, r \in Targets : Decide(p, a, r)
        BY <1>1
    <2>2. PICK b \in BundleOutcomes, drop \in {"no", "owner", "sealed"} :
             admitNoBundle' = (admitNoBundle \/ (Admit(Dropped(fstore[r], drop), p, a, b) /\ b # "allow"))
        BY <2>1, DecideFlags
    <2>3. Admit(Dropped(fstore[r], drop), p, a, b) => b = "allow"
        BY AdmitIsBundleAllow
    <2> QED
        BY <2>2, <2>3 DEF BundleRefusalHonored
<1>2. CASE ~(\E p \in Seats, a \in Acts, r \in Targets : Decide(p, a, r))
    BY <1>2, FlagsUnchanged DEF Flags, BundleRefusalHonored
<1> QED
    BY <1>1, <1>2

-----------------------------------------------------------------------------
(* The floor's inputs are the truth: the lift writes both, and only the          *)
(* mutation lets the bundle write one.                                           *)

LEMMA NextInputs ==
    ASSUME Mut # "M_WRITE", TypeOK, BundleCannotWriteFloorInputs, [Next]_vars
    PROVE  BundleCannotWriteFloorInputs'
<1>1. CASE UNCHANGED vars
    BY <1>1 DEF BundleCannotWriteFloorInputs, vars
<1>2. ASSUME NEW t \in Targets, NEW s \in Seats, Reassign(t, s) PROVE BundleCannotWriteFloorInputs'
    BY <1>2 DEF Reassign, BundleCannotWriteFloorInputs
<1>3. ASSUME NEW t \in Targets, NEW s \in Seats, BundleWrite(t, s) PROVE BundleCannotWriteFloorInputs'
    BY <1>3 DEF BundleWrite
<1>4. ASSUME NEW t \in Targets, Seal(t) PROVE BundleCannotWriteFloorInputs'
    BY <1>4 DEF Seal, BundleCannotWriteFloorInputs
<1>5. ASSUME NEW p \in Seats, NEW a \in Acts, NEW r \in Targets, Decide(p, a, r) PROVE BundleCannotWriteFloorInputs'
    BY <1>5 DEF Decide, BundleCannotWriteFloorInputs
<1> QED
    BY <1>1, <1>2, <1>3, <1>4, <1>5 DEF Next

-----------------------------------------------------------------------------
(* EnvelopeHolds, with the inputs invariant and the type invariant.              *)

InvE == TypeOK /\ BundleCannotWriteFloorInputs /\ EnvelopeHolds

LEMMA NextInvE ==
    ASSUME Mut # "M_WRITE", Mut # "M_ERR", Mut # "M_OVERRIDE", InvE, [Next]_vars
    PROVE  InvE'
<1>0. TypeOK' /\ BundleCannotWriteFloorInputs'
    BY NextTypeOK, NextInputs DEF InvE
<1>1. CASE \E p \in Seats, a \in Acts, r \in Targets : Decide(p, a, r)
    <2>1. PICK p \in Seats, a \in Acts, r \in Targets : Decide(p, a, r)
        BY <1>1
    <2>2. PICK b \in BundleOutcomes, drop \in {"no", "owner", "sealed"} :
             admitOutside' = (admitOutside \/ (Admit(Dropped(fstore[r], drop), p, a, b) /\ ~Envelope(p, a, r)))
        BY <2>1, DecideFlags
    <2>3. Admit(Dropped(fstore[r], drop), p, a, b) => Envelope(p, a, r)
        <3> SUFFICES ASSUME Admit(Dropped(fstore[r], drop), p, a, b) PROVE Envelope(p, a, r) OBVIOUS
        <3>1. EngineAllow(Dropped(fstore[r], drop), p, a) /\ ~EngineErr(Dropped(fstore[r], drop), p, a)
            BY AdmitIsFloorPermit
        <3> QED
            BY <3>1, PermitWithinEnvelope DEF InvE, BundleCannotWriteFloorInputs
    <2> QED
        BY <1>0, <2>2, <2>3 DEF InvE, EnvelopeHolds
<1>2. CASE ~(\E p \in Seats, a \in Acts, r \in Targets : Decide(p, a, r))
    BY <1>0, <1>2, FlagsUnchanged DEF Flags, InvE, EnvelopeHolds
<1> QED
    BY <1>1, <1>2

-----------------------------------------------------------------------------
LEMMA InitAll == Init => TypeOK /\ Safe
BY InitTypeOK DEF Init, Safe, AdmitImpliesFloorPermit, FloorErrorIsDeny, BundleRefusalHonored,
                  BundleCannotWriteFloorInputs, EnvelopeHolds

THEOREM AdmitImpliesFloorPermitAlways ==
    ASSUME Mut # "M_ERR", Mut # "M_OVERRIDE"
    PROVE  Spec => []AdmitImpliesFloorPermit
<1>1. (AdmitImpliesFloorPermit /\ FloorErrorIsDeny) /\ [Next]_vars => (AdmitImpliesFloorPermit /\ FloorErrorIsDeny)'
    BY NextFloorFlags
<1>2. Init => AdmitImpliesFloorPermit /\ FloorErrorIsDeny
    BY InitAll DEF Safe
<1> QED
    BY <1>1, <1>2, PTL DEF Spec

THEOREM FloorErrorIsDenyAlways ==
    ASSUME Mut # "M_ERR", Mut # "M_OVERRIDE"
    PROVE  Spec => []FloorErrorIsDeny
<1>1. (AdmitImpliesFloorPermit /\ FloorErrorIsDeny) /\ [Next]_vars => (AdmitImpliesFloorPermit /\ FloorErrorIsDeny)'
    BY NextFloorFlags
<1>2. Init => AdmitImpliesFloorPermit /\ FloorErrorIsDeny
    BY InitAll DEF Safe
<1> QED
    BY <1>1, <1>2, PTL DEF Spec

THEOREM BundleRefusalHonoredAlways ==
    ASSUME Mut # "M_FAILOPEN", Mut # "M_OVERRIDE"
    PROVE  Spec => []BundleRefusalHonored
<1>1. BundleRefusalHonored /\ [Next]_vars => BundleRefusalHonored'
    BY NextBundleFlag
<1>2. Init => BundleRefusalHonored
    BY InitAll DEF Safe
<1> QED
    BY <1>1, <1>2, PTL DEF Spec

THEOREM BundleCannotWriteFloorInputsAlways ==
    ASSUME Mut # "M_WRITE"
    PROVE  Spec => []BundleCannotWriteFloorInputs
<1>1. (TypeOK /\ BundleCannotWriteFloorInputs) /\ [Next]_vars => (TypeOK /\ BundleCannotWriteFloorInputs)'
    BY NextTypeOK, NextInputs
<1>2. Init => TypeOK /\ BundleCannotWriteFloorInputs
    BY InitAll DEF Safe
<1> QED
    BY <1>1, <1>2, PTL DEF Spec

THEOREM EnvelopeHoldsAlways ==
    ASSUME Mut # "M_WRITE", Mut # "M_ERR", Mut # "M_OVERRIDE"
    PROVE  Spec => []EnvelopeHolds
<1>1. InvE /\ [Next]_vars => InvE'
    BY NextInvE
<1>2. Init => InvE
    BY InitAll DEF InvE, Safe
<1>3. InvE => EnvelopeHolds
    BY DEF InvE
<1> QED
    BY <1>1, <1>2, <1>3, PTL DEF Spec

THEOREM SafeAlways ==
    ASSUME Mut = "none"
    PROVE  Spec => []Safe
<1>1. Spec => []AdmitImpliesFloorPermit
    BY AdmitImpliesFloorPermitAlways
<1>2. Spec => []FloorErrorIsDeny
    BY FloorErrorIsDenyAlways
<1>3. Spec => []BundleRefusalHonored
    BY BundleRefusalHonoredAlways
<1>4. Spec => []BundleCannotWriteFloorInputs
    BY BundleCannotWriteFloorInputsAlways
<1>5. Spec => []EnvelopeHolds
    BY EnvelopeHoldsAlways
<1> QED
    BY <1>1, <1>2, <1>3, <1>4, <1>5, PTL DEF Safe

-----------------------------------------------------------------------------
(* Why the mutations must fail. The counterexamples are TLC's.                   *)

(* M_OVERRIDE: a bundle allow admits whatever the floor said.                    *)
LEMMA MutOverrideAdmitsOnAllow ==
    ASSUME Mut = "M_OVERRIDE", NEW e, NEW p, NEW a
    PROVE  Admit(e, p, a, "allow")
BY DEF Admit

(* M_ERR: an engine error does not deny; a permit with error passes the floor.   *)
LEMMA MutErrPermitsWithError ==
    ASSUME Mut = "M_ERR", NEW e, NEW p, NEW a, EngineAllow(e, p, a)
    PROVE  FloorPermit(e, p, a)
BY DEF FloorPermit

(* M_FAILOPEN: only an explicit deny denies; error, undefined, absent and         *)
(* unreachable pass.                                                             *)
LEMMA MutFailOpenPassesErrors ==
    ASSUME Mut = "M_FAILOPEN", NEW b \in BundleOutcomes \ {"allow", "deny"}
    PROVE  ~BundleDeny(b)
BY DEF BundleDeny

(* M_WRITE: the bundle can move the floor's copy of an owner off the truth.      *)
LEMMA MutWriteDivergesInputs ==
    ASSUME Mut = "M_WRITE", TypeOK, NEW t \in Targets, NEW s \in Seats, s # truth[t].owner, BundleWrite(t, s)
    PROVE  fstore' # truth'
BY DEF BundleWrite, TypeOK, Entry

=============================================================================
