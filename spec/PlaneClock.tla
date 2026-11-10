------------------------------ MODULE PlaneClock ------------------------------
(* An autonomous plane's clock is its ticks: ADR-0064 (Proposed), its          *)
(* ratification condition (§8), with `EntryEndsAtExtent` also ADR-0062 §4 and  *)
(* §5, and proposal §10 of                                                     *)
(* derived/topak-federated-c2-design-proposal-2026.11.10b.md. Ticks are        *)
(* numbered from the charter and signed by a certificate of replicas, each on  *)
(* its own clock. Every interval is a count of ticks from a named tick.        *)
(*                                                                             *)
(* Time is explicit and discrete: `now` is real time in whole units and P      *)
(* units are one tick period. Each replica has a clock of a declared class:    *)
(* sound (it keeps real time, its early margin folded in), `Slow` (it may lag  *)
(* without limit), `Fast` (it may lead) or `Captured` (it signs anything, and  *)
(* its clock is read by nothing). A certificate is one atomic step by a set of *)
(* at least `Cert` replicas: no ballot, primary or view is modelled, which is  *)
(* ADR-0061's and Membership.tla's.                                            *)
(*                                                                             *)
(*   NoGrantPastExpiry   no grant under an intent one tick period or more past *)
(*                       its `expiry`, as real time, the `expiry` being the    *)
(*                       one the intent named (§4)                             *)
(*   EntryEndsAtExtent   a running entry is short of its extent and of the     *)
(*                       largest extent an entry may declare, counted in ticks *)
(*                       applied, and its governor's own clock has not passed  *)
(*                       the next tick's due time (ADR-0062 §4, ADR-0064 §5)   *)
(*   NoStretchUnlessSlow a governor whose clock is not slow runs no entry past *)
(*                       one overdue tick in real time                         *)
(*                                                                             *)
(* THE PREMISE AND WHAT THIS IS NOT. NoGrantPastExpiry rests on §4's premise,  *)
(* the named assumption ClockPremise: captured and slow replicas together are  *)
(* fewer than a certificate. So it is a declared bound with a premise about    *)
(* time, and NOT a safety theorem in the lattice analysis's sense. Row         *)
(* M_TOOSLOW runs with the premise false and the bound fails. Outstanding.tla  *)
(* (ADR-0063) carries the bound that has no such premise. The timing budget    *)
(* is only partly expressible in TLA+ (ToO §11.3) and ADR-0032 defers a timed  *)
(* automaton: this is discrete time, with no clock rates and no margins, and   *)
(* it says nothing about a real clock's drift.                                 *)
(*                                                                             *)
(* THE RESIDUAL. "Overdue" is defined by the governor's own clock (ADR-0064    *)
(* §5, by the custodian's decision): the next tick is overdue when `gclock`    *)
(* has reached that tick's due time. So EntryEndsAtExtent's third clause is a  *)
(* statement about `gclock`, and not about `now`. A slow governor clock finds  *)
(* a tick overdue late and can stretch the entry in progress in real time.     *)
(* That can happen only when the plane's ticks have also stopped reaching the  *)
(* governor: an entry's extent is counted in ticks applied, so the first two   *)
(* clauses hold whatever the clock does. The witness NeverStretched is         *)
(* violated at GovClass = "slow" and shows the residual is reachable;          *)
(* NoStretchUnlessSlow states that nothing else reaches it. ADR-0064 §5 says   *)
(* this has the shape of ADR-0045's finding 2.                                 *)
(*                                                                             *)
(* A FINDING ON §2. The first rule on a replica's vote (never sign a tick      *)
(* ahead of your clock) carries no property here. A tick ahead of real time    *)
(* moves an expiry and an extent nearer, which only subtracts. It is the       *)
(* second rule (no grant while the next tick is due) that NoGrantPastExpiry    *)
(* rests on. The first rule is what keeps a captured or fast quorum from       *)
(* burning a plane's intervals: that is availability, ADR-0032's side.         *)
(*                                                                             *)
(* What is abstracted. One intent, one governor, one lease flag, one entry at  *)
(* a time. `lease` is set by a grant and cleared by going alone, and its `ttl` *)
(* is not modelled: ADR-0064 §3 ends a lease no later than its intent, so the  *)
(* bound on a grant is the bound on the lease's start. Going alone is urgent:  *)
(* real time does not pass a running entry's overdue tick by the governor's    *)
(* own clock until the watchdog has acted, which is "at once" (ADR-0062 §5).   *)
(* An extent is a number of ticks; distance and region are measurements        *)
(* (ADR-0068). Margins are folded into a clock's class.                        *)
(*                                                                             *)
(* Mut = "none":            ADR-0064 as drafted.                               *)
(* Mut = "M_ONECLOCK":      one replica's clock decides a certificate. Must    *)
(*                          break NoGrantPastExpiry.                           *)
(* Mut = "M_RECEIPT":       an intent's interval starts at receipt, not at the *)
(*                          tick it names: the NATO reading's F1. Must break   *)
(*                          NoGrantPastExpiry.                                 *)
(* Mut = "M_RELATIVETICK":  a tick is measured from the tick before, so a      *)
(*                          stall hides its length. This is the first draft of *)
(*                          §2 (ADR-0064 Findings, 1). Must break              *)
(*                          NoGrantPastExpiry.                                 *)
(* Mut = "M_TOOSLOW":       the premise is waived, and the run sets captured   *)
(*                          and slow to a certificate. Must break              *)
(*                          NoGrantPastExpiry.                                 *)
(* Mut = "M_NOEXTENT":      an entry with no extent loads. Must break          *)
(*                          EntryEndsAtExtent.                                 *)
(* Mut = "M_NOWATCHDOG":    an overdue tick ends nothing. Must break           *)
(*                          EntryEndsAtExtent and NoStretchUnlessSlow.         *)
(*                                                                             *)
(* Deadlock is not checked: the bound on `now` is the run script's.            *)
EXTENDS Naturals, FiniteSets

CONSTANTS Mut, Replicas, Cert, Captured, Slow, Fast, GovClass, P, Base, D, MaxExtent, MaxNow, MaxTick

ASSUME ClassesWF    == (Captured \cup Slow \cup Fast) \subseteq Replicas
ASSUME ClockPremise == Mut = "M_TOOSLOW" \/ Cardinality(Captured \cup Slow) < Cert

Certs     == {S \in SUBSET Replicas : Cardinality(S) >= Cert}
Steps     == [Replicas -> 0..2]
NoExtent  == MaxExtent + MaxTick + 1
Extents   == (1..MaxExtent) \cup (IF Mut = "M_NOEXTENT" THEN {NoExtent} ELSE {})

\* The real time at which tick t + 1 is due, numbered from the charter.
Deadline(t) == (t + 1) * P

TrueExpiry == Base + D

VARIABLES now, clock, gclock, tick, gtick, lastAt, delivered, expiry, lease,
          running, start, endAt, lateGrant, seen
vars == <<now, clock, gclock, tick, gtick, lastAt, delivered, expiry, lease,
          running, start, endAt, lateGrant, seen>>

Init ==
  /\ now = 0
  /\ clock = [r \in Replicas |-> 0]
  /\ gclock = 0
  /\ tick = 0
  /\ gtick = 0
  /\ lastAt = [r \in Replicas |-> 0]
  /\ delivered = FALSE
  /\ expiry = 0
  /\ lease = FALSE
  /\ running = FALSE
  /\ start = 0
  /\ endAt = 0
  /\ lateGrant = FALSE
  /\ seen = {}

\* How far a clock may move in one unit of real time.
LegalStep(x, d) ==
  IF x \in Captured THEN d = 0
  ELSE IF x \in Slow THEN d \in {0, 1}
  ELSE IF x \in Fast THEN d \in {1, 2}
  ELSE d = 1

LegalGov(g) ==
  IF GovClass = "slow" THEN g \in {0, 1}
  ELSE IF GovClass = "fast" THEN g \in {1, 2}
  ELSE g = 1

\* When a replica finds the next tick due.
Due(x) == IF Mut = "M_RELATIVETICK" THEN lastAt[x] + P ELSE Deadline(tick)

SignsTick(x)  == x \in Captured \/ clock[x] >= Due(x)
SignsGrant(x) == x \in Captured \/ clock[x] < Due(x)

TickOK(S)  == IF Mut = "M_ONECLOCK" THEN \E x \in S : SignsTick(x)  ELSE \A x \in S : SignsTick(x)
GrantOK(S) == IF Mut = "M_ONECLOCK" THEN \E x \in S : SignsGrant(x) ELSE \A x \in S : SignsGrant(x)

\* By the governor's own clock, the next tick is overdue.
Overdue == gclock >= Deadline(gtick)

\* The watchdog is urgent: time does not pass a running entry's overdue tick by its own clock.
WatchdogHolds(g) == Mut # "M_NOWATCHDOG" /\ running /\ gclock + g > Deadline(gtick)

Advance(d, g) ==
  /\ now < MaxNow
  /\ \A x \in Replicas : LegalStep(x, d[x])
  /\ LegalGov(g)
  /\ ~WatchdogHolds(g)
  /\ now' = now + 1
  /\ clock' = [x \in Replicas |-> clock[x] + d[x]]
  /\ gclock' = gclock + g
  /\ UNCHANGED <<tick, gtick, lastAt, delivered, expiry, lease, running, start, endAt, lateGrant, seen>>

\* The intent reaches the plane. It names tick Base, and an adversary may withhold it.
Deliver ==
  /\ ~delivered
  /\ Base <= tick
  /\ delivered' = TRUE
  /\ expiry' = IF Mut = "M_RECEIPT" THEN tick + D ELSE TrueExpiry
  /\ seen' = seen \cup (IF tick > Base THEN {"withheld"} ELSE {})
  /\ UNCHANGED <<now, clock, gclock, tick, gtick, lastAt, lease, running, start, endAt, lateGrant>>

\* A certificate orders the next tick.
TickCert(S) ==
  /\ tick < MaxTick
  /\ TickOK(S)
  /\ tick' = tick + 1
  /\ lastAt' = IF Mut = "M_RELATIVETICK" THEN clock ELSE lastAt
  /\ UNCHANGED <<now, clock, gclock, gtick, delivered, expiry, lease, running, start, endAt, lateGrant, seen>>

RefuseTick(S) ==
  /\ ~TickOK(S)
  /\ seen' = seen \cup {"tickRefused"}
  /\ UNCHANGED <<now, clock, gclock, tick, gtick, lastAt, delivered, expiry, lease, running, start, endAt, lateGrant>>

\* A certificate orders a grant under the intent: a comparison in the log, and each signer's clock.
Grant(S) ==
  /\ delivered
  /\ tick <= expiry
  /\ GrantOK(S)
  /\ lease' = TRUE
  /\ lateGrant' = (lateGrant \/ now >= Deadline(TrueExpiry))
  /\ seen' = seen \cup {"grant"} \cup (IF now > TrueExpiry * P THEN {"slack"} ELSE {})
  /\ UNCHANGED <<now, clock, gclock, tick, gtick, lastAt, delivered, expiry, running, start, endAt>>

RefuseGrant(S) ==
  /\ delivered
  /\ tick <= expiry
  /\ ~GrantOK(S)
  /\ seen' = seen \cup {"grantRefused"}
  /\ UNCHANGED <<now, clock, gclock, tick, gtick, lastAt, delivered, expiry, lease, running, start, endAt, lateGrant>>

\* The governor applies the next tick. An entry at its extent ends.
ApplyTick ==
  /\ gtick < tick
  /\ gtick' = gtick + 1
  /\ IF running /\ gtick + 1 >= endAt
       THEN /\ running' = FALSE
            /\ start' = 0
            /\ endAt' = 0
            /\ seen' = seen \cup {"extentEnded"}
       ELSE UNCHANGED <<running, start, endAt, seen>>
  /\ UNCHANGED <<now, clock, gclock, tick, lastAt, delivered, expiry, lease, lateGrant>>

\* The governor permits an entry under a live lease, while it hears its plane.
StartEntry(ext) ==
  /\ lease
  /\ ~running
  /\ ~Overdue
  /\ running' = TRUE
  /\ start' = gtick
  /\ endAt' = gtick + ext
  /\ seen' = seen \cup {"ran"}
  /\ UNCHANGED <<now, clock, gclock, tick, gtick, lastAt, delivered, expiry, lease, lateGrant>>

\* The next tick is overdue, so the vehicle is alone: the lease and any entry end.
GoAlone ==
  /\ Mut # "M_NOWATCHDOG"
  /\ Overdue
  /\ lease \/ running
  /\ lease' = FALSE
  /\ running' = FALSE
  /\ start' = 0
  /\ endAt' = 0
  /\ seen' = seen \cup {"alone"}
  /\ UNCHANGED <<now, clock, gclock, tick, gtick, lastAt, delivered, expiry, lateGrant>>

Next ==
  \/ \E d \in Steps, g \in 0..2 : Advance(d, g)
  \/ Deliver
  \/ ApplyTick
  \/ GoAlone
  \/ \E S \in Certs : TickCert(S) \/ RefuseTick(S) \/ Grant(S) \/ RefuseGrant(S)
  \/ \E ext \in Extents : StartEntry(ext)

Spec == Init /\ [][Next]_vars

\* --- the properties -----------------------------------------------------------

NoGrantPastExpiry == ~lateGrant

EntryEndsAtExtent ==
  running =>
    /\ gtick < endAt
    /\ gtick < start + MaxExtent
    /\ gclock <= Deadline(gtick)

Stretched == running /\ now > Deadline(gtick)

NoStretchUnlessSlow == GovClass # "slow" => ~Stretched

Safe == NoGrantPastExpiry /\ EntryEndsAtExtent /\ NoStretchUnlessSlow

\* --- witnesses: each must be VIOLATED ------------------------------------------

NeverGranted      == "grant" \notin seen
NeverGrantInSlack == "slack" \notin seen
NeverGrantRefused == "grantRefused" \notin seen
NeverTickRefused  == "tickRefused" \notin seen
NeverWithheld     == "withheld" \notin seen
NeverEntryRan     == "ran" \notin seen
NeverExtentEnded  == "extentEnded" \notin seen
NeverAlone        == "alone" \notin seen
NeverStalled      == now < Deadline(tick + 1)
NeverStretched    == ~Stretched
=============================================================================
