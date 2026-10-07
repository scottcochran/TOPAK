import TopakSpec.Seats
/-!
# A Seats-shaped model of `State::apply`

`crates/topak-core/src/state.rs` `State::apply` is the replicated state machine. This file models the part of it
that `spec/Seats.tla` (ADR-0037) is about: which seats hold a live lease, for which principal, under which
alphabet, and what was admitted under them. It is a **model**, not a transcription: each arm keeps the checks
and the effects on those fields, and every other check the arm makes is one Boolean, `ok`, that can only refuse.
The model's steps are then every step the code can take, whatever those other checks decide.

What is proved:
- `model_inv`: on every state the model reaches, at any number of seats and principals, a principal holds at
  most one live lease, a seat at most one, every live alphabet is within its seat's kind, and every admitted
  act was within the kind of the seat it was admitted under. No premise beyond the log's (below).
- `model_refines_seats`: at `Seats.tla`'s constants (three seats of the module's kinds, two principals), every
  state the model reaches maps to a state `Seats.Next` at `Mut = "none"` reaches, a model step being a module
  step, a run of `EndRound`s, an `Act` and then an `EndRound` (a terminal act), or a stutter. So
  `Seats_proof.tla`'s two theorems hold of the model (`model_seats_safe`).

What it premises:
- **The log.** `apply` is called at strictly increasing indices (`Next`'s `st.last < index`). `apply_inner` does
  not check this itself; a lease's fence is its log index (ADR-0031 §2), and the consensus layer delivers each
  index once, in order.
- **The model is the code.** Written from the Rust and read against it, and checked against the reference's
  recorded traces by `SeatsReplay.lean` (`seats-replay.sh`), which runs every recorded step through `apply` here
  with `ok` set to whether the reference applied it, and compares the result, the leases, the live index, the
  seat kinds and `last_applied` after it. That is the direction the proofs need: every recorded code step is a
  model step. A test, not a proof. Its first run found a gap: `Submit` and `Vote` end the lease (`terminal`).
- **Where the model reads the state differently.** The Rust finds live leases through `live_by_seat`'s values;
  the model finds them as live records indexed at their own seat (`ends`, `heldElsewhere`). On every state the
  invariant `Indexed` holds of the two sets are equal; the replay checks them on the recorded ones.
- **At the module's constants, no issuance changes a seat's kind** (`INext`). The code allows it:
  `rules::validate_issuance` does not compare the issued seats with the current ones, though `types.rs` says a
  kind is "never changed". `model_inv` needs no such premise, because an issuance ends every live lease
  (`issue_inv`); `Seats.tla`'s `KindOf` is a constant, so the refinement does.

It is not a stage of T-0045-28's chain (ADR-0053 §5, R1): the oracle `ok` stands for most of `apply`.
-/

namespace Topak.SeatsModel
open Topak.Spec

/-! ## The code's types -/

/-- `types.rs` `ActionKind`. -/
inductive ActionKind | Read | Draft | Invoke | Emit | Submit | Vote | Consult | Actuate | Report
  deriving DecidableEq, Repr

def ActionKind.all : List ActionKind := [.Read, .Draft, .Invoke, .Emit, .Submit, .Vote, .Consult, .Actuate, .Report]

theorem ActionKind.mem_all (a : ActionKind) : a ∈ ActionKind.all := by cases a <;> decide

/-- `types.rs` `SeatKind`. -/
inductive SeatKind | Thinker | Observer | Grant | Operator | Emergency
  deriving DecidableEq, Repr

/-- `SeatKind::allows`, ADR-0037 §4 and ADR-0043 §2.
```
SeatKind::Thinker => matches!(k, Read | Draft | Invoke | Emit | Submit | Consult | Actuate | Report),
SeatKind::Observer => matches!(k, Read | Emit | Vote | Consult | Report),
SeatKind::Grant => matches!(k, Read | Emit | Vote),
SeatKind::Operator => false,
SeatKind::Emergency => matches!(k, Consult | Actuate | Report),
``` -/
def SeatKind.allows : SeatKind → ActionKind → Bool
  | .Thinker, .Vote => false
  | .Thinker, _ => true
  | .Observer, k => match k with | .Read | .Emit | .Vote | .Consult | .Report => true | _ => false
  | .Grant, k => match k with | .Read | .Emit | .Vote => true | _ => false
  | .Operator, _ => false
  | .Emergency, k => match k with | .Consult | .Actuate | .Report => true | _ => false

/-- A lease's alphabet, `BTreeSet<ActionKind>`, as its characteristic function. -/
abbrev Alphabet := ActionKind → Bool

/-- `alphabet.iter().find(|k| !kind.allows(**k))` is `None`. -/
def withinKind (α : Alphabet) (k : SeatKind) : Bool := ActionKind.all.all fun a => !α a || k.allows a

/-- `new.alphabet.is_subset(&self.alphabet)`. -/
def subsetOf (α β : Alphabet) : Bool := ActionKind.all.all fun a => !α a || β a

theorem withinKind_spec {α : Alphabet} {k : SeatKind} (h : withinKind α k = true) (a : ActionKind)
    (ha : α a = true) : k.allows a = true := by
  have := List.all_eq_true.mp h a (ActionKind.mem_all a)
  simp [ha] at this; exact this

theorem subsetOf_spec {α β : Alphabet} (h : subsetOf α β = true) (a : ActionKind) (ha : α a = true) :
    β a = true := by
  have := List.all_eq_true.mp h a (ActionKind.mem_all a)
  simp [ha] at this; exact this

set_option linter.unusedSectionVars false

variable {σ π δ : Type} [DecidableEq σ] [DecidableEq π] [DecidableEq δ]

/-- A `LeaseRecord`, as far as the model reads it: its lease's seat, principal, Persona, confinement digest and
alphabet, and whether it has ended (`live() == ended.is_none()`). -/
structure Rec (σ π δ : Type) where
  seat : σ
  principal : π
  persona : δ
  conf : δ
  alphabet : Alphabet
  live : Bool

/-- `state.rs` `RevocationTarget`, and its `matches`. -/
inductive RevTarget (π δ : Type) | principal (p : π) | persona (d : δ) | confinement (d : δ)

def RevTarget.matches : RevTarget π δ → Rec σ π δ → Bool
  | .principal p, r => decide (r.principal = p)
  | .persona d, r => decide (r.persona = d)
  | .confinement d, r => decide (r.conf = d)

/-- The model's state: the issued seats' kinds (`rules.seats[..].kind`), `leases`, `live_by_seat`,
`last_applied`, and `acted`, a history variable: every admitted act with its seat's kind at admission. The
code keeps no such list; the log does, as the `Admit` entries applied `Admitted`. -/
structure MState (σ π δ : Type) where
  kinds : σ → Option SeatKind
  leases : Nat → Option (Rec σ π δ)
  liveBySeat : σ → Option Nat
  last : Nat
  acted : List (ActionKind × Option SeatKind)

/-- The entries, as the model reads them. A `Grant` on either path (unsigned, a `Regrant`'s, an activation's,
which `apply_activate` builds and passes to `apply_grant`) is `grant`; `Revoke`, `Contested` and an operator's
`Revoke` are `revoke`; `EpochIncrement` and `FenceEpoch` are `fence`; an operator's `EndRound` is `endSeat`.
Everything else is `other`: it touches none of the model's fields. -/
inductive MEntry (σ π δ : Type)
  | grant (seat : σ) (principal : π) (persona conf : δ) (alphabet : Alphabet)
  | renew (seat : σ) (fence : Nat) (alphabet : Alphabet)
  | admit (seat : σ) (fence : Nat) (act : ActionKind)
  | endRound (seat : σ) (fence : Nat)
  | endSeat (seat : σ)
  | revoke (target : RevTarget π δ)
  | fence
  | issue (kinds : σ → Option SeatKind)
  | other

/-- `Applied`, coarsened to what the model decides. -/
inductive MApplied | granted (fence : Nat) | renewed (fence : Nat) | admitted | roundEnded | revoked | fenced
  | issued | rejected | unmodelled
  deriving DecidableEq, Repr

/-! ## The arms -/

/-- `end_lease` applied to every fence `P` names, at once. A fence ends when its record is live and is the one
`live_by_seat` holds at its seat; `live_by_seat` loses every entry that ended. -/
def ends (st : MState σ π δ) (P : Nat → Rec σ π δ → Bool) (f : Nat) : Bool :=
  match st.leases f with
  | some r => r.live && decide (st.liveBySeat r.seat = some f) && P f r
  | none => false

def endMany (st : MState σ π δ) (P : Nat → Rec σ π δ → Bool) : MState σ π δ :=
  { st with
    leases := fun f => (st.leases f).map fun r => if ends st P f then { r with live := false } else r
    liveBySeat := fun s => match st.liveBySeat s with
      | some f => if ends st P f then none else some f
      | none => none }

/-- The `apply_grant` check `live_by_seat.values().filter_map(..).find(|r| r.lease.principal == req.principal)`
(ADR-0037 §1): some live lease, indexed at its seat, is the principal's. Fences run to `last`. -/
def heldElsewhere (st : MState σ π δ) (p : π) : Bool :=
  (List.range (st.last + 1)).any fun f =>
    match st.leases f with
    | some r => r.live && decide (st.liveBySeat r.seat = some f) && decide (r.principal = p)
    | none => false

/-- `apply_grant`, the checks on the model's fields in the code's order, then the rest as `ok`:
```
let Some(domain) = self.rules.seat_domain(&req.seat) else { return Rejected(..) };
if self.live_by_seat.contains_key(&req.seat) { return Rejected(..) }
...
let kind = self.rules.seat_kind(&req.seat).expect("declared seat has a kind");
if let Some(k) = req.alphabet.iter().find(|k| !kind.allows(**k)) { return Rejected(..) }
if let Some(other) = self.live_by_seat.values().filter_map(|f| self.leases.get(f))
    .find(|r| r.lease.principal == req.principal) { return Rejected(..) }
...
self.leases.insert(index, LeaseRecord { lease, ended: None, .. });
self.live_by_seat.insert(req.seat.clone(), index);
``` -/
def applyGrant (st : MState σ π δ) (index : Nat) (seat : σ) (p : π) (persona conf : δ) (α : Alphabet)
    (ok : Bool) : MState σ π δ × MApplied :=
  match st.kinds seat with
  | none => (st, .rejected)
  | some k =>
    if (st.liveBySeat seat).isSome then (st, .rejected)
    else if !withinKind α k then (st, .rejected)
    else if heldElsewhere st p then (st, .rejected)
    else if !ok then (st, .rejected)
    else ({ st with leases := upd st.leases index (some ⟨seat, p, persona, conf, α, true⟩)
                    liveBySeat := upd st.liveBySeat seat (some index) }, .granted index)

/-- `apply_renew`:
```
let Some(old) = self.leases.get(&req.fence) else { return Rejected(..) };
if old.lease.seat != req.seat || !old.live() { return Rejected(..) }
...  // check_renewal: `new.alphabet.is_subset(&self.alphabet)`, and the rest
let rec = LeaseRecord { lease: new, attestation, ..old.clone() };
self.leases.get_mut(&old_fence).ended = Some(EndReason::Renewed);
self.leases.insert(index, rec);
self.live_by_seat.insert(req.seat.clone(), index);
``` -/
def applyRenew (st : MState σ π δ) (index : Nat) (seat : σ) (fence : Nat) (α : Alphabet) (ok : Bool) :
    MState σ π δ × MApplied :=
  match st.leases fence with
  | none => (st, .rejected)
  | some old =>
    if decide (old.seat = seat) && old.live && subsetOf α old.alphabet && ok then
      ({ st with leases := upd (upd st.leases fence (some { old with live := false })) index
                             (some { old with alphabet := α })
                 liveBySeat := upd st.liveBySeat seat (some index) }, .renewed index)
    else (st, .rejected)

/-- `Submit` is terminal for the authoring round and `Vote` for the voter's promotion round (`EndReason::Submitted`,
`Voted`). -/
def terminal : ActionKind → Bool
  | .Submit | .Vote => true
  | _ => false

/-- The admit's act, recorded. -/
def admitted (st : MState σ π δ) (seat : σ) (a : ActionKind) : MState σ π δ :=
  { st with acted := (a, st.kinds seat) :: st.acted }

/-- `apply_admit`, through `check_live`: the lease exists, is the seat's, has not ended, and the act's kind is
in its alphabet (`rec.lease.alphabet.contains(&kind)`). Its effect on the model's fields is `acted`, and, for a
terminal act, the end of the lease:
```
Admitted::Submit { artifact } => { ..; self.end_lease(fence, EndReason::Submitted); }
Admitted::Vote { .. } => { ..; self.end_lease(fence, EndReason::Voted); }
``` -/
def applyAdmit (st : MState σ π δ) (seat : σ) (fence : Nat) (a : ActionKind) (ok : Bool) :
    MState σ π δ × MApplied :=
  match st.leases fence with
  | none => (st, .rejected)
  | some r =>
    if decide (r.seat = seat) && r.live && r.alphabet a && ok then
      (if terminal a then endMany (admitted st seat a) (fun g _ => g == fence) else admitted st seat a, .admitted)
    else (st, .rejected)

/-- The arms of `apply_inner` and `apply_control` that touch the model's fields. `EndRound`:
`Some(r) if &r.lease.seat == seat && r.live() => self.end_lease(*fence, *reason)`. An operator's `EndRound`:
`match self.live_by_seat.get(target) { Some(fence) => self.end_lease(fence, ..) .. }`. `Revoke`: every live
lease the target matches. `EpochIncrement`, `FenceEpoch`: `end_all_live`. `Issue`: the new rules, then
`end_all_live`. -/
def applyArm (st : MState σ π δ) (index : Nat) (ok : Bool) : MEntry σ π δ → MState σ π δ × MApplied
  | .grant seat p persona conf α => applyGrant st index seat p persona conf α ok
  | .renew seat fence α => applyRenew st index seat fence α ok
  | .admit seat fence a => applyAdmit st seat fence a ok
  | .endRound seat fence =>
    match st.leases fence with
    | some r => if decide (r.seat = seat) && r.live && ok then (endMany st fun g _ => g == fence, .roundEnded)
                else (st, .rejected)
    | none => (st, .rejected)
  | .endSeat seat =>
    match st.liveBySeat seat with
    | some f => if ok then (endMany st fun g _ => g == f, .roundEnded) else (st, .rejected)
    | none => (st, .rejected)
  | .revoke t => if ok then (endMany st fun _ r => t.matches r, .revoked) else (st, .rejected)
  | .fence => if ok then (endMany st fun _ _ => true, .fenced) else (st, .rejected)
  | .issue ks => if ok then ({ endMany st (fun _ _ => true) with kinds := ks }, .issued) else (st, .rejected)
  | .other => if ok then (st, .unmodelled) else (st, .rejected)

/-- `State::apply` at log index `index`: `self.last_applied = index`, then the arm. -/
def apply (st : MState σ π δ) (index : Nat) (e : MEntry σ π δ) (ok : Bool) : MState σ π δ × MApplied :=
  let r := applyArm st index ok e
  ({ r.1 with last := index }, r.2)

/-! ## The model as a transition system -/

/-- A fresh `State`: no lease, nothing indexed, nothing admitted. The rules and `last_applied` are anything. -/
def Init (st : MState σ π δ) : Prop :=
  st.leases = (fun _ => none) ∧ st.liveBySeat = (fun _ => none) ∧ st.acted = []

/-- One applied entry, at an index past the last, whatever the checks the model leaves out decide. -/
def Next (st st' : MState σ π δ) : Prop :=
  ∃ index e ok, st.last < index ∧ st' = (apply st index e ok).1

/-! ## The invariant -/

/-- `live_by_seat` indexes exactly the live records, each at its own seat. -/
def Indexed (st : MState σ π δ) : Prop :=
  (∀ s f, st.liveBySeat s = some f → ∃ r, st.leases f = some r ∧ r.seat = s ∧ r.live = true) ∧
  (∀ f r, st.leases f = some r → r.live = true → st.liveBySeat r.seat = some f)

/-- No fence is past `last_applied`. -/
def Fenced (st : MState σ π δ) : Prop := ∀ f r, st.leases f = some r → f ≤ st.last

/-- ADR-0037 §4: a live alphabet is within its seat's kind. -/
def AlphabetsWithinKind (st : MState σ π δ) : Prop :=
  ∀ f r, st.leases f = some r → r.live = true →
    ∃ k, st.kinds r.seat = some k ∧ ∀ a, r.alphabet a = true → k.allows a = true

/-- ADR-0037 §4, of what happened: every admitted act was within the kind of the seat it was admitted under. -/
def ActedWithinKind (st : MState σ π δ) : Prop :=
  ∀ x, x ∈ st.acted → ∃ k, x.2 = some k ∧ k.allows x.1 = true

/-- ADR-0037 §1: two live leases are two principals. -/
def OnePrincipalOneLease (st : MState σ π δ) : Prop :=
  ∀ f g r r', st.leases f = some r → st.leases g = some r' → r.live = true → r'.live = true → f ≠ g →
    r.principal ≠ r'.principal

def Inv (st : MState σ π δ) : Prop :=
  Indexed st ∧ Fenced st ∧ AlphabetsWithinKind st ∧ ActedWithinKind st ∧ OnePrincipalOneLease st

theorem init_inv (st : MState σ π δ) (h : Init st) : Inv st := by
  obtain ⟨hl, hb, ha⟩ := h
  refine ⟨⟨?_, ?_⟩, ?_, ?_, ?_, ?_⟩
  · intro s f h; rw [hb] at h; cases h
  · intro f r h; rw [hl] at h; cases h
  · intro f r h; rw [hl] at h; cases h
  · intro f r h; rw [hl] at h; cases h
  · intro x hx; rw [ha] at hx; cases hx
  · intro f g r r' h; rw [hl] at h; cases h

/-- Moving `last_applied` forward keeps the invariant. -/
theorem inv_last {st : MState σ π δ} (hi : Inv st) {n : Nat} (h : st.last ≤ n) : Inv { st with last := n } := by
  obtain ⟨hI, hF, hA, hD, hO⟩ := hi
  exact ⟨hI, fun f r hr => Nat.le_trans (hF f r hr) h, hA, hD, hO⟩

/-! ### Ending leases -/

theorem endMany_leases (st : MState σ π δ) (P) (f : Nat) :
    (endMany st P).leases f = (st.leases f).map fun r => if ends st P f then { r with live := false } else r :=
  rfl

/-- A record live after `endMany` was live before, and is the same record. -/
theorem endMany_live {st : MState σ π δ} {P f r} (h : (endMany st P).leases f = some r) (hl : r.live = true) :
    st.leases f = some r ∧ ends st P f = false := by
  rw [endMany_leases] at h
  cases hf : st.leases f with
  | none => simp [hf] at h
  | some r0 =>
    rw [hf] at h
    cases he : ends st P f
    · simp [he] at h; subst h; exact ⟨rfl, rfl⟩
    · simp [he] at h; subst h; simp at hl

theorem endMany_some {st : MState σ π δ} {P f r} (h : (endMany st P).leases f = some r) :
    ∃ r0, st.leases f = some r0 := by
  rw [endMany_leases] at h
  cases hf : st.leases f with
  | none => simp [hf] at h
  | some r0 => exact ⟨r0, rfl⟩

theorem endMany_lbs {st : MState σ π δ} {P s f} (h : (endMany st P).liveBySeat s = some f) :
    st.liveBySeat s = some f ∧ ends st P f = false := by
  simp only [endMany] at h
  cases hs : st.liveBySeat s with
  | none => simp [hs] at h
  | some g =>
    rw [hs] at h
    cases he : ends st P g
    · simp [he] at h; subst h; exact ⟨rfl, he⟩
    · simp [he] at h

theorem endMany_inv (st : MState σ π δ) (P) (hi : Inv st) : Inv (endMany st P) := by
  obtain ⟨⟨hI1, hI2⟩, hF, hA, hD, hO⟩ := hi
  refine ⟨⟨?_, ?_⟩, ?_, ?_, ?_, ?_⟩
  · intro s f h
    obtain ⟨hs, he⟩ := endMany_lbs h
    obtain ⟨r, hr, hseat, hlive⟩ := hI1 s f hs
    refine ⟨r, ?_, hseat, hlive⟩
    rw [endMany_leases, hr]; simp [he]
  · intro f r h hl
    obtain ⟨h0, he⟩ := endMany_live h hl
    have hb := hI2 f r h0 hl
    show (match st.liveBySeat r.seat with | some f => if ends st P f then none else some f | none => none) = _
    rw [hb]; simp [he]
  · intro f r h
    obtain ⟨r0, h0⟩ := endMany_some h
    exact hF f r0 h0
  · intro f r h hl
    exact hA f r (endMany_live h hl).1 hl
  · exact hD
  · intro f g r r' h h' hl hl' hfg
    exact hO f g r r' (endMany_live h hl).1 (endMany_live h' hl').1 hl hl' hfg

/-- After ending everything, nothing is indexed and nothing is live. -/
theorem endAll_none (st : MState σ π δ) (hi : Inv st) (s : σ) :
    (endMany st fun _ _ => true).liveBySeat s = none := by
  cases h : (endMany st fun _ _ => true).liveBySeat s with
  | none => rfl
  | some f =>
    exfalso
    obtain ⟨hs, he⟩ := endMany_lbs h
    obtain ⟨r, hr, hseat, hlive⟩ := hi.1.1 s f hs
    simp [ends, hr, hlive, hseat, hs] at he

theorem endAll_dead (st : MState σ π δ) (hi : Inv st) (f : Nat) (r : Rec σ π δ)
    (h : (endMany st fun _ _ => true).leases f = some r) : r.live = false := by
  cases hl : r.live
  · rfl
  · exfalso
    obtain ⟨h0, he⟩ := endMany_live h hl
    have hb := hi.1.2 f r h0 hl
    simp [ends, h0, hl, hb] at he

/-! ### Every step keeps the invariant -/

theorem heldElsewhere_false {st : MState σ π δ} {p : π} (hh : heldElsewhere st p = false) (hF : Fenced st)
    (hI2 : ∀ f r, st.leases f = some r → r.live = true → st.liveBySeat r.seat = some f)
    (f : Nat) (r : Rec σ π δ) (hr : st.leases f = some r) (hl : r.live = true) : r.principal ≠ p := by
  intro hp
  have hmem : f ∈ List.range (st.last + 1) := List.mem_range.mpr (Nat.lt_succ_of_le (hF f r hr))
  have := List.any_eq_false.mp hh f hmem
  simp [hr, hl, hI2 f r hr hl, hp] at this


/-! ### What each arm does -/

theorem applyGrant_cases (st : MState σ π δ) (index : Nat) (seat : σ) (p : π) (persona conf : δ) (α : Alphabet)
    (ok : Bool) :
    applyGrant st index seat p persona conf α ok = (st, .rejected) ∨
    ∃ k, st.kinds seat = some k ∧ st.liveBySeat seat = none ∧ withinKind α k = true ∧
      heldElsewhere st p = false ∧
      applyGrant st index seat p persona conf α ok =
        ({ st with leases := upd st.leases index (some ⟨seat, p, persona, conf, α, true⟩),
                   liveBySeat := upd st.liveBySeat seat (some index) }, .granted index) := by
  unfold applyGrant
  split
  · exact Or.inl rfl
  · rename_i k hk
    split
    · exact Or.inl rfl
    · split
      · exact Or.inl rfl
      · split
        · exact Or.inl rfl
        · split
          · exact Or.inl rfl
          · right
            refine ⟨k, hk, ?_, ?_, ?_, rfl⟩ <;> simp_all

theorem applyRenew_cases (st : MState σ π δ) (index : Nat) (seat : σ) (fence : Nat) (α : Alphabet) (ok : Bool) :
    applyRenew st index seat fence α ok = (st, .rejected) ∨
    ∃ old, st.leases fence = some old ∧ old.seat = seat ∧ old.live = true ∧ subsetOf α old.alphabet = true ∧
      applyRenew st index seat fence α ok =
        ({ st with leases := upd (upd st.leases fence (some { old with live := false })) index
                               (some { old with alphabet := α }),
                   liveBySeat := upd st.liveBySeat seat (some index) }, .renewed index) := by
  unfold applyRenew
  split
  · exact Or.inl rfl
  · rename_i old hold
    split
    · rename_i hc
      simp only [Bool.and_eq_true, decide_eq_true_eq] at hc
      exact Or.inr ⟨old, hold, hc.1.1.1, hc.1.1.2, hc.1.2, rfl⟩
    · exact Or.inl rfl

theorem applyAdmit_cases (st : MState σ π δ) (seat : σ) (fence : Nat) (a : ActionKind) (ok : Bool) :
    applyAdmit st seat fence a ok = (st, .rejected) ∨
    ∃ r, st.leases fence = some r ∧ r.seat = seat ∧ r.live = true ∧ r.alphabet a = true ∧
      applyAdmit st seat fence a ok =
        (if terminal a then endMany (admitted st seat a) (fun g _ => g == fence) else admitted st seat a,
          .admitted) := by
  unfold applyAdmit
  split
  · exact Or.inl rfl
  · rename_i r hr
    split
    · rename_i hc
      simp only [Bool.and_eq_true, decide_eq_true_eq] at hc
      exact Or.inr ⟨r, hr, hc.1.1.1, hc.1.1.2, hc.1.2, rfl⟩
    · exact Or.inl rfl

section steps
variable (st : MState σ π δ) (index : Nat) (ok : Bool)

/-- A refused entry moves `last_applied` and nothing else. -/
theorem rej_inv (hi : Inv st) (hidx : st.last < index) : Inv { st with last := index } :=
  inv_last hi (Nat.le_of_lt hidx)

theorem fresh_of {st : MState σ π δ} {index : Nat} (hF : Fenced st) (hidx : st.last < index) :
    ∀ f r, st.leases f = some r → f ≠ index := fun f r h hf => by
  have := hF f r h; omega

theorem grant_inv (seat p persona conf α) (hi : Inv st) (hidx : st.last < index) :
    Inv (apply st index (.grant seat p persona conf α) ok).1 := by
  have hrej := rej_inv st index hi hidx
  obtain ⟨⟨hI1, hI2⟩, hF, hA, hD, hO⟩ := hi
  have fresh := fresh_of hF hidx
  simp only [apply, applyArm]
  rcases applyGrant_cases st index seat p persona conf α ok with h | ⟨k, hk, hlb, hw, hh, happ⟩
  · rw [h]; exact hrej
  rw [happ]
  show Inv { st with leases := upd st.leases index (some ⟨seat, p, persona, conf, α, true⟩),
                     liveBySeat := upd st.liveBySeat seat (some index), last := index }
  refine ⟨⟨?_, ?_⟩, ?_, ?_, ?_, ?_⟩
  · intro s f h
    simp only at h ⊢
    by_cases hs : s = seat
    · subst hs; rw [upd_same] at h; cases h; exact ⟨_, upd_same _ _ _, rfl, rfl⟩
    · rw [upd_other _ _ _ _ hs] at h
      obtain ⟨r, hr, hseat, hlive⟩ := hI1 s f h
      refine ⟨r, ?_, hseat, hlive⟩
      rw [upd_other _ _ _ _ (fresh f r hr)]; exact hr
  · intro f r h hl
    simp only at h ⊢
    by_cases hf : f = index
    · subst hf; rw [upd_same] at h; cases h; exact upd_same _ _ _
    · rw [upd_other _ _ _ _ hf] at h
      have hb := hI2 f r h hl
      have hne : r.seat ≠ seat := fun he => by rw [he, hlb] at hb; cases hb
      rw [upd_other _ _ _ _ hne]; exact hb
  · intro f r h
    simp only at h ⊢
    by_cases hf : f = index
    · omega
    · rw [upd_other _ _ _ _ hf] at h; have := hF f r h; omega
  · intro f r h hl
    simp only at h ⊢
    by_cases hf : f = index
    · subst hf; rw [upd_same] at h; cases h
      exact ⟨k, hk, fun a ha => withinKind_spec hw a ha⟩
    · rw [upd_other _ _ _ _ hf] at h; exact hA f r h hl
  · exact hD
  · intro f g r r' h h' hl hl' hfg
    simp only at h h'
    by_cases hf : f = index
    · subst hf
      rw [upd_same] at h; cases h
      rw [upd_other _ _ _ _ (Ne.symm hfg)] at h'
      exact fun he => heldElsewhere_false hh hF hI2 g r' h' hl' he.symm
    · rw [upd_other _ _ _ _ hf] at h
      by_cases hg : g = index
      · subst hg
        rw [upd_same] at h'; cases h'
        exact heldElsewhere_false hh hF hI2 f r h hl
      · rw [upd_other _ _ _ _ hg] at h'
        exact hO f g r r' h h' hl hl' hfg

theorem renew_inv (seat fence α) (hi : Inv st) (hidx : st.last < index) :
    Inv (apply st index (.renew seat fence α) ok).1 := by
  have hrej := rej_inv st index hi hidx
  obtain ⟨⟨hI1, hI2⟩, hF, hA, hD, hO⟩ := hi
  have fresh := fresh_of hF hidx
  simp only [apply, applyArm]
  rcases applyRenew_cases st index seat fence α ok with h | ⟨old, hfo, hseat, hlive, hsub, happ⟩
  · rw [h]; exact hrej
  rw [happ]
  have hbo : st.liveBySeat seat = some fence := hseat ▸ hI2 fence old hfo hlive
  have hfi : fence ≠ index := fresh fence old hfo
  show Inv { st with leases := upd (upd st.leases fence (some { old with live := false })) index
                                 (some { old with alphabet := α }),
                     liveBySeat := upd st.liveBySeat seat (some index), last := index }
  -- the records after: the new one at `index`, the old one ended, the rest as they were
  have L : ∀ f, f ≠ index → f ≠ fence →
      upd (upd st.leases fence (some { old with live := false })) index (some { old with alphabet := α }) f
        = st.leases f := fun f h1 h2 => by rw [upd_other _ _ _ _ h1, upd_other _ _ _ _ h2]
  refine ⟨⟨?_, ?_⟩, ?_, ?_, ?_, ?_⟩
  · intro s f h
    simp only at h ⊢
    by_cases hs : s = seat
    · subst hs; rw [upd_same] at h; cases h
      exact ⟨_, upd_same _ _ _, hseat, hlive⟩
    · rw [upd_other _ _ _ _ hs] at h
      obtain ⟨r, hr, hrs, hrl⟩ := hI1 s f h
      have hff : f ≠ fence := fun he => by subst he; rw [hfo] at hr; cases hr; exact hs (hrs.symm.trans hseat)
      exact ⟨r, (L f (fresh f r hr) hff).trans hr, hrs, hrl⟩
  · intro f r h hl
    simp only at h ⊢
    by_cases hf : f = index
    · subst hf; rw [upd_same] at h; cases h; simp only; rw [hseat]; exact upd_same _ _ _
    · by_cases hff : f = fence
      · subst hff; rw [upd_other _ _ _ _ hf, upd_same] at h; cases h; simp at hl
      · rw [L f hf hff] at h
        have hb := hI2 f r h hl
        have hne : r.seat ≠ seat := fun he => by rw [he, hbo] at hb; cases hb; exact hff rfl
        rw [upd_other _ _ _ _ hne]; exact hb
  · intro f r h
    simp only at h ⊢
    by_cases hf : f = index
    · omega
    · by_cases hff : f = fence
      · have := hF fence old hfo; omega
      · rw [L f hf hff] at h; have := hF f r h; omega
  · intro f r h hl
    simp only at h ⊢
    by_cases hf : f = index
    · subst hf; rw [upd_same] at h; cases h
      obtain ⟨k, hk, hka⟩ := hA fence old hfo hlive
      exact ⟨k, hk, fun a ha => hka a (subsetOf_spec hsub a ha)⟩
    · by_cases hff : f = fence
      · subst hff; rw [upd_other _ _ _ _ hf, upd_same] at h; cases h; simp at hl
      · rw [L f hf hff] at h; exact hA f r h hl
  · exact hD
  · -- the new record is the old one's principal, and the old one has ended
    have cases_of : ∀ f r, upd (upd st.leases fence (some { old with live := false })) index
          (some { old with alphabet := α }) f = some r → r.live = true →
          (f = index ∧ r = { old with alphabet := α }) ∨ (f ≠ index ∧ f ≠ fence ∧ st.leases f = some r) := by
      intro f r h hl
      by_cases hf : f = index
      · subst hf; rw [upd_same] at h; cases h; exact Or.inl ⟨rfl, rfl⟩
      · by_cases hff : f = fence
        · subst hff; rw [upd_other _ _ _ _ hf, upd_same] at h; cases h; simp at hl
        · exact Or.inr ⟨hf, hff, (L f hf hff).symm.trans h⟩
    intro f g r r' h h' hl hl' hfg
    simp only at h h'
    rcases cases_of f r h hl with ⟨hf, rfl⟩ | ⟨hf, hff, h0⟩ <;>
      rcases cases_of g r' h' hl' with ⟨hg, rfl⟩ | ⟨hg, hgf, h0'⟩
    · exact absurd (hf.trans hg.symm) hfg
    · exact hO fence g old r' hfo h0' hlive hl' (Ne.symm hgf)
    · exact hO f fence r old h0 hfo hl hlive hff
    · exact hO f g r r' h0 h0' hl hl' hfg

/-- The act recorded, before a terminal act ends the lease. -/
theorem admitted_inv {st : MState σ π δ} {seat fence a r} (hi : Inv st) (hfo : st.leases fence = some r)
    (hseat : r.seat = seat) (hlive : r.live = true) (ha : r.alphabet a = true) : Inv (admitted st seat a) := by
  obtain ⟨⟨hI1, hI2⟩, hF, hA, hD, hO⟩ := hi
  refine ⟨⟨hI1, hI2⟩, hF, hA, ?_, hO⟩
  intro x hx
  simp only [admitted, List.mem_cons] at hx
  rcases hx with rfl | hx
  · obtain ⟨k, hk, hka⟩ := hA fence r hfo hlive
    exact ⟨k, hseat ▸ hk, hka a ha⟩
  · exact hD x hx

theorem admit_inv (seat fence a) (hi : Inv st) (hidx : st.last < index) :
    Inv (apply st index (.admit seat fence a) ok).1 := by
  have hrej := rej_inv st index hi hidx
  simp only [apply, applyArm]
  rcases applyAdmit_cases st seat fence a ok with h | ⟨r, hfo, hseat, hlive, ha, happ⟩
  · rw [h]; exact hrej
  rw [happ]
  have h1 := admitted_inv hi hfo hseat hlive ha
  cases terminal a
  · exact inv_last h1 (Nat.le_of_lt hidx)
  · exact inv_last (endMany_inv _ _ h1) (Nat.le_of_lt hidx)

theorem endMany_step_inv (P) (hi : Inv st) (hidx : st.last < index) :
    Inv { endMany st P with last := index } :=
  inv_last (endMany_inv st P hi) (Nat.le_of_lt hidx)

theorem issue_inv (ks) (hi : Inv st) (hidx : st.last < index) :
    Inv (apply st index (.issue ks) ok).1 := by
  have hrej := rej_inv st index hi hidx
  simp only [apply, applyArm]
  cases ok
  · exact hrej
  have he := endMany_step_inv st index (fun _ _ => true) hi hidx
  obtain ⟨-, hF, -, hD, -⟩ := he
  refine ⟨⟨?_, ?_⟩, hF, ?_, hD, ?_⟩
  · intro s f h
    have h' : (endMany st fun _ _ => true).liveBySeat s = some f := h
    rw [endAll_none st hi s] at h'; cases h'
  · intro f r h hl
    have h' : (endMany st fun _ _ => true).leases f = some r := h
    rw [endAll_dead st hi f r h'] at hl; cases hl
  · intro f r h hl
    have h' : (endMany st fun _ _ => true).leases f = some r := h
    rw [endAll_dead st hi f r h'] at hl; cases hl
  · intro f g r r' h _ hl
    have h' : (endMany st fun _ _ => true).leases f = some r := h
    rw [endAll_dead st hi f r h'] at hl; cases hl

theorem step_inv (e : MEntry σ π δ) (hi : Inv st) (hidx : st.last < index) :
    Inv (apply st index e ok).1 := by
  have hrej := rej_inv st index hi hidx
  have hend := fun P => endMany_step_inv st index P hi hidx
  cases e with
  | grant seat p persona conf α => exact grant_inv st index ok seat p persona conf α hi hidx
  | renew seat fence α => exact renew_inv st index ok seat fence α hi hidx
  | admit seat fence a => exact admit_inv st index ok seat fence a hi hidx
  | issue ks => exact issue_inv st index ok ks hi hidx
  | endRound seat fence =>
    simp only [apply, applyArm]
    split
    · split
      · exact hend _
      · exact hrej
    · exact hrej
  | endSeat seat =>
    simp only [apply, applyArm]
    split
    · split
      · exact hend _
      · exact hrej
    · exact hrej
  | revoke t => simp only [apply, applyArm]; split <;> first | exact hend _ | exact hrej
  | fence => simp only [apply, applyArm]; split <;> first | exact hend _ | exact hrej
  | other => simp only [apply, applyArm]; split <;> exact hrej

end steps

/-- **The model's invariant**, at any number of seats and principals, whatever the checks it leaves out decide. -/
theorem model_inv : ∀ st : MState σ π δ, Reachable Init Next st → Inv st :=
  invariant Inv Inv init_inv
    (fun st _ hi ⟨index, e, ok, hidx, he⟩ => he ▸ step_inv st index ok e hi hidx) (fun _ h => h)

/-- ADR-0037 §1 of the model: two seats with live leases are held by two principals. -/
theorem model_one_seat_per_principal (st : MState σ π δ) (h : Reachable Init Next st) (s t : σ) (f g : Nat)
    (r r' : Rec σ π δ) (hst : s ≠ t) (hs : st.liveBySeat s = some f) (ht : st.liveBySeat t = some g)
    (hr : st.leases f = some r) (hr' : st.leases g = some r') : r.principal ≠ r'.principal := by
  obtain ⟨⟨hI1, -⟩, -, -, -, hO⟩ := model_inv st h
  obtain ⟨r1, h1, hs1, hl1⟩ := hI1 s f hs
  obtain ⟨r2, h2, hs2, hl2⟩ := hI1 t g ht
  rw [hr] at h1; cases h1
  rw [hr'] at h2; cases h2
  exact hO f g r r' hr hr' hl1 hl2 fun hfg => by subst hfg; rw [hr] at hr'; cases hr'; exact hst (hs1.symm.trans hs2)

/-- ADR-0037 §4 of the model: every admitted act was within its seat's kind. -/
theorem model_acted_within_kind (st : MState σ π δ) (h : Reachable Init Next st) : ActedWithinKind st :=
  (model_inv st h).2.2.2.1

/-! ## The model refines `Seats.tla` at the module's constants

Three seats of the module's kinds, `s1` a thinker, `s2` an observer, `s3` a grant seat; two principals. The code's
nine action kinds are read as the module's four by `actMap`: what reads (`Read`, `Consult`), what authors (`Draft`,
`Invoke`, `Submit`, `Actuate`), what emits (`Emit`, `Report`) and `Vote`. Under it each kind's `allows` is exactly
the module's `KindBound` (`allows_image`). A live lease's alphabet is read as its seat's kind bound, which is the
alphabet the module issues; the code may issue less (`withinKind`), never more. -/

namespace Inst
open Topak.Spec.Seats (Seat Principal Kind KindOf KindBound NoLease LeaseRec ActRec)

def codeKind : Kind → SeatKind
  | .thinker => .Thinker
  | .observer => .Observer
  | .grant => .Grant

theorem codeKind_inj {a b : Kind} (h : codeKind a = codeKind b) : a = b := by
  cases a <;> cases b <;> first | rfl | cases h

/-- The issued seats at the module's constants: `KindOf`, as the code's kinds. -/
def kindsI : Seat → Option SeatKind := fun s => some (codeKind (KindOf s))

def actMap : ActionKind → Seats.Act
  | .Read | .Consult => .Read
  | .Draft | .Invoke | .Submit | .Actuate => .Draft
  | .Emit | .Report => .Emit
  | .Vote => .Vote

/-- What a kind allows, read through `actMap`, is within the module's `KindBound`. -/
theorem allows_bound (K : Kind) (a : ActionKind) (h : (codeKind K).allows a = true) : actMap a ∈ KindBound K := by
  cases K <;> cases a <;> simp_all [codeKind, SeatKind.allows, actMap, KindBound]

/-- And it is all of it: every act of the bound is some allowed kind's image. -/
theorem allows_image (K : Kind) (b : Seats.Act) (h : b ∈ KindBound K) :
    ∃ a, (codeKind K).allows a = true ∧ actMap a = b := by
  cases K <;> cases b <;> simp_all [KindBound] <;>
    first
    | exact ⟨.Read, rfl, rfl⟩ | exact ⟨.Draft, rfl, rfl⟩ | exact ⟨.Emit, rfl, rfl⟩ | exact ⟨.Vote, rfl, rfl⟩

variable {δ : Type} [DecidableEq δ]

abbrev IState (δ : Type) := MState Seat Principal δ

/-- The abstraction: seat `s` holds a live lease when `live_by_seat` indexes one there, for its principal, under
its kind's bound; `acted` is every admitted act, read through `actMap`, with the kind it was admitted under. -/
def absOf (s : Seat) : Option (Rec Seat Principal δ) → LeaseRec
  | some r => ⟨True, some r.principal, KindBound (KindOf s)⟩
  | none => NoLease

def absLease (st : IState δ) (s : Seat) : LeaseRec := absOf s ((st.liveBySeat s).bind st.leases)

def abs (st : IState δ) : Seats.State :=
  ⟨absLease st, fun ar => ∃ x, x ∈ st.acted ∧ actMap x.1 = ar.act ∧ x.2 = some (codeKind ar.kind)⟩

theorem absLease_of {st : IState δ} {s f r} (hs : st.liveBySeat s = some f) (hr : st.leases f = some r) :
    absLease st s = ⟨True, some r.principal, KindBound (KindOf s)⟩ := by
  simp [absLease, hs, hr, absOf]

theorem absLease_none {st : IState δ} {s} (hs : st.liveBySeat s = none) : absLease st s = NoLease := by
  simp [absLease, hs, absOf]

theorem absLease_dangling {st : IState δ} {s f} (hs : st.liveBySeat s = some f) (hr : st.leases f = none) :
    absLease st s = NoLease := by
  simp [absLease, hs, hr, absOf]

/-- `absLease` reads `live_by_seat` at `s` and `leases` at what it holds there, and nothing else. -/
theorem absLease_congr {st st' : IState δ} {s} (hs : st'.liveBySeat s = st.liveBySeat s)
    (hr : ∀ f, st.liveBySeat s = some f → st'.leases f = st.leases f) : absLease st' s = absLease st s := by
  cases h : st.liveBySeat s with
  | none => rw [absLease_none (hs.trans h), absLease_none h]
  | some f =>
    have h' := hs.trans h
    cases hr0 : st.leases f with
    | none => rw [absLease_dangling h' ((hr f h).trans hr0), absLease_dangling h hr0]
    | some r => rw [absLease_of h' ((hr f h).trans hr0), absLease_of h hr0]

def IInit (st : IState δ) : Prop := Init st ∧ st.kinds = kindsI

/-- A model step that issues no new seat kinds: the module's `KindOf` is a constant. -/
def INext (st st' : IState δ) : Prop := Next st st' ∧ st'.kinds = st.kinds

/-- A run of module steps. -/
inductive Steps {α : Type} (R : α → α → Prop) : α → α → Prop
  | refl (a : α) : Steps R a a
  | tail {a b c : α} : Steps R a b → R b c → Steps R a c

theorem Steps.single {α : Type} {R : α → α → Prop} {a b : α} (h : R a b) : Steps R a b := .tail (.refl a) h

theorem Steps.trans {α : Type} {R : α → α → Prop} {a b c : α} (h1 : Steps R a b) (h2 : Steps R b c) :
    Steps R a c := by
  induction h2 with
  | refl => exact h1
  | tail _ hn ih => exact .tail ih hn

theorem reach_steps {α : Type} {I : α → Prop} {N : α → α → Prop} {a b : α} (ha : Reachable I N a)
    (h : Steps N a b) : Reachable I N b := by
  induction h with
  | refl => exact ha
  | tail _ hn ih => exact .step ih hn

/-! ### Ending several seats is a run of `EndRound`s -/

/-- The module state with the seats `E` names reset to `NoLease`. -/
def endSet (S : Seats.State) (E : Seat → Bool) : Seats.State :=
  ⟨fun s => if E s then NoLease else S.lease s, S.acted⟩

theorem endOne (S : Seats.State) (s : Seat) (b : Bool) (h : b = true → (S.lease s).live) :
    Steps (Seats.Next .none) S (if b then ⟨upd S.lease s NoLease, S.acted⟩ else S) := by
  cases b
  · exact .refl S
  · exact .single ⟨s, Or.inr (Or.inl ⟨h rfl, rfl, rfl⟩)⟩

theorem endSet_steps (S : Seats.State) (E : Seat → Bool) (hE : ∀ s, E s = true → (S.lease s).live) :
    Steps (Seats.Next .none) S (endSet S E) := by
  -- end `s1`, then `s2`, then `s3`, each only where `E` names it
  have step : ∀ (L : Seat → LeaseRec) (s : Seat), (E s = true → (L s).live) →
      Steps (Seats.Next .none) ⟨L, S.acted⟩ ⟨if E s = true then upd L s NoLease else L, S.acted⟩ := by
    intro L s h
    cases hEs : E s
    · rw [if_neg (by simp)]; exact .refl _
    · rw [if_pos rfl]; exact .single ⟨s, Or.inr (Or.inl ⟨h hEs, rfl, rfl⟩)⟩
  let L1 : Seat → LeaseRec := if E .s1 = true then upd S.lease .s1 NoLease else S.lease
  let L2 : Seat → LeaseRec := if E .s2 = true then upd L1 .s2 NoLease else L1
  let L3 : Seat → LeaseRec := if E .s3 = true then upd L2 .s3 NoLease else L2
  have l1 : ∀ t, t ≠ .s1 → L1 t = S.lease t := by
    intro t ht; simp only [L1]; split <;> simp [upd, ht]
  have l2 : ∀ t, t ≠ .s2 → L2 t = L1 t := by
    intro t ht; simp only [L2]; split <;> simp [upd, ht]
  have s1 := step S.lease .s1 (hE .s1)
  have s2 := step L1 .s2 fun h => (l1 .s2 (by decide)).symm ▸ hE .s2 h
  have s3 := step L2 .s3 fun h => ((l2 .s3 (by decide)).trans (l1 .s3 (by decide))).symm ▸ hE .s3 h
  have heq : (⟨L3, S.acted⟩ : Seats.State) = endSet S E := by
    show (⟨L3, S.acted⟩ : Seats.State) = ⟨fun s => if E s then NoLease else S.lease s, S.acted⟩
    congr 1
    funext t
    simp only [L3, L2, L1]
    cases e1 : E .s1 <;> cases e2 : E .s2 <;> cases e3 : E .s3 <;> cases t <;> simp [upd, e1, e2, e3]
  exact heq ▸ (s1.trans s2).trans s3

/-! ### Each model step is module steps -/

theorem abs_last (st : IState δ) (n : Nat) : abs { st with last := n } = abs st := rfl

/-- Whether `endMany` ends the lease seat `s` holds. -/
def endsAt (st : IState δ) (P : Nat → Rec Seat Principal δ → Bool) (s : Seat) : Bool :=
  match st.liveBySeat s with
  | some f => ends st P f
  | none => false

theorem abs_endMany (st : IState δ) (P) : abs (endMany st P) = endSet (abs st) (endsAt st P) := by
  show (⟨absLease (endMany st P), _⟩ : Seats.State) = ⟨fun s => if endsAt st P s then NoLease else absLease st s, _⟩
  congr 1
  funext t
  cases ht : st.liveBySeat t with
  | none =>
    have : (endMany st P).liveBySeat t = none := by simp [endMany, ht]
    simp [absLease_none this, absLease_none ht, endsAt, ht]
  | some f =>
    cases he : ends st P f
    · have hl : (endMany st P).liveBySeat t = some f := by simp [endMany, ht, he]
      have hr : (endMany st P).leases f = st.leases f := by
        rw [endMany_leases]; cases st.leases f <;> simp [he]
      simp only [endsAt, ht, he, Bool.false_eq_true, if_false]
      exact absLease_congr (hl.trans ht.symm) fun g hg => by rw [ht] at hg; cases hg; exact hr
    · have hl : (endMany st P).liveBySeat t = none := by simp [endMany, ht, he]
      simp [absLease_none hl, endsAt, ht, he]

theorem endMany_steps (st : IState δ) (hi : Inv st) (P) :
    Steps (Seats.Next .none) (abs st) (abs (endMany st P)) := by
  rw [abs_endMany st P]
  apply endSet_steps
  intro s hE
  cases hs : st.liveBySeat s with
  | none => simp [endsAt, hs] at hE
  | some f =>
    obtain ⟨r, hr, -, -⟩ := hi.1.1 s f hs
    show (absLease st s).live
    rw [absLease_of hs hr]; trivial

theorem step_refines (st : IState δ) (index : Nat) (e : MEntry Seat Principal δ) (ok : Bool) (hi : Inv st)
    (hk : st.kinds = kindsI) (hidx : st.last < index) :
    Steps (Seats.Next .none) (abs st) (abs (apply st index e ok).1) := by
  obtain ⟨⟨hI1, hI2⟩, hF, hA, hD, hO⟩ := hi
  have hi : Inv st := ⟨⟨hI1, hI2⟩, hF, hA, hD, hO⟩
  have fresh := fresh_of hF hidx
  have stut : Steps (Seats.Next .none) (abs st) (abs { st with last := index }) := .refl _
  have hend : ∀ P, Steps (Seats.Next .none) (abs st) (abs { endMany st P with last := index }) :=
    fun P => endMany_steps st hi P
  cases e with
  | grant seat p persona conf α =>
    simp only [apply, applyArm]
    rcases applyGrant_cases st index seat p persona conf α ok with h | ⟨k, -, hlb, -, hh, happ⟩
    · rw [h]; exact stut
    rw [happ, abs_last]
    apply Steps.single
    refine ⟨seat, Or.inr (Or.inr ⟨p, ?_, Or.inr ?_, ?_, rfl⟩)⟩
    · show ¬ (absLease st seat).live
      rw [absLease_none hlb]; exact id
    · rintro ⟨t, -, hlive, hp⟩
      change (absLease st t).live at hlive
      change (absLease st t).principal = some p at hp
      cases ht : st.liveBySeat t with
      | none => rw [absLease_none ht] at hlive; exact hlive
      | some f =>
        obtain ⟨r, hr, -, hl⟩ := hI1 t f ht
        rw [absLease_of ht hr] at hp
        exact heldElsewhere_false hh hF hI2 f r hr hl (Option.some.inj hp)
    · show absLease _ = _
      funext t
      by_cases hts : t = seat
      · subst hts
        rw [upd_same, absLease_of (f := index) (upd_same _ _ _) (upd_same _ _ _)]
        rfl
      · rw [upd_other _ _ _ _ hts]
        refine absLease_congr (upd_other _ _ _ _ hts) fun f hf => ?_
        obtain ⟨r, hr, -, -⟩ := hI1 t f hf
        exact upd_other _ _ _ _ (fresh f r hr)
  | renew seat fence α =>
    simp only [apply, applyArm]
    rcases applyRenew_cases st index seat fence α ok with h | ⟨old, hfo, hseat, hlive, -, happ⟩
    · rw [h]; exact stut
    rw [happ]
    have hbo : st.liveBySeat seat = some fence := hseat ▸ hI2 fence old hfo hlive
    suffices heq : abs { st with leases := upd (upd st.leases fence (some { old with live := false })) index
                                   (some { old with alphabet := α }),
                                 liveBySeat := upd st.liveBySeat seat (some index), last := index } = abs st by
      rw [heq]; exact .refl _
    show (⟨absLease _, _⟩ : Seats.State) = ⟨absLease st, _⟩
    congr 1
    funext t
    by_cases hts : t = seat
    · subst hts
      rw [absLease_of (f := index) (upd_same _ _ _) (upd_same _ _ _), absLease_of hbo hfo]
    · refine absLease_congr (upd_other _ _ _ _ hts) fun f hf => ?_
      obtain ⟨r, hr, hrs, -⟩ := hI1 t f hf
      have hff : f ≠ fence := fun he => by subst he; rw [hfo] at hr; cases hr; exact hts (hrs.symm.trans hseat)
      show upd (upd st.leases fence _) index _ f = _
      rw [upd_other _ _ _ _ (fresh f r hr), upd_other _ _ _ _ hff]
  | admit seat fence a =>
    simp only [apply, applyArm]
    rcases applyAdmit_cases st seat fence a ok with h | ⟨r, hfo, hseat, hlive, ha, happ⟩
    · rw [h]; exact stut
    rw [happ]
    have hbo : st.liveBySeat seat = some fence := hseat ▸ hI2 fence r hfo hlive
    obtain ⟨k, hk', hka⟩ := hA fence r hfo hlive
    rw [hseat, hk] at hk'
    have hkk : k = codeKind (KindOf seat) := (Option.some.inj hk').symm
    have hab := absLease_of hbo hfo
    -- the act: one `Act(seat)` step
    have hact : Steps (Seats.Next .none) (abs st) (abs (admitted st seat a)) := by
      apply Steps.single
      refine ⟨seat, Or.inl ⟨?_, ⟨actMap a, ?_, ?_⟩, rfl⟩⟩
      · show (absLease st seat).live
        rw [hab]; trivial
      · show actMap a ∈ (absLease st seat).alphabet
        rw [hab]
        exact allows_bound _ a (hkk ▸ hka a ha)
      · apply PSet.ext
        intro ar
        cases ar with
        | mk act kind =>
          show (∃ x, x ∈ (a, st.kinds seat) :: st.acted ∧ actMap x.1 = act ∧ x.2 = some (codeKind kind)) ↔
            (∃ x, x ∈ st.acted ∧ actMap x.1 = act ∧ x.2 = some (codeKind kind)) ∨
              (⟨act, kind⟩ : ActRec) = ⟨actMap a, KindOf seat⟩
          constructor
          · rintro ⟨x, hx, h1, h2⟩
            rcases List.mem_cons.mp hx with rfl | hx
            · right
              rw [hk] at h2
              have := codeKind_inj (Option.some.inj h2)
              rw [← h1, this]
            · exact Or.inl ⟨x, hx, h1, h2⟩
          · rintro (⟨x, hx, h1, h2⟩ | h)
            · exact ⟨x, List.mem_cons_of_mem _ hx, h1, h2⟩
            · cases h
              exact ⟨(a, st.kinds seat), List.mem_cons_self .., rfl, by rw [hk]; rfl⟩
    -- a terminal act then ends the lease: one `EndRound(seat)` step
    cases terminal a
    · exact hact
    · exact hact.trans (endMany_steps _ (admitted_inv hi hfo hseat hlive ha) _)
  | endRound seat fence =>
    simp only [apply, applyArm]
    split
    · split
      · exact hend _
      · exact stut
    · exact stut
  | endSeat seat =>
    simp only [apply, applyArm]
    split
    · split
      · exact hend _
      · exact stut
    · exact stut
  | revoke t => simp only [apply, applyArm]; split; exact hend _; exact stut
  | fence => simp only [apply, applyArm]; split; exact hend _; exact stut
  | issue ks =>
    simp only [apply, applyArm]
    split
    · exact endMany_steps st hi _
    · exact stut
  | other => simp only [apply, applyArm]; split <;> exact stut

/-- **The refinement.** Every state the model reaches at the module's constants, issuing no new kinds, maps to a
state `Seats.tla` reaches at `Mut = "none"`. -/
theorem model_refines_seats (st : IState δ) (h : Reachable IInit INext st) :
    Reachable Seats.Init (Seats.Next .none) (abs st) ∧ Inv st ∧ st.kinds = kindsI := by
  induction h with
  | init hi =>
    obtain ⟨⟨hl, hb, ha⟩, hk⟩ := hi
    refine ⟨.init ⟨?_, ?_⟩, init_inv _ ⟨hl, hb, ha⟩, hk⟩
    · funext s; exact absLease_none (by rw [hb])
    · apply PSet.ext; intro ar
      refine ⟨fun ⟨x, hx, _⟩ => ?_, fun h => False.elim h⟩
      rw [ha] at hx; cases hx
  | step _ hn ih =>
    obtain ⟨hr, hi, hk⟩ := ih
    obtain ⟨⟨index, e, ok, hidx, he⟩, hks⟩ := hn
    subst he
    exact ⟨reach_steps hr (step_refines _ index e ok hi hk hidx), step_inv _ index ok e hi hidx, hks.trans hk⟩

/-- `Seats_proof.tla`'s `SafeAlways`, of the model: no non-thinker authored, no thinker voted, and no principal
held two seats. -/
theorem model_seats_safe (st : IState δ) (h : Reachable IInit INext st) : Seats.Safe (abs st) :=
  Seats.SafeAlways _ (model_refines_seats st h).1

end Inst

#print axioms model_inv
#print axioms Inst.model_refines_seats
#print axioms Inst.model_seats_safe

end Topak.SeatsModel
