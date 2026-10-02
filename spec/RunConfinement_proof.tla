------------------------- MODULE RunConfinement_proof -------------------------
(* TLAPS proofs of the two invariants RunConfinement.tla states (ADR-0034 A2,    *)
(* pending: P4 for Run is channel fidelity):                                     *)
(*                                                                               *)
(*   THEOREM EffectsOnDeclaredChannelsAlways  == Spec => []EffectsOnDeclaredChannels *)
(*       (Mut \notin {"M_CHANNEL", "M_NATIVE"} and ~(Mut = "M_FILTER" /\ Filtered)) *)
(*   THEOREM ContainedEffectsUseHeldToolsAlways == Spec => []ContainedEffectsUseHeldTools *)
(*       (Mut # "M_NATIVE")                                                      *)
(*   THEOREM SafeAlways == Spec => []Safe   (Mut = "none")                       *)
(*                                                                               *)
(* Each theorem takes as hypothesis only the mutations that break it, as the     *)
(* TLC rows found (RunConfinement-results-2026.10.02.txt): M_CHANNEL breaks the   *)
(* first and not the second; M_NATIVE both; M_FILTER the first, and only where   *)
(* D-0034-5 is declared, which is why its hypothesis carries `Filtered`. Both    *)
(* invariants are inductive on their own: a new effect's target follows from the *)
(* mechanism's check and the runtime's reach, and nothing else changes effects.  *)
(* The one assumption is that `Filtered` is a Boolean, which every run supplies. *)
(*                                                                               *)
(* RunConfinement.tla is not edited; this module extends it. The mutations and   *)
(* the five witnesses stay with TLC; the lemmas at the end say what each         *)
(* mutation admits.                                                              *)
(*                                                                               *)
(* Check with:  ../tools/tlapm RunConfinement_proof.tla   (from spec/; see       *)
(*              proof-results.sh for the results file)                           *)
EXTENDS RunConfinement, TLAPS

ASSUME FilteredBool == Filtered \in BOOLEAN

LEMMA KindValues == Kind["w"] = "wasm" /\ Kind["f"] = "filtered" /\ Kind["n"] = "native"
BY DEF Kind, Tools

LEMMA ToolCases == \A t \in Tools : t = "w" \/ t = "f" \/ t = "n"
BY DEF Tools

(* What a held tool can reach, when nothing that breaks the target is in force. *)
LEMMA HeldReachesDeclared ==
    ASSUME Mut # "M_CHANNEL", ~(Mut = "M_FILTER" /\ Filtered), NEW t \in Tools, Held(t)
    PROVE  Reach(t) = {Declared[t]}
<1>1. CASE t = "w"
    BY <1>1, KindValues DEF Reach
<1>2. CASE t = "f"
    <2>1. Filtered
        BY <1>2, KindValues, FilteredBool DEF Held
    <2>2. Mut # "M_FILTER"
        BY <2>1
    <2> QED
        BY <1>2, <2>2, KindValues DEF Reach
<1>3. CASE t = "n"
    BY <1>3, KindValues DEF Held
<1> QED
    BY <1>1, <1>2, <1>3, ToolCases

(* The mechanism's check, read for a contained lease: only a held tool passes.  *)
LEMMA ContainedHeld ==
    ASSUME Mut # "M_NATIVE", NEW p \in Principals, NEW t \in Tools, Fidelity(p, t), Contained(p)
    PROVE  Held(t)
BY DEF Fidelity, Contained

(* An Actuate either refuses, leaving effects, or adds one effect, at a target the *)
(* tool host lets the tool open, marked with the lease's containment.            *)
LEMMA ActuateEffect ==
    ASSUME NEW p \in Principals, NEW t \in Tools, Actuate(p, t)
    PROVE  \/ effects' = effects
           \/ /\ Fidelity(p, t)
              /\ \E tgt \in Reach(t) :
                   effects' = effects \cup {[contained |-> Contained(p), tool |-> t, target |-> tgt]}
BY DEF Actuate

-----------------------------------------------------------------------------
LEMMA NextDeclared ==
    ASSUME Mut \notin {"M_CHANNEL", "M_NATIVE"}, ~(Mut = "M_FILTER" /\ Filtered),
           EffectsOnDeclaredChannels, [Next]_vars
    PROVE  EffectsOnDeclaredChannels'
<1>1. CASE UNCHANGED vars
    BY <1>1 DEF vars, EffectsOnDeclaredChannels
<1>2. ASSUME NEW p \in Principals, Grant(p) PROVE EffectsOnDeclaredChannels'
    BY <1>2 DEF Grant, EffectsOnDeclaredChannels
<1>3. ASSUME NEW p \in Principals, EndRound(p) PROVE EffectsOnDeclaredChannels'
    BY <1>3 DEF EndRound, EffectsOnDeclaredChannels
<1>4. ASSUME NEW p \in Principals, NEW t \in Tools, Actuate(p, t) PROVE EffectsOnDeclaredChannels'
    <2>1. CASE effects' = effects
        BY <2>1 DEF EffectsOnDeclaredChannels
    <2>2. CASE /\ Fidelity(p, t)
               /\ \E tgt \in Reach(t) :
                    effects' = effects \cup {[contained |-> Contained(p), tool |-> t, target |-> tgt]}
        <3>1. PICK tgt \in Reach(t) :
                effects' = effects \cup {[contained |-> Contained(p), tool |-> t, target |-> tgt]}
            BY <2>2
        <3>2. Contained(p) => tgt = Declared[t]
            <4> SUFFICES ASSUME Contained(p) PROVE tgt = Declared[t]
                OBVIOUS
            <4>1. Held(t)
                BY <2>2, ContainedHeld
            <4>2. Reach(t) = {Declared[t]}
                BY <4>1, HeldReachesDeclared
            <4> QED
                BY <3>1, <4>2
        <3> QED
            BY <3>1, <3>2 DEF EffectsOnDeclaredChannels
    <2> QED
        BY <1>4, <2>1, <2>2, ActuateEffect
<1> QED
    BY <1>1, <1>2, <1>3, <1>4 DEF Next

LEMMA NextHeld ==
    ASSUME Mut # "M_NATIVE", ContainedEffectsUseHeldTools, [Next]_vars
    PROVE  ContainedEffectsUseHeldTools'
<1>1. CASE UNCHANGED vars
    BY <1>1 DEF vars, ContainedEffectsUseHeldTools
<1>2. ASSUME NEW p \in Principals, Grant(p) PROVE ContainedEffectsUseHeldTools'
    BY <1>2 DEF Grant, ContainedEffectsUseHeldTools
<1>3. ASSUME NEW p \in Principals, EndRound(p) PROVE ContainedEffectsUseHeldTools'
    BY <1>3 DEF EndRound, ContainedEffectsUseHeldTools
<1>4. ASSUME NEW p \in Principals, NEW t \in Tools, Actuate(p, t) PROVE ContainedEffectsUseHeldTools'
    <2>1. CASE effects' = effects
        BY <2>1 DEF ContainedEffectsUseHeldTools
    <2>2. CASE /\ Fidelity(p, t)
               /\ \E tgt \in Reach(t) :
                    effects' = effects \cup {[contained |-> Contained(p), tool |-> t, target |-> tgt]}
        <3>1. PICK tgt \in Reach(t) :
                effects' = effects \cup {[contained |-> Contained(p), tool |-> t, target |-> tgt]}
            BY <2>2
        <3>2. Contained(p) => Held(t)
            BY <2>2, ContainedHeld
        <3> QED
            BY <3>1, <3>2 DEF ContainedEffectsUseHeldTools
    <2> QED
        BY <1>4, <2>1, <2>2, ActuateEffect
<1> QED
    BY <1>1, <1>2, <1>3, <1>4 DEF Next

LEMMA InitBoth == Init => EffectsOnDeclaredChannels /\ ContainedEffectsUseHeldTools
BY DEF Init, EffectsOnDeclaredChannels, ContainedEffectsUseHeldTools

THEOREM EffectsOnDeclaredChannelsAlways ==
    ASSUME Mut \notin {"M_CHANNEL", "M_NATIVE"}, ~(Mut = "M_FILTER" /\ Filtered)
    PROVE  Spec => []EffectsOnDeclaredChannels
<1>1. EffectsOnDeclaredChannels /\ [Next]_vars => EffectsOnDeclaredChannels'
    BY NextDeclared
<1>2. Init => EffectsOnDeclaredChannels
    BY InitBoth
<1> QED
    BY <1>1, <1>2, PTL DEF Spec

THEOREM ContainedEffectsUseHeldToolsAlways ==
    ASSUME Mut # "M_NATIVE"
    PROVE  Spec => []ContainedEffectsUseHeldTools
<1>1. ContainedEffectsUseHeldTools /\ [Next]_vars => ContainedEffectsUseHeldTools'
    BY NextHeld
<1>2. Init => ContainedEffectsUseHeldTools
    BY InitBoth
<1> QED
    BY <1>1, <1>2, PTL DEF Spec

THEOREM SafeAlways ==
    ASSUME Mut = "none"
    PROVE  Spec => []Safe
<1>1. Spec => []EffectsOnDeclaredChannels
    BY EffectsOnDeclaredChannelsAlways
<1>2. Spec => []ContainedEffectsUseHeldTools
    BY ContainedEffectsUseHeldToolsAlways
<1> QED
    BY <1>1, <1>2, PTL DEF Safe

-----------------------------------------------------------------------------
(* What each mutation admits: the guard it removes. Their counterexamples are    *)
(* TLC's (RunConfinement-results-2026.10.02.txt, rows ch, nat, nath, fil).        *)

LEMMA MutChannelReachesAll == Mut = "M_CHANNEL" => Reach("w") = Targets
BY KindValues DEF Reach

LEMMA MutNativeAdmitsAll == Mut = "M_NATIVE" => \A p \in Principals, t \in Tools : Fidelity(p, t)
BY DEF Fidelity

LEMMA MutFilterReachesAll == Mut = "M_FILTER" => Reach("f") = Targets
BY KindValues DEF Reach

LEMMA NativeIsNeverHeld == ~Held("n")
BY KindValues DEF Held
=============================================================================
