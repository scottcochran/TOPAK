------------------------------- MODULE Mesh -------------------------------
(* A workflow that is a mesh: ADR-0055 (Proposed), its ratification          *)
(* condition (§11). ADR-0054's workflow with its one structural rule         *)
(* removed: the graph may have cycles. What replaces acyclicity is an        *)
(* activation budget the promotion votes on, every lease charged to it, the  *)
(* orchestrator's rounds included. A node may run more than once, so         *)
(* attributes, decision points and findings are kept per activation, and a   *)
(* guard reads the activation that triggered it and that activation's causal  *)
(* history, never a node's latest value.                                     *)
(*                                                                             *)
(* The mesh is fixed and small:                                                *)
(*                                                                             *)
(*            e1 (chosen, clear)                                               *)
(*        s ---------------------> w        e2 (chosen, handle,                *)
(*        ^                        |            guard: s ok)                   *)
(*        +------------------------+     s ---------------------> x            *)
(*            e3 (computed, clear)                                             *)
(*                                                                             *)
(* `s` is the root and the one decision node, `w` a worker on the loop, `x`  *)
(* the sink, outward. The budget N is 6: one loop and the exit. Every worker *)
(* is havoc (any outcome, and it may read untrusted content at any round);  *)
(* the orchestrator routes any chosen edge whenever its lease is live; a     *)
(* finding may land on any activation that has started, at any moment.       *)
(*                                                                             *)
(*   BudgetBound            no more than N leases are ever granted, the        *)
(*                          orchestrator's rounds included                     *)
(*   CompletedOnlyBySink    a workflow completes only when an activation of    *)
(*                          its sink has ended; running out of budget fails it *)
(*   RouteOnItsEvent        every applied Route consumed the activation it was *)
(*                          decided for                                        *)
(*   NoActivationAfterFinding no activation is created by an edge out of an   *)
(*                          activation whose causal history held a finding     *)
(*                          ordered before it                                  *)
(*   LabelCoversTruth       an activation that really carries untrusted        *)
(*                          content is labelled untrusted: taint is carried    *)
(*                          around the cycle along clear edges                 *)
(*   TaintedNeverOutward    the outward sink is never entered from an          *)
(*                          activation that really carries untrusted content   *)
(*   ClearHopsAlternate     every activation entered by a clear edge has a     *)
(*                          Thinker lineage different from its trigger's       *)
(*                                                                             *)
(* ADR-0054's properties about one decision (the re-check at apply, one route *)
(* per decision, no default edge, coverage) are Workflow.tla's and are not    *)
(* repeated. Not modelled: fan-out, scoped joins and serialisation per node   *)
(* (this mesh never runs two activations at once); Observer lineage; epochs   *)
(* and fences; the track the orchestrator is delivered; the gate's bipartite  *)
(* check, which is static and whose runtime consequence is ClearHopsAlternate.*)
(* Deadlock is not checked: a workflow may stall, and stalling is safe.       *)
(*                                                                             *)
(* Mut = "none":            ADR-0055 as drafted.                               *)
(* Mut = "M_OVERRUN":       the budget is checked with <= in place of <.       *)
(* Mut = "M_ORCHFREE":      the orchestrator's rounds are not charged.         *)
(* Mut = "M_BUDGETDONE":    running out of budget completes the workflow.      *)
(* Mut = "M_TRACKER":       the orchestrator holds one lease across decision   *)
(*                          events, as a tracker would, and a route names its  *)
(*                          node, not its activation: it applies to whichever  *)
(*                          activation of the node is open when it commits.    *)
(* Mut = "M_SOURCEONLY":    a finding disables only edges out of the           *)
(*                          activation it is against, not out of activations   *)
(*                          downstream of it.                                  *)
(* Mut = "M_FORGETTAINT":   a clear input does not join the receiver's label.  *)
(* Mut = "M_NOLINEAGE":     the promotion gate does not check lineages.        *)
EXTENDS Integers, FiniteSets, Sequences

CONSTANT Mut

N        == 6                    \* the activation budget the promotion votes on
Nodes    == {"s", "w", "x"}
Lin      == {"A", "B"}
Sts      == {"ok", "bad"}
Edges    == {"e1", "e2", "e3"}
Src      == [e \in Edges |-> CASE e = "e1" -> "s" [] e = "e2" -> "s" [] e = "e3" -> "w"]
Dst      == [e \in Edges |-> CASE e = "e1" -> "w" [] e = "e2" -> "x" [] e = "e3" -> "s"]
Chosen   == {"e1", "e2"}
Clear    == {"e1", "e3"}         \* edges whose target reads the source's output in the clear
Outward  == {"x"}
Sink     == "x"
Root     == "s"
Tracker  == Mut = "M_TRACKER"

Seatings == [Nodes -> Lin]
\* The gate: the clear edges are 2-coloured by the Thinkers' lineages (ADR-0055 §5).
Alternates(st) == \A e \in Clear : st[Src[e]] # st[Dst[e]]

Max(S) == CHOOSE m \in S : \A y \in S : y <= m

VARIABLES
  promoted,   \* the mesh has been promoted
  seat,       \* each node's Thinker lineage, fixed by the promotion
  wf,         \* the workflow: running, completed, failed
  acts,       \* the activations, in log order: [node, trig, via, status, st, lbl, truth, lin, hist,
              \*   found, foundAt, at]; trig is the activation it was entered from, hist its causal history
  nCharged,   \* leases charged to the budget
  nAll,       \* leases granted, charged or not (ghost)
  exhausted,  \* a grant was refused for want of budget
  orch,       \* the orchestrator's round: [live, ev, id]
  nRounds,    \* orchestrator rounds granted
  served,     \* decision events an orchestrator round has been granted for
  consumed,   \* decision events consumed by an applied Route
  decFailed,  \* decision events that failed
  pending,    \* Routes decided and not yet applied: [edge, ev, round]
  applied,    \* Routes applied (ghost): [edge, ev, to, at]
  voided,     \* Routes void at apply (ghost): [edge, why]
  idx         \* the log position of the last ordered entry (ghost)

budV  == <<nCharged, nAll, exhausted>>
orchV == <<orch, nRounds, served>>
decV  == <<consumed, decFailed, pending, applied, voided>>
vars  == <<promoted, seat, wf, acts, budV, orchV, decV, idx>>

Init ==
  /\ promoted = FALSE
  /\ seat = [n \in Nodes |-> "A"]
  /\ wf = "running"
  /\ acts = <<>>
  /\ nCharged = 0 /\ nAll = 0 /\ exhausted = FALSE
  /\ orch = [live |-> FALSE, ev |-> 0, id |-> 0]
  /\ nRounds = 0 /\ served = {}
  /\ consumed = {} /\ decFailed = {}
  /\ pending = {} /\ applied = {} /\ voided = {}
  /\ idx = 0

\* --- the mechanism's rules ----------------------------------------------------

Ix(as) == 1..Len(as)

\* An activation of node n, entered by edge e from activation t of `as`, created at log position at.
\* A clear edge carries the source's label and its real taint into the receiver (ADR-0054 §5).
NewAct(as, n, t, e, at) ==
  [node |-> n, trig |-> t, via |-> e, status |-> "ready", st |-> "none",
   lbl |-> (e \in Clear /\ Mut # "M_FORGETTAINT" /\ as[t].lbl),
   truth |-> (e \in Clear /\ as[t].truth),
   lin |-> seat[n], hist |-> {Len(as) + 1} \cup as[t].hist,
   found |-> FALSE, foundAt |-> 0, at |-> at]

\* A guard over the triggering activation's typed attributes (ADR-0055 §3).
Guard(as, e, i) == IF e = "e2" THEN as[i].st = "ok" ELSE TRUE

\* The routing rule over labels (ADR-0054 §5).
TaintOK(as, e, i) == ~(Dst[e] \in Outward /\ as[i].lbl)

\* No finding against the activation or anything in its causal history (ADR-0055 §3).
Unfound(as, i) == \A a \in (IF Mut = "M_SOURCEONLY" THEN {i} ELSE as[i].hist) : ~as[a].found

EnabledIn(as, e, i) == /\ as[i].node = Src[e] /\ as[i].status = "ended"
                       /\ Guard(as, e, i) /\ TaintOK(as, e, i) /\ Unfound(as, i)

\* The decision events still open: ended activations of the decision node, neither consumed nor failed.
OpenEv == {i \in Ix(acts) : acts[i].node = "s" /\ acts[i].status = "ended"
                            /\ i \notin consumed /\ i \notin decFailed}

LatestOpen == IF OpenEv = {} THEN 0 ELSE Max(OpenEv)

CanCharge == IF Mut = "M_OVERRUN" THEN nCharged <= N ELSE nCharged < N

\* --- actions -----------------------------------------------------------------

\* The promotion: a quorum grant of the mesh, its seatings and its budget, gated on lineage.
Promote(st) ==
  /\ ~promoted
  /\ Mut = "M_NOLINEAGE" \/ Alternates(st)
  /\ promoted' = TRUE /\ seat' = st
  /\ acts' = <<[node |-> Root, trig |-> 0, via |-> "root", status |-> "ready", st |-> "none",
                lbl |-> FALSE, truth |-> FALSE, lin |-> st[Root], hist |-> {1},
                found |-> FALSE, foundAt |-> 0, at |-> 0]>>
  /\ UNCHANGED <<wf, budV, orchV, decV, idx>>

\* A ready activation's lease is granted and charged to the budget, or refused for want of it.
Grant(i) ==
  /\ wf = "running" /\ acts[i].status = "ready"
  /\ IF CanCharge
       THEN /\ acts' = [acts EXCEPT ![i].status = "running"]
            /\ nCharged' = nCharged + 1 /\ nAll' = nAll + 1
            /\ UNCHANGED exhausted
       ELSE /\ acts' = [acts EXCEPT ![i].status = "failed"]
            /\ exhausted' = TRUE
            /\ UNCHANGED <<nCharged, nAll>>
  /\ UNCHANGED <<promoted, seat, wf, orchV, decV, idx>>

\* A worker's round ends: any outcome, and it may have read untrusted content (t). Its attributes
\* are lifted in one entry, and a computed edge out of it is evaluated in that same entry.
End(i, s, t) ==
  /\ acts[i].status = "running"
  /\ idx' = idx + 1
  /\ LET a1 == [acts EXCEPT ![i].status = "ended", ![i].st = s,
                            ![i].lbl = @ \/ t, ![i].truth = @ \/ t]
     IN acts' = IF acts[i].node = "w" /\ wf = "running" /\ EnabledIn(a1, "e3", i)
                  THEN Append(a1, NewAct(a1, "s", i, "e3", idx + 1))
                  ELSE a1
  /\ UNCHANGED <<promoted, seat, wf, budV, orchV, decV>>

\* A finding against an activation that has started, ordered in the log.
Finding(i) ==
  /\ acts[i].status \in {"running", "ended"} /\ ~acts[i].found
  /\ idx' = idx + 1
  /\ acts' = [acts EXCEPT ![i].found = TRUE, ![i].foundAt = idx + 1]
  /\ UNCHANGED <<promoted, seat, wf, budV, orchV, decV>>

\* An orchestrator round for one decision event, charged to the budget (ADR-0055 §6). Under
\* M_TRACKER one round is granted once and serves every event after it.
OrchGrant(ev) ==
  /\ wf = "running" /\ ~orch.live /\ ev \in OpenEv
  /\ IF Tracker THEN nRounds = 0 ELSE ev \notin served
  /\ IF Mut = "M_ORCHFREE" \/ CanCharge
       THEN /\ orch' = [live |-> TRUE, ev |-> IF Tracker THEN 0 ELSE ev, id |-> nRounds + 1]
            /\ nRounds' = nRounds + 1
            /\ nAll' = nAll + 1
            /\ nCharged' = IF Mut = "M_ORCHFREE" THEN nCharged ELSE nCharged + 1
            /\ served' = served \cup {ev}
            /\ UNCHANGED <<decFailed, exhausted>>
       ELSE /\ decFailed' = decFailed \cup {ev} /\ exhausted' = TRUE
            /\ UNCHANGED <<orch, nRounds, nAll, nCharged, served>>
  /\ UNCHANGED <<promoted, seat, wf, acts, consumed, pending, applied, voided, idx>>

\* The event a Route is decided for: the round's own, or under M_TRACKER the latest open one.
DecideEv == IF Tracker THEN LatestOpen ELSE orch.ev

\* The orchestrator's `Route(edge)`, decided by one replica. Havoc: any chosen edge.
Decide(e) ==
  /\ wf = "running" /\ orch.live /\ e \in Chosen
  /\ DecideEv \in OpenEv /\ EnabledIn(acts, e, DecideEv)
  /\ pending' = pending \cup {[edge |-> e, ev |-> DecideEv, round |-> orch.id]}
  /\ UNCHANGED <<promoted, seat, wf, acts, budV, orchV, consumed, decFailed, applied, voided, idx>>

\* The Route commits and is applied at its log position, with the checks run again. It consumes
\* the activation it names; under M_TRACKER it names none and takes the latest open one.
Apply(r) ==
  /\ r \in pending
  /\ pending' = pending \ {r}
  /\ idx' = idx + 1
  /\ LET tgt  == IF Tracker THEN LatestOpen ELSE r.ev
         live == orch.live /\ (Tracker \/ (orch.id = r.round /\ orch.ev = r.ev))
         ok   == live /\ wf = "running" /\ tgt \in OpenEv /\ EnabledIn(acts, r.edge, tgt)
     IN IF ok
          THEN /\ consumed' = consumed \cup {tgt}
               /\ acts' = Append(acts, NewAct(acts, Dst[r.edge], tgt, r.edge, idx + 1))
               /\ applied' = applied \cup {[edge |-> r.edge, ev |-> r.ev, to |-> tgt, at |-> idx + 1]}
               /\ orch' = IF Tracker THEN orch ELSE [orch EXCEPT !.live = FALSE]
               /\ UNCHANGED voided
          ELSE /\ voided' = voided \cup {[edge |-> r.edge,
                                         why |-> CASE ~live                  -> "lease"
                                                   [] wf # "running"         -> "ended"
                                                   [] tgt \notin OpenEv      -> "closed"
                                                   [] acts[tgt].found        -> "finding"
                                                   [] ~Unfound(acts, tgt)    -> "history"
                                                   [] OTHER                  -> "guard"]}
               /\ UNCHANGED <<consumed, acts, applied, orch>>
  /\ UNCHANGED <<promoted, seat, wf, budV, nRounds, served, decFailed>>

\* The orchestrator's lease lapses.
OrchLapse ==
  /\ orch.live
  /\ orch' = [orch EXCEPT !.live = FALSE]
  /\ UNCHANGED <<promoted, seat, wf, acts, budV, nRounds, served, decV, idx>>

\* A decision event whose round has lapsed, with no route in flight, fails. No default edge.
DecisionLapse(ev) ==
  /\ wf = "running" /\ ev \in OpenEv /\ pending = {}
  /\ IF Tracker THEN nRounds > 0 /\ ~orch.live
                ELSE ev \in served /\ ~(orch.live /\ orch.ev = ev)
  /\ decFailed' = decFailed \cup {ev}
  /\ UNCHANGED <<promoted, seat, wf, acts, budV, orchV, consumed, pending, applied, voided, idx>>

SinkEnded == \E i \in Ix(acts) : acts[i].node = Sink /\ acts[i].status = "ended"

Quiescent == /\ \A i \in Ix(acts) : acts[i].status \notin {"ready", "running"}
             /\ OpenEv = {} /\ pending = {}

\* The mechanism decides completion. Running out of budget, or nothing left to run, fails it.
Settle ==
  /\ promoted /\ wf = "running"
  /\ \/ SinkEnded /\ wf' = "completed"
     \/ /\ ~SinkEnded /\ (exhausted \/ Quiescent)
        /\ wf' = IF Mut = "M_BUDGETDONE" /\ exhausted THEN "completed" ELSE "failed"
  /\ UNCHANGED <<promoted, seat, acts, budV, orchV, decV, idx>>

Next == \/ \E st \in Seatings : Promote(st)
        \/ \E i \in Ix(acts) : Grant(i) \/ Finding(i) \/ OrchGrant(i) \/ DecisionLapse(i)
        \/ \E i \in Ix(acts), s \in Sts, t \in BOOLEAN : End(i, s, t)
        \/ \E e \in Chosen : Decide(e)
        \/ \E r \in pending : Apply(r)
        \/ OrchLapse \/ Settle

Spec == Init /\ [][Next]_vars

\* --- the properties ----------------------------------------------------------

BudgetBound == nAll <= N

CompletedOnlyBySink == wf = "completed" => SinkEnded

RouteOnItsEvent == \A r \in applied : r.ev = r.to

NoActivationAfterFinding ==
  \A j \in Ix(acts) : j > 1 =>
    \A a \in acts[acts[j].trig].hist : ~acts[a].found \/ acts[a].foundAt > acts[j].at

LabelCoversTruth == \A i \in Ix(acts) : acts[i].truth => acts[i].lbl

TaintedNeverOutward ==
  \A j \in Ix(acts) : (j > 1 /\ acts[j].node \in Outward) => ~acts[acts[j].trig].truth

ClearHopsAlternate ==
  \A j \in Ix(acts) : (j > 1 /\ acts[j].via \in Clear) => acts[j].lin # acts[acts[j].trig].lin

Safe == /\ BudgetBound /\ CompletedOnlyBySink /\ RouteOnItsEvent /\ NoActivationAfterFinding
        /\ LabelCoversTruth /\ TaintedNeverOutward /\ ClearHopsAlternate

\* --- a state constraint, for one row only -------------------------------------

\* M_ORCHFREE stops charging the orchestrator, and M_TRACKER grants it one round for the whole run,
\* so under either the budget buys more worker rounds and the state space outgrows the machine. Their
\* remainder rows are checked up to one lease past the budget, the reach M_OVERRUN's row has with no
\* constraint (ADR-0055 §11). No other row uses it.
CapOnePast == nAll <= N + 1

\* --- reachability witnesses: each must be VIOLATED ---------------------------

\* The loop runs: the decision node is activated a second time.
NeverLooped == Cardinality({i \in Ix(acts) : acts[i].node = "s"}) < 2
\* The workflow completes after going round the loop.
NeverCompletedAfterLoop == ~(wf = "completed" /\ ~NeverLooped)
\* The budget runs out.
NeverExhausted == ~exhausted
\* Untrusted content read on the loop is carried back to the decision node.
NeverTaintAroundLoop ==
  ~(\E i \in Ix(acts) : i > 1 /\ acts[i].node = "s" /\ acts[acts[i].trig].truth)
\* The exit is closed by taint: a decision that would take the exit carries an untrusted label,
\* and the workflow fails.
NeverExitClosedByTaint ==
  ~(wf = "failed" /\ \E i \in Ix(acts) : /\ acts[i].node = "s" /\ acts[i].status = "ended"
                                          /\ acts[i].st = "ok" /\ acts[i].lbl /\ ~acts[i].found)
\* A route is void because of a finding upstream of the activation it was decided for.
NeverVoidedByHistory == \A v \in voided : v.why # "history"
\* A route decided in one round is void because that round has ended: the stale route.
NeverVoidedByLease == \A v \in voided : v.why # "lease"
=============================================================================
