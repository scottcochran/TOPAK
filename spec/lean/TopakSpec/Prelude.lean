/-!
# Prelude: TLA+ sets, EXCEPT, cardinality and `Spec => []P` in Lean

What every re-encoded module shares. A TLA+ module's state is a Lean structure; its `Init` is a predicate on
states; its `Next` is a relation between a state and its successor, one disjunct per action; `Spec => []P`
is `∀ s, Reachable Init Next s → P s`, proved by `invariant`, the induction TLAPS leaves to LS4.

Conventions, each a place where the Lean is not the TLA+ character for character:
- a TLA+ set is a predicate `PSet α := α → Prop`, so `SUBSET S` is every predicate and no finiteness is
  assumed where the module needs none; `{a, b}`, `∪`, `∩`, `\`, `⊆`, `∈`, `∅` are the usual notation;
- a string-valued constant set (`{"s1", "s2"}`) is an inductive type with one constructor per string;
- a BOOLEAN variable is a `Prop`, and `x' = (a \/ b)` is `(x' ↔ a ∨ b)`; `UNCHANGED x` is `x' = x`;
- `IF c THEN a ELSE b` with a decidable `c` (a constant, a Bool) is `if`; with an undecidable `c` (a set
  membership) it is the pair `(c → x = a) ∧ (¬c → x = b)`, so no classical choice enters a definition;
- `S # {}` is `NonEmpty S`, "some element is in S", which is how every module uses it;
- `Cardinality` is the relation `HasCard`, built up from the empty set one element at a time;
- stuttering steps (`[Next]_vars`) are dropped: an invariant is kept by a step that changes nothing.
-/

namespace Topak.Spec

/-! ## Sets as predicates -/

abbrev PSet (α : Type) := α → Prop

namespace PSet
variable {α : Type}

instance : Membership α (PSet α) := ⟨fun S a => S a⟩
instance : EmptyCollection (PSet α) := ⟨fun _ => False⟩
instance : Singleton α (PSet α) := ⟨fun x a => a = x⟩
instance : Insert α (PSet α) := ⟨fun x S a => a = x ∨ S a⟩
instance : Union (PSet α) := ⟨fun S T a => S a ∨ T a⟩
instance : Inter (PSet α) := ⟨fun S T a => S a ∧ T a⟩
instance : SDiff (PSet α) := ⟨fun S T a => S a ∧ ¬ T a⟩
instance : HasSubset (PSet α) := ⟨fun S T => ∀ a, a ∈ S → a ∈ T⟩

/-- The whole type: TLA+'s universe set for a constant set. -/
def univ : PSet α := fun _ => True

theorem mem_def (S : PSet α) (a : α) : (a ∈ S) = S a := rfl
@[simp] theorem mem_empty (a : α) : (a ∈ (∅ : PSet α)) ↔ False := Iff.rfl
@[simp] theorem mem_singleton (a x : α) : a ∈ ({x} : PSet α) ↔ a = x := Iff.rfl
@[simp] theorem mem_insert (a x : α) (S : PSet α) : a ∈ insert x S ↔ a = x ∨ a ∈ S := Iff.rfl
@[simp] theorem mem_union (a : α) (S T : PSet α) : a ∈ S ∪ T ↔ a ∈ S ∨ a ∈ T := Iff.rfl
@[simp] theorem mem_inter (a : α) (S T : PSet α) : a ∈ S ∩ T ↔ a ∈ S ∧ a ∈ T := Iff.rfl
@[simp] theorem mem_sdiff (a : α) (S T : PSet α) : a ∈ S \ T ↔ a ∈ S ∧ ¬ a ∈ T := Iff.rfl
@[simp] theorem mem_univ (a : α) : a ∈ (univ : PSet α) ↔ True := Iff.rfl
theorem subset_def (S T : PSet α) : (S ⊆ T) = ∀ a, a ∈ S → a ∈ T := rfl

theorem ext {S T : PSet α} (h : ∀ a, a ∈ S ↔ a ∈ T) : S = T := funext fun a => propext (h a)

/-- `S = {}`: no element. -/
theorem eq_empty_iff (S : PSet α) : S = ∅ ↔ ∀ a, ¬ a ∈ S := by
  constructor
  · intro h a ha; rw [h] at ha; exact ha
  · intro h; apply ext; intro a; exact ⟨fun ha => h a ha, fun h' => h'.elim⟩

/-- `S # {}`, read as "S has an element". The two are equal only classically, and this is the reading
every module uses `S # {}` for: a test that something is in the set. -/
def NonEmpty (S : PSet α) : Prop := ∃ a, a ∈ S

/-- `Cardinality S = n`, for a finite set built one element at a time. -/
inductive HasCard : PSet α → Nat → Prop
  | empty : HasCard ∅ 0
  | insert {S : PSet α} {n : Nat} (a : α) : HasCard S n → a ∉ S → HasCard (insert a S) (n + 1)

end PSet

/-! ## EXCEPT -/

/-- `[f EXCEPT ![x] = v]`. -/
def upd {α β : Type} [DecidableEq α] (f : α → β) (x : α) (v : β) : α → β :=
  fun y => if y = x then v else f y

@[simp] theorem upd_same {α β : Type} [DecidableEq α] (f : α → β) (x : α) (v : β) : upd f x v x = v := by
  simp [upd]

@[simp] theorem upd_other {α β : Type} [DecidableEq α] (f : α → β) (x y : α) (v : β) (h : y ≠ x) :
    upd f x v y = f y := by
  simp [upd, h]

theorem upd_apply {α β : Type} [DecidableEq α] (f : α → β) (x y : α) (v : β) :
    upd f x v y = if y = x then v else f y := rfl

/-! ## `Spec => []P` -/

/-- The states `Init /\ [][Next]_vars` reaches. -/
inductive Reachable {σ : Type} (Init : σ → Prop) (Next : σ → σ → Prop) : σ → Prop
  | init {s : σ} : Init s → Reachable Init Next s
  | step {s s' : σ} : Reachable Init Next s → Next s s' → Reachable Init Next s'

/-- The step TLAPS hands to LS4 (`BY ..., PTL DEF Spec`): `Init => Inv`, `Inv /\ [Next]_vars => Inv'`
and `Inv => P` give `Spec => []P`. Here it is induction on `Reachable`, checked by the kernel. -/
theorem invariant {σ : Type} {Init : σ → Prop} {Next : σ → σ → Prop} (Inv P : σ → Prop)
    (hinit : ∀ s, Init s → Inv s)
    (hstep : ∀ s s', Inv s → Next s s' → Inv s')
    (hP : ∀ s, Inv s → P s) :
    ∀ s, Reachable Init Next s → P s := by
  intro s h
  apply hP
  induction h with
  | init hi => exact hinit _ hi
  | step _ hn ih => exact hstep _ _ ih hn

end Topak.Spec
