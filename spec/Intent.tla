-------------------------------- MODULE Intent --------------------------------
(* Every effect is admitted at the intent boundary: ADR-0060 (Proposed), its   *)
(* ratification condition (§7), with EveryEffectHasALease from ADR-0062 §2     *)
(* and §11, and proposal §10 of                                                *)
(* derived/topak-federated-c2-design-proposal-2026.11.10b.md.                  *)
(*                                                                             *)
(* Two sides. The commanded plane orders intents: the first by the tally that  *)
(* promoted the mesh, each later one by one operator, every field the promoted *)
(* seating's or narrower ⟨Q4⟩. The autonomous plane grants each vehicle a      *)
(* lease under the live intent, and its log takes nothing that changes         *)
(* authority. A vehicle's governor permits each entry under its lease and      *)
(* counts it, with no further round.                                           *)
(*                                                                             *)
(*   EveryEffectHasAnIntent  every reversible effect has an intent ordered at  *)
(*                           the commanded plane before it, live when the      *)
(*                           effect's lease was granted (§1)                   *)
(*   EveryEffectHasALease    every reversible effect has a lease ordered at    *)
(*                           its plane before it, and is within that lease's   *)
(*                           count (ADR-0062 §2)                               *)
(*   IntentNarrows           every intent is within the promoted seating, and  *)
(*                           not merely within the last intent (§2)            *)
(*   AutonomousAddsNothing   the autonomous plane's log holds no promotion,    *)
(*                           seating, issuance, bundle change or operator's    *)
(*                           grant, and no change of membership off its        *)
(*                           schedule (§3)                                     *)
(*                                                                             *)
(* What is abstracted. An irreversible effect, and so proposal §10's "or a     *)
(* person's act", is Release.tla's: every effect here is reversible. Time is   *)
(* nondeterminism: an intent ends by EndIntent, whichever of expiry, revocation*)
(* and a fence it was. An intent has two of its fields: `envelope` (a set,     *)
(* narrowed by subset) and `budget` (a number, narrowed by <=). `expiry` and   *)
(* `task` have the shape of those two and are not repeated. ADR-0050's live    *)
(* lease and live peer on a successor are that record's and are not modelled.  *)
(* A lease's fields other than its count are within the intent by              *)
(* Federation.tla's LeaseWithinChain, an intent being a charter for one round. *)
(* The membership schedule's own rule is Membership.tla's: here a scheduled    *)
(* step and an unscheduled one are two kinds of log entry.                     *)
(*                                                                             *)
(* THE AUTONOMOUS PLANE IS HONEST HERE. A captured plane is a havoc issuer     *)
(* (ADR-0059 §4): it can sign a lease under an intent that has ended, and no   *)
(* log of its own is evidence. What bounds it is Federation.tla's chain check  *)
(* and Outstanding.tla. So "live when its lease was granted" is a claim about  *)
(* an honest plane, and §3's claim is a claim about the log of an honest one.  *)
(* EndLease is free, so a lease may outlive its intent, and an effect can      *)
(* follow its intent's end: the witness NeverEffectAfterIntentEnded is         *)
(* violated. That is the case ADR-0063 bounds, and §1's predecessor is ordered *)
(* before the effect, not live at it.                                          *)
(*                                                                             *)
(* Mut = "none":           ADR-0060 and ADR-0062 §2 as drafted.                *)
(* Mut = "M_NOINTENT":     the autonomous plane grants a lease with no live    *)
(*                         intent. EveryEffectHasAnIntent must fail.           *)
(* Mut = "M_NOCOUNT":      the governor does not count.                        *)
(*                         EveryEffectHasALease must fail.                     *)
(* Mut = "M_WIDEINTENT":   a successor widens the envelope past the seating.   *)
(*                         IntentNarrows must fail.                            *)
(* Mut = "M_LASTINTENT":   ADR-0050's rule, which ⟨Q4⟩ declined: a successor   *)
(*                         is bounded by the last intent. No property fails.   *)
(*                         Its effect is that a commander who narrows cannot   *)
(*                         restore: the witness NeverRestored is no longer     *)
(*                         violated. An addition to proposal §10's table.      *)
(* Mut = "M_LITEPROMOTES": the autonomous plane orders a promotion.            *)
(*                         AutonomousAddsNothing must fail.                    *)
(*                                                                             *)
(* MaxRound, MaxLease and MaxEffects only cut the state space. Deadlock is not *)
(* checked: an intent that has ended and is not followed is safe.              *)
EXTENDS Naturals

CONSTANTS Mut, Vehicles, SeatingBudget, MaxRound, MaxLease, MaxCount, MaxEffects

Entries         == {"e1", "e2", "e3"}
SeatingEnvelope == {"e1", "e2"}

AuthorityKinds == {"promotion", "seating", "issuance", "bundle", "operatorGrant", "offSchedule"}
AllowedKinds   == {"subtract", "scheduleStep"}
LogKinds       == AuthorityKinds \cup AllowedKinds

NoIntent == [live |-> FALSE, envelope |-> {}, budget |-> 0]
NoLease  == [live |-> FALSE, gen |-> 0, count |-> 0, used |-> 0, intent |-> 0]

IntentSpace == [envelope : SUBSET Entries, budget : 1..(SeatingBudget + 1)]

VARIABLES round, intent, spent, lease, ordered, granted, effects, log, seen
vars == <<round, intent, spent, lease, ordered, granted, effects, log, seen>>

Init ==
  /\ round   = 0
  /\ intent  = NoIntent
  /\ spent   = 0
  /\ lease   = [v \in Vehicles |-> NoLease]
  /\ ordered = {}
  /\ granted = {}
  /\ effects = {}
  /\ log     = {}
  /\ seen    = {}

\* The mechanism's guards, each open to one mutation.
EnvelopeOK(o) ==
  IF round >= 1 /\ Mut = "M_WIDEINTENT" THEN TRUE
  ELSE IF round >= 1 /\ Mut = "M_LASTINTENT" THEN o.envelope \subseteq intent.envelope
  ELSE o.envelope \subseteq SeatingEnvelope
Bounded(o) == EnvelopeOK(o) /\ o.budget <= SeatingBudget

LiveOK     == Mut = "M_NOINTENT" \/ intent.live
Budgeted   == intent.live => spent < intent.budget
Counted(v) == Mut = "M_NOCOUNT" \/ lease[v].used < lease[v].count
Admissible(k) == k \in AllowedKinds \/ (Mut = "M_LITEPROMOTES" /\ k = "promotion")

\* The intent a grant is made under: the live one's round, and 0 if none is live.
LiveRound == IF intent.live THEN round ELSE 0

\* The commanded plane orders an intent: by the promotion's tally when it is the first, by
\* one operator when it is a later one. Either way it is bounded by the promoted seating.
Order(o) ==
  /\ round < MaxRound
  /\ Bounded(o)
  /\ round' = round + 1
  /\ intent' = [live |-> TRUE, envelope |-> o.envelope, budget |-> o.budget]
  /\ spent' = 0
  /\ ordered' = ordered \cup {[round |-> round + 1, envelope |-> o.envelope, budget |-> o.budget]}
  /\ seen' = seen \cup (IF /\ round >= 1
                           /\ ~(o.envelope \subseteq intent.envelope)
                           /\ o.envelope \subseteq SeatingEnvelope
                        THEN {"restored"} ELSE {})
  /\ UNCHANGED <<lease, granted, effects, log>>

RefuseOrder(o) ==
  /\ round < MaxRound
  /\ ~Bounded(o)
  /\ seen' = seen \cup {"refWide"}
  /\ UNCHANGED <<round, intent, spent, lease, ordered, granted, effects, log>>

\* An intent ends: at its expiry, its budget spent, ended or revoked, or a plane above fenced.
EndIntent ==
  /\ intent.live
  /\ intent' = [intent EXCEPT !.live = FALSE]
  /\ UNCHANGED <<round, spent, lease, ordered, granted, effects, log, seen>>

\* The autonomous plane's one grant: a vehicle's lease under the live intent, ordered.
\* A re-lease after a lease has ended is charged again ⟨Q15⟩.
Grant(v, c) ==
  /\ LiveOK
  /\ Budgeted
  /\ ~lease[v].live
  /\ lease[v].gen < MaxLease
  /\ lease' = [lease EXCEPT ![v] = [live |-> TRUE, gen |-> lease[v].gen + 1, count |-> c,
                                    used |-> 0, intent |-> LiveRound]]
  /\ spent' = IF intent.live THEN spent + 1 ELSE spent
  /\ granted' = granted \cup {[v |-> v, gen |-> lease[v].gen + 1, count |-> c, intent |-> LiveRound]}
  /\ log' = log \cup {"lease"}
  /\ seen' = seen \cup {"leased"}
                  \cup (IF lease[v].gen >= 1 /\ lease[v].intent = LiveRound /\ LiveRound >= 1
                        THEN {"relet"} ELSE {})
  /\ UNCHANGED <<round, intent, ordered, effects>>

RefuseGrant(v) ==
  /\ ~lease[v].live
  /\ lease[v].gen < MaxLease
  /\ ~(LiveOK /\ Budgeted)
  /\ seen' = seen \cup (IF LiveOK THEN {} ELSE {"refNoIntent"})
                  \cup (IF Budgeted THEN {} ELSE {"refBudget"})
  /\ UNCHANGED <<round, intent, spent, lease, ordered, granted, effects, log>>

\* The governor permits an entry under its lease, counts it, and asks no plane.
Effect(v) ==
  /\ lease[v].live
  /\ Counted(v)
  /\ lease[v].used < MaxEffects
  /\ effects' = effects \cup {[v |-> v, gen |-> lease[v].gen, n |-> lease[v].used + 1,
                               intent |-> lease[v].intent]}
  /\ lease' = [lease EXCEPT ![v].used = lease[v].used + 1]
  /\ seen' = seen \cup {"effect"}
                  \cup (IF lease[v].used + 1 = lease[v].count THEN {"countSpent"} ELSE {})
                  \cup (IF LiveRound # lease[v].intent THEN {"afterEnd"} ELSE {})
  /\ UNCHANGED <<round, intent, spent, ordered, granted, log>>

RefuseEffect(v) ==
  /\ lease[v].live
  /\ ~Counted(v)
  /\ seen' = seen \cup {"refCount"}
  /\ UNCHANGED <<round, intent, spent, lease, ordered, granted, effects, log>>

\* A lease ends: its count spent, at its ttl, ended, revoked, fenced, or its vehicle alone.
EndLease(v) ==
  /\ lease[v].live
  /\ lease' = [lease EXCEPT ![v].live = FALSE]
  /\ UNCHANGED <<round, intent, spent, ordered, granted, effects, log, seen>>

\* What the autonomous plane's log may take. Anything may be proposed to it.
AutoOrder(k) ==
  /\ Admissible(k)
  /\ k \notin log
  /\ log' = log \cup {k}
  /\ UNCHANGED <<round, intent, spent, lease, ordered, granted, effects, seen>>

AutoRefuse(k) ==
  /\ ~Admissible(k)
  /\ seen' = seen \cup {"refAuth"}
  /\ UNCHANGED <<round, intent, spent, lease, ordered, granted, effects, log>>

Next ==
  \/ \E o \in IntentSpace : Order(o) \/ RefuseOrder(o)
  \/ EndIntent
  \/ \E v \in Vehicles :
       \/ \E c \in 1..MaxCount : Grant(v, c)
       \/ RefuseGrant(v) \/ Effect(v) \/ RefuseEffect(v) \/ EndLease(v)
  \/ \E k \in LogKinds : AutoOrder(k) \/ AutoRefuse(k)

Spec == Init /\ [][Next]_vars

\* --- the four properties ------------------------------------------------------

EveryEffectHasAnIntent == \A x \in effects : \E i \in ordered : i.round = x.intent

EveryEffectHasALease ==
  \A x \in effects : \E l \in granted : l.v = x.v /\ l.gen = x.gen /\ x.n <= l.count

IntentNarrows ==
  \A x \in ordered : x.envelope \subseteq SeatingEnvelope /\ x.budget <= SeatingBudget

AutonomousAddsNothing == log \cap AuthorityKinds = {}

Safe == EveryEffectHasAnIntent /\ EveryEffectHasALease /\ IntentNarrows /\ AutonomousAddsNothing

\* --- witnesses: each must be VIOLATED ------------------------------------------

NeverOrdered     == ordered = {}
NeverSuccessor   == round < 2
NeverRestored    == "restored" \notin seen
NeverRefusedWide == "refWide" \notin seen
NeverLeased      == "leased" \notin seen
NeverEffect      == "effect" \notin seen
NeverCountSpent  == "countSpent" \notin seen
NeverEffectAfterIntentEnded == "afterEnd" \notin seen
NeverRefusedAtCount    == "refCount" \notin seen
NeverRefusedNoIntent   == "refNoIntent" \notin seen
NeverRefusedBudget     == "refBudget" \notin seen
NeverReletSameIntent   == "relet" \notin seen
NeverRefusedAuthority  == "refAuth" \notin seen
NeverScheduleStep      == "scheduleStep" \notin log
=============================================================================
