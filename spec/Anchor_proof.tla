---------------------------- MODULE Anchor_proof ----------------------------
(* TLAPS proofs of the invariants Anchor.tla states (ADR-0029 §5 bootstrap      *)
(* module 2 of 5), for every value of the constants TLC ran at and beyond:       *)
(*                                                                               *)
(*   THEOREM FloorPreservedAlways == Spec => []FloorPreserved   (Mut = "none")   *)
(*   THEOREM EpochMonotoneAlways  == Spec => []EpochMonotone                     *)
(*                                                                               *)
(* Anchor.tla is cited by digest in ADR-0029 and is not edited; this module      *)
(* extends it. The mutation M_FLOOR and the reachability witness NeverIssued     *)
(* stay with TLC (bootstrap-results-2026.09.23.txt): a counterexample is a       *)
(* behaviour, and TLAPS proves theorems. MutAdmitsAll below says why the         *)
(* mutation must fail.                                                           *)
(*                                                                               *)
(* Check with:  ../tools/tlapm Anchor_proof.tla   (from spec/; see               *)
(*              proof-results.sh for the results file)                           *)
EXTENDS Anchor, TLAPS

(* Anchor.tla leaves Active, MaxEpoch and Mut unconstrained; bootstrap-run.sh    *)
(* sets them per row. The proofs need two of those settings as assumptions:      *)
(* the floor in force names only entries the floor defines (Entry is a CASE      *)
(* with no OTHER arm), and the epoch bound is a natural.                         *)
ASSUME ActiveEntries == Active \subseteq AllEntries
ASSUME MaxEpochNat   == MaxEpoch \in Nat

-----------------------------------------------------------------------------
(* FloorPreserved                                                                *)
(*                                                                               *)
(* Floor(rules) is inductive by itself. Genesis conforms to the floor            *)
(* (RulesFloorBase's ASSUME, restricted to the entries in force), and under      *)
(* Mut = "none" an issuance is admissible only if the issued rules conform.      *)
(* Nothing else changes rules.                                                   *)

(* RulesFloorBase states this as an unnamed ASSUME; TLAPS does not use an       *)
(* unnamed module assumption unless cited, so it is proved here from the        *)
(* definitions. It is GenesisSatisfiesFloor in shape (ADR-0027 §2).             *)
LEMMA GenesisEntries == \A e \in AllEntries : Entry(e, Genesis)
BY DEF AllEntries, Entry, Genesis, Humans, Author, AnchorKeys, AuthActs

LEMMA GenesisFloor == Floor(Genesis)
BY GenesisEntries, ActiveEntries DEF Floor

LEMMA InitFloor == Init => FloorPreserved
BY GenesisFloor DEF Init, FloorPreserved

LEMMA NextFloor ==
    ASSUME Mut = "none", FloorPreserved, [Next]_vars
    PROVE  FloorPreserved'
<1>1. CASE UNCHANGED vars
    BY <1>1 DEF FloorPreserved, vars
<1>2. CASE Issue
    <2>1. PICK r \in RuleSpace : Admissible(r) /\ rules' = r
        BY <1>2 DEF Issue
    <2>2. Floor(r)
        BY <2>1 DEF Admissible
    <2> QED
        BY <2>1, <2>2 DEF FloorPreserved
<1> QED
    BY <1>1, <1>2 DEF Next

THEOREM FloorPreservedAlways ==
    ASSUME Mut = "none"
    PROVE  Spec => []FloorPreserved
<1>1. FloorPreserved /\ [Next]_vars => FloorPreserved'
    BY NextFloor
<1> QED
    BY InitFloor, <1>1, PTL DEF Spec

(* Why M_FLOOR must fail: with the floor check omitted, every rule in the space  *)
(* is admissible, so Issue can leave the floor from any state with an epoch      *)
(* to spare. The counterexample itself is TLC's (row anchor-mut).                *)
LEMMA MutAdmitsAll ==
    ASSUME Mut = "M_FLOOR"
    PROVE  \A r \in RuleSpace : Admissible(r)
BY DEF Admissible, Authentic

-----------------------------------------------------------------------------
(* EpochMonotone                                                                 *)
(*                                                                               *)
(* The epoch starts at 0 and Issue adds one only while it is below MaxEpoch,     *)
(* so 0..MaxEpoch is inductive. This holds under either mutation setting.        *)

LEMMA InitEpoch == Init => EpochMonotone
BY MaxEpochNat DEF Init, EpochMonotone

LEMMA NextEpoch == EpochMonotone /\ [Next]_vars => EpochMonotone'
<1> SUFFICES ASSUME EpochMonotone, [Next]_vars
             PROVE  EpochMonotone'
    OBVIOUS
<1>1. CASE UNCHANGED vars
    BY <1>1 DEF EpochMonotone, vars
<1>2. CASE Issue
    BY <1>2, MaxEpochNat DEF Issue, EpochMonotone
<1> QED
    BY <1>1, <1>2 DEF Next

THEOREM EpochMonotoneAlways == Spec => []EpochMonotone
BY InitEpoch, NextEpoch, PTL DEF Spec

=============================================================================
