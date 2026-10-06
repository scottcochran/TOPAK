import TopakSpec.RulesFloorBase
/-!
# BreakGlass.tla in Lean

ADR-0029 §5 bootstrap module 5 of 5; ADR-0009 and ADR-0026 R7: break-glass grants authority within the
rules in force and never alters them. `spec/BreakGlass.tla` re-encoded; `spec/BreakGlass_proof.tla`'s
theorem proved by induction on reachable states with its invariant `Floor(rules) ∧ BreakGlassNever-
ChangesAuthority`. Of the TLAPS proof's two assumptions, `Active ⊆ AllEntries` holds by type; `"R7" ∈
Active` is the hypothesis `hR7`, as it must be: the property is R7's claim.

Mutation: `M_SCOPE`, the mechanism ignores `bgScope`. Dropping R7 from `Active` is the other mutation,
and is the hypothesis the theorem cannot do without.
-/

namespace Topak.Spec.BreakGlass
open Topak.Spec PSet RulesFloorBase

inductive Mut | none | M_SCOPE
  deriving DecidableEq

/-- `VARIABLES rules, epoch, bgDid` -/
structure State where
  rules : Rules
  epoch : Nat
  bgDid : PSet BGAct

/-- `Init == rules = Genesis /\ epoch = 0 /\ bgDid = {}` -/
def Init (st : State) : Prop := st.rules = Genesis ∧ st.epoch = 0 ∧ st.bgDid = ∅

/-- ```
Issue == /\ epoch < MaxEpoch
         /\ ∃ r ∈ RuleSpace : Floor(r) /\ rules' = r
         /\ epoch' = epoch + 1
         /\ UNCHANGED bgDid
``` -/
def Issue (Active : PSet EntryName) (MaxEpoch : Nat) (st st' : State) : Prop :=
  st.epoch < MaxEpoch ∧
  (∃ r, r ∈ RuleSpace ∧ Floor Active r ∧ st'.rules = r) ∧
  st'.epoch = st.epoch + 1 ∧
  st'.bgDid = st.bgDid

/-- `Admits(x) == IF Mut = "M_SCOPE" THEN x ∈ BGActs ELSE x ∈ rules.bgScope` -/
def Admits (m : Mut) (st : State) (x : BGAct) : Prop :=
  if m = .M_SCOPE then x ∈ BGActs else x ∈ st.rules.bgScope

/-- `BreakGlass == ∃ x ∈ BGActs : Admits(x) /\ bgDid' = bgDid ∪ {x} /\ UNCHANGED <<rules, epoch>>` -/
def BreakGlassStep (m : Mut) (st st' : State) : Prop :=
  (∃ x, x ∈ BGActs ∧ Admits m st x ∧ st'.bgDid = st.bgDid ∪ {x}) ∧
  st'.rules = st.rules ∧ st'.epoch = st.epoch

/-- `Next == Issue \/ BreakGlass` -/
def Next (m : Mut) (Active : PSet EntryName) (MaxEpoch : Nat) (st st' : State) : Prop :=
  Issue Active MaxEpoch st st' ∨ BreakGlassStep m st st'

/-- `BreakGlassNeverChangesAuthority == bgDid ∩ AuthActs = {}` -/
def BreakGlassNeverChangesAuthority (st : State) : Prop := st.bgDid ∩ AuthActs = ∅

/-! ## Proofs -/

/-- The inductive invariant: the floor holds of the issued rules, and nothing break-glass has done
changes authority. The floor is needed because R7 is what keeps the envelope away from the authority
actions. -/
def Inv (Active : PSet EntryName) (st : State) : Prop :=
  Floor Active st.rules ∧ BreakGlassNeverChangesAuthority st

theorem InitInv (Active : PSet EntryName) (st : State) (h : Init st) : Inv Active st := by
  obtain ⟨hr, -, hb⟩ := h
  refine ⟨?_, ?_⟩
  · rw [hr]; exact GenesisFloor Active
  · unfold BreakGlassNeverChangesAuthority; rw [hb, eq_empty_iff]
    rintro a ⟨ha, -⟩; exact ha

theorem NextInv (Active : PSet EntryName) (hR7 : EntryName.R7 ∈ Active) (MaxEpoch : Nat) (st st' : State)
    (hi : Inv Active st) (hn : Next .none Active MaxEpoch st st') : Inv Active st' := by
  obtain ⟨hF, hB⟩ := hi
  rcases hn with ⟨-, ⟨r, -, hFr, hr⟩, -, hb⟩ | ⟨⟨x, -, hadm, hb⟩, hr, -⟩
  · -- Issue: the floor bounds the issuance; bgDid is unchanged
    refine ⟨?_, ?_⟩
    · rw [hr]; exact hFr
    · unfold BreakGlassNeverChangesAuthority; rw [hb]; exact hB
  · -- BreakGlass: x is in bgScope, and R7 keeps bgScope clear of the authority actions
    have hx : x ∈ st.rules.bgScope := by
      unfold Admits at hadm; rw [if_neg (by decide)] at hadm; exact hadm
    have hR7e : st.rules.bgScope ∩ AuthActs = ∅ := hF .R7 hR7
    refine ⟨?_, ?_⟩
    · rw [hr]; exact hF
    · unfold BreakGlassNeverChangesAuthority
      rw [hb, eq_empty_iff]
      rintro a ⟨ha | ha, hauth⟩
      · have : a ∈ st.bgDid ∩ AuthActs := ⟨ha, hauth⟩
        rw [hB] at this; exact this
      · have ha : a = x := ha
        subst ha
        have : a ∈ st.rules.bgScope ∩ AuthActs := ⟨hx, hauth⟩
        rw [hR7e] at this; exact this

/-- `THEOREM NeverChangesAuthority == ASSUME Mut = "none" PROVE Spec => []BreakGlassNeverChangesAuthority`,
under `"R7" ∈ Active`. -/
theorem NeverChangesAuthority (Active : PSet EntryName) (hR7 : EntryName.R7 ∈ Active) (MaxEpoch : Nat) :
    ∀ st, Reachable Init (Next .none Active MaxEpoch) st → BreakGlassNeverChangesAuthority st :=
  invariant (Inv Active) BreakGlassNeverChangesAuthority (InitInv Active) (NextInv Active hR7 MaxEpoch)
    (fun _ h => h.2)

/-- `MutAdmitsAuthority`: with the envelope ignored, every authority action is admitted. -/
theorem MutAdmitsAuthority (st : State) (x : BGAct) (hx : x ∈ AuthActs) : x ∈ BGActs ∧ Admits .M_SCOPE st x := by
  refine ⟨Or.inl hx, ?_⟩
  unfold Admits; rw [if_pos rfl]; exact Or.inl hx

#print axioms NeverChangesAuthority

end Topak.Spec.BreakGlass
