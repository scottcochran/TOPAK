------------------------ MODULE RulesFloorNV_rev5_proof ------------------------
(* TLAPS proofs of the six properties RulesFloorNV_rev5.tla states (ADR-0026     *)
(* R1, R2, R5, R7, R9; ADR-0024 revision 5), each under the floor entry or       *)
(* mechanism setting it rests on:                                                *)
(*                                                                               *)
(*   THEOREM P1Always == Spec => []P1_Unanimity          ("R1" \in Active)       *)
(*   THEOREM P2Always == Spec => []P2_TwoSeatsCounted    ("R2" \in Active)       *)
(*   THEOREM P3Always == Spec => []P3_AuthorNotCounted   (Mech # "norecuse")     *)
(*   THEOREM P5Always == Spec => []P5_AnchorNotApprover  ("R5" \in Active)       *)
(*   THEOREM P7Always == Spec => []P7_BGNoAuthority      ("R7" \in Active)       *)
(*   THEOREM P9Always == Spec => []P9_NoSoloGrant                                *)
(*                        ("R2" \in Active /\ ("R1" \in Active \/ "R9" \in Active)) *)
(*   THEOREM SafeAlways == Spec => []Safe   (AllEntries \subseteq Active, Mech # "norecuse") *)
(*                                                                               *)
(* The P9 hypothesis is the premise table's "binds only with R1 relaxed" made    *)
(* exact: under unanimity (R1) the approvers are the counted seats, and R2 makes *)
(* those at least two; under a threshold, R9 makes the threshold at least two.   *)
(* Either way R2 is needed, since R9 says nothing when the mode is "all".        *)
(*                                                                               *)
(* The module also states, as unnamed ASSUMEs, that the genesis rules satisfy    *)
(* the floor and that every entry is independently droppable. TLC evaluates     *)
(* those; here they are theorems (GenesisEntries, EntriesIndependent,            *)
(* R9IndependentUnderThreshold), each with an explicit witness.                  *)
(*                                                                               *)
(* PromotionEnabled already states the cardinalities the properties compare, so  *)
(* the proofs carry them as terms; one FiniteSetTheorems fact, that the          *)
(* approvers' cardinality is a natural, is needed to chain two inequalities.     *)
(*                                                                               *)
(* RulesFloorNV_rev5.tla is cited by digest in ADR-0026 and ADR-0033 and is not  *)
(* edited; this module extends it. The dropped-entry rows and the witness stay   *)
(* with TLC (RulesFloorNV-rev5-results-2026.09.23.txt).                          *)
(*                                                                               *)
(* Check with:  ../tools/tlapm RulesFloorNV_rev5_proof.tla   (from spec/; see    *)
(*              proof-results.sh for the results file)                           *)
EXTENDS RulesFloorNV_rev5, FiniteSetTheorems, TLAPS

(* The floor in force names only entries the floor defines (Entry is a CASE      *)
(* with no OTHER arm); the run script supplies Active per row.                   *)
ASSUME ActiveEntries == Active \subseteq AllEntries

-----------------------------------------------------------------------------
(* The module's three ASSUMEs, as theorems.                                      *)

LEMMA GenesisEntries == \A e \in AllEntries : Entry(e, Genesis)
BY DEF AllEntries, Entry, Genesis, Humans, Author, AnchorKeys, AuthActs

LEMMA GenesisRules == Genesis \in RuleSpace
BY DEF Genesis, RuleSpace, QVals, Humans, Author, AnchorKeys, BGActs

LEMMA EntriesIndependent ==
    \A e \in AllEntries \ {"R9"} :
      \E r \in RuleSpace : ~Entry(e, r) /\ \A f \in AllEntries \ {e} : Entry(f, r)
<1>1. \E r \in RuleSpace : ~Entry("R1", r) /\ \A f \in AllEntries \ {"R1"} : Entry(f, r)
    <2> DEFINE w == [grant |-> Humans \ ({Author} \cup AnchorKeys), quorum |-> [mode |-> "k", k |-> 2],
                 minGrant |-> 2, bgScope |-> {"Op"}]
    <2>1. w \in RuleSpace
        BY DEF RuleSpace, QVals, Humans, Author, AnchorKeys, BGActs
    <2>2. ~Entry("R1", w) /\ \A f \in AllEntries \ {"R1"} : Entry(f, w)
        BY DEF Entry, AllEntries, Humans, Author, AnchorKeys, AuthActs, BGActs
    <2> QED
        BY <2>1, <2>2
<1>2. \E r \in RuleSpace : ~Entry("R2", r) /\ \A f \in AllEntries \ {"R2"} : Entry(f, r)
    <2> DEFINE w == [grant |-> Humans \ ({Author} \cup AnchorKeys), quorum |-> [mode |-> "all", k |-> 0],
                 minGrant |-> 1, bgScope |-> {"Op"}]
    <2>1. w \in RuleSpace
        BY DEF RuleSpace, QVals, Humans, Author, AnchorKeys, BGActs
    <2>2. ~Entry("R2", w) /\ \A f \in AllEntries \ {"R2"} : Entry(f, w)
        BY DEF Entry, AllEntries, Humans, Author, AnchorKeys, AuthActs, BGActs
    <2> QED
        BY <2>1, <2>2
<1>3. \E r \in RuleSpace : ~Entry("R5", r) /\ \A f \in AllEntries \ {"R5"} : Entry(f, r)
    <2> DEFINE w == [grant |-> Humans, quorum |-> [mode |-> "all", k |-> 0],
                 minGrant |-> 2, bgScope |-> {"Op"}]
    <2>1. w \in RuleSpace
        BY DEF RuleSpace, QVals, Humans, Author, AnchorKeys, BGActs
    <2>2. ~Entry("R5", w) /\ \A f \in AllEntries \ {"R5"} : Entry(f, w)
        BY DEF Entry, AllEntries, Humans, Author, AnchorKeys, AuthActs, BGActs
    <2> QED
        BY <2>1, <2>2
<1>4. \E r \in RuleSpace : ~Entry("R7", r) /\ \A f \in AllEntries \ {"R7"} : Entry(f, r)
    <2> DEFINE w == [grant |-> Humans \ ({Author} \cup AnchorKeys), quorum |-> [mode |-> "all", k |-> 0],
                 minGrant |-> 2, bgScope |-> {"Issue", "Op"}]
    <2>1. w \in RuleSpace
        BY DEF RuleSpace, QVals, Humans, Author, AnchorKeys, BGActs
    <2>2. ~Entry("R7", w) /\ \A f \in AllEntries \ {"R7"} : Entry(f, w)
        BY DEF Entry, AllEntries, Humans, Author, AnchorKeys, AuthActs, BGActs
    <2> QED
        BY <2>1, <2>2
<1> QED
    BY <1>1, <1>2, <1>3, <1>4 DEF AllEntries

LEMMA R9IndependentUnderThreshold ==
    \E r \in RuleSpace : ~Entry("R9", r) /\ \A f \in AllEntries \ {"R1", "R9"} : Entry(f, r)
<1> DEFINE w == [grant |-> Humans \ ({Author} \cup AnchorKeys), quorum |-> [mode |-> "k", k |-> 1],
                 minGrant |-> 2, bgScope |-> {"Op"}]
<1>1. w \in RuleSpace
    BY DEF RuleSpace, QVals, Humans, Author, AnchorKeys, BGActs
<1>2. ~Entry("R9", w) /\ \A f \in AllEntries \ {"R1", "R9"} : Entry(f, w)
    BY DEF Entry, AllEntries, Humans, Author, AnchorKeys, AuthActs, BGActs
<1> QED
    BY <1>1, <1>2

-----------------------------------------------------------------------------
(* The base invariant: the issued rules are in the rule space and satisfy the    *)
(* floor. It holds under every setting.                                          *)

Base == rules \in RuleSpace /\ Floor(rules)

LEMMA InitBase == Init => Base
BY GenesisEntries, GenesisRules, ActiveEntries DEF Init, Base, Floor

LEMMA NextBase == Base /\ [Next]_vars => Base'
<1> SUFFICES ASSUME Base, [Next]_vars PROVE Base' OBVIOUS
<1>1. CASE UNCHANGED vars
    BY <1>1 DEF Base, Floor, Entry, vars
<1>2. CASE Issue
    <2>1. PICK r \in RuleSpace : Floor(r) /\ rules' = r
        BY <1>2 DEF Issue
    <2> QED
        BY <2>1 DEF Base, Floor, Entry
<1>3. CASE Promote
    BY <1>3 DEF Promote, Base, Floor, Entry
<1>4. CASE BreakGlass
    BY <1>4 DEF BreakGlass, Base, Floor, Entry
<1>5. ASSUME NEW h \in Humans, Vote(h) PROVE Base'
    BY <1>5 DEF Vote, Base, Floor, Entry
<1> QED
    BY <1>1, <1>2, <1>3, <1>4, <1>5 DEF Next

(* An entry in force constrains the issued rules.                               *)
LEMMA InForce ==
    ASSUME Base, NEW e \in Active
    PROVE  Entry(e, rules)
BY DEF Base, Floor

-----------------------------------------------------------------------------
(* The promotion properties. Every step either leaves the promotion triple       *)
(* alone or is Promote; after a promotion nothing changes the triple again,      *)
(* since Issue and Vote need ~promoted. So each property is established at       *)
(* Promote and frozen.                                                           *)

LEMMA Steps ==
    ASSUME [Next]_vars
    PROVE  UNCHANGED <<promoted, approvers, seats>> \/ Promote
BY DEF Next, Issue, BreakGlass, Vote, vars

LEMMA PromoteSets ==
    ASSUME Promote
    PROVE  /\ ~promoted /\ promoted' = TRUE
           /\ approvers' = Recorded /\ seats' = Counted
           /\ Cardinality(Counted) >= rules.minGrant
           /\ IF rules.quorum.mode = "all" THEN Recorded = Counted
                                          ELSE Cardinality(Recorded) >= rules.quorum.k
BY DEF Promote, PromotionEnabled

LEMMA RecordedWithin == Recorded \subseteq Counted /\ Counted \subseteq rules.grant
BY DEF Recorded, Counted

LEMMA HumansFinite == IsFiniteSet(Humans)
BY FS_EmptySet, FS_AddElement DEF Humans

LEMMA RecordedCardinality ==
    ASSUME Base
    PROVE  Cardinality(Recorded) \in Nat
<1>1. Recorded \subseteq Humans
    BY RecordedWithin DEF Base, RuleSpace
<1> QED
    BY <1>1, HumansFinite, FS_Subset, FS_CardinalityType

LEMMA NextP1 ==
    ASSUME "R1" \in Active, Base, P1_Unanimity, [Next]_vars
    PROVE  P1_Unanimity'
<1>1. CASE UNCHANGED <<promoted, approvers, seats>>
    BY <1>1 DEF P1_Unanimity
<1>2. CASE Promote
    <2>1. rules.quorum.mode = "all"
        BY InForce DEF Entry
    <2> QED
        BY <1>2, <2>1, PromoteSets DEF P1_Unanimity
<1> QED
    BY Steps, <1>1, <1>2

LEMMA NextP2 ==
    ASSUME "R2" \in Active, Base, P2_TwoSeatsCounted, [Next]_vars
    PROVE  P2_TwoSeatsCounted'
<1>1. CASE UNCHANGED <<promoted, approvers, seats>>
    BY <1>1 DEF P2_TwoSeatsCounted
<1>2. CASE Promote
    <2>1. rules.minGrant >= 2 /\ rules.minGrant \in 0..2
        BY InForce DEF Entry, Base, RuleSpace
    <2> QED
        BY <1>2, <2>1, PromoteSets DEF P2_TwoSeatsCounted
<1> QED
    BY Steps, <1>1, <1>2

LEMMA NextP3 ==
    ASSUME Mech # "norecuse", Base, P3_AuthorNotCounted, [Next]_vars
    PROVE  P3_AuthorNotCounted'
<1>1. CASE UNCHANGED <<promoted, approvers, seats>>
    BY <1>1 DEF P3_AuthorNotCounted
<1>2. CASE Promote
    <2>1. Author \notin Counted
        BY DEF Counted
    <2> QED
        BY <1>2, <2>1, PromoteSets, RecordedWithin DEF P3_AuthorNotCounted
<1> QED
    BY Steps, <1>1, <1>2

LEMMA NextP5 ==
    ASSUME "R5" \in Active, Base, P5_AnchorNotApprover, [Next]_vars
    PROVE  P5_AnchorNotApprover'
<1>1. CASE UNCHANGED <<promoted, approvers, seats>>
    BY <1>1 DEF P5_AnchorNotApprover
<1>2. CASE Promote
    <2>1. rules.grant \cap AnchorKeys = {}
        BY InForce DEF Entry
    <2> QED
        BY <1>2, <2>1, PromoteSets, RecordedWithin DEF P5_AnchorNotApprover
<1> QED
    BY Steps, <1>1, <1>2

LEMMA NextP9 ==
    ASSUME "R2" \in Active, "R1" \in Active \/ "R9" \in Active,
           Base, P9_NoSoloGrant, [Next]_vars
    PROVE  P9_NoSoloGrant'
<1>1. CASE UNCHANGED <<promoted, approvers, seats>>
    BY <1>1 DEF P9_NoSoloGrant
<1>2. CASE Promote
    <2>1. rules.minGrant >= 2 /\ rules.minGrant \in 0..2 /\ rules.quorum \in QVals
        BY InForce DEF Entry, Base, RuleSpace
    <2>2. CASE rules.quorum.mode = "all"
        BY <1>2, <2>1, <2>2, PromoteSets DEF P9_NoSoloGrant
    <2>3. CASE rules.quorum.mode # "all"
        <3>1. "R9" \in Active
            BY <2>3, InForce DEF Entry
        <3>2. rules.quorum.k >= 2
            BY <2>3, <3>1, InForce DEF Entry
        <3>3. Cardinality(Recorded) >= rules.quorum.k
            BY <1>2, <2>3, PromoteSets
        <3>4. rules.quorum.k \in 0..4
            BY <2>1 DEF QVals
        <3>5. Cardinality(approvers') >= 2
            BY <1>2, <3>2, <3>3, <3>4, PromoteSets, RecordedCardinality
        <3> QED
            BY <1>2, <3>5, PromoteSets DEF P9_NoSoloGrant
    <2> QED
        BY <2>2, <2>3
<1> QED
    BY Steps, <1>1, <1>2

-----------------------------------------------------------------------------
(* P7, the break-glass property, is the same proof as BreakGlass_proof: R7       *)
(* keeps the envelope away from the authority actions.                           *)

LEMMA NextP7 ==
    ASSUME "R7" \in Active, Base, P7_BGNoAuthority, [Next]_vars
    PROVE  P7_BGNoAuthority'
<1>1. CASE UNCHANGED vars
    BY <1>1 DEF P7_BGNoAuthority, vars
<1>2. CASE Issue
    BY <1>2 DEF Issue, P7_BGNoAuthority
<1>3. CASE Promote
    BY <1>3 DEF Promote, P7_BGNoAuthority
<1>4. CASE BreakGlass
    <2>1. PICK x \in rules.bgScope : bgDid' = bgDid \cup {x}
        BY <1>4 DEF BreakGlass
    <2>2. rules.bgScope \cap AuthActs = {}
        BY InForce DEF Entry
    <2> QED
        BY <2>1, <2>2 DEF P7_BGNoAuthority
<1>5. ASSUME NEW h \in Humans, Vote(h) PROVE P7_BGNoAuthority'
    BY <1>5 DEF Vote, P7_BGNoAuthority
<1> QED
    BY <1>1, <1>2, <1>3, <1>4, <1>5 DEF Next

-----------------------------------------------------------------------------
LEMMA InitAll == Init => Base /\ Safe
BY InitBase DEF Init, Safe, P1_Unanimity, P2_TwoSeatsCounted, P3_AuthorNotCounted,
                P5_AnchorNotApprover, P7_BGNoAuthority, P9_NoSoloGrant

THEOREM P1Always ==
    ASSUME "R1" \in Active
    PROVE  Spec => []P1_Unanimity
<1>1. (Base /\ P1_Unanimity) /\ [Next]_vars => (Base /\ P1_Unanimity)'
    BY NextBase, NextP1
<1>2. Init => Base /\ P1_Unanimity
    BY InitAll DEF Safe
<1> QED
    BY <1>1, <1>2, PTL DEF Spec

THEOREM P2Always ==
    ASSUME "R2" \in Active
    PROVE  Spec => []P2_TwoSeatsCounted
<1>1. (Base /\ P2_TwoSeatsCounted) /\ [Next]_vars => (Base /\ P2_TwoSeatsCounted)'
    BY NextBase, NextP2
<1>2. Init => Base /\ P2_TwoSeatsCounted
    BY InitAll DEF Safe
<1> QED
    BY <1>1, <1>2, PTL DEF Spec

THEOREM P3Always ==
    ASSUME Mech # "norecuse"
    PROVE  Spec => []P3_AuthorNotCounted
<1>1. (Base /\ P3_AuthorNotCounted) /\ [Next]_vars => (Base /\ P3_AuthorNotCounted)'
    BY NextBase, NextP3
<1>2. Init => Base /\ P3_AuthorNotCounted
    BY InitAll DEF Safe
<1> QED
    BY <1>1, <1>2, PTL DEF Spec

THEOREM P5Always ==
    ASSUME "R5" \in Active
    PROVE  Spec => []P5_AnchorNotApprover
<1>1. (Base /\ P5_AnchorNotApprover) /\ [Next]_vars => (Base /\ P5_AnchorNotApprover)'
    BY NextBase, NextP5
<1>2. Init => Base /\ P5_AnchorNotApprover
    BY InitAll DEF Safe
<1> QED
    BY <1>1, <1>2, PTL DEF Spec

THEOREM P7Always ==
    ASSUME "R7" \in Active
    PROVE  Spec => []P7_BGNoAuthority
<1>1. (Base /\ P7_BGNoAuthority) /\ [Next]_vars => (Base /\ P7_BGNoAuthority)'
    BY NextBase, NextP7
<1>2. Init => Base /\ P7_BGNoAuthority
    BY InitAll DEF Safe
<1> QED
    BY <1>1, <1>2, PTL DEF Spec

THEOREM P9Always ==
    ASSUME "R2" \in Active, "R1" \in Active \/ "R9" \in Active
    PROVE  Spec => []P9_NoSoloGrant
<1>1. (Base /\ P9_NoSoloGrant) /\ [Next]_vars => (Base /\ P9_NoSoloGrant)'
    BY NextBase, NextP9
<1>2. Init => Base /\ P9_NoSoloGrant
    BY InitAll DEF Safe
<1> QED
    BY <1>1, <1>2, PTL DEF Spec

THEOREM SafeAlways ==
    ASSUME AllEntries \subseteq Active, Mech # "norecuse"
    PROVE  Spec => []Safe
<1>0. "R1" \in Active /\ "R2" \in Active /\ "R5" \in Active /\ "R7" \in Active /\ "R9" \in Active
    BY DEF AllEntries
<1>1. Spec => []P1_Unanimity
    BY <1>0, P1Always
<1>2. Spec => []P2_TwoSeatsCounted
    BY <1>0, P2Always
<1>3. Spec => []P3_AuthorNotCounted
    BY P3Always
<1>5. Spec => []P5_AnchorNotApprover
    BY <1>0, P5Always
<1>7. Spec => []P7_BGNoAuthority
    BY <1>0, P7Always
<1>9. Spec => []P9_NoSoloGrant
    BY <1>0, P9Always
<1> QED
    BY <1>1, <1>2, <1>3, <1>5, <1>7, <1>9, PTL DEF Safe

-----------------------------------------------------------------------------
(* Why the dropped-entry rows must fail: with an entry out of force the floor    *)
(* admits a rule that violates it (EntriesIndependent, above), and the           *)
(* properties above rest on exactly that entry. The one mechanism mutation       *)
(* counts the author. The counterexamples are TLC's.                             *)
LEMMA MutNoRecuseCountsAuthor ==
    ASSUME Mech = "norecuse"
    PROVE  Counted = rules.grant
BY DEF Counted

=============================================================================
