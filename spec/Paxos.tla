--------------------------------- MODULE Paxos ---------------------------------
(* The consensus log at the message level: the `Paxos` module Theory of        *)
(* Operation 11.3 puts over `Voting`, and that ADR-0033's finding 9 asks to    *)
(* model proposer retry (ADR-0033, section 7, Findings; mechanism/             *)
(* GAPS-AND-ASSUMPTIONS.md, section 4, finding 9). ADR-0033 section 2, row P,  *)
(* names the layering and section 3 the fault model.                           *)
(*                                                                             *)
(* This is an OPERATIONAL model of the reference's replica                     *)
(* (mechanism/crates/topak-paxos/src/replica.rs), written from its text, one   *)
(* operator per function there and in the same order of effects. A step is one *)
(* call of `Replica::handle`: the input's handler, then every message the      *)
(* replica addressed to itself, in the order it sent them (`Drain`), as the    *)
(* code's `local` queue does. `PaxosTrace.tla` replays the reference's         *)
(* recorded runs through the same operators (trace validation, stage one of a  *)
(* refinement, as `Mechanism.tla` is for the admit path), so what TLC checks   *)
(* below is checked of the model the code is compared with.                    *)
(*                                                                             *)
(* Fault model (ADR-0033 section 3; GAPS I1): crash-recovery, not Byzantine. A *)
(* replica may stop, lose volatile state and restart from durable acceptor     *)
(* state. It does not lie.                                                     *)
(*                                                                             *)
(* What is abstracted, and how:                                                *)
(*   time      No clock. `Elect` is a follower's or a candidate's election     *)
(*             timeout and `Beat` a leader's heartbeat interval, each enabled  *)
(*             whenever the role allows it: clocks buy liveness only (ADR-0032 *)
(*             section 1), so every timing is a behaviour here.                *)
(*   network   `msgs` only grows and any message in it can be received at any  *)
(*             time, any number of times: loss, delay, reordering, partition   *)
(*             and duplication. `Forward` is the exception, because receiving  *)
(*             one is not idempotent: forwards in flight are a bag (`fwd`), a  *)
(*             receipt takes one out, and the network duplicating one is the   *)
(*             explicit `DupForward`, counted in `duped`.                      *)
(*   crash     `Crash(r)` is a crash and the restart together: the replica     *)
(*             comes back with its durable acceptor state (promise and         *)
(*             accepted map) and nothing else. Being down is receiving nothing.*)
(*   the host  `Hand(r, v)` is the host proposing `v` at `r`, the first time   *)
(*             or again: the host retries what it has not seen decided under   *)
(*             an idempotent entry id (replica.rs, `step_down`). The host      *)
(*             makes every `Persist*` output durable before it transmits       *)
(*             (ADR-0033 section 3); M_NOPERSIST is a host that does not.      *)
(*   catch-up  `max_catchup` is not modelled: a catch-up answers with every    *)
(*             slot asked for.                                                 *)
(*   values    `Values` are positive naturals and `Noop` is 0. A ballot        *)
(*             (round, node) is the natural `round * (N + 1) + node`, so the   *)
(*             code's order on ballots is `<` and its default ballot is 0.     *)
(*                                                                             *)
(* Ghost variables record history the replicas do not keep: `votes` (every     *)
(* durable accept; the `Voting` layer's `votes`, as voting.rs keeps it),       *)
(* `learned` (every command a learner took for a slot), and three counters per *)
(* value (`handed`, `assigned`, `duped`).                                      *)
(*                                                                             *)
(* Properties, under Mut = "none":                                             *)
(*   OneValuePerBallot  `Voting`'s (voting.rs). Two votes in one slot at one   *)
(*                      ballot are for one command.                            *)
(*   ChosenUnique       `Voting`'s. A slot has at most one command voted for   *)
(*                      by a majority at one ballot.                           *)
(*   Agreement          No two learners, ever, take different commands for one *)
(*                      slot (across restarts: `learned` is not lost in a      *)
(*                      crash). The log is one log.                            *)
(*   LearnerSound       What a learner takes is chosen.                        *)
(*   OnlyHanded         What a learner takes is `Noop` or was handed in.       *)
(*   NoAmplification    Finding 9. Every fresh slot a value is put in is paid  *)
(*                      for by one hand-in from the host or one duplicate the  *)
(*                      network made: assigned[v] <= handed[v] + duped[v].     *)
(*                      Adopting a value in phase 1 keeps its slot and is not  *)
(*                      an assignment.                                         *)
(*   Safe               their conjunction, with TypeOK.                        *)
(*                                                                             *)
(* Mutations, one guard each, and what each must break:                        *)
(*   M_IGNOREPROMISED  a new leader ignores the values its promises report     *)
(*                     (the code's `IgnorePromisedValues`). Breaks             *)
(*                     ChosenUnique and Agreement.                             *)
(*   M_BELOWPROMISE    an acceptor accepts below its promise (the code's       *)
(*                     `AcceptBelowPromise`). Breaks ChosenUnique and          *)
(*                     Agreement.                                              *)
(*   M_NOPERSIST       a replica comes back from a crash without its durable   *)
(*                     state: the host sent before it persisted.               *)
(*                     Breaks ChosenUnique and Agreement.                      *)
(*   M_REQUEUE         a leader that steps down puts its in-flight values back *)
(*                     in its queue, as the first implementation did (finding  *)
(*                     9). Breaks NoAmplification, and no safety property: the *)
(*                     log stays a log and its backlog doubles each term.      *)
(* The first three keep OneValuePerBallot, LearnerSound, OnlyHanded and        *)
(* NoAmplification (`KeptUnderLogMutations`); M_REQUEUE keeps every property   *)
(* but its own (`KeptUnderRequeue`).                                           *)
(*                                                                             *)
(* Witnesses, each a property that must be VIOLATED under Mut = "none":        *)
(*   NeverChosen, NeverLearned, NeverSecondLeader, NeverAdopted (a new leader  *)
(*   re-proposes a command voted for at a lower ballot), NeverGapFilled (a     *)
(*   leader proposes `Noop`), NeverNacked, NeverForwarded, NeverCaughtUp,      *)
(*   NeverTwoSlots (a value handed in twice sits in two slots, which the       *)
(*   property allows and the host's entry id absorbs), NeverDuped.             *)
(*                                                                             *)
(* No liveness is stated. The reference's simulation checks delivery after the *)
(* network heals (tests/sim.rs); nothing here does.                            *)
(*                                                                             *)
(* Electors, Beaters, Hosts, Crashers, MaxRound, MaxHand, MaxDup and MaxCrash  *)
(* only cut the state space and are set in the run script. Every replica is an *)
(* acceptor and a learner, forwards, and sends the heartbeat `become_leader`   *)
(* sends, whatever those sets are. `Hand` also cuts by symmetry: values are    *)
(* only compared for equality, so the host hands a value in for the first time *)
(* only after every smaller one, which loses no behaviour up to renaming.      *)
EXTENDS Naturals, FiniteSets, Sequences

CONSTANTS Mut,       \* "none" or one mutation
          N,         \* the number of replicas; replicas are 1..N
          Values,    \* what the host may hand in
          Electors,  \* the replicas whose election timeout may fire
          Beaters,   \* the replicas whose heartbeat interval may fire
          Hosts,     \* the replicas the host hands values in at
          Crashers,  \* the replicas that may crash
          MaxRound,  \* no election beyond this round
          MaxHand,   \* the host hands a value in at most this many times
          MaxDup,    \* the network duplicates at most this many forwards
          MaxCrash   \* at most this many crashes

ASSUME NPositive      == N \in Nat \ {0}
ASSUME ValuesPositive == \A v \in Values : v \in Nat \ {0}

VARIABLES st,        \* st[r]: replica r's state, as replica.rs keeps it
          msgs,      \* every message sent to another replica, Forward excepted
          fwd,       \* fwd[<<from, to, v>>]: forwards of v in flight
          votes,     \* ghost: <<acceptor, slot, ballot, cmd>>, every durable accept
          learned,   \* ghost: <<slot, cmd>>, every command a learner took
          handed,    \* ghost: handed[v], hand-ins of v
          assigned,  \* ghost: assigned[v], fresh slots v was put in
          duped,     \* ghost: duped[v], forwards of v the network duplicated
          crashes    \* ghost: crashes so far (for MaxCrash)
vars == <<st, msgs, fwd, votes, learned, handed, assigned, duped, crashes>>

Replicas == 1..N
Noop     == 0
Majority == N \div 2 + 1

Bal(round, node) == round * (N + 1) + node
Round(b)         == b \div (N + 1)
Owner(b)         == b % (N + 1)

\* --- maps, as functions on a finite set of keys --------------------------------
EmptyMap     == [x \in {} |-> 0]
Put(f, k, v) == [x \in DOMAIN f \cup {k} |-> IF x = k THEN v ELSE f[x]]
Max(S)       == CHOOSE x \in S : \A y \in S : y <= x
Min(S)       == CHOOSE x \in S : \A y \in S : x <= y

RECURSIVE Sorted(_)
Sorted(S) == IF S = {} THEN << >> ELSE <<Min(S)>> \o Sorted(S \ {Min(S)})

\* --- a replica's state ---------------------------------------------------------
\* accepted: slot -> <<ballot, cmd>>.  chosen: slot -> cmd (the learner).
\* promises: node -> a set of <<slot, ballot, cmd>> (a candidate's).
\* inflight: slot -> [cmd, acks] (a leader's).  hint: the leader hint, 0 for none.
\* bal, from, promises, nextSlot and inflight are 0 or empty outside the role that
\* has them, so two states of the code that differ only there are one state here.
Fresh(promised, accepted) ==
  [promised |-> promised, accepted |-> accepted, chosen |-> EmptyMap, maxSeen |-> promised,
   role |-> "follower", bal |-> 0, from |-> 0, promises |-> EmptyMap,
   nextSlot |-> 0, inflight |-> EmptyMap, hint |-> 0, queue |-> << >>]

\* `next_deliver`: the first slot the learner has no command for. The code keeps it
\* as a field; it is this function of `chosen`, because `learn` ignores a slot below it.
NextDeliver(s) == Min({n \in 1..(Cardinality(DOMAIN s.chosen) + 1) : n \notin DOMAIN s.chosen})

\* --- messages ------------------------------------------------------------------
PrepareMsg(f, t, b, sl)     == [type |-> "prepare", from |-> f, to |-> t, bal |-> b, slot |-> sl]
PromiseMsg(f, t, b, acc)    == [type |-> "promise", from |-> f, to |-> t, bal |-> b, acc |-> acc]
NackMsg(f, t, rej, pro)     == [type |-> "nack", from |-> f, to |-> t, rejected |-> rej, promised |-> pro]
AcceptMsg(f, t, b, sl, cmd) == [type |-> "accept", from |-> f, to |-> t, bal |-> b, slot |-> sl, cmd |-> cmd]
AcceptedMsg(f, t, b, sl)    == [type |-> "accepted", from |-> f, to |-> t, bal |-> b, slot |-> sl]
CommitMsg(f, t, sl, cmd)    == [type |-> "commit", from |-> f, to |-> t, slot |-> sl, cmd |-> cmd]
HeartbeatMsg(f, t, b, nx)   == [type |-> "heartbeat", from |-> f, to |-> t, bal |-> b, next |-> nx]
CatchUpMsg(f, t, sl)        == [type |-> "catchup", from |-> f, to |-> t, slot |-> sl]
ForwardMsg(f, t, v)         == [type |-> "forward", from |-> f, to |-> t, value |-> v]

\* --- one call of `handle`, as a context ----------------------------------------
\* s: the replica's state.  out: messages sent to others.  local: messages sent to
\* itself, not yet handled.  fwd: forwards sent, as <<to, value>>.  votes, learned,
\* assigned: what this call adds to the ghosts.
Ctx(s) == [s |-> s, out |-> {}, local |-> << >>, fwd |-> << >>,
           votes |-> {}, learned |-> {}, assigned |-> << >>]

Send(c, m) == IF m.to = m.from THEN [c EXCEPT !.local = Append(@, m)]
                               ELSE [c EXCEPT !.out = @ \cup {m}]

\* `broadcast`: to every member in order. Only the place of the message to itself
\* among the replica's own sends is an order anything reads.
Broadcast(r, c, M(_)) ==
  [c EXCEPT !.out = @ \cup {M(t) : t \in Replicas \ {r}}, !.local = Append(@, M(r))]

\* `step_down`. M_REQUEUE puts the in-flight values back in the queue, in slot order.
StepDown(c) ==
  LET s    == c.s
      sl   == Sorted(DOMAIN s.inflight)
      cmds == [k \in 1..Len(sl) |-> s.inflight[sl[k]].cmd]
      back == IF Mut = "M_REQUEUE" /\ s.role = "leader"
              THEN SelectSeq(cmds, LAMBDA x : x # Noop) ELSE << >>
  IN [c EXCEPT !.s = [s EXCEPT !.role = "follower", !.bal = 0, !.from = 0, !.promises = EmptyMap,
                               !.nextSlot = 0, !.inflight = EmptyMap, !.queue = @ \o back]]

\* `observe`: note a ballot seen on the wire; step down if someone is ahead.
Observe(c, b) ==
  LET c1 == IF b > c.s.maxSeen THEN [c EXCEPT !.s.maxSeen = b] ELSE c
  IN IF c1.s.role # "follower" /\ b > c1.s.bal THEN StepDown(c1) ELSE c1

\* The leader's branch of `propose`: a fresh slot for v.
Assign(r, c, v) ==
  LET s  == c.s
      sl == s.nextSlot
      c1 == [c EXCEPT !.s.nextSlot = sl + 1,
                      !.s.inflight = Put(@, sl, [cmd |-> v, acks |-> {}]),
                      !.assigned = Append(@, v)]
  IN Broadcast(r, c1, LAMBDA t : AcceptMsg(r, t, s.bal, sl, v))

RECURSIVE AssignAll(_, _, _)
AssignAll(r, c, q) == IF q = << >> THEN c ELSE AssignAll(r, Assign(r, c, Head(q)), Tail(q))

\* `flush_queue`: a leader proposes its queue; a replica with a hint forwards it.
FlushQueue(r, c) ==
  LET s == c.s
  IN IF s.role = "leader" THEN AssignAll(r, [c EXCEPT !.s.queue = << >>], s.queue)
     ELSE IF s.hint # 0 /\ s.hint # r
          THEN [c EXCEPT !.s.queue = << >>,
                         !.fwd = @ \o [k \in 1..Len(s.queue) |-> <<s.hint, s.queue[k]>>]]
          ELSE c

\* `propose`.
Propose(r, c, v) ==
  IF c.s.role = "leader" THEN Assign(r, c, v)
  ELSE FlushQueue(r, [c EXCEPT !.s.queue = Append(@, v)])

\* `start_election`.
StartElection(r, c) ==
  LET b  == Bal(Round(c.s.maxSeen) + 1, r)
      c1 == StepDown([c EXCEPT !.s.maxSeen = b])
      fr == NextDeliver(c1.s)
      c2 == [c1 EXCEPT !.s.role = "candidate", !.s.bal = b, !.s.from = fr, !.s.hint = 0]
  IN Broadcast(r, c2, LAMBDA t : PrepareMsg(r, t, b, fr))

\* Accepts for the slots in sls, in order, each with its in-flight command.
RECURSIVE SendAccepts(_, _, _)
SendAccepts(r, c, sls) ==
  IF sls = << >> THEN c
  ELSE SendAccepts(r, Broadcast(r, c, LAMBDA t : AcceptMsg(r, t, c.s.bal, Head(sls),
                                                           c.s.inflight[Head(sls)].cmd)),
                   Tail(sls))

\* `become_leader`. Phase 1's purpose: for every slot from `from`, adopt the command
\* accepted at the highest ballot any promise reports; a slot nobody reports is a gap
\* and gets Noop. Among promises that report the highest ballot for a slot the code
\* takes the first in node order, which is what `first` is.
BecomeLeader(r, c) ==
  LET s       == c.s
      triples == UNION {s.promises[a] : a \in DOMAIN s.promises}
      seen    == IF Mut = "M_IGNOREPROMISED" THEN {} ELSE triples
      slots   == {t[1] : t \in seen}
      Best(sl) ==
        LET mb    == Max({t[2] : t \in {u \in seen : u[1] = sl}})
            first == Min({a \in DOMAIN s.promises : \E t \in s.promises[a] : t[1] = sl /\ t[2] = mb})
        IN (CHOOSE t \in s.promises[first] : t[1] = sl /\ t[2] = mb)[3]
      top     == Max({s.from - 1} \cup slots)
      CmdAt(sl) == IF sl \in DOMAIN s.chosen THEN s.chosen[sl]
                   ELSE IF sl \in slots THEN Best(sl) ELSE Noop
      range   == s.from..top
      c1 == [c EXCEPT !.s = [s EXCEPT !.role = "leader", !.from = 0, !.promises = EmptyMap,
                                      !.nextSlot = top + 1, !.hint = r,
                                      !.inflight = [sl \in range |-> [cmd |-> CmdAt(sl), acks |-> {}]]]]
      c2 == SendAccepts(r, c1, Sorted(range))
      c3 == Broadcast(r, c2, LAMBDA t : HeartbeatMsg(r, t, s.bal, NextDeliver(s)))
  IN FlushQueue(r, c3)

\* `learn`.
Learn(c, sl, cmd) ==
  IF sl < NextDeliver(c.s) \/ sl \in DOMAIN c.s.chosen THEN c
  ELSE [c EXCEPT !.s.chosen = Put(@, sl, cmd), !.learned = @ \cup {<<sl, cmd>>}]

\* `on_msg`, one case per message.
OnPrepare(r, c, m) ==
  IF m.bal >= c.s.promised
  THEN LET c1  == Observe([c EXCEPT !.s.promised = m.bal], m.bal)
           acc == {<<sl, c1.s.accepted[sl][1], c1.s.accepted[sl][2]>> :
                     sl \in {x \in DOMAIN c1.s.accepted : x >= m.slot}}
       IN Send(c1, PromiseMsg(r, m.from, m.bal, acc))
  ELSE Send(c, NackMsg(r, m.from, m.bal, c.s.promised))

OnPromise(r, c, m) ==
  IF c.s.role = "candidate" /\ c.s.bal = m.bal
  THEN LET c1 == [c EXCEPT !.s.promises = Put(@, m.from, m.acc)]
       IN IF Cardinality(DOMAIN c1.s.promises) >= Majority THEN BecomeLeader(r, c1) ELSE c1
  ELSE c

OnNack(r, c, m) ==
  IF c.s.role # "follower" /\ c.s.bal = m.rejected THEN Observe(c, m.promised) ELSE c

OnAccept(r, c, m) ==
  IF m.bal >= c.s.promised \/ Mut = "M_BELOWPROMISE"
  THEN LET c1 == [c EXCEPT !.s.promised = IF m.bal > @ THEN m.bal ELSE @,
                           !.s.accepted = Put(@, m.slot, <<m.bal, m.cmd>>),
                           !.votes = @ \cup {<<m.slot, m.bal, m.cmd>>}]
           c2 == Observe(c1, m.bal)
           c3 == IF m.from # r THEN [c2 EXCEPT !.s.hint = Owner(m.bal)] ELSE c2
       IN Send(c3, AcceptedMsg(r, m.from, m.bal, m.slot))
  ELSE Send(c, NackMsg(r, m.from, m.bal, c.s.promised))

OnAccepted(r, c, m) ==
  IF c.s.role = "leader" /\ c.s.bal = m.bal /\ m.slot \in DOMAIN c.s.inflight
  THEN LET e    == c.s.inflight[m.slot]
           acks == e.acks \cup {m.from}
       IN IF Cardinality(acks) >= Majority
          THEN Broadcast(r, [c EXCEPT !.s.inflight = [x \in DOMAIN @ \ {m.slot} |-> @[x]]],
                         LAMBDA t : CommitMsg(r, t, m.slot, e.cmd))
          ELSE [c EXCEPT !.s.inflight[m.slot].acks = acks]
  ELSE c

OnHeartbeat(r, c, m) ==
  IF m.bal >= c.s.maxSeen
  THEN LET c1 == Observe(c, m.bal)
       IN IF Owner(m.bal) # r
          THEN LET c2 == FlushQueue(r, [c1 EXCEPT !.s.hint = Owner(m.bal)])
               IN IF m.next > NextDeliver(c2.s)
                  THEN Send(c2, CatchUpMsg(r, m.from, NextDeliver(c2.s))) ELSE c2
          ELSE c1
  ELSE c

RECURSIVE SendCommits(_, _, _, _)
SendCommits(r, c, to, sls) ==
  IF sls = << >> THEN c
  ELSE SendCommits(r, Send(c, CommitMsg(r, to, Head(sls), c.s.chosen[Head(sls)])), to, Tail(sls))

OnCatchUp(r, c, m) ==
  IF m.slot >= NextDeliver(c.s) THEN c
  ELSE SendCommits(r, c, m.from, Sorted({sl \in DOMAIN c.s.chosen : sl >= m.slot /\ sl < NextDeliver(c.s)}))

\* Only a leader acts on a forward; anyone else queues it and does not flush.
OnForward(r, c, m) ==
  IF c.s.role = "leader" THEN Assign(r, c, m.value) ELSE [c EXCEPT !.s.queue = Append(@, m.value)]

OnMsg(r, c, m) ==
  CASE m.type = "prepare"   -> OnPrepare(r, c, m)
    [] m.type = "promise"   -> OnPromise(r, c, m)
    [] m.type = "nack"      -> OnNack(r, c, m)
    [] m.type = "accept"    -> OnAccept(r, c, m)
    [] m.type = "accepted"  -> OnAccepted(r, c, m)
    [] m.type = "commit"    -> Learn(c, m.slot, m.cmd)
    [] m.type = "heartbeat" -> OnHeartbeat(r, c, m)
    [] m.type = "catchup"   -> OnCatchUp(r, c, m)
    [] m.type = "forward"   -> OnForward(r, c, m)

\* The rest of `handle`: every message the replica sent itself, in order.
RECURSIVE Drain(_, _)
Drain(r, c) == IF c.local = << >> THEN c
               ELSE Drain(r, OnMsg(r, [c EXCEPT !.local = Tail(@)], Head(c.local)))

\* A leader's heartbeat tick: the heartbeat, then what is not yet chosen again.
BeatCtx(r, c) ==
  SendAccepts(r, Broadcast(r, c, LAMBDA t : HeartbeatMsg(r, t, c.s.bal, NextDeliver(c.s))),
              Sorted(DOMAIN c.s.inflight))

\* What a crash leaves: the durable acceptor state, unless the host never wrote it.
Recovered(s) == IF Mut = "M_NOPERSIST" THEN Fresh(0, EmptyMap) ELSE Fresh(s.promised, s.accepted)

\* --- the system ----------------------------------------------------------------
Count(q, v) == Cardinality({k \in 1..Len(q) : q[k] = v})

\* The effect of one call at r whose context ended as c. `taken` is the forward the
\* call received, as <<from, to, v>>, or << >>.
Effect(r, c, taken) ==
  /\ st' = [st EXCEPT ![r] = c.s]
  /\ msgs' = msgs \cup c.out
  /\ fwd' = [k \in DOMAIN fwd |->
               (IF k = taken THEN fwd[k] - 1 ELSE fwd[k])
               + Cardinality({j \in 1..Len(c.fwd) : <<r, c.fwd[j][1], c.fwd[j][2]>> = k})]
  /\ votes' = votes \cup {<<r, x[1], x[2], x[3]>> : x \in c.votes}
  /\ learned' = learned \cup c.learned
  /\ assigned' = [v \in Values |-> assigned[v] + Count(c.assigned, v)]

Hand(r, v) ==
  /\ r \in Hosts
  /\ handed[v] < MaxHand
  /\ \A w \in Values : w < v => handed[w] > 0
  /\ Effect(r, Drain(r, Propose(r, Ctx(st[r]), v)), << >>)
  /\ handed' = [handed EXCEPT ![v] = @ + 1]
  /\ UNCHANGED <<duped, crashes>>

Elect(r) ==
  /\ r \in Electors
  /\ st[r].role # "leader"
  /\ Round(st[r].maxSeen) < MaxRound
  /\ Effect(r, Drain(r, StartElection(r, Ctx(st[r]))), << >>)
  /\ UNCHANGED <<handed, duped, crashes>>

Beat(r) ==
  /\ r \in Beaters
  /\ st[r].role = "leader"
  /\ Effect(r, Drain(r, BeatCtx(r, Ctx(st[r]))), << >>)
  /\ UNCHANGED <<handed, duped, crashes>>

Receive(m) ==
  /\ Effect(m.to, Drain(m.to, OnMsg(m.to, Ctx(st[m.to]), m)), << >>)
  /\ UNCHANGED <<handed, duped, crashes>>

ReceiveForward(k) ==
  /\ fwd[k] > 0
  /\ Effect(k[2], Drain(k[2], OnMsg(k[2], Ctx(st[k[2]]), ForwardMsg(k[1], k[2], k[3]))), k)
  /\ UNCHANGED <<handed, duped, crashes>>

DupForward(k) ==
  /\ fwd[k] > 0
  /\ duped[k[3]] < MaxDup
  /\ fwd' = [fwd EXCEPT ![k] = @ + 1]
  /\ duped' = [duped EXCEPT ![k[3]] = @ + 1]
  /\ UNCHANGED <<st, msgs, votes, learned, handed, assigned, crashes>>

Crash(r) ==
  /\ r \in Crashers
  /\ crashes < MaxCrash
  /\ st' = [st EXCEPT ![r] = Recovered(st[r])]
  /\ crashes' = crashes + 1
  /\ UNCHANGED <<msgs, fwd, votes, learned, handed, assigned, duped>>

Init ==
  /\ st = [r \in Replicas |-> Fresh(0, EmptyMap)]
  /\ msgs = {}
  /\ fwd = [k \in Replicas \X Replicas \X Values |-> 0]
  /\ votes = {}
  /\ learned = {}
  /\ handed = [v \in Values |-> 0]
  /\ assigned = [v \in Values |-> 0]
  /\ duped = [v \in Values |-> 0]
  /\ crashes = 0

Next ==
  \/ \E r \in Replicas, v \in Values : Hand(r, v)
  \/ \E r \in Replicas : Elect(r) \/ Beat(r) \/ Crash(r)
  \/ \E m \in msgs : Receive(m)
  \/ \E k \in DOMAIN fwd : ReceiveForward(k) \/ DupForward(k)

Spec == Init /\ [][Next]_vars

\* --- properties ----------------------------------------------------------------
ChosenAt(sl, b, cmd) == Cardinality({a \in Replicas : <<a, sl, b, cmd>> \in votes}) >= Majority
Chosen(sl, cmd)      == \E x \in votes : x[2] = sl /\ x[4] = cmd /\ ChosenAt(sl, x[3], cmd)

TypeOK ==
  /\ \A r \in Replicas :
       /\ st[r].role \in {"follower", "candidate", "leader"}
       /\ st[r].promised \in Nat /\ st[r].maxSeen \in Nat /\ st[r].bal \in Nat
       /\ st[r].promised <= st[r].maxSeen /\ st[r].bal <= st[r].maxSeen
       /\ st[r].role # "follower" => Owner(st[r].bal) = r
       /\ st[r].role = "follower" => st[r].bal = 0
       /\ st[r].role # "candidate" => st[r].from = 0 /\ st[r].promises = EmptyMap
       /\ st[r].role # "leader" => st[r].nextSlot = 0 /\ st[r].inflight = EmptyMap
       /\ st[r].hint \in Replicas \cup {0}
       /\ \A k \in 1..Len(st[r].queue) : st[r].queue[k] \in Values
       /\ \A sl \in DOMAIN st[r].accepted : st[r].accepted[sl][2] \in Values \cup {Noop}
       /\ \A sl \in DOMAIN st[r].chosen : st[r].chosen[sl] \in Values \cup {Noop}
  /\ \A m \in msgs : m.from \in Replicas /\ m.to \in Replicas /\ m.from # m.to
  /\ \A k \in DOMAIN fwd : fwd[k] \in Nat
  /\ \A x \in votes : x[1] \in Replicas /\ x[4] \in Values \cup {Noop}

OneValuePerBallot == \A x, y \in votes : x[2] = y[2] /\ x[3] = y[3] => x[4] = y[4]
ChosenUnique      == \A x, y \in votes :
                       x[2] = y[2] /\ ChosenAt(x[2], x[3], x[4]) /\ ChosenAt(y[2], y[3], y[4]) => x[4] = y[4]
Agreement         == \A x, y \in learned : x[1] = y[1] => x[2] = y[2]
LearnerSound      == \A x \in learned : Chosen(x[1], x[2])
OnlyHanded        == \A x \in learned : x[2] = Noop \/ handed[x[2]] > 0
NoAmplification   == \A v \in Values : assigned[v] <= handed[v] + duped[v]

Safe == TypeOK /\ OneValuePerBallot /\ ChosenUnique /\ Agreement /\ LearnerSound /\ OnlyHanded
        /\ NoAmplification

\* What a mutation must not break: the "HOLDS" half of its rows.
KeptUnderLogMutations == TypeOK /\ OneValuePerBallot /\ LearnerSound /\ OnlyHanded /\ NoAmplification
KeptUnderRequeue      == TypeOK /\ OneValuePerBallot /\ ChosenUnique /\ Agreement /\ LearnerSound
                         /\ OnlyHanded

\* --- witnesses: each must be VIOLATED under Mut = "none" -----------------------
NeverChosen       == \A x \in votes : ~ChosenAt(x[2], x[3], x[4])
NeverLearned      == learned = {}
NeverSecondLeader == \A m, n \in msgs : m.type = "heartbeat" /\ n.type = "heartbeat" => m.from = n.from
NeverAdopted      == \A m \in msgs : m.type = "accept" =>
                       ~\E x \in votes : x[2] = m.slot /\ x[4] = m.cmd /\ x[3] < m.bal
NeverGapFilled    == \A m \in msgs : m.type = "accept" => m.cmd # Noop
NeverNacked       == \A m \in msgs : m.type # "nack"
NeverForwarded    == \A k \in DOMAIN fwd : fwd[k] = 0
NeverCaughtUp     == \A m \in msgs : m.type # "catchup"
NeverTwoSlots     == \A v \in Values : assigned[v] < 2
NeverDuped        == \A v \in Values : duped[v] = 0
================================================================================
