---------------------------- MODULE Workflow_proof ----------------------------
(* TLAPS proof of the invariants of Workflow.tla (ADR-0054 §12). Workflow.tla  *)
(* is not edited.                                                              *)
(*                                                                             *)
(*   THEOREM AppliedRouteEnabledAlways    [Mut # "M_DECIDEONLY",               *)
(*                                         Mut # "M_NOCONSUME"]                *)
(*   THEOREM OneRoutePerDecisionAlways    [Mut # "M_DECIDEONLY",               *)
(*                                         Mut # "M_NOCONSUME"]                *)
(*   THEOREM FindingPrecedesNoRouteAlways [Mut # "M_DECIDEONLY"]               *)
(*   THEOREM ChosenOnlyByRouteAlways      [Mut # "M_DEFAULT"]                  *)
(*   THEOREM EdgeAfterCoverageAlways      [Mut # "M_UNCOVERED"]                *)
(*   THEOREM TaintedNeverOutwardAlways    [Mut # "M_NOTAINT"]                  *)
(*   THEOREM GrantUnderPromotionAlways    [Mut # "M_GRANTANYEPOCH"]            *)
(*   THEOREM PromotedAlternatesAlways     [Mut # "M_NOLINEAGE"]                *)
(*   THEOREM CompletedOnlyBySinkAlways    [Mut # "M_TIMEOUTDONE"]              *)
(*   THEOREM BasisStableAlways            [Mut # "M_REWRITE"]                  *)
(*   THEOREM SafeAlways                   [Mut = "none"]                       *)
(*                                                                             *)
(* Each hypothesis is the mutation the "breaks" rows of Workflow-rows.txt      *)
(* pair with the property, and no other.                                       *)
(*                                                                             *)
(* The strengthening. `Shape` holds under every mutation: the type invariant;  *)
(* before the promotion nothing has started and no route is in flight; the     *)
(* source of a route in flight has ended, and an ended node stays ended; a     *)
(* node with no finding has no finding position; every applied route's         *)
(* position is at or before the log's.                                         *)
(*                                                                             *)
(* On top of it, what a route in flight carries from decide to apply:          *)
(*   EdgeAfterCoverage   its source is covered, and coverage is never undone;  *)
(*   TaintedNeverOutward a route to an outward node was decided on a trusted   *)
(*                       source label, and an ended node's label does not      *)
(*                       change, not even under M_REWRITE, which rewrites its  *)
(*                       status alone;                                         *)
(*   BasisStable         its basis is the decision node's attributes, which    *)
(*                       only a rewrite could change once that node has ended. *)
(* These are why neither property is broken by M_DECIDEONLY: the check at      *)
(* decide stays true at apply. OneRoutePerDecision is carried by "the applied  *)
(* set is empty or one element, and empty until the decision is consumed".     *)
(* FindingPrecedesNoRoute needs only `Shape`, the guard at apply, and a        *)
(* finding's position being past every position already in the log.           *)
(*                                                                             *)
(* Mutations and witnesses are behaviours and stay with TLC                    *)
(* (Workflow-results-*.txt). Check: tools/tlapm --cleanfp --strict.            *)
EXTENDS Workflow, FiniteSetTheorems, TLAPS

Statuses == {"idle", "ready", "running", "ended", "failed"}
Hows     == {"none", "route", "computed", "default"}
Whys     == {"lease", "ended", "consumed", "finding", "guard"}
AttrRec  == [st : Sts \cup {"none"}, lbl : Lbls]
PendRec  == [edge : Chosen, ep : Nat, basis : AttrRec]
AppRec   == [edge : Chosen, at : Nat, ok : BOOLEAN, basis : AttrRec, now : AttrRec]

TypeOK ==
  /\ promoted \in BOOLEAN
  /\ seatOK \in BOOLEAN
  /\ epoch \in Nat
  /\ orchLive \in BOOLEAN
  /\ wf \in {"running", "completed", "failed"}
  /\ status \in [Nodes -> Statuses]
  /\ attr \in [Nodes -> AttrRec]
  /\ grantEpoch \in [Nodes -> Int]
  /\ covered \in [Nodes -> BOOLEAN]
  /\ finding \in [Nodes -> BOOLEAN]
  /\ findingAt \in [Nodes -> Nat]
  /\ idx \in Nat
  /\ consumed \in BOOLEAN
  /\ decisionFailed \in BOOLEAN
  /\ pending \subseteq PendRec
  /\ applied \subseteq AppRec
  /\ voided \subseteq [edge : Edges, why : Whys]
  /\ activatedBy \in [Nodes -> Hows]
  /\ routedOnTaint \in [Nodes -> BOOLEAN]
  /\ uncoveredAct \in [Nodes -> BOOLEAN]

BeforePromotion == ~promoted => /\ pending = {}
                                /\ \A n \in Nodes : status[n] = "idle"
PendingEnded    == \A r \in pending : status[Src[r.edge]] = "ended"
NoFindingNoAt   == \A n \in Nodes : ~finding[n] => findingAt[n] = 0
AppliedBound    == \A r \in applied : r.at <= idx

Shape == TypeOK /\ BeforePromotion /\ PendingEnded /\ NoFindingNoAt /\ AppliedBound

\* At most one route has been applied, and none until the decision point is consumed.
AtMostOne == /\ applied = {} \/ \E x \in AppRec : applied = {x}
             /\ ~consumed => applied = {}
\* What a route in flight carries from decide to apply.
PendingCovered == \A r \in pending : covered[Src[r.edge]]
PendingTrusted == \A r \in pending : ~(Dst[r.edge] \in Outward /\ attr[Src[r.edge]].lbl = "untrusted")
PendingBasis   == \A r \in pending : r.basis = attr["s"]

InvO == AtMostOne
InvC == EdgeAfterCoverage /\ PendingCovered
InvT == TaintedNeverOutward /\ PendingTrusted
InvB == BasisStable /\ PendingBasis
-----------------------------------------------------------------------------
LEMMA EdgeFacts ==
  /\ Chosen \subseteq Edges
  /\ Computed \subseteq Edges
  /\ \A e \in Edges : Src[e] \in Nodes /\ Dst[e] \in Nodes
  /\ \A e \in Edges : Anc[Src[e]] \cup {Src[e]} \subseteq Nodes
  /\ \A e \in Chosen : Src[e] = "s"
  /\ \A e \in Computed : Dst[e] = "j"
  /\ \A e \in Chosen : Dst[e] # "j"
  /\ Dst["e1"] = "b" /\ Dst["e2"] = "c"
  /\ Outward = {"c"}
  /\ Sink = "j"
  BY DEF Chosen, Computed, Edges, Src, Dst, Anc, Nodes, Outward, Sink

LEMMA NoAttrRec == NoAttr \in AttrRec
  BY DEF NoAttr, AttrRec, Lbls

LEMMA InitTypeOK == Init => TypeOK
  BY NoAttrRec DEF Init, TypeOK, PE, Statuses, Hows

\* What Activate does, for every edge, in one shape.
LEMMA ActivateShape ==
  ASSUME TypeOK, NEW e \in Edges, NEW how \in Hows, Activate(e, how)
  PROVE  /\ status' \in [Nodes -> Statuses]
         /\ activatedBy' \in [Nodes -> Hows]
         /\ routedOnTaint' \in [Nodes -> BOOLEAN]
         /\ uncoveredAct' \in [Nodes -> BOOLEAN]
         /\ \A n \in Nodes : status[n] = "ended" => status'[n] = "ended"
         /\ \A n \in Nodes : n # Dst[e] => /\ status'[n] = status[n]
                                           /\ activatedBy'[n] = activatedBy[n]
                                           /\ routedOnTaint'[n] = routedOnTaint[n]
                                           /\ uncoveredAct'[n] = uncoveredAct[n]
         /\ \/ /\ activatedBy'[Dst[e]] = how
               /\ routedOnTaint'[Dst[e]] = (attr[Src[e]].lbl = "untrusted")
               /\ uncoveredAct'[Dst[e]] = ~covered[Src[e]]
            \/ /\ activatedBy'[Dst[e]] = activatedBy[Dst[e]]
               /\ routedOnTaint'[Dst[e]] = routedOnTaint[Dst[e]]
               /\ uncoveredAct'[Dst[e]] = uncoveredAct[Dst[e]]
<1>1. Dst[e] \in Nodes /\ Src[e] \in Nodes
  BY EdgeFacts
<1> QED
  BY <1>1 DEF Activate, TypeOK, Statuses

\* Activate's four writes, as one fact: citing it is an instantiation, where citing ActivateShape
\* for the same conjuncts is too large a match for the checked SMT route.
ActivateTypesP == /\ status' \in [Nodes -> Statuses]
                  /\ activatedBy' \in [Nodes -> Hows]
                  /\ routedOnTaint' \in [Nodes -> BOOLEAN]
                  /\ uncoveredAct' \in [Nodes -> BOOLEAN]

LEMMA ActivateTypes ==
  ASSUME TypeOK, NEW e \in Edges, NEW how \in Hows, Activate(e, how)
  PROVE  ActivateTypesP
<1>1. Dst[e] \in Nodes
  BY EdgeFacts
<1> QED
  BY <1>1 DEF Activate, TypeOK, Statuses, ActivateTypesP

\* M_DEFAULT's choice is a chosen edge that is enabled.
LEMMA DefaultEdge ==
  ASSUME \E e \in Chosen : Enabled(e)
  PROVE  LET ch == CHOOSE x \in Chosen : Enabled(x) IN ch \in Chosen /\ Enabled(ch)
  OBVIOUS

LEMMA ApplyTypeOK ==
  ASSUME TypeOK, NEW r \in pending, Apply(r)
  PROVE  /\ pending' \subseteq PendRec /\ idx' \in Nat
         /\ applied' \subseteq AppRec
         /\ voided' \subseteq [edge : Edges, why : Whys]
         /\ consumed' \in BOOLEAN
         /\ status' \in [Nodes -> Statuses]
         /\ activatedBy' \in [Nodes -> Hows]
         /\ routedOnTaint' \in [Nodes -> BOOLEAN]
         /\ uncoveredAct' \in [Nodes -> BOOLEAN]
<1>1. r \in PendRec /\ r.edge \in Edges
  BY EdgeFacts DEF TypeOK, PendRec
<1>2. attr["s"] \in AttrRec /\ r.basis \in AttrRec /\ r.edge \in Chosen
  BY <1>1 DEF TypeOK, PendRec, Nodes
<1>3. RouteOK(r, FALSE) \in BOOLEAN
  BY DEF RouteOK
<1>4. Why(r) \in Whys
  BY DEF Why, Whys
<1>5. "route" \in Hows
  BY DEF Hows
<1>6. [edge |-> r.edge, at |-> idx + 1, ok |-> RouteOK(r, FALSE), basis |-> r.basis, now |-> attr["s"]] \in AppRec
  BY <1>2, <1>3 DEF TypeOK, AppRec
<1>7. [edge |-> r.edge, why |-> Why(r)] \in [edge : Edges, why : Whys]
  BY <1>1, <1>4
<1>8. CASE Mut = "M_DECIDEONLY" \/ RouteOK(r, TRUE)
  <2>1. /\ pending' = pending \ {r} /\ idx' = idx + 1 /\ consumed' = TRUE
        /\ Activate(r.edge, "route")
        /\ applied' = applied \cup {[edge |-> r.edge, at |-> idx + 1, ok |-> RouteOK(r, FALSE),
                                     basis |-> r.basis, now |-> attr["s"]]}
        /\ UNCHANGED voided
    BY <1>8 DEF Apply
  <2>2. ActivateTypesP
    BY <1>1, <1>5, <2>1, ActivateTypes
  <2> QED
    BY <1>6, <2>1, <2>2 DEF TypeOK, ActivateTypesP
<1>9. CASE ~(Mut = "M_DECIDEONLY" \/ RouteOK(r, TRUE))
  <2>1. /\ pending' = pending \ {r} /\ idx' = idx + 1
        /\ voided' = voided \cup {[edge |-> r.edge, why |-> Why(r)]}
        /\ UNCHANGED <<consumed, status, applied, act>>
    BY <1>9 DEF Apply
  <2> QED
    BY <1>7, <2>1 DEF TypeOK, act
<1> QED
  BY <1>8, <1>9

LEMMA NextTypeOK == TypeOK /\ [Next]_vars => TypeOK'
<1> SUFFICES ASSUME TypeOK, [Next]_vars PROVE TypeOK' OBVIOUS
<1>1. CASE UNCHANGED vars
  BY <1>1 DEF TypeOK, vars, top, nodeV, obsV, route, act
<1>2. ASSUME NEW st \in Seatings, Promote(st) PROVE TypeOK'
  <2>1. Alternates(st) \in BOOLEAN
    BY DEF Alternates
  <2> QED
    BY <1>2, <2>1 DEF Promote, TypeOK, Nodes, Statuses, obsV, route, act
<1>3. ASSUME NEW n \in Nodes, Grant(n) PROVE TypeOK'
  BY <1>3 DEF Grant, TypeOK, Statuses, top, obsV, route, act, PE
<1>4. ASSUME NEW n \in Nodes, Fail(n) PROVE TypeOK'
  BY <1>4 DEF Fail, TypeOK, Statuses, top, obsV, route, act
<1>5. ASSUME NEW n \in Nodes, Cover(n) PROVE TypeOK'
  BY <1>5 DEF Cover, TypeOK, top, obsV, route, act
<1>6. ASSUME NEW n \in Nodes, Finding(n) PROVE TypeOK'
  BY <1>6 DEF Finding, TypeOK, top, nodeV, route, act
<1>7. ASSUME NEW n \in Nodes, NEW s \in Sts, NEW l \in Lbls, End(n, s, l) PROVE TypeOK'
  BY <1>7 DEF End, TypeOK, AttrRec, Statuses, top, obsV, route, act
<1>8. ASSUME NEW n \in Nodes, NEW s \in Sts, Rewrite(n, s) PROVE TypeOK'
  BY <1>8 DEF Rewrite, TypeOK, AttrRec, top, obsV, route, act
<1>9. ASSUME NEW e \in Chosen, Decide(e) PROVE TypeOK'
  <2>1. attr["s"] \in AttrRec
    BY DEF TypeOK, Nodes
  <2>2. [edge |-> e, ep |-> epoch, basis |-> attr["s"]] \in PendRec
    BY <2>1 DEF TypeOK, PendRec
  <2> QED
    BY <1>9, <2>2 DEF Decide, TypeOK, top, nodeV, obsV, act
<1>10. ASSUME NEW r \in pending, Apply(r) PROVE TypeOK'
  <2>1. UNCHANGED <<promoted, seatOK, epoch, orchLive, wf, attr, grantEpoch, covered, finding, findingAt,
                    decisionFailed>>
    BY <1>10 DEF Apply, top
  <2> QED
    BY <1>10, <2>1, ApplyTypeOK DEF TypeOK
<1>11. ASSUME NEW e \in Computed, Fire(e) PROVE TypeOK'
  <2>1. e \in Edges /\ "computed" \in Hows
    BY EdgeFacts DEF Hows
  <2>2. /\ status' \in [Nodes -> Statuses]
        /\ activatedBy' \in [Nodes -> Hows]
        /\ routedOnTaint' \in [Nodes -> BOOLEAN]
        /\ uncoveredAct' \in [Nodes -> BOOLEAN]
    BY <1>11, <2>1, ActivateShape DEF Fire
  <2> QED
    BY <1>11, <2>2 DEF Fire, TypeOK, top, obsV, route
<1>12. CASE OrchLapse
  BY <1>12 DEF OrchLapse, TypeOK, nodeV, obsV, route, act
<1>13. CASE DecisionLapse
  <2>1. CASE Mut = "M_DEFAULT" /\ \E e \in Chosen : Enabled(e)
    <3>1. /\ consumed' = TRUE /\ UNCHANGED decisionFailed
          /\ Activate(CHOOSE x \in Chosen : Enabled(x), "default")
      BY <1>13, <2>1 DEF DecisionLapse
    <3>2. (CHOOSE x \in Chosen : Enabled(x)) \in Edges /\ "default" \in Hows
      BY <2>1, DefaultEdge, EdgeFacts DEF Hows
    <3>3. ActivateTypesP
      BY <3>1, <3>2, ActivateTypes
    <3> QED
      BY <1>13, <3>1, <3>3 DEF DecisionLapse, TypeOK, top, obsV, ActivateTypesP
  <2>2. CASE ~(Mut = "M_DEFAULT" /\ \E e \in Chosen : Enabled(e))
    BY <1>13, <2>2 DEF DecisionLapse, TypeOK, top, obsV, act
  <2> QED
    BY <2>1, <2>2
<1>14. CASE Fence
  BY <1>14 DEF Fence, TypeOK, PE, Statuses, route, act
<1>15. CASE Settle
  BY <1>15 DEF Settle, TypeOK, nodeV, obsV, route, act
<1> QED
  BY <1>1, <1>2, <1>3, <1>4, <1>5, <1>6, <1>7, <1>8, <1>9, <1>10, <1>11, <1>12, <1>13, <1>14, <1>15 DEF Next

LEMMA InitShape == Init => Shape
  BY InitTypeOK DEF Init, Shape, BeforePromotion, PendingEnded, NoFindingNoAt, AppliedBound

\* An ended node stays ended: every action, given that nothing has started before the promotion.
LEMMA EndedFrozen ==
  ASSUME TypeOK, BeforePromotion, [Next]_vars
  PROVE  \A n \in Nodes : status[n] = "ended" => status'[n] = "ended"
<1> SUFFICES ASSUME NEW m \in Nodes, status[m] = "ended" PROVE status'[m] = "ended" OBVIOUS
<1>1. promoted
  BY DEF BeforePromotion
<1>2. CASE UNCHANGED vars
  BY <1>2 DEF vars, nodeV
<1>3. ASSUME NEW st \in Seatings, Promote(st) PROVE status'[m] = "ended"
  BY <1>1, <1>3 DEF Promote
<1>4. ASSUME NEW n \in Nodes, Grant(n) PROVE status'[m] = "ended"
  BY <1>4 DEF Grant, TypeOK
<1>5. ASSUME NEW n \in Nodes, Fail(n) PROVE status'[m] = "ended"
  BY <1>5 DEF Fail, TypeOK
<1>6. ASSUME NEW n \in Nodes, Cover(n) PROVE status'[m] = "ended"
  BY <1>6 DEF Cover
<1>7. ASSUME NEW n \in Nodes, Finding(n) PROVE status'[m] = "ended"
  BY <1>7 DEF Finding, nodeV
<1>8. ASSUME NEW n \in Nodes, NEW s \in Sts, NEW l \in Lbls, End(n, s, l) PROVE status'[m] = "ended"
  BY <1>8 DEF End, TypeOK
<1>9. ASSUME NEW n \in Nodes, NEW s \in Sts, Rewrite(n, s) PROVE status'[m] = "ended"
  BY <1>9 DEF Rewrite
<1>10. ASSUME NEW e \in Chosen, Decide(e) PROVE status'[m] = "ended"
  BY <1>10 DEF Decide, nodeV
<1>11. ASSUME NEW r \in pending, Apply(r) PROVE status'[m] = "ended"
  <2>1. r \in PendRec /\ r.edge \in Edges
    BY EdgeFacts DEF TypeOK, PendRec
  <2>2. "route" \in Hows
    BY DEF Hows
  <2>3. CASE Mut = "M_DECIDEONLY" \/ RouteOK(r, TRUE)
    <3>1. Activate(r.edge, "route")
      BY <1>11, <2>3 DEF Apply
    <3> QED
      BY <2>1, <2>2, <3>1, ActivateShape
  <2>4. CASE ~(Mut = "M_DECIDEONLY" \/ RouteOK(r, TRUE))
    BY <1>11, <2>4 DEF Apply
  <2> QED
    BY <2>3, <2>4
<1>12. ASSUME NEW e \in Computed, Fire(e) PROVE status'[m] = "ended"
  <2>1. e \in Edges /\ "computed" \in Hows
    BY EdgeFacts DEF Hows
  <2> QED
    BY <1>12, <2>1, ActivateShape DEF Fire
<1>13. CASE OrchLapse
  BY <1>13 DEF OrchLapse, nodeV
<1>14. CASE DecisionLapse
  <2>1. CASE Mut = "M_DEFAULT" /\ \E e \in Chosen : Enabled(e)
    <3>1. Activate(CHOOSE x \in Chosen : Enabled(x), "default")
      BY <1>14, <2>1 DEF DecisionLapse
    <3>2. (CHOOSE x \in Chosen : Enabled(x)) \in Edges /\ "default" \in Hows
      BY <2>1, DefaultEdge, EdgeFacts DEF Hows
    <3> QED
      BY <3>1, <3>2, ActivateShape
  <2>2. CASE ~(Mut = "M_DEFAULT" /\ \E e \in Chosen : Enabled(e))
    BY <1>14, <2>2 DEF DecisionLapse
  <2> QED
    BY <2>1, <2>2
<1>15. CASE Fence
  BY <1>15 DEF Fence
<1>16. CASE Settle
  BY <1>16 DEF Settle, nodeV
<1> QED
  BY <1>2, <1>3, <1>4, <1>5, <1>6, <1>7, <1>8, <1>9, <1>10, <1>11, <1>12, <1>13, <1>14, <1>15, <1>16 DEF Next

\* Every action but Apply leaves the applied set alone, and idx only grows.
LEMMA AppliedStep ==
  ASSUME [Next]_vars
  PROVE  /\ (UNCHANGED applied) \/ \E r \in pending : Apply(r)
         /\ idx \in Nat => idx' \in Nat /\ idx' >= idx
<1>1. CASE UNCHANGED vars
  BY <1>1 DEF vars, route, obsV
<1>2. ASSUME \/ \E st \in Seatings : Promote(st)
             \/ \E n \in Nodes : Grant(n) \/ Fail(n) \/ Cover(n)
             \/ \E n \in Nodes, s \in Sts, l \in Lbls : End(n, s, l)
             \/ \E n \in Nodes, s \in Sts : Rewrite(n, s)
             \/ \E e \in Chosen : Decide(e)
             \/ \E e \in Computed : Fire(e)
             \/ OrchLapse \/ DecisionLapse \/ Settle
      PROVE  UNCHANGED <<applied, idx>>
  BY <1>2 DEF Promote, Grant, Fail, Cover, End, Rewrite, Decide, Fire, OrchLapse, DecisionLapse, Settle,
              route, obsV
<1>3. ASSUME NEW n \in Nodes, Finding(n) PROVE UNCHANGED applied /\ idx' = idx + 1
  BY <1>3 DEF Finding, route
<1>4. CASE Fence
  BY <1>4 DEF Fence, route
<1>5. ASSUME NEW r \in pending, Apply(r) PROVE idx' = idx + 1
  BY <1>5 DEF Apply
<1> QED
  BY <1>1, <1>2, <1>3, <1>4, <1>5 DEF Next

\* Every action but Apply, Fire and DecisionLapse leaves the activation record alone.
LEMMA ActStep ==
  ASSUME [Next]_vars
  PROVE  \/ UNCHANGED <<activatedBy, routedOnTaint, uncoveredAct>>
         \/ \E r \in pending : Apply(r)
         \/ \E e \in Computed : Fire(e)
         \/ DecisionLapse
<1>1. CASE UNCHANGED vars
  BY <1>1 DEF vars, act
<1>2. ASSUME \/ \E st \in Seatings : Promote(st)
             \/ \E n \in Nodes : Grant(n) \/ Fail(n) \/ Cover(n) \/ Finding(n)
             \/ \E n \in Nodes, s \in Sts, l \in Lbls : End(n, s, l)
             \/ \E n \in Nodes, s \in Sts : Rewrite(n, s)
             \/ \E e \in Chosen : Decide(e)
             \/ OrchLapse \/ Fence \/ Settle
      PROVE  UNCHANGED <<activatedBy, routedOnTaint, uncoveredAct>>
  BY <1>2 DEF Promote, Grant, Fail, Cover, Finding, End, Rewrite, Decide, OrchLapse, Fence, Settle, act
<1> QED
  BY <1>1, <1>2 DEF Next

LEMMA NextShape == Shape /\ [Next]_vars => Shape'
<1> SUFFICES ASSUME Shape, [Next]_vars PROVE Shape' OBVIOUS
<1>0. /\ TypeOK /\ TypeOK'
      /\ BeforePromotion /\ PendingEnded /\ NoFindingNoAt /\ AppliedBound
  BY NextTypeOK DEF Shape
<1>f. \A n \in Nodes : status[n] = "ended" => status'[n] = "ended"
  BY <1>0, EndedFrozen
<1>a. AppliedBound'
  <2> SUFFICES ASSUME NEW r \in applied' PROVE r.at <= idx'
    BY DEF AppliedBound
  <2>1. idx \in Nat /\ idx' \in Nat /\ idx' >= idx
    BY <1>0, AppliedStep DEF TypeOK
  <2>2. CASE UNCHANGED applied
    <3>1. r \in applied /\ r.at \in Nat
      BY <1>0, <2>2 DEF TypeOK, AppRec
    <3>2. r.at <= idx
      BY <1>0, <3>1 DEF AppliedBound
    <3> QED
      BY <2>1, <3>1, <3>2
  <2>3. ASSUME NEW q \in pending, Apply(q) PROVE r.at <= idx'
    <3>1. CASE Mut = "M_DECIDEONLY" \/ RouteOK(q, TRUE)
      <4>1. /\ idx' = idx + 1
            /\ applied' = applied \cup {[edge |-> q.edge, at |-> idx + 1, ok |-> RouteOK(q, FALSE),
                                         basis |-> q.basis, now |-> attr["s"]]}
        BY <2>3, <3>1 DEF Apply
      <4>2. r \in applied => r.at <= idx /\ r.at \in Nat
        BY <1>0 DEF AppliedBound, TypeOK, AppRec
      <4>3. r \notin applied => r.at = idx + 1
        BY <4>1
      <4> QED
        BY <2>1, <4>1, <4>2, <4>3
    <3>2. CASE ~(Mut = "M_DECIDEONLY" \/ RouteOK(q, TRUE))
      <4>1. UNCHANGED applied /\ idx' = idx + 1
        BY <2>3, <3>2 DEF Apply
      <4>2. r.at <= idx /\ r.at \in Nat
        BY <1>0, <4>1 DEF AppliedBound, TypeOK, AppRec
      <4> QED
        BY <2>1, <4>1, <4>2
    <3> QED
      BY <3>1, <3>2
  <2> QED
    BY <2>2, <2>3, AppliedStep
<1>b. BeforePromotion' /\ PendingEnded' /\ NoFindingNoAt'
  <2>1. CASE UNCHANGED vars
    BY <1>0, <2>1 DEF vars, top, nodeV, obsV, route, BeforePromotion, PendingEnded, NoFindingNoAt
  <2>2. ASSUME NEW st \in Seatings, Promote(st) PROVE BeforePromotion' /\ PendingEnded' /\ NoFindingNoAt'
    BY <1>0, <2>2 DEF Promote, BeforePromotion, PendingEnded, NoFindingNoAt, obsV, route
  <2>3. ASSUME NEW n \in Nodes, Grant(n) PROVE BeforePromotion' /\ PendingEnded' /\ NoFindingNoAt'
    <3>1. promoted /\ promoted' /\ UNCHANGED <<pending, finding, findingAt>>
      BY <2>3 DEF Grant, top, obsV, route
    <3>2. PendingEnded'
      BY <1>0, <1>f, <3>1, EdgeFacts DEF PendingEnded, TypeOK, PendRec
    <3> QED
      BY <1>0, <3>1, <3>2 DEF BeforePromotion, NoFindingNoAt
  <2>4. ASSUME NEW n \in Nodes, Fail(n) PROVE BeforePromotion' /\ PendingEnded' /\ NoFindingNoAt'
    <3>1. /\ UNCHANGED <<promoted, pending, finding, findingAt>>
          /\ status[n] = "running"
          /\ status' = [status EXCEPT ![n] = "failed"]
      BY <2>4 DEF Fail, top, obsV, route
    <3>2. promoted
      BY <1>0, <3>1 DEF BeforePromotion
    <3>3. PendingEnded'
      BY <1>0, <1>f, <3>1, EdgeFacts DEF PendingEnded, TypeOK, PendRec
    <3> QED
      BY <1>0, <3>1, <3>2, <3>3 DEF BeforePromotion, NoFindingNoAt
  <2>5. ASSUME NEW n \in Nodes, Cover(n) PROVE BeforePromotion' /\ PendingEnded' /\ NoFindingNoAt'
    BY <1>0, <2>5 DEF Cover, top, obsV, route, BeforePromotion, PendingEnded, NoFindingNoAt
  <2>6. ASSUME NEW n \in Nodes, Finding(n) PROVE BeforePromotion' /\ PendingEnded' /\ NoFindingNoAt'
    BY <1>0, <2>6 DEF Finding, top, nodeV, route, BeforePromotion, PendingEnded, NoFindingNoAt, TypeOK
  <2>7. ASSUME NEW n \in Nodes, NEW s \in Sts, NEW l \in Lbls, End(n, s, l)
        PROVE  BeforePromotion' /\ PendingEnded' /\ NoFindingNoAt'
    <3>1. /\ UNCHANGED <<promoted, pending, finding, findingAt>>
          /\ status[n] = "running"
          /\ status' = [status EXCEPT ![n] = "ended"]
      BY <2>7 DEF End, top, obsV, route
    <3>2. promoted
      BY <1>0, <3>1 DEF BeforePromotion
    <3>3. PendingEnded'
      BY <1>0, <1>f, <3>1, EdgeFacts DEF PendingEnded, TypeOK, PendRec
    <3> QED
      BY <1>0, <3>1, <3>2, <3>3 DEF BeforePromotion, NoFindingNoAt
  <2>8. ASSUME NEW n \in Nodes, NEW s \in Sts, Rewrite(n, s)
        PROVE  BeforePromotion' /\ PendingEnded' /\ NoFindingNoAt'
    BY <1>0, <2>8 DEF Rewrite, top, obsV, route, BeforePromotion, PendingEnded, NoFindingNoAt
  <2>9. ASSUME NEW e \in Chosen, Decide(e) PROVE BeforePromotion' /\ PendingEnded' /\ NoFindingNoAt'
    <3>1. /\ promoted /\ promoted' /\ UNCHANGED <<status, finding, findingAt>>
          /\ pending' = pending \cup {[edge |-> e, ep |-> epoch, basis |-> attr["s"]]}
          /\ status[Src[e]] = "ended"
      BY <2>9 DEF Decide, RouteOK, Enabled, top, nodeV, obsV
    <3> QED
      BY <1>0, <3>1 DEF BeforePromotion, PendingEnded, NoFindingNoAt
  <2>10. ASSUME NEW r \in pending, Apply(r) PROVE BeforePromotion' /\ PendingEnded' /\ NoFindingNoAt'
    <3>1. /\ promoted /\ promoted'
          /\ pending' = pending \ {r}
          /\ UNCHANGED <<finding, findingAt>>
      BY <1>0, <2>10 DEF Apply, BeforePromotion, top
    <3>2. PendingEnded'
      BY <1>0, <1>f, <3>1, EdgeFacts DEF PendingEnded, TypeOK, PendRec
    <3> QED
      BY <1>0, <3>1, <3>2 DEF BeforePromotion, NoFindingNoAt
  <2>11. ASSUME NEW e \in Computed, Fire(e) PROVE BeforePromotion' /\ PendingEnded' /\ NoFindingNoAt'
    <3>1. promoted /\ promoted' /\ UNCHANGED <<pending, finding, findingAt>>
      BY <2>11 DEF Fire, top, obsV, route
    <3>2. PendingEnded'
      BY <1>0, <1>f, <3>1, EdgeFacts DEF PendingEnded, TypeOK, PendRec
    <3> QED
      BY <1>0, <3>1, <3>2 DEF BeforePromotion, NoFindingNoAt
  <2>12. CASE OrchLapse
    BY <1>0, <2>12 DEF OrchLapse, nodeV, obsV, route, BeforePromotion, PendingEnded, NoFindingNoAt
  <2>13. CASE DecisionLapse
    <3>1. promoted /\ promoted' /\ UNCHANGED <<pending, finding, findingAt>>
      BY <2>13 DEF DecisionLapse, top, obsV
    <3>2. PendingEnded'
      BY <1>0, <1>f, <3>1, EdgeFacts DEF PendingEnded, TypeOK, PendRec
    <3> QED
      BY <1>0, <3>1, <3>2 DEF BeforePromotion, NoFindingNoAt
  <2>14. CASE Fence
    <3>1. promoted /\ promoted' /\ UNCHANGED <<pending, finding, findingAt>>
      BY <2>14 DEF Fence, route
    <3>2. PendingEnded'
      BY <1>0, <1>f, <3>1, EdgeFacts DEF PendingEnded, TypeOK, PendRec
    <3> QED
      BY <1>0, <3>1, <3>2 DEF BeforePromotion, NoFindingNoAt
  <2>15. CASE Settle
    BY <1>0, <2>15 DEF Settle, nodeV, obsV, route, BeforePromotion, PendingEnded, NoFindingNoAt
  <2> QED
    BY <2>1, <2>2, <2>3, <2>4, <2>5, <2>6, <2>7, <2>8, <2>9, <2>10, <2>11, <2>12, <2>13, <2>14, <2>15 DEF Next
<1> QED
  BY <1>0, <1>a, <1>b DEF Shape
-----------------------------------------------------------------------------
LEMMA NextAppliedRouteEnabled ==
  ASSUME Mut # "M_DECIDEONLY", Mut # "M_NOCONSUME", AppliedRouteEnabled, [Next]_vars
  PROVE  AppliedRouteEnabled'
<1>1. CASE UNCHANGED applied
  BY <1>1 DEF AppliedRouteEnabled
<1>2. ASSUME NEW r \in pending, Apply(r) PROVE AppliedRouteEnabled'
  <2>1. CASE RouteOK(r, TRUE)
    <3>1. RouteOK(r, FALSE)
      BY <2>1 DEF RouteOK
    <3>2. applied' = applied \cup {[edge |-> r.edge, at |-> idx + 1, ok |-> RouteOK(r, FALSE),
                                    basis |-> r.basis, now |-> attr["s"]]}
      BY <1>2, <2>1 DEF Apply
    <3> QED
      BY <3>1, <3>2 DEF AppliedRouteEnabled
  <2>2. CASE ~RouteOK(r, TRUE)
    <3>1. UNCHANGED applied
      BY <1>2, <2>2 DEF Apply
    <3> QED
      BY <3>1 DEF AppliedRouteEnabled
  <2> QED
    BY <2>1, <2>2
<1> QED
  BY <1>1, <1>2, AppliedStep

THEOREM AppliedRouteEnabledAlways ==
  ASSUME Mut # "M_DECIDEONLY", Mut # "M_NOCONSUME"
  PROVE  Spec => []AppliedRouteEnabled
<1>1. AppliedRouteEnabled /\ [Next]_vars => AppliedRouteEnabled'
  BY NextAppliedRouteEnabled
<1>2. Init => AppliedRouteEnabled
  BY DEF Init, AppliedRouteEnabled
<1> QED
  BY <1>1, <1>2, PTL DEF Spec
-----------------------------------------------------------------------------
LEMMA NextAtMostOne ==
  ASSUME Mut # "M_DECIDEONLY", Mut # "M_NOCONSUME", TypeOK, AtMostOne, [Next]_vars
  PROVE  AtMostOne'
<1>1. consumed => consumed'
  <2>1. CASE UNCHANGED vars
    BY <2>1 DEF vars, route
  <2>2. ASSUME NEW r \in pending, Apply(r) PROVE consumed => consumed'
    BY <2>2 DEF Apply
  <2>3. CASE DecisionLapse
    BY <2>3 DEF DecisionLapse
  <2>4. ASSUME \/ \E st \in Seatings : Promote(st)
               \/ \E n \in Nodes : Grant(n) \/ Fail(n) \/ Cover(n) \/ Finding(n)
               \/ \E n \in Nodes, s \in Sts, l \in Lbls : End(n, s, l)
               \/ \E n \in Nodes, s \in Sts : Rewrite(n, s)
               \/ \E e \in Chosen : Decide(e)
               \/ \E e \in Computed : Fire(e)
               \/ OrchLapse \/ Fence \/ Settle
        PROVE  UNCHANGED consumed
    BY <2>4 DEF Promote, Grant, Fail, Cover, Finding, End, Rewrite, Decide, Fire, OrchLapse, Fence, Settle, route
  <2> QED
    BY <2>1, <2>2, <2>3, <2>4 DEF Next
<1>2. CASE UNCHANGED applied
  BY <1>1, <1>2 DEF AtMostOne
<1>3. ASSUME NEW r \in pending, Apply(r) PROVE AtMostOne'
  <2>1. CASE RouteOK(r, TRUE)
    <3> DEFINE w == [edge |-> r.edge, at |-> idx + 1, ok |-> RouteOK(r, FALSE),
                     basis |-> r.basis, now |-> attr["s"]]
    <3>1. /\ applied' = applied \cup {w}
          /\ consumed' = TRUE
      BY <1>3, <2>1 DEF Apply
    <3>2. ~consumed
      BY <2>1 DEF RouteOK
    <3>3. applied = {}
      BY <3>2 DEF AtMostOne
    <3>4. applied' = {w}
      BY <3>1, <3>3
    <3>5. w \in AppRec
      <4>1. r \in PendRec /\ attr["s"] \in AttrRec
        BY DEF TypeOK, Nodes
      <4>2. RouteOK(r, FALSE) \in BOOLEAN
        BY DEF RouteOK
      <4> QED
        BY <4>1, <4>2 DEF TypeOK, AppRec, PendRec
    <3> QED
      BY <3>1, <3>4, <3>5 DEF AtMostOne
  <2>2. CASE ~RouteOK(r, TRUE)
    <3>1. UNCHANGED <<applied, consumed>>
      BY <1>3, <2>2 DEF Apply
    <3> QED
      BY <3>1 DEF AtMostOne
  <2> QED
    BY <2>1, <2>2
<1> QED
  BY <1>2, <1>3, AppliedStep

LEMMA AtMostOneBound ==
  ASSUME AtMostOne
  PROVE  OneRoutePerDecision
<1>1. CASE applied = {}
  BY <1>1, FS_EmptySet DEF OneRoutePerDecision
<1>2. ASSUME NEW x \in AppRec, applied = {x} PROVE OneRoutePerDecision
  BY <1>2, FS_Singleton DEF OneRoutePerDecision
<1> QED
  BY <1>1, <1>2 DEF AtMostOne

THEOREM OneRoutePerDecisionAlways ==
  ASSUME Mut # "M_DECIDEONLY", Mut # "M_NOCONSUME"
  PROVE  Spec => []OneRoutePerDecision
<1>1. Shape /\ AtMostOne /\ [Next]_vars => Shape' /\ AtMostOne'
  BY NextShape, NextAtMostOne DEF Shape
<1>2. Init => Shape /\ AtMostOne
  BY InitShape DEF Init, AtMostOne
<1>3. AtMostOne => OneRoutePerDecision
  BY AtMostOneBound
<1> QED
  BY <1>1, <1>2, <1>3, PTL DEF Spec
-----------------------------------------------------------------------------
LEMMA NextFindingPrecedes ==
  ASSUME Mut # "M_DECIDEONLY", Shape, FindingPrecedesNoRoute, [Next]_vars
  PROVE  FindingPrecedesNoRoute'
<1>0. /\ TypeOK /\ NoFindingNoAt /\ AppliedBound
      /\ \A e \in Edges : Anc[Src[e]] \cup {Src[e]} \subseteq Nodes
      /\ Chosen \subseteq Edges
  BY EdgeFacts DEF Shape
<1>1. CASE UNCHANGED <<applied, findingAt>>
  BY <1>1 DEF FindingPrecedesNoRoute
<1>2. ASSUME NEW n \in Nodes, Finding(n) PROVE FindingPrecedesNoRoute'
  <2> SUFFICES ASSUME NEW r \in applied', NEW b \in Anc[Src[r.edge]] \cup {Src[r.edge]}
               PROVE  findingAt'[b] = 0 \/ findingAt'[b] > r.at
    BY DEF FindingPrecedesNoRoute
  <2>1. UNCHANGED applied /\ findingAt' = [findingAt EXCEPT ![n] = idx + 1]
    BY <1>2 DEF Finding, route
  <2>2. r \in applied /\ r \in AppRec /\ r.edge \in Edges /\ r.at \in Nat /\ r.at <= idx /\ b \in Nodes
    BY <1>0, <2>1 DEF TypeOK, AppRec, AppliedBound
  <2>3. CASE b = n
    BY <1>0, <2>1, <2>2, <2>3 DEF TypeOK
  <2>4. CASE b # n
    <3>1. findingAt'[b] = findingAt[b]
      BY <1>0, <2>1, <2>2, <2>4 DEF TypeOK
    <3>2. findingAt[b] = 0 \/ findingAt[b] > r.at
      BY <2>2 DEF FindingPrecedesNoRoute
    <3> QED
      BY <3>1, <3>2
  <2> QED
    BY <2>3, <2>4
<1>3. ASSUME NEW r \in pending, Apply(r) PROVE FindingPrecedesNoRoute'
  <2>1. CASE RouteOK(r, TRUE)
    <3> DEFINE w == [edge |-> r.edge, at |-> idx + 1, ok |-> RouteOK(r, FALSE),
                     basis |-> r.basis, now |-> attr["s"]]
    <3>1. applied' = applied \cup {w} /\ UNCHANGED findingAt
      BY <1>3, <2>1 DEF Apply
    <3>2. Unfound(r.edge)
      BY <2>1 DEF RouteOK, Enabled
    <3>3. r.edge \in Edges
      BY <1>0 DEF TypeOK, PendRec
    <3>4. \A b \in Anc[Src[r.edge]] \cup {Src[r.edge]} : findingAt[b] = 0
      BY <1>0, <3>2, <3>3 DEF Unfound, NoFindingNoAt
    <3> SUFFICES ASSUME NEW q \in applied', NEW b \in Anc[Src[q.edge]] \cup {Src[q.edge]}
                 PROVE  findingAt'[b] = 0 \/ findingAt'[b] > q.at
      BY DEF FindingPrecedesNoRoute
    <3>5. CASE q \in applied
      BY <3>1, <3>5 DEF FindingPrecedesNoRoute
    <3>6. CASE q = w
      <4>1. q.edge = r.edge
        BY <3>6
      <4> QED
        BY <3>1, <3>4, <4>1
    <3> QED
      BY <3>1, <3>5, <3>6
  <2>2. CASE ~RouteOK(r, TRUE)
    <3>1. UNCHANGED <<applied, findingAt>>
      BY <1>3, <2>2 DEF Apply
    <3> QED
      BY <3>1 DEF FindingPrecedesNoRoute
  <2> QED
    BY <2>1, <2>2
<1>4. ASSUME \/ \E st \in Seatings : Promote(st)
             \/ \E n \in Nodes : Grant(n) \/ Fail(n) \/ Cover(n)
             \/ \E n \in Nodes, s \in Sts, l \in Lbls : End(n, s, l)
             \/ \E n \in Nodes, s \in Sts : Rewrite(n, s)
             \/ \E e \in Chosen : Decide(e)
             \/ \E e \in Computed : Fire(e)
             \/ OrchLapse \/ DecisionLapse \/ Fence \/ Settle
      PROVE  UNCHANGED <<applied, findingAt>>
  BY <1>4 DEF Promote, Grant, Fail, Cover, End, Rewrite, Decide, Fire, OrchLapse, DecisionLapse, Fence, Settle,
              route, obsV
<1>5. CASE UNCHANGED vars
  BY <1>1, <1>5 DEF vars, route, obsV
<1> QED
  BY <1>1, <1>2, <1>3, <1>4, <1>5 DEF Next

THEOREM FindingPrecedesNoRouteAlways ==
  ASSUME Mut # "M_DECIDEONLY"
  PROVE  Spec => []FindingPrecedesNoRoute
<1>1. Shape /\ FindingPrecedesNoRoute /\ [Next]_vars => Shape' /\ FindingPrecedesNoRoute'
  BY NextShape, NextFindingPrecedes
<1>2. Init => Shape /\ FindingPrecedesNoRoute
  BY InitShape DEF Init, FindingPrecedesNoRoute
<1> QED
  BY <1>1, <1>2, PTL DEF Spec
-----------------------------------------------------------------------------
LEMMA NextChosenOnlyByRoute ==
  ASSUME Mut # "M_DEFAULT", TypeOK, ChosenOnlyByRoute, [Next]_vars
  PROVE  ChosenOnlyByRoute'
<1>0. /\ Chosen \subseteq Edges /\ Computed \subseteq Edges
      /\ \A e \in Edges : Dst[e] \in Nodes
      /\ \A e \in Computed : Dst[e] = "j"
      /\ \A e \in Chosen : Dst[e] # "j"
  BY EdgeFacts
<1>1. CASE UNCHANGED <<activatedBy, routedOnTaint, uncoveredAct>>
  BY <1>1 DEF ChosenOnlyByRoute
<1>2. ASSUME NEW r \in pending, Apply(r) PROVE ChosenOnlyByRoute'
  <2>1. r.edge \in Chosen /\ r.edge \in Edges
    BY <1>0 DEF TypeOK, PendRec
  <2>2. "route" \in Hows
    BY DEF Hows
  <2>3. CASE Mut = "M_DECIDEONLY" \/ RouteOK(r, TRUE)
    <3>1. Activate(r.edge, "route")
      BY <1>2, <2>3 DEF Apply
    <3>2. /\ \A n \in Nodes : n # Dst[r.edge] => activatedBy'[n] = activatedBy[n]
          /\ activatedBy'[Dst[r.edge]] = "route" \/ activatedBy'[Dst[r.edge]] = activatedBy[Dst[r.edge]]
      BY <2>1, <2>2, <3>1, ActivateShape
    <3> SUFFICES ASSUME NEW e \in Chosen PROVE activatedBy'[Dst[e]] \in {"none", "route"}
      BY DEF ChosenOnlyByRoute
    <3>3. Dst[e] \in Nodes
      BY <1>0
    <3> QED
      BY <3>2, <3>3 DEF ChosenOnlyByRoute
  <2>4. CASE ~(Mut = "M_DECIDEONLY" \/ RouteOK(r, TRUE))
    <3>1. UNCHANGED activatedBy
      BY <1>2, <2>4 DEF Apply, act
    <3> QED
      BY <3>1 DEF ChosenOnlyByRoute
  <2> QED
    BY <2>3, <2>4
<1>3. ASSUME NEW e \in Computed, Fire(e) PROVE ChosenOnlyByRoute'
  <2>1. e \in Edges /\ "computed" \in Hows
    BY <1>0 DEF Hows
  <2>2. Activate(e, "computed")
    BY <1>3 DEF Fire
  <2>3. \A n \in Nodes : n # Dst[e] => activatedBy'[n] = activatedBy[n]
    BY <2>1, <2>2, ActivateShape
  <2> SUFFICES ASSUME NEW c \in Chosen PROVE activatedBy'[Dst[c]] \in {"none", "route"}
    BY DEF ChosenOnlyByRoute
  <2>4. Dst[c] \in Nodes /\ Dst[c] # Dst[e]
    BY <1>0
  <2> QED
    BY <2>3, <2>4 DEF ChosenOnlyByRoute
<1>4. CASE DecisionLapse
  <2>1. UNCHANGED activatedBy
    BY <1>4 DEF DecisionLapse, act
  <2> QED
    BY <2>1 DEF ChosenOnlyByRoute
<1> QED
  BY <1>1, <1>2, <1>3, <1>4, ActStep

THEOREM ChosenOnlyByRouteAlways ==
  ASSUME Mut # "M_DEFAULT"
  PROVE  Spec => []ChosenOnlyByRoute
<1>1. TypeOK /\ ChosenOnlyByRoute /\ [Next]_vars => TypeOK' /\ ChosenOnlyByRoute'
  BY NextTypeOK, NextChosenOnlyByRoute
<1>2. Init => TypeOK /\ ChosenOnlyByRoute
  BY InitTypeOK, EdgeFacts DEF Init, ChosenOnlyByRoute
<1> QED
  BY <1>1, <1>2, PTL DEF Spec
-----------------------------------------------------------------------------
LEMMA NextInvC ==
  ASSUME Mut # "M_UNCOVERED", Shape, InvC, [Next]_vars
  PROVE  InvC'
<1>0. /\ TypeOK /\ EdgeAfterCoverage /\ PendingCovered
      /\ Chosen \subseteq Edges /\ Computed \subseteq Edges
      /\ \A e \in Edges : Src[e] \in Nodes /\ Dst[e] \in Nodes
  BY EdgeFacts DEF Shape, InvC
<1>m. \A n \in Nodes : covered[n] => covered'[n]
  <2>1. CASE UNCHANGED vars
    BY <2>1 DEF vars, nodeV
  <2>2. ASSUME NEW n \in Nodes, Cover(n) PROVE \A m \in Nodes : covered[m] => covered'[m]
    BY <1>0, <2>2 DEF Cover, TypeOK
  <2>3. ASSUME \/ \E st \in Seatings : Promote(st)
               \/ \E n \in Nodes : Grant(n) \/ Fail(n) \/ Finding(n)
               \/ \E n \in Nodes, s \in Sts, l \in Lbls : End(n, s, l)
               \/ \E n \in Nodes, s \in Sts : Rewrite(n, s)
               \/ \E e \in Chosen : Decide(e)
               \/ \E r \in pending : Apply(r)
               \/ \E e \in Computed : Fire(e)
               \/ OrchLapse \/ DecisionLapse \/ Fence \/ Settle
        PROVE  UNCHANGED covered
    BY <2>3 DEF Promote, Grant, Fail, Finding, End, Rewrite, Decide, Apply, Fire, OrchLapse, DecisionLapse, Fence,
                Settle, nodeV
  <2> QED
    BY <2>1, <2>2, <2>3 DEF Next
<1>u. EdgeAfterCoverage'
  <2>1. CASE UNCHANGED <<activatedBy, routedOnTaint, uncoveredAct>>
    BY <1>0, <2>1 DEF EdgeAfterCoverage
  <2>2. ASSUME NEW r \in pending, Apply(r) PROVE EdgeAfterCoverage'
    <3>1. r.edge \in Edges /\ covered[Src[r.edge]] /\ "route" \in Hows
      BY <1>0 DEF TypeOK, PendRec, PendingCovered, Hows
    <3>2. CASE Mut = "M_DECIDEONLY" \/ RouteOK(r, TRUE)
      <4>1. Activate(r.edge, "route")
        BY <2>2, <3>2 DEF Apply
      <4>2. /\ \A n \in Nodes : n # Dst[r.edge] => uncoveredAct'[n] = uncoveredAct[n]
            /\ uncoveredAct'[Dst[r.edge]] = ~covered[Src[r.edge]] \/ uncoveredAct'[Dst[r.edge]] = uncoveredAct[Dst[r.edge]]
        BY <1>0, <3>1, <4>1, ActivateShape
      <4> QED
        BY <1>0, <3>1, <4>2 DEF EdgeAfterCoverage
    <3>3. CASE ~(Mut = "M_DECIDEONLY" \/ RouteOK(r, TRUE))
      <4>1. UNCHANGED uncoveredAct
        BY <2>2, <3>3 DEF Apply, act
      <4> QED
        BY <1>0, <4>1 DEF EdgeAfterCoverage
    <3> QED
      BY <3>2, <3>3
  <2>3. ASSUME NEW e \in Computed, Fire(e) PROVE EdgeAfterCoverage'
    <3>1. e \in Edges /\ "computed" \in Hows /\ Activate(e, "computed") /\ covered[Src[e]]
      BY <1>0, <2>3 DEF Fire, Enabled, CoveredOK, Hows
    <3>2. /\ \A n \in Nodes : n # Dst[e] => uncoveredAct'[n] = uncoveredAct[n]
          /\ uncoveredAct'[Dst[e]] = ~covered[Src[e]] \/ uncoveredAct'[Dst[e]] = uncoveredAct[Dst[e]]
      BY <1>0, <3>1, ActivateShape
    <3> QED
      BY <1>0, <3>1, <3>2 DEF EdgeAfterCoverage
  <2>4. CASE DecisionLapse
    <3>1. CASE Mut = "M_DEFAULT" /\ \E e \in Chosen : Enabled(e)
      <4> DEFINE ch == CHOOSE x \in Chosen : Enabled(x)
      <4>1. ch \in Chosen /\ Enabled(ch)
        BY <3>1, DefaultEdge
      <4>2. ch \in Edges /\ "default" \in Hows /\ covered[Src[ch]]
        BY <1>0, <4>1 DEF Enabled, CoveredOK, Hows
      <4>3. Activate(ch, "default")
        BY <2>4, <3>1 DEF DecisionLapse
      <4>4. /\ \A n \in Nodes : n # Dst[ch] => uncoveredAct'[n] = uncoveredAct[n]
            /\ uncoveredAct'[Dst[ch]] = ~covered[Src[ch]] \/ uncoveredAct'[Dst[ch]] = uncoveredAct[Dst[ch]]
        BY <1>0, <4>2, <4>3, ActivateShape
      <4> QED
        BY <1>0, <4>2, <4>4 DEF EdgeAfterCoverage
    <3>2. CASE ~(Mut = "M_DEFAULT" /\ \E e \in Chosen : Enabled(e))
      <4>1. UNCHANGED uncoveredAct
        BY <2>4, <3>2 DEF DecisionLapse, act
      <4> QED
        BY <1>0, <4>1 DEF EdgeAfterCoverage
    <3> QED
      BY <3>1, <3>2
  <2> QED
    BY <2>1, <2>2, <2>3, <2>4, ActStep
<1>p. PendingCovered'
  <2> SUFFICES ASSUME NEW r \in pending' PROVE covered'[Src[r.edge]]
    BY DEF PendingCovered
  <2>1. CASE UNCHANGED vars
    BY <1>0, <2>1 DEF vars, route, nodeV, PendingCovered
  <2>2. ASSUME NEW e \in Chosen, Decide(e) PROVE covered'[Src[r.edge]]
    <3>1. /\ pending' = pending \cup {[edge |-> e, ep |-> epoch, basis |-> attr["s"]]}
          /\ UNCHANGED covered
          /\ covered[Src[e]]
      BY <2>2 DEF Decide, RouteOK, Enabled, CoveredOK, nodeV
    <3> QED
      BY <1>0, <3>1 DEF PendingCovered
  <2>3. ASSUME NEW q \in pending, Apply(q) PROVE covered'[Src[r.edge]]
    <3>1. pending' = pending \ {q} /\ UNCHANGED covered
      BY <2>3 DEF Apply
    <3> QED
      BY <1>0, <3>1 DEF PendingCovered
  <2>4. ASSUME \/ \E st \in Seatings : Promote(st)
               \/ \E n \in Nodes : Grant(n) \/ Fail(n) \/ Cover(n) \/ Finding(n)
               \/ \E n \in Nodes, s \in Sts, l \in Lbls : End(n, s, l)
               \/ \E n \in Nodes, s \in Sts : Rewrite(n, s)
               \/ \E e \in Computed : Fire(e)
               \/ OrchLapse \/ DecisionLapse \/ Fence \/ Settle
        PROVE  UNCHANGED pending
    BY <2>4 DEF Promote, Grant, Fail, Cover, Finding, End, Rewrite, Fire, OrchLapse, DecisionLapse, Fence, Settle, route
  <2>5. ASSUME UNCHANGED pending PROVE covered'[Src[r.edge]]
    <3>1. r \in pending /\ r.edge \in Edges
      BY <2>5, <1>0 DEF TypeOK, PendRec
    <3>2. covered[Src[r.edge]] /\ Src[r.edge] \in Nodes
      BY <1>0, <3>1 DEF PendingCovered
    <3> QED
      BY <1>m, <3>2
  <2> QED
    BY <2>1, <2>2, <2>3, <2>4, <2>5 DEF Next
<1> QED
  BY <1>u, <1>p DEF InvC

THEOREM EdgeAfterCoverageAlways ==
  ASSUME Mut # "M_UNCOVERED"
  PROVE  Spec => []EdgeAfterCoverage
<1>1. Shape /\ InvC /\ [Next]_vars => Shape' /\ InvC'
  BY NextShape, NextInvC
<1>2. Init => Shape /\ InvC
  BY InitShape DEF Init, InvC, EdgeAfterCoverage, PendingCovered
<1>3. InvC => EdgeAfterCoverage
  BY DEF InvC
<1> QED
  BY <1>1, <1>2, <1>3, PTL DEF Spec
-----------------------------------------------------------------------------
LEMMA NextInvT ==
  ASSUME Mut # "M_NOTAINT", Shape, InvT, [Next]_vars
  PROVE  InvT'
<1>0. /\ TypeOK /\ PendingEnded /\ BeforePromotion /\ TaintedNeverOutward /\ PendingTrusted
      /\ Chosen \subseteq Edges /\ Computed \subseteq Edges
      /\ \A e \in Edges : Src[e] \in Nodes /\ Dst[e] \in Nodes
      /\ \A e \in Computed : Dst[e] = "j"
      /\ Outward = {"c"}
  BY EdgeFacts DEF Shape, InvT
<1>1. PendingTrusted'
  <2> SUFFICES ASSUME NEW r \in pending'
               PROVE  ~(Dst[r.edge] \in Outward /\ attr'[Src[r.edge]].lbl = "untrusted")
    BY DEF PendingTrusted
  <2>u. ASSUME UNCHANGED <<pending, attr>>
        PROVE  ~(Dst[r.edge] \in Outward /\ attr'[Src[r.edge]].lbl = "untrusted")
    BY <1>0, <2>u DEF PendingTrusted
  <2>1. CASE UNCHANGED vars
    BY <2>1, <2>u DEF vars, route, nodeV
  <2>2. ASSUME NEW e \in Chosen, Decide(e)
        PROVE  ~(Dst[r.edge] \in Outward /\ attr'[Src[r.edge]].lbl = "untrusted")
    <3>1. /\ pending' = pending \cup {[edge |-> e, ep |-> epoch, basis |-> attr["s"]]}
          /\ UNCHANGED attr
          /\ ~(Dst[e] \in Outward /\ attr[Src[e]].lbl = "untrusted")
      BY <2>2 DEF Decide, RouteOK, Enabled, TaintOK, nodeV
    <3> QED
      BY <1>0, <3>1 DEF PendingTrusted
  <2>3. ASSUME NEW q \in pending, Apply(q)
        PROVE  ~(Dst[r.edge] \in Outward /\ attr'[Src[r.edge]].lbl = "untrusted")
    <3>1. pending' = pending \ {q} /\ UNCHANGED attr
      BY <2>3 DEF Apply
    <3> QED
      BY <1>0, <3>1 DEF PendingTrusted
  <2>4. ASSUME NEW n \in Nodes, NEW s \in Sts, NEW l \in Lbls, End(n, s, l)
        PROVE  ~(Dst[r.edge] \in Outward /\ attr'[Src[r.edge]].lbl = "untrusted")
    <3>1. /\ UNCHANGED pending
          /\ status[n] = "running"
          /\ attr' = [attr EXCEPT ![n] = [st |-> s, lbl |-> l]]
      BY <2>4 DEF End, route
    <3>2. r \in pending /\ r.edge \in Edges /\ status[Src[r.edge]] = "ended"
      BY <1>0, <3>1 DEF TypeOK, PendRec, PendingEnded
    <3>3. Src[r.edge] # n /\ Src[r.edge] \in Nodes
      BY <1>0, <3>1, <3>2
    <3>4. attr'[Src[r.edge]] = attr[Src[r.edge]]
      BY <1>0, <3>1, <3>3 DEF TypeOK
    <3> QED
      BY <1>0, <3>2, <3>4 DEF PendingTrusted
  <2>5. ASSUME NEW n \in Nodes, NEW s \in Sts, Rewrite(n, s)
        PROVE  ~(Dst[r.edge] \in Outward /\ attr'[Src[r.edge]].lbl = "untrusted")
    <3>1. UNCHANGED pending /\ attr' = [attr EXCEPT ![n].st = s]
      BY <2>5 DEF Rewrite, route
    <3>2. r \in pending /\ r.edge \in Edges /\ Src[r.edge] \in Nodes
      BY <1>0, <3>1 DEF TypeOK, PendRec
    <3>3. attr'[Src[r.edge]].lbl = attr[Src[r.edge]].lbl
      <4>1. attr[n] \in AttrRec /\ attr[Src[r.edge]] \in AttrRec
        BY <1>0, <3>2 DEF TypeOK
      <4> QED
        BY <1>0, <3>1, <3>2, <4>1 DEF TypeOK, AttrRec
    <3> QED
      BY <1>0, <3>2, <3>3 DEF PendingTrusted
  <2>6. ASSUME \/ \E st \in Seatings : Promote(st)
               \/ \E n \in Nodes : Grant(n) \/ Fail(n) \/ Cover(n) \/ Finding(n)
               \/ \E e \in Computed : Fire(e)
               \/ OrchLapse \/ DecisionLapse \/ Fence \/ Settle
        PROVE  ~(Dst[r.edge] \in Outward /\ attr'[Src[r.edge]].lbl = "untrusted")
    <3>1. UNCHANGED <<pending, attr>>
      BY <2>6 DEF Promote, Grant, Fail, Cover, Finding, Fire, OrchLapse, DecisionLapse, Fence, Settle, route, nodeV
    <3> QED
      BY <3>1, <2>u
  <2> QED
    BY <2>1, <2>2, <2>3, <2>4, <2>5, <2>6 DEF Next
<1>2. TaintedNeverOutward'
  <2>1. CASE UNCHANGED <<activatedBy, routedOnTaint, uncoveredAct>>
    BY <1>0, <2>1 DEF TaintedNeverOutward
  <2>2. ASSUME NEW r \in pending, Apply(r) PROVE TaintedNeverOutward'
    <3>1. r.edge \in Edges /\ "route" \in Hows /\ ~(Dst[r.edge] \in Outward /\ attr[Src[r.edge]].lbl = "untrusted")
      BY <1>0 DEF TypeOK, PendRec, PendingTrusted, Hows
    <3>2. CASE Mut = "M_DECIDEONLY" \/ RouteOK(r, TRUE)
      <4>1. Activate(r.edge, "route")
        BY <2>2, <3>2 DEF Apply
      <4>2. /\ "c" # Dst[r.edge] => /\ activatedBy'["c"] = activatedBy["c"]
                                      /\ routedOnTaint'["c"] = routedOnTaint["c"]
            /\ \/ activatedBy'[Dst[r.edge]] = "route" /\ routedOnTaint'[Dst[r.edge]] = (attr[Src[r.edge]].lbl = "untrusted")
               \/ activatedBy'[Dst[r.edge]] = activatedBy[Dst[r.edge]] /\ routedOnTaint'[Dst[r.edge]] = routedOnTaint[Dst[r.edge]]
        BY <1>0, <3>1, <4>1, ActivateShape DEF Nodes
      <4> QED
        BY <1>0, <3>1, <4>2 DEF TaintedNeverOutward
    <3>3. CASE ~(Mut = "M_DECIDEONLY" \/ RouteOK(r, TRUE))
      <4>1. UNCHANGED <<activatedBy, routedOnTaint>>
        BY <2>2, <3>3 DEF Apply, act
      <4> QED
        BY <1>0, <4>1 DEF TaintedNeverOutward
    <3> QED
      BY <3>2, <3>3
  <2>3. ASSUME NEW e \in Computed, Fire(e) PROVE TaintedNeverOutward'
    <3>1. e \in Edges /\ "computed" \in Hows /\ Activate(e, "computed") /\ Dst[e] # "c"
      BY <1>0, <2>3 DEF Fire, Hows
    <3>2. activatedBy'["c"] = activatedBy["c"] /\ routedOnTaint'["c"] = routedOnTaint["c"]
      BY <1>0, <3>1, ActivateShape DEF Nodes
    <3> QED
      BY <1>0, <3>2 DEF TaintedNeverOutward
  <2>4. CASE DecisionLapse
    <3>1. CASE Mut = "M_DEFAULT" /\ \E e \in Chosen : Enabled(e)
      <4> DEFINE ch == CHOOSE x \in Chosen : Enabled(x)
      <4>1. ch \in Chosen /\ Enabled(ch)
        BY <3>1, DefaultEdge
      <4>2. /\ ch \in Edges /\ "default" \in Hows
            /\ ~(Dst[ch] \in Outward /\ attr[Src[ch]].lbl = "untrusted")
        BY <1>0, <4>1 DEF Enabled, TaintOK, Hows
      <4>3. Activate(ch, "default")
        BY <2>4, <3>1 DEF DecisionLapse
      <4>4. /\ "c" # Dst[ch] => /\ activatedBy'["c"] = activatedBy["c"]
                                 /\ routedOnTaint'["c"] = routedOnTaint["c"]
            /\ \/ activatedBy'[Dst[ch]] = "default" /\ routedOnTaint'[Dst[ch]] = (attr[Src[ch]].lbl = "untrusted")
               \/ activatedBy'[Dst[ch]] = activatedBy[Dst[ch]] /\ routedOnTaint'[Dst[ch]] = routedOnTaint[Dst[ch]]
        BY <1>0, <4>2, <4>3, ActivateShape DEF Nodes
      <4> QED
        BY <1>0, <4>2, <4>4 DEF TaintedNeverOutward
    <3>2. CASE ~(Mut = "M_DEFAULT" /\ \E e \in Chosen : Enabled(e))
      <4>1. UNCHANGED <<activatedBy, routedOnTaint>>
        BY <2>4, <3>2 DEF DecisionLapse, act
      <4> QED
        BY <1>0, <4>1 DEF TaintedNeverOutward
    <3> QED
      BY <3>1, <3>2
  <2> QED
    BY <2>1, <2>2, <2>3, <2>4, ActStep
<1> QED
  BY <1>1, <1>2 DEF InvT

THEOREM TaintedNeverOutwardAlways ==
  ASSUME Mut # "M_NOTAINT"
  PROVE  Spec => []TaintedNeverOutward
<1>1. Shape /\ InvT /\ [Next]_vars => Shape' /\ InvT'
  BY NextShape, NextInvT
<1>2. Init => Shape /\ InvT
  BY InitShape, EdgeFacts DEF Init, InvT, TaintedNeverOutward, PendingTrusted, Outward, Nodes
<1>3. InvT => TaintedNeverOutward
  BY DEF InvT
<1> QED
  BY <1>1, <1>2, <1>3, PTL DEF Spec
-----------------------------------------------------------------------------
LEMMA NextGrantUnderPromotion ==
  ASSUME Mut # "M_GRANTANYEPOCH", TypeOK, GrantUnderPromotion, [Next]_vars
  PROVE  GrantUnderPromotion'
<1>1. ASSUME NEW n \in Nodes, Grant(n) PROVE GrantUnderPromotion'
  <2>1. CASE epoch = PE
    <3>1. grantEpoch' = [grantEpoch EXCEPT ![n] = epoch]
      BY <1>1, <2>1 DEF Grant
    <3> QED
      BY <2>1, <3>1 DEF GrantUnderPromotion, TypeOK
  <2>2. CASE epoch # PE
    <3>1. UNCHANGED grantEpoch
      BY <1>1, <2>2 DEF Grant
    <3> QED
      BY <3>1 DEF GrantUnderPromotion
  <2> QED
    BY <2>1, <2>2
<1>2. CASE UNCHANGED grantEpoch
  BY <1>2 DEF GrantUnderPromotion
<1>3. ASSUME \/ \E st \in Seatings : Promote(st)
             \/ \E n \in Nodes : Fail(n) \/ Cover(n) \/ Finding(n)
             \/ \E n \in Nodes, s \in Sts, l \in Lbls : End(n, s, l)
             \/ \E n \in Nodes, s \in Sts : Rewrite(n, s)
             \/ \E e \in Chosen : Decide(e)
             \/ \E r \in pending : Apply(r)
             \/ \E e \in Computed : Fire(e)
             \/ OrchLapse \/ DecisionLapse \/ Fence \/ Settle
      PROVE  UNCHANGED grantEpoch
  BY <1>3 DEF Promote, Fail, Cover, Finding, End, Rewrite, Decide, Apply, Fire, OrchLapse, DecisionLapse, Fence,
              Settle, nodeV
<1>4. CASE UNCHANGED vars
  BY <1>4, <1>2 DEF vars, nodeV
<1> QED
  BY <1>1, <1>2, <1>3, <1>4 DEF Next

THEOREM GrantUnderPromotionAlways ==
  ASSUME Mut # "M_GRANTANYEPOCH"
  PROVE  Spec => []GrantUnderPromotion
<1>1. TypeOK /\ GrantUnderPromotion /\ [Next]_vars => TypeOK' /\ GrantUnderPromotion'
  BY NextTypeOK, NextGrantUnderPromotion
<1>2. Init => TypeOK /\ GrantUnderPromotion
  BY InitTypeOK DEF Init, GrantUnderPromotion
<1> QED
  BY <1>1, <1>2, PTL DEF Spec
-----------------------------------------------------------------------------
LEMMA NextPromotedAlternates ==
  ASSUME Mut # "M_NOLINEAGE", PromotedAlternates, [Next]_vars
  PROVE  PromotedAlternates'
<1>1. ASSUME NEW st \in Seatings, Promote(st) PROVE PromotedAlternates'
  BY <1>1 DEF Promote, PromotedAlternates
<1>2. CASE UNCHANGED <<promoted, seatOK>>
  BY <1>2 DEF PromotedAlternates
<1>3. ASSUME \/ \E n \in Nodes : Grant(n) \/ Fail(n) \/ Cover(n) \/ Finding(n)
             \/ \E n \in Nodes, s \in Sts, l \in Lbls : End(n, s, l)
             \/ \E n \in Nodes, s \in Sts : Rewrite(n, s)
             \/ \E e \in Chosen : Decide(e)
             \/ \E r \in pending : Apply(r)
             \/ \E e \in Computed : Fire(e)
             \/ OrchLapse \/ DecisionLapse \/ Fence \/ Settle
      PROVE  UNCHANGED <<promoted, seatOK>>
  BY <1>3 DEF Grant, Fail, Cover, Finding, End, Rewrite, Decide, Apply, Fire, OrchLapse, DecisionLapse, Fence, Settle, top
<1>4. CASE UNCHANGED vars
  BY <1>4, <1>2 DEF vars, top
<1> QED
  BY <1>1, <1>2, <1>3, <1>4 DEF Next

THEOREM PromotedAlternatesAlways ==
  ASSUME Mut # "M_NOLINEAGE"
  PROVE  Spec => []PromotedAlternates
<1>1. PromotedAlternates /\ [Next]_vars => PromotedAlternates'
  BY NextPromotedAlternates
<1>2. Init => PromotedAlternates
  BY DEF Init, PromotedAlternates
<1> QED
  BY <1>1, <1>2, PTL DEF Spec
-----------------------------------------------------------------------------
LEMMA NextCompletedOnlyBySink ==
  ASSUME Mut # "M_TIMEOUTDONE", Shape, CompletedOnlyBySink, [Next]_vars
  PROVE  CompletedOnlyBySink'
<1>0. /\ TypeOK /\ BeforePromotion /\ Sink \in Nodes
  BY EdgeFacts DEF Shape, Nodes
<1>f. status[Sink] = "ended" => status'[Sink] = "ended"
  BY <1>0, EndedFrozen
<1>1. CASE Settle
  BY <1>0, <1>1 DEF Settle, CompletedOnlyBySink, nodeV
<1>2. ASSUME \/ \E st \in Seatings : Promote(st)
             \/ \E n \in Nodes : Grant(n) \/ Fail(n) \/ Cover(n) \/ Finding(n)
             \/ \E n \in Nodes, s \in Sts, l \in Lbls : End(n, s, l)
             \/ \E n \in Nodes, s \in Sts : Rewrite(n, s)
             \/ \E e \in Chosen : Decide(e)
             \/ \E r \in pending : Apply(r)
             \/ \E e \in Computed : Fire(e)
             \/ OrchLapse \/ DecisionLapse \/ Fence
      PROVE  UNCHANGED wf
  BY <1>2 DEF Promote, Grant, Fail, Cover, Finding, End, Rewrite, Decide, Apply, Fire, OrchLapse, DecisionLapse, Fence, top
<1>3. CASE UNCHANGED vars
  BY <1>3 DEF vars, top, CompletedOnlyBySink, nodeV
<1> QED
  BY <1>f, <1>1, <1>2, <1>3 DEF Next, CompletedOnlyBySink

THEOREM CompletedOnlyBySinkAlways ==
  ASSUME Mut # "M_TIMEOUTDONE"
  PROVE  Spec => []CompletedOnlyBySink
<1>1. Shape /\ CompletedOnlyBySink /\ [Next]_vars => Shape' /\ CompletedOnlyBySink'
  BY NextShape, NextCompletedOnlyBySink
<1>2. Init => Shape /\ CompletedOnlyBySink
  BY InitShape DEF Init, CompletedOnlyBySink
<1> QED
  BY <1>1, <1>2, PTL DEF Spec
-----------------------------------------------------------------------------
LEMMA NextInvB ==
  ASSUME Mut # "M_REWRITE", Shape, InvB, [Next]_vars
  PROVE  InvB'
<1>0. /\ TypeOK /\ PendingEnded /\ BasisStable /\ PendingBasis
      /\ Chosen \subseteq Edges
      /\ \A e \in Chosen : Src[e] = "s"
      /\ "s" \in Nodes
  BY EdgeFacts DEF Shape, InvB, Nodes
<1>e. pending # {} => status["s"] = "ended"
  BY <1>0 DEF PendingEnded, TypeOK, PendRec
<1>1. CASE UNCHANGED <<attr, pending, applied>>
  BY <1>0, <1>1 DEF InvB, BasisStable, PendingBasis
<1>2. ASSUME NEW e \in Chosen, Decide(e) PROVE InvB'
  <2>1. /\ pending' = pending \cup {[edge |-> e, ep |-> epoch, basis |-> attr["s"]]}
        /\ UNCHANGED <<attr, applied>>
    BY <1>2 DEF Decide, nodeV
  <2> QED
    BY <1>0, <2>1 DEF InvB, BasisStable, PendingBasis
<1>3. ASSUME NEW r \in pending, Apply(r) PROVE InvB'
  <2>1. pending' = pending \ {r} /\ UNCHANGED attr
    BY <1>3 DEF Apply
  <2>2. r.basis = attr["s"]
    BY <1>0 DEF PendingBasis
  <2>3. PendingBasis'
    BY <1>0, <2>1 DEF PendingBasis
  <2>4. CASE Mut = "M_DECIDEONLY" \/ RouteOK(r, TRUE)
    <3>1. applied' = applied \cup {[edge |-> r.edge, at |-> idx + 1, ok |-> RouteOK(r, FALSE),
                                    basis |-> r.basis, now |-> attr["s"]]}
      BY <1>3, <2>4 DEF Apply
    <3> QED
      BY <1>0, <2>2, <2>3, <3>1 DEF InvB, BasisStable
  <2>5. CASE ~(Mut = "M_DECIDEONLY" \/ RouteOK(r, TRUE))
    <3>1. UNCHANGED applied
      BY <1>3, <2>5 DEF Apply
    <3> QED
      BY <1>0, <2>3, <3>1 DEF InvB, BasisStable
  <2> QED
    BY <2>4, <2>5
<1>4. ASSUME NEW n \in Nodes, NEW s \in Sts, NEW l \in Lbls, End(n, s, l) PROVE InvB'
  <2>1. /\ UNCHANGED <<pending, applied>>
        /\ status[n] = "running"
        /\ attr' = [attr EXCEPT ![n] = [st |-> s, lbl |-> l]]
    BY <1>4 DEF End, route
  <2>2. PendingBasis'
    <3> SUFFICES ASSUME NEW r \in pending' PROVE r.basis = attr'["s"]
      BY DEF PendingBasis
    <3>1. r \in pending /\ n # "s"
      BY <1>e, <2>1
    <3>2. attr'["s"] = attr["s"]
      BY <1>0, <2>1, <3>1 DEF TypeOK
    <3> QED
      BY <1>0, <3>1, <3>2 DEF PendingBasis
  <2> QED
    BY <1>0, <2>1, <2>2 DEF InvB, BasisStable
<1>5. ASSUME \/ \E st \in Seatings : Promote(st)
             \/ \E n \in Nodes : Grant(n) \/ Fail(n) \/ Cover(n) \/ Finding(n)
             \/ \E n \in Nodes, s \in Sts : Rewrite(n, s)
             \/ \E e \in Computed : Fire(e)
             \/ OrchLapse \/ DecisionLapse \/ Fence \/ Settle
      PROVE  UNCHANGED <<attr, pending, applied>>
  BY <1>5 DEF Promote, Grant, Fail, Cover, Finding, Rewrite, Fire, OrchLapse, DecisionLapse, Fence, Settle, route, nodeV
<1>6. CASE UNCHANGED vars
  BY <1>6, <1>1 DEF vars, route, nodeV
<1> QED
  BY <1>1, <1>2, <1>3, <1>4, <1>5, <1>6 DEF Next

THEOREM BasisStableAlways ==
  ASSUME Mut # "M_REWRITE"
  PROVE  Spec => []BasisStable
<1>1. Shape /\ InvB /\ [Next]_vars => Shape' /\ InvB'
  BY NextShape, NextInvB
<1>2. Init => Shape /\ InvB
  BY InitShape DEF Init, InvB, BasisStable, PendingBasis
<1>3. InvB => BasisStable
  BY DEF InvB
<1> QED
  BY <1>1, <1>2, <1>3, PTL DEF Spec
-----------------------------------------------------------------------------
THEOREM SafeAlways ==
  ASSUME Mut = "none"
  PROVE  Spec => []Safe
<1>1. Spec => []AppliedRouteEnabled
  BY AppliedRouteEnabledAlways
<1>2. Spec => []OneRoutePerDecision
  BY OneRoutePerDecisionAlways
<1>3. Spec => []FindingPrecedesNoRoute
  BY FindingPrecedesNoRouteAlways
<1>4. Spec => []ChosenOnlyByRoute
  BY ChosenOnlyByRouteAlways
<1>5. Spec => []EdgeAfterCoverage
  BY EdgeAfterCoverageAlways
<1>6. Spec => []TaintedNeverOutward
  BY TaintedNeverOutwardAlways
<1>7. Spec => []GrantUnderPromotion
  BY GrantUnderPromotionAlways
<1>8. Spec => []PromotedAlternates
  BY PromotedAlternatesAlways
<1>9. Spec => []CompletedOnlyBySink
  BY CompletedOnlyBySinkAlways
<1>10. Spec => []BasisStable
  BY BasisStableAlways
<1> QED
  BY <1>1, <1>2, <1>3, <1>4, <1>5, <1>6, <1>7, <1>8, <1>9, <1>10, PTL DEF Safe
-----------------------------------------------------------------------------
(* Why the mutations must fail: each lemma states, in the module's terms, the  *)
(* guard the mutation removes. The counterexamples are TLC's.                  *)

\* M_DECIDEONLY: apply takes the route whatever the checks now say.
LEMMA MutDecideOnlySkipsTheRecheck ==
  ASSUME Mut = "M_DECIDEONLY", NEW r
  PROVE  Mut = "M_DECIDEONLY" \/ RouteOK(r, TRUE)
  OBVIOUS

\* M_NOCONSUME: a consumed decision point still passes the check at apply.
LEMMA MutNoConsumeIgnoresConsumed ==
  ASSUME Mut = "M_NOCONSUME", NEW r, orchLive, epoch = r.ep, wf = "running", Enabled(r.edge)
  PROVE  RouteOK(r, TRUE)
  BY DEF RouteOK

\* M_DEFAULT: an enabled chosen edge gives the lapse an edge to take.
LEMMA MutDefaultTakesAnEdge ==
  ASSUME Mut = "M_DEFAULT", \E e \in Chosen : Enabled(e)
  PROVE  Mut = "M_DEFAULT" /\ \E e \in Chosen : Enabled(e)
  OBVIOUS

\* M_UNCOVERED: an edge is enabled with its source's coverage unread.
LEMMA MutUncoveredIgnoresCoverage ==
  ASSUME Mut = "M_UNCOVERED", NEW e
  PROVE  CoveredOK(e)
  BY DEF CoveredOK

\* M_NOTAINT: an untrusted label does not close an outward edge.
LEMMA MutNoTaintIgnoresTheLabel ==
  ASSUME Mut = "M_NOTAINT", NEW e
  PROVE  TaintOK(e)
  BY DEF TaintOK

\* M_GRANTANYEPOCH: the grant's test passes at a fenced epoch.
LEMMA MutGrantAnyEpochSkipsTheFence ==
  ASSUME Mut = "M_GRANTANYEPOCH"
  PROVE  Mut = "M_GRANTANYEPOCH" \/ epoch = PE
  OBVIOUS

\* M_NOLINEAGE: the gate passes a seating that does not alternate.
LEMMA MutNoLineagePassesTheGate ==
  ASSUME Mut = "M_NOLINEAGE", NEW st
  PROVE  Mut = "M_NOLINEAGE" \/ Alternates(st)
  OBVIOUS

\* M_TIMEOUTDONE: a failed decision is recorded as a completion.
LEMMA MutTimeoutDoneCompletes ==
  ASSUME Mut = "M_TIMEOUTDONE", decisionFailed
  PROVE  (IF Mut = "M_TIMEOUTDONE" /\ decisionFailed THEN "completed" ELSE "failed") = "completed"
  OBVIOUS

\* M_REWRITE: the rewrite is enabled for an ended node whose attribute differs.
LEMMA MutRewriteAdmitsARewrite ==
  ASSUME Mut = "M_REWRITE", NEW n, NEW s, status[n] = "ended", attr[n].st # s
  PROVE  Mut = "M_REWRITE" /\ status[n] = "ended" /\ attr[n].st # s
  OBVIOUS
=============================================================================
