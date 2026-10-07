import TopakSpec.Prelude
/-!
# Coupling.tla in Lean

ADR-0039, Observer liveness coupled to admission in Run. `spec/Coupling.tla` re-encoded;
`spec/Coupling_proof.tla`'s theorems proved by induction on reachable states with its inductive invariant
(`Shape`, `Past`, `Bound`), for every `K`, `R` and `MaxRound`. The constants are a `Cfg`. The TLAPS proof's
three assumptions, that `K`, `R` and `MaxRound` are naturals, hold by type. `K < R`, which the module notes,
is not needed and not assumed; neither is `MaxRound = 2`.

Encoding notes beyond the prelude's: `tLive`, `oLease` and the two `fresh` fields, which the module only
ever sets to TRUE or FALSE, are `Bool`; the three flag variables are `Prop`. `mark` and `seal`, TLA+
functions on `Rounds`, are `Nat → Nat` and the invariants speak of them on `Rounds` only; `seal` is `seals`, since
`seal` is a Lean keyword. TLA+'s `-` on
naturals is integer subtraction, so `seq - mark[round]` is computed in `Int`. The arithmetic the TLAPS
proof hands to SMT is closed by `omega`.

Mutations: `M_NOCOUPLE`, `M_MARK`, `M_ROUNDS`, `M_CORR`. Each theorem takes only the mutations that break it.
-/

namespace Topak.Spec.Coupling
open Topak.Spec PSet

inductive Mut | none | M_NOCOUPLE | M_MARK | M_ROUNDS | M_CORR
  deriving DecidableEq

/-- `CONSTANTS Mut, K, R, MaxRound` -/
structure Cfg where
  m : Mut
  K : Nat
  R : Nat
  MaxRound : Nat

/-- `Rounds == 1..MaxRound` -/
def Rounds (c : Cfg) (r : Nat) : Prop := 1 ≤ r ∧ r ≤ c.MaxRound

/-- `fresh \in [o : BOOLEAN, c : BOOLEAN]` -/
structure Fresh where
  o : Bool
  c : Bool
  deriving DecidableEq

structure State where
  round : Nat
  tLive : Bool
  seq : Nat
  oLease : Bool
  fresh : Fresh
  mark : Nat → Nat
  seals : Nat → Nat
  admittedUnlive : Prop
  refusedForCorr : Prop
  refused : Prop

/-- `Init`: round 0, nothing live, zero marks and seals on every round, flags down. -/
def Init (c : Cfg) (st : State) : Prop :=
  st.round = 0 ∧ st.tLive = false ∧ st.seq = 0 ∧ st.oLease = false ∧ st.fresh = ⟨false, false⟩ ∧
  (∀ r, Rounds c r → st.mark r = 0) ∧ (∀ r, Rounds c r → st.seals r = 0) ∧
  ¬ st.admittedUnlive ∧ ¬ st.refusedForCorr ∧ ¬ st.refused

/-- `Coupled == Mut # "M_NOCOUPLE"` -/
def Coupled (c : Cfg) : Prop := c.m ≠ .M_NOCOUPLE

/-- §1. `LiveO == oLease /\ fresh.o /\ IF Mut = "M_MARK" \/ round = 0 THEN TRUE ELSE seq - mark[round] < K` -/
def LiveO (c : Cfg) (st : State) : Prop :=
  st.oLease = true ∧ st.fresh.o = true ∧
  (if c.m = .M_MARK ∨ st.round = 0 then True else (st.seq : Int) - st.mark st.round < c.K)

/-- `LiveC == fresh.c` -/
def LiveC (st : State) : Prop := st.fresh.c = true

/-- The flags, unchanged. -/
def FlagsUnch (st st' : State) : Prop :=
  (st'.admittedUnlive ↔ st.admittedUnlive) ∧ (st'.refusedForCorr ↔ st.refusedForCorr) ∧ (st'.refused ↔ st.refused)

/-- §2. ```
GrantT == /\ ~tLive /\ round < MaxRound
          /\ IF round = 0 \/ Mut = "M_ROUNDS" THEN TRUE ELSE mark[round] >= seal[round]
          /\ round' = round + 1 /\ tLive' = TRUE /\ seq' = 0
          /\ UNCHANGED <<oLease, fresh, mark, seal, admittedUnlive, refusedForCorr, refused>>
``` -/
def GrantT (c : Cfg) (st st' : State) : Prop :=
  st.tLive = false ∧ st.round < c.MaxRound ∧
  (if st.round = 0 ∨ c.m = .M_ROUNDS then True else st.mark st.round ≥ st.seals st.round) ∧
  st'.round = st.round + 1 ∧ st'.tLive = true ∧ st'.seq = 0 ∧
  st'.oLease = st.oLease ∧ st'.fresh = st.fresh ∧ st'.mark = st.mark ∧ st'.seals = st.seals ∧ FlagsUnch st st'

/-- `Allowed == (~Coupled \/ LiveO) /\ (Mut # "M_CORR" \/ LiveC)` -/
def Allowed (c : Cfg) (st : State) : Prop :=
  (¬ Coupled c ∨ LiveO c st) ∧ (c.m ≠ .M_CORR ∨ LiveC st)

/-- ```
Admit == /\ tLive /\ seq < R /\ Allowed
         /\ seq' = seq + 1
         /\ admittedUnlive' = (admittedUnlive \/ ~LiveO)
         /\ UNCHANGED <<round, tLive, oLease, fresh, mark, seal, refusedForCorr, refused>>
``` -/
def Admit (c : Cfg) (st st' : State) : Prop :=
  st.tLive = true ∧ st.seq < c.R ∧ Allowed c st ∧
  st'.seq = st.seq + 1 ∧
  (st'.admittedUnlive ↔ (st.admittedUnlive ∨ ¬ LiveO c st)) ∧
  st'.round = st.round ∧ st'.tLive = st.tLive ∧ st'.oLease = st.oLease ∧ st'.fresh = st.fresh ∧
  st'.mark = st.mark ∧ st'.seals = st.seals ∧
  (st'.refusedForCorr ↔ st.refusedForCorr) ∧ (st'.refused ↔ st.refused)

/-- ```
Refuse == /\ tLive /\ seq < R /\ ~Allowed
          /\ refused' = TRUE
          /\ refusedForCorr' = (refusedForCorr \/ (LiveO /\ ~LiveC))
          /\ UNCHANGED <<round, tLive, seq, oLease, fresh, mark, seal, admittedUnlive>>
``` -/
def Refuse (c : Cfg) (st st' : State) : Prop :=
  st.tLive = true ∧ st.seq < c.R ∧ ¬ Allowed c st ∧
  st'.refused ∧
  (st'.refusedForCorr ↔ (st.refusedForCorr ∨ (LiveO c st ∧ ¬ LiveC st))) ∧
  st'.round = st.round ∧ st'.tLive = st.tLive ∧ st'.seq = st.seq ∧ st'.oLease = st.oLease ∧
  st'.fresh = st.fresh ∧ st'.mark = st.mark ∧ st'.seals = st.seals ∧
  (st'.admittedUnlive ↔ st.admittedUnlive)

/-- `EndRoundT == tLive /\ tLive' = FALSE /\ seal' = [seal EXCEPT ![round] = seq] /\ UNCHANGED <<...>>` -/
def EndRoundT (st st' : State) : Prop :=
  st.tLive = true ∧ st'.tLive = false ∧ st'.seals = upd st.seals st.round st.seq ∧
  st'.round = st.round ∧ st'.seq = st.seq ∧ st'.oLease = st.oLease ∧ st'.fresh = st.fresh ∧
  st'.mark = st.mark ∧ FlagsUnch st st'

/-- ```
Heartbeat(r, w) == /\ oLease /\ r <= round /\ r >= 1
                   /\ w >= mark[r] /\ w <= (IF r = round THEN seq ELSE seal[r])
                   /\ mark' = [mark EXCEPT ![r] = w]
                   /\ fresh' = [fresh EXCEPT !.o = TRUE]
                   /\ UNCHANGED <<round, tLive, seq, oLease, seal, admittedUnlive, refusedForCorr, refused>>
``` -/
def Heartbeat (r w : Nat) (st st' : State) : Prop :=
  st.oLease = true ∧ r ≤ st.round ∧ r ≥ 1 ∧
  w ≥ st.mark r ∧ w ≤ (if r = st.round then st.seq else st.seals r) ∧
  st'.mark = upd st.mark r w ∧
  st'.fresh = ⟨true, st.fresh.c⟩ ∧
  st'.round = st.round ∧ st'.tLive = st.tLive ∧ st'.seq = st.seq ∧ st'.oLease = st.oLease ∧
  st'.seals = st.seals ∧ FlagsUnch st st'

/-- The actions that touch none of `round`, `tLive`, `seq`, `mark`, `seal`: their common frame. -/
def Quiet (st st' : State) : Prop :=
  st'.round = st.round ∧ st'.tLive = st.tLive ∧ st'.seq = st.seq ∧ st'.mark = st.mark ∧ st'.seals = st.seals ∧
  FlagsUnch st st'

/-- `CorrBeat == fresh' = [fresh EXCEPT !.c = TRUE] /\ UNCHANGED <<...>>` -/
def CorrBeat (st st' : State) : Prop :=
  st'.fresh = ⟨st.fresh.o, true⟩ ∧ st'.oLease = st.oLease ∧ Quiet st st'

/-- `Stale("o")` and `Stale("c")`: `fresh[x] /\ fresh' = [fresh EXCEPT ![x] = FALSE] /\ UNCHANGED <<...>>` -/
def StaleO (st st' : State) : Prop :=
  st.fresh.o = true ∧ st'.fresh = ⟨false, st.fresh.c⟩ ∧ st'.oLease = st.oLease ∧ Quiet st st'
def StaleC (st st' : State) : Prop :=
  st.fresh.c = true ∧ st'.fresh = ⟨st.fresh.o, false⟩ ∧ st'.oLease = st.oLease ∧ Quiet st st'

/-- `GrantO == ~oLease /\ oLease' = TRUE /\ UNCHANGED <<...>>`; `EndO` the reverse. -/
def GrantO (st st' : State) : Prop :=
  st.oLease = false ∧ st'.oLease = true ∧ st'.fresh = st.fresh ∧ Quiet st st'
def EndO (st st' : State) : Prop :=
  st.oLease = true ∧ st'.oLease = false ∧ st'.fresh = st.fresh ∧ Quiet st st'

/-- ```
Next == \/ GrantT \/ Admit \/ Refuse \/ EndRoundT \/ CorrBeat \/ GrantO \/ EndO
        \/ \E x \in {"o", "c"} : Stale(x)
        \/ \E r \in Rounds, w \in 0..R : Heartbeat(r, w)
``` -/
def Next (c : Cfg) (st st' : State) : Prop :=
  GrantT c st st' ∨ Admit c st st' ∨ Refuse c st st' ∨ EndRoundT st st' ∨ CorrBeat st st' ∨
  GrantO st st' ∨ EndO st st' ∨ StaleO st st' ∨ StaleC st st' ∨
  ∃ r w, Rounds c r ∧ w ≤ c.R ∧ Heartbeat r w st st'

/-! ## The three properties -/

/-- §2. `NoAdmitWithoutLiveObserver == ~admittedUnlive` -/
def NoAdmitWithoutLiveObserver (st : State) : Prop := ¬ st.admittedUnlive

/-- `Unread == IF round = 0 THEN 0 ELSE seq - mark[round]` -/
def Unread (st : State) : Int := if st.round = 0 then 0 else (st.seq : Int) - st.mark st.round
/-- `PriorUnread == IF round = 2 THEN seal[1] - mark[1] ELSE 0` -/
def PriorUnread (st : State) : Int := if st.round = 2 then (st.seals 1 : Int) - st.mark 1 else 0
/-- §2. `UnreadBounded == Unread + PriorUnread <= K` -/
def UnreadBounded (c : Cfg) (st : State) : Prop := Unread st + PriorUnread st ≤ c.K

/-- §4. `CorrelatorNeverGates == ~refusedForCorr` -/
def CorrelatorNeverGates (st : State) : Prop := ¬ st.refusedForCorr

def Safe (c : Cfg) (st : State) : Prop :=
  NoAdmitWithoutLiveObserver st ∧ UnreadBounded c st ∧ CorrelatorNeverGates st

/-! ## The inductive invariant for UnreadBounded -/

/-- What `TypeOK` says beyond the types: the round is within range, and a live Thinker is in a round. -/
def TypeOK (c : Cfg) (st : State) : Prop := st.round ≤ c.MaxRound ∧ (st.tLive = true → st.round ≥ 1)
/-- `Future == \A r \in Rounds : r > round => mark[r] = 0 /\ seal[r] = 0` -/
def Future (c : Cfg) (st : State) : Prop := ∀ r, Rounds c r → r > st.round → st.mark r = 0 ∧ st.seals r = 0
/-- `MarkLeSeq == round >= 1 => mark[round] <= seq` -/
def MarkLeSeq (st : State) : Prop := st.round ≥ 1 → st.mark st.round ≤ st.seq
/-- `SealedIdle == (round >= 1 /\ ~tLive) => seal[round] = seq` -/
def SealedIdle (st : State) : Prop := st.round ≥ 1 ∧ st.tLive = false → st.seals st.round = st.seq
def Shape (c : Cfg) (st : State) : Prop := TypeOK c st ∧ Future c st ∧ MarkLeSeq st ∧ SealedIdle st

/-- `Past == \A r \in Rounds : r < round => mark[r] = seal[r]` -/
def Past (c : Cfg) (st : State) : Prop := ∀ r, Rounds c r → r < st.round → st.mark r = st.seals r
/-- `Bound == round >= 1 => seq - mark[round] <= K` -/
def Bound (c : Cfg) (st : State) : Prop := st.round ≥ 1 → (st.seq : Int) - st.mark st.round ≤ c.K
def InvU (c : Cfg) (st : State) : Prop := Shape c st ∧ Past c st ∧ Bound c st

theorem InitShape (c : Cfg) (st : State) (h : Init c st) : Shape c st := by
  obtain ⟨hr, ht, hs, -, -, hm, hl, -, -, -⟩ := h
  refine ⟨⟨by omega, fun h' => by rw [ht] at h'; cases h'⟩, ?_, ?_, ?_⟩
  · intro r hr' _; exact ⟨hm r hr', hl r hr'⟩
  · intro h'; omega
  · intro h'; omega

/-- Shape holds under every mutation. -/
theorem NextShape (c : Cfg) (st st' : State) (hi : Shape c st) (hn : Next c st st') : Shape c st' := by
  obtain ⟨⟨hmax, hlive⟩, hF, hM, hS⟩ := hi
  rcases hn with h | h | h | h | h | h | h | h | h | ⟨r, w, hr, hw, h⟩
  · -- GrantT
    obtain ⟨ht, hlt, hcov, hr', ht', hs', -, -, hm', hl', -⟩ := h
    refine ⟨⟨by omega, fun _ => by omega⟩, ?_, ?_, ?_⟩
    · intro r hr hgt; rw [hm', hl']; exact hF r hr (by omega)
    · intro _; rw [hm', hr', hs']
      have := hF (st.round + 1) ⟨by omega, by omega⟩ (by omega)
      omega
    · intro ⟨_, h2⟩; rw [ht'] at h2; cases h2
  · -- Admit
    obtain ⟨ht, -, -, hs', -, hr', ht', -, -, hm', hl', -, -⟩ := h
    refine ⟨⟨by omega, fun _ => by rw [hr']; exact hlive ht⟩, ?_, ?_, ?_⟩
    · intro r hr hgt; rw [hm', hl']; exact hF r hr (by omega)
    · intro _; rw [hm', hr', hs']; have := hM (by omega); omega
    · intro ⟨_, h2⟩; rw [ht', ht] at h2; cases h2
  · -- Refuse
    obtain ⟨ht, -, -, -, -, hr', ht', hs', -, -, hm', hl', -⟩ := h
    refine ⟨⟨by omega, fun _ => by rw [hr']; exact hlive ht⟩, ?_, ?_, ?_⟩
    · intro r hr hgt; rw [hm', hl']; exact hF r hr (by omega)
    · intro _; rw [hm', hr', hs']; exact hM (by omega)
    · intro ⟨_, h2⟩; rw [ht', ht] at h2; cases h2
  · -- EndRoundT
    obtain ⟨ht, ht', hl', hr', hs', -, -, hm', -⟩ := h
    have h1 := hlive ht
    refine ⟨⟨by omega, fun h2 => by rw [ht'] at h2; cases h2⟩, ?_, ?_, ?_⟩
    · intro r hr hgt; rw [hm', hl', hr'] at *; rw [upd_other _ _ _ _ (by omega)]
      exact hF r hr (by rw [hr'] at hgt; exact hgt)
    · intro _; rw [hm', hr', hs']; exact hM h1
    · intro _; rw [hl', hr', hs', upd_same]
  · -- CorrBeat
    obtain ⟨-, -, hr', ht', hs', hm', hl', -⟩ := h
    exact ⟨⟨by omega, fun h2 => by rw [hr']; exact hlive (ht' ▸ h2)⟩,
      fun r hr hgt => by rw [hm', hl']; exact hF r hr (by omega),
      fun h2 => by rw [hm', hr', hs']; exact hM (by omega),
      fun ⟨h2, h3⟩ => by rw [hl', hr', hs']; exact hS ⟨by omega, by rw [← ht']; exact h3⟩⟩
  · -- GrantO
    obtain ⟨-, -, -, hr', ht', hs', hm', hl', -⟩ := h
    exact ⟨⟨by omega, fun h2 => by rw [hr']; exact hlive (ht' ▸ h2)⟩,
      fun r hr hgt => by rw [hm', hl']; exact hF r hr (by omega),
      fun h2 => by rw [hm', hr', hs']; exact hM (by omega),
      fun ⟨h2, h3⟩ => by rw [hl', hr', hs']; exact hS ⟨by omega, by rw [← ht']; exact h3⟩⟩
  · -- EndO
    obtain ⟨-, -, -, hr', ht', hs', hm', hl', -⟩ := h
    exact ⟨⟨by omega, fun h2 => by rw [hr']; exact hlive (ht' ▸ h2)⟩,
      fun r hr hgt => by rw [hm', hl']; exact hF r hr (by omega),
      fun h2 => by rw [hm', hr', hs']; exact hM (by omega),
      fun ⟨h2, h3⟩ => by rw [hl', hr', hs']; exact hS ⟨by omega, by rw [← ht']; exact h3⟩⟩
  · -- StaleO
    obtain ⟨-, -, -, hr', ht', hs', hm', hl', -⟩ := h
    exact ⟨⟨by omega, fun h2 => by rw [hr']; exact hlive (ht' ▸ h2)⟩,
      fun r hr hgt => by rw [hm', hl']; exact hF r hr (by omega),
      fun h2 => by rw [hm', hr', hs']; exact hM (by omega),
      fun ⟨h2, h3⟩ => by rw [hl', hr', hs']; exact hS ⟨by omega, by rw [← ht']; exact h3⟩⟩
  · -- StaleC
    obtain ⟨-, -, -, hr', ht', hs', hm', hl', -⟩ := h
    exact ⟨⟨by omega, fun h2 => by rw [hr']; exact hlive (ht' ▸ h2)⟩,
      fun r hr hgt => by rw [hm', hl']; exact hF r hr (by omega),
      fun h2 => by rw [hm', hr', hs']; exact hM (by omega),
      fun ⟨h2, h3⟩ => by rw [hl', hr', hs']; exact hS ⟨by omega, by rw [← ht']; exact h3⟩⟩
  · -- Heartbeat(r, w): the mark at r rises to at most the sequence or the seal
    obtain ⟨-, hle, hge, hwm, hwu, hm', -, hr', ht', hs', -, hl', -⟩ := h
    refine ⟨⟨by omega, fun h2 => by rw [hr']; exact hlive (ht' ▸ h2)⟩, ?_, ?_, ?_⟩
    · intro r' hr' hgt
      rw [hm', hl']
      rw [upd_other _ _ _ _ (by omega)]
      exact hF r' hr' (by omega)
    · intro _
      rw [hm', hr', hs']
      by_cases hrr : st.round = r
      · rw [hrr, upd_same]; rw [if_pos (by omega)] at hwu; exact hwu
      · rw [upd_other _ _ _ _ hrr]; exact hM (by omega)
    · intro ⟨h2, h3⟩; rw [hl', hr', hs']; exact hS ⟨by omega, by rw [← ht']; exact h3⟩

theorem InitInvU (c : Cfg) (st : State) (h : Init c st) : InvU c st := by
  refine ⟨InitShape c st h, ?_, ?_⟩
  · intro r _ hlt; have := h.1; omega
  · intro h'; have := h.1; omega

theorem NextInvU (c : Cfg) (h1 : c.m ≠ .M_MARK) (h2 : c.m ≠ .M_ROUNDS) (h3 : c.m ≠ .M_NOCOUPLE)
    (st st' : State) (hi : InvU c st) (hn : Next c st st') : InvU c st' := by
  have hS' := NextShape c st st' hi.1 hn
  obtain ⟨⟨⟨hmax, hlive⟩, hF, hM, hSi⟩, hP, hB⟩ := hi
  refine ⟨hS', ?_, ?_⟩
  -- Past'
  · rcases hn with h | h | h | h | h | h | h | h | h | ⟨r, w, hr, hw, h⟩
    · -- GrantT: the finished round was read to its seal, and a mark never passes a seal
      obtain ⟨ht, hlt, hcov, hr', ht', hs', -, -, hm', hl', -⟩ := h
      intro r hr hlt'
      obtain ⟨hr1, hr2⟩ := hr
      rw [hm', hl']
      by_cases hrr : r = st.round
      · have hround : st.round ≥ 1 := by omega
        have hcov' : st.mark st.round ≥ st.seals st.round := by
          by_cases h0 : st.round = 0 ∨ c.m = .M_ROUNDS
          · rcases h0 with h0 | h0
            · omega
            · exact absurd h0 h2
          · rw [if_neg h0] at hcov; exact hcov
        have h3 := hSi ⟨hround, ht⟩
        have h4 := hM hround
        rw [hrr]; omega
      · exact hP r ⟨hr1, hr2⟩ (by omega)
    · obtain ⟨-, -, -, -, -, hr', -, -, -, hm', hl', -, -⟩ := h
      intro r hr hlt; rw [hm', hl']; exact hP r hr (by omega)
    · obtain ⟨-, -, -, -, -, hr', -, -, -, -, hm', hl', -⟩ := h
      intro r hr hlt; rw [hm', hl']; exact hP r hr (by omega)
    · obtain ⟨-, -, hl', hr', -, -, -, hm', -⟩ := h
      intro r hr hlt; rw [hm', hl', hr'] at *; rw [upd_other _ _ _ _ (by omega)]; exact hP r hr (by omega)
    · obtain ⟨-, -, hr', -, -, hm', hl', -⟩ := h
      intro r hr hlt; rw [hm', hl']; exact hP r hr (by omega)
    · obtain ⟨-, -, -, hr', -, -, hm', hl', -⟩ := h
      intro r hr hlt; rw [hm', hl']; exact hP r hr (by omega)
    · obtain ⟨-, -, -, hr', -, -, hm', hl', -⟩ := h
      intro r hr hlt; rw [hm', hl']; exact hP r hr (by omega)
    · obtain ⟨-, -, -, hr', -, -, hm', hl', -⟩ := h
      intro r hr hlt; rw [hm', hl']; exact hP r hr (by omega)
    · obtain ⟨-, -, -, hr', -, -, hm', hl', -⟩ := h
      intro r hr hlt; rw [hm', hl']; exact hP r hr (by omega)
    · -- Heartbeat on a past round: the mark cannot pass the seal it already equals
      obtain ⟨-, hle, hge, hwm, hwu, hm', -, hr', -, -, -, hl', -⟩ := h
      intro r' hr' hlt
      rw [hm', hl']
      by_cases hrr : r' = r
      · subst hrr
        rw [upd_same]
        rw [if_neg (by omega)] at hwu
        have := hP r' hr' (by omega)
        omega
      · rw [upd_other _ _ _ _ hrr]; exact hP r' hr' (by omega)
  -- Bound'
  · rcases hn with h | h | h | h | h | h | h | h | h | ⟨r, w, hr, hw, h⟩
    · obtain ⟨-, hlt, -, hr', -, hs', -, -, hm', -, -⟩ := h
      intro _; rw [hm', hr', hs']
      have := hF (st.round + 1) ⟨by omega, by omega⟩ (by omega)
      omega
    · -- Admit: the admit needs LiveO, whose backlog is below K
      obtain ⟨ht, -, ⟨hal, -⟩, hs', -, hr', -, -, -, hm', -, -, -⟩ := h
      intro _
      rw [hm', hr', hs']
      have hlo : LiveO c st := by
        rcases hal with hal | hal
        · exact absurd h3 hal
        · exact hal
      obtain ⟨-, -, hk⟩ := hlo
      have hround : st.round ≥ 1 := hlive ht
      have hcond : ¬ (c.m = .M_MARK ∨ st.round = 0) := fun h => h.elim (fun h => h1 h) (fun h => by omega)
      rw [if_neg hcond] at hk
      omega
    · obtain ⟨-, -, -, -, -, hr', -, hs', -, -, hm', -, -⟩ := h
      intro _; rw [hm', hr', hs']; exact hB (by omega)
    · obtain ⟨-, -, -, hr', hs', -, -, hm', -⟩ := h
      intro _; rw [hm', hr', hs']; exact hB (by omega)
    · obtain ⟨-, -, hr', -, hs', hm', -, -⟩ := h
      intro _; rw [hm', hr', hs']; exact hB (by omega)
    · obtain ⟨-, -, -, hr', -, hs', hm', -, -⟩ := h
      intro _; rw [hm', hr', hs']; exact hB (by omega)
    · obtain ⟨-, -, -, hr', -, hs', hm', -, -⟩ := h
      intro _; rw [hm', hr', hs']; exact hB (by omega)
    · obtain ⟨-, -, -, hr', -, hs', hm', -, -⟩ := h
      intro _; rw [hm', hr', hs']; exact hB (by omega)
    · obtain ⟨-, -, -, hr', -, hs', hm', -, -⟩ := h
      intro _; rw [hm', hr', hs']; exact hB (by omega)
    · -- Heartbeat: a mark only rises
      obtain ⟨-, hle, hge, hwm, hwu, hm', -, hr', -, hs', -, -, -⟩ := h
      intro _
      rw [hm', hr', hs']
      by_cases hrr : st.round = r
      · rw [hrr, upd_same]; have := hB (by omega); rw [hrr] at this; omega
      · rw [upd_other _ _ _ _ hrr]; exact hB (by omega)

/-- `InvUBounded`: the invariant gives the property. PriorUnread is zero: round 1's mark is its seal. -/
theorem InvUBounded (c : Cfg) (st : State) (h : InvU c st) : UnreadBounded c st := by
  obtain ⟨⟨⟨hmax, -⟩, -, hM, -⟩, hP, hB⟩ := h
  unfold UnreadBounded Unread PriorUnread
  by_cases h0 : st.round = 0
  · rw [if_pos h0, if_neg (by omega)]; omega
  · rw [if_neg h0]
    have hb := hB (by omega)
    by_cases h2 : st.round = 2
    · rw [if_pos h2]
      have := hP 1 ⟨by omega, by omega⟩ (by omega)
      omega
    · rw [if_neg h2]; omega

/-- `THEOREM UnreadBoundedAlways == ASSUME Mut \notin {"M_MARK", "M_ROUNDS", "M_NOCOUPLE"} PROVE Spec => []UnreadBounded`,
for every K, R and MaxRound. -/
theorem UnreadBoundedAlways (c : Cfg) (h1 : c.m ≠ .M_MARK) (h2 : c.m ≠ .M_ROUNDS) (h3 : c.m ≠ .M_NOCOUPLE) :
    ∀ st, Reachable (Init c) (Next c) st → UnreadBounded c st :=
  invariant (InvU c) (UnreadBounded c) (InitInvU c) (NextInvU c h1 h2 h3) (InvUBounded c)

/-! ## The two flags -/

theorem NextNoAdmit (c : Cfg) (hm : c.m ≠ .M_NOCOUPLE) (st st' : State)
    (hd : NoAdmitWithoutLiveObserver st) (hn : Next c st st') : NoAdmitWithoutLiveObserver st' := by
  rcases hn with ⟨-, -, -, -, -, -, -, -, -, -, hA, -⟩ | ⟨-, -, ⟨hal, -⟩, -, hA, -⟩ |
    ⟨-, -, -, -, -, -, -, -, -, -, -, -, hA⟩ | ⟨-, -, -, -, -, -, -, -, hA, -⟩ | ⟨-, -, -, -, -, -, -, hA, -⟩ |
    ⟨-, -, -, -, -, -, -, -, hA, -⟩ | ⟨-, -, -, -, -, -, -, -, hA, -⟩ | ⟨-, -, -, -, -, -, -, -, hA, -⟩ |
    ⟨-, -, -, -, -, -, -, -, hA, -⟩ | ⟨r, w, -, -, -, -, -, -, -, -, -, -, -, -, -, -, hA, -⟩
  all_goals try exact fun h' => hd (hA.mp h')
  -- Admit: coupled, so LiveO held
  intro h'
  rcases hA.mp h' with h' | h'
  · exact hd h'
  · rcases hal with hal | hal
    · exact absurd hm hal
    · exact h' hal

/-- `THEOREM NoAdmitWithoutLiveObserverAlways == ASSUME Mut # "M_NOCOUPLE" PROVE Spec => []NoAdmitWithoutLiveObserver` -/
theorem NoAdmitWithoutLiveObserverAlways (c : Cfg) (hm : c.m ≠ .M_NOCOUPLE) :
    ∀ st, Reachable (Init c) (Next c) st → NoAdmitWithoutLiveObserver st :=
  invariant NoAdmitWithoutLiveObserver NoAdmitWithoutLiveObserver (fun _ h => h.2.2.2.2.2.2.2.1)
    (NextNoAdmit c hm) (fun _ h => h)

theorem NextCorr (c : Cfg) (hm : c.m ≠ .M_CORR) (st st' : State)
    (hd : CorrelatorNeverGates st) (hn : Next c st st') : CorrelatorNeverGates st' := by
  rcases hn with ⟨-, -, -, -, -, -, -, -, -, -, -, hR, -⟩ | ⟨-, -, -, -, -, -, -, -, -, -, -, hR, -⟩ |
    ⟨-, -, hna, -, hR, -⟩ | ⟨-, -, -, -, -, -, -, -, -, hR, -⟩ | ⟨-, -, -, -, -, -, -, -, hR, -⟩ |
    ⟨-, -, -, -, -, -, -, -, -, hR, -⟩ | ⟨-, -, -, -, -, -, -, -, -, hR, -⟩ | ⟨-, -, -, -, -, -, -, -, -, hR, -⟩ |
    ⟨-, -, -, -, -, -, -, -, -, hR, -⟩ | ⟨r, w, -, -, -, -, -, -, -, -, -, -, -, -, -, -, -, hR, -⟩
  all_goals try exact fun h' => hd (hR.mp h')
  -- Refuse: not Allowed, and not coupled to the correlator, so LiveO failed
  intro h'
  rcases hR.mp h' with h' | ⟨hlo, -⟩
  · exact hd h'
  · exact hna ⟨Or.inr hlo, Or.inl hm⟩

/-- `THEOREM CorrelatorNeverGatesAlways == ASSUME Mut # "M_CORR" PROVE Spec => []CorrelatorNeverGates` -/
theorem CorrelatorNeverGatesAlways (c : Cfg) (hm : c.m ≠ .M_CORR) :
    ∀ st, Reachable (Init c) (Next c) st → CorrelatorNeverGates st :=
  invariant CorrelatorNeverGates CorrelatorNeverGates (fun _ h => h.2.2.2.2.2.2.2.2.1)
    (NextCorr c hm) (fun _ h => h)

/-- `THEOREM SafeAlways == ASSUME Mut = "none" PROVE Spec => []Safe`, for every K, R and MaxRound. -/
theorem SafeAlways (K R MaxRound : Nat) :
    ∀ st, Reachable (Init ⟨.none, K, R, MaxRound⟩) (Next ⟨.none, K, R, MaxRound⟩) st →
      Safe ⟨.none, K, R, MaxRound⟩ st :=
  fun st h => ⟨NoAdmitWithoutLiveObserverAlways _ (by simp) st h,
    UnreadBoundedAlways _ (by simp) (by simp) (by simp) st h,
    CorrelatorNeverGatesAlways _ (by simp) st h⟩

/-! ## Why the mutations must fail (the counterexamples are TLC's) -/

/-- `MutNoCoupleAllowsAll`: uncoupled, every admit is allowed whatever the Observer's state. -/
theorem MutNoCoupleAllowsAll (K R MaxRound : Nat) (st : State) : Allowed ⟨.M_NOCOUPLE, K, R, MaxRound⟩ st :=
  ⟨Or.inl (fun h => h rfl), Or.inl (by simp)⟩

/-- `MutMarkIgnoresBacklog`: under M_MARK a fresh Observer with a lease is live at any backlog. -/
theorem MutMarkIgnoresBacklog (K R MaxRound : Nat) (st : State) (ho : st.oLease = true) (hf : st.fresh.o = true) :
    LiveO ⟨.M_MARK, K, R, MaxRound⟩ st :=
  ⟨ho, hf, by rw [if_pos (Or.inl rfl)]; trivial⟩

/-- `MutRoundsGrantsUncovered`: under M_ROUNDS the grant does not wait for the previous round to be read. -/
theorem MutRoundsGrantsUncovered (K R MaxRound : Nat) (st : State) :
    (if st.round = 0 ∨ (⟨.M_ROUNDS, K, R, MaxRound⟩ : Cfg).m = .M_ROUNDS then True
     else st.mark st.round ≥ st.seals st.round) := by
  rw [if_pos (Or.inr rfl)]; trivial

/-- `MutCorrGates`: under M_CORR a stale correlator refuses even with a live cell Observer. -/
theorem MutCorrGates (K R MaxRound : Nat) (st : State) (hc : st.fresh.c = false) :
    ¬ Allowed ⟨.M_CORR, K, R, MaxRound⟩ st := by
  rintro ⟨-, h⟩
  rcases h with h | h
  · exact h rfl
  · unfold LiveC at h; rw [hc] at h; cases h

#print axioms UnreadBoundedAlways
#print axioms NoAdmitWithoutLiveObserverAlways
#print axioms CorrelatorNeverGatesAlways
#print axioms SafeAlways

end Topak.Spec.Coupling
