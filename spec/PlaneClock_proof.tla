--------------------------- MODULE PlaneClock_proof ---------------------------
(* TLAPS proof of the invariants of PlaneClock.tla (ADR-0064 §8), for every    *)
(* value of the constants the assumptions below admit: every set of replicas,  *)
(* every certificate size, every tick period, every intent and every bound.    *)
(* PlaneClock.tla is not edited.                                               *)
(*                                                                             *)
(*   THEOREM NoGrantPastExpiryAlways                                           *)
(*        [Mut # "M_ONECLOCK", # "M_RECEIPT", # "M_RELATIVETICK", # "M_TOOSLOW"]*)
(*   THEOREM EntryEndsAtExtentAlways   [Mut # "M_NOEXTENT", # "M_NOWATCHDOG"]  *)
(*   THEOREM NoStretchUnlessSlowAlways [Mut # "M_NOWATCHDOG"]                  *)
(*   THEOREM SafeAlways                [Mut = "none"]                          *)
(*                                                                             *)
(* NoGrantPastExpiryAlways rests on ClockPremise, PlaneClock.tla's named       *)
(* assumption, through CertHasSound: a certificate holds a replica that is     *)
(* neither captured nor slow. It is a declared bound under a premise about     *)
(* time, not a safety theorem in the lattice analysis's sense.                 *)
(*                                                                             *)
(* The strengthening. `Shape` holds under every mutation: the type invariant;  *)
(* a replica neither captured nor slow has a clock at or above real time, and  *)
(* so has a governor whose clock is not slow; a running entry is short of its  *)
(* end. NoGrantPastExpiry adds that a delivered intent's expiry is the one it  *)
(* names; the flag is then false at Grant, because the sound signer's clock is *)
(* below the next tick's due time, which is at or below the expiry's. The      *)
(* other two properties add one clause each: an entry's end is within          *)
(* MaxExtent of its start, and a running entry's governor clock has not passed *)
(* the next tick's due time.                                                   *)
(*                                                                             *)
(* Mutations and witnesses are behaviours and stay with TLC                    *)
(* (PlaneClock-results-*.txt). Check: tools/tlapm --cleanfp --strict.          *)
EXTENDS PlaneClock, FiniteSetTheorems, TLAPS

ASSUME PNat           == P \in Nat
ASSUME BaseNat        == Base \in Nat
ASSUME DNat           == D \in Nat
ASSUME MaxExtentNat   == MaxExtent \in Nat
ASSUME MaxTickNat     == MaxTick \in Nat
ASSUME CertNat        == Cert \in Nat
ASSUME ReplicasFinite == IsFiniteSet(Replicas)

Tags == {"withheld", "tickRefused", "grant", "slack", "grantRefused", "extentEnded", "ran", "alone"}

TypeOK ==
  /\ now \in Nat
  /\ clock \in [Replicas -> Nat]
  /\ gclock \in Nat
  /\ tick \in Nat
  /\ gtick \in Nat
  /\ lastAt \in [Replicas -> Nat]
  /\ delivered \in BOOLEAN
  /\ expiry \in Nat
  /\ lease \in BOOLEAN
  /\ running \in BOOLEAN
  /\ start \in Nat
  /\ endAt \in Nat
  /\ lateGrant \in BOOLEAN
  /\ seen \subseteq Tags

SoundClocks == \A y \in Replicas : y \notin (Captured \cup Slow) => clock[y] >= now
GovSound    == GovClass # "slow" => gclock >= now
RunExt      == running => gtick < endAt

Shape == TypeOK /\ SoundClocks /\ GovSound /\ RunExt

ExpiryTrue == delivered => expiry = TrueExpiry
InvGrant   == Shape /\ ExpiryTrue /\ NoGrantPastExpiry

ExtBound == running => endAt <= start + MaxExtent
Watch    == running => gclock <= Deadline(gtick)
InvExt   == Shape /\ ExtBound
InvWatch == Shape /\ Watch
-----------------------------------------------------------------------------
LEMMA DeadlineType ==
  ASSUME NEW a \in Nat PROVE Deadline(a) \in Nat
  BY PNat DEF Deadline

LEMMA DeadlineMono ==
  ASSUME NEW a \in Nat, NEW b \in Nat, a <= b PROVE Deadline(a) <= Deadline(b)
<1> PICK k \in Nat : b = a + k
  <2> WITNESS b - a \in Nat
  <2> QED OBVIOUS
<1>1. (b + 1) * P = (a + 1) * P + k * P
  BY PNat
<1>2. k * P \in Nat /\ (a + 1) * P \in Nat
  BY PNat
<1> QED
  BY <1>1, <1>2 DEF Deadline

LEMMA TrueExpiryNat == TrueExpiry \in Nat
  BY BaseNat, DNat DEF TrueExpiry

LEMMA ExtentsFacts ==
  ASSUME NEW ext \in Extents
  PROVE  /\ ext \in Nat
         /\ ext >= 1
         /\ Mut # "M_NOEXTENT" => ext <= MaxExtent
  BY MaxExtentNat, MaxTickNat DEF Extents, NoExtent

\* A certificate holds a replica that is neither captured nor slow: §4's premise, used once.
LEMMA CertHasSound ==
  ASSUME Mut # "M_TOOSLOW", NEW S \in Certs
  PROVE  \E y \in S : y \notin (Captured \cup Slow)
<1> DEFINE B == Captured \cup Slow
<1>1. B \in SUBSET Replicas
  BY ClassesWF
<1>2. IsFiniteSet(B) /\ Cardinality(B) \in Nat
  BY <1>1, ReplicasFinite, FS_Subset, FS_CardinalityType
<1>3. S \subseteq Replicas /\ Cardinality(S) >= Cert
  BY DEF Certs
<1>4. Cardinality(B) < Cert
  BY ClockPremise
<1> SUFFICES ASSUME \A y \in S : y \in B PROVE FALSE
  OBVIOUS
<1>5. S \in SUBSET B
  OBVIOUS
<1>6. Cardinality(S) <= Cardinality(B) /\ IsFiniteSet(S)
  BY <1>2, <1>5, FS_Subset
<1>7. Cardinality(S) \in Nat
  BY <1>6, FS_CardinalityType
<1> QED
  BY <1>2, <1>3, <1>4, <1>6, <1>7, CertNat

LEMMA InitShape == Init => Shape
<1> SUFFICES ASSUME Init PROVE Shape OBVIOUS
<1>1. TypeOK
  BY DEF Init, TypeOK
<1>2. SoundClocks
  BY DEF Init, SoundClocks
<1>3. GovSound
  BY DEF Init, GovSound
<1>4. RunExt
  BY DEF Init, RunExt
<1> QED
  BY <1>1, <1>2, <1>3, <1>4 DEF Shape

LEMMA NextTypeOK == TypeOK /\ [Next]_vars => TypeOK'
<1> SUFFICES ASSUME TypeOK, [Next]_vars PROVE TypeOK' OBVIOUS
<1>1. CASE UNCHANGED vars
  BY <1>1 DEF TypeOK, vars
<1>2. ASSUME NEW d \in Steps, NEW g \in 0..2, Advance(d, g) PROVE TypeOK'
  <2>1. /\ now' = now + 1
        /\ clock' = [y \in Replicas |-> clock[y] + d[y]]
        /\ gclock' = gclock + g
        /\ UNCHANGED <<tick, gtick, lastAt, delivered, expiry, lease, running, start, endAt, lateGrant, seen>>
    BY <1>2 DEF Advance
  <2>2. d \in [Replicas -> 0..2]
    BY DEF Steps
  <2>3. clock' \in [Replicas -> Nat]
    BY <2>1, <2>2 DEF TypeOK
  <2> QED
    BY <2>1, <2>3 DEF TypeOK
<1>3. CASE Deliver
  <2>1. expiry' \in Nat
    BY <1>3, TrueExpiryNat, DNat DEF Deliver, TypeOK
  <2>2. seen' \subseteq Tags
    BY <1>3 DEF Deliver, TypeOK, Tags
  <2> QED
    BY <1>3, <2>1, <2>2 DEF Deliver, TypeOK
<1>4. CASE ApplyTick
  <2>1. CASE running /\ gtick + 1 >= endAt
    <3>1. seen' = seen \cup {"extentEnded"} /\ running' = FALSE /\ start' = 0 /\ endAt' = 0
      BY <1>4, <2>1 DEF ApplyTick
    <3>2. seen' \subseteq Tags
      BY <3>1 DEF TypeOK, Tags
    <3> QED
      BY <1>4, <3>1, <3>2 DEF ApplyTick, TypeOK
  <2>2. CASE ~(running /\ gtick + 1 >= endAt)
    <3>1. UNCHANGED <<running, start, endAt, seen>>
      BY <1>4, <2>2 DEF ApplyTick
    <3> QED
      BY <1>4, <3>1 DEF ApplyTick, TypeOK
  <2> QED
    BY <2>1, <2>2
<1>5. CASE GoAlone
  <2>1. seen' \subseteq Tags
    BY <1>5 DEF GoAlone, TypeOK, Tags
  <2> QED
    BY <1>5, <2>1 DEF GoAlone, TypeOK
<1>6. ASSUME NEW S \in Certs, TickCert(S) PROVE TypeOK'
  <2>1. tick' = tick + 1 /\ lastAt' \in [Replicas -> Nat]
    BY <1>6 DEF TickCert, TypeOK
  <2> QED
    BY <1>6, <2>1 DEF TickCert, TypeOK
<1>7. ASSUME NEW S \in Certs, RefuseTick(S) PROVE TypeOK'
  <2>1. seen' \subseteq Tags
    BY <1>7 DEF RefuseTick, TypeOK, Tags
  <2> QED
    BY <1>7, <2>1 DEF RefuseTick, TypeOK
<1>8. ASSUME NEW S \in Certs, Grant(S) PROVE TypeOK'
  <2>1. seen' \subseteq Tags
    BY <1>8 DEF Grant, TypeOK, Tags
  <2>2. lease' \in BOOLEAN /\ lateGrant' \in BOOLEAN
    BY <1>8 DEF Grant, TypeOK
  <2> QED
    BY <1>8, <2>1, <2>2 DEF Grant, TypeOK
<1>9. ASSUME NEW S \in Certs, RefuseGrant(S) PROVE TypeOK'
  <2>1. seen' \subseteq Tags
    BY <1>9 DEF RefuseGrant, TypeOK, Tags
  <2> QED
    BY <1>9, <2>1 DEF RefuseGrant, TypeOK
<1>10. ASSUME NEW ext \in Extents, StartEntry(ext) PROVE TypeOK'
  <2>1. ext \in Nat
    BY ExtentsFacts
  <2>2. seen' \subseteq Tags
    BY <1>10 DEF StartEntry, TypeOK, Tags
  <2> QED
    BY <1>10, <2>1, <2>2 DEF StartEntry, TypeOK
<1> QED
  BY <1>1, <1>2, <1>3, <1>4, <1>5, <1>6, <1>7, <1>8, <1>9, <1>10 DEF Next

LEMMA NextShape == Shape /\ [Next]_vars => Shape'
<1> SUFFICES ASSUME Shape, [Next]_vars PROVE Shape' OBVIOUS
<1>0. TypeOK /\ TypeOK'
  BY NextTypeOK DEF Shape
<1>a. SoundClocks /\ GovSound /\ RunExt
  BY DEF Shape
<1>1. CASE UNCHANGED vars
  BY <1>0, <1>a, <1>1 DEF Shape, SoundClocks, GovSound, RunExt, vars
<1>2. ASSUME NEW d \in Steps, NEW g \in 0..2, Advance(d, g) PROVE Shape'
  <2>1. /\ now' = now + 1
        /\ clock' = [y \in Replicas |-> clock[y] + d[y]]
        /\ gclock' = gclock + g
        /\ \A y \in Replicas : LegalStep(y, d[y])
        /\ LegalGov(g)
        /\ UNCHANGED <<gtick, running, endAt>>
    BY <1>2 DEF Advance
  <2>2. d \in [Replicas -> 0..2]
    BY DEF Steps
  <2>3. SoundClocks'
    <3> SUFFICES ASSUME NEW z \in Replicas, z \notin (Captured \cup Slow) PROVE clock'[z] >= now'
      BY DEF SoundClocks
    <3>1. d[z] >= 1 /\ d[z] \in Nat
      BY <2>1, <2>2 DEF LegalStep
    <3>2. clock[z] >= now /\ clock[z] \in Nat /\ now \in Nat
      BY <1>0, <1>a DEF SoundClocks, TypeOK
    <3>3. clock'[z] = clock[z] + d[z]
      BY <2>1
    <3> QED
      BY <2>1, <3>1, <3>2, <3>3
  <2>4. GovSound'
    <3> SUFFICES ASSUME GovClass # "slow" PROVE gclock' >= now'
      BY DEF GovSound
    <3>1. g >= 1
      BY <2>1 DEF LegalGov
    <3>2. gclock >= now /\ gclock \in Nat /\ now \in Nat
      BY <1>0, <1>a DEF GovSound, TypeOK
    <3> QED
      BY <2>1, <3>1, <3>2
  <2>5. RunExt'
    BY <1>a, <2>1 DEF RunExt
  <2> QED
    BY <1>0, <2>3, <2>4, <2>5 DEF Shape
<1>3. CASE Deliver \/ GoAlone
  <2>1. UNCHANGED <<now, clock, gclock, gtick>>
    BY <1>3 DEF Deliver, GoAlone
  <2>2. SoundClocks' /\ GovSound'
    BY <1>a, <2>1 DEF SoundClocks, GovSound
  <2>3. RunExt'
    <3>1. CASE Deliver
      <4>1. UNCHANGED <<running, endAt>>
        BY <3>1 DEF Deliver
      <4> QED
        BY <1>a, <2>1, <4>1 DEF RunExt
    <3>2. CASE GoAlone
      <4>1. running' = FALSE
        BY <3>2 DEF GoAlone
      <4> QED
        BY <4>1 DEF RunExt
    <3> QED
      BY <1>3, <3>1, <3>2
  <2> QED
    BY <1>0, <2>2, <2>3 DEF Shape
<1>4. CASE ApplyTick
  <2>1. UNCHANGED <<now, clock, gclock>> /\ gtick' = gtick + 1
    BY <1>4 DEF ApplyTick
  <2>2. SoundClocks' /\ GovSound'
    BY <1>a, <2>1 DEF SoundClocks, GovSound
  <2>3. RunExt'
    <3>1. CASE running /\ gtick + 1 >= endAt
      <4>1. running' = FALSE
        BY <1>4, <3>1 DEF ApplyTick
      <4> QED
        BY <4>1 DEF RunExt
    <3>2. CASE ~(running /\ gtick + 1 >= endAt)
      <4>1. UNCHANGED <<running, endAt>>
        BY <1>4, <3>2 DEF ApplyTick
      <4>2. running => gtick + 1 < endAt
        BY <1>0, <3>2 DEF TypeOK
      <4> QED
        BY <2>1, <4>1, <4>2 DEF RunExt
    <3> QED
      BY <3>1, <3>2
  <2> QED
    BY <1>0, <2>2, <2>3 DEF Shape
<1>5. ASSUME NEW S \in Certs, TickCert(S) \/ RefuseTick(S) \/ Grant(S) \/ RefuseGrant(S) PROVE Shape'
  <2>1. UNCHANGED <<now, clock, gclock, gtick, running, endAt>>
    BY <1>5 DEF TickCert, RefuseTick, Grant, RefuseGrant
  <2>2. SoundClocks' /\ GovSound' /\ RunExt'
    BY <1>a, <2>1 DEF SoundClocks, GovSound, RunExt
  <2> QED
    BY <1>0, <2>2 DEF Shape
<1>6. ASSUME NEW ext \in Extents, StartEntry(ext) PROVE Shape'
  <2>1. /\ UNCHANGED <<now, clock, gclock, gtick>>
        /\ running' = TRUE
        /\ endAt' = gtick + ext
    BY <1>6 DEF StartEntry
  <2>2. ext \in Nat /\ ext >= 1
    BY ExtentsFacts
  <2>3. SoundClocks' /\ GovSound'
    BY <1>a, <2>1 DEF SoundClocks, GovSound
  <2>4. RunExt'
    BY <1>0, <2>1, <2>2 DEF RunExt, TypeOK
  <2> QED
    BY <1>0, <2>3, <2>4 DEF Shape
<1> QED
  BY <1>1, <1>2, <1>3, <1>4, <1>5, <1>6 DEF Next
-----------------------------------------------------------------------------
(* NoGrantPastExpiry: at Grant, the sound signer's clock against the due time. *)

\* Only Deliver moves the expiry, and only Grant moves the flag.
LEMMA GrantFrame ==
  ASSUME [Next]_vars
  PROVE  \/ UNCHANGED <<lateGrant, delivered, expiry>>
         \/ Deliver
         \/ \E S \in Certs : Grant(S)
<1> SUFFICES ASSUME Next, ~UNCHANGED <<lateGrant, delivered, expiry>>, ~Deliver
             PROVE  \E S \in Certs : Grant(S)
  BY DEF vars
<1>1. \A d \in Steps, g \in 0..2 : ~Advance(d, g)
  BY DEF Advance
<1>2. ~ApplyTick /\ ~GoAlone
  BY DEF ApplyTick, GoAlone
<1>3. \A S \in Certs : ~TickCert(S) /\ ~RefuseTick(S) /\ ~RefuseGrant(S)
  BY DEF TickCert, RefuseTick, RefuseGrant
<1>4. \A ext \in Extents : ~StartEntry(ext)
  BY DEF StartEntry
<1> QED
  BY <1>1, <1>2, <1>3, <1>4 DEF Next

LEMMA GrantInTime ==
  ASSUME Mut # "M_ONECLOCK", Mut # "M_RELATIVETICK", Mut # "M_TOOSLOW",
         Shape, ExpiryTrue, NEW S \in Certs, Grant(S)
  PROVE  now < Deadline(TrueExpiry)
<1>1. PICK y \in S : y \notin (Captured \cup Slow)
  BY CertHasSound
<1>2. y \in Replicas
  BY DEF Certs
<1>3. clock[y] >= now /\ clock[y] \in Nat /\ now \in Nat
  BY <1>1, <1>2 DEF Shape, SoundClocks, TypeOK
<1>4. clock[y] < Deadline(tick)
  <2>1. GrantOK(S)
    BY DEF Grant
  <2>2. SignsGrant(y)
    BY <2>1 DEF GrantOK
  <2> QED
    BY <1>1, <2>2 DEF SignsGrant, Due
<1>5. tick <= TrueExpiry /\ tick \in Nat
  BY DEF Grant, ExpiryTrue, Shape, TypeOK
<1>6. Deadline(tick) <= Deadline(TrueExpiry) /\ Deadline(tick) \in Nat /\ Deadline(TrueExpiry) \in Nat
  BY <1>5, TrueExpiryNat, DeadlineMono, DeadlineType
<1> QED
  BY <1>3, <1>4, <1>6

LEMMA InitGrant == Init => InvGrant
  BY InitShape DEF Init, InvGrant, ExpiryTrue, NoGrantPastExpiry

LEMMA NextGrant ==
  ASSUME Mut # "M_ONECLOCK", Mut # "M_RECEIPT", Mut # "M_RELATIVETICK", Mut # "M_TOOSLOW",
         InvGrant, [Next]_vars
  PROVE  InvGrant'
<1>0. Shape /\ Shape' /\ ExpiryTrue /\ NoGrantPastExpiry
  BY NextShape DEF InvGrant
<1>1. CASE UNCHANGED <<lateGrant, delivered, expiry>>
  BY <1>0, <1>1 DEF InvGrant, ExpiryTrue, NoGrantPastExpiry
<1>2. CASE Deliver
  <2>1. expiry' = TrueExpiry /\ UNCHANGED lateGrant
    BY <1>2 DEF Deliver
  <2> QED
    BY <1>0, <2>1 DEF InvGrant, ExpiryTrue, NoGrantPastExpiry
<1>3. CASE \E S \in Certs : Grant(S)
  <2>1. PICK S \in Certs : Grant(S)
    BY <1>3
  <2>2. now < Deadline(TrueExpiry)
    BY <1>0, <2>1, GrantInTime
  <2>3. /\ lateGrant' = (lateGrant \/ now >= Deadline(TrueExpiry))
        /\ UNCHANGED <<delivered, expiry>>
    BY <2>1 DEF Grant
  <2>4. ~(now >= Deadline(TrueExpiry))
    BY <1>0, <2>2, TrueExpiryNat, DeadlineType DEF Shape, TypeOK
  <2>5. ~lateGrant'
    BY <1>0, <2>3, <2>4 DEF NoGrantPastExpiry
  <2> QED
    BY <1>0, <2>3, <2>5 DEF InvGrant, ExpiryTrue, NoGrantPastExpiry
<1> QED
  BY <1>1, <1>2, <1>3, GrantFrame

THEOREM NoGrantPastExpiryAlways ==
  ASSUME Mut # "M_ONECLOCK", Mut # "M_RECEIPT", Mut # "M_RELATIVETICK", Mut # "M_TOOSLOW"
  PROVE  Spec => []NoGrantPastExpiry
<1>1. InvGrant /\ [Next]_vars => InvGrant'
  BY NextGrant
<1>2. InvGrant => NoGrantPastExpiry
  BY DEF InvGrant
<1> QED
  BY InitGrant, <1>1, <1>2, PTL DEF Spec
-----------------------------------------------------------------------------
(* EntryEndsAtExtent, clause by clause.                                        *)

LEMMA InitExt == Init => InvExt
  BY InitShape DEF Init, InvExt, ExtBound

LEMMA NextExt ==
  ASSUME Mut # "M_NOEXTENT", InvExt, [Next]_vars
  PROVE  InvExt'
<1>0. Shape /\ Shape' /\ ExtBound
  BY NextShape DEF InvExt
<1>t. TypeOK
  BY <1>0 DEF Shape
<1>1. CASE UNCHANGED <<running, start, endAt>>
  BY <1>0, <1>1 DEF InvExt, ExtBound
<1>2. ASSUME NEW ext \in Extents, StartEntry(ext) PROVE InvExt'
  <2>1. running' = TRUE /\ start' = gtick /\ endAt' = gtick + ext
    BY <1>2 DEF StartEntry
  <2>2. ext \in Nat /\ ext <= MaxExtent
    BY ExtentsFacts
  <2>3. ExtBound'
    BY <1>t, <2>1, <2>2, MaxExtentNat DEF ExtBound, TypeOK
  <2> QED
    BY <1>0, <2>3 DEF InvExt
<1>3. CASE ApplyTick
  <2>1. CASE running /\ gtick + 1 >= endAt
    <3>1. running' = FALSE
      BY <1>3, <2>1 DEF ApplyTick
    <3> QED
      BY <1>0, <3>1 DEF InvExt, ExtBound
  <2>2. CASE ~(running /\ gtick + 1 >= endAt)
    <3>1. UNCHANGED <<running, start, endAt>>
      BY <1>3, <2>2 DEF ApplyTick
    <3> QED
      BY <1>1, <3>1
  <2> QED
    BY <2>1, <2>2
<1>4. CASE GoAlone
  <2>1. running' = FALSE
    BY <1>4 DEF GoAlone
  <2> QED
    BY <1>0, <2>1 DEF InvExt, ExtBound
<1>5. QED
  <2>1. CASE \/ \E d \in Steps, g \in 0..2 : Advance(d, g)
             \/ Deliver
             \/ \E S \in Certs : TickCert(S) \/ RefuseTick(S) \/ Grant(S) \/ RefuseGrant(S)
             \/ UNCHANGED vars
    <3>1. UNCHANGED <<running, start, endAt>>
      BY <2>1 DEF Advance, Deliver, TickCert, RefuseTick, Grant, RefuseGrant, vars
    <3> QED
      BY <1>1, <3>1
  <2> QED
    BY <1>2, <1>3, <1>4, <2>1 DEF Next

LEMMA InitWatch == Init => InvWatch
<1> SUFFICES ASSUME Init PROVE InvWatch OBVIOUS
<1>1. Shape
  BY InitShape
<1>2. Watch
  BY DEF Init, Watch
<1> QED
  BY <1>1, <1>2 DEF InvWatch

LEMMA NextWatch ==
  ASSUME Mut # "M_NOWATCHDOG", InvWatch, [Next]_vars
  PROVE  InvWatch'
<1>0. Shape /\ Shape' /\ Watch
  BY NextShape DEF InvWatch
<1>t. TypeOK
  BY <1>0 DEF Shape
<1>1. CASE UNCHANGED <<running, gclock, gtick>>
  BY <1>0, <1>1 DEF InvWatch, Watch
<1>2. ASSUME NEW d \in Steps, NEW g \in 0..2, Advance(d, g) PROVE InvWatch'
  <2>1. /\ ~WatchdogHolds(g)
        /\ gclock' = gclock + g
        /\ UNCHANGED <<running, gtick>>
    BY <1>2 DEF Advance
  <2>2. running => gclock + g <= Deadline(gtick)
    <3>1. Deadline(gtick) \in Nat /\ gclock \in Nat /\ g \in Nat
      BY <1>t, DeadlineType DEF TypeOK
    <3> QED
      BY <2>1, <3>1 DEF WatchdogHolds
  <2> QED
    BY <1>0, <2>1, <2>2 DEF InvWatch, Watch
<1>3. ASSUME NEW ext \in Extents, StartEntry(ext) PROVE InvWatch'
  <2>1. /\ ~Overdue
        /\ UNCHANGED <<gclock, gtick>>
    BY <1>3 DEF StartEntry
  <2>2. gclock <= Deadline(gtick)
    BY <1>t, <2>1, DeadlineType DEF Overdue, TypeOK
  <2> QED
    BY <1>0, <2>1, <2>2 DEF InvWatch, Watch
<1>4. CASE ApplyTick
  <2>1. gtick' = gtick + 1 /\ UNCHANGED gclock /\ (running' => running)
    BY <1>4 DEF ApplyTick
  <2>2. running => gclock <= Deadline(gtick)
    BY <1>0 DEF Watch
  <2>3. Deadline(gtick) <= Deadline(gtick + 1)
    BY <1>t, DeadlineMono DEF TypeOK
  <2>4. Deadline(gtick) \in Nat /\ Deadline(gtick + 1) \in Nat /\ gclock \in Nat
    BY <1>t, DeadlineType DEF TypeOK
  <2>5. Watch'
    BY <2>1, <2>2, <2>3, <2>4 DEF Watch
  <2> QED
    BY <1>0, <2>5 DEF InvWatch
<1>5. CASE GoAlone
  <2>1. running' = FALSE
    BY <1>5 DEF GoAlone
  <2> QED
    BY <1>0, <2>1 DEF InvWatch, Watch
<1>6. QED
  <2>1. CASE \/ Deliver
             \/ \E S \in Certs : TickCert(S) \/ RefuseTick(S) \/ Grant(S) \/ RefuseGrant(S)
             \/ UNCHANGED vars
    <3>1. UNCHANGED <<running, gclock, gtick>>
      BY <2>1 DEF Deliver, TickCert, RefuseTick, Grant, RefuseGrant, vars
    <3> QED
      BY <1>1, <3>1
  <2> QED
    BY <1>2, <1>3, <1>4, <1>5, <2>1 DEF Next

THEOREM WatchAlways ==
  ASSUME Mut # "M_NOWATCHDOG"
  PROVE  Spec => []InvWatch
<1>1. InvWatch /\ [Next]_vars => InvWatch'
  BY NextWatch
<1> QED
  BY InitWatch, <1>1, PTL DEF Spec

THEOREM ExtAlways ==
  ASSUME Mut # "M_NOEXTENT"
  PROVE  Spec => []InvExt
<1>1. InvExt /\ [Next]_vars => InvExt'
  BY NextExt
<1> QED
  BY InitExt, <1>1, PTL DEF Spec

LEMMA EntryFromInvs == InvExt /\ InvWatch => EntryEndsAtExtent
<1> SUFFICES ASSUME InvExt, InvWatch, running
             PROVE  /\ gtick < endAt
                    /\ gtick < start + MaxExtent
                    /\ gclock <= Deadline(gtick)
  BY DEF EntryEndsAtExtent
<1>1. TypeOK /\ RunExt /\ ExtBound /\ Watch
  BY DEF InvExt, InvWatch, Shape
<1>2. gtick < endAt /\ endAt <= start + MaxExtent
  BY <1>1 DEF RunExt, ExtBound
<1>3. gtick \in Nat /\ endAt \in Nat /\ start \in Nat
  BY <1>1 DEF TypeOK
<1> QED
  BY <1>1, <1>2, <1>3, MaxExtentNat DEF Watch

THEOREM EntryEndsAtExtentAlways ==
  ASSUME Mut # "M_NOEXTENT", Mut # "M_NOWATCHDOG"
  PROVE  Spec => []EntryEndsAtExtent
<1>1. Spec => []InvExt
  BY ExtAlways
<1>2. Spec => []InvWatch
  BY WatchAlways
<1> QED
  BY <1>1, <1>2, EntryFromInvs, PTL

LEMMA StretchFromWatch == InvWatch => NoStretchUnlessSlow
<1> SUFFICES ASSUME InvWatch, GovClass # "slow", running PROVE ~(now > Deadline(gtick))
  BY DEF NoStretchUnlessSlow, Stretched
<1>1. TypeOK /\ GovSound /\ Watch
  BY DEF InvWatch, Shape
<1>2. gclock >= now /\ gclock <= Deadline(gtick)
  BY <1>1 DEF GovSound, Watch
<1>3. gclock \in Nat /\ now \in Nat /\ Deadline(gtick) \in Nat
  BY <1>1, DeadlineType DEF TypeOK
<1> QED
  BY <1>2, <1>3

THEOREM NoStretchUnlessSlowAlways ==
  ASSUME Mut # "M_NOWATCHDOG"
  PROVE  Spec => []NoStretchUnlessSlow
<1>1. Spec => []InvWatch
  BY WatchAlways
<1> QED
  BY <1>1, StretchFromWatch, PTL
-----------------------------------------------------------------------------
THEOREM SafeAlways ==
  ASSUME Mut = "none"
  PROVE  Spec => []Safe
<1>1. Spec => []NoGrantPastExpiry
  BY NoGrantPastExpiryAlways
<1>2. Spec => []EntryEndsAtExtent
  BY EntryEndsAtExtentAlways
<1>3. Spec => []NoStretchUnlessSlow
  BY NoStretchUnlessSlowAlways
<1> QED
  BY <1>1, <1>2, <1>3, PTL DEF Safe
-----------------------------------------------------------------------------
(* Why the mutations must fail. The counterexamples are TLC's.                 *)

LEMMA MutOneClockAcceptsOneSigner ==
  ASSUME Mut = "M_ONECLOCK", NEW S, NEW y \in S, SignsGrant(y)
  PROVE  GrantOK(S)
  BY DEF GrantOK

LEMMA MutReceiptCountsFromDelivery ==
  ASSUME Mut = "M_RECEIPT", Deliver
  PROVE  expiry' = tick + D
  BY DEF Deliver

LEMMA MutRelativeTickReadsLastAt ==
  ASSUME Mut = "M_RELATIVETICK", NEW y
  PROVE  Due(y) = lastAt[y] + P
  BY DEF Due

LEMMA MutTooSlowWaivesThePremise ==
  ASSUME Cardinality(Captured \cup Slow) >= Cert, Cert \in Nat,
         IsFiniteSet(Captured \cup Slow)
  PROVE  Mut = "M_TOOSLOW"
<1>1. Cardinality(Captured \cup Slow) \in Nat
  BY FS_CardinalityType
<1> QED
  BY <1>1, ClockPremise

LEMMA MutNoExtentLoadsNoExtent ==
  ASSUME Mut = "M_NOEXTENT"
  PROVE  NoExtent \in Extents
  BY DEF Extents

LEMMA MutNoWatchdogHoldsNothing ==
  ASSUME Mut = "M_NOWATCHDOG", NEW g
  PROVE  ~WatchdogHolds(g)
  BY DEF WatchdogHolds
=============================================================================
