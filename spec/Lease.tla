------------------------------- MODULE Lease -------------------------------
(* Properties for ADR-0031, the lease schema.                                  *)
(*                                                                             *)
(*   LeaseAuthorityMonotone   §4  renewal never adds authority                 *)
(*   NoActionUnderFencedEpoch §5  a fleet fence: no action at a stale epoch     *)
(*   RevokedStaysStopped      §5  a revoked principal holds no live lease (R3)  *)
(*   Rung0NeverContained      §3  rung 0 is Mediated, always                    *)
(*                                                                             *)
(* Authority is modeled as (alphabet, rung, role). Narrowing the alphabet or   *)
(* lowering the rung subtracts; either one growing is an increase. The round    *)
(* role is not ordered: author and voter admit different actions, so a         *)
(* renewal that changes it is not a narrowing. A grant may increase authority  *)
(* - it is an admit decision at a fresh fence - and a renewal may not.          *)
(* The round number is not modeled: its safety role is topic non-reuse, which  *)
(* is outside this module, and renewal keeps it exactly as it keeps the role.   *)
(*                                                                             *)
(* Mut = "none":    the mechanism as ADR-0031 specifies it.                     *)
(* Mut = "M_RENEW": renewal may issue any authority. §4 must fail.              *)
(* Mut = "M_FENCE": the mechanism admits an action whose lease epoch is stale,  *)
(*                  i.e. revocation does not fence. §5 must fail.               *)
(* Mut = "M_RUNG":  Contained ignores the rung. §3 must fail.                   *)
(* Mut = "M_ROLE":  renewal checks alphabet and rung but not the role, so a    *)
(*                  voter's lease can be renewed as an author's. §4 must fail.  *)
(* Mut = "M_REVOKE": a grant ignores the revocation set, so a revoked          *)
(*                  principal is simply granted again. §5 must fail.            *)
(*                                                                             *)
(* R3: revocation has two tools. RevokeLease(p) ends one principal's lease and *)
(* bars it from later grants; the epoch is untouched. Revoke is the fleet      *)
(* fence. `revoked` holds principals; in the mechanism it holds principals,     *)
(* Persona digests and confinement digests, which a principal stands for here. *)
EXTENDS FiniteSets, Naturals

CONSTANTS Mut, MaxEpoch, MaxFence

Principals == {"p1", "p2"}
Acts       == {"Read", "Emit"}
Rungs      == 0..2
Roles      == {"author", "voter"}

\* A lease. `live` distinguishes a granted lease from no lease at all.
NoLease == [live |-> FALSE, alphabet |-> {}, rung |-> 0, role |-> "none", epoch |-> 0, fence |-> 0]

VARIABLES lease, prev, epoch, fence, acted, staleAdmitted, revoked
vars == <<lease, prev, epoch, fence, acted, staleAdmitted, revoked>>

Init == /\ lease = [p \in Principals |-> NoLease]
        /\ prev  = [p \in Principals |-> NoLease]
        /\ epoch = 0
        /\ fence = 0
        /\ acted = {}
        /\ staleAdmitted = FALSE
        /\ revoked = {}

\* ADR-0031 §4. leaseNext ⊑ leaseCur: narrower alphabet, no higher rung, and the
\* same round role (§1 R1: a renewal that changes the role is a grant).
Narrows(new, old) == new.alphabet \subseteq old.alphabet /\ new.rung <= old.rung
Refines(new, old) == Narrows(new, old) /\ new.role = old.role

\* What the mechanism checks at renewal. M_RENEW checks nothing; M_ROLE drops the role.
RenewalAllowed(new, old) ==
  CASE Mut = "M_RENEW" -> TRUE
    [] Mut = "M_ROLE"  -> Narrows(new, old)
    [] OTHER           -> Refines(new, old)

\* A fresh grant: any authority, at the current epoch and a new fence index.
\* ADR-0031 §2: the lease is round-coterminous, so a principal holds at most one
\* live lease. A grant therefore requires that no lease is live - otherwise a
\* grant could replace a live lease with wider authority and §4 would guarantee
\* nothing, since the wide path would simply avoid renewal.
Grant(p) ==
  /\ ~lease[p].live
  /\ Mut = "M_REVOKE" \/ p \notin revoked        \* R3: the revocation set bars a grant
  /\ fence < MaxFence
  /\ \E a \in SUBSET Acts, r \in Rungs, ro \in Roles :
       lease' = [lease EXCEPT ![p] = [live |-> TRUE, alphabet |-> a, rung |-> r, role |-> ro,
                                      epoch |-> epoch, fence |-> fence + 1]]
  /\ prev' = [prev EXCEPT ![p] = lease[p]]
  /\ fence' = fence + 1
  /\ UNCHANGED <<epoch, acted, staleAdmitted, revoked>>

\* A renewal: same principal, same epoch, new fence, authority may only narrow.
\* The role is drawn freely so that the mechanism's check is what refuses a change.
Renew(p) ==
  /\ lease[p].live
  /\ lease[p].epoch = epoch
  /\ fence < MaxFence
  /\ \E a \in SUBSET Acts, r \in Rungs, ro \in Roles :
       LET new == [live |-> TRUE, alphabet |-> a, rung |-> r, role |-> ro,
                   epoch |-> epoch, fence |-> fence + 1]
       IN  /\ RenewalAllowed(new, lease[p])
           /\ lease' = [lease EXCEPT ![p] = new]
  /\ prev' = [prev EXCEPT ![p] = lease[p]]
  /\ fence' = fence + 1
  /\ UNCHANGED <<epoch, acted, staleAdmitted, revoked>>

\* ADR-0031 §5. The fleet fence increments the epoch, which fences every lease at
\* the old epoch. Leases are left in place: the fence is what rejects them.
Revoke ==
  /\ epoch < MaxEpoch
  /\ epoch' = epoch + 1
  /\ UNCHANGED <<lease, prev, fence, acted, staleAdmitted, revoked>>

\* An action is admitted only under a live lease, within its alphabet, at the
\* current epoch. The epoch check is the fence (ADR-0022 §2).
EpochOK(p) == IF Mut = "M_FENCE" THEN TRUE ELSE lease[p].epoch = epoch

Act(p) ==
  /\ lease[p].live
  /\ EpochOK(p)
  /\ \E a \in lease[p].alphabet :
       acted' = acted \cup {[principal |-> p, act |-> a, atEpoch |-> epoch,
                             leaseEpoch |-> lease[p].epoch]}
  /\ staleAdmitted' = (staleAdmitted \/ lease[p].epoch # epoch)
  /\ UNCHANGED <<lease, prev, epoch, fence, revoked>>

\* ADR-0031 §5 R3. A targeted revocation ends one principal's live lease, if it
\* has one, and bars later grants to it. It is ordered and needs no quorum; it
\* leaves the epoch, and every other principal's lease, untouched.
RevokeLease(p) ==
  /\ p \notin revoked
  /\ revoked' = revoked \cup {p}
  /\ lease' = [lease EXCEPT ![p] = NoLease]
  /\ prev'  = [prev EXCEPT ![p] = NoLease]
  /\ UNCHANGED <<epoch, fence, acted, staleAdmitted>>

\* The round ends: the lease expires with it (§2). A new round begins with a
\* fresh grant, which is where authority may increase.
EndRound(p) ==
  /\ lease[p].live
  /\ lease' = [lease EXCEPT ![p] = NoLease]
  /\ prev'  = [prev EXCEPT ![p] = NoLease]
  /\ UNCHANGED <<epoch, fence, acted, staleAdmitted, revoked>>

Next == Revoke \/ \E p \in Principals : Grant(p) \/ Renew(p) \/ Act(p) \/ EndRound(p) \/ RevokeLease(p)
Spec == Init /\ [][Next]_vars

\* ADR-0031 §3. Confinement is necessary, not sufficient: the provenance axis is
\* unwritten, so this models only the rung half. Rung 0 is Mediated, always.
Contained(p) ==
  /\ lease[p].live
  /\ IF Mut = "M_RUNG" THEN TRUE ELSE lease[p].rung >= 1

\* --- the three properties -------------------------------------------------

\* §4. Every live lease that replaced a live lease for the same principal
\* refines it. A fresh grant after no lease is not a renewal and is exempt.
LeaseAuthorityMonotone ==
  \A p \in Principals :
    (lease[p].live /\ prev[p].live /\ lease[p].epoch = prev[p].epoch)
      => Refines(lease[p], prev[p])

\* §5. No action was ever admitted under a lease whose epoch had been fenced.
NoActionUnderFencedEpoch ==
  /\ ~staleAdmitted
  /\ \A r \in acted : r.leaseEpoch = r.atEpoch

\* §3. A rung-0 principal is never Contained.
Rung0NeverContained ==
  \A p \in Principals : (lease[p].live /\ lease[p].rung = 0) => ~Contained(p)

\* §5 R3. A revoked principal holds no live lease, now or after any later grant.
RevokedStaysStopped == \A p \in revoked : ~lease[p].live

Safe == LeaseAuthorityMonotone /\ NoActionUnderFencedEpoch /\ Rung0NeverContained /\ RevokedStaysStopped

\* --- reachability witnesses: each must be VIOLATED -------------------------
NeverActed    == acted = {}
NeverRenewed  == \A p \in Principals : ~(lease[p].live /\ prev[p].live)
NeverRevoked  == epoch = 0
\* The case §5 is actually about: a lease outlives a revocation.
NeverStaleLease == \A p \in Principals : lease[p].live => lease[p].epoch = epoch
\* Finding 5, the case R3 is about: one principal is revoked while another's lease
\* stays live and usable at the current epoch.
NeverSelectiveRevoke ==
  ~\E p, q \in Principals : p \in revoked /\ q \notin revoked /\ lease[q].live /\ lease[q].epoch = epoch
=============================================================================
