import TopakSpec.Prelude
/-!
# Lease_A1.tla in Lean

ADR-0031, the lease schema, as amended by A1: renewal keeps the rung. `spec/Lease_A1.tla` re-encoded;
`spec/Lease_A1_proof.tla`'s theorems proved by induction on reachable states. The constants `MaxEpoch` and
`MaxFence` are parameters that only cut the state space, as the TLAPS proof notes; the epoch and fence are
unbounded naturals. `TypeOK` has no counterpart: the types carry it, and `Rungs == 0..3` is the side
condition `r ≤ 3` on a grant or renewal.

Encoding notes beyond the prelude's: `live`, only ever TRUE or FALSE, is `Bool`; `role`, which is a role or
"none", is `Option Role`; `staleAdmitted` is a `Prop`. The TLA+ action `Act(p)` is `ActStep`.

Mutations: `M_RENEW`, `M_FENCE`, `M_RUNG`, `M_ROLE`, `M_REVOKE`, `M_LOWER`. Each theorem takes only the
mutations that break it. `Rung0NeverContained` needs no induction: it holds of every state once `Contained`
reads the rung.
-/

namespace Topak.Spec.Lease_A1
open Topak.Spec PSet

inductive Mut | none | M_RENEW | M_FENCE | M_RUNG | M_ROLE | M_REVOKE | M_LOWER
  deriving DecidableEq

structure Cfg where
  m : Mut
  MaxEpoch : Nat
  MaxFence : Nat

inductive Principal | p1 | p2
  deriving DecidableEq
/-- `Acts == {"Read", "Emit"}` -/
inductive Act | Read | Emit
  deriving DecidableEq
/-- `Roles == {"author", "voter"}`; the lease's `role` may also be "none". -/
inductive Role | author | voter
  deriving DecidableEq

/-- `[live, alphabet, rung, role, epoch, fence]` -/
structure LeaseRec where
  live : Bool
  alphabet : PSet Act
  rung : Nat
  role : Option Role
  epoch : Nat
  fence : Nat

/-- `NoLease == [live |-> FALSE, alphabet |-> {}, rung |-> 0, role |-> "none", epoch |-> 0, fence |-> 0]` -/
def NoLease : LeaseRec := ⟨false, ∅, 0, none, 0, 0⟩

/-- `[principal |-> p, act |-> a, atEpoch |-> epoch, leaseEpoch |-> lease[p].epoch]` -/
structure ActRec where
  principal : Principal
  act : Act
  atEpoch : Nat
  leaseEpoch : Nat

/-- `VARIABLES lease, prev, epoch, fence, acted, staleAdmitted, revoked` -/
structure State where
  lease : Principal → LeaseRec
  prev : Principal → LeaseRec
  epoch : Nat
  fence : Nat
  acted : PSet ActRec
  staleAdmitted : Prop
  revoked : PSet Principal

def Init (st : State) : Prop :=
  (st.lease = fun _ => NoLease) ∧ (st.prev = fun _ => NoLease) ∧ st.epoch = 0 ∧ st.fence = 0 ∧
  st.acted = ∅ ∧ ¬ st.staleAdmitted ∧ st.revoked = ∅

/-- `Narrows(new, old) == new.alphabet ⊆ old.alphabet` -/
def Narrows (new old : LeaseRec) : Prop := new.alphabet ⊆ old.alphabet
/-- `LowerOrSame(new, old) == new.rung <= old.rung` -/
def LowerOrSame (new old : LeaseRec) : Prop := new.rung ≤ old.rung
/-- `Refines(new, old) == Narrows(new, old) /\ new.rung = old.rung /\ new.role = old.role` -/
def Refines (new old : LeaseRec) : Prop := Narrows new old ∧ new.rung = old.rung ∧ new.role = old.role

/-- ```
RenewalAllowed(new, old) ==
  CASE Mut = "M_RENEW" -> TRUE
    [] Mut = "M_ROLE"  -> Narrows(new, old) /\ new.rung = old.rung
    [] Mut = "M_LOWER" -> Narrows(new, old) /\ LowerOrSame(new, old) /\ new.role = old.role
    [] OTHER           -> Refines(new, old)
``` -/
def RenewalAllowed (m : Mut) (new old : LeaseRec) : Prop :=
  match m with
  | .M_RENEW => True
  | .M_ROLE => Narrows new old ∧ new.rung = old.rung
  | .M_LOWER => Narrows new old ∧ LowerOrSame new old ∧ new.role = old.role
  | _ => Refines new old

/-- The frame of the variables an action leaves alone. -/
def Unch (st st' : State) (epoch fence acted stale revoked : Bool) : Prop :=
  (epoch = true → st'.epoch = st.epoch) ∧ (fence = true → st'.fence = st.fence) ∧
  (acted = true → st'.acted = st.acted) ∧ (stale = true → (st'.staleAdmitted ↔ st.staleAdmitted)) ∧
  (revoked = true → st'.revoked = st.revoked)

/-- ```
Grant(p) == /\ ~lease[p].live
            /\ Mut = "M_REVOKE" \/ p ∉ revoked
            /\ fence < MaxFence
            /\ ∃ a ∈ SUBSET Acts, r ∈ Rungs, ro ∈ Roles :
                 lease' = [lease EXCEPT ![p] = [live |-> TRUE, alphabet |-> a, rung |-> r, role |-> ro,
                                                epoch |-> epoch, fence |-> fence + 1]]
            /\ prev' = [prev EXCEPT ![p] = lease[p]]
            /\ fence' = fence + 1
            /\ UNCHANGED <<epoch, acted, staleAdmitted, revoked>>
``` -/
def Grant (c : Cfg) (p : Principal) (st st' : State) : Prop :=
  (st.lease p).live = false ∧
  (c.m = .M_REVOKE ∨ ¬ p ∈ st.revoked) ∧
  st.fence < c.MaxFence ∧
  (∃ (a : PSet Act) (r : Nat) (ro : Role), r ≤ 3 ∧
    st'.lease = upd st.lease p ⟨true, a, r, some ro, st.epoch, st.fence + 1⟩) ∧
  st'.prev = upd st.prev p (st.lease p) ∧
  st'.fence = st.fence + 1 ∧
  Unch st st' true false true true true

/-- ```
Renew(p) == /\ lease[p].live /\ lease[p].epoch = epoch /\ fence < MaxFence
            /\ ∃ a ∈ SUBSET Acts, r ∈ Rungs, ro ∈ Roles :
                 LET new == [live |-> TRUE, alphabet |-> a, rung |-> r, role |-> ro, epoch |-> epoch, fence |-> fence + 1]
                 IN  RenewalAllowed(new, lease[p]) /\ lease' = [lease EXCEPT ![p] = new]
            /\ prev' = [prev EXCEPT ![p] = lease[p]]
            /\ fence' = fence + 1
            /\ UNCHANGED <<epoch, acted, staleAdmitted, revoked>>
``` -/
def Renew (c : Cfg) (p : Principal) (st st' : State) : Prop :=
  (st.lease p).live = true ∧ (st.lease p).epoch = st.epoch ∧ st.fence < c.MaxFence ∧
  (∃ (a : PSet Act) (r : Nat) (ro : Role), r ≤ 3 ∧
    RenewalAllowed c.m ⟨true, a, r, some ro, st.epoch, st.fence + 1⟩ (st.lease p) ∧
    st'.lease = upd st.lease p ⟨true, a, r, some ro, st.epoch, st.fence + 1⟩) ∧
  st'.prev = upd st.prev p (st.lease p) ∧
  st'.fence = st.fence + 1 ∧
  Unch st st' true false true true true

/-- `Revoke == epoch < MaxEpoch /\ epoch' = epoch + 1 /\ UNCHANGED <<lease, prev, fence, acted, staleAdmitted, revoked>>` -/
def Revoke (c : Cfg) (st st' : State) : Prop :=
  st.epoch < c.MaxEpoch ∧ st'.epoch = st.epoch + 1 ∧
  st'.lease = st.lease ∧ st'.prev = st.prev ∧ Unch st st' false true true true true

/-- `EpochOK(p) == IF Mut = "M_FENCE" THEN TRUE ELSE lease[p].epoch = epoch` -/
def EpochOK (c : Cfg) (p : Principal) (st : State) : Prop :=
  if c.m = .M_FENCE then True else (st.lease p).epoch = st.epoch

/-- ```
Act(p) == /\ lease[p].live /\ EpochOK(p)
          /\ ∃ a ∈ lease[p].alphabet :
               acted' = acted ∪ {[principal |-> p, act |-> a, atEpoch |-> epoch, leaseEpoch |-> lease[p].epoch]}
          /\ staleAdmitted' = (staleAdmitted \/ lease[p].epoch # epoch)
          /\ UNCHANGED <<lease, prev, epoch, fence, revoked>>
``` -/
def ActStep (c : Cfg) (p : Principal) (st st' : State) : Prop :=
  (st.lease p).live = true ∧ EpochOK c p st ∧
  (∃ a, a ∈ (st.lease p).alphabet ∧ st'.acted = st.acted ∪ {⟨p, a, st.epoch, (st.lease p).epoch⟩}) ∧
  (st'.staleAdmitted ↔ (st.staleAdmitted ∨ (st.lease p).epoch ≠ st.epoch)) ∧
  st'.lease = st.lease ∧ st'.prev = st.prev ∧ Unch st st' true true false false true

/-- ```
RevokeLease(p) == /\ p ∉ revoked /\ revoked' = revoked ∪ {p}
                  /\ lease' = [lease EXCEPT ![p] = NoLease] /\ prev' = [prev EXCEPT ![p] = NoLease]
                  /\ UNCHANGED <<epoch, fence, acted, staleAdmitted>>
``` -/
def RevokeLease (p : Principal) (st st' : State) : Prop :=
  ¬ p ∈ st.revoked ∧ st'.revoked = st.revoked ∪ {p} ∧
  st'.lease = upd st.lease p NoLease ∧ st'.prev = upd st.prev p NoLease ∧
  Unch st st' true true true true false

/-- `EndRound(p) == lease[p].live /\ lease' = [lease EXCEPT ![p] = NoLease] /\ prev' = [prev EXCEPT ![p] = NoLease] /\ UNCHANGED <<...>>` -/
def EndRound (p : Principal) (st st' : State) : Prop :=
  (st.lease p).live = true ∧
  st'.lease = upd st.lease p NoLease ∧ st'.prev = upd st.prev p NoLease ∧
  Unch st st' true true true true true

def Next (c : Cfg) (st st' : State) : Prop :=
  Revoke c st st' ∨ ∃ p, Grant c p st st' ∨ Renew c p st st' ∨ ActStep c p st st' ∨ EndRound p st st' ∨ RevokeLease p st st'

/-- §3. `Contained(p) == lease[p].live /\ IF Mut = "M_RUNG" THEN TRUE ELSE lease[p].rung >= 1` -/
def Contained (c : Cfg) (p : Principal) (st : State) : Prop :=
  (st.lease p).live = true ∧ (if c.m = .M_RUNG then True else (st.lease p).rung ≥ 1)

/-! ## The four properties -/

/-- §4. `∀ p : (lease[p].live /\ prev[p].live /\ lease[p].epoch = prev[p].epoch) => Refines(lease[p], prev[p])` -/
def LeaseAuthorityMonotone (st : State) : Prop :=
  ∀ p, ((st.lease p).live = true ∧ (st.prev p).live = true ∧ (st.lease p).epoch = (st.prev p).epoch) →
    Refines (st.lease p) (st.prev p)

/-- §5. `~staleAdmitted /\ ∀ r ∈ acted : r.leaseEpoch = r.atEpoch` -/
def NoActionUnderFencedEpoch (st : State) : Prop :=
  ¬ st.staleAdmitted ∧ ∀ r, r ∈ st.acted → r.leaseEpoch = r.atEpoch

/-- §3. `∀ p : (lease[p].live /\ lease[p].rung = 0) => ~Contained(p)` -/
def Rung0NeverContained (c : Cfg) (st : State) : Prop :=
  ∀ p, ((st.lease p).live = true ∧ (st.lease p).rung = 0) → ¬ Contained c p st

/-- §5 R3. `∀ p ∈ revoked : ~lease[p].live` -/
def RevokedStaysStopped (st : State) : Prop := ∀ p, p ∈ st.revoked → (st.lease p).live = false

def Safe (c : Cfg) (st : State) : Prop :=
  LeaseAuthorityMonotone st ∧ NoActionUnderFencedEpoch st ∧ Rung0NeverContained c st ∧ RevokedStaysStopped st

/-! ## Proofs -/

/-- `RenewRefines`: under the specified rule a renewal refines its predecessor. -/
theorem RenewRefines (m : Mut) (h1 : m ≠ .M_RENEW) (h2 : m ≠ .M_ROLE) (h3 : m ≠ .M_LOWER)
    (new old : LeaseRec) (h : RenewalAllowed m new old) : Refines new old := by
  cases m <;> first | exact h | exact absurd rfl h1 | exact absurd rfl h2 | exact absurd rfl h3

theorem InitMonotone (st : State) (h : Init st) : LeaseAuthorityMonotone st := by
  rintro p ⟨hl, -, -⟩; rw [h.1] at hl; cases hl

theorem NextMonotone (c : Cfg) (h1 : c.m ≠ .M_RENEW) (h2 : c.m ≠ .M_ROLE) (h3 : c.m ≠ .M_LOWER)
    (st st' : State) (hi : LeaseAuthorityMonotone st) (hn : Next c st st') : LeaseAuthorityMonotone st' := by
  rcases hn with ⟨-, -, hl, hp, -⟩ | ⟨p, h | h | h | h | h⟩
  · intro q hq; rw [hl, hp] at hq ⊢; exact hi q hq
  · -- Grant(p): p's predecessor is not live; others unchanged
    obtain ⟨hnl, -, -, ⟨a, r, ro, -, hl⟩, hp, -⟩ := h
    intro q hq
    rw [hl, hp] at hq ⊢
    by_cases hqp : q = p
    · subst hqp; rw [upd_same, upd_same] at hq; rw [hnl] at hq; exact absurd hq.2.1 (by decide)
    · rw [upd_other _ _ _ _ hqp, upd_other _ _ _ _ hqp] at hq ⊢; exact hi q hq
  · -- Renew(p): the new lease refines the old
    obtain ⟨-, -, -, ⟨a, r, ro, -, hra, hl⟩, hp, -⟩ := h
    intro q hq
    rw [hl, hp] at hq ⊢
    by_cases hqp : q = p
    · subst hqp; rw [upd_same, upd_same]; exact RenewRefines c.m h1 h2 h3 _ _ hra
    · rw [upd_other _ _ _ _ hqp, upd_other _ _ _ _ hqp] at hq ⊢; exact hi q hq
  · obtain ⟨-, -, -, -, hl, hp, -⟩ := h
    intro q hq; rw [hl, hp] at hq ⊢; exact hi q hq
  · obtain ⟨-, hl, hp, -⟩ := h
    intro q hq; rw [hl, hp] at hq ⊢
    by_cases hqp : q = p
    · subst hqp; rw [upd_same] at hq; exact absurd hq.1 (by decide)
    · rw [upd_other _ _ _ _ hqp, upd_other _ _ _ _ hqp] at hq ⊢; exact hi q hq
  · obtain ⟨-, -, hl, hp, -⟩ := h
    intro q hq; rw [hl, hp] at hq ⊢
    by_cases hqp : q = p
    · subst hqp; rw [upd_same] at hq; exact absurd hq.1 (by decide)
    · rw [upd_other _ _ _ _ hqp, upd_other _ _ _ _ hqp] at hq ⊢; exact hi q hq

/-- `THEOREM LeaseAuthorityMonotoneAlways == ASSUME Mut \notin {"M_RENEW", "M_ROLE", "M_LOWER"} PROVE Spec => []LeaseAuthorityMonotone` -/
theorem LeaseAuthorityMonotoneAlways (c : Cfg) (h1 : c.m ≠ .M_RENEW) (h2 : c.m ≠ .M_ROLE) (h3 : c.m ≠ .M_LOWER) :
    ∀ st, Reachable Init (Next c) st → LeaseAuthorityMonotone st :=
  invariant LeaseAuthorityMonotone LeaseAuthorityMonotone InitMonotone (NextMonotone c h1 h2 h3) (fun _ h => h)

theorem InitFenced (st : State) (h : Init st) : NoActionUnderFencedEpoch st :=
  ⟨h.2.2.2.2.2.1, fun r hr => by rw [h.2.2.2.2.1] at hr; exact hr.elim⟩

theorem NextFenced (c : Cfg) (hm : c.m ≠ .M_FENCE) (st st' : State) (hi : NoActionUnderFencedEpoch st)
    (hn : Next c st st') : NoActionUnderFencedEpoch st' := by
  obtain ⟨hs, ha⟩ := hi
  rcases hn with ⟨-, -, -, -, -, -, hac, hst, -⟩ | ⟨p, h | h | h | h | h⟩
  · exact ⟨fun h => hs ((hst rfl).mp h), fun r hr => ha r (by rw [hac rfl] at hr; exact hr)⟩
  · obtain ⟨-, -, -, -, -, -, -, -, hac, hst, -⟩ := h
    exact ⟨fun h => hs ((hst rfl).mp h), fun r hr => ha r (by rw [hac rfl] at hr; exact hr)⟩
  · obtain ⟨-, -, -, -, -, -, -, -, hac, hst, -⟩ := h
    exact ⟨fun h => hs ((hst rfl).mp h), fun r hr => ha r (by rw [hac rfl] at hr; exact hr)⟩
  · -- Act(p): the fence holds, so the lease epoch is the current one
    obtain ⟨-, hok, ⟨a, -, hac⟩, hst, -⟩ := h
    have heq : (st.lease p).epoch = st.epoch := by
      unfold EpochOK at hok; rw [if_neg hm] at hok; exact hok
    refine ⟨?_, ?_⟩
    · intro h; rcases hst.mp h with h | h
      · exact hs h
      · exact h heq
    · intro r hr; rw [hac] at hr
      rcases hr with hr | hr
      · exact ha r hr
      · have hr : r = ⟨p, a, st.epoch, (st.lease p).epoch⟩ := hr
        subst hr; exact heq
  · obtain ⟨-, -, -, -, -, hac, hst, -⟩ := h
    exact ⟨fun h => hs ((hst rfl).mp h), fun r hr => ha r (by rw [hac rfl] at hr; exact hr)⟩
  · obtain ⟨-, -, -, -, -, -, hac, hst, -⟩ := h
    exact ⟨fun h => hs ((hst rfl).mp h), fun r hr => ha r (by rw [hac rfl] at hr; exact hr)⟩

/-- `THEOREM NoActionUnderFencedEpochAlways == ASSUME Mut # "M_FENCE" PROVE Spec => []NoActionUnderFencedEpoch` -/
theorem NoActionUnderFencedEpochAlways (c : Cfg) (hm : c.m ≠ .M_FENCE) :
    ∀ st, Reachable Init (Next c) st → NoActionUnderFencedEpoch st :=
  invariant NoActionUnderFencedEpoch NoActionUnderFencedEpoch InitFenced (NextFenced c hm) (fun _ h => h)

/-- `Rung0Valid`: once `Contained` reads the rung, a rung-0 lease is never Contained, in every state. -/
theorem Rung0Valid (c : Cfg) (hm : c.m ≠ .M_RUNG) (st : State) : Rung0NeverContained c st := by
  rintro p ⟨-, h0⟩ ⟨-, hc⟩
  rw [if_neg hm] at hc; omega

/-- `THEOREM Rung0NeverContainedAlways == ASSUME Mut # "M_RUNG" PROVE Spec => []Rung0NeverContained` -/
theorem Rung0NeverContainedAlways (c : Cfg) (hm : c.m ≠ .M_RUNG) :
    ∀ st, Reachable Init (Next c) st → Rung0NeverContained c st :=
  fun st _ => Rung0Valid c hm st

theorem InitRevoked (st : State) (h : Init st) : RevokedStaysStopped st := by
  intro p hp; rw [h.2.2.2.2.2.2] at hp; exact hp.elim

theorem NextRevoked (c : Cfg) (hm : c.m ≠ .M_REVOKE) (st st' : State) (hi : RevokedStaysStopped st)
    (hn : Next c st st') : RevokedStaysStopped st' := by
  rcases hn with ⟨-, -, hl, -, -, -, -, -, hrv⟩ | ⟨p, h | h | h | h | h⟩
  · intro q hq; rw [hl]; rw [hrv rfl] at hq; exact hi q hq
  · -- Grant(p): p is not revoked, so a revoked q is another principal
    obtain ⟨-, hnr, -, ⟨a, r, ro, -, hl⟩, -, -, -, -, -, -, hrv⟩ := h
    have hnr : ¬ p ∈ st.revoked := by
      rcases hnr with h | h
      · exact absurd h hm
      · exact h
    intro q hq; rw [hrv rfl] at hq; rw [hl]
    have hqp : q ≠ p := fun h => hnr (h ▸ hq)
    rw [upd_other _ _ _ _ hqp]; exact hi q hq
  · -- Renew(p): p is live, so not revoked
    obtain ⟨hlive, -, -, ⟨a, r, ro, -, -, hl⟩, -, -, -, -, -, -, hrv⟩ := h
    intro q hq; rw [hrv rfl] at hq; rw [hl]
    have hqp : q ≠ p := by
      intro h; subst h; have := hi q hq; rw [this] at hlive; cases hlive
    rw [upd_other _ _ _ _ hqp]; exact hi q hq
  · obtain ⟨-, -, -, -, hl, -, -, -, -, -, hrv⟩ := h
    intro q hq; rw [hl]; rw [hrv rfl] at hq; exact hi q hq
  · obtain ⟨-, hl, -, -, -, -, -, hrv⟩ := h
    intro q hq; rw [hrv rfl] at hq; rw [hl]
    by_cases hqp : q = p
    · subst hqp; rw [upd_same]; rfl
    · rw [upd_other _ _ _ _ hqp]; exact hi q hq
  · obtain ⟨-, hrv, hl, -⟩ := h
    intro q hq; rw [hrv] at hq; rw [hl]
    by_cases hqp : q = p
    · subst hqp; rw [upd_same]; rfl
    · rw [upd_other _ _ _ _ hqp]
      rcases hq with hq | hq
      · exact hi q hq
      · exact absurd hq hqp

/-- `THEOREM RevokedStaysStoppedAlways == ASSUME Mut # "M_REVOKE" PROVE Spec => []RevokedStaysStopped` -/
theorem RevokedStaysStoppedAlways (c : Cfg) (hm : c.m ≠ .M_REVOKE) :
    ∀ st, Reachable Init (Next c) st → RevokedStaysStopped st :=
  invariant RevokedStaysStopped RevokedStaysStopped InitRevoked (NextRevoked c hm) (fun _ h => h)

/-- `THEOREM SafeAlways == ASSUME Mut = "none" PROVE Spec => []Safe`, for every MaxEpoch and MaxFence. -/
theorem SafeAlways (MaxEpoch MaxFence : Nat) :
    ∀ st, Reachable Init (Next ⟨.none, MaxEpoch, MaxFence⟩) st → Safe ⟨.none, MaxEpoch, MaxFence⟩ st :=
  fun st h => ⟨LeaseAuthorityMonotoneAlways _ (by simp) (by simp) (by simp) st h,
    NoActionUnderFencedEpochAlways _ (by simp) st h,
    Rung0NeverContainedAlways _ (by simp) st h,
    RevokedStaysStoppedAlways _ (by simp) st h⟩

/-! ## Why the mutations must fail (the counterexamples are TLC's) -/

theorem MutRenewAllowsAll (new old : LeaseRec) : RenewalAllowed .M_RENEW new old := trivial
theorem MutRoleIgnored (new old : LeaseRec) (h : Narrows new old ∧ new.rung = old.rung) : RenewalAllowed .M_ROLE new old := h
theorem MutLowerAccepted (new old : LeaseRec) (h : Narrows new old ∧ LowerOrSame new old ∧ new.role = old.role) :
    RenewalAllowed .M_LOWER new old := h
theorem MutFenceIgnoresEpoch (MaxEpoch MaxFence : Nat) (p : Principal) (st : State) :
    EpochOK ⟨.M_FENCE, MaxEpoch, MaxFence⟩ p st := by unfold EpochOK; rw [if_pos rfl]; trivial
theorem MutRungContainsAll (MaxEpoch MaxFence : Nat) (p : Principal) (st : State) (h : (st.lease p).live = true) :
    Contained ⟨.M_RUNG, MaxEpoch, MaxFence⟩ p st := ⟨h, by rw [if_pos rfl]; trivial⟩
theorem MutRevokeGrantsAgain (MaxEpoch MaxFence : Nat) : (⟨.M_REVOKE, MaxEpoch, MaxFence⟩ : Cfg).m = .M_REVOKE ∨ True := Or.inl rfl

#print axioms LeaseAuthorityMonotoneAlways
#print axioms NoActionUnderFencedEpochAlways
#print axioms Rung0NeverContainedAlways
#print axioms RevokedStaysStoppedAlways
#print axioms SafeAlways

end Topak.Spec.Lease_A1
