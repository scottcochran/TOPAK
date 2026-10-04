--------------------------- MODULE ToolList_proof ---------------------------
(* TLAPS proofs of the five invariants ToolList.tla states (ADR-0048, Proposed:  *)
(* a Thinker learns its tools from the mechanism):                               *)
(*                                                                               *)
(*   ToolListIsExactAlways     (Mut \notin {"M_RECOMPUTE", "M_WIDE"})            *)
(*   ToldMatchesDecidedAlways  (Mut \notin {"M_RECOMPUTE", "M_WIDE",             *)
(*                                         "M_DECIDELATEST"})                    *)
(*   ListFixedForRoundAlways   (Mut # "M_RECOMPUTE")                             *)
(*   OpeningRecordFirstAlways  (Mut # "M_LATE")                                  *)
(*   OpenedListIsToldAlways    (Mut # "M_RECOMPUTE")                             *)
(*   SafeAlways == Spec => []Safe   (Mut = "none")                               *)
(*                                                                               *)
(* Each theorem takes as hypothesis only the mutations that break it, as the     *)
(* TLC rows found (ToolList-results-2026.10.04.txt). ToolListIsExact,            *)
(* ListFixedForRound and OpenedListIsTold are inductive as stated.               *)
(* ToldMatchesDecided rests on ToolListIsExact: a call is admitted exactly when  *)
(* its tool is in the lease's allowlist, which is what the Thinker was told.     *)
(* OpeningRecordFirst rests on "a live round's topic is opened".                 *)
(*                                                                               *)
(* The module has no constant but Mut, so nothing is assumed. The two revisions  *)
(* and their allowlists are the module's; the proofs do not use which tools      *)
(* each allows.                                                                  *)
(*                                                                               *)
(* ToolList.tla is not edited; this module extends it. The mutations and the     *)
(* witnesses stay with TLC; the lemmas at the end say what each mutation admits. *)
(*                                                                               *)
(* Check with:  ../tools/tlapm ToolList_proof.tla   (from spec/; see             *)
(*              proof-results.sh and proof-cert.sh for the results files)        *)
EXTENDS ToolList, TLAPS

TypeOK ==
  /\ latest \in Revs
  /\ lease \in [live : BOOLEAN, rev : Revs, narrow : SUBSET Tools]
  /\ opened \in BOOLEAN
  /\ actsBeforeOpen \in BOOLEAN

\* A live round's topic has its opening record.
LiveOpened == lease.live => opened

LEMMA TypeInit == Init => TypeOK
BY DEF Init, TypeOK, Revs, Tools

LEMMA TypeNext == ASSUME TypeOK, [Next]_vars PROVE TypeOK'
<1>1. CASE UNCHANGED vars
    BY <1>1 DEF vars, TypeOK
<1>2. ASSUME NEW n \in SUBSET Tools, Grant(n) PROVE TypeOK'
    BY <1>2 DEF Grant, TypeOK
<1>3. ASSUME NEW r \in Revs, Promote(r) PROVE TypeOK'
    BY <1>3 DEF Promote, TypeOK
<1>4. ASSUME NEW t \in Tools, Call(t) PROVE TypeOK'
    BY <1>4 DEF Call, TypeOK
<1>5. CASE WriteOpen
    BY <1>5 DEF WriteOpen, TypeOK
<1>6. CASE EndRound
    BY <1>6 DEF EndRound, TypeOK
<1> QED
    BY <1>1, <1>2, <1>3, <1>4, <1>5, <1>6 DEF Next

THEOREM TypeAlways == Spec => []TypeOK
<1>1. TypeOK /\ [Next]_vars => TypeOK'
    BY TypeNext
<1> QED
    BY <1>1, TypeInit, PTL DEF Spec

-----------------------------------------------------------------------------
LEMMA ExactNext ==
    ASSUME Mut \notin {"M_RECOMPUTE", "M_WIDE"}, TypeOK, ToolListIsExact, [Next]_vars
    PROVE  ToolListIsExact'
<1> USE DEF ToolListIsExact
<1>1. CASE UNCHANGED vars
    BY <1>1 DEF vars
<1>2. ASSUME NEW n \in SUBSET Tools, Grant(n) PROVE ToolListIsExact'
    BY <1>2 DEF Grant, List, TypeOK
<1>3. ASSUME NEW r \in Revs, Promote(r) PROVE ToolListIsExact'
    BY <1>3 DEF Promote
<1>4. ASSUME NEW t \in Tools, Call(t) PROVE ToolListIsExact'
    BY <1>4 DEF Call
<1>5. CASE WriteOpen
    BY <1>5 DEF WriteOpen
<1>6. CASE EndRound
    BY <1>6 DEF EndRound, TypeOK
<1> QED
    BY <1>1, <1>2, <1>3, <1>4, <1>5, <1>6 DEF Next

LEMMA DecidedNext ==
    ASSUME Mut \notin {"M_RECOMPUTE", "M_WIDE", "M_DECIDELATEST"}, TypeOK, ToolListIsExact,
           ToldMatchesDecided, [Next]_vars
    PROVE  ToldMatchesDecided'
<1> USE DEF ToldMatchesDecided
<1>1. CASE UNCHANGED vars
    BY <1>1 DEF vars
<1>2. ASSUME NEW n \in SUBSET Tools, Grant(n) PROVE ToldMatchesDecided'
    BY <1>2 DEF Grant
<1>3. ASSUME NEW r \in Revs, Promote(r) PROVE ToldMatchesDecided'
    BY <1>3 DEF Promote
<1>4. ASSUME NEW t \in Tools, Call(t) PROVE ToldMatchesDecided'
    <2>1. lease.live /\ told = Allow[lease.rev] \cap lease.narrow
        BY <1>4 DEF Call, ToolListIsExact
    <2>2. DecideRev = lease.rev
        BY DEF DecideRev
    <2>3. CASE t \in Allow[DecideRev] \cap lease.narrow
        <3>1. t \in told
            BY <2>1, <2>2, <2>3
        <3> QED
            BY <1>4, <2>3, <3>1 DEF Call
    <2>4. CASE t \notin Allow[DecideRev] \cap lease.narrow
        <3>1. t \notin told
            BY <2>1, <2>2, <2>4
        <3> QED
            BY <1>4, <2>4, <3>1 DEF Call
    <2> QED
        BY <2>3, <2>4
<1>5. CASE WriteOpen
    BY <1>5 DEF WriteOpen
<1>6. CASE EndRound
    BY <1>6 DEF EndRound
<1> QED
    BY <1>1, <1>2, <1>3, <1>4, <1>5, <1>6 DEF Next

LEMMA FixedNext ==
    ASSUME Mut # "M_RECOMPUTE", TypeOK, ListFixedForRound, [Next]_vars
    PROVE  ListFixedForRound'
<1> USE DEF ListFixedForRound
<1>1. CASE UNCHANGED vars
    BY <1>1 DEF vars
<1>2. ASSUME NEW n \in SUBSET Tools, Grant(n) PROVE ListFixedForRound'
    BY <1>2 DEF Grant
<1>3. ASSUME NEW r \in Revs, Promote(r) PROVE ListFixedForRound'
    BY <1>3 DEF Promote
<1>4. ASSUME NEW t \in Tools, Call(t) PROVE ListFixedForRound'
    BY <1>4 DEF Call
<1>5. CASE WriteOpen
    BY <1>5 DEF WriteOpen
<1>6. CASE EndRound
    BY <1>6 DEF EndRound, TypeOK
<1> QED
    BY <1>1, <1>2, <1>3, <1>4, <1>5, <1>6 DEF Next

LEMMA FirstNext ==
    ASSUME Mut # "M_LATE", TypeOK, LiveOpened /\ OpeningRecordFirst, [Next]_vars
    PROVE  (LiveOpened /\ OpeningRecordFirst)'
<1> USE DEF LiveOpened, OpeningRecordFirst
<1>1. CASE UNCHANGED vars
    BY <1>1 DEF vars
<1>2. ASSUME NEW n \in SUBSET Tools, Grant(n) PROVE (LiveOpened /\ OpeningRecordFirst)'
    BY <1>2 DEF Grant
<1>3. ASSUME NEW r \in Revs, Promote(r) PROVE (LiveOpened /\ OpeningRecordFirst)'
    BY <1>3 DEF Promote
<1>4. ASSUME NEW t \in Tools, Call(t) PROVE (LiveOpened /\ OpeningRecordFirst)'
    BY <1>4 DEF Call, TypeOK
<1>5. CASE WriteOpen
    BY <1>5 DEF WriteOpen
<1>6. CASE EndRound
    BY <1>6 DEF EndRound, TypeOK
<1> QED
    BY <1>1, <1>2, <1>3, <1>4, <1>5, <1>6 DEF Next

LEMMA OpenedNext ==
    ASSUME Mut # "M_RECOMPUTE", TypeOK, OpenedListIsTold, [Next]_vars
    PROVE  OpenedListIsTold'
<1> USE DEF OpenedListIsTold
<1>1. CASE UNCHANGED vars
    BY <1>1 DEF vars
<1>2. ASSUME NEW n \in SUBSET Tools, Grant(n) PROVE OpenedListIsTold'
    BY <1>2 DEF Grant
<1>3. ASSUME NEW r \in Revs, Promote(r) PROVE OpenedListIsTold'
    BY <1>3 DEF Promote
<1>4. ASSUME NEW t \in Tools, Call(t) PROVE OpenedListIsTold'
    BY <1>4 DEF Call
<1>5. CASE WriteOpen
    BY <1>5 DEF WriteOpen
<1>6. CASE EndRound
    BY <1>6 DEF EndRound
<1> QED
    BY <1>1, <1>2, <1>3, <1>4, <1>5, <1>6 DEF Next

-----------------------------------------------------------------------------
THEOREM ToolListIsExactAlways ==
    ASSUME Mut \notin {"M_RECOMPUTE", "M_WIDE"}
    PROVE  Spec => []ToolListIsExact
<1>1. Init => ToolListIsExact
    BY DEF Init, ToolListIsExact
<1>2. TypeOK /\ ToolListIsExact /\ [Next]_vars => ToolListIsExact'
    BY ExactNext
<1>3. Spec => []TypeOK
    BY TypeAlways
<1> QED
    BY <1>1, <1>2, <1>3, PTL DEF Spec

THEOREM ToldMatchesDecidedAlways ==
    ASSUME Mut \notin {"M_RECOMPUTE", "M_WIDE", "M_DECIDELATEST"}
    PROVE  Spec => []ToldMatchesDecided
<1>1. Init => ToldMatchesDecided
    BY DEF Init, ToldMatchesDecided
<1>2. TypeOK /\ ToolListIsExact /\ ToldMatchesDecided /\ [Next]_vars => ToldMatchesDecided'
    BY DecidedNext
<1>3. Spec => []TypeOK
    BY TypeAlways
<1>4. Spec => []ToolListIsExact
    BY ToolListIsExactAlways
<1> QED
    BY <1>1, <1>2, <1>3, <1>4, PTL DEF Spec

THEOREM ListFixedForRoundAlways ==
    ASSUME Mut # "M_RECOMPUTE"
    PROVE  Spec => []ListFixedForRound
<1>1. Init => ListFixedForRound
    BY DEF Init, ListFixedForRound
<1>2. TypeOK /\ ListFixedForRound /\ [Next]_vars => ListFixedForRound'
    BY FixedNext
<1>3. Spec => []TypeOK
    BY TypeAlways
<1> QED
    BY <1>1, <1>2, <1>3, PTL DEF Spec

THEOREM OpeningRecordFirstAlways ==
    ASSUME Mut # "M_LATE"
    PROVE  Spec => []OpeningRecordFirst
<1>1. Init => LiveOpened /\ OpeningRecordFirst
    BY DEF Init, LiveOpened, OpeningRecordFirst
<1>2. TypeOK /\ (LiveOpened /\ OpeningRecordFirst) /\ [Next]_vars => (LiveOpened /\ OpeningRecordFirst)'
    BY FirstNext
<1>3. Spec => []TypeOK
    BY TypeAlways
<1> QED
    BY <1>1, <1>2, <1>3, PTL DEF Spec

THEOREM OpenedListIsToldAlways ==
    ASSUME Mut # "M_RECOMPUTE"
    PROVE  Spec => []OpenedListIsTold
<1>1. Init => OpenedListIsTold
    BY DEF Init, OpenedListIsTold
<1>2. TypeOK /\ OpenedListIsTold /\ [Next]_vars => OpenedListIsTold'
    BY OpenedNext
<1>3. Spec => []TypeOK
    BY TypeAlways
<1> QED
    BY <1>1, <1>2, <1>3, PTL DEF Spec

THEOREM SafeAlways ==
    ASSUME Mut = "none"
    PROVE  Spec => []Safe
<1>1. Spec => []ToolListIsExact
    BY ToolListIsExactAlways
<1>2. Spec => []ToldMatchesDecided
    BY ToldMatchesDecidedAlways
<1>3. Spec => []ListFixedForRound
    BY ListFixedForRoundAlways
<1>4. Spec => []OpeningRecordFirst
    BY OpeningRecordFirstAlways
<1>5. Spec => []OpenedListIsTold
    BY OpenedListIsToldAlways
<1> QED
    BY <1>1, <1>2, <1>3, <1>4, <1>5, PTL DEF Safe

-----------------------------------------------------------------------------
(* What each mutation admits: the guard it removes. Their counterexamples are    *)
(* TLC's (ToolList-results-2026.10.04.txt).                                      *)

LEMMA MutWideIgnoresNarrowing == Mut = "M_WIDE" => \A r \in Revs, n \in SUBSET Tools : List(r, n) = Allow[r]
BY DEF List

LEMMA MutDecideLatestReadsLatest == Mut = "M_DECIDELATEST" => DecideRev = latest
BY DEF DecideRev

LEMMA MutLateGrantsUnopened ==
    ASSUME Mut = "M_LATE", NEW n \in SUBSET Tools, Grant(n)
    PROVE  ~opened'
BY DEF Grant

LEMMA MutRecomputeRedelivers ==
    ASSUME Mut = "M_RECOMPUTE", NEW r \in Revs, Promote(r), lease.live
    PROVE  told' = List(r, lease.narrow)
BY DEF Promote
=============================================================================
