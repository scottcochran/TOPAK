-------------------------- MODULE BreakGlass_proof --------------------------
(* TLAPS proof of the invariant BreakGlass.tla states (ADR-0029 §5 bootstrap   *)
(* module 5 of 5), for every floor subset and epoch bound:                      *)
(*                                                                               *)
(*   THEOREM NeverChangesAuthority ==                                            *)
(*     Spec => []BreakGlassNeverChangesAuthority          (Mut = "none")         *)
(*                                                                               *)
(* BreakGlass.tla is cited by digest in ADR-0029 and is not edited; this        *)
(* module extends it. The mutation M_SCOPE and the witness NeverBreakGlass stay  *)
(* with TLC (bootstrap-results-2026.09.23.txt); MutAdmitsAuthority below says    *)
(* why the mutation must fail.                                                   *)
(*                                                                               *)
(* Check with:  ../tools/tlapm BreakGlass_proof.tla   (from spec/; see           *)
(*              proof-results.sh for the results file)                           *)
EXTENDS BreakGlass, TLAPS

(* BreakGlass.tla leaves Active and Mut unconstrained; bootstrap-run.sh sets     *)
(* them per row. The floor in force names only entries the floor defines (Entry  *)
(* is a CASE with no OTHER arm), and it includes R7: the property is R7's        *)
(* claim, so it is false under any floor that drops R7 (ADR-0026 R7; the         *)
(* theorem-premise-binding row).                                                 *)
ASSUME ActiveEntries == Active \subseteq AllEntries
ASSUME R7InForce     == "R7" \in Active

-----------------------------------------------------------------------------
(* RulesFloorBase states this as an unnamed ASSUME; TLAPS does not use an       *)
(* unnamed module assumption unless cited, so it is proved from the             *)
(* definitions, as in Anchor_proof.                                             *)
LEMMA GenesisEntries == \A e \in AllEntries : Entry(e, Genesis)
BY DEF AllEntries, Entry, Genesis, Humans, Author, AnchorKeys, AuthActs

(* The inductive invariant: the floor holds of the issued rules, and nothing     *)
(* break-glass has done changes authority. The floor is needed because R7 is     *)
(* what keeps the envelope away from the authority actions.                      *)
Inv == Floor(rules) /\ BreakGlassNeverChangesAuthority

LEMMA InitInv == Init => Inv
BY GenesisEntries, ActiveEntries DEF Init, Inv, Floor, BreakGlassNeverChangesAuthority

LEMMA NextInv ==
    ASSUME Mut = "none", Inv, [Next]_vars
    PROVE  Inv'
<1>1. CASE UNCHANGED vars
    BY <1>1 DEF Inv, Floor, BreakGlassNeverChangesAuthority, vars
<1>2. CASE Issue
    <2>1. PICK r \in RuleSpace : Floor(r) /\ rules' = r
        BY <1>2 DEF Issue
    <2> QED
        BY <1>2, <2>1 DEF Issue, Inv, BreakGlassNeverChangesAuthority
<1>3. CASE BreakGlass
    <2>1. PICK x \in BGActs : Admits(x) /\ bgDid' = bgDid \cup {x}
        BY <1>3 DEF BreakGlass
    <2>2. x \in rules.bgScope
        BY <2>1 DEF Admits
    <2>3. rules.bgScope \cap AuthActs = {}
        BY R7InForce DEF Inv, Floor, Entry
    <2>4. (bgDid \cup {x}) \cap AuthActs = {}
        BY <2>2, <2>3 DEF Inv, BreakGlassNeverChangesAuthority
    <2> QED
        BY <1>3, <2>1, <2>4 DEF BreakGlass, Inv, Floor, BreakGlassNeverChangesAuthority
<1> QED
    BY <1>1, <1>2, <1>3 DEF Next

THEOREM NeverChangesAuthority ==
    ASSUME Mut = "none"
    PROVE  Spec => []BreakGlassNeverChangesAuthority
<1>1. Inv /\ [Next]_vars => Inv'
    BY NextInv
<1>2. Inv => BreakGlassNeverChangesAuthority
    BY DEF Inv
<1> QED
    BY InitInv, <1>1, <1>2, PTL DEF Spec

(* Why M_SCOPE must fail: with the envelope ignored, every break-glass action    *)
(* is admitted, and the authority actions are among them. The counterexample     *)
(* itself is TLC's (row bg-mut).                                                 *)
LEMMA MutAdmitsAuthority ==
    ASSUME Mut = "M_SCOPE"
    PROVE  \A x \in AuthActs : x \in BGActs /\ Admits(x)
BY DEF Admits, BGActs

=============================================================================
