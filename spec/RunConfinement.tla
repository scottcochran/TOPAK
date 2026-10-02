------------------------- MODULE RunConfinement -------------------------
(* Channel fidelity for Run: ADR-0034 A2 (pending), P4 for Run, and its         *)
(* ratification condition (ii). A Run tool runs on the mechanism's side of the  *)
(* front door and opens an effect channel. The profile's P4 says each tool is   *)
(* held to the channel its allowlist entry declares (ADR-0040 §3).              *)
(*                                                                              *)
(*   EffectsOnDeclaredChannels   every effect admitted under a Contained Run    *)
(*                               lease reached its tool's declared target       *)
(*   ContainedEffectsUseHeldTools every such effect used a tool that something  *)
(*                               holds to its channel                           *)
(*                                                                              *)
(* What holds a tool to its channel, by kind:                                   *)
(*   wasm      the runtime: the module's one network capability is its declared *)
(*             target (A2 P4; topak-contain wasmtool). A check, by construction *)
(*   filtered  a native tool behind an egress filter in the tool host           *)
(*             (D-0034-5). A trust, held only when the deployment declares it   *)
(*             (`Filtered`)                                                     *)
(*   native    nothing (D-0034-6; ADR-0045 T-0045-24 excluded)                  *)
(*                                                                              *)
(* The mechanism's part is `State::channel_fidelity`: under a lease whose Run   *)
(* profile says P4 passes, an `Actuate` names only a held tool. A profile that  *)
(* says P4 fails claims nothing; its principal is Mediated and may use any tool.*)
(*                                                                              *)
(* Only P4 is modelled. A lease here is attested at its declared rung, its      *)
(* Persona in house and the criterion in force, so `Contained` reduces to the   *)
(* profile's P4; those conjuncts are Confinement_A1.tla's and ADR-0034 §4's.    *)
(* What a tool says on its channel is not modelled: fidelity is about which     *)
(* channel, not what is said on it (A2).                                        *)
(*                                                                              *)
(* Mut = "none":       the mechanism and runtime as A2 specifies them.          *)
(* Mut = "M_CHANNEL":  the Wasm runtime does not bind the target. Must break    *)
(*                     EffectsOnDeclaredChannels.                               *)
(* Mut = "M_NATIVE":   the mechanism's check is dropped: a native tool is       *)
(*                     admitted under a P4-pass lease. Must break both.         *)
(* Mut = "M_FILTER":   the egress filter does not bind. Must break              *)
(*                     EffectsOnDeclaredChannels when D-0034-5 is declared, and *)
(*                     change nothing when it is not.                           *)
EXTENDS FiniteSets

CONSTANTS Mut, Filtered

Principals == {"p1", "p2"}
Tools      == {"w", "f", "n"}
Kind       == [t \in Tools |-> CASE t = "w" -> "wasm" [] t = "f" -> "filtered" [] t = "n" -> "native"]
Targets    == {"a", "b", "c"}
Declared   == [t \in Tools |-> CASE t = "w" -> "a" [] t = "f" -> "b" [] t = "n" -> "c"]

NoLease == [live |-> FALSE, p4 |-> "fail"]

VARIABLES lease, effects, refused
vars == <<lease, effects, refused>>

Init == /\ lease = [p \in Principals |-> NoLease]
        /\ effects = {}
        /\ refused = FALSE

\* What holds a tool to its channel in this deployment.
Held(t) == Kind[t] = "wasm" \/ (Kind[t] = "filtered" /\ Filtered)

\* The targets the tool host lets a tool open.
Reach(t) ==
  CASE Kind[t] = "wasm"     -> IF Mut = "M_CHANNEL" THEN Targets ELSE {Declared[t]}
    [] Kind[t] = "filtered" -> IF Mut = "M_FILTER" THEN Targets ELSE {Declared[t]}
    [] Kind[t] = "native"   -> Targets

\* State::channel_fidelity: a lease whose Run profile says P4 passes names only held tools.
Fidelity(p, t) == Mut = "M_NATIVE" \/ lease[p].p4 # "pass" \/ Held(t)

Contained(p) == lease[p].live /\ lease[p].p4 = "pass"

\* A grant, on a Run profile that says P4 passes or fails.
Grant(p) ==
  /\ ~lease[p].live
  /\ \E v \in {"pass", "fail"} : lease' = [lease EXCEPT ![p] = [live |-> TRUE, p4 |-> v]]
  /\ UNCHANGED <<effects, refused>>

\* An `Actuate` of tool t. Refused at apply if the check fails; otherwise the tool opens a
\* target the tool host lets it, and the effect is recorded with what the lease was.
Actuate(p, t) ==
  /\ lease[p].live
  /\ IF Fidelity(p, t)
       THEN /\ \E tgt \in Reach(t) :
                 effects' = effects \cup {[contained |-> Contained(p), tool |-> t, target |-> tgt]}
            /\ UNCHANGED <<lease, refused>>
       ELSE /\ refused' = TRUE
            /\ UNCHANGED <<lease, effects>>

EndRound(p) ==
  /\ lease[p].live
  /\ lease' = [lease EXCEPT ![p] = NoLease]
  /\ UNCHANGED <<effects, refused>>

Next == \E p \in Principals : Grant(p) \/ EndRound(p) \/ \E t \in Tools : Actuate(p, t)
Spec == Init /\ [][Next]_vars

\* --- the properties ----------------------------------------------------------

EffectsOnDeclaredChannels == \A e \in effects : e.contained => e.target = Declared[e.tool]

ContainedEffectsUseHeldTools == \A e \in effects : e.contained => Held(e.tool)

Safe == EffectsOnDeclaredChannels /\ ContainedEffectsUseHeldTools

\* --- reachability witnesses: each must be VIOLATED ---------------------------

\* A Contained Run principal acts: the property is not vacuous.
NeverContainedEffect   == \A e \in effects : ~e.contained
\* A Mediated Run principal acts too: Contained is not everyone.
NeverMediatedEffect    == \A e \in effects : e.contained
\* The check fires: a native tool under a P4-pass lease is refused.
NeverRefused           == ~refused
\* An undeclared target is reached at all, by a Mediated principal's native tool: the
\* model lets a tool misbehave, so the invariant is not true by the model's construction.
NeverUndeclaredTarget  == \A e \in effects : e.target = Declared[e.tool]
=============================================================================
