------------------------------- MODULE Anchor -------------------------------
(* ADR-0029 §5 bootstrap module 2 of 5.                                        *)
(* Invariant: FloorPreserved.                                                  *)
(*                                                                             *)
(* ADR-0025: the trust anchor is a havoc issuer. `Issue` is an environment     *)
(* action constrained only by `Authentic`, an epoch increment, and the rules    *)
(* floor (ADR-0026 §1). Safety is proven for every issuance sequence meeting    *)
(* those constraints, so anchor custody never enters the proof.                 *)
(*                                                                             *)
(* `Authentic` is opaque here, as ADR-0025 §2 requires. Modeling it as TRUE is  *)
(* the havoc reading and is the strongest case: the anchor may issue anything   *)
(* the floor admits, including rules a careless custodian would not intend.     *)
(*                                                                             *)
(* Mut = "none":     the mechanism as ADR-0026 §1 specifies it.                 *)
(* Mut = "M_FLOOR":  mutation. The mechanism accepts an issuance without        *)
(*                   checking it against the floor. FloorPreserved must fail.   *)
EXTENDS RulesFloorBase

CONSTANTS Mut, MaxEpoch

VARIABLES rules, epoch
vars == <<rules, epoch>>

Init == rules = Genesis /\ epoch = 0

\* ADR-0025 §2: Authentic(i) is opaque in the specification. Under havoc every
\* issuance is authentic; the custody declaration instantiates it, outside the
\* model (ADR-0025 annex).
Authentic(r) == TRUE

Admissible(r) ==
  IF Mut = "M_FLOOR" THEN Authentic(r)          \* the floor check, omitted
                     ELSE Authentic(r) /\ Floor(r)

Issue ==
  /\ epoch < MaxEpoch
  /\ \E r \in RuleSpace :
       /\ Admissible(r)
       /\ rules' = r
  /\ epoch' = epoch + 1

Next == Issue
Spec == Init /\ [][Next]_vars

\* FloorPreserved. Every reachable rules state conforms to the floor, whatever
\* the anchor issues and however many times it issues.
FloorPreserved == Floor(rules)

\* The epoch chain is rooted at genesis and advances by one (ADR-0027 §4).
EpochMonotone == epoch \in 0..MaxEpoch

\* Reachability witness: must be VIOLATED, or FloorPreserved holds because the
\* anchor never issued anything.
NeverIssued == epoch = 0
=============================================================================
