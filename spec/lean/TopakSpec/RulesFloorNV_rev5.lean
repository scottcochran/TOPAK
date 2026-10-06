import TopakSpec.Prelude
/-!
# RulesFloorNV_rev5.tla in Lean

ADR-0026's rules floor after the 2026.09.23 revisions, non-vacuity by property. `spec/RulesFloorNV_rev5.tla`
re-encoded; `spec/RulesFloorNV_rev5_proof.tla`'s theorems proved by induction on reachable states, each under
the floor entry or mechanism setting it rests on. This is one of the three modules the certified TLAPS run
does not certify (`proof-certification.md`: Isabelle refuses one of Zenon's five scripts); here every step is
kernel-checked.

Encoding notes beyond the prelude's: sets of humans (`grant`, `approvers`, `seats`, `Recorded`, `Counted`) are
`Human → Bool`, so `Cardinality` is the computable `card`, a count over the five humans, and the
`FiniteSetTheorems` the TLAPS proof needs vanish. `S ∩ T = {}` on those sets is `∀ h, ¬(S h ∧ T h)`.
`BGActs` and `AuthActs` share one type `Act`. The module's three unnamed `ASSUME`s are theorems, as in the
TLAPS module, each with its witness. `Active ⊆ AllEntries` holds by type.
-/

namespace Topak.Spec.RulesFloorNV_rev5
open Topak.Spec PSet

inductive Mech | rev5 | norecuse
  deriving DecidableEq

/-- `Humans == {"h1", "h2", "h3", "h4", "h5"}` -/
inductive Human | h1 | h2 | h3 | h4 | h5
  deriving DecidableEq
def Humans : List Human := [.h1, .h2, .h3, .h4, .h5]
def Author : Human := .h1
/-- `AnchorKeys == {"h4"}` -/
def AnchorKeys : Human → Bool := fun h => h == .h4

/-- `AuthActs ∪ BGActs` as one type. -/
inductive Act | Issue | Vote | Promote | Op
  deriving DecidableEq
/-- `AuthActs == {"Issue", "Vote", "Promote"}` -/
def AuthActs : PSet Act := {.Issue, .Vote, .Promote}
/-- `BGActs == {"Issue", "Op"}` -/
def BGActs : PSet Act := {.Issue, .Op}

inductive QMode | all | k
  deriving DecidableEq
/-- `QVals == [mode : {"all", "k"}, k : 0..4]` -/
structure QVal where
  mode : QMode
  k : Nat
  deriving DecidableEq

/-- `RuleSpace == [grant : SUBSET Humans, quorum : QVals, minGrant : 0..2, bgScope : SUBSET BGActs]` -/
structure Rules where
  grant : Human → Bool
  quorum : QVal
  minGrant : Nat
  bgScope : PSet Act

def RuleSpace (r : Rules) : Prop := r.quorum.k ≤ 4 ∧ r.minGrant ≤ 2 ∧ r.bgScope ⊆ BGActs

/-- `Cardinality` of a set of humans. -/
def card (S : Human → Bool) : Nat := Humans.countP S

inductive EntryName | R1 | R2 | R5 | R7 | R9
  deriving DecidableEq

/-- ```
Entry(e, r) ==
  CASE e = "R1" -> r.quorum.mode = "all"
    [] e = "R2" -> r.minGrant >= 2
    [] e = "R5" -> r.grant ∩ AnchorKeys = {}
    [] e = "R7" -> r.bgScope ∩ AuthActs = {}
    [] e = "R9" -> r.quorum.mode = "all" \/ r.quorum.k >= 2
``` -/
def Entry : EntryName → Rules → Prop
  | .R1, r => r.quorum.mode = .all
  | .R2, r => r.minGrant ≥ 2
  | .R5, r => ∀ h, ¬ (r.grant h = true ∧ AnchorKeys h = true)
  | .R7, r => r.bgScope ∩ AuthActs = ∅
  | .R9, r => r.quorum.mode = .all ∨ r.quorum.k ≥ 2

def Floor (Active : PSet EntryName) (r : Rules) : Prop := ∀ e, e ∈ Active → Entry e r

/-- `Genesis == [grant |-> Humans \ ({Author} ∪ AnchorKeys), quorum |-> [mode |-> "all", k |-> 0], minGrant |-> 2, bgScope |-> {"Op"}]` -/
def Genesis : Rules := ⟨fun h => !(h == Author || AnchorKeys h), ⟨.all, 0⟩, 2, {.Op}⟩

inductive VoteVal | none | grant | deny
  deriving DecidableEq

/-- `VARIABLES rules, issued, votes, promoted, approvers, seats, bgDid` -/
structure State where
  rules : Rules
  issued : Bool
  votes : Human → VoteVal
  promoted : Bool
  approvers : Human → Bool
  seats : Human → Bool
  bgDid : PSet Act

def Init (st : State) : Prop :=
  st.rules = Genesis ∧ st.issued = false ∧ (st.votes = fun _ => .none) ∧ st.promoted = false ∧
  (st.approvers = fun _ => false) ∧ (st.seats = fun _ => false) ∧ st.bgDid = ∅

/-- `Counted == IF Mech = "norecuse" THEN rules.grant ELSE rules.grant \ {Author}` -/
def Counted (m : Mech) (st : State) : Human → Bool :=
  if m = .norecuse then st.rules.grant else fun h => st.rules.grant h && !(h == Author)

/-- `Recorded == {h ∈ Counted : votes[h] = "grant"}` -/
def Recorded (m : Mech) (st : State) : Human → Bool :=
  fun h => Counted m st h && (st.votes h == .grant)

/-- ```
PromotionEnabled == /\ Cardinality(Counted) >= rules.minGrant
                    /\ IF rules.quorum.mode = "all" THEN Recorded = Counted
                       ELSE Cardinality(Recorded) >= rules.quorum.k
``` -/
def PromotionEnabled (m : Mech) (st : State) : Prop :=
  card (Counted m st) ≥ st.rules.minGrant ∧
  (if st.rules.quorum.mode = .all then Recorded m st = Counted m st
   else card (Recorded m st) ≥ st.rules.quorum.k)

/-- The promotion triple and the rest, unchanged. -/
def TripleUnch (st st' : State) : Prop :=
  st'.promoted = st.promoted ∧ st'.approvers = st.approvers ∧ st'.seats = st.seats

/-- `Issue == ~issued /\ ~promoted /\ ∃ r ∈ RuleSpace : Floor(r) /\ rules' = r /\ issued' = TRUE /\ votes' = [h ∈ Humans |-> "none"] /\ UNCHANGED <<promoted, approvers, seats, bgDid>>` -/
def Issue (Active : PSet EntryName) (st st' : State) : Prop :=
  st.issued = false ∧ st.promoted = false ∧
  (∃ r, RuleSpace r ∧ Floor Active r ∧ st'.rules = r) ∧
  st'.issued = true ∧ (st'.votes = fun _ => .none) ∧ TripleUnch st st' ∧ st'.bgDid = st.bgDid

/-- `Vote(h) == ~promoted /\ h ∈ rules.grant /\ votes[h] = "none" /\ (Mech # "norecuse" => h # Author) /\ ∃ v ∈ {"grant", "deny"} : votes' = [votes EXCEPT ![h] = v] /\ UNCHANGED <<...>>` -/
def Vote (m : Mech) (h : Human) (st st' : State) : Prop :=
  st.promoted = false ∧ st.rules.grant h = true ∧ st.votes h = .none ∧
  (m ≠ .norecuse → h ≠ Author) ∧
  (∃ v, (v = .grant ∨ v = .deny) ∧ st'.votes = upd st.votes h v) ∧
  st'.rules = st.rules ∧ st'.issued = st.issued ∧ TripleUnch st st' ∧ st'.bgDid = st.bgDid

/-- `Promote == ~promoted /\ PromotionEnabled /\ promoted' = TRUE /\ approvers' = Recorded /\ seats' = Counted /\ UNCHANGED <<rules, issued, votes, bgDid>>` -/
def Promote (m : Mech) (st st' : State) : Prop :=
  st.promoted = false ∧ PromotionEnabled m st ∧
  st'.promoted = true ∧ st'.approvers = Recorded m st ∧ st'.seats = Counted m st ∧
  st'.rules = st.rules ∧ st'.issued = st.issued ∧ st'.votes = st.votes ∧ st'.bgDid = st.bgDid

/-- `BreakGlass == ∃ x ∈ rules.bgScope : bgDid' = bgDid ∪ {x} /\ UNCHANGED <<rules, issued, votes, promoted, approvers, seats>>` -/
def BreakGlass (st st' : State) : Prop :=
  (∃ x, x ∈ st.rules.bgScope ∧ st'.bgDid = st.bgDid ∪ {x}) ∧
  st'.rules = st.rules ∧ st'.issued = st.issued ∧ st'.votes = st.votes ∧ TripleUnch st st'

def Next (m : Mech) (Active : PSet EntryName) (st st' : State) : Prop :=
  Issue Active st st' ∨ Promote m st st' ∨ BreakGlass st st' ∨ ∃ h, Vote m h st st'

/-! ## The properties, one per entry -/

def P1_Unanimity (st : State) : Prop := st.promoted = true → st.approvers = st.seats
def P2_TwoSeatsCounted (st : State) : Prop := st.promoted = true → card st.seats ≥ 2
def P3_AuthorNotCounted (st : State) : Prop := st.promoted = true → st.approvers Author = false
def P5_AnchorNotApprover (st : State) : Prop :=
  st.promoted = true → ∀ h, ¬ (st.approvers h = true ∧ AnchorKeys h = true)
def P7_BGNoAuthority (st : State) : Prop := st.bgDid ∩ AuthActs = ∅
def P9_NoSoloGrant (st : State) : Prop := st.promoted = true → card st.approvers ≥ 2

def Safe (st : State) : Prop :=
  P1_Unanimity st ∧ P2_TwoSeatsCounted st ∧ P3_AuthorNotCounted st ∧ P5_AnchorNotApprover st ∧
  P7_BGNoAuthority st ∧ P9_NoSoloGrant st

/-! ## The module's three ASSUMEs, as theorems -/

theorem genesis_R7 : Genesis.bgScope ∩ AuthActs = ∅ := by
  rw [eq_empty_iff]; intro a ha
  obtain ⟨h1, h2⟩ := (mem_inter _ _ _).mp ha
  cases a <;> simp_all [Genesis, AuthActs]

/-- `ASSUME ∀ e ∈ AllEntries : Entry(e, Genesis)` -/
theorem GenesisEntries : ∀ e, Entry e Genesis := by
  intro e; cases e
  · rfl
  · show Genesis.minGrant ≥ 2; decide
  · intro h; cases h <;> simp [Genesis, AnchorKeys, Author]
  · exact genesis_R7
  · exact Or.inl rfl

theorem GenesisRules : RuleSpace Genesis := by
  refine ⟨by decide, by decide, ?_⟩
  intro a ha; have : a = .Op := ha; subst this; exact Or.inr rfl

/-- `ASSUME ∀ e ∈ AllEntries \ {"R9"} : ∃ r ∈ RuleSpace : ~Entry(e, r) /\ ∀ f ∈ AllEntries \ {e} : Entry(f, r)`:
each entry but R9 is independently droppable. One witness per entry, as in the TLAPS proof. -/
theorem EntriesIndependent (e : EntryName) (he : e ≠ .R9) :
    ∃ r, RuleSpace r ∧ ¬ Entry e r ∧ ∀ f, f ≠ e → Entry f r := by
  cases e
  · -- R1 dropped: a threshold of 2
    refine ⟨{ Genesis with quorum := ⟨.k, 2⟩ }, ⟨by decide, by decide, GenesisRules.2.2⟩, (fun h => by cases h), ?_⟩
    intro f hf; cases f
    · exact absurd rfl hf
    · show (2:Nat) ≥ 2; decide
    · exact GenesisEntries .R5
    · exact genesis_R7
    · exact Or.inr (by decide)
  · -- R2 dropped: minGrant 1
    refine ⟨{ Genesis with minGrant := 1 }, ⟨by decide, by decide, GenesisRules.2.2⟩, (by show ¬ ((1:Nat) ≥ 2); decide), ?_⟩
    intro f hf; cases f
    · rfl
    · exact absurd rfl hf
    · exact GenesisEntries .R5
    · exact genesis_R7
    · exact Or.inl rfl
  · -- R5 dropped: the anchor key-holder on the roster
    refine ⟨{ Genesis with grant := fun h => !(h == Author) }, ⟨by decide, by decide, GenesisRules.2.2⟩, ?_, ?_⟩
    · intro h; exact h .h4 ⟨by decide, by decide⟩
    · intro f hf; cases f
      · rfl
      · show (2:Nat) ≥ 2; decide
      · exact absurd rfl hf
      · exact genesis_R7
      · exact Or.inl rfl
  · -- R7 dropped: Issue in the break-glass envelope
    refine ⟨{ Genesis with bgScope := {.Issue} }, ⟨by decide, by decide, ?_⟩, ?_, ?_⟩
    · intro a ha; have : a = .Issue := ha; subst this; exact Or.inl rfl
    · intro h
      have h' : ({Act.Issue} : PSet Act) ∩ AuthActs = ∅ := h
      rw [eq_empty_iff] at h'; exact h' .Issue ⟨rfl, Or.inl rfl⟩
    · intro f hf; cases f
      · rfl
      · show (2:Nat) ≥ 2; decide
      · exact GenesisEntries .R5
      · exact absurd rfl hf
      · exact Or.inl rfl
  · exact absurd rfl he

/-- `ASSUME ∃ r ∈ RuleSpace : ~Entry("R9", r) /\ ∀ f ∈ AllEntries \ {"R1", "R9"} : Entry(f, r)`:
R9's independence relative to a floor without R1: a threshold of 1. -/
theorem R9IndependentUnderThreshold :
    ∃ r, RuleSpace r ∧ ¬ Entry .R9 r ∧ ∀ f, f ≠ .R1 → f ≠ .R9 → Entry f r := by
  refine ⟨{ Genesis with quorum := ⟨.k, 1⟩ }, ⟨by decide, by decide, GenesisRules.2.2⟩, ?_, ?_⟩
  · intro h; rcases h with h | h
    · cases h
    · exact absurd h (by decide)
  · intro f h1 h9; cases f
    · exact absurd rfl h1
    · show (2:Nat) ≥ 2; decide
    · exact GenesisEntries .R5
    · exact genesis_R7
    · exact absurd rfl h9

/-! ## Proofs -/

/-- `Base == rules ∈ RuleSpace /\ Floor(rules)`: holds under every setting. -/
def Base (Active : PSet EntryName) (st : State) : Prop := RuleSpace st.rules ∧ Floor Active st.rules

theorem InitBase (Active : PSet EntryName) (st : State) (h : Init st) : Base Active st := by
  rw [Base, h.1]; exact ⟨GenesisRules, fun e _ => GenesisEntries e⟩

theorem NextBase (m : Mech) (Active : PSet EntryName) (st st' : State) (hb : Base Active st)
    (hn : Next m Active st st') : Base Active st' := by
  rcases hn with ⟨-, -, ⟨r, hr, hf, hr'⟩, -⟩ | ⟨-, -, -, -, -, hr, -⟩ | ⟨-, hr, -⟩ | ⟨h, -, -, -, -, -, hr, -⟩
  · rw [Base, hr']; exact ⟨hr, hf⟩
  · rw [Base, hr]; exact hb
  · rw [Base, hr]; exact hb
  · rw [Base, hr]; exact hb

/-- `Steps`: every step leaves the promotion triple alone or is `Promote`. -/
theorem Steps (m : Mech) (Active : PSet EntryName) (st st' : State) (hn : Next m Active st st') :
    TripleUnch st st' ∨ Promote m st st' := by
  rcases hn with h | h | h | ⟨_, h⟩
  · exact Or.inl h.2.2.2.2.2.1
  · exact Or.inr h
  · exact Or.inl h.2.2.2.2
  · exact Or.inl h.2.2.2.2.2.2.2.1

/-- A recorded approver is a counted seat, and a counted seat is on the roster. -/
theorem recorded_counted (m : Mech) (st : State) (h : Human) (hr : Recorded m st h = true) : Counted m st h = true := by
  unfold Recorded at hr; exact (Bool.and_eq_true _ _ |>.mp hr).1
theorem counted_grant (m : Mech) (st : State) (h : Human) (hc : Counted m st h = true) : st.rules.grant h = true := by
  unfold Counted at hc; split at hc
  · exact hc
  · exact (Bool.and_eq_true _ _ |>.mp hc).1

/-- Under the specified mechanism the author is not a counted seat. -/
theorem author_not_counted (st : State) : Counted .rev5 st Author = false := by
  simp [Counted]

/-- The per-property step. Each property is established at `Promote` from `PromotionEnabled` and the entry in
force, and frozen after it. -/
theorem NextP1 (m : Mech) (Active : PSet EntryName) (hR1 : EntryName.R1 ∈ Active) (st st' : State)
    (hb : Base Active st) (hp : P1_Unanimity st) (hn : Next m Active st st') : P1_Unanimity st' := by
  rcases Steps m Active st st' hn with ⟨h1, h2, h3⟩ | ⟨-, ⟨-, hq⟩, h1, h2, h3, -⟩
  · intro h; rw [h2, h3]; exact hp (h1 ▸ h)
  · intro _; rw [h2, h3]
    have hall : st.rules.quorum.mode = .all := hb.2 .R1 hR1
    rw [if_pos hall] at hq; exact hq

theorem NextP2 (m : Mech) (Active : PSet EntryName) (hR2 : EntryName.R2 ∈ Active) (st st' : State)
    (hb : Base Active st) (hp : P2_TwoSeatsCounted st) (hn : Next m Active st st') : P2_TwoSeatsCounted st' := by
  rcases Steps m Active st st' hn with ⟨h1, h2, h3⟩ | ⟨-, ⟨hc, -⟩, h1, h2, h3, -⟩
  · intro h; rw [h3]; exact hp (h1 ▸ h)
  · intro _; rw [h3]
    have hmin : st.rules.minGrant ≥ 2 := hb.2 .R2 hR2
    omega

theorem NextP3 (Active : PSet EntryName) (st st' : State) (hp : P3_AuthorNotCounted st)
    (hn : Next .rev5 Active st st') : P3_AuthorNotCounted st' := by
  rcases Steps .rev5 Active st st' hn with ⟨h1, h2, h3⟩ | ⟨-, -, h1, h2, h3, -⟩
  · intro h; rw [h2]; exact hp (h1 ▸ h)
  · intro _; rw [h2]
    unfold Recorded; rw [author_not_counted]; rfl

theorem NextP5 (m : Mech) (Active : PSet EntryName) (hR5 : EntryName.R5 ∈ Active) (st st' : State)
    (hb : Base Active st) (hp : P5_AnchorNotApprover st) (hn : Next m Active st st') : P5_AnchorNotApprover st' := by
  rcases Steps m Active st st' hn with ⟨h1, h2, h3⟩ | ⟨-, -, h1, h2, h3, -⟩
  · intro h; rw [h2]; exact hp (h1 ▸ h)
  · intro _ h ⟨ha, hk⟩
    rw [h2] at ha
    have : st.rules.grant h = true := counted_grant m st h (recorded_counted m st h ha)
    exact hb.2 .R5 hR5 h ⟨this, hk⟩

theorem NextP9 (m : Mech) (Active : PSet EntryName) (hR2 : EntryName.R2 ∈ Active)
    (hR19 : EntryName.R1 ∈ Active ∨ EntryName.R9 ∈ Active) (st st' : State)
    (hb : Base Active st) (hp : P9_NoSoloGrant st) (hn : Next m Active st st') : P9_NoSoloGrant st' := by
  rcases Steps m Active st st' hn with ⟨h1, h2, h3⟩ | ⟨-, ⟨hc, hq⟩, h1, h2, h3, -⟩
  · intro h; rw [h2]; exact hp (h1 ▸ h)
  · intro _; rw [h2]
    have hmin : st.rules.minGrant ≥ 2 := hb.2 .R2 hR2
    by_cases hall : st.rules.quorum.mode = .all
    · rw [if_pos hall] at hq; rw [hq]; omega
    · rw [if_neg hall] at hq
      have hk : st.rules.quorum.k ≥ 2 := by
        rcases hR19 with h1 | h9
        · exact absurd (hb.2 .R1 h1) hall
        · rcases hb.2 .R9 h9 with h | h
          · exact absurd h hall
          · exact h
      omega

theorem NextP7 (m : Mech) (Active : PSet EntryName) (hR7 : EntryName.R7 ∈ Active) (st st' : State)
    (hb : Base Active st) (hp : P7_BGNoAuthority st) (hn : Next m Active st st') : P7_BGNoAuthority st' := by
  rcases hn with ⟨-, -, -, -, -, -, hd⟩ | ⟨-, -, -, -, -, -, -, -, hd⟩ | ⟨⟨x, hx, hd⟩, -⟩ | ⟨_, -, -, -, -, -, -, -, -, hd⟩
  · unfold P7_BGNoAuthority; rw [hd]; exact hp
  · unfold P7_BGNoAuthority; rw [hd]; exact hp
  · unfold P7_BGNoAuthority; rw [hd, eq_empty_iff]
    rintro a ⟨ha | ha, hauth⟩
    · have : a ∈ st.bgDid ∩ AuthActs := ⟨ha, hauth⟩
      rw [hp] at this; exact this
    · have ha : a = x := ha; subst ha
      have hR7e : st.rules.bgScope ∩ AuthActs = ∅ := hb.2 .R7 hR7
      have : a ∈ st.rules.bgScope ∩ AuthActs := ⟨hx, hauth⟩
      rw [hR7e] at this; exact this
  · unfold P7_BGNoAuthority; rw [hd]; exact hp

theorem InitSafe (st : State) (h : Init st) : Safe st := by
  obtain ⟨-, -, -, hp, -, -, hd⟩ := h
  refine ⟨?_, ?_, ?_, ?_, ?_, ?_⟩ <;> try (intro h'; rw [hp] at h'; cases h')
  unfold P7_BGNoAuthority; rw [hd, eq_empty_iff]; rintro a ⟨ha, -⟩; exact ha

/-- `THEOREM P1Always == Spec => []P1_Unanimity` under `"R1" ∈ Active`. -/
theorem P1Always (m : Mech) (Active : PSet EntryName) (hR1 : EntryName.R1 ∈ Active) :
    ∀ st, Reachable Init (Next m Active) st → P1_Unanimity st :=
  invariant (fun st => Base Active st ∧ P1_Unanimity st) P1_Unanimity
    (fun st h => ⟨InitBase Active st h, (InitSafe st h).1⟩)
    (fun st st' ⟨hb, hp⟩ hn => ⟨NextBase m Active st st' hb hn, NextP1 m Active hR1 st st' hb hp hn⟩)
    (fun _ h => h.2)

/-- `THEOREM P2Always == Spec => []P2_TwoSeatsCounted` under `"R2" ∈ Active`. -/
theorem P2Always (m : Mech) (Active : PSet EntryName) (hR2 : EntryName.R2 ∈ Active) :
    ∀ st, Reachable Init (Next m Active) st → P2_TwoSeatsCounted st :=
  invariant (fun st => Base Active st ∧ P2_TwoSeatsCounted st) P2_TwoSeatsCounted
    (fun st h => ⟨InitBase Active st h, (InitSafe st h).2.1⟩)
    (fun st st' ⟨hb, hp⟩ hn => ⟨NextBase m Active st st' hb hn, NextP2 m Active hR2 st st' hb hp hn⟩)
    (fun _ h => h.2)

/-- `THEOREM P3Always == Spec => []P3_AuthorNotCounted` under `Mech # "norecuse"`. -/
theorem P3Always (Active : PSet EntryName) :
    ∀ st, Reachable Init (Next .rev5 Active) st → P3_AuthorNotCounted st :=
  invariant P3_AuthorNotCounted P3_AuthorNotCounted (fun st h => (InitSafe st h).2.2.1)
    (NextP3 Active) (fun _ h => h)

/-- `THEOREM P5Always == Spec => []P5_AnchorNotApprover` under `"R5" ∈ Active`. -/
theorem P5Always (m : Mech) (Active : PSet EntryName) (hR5 : EntryName.R5 ∈ Active) :
    ∀ st, Reachable Init (Next m Active) st → P5_AnchorNotApprover st :=
  invariant (fun st => Base Active st ∧ P5_AnchorNotApprover st) P5_AnchorNotApprover
    (fun st h => ⟨InitBase Active st h, (InitSafe st h).2.2.2.1⟩)
    (fun st st' ⟨hb, hp⟩ hn => ⟨NextBase m Active st st' hb hn, NextP5 m Active hR5 st st' hb hp hn⟩)
    (fun _ h => h.2)

/-- `THEOREM P7Always == Spec => []P7_BGNoAuthority` under `"R7" ∈ Active`. -/
theorem P7Always (m : Mech) (Active : PSet EntryName) (hR7 : EntryName.R7 ∈ Active) :
    ∀ st, Reachable Init (Next m Active) st → P7_BGNoAuthority st :=
  invariant (fun st => Base Active st ∧ P7_BGNoAuthority st) P7_BGNoAuthority
    (fun st h => ⟨InitBase Active st h, (InitSafe st h).2.2.2.2.1⟩)
    (fun st st' ⟨hb, hp⟩ hn => ⟨NextBase m Active st st' hb hn, NextP7 m Active hR7 st st' hb hp hn⟩)
    (fun _ h => h.2)

/-- `THEOREM P9Always == Spec => []P9_NoSoloGrant` under `"R2" ∈ Active /\ ("R1" ∈ Active \/ "R9" ∈ Active)`. -/
theorem P9Always (m : Mech) (Active : PSet EntryName) (hR2 : EntryName.R2 ∈ Active)
    (hR19 : EntryName.R1 ∈ Active ∨ EntryName.R9 ∈ Active) :
    ∀ st, Reachable Init (Next m Active) st → P9_NoSoloGrant st :=
  invariant (fun st => Base Active st ∧ P9_NoSoloGrant st) P9_NoSoloGrant
    (fun st h => ⟨InitBase Active st h, (InitSafe st h).2.2.2.2.2⟩)
    (fun st st' ⟨hb, hp⟩ hn => ⟨NextBase m Active st st' hb hn, NextP9 m Active hR2 hR19 st st' hb hp hn⟩)
    (fun _ h => h.2)

/-- `THEOREM SafeAlways == Spec => []Safe` under `AllEntries ⊆ Active, Mech # "norecuse"`. -/
theorem SafeAlways (Active : PSet EntryName) (hall : ∀ e, e ∈ Active) :
    ∀ st, Reachable Init (Next .rev5 Active) st → Safe st :=
  fun st h => ⟨P1Always _ Active (hall .R1) st h, P2Always _ Active (hall .R2) st h, P3Always Active st h,
    P5Always _ Active (hall .R5) st h, P7Always _ Active (hall .R7) st h,
    P9Always _ Active (hall .R2) (Or.inl (hall .R1)) st h⟩

/-- `MutNoRecuseCountsAuthor`: without recusal the author on the roster is a counted seat. -/
theorem MutNoRecuseCountsAuthor (st : State) (h : st.rules.grant Author = true) : Counted .norecuse st Author = true := by
  simp [Counted, h]

#print axioms P1Always
#print axioms P2Always
#print axioms P3Always
#print axioms P5Always
#print axioms P7Always
#print axioms P9Always
#print axioms SafeAlways

end Topak.Spec.RulesFloorNV_rev5
