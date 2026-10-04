------------------------- MODULE Operators_proof -------------------------
(* TLAPS proofs of the twelve invariants Operators.tla states (ADR-0050,         *)
(* Proposed: the operator as a principal), for every set of operators and every  *)
(* round bound:                                                                  *)
(*                                                                               *)
(*   FirstLeaseHasAQuorumAlways          (Mut # "M_NOSEAT")                      *)
(*   LeaseWithinSeatingAlways            (Mut \notin {"M_NOSEAT", "M_WIDEN"})    *)
(*   SuccessorNeverWidensAlways          (Mut # "M_WIDEN")                       *)
(*   ExpiredOperatorOnlyDeniesAlways     (Mut # "M_LAPSEDADD")                   *)
(*   NoAddWithoutLiveLeaseAndPeerAlways  (Mut \notin {"M_LAPSEDADD", "M_PEER"})  *)
(*   NoSelfRegrantAlways                 (Mut # "M_SELF")                        *)
(*   OperatorLeaseWasVouchedAlways       (Mut \notin {"M_NOATTEST", "M_NOSEAT"}) *)
(*   NoDenyOnAStaleKeyAlways             (Mut # "M_STALEKEY")                    *)
(*   NoDenyByRevokedAlways               (every Mut)                             *)
(*   EveryStopIsAttributedAlways         (Mut # "M_ANON")                        *)
(*   RevokedStaysOutAlways               (every Mut)                             *)
(*   DenyAlwaysAvailableAlways           (Mut # "M_DENYLEASE")                   *)
(*   SafeAlways == Spec => []Safe        (Mut = "none")                          *)
(*                                                                               *)
(* Each theorem takes as hypothesis only the mutations that break it. Writing    *)
(* them found one the TLC rows had not: M_NOSEAT also breaks                     *)
(* OperatorLeaseWasVouched, because the reference's first grant reads no         *)
(* assertion. TLC at two operators could not reach it (the grantor of an         *)
(* operator's lease has no live peer there) and reaches it at three              *)
(* (Operators-results, rows nsv and nsv3).                                       *)
(*                                                                               *)
(* No assumption is made on the constants: Ops may be any set and MaxRound any   *)
(* value, where TLC ran two or three operators and two rounds. The inductive     *)
(* invariants are a type invariant that holds under every mutation, and for each *)
(* property the property itself or a statement of it over every lease and not    *)
(* only the live ones: every lease that was ever granted has a quorum at its     *)
(* root, and no lease is wider than its seating. DenyAlwaysAvailable is true in  *)
(* every state and needs no induction.                                           *)
(*                                                                               *)
(* Operators.tla is not edited; this module extends it. The mutations and the    *)
(* witnesses stay with TLC; the lemmas at the end say what each mutation admits. *)
(*                                                                               *)
(* Check with:  ../tools/tlapm Operators_proof.tla   (from spec/; see            *)
(*              proof-results.sh for the results file)                           *)
EXTENDS Operators, TLAPS

LeaseType == [live : BOOLEAN, width : 0..MaxW, round : Nat, root : {"none", "quorum"}, attested : BOOLEAN]

TypeOK ==
  /\ seating \in [Principals -> 0..MaxW]
  /\ inForce \in [Principals -> BOOLEAN]
  /\ lease \in [Principals -> LeaseType]
  /\ vouched \in [Ops -> BOOLEAN]

\* Every lease that was ever granted began at a quorum.
Rooted == \A p \in Principals : lease[p].round > 0 => lease[p].root = "quorum"
\* A live lease was granted.
LiveGranted == \A p \in Principals : Live(p) => lease[p].round > 0
\* No lease, live or not, is wider than the seating.
Within == \A p \in Principals : lease[p].width <= seating[p]

LEMMA NoLeaseTyped == NoLease \in LeaseType
BY DEF NoLease, LeaseType, MaxW

LEMMA VouchedAtBool == ASSUME TypeOK, NEW p \in Principals PROVE VouchedAt(p) \in BOOLEAN
BY DEF VouchedAt, TypeOK

-----------------------------------------------------------------------------
(* The type invariant, under every mutation.                                     *)

LEMMA TypeInit == Init => TypeOK
BY NoLeaseTyped DEF Init, TypeOK, MaxW

LEMMA TypeNext == ASSUME TypeOK, [Next]_vars PROVE TypeOK'
<1>1. CASE UNCHANGED vars
    BY <1>1 DEF vars, TypeOK
<1>2. ASSUME NEW p \in Principals, NEW w \in 1..MaxW, Seat(p, w) PROVE TypeOK'
    BY <1>2, VouchedAtBool DEF Seat, TypeOK, LeaseType, MaxW
<1>3. ASSUME NEW o \in Ops, NEW p \in Principals, NEW w \in 1..MaxW, Regrant(o, p, w) PROVE TypeOK'
    BY <1>3, VouchedAtBool DEF Regrant, TypeOK, LeaseType, MaxW
<1>4. ASSUME NEW o \in Ops, NEW p \in Principals, NEW w \in 1..MaxW, Grant(o, p, w) PROVE TypeOK'
    BY <1>4, VouchedAtBool DEF Grant, TypeOK, LeaseType, MaxW
<1>5. ASSUME NEW o \in Ops, NEW p \in Principals, Renew(o, p) PROVE TypeOK'
    BY <1>5, VouchedAtBool DEF Renew, TypeOK, LeaseType
<1>6. ASSUME NEW o \in Ops, NEW p \in Principals, EndRound(o, p) PROVE TypeOK'
    BY <1>6 DEF EndRound, TypeOK, LeaseType
<1>7. ASSUME NEW o \in Ops, NEW p \in Principals, Revoke(o, p) PROVE TypeOK'
    BY <1>7 DEF Revoke, TypeOK, LeaseType
<1>8. ASSUME NEW o \in Ops, FenceEpoch(o) PROVE TypeOK'
    BY <1>8 DEF FenceEpoch, TypeOK, LeaseType
<1>9. ASSUME NEW o \in Ops, Unvouch(o) \/ Vouch(o) PROVE TypeOK'
    BY <1>9 DEF Unvouch, Vouch, TypeOK
<1>10. ASSUME NEW p \in Principals, Expire(p) PROVE TypeOK'
    BY <1>10 DEF Expire, TypeOK, LeaseType
<1>11. CASE AnonFence
    BY <1>11 DEF AnonFence, TypeOK, LeaseType
<1> QED
    BY <1>1, <1>2, <1>3, <1>4, <1>5, <1>6, <1>7, <1>8, <1>9, <1>10, <1>11 DEF Next

THEOREM TypeAlways == Spec => []TypeOK
<1>1. TypeOK /\ [Next]_vars => TypeOK'
    BY TypeNext
<1> QED
    BY <1>1, TypeInit, PTL DEF Spec

-----------------------------------------------------------------------------
(* The lease invariants: Rooted, LiveGranted, Within, OperatorLeaseWasVouched,   *)
(* RevokedStaysOut. Each is over the lease table and is proved action by action. *)


LEMMA RootedNext ==
    ASSUME Mut # "M_NOSEAT", TypeOK, Rooted /\ LiveGranted, [Next]_vars
    PROVE  (Rooted /\ LiveGranted)'
<1> USE DEF Rooted, LiveGranted, Live
<1>1. CASE UNCHANGED vars
    BY <1>1 DEF vars
<1>2. ASSUME NEW p \in Principals, NEW w \in 1..MaxW, Seat(p, w) PROVE (Rooted /\ LiveGranted)'
    BY <1>2 DEF Seat, TypeOK, LeaseType
<1>3. ASSUME NEW o \in Ops, NEW p \in Principals, NEW w \in 1..MaxW, Regrant(o, p, w)
      PROVE (Rooted /\ LiveGranted)'
    BY <1>3 DEF Regrant, TypeOK, LeaseType
<1>4. ASSUME NEW o \in Ops, NEW p \in Principals, NEW w \in 1..MaxW, Grant(o, p, w)
      PROVE (Rooted /\ LiveGranted)'
    BY <1>4 DEF Grant
<1>5. ASSUME NEW o \in Ops, NEW p \in Principals, Renew(o, p) PROVE (Rooted /\ LiveGranted)'
    BY <1>5 DEF Renew, TypeOK, LeaseType
<1>6. ASSUME NEW o \in Ops, NEW p \in Principals, EndRound(o, p) PROVE (Rooted /\ LiveGranted)'
    BY <1>6 DEF EndRound, TypeOK, LeaseType
<1>7. ASSUME NEW o \in Ops, NEW p \in Principals, Revoke(o, p) PROVE (Rooted /\ LiveGranted)'
    BY <1>7 DEF Revoke, TypeOK, LeaseType
<1>8. ASSUME NEW o \in Ops, FenceEpoch(o) PROVE (Rooted /\ LiveGranted)'
    BY <1>8 DEF FenceEpoch, TypeOK, LeaseType
<1>9. ASSUME NEW o \in Ops, Unvouch(o) \/ Vouch(o) PROVE (Rooted /\ LiveGranted)'
    BY <1>9 DEF Unvouch, Vouch
<1>10. ASSUME NEW p \in Principals, Expire(p) PROVE (Rooted /\ LiveGranted)'
    BY <1>10 DEF Expire, TypeOK, LeaseType
<1>11. CASE AnonFence
    BY <1>11 DEF AnonFence, TypeOK, LeaseType
<1> QED
    BY <1>1, <1>2, <1>3, <1>4, <1>5, <1>6, <1>7, <1>8, <1>9, <1>10, <1>11 DEF Next

LEMMA WithinNext ==
    ASSUME Mut \notin {"M_NOSEAT", "M_WIDEN"}, TypeOK, Within, [Next]_vars
    PROVE  Within'
<1> USE DEF Within
<1>1. CASE UNCHANGED vars
    BY <1>1 DEF vars
<1>2. ASSUME NEW p \in Principals, NEW w \in 1..MaxW, Seat(p, w) PROVE Within'
    BY <1>2 DEF Seat, TypeOK, LeaseType, MaxW
<1>3. ASSUME NEW o \in Ops, NEW p \in Principals, NEW w \in 1..MaxW, Regrant(o, p, w) PROVE Within'
    BY <1>3 DEF Regrant, TypeOK, LeaseType, MaxW
<1>4. ASSUME NEW o \in Ops, NEW p \in Principals, NEW w \in 1..MaxW, Grant(o, p, w) PROVE Within'
    BY <1>4 DEF Grant
<1>5. ASSUME NEW o \in Ops, NEW p \in Principals, Renew(o, p) PROVE Within'
    BY <1>5 DEF Renew, TypeOK, LeaseType
<1>6. ASSUME NEW o \in Ops, NEW p \in Principals, EndRound(o, p) PROVE Within'
    BY <1>6 DEF EndRound, TypeOK, LeaseType
<1>7. ASSUME NEW o \in Ops, NEW p \in Principals, Revoke(o, p) PROVE Within'
    BY <1>7 DEF Revoke, TypeOK, LeaseType
<1>8. ASSUME NEW o \in Ops, FenceEpoch(o) PROVE Within'
    BY <1>8 DEF FenceEpoch, TypeOK, LeaseType
<1>9. ASSUME NEW o \in Ops, Unvouch(o) \/ Vouch(o) PROVE Within'
    BY <1>9 DEF Unvouch, Vouch
<1>10. ASSUME NEW p \in Principals, Expire(p) PROVE Within'
    BY <1>10 DEF Expire, TypeOK, LeaseType
<1>11. CASE AnonFence
    BY <1>11 DEF AnonFence, TypeOK, LeaseType
<1> QED
    BY <1>1, <1>2, <1>3, <1>4, <1>5, <1>6, <1>7, <1>8, <1>9, <1>10, <1>11 DEF Next

LEMMA VouchedNext ==
    ASSUME Mut \notin {"M_NOATTEST", "M_NOSEAT"}, TypeOK, OperatorLeaseWasVouched, [Next]_vars
    PROVE  OperatorLeaseWasVouched'
<1> USE DEF OperatorLeaseWasVouched, Live, Attests, VouchedAt, Principals
<1>1. CASE UNCHANGED vars
    BY <1>1 DEF vars
<1>2. ASSUME NEW p \in Principals, NEW w \in 1..MaxW, Seat(p, w) PROVE OperatorLeaseWasVouched'
    BY <1>2 DEF Seat, TypeOK, LeaseType
<1>3. ASSUME NEW o \in Ops, NEW p \in Principals, NEW w \in 1..MaxW, Regrant(o, p, w)
      PROVE OperatorLeaseWasVouched'
    BY <1>3 DEF Regrant, TypeOK, LeaseType
<1>4. ASSUME NEW o \in Ops, NEW p \in Principals, NEW w \in 1..MaxW, Grant(o, p, w)
      PROVE OperatorLeaseWasVouched'
    BY <1>4 DEF Grant
<1>5. ASSUME NEW o \in Ops, NEW p \in Principals, Renew(o, p) PROVE OperatorLeaseWasVouched'
    BY <1>5 DEF Renew, TypeOK, LeaseType
<1>6. ASSUME NEW o \in Ops, NEW p \in Principals, EndRound(o, p) PROVE OperatorLeaseWasVouched'
    BY <1>6 DEF EndRound, TypeOK, LeaseType
<1>7. ASSUME NEW o \in Ops, NEW p \in Principals, Revoke(o, p) PROVE OperatorLeaseWasVouched'
    BY <1>7 DEF Revoke, TypeOK, LeaseType
<1>8. ASSUME NEW o \in Ops, FenceEpoch(o) PROVE OperatorLeaseWasVouched'
    BY <1>8 DEF FenceEpoch, TypeOK, LeaseType
<1>9. ASSUME NEW o \in Ops, Unvouch(o) \/ Vouch(o) PROVE OperatorLeaseWasVouched'
    BY <1>9 DEF Unvouch, Vouch
<1>10. ASSUME NEW p \in Principals, Expire(p) PROVE OperatorLeaseWasVouched'
    BY <1>10 DEF Expire, TypeOK, LeaseType
<1>11. CASE AnonFence
    BY <1>11 DEF AnonFence, TypeOK, LeaseType
<1> QED
    BY <1>1, <1>2, <1>3, <1>4, <1>5, <1>6, <1>7, <1>8, <1>9, <1>10, <1>11 DEF Next

LEMMA RevokedNext ==
    ASSUME TypeOK, RevokedStaysOut, [Next]_vars
    PROVE  RevokedStaysOut'
<1> USE DEF RevokedStaysOut, Live
<1>1. CASE UNCHANGED vars
    BY <1>1 DEF vars
<1>2. ASSUME NEW p \in Principals, NEW w \in 1..MaxW, Seat(p, w) PROVE RevokedStaysOut'
    BY <1>2 DEF Seat, TypeOK, LeaseType
<1>3. ASSUME NEW o \in Ops, NEW p \in Principals, NEW w \in 1..MaxW, Regrant(o, p, w) PROVE RevokedStaysOut'
    BY <1>3 DEF Regrant, TypeOK, LeaseType
<1>4. ASSUME NEW o \in Ops, NEW p \in Principals, NEW w \in 1..MaxW, Grant(o, p, w) PROVE RevokedStaysOut'
    BY <1>4 DEF Grant, TypeOK, LeaseType
<1>5. ASSUME NEW o \in Ops, NEW p \in Principals, Renew(o, p) PROVE RevokedStaysOut'
    BY <1>5 DEF Renew, TypeOK, LeaseType
<1>6. ASSUME NEW o \in Ops, NEW p \in Principals, EndRound(o, p) PROVE RevokedStaysOut'
    BY <1>6 DEF EndRound, TypeOK, LeaseType
<1>7. ASSUME NEW o \in Ops, NEW p \in Principals, Revoke(o, p) PROVE RevokedStaysOut'
    BY <1>7 DEF Revoke, TypeOK, LeaseType
<1>8. ASSUME NEW o \in Ops, FenceEpoch(o) PROVE RevokedStaysOut'
    BY <1>8 DEF FenceEpoch, TypeOK, LeaseType
<1>9. ASSUME NEW o \in Ops, Unvouch(o) \/ Vouch(o) PROVE RevokedStaysOut'
    BY <1>9 DEF Unvouch, Vouch
<1>10. ASSUME NEW p \in Principals, Expire(p) PROVE RevokedStaysOut'
    BY <1>10 DEF Expire, TypeOK, LeaseType
<1>11. CASE AnonFence
    BY <1>11 DEF AnonFence, TypeOK, LeaseType
<1> QED
    BY <1>1, <1>2, <1>3, <1>4, <1>5, <1>6, <1>7, <1>8, <1>9, <1>10, <1>11 DEF Next

-----------------------------------------------------------------------------
(* The add and deny invariants. `adds` and `stops` hold the last admitted one,   *)
(* so each step either leaves the set or replaces it with one record whose       *)
(* fields the action's guard fixes.                                              *)

\* What every step does to `adds`.
LEMMA AddsStep ==
    ASSUME [Next]_vars
    PROVE  \/ adds' = adds
           \/ \E o \in Ops, p \in Principals, w \in 1..MaxW :
                /\ Regrant(o, p, w)
                /\ adds' = {AddRecord("regrant", o, p, lease[p].width, w)}
           \/ \E o \in Ops, p \in Principals :
                /\ Renew(o, p)
                /\ adds' = {AddRecord("renew", o, p, lease[p].width, lease[p].width)}
           \/ \E o \in Ops, p \in Principals, w \in 1..MaxW :
                /\ Grant(o, p, w)
                /\ adds' = {AddRecord("grant", o, p, 0, w)}
BY DEF Next, vars, Seat, Regrant, Renew, Grant, EndRound, Revoke, FenceEpoch, AnonFence, Expire, Unvouch, Vouch

\* What every step does to `stops`.
LEMMA StopsStep ==
    ASSUME [Next]_vars
    PROVE  \/ stops' = stops
           \/ \E o \in Ops, k \in {"end", "revoke", "fence"} :
                /\ MayDeny(o)
                /\ stops' = {StopRecord(k, o)}
           \/ /\ Mut = "M_ANON"
              /\ stops' = {[kind |-> "fence", by |-> "nobody", byLive |-> TRUE, vouched |-> TRUE, inForce |-> TRUE]}
BY DEF Next, vars, Seat, Regrant, Renew, Grant, EndRound, Revoke, FenceEpoch, AnonFence, Expire, Unvouch, Vouch

LEMMA WidensNext ==
    ASSUME Mut # "M_WIDEN", SuccessorNeverWidens, [Next]_vars
    PROVE  SuccessorNeverWidens'
BY AddsStep DEF SuccessorNeverWidens, AddRecord, Regrant

LEMMA LapsedNext ==
    ASSUME Mut # "M_LAPSEDADD", ExpiredOperatorOnlyDenies, [Next]_vars
    PROVE  ExpiredOperatorOnlyDenies'
BY AddsStep DEF ExpiredOperatorOnlyDenies, AddRecord, Regrant, Renew, Grant, MayAdd

LEMMA PeerNext ==
    ASSUME Mut \notin {"M_LAPSEDADD", "M_PEER"}, NoAddWithoutLiveLeaseAndPeer, [Next]_vars
    PROVE  NoAddWithoutLiveLeaseAndPeer'
BY AddsStep DEF NoAddWithoutLiveLeaseAndPeer, AddRecord, Regrant, Renew, Grant, MayAdd

LEMMA SelfNext ==
    ASSUME Mut # "M_SELF", NoSelfRegrant, [Next]_vars
    PROVE  NoSelfRegrant'
BY AddsStep DEF NoSelfRegrant, AddRecord, Regrant, Renew, Grant, MayAdd

LEMMA StaleNext ==
    ASSUME Mut # "M_STALEKEY", NoDenyOnAStaleKey, [Next]_vars
    PROVE  NoDenyOnAStaleKey'
BY StopsStep DEF NoDenyOnAStaleKey, StopRecord, MayDeny

LEMMA RevokedDenyNext ==
    ASSUME NoDenyByRevoked, [Next]_vars
    PROVE  NoDenyByRevoked'
BY StopsStep DEF NoDenyByRevoked, StopRecord, MayDeny

LEMMA AttributedNext ==
    ASSUME Mut # "M_ANON", EveryStopIsAttributed, [Next]_vars
    PROVE  EveryStopIsAttributed'
BY StopsStep DEF EveryStopIsAttributed, StopRecord

(* A deny is enabled wherever its guard holds: every state, no induction.        *)
LEMMA DenyEnabled ==
    ASSUME Mut # "M_DENYLEASE"
    PROVE  DenyAlwaysAvailable
BY ExpandENABLED DEF DenyAlwaysAvailable, FenceEpoch, MayDeny

-----------------------------------------------------------------------------
THEOREM FirstLeaseHasAQuorumAlways ==
    ASSUME Mut # "M_NOSEAT"
    PROVE  Spec => []FirstLeaseHasAQuorum
<1>1. Init => Rooted /\ LiveGranted
    BY DEF Init, Rooted, LiveGranted, Live, NoLease
<1>2. TypeOK /\ (Rooted /\ LiveGranted) /\ [Next]_vars => (Rooted /\ LiveGranted)'
    BY RootedNext
<1>3. Rooted /\ LiveGranted => FirstLeaseHasAQuorum
    BY DEF Rooted, LiveGranted, FirstLeaseHasAQuorum
<1>4. Spec => []TypeOK
    BY TypeAlways
<1> QED
    BY <1>1, <1>2, <1>3, <1>4, PTL DEF Spec

THEOREM LeaseWithinSeatingAlways ==
    ASSUME Mut \notin {"M_NOSEAT", "M_WIDEN"}
    PROVE  Spec => []LeaseWithinSeating
<1>1. Init => Within
    BY DEF Init, Within, NoLease
<1>2. TypeOK /\ Within /\ [Next]_vars => Within'
    BY WithinNext
<1>3. Within => LeaseWithinSeating
    BY DEF Within, LeaseWithinSeating
<1>4. Spec => []TypeOK
    BY TypeAlways
<1> QED
    BY <1>1, <1>2, <1>3, <1>4, PTL DEF Spec

THEOREM SuccessorNeverWidensAlways ==
    ASSUME Mut # "M_WIDEN"
    PROVE  Spec => []SuccessorNeverWidens
<1>1. Init => SuccessorNeverWidens
    BY DEF Init, SuccessorNeverWidens
<1>2. SuccessorNeverWidens /\ [Next]_vars => SuccessorNeverWidens'
    BY WidensNext
<1> QED
    BY <1>1, <1>2, PTL DEF Spec

THEOREM ExpiredOperatorOnlyDeniesAlways ==
    ASSUME Mut # "M_LAPSEDADD"
    PROVE  Spec => []ExpiredOperatorOnlyDenies
<1>1. Init => ExpiredOperatorOnlyDenies
    BY DEF Init, ExpiredOperatorOnlyDenies
<1>2. ExpiredOperatorOnlyDenies /\ [Next]_vars => ExpiredOperatorOnlyDenies'
    BY LapsedNext
<1> QED
    BY <1>1, <1>2, PTL DEF Spec

THEOREM NoAddWithoutLiveLeaseAndPeerAlways ==
    ASSUME Mut \notin {"M_LAPSEDADD", "M_PEER"}
    PROVE  Spec => []NoAddWithoutLiveLeaseAndPeer
<1>1. Init => NoAddWithoutLiveLeaseAndPeer
    BY DEF Init, NoAddWithoutLiveLeaseAndPeer
<1>2. NoAddWithoutLiveLeaseAndPeer /\ [Next]_vars => NoAddWithoutLiveLeaseAndPeer'
    BY PeerNext
<1> QED
    BY <1>1, <1>2, PTL DEF Spec

THEOREM NoSelfRegrantAlways ==
    ASSUME Mut # "M_SELF"
    PROVE  Spec => []NoSelfRegrant
<1>1. Init => NoSelfRegrant
    BY DEF Init, NoSelfRegrant
<1>2. NoSelfRegrant /\ [Next]_vars => NoSelfRegrant'
    BY SelfNext
<1> QED
    BY <1>1, <1>2, PTL DEF Spec

THEOREM OperatorLeaseWasVouchedAlways ==
    ASSUME Mut \notin {"M_NOATTEST", "M_NOSEAT"}
    PROVE  Spec => []OperatorLeaseWasVouched
<1>1. Init => OperatorLeaseWasVouched
    BY DEF Init, OperatorLeaseWasVouched, Live, NoLease, Principals
<1>2. TypeOK /\ OperatorLeaseWasVouched /\ [Next]_vars => OperatorLeaseWasVouched'
    BY VouchedNext
<1>3. Spec => []TypeOK
    BY TypeAlways
<1> QED
    BY <1>1, <1>2, <1>3, PTL DEF Spec

THEOREM NoDenyOnAStaleKeyAlways ==
    ASSUME Mut # "M_STALEKEY"
    PROVE  Spec => []NoDenyOnAStaleKey
<1>1. Init => NoDenyOnAStaleKey
    BY DEF Init, NoDenyOnAStaleKey
<1>2. NoDenyOnAStaleKey /\ [Next]_vars => NoDenyOnAStaleKey'
    BY StaleNext
<1> QED
    BY <1>1, <1>2, PTL DEF Spec

THEOREM NoDenyByRevokedAlways == Spec => []NoDenyByRevoked
<1>1. Init => NoDenyByRevoked
    BY DEF Init, NoDenyByRevoked
<1>2. NoDenyByRevoked /\ [Next]_vars => NoDenyByRevoked'
    BY RevokedDenyNext
<1> QED
    BY <1>1, <1>2, PTL DEF Spec

THEOREM EveryStopIsAttributedAlways ==
    ASSUME Mut # "M_ANON"
    PROVE  Spec => []EveryStopIsAttributed
<1>1. Init => EveryStopIsAttributed
    BY DEF Init, EveryStopIsAttributed
<1>2. EveryStopIsAttributed /\ [Next]_vars => EveryStopIsAttributed'
    BY AttributedNext
<1> QED
    BY <1>1, <1>2, PTL DEF Spec

THEOREM RevokedStaysOutAlways == Spec => []RevokedStaysOut
<1>1. Init => RevokedStaysOut
    BY DEF Init, RevokedStaysOut, Live, NoLease
<1>2. TypeOK /\ RevokedStaysOut /\ [Next]_vars => RevokedStaysOut'
    BY RevokedNext
<1>3. Spec => []TypeOK
    BY TypeAlways
<1> QED
    BY <1>1, <1>2, <1>3, PTL DEF Spec

THEOREM DenyAlwaysAvailableAlways ==
    ASSUME Mut # "M_DENYLEASE"
    PROVE  Spec => []DenyAlwaysAvailable
<1>1. DenyAlwaysAvailable
    BY DenyEnabled
<1> QED
    BY <1>1, PTL

THEOREM SafeAlways ==
    ASSUME Mut = "none"
    PROVE  Spec => []Safe
<1>1. Spec => []FirstLeaseHasAQuorum
    BY FirstLeaseHasAQuorumAlways
<1>2. Spec => []LeaseWithinSeating
    BY LeaseWithinSeatingAlways
<1>3. Spec => []SuccessorNeverWidens
    BY SuccessorNeverWidensAlways
<1>4. Spec => []NoAddWithoutLiveLeaseAndPeer
    BY NoAddWithoutLiveLeaseAndPeerAlways
<1>5. Spec => []NoSelfRegrant
    BY NoSelfRegrantAlways
<1>6. Spec => []OperatorLeaseWasVouched
    BY OperatorLeaseWasVouchedAlways
<1>7. Spec => []NoDenyOnAStaleKey
    BY NoDenyOnAStaleKeyAlways
<1>8. Spec => []NoDenyByRevoked
    BY NoDenyByRevokedAlways
<1>9. Spec => []EveryStopIsAttributed
    BY EveryStopIsAttributedAlways
<1>10. Spec => []RevokedStaysOut
    BY RevokedStaysOutAlways
<1>11. Spec => []DenyAlwaysAvailable
    BY DenyAlwaysAvailableAlways
<1> QED
    BY <1>1, <1>2, <1>3, <1>4, <1>5, <1>6, <1>7, <1>8, <1>9, <1>10, <1>11, PTL DEF Safe

-----------------------------------------------------------------------------
(* What each mutation admits: the guard it removes. Their counterexamples are    *)
(* TLC's (Operators-results-2026.10.04.txt).                                     *)

LEMMA MutLapsedPeerSelf ==
    ASSUME NEW o \in Ops, NEW p \in Principals, inForce[o]
    PROVE  /\ (Mut = "M_LAPSEDADD" /\ PeerLive(o) /\ p # o) => MayAdd(o, p)
           /\ (Mut = "M_PEER" /\ Live(o) /\ p # o) => MayAdd(o, p)
           /\ (Mut = "M_SELF" /\ Live(o) /\ PeerLive(o)) => MayAdd(o, o)
BY DEF MayAdd

LEMMA MutNoAttestAttestsAll == Mut = "M_NOATTEST" => \A p \in Principals : Attests(p)
BY DEF Attests

LEMMA MutStaleKeyDenies ==
    ASSUME Mut = "M_STALEKEY", NEW o \in Ops, inForce[o]
    PROVE  MayDeny(o)
BY DEF MayDeny

LEMMA MutDenyLeaseNeedsLease ==
    ASSUME Mut = "M_DENYLEASE", NEW o \in Ops, MayDeny(o)
    PROVE  Live(o)
BY DEF MayDeny

LEMMA NoneNeverGrants == Mut # "M_NOSEAT" => \A o \in Ops, p \in Principals, w \in 1..MaxW : ~Grant(o, p, w)
BY DEF Grant
=============================================================================
