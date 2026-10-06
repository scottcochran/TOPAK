import TopakSpec.Prelude
/-!
# FloorComposition.tla in Lean

ADR-0030 §1, §3, §4: monotone composition of a verified floor with an unverified bundle. `spec/FloorComposition.tla`
re-encoded; `spec/FloorComposition_proof.tla`'s six theorems proved by induction on reachable states, each under the
mutations that break it, as the TLAPS proof states them.

Encoding notes beyond the prelude's: the module's `NONE` is `Option.none`, so an entry's `owner` is `Option Seat` and
its `sealed` is `Option Bool` ("yes" is `some true`, "no" `some false`); a policy's result "T", "F" or "ERR" is `Res`;
the sets `Permits(e, p, a)` and `Forbids(e, a)` are lists, and `"T" \in S` is list membership. The seven flags are
`Prop`, and a successor is written `{ st with … }`, so `x' = (x \/ y)` is `x := x ∨ y`. The TLAPS proof's `TypeOK` is
not needed: an entry with `NONE` in the truth only makes a policy "ERR", which denies.

`mechanism/lean/Topak/FloorRefinement.lean` proves that the code's decision, the `topak-floor` wrapper and `compose`
together, is a `Decide` step of this module.
-/

namespace Topak.Spec.FloorComposition
open Topak.Spec PSet

inductive Mut | none | M_OVERRIDE | M_ERR | M_FAILOPEN | M_WRITE
  deriving DecidableEq

/-- `Seats == {"s1", "s2"}` -/
inductive Seat | s1 | s2
  deriving DecidableEq
/-- `Targets == {"t1", "t2"}` -/
inductive Target | t1 | t2
  deriving DecidableEq
/-- `Acts == {"Read", "Draft", "Emit"}` -/
inductive Act | Read | Draft | Emit
  deriving DecidableEq
/-- `BundleOutcomes == {"allow", "deny", "error", "undefined", "absent", "unreachable"}` -/
inductive BOut | allow | deny | error | undefined | absent | unreachable
  deriving DecidableEq
/-- A policy's result against a slice: "T", "F" or "ERR". -/
inductive Res | T | F | ERR
  deriving DecidableEq
/-- `drop \in {"no", "owner", "sealed"}` -/
inductive Drop | no | owner | sealed
  deriving DecidableEq

/-- `Rec(o, s) == [owner |-> o, sealed |-> s]`, with `NONE` as `none`. -/
structure Rec where
  owner : Option Seat
  sealed : Option Bool
  deriving DecidableEq

/-- `VARIABLES truth, fstore, admitNoFloor, admitWithErr, admitNoBundle, admitOutside, sawAdmit, sawNarrow, sawFloorErr` -/
structure State where
  truth : Target → Rec
  fstore : Target → Rec
  admitNoFloor : Prop
  admitWithErr : Prop
  admitNoBundle : Prop
  admitOutside : Prop
  sawAdmit : Prop
  sawNarrow : Prop
  sawFloorErr : Prop

/-- `truth = [t \in Targets |-> Rec(IF t = "t1" THEN "s1" ELSE "s2", "no")]` -/
def genesis : Target → Rec
  | .t1 => ⟨some .s1, some false⟩
  | .t2 => ⟨some .s2, some false⟩

/-- `Init`: `fstore = truth`, every flag `FALSE`. -/
def Init (st : State) : Prop :=
  st.truth = genesis ∧ st.fstore = genesis ∧ ¬ st.admitNoFloor ∧ ¬ st.admitWithErr ∧ ¬ st.admitNoBundle ∧
  ¬ st.admitOutside ∧ ¬ st.sawAdmit ∧ ¬ st.sawNarrow ∧ ¬ st.sawFloorErr

/-- `Reassign(t, s)`: the lift writes the owner to the truth and the floor's store together. -/
def Reassign (t : Target) (s : Seat) (st st' : State) : Prop :=
  st' = { st with truth := upd st.truth t { st.truth t with owner := some s },
                  fstore := upd st.fstore t { st.fstore t with owner := some s } }

/-- `Seal(t)`: `truth[t].sealed = "no"`, then the lift writes "yes" to both. -/
def Seal (t : Target) (st st' : State) : Prop :=
  (st.truth t).sealed = some false ∧
  st' = { st with truth := upd st.truth t { st.truth t with sealed := some true },
                  fstore := upd st.fstore t { st.fstore t with sealed := some true } }

/-- `BundleWrite(t, s)`: under `M_WRITE` only, a bundle writes the floor's store and not the truth. -/
def BundleWrite (m : Mut) (t : Target) (s : Seat) (st st' : State) : Prop :=
  m = .M_WRITE ∧ st' = { st with fstore := upd st.fstore t { st.fstore t with owner := some s } }

/-- `OwnerIs(e, p) == IF e.owner = NONE THEN "ERR" ELSE IF e.owner = p THEN "T" ELSE "F"` -/
def OwnerIs (e : Rec) (p : Seat) : Res :=
  match e.owner with
  | none => .ERR
  | some o => if o = p then .T else .F

/-- `SealedIs(e) == IF e.sealed = NONE THEN "ERR" ELSE IF e.sealed = "yes" THEN "T" ELSE "F"` -/
def SealedIs (e : Rec) : Res :=
  match e.sealed with
  | none => .ERR
  | some true => .T
  | some false => .F

/-- ```
Permits(e, p, a) == { IF a = "Read"  THEN "T" ELSE "F",
                      IF a = "Draft" THEN OwnerIs(e, p) ELSE "F",
                      IF a = "Emit"  THEN OwnerIs(e, p) ELSE "F" }
``` P1, P2 and P3. -/
def Permits (e : Rec) (p : Seat) (a : Act) : List Res :=
  [if a = .Read then .T else .F, if a = .Draft then OwnerIs e p else .F, if a = .Emit then OwnerIs e p else .F]

/-- `Forbids(e, a) == { IF a = "Emit" THEN SealedIs(e) ELSE "F" }`: F1. -/
def Forbids (e : Rec) (a : Act) : List Res := [if a = .Emit then SealedIs e else .F]

/-- `EngineAllow(e, p, a) == ("T" \notin Forbids(e, a)) /\ ("T" \in Permits(e, p, a))` -/
def EngineAllow (e : Rec) (p : Seat) (a : Act) : Prop := Res.T ∉ Forbids e a ∧ Res.T ∈ Permits e p a
/-- `EngineErr(e, p, a) == ("ERR" \in Forbids(e, a)) \/ ("ERR" \in Permits(e, p, a))` -/
def EngineErr (e : Rec) (p : Seat) (a : Act) : Prop := Res.ERR ∈ Forbids e a ∨ Res.ERR ∈ Permits e p a

/-- `FloorPermit(e, p, a) == IF Mut = "M_ERR" THEN EngineAllow(e, p, a) ELSE EngineAllow(e, p, a) /\ ~EngineErr(e, p, a)` -/
def FloorPermit (m : Mut) (e : Rec) (p : Seat) (a : Act) : Prop :=
  if m = .M_ERR then EngineAllow e p a else EngineAllow e p a ∧ ¬ EngineErr e p a

/-- `BundleDeny(b) == IF Mut = "M_FAILOPEN" THEN b = "deny" ELSE b # "allow"` -/
def BundleDeny (m : Mut) (b : BOut) : Prop := if m = .M_FAILOPEN then b = .deny else b ≠ .allow

/-- ```
Admit(e, p, a, b) == IF Mut = "M_OVERRIDE" THEN FloorPermit(e, p, a) \/ b = "allow"
                                            ELSE FloorPermit(e, p, a) /\ ~BundleDeny(b)
``` -/
def Admit (m : Mut) (e : Rec) (p : Seat) (a : Act) (b : BOut) : Prop :=
  if m = .M_OVERRIDE then FloorPermit m e p a ∨ b = .allow else FloorPermit m e p a ∧ ¬ BundleDeny m b

/-- `Envelope(p, a, r)`, stated against the truth. -/
def Envelope (st : State) (p : Seat) (a : Act) (r : Target) : Prop :=
  a = .Read ∨ (a = .Draft ∧ (st.truth r).owner = some p) ∨
  (a = .Emit ∧ (st.truth r).owner = some p ∧ (st.truth r).sealed = some false)

/-- The `CASE` on `drop` in `Decide`: the slice handed to the engine, with at most one attribute dropped. -/
def Dropped (e0 : Rec) : Drop → Rec
  | .no => e0
  | .owner => { e0 with owner := none }
  | .sealed => { e0 with sealed := none }

/-- The flags after a decision at `(p, a, r)` on slice `e`, bundle outcome `b`, whose admit is `ok`: the primed
conjuncts of `Decide`, with `ok` left free so that a code decision can supply its own (FloorRefinement.lean). -/
def decided (st : State) (m : Mut) (e : Rec) (p : Seat) (a : Act) (r : Target) (b : BOut) (ok : Prop) : State :=
  { st with
    admitNoFloor := st.admitNoFloor ∨ (ok ∧ ¬ (EngineAllow e p a ∧ ¬ EngineErr e p a))
    admitWithErr := st.admitWithErr ∨ (ok ∧ EngineErr e p a)
    admitNoBundle := st.admitNoBundle ∨ (ok ∧ b ≠ .allow)
    admitOutside := st.admitOutside ∨ (ok ∧ ¬ Envelope st p a r)
    sawAdmit := st.sawAdmit ∨ ok
    sawNarrow := st.sawNarrow ∨ (FloorPermit m e p a ∧ ¬ ok)
    sawFloorErr := st.sawFloorErr ∨ EngineErr e p a }

/-- ```
Decide(p, a, r) ==
  \E b \in BundleOutcomes, drop \in {"no", "owner", "sealed"} :
    LET e0 == fstore[r]
        e  == CASE drop = "owner" -> [e0 EXCEPT !.owner = NONE] [] drop = "sealed" -> [e0 EXCEPT !.sealed = NONE]
              [] OTHER -> e0
        ok == Admit(e, p, a, b)
    IN /\ admitNoFloor' = (admitNoFloor \/ (ok /\ ~(EngineAllow(e, p, a) /\ ~EngineErr(e, p, a))))
       /\ ... /\ UNCHANGED <<truth, fstore>>
``` -/
def Decide (m : Mut) (p : Seat) (a : Act) (r : Target) (st st' : State) : Prop :=
  ∃ (b : BOut) (d : Drop), st' = decided st m (Dropped (st.fstore r) d) p a r b
                                    (Admit m (Dropped (st.fstore r) d) p a b)

/-- `Next == \/ \E t, s : Reassign(t, s) \/ BundleWrite(t, s) \/ \E t : Seal(t) \/ \E p, a, r : Decide(p, a, r)` -/
def Next (m : Mut) (st st' : State) : Prop :=
  (∃ t s, Reassign t s st st' ∨ BundleWrite m t s st st') ∨ (∃ t, Seal t st st') ∨
  ∃ p a r, Decide m p a r st st'

/-! ## The five properties -/

def AdmitImpliesFloorPermit (st : State) : Prop := ¬ st.admitNoFloor
def FloorErrorIsDeny (st : State) : Prop := ¬ st.admitWithErr
def BundleRefusalHonored (st : State) : Prop := ¬ st.admitNoBundle
def BundleCannotWriteFloorInputs (st : State) : Prop := st.fstore = st.truth
def EnvelopeHolds (st : State) : Prop := ¬ st.admitOutside

def Safe (st : State) : Prop :=
  AdmitImpliesFloorPermit st ∧ FloorErrorIsDeny st ∧ BundleRefusalHonored st ∧ BundleCannotWriteFloorInputs st ∧
  EnvelopeHolds st

/-! ## What an admit implies -/

/-- `AdmitIsFloorPermit`: under the specified `Admit`, an admit is a floor permit without engine error. -/
theorem AdmitIsFloorPermit (m : Mut) (h1 : m ≠ .M_ERR) (h2 : m ≠ .M_OVERRIDE) (e : Rec) (p : Seat) (a : Act)
    (b : BOut) (h : Admit m e p a b) : EngineAllow e p a ∧ ¬ EngineErr e p a := by
  unfold Admit FloorPermit at h
  rw [if_neg h2, if_neg h1] at h
  exact h.1

/-- `AdmitIsBundleAllow`: under the specified `Admit`, an admit had an affirmative bundle allow. -/
theorem AdmitIsBundleAllow (m : Mut) (h1 : m ≠ .M_FAILOPEN) (h2 : m ≠ .M_OVERRIDE) (e : Rec) (p : Seat) (a : Act)
    (b : BOut) (h : Admit m e p a b) : b = .allow := by
  unfold Admit BundleDeny at h
  rw [if_neg h2, if_neg h1] at h
  exact Decidable.of_not_not h.2

/-- `PermitWithinEnvelope`: a floor permit without error, on the truth with at most one attribute dropped, lies within
the envelope: a dropped attribute the act needs is an error, so the permit was decided on the true owner and seal. -/
theorem PermitWithinEnvelope (st : State) (hI : st.fstore = st.truth) (p : Seat) (a : Act) (r : Target) (d : Drop)
    (hA : EngineAllow (Dropped (st.fstore r) d) p a) (hE : ¬ EngineErr (Dropped (st.fstore r) d) p a) :
    Envelope st p a r := by
  rw [hI] at hA hE
  unfold Envelope
  cases hr : st.truth r with
  | mk o sl =>
    rw [hr] at hA hE
    rcases a with _ | _ | _ <;> rcases d with _ | _ | _ <;> rcases o with _ | (_ | _) <;>
      rcases sl with _ | (_ | _) <;> rcases p with _ | _ <;>
      simp_all [EngineAllow, EngineErr, Permits, Forbids, OwnerIs, SealedIs, Dropped]

/-! ## The flag invariants, by induction on reachable states -/

theorem InitSafe (st : State) (h : Init st) : Safe st := by
  obtain ⟨ht, hf, h1, h2, h3, h4, -⟩ := h
  exact ⟨h1, h2, h3, by unfold BundleCannotWriteFloorInputs; rw [ht, hf], h4⟩

/-- Every step but `Decide` leaves the flags alone. -/
theorem flags_of_lift (m : Mut) (st st' : State)
    (h : (∃ t s, Reassign t s st st' ∨ BundleWrite m t s st st') ∨ (∃ t, Seal t st st')) :
    st'.admitNoFloor = st.admitNoFloor ∧ st'.admitWithErr = st.admitWithErr ∧
    st'.admitNoBundle = st.admitNoBundle ∧ st'.admitOutside = st.admitOutside := by
  rcases h with ⟨t, s, h | ⟨-, h⟩⟩ | ⟨t, -, h⟩ <;> subst h <;> exact ⟨rfl, rfl, rfl, rfl⟩

def InvF (st : State) : Prop := AdmitImpliesFloorPermit st ∧ FloorErrorIsDeny st

theorem NextFloorFlags (m : Mut) (h1 : m ≠ .M_ERR) (h2 : m ≠ .M_OVERRIDE) (st st' : State) (hi : InvF st)
    (hn : Next m st st') : InvF st' := by
  obtain ⟨hF, hE⟩ := hi
  rcases hn with h | h | ⟨p, a, r, b, d, rfl⟩
  · obtain ⟨e1, e2, -, -⟩ := flags_of_lift m st st' (Or.inl h)
    exact ⟨by unfold AdmitImpliesFloorPermit; rw [e1]; exact hF, by unfold FloorErrorIsDeny; rw [e2]; exact hE⟩
  · obtain ⟨e1, e2, -, -⟩ := flags_of_lift m st st' (Or.inr h)
    exact ⟨by unfold AdmitImpliesFloorPermit; rw [e1]; exact hF, by unfold FloorErrorIsDeny; rw [e2]; exact hE⟩
  · have hp := AdmitIsFloorPermit m h1 h2 (Dropped (st.fstore r) d) p a b
    refine ⟨?_, ?_⟩
    · rintro (h | ⟨hok, hn⟩)
      · exact hF h
      · exact hn (hp hok)
    · rintro (h | ⟨hok, he⟩)
      · exact hE h
      · exact (hp hok).2 he

/-- `THEOREM AdmitImpliesFloorPermitAlways == ASSUME Mut \notin {"M_ERR", "M_OVERRIDE"} PROVE Spec => []AdmitImpliesFloorPermit` -/
theorem AdmitImpliesFloorPermitAlways (m : Mut) (h1 : m ≠ .M_ERR) (h2 : m ≠ .M_OVERRIDE) :
    ∀ st, Reachable Init (Next m) st → AdmitImpliesFloorPermit st :=
  invariant InvF AdmitImpliesFloorPermit (fun st h => ⟨(InitSafe st h).1, (InitSafe st h).2.1⟩)
    (NextFloorFlags m h1 h2) (fun _ h => h.1)

/-- `THEOREM FloorErrorIsDenyAlways == ASSUME Mut \notin {"M_ERR", "M_OVERRIDE"} PROVE Spec => []FloorErrorIsDeny` -/
theorem FloorErrorIsDenyAlways (m : Mut) (h1 : m ≠ .M_ERR) (h2 : m ≠ .M_OVERRIDE) :
    ∀ st, Reachable Init (Next m) st → FloorErrorIsDeny st :=
  invariant InvF FloorErrorIsDeny (fun st h => ⟨(InitSafe st h).1, (InitSafe st h).2.1⟩)
    (NextFloorFlags m h1 h2) (fun _ h => h.2)

theorem NextBundleFlag (m : Mut) (h1 : m ≠ .M_FAILOPEN) (h2 : m ≠ .M_OVERRIDE) (st st' : State)
    (hi : BundleRefusalHonored st) (hn : Next m st st') : BundleRefusalHonored st' := by
  rcases hn with h | h | ⟨p, a, r, b, d, rfl⟩
  · obtain ⟨-, -, e3, -⟩ := flags_of_lift m st st' (Or.inl h)
    unfold BundleRefusalHonored; rw [e3]; exact hi
  · obtain ⟨-, -, e3, -⟩ := flags_of_lift m st st' (Or.inr h)
    unfold BundleRefusalHonored; rw [e3]; exact hi
  · rintro (h | ⟨hok, hb⟩)
    · exact hi h
    · exact hb (AdmitIsBundleAllow m h1 h2 _ p a b hok)

/-- `THEOREM BundleRefusalHonoredAlways == ASSUME Mut \notin {"M_FAILOPEN", "M_OVERRIDE"} PROVE Spec => []BundleRefusalHonored` -/
theorem BundleRefusalHonoredAlways (m : Mut) (h1 : m ≠ .M_FAILOPEN) (h2 : m ≠ .M_OVERRIDE) :
    ∀ st, Reachable Init (Next m) st → BundleRefusalHonored st :=
  invariant BundleRefusalHonored BundleRefusalHonored (fun st h => (InitSafe st h).2.2.1)
    (NextBundleFlag m h1 h2) (fun _ h => h)

/-! ## The floor's inputs are the truth -/

theorem NextInputs (m : Mut) (hm : m ≠ .M_WRITE) (st st' : State) (hi : BundleCannotWriteFloorInputs st)
    (hn : Next m st st') : BundleCannotWriteFloorInputs st' := by
  unfold BundleCannotWriteFloorInputs at *
  rcases hn with ⟨t, s, h | ⟨hw, -⟩⟩ | ⟨t, -, h⟩ | ⟨p, a, r, b, d, rfl⟩
  · subst h; simp only; rw [hi]
  · exact absurd hw hm
  · subst h; simp only; rw [hi]
  · exact hi

/-- `THEOREM BundleCannotWriteFloorInputsAlways == ASSUME Mut # "M_WRITE" PROVE Spec => []BundleCannotWriteFloorInputs` -/
theorem BundleCannotWriteFloorInputsAlways (m : Mut) (hm : m ≠ .M_WRITE) :
    ∀ st, Reachable Init (Next m) st → BundleCannotWriteFloorInputs st :=
  invariant BundleCannotWriteFloorInputs BundleCannotWriteFloorInputs (fun st h => (InitSafe st h).2.2.2.1)
    (NextInputs m hm) (fun _ h => h)

/-! ## EnvelopeHolds, with the inputs invariant -/

def InvE (st : State) : Prop := BundleCannotWriteFloorInputs st ∧ EnvelopeHolds st

theorem NextInvE (m : Mut) (h1 : m ≠ .M_WRITE) (h2 : m ≠ .M_ERR) (h3 : m ≠ .M_OVERRIDE) (st st' : State)
    (hi : InvE st) (hn : Next m st st') : InvE st' := by
  obtain ⟨hI, hEnv⟩ := hi
  refine ⟨NextInputs m h1 st st' hI hn, ?_⟩
  rcases hn with h | h | ⟨p, a, r, b, d, rfl⟩
  · obtain ⟨-, -, -, e4⟩ := flags_of_lift m st st' (Or.inl h)
    unfold EnvelopeHolds; rw [e4]; exact hEnv
  · obtain ⟨-, -, -, e4⟩ := flags_of_lift m st st' (Or.inr h)
    unfold EnvelopeHolds; rw [e4]; exact hEnv
  · rintro (h | ⟨hok, hout⟩)
    · exact hEnv h
    · obtain ⟨hA, hE⟩ := AdmitIsFloorPermit m h2 h3 _ p a b hok
      exact hout (PermitWithinEnvelope st hI p a r d hA hE)

/-- `THEOREM EnvelopeHoldsAlways == ASSUME Mut \notin {"M_WRITE", "M_ERR", "M_OVERRIDE"} PROVE Spec => []EnvelopeHolds` -/
theorem EnvelopeHoldsAlways (m : Mut) (h1 : m ≠ .M_WRITE) (h2 : m ≠ .M_ERR) (h3 : m ≠ .M_OVERRIDE) :
    ∀ st, Reachable Init (Next m) st → EnvelopeHolds st :=
  invariant InvE EnvelopeHolds (fun st h => ⟨(InitSafe st h).2.2.2.1, (InitSafe st h).2.2.2.2⟩)
    (NextInvE m h1 h2 h3) (fun _ h => h.2)

/-- `THEOREM SafeAlways == ASSUME Mut = "none" PROVE Spec => []Safe` -/
theorem SafeAlways : ∀ st, Reachable Init (Next .none) st → Safe st :=
  fun st h => ⟨AdmitImpliesFloorPermitAlways .none (by simp) (by simp) st h,
    FloorErrorIsDenyAlways .none (by simp) (by simp) st h,
    BundleRefusalHonoredAlways .none (by simp) (by simp) st h,
    BundleCannotWriteFloorInputsAlways .none (by simp) st h,
    EnvelopeHoldsAlways .none (by simp) (by simp) (by simp) st h⟩

/-! ## Why the mutations must fail (the counterexamples are TLC's) -/

/-- `MutOverrideAdmitsOnAllow`: a bundle allow admits whatever the floor said. -/
theorem MutOverrideAdmitsOnAllow (e : Rec) (p : Seat) (a : Act) : Admit .M_OVERRIDE e p a .allow := by
  unfold Admit; rw [if_pos rfl]; exact Or.inr rfl

/-- `MutErrPermitsWithError`: an engine error does not deny; a permit with error passes the floor. -/
theorem MutErrPermitsWithError (e : Rec) (p : Seat) (a : Act) (h : EngineAllow e p a) : FloorPermit .M_ERR e p a := by
  unfold FloorPermit; rw [if_pos rfl]; exact h

/-- `MutFailOpenPassesErrors`: only an explicit deny denies. -/
theorem MutFailOpenPassesErrors (b : BOut) (_h1 : b ≠ .allow) (h2 : b ≠ .deny) : ¬ BundleDeny .M_FAILOPEN b := by
  unfold BundleDeny; rw [if_pos rfl]; exact h2

/-- `MutWriteDivergesInputs`: the bundle can move the floor's copy of an owner off the truth. -/
theorem MutWriteDivergesInputs (st st' : State) (t : Target) (s : Seat)
    (hs : (st.truth t).owner ≠ some s) (h : BundleWrite .M_WRITE t s st st') : st'.fstore ≠ st'.truth := by
  obtain ⟨-, rfl⟩ := h
  intro heq
  have := congrFun heq t
  simp only [upd_same] at this
  exact hs (by rw [← this])

#print axioms AdmitImpliesFloorPermitAlways
#print axioms FloorErrorIsDenyAlways
#print axioms BundleRefusalHonoredAlways
#print axioms BundleCannotWriteFloorInputsAlways
#print axioms EnvelopeHoldsAlways
#print axioms SafeAlways

end Topak.Spec.FloorComposition
