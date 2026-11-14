------------------------------ MODULE PaxosTrace ------------------------------
(* Trace validation of the reference's replica against `Paxos.tla`: stage one   *)
(* of a refinement, as `Mechanism.tla` is for the admit path (ADR-0045          *)
(* T-0045-28). The reference's simulation (mechanism/crates/topak-paxos/        *)
(* tests/sim.rs) records one event per call of `Replica::handle`, across every  *)
(* replica of a run and in the order the calls were made: what the call was     *)
(* given, the replica's state after it (`Replica::snapshot`), and what it sent. *)
(* `TraceSpec` replays the events through the operators `Paxos.tla`'s `Next` is *)
(* made of, without that module's bounds, and three invariants compare:         *)
(*   TraceReceivable    what a replica was given could be given: a message      *)
(*                      received was sent, a forward received or duplicated was *)
(*                      in flight, an election was a non-leader's and a         *)
(*                      heartbeat a leader's;                                   *)
(*   TraceStateMatches  the replica's state after the call is the model's,      *)
(*                      field for field, and so is its `next_deliver`;          *)
(*   TraceSendsMatch    the call sent exactly the messages the model sends, and *)
(*                      the same forwards in the same order.                    *)
(* Each is stated of the event about to be replayed, so the first violated one  *)
(* names the first event the code and the model disagree on. `Safe` is checked  *)
(* on the replayed states as well, over the ghosts the model keeps.             *)
(*                                                                              *)
(* Events (`ev`), and the fields each has besides `node`:                       *)
(*   hand   value                      the host proposed at the replica         *)
(*   elect                             a tick that started an election          *)
(*   beat                              a tick that sent a heartbeat             *)
(*   recv   msg                        a message from another replica           *)
(*   fwd    from, value                a forward from another replica           *)
(*   dup    from, to, value            the network duplicated a forward         *)
(*   crash                             the replica restarted                    *)
(* All but `dup` have `after`; all but `dup` and `crash` have `nextDeliver`,    *)
(* `sent` and `fwds`. A tick that did nothing is not an event: the model has no *)
(* clock. A message the network dropped or delayed is not one either.           *)
(*                                                                              *)
(* What this is not: a proof, or a claim about a run that was not recorded. A   *)
(* trace that validates shows the code agreed with the model on that run. The   *)
(* host in these runs is the simulation's, not `topak-node`'s driver and WAL.   *)
EXTENDS Paxos, TLC

CONSTANT Trace
VARIABLE i
tvars == <<vars, i>>

Pending == i < Len(Trace)

\* The context one event's call of `handle` ends in.
EventCtx(e) ==
  LET r == e.node
  IN CASE e.ev = "hand"  -> Drain(r, Propose(r, Ctx(st[r]), e.value))
       [] e.ev = "elect" -> Drain(r, StartElection(r, Ctx(st[r])))
       [] e.ev = "beat"  -> Drain(r, BeatCtx(r, Ctx(st[r])))
       [] e.ev = "recv"  -> Drain(r, OnMsg(r, Ctx(st[r]), e.msg))
       [] e.ev = "fwd"   -> Drain(r, OnMsg(r, Ctx(st[r]), ForwardMsg(e.from, r, e.value)))

TraceInit == Init /\ i = 0

TraceStep ==
  /\ Pending
  /\ i' = i + 1
  /\ LET e == Trace[i + 1]
     IN \/ /\ e.ev = "crash"
           /\ st' = [st EXCEPT ![e.node] = Recovered(@)]
           /\ crashes' = crashes + 1
           /\ UNCHANGED <<msgs, fwd, votes, learned, handed, assigned, duped>>
        \/ /\ e.ev = "dup"
           /\ fwd' = [fwd EXCEPT ![<<e.from, e.to, e.value>>] = @ + 1]
           /\ duped' = [duped EXCEPT ![e.value] = @ + 1]
           /\ UNCHANGED <<st, msgs, votes, learned, handed, assigned, crashes>>
        \/ /\ e.ev = "hand"
           /\ Effect(e.node, EventCtx(e), << >>)
           /\ handed' = [handed EXCEPT ![e.value] = @ + 1]
           /\ UNCHANGED <<duped, crashes>>
        \/ /\ e.ev = "fwd"
           /\ Effect(e.node, EventCtx(e), <<e.from, e.node, e.value>>)
           /\ UNCHANGED <<handed, duped, crashes>>
        \/ /\ e.ev \in {"elect", "beat", "recv"}
           /\ Effect(e.node, EventCtx(e), << >>)
           /\ UNCHANGED <<handed, duped, crashes>>

Done      == ~Pending /\ UNCHANGED tvars
TraceNext == TraceStep \/ Done
TraceSpec == TraceInit /\ [][TraceNext]_tvars

TraceReceivable ==
  Pending =>
    LET e == Trace[i + 1]
    IN /\ e.ev = "recv"  => e.msg \in msgs
       /\ e.ev = "fwd"   => fwd[<<e.from, e.node, e.value>>] > 0
       /\ e.ev = "dup"   => fwd[<<e.from, e.to, e.value>>] > 0
       /\ e.ev = "elect" => st[e.node].role # "leader"
       /\ e.ev = "beat"  => st[e.node].role = "leader"

TraceStateMatches ==
  Pending =>
    LET e == Trace[i + 1]
    IN CASE e.ev = "dup"   -> TRUE
         [] e.ev = "crash" -> Recovered(st[e.node]) = e.after
         [] OTHER          -> /\ EventCtx(e).s = e.after
                              /\ NextDeliver(EventCtx(e).s) = e.nextDeliver

TraceSendsMatch ==
  Pending =>
    LET e == Trace[i + 1]
    IN e.ev \notin {"dup", "crash"} => EventCtx(e).out = e.sent /\ EventCtx(e).fwd = e.fwds
================================================================================
