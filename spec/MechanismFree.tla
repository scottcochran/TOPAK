---------------------------- MODULE MechanismFree ----------------------------
(* Mechanism.tla, run freely: step 1 of refinement-plan.md.                       *)
(*                                                                                *)
(* Mechanism.tla's only specification replays a recorded trace, so no state of    *)
(* the operational model is examined but those a test reaches. This module gives  *)
(* the same `Apply` a generator of entries and a depth: from a fixture, every     *)
(* entry the generator can write is applied, to `Depth` entries. It edits         *)
(* nothing in Mechanism.tla, and it says nothing about the code: an entry here    *)
(* is the generator's, not a replica's. What it checks is the model, on states    *)
(* no trace holds.                                                                *)
(*                                                                                *)
(*   TypeOK              the projected state keeps its shape: indices, epochs,    *)
(*                       counters and rosters are where the header of             *)
(*                       Mechanism.tla puts them                                  *)
(*   Indexed             `liveBySeat` indexes exactly the leases that have not    *)
(*                       ended, each at its own seat                              *)
(*   ConfinementRefined  ConfinementRefinement.tla's four predicates, which the   *)
(*                       replay checks on recorded states, on every generated one *)
(*                                                                                *)
(* The fixture is the state tests/mutations.rs builds for                         *)
(* `run_alphabets_are_bounded_by_seat_kind_and_domain` (State::genesis of its     *)
(* rules, with a Run cell), as trace.rs projects it before the first entry:       *)
(* seven seats, a Build Thinker with its Observer and three grant seats, a Run    *)
(* Thinker with its cell Observer; nothing leased, nothing applied.               *)
(*                                                                                *)
(* THE GENERATOR, first cut: seven of the sixteen entry kinds. A grant on the     *)
(* unsigned path, a renewal, an admit, an end of round, a targeted revocation,    *)
(* the fleet fence, and a gate attestation, without which no vote is admissible.  *)
(* Each has the fields trace.rs projects for it. Where the trace carries a        *)
(* trusted input the generator offers both answers (an admit's `ok`); where the   *)
(* code would refuse, it offers the refused form beside the admitted one (an      *)
(* alphabet outside the seat's kind, a round number reused, a renewal that        *)
(* widens, an action outside the alphabet, a stale `clearSet`, a watermark above  *)
(* what exists, an entry whose id has been applied).                              *)
(*                                                                                *)
(* NOT GENERATED, and so not reached: a grant above rung 0 and every appraisal    *)
(* (so `contained` stays empty and three of ConfinementRefinement's predicates    *)
(* hold of nothing); a profile, a Contested verdict; an issuance; an operator's   *)
(* request, an emergency seating and its activation; a workflow's load and        *)
(* grant, a route, a typed outcome, a finding; a break-glass approval; a task     *)
(* label; a session proof; a revocation by Persona or by confinement. The         *)
(* `Never...` rows that HOLD say which.                                           *)
(*                                                                                *)
(* Mut = "none":      the generator as written.                                   *)
(* Mut = "M_NOGRANT": the generator offers no grant. Every witness that needs a   *)
(*                    lease must then HOLD: a control on the witnesses, not on    *)
(*                    the model.                                                  *)
(*                                                                                *)
(* Constants, bounded in the run: `Depth`, the number of entries; `Principals`;   *)
(* `GenSeats`, the fixture's seats the generator writes for; `Artifacts`; and     *)
(* `Steps`, the entry kinds it writes, so that a row can narrow the generator and *)
(* go deeper: a promotion is nine entries from the fixture. `InitState` and       *)
(* `Trace` are Mechanism.tla's, for the replay; nothing here reads them, and a    *)
(* run binds them to a string.                                                    *)
(*                                                                                *)
(* `last` is the kind of the last entry's result, kept so that a witness can ask  *)
(* whether a result is reachable. A state with no successor is at the depth.      *)
EXTENDS ConfinementRefinement

CONSTANTS Mut, Depth, Principals, GenSeats, Artifacts, Steps

VARIABLE last
fvars == <<st, i, last>>

Seat(domain, kind, cell) == [cell |-> cell, domain |-> domain, kind |-> kind, rung |-> 0]

Fixture ==
  [epoch |-> 0, rulesEpoch |-> 0,
   seats |-> ("a1"  :> Seat("build", "thinker", NONE)) @@ ("o1" :> Seat("build", "observer", "a1"))
          @@ ("g1"  :> Seat("build", "grant", NONE))   @@ ("g2" :> Seat("build", "grant", NONE))
          @@ ("g3"  :> Seat("build", "grant", NONE))
          @@ ("r1"  :> Seat("run", "thinker", NONE))   @@ ("ro1" :> Seat("run", "observer", "r1")),
   grantRoster |-> {"a1", "g1", "g2", "g3"}, vetoRoster |-> {"o1"}, quorum |-> "all", minGrant |-> 2,
   bgIssued |-> FALSE, bgRoster |-> {}, bgQuorum |-> 0,
   seatings |-> EmptyFn, lastLease |-> EmptyFn, controlCtr |-> EmptyFn, emSeatings |-> EmptyFn,
   activations |-> <<>>, verifierKeys |-> {}, bundleKeys |-> {}, personas |-> EmptyFn, criterion |-> FALSE,
   leases |-> EmptyFn, liveBySeat |-> EmptyFn, lastRound |-> EmptyFn, candidates |-> EmptyFn,
   gates |-> EmptyFn, approvals |-> EmptyFn, revoked |-> {}, appliedIds |-> {}, lastApplied |-> 0,
   k |-> 8, tPersona |-> 3600000, marks |-> EmptyFn, seals |-> EmptyFn, profiles |-> EmptyFn,
   contested |-> EmptyFn, contained |-> {}, wasmTools |-> {}, buildBound |-> 3, runBound |-> 3,
   workflows |-> EmptyFn, wfBindings |-> EmptyFn]

ASSUME GenSeatsDeclared == GenSeats \subseteq DOMAIN Fixture.seats
ASSUME DepthNat == Depth \in Nat
AllSteps == {"grant", "renew", "admit", "end", "revoke", "fence", "gates", "again"}
ASSUME StepsKnown == Steps \subseteq AllSteps

\* --- the generator: one operator for each entry kind --------------------------------

Id(n) == ToString(n)

AllKinds == {"Read", "Draft", "Invoke", "Emit", "Submit", "Vote", "Consult", "Actuate", "Report", "Route"}
\* What the seat's kind and domain allow, and the same with a variant no seat here is issued
Full(s, seat) == {k \in AllKinds : KindAllows(SeatKindOf(s, seat), k) /\ DomainOf(k) = SeatDomain(s, seat)}
Wide(a)       == a \cup {"Route"}

Rounds(s, seat) == IF seat \in DOMAIN s.lastRound THEN {s.lastRound[seat] + 1, s.lastRound[seat]} ELSE {1}

GrantEntry(s, n, seat, p, alphabet, round) ==
  [kind |-> "Grant", id |-> Id(n), principal |-> p, seat |-> seat, persona |-> "persona", bundle |-> "bundle",
   conf |-> "conf", rung |-> 0, alphabet |-> alphabet, ttl |-> 1000, round |-> round,
   role |-> IF SeatDomain(s, seat) = "build" /\ SeatKindOf(s, seat) \in {"grant", "observer"} THEN "voter" ELSE "author",
   taskLabelled |-> FALSE, taskLabel |-> {}, taskLabelsAllowed |-> {}, signOnOk |-> FALSE,
   appraisal |-> NONE, sigOk |-> FALSE, sigKey |-> NONE]

\* A renewal names the seat's last lease, live or ended, and keeps its rung and ttl
RenewEntry(s, n, seat, alphabet) ==
  [kind |-> "Renew", id |-> Id(n), seat |-> seat, fence |-> s.lastLease[seat], alphabet |-> alphabet,
   rung |-> s.leases[s.lastLease[seat]].rung, ttl |-> s.leases[s.lastLease[seat]].ttl,
   appraisal |-> NONE, sigOk |-> FALSE, sigKey |-> NONE]

\* An admit under the seat's last lease, at that lease's epoch
AdmitEntry(s, n, seat, action, labels, ok) ==
  [kind |-> "Admit", id |-> Id(n), seat |-> seat, lease |-> s.lastLease[seat],
   epoch |-> s.leases[s.lastLease[seat]].epoch, action |-> action, session |-> NONE, proofOk |-> FALSE,
   labels |-> labels, ok |-> ok]

\* The rounds a heartbeat may name: every coupled seat's live round, and every seal
Topics(s) == {TopicOf(s.leases[s.liveBySeat[t]]) : t \in {t \in DOMAIN s.liveBySeat : Coupled(SeatKindOf(s, t))}}
             \cup {s.seals[t].topic : t \in DOMAIN s.seals}

\* --- the free specification ---------------------------------------------------------

Step(e) ==
  LET r == Apply(st, i + 1, e) IN
  /\ st' = r.st
  /\ i' = i + 1
  /\ last' = r.res.kind

Held(s) == GenSeats \cap DOMAIN s.lastLease          \* seats with a lease, live or ended

GrantStep ==
  \E seat \in GenSeats, p \in Principals :
    \E a \in {Full(st, seat), Wide(Full(st, seat))}, r \in Rounds(st, seat) :
      Step(GrantEntry(st, i + 1, seat, p, a, r))

RenewStep ==
  \E seat \in Held(st) :
    \E a \in {st.leases[st.lastLease[seat]].alphabet, Wide(st.leases[st.lastLease[seat]].alphabet)} :
      Step(RenewEntry(st, i + 1, seat, a))

\* Each variant is offered where the lease's alphabet holds it, so that it reaches the check
\* that is about it. `Draft` is offered where the alphabet does not hold it: the action outside
\* the alphabet. A route here has no stamp and no orchestrator's round, and is void.
AdmitStep ==
  \E seat \in Held(st) :
    LET lr      == st.leases[st.lastLease[seat]]
        Has(k)  == k \in lr.alphabet
        A(action, labels) == Step(AdmitEntry(st, i + 1, seat, action, labels, TRUE))
        Lab(cs, rl) == [clearSet |-> cs, resultLabel |-> rl, delivery |-> "clear"]
    IN \/ \E k \in {"Read", "Emit"} : Has(k) /\ A([kind |-> k], NONE)
       \/ Has("Report") /\ A([kind |-> "Report", outcome |-> NONE], NONE)
       \/ ~Has("Draft") /\ A([kind |-> "Draft"], NONE)
       \/ A([kind |-> "Route", edge |-> "none", stamp |-> NONE], NONE)
       \/ Has("Submit") /\ \E art \in Artifacts : A([kind |-> "Submit", artifact |-> art], NONE)
       \/ Has("Vote") /\ \E art \in Artifacts, v \in {"grant", "deny"} :
            A([kind |-> "Vote", verdict |-> v, artifact |-> art, evidence |-> "evidence",
               rulesEpoch |-> st.rulesEpoch], NONE)
       \/ Has("Consult") /\ \E rl \in {{}, {"untrusted"}} :
            A([kind |-> "Consult", object |-> "object"], Lab(lr.clearSet, rl))
       \/ Has("Actuate") /\ \E rl \in {{}, {"untrusted"}} :
            A([kind |-> "Actuate", tool |-> "tool"], Lab(lr.clearSet, rl))
       \* decided against a clearSet the round does not have
       \/ Has("Actuate") /\ A([kind |-> "Actuate", tool |-> "tool"], Lab(lr.clearSet \cup {"stale"}, {}))
       \/ SeatKindOf(st, seat) = "observer" /\ \E via \in {"Emit", "Report"} \cap lr.alphabet :
            \E t \in Topics(st), w \in 0..3 :
              A([kind |-> "Heartbeat", via |-> via, topic |-> t, watermark |-> w], NONE)
       \* decided under other mechanism parameters: the trace's `ok`
       \/ Step(AdmitEntry(st, i + 1, seat, [kind |-> "Emit"], NONE, FALSE))

EndStep ==
  \E seat \in Held(st), reason \in {"expired", "abstained"} :
    Step([kind |-> "EndRound", id |-> Id(i + 1), seat |-> seat, fence |-> st.lastLease[seat], reason |-> reason])

RevokeStep ==
  \E p \in Principals :
    Step([kind |-> "Revoke", id |-> Id(i + 1), target |-> [kind |-> "principal", id |-> p]])

FenceStep == Step([kind |-> "EpochIncrement", id |-> Id(i + 1)])

GatesStep ==
  \E art \in Artifacts :
    Step([kind |-> "GatesPassed", id |-> Id(i + 1), artifact |-> art, evidence |-> "evidence"])

\* An entry whose id has been applied: a duplicate, which changes nothing but the index
AgainStep == i > 0 /\ Step([kind |-> "EpochIncrement", id |-> Id(i)])

FreeInit == st = Fixture /\ i = 0 /\ last = NONE
FreeNext ==
  /\ i < Depth
  /\ \/ "grant"  \in Steps /\ Mut # "M_NOGRANT" /\ GrantStep
     \/ "renew"  \in Steps /\ RenewStep
     \/ "admit"  \in Steps /\ AdmitStep
     \/ "end"    \in Steps /\ EndStep
     \/ "revoke" \in Steps /\ RevokeStep
     \/ "fence"  \in Steps /\ FenceStep
     \/ "gates"  \in Steps /\ GatesStep
     \/ "again"  \in Steps /\ AgainStep
Spec == FreeInit /\ [][FreeNext]_fvars

\* --- the properties ------------------------------------------------------------------

EndReasons == {"submitted", "abstained", "voted", "expired", "fenced", "revoked", "rules_changed", "operator",
               "renewed", "outcome", "routed"}

LeaseOK(f) ==
  LET lr == st.leases[f] IN
  /\ f \in 1..i
  /\ lr.seat \in DOMAIN st.seats
  /\ lr.principal \in Principals
  /\ lr.epoch \in 0..st.epoch
  /\ lr.rulesEpoch = st.rulesEpoch
  /\ lr.round \in Nat /\ lr.rung \in 0..3
  /\ lr.alphabet \subseteq AllKinds
  /\ lr.ended \in EndReasons \cup {NONE}
  /\ lr.actions \in 0..Bound(st, lr.seat)
  /\ lr.seq \in 0..lr.actions
  /\ DOMAIN lr.results \subseteq 1..lr.seq

TypeOK ==
  /\ st.lastApplied = i
  /\ st.epoch \in 0..i
  /\ st.appliedIds \subseteq {Id(n) : n \in 1..i}
  /\ \A f \in DOMAIN st.leases : LeaseOK(f)
  /\ DOMAIN st.liveBySeat \subseteq DOMAIN st.seats
  /\ DOMAIN st.lastLease \subseteq DOMAIN st.seats
  /\ DOMAIN st.lastRound = DOMAIN st.lastLease
  /\ \A x \in DOMAIN st.lastLease : /\ st.lastLease[x] \in DOMAIN st.leases
                                    /\ st.leases[st.lastLease[x]].seat = x
                                    /\ st.leases[st.lastLease[x]].round = st.lastRound[x]
  /\ \A x \in DOMAIN st.seals : /\ Coupled(SeatKindOf(st, x))
                                /\ st.seals[x].topic[1] = x
                                /\ st.seals[x].seq \in Nat
  /\ \A o \in DOMAIN st.marks : /\ SeatKindOf(st, o) = "observer"
                                /\ \A t \in DOMAIN st.marks[o] : st.marks[o][t] \in Nat
  /\ \A a \in DOMAIN st.candidates :
       LET c == st.candidates[a] IN
       /\ c.artifact = a /\ a \in Artifacts
       /\ c.author \in DOMAIN st.seats
       /\ DOMAIN c.votes \subseteq DOMAIN st.seats
       /\ (IsNone(c.promotedAt) \/ c.promotedAt \in 1..i)
  /\ DOMAIN st.gates \subseteq Artifacts
  /\ st.revoked \subseteq {[kind |-> "principal", id |-> p] : p \in Principals}
  /\ st.contained \subseteq DOMAIN st.leases
  /\ DOMAIN st.workflows = {} /\ DOMAIN st.wfBindings = {}

Indexed ==
  /\ \A x \in DOMAIN st.liveBySeat :
       LET f == st.liveBySeat[x] IN
       f \in DOMAIN st.leases /\ st.leases[f].seat = x /\ st.leases[f].ended = NONE
  /\ \A f \in DOMAIN st.leases :
       st.leases[f].ended = NONE =>
         st.leases[f].seat \in DOMAIN st.liveBySeat /\ st.liveBySeat[st.leases[f].seat] = f

Safe == TypeOK /\ Indexed /\ ConfinementRefined

\* A state with no successor is at the depth: the generator always has an entry to write
TerminalAtDepth == i = Depth \/ ENABLED FreeNext

\* --- witnesses: each must be VIOLATED, or the row says why it HOLDS -------------------

NeverGranted     == last # "LeaseGranted"
NeverRenewed     == last # "Renewed"
NeverAdmitted    == last # "Admitted"
NeverRoundEnded  == last # "RoundEnded"
NeverRevoked     == last # "Revoked"
NeverFenced      == last # "EpochIncremented"
NeverGated       == last # "GatesRecorded"
NeverRejected    == last # "Rejected"
NeverDuplicate   == last # "Duplicate"
NeverSealed      == DOMAIN st.seals = {}
NeverCandidate   == DOMAIN st.candidates = {}
NeverMarked      == DOMAIN st.marks = {}
NeverRevokedLive == \A f \in DOMAIN st.leases : st.leases[f].ended # "revoked"
NeverTainted     == \A f \in DOMAIN st.leases : "untrusted" \notin st.leases[f].clearSet
NeverAtBound     == \A f \in DOMAIN st.leases : st.leases[f].actions < Bound(st, st.leases[f].seat)
\* What the first cut does not reach
NeverPromoted    == \A a \in DOMAIN st.candidates : IsNone(st.candidates[a].promotedAt)
NeverContained   == st.contained = {}
NeverContested   == DOMAIN st.contested = {}
=============================================================================
