----------------------------- MODULE Observers -----------------------------
(* Properties for ADR-0038, Observer scoping.                                  *)
(*                                                                             *)
(*   DenyByAnyOf     §5  a finding from any member of W(t) blocks t's next     *)
(*                       admit; no quorum of Observers is sought               *)
(*   ReachIsBounded  §1  a cell Observer's finding never names a principal      *)
(*                       outside its cell; only a correlator reaches across     *)
(*                                                                             *)
(* Two cells, each a Thinker and its cell Observer, and one correlator with no  *)
(* cell. W(t), the watched-by relation (§2), is the cell Observer of t's cell  *)
(* plus the correlator. A finding is deny-only: it blocks the target's next    *)
(* admit and nothing else (ADR-0007). Findings clear when the round ends.      *)
(*                                                                             *)
(* Mut = "none":     the mechanism as ADR-0038 specifies it.                    *)
(* Mut = "M_QUORUM": a finding takes effect only when a majority of W(t) have  *)
(*                   found against t. §5 must fail: one honest finding is      *)
(*                   suppressed by the other Observer's silence.               *)
(* Mut = "M_REACH":  a cell Observer may find against any principal in the     *)
(*                   domain. §1 must fail.                                     *)
EXTENDS FiniteSets, Naturals

CONSTANTS Mut

Thinkers  == {"t1", "t2"}
Observers == {"o1", "o2", "corr"}
CellOf    == [t1 |-> "c1", t2 |-> "c2", o1 |-> "c1", o2 |-> "c2", corr |-> "none"]

\* §2. W(t): the Observer seats authorized on t's round topic.
W(t) == {o \in Observers : CellOf[o] = CellOf[t] \/ CellOf[o] = "none"}

\* Who an Observer may find against. Under M_REACH a cell Observer reaches everyone.
Reach(o) == IF Mut = "M_REACH" \/ CellOf[o] = "none" THEN Thinkers
            ELSE {t \in Thinkers : CellOf[t] = CellOf[o]}

VARIABLES findings, admittedOverFinding, refused
vars == <<findings, admittedOverFinding, refused>>

Init == /\ findings = {}
        /\ admittedOverFinding = FALSE
        /\ refused = {}

Finding(o, t) ==
  /\ t \in Reach(o)
  /\ findings' = findings \cup {[obs |-> o, target |-> t]}
  /\ UNCHANGED <<admittedOverFinding, refused>>

Found(t) == {f.obs : f \in {g \in findings : g.target = t}}

\* §5. Any-of: t is blocked if any member of W(t) has found against it.
\* M_QUORUM: blocked only if more than half of W(t) have.
Blocked(t) ==
  IF Mut = "M_QUORUM" THEN 2 * Cardinality(Found(t) \cap W(t)) > Cardinality(W(t))
  ELSE Found(t) \cap W(t) # {}

Admit(t) ==
  /\ ~Blocked(t)
  /\ admittedOverFinding' = (admittedOverFinding \/ (Found(t) \cap W(t) # {}))
  /\ UNCHANGED <<findings, refused>>

Refuse(t) ==
  /\ Blocked(t)
  /\ refused' = refused \cup {t}
  /\ UNCHANGED <<findings, admittedOverFinding>>

\* The round ends: the findings against t clear with it.
EndRound(t) ==
  /\ findings' = {f \in findings : f.target # t}
  /\ UNCHANGED <<admittedOverFinding, refused>>

Next == \E t \in Thinkers : Admit(t) \/ Refuse(t) \/ EndRound(t) \/ \E o \in Observers : Finding(o, t)
Spec == Init /\ [][Next]_vars

\* --- the two properties -----------------------------------------------------

\* §5. No admit ever went through while some member of W(t) had found against t.
DenyByAnyOf == ~admittedOverFinding

\* §1. A cell Observer's finding names only a principal in its own cell.
ReachIsBounded ==
  \A f \in findings : CellOf[f.obs] = "none" \/ CellOf[f.obs] = CellOf[f.target]

Safe == DenyByAnyOf /\ ReachIsBounded

\* --- reachability witnesses: each must be VIOLATED ---------------------------
NeverFound            == findings = {}
NeverRefused          == refused = {}
CorrelatorNeverFinds  == ~\E f \in findings : f.obs = "corr"
\* One Observer's finding alone is enough (§5): t is refused while only one member of W(t) has found.
NeverRefusedOnOne     == ~\E t \in refused : Cardinality(Found(t) \cap W(t)) = 1
=============================================================================
