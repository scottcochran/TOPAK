---------------------------- MODULE Operators ----------------------------
(* The operator as a principal: ADR-0050 (Proposed), its ratification          *)
(* condition (§10). A principal's first lease comes from a quorum. An operator *)
(* holding a live lease, with a live peer, makes successor grants and renewals *)
(* that never widen. A deny needs no lease: it needs the operator's Persona in *)
(* force and a credential that is fresh, by the lease or by a sign-on          *)
(* assertion (R1).                                                             *)
(*                                                                             *)
(* The mechanism sees keys, leases and assertions. This module also carries,   *)
(* as ghost state the mechanism never reads, whether the identity provider     *)
(* still vouches for the person behind a key (`vouched`), and for every lease  *)
(* whether its chain of grants began at a quorum (`root`).                     *)
(*                                                                             *)
(*   FirstLeaseHasAQuorum      every live lease descends from a seating        *)
(*   LeaseWithinSeating        no lease is wider than the quorum's grant       *)
(*   SuccessorNeverWidens      every successor grant is its predecessor's      *)
(*                             width or narrower                               *)
(*   NoAddWithoutLiveLeaseAndPeer  every add was made under a live lease with  *)
(*                             another operator's lease live                   *)
(*   ExpiredOperatorOnlyDenies the first half of that, by itself               *)
(*   NoSelfRegrant             no operator regranted or renewed itself         *)
(*   OperatorLeaseWasVouched   a live operator lease was attested, at its last *)
(*                             boundary, by a provider that vouched            *)
(*   NoDenyOnAStaleKey         no deny was admitted from an operator with no   *)
(*                             live lease whose provider did not vouch         *)
(*   NoDenyByRevoked           no deny was admitted from a revoked Persona     *)
(*   EveryStopIsAttributed     every stop names an operator                    *)
(*   RevokedStaysOut           a revoked principal holds no live lease         *)
(*   FleetFenceNeedsLease      no fleet fence was admitted from an operator    *)
(*                             with no live lease (R5)                         *)
(*   DenyAlwaysAvailable       an operator whose Persona is in force and whose *)
(*                             provider vouches can revoke any principal in    *)
(*                             force, in every state                           *)
(*                                                                             *)
(* A lease's `width` stands for its authority: a larger width is a wider       *)
(* alphabet. Persona, bundle and confinement are not modelled apart from it; a *)
(* change of any of them is a first lease (ADR-0050 §2) and is a `Seat` here.  *)
(*                                                                             *)
(* Declared premises, not modelled: the identity provider is honest, so an     *)
(* assertion verifies exactly when the provider vouches (a compromised         *)
(* provider is ADR-0050 §8's, and one provider for all is D-0050-2); one       *)
(* domain; the task and its label (§5); what a peer has read (§6 reads         *)
(* presence only). `adds` and `stops` hold the last admitted add and deny, not *)
(* the history: every admitted one is the last in the state after it, so an    *)
(* invariant over the last is an invariant over all. Time is not modelled: a lease lapses whenever `Expire`      *)
(* says, and a provider withdraws whenever `Unvouch` says.                     *)
(*                                                                             *)
(* Mut = "none":        ADR-0050 as revised at R5.                             *)
(* Mut = "M_NOSEAT":    an operator may grant a first lease, as the reference  *)
(*                      does today. Must break FirstLeaseHasAQuorum and        *)
(*                      LeaseWithinSeating; and, with three operators,         *)
(*                      OperatorLeaseWasVouched, because that grant reads no   *)
(*                      assertion (found writing the proof; with two operators *)
(*                      the grantor of an operator's lease has no live peer).  *)
(* Mut = "M_WIDEN":     a successor may be wider. Must break                   *)
(*                      SuccessorNeverWidens and LeaseWithinSeating.           *)
(* Mut = "M_PEER":      the peer rule is dropped. Must break                   *)
(*                      NoAddWithoutLiveLeaseAndPeer and not                   *)
(*                      ExpiredOperatorOnlyDenies.                             *)
(* Mut = "M_LAPSEDADD": an operator with no live lease may add. Must break     *)
(*                      ExpiredOperatorOnlyDenies.                             *)
(* Mut = "M_SELF":      an operator may regrant itself. Must break             *)
(*                      NoSelfRegrant.                                         *)
(* Mut = "M_NOATTEST":  the sign-on assertion is not read at a lease boundary. *)
(*                      Must break OperatorLeaseWasVouched.                    *)
(* Mut = "M_STALEKEY":  a deny by key alone with no live lease: ADR-0050       *)
(*                      before R1. Must break NoDenyOnAStaleKey.               *)
(* Mut = "M_DENYLEASE": a deny needs a live lease. Must break                  *)
(*                      DenyAlwaysAvailable.                                   *)
(* Mut = "M_ANON":      a stop with no author, as the socket allows today.     *)
(*                      Must break EveryStopIsAttributed.                      *)
(* Mut = "M_LAPSEDFENCE": an operator with no live lease may fence the fleet,  *)
(*                      on a fresh assertion: ADR-0050 before R5. Must break   *)
(*                      FleetFenceNeedsLease and nothing else.                 *)
EXTENDS Integers, FiniteSets

CONSTANTS Mut, Ops, MaxRound

Workers    == {"w"}
Principals == Ops \cup Workers
MaxW       == 2

NoLease == [live |-> FALSE, width |-> 0, round |-> 0, root |-> "none", attested |-> FALSE]

VARIABLES
  seating,   \* the width the quorum last seated each principal at; 0 is never seated
  inForce,   \* the principal's Persona is promoted and not revoked
  lease,
  vouched,   \* the provider vouches for the person behind an operator's key (ghost)
  adds,      \* the last admitted add, with what was true when it was admitted: {} or one record
  stops,     \* the last admitted deny, likewise
  fenced     \* a fleet fence has happened

vars == <<seating, inForce, lease, vouched, adds, stops, fenced>>

Init ==
  /\ seating = [p \in Principals |-> 0]
  /\ inForce = [p \in Principals |-> TRUE]
  /\ lease = [p \in Principals |-> NoLease]
  /\ vouched = [o \in Ops |-> TRUE]
  /\ adds = {}
  /\ stops = {}
  /\ fenced = FALSE

Live(p)     == lease[p].live
PeerLive(o) == \E q \in Ops \ {o} : Live(q)

\* The sign-on assertion read at a lease boundary. The provider is honest: it verifies
\* exactly when the provider vouches. A worker's Persona attestation is not modelled.
Attests(p) == IF p \in Ops THEN vouched[p] \/ Mut = "M_NOATTEST" ELSE TRUE
VouchedAt(p) == IF p \in Ops THEN vouched[p] ELSE FALSE

\* A quorum completes a seating: an anchor issuance at genesis, or a promotion. The
\* mechanism grants the first lease. No operator is involved.
Seat(p, w) ==
  /\ inForce[p] /\ ~Live(p) /\ lease[p].round < MaxRound
  /\ Attests(p)
  /\ seating' = [seating EXCEPT ![p] = w]
  /\ lease' = [lease EXCEPT ![p] = [live |-> TRUE, width |-> w, round |-> @.round + 1,
                                    root |-> "quorum", attested |-> VouchedAt(p)]]
  /\ UNCHANGED <<inForce, vouched, adds, stops, fenced>>

\* What every add needs of the operator who makes it.
MayAdd(o, p) ==
  /\ inForce[o]
  /\ (Live(o) \/ Mut = "M_LAPSEDADD")
  /\ (PeerLive(o) \/ Mut = "M_PEER")
  /\ (p # o \/ Mut = "M_SELF")

AddRecord(k, o, p, prev, new) ==
  [kind |-> k, by |-> o, target |-> p, byLive |-> Live(o), peerLive |-> PeerLive(o), prev |-> prev, new |-> new]

\* A successor grant: the principal's next round, nothing wider.
Regrant(o, p, w) ==
  /\ MayAdd(o, p)
  /\ inForce[p] /\ ~Live(p) /\ lease[p].round > 0 /\ lease[p].round < MaxRound
  /\ (w <= lease[p].width \/ Mut = "M_WIDEN")
  /\ Attests(p)
  /\ lease' = [lease EXCEPT ![p] = [live |-> TRUE, width |-> w, round |-> @.round + 1,
                                    root |-> @.root, attested |-> VouchedAt(p)]]
  /\ adds' = {AddRecord("regrant", o, p, lease[p].width, w)}
  /\ UNCHANGED <<seating, inForce, vouched, stops, fenced>>

\* A renewal: the same round. For an operator it re-reads the assertion; one that does not
\* verify is a refused renewal, and the lease lapses by `Expire`.
Renew(o, p) ==
  /\ MayAdd(o, p)
  /\ inForce[p] /\ Live(p)
  /\ Attests(p)
  /\ lease' = [lease EXCEPT ![p].attested = VouchedAt(p)]
  /\ adds' = {AddRecord("renew", o, p, lease[p].width, lease[p].width)}
  /\ UNCHANGED <<seating, inForce, vouched, stops, fenced>>

\* The reference today: an operator grants a first lease, with no seating behind it.
Grant(o, p, w) ==
  /\ Mut = "M_NOSEAT"
  /\ MayAdd(o, p)
  /\ inForce[p] /\ ~Live(p) /\ lease[p].round < MaxRound
  /\ lease' = [lease EXCEPT ![p] = [live |-> TRUE, width |-> w, round |-> @.round + 1,
                                    root |-> "none", attested |-> VouchedAt(p)]]
  /\ adds' = {AddRecord("grant", o, p, 0, w)}
  /\ UNCHANGED <<seating, inForce, vouched, stops, fenced>>

\* What every deny needs: the Persona in force, and a fresh credential, by the lease or by
\* a sign-on assertion naming the current fence (R1).
MayDeny(o) ==
  /\ inForce[o]
  /\ (Live(o) \/ vouched[o] \/ Mut = "M_STALEKEY")
  /\ (Live(o) \/ Mut # "M_DENYLEASE")

StopRecord(k, o) == [kind |-> k, by |-> o, byLive |-> Live(o), vouched |-> vouched[o], inForce |-> inForce[o]]

EndRound(o, p) ==
  /\ MayDeny(o) /\ Live(p)
  /\ lease' = [lease EXCEPT ![p].live = FALSE]
  /\ stops' = {StopRecord("end", o)}
  /\ UNCHANGED <<seating, inForce, vouched, adds, fenced>>

Revoke(o, p) ==
  /\ MayDeny(o) /\ inForce[p]
  /\ inForce' = [inForce EXCEPT ![p] = FALSE]
  /\ lease' = [lease EXCEPT ![p].live = FALSE]
  /\ stops' = {StopRecord("revoke", o)}
  /\ UNCHANGED <<seating, vouched, adds, fenced>>

\* The fleet fence is the one deny that needs a live lease (R5): a lapsed operator stops its
\* own domain and not the fleet.
FenceEpoch(o) ==
  /\ MayDeny(o)
  /\ (Live(o) \/ Mut = "M_LAPSEDFENCE")
  /\ lease' = [p \in Principals |-> [lease[p] EXCEPT !.live = FALSE]]
  /\ stops' = {StopRecord("fence", o)}
  /\ fenced' = TRUE
  /\ UNCHANGED <<seating, inForce, vouched, adds>>

\* The socket today: a fence that names nobody.
AnonFence ==
  /\ Mut = "M_ANON"
  /\ lease' = [p \in Principals |-> [lease[p] EXCEPT !.live = FALSE]]
  /\ stops' = {[kind |-> "fence", by |-> "nobody", byLive |-> TRUE, vouched |-> TRUE, inForce |-> TRUE]}
  /\ fenced' = TRUE
  /\ UNCHANGED <<seating, inForce, vouched, adds>>

\* The environment: a lease lapses; a provider stops or resumes vouching for a person.
Expire(p)  == Live(p) /\ lease' = [lease EXCEPT ![p].live = FALSE]
              /\ UNCHANGED <<seating, inForce, vouched, adds, stops, fenced>>
Unvouch(o) == vouched[o] /\ vouched' = [vouched EXCEPT ![o] = FALSE]
              /\ UNCHANGED <<seating, inForce, lease, adds, stops, fenced>>
Vouch(o)   == ~vouched[o] /\ vouched' = [vouched EXCEPT ![o] = TRUE]
              /\ UNCHANGED <<seating, inForce, lease, adds, stops, fenced>>

Next ==
  \/ \E p \in Principals, w \in 1..MaxW : Seat(p, w)
  \/ \E o \in Ops, p \in Principals, w \in 1..MaxW : Regrant(o, p, w) \/ Grant(o, p, w)
  \/ \E o \in Ops, p \in Principals : Renew(o, p) \/ EndRound(o, p) \/ Revoke(o, p)
  \/ \E o \in Ops : FenceEpoch(o) \/ Unvouch(o) \/ Vouch(o)
  \/ \E p \in Principals : Expire(p)
  \/ AnonFence

Spec == Init /\ [][Next]_vars

\* --- the properties ----------------------------------------------------------

FirstLeaseHasAQuorum == \A p \in Principals : Live(p) => lease[p].root = "quorum"

LeaseWithinSeating == \A p \in Principals : Live(p) => lease[p].width <= seating[p]

SuccessorNeverWidens == \A a \in adds : a.kind = "regrant" => a.new <= a.prev

ExpiredOperatorOnlyDenies == \A a \in adds : a.byLive

NoAddWithoutLiveLeaseAndPeer == \A a \in adds : a.byLive /\ a.peerLive

NoSelfRegrant == \A a \in adds : a.by # a.target

OperatorLeaseWasVouched == \A o \in Ops : Live(o) => lease[o].attested

NoDenyOnAStaleKey == \A s \in stops : s.byLive \/ s.vouched

NoDenyByRevoked == \A s \in stops : s.inForce

EveryStopIsAttributed == \A s \in stops : s.by \in Ops

RevokedStaysOut == \A p \in Principals : ~inForce[p] => ~Live(p)

FleetFenceNeedsLease == \A s \in stops : s.kind = "fence" => s.byLive

DenyAlwaysAvailable ==
  \A o \in Ops : (inForce[o] /\ vouched[o]) => \A p \in Principals : inForce[p] => ENABLED Revoke(o, p)

Safe == /\ FirstLeaseHasAQuorum /\ LeaseWithinSeating /\ SuccessorNeverWidens
        /\ NoAddWithoutLiveLeaseAndPeer /\ NoSelfRegrant /\ OperatorLeaseWasVouched
        /\ NoDenyOnAStaleKey /\ NoDenyByRevoked /\ EveryStopIsAttributed /\ RevokedStaysOut
        /\ FleetFenceNeedsLease /\ DenyAlwaysAvailable

\* --- reachability witnesses: each must be VIOLATED unless the row says otherwise

\* An operator continues a quorum's grant: a successor grant to a worker is admitted.
NeverWorkerRegrant == \A a \in adds : ~(a.kind = "regrant" /\ a.target \in Workers)
\* A successor is narrower than its predecessor.
NeverNarrowed == \A a \in adds : a.new = a.prev
\* An operator whose lease has lapsed denies, on a fresh assertion.
NeverLapsedDeny == \A s \in stops : s.byLive
\* The stale-key state is reached: a Persona in force, no live lease, no provider.
NeverStaleKey == \A o \in Ops : ~(inForce[o] /\ ~Live(o) /\ ~vouched[o])
\* The peer rule bites: an operator holds a live lease and no peer does.
NeverPeerless == \A o \in Ops : ~(Live(o) /\ ~PeerLive(o))
\* A lease exists again after a fleet fence: a quorum can recover.
NeverRecovered == ~(fenced /\ \E p \in Principals : Live(p))
\* An operator's own next round is granted by a peer. With two operators this HOLDS: the
\* only peer of the grantor is the target, whose lease is not live. It takes three.
NeverOperatorRegranted == \A a \in adds : ~(a.kind = "regrant" /\ a.target \in Ops)
\* A fleet fence happens, and a lapsed operator revokes: the stop is not vacuous either way.
NeverFenced == ~fenced
NeverLapsedRevoke == \A s \in stops : ~(s.kind = "revoke" /\ ~s.byLive)
\* A peer renews an operator's lease. Reached with two.
NeverOperatorRenewed == \A a \in adds : ~(a.kind = "renew" /\ a.target \in Ops)
=============================================================================
