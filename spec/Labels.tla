------------------------------ MODULE Labels ------------------------------
(* Labels on Run's ingress: ADR-0047 (Proposed), its ratification condition    *)
(* (§11). The Listener labels each item it delivers by the item's source,      *)
(* delivers it clear or as a handle, and the floor refuses three outward calls *)
(* by the labels the mechanism has computed (F1 to F3; ADR-0041 A1's R5 to R7).*)
(*                                                                             *)
(* The mechanism sees labels. This module also carries what the labels are     *)
(* about, as ghost state the mechanism never reads:                            *)
(*   tainted   the item's bytes could have been written from outside           *)
(*   secret    the item's bytes must not leave the deployment                  *)
(* and states the floor's minimum over the ghost state, so that a label rule   *)
(* that is satisfied by the mechanism's own bookkeeping and wrong about the    *)
(* world is a counterexample and not a pass.                                   *)
(*                                                                             *)
(*   NoUnlabelledDelivery      every delivered item has a declared label       *)
(*   SuppressedNeverInGuest    the bytes of an item the table suppresses are   *)
(*                             not in the guest                                *)
(*   ClearSetCoversGuest       clearSet holds every label read in the clear    *)
(*   ClearSetOnlyGrows         (a step property) clearSet never shrinks        *)
(*   ResultLabelCoversInputs   a result's label holds its handle inputs'       *)
(*                             labels, less what its entry releases            *)
(*   LabelsCoverTruth          tainted => `untrusted` in the label; secret =>  *)
(*                             `restricted` in the label                       *)
(*   OutsideResultIsUntrusted  F4: an outward tool's result carries            *)
(*                             `untrusted`                                     *)
(*   ReservedReleasedOnlyIfIssued  F5: a reserved name is released only by an  *)
(*                             entry the issued rules name                     *)
(*   NoReadThenSend            F1, over the truth: no outward call by a        *)
(*                             Thinker that has read tainted bytes carries a   *)
(*                             secret out                                      *)
(*   NoSteeredDestination      F2 and F3, over the truth: no outward call's    *)
(*                             destination is tainted                          *)
(*   FloorMinimumHolds         the last two                                    *)
(*                             (ADR-0047 §11 names this one)                   *)
(*                                                                             *)
(* Four tools, one of each kind the rules distinguish:                         *)
(*   fetch   outward; a body input; returns outside content                    *)
(*   send    outward; a destination input and a body input                     *)
(*   vault   inside; no input; returns a secret; declared `restricted`         *)
(*   echo    inside; a body input; returns what it was given. It may be        *)
(*           declared to release `restricted` (a redactor)                     *)
(* An input is a literal or a handle. A literal may carry anything the Thinker *)
(* has read in the clear, which is what "havoc" means here.                    *)
(*                                                                             *)
(* What the bundle and the grant choose is chosen at Init, every way the load  *)
(* checks allow: the task's label, fetch's declared label (or none), the names *)
(* the delivery table suppresses, whether echo releases `restricted`, and      *)
(* whether the issued rules name echo.                                         *)
(*                                                                             *)
(* Declared premises, not modelled: vault and the Run root are declared        *)
(* truthfully (ADR-0045 A1's T-0045-33: a wrong declaration of a source that   *)
(* is not outward is seen by nothing); an issued releasing entry really does   *)
(* remove the secret; the task's label is true. One principal, one round: a    *)
(* handle names an item of the same round (ADR-0049 §3). `accepts` is not      *)
(* modelled: every input accepts every label, the widest case.                 *)
(*                                                                             *)
(* Mut = "none":       ADR-0047 as revised at R10.                             *)
(* Mut = "M_LITERAL":  a result's label does not take clearSet when an input   *)
(*                     is a literal: ADR-0047 as written before R10. Must      *)
(*                     break LabelsCoverTruth and NoSteeredDestination.        *)
(* Mut = "M_JOIN":     a result's label does not take its handle inputs'       *)
(*                     labels. Must break ResultLabelCoversInputs,             *)
(*                     LabelsCoverTruth and FloorMinimumHolds.                 *)
(* Mut = "M_LOAD":     the load checks F4 to F6 are dropped. Must break        *)
(*                     NoUnlabelledDelivery, OutsideResultIsUntrusted,         *)
(*                     ReservedReleasedOnlyIfIssued, LabelsCoverTruth and      *)
(*                     FloorMinimumHolds.                                      *)
(* Mut = "M_RESET":    a clear delivery replaces clearSet. Must break          *)
(*                     ClearSetOnlyGrows, ClearSetCoversGuest,                 *)
(*                     LabelsCoverTruth and FloorMinimumHolds.                 *)
(* Mut = "M_DELIVER":  the Listener sends the bytes of a suppressed item. Must *)
(*                     break SuppressedNeverInGuest, ClearSetCoversGuest,      *)
(*                     LabelsCoverTruth and FloorMinimumHolds.                 *)
(* The LabelsCoverTruth rows under M_LOAD, M_RESET and M_DELIVER, and          *)
(* ClearSetCoversGuest under M_DELIVER, were found writing the proof           *)
(* (Labels_proof.tla) and are in the results file from 2026.10.04 on.          *)
(* Mut = "M_F1", "M_F2", "M_F3": that forbid is dropped. M_F1 must break       *)
(*                     NoReadThenSend; M_F2 and M_F3 NoSteeredDestination.     *)
EXTENDS Integers, FiniteSets

CONSTANTS Mut, MaxSeq

U == "untrusted"
R == "restricted"
Names == {U, R}

Tools    == {"fetch", "send", "vault", "echo"}
Outward  == [t \in Tools |-> t \in {"fetch", "send"}]
HasDest  == [t \in Tools |-> t = "send"]
HasBody  == [t \in Tools |-> t \in {"fetch", "send", "echo"}]

\* An input is absent, a literal, or a handle: the id of an item of this round.
None == -1
Lit  == 0
Doc  == MaxSeq + 1            \* the one object in the Run root; results are 1..MaxSeq
Ids  == 1..(MaxSeq + 1)

VARIABLES
  taskLabel,       \* the grant's label for the task
  fetchDeclared,   \* whether the bundle declares a label for fetch at all
  fetchLabel,      \* the label it declares
  suppress,        \* the names whose delivery mode is `handle`
  echoReleases,    \* the names echo's entry releases
  issued,          \* whether the issued rules name echo as a releasing entry
  items,           \* what has been admitted and recorded, by id
  guest,           \* ids whose bytes entered the guest (ghost)
  clearSet,        \* the mechanism's fold
  seq,
  effects,         \* admitted outward calls, with the truth about each (ghost)
  refused          \* which forbids have fired

bundle == <<taskLabel, fetchDeclared, fetchLabel, suppress, echoReleases, issued>>
vars   == <<taskLabel, fetchDeclared, fetchLabel, suppress, echoReleases, issued,
            items, guest, clearSet, seq, effects, refused>>

\* F4 to F6 (ADR-0049 §6, W6 to W8), as far as these four entries exercise them.
WellFormed ==
  \/ Mut = "M_LOAD"
  \/ /\ fetchDeclared                           \* F6: no entry without a label
     /\ U \in fetchLabel                        \* F4: an outward entry carries `untrusted`
     /\ (echoReleases # {} => issued)           \* F5: a reserved name released only if issued

Init ==
  /\ taskLabel \in SUBSET Names
  /\ fetchDeclared \in BOOLEAN
  /\ fetchLabel \in SUBSET Names
  /\ suppress \in SUBSET Names
  /\ echoReleases \in {{}, {R}}
  /\ issued \in BOOLEAN
  /\ (~fetchDeclared => fetchLabel = {})
  /\ WellFormed
  /\ items = {}
  /\ guest = {}
  /\ clearSet = taskLabel                       \* the task is always delivered clear
  /\ seq = 0
  /\ effects = {}
  /\ refused = {}

Item(i)   == CHOOSE x \in items : x.id = i
Exists(i) == \E x \in items : x.id = i

\* The declared label of a tool's result, and what its entry releases.
Decl(t) == CASE t = "fetch" -> fetchLabel
             [] t = "send"  -> {U}
             [] t = "vault" -> {R}
             [] t = "echo"  -> {}
Releases(t) == IF t = "echo" THEN echoReleases ELSE {}

\* What the Thinker has really read (ghost). The task is as its label says.
ThinkerTainted == U \in taskLabel \/ \E x \in items : x.id \in guest /\ x.tainted
ThinkerSecret  == R \in taskLabel \/ \E x \in items : x.id \in guest /\ x.secret

IsHandle(a) == a \in Ids
InLabel(a)  == IF IsHandle(a) THEN Item(a).label ELSE {}
InTaint(a)  == IF IsHandle(a) THEN Item(a).tainted ELSE a = Lit /\ ThinkerTainted
InSecret(a) == IF IsHandle(a) THEN Item(a).secret ELSE a = Lit /\ ThinkerSecret

\* Delivery of a new item with label l: what enters the guest and the fold.
Clear(l) == l \cap suppress = {}
Deliver(i, l) ==
  /\ guest' = IF Clear(l) \/ Mut = "M_DELIVER" THEN guest \cup {i} ELSE guest
  /\ clearSet' = IF Clear(l)
                   THEN (IF Mut = "M_RESET" THEN l ELSE clearSet \cup l)
                   ELSE clearSet

\* `Consult` of the one object in the Run root: declared with no name, and clean.
Consult ==
  /\ ~Exists(Doc)
  /\ items' = items \cup {[id |-> Doc, tool |-> "root", label |-> {}, labelled |-> TRUE,
                           mode |-> IF Clear({}) THEN "clear" ELSE "handle",
                           rawIn |-> {}, tainted |-> FALSE, secret |-> FALSE]}
  /\ Deliver(Doc, {})
  /\ UNCHANGED <<bundle, seq, effects, refused>>

\* `Actuate` of tool t with destination d and body b.
Actuate(t, d, b) ==
  /\ seq < MaxSeq
  /\ d \in (IF HasDest[t] THEN {Lit} \cup {i \in Ids : Exists(i)} ELSE {None})
  /\ b \in (IF HasBody[t] THEN {Lit} \cup {i \in Ids : Exists(i)} ELSE {None})
  /\ LET inL == InLabel(d) \cup InLabel(b)
         f1  == Mut # "M_F1" /\ Outward[t] /\ U \in clearSet /\ (R \in clearSet \/ R \in inL)
         f2  == Mut # "M_F2" /\ Outward[t] /\ U \in clearSet /\ d = Lit
         f3  == Mut # "M_F3" /\ Outward[t] /\ IsHandle(d) /\ U \in Item(d).label
         fired == (IF f1 THEN {"F1"} ELSE {}) \cup (IF f2 THEN {"F2"} ELSE {})
                    \cup (IF f3 THEN {"F3"} ELSE {})
         \* ADR-0047 §1: the entry's label, joined with the handle inputs' labels and,
         \* where an input is a literal, with clearSet (R10); less what the entry releases.
         joinH == IF Mut = "M_JOIN" THEN {} ELSE inL
         joinL == IF (d = Lit \/ b = Lit) /\ Mut # "M_LITERAL" THEN clearSet ELSE {}
         l     == (Decl(t) \cup joinH \cup joinL) \ Releases(t)
         i     == seq + 1
         honestRelease == Releases(t) # {} /\ issued
     IN IF fired # {}
          THEN /\ refused' = refused \cup fired
               /\ UNCHANGED <<bundle, items, guest, clearSet, seq, effects>>
          ELSE /\ items' = items \cup
                    {[id |-> i, tool |-> t, label |-> l,
                      labelled |-> (t # "fetch" \/ fetchDeclared),
                      mode |-> IF Clear(l) THEN "clear" ELSE "handle",
                      rawIn |-> inL,
                      tainted |-> Outward[t] \/ InTaint(d) \/ InTaint(b),
                      secret |-> t = "vault" \/ ((InSecret(d) \/ InSecret(b)) /\ ~honestRelease)]}
               /\ Deliver(i, l)
               /\ seq' = i
               /\ effects' = IF Outward[t]
                               THEN effects \cup {[tool |-> t, by |-> ThinkerTainted,
                                                   steered |-> InTaint(d),
                                                   leak |-> InSecret(d) \/ InSecret(b)]}
                               ELSE effects
               /\ UNCHANGED <<bundle, refused>>

Next == \/ Consult
        \/ \E t \in Tools, d \in {None, Lit} \cup Ids, b \in {None, Lit} \cup Ids : Actuate(t, d, b)

Spec == Init /\ [][Next]_vars

\* --- the properties ----------------------------------------------------------

NoUnlabelledDelivery == \A x \in items : x.labelled

SuppressedNeverInGuest == \A x \in items : x.id \in guest => Clear(x.label)

ClearSetCoversGuest == \A x \in items : x.id \in guest => x.label \subseteq clearSet

ClearSetOnlyGrows == [][clearSet \subseteq clearSet']_vars

ResultLabelCoversInputs ==
  \A x \in items : x.tool \in Tools => (x.rawIn \ Releases(x.tool)) \subseteq x.label

LabelsCoverTruth ==
  \A x \in items : (x.tainted => U \in x.label) /\ (x.secret => R \in x.label)

OutsideResultIsUntrusted == \A x \in items : (x.tool \in Tools /\ Outward[x.tool]) => U \in x.label

ReservedReleasedOnlyIfIssued ==
  \A x \in items : (x.tool \in Tools /\ (x.rawIn \cap Releases(x.tool)) # {}) => issued

NoReadThenSend == \A e \in effects : ~(e.by /\ e.leak)

NoSteeredDestination == \A e \in effects : ~e.steered

FloorMinimumHolds == NoReadThenSend /\ NoSteeredDestination

Safe == /\ NoUnlabelledDelivery /\ SuppressedNeverInGuest /\ ClearSetCoversGuest
        /\ ResultLabelCoversInputs /\ LabelsCoverTruth /\ OutsideResultIsUntrusted
        /\ ReservedReleasedOnlyIfIssued /\ FloorMinimumHolds

\* --- reachability witnesses: each must be VIOLATED ---------------------------

\* An outward call is admitted at all: the floor's minimum is not vacuous.
NeverOutwardEffect == effects = {}
\* A Thinker that has read tainted bytes still makes an outward call: the forbids do
\* not simply stop a tainted round.
NeverTaintedOutward == \A e \in effects : ~e.by
\* Each forbid fires.
NeverF1 == "F1" \notin refused
NeverF2 == "F2" \notin refused
NeverF3 == "F3" \notin refused
\* An item is delivered as a handle, and a handle is used as an input.
NeverSuppressed == \A x \in items : x.mode = "clear"
NeverHandleInput == \A x \in items : x.rawIn = {}
\* A secret leaves by an outward call of a Thinker that read nothing tainted: F1 is
\* a rule about injection and not a ban on sending.
NeverCleanLeak == \A e \in effects : ~e.leak
\* An issued releasing entry removes a reserved name.
NeverReleased == \A x \in items : x.tool \in Tools => (x.rawIn \cap Releases(x.tool)) = {}
=============================================================================
