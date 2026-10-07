import TopakSpec.Prelude
/-!
# FloorRouting.tla in Lean

ADR-0030 §5: floor revisions classified mechanically and routed. `spec/FloorRouting.tla` re-encoded;
`spec/FloorRouting_proof.tla`'s theorems proved by induction on reachable states. A floor is the set of
requests it permits over `U`; a proposal (`new ∈ SUBSET U`) is any predicate on `U`. The two-valued
`Route(new, old)` is the predicate `RoutesPromote`: `Route = "promote"` is `RoutesPromote`, `Route =
"issue"` is its negation.

Mutations: `M_ROUTE`, only a strict superset is a relaxation; `M_GATE`, the non-vacuity gate is off. As in
the TLAPS module, the theorems take `Mut = "none"`.
-/

namespace Topak.Spec.FloorRouting
open Topak.Spec PSet

inductive Mut | none | M_ROUTE | M_GATE
  deriving DecidableEq

/-- `U == {"r1", "r2", "r3"}` -/
inductive Req | r1 | r2 | r3
  deriving DecidableEq

def U : PSet Req := univ
/-- `Genesis == {"r1"}` -/
def Genesis : PSet Req := {.r1}

/-- `VARIABLES deployed, wideNoIssue, sawIncomparable, sawRelaxIssued, sawTighten` -/
structure State where
  deployed : PSet Req
  wideNoIssue : Prop
  sawIncomparable : Prop
  sawRelaxIssued : Prop
  sawTighten : Prop

/-- `Init == deployed = Genesis /\ wideNoIssue = FALSE /\ sawIncomparable = FALSE /\ ...` -/
def Init (st : State) : Prop :=
  st.deployed = Genesis ∧ ¬ st.wideNoIssue ∧ ¬ st.sawIncomparable ∧ ¬ st.sawRelaxIssued ∧ ¬ st.sawTighten

/-- `NewImpliesOld(new, old) == new ⊆ old` -/
def NewImpliesOld (new old : PSet Req) : Prop := new ⊆ old
/-- `OldImpliesNew(new, old) == old ⊆ new` -/
def OldImpliesNew (new old : PSet Req) : Prop := old ⊆ new

/-- ```
Route(new, old) ==
  IF Mut = "M_ROUTE"
    THEN IF OldImpliesNew(new, old) /\ ~NewImpliesOld(new, old) THEN "issue" ELSE "promote"
    ELSE IF NewImpliesOld(new, old) THEN "promote" ELSE "issue"
```
as the predicate "Route(new, old) = "promote"". -/
def RoutesPromote (m : Mut) (new old : PSet Req) : Prop :=
  if m = .M_ROUTE then ¬ (OldImpliesNew new old ∧ ¬ NewImpliesOld new old) else NewImpliesOld new old

/-- `PassesGates(new) == IF Mut = "M_GATE" THEN TRUE ELSE new # U` -/
def PassesGates (m : Mut) (new : PSet Req) : Prop := if m = .M_GATE then True else new ≠ U

/-- `Incomparable(new, old) == ~NewImpliesOld(new, old) /\ ~OldImpliesNew(new, old)` -/
def Incomparable (new old : PSet Req) : Prop := ¬ NewImpliesOld new old ∧ ¬ OldImpliesNew new old

/-- ```
Promote(new) ==
  /\ PassesGates(new)
  /\ Route(new, deployed) = "promote"
  /\ deployed' = new
  /\ wideNoIssue' = (wideNoIssue \/ ~(new ⊆ deployed))
  /\ sawIncomparable' = (sawIncomparable \/ Incomparable(new, deployed))
  /\ sawTighten' = (sawTighten \/ (new ⊆ deployed /\ new # deployed))
  /\ UNCHANGED sawRelaxIssued
``` -/
def Promote (m : Mut) (new : PSet Req) (st st' : State) : Prop :=
  PassesGates m new ∧
  RoutesPromote m new st.deployed ∧
  st'.deployed = new ∧
  (st'.wideNoIssue ↔ (st.wideNoIssue ∨ ¬ new ⊆ st.deployed)) ∧
  (st'.sawIncomparable ↔ (st.sawIncomparable ∨ Incomparable new st.deployed)) ∧
  (st'.sawTighten ↔ (st.sawTighten ∨ (new ⊆ st.deployed ∧ new ≠ st.deployed))) ∧
  (st'.sawRelaxIssued ↔ st.sawRelaxIssued)

/-- ```
IssueAndPromote(new) ==
  /\ PassesGates(new)
  /\ Route(new, deployed) = "issue"
  /\ deployed' = new
  /\ sawIncomparable' = (sawIncomparable \/ Incomparable(new, deployed))
  /\ sawRelaxIssued' = TRUE
  /\ UNCHANGED <<wideNoIssue, sawTighten>>
``` -/
def IssueAndPromote (m : Mut) (new : PSet Req) (st st' : State) : Prop :=
  PassesGates m new ∧
  ¬ RoutesPromote m new st.deployed ∧
  st'.deployed = new ∧
  (st'.sawIncomparable ↔ (st.sawIncomparable ∨ Incomparable new st.deployed)) ∧
  st'.sawRelaxIssued ∧
  (st'.wideNoIssue ↔ st.wideNoIssue) ∧ (st'.sawTighten ↔ st.sawTighten)

/-- `Next == ∃ new ∈ SUBSET U : Promote(new) \/ IssueAndPromote(new)` -/
def Next (m : Mut) (st st' : State) : Prop :=
  ∃ new : PSet Req, Promote m new st st' ∨ IssueAndPromote m new st st'

/-! ## The two properties -/

/-- `NoWideningWithoutIssuance == ~wideNoIssue` -/
def NoWideningWithoutIssuance (st : State) : Prop := ¬ st.wideNoIssue
/-- `FloorNeverVacuous == deployed # U` -/
def FloorNeverVacuous (st : State) : Prop := st.deployed ≠ U

def Safe (st : State) : Prop := NoWideningWithoutIssuance st ∧ FloorNeverVacuous st

/-! ## Proofs -/

theorem InitSafe (st : State) (h : Init st) : Safe st := by
  obtain ⟨hd, hw, -, -, -⟩ := h
  refine ⟨hw, ?_⟩
  unfold FloorNeverVacuous
  rw [hd]
  intro h
  have : Req.r2 ∈ Genesis := by rw [h]; trivial
  simp [Genesis] at this

/-- `PromoteNarrows`: under the specified routing, a promotion is a floor that implies the deployed one. -/
theorem PromoteNarrows (new old : PSet Req) (h : RoutesPromote .none new old) : new ⊆ old := by
  unfold RoutesPromote at h
  rw [if_neg (by decide)] at h
  exact h

theorem NextSafe (st st' : State) (hs : Safe st) (hn : Next .none st st') : Safe st' := by
  obtain ⟨hw, -⟩ := hs
  obtain ⟨new, h⟩ := hn
  rcases h with ⟨hg, hr, hd, hwide, -, -, -⟩ | ⟨hg, -, hd, -, -, hwide, -⟩
  · refine ⟨?_, ?_⟩
    · intro h'
      rcases hwide.mp h' with h' | h'
      · exact hw h'
      · exact h' (PromoteNarrows new st.deployed hr)
    · unfold FloorNeverVacuous
      rw [hd]
      unfold PassesGates at hg
      rw [if_neg (by decide)] at hg
      exact hg
  · refine ⟨fun h' => hw (hwide.mp h'), ?_⟩
    unfold FloorNeverVacuous
    rw [hd]
    unfold PassesGates at hg
    rw [if_neg (by decide)] at hg
    exact hg

/-- `THEOREM SafeAlways == ASSUME Mut = "none" PROVE Spec => []Safe` -/
theorem SafeAlways : ∀ st, Reachable Init (Next .none) st → Safe st :=
  invariant Safe Safe InitSafe NextSafe (fun _ h => h)

/-- `THEOREM NoWideningAlways == ASSUME Mut = "none" PROVE Spec => []NoWideningWithoutIssuance` -/
theorem NoWideningAlways : ∀ st, Reachable Init (Next .none) st → NoWideningWithoutIssuance st :=
  fun st h => (SafeAlways st h).1

/-- `THEOREM NeverVacuousAlways == ASSUME Mut = "none" PROVE Spec => []FloorNeverVacuous` -/
theorem NeverVacuousAlways : ∀ st, Reachable Init (Next .none) st → FloorNeverVacuous st :=
  fun st h => (SafeAlways st h).2

/-! ## Why the mutations must fail (the counterexamples are TLC's) -/

/-- `MutGateAdmitsU`: with the gate off, the vacuous floor passes. -/
theorem MutGateAdmitsU : PassesGates .M_GATE U := by
  unfold PassesGates; rw [if_pos rfl]; trivial

/-- `MutRoutePromotesIncomparable`: under M_ROUTE an incomparable floor rides the promotion path. -/
theorem MutRoutePromotesIncomparable (new old : PSet Req) (h : Incomparable new old) :
    RoutesPromote .M_ROUTE new old := by
  unfold RoutesPromote; rw [if_pos rfl]
  exact fun ⟨ho, _⟩ => h.2 ho

#print axioms SafeAlways
#print axioms NoWideningAlways
#print axioms NeverVacuousAlways

end Topak.Spec.FloorRouting
