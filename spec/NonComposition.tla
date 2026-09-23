---------------------------- MODULE NonComposition ----------------------------
(* Non-composition properties for ADR-0013 §4: NC-1 and NC-2.                  *)
(* Erasure (ADR-0006) composed with break-glass (ADR-0009), against the        *)
(* forensic floor (ADR-0028 §1-§2).                                            *)
(*                                                                             *)
(* Mut = "none": the mechanism as the records specify it.                      *)
(* Mut = "M1":   mutation for NC-1. F1 admit decisions are dropped from the     *)
(*               erasure envelope's denials, so the authority trail is         *)
(*               erasable. NC-1 must fail.                                     *)
(* Mut = "M2":   mutation for NC-2. A break-glass grant widens the erasure     *)
(*               envelope to every class, rather than only narrowing it.       *)
(*               NC-2 must fail.                                               *)
(*                                                                             *)
(* Discipline follows RulesFloorNV: the properties are fixed and state what     *)
(* the records claim; a mutation changes the mechanism, never the property.     *)
EXTENDS FiniteSets, Naturals

CONSTANT Mut

Effects == {"e1", "e2"}

\* The ADR-0028 classes this model carries. F1 admit decisions, F5 break-glass
\* invocations, F6 erasure events. F2, F3 and F4 have the same shape as F5 here
\* and are omitted to keep the state space small.
ForensicKinds == {"F1", "F5", "F6"}

AdmitRec(e) == [kind |-> "F1", eff |-> e]
PayRec(e)   == [kind |-> "payload", eff |-> e]
BGRecord    == [kind |-> "F5", eff |-> "bg"]
EraseRecord == [kind |-> "F6", eff |-> "bg"]

VARIABLES admitted, viaBG, bgActive, created, retained
vars == <<admitted, viaBG, bgActive, created, retained>>

Init == /\ admitted = {} /\ viaBG = {} /\ bgActive = FALSE
        /\ created = {} /\ retained = {}

\* The erasure envelope. ADR-0028 §2 makes each forensic class a policy-floor
\* denial on the erasure action, and bundles may only narrow further, so no
\* grant - break-glass included - widens it.
Erasable(r) ==
  CASE Mut = "M1" -> r.kind \notin (ForensicKinds \ {"F1"})
    [] Mut = "M2" -> IF bgActive THEN TRUE ELSE r.kind \notin ForensicKinds
    [] OTHER      -> r.kind \notin ForensicKinds

\* Break-glass is invoked, and its invocation is recorded (class F5).
InvokeBG == /\ ~bgActive
            /\ bgActive' = TRUE
            /\ created'  = created \cup {BGRecord}
            /\ retained' = retained \cup {BGRecord}
            /\ UNCHANGED <<admitted, viaBG>>

\* An effect is admitted. The admit decision (F1) and the payload are recorded.
\* Admitted while break-glass is active, the effect is authorized under it.
Admit(e) == /\ e \notin admitted
            /\ admitted' = admitted \cup {e}
            /\ viaBG'    = IF bgActive THEN viaBG \cup {e} ELSE viaBG
            /\ created'  = created  \cup {AdmitRec(e), PayRec(e)}
            /\ retained' = retained \cup {AdmitRec(e), PayRec(e)}
            /\ UNCHANGED bgActive

\* An erasure demand removes whatever the envelope admits, and is itself
\* recorded (class F6) the first time it happens.
Erase == /\ \E S \in SUBSET retained :
              /\ S # {}
              /\ \A r \in S : Erasable(r)
              /\ created'  = created \cup {EraseRecord}
              /\ retained' = IF EraseRecord \in created
                             THEN retained \ S
                             ELSE (retained \ S) \cup {EraseRecord}
         /\ UNCHANGED <<admitted, viaBG, bgActive>>

Next == InvokeBG \/ Erase \/ \E e \in Effects : Admit(e)
Spec == Init /\ [][Next]_vars

\* An effect is attributable while its admit decision survives, and - if it was
\* authorized under break-glass - while that invocation survives too.
Attributable(e) == /\ AdmitRec(e) \in retained
                   /\ (e \in viaBG => BGRecord \in retained)

\* NC-1. Break-glass chained with erasure never yields an effect that is
\* authorized, erased, and unattributable.
NC1 == \A e \in admitted : (PayRec(e) \notin retained) => Attributable(e)

\* NC-2. Erasure never removes a record in a forensic-floor data class, under
\* any composition with break-glass.
NC2 == \A r \in created : r.kind \in ForensicKinds => r \in retained

Safe == NC1 /\ NC2

\* Reachability witnesses. Each must be VIOLATED, or the properties above hold
\* vacuously: nothing is ever erased, or break-glass never authorizes anything.
NeverErased   == \A r \in created : r \in retained
NeverBGEffect == viaBG = {}
\* The composition NC-1 is about: an effect authorized under break-glass whose
\* payload is then erased. Without this witness NC-1 could hold because the two
\* privileged paths never meet.
NeverBGErased == \A e \in viaBG : PayRec(e) \in retained
=============================================================================
