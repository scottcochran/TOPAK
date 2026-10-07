import TopakSpec.FloorComposition
/-!
# A decidable mirror of the `FloorComposition` encoding, for checking it against TLC's state graph

As `Mirror/Seats.lean`: a concrete state with the seven flags as Booleans, `toState` into the encoding's states,
the successors `succC`, and `next_iff`, `init_iff` and one Boolean per property, each proved equal to the encoding's.
The engine's and the bundle's predicates are decidable as the encoding states them, so `decide` evaluates them.
-/

namespace Topak.Spec.FloorComposition.Mirror
open Topak.Spec Topak.Spec.FloorComposition

def seats : List Seat := [.s1, .s2]
def targets : List Target := [.t1, .t2]
def acts : List Act := [.Read, .Draft, .Emit]
def bouts : List BOut := [.allow, .deny, .error, .undefined, .absent, .unreachable]
def drops : List Drop := [.no, .owner, .sealed]

theorem mem_seats (s : Seat) : s ∈ seats := by cases s <;> simp [seats]
theorem mem_targets (t : Target) : t ∈ targets := by cases t <;> simp [targets]
theorem mem_acts (a : Act) : a ∈ acts := by cases a <;> simp [acts]
theorem mem_bouts (b : BOut) : b ∈ bouts := by cases b <;> simp [bouts]
theorem mem_drops (d : Drop) : d ∈ drops := by cases d <;> simp [drops]

structure CState where
  truth : Target → Rec
  fstore : Target → Rec
  noFloor : Bool
  withErr : Bool
  noBundle : Bool
  outside : Bool
  sawAdmit : Bool
  sawNarrow : Bool
  sawFloorErr : Bool

abbrev toState (c : CState) : State :=
  ⟨c.truth, c.fstore, c.noFloor = true, c.withErr = true, c.noBundle = true, c.outside = true, c.sawAdmit = true,
   c.sawNarrow = true, c.sawFloorErr = true⟩

def eqC (c d : CState) : Bool :=
  targets.all (fun t => c.truth t == d.truth t && c.fstore t == d.fstore t) &&
    c.noFloor == d.noFloor && c.withErr == d.withErr && c.noBundle == d.noBundle && c.outside == d.outside &&
    c.sawAdmit == d.sawAdmit && c.sawNarrow == d.sawNarrow && c.sawFloorErr == d.sawFloorErr

theorem bool_eq_of_prop {a b : Bool} (h : (a = true) = (b = true)) : a = b := by
  cases a <;> cases b <;> simp_all

theorem eqC_iff (c d : CState) : eqC c d = true ↔ toState c = toState d := by
  simp only [eqC, Bool.and_eq_true, List.all_eq_true, beq_iff_eq, toState, State.mk.injEq]
  constructor
  · rintro ⟨⟨⟨⟨⟨⟨⟨h, h1⟩, h2⟩, h3⟩, h4⟩, h5⟩, h6⟩, h7⟩
    refine ⟨funext fun t => (h t (mem_targets t)).1, funext fun t => (h t (mem_targets t)).2, ?_⟩
    simp [h1, h2, h3, h4, h5, h6, h7]
  · rintro ⟨h1, h2, h3, h4, h5, h6, h7, h8, h9⟩
    exact ⟨⟨⟨⟨⟨⟨⟨fun t _ => ⟨congrFun h1 t, congrFun h2 t⟩, bool_eq_of_prop h3⟩, bool_eq_of_prop h4⟩,
      bool_eq_of_prop h5⟩, bool_eq_of_prop h6⟩, bool_eq_of_prop h7⟩, bool_eq_of_prop h8⟩, bool_eq_of_prop h9⟩

/-! ## The encoding's predicates are decidable as stated -/

instance (e : Rec) (p : Seat) (a : Act) : Decidable (EngineAllow e p a) := by unfold EngineAllow; infer_instance
instance (e : Rec) (p : Seat) (a : Act) : Decidable (EngineErr e p a) := by unfold EngineErr; infer_instance
instance (m : Mut) (e : Rec) (p : Seat) (a : Act) : Decidable (FloorPermit m e p a) := by
  unfold FloorPermit; split <;> infer_instance
instance (m : Mut) (b : BOut) : Decidable (BundleDeny m b) := by unfold BundleDeny; split <;> infer_instance
instance (m : Mut) (e : Rec) (p : Seat) (a : Act) (b : BOut) : Decidable (Admit m e p a b) := by
  unfold Admit; split <;> infer_instance
instance (st : State) (p : Seat) (a : Act) (r : Target) : Decidable (Envelope st p a r) := by
  unfold Envelope; infer_instance

/-- `decided`, on the mirror: the flags after a decision whose admit is `ok`. -/
def decidedC (c : CState) (m : Mut) (e : Rec) (p : Seat) (a : Act) (r : Target) (b : BOut) (ok : Bool) : CState :=
  { c with
    noFloor := c.noFloor || (ok && !decide (EngineAllow e p a ∧ ¬ EngineErr e p a))
    withErr := c.withErr || (ok && decide (EngineErr e p a))
    noBundle := c.noBundle || (ok && decide (b ≠ .allow))
    outside := c.outside || (ok && !decide (Envelope (toState c) p a r))
    sawAdmit := c.sawAdmit || ok
    sawNarrow := c.sawNarrow || (decide (FloorPermit m e p a) && !ok)
    sawFloorErr := c.sawFloorErr || decide (EngineErr e p a) }

theorem toState_decided (c : CState) (m : Mut) (e : Rec) (p : Seat) (a : Act) (r : Target) (b : BOut) :
    toState (decidedC c m e p a r b (decide (Admit m e p a b))) = decided (toState c) m e p a r b (Admit m e p a b) := by
  simp only [toState, decidedC, decided, Bool.or_eq_true, Bool.and_eq_true, Bool.not_eq_true', decide_eq_true_eq,
    decide_eq_false_iff_not]

def succC (m : Mut) (c : CState) : List CState :=
  (targets.flatMap fun t => seats.map fun s =>
    { c with truth := upd c.truth t { c.truth t with owner := some s },
             fstore := upd c.fstore t { c.fstore t with owner := some s } }) ++
  (if m = .M_WRITE then targets.flatMap fun t => seats.map fun s =>
    { c with fstore := upd c.fstore t { c.fstore t with owner := some s } } else []) ++
  (targets.filterMap fun t => if (c.truth t).sealed = some false then
    some { c with truth := upd c.truth t { c.truth t with sealed := some true },
                  fstore := upd c.fstore t { c.fstore t with sealed := some true } } else none) ++
  (seats.flatMap fun p => acts.flatMap fun a => targets.flatMap fun r => bouts.flatMap fun b => drops.map fun d =>
    decidedC c m (Dropped (c.fstore r) d) p a r b (decide (Admit m (Dropped (c.fstore r) d) p a b)))

theorem next_iff (m : Mut) (c : CState) (S : State) :
    Next m (toState c) S ↔ ∃ d, d ∈ succC m c ∧ S = toState d := by
  constructor
  · rintro ((⟨t, s, h | ⟨hm, h⟩⟩) | ⟨t, hs, h⟩ | ⟨p, a, r, b, d, h⟩)
    · refine ⟨{ c with truth := upd c.truth t { c.truth t with owner := some s },
                       fstore := upd c.fstore t { c.fstore t with owner := some s } }, ?_, h⟩
      simp only [succC, List.mem_append, List.mem_flatMap, List.mem_map]
      exact Or.inl (Or.inl (Or.inl ⟨t, mem_targets t, s, mem_seats s, rfl⟩))
    · refine ⟨{ c with fstore := upd c.fstore t { c.fstore t with owner := some s } }, ?_, h⟩
      simp only [succC, List.mem_append, List.mem_flatMap, List.mem_map, if_pos hm]
      exact Or.inl (Or.inl (Or.inr ⟨t, mem_targets t, s, mem_seats s, rfl⟩))
    · refine ⟨{ c with truth := upd c.truth t { c.truth t with sealed := some true },
                       fstore := upd c.fstore t { c.fstore t with sealed := some true } }, ?_, h⟩
      simp only [succC, List.mem_append, List.mem_filterMap]
      exact Or.inl (Or.inr ⟨t, mem_targets t, by rw [if_pos hs]⟩)
    · refine ⟨decidedC c m (Dropped (c.fstore r) d) p a r b (decide (Admit m (Dropped (c.fstore r) d) p a b)), ?_, ?_⟩
      · simp only [succC, List.mem_append, List.mem_flatMap, List.mem_map]
        exact Or.inr ⟨p, mem_seats p, a, mem_acts a, r, mem_targets r, b, mem_bouts b, d, mem_drops d, rfl⟩
      · rw [h, toState_decided]
  · rintro ⟨d, hd, rfl⟩
    simp only [succC, List.mem_append, List.mem_flatMap, List.mem_map, List.mem_filterMap] at hd
    rcases hd with ((⟨t, -, s, -, rfl⟩ | hd) | ⟨t, -, hs⟩) | ⟨p, -, a, -, r, -, b, -, dr, -, rfl⟩
    · exact Or.inl ⟨t, s, Or.inl rfl⟩
    · split at hd
      · rename_i hm
        simp only [List.mem_flatMap, List.mem_map] at hd
        obtain ⟨t, -, s, -, rfl⟩ := hd
        exact Or.inl ⟨t, s, Or.inr ⟨hm, rfl⟩⟩
      · cases hd
    · split at hs
      · rename_i hseal
        cases hs
        exact Or.inr (Or.inl ⟨t, hseal, rfl⟩)
      · cases hs
    · refine Or.inr (Or.inr ⟨p, a, r, b, dr, ?_⟩)
      rw [toState_decided]

def cInit : CState := ⟨genesis, genesis, false, false, false, false, false, false, false⟩

theorem init_iff (S : State) : Init S ↔ S = toState cInit := by
  constructor
  · rintro ⟨h1, h2, h3, h4, h5, h6, h7, h8, h9⟩
    cases S
    simp only at h1 h2 h3 h4 h5 h6 h7 h8 h9
    simp only [toState, cInit, Bool.false_eq_true, State.mk.injEq]
    exact ⟨h1, h2, propext ⟨h3, False.elim⟩, propext ⟨h4, False.elim⟩, propext ⟨h5, False.elim⟩,
      propext ⟨h6, False.elim⟩, propext ⟨h7, False.elim⟩, propext ⟨h8, False.elim⟩, propext ⟨h9, False.elim⟩⟩
  · rintro rfl
    simp [Init, toState, cInit]

/-! ## The properties -/

def aifpB (c : CState) : Bool := !c.noFloor
def fedB (c : CState) : Bool := !c.withErr
def brhB (c : CState) : Bool := !c.noBundle
def bcwB (c : CState) : Bool := targets.all fun t => c.fstore t == c.truth t
def envB (c : CState) : Bool := !c.outside

theorem aifp_iff (c : CState) : aifpB c = true ↔ AdmitImpliesFloorPermit (toState c) := by
  simp [aifpB, AdmitImpliesFloorPermit, toState]
theorem fed_iff (c : CState) : fedB c = true ↔ FloorErrorIsDeny (toState c) := by
  simp [fedB, FloorErrorIsDeny, toState]
theorem brh_iff (c : CState) : brhB c = true ↔ BundleRefusalHonored (toState c) := by
  simp [brhB, BundleRefusalHonored, toState]
theorem env_iff (c : CState) : envB c = true ↔ EnvelopeHolds (toState c) := by
  simp [envB, EnvelopeHolds, toState]
theorem bcw_iff (c : CState) : bcwB c = true ↔ BundleCannotWriteFloorInputs (toState c) := by
  simp only [bcwB, List.all_eq_true, beq_iff_eq, BundleCannotWriteFloorInputs, toState]
  exact ⟨fun h => funext fun t => h t (mem_targets t), fun h t _ => congrFun h t⟩

end Topak.Spec.FloorComposition.Mirror

#print axioms Topak.Spec.FloorComposition.Mirror.next_iff
#print axioms Topak.Spec.FloorComposition.Mirror.init_iff
#print axioms Topak.Spec.FloorComposition.Mirror.eqC_iff
#print axioms Topak.Spec.FloorComposition.Mirror.aifp_iff
#print axioms Topak.Spec.FloorComposition.Mirror.fed_iff
#print axioms Topak.Spec.FloorComposition.Mirror.brh_iff
#print axioms Topak.Spec.FloorComposition.Mirror.bcw_iff
#print axioms Topak.Spec.FloorComposition.Mirror.env_iff
