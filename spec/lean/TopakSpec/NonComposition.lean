import TopakSpec.Prelude
/-!
# NonComposition.tla in Lean

ADR-0013 §4, NC-1 and NC-2: erasure composed with break-glass against the forensic floor.
`spec/NonComposition.tla` re-encoded; `spec/NonComposition_proof.tla`'s theorems proved by induction on
reachable states with its inductive invariant (`NC2 ∧ BGCreated ∧ ViaBGAdmitted ∧ AdmitCreated`).
`bgActive` is a `Bool`, so the two `IF bgActive` are `if`; `IF EraseRecord ∈ created` is a membership
test, so it is the pair of implications the prelude describes. The record field `eff` ranges over the
effects and "bg", which is `Eff`.

Mutations: `M1`, F1 admit decisions are erasable; `M2`, a break-glass grant widens the erasure envelope to
everything. Each theorem takes both as hypotheses, as the TLAPS module does.

This is the one module whose proof is classical (`Classical.choice` in `#print axioms`): the `Erase` step
cases on whether `EraseRecord ∈ created`, a membership TLA+ decides by excluded middle, and so does the
proof. The other six modules use only `propext` and `Quot.sound`.
-/

namespace Topak.Spec.NonComposition
open Topak.Spec PSet

inductive Mut | none | M1 | M2
  deriving DecidableEq

/-- `Effects == {"e1", "e2"}` -/
inductive Effect | e1 | e2
  deriving DecidableEq
/-- The `kind` field: `ForensicKinds ∪ {"payload"}` -/
inductive RKind | F1 | F5 | F6 | payload
  deriving DecidableEq
/-- The `eff` field: an effect, or "bg". -/
inductive Eff | of (e : Effect) | bg
  deriving DecidableEq

structure Rec where
  kind : RKind
  eff : Eff
  deriving DecidableEq

/-- `ForensicKinds == {"F1", "F5", "F6"}` -/
def ForensicKinds : PSet RKind := {.F1, .F5, .F6}

/-- `AdmitRec(e) == [kind |-> "F1", eff |-> e]` -/
def AdmitRec (e : Effect) : Rec := ⟨.F1, .of e⟩
/-- `PayRec(e) == [kind |-> "payload", eff |-> e]` -/
def PayRec (e : Effect) : Rec := ⟨.payload, .of e⟩
/-- `BGRecord == [kind |-> "F5", eff |-> "bg"]` -/
def BGRecord : Rec := ⟨.F5, .bg⟩
/-- `EraseRecord == [kind |-> "F6", eff |-> "bg"]` -/
def EraseRecord : Rec := ⟨.F6, .bg⟩

/-- `VARIABLES admitted, viaBG, bgActive, created, retained` -/
structure State where
  admitted : PSet Effect
  viaBG : PSet Effect
  bgActive : Bool
  created : PSet Rec
  retained : PSet Rec

def Init (st : State) : Prop :=
  st.admitted = ∅ ∧ st.viaBG = ∅ ∧ st.bgActive = false ∧ st.created = ∅ ∧ st.retained = ∅

/-- ```
Erasable(r) ==
  CASE Mut = "M1" -> r.kind ∉ (ForensicKinds \ {"F1"})
    [] Mut = "M2" -> IF bgActive THEN TRUE ELSE r.kind ∉ ForensicKinds
    [] OTHER      -> r.kind ∉ ForensicKinds
``` -/
def Erasable (m : Mut) (st : State) (r : Rec) : Prop :=
  match m with
  | .M1 => r.kind ∉ (ForensicKinds \ {.F1})
  | .M2 => if st.bgActive then True else r.kind ∉ ForensicKinds
  | .none => r.kind ∉ ForensicKinds

/-- ```
InvokeBG == /\ ~bgActive
            /\ bgActive' = TRUE
            /\ created'  = created ∪ {BGRecord}
            /\ retained' = retained ∪ {BGRecord}
            /\ UNCHANGED <<admitted, viaBG>>
``` -/
def InvokeBG (st st' : State) : Prop :=
  st.bgActive = false ∧ st'.bgActive = true ∧
  st'.created = st.created ∪ {BGRecord} ∧
  st'.retained = st.retained ∪ {BGRecord} ∧
  st'.admitted = st.admitted ∧ st'.viaBG = st.viaBG

/-- ```
Admit(e) == /\ e ∉ admitted
            /\ admitted' = admitted ∪ {e}
            /\ viaBG'    = IF bgActive THEN viaBG ∪ {e} ELSE viaBG
            /\ created'  = created  ∪ {AdmitRec(e), PayRec(e)}
            /\ retained' = retained ∪ {AdmitRec(e), PayRec(e)}
            /\ UNCHANGED bgActive
``` -/
def Admit (e : Effect) (st st' : State) : Prop :=
  e ∉ st.admitted ∧
  st'.admitted = st.admitted ∪ {e} ∧
  st'.viaBG = (if st.bgActive then st.viaBG ∪ {e} else st.viaBG) ∧
  st'.created = st.created ∪ {AdmitRec e, PayRec e} ∧
  st'.retained = st.retained ∪ {AdmitRec e, PayRec e} ∧
  st'.bgActive = st.bgActive

/-- ```
Erase == /\ ∃ S ∈ SUBSET retained :
              /\ S # {}
              /\ ∀ r ∈ S : Erasable(r)
              /\ created'  = created ∪ {EraseRecord}
              /\ retained' = IF EraseRecord ∈ created
                             THEN retained \ S
                             ELSE (retained \ S) ∪ {EraseRecord}
         /\ UNCHANGED <<admitted, viaBG, bgActive>>
``` -/
def Erase (m : Mut) (st st' : State) : Prop :=
  (∃ S : PSet Rec, S ⊆ st.retained ∧ NonEmpty S ∧
    (∀ r, r ∈ S → Erasable m st r) ∧
    st'.created = st.created ∪ {EraseRecord} ∧
    (EraseRecord ∈ st.created → st'.retained = st.retained \ S) ∧
    (EraseRecord ∉ st.created → st'.retained = (st.retained \ S) ∪ {EraseRecord})) ∧
  st'.admitted = st.admitted ∧ st'.viaBG = st.viaBG ∧ st'.bgActive = st.bgActive

/-- `Next == InvokeBG \/ Erase \/ ∃ e ∈ Effects : Admit(e)` -/
def Next (m : Mut) (st st' : State) : Prop :=
  InvokeBG st st' ∨ Erase m st st' ∨ ∃ e, Admit e st st'

/-! ## The two properties -/

/-- `Attributable(e) == AdmitRec(e) ∈ retained /\ (e ∈ viaBG => BGRecord ∈ retained)` -/
def Attributable (st : State) (e : Effect) : Prop :=
  AdmitRec e ∈ st.retained ∧ (e ∈ st.viaBG → BGRecord ∈ st.retained)

/-- NC-1. `∀ e ∈ admitted : (PayRec(e) ∉ retained) => Attributable(e)` -/
def NC1 (st : State) : Prop := ∀ e, e ∈ st.admitted → PayRec e ∉ st.retained → Attributable st e

/-- NC-2. `∀ r ∈ created : r.kind ∈ ForensicKinds => r ∈ retained` -/
def NC2 (st : State) : Prop := ∀ r, r ∈ st.created → r.kind ∈ ForensicKinds → r ∈ st.retained

def Safe (st : State) : Prop := NC1 st ∧ NC2 st

/-! ## Proofs -/

/-- `BGCreated == bgActive => BGRecord ∈ created` -/
def BGCreated (st : State) : Prop := st.bgActive = true → BGRecord ∈ st.created
/-- `ViaBGAdmitted == viaBG ⊆ admitted` -/
def ViaBGAdmitted (st : State) : Prop := st.viaBG ⊆ st.admitted
/-- `AdmitCreated == ∀ e ∈ admitted : AdmitRec(e) ∈ created /\ (e ∈ viaBG => BGRecord ∈ created)` -/
def AdmitCreated (st : State) : Prop :=
  ∀ e, e ∈ st.admitted → AdmitRec e ∈ st.created ∧ (e ∈ st.viaBG → BGRecord ∈ st.created)

def Inv (st : State) : Prop := NC2 st ∧ BGCreated st ∧ ViaBGAdmitted st ∧ AdmitCreated st

/-- `ForensicKept`: under the specified rule, a forensic record is not erasable. -/
theorem ForensicKept (m : Mut) (h1 : m ≠ .M1) (h2 : m ≠ .M2) (st : State) (r : Rec)
    (hk : r.kind ∈ ForensicKinds) : ¬ Erasable m st r := by
  cases m
  · exact fun hn => hn hk
  · exact absurd rfl h1
  · exact absurd rfl h2

theorem InitInv (st : State) (h : Init st) : Inv st := by
  obtain ⟨ha, hv, hb, hc, -⟩ := h
  refine ⟨?_, ?_, ?_, ?_⟩
  · intro r hr; simp [hc] at hr
  · intro hbA; rw [hb] at hbA; cases hbA
  · intro e he; simp [hv] at he
  · intro e he; simp [ha] at he

theorem F1_forensic : (AdmitRec e).kind ∈ ForensicKinds := by simp [AdmitRec, ForensicKinds]
theorem F5_forensic : BGRecord.kind ∈ ForensicKinds := by simp [BGRecord, ForensicKinds]
theorem F6_forensic : EraseRecord.kind ∈ ForensicKinds := by simp [EraseRecord, ForensicKinds]

theorem NextInv (m : Mut) (h1 : m ≠ .M1) (h2 : m ≠ .M2) (st st' : State) (hi : Inv st) (hn : Next m st st') :
    Inv st' := by
  obtain ⟨hNC2, hBG, hVia, hAC⟩ := hi
  rcases hn with ⟨-, -, hc, hr, ha, hv⟩ | ⟨⟨S, -, -, hEr, hc, hr1, hr2⟩, ha, hv, hb⟩ | ⟨e, hne, ha, hv, hc, hr, hb⟩
  · -- InvokeBG: one record created and retained
    refine ⟨?_, ?_, ?_, ?_⟩
    · intro r hr' hk
      rw [hc] at hr'; rw [hr]
      rcases hr' with hr' | hr'
      · exact Or.inl (hNC2 r hr' hk)
      · exact Or.inr hr'
    · intro _; rw [hc]; exact Or.inr rfl
    · unfold ViaBGAdmitted; rw [hv, ha]; exact hVia
    · intro e he
      rw [ha] at he; rw [hv, hc]
      obtain ⟨x, y⟩ := hAC e he
      exact ⟨Or.inl x, fun hv' => Or.inl (y hv')⟩
  · -- Erase: nothing forensic is in S, so NC2 survives; the erasure record is itself retained
    have hkeep : ∀ r, r.kind ∈ ForensicKinds → ¬ r ∈ S :=
      fun r hk hS' => ForensicKept m h1 h2 st r hk (hEr r hS')
    have hret : ∀ r, r ∈ st.retained → ¬ r ∈ S → r ∈ st'.retained := by
      intro r hr hnS
      by_cases hE : EraseRecord ∈ st.created
      · rw [hr1 hE]; exact ⟨hr, hnS⟩
      · rw [hr2 hE]; exact Or.inl ⟨hr, hnS⟩
    have hE' : EraseRecord ∈ st'.retained := by
      by_cases hE : EraseRecord ∈ st.created
      · exact hret _ (hNC2 _ hE F6_forensic) (hkeep _ F6_forensic)
      · rw [hr2 hE]; exact Or.inr rfl
    refine ⟨?_, ?_, ?_, ?_⟩
    · intro r hr' hk
      rw [hc] at hr'
      rcases hr' with hr' | hr'
      · exact hret r (hNC2 r hr' hk) (hkeep r hk)
      · have hr' : r = EraseRecord := hr'
        subst hr'; exact hE'
    · intro hbA; rw [hb] at hbA; rw [hc]; exact Or.inl (hBG hbA)
    · unfold ViaBGAdmitted; rw [hv, ha]; exact hVia
    · intro e he
      rw [ha] at he; rw [hv, hc]
      obtain ⟨x, y⟩ := hAC e he
      exact ⟨Or.inl x, fun hv' => Or.inl (y hv')⟩
  · -- Admit(e): its admit record is created and retained; under break-glass the invocation was recorded
    refine ⟨?_, ?_, ?_, ?_⟩
    · intro r hr' hk
      rw [hc] at hr'; rw [hr]
      rcases hr' with hr' | hr'
      · exact Or.inl (hNC2 r hr' hk)
      · exact Or.inr hr'
    · intro hbA; rw [hb] at hbA; rw [hc]; exact Or.inl (hBG hbA)
    · intro x hx
      rw [ha]; rw [hv] at hx
      by_cases hbt : st.bgActive = true
      · rw [if_pos hbt] at hx
        rcases hx with hx | hx
        · exact Or.inl (hVia x hx)
        · exact Or.inr hx
      · rw [if_neg hbt] at hx
        exact Or.inl (hVia x hx)
    · intro x hx
      rw [ha] at hx; rw [hv, hc]
      rcases hx with hx | hx
      · obtain ⟨y, z⟩ := hAC x hx
        refine ⟨Or.inl y, fun hvx => ?_⟩
        by_cases hbt : st.bgActive = true
        · rw [if_pos hbt] at hvx
          rcases hvx with hvx | hvx
          · exact Or.inl (z hvx)
          · exact Or.inl (hBG hbt)
        · rw [if_neg hbt] at hvx
          exact Or.inl (z hvx)
      · have hx : x = e := hx
        subst hx
        refine ⟨Or.inr (Or.inl rfl), fun hvx => ?_⟩
        by_cases hbt : st.bgActive = true
        · exact Or.inl (hBG hbt)
        · rw [if_neg hbt] at hvx
          exact absurd (hVia x hvx) hne

/-- `InvSafe`: NC1 follows, since the records it needs were created and NC2 keeps them. -/
theorem InvSafe (st : State) (h : Inv st) : Safe st := by
  obtain ⟨hNC2, -, -, hAC⟩ := h
  refine ⟨?_, hNC2⟩
  intro e he _
  obtain ⟨x, y⟩ := hAC e he
  exact ⟨hNC2 _ x F1_forensic, fun hv => hNC2 _ (y hv) F5_forensic⟩

/-- `THEOREM SafeAlways == ASSUME Mut # "M1", Mut # "M2" PROVE Spec => []Safe` -/
theorem SafeAlways (m : Mut) (h1 : m ≠ .M1) (h2 : m ≠ .M2) :
    ∀ st, Reachable Init (Next m) st → Safe st :=
  invariant Inv Safe InitInv (NextInv m h1 h2) InvSafe

theorem NC1Always (m : Mut) (h1 : m ≠ .M1) (h2 : m ≠ .M2) :
    ∀ st, Reachable Init (Next m) st → NC1 st :=
  fun st h => (SafeAlways m h1 h2 st h).1

theorem NC2Always (m : Mut) (h1 : m ≠ .M1) (h2 : m ≠ .M2) :
    ∀ st, Reachable Init (Next m) st → NC2 st :=
  fun st h => (SafeAlways m h1 h2 st h).2

/-! ## Why the mutations must fail (the counterexamples are TLC's) -/

/-- `MutM1ErasesAdmitRecord`: under M1 the admit decision is erasable. -/
theorem MutM1ErasesAdmitRecord (st : State) (e : Effect) : Erasable .M1 st (AdmitRec e) :=
  fun ⟨_, h⟩ => h rfl

/-- `MutM2ErasesAllUnderBreakGlass`: under M2 with break-glass active, everything is erasable. -/
theorem MutM2ErasesAllUnderBreakGlass (st : State) (hb : st.bgActive = true) (r : Rec) : Erasable .M2 st r := by
  simp [Erasable, hb]

#print axioms SafeAlways
#print axioms NC1Always
#print axioms NC2Always

end Topak.Spec.NonComposition
