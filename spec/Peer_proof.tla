-------------------------------- MODULE Peer_proof --------------------------------
(* TLAPS proof of the invariants of Peer.tla (ADR-0065 §9), for every value of *)
(* the constants: no assumption is made on MaxDeliver or MaxSend. Peer.tla is  *)
(* not edited.                                                                 *)
(*                                                                             *)
(*   THEOREM PeerAddsNothingAlways     [Mut # "M_PEERENABLES"]                 *)
(*   THEOREM NarrowsInReceivedAlways   [Mut # "M_PEERENABLES"]                 *)
(*   THEOREM ReceivedIsUntrustedAlways [Mut # "M_SENDERLABEL"]                 *)
(*   THEOREM SendWithinTopicsAlways    [Mut # "M_ANYTOPIC"]                    *)
(*   THEOREM SafeAlways                [Mut = "none"]                          *)
(*                                                                             *)
(* No strengthening is needed. PeerAddsNothing and NarrowsInReceived are true  *)
(* of every state under their hypothesis, reachable or not: each cause of a    *)
(* refusal is an existential over the items, so it can only be lost by         *)
(* removing some, and with M_PEERENABLES absent nothing else reads them. They  *)
(* are state lemmas lifted by PTL. ReceivedIsUntrusted is an append-only set   *)
(* whose one report-appending action is the receiver's labelling, and          *)
(* SendWithinTopics is a flag at the one action that can set it.               *)
(*                                                                             *)
(* These theorems are about `received` as the module defines it, what a peer   *)
(* originates and what subtracts. The module's header records why a relayed    *)
(* certified lease is not in it.                                               *)
(*                                                                             *)
(* Mutations and witnesses are behaviours and stay with TLC                    *)
(* (Peer-results-*.txt). Check: tools/tlapm --cleanfp --strict.                *)
EXTENDS Peer, TLAPS

Tags == {"permit", "handlePermit", "relayedLease", "narrowedClear", "measuredStop",
         "fenceStop", "dropped", "refSendDecl", "refSendBundle", "sent", "labelLow"}

TypeOK ==
  /\ live \in BOOLEAN
  /\ viaPeer \in BOOLEAN
  /\ fenceOrdered \in BOOLEAN
  /\ received \subseteq Item
  /\ deliveries \in Nat
  /\ sends \in Nat
  /\ offTopicSent \in BOOLEAN
  /\ seen \subseteq Tags
-----------------------------------------------------------------------------
LEMMA InitTypeOK == Init => TypeOK
  BY DEF Init, TypeOK

LEMMA FenceItemType == FenceItem \in Item
  BY DEF FenceItem, Item, Topics, Labels

LEMMA MeasuredItemType ==
  ASSUME NEW val \in {"near", "far"}
  PROVE  MeasuredItem(val) \in Item
  BY DEF MeasuredItem, Item, Topics, Labels

LEMMA DeliveredLabelsType ==
  ASSUME NEW t \in Heard, NEW L \in SUBSET Labels
  PROVE  DeliveredLabels(t, L) \subseteq Labels
  BY DEF DeliveredLabels, Heard, Labels, Name

LEMMA HeardTopics == Heard \subseteq Topics
  BY DEF Heard, Topics

LEMMA NextTypeOK == TypeOK /\ [Next]_vars => TypeOK'
<1> SUFFICES ASSUME TypeOK, [Next]_vars PROVE TypeOK' OBVIOUS
<1>1. CASE UNCHANGED vars
  BY <1>1 DEF TypeOK, vars
<1>2. ASSUME NEW via \in BOOLEAN, Grant(via) PROVE TypeOK'
  BY <1>2 DEF Grant, TypeOK
<1>3. CASE OrderFence
  BY <1>3 DEF OrderFence, TypeOK
<1>4. CASE RelayFence
  BY <1>4, FenceItemType DEF RelayFence, TypeOK
<1>5. ASSUME NEW val \in {"near", "far"}, ReceiveMeasured(val) PROVE TypeOK'
  BY <1>5, MeasuredItemType DEF ReceiveMeasured, TypeOK
<1>6. ASSUME NEW t \in Heard, NEW L \in SUBSET Labels, Deliver(t, L) PROVE TypeOK'
  <2> DEFINE new == [kind |-> "report", topic |-> t, labels |-> DeliveredLabels(t, L),
                     clear |-> t \in ClearTopics, value |-> "none"]
  <2>1. DeliveredLabels(t, L) \subseteq Labels /\ t \in Topics
    BY DeliveredLabelsType, HeardTopics
  <2>2. new \in Item
    BY <2>1 DEF Item
  <2>3. received' = received \cup {new}
    BY <1>6 DEF Deliver
  <2>4. received' \subseteq Item
    BY <2>2, <2>3 DEF TypeOK
  <2>5. seen' \subseteq Tags
    BY <1>6 DEF Deliver, TypeOK, Tags
  <2>6. deliveries' \in Nat /\ UNCHANGED <<live, viaPeer, fenceOrdered, sends, offTopicSent>>
    BY <1>6 DEF Deliver, TypeOK
  <2> QED
    BY <2>4, <2>5, <2>6 DEF TypeOK
<1>7. ASSUME NEW t \in Topics \ Heard, Drop(t) PROVE TypeOK'
  BY <1>7 DEF Drop, TypeOK, Tags
<1>8. ASSUME NEW t \in Topics, Send(t) PROVE TypeOK'
  BY <1>8 DEF Send, TypeOK, Tags
<1>9. ASSUME NEW t \in Topics, RefuseSend(t) PROVE TypeOK'
  <2> DEFINE S == (IF TopicOK(t) THEN {} ELSE {"refSendDecl"})
                  \cup (IF BundleOK(t) THEN {} ELSE {"refSendBundle"})
  <2> HIDE DEF TopicOK, BundleOK
  <2>1. S \subseteq Tags
    BY DEF Tags
  <2>2. seen' = seen \cup S
    BY <1>9 DEF RefuseSend
  <2>3. UNCHANGED <<live, viaPeer, fenceOrdered, received, deliveries, sends, offTopicSent>>
    BY <1>9 DEF RefuseSend
  <2> QED
    BY <2>1, <2>2, <2>3 DEF TypeOK
<1>10. ASSUME NEW e \in Entries, Permit(e) PROVE TypeOK'
  <2> DEFINE S == {"permit"}
                  \cup (IF e = "egress" /\ \E y \in received : y.kind = "report" /\ ~y.clear /\ "untrusted" \in y.labels
                        THEN {"handlePermit"} ELSE {})
                  \cup (IF viaPeer THEN {"relayedLease"} ELSE {})
  <2>1. S \subseteq Tags
    BY DEF Tags
  <2>2. seen' = seen \cup S
    BY <1>10 DEF Permit
  <2>3. UNCHANGED <<live, viaPeer, fenceOrdered, received, deliveries, sends, offTopicSent>>
    BY <1>10 DEF Permit
  <2> QED
    BY <2>1, <2>2, <2>3 DEF TypeOK
<1>11. ASSUME NEW e \in Entries, Refuse(e) PROVE TypeOK'
  <2> DEFINE S == (IF Decide(e, {}) /\ LabelStop(e, received) THEN {"narrowedClear"} ELSE {})
                  \cup (IF MeasuredStop(e, received) THEN {"measuredStop"} ELSE {})
                  \cup (IF CertifiedStop(received) THEN {"fenceStop"} ELSE {})
  <2> HIDE DEF Decide, LabelStop, MeasuredStop, CertifiedStop
  <2>1. S \subseteq Tags
    BY DEF Tags
  <2>2. seen' = seen \cup S
    BY <1>11 DEF Refuse
  <2>3. UNCHANGED <<live, viaPeer, fenceOrdered, received, deliveries, sends, offTopicSent>>
    BY <1>11 DEF Refuse
  <2> QED
    BY <2>1, <2>2, <2>3 DEF TypeOK
<1> QED
  BY <1>1, <1>2, <1>3, <1>4, <1>5, <1>6, <1>7, <1>8, <1>9, <1>10, <1>11 DEF Next

THEOREM TypeAlways == Spec => []TypeOK
<1>1. TypeOK /\ [Next]_vars => TypeOK'
  BY NextTypeOK
<1> QED
  BY InitTypeOK, <1>1, PTL DEF Spec
-----------------------------------------------------------------------------
(* Receipt only narrows. A cause of refusal is an existential over the items.  *)

LEMMA StopsMonotone ==
  ASSUME NEW e, NEW S, NEW T, T \subseteq S, Stops(e, T)
  PROVE  Stops(e, S)
  BY DEF Stops, CertifiedStop, MeasuredStop, LabelStop

LEMMA NoStopsOnEmpty ==
  ASSUME NEW e
  PROVE  ~Stops(e, {})
  BY DEF Stops, CertifiedStop, MeasuredStop, LabelStop

LEMMA EnabledIsAlphabet ==
  ASSUME Mut # "M_PEERENABLES", NEW e, NEW S
  PROVE  Decide(e, S) <=> (live /\ e \in Alphabet /\ ~Stops(e, S))
  BY DEF Decide, PeerEnables

LEMMA NarrowsValid ==
  ASSUME Mut # "M_PEERENABLES"
  PROVE  NarrowsInReceived
<1> SUFFICES ASSUME NEW e \in Entries, NEW T \in SUBSET received, Decide(e, received)
             PROVE  Decide(e, T)
  BY DEF NarrowsInReceived
<1>1. live /\ e \in Alphabet /\ ~Stops(e, received)
  BY EnabledIsAlphabet
<1>2. ~Stops(e, T)
  BY <1>1, StopsMonotone
<1> QED
  BY <1>1, <1>2, EnabledIsAlphabet

LEMMA AddsNothingValid ==
  ASSUME Mut # "M_PEERENABLES"
  PROVE  PeerAddsNothing
<1> SUFFICES ASSUME NEW e \in Entries, Decide(e, received)
             PROVE  Decide(e, {})
  BY DEF PeerAddsNothing
<1>1. live /\ e \in Alphabet
  BY EnabledIsAlphabet
<1>2. ~Stops(e, {})
  BY NoStopsOnEmpty
<1> QED
  BY <1>1, <1>2, EnabledIsAlphabet

THEOREM PeerAddsNothingAlways ==
  ASSUME Mut # "M_PEERENABLES"
  PROVE  Spec => []PeerAddsNothing
<1>1. PeerAddsNothing
  BY AddsNothingValid
<1> QED
  BY <1>1, PTL

THEOREM NarrowsInReceivedAlways ==
  ASSUME Mut # "M_PEERENABLES"
  PROVE  Spec => []NarrowsInReceived
<1>1. NarrowsInReceived
  BY NarrowsValid
<1> QED
  BY <1>1, PTL
-----------------------------------------------------------------------------
(* The receiver labels every report it delivers.                               *)

LEMMA NextReceivedIsUntrusted ==
  ASSUME Mut # "M_SENDERLABEL", ReceivedIsUntrusted, [Next]_vars
  PROVE  ReceivedIsUntrusted'
<1> DEFINE Good(y) == y.kind = "report" => ("untrusted" \in y.labels /\ Name[y.topic] \in y.labels)
<1> USE DEF ReceivedIsUntrusted
<1>0. \A y \in received : Good(y)
  OBVIOUS
<1>1. CASE UNCHANGED received
  BY <1>0, <1>1
<1>2. CASE RelayFence
  <2>1. received' = received \cup {FenceItem}
    BY <1>2 DEF RelayFence
  <2>2. Good(FenceItem)
    BY DEF FenceItem
  <2> QED
    BY <1>0, <2>1, <2>2
<1>3. ASSUME NEW val \in {"near", "far"}, ReceiveMeasured(val) PROVE ReceivedIsUntrusted'
  <2>1. received' = received \cup {MeasuredItem(val)}
    BY <1>3 DEF ReceiveMeasured
  <2>2. Good(MeasuredItem(val))
    BY DEF MeasuredItem
  <2> QED
    BY <1>0, <2>1, <2>2
<1>4. ASSUME NEW t \in Heard, NEW L \in SUBSET Labels, Deliver(t, L) PROVE ReceivedIsUntrusted'
  <2> DEFINE new == [kind |-> "report", topic |-> t, labels |-> DeliveredLabels(t, L),
                     clear |-> t \in ClearTopics, value |-> "none"]
  <2>1. received' = received \cup {new}
    BY <1>4 DEF Deliver
  <2>2. DeliveredLabels(t, L) = L \cup {"untrusted", Name[t]}
    BY DEF DeliveredLabels
  <2>3. Good(new)
    BY <2>2
  <2> QED
    BY <1>0, <2>1, <2>3
<1>5. QED
  <2>1. CASE Next
    <3>1. CASE \E via \in BOOLEAN : Grant(via)
      <4>1. UNCHANGED received
        BY <3>1 DEF Grant
      <4> QED
        BY <4>1, <1>1
    <3>2. CASE OrderFence
      <4>1. UNCHANGED received
        BY <3>2 DEF OrderFence
      <4> QED
        BY <4>1, <1>1
    <3>3. CASE RelayFence
      BY <3>3, <1>2
    <3>4. CASE \E val \in {"near", "far"} : ReceiveMeasured(val)
      BY <3>4, <1>3
    <3>5. CASE \E t \in Heard, L \in SUBSET Labels : Deliver(t, L)
      BY <3>5, <1>4
    <3>6. CASE \E t \in Topics \ Heard : Drop(t)
      <4>1. UNCHANGED received
        BY <3>6 DEF Drop
      <4> QED
        BY <4>1, <1>1
    <3>7. CASE \E t \in Topics : Send(t) \/ RefuseSend(t)
      <4>1. UNCHANGED received
        BY <3>7 DEF Send, RefuseSend
      <4> QED
        BY <4>1, <1>1
    <3>8. CASE \E e \in Entries : Permit(e) \/ Refuse(e)
      <4>1. UNCHANGED received
        BY <3>8 DEF Permit, Refuse
      <4> QED
        BY <4>1, <1>1
    <3> QED
      BY <2>1, <3>1, <3>2, <3>3, <3>4, <3>5, <3>6, <3>7, <3>8 DEF Next
  <2>2. CASE UNCHANGED vars
    <3>1. UNCHANGED received
      BY <2>2 DEF vars
    <3> QED
      BY <3>1, <1>1
  <2> QED
    BY <2>1, <2>2

THEOREM ReceivedIsUntrustedAlways ==
  ASSUME Mut # "M_SENDERLABEL"
  PROVE  Spec => []ReceivedIsUntrusted
<1>1. ReceivedIsUntrusted /\ [Next]_vars => ReceivedIsUntrusted'
  BY NextReceivedIsUntrusted
<1>2. Init => ReceivedIsUntrusted
  BY DEF Init, ReceivedIsUntrusted
<1> QED
  BY <1>1, <1>2, PTL DEF Spec
-----------------------------------------------------------------------------
(* The flag, at the one action that can set it.                                *)

LEMMA NextSendWithinTopics ==
  ASSUME Mut # "M_ANYTOPIC", SendWithinTopics, [Next]_vars
  PROVE  SendWithinTopics'
<1> USE DEF SendWithinTopics
<1>1. CASE UNCHANGED offTopicSent
  BY <1>1
<1>2. ASSUME NEW t \in Topics, Send(t) PROVE SendWithinTopics'
  <2>1. t \in Declared
    BY <1>2 DEF Send, TopicOK
  <2> QED
    BY <1>2, <2>1 DEF Send
<1>3. QED
  <2>1. CASE Next
    <3>1. CASE \E t \in Topics : Send(t)
      BY <3>1, <1>2
    <3>2. CASE ~\E t \in Topics : Send(t)
      <4>1. UNCHANGED offTopicSent
        BY <2>1, <3>2 DEF Next, Grant, OrderFence, RelayFence, ReceiveMeasured, Deliver, Drop, RefuseSend, Permit, Refuse
      <4> QED
        BY <4>1, <1>1
    <3> QED
      BY <3>1, <3>2
  <2>2. CASE UNCHANGED vars
    <3>1. UNCHANGED offTopicSent
      BY <2>2 DEF vars
    <3> QED
      BY <3>1, <1>1
  <2> QED
    BY <2>1, <2>2

THEOREM SendWithinTopicsAlways ==
  ASSUME Mut # "M_ANYTOPIC"
  PROVE  Spec => []SendWithinTopics
<1>1. SendWithinTopics /\ [Next]_vars => SendWithinTopics'
  BY NextSendWithinTopics
<1>2. Init => SendWithinTopics
  BY DEF Init, SendWithinTopics
<1> QED
  BY <1>1, <1>2, PTL DEF Spec
-----------------------------------------------------------------------------
THEOREM SafeAlways ==
  ASSUME Mut = "none"
  PROVE  Spec => []Safe
<1>1. Spec => []PeerAddsNothing
  BY PeerAddsNothingAlways
<1>2. Spec => []NarrowsInReceived
  BY NarrowsInReceivedAlways
<1>3. Spec => []ReceivedIsUntrusted
  BY ReceivedIsUntrustedAlways
<1>4. Spec => []SendWithinTopics
  BY SendWithinTopicsAlways
<1> QED
  BY <1>1, <1>2, <1>3, <1>4, PTL DEF Safe
-----------------------------------------------------------------------------
(* Why the mutations must fail. The counterexamples are TLC's.                 *)

LEMMA MutPeerEnablesEnablesGated ==
  ASSUME Mut = "M_PEERENABLES", live, NEW S, \E y \in S : y.kind = "report", ~Stops("gated", S)
  PROVE  Decide("gated", S)
  BY DEF Decide, PeerEnables

LEMMA MutSenderLabelTakesTheLabel ==
  ASSUME Mut = "M_SENDERLABEL", NEW t, NEW L
  PROVE  DeliveredLabels(t, L) = L
  BY DEF DeliveredLabels

LEMMA MutAnyTopicAdmitsAny ==
  ASSUME Mut = "M_ANYTOPIC", NEW t
  PROVE  TopicOK(t)
  BY DEF TopicOK
=============================================================================
