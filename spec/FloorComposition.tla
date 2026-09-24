--------------------------- MODULE FloorComposition ---------------------------
(* Properties for ADR-0030 §1, §3 and §4: monotone composition of a verified    *)
(* floor with an unverified bundle.                                            *)
(*                                                                             *)
(*   AdmitImpliesFloorPermit      §1  no admit without a clean floor permit     *)
(*   FloorErrorIsDeny             §1  a floor evaluation error is a deny        *)
(*   BundleRefusalHonored         §1  bundle deny/error/undefined/absent denies *)
(*   BundleCannotWriteFloorInputs §3  the floor reads only what the lift wrote  *)
(*   EnvelopeHolds                    every admit lies inside the envelope the  *)
(*                                    floor's analysis proves over schema S     *)
(*                                                                             *)
(* The floor is a small Cedar-shaped policy set evaluated with Cedar's rules:   *)
(* any satisfied forbid denies; else any satisfied permit allows; else deny. A  *)
(* policy whose condition reads a missing attribute errors and is SKIPPED, so a *)
(* forbid that errors does not fire. That is the hazard §1 closes.              *)
(*                                                                             *)
(*   P1  permit Read                                                            *)
(*   P2  permit Draft when resource.owner == principal                          *)
(*   P3  permit Emit  when resource.owner == principal                          *)
(*   F1  forbid Emit  when resource.sealed                                      *)
(*                                                                             *)
(* The bundle is havoc: at every decision it may return any outcome. That       *)
(* quantifies over every bundle at once, including stale and hostile ones.      *)
(*                                                                             *)
(* The lift writes the floor's store and a ghost copy (`truth`). The slice      *)
(* handed to the engine may drop an attribute - a fault §4 forbids, modeled     *)
(* here because §1 must hold even when §4 is violated.                          *)
(*                                                                             *)
(* Mut = "none":        the mechanism as ADR-0030 specifies it.                 *)
(* Mut = "M_OVERRIDE":  permit-override - a bundle allow grants on its own.     *)
(* Mut = "M_ERR":       the mechanism takes the engine decision, ignoring errors*)
(* Mut = "M_FAILOPEN":  bundle error/undefined/absent/unreachable is not a deny *)
(* Mut = "M_WRITE":     the bundle tier has a write path to the floor's store   *)
EXTENDS FiniteSets

CONSTANTS Mut

Seats   == {"s1", "s2"}
Targets == {"t1", "t2"}
Acts    == {"Read", "Draft", "Emit"}
NONE    == "none"                          \* a missing attribute
\* `sealed` is "yes" or "no" as stored; NONE only in a slice that dropped it.

BundleOutcomes == {"allow", "deny", "error", "undefined", "absent", "unreachable"}

VARIABLES truth,        \* ghost: what the lift wrote, per target
          fstore,       \* what the floor reads, per target
          admitNoFloor, \* flags: an admit violated the named property
          admitWithErr,
          admitNoBundle,
          admitOutside,
          sawAdmit,     \* witnesses
          sawNarrow,
          sawFloorErr
vars == <<truth, fstore, admitNoFloor, admitWithErr, admitNoBundle, admitOutside,
          sawAdmit, sawNarrow, sawFloorErr>>

Rec(o, s) == [owner |-> o, sealed |-> s]

Init == /\ truth  = [t \in Targets |-> Rec(IF t = "t1" THEN "s1" ELSE "s2", "no")]
        /\ fstore = truth
        /\ admitNoFloor = FALSE /\ admitWithErr = FALSE
        /\ admitNoBundle = FALSE /\ admitOutside = FALSE
        /\ sawAdmit = FALSE /\ sawNarrow = FALSE /\ sawFloorErr = FALSE

Flags == <<admitNoFloor, admitWithErr, admitNoBundle, admitOutside, sawAdmit, sawNarrow, sawFloorErr>>

\* --- the lift: the only legitimate writer of floor inputs -------------------
Reassign(t, s) ==
  /\ truth'  = [truth  EXCEPT ![t].owner = s]
  /\ fstore' = [fstore EXCEPT ![t].owner = s]
  /\ UNCHANGED Flags

Seal(t) ==
  /\ truth[t].sealed = "no"
  /\ truth'  = [truth  EXCEPT ![t].sealed = "yes"]
  /\ fstore' = [fstore EXCEPT ![t].sealed = "yes"]
  /\ UNCHANGED Flags

\* --- M_WRITE: a bundle writes a floor input the lift did not ---------------
BundleWrite(t, s) ==
  /\ Mut = "M_WRITE"
  /\ fstore' = [fstore EXCEPT ![t].owner = s]
  /\ UNCHANGED <<truth>> /\ UNCHANGED Flags

\* --- Cedar-shaped evaluation ------------------------------------------------
\* Each policy yields "T", "F", or "ERR" against the slice `e` for resource r.
OwnerIs(e, p) == IF e.owner = NONE THEN "ERR" ELSE IF e.owner = p THEN "T" ELSE "F"
SealedIs(e)   == IF e.sealed = NONE THEN "ERR" ELSE IF e.sealed = "yes" THEN "T" ELSE "F"

Permits(e, p, a) ==
  { IF a = "Read"  THEN "T" ELSE "F",
    IF a = "Draft" THEN OwnerIs(e, p) ELSE "F",
    IF a = "Emit"  THEN OwnerIs(e, p) ELSE "F" }
Forbids(e, a) == { IF a = "Emit" THEN SealedIs(e) ELSE "F" }

EngineAllow(e, p, a) == ("T" \notin Forbids(e, a)) /\ ("T" \in Permits(e, p, a))
EngineErr(e, p, a)   == ("ERR" \in Forbids(e, a)) \/ ("ERR" \in Permits(e, p, a))

\* §1. The mechanism's floor_permit: Allow with no evaluation errors.
FloorPermit(e, p, a) ==
  IF Mut = "M_ERR" THEN EngineAllow(e, p, a)
                   ELSE EngineAllow(e, p, a) /\ ~EngineErr(e, p, a)

\* §1. bundle_deny: anything but an affirmative "allow".
BundleDeny(b) == IF Mut = "M_FAILOPEN" THEN b = "deny" ELSE b # "allow"

Admit(e, p, a, b) ==
  IF Mut = "M_OVERRIDE" THEN FloorPermit(e, p, a) \/ b = "allow"
                        ELSE FloorPermit(e, p, a) /\ ~BundleDeny(b)

\* The envelope the floor's analysis proves over complete, schema-conforming
\* stores written by the lift - stated against `truth`, not the slice.
Envelope(p, a, r) ==
  \/ a = "Read"
  \/ a = "Draft" /\ truth[r].owner = p
  \/ a = "Emit"  /\ truth[r].owner = p /\ truth[r].sealed = "no"

\* A decision. `drop` models an incomplete slice (a §4 fault).
Decide(p, a, r) ==
  \E b \in BundleOutcomes, drop \in {"no", "owner", "sealed"} :
    LET e0 == fstore[r]
        e  == CASE drop = "owner"  -> [e0 EXCEPT !.owner = NONE]
                [] drop = "sealed" -> [e0 EXCEPT !.sealed = NONE]
                [] OTHER           -> e0
        ok == Admit(e, p, a, b)
    IN /\ admitNoFloor'  = (admitNoFloor  \/ (ok /\ ~(EngineAllow(e, p, a) /\ ~EngineErr(e, p, a))))
       /\ admitWithErr'  = (admitWithErr  \/ (ok /\ EngineErr(e, p, a)))
       /\ admitNoBundle' = (admitNoBundle \/ (ok /\ b # "allow"))
       /\ admitOutside'  = (admitOutside  \/ (ok /\ ~Envelope(p, a, r)))
       /\ sawAdmit'      = (sawAdmit \/ ok)
       /\ sawNarrow'     = (sawNarrow \/ (FloorPermit(e, p, a) /\ ~ok))
       /\ sawFloorErr'   = (sawFloorErr \/ EngineErr(e, p, a))
       /\ UNCHANGED <<truth, fstore>>

Next ==
  \/ \E t \in Targets, s \in Seats : Reassign(t, s) \/ BundleWrite(t, s)
  \/ \E t \in Targets : Seal(t)
  \/ \E p \in Seats, a \in Acts, r \in Targets : Decide(p, a, r)
Spec == Init /\ [][Next]_vars

\* --- the properties ---------------------------------------------------------
AdmitImpliesFloorPermit      == ~admitNoFloor
FloorErrorIsDeny             == ~admitWithErr
BundleRefusalHonored         == ~admitNoBundle
BundleCannotWriteFloorInputs == fstore = truth
EnvelopeHolds                == ~admitOutside

Safe == AdmitImpliesFloorPermit /\ FloorErrorIsDeny /\ BundleRefusalHonored
        /\ BundleCannotWriteFloorInputs /\ EnvelopeHolds

\* --- reachability witnesses: each must be VIOLATED --------------------------
NeverAdmitted  == ~sawAdmit
\* The one ADR-0030 names: a bundle refuses something the floor permits.
\* Without it AdmitImpliesFloorPermit could hold because the tiers never disagree.
NeverNarrowed  == ~sawNarrow
NeverFloorError == ~sawFloorErr
=============================================================================
