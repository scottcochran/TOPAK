---------------------------- MODULE BreakGlass_A1 ----------------------------
(* Successor to BreakGlass.tla (ADR-0029 §5 bootstrap module 5 of 5), owed by   *)
(* ADR-0052 §9 where that module models X1. BreakGlass.tla is cited by digest   *)
(* in ADR-0029 and is not edited.                                               *)
(* Invariant: EmergencyNeverChangesAuthority.                                   *)
(*                                                                              *)
(* ADR-0052 (Proposed) makes break-glass an emergency seating: the roster's     *)
(* quorum seats a person on a seat of kind `emergency` for one round. There is  *)
(* no issued envelope of actions any more. What an emergency lease may do is    *)
(* its alphabet, and its alphabet is its kind's: Consult, Actuate and Report    *)
(* (ADR-0052 §1), here the one ordinary operation "Op".                         *)
(*                                                                              *)
(* ADR-0026 A2 (pending) therefore changes R7's subject. R7 forbade an issued   *)
(* break-glass envelope from naming Issue, Vote or promotion. It is kept, read  *)
(* as "no activation of an emergency seating grants a lease whose alphabet      *)
(* holds an authority act", so that a later change to the kind's alphabet meets *)
(* it. `rules.bgScope` is still in the rule space RulesFloorBase defines and is *)
(* read by nothing here: what the rules carry for break-glass is the roster and *)
(* its quorum, which Emergency.tla models and this module does not.             *)
(*                                                                              *)
(* Two independent guards, as before, because they fail independently:          *)
(*   the floor entry R7, which refuses an activation whose lease would hold an  *)
(*   authority act; and the mechanism, which must confine an emergency seat's   *)
(*   action to its lease's alphabet.                                            *)
(*                                                                              *)
(* Mut = "none":    both guards in force, and the kind's alphabet as decided.   *)
(* Mut = "M_SCOPE": the mechanism ignores the lease's alphabet and admits any   *)
(*                  action from an emergency seat. The invariant must fail.     *)
(* Mut = "M_KIND":  a later change gives the kind an authority act. With R7 in  *)
(*                  Active the activation is refused and the invariant holds:   *)
(*                  that is the reading A2 keeps R7 for. With R7 dropped the    *)
(*                  invariant must fail, which is what makes R7 non-vacuous     *)
(*                  under its new subject (ADR-0026 §6, §7).                    *)
(* Under Mut = "none", dropping R7 changes nothing: the kind's alphabet holds   *)
(* no authority act, so R7 has nothing to refuse. A2 says so, and row a1-nor7   *)
(* shows it.                                                                    *)
EXTENDS RulesFloorBase

CONSTANTS Mut, MaxEpoch, MaxRound

NoLease == [alphabet |-> {}, round |-> 0]

VARIABLES rules, epoch, round, lease, emDid
vars == <<rules, epoch, round, lease, emDid>>

Init == rules = Genesis /\ epoch = 0 /\ round = 0 /\ lease = NoLease /\ emDid = {}

\* The anchor issues rules; the floor bounds every issuance (Anchor module). A
\* new rules epoch ends every live lease, the emergency seat's with them.
Issue ==
  /\ epoch < MaxEpoch
  /\ \E r \in RuleSpace : Floor(r) /\ rules' = r
  /\ epoch' = epoch + 1
  /\ lease' = NoLease
  /\ UNCHANGED <<round, emDid>>

\* The alphabet of the `emergency` kind: a mechanism constant (ADR-0052 §1).
KindAlphabet == IF Mut = "M_KIND" THEN BGActs ELSE {"Op"}

\* R7 under its new subject (ADR-0026 A2): an activation grants no lease whose
\* alphabet holds an authority act.
R7Admits(alphabet) == "R7" \in Active => alphabet \cap AuthActs = {}

\* The roster's quorum activates the seating: one lease, for one round. The
\* quorum itself is Emergency.tla's.
Activate ==
  /\ lease = NoLease
  /\ round < MaxRound
  /\ R7Admits(KindAlphabet)
  /\ round' = round + 1
  /\ lease' = [alphabet |-> KindAlphabet, round |-> round + 1]
  /\ UNCHANGED <<rules, epoch, emDid>>

\* What the mechanism admits from the emergency seat: its lease's alphabet.
Admits(x) == IF Mut = "M_SCOPE" THEN x \in BGActs      \* alphabet ignored
                                ELSE x \in lease.alphabet

Act ==
  /\ lease # NoLease
  /\ \E x \in BGActs : Admits(x) /\ emDid' = emDid \cup {x}
  /\ UNCHANGED <<rules, epoch, round, lease>>

\* The round ends, and the lease with it. There is no successor (ADR-0052 §3).
EndRound ==
  /\ lease # NoLease
  /\ lease' = NoLease
  /\ UNCHANGED <<rules, epoch, round, emDid>>

Next == Issue \/ Activate \/ Act \/ EndRound
Spec == Init /\ [][Next]_vars

\* EmergencyNeverChangesAuthority. Nothing done from an emergency seat is an
\* authority-changing action, under any issuance sequence the floor admits.
EmergencyNeverChangesAuthority == emDid \cap AuthActs = {}

\* Reachability witnesses: each must be VIOLATED, or the invariant holds
\* because no emergency seat ever acts, or because no second quorum ever seats.
NeverEmergencyAct == emDid = {}
NeverSecondRound  == round < 2
=============================================================================
