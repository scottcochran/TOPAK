----------------------------- MODULE Workflow -----------------------------
(* A promoted workflow: ADR-0054 (Proposed), its ratification condition       *)
(* (§12). The workflow is a DAG promoted to Run. Its promotion carries every  *)
(* seating, so the mechanism grants each node's lease when the node becomes   *)
(* ready and no principal grants another. Every edge has a guard over typed   *)
(* attributes the mechanism lifts; a computed edge fires when its guard holds *)
(* and a chosen edge is selected by the orchestrator cell's `Route(edge)`     *)
(* among the chosen edges whose guards hold. A `Route` is decided by one      *)
(* replica and applied at its log position, and the mechanism checks run      *)
(* again at apply: a route that fails them is void.                           *)
(*                                                                             *)
(* The DAG is fixed and small:                                                 *)
(*                                                                             *)
(*        e1 (chosen, guard: s ok, clear)   e3 (computed, clear)               *)
(*     s ---------------------------------> b ----------------> j              *)
(*     |                                                        ^              *)
(*     +---------------------------------> c -------------------+              *)
(*        e2 (chosen, guard: true, handle)  e4 (computed, handle)              *)
(*                                                                             *)
(* `c` is outward: its lease reaches an outward entry. `s` is the one decision *)
(* point and `j` the sink, joined on any. The orchestrator and every worker    *)
(* are havoc: a worker ends with any status and any label, and the            *)
(* orchestrator routes any chosen edge at any moment its lease is live. A      *)
(* node's cell Observer reports coverage to its seal at some moment after it   *)
(* ends; a finding, from that Observer or a correlator, may land on any node   *)
(* that has started at any moment, coverage or not; and the rules epoch may be *)
(* fenced once.                                                                *)
(*                                                                             *)
(*   AppliedRouteEnabled    every applied Route names an edge enabled in the   *)
(*                          state at its apply position                        *)
(*   OneRoutePerDecision    a decision point is consumed at most once          *)
(*   FindingPrecedesNoRoute no Route applies after a finding against its       *)
(*                          source or an ancestor has been ordered             *)
(*   ChosenOnlyByRoute      a chosen edge's target is activated only by an     *)
(*                          applied Route: a lapsed orchestrator takes no      *)
(*                          default edge                                       *)
(*   EdgeAfterCoverage      no node is activated by an edge whose source's     *)
(*                          round its cell Observer has not read to the seal   *)
(*   TaintedNeverOutward    no outward node is activated by an edge whose      *)
(*                          guard read an attribute labelled untrusted         *)
(*   GrantUnderPromotion    every node granted was granted under the rules     *)
(*                          epoch of the promotion                             *)
(*   PromotedAlternates     a promoted seating alternates lineages on every    *)
(*                          clear edge, and no cell's Observer shares its      *)
(*                          Thinker's lineage                                  *)
(*   CompletedOnlyBySink    a workflow completes only when its sink has ended  *)
(*   BasisStable            what an applied Route was decided on is what holds *)
(*                          when it applies                                    *)
(*                                                                             *)
(* Not modelled: more than one decision point; multi-select; joins on all; Run *)
(* admits inside a node's round (RunCoupling.tla, Labels.tla); attestation at  *)
(* grant (Confinement_A1.tla); the orchestrator cell's own seating and its     *)
(* successor rounds; lineage beyond two values; erasure. Deadlock is not       *)
(* checked: a workflow may stall, and stalling is safe.                        *)
(*                                                                             *)
(* Mut = "none":            ADR-0054 as drafted.                               *)
(* Mut = "M_DECIDEONLY":    the mechanism checks run at decide and not again   *)
(*                          at apply.                                          *)
(* Mut = "M_NOCONSUME":     apply does not check that the decision point is    *)
(*                          unconsumed.                                        *)
(* Mut = "M_DEFAULT":       when the orchestrator's lease lapses with the      *)
(*                          decision open, the mechanism takes the first       *)
(*                          enabled chosen edge.                               *)
(* Mut = "M_UNCOVERED":     an edge is enabled without its source's coverage.  *)
(* Mut = "M_NOTAINT":       guards ignore the labels of what they read.        *)
(* Mut = "M_GRANTANYEPOCH": a ready node is granted under any rules epoch.     *)
(* Mut = "M_NOLINEAGE":     the promotion gate does not check lineages.        *)
(* Mut = "M_TIMEOUTDONE":   a failed decision completes the workflow.          *)
(* Mut = "M_REWRITE":       a worker may rewrite its status attribute after    *)
(*                          its node has ended.                                *)
EXTENDS Integers, FiniteSets

CONSTANT Mut

Nodes   == {"s", "b", "c", "j"}
Lin     == {"A", "B"}
Sts     == {"ok", "bad"}
Lbls    == {"trusted", "untrusted"}

Edges   == {"e1", "e2", "e3", "e4"}
Src     == [e \in Edges |-> CASE e = "e1" -> "s" [] e = "e2" -> "s" [] e = "e3" -> "b" [] e = "e4" -> "c"]
Dst     == [e \in Edges |-> CASE e = "e1" -> "b" [] e = "e2" -> "c" [] e = "e3" -> "j" [] e = "e4" -> "j"]
Chosen  == {"e1", "e2"}
Computed == Edges \ Chosen
Clear   == {"e1", "e3"}          \* edges whose target reads the source's output in the clear
Outward == {"c"}
Anc     == [n \in Nodes |-> CASE n = "s" -> {} [] n = "b" -> {"s"} [] n = "c" -> {"s"}
                                 [] n = "j" -> {"s", "b", "c"}]
Sink    == "j"
PE      == 0                     \* the rules epoch the workflow was promoted under

Seatings == [Nodes -> [t : Lin, o : Lin]]
Alternates(st) == /\ \A n \in Nodes : st[n].t # st[n].o
                  /\ \A e \in Clear : st[Src[e]].t # st[Dst[e]].t

NoAttr == [st |-> "none", lbl |-> "trusted"]

VARIABLES
  promoted,        \* the workflow has been promoted
  seatOK,          \* the promoted seating passed Alternates (ghost; the seating itself is read by nothing
                   \* after the gate, so it is not kept, which keeps one state per verdict)
  epoch,           \* the rules epoch
  orchLive,        \* the orchestrator's lease is live
  wf,              \* the workflow: running, completed, failed
  status,          \* each node: idle, ready, running, ended, failed
  attr,            \* each node's attributes, lifted when it ends: [st, lbl]
  grantEpoch,      \* the rules epoch each node was granted under (ghost; -1 if never)
  covered,         \* the node's cell Observer has reported coverage to its seal
  finding,         \* a finding has been ordered against the node
  findingAt,       \* the log position of that finding (ghost)
  idx,             \* the log position of the last ordered entry (ghost)
  consumed,        \* the decision point at s has been consumed
  decisionFailed,  \* the decision point at s failed: the orchestrator's lease lapsed
  pending,         \* Routes decided and not yet applied: [edge, ep, basis]
  applied,         \* Routes applied (ghost): [edge, at, ok, basis, now]
  voided,          \* Routes void at apply (ghost): [edge, why]
  activatedBy,     \* how each node was activated: none, route, computed, default (ghost)
  routedOnTaint,   \* the activating edge's guard read an untrusted attribute (ghost)
  uncoveredAct     \* the activating edge's source was not covered (ghost)

top   == <<promoted, seatOK, epoch, orchLive, wf>>
nodeV == <<status, attr, grantEpoch, covered>>
obsV  == <<finding, findingAt, idx>>
route == <<consumed, decisionFailed, pending, applied, voided>>
act   == <<activatedBy, routedOnTaint, uncoveredAct>>
vars  == <<top, nodeV, obsV, route, act>>

Init ==
  /\ promoted = FALSE
  /\ seatOK = TRUE
  /\ epoch = PE
  /\ orchLive = FALSE
  /\ wf = "running"
  /\ status = [n \in Nodes |-> "idle"]
  /\ attr = [n \in Nodes |-> NoAttr]
  /\ grantEpoch = [n \in Nodes |-> -1]
  /\ covered = [n \in Nodes |-> FALSE]
  /\ finding = [n \in Nodes |-> FALSE]
  /\ findingAt = [n \in Nodes |-> 0]
  /\ idx = 0
  /\ consumed = FALSE
  /\ decisionFailed = FALSE
  /\ pending = {}
  /\ applied = {}
  /\ voided = {}
  /\ activatedBy = [n \in Nodes |-> "none"]
  /\ routedOnTaint = [n \in Nodes |-> FALSE]
  /\ uncoveredAct = [n \in Nodes |-> FALSE]

\* --- the mechanism's rules ----------------------------------------------------

\* A guard over typed attributes: ADR-0054 §4.
Guard(e) == CASE e = "e1" -> attr["s"].st = "ok"
              [] e = "e2" -> TRUE
              [] e = "e3" -> TRUE
              [] e = "e4" -> TRUE

\* The routing rule over labels: ADR-0054 §5. Every guard here reads the attributes of its source.
TaintOK(e) == Mut = "M_NOTAINT" \/ ~(Dst[e] \in Outward /\ attr[Src[e]].lbl = "untrusted")

\* The source's round has been read to its seal: ADR-0039's carry, at the edge (ADR-0054 §7).
CoveredOK(e) == Mut = "M_UNCOVERED" \/ covered[Src[e]]

\* No finding against the source or an ancestor: a finding only subtracts.
Unfound(e) == \A a \in Anc[Src[e]] \cup {Src[e]} : ~finding[a]

Enabled(e) == /\ status[Src[e]] = "ended"
              /\ Guard(e) /\ TaintOK(e) /\ CoveredOK(e) /\ Unfound(e)
              /\ epoch = PE

\* The checks a Route must pass, at decide and again at apply: ADR-0054 §8. M_NOCONSUME drops the
\* consumption check at apply only.
RouteOK(r, atApply) == /\ orchLive
                       /\ epoch = r.ep
                       /\ wf = "running"
                       /\ ((Mut = "M_NOCONSUME" /\ atApply) \/ ~consumed)
                       /\ Enabled(r.edge)

Why(r) == CASE ~orchLive \/ epoch # r.ep -> "lease"
            [] wf # "running"            -> "ended"
            [] consumed                  -> "consumed"
            [] ~Unfound(r.edge)          -> "finding"
            [] OTHER                     -> "guard"

\* A node is activated at most once: a node that is not idle is left as it is.
Activate(e, how) ==
  IF status[Dst[e]] = "idle"
    THEN /\ status' = [status EXCEPT ![Dst[e]] = "ready"]
         /\ activatedBy' = [activatedBy EXCEPT ![Dst[e]] = how]
         /\ routedOnTaint' = [routedOnTaint EXCEPT ![Dst[e]] = attr[Src[e]].lbl = "untrusted"]
         /\ uncoveredAct' = [uncoveredAct EXCEPT ![Dst[e]] = ~covered[Src[e]]]
    ELSE UNCHANGED <<status, activatedBy, routedOnTaint, uncoveredAct>>

\* --- actions -----------------------------------------------------------------

\* The promotion: a quorum grant of the DAG and its seatings, gated on lineage (ADR-0054 §2, §6).
Promote(st) ==
  /\ ~promoted
  /\ Mut = "M_NOLINEAGE" \/ Alternates(st)
  /\ promoted' = TRUE /\ seatOK' = Alternates(st) /\ orchLive' = TRUE
  /\ status' = [status EXCEPT !["s"] = "ready"]
  /\ UNCHANGED <<epoch, wf, attr, grantEpoch, covered, obsV, route, act>>

\* A ready node's lease is granted under the promotion, or refused and the node fails.
Grant(n) ==
  /\ promoted /\ status[n] = "ready" /\ wf = "running"
  /\ IF Mut = "M_GRANTANYEPOCH" \/ epoch = PE
       THEN status' = [status EXCEPT ![n] = "running"] /\ grantEpoch' = [grantEpoch EXCEPT ![n] = epoch]
       ELSE status' = [status EXCEPT ![n] = "failed"]  /\ UNCHANGED grantEpoch
  /\ UNCHANGED <<top, attr, covered, obsV, route, act>>

\* A worker's round ends. Havoc: any status, any label. The attributes are lifted once.
End(n, s, l) ==
  /\ status[n] = "running"
  /\ status' = [status EXCEPT ![n] = "ended"]
  /\ attr' = [attr EXCEPT ![n] = [st |-> s, lbl |-> l]]
  /\ UNCHANGED <<top, grantEpoch, covered, obsV, route, act>>

\* M_REWRITE only: a worker changes its status attribute after its node has ended.
Rewrite(n, s) ==
  /\ Mut = "M_REWRITE" /\ status[n] = "ended" /\ attr[n].st # s
  /\ attr' = [attr EXCEPT ![n].st = s]
  /\ UNCHANGED <<top, status, grantEpoch, covered, obsV, route, act>>

\* A worker's round ends without an end: its lease lapsed.
Fail(n) ==
  /\ status[n] = "running"
  /\ status' = [status EXCEPT ![n] = "failed"]
  /\ UNCHANGED <<top, attr, grantEpoch, covered, obsV, route, act>>

\* The node's cell Observer reports a heartbeat whose mark reaches the node's seal.
Cover(n) ==
  /\ status[n] = "ended" /\ ~covered[n]
  /\ covered' = [covered EXCEPT ![n] = TRUE]
  /\ UNCHANGED <<top, status, attr, grantEpoch, obsV, route, act>>

\* A finding against a node that has started, ordered in the log. From the cell Observer or a
\* correlator, before coverage or after it.
Finding(n) ==
  /\ status[n] \in {"running", "ended"} /\ ~finding[n]
  /\ finding' = [finding EXCEPT ![n] = TRUE]
  /\ idx' = idx + 1
  /\ findingAt' = [findingAt EXCEPT ![n] = idx + 1]
  /\ UNCHANGED <<top, nodeV, route, act>>

\* The orchestrator's `Route(edge)`, decided by one replica. Havoc: any chosen edge. A route that
\* fails the checks is denied, which is not ordered and changes nothing here.
Decide(e) ==
  /\ promoted /\ e \in Chosen
  /\ RouteOK([edge |-> e, ep |-> epoch], FALSE)
  /\ pending' = pending \cup {[edge |-> e, ep |-> epoch, basis |-> attr["s"]]}
  /\ UNCHANGED <<top, nodeV, obsV, consumed, decisionFailed, applied, voided, act>>

\* The Route commits and every replica applies it at its log position.
Apply(r) ==
  /\ r \in pending
  /\ pending' = pending \ {r}
  /\ idx' = idx + 1
  /\ IF Mut = "M_DECIDEONLY" \/ RouteOK(r, TRUE)
       THEN /\ consumed' = TRUE
            /\ Activate(r.edge, "route")
            /\ applied' = applied \cup {[edge |-> r.edge, at |-> idx + 1, ok |-> RouteOK(r, FALSE),
                                         basis |-> r.basis, now |-> attr["s"]]}
            /\ UNCHANGED voided
       ELSE /\ voided' = voided \cup {[edge |-> r.edge, why |-> Why(r)]}
            /\ UNCHANGED <<consumed, status, applied, act>>
  /\ UNCHANGED <<top, attr, grantEpoch, covered, finding, findingAt, decisionFailed>>

\* A computed edge fires inside the apply of the entry that enabled it: one evaluation, no gap.
Fire(e) ==
  /\ promoted /\ e \in Computed /\ wf = "running"
  /\ status[Dst[e]] = "idle" /\ Enabled(e)
  /\ Activate(e, "computed")
  /\ UNCHANGED <<top, attr, grantEpoch, covered, obsV, route>>

\* The orchestrator's lease lapses. Its successor rounds are not modelled.
OrchLapse ==
  /\ orchLive
  /\ orchLive' = FALSE
  /\ UNCHANGED <<promoted, seatOK, epoch, wf, nodeV, obsV, route, act>>

\* The decision point is open, no route is in flight and no orchestrator is live: it fails.
\* Under M_DEFAULT the mechanism takes the first enabled chosen edge instead.
DecisionLapse ==
  /\ promoted /\ ~orchLive /\ ~consumed /\ ~decisionFailed /\ pending = {} /\ wf = "running"
  /\ status["s"] = "ended"
  /\ IF Mut = "M_DEFAULT" /\ \E e \in Chosen : Enabled(e)
       THEN /\ consumed' = TRUE
            /\ Activate(CHOOSE x \in Chosen : Enabled(x), "default")
            /\ UNCHANGED decisionFailed
       ELSE /\ decisionFailed' = TRUE
            /\ UNCHANGED <<consumed, status, act>>
  /\ UNCHANGED <<top, attr, grantEpoch, covered, obsV, pending, applied, voided>>

\* An epoch fence: every live round ends.
Fence ==
  /\ promoted /\ epoch = PE
  /\ epoch' = PE + 1
  /\ idx' = idx + 1
  /\ orchLive' = FALSE
  /\ status' = [n \in Nodes |-> IF status[n] = "running" THEN "failed" ELSE status[n]]
  /\ UNCHANGED <<promoted, seatOK, wf, attr, grantEpoch, covered, finding, findingAt, route, act>>

\* The mechanism decides completion. A failed node or a failed decision fails the workflow.
Settle ==
  /\ promoted /\ wf = "running"
  /\ \/ /\ status[Sink] = "ended" /\ wf' = "completed"
     \/ /\ status[Sink] # "ended"
        /\ decisionFailed \/ \E n \in Nodes : status[n] = "failed"
        /\ wf' = IF Mut = "M_TIMEOUTDONE" /\ decisionFailed THEN "completed" ELSE "failed"
  /\ UNCHANGED <<promoted, seatOK, epoch, orchLive, nodeV, obsV, route, act>>

Next == \/ \E st \in Seatings : Promote(st)
        \/ \E n \in Nodes : Grant(n) \/ Fail(n) \/ Cover(n) \/ Finding(n)
        \/ \E n \in Nodes, s \in Sts, l \in Lbls : End(n, s, l)
        \/ \E n \in Nodes, s \in Sts : Rewrite(n, s)
        \/ \E e \in Chosen : Decide(e)
        \/ \E r \in pending : Apply(r)
        \/ \E e \in Computed : Fire(e)
        \/ OrchLapse \/ DecisionLapse \/ Fence \/ Settle

Spec == Init /\ [][Next]_vars

\* --- the properties ----------------------------------------------------------

AppliedRouteEnabled == \A r \in applied : r.ok

OneRoutePerDecision == Cardinality(applied) <= 1

FindingPrecedesNoRoute ==
  \A r \in applied : \A a \in Anc[Src[r.edge]] \cup {Src[r.edge]} :
     findingAt[a] = 0 \/ findingAt[a] > r.at

ChosenOnlyByRoute == \A e \in Chosen : activatedBy[Dst[e]] \in {"none", "route"}

EdgeAfterCoverage == \A n \in Nodes : ~uncoveredAct[n]

TaintedNeverOutward == \A n \in Outward : activatedBy[n] # "none" => ~routedOnTaint[n]

GrantUnderPromotion == \A n \in Nodes : grantEpoch[n] \in {-1, PE}

PromotedAlternates == promoted => seatOK

CompletedOnlyBySink == wf = "completed" => status[Sink] = "ended"

BasisStable == \A r \in applied : r.basis = r.now

Safe == /\ AppliedRouteEnabled /\ OneRoutePerDecision /\ FindingPrecedesNoRoute
        /\ ChosenOnlyByRoute /\ EdgeAfterCoverage /\ TaintedNeverOutward
        /\ GrantUnderPromotion /\ PromotedAlternates /\ CompletedOnlyBySink /\ BasisStable

\* --- a state constraint, for one row only -------------------------------------

\* M_REWRITE lets a worker change its outcome after its node has ended, so a route can be decided,
\* voided at apply and decided again without end, and the log index has no bound. Its remainder row
\* is checked up to log index 6, the furthest the unmutated module reaches: LogReach holds and
\* NeverLogSix is violated with Mut = "none" (ADR-0054 §12). No other row uses it.
CapLog == idx <= 6

\* The bound CapLog rests on. Not a property of the design: it must hold with Mut = "none".
LogReach == idx <= 6

\* --- reachability witnesses: each must be VIOLATED ---------------------------

\* A route is applied, and the workflow completes.
NeverRouted == applied = {}
NeverCompleted == wf # "completed"
\* A route is void at apply because a finding was ordered between its decide and its apply,
\* after coverage: the race the re-check exists for, which coverage does not close.
NeverVoidedByFinding == \A v \in voided : v.why # "finding"
\* A route is void because another consumed the decision point first.
NeverVoidedByConsumed == \A v \in voided : v.why # "consumed"
\* A route is void because the orchestrator's lease or the epoch moved.
NeverVoidedByLease == \A v \in voided : v.why # "lease"
\* The orchestrator lapses with the decision open, and the decision fails.
NeverDecisionFailed == ~decisionFailed
\* The outward node is reached, under a trusted attribute.
NeverOutward == activatedBy["c"] = "none"
\* A computed edge fires.
NeverComputed == \A n \in Nodes : activatedBy[n] # "computed"
\* A ready node is refused at grant after a fence.
NeverRefusedAtGrant == ~(\E n \in Nodes : status[n] = "failed" /\ grantEpoch[n] = -1)
\* The log reaches index 6, so CapLog cuts nothing the unmutated module does.
NeverLogSix == idx < 6
=============================================================================
