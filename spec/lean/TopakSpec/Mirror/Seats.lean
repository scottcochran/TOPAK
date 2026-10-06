import TopakSpec.Seats
/-!
# A decidable mirror of the `Seats` encoding, for checking it against TLC's state graph

`TopakSpec/Seats.lean` states `Seats.tla` with sets as predicates and `live` as a `Prop`, so its `Next` cannot be
evaluated. This file gives a concrete state, `CState`, with Booleans and Boolean functions, a map `toState` into the
encoding's states, and a list of successors, `succC`, and proves:

- `next_iff`: from `toState c`, the encoding's `Next m` reaches exactly the states `toState d` for `d` in
  `succC m c`. So a TLC edge is a `Next` step iff its target is in the list, and every `Next` step is one of the
  list's;
- `init_iff`: a state satisfies the encoding's `Init` iff it is `toState cInit`;
- `ota_iff`, `osp_iff`: the two properties, as Booleans.

`spec/lean/GraphCheck.lean` evaluates these on TLC's dumped state graph (`graph-check.sh`). The theorems here are
proved; the evaluation is a test.
-/

namespace Topak.Spec.Seats.Mirror
open Topak.Spec Topak.Spec.Seats

def seats : List Seat := [.s1, .s2, .s3]
def principals : List Principal := [.p1, .p2]
def acts : List Act := [.Read, .Draft, .Emit, .Vote]
def kinds : List Kind := [.thinker, .observer, .grant]

theorem mem_seats (s : Seat) : s ∈ seats := by cases s <;> simp [seats]
theorem mem_principals (p : Principal) : p ∈ principals := by cases p <;> simp [principals]
theorem mem_acts (a : Act) : a ∈ acts := by cases a <;> simp [acts]
theorem mem_kinds (k : Kind) : k ∈ kinds := by cases k <;> simp [kinds]

/-- A lease record, its `live` a Boolean and its alphabet a Boolean function. -/
structure CLease where
  live : Bool
  principal : Option Principal
  alphabet : Act → Bool

/-- A state: each seat's lease, and `acted` as a Boolean function of an act and a kind. -/
structure CState where
  lease : Seat → CLease
  acted : Act → Kind → Bool

def toLease (l : CLease) : LeaseRec := ⟨l.live = true, l.principal, fun a => l.alphabet a = true⟩

def toState (c : CState) : State := ⟨fun s => toLease (c.lease s), fun r => c.acted r.act r.kind = true⟩

def leaseEq (l m : CLease) : Bool :=
  l.live == m.live && l.principal == m.principal && acts.all fun a => l.alphabet a == m.alphabet a

def eqC (c d : CState) : Bool :=
  seats.all (fun s => leaseEq (c.lease s) (d.lease s)) && acts.all fun a => kinds.all fun k => c.acted a k == d.acted a k

theorem bool_eq_of_prop {a b : Bool} (h : (a = true) = (b = true)) : a = b := by
  cases a <;> cases b <;> simp_all

theorem toLease_inj {l m : CLease} : toLease l = toLease m ↔ leaseEq l m = true := by
  constructor
  · intro h
    simp only [toLease, LeaseRec.mk.injEq] at h
    obtain ⟨h1, h2, h3⟩ := h
    simp only [leaseEq, Bool.and_eq_true, beq_iff_eq, List.all_eq_true]
    exact ⟨⟨bool_eq_of_prop h1, h2⟩, fun a _ => bool_eq_of_prop (congrFun h3 a)⟩
  · intro h
    simp only [leaseEq, Bool.and_eq_true, beq_iff_eq, List.all_eq_true] at h
    obtain ⟨⟨h1, h2⟩, h3⟩ := h
    simp only [toLease, h1, h2]
    congr 1
    funext a
    rw [h3 a (mem_acts a)]

theorem eqC_iff (c d : CState) : eqC c d = true ↔ toState c = toState d := by
  simp only [eqC, Bool.and_eq_true, List.all_eq_true, beq_iff_eq, toState, State.mk.injEq]
  constructor
  · rintro ⟨h1, h2⟩
    refine ⟨funext fun s => toLease_inj.mpr (h1 s (mem_seats s)), funext fun r => ?_⟩
    rw [h2 r.act (mem_acts _) r.kind (mem_kinds _)]
  · rintro ⟨h1, h2⟩
    refine ⟨fun s _ => toLease_inj.mp (congrFun h1 s), fun a _ k _ => bool_eq_of_prop (congrFun h2 ⟨a, k⟩)⟩

/-! ## Updates -/

def NoLeaseC : CLease := ⟨false, none, fun _ => false⟩

theorem toLease_none : toLease NoLeaseC = NoLease := by
  simp only [toLease, NoLeaseC, NoLease, Bool.false_eq_true]
  rfl

def updL (f : Seat → CLease) (s : Seat) (l : CLease) : Seat → CLease := fun t => if t = s then l else f t

theorem toState_lease (c : CState) (s : Seat) (l : CLease) :
    (toState { c with lease := updL c.lease s l }).lease = upd (toState c).lease s (toLease l) := by
  funext t
  simp only [toState, updL, upd]
  split <;> rfl

def updActed (f : Act → Kind → Bool) (a : Act) (k : Kind) : Act → Kind → Bool :=
  fun a' k' => (a' == a && k' == k) || f a' k'

theorem toState_acted (c : CState) (a : Act) (k : Kind) :
    (toState { c with acted := updActed c.acted a k }).acted = (toState c).acted ∪ {⟨a, k⟩} := by
  apply PSet.ext
  intro r
  cases r with
  | mk a' k' =>
    show ((a' == a && k' == k) || c.acted a' k') = true ↔ c.acted a' k' = true ∨ (⟨a', k'⟩ : ActRec) = ⟨a, k⟩
    simp only [Bool.or_eq_true, Bool.and_eq_true, beq_iff_eq, ActRec.mk.injEq]
    exact Or.comm

/-! ## The kind bound and the hold, as Booleans -/

def kbB : Kind → Act → Bool
  | .thinker, a => a == .Read || a == .Draft || a == .Emit
  | .observer, a => a == .Read || a == .Emit || a == .Vote
  | .grant, a => a == .Read || a == .Emit || a == .Vote

theorem kbB_eq (k : Kind) : (fun a => kbB k a = true) = KindBound k := by
  funext a
  apply propext
  show kbB k a = true ↔ a ∈ KindBound k
  cases k <;> cases a <;> simp [kbB, KindBound]

def heldB (c : CState) (p : Principal) (s : Seat) : Bool :=
  seats.any fun t => decide (t ≠ s) && (c.lease t).live && (c.lease t).principal == some p

theorem heldB_iff (c : CState) (p : Principal) (s : Seat) : heldB c p s = true ↔ HoldsElsewhere (toState c) p s := by
  simp only [heldB, List.any_eq_true, Bool.and_eq_true, decide_eq_true_eq, beq_iff_eq, HoldsElsewhere, toState,
    toLease]
  constructor
  · rintro ⟨t, -, ⟨h1, h2⟩, h3⟩; exact ⟨t, h1, h2, h3⟩
  · rintro ⟨t, h1, h2, h3⟩; exact ⟨t, mem_seats t, ⟨h1, h2⟩, h3⟩

/-- The alphabet a grant issues. -/
def grantAlpha (m : Mut) (s : Seat) : Act → Bool := if m = .M_KIND then fun _ => true else kbB (KindOf s)

theorem grantAlpha_eq (m : Mut) (s : Seat) :
    (fun a => grantAlpha m s a = true) = (if m = .M_KIND then Acts else KindBound (KindOf s)) := by
  unfold grantAlpha
  split
  · funext a; exact propext ⟨fun _ => trivial, fun _ => rfl⟩
  · exact kbB_eq _

/-! ## The successors -/

def actSucc (c : CState) : List CState :=
  seats.flatMap fun s =>
    if (c.lease s).live then (acts.filter (c.lease s).alphabet).map fun a => { c with acted := updActed c.acted a (KindOf s) }
    else []

def endSucc (c : CState) : List CState :=
  seats.filterMap fun s => if (c.lease s).live then some { c with lease := updL c.lease s NoLeaseC } else none

def grantSucc (m : Mut) (c : CState) : List CState :=
  seats.flatMap fun s => principals.filterMap fun p =>
    if !(c.lease s).live && (decide (m = .M_SEAT) || !heldB c p s) then
      some { c with lease := updL c.lease s ⟨true, some p, grantAlpha m s⟩ }
    else none

def succC (m : Mut) (c : CState) : List CState := actSucc c ++ endSucc c ++ grantSucc m c

theorem state_ext {S T : State} (h1 : S.lease = T.lease) (h2 : S.acted = T.acted) : S = T := by
  cases S; cases T; simp only at h1 h2; subst h1; subst h2; rfl

theorem next_iff (m : Mut) (c : CState) (S : State) :
    Next m (toState c) S ↔ ∃ d, d ∈ succC m c ∧ S = toState d := by
  constructor
  · rintro ⟨s, hs⟩
    rcases hs with ⟨hlive, ⟨a, ha, hacted⟩, hlease⟩ | ⟨hlive, hlease, hacted⟩ | ⟨p, hfree, hhold, hlease, hacted⟩
    · -- Act(s)
      refine ⟨{ c with acted := updActed c.acted a (KindOf s) }, ?_, ?_⟩
      · have hl : (c.lease s).live = true := hlive
        have ha' : (c.lease s).alphabet a = true := ha
        simp only [succC, List.mem_append, actSucc, List.mem_flatMap]
        refine Or.inl (Or.inl ⟨s, mem_seats s, ?_⟩)
        rw [if_pos hl]
        exact List.mem_map.mpr ⟨a, List.mem_filter.mpr ⟨mem_acts a, ha'⟩, rfl⟩
      · exact state_ext hlease (by rw [hacted, toState_acted])
    · -- EndRound(s)
      refine ⟨{ c with lease := updL c.lease s NoLeaseC }, ?_, ?_⟩
      · have hl : (c.lease s).live = true := hlive
        simp only [succC, List.mem_append, endSucc, List.mem_filterMap]
        exact Or.inl (Or.inr ⟨s, mem_seats s, by rw [if_pos hl]⟩)
      · exact state_ext (by rw [hlease, toState_lease, toLease_none]) hacted
    · -- Grant(p, s)
      refine ⟨{ c with lease := updL c.lease s ⟨true, some p, grantAlpha m s⟩ }, ?_, ?_⟩
      · have hl : (c.lease s).live = false := by
          cases h : (c.lease s).live
          · rfl
          · exact absurd h hfree
        have hg : (decide (m = .M_SEAT) || !heldB c p s) = true := by
          rcases hhold with h | h
          · simp [h]
          · have : heldB c p s = false := by
              cases hb : heldB c p s
              · rfl
              · exact absurd ((heldB_iff c p s).mp hb) h
            simp [this]
        simp only [succC, List.mem_append, grantSucc, List.mem_flatMap, List.mem_filterMap]
        refine Or.inr ⟨s, mem_seats s, p, mem_principals p, ?_⟩
        rw [if_pos (by simp [hl, hg])]
      · refine state_ext ?_ hacted
        rw [hlease, toState_lease]
        congr 1
        simp only [toLease, grantAlpha_eq]
  · rintro ⟨d, hd, rfl⟩
    simp only [succC, List.mem_append] at hd
    rcases hd with (hd | hd) | hd
    · simp only [actSucc, List.mem_flatMap] at hd
      obtain ⟨s, -, hs⟩ := hd
      split at hs
      · rename_i hl
        obtain ⟨a, ha, rfl⟩ := List.mem_map.mp hs
        refine ⟨s, Or.inl ⟨hl, ⟨a, (List.mem_filter.mp ha).2, ?_⟩, rfl⟩⟩
        rw [toState_acted]
      · cases hs
    · simp only [endSucc, List.mem_filterMap] at hd
      obtain ⟨s, -, hs⟩ := hd
      split at hs
      · rename_i hl
        cases hs
        refine ⟨s, Or.inr (Or.inl ⟨hl, ?_, rfl⟩)⟩
        rw [toState_lease, toLease_none]
      · cases hs
    · simp only [grantSucc, List.mem_flatMap, List.mem_filterMap] at hd
      obtain ⟨s, -, p, -, hs⟩ := hd
      split at hs
      · rename_i hc
        cases hs
        simp only [Bool.and_eq_true, Bool.not_eq_true', Bool.or_eq_true, decide_eq_true_eq] at hc
        obtain ⟨hl, hg⟩ := hc
        refine ⟨s, Or.inr (Or.inr ⟨p, ?_, ?_, ?_, rfl⟩)⟩
        · show ¬ ((c.lease s).live = true)
          rw [hl]; exact Bool.false_ne_true
        · rcases hg with h | h
          · exact Or.inl h
          · exact Or.inr fun hh => by rw [(heldB_iff c p s).mpr hh] at h; cases h
        · rw [toState_lease]
          congr 1
          simp only [toLease, grantAlpha_eq]
      · cases hs

/-! ## `Init` and the properties -/

def cInit : CState := ⟨fun _ => NoLeaseC, fun _ _ => false⟩

theorem init_iff (S : State) : Init S ↔ S = toState cInit := by
  have hacted : (toState cInit).acted = ∅ := by
    funext r; exact propext ⟨fun h => Bool.false_ne_true h, fun h => h.elim⟩
  constructor
  · rintro ⟨h1, h2⟩
    refine state_ext ?_ ?_
    · rw [h1]; funext s; exact toLease_none.symm
    · rw [h2, hacted]
  · rintro rfl
    exact ⟨funext fun _ => toLease_none, hacted⟩

theorem all_ak (f : Act → Kind → Bool) : (acts.all fun a => kinds.all fun k => f a k) = true ↔ ∀ a k, f a k = true := by
  simp only [List.all_eq_true]
  exact ⟨fun h a k => h a (mem_acts a) k (mem_kinds k), fun h a _ k _ => h a k⟩

theorem all_ss (f : Seat → Seat → Bool) : (seats.all fun s => seats.all fun t => f s t) = true ↔ ∀ s t, f s t = true := by
  simp only [List.all_eq_true]
  exact ⟨fun h s t => h s (mem_seats s) t (mem_seats t), fun h s _ t _ => h s t⟩

def otaB (c : CState) : Bool :=
  acts.all fun a => kinds.all fun k =>
    !c.acted a k || ((a != .Draft || k == .thinker) && (a != .Vote || k != .thinker))

theorem ota_one (x : Bool) (a : Act) (k : Kind) :
    (!x || ((a != .Draft || k == .thinker) && (a != .Vote || k != .thinker))) = true ↔
      (x = true → (a ∈ Authoring → k = .thinker) ∧ (a = .Vote → k ≠ .thinker)) := by
  cases x <;> cases a <;> cases k <;> simp [Authoring]

theorem ota_iff (c : CState) : otaB c = true ↔ OnlyThinkersAuthor (toState c) := by
  unfold otaB
  rw [all_ak]
  simp only [ota_one]
  constructor
  · intro h r hr; exact h r.act r.kind hr
  · intro h a k hx; exact h ⟨a, k⟩ hx

def ospB (c : CState) : Bool :=
  seats.all fun s => seats.all fun t =>
    !(decide (s ≠ t) && (c.lease s).live && (c.lease t).live) || (c.lease s).principal != (c.lease t).principal

theorem osp_one (s t : Seat) (ls lt : Bool) (ps pt : Option Principal) :
    (!(decide (s ≠ t) && ls && lt) || ps != pt) = true ↔ (s ≠ t ∧ ls = true ∧ lt = true → ps ≠ pt) := by
  cases ls <;> cases lt <;> by_cases h : s = t <;> simp [h]

theorem osp_iff (c : CState) : ospB c = true ↔ OneSeatPerPrincipal (toState c) := by
  unfold ospB
  rw [all_ss]
  simp only [osp_one]
  exact Iff.rfl

end Topak.Spec.Seats.Mirror


#print axioms Topak.Spec.Seats.Mirror.next_iff
#print axioms Topak.Spec.Seats.Mirror.init_iff
#print axioms Topak.Spec.Seats.Mirror.eqC_iff
#print axioms Topak.Spec.Seats.Mirror.ota_iff
#print axioms Topak.Spec.Seats.Mirror.osp_iff
