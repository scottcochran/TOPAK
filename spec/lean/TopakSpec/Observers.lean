import TopakSpec.Prelude
/-!
# Observers.tla in Lean

ADR-0038, Observer scoping. `spec/Observers.tla` re-encoded; `spec/Observers_proof.tla`'s theorems
proved by induction on reachable states. `CellOf`, one TLA+ function over Thinkers and Observers with
"none" for the correlator, is two Lean functions, `CellOfT` and `CellOfO`, the second into `Option Cell`.
The TLA+ action `Finding(o, t)` is `FindingStep` here, since `Finding` names the record.

Mutations: `M_QUORUM`, a finding takes effect only when a majority of W(t) have found; `M_REACH`, a cell
Observer may find against anyone. Each theorem takes as hypothesis only the mutation that breaks it.
-/

namespace Topak.Spec.Observers
open Topak.Spec PSet

inductive Mut | none | M_QUORUM | M_REACH
  deriving DecidableEq

/-- `Thinkers == {"t1", "t2"}` -/
inductive Thinker | t1 | t2
  deriving DecidableEq
/-- `Observers == {"o1", "o2", "corr"}` -/
inductive Observer | o1 | o2 | corr
  deriving DecidableEq
inductive Cell | c1 | c2
  deriving DecidableEq

/-- `CellOf == [t1 |-> "c1", t2 |-> "c2", o1 |-> "c1", o2 |-> "c2", corr |-> "none"]` -/
def CellOfT : Thinker → Cell
  | .t1 => .c1
  | .t2 => .c2
def CellOfO : Observer → Option Cell
  | .o1 => some .c1
  | .o2 => some .c2
  | .corr => none

def Thinkers : PSet Thinker := univ

/-- §2. `W(t) == {o ∈ Observers : CellOf[o] = CellOf[t] \/ CellOf[o] = "none"}` -/
def W (t : Thinker) : PSet Observer := fun o => CellOfO o = some (CellOfT t) ∨ CellOfO o = none

@[simp] theorem mem_W (t : Thinker) (o : Observer) :
    o ∈ W t ↔ (CellOfO o = some (CellOfT t) ∨ CellOfO o = none) := Iff.rfl

/-- ```
Reach(o) == IF Mut = "M_REACH" \/ CellOf[o] = "none" THEN Thinkers
            ELSE {t ∈ Thinkers : CellOf[t] = CellOf[o]}
``` -/
def Reach (m : Mut) (o : Observer) : PSet Thinker :=
  if m = .M_REACH ∨ CellOfO o = none then Thinkers else fun t => some (CellOfT t) = CellOfO o

/-- `[obs |-> o, target |-> t]` -/
structure Finding where
  obs : Observer
  target : Thinker

/-- `VARIABLES findings, admittedOverFinding, refused` -/
structure State where
  findings : PSet Finding
  admittedOverFinding : Prop
  refused : PSet Thinker

/-- `Init == findings = {} /\ admittedOverFinding = FALSE /\ refused = {}` -/
def Init (st : State) : Prop := st.findings = ∅ ∧ ¬ st.admittedOverFinding ∧ st.refused = ∅

/-- ```
Finding(o, t) ==
  /\ t ∈ Reach(o)
  /\ findings' = findings ∪ {[obs |-> o, target |-> t]}
  /\ UNCHANGED <<admittedOverFinding, refused>>
``` -/
def FindingStep (m : Mut) (o : Observer) (t : Thinker) (st st' : State) : Prop :=
  t ∈ Reach m o ∧
  st'.findings = st.findings ∪ {⟨o, t⟩} ∧
  (st'.admittedOverFinding ↔ st.admittedOverFinding) ∧ st'.refused = st.refused

/-- `Found(t) == {f.obs : f ∈ {g ∈ findings : g.target = t}}` -/
def Found (st : State) (t : Thinker) : PSet Observer :=
  fun o => ∃ f, f ∈ st.findings ∧ f.target = t ∧ f.obs = o

/-- §5. ```
Blocked(t) ==
  IF Mut = "M_QUORUM" THEN 2 * Cardinality(Found(t) ∩ W(t)) > Cardinality(W(t))
  ELSE Found(t) ∩ W(t) # {}
``` -/
def Blocked (m : Mut) (st : State) (t : Thinker) : Prop :=
  if m = .M_QUORUM then ∃ n k, HasCard (Found st t ∩ W t) n ∧ HasCard (W t) k ∧ 2 * n > k
  else NonEmpty (Found st t ∩ W t)

/-- ```
Admit(t) ==
  /\ ~Blocked(t)
  /\ admittedOverFinding' = (admittedOverFinding \/ (Found(t) ∩ W(t) # {}))
  /\ UNCHANGED <<findings, refused>>
``` -/
def Admit (m : Mut) (t : Thinker) (st st' : State) : Prop :=
  ¬ Blocked m st t ∧
  (st'.admittedOverFinding ↔ (st.admittedOverFinding ∨ NonEmpty (Found st t ∩ W t))) ∧
  st'.findings = st.findings ∧ st'.refused = st.refused

/-- `Refuse(t) == Blocked(t) /\ refused' = refused ∪ {t} /\ UNCHANGED <<findings, admittedOverFinding>>` -/
def Refuse (m : Mut) (t : Thinker) (st st' : State) : Prop :=
  Blocked m st t ∧ st'.refused = st.refused ∪ {t} ∧
  st'.findings = st.findings ∧ (st'.admittedOverFinding ↔ st.admittedOverFinding)

/-- `EndRound(t) == findings' = {f ∈ findings : f.target # t} /\ UNCHANGED <<admittedOverFinding, refused>>` -/
def EndRound (t : Thinker) (st st' : State) : Prop :=
  (st'.findings = fun f => f ∈ st.findings ∧ f.target ≠ t) ∧
  (st'.admittedOverFinding ↔ st.admittedOverFinding) ∧ st'.refused = st.refused

/-- `Next == ∃ t ∈ Thinkers : Admit(t) \/ Refuse(t) \/ EndRound(t) \/ ∃ o ∈ Observers : Finding(o, t)` -/
def Next (m : Mut) (st st' : State) : Prop :=
  ∃ t, Admit m t st st' ∨ Refuse m t st st' ∨ EndRound t st st' ∨ ∃ o, FindingStep m o t st st'

/-! ## The two properties -/

/-- §5. `DenyByAnyOf == ~admittedOverFinding` -/
def DenyByAnyOf (st : State) : Prop := ¬ st.admittedOverFinding

/-- §1. `ReachIsBounded == ∀ f ∈ findings : CellOf[f.obs] = "none" \/ CellOf[f.obs] = CellOf[f.target]` -/
def ReachIsBounded (st : State) : Prop :=
  ∀ f, f ∈ st.findings → CellOfO f.obs = none ∨ CellOfO f.obs = some (CellOfT f.target)

def Safe (st : State) : Prop := DenyByAnyOf st ∧ ReachIsBounded st

/-! ## Proofs -/

theorem InitSafe (st : State) (h : Init st) : Safe st := by
  obtain ⟨hf, ha, -⟩ := h
  exact ⟨ha, fun f hf' => by simp [hf] at hf'⟩

theorem NextDeny (m : Mut) (hm : m ≠ .M_QUORUM) (st st' : State) (hd : DenyByAnyOf st) (hn : Next m st st') :
    DenyByAnyOf st' := by
  obtain ⟨t, h⟩ := hn
  rcases h with ⟨hb, hflag, -, -⟩ | ⟨-, -, -, hflag⟩ | ⟨-, hflag, -⟩ | ⟨o, -, -, hflag, -⟩
  · -- Admit(t): not blocked, so under any-of no watcher has found; the flag is unchanged
    intro h'
    rcases hflag.mp h' with h' | h'
    · exact hd h'
    · apply hb
      unfold Blocked
      rw [if_neg hm]
      exact h'
  · exact fun h' => hd (hflag.mp h')
  · exact fun h' => hd (hflag.mp h')
  · exact fun h' => hd (hflag.mp h')

/-- `THEOREM DenyByAnyOfAlways == ASSUME Mut # "M_QUORUM" PROVE Spec => []DenyByAnyOf` -/
theorem DenyByAnyOfAlways (m : Mut) (hm : m ≠ .M_QUORUM) :
    ∀ st, Reachable Init (Next m) st → DenyByAnyOf st :=
  invariant DenyByAnyOf DenyByAnyOf (fun st h => (InitSafe st h).1) (NextDeny m hm) (fun _ h => h)

theorem NextReach (m : Mut) (hm : m ≠ .M_REACH) (st st' : State) (hr : ReachIsBounded st) (hn : Next m st st') :
    ReachIsBounded st' := by
  obtain ⟨t, h⟩ := hn
  rcases h with ⟨-, -, hf, -⟩ | ⟨-, -, hf, -⟩ | ⟨hf, -, -⟩ | ⟨o, hreach, hf, -, -⟩
  · unfold ReachIsBounded; rw [hf]; exact hr
  · unfold ReachIsBounded; rw [hf]; exact hr
  · unfold ReachIsBounded; rw [hf]; rintro f ⟨hf', -⟩; exact hr f hf'
  · -- Finding(o, t): t is within o's reach, which under Mut # "M_REACH" is o's cell or everyone for the correlator
    unfold ReachIsBounded
    rw [hf]
    intro f hf'
    rcases hf' with hf' | hf'
    · exact hr f hf'
    · have hf' : f = ⟨o, t⟩ := hf'
      subst hf'
      by_cases hc : m = .M_REACH ∨ CellOfO o = none
      · rcases hc with hc | hc
        · exact absurd hc hm
        · exact Or.inl hc
      · have : some (CellOfT t) = CellOfO o := by
          unfold Reach at hreach
          rw [if_neg hc] at hreach
          exact hreach
        exact Or.inr this.symm

/-- `THEOREM ReachIsBoundedAlways == ASSUME Mut # "M_REACH" PROVE Spec => []ReachIsBounded` -/
theorem ReachIsBoundedAlways (m : Mut) (hm : m ≠ .M_REACH) :
    ∀ st, Reachable Init (Next m) st → ReachIsBounded st :=
  invariant ReachIsBounded ReachIsBounded (fun st h => (InitSafe st h).2) (NextReach m hm) (fun _ h => h)

/-- `THEOREM SafeAlways == ASSUME Mut = "none" PROVE Spec => []Safe` -/
theorem SafeAlways : ∀ st, Reachable Init (Next .none) st → Safe st :=
  fun st h => ⟨DenyByAnyOfAlways .none (by decide) st h, ReachIsBoundedAlways .none (by decide) st h⟩

/-! ## Why the mutations must fail (the counterexamples are TLC's) -/

/-- `MutReachIsEverything`: under M_REACH every observer reaches every thinker. -/
theorem MutReachIsEverything (o : Observer) (t : Thinker) : t ∈ Reach .M_REACH o := by
  unfold Reach; rw [if_pos (Or.inl rfl)]; trivial

/-- `MutQuorumAdmitsOneOfTwo`: W(t) has exactly two members, the cell Observer and the correlator, so
under M_QUORUM a finding blocks only when both have found: one finding of two is let through. -/
theorem W_t1 : W .t1 = insert .o1 (insert .corr ∅) := by
  apply ext; intro o; cases o <;> simp [CellOfO, CellOfT]
theorem W_t2 : W .t2 = insert .o2 (insert .corr ∅) := by
  apply ext; intro o; cases o <;> simp [CellOfO, CellOfT]

theorem WHasTwo (t : Thinker) : HasCard (W t) 2 := by
  cases t
  · rw [W_t1]; exact HasCard.insert _ (HasCard.insert _ HasCard.empty (by simp)) (by simp)
  · rw [W_t2]; exact HasCard.insert _ (HasCard.insert _ HasCard.empty (by simp)) (by simp)

theorem MutQuorumNeedsTwo (n : Nat) (h : 2 * n > 2) : n ≥ 2 := by omega

#print axioms DenyByAnyOfAlways
#print axioms ReachIsBoundedAlways
#print axioms SafeAlways

end Topak.Spec.Observers
