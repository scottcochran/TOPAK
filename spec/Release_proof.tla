---------------------------- MODULE Release_proof -----------------------------
(* TLAPS proof of the invariants of Release.tla (ADR-0066 §7), for every act   *)
(* bound, every tick bound and every freshness window. Release.tla is not      *)
(* edited.                                                                     *)
(*                                                                             *)
(*   THEOREM SignedByPersonAlways          [Mut # "M_AGENTRELEASE"]            *)
(*   THEOREM OrderedAtCommandAlways        [Mut # "M_LITERELEASE"]             *)
(*   THEOREM UsedOnceAlways                [Mut # "M_REPLAY",                  *)
(*                                          Mut # "M_ANYVEHICLE"]              *)
(*   THEOREM NoOlderThanDeclaredAlways     [Mut # "M_LATEFIRST"]               *)
(*   THEOREM IrreversibleIsAPersonsAlways  [all five of the above]             *)
(*   THEOREM ConflictIsAFindingAlways      [Mut # "M_VOID"]                    *)
(*   THEOREM OrderedInContactAlways        [Mut # "M_NOCONTACT"]               *)
(*   THEOREM ReleaseNeverCoupledAlways     [Mut # "M_OBSCOUPLE",               *)
(*                                          Mut # "M_AGENTPROPOSES"]           *)
(*   THEOREM SafeAlways                    [Mut = "none"]                      *)
(*                                                                             *)
(* The strengthening. `Shape` holds under every mutation: the type invariant;  *)
(* an id not yet handed out names no act; an act names a vehicle; a delivered  *)
(* id names an act. The four flags of IrreversibleIsAPersons, and OrderedIn-   *)
(* Contact's, are inductive alone, each at the one action that sets it against *)
(* the guard its mutation removes. UsedOnce needs `BindUsed`: every fired id   *)
(* names an act and is in the record of the vehicle that act names. That is    *)
(* what makes a governor's own `used` a global fact, and it rests on the check *)
(* M_ANYVEHICLE removes (the module's header, finding 1). ConflictIsAFinding   *)
(* is inductive alone. ReleaseNeverCoupled holds in every state under its      *)
(* hypothesis and needs no induction: the admit's guard reads neither an agent *)
(* nor an Observer. It is a state lemma, proved BY ExpandENABLED in the one    *)
(* step that states it, with no binder over the ENABLED, so no backend sees an *)
(* unexpanded ENABLED under a quantifier.                                      *)
(*                                                                             *)
(* Mutations and witnesses are behaviours and stay with TLC                    *)
(* (Release-results-*.txt). Check: tools/tlapm --cleanfp --strict.             *)
EXTENDS Release, TLAPS

ASSUME MaxActsNat == MaxActs \in Nat
ASSUME MaxTickNat == MaxTick \in Nat
ASSUME FreshTNat  == FreshT \in Nat

ActRec == [signer : Signers \cup {"none"}, plane : {"cmd", "lite", "none"},
           tick : Nat, vehicle : Vehicles \cup {"none"}]

TypeOK ==
  /\ relLive \in BOOLEAN
  /\ contact \in BOOLEAN
  /\ obsLive \in BOOLEAN
  /\ agentBusy \in BOOLEAN
  /\ tick \in Nat
  /\ nextId \in Nat
  /\ nextId >= 1
  /\ acts \in [Ids -> ActRec]
  /\ delivered \subseteq Ids
  /\ relayRefused \subseteq Ids
  /\ used \in [Vehicles -> SUBSET Ids]
  /\ firedIds \subseteq Ids
  /\ standing \subseteq Ids
  /\ findings \subseteq Ids
  /\ notPerson \in BOOLEAN
  /\ notCommanded \in BOOLEAN
  /\ replayed \in BOOLEAN
  /\ stale \in BOOLEAN
  /\ noContact \in BOOLEAN

NotYet        == \A i \in Ids : i >= nextId => acts[i] = NoAct
ActsWF        == \A i \in Ids : acts[i] # NoAct => acts[i].vehicle \in Vehicles
DeliveredActs == \A i \in delivered : acts[i] # NoAct

Shape == TypeOK /\ NotYet /\ ActsWF /\ DeliveredActs

BindUsed == \A i \in firedIds : acts[i] # NoAct /\ i \in used[acts[i].vehicle]
-----------------------------------------------------------------------------
LEMMA NoActRec == NoAct \in ActRec
  BY DEF NoAct, ActRec

LEMMA ActFacts ==
  ASSUME NEW s \in Signers, NEW pl \in {"cmd", "lite"}, NEW v \in Vehicles, tick \in Nat
  PROVE  /\ Act(s, pl, v) \in ActRec
         /\ Act(s, pl, v) # NoAct
         /\ Act(s, pl, v).vehicle \in Vehicles
  BY DEF Act, ActRec, NoAct, Signers

\* The three actions that write an act, in one shape.
LEMMA NewAct ==
  ASSUME TypeOK, AdmitRelease \/ AdmitAgent \/ \E s \in Signers : LiteOriginate(s)
  PROVE  \E a \in ActRec :
           /\ a # NoAct
           /\ a.vehicle \in Vehicles
           /\ acts' = [acts EXCEPT ![nextId] = a]
           /\ nextId' = nextId + 1
           /\ nextId <= MaxActs
           /\ delivered' = delivered \/ delivered' = delivered \cup {nextId}
           /\ UNCHANGED <<relLive, contact, tick, obsLive, agentBusy, relayRefused,
                          used, firedIds, standing, findings,
                          notPerson, notCommanded, replayed, stale>>
           /\ noContact' \in BOOLEAN
           /\ (noContact' # noContact => AdmitRelease)
<1>1. CASE AdmitRelease
  <2>1. PICK v \in Vehicles : acts' = [acts EXCEPT ![nextId] = Act("person", "cmd", v)]
    BY <1>1 DEF AdmitRelease
  <2>2. /\ Act("person", "cmd", v) \in ActRec /\ Act("person", "cmd", v) # NoAct
        /\ Act("person", "cmd", v).vehicle \in Vehicles
    BY ActFacts DEF TypeOK, Signers
  <2>3. noContact' \in BOOLEAN
    BY <1>1 DEF AdmitRelease, TypeOK
  <2> QED
    BY <1>1, <2>1, <2>2, <2>3 DEF AdmitRelease
<1>2. CASE AdmitAgent
  <2>1. PICK v \in Vehicles : acts' = [acts EXCEPT ![nextId] = Act("agent", "cmd", v)]
    BY <1>2 DEF AdmitAgent
  <2>2. /\ Act("agent", "cmd", v) \in ActRec /\ Act("agent", "cmd", v) # NoAct
        /\ Act("agent", "cmd", v).vehicle \in Vehicles
    BY ActFacts DEF TypeOK, Signers
  <2>3. noContact' = noContact
    BY <1>2 DEF AdmitAgent
  <2>4. noContact' \in BOOLEAN
    BY <2>3 DEF TypeOK
  <2> QED
    BY <1>2, <2>1, <2>2, <2>3, <2>4 DEF AdmitAgent
<1>3. CASE \E s \in Signers : LiteOriginate(s)
  <2>1. PICK s \in Signers : LiteOriginate(s)
    BY <1>3
  <2>2. PICK v \in Vehicles : acts' = [acts EXCEPT ![nextId] = Act(s, "lite", v)]
    BY <2>1 DEF LiteOriginate
  <2>3. /\ Act(s, "lite", v) \in ActRec /\ Act(s, "lite", v) # NoAct
        /\ Act(s, "lite", v).vehicle \in Vehicles
    BY ActFacts DEF TypeOK
  <2>4. noContact' = noContact
    BY <2>1 DEF LiteOriginate
  <2>5. noContact' \in BOOLEAN
    BY <2>4 DEF TypeOK
  <2> QED
    BY <2>1, <2>2, <2>3, <2>4, <2>5 DEF LiteOriginate
<1> QED
  BY <1>1, <1>2, <1>3

LEMMA InitShape == Init => Shape
<1> SUFFICES ASSUME Init PROVE Shape OBVIOUS
<1>1. TypeOK
  BY NoActRec DEF Init, TypeOK
<1>2. NotYet
  BY DEF Init, NotYet
<1>3. ActsWF
  BY DEF Init, ActsWF
<1>4. DeliveredActs
  BY DEF Init, DeliveredActs
<1> QED
  BY <1>1, <1>2, <1>3, <1>4 DEF Shape

\* The actions that touch neither an act nor what was delivered.
Quiet == Activate \/ EndRelease \/ LinkToggle \/ ObsToggle \/ AgentToggle \/ Advance

LEMMA QuietFacts ==
  ASSUME Quiet
  PROVE  UNCHANGED <<nextId, acts, delivered, relayRefused, used, firedIds, standing, findings,
                     notPerson, notCommanded, replayed, stale, noContact>>
  BY DEF Quiet, Activate, EndRelease, LinkToggle, ObsToggle, AgentToggle, Advance

LEMMA QuietType ==
  ASSUME TypeOK, Quiet
  PROVE  TypeOK'
<1>1. UNCHANGED <<nextId, acts, delivered, relayRefused, used, firedIds, standing, findings,
                  notPerson, notCommanded, replayed, stale, noContact>>
  BY QuietFacts
<1>2. /\ relLive' \in BOOLEAN /\ contact' \in BOOLEAN /\ obsLive' \in BOOLEAN /\ agentBusy' \in BOOLEAN /\ tick' \in Nat
  BY DEF Quiet, Activate, EndRelease, LinkToggle, ObsToggle, AgentToggle, Advance, TypeOK
<1> QED
  BY <1>1, <1>2 DEF TypeOK

LEMMA NextShape == Shape /\ [Next]_vars => Shape'
<1> SUFFICES ASSUME Shape, [Next]_vars PROVE Shape' OBVIOUS
<1>0. TypeOK
  BY DEF Shape
<1>1. CASE UNCHANGED vars
  BY <1>1 DEF Shape, TypeOK, NotYet, ActsWF, DeliveredActs, vars
<1>2. CASE Quiet
  <2>1. TypeOK'
    BY <1>0, <1>2, QuietType
  <2>2. UNCHANGED <<nextId, acts, delivered>>
    BY <1>2, QuietFacts
  <2> QED
    BY <2>1, <2>2 DEF Shape, NotYet, ActsWF, DeliveredActs
<1>3. CASE AdmitRelease \/ AdmitAgent \/ \E s \in Signers : LiteOriginate(s)
  <2>1. PICK a \in ActRec :
           /\ a # NoAct
           /\ a.vehicle \in Vehicles
           /\ acts' = [acts EXCEPT ![nextId] = a]
           /\ nextId' = nextId + 1
           /\ nextId <= MaxActs
           /\ delivered' = delivered \/ delivered' = delivered \cup {nextId}
           /\ UNCHANGED <<relLive, contact, tick, obsLive, agentBusy, relayRefused,
                          used, firedIds, standing, findings,
                          notPerson, notCommanded, replayed, stale>>
           /\ noContact' \in BOOLEAN
    BY <1>0, <1>3, NewAct
  <2>2. nextId \in Ids
    BY <1>0, <2>1, MaxActsNat DEF TypeOK, Ids
  <2>3. TypeOK'
    <3>1. acts' \in [Ids -> ActRec]
      BY <1>0, <2>1, <2>2 DEF TypeOK
    <3>2. delivered' \subseteq Ids
      BY <1>0, <2>1, <2>2 DEF TypeOK
    <3>3. nextId' \in Nat /\ nextId' >= 1
      BY <1>0, <2>1 DEF TypeOK
    <3> QED
      BY <1>0, <2>1, <3>1, <3>2, <3>3 DEF TypeOK
  <2>4. NotYet'
    <3> SUFFICES ASSUME NEW i \in Ids, i >= nextId' PROVE acts'[i] = NoAct
      BY DEF NotYet
    <3>1. i # nextId /\ i >= nextId
      BY <1>0, <2>1, MaxActsNat DEF TypeOK, Ids
    <3>2. acts'[i] = acts[i]
      BY <1>0, <2>1, <3>1 DEF TypeOK
    <3> QED
      BY <3>1, <3>2 DEF Shape, NotYet
  <2>5. ActsWF'
    <3> SUFFICES ASSUME NEW i \in Ids, acts'[i] # NoAct PROVE acts'[i].vehicle \in Vehicles
      BY DEF ActsWF
    <3>1. CASE i = nextId
      BY <1>0, <2>1, <2>2, <3>1 DEF TypeOK
    <3>2. CASE i # nextId
      BY <1>0, <2>1, <3>2 DEF Shape, ActsWF, TypeOK
    <3> QED
      BY <3>1, <3>2
  <2>6. DeliveredActs'
    <3> SUFFICES ASSUME NEW i \in delivered' PROVE acts'[i] # NoAct
      BY DEF DeliveredActs
    <3>1. CASE i = nextId
      BY <1>0, <2>1, <2>2, <3>1 DEF TypeOK
    <3>2. CASE i # nextId
      <4>1. i \in delivered
        BY <2>1, <3>2
      <4>2. i \in Ids
        BY <1>0, <4>1 DEF TypeOK
      <4>3. acts'[i] = acts[i]
        BY <1>0, <2>1, <3>2, <4>2 DEF TypeOK
      <4> QED
        BY <4>1, <4>3 DEF Shape, DeliveredActs
    <3> QED
      BY <3>1, <3>2
  <2> QED
    BY <2>3, <2>4, <2>5, <2>6 DEF Shape
<1>4. ASSUME NEW id \in Ids, Relay(id) PROVE Shape'
  <2>1. /\ acts[id] # NoAct
        /\ delivered' = delivered \cup {id}
        /\ UNCHANGED <<relLive, contact, tick, obsLive, agentBusy, nextId, acts, relayRefused,
                       used, firedIds, standing, findings,
                       notPerson, notCommanded, replayed, stale, noContact>>
    BY <1>4 DEF Relay
  <2>2. TypeOK'
    BY <1>0, <2>1 DEF TypeOK
  <2>3. DeliveredActs'
    BY <2>1 DEF Shape, DeliveredActs
  <2> QED
    BY <2>1, <2>2, <2>3 DEF Shape, NotYet, ActsWF
<1>5. ASSUME NEW id \in Ids, RelayRefuse(id) PROVE Shape'
  <2>1. /\ relayRefused' = relayRefused \cup {id}
        /\ UNCHANGED <<relLive, contact, tick, obsLive, agentBusy, nextId, acts, delivered,
                       used, firedIds, standing, findings,
                       notPerson, notCommanded, replayed, stale, noContact>>
    BY <1>5 DEF RelayRefuse
  <2>2. TypeOK'
    BY <1>0, <2>1 DEF TypeOK
  <2> QED
    BY <2>1, <2>2 DEF Shape, NotYet, ActsWF, DeliveredActs
<1>6. ASSUME NEW id \in Ids, CheckFails(id) PROVE Shape'
  <2>1. /\ findings' = findings \cup {id}
        /\ relLive' = FALSE
        /\ standing' \subseteq Ids
        /\ UNCHANGED <<contact, tick, obsLive, agentBusy, nextId, acts, delivered, relayRefused,
                       used, firedIds, notPerson, notCommanded, replayed, stale, noContact>>
    <3>1. standing' = standing \/ standing' = standing \ {id}
      BY <1>6 DEF CheckFails
    <3>2. standing' \subseteq Ids
      BY <1>0, <3>1 DEF TypeOK
    <3> QED
      BY <1>6, <3>2 DEF CheckFails
  <2>2. TypeOK'
    BY <1>0, <2>1 DEF TypeOK
  <2> QED
    BY <2>1, <2>2 DEF Shape, NotYet, ActsWF, DeliveredActs
<1>7. ASSUME NEW v \in Vehicles, NEW id \in Ids, Fire(v, id) PROVE Shape'
  <2>1. /\ notPerson' \in BOOLEAN /\ notCommanded' \in BOOLEAN /\ replayed' \in BOOLEAN /\ stale' \in BOOLEAN
    BY <1>0, <1>7 DEF Fire, TypeOK
  <2>2. /\ used' = [used EXCEPT ![v] = used[v] \cup {id}]
        /\ firedIds' = firedIds \cup {id}
        /\ standing' = standing \cup {id}
        /\ UNCHANGED <<relLive, contact, tick, obsLive, agentBusy, nextId, acts, delivered, relayRefused,
                       findings, noContact>>
    BY <1>7 DEF Fire
  <2>3. used' \in [Vehicles -> SUBSET Ids]
    BY <1>0, <2>2 DEF TypeOK
  <2>4. TypeOK'
    BY <1>0, <2>1, <2>2, <2>3 DEF TypeOK
  <2> QED
    BY <2>2, <2>4 DEF Shape, NotYet, ActsWF, DeliveredActs
<1>8. ASSUME NEW v \in Vehicles, NEW id \in Ids, RefuseAct(v, id) PROVE Shape'
  <2>1. UNCHANGED <<relLive, contact, tick, obsLive, agentBusy, nextId, acts, delivered, relayRefused,
                    used, firedIds, standing, findings,
                    notPerson, notCommanded, replayed, stale, noContact>>
    BY <1>8 DEF RefuseAct
  <2>2. TypeOK'
    BY <1>0, <2>1 DEF TypeOK
  <2> QED
    BY <2>1, <2>2 DEF Shape, NotYet, ActsWF, DeliveredActs
<1> QED
  <2>1. ASSUME Next PROVE Shape'
    <3>1. CASE \E id \in Ids : Relay(id) \/ RelayRefuse(id) \/ CheckFails(id)
      BY <3>1, <1>4, <1>5, <1>6
    <3>2. CASE \E v \in Vehicles, id \in Ids : Fire(v, id) \/ RefuseAct(v, id)
      BY <3>2, <1>7, <1>8
    <3>3. CASE Activate \/ EndRelease \/ LinkToggle \/ ObsToggle \/ AgentToggle \/ Advance
      BY <3>3, <1>2 DEF Quiet
    <3>4. CASE AdmitRelease \/ AdmitAgent \/ \E s \in Signers : LiteOriginate(s)
      BY <3>4, <1>3
    <3> QED
      BY <2>1, <3>1, <3>2, <3>3, <3>4 DEF Next
  <2> QED
    BY <1>1, <2>1 DEF vars
-----------------------------------------------------------------------------
THEOREM ShapeAlways == Spec => []Shape
<1>1. Shape /\ [Next]_vars => Shape'
  BY NextShape
<1> QED
  BY InitShape, <1>1, PTL DEF Spec
-----------------------------------------------------------------------------
(* The flags, each at its one action.                                          *)

\* Only Fire moves the four flags of IrreversibleIsAPersons.
LEMMA FireFrame ==
  ASSUME [Next]_vars
  PROVE  \/ UNCHANGED <<notPerson, notCommanded, replayed, stale>>
         \/ \E v \in Vehicles, id \in Ids : Fire(v, id)
<1>1. CASE UNCHANGED vars
  BY <1>1 DEF vars
<1>2. CASE \E id \in Ids : Relay(id) \/ RelayRefuse(id) \/ CheckFails(id)
  BY <1>2 DEF Relay, RelayRefuse, CheckFails
<1>3. CASE \E v \in Vehicles, id \in Ids : Fire(v, id) \/ RefuseAct(v, id)
  BY <1>3 DEF RefuseAct
<1>4. CASE Activate \/ EndRelease \/ LinkToggle \/ ObsToggle \/ AgentToggle \/ Advance
  BY <1>4, QuietFacts DEF Quiet
<1>5. CASE AdmitRelease \/ AdmitAgent \/ \E s \in Signers : LiteOriginate(s)
  <2>1. CASE AdmitRelease
    BY <2>1 DEF AdmitRelease
  <2>2. CASE AdmitAgent
    BY <2>2 DEF AdmitAgent
  <2>3. CASE \E s \in Signers : LiteOriginate(s)
    BY <2>3 DEF LiteOriginate
  <2> QED
    BY <1>5, <2>1, <2>2, <2>3
<1> QED
  BY <1>1, <1>2, <1>3, <1>4, <1>5 DEF Next

LEMMA NextSignedByPerson ==
  ASSUME Mut # "M_AGENTRELEASE", SignedByPerson, [Next]_vars
  PROVE  SignedByPerson'
<1>1. CASE UNCHANGED <<notPerson, notCommanded, replayed, stale>>
  BY <1>1 DEF SignedByPerson
<1>2. CASE \E v \in Vehicles, id \in Ids : Fire(v, id)
  BY <1>2 DEF Fire, Interlock, KeyOK, SignedByPerson
<1> QED
  BY <1>1, <1>2, FireFrame

THEOREM SignedByPersonAlways ==
  ASSUME Mut # "M_AGENTRELEASE"
  PROVE  Spec => []SignedByPerson
<1>1. SignedByPerson /\ [Next]_vars => SignedByPerson'
  BY NextSignedByPerson
<1>2. Init => SignedByPerson
  BY DEF Init, SignedByPerson
<1> QED
  BY <1>1, <1>2, PTL DEF Spec

LEMMA NextOrderedAtCommand ==
  ASSUME Mut # "M_LITERELEASE", OrderedAtCommand, [Next]_vars
  PROVE  OrderedAtCommand'
<1>1. CASE UNCHANGED <<notPerson, notCommanded, replayed, stale>>
  BY <1>1 DEF OrderedAtCommand
<1>2. CASE \E v \in Vehicles, id \in Ids : Fire(v, id)
  BY <1>2 DEF Fire, Interlock, CertOK, OrderedAtCommand
<1> QED
  BY <1>1, <1>2, FireFrame

THEOREM OrderedAtCommandAlways ==
  ASSUME Mut # "M_LITERELEASE"
  PROVE  Spec => []OrderedAtCommand
<1>1. OrderedAtCommand /\ [Next]_vars => OrderedAtCommand'
  BY NextOrderedAtCommand
<1>2. Init => OrderedAtCommand
  BY DEF Init, OrderedAtCommand
<1> QED
  BY <1>1, <1>2, PTL DEF Spec

LEMMA NextNoOlderThanDeclared ==
  ASSUME Mut # "M_LATEFIRST", NoOlderThanDeclared, [Next]_vars, Shape
  PROVE  NoOlderThanDeclared'
<1>1. CASE UNCHANGED <<notPerson, notCommanded, replayed, stale>>
  BY <1>1 DEF NoOlderThanDeclared
<1>2. CASE \E v \in Vehicles, id \in Ids : Fire(v, id)
  <2>1. PICK v \in Vehicles, id \in Ids : Fire(v, id)
    BY <1>2
  <2>2. tick <= acts[id].tick + FreshT
    BY <2>1 DEF Fire, Interlock, FreshOK
  <2>3. tick \in Nat /\ acts[id].tick \in Nat
    BY DEF Shape, TypeOK, ActRec
  <2>4. ~(tick > acts[id].tick + FreshT)
    BY <2>2, <2>3, FreshTNat
  <2> QED
    BY <2>1, <2>4 DEF Fire, NoOlderThanDeclared
<1> QED
  BY <1>1, <1>2, FireFrame

InvFresh == Shape /\ NoOlderThanDeclared

THEOREM NoOlderThanDeclaredAlways ==
  ASSUME Mut # "M_LATEFIRST"
  PROVE  Spec => []NoOlderThanDeclared
<1>1. InvFresh /\ [Next]_vars => InvFresh'
  <2> SUFFICES ASSUME InvFresh, [Next]_vars PROVE InvFresh' OBVIOUS
  <2>1. Shape'
    BY NextShape DEF InvFresh
  <2>2. NoOlderThanDeclared'
    BY NextNoOlderThanDeclared DEF InvFresh
  <2> QED
    BY <2>1, <2>2 DEF InvFresh
<1>2. Init => InvFresh
  BY InitShape DEF Init, InvFresh, NoOlderThanDeclared
<1>3. InvFresh => NoOlderThanDeclared
  BY DEF InvFresh
<1> QED
  BY <1>1, <1>2, <1>3, PTL DEF Spec
-----------------------------------------------------------------------------
(* UsedOnce: every fired id is in the record of the vehicle its act names.     *)

InvOnce == Shape /\ BindUsed /\ UsedOnce

LEMMA InitOnce == Init => InvOnce
<1> SUFFICES ASSUME Init PROVE InvOnce OBVIOUS
<1>1. Shape
  BY InitShape
<1>2. BindUsed
  BY DEF Init, BindUsed
<1>3. UsedOnce
  BY DEF Init, UsedOnce
<1> QED
  BY <1>1, <1>2, <1>3 DEF InvOnce

LEMMA NextOnce ==
  ASSUME Mut # "M_REPLAY", Mut # "M_ANYVEHICLE", InvOnce, [Next]_vars
  PROVE  InvOnce'
<1>0. Shape /\ Shape' /\ BindUsed /\ UsedOnce
  BY NextShape DEF InvOnce
<1>a. TypeOK /\ TypeOK'
  BY <1>0 DEF Shape
<1>1. CASE UNCHANGED <<acts, used, firedIds, replayed>>
  <2>1. BindUsed' /\ UsedOnce'
    BY <1>0, <1>1 DEF BindUsed, UsedOnce
  <2> QED
    BY <1>0, <2>1 DEF InvOnce
<1>2. CASE AdmitRelease \/ AdmitAgent \/ \E s \in Signers : LiteOriginate(s)
  <2>1. PICK a \in ActRec :
           /\ a # NoAct
           /\ acts' = [acts EXCEPT ![nextId] = a]
           /\ UNCHANGED <<used, firedIds, replayed>>
    BY <1>a, <1>2, NewAct
  <2>2. BindUsed'
    <3> SUFFICES ASSUME NEW i \in firedIds' PROVE acts'[i] # NoAct /\ i \in used'[acts'[i].vehicle]
      BY DEF BindUsed
    <3>1. i \in firedIds /\ i \in Ids
      BY <1>a, <2>1 DEF TypeOK
    <3>2. acts[i] # NoAct /\ i \in used[acts[i].vehicle]
      BY <1>0, <3>1 DEF BindUsed
    <3>3. i < nextId
      <4>1. ~(i >= nextId)
        BY <1>0, <3>1, <3>2 DEF Shape, NotYet
      <4> QED
        BY <1>a, <3>1, <4>1, MaxActsNat DEF TypeOK, Ids
    <3>4. i # nextId
      BY <1>a, <3>1, <3>3, MaxActsNat DEF TypeOK, Ids
    <3>5. acts'[i] = acts[i]
      BY <1>a, <2>1, <3>1, <3>4 DEF TypeOK
    <3> QED
      BY <2>1, <3>2, <3>5
  <2>3. UsedOnce'
    BY <1>0, <2>1 DEF UsedOnce
  <2> QED
    BY <1>0, <2>2, <2>3 DEF InvOnce
<1>3. ASSUME NEW v \in Vehicles, NEW id \in Ids, Fire(v, id) PROVE InvOnce'
  <2>1. /\ id \notin used[v]
        /\ acts[id].vehicle = v
        /\ id \in delivered
        /\ UNCHANGED acts
        /\ used' = [used EXCEPT ![v] = used[v] \cup {id}]
        /\ firedIds' = firedIds \cup {id}
        /\ replayed' = (replayed \/ id \in firedIds)
    BY <1>3 DEF Fire, Interlock, UnusedOK, VehicleOK
  <2>2. id \notin firedIds
    <3>1. SUFFICES ASSUME id \in firedIds PROVE FALSE
      OBVIOUS
    <3>2. id \in used[acts[id].vehicle]
      BY <1>0, <3>1 DEF BindUsed
    <3> QED
      BY <2>1, <3>2
  <2>3. UsedOnce'
    BY <1>0, <2>1, <2>2 DEF UsedOnce
  <2>4. acts[id] # NoAct
    BY <1>0, <2>1 DEF Shape, DeliveredActs
  <2>5. BindUsed'
    <3> SUFFICES ASSUME NEW i \in firedIds' PROVE acts'[i] # NoAct /\ i \in used'[acts'[i].vehicle]
      BY DEF BindUsed
    <3>1. CASE i = id
      BY <1>a, <2>1, <2>4, <3>1 DEF TypeOK
    <3>2. CASE i # id
      <4>1. i \in firedIds /\ i \in Ids
        BY <1>a, <2>1, <3>2 DEF TypeOK
      <4>2. acts[i] # NoAct /\ i \in used[acts[i].vehicle]
        BY <1>0, <4>1 DEF BindUsed
      <4>3. acts[i].vehicle \in Vehicles
        BY <1>0, <4>1, <4>2 DEF Shape, ActsWF
      <4>4. used[acts[i].vehicle] \subseteq used'[acts[i].vehicle]
        BY <1>a, <2>1, <4>3 DEF TypeOK
      <4> QED
        BY <2>1, <4>2, <4>4
    <3> QED
      BY <3>1, <3>2
  <2> QED
    BY <1>0, <2>3, <2>5 DEF InvOnce
<1>4. CASE [Next]_vars
  <2>1. CASE AdmitRelease \/ AdmitAgent \/ \E s \in Signers : LiteOriginate(s)
    BY <2>1, <1>2
  <2>2. CASE \E v \in Vehicles, id \in Ids : Fire(v, id)
    BY <2>2, <1>3
  <2>3. CASE /\ ~(AdmitRelease \/ AdmitAgent \/ \E s \in Signers : LiteOriginate(s))
             /\ ~\E v \in Vehicles, id \in Ids : Fire(v, id)
    <3>1. UNCHANGED <<acts, used, firedIds, replayed>>
      <4>1. CASE UNCHANGED vars
        BY <4>1 DEF vars
      <4>2. CASE \E id \in Ids : Relay(id) \/ RelayRefuse(id) \/ CheckFails(id)
        BY <4>2 DEF Relay, RelayRefuse, CheckFails
      <4>3. CASE \E v \in Vehicles, id \in Ids : Fire(v, id) \/ RefuseAct(v, id)
        BY <2>3, <4>3 DEF RefuseAct
      <4>4. CASE Activate \/ EndRelease \/ LinkToggle \/ ObsToggle \/ AgentToggle \/ Advance
        BY <4>4, QuietFacts DEF Quiet
      <4> QED
        BY <2>3, <4>1, <4>2, <4>3, <4>4 DEF Next
    <3> QED
      BY <3>1, <1>1
  <2> QED
    BY <2>1, <2>2, <2>3
<1> QED
  BY <1>4

THEOREM UsedOnceAlways ==
  ASSUME Mut # "M_REPLAY", Mut # "M_ANYVEHICLE"
  PROVE  Spec => []UsedOnce
<1>1. InvOnce /\ [Next]_vars => InvOnce'
  BY NextOnce
<1>2. InvOnce => UsedOnce
  BY DEF InvOnce
<1> QED
  BY InitOnce, <1>1, <1>2, PTL DEF Spec

THEOREM IrreversibleIsAPersonsAlways ==
  ASSUME Mut # "M_AGENTRELEASE", Mut # "M_LITERELEASE", Mut # "M_REPLAY",
         Mut # "M_ANYVEHICLE", Mut # "M_LATEFIRST"
  PROVE  Spec => []IrreversibleIsAPersons
<1>1. Spec => []SignedByPerson
  BY SignedByPersonAlways
<1>2. Spec => []OrderedAtCommand
  BY OrderedAtCommandAlways
<1>3. Spec => []UsedOnce
  BY UsedOnceAlways
<1>4. Spec => []NoOlderThanDeclared
  BY NoOlderThanDeclaredAlways
<1> QED
  BY <1>1, <1>2, <1>3, <1>4, PTL DEF IrreversibleIsAPersons
-----------------------------------------------------------------------------
(* ConflictIsAFinding: only Fire and CheckFails move what is fired or standing,*)
(* and a failed check leaves what stands.                                      *)

LEMMA ConflictFrame ==
  ASSUME [Next]_vars
  PROVE  \/ UNCHANGED <<firedIds, standing>>
         \/ \E v \in Vehicles, id \in Ids : Fire(v, id)
         \/ \E id \in Ids : CheckFails(id)
<1>1. CASE UNCHANGED vars
  BY <1>1 DEF vars
<1>2. CASE \E id \in Ids : Relay(id) \/ RelayRefuse(id) \/ CheckFails(id)
  BY <1>2 DEF Relay, RelayRefuse
<1>3. CASE \E v \in Vehicles, id \in Ids : Fire(v, id) \/ RefuseAct(v, id)
  BY <1>3 DEF RefuseAct
<1>4. CASE Activate \/ EndRelease \/ LinkToggle \/ ObsToggle \/ AgentToggle \/ Advance
  BY <1>4, QuietFacts DEF Quiet
<1>5. CASE AdmitRelease \/ AdmitAgent \/ \E s \in Signers : LiteOriginate(s)
  <2>1. CASE AdmitRelease
    BY <2>1 DEF AdmitRelease
  <2>2. CASE AdmitAgent
    BY <2>2 DEF AdmitAgent
  <2>3. CASE \E s \in Signers : LiteOriginate(s)
    BY <2>3 DEF LiteOriginate
  <2> QED
    BY <1>5, <2>1, <2>2, <2>3
<1> QED
  BY <1>1, <1>2, <1>3, <1>4, <1>5 DEF Next

LEMMA NextConflict ==
  ASSUME Mut # "M_VOID", ConflictIsAFinding, [Next]_vars
  PROVE  ConflictIsAFinding'
<1>1. CASE UNCHANGED <<firedIds, standing>>
  BY <1>1 DEF ConflictIsAFinding
<1>2. CASE \E v \in Vehicles, id \in Ids : Fire(v, id)
  <2>1. PICK v \in Vehicles, id \in Ids : Fire(v, id)
    BY <1>2
  <2>2. firedIds' = firedIds \cup {id} /\ standing' = standing \cup {id}
    BY <2>1 DEF Fire
  <2> QED
    BY <2>2 DEF ConflictIsAFinding
<1>3. CASE \E id \in Ids : CheckFails(id)
  <2>1. PICK id \in Ids : CheckFails(id)
    BY <1>3
  <2>2. firedIds' = firedIds /\ standing' = standing
    BY <2>1 DEF CheckFails
  <2> QED
    BY <2>2 DEF ConflictIsAFinding
<1> QED
  BY <1>1, <1>2, <1>3, ConflictFrame

THEOREM ConflictIsAFindingAlways ==
  ASSUME Mut # "M_VOID"
  PROVE  Spec => []ConflictIsAFinding
<1>1. ConflictIsAFinding /\ [Next]_vars => ConflictIsAFinding'
  BY NextConflict
<1>2. Init => ConflictIsAFinding
  BY DEF Init, ConflictIsAFinding
<1> QED
  BY <1>1, <1>2, PTL DEF Spec
-----------------------------------------------------------------------------
(* OrderedInContact: only AdmitRelease moves the flag.                         *)

LEMMA ContactFrame ==
  ASSUME [Next]_vars
  PROVE  UNCHANGED noContact \/ AdmitRelease
<1>1. CASE UNCHANGED vars
  BY <1>1 DEF vars
<1>2. CASE \E id \in Ids : Relay(id) \/ RelayRefuse(id) \/ CheckFails(id)
  BY <1>2 DEF Relay, RelayRefuse, CheckFails
<1>3. CASE \E v \in Vehicles, id \in Ids : Fire(v, id) \/ RefuseAct(v, id)
  BY <1>3 DEF Fire, RefuseAct
<1>4. CASE Activate \/ EndRelease \/ LinkToggle \/ ObsToggle \/ AgentToggle \/ Advance
  BY <1>4, QuietFacts DEF Quiet
<1>5. CASE AdmitAgent \/ \E s \in Signers : LiteOriginate(s)
  <2>1. CASE AdmitAgent
    BY <2>1 DEF AdmitAgent
  <2>2. CASE \E s \in Signers : LiteOriginate(s)
    BY <2>2 DEF LiteOriginate
  <2> QED
    BY <1>5, <2>1, <2>2
<1> QED
  BY <1>1, <1>2, <1>3, <1>4, <1>5 DEF Next

LEMMA NextOrderedInContact ==
  ASSUME Mut # "M_NOCONTACT", OrderedInContact, [Next]_vars
  PROVE  OrderedInContact'
<1>1. CASE UNCHANGED noContact
  BY <1>1 DEF OrderedInContact
<1>2. CASE AdmitRelease
  BY <1>2 DEF AdmitRelease, LinkOK, OrderedInContact
<1> QED
  BY <1>1, <1>2, ContactFrame

THEOREM OrderedInContactAlways ==
  ASSUME Mut # "M_NOCONTACT"
  PROVE  Spec => []OrderedInContact
<1>1. OrderedInContact /\ [Next]_vars => OrderedInContact'
  BY NextOrderedInContact
<1>2. Init => OrderedInContact
  BY DEF Init, OrderedInContact
<1> QED
  BY <1>1, <1>2, PTL DEF Spec
-----------------------------------------------------------------------------
(* ReleaseNeverCoupled: valid in every state under its hypothesis.             *)

LEMMA ReleaseNeverCoupledValid ==
  ASSUME Mut # "M_OBSCOUPLE", Mut # "M_AGENTPROPOSES"
  PROVE  ReleaseNeverCoupled
BY ExpandENABLED, Isa DEF ReleaseNeverCoupled, AdmitRelease, LinkOK, Uncoupled, Vehicles

THEOREM ReleaseNeverCoupledAlways ==
  ASSUME Mut # "M_OBSCOUPLE", Mut # "M_AGENTPROPOSES"
  PROVE  Spec => []ReleaseNeverCoupled
<1>1. ReleaseNeverCoupled
  BY ReleaseNeverCoupledValid
<1> QED
  BY <1>1, PTL
-----------------------------------------------------------------------------
THEOREM SafeAlways ==
  ASSUME Mut = "none"
  PROVE  Spec => []Safe
<1>1. Spec => []IrreversibleIsAPersons
  BY IrreversibleIsAPersonsAlways
<1>2. Spec => []ConflictIsAFinding
  BY ConflictIsAFindingAlways
<1>3. Spec => []OrderedInContact
  BY OrderedInContactAlways
<1> QED
  BY <1>1, <1>2, <1>3, PTL DEF Safe
-----------------------------------------------------------------------------
(* Why the mutations must fail. The counterexamples are TLC's.                 *)

LEMMA MutAgentReleaseSkipsTheKey ==
  ASSUME Mut = "M_AGENTRELEASE", NEW id
  PROVE  KeyOK(id)
  BY DEF KeyOK

LEMMA MutLiteReleaseTakesAnyCertificate ==
  ASSUME Mut = "M_LITERELEASE", NEW id
  PROVE  CertOK(id)
  BY DEF CertOK

LEMMA MutReplayIgnoresUsed ==
  ASSUME Mut = "M_REPLAY", NEW v, NEW id
  PROVE  UnusedOK(v, id)
  BY DEF UnusedOK

LEMMA MutAnyVehicleIgnoresTheVehicle ==
  ASSUME Mut = "M_ANYVEHICLE", NEW v, NEW id
  PROVE  VehicleOK(v, id)
  BY DEF VehicleOK

LEMMA MutLateFirstIgnoresTheTicks ==
  ASSUME Mut = "M_LATEFIRST", NEW id
  PROVE  FreshOK(id)
  BY DEF FreshOK

LEMMA MutNoContactAdmitsCut ==
  ASSUME Mut = "M_NOCONTACT"
  PROVE  LinkOK
  BY DEF LinkOK

LEMMA MutVoidRemovesFromStanding ==
  ASSUME Mut = "M_VOID", NEW id, CheckFails(id)
  PROVE  standing' = standing \ {id}
  BY DEF CheckFails

LEMMA MutObsCoupleNeedsObserver ==
  ASSUME Mut = "M_OBSCOUPLE", ~obsLive
  PROVE  ~Uncoupled
  BY DEF Uncoupled

LEMMA MutAgentProposesNeedsAgent ==
  ASSUME Mut = "M_AGENTPROPOSES", ~agentBusy
  PROVE  ~Uncoupled
  BY DEF Uncoupled
=============================================================================
