import TopakSpec.Prelude
/-!
# Confinement.tla and Confinement_A1.tla in Lean

ADR-0034, attested confinement. `spec/Confinement_A1.tla` re-encoded, with its frozen predecessor
`spec/Confinement.tla` as the same encoding under one flag: the two modules differ only in `Evidence`, which
reads the asked profile at rungs 0 and 1 in A1 (`Declared <= 1`, ADR-0034 finding 6) and at rung 1 only in
the frozen module (`Declared = 1`). `Cfg.a1` selects the clause, and every theorem is proved for both values,
so `Confinement_proof.tla`'s and `Confinement_A1_proof.tla`'s theorems are each covered. These are two of the
three modules the certified TLAPS run does not certify: three `TypeOK` steps in each are proved by Z3 and by
nothing else (`proof-certification.md`). Here `TypeOK` has no counterpart, and every step is kernel-checked.

The proofs follow the TLAPS modules' inductive invariants: generation binding for `ContainedMeansConfined`
(`GuestImg`, `GuestGen`, `LowRungHonest`, `PendingBinds`, `LeaseBinds`), `PendingAttested` for
`NoSilentDowngrade`, `contested ⊆ revoked` and `RevokedNotLive` for `ContestedStopped`, and `FreshAppraisal`
by itself. The one TLAPS assumption, `Declared ∈ 0..3`, is not needed and not taken; the theorems hold for
every natural `Declared`. `MaxEpoch`, `MaxIdx` and `MaxGen` only cut the state space.

Encoding notes beyond the prelude's: a successor state is written `st' = { st with ... }`, which is the
TLA+ action's primed conjuncts and its `UNCHANGED` list at once; string-valued fields are inductive types
(`Image` for profiles and "rogue"/"none", `PendV` for a pending verdict, `RenewOut` for the renewal witness
set); `live` and `verifierUp` are `Bool`; the record field `contained` and the flags `refused` and
`tamperKilled` are `Prop`. An `IF`/`CASE` chain whose branches assign different successors is the disjunction
of its branches with their conditions. The TLA+ action `Act(p)` is `ActStep`.
-/

namespace Topak.Spec.Confinement
open Topak.Spec PSet

inductive Mut | none | M_HOST | M_HW | M_CONTESTED | M_UNBOUND | M_STALE | M_DOWNGRADE | M_PROFILE | M_RENEWLOW
  deriving DecidableEq

/-- `CONSTANTS Mut, Declared, MaxEpoch, MaxIdx, MaxGen`, and which module: `a1 = true` is Confinement_A1. -/
structure Cfg where
  m : Mut
  Declared : Nat
  MaxEpoch : Nat
  MaxIdx : Nat
  MaxGen : Nat
  a1 : Bool

inductive Principal | p1 | p2
  deriving DecidableEq

/-- `Promoted ∪ {"rogue", "none"}` -/
inductive Image | arch | med | rogue | none
  deriving DecidableEq
/-- `Promoted == {"arch", "med"}` -/
def Promoted (i : Image) : Prop := i = .arch ∨ i = .med
def Arch : Image := .arch

inductive VerdictV | Attested | Contested | Unattestable
  deriving DecidableEq
/-- A pending appraisal's verdict: "none", or one of the two a grant can read. -/
inductive PendV | none | Attested | Unattestable
  deriving DecidableEq
inductive RenewOut | renewed | contested | lowered | lapsed
  deriving DecidableEq

structure GuestRec where
  img : Image
  asked : Image
  boot : Image
  gen : Nat
structure PendRec where
  v : PendV
  prof : Image
  nEpoch : Nat
  gen : Nat
structure LeaseRec where
  live : Bool
  rung : Nat
  prof : Image
  epoch : Nat
  nEpoch : Nat
  gen : Nat
/-- `[principal |-> p, contained |-> Contained(p), img |-> guest[p].img]` -/
structure ActRec where
  principal : Principal
  contained : Prop
  img : Image

def NoGuest : GuestRec := ⟨.none, .none, .none, 0⟩
def NoPending : PendRec := ⟨.none, .none, 0, 0⟩
def NoLease : LeaseRec := ⟨false, 0, .none, 0, 0, 0⟩

structure State where
  guest : Principal → GuestRec
  gens : Principal → Nat
  pending : Principal → PendRec
  lease : Principal → LeaseRec
  epoch : Nat
  idx : Nat
  revoked : PSet Principal
  verifierUp : Bool
  acted : PSet ActRec
  contested : PSet Principal
  refused : Prop
  tamperKilled : Prop
  renewOut : PSet RenewOut

def Init (st : State) : Prop :=
  (st.guest = fun _ => NoGuest) ∧ (st.gens = fun _ => 0) ∧ (st.pending = fun _ => NoPending) ∧
  (st.lease = fun _ => NoLease) ∧ st.epoch = 0 ∧ st.idx = 0 ∧ st.revoked = ∅ ∧ st.verifierUp = true ∧
  st.acted = ∅ ∧ st.contested = ∅ ∧ ¬ st.refused ∧ ¬ st.tamperKilled ∧ st.renewOut = ∅

/-! ## The host -/

/-- `HostMayLaunchRogue == Declared >= 2 \/ Mut = "M_HOST"` -/
def HostMayLaunchRogue (c : Cfg) : Prop := c.Declared ≥ 2 ∨ c.m = .M_HOST

/-- ```
Launch(p) == /\ guest[p].img = "none" /\ gens[p] < MaxGen
             /\ ∃ asked ∈ Promoted : ∃ img ∈ (IF HostMayLaunchRogue THEN {asked, "rogue"} ELSE {asked}) :
                  guest' = [guest EXCEPT ![p] = [img |-> img, asked |-> asked, boot |-> img, gen |-> gens[p] + 1]]
             /\ gens' = [gens EXCEPT ![p] = @ + 1]
             /\ UNCHANGED <<...>>
``` -/
def Launch (c : Cfg) (p : Principal) (st st' : State) : Prop :=
  (st.guest p).img = .none ∧ st.gens p < c.MaxGen ∧
  ∃ asked img, Promoted asked ∧ (img = asked ∨ (HostMayLaunchRogue c ∧ img = .rogue)) ∧
    st' = { st with guest := upd st.guest p ⟨img, asked, img, st.gens p + 1⟩,
                    gens := upd st.gens p (st.gens p + 1) }

/-- `Kill(p) == guest[p].img # "none" /\ guest' = [guest EXCEPT ![p] = NoGuest] /\ UNCHANGED <<...>>` -/
def Kill (p : Principal) (st st' : State) : Prop :=
  (st.guest p).img ≠ .none ∧ st' = { st with guest := upd st.guest p NoGuest }

/-- ```
Tamper(p) == /\ guest[p].img ∉ {"none", "rogue"}
             /\ \/ Declared <= 2 /\ Mut = "M_HOST" /\ guest' = [guest EXCEPT ![p].img = "rogue"] /\ UNCHANGED tamperKilled
                \/ Declared = 3 /\ Mut = "M_HW" /\ guest' = [guest EXCEPT ![p].img = "rogue"] /\ UNCHANGED tamperKilled
                \/ Declared = 3 /\ Mut # "M_HW" /\ guest' = [guest EXCEPT ![p] = NoGuest] /\ tamperKilled' = TRUE
             /\ UNCHANGED <<...>>
``` -/
def Tamper (c : Cfg) (p : Principal) (st st' : State) : Prop :=
  (st.guest p).img ≠ .none ∧ (st.guest p).img ≠ .rogue ∧
  ((c.Declared ≤ 2 ∧ c.m = .M_HOST ∧ st' = { st with guest := upd st.guest p { st.guest p with img := .rogue } }) ∨
   (c.Declared = 3 ∧ c.m = .M_HW ∧ st' = { st with guest := upd st.guest p { st.guest p with img := .rogue } }) ∨
   (c.Declared = 3 ∧ c.m ≠ .M_HW ∧ st' = { st with guest := upd st.guest p NoGuest, tamperKilled := True }))

/-- `VerifierFlip == Declared = 3 /\ verifierUp' = ~verifierUp /\ UNCHANGED <<...>>` -/
def VerifierFlip (c : Cfg) (st st' : State) : Prop :=
  c.Declared = 3 ∧ st' = { st with verifierUp := !st.verifierUp }

/-! ## The mechanism -/

/-- `Evidence(p) == IF Declared <= 1 THEN guest[p].asked ELSE guest[p].boot` in Confinement_A1;
`IF Declared = 1 THEN ... ELSE ...` in the frozen Confinement. -/
def LowRung (c : Cfg) : Prop := if c.a1 then c.Declared ≤ 1 else c.Declared = 1
instance (c : Cfg) : Decidable (LowRung c) := by unfold LowRung; infer_instance
def Evidence (c : Cfg) (p : Principal) (st : State) : Image :=
  if LowRung c then (st.guest p).asked else (st.guest p).boot

/-- ```
Verdict(p) == IF Declared = 3 /\ ~verifierUp THEN "Unattestable"
              ELSE IF Evidence(p) = guest[p].asked THEN "Attested" ELSE "Contested"
``` -/
def Verdict (c : Cfg) (p : Principal) (st : State) : VerdictV :=
  if c.Declared = 3 ∧ st.verifierUp = false then .Unattestable
  else if Evidence c p st = (st.guest p).asked then .Attested else .Contested

/-- `IF v = "Contested" THEN "Attested" ELSE v`, into a pending verdict. -/
def toPend : VerdictV → PendV
  | .Attested => .Attested
  | .Contested => .Attested
  | .Unattestable => .Unattestable

/-- ```
Appraise(p) == /\ guest[p].img # "none" /\ ~lease[p].live /\ p ∉ revoked /\ pending[p].v = "none"
               /\ LET v == Verdict(p) IN
                  IF v = "Contested" /\ Mut # "M_CONTESTED"
                  THEN idx < MaxIdx /\ idx' = idx + 1 /\ revoked' = revoked ∪ {p} /\ contested' = contested ∪ {p}
                  ELSE IF v = "Unattestable" /\ Mut # "M_DOWNGRADE" THEN refused' = TRUE
                  ELSE /\ pending' = [pending EXCEPT ![p] = [v |-> IF v = "Contested" THEN "Attested" ELSE v,
                                                            prof |-> guest[p].asked, nEpoch |-> epoch, gen |-> guest[p].gen]]
                       /\ contested' = IF v = "Contested" THEN contested ∪ {p} ELSE contested
               /\ UNCHANGED <<...>>
``` -/
def Appraise (c : Cfg) (p : Principal) (st st' : State) : Prop :=
  (st.guest p).img ≠ .none ∧ (st.lease p).live = false ∧ ¬ p ∈ st.revoked ∧ (st.pending p).v = .none ∧
  ((Verdict c p st = .Contested ∧ c.m ≠ .M_CONTESTED ∧ st.idx < c.MaxIdx ∧
      st' = { st with idx := st.idx + 1, revoked := st.revoked ∪ {p}, contested := st.contested ∪ {p} }) ∨
   (¬ (Verdict c p st = .Contested ∧ c.m ≠ .M_CONTESTED) ∧ Verdict c p st = .Unattestable ∧ c.m ≠ .M_DOWNGRADE ∧
      st' = { st with refused := True }) ∨
   (¬ (Verdict c p st = .Contested ∧ c.m ≠ .M_CONTESTED) ∧ ¬ (Verdict c p st = .Unattestable ∧ c.m ≠ .M_DOWNGRADE) ∧
      st' = { st with pending := upd st.pending p ⟨toPend (Verdict c p st), (st.guest p).asked, st.epoch, (st.guest p).gen⟩,
                      contested := if Verdict c p st = .Contested then st.contested ∪ {p} else st.contested }))

/-- `Discard(p) == pending[p].v # "none" /\ pending' = [pending EXCEPT ![p] = NoPending] /\ UNCHANGED <<...>>` -/
def Discard (p : Principal) (st st' : State) : Prop :=
  (st.pending p).v ≠ .none ∧ st' = { st with pending := upd st.pending p NoPending }

def FreshEpoch (c : Cfg) (p : Principal) (st : State) : Prop := c.m = .M_STALE ∨ (st.pending p).nEpoch = st.epoch
def SameGuest (c : Cfg) (p : Principal) (st : State) : Prop := c.m = .M_UNBOUND ∨ (st.pending p).gen = (st.guest p).gen

/-- ```
Grant(p) == /\ pending[p].v ∈ {"Attested", "Unattestable"} /\ ~lease[p].live /\ p ∉ revoked /\ idx < MaxIdx
            /\ FreshEpoch(p) /\ SameGuest(p)
            /\ lease' = [lease EXCEPT ![p] = [live |-> TRUE, rung |-> IF pending[p].v = "Attested" THEN Declared ELSE 0,
                                               prof |-> pending[p].prof, epoch |-> epoch, nEpoch |-> pending[p].nEpoch, gen |-> pending[p].gen]]
            /\ pending' = [pending EXCEPT ![p] = NoPending] /\ idx' = idx + 1
            /\ UNCHANGED <<...>>
``` -/
def Grant (c : Cfg) (p : Principal) (st st' : State) : Prop :=
  ((st.pending p).v = .Attested ∨ (st.pending p).v = .Unattestable) ∧
  (st.lease p).live = false ∧ ¬ p ∈ st.revoked ∧ st.idx < c.MaxIdx ∧ FreshEpoch c p st ∧ SameGuest c p st ∧
  st' = { st with lease := upd st.lease p ⟨true, if (st.pending p).v = .Attested then c.Declared else 0,
                                           (st.pending p).prof, st.epoch, (st.pending p).nEpoch, (st.pending p).gen⟩,
                  pending := upd st.pending p NoPending, idx := st.idx + 1 }

/-- §4. `Contained(p) == lease[p].live /\ lease[p].rung >= 1 /\ (Mut = "M_PROFILE" \/ lease[p].prof = Arch)` -/
def Contained (c : Cfg) (p : Principal) (st : State) : Prop :=
  (st.lease p).live = true ∧ (st.lease p).rung ≥ 1 ∧ (c.m = .M_PROFILE ∨ (st.lease p).prof = Arch)

/-- ```
Act(p) == /\ lease[p].live /\ lease[p].epoch = epoch /\ guest[p].img # "none"
          /\ (Mut = "M_UNBOUND" \/ lease[p].gen = guest[p].gen)
          /\ acted' = acted ∪ {[principal |-> p, contained |-> Contained(p), img |-> guest[p].img]}
          /\ UNCHANGED <<...>>
``` -/
def ActStep (c : Cfg) (p : Principal) (st st' : State) : Prop :=
  (st.lease p).live = true ∧ (st.lease p).epoch = st.epoch ∧ (st.guest p).img ≠ .none ∧
  (c.m = .M_UNBOUND ∨ (st.lease p).gen = (st.guest p).gen) ∧
  st' = { st with acted := st.acted ∪ {⟨p, Contained c p st, (st.guest p).img⟩} }

/-- ```
Renew(p) == /\ lease[p].live /\ lease[p].epoch = epoch /\ guest[p].img # "none" /\ lease[p].gen = guest[p].gen
            /\ idx < MaxIdx /\ idx' = idx + 1
            /\ LET v == Verdict(p) IN
               CASE v = "Attested" -> lease' = [lease EXCEPT ![p].nEpoch = epoch] /\ renewOut' = renewOut ∪ {"renewed"} /\ UNCHANGED <<revoked, contested>>
                 [] v = "Contested" -> lease' = [lease EXCEPT ![p] = NoLease] /\ revoked' = revoked ∪ {p} /\ contested' = contested ∪ {p} /\ renewOut' = renewOut ∪ {"contested"}
                 [] v = "Unattestable" /\ Mut = "M_RENEWLOW" -> lease' = [lease EXCEPT ![p].rung = 0, ![p].nEpoch = epoch] /\ renewOut' = renewOut ∪ {"lowered"} /\ UNCHANGED <<revoked, contested>>
                 [] OTHER -> lease' = [lease EXCEPT ![p] = NoLease] /\ renewOut' = renewOut ∪ {"lapsed"} /\ UNCHANGED <<revoked, contested>>
            /\ UNCHANGED <<...>>
``` -/
def Renew (c : Cfg) (p : Principal) (st st' : State) : Prop :=
  (st.lease p).live = true ∧ (st.lease p).epoch = st.epoch ∧ (st.guest p).img ≠ .none ∧
  (st.lease p).gen = (st.guest p).gen ∧ st.idx < c.MaxIdx ∧
  ((Verdict c p st = .Attested ∧
      st' = { st with idx := st.idx + 1, lease := upd st.lease p { st.lease p with nEpoch := st.epoch },
                      renewOut := st.renewOut ∪ {.renewed} }) ∨
   (Verdict c p st = .Contested ∧
      st' = { st with idx := st.idx + 1, lease := upd st.lease p NoLease, revoked := st.revoked ∪ {p},
                      contested := st.contested ∪ {p}, renewOut := st.renewOut ∪ {.contested} }) ∨
   (Verdict c p st = .Unattestable ∧ c.m = .M_RENEWLOW ∧
      st' = { st with idx := st.idx + 1, lease := upd st.lease p { st.lease p with rung := 0, nEpoch := st.epoch },
                      renewOut := st.renewOut ∪ {.lowered} }) ∨
   (Verdict c p st = .Unattestable ∧ c.m ≠ .M_RENEWLOW ∧
      st' = { st with idx := st.idx + 1, lease := upd st.lease p NoLease, renewOut := st.renewOut ∪ {.lapsed} }))

/-- `EndRound(p) == lease[p].live /\ lease' = [lease EXCEPT ![p] = NoLease] /\ guest' = [guest EXCEPT ![p] = NoGuest] /\ UNCHANGED <<...>>` -/
def EndRound (p : Principal) (st st' : State) : Prop :=
  (st.lease p).live = true ∧ st' = { st with lease := upd st.lease p NoLease, guest := upd st.guest p NoGuest }

/-- `Fence == epoch < MaxEpoch /\ idx < MaxIdx /\ epoch' = epoch + 1 /\ idx' = idx + 1 /\ UNCHANGED <<...>>` -/
def Fence (c : Cfg) (st st' : State) : Prop :=
  st.epoch < c.MaxEpoch ∧ st.idx < c.MaxIdx ∧ st' = { st with epoch := st.epoch + 1, idx := st.idx + 1 }

def Next (c : Cfg) (st st' : State) : Prop :=
  Fence c st st' ∨ VerifierFlip c st st' ∨
  ∃ p, Launch c p st st' ∨ Kill p st st' ∨ Tamper c p st st' ∨ Appraise c p st st' ∨ Discard p st st' ∨
       Grant c p st st' ∨ Renew c p st st' ∨ ActStep c p st st' ∨ EndRound p st st'

/-! ## The four properties -/

/-- §4. `∀ r ∈ acted : r.contained => r.img = Arch` -/
def ContainedMeansConfined (st : State) : Prop := ∀ r, r ∈ st.acted → r.contained → r.img = Arch
/-- §3. `∀ p : lease[p].live => lease[p].rung = Declared` -/
def NoSilentDowngrade (c : Cfg) (st : State) : Prop := ∀ p, (st.lease p).live = true → (st.lease p).rung = c.Declared
/-- §3. `∀ p ∈ contested : p ∈ revoked /\ ~lease[p].live` -/
def ContestedStopped (st : State) : Prop := ∀ p, p ∈ st.contested → p ∈ st.revoked ∧ (st.lease p).live = false
/-- §3. `∀ p : lease[p].live => lease[p].nEpoch = lease[p].epoch` -/
def FreshAppraisal (st : State) : Prop := ∀ p, (st.lease p).live = true → (st.lease p).nEpoch = (st.lease p).epoch

def Safe (c : Cfg) (st : State) : Prop :=
  ContainedMeansConfined st ∧ NoSilentDowngrade c st ∧ ContestedStopped st ∧ FreshAppraisal st

/-! ## ContainedMeansConfined: generation binding -/

def GuestImg (st : State) : Prop := ∀ p, (st.guest p).img = (st.guest p).boot
def GuestGen (st : State) : Prop :=
  ∀ p, ((st.guest p).img = .none → (st.guest p).gen = 0) ∧
       ((st.guest p).img ≠ .none → (st.guest p).gen = st.gens p ∧ st.gens p ≥ 1)
def LowRungHonest (c : Cfg) (st : State) : Prop :=
  ∀ p, c.Declared < 2 → (st.guest p).img ≠ .none → (st.guest p).boot = (st.guest p).asked
def PendingBinds (st : State) : Prop :=
  ∀ p, (st.pending p).v = .Attested →
    (st.pending p).gen ≥ 1 ∧ (st.pending p).gen ≤ st.gens p ∧
    ((st.guest p).img ≠ .none → (st.pending p).gen = (st.guest p).gen →
      (st.pending p).prof = (st.guest p).asked ∧ (st.guest p).boot = (st.guest p).asked)
def LeaseBinds (st : State) : Prop :=
  ∀ p, (st.lease p).live = true → (st.lease p).rung ≥ 1 →
    (st.lease p).gen ≥ 1 ∧ (st.lease p).gen ≤ st.gens p ∧
    ((st.guest p).img ≠ .none → (st.lease p).gen = (st.guest p).gen →
      (st.lease p).prof = (st.guest p).asked ∧ (st.guest p).boot = (st.guest p).asked)
def InvC (c : Cfg) (st : State) : Prop :=
  GuestImg st ∧ GuestGen st ∧ LowRungHonest c st ∧ PendingBinds st ∧ LeaseBinds st ∧ ContainedMeansConfined st

theorem InitInvC (c : Cfg) (st : State) (h : Init st) : InvC c st := by
  obtain ⟨hg, hgs, hp, hl, -, -, -, -, ha, -⟩ := h
  refine ⟨?_, ?_, ?_, ?_, ?_, ?_⟩
  · intro p; rw [hg]; rfl
  · intro p; rw [hg, hgs]; exact ⟨fun _ => rfl, fun h => absurd rfl h⟩
  · intro p _ h; rw [hg] at h; exact absurd rfl h
  · intro p h; rw [hp] at h; cases h
  · intro p h; rw [hl] at h; cases h
  · intro r hr; rw [ha] at hr; exact hr.elim

/-- An Attested verdict says the booted image is the asked one, given honest low rungs. -/
theorem attested_boot (c : Cfg) (p : Principal) (st : State) (hL : LowRungHonest c st)
    (hg : (st.guest p).img ≠ .none) (hv : Verdict c p st = .Attested) :
    (st.guest p).boot = (st.guest p).asked := by
  unfold Verdict at hv
  split at hv
  · cases hv
  · split at hv
    · rename_i hE
      unfold Evidence at hE
      split at hE
      · rename_i hlow
        apply hL p _ hg
        unfold LowRung at hlow
        split at hlow <;> omega
      · exact hE
    · cases hv

theorem NextInvC (c : Cfg) (hH : c.m ≠ .M_HOST) (hW : c.m ≠ .M_HW) (hC : c.m ≠ .M_CONTESTED)
    (hU : c.m ≠ .M_UNBOUND) (hP : c.m ≠ .M_PROFILE) (st st' : State) (hi : InvC c st) (hn : Next c st st') :
    InvC c st' := by
  obtain ⟨hI, hG, hL, hPB, hLB, hCMC⟩ := hi
  rcases hn with ⟨-, -, rfl⟩ | ⟨-, rfl⟩ | ⟨p, h | h | h | h | h | h | h | h | h⟩
  · exact ⟨hI, hG, hL, hPB, hLB, hCMC⟩
  · exact ⟨hI, hG, hL, hPB, hLB, hCMC⟩
  · -- Launch(p): the host launches what was asked below rung 2
    obtain ⟨hnone, -, asked, img, hprom, himg, rfl⟩ := h
    have hhonest : c.Declared < 2 → img = asked := by
      intro hd
      rcases himg with h | ⟨hr | hr, -⟩
      · exact h
      · omega
      · exact absurd hr hH
    have hne : img ≠ .none := by
      rcases himg with h' | ⟨-, h'⟩
      · subst h'; rcases hprom with ha | ha <;> (subst ha; decide)
      · subst h'; decide
    refine ⟨?_, ?_, ?_, ?_, ?_, hCMC⟩
    · intro q; by_cases hq : q = p
      · subst hq; simp only [upd_same]
      · simp only [upd_other _ _ _ _ hq]; exact hI q
    · intro q; by_cases hq : q = p
      · subst hq; simp only [upd_same]
        exact ⟨fun h => absurd h hne, fun _ => ⟨trivial, Nat.succ_pos _⟩⟩
      · simp only [upd_other _ _ _ _ hq]; exact hG q
    · intro q hd hne'; by_cases hq : q = p
      · subst hq; simp only [upd_same]; exact hhonest hd
      · simp only [upd_other _ _ _ _ hq] at hne' ⊢; exact hL q hd hne'
    · intro q hv; by_cases hq : q = p
      · subst hq
        obtain ⟨h1, h2, -⟩ := hPB q hv
        simp only [upd_same]
        exact ⟨h1, by omega, fun _ hgen => by omega⟩
      · simp only [upd_other _ _ _ _ hq]; exact hPB q hv
    · intro q hl hr; by_cases hq : q = p
      · subst hq
        obtain ⟨h1, h2, -⟩ := hLB q hl hr
        simp only [upd_same]
        exact ⟨h1, by omega, fun _ hgen => by omega⟩
      · simp only [upd_other _ _ _ _ hq]; exact hLB q hl hr
  · -- Kill(p)
    obtain ⟨-, rfl⟩ := h
    refine ⟨?_, ?_, ?_, ?_, ?_, hCMC⟩
    · intro q; by_cases hq : q = p
      · subst hq; simp only [upd_same]; rfl
      · simp only [upd_other _ _ _ _ hq]; exact hI q
    · intro q; by_cases hq : q = p
      · subst hq; simp only [upd_same]; exact ⟨fun _ => rfl, fun h => absurd rfl h⟩
      · simp only [upd_other _ _ _ _ hq]; exact hG q
    · intro q hd hne; by_cases hq : q = p
      · subst hq; simp only [upd_same] at hne; exact absurd rfl hne
      · simp only [upd_other _ _ _ _ hq] at hne ⊢; exact hL q hd hne
    · intro q hv; by_cases hq : q = p
      · subst hq; obtain ⟨h1, h2, -⟩ := hPB q hv
        simp only [upd_same]; exact ⟨h1, h2, fun hne => absurd rfl hne⟩
      · simp only [upd_other _ _ _ _ hq]; exact hPB q hv
    · intro q hl hr; by_cases hq : q = p
      · subst hq; obtain ⟨h1, h2, -⟩ := hLB q hl hr
        simp only [upd_same]; exact ⟨h1, h2, fun hne => absurd rfl hne⟩
      · simp only [upd_other _ _ _ _ hq]; exact hLB q hl hr
  · -- Tamper(p): under the specified host and hardware, Tamper only kills
    obtain ⟨-, -, ⟨-, hm, -⟩ | ⟨-, hm, -⟩ | ⟨-, -, rfl⟩⟩ := h
    · exact absurd hm hH
    · exact absurd hm hW
    refine ⟨?_, ?_, ?_, ?_, ?_, hCMC⟩
    · intro q; by_cases hq : q = p
      · subst hq; simp only [upd_same]; rfl
      · simp only [upd_other _ _ _ _ hq]; exact hI q
    · intro q; by_cases hq : q = p
      · subst hq; simp only [upd_same]; exact ⟨fun _ => rfl, fun h => absurd rfl h⟩
      · simp only [upd_other _ _ _ _ hq]; exact hG q
    · intro q hd hne; by_cases hq : q = p
      · subst hq; simp only [upd_same] at hne; exact absurd rfl hne
      · simp only [upd_other _ _ _ _ hq] at hne ⊢; exact hL q hd hne
    · intro q hv; by_cases hq : q = p
      · subst hq; obtain ⟨h1, h2, -⟩ := hPB q hv
        simp only [upd_same]; exact ⟨h1, h2, fun hne => absurd rfl hne⟩
      · simp only [upd_other _ _ _ _ hq]; exact hPB q hv
    · intro q hl hr; by_cases hq : q = p
      · subst hq; obtain ⟨h1, h2, -⟩ := hLB q hl hr
        simp only [upd_same]; exact ⟨h1, h2, fun hne => absurd rfl hne⟩
      · simp only [upd_other _ _ _ _ hq]; exact hLB q hl hr
  · -- Appraise(p)
    obtain ⟨hg, -, -, -, ⟨-, -, -, rfl⟩ | ⟨-, -, -, rfl⟩ | ⟨hnc, hnu, rfl⟩⟩ := h
    · exact ⟨hI, hG, hL, hPB, hLB, hCMC⟩
    · exact ⟨hI, hG, hL, hPB, hLB, hCMC⟩
    · refine ⟨hI, hG, hL, ?_, hLB, hCMC⟩
      intro q hv; by_cases hq : q = p
      · subst hq
        simp only [upd_same] at hv ⊢
        have hgen := (hG q).2 hg
        -- the verdict was Attested: Contested needs M_CONTESTED, Unattestable is refused
        have hv' : Verdict c q st = .Attested := by
          cases hvv : Verdict c q st
          · rfl
          · exact absurd ⟨hvv, hC⟩ hnc
          · rw [hvv] at hv; cases hv
        exact ⟨by omega, by omega, fun _ _ => ⟨trivial, attested_boot c q st hL hg hv'⟩⟩
      · simp only [upd_other _ _ _ _ hq] at hv ⊢; exact hPB q hv
  · -- Discard(p)
    obtain ⟨-, rfl⟩ := h
    refine ⟨hI, hG, hL, ?_, hLB, hCMC⟩
    intro q hv; by_cases hq : q = p
    · subst hq; simp only [upd_same] at hv; cases hv
    · simp only [upd_other _ _ _ _ hq] at hv ⊢; exact hPB q hv
  · -- Grant(p): the lease copies the appraisal's generation and profile
    obtain ⟨hv, -, -, -, -, -, rfl⟩ := h
    refine ⟨hI, hG, hL, ?_, ?_, hCMC⟩
    · intro q hv'; by_cases hq : q = p
      · subst hq; simp only [upd_same] at hv'; cases hv'
      · simp only [upd_other _ _ _ _ hq] at hv' ⊢; exact hPB q hv'
    · intro q hl hr; by_cases hq : q = p
      · subst hq
        rcases hv with hatt | hun
        · simp only [upd_same]
          exact hPB q hatt
        · simp only [upd_same, hun] at hr
          cases hr
      · simp only [upd_other _ _ _ _ hq] at hl hr ⊢; exact hLB q hl hr
  · -- Renew(p)
    obtain ⟨-, -, -, -, -, ⟨-, rfl⟩ | ⟨-, rfl⟩ | ⟨-, -, rfl⟩ | ⟨-, -, rfl⟩⟩ := h
    · refine ⟨hI, hG, hL, hPB, ?_, hCMC⟩
      intro q hl hr; by_cases hq : q = p
      · subst hq; simp only [upd_same] at hl hr ⊢; exact hLB q hl hr
      · simp only [upd_other _ _ _ _ hq] at hl hr ⊢; exact hLB q hl hr
    · refine ⟨hI, hG, hL, hPB, ?_, hCMC⟩
      intro q hl hr; by_cases hq : q = p
      · subst hq; simp only [upd_same] at hl; cases hl
      · simp only [upd_other _ _ _ _ hq] at hl hr ⊢; exact hLB q hl hr
    · refine ⟨hI, hG, hL, hPB, ?_, hCMC⟩
      intro q hl hr; by_cases hq : q = p
      · subst hq; simp only [upd_same] at hr; omega
      · simp only [upd_other _ _ _ _ hq] at hl hr ⊢; exact hLB q hl hr
    · refine ⟨hI, hG, hL, hPB, ?_, hCMC⟩
      intro q hl hr; by_cases hq : q = p
      · subst hq; simp only [upd_same] at hl; cases hl
      · simp only [upd_other _ _ _ _ hq] at hl hr ⊢; exact hLB q hl hr
  · -- Act(p): a contained act runs the asked image, which is the lease's profile, Arch
    obtain ⟨hl, -, hg, hgen, rfl⟩ := h
    refine ⟨hI, hG, hL, hPB, hLB, ?_⟩
    intro r hr hc
    rcases hr with hr | hr
    · exact hCMC r hr hc
    · have hr : r = ⟨p, Contained c p st, (st.guest p).img⟩ := hr
      subst hr
      obtain ⟨-, hrung, hprof⟩ := hc
      have hgen' : (st.lease p).gen = (st.guest p).gen := by
        rcases hgen with h | h
        · exact absurd h hU
        · exact h
      obtain ⟨-, -, hb⟩ := hLB p hl hrung
      obtain ⟨hprof', hboot⟩ := hb hg hgen'
      have hprof'' : (st.lease p).prof = Arch := by
        rcases hprof with h | h
        · exact absurd h hP
        · exact h
      show (st.guest p).img = Arch
      rw [hI p, hboot, ← hprof', hprof'']
  · -- EndRound(p)
    obtain ⟨-, rfl⟩ := h
    refine ⟨?_, ?_, ?_, ?_, ?_, hCMC⟩
    · intro q; by_cases hq : q = p
      · subst hq; simp only [upd_same]; rfl
      · simp only [upd_other _ _ _ _ hq]; exact hI q
    · intro q; by_cases hq : q = p
      · subst hq; simp only [upd_same]; exact ⟨fun _ => rfl, fun h => absurd rfl h⟩
      · simp only [upd_other _ _ _ _ hq]; exact hG q
    · intro q hd hne; by_cases hq : q = p
      · subst hq; simp only [upd_same] at hne; exact absurd rfl hne
      · simp only [upd_other _ _ _ _ hq] at hne ⊢; exact hL q hd hne
    · intro q hv; by_cases hq : q = p
      · subst hq; obtain ⟨h1, h2, -⟩ := hPB q hv
        simp only [upd_same]; exact ⟨h1, h2, fun hne => absurd rfl hne⟩
      · simp only [upd_other _ _ _ _ hq]; exact hPB q hv
    · intro q hl hr; by_cases hq : q = p
      · subst hq; simp only [upd_same] at hl; cases hl
      · simp only [upd_other _ _ _ _ hq] at hl hr ⊢; exact hLB q hl hr

/-- `THEOREM ContainedMeansConfinedAlways == ASSUME Mut \notin {"M_HOST", "M_HW", "M_CONTESTED", "M_UNBOUND", "M_PROFILE"} PROVE Spec => []ContainedMeansConfined` -/
theorem ContainedMeansConfinedAlways (c : Cfg) (hH : c.m ≠ .M_HOST) (hW : c.m ≠ .M_HW) (hC : c.m ≠ .M_CONTESTED)
    (hU : c.m ≠ .M_UNBOUND) (hP : c.m ≠ .M_PROFILE) :
    ∀ st, Reachable Init (Next c) st → ContainedMeansConfined st :=
  invariant (InvC c) ContainedMeansConfined (InitInvC c) (NextInvC c hH hW hC hU hP) (fun _ h => h.2.2.2.2.2)

/-! ## NoSilentDowngrade -/

def PendingAttested (st : State) : Prop := ∀ p, (st.pending p).v ≠ .Unattestable
def InvD (c : Cfg) (st : State) : Prop := PendingAttested st ∧ NoSilentDowngrade c st

theorem InitInvD (c : Cfg) (st : State) (h : Init st) : InvD c st := by
  obtain ⟨-, -, hp, hl, -⟩ := h
  exact ⟨fun p => (by rw [hp]; exact fun h => by cases h), fun p hl' => (by rw [hl] at hl'; cases hl')⟩

theorem NextInvD (c : Cfg) (hD : c.m ≠ .M_DOWNGRADE) (hR : c.m ≠ .M_RENEWLOW) (st st' : State)
    (hi : InvD c st) (hn : Next c st st') : InvD c st' := by
  obtain ⟨hPA, hNS⟩ := hi
  rcases hn with ⟨-, -, rfl⟩ | ⟨-, rfl⟩ | ⟨p, h | h | h | h | h | h | h | h | h⟩
  · exact ⟨hPA, hNS⟩
  · exact ⟨hPA, hNS⟩
  · obtain ⟨-, -, -, -, -, -, rfl⟩ := h; exact ⟨hPA, hNS⟩
  · obtain ⟨-, rfl⟩ := h; exact ⟨hPA, hNS⟩
  · obtain ⟨-, -, ⟨-, -, rfl⟩ | ⟨-, -, rfl⟩ | ⟨-, -, rfl⟩⟩ := h <;> exact ⟨hPA, hNS⟩
  · -- Appraise(p): an Unattestable verdict is refused, so what is recorded is Attested
    obtain ⟨-, -, -, -, ⟨-, -, -, rfl⟩ | ⟨-, -, -, rfl⟩ | ⟨-, hnu, rfl⟩⟩ := h
    · exact ⟨hPA, hNS⟩
    · exact ⟨hPA, hNS⟩
    · refine ⟨?_, hNS⟩
      intro q; by_cases hq : q = p
      · subst hq; simp only [upd_same]
        cases hvv : Verdict c q st
        · exact fun h => by cases h
        · exact fun h => by cases h
        · exact absurd ⟨hvv, hD⟩ hnu
      · simp only [upd_other _ _ _ _ hq]; exact hPA q
  · obtain ⟨-, rfl⟩ := h
    refine ⟨?_, hNS⟩
    intro q; by_cases hq : q = p
    · subst hq; simp only [upd_same]; exact fun h => by cases h
    · simp only [upd_other _ _ _ _ hq]; exact hPA q
  · -- Grant(p): the verdict is Attested, so the rung is the declared one
    obtain ⟨hv, -, -, -, -, -, rfl⟩ := h
    have hatt : (st.pending p).v = .Attested := by
      rcases hv with h | h
      · exact h
      · exact absurd h (hPA p)
    refine ⟨?_, ?_⟩
    · intro q; by_cases hq : q = p
      · subst hq; simp only [upd_same]; exact fun h => by cases h
      · simp only [upd_other _ _ _ _ hq]; exact hPA q
    · intro q hl; by_cases hq : q = p
      · subst hq; simp only [upd_same]; rw [if_pos hatt]
      · simp only [upd_other _ _ _ _ hq] at hl ⊢; exact hNS q hl
  · -- Renew(p): renewed at the same rung, or lapsed; never lowered
    obtain ⟨-, -, -, -, -, ⟨-, rfl⟩ | ⟨-, rfl⟩ | ⟨-, hm, -⟩ | ⟨-, -, rfl⟩⟩ := h
    · refine ⟨hPA, ?_⟩
      intro q hl; by_cases hq : q = p
      · subst hq; simp only [upd_same] at hl ⊢; exact hNS q hl
      · simp only [upd_other _ _ _ _ hq] at hl ⊢; exact hNS q hl
    · refine ⟨hPA, ?_⟩
      intro q hl; by_cases hq : q = p
      · subst hq; simp only [upd_same] at hl; cases hl
      · simp only [upd_other _ _ _ _ hq] at hl ⊢; exact hNS q hl
    · exact absurd hm hR
    · refine ⟨hPA, ?_⟩
      intro q hl; by_cases hq : q = p
      · subst hq; simp only [upd_same] at hl; cases hl
      · simp only [upd_other _ _ _ _ hq] at hl ⊢; exact hNS q hl
  · obtain ⟨-, -, -, -, rfl⟩ := h; exact ⟨hPA, hNS⟩
  · obtain ⟨-, rfl⟩ := h
    refine ⟨hPA, ?_⟩
    intro q hl; by_cases hq : q = p
    · subst hq; simp only [upd_same] at hl; cases hl
    · simp only [upd_other _ _ _ _ hq] at hl ⊢; exact hNS q hl

/-- `THEOREM NoSilentDowngradeAlways == ASSUME Mut \notin {"M_DOWNGRADE", "M_RENEWLOW"} PROVE Spec => []NoSilentDowngrade` -/
theorem NoSilentDowngradeAlways (c : Cfg) (hD : c.m ≠ .M_DOWNGRADE) (hR : c.m ≠ .M_RENEWLOW) :
    ∀ st, Reachable Init (Next c) st → NoSilentDowngrade c st :=
  invariant (InvD c) (NoSilentDowngrade c) (InitInvD c) (NextInvD c hD hR) (fun _ h => h.2)

/-! ## ContestedStopped -/

def RevokedNotLive (st : State) : Prop := ∀ p, p ∈ st.revoked → (st.lease p).live = false
def InvS (st : State) : Prop := (∀ p, p ∈ st.contested → p ∈ st.revoked) ∧ RevokedNotLive st

theorem InitInvS (st : State) (h : Init st) : InvS st := by
  obtain ⟨-, -, -, -, -, -, hr, -, -, hc, -⟩ := h
  exact ⟨fun p hp => by rw [hc] at hp; exact hp.elim, fun p hp => by rw [hr] at hp; exact hp.elim⟩

theorem NextInvS (c : Cfg) (hC : c.m ≠ .M_CONTESTED) (st st' : State) (hi : InvS st) (hn : Next c st st') : InvS st' := by
  obtain ⟨hCR, hRL⟩ := hi
  rcases hn with ⟨-, -, rfl⟩ | ⟨-, rfl⟩ | ⟨p, h | h | h | h | h | h | h | h | h⟩
  · exact ⟨hCR, hRL⟩
  · exact ⟨hCR, hRL⟩
  · obtain ⟨-, -, -, -, -, -, rfl⟩ := h; exact ⟨hCR, hRL⟩
  · obtain ⟨-, rfl⟩ := h; exact ⟨hCR, hRL⟩
  · obtain ⟨-, -, ⟨-, -, rfl⟩ | ⟨-, -, rfl⟩ | ⟨-, -, rfl⟩⟩ := h <;> exact ⟨hCR, hRL⟩
  · -- Appraise(p): a Contested verdict revokes at once; p holds no lease
    obtain ⟨-, hnl, -, -, ⟨-, -, -, rfl⟩ | ⟨-, -, -, rfl⟩ | ⟨hnc, -, rfl⟩⟩ := h
    · refine ⟨?_, ?_⟩
      · intro q hq; rcases hq with hq | hq
        · exact Or.inl (hCR q hq)
        · exact Or.inr hq
      · intro q hq; rcases hq with hq | hq
        · exact hRL q hq
        · have hq : q = p := hq; subst hq; exact hnl
    · exact ⟨hCR, hRL⟩
    · refine ⟨?_, hRL⟩
      intro q hq
      have hnotc : ¬ Verdict c p st = .Contested := fun h => hnc ⟨h, hC⟩
      rw [if_neg hnotc] at hq
      exact hCR q hq
  · obtain ⟨-, rfl⟩ := h; exact ⟨hCR, hRL⟩
  · -- Grant(p): p is not revoked; a revoked q keeps its lease
    obtain ⟨-, -, hnr, -, -, -, rfl⟩ := h
    refine ⟨hCR, ?_⟩
    intro q hq
    have hqp : q ≠ p := fun h => hnr (h ▸ hq)
    simp only [upd_other _ _ _ _ hqp]; exact hRL q hq
  · -- Renew(p): p is live, so not revoked; Contested revokes and ends the lease
    obtain ⟨hl, -, -, -, -, ⟨-, rfl⟩ | ⟨-, rfl⟩ | ⟨-, -, rfl⟩ | ⟨-, -, rfl⟩⟩ := h
    · refine ⟨hCR, ?_⟩
      intro q hq
      have hqp : q ≠ p := fun h => by subst h; rw [hRL q hq] at hl; cases hl
      simp only [upd_other _ _ _ _ hqp]; exact hRL q hq
    · refine ⟨?_, ?_⟩
      · intro q hq; rcases hq with hq | hq
        · exact Or.inl (hCR q hq)
        · exact Or.inr hq
      · intro q hq; by_cases hqp : q = p
        · subst hqp; simp only [upd_same]; rfl
        · simp only [upd_other _ _ _ _ hqp]
          rcases hq with hq | hq
          · exact hRL q hq
          · exact absurd hq hqp
    · refine ⟨hCR, ?_⟩
      intro q hq
      have hqp : q ≠ p := fun h => by subst h; rw [hRL q hq] at hl; cases hl
      simp only [upd_other _ _ _ _ hqp]; exact hRL q hq
    · refine ⟨hCR, ?_⟩
      intro q hq; by_cases hqp : q = p
      · subst hqp; simp only [upd_same]; rfl
      · simp only [upd_other _ _ _ _ hqp]; exact hRL q hq
  · obtain ⟨-, -, -, -, rfl⟩ := h; exact ⟨hCR, hRL⟩
  · obtain ⟨-, rfl⟩ := h
    refine ⟨hCR, ?_⟩
    intro q hq; by_cases hqp : q = p
    · subst hqp; simp only [upd_same]; rfl
    · simp only [upd_other _ _ _ _ hqp]; exact hRL q hq

/-- `THEOREM ContestedStoppedAlways == ASSUME Mut # "M_CONTESTED" PROVE Spec => []ContestedStopped` -/
theorem ContestedStoppedAlways (c : Cfg) (hC : c.m ≠ .M_CONTESTED) :
    ∀ st, Reachable Init (Next c) st → ContestedStopped st :=
  invariant InvS ContestedStopped InitInvS (NextInvS c hC)
    (fun _ ⟨hCR, hRL⟩ p hp => ⟨hCR p hp, hRL p (hCR p hp)⟩)

/-! ## FreshAppraisal -/

theorem InitInvF (st : State) (h : Init st) : FreshAppraisal st := by
  obtain ⟨-, -, -, hl, -⟩ := h
  intro p hl'; rw [hl] at hl'; cases hl'

theorem NextInvF (c : Cfg) (hS : c.m ≠ .M_STALE) (st st' : State) (hi : FreshAppraisal st) (hn : Next c st st') :
    FreshAppraisal st' := by
  rcases hn with ⟨-, -, rfl⟩ | ⟨-, rfl⟩ | ⟨p, h | h | h | h | h | h | h | h | h⟩
  · exact hi
  · exact hi
  · obtain ⟨-, -, -, -, -, -, rfl⟩ := h; exact hi
  · obtain ⟨-, rfl⟩ := h; exact hi
  · obtain ⟨-, -, ⟨-, -, rfl⟩ | ⟨-, -, rfl⟩ | ⟨-, -, rfl⟩⟩ := h <;> exact hi
  · obtain ⟨-, -, -, -, ⟨-, -, -, rfl⟩ | ⟨-, -, -, rfl⟩ | ⟨-, -, rfl⟩⟩ := h <;> exact hi
  · obtain ⟨-, rfl⟩ := h; exact hi
  · -- Grant(p): the appraisal is fresh, so the lease's nEpoch is the current epoch
    obtain ⟨-, -, -, -, hfe, -, rfl⟩ := h
    have hfe : (st.pending p).nEpoch = st.epoch := by
      rcases hfe with h | h
      · exact absurd h hS
      · exact h
    intro q hl; by_cases hq : q = p
    · subst hq; simp only [upd_same]; exact hfe
    · simp only [upd_other _ _ _ _ hq] at hl ⊢; exact hi q hl
  · -- Renew(p): re-attested at the current epoch, which is the lease's epoch
    obtain ⟨-, hle, -, -, -, ⟨-, rfl⟩ | ⟨-, rfl⟩ | ⟨-, -, rfl⟩ | ⟨-, -, rfl⟩⟩ := h
    · intro q hl; by_cases hq : q = p
      · subst hq; simp only [upd_same]; exact hle.symm
      · simp only [upd_other _ _ _ _ hq] at hl ⊢; exact hi q hl
    · intro q hl; by_cases hq : q = p
      · subst hq; simp only [upd_same] at hl; cases hl
      · simp only [upd_other _ _ _ _ hq] at hl ⊢; exact hi q hl
    · intro q hl; by_cases hq : q = p
      · subst hq; simp only [upd_same]; exact hle.symm
      · simp only [upd_other _ _ _ _ hq] at hl ⊢; exact hi q hl
    · intro q hl; by_cases hq : q = p
      · subst hq; simp only [upd_same] at hl; cases hl
      · simp only [upd_other _ _ _ _ hq] at hl ⊢; exact hi q hl
  · obtain ⟨-, -, -, -, rfl⟩ := h; exact hi
  · obtain ⟨-, rfl⟩ := h
    intro q hl; by_cases hq : q = p
    · subst hq; simp only [upd_same] at hl; cases hl
    · simp only [upd_other _ _ _ _ hq] at hl ⊢; exact hi q hl

/-- `THEOREM FreshAppraisalAlways == ASSUME Mut # "M_STALE" PROVE Spec => []FreshAppraisal` -/
theorem FreshAppraisalAlways (c : Cfg) (hS : c.m ≠ .M_STALE) :
    ∀ st, Reachable Init (Next c) st → FreshAppraisal st :=
  invariant FreshAppraisal FreshAppraisal InitInvF (NextInvF c hS) (fun _ h => h)

/-- `THEOREM SafeAlways == ASSUME Mut = "none" PROVE Spec => []Safe`, for every rung and bound, in both modules. -/
theorem SafeAlways (Declared MaxEpoch MaxIdx MaxGen : Nat) (a1 : Bool) :
    ∀ st, Reachable Init (Next ⟨.none, Declared, MaxEpoch, MaxIdx, MaxGen, a1⟩) st →
      Safe ⟨.none, Declared, MaxEpoch, MaxIdx, MaxGen, a1⟩ st :=
  fun st h =>
    ⟨ContainedMeansConfinedAlways _ (by simp) (by simp) (by simp)
        (by simp) (by simp) st h,
     NoSilentDowngradeAlways _ (by simp) (by simp) st h,
     ContestedStoppedAlways _ (by simp) st h,
     FreshAppraisalAlways _ (by simp) st h⟩

/-- The two modules by name. -/
theorem Confinement_A1_SafeAlways (Declared MaxEpoch MaxIdx MaxGen : Nat) :
    ∀ st, Reachable Init (Next ⟨.none, Declared, MaxEpoch, MaxIdx, MaxGen, true⟩) st →
      Safe ⟨.none, Declared, MaxEpoch, MaxIdx, MaxGen, true⟩ st := SafeAlways Declared MaxEpoch MaxIdx MaxGen true
theorem Confinement_SafeAlways (Declared MaxEpoch MaxIdx MaxGen : Nat) :
    ∀ st, Reachable Init (Next ⟨.none, Declared, MaxEpoch, MaxIdx, MaxGen, false⟩) st →
      Safe ⟨.none, Declared, MaxEpoch, MaxIdx, MaxGen, false⟩ st := SafeAlways Declared MaxEpoch MaxIdx MaxGen false

#print axioms ContainedMeansConfinedAlways
#print axioms NoSilentDowngradeAlways
#print axioms ContestedStoppedAlways
#print axioms FreshAppraisalAlways
#print axioms SafeAlways

end Topak.Spec.Confinement
