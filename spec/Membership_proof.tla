--------------------------- MODULE Membership_proof ---------------------------
(* TLAPS proof of the invariants of Membership.tla (ADR-0061 §7), for every    *)
(* capture floor and every set of captured replicas the module's assumptions   *)
(* admit, and every schedule. Membership.tla is not edited.                    *)
(*                                                                             *)
(*   THEOREM StepInScheduleAlways      [Mut # "M_OFFSCHEDULE"]                 *)
(*   THEOREM StepAtFloorAlways         [Mut # "M_BELOWFLOOR"]                  *)
(*   THEOREM StepByQuorumAlways        [Mut # "M_MINORITYSTEP"]                *)
(*   THEOREM AtMostOneSuccessorAlways  [Mut # "M_MINORITYSTEP",                *)
(*                                      Mut # "M_BELOWFLOOR",                  *)
(*                                      Mut # "M_TWOVOTES"]                    *)
(*   THEOREM SafeAlways                [Mut = "none"]                          *)
(*                                                                             *)
(* The strengthening. `Shape` holds under every mutation: the type invariant;  *)
(* a step drops a member of the membership it replaces and is signed from      *)
(* within it; and every honest signer of a step has a ballot for exactly that  *)
(* step, since ballots only accumulate. AtMostOneSuccessor then rests on three *)
(* more clauses: StepByQuorum; OneVote, an honest replica's ballots agree per  *)
(* membership; and ReachedAtFloor, every membership some path reaches still    *)
(* tolerates the floor. The step that adds a second step from a membership is  *)
(* refuted by QuorumIntersection: the two signer sets share a replica that is  *)
(* not captured, and it has a ballot for each drop.                            *)
(*                                                                             *)
(* QuorumIntersection is the counting: |A| + |B| = |A \cup B| + |A \cap B| <=  *)
(* n + |Captured| <= n + Floor <= n + f < 2 * Cert(n), if A \cap B were all    *)
(* captured. CapturedWithinFloor and FloorAtStart are the module's named       *)
(* assumptions.                                                                *)
(*                                                                             *)
(* Mutations and witnesses are behaviours and stay with TLC                    *)
(* (Membership-results-*.txt). Check: tools/tlapm --cleanfp --strict.          *)
EXTENDS Membership, FiniteSetTheorems, TLAPS

BallotRec == [voter : Replicas, from : SUBSET Replicas, drop : Replicas]
StepRec   == [from : SUBSET Replicas, drop : Replicas, signers : SUBSET Replicas]

TypeOK == votes \subseteq BallotRec /\ steps \subseteq StepRec

DropIn       == \A t1 \in steps : t1.drop \in t1.from /\ t1.signers \subseteq t1.from
SignersVoted == \A t2 \in steps : \A z \in t2.signers \ Captured : Ballot(z, t2.from, t2.drop) \in votes

Shape == TypeOK /\ DropIn /\ SignersVoted

OneVote == \A b1, b2 \in votes : (b1.voter = b2.voter /\ b1.from = b2.from) => b1.drop = b2.drop

ReachedAtFloor == \A k \in Reached : FOf(Cardinality(k)) >= Floor

\* The two shapes of a step of Next.
Signing  == \E m \in Reached : \E d \in m : \E r \in Replicas : Sign(r, m, d)
Ordering == \E m \in Reached : \E d \in m : \E A \in SUBSET m : Order(m, d, A)
-----------------------------------------------------------------------------
LEMMA NextForms == Next <=> Signing \/ Ordering
  BY DEF Next, Signing, Ordering

LEMMA ReplicasFinite == IsFiniteSet(Replicas)
<1>1. IsFiniteSet({"r1"})
  BY FS_Singleton
<1>2. IsFiniteSet({"r1"} \cup {"r2"})
  BY <1>1, FS_AddElement
<1>3. IsFiniteSet({"r1"} \cup {"r2"} \cup {"r3"})
  BY <1>2, FS_AddElement
<1>4. IsFiniteSet({"r1"} \cup {"r2"} \cup {"r3"} \cup {"r4"})
  BY <1>3, FS_AddElement
<1>5. IsFiniteSet({"r1"} \cup {"r2"} \cup {"r3"} \cup {"r4"} \cup {"r5"})
  BY <1>4, FS_AddElement
<1>6. Replicas = {"r1"} \cup {"r2"} \cup {"r3"} \cup {"r4"} \cup {"r5"}
  BY DEF Replicas
<1> QED
  BY <1>5, <1>6

LEMMA FiniteParts ==
  ASSUME NEW k \in SUBSET Replicas
  PROVE  IsFiniteSet(k) /\ Cardinality(k) \in Nat
  BY ReplicasFinite, FS_Subset, FS_CardinalityType

\* Arithmetic of §1, for a membership that has a member.
LEMMA CertFacts ==
  ASSUME NEW n \in Nat, n >= 1
  PROVE  /\ FOf(n) \in Nat
         /\ Cert(n) \in Nat
         /\ 2 * Cert(n) >= n + FOf(n) + 1
<1>1. FOf(n) \in Nat
  BY DEF FOf
<1>2. (n + FOf(n)) \div 2 \in Nat /\ 2 * ((n + FOf(n)) \div 2) >= n + FOf(n) - 1
  BY <1>1
<1> QED
  BY <1>1, <1>2 DEF Cert

LEMMA NonEmptySize ==
  ASSUME NEW k \in SUBSET Replicas, NEW d \in k
  PROVE  Cardinality(k) >= 1
<1>1. IsFiniteSet(k) /\ Cardinality(k) \in Nat
  BY FiniteParts
<1>2. k # {}
  OBVIOUS
<1>3. Cardinality(k) # 0
  BY <1>1, <1>2, FS_EmptySet
<1> QED
  BY <1>1, <1>3

LEMMA QuorumIntersection ==
  ASSUME NEW k \in SUBSET Replicas, NEW d \in k,
         NEW A1 \in SUBSET k, NEW A2 \in SUBSET k,
         Cardinality(A1) >= Cert(Cardinality(k)),
         Cardinality(A2) >= Cert(Cardinality(k)),
         FOf(Cardinality(k)) >= Floor
  PROVE  \E z \in A1 \cap A2 : z \notin Captured
<1> SUFFICES ASSUME A1 \cap A2 \subseteq Captured PROVE FALSE
  OBVIOUS
<1>1. /\ IsFiniteSet(k) /\ Cardinality(k) \in Nat
      /\ IsFiniteSet(A1) /\ Cardinality(A1) \in Nat
      /\ IsFiniteSet(A2) /\ Cardinality(A2) \in Nat
  BY FiniteParts
<1>2. Cardinality(k) >= 1
  BY NonEmptySize
<1>3. /\ Cert(Cardinality(k)) \in Nat /\ FOf(Cardinality(k)) \in Nat
      /\ 2 * Cert(Cardinality(k)) >= Cardinality(k) + FOf(Cardinality(k)) + 1
  BY <1>1, <1>2, CertFacts
<1>4. /\ IsFiniteSet(A1 \cup A2)
      /\ Cardinality(A1 \cup A2) = Cardinality(A1) + Cardinality(A2) - Cardinality(A1 \cap A2)
  BY <1>1, FS_Union
<1>5. A1 \cup A2 \in SUBSET k
  OBVIOUS
<1>6. Cardinality(A1 \cup A2) <= Cardinality(k)
  BY <1>1, <1>5, FS_Subset
<1>7. IsFiniteSet(Captured) /\ Cardinality(Captured) \in Nat
  BY CapturedWithinFloor, FiniteParts
<1>8. A1 \cap A2 \in SUBSET Captured
  OBVIOUS
<1>9. IsFiniteSet(A1 \cap A2) /\ Cardinality(A1 \cap A2) \in Nat
      /\ Cardinality(A1 \cap A2) <= Cardinality(Captured)
  BY <1>7, <1>8, FS_Subset, FS_CardinalityType
<1>10. Cardinality(A1 \cap A2) <= FOf(Cardinality(k))
  BY <1>3, <1>7, <1>9, CapturedWithinFloor, FloorAtStart
<1>11. Cardinality(A1 \cup A2) \in Nat
  BY <1>4, FS_CardinalityType
<1> HIDE DEF Cert, FOf
<1> QED
  BY <1>1, <1>3, <1>4, <1>6, <1>9, <1>10, <1>11
-----------------------------------------------------------------------------
LEMMA InitShape == Init => Shape
  BY DEF Init, Shape, TypeOK, DropIn, SignersVoted

LEMMA ReachedType ==
  ASSUME TypeOK PROVE Reached \subseteq SUBSET Replicas
  BY DEF TypeOK, StepRec, Reached

LEMMA SignFacts ==
  ASSUME NEW r, NEW m, NEW d, Sign(r, m, d)
  PROVE  /\ votes' = votes \cup {Ballot(r, m, d)}
         /\ steps' = steps
  BY DEF Sign

LEMMA OrderFacts ==
  ASSUME NEW m, NEW d, NEW A, Order(m, d, A)
  PROVE  /\ steps' = steps \cup {[from |-> m, drop |-> d, signers |-> A]}
         /\ votes' = votes
         /\ \A y \in A \ Captured : Ballot(y, m, d) \in votes
         /\ InSchedule(m)
         /\ AtFloor(m)
         /\ Enough(m, A)
  BY DEF Order

LEMMA NextShape == Shape /\ [Next]_vars => Shape'
<1> SUFFICES ASSUME Shape, [Next]_vars PROVE Shape'
  OBVIOUS
<1>0. TypeOK /\ DropIn /\ SignersVoted
  BY DEF Shape
<1>r. Reached \subseteq SUBSET Replicas
  BY <1>0, ReachedType
<1>1. CASE UNCHANGED vars
  BY <1>0, <1>1 DEF vars, Shape, TypeOK, DropIn, SignersVoted
<1>2. CASE Signing
  <2>1. PICK m \in Reached : \E d \in m : \E r \in Replicas : Sign(r, m, d)
    BY <1>2 DEF Signing
  <2>2. PICK d \in m : \E r \in Replicas : Sign(r, m, d)
    BY <2>1
  <2>3. PICK r \in Replicas : Sign(r, m, d)
    BY <2>2
  <2>4. votes' = votes \cup {Ballot(r, m, d)} /\ steps' = steps
    BY <2>3, SignFacts
  <2>5. Ballot(r, m, d) \in BallotRec
    BY <1>r DEF Ballot, BallotRec
  <2>6. TypeOK'
    BY <1>0, <2>4, <2>5 DEF TypeOK
  <2>7. DropIn'
    BY <1>0, <2>4 DEF DropIn
  <2>8. SignersVoted'
    BY <1>0, <2>4 DEF SignersVoted
  <2> QED
    BY <2>6, <2>7, <2>8 DEF Shape
<1>3. CASE Ordering
  <2>1. PICK m \in Reached : \E d \in m : \E A \in SUBSET m : Order(m, d, A)
    BY <1>3 DEF Ordering
  <2>2. PICK d \in m : \E A \in SUBSET m : Order(m, d, A)
    BY <2>1
  <2>3. PICK A \in SUBSET m : Order(m, d, A)
    BY <2>2
  <2> DEFINE n == [from |-> m, drop |-> d, signers |-> A]
  <2>4. /\ steps' = steps \cup {n}
        /\ votes' = votes
        /\ \A y \in A \ Captured : Ballot(y, m, d) \in votes
    BY <2>3, OrderFacts
  <2>5. n \in StepRec
    BY <1>r DEF StepRec
  <2>6. n.drop \in n.from /\ n.signers \subseteq n.from
    OBVIOUS
  <2>7. TypeOK'
    BY <1>0, <2>4, <2>5 DEF TypeOK
  <2>8. DropIn'
    <3> SUFFICES ASSUME NEW t \in steps' PROVE t.drop \in t.from /\ t.signers \subseteq t.from
      BY DEF DropIn
    <3>1. t \in steps \/ t = n
      BY <2>4
    <3> QED
      BY <1>0, <2>6, <3>1 DEF DropIn
  <2>9. SignersVoted'
    <3> SUFFICES ASSUME NEW t \in steps', NEW z \in t.signers \ Captured
                 PROVE  Ballot(z, t.from, t.drop) \in votes
      BY <2>4 DEF SignersVoted
    <3>1. t \in steps \/ t = n
      BY <2>4
    <3>2. CASE t \in steps
      BY <1>0, <3>2 DEF SignersVoted
    <3>3. CASE t = n
      BY <2>4, <3>3
    <3> QED
      BY <3>1, <3>2, <3>3
  <2> QED
    BY <2>7, <2>8, <2>9 DEF Shape
<1> QED
  BY <1>1, <1>2, <1>3, NextForms

THEOREM ShapeAlways == Spec => []Shape
<1>1. Shape /\ [Next]_vars => Shape'
  BY NextShape
<1> QED
  BY InitShape, <1>1, PTL DEF Spec
-----------------------------------------------------------------------------
(* The three guards at Order. Each property is over the append-only `steps`.   *)

LEMMA NextStepInSchedule ==
  ASSUME Mut # "M_OFFSCHEDULE", StepInSchedule, [Next]_vars
  PROVE  StepInSchedule'
<1>1. CASE UNCHANGED vars
  BY <1>1 DEF vars, StepInSchedule
<1>2. CASE Signing
  <2>1. PICK m \in Reached : \E d \in m : \E r \in Replicas : Sign(r, m, d)
    BY <1>2 DEF Signing
  <2>2. PICK d \in m : \E r \in Replicas : Sign(r, m, d)
    BY <2>1
  <2>3. PICK r \in Replicas : Sign(r, m, d)
    BY <2>2
  <2> QED
    BY <2>3, SignFacts DEF StepInSchedule
<1>3. CASE Ordering
  <2>1. PICK m \in Reached : \E d \in m : \E A \in SUBSET m : Order(m, d, A)
    BY <1>3 DEF Ordering
  <2>2. PICK d \in m : \E A \in SUBSET m : Order(m, d, A)
    BY <2>1
  <2>3. PICK A \in SUBSET m : Order(m, d, A)
    BY <2>2
  <2> DEFINE n == [from |-> m, drop |-> d, signers |-> A]
  <2>4. steps' = steps \cup {n} /\ InSchedule(m)
    BY <2>3, OrderFacts
  <2> SUFFICES ASSUME NEW t \in steps' PROVE Cardinality(t.from) - 1 \in Schedule
    BY DEF StepInSchedule
  <2>5. t \in steps \/ t = n
    BY <2>4
  <2> QED
    BY <2>4, <2>5 DEF StepInSchedule, InSchedule
<1> QED
  BY <1>1, <1>2, <1>3, NextForms

THEOREM StepInScheduleAlways ==
  ASSUME Mut # "M_OFFSCHEDULE"
  PROVE  Spec => []StepInSchedule
<1>1. StepInSchedule /\ [Next]_vars => StepInSchedule'
  BY NextStepInSchedule
<1>2. Init => StepInSchedule
  BY DEF Init, StepInSchedule
<1> QED
  BY <1>1, <1>2, PTL DEF Spec

LEMMA NextStepAtFloor ==
  ASSUME Mut # "M_BELOWFLOOR", StepAtFloor, [Next]_vars
  PROVE  StepAtFloor'
<1>1. CASE UNCHANGED vars
  BY <1>1 DEF vars, StepAtFloor
<1>2. CASE Signing
  <2>1. PICK m \in Reached : \E d \in m : \E r \in Replicas : Sign(r, m, d)
    BY <1>2 DEF Signing
  <2>2. PICK d \in m : \E r \in Replicas : Sign(r, m, d)
    BY <2>1
  <2>3. PICK r \in Replicas : Sign(r, m, d)
    BY <2>2
  <2> QED
    BY <2>3, SignFacts DEF StepAtFloor
<1>3. CASE Ordering
  <2>1. PICK m \in Reached : \E d \in m : \E A \in SUBSET m : Order(m, d, A)
    BY <1>3 DEF Ordering
  <2>2. PICK d \in m : \E A \in SUBSET m : Order(m, d, A)
    BY <2>1
  <2>3. PICK A \in SUBSET m : Order(m, d, A)
    BY <2>2
  <2> DEFINE n == [from |-> m, drop |-> d, signers |-> A]
  <2>4. steps' = steps \cup {n} /\ AtFloor(m)
    BY <2>3, OrderFacts
  <2> SUFFICES ASSUME NEW t \in steps' PROVE FOf(Cardinality(t.from) - 1) >= Floor
    BY DEF StepAtFloor
  <2>5. t \in steps \/ t = n
    BY <2>4
  <2> QED
    BY <2>4, <2>5 DEF StepAtFloor, AtFloor
<1> QED
  BY <1>1, <1>2, <1>3, NextForms

THEOREM StepAtFloorAlways ==
  ASSUME Mut # "M_BELOWFLOOR"
  PROVE  Spec => []StepAtFloor
<1>1. StepAtFloor /\ [Next]_vars => StepAtFloor'
  BY NextStepAtFloor
<1>2. Init => StepAtFloor
  BY DEF Init, StepAtFloor
<1> QED
  BY <1>1, <1>2, PTL DEF Spec

InvQuorum == Shape /\ StepByQuorum

\* A step's certificate, read off Enough when M_MINORITYSTEP is absent.
LEMMA EnoughIsCert ==
  ASSUME Mut # "M_MINORITYSTEP", NEW k \in SUBSET Replicas, NEW d \in k, NEW A, Enough(k, A)
  PROVE  Cardinality(A) >= Cert(Cardinality(k))
<1>1. Cardinality(k) \in Nat /\ Cardinality(k) >= 1
  BY FiniteParts, NonEmptySize
<1>2. Cert(Cardinality(k)) \in Nat
  BY <1>1, CertFacts
<1> HIDE DEF Cert
<1> QED
  BY <1>2 DEF Enough

LEMMA NextStepByQuorum ==
  ASSUME Mut # "M_MINORITYSTEP", InvQuorum, [Next]_vars
  PROVE  InvQuorum'
<1>0. Shape /\ Shape' /\ StepByQuorum
  BY NextShape DEF InvQuorum
<1>r. Reached \subseteq SUBSET Replicas
  BY <1>0, ReachedType DEF Shape
<1>1. CASE UNCHANGED vars
  BY <1>0, <1>1 DEF vars, InvQuorum, StepByQuorum
<1>2. CASE Signing
  <2>1. PICK m \in Reached : \E d \in m : \E r \in Replicas : Sign(r, m, d)
    BY <1>2 DEF Signing
  <2>2. PICK d \in m : \E r \in Replicas : Sign(r, m, d)
    BY <2>1
  <2>3. PICK r \in Replicas : Sign(r, m, d)
    BY <2>2
  <2> QED
    BY <1>0, <2>3, SignFacts DEF InvQuorum, StepByQuorum
<1>3. CASE Ordering
  <2>1. PICK m \in Reached : \E d \in m : \E A \in SUBSET m : Order(m, d, A)
    BY <1>3 DEF Ordering
  <2>2. PICK d \in m : \E A \in SUBSET m : Order(m, d, A)
    BY <2>1
  <2>3. PICK A \in SUBSET m : Order(m, d, A)
    BY <2>2
  <2> DEFINE n == [from |-> m, drop |-> d, signers |-> A]
  <2>4. steps' = steps \cup {n} /\ Enough(m, A)
    BY <2>3, OrderFacts
  <2>5. m \in SUBSET Replicas
    BY <1>r
  <2>6. Cardinality(A) >= Cert(Cardinality(m))
    BY <2>2, <2>4, <2>5, EnoughIsCert
  <2>7. StepByQuorum'
    <3> SUFFICES ASSUME NEW t \in steps' PROVE Cardinality(t.signers) >= Cert(Cardinality(t.from))
      BY DEF StepByQuorum
    <3>1. t \in steps \/ t = n
      BY <2>4
    <3> QED
      BY <1>0, <2>6, <3>1 DEF StepByQuorum
  <2> QED
    BY <1>0, <2>7 DEF InvQuorum
<1> QED
  BY <1>1, <1>2, <1>3, NextForms

THEOREM StepByQuorumAlways ==
  ASSUME Mut # "M_MINORITYSTEP"
  PROVE  Spec => []StepByQuorum
<1>1. InvQuorum /\ [Next]_vars => InvQuorum'
  BY NextStepByQuorum
<1>2. Init => InvQuorum
  BY InitShape DEF Init, InvQuorum, StepByQuorum
<1>3. InvQuorum => StepByQuorum
  BY DEF InvQuorum
<1> QED
  BY <1>1, <1>2, <1>3, PTL DEF Spec
-----------------------------------------------------------------------------
(* AtMostOneSuccessor: a second step from a membership is refuted through an   *)
(* honest replica common to the two certificates.                              *)

InvOne == Shape /\ StepByQuorum /\ OneVote /\ ReachedAtFloor /\ AtMostOneSuccessor

LEMMA InitInvOne == Init => InvOne
<1> SUFFICES ASSUME Init PROVE InvOne
  OBVIOUS
<1>1. Shape
  BY InitShape
<1>2. Reached = {Replicas}
  BY DEF Init, Reached
<1>3. ReachedAtFloor
  BY <1>2, FloorAtStart DEF ReachedAtFloor
<1>4. StepByQuorum /\ OneVote /\ AtMostOneSuccessor
  BY DEF Init, StepByQuorum, OneVote, AtMostOneSuccessor
<1> QED
  BY <1>1, <1>3, <1>4 DEF InvOne

\* Two steps from a reached membership carry the same drop, whichever two they are.
LEMMA TwoCertificates ==
  ASSUME NEW k \in SUBSET Replicas, NEW d1 \in k, NEW d2 \in k,
         NEW A1 \in SUBSET k, NEW A2 \in SUBSET k,
         Cardinality(A1) >= Cert(Cardinality(k)),
         Cardinality(A2) >= Cert(Cardinality(k)),
         FOf(Cardinality(k)) >= Floor,
         \A y \in A1 \ Captured : Ballot(y, k, d1) \in votes,
         \A y \in A2 \ Captured : Ballot(y, k, d2) \in votes,
         OneVote
  PROVE  d1 = d2
<1>1. PICK z \in A1 \cap A2 : z \notin Captured
  BY QuorumIntersection
<1>2. Ballot(z, k, d1) \in votes /\ Ballot(z, k, d2) \in votes
  BY <1>1
<1> QED
  BY <1>2 DEF OneVote, Ballot

LEMMA NextInvOne ==
  ASSUME Mut # "M_MINORITYSTEP", Mut # "M_BELOWFLOOR", Mut # "M_TWOVOTES", InvOne, [Next]_vars
  PROVE  InvOne'
<1>0. /\ Shape /\ Shape' /\ StepByQuorum /\ OneVote /\ ReachedAtFloor /\ AtMostOneSuccessor
  BY NextShape DEF InvOne
<1>a. TypeOK /\ DropIn /\ SignersVoted
  BY <1>0 DEF Shape
<1>r. Reached \subseteq SUBSET Replicas
  BY <1>a, ReachedType
<1>q. StepByQuorum'
  <2>1. InvQuorum
    BY <1>0 DEF InvQuorum
  <2>2. InvQuorum'
    BY <2>1, NextStepByQuorum
  <2> QED
    BY <2>2 DEF InvQuorum
<1>1. CASE UNCHANGED vars
  <2>1. OneVote' /\ ReachedAtFloor' /\ AtMostOneSuccessor'
    BY <1>0, <1>1 DEF vars, OneVote, ReachedAtFloor, AtMostOneSuccessor, Reached
  <2> QED
    BY <1>0, <1>q, <2>1 DEF InvOne
<1>2. CASE Signing
  <2>1. PICK m \in Reached : \E d \in m : \E r \in Replicas : Sign(r, m, d)
    BY <1>2 DEF Signing
  <2>2. PICK d \in m : \E r \in Replicas : Sign(r, m, d)
    BY <2>1
  <2>3. PICK r \in Replicas : Sign(r, m, d)
    BY <2>2
  <2> DEFINE n == Ballot(r, m, d)
  <2>4. /\ votes' = votes \cup {n} /\ steps' = steps
        /\ ~\E b \in votes : b.voter = r /\ b.from = m
    BY <2>3, SignFacts DEF Sign, FirstVote
  <2>5. n.voter = r /\ n.from = m /\ n.drop = d
    BY DEF Ballot
  <2>6. OneVote'
    <3> SUFFICES ASSUME NEW b1 \in votes', NEW b2 \in votes', b1.voter = b2.voter, b1.from = b2.from
                 PROVE  b1.drop = b2.drop
      BY DEF OneVote
    <3>1. b1 \in votes \/ b1 = n
      BY <2>4
    <3>2. b2 \in votes \/ b2 = n
      BY <2>4
    <3> QED
      BY <1>0, <2>4, <2>5, <3>1, <3>2 DEF OneVote
  <2>7. ReachedAtFloor' /\ AtMostOneSuccessor'
    BY <1>0, <2>4 DEF ReachedAtFloor, AtMostOneSuccessor, Reached
  <2> QED
    BY <1>0, <1>q, <2>6, <2>7 DEF InvOne
<1>3. CASE Ordering
  <2>1. PICK m \in Reached : \E d \in m : \E A \in SUBSET m : Order(m, d, A)
    BY <1>3 DEF Ordering
  <2>2. PICK d \in m : \E A \in SUBSET m : Order(m, d, A)
    BY <2>1
  <2>3. PICK A \in SUBSET m : Order(m, d, A)
    BY <2>2
  <2> DEFINE n == [from |-> m, drop |-> d, signers |-> A]
  <2>4. /\ steps' = steps \cup {n}
        /\ votes' = votes
        /\ \A y \in A \ Captured : Ballot(y, m, d) \in votes
        /\ AtFloor(m)
        /\ Enough(m, A)
    BY <2>3, OrderFacts
  <2>5. m \in SUBSET Replicas
    BY <1>r
  <2>6. Cardinality(A) >= Cert(Cardinality(m))
    BY <2>2, <2>4, <2>5, EnoughIsCert
  <2>7. FOf(Cardinality(m) - 1) >= Floor
    BY <2>4 DEF AtFloor
  <2>8. FOf(Cardinality(m)) >= Floor
    BY <1>0 DEF ReachedAtFloor
  <2>9. OneVote'
    BY <1>0, <2>4 DEF OneVote
  <2>10. ReachedAtFloor'
    <3> SUFFICES ASSUME NEW k \in Reached' PROVE FOf(Cardinality(k)) >= Floor
      BY DEF ReachedAtFloor
    <3>1. k \in Reached \/ k = m \ {d}
      BY <2>4 DEF Reached
    <3>2. CASE k \in Reached
      BY <1>0, <3>2 DEF ReachedAtFloor
    <3>3. CASE k = m \ {d}
      <4>1. IsFiniteSet(m)
        BY <2>5, FiniteParts
      <4>2. Cardinality(m \ {d}) = Cardinality(m) - 1
        BY <2>2, <4>1, FS_RemoveElement
      <4> QED
        BY <2>7, <3>3, <4>2
    <3> QED
      BY <3>1, <3>2, <3>3
  <2>11. AtMostOneSuccessor'
    \* An old step from m carries the drop of the new one; everything else is the old invariant.
    <3>1. ASSUME NEW t \in steps, t.from = m PROVE t.drop = d
      <4>1. t.drop \in m /\ t.signers \in SUBSET m
        BY <1>a, <3>1 DEF DropIn
      <4>2. Cardinality(t.signers) >= Cert(Cardinality(m))
        BY <1>0, <3>1 DEF StepByQuorum
      <4>3. \A y \in t.signers \ Captured : Ballot(y, m, t.drop) \in votes
        BY <1>a, <3>1 DEF SignersVoted
      <4>4. OneVote
        BY <1>0
      <4> QED
        BY <2>2, <2>4, <2>5, <2>6, <2>8, <4>1, <4>2, <4>3, <4>4, TwoCertificates
    <3> SUFFICES ASSUME NEW s1 \in steps', NEW s2 \in steps', s1.from = s2.from
                 PROVE  s1.drop = s2.drop
      BY DEF AtMostOneSuccessor
    <3>2. s1 \in steps \/ s1 = n
      BY <2>4
    <3>3. s2 \in steps \/ s2 = n
      BY <2>4
    <3> QED
      BY <1>0, <3>1, <3>2, <3>3 DEF AtMostOneSuccessor
  <2> QED
    BY <1>0, <1>q, <2>9, <2>10, <2>11 DEF InvOne
<1> QED
  BY <1>1, <1>2, <1>3, NextForms

THEOREM AtMostOneSuccessorAlways ==
  ASSUME Mut # "M_MINORITYSTEP", Mut # "M_BELOWFLOOR", Mut # "M_TWOVOTES"
  PROVE  Spec => []AtMostOneSuccessor
<1>1. InvOne /\ [Next]_vars => InvOne'
  BY NextInvOne
<1>2. InvOne => AtMostOneSuccessor
  BY DEF InvOne
<1> QED
  BY InitInvOne, <1>1, <1>2, PTL DEF Spec
-----------------------------------------------------------------------------
THEOREM SafeAlways ==
  ASSUME Mut = "none"
  PROVE  Spec => []Safe
<1>1. Spec => []StepInSchedule
  BY StepInScheduleAlways
<1>2. Spec => []StepAtFloor
  BY StepAtFloorAlways
<1>3. Spec => []StepByQuorum
  BY StepByQuorumAlways
<1>4. Spec => []AtMostOneSuccessor
  BY AtMostOneSuccessorAlways
<1> QED
  BY <1>1, <1>2, <1>3, <1>4, PTL DEF Safe, OneSuccessor
-----------------------------------------------------------------------------
(* Why the mutations must fail. The counterexamples are TLC's.                 *)

LEMMA MutMinorityTakesOneFewer ==
  ASSUME Mut = "M_MINORITYSTEP", NEW k \in SUBSET Replicas, NEW d \in k, NEW A,
         Cardinality(A) >= Cert(Cardinality(k)) - 1
  PROVE  Enough(k, A)
  BY DEF Enough

LEMMA MutBelowFloorAdmitsAny ==
  ASSUME Mut = "M_BELOWFLOOR", NEW k
  PROVE  AtFloor(k)
  BY DEF AtFloor

LEMMA MutOffScheduleAdmitsAny ==
  ASSUME Mut = "M_OFFSCHEDULE", NEW k
  PROVE  InSchedule(k)
  BY DEF InSchedule

LEMMA MutTwoVotesAdmitsAny ==
  ASSUME Mut = "M_TWOVOTES", NEW r, NEW k
  PROVE  FirstVote(r, k)
  BY DEF FirstVote
=============================================================================
