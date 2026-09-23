------------------------------- MODULE Lease -------------------------------
(* Properties for ADR-0031, the lease schema.                                  *)
(*                                                                             *)
(*   LeaseAuthorityMonotone   §4  renewal never adds authority                 *)
(*   NoActionUnderFencedEpoch §5  revocation fences: no action at a stale epoch *)
(*   Rung0NeverContained      §3  rung 0 is Mediated, always                    *)
(*                                                                             *)
(* Authority is modeled as the pair (alphabet, rung). Narrowing the alphabet or *)
(* lowering the rung subtracts; either one growing is an increase. A grant may  *)
(* increase authority - it is an admit decision at a fresh fence - and a        *)
(* renewal may not.                                                            *)
(*                                                                             *)
(* Mut = "none":    the mechanism as ADR-0031 specifies it.                     *)
(* Mut = "M_RENEW": renewal may issue any authority. §4 must fail.              *)
(* Mut = "M_FENCE": the mechanism admits an action whose lease epoch is stale,  *)
(*                  i.e. revocation does not fence. §5 must fail.               *)
(* Mut = "M_RUNG":  Contained ignores the rung. §3 must fail.                   *)
EXTENDS FiniteSets, Naturals

CONSTANTS Mut, MaxEpoch, MaxFence

Principals == {"p1", "p2"}
Acts       == {"Read", "Emit"}
Rungs      == 0..2

\* A lease. `live` distinguishes a granted lease from no lease at all.
NoLease == [live |-> FALSE, alphabet |-> {}, rung |-> 0, epoch |-> 0, fence |-> 0]

VARIABLES lease, prev, epoch, fence, acted, staleAdmitted
vars == <<lease, prev, epoch, fence, acted, staleAdmitted>>

Init == /\ lease = [p \in Principals |-> NoLease]
        /\ prev  = [p \in Principals |-> NoLease]
        /\ epoch = 0
        /\ fence = 0
        /\ acted = {}
        /\ staleAdmitted = FALSE

\* ADR-0031 §4. leaseNext ⊑ leaseCur: narrower alphabet, no higher rung.
Refines(new, old) == new.alphabet \subseteq old.alphabet /\ new.rung <= old.rung

\* A fresh grant: any authority, at the current epoch and a new fence index.
\* ADR-0031 §2: the lease is round-coterminous, so a principal holds at most one
\* live lease. A grant therefore requires that no lease is live - otherwise a
\* grant could replace a live lease with wider authority and §4 would guarantee
\* nothing, since the wide path would simply avoid renewal.
Grant(p) ==
  /\ ~lease[p].live
  /\ fence < MaxFence
  /\ \E a \in SUBSET Acts, r \in Rungs :
       lease' = [lease EXCEPT ![p] = [live |-> TRUE, alphabet |-> a, rung |-> r,
                                      epoch |-> epoch, fence |-> fence + 1]]
  /\ prev' = [prev EXCEPT ![p] = lease[p]]
  /\ fence' = fence + 1
  /\ UNCHANGED <<epoch, acted, staleAdmitted>>

\* A renewal: same principal, same epoch, new fence, authority may only narrow.
Renew(p) ==
  /\ lease[p].live
  /\ lease[p].epoch = epoch
  /\ fence < MaxFence
  /\ \E a \in SUBSET Acts, r \in Rungs :
       LET new == [live |-> TRUE, alphabet |-> a, rung |-> r,
                   epoch |-> epoch, fence |-> fence + 1]
       IN  /\ \/ Mut = "M_RENEW"                 \* mutation: no refinement check
              \/ Refines(new, lease[p])
           /\ lease' = [lease EXCEPT ![p] = new]
  /\ prev' = [prev EXCEPT ![p] = lease[p]]
  /\ fence' = fence + 1
  /\ UNCHANGED <<epoch, acted, staleAdmitted>>

\* ADR-0031 §5. Revocation increments the epoch, which fences every lease at the
\* old epoch. Leases are left in place: the fence is what rejects them.
Revoke ==
  /\ epoch < MaxEpoch
  /\ epoch' = epoch + 1
  /\ UNCHANGED <<lease, prev, fence, acted, staleAdmitted>>

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
  /\ UNCHANGED <<lease, prev, epoch, fence>>

\* The round ends: the lease expires with it (§2). A new round begins with a
\* fresh grant, which is where authority may increase.
EndRound(p) ==
  /\ lease[p].live
  /\ lease' = [lease EXCEPT ![p] = NoLease]
  /\ prev'  = [prev EXCEPT ![p] = NoLease]
  /\ UNCHANGED <<epoch, fence, acted, staleAdmitted>>

Next == Revoke \/ \E p \in Principals : Grant(p) \/ Renew(p) \/ Act(p) \/ EndRound(p)
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

Safe == LeaseAuthorityMonotone /\ NoActionUnderFencedEpoch /\ Rung0NeverContained

\* --- reachability witnesses: each must be VIOLATED -------------------------
NeverActed    == acted = {}
NeverRenewed  == \A p \in Principals : ~(lease[p].live /\ prev[p].live)
NeverRevoked  == epoch = 0
\* The case §5 is actually about: a lease outlives a revocation.
NeverStaleLease == \A p \in Principals : lease[p].live => lease[p].epoch = epoch
=============================================================================
