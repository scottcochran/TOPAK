import TopakSpec.Prelude
/-!
# RunSeats.tla in Lean

ADR-0043 §2, alphabets by seat kind in Run, and ADR-0040 §2, no variant name common to Build and Run.
`spec/RunSeats.tla` re-encoded; `spec/RunSeats_proof.tla`'s theorems proved by induction on reachable
states, with its inductive invariant `Alphabets` and its `ByKind`, `ByDomain` for the LET in `Grant`.
The finite-table lemmas (`KindActuate`, `ObserverRun`, `DomainNames`) are checked by cases over every
mutation, seat and act. The TLA+ action `Act(s)` is `ActStep` here.

Mutations: `M_KIND`, `M_DOMAIN`, `M_OBSEMIT`. Each theorem takes as hypothesis only the mutations that
break it; `M_OBSEMIT` breaks none, and the theorems hold under it.
-/

namespace Topak.Spec.RunSeats
open Topak.Spec PSet

inductive Mut | none | M_KIND | M_DOMAIN | M_OBSEMIT
  deriving DecidableEq

/-- `Seats == {"rt", "ro", "bt", "bo"}` -/
inductive Seat | rt | ro | bt | bo
  deriving DecidableEq
/-- `BuildActs ∪ RunActs` -/
inductive Act | Read | Draft | Emit | Consult | Actuate | Report
  deriving DecidableEq
inductive Kind | thinker | observer
  deriving DecidableEq
inductive Domain | run | build
  deriving DecidableEq

/-- `BuildActs == {"Read", "Draft", "Emit"}` -/
def BuildActs : PSet Act := {.Read, .Draft, .Emit}
/-- `RunActs == {"Consult", "Actuate", "Report"}` -/
def RunActs : PSet Act := {.Consult, .Actuate, .Report}
def Acts : PSet Act := BuildActs ∪ RunActs

/-- `KindOf == [rt |-> "thinker", ro |-> "observer", bt |-> "thinker", bo |-> "observer"]` -/
def KindOf : Seat → Kind
  | .rt => .thinker | .ro => .observer | .bt => .thinker | .bo => .observer
/-- `DomainOf == [rt |-> "run", ro |-> "run", bt |-> "build", bo |-> "build"]` -/
def DomainOf : Seat → Domain
  | .rt => .run | .ro => .run | .bt => .build | .bo => .build

/-- `DomainActs(d) == IF d = "run" THEN RunActs ELSE BuildActs` -/
def DomainActs : Domain → PSet Act
  | .run => RunActs
  | .build => BuildActs

/-- ADR-0037 §4 for Build, ADR-0043 §2 for Run.
```
KindBound(k) ==
  CASE k = "thinker"  -> {"Read", "Draft", "Emit", "Consult", "Actuate", "Report"}
    [] k = "observer" -> IF Mut = "M_OBSEMIT" THEN {"Read", "Emit", "Report"}
                                              ELSE {"Read", "Emit", "Consult", "Report"}
``` -/
def KindBound (m : Mut) : Kind → PSet Act
  | .thinker  => {.Read, .Draft, .Emit, .Consult, .Actuate, .Report}
  | .observer => if m = .M_OBSEMIT then {.Read, .Emit, .Report} else {.Read, .Emit, .Consult, .Report}

structure LeaseRec where
  live : Prop
  alphabet : PSet Act

/-- `NoLease == [live |-> FALSE, alphabet |-> {}]` -/
def NoLease : LeaseRec := ⟨False, ∅⟩

/-- `[act |-> a, kind |-> KindOf[s], domain |-> DomainOf[s]]` -/
structure ActRec where
  act : Act
  kind : Kind
  domain : Domain

structure State where
  lease : Seat → LeaseRec
  acted : PSet ActRec

def Init (st : State) : Prop := (st.lease = fun _ => NoLease) ∧ st.acted = ∅

/-- The LET of `Grant`: `byKind == IF Mut = "M_KIND" THEN Acts ELSE KindBound(KindOf[s])` -/
def ByKind (m : Mut) (s : Seat) : PSet Act := if m = .M_KIND then Acts else KindBound m (KindOf s)
/-- `byDomain == IF Mut = "M_DOMAIN" THEN Acts ELSE DomainActs(DomainOf[s])` -/
def ByDomain (m : Mut) (s : Seat) : PSet Act := if m = .M_DOMAIN then Acts else DomainActs (DomainOf s)

/-- ```
Grant(s) ==
  /\ ~lease[s].live
  /\ LET byKind == ... byDomain == ...
     IN lease' = [lease EXCEPT ![s] = [live |-> TRUE, alphabet |-> byKind ∩ byDomain]]
  /\ UNCHANGED acted
``` -/
def Grant (m : Mut) (s : Seat) (st st' : State) : Prop :=
  ¬ (st.lease s).live ∧
  st'.lease = upd st.lease s ⟨True, ByKind m s ∩ ByDomain m s⟩ ∧
  st'.acted = st.acted

/-- ```
Act(s) ==
  /\ lease[s].live
  /\ ∃ a ∈ lease[s].alphabet : acted' = acted ∪ {[act |-> a, kind |-> KindOf[s], domain |-> DomainOf[s]]}
  /\ UNCHANGED lease
``` -/
def ActStep (s : Seat) (st st' : State) : Prop :=
  (st.lease s).live ∧
  (∃ a, a ∈ (st.lease s).alphabet ∧ st'.acted = st.acted ∪ {⟨a, KindOf s, DomainOf s⟩}) ∧
  st'.lease = st.lease

/-- `EndRound(s) == lease[s].live /\ lease' = [lease EXCEPT ![s] = NoLease] /\ UNCHANGED acted` -/
def EndRound (s : Seat) (st st' : State) : Prop :=
  (st.lease s).live ∧ st'.lease = upd st.lease s NoLease ∧ st'.acted = st.acted

/-- `Next == ∃ s ∈ Seats : Act(s) \/ EndRound(s) \/ Grant(s)` -/
def Next (m : Mut) (st st' : State) : Prop :=
  ∃ s, ActStep s st st' ∨ EndRound s st st' ∨ Grant m s st st'

/-! ## The three properties -/

/-- ADR-0043 §2. `∀ r ∈ acted : r.act = "Actuate" => r.kind = "thinker"` -/
def OnlyThinkersActuate (st : State) : Prop :=
  ∀ r, r ∈ st.acted → r.act = .Actuate → r.kind = .thinker

/-- ADR-0043 §2. `∀ r ∈ acted : (r.kind = "observer" /\ r.domain = "run") => r.act ∈ {"Consult", "Report"}` -/
def ObserversConsultAndReport (st : State) : Prop :=
  ∀ r, r ∈ st.acted → (r.kind = .observer ∧ r.domain = .run) → r.act ∈ ({.Consult, .Report} : PSet Act)

/-- ADR-0040 §2. `∀ r ∈ acted : (r.act ∈ RunActs) <=> (r.domain = "run")` -/
def NoNameCrossesDomains (st : State) : Prop :=
  ∀ r, r ∈ st.acted → (r.act ∈ RunActs ↔ r.domain = .run)

def Safe (st : State) : Prop := OnlyThinkersActuate st ∧ ObserversConsultAndReport st ∧ NoNameCrossesDomains st

/-! ## The finite tables, one fact per invariant -/

theorem KindActuate (m : Mut) (hm : m ≠ .M_KIND) (s : Seat) (a : Act) (h : a ∈ ByKind m s) (ha : a = .Actuate) :
    KindOf s = .thinker := by
  cases m <;> cases s <;> cases a <;> simp_all [ByKind, KindOf, KindBound]

theorem ObserverRun (m : Mut) (hk : m ≠ .M_KIND) (hd : m ≠ .M_DOMAIN) (s : Seat) (a : Act)
    (h : a ∈ ByKind m s ∩ ByDomain m s) (hko : KindOf s = .observer) (hdo : DomainOf s = .run) :
    a ∈ ({.Consult, .Report} : PSet Act) := by
  cases m <;> cases s <;> cases a <;>
    simp_all [ByKind, ByDomain, KindOf, DomainOf, KindBound, DomainActs, RunActs]

theorem DomainNames (m : Mut) (hd : m ≠ .M_DOMAIN) (s : Seat) (a : Act) (h : a ∈ ByDomain m s) :
    (a ∈ RunActs ↔ DomainOf s = .run) := by
  cases m <;> cases s <;> cases a <;> simp_all [ByDomain, DomainOf, DomainActs, BuildActs, RunActs]

/-! ## Proofs -/

/-- `Alphabets`: every live alphabet is the granted one. Holds under every mutation. -/
def Alphabets (m : Mut) (st : State) : Prop :=
  ∀ s, (st.lease s).live → (st.lease s).alphabet = ByKind m s ∩ ByDomain m s

/-- One inductive invariant for the three properties, each guarded by the mutations that break it. -/
def Inv (m : Mut) (st : State) : Prop :=
  Alphabets m st ∧
  (m ≠ .M_KIND → OnlyThinkersActuate st) ∧
  (m ≠ .M_KIND → m ≠ .M_DOMAIN → ObserversConsultAndReport st) ∧
  (m ≠ .M_DOMAIN → NoNameCrossesDomains st)

theorem InitInv (m : Mut) (st : State) (h : Init st) : Inv m st := by
  obtain ⟨hl, ha⟩ := h
  refine ⟨?_, ?_, ?_, ?_⟩
  · intro s hs; simp [hl, NoLease] at hs
  · intro _ r hr; simp [ha] at hr
  · intro _ _ r hr; simp [ha] at hr
  · intro _ r hr; simp [ha] at hr

theorem NextInv (m : Mut) (st st' : State) (hi : Inv m st) (hn : Next m st st') : Inv m st' := by
  obtain ⟨hA, hT, hO, hD⟩ := hi
  obtain ⟨s, hs⟩ := hn
  rcases hs with ⟨hlive, ⟨a, ha, hacted⟩, hlease⟩ | ⟨-, hlease, hacted⟩ | ⟨-, hlease, hacted⟩
  · -- Act(s): the act is in a live alphabet, which is the granted one
    have hA' : Alphabets m st' := by intro t ht; rw [hlease] at ht ⊢; exact hA t ht
    rw [hA s hlive] at ha
    obtain ⟨hak, had⟩ := (PSet.mem_inter _ _ _).mp ha
    refine ⟨hA', ?_, ?_, ?_⟩
    · intro hk r hr
      rw [hacted] at hr
      rcases hr with hr | hr
      · exact hT hk r hr
      · have hr : r = ⟨a, KindOf s, DomainOf s⟩ := hr
        subst hr
        intro hact
        exact KindActuate m hk s a hak hact
    · intro hk hd r hr
      rw [hacted] at hr
      rcases hr with hr | hr
      · exact hO hk hd r hr
      · have hr : r = ⟨a, KindOf s, DomainOf s⟩ := hr
        subst hr
        intro ⟨hko, hdo⟩
        exact ObserverRun m hk hd s a ha hko hdo
    · intro hd r hr
      rw [hacted] at hr
      rcases hr with hr | hr
      · exact hD hd r hr
      · have hr : r = ⟨a, KindOf s, DomainOf s⟩ := hr
        subst hr
        exact DomainNames m hd s a had
  · -- EndRound(s)
    have hA' : Alphabets m st' := by
      intro t ht
      rw [hlease] at ht ⊢
      by_cases hts : t = s
      · subst hts; simp [NoLease] at ht
      · rw [upd_other _ _ _ _ hts] at ht ⊢; exact hA t ht
    refine ⟨hA', ?_, ?_, ?_⟩
    · intro hk; unfold OnlyThinkersActuate; rw [hacted]; exact hT hk
    · intro hk hd; unfold ObserversConsultAndReport; rw [hacted]; exact hO hk hd
    · intro hd; unfold NoNameCrossesDomains; rw [hacted]; exact hD hd
  · -- Grant(s): the issued alphabet is ByKind ∩ ByDomain by construction
    have hA' : Alphabets m st' := by
      intro t ht
      rw [hlease] at ht ⊢
      by_cases hts : t = s
      · subst hts; simp
      · rw [upd_other _ _ _ _ hts] at ht ⊢; exact hA t ht
    refine ⟨hA', ?_, ?_, ?_⟩
    · intro hk; unfold OnlyThinkersActuate; rw [hacted]; exact hT hk
    · intro hk hd; unfold ObserversConsultAndReport; rw [hacted]; exact hO hk hd
    · intro hd; unfold NoNameCrossesDomains; rw [hacted]; exact hD hd

/-- `THEOREM OnlyThinkersActuateAlways == ASSUME Mut # "M_KIND" PROVE Spec => []OnlyThinkersActuate` -/
theorem OnlyThinkersActuateAlways (m : Mut) (hm : m ≠ .M_KIND) :
    ∀ st, Reachable Init (Next m) st → OnlyThinkersActuate st :=
  invariant (Inv m) OnlyThinkersActuate (InitInv m) (NextInv m) (fun _ h => h.2.1 hm)

/-- `THEOREM ObserversConsultAndReportAlways == ASSUME Mut # "M_KIND", Mut # "M_DOMAIN" PROVE ...` -/
theorem ObserversConsultAndReportAlways (m : Mut) (hk : m ≠ .M_KIND) (hd : m ≠ .M_DOMAIN) :
    ∀ st, Reachable Init (Next m) st → ObserversConsultAndReport st :=
  invariant (Inv m) ObserversConsultAndReport (InitInv m) (NextInv m) (fun _ h => h.2.2.1 hk hd)

/-- `THEOREM NoNameCrossesDomainsAlways == ASSUME Mut # "M_DOMAIN" PROVE Spec => []NoNameCrossesDomains` -/
theorem NoNameCrossesDomainsAlways (m : Mut) (hd : m ≠ .M_DOMAIN) :
    ∀ st, Reachable Init (Next m) st → NoNameCrossesDomains st :=
  invariant (Inv m) NoNameCrossesDomains (InitInv m) (NextInv m) (fun _ h => h.2.2.2 hd)

/-- `THEOREM SafeAlways == ASSUME Mut = "none" PROVE Spec => []Safe` -/
theorem SafeAlways : ∀ st, Reachable Init (Next .none) st → Safe st :=
  fun st h => ⟨OnlyThinkersActuateAlways .none (by decide) st h,
    ObserversConsultAndReportAlways .none (by decide) (by decide) st h,
    NoNameCrossesDomainsAlways .none (by decide) st h⟩

/-- M_OBSEMIT breaks nothing: the three theorems hold under it too (ADR-0046 §5). -/
theorem SafeUnderObsEmit : ∀ st, Reachable Init (Next .M_OBSEMIT) st → Safe st :=
  fun st h => ⟨OnlyThinkersActuateAlways .M_OBSEMIT (by decide) st h,
    ObserversConsultAndReportAlways .M_OBSEMIT (by decide) (by decide) st h,
    NoNameCrossesDomainsAlways .M_OBSEMIT (by decide) st h⟩

#print axioms OnlyThinkersActuateAlways
#print axioms ObserversConsultAndReportAlways
#print axioms NoNameCrossesDomainsAlways
#print axioms SafeAlways

end Topak.Spec.RunSeats
