------------------------- MODULE Coupling_live_proof -------------------------
(* TLAPS proofs for Coupling_live.tla (ADR-0039 §2): its Next is Coupling's, so   *)
(* Coupling's three invariants hold of it. For every K, R and MaxRound in Nat:   *)
(*                                                                               *)
(*   SpecLImpliesSpec == SpecL => Spec        (every Mut)                        *)
(*   NoAdmitWithoutLiveObserverAlwaysL        (Mut # "M_NOCOUPLE")               *)
(*   UnreadBoundedAlwaysL                     (Mut \notin {"M_MARK", "M_ROUNDS", "M_NOCOUPLE"}) *)
(*   CorrelatorNeverGatesAlwaysL              (Mut # "M_CORR")                   *)
(*   SafeAlwaysL == SpecL => []Safe           (Mut \in {"none", "M_HBLIVE", "M_HBCOUPLED"}) *)
(*                                                                               *)
(* Every NextL step is a Next step of Coupling.tla, under every Mut: HeartbeatL  *)
(* is Heartbeat with two conjuncts added. Under every Mut but the two liveness   *)
(* mutations NextL is Next exactly (NextIsNextL). So SpecL => Spec, and each      *)
(* invariant Coupling_proof proves of Spec holds of SpecL under the hypothesis   *)
(* it has there, which neither liveness mutation touches.                        *)
(*                                                                               *)
(* What is not proved here. The four leads-to properties (AdmitStallEnds,        *)
(* GrantStallEnds, AdmitsResume, NextRoundGranted), under A12, ThinkerAsks and   *)
(* GrantsMade, are owed, with K >= 1 as a hypothesis of the two admit            *)
(* properties. Two are quantified and all four have ENABLED premises. tlapm      *)
(* 7824dab has known unsound cases, in which SMT, Zenon, Isabelle and even PTL   *)
(* certify a false statement: a term under a binder, and two terms given one     *)
(* name (spec/proof-certification.md, sections 8 and 10). A WF1 or SF1 step on a *)
(* decreasing measure needs a quantified leads-to hypothesis inside the proof,   *)
(* which PTL cannot combine from instances, and no route for it under section    *)
(* 10's rules is known yet in TLAPS; Lean (ADR-0053) is the plan's other route.  *)
(* TLC checks the four at small constants, with each fairness condition          *)
(* dropped or weakened and each mutation that must break one                     *)
(* (Coupling_live-results-2026.10.07.txt).                                       *)
(* Nothing here uses fairness: a theorem about SpecL holds of every fair spec    *)
(* the module defines, since each adds conjuncts to it.                          *)
(*                                                                               *)
(* Coupling.tla, Coupling_live.tla and Coupling_proof.tla are not edited; this   *)
(* module extends the last two. Its three assumptions restate Coupling_proof's   *)
(* KNat, RNat and MaxRoundNat, on which the cited theorems rest, so that the     *)
(* results file names them. The lemmas at the end say what each liveness        *)
(* mutation removes; the behaviours that break the leads-to properties are       *)
(* TLC's.                                                                        *)
(*                                                                               *)
(* Check with:  ../tools/tlapm Coupling_live_proof.tla   (from spec/; see        *)
(*              proof-results.sh and proof-cert.sh for the results files)        *)
EXTENDS Coupling_live, Coupling_proof, TLAPS

ASSUME KNatL        == K \in Nat
ASSUME RNatL        == R \in Nat
ASSUME MaxRoundNatL == MaxRound \in Nat

-----------------------------------------------------------------------------
(* Every NextL step is a Next step, under every Mut.                             *)

LEMMA HeartbeatLIsHeartbeat ==
    ASSUME NEW r, NEW w, HeartbeatL(r, w)
    PROVE  Heartbeat(r, w)
BY DEF HeartbeatL

LEMMA NextLIsNext == NextL => Next
BY HeartbeatLIsHeartbeat DEF NextL, Next

(* Under every other Mut the converse holds: NextL is Next.                     *)
LEMMA NextIsNextL ==
    ASSUME Mut \notin {"M_HBLIVE", "M_HBCOUPLED"}
    PROVE  Next <=> NextL
BY DEF NextL, Next, HeartbeatL

THEOREM SpecLImpliesSpec == SpecL => Spec
<1>1. [NextL]_vars => [Next]_vars
    BY NextLIsNext
<1> QED
    BY <1>1, PTL DEF SpecL, Spec

-----------------------------------------------------------------------------
(* Coupling_proof's theorems, for SpecL.                                         *)

THEOREM NoAdmitWithoutLiveObserverAlwaysL ==
    ASSUME Mut # "M_NOCOUPLE"
    PROVE  SpecL => []NoAdmitWithoutLiveObserver
BY SpecLImpliesSpec, NoAdmitWithoutLiveObserverAlways

THEOREM UnreadBoundedAlwaysL ==
    ASSUME Mut # "M_MARK", Mut # "M_ROUNDS", Mut # "M_NOCOUPLE"
    PROVE  SpecL => []UnreadBounded
BY SpecLImpliesSpec, UnreadBoundedAlways

THEOREM CorrelatorNeverGatesAlwaysL ==
    ASSUME Mut # "M_CORR"
    PROVE  SpecL => []CorrelatorNeverGates
BY SpecLImpliesSpec, CorrelatorNeverGatesAlways

(* The two liveness mutations break none of the three.                          *)
THEOREM SafeAlwaysL ==
    ASSUME Mut \in {"none", "M_HBLIVE", "M_HBCOUPLED"}
    PROVE  SpecL => []Safe
<1>1. SpecL => []NoAdmitWithoutLiveObserver
    BY NoAdmitWithoutLiveObserverAlwaysL
<1>2. SpecL => []UnreadBounded
    BY UnreadBoundedAlwaysL
<1>3. SpecL => []CorrelatorNeverGates
    BY CorrelatorNeverGatesAlwaysL
<1> QED
    BY <1>1, <1>2, <1>3, PTL DEF Safe

-----------------------------------------------------------------------------
(* What each liveness mutation removes. Every safety property holds under both;  *)
(* the behaviours in which a leads-to property fails are TLC's.                  *)

(* M_HBLIVE: no heartbeat once the Thinker's round has ended, so a round that   *)
(* ends unread is never read to its seal, and the next grant waits for good.    *)
LEMMA MutHbLiveNoBeatAfterRound ==
    ASSUME Mut = "M_HBLIVE", ~tLive, NEW r, NEW w
    PROVE  ~HeartbeatL(r, w)
BY DEF HeartbeatL

(* M_HBCOUPLED: no heartbeat from an Observer that is not live, so an Observer  *)
(* that is stale or behind cannot catch up by its own report.                   *)
LEMMA MutHbCoupledNoBeatUnlive ==
    ASSUME Mut = "M_HBCOUPLED", ~LiveO, NEW r, NEW w
    PROVE  ~HeartbeatL(r, w)
BY DEF HeartbeatL
=============================================================================
