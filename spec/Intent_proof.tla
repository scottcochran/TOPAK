----------------------------- MODULE Intent_proof -----------------------------
(* TLAPS proof of the invariants of Intent.tla (ADR-0060 §7, ADR-0062 §2), for *)
(* every value of the constants the assumptions below admit: every set of      *)
(* vehicles, every seating budget, every count, and every value of the bounds  *)
(* that only cut the state space. Intent.tla is not edited.                    *)
(*                                                                             *)
(*   THEOREM EveryEffectHasAnIntentAlways [Mut # "M_NOINTENT"]                 *)
(*   THEOREM EveryEffectHasALeaseAlways   [Mut # "M_NOCOUNT"]                  *)
(*   THEOREM IntentNarrowsAlways          [Mut # "M_WIDEINTENT"]               *)
(*   THEOREM AutonomousAddsNothingAlways  [Mut # "M_LITEPROMOTES"]             *)
(*   THEOREM SafeAlways                   [Mut = "none"]                       *)
(*                                                                             *)
(* The strengthening. Each property is over an append-only set, and each is    *)
(* inductive once one state fact says what the appending action can append.    *)
(* EveryEffectHasAnIntent needs that a live intent is in `ordered` under its   *)
(* round, and that a live lease names an intent in `ordered`: an effect takes  *)
(* its intent from its lease, a lease from the live intent, and `ordered` only *)
(* grows. EveryEffectHasALease needs that a live lease is in `granted` with    *)
(* its generation and count, and that a lease's use is at most its count: the  *)
(* guard M_NOCOUNT removes. IntentNarrows carries the current intent's         *)
(* envelope within the seating, which M_LASTINTENT's guard reads, so the       *)
(* theorem covers that mutation as well. AutonomousAddsNothing is inductive    *)
(* alone: the one appending action that takes a proposed kind is guarded by    *)
(* Admissible. The type invariant holds under every mutation; `log` and `seen` *)
(* are outside it, since no step reads their type.                             *)
(*                                                                             *)
(* Mutations and witnesses are behaviours and stay with TLC                    *)
(* (Intent-results-*.txt). Check: tools/tlapm --cleanfp --strict.              *)
EXTENDS Intent, TLAPS

ASSUME SeatingBudgetNat == SeatingBudget \in Nat
ASSUME MaxCountNat      == MaxCount \in Nat

IntentRec  == [live : BOOLEAN, envelope : SUBSET Entries, budget : Nat]
LeaseRec   == [live : BOOLEAN, gen : Nat, count : Nat, used : Nat, intent : Nat]
OrderedRec == [round : Nat, envelope : SUBSET Entries, budget : Nat]
GrantRec   == [v : Vehicles, gen : Nat, count : Nat, intent : Nat]
EffectRec  == [v : Vehicles, gen : Nat, n : Nat, intent : Nat]

TypeOK ==
  /\ round \in Nat
  /\ intent \in IntentRec
  /\ spent \in Nat
  /\ lease \in [Vehicles -> LeaseRec]
  /\ ordered \subseteq OrderedRec
  /\ granted \subseteq GrantRec
  /\ effects \subseteq EffectRec

LiveOrdered    == intent.live => \E j \in ordered : j.round = round
LeaseHasIntent == \A w \in Vehicles : lease[w].live => \E j \in ordered : j.round = lease[w].intent
InvI == TypeOK /\ LiveOrdered /\ LeaseHasIntent /\ EveryEffectHasAnIntent

LeaseGranted ==
  \A w \in Vehicles :
    lease[w].live => \E h \in granted : h.v = w /\ h.gen = lease[w].gen /\ h.count = lease[w].count
UsedLe == \A w \in Vehicles : lease[w].used <= lease[w].count
InvL == TypeOK /\ LeaseGranted /\ UsedLe /\ EveryEffectHasALease

IntentInSeating == round >= 1 => intent.envelope \subseteq SeatingEnvelope
InvN == TypeOK /\ IntentInSeating /\ IntentNarrows
-----------------------------------------------------------------------------
LEMMA IntentSpaceFacts ==
  ASSUME NEW o \in IntentSpace
  PROVE  o.envelope \subseteq Entries /\ o.budget \in Nat
  BY SeatingBudgetNat DEF IntentSpace

LEMMA CountFacts ==
  ASSUME NEW c \in 1..MaxCount
  PROVE  c \in Nat
  BY MaxCountNat

LEMMA NoLeaseFacts == NoLease \in LeaseRec
  BY DEF NoLease, LeaseRec

LEMMA NoIntentFacts == NoIntent \in IntentRec
  BY DEF NoIntent, IntentRec

LEMMA InitTypeOK == Init => TypeOK
  BY NoLeaseFacts, NoIntentFacts DEF Init, TypeOK

LEMMA LiveRoundNat == TypeOK => LiveRound \in Nat
  BY DEF TypeOK, LiveRound

LEMMA NextTypeOK == TypeOK /\ [Next]_vars => TypeOK'
<1> SUFFICES ASSUME TypeOK, [Next]_vars PROVE TypeOK' OBVIOUS
<1>1. CASE UNCHANGED vars
  BY <1>1 DEF TypeOK, vars
<1>2. ASSUME NEW o \in IntentSpace, Order(o) PROVE TypeOK'
  <2>1. o.envelope \subseteq Entries /\ o.budget \in Nat
    BY IntentSpaceFacts
  <2>2. /\ round' = round + 1
        /\ intent' = [live |-> TRUE, envelope |-> o.envelope, budget |-> o.budget]
        /\ spent' = 0
        /\ ordered' = ordered \cup {[round |-> round + 1, envelope |-> o.envelope, budget |-> o.budget]}
        /\ UNCHANGED <<lease, granted, effects>>
    BY <1>2 DEF Order
  <2>3. round' \in Nat /\ intent' \in IntentRec /\ spent' \in Nat
    BY <2>1, <2>2 DEF TypeOK, IntentRec
  <2>4. ordered' \subseteq OrderedRec
    BY <2>1, <2>2 DEF TypeOK, OrderedRec
  <2> QED
    BY <2>2, <2>3, <2>4 DEF TypeOK
<1>3. ASSUME NEW o \in IntentSpace, RefuseOrder(o) PROVE TypeOK'
  BY <1>3 DEF RefuseOrder, TypeOK
<1>4. CASE EndIntent
  <2>1. /\ intent' = [intent EXCEPT !.live = FALSE]
        /\ UNCHANGED <<round, spent, lease, ordered, granted, effects>>
    BY <1>4 DEF EndIntent
  <2>2. intent' \in IntentRec
    BY <2>1 DEF TypeOK, IntentRec
  <2> QED
    BY <2>1, <2>2 DEF TypeOK
<1>5. ASSUME NEW v \in Vehicles, NEW c \in 1..MaxCount, Grant(v, c) PROVE TypeOK'
  <2>1. c \in Nat /\ LiveRound \in Nat
    BY CountFacts, LiveRoundNat
  <2>2. /\ lease' = [lease EXCEPT ![v] = [live |-> TRUE, gen |-> lease[v].gen + 1, count |-> c,
                                          used |-> 0, intent |-> LiveRound]]
        /\ spent' = IF intent.live THEN spent + 1 ELSE spent
        /\ granted' = granted \cup {[v |-> v, gen |-> lease[v].gen + 1, count |-> c, intent |-> LiveRound]}
        /\ UNCHANGED <<round, intent, ordered, effects>>
    BY <1>5 DEF Grant
  <2>3. lease[v] \in LeaseRec /\ lease[v].gen \in Nat
    BY DEF TypeOK, LeaseRec
  <2>4. lease' \in [Vehicles -> LeaseRec]
    BY <2>1, <2>2, <2>3 DEF TypeOK, LeaseRec
  <2>5. spent' \in Nat
    BY <2>2 DEF TypeOK
  <2>6. granted' \subseteq GrantRec
    BY <2>1, <2>2, <2>3 DEF TypeOK, GrantRec
  <2> QED
    BY <2>2, <2>4, <2>5, <2>6 DEF TypeOK
<1>6. ASSUME NEW v \in Vehicles, Effect(v) PROVE TypeOK'
  <2>1. /\ effects' = effects \cup {[v |-> v, gen |-> lease[v].gen, n |-> lease[v].used + 1,
                                     intent |-> lease[v].intent]}
        /\ lease' = [lease EXCEPT ![v].used = lease[v].used + 1]
        /\ UNCHANGED <<round, intent, spent, ordered, granted>>
    BY <1>6 DEF Effect
  <2>2. lease[v] \in LeaseRec /\ lease[v].used \in Nat /\ lease[v].gen \in Nat /\ lease[v].intent \in Nat
    BY DEF TypeOK, LeaseRec
  <2>3. lease' \in [Vehicles -> LeaseRec]
    BY <2>1, <2>2 DEF TypeOK, LeaseRec
  <2>4. effects' \subseteq EffectRec
    BY <2>1, <2>2 DEF TypeOK, EffectRec
  <2> QED
    BY <2>1, <2>3, <2>4 DEF TypeOK
<1>7. ASSUME NEW v \in Vehicles, RefuseGrant(v) \/ RefuseEffect(v) PROVE TypeOK'
  BY <1>7 DEF RefuseGrant, RefuseEffect, TypeOK
<1>8. ASSUME NEW v \in Vehicles, EndLease(v) PROVE TypeOK'
  <2>1. /\ lease' = [lease EXCEPT ![v].live = FALSE]
        /\ UNCHANGED <<round, intent, spent, ordered, granted, effects>>
    BY <1>8 DEF EndLease
  <2>2. lease[v] \in LeaseRec
    BY DEF TypeOK
  <2>3. lease' \in [Vehicles -> LeaseRec]
    BY <2>1, <2>2 DEF TypeOK, LeaseRec
  <2> QED
    BY <2>1, <2>3 DEF TypeOK
<1>9. ASSUME NEW k \in LogKinds, AutoOrder(k) \/ AutoRefuse(k) PROVE TypeOK'
  BY <1>9 DEF AutoOrder, AutoRefuse, TypeOK
<1> QED
  BY <1>1, <1>2, <1>3, <1>4, <1>5, <1>6, <1>7, <1>8, <1>9 DEF Next

\* The actions that touch none of the state the first three invariants read.
LEMMA QuietOrder ==
  ASSUME NEW o \in IntentSpace, RefuseOrder(o)
  PROVE  UNCHANGED <<round, intent, spent, lease, ordered, granted, effects>>
  BY DEF RefuseOrder

LEMMA QuietVehicle ==
  ASSUME NEW v \in Vehicles, RefuseGrant(v) \/ RefuseEffect(v)
  PROVE  UNCHANGED <<round, intent, spent, lease, ordered, granted, effects>>
  BY DEF RefuseGrant, RefuseEffect

LEMMA QuietLog ==
  ASSUME NEW k \in LogKinds, AutoOrder(k) \/ AutoRefuse(k)
  PROVE  UNCHANGED <<round, intent, spent, lease, ordered, granted, effects>>
  BY DEF AutoOrder, AutoRefuse
-----------------------------------------------------------------------------
(* EveryEffectHasAnIntent.                                                     *)

LEMMA InitInvI == Init => InvI
  BY InitTypeOK DEF Init, InvI, LiveOrdered, LeaseHasIntent, EveryEffectHasAnIntent, NoIntent, NoLease

LEMMA NextInvI ==
  ASSUME Mut # "M_NOINTENT", InvI, [Next]_vars
  PROVE  InvI'
<1>0. TypeOK /\ TypeOK' /\ LiveOrdered /\ LeaseHasIntent /\ EveryEffectHasAnIntent
  BY NextTypeOK DEF InvI
<1>a. ASSUME UNCHANGED <<round, intent, spent, lease, ordered, granted, effects>> PROVE InvI'
  BY <1>0, <1>a DEF InvI, LiveOrdered, LeaseHasIntent, EveryEffectHasAnIntent
<1>1. CASE UNCHANGED vars
  BY <1>1, <1>a DEF vars
<1>2. ASSUME NEW o \in IntentSpace, Order(o) PROVE InvI'
  <2> DEFINE r == [round |-> round + 1, envelope |-> o.envelope, budget |-> o.budget]
  <2>1. /\ round' = round + 1
        /\ intent'.live
        /\ ordered' = ordered \cup {r}
        /\ UNCHANGED <<lease, effects>>
    BY <1>2 DEF Order
  <2>2. LiveOrdered'
    <3>1. r \in ordered' /\ r.round = round'
      BY <2>1
    <3> QED
      BY <3>1 DEF LiveOrdered
  <2>3. LeaseHasIntent'
    <3> SUFFICES ASSUME NEW w \in Vehicles, lease'[w].live
                 PROVE  \E j \in ordered' : j.round = lease'[w].intent
      BY DEF LeaseHasIntent
    <3>1. PICK h \in ordered : h.round = lease[w].intent
      BY <1>0, <2>1 DEF LeaseHasIntent
    <3>2. h \in ordered'
      BY <2>1
    <3> QED
      BY <2>1, <3>1, <3>2
  <2>4. EveryEffectHasAnIntent'
    <3> SUFFICES ASSUME NEW y \in effects'
                 PROVE  \E j \in ordered' : j.round = y.intent
      BY DEF EveryEffectHasAnIntent
    <3>1. PICK h \in ordered : h.round = y.intent
      BY <1>0, <2>1 DEF EveryEffectHasAnIntent
    <3>2. h \in ordered'
      BY <2>1
    <3> QED
      BY <3>1, <3>2
  <2> QED
    BY <1>0, <2>2, <2>3, <2>4 DEF InvI
<1>3. ASSUME NEW o \in IntentSpace, RefuseOrder(o) PROVE InvI'
  BY <1>3, <1>a, QuietOrder
<1>4. CASE EndIntent
  <2>1. /\ intent' = [intent EXCEPT !.live = FALSE]
        /\ UNCHANGED <<round, lease, ordered, effects>>
    BY <1>4 DEF EndIntent
  <2>2. ~intent'.live
    BY <1>0, <2>1 DEF TypeOK, IntentRec
  <2>3. LiveOrdered'
    BY <2>2 DEF LiveOrdered
  <2>4. LeaseHasIntent' /\ EveryEffectHasAnIntent'
    BY <1>0, <2>1 DEF LeaseHasIntent, EveryEffectHasAnIntent
  <2> QED
    BY <1>0, <2>3, <2>4 DEF InvI
<1>5. ASSUME NEW v \in Vehicles, NEW c \in 1..MaxCount, Grant(v, c) PROVE InvI'
  <2>1. /\ intent.live
        /\ LiveRound = round
        /\ lease' = [lease EXCEPT ![v] = [live |-> TRUE, gen |-> lease[v].gen + 1, count |-> c,
                                          used |-> 0, intent |-> LiveRound]]
        /\ UNCHANGED <<round, intent, ordered, effects>>
    BY <1>5 DEF Grant, LiveOK, LiveRound
  <2>2. LiveOrdered'
    BY <1>0, <2>1 DEF LiveOrdered
  <2>3. LeaseHasIntent'
    <3> SUFFICES ASSUME NEW w \in Vehicles, lease'[w].live
                 PROVE  \E j \in ordered' : j.round = lease'[w].intent
      BY DEF LeaseHasIntent
    <3>1. CASE w = v
      <4>1. lease'[w].intent = round
        BY <1>0, <2>1, <3>1 DEF TypeOK
      <4>2. PICK h \in ordered : h.round = round
        BY <1>0, <2>1 DEF LiveOrdered
      <4> QED
        BY <2>1, <4>1, <4>2
    <3>2. CASE w # v
      <4>1. lease'[w] = lease[w]
        BY <1>0, <2>1, <3>2 DEF TypeOK
      <4>2. PICK h \in ordered : h.round = lease[w].intent
        BY <1>0, <4>1 DEF LeaseHasIntent
      <4> QED
        BY <2>1, <4>1, <4>2
    <3> QED
      BY <3>1, <3>2
  <2>4. EveryEffectHasAnIntent'
    BY <1>0, <2>1 DEF EveryEffectHasAnIntent
  <2> QED
    BY <1>0, <2>2, <2>3, <2>4 DEF InvI
<1>6. ASSUME NEW v \in Vehicles, Effect(v) PROVE InvI'
  <2>1. /\ lease[v].live
        /\ effects' = effects \cup {[v |-> v, gen |-> lease[v].gen, n |-> lease[v].used + 1,
                                     intent |-> lease[v].intent]}
        /\ lease' = [lease EXCEPT ![v].used = lease[v].used + 1]
        /\ UNCHANGED <<round, intent, ordered>>
    BY <1>6 DEF Effect
  <2>2. LiveOrdered'
    BY <1>0, <2>1 DEF LiveOrdered
  <2>3. LeaseHasIntent'
    <3> SUFFICES ASSUME NEW w \in Vehicles, lease'[w].live
                 PROVE  \E j \in ordered' : j.round = lease'[w].intent
      BY DEF LeaseHasIntent
    <3>1. lease[v] \in LeaseRec
      BY <1>0 DEF TypeOK
    <3>2. lease'[w].live = lease[w].live /\ lease'[w].intent = lease[w].intent
      BY <1>0, <2>1, <3>1 DEF TypeOK, LeaseRec
    <3>3. PICK h \in ordered : h.round = lease[w].intent
      BY <1>0, <3>2 DEF LeaseHasIntent
    <3> QED
      BY <2>1, <3>2, <3>3
  <2>4. EveryEffectHasAnIntent'
    <3> SUFFICES ASSUME NEW y \in effects'
                 PROVE  \E j \in ordered' : j.round = y.intent
      BY DEF EveryEffectHasAnIntent
    <3>1. CASE y \in effects
      <4>1. PICK h \in ordered : h.round = y.intent
        BY <1>0, <3>1 DEF EveryEffectHasAnIntent
      <4> QED
        BY <2>1, <4>1
    <3>2. CASE y \notin effects
      <4>1. y.intent = lease[v].intent
        BY <2>1, <3>2
      <4>2. PICK h \in ordered : h.round = lease[v].intent
        BY <1>0, <2>1 DEF LeaseHasIntent
      <4> QED
        BY <2>1, <4>1, <4>2
    <3> QED
      BY <3>1, <3>2
  <2> QED
    BY <1>0, <2>2, <2>3, <2>4 DEF InvI
<1>7. ASSUME NEW v \in Vehicles, RefuseGrant(v) \/ RefuseEffect(v) PROVE InvI'
  BY <1>7, <1>a, QuietVehicle
<1>8. ASSUME NEW v \in Vehicles, EndLease(v) PROVE InvI'
  <2>1. /\ lease' = [lease EXCEPT ![v].live = FALSE]
        /\ UNCHANGED <<round, intent, ordered, effects>>
    BY <1>8 DEF EndLease
  <2>2. LiveOrdered' /\ EveryEffectHasAnIntent'
    BY <1>0, <2>1 DEF LiveOrdered, EveryEffectHasAnIntent
  <2>3. LeaseHasIntent'
    <3> SUFFICES ASSUME NEW w \in Vehicles, lease'[w].live
                 PROVE  \E j \in ordered' : j.round = lease'[w].intent
      BY DEF LeaseHasIntent
    <3>1. lease[v] \in LeaseRec
      BY <1>0 DEF TypeOK
    <3>2. w # v
      BY <1>0, <2>1, <3>1 DEF TypeOK, LeaseRec
    <3>3. lease'[w] = lease[w]
      BY <1>0, <2>1, <3>2 DEF TypeOK
    <3>4. PICK h \in ordered : h.round = lease[w].intent
      BY <1>0, <3>3 DEF LeaseHasIntent
    <3> QED
      BY <2>1, <3>3, <3>4
  <2> QED
    BY <1>0, <2>2, <2>3 DEF InvI
<1>9. ASSUME NEW k \in LogKinds, AutoOrder(k) \/ AutoRefuse(k) PROVE InvI'
  BY <1>9, <1>a, QuietLog
<1> QED
  BY <1>1, <1>2, <1>3, <1>4, <1>5, <1>6, <1>7, <1>8, <1>9 DEF Next

THEOREM EveryEffectHasAnIntentAlways ==
  ASSUME Mut # "M_NOINTENT"
  PROVE  Spec => []EveryEffectHasAnIntent
<1>1. InvI /\ [Next]_vars => InvI'
  BY NextInvI
<1>2. InvI => EveryEffectHasAnIntent
  BY DEF InvI
<1> QED
  BY InitInvI, <1>1, <1>2, PTL DEF Spec
-----------------------------------------------------------------------------
(* EveryEffectHasALease.                                                       *)

LEMMA InitInvL == Init => InvL
  BY InitTypeOK, NoLeaseFacts
     DEF Init, InvL, LeaseGranted, UsedLe, EveryEffectHasALease, NoLease

LEMMA NextInvL ==
  ASSUME Mut # "M_NOCOUNT", InvL, [Next]_vars
  PROVE  InvL'
<1>0. TypeOK /\ TypeOK' /\ LeaseGranted /\ UsedLe /\ EveryEffectHasALease
  BY NextTypeOK DEF InvL
<1>a. ASSUME UNCHANGED <<lease, granted, effects>> PROVE InvL'
  BY <1>0, <1>a DEF InvL, LeaseGranted, UsedLe, EveryEffectHasALease
<1>1. CASE UNCHANGED vars
  BY <1>1, <1>a DEF vars
<1>2. ASSUME NEW o \in IntentSpace, Order(o) PROVE InvL'
  <2>1. UNCHANGED <<lease, granted, effects>>
    BY <1>2 DEF Order
  <2> QED
    BY <2>1, <1>a
<1>3. ASSUME NEW o \in IntentSpace, RefuseOrder(o) PROVE InvL'
  BY <1>3, <1>a, QuietOrder
<1>4. CASE EndIntent
  <2>1. UNCHANGED <<lease, granted, effects>>
    BY <1>4 DEF EndIntent
  <2> QED
    BY <2>1, <1>a
<1>5. ASSUME NEW v \in Vehicles, NEW c \in 1..MaxCount, Grant(v, c) PROVE InvL'
  <2> DEFINE r == [v |-> v, gen |-> lease[v].gen + 1, count |-> c, intent |-> LiveRound]
  <2>1. /\ lease' = [lease EXCEPT ![v] = [live |-> TRUE, gen |-> lease[v].gen + 1, count |-> c,
                                          used |-> 0, intent |-> LiveRound]]
        /\ granted' = granted \cup {r}
        /\ UNCHANGED effects
    BY <1>5 DEF Grant
  <2>2. c \in Nat
    BY CountFacts
  <2>3. LeaseGranted'
    <3> SUFFICES ASSUME NEW w \in Vehicles, lease'[w].live
                 PROVE  \E h \in granted' : h.v = w /\ h.gen = lease'[w].gen /\ h.count = lease'[w].count
      BY DEF LeaseGranted
    <3>1. CASE w = v
      <4>1. r \in granted'
        BY <2>1
      <4>2. r.v = w /\ r.gen = lease'[w].gen /\ r.count = lease'[w].count
        BY <1>0, <2>1, <3>1 DEF TypeOK
      <4> QED
        BY <4>1, <4>2
    <3>2. CASE w # v
      <4>1. lease'[w] = lease[w]
        BY <1>0, <2>1, <3>2 DEF TypeOK
      <4>2. PICK h \in granted : h.v = w /\ h.gen = lease[w].gen /\ h.count = lease[w].count
        BY <1>0, <4>1 DEF LeaseGranted
      <4>3. h \in granted'
        BY <2>1
      <4> QED
        BY <4>1, <4>2, <4>3
    <3> QED
      BY <3>1, <3>2
  <2>4. UsedLe'
    <3> SUFFICES ASSUME NEW w \in Vehicles PROVE lease'[w].used <= lease'[w].count
      BY DEF UsedLe
    <3>1. CASE w = v
      <4>1. lease'[w].used = 0 /\ lease'[w].count = c
        BY <1>0, <2>1, <3>1 DEF TypeOK
      <4> QED
        BY <2>2, <4>1
    <3>2. CASE w # v
      <4>1. lease'[w] = lease[w]
        BY <1>0, <2>1, <3>2 DEF TypeOK
      <4> QED
        BY <1>0, <4>1 DEF UsedLe
    <3> QED
      BY <3>1, <3>2
  <2>5. EveryEffectHasALease'
    <3> SUFFICES ASSUME NEW y \in effects'
                 PROVE  \E h \in granted' : h.v = y.v /\ h.gen = y.gen /\ y.n <= h.count
      BY DEF EveryEffectHasALease
    <3>1. PICK h \in granted : h.v = y.v /\ h.gen = y.gen /\ y.n <= h.count
      BY <1>0, <2>1 DEF EveryEffectHasALease
    <3>2. h \in granted'
      BY <2>1
    <3> QED
      BY <3>1, <3>2
  <2> QED
    BY <1>0, <2>3, <2>4, <2>5 DEF InvL
<1>6. ASSUME NEW v \in Vehicles, Effect(v) PROVE InvL'
  <2>1. /\ lease[v].live
        /\ lease[v].used < lease[v].count
        /\ effects' = effects \cup {[v |-> v, gen |-> lease[v].gen, n |-> lease[v].used + 1,
                                     intent |-> lease[v].intent]}
        /\ lease' = [lease EXCEPT ![v].used = lease[v].used + 1]
        /\ UNCHANGED granted
    BY <1>6 DEF Effect, Counted
  <2>2. /\ lease[v] \in LeaseRec
        /\ lease[v].used \in Nat /\ lease[v].count \in Nat
    BY <1>0 DEF TypeOK, LeaseRec
  <2>3. /\ lease'[v].used = lease[v].used + 1
        /\ lease'[v].live = lease[v].live
        /\ lease'[v].gen = lease[v].gen
        /\ lease'[v].count = lease[v].count
    BY <1>0, <2>1, <2>2 DEF TypeOK, LeaseRec
  <2>4. \A w \in Vehicles : w # v => lease'[w] = lease[w]
    BY <1>0, <2>1 DEF TypeOK
  <2>5. LeaseGranted'
    <3> SUFFICES ASSUME NEW w \in Vehicles, lease'[w].live
                 PROVE  \E h \in granted' : h.v = w /\ h.gen = lease'[w].gen /\ h.count = lease'[w].count
      BY DEF LeaseGranted
    <3>1. CASE w = v
      <4>1. PICK h \in granted : h.v = w /\ h.gen = lease[w].gen /\ h.count = lease[w].count
        BY <1>0, <2>3, <3>1 DEF LeaseGranted
      <4> QED
        BY <2>1, <2>3, <3>1, <4>1
    <3>2. CASE w # v
      <4>1. PICK h \in granted : h.v = w /\ h.gen = lease[w].gen /\ h.count = lease[w].count
        BY <1>0, <2>4, <3>2 DEF LeaseGranted
      <4> QED
        BY <2>1, <2>4, <3>2, <4>1
    <3> QED
      BY <3>1, <3>2
  <2>6. UsedLe'
    <3> SUFFICES ASSUME NEW w \in Vehicles PROVE lease'[w].used <= lease'[w].count
      BY DEF UsedLe
    <3>1. CASE w = v
      BY <2>1, <2>2, <2>3, <3>1
    <3>2. CASE w # v
      BY <1>0, <2>4, <3>2 DEF UsedLe
    <3> QED
      BY <3>1, <3>2
  <2>7. EveryEffectHasALease'
    <3> SUFFICES ASSUME NEW y \in effects'
                 PROVE  \E h \in granted' : h.v = y.v /\ h.gen = y.gen /\ y.n <= h.count
      BY DEF EveryEffectHasALease
    <3>1. CASE y \in effects
      <4>1. PICK h \in granted : h.v = y.v /\ h.gen = y.gen /\ y.n <= h.count
        BY <1>0, <3>1 DEF EveryEffectHasALease
      <4> QED
        BY <2>1, <4>1
    <3>2. CASE y \notin effects
      <4>1. y.v = v /\ y.gen = lease[v].gen /\ y.n = lease[v].used + 1
        BY <2>1, <3>2
      <4>2. PICK h \in granted : h.v = v /\ h.gen = lease[v].gen /\ h.count = lease[v].count
        BY <1>0, <2>1 DEF LeaseGranted
      <4>3. y.n <= h.count
        BY <2>1, <2>2, <4>1, <4>2
      <4> QED
        BY <2>1, <4>1, <4>2, <4>3
    <3> QED
      BY <3>1, <3>2
  <2> QED
    BY <1>0, <2>5, <2>6, <2>7 DEF InvL
<1>7. ASSUME NEW v \in Vehicles, RefuseGrant(v) \/ RefuseEffect(v) PROVE InvL'
  BY <1>7, <1>a, QuietVehicle
<1>8. ASSUME NEW v \in Vehicles, EndLease(v) PROVE InvL'
  <2>1. /\ lease' = [lease EXCEPT ![v].live = FALSE]
        /\ UNCHANGED <<granted, effects>>
    BY <1>8 DEF EndLease
  <2>2. lease[v] \in LeaseRec
    BY <1>0 DEF TypeOK
  <2>3. /\ ~lease'[v].live
        /\ lease'[v].used = lease[v].used
        /\ lease'[v].count = lease[v].count
    BY <1>0, <2>1, <2>2 DEF TypeOK, LeaseRec
  <2>4. \A w \in Vehicles : w # v => lease'[w] = lease[w]
    BY <1>0, <2>1 DEF TypeOK
  <2>5. LeaseGranted'
    <3> SUFFICES ASSUME NEW w \in Vehicles, lease'[w].live
                 PROVE  \E h \in granted' : h.v = w /\ h.gen = lease'[w].gen /\ h.count = lease'[w].count
      BY DEF LeaseGranted
    <3>1. w # v
      BY <2>3
    <3>2. PICK h \in granted : h.v = w /\ h.gen = lease[w].gen /\ h.count = lease[w].count
      BY <1>0, <2>4, <3>1 DEF LeaseGranted
    <3> QED
      BY <2>1, <2>4, <3>1, <3>2
  <2>6. UsedLe'
    <3> SUFFICES ASSUME NEW w \in Vehicles PROVE lease'[w].used <= lease'[w].count
      BY DEF UsedLe
    <3>1. CASE w = v
      BY <1>0, <2>3, <3>1 DEF UsedLe
    <3>2. CASE w # v
      BY <1>0, <2>4, <3>2 DEF UsedLe
    <3> QED
      BY <3>1, <3>2
  <2>7. EveryEffectHasALease'
    BY <1>0, <2>1 DEF EveryEffectHasALease
  <2> QED
    BY <1>0, <2>5, <2>6, <2>7 DEF InvL
<1>9. ASSUME NEW k \in LogKinds, AutoOrder(k) \/ AutoRefuse(k) PROVE InvL'
  BY <1>9, <1>a, QuietLog
<1> QED
  BY <1>1, <1>2, <1>3, <1>4, <1>5, <1>6, <1>7, <1>8, <1>9 DEF Next

THEOREM EveryEffectHasALeaseAlways ==
  ASSUME Mut # "M_NOCOUNT"
  PROVE  Spec => []EveryEffectHasALease
<1>1. InvL /\ [Next]_vars => InvL'
  BY NextInvL
<1>2. InvL => EveryEffectHasALease
  BY DEF InvL
<1> QED
  BY InitInvL, <1>1, <1>2, PTL DEF Spec
-----------------------------------------------------------------------------
(* IntentNarrows.                                                              *)

LEMMA InitInvN == Init => InvN
  BY InitTypeOK DEF Init, InvN, IntentInSeating, IntentNarrows

LEMMA NextInvN ==
  ASSUME Mut # "M_WIDEINTENT", InvN, [Next]_vars
  PROVE  InvN'
<1>0. TypeOK /\ TypeOK' /\ IntentInSeating /\ IntentNarrows
  BY NextTypeOK DEF InvN
<1>a. ASSUME UNCHANGED <<round, intent, ordered>> PROVE InvN'
  BY <1>0, <1>a DEF InvN, IntentInSeating, IntentNarrows
<1>1. CASE UNCHANGED vars
  BY <1>1, <1>a DEF vars
<1>2. ASSUME NEW o \in IntentSpace, Order(o) PROVE InvN'
  <2> DEFINE r == [round |-> round + 1, envelope |-> o.envelope, budget |-> o.budget]
  <2>1. /\ round' = round + 1
        /\ intent'.envelope = o.envelope
        /\ ordered' = ordered \cup {r}
        /\ EnvelopeOK(o)
        /\ o.budget <= SeatingBudget
    BY <1>2 DEF Order, Bounded
  <2>2. o.envelope \subseteq SeatingEnvelope
    <3>1. CASE round >= 1 /\ Mut = "M_LASTINTENT"
      <4>1. o.envelope \subseteq intent.envelope
        BY <2>1, <3>1 DEF EnvelopeOK
      <4>2. intent.envelope \subseteq SeatingEnvelope
        BY <1>0, <3>1 DEF IntentInSeating
      <4> QED
        BY <4>1, <4>2
    <3>2. CASE ~(round >= 1 /\ Mut = "M_LASTINTENT")
      BY <2>1, <3>2 DEF EnvelopeOK
    <3> QED
      BY <3>1, <3>2
  <2>3. IntentInSeating'
    BY <2>1, <2>2 DEF IntentInSeating
  <2>4. IntentNarrows'
    <3> SUFFICES ASSUME NEW y \in ordered'
                 PROVE  y.envelope \subseteq SeatingEnvelope /\ y.budget <= SeatingBudget
      BY DEF IntentNarrows
    <3>1. CASE y \in ordered
      BY <1>0, <3>1 DEF IntentNarrows
    <3>2. CASE y = r
      BY <2>1, <2>2, <3>2
    <3> QED
      BY <2>1, <3>1, <3>2
  <2> QED
    BY <1>0, <2>3, <2>4 DEF InvN
<1>3. ASSUME NEW o \in IntentSpace, RefuseOrder(o) PROVE InvN'
  BY <1>3, <1>a, QuietOrder
<1>4. CASE EndIntent
  <2>1. /\ intent' = [intent EXCEPT !.live = FALSE]
        /\ UNCHANGED <<round, ordered>>
    BY <1>4 DEF EndIntent
  <2>2. intent'.envelope = intent.envelope
    BY <1>0, <2>1 DEF TypeOK, IntentRec
  <2>3. IntentInSeating' /\ IntentNarrows'
    BY <1>0, <2>1, <2>2 DEF IntentInSeating, IntentNarrows
  <2> QED
    BY <1>0, <2>3 DEF InvN
<1>5. ASSUME NEW v \in Vehicles, NEW c \in 1..MaxCount, Grant(v, c) PROVE InvN'
  <2>1. UNCHANGED <<round, intent, ordered>>
    BY <1>5 DEF Grant
  <2> QED
    BY <2>1, <1>a
<1>6. ASSUME NEW v \in Vehicles, Effect(v) \/ EndLease(v) PROVE InvN'
  <2>1. UNCHANGED <<round, intent, ordered>>
    BY <1>6 DEF Effect, EndLease
  <2> QED
    BY <2>1, <1>a
<1>7. ASSUME NEW v \in Vehicles, RefuseGrant(v) \/ RefuseEffect(v) PROVE InvN'
  BY <1>7, <1>a, QuietVehicle
<1>9. ASSUME NEW k \in LogKinds, AutoOrder(k) \/ AutoRefuse(k) PROVE InvN'
  BY <1>9, <1>a, QuietLog
<1> QED
  BY <1>1, <1>2, <1>3, <1>4, <1>5, <1>6, <1>7, <1>9 DEF Next

THEOREM IntentNarrowsAlways ==
  ASSUME Mut # "M_WIDEINTENT"
  PROVE  Spec => []IntentNarrows
<1>1. InvN /\ [Next]_vars => InvN'
  BY NextInvN
<1>2. InvN => IntentNarrows
  BY DEF InvN
<1> QED
  BY InitInvN, <1>1, <1>2, PTL DEF Spec
-----------------------------------------------------------------------------
(* AutonomousAddsNothing: inductive alone.                                     *)

LEMMA NextAutonomous ==
  ASSUME Mut # "M_LITEPROMOTES", AutonomousAddsNothing, [Next]_vars
  PROVE  AutonomousAddsNothing'
<1>1. CASE UNCHANGED vars
  BY <1>1 DEF vars, AutonomousAddsNothing
<1>2. ASSUME NEW o \in IntentSpace, Order(o) \/ RefuseOrder(o) PROVE AutonomousAddsNothing'
  BY <1>2 DEF Order, RefuseOrder, AutonomousAddsNothing
<1>3. CASE EndIntent
  BY <1>3 DEF EndIntent, AutonomousAddsNothing
<1>4. ASSUME NEW v \in Vehicles, NEW c \in 1..MaxCount, Grant(v, c) PROVE AutonomousAddsNothing'
  <2>1. log' = log \cup {"lease"}
    BY <1>4 DEF Grant
  <2>2. "lease" \notin AuthorityKinds
    BY DEF AuthorityKinds
  <2> QED
    BY <2>1, <2>2 DEF AutonomousAddsNothing
<1>5. ASSUME NEW v \in Vehicles, RefuseGrant(v) \/ Effect(v) \/ RefuseEffect(v) \/ EndLease(v)
      PROVE AutonomousAddsNothing'
  BY <1>5 DEF RefuseGrant, Effect, RefuseEffect, EndLease, AutonomousAddsNothing
<1>6. ASSUME NEW k \in LogKinds, AutoOrder(k) PROVE AutonomousAddsNothing'
  <2>1. k \in AllowedKinds /\ log' = log \cup {k}
    BY <1>6 DEF AutoOrder, Admissible
  <2>2. k \notin AuthorityKinds
    BY <2>1 DEF AllowedKinds, AuthorityKinds
  <2> QED
    BY <2>1, <2>2 DEF AutonomousAddsNothing
<1>7. ASSUME NEW k \in LogKinds, AutoRefuse(k) PROVE AutonomousAddsNothing'
  BY <1>7 DEF AutoRefuse, AutonomousAddsNothing
<1> QED
  BY <1>1, <1>2, <1>3, <1>4, <1>5, <1>6, <1>7 DEF Next

THEOREM AutonomousAddsNothingAlways ==
  ASSUME Mut # "M_LITEPROMOTES"
  PROVE  Spec => []AutonomousAddsNothing
<1>1. AutonomousAddsNothing /\ [Next]_vars => AutonomousAddsNothing'
  BY NextAutonomous
<1>2. Init => AutonomousAddsNothing
  BY DEF Init, AutonomousAddsNothing
<1> QED
  BY <1>1, <1>2, PTL DEF Spec
-----------------------------------------------------------------------------
THEOREM SafeAlways ==
  ASSUME Mut = "none"
  PROVE  Spec => []Safe
<1>1. Spec => []EveryEffectHasAnIntent
  BY EveryEffectHasAnIntentAlways
<1>2. Spec => []EveryEffectHasALease
  BY EveryEffectHasALeaseAlways
<1>3. Spec => []IntentNarrows
  BY IntentNarrowsAlways
<1>4. Spec => []AutonomousAddsNothing
  BY AutonomousAddsNothingAlways
<1> QED
  BY <1>1, <1>2, <1>3, <1>4, PTL DEF Safe
-----------------------------------------------------------------------------
(* Why the mutations must fail. The counterexamples are TLC's.                 *)

LEMMA MutNoIntentGrantsAnyway ==
  ASSUME Mut = "M_NOINTENT"
  PROVE  LiveOK
  BY DEF LiveOK

LEMMA MutNoCountCountsNothing ==
  ASSUME Mut = "M_NOCOUNT", NEW v
  PROVE  Counted(v)
  BY DEF Counted

LEMMA MutWideIntentAdmitsAny ==
  ASSUME Mut = "M_WIDEINTENT", NEW o, round >= 1
  PROVE  EnvelopeOK(o)
  BY DEF EnvelopeOK

LEMMA MutLastIntentReadsTheLast ==
  ASSUME Mut = "M_LASTINTENT", NEW o, round >= 1, o.envelope \subseteq intent.envelope
  PROVE  EnvelopeOK(o)
  BY DEF EnvelopeOK

LEMMA MutLitePromotesAdmitsPromotion ==
  ASSUME Mut = "M_LITEPROMOTES"
  PROVE  Admissible("promotion")
  BY DEF Admissible
=============================================================================
