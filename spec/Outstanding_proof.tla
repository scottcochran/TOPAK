-------------------------- MODULE Outstanding_proof --------------------------
(* TLAPS proof of the invariants of Outstanding.tla (ADR-0063 §8), for every   *)
(* value of the constants the assumptions below admit: every KUp, every lease  *)
(* count, every set of active slots, a plane captured or not. Outstanding.tla  *)
(* is not edited. No assumption here mentions time, and the module has none.   *)
(*                                                                             *)
(*   THEOREM CountExactAlways                 [no hypothesis]                  *)
(*   THEOREM SealedIsSpentAlways              [Mut # "M_EARLYRELEASE"]         *)
(*   THEOREM EffectsAfterHonestAlways         [Mut # "M_NOCHARGE", "M_ATMOST", *)
(*                                             "M_EARLYRELEASE", "M_NOSTOP"]   *)
(*   THEOREM EffectsAfterPerGovernorAlways    [Mut # "M_ATMOST",               *)
(*                                             "M_EARLYRELEASE", "M_NOSTOP",   *)
(*                                             "M_TRUSTMARK", "M_ORDEREDFREE"] *)
(*   THEOREM HavocPlaneBoundedInEffectsAlways [Mut # "M_ATMOST",               *)
(*                                             "M_EARLYRELEASE", "M_TRUSTMARK",*)
(*                                             "M_ORDEREDFREE"]                *)
(*   THEOREM SafeAlways                       [Mut = "none"]                   *)
(*                                                                             *)
(* The strengthening. `Shape` holds under every mutation: the type invariant,  *)
(* used within count, after within used, read within used, a free slot is the  *)
(* empty record, a slot in use has a governor, and nothing is counted after a  *)
(* revocation that has not happened. `Sealed` adds, under no early release,    *)
(* that a marked lease is sealed and fully read, and that a lease marked       *)
(* before the revocation has no effect after it. Those two carry §4's          *)
(* argument: what a pre-revocation watermark releases produced nothing after   *)
(* the revocation.                                                             *)
(*                                                                             *)
(* The bounds. A charge is released only by a mark (`PUnmarked`, `GUnmarked`). *)
(* A lease marked after the revocation is released only by a hearer that then  *)
(* stops (`PStopped`, `GStopped`), so while a hearer still grants, its account *)
(* equals the account that also counts those leases (`CA`, `CG`). So that      *)
(* second sum never reaches KUp, it bounds the effects after the revocation    *)
(* term by term, and the unread effects are bounded by the governor's own      *)
(* account alone, which needs no stop.                                         *)
(*                                                                             *)
(* Mutations and witnesses are behaviours and stay with TLC                    *)
(* (Outstanding-results-*.txt). Check: tools/tlapm --cleanfp --strict.         *)
EXTENDS Outstanding, TLAPS

ASSUME MaxCountNat == MaxCount \in Nat

SlotRec == [st : {"free", "live", "sealed"}, gov : Governors \cup {"none"}, kind : Kinds,
            count : Nat, used : Nat, after : Nat, mark : {"none", "before", "after"}, read : Nat,
            pc : BOOLEAN, gc : BOOLEAN]
Tags == {"grant", "effect", "revoked", "mark", "release", "lateRelease", "reclaim", "refBound", "refGov"}

TypeOK ==
  /\ slot \in [Slots -> SlotRec]
  /\ revoked \in BOOLEAN
  /\ pStopped \in BOOLEAN
  /\ gStopped \in [Governors -> BOOLEAN]
  /\ spent \in BOOLEAN
  /\ seen \subseteq Tags

ShapeS ==
  \A x \in Slots :
    /\ slot[x].used <= slot[x].count
    /\ slot[x].after <= slot[x].used
    /\ slot[x].read <= slot[x].used
    /\ (slot[x].st = "free" => slot[x] = Free)
    /\ (slot[x].st # "free" => slot[x].gov \in Governors)
    /\ (~revoked => slot[x].after = 0)

Shape == TypeOK /\ ShapeS

MarkedSealed == \A x \in Slots : slot[x].mark # "none" => (slot[x].st = "sealed" /\ slot[x].read = slot[x].used)
BeforeZero   == \A x \in Slots : slot[x].mark = "before" => slot[x].after = 0
Sealed == Shape /\ MarkedSealed /\ BeforeZero

PUnmarked == \A x \in Slots : (~slot[x].pc /\ slot[x].st # "free") => slot[x].mark # "none"
GUnmarked == \A x \in Slots : (~slot[x].gc /\ slot[x].st # "free") => slot[x].mark # "none"
PStopAfter == \A x \in Slots : (slot[x].mark = "after" /\ ~slot[x].pc) => pStopped
GStopAfter == \A x \in Slots : (slot[x].mark = "after" /\ ~slot[x].gc) => gStopped[slot[x].gov]

CA(x) == IF slot[x].pc \/ slot[x].mark = "after" THEN slot[x].count ELSE 0
EffCharge == CA("l1") + CA("l2") + CA("l3")
HonestBound == ~PlaneCaptured => EffCharge < KUp

CG(g, x) == IF slot[x].gov = g /\ (slot[x].gc \/ slot[x].mark = "after") THEN slot[x].count ELSE 0
GovEffCharge(g) == CG(g, "l1") + CG(g, "l2") + CG(g, "l3")
PerGovBound == \A g \in Governors : GovEffCharge(g) < KUp

AcctBound == \A g \in Governors : Acct(g) < KUp

InvH == Sealed /\ PUnmarked /\ PStopAfter /\ HonestBound
InvG == Sealed /\ GUnmarked /\ GStopAfter /\ PerGovBound
InvU == Sealed /\ GUnmarked /\ AcctBound
-----------------------------------------------------------------------------
LEMMA SlotsLiteral == \A x \in Slots : x = "l1" \/ x = "l2" \/ x = "l3"
  BY DEF Slots

LEMMA SlotsMembers == "l1" \in Slots /\ "l2" \in Slots /\ "l3" \in Slots
  BY DEF Slots

LEMMA FreeFacts ==
  /\ Free \in SlotRec
  /\ Free.st = "free" /\ Free.gov = "none" /\ Free.count = 0 /\ Free.used = 0 /\ Free.after = 0
  /\ Free.mark = "none" /\ Free.read = 0 /\ Free.pc = FALSE /\ Free.gc = FALSE
  BY DEF Free, SlotRec, Kinds

LEMMA FreshFacts ==
  ASSUME NEW g \in Governors, NEW n \in Nat, NEW k \in Kinds
  PROVE  /\ Fresh(g, n, k) \in SlotRec
         /\ Fresh(g, n, k).st = "live" /\ Fresh(g, n, k).gov = g /\ Fresh(g, n, k).kind = k
         /\ Fresh(g, n, k).count = n /\ Fresh(g, n, k).used = 0 /\ Fresh(g, n, k).after = 0
         /\ Fresh(g, n, k).mark = "none" /\ Fresh(g, n, k).read = 0
         /\ Fresh(g, n, k).pc = PlaneCharges /\ Fresh(g, n, k).gc = GovCounts(k)
  BY FreeFacts DEF Fresh, Free, SlotRec, PlaneCharges, GovCounts

LEMMA InitShape == Init => Shape
<1> SUFFICES ASSUME Init PROVE Shape OBVIOUS
<1>1. TypeOK
  BY FreeFacts DEF Init, TypeOK, Tags
<1>2. ShapeS
  BY FreeFacts DEF Init, ShapeS
<1> QED
  BY <1>1, <1>2 DEF Shape

LEMMA GrantFacts ==
  ASSUME TypeOK, NEW x \in Slots, NEW g \in Governors, NEW n \in 1..MaxCount, NEW k \in Kinds,
         Grant(x, g, n, k)
  PROVE  /\ n \in Nat /\ n >= 1
         /\ slot[x].st = "free"
         /\ slot' = [slot EXCEPT ![x] = Fresh(g, n, k)]
         /\ slot'[x] = Fresh(g, n, k)
         /\ \A y \in Slots : y # x => slot'[y] = slot[y]
         /\ PlaneAllows(n) /\ GovAllows(g, n, k)
         /\ seen' = seen \cup {"grant"}
         /\ UNCHANGED <<revoked, pStopped, gStopped, spent>>
  BY MaxCountNat DEF Grant, TypeOK

LEMMA NextShape == Shape /\ [Next]_vars => Shape'
<1> SUFFICES ASSUME Shape, [Next]_vars PROVE Shape' OBVIOUS
<1>0. TypeOK /\ ShapeS
  BY DEF Shape
<1>1. CASE UNCHANGED vars
  BY <1>0, <1>1 DEF Shape, TypeOK, ShapeS, vars
<1>2. ASSUME NEW x \in Slots, NEW g \in Governors, NEW n \in 1..MaxCount, NEW k \in Kinds, Grant(x, g, n, k)
      PROVE Shape'
  <2>1. /\ n \in Nat /\ n >= 1
        /\ slot' = [slot EXCEPT ![x] = Fresh(g, n, k)]
        /\ slot'[x] = Fresh(g, n, k)
        /\ \A y \in Slots : y # x => slot'[y] = slot[y]
        /\ seen' = seen \cup {"grant"}
        /\ UNCHANGED <<revoked, pStopped, gStopped, spent>>
    BY <1>0, <1>2, GrantFacts
  <2>2. Fresh(g, n, k) \in SlotRec
    BY <2>1, FreshFacts
  <2>3. TypeOK'
    BY <1>0, <2>1, <2>2 DEF TypeOK, Tags
  <2>4. ShapeS'
    <3> SUFFICES ASSUME NEW y \in Slots
                 PROVE /\ slot'[y].used <= slot'[y].count
                       /\ slot'[y].after <= slot'[y].used
                       /\ slot'[y].read <= slot'[y].used
                       /\ (slot'[y].st = "free" => slot'[y] = Free)
                       /\ (slot'[y].st # "free" => slot'[y].gov \in Governors)
                       /\ (~revoked' => slot'[y].after = 0)
      BY DEF ShapeS
    <3>1. CASE y = x
      BY <2>1, <3>1, FreshFacts
    <3>2. CASE y # x
      BY <1>0, <2>1, <3>2 DEF ShapeS
    <3> QED
      BY <3>1, <3>2
  <2> QED
    BY <2>3, <2>4 DEF Shape
<1>3. ASSUME NEW x \in Slots, Effect(x) PROVE Shape'
  <2>1. /\ slot[x].st = "live" /\ slot[x].used < slot[x].count
        /\ slot' = [slot EXCEPT ![x].used = @ + 1, ![x].after = @ + (IF revoked THEN 1 ELSE 0)]
        /\ spent' = (spent \/ slot[x].mark # "none")
        /\ seen' = seen \cup {"effect"}
        /\ UNCHANGED <<revoked, pStopped, gStopped>>
    BY <1>3 DEF Effect
  <2>2. /\ slot[x] \in SlotRec
        /\ slot[x].used <= slot[x].count /\ slot[x].after <= slot[x].used /\ slot[x].read <= slot[x].used
        /\ (~revoked => slot[x].after = 0)
        /\ slot[x].gov \in Governors
    BY <1>0, <2>1 DEF TypeOK, ShapeS
  <2>3. TypeOK'
    <3>1. slot' \in [Slots -> SlotRec]
      BY <1>0, <2>1, <2>2 DEF TypeOK, SlotRec
    <3> QED
      BY <1>0, <2>1, <3>1 DEF TypeOK, Tags
  <2>4. ShapeS'
    <3> SUFFICES ASSUME NEW y \in Slots
                 PROVE /\ slot'[y].used <= slot'[y].count
                       /\ slot'[y].after <= slot'[y].used
                       /\ slot'[y].read <= slot'[y].used
                       /\ (slot'[y].st = "free" => slot'[y] = Free)
                       /\ (slot'[y].st # "free" => slot'[y].gov \in Governors)
                       /\ (~revoked' => slot'[y].after = 0)
      BY DEF ShapeS
    <3>1. CASE y = x
      BY <1>0, <2>1, <2>2, <3>1 DEF TypeOK, SlotRec
    <3>2. CASE y # x
      BY <1>0, <2>1, <3>2 DEF ShapeS, TypeOK
    <3> QED
      BY <3>1, <3>2
  <2> QED
    BY <2>3, <2>4 DEF Shape
<1>4. ASSUME NEW x \in Slots, Seal(x) PROVE Shape'
  <2>1. /\ slot[x].st = "live" /\ slot' = [slot EXCEPT ![x].st = "sealed"]
        /\ UNCHANGED <<revoked, pStopped, gStopped, spent, seen>>
    BY <1>4 DEF Seal
  <2>2. slot[x] \in SlotRec /\ slot[x].gov \in Governors
    BY <1>0, <2>1 DEF TypeOK, ShapeS
  <2>3. TypeOK'
    <3>1. slot' \in [Slots -> SlotRec]
      BY <1>0, <2>1, <2>2 DEF TypeOK, SlotRec
    <3> QED
      BY <1>0, <2>1, <3>1 DEF TypeOK
  <2>4. ShapeS'
    <3> SUFFICES ASSUME NEW y \in Slots
                 PROVE /\ slot'[y].used <= slot'[y].count
                       /\ slot'[y].after <= slot'[y].used
                       /\ slot'[y].read <= slot'[y].used
                       /\ (slot'[y].st = "free" => slot'[y] = Free)
                       /\ (slot'[y].st # "free" => slot'[y].gov \in Governors)
                       /\ (~revoked' => slot'[y].after = 0)
      BY DEF ShapeS
    <3>1. CASE y = x
      BY <1>0, <2>1, <2>2, <3>1 DEF TypeOK, SlotRec, ShapeS
    <3>2. CASE y # x
      BY <1>0, <2>1, <3>2 DEF ShapeS, TypeOK
    <3> QED
      BY <3>1, <3>2
  <2> QED
    BY <2>3, <2>4 DEF Shape
<1>5. ASSUME NEW x \in Slots, Mark(x) PROVE Shape'
  <2>1. /\ slot[x].st \in {"sealed", "live"} /\ slot[x].mark = "none"
        /\ slot' = [slot EXCEPT ![x].mark = IF revoked THEN "after" ELSE "before", ![x].read = slot[x].used]
        /\ seen' = seen \cup {"mark"}
        /\ UNCHANGED <<revoked, pStopped, gStopped, spent>>
    BY <1>5 DEF Mark, Markable
  <2>2. slot[x] \in SlotRec /\ slot[x].gov \in Governors
    BY <1>0, <2>1 DEF TypeOK, ShapeS
  <2>3. TypeOK'
    <3>1. slot' \in [Slots -> SlotRec]
      BY <1>0, <2>1, <2>2 DEF TypeOK, SlotRec
    <3> QED
      BY <1>0, <2>1, <3>1 DEF TypeOK, Tags
  <2>4. ShapeS'
    <3> SUFFICES ASSUME NEW y \in Slots
                 PROVE /\ slot'[y].used <= slot'[y].count
                       /\ slot'[y].after <= slot'[y].used
                       /\ slot'[y].read <= slot'[y].used
                       /\ (slot'[y].st = "free" => slot'[y] = Free)
                       /\ (slot'[y].st # "free" => slot'[y].gov \in Governors)
                       /\ (~revoked' => slot'[y].after = 0)
      BY DEF ShapeS
    <3>1. CASE y = x
      BY <1>0, <2>1, <2>2, <3>1 DEF TypeOK, SlotRec, ShapeS
    <3>2. CASE y # x
      BY <1>0, <2>1, <3>2 DEF ShapeS, TypeOK
    <3> QED
      BY <3>1, <3>2
  <2> QED
    BY <2>3, <2>4 DEF Shape
<1>6. ASSUME NEW x \in Slots, HearP(x) PROVE Shape'
  <2>1. /\ slot[x].pc
        /\ slot' = [slot EXCEPT ![x].pc = FALSE]
        /\ pStopped' = (pStopped \/ (slot[x].mark = "after" /\ Stops))
        /\ seen' \subseteq seen \cup {"release", "lateRelease"}
        /\ UNCHANGED <<revoked, gStopped, spent>>
    BY <1>6 DEF HearP
  <2>2. slot[x] \in SlotRec /\ slot[x].st # "free" /\ slot[x].gov \in Governors
    BY <1>0, <2>1, FreeFacts DEF TypeOK, ShapeS
  <2>3. TypeOK'
    <3>1. slot' \in [Slots -> SlotRec]
      BY <1>0, <2>1, <2>2 DEF TypeOK, SlotRec
    <3>2. pStopped' \in BOOLEAN
      BY <1>0, <2>1 DEF TypeOK
    <3>3. seen' \subseteq Tags
      BY <1>0, <2>1 DEF TypeOK, Tags
    <3> QED
      BY <1>0, <2>1, <3>1, <3>2, <3>3 DEF TypeOK
  <2>4. ShapeS'
    <3> SUFFICES ASSUME NEW y \in Slots
                 PROVE /\ slot'[y].used <= slot'[y].count
                       /\ slot'[y].after <= slot'[y].used
                       /\ slot'[y].read <= slot'[y].used
                       /\ (slot'[y].st = "free" => slot'[y] = Free)
                       /\ (slot'[y].st # "free" => slot'[y].gov \in Governors)
                       /\ (~revoked' => slot'[y].after = 0)
      BY DEF ShapeS
    <3>1. CASE y = x
      BY <1>0, <2>1, <2>2, <3>1 DEF TypeOK, SlotRec, ShapeS
    <3>2. CASE y # x
      BY <1>0, <2>1, <3>2 DEF ShapeS, TypeOK
    <3> QED
      BY <3>1, <3>2
  <2> QED
    BY <2>3, <2>4 DEF Shape
<1>7. ASSUME NEW x \in Slots, HearG(x) PROVE Shape'
  <2>1. /\ slot[x].gc
        /\ slot' = [slot EXCEPT ![x].gc = FALSE]
        /\ gStopped' = [gStopped EXCEPT ![slot[x].gov] = @ \/ (slot[x].mark = "after" /\ Stops)]
        /\ seen' = seen \cup {"release"}
        /\ UNCHANGED <<revoked, pStopped, spent>>
    BY <1>7 DEF HearG
  <2>2. slot[x] \in SlotRec /\ slot[x].st # "free" /\ slot[x].gov \in Governors
    BY <1>0, <2>1, FreeFacts DEF TypeOK, ShapeS
  <2>3. TypeOK'
    <3>1. slot' \in [Slots -> SlotRec]
      BY <1>0, <2>1, <2>2 DEF TypeOK, SlotRec
    <3>2. gStopped' \in [Governors -> BOOLEAN]
      BY <1>0, <2>1, <2>2 DEF TypeOK
    <3> QED
      BY <1>0, <2>1, <3>1, <3>2 DEF TypeOK, Tags
  <2>4. ShapeS'
    <3> SUFFICES ASSUME NEW y \in Slots
                 PROVE /\ slot'[y].used <= slot'[y].count
                       /\ slot'[y].after <= slot'[y].used
                       /\ slot'[y].read <= slot'[y].used
                       /\ (slot'[y].st = "free" => slot'[y] = Free)
                       /\ (slot'[y].st # "free" => slot'[y].gov \in Governors)
                       /\ (~revoked' => slot'[y].after = 0)
      BY DEF ShapeS
    <3>1. CASE y = x
      BY <1>0, <2>1, <2>2, <3>1 DEF TypeOK, SlotRec, ShapeS
    <3>2. CASE y # x
      BY <1>0, <2>1, <3>2 DEF ShapeS, TypeOK
    <3> QED
      BY <3>1, <3>2
  <2> QED
    BY <2>3, <2>4 DEF Shape
<1>8. ASSUME NEW x \in Slots, HearWord(x) PROVE Shape'
  <2>1. /\ slot[x].st = "sealed"
        /\ slot' = [slot EXCEPT ![x].gc = FALSE]
        /\ UNCHANGED <<revoked, pStopped, gStopped, spent, seen>>
    BY <1>8 DEF HearWord
  <2>2. slot[x] \in SlotRec /\ slot[x].gov \in Governors
    BY <1>0, <2>1 DEF TypeOK, ShapeS
  <2>3. TypeOK'
    <3>1. slot' \in [Slots -> SlotRec]
      BY <1>0, <2>1, <2>2 DEF TypeOK, SlotRec
    <3> QED
      BY <1>0, <2>1, <3>1 DEF TypeOK
  <2>4. ShapeS'
    <3> SUFFICES ASSUME NEW y \in Slots
                 PROVE /\ slot'[y].used <= slot'[y].count
                       /\ slot'[y].after <= slot'[y].used
                       /\ slot'[y].read <= slot'[y].used
                       /\ (slot'[y].st = "free" => slot'[y] = Free)
                       /\ (slot'[y].st # "free" => slot'[y].gov \in Governors)
                       /\ (~revoked' => slot'[y].after = 0)
      BY DEF ShapeS
    <3>1. CASE y = x
      BY <1>0, <2>1, <2>2, <3>1 DEF TypeOK, SlotRec, ShapeS
    <3>2. CASE y # x
      BY <1>0, <2>1, <3>2 DEF ShapeS, TypeOK
    <3> QED
      BY <3>1, <3>2
  <2> QED
    BY <2>3, <2>4 DEF Shape
<1>9. ASSUME NEW x \in Slots, Reclaim(x) PROVE Shape'
  <2>1. /\ slot' = [slot EXCEPT ![x] = Free]
        /\ seen' = seen \cup {"reclaim"}
        /\ UNCHANGED <<revoked, pStopped, gStopped, spent>>
    BY <1>9 DEF Reclaim
  <2>3. TypeOK'
    <3>1. slot' \in [Slots -> SlotRec]
      BY <1>0, <2>1, FreeFacts DEF TypeOK
    <3> QED
      BY <1>0, <2>1, <3>1 DEF TypeOK, Tags
  <2>4. ShapeS'
    <3> SUFFICES ASSUME NEW y \in Slots
                 PROVE /\ slot'[y].used <= slot'[y].count
                       /\ slot'[y].after <= slot'[y].used
                       /\ slot'[y].read <= slot'[y].used
                       /\ (slot'[y].st = "free" => slot'[y] = Free)
                       /\ (slot'[y].st # "free" => slot'[y].gov \in Governors)
                       /\ (~revoked' => slot'[y].after = 0)
      BY DEF ShapeS
    <3>1. CASE y = x
      BY <1>0, <2>1, <3>1, FreeFacts DEF TypeOK
    <3>2. CASE y # x
      BY <1>0, <2>1, <3>2 DEF ShapeS, TypeOK
    <3> QED
      BY <3>1, <3>2
  <2> QED
    BY <2>3, <2>4 DEF Shape
<1>10. CASE Revoke
  <2>1. /\ revoked' = TRUE /\ seen' = seen \cup {"revoked"}
        /\ UNCHANGED <<slot, pStopped, gStopped, spent>>
    BY <1>10 DEF Revoke
  <2>3. TypeOK'
    BY <1>0, <2>1 DEF TypeOK, Tags
  <2>4. ShapeS'
    BY <1>0, <2>1 DEF ShapeS
  <2> QED
    BY <2>3, <2>4 DEF Shape
<1>11. ASSUME NEW n \in 1..MaxCount, RefuseBound(n) PROVE Shape'
  <2>1. /\ seen' = seen \cup {"refBound"}
        /\ UNCHANGED <<slot, revoked, pStopped, gStopped, spent>>
    BY <1>11 DEF RefuseBound
  <2> QED
    BY <1>0, <2>1 DEF Shape, TypeOK, ShapeS, Tags
<1>12. ASSUME NEW g \in Governors, NEW n \in 1..MaxCount, RefuseGov(g, n) PROVE Shape'
  <2>1. /\ seen' = seen \cup {"refGov"}
        /\ UNCHANGED <<slot, revoked, pStopped, gStopped, spent>>
    BY <1>12 DEF RefuseGov
  <2> QED
    BY <1>0, <2>1 DEF Shape, TypeOK, ShapeS, Tags
<1> QED
  BY <1>1, <1>2, <1>3, <1>4, <1>5, <1>6, <1>7, <1>8, <1>9, <1>10, <1>11, <1>12 DEF Next
-----------------------------------------------------------------------------
THEOREM CountExactAlways == Spec => []CountExact
<1>1. Shape /\ [Next]_vars => Shape'
  BY NextShape
<1>2. Shape => CountExact
  BY DEF Shape, ShapeS, CountExact
<1> QED
  BY InitShape, <1>1, <1>2, PTL DEF Spec
-----------------------------------------------------------------------------
(* Sealed: a marked lease is sealed and read; marked before means nothing after. *)

LEMMA InitSealed == Init => Sealed
<1> SUFFICES ASSUME Init PROVE Sealed OBVIOUS
<1>1. Shape
  BY InitShape
<1>2. MarkedSealed /\ BeforeZero
  BY FreeFacts DEF Init, MarkedSealed, BeforeZero
<1> QED
  BY <1>1, <1>2 DEF Sealed

LEMMA NextSealed ==
  ASSUME Mut # "M_EARLYRELEASE", Sealed, [Next]_vars
  PROVE  Sealed'
<1>0. Shape /\ Shape' /\ MarkedSealed /\ BeforeZero
  BY NextShape DEF Sealed
<1>a. TypeOK /\ TypeOK' /\ ShapeS
  BY <1>0 DEF Shape
<1>1. CASE UNCHANGED slot
  BY <1>0, <1>1 DEF Sealed, MarkedSealed, BeforeZero
<1>2. ASSUME NEW x \in Slots, NEW g \in Governors, NEW n \in 1..MaxCount, NEW k \in Kinds, Grant(x, g, n, k)
      PROVE Sealed'
  <2>1. /\ n \in Nat /\ slot'[x] = Fresh(g, n, k)
        /\ \A y \in Slots : y # x => slot'[y] = slot[y]
    BY <1>a, <1>2, GrantFacts
  <2>2. MarkedSealed' /\ BeforeZero'
    <3>1. Fresh(g, n, k).mark = "none"
      BY <2>1, FreshFacts
    <3> QED
      BY <1>0, <2>1, <3>1 DEF MarkedSealed, BeforeZero
  <2> QED
    BY <1>0, <2>2 DEF Sealed
<1>3. ASSUME NEW x \in Slots, Effect(x) PROVE Sealed'
  <2>1. /\ slot[x].st = "live"
        /\ slot' = [slot EXCEPT ![x].used = @ + 1, ![x].after = @ + (IF revoked THEN 1 ELSE 0)]
    BY <1>3 DEF Effect
  <2>2. slot[x].mark = "none" /\ slot[x] \in SlotRec
    BY <1>0, <1>a, <2>1 DEF MarkedSealed, TypeOK
  <2>3. /\ slot'[x].mark = "none"
        /\ \A y \in Slots : y # x => slot'[y] = slot[y]
    BY <1>a, <2>1, <2>2 DEF TypeOK, SlotRec
  <2>4. MarkedSealed' /\ BeforeZero'
    BY <1>0, <2>3 DEF MarkedSealed, BeforeZero
  <2> QED
    BY <1>0, <2>4 DEF Sealed
<1>4. ASSUME NEW x \in Slots, Seal(x) PROVE Sealed'
  <2>1. /\ slot[x].st = "live" /\ slot' = [slot EXCEPT ![x].st = "sealed"]
    BY <1>4 DEF Seal
  <2>2. slot[x].mark = "none" /\ slot[x] \in SlotRec
    BY <1>0, <1>a, <2>1 DEF MarkedSealed, TypeOK
  <2>3. /\ slot'[x].mark = "none"
        /\ \A y \in Slots : y # x => slot'[y] = slot[y]
    BY <1>a, <2>1, <2>2 DEF TypeOK, SlotRec
  <2>4. MarkedSealed' /\ BeforeZero'
    BY <1>0, <2>3 DEF MarkedSealed, BeforeZero
  <2> QED
    BY <1>0, <2>4 DEF Sealed
<1>5. ASSUME NEW x \in Slots, Mark(x) PROVE Sealed'
  <2>1. /\ slot[x].st = "sealed" /\ slot[x].mark = "none"
        /\ slot' = [slot EXCEPT ![x].mark = IF revoked THEN "after" ELSE "before", ![x].read = slot[x].used]
        /\ revoked' = revoked
    BY <1>5 DEF Mark, Markable
  <2>2. slot[x] \in SlotRec /\ (~revoked => slot[x].after = 0)
    BY <1>a, <2>1 DEF TypeOK, ShapeS
  <2>3. /\ slot'[x].st = "sealed" /\ slot'[x].read = slot[x].used /\ slot'[x].used = slot[x].used
        /\ slot'[x].after = slot[x].after
        /\ slot'[x].mark = IF revoked THEN "after" ELSE "before"
        /\ \A y \in Slots : y # x => slot'[y] = slot[y]
    BY <1>a, <2>1, <2>2 DEF TypeOK, SlotRec
  <2>4. MarkedSealed'
    <3> SUFFICES ASSUME NEW y \in Slots, slot'[y].mark # "none"
                 PROVE slot'[y].st = "sealed" /\ slot'[y].read = slot'[y].used
      BY DEF MarkedSealed
    <3>1. CASE y = x
      BY <2>3, <3>1
    <3>2. CASE y # x
      BY <1>0, <2>3, <3>2 DEF MarkedSealed
    <3> QED
      BY <3>1, <3>2
  <2>5. BeforeZero'
    <3> SUFFICES ASSUME NEW y \in Slots, slot'[y].mark = "before"
                 PROVE slot'[y].after = 0
      BY DEF BeforeZero
    <3>1. CASE y = x
      BY <2>2, <2>3, <3>1
    <3>2. CASE y # x
      BY <1>0, <2>3, <3>2 DEF BeforeZero
    <3> QED
      BY <3>1, <3>2
  <2> QED
    BY <1>0, <2>4, <2>5 DEF Sealed
<1>6. ASSUME NEW x \in Slots, HearP(x) \/ HearG(x) \/ HearWord(x) PROVE Sealed'
  <2>1. slot' = [slot EXCEPT ![x].pc = FALSE] \/ slot' = [slot EXCEPT ![x].gc = FALSE]
    BY <1>6 DEF HearP, HearG, HearWord
  <2>2. slot[x] \in SlotRec
    BY <1>a DEF TypeOK
  <2>3. /\ slot'[x].st = slot[x].st /\ slot'[x].mark = slot[x].mark /\ slot'[x].read = slot[x].read
        /\ slot'[x].used = slot[x].used /\ slot'[x].after = slot[x].after
        /\ \A y \in Slots : y # x => slot'[y] = slot[y]
    BY <1>a, <2>1, <2>2 DEF TypeOK, SlotRec
  <2>4. MarkedSealed' /\ BeforeZero'
    <3>1. MarkedSealed'
      <4> SUFFICES ASSUME NEW y \in Slots, slot'[y].mark # "none"
                   PROVE slot'[y].st = "sealed" /\ slot'[y].read = slot'[y].used
        BY DEF MarkedSealed
      <4>1. CASE y = x
        BY <1>0, <2>3, <4>1 DEF MarkedSealed
      <4>2. CASE y # x
        BY <1>0, <2>3, <4>2 DEF MarkedSealed
      <4> QED
        BY <4>1, <4>2
    <3>2. BeforeZero'
      <4> SUFFICES ASSUME NEW y \in Slots, slot'[y].mark = "before"
                   PROVE slot'[y].after = 0
        BY DEF BeforeZero
      <4>1. CASE y = x
        BY <1>0, <2>3, <4>1 DEF BeforeZero
      <4>2. CASE y # x
        BY <1>0, <2>3, <4>2 DEF BeforeZero
      <4> QED
        BY <4>1, <4>2
    <3> QED
      BY <3>1, <3>2
  <2> QED
    BY <1>0, <2>4 DEF Sealed
<1>7. ASSUME NEW x \in Slots, Reclaim(x) PROVE Sealed'
  <2>1. slot' = [slot EXCEPT ![x] = Free]
    BY <1>7 DEF Reclaim
  <2>2. /\ slot'[x].mark = "none"
        /\ \A y \in Slots : y # x => slot'[y] = slot[y]
    BY <1>a, <2>1, FreeFacts DEF TypeOK
  <2>4. MarkedSealed' /\ BeforeZero'
    BY <1>0, <2>2 DEF MarkedSealed, BeforeZero
  <2> QED
    BY <1>0, <2>4 DEF Sealed
<1> QED
  <2>1. ASSUME Revoke PROVE UNCHANGED slot
    BY <2>1 DEF Revoke
  <2>2. ASSUME NEW n \in 1..MaxCount, RefuseBound(n) PROVE UNCHANGED slot
    BY <2>2 DEF RefuseBound
  <2>3. ASSUME NEW g \in Governors, NEW n \in 1..MaxCount, RefuseGov(g, n) PROVE UNCHANGED slot
    BY <2>3 DEF RefuseGov
  <2>4. ASSUME UNCHANGED vars PROVE UNCHANGED slot
    BY <2>4 DEF vars
  <2> QED
    BY <1>1, <1>2, <1>3, <1>4, <1>5, <1>6, <1>7, <2>1, <2>2, <2>3, <2>4 DEF Next

InvS == Sealed /\ ~spent

LEMMA NextSpent ==
  ASSUME Mut # "M_EARLYRELEASE", InvS, [Next]_vars
  PROVE  InvS'
<1>0. Sealed /\ Sealed' /\ ~spent
  BY NextSealed DEF InvS
<1>1. ~spent'
  <2>1. CASE \E x \in Slots : Effect(x)
    <3>1. PICK x \in Slots : Effect(x)
      BY <2>1
    <3>2. slot[x].st = "live" /\ spent' = (spent \/ slot[x].mark # "none")
      BY <3>1 DEF Effect
    <3>3. slot[x].mark = "none"
      BY <1>0, <3>2 DEF Sealed, MarkedSealed
    <3> QED
      BY <1>0, <3>2, <3>3
  <2>2. CASE ~\E x \in Slots : Effect(x)
    <3>1. UNCHANGED spent
      BY <2>2 DEF Next, vars, Grant, Seal, Mark, HearP, HearG, HearWord, Reclaim, Revoke, RefuseBound, RefuseGov
    <3> QED
      BY <1>0, <3>1
  <2> QED
    BY <2>1, <2>2
<1> QED
  BY <1>0, <1>1 DEF InvS

THEOREM SealedIsSpentAlways ==
  ASSUME Mut # "M_EARLYRELEASE"
  PROVE  Spec => []SealedIsSpent
<1>1. InvS /\ [Next]_vars => InvS'
  BY NextSpent
<1>2. Init => InvS
  BY InitSealed DEF Init, InvS
<1>3. InvS => SealedIsSpent
  BY DEF InvS, SealedIsSpent
<1> QED
  BY <1>1, <1>2, <1>3, PTL DEF Spec
-----------------------------------------------------------------------------
(* The plane's account: EffCharge never reaches KUp, and it bounds the effects. *)

LEMMA InitH == Init => InvH
<1> SUFFICES ASSUME Init PROVE InvH OBVIOUS
<1>1. Sealed
  BY InitSealed
<1>2. PUnmarked /\ PStopAfter
  BY FreeFacts DEF Init, PUnmarked, PStopAfter
<1>3. HonestBound
  <2>1. CA("l1") = 0 /\ CA("l2") = 0 /\ CA("l3") = 0
    BY FreeFacts, SlotsMembers DEF Init, CA
  <2> QED
    BY <2>1, KUpPositive DEF HonestBound, EffCharge
<1> QED
  BY <1>1, <1>2, <1>3 DEF InvH

LEMMA NextH ==
  ASSUME Mut # "M_NOCHARGE", Mut # "M_ATMOST", Mut # "M_EARLYRELEASE", Mut # "M_NOSTOP", InvH, [Next]_vars
  PROVE  InvH'
<1>0. Sealed /\ Sealed' /\ PUnmarked /\ PStopAfter /\ HonestBound
  BY NextSealed DEF InvH
<1>a. TypeOK /\ TypeOK' /\ ShapeS
  BY <1>0 DEF Sealed, Shape
<1>k. KUp \in Nat
  BY KUpPositive
<1>c. \A y \in Slots : /\ slot[y].count \in Nat /\ slot[y] \in SlotRec
  BY <1>a DEF TypeOK, SlotRec
<1>d. \A y \in Slots : CA(y) \in Nat
  BY <1>c DEF CA
<1>e. EffCharge \in Nat
  BY <1>d, SlotsMembers DEF EffCharge
<1>1. CASE UNCHANGED <<slot, pStopped>>
  <2>1. /\ PUnmarked' /\ PStopAfter'
    BY <1>0, <1>1 DEF PUnmarked, PStopAfter
  <2>2. HonestBound'
    BY <1>0, <1>1 DEF HonestBound, EffCharge, CA
  <2> QED
    BY <1>0, <2>1, <2>2 DEF InvH
<1>2. ASSUME NEW x \in Slots, NEW g \in Governors, NEW n \in 1..MaxCount, NEW k \in Kinds, Grant(x, g, n, k)
      PROVE InvH'
  <2>1. /\ n \in Nat /\ n >= 1
        /\ slot[x].st = "free"
        /\ slot'[x] = Fresh(g, n, k)
        /\ \A y \in Slots : y # x => slot'[y] = slot[y]
        /\ PlaneAllows(n)
        /\ UNCHANGED <<revoked, pStopped>>
    BY <1>a, <1>2, GrantFacts
  <2>2. /\ slot'[x].pc = TRUE /\ slot'[x].mark = "none" /\ slot'[x].st = "live" /\ slot'[x].count = n
    BY <2>1, FreshFacts DEF PlaneCharges
  <2>3. slot[x] = Free
    BY <1>a, <2>1 DEF ShapeS
  <2>4. PUnmarked' /\ PStopAfter'
    <3>1. PUnmarked'
      <4> SUFFICES ASSUME NEW y \in Slots, ~slot'[y].pc, slot'[y].st # "free"
                   PROVE slot'[y].mark # "none"
        BY DEF PUnmarked
      <4>1. y # x
        BY <2>2
      <4> QED
        BY <1>0, <2>1, <4>1 DEF PUnmarked
    <3>2. PStopAfter'
      <4> SUFFICES ASSUME NEW y \in Slots, slot'[y].mark = "after", ~slot'[y].pc
                   PROVE pStopped'
        BY DEF PStopAfter
      <4>1. y # x
        BY <2>2
      <4> QED
        BY <1>0, <2>1, <4>1 DEF PStopAfter
    <3> QED
      BY <3>1, <3>2
  <2>5. HonestBound'
    <3> SUFFICES ASSUME ~PlaneCaptured PROVE EffCharge' < KUp
      BY DEF HonestBound
    <3>1. ~pStopped /\ Charge + n < KUp
      BY <2>1, CapturedBool DEF PlaneAllows, Bound
    <3>2. \A y \in Slots : CA(y) = PC(y)
      <4> SUFFICES ASSUME NEW y \in Slots PROVE CA(y) = PC(y)
        OBVIOUS
      <4>1. slot[y].mark = "after" => slot[y].pc
        BY <1>0, <3>1 DEF PStopAfter
      <4> QED
        BY <4>1 DEF CA, PC
    <3>3. EffCharge = Charge
      BY <3>2, SlotsMembers DEF EffCharge, Charge
    <3>4. CA(x) = 0
      BY <2>3, FreeFacts DEF CA
    <3>5. CA(x)' = n
      BY <2>2 DEF CA
    <3>6. \A y \in Slots : y # x => CA(y)' = CA(y)
      BY <2>1 DEF CA
    <3>7. EffCharge' = EffCharge + n
      <4>1. CASE x = "l1"
        BY <3>4, <3>5, <3>6, <4>1, <1>d, SlotsMembers, <2>1 DEF EffCharge
      <4>2. CASE x = "l2"
        BY <3>4, <3>5, <3>6, <4>2, <1>d, SlotsMembers, <2>1 DEF EffCharge
      <4>3. CASE x = "l3"
        BY <3>4, <3>5, <3>6, <4>3, <1>d, SlotsMembers, <2>1 DEF EffCharge
      <4> QED
        BY <4>1, <4>2, <4>3, SlotsLiteral
    <3> QED
      BY <3>1, <3>3, <3>7, <1>e, <2>1, <1>k
  <2> QED
    BY <1>0, <2>4, <2>5 DEF InvH
<1>3. ASSUME NEW x \in Slots, Effect(x) \/ Seal(x)
      PROVE InvH'
  <2>1. /\ slot[x] \in SlotRec
        /\ slot' = [slot EXCEPT ![x].used = @ + 1, ![x].after = @ + (IF revoked THEN 1 ELSE 0)]
           \/ slot' = [slot EXCEPT ![x].st = "sealed"]
        /\ pStopped' = pStopped
        /\ slot[x].st = "live"
    BY <1>a, <1>3 DEF TypeOK, Effect, Seal
  <2>2. /\ slot'[x].pc = slot[x].pc /\ slot'[x].mark = slot[x].mark /\ slot'[x].count = slot[x].count
        /\ slot'[x].st # "free"
        /\ \A y \in Slots : y # x => slot'[y] = slot[y]
    BY <1>a, <2>1 DEF TypeOK, SlotRec
  <2>3. PUnmarked' /\ PStopAfter'
    <3>1. PUnmarked'
      <4> SUFFICES ASSUME NEW y \in Slots, ~slot'[y].pc, slot'[y].st # "free"
                   PROVE slot'[y].mark # "none"
        BY DEF PUnmarked
      <4>1. CASE y = x
        BY <1>0, <2>1, <2>2, <4>1 DEF PUnmarked
      <4>2. CASE y # x
        BY <1>0, <2>2, <4>2 DEF PUnmarked
      <4> QED
        BY <4>1, <4>2
    <3>2. PStopAfter'
      <4> SUFFICES ASSUME NEW y \in Slots, slot'[y].mark = "after", ~slot'[y].pc
                   PROVE pStopped'
        BY DEF PStopAfter
      <4>1. CASE y = x
        BY <1>0, <2>1, <2>2, <4>1 DEF PStopAfter
      <4>2. CASE y # x
        BY <1>0, <2>1, <2>2, <4>2 DEF PStopAfter
      <4> QED
        BY <4>1, <4>2
    <3> QED
      BY <3>1, <3>2
  <2>4. HonestBound'
    <3>1. \A y \in Slots : CA(y)' = CA(y)
      <4> SUFFICES ASSUME NEW y \in Slots PROVE CA(y)' = CA(y)
        OBVIOUS
      <4>1. CASE y = x
        BY <2>2, <4>1 DEF CA
      <4>2. CASE y # x
        BY <2>2, <4>2 DEF CA
      <4> QED
        BY <4>1, <4>2
    <3> QED
      BY <1>0, <3>1, SlotsMembers DEF HonestBound, EffCharge
  <2> QED
    BY <1>0, <2>3, <2>4 DEF InvH
<1>4. ASSUME NEW x \in Slots, Mark(x) PROVE InvH'
  <2>1. /\ slot[x].st = "sealed" /\ slot[x].mark = "none"
        /\ slot' = [slot EXCEPT ![x].mark = IF revoked THEN "after" ELSE "before", ![x].read = slot[x].used]
        /\ pStopped' = pStopped
    BY <1>4 DEF Mark, Markable
  <2>2. slot[x] \in SlotRec /\ slot[x].pc
    BY <1>0, <1>a, <2>1 DEF TypeOK, PUnmarked
  <2>3. /\ slot'[x].pc = TRUE /\ slot'[x].count = slot[x].count /\ slot'[x].st = "sealed"
        /\ slot'[x].mark # "none"
        /\ \A y \in Slots : y # x => slot'[y] = slot[y]
    BY <1>a, <2>1, <2>2 DEF TypeOK, SlotRec
  <2>4. PUnmarked' /\ PStopAfter'
    <3>1. PUnmarked'
      <4> SUFFICES ASSUME NEW y \in Slots, ~slot'[y].pc, slot'[y].st # "free"
                   PROVE slot'[y].mark # "none"
        BY DEF PUnmarked
      <4>1. y # x
        BY <2>3
      <4> QED
        BY <1>0, <2>3, <4>1 DEF PUnmarked
    <3>2. PStopAfter'
      <4> SUFFICES ASSUME NEW y \in Slots, slot'[y].mark = "after", ~slot'[y].pc
                   PROVE pStopped'
        BY DEF PStopAfter
      <4>1. y # x
        BY <2>3
      <4> QED
        BY <1>0, <2>1, <2>3, <4>1 DEF PStopAfter
    <3> QED
      BY <3>1, <3>2
  <2>5. HonestBound'
    <3>1. \A y \in Slots : CA(y)' = CA(y)
      <4> SUFFICES ASSUME NEW y \in Slots PROVE CA(y)' = CA(y)
        OBVIOUS
      <4>1. CASE y = x
        BY <2>2, <2>3, <4>1 DEF CA
      <4>2. CASE y # x
        BY <2>3, <4>2 DEF CA
      <4> QED
        BY <4>1, <4>2
    <3> QED
      BY <1>0, <3>1, SlotsMembers DEF HonestBound, EffCharge
  <2> QED
    BY <1>0, <2>4, <2>5 DEF InvH
<1>5. ASSUME NEW x \in Slots, HearP(x) PROVE InvH'
  <2>1. /\ slot[x].mark # "none" /\ slot[x].pc
        /\ slot' = [slot EXCEPT ![x].pc = FALSE]
        /\ pStopped' = (pStopped \/ (slot[x].mark = "after" /\ Stops))
    BY <1>5 DEF HearP
  <2>2. slot[x] \in SlotRec
    BY <1>a DEF TypeOK
  <2>3. /\ slot'[x].pc = FALSE /\ slot'[x].mark = slot[x].mark /\ slot'[x].count = slot[x].count
        /\ slot'[x].st = slot[x].st
        /\ \A y \in Slots : y # x => slot'[y] = slot[y]
    BY <1>a, <2>1, <2>2 DEF TypeOK, SlotRec
  <2>4. pStopped => pStopped'
    BY <2>1
  <2>5. PUnmarked' /\ PStopAfter'
    <3>1. PUnmarked'
      <4> SUFFICES ASSUME NEW y \in Slots, ~slot'[y].pc, slot'[y].st # "free"
                   PROVE slot'[y].mark # "none"
        BY DEF PUnmarked
      <4>1. CASE y = x
        BY <2>1, <2>3, <4>1
      <4>2. CASE y # x
        BY <1>0, <2>3, <4>2 DEF PUnmarked
      <4> QED
        BY <4>1, <4>2
    <3>2. PStopAfter'
      <4> SUFFICES ASSUME NEW y \in Slots, slot'[y].mark = "after", ~slot'[y].pc
                   PROVE pStopped'
        BY DEF PStopAfter
      <4>1. CASE y = x
        BY <2>1, <2>3, <4>1 DEF Stops
      <4>2. CASE y # x
        BY <1>0, <2>3, <2>4, <4>2 DEF PStopAfter
      <4> QED
        BY <4>1, <4>2
    <3> QED
      BY <3>1, <3>2
  <2>6. HonestBound'
    <3> SUFFICES ASSUME ~PlaneCaptured PROVE EffCharge' < KUp
      BY DEF HonestBound
    <3>1. EffCharge < KUp
      BY <1>0 DEF HonestBound
    <3>2. \A y \in Slots : CA(y)' <= CA(y) /\ CA(y)' \in Nat
      <4> SUFFICES ASSUME NEW y \in Slots PROVE CA(y)' <= CA(y) /\ CA(y)' \in Nat
        OBVIOUS
      <4>0. slot[y].count \in Nat
        BY <1>c
      <4>1. CASE y = x
        BY <2>3, <4>0, <4>1 DEF CA
      <4>2. CASE y # x
        BY <2>3, <4>0, <4>2 DEF CA
      <4> QED
        BY <4>1, <4>2
    <3> QED
      BY <1>d, <1>k, <3>1, <3>2, SlotsMembers DEF EffCharge
  <2> QED
    BY <1>0, <2>5, <2>6 DEF InvH
<1>6. ASSUME NEW x \in Slots, HearG(x) \/ HearWord(x) PROVE InvH'
  <2>1. /\ slot' = [slot EXCEPT ![x].gc = FALSE]
        /\ pStopped' = pStopped
    BY <1>6 DEF HearG, HearWord
  <2>2. slot[x] \in SlotRec
    BY <1>a DEF TypeOK
  <2>3. /\ slot'[x].pc = slot[x].pc /\ slot'[x].mark = slot[x].mark /\ slot'[x].count = slot[x].count
        /\ slot'[x].st = slot[x].st
        /\ \A y \in Slots : y # x => slot'[y] = slot[y]
    BY <1>a, <2>1, <2>2 DEF TypeOK, SlotRec
  <2>4. PUnmarked' /\ PStopAfter'
    <3>1. PUnmarked'
      <4> SUFFICES ASSUME NEW y \in Slots, ~slot'[y].pc, slot'[y].st # "free"
                   PROVE slot'[y].mark # "none"
        BY DEF PUnmarked
      <4>1. CASE y = x
        BY <1>0, <2>3, <4>1 DEF PUnmarked
      <4>2. CASE y # x
        BY <1>0, <2>3, <4>2 DEF PUnmarked
      <4> QED
        BY <4>1, <4>2
    <3>2. PStopAfter'
      <4> SUFFICES ASSUME NEW y \in Slots, slot'[y].mark = "after", ~slot'[y].pc
                   PROVE pStopped'
        BY DEF PStopAfter
      <4>1. CASE y = x
        BY <1>0, <2>1, <2>3, <4>1 DEF PStopAfter
      <4>2. CASE y # x
        BY <1>0, <2>1, <2>3, <4>2 DEF PStopAfter
      <4> QED
        BY <4>1, <4>2
    <3> QED
      BY <3>1, <3>2
  <2>5. HonestBound'
    <3>1. \A y \in Slots : CA(y)' = CA(y)
      <4> SUFFICES ASSUME NEW y \in Slots PROVE CA(y)' = CA(y)
        OBVIOUS
      <4>1. CASE y = x
        BY <2>3, <4>1 DEF CA
      <4>2. CASE y # x
        BY <2>3, <4>2 DEF CA
      <4> QED
        BY <4>1, <4>2
    <3> QED
      BY <1>0, <3>1, SlotsMembers DEF HonestBound, EffCharge
  <2> QED
    BY <1>0, <2>4, <2>5 DEF InvH
<1>7. ASSUME NEW x \in Slots, Reclaim(x) PROVE InvH'
  <2>1. /\ slot' = [slot EXCEPT ![x] = Free]
        /\ pStopped' = pStopped
    BY <1>7 DEF Reclaim
  <2>2. /\ slot'[x] = Free
        /\ \A y \in Slots : y # x => slot'[y] = slot[y]
    BY <1>a, <2>1 DEF TypeOK
  <2>3. PUnmarked' /\ PStopAfter'
    <3>1. PUnmarked'
      <4> SUFFICES ASSUME NEW y \in Slots, ~slot'[y].pc, slot'[y].st # "free"
                   PROVE slot'[y].mark # "none"
        BY DEF PUnmarked
      <4>1. y # x
        BY <2>2, FreeFacts
      <4> QED
        BY <1>0, <2>2, <4>1 DEF PUnmarked
    <3>2. PStopAfter'
      <4> SUFFICES ASSUME NEW y \in Slots, slot'[y].mark = "after", ~slot'[y].pc
                   PROVE pStopped'
        BY DEF PStopAfter
      <4>1. y # x
        BY <2>2, FreeFacts
      <4> QED
        BY <1>0, <2>1, <2>2, <4>1 DEF PStopAfter
    <3> QED
      BY <3>1, <3>2
  <2>4. HonestBound'
    <3> SUFFICES ASSUME ~PlaneCaptured PROVE EffCharge' < KUp
      BY DEF HonestBound
    <3>1. EffCharge < KUp
      BY <1>0 DEF HonestBound
    <3>2. \A y \in Slots : CA(y)' <= CA(y) /\ CA(y)' \in Nat
      <4> SUFFICES ASSUME NEW y \in Slots PROVE CA(y)' <= CA(y) /\ CA(y)' \in Nat
        OBVIOUS
      <4>0. slot[y].count \in Nat
        BY <1>c
      <4>1. CASE y = x
        BY <2>2, <4>0, <4>1, FreeFacts DEF CA
      <4>2. CASE y # x
        BY <2>2, <4>0, <4>2 DEF CA
      <4> QED
        BY <4>1, <4>2
    <3> QED
      BY <1>d, <1>k, <3>1, <3>2, SlotsMembers DEF EffCharge
  <2> QED
    BY <1>0, <2>3, <2>4 DEF InvH
<1> QED
  <2>1. ASSUME Revoke PROVE UNCHANGED <<slot, pStopped>>
    BY <2>1 DEF Revoke
  <2>2. ASSUME NEW n \in 1..MaxCount, RefuseBound(n) PROVE UNCHANGED <<slot, pStopped>>
    BY <2>2 DEF RefuseBound
  <2>3. ASSUME NEW g \in Governors, NEW n \in 1..MaxCount, RefuseGov(g, n) PROVE UNCHANGED <<slot, pStopped>>
    BY <2>3 DEF RefuseGov
  <2>4. ASSUME UNCHANGED vars PROVE UNCHANGED <<slot, pStopped>>
    BY <2>4 DEF vars
  <2> QED
    BY <1>1, <1>2, <1>3, <1>4, <1>5, <1>6, <1>7, <2>1, <2>2, <2>3, <2>4 DEF Next

LEMMA HBounds ==
  ASSUME InvH, ~PlaneCaptured PROVE TotalAfter < KUp
<1>0. TypeOK /\ ShapeS /\ BeforeZero /\ PUnmarked /\ HonestBound
  BY DEF InvH, Sealed, Shape
<1>1. \A y \in Slots : slot[y].after <= CA(y) /\ slot[y].after \in Nat /\ CA(y) \in Nat
  <2> SUFFICES ASSUME NEW y \in Slots
               PROVE slot[y].after <= CA(y) /\ slot[y].after \in Nat /\ CA(y) \in Nat
    OBVIOUS
  <2>0. /\ slot[y] \in SlotRec /\ slot[y].after \in Nat /\ slot[y].used \in Nat /\ slot[y].count \in Nat
        /\ slot[y].used <= slot[y].count /\ slot[y].after <= slot[y].used
    BY <1>0 DEF TypeOK, SlotRec, ShapeS
  <2>1. CASE slot[y].pc \/ slot[y].mark = "after"
    BY <2>0, <2>1 DEF CA
  <2>2. CASE ~(slot[y].pc \/ slot[y].mark = "after")
    <3>1. CA(y) = 0
      BY <2>2 DEF CA
    <3>2. CASE slot[y].st = "free"
      BY <1>0, <3>1, <3>2, FreeFacts DEF ShapeS
    <3>3. CASE slot[y].st # "free"
      <4>1. slot[y].mark # "none"
        BY <1>0, <2>2, <3>3 DEF PUnmarked
      <4>2. slot[y].mark = "before"
        BY <2>0, <2>2, <4>1 DEF SlotRec
      <4> QED
        BY <1>0, <3>1, <4>2 DEF BeforeZero
    <3> QED
      BY <3>2, <3>3
  <2> QED
    BY <2>1, <2>2
<1>2. EffCharge < KUp
  BY <1>0 DEF HonestBound
<1>3. KUp \in Nat
  BY KUpPositive
<1> QED
  BY <1>1, <1>2, <1>3, SlotsMembers DEF TotalAfter, EffCharge

THEOREM EffectsAfterHonestAlways ==
  ASSUME Mut # "M_NOCHARGE", Mut # "M_ATMOST", Mut # "M_EARLYRELEASE", Mut # "M_NOSTOP"
  PROVE  Spec => []EffectsAfterHonest
<1>1. InvH /\ [Next]_vars => InvH'
  BY NextH
<1>2. InvH => EffectsAfterHonest
  BY HBounds DEF EffectsAfterHonest
<1> QED
  BY InitH, <1>1, <1>2, PTL DEF Spec
-----------------------------------------------------------------------------
(* The governor's account: the same two steps, for each honest governor.       *)

LEMMA InitG == Init => InvG
<1> SUFFICES ASSUME Init PROVE InvG OBVIOUS
<1>1. Sealed
  BY InitSealed
<1>2. GUnmarked /\ GStopAfter
  BY FreeFacts DEF Init, GUnmarked, GStopAfter
<1>3. PerGovBound
  <2> SUFFICES ASSUME NEW h \in Governors PROVE GovEffCharge(h) < KUp
    BY DEF PerGovBound
  <2>1. CG(h, "l1") = 0 /\ CG(h, "l2") = 0 /\ CG(h, "l3") = 0
    BY FreeFacts, SlotsMembers DEF Init, CG
  <2> QED
    BY <2>1, KUpPositive DEF GovEffCharge
<1> QED
  BY <1>1, <1>2, <1>3 DEF InvG

LEMMA NextG ==
  ASSUME Mut # "M_ATMOST", Mut # "M_EARLYRELEASE", Mut # "M_NOSTOP", Mut # "M_TRUSTMARK", Mut # "M_ORDEREDFREE",
         InvG, [Next]_vars
  PROVE  InvG'
<1>0. Sealed /\ Sealed' /\ GUnmarked /\ GStopAfter /\ PerGovBound
  BY NextSealed DEF InvG
<1>a. TypeOK /\ TypeOK' /\ ShapeS
  BY <1>0 DEF Sealed, Shape
<1>k. KUp \in Nat
  BY KUpPositive
<1>c. \A y \in Slots : /\ slot[y].count \in Nat /\ slot[y] \in SlotRec
  BY <1>a DEF TypeOK, SlotRec
<1>d. \A h \in Governors, y \in Slots : CG(h, y) \in Nat
  BY <1>c DEF CG
<1>g. \A y \in Slots : slot[y].mark = "after" => slot[y].gov \in Governors
  BY <1>a, FreeFacts DEF ShapeS
<1>1. CASE UNCHANGED <<slot, gStopped>>
  <2>1. GUnmarked' /\ GStopAfter'
    BY <1>0, <1>1 DEF GUnmarked, GStopAfter
  <2>2. PerGovBound'
    BY <1>0, <1>1 DEF PerGovBound, GovEffCharge, CG
  <2> QED
    BY <1>0, <2>1, <2>2 DEF InvG
<1>2. ASSUME NEW x \in Slots, NEW g0 \in Governors, NEW n \in 1..MaxCount, NEW k \in Kinds, Grant(x, g0, n, k)
      PROVE InvG'
  <2>1. /\ n \in Nat /\ n >= 1
        /\ slot[x].st = "free"
        /\ slot'[x] = Fresh(g0, n, k)
        /\ \A y \in Slots : y # x => slot'[y] = slot[y]
        /\ GovAllows(g0, n, k)
        /\ UNCHANGED gStopped
    BY <1>a, <1>2, GrantFacts
  <2>2. /\ slot'[x].gc = TRUE /\ slot'[x].mark = "none" /\ slot'[x].st = "live"
        /\ slot'[x].count = n /\ slot'[x].gov = g0
    BY <2>1, FreshFacts DEF GovCounts
  <2>3. slot[x] = Free
    BY <1>a, <2>1 DEF ShapeS
  <2>4. GUnmarked' /\ GStopAfter'
    <3>1. GUnmarked'
      <4> SUFFICES ASSUME NEW y \in Slots, ~slot'[y].gc, slot'[y].st # "free"
                   PROVE slot'[y].mark # "none"
        BY DEF GUnmarked
      <4>1. y # x
        BY <2>2
      <4> QED
        BY <1>0, <2>1, <4>1 DEF GUnmarked
    <3>2. GStopAfter'
      <4> SUFFICES ASSUME NEW y \in Slots, slot'[y].mark = "after", ~slot'[y].gc
                   PROVE gStopped'[slot'[y].gov]
        BY DEF GStopAfter
      <4>1. y # x
        BY <2>2
      <4> QED
        BY <1>0, <2>1, <4>1 DEF GStopAfter
    <3> QED
      BY <3>1, <3>2
  <2>5. PerGovBound'
    <3> SUFFICES ASSUME NEW h \in Governors PROVE GovEffCharge(h)' < KUp
      BY DEF PerGovBound
    <3>0. CG(h, x) = 0
      BY <2>3, FreeFacts DEF CG
    <3>a. GovEffCharge(h) \in Nat /\ GovEffCharge(h) < KUp
      BY <1>0, <1>d, SlotsMembers DEF PerGovBound, GovEffCharge
    <3>b. \A y \in Slots : y # x => CG(h, y)' = CG(h, y)
      BY <2>1 DEF CG
    <3>1. CASE h = g0
      <4>1. ~gStopped[g0] /\ Acct(g0) + n < KUp
        BY <2>1 DEF GovAllows, GovCounts, Bound
      <4>2. \A y \in Slots : CG(g0, y) = GC(g0, y)
        <5> SUFFICES ASSUME NEW y \in Slots PROVE CG(g0, y) = GC(g0, y)
          OBVIOUS
        <5>1. (slot[y].gov = g0 /\ slot[y].mark = "after") => slot[y].gc
          BY <1>0, <4>1 DEF GStopAfter
        <5> QED
          BY <5>1 DEF CG, GC
      <4>3. GovEffCharge(g0) = Acct(g0)
        BY <4>2, SlotsMembers DEF GovEffCharge, Acct
      <4>4. CG(g0, x)' = n
        BY <2>2 DEF CG
      <4>5. GovEffCharge(g0)' = GovEffCharge(g0) + n
        <5>1. CASE x = "l1"
          BY <3>0, <3>1, <3>b, <4>4, <5>1, <1>d, SlotsMembers, <2>1 DEF GovEffCharge
        <5>2. CASE x = "l2"
          BY <3>0, <3>1, <3>b, <4>4, <5>2, <1>d, SlotsMembers, <2>1 DEF GovEffCharge
        <5>3. CASE x = "l3"
          BY <3>0, <3>1, <3>b, <4>4, <5>3, <1>d, SlotsMembers, <2>1 DEF GovEffCharge
        <5> QED
          BY <5>1, <5>2, <5>3, SlotsLiteral
      <4> QED
        BY <3>1, <3>a, <4>1, <4>3, <4>5, <2>1, <1>k
    <3>2. CASE h # g0
      <4>1. CG(h, x)' = 0
        BY <2>2, <3>2 DEF CG
      <4>2. \A y \in Slots : CG(h, y)' = CG(h, y)
        BY <3>0, <3>b, <4>1
      <4> QED
        BY <3>a, <4>2, SlotsMembers DEF GovEffCharge
    <3> QED
      BY <3>1, <3>2
  <2> QED
    BY <1>0, <2>4, <2>5 DEF InvG
<1>3. ASSUME NEW x \in Slots, Effect(x) \/ Seal(x)
      PROVE InvG'
  <2>1. /\ slot[x] \in SlotRec
        /\ slot' = [slot EXCEPT ![x].used = @ + 1, ![x].after = @ + (IF revoked THEN 1 ELSE 0)]
           \/ slot' = [slot EXCEPT ![x].st = "sealed"]
        /\ gStopped' = gStopped
        /\ slot[x].st = "live"
    BY <1>a, <1>3 DEF TypeOK, Effect, Seal
  <2>2. /\ slot'[x].gc = slot[x].gc /\ slot'[x].mark = slot[x].mark /\ slot'[x].count = slot[x].count
        /\ slot'[x].gov = slot[x].gov /\ slot'[x].st # "free"
        /\ \A y \in Slots : y # x => slot'[y] = slot[y]
    BY <1>a, <2>1 DEF TypeOK, SlotRec
  <2>3. GUnmarked' /\ GStopAfter'
    <3>1. GUnmarked'
      <4> SUFFICES ASSUME NEW y \in Slots, ~slot'[y].gc, slot'[y].st # "free"
                   PROVE slot'[y].mark # "none"
        BY DEF GUnmarked
      <4>1. CASE y = x
        BY <1>0, <2>1, <2>2, <4>1 DEF GUnmarked
      <4>2. CASE y # x
        BY <1>0, <2>2, <4>2 DEF GUnmarked
      <4> QED
        BY <4>1, <4>2
    <3>2. GStopAfter'
      <4> SUFFICES ASSUME NEW y \in Slots, slot'[y].mark = "after", ~slot'[y].gc
                   PROVE gStopped'[slot'[y].gov]
        BY DEF GStopAfter
      <4>1. CASE y = x
        BY <1>0, <2>1, <2>2, <4>1 DEF GStopAfter
      <4>2. CASE y # x
        BY <1>0, <2>1, <2>2, <4>2 DEF GStopAfter
      <4> QED
        BY <4>1, <4>2
    <3> QED
      BY <3>1, <3>2
  <2>4. PerGovBound'
    <3> SUFFICES ASSUME NEW h \in Governors PROVE GovEffCharge(h)' < KUp
      BY DEF PerGovBound
    <3>1. \A y \in Slots : CG(h, y)' = CG(h, y)
      <4> SUFFICES ASSUME NEW y \in Slots PROVE CG(h, y)' = CG(h, y)
        OBVIOUS
      <4>1. CASE y = x
        BY <2>2, <4>1 DEF CG
      <4>2. CASE y # x
        BY <2>2, <4>2 DEF CG
      <4> QED
        BY <4>1, <4>2
    <3> QED
      BY <1>0, <3>1, SlotsMembers DEF PerGovBound, GovEffCharge
  <2> QED
    BY <1>0, <2>3, <2>4 DEF InvG
<1>4. ASSUME NEW x \in Slots, Mark(x) PROVE InvG'
  <2>1. /\ slot[x].st = "sealed" /\ slot[x].mark = "none"
        /\ slot' = [slot EXCEPT ![x].mark = IF revoked THEN "after" ELSE "before", ![x].read = slot[x].used]
        /\ gStopped' = gStopped
    BY <1>4 DEF Mark, Markable
  <2>2. slot[x] \in SlotRec /\ slot[x].gc
    BY <1>0, <1>a, <2>1 DEF TypeOK, GUnmarked
  <2>3. /\ slot'[x].gc = TRUE /\ slot'[x].count = slot[x].count /\ slot'[x].st = "sealed"
        /\ slot'[x].gov = slot[x].gov /\ slot'[x].mark # "none"
        /\ \A y \in Slots : y # x => slot'[y] = slot[y]
    BY <1>a, <2>1, <2>2 DEF TypeOK, SlotRec
  <2>4. GUnmarked' /\ GStopAfter'
    <3>1. GUnmarked'
      <4> SUFFICES ASSUME NEW y \in Slots, ~slot'[y].gc, slot'[y].st # "free"
                   PROVE slot'[y].mark # "none"
        BY DEF GUnmarked
      <4>1. y # x
        BY <2>3
      <4> QED
        BY <1>0, <2>3, <4>1 DEF GUnmarked
    <3>2. GStopAfter'
      <4> SUFFICES ASSUME NEW y \in Slots, slot'[y].mark = "after", ~slot'[y].gc
                   PROVE gStopped'[slot'[y].gov]
        BY DEF GStopAfter
      <4>1. y # x
        BY <2>3
      <4> QED
        BY <1>0, <2>1, <2>3, <4>1 DEF GStopAfter
    <3> QED
      BY <3>1, <3>2
  <2>5. PerGovBound'
    <3> SUFFICES ASSUME NEW h \in Governors PROVE GovEffCharge(h)' < KUp
      BY DEF PerGovBound
    <3>1. \A y \in Slots : CG(h, y)' = CG(h, y)
      <4> SUFFICES ASSUME NEW y \in Slots PROVE CG(h, y)' = CG(h, y)
        OBVIOUS
      <4>1. CASE y = x
        BY <2>2, <2>3, <4>1 DEF CG
      <4>2. CASE y # x
        BY <2>3, <4>2 DEF CG
      <4> QED
        BY <4>1, <4>2
    <3> QED
      BY <1>0, <3>1, SlotsMembers DEF PerGovBound, GovEffCharge
  <2> QED
    BY <1>0, <2>4, <2>5 DEF InvG
<1>5. ASSUME NEW x \in Slots, HearP(x) PROVE InvG'
  <2>1. /\ slot' = [slot EXCEPT ![x].pc = FALSE]
        /\ gStopped' = gStopped
    BY <1>5 DEF HearP
  <2>2. slot[x] \in SlotRec
    BY <1>a DEF TypeOK
  <2>3. /\ slot'[x].gc = slot[x].gc /\ slot'[x].mark = slot[x].mark /\ slot'[x].count = slot[x].count
        /\ slot'[x].gov = slot[x].gov /\ slot'[x].st = slot[x].st
        /\ \A y \in Slots : y # x => slot'[y] = slot[y]
    BY <1>a, <2>1, <2>2 DEF TypeOK, SlotRec
  <2>4. GUnmarked' /\ GStopAfter'
    <3>1. GUnmarked'
      <4> SUFFICES ASSUME NEW y \in Slots, ~slot'[y].gc, slot'[y].st # "free"
                   PROVE slot'[y].mark # "none"
        BY DEF GUnmarked
      <4>1. CASE y = x
        BY <1>0, <2>3, <4>1 DEF GUnmarked
      <4>2. CASE y # x
        BY <1>0, <2>3, <4>2 DEF GUnmarked
      <4> QED
        BY <4>1, <4>2
    <3>2. GStopAfter'
      <4> SUFFICES ASSUME NEW y \in Slots, slot'[y].mark = "after", ~slot'[y].gc
                   PROVE gStopped'[slot'[y].gov]
        BY DEF GStopAfter
      <4>1. CASE y = x
        BY <1>0, <2>1, <2>3, <4>1 DEF GStopAfter
      <4>2. CASE y # x
        BY <1>0, <2>1, <2>3, <4>2 DEF GStopAfter
      <4> QED
        BY <4>1, <4>2
    <3> QED
      BY <3>1, <3>2
  <2>5. PerGovBound'
    <3> SUFFICES ASSUME NEW h \in Governors PROVE GovEffCharge(h)' < KUp
      BY DEF PerGovBound
    <3>1. \A y \in Slots : CG(h, y)' = CG(h, y)
      <4> SUFFICES ASSUME NEW y \in Slots PROVE CG(h, y)' = CG(h, y)
        OBVIOUS
      <4>1. CASE y = x
        BY <2>3, <4>1 DEF CG
      <4>2. CASE y # x
        BY <2>3, <4>2 DEF CG
      <4> QED
        BY <4>1, <4>2
    <3> QED
      BY <1>0, <3>1, SlotsMembers DEF PerGovBound, GovEffCharge
  <2> QED
    BY <1>0, <2>4, <2>5 DEF InvG
<1>6. ASSUME NEW x \in Slots, HearG(x) PROVE InvG'
  <2>1. /\ slot[x].mark # "none" /\ slot[x].gc
        /\ slot' = [slot EXCEPT ![x].gc = FALSE]
        /\ gStopped' = [gStopped EXCEPT ![slot[x].gov] = @ \/ (slot[x].mark = "after" /\ Stops)]
    BY <1>6 DEF HearG
  <2>2. slot[x] \in SlotRec /\ slot[x].st # "free" /\ slot[x].gov \in Governors
    BY <1>a, <2>1, FreeFacts DEF TypeOK, ShapeS
  <2>3. /\ slot'[x].gc = FALSE /\ slot'[x].mark = slot[x].mark /\ slot'[x].count = slot[x].count
        /\ slot'[x].gov = slot[x].gov /\ slot'[x].st = slot[x].st
        /\ \A y \in Slots : y # x => slot'[y] = slot[y]
    BY <1>a, <2>1, <2>2 DEF TypeOK, SlotRec
  <2>4. \A h \in Governors : gStopped[h] => gStopped'[h]
    BY <1>a, <2>1, <2>2 DEF TypeOK
  <2>5. slot[x].mark = "after" => gStopped'[slot[x].gov]
    BY <1>a, <2>1, <2>2 DEF TypeOK, Stops
  <2>6. GUnmarked' /\ GStopAfter'
    <3>1. GUnmarked'
      <4> SUFFICES ASSUME NEW y \in Slots, ~slot'[y].gc, slot'[y].st # "free"
                   PROVE slot'[y].mark # "none"
        BY DEF GUnmarked
      <4>1. CASE y = x
        BY <2>1, <2>3, <4>1
      <4>2. CASE y # x
        BY <1>0, <2>3, <4>2 DEF GUnmarked
      <4> QED
        BY <4>1, <4>2
    <3>2. GStopAfter'
      <4> SUFFICES ASSUME NEW y \in Slots, slot'[y].mark = "after", ~slot'[y].gc
                   PROVE gStopped'[slot'[y].gov]
        BY DEF GStopAfter
      <4>1. CASE y = x
        BY <2>3, <2>5, <4>1
      <4>2. CASE y # x
        <5>1. slot[y].mark = "after" /\ ~slot[y].gc /\ slot'[y].gov = slot[y].gov
          BY <2>3, <4>2
        <5>2. gStopped[slot[y].gov] /\ slot[y].gov \in Governors
          BY <1>0, <1>g, <5>1 DEF GStopAfter
        <5> QED
          BY <2>4, <5>1, <5>2
      <4> QED
        BY <4>1, <4>2
    <3> QED
      BY <3>1, <3>2
  <2>7. PerGovBound'
    <3> SUFFICES ASSUME NEW h \in Governors PROVE GovEffCharge(h)' < KUp
      BY DEF PerGovBound
    <3>1. GovEffCharge(h) < KUp
      BY <1>0 DEF PerGovBound
    <3>2. \A y \in Slots : CG(h, y)' <= CG(h, y) /\ CG(h, y)' \in Nat
      <4> SUFFICES ASSUME NEW y \in Slots PROVE CG(h, y)' <= CG(h, y) /\ CG(h, y)' \in Nat
        OBVIOUS
      <4>0. slot[y].count \in Nat
        BY <1>c
      <4>1. CASE y = x
        BY <2>3, <4>0, <4>1 DEF CG
      <4>2. CASE y # x
        BY <2>3, <4>0, <4>2 DEF CG
      <4> QED
        BY <4>1, <4>2
    <3> QED
      BY <1>d, <1>k, <3>1, <3>2, SlotsMembers DEF GovEffCharge
  <2> QED
    BY <1>0, <2>6, <2>7 DEF InvG
<1>7. ASSUME NEW x \in Slots, Reclaim(x) PROVE InvG'
  <2>1. /\ slot' = [slot EXCEPT ![x] = Free]
        /\ gStopped' = gStopped
    BY <1>7 DEF Reclaim
  <2>2. /\ slot'[x] = Free
        /\ \A y \in Slots : y # x => slot'[y] = slot[y]
    BY <1>a, <2>1 DEF TypeOK
  <2>3. GUnmarked' /\ GStopAfter'
    <3>1. GUnmarked'
      <4> SUFFICES ASSUME NEW y \in Slots, ~slot'[y].gc, slot'[y].st # "free"
                   PROVE slot'[y].mark # "none"
        BY DEF GUnmarked
      <4>1. y # x
        BY <2>2, FreeFacts
      <4> QED
        BY <1>0, <2>2, <4>1 DEF GUnmarked
    <3>2. GStopAfter'
      <4> SUFFICES ASSUME NEW y \in Slots, slot'[y].mark = "after", ~slot'[y].gc
                   PROVE gStopped'[slot'[y].gov]
        BY DEF GStopAfter
      <4>1. y # x
        BY <2>2, FreeFacts
      <4> QED
        BY <1>0, <2>1, <2>2, <4>1 DEF GStopAfter
    <3> QED
      BY <3>1, <3>2
  <2>4. PerGovBound'
    <3> SUFFICES ASSUME NEW h \in Governors PROVE GovEffCharge(h)' < KUp
      BY DEF PerGovBound
    <3>1. GovEffCharge(h) < KUp
      BY <1>0 DEF PerGovBound
    <3>2. \A y \in Slots : CG(h, y)' <= CG(h, y) /\ CG(h, y)' \in Nat
      <4> SUFFICES ASSUME NEW y \in Slots PROVE CG(h, y)' <= CG(h, y) /\ CG(h, y)' \in Nat
        OBVIOUS
      <4>0. slot[y].count \in Nat
        BY <1>c
      <4>1. CASE y = x
        BY <2>2, <4>0, <4>1, FreeFacts DEF CG
      <4>2. CASE y # x
        BY <2>2, <4>0, <4>2 DEF CG
      <4> QED
        BY <4>1, <4>2
    <3> QED
      BY <1>d, <1>k, <3>1, <3>2, SlotsMembers DEF GovEffCharge
  <2> QED
    BY <1>0, <2>3, <2>4 DEF InvG
<1>8. ASSUME NEW x \in Slots, HearWord(x) PROVE InvG'
  BY <1>8 DEF HearWord
<1> QED
  <2>1. ASSUME Revoke PROVE UNCHANGED <<slot, gStopped>>
    BY <2>1 DEF Revoke
  <2>2. ASSUME NEW n \in 1..MaxCount, RefuseBound(n) PROVE UNCHANGED <<slot, gStopped>>
    BY <2>2 DEF RefuseBound
  <2>3. ASSUME NEW g \in Governors, NEW n \in 1..MaxCount, RefuseGov(g, n) PROVE UNCHANGED <<slot, gStopped>>
    BY <2>3 DEF RefuseGov
  <2>4. ASSUME UNCHANGED vars PROVE UNCHANGED <<slot, gStopped>>
    BY <2>4 DEF vars
  <2> QED
    BY <1>1, <1>2, <1>3, <1>4, <1>5, <1>6, <1>7, <1>8, <2>1, <2>2, <2>3, <2>4 DEF Next

LEMMA GBounds == InvG => EffectsAfterPerGovernor
<1> SUFFICES ASSUME InvG, NEW h \in Governors PROVE AfterOf(h) < KUp
  BY DEF EffectsAfterPerGovernor
<1>0. TypeOK /\ ShapeS /\ BeforeZero /\ GUnmarked /\ PerGovBound
  BY DEF InvG, Sealed, Shape
<1>1. \A y \in Slots : AfterAt(h, y) <= CG(h, y) /\ AfterAt(h, y) \in Nat /\ CG(h, y) \in Nat
  <2> SUFFICES ASSUME NEW y \in Slots
               PROVE AfterAt(h, y) <= CG(h, y) /\ AfterAt(h, y) \in Nat /\ CG(h, y) \in Nat
    OBVIOUS
  <2>0. /\ slot[y] \in SlotRec /\ slot[y].after \in Nat /\ slot[y].used \in Nat /\ slot[y].count \in Nat
        /\ slot[y].used <= slot[y].count /\ slot[y].after <= slot[y].used
    BY <1>0 DEF TypeOK, SlotRec, ShapeS
  <2>1. CASE slot[y].gov # h
    BY <2>0, <2>1 DEF AfterAt, CG
  <2>2. CASE slot[y].gov = h /\ (slot[y].gc \/ slot[y].mark = "after")
    BY <2>0, <2>2 DEF AfterAt, CG
  <2>3. CASE slot[y].gov = h /\ ~(slot[y].gc \/ slot[y].mark = "after")
    <3>1. CG(h, y) = 0 /\ AfterAt(h, y) = slot[y].after
      BY <2>3 DEF AfterAt, CG
    <3>2. slot[y].st # "free"
      BY <1>0, <2>3, FreeFacts DEF ShapeS, Governors
    <3>3. slot[y].mark # "none"
      BY <1>0, <2>3, <3>2 DEF GUnmarked
    <3>4. slot[y].mark = "before"
      BY <2>0, <2>3, <3>3 DEF SlotRec
    <3> QED
      BY <1>0, <3>1, <3>4 DEF BeforeZero
  <2> QED
    BY <2>1, <2>2, <2>3
<1>2. GovEffCharge(h) < KUp
  BY <1>0 DEF PerGovBound
<1>3. KUp \in Nat
  BY KUpPositive
<1> QED
  BY <1>1, <1>2, <1>3, SlotsMembers DEF AfterOf, GovEffCharge

THEOREM EffectsAfterPerGovernorAlways ==
  ASSUME Mut # "M_ATMOST", Mut # "M_EARLYRELEASE", Mut # "M_NOSTOP", Mut # "M_TRUSTMARK", Mut # "M_ORDEREDFREE"
  PROVE  Spec => []EffectsAfterPerGovernor
<1>1. InvG /\ [Next]_vars => InvG'
  BY NextG
<1> QED
  BY InitG, <1>1, GBounds, PTL DEF Spec
-----------------------------------------------------------------------------
(* Unread effects: the governor's own account alone, with no stop.             *)

LEMMA InitU == Init => InvU
<1> SUFFICES ASSUME Init PROVE InvU OBVIOUS
<1>1. Sealed
  BY InitSealed
<1>2. GUnmarked
  BY FreeFacts DEF Init, GUnmarked
<1>3. AcctBound
  <2> SUFFICES ASSUME NEW h \in Governors PROVE Acct(h) < KUp
    BY DEF AcctBound
  <2>1. GC(h, "l1") = 0 /\ GC(h, "l2") = 0 /\ GC(h, "l3") = 0
    BY FreeFacts, SlotsMembers DEF Init, GC
  <2> QED
    BY <2>1, KUpPositive DEF Acct
<1> QED
  BY <1>1, <1>2, <1>3 DEF InvU

LEMMA NextU ==
  ASSUME Mut # "M_ATMOST", Mut # "M_EARLYRELEASE", Mut # "M_TRUSTMARK", Mut # "M_ORDEREDFREE", InvU, [Next]_vars
  PROVE  InvU'
<1>0. Sealed /\ Sealed' /\ GUnmarked /\ AcctBound
  BY NextSealed DEF InvU
<1>a. TypeOK /\ TypeOK' /\ ShapeS
  BY <1>0 DEF Sealed, Shape
<1>k. KUp \in Nat
  BY KUpPositive
<1>c. \A y \in Slots : /\ slot[y].count \in Nat /\ slot[y] \in SlotRec
  BY <1>a DEF TypeOK, SlotRec
<1>d. \A h \in Governors, y \in Slots : GC(h, y) \in Nat
  BY <1>c DEF GC
<1>1. CASE UNCHANGED slot
  <2>1. GUnmarked'
    BY <1>0, <1>1 DEF GUnmarked
  <2>2. AcctBound'
    BY <1>0, <1>1 DEF AcctBound, Acct, GC
  <2> QED
    BY <1>0, <2>1, <2>2 DEF InvU
<1>2. ASSUME NEW x \in Slots, NEW g0 \in Governors, NEW n \in 1..MaxCount, NEW k \in Kinds, Grant(x, g0, n, k)
      PROVE InvU'
  <2>1. /\ n \in Nat /\ n >= 1
        /\ slot[x].st = "free"
        /\ slot'[x] = Fresh(g0, n, k)
        /\ \A y \in Slots : y # x => slot'[y] = slot[y]
        /\ GovAllows(g0, n, k)
    BY <1>a, <1>2, GrantFacts
  <2>2. /\ slot'[x].gc = TRUE /\ slot'[x].mark = "none" /\ slot'[x].st = "live"
        /\ slot'[x].count = n /\ slot'[x].gov = g0
    BY <2>1, FreshFacts DEF GovCounts
  <2>3. slot[x] = Free
    BY <1>a, <2>1 DEF ShapeS
  <2>4. GUnmarked'
    <3> SUFFICES ASSUME NEW y \in Slots, ~slot'[y].gc, slot'[y].st # "free"
                 PROVE slot'[y].mark # "none"
      BY DEF GUnmarked
    <3>1. y # x
      BY <2>2
    <3> QED
      BY <1>0, <2>1, <3>1 DEF GUnmarked
  <2>5. AcctBound'
    <3> SUFFICES ASSUME NEW h \in Governors PROVE Acct(h)' < KUp
      BY DEF AcctBound
    <3>0. GC(h, x) = 0
      BY <2>3, FreeFacts DEF GC
    <3>a. Acct(h) \in Nat /\ Acct(h) < KUp
      BY <1>0, <1>d, SlotsMembers DEF AcctBound, Acct
    <3>b. \A y \in Slots : y # x => GC(h, y)' = GC(h, y)
      BY <2>1 DEF GC
    <3>1. CASE h = g0
      <4>1. Acct(g0) + n < KUp
        BY <2>1 DEF GovAllows, GovCounts, Bound
      <4>2. GC(g0, x)' = n
        BY <2>2 DEF GC
      <4>3. Acct(g0)' = Acct(g0) + n
        <5>1. CASE x = "l1"
          BY <3>0, <3>1, <3>b, <4>2, <5>1, <1>d, SlotsMembers, <2>1 DEF Acct
        <5>2. CASE x = "l2"
          BY <3>0, <3>1, <3>b, <4>2, <5>2, <1>d, SlotsMembers, <2>1 DEF Acct
        <5>3. CASE x = "l3"
          BY <3>0, <3>1, <3>b, <4>2, <5>3, <1>d, SlotsMembers, <2>1 DEF Acct
        <5> QED
          BY <5>1, <5>2, <5>3, SlotsLiteral
      <4> QED
        BY <3>1, <3>a, <4>1, <4>3, <2>1, <1>k
    <3>2. CASE h # g0
      <4>1. GC(h, x)' = 0
        BY <2>2, <3>2 DEF GC
      <4>2. \A y \in Slots : GC(h, y)' = GC(h, y)
        BY <3>0, <3>b, <4>1
      <4> QED
        BY <3>a, <4>2, SlotsMembers DEF Acct
    <3> QED
      BY <3>1, <3>2
  <2> QED
    BY <1>0, <2>4, <2>5 DEF InvU
<1>3. ASSUME NEW x \in Slots, Effect(x) \/ Seal(x) \/ HearP(x)
      PROVE InvU'
  <2>1. /\ slot[x] \in SlotRec
        /\ \/ slot' = [slot EXCEPT ![x].used = @ + 1, ![x].after = @ + (IF revoked THEN 1 ELSE 0)]
           \/ slot' = [slot EXCEPT ![x].st = "sealed"]
           \/ slot' = [slot EXCEPT ![x].pc = FALSE]
    BY <1>a, <1>3 DEF TypeOK, Effect, Seal, HearP
  <2>2. /\ slot'[x].gc = slot[x].gc /\ slot'[x].mark = slot[x].mark /\ slot'[x].count = slot[x].count
        /\ slot'[x].gov = slot[x].gov
        /\ (slot'[x].st = slot[x].st \/ slot'[x].st = "sealed")
        /\ \A y \in Slots : y # x => slot'[y] = slot[y]
    BY <1>a, <2>1 DEF TypeOK, SlotRec
  <2>3. GUnmarked'
    <3> SUFFICES ASSUME NEW y \in Slots, ~slot'[y].gc, slot'[y].st # "free"
                 PROVE slot'[y].mark # "none"
      BY DEF GUnmarked
    <3>1. CASE y = x
      <4>1. slot[x].st # "free"
        BY <1>a, <1>3, <2>2, <3>1, FreeFacts DEF ShapeS, Effect, Seal, HearP
      <4> QED
        BY <1>0, <2>2, <3>1, <4>1 DEF GUnmarked
    <3>2. CASE y # x
      BY <1>0, <2>2, <3>2 DEF GUnmarked
    <3> QED
      BY <3>1, <3>2
  <2>4. AcctBound'
    <3> SUFFICES ASSUME NEW h \in Governors PROVE Acct(h)' < KUp
      BY DEF AcctBound
    <3>1. \A y \in Slots : GC(h, y)' = GC(h, y)
      <4> SUFFICES ASSUME NEW y \in Slots PROVE GC(h, y)' = GC(h, y)
        OBVIOUS
      <4>1. CASE y = x
        BY <2>2, <4>1 DEF GC
      <4>2. CASE y # x
        BY <2>2, <4>2 DEF GC
      <4> QED
        BY <4>1, <4>2
    <3> QED
      BY <1>0, <3>1, SlotsMembers DEF AcctBound, Acct
  <2> QED
    BY <1>0, <2>3, <2>4 DEF InvU
<1>4. ASSUME NEW x \in Slots, Mark(x) PROVE InvU'
  <2>1. /\ slot[x].st = "sealed" /\ slot[x].mark = "none"
        /\ slot' = [slot EXCEPT ![x].mark = IF revoked THEN "after" ELSE "before", ![x].read = slot[x].used]
    BY <1>4 DEF Mark, Markable
  <2>2. slot[x] \in SlotRec
    BY <1>a DEF TypeOK
  <2>3. /\ slot'[x].gc = slot[x].gc /\ slot'[x].count = slot[x].count
        /\ slot'[x].gov = slot[x].gov /\ slot'[x].mark # "none"
        /\ \A y \in Slots : y # x => slot'[y] = slot[y]
    BY <1>a, <2>1, <2>2 DEF TypeOK, SlotRec
  <2>4. GUnmarked'
    <3> SUFFICES ASSUME NEW y \in Slots, ~slot'[y].gc, slot'[y].st # "free"
                 PROVE slot'[y].mark # "none"
      BY DEF GUnmarked
    <3>1. CASE y = x
      BY <2>3, <3>1
    <3>2. CASE y # x
      BY <1>0, <2>3, <3>2 DEF GUnmarked
    <3> QED
      BY <3>1, <3>2
  <2>5. AcctBound'
    <3> SUFFICES ASSUME NEW h \in Governors PROVE Acct(h)' < KUp
      BY DEF AcctBound
    <3>1. \A y \in Slots : GC(h, y)' = GC(h, y)
      <4> SUFFICES ASSUME NEW y \in Slots PROVE GC(h, y)' = GC(h, y)
        OBVIOUS
      <4>1. CASE y = x
        BY <2>3, <4>1 DEF GC
      <4>2. CASE y # x
        BY <2>3, <4>2 DEF GC
      <4> QED
        BY <4>1, <4>2
    <3> QED
      BY <1>0, <3>1, SlotsMembers DEF AcctBound, Acct
  <2> QED
    BY <1>0, <2>4, <2>5 DEF InvU
<1>5. ASSUME NEW x \in Slots, HearG(x) PROVE InvU'
  <2>1. /\ slot[x].mark # "none"
        /\ slot' = [slot EXCEPT ![x].gc = FALSE]
    BY <1>5 DEF HearG
  <2>2. slot[x] \in SlotRec
    BY <1>a DEF TypeOK
  <2>3. /\ slot'[x].gc = FALSE /\ slot'[x].mark = slot[x].mark /\ slot'[x].count = slot[x].count
        /\ slot'[x].gov = slot[x].gov
        /\ \A y \in Slots : y # x => slot'[y] = slot[y]
    BY <1>a, <2>1, <2>2 DEF TypeOK, SlotRec
  <2>4. GUnmarked'
    <3> SUFFICES ASSUME NEW y \in Slots, ~slot'[y].gc, slot'[y].st # "free"
                 PROVE slot'[y].mark # "none"
      BY DEF GUnmarked
    <3>1. CASE y = x
      BY <2>1, <2>3, <3>1
    <3>2. CASE y # x
      BY <1>0, <2>3, <3>2 DEF GUnmarked
    <3> QED
      BY <3>1, <3>2
  <2>5. AcctBound'
    <3> SUFFICES ASSUME NEW h \in Governors PROVE Acct(h)' < KUp
      BY DEF AcctBound
    <3>1. Acct(h) < KUp
      BY <1>0 DEF AcctBound
    <3>2. \A y \in Slots : GC(h, y)' <= GC(h, y) /\ GC(h, y)' \in Nat
      <4> SUFFICES ASSUME NEW y \in Slots PROVE GC(h, y)' <= GC(h, y) /\ GC(h, y)' \in Nat
        OBVIOUS
      <4>0. slot[y].count \in Nat
        BY <1>c
      <4>1. CASE y = x
        BY <2>3, <4>0, <4>1 DEF GC
      <4>2. CASE y # x
        BY <2>3, <4>0, <4>2 DEF GC
      <4> QED
        BY <4>1, <4>2
    <3> QED
      BY <1>d, <1>k, <3>1, <3>2, SlotsMembers DEF Acct
  <2> QED
    BY <1>0, <2>4, <2>5 DEF InvU
<1>6. ASSUME NEW x \in Slots, Reclaim(x) PROVE InvU'
  <2>1. slot' = [slot EXCEPT ![x] = Free]
    BY <1>6 DEF Reclaim
  <2>2. /\ slot'[x] = Free
        /\ \A y \in Slots : y # x => slot'[y] = slot[y]
    BY <1>a, <2>1 DEF TypeOK
  <2>3. GUnmarked'
    <3> SUFFICES ASSUME NEW y \in Slots, ~slot'[y].gc, slot'[y].st # "free"
                 PROVE slot'[y].mark # "none"
      BY DEF GUnmarked
    <3>1. y # x
      BY <2>2, FreeFacts
    <3> QED
      BY <1>0, <2>2, <3>1 DEF GUnmarked
  <2>4. AcctBound'
    <3> SUFFICES ASSUME NEW h \in Governors PROVE Acct(h)' < KUp
      BY DEF AcctBound
    <3>1. Acct(h) < KUp
      BY <1>0 DEF AcctBound
    <3>2. \A y \in Slots : GC(h, y)' <= GC(h, y) /\ GC(h, y)' \in Nat
      <4> SUFFICES ASSUME NEW y \in Slots PROVE GC(h, y)' <= GC(h, y) /\ GC(h, y)' \in Nat
        OBVIOUS
      <4>0. slot[y].count \in Nat
        BY <1>c
      <4>1. CASE y = x
        BY <2>2, <4>0, <4>1, FreeFacts DEF GC
      <4>2. CASE y # x
        BY <2>2, <4>0, <4>2 DEF GC
      <4> QED
        BY <4>1, <4>2
    <3> QED
      BY <1>d, <1>k, <3>1, <3>2, SlotsMembers DEF Acct
  <2> QED
    BY <1>0, <2>3, <2>4 DEF InvU
<1>7. ASSUME NEW x \in Slots, HearWord(x) PROVE InvU'
  BY <1>7 DEF HearWord
<1> QED
  <2>1. ASSUME Revoke PROVE UNCHANGED slot
    BY <2>1 DEF Revoke
  <2>2. ASSUME NEW n \in 1..MaxCount, RefuseBound(n) PROVE UNCHANGED slot
    BY <2>2 DEF RefuseBound
  <2>3. ASSUME NEW g \in Governors, NEW n \in 1..MaxCount, RefuseGov(g, n) PROVE UNCHANGED slot
    BY <2>3 DEF RefuseGov
  <2>4. ASSUME UNCHANGED vars PROVE UNCHANGED slot
    BY <2>4 DEF vars
  <2> QED
    BY <1>1, <1>2, <1>3, <1>4, <1>5, <1>6, <1>7, <2>1, <2>2, <2>3, <2>4 DEF Next

LEMMA UBounds == InvU => HavocPlaneBoundedInEffects
<1> SUFFICES ASSUME InvU, NEW h \in Governors PROVE UnreadOf(h) < KUp
  BY DEF HavocPlaneBoundedInEffects
<1>0. TypeOK /\ ShapeS /\ MarkedSealed /\ GUnmarked /\ AcctBound
  BY DEF InvU, Sealed, Shape
<1>1. \A y \in Slots : UnreadAt(h, y) <= GC(h, y) /\ UnreadAt(h, y) \in Nat /\ GC(h, y) \in Nat
  <2> SUFFICES ASSUME NEW y \in Slots
               PROVE UnreadAt(h, y) <= GC(h, y) /\ UnreadAt(h, y) \in Nat /\ GC(h, y) \in Nat
    OBVIOUS
  <2>0. /\ slot[y] \in SlotRec /\ slot[y].read \in Nat /\ slot[y].used \in Nat /\ slot[y].count \in Nat
        /\ slot[y].used <= slot[y].count /\ slot[y].read <= slot[y].used
    BY <1>0 DEF TypeOK, SlotRec, ShapeS
  <2>1. CASE slot[y].gov # h
    BY <2>0, <2>1 DEF UnreadAt, GC
  <2>2. CASE slot[y].gov = h /\ slot[y].gc
    BY <2>0, <2>2 DEF UnreadAt, GC
  <2>3. CASE slot[y].gov = h /\ ~slot[y].gc
    <3>1. GC(h, y) = 0 /\ UnreadAt(h, y) = slot[y].used - slot[y].read
      BY <2>3 DEF UnreadAt, GC
    <3>2. slot[y].st # "free"
      BY <1>0, <2>3, FreeFacts DEF ShapeS, Governors
    <3>3. slot[y].mark # "none"
      BY <1>0, <2>3, <3>2 DEF GUnmarked
    <3>4. slot[y].read = slot[y].used
      BY <1>0, <3>3 DEF MarkedSealed
    <3> QED
      BY <2>0, <3>1, <3>4
  <2> QED
    BY <2>1, <2>2, <2>3
<1>2. Acct(h) < KUp
  BY <1>0 DEF AcctBound
<1>3. KUp \in Nat
  BY KUpPositive
<1> QED
  BY <1>1, <1>2, <1>3, SlotsMembers DEF UnreadOf, Acct

THEOREM HavocPlaneBoundedInEffectsAlways ==
  ASSUME Mut # "M_ATMOST", Mut # "M_EARLYRELEASE", Mut # "M_TRUSTMARK", Mut # "M_ORDEREDFREE"
  PROVE  Spec => []HavocPlaneBoundedInEffects
<1>1. InvU /\ [Next]_vars => InvU'
  BY NextU
<1> QED
  BY InitU, <1>1, UBounds, PTL DEF Spec
-----------------------------------------------------------------------------
THEOREM SafeAlways ==
  ASSUME Mut = "none"
  PROVE  Spec => []Safe
<1>1. Spec => []EffectsAfterHonest
  BY EffectsAfterHonestAlways
<1>2. Spec => []EffectsAfterPerGovernor
  BY EffectsAfterPerGovernorAlways
<1>3. Spec => []HavocPlaneBoundedInEffects
  BY HavocPlaneBoundedInEffectsAlways
<1>4. Spec => []SealedIsSpent
  BY SealedIsSpentAlways
<1>5. Spec => []CountExact
  BY CountExactAlways
<1> QED
  BY <1>1, <1>2, <1>3, <1>4, <1>5, PTL DEF Safe, EffectsAfterRevocationBounded
-----------------------------------------------------------------------------
(* Why the mutations must fail. The counterexamples are TLC's.                 *)

LEMMA MutNoChargeLeavesNoCharge == Mut = "M_NOCHARGE" => ~PlaneCharges
  BY DEF PlaneCharges

LEMMA MutAtMostAdmitsTheBound == Mut = "M_ATMOST" => Bound(KUp)
  BY KUpPositive DEF Bound

LEMMA MutTrustMarkIsTheOnlyWordRelease ==
  ASSUME NEW x, HearWord(x)
  PROVE  Mut = "M_TRUSTMARK" /\ PlaneCaptured
  BY DEF HearWord

LEMMA MutEarlyReleaseMarksALiveLease ==
  ASSUME Mut = "M_EARLYRELEASE", NEW x, slot[x].st = "live"
  PROVE  Markable(x)
  BY DEF Markable

LEMMA MutNoStopDoesNotStop == Mut = "M_NOSTOP" => ~Stops
  BY DEF Stops

LEMMA MutOrderedFreeLeavesItUncounted == Mut = "M_ORDEREDFREE" => ~GovCounts("ordered")
  BY DEF GovCounts
=============================================================================
