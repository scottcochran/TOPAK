----------------------------- MODULE Alone_proof -----------------------------
(* TLAPS proof of the invariants of Alone.tla (ADR-0062 §11), for every value  *)
(* of the constants the assumptions below admit: every count, every number of  *)
(* leases and fences, and every beacon count. Alone.tla is not edited.         *)
(*                                                                             *)
(*   THEOREM AlonePermitsNothingAlways                                         *)
(*     [Mut \notin {M_ALONEACTS, M_ENTRYAFTEREND, M_BEACONUNCOUNTED}]          *)
(*   THEOREM ExpiryGrantsNothingAlways                                         *)
(*     [Mut \notin {M_ENTRYAFTEREND, M_STACKCHOOSES}]                          *)
(*   THEOREM LocalNeverWaitsAlways                                             *)
(*     [Mut \notin {M_WAITPRIMARY, M_WAITPEER, M_WAITOBSERVER}]                *)
(*   THEOREM TerminalNeverWaitsAlways  [Mut # M_STACKGATED]                    *)
(*   THEOREM SafeAlways                [Mut = "none"]                          *)
(*                                                                             *)
(* The strengthening. AlonePermitsNothing rests on one clause, LiveHears: a    *)
(* live lease means the vehicle hears its plane, since a grant needs hearing   *)
(* and going alone ends the lease. Permit reads only the lease, so its flag    *)
(* stays false because of that clause. The beacon clause is arithmetic at      *)
(* Beacon. ExpiryGrantsNothing is two flags, each inductive alone at the one   *)
(* action that sets it. The two ENABLED invariants need no induction: each is  *)
(* valid in every state under its hypothesis, proved in one step from its      *)
(* expansion, and lifted by PTL, as in Emergency_live_proof.tla. No ENABLED    *)
(* appears under a binder, and no backend sees one unexpanded.                 *)
(*                                                                             *)
(* Mutations and witnesses are behaviours and stay with TLC                    *)
(* (Alone-results-*.txt). Check: tools/tlapm --cleanfp --strict.               *)
EXTENDS Alone, TLAPS

ASSUME MaxBeaconNat == MaxBeacon \in Nat

Tags == {"local", "ordered", "alone", "beacon", "recover", "fenceAlone", "regrant"}

TypeOK ==
  /\ lstate \in {"none", "live", "ended"}
  /\ alphabet \subseteq Entries
  /\ used \in Nat
  /\ beacons \in Nat
  /\ hears \in BOOLEAN
  /\ fence \in Nat
  /\ grants \in Nat
  /\ primary \in {"up", "down"}
  /\ peer \in {"up", "down"}
  /\ observer \in {"live", "stale"}
  /\ stack \in {"ready", "wedged"}
  /\ aloneActed \in BOOLEAN
  /\ entryAfterEnd \in BOOLEAN
  /\ wrongTerminal \in BOOLEAN
  /\ recovered \in Behaviours \cup {"none"}
  /\ seen \subseteq Tags

LiveHears == lstate = "live" => hears
InvAlone  == TypeOK /\ LiveHears /\ ~aloneActed /\ BeaconWithin
-----------------------------------------------------------------------------
LEMMA InitTypeOK == Init => TypeOK
  BY DEF Init, TypeOK, Behaviours

LEMMA NextTypeOK == TypeOK /\ [Next]_vars => TypeOK'
<1> SUFFICES ASSUME TypeOK, [Next]_vars PROVE TypeOK' OBVIOUS
<1>1. CASE UNCHANGED vars
  BY <1>1 DEF TypeOK, vars
<1>2. ASSUME NEW a \in Alphabets, Grant(a) PROVE TypeOK'
  <2>1. seen' \subseteq Tags
    BY <1>2 DEF Grant, TypeOK, Tags
  <2>2. alphabet' \subseteq Entries
    BY <1>2 DEF Grant, Alphabets, Entries, LocalEntries, OrderedEntries
  <2> QED
    BY <1>2, <2>1, <2>2 DEF Grant, TypeOK
<1>3. ASSUME NEW e \in Entries, Permit(e) PROVE TypeOK'
  <2>1. seen' \subseteq Tags
    BY <1>3 DEF Permit, TypeOK, Tags
  <2> QED
    BY <1>3, <2>1 DEF Permit, TypeOK
<1>4. CASE EndLease
  BY <1>4 DEF EndLease, TypeOK
<1>5. CASE GoAlone
  <2>1. seen' \subseteq Tags
    BY <1>5 DEF GoAlone, TypeOK, Tags
  <2>2. lstate' \in {"none", "live", "ended"}
    BY <1>5 DEF GoAlone, AfterGoAlone, Ended, TypeOK
  <2> QED
    BY <1>5, <2>1, <2>2 DEF GoAlone, TypeOK
<1>6. CASE HearAgain
  BY <1>6 DEF HearAgain, TypeOK
<1>7. CASE FenceRelay
  <2>1. seen' \subseteq Tags
    BY <1>7 DEF FenceRelay, TypeOK, Tags
  <2>2. lstate' \in {"none", "live", "ended"}
    BY <1>7 DEF FenceRelay, Ended, TypeOK
  <2> QED
    BY <1>7, <2>1, <2>2 DEF FenceRelay, TypeOK
<1>8. CASE Beacon
  <2>1. seen' \subseteq Tags
    BY <1>8 DEF Beacon, TypeOK, Tags
  <2> QED
    BY <1>8, <2>1 DEF Beacon, TypeOK
<1>9. ASSUME NEW b \in Behaviours, Recover(b) PROVE TypeOK'
  <2>1. seen' \subseteq Tags
    BY <1>9 DEF Recover, TypeOK, Tags
  <2> QED
    BY <1>9, <2>1 DEF Recover, TypeOK
<1>10. CASE MovePrimary
  BY <1>10 DEF MovePrimary, TypeOK
<1>11. CASE MovePeer
  BY <1>11 DEF MovePeer, TypeOK
<1>12. CASE MoveObserver
  BY <1>12 DEF MoveObserver, TypeOK
<1>13. CASE MoveStack
  BY <1>13 DEF MoveStack, TypeOK
<1> QED
  BY <1>1, <1>2, <1>3, <1>4, <1>5, <1>6, <1>7, <1>8, <1>9, <1>10, <1>11, <1>12, <1>13 DEF Next

THEOREM TypeAlways == Spec => []TypeOK
<1>1. TypeOK /\ [Next]_vars => TypeOK'
  BY NextTypeOK
<1> QED
  BY InitTypeOK, <1>1, PTL DEF Spec
-----------------------------------------------------------------------------
(* AlonePermitsNothing.                                                        *)

LEMMA InitInvAlone == Init => InvAlone
  BY InitTypeOK, MaxBeaconNat DEF Init, InvAlone, LiveHears, BeaconWithin

LEMMA NextInvAlone ==
  ASSUME Mut # "M_ALONEACTS", Mut # "M_ENTRYAFTEREND", Mut # "M_BEACONUNCOUNTED",
         InvAlone, [Next]_vars
  PROVE  InvAlone'
<1>0. TypeOK /\ TypeOK'
  BY NextTypeOK DEF InvAlone
<1>a. LiveHears /\ ~aloneActed /\ BeaconWithin
  BY DEF InvAlone
<1>1. CASE UNCHANGED vars
  BY <1>0, <1>a, <1>1 DEF InvAlone, LiveHears, BeaconWithin, vars
<1>2. ASSUME NEW a \in Alphabets, Grant(a) PROVE InvAlone'
  <2>1. hears' = hears /\ hears /\ beacons' = 0 /\ aloneActed' = aloneActed
    BY <1>2 DEF Grant
  <2> QED
    BY <1>0, <1>a, <2>1, MaxBeaconNat DEF InvAlone, LiveHears, BeaconWithin
<1>3. ASSUME NEW e \in Entries, Permit(e) PROVE InvAlone'
  <2>1. lstate = "live"
    BY <1>3 DEF Permit, PermitLive
  <2>2. hears
    BY <1>a, <2>1 DEF LiveHears
  <2>3. /\ aloneActed' = (aloneActed \/ ~hears)
        /\ UNCHANGED <<lstate, hears, beacons>>
    BY <1>3 DEF Permit
  <2> QED
    BY <1>0, <1>a, <2>2, <2>3 DEF InvAlone, LiveHears, BeaconWithin
<1>4. CASE EndLease
  BY <1>0, <1>a, <1>4 DEF EndLease, InvAlone, LiveHears, BeaconWithin
<1>5. CASE GoAlone
  <2>1. lstate' # "live"
    BY <1>0, <1>5 DEF GoAlone, AfterGoAlone, Ended, TypeOK
  <2>2. UNCHANGED <<aloneActed, beacons>>
    BY <1>5 DEF GoAlone
  <2> QED
    BY <1>0, <1>a, <2>1, <2>2 DEF InvAlone, LiveHears, BeaconWithin
<1>6. CASE HearAgain
  BY <1>0, <1>a, <1>6 DEF HearAgain, InvAlone, LiveHears, BeaconWithin
<1>7. CASE FenceRelay
  <2>1. lstate' # "live"
    BY <1>0, <1>7 DEF FenceRelay, Ended, TypeOK
  <2>2. UNCHANGED <<aloneActed, beacons>>
    BY <1>7 DEF FenceRelay
  <2> QED
    BY <1>0, <1>a, <2>1, <2>2 DEF InvAlone, LiveHears, BeaconWithin
<1>8. CASE Beacon
  <2>1. /\ beacons < MaxBeacon
        /\ beacons' = beacons + 1
        /\ UNCHANGED <<lstate, hears, aloneActed>>
    BY <1>8 DEF Beacon, BeaconLimit
  <2>2. beacons' <= MaxBeacon
    BY <1>0, <2>1, MaxBeaconNat DEF TypeOK
  <2> QED
    BY <1>0, <1>a, <2>1, <2>2 DEF InvAlone, LiveHears, BeaconWithin
<1>9. ASSUME NEW b \in Behaviours, Recover(b) PROVE InvAlone'
  BY <1>0, <1>a, <1>9 DEF Recover, InvAlone, LiveHears, BeaconWithin
<1>10. CASE MovePrimary \/ MovePeer \/ MoveObserver \/ MoveStack
  <2>1. UNCHANGED <<lstate, hears, aloneActed, beacons>>
    BY <1>10 DEF MovePrimary, MovePeer, MoveObserver, MoveStack
  <2> QED
    BY <1>0, <1>a, <2>1 DEF InvAlone, LiveHears, BeaconWithin
<1> QED
  BY <1>1, <1>2, <1>3, <1>4, <1>5, <1>6, <1>7, <1>8, <1>9, <1>10 DEF Next

THEOREM AlonePermitsNothingAlways ==
  ASSUME Mut # "M_ALONEACTS", Mut # "M_ENTRYAFTEREND", Mut # "M_BEACONUNCOUNTED"
  PROVE  Spec => []AlonePermitsNothing
<1>1. InvAlone /\ [Next]_vars => InvAlone'
  BY NextInvAlone
<1>2. InvAlone => AlonePermitsNothing
  BY DEF InvAlone, AlonePermitsNothing
<1> QED
  BY InitInvAlone, <1>1, <1>2, PTL DEF Spec
-----------------------------------------------------------------------------
(* ExpiryGrantsNothing: two flags, each inductive alone.                       *)

LEMMA NextExpiry ==
  ASSUME Mut # "M_ENTRYAFTEREND", Mut # "M_STACKCHOOSES", ExpiryGrantsNothing, [Next]_vars
  PROVE  ExpiryGrantsNothing'
<1>a. ~entryAfterEnd /\ ~wrongTerminal
  BY DEF ExpiryGrantsNothing
<1>1. CASE UNCHANGED vars
  BY <1>a, <1>1 DEF ExpiryGrantsNothing, vars
<1>2. ASSUME NEW a \in Alphabets, Grant(a) PROVE ExpiryGrantsNothing'
  BY <1>a, <1>2 DEF Grant, ExpiryGrantsNothing
<1>3. ASSUME NEW e \in Entries, Permit(e) PROVE ExpiryGrantsNothing'
  <2>1. lstate = "live"
    BY <1>3 DEF Permit, PermitLive
  <2> QED
    BY <1>a, <1>3, <2>1 DEF Permit, ExpiryGrantsNothing
<1>4. CASE EndLease \/ GoAlone \/ HearAgain \/ FenceRelay \/ Beacon
  <2>1. UNCHANGED <<entryAfterEnd, wrongTerminal>>
    BY <1>4 DEF EndLease, GoAlone, HearAgain, FenceRelay, Beacon
  <2> QED
    BY <1>a, <2>1 DEF ExpiryGrantsNothing
<1>5. ASSUME NEW b \in Behaviours, Recover(b) PROVE ExpiryGrantsNothing'
  <2>1. b \in {"hold", Seated}
    BY <1>5 DEF Recover, RecoverOK
  <2>2. /\ wrongTerminal' = (wrongTerminal \/ b \notin {"hold", Seated})
        /\ UNCHANGED entryAfterEnd
    BY <1>5 DEF Recover
  <2> QED
    BY <1>a, <2>1, <2>2 DEF ExpiryGrantsNothing
<1>6. CASE MovePrimary \/ MovePeer \/ MoveObserver \/ MoveStack
  <2>1. UNCHANGED <<entryAfterEnd, wrongTerminal>>
    BY <1>6 DEF MovePrimary, MovePeer, MoveObserver, MoveStack
  <2> QED
    BY <1>a, <2>1 DEF ExpiryGrantsNothing
<1> QED
  BY <1>1, <1>2, <1>3, <1>4, <1>5, <1>6 DEF Next

THEOREM ExpiryGrantsNothingAlways ==
  ASSUME Mut # "M_ENTRYAFTEREND", Mut # "M_STACKCHOOSES"
  PROVE  Spec => []ExpiryGrantsNothing
<1>1. ExpiryGrantsNothing /\ [Next]_vars => ExpiryGrantsNothing'
  BY NextExpiry
<1>2. Init => ExpiryGrantsNothing
  BY DEF Init, ExpiryGrantsNothing
<1> QED
  BY <1>1, <1>2, PTL DEF Spec
-----------------------------------------------------------------------------
(* The two ENABLED invariants: valid in every state under their hypotheses,    *)
(* each proved in one step from its expansion. Elsewhere they appear by name.  *)

LEMMA LocalNeverWaitsValid ==
  ASSUME Mut # "M_WAITPRIMARY", Mut # "M_WAITPEER", Mut # "M_WAITOBSERVER"
  PROVE  LocalNeverWaits
BY ExpandENABLED, Isa DEF LocalNeverWaits, Permit, PermitLive, Gate, LocalGate, LocalEntries

THEOREM LocalNeverWaitsAlways ==
  ASSUME Mut # "M_WAITPRIMARY", Mut # "M_WAITPEER", Mut # "M_WAITOBSERVER"
  PROVE  Spec => []LocalNeverWaits
<1>1. LocalNeverWaits
  BY LocalNeverWaitsValid
<1> QED
  BY <1>1, PTL

LEMMA TerminalNeverWaitsValid ==
  ASSUME Mut # "M_STACKGATED"
  PROVE  TerminalNeverWaits
BY ExpandENABLED, Isa DEF TerminalNeverWaits, Recover, RecoverGate, RecoverOK

THEOREM TerminalNeverWaitsAlways ==
  ASSUME Mut # "M_STACKGATED"
  PROVE  Spec => []TerminalNeverWaits
<1>1. TerminalNeverWaits
  BY TerminalNeverWaitsValid
<1> QED
  BY <1>1, PTL
-----------------------------------------------------------------------------
THEOREM SafeAlways ==
  ASSUME Mut = "none"
  PROVE  Spec => []Safe
<1>1. Spec => []AlonePermitsNothing
  BY AlonePermitsNothingAlways
<1>2. Spec => []ExpiryGrantsNothing
  BY ExpiryGrantsNothingAlways
<1>3. Spec => []LocalNeverWaits
  BY LocalNeverWaitsAlways
<1>4. Spec => []TerminalNeverWaits
  BY TerminalNeverWaitsAlways
<1> QED
  BY <1>1, <1>2, <1>3, <1>4, PTL DEF Safe
-----------------------------------------------------------------------------
(* Why the mutations must fail. The counterexamples are TLC's.                 *)

LEMMA MutAloneActsKeepsLease ==
  ASSUME Mut = "M_ALONEACTS"
  PROVE  AfterGoAlone = lstate
  BY DEF AfterGoAlone

LEMMA MutBeaconUncountedRaisesLimit ==
  ASSUME Mut = "M_BEACONUNCOUNTED"
  PROVE  BeaconLimit = MaxBeacon + 1
  BY DEF BeaconLimit

LEMMA MutStackChoosesAdmitsAny ==
  ASSUME Mut = "M_STACKCHOOSES", NEW b
  PROVE  RecoverOK(b)
  BY DEF RecoverOK

LEMMA MutEntryAfterEndKeepsPermit ==
  ASSUME Mut = "M_ENTRYAFTEREND", lstate = "ended"
  PROVE  PermitLive
  BY DEF PermitLive

LEMMA MutWaitPrimaryWaits ==
  ASSUME Mut = "M_WAITPRIMARY", primary = "down"
  PROVE  ~ENABLED Permit("l1")
BY ExpandENABLED, Isa DEF Permit, Gate, LocalGate, LocalEntries

LEMMA MutWaitPeerWaits ==
  ASSUME Mut = "M_WAITPEER", peer = "down"
  PROVE  ~ENABLED Permit("l1")
BY ExpandENABLED, Isa DEF Permit, Gate, LocalGate, LocalEntries

LEMMA MutWaitObserverWaits ==
  ASSUME Mut = "M_WAITOBSERVER", observer = "stale"
  PROVE  ~ENABLED Permit("l1")
BY ExpandENABLED, Isa DEF Permit, Gate, LocalGate, LocalEntries

LEMMA MutStackGatedWaits ==
  ASSUME Mut = "M_STACKGATED", stack = "wedged"
  PROVE  ~ENABLED Recover(Seated)
BY ExpandENABLED, Isa DEF Recover, RecoverGate
=============================================================================
