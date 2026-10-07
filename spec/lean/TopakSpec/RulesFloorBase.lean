import TopakSpec.Prelude
/-!
# RulesFloorBase.tla in Lean

Shared definitions for the ADR-0029 §5 bootstrap modules: the rule space, the rules-floor entries and the
genesis rules. `spec/RulesFloorBase.tla` re-encoded. Its constant `Active`, the entries in force, is a
parameter of `Floor`; its one `ASSUME`, that genesis satisfies every entry, is the theorem
`GenesisEntries`. The TLAPS proofs' `ActiveEntries == Active ⊆ AllEntries` has no counterpart: `Active`
is a set of `EntryName`, so it is within `AllEntries` by type.
-/

namespace Topak.Spec.RulesFloorBase
open Topak.Spec PSet

/-- `Humans == {"h1", "h2", "h3", "h4", "h5"}` -/
inductive Human | h1 | h2 | h3 | h4 | h5
  deriving DecidableEq
def Humans : PSet Human := univ
/-- `Author == "h1"` -/
def Author : Human := .h1
/-- `AnchorKeys == {"h4"}` -/
def AnchorKeys : PSet Human := {.h4}

/-- `BGActs == AuthActs ∪ {"Op"}`, as a type. -/
inductive BGAct | Issue | Vote | Promote | Op
  deriving DecidableEq
/-- `AuthActs == {"Issue", "Vote", "Promote"}` -/
def AuthActs : PSet BGAct := {.Issue, .Vote, .Promote}
def BGActs : PSet BGAct := AuthActs ∪ {.Op}

inductive QMode | all | k
  deriving DecidableEq
/-- `QVals == [mode : {"all", "k"}, k : 0..4]` -/
structure QVal where
  mode : QMode
  k : Nat
def QVals : PSet QVal := fun q => q.k ≤ 4

/-- The record type of `RuleSpace`. -/
structure Rules where
  grant : PSet Human
  quorum : QVal
  minGrant : Nat
  bgScope : PSet BGAct
  exceptions : Nat

/-- ```
RuleSpace == [grant : SUBSET Humans, quorum : QVals, minGrant : 0..2, bgScope : SUBSET BGActs, exceptions : 0..3]
``` -/
def RuleSpace : PSet Rules := fun r => r.quorum ∈ QVals ∧ r.minGrant ≤ 2 ∧ r.exceptions ≤ 3

/-- `AllEntries == {"R1", "R2", "R5", "R6", "R7", "R9"}`, as a type. -/
inductive EntryName | R1 | R2 | R5 | R6 | R7 | R9
  deriving DecidableEq
def AllEntries : PSet EntryName := univ

/-- ```
Entry(e, r) ==
  CASE e = "R1" -> r.quorum.mode = "all"
    [] e = "R2" -> r.minGrant >= 2
    [] e = "R5" -> r.grant ∩ AnchorKeys = {}
    [] e = "R6" -> r.exceptions <= 2
    [] e = "R7" -> r.bgScope ∩ AuthActs = {}
    [] e = "R9" -> r.quorum.mode = "all" \/ r.quorum.k >= 2
``` -/
def Entry : EntryName → Rules → Prop
  | .R1, r => r.quorum.mode = .all
  | .R2, r => r.minGrant ≥ 2
  | .R5, r => r.grant ∩ AnchorKeys = ∅
  | .R6, r => r.exceptions ≤ 2
  | .R7, r => r.bgScope ∩ AuthActs = ∅
  | .R9, r => r.quorum.mode = .all ∨ r.quorum.k ≥ 2

/-- `Floor(r) == ∀ e ∈ Active : Entry(e, r)` -/
def Floor (Active : PSet EntryName) (r : Rules) : Prop := ∀ e, e ∈ Active → Entry e r

/-- ```
Genesis == [grant |-> Humans \ ({Author} ∪ AnchorKeys), quorum |-> [mode |-> "all", k |-> 0],
            minGrant |-> 2, bgScope |-> {"Op"}, exceptions |-> 2]
``` -/
def Genesis : Rules :=
  ⟨Humans \ ({Author} ∪ AnchorKeys), ⟨.all, 0⟩, 2, {.Op}, 2⟩

/-- `ASSUME ∀ e ∈ AllEntries : Entry(e, Genesis)`, proved from the definitions as the TLAPS modules do. -/
theorem GenesisEntries : ∀ e, e ∈ AllEntries → Entry e Genesis := by
  intro e _
  cases e
  · rfl
  · show Genesis.minGrant ≥ 2; decide
  · rw [Entry, eq_empty_iff]
    intro a ha
    obtain ⟨h1, h2⟩ := (mem_inter _ _ _).mp ha
    cases a <;> simp_all [Genesis, AnchorKeys, Author, Humans]
  · show Genesis.exceptions ≤ 2; decide
  · rw [Entry, eq_empty_iff]
    intro a ha
    obtain ⟨h1, h2⟩ := (mem_inter _ _ _).mp ha
    cases a <;> simp_all [Genesis, AuthActs]
  · exact Or.inl rfl

/-- `GenesisFloor`: genesis satisfies whatever floor is in force. -/
theorem GenesisFloor (Active : PSet EntryName) : Floor Active Genesis :=
  fun e _ => GenesisEntries e trivial

theorem genesis_in_RuleSpace : Genesis ∈ RuleSpace :=
  ⟨show Genesis.quorum.k ≤ 4 by decide, show Genesis.minGrant ≤ 2 by decide, show Genesis.exceptions ≤ 3 by decide⟩

end Topak.Spec.RulesFloorBase
