--------------------------- MODULE RulesFloorBase ---------------------------
(* Shared definitions for the ADR-0029 §5 bootstrap modules: the rule space,   *)
(* the rules-floor entries, and the genesis rules.                             *)
(*                                                                             *)
(* This is the live definition of the floor. `RulesFloorNV.tla` (G1) and       *)
(* `RulesFloorNV_rev5.tla` (ADR-0026 §7) each carry their own frozen copy:     *)
(* both are dated artifacts cited by digest in accepted records, so they are   *)
(* never edited. Divergence between them and this module is expected and is    *)
(* what the dates are for.                                                     *)
(*                                                                             *)
(* Floor contents as ratified 2026.09.23: R1, R2, R5, R6, R7, R9.              *)
(*   R3 withdrawn (recusal is a mechanism constant, ADR-0024 §6)               *)
(*   R4 withdrawn (a timeout is never a grant, ADR-0024 §2)                    *)
(*   R8 reserved, candidate (break-glass grant TTL)                            *)
EXTENDS FiniteSets, Naturals

CONSTANT Active          \* the floor entries in force; drop one to mutate

Humans     == {"h1", "h2", "h3", "h4", "h5"}
Author     == "h1"
AnchorKeys == {"h4"}

\* Actions that change authority. ADR-0026 R7 keeps break-glass out of all three.
AuthActs == {"Issue", "Vote", "Promote"}
\* What an issuance could put in a break-glass envelope: ordinary operations,
\* and - if the floor let it - the authority-changing actions.
BGActs   == AuthActs \cup {"Op"}

\* quorum is "all" or a grant-vote threshold k (ADR-0024 §2, revision 5).
\* Tagged because TLC will not compare a string with a number; the records
\* write it as one field.
QVals == [mode : {"all", "k"}, k : 0..4]

RuleSpace == [grant       : SUBSET Humans,
              quorum      : QVals,
              minGrant    : 0..2,
              bgScope     : SUBSET BGActs,
              exceptions  : 0..3]       \* declared policy-floor exceptions (ADR-0013 §2)

Entry(e, r) ==
  CASE e = "R1" -> r.quorum.mode = "all"
    [] e = "R2" -> r.minGrant >= 2
    [] e = "R5" -> r.grant \cap AnchorKeys = {}
    [] e = "R6" -> r.exceptions <= 2
    [] e = "R7" -> r.bgScope \cap AuthActs = {}
    [] e = "R9" -> r.quorum.mode = "all" \/ r.quorum.k >= 2

AllEntries == {"R1", "R2", "R5", "R6", "R7", "R9"}

Floor(r) == \A e \in Active : Entry(e, r)

\* Genesis rules (ADR-0027): pre-blessed, resident, and floor-conformant.
\* Two exceptions at genesis: erasure and break-glass (ADR-0013 §3).
Genesis == [grant      |-> Humans \ ({Author} \cup AnchorKeys),
            quorum     |-> [mode |-> "all", k |-> 0],
            minGrant   |-> 2,
            bgScope    |-> {"Op"},
            exceptions |-> 2]

\* ADR-0027 §2 / ADR-0029 §5: the genesis rules satisfy the floor. This is the
\* shape of GenesisSatisfiesFloor; the Genesis module checks it as an invariant
\* over the real genesis contents once those are written.
ASSUME \A e \in AllEntries : Entry(e, Genesis)
=============================================================================
