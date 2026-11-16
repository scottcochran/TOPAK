---------------------------------- MODULE Peer ----------------------------------
(* Stacks report to each other on topics promoted with the mesh: ADR-0065      *)
(* (Proposed), its ratification condition (§9), and proposal §10 of            *)
(* derived/topak-federated-c2-design-proposal-2026.11.10b.md. A send is        *)
(* permitted and never ordered, receipt is labelled ingress, and nothing a     *)
(* peer originates enables anything.                                           *)
(*                                                                             *)
(* One receiving governor, its lease, and an honest sending governor. The      *)
(* radio belongs to the adversary: any report on any topic, with any labels,   *)
(* can arrive, which is more than honest senders produce and is what a         *)
(* captured sender can do. Three kinds of traffic (§1) arrive as items:        *)
(*   certified  a fence the plane ordered, relayed by a peer that originates   *)
(*              nothing (the certificate is taken as unforgeable, ADR-0059 §5) *)
(*   measured   another governor's measured fact, which may refuse and never   *)
(*              permits, and which a captured governor may lie about           *)
(*   report     a stack's report, delivered as labelled ingress                *)
(* A decision is a state function of the request and of the items received,    *)
(* so the property can compare the decision with and without them.             *)
(*                                                                             *)
(*   PeerAddsNothing     every request permitted is still permitted with       *)
(*                       every item received from peers removed (§1)           *)
(*   NarrowsInReceived   every request permitted is still permitted with any   *)
(*                       subset of those items: receipt only narrows, which    *)
(*                       is the monotonicity ADR-0067 §7 asks the stage to     *)
(*                       show                                                  *)
(*   ReceivedIsUntrusted a delivered report's label holds `untrusted` and its  *)
(*                       topic's name, whatever its sender declared (§3)       *)
(*   SendWithinTopics    every report an honest governor sends is to a topic   *)
(*                       the mesh declares for the seat (§2, §4)               *)
(*                                                                             *)
(* A FINDING, ON §1'S SENTENCE. "The same request with every item received     *)
(* from peers removed is still permitted" is false read literally. §1's table  *)
(* has a peer relay certified facts, and leases are among them: a vehicle      *)
(* whose lease reached it through a peer is permitted because of an item       *)
(* received from a peer, and with that item removed it is not. The heading     *)
(* says what is meant, nothing a peer ORIGINATES. So PeerAddsNothing ranges    *)
(* over what a peer originates and what subtracts, the items in `received`;    *)
(* a certified lease is the plane's act and sets `live`. The witness           *)
(* NeverPermitUnderRelayedLease shows that the literal reading is not a        *)
(* property of the mechanism: a request is permitted under a lease a peer      *)
(* relayed, and it must be VIOLATED.                                           *)
(*                                                                             *)
(* What the labels guarantee. The receiver adds `untrusted` and the topic's    *)
(* name, so those two survive a captured sender. A name the sender added       *)
(* itself does not: §3's "cannot remove any" holds of an honest governor, and  *)
(* a captured one is the case in which it matters.                             *)
(*                                                                             *)
(* What is abstracted. Requests are three entries: `act`, which a bundle       *)
(* refuses after a clear report labelled `n1`, and which a measured `near`     *)
(* refuses; `egress`, which the floor's label forbids refuse after any clear   *)
(* `untrusted` report; and `gated`, in no alphabet, which only M_PEERENABLES   *)
(* can reach. Topic t1 is delivered clear, t2 as a handle, and tx is declared  *)
(* for nobody. t2 is declared but silenced by a bundle for sending. A send's   *)
(* count is `MaxSend`. Sends are recorded by digest on the vehicle's chain     *)
(* (§2), which is not modelled, nor is the lease's end: `live` only rises.     *)
(* Whether a report is read, and what a stack does with it, is not modelled:   *)
(* §5 makes nothing rest on it. The bound on deliveries only cuts the state    *)
(* space. Mesh.tla is not edited and not extended.                             *)
(*                                                                             *)
(* Mut = "none":           ADR-0065 as drafted.                                *)
(* Mut = "M_PEERENABLES":  a report enables one entry, `gated`.                *)
(*                         PeerAddsNothing and NarrowsInReceived must fail.    *)
(* Mut = "M_SENDERLABEL":  the sender's label is taken as given.               *)
(*                         ReceivedIsUntrusted must fail.                      *)
(* Mut = "M_ANYTOPIC":     a governor sends a report to an undeclared topic.   *)
(*                         SendWithinTopics must fail.                         *)
(*                                                                             *)
(* Deadlock is not checked: the bounds end every behaviour, and stopping is    *)
(* safe.                                                                       *)
EXTENDS Naturals

CONSTANTS Mut, MaxDeliver, MaxSend

Entries  == {"act", "egress", "gated"}
Alphabet == {"act", "egress"}
Topics   == {"t1", "t2", "tx"}
Declared == {"t1", "t2"}
Heard    == {"t1", "t2"}
Silenced == {"t2"}
Labels   == {"untrusted", "n1", "n2"}
Name     == [t1 |-> "n1", t2 |-> "n2"]
ClearTopics == {"t1"}

Item == [kind : {"report", "measured", "certified"},
         topic : Topics \cup {"none"},
         labels : SUBSET Labels,
         clear : BOOLEAN,
         value : {"none", "near", "far", "fence"}]

FenceItem == [kind |-> "certified", topic |-> "none", labels |-> {}, clear |-> FALSE, value |-> "fence"]
MeasuredItem(val) == [kind |-> "measured", topic |-> "none", labels |-> {}, clear |-> FALSE, value |-> val]

VARIABLES live, viaPeer, fenceOrdered, received, deliveries, sends, offTopicSent, seen
vars == <<live, viaPeer, fenceOrdered, received, deliveries, sends, offTopicSent, seen>>

Init ==
  /\ live = FALSE
  /\ viaPeer = FALSE
  /\ fenceOrdered = FALSE
  /\ received = {}
  /\ deliveries = 0
  /\ sends = 0
  /\ offTopicSent = FALSE
  /\ seen = {}

\* The receiver's labelling, open to one mutation.
DeliveredLabels(t, L) == IF Mut = "M_SENDERLABEL" THEN L ELSE L \cup {"untrusted", Name[t]}

\* The decision: a state function of a request and of the items received.
CertifiedStop(S) == \E x \in S : x.kind = "certified"
MeasuredStop(e, S) == e = "act" /\ \E x \in S : x.kind = "measured" /\ x.value = "near"
LabelStop(e, S) ==
  \E x \in S :
    /\ x.kind = "report"
    /\ x.clear
    /\ \/ e = "egress" /\ "untrusted" \in x.labels
       \/ e = "act" /\ "n1" \in x.labels
Stops(e, S) == CertifiedStop(S) \/ MeasuredStop(e, S) \/ LabelStop(e, S)

PeerEnables(e, S) == Mut = "M_PEERENABLES" /\ e = "gated" /\ \E x \in S : x.kind = "report"

Decide(e, S) == live /\ (e \in Alphabet \/ PeerEnables(e, S)) /\ ~Stops(e, S)

\* The plane grants the lease; a peer may have relayed it.
Grant(via) ==
  /\ ~live
  /\ live' = TRUE
  /\ viaPeer' = via
  /\ UNCHANGED <<fenceOrdered, received, deliveries, sends, offTopicSent, seen>>

OrderFence ==
  /\ ~fenceOrdered
  /\ fenceOrdered' = TRUE
  /\ UNCHANGED <<live, viaPeer, received, deliveries, sends, offTopicSent, seen>>

\* A peer relays a certified subtraction. A peer cannot originate one.
RelayFence ==
  /\ fenceOrdered
  /\ deliveries < MaxDeliver
  /\ received' = received \cup {FenceItem}
  /\ deliveries' = deliveries + 1
  /\ UNCHANGED <<live, viaPeer, fenceOrdered, sends, offTopicSent, seen>>

\* A peer's governor reports a measured fact, true or not.
ReceiveMeasured(val) ==
  /\ deliveries < MaxDeliver
  /\ received' = received \cup {MeasuredItem(val)}
  /\ deliveries' = deliveries + 1
  /\ UNCHANGED <<live, viaPeer, fenceOrdered, sends, offTopicSent, seen>>

\* A report arrives on a topic the seat hears, with whatever labels its sender declared.
Deliver(t, L) ==
  /\ deliveries < MaxDeliver
  /\ received' = received \cup {[kind |-> "report", topic |-> t, labels |-> DeliveredLabels(t, L),
                                 clear |-> t \in ClearTopics, value |-> "none"]}
  /\ deliveries' = deliveries + 1
  /\ seen' = seen \cup (IF "untrusted" \in L THEN {} ELSE {"labelLow"})
  /\ UNCHANGED <<live, viaPeer, fenceOrdered, sends, offTopicSent>>

\* A report on a topic the seat does not hear is not delivered.
Drop(t) ==
  /\ seen' = seen \cup {"dropped"}
  /\ UNCHANGED <<live, viaPeer, fenceOrdered, received, deliveries, sends, offTopicSent>>

\* The mesh's declaration and the bundle's rule for a send, the first open to one mutation.
TopicOK(t)  == Mut = "M_ANYTOPIC" \/ t \in Declared
BundleOK(t) == t \notin Silenced

\* An honest governor permits a send. It is not ordered and is not charged to K_up.
Send(t) ==
  /\ live
  /\ sends < MaxSend
  /\ TopicOK(t)
  /\ BundleOK(t)
  /\ sends' = sends + 1
  /\ offTopicSent' = (offTopicSent \/ t \notin Declared)
  /\ seen' = seen \cup {"sent"}
  /\ UNCHANGED <<live, viaPeer, fenceOrdered, received, deliveries>>

RefuseSend(t) ==
  /\ ~(TopicOK(t) /\ BundleOK(t))
  /\ seen' = seen \cup (IF TopicOK(t) THEN {} ELSE {"refSendDecl"})
                  \cup (IF BundleOK(t) THEN {} ELSE {"refSendBundle"})
  /\ UNCHANGED <<live, viaPeer, fenceOrdered, received, deliveries, sends, offTopicSent>>

Permit(e) ==
  /\ Decide(e, received)
  /\ seen' = seen \cup {"permit"}
                  \cup (IF e = "egress" /\ \E y \in received : y.kind = "report" /\ ~y.clear /\ "untrusted" \in y.labels
                        THEN {"handlePermit"} ELSE {})
                  \cup (IF viaPeer THEN {"relayedLease"} ELSE {})
  /\ UNCHANGED <<live, viaPeer, fenceOrdered, received, deliveries, sends, offTopicSent>>

Refuse(e) ==
  /\ ~Decide(e, received)
  /\ seen' = seen \cup (IF Decide(e, {}) /\ LabelStop(e, received) THEN {"narrowedClear"} ELSE {})
                  \cup (IF MeasuredStop(e, received) THEN {"measuredStop"} ELSE {})
                  \cup (IF CertifiedStop(received) THEN {"fenceStop"} ELSE {})
  /\ UNCHANGED <<live, viaPeer, fenceOrdered, received, deliveries, sends, offTopicSent>>

Next ==
  \/ \E via \in BOOLEAN : Grant(via)
  \/ OrderFence
  \/ RelayFence
  \/ \E val \in {"near", "far"} : ReceiveMeasured(val)
  \/ \E t \in Heard, L \in SUBSET Labels : Deliver(t, L)
  \/ \E t \in Topics \ Heard : Drop(t)
  \/ \E t \in Topics : Send(t) \/ RefuseSend(t)
  \/ \E e \in Entries : Permit(e) \/ Refuse(e)

Spec == Init /\ [][Next]_vars

\* --- the properties ------------------------------------------------------------

PeerAddsNothing == \A e \in Entries : Decide(e, received) => Decide(e, {})

NarrowsInReceived ==
  \A e \in Entries : \A T \in SUBSET received : Decide(e, received) => Decide(e, T)

ReceivedIsUntrusted ==
  \A x \in received : x.kind = "report" => ("untrusted" \in x.labels /\ Name[x.topic] \in x.labels)

SendWithinTopics == ~offTopicSent

Safe == PeerAddsNothing /\ NarrowsInReceived /\ ReceivedIsUntrusted /\ SendWithinTopics

\* --- witnesses: each must be VIOLATED ------------------------------------------

NeverPermitted            == "permit" \notin seen
NeverNarrowedByClear      == "narrowedClear" \notin seen  \* a clear report refuses what is permitted without it
NeverPermitAfterHandle    == "handlePermit" \notin seen   \* a report delivered as a handle does not narrow
NeverRefusedByMeasured    == "measuredStop" \notin seen
NeverStoppedByFence       == "fenceStop" \notin seen
NeverDroppedOffTopic      == "dropped" \notin seen
NeverSendRefusedDeclared  == "refSendDecl" \notin seen
NeverSendRefusedByBundle  == "refSendBundle" \notin seen
NeverSent                 == "sent" \notin seen
NeverSenderLabelledLow    == "labelLow" \notin seen       \* a sender declares no `untrusted`
NeverPermitUnderRelayedLease == "relayedLease" \notin seen \* the header's finding on §1
=============================================================================
