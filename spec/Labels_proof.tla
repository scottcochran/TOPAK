---------------------------- MODULE Labels_proof ----------------------------
(* TLAPS proofs of the invariants Labels.tla states (ADR-0047, Proposed: the     *)
(* Listener labels what it delivers), for every bound MaxSeq:                    *)
(*                                                                               *)
(*   NoUnlabelledDeliveryAlways          (Mut # "M_LOAD")                        *)
(*   OutsideResultIsUntrustedAlways      (Mut # "M_LOAD")                        *)
(*   ReservedReleasedOnlyIfIssuedAlways  (Mut # "M_LOAD")                        *)
(*   ResultLabelCoversInputsAlways       (Mut # "M_JOIN")                        *)
(*   SuppressedNeverInGuestAlways        (Mut # "M_DELIVER")                     *)
(*   ClearSetCoversGuestAlways           (Mut \notin {"M_RESET", "M_DELIVER"})   *)
(*   ClearSetOnlyGrowsAlways             (Mut # "M_RESET")                       *)
(*   LabelsCoverTruthAlways              (Mut \notin Honest's five)              *)
(*   NoReadThenSendAlways                (those five, and Mut # "M_F1")          *)
(*   NoSteeredDestinationAlways          (those five, and Mut \notin {"M_F2",    *)
(*                                        "M_F3"})                               *)
(*   SafeAlways == Spec => []Safe        (Mut = "none")                          *)
(*                                                                               *)
(* "Those five" are M_JOIN, M_LITERAL, M_LOAD, M_RESET and M_DELIVER: the        *)
(* mutations under which a label, or clearSet, stops covering what it is about.  *)
(* The floor's minimum is proved from that covering: LabelsCoverTruth,           *)
(* ClearSetCoversGuest, and the task's label being in clearSet. With them, a     *)
(* call that a tainted Thinker could use to send a secret, or whose destination  *)
(* is tainted, meets the condition of F1, F2 or F3 and is refused.               *)
(*                                                                               *)
(* Writing the hypotheses added four rows to what the TLC run of 10.03 had:      *)
(* M_LOAD, M_RESET and M_DELIVER break LabelsCoverTruth as well, the last two    *)
(* because a literal input's label is taken from clearSet (R10); and M_DELIVER   *)
(* breaks ClearSetCoversGuest. TLC confirms each (Labels-results-2026.10.04).    *)
(* It also needed an invariant no property names: only an item that exists is    *)
(* in the guest. Without it a new item could take an id the guest already held.  *)
(*                                                                               *)
(* The one assumption is that MaxSeq is a natural number, which every run        *)
(* supplies. The theorems hold for every value of it, where TLC ran 3 and 4.     *)
(*                                                                               *)
(* Labels.tla is not edited; this module extends it. The operators below name    *)
(* the parts of Actuate's LET, so that a step can be stated once (ActuateShape)  *)
(* and each invariant proved from the shape. The mutations and the witnesses     *)
(* stay with TLC.                                                                *)
(*                                                                               *)
(* Check with:  ../tools/tlapm Labels_proof.tla   (from spec/; see               *)
(*              proof-results.sh and proof-cert.sh for the results files)        *)
EXTENDS Labels, TLAPS

ASSUME MaxSeqNat == MaxSeq \in Nat

InL(d, b)  == InLabel(d) \cup InLabel(b)
F1(t, d, b) == Mut # "M_F1" /\ Outward[t] /\ U \in clearSet /\ (R \in clearSet \/ R \in InL(d, b))
F2(t, d)    == Mut # "M_F2" /\ Outward[t] /\ U \in clearSet /\ d = Lit
F3(t, d)    == Mut # "M_F3" /\ Outward[t] /\ IsHandle(d) /\ U \in Item(d).label
JoinH(d, b) == IF Mut = "M_JOIN" THEN {} ELSE InL(d, b)
JoinL(d, b) == IF (d = Lit \/ b = Lit) /\ Mut # "M_LITERAL" THEN clearSet ELSE {}
NewLabel(t, d, b)  == (Decl(t) \cup JoinH(d, b) \cup JoinL(d, b)) \ Releases(t)
NewTaint(t, d, b)  == Outward[t] \/ InTaint(d) \/ InTaint(b)
NewSecret(t, d, b) == t = "vault" \/ ((InSecret(d) \/ InSecret(b)) /\ ~(Releases(t) # {} /\ issued))
NewItem(t, d, b) ==
  [id |-> seq + 1, tool |-> t, label |-> NewLabel(t, d, b),
   labelled |-> (t # "fetch" \/ fetchDeclared),
   mode |-> IF Clear(NewLabel(t, d, b)) THEN "clear" ELSE "handle",
   rawIn |-> InL(d, b), tainted |-> NewTaint(t, d, b), secret |-> NewSecret(t, d, b)]
NewEffect(t, d, b) ==
  [tool |-> t, by |-> ThinkerTainted, steered |-> InTaint(d), leak |-> InSecret(d) \/ InSecret(b)]
DocItem ==
  [id |-> Doc, tool |-> "root", label |-> {}, labelled |-> TRUE,
   mode |-> IF Clear({}) THEN "clear" ELSE "handle", rawIn |-> {}, tainted |-> FALSE, secret |-> FALSE]

\* An input is a literal, absent, or the id of an item that exists.
ArgOK(a) == a = Lit \/ a = None \/ (a \in Ids /\ Exists(a))

\* The three shapes a step has.
Still == UNCHANGED <<taskLabel, fetchDeclared, fetchLabel, suppress, echoReleases, issued,
                     items, guest, clearSet, seq, effects>>
ConsultS ==
  /\ ~Exists(Doc)
  /\ items' = items \cup {DocItem}
  /\ Deliver(Doc, {})
  /\ UNCHANGED <<taskLabel, fetchDeclared, fetchLabel, suppress, echoReleases, issued, seq, effects>>
Admit(t, d, b) ==
  /\ seq < MaxSeq
  /\ ArgOK(d) /\ ArgOK(b)
  /\ ~F1(t, d, b) /\ ~F2(t, d) /\ ~F3(t, d)
  /\ items' = items \cup {NewItem(t, d, b)}
  /\ Deliver(seq + 1, NewLabel(t, d, b))
  /\ seq' = seq + 1
  /\ effects' = IF Outward[t] THEN effects \cup {NewEffect(t, d, b)} ELSE effects
  /\ UNCHANGED <<taskLabel, fetchDeclared, fetchLabel, suppress, echoReleases, issued>>

LEMMA ActuateShape ==
    ASSUME NEW t \in Tools, NEW d, NEW b, Actuate(t, d, b)
    PROVE  Still \/ Admit(t, d, b)
<1>1. ArgOK(d) /\ ArgOK(b)
    BY DEF Actuate, ArgOK
<1> QED
    BY <1>1 DEF Actuate, Still, Admit, bundle, F1, F2, F3, InL, JoinH, JoinL, NewLabel, NewTaint,
              NewSecret, NewItem, NewEffect

LEMMA StepShape ==
    ASSUME [Next]_vars
    PROVE  Still \/ ConsultS \/ \E t \in Tools : \E d, b : Admit(t, d, b)
<1>1. CASE UNCHANGED vars
    BY <1>1 DEF vars, Still
<1>2. CASE Consult
    BY <1>2 DEF Consult, ConsultS, DocItem, bundle
<1>3. ASSUME NEW t \in Tools, NEW d \in {None, Lit} \cup Ids, NEW b \in {None, Lit} \cup Ids, Actuate(t, d, b)
      PROVE  Still \/ Admit(t, d, b)
    BY <1>3, ActuateShape
<1> QED
    BY <1>1, <1>2, <1>3 DEF Next

\* A handle among a call's inputs names an item that exists.
LEMMA HandleExists ==
    ASSUME NEW a, ArgOK(a), IsHandle(a)
    PROVE  Item(a) \in items
<1>1. a # Lit /\ a # None
    BY MaxSeqNat DEF IsHandle, Ids, Lit, None
<1>2. \E x \in items : x.id = a
    BY <1>1 DEF ArgOK, Exists
<1> QED
    BY <1>2 DEF Item

-----------------------------------------------------------------------------
(* The supporting invariants.                                                    *)

TypeOK == /\ echoReleases \in {{}, {R}}
          /\ seq \in Nat /\ seq <= MaxSeq
\* The load checks held of the bundle that loaded (F4 to F6).
Loaded == fetchDeclared /\ U \in fetchLabel /\ (echoReleases # {} => issued)
\* A result's id is at most seq; the consulted object's is Doc.
IdsUsed == \A x \in items : x.id \in 1..seq \/ x.id = Doc
\* The task is delivered clear.
TaskIn == taskLabel \subseteq clearSet
\* Only an item that exists is in the guest.
GuestIn == \A i \in guest : Exists(i)

LEMMA TypeNext == ASSUME TypeOK, [Next]_vars PROVE TypeOK'
<1>1. CASE Still
    BY <1>1 DEF Still, TypeOK
<1>2. CASE ConsultS
    BY <1>2 DEF ConsultS, TypeOK
<1>3. ASSUME NEW t \in Tools, NEW d, NEW b, Admit(t, d, b) PROVE TypeOK'
    BY <1>3, MaxSeqNat DEF Admit, TypeOK
<1> QED
    BY <1>1, <1>2, <1>3, StepShape

LEMMA LoadedNext == ASSUME Loaded, [Next]_vars PROVE Loaded'
<1>1. CASE Still
    BY <1>1 DEF Still, Loaded
<1>2. CASE ConsultS
    BY <1>2 DEF ConsultS, Loaded
<1>3. ASSUME NEW t \in Tools, NEW d, NEW b, Admit(t, d, b) PROVE Loaded'
    BY <1>3 DEF Admit, Loaded
<1> QED
    BY <1>1, <1>2, <1>3, StepShape

LEMMA IdsNext == ASSUME TypeOK, IdsUsed, [Next]_vars PROVE IdsUsed'
<1>1. CASE Still
    BY <1>1 DEF Still, IdsUsed
<1>2. CASE ConsultS
    BY <1>2 DEF ConsultS, IdsUsed, DocItem
<1>3. ASSUME NEW t \in Tools, NEW d, NEW b, Admit(t, d, b) PROVE IdsUsed'
    <2>1. NewItem(t, d, b).id = seq + 1
        BY DEF NewItem
    <2> QED
        BY <1>3, <2>1, MaxSeqNat DEF Admit, IdsUsed, TypeOK
<1> QED
    BY <1>1, <1>2, <1>3, StepShape

\* The id a step gives a new item is fresh.
LEMMA FreshResult ==
    ASSUME TypeOK, IdsUsed, seq < MaxSeq
    PROVE  \A x \in items : x.id # seq + 1
BY MaxSeqNat DEF TypeOK, IdsUsed, Doc

LEMMA GuestNext == ASSUME GuestIn, [Next]_vars PROVE GuestIn'
<1>1. CASE Still
    BY <1>1 DEF Still, GuestIn, Exists
<1>2. CASE ConsultS
    <2>1. items' = items \cup {DocItem} /\ guest' \subseteq guest \cup {Doc} /\ DocItem.id = Doc
        BY <1>2 DEF ConsultS, Deliver, DocItem
    <2> QED
        BY <2>1 DEF GuestIn, Exists
<1>3. ASSUME NEW t \in Tools, NEW d, NEW b, Admit(t, d, b) PROVE GuestIn'
    <2>1. /\ items' = items \cup {NewItem(t, d, b)} /\ guest' \subseteq guest \cup {seq + 1}
          /\ NewItem(t, d, b).id = seq + 1
        BY <1>3 DEF Admit, Deliver, NewItem
    <2> QED
        BY <2>1 DEF GuestIn, Exists
<1> QED
    BY <1>1, <1>2, <1>3, StepShape

LEMMA TaskNext == ASSUME Mut # "M_RESET", TaskIn, [Next]_vars PROVE TaskIn'
<1>1. CASE Still
    BY <1>1 DEF Still, TaskIn
<1>2. CASE ConsultS
    BY <1>2 DEF ConsultS, TaskIn, Deliver
<1>3. ASSUME NEW t \in Tools, NEW d, NEW b, Admit(t, d, b) PROVE TaskIn'
    BY <1>3 DEF Admit, TaskIn, Deliver
<1> QED
    BY <1>1, <1>2, <1>3, StepShape

-----------------------------------------------------------------------------
(* The invariants that are about one item alone.                                 *)

LEMMA UnlabelledNext == ASSUME Loaded, NoUnlabelledDelivery, [Next]_vars PROVE NoUnlabelledDelivery'
<1>1. CASE Still
    BY <1>1 DEF Still, NoUnlabelledDelivery
<1>2. CASE ConsultS
    BY <1>2 DEF ConsultS, NoUnlabelledDelivery, DocItem
<1>3. ASSUME NEW t \in Tools, NEW d, NEW b, Admit(t, d, b) PROVE NoUnlabelledDelivery'
    <2>1. NewItem(t, d, b).labelled
        BY DEF NewItem, Loaded
    <2> QED
        BY <1>3, <2>1 DEF Admit, NoUnlabelledDelivery
<1> QED
    BY <1>1, <1>2, <1>3, StepShape

LEMMA OutsideNext ==
    ASSUME TypeOK, Loaded, OutsideResultIsUntrusted, [Next]_vars PROVE OutsideResultIsUntrusted'
<1>1. CASE Still
    BY <1>1 DEF Still, OutsideResultIsUntrusted
<1>2. CASE ConsultS
    <2>1. DocItem.tool = "root" /\ "root" \notin Tools
        BY DEF DocItem, Tools
    <2> QED
        BY <1>2, <2>1 DEF ConsultS, OutsideResultIsUntrusted
<1>3. ASSUME NEW t \in Tools, NEW d, NEW b, Admit(t, d, b) PROVE OutsideResultIsUntrusted'
    <2>1. Outward[t] => U \in NewLabel(t, d, b)
        <3> SUFFICES ASSUME Outward[t] PROVE U \in NewLabel(t, d, b)
            OBVIOUS
        <3>1. t = "fetch" \/ t = "send"
            BY DEF Outward, Tools
        <3>2. U \in Decl(t)
            BY <3>1 DEF Decl, Loaded
        <3>3. Releases(t) = {}
            BY <3>1 DEF Releases
        <3> QED
            BY <3>2, <3>3 DEF NewLabel
    <2>2. NewItem(t, d, b).tool = t /\ NewItem(t, d, b).label = NewLabel(t, d, b)
        BY DEF NewItem
    <2> QED
        BY <1>3, <2>1, <2>2 DEF Admit, OutsideResultIsUntrusted
<1> QED
    BY <1>1, <1>2, <1>3, StepShape

LEMMA ReleasedNext ==
    ASSUME Loaded, ReservedReleasedOnlyIfIssued, [Next]_vars PROVE ReservedReleasedOnlyIfIssued'
<1>0. \A u : Releases(u) # {} => issued
    BY DEF Releases, Loaded
<1>1. CASE Still
    BY <1>1 DEF Still, ReservedReleasedOnlyIfIssued, Releases
<1>2. CASE ConsultS
    <2>1. issued' = issued /\ echoReleases' = echoReleases
        BY <1>2 DEF ConsultS
    <2> QED
        BY <1>0, <1>2, <2>1 DEF ConsultS, ReservedReleasedOnlyIfIssued, Releases
<1>3. ASSUME NEW t \in Tools, NEW d, NEW b, Admit(t, d, b) PROVE ReservedReleasedOnlyIfIssued'
    <2>1. issued' = issued /\ echoReleases' = echoReleases
        BY <1>3 DEF Admit
    <2> QED
        BY <1>0, <1>3, <2>1 DEF Admit, ReservedReleasedOnlyIfIssued, Releases
<1> QED
    BY <1>1, <1>2, <1>3, StepShape

LEMMA CoversInputsNext ==
    ASSUME Mut # "M_JOIN", ResultLabelCoversInputs, [Next]_vars PROVE ResultLabelCoversInputs'
<1>1. CASE Still
    BY <1>1 DEF Still, ResultLabelCoversInputs, Releases
<1>2. CASE ConsultS
    <2>1. echoReleases' = echoReleases /\ DocItem.rawIn = {}
        BY <1>2 DEF ConsultS, DocItem
    <2> QED
        BY <1>2, <2>1 DEF ConsultS, ResultLabelCoversInputs, Releases
<1>3. ASSUME NEW t \in Tools, NEW d, NEW b, Admit(t, d, b) PROVE ResultLabelCoversInputs'
    <2>1. echoReleases' = echoReleases
        BY <1>3 DEF Admit
    <2>2. /\ NewItem(t, d, b).tool = t /\ NewItem(t, d, b).rawIn = InL(d, b)
          /\ NewItem(t, d, b).label = NewLabel(t, d, b)
        BY DEF NewItem
    <2>3. (InL(d, b) \ Releases(t)) \subseteq NewLabel(t, d, b)
        BY DEF NewLabel, JoinH
    <2> QED
        BY <1>3, <2>1, <2>2, <2>3 DEF Admit, ResultLabelCoversInputs, Releases
<1> QED
    BY <1>1, <1>2, <1>3, StepShape

-----------------------------------------------------------------------------
(* The invariants about what is in the guest.                                    *)

LEMMA SuppressedNext ==
    ASSUME Mut # "M_DELIVER", TypeOK, IdsUsed, GuestIn, SuppressedNeverInGuest, [Next]_vars
    PROVE  SuppressedNeverInGuest'
<1>1. CASE Still
    BY <1>1 DEF Still, SuppressedNeverInGuest, Clear
<1>2. CASE ConsultS
    <2>1. /\ suppress' = suppress /\ items' = items \cup {DocItem}
          /\ guest' \subseteq guest \cup {Doc} /\ DocItem.label = {}
        BY <1>2 DEF ConsultS, Deliver, DocItem
    <2>2. \A x \in items : x.id # Doc
        BY <1>2 DEF ConsultS, Exists
    <2>3. ASSUME NEW x \in items', x.id \in guest' PROVE x.label \cap suppress = {}
        <3>1. CASE x \in items
            BY <3>1, <2>1, <2>2, <2>3 DEF SuppressedNeverInGuest, Clear
        <3>2. CASE x = DocItem
            BY <3>2, <2>1
        <3> QED
            BY <3>1, <3>2, <2>1
    <2> QED
        BY <2>1, <2>3 DEF SuppressedNeverInGuest, Clear
<1>3. ASSUME NEW t \in Tools, NEW d, NEW b, Admit(t, d, b) PROVE SuppressedNeverInGuest'
    <2>1. suppress' = suppress /\ \A x \in items : x.id # seq + 1
        BY <1>3, FreshResult DEF Admit
    <2>2. NewItem(t, d, b).id = seq + 1 /\ NewItem(t, d, b).label = NewLabel(t, d, b)
        BY DEF NewItem
    <2>3. /\ items' = items \cup {NewItem(t, d, b)}
          /\ guest' = IF Clear(NewLabel(t, d, b)) THEN guest \cup {seq + 1} ELSE guest
        BY <1>3 DEF Admit, Deliver
    <2>4. seq + 1 \notin guest
        BY <2>1 DEF GuestIn, Exists
    <2>5. ASSUME NEW x \in items', x.id \in guest' PROVE x.label \cap suppress = {}
        <3>1. CASE x \in items
            <4>1. x.id \in guest
                BY <3>1, <2>1, <2>3, <2>5
            <4> QED
                BY <3>1, <4>1 DEF SuppressedNeverInGuest, Clear
        <3>2. CASE x = NewItem(t, d, b)
            <4>1. Clear(NewLabel(t, d, b))
                BY <3>2, <2>2, <2>3, <2>4, <2>5
            <4> QED
                BY <3>2, <2>2, <4>1 DEF Clear
        <3> QED
            BY <3>1, <3>2, <2>3
    <2> QED
        BY <2>1, <2>5 DEF SuppressedNeverInGuest, Clear
<1> QED
    BY <1>1, <1>2, <1>3, StepShape

LEMMA CoverNext ==
    ASSUME Mut \notin {"M_RESET", "M_DELIVER"}, TypeOK, IdsUsed, GuestIn, ClearSetCoversGuest, [Next]_vars
    PROVE  ClearSetCoversGuest'
<1>1. CASE Still
    BY <1>1 DEF Still, ClearSetCoversGuest
<1>2. CASE ConsultS
    <2>1. /\ items' = items \cup {DocItem} /\ guest' \subseteq guest \cup {Doc}
          /\ clearSet \subseteq clearSet' /\ DocItem.label = {}
        BY <1>2 DEF ConsultS, Deliver, DocItem
    <2>2. \A x \in items : x.id # Doc
        BY <1>2 DEF ConsultS, Exists
    <2>3. ASSUME NEW x \in items', x.id \in guest' PROVE x.label \subseteq clearSet'
        <3>1. CASE x \in items
            BY <3>1, <2>1, <2>2, <2>3 DEF ClearSetCoversGuest
        <3>2. CASE x = DocItem
            BY <3>2, <2>1
        <3> QED
            BY <3>1, <3>2, <2>1
    <2> QED
        BY <2>3 DEF ClearSetCoversGuest
<1>3. ASSUME NEW t \in Tools, NEW d, NEW b, Admit(t, d, b) PROVE ClearSetCoversGuest'
    <2>1. \A x \in items : x.id # seq + 1
        BY <1>3, FreshResult DEF Admit
    <2>2. NewItem(t, d, b).id = seq + 1 /\ NewItem(t, d, b).label = NewLabel(t, d, b)
        BY DEF NewItem
    <2>3. /\ items' = items \cup {NewItem(t, d, b)}
          /\ guest' = IF Clear(NewLabel(t, d, b)) THEN guest \cup {seq + 1} ELSE guest
          /\ clearSet' = IF Clear(NewLabel(t, d, b)) THEN clearSet \cup NewLabel(t, d, b) ELSE clearSet
        BY <1>3 DEF Admit, Deliver
    <2>4. seq + 1 \notin guest
        BY <2>1 DEF GuestIn, Exists
    <2>5. ASSUME NEW x \in items', x.id \in guest' PROVE x.label \subseteq clearSet'
        <3>1. CASE x \in items
            <4>1. x.id \in guest
                BY <3>1, <2>1, <2>3, <2>5
            <4> QED
                BY <3>1, <4>1, <2>3 DEF ClearSetCoversGuest
        <3>2. CASE x = NewItem(t, d, b)
            <4>1. Clear(NewLabel(t, d, b))
                BY <3>2, <2>2, <2>3, <2>4, <2>5
            <4> QED
                BY <3>2, <2>2, <2>3, <4>1
        <3> QED
            BY <3>1, <3>2, <2>3
    <2> QED
        BY <2>5 DEF ClearSetCoversGuest
<1> QED
    BY <1>1, <1>2, <1>3, StepShape

LEMMA GrowsStep == ASSUME Mut # "M_RESET", [Next]_vars PROVE clearSet \subseteq clearSet'
<1>1. CASE Still
    BY <1>1 DEF Still
<1>2. CASE ConsultS
    BY <1>2 DEF ConsultS, Deliver
<1>3. ASSUME NEW t \in Tools, NEW d, NEW b, Admit(t, d, b) PROVE clearSet \subseteq clearSet'
    BY <1>3 DEF Admit, Deliver
<1> QED
    BY <1>1, <1>2, <1>3, StepShape

-----------------------------------------------------------------------------
(* Labels cover the truth, and with that the floor's minimum.                    *)

\* What the Thinker has really read is in clearSet.
LEMMA ThinkerCovered ==
    ASSUME TaskIn, ClearSetCoversGuest, LabelsCoverTruth
    PROVE  (ThinkerTainted => U \in clearSet) /\ (ThinkerSecret => R \in clearSet)
BY DEF TaskIn, ClearSetCoversGuest, LabelsCoverTruth, ThinkerTainted, ThinkerSecret

\* What an input really carries is in its label, or, for a literal, in clearSet.
LEMMA InputCovered ==
    ASSUME TaskIn, ClearSetCoversGuest, LabelsCoverTruth, NEW a, ArgOK(a)
    PROVE  /\ InTaint(a) => (IF IsHandle(a) THEN U \in InLabel(a) ELSE a = Lit /\ U \in clearSet)
           /\ InSecret(a) => (IF IsHandle(a) THEN R \in InLabel(a) ELSE a = Lit /\ R \in clearSet)
<1>1. CASE IsHandle(a)
    <2>1. Item(a) \in items
        BY <1>1, HandleExists
    <2> QED
        BY <1>1, <2>1 DEF InTaint, InSecret, InLabel, LabelsCoverTruth
<1>2. CASE ~IsHandle(a)
    BY <1>2, ThinkerCovered DEF InTaint, InSecret
<1> QED
    BY <1>1, <1>2

Honest == Mut \notin {"M_JOIN", "M_LITERAL", "M_LOAD", "M_RESET", "M_DELIVER"}

LEMMA TruthNext ==
    ASSUME Honest, TypeOK, Loaded, TaskIn, ClearSetCoversGuest, LabelsCoverTruth, [Next]_vars
    PROVE  LabelsCoverTruth'
<1>1. CASE Still
    BY <1>1 DEF Still, LabelsCoverTruth
<1>2. CASE ConsultS
    <2>1. ~DocItem.tainted /\ ~DocItem.secret
        BY DEF DocItem
    <2> QED
        BY <1>2, <2>1 DEF ConsultS, LabelsCoverTruth
<1>3. ASSUME NEW t \in Tools, NEW d, NEW b, Admit(t, d, b) PROVE LabelsCoverTruth'
    <2>0. ArgOK(d) /\ ArgOK(b)
        BY <1>3 DEF Admit
    <2>1. U # R /\ Releases(t) \subseteq {R}
        BY DEF U, R, Releases, TypeOK
    <2>2. JoinH(d, b) = InL(d, b)
        BY DEF JoinH, Honest
    <2>3. (d = Lit \/ b = Lit) => JoinL(d, b) = clearSet
        BY DEF JoinL, Honest
    <2>4. NewTaint(t, d, b) => U \in NewLabel(t, d, b)
        <3> SUFFICES ASSUME NewTaint(t, d, b) PROVE U \in Decl(t) \cup JoinH(d, b) \cup JoinL(d, b)
            BY <2>1 DEF NewLabel
        <3>1. CASE Outward[t]
            <4>1. t = "fetch" \/ t = "send"
                BY <3>1 DEF Outward, Tools
            <4> QED
                BY <4>1 DEF Decl, Loaded
        <3>2. CASE InTaint(d)
            BY <3>2, <2>0, <2>2, <2>3, InputCovered DEF InL
        <3>3. CASE InTaint(b)
            BY <3>3, <2>0, <2>2, <2>3, InputCovered DEF InL
        <3> QED
            BY <3>1, <3>2, <3>3 DEF NewTaint
    <2>5. NewSecret(t, d, b) => R \in NewLabel(t, d, b)
        <3> SUFFICES ASSUME NewSecret(t, d, b) PROVE R \in NewLabel(t, d, b)
            OBVIOUS
        <3>1. CASE t = "vault"
            BY <3>1 DEF NewLabel, Decl, Releases
        <3>2. CASE (InSecret(d) \/ InSecret(b)) /\ ~(Releases(t) # {} /\ issued)
            <4>1. Releases(t) = {}
                BY <3>2 DEF Releases, Loaded
            <4>2. R \in JoinH(d, b) \cup JoinL(d, b)
                <5>1. CASE InSecret(d)
                    BY <5>1, <2>0, <2>2, <2>3, InputCovered DEF InL
                <5>2. CASE InSecret(b)
                    BY <5>2, <2>0, <2>2, <2>3, InputCovered DEF InL
                <5> QED
                    BY <3>2, <5>1, <5>2
            <4> QED
                BY <4>1, <4>2 DEF NewLabel
        <3> QED
            BY <3>1, <3>2 DEF NewSecret
    <2>6. /\ NewItem(t, d, b).label = NewLabel(t, d, b)
          /\ NewItem(t, d, b).tainted = NewTaint(t, d, b)
          /\ NewItem(t, d, b).secret = NewSecret(t, d, b)
        BY DEF NewItem
    <2> QED
        BY <1>3, <2>4, <2>5, <2>6 DEF Admit, LabelsCoverTruth
<1> QED
    BY <1>1, <1>2, <1>3, StepShape

LEMMA ReadSendNext ==
    ASSUME Mut # "M_F1", TaskIn, ClearSetCoversGuest, LabelsCoverTruth, NoReadThenSend, [Next]_vars
    PROVE  NoReadThenSend'
<1>1. CASE Still
    BY <1>1 DEF Still, NoReadThenSend
<1>2. CASE ConsultS
    BY <1>2 DEF ConsultS, NoReadThenSend
<1>3. ASSUME NEW t \in Tools, NEW d, NEW b, Admit(t, d, b) PROVE NoReadThenSend'
    <2>1. CASE ~Outward[t]
        BY <1>3, <2>1 DEF Admit, NoReadThenSend
    <2>2. CASE Outward[t]
        <3>0. ArgOK(d) /\ ArgOK(b) /\ ~F1(t, d, b)
            BY <1>3 DEF Admit
        <3>1. ~(ThinkerTainted /\ (InSecret(d) \/ InSecret(b)))
            <4> SUFFICES ASSUME ThinkerTainted, InSecret(d) \/ InSecret(b) PROVE FALSE
                OBVIOUS
            <4>1. U \in clearSet
                BY ThinkerCovered
            <4>2. R \in clearSet \/ R \in InL(d, b)
                <5>1. CASE InSecret(d)
                    BY <5>1, <3>0, InputCovered DEF InL
                <5>2. CASE InSecret(b)
                    BY <5>2, <3>0, InputCovered DEF InL
                <5> QED
                    BY <5>1, <5>2
            <4> QED
                BY <2>2, <3>0, <4>1, <4>2 DEF F1
        <3>2. /\ NewEffect(t, d, b).by = ThinkerTainted
              /\ NewEffect(t, d, b).leak = (InSecret(d) \/ InSecret(b))
            BY DEF NewEffect
        <3> QED
            BY <1>3, <2>2, <3>1, <3>2 DEF Admit, NoReadThenSend
    <2> QED
        BY <2>1, <2>2
<1> QED
    BY <1>1, <1>2, <1>3, StepShape

LEMMA SteeredNext ==
    ASSUME Mut \notin {"M_F2", "M_F3"}, TaskIn, ClearSetCoversGuest, LabelsCoverTruth,
           NoSteeredDestination, [Next]_vars
    PROVE  NoSteeredDestination'
<1>1. CASE Still
    BY <1>1 DEF Still, NoSteeredDestination
<1>2. CASE ConsultS
    BY <1>2 DEF ConsultS, NoSteeredDestination
<1>3. ASSUME NEW t \in Tools, NEW d, NEW b, Admit(t, d, b) PROVE NoSteeredDestination'
    <2>1. CASE ~Outward[t]
        BY <1>3, <2>1 DEF Admit, NoSteeredDestination
    <2>2. CASE Outward[t]
        <3>0. ArgOK(d) /\ ~F2(t, d) /\ ~F3(t, d)
            BY <1>3 DEF Admit
        <3>1. ~InTaint(d)
            <4> SUFFICES ASSUME InTaint(d) PROVE FALSE
                OBVIOUS
            <4>1. CASE IsHandle(d)
                <5>1. U \in Item(d).label
                    BY <4>1, <3>0, InputCovered DEF InLabel
                <5> QED
                    BY <2>2, <3>0, <4>1, <5>1 DEF F3
            <4>2. CASE ~IsHandle(d)
                <5>1. d = Lit /\ U \in clearSet
                    BY <4>2, <3>0, InputCovered
                <5> QED
                    BY <2>2, <3>0, <5>1 DEF F2
            <4> QED
                BY <4>1, <4>2
        <3>2. NewEffect(t, d, b).steered = InTaint(d)
            BY DEF NewEffect
        <3> QED
            BY <1>3, <2>2, <3>1, <3>2 DEF Admit, NoSteeredDestination
    <2> QED
        BY <2>1, <2>2
<1> QED
    BY <1>1, <1>2, <1>3, StepShape

-----------------------------------------------------------------------------
LEMMA InitBase == Init => TypeOK /\ IdsUsed /\ GuestIn /\ TaskIn
BY MaxSeqNat DEF Init, TypeOK, IdsUsed, GuestIn, TaskIn

LEMMA InitLoaded == ASSUME Mut # "M_LOAD" PROVE Init => Loaded
BY DEF Init, WellFormed, Loaded

THEOREM BaseAlways == Spec => [](TypeOK /\ IdsUsed /\ GuestIn)
<1>1. (TypeOK /\ IdsUsed /\ GuestIn) /\ [Next]_vars => (TypeOK /\ IdsUsed /\ GuestIn)'
    BY TypeNext, IdsNext, GuestNext
<1> QED
    BY <1>1, InitBase, PTL DEF Spec

THEOREM LoadedAlways == ASSUME Mut # "M_LOAD" PROVE Spec => []Loaded
<1>1. Loaded /\ [Next]_vars => Loaded'
    BY LoadedNext
<1>2. Init => Loaded
    BY InitLoaded
<1> QED
    BY <1>1, <1>2, PTL DEF Spec

THEOREM TaskAlways == ASSUME Mut # "M_RESET" PROVE Spec => []TaskIn
<1>1. TaskIn /\ [Next]_vars => TaskIn'
    BY TaskNext
<1> QED
    BY <1>1, InitBase, PTL DEF Spec

THEOREM NoUnlabelledDeliveryAlways == ASSUME Mut # "M_LOAD" PROVE Spec => []NoUnlabelledDelivery
<1>1. Init => NoUnlabelledDelivery
    BY DEF Init, NoUnlabelledDelivery
<1>2. Loaded /\ NoUnlabelledDelivery /\ [Next]_vars => NoUnlabelledDelivery'
    BY UnlabelledNext
<1>3. Spec => []Loaded
    BY LoadedAlways
<1> QED
    BY <1>1, <1>2, <1>3, PTL DEF Spec

THEOREM OutsideResultIsUntrustedAlways == ASSUME Mut # "M_LOAD" PROVE Spec => []OutsideResultIsUntrusted
<1>1. Init => OutsideResultIsUntrusted
    BY DEF Init, OutsideResultIsUntrusted
<1>2. (TypeOK /\ IdsUsed /\ GuestIn) /\ Loaded /\ OutsideResultIsUntrusted /\ [Next]_vars => OutsideResultIsUntrusted'
    BY OutsideNext
<1>3. Spec => []Loaded
    BY LoadedAlways
<1> QED
    BY <1>1, <1>2, <1>3, BaseAlways, PTL DEF Spec

THEOREM ReservedReleasedOnlyIfIssuedAlways ==
    ASSUME Mut # "M_LOAD" PROVE Spec => []ReservedReleasedOnlyIfIssued
<1>1. Init => ReservedReleasedOnlyIfIssued
    BY DEF Init, ReservedReleasedOnlyIfIssued
<1>2. Loaded /\ ReservedReleasedOnlyIfIssued /\ [Next]_vars => ReservedReleasedOnlyIfIssued'
    BY ReleasedNext
<1>3. Spec => []Loaded
    BY LoadedAlways
<1> QED
    BY <1>1, <1>2, <1>3, PTL DEF Spec

THEOREM ResultLabelCoversInputsAlways == ASSUME Mut # "M_JOIN" PROVE Spec => []ResultLabelCoversInputs
<1>1. Init => ResultLabelCoversInputs
    BY DEF Init, ResultLabelCoversInputs
<1>2. ResultLabelCoversInputs /\ [Next]_vars => ResultLabelCoversInputs'
    BY CoversInputsNext
<1> QED
    BY <1>1, <1>2, PTL DEF Spec

THEOREM SuppressedNeverInGuestAlways == ASSUME Mut # "M_DELIVER" PROVE Spec => []SuppressedNeverInGuest
<1>1. Init => SuppressedNeverInGuest
    BY DEF Init, SuppressedNeverInGuest
<1>2. (TypeOK /\ IdsUsed /\ GuestIn) /\ SuppressedNeverInGuest /\ [Next]_vars => SuppressedNeverInGuest'
    BY SuppressedNext
<1> QED
    BY <1>1, <1>2, BaseAlways, PTL DEF Spec

THEOREM ClearSetCoversGuestAlways ==
    ASSUME Mut \notin {"M_RESET", "M_DELIVER"} PROVE Spec => []ClearSetCoversGuest
<1>1. Init => ClearSetCoversGuest
    BY DEF Init, ClearSetCoversGuest
<1>2. (TypeOK /\ IdsUsed /\ GuestIn) /\ ClearSetCoversGuest /\ [Next]_vars => ClearSetCoversGuest'
    BY CoverNext
<1> QED
    BY <1>1, <1>2, BaseAlways, PTL DEF Spec

THEOREM ClearSetOnlyGrowsAlways == ASSUME Mut # "M_RESET" PROVE Spec => ClearSetOnlyGrows
<1>1. [Next]_vars => (clearSet \subseteq clearSet')
    BY GrowsStep
<1>2. [Next]_vars => [clearSet \subseteq clearSet']_vars
    BY <1>1
<1> QED
    BY <1>2, PTL DEF Spec, ClearSetOnlyGrows

THEOREM LabelsCoverTruthAlways == ASSUME Honest PROVE Spec => []LabelsCoverTruth
<1>0. Mut # "M_LOAD" /\ Mut # "M_RESET" /\ Mut \notin {"M_RESET", "M_DELIVER"}
    BY DEF Honest
<1>1. Init => LabelsCoverTruth
    BY DEF Init, LabelsCoverTruth
<1>2. (TypeOK /\ IdsUsed /\ GuestIn) /\ Loaded /\ TaskIn /\ ClearSetCoversGuest /\ LabelsCoverTruth /\ [Next]_vars
        => LabelsCoverTruth'
    BY TruthNext
<1>3. Spec => []Loaded
    BY <1>0, LoadedAlways
<1>4. Spec => []TaskIn
    BY <1>0, TaskAlways
<1>5. Spec => []ClearSetCoversGuest
    BY <1>0, ClearSetCoversGuestAlways
<1> QED
    BY <1>1, <1>2, <1>3, <1>4, <1>5, BaseAlways, PTL DEF Spec

THEOREM NoReadThenSendAlways == ASSUME Honest, Mut # "M_F1" PROVE Spec => []NoReadThenSend
<1>0. Mut # "M_RESET" /\ Mut \notin {"M_RESET", "M_DELIVER"}
    BY DEF Honest
<1>1. Init => NoReadThenSend
    BY DEF Init, NoReadThenSend
<1>2. TaskIn /\ ClearSetCoversGuest /\ LabelsCoverTruth /\ NoReadThenSend /\ [Next]_vars => NoReadThenSend'
    BY ReadSendNext
<1>3. Spec => []TaskIn
    BY <1>0, TaskAlways
<1>4. Spec => []ClearSetCoversGuest
    BY <1>0, ClearSetCoversGuestAlways
<1>5. Spec => []LabelsCoverTruth
    BY LabelsCoverTruthAlways
<1> QED
    BY <1>1, <1>2, <1>3, <1>4, <1>5, PTL DEF Spec

THEOREM NoSteeredDestinationAlways ==
    ASSUME Honest, Mut \notin {"M_F2", "M_F3"} PROVE Spec => []NoSteeredDestination
<1>0. Mut # "M_RESET" /\ Mut \notin {"M_RESET", "M_DELIVER"}
    BY DEF Honest
<1>1. Init => NoSteeredDestination
    BY DEF Init, NoSteeredDestination
<1>2. TaskIn /\ ClearSetCoversGuest /\ LabelsCoverTruth /\ NoSteeredDestination /\ [Next]_vars
        => NoSteeredDestination'
    BY SteeredNext
<1>3. Spec => []TaskIn
    BY <1>0, TaskAlways
<1>4. Spec => []ClearSetCoversGuest
    BY <1>0, ClearSetCoversGuestAlways
<1>5. Spec => []LabelsCoverTruth
    BY LabelsCoverTruthAlways
<1> QED
    BY <1>1, <1>2, <1>3, <1>4, <1>5, PTL DEF Spec

THEOREM SafeAlways == ASSUME Mut = "none" PROVE Spec => []Safe
<1>0. /\ Honest /\ Mut # "M_LOAD" /\ Mut # "M_JOIN" /\ Mut # "M_DELIVER" /\ Mut # "M_F1"
      /\ Mut \notin {"M_RESET", "M_DELIVER"} /\ Mut \notin {"M_F2", "M_F3"}
    BY DEF Honest
<1>1. Spec => []NoUnlabelledDelivery
    BY <1>0, NoUnlabelledDeliveryAlways
<1>2. Spec => []SuppressedNeverInGuest
    BY <1>0, SuppressedNeverInGuestAlways
<1>3. Spec => []ClearSetCoversGuest
    BY <1>0, ClearSetCoversGuestAlways
<1>4. Spec => []ResultLabelCoversInputs
    BY <1>0, ResultLabelCoversInputsAlways
<1>5. Spec => []LabelsCoverTruth
    BY <1>0, LabelsCoverTruthAlways
<1>6. Spec => []OutsideResultIsUntrusted
    BY <1>0, OutsideResultIsUntrustedAlways
<1>7. Spec => []ReservedReleasedOnlyIfIssued
    BY <1>0, ReservedReleasedOnlyIfIssuedAlways
<1>8. Spec => []NoReadThenSend
    BY <1>0, NoReadThenSendAlways
<1>9. Spec => []NoSteeredDestination
    BY <1>0, NoSteeredDestinationAlways
<1> QED
    BY <1>1, <1>2, <1>3, <1>4, <1>5, <1>6, <1>7, <1>8, <1>9, PTL DEF Safe, FloorMinimumHolds

-----------------------------------------------------------------------------
(* What each mutation admits: the guard it removes. Their counterexamples are    *)
(* TLC's (Labels-results).                                                       *)

LEMMA MutForbidsOff ==
    /\ Mut = "M_F1" => \A t \in Tools : \A d, b : ~F1(t, d, b)
    /\ Mut = "M_F2" => \A t \in Tools : \A d : ~F2(t, d)
    /\ Mut = "M_F3" => \A t \in Tools : \A d : ~F3(t, d)
BY DEF F1, F2, F3

LEMMA MutJoinDropsHandles == Mut = "M_JOIN" => \A d, b : JoinH(d, b) = {}
BY DEF JoinH

LEMMA MutLiteralDropsClearSet == Mut = "M_LITERAL" => \A d, b : JoinL(d, b) = {}
BY DEF JoinL

LEMMA MutLoadLoadsAnything == Mut = "M_LOAD" => WellFormed
BY DEF WellFormed
=============================================================================
