--------------------------- MODULE NonComposition_A1 ---------------------------
(* Successor to NonComposition.tla (ADR-0013 §4: NC-1 and NC-2), owed by         *)
(* ADR-0052 §9 where that module models X1. NonComposition.tla is cited by      *)
(* digest in ADR-0013 and is not edited.                                        *)
(*                                                                              *)
(* Erasure (ADR-0006) composed with break-glass, against the forensic floor     *)
(* (ADR-0028 §1-§2), with break-glass as ADR-0052 (Proposed) has it: an         *)
(* emergency seating. The roster's quorum activates it for one round; the       *)
(* activation is the forensic record (class F5, ADR-0052 §5); the lease ends    *)
(* with its round and another round is another activation, with its own record. *)
(* The predecessor had one break-glass invocation that stayed active for ever,  *)
(* which is X1's scope: an approval good until the epoch ends.                  *)
(*                                                                              *)
(* Mut = "none": the mechanism as the records specify it.                       *)
(* Mut = "M1":   mutation for NC-1. F1 admit decisions are dropped from the     *)
(*               erasure envelope's denials, so the authority trail is          *)
(*               erasable. NC-1 must fail.                                      *)
(* Mut = "M2":   mutation for NC-2. A live emergency lease widens the erasure   *)
(*               envelope to every class, rather than leaving it alone.         *)
(*               NC-2 must fail.                                                *)
(* Mut = "M3":   new with the seating. An activation's record is kept only      *)
(*               while its round is live: once the round ends it is erasable.   *)
(*               Both must fail. Under X1 there was no "after" to lose it in.   *)
(*                                                                              *)
(* The properties are the predecessor's, restated for a record per activation:  *)
(* a mutation changes the mechanism, never the property.                        *)
EXTENDS FiniteSets, Naturals

CONSTANTS Mut, MaxRound

Effects == {"e1", "e2"}
Rounds  == 1..MaxRound

\* The ADR-0028 classes this model carries. F1 admit decisions, F5 activations
\* of an emergency seating, F6 erasure events. F2, F3 and F4 have the same shape
\* as F5 here and are omitted to keep the state space small.
ForensicKinds == {"F1", "F5", "F6"}

AdmitRec(e)  == [kind |-> "F1", eff |-> e, round |-> 0]
PayRec(e)    == [kind |-> "payload", eff |-> e, round |-> 0]
ActRecord(r) == [kind |-> "F5", eff |-> "em", round |-> r]
EraseRecord  == [kind |-> "F6", eff |-> "em", round |-> 0]

\* live: the round of the emergency seat's live lease, 0 when it holds none.
\* via:  the pairs <<e, r>>: effect e was admitted under the activation of round r.
VARIABLES admitted, via, live, last, created, retained
vars == <<admitted, via, live, last, created, retained>>

Init == /\ admitted = {} /\ via = {} /\ live = 0 /\ last = 0
        /\ created = {} /\ retained = {}

\* The erasure envelope. ADR-0028 §2 makes each forensic class a policy-floor
\* denial on the erasure action, and bundles may only narrow further, so no
\* grant - an emergency seat's lease included - widens it.
Erasable(r) ==
  CASE Mut = "M1" -> r.kind \notin (ForensicKinds \ {"F1"})
    [] Mut = "M2" -> IF live # 0 THEN TRUE ELSE r.kind \notin ForensicKinds
    [] Mut = "M3" -> \/ r.kind \notin ForensicKinds
                     \/ r.kind = "F5" /\ r.round # live
    [] OTHER      -> r.kind \notin ForensicKinds

\* The roster's quorum activates the seating for one round, and the activation
\* is recorded (class F5). Round numbers are never reused (ADR-0031 §2).
Activate == /\ live = 0
            /\ last < MaxRound
            /\ live' = last + 1
            /\ last' = last + 1
            /\ created'  = created \cup {ActRecord(last + 1)}
            /\ retained' = retained \cup {ActRecord(last + 1)}
            /\ UNCHANGED <<admitted, via>>

\* The round ends, and the lease with it (ADR-0052 §3). Its record does not.
EndRound == /\ live # 0
            /\ live' = 0
            /\ UNCHANGED <<admitted, via, last, created, retained>>

\* An effect is admitted. The admit decision (F1) and the payload are recorded.
\* Admitted from the emergency seat, the effect is authorized under the
\* activation of the round it was made in.
Admit(e) == /\ e \notin admitted
            /\ admitted' = admitted \cup {e}
            /\ via'      = IF live # 0 THEN via \cup {<<e, live>>} ELSE via
            /\ created'  = created  \cup {AdmitRec(e), PayRec(e)}
            /\ retained' = retained \cup {AdmitRec(e), PayRec(e)}
            /\ UNCHANGED <<live, last>>

\* An erasure demand removes whatever the envelope admits, and is itself
\* recorded (class F6) the first time it happens.
Erase == /\ \E S \in SUBSET retained :
              /\ S # {}
              /\ \A r \in S : Erasable(r)
              /\ created'  = created \cup {EraseRecord}
              /\ retained' = IF EraseRecord \in created
                             THEN retained \ S
                             ELSE (retained \ S) \cup {EraseRecord}
         /\ UNCHANGED <<admitted, via, live, last>>

Next == Activate \/ EndRound \/ Erase \/ \E e \in Effects : Admit(e)
Spec == Init /\ [][Next]_vars

\* An effect is attributable while its admit decision survives, and - if it was
\* authorized under an activation - while that activation's record survives too.
Attributable(e) == /\ AdmitRec(e) \in retained
                   /\ \A r \in Rounds : <<e, r>> \in via => ActRecord(r) \in retained

\* NC-1. Break-glass chained with erasure never yields an effect that is
\* authorized, erased, and unattributable.
NC1 == \A e \in admitted : (PayRec(e) \notin retained) => Attributable(e)

\* NC-2. Erasure never removes a record in a forensic-floor data class, under
\* any composition with break-glass.
NC2 == \A r \in created : r.kind \in ForensicKinds => r \in retained

Safe == NC1 /\ NC2

\* Reachability witnesses. Each must be VIOLATED, or the properties above hold
\* vacuously.
NeverErased     == \A r \in created : r \in retained
NeverEmEffect   == via = {}
\* The composition NC-1 is about: an effect authorized under an activation whose
\* payload is then erased.
NeverEmErased   == \A p \in via : PayRec(p[1]) \in retained
\* The case the seating adds: that erasure after the round has ended.
NeverErasedAfterRound == \A p \in via : PayRec(p[1]) \notin retained => p[2] = live
\* And a second activation, with a record of its own.
NeverSecondActivation == last < 2
=============================================================================
