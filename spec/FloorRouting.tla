----------------------------- MODULE FloorRouting -----------------------------
(* Properties for ADR-0030 §5: floor revisions are classified mechanically and   *)
(* routed to the authority ToO §3.2 requires.                                  *)
(*                                                                             *)
(*   NoWideningWithoutIssuance  a floor that permits anything its predecessor  *)
(*                              did not is never deployed without an anchor    *)
(*                              issuance                                       *)
(*   FloorNeverVacuous          the non-vacuity gate: the deployed floor never *)
(*                              permits every request                          *)
(*                                                                             *)
(* A floor is modeled by its meaning: the set of requests it permits, over a   *)
(* small universe U. `F' => F` is `F' \subseteq F`. This checks the routing    *)
(* logic, not the analyzer: it assumes the implies answers are correct, which  *)
(* is exactly the solver-trust assumption ADR-0030 states.                     *)
(*                                                                             *)
(* Proposals are havoc: a Build author, Byzantine by premise, may propose any  *)
(* floor. The anchor may consent to an issuance or refuse it.                  *)
(*                                                                             *)
(* Mut = "none":    routing as ADR-0030 §5 specifies it.                        *)
(* Mut = "M_ROUTE": only a strict superset is treated as a relaxation, so an   *)
(*                  incomparable revision rides an ordinary promotion.         *)
(* Mut = "M_GATE":  the non-vacuity gate is off.                                *)
EXTENDS FiniteSets

CONSTANTS Mut

U       == {"r1", "r2", "r3"}
Genesis == {"r1"}

VARIABLES deployed, wideNoIssue, sawIncomparable, sawRelaxIssued, sawTighten
vars == <<deployed, wideNoIssue, sawIncomparable, sawRelaxIssued, sawTighten>>

Init == /\ deployed = Genesis
        /\ wideNoIssue = FALSE
        /\ sawIncomparable = FALSE /\ sawRelaxIssued = FALSE /\ sawTighten = FALSE

NewImpliesOld(new, old) == new \subseteq old
OldImpliesNew(new, old) == old \subseteq new

Route(new, old) ==
  IF Mut = "M_ROUTE"
    THEN IF OldImpliesNew(new, old) /\ ~NewImpliesOld(new, old) THEN "issue" ELSE "promote"
    ELSE IF NewImpliesOld(new, old) THEN "promote" ELSE "issue"

\* ADR-0030 §5 non-vacuity: not always-allows.
PassesGates(new) == IF Mut = "M_GATE" THEN TRUE ELSE new # U

Incomparable(new, old) == ~NewImpliesOld(new, old) /\ ~OldImpliesNew(new, old)

\* A proposal promoted by quorum alone.
Promote(new) ==
  /\ PassesGates(new)
  /\ Route(new, deployed) = "promote"
  /\ deployed' = new
  /\ wideNoIssue' = (wideNoIssue \/ ~(new \subseteq deployed))
  /\ sawIncomparable' = (sawIncomparable \/ Incomparable(new, deployed))
  /\ sawTighten' = (sawTighten \/ (new \subseteq deployed /\ new # deployed))
  /\ UNCHANGED sawRelaxIssued

\* A proposal the router sends to the anchor, which consents.
IssueAndPromote(new) ==
  /\ PassesGates(new)
  /\ Route(new, deployed) = "issue"
  /\ deployed' = new
  /\ sawIncomparable' = (sawIncomparable \/ Incomparable(new, deployed))
  /\ sawRelaxIssued' = TRUE
  /\ UNCHANGED <<wideNoIssue, sawTighten>>

\* Anchor refusal changes nothing, and is omitted as a stuttering step.

Next == \E new \in SUBSET U : Promote(new) \/ IssueAndPromote(new)
Spec == Init /\ [][Next]_vars

NoWideningWithoutIssuance == ~wideNoIssue
FloorNeverVacuous         == deployed # U
Safe == NoWideningWithoutIssuance /\ FloorNeverVacuous

\* --- reachability witnesses: each must be VIOLATED --------------------------
NeverIncomparable == ~sawIncomparable
NeverRelaxIssued  == ~sawRelaxIssued
NeverTightened    == ~sawTighten
=============================================================================
