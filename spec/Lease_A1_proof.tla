---------------------------- MODULE Lease_A1_proof ----------------------------
(* TLAPS proofs of the four invariants Lease_A1.tla states (ADR-0031 §4, A1):   *)
(*                                                                               *)
(*   THEOREM LeaseAuthorityMonotoneAlways  == Spec => []LeaseAuthorityMonotone   *)
(*                                 (Mut \notin {"M_RENEW", "M_ROLE", "M_LOWER"}) *)
(*   THEOREM NoActionUnderFencedEpochAlways == Spec => []NoActionUnderFencedEpoch *)
(*                                 (Mut # "M_FENCE")                             *)
(*   THEOREM Rung0NeverContainedAlways     == Spec => []Rung0NeverContained      *)
(*                                 (Mut # "M_RUNG")                              *)
(*   THEOREM RevokedStaysStoppedAlways     == Spec => []RevokedStaysStopped      *)
(*                                 (Mut # "M_REVOKE")                            *)
(*   THEOREM SafeAlways                    == Spec => []Safe   (Mut = "none")    *)
(*                                                                               *)
(* Each theorem takes as hypothesis only the mutations that break it. Every      *)
(* invariant is inductive with the type invariant below, so the proofs are       *)
(* bookkeeping over seven variables and six actions. The epoch and fence bounds  *)
(* only cut the state space, so MaxEpoch and MaxFence need no assumption.        *)
(* Lease_A1.tla is cited by digest in ADR-0031 and is not edited; this module    *)
(* extends it. The mutations and the six witnesses stay with TLC                 *)
(* (Lease_A1-results-2026.09.28.txt); the lemmas at the end say why each         *)
(* mutation must fail.                                                           *)
(*                                                                               *)
(* Check with:  ../tools/tlapm Lease_A1_proof.tla   (from spec/; see             *)
(*              proof-results.sh for the results file)                           *)
EXTENDS Lease_A1, TLAPS

LeaseRec == [live : BOOLEAN, alphabet : SUBSET Acts, rung : Rungs,
             role : Roles \cup {"none"}, epoch : Nat, fence : Nat]
TypeOK == /\ lease \in [Principals -> LeaseRec]
          /\ prev  \in [Principals -> LeaseRec]
          /\ epoch \in Nat
          /\ fence \in Nat
          /\ revoked \subseteq Principals
          /\ staleAdmitted \in BOOLEAN

LEMMA NoLeaseRec == NoLease \in LeaseRec
BY DEF NoLease, LeaseRec, Rungs, Roles, Acts

-----------------------------------------------------------------------------
(* The type invariant holds under every mutation.                                *)

LEMMA InitTypeOK == Init => TypeOK
BY NoLeaseRec DEF Init, TypeOK

LEMMA NextTypeOK == TypeOK /\ [Next]_vars => TypeOK'
<1> SUFFICES ASSUME TypeOK, [Next]_vars PROVE TypeOK' OBVIOUS
<1>1. CASE UNCHANGED vars
    BY <1>1 DEF TypeOK, vars
<1>2. CASE Revoke
    BY <1>2 DEF Revoke, TypeOK
<1>3. ASSUME NEW p \in Principals, Grant(p) PROVE TypeOK'
    <2>1. PICK a \in SUBSET Acts, r \in Rungs, ro \in Roles :
            lease' = [lease EXCEPT ![p] = [live |-> TRUE, alphabet |-> a, rung |-> r, role |-> ro,
                                           epoch |-> epoch, fence |-> fence + 1]]
        BY <1>3 DEF Grant
    <2>2. [live |-> TRUE, alphabet |-> a, rung |-> r, role |-> ro, epoch |-> epoch, fence |-> fence + 1] \in LeaseRec
        BY DEF TypeOK, LeaseRec
    <2> QED
        BY <1>3, <2>1, <2>2 DEF Grant, TypeOK
<1>4. ASSUME NEW p \in Principals, Renew(p) PROVE TypeOK'
    <2>1. PICK a \in SUBSET Acts, r \in Rungs, ro \in Roles :
            lease' = [lease EXCEPT ![p] = [live |-> TRUE, alphabet |-> a, rung |-> r, role |-> ro,
                                           epoch |-> epoch, fence |-> fence + 1]]
        BY <1>4 DEF Renew
    <2>2. [live |-> TRUE, alphabet |-> a, rung |-> r, role |-> ro, epoch |-> epoch, fence |-> fence + 1] \in LeaseRec
        BY DEF TypeOK, LeaseRec
    <2> QED
        BY <1>4, <2>1, <2>2 DEF Renew, TypeOK
<1>5. ASSUME NEW p \in Principals, Act(p) PROVE TypeOK'
    BY <1>5 DEF Act, TypeOK
<1>6. ASSUME NEW p \in Principals, EndRound(p) PROVE TypeOK'
    BY <1>6, NoLeaseRec DEF EndRound, TypeOK
<1>7. ASSUME NEW p \in Principals, RevokeLease(p) PROVE TypeOK'
    BY <1>7, NoLeaseRec DEF RevokeLease, TypeOK
<1> QED
    BY <1>1, <1>2, <1>3, <1>4, <1>5, <1>6, <1>7 DEF Next

-----------------------------------------------------------------------------
(* LeaseAuthorityMonotone. A grant's predecessor is not live; a renewal under    *)
(* the specified rule refines its predecessor; nothing else makes both live.     *)

LEMMA RenewRefines ==
    ASSUME Mut # "M_RENEW", Mut # "M_ROLE", Mut # "M_LOWER", NEW new, NEW old, RenewalAllowed(new, old)
    PROVE  Refines(new, old)
BY DEF RenewalAllowed

LEMMA NextMonotone ==
    ASSUME Mut # "M_RENEW", Mut # "M_ROLE", Mut # "M_LOWER",
           TypeOK, LeaseAuthorityMonotone, [Next]_vars
    PROVE  LeaseAuthorityMonotone'
<1>1. CASE UNCHANGED vars
    BY <1>1 DEF LeaseAuthorityMonotone, Refines, Narrows, vars
<1>2. CASE Revoke
    BY <1>2 DEF Revoke, LeaseAuthorityMonotone, Refines, Narrows
<1>3. ASSUME NEW p \in Principals, Grant(p) PROVE LeaseAuthorityMonotone'
    <2>1. ~lease[p].live /\ prev' = [prev EXCEPT ![p] = lease[p]]
        BY <1>3 DEF Grant
    <2>2. \A q \in Principals : q # p => lease'[q] = lease[q]
        BY <1>3 DEF Grant, TypeOK
    <2> QED
        BY <2>1, <2>2 DEF TypeOK, LeaseAuthorityMonotone, Refines, Narrows
<1>4. ASSUME NEW p \in Principals, Renew(p) PROVE LeaseAuthorityMonotone'
    <2>1. PICK a \in SUBSET Acts, r \in Rungs, ro \in Roles :
            LET new == [live |-> TRUE, alphabet |-> a, rung |-> r, role |-> ro,
                        epoch |-> epoch, fence |-> fence + 1]
            IN  /\ RenewalAllowed(new, lease[p])
                /\ lease' = [lease EXCEPT ![p] = new]
        BY <1>4 DEF Renew
    <2>2. prev' = [prev EXCEPT ![p] = lease[p]]
        BY <1>4 DEF Renew
    <2>3. Refines(lease'[p], prev'[p])
        BY <2>1, <2>2, RenewRefines DEF TypeOK
    <2>4. \A q \in Principals : q # p => lease'[q] = lease[q] /\ prev'[q] = prev[q]
        BY <2>1, <2>2 DEF TypeOK
    <2> QED
        BY <2>3, <2>4 DEF TypeOK, LeaseAuthorityMonotone, Refines, Narrows
<1>5. ASSUME NEW p \in Principals, Act(p) PROVE LeaseAuthorityMonotone'
    BY <1>5 DEF Act, LeaseAuthorityMonotone, Refines, Narrows
<1>6. ASSUME NEW p \in Principals, EndRound(p) PROVE LeaseAuthorityMonotone'
    <2>1. lease' = [lease EXCEPT ![p] = NoLease] /\ prev' = [prev EXCEPT ![p] = NoLease]
        BY <1>6 DEF EndRound
    <2> QED
        BY <2>1 DEF TypeOK, NoLease, LeaseAuthorityMonotone, Refines, Narrows
<1>7. ASSUME NEW p \in Principals, RevokeLease(p) PROVE LeaseAuthorityMonotone'
    <2>1. lease' = [lease EXCEPT ![p] = NoLease] /\ prev' = [prev EXCEPT ![p] = NoLease]
        BY <1>7 DEF RevokeLease
    <2> QED
        BY <2>1 DEF TypeOK, NoLease, LeaseAuthorityMonotone, Refines, Narrows
<1> QED
    BY <1>1, <1>2, <1>3, <1>4, <1>5, <1>6, <1>7 DEF Next

THEOREM LeaseAuthorityMonotoneAlways ==
    ASSUME Mut # "M_RENEW", Mut # "M_ROLE", Mut # "M_LOWER"
    PROVE  Spec => []LeaseAuthorityMonotone
<1>1. (TypeOK /\ LeaseAuthorityMonotone) /\ [Next]_vars => (TypeOK /\ LeaseAuthorityMonotone)'
    BY NextTypeOK, NextMonotone
<1>2. Init => TypeOK /\ LeaseAuthorityMonotone
    BY InitTypeOK, NoLeaseRec DEF Init, LeaseAuthorityMonotone, NoLease
<1> QED
    BY <1>1, <1>2, PTL DEF Spec

-----------------------------------------------------------------------------
(* NoActionUnderFencedEpoch. An act under the specified check carries the        *)
(* current epoch as both its lease epoch and its acting epoch.                   *)

LEMMA NextFenced ==
    ASSUME Mut # "M_FENCE", NoActionUnderFencedEpoch, [Next]_vars
    PROVE  NoActionUnderFencedEpoch'
<1>1. CASE UNCHANGED vars
    BY <1>1 DEF NoActionUnderFencedEpoch, vars
<1>2. CASE Revoke
    BY <1>2 DEF Revoke, NoActionUnderFencedEpoch
<1>3. ASSUME NEW p \in Principals, Grant(p) PROVE NoActionUnderFencedEpoch'
    BY <1>3 DEF Grant, NoActionUnderFencedEpoch
<1>4. ASSUME NEW p \in Principals, Renew(p) PROVE NoActionUnderFencedEpoch'
    BY <1>4 DEF Renew, NoActionUnderFencedEpoch
<1>5. ASSUME NEW p \in Principals, Act(p) PROVE NoActionUnderFencedEpoch'
    <2>1. lease[p].epoch = epoch
        BY <1>5 DEF Act, EpochOK
    <2>2. PICK a \in lease[p].alphabet :
            acted' = acted \cup {[principal |-> p, act |-> a, atEpoch |-> epoch, leaseEpoch |-> lease[p].epoch]}
        BY <1>5 DEF Act
    <2>3. staleAdmitted' = (staleAdmitted \/ lease[p].epoch # epoch)
        BY <1>5 DEF Act
    <2> QED
        BY <2>1, <2>2, <2>3 DEF NoActionUnderFencedEpoch
<1>6. ASSUME NEW p \in Principals, EndRound(p) PROVE NoActionUnderFencedEpoch'
    BY <1>6 DEF EndRound, NoActionUnderFencedEpoch
<1>7. ASSUME NEW p \in Principals, RevokeLease(p) PROVE NoActionUnderFencedEpoch'
    BY <1>7 DEF RevokeLease, NoActionUnderFencedEpoch
<1> QED
    BY <1>1, <1>2, <1>3, <1>4, <1>5, <1>6, <1>7 DEF Next

THEOREM NoActionUnderFencedEpochAlways ==
    ASSUME Mut # "M_FENCE"
    PROVE  Spec => []NoActionUnderFencedEpoch
<1>1. NoActionUnderFencedEpoch /\ [Next]_vars => NoActionUnderFencedEpoch'
    BY NextFenced
<1>2. Init => NoActionUnderFencedEpoch
    BY DEF Init, NoActionUnderFencedEpoch
<1> QED
    BY <1>1, <1>2, PTL DEF Spec

-----------------------------------------------------------------------------
(* Rung0NeverContained holds in every state under the specified Contained: a     *)
(* rung-0 lease is excluded by definition, so no induction is needed.            *)

LEMMA Rung0Valid ==
    ASSUME Mut # "M_RUNG"
    PROVE  Rung0NeverContained
BY DEF Rung0NeverContained, Contained

THEOREM Rung0NeverContainedAlways ==
    ASSUME Mut # "M_RUNG"
    PROVE  Spec => []Rung0NeverContained
<1>1. Rung0NeverContained
    BY Rung0Valid
<1> QED
    BY <1>1, PTL

-----------------------------------------------------------------------------
(* RevokedStaysStopped. A grant under the specified guard refuses a revoked      *)
(* principal; a renewal needs a live lease, which a revoked principal lacks.     *)

LEMMA NextRevoked ==
    ASSUME Mut # "M_REVOKE", TypeOK, RevokedStaysStopped, [Next]_vars
    PROVE  RevokedStaysStopped'
<1>1. CASE UNCHANGED vars
    BY <1>1 DEF RevokedStaysStopped, vars
<1>2. CASE Revoke
    BY <1>2 DEF Revoke, RevokedStaysStopped
<1>3. ASSUME NEW p \in Principals, Grant(p) PROVE RevokedStaysStopped'
    <2>1. p \notin revoked /\ UNCHANGED revoked
        BY <1>3 DEF Grant
    <2>2. \A q \in Principals : q # p => lease'[q] = lease[q]
        BY <1>3 DEF Grant, TypeOK
    <2> QED
        BY <2>1, <2>2 DEF TypeOK, RevokedStaysStopped
<1>4. ASSUME NEW p \in Principals, Renew(p) PROVE RevokedStaysStopped'
    <2>1. lease[p].live /\ UNCHANGED revoked
        BY <1>4 DEF Renew
    <2>2. p \notin revoked
        BY <2>1 DEF RevokedStaysStopped
    <2>3. \A q \in Principals : q # p => lease'[q] = lease[q]
        BY <1>4 DEF Renew, TypeOK
    <2> QED
        BY <2>1, <2>2, <2>3 DEF TypeOK, RevokedStaysStopped
<1>5. ASSUME NEW p \in Principals, Act(p) PROVE RevokedStaysStopped'
    BY <1>5 DEF Act, RevokedStaysStopped
<1>6. ASSUME NEW p \in Principals, EndRound(p) PROVE RevokedStaysStopped'
    BY <1>6 DEF EndRound, TypeOK, NoLease, RevokedStaysStopped
<1>7. ASSUME NEW p \in Principals, RevokeLease(p) PROVE RevokedStaysStopped'
    BY <1>7 DEF RevokeLease, TypeOK, NoLease, RevokedStaysStopped
<1> QED
    BY <1>1, <1>2, <1>3, <1>4, <1>5, <1>6, <1>7 DEF Next

THEOREM RevokedStaysStoppedAlways ==
    ASSUME Mut # "M_REVOKE"
    PROVE  Spec => []RevokedStaysStopped
<1>1. (TypeOK /\ RevokedStaysStopped) /\ [Next]_vars => (TypeOK /\ RevokedStaysStopped)'
    BY NextTypeOK, NextRevoked
<1>2. Init => TypeOK /\ RevokedStaysStopped
    BY InitTypeOK DEF Init, RevokedStaysStopped
<1> QED
    BY <1>1, <1>2, PTL DEF Spec

-----------------------------------------------------------------------------
THEOREM SafeAlways ==
    ASSUME Mut = "none"
    PROVE  Spec => []Safe
<1>1. Spec => []LeaseAuthorityMonotone
    BY LeaseAuthorityMonotoneAlways
<1>2. Spec => []NoActionUnderFencedEpoch
    BY NoActionUnderFencedEpochAlways
<1>3. Spec => []Rung0NeverContained
    BY Rung0NeverContainedAlways
<1>4. Spec => []RevokedStaysStopped
    BY RevokedStaysStoppedAlways
<1> QED
    BY <1>1, <1>2, <1>3, <1>4, PTL DEF Safe

-----------------------------------------------------------------------------
(* Why the mutations must fail. The counterexamples are TLC's.                   *)

(* M_RENEW allows any renewal; M_ROLE ignores the role; M_LOWER accepts a lower  *)
(* rung. Each admits a renewal that does not refine its predecessor.             *)
LEMMA MutRenewAllowsAll ==
    ASSUME Mut = "M_RENEW", NEW new, NEW old
    PROVE  RenewalAllowed(new, old)
BY DEF RenewalAllowed

LEMMA MutRoleIgnored ==
    ASSUME Mut = "M_ROLE", NEW new, NEW old, Narrows(new, old), new.rung = old.rung
    PROVE  RenewalAllowed(new, old)
BY DEF RenewalAllowed

LEMMA MutLowerAccepted ==
    ASSUME Mut = "M_LOWER", NEW new, NEW old,
           Narrows(new, old), new.rung <= old.rung, new.role = old.role
    PROVE  RenewalAllowed(new, old)
BY DEF RenewalAllowed, LowerOrSame

(* M_FENCE drops the epoch check, so a stale lease acts.                         *)
LEMMA MutFenceIgnoresEpoch ==
    ASSUME Mut = "M_FENCE", NEW p \in Principals
    PROVE  EpochOK(p)
BY DEF EpochOK

(* M_RUNG calls every live lease contained, rung 0 included.                     *)
LEMMA MutRungContainsAll ==
    ASSUME Mut = "M_RUNG", NEW p \in Principals, lease[p].live
    PROVE  Contained(p)
BY DEF Contained

(* M_REVOKE drops the revocation guard, so a revoked principal can be granted    *)
(* again while the fence has room.                                               *)
LEMMA MutRevokeGrantsAgain ==
    ASSUME Mut = "M_REVOKE", TypeOK, NEW p \in Principals,
           p \in revoked, ~lease[p].live, fence < MaxFence
    PROVE  ENABLED Grant(p)
BY ExpandENABLED DEF Grant, TypeOK, Rungs, Roles, Acts

=============================================================================
