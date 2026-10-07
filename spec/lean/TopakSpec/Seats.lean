import TopakSpec.Prelude
/-!
# Seats.tla in Lean

ADR-0037: the LTRO decomposition into principals. `spec/Seats.tla`, re-encoded as a transition system;
`spec/Seats_proof.tla`'s theorems proved by induction on reachable states, with its inductive
invariant `Alphabets`. Each definition carries the TLA+ it transcribes. The `TypeOK` lemmas of the TLAPS
proof have no counterpart: Lean's types carry them. The TLA+ action `Act(s)` is `ActStep` here, since
`Act` names the set of acts.

Mutations: `M_KIND`, the grant path ignores the kind bound; `M_SEAT`, the one-live-lease rule is keyed by
seat only. Each theorem takes as hypothesis only the mutation that breaks it. Witnesses stay with TLC.
-/

namespace Topak.Spec.Seats
open Topak.Spec PSet

inductive Mut | none | M_KIND | M_SEAT
  deriving DecidableEq

/-- `Principals == {"p1", "p2"}` -/
inductive Principal | p1 | p2
  deriving DecidableEq
/-- `Seats == {"s1", "s2", "s3"}` -/
inductive Seat | s1 | s2 | s3
  deriving DecidableEq
/-- `Acts == {"Read", "Draft", "Emit", "Vote"}` -/
inductive Act | Read | Draft | Emit | Vote
  deriving DecidableEq
/-- The kinds `KindOf` ranges over. -/
inductive Kind | thinker | observer | grant
  deriving DecidableEq

def Acts : PSet Act := univ
/-- `Authoring == {"Draft"}` -/
def Authoring : PSet Act := {.Draft}

/-- `KindOf == [s1 |-> "thinker", s2 |-> "observer", s3 |-> "grant"]` -/
def KindOf : Seat → Kind
  | .s1 => .thinker
  | .s2 => .observer
  | .s3 => .grant

/-- ADR-0037 §4, Build column.
```
KindBound(k) ==
  CASE k = "thinker"  -> {"Read", "Draft", "Emit"}
    [] k = "observer" -> {"Read", "Emit", "Vote"}
    [] k = "grant"    -> {"Read", "Emit", "Vote"}
``` -/
def KindBound : Kind → PSet Act
  | .thinker  => {.Read, .Draft, .Emit}
  | .observer => {.Read, .Emit, .Vote}
  | .grant    => {.Read, .Emit, .Vote}

/-- `[live : BOOLEAN, principal : Principals ∪ {"none"}, alphabet : SUBSET Acts]`; "none" is `Option.none`. -/
structure LeaseRec where
  live : Prop
  principal : Option Principal
  alphabet : PSet Act

/-- `NoLease == [live |-> FALSE, principal |-> "none", alphabet |-> {}]` -/
def NoLease : LeaseRec := ⟨False, none, ∅⟩

/-- `[act |-> a, kind |-> KindOf[s]]` -/
structure ActRec where
  act : Act
  kind : Kind

/-- `VARIABLES lease, acted` -/
structure State where
  lease : Seat → LeaseRec
  acted : PSet ActRec

/-- `Init == lease = [s ∈ Seats |-> NoLease] /\ acted = {}` -/
def Init (st : State) : Prop := (st.lease = fun _ => NoLease) ∧ st.acted = ∅

/-- `HoldsElsewhere(p, s) == ∃ t ∈ Seats : t # s /\ lease[t].live /\ lease[t].principal = p` -/
def HoldsElsewhere (st : State) (p : Principal) (s : Seat) : Prop :=
  ∃ t, t ≠ s ∧ (st.lease t).live ∧ (st.lease t).principal = some p

/-- ```
Grant(p, s) ==
  /\ ~lease[s].live
  /\ Mut = "M_SEAT" \/ ~HoldsElsewhere(p, s)
  /\ LET a == IF Mut = "M_KIND" THEN Acts ELSE KindBound(KindOf[s])
     IN lease' = [lease EXCEPT ![s] = [live |-> TRUE, principal |-> p, alphabet |-> a]]
  /\ UNCHANGED acted
``` -/
def Grant (m : Mut) (p : Principal) (s : Seat) (st st' : State) : Prop :=
  ¬ (st.lease s).live ∧
  (m = .M_SEAT ∨ ¬ HoldsElsewhere st p s) ∧
  st'.lease = upd st.lease s ⟨True, some p, if m = .M_KIND then Acts else KindBound (KindOf s)⟩ ∧
  st'.acted = st.acted

/-- ```
Act(s) ==
  /\ lease[s].live
  /\ ∃ a ∈ lease[s].alphabet : acted' = acted ∪ {[act |-> a, kind |-> KindOf[s]]}
  /\ UNCHANGED lease
``` -/
def ActStep (s : Seat) (st st' : State) : Prop :=
  (st.lease s).live ∧
  (∃ a, a ∈ (st.lease s).alphabet ∧ st'.acted = st.acted ∪ {⟨a, KindOf s⟩}) ∧
  st'.lease = st.lease

/-- `EndRound(s) == lease[s].live /\ lease' = [lease EXCEPT ![s] = NoLease] /\ UNCHANGED acted` -/
def EndRound (s : Seat) (st st' : State) : Prop :=
  (st.lease s).live ∧ st'.lease = upd st.lease s NoLease ∧ st'.acted = st.acted

/-- `Next == ∃ s ∈ Seats : Act(s) \/ EndRound(s) \/ ∃ p ∈ Principals : Grant(p, s)` -/
def Next (m : Mut) (st st' : State) : Prop :=
  ∃ s, ActStep s st st' ∨ EndRound s st st' ∨ ∃ p, Grant m p s st st'

/-! ## The two properties -/

/-- §4. ```
OnlyThinkersAuthor ==
  ∀ r ∈ acted : /\ r.act ∈ Authoring => r.kind = "thinker"
                /\ r.act = "Vote"    => r.kind # "thinker"
``` -/
def OnlyThinkersAuthor (st : State) : Prop :=
  ∀ r, r ∈ st.acted → (r.act ∈ Authoring → r.kind = .thinker) ∧ (r.act = .Vote → r.kind ≠ .thinker)

/-- §1. `∀ s, t ∈ Seats : (s # t /\ lease[s].live /\ lease[t].live) => lease[s].principal # lease[t].principal` -/
def OneSeatPerPrincipal (st : State) : Prop :=
  ∀ s t, (s ≠ t ∧ (st.lease s).live ∧ (st.lease t).live) → (st.lease s).principal ≠ (st.lease t).principal

def Safe (st : State) : Prop := OnlyThinkersAuthor st ∧ OneSeatPerPrincipal st

/-! ## Proofs -/

/-- `KindBoundKinds` of the TLAPS proof: a kind bound admits an authoring act only for a thinker and
Vote only for others. A finite table, checked by cases. -/
theorem KindBoundKinds (s : Seat) (a : Act) (h : a ∈ KindBound (KindOf s)) :
    (a ∈ Authoring → KindOf s = .thinker) ∧ (a = .Vote → KindOf s ≠ .thinker) := by
  cases s <;> cases a <;> simp_all [KindBound, KindOf, Authoring]

/-- `Alphabets`: under the specified grant a live alphabet is the seat's kind bound. -/
def Alphabets (st : State) : Prop :=
  ∀ s, (st.lease s).live → (st.lease s).alphabet = KindBound (KindOf s)

def InvA (st : State) : Prop := Alphabets st ∧ OnlyThinkersAuthor st

theorem InitInvA (st : State) (h : Init st) : InvA st := by
  obtain ⟨hl, ha⟩ := h
  constructor
  · intro s hs; simp [hl, NoLease] at hs
  · intro r hr; simp [ha] at hr

theorem NextInvA (m : Mut) (hm : m ≠ .M_KIND) (st st' : State) (hi : InvA st) (hn : Next m st st') :
    InvA st' := by
  obtain ⟨hA, hO⟩ := hi
  obtain ⟨s, hs⟩ := hn
  rcases hs with ⟨hlive, ⟨a, ha, hacted⟩, hlease⟩ | ⟨-, hlease, hacted⟩ | ⟨p, -, -, hlease, hacted⟩
  · -- Act(s): the alphabet acted from is a live one, hence the kind bound
    constructor
    · intro t ht; rw [hlease] at ht ⊢; exact hA t ht
    · intro r hr
      rw [hacted] at hr
      rcases hr with hr | hr
      · exact hO r hr
      · have hr : r = ⟨a, KindOf s⟩ := hr
        subst hr
        rw [hA s hlive] at ha
        exact KindBoundKinds s a ha
  · -- EndRound(s)
    constructor
    · intro t ht
      rw [hlease] at ht ⊢
      by_cases hts : t = s
      · subst hts; simp [NoLease] at ht
      · rw [upd_other _ _ _ _ hts] at ht ⊢; exact hA t ht
    · intro r hr; rw [hacted] at hr; exact hO r hr
  · -- Grant(p, s): the issued alphabet is the kind bound, since Mut # "M_KIND"
    constructor
    · intro t ht
      rw [hlease] at ht ⊢
      by_cases hts : t = s
      · subst hts; simp [hm]
      · rw [upd_other _ _ _ _ hts] at ht ⊢; exact hA t ht
    · intro r hr; rw [hacted] at hr; exact hO r hr

/-- `THEOREM OnlyThinkersAuthorAlways == ASSUME Mut # "M_KIND" PROVE Spec => []OnlyThinkersAuthor` -/
theorem OnlyThinkersAuthorAlways (m : Mut) (hm : m ≠ .M_KIND) :
    ∀ st, Reachable Init (Next m) st → OnlyThinkersAuthor st :=
  invariant InvA OnlyThinkersAuthor InitInvA (NextInvA m hm) (fun _ h => h.2)

theorem InitInvS (st : State) (h : Init st) : OneSeatPerPrincipal st := by
  obtain ⟨hl, -⟩ := h
  rintro s t ⟨-, hs, -⟩
  simp [hl, NoLease] at hs

theorem NextInvS (m : Mut) (hm : m ≠ .M_SEAT) (st st' : State) (hi : OneSeatPerPrincipal st)
    (hn : Next m st st') : OneSeatPerPrincipal st' := by
  obtain ⟨s, hs⟩ := hn
  rcases hs with ⟨-, -, hlease⟩ | ⟨-, hlease, -⟩ | ⟨p, -, hhold, hlease, -⟩
  · unfold OneSeatPerPrincipal; rw [hlease]; exact hi
  · -- EndRound(s): one fewer live lease
    intro u v ⟨huv, hu, hv⟩
    rw [hlease] at hu hv ⊢
    by_cases hus : u = s
    · subst hus; simp [NoLease] at hu
    · by_cases hvs : v = s
      · subst hvs; simp [NoLease] at hv
      · rw [upd_other _ _ _ _ hus] at hu ⊢
        rw [upd_other _ _ _ _ hvs] at hv ⊢
        exact hi u v ⟨huv, hu, hv⟩
  · -- Grant(p, s): refused when p holds another live seat, since Mut # "M_SEAT"
    have hnh : ¬ HoldsElsewhere st p s := by
      rcases hhold with h | h
      · exact absurd h hm
      · exact h
    intro u v ⟨huv, hu, hv⟩
    rw [hlease] at hu hv ⊢
    by_cases hus : u = s
    · subst hus
      rw [upd_other _ _ _ _ (Ne.symm huv)] at hv ⊢
      rw [upd_same]
      intro heq
      exact hnh ⟨v, Ne.symm huv, hv, heq.symm⟩
    · by_cases hvs : v = s
      · subst hvs
        rw [upd_other _ _ _ _ hus] at hu ⊢
        rw [upd_same]
        intro heq
        exact hnh ⟨u, hus, hu, heq⟩
      · rw [upd_other _ _ _ _ hus] at hu ⊢
        rw [upd_other _ _ _ _ hvs] at hv ⊢
        exact hi u v ⟨huv, hu, hv⟩

/-- `THEOREM OneSeatPerPrincipalAlways == ASSUME Mut # "M_SEAT" PROVE Spec => []OneSeatPerPrincipal` -/
theorem OneSeatPerPrincipalAlways (m : Mut) (hm : m ≠ .M_SEAT) :
    ∀ st, Reachable Init (Next m) st → OneSeatPerPrincipal st :=
  invariant OneSeatPerPrincipal OneSeatPerPrincipal InitInvS (NextInvS m hm) (fun _ h => h)

/-- `THEOREM SafeAlways == ASSUME Mut = "none" PROVE Spec => []Safe` -/
theorem SafeAlways : ∀ st, Reachable Init (Next .none) st → Safe st :=
  fun st h => ⟨OnlyThinkersAuthorAlways .none (by decide) st h, OneSeatPerPrincipalAlways .none (by decide) st h⟩

/-! ## Why the mutations must fail (the counterexamples are TLC's) -/

/-- `MutKindGrantsAll`: under M_KIND a grant issues every act. -/
theorem MutKindGrantsAll (p : Principal) (s : Seat) (st st' : State) (h : Grant .M_KIND p s st st') :
    (st'.lease s).alphabet = Acts := by
  obtain ⟨-, -, hl, -⟩ := h
  rw [hl, upd_same]
  rfl

/-- `MutSeatIgnoresHolder`: under M_SEAT a grant is not refused for a principal seated elsewhere. -/
theorem MutSeatIgnoresHolder (p : Principal) (s : Seat) (st : State) (hfree : ¬ (st.lease s).live)
    (_ : HoldsElsewhere st p s) :
    Grant .M_SEAT p s st ⟨upd st.lease s ⟨True, some p, KindBound (KindOf s)⟩, st.acted⟩ := by
  refine ⟨hfree, Or.inl rfl, ?_, rfl⟩
  simp

#print axioms OnlyThinkersAuthorAlways
#print axioms OneSeatPerPrincipalAlways
#print axioms SafeAlways

end Topak.Spec.Seats
