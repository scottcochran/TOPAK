import TopakSpec.RulesFloorBase
/-!
# Anchor.tla in Lean

ADR-0029 §5 bootstrap module 2 of 5; ADR-0025, the trust anchor as a havoc issuer bounded by the floor.
`spec/Anchor.tla` re-encoded; `spec/Anchor_proof.tla`'s theorems proved by induction on reachable states.
The constants `Active` and `MaxEpoch` are parameters. Of the TLAPS proof's two assumptions,
`Active ⊆ AllEntries` holds by type and `MaxEpoch ∈ Nat` by type, so the Lean theorems take none.

Mutation: `M_FLOOR`, the mechanism accepts an issuance without checking the floor.
-/

namespace Topak.Spec.Anchor
open Topak.Spec PSet RulesFloorBase

inductive Mut | none | M_FLOOR
  deriving DecidableEq

/-- `VARIABLES rules, epoch` -/
structure State where
  rules : Rules
  epoch : Nat

/-- `Init == rules = Genesis /\ epoch = 0` -/
def Init (st : State) : Prop := st.rules = Genesis ∧ st.epoch = 0

/-- `Authentic(r) == TRUE`: opaque in ADR-0025 §2; havoc is the strongest case. -/
def Authentic (_ : Rules) : Prop := True

/-- `Admissible(r) == IF Mut = "M_FLOOR" THEN Authentic(r) ELSE Authentic(r) /\ Floor(r)` -/
def Admissible (m : Mut) (Active : PSet EntryName) (r : Rules) : Prop :=
  if m = .M_FLOOR then Authentic r else Authentic r ∧ Floor Active r

/-- ```
Issue == /\ epoch < MaxEpoch
         /\ ∃ r ∈ RuleSpace : Admissible(r) /\ rules' = r
         /\ epoch' = epoch + 1
``` -/
def Issue (m : Mut) (Active : PSet EntryName) (MaxEpoch : Nat) (st st' : State) : Prop :=
  st.epoch < MaxEpoch ∧
  (∃ r, r ∈ RuleSpace ∧ Admissible m Active r ∧ st'.rules = r) ∧
  st'.epoch = st.epoch + 1

/-- `Next == Issue` -/
def Next (m : Mut) (Active : PSet EntryName) (MaxEpoch : Nat) (st st' : State) : Prop :=
  Issue m Active MaxEpoch st st'

/-- `FloorPreserved == Floor(rules)` -/
def FloorPreserved (Active : PSet EntryName) (st : State) : Prop := Floor Active st.rules
/-- `EpochMonotone == epoch ∈ 0..MaxEpoch` -/
def EpochMonotone (MaxEpoch : Nat) (st : State) : Prop := st.epoch ≤ MaxEpoch

/-! ## Proofs -/

theorem InitFloor (Active : PSet EntryName) (st : State) (h : Init st) : FloorPreserved Active st := by
  unfold FloorPreserved; rw [h.1]; exact GenesisFloor Active

theorem NextFloor (Active : PSet EntryName) (MaxEpoch : Nat) (st st' : State)
    (_ : FloorPreserved Active st) (hn : Next .none Active MaxEpoch st st') : FloorPreserved Active st' := by
  obtain ⟨-, ⟨r, -, hadm, hr⟩, -⟩ := hn
  unfold FloorPreserved; rw [hr]
  unfold Admissible at hadm
  rw [if_neg (by decide)] at hadm
  exact hadm.2

/-- `THEOREM FloorPreservedAlways == ASSUME Mut = "none" PROVE Spec => []FloorPreserved` -/
theorem FloorPreservedAlways (Active : PSet EntryName) (MaxEpoch : Nat) :
    ∀ st, Reachable Init (Next .none Active MaxEpoch) st → FloorPreserved Active st :=
  invariant (FloorPreserved Active) (FloorPreserved Active) (InitFloor Active) (NextFloor Active MaxEpoch)
    (fun _ h => h)

theorem InitEpoch (MaxEpoch : Nat) (st : State) (h : Init st) : EpochMonotone MaxEpoch st := by
  unfold EpochMonotone; rw [h.2]; exact Nat.zero_le _

theorem NextEpoch (m : Mut) (Active : PSet EntryName) (MaxEpoch : Nat) (st st' : State)
    (_ : EpochMonotone MaxEpoch st) (hn : Next m Active MaxEpoch st st') : EpochMonotone MaxEpoch st' := by
  obtain ⟨hlt, -, he⟩ := hn
  unfold EpochMonotone; rw [he]; exact hlt

/-- `THEOREM EpochMonotoneAlways == Spec => []EpochMonotone`, under either mutation setting. -/
theorem EpochMonotoneAlways (m : Mut) (Active : PSet EntryName) (MaxEpoch : Nat) :
    ∀ st, Reachable Init (Next m Active MaxEpoch) st → EpochMonotone MaxEpoch st :=
  invariant (EpochMonotone MaxEpoch) (EpochMonotone MaxEpoch) (InitEpoch MaxEpoch)
    (NextEpoch m Active MaxEpoch) (fun _ h => h)

/-- `MutAdmitsAll`: with the floor check omitted, every rule in the space is admissible. -/
theorem MutAdmitsAll (Active : PSet EntryName) (r : Rules) : Admissible .M_FLOOR Active r := by
  unfold Admissible; rw [if_pos rfl]; trivial

#print axioms FloorPreservedAlways
#print axioms EpochMonotoneAlways

end Topak.Spec.Anchor
