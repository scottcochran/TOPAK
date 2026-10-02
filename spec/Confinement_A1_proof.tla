------------------------- MODULE Confinement_A1_proof -------------------------
(* TLAPS proofs of the four invariants Confinement.tla states (ADR-0034 §7,     *)
(* A1), for every declared rung:                                                 *)
(*                                                                               *)
(*   THEOREM ContainedMeansConfinedAlways == Spec => []ContainedMeansConfined    *)
(*       (Mut \notin {"M_HOST", "M_HW", "M_CONTESTED", "M_UNBOUND", "M_PROFILE"}) *)
(*   THEOREM NoSilentDowngradeAlways      == Spec => []NoSilentDowngrade         *)
(*       (Mut \notin {"M_DOWNGRADE", "M_RENEWLOW"})                              *)
(*   THEOREM ContestedStoppedAlways       == Spec => []ContestedStopped          *)
(*       (Mut # "M_CONTESTED")                                                   *)
(*   THEOREM FreshAppraisalAlways         == Spec => []FreshAppraisal            *)
(*       (Mut # "M_STALE")                                                       *)
(*   THEOREM SafeAlways                   == Spec => []Safe   (Mut = "none")     *)
(*                                                                               *)
(* Each theorem takes as hypothesis only the mutations that break it. The one    *)
(* assumption is that Declared is a rung, 0..3 (ADR-0034 §2); the proofs hold    *)
(* for every rung at once, where TLC ran one rung per row. MaxEpoch, MaxIdx and  *)
(* MaxGen only cut the state space and need no assumption.                       *)
(*                                                                               *)
(* ContainedMeansConfined rests on generation binding: a guest's asked and boot  *)
(* images never change while its generation stands; an attested appraisal and    *)
(* the lease granted on it remember that generation and the asked image; an act  *)
(* is admitted only against the same generation. Under the specified mechanism   *)
(* the running image is the booted one, so a contained act runs the asked        *)
(* image, which the lease profile names: Arch.                                   *)
(*                                                                               *)
(* The proof of Confinement.tla, changed in one case split: the successor       *)
(* Confinement_A1.tla differs only in `Evidence` at rung 0 (ADR-0034 finding 6), *)
(* so in the step that expands `Evidence` rung 0 joins rung 1 in the case        *)
(* LowRungHonest covers, where Confinement_proof split on `Declared = 1`. This    *)
(* module extends the successor. The mutations and the eight witnesses stay with TLC        *)
(* (Confinement-results-2026.09.25/28/30.txt); the lemmas at the end say why     *)
(* each mutation must fail.                                                      *)
(*                                                                               *)
(* Check with:  ../tools/tlapm Confinement_proof.tla   (from spec/; see          *)
(*              proof-results.sh for the results file)                           *)
EXTENDS Confinement_A1, TLAPS

ASSUME DeclaredRung == Declared \in 0..3

Images == Promoted \cup {"rogue", "none"}
GuestRec == [img : Images, asked : Promoted \cup {"none"}, boot : Images, gen : Nat]
PendRec  == [v : {"none", "Attested", "Unattestable"}, prof : Promoted \cup {"none"}, nEpoch : Nat, gen : Nat]
LeaseRec == [live : BOOLEAN, rung : Nat, prof : Promoted \cup {"none"}, epoch : Nat, nEpoch : Nat, gen : Nat]
TypeOK == /\ guest   \in [Principals -> GuestRec]
          /\ gens    \in [Principals -> Nat]
          /\ pending \in [Principals -> PendRec]
          /\ lease   \in [Principals -> LeaseRec]
          /\ epoch \in Nat
          /\ idx \in Nat
          /\ revoked \subseteq Principals
          /\ verifierUp \in BOOLEAN
          /\ contested \subseteq Principals

LEMMA NoRecs == NoGuest \in GuestRec /\ NoPending \in PendRec /\ NoLease \in LeaseRec
BY DEF NoGuest, NoPending, NoLease, GuestRec, PendRec, LeaseRec, Images

LEMMA VerdictValues ==
    ASSUME NEW p \in Principals
    PROVE  Verdict(p) \in {"Attested", "Contested", "Unattestable"}
BY DEF Verdict

-----------------------------------------------------------------------------
(* The type invariant holds under every mutation.                                *)

LEMMA InitTypeOK == Init => TypeOK
BY NoRecs DEF Init, TypeOK

LEMMA NextTypeOK == TypeOK /\ [Next]_vars => TypeOK'
<1> SUFFICES ASSUME TypeOK, [Next]_vars PROVE TypeOK' OBVIOUS
<1>1. CASE UNCHANGED vars
    BY <1>1 DEF TypeOK, vars
<1>2. CASE Fence
    BY <1>2 DEF Fence, TypeOK
<1>3. CASE VerifierFlip
    BY <1>3 DEF VerifierFlip, TypeOK
<1>4. ASSUME NEW p \in Principals, Launch(p) PROVE TypeOK'
    <2>0. PICK asked \in Promoted : \E img \in (IF HostMayLaunchRogue THEN {asked, "rogue"} ELSE {asked}) :
            guest' = [guest EXCEPT ![p] = [img |-> img, asked |-> asked, boot |-> img, gen |-> gens[p] + 1]]
        BY <1>4 DEF Launch
    <2>1. PICK img \in (IF HostMayLaunchRogue THEN {asked, "rogue"} ELSE {asked}) :
            guest' = [guest EXCEPT ![p] = [img |-> img, asked |-> asked, boot |-> img, gen |-> gens[p] + 1]]
        BY <2>0
    <2>2. [img |-> img, asked |-> asked, boot |-> img, gen |-> gens[p] + 1] \in GuestRec
        BY DEF TypeOK, GuestRec, Images
    <2> QED
        BY <1>4, <2>1, <2>2 DEF Launch, TypeOK
<1>5. ASSUME NEW p \in Principals, Kill(p) PROVE TypeOK'
    BY <1>5, NoRecs DEF Kill, TypeOK
<1>6. ASSUME NEW p \in Principals, Tamper(p) PROVE TypeOK'
    BY <1>6, NoRecs DEF Tamper, TypeOK, GuestRec, Images
<1>7. ASSUME NEW p \in Principals, Appraise(p) PROVE TypeOK'
    <2>1. Verdict(p) \in {"Attested", "Contested", "Unattestable"}
        BY VerdictValues
    <2> QED
        BY <1>7, <2>1 DEF Appraise, TypeOK, PendRec, GuestRec
<1>8. ASSUME NEW p \in Principals, Discard(p) PROVE TypeOK'
    BY <1>8, NoRecs DEF Discard, TypeOK
<1>9. ASSUME NEW p \in Principals, Grant(p) PROVE TypeOK'
    BY <1>9, NoRecs, DeclaredRung DEF Grant, TypeOK, LeaseRec, PendRec
<1>10. ASSUME NEW p \in Principals, Renew(p) PROVE TypeOK'
    <2>1. Verdict(p) \in {"Attested", "Contested", "Unattestable"}
        BY VerdictValues
    <2> QED
        BY <1>10, <2>1, NoRecs DEF Renew, TypeOK, LeaseRec
<1>11. ASSUME NEW p \in Principals, Act(p) PROVE TypeOK'
    BY <1>11 DEF Act, TypeOK
<1>12. ASSUME NEW p \in Principals, EndRound(p) PROVE TypeOK'
    BY <1>12, NoRecs DEF EndRound, TypeOK
<1> QED
    BY <1>1, <1>2, <1>3, <1>4, <1>5, <1>6, <1>7, <1>8, <1>9, <1>10, <1>11, <1>12 DEF Next

-----------------------------------------------------------------------------
(* ContainedMeansConfined                                                        *)

(* The running image is the booted image: no host or hardware tampering.         *)
GuestImg == \A p \in Principals : guest[p].img = guest[p].boot
(* A live guest carries the current generation; an empty slot carries 0.         *)
GuestGen == \A p \in Principals :
              IF guest[p].img = "none" THEN guest[p].gen = 0
                                       ELSE guest[p].gen = gens[p] /\ gens[p] >= 1
(* Below rung 2 the host cannot launch a rogue image, so boot is asked.          *)
LowRungHonest == \A p \in Principals :
                   (Declared < 2 /\ guest[p].img # "none") => guest[p].boot = guest[p].asked
(* An attested appraisal remembers a generation at or below the current one,     *)
(* and while that guest stands, its asked image is the profile and is booted.    *)
PendingBinds == \A p \in Principals :
  pending[p].v = "Attested" =>
    /\ pending[p].gen >= 1 /\ pending[p].gen <= gens[p]
    /\ (guest[p].img # "none" /\ pending[p].gen = guest[p].gen)
         => pending[p].prof = guest[p].asked /\ guest[p].boot = guest[p].asked
(* The same for a lease above rung 0, which was granted on such an appraisal.    *)
LeaseBinds == \A p \in Principals :
  (lease[p].live /\ lease[p].rung >= 1) =>
    /\ lease[p].gen >= 1 /\ lease[p].gen <= gens[p]
    /\ (guest[p].img # "none" /\ lease[p].gen = guest[p].gen)
         => lease[p].prof = guest[p].asked /\ guest[p].boot = guest[p].asked

InvC == /\ TypeOK /\ GuestImg /\ GuestGen /\ LowRungHonest
        /\ PendingBinds /\ LeaseBinds /\ ContainedMeansConfined

LEMMA InitInvC == Init => InvC
BY InitTypeOK DEF Init, InvC, GuestImg, GuestGen, LowRungHonest, PendingBinds, LeaseBinds,
                  ContainedMeansConfined, NoGuest, NoPending, NoLease

(* Under the specified host and hardware, Tamper only kills.                     *)
LEMMA TamperKills ==
    ASSUME Mut # "M_HOST", Mut # "M_HW", NEW p \in Principals, Tamper(p)
    PROVE  /\ guest' = [guest EXCEPT ![p] = NoGuest]
           /\ UNCHANGED <<gens, pending, lease, epoch, idx, revoked, verifierUp, acted, contested, refused, renewOut>>
BY DEF Tamper

LEMMA NextInvC ==
    ASSUME Mut # "M_HOST", Mut # "M_HW", Mut # "M_CONTESTED", Mut # "M_UNBOUND", Mut # "M_PROFILE",
           InvC, [Next]_vars
    PROVE  InvC'
<1>0. TypeOK /\ TypeOK'
    BY NextTypeOK DEF InvC
<1>1. CASE UNCHANGED vars
    BY <1>0, <1>1 DEF InvC, GuestImg, GuestGen, LowRungHonest, PendingBinds, LeaseBinds, ContainedMeansConfined, vars
<1>2. CASE Fence
    BY <1>0, <1>2 DEF Fence, InvC, GuestImg, GuestGen, LowRungHonest, PendingBinds, LeaseBinds, ContainedMeansConfined
<1>3. CASE VerifierFlip
    BY <1>0, <1>3 DEF VerifierFlip, InvC, GuestImg, GuestGen, LowRungHonest, PendingBinds, LeaseBinds, ContainedMeansConfined
<1>4. ASSUME NEW p \in Principals, Launch(p) PROVE InvC'
    <2>0. PICK asked \in Promoted : \E img \in (IF HostMayLaunchRogue THEN {asked, "rogue"} ELSE {asked}) :
            guest' = [guest EXCEPT ![p] = [img |-> img, asked |-> asked, boot |-> img, gen |-> gens[p] + 1]]
        BY <1>4 DEF Launch
    <2>1. PICK img \in (IF HostMayLaunchRogue THEN {asked, "rogue"} ELSE {asked}) :
            guest' = [guest EXCEPT ![p] = [img |-> img, asked |-> asked, boot |-> img, gen |-> gens[p] + 1]]
        BY <2>0
    <2>2. guest[p].img = "none" /\ gens' = [gens EXCEPT ![p] = gens[p] + 1]
          /\ UNCHANGED <<pending, lease, epoch, idx, revoked, verifierUp, acted, contested, refused, tamperKilled, renewOut>>
        BY <1>4 DEF Launch
    <2>3. Declared < 2 => img = asked
        BY <2>1, DeclaredRung DEF HostMayLaunchRogue
    <2>4. GuestImg' /\ GuestGen' /\ LowRungHonest'
        <3>1. img # "none" /\ guest'[p] = [img |-> img, asked |-> asked, boot |-> img, gen |-> gens[p] + 1]
              /\ gens'[p] = gens[p] + 1
              /\ \A q \in Principals : q # p => guest'[q] = guest[q] /\ gens'[q] = gens[q]
            BY <1>0, <2>1, <2>2 DEF TypeOK, GuestRec, Promoted
        <3>2. GuestImg'
            BY <1>0, <3>1 DEF TypeOK, GuestRec, InvC, GuestImg
        <3>3. GuestGen'
            BY <1>0, <3>1 DEF TypeOK, GuestRec, InvC, GuestGen
        <3>4. LowRungHonest'
            BY <1>0, <2>3, <3>1 DEF TypeOK, GuestRec, InvC, LowRungHonest
        <3> QED
            BY <3>2, <3>3, <3>4
    <2>5. PendingBinds'
        BY <1>0, <2>1, <2>2 DEF TypeOK, GuestRec, PendRec, InvC, PendingBinds
    <2>6. LeaseBinds'
        BY <1>0, <2>1, <2>2 DEF TypeOK, GuestRec, LeaseRec, InvC, LeaseBinds
    <2> QED
        BY <1>0, <2>2, <2>4, <2>5, <2>6 DEF InvC, ContainedMeansConfined
<1>5. ASSUME NEW p \in Principals, Kill(p) PROVE InvC'
    BY <1>0, <1>5 DEF Kill, TypeOK, GuestRec, NoGuest, InvC, GuestImg, GuestGen, LowRungHonest, PendingBinds, LeaseBinds, ContainedMeansConfined
<1>6. ASSUME NEW p \in Principals, Tamper(p) PROVE InvC'
    <2>1. guest' = [guest EXCEPT ![p] = NoGuest]
          /\ UNCHANGED <<gens, pending, lease, epoch, idx, revoked, verifierUp, acted, contested, refused, renewOut>>
        BY <1>6, TamperKills
    <2> QED
        BY <1>0, <2>1 DEF TypeOK, GuestRec, NoGuest, InvC, GuestImg, GuestGen, LowRungHonest, PendingBinds, LeaseBinds, ContainedMeansConfined
<1>7. ASSUME NEW p \in Principals, Appraise(p) PROVE InvC'
    <2>1. guest[p].img # "none" /\ ~lease[p].live /\ pending[p].v = "none"
          /\ UNCHANGED <<guest, gens, lease, epoch, verifierUp, acted, tamperKilled, renewOut>>
        BY <1>7 DEF Appraise
    <2>2. GuestImg' /\ GuestGen' /\ LowRungHonest' /\ LeaseBinds' /\ ContainedMeansConfined'
        BY <1>0, <2>1 DEF InvC, GuestImg, GuestGen, LowRungHonest, LeaseBinds, ContainedMeansConfined
    <2>3. Verdict(p) \in {"Attested", "Contested", "Unattestable"}
        BY VerdictValues
    <2>4. CASE Verdict(p) = "Contested"
        <3>1. UNCHANGED pending
            BY <1>7, <2>4 DEF Appraise
        <3> QED
            BY <1>0, <2>1, <2>2, <3>1 DEF InvC, PendingBinds
    <2>5. CASE Verdict(p) = "Unattestable"
        <3>1. \/ UNCHANGED pending
              \/ pending' = [pending EXCEPT ![p] = [v |-> "Unattestable", prof |-> guest[p].asked,
                                                    nEpoch |-> epoch, gen |-> guest[p].gen]]
            BY <1>7, <2>5 DEF Appraise
        <3> QED
            BY <1>0, <2>1, <2>2, <3>1 DEF TypeOK, PendRec, InvC, PendingBinds
    <2>6. CASE Verdict(p) = "Attested"
        <3>1. pending' = [pending EXCEPT ![p] = [v |-> "Attested", prof |-> guest[p].asked,
                                                 nEpoch |-> epoch, gen |-> guest[p].gen]]
            BY <1>7, <2>6 DEF Appraise
        <3>2. guest[p].boot = guest[p].asked
            <4>1. CASE Declared <= 1
                BY <2>1, <4>1, DeclaredRung DEF InvC, LowRungHonest
            <4>2. CASE ~(Declared <= 1)
                BY <2>6, <4>2 DEF Verdict, Evidence
            <4> QED
                BY <4>1, <4>2
        <3>3. guest[p].gen >= 1 /\ guest[p].gen <= gens[p]
            BY <1>0, <2>1 DEF TypeOK, InvC, GuestGen
        <3> QED
            BY <1>0, <2>1, <2>2, <3>1, <3>2, <3>3 DEF TypeOK, PendRec, InvC, PendingBinds
    <2> QED
        BY <2>3, <2>4, <2>5, <2>6
<1>8. ASSUME NEW p \in Principals, Discard(p) PROVE InvC'
    BY <1>0, <1>8 DEF Discard, TypeOK, PendRec, NoPending, InvC, GuestImg, GuestGen, LowRungHonest, PendingBinds, LeaseBinds, ContainedMeansConfined
<1>9. ASSUME NEW p \in Principals, Grant(p) PROVE InvC'
    <2>1. /\ pending[p].v \in {"Attested", "Unattestable"}
          /\ lease' = [lease EXCEPT ![p] =
                 [live |-> TRUE,
                  rung |-> IF pending[p].v = "Attested" THEN Declared ELSE 0,
                  prof |-> pending[p].prof, epoch |-> epoch,
                  nEpoch |-> pending[p].nEpoch, gen |-> pending[p].gen]]
          /\ pending' = [pending EXCEPT ![p] = NoPending]
          /\ UNCHANGED <<guest, gens, epoch, revoked, verifierUp, acted, contested, refused, tamperKilled, renewOut>>
        BY <1>9 DEF Grant
    <2>2. GuestImg' /\ GuestGen' /\ LowRungHonest' /\ ContainedMeansConfined' /\ PendingBinds'
        BY <1>0, <2>1 DEF TypeOK, PendRec, NoPending, InvC, GuestImg, GuestGen, LowRungHonest, PendingBinds, ContainedMeansConfined
    <2>3. LeaseBinds'
        <3>1. lease'[p].rung >= 1 => pending[p].v = "Attested"
            BY <1>0, <2>1 DEF TypeOK, LeaseRec
        <3>2. /\ lease'[p].live /\ lease'[p].prof = pending[p].prof /\ lease'[p].gen = pending[p].gen
              /\ \A q \in Principals : q # p => lease'[q] = lease[q]
            BY <1>0, <2>1 DEF TypeOK, LeaseRec
        <3> QED
            BY <1>0, <2>1, <3>1, <3>2 DEF TypeOK, InvC, PendingBinds, LeaseBinds
    <2> QED
        BY <1>0, <2>2, <2>3 DEF InvC
<1>10. ASSUME NEW p \in Principals, Renew(p) PROVE InvC'
    <2>1. /\ lease[p].live
          /\ UNCHANGED <<guest, gens, pending, epoch, verifierUp, acted, refused, tamperKilled>>
        BY <1>10 DEF Renew
    <2>2. GuestImg' /\ GuestGen' /\ LowRungHonest' /\ PendingBinds' /\ ContainedMeansConfined'
        BY <1>0, <2>1 DEF InvC, GuestImg, GuestGen, LowRungHonest, PendingBinds, ContainedMeansConfined
    <2>3. \/ lease' = [lease EXCEPT ![p].nEpoch = epoch]
          \/ lease' = [lease EXCEPT ![p] = NoLease]
          \/ lease' = [lease EXCEPT ![p].rung = 0, ![p].nEpoch = epoch]
        BY <1>10 DEF Renew
    <2>4. LeaseBinds'
        BY <1>0, <2>1, <2>3 DEF TypeOK, LeaseRec, NoLease, InvC, LeaseBinds
    <2> QED
        BY <1>0, <2>2, <2>4 DEF InvC
<1>11. ASSUME NEW p \in Principals, Act(p) PROVE InvC'
    <2>1. /\ lease[p].live /\ guest[p].img # "none" /\ lease[p].gen = guest[p].gen
          /\ acted' = acted \cup {[principal |-> p, contained |-> Contained(p), img |-> guest[p].img]}
          /\ UNCHANGED <<guest, gens, pending, lease, epoch, idx, revoked, verifierUp, contested, refused, tamperKilled, renewOut>>
        BY <1>11 DEF Act
    <2>2. Contained(p) => guest[p].img = Arch
        <3> SUFFICES ASSUME Contained(p) PROVE guest[p].img = Arch OBVIOUS
        <3>1. lease[p].rung >= 1 /\ lease[p].prof = Arch
            BY DEF Contained
        <3>2. lease[p].prof = guest[p].asked /\ guest[p].boot = guest[p].asked
            BY <2>1, <3>1 DEF InvC, LeaseBinds
        <3> QED
            BY <3>1, <3>2 DEF InvC, GuestImg
    <2>3. ContainedMeansConfined'
        BY <2>1, <2>2 DEF InvC, ContainedMeansConfined
    <2> QED
        BY <1>0, <2>1, <2>3 DEF InvC, GuestImg, GuestGen, LowRungHonest, PendingBinds, LeaseBinds
<1>12. ASSUME NEW p \in Principals, EndRound(p) PROVE InvC'
    BY <1>0, <1>12 DEF EndRound, TypeOK, GuestRec, LeaseRec, NoGuest, NoLease, InvC, GuestImg, GuestGen, LowRungHonest, PendingBinds, LeaseBinds, ContainedMeansConfined
<1> QED
    BY <1>1, <1>2, <1>3, <1>4, <1>5, <1>6, <1>7, <1>8, <1>9, <1>10, <1>11, <1>12 DEF Next

THEOREM ContainedMeansConfinedAlways ==
    ASSUME Mut # "M_HOST", Mut # "M_HW", Mut # "M_CONTESTED", Mut # "M_UNBOUND", Mut # "M_PROFILE"
    PROVE  Spec => []ContainedMeansConfined
<1>1. InvC /\ [Next]_vars => InvC'
    BY NextInvC
<1>2. InvC => ContainedMeansConfined
    BY DEF InvC
<1> QED
    BY InitInvC, <1>1, <1>2, PTL DEF Spec

-----------------------------------------------------------------------------
(* NoSilentDowngrade. An unattestable appraisal is refused rather than held, so  *)
(* every grant is at the declared rung, and a renewal keeps or ends the lease.   *)

PendingAttested == \A p \in Principals : pending[p].v # "Unattestable"
InvD == TypeOK /\ PendingAttested /\ NoSilentDowngrade

LEMMA InitInvD == Init => InvD
BY InitTypeOK DEF Init, InvD, PendingAttested, NoSilentDowngrade, NoPending, NoLease

LEMMA NextInvD ==
    ASSUME Mut # "M_DOWNGRADE", Mut # "M_RENEWLOW", InvD, [Next]_vars
    PROVE  InvD'
<1>0. TypeOK /\ TypeOK'
    BY NextTypeOK DEF InvD
<1>1. CASE UNCHANGED vars
    BY <1>0, <1>1 DEF InvD, PendingAttested, NoSilentDowngrade, vars
<1>2. CASE Fence
    BY <1>0, <1>2 DEF Fence, InvD, PendingAttested, NoSilentDowngrade
<1>3. CASE VerifierFlip
    BY <1>0, <1>3 DEF VerifierFlip, InvD, PendingAttested, NoSilentDowngrade
<1>4. ASSUME NEW p \in Principals, Launch(p) PROVE InvD'
    BY <1>0, <1>4 DEF Launch, InvD, PendingAttested, NoSilentDowngrade
<1>5. ASSUME NEW p \in Principals, Kill(p) PROVE InvD'
    BY <1>0, <1>5 DEF Kill, InvD, PendingAttested, NoSilentDowngrade
<1>6. ASSUME NEW p \in Principals, Tamper(p) PROVE InvD'
    BY <1>0, <1>6 DEF Tamper, InvD, PendingAttested, NoSilentDowngrade
<1>7. ASSUME NEW p \in Principals, Appraise(p) PROVE InvD'
    <2>1. UNCHANGED lease
        BY <1>7 DEF Appraise
    <2>2. \/ UNCHANGED pending
          \/ pending' = [pending EXCEPT ![p] = [v |-> "Attested", prof |-> guest[p].asked,
                                                nEpoch |-> epoch, gen |-> guest[p].gen]]
        BY <1>7, VerdictValues DEF Appraise
    <2> QED
        BY <1>0, <2>1, <2>2 DEF TypeOK, PendRec, InvD, PendingAttested, NoSilentDowngrade
<1>8. ASSUME NEW p \in Principals, Discard(p) PROVE InvD'
    BY <1>0, <1>8 DEF Discard, TypeOK, PendRec, NoPending, InvD, PendingAttested, NoSilentDowngrade
<1>9. ASSUME NEW p \in Principals, Grant(p) PROVE InvD'
    <2>1. pending[p].v = "Attested"
        BY <1>9 DEF Grant, InvD, PendingAttested
    <2>2. /\ lease' = [lease EXCEPT ![p] =
                 [live |-> TRUE, rung |-> Declared,
                  prof |-> pending[p].prof, epoch |-> epoch,
                  nEpoch |-> pending[p].nEpoch, gen |-> pending[p].gen]]
          /\ pending' = [pending EXCEPT ![p] = NoPending]
        BY <1>9, <2>1 DEF Grant
    <2> QED
        BY <1>0, <2>2 DEF TypeOK, LeaseRec, PendRec, NoPending, InvD, PendingAttested, NoSilentDowngrade
<1>10. ASSUME NEW p \in Principals, Renew(p) PROVE InvD'
    <2>1. UNCHANGED pending
        BY <1>10 DEF Renew
    <2>2. \/ lease' = [lease EXCEPT ![p].nEpoch = epoch]
          \/ lease' = [lease EXCEPT ![p] = NoLease]
        BY <1>10 DEF Renew
    <2> QED
        BY <1>0, <2>1, <2>2 DEF TypeOK, LeaseRec, NoLease, InvD, PendingAttested, NoSilentDowngrade
<1>11. ASSUME NEW p \in Principals, Act(p) PROVE InvD'
    BY <1>0, <1>11 DEF Act, InvD, PendingAttested, NoSilentDowngrade
<1>12. ASSUME NEW p \in Principals, EndRound(p) PROVE InvD'
    BY <1>0, <1>12 DEF EndRound, TypeOK, LeaseRec, NoLease, InvD, PendingAttested, NoSilentDowngrade
<1> QED
    BY <1>1, <1>2, <1>3, <1>4, <1>5, <1>6, <1>7, <1>8, <1>9, <1>10, <1>11, <1>12 DEF Next

THEOREM NoSilentDowngradeAlways ==
    ASSUME Mut # "M_DOWNGRADE", Mut # "M_RENEWLOW"
    PROVE  Spec => []NoSilentDowngrade
<1>1. InvD /\ [Next]_vars => InvD'
    BY NextInvD
<1>2. InvD => NoSilentDowngrade
    BY DEF InvD
<1> QED
    BY InitInvD, <1>1, <1>2, PTL DEF Spec

-----------------------------------------------------------------------------
(* ContestedStopped. A contested verdict revokes, a revoked principal is never    *)
(* granted or renewed, and a renewal that finds a contest ends the lease.        *)

RevokedNotLive == \A p \in revoked : ~lease[p].live
InvS == TypeOK /\ contested \subseteq revoked /\ RevokedNotLive

LEMMA InitInvS == Init => InvS
BY InitTypeOK DEF Init, InvS, RevokedNotLive

LEMMA NextInvS ==
    ASSUME Mut # "M_CONTESTED", InvS, [Next]_vars
    PROVE  InvS'
<1>0. TypeOK /\ TypeOK'
    BY NextTypeOK DEF InvS
<1>1. CASE UNCHANGED vars
    BY <1>0, <1>1 DEF InvS, RevokedNotLive, vars
<1>2. CASE Fence
    BY <1>0, <1>2 DEF Fence, InvS, RevokedNotLive
<1>3. CASE VerifierFlip
    BY <1>0, <1>3 DEF VerifierFlip, InvS, RevokedNotLive
<1>4. ASSUME NEW p \in Principals, Launch(p) PROVE InvS'
    BY <1>0, <1>4 DEF Launch, InvS, RevokedNotLive
<1>5. ASSUME NEW p \in Principals, Kill(p) PROVE InvS'
    BY <1>0, <1>5 DEF Kill, InvS, RevokedNotLive
<1>6. ASSUME NEW p \in Principals, Tamper(p) PROVE InvS'
    BY <1>0, <1>6 DEF Tamper, InvS, RevokedNotLive
<1>7. ASSUME NEW p \in Principals, Appraise(p) PROVE InvS'
    <2>1. ~lease[p].live /\ UNCHANGED lease
        BY <1>7 DEF Appraise
    <2>2. \/ (revoked' = revoked \cup {p} /\ contested' = contested \cup {p})
          \/ (UNCHANGED revoked /\ UNCHANGED contested)
        BY <1>7 DEF Appraise
    <2> QED
        BY <1>0, <2>1, <2>2 DEF InvS, RevokedNotLive
<1>8. ASSUME NEW p \in Principals, Discard(p) PROVE InvS'
    BY <1>0, <1>8 DEF Discard, InvS, RevokedNotLive
<1>9. ASSUME NEW p \in Principals, Grant(p) PROVE InvS'
    <2>1. p \notin revoked /\ UNCHANGED <<revoked, contested>>
        BY <1>9 DEF Grant
    <2>2. \A q \in Principals : q # p => lease'[q] = lease[q]
        BY <1>0, <1>9 DEF Grant, TypeOK
    <2> QED
        BY <1>0, <2>1, <2>2 DEF TypeOK, InvS, RevokedNotLive
<1>10. ASSUME NEW p \in Principals, Renew(p) PROVE InvS'
    <2>1. lease[p].live
        BY <1>10 DEF Renew
    <2>2. p \notin revoked
        BY <2>1 DEF InvS, RevokedNotLive
    <2>3. \/ (lease' = [lease EXCEPT ![p].nEpoch = epoch] /\ UNCHANGED <<revoked, contested>>)
          \/ (lease' = [lease EXCEPT ![p] = NoLease] /\ revoked' = revoked \cup {p} /\ contested' = contested \cup {p})
          \/ (lease' = [lease EXCEPT ![p].rung = 0, ![p].nEpoch = epoch] /\ UNCHANGED <<revoked, contested>>)
          \/ (lease' = [lease EXCEPT ![p] = NoLease] /\ UNCHANGED <<revoked, contested>>)
        BY <1>10 DEF Renew
    <2> QED
        BY <1>0, <2>2, <2>3 DEF TypeOK, LeaseRec, NoLease, InvS, RevokedNotLive
<1>11. ASSUME NEW p \in Principals, Act(p) PROVE InvS'
    BY <1>0, <1>11 DEF Act, InvS, RevokedNotLive
<1>12. ASSUME NEW p \in Principals, EndRound(p) PROVE InvS'
    BY <1>0, <1>12 DEF EndRound, TypeOK, LeaseRec, NoLease, InvS, RevokedNotLive
<1> QED
    BY <1>1, <1>2, <1>3, <1>4, <1>5, <1>6, <1>7, <1>8, <1>9, <1>10, <1>11, <1>12 DEF Next

THEOREM ContestedStoppedAlways ==
    ASSUME Mut # "M_CONTESTED"
    PROVE  Spec => []ContestedStopped
<1>1. InvS /\ [Next]_vars => InvS'
    BY NextInvS
<1>2. InvS => ContestedStopped
    BY DEF InvS, RevokedNotLive, ContestedStopped
<1> QED
    BY InitInvS, <1>1, <1>2, PTL DEF Spec

-----------------------------------------------------------------------------
(* FreshAppraisal. A grant takes a pending appraisal from the current epoch and  *)
(* stamps the lease with that epoch; a renewal re-stamps at the current epoch.   *)

InvF == TypeOK /\ FreshAppraisal

LEMMA InitInvF == Init => InvF
BY InitTypeOK DEF Init, InvF, FreshAppraisal, NoLease

LEMMA NextInvF ==
    ASSUME Mut # "M_STALE", InvF, [Next]_vars
    PROVE  InvF'
<1>0. TypeOK /\ TypeOK'
    BY NextTypeOK DEF InvF
<1>1. CASE UNCHANGED vars
    BY <1>0, <1>1 DEF InvF, FreshAppraisal, vars
<1>2. CASE Fence
    BY <1>0, <1>2 DEF Fence, InvF, FreshAppraisal
<1>3. CASE VerifierFlip
    BY <1>0, <1>3 DEF VerifierFlip, InvF, FreshAppraisal
<1>4. ASSUME NEW p \in Principals, Launch(p) PROVE InvF'
    BY <1>0, <1>4 DEF Launch, InvF, FreshAppraisal
<1>5. ASSUME NEW p \in Principals, Kill(p) PROVE InvF'
    BY <1>0, <1>5 DEF Kill, InvF, FreshAppraisal
<1>6. ASSUME NEW p \in Principals, Tamper(p) PROVE InvF'
    BY <1>0, <1>6 DEF Tamper, InvF, FreshAppraisal
<1>7. ASSUME NEW p \in Principals, Appraise(p) PROVE InvF'
    BY <1>0, <1>7 DEF Appraise, InvF, FreshAppraisal
<1>8. ASSUME NEW p \in Principals, Discard(p) PROVE InvF'
    BY <1>0, <1>8 DEF Discard, InvF, FreshAppraisal
<1>9. ASSUME NEW p \in Principals, Grant(p) PROVE InvF'
    <2>1. /\ pending[p].nEpoch = epoch
          /\ lease' = [lease EXCEPT ![p] =
                 [live |-> TRUE,
                  rung |-> IF pending[p].v = "Attested" THEN Declared ELSE 0,
                  prof |-> pending[p].prof, epoch |-> epoch,
                  nEpoch |-> pending[p].nEpoch, gen |-> pending[p].gen]]
        BY <1>9 DEF Grant, FreshEpoch
    <2> QED
        BY <1>0, <2>1 DEF TypeOK, LeaseRec, InvF, FreshAppraisal
<1>10. ASSUME NEW p \in Principals, Renew(p) PROVE InvF'
    <2>1. lease[p].epoch = epoch
        BY <1>10 DEF Renew
    <2>2. \/ lease' = [lease EXCEPT ![p].nEpoch = epoch]
          \/ lease' = [lease EXCEPT ![p] = NoLease]
          \/ lease' = [lease EXCEPT ![p].rung = 0, ![p].nEpoch = epoch]
        BY <1>10 DEF Renew
    <2> QED
        BY <1>0, <2>1, <2>2 DEF TypeOK, LeaseRec, NoLease, InvF, FreshAppraisal
<1>11. ASSUME NEW p \in Principals, Act(p) PROVE InvF'
    BY <1>0, <1>11 DEF Act, InvF, FreshAppraisal
<1>12. ASSUME NEW p \in Principals, EndRound(p) PROVE InvF'
    BY <1>0, <1>12 DEF EndRound, TypeOK, LeaseRec, NoLease, InvF, FreshAppraisal
<1> QED
    BY <1>1, <1>2, <1>3, <1>4, <1>5, <1>6, <1>7, <1>8, <1>9, <1>10, <1>11, <1>12 DEF Next

THEOREM FreshAppraisalAlways ==
    ASSUME Mut # "M_STALE"
    PROVE  Spec => []FreshAppraisal
<1>1. InvF /\ [Next]_vars => InvF'
    BY NextInvF
<1>2. InvF => FreshAppraisal
    BY DEF InvF
<1> QED
    BY InitInvF, <1>1, <1>2, PTL DEF Spec

-----------------------------------------------------------------------------
THEOREM SafeAlways ==
    ASSUME Mut = "none"
    PROVE  Spec => []Safe
<1>1. Spec => []ContainedMeansConfined
    BY ContainedMeansConfinedAlways
<1>2. Spec => []NoSilentDowngrade
    BY NoSilentDowngradeAlways
<1>3. Spec => []ContestedStopped
    BY ContestedStoppedAlways
<1>4. Spec => []FreshAppraisal
    BY FreshAppraisalAlways
<1> QED
    BY <1>1, <1>2, <1>3, <1>4, PTL DEF Safe

-----------------------------------------------------------------------------
(* Why the mutations must fail. The counterexamples are TLC's.                   *)

(* M_HOST: the host may launch a rogue image at any rung, and tamper below 3.   *)
LEMMA MutHostLaunchesRogue ==
    ASSUME Mut = "M_HOST"
    PROVE  HostMayLaunchRogue
BY DEF HostMayLaunchRogue

(* M_HW: at rung 3 a tamper swaps the running image for a rogue one and keeps   *)
(* the guest, instead of killing it.                                             *)
LEMMA MutHwTamperSwaps ==
    ASSUME Mut = "M_HW", Declared = 3, TypeOK, NEW p \in Principals, Tamper(p)
    PROVE  guest' = [guest EXCEPT ![p].img = "rogue"]
BY DEF Tamper

(* M_CONTESTED: a contested verdict is recorded as attested, without revoking.   *)
LEMMA MutContestedHeld ==
    ASSUME Mut = "M_CONTESTED", TypeOK, NEW p \in Principals, Appraise(p), Verdict(p) = "Contested"
    PROVE  pending'[p].v = "Attested" /\ UNCHANGED revoked
BY DEF Appraise, TypeOK, PendRec

(* M_UNBOUND: a lease is granted and acted on without the generation check.      *)
LEMMA MutUnboundIgnoresGeneration ==
    ASSUME Mut = "M_UNBOUND", NEW p \in Principals
    PROVE  SameGuest(p)
BY DEF SameGuest

(* M_PROFILE: a lease above rung 0 counts as contained whatever its profile.     *)
LEMMA MutProfileIgnored ==
    ASSUME Mut = "M_PROFILE", NEW p \in Principals, lease[p].live, lease[p].rung >= 1
    PROVE  Contained(p)
BY DEF Contained

(* M_DOWNGRADE: an unattestable verdict is held as pending and granted at rung 0. *)
LEMMA MutDowngradeHolds ==
    ASSUME Mut = "M_DOWNGRADE", TypeOK, NEW p \in Principals, Appraise(p), Verdict(p) = "Unattestable"
    PROVE  pending'[p].v = "Unattestable"
BY DEF Appraise, TypeOK, PendRec

LEMMA UnattestableGrantsRung0 ==
    ASSUME TypeOK, NEW p \in Principals, Grant(p), pending[p].v = "Unattestable"
    PROVE  lease'[p].live /\ lease'[p].rung = 0
BY DEF Grant, TypeOK, LeaseRec

(* M_RENEWLOW: a renewal that cannot attest lowers the rung and keeps the lease. *)
LEMMA MutRenewLowers ==
    ASSUME Mut = "M_RENEWLOW", TypeOK, NEW p \in Principals, Renew(p), Verdict(p) = "Unattestable"
    PROVE  lease'[p].live /\ lease'[p].rung = 0
BY DEF Renew, TypeOK, LeaseRec

(* M_STALE: an appraisal from an earlier epoch is accepted at grant.             *)
LEMMA MutStaleAccepted ==
    ASSUME Mut = "M_STALE", NEW p \in Principals
    PROVE  FreshEpoch(p)
BY DEF FreshEpoch

=============================================================================
