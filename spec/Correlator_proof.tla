------------------------- MODULE Correlator_proof -------------------------
(* TLAPS proofs of the eight invariants Correlator.tla states (ADR-0051,         *)
(* Proposed: the correlator's detection function), for every set of Thinkers,    *)
(* shared targets and correlators, every set of honest correlators, and every    *)
(* bound:                                                                        *)
(*                                                                               *)
(*   CarriedCoversSplitPathAlways  (Mut \notin {"M_ROUNDSCOPE", "M_ONEHOP"})     *)
(*   FindingHasEvidenceAlways      (Mut # "M_BARE")                              *)
(*   IngressReachIsSharedAlways    (Mut # "M_DOMAIN")                            *)
(*   SilenceIsCountedAlways        (Mut # "M_SELF")                              *)
(*   MissIsOnACorrelationAlways    (Mut # "M_TIERLESS")                          *)
(*   HonestNeverChargedAlways      (Mut \notin {"M_BARE", "M_TIERLESS"})         *)
(*   StoreWithinRecordAlways       (Mut # "M_KEEP")                              *)
(*   LagNeverGatesAlways           (Mut # "M_COUPLE")                            *)
(*   SafeAlways == Spec => []Safe  (Mut = "none")                                *)
(*                                                                               *)
(* Each theorem takes as hypothesis only the mutations that break it.            *)
(*                                                                               *)
(* No assumption is made on the constants: Thinkers, Stores, Corrs and Honest    *)
(* may be any sets and MaxRound, MaxSends and MMiss any values, where TLC ran    *)
(* two Thinkers, one or two targets, two correlators of which one is honest,     *)
(* two rounds and one send.                                                      *)
(*                                                                               *)
(* The inductive invariants. A type invariant, under every mutation.             *)
(* CarriedCoversSplitPath rests on two: `Ghost`, that the fold's value covers    *)
(* the ghost truth (a tainted target is carried or forgotten; a tainted context  *)
(* is effective or lost; every send was recorded so), and `HonestFolded`, that   *)
(* an honest correlator's mark has passed only sends it found or sends the fold  *)
(* did not fire on. HonestNeverCharged adds `CitedFired`, that every finding     *)
(* cites a send the fold fired on. StoreWithinRecord adds `ErasedArePast`, that  *)
(* an erased round is below its Thinker's current one. The rest are inductive    *)
(* alone, and LagNeverGates is true in every state and needs no induction.       *)
(*                                                                               *)
(* Correlator.tla is not edited; this module extends it. The mutations and the   *)
(* witnesses stay with TLC; the lemmas at the end say what each mutation admits. *)
(*                                                                               *)
(* Check with:  ../tools/tlapm Correlator_proof.tla   (from spec/; see           *)
(*              proof-results.sh for the results file)                           *)
EXTENDS Correlator, TLAPS

TypeOK ==
  /\ round \in [Thinkers -> Nat]
  /\ clearU \in [Thinkers -> BOOLEAN]
  /\ effU \in [Thinkers -> BOOLEAN]
  /\ tainted \in [Thinkers -> BOOLEAN]
  /\ lost \in [Thinkers -> BOOLEAN]
  /\ storeTaint \in [Stores -> BOOLEAN]
  /\ forgot \in [Stores -> BOOLEAN]
  /\ erased \subseteq [who : Thinkers, round : Nat]
  /\ marked \in [Corrs -> SUBSET sends]

\* The fold covers the ghost truth.
StoreTracked   == \A x \in Stores : storeTaint[x] => Carried(x) \/ forgot[x]
ContextTracked == \A t \in Thinkers : tainted[t] => effU[t] \/ lost[t]
SendTracked    == \A s \in sends : s.tainted => s.eff \/ s.lost
Ghost == StoreTracked /\ ContextTracked /\ SendTracked

\* An honest correlator's mark has passed only what it found or what did not fire.
HonestFolded == \A c \in Honest \cap Corrs : \A s \in marked[c] : Has(c, s) \/ ~s.eff

\* Every `carried-label` finding cites a send the fold fired on.
CitedFired == \A f \in carriedF : f.cite.eff

\* An erased round is below its Thinker's current round.
ErasedArePast == \A k \in erased : k.round < round[k.who]

-----------------------------------------------------------------------------
(* The type invariant, under every mutation.                                     *)

LEMMA TypeInit == Init => TypeOK
BY DEF Init, TypeOK

LEMMA TypeNext ==
    ASSUME TypeOK, [Next]_vars
    PROVE  TypeOK'
<1> USE DEF TypeOK
<1>1. CASE UNCHANGED vars
    BY <1>1 DEF vars
<1>2. ASSUME NEW t \in Thinkers, NEW i \in Items, NEW bad \in BOOLEAN, Read(t, i, bad) PROVE TypeOK'
    BY <1>2 DEF Read
<1>3. ASSUME NEW t \in Thinkers, NEW x \in Stores, Touch(t, x) PROVE TypeOK'
    BY <1>3 DEF Touch, Carried
<1>4. ASSUME NEW t \in Thinkers, Send(t) PROVE TypeOK'
    BY <1>4 DEF Send
<1>5. ASSUME NEW t \in Thinkers, EndRound(t) PROVE TypeOK'
    BY <1>5 DEF EndRound
<1>6. ASSUME NEW t \in Thinkers, NEW r \in 1..MaxRound, Erase(t, r) PROVE TypeOK'
    BY <1>6 DEF Erase
<1>7. ASSUME NEW t \in Thinkers, NEW i \in Items, ObsFind(t, i) PROVE TypeOK'
    BY <1>7 DEF ObsFind
<1>8. ASSUME NEW c \in Corrs, NEW s \in sends, Report(c, s) PROVE TypeOK'
    BY <1>8 DEF Report
<1>9. ASSUME NEW c \in Corrs, NEW s \in sends, Pass(c, s) PROVE TypeOK'
    BY <1>9 DEF Pass
<1>10. ASSUME NEW c \in Corrs, NEW i \in Items, Propagate(c, i) PROVE TypeOK'
    BY <1>10 DEF Propagate
<1>11. ASSUME NEW c \in Corrs, NEW q \in Corrs, Name(c, q) PROVE TypeOK'
    BY <1>11 DEF Name
<1> QED
    BY <1>1, <1>2, <1>3, <1>4, <1>5, <1>6, <1>7, <1>8, <1>9, <1>10, <1>11 DEF Next

THEOREM TypeAlways == Spec => []TypeOK
<1>1. TypeOK /\ [Next]_vars => TypeOK'
    BY TypeNext
<1> QED
    BY <1>1, TypeInit, PTL DEF Spec

-----------------------------------------------------------------------------
(* The fold covers the ghost truth: what CarriedCoversSplitPath rests on.        *)

LEMMA GhostNext ==
    ASSUME Mut \notin {"M_ROUNDSCOPE", "M_ONEHOP"}, TypeOK, Ghost, [Next]_vars
    PROVE  Ghost'
<1> USE DEF Ghost, StoreTracked, ContextTracked, SendTracked, Carried, TypeOK
<1>1. CASE UNCHANGED vars
    BY <1>1 DEF vars
<1>2. ASSUME NEW t \in Thinkers, NEW i \in Items, NEW bad \in BOOLEAN, Read(t, i, bad) PROVE Ghost'
    BY <1>2 DEF Read
<1>3. ASSUME NEW t \in Thinkers, NEW x \in Stores, Touch(t, x) PROVE Ghost'
    BY <1>3 DEF Touch, Out
<1>4. ASSUME NEW t \in Thinkers, Send(t) PROVE Ghost'
    BY <1>4 DEF Send
<1>5. ASSUME NEW t \in Thinkers, EndRound(t) PROVE Ghost'
    BY <1>5 DEF EndRound
<1>6. ASSUME NEW t \in Thinkers, NEW r \in 1..MaxRound, Erase(t, r) PROVE Ghost'
    BY <1>6 DEF Erase
<1>7. ASSUME NEW t \in Thinkers, NEW i \in Items, ObsFind(t, i) PROVE Ghost'
    BY <1>7 DEF ObsFind
<1>8. ASSUME NEW c \in Corrs, NEW s \in sends, Report(c, s) PROVE Ghost'
    BY <1>8 DEF Report
<1>9. ASSUME NEW c \in Corrs, NEW s \in sends, Pass(c, s) PROVE Ghost'
    BY <1>9 DEF Pass
<1>10. ASSUME NEW c \in Corrs, NEW i \in Items, Propagate(c, i) PROVE Ghost'
    BY <1>10 DEF Propagate
<1>11. ASSUME NEW c \in Corrs, NEW q \in Corrs, Name(c, q) PROVE Ghost'
    BY <1>11 DEF Name
<1> QED
    BY <1>1, <1>2, <1>3, <1>4, <1>5, <1>6, <1>7, <1>8, <1>9, <1>10, <1>11 DEF Next

LEMMA HonestFoldedNext ==
    ASSUME TypeOK, HonestFolded, [Next]_vars
    PROVE  HonestFolded'
<1> USE DEF HonestFolded, Has, TypeOK
<1>1. CASE UNCHANGED vars
    BY <1>1 DEF vars
<1>2. ASSUME NEW t \in Thinkers, NEW i \in Items, NEW bad \in BOOLEAN, Read(t, i, bad) PROVE HonestFolded'
    BY <1>2 DEF Read
<1>3. ASSUME NEW t \in Thinkers, NEW x \in Stores, Touch(t, x) PROVE HonestFolded'
    BY <1>3 DEF Touch
<1>4. ASSUME NEW t \in Thinkers, Send(t) PROVE HonestFolded'
    BY <1>4 DEF Send
<1>5. ASSUME NEW t \in Thinkers, EndRound(t) PROVE HonestFolded'
    BY <1>5 DEF EndRound
<1>6. ASSUME NEW t \in Thinkers, NEW r \in 1..MaxRound, Erase(t, r) PROVE HonestFolded'
    BY <1>6 DEF Erase
<1>7. ASSUME NEW t \in Thinkers, NEW i \in Items, ObsFind(t, i) PROVE HonestFolded'
    BY <1>7 DEF ObsFind
<1>8. ASSUME NEW c \in Corrs, NEW s \in sends, Report(c, s) PROVE HonestFolded'
    BY <1>8 DEF Report
<1>9. ASSUME NEW c \in Corrs, NEW s \in sends, Pass(c, s) PROVE HonestFolded'
    BY <1>9 DEF Pass
<1>10. ASSUME NEW c \in Corrs, NEW i \in Items, Propagate(c, i) PROVE HonestFolded'
    BY <1>10 DEF Propagate
<1>11. ASSUME NEW c \in Corrs, NEW q \in Corrs, Name(c, q) PROVE HonestFolded'
    BY <1>11 DEF Name
<1> QED
    BY <1>1, <1>2, <1>3, <1>4, <1>5, <1>6, <1>7, <1>8, <1>9, <1>10, <1>11 DEF Next

-----------------------------------------------------------------------------
(* The properties that are inductive alone.                                      *)

LEMMA EvidenceNext ==
    ASSUME Mut # "M_BARE", FindingHasEvidence, [Next]_vars
    PROVE  FindingHasEvidence'
<1> USE DEF FindingHasEvidence
<1>1. CASE UNCHANGED vars
    BY <1>1 DEF vars
<1>2. ASSUME NEW t \in Thinkers, NEW i \in Items, NEW bad \in BOOLEAN, Read(t, i, bad) PROVE FindingHasEvidence'
    BY <1>2 DEF Read
<1>3. ASSUME NEW t \in Thinkers, NEW x \in Stores, Touch(t, x) PROVE FindingHasEvidence'
    BY <1>3 DEF Touch
<1>4. ASSUME NEW t \in Thinkers, Send(t) PROVE FindingHasEvidence'
    BY <1>4 DEF Send
<1>5. ASSUME NEW t \in Thinkers, EndRound(t) PROVE FindingHasEvidence'
    BY <1>5 DEF EndRound
<1>6. ASSUME NEW t \in Thinkers, NEW r \in 1..MaxRound, Erase(t, r) PROVE FindingHasEvidence'
    BY <1>6 DEF Erase
<1>7. ASSUME NEW t \in Thinkers, NEW i \in Items, ObsFind(t, i) PROVE FindingHasEvidence'
    BY <1>7 DEF ObsFind
<1>8. ASSUME NEW c \in Corrs, NEW s \in sends, Report(c, s) PROVE FindingHasEvidence'
    BY <1>8 DEF Report
<1>9. ASSUME NEW c \in Corrs, NEW s \in sends, Pass(c, s) PROVE FindingHasEvidence'
    BY <1>9 DEF Pass
<1>10. ASSUME NEW c \in Corrs, NEW i \in Items, Propagate(c, i) PROVE FindingHasEvidence'
    BY <1>10 DEF Propagate
<1>11. ASSUME NEW c \in Corrs, NEW q \in Corrs, Name(c, q) PROVE FindingHasEvidence'
    BY <1>11 DEF Name
<1> QED
    BY <1>1, <1>2, <1>3, <1>4, <1>5, <1>6, <1>7, <1>8, <1>9, <1>10, <1>11 DEF Next

LEMMA ReachNext ==
    ASSUME Mut # "M_DOMAIN", IngressReachIsShared, [Next]_vars
    PROVE  IngressReachIsShared'
<1> USE DEF IngressReachIsShared
<1>1. CASE UNCHANGED vars
    BY <1>1 DEF vars
<1>2. ASSUME NEW t \in Thinkers, NEW i \in Items, NEW bad \in BOOLEAN, Read(t, i, bad) PROVE IngressReachIsShared'
    BY <1>2 DEF Read
<1>3. ASSUME NEW t \in Thinkers, NEW x \in Stores, Touch(t, x) PROVE IngressReachIsShared'
    BY <1>3 DEF Touch
<1>4. ASSUME NEW t \in Thinkers, Send(t) PROVE IngressReachIsShared'
    BY <1>4 DEF Send
<1>5. ASSUME NEW t \in Thinkers, EndRound(t) PROVE IngressReachIsShared'
    BY <1>5 DEF EndRound
<1>6. ASSUME NEW t \in Thinkers, NEW r \in 1..MaxRound, Erase(t, r) PROVE IngressReachIsShared'
    BY <1>6 DEF Erase
<1>7. ASSUME NEW t \in Thinkers, NEW i \in Items, ObsFind(t, i) PROVE IngressReachIsShared'
    BY <1>7 DEF ObsFind
<1>8. ASSUME NEW c \in Corrs, NEW s \in sends, Report(c, s) PROVE IngressReachIsShared'
    BY <1>8 DEF Report
<1>9. ASSUME NEW c \in Corrs, NEW s \in sends, Pass(c, s) PROVE IngressReachIsShared'
    BY <1>9 DEF Pass
<1>10. ASSUME NEW c \in Corrs, NEW i \in Items, Propagate(c, i) PROVE IngressReachIsShared'
    BY <1>10 DEF Propagate
<1>11. ASSUME NEW c \in Corrs, NEW q \in Corrs, Name(c, q) PROVE IngressReachIsShared'
    BY <1>11 DEF Name
<1> QED
    BY <1>1, <1>2, <1>3, <1>4, <1>5, <1>6, <1>7, <1>8, <1>9, <1>10, <1>11 DEF Next

LEMMA SilenceNext ==
    ASSUME Mut # "M_SELF", TypeOK, SilenceIsCounted, [Next]_vars
    PROVE  SilenceIsCounted'
<1> USE DEF SilenceIsCounted, Has, TypeOK
<1>1. CASE UNCHANGED vars
    BY <1>1 DEF vars
<1>2. ASSUME NEW t \in Thinkers, NEW i \in Items, NEW bad \in BOOLEAN, Read(t, i, bad) PROVE SilenceIsCounted'
    BY <1>2 DEF Read
<1>3. ASSUME NEW t \in Thinkers, NEW x \in Stores, Touch(t, x) PROVE SilenceIsCounted'
    BY <1>3 DEF Touch
<1>4. ASSUME NEW t \in Thinkers, Send(t) PROVE SilenceIsCounted'
    BY <1>4 DEF Send
<1>5. ASSUME NEW t \in Thinkers, EndRound(t) PROVE SilenceIsCounted'
    BY <1>5 DEF EndRound
<1>6. ASSUME NEW t \in Thinkers, NEW r \in 1..MaxRound, Erase(t, r) PROVE SilenceIsCounted'
    BY <1>6 DEF Erase
<1>7. ASSUME NEW t \in Thinkers, NEW i \in Items, ObsFind(t, i) PROVE SilenceIsCounted'
    BY <1>7 DEF ObsFind
<1>8. ASSUME NEW c \in Corrs, NEW s \in sends, Report(c, s) PROVE SilenceIsCounted'
    BY <1>8 DEF Report
<1>9. ASSUME NEW c \in Corrs, NEW s \in sends, Pass(c, s) PROVE SilenceIsCounted'
    BY <1>9 DEF Pass
<1>10. ASSUME NEW c \in Corrs, NEW i \in Items, Propagate(c, i) PROVE SilenceIsCounted'
    BY <1>10 DEF Propagate
<1>11. ASSUME NEW c \in Corrs, NEW q \in Corrs, Name(c, q) PROVE SilenceIsCounted'
    BY <1>11 DEF Name
<1> QED
    BY <1>1, <1>2, <1>3, <1>4, <1>5, <1>6, <1>7, <1>8, <1>9, <1>10, <1>11 DEF Next

LEMMA TierNext ==
    ASSUME Mut # "M_TIERLESS", MissIsOnACorrelation, [Next]_vars
    PROVE  MissIsOnACorrelation'
<1> USE DEF MissIsOnACorrelation
<1>1. CASE UNCHANGED vars
    BY <1>1 DEF vars
<1>2. ASSUME NEW t \in Thinkers, NEW i \in Items, NEW bad \in BOOLEAN, Read(t, i, bad) PROVE MissIsOnACorrelation'
    BY <1>2 DEF Read
<1>3. ASSUME NEW t \in Thinkers, NEW x \in Stores, Touch(t, x) PROVE MissIsOnACorrelation'
    BY <1>3 DEF Touch
<1>4. ASSUME NEW t \in Thinkers, Send(t) PROVE MissIsOnACorrelation'
    BY <1>4 DEF Send
<1>5. ASSUME NEW t \in Thinkers, EndRound(t) PROVE MissIsOnACorrelation'
    BY <1>5 DEF EndRound
<1>6. ASSUME NEW t \in Thinkers, NEW r \in 1..MaxRound, Erase(t, r) PROVE MissIsOnACorrelation'
    BY <1>6 DEF Erase
<1>7. ASSUME NEW t \in Thinkers, NEW i \in Items, ObsFind(t, i) PROVE MissIsOnACorrelation'
    BY <1>7 DEF ObsFind
<1>8. ASSUME NEW c \in Corrs, NEW s \in sends, Report(c, s) PROVE MissIsOnACorrelation'
    BY <1>8 DEF Report
<1>9. ASSUME NEW c \in Corrs, NEW s \in sends, Pass(c, s) PROVE MissIsOnACorrelation'
    BY <1>9 DEF Pass
<1>10. ASSUME NEW c \in Corrs, NEW i \in Items, Propagate(c, i) PROVE MissIsOnACorrelation'
    BY <1>10 DEF Propagate
<1>11. ASSUME NEW c \in Corrs, NEW q \in Corrs, Name(c, q) PROVE MissIsOnACorrelation'
    BY <1>11 DEF Name
<1> QED
    BY <1>1, <1>2, <1>3, <1>4, <1>5, <1>6, <1>7, <1>8, <1>9, <1>10, <1>11 DEF Next

-----------------------------------------------------------------------------
(* HonestNeverCharged, with CitedFired; StoreWithinRecord, with ErasedArePast.   *)

LEMMA CitedNext ==
    ASSUME Mut # "M_BARE", CitedFired, [Next]_vars
    PROVE  CitedFired'
<1> USE DEF CitedFired
<1>1. CASE UNCHANGED vars
    BY <1>1 DEF vars
<1>2. ASSUME NEW t \in Thinkers, NEW i \in Items, NEW bad \in BOOLEAN, Read(t, i, bad) PROVE CitedFired'
    BY <1>2 DEF Read
<1>3. ASSUME NEW t \in Thinkers, NEW x \in Stores, Touch(t, x) PROVE CitedFired'
    BY <1>3 DEF Touch
<1>4. ASSUME NEW t \in Thinkers, Send(t) PROVE CitedFired'
    BY <1>4 DEF Send
<1>5. ASSUME NEW t \in Thinkers, EndRound(t) PROVE CitedFired'
    BY <1>5 DEF EndRound
<1>6. ASSUME NEW t \in Thinkers, NEW r \in 1..MaxRound, Erase(t, r) PROVE CitedFired'
    BY <1>6 DEF Erase
<1>7. ASSUME NEW t \in Thinkers, NEW i \in Items, ObsFind(t, i) PROVE CitedFired'
    BY <1>7 DEF ObsFind
<1>8. ASSUME NEW c \in Corrs, NEW s \in sends, Report(c, s) PROVE CitedFired'
    BY <1>8 DEF Report
<1>9. ASSUME NEW c \in Corrs, NEW s \in sends, Pass(c, s) PROVE CitedFired'
    BY <1>9 DEF Pass
<1>10. ASSUME NEW c \in Corrs, NEW i \in Items, Propagate(c, i) PROVE CitedFired'
    BY <1>10 DEF Propagate
<1>11. ASSUME NEW c \in Corrs, NEW q \in Corrs, Name(c, q) PROVE CitedFired'
    BY <1>11 DEF Name
<1> QED
    BY <1>1, <1>2, <1>3, <1>4, <1>5, <1>6, <1>7, <1>8, <1>9, <1>10, <1>11 DEF Next

LEMMA ChargedNext ==
    ASSUME Mut \notin {"M_BARE", "M_TIERLESS"}, TypeOK, HonestFolded, CitedFired, HonestNeverCharged, [Next]_vars
    PROVE  HonestNeverCharged'
<1> USE DEF HonestNeverCharged, HonestFolded, CitedFired, Has, TypeOK
<1>1. CASE UNCHANGED vars
    BY <1>1 DEF vars
<1>2. ASSUME NEW t \in Thinkers, NEW i \in Items, NEW bad \in BOOLEAN, Read(t, i, bad) PROVE HonestNeverCharged'
    BY <1>2 DEF Read
<1>3. ASSUME NEW t \in Thinkers, NEW x \in Stores, Touch(t, x) PROVE HonestNeverCharged'
    BY <1>3 DEF Touch
<1>4. ASSUME NEW t \in Thinkers, Send(t) PROVE HonestNeverCharged'
    BY <1>4 DEF Send
<1>5. ASSUME NEW t \in Thinkers, EndRound(t) PROVE HonestNeverCharged'
    BY <1>5 DEF EndRound
<1>6. ASSUME NEW t \in Thinkers, NEW r \in 1..MaxRound, Erase(t, r) PROVE HonestNeverCharged'
    BY <1>6 DEF Erase
<1>7. ASSUME NEW t \in Thinkers, NEW i \in Items, ObsFind(t, i) PROVE HonestNeverCharged'
    BY <1>7 DEF ObsFind
<1>8. ASSUME NEW c \in Corrs, NEW s \in sends, Report(c, s) PROVE HonestNeverCharged'
    BY <1>8 DEF Report
<1>9. ASSUME NEW c \in Corrs, NEW s \in sends, Pass(c, s) PROVE HonestNeverCharged'
    BY <1>9 DEF Pass
<1>10. ASSUME NEW c \in Corrs, NEW i \in Items, Propagate(c, i) PROVE HonestNeverCharged'
    BY <1>10 DEF Propagate
<1>11. ASSUME NEW c \in Corrs, NEW q \in Corrs, Name(c, q) PROVE HonestNeverCharged'
    BY <1>11 DEF Name
<1> QED
    BY <1>1, <1>2, <1>3, <1>4, <1>5, <1>6, <1>7, <1>8, <1>9, <1>10, <1>11 DEF Next

LEMMA StoreNext ==
    ASSUME Mut # "M_KEEP", TypeOK, StoreWithinRecord /\ ErasedArePast, [Next]_vars
    PROVE  (StoreWithinRecord /\ ErasedArePast)'
<1> USE DEF StoreWithinRecord, ErasedArePast, TypeOK
<1>1. CASE UNCHANGED vars
    BY <1>1 DEF vars
<1>2. ASSUME NEW t \in Thinkers, NEW i \in Items, NEW bad \in BOOLEAN, Read(t, i, bad) PROVE (StoreWithinRecord /\ ErasedArePast)'
    BY <1>2 DEF Read
<1>3. ASSUME NEW t \in Thinkers, NEW x \in Stores, Touch(t, x) PROVE (StoreWithinRecord /\ ErasedArePast)'
    BY <1>3 DEF Touch
<1>4. ASSUME NEW t \in Thinkers, Send(t) PROVE (StoreWithinRecord /\ ErasedArePast)'
    BY <1>4 DEF Send
<1>5. ASSUME NEW t \in Thinkers, EndRound(t) PROVE (StoreWithinRecord /\ ErasedArePast)'
    BY <1>5 DEF EndRound
<1>6. ASSUME NEW t \in Thinkers, NEW r \in 1..MaxRound, Erase(t, r) PROVE (StoreWithinRecord /\ ErasedArePast)'
    BY <1>6 DEF Erase
<1>7. ASSUME NEW t \in Thinkers, NEW i \in Items, ObsFind(t, i) PROVE (StoreWithinRecord /\ ErasedArePast)'
    BY <1>7 DEF ObsFind
<1>8. ASSUME NEW c \in Corrs, NEW s \in sends, Report(c, s) PROVE (StoreWithinRecord /\ ErasedArePast)'
    BY <1>8 DEF Report
<1>9. ASSUME NEW c \in Corrs, NEW s \in sends, Pass(c, s) PROVE (StoreWithinRecord /\ ErasedArePast)'
    BY <1>9 DEF Pass
<1>10. ASSUME NEW c \in Corrs, NEW i \in Items, Propagate(c, i) PROVE (StoreWithinRecord /\ ErasedArePast)'
    BY <1>10 DEF Propagate
<1>11. ASSUME NEW c \in Corrs, NEW q \in Corrs, Name(c, q) PROVE (StoreWithinRecord /\ ErasedArePast)'
    BY <1>11 DEF Name
<1> QED
    BY <1>1, <1>2, <1>3, <1>4, <1>5, <1>6, <1>7, <1>8, <1>9, <1>10, <1>11 DEF Next

(* A call on a shared target is enabled wherever no finding names the caller:    *)
(* every state, no induction.                                                    *)
LEMMA LagEnabled ==
    ASSUME Mut # "M_COUPLE"
    PROVE  LagNeverGates
BY ExpandENABLED DEF LagNeverGates, Touch, Blocked, Out, Carried

-----------------------------------------------------------------------------
THEOREM CarriedCoversSplitPathAlways ==
    ASSUME Mut \notin {"M_ROUNDSCOPE", "M_ONEHOP"}
    PROVE  Spec => []CarriedCoversSplitPath
<1>1. Init => Ghost /\ HonestFolded
    BY DEF Init, Ghost, StoreTracked, ContextTracked, SendTracked, HonestFolded, Carried
<1>2. TypeOK /\ (Ghost /\ HonestFolded) /\ [Next]_vars => (Ghost /\ HonestFolded)'
    BY GhostNext, HonestFoldedNext
<1>3. Ghost /\ HonestFolded => CarriedCoversSplitPath
    BY DEF Ghost, SendTracked, HonestFolded, CarriedCoversSplitPath
<1>4. Spec => []TypeOK
    BY TypeAlways
<1> QED
    BY <1>1, <1>2, <1>3, <1>4, PTL DEF Spec

THEOREM FindingHasEvidenceAlways ==
    ASSUME Mut # "M_BARE"
    PROVE  Spec => []FindingHasEvidence
<1>1. Init => FindingHasEvidence
    BY DEF Init, FindingHasEvidence
<1>2. FindingHasEvidence /\ [Next]_vars => FindingHasEvidence'
    BY EvidenceNext
<1> QED
    BY <1>1, <1>2, PTL DEF Spec

THEOREM IngressReachIsSharedAlways ==
    ASSUME Mut # "M_DOMAIN"
    PROVE  Spec => []IngressReachIsShared
<1>1. Init => IngressReachIsShared
    BY DEF Init, IngressReachIsShared
<1>2. IngressReachIsShared /\ [Next]_vars => IngressReachIsShared'
    BY ReachNext
<1> QED
    BY <1>1, <1>2, PTL DEF Spec

THEOREM MissIsOnACorrelationAlways ==
    ASSUME Mut # "M_TIERLESS"
    PROVE  Spec => []MissIsOnACorrelation
<1>1. Init => MissIsOnACorrelation
    BY DEF Init, MissIsOnACorrelation
<1>2. MissIsOnACorrelation /\ [Next]_vars => MissIsOnACorrelation'
    BY TierNext
<1> QED
    BY <1>1, <1>2, PTL DEF Spec

THEOREM SilenceIsCountedAlways ==
    ASSUME Mut # "M_SELF"
    PROVE  Spec => []SilenceIsCounted
<1>1. Init => SilenceIsCounted
    BY DEF Init, SilenceIsCounted
<1>2. TypeOK /\ SilenceIsCounted /\ [Next]_vars => SilenceIsCounted'
    BY SilenceNext
<1>3. Spec => []TypeOK
    BY TypeAlways
<1> QED
    BY <1>1, <1>2, <1>3, PTL DEF Spec

THEOREM HonestNeverChargedAlways ==
    ASSUME Mut \notin {"M_BARE", "M_TIERLESS"}
    PROVE  Spec => []HonestNeverCharged
<1> DEFINE Inv == HonestFolded /\ CitedFired /\ HonestNeverCharged
<1>1. Init => Inv
    BY DEF Init, HonestFolded, CitedFired, HonestNeverCharged
<1>2. TypeOK /\ Inv /\ [Next]_vars => Inv'
    BY HonestFoldedNext, CitedNext, ChargedNext
<1>3. Spec => []TypeOK
    BY TypeAlways
<1> QED
    BY <1>1, <1>2, <1>3, PTL DEF Spec

THEOREM StoreWithinRecordAlways ==
    ASSUME Mut # "M_KEEP"
    PROVE  Spec => []StoreWithinRecord
<1> DEFINE Inv == StoreWithinRecord /\ ErasedArePast
<1>1. Init => Inv
    BY DEF Init, StoreWithinRecord, ErasedArePast
<1>2. TypeOK /\ Inv /\ [Next]_vars => Inv'
    BY StoreNext
<1>3. Spec => []TypeOK
    BY TypeAlways
<1> QED
    BY <1>1, <1>2, <1>3, PTL DEF Spec

THEOREM LagNeverGatesAlways ==
    ASSUME Mut # "M_COUPLE"
    PROVE  Spec => []LagNeverGates
<1>1. LagNeverGates
    BY LagEnabled
<1> QED
    BY <1>1, PTL

THEOREM SafeAlways ==
    ASSUME Mut = "none"
    PROVE  Spec => []Safe
<1>1. Spec => []CarriedCoversSplitPath
    BY CarriedCoversSplitPathAlways
<1>2. Spec => []FindingHasEvidence
    BY FindingHasEvidenceAlways
<1>3. Spec => []IngressReachIsShared
    BY IngressReachIsSharedAlways
<1>4. Spec => []SilenceIsCounted
    BY SilenceIsCountedAlways
<1>5. Spec => []MissIsOnACorrelation
    BY MissIsOnACorrelationAlways
<1>6. Spec => []HonestNeverCharged
    BY HonestNeverChargedAlways
<1>7. Spec => []StoreWithinRecord
    BY StoreWithinRecordAlways
<1>8. Spec => []LagNeverGates
    BY LagNeverGatesAlways
<1> QED
    BY <1>1, <1>2, <1>3, <1>4, <1>5, <1>6, <1>7, <1>8, PTL DEF Safe

-----------------------------------------------------------------------------
(* What each mutation admits: the guard or the update it removes.                *)

\* M_ROUNDSCOPE: no call leaves a row, so nothing is carried past a round.
LEMMA MutRoundscopeCarriesNothing ==
    ASSUME Mut = "M_ROUNDSCOPE", NEW t \in Thinkers, NEW x \in Stores, Touch(t, x)
    PROVE  writes' = writes
BY DEF Touch

\* M_ONEHOP: a caller whose taint came through a target, and not from its own
\* round's reads, leaves no row.
LEMMA MutOneHopDropsTheSecondHop ==
    ASSUME Mut = "M_ONEHOP", NEW t \in Thinkers, NEW x \in Stores, Touch(t, x), ~clearU[t]
    PROVE  writes' = writes
BY DEF Touch, Out

\* M_BARE: a finding is made on a send the fold did not fire on.
LEMMA MutBareFindsAnything ==
    ASSUME Mut = "M_BARE", NEW c \in Corrs, NEW s \in sends, s \notin marked[c]
    PROVE  ENABLED Report(c, s)
BY ExpandENABLED DEF Report

\* M_DOMAIN: every Thinker is named.
LEMMA MutDomainNamesAll ==
    ASSUME Mut = "M_DOMAIN", NEW c \in Corrs, NEW i \in Items, Propagate(c, i)
    PROVE  Thinkers \subseteq named'
BY DEF Propagate

\* M_SELF: no report and no pass counts a miss.
LEMMA MutSelfCountsNothing ==
    ASSUME Mut = "M_SELF", NEW c \in Corrs, NEW s \in sends, Report(c, s) \/ Pass(c, s)
    PROVE  misses' = misses
BY DEF Report, Pass

\* M_TIERLESS: a cell Observer's judgment charges every correlator.
LEMMA MutTierlessChargesAll ==
    ASSUME Mut = "M_TIERLESS", NEW t \in Thinkers, NEW i \in Items, ObsFind(t, i), NEW c \in Corrs
    PROVE  [obs |-> c, tier |-> "judgment", cite |-> i] \in misses'
BY DEF ObsFind

\* M_KEEP: erasing a round drops nothing.
LEMMA MutKeepDropsNothing ==
    ASSUME Mut = "M_KEEP", NEW t \in Thinkers, NEW r \in 1..MaxRound, Erase(t, r)
    PROVE  writes' = writes /\ delivered' = delivered
BY DEF Erase

\* M_COUPLE: a call waits for a correlator whose mark has passed every send.
LEMMA MutCoupleWaits ==
    ASSUME Mut = "M_COUPLE", NEW t \in Thinkers, NEW x \in Stores, Touch(t, x)
    PROVE  \E c \in Corrs : sends \subseteq marked[c]
BY DEF Touch
=============================================================================
