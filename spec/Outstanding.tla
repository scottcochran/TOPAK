----------------------------- MODULE Outstanding -----------------------------
(* Revocation below the intent boundary, bounded in effects: ADR-0063          *)
(* (Proposed), its ratification condition (§8), and proposal §10 of            *)
(* derived/topak-federated-c2-design-proposal-2026.11.10b.md. The intent       *)
(* boundary reads a plane's record and answers with watermarks; a plane may    *)
(* have `KUp` effects outstanding and no more; each governor keeps the same    *)
(* account for itself.                                                         *)
(*                                                                             *)
(* THERE IS NO CLOCK IN THIS MODULE, and that absence is the point of it.      *)
(* ADR-0063 §6: the bound reads no clock, so ADR-0032's first clause holds and *)
(* is computed rather than stated. No variable or guard here is a time. A cut  *)
(* link, a late watermark and a watermark never delivered are all behaviours   *)
(* of the same actions, taken or not.                                          *)
(*                                                                             *)
(*   EffectsAfterHonest      after the intent boundary orders a revocation,    *)
(*                           the vehicles of an honest plane produce fewer     *)
(*                           than KUp further effects (§4, first row)          *)
(*   EffectsAfterPerGovernor under any plane, each honest governor produces    *)
(*                           fewer than KUp further effects (§4, first row)    *)
(*   EffectsAfterRevocationBounded   the two together                          *)
(*   HavocPlaneBoundedInEffects      each honest governor has permitted fewer  *)
(*                           than KUp effects that no watermark covers, the    *)
(*                           plane signing anything (§3)                       *)
(*   SealedIsSpent           a lease a watermark covers produces no further    *)
(*                           effect (§4's argument)                            *)
(*   CountExact              no lease permits more entries than its count.     *)
(*                           §4's third clause of the first row, "at most what *)
(*                           is left of its lease's count", is this            *)
(*                                                                             *)
(* What is modelled. `slot` is a fixed set of three lease slots, of which the  *)
(* constant `Active` may be used; a slot is reclaimed once its lease has been  *)
(* read and released, so the number of leases over a behaviour is unbounded    *)
(* and the number outstanding at once is at most three. Two governors, honest. *)
(* A watermark is one lease's coverage: a watermark covering several leases is *)
(* several of these delivered together, and the adversary may deliver fewer,   *)
(* so this has more behaviours and not fewer. `mark` says whether it was       *)
(* ordered `before` or `after` the revocation, and a watermark ordered after   *)
(* carries the moved fence. `read` is what the boundary has read of the lease. *)
(* Truth is the boundary's: a watermark exists only if the boundary ordered    *)
(* it, because its certificate cannot be forged (ADR-0059 §5). A captured      *)
(* plane cannot forge a vehicle's seal (ADR-0062 §6), so the boundary marks    *)
(* only what the governor sealed. A captured plane grants what it likes, and   *)
(* delivers or withholds any watermark; so the plane's charge means nothing    *)
(* under capture and the governor's account does. `pc` and `gc` are the two    *)
(* accounts, read as sums over the slots, so a charge is one bit on one slot.  *)
(* A fence pushed ahead of a watermark can only stop a plane or a vehicle      *)
(* earlier, so it is not modelled: it subtracts. A plane is not re-seated. An  *)
(* ordered entry is a lease of count one and kind "ordered". Reports are not   *)
(* charged (ADR-0065) and a tick is not an effect, so neither appears.         *)
(*                                                                             *)
(* FINDINGS against ADR-0063, each with its rows.                              *)
(*                                                                             *)
(* 1. §3's governor rule names only leases: "the counts of its own leases that *)
(*    no watermark covers". Read literally, a captured plane can admit ordered *)
(*    entries without limit and an honest governor carries them out unaccounted.*)
(*    M_ORDEREDFREE is that reading and breaks both per-governor properties.   *)
(*    The module charges an ordered entry to the governor's account, which is  *)
(*    what "the same account" and "What is charged is an effect" require. The  *)
(*    sentence should say so.                                                  *)
(* 2. §4's argument says "every effect after the revocation is charged to a    *)
(*    lease or an entry that w does not cover", with w the LAST watermark      *)
(*    before the revocation. A watermark covers one segment and is not         *)
(*    cumulative (§2), so it must read: that no watermark ordered before the   *)
(*    revocation covers. The bound holds on that reading, which is what the    *)
(*    module states: a charge is released by a pre-revocation watermark only.  *)
(* 3. The argument needs the stop to be load-bearing, and only says so         *)
(*    in passing. A watermark ordered after the revocation releases a charge   *)
(*    whose lease may have produced effects after the revocation. If the       *)
(*    hearer released it and went on granting, the bound would fail: M_NOSTOP. *)
(*    What makes it safe is that the same watermark carries the fence.         *)
(* 4. The strict form makes KUp a capacity of KUp - 1, and KUp = 1 grants      *)
(*    nothing at all. So a charter's kUp must be at least 2, and a lease whose *)
(*    count is KUp or more can never be granted. Neither is stated. Row        *)
(*    w-k1-nogrant.                                                            *)
(*                                                                             *)
(* Mut = "none":           ADR-0063 as drafted.                                *)
(* Mut = "M_NOCHARGE":     a lease is granted without charging the plane.      *)
(*                         EffectsAfterHonest must fail.                       *)
(* Mut = "M_ATMOST":       the bound is "at most KUp" (§3), which lets one     *)
(*                         more through: ADR-0039's finding about K.           *)
(*                         EffectsAfterHonest, EffectsAfterPerGovernor and     *)
(*                         HavocPlaneBoundedInEffects must fail.               *)
(* Mut = "M_TRUSTMARK":    a governor takes a captured plane's word for what   *)
(*                         has been read. EffectsAfterPerGovernor and          *)
(*                         HavocPlaneBoundedInEffects must fail.               *)
(* Mut = "M_EARLYRELEASE": a watermark may cover a lease not yet sealed.       *)
(*                         SealedIsSpent must fail, and the other three.       *)
(* Mut = "M_NOSTOP":       a plane or a governor that hears the moved fence    *)
(*                         does not stop. Added: finding 3.                    *)
(*                         EffectsAfterHonest and EffectsAfterPerGovernor must *)
(*                         fail, and HavocPlaneBoundedInEffects must hold.     *)
(* Mut = "M_ORDEREDFREE":  §3's governor rule read literally. Added: finding   *)
(*                         1. EffectsAfterPerGovernor and                      *)
(*                         HavocPlaneBoundedInEffects must fail.               *)
(*                                                                             *)
(* Deadlock is not checked: a plane that has stopped is safe.                  *)
EXTENDS Naturals

CONSTANTS Mut, KUp, MaxCount, Active, PlaneCaptured

Slots     == {"l1", "l2", "l3"}
Governors == {"g1", "g2"}
Kinds     == {"lease", "ordered"}

ASSUME ActiveSlots == Active \subseteq Slots
ASSUME KUpPositive == KUp \in Nat /\ KUp >= 1
ASSUME CapturedBool == PlaneCaptured \in BOOLEAN

Free == [st |-> "free", gov |-> "none", kind |-> "lease", count |-> 0, used |-> 0,
         after |-> 0, mark |-> "none", read |-> 0, pc |-> FALSE, gc |-> FALSE]

VARIABLES slot, revoked, pStopped, gStopped, spent, seen
vars == <<slot, revoked, pStopped, gStopped, spent, seen>>

Init ==
  /\ slot = [x \in Slots |-> Free]
  /\ revoked = FALSE
  /\ pStopped = FALSE
  /\ gStopped = [g \in Governors |-> FALSE]
  /\ spent = FALSE
  /\ seen = {}

\* The two accounts, as sums over the literal slots.
PC(x) == IF slot[x].pc THEN slot[x].count ELSE 0
Charge == PC("l1") + PC("l2") + PC("l3")
GC(g, x) == IF slot[x].gc /\ slot[x].gov = g THEN slot[x].count ELSE 0
Acct(g) == GC(g, "l1") + GC(g, "l2") + GC(g, "l3")

\* The mechanism's guards, each open to one mutation.
Bound(n)         == IF Mut = "M_ATMOST" THEN n <= KUp ELSE n < KUp
PlaneCharges     == Mut # "M_NOCHARGE"
GovCounts(k)     == ~(Mut = "M_ORDEREDFREE" /\ k = "ordered")
Stops            == Mut # "M_NOSTOP"
PlaneAllows(n)   == PlaneCaptured \/ (~pStopped /\ Bound(Charge + n))
GovAllows(g, n, k) == ~gStopped[g] /\ (~GovCounts(k) \/ Bound(Acct(g) + n))
Markable(x)      == slot[x].st = "sealed" \/ (Mut = "M_EARLYRELEASE" /\ slot[x].st = "live")

Fresh(g, n, k) == [Free EXCEPT !.st = "live", !.gov = g, !.kind = k, !.count = n,
                               !.pc = PlaneCharges, !.gc = GovCounts(k)]

\* The plane grants a lease, or admits an ordered entry, and the governor accepts it.
Grant(x, g, n, k) ==
  /\ x \in Active
  /\ slot[x].st = "free"
  /\ k = "lease" \/ n = 1
  /\ PlaneAllows(n)
  /\ GovAllows(g, n, k)
  /\ slot' = [slot EXCEPT ![x] = Fresh(g, n, k)]
  /\ seen' = seen \cup {"grant"}
  /\ UNCHANGED <<revoked, pStopped, gStopped, spent>>

\* The governor permits one entry under a lease. The count is its own arithmetic.
Effect(x) ==
  /\ slot[x].st = "live"
  /\ slot[x].used < slot[x].count
  /\ ~gStopped[slot[x].gov]
  /\ slot' = [slot EXCEPT ![x].used = @ + 1, ![x].after = @ + (IF revoked THEN 1 ELSE 0)]
  /\ spent' = (spent \/ slot[x].mark # "none")
  /\ seen' = seen \cup {"effect"}
  /\ UNCHANGED <<revoked, pStopped, gStopped>>

\* A lease ends and the governor seals it: any reason, at any moment.
Seal(x) ==
  /\ slot[x].st = "live"
  /\ slot' = [slot EXCEPT ![x].st = "sealed"]
  /\ UNCHANGED <<revoked, pStopped, gStopped, spent, seen>>

\* The intent boundary orders the revocation (or a fence).
Revoke ==
  /\ ~revoked
  /\ revoked' = TRUE
  /\ seen' = seen \cup {"revoked"}
  /\ UNCHANGED <<slot, pStopped, gStopped, spent>>

\* The intent boundary orders a watermark covering a sealed lease.
Mark(x) ==
  /\ Markable(x)
  /\ slot[x].mark = "none"
  /\ slot' = [slot EXCEPT ![x].mark = IF revoked THEN "after" ELSE "before", ![x].read = slot[x].used]
  /\ seen' = seen \cup {"mark"}
  /\ UNCHANGED <<revoked, pStopped, gStopped, spent>>

\* The plane hears a watermark and releases the charge. One ordered after the revocation
\* carries the moved fence, and the plane stops.
HearP(x) ==
  /\ slot[x].mark # "none"
  /\ slot[x].pc
  /\ slot' = [slot EXCEPT ![x].pc = FALSE]
  /\ pStopped' = (pStopped \/ (slot[x].mark = "after" /\ Stops))
  /\ seen' = seen \cup {"release"}
           \cup (IF revoked /\ slot[x].mark = "before" THEN {"lateRelease"} ELSE {})
  /\ UNCHANGED <<revoked, gStopped, spent>>

\* The governor hears a watermark over its own lease: a certificate it checks.
HearG(x) ==
  /\ slot[x].mark # "none"
  /\ slot[x].gc
  /\ slot' = [slot EXCEPT ![x].gc = FALSE]
  /\ gStopped' = [gStopped EXCEPT ![slot[x].gov] = @ \/ (slot[x].mark = "after" /\ Stops)]
  /\ seen' = seen \cup {"release"}
  /\ UNCHANGED <<revoked, pStopped, spent>>

\* Under M_TRUSTMARK a governor releases on its captured plane's word.
HearWord(x) ==
  /\ Mut = "M_TRUSTMARK"
  /\ PlaneCaptured
  /\ slot[x].st = "sealed"
  /\ slot[x].mark = "none"
  /\ slot[x].gc
  /\ slot' = [slot EXCEPT ![x].gc = FALSE]
  /\ UNCHANGED <<revoked, pStopped, gStopped, spent, seen>>

\* A slot read and released is free for another lease.
Reclaim(x) ==
  /\ slot[x].st = "sealed"
  /\ slot[x].mark = "before"
  /\ ~slot[x].pc
  /\ ~slot[x].gc
  /\ slot' = [slot EXCEPT ![x] = Free]
  /\ seen' = seen \cup {"reclaim"}
  /\ UNCHANGED <<revoked, pStopped, gStopped, spent>>

\* The plane refuses for what is outstanding, and not for the size of the lease alone.
RefuseBound(n) ==
  /\ ~PlaneCaptured
  /\ n < KUp
  /\ ~Bound(Charge + n)
  /\ seen' = seen \cup {"refBound"}
  /\ UNCHANGED <<slot, revoked, pStopped, gStopped, spent>>

\* A governor refuses what its plane would grant, on its own account.
RefuseGov(g, n) ==
  /\ PlaneCaptured
  /\ n < KUp
  /\ ~Bound(Acct(g) + n)
  /\ seen' = seen \cup {"refGov"}
  /\ UNCHANGED <<slot, revoked, pStopped, gStopped, spent>>

Next ==
  \/ \E x \in Slots, g \in Governors, n \in 1..MaxCount, k \in Kinds : Grant(x, g, n, k)
  \/ \E x \in Slots : Effect(x) \/ Seal(x) \/ Mark(x) \/ HearP(x) \/ HearG(x) \/ HearWord(x) \/ Reclaim(x)
  \/ Revoke
  \/ \E n \in 1..MaxCount : RefuseBound(n)
  \/ \E g \in Governors, n \in 1..MaxCount : RefuseGov(g, n)

Spec == Init /\ [][Next]_vars

\* --- the properties -------------------------------------------------------------

TotalAfter == slot["l1"].after + slot["l2"].after + slot["l3"].after
AfterAt(g, x) == IF slot[x].gov = g THEN slot[x].after ELSE 0
AfterOf(g) == AfterAt(g, "l1") + AfterAt(g, "l2") + AfterAt(g, "l3")
UnreadAt(g, x) == IF slot[x].gov = g THEN slot[x].used - slot[x].read ELSE 0
UnreadOf(g) == UnreadAt(g, "l1") + UnreadAt(g, "l2") + UnreadAt(g, "l3")

EffectsAfterHonest      == ~PlaneCaptured => TotalAfter < KUp
EffectsAfterPerGovernor == \A g \in Governors : AfterOf(g) < KUp
EffectsAfterRevocationBounded == EffectsAfterHonest /\ EffectsAfterPerGovernor
HavocPlaneBoundedInEffects == \A g \in Governors : UnreadOf(g) < KUp
SealedIsSpent == ~spent
CountExact == \A x \in Slots : slot[x].used <= slot[x].count

Safe == EffectsAfterRevocationBounded /\ HavocPlaneBoundedInEffects /\ SealedIsSpent /\ CountExact

\* --- witnesses: each must be VIOLATED, except NeverGranted at KUp = 1 ----------------

NeverGranted         == "grant" \notin seen
NeverEffect          == "effect" \notin seen
NeverEffectAfter     == TotalAfter = 0
NeverTight           == TotalAfter < KUp - 1
NeverRefusedAtBound  == "refBound" \notin seen
NeverGovernorRefused == "refGov" \notin seen
NeverStopped         == ~pStopped /\ \A g \in Governors : ~gStopped[g]
NeverLateRelease     == "lateRelease" \notin seen
NeverRecycled        == "reclaim" \notin seen
NeverCovered         == \A x \in Slots : slot[x].mark = "none"
=============================================================================
