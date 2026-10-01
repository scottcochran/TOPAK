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
(*                                                                                *)
(* Not modelled: the floor and bundle decisions (an Admit entry is already a      *)
(* decision; apply re-checks the mechanism conditions only, as the code does),    *)
(* the clock (expiry arrives as an ordered EndRound), payloads, denials (never    *)
(* logged), and the Paxos log itself (entries arrive in index order).             *)
(*                                                                                *)
(* Shapes. Every record below has exactly the fields `trace.rs` projects; a       *)
(* function is `(k :> v @@ ...)`, a set `{...}`, a round topic `<<seat, epoch,   *)
(* round>>`, and "none" stands for an absent value.                               *)
(*                                                                                *)
(* State: epoch rulesEpoch seats grantRoster vetoRoster quorum minGrant bgIssued  *)
(*        bgRoster (a set, empty when no break-glass roster is issued)            *)
(*        verifierKeys bundleKeys (ADR-0025 §1 (f); carried, read by nothing here) *)
(*        leases liveBySeat lastRound candidates gates approvals revoked          *)
(*        appliedIds lastApplied k tPersona marks seals buildBound runBound       *)
(* Lease: principal seat persona epoch rulesEpoch conf rung alphabet round role   *)
(*        ttl ended actions seq                                                   *)
(* Candidate: artifact author votes promotedAt · Vote: verdict evidence rulesEpoch*)
(* Result: kind, plus fence | seq promoted | ended | epoch | rulesEpoch | approvals*)
EXTENDS Naturals, Sequences, FiniteSets, TLC

CONSTANTS InitState, Trace

NONE == "none"
RunKinds == {"Consult", "Actuate", "Report"}
RunEffects == {"Actuate", "Report"}
EmptyFn == [x \in {} |-> x]

DomainOf(k) == IF k \in RunKinds THEN "run" ELSE "build"

\* SeatKind::allows (ADR-0037 §4, ADR-0043 §2)
KindAllows(kind, k) ==
  CASE kind = "thinker"  -> k \in {"Read", "Draft", "Invoke", "Emit", "Submit", "Consult", "Actuate", "Report"}
    [] kind = "observer" -> k \in {"Read", "Emit", "Vote", "Consult", "Report"}
    [] kind = "grant"    -> k \in {"Read", "Emit", "Vote"}
    [] OTHER             -> FALSE

\* TLC refuses `=` between an integer and a string, so an absent value is tested by type.
IsNone(x)       == x \in STRING /\ x = NONE
Remove(f, x)    == [y \in DOMAIN f \ {x} |-> f[y]]
Put(f, x, v)    == (x :> v) @@ f
Sat(a, b)       == IF a >= b THEN a - b ELSE 0
Rej(s)          == [st |-> s, res |-> [kind |-> "Rejected"]]

SeatDomain(s, seat) == IF seat \in DOMAIN s.seats THEN s.seats[seat].domain ELSE NONE
SeatKindOf(s, seat) == IF seat \in DOMAIN s.seats THEN s.seats[seat].kind ELSE NONE
CellObservers(s, t) == {o \in DOMAIN s.seats : s.seats[o].kind = "observer" /\ s.seats[o].cell = t}
Watches(s, o, t) ==
  /\ o \in DOMAIN s.seats /\ t \in DOMAIN s.seats
  /\ s.seats[o].kind = "observer" /\ s.seats[t].kind = "thinker"
  /\ IF s.seats[o].cell = NONE THEN s.seats[o].domain = s.seats[t].domain ELSE s.seats[o].cell = t

HasLive(s, seat)   == seat \in DOMAIN s.liveBySeat
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
         cands == {t \in DOMAIN s.seats : s.seats[t].kind = "thinker" /\ (LiveTopic(t) \/ SealTopic(t))}
     IN /\ cands # {}
        /\ LET t == CHOOSE t \in cands : TRUE
               upper == IF LiveTopic(t) THEN s.leases[s.liveBySeat[t]].seq ELSE s.seals[t].seq
           IN /\ Watches(s, seat, t)
              /\ wm <= upper
              /\ wm >= Mark(s, seat, topic)

\* The action kind check_live reads: a heartbeat is checked under the variant it arrived as
AK(a) == IF a.kind = "Heartbeat" THEN a.via ELSE a.kind

\* State::check_action_preconditions
Preconditions(s, e) ==
  LET a == e.action IN
  CASE a.kind = "Submit"    -> a.artifact \notin DOMAIN s.candidates
    [] a.kind = "Vote"      -> /\ a.artifact \in DOMAIN s.candidates
                               /\ IsNone(s.candidates[a.artifact].promotedAt)
                               /\ a.artifact \in DOMAIN s.gates
                               /\ s.gates[a.artifact] = a.evidence
    [] a.kind = "Heartbeat" -> HeartbeatOk(s, e.seat, a.topic, a.watermark)
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
       IN IF SeatKindOf(s, rec.seat) = "thinker"
            THEN [s2 EXCEPT !.seals = Put(@, rec.seat, SealOf(rec))] ELSE s2

\* State::end_all_live: every live lease ends; every live Thinker's round seals
EndAllLive(s, reason) ==
  LET live     == {s.liveBySeat[x] : x \in DOMAIN s.liveBySeat}
      leases2  == [f \in DOMAIN s.leases |->
                     IF f \in live /\ s.leases[f].ended = NONE
                       THEN [s.leases[f] EXCEPT !.ended = reason] ELSE s.leases[f]]
      thinkers == {x \in DOMAIN s.liveBySeat : SeatKindOf(s, x) = "thinker"}
      newSeals == [x \in thinkers |-> SealOf(s.leases[s.liveBySeat[x]])]
  IN [s EXCEPT !.leases = leases2, !.liveBySeat = EmptyFn, !.seals = newSeals @@ @]

TargetMatches(t, lr) ==
  \/ t.kind = "principal"   /\ t.id = lr.principal
  \/ t.kind = "persona"     /\ t.id = lr.persona
  \/ t.kind = "confinement" /\ t.id = lr.conf

\* State::apply_grant
ApplyGrant(s, idx, e) ==
  LET dom  == SeatDomain(s, e.seat)
      kind == SeatKindOf(s, e.seat)
      busy == \E x \in DOMAIN s.liveBySeat : s.leases[s.liveBySeat[x]].principal = e.principal
      revokedHit == \E t \in s.revoked : TargetMatches(t, [principal |-> e.principal, persona |-> e.persona, conf |-> e.conf])
      unread == /\ dom = "run" /\ kind = "thinker" /\ e.seat \in DOMAIN s.seals
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
     ELSE IF e.ttl > s.tPersona THEN Rej(s)      \* ADR-0031 A2
     ELSE IF unread THEN Rej(s)
     ELSE IF reused THEN Rej(s)
     ELSE LET lr == [principal |-> e.principal, seat |-> e.seat, persona |-> e.persona,
                     epoch |-> s.epoch, rulesEpoch |-> s.rulesEpoch, conf |-> e.conf, rung |-> e.rung,
                     alphabet |-> e.alphabet, round |-> e.round, role |-> e.role, ttl |-> e.ttl,
                     ended |-> NONE, actions |-> 0, seq |-> 0]
          IN [st  |-> [s EXCEPT !.leases = Put(@, idx, lr), !.liveBySeat = Put(@, e.seat, idx),
                                !.lastRound = Put(@, e.seat, e.round)],
              res |-> [kind |-> "LeaseGranted", fence |-> idx]]

\* State::apply_renew (ADR-0031 §4, A1)
ApplyRenew(s, idx, e) ==
  IF e.fence \notin DOMAIN s.leases THEN Rej(s)
  ELSE LET old == s.leases[e.fence] IN
    IF old.seat # e.seat \/ old.ended # NONE THEN Rej(s)
    ELSE IF old.epoch # s.epoch \/ old.rulesEpoch # s.rulesEpoch THEN Rej(s)
    ELSE IF e.ttl > s.tPersona THEN Rej(s)      \* ADR-0031 A2
    ELSE IF ~(e.alphabet \subseteq old.alphabet) THEN Rej(s)
    ELSE IF e.rung # old.rung THEN Rej(s)
    ELSE IF e.ttl > old.ttl THEN Rej(s)
    ELSE LET new == [old EXCEPT !.alphabet = e.alphabet, !.ttl = e.ttl]
         IN [st  |-> [s EXCEPT !.leases = Put([@ EXCEPT ![e.fence].ended = "renewed"], idx, new),
                               !.liveBySeat = Put(@, e.seat, idx)],
             res |-> [kind |-> "Renewed", fence |-> idx]]

\* State::apply_revoke (ADR-0031 §5 R3)
ApplyRevoke(s, e) ==
  LET t        == e.target
      liveF    == {s.liveBySeat[x] : x \in DOMAIN s.liveBySeat}
      hit      == {f \in liveF : TargetMatches(t, s.leases[f])}
      hitSeats == {s.leases[f].seat : f \in hit}
      leases2  == [f \in DOMAIN s.leases |-> IF f \in hit THEN [s.leases[f] EXCEPT !.ended = "revoked"] ELSE s.leases[f]]
      thinkers == {x \in hitSeats : SeatKindOf(s, x) = "thinker"}
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
  ELSE IF ~CheckLive(s, e) THEN Rej(s)
  ELSE IF e.action.kind \in RunEffects /\ SeatKindOf(s, e.seat) = "thinker" /\ ~ObserverCovers(s, e.seat) THEN Rej(s)
  ELSE LET f   == e.lease
           a   == e.action
           lr1 == [s.leases[f] EXCEPT !.actions = @ + 1]
       IN CASE a.kind \in {"Emit", "Report", "Actuate"} ->
               LET lr2 == [lr1 EXCEPT !.seq = @ + 1]
               IN [st |-> [s EXCEPT !.leases = Put(@, f, lr2)], res |-> Admitted(lr2.seq, NONE)]
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
                           !.bgIssued = r.bgIssued, !.bgRoster = r.bgRoster,
                           !.verifierKeys = r.verifierKeys, !.bundleKeys = r.bundleKeys]
       IN [st |-> EndAllLive(s1, "rules_changed"), res |-> [kind |-> "Issued", rulesEpoch |-> r.rulesEpoch]]

ApplyBreakGlass(s, e) ==
  IF ~s.bgIssued THEN Rej(s)
  ELSE IF e.epoch # s.epoch THEN Rej(s)
  ELSE IF e.key \notin s.bgRoster \/ ~e.ok THEN Rej(s)
  ELSE LET bySeat == IF e.seat \in DOMAIN s.approvals THEN s.approvals[e.seat] ELSE EmptyFn
           keys   == (IF e.epoch \in DOMAIN bySeat THEN bySeat[e.epoch] ELSE {}) \cup {e.key}
       IN [st  |-> [s EXCEPT !.approvals = Put(@, e.seat, Put(bySeat, e.epoch, keys))],
           res |-> [kind |-> "BreakGlassApproved", approvals |-> Cardinality(keys)]]

\* State::apply
Apply(s0, idx, e) ==
  LET s == [s0 EXCEPT !.lastApplied = idx] IN
  IF e.id \in s.appliedIds THEN [st |-> s, res |-> [kind |-> "Duplicate"]]
  ELSE LET s1 == [s EXCEPT !.appliedIds = @ \cup {e.id}] IN
    CASE e.kind = "Grant"             -> ApplyGrant(s1, idx, e)
      [] e.kind = "Renew"             -> ApplyRenew(s1, idx, e)
      [] e.kind = "Admit"             -> ApplyAdmit(s1, idx, e)
      [] e.kind = "EndRound"          -> ApplyEndRound(s1, e)
      [] e.kind = "Revoke"            -> ApplyRevoke(s1, e)
      [] e.kind = "EpochIncrement"    -> [st |-> EndAllLive([s1 EXCEPT !.epoch = @ + 1], "fenced"),
                                          res |-> [kind |-> "EpochIncremented", epoch |-> s1.epoch + 1]]
      [] e.kind = "Issue"             -> ApplyIssue(s1, e)
      [] e.kind = "GatesPassed"       -> [st |-> [s1 EXCEPT !.gates = Put(@, e.artifact, e.evidence)],
                                          res |-> [kind |-> "GatesRecorded"]]
      [] e.kind = "BreakGlassApprove" -> ApplyBreakGlass(s1, e)

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
