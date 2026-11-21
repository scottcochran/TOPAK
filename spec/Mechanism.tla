---------------------------- MODULE Mechanism ----------------------------
(* The operational model of the reference's replicated state machine:            *)
(* `topak-core` `State::apply` and `check_live`, one operator per log entry       *)
(* kind, written as a function from a projected state and an entry to the next   *)
(* state and the result kind.                                                     *)
(*                                                                                *)
(* Stage 1 of the refinement chain (ADR-0045 T-0045-28; ADR-0033's debt): TRACE   *)
(* VALIDATION. The reference records every `apply` as a step (`trace.rs`), and    *)
(* `TraceSpec` below replays the recorded entries through `Apply`, checking at    *)
(* every step that the model's next projected state and result equal the          *)
(* reference's. A mismatch violates `TraceMatches` at the first step that differs.*)
(*                                                                                *)
(* What this module is: the specification the code is checked against, with the  *)
(* same rules the discriminating modules state (Lease_A1, Seats, Observers,       *)
(* Coupling, RunCoupling, RunSeats) written once, operationally. What it is not:  *)
(* a proof. A trace that validates shows the code agreed with the model on that   *)
(* behaviour. ADR-0045 T-0045-28 stays a trust-root row until a refinement exists.*)
(*                                                                                *)
(* Three facts are taken from the trace rather than computed here, and are the    *)
(* trace's trusted inputs (an `ok` field on the entry):                           *)
(*   Issue             whether `validate_issuance` passed: signatures and the     *)
(*                     rules floor (RulesFloorNV_rev5 checks the floor itself)    *)
(*   BreakGlassApprove whether the approval's signature verified                  *)
(*   Admit             whether the admit's parameter digest matched the replica's *)
(*                     and, under an attested session key, whether the session    *)
(*                     proof verified under it (`proofOk`)                        *)
(*   Grant Renew       whether the appraisal's signature verified (`sigOk`), and  *)
(*   Contested         the key it names (`sigKey`); the model checks the key is   *)
(*                     an issued verifier key (ADR-0025 §1 (f))                   *)
(*   ProfileRegister   what the file parses to: well-formed (`ok`), its digest,   *)
(*                     its artifact digest, and the summary below                 *)
(*   Grant             whether the sign-on assertion verifies for the seat, at    *)
(*                     this state, under an issued provider key (`signOnOk`)      *)
(*   Control           whether the request is signed by the operator seat's key   *)
(*                     (`sigOk`); whether the operator's own assertion verifies   *)
(*                     (`freshOk`), and a target operator's (`targetSignOnOk`);   *)
(*                     and, for a Revoke, the seat it was lifted on, which is in  *)
(*                     the carried facts: the model checks the seat is one the    *)
(*                     target is seated at, in another domain if there is one,    *)
(*                     and not which of several the code picked                   *)
(*   Activate          the roster keys whose signature over this activation       *)
(*                     verified (`approvers`); the grant's Persona and its        *)
(*                     confinement digest, which are digests the code computes    *)
(*   WorkflowLoad      what the workflow's text parses to (`def`), the digests    *)
(*                     of the text and of its artifact (`workflow`, `artifact`),  *)
(*                     and whether every load check passed (`ok`): the model      *)
(*                     neither parses nor restates the load checks                *)
(*                                                                                *)
(* Labels (ADR-0047), operators (ADR-0050) and the emergency seating (ADR-0052),  *)
(* all Proposed, are modelled as `apply` holds every replica to them: the round's *)
(* labels folded from the admits, the control facts recomputed and compared, the  *)
(* envelope of C1 to C9 restated (`Permitted`), the activation's quorum. X1 is    *)
(* retired: a BreakGlassApprove is rejected, and `approvals` stays empty.         *)
(*                                                                                *)
(* Workflows and meshes (ADR-0054, ADR-0055; both Proposed) are modelled as       *)
(* `apply` runs them (workflow.rs): the load under a promotion; a slot's grant,   *)
(* rebuilt from the promoted seating and compared with the one ordered; a route   *)
(* checked again where it is applied; a typed outcome; a finding; and, after      *)
(* every entry that is not a duplicate, the advance: the ends of workflow leases  *)
(* lifted, the fence, coverage at the edge, each computed edge evaluated once in  *)
(* the code's order, decision events with no edge left, joins and skips,          *)
(* completion and failure. `Workflow.tla` and `Mesh.tla` state their properties   *)
(* over one fixed graph each; this is the engine, for whatever graph a trace      *)
(* loads. An orchestrator seat is coupled as a Thinker's is (ADR-0039 A3,         *)
(* pending), and `Route` is an effect (ADR-0041 A4).                              *)
(*                                                                                *)
(* Confinement (ADR-0034 §3, ADR-0036 §6) is modelled as the code checks it at    *)
(* apply: the appraisal against the registered profile, the nonce's epoch, the    *)
(* session proof at Admit. `contained` is the set of fences `State::contained`    *)
(* holds for, recomputed by the model after every step, so the lookup itself is   *)
(* validated. `ConfinementRefinement.tla` reads the same traces against the        *)
(* abstract `Confinement_A1.tla`.                                                 *)
(*                                                                                *)
(* Not modelled: the floor and bundle decisions (an Admit entry is already a      *)
(* decision; apply re-checks the mechanism conditions only, as the code does),    *)
(* the clock (expiry arrives as an ordered EndRound), payloads, denials (never    *)
(* logged), and the Paxos log itself (entries arrive in index order). Of a        *)
(* workflow: its load checks (a trusted input, above); the reason a workflow, an  *)
(* activation or a decision event failed for, which is a status here as a         *)
(* rejection is a result; and, of a slot's grant, any difference from the         *)
(* seating's in a field the trace does not project of a grant.                    *)
(*                                                                                *)
(* Shapes. Every record below has exactly the fields `trace.rs` projects; a       *)
(* function is `(k :> v @@ ...)`, a set `{...}`, a round topic `<<seat, epoch,   *)
(* round>>`, and "none" stands for an absent value.                               *)
(*                                                                                *)
(* State: epoch rulesEpoch seats grantRoster vetoRoster quorum minGrant bgIssued  *)
(*        bgRoster (a set, empty when no break-glass roster is issued) bgQuorum   *)
(*        seatings lastLease controlCtr emSeatings activations (a sequence)       *)
(*        verifierKeys bundleKeys (ADR-0025 §1 (f)) personas criterion           *)
(*        leases liveBySeat lastRound candidates gates approvals revoked          *)
(*        appliedIds lastApplied k tPersona marks seals profiles contested        *)
(*        contained wasmTools buildBound runBound workflows wfBindings            *)
(* Seat: domain kind cell rung                                                    *)
(* Lease: principal seat persona bundle epoch rulesEpoch conf rung alphabet round *)
(*        role ttl ended actions seq att sessionCtr clearSet results consults     *)
(*        person envelope · Item: label delivery                                  *)
(* Seating: principal persona bundle conf rung alphabet role taskLabels           *)
(* EmSeating: persons bundle envDomain envNamed taskLabels drill                  *)
(* Facts: the sixteen fields of `ControlFacts`                                    *)
(* Att: verdict nEpoch nIndex gen key platform · Profile: artifact summary        *)
(*        registeredAt · Summary: image persona measurement minTcb domain p3 p4 p5*)
(* Appraisal: verdict rung profile persona nEpoch nIndex principal round key      *)
(*        measurement tcb platform gen evidence                                   *)
(* Candidate: artifact author votes promotedAt · Vote: verdict evidence rulesEpoch*)
(* Result: kind, plus fence | seq promoted | ended | epoch | rulesEpoch | approvals*)
(*        | workflow                                                              *)
(* Run (a loaded workflow, by the digest of its text): def artifact loadedAt      *)
(*        epoch rulesEpoch outward status acts events charged chargedNode         *)
(*        exhausted evaluated (pairs <<activation, edge>>)                        *)
(* Def: kind root sinks nodes edges orchestrator budget; nodes and edges are      *)
(*        sequences, in the order the code's maps iterate                         *)
(* Node: name outcomes outward join, and a seating's fields · Seating: seat       *)
(*        principal persona bundle conf rung alphabet ttl taskLabel               *)
(* Edge: id from to kind guard delivery · Budget: n perNode                       *)
(* Guard: op, plus g | gs | node anyOf | node has | node cmp value                *)
(* Activation (numbered from 0, as events and histories are): node trig via fired *)
(*        status fence hist createdAt clearInputs handleInputs attrs found seal   *)
(*        covered · Attrs: end actuates label outcome output                      *)
(* Event: state fence edge · Binding (by fence): workflow slot act actuates       *)
(*        reports outcome lifted · Stamp: workflow event basis                    *)
EXTENDS Naturals, Sequences, FiniteSets, TLC

CONSTANTS InitState, Trace

NONE == "none"
RunKinds == {"Consult", "Actuate", "Report", "Route"}
RunEffects == {"Actuate", "Report", "Route"}             \* ActionKind::is_run_effect (ADR-0041 A4)
EmptyFn == [x \in {} |-> x]

DomainOf(k) == IF k \in RunKinds THEN "run" ELSE "build"
InHouse == {"in_house_pretrain", "in_house_finetune"}   \* ADR-0017's axis, Provenance::in_house

\* SeatKind::allows (ADR-0037 §4, ADR-0043 §2)
KindAllows(kind, k) ==
  CASE kind = "thinker"  -> k \in {"Read", "Draft", "Invoke", "Emit", "Submit", "Consult", "Actuate", "Report"}
    [] kind = "observer" -> k \in {"Read", "Emit", "Vote", "Consult", "Report"}
    [] kind = "grant"    -> k \in {"Read", "Emit", "Vote"}
    [] kind = "emergency" -> k \in {"Consult", "Actuate", "Report"}   \* ADR-0052 §1
    [] kind = "orchestrator" -> k \in {"Route", "Report"}             \* ADR-0054 §3
    [] OTHER             -> FALSE                                    \* an operator is issued none

\* SeatKind::is_coupled (ADR-0039 §2; A3, pending): a seat whose effect-bearing admits need a live
\* cell Observer, whose rounds seal, and whose next round waits for the last to be read
Coupled(kind) == kind \in {"thinker", "orchestrator"}

\* TLC refuses `=` between an integer and a string, and `\in STRING` on an integer or a
\* record, so an absent value is tested on its printed form, which every value has.
IsNone(x)       == ToString(x) = ToString(NONE)
Remove(f, x)    == [y \in DOMAIN f \ {x} |-> f[y]]
Put(f, x, v)    == (x :> v) @@ f
Sat(a, b)       == IF a >= b THEN a - b ELSE 0
Rej(s)          == [st |-> s, res |-> [kind |-> "Rejected"]]

SeatDomain(s, seat) == IF seat \in DOMAIN s.seats THEN s.seats[seat].domain ELSE NONE
SeatKindOf(s, seat) == IF seat \in DOMAIN s.seats THEN s.seats[seat].kind ELSE NONE
CellObservers(s, t) == {o \in DOMAIN s.seats : s.seats[o].kind = "observer" /\ s.seats[o].cell = t}
Watches(s, o, t) ==
  /\ o \in DOMAIN s.seats /\ t \in DOMAIN s.seats
  /\ s.seats[o].kind = "observer" /\ Coupled(s.seats[t].kind)
  /\ IF s.seats[o].cell = NONE THEN s.seats[o].domain = s.seats[t].domain ELSE s.seats[o].cell = t

HasLive(s, seat)   == seat \in DOMAIN s.liveBySeat

\* --- operators and seatings (ADR-0050; control.rs) ----------------------------------
OperatorsDeclared(s) == \E x \in DOMAIN s.seats : s.seats[x].kind = "operator"
LiveOperators(s, dom) ==
  {x \in DOMAIN s.liveBySeat : x \in DOMAIN s.seats /\ s.seats[x].kind = "operator" /\ s.seats[x].domain = dom}
LastFence(s, seat) == IF seat \in DOMAIN s.lastLease THEN s.lastLease[seat] ELSE 0
Ctr(s, op) == IF op \in DOMAIN s.controlCtr THEN s.controlCtr[op] ELSE 0
TopicOf(lr)        == <<lr.seat, lr.epoch, lr.round>>
Mark(s, o, topic)  == IF o \in DOMAIN s.marks /\ topic \in DOMAIN s.marks[o] THEN s.marks[o][topic] ELSE 0
Bound(s, seat)     == IF SeatDomain(s, seat) = "run" THEN s.runBound ELSE s.buildBound

\* State::observer_covers, the deterministic half of live(o) (ADR-0039 §1; ADR-0042 §2)
ObserverCovers(s, thinker) ==
  /\ HasLive(s, thinker)
  /\ LET t == s.leases[s.liveBySeat[thinker]] IN
     \E o \in CellObservers(s, thinker) :
       /\ HasLive(s, o)
       /\ Sat(t.seq, Mark(s, o, TopicOf(t))) < s.k

\* State::author_covered (ADR-0039 §3)
AuthorCovered(s, author) ==
  /\ author \in DOMAIN s.seals
  /\ \E o \in CellObservers(s, author) : Mark(s, o, s.seals[author].topic) >= s.seals[author].seq

\* State::check_heartbeat (ADR-0039 §1)
HeartbeatOk(s, seat, topic, wm) ==
  /\ SeatKindOf(s, seat) = "observer"
  /\ LET LiveTopic(t) == HasLive(s, t) /\ TopicOf(s.leases[s.liveBySeat[t]]) = topic
         SealTopic(t) == t \in DOMAIN s.seals /\ s.seals[t].topic = topic
         cands == {t \in DOMAIN s.seats : Coupled(s.seats[t].kind) /\ (LiveTopic(t) \/ SealTopic(t))}
     IN /\ cands # {}
        /\ LET t == CHOOSE t \in cands : TRUE
               upper == IF LiveTopic(t) THEN s.leases[s.liveBySeat[t]].seq ELSE s.seals[t].seq
           IN /\ Watches(s, seat, t)
              /\ wm <= upper
              /\ wm >= Mark(s, seat, topic)

\* The action kind check_live reads: a heartbeat or a finding is checked under the variant it
\* arrived as
AK(a) == IF a.kind \in {"Heartbeat", "Finding"} THEN a.via ELSE a.kind

\* --- workflows and meshes: what a check reads (ADR-0054, ADR-0055, Proposed; workflow.rs) ---
\* Activations, decision events and history sets are numbered from 0, as the code's vector is.
\* Nodes and edges are sequences in the order the code's maps iterate, which is the order the
\* engine visits them in.

MinOf(S) == CHOOSE x \in S : \A y \in S : x <= y
MaxOf(S) == CHOOSE x \in S : \A y \in S : x >= y

NActs(run)       == Cardinality(DOMAIN run.acts)
ActAt(run, j)    == run.acts[j + 1]
ActIdx(run)      == 0 .. NActs(run) - 1
ActsOf(run, n)   == {j \in ActIdx(run) : ActAt(run, j).node = n}
NodeNames(def)   == {def.nodes[k].name : k \in DOMAIN def.nodes}
NodeOf(run, n)   == run.def.nodes[CHOOSE k \in DOMAIN run.def.nodes : run.def.nodes[k].name = n]
EdgeIds(run)     == {run.def.edges[k].id : k \in DOMAIN run.def.edges}
EdgeOf(run, id)  == run.def.edges[CHOOSE k \in DOMAIN run.def.edges : run.def.edges[k].id = id]
InEdges(run, n)  == {run.def.edges[k].id : k \in {k \in DOMAIN run.def.edges : run.def.edges[k].to = n}}
ChosenOut(run, n) == {run.def.edges[k].id : k \in {k \in DOMAIN run.def.edges :
                                                     run.def.edges[k].from = n /\ run.def.edges[k].kind = "chosen"}}
HasOut(run, n)   == \E k \in DOMAIN run.def.edges : run.def.edges[k].from = n

OpenEvent        == [state |-> "open", fence |-> NONE, edge |-> NONE]
FailedEvent      == [state |-> "failed", fence |-> NONE, edge |-> NONE]

\* Guard::reads
RECURSIVE GuardReads(_)
GuardReads(g) ==
  CASE g.op = "true"            -> {}
    [] g.op = "not"             -> GuardReads(g.g)
    [] g.op \in {"all", "any"}  -> UNION {GuardReads(g.gs[k]) : k \in DOMAIN g.gs}
    [] OTHER                    -> {g.node}

\* Run::attrs_in_history: the latest ended activation of `node` in activation i's causal history
AttrsInHistory(run, i, node) ==
  LET c == {j \in ActAt(run, i).hist : ActAt(run, j).node = node /\ ~IsNone(ActAt(run, j).attrs)}
  IN IF c = {} THEN NONE ELSE ActAt(run, MaxOf(c)).attrs

\* Guard::eval (ADR-0054 §4): a node with no attributes in reach makes every atom over it false
RECURSIVE GuardEval(_, _, _)
GuardEval(run, i, g) ==
  CASE g.op = "true" -> TRUE
    [] g.op = "not"  -> ~GuardEval(run, i, g.g)
    [] g.op = "all"  -> \A k \in DOMAIN g.gs : GuardEval(run, i, g.gs[k])
    [] g.op = "any"  -> \E k \in DOMAIN g.gs : GuardEval(run, i, g.gs[k])
    [] OTHER ->
         LET a == AttrsInHistory(run, i, g.node) IN
         /\ ~IsNone(a)
         /\ CASE g.op = "outcome" -> a.outcome \in g.anyOf
              [] g.op = "end"     -> a.end \in g.anyOf
              [] g.op = "label"   -> g.has \in a.label
              [] g.op = "count"   -> CASE g.cmp = "lt" -> a.actuates < g.value
                                       [] g.cmp = "le" -> a.actuates <= g.value
                                       [] g.cmp = "eq" -> a.actuates = g.value
                                       [] g.cmp = "ge" -> a.actuates >= g.value
                                       [] g.cmp = "gt" -> a.actuates > g.value

\* Run::disabled is None: the source ended and covered (ADR-0054 §7), no finding against any
\* activation in its causal history (ADR-0055 §3), its guard true (§4), and the routing rule (§5)
Enabled(run, i, eid) ==
  /\ eid \in EdgeIds(run)
  /\ LET e == EdgeOf(run, eid)
         a == ActAt(run, i)
         Tainted(n) == LET x == AttrsInHistory(run, i, n) IN ~IsNone(x) /\ "untrusted" \in x.label
     IN /\ a.node = e.from /\ a.status = "ended"
        /\ a.covered
        /\ ~\E j \in a.hist : ActAt(run, j).found
        /\ GuardEval(run, i, e.guard)
        /\ LET restrictedIn == e.delivery = "clear" /\ ~IsNone(a.attrs) /\ "restricted" \in a.attrs.label
           IN (e.to \in run.outward \/ restrictedIn) => ~\E n \in GuardReads(e.guard) \cup {e.from} : Tainted(n)

\* State::route_check (ADR-0054 §8): the round is the one granted for the event the route names,
\* the workflow running, the event served by this round, the edge a chosen edge out of it, enabled
RouteCheck(s, fence, edge, wf, ev) ==
  /\ fence \in DOMAIN s.wfBindings
  /\ s.wfBindings[fence].workflow = wf /\ s.wfBindings[fence].slot = "decision" /\ s.wfBindings[fence].act = ev
  /\ wf \in DOMAIN s.workflows
  /\ LET run == s.workflows[wf] IN
     /\ run.status = "running"
     /\ ev \in DOMAIN run.events /\ run.events[ev].state = "served" /\ run.events[ev].fence = fence
     /\ edge \in EdgeIds(run) /\ EdgeOf(run, edge).kind = "chosen" /\ EdgeOf(run, edge).from = ActAt(run, ev).node
     /\ Enabled(run, ev, edge)

\* State::check_finding: a finding names a round of a coupled seat in the Observer's reach
FindingOk(s, seat, topic) ==
  /\ SeatKindOf(s, seat) = "observer"
  /\ \E f \in DOMAIN s.leases : /\ SeatDomain(s, s.leases[f].seat) # NONE
                                /\ TopicOf(s.leases[f]) = topic
                                /\ Watches(s, seat, s.leases[f].seat)

\* State::workflow_admit_check: at apply a route is checked again against the stamp it carries,
\* and a typed outcome is one of its node's (ADR-0054 §4, §8)
WfAdmitCheck(s, e) ==
  LET a == e.action IN
  CASE a.kind = "Route" -> ~IsNone(a.stamp) /\ RouteCheck(s, e.lease, a.edge, a.stamp.workflow, a.stamp.event)
    [] a.kind = "Report" /\ ~IsNone(a.outcome) ->
         /\ e.lease \in DOMAIN s.wfBindings
         /\ s.wfBindings[e.lease].slot = "node"
         /\ LET b == s.wfBindings[e.lease]
                run == s.workflows[b.workflow]
            IN a.outcome \in NodeOf(run, ActAt(run, b.act).node).outcomes
    [] OTHER -> TRUE

\* State::check_action_preconditions
Preconditions(s, e) ==
  LET a == e.action IN
  CASE a.kind = "Submit"    -> a.artifact \notin DOMAIN s.candidates
    [] a.kind = "Vote"      -> /\ a.artifact \in DOMAIN s.candidates
                               /\ IsNone(s.candidates[a.artifact].promotedAt)
                               /\ a.artifact \in DOMAIN s.gates
                               /\ s.gates[a.artifact] = a.evidence
    [] a.kind = "Heartbeat" -> HeartbeatOk(s, e.seat, a.topic, a.watermark)
    [] a.kind = "Finding"   -> FindingOk(s, e.seat, a.topic)
    \* State::workflow_preconditions: a route under its round's own binding
    [] a.kind = "Route"     -> /\ e.lease \in DOMAIN s.wfBindings
                               /\ RouteCheck(s, e.lease, a.edge, s.wfBindings[e.lease].workflow, s.wfBindings[e.lease].act)
    [] OTHER                -> TRUE

\* State::check_live: the epoch fence first (ADR-0022 §2), then the lease
CheckLive(s, e) ==
  /\ e.lease \in DOMAIN s.leases
  /\ LET rec == s.leases[e.lease] IN
     /\ rec.seat = e.seat
     /\ rec.epoch = s.epoch
     /\ e.epoch = rec.epoch
     /\ rec.rulesEpoch = s.rulesEpoch
     /\ rec.ended = NONE
     /\ AK(e.action) \in rec.alphabet
     /\ rec.actions < Bound(s, e.seat)
     /\ Preconditions(s, e)

\* promotion::tally_with_coverage = Promoted (ADR-0024 with A2; ADR-0039 §3)
TallyPromoted(s, c, covered) ==
  /\ c.artifact \in DOMAIN s.gates
  /\ LET ev == s.gates[c.artifact]
         Current(r, v) == r.verdict = v /\ r.evidence = ev /\ r.rulesEpoch = s.rulesEpoch
         Voted(x, v) == x \in DOMAIN c.votes /\ Current(c.votes[x], v)
         counted == s.grantRoster \ {c.author}
         granted == {x \in counted : Voted(x, "grant")}
         vetoDeny == \E x \in s.vetoRoster : Voted(x, "deny")
         grantDeny == \E x \in counted : Voted(x, "deny")
         would == IF s.quorum = "all"
                    THEN ~grantDeny /\ Cardinality(granted) = Cardinality(counted)
                    ELSE Cardinality(granted) >= s.quorum
     IN /\ Cardinality(counted) >= s.minGrant
        /\ ~vetoDeny
        /\ would
        /\ covered

SealOf(lr) == [topic |-> TopicOf(lr), seq |-> lr.seq]

\* State::end_lease
EndLease(s, fence, reason) ==
  IF fence \notin DOMAIN s.leases \/ s.leases[fence].ended # NONE THEN s
  ELSE LET rec == s.leases[fence]
           s1  == [s EXCEPT !.leases = [@ EXCEPT ![fence].ended = reason]]
           s2  == IF rec.seat \in DOMAIN s1.liveBySeat /\ s1.liveBySeat[rec.seat] = fence
                    THEN [s1 EXCEPT !.liveBySeat = Remove(@, rec.seat)] ELSE s1
       IN IF Coupled(SeatKindOf(s, rec.seat))
            THEN [s2 EXCEPT !.seals = Put(@, rec.seat, SealOf(rec))] ELSE s2

\* State::end_all_live: every live lease ends; every live coupled seat's round seals
EndAllLive(s, reason) ==
  LET live     == {s.liveBySeat[x] : x \in DOMAIN s.liveBySeat}
      leases2  == [f \in DOMAIN s.leases |->
                     IF f \in live /\ s.leases[f].ended = NONE
                       THEN [s.leases[f] EXCEPT !.ended = reason] ELSE s.leases[f]]
      thinkers == {x \in DOMAIN s.liveBySeat : Coupled(SeatKindOf(s, x))}
      newSeals == [x \in thinkers |-> SealOf(s.leases[s.liveBySeat[x]])]
  IN [s EXCEPT !.leases = leases2, !.liveBySeat = EmptyFn, !.seals = newSeals @@ @]

\* --- workflows and meshes: the engine (workflow.rs) -----------------------------------

\* Run::enter: a new activation of the edge's target, or one more fired edge into a waiting join
Enter(run, src, eid, at) ==
  LET e      == EdgeOf(run, eid)
      from   == ActAt(run, src)
      label  == IF IsNone(from.attrs) THEN {} ELSE from.attrs.label
      clear  == IF e.delivery = "clear" THEN label ELSE {}
      handle == IF e.delivery = "clear" THEN {} ELSE label
      there  == ActsOf(run, e.to)
  IN IF run.def.kind = "dag" /\ there # {}
       THEN LET j == MinOf(there) IN
            IF ActAt(run, j).status = "waiting"
              THEN [run EXCEPT !.acts[j + 1] = [@ EXCEPT !.fired = @ \cup {eid}, !.clearInputs = @ \cup clear,
                                                         !.handleInputs = @ \cup handle, !.hist = @ \cup from.hist]]
              ELSE run                    \* an `any` join already entered: the edge changes nothing
       ELSE [run EXCEPT !.acts = Append(@,
               [node |-> e.to, trig |-> src, via |-> eid, fired |-> {eid},
                status |-> IF NodeOf(run, e.to).join = "all" THEN "waiting" ELSE "ready", fence |-> NONE,
                hist |-> from.hist \cup {NActs(run)}, createdAt |-> at, clearInputs |-> clear,
                handleInputs |-> handle, attrs |-> NONE, found |-> FALSE, seal |-> NONE, covered |-> FALSE])]

\* Run::dead: in a dag, whether the edge can no longer fire
Dead(run, eid) ==
  LET e    == EdgeOf(run, eid)
      from == ActsOf(run, e.from)
  IN IF from = {} THEN FALSE
     ELSE LET i == MinOf(from)
              a == ActAt(run, i)
          IN CASE a.status \in {"failed", "skipped"} -> TRUE
               [] a.status = "ended" ->
                    IF e.kind = "computed"
                      THEN <<i, eid>> \in run.evaluated /\ ~\E j \in ActsOf(run, e.to) : eid \in ActAt(run, j).fired
                      ELSE IF i \notin DOMAIN run.events THEN FALSE
                      ELSE (CASE run.events[i].state = "consumed" -> run.events[i].edge # eid
                              [] run.events[i].state = "failed"   -> TRUE
                              [] OTHER                            -> FALSE)
               [] OTHER -> FALSE

\* Run::settle_joins (ADR-0054 §1): one pass over the nodes in order, then again until nothing
\* changes. A node every incoming edge of which is dead is skipped; a waiting `all` join is ready
\* when every incoming edge has fired or is dead.
RECURSIVE SettlePass(_, _, _, _)
SettlePass(run, k, changed, at) ==
  IF k > Cardinality(DOMAIN run.def.nodes) THEN [run |-> run, changed |-> changed]
  ELSE LET n   == run.def.nodes[k].name
           ins == InEdges(run, n)
           pos == ActsOf(run, n)
       IN IF n = run.def.root THEN SettlePass(run, k + 1, changed, at)
          ELSE IF pos = {} /\ ins # {} /\ (\A x \in ins : Dead(run, x))
            THEN SettlePass([run EXCEPT !.acts = Append(@,
                   [node |-> n, trig |-> NONE, via |-> NONE, fired |-> {}, status |-> "skipped", fence |-> NONE,
                    hist |-> {}, createdAt |-> at, clearInputs |-> {}, handleInputs |-> {}, attrs |-> NONE,
                    found |-> FALSE, seal |-> NONE, covered |-> FALSE])], k + 1, TRUE, at)
          ELSE IF pos # {} /\ ActAt(run, MinOf(pos)).status = "waiting"
                  /\ (\A x \in ins : x \in ActAt(run, MinOf(pos)).fired \/ Dead(run, x))
            THEN SettlePass([run EXCEPT !.acts[MinOf(pos) + 1].status = "ready"], k + 1, TRUE, at)
          ELSE SettlePass(run, k + 1, changed, at)

RECURSIVE SettleJoins(_, _)
SettleJoins(run, at) ==
  IF run.def.kind # "dag" THEN run
  ELSE LET r == SettlePass(run, 1, FALSE, at) IN IF r.changed THEN SettleJoins(r.run, at) ELSE r.run

\* Run::settle (ADR-0054 §9, ADR-0055 §8): completion first, then failure, then quiescence
Settle(run) ==
  IF run.status # "running" THEN run
  ELSE LET sinkEnded == \E j \in ActIdx(run) : ActAt(run, j).node \in run.def.sinks /\ ActAt(run, j).status = "ended"
           sinksDone == \A x \in run.def.sinks : \E j \in ActsOf(run, x) : ActAt(run, j).status \in {"ended", "skipped"}
           nodeFailed == \E j \in ActIdx(run) : ActAt(run, j).status = "failed"
           eventFailed == \E ev \in DOMAIN run.events : run.events[ev].state = "failed"
           busy      == \E j \in ActIdx(run) : ActAt(run, j).status \in {"ready", "running", "waiting"}
           deciding  == \E ev \in DOMAIN run.events : run.events[ev].state \in {"open", "served"}
           pending   == \E j \in ActIdx(run) : /\ ActAt(run, j).status = "ended" /\ ~ActAt(run, j).covered
                                               /\ HasOut(run, ActAt(run, j).node)
           done      == [run EXCEPT !.status = "completed"]
           failed    == [run EXCEPT !.status = "failed"]
           quiet     == IF ~busy /\ ~deciding /\ ~pending THEN failed ELSE run
       IN IF run.def.kind = "dag"
            THEN IF sinksDone /\ sinkEnded THEN done
                 ELSE IF nodeFailed \/ eventFailed THEN failed
                 ELSE quiet
            ELSE IF sinkEnded THEN done
                 ELSE IF run.exhausted THEN failed
                 ELSE quiet

\* Run::charge (ADR-0055 §2): the budget, at a grant
Charge(run, node) ==
  LET b == run.def.budget IN
  IF IsNone(b) THEN [ok |-> TRUE, run |-> run]
  ELSE LET cnt == IF node \in DOMAIN run.chargedNode THEN run.chargedNode[node] ELSE 0 IN
    IF run.charged >= b.n THEN [ok |-> FALSE, run |-> [run EXCEPT !.exhausted = TRUE]]
    ELSE IF node \in DOMAIN b.perNode /\ cnt >= b.perNode[node] THEN [ok |-> FALSE, run |-> [run EXCEPT !.exhausted = TRUE]]
    ELSE [ok |-> TRUE, run |-> [run EXCEPT !.charged = @ + 1, !.chargedNode = Put(@, node, cnt + 1)]]

\* EndKind::of (ADR-0054 §4)
EndKindOf(r) ==
  CASE r \in {"outcome", "routed", "submitted", "voted", "abstained"} -> "outcome"
    [] r \in {"expired", "renewed"}                                   -> "expired"
    [] r \in {"fenced", "rules_changed"}                              -> "fenced"
    [] OTHER                                                          -> "revoked"   \* revoked, operator

\* State::workflow_advance, step 1: lift the end of one workflow lease into its run
LiftOne(s, fence) ==
  LET rec  == s.leases[fence]
      b    == s.wfBindings[fence]
      run  == s.workflows[b.workflow]
      seal == IF SeatDomain(s, rec.seat) = NONE THEN NONE ELSE SealOf(rec)
      end  == EndKindOf(rec.ended)
      run2 == IF b.slot = "node"
                THEN LET a  == ActAt(run, b.act)
                         a2 == IF end \in {"fenced", "revoked"}
                                 THEN [a EXCEPT !.seal = seal, !.status = "failed", !.fence = NONE]
                                 ELSE [a EXCEPT !.seal = seal, !.status = "ended", !.fence = NONE,
                                                !.attrs = [end |-> end, actuates |-> b.actuates, label |-> rec.clearSet,
                                                           outcome |-> b.outcome, output |-> b.reports]]
                         r1 == [run EXCEPT !.acts[b.act + 1] = a2]
                     IN IF a2.status = "ended" /\ ChosenOut(run, a.node) # {}
                          THEN [r1 EXCEPT !.events = Put(@, b.act, OpenEvent)] ELSE r1
                \* ADR-0054 §8: a lapsed orchestrator fails its decision point and takes no edge
                ELSE IF b.act \in DOMAIN run.events /\ run.events[b.act].state = "served" /\ run.events[b.act].fence = fence
                       THEN [run EXCEPT !.events = Put(@, b.act, FailedEvent)] ELSE run
  IN [s EXCEPT !.wfBindings[fence].lifted = TRUE, !.workflows = Put(@, b.workflow, run2)]

Unlifted(s) == {f \in DOMAIN s.wfBindings : ~s.wfBindings[f].lifted /\ f \in DOMAIN s.leases /\ s.leases[f].ended # NONE}

RECURSIVE LiftAll(_, _)
LiftAll(s, F) == IF F = {} THEN s ELSE LET f == CHOOSE x \in F : TRUE IN LiftAll(LiftOne(s, f), F \ {f})

\* Step 4: computed edges, each evaluated once, when its source has ended and is covered. The
\* code takes the first unevaluated pair, in activation order and then edge order, and starts
\* again; nothing it does makes an earlier pair eligible, so that is one pass in that order.
RECURSIVE FireEdges(_, _, _, _)
FireEdges(run, i, k, at) ==
  IF i >= NActs(run) THEN run
  ELSE IF k > Cardinality(DOMAIN run.def.edges) THEN FireEdges(run, i + 1, 1, at)
  ELSE LET a == ActAt(run, i)
           e == run.def.edges[k]
       IN IF a.status = "ended" /\ a.covered /\ e.from = a.node /\ e.kind = "computed" /\ <<i, e.id>> \notin run.evaluated
            THEN LET r1 == [run EXCEPT !.evaluated = @ \cup {<<i, e.id>>}]
                 IN FireEdges(IF Enabled(r1, i, e.id) THEN Enter(r1, i, e.id, at) ELSE r1, i, k + 1, at)
            ELSE FireEdges(run, i, k + 1, at)

\* Steps 2 to 6, for one running workflow
AdvanceRun(s, run, at) ==
  \* 2. the fence: what the workflow has not yet issued is void (ADR-0024 A4, ADR-0054 §9)
  IF run.epoch # s.epoch \/ run.rulesEpoch # s.rulesEpoch
    THEN [run EXCEPT !.acts = [k \in DOMAIN @ |-> IF @[k].status \in {"ready", "waiting"}
                                                    THEN [@[k] EXCEPT !.status = "failed"] ELSE @[k]],
                     !.status = "failed"]
  ELSE LET \* 3. coverage at the edge (ADR-0039 A3, ADR-0054 §7)
           Cov(a) == /\ a.status = "ended" /\ ~a.covered /\ ~IsNone(a.seal)
                     /\ \E o \in CellObservers(s, NodeOf(run, a.node).seat) : Mark(s, o, a.seal.topic) >= a.seal.seq
           r1 == [run EXCEPT !.acts = [k \in DOMAIN @ |-> IF Cov(@[k]) THEN [@[k] EXCEPT !.covered = TRUE] ELSE @[k]]]
           r2 == FireEdges(r1, 0, 1, at)
           \* 5. a decision event no round holds, with no chosen edge left enabled, fails (§8)
           deadEv == {ev \in DOMAIN r2.events :
                        /\ r2.events[ev].state = "open" /\ ActAt(r2, ev).covered
                        /\ \A x \in ChosenOut(r2, ActAt(r2, ev).node) : ~Enabled(r2, ev, x)}
           r3 == [r2 EXCEPT !.events = [ev \in DOMAIN @ |-> IF ev \in deadEv THEN FailedEvent ELSE @[ev]]]
       IN Settle(SettleJoins(r3, at))           \* 6. joins and skips, then completion and failure

\* State::workflow_advance: after every apply, each running workflow moves as far as it can
Advance(s, at) ==
  LET s1 == LiftAll(s, Unlifted(s))
  IN [s1 EXCEPT !.workflows = [id \in DOMAIN @ |-> IF @[id].status = "running" THEN AdvanceRun(s1, @[id], at) ELSE @[id]]]

\* State::workflow_finding (ADR-0054 §4's `found`): every activation run in the round is marked
WorkflowFinding(s, topic) ==
  LET hits == {f \in DOMAIN s.wfBindings : /\ s.wfBindings[f].slot = "node" /\ f \in DOMAIN s.leases
                                           /\ SeatDomain(s, s.leases[f].seat) # NONE
                                           /\ TopicOf(s.leases[f]) = topic}
      Hit(id, j) == \E f \in hits : s.wfBindings[f].workflow = id /\ s.wfBindings[f].act = j
  IN [s EXCEPT !.workflows = [id \in DOMAIN @ |->
        [@[id] EXCEPT !.acts = [k \in DOMAIN @ |-> IF Hit(id, k - 1) THEN [@[k] EXCEPT !.found = TRUE] ELSE @[k]]]]]

\* State::workflow_admitted: after an admit under a workflow lease is counted. A route consumes
\* its event, enters its target and ends the orchestrator's round; an outcome ends the worker's
WorkflowAdmitted(s, at, fence, a, seq) ==
  CASE a.kind = "Actuate" -> [s EXCEPT !.wfBindings[fence].actuates = @ + 1]
    [] a.kind = "Report" ->
         LET s1 == [s EXCEPT !.wfBindings[fence].reports = Append(@, seq)] IN
         IF IsNone(a.outcome) THEN s1
         ELSE EndLease([s1 EXCEPT !.wfBindings[fence].outcome = a.outcome], fence, "outcome")
    [] a.kind = "Route" /\ ~IsNone(a.stamp) ->
         LET run == s.workflows[a.stamp.workflow]
             r1  == [run EXCEPT !.events = Put(@, a.stamp.event, [state |-> "consumed", fence |-> NONE, edge |-> a.edge])]
         IN EndLease([s EXCEPT !.workflows = Put(@, a.stamp.workflow, Enter(r1, a.stamp.event, a.edge, at))], fence, "routed")
    [] OTHER -> s

\* --- confinement (ADR-0034, ADR-0036; confine.rs) ----------------------------------

TcbOf(x) == IF IsNone(x) THEN 0 ELSE x

\* Profile::check_for_rung: what P7 names, by rung
ProfileForRung(p, r) ==
  \/ r = 0
  \/ /\ p.image
     /\ ~IsNone(p.persona)
     /\ (r >= 2 => ~IsNone(p.measurement))
     /\ (r >= 3 => ~IsNone(p.minTcb))

\* Profile::meets_p3_p5 (ADR-0034 §4; D-0034-3; for Run, P4 is channel fidelity, A2 pending)
ToolVariant(p) == IF p.domain = "run" THEN "Actuate" ELSE "Invoke"
MeetsP3P5(p, alphabet) ==
  /\ p.p3 = "pass"
  /\ (p.p4 = "pass" \/ (p.p4 = "vacuous" /\ ToolVariant(p) \notin alphabet))
  /\ p.p5 = "pass"
\* State::channel_fidelity (ADR-0034 A2, pending): under an attested Run lease whose profile says P4
\* passes, an Actuate names only a tool held to its declared channel
ChannelFidelity(s, f, tool) ==
  LET l == s.leases[f] IN
  \/ IsNone(l.att)
  \/ l.conf \notin DOMAIN s.profiles
  \/ s.profiles[l.conf].summary.domain # "run"
  \/ s.profiles[l.conf].summary.p4 # "pass"
  \/ tool \in s.wasmTools

\* State::check_appraisal (ADR-0034 §3.2): w names what the request fixes
AppraisalOk(s, idx, e, w) ==
  LET a == e.appraisal IN
  /\ a.verdict = "attested"
  /\ a.rung = w.rung
  /\ a.profile = w.conf
  /\ w.conf \in DOMAIN s.profiles
  /\ LET p == s.profiles[w.conf].summary IN
     /\ p.domain = w.domain                        \* ADR-0034 §1: schema shared, profile not
     /\ ProfileForRung(p, w.rung)
     /\ a.persona = w.persona
     /\ p.persona = w.persona
     /\ a.principal = w.principal
     /\ a.round = w.round
     /\ a.nEpoch = s.epoch                         \* FreshEpoch
     /\ a.nIndex < idx
     /\ a.nIndex >= w.minIndex
     /\ (w.rung >= 2 => /\ ~IsNone(a.key)
                        /\ a.measurement = p.measurement
                        /\ TcbOf(a.tcb) >= TcbOf(p.minTcb))
     /\ IF w.rung = 1 THEN a.platform = "launcher"
        ELSE IF w.rung = 2 THEN FALSE              \* the rung-2 seam
        ELSE e.sigOk /\ e.sigKey \in s.verifierKeys

AttOf(a) == [verdict |-> a.verdict, nEpoch |-> a.nEpoch, nIndex |-> a.nIndex,
             gen |-> a.gen, key |-> a.key, platform |-> a.platform]

\* The key an action under the lease is signed with: an attested guest's session key
\* (ADR-0034 §3.5), or, on an emergency seat's lease, the person's (ADR-0052 §1)
HasKey(lr) == (~IsNone(lr.att) /\ ~IsNone(lr.att.key)) \/ ~IsNone(lr.person)

\* State::contained (ADR-0034 §4): a lookup over the lease, the profile and the issued rules
ContainedF(s, f) ==
  LET l == s.leases[f] IN
  /\ l.ended = NONE
  /\ l.rung >= 1
  /\ l.seat \in DOMAIN s.seats
  /\ s.seats[l.seat].rung = l.rung
  /\ ~IsNone(l.att)
  /\ l.att.verdict = "attested"
  /\ l.conf \in DOMAIN s.profiles
  /\ MeetsP3P5(s.profiles[l.conf].summary, l.alphabet)
  /\ l.persona \in DOMAIN s.personas
  /\ s.personas[l.persona] \in InHouse
  /\ s.criterion
  /\ s.profiles[l.conf].summary.domain = SeatDomain(s, l.seat)

ContainedSet(s) == {f \in DOMAIN s.leases : ContainedF(s, f)}

TargetMatches(t, lr) ==
  \/ t.kind = "principal"   /\ t.id = lr.principal
  \/ t.kind = "persona"     /\ t.id = lr.persona
  \/ t.kind = "confinement" /\ t.id = lr.conf

\* State::seated: seated, and nothing it was seated with has been revoked
Seated(s, seat) ==
  /\ seat \in DOMAIN s.seatings
  /\ ~\E t \in s.revoked : TargetMatches(t, s.seatings[seat])

SameBinding(a, b) ==
  a.principal = b.principal /\ a.persona = b.persona /\ a.bundle = b.bundle /\ a.conf = b.conf /\ a.rung = b.rung

\* State::not_a_first_seating (ADR-0050 §2): an unsigned grant that keeps the seat's seated
\* binding is a successor, and an operator's, wherever two operators of the domain are live
NotAFirstSeating(s, e) ==
  /\ OperatorsDeclared(s)
  /\ e.seat \in DOMAIN s.seatings
  /\ SameBinding(s.seatings[e.seat], e)
  /\ SeatDomain(s, e.seat) # NONE
  /\ Cardinality(LiveOperators(s, SeatDomain(s, e.seat))) >= 2

SeatingOf(e) == [principal |-> e.principal, persona |-> e.persona, bundle |-> e.bundle, conf |-> e.conf,
                 rung |-> e.rung, alphabet |-> e.alphabet, role |-> e.role, taskLabels |-> e.taskLabelsAllowed]

\* State::apply_grant
ApplyGrant(s, idx, e) ==
  LET dom  == SeatDomain(s, e.seat)
      kind == SeatKindOf(s, e.seat)
      busy == \E x \in DOMAIN s.liveBySeat : s.leases[s.liveBySeat[x]].principal = e.principal
      revokedHit == \E t \in s.revoked : TargetMatches(t, [principal |-> e.principal, persona |-> e.persona, conf |-> e.conf])
      unread == /\ dom = "run" /\ Coupled(kind) /\ e.seat \in DOMAIN s.seals
                /\ ~(\E o \in CellObservers(s, e.seat) : Mark(s, o, s.seals[e.seat].topic) >= s.seals[e.seat].seq)
      reused == e.seat \in DOMAIN s.lastRound /\ e.round <= s.lastRound[e.seat]
  IN IF dom = NONE THEN Rej(s)
     ELSE IF e.seat \in DOMAIN s.liveBySeat THEN Rej(s)
     ELSE IF \E k \in e.alphabet : DomainOf(k) # dom THEN Rej(s)
     ELSE IF \E k \in e.alphabet : ~KindAllows(kind, k) THEN Rej(s)
     ELSE IF busy THEN Rej(s)
     ELSE IF e.role = "voter" /\ dom # "build" THEN Rej(s)
     ELSE IF revokedHit THEN Rej(s)
     ELSE IF e.rung > 3 THEN Rej(s)
     ELSE IF e.rung # s.seats[e.seat].rung THEN Rej(s)   \* ADR-0034 §3.4, M_DOWNGRADE
     ELSE IF kind = "operator" /\ ~e.signOnOk THEN Rej(s)   \* ADR-0050 §3: sign-on at the lease boundary
     ELSE IF e.rung = 0 /\ ~IsNone(e.appraisal) THEN Rej(s)
     ELSE IF e.rung > 0 /\ IsNone(e.appraisal) THEN Rej(s)
     ELSE IF e.rung > 0 /\ ~AppraisalOk(s, idx, e, [principal |-> e.principal, round |-> e.round,
                              conf |-> e.conf, persona |-> e.persona, rung |-> e.rung, domain |-> dom, minIndex |-> 0])
       THEN Rej(s)
     ELSE IF e.ttl > s.tPersona THEN Rej(s)      \* ADR-0031 A2
     ELSE IF unread THEN Rej(s)
     ELSE IF reused THEN Rej(s)
     ELSE LET lr == [principal |-> e.principal, seat |-> e.seat, persona |-> e.persona, bundle |-> e.bundle,
                     epoch |-> s.epoch, rulesEpoch |-> s.rulesEpoch, conf |-> e.conf, rung |-> e.rung,
                     alphabet |-> e.alphabet, round |-> e.round, role |-> e.role, ttl |-> e.ttl,
                     ended |-> NONE, actions |-> 0, seq |-> 0,
                     att |-> IF e.rung = 0 THEN NONE ELSE AttOf(e.appraisal), sessionCtr |-> 0,
                     \* ADR-0047 §4: the task is delivered clear, so clearSet starts from its label
                     clearSet |-> e.taskLabel, results |-> EmptyFn, consults |-> EmptyFn,
                     person |-> NONE, envelope |-> EmptyFn]
          IN [st  |-> [s EXCEPT !.leases = Put(@, idx, lr), !.liveBySeat = Put(@, e.seat, idx),
                                !.lastRound = Put(@, e.seat, e.round), !.lastLease = Put(@, e.seat, idx)],
              res |-> [kind |-> "LeaseGranted", fence |-> idx]]

\* State::apply_renew (ADR-0031 §4, A1)
ApplyRenew(s, idx, e) ==
  IF e.fence \notin DOMAIN s.leases THEN Rej(s)
  ELSE LET old == s.leases[e.fence] IN
    IF old.seat # e.seat \/ old.ended # NONE THEN Rej(s)
    ELSE IF SeatKindOf(s, e.seat) = "emergency" THEN Rej(s)   \* ADR-0052 §3: no renewal
    ELSE IF old.epoch # s.epoch \/ old.rulesEpoch # s.rulesEpoch THEN Rej(s)
    ELSE IF e.ttl > s.tPersona THEN Rej(s)      \* ADR-0031 A2
    ELSE IF ~(e.alphabet \subseteq old.alphabet) THEN Rej(s)
    ELSE IF e.rung # old.rung THEN Rej(s)
    ELSE IF e.ttl > old.ttl THEN Rej(s)
    \* ADR-0034 §3.6: an attested lease renews on a fresh appraisal of the same guest
    ELSE IF IsNone(old.att) /\ ~IsNone(e.appraisal) THEN Rej(s)
    ELSE IF ~IsNone(old.att) /\ IsNone(e.appraisal) THEN Rej(s)
    ELSE IF ~IsNone(old.att) /\ ~AppraisalOk(s, idx, e, [principal |-> old.principal, round |-> old.round,
                                  conf |-> old.conf, persona |-> old.persona, rung |-> old.rung,
                                  domain |-> SeatDomain(s, old.seat), minIndex |-> e.fence])
      THEN Rej(s)
    ELSE IF ~IsNone(old.att) /\ (e.appraisal.gen # old.att.gen \/ e.appraisal.key # old.att.key) THEN Rej(s)
    ELSE LET new == [old EXCEPT !.alphabet = e.alphabet, !.ttl = e.ttl,
                                !.att = IF IsNone(old.att) THEN NONE ELSE AttOf(e.appraisal)]
         IN [st  |-> [s EXCEPT !.leases = Put([@ EXCEPT ![e.fence].ended = "renewed"], idx, new),
                               !.liveBySeat = Put(@, e.seat, idx), !.lastLease = Put(@, e.seat, idx)],
             res |-> [kind |-> "Renewed", fence |-> idx]]

\* State::apply_revoke (ADR-0031 §5 R3)
ApplyRevoke(s, e) ==
  LET t        == e.target
      liveF    == {s.liveBySeat[x] : x \in DOMAIN s.liveBySeat}
      hit      == {f \in liveF : TargetMatches(t, s.leases[f])}
      hitSeats == {s.leases[f].seat : f \in hit}
      leases2  == [f \in DOMAIN s.leases |-> IF f \in hit THEN [s.leases[f] EXCEPT !.ended = "revoked"] ELSE s.leases[f]]
      thinkers == {x \in hitSeats : Coupled(SeatKindOf(s, x))}
      newSeals == [x \in thinkers |-> SealOf(s.leases[s.liveBySeat[x]])]
  IN [st  |-> [s EXCEPT !.revoked = @ \cup {t}, !.leases = leases2,
                        !.liveBySeat = [x \in DOMAIN @ \ hitSeats |-> @[x]],
                        !.seals = newSeals @@ @,
                        !.approvals = [x \in DOMAIN @ \ hitSeats |-> @[x]]],
      res |-> [kind |-> "Revoked", ended |-> Cardinality(hit)]]

Admitted(seq, promoted) == [kind |-> "Admitted", seq |-> seq, promoted |-> promoted]

\* State::apply_admit: the re-check across the consensus gap, then the effect on state
ApplyAdmit(s, idx, e) ==
  IF ~e.ok THEN Rej(s)
  \* ADR-0054 §8: a route is checked again where it is applied, and is void if it fails
  ELSE IF ~WfAdmitCheck(s, e) THEN Rej(s)
  ELSE IF ~CheckLive(s, e) THEN Rej(s)
  ELSE IF e.action.kind \in RunEffects /\ Coupled(SeatKindOf(s, e.seat)) /\ ~ObserverCovers(s, e.seat) THEN Rej(s)
  ELSE IF e.action.kind = "Actuate" /\ ~ChannelFidelity(s, e.lease, e.action.tool) THEN Rej(s)
  \* ADR-0047 §1, §4: no Run delivery is unlabelled, and the floor's answer was about the clearSet
  \* the admit names; if the round's has grown since, the admit is refused
  ELSE IF e.action.kind \in {"Consult", "Actuate"}
          /\ (IsNone(e.labels) \/ e.labels.clearSet # s.leases[e.lease].clearSet) THEN Rej(s)
  \* ADR-0034 §3.5: under a session key, the attested guest's proof with a fresh counter
  ELSE IF HasKey(s.leases[e.lease])
          /\ (IsNone(e.session) \/ ~e.proofOk \/ e.session.ctr <= s.leases[e.lease].sessionCtr) THEN Rej(s)
  ELSE LET f   == e.lease
           a   == e.action
           lr1 == [s.leases[f] EXCEPT !.actions = @ + 1,
                                      !.sessionCtr = IF HasKey(s.leases[f]) THEN e.session.ctr ELSE @]
           item == [label |-> e.labels.resultLabel, delivery |-> e.labels.delivery]
           \* ADR-0047 §4: what is delivered clear joins clearSet, at admit
           Read(cs) == IF e.labels.delivery = "clear" THEN cs \cup e.labels.resultLabel ELSE cs
           r == CASE a.kind \in {"Emit", "Report", "Route"} ->
               LET lr2 == [lr1 EXCEPT !.seq = @ + 1]
               IN [st |-> [s EXCEPT !.leases = Put(@, f, lr2)], res |-> Admitted(lr2.seq, NONE)]
          [] a.kind = "Finding" ->
               LET lr2 == [lr1 EXCEPT !.seq = @ + 1]
               IN [st |-> WorkflowFinding([s EXCEPT !.leases = Put(@, f, lr2)], a.topic), res |-> Admitted(lr2.seq, NONE)]
          [] a.kind = "Actuate" ->
               LET lr2 == [lr1 EXCEPT !.seq = @ + 1, !.results = Put(@, lr1.seq + 1, item), !.clearSet = Read(@)]
               IN [st |-> [s EXCEPT !.leases = Put(@, f, lr2)], res |-> Admitted(lr2.seq, NONE)]
          [] a.kind = "Consult" ->
               LET lr2 == [lr1 EXCEPT !.consults = Put(@, a.object, item), !.clearSet = Read(@)]
               IN [st |-> [s EXCEPT !.leases = Put(@, f, lr2)], res |-> Admitted(NONE, NONE)]
          [] a.kind = "Heartbeat" ->
               LET lr2   == [lr1 EXCEPT !.seq = @ + 1]
                   marks == Put(s.marks, e.seat, Put(IF e.seat \in DOMAIN s.marks THEN s.marks[e.seat] ELSE EmptyFn, a.topic, a.watermark))
                   s1    == [s EXCEPT !.leases = Put(@, f, lr2), !.marks = marks]
                   authors == {x \in DOMAIN s1.seals : s1.seals[x].topic = a.topic}
                   promo == {art \in DOMAIN s1.candidates :
                               /\ s1.candidates[art].author \in authors
                               /\ IsNone(s1.candidates[art].promotedAt)
                               /\ TallyPromoted(s1, s1.candidates[art], AuthorCovered(s1, s1.candidates[art].author))}
                   cands == [art \in DOMAIN s1.candidates |->
                               IF art \in promo THEN [s1.candidates[art] EXCEPT !.promotedAt = idx] ELSE s1.candidates[art]]
               IN [st  |-> [s1 EXCEPT !.candidates = cands],
                   res |-> Admitted(lr2.seq, IF promo = {} THEN NONE ELSE CHOOSE x \in promo : TRUE)]
          [] a.kind = "Submit" ->
               LET c  == [artifact |-> a.artifact, author |-> e.seat, votes |-> EmptyFn, promotedAt |-> NONE]
                   s1 == [s EXCEPT !.leases = Put(@, f, lr1), !.candidates = Put(@, a.artifact, c)]
               IN [st |-> EndLease(s1, f, "submitted"), res |-> Admitted(NONE, NONE)]
          [] a.kind = "Vote" ->
               LET c0      == s.candidates[a.artifact]
                   covered == AuthorCovered(s, c0.author)
                   c1      == [c0 EXCEPT !.votes = Put(@, e.seat, [verdict |-> a.verdict, evidence |-> a.evidence, rulesEpoch |-> a.rulesEpoch])]
                   prom    == TallyPromoted(s, c1, covered)
                   c2      == IF prom THEN [c1 EXCEPT !.promotedAt = idx] ELSE c1
                   s1      == [s EXCEPT !.leases = Put(@, f, lr1), !.candidates = Put(@, a.artifact, c2)]
               IN [st |-> EndLease(s1, f, "voted"), res |-> Admitted(NONE, IF prom THEN a.artifact ELSE NONE)]
          [] OTHER ->
               [st |-> [s EXCEPT !.leases = Put(@, f, lr1)], res |-> Admitted(NONE, NONE)]
       IN IF f \in DOMAIN s.wfBindings
            THEN [st |-> WorkflowAdmitted(r.st, idx, f, a, r.res.seq), res |-> r.res] ELSE r

ApplyEndRound(s, e) ==
  IF e.reason = "abstained" /\ SeatDomain(s, e.seat) = "run" THEN Rej(s)
  ELSE IF e.fence \in DOMAIN s.leases /\ s.leases[e.fence].seat = e.seat /\ s.leases[e.fence].ended = NONE
         THEN [st |-> EndLease(s, e.fence, e.reason), res |-> [kind |-> "RoundEnded"]]
         ELSE Rej(s)

ApplyIssue(s, e) ==
  IF ~e.ok THEN Rej(s)
  ELSE LET r  == e.rules
           s1 == [s EXCEPT !.rulesEpoch = r.rulesEpoch, !.seats = r.seats, !.grantRoster = r.grantRoster,
                           !.vetoRoster = r.vetoRoster, !.quorum = r.quorum, !.minGrant = r.minGrant,
                           !.bgIssued = r.bgIssued, !.bgRoster = r.bgRoster, !.bgQuorum = r.bgQuorum,
                           !.verifierKeys = r.verifierKeys, !.bundleKeys = r.bundleKeys,
                           !.personas = r.personas, !.criterion = r.criterion]
       IN [st |-> EndAllLive(s1, "rules_changed"), res |-> [kind |-> "Issued", rulesEpoch |-> r.rulesEpoch]]

\* --- the control alphabet (ADR-0050 §4; control.rs, State::control_facts, apply_control) ---

NoFacts(s, e) ==
  LET op == e.operator IN
  [personaInForce |-> Seated(s, op), hasLease |-> HasLive(s, op),
   peerLive |-> LiveOperators(s, SeatDomain(s, op)) \ {op} # {},
   freshAssertion |-> e.freshOk,
   targetSeated |-> FALSE, targetLive |-> FALSE, sameBinding |-> FALSE, nextRound |-> FALSE,
   lastAlphabet |-> {}, newAlphabet |-> {}, taskLabelled |-> FALSE, taskLabel |-> {},
   taskLabelsAllowed |-> {}, domain |-> SeatDomain(s, op), targetDomain |-> NONE, targetSeat |-> NONE]

OnSeat(s, f, seat) ==
  [f EXCEPT !.targetSeat = seat, !.targetDomain = SeatDomain(s, seat),
            !.targetSeated = Seated(s, seat), !.targetLive = HasLive(s, seat)]

HasLast(s, seat) == seat \in DOMAIN s.lastLease /\ s.lastLease[seat] \in DOMAIN s.leases
LastOf(s, seat)  == s.leases[s.lastLease[seat]]

\* The seats a revocation's target is seated at, in the operator's domain or outside it
SeatedAt(s, t, dom, outside) ==
  {x \in DOMAIN s.seatings :
     /\ TargetMatches(t, s.seatings[x])
     /\ SeatDomain(s, x) # NONE
     /\ (SeatDomain(s, x) # dom) = outside}

\* State::control_facts. `ok` is FALSE where the code returns an error and computes none.
\* A revocation is lifted on a seat the target is seated at, one outside the operator's domain
\* if there is one, so that C9 sees a revocation that reaches outside it. Which of several such
\* seats is the code's choice, taken from the carried facts and checked to be one of them.
ControlFacts(s, e) ==
  LET op   == e.operator
      a    == e.action
      base == NoFacts(s, e)
      dom  == SeatDomain(s, op)
      bad  == [ok |-> FALSE, f |-> base]
      good(f) == [ok |-> TRUE, f |-> f]
  IN IF e.epoch # s.epoch THEN bad
     ELSE CASE a.kind = "Regrant" ->
            IF SeatKindOf(s, a.target) = "emergency" THEN bad   \* ADR-0052 §3: no successor
            ELSE IF SeatDomain(s, a.target) = NONE THEN bad
            ELSE LET f1 == OnSeat(s, base, a.target)
                     f2 == IF a.target \in DOMAIN s.seatings /\ HasLast(s, a.target)
                             THEN [f1 EXCEPT !.sameBinding = SameBinding(s.seatings[a.target], LastOf(s, a.target)),
                                             !.nextRound = LastOf(s, a.target).round + 1 = a.round,
                                             !.lastAlphabet = LastOf(s, a.target).alphabet,
                                             !.taskLabelsAllowed = s.seatings[a.target].taskLabels]
                             ELSE f1
                 IN good([f2 EXCEPT !.newAlphabet = a.alphabet, !.taskLabelled = a.taskLabelled,
                                    !.taskLabel = a.taskLabel])
          [] a.kind = "Renew" ->
            IF SeatKindOf(s, a.target) = "emergency" THEN bad   \* ADR-0052 §3: no renewal
            ELSE IF SeatDomain(s, a.target) = NONE THEN bad
            ELSE LET f1 == OnSeat(s, base, a.target)
                 IN good([f1 EXCEPT !.lastAlphabet = IF HasLast(s, a.target) THEN LastOf(s, a.target).alphabet ELSE {},
                                    !.newAlphabet = a.alphabet])
          [] a.kind = "EndRound" ->
            IF SeatDomain(s, a.target) = NONE THEN bad ELSE good(OnSeat(s, base, a.target))
          [] a.kind = "Revoke" ->
            LET outside == SeatedAt(s, a.target, dom, TRUE)
                inside  == SeatedAt(s, a.target, dom, FALSE)
                picked  == e.facts.targetSeat
            IN IF outside \cup inside = {} THEN bad
               ELSE IF outside # {} THEN (IF picked \in outside THEN good(OnSeat(s, base, picked)) ELSE bad)
               ELSE (IF picked \in inside THEN good(OnSeat(s, base, picked)) ELSE bad)
          [] OTHER -> good(base)                                \* AttestGates, FenceEpoch

\* ControlFacts::permitted: the envelope of C1 to C9, restated at apply
Permitted(f, a, op) ==
  LET own    == f.domain # NONE /\ f.domain = f.targetDomain
      isSelf == f.targetSeat = op
      isAdd  == a.kind \in {"Regrant", "Renew", "AttestGates"}
      c5     == isAdd => (f.hasLease /\ f.peerLive)
      deny   == f.personaInForce /\ (f.hasLease \/ f.freshAssertion)
  IN /\ c5
     /\ CASE a.kind = "Regrant" ->
               /\ ~isSelf                                                   \* C6
               /\ f.taskLabelled /\ f.taskLabel \subseteq f.taskLabelsAllowed  \* C8
               /\ own /\ f.targetSeated /\ ~f.targetLive /\ f.sameBinding /\ f.nextRound
               /\ f.newAlphabet \subseteq f.lastAlphabet                     \* C1
          [] a.kind = "Renew"       -> ~isSelf /\ own /\ f.targetLive       \* C6, C2
          [] a.kind = "AttestGates" -> f.domain = "build"                  \* C3
          [] a.kind = "FenceEpoch"  -> f.hasLease /\ deny                   \* C7, C4
          [] OTHER                  -> own /\ deny                          \* C9, C4: EndRound, Revoke

\* State::apply_control
ApplyControl(s, idx, e) ==
  LET op == e.operator
      a  == e.action
  IN IF SeatKindOf(s, op) # "operator" THEN Rej(s)
     ELSE IF ~e.sigOk THEN Rej(s)
     ELSE IF e.ctr <= Ctr(s, op) THEN Rej(s)
     ELSE LET cf == ControlFacts(s, e) IN
       IF ~cf.ok THEN Rej(s)
       ELSE IF cf.f # e.facts THEN Rej(s)                 \* decided on facts that no longer hold
       ELSE IF ~Permitted(cf.f, a, op) THEN Rej(s)
       ELSE LET s1 == [s EXCEPT !.controlCtr = Put(@, op, e.ctr)] IN
         CASE a.kind = "Regrant" ->
                IF IsNone(e.grant) \/ a.target \notin DOMAIN s1.seatings THEN Rej(s1)
                ELSE LET g  == e.grant
                         sg == s1.seatings[a.target]
                         asked  == /\ g.seat = a.target /\ g.round = a.round /\ g.alphabet = a.alphabet
                                   /\ g.ttl = a.ttl /\ g.taskLabelled = a.taskLabelled
                                   /\ g.taskLabel = a.taskLabel /\ e.signOnSame
                         seated == SameBinding(g, sg) /\ g.role = sg.role
                     IN IF ~(asked /\ seated) THEN Rej(s1) ELSE ApplyGrant(s1, idx, g)
           [] a.kind = "Renew" ->
                IF IsNone(e.renew) THEN Rej(s1)
                ELSE LET r == e.renew IN
                  IF r.seat # a.target \/ r.alphabet # a.alphabet \/ r.ttl # a.ttl THEN Rej(s1)
                  ELSE IF SeatKindOf(s1, a.target) = "operator" /\ ~e.targetSignOnOk THEN Rej(s1)
                  ELSE ApplyRenew(s1, idx, r)
           [] a.kind = "AttestGates" ->
                [st |-> [s1 EXCEPT !.gates = Put(@, a.artifact, a.evidence)], res |-> [kind |-> "GatesRecorded"]]
           [] a.kind = "EndRound" ->
                IF HasLive(s1, a.target)
                  THEN [st |-> EndLease(s1, s1.liveBySeat[a.target], "operator"), res |-> [kind |-> "RoundEnded"]]
                  ELSE Rej(s1)
           [] a.kind = "Revoke" -> ApplyRevoke(s1, [target |-> a.target])
           [] a.kind = "FenceEpoch" ->
                [st |-> EndAllLive([s1 EXCEPT !.epoch = @ + 1], "fenced"),
                 res |-> [kind |-> "EpochIncremented", epoch |-> s1.epoch + 1]]

\* --- the emergency seating (ADR-0052; State::apply_activate) --------------------------

\* State::apply_activate: the roster's quorum seats one named person for one round
ApplyActivate(s, idx, e) ==
  IF SeatKindOf(s, e.seat) # "emergency" THEN Rej(s)
  ELSE IF e.seat \notin DOMAIN s.emSeatings THEN Rej(s)
  ELSE LET sg == s.emSeatings[e.seat] IN
    IF e.epoch # s.epoch THEN Rej(s)
    ELSE IF e.person \notin sg.persons THEN Rej(s)
    ELSE IF ~s.bgIssued THEN Rej(s)
    ELSE IF Cardinality(e.approvers) < s.bgQuorum THEN Rej(s)
    ELSE IF e.taskSome /\ ~e.taskLabelled THEN Rej(s)            \* ADR-0047 §1
    ELSE IF e.taskLabelled /\ ~(e.taskLabel \subseteq sg.taskLabels) THEN Rej(s)
    ELSE IF ~sg.envDomain /\ ~(DOMAIN e.envelope = sg.envNamed /\ \A t \in DOMAIN e.envelope : e.envelope[t] = sg.bundle)
      THEN Rej(s)
    ELSE LET g == [principal |-> e.person, seat |-> e.seat, persona |-> e.persona, bundle |-> sg.bundle,
                   conf |-> e.conf, rung |-> 0, alphabet |-> {"Consult", "Actuate", "Report"},
                   ttl |-> e.ttl, round |-> e.round, role |-> "author",
                   taskLabelled |-> e.taskLabelled, taskLabel |-> e.taskLabel, taskLabelsAllowed |-> {},
                   signOnOk |-> FALSE, appraisal |-> NONE, sigOk |-> FALSE, sigKey |-> NONE]
             r == ApplyGrant(s, idx, g)
         IN IF r.res.kind # "LeaseGranted" THEN r
            ELSE LET seating == [SeatingOf(g) EXCEPT !.taskLabels = sg.taskLabels]
                     rec == [at |-> idx, seat |-> e.seat, person |-> e.person, epoch |-> e.epoch,
                             round |-> e.round, approvers |-> e.approvers, drill |-> sg.drill]
                 IN [st  |-> [r.st EXCEPT !.leases = [@ EXCEPT ![idx].person = e.person, ![idx].envelope = e.envelope],
                                          !.seatings = Put(@, e.seat, seating),
                                          !.activations = Append(@, rec)],
                     res |-> r.res]

\* The unsigned grant: the BOOTSTRAP path's first seating (ADR-0050 §2)
ApplySeating(s, idx, e) ==
  IF SeatKindOf(s, e.seat) = "emergency" THEN Rej(s)             \* leased only by an activation
  ELSE IF NotAFirstSeating(s, e) THEN Rej(s)
  ELSE LET r == ApplyGrant(s, idx, e) IN
    IF r.res.kind # "LeaseGranted" THEN r
    ELSE [st |-> [r.st EXCEPT !.seatings = Put(@, e.seat, SeatingOf(e))], res |-> r.res]

\* ADR-0050 §4: where the rules declare an operator, the unsigned path seats and does nothing
\* else. What the mechanism orders for itself stays: an expiry, an abstention, a terminal vote,
\* a re-attestation at renewal, a Contested verdict.
Unsigned(e) ==
  \/ e.kind = "Renew" /\ IsNone(e.appraisal)
  \/ e.kind = "EndRound" /\ e.reason = "operator"
  \/ e.kind \in {"Revoke", "EpochIncrement", "GatesPassed"}

\* State::apply_contested (ADR-0034 §3.3, §3.7): a signed rung-3 Contested revokes the principal
ApplyContested(s, e) ==
  LET a == e.appraisal IN
  IF a.verdict # "contested" THEN Rej(s)
  ELSE IF a.rung <= 2 THEN Rej(s)
  ELSE IF ~(e.sigOk /\ e.sigKey \in s.verifierKeys) THEN Rej(s)
  ELSE LET r == ApplyRevoke(s, [target |-> [kind |-> "principal", id |-> a.principal]])
       IN [st  |-> [r.st EXCEPT !.contested = Put(@, a.principal, a.evidence)],
           res |-> [kind |-> "Contested", ended |-> r.res.ended]]

\* State::apply_profile_register (ADR-0034 §1): only a promoted artifact is a reference value
ApplyProfileRegister(s, idx, e) ==
  IF ~e.ok THEN Rej(s)
  ELSE IF ~(e.artifact \in DOMAIN s.candidates /\ ~IsNone(s.candidates[e.artifact].promotedAt)) THEN Rej(s)
  ELSE [st  |-> IF e.digest \in DOMAIN s.profiles THEN s
                ELSE [s EXCEPT !.profiles = Put(@, e.digest,
                        [artifact |-> e.artifact, summary |-> e.profile, registeredAt |-> idx])],
        res |-> [kind |-> "ProfileRegistered", digest |-> e.digest]]

\* State::apply_workflow_load (ADR-0054 §1, §2): only from a promoted single-file workspace, and
\* only if every load check passes. `ok`, the workflow's digest, its artifact and what its text
\* parses to are the trace's.
ApplyWorkflowLoad(s, idx, e) ==
  IF ~(e.artifact \in DOMAIN s.candidates /\ ~IsNone(s.candidates[e.artifact].promotedAt)) THEN Rej(s)
  ELSE IF ~e.ok THEN Rej(s)
  ELSE IF ~(e.outward \subseteq NodeNames(e.def)) THEN Rej(s)
  ELSE IF e.workflow \in DOMAIN s.workflows THEN Rej(s)
  ELSE LET declared == {e.def.nodes[k].name : k \in {k \in DOMAIN e.def.nodes : e.def.nodes[k].outward}}
           root == [node |-> e.def.root, trig |-> NONE, via |-> NONE, fired |-> {}, status |-> "ready",
                    fence |-> NONE, hist |-> {0}, createdAt |-> idx, clearInputs |-> {}, handleInputs |-> {},
                    attrs |-> NONE, found |-> FALSE, seal |-> NONE, covered |-> FALSE]
           run  == [def |-> e.def, artifact |-> e.artifact, loadedAt |-> idx, epoch |-> s.epoch,
                    rulesEpoch |-> s.rulesEpoch, outward |-> declared \cup e.outward, status |-> "running",
                    acts |-> <<root>>, events |-> EmptyFn, charged |-> 0, chargedNode |-> EmptyFn,
                    exhausted |-> FALSE, evaluated |-> {}]
       IN [st  |-> [s EXCEPT !.workflows = Put(@, e.workflow, run)],
           res |-> [kind |-> "WorkflowLoaded", workflow |-> e.workflow]]

\* workflow::grant_for: the grant a slot is entitled to, as far as the trace projects a grant
GrantFor(sg, round, clear) ==
  [principal |-> sg.principal, seat |-> sg.seat, persona |-> sg.persona, bundle |-> sg.bundle, conf |-> sg.conf,
   rung |-> sg.rung, alphabet |-> sg.alphabet, ttl |-> sg.ttl, round |-> round, role |-> "author",
   taskLabelled |-> TRUE, taskLabel |-> sg.taskLabel \cup clear, taskLabelsAllowed |-> {}]
SameGrant(w, g) == \A x \in DOMAIN w : w[x] = g[x]

\* `fail` in apply_workflow_grant: the slot fails, nothing stands in, and the workflow moves
FailSlot(s, idx, e, run) ==
  LET run2 == IF e.slot = "node" THEN [run EXCEPT !.acts[e.act + 1].status = "failed"]
              ELSE [run EXCEPT !.events = Put(@, e.act, FailedEvent)]
  IN [st |-> Advance([s EXCEPT !.workflows = Put(@, e.workflow, run2)], idx), res |-> [kind |-> "WorkflowFailed"]]

\* State::apply_workflow_grant (ADR-0054 §2; ADR-0024 A4, ADR-0031 A4, pending). A slot that is
\* not ready, or must wait, is refused and nothing changes. Otherwise the grant is made under the
\* promotion; one the budget or a grant check refuses fails the slot.
ApplyWorkflowGrant(s, idx, e) ==
  IF e.workflow \notin DOMAIN s.workflows THEN Rej(s)
  ELSE LET run == s.workflows[e.workflow] IN
    IF run.status # "running" THEN Rej(s)
    ELSE IF e.slot = "node" /\ ~(e.act < NActs(run) /\ ActAt(run, e.act).status = "ready") THEN Rej(s)
    ELSE IF e.slot = "decision" /\ ~(e.act \in DOMAIN run.events /\ run.events[e.act].state = "open") THEN Rej(s)
    \* ADR-0054 §3: decision events are served in log order
    ELSE IF e.slot = "decision" /\ (\E x \in DOMAIN run.events : x < e.act /\ run.events[x].state = "open") THEN Rej(s)
    ELSE IF e.slot = "decision" /\ IsNone(run.def.orchestrator) THEN Rej(s)
    ELSE LET sg     == IF e.slot = "node" THEN NodeOf(run, ActAt(run, e.act).node) ELSE run.def.orchestrator
             node   == IF e.slot = "node" THEN ActAt(run, e.act).node ELSE "orchestrator"
             clear  == IF e.slot = "node" THEN ActAt(run, e.act).clearInputs ELSE {}
             round  == IF sg.seat \in DOMAIN s.lastRound THEN s.lastRound[sg.seat] + 1 ELSE 1
             \* waits, not failures: the seat or its principal holds a live lease, or the seat's
             \* last round is not yet read to its seal
             busy   == \/ sg.seat \in DOMAIN s.liveBySeat
                       \/ \E x \in DOMAIN s.liveBySeat : s.leases[s.liveBySeat[x]].principal = sg.principal
             unread == /\ sg.seat \in DOMAIN s.seals
                       /\ ~(\E o \in CellObservers(s, sg.seat) : Mark(s, o, s.seals[sg.seat].topic) >= s.seals[sg.seat].seq)
         IN IF ~SameGrant(GrantFor(sg, round, clear), e.grant) THEN Rej(s)
            ELSE IF busy THEN Rej(s)
            ELSE IF unread THEN Rej(s)
            \* ADR-0024 A4: a fence, or a change of rules, voids what the workflow has not issued
            ELSE IF run.epoch # s.epoch \/ run.rulesEpoch # s.rulesEpoch THEN FailSlot(s, idx, e, run)
            ELSE LET c == Charge(run, node) IN
              IF ~c.ok THEN FailSlot(s, idx, e, c.run)
              ELSE LET r == ApplyGrant([s EXCEPT !.workflows = Put(@, e.workflow, c.run)], idx, e.grant) IN
                IF r.res.kind # "LeaseGranted" THEN FailSlot(r.st, idx, e, c.run)
                ELSE LET run2 == IF e.slot = "node"
                                   THEN [c.run EXCEPT !.acts[e.act + 1].status = "running", !.acts[e.act + 1].fence = idx]
                                   ELSE [c.run EXCEPT !.events = Put(@, e.act, [state |-> "served", fence |-> idx, edge |-> NONE])]
                         bind == [workflow |-> e.workflow, slot |-> e.slot, act |-> e.act, actuates |-> 0,
                                  reports |-> <<>>, outcome |-> NONE, lifted |-> FALSE]
                     IN [st  |-> [r.st EXCEPT !.workflows = Put(@, e.workflow, run2), !.wfBindings = Put(@, idx, bind)],
                         res |-> r.res]

\* State::apply_entry
ApplyRaw(s0, idx, e) ==
  LET s == [s0 EXCEPT !.lastApplied = idx] IN
  IF e.id \in s.appliedIds THEN [st |-> s, res |-> [kind |-> "Duplicate"]]
  ELSE LET s1 == [s EXCEPT !.appliedIds = @ \cup {e.id}] IN
    IF OperatorsDeclared(s1) /\ Unsigned(e) THEN Rej(s1)
    ELSE
    CASE e.kind = "Grant"             -> ApplySeating(s1, idx, e)
      [] e.kind = "Control"           -> ApplyControl(s1, idx, e)
      [] e.kind = "Activate"          -> ApplyActivate(s1, idx, e)
      [] e.kind = "EmergencySeating"  ->
           IF SeatKindOf(s1, e.seat) # "emergency" THEN Rej(s1)
           ELSE [st |-> [s1 EXCEPT !.emSeatings = Put(@, e.seat, e.seating)], res |-> [kind |-> "EmergencyPrepared"]]
      [] e.kind = "Renew"             -> ApplyRenew(s1, idx, e)
      [] e.kind = "Admit"             -> ApplyAdmit(s1, idx, e)
      [] e.kind = "EndRound"          -> ApplyEndRound(s1, e)
      [] e.kind = "Revoke"            -> ApplyRevoke(s1, e)
      [] e.kind = "EpochIncrement"    -> [st |-> EndAllLive([s1 EXCEPT !.epoch = @ + 1], "fenced"),
                                          res |-> [kind |-> "EpochIncremented", epoch |-> s1.epoch + 1]]
      [] e.kind = "Issue"             -> ApplyIssue(s1, e)
      [] e.kind = "GatesPassed"       -> [st |-> [s1 EXCEPT !.gates = Put(@, e.artifact, e.evidence)],
                                          res |-> [kind |-> "GatesRecorded"]]
      [] e.kind = "BreakGlassApprove" -> Rej(s1)       \* X1 is retired (ADR-0052 §2)
      [] e.kind = "Contested"         -> ApplyContested(s1, e)
      [] e.kind = "ProfileRegister"   -> ApplyProfileRegister(s1, idx, e)
      [] e.kind = "WorkflowLoad"      -> ApplyWorkflowLoad(s1, idx, e)
      [] e.kind = "WorkflowGrant"     -> ApplyWorkflowGrant(s1, idx, e)

\* State::apply_inner: whatever the entry changed, each running workflow moves as far as it can,
\* in the same apply; a duplicate changed nothing (ADR-0054, ADR-0055). The projection carries
\* `contained`, which the model recomputes after every step.
Apply(s0, idx, e) ==
  LET r  == ApplyRaw(s0, idx, e)
      s1 == IF DOMAIN r.st.workflows # {} /\ r.res.kind # "Duplicate" THEN Advance(r.st, idx) ELSE r.st
  IN [st |-> [s1 EXCEPT !.contained = ContainedSet(s1)], res |-> r.res]

\* --- trace validation ---------------------------------------------------------

VARIABLES st, i
vars == <<st, i>>

TraceInit == st = InitState /\ i = 0
TraceStep == /\ i < Len(Trace)
             /\ st' = Apply(st, Trace[i + 1].index, Trace[i + 1].entry).st
             /\ i' = i + 1
Done      == i = Len(Trace) /\ UNCHANGED vars
TraceNext == TraceStep \/ Done
TraceSpec == TraceInit /\ [][TraceNext]_vars

\* Violated at the first step whose model result differs from the recorded one.
TraceMatches ==
  \/ i = Len(Trace)
  \/ LET step == Trace[i + 1]
         r    == Apply(st, step.index, step.entry)
     IN r.st = step.state /\ r.res = step.applied
=============================================================================
