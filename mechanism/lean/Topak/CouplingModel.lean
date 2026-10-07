import Topak.SeatsModel
/-!
# A Coupling-shaped model of `State::apply`, on the Seats-shaped one

`Topak/SeatsModel.lean` models the arms of `State::apply` on the leases, the live index, the seat kinds and the
admitted acts, and leaves every other check to one oracle `ok`. This file narrows that oracle where
`spec/Coupling.tla` (ADR-0039, ADR-0042) is about: what an Observer has read of a Thinker's round. It adds to the
state each lease's epoch, round, sequence number and action count, the seats' domains and cells, the fleet epoch,
the watermarks (`marks`), the seals and each seat's last round; and to the checks:

- at grant, the alphabet within the seat's domain, the cross-round condition (ADR-0039 §2) and round numbers
  never reused;
- at admit, the round bound, a heartbeat's validity (`check_heartbeat`), and the coupling of a Thinker's `Actuate`
  and `Report` to a cell Observer whose watermark is within `K` of the Thinker's sequence (`observer_covers`).

Its `apply` is `SeatsModel.apply` with those checks folded into `ok`, and its extra fields updated after: so every
step of this model is a step of the Seats-shaped one, and every theorem proved there holds here (`base_reach`).
Every check still outside both is `ok`, as before.

What is proved, at any number of seats and principals, of every reachable state:
- `model_unread_bounded`: a Run Thinker's live round has at most `K` effects unread by some cell Observer;
- `model_prior_read`: and its previous round, by its seal, has been read to the seal by some cell Observer.
Together these are `Coupling.tla`'s `UnreadBounded` where the cell has one Observer; with more, each bound has its
own witness. `admit_coupled`: an admitted `Actuate` or `Report` of a Thinker had a covering cell Observer.

What it premises, beyond the Seats-shaped model's: the heartbeat's freshness, `live(o)`'s condition 2, is a
per-replica clock checked at decide and not at apply (`observer_covers(.., &|_| true)` in `apply_admit`), so the
model, like the code, does not check it. The model is checked against the reference's recorded traces by
`SeatsReplay.lean`, which compares the new fields too. It is not a stage of T-0045-28's chain (ADR-0053 §5).
-/

namespace Topak.CouplingModel
open Topak.Spec Topak.SeatsModel

set_option linter.unusedSectionVars false

/-! ## The code's further types -/

/-- `types.rs` `Domain`. -/
inductive Domain | build | run
  deriving DecidableEq, Repr

/-- `ActionKind::domain`: `ActionKind::BUILD` and `ActionKind::RUN`. -/
def actDom : ActionKind → Domain
  | .Consult | .Actuate | .Report => .run
  | _ => .build

/-- The admits that count in a lease's sequence number: `Admitted::Emit | Report | Actuate`, and a heartbeat,
which travels by `Emit` or `Report`. -/
def effect : ActionKind → Bool
  | .Emit | .Report | .Actuate => true
  | _ => false

/-- A round's topic, `topak.<chain>.<domain>.<seat>.e<epoch>.r<round>`, as the trace projects it:
`<<seat, epoch, round>>`. The chain is one, and a seat's round is never reused, so the triple names the topic. -/
abbrev Topic (σ : Type) := σ × Nat × Nat

/-- What the model keeps of a `LeaseRecord` beyond `Rec`: `lease.epoch`, `lease.round`, `seq`, `actions`. -/
structure LX where
  epoch : Nat
  round : Nat
  seq : Nat
  actions : Nat
  deriving DecidableEq, Repr

/-- `ObserverValues::k` and `Params::round_bound_for`, fixed at startup. -/
structure Params where
  K : Nat
  buildBound : Nat
  runBound : Nat

def Params.bound (P : Params) : Domain → Nat
  | .build => P.buildBound
  | .run => P.runBound

variable {σ π δ : Type} [DecidableEq σ] [DecidableEq π] [DecidableEq δ]

/-- The further state: the issued seats (`rules.seats`: the list, each one's domain and cell), `epoch`, each
fence's `LX`, `marks` (observer seat → topic → watermark), `seals` (Thinker seat → its last ended round's topic and
final sequence number), `last_round`. -/
structure XState (σ : Type) where
  seats : List σ
  domain : σ → Option Domain
  cell : σ → Option σ
  epoch : Nat
  lx : Nat → LX
  marks : σ → Topic σ → Nat
  seals : σ → Option (Topic σ × Nat)
  lastRound : σ → Option Nat

structure RState (σ π δ : Type) where
  base : MState σ π δ
  x : XState σ

/-- The entries, with what the further checks read: a grant's round, an admit's heartbeat (its topic and
watermark), an issuance's domains, cells and seat list. -/
inductive REntry (σ π δ : Type)
  | grant (seat : σ) (principal : π) (persona conf : δ) (alphabet : Alphabet) (round : Nat)
  | renew (seat : σ) (fence : Nat) (alphabet : Alphabet)
  | admit (seat : σ) (fence : Nat) (act : ActionKind) (hb : Option (Topic σ × Nat))
  | endRound (seat : σ) (fence : Nat)
  | endSeat (seat : σ)
  | revoke (target : RevTarget π δ)
  | fence
  | issue (kinds : σ → Option SeatKind) (domain : σ → Option Domain) (cell : σ → Option σ) (seats : List σ)
  | other

def REntry.base : REntry σ π δ → MEntry σ π δ
  | .grant seat p persona conf α _ => .grant seat p persona conf α
  | .renew seat fn α => .renew seat fn α
  | .admit seat fn a _ => .admit seat fn a
  | .endRound seat fn => .endRound seat fn
  | .endSeat seat => .endSeat seat
  | .revoke t => .revoke t
  | .fence => .fence
  | .issue ks _ _ _ => .issue ks
  | .other => .other

/-! ## The further checks -/

/-- `topic_of(rec)`: the topic of the lease at fence `f`, held at seat `s`. -/
def topicOf (x : XState σ) (s : σ) (f : Nat) : Topic σ := (s, (x.lx f).epoch, (x.lx f).round)

/-- `Rules::cell_observers(thinker)`: the observer seats declaring `cell = thinker`. -/
def cellObsOf (kinds : σ → Option SeatKind) (x : XState σ) (t : σ) : List σ :=
  x.seats.filter fun o => kinds o == some .Observer && x.cell o == some t

def cellObs (st : RState σ π δ) (t : σ) : List σ := cellObsOf st.base.kinds st.x t

/-- `live_lease(seat)`: the record `live_by_seat` holds there. -/
def liveLease (st : RState σ π δ) (s : σ) : Option (Nat × Rec σ π δ) :=
  match st.base.liveBySeat s with
  | some f => (st.base.leases f).map fun r => (f, r)
  | none => none

/-- `observer_covers(thinker, &|_| true)`, the deterministic half of `live(o)` (ADR-0039 §1, conditions 1 and 3):
```
let Some(t) = self.live_lease(thinker) else { return false };
let Some(topic) = self.topic_of(t) else { return false };
self.rules.cell_observers(thinker).iter().any(|o| {
    self.live_lease(o).is_some() && fresh(o) && t.seq.saturating_sub(self.mark(o, &topic)) < self.observer.k
})
``` -/
def covers (P : Params) (st : RState σ π δ) (t : σ) : Bool :=
  match liveLease st t with
  | some (f, _) =>
    (st.x.domain t).isSome &&
      (cellObs st t).any fun o => (liveLease st o).isSome && decide ((st.x.lx f).seq - st.x.marks o (topicOf st.x t f) < P.K)
  | none => false

/-- `Rules::watches(observer, thinker)`: its cell Observer, or a correlator of the Thinker's domain. -/
def watches (st : RState σ π δ) (o t : σ) : Bool :=
  st.base.kinds o == some .Observer && st.base.kinds t == some .Thinker &&
    match st.x.cell o with
    | some c => c == t
    | none => st.x.domain o == st.x.domain t

/-- What exists in the round a heartbeat names: the live round's sequence number, or the seal's. -/
def hbUpper (st : RState σ π δ) (T : Topic σ) : Option Nat :=
  let t := T.1
  let sealed : Option Nat := match st.x.seals t with
    | some (T', n) => if T' = T then some n else none
    | none => none
  if st.base.kinds t = some .Thinker then
    match liveLease st t with
    | some (f, _) => if (st.x.domain t).isSome && topicOf st.x t f = T then some (st.x.lx f).seq else sealed
    | none => sealed
  else none

/-- `check_heartbeat(seat, h)`: an observer seat, a topic naming a Thinker's live or sealed round in its reach, a
watermark at most what exists and at least the last reported. A heartbeat travels by `Emit` or `Report`. -/
def hbOK (st : RState σ π δ) (seat : σ) (a : ActionKind) (h : Topic σ × Nat) : Bool :=
  st.base.kinds seat == some .Observer && (a == .Emit || a == .Report) &&
    match hbUpper st h.1 with
    | some u => watches st seat h.1.1 && decide (h.2 ≤ u) && decide (st.x.marks seat h.1 ≤ h.2)
    | none => false

/-- `req.alphabet.iter().find(|k| k.domain() != domain)` is `None`, for a declared seat. -/
def domainOK (st : RState σ π δ) (seat : σ) (α : Alphabet) : Bool :=
  match st.x.domain seat with
  | some d => ActionKind.all.all fun a => !α a || actDom a == d
  | none => false

/-- ADR-0039 §2, at grant: in Run, a Thinker's next round only once a cell Observer has read its last to the seal.
```
if domain == Domain::Run && kind == SeatKind::Thinker && let Some(seal) = self.seals.get(&req.seat)
    && !self.rules.cell_observers(&req.seat).iter().any(|o| self.mark(o, &seal.topic) >= seal.seq)
{ return Applied::Rejected(..) }
``` -/
def crossRoundOK (st : RState σ π δ) (seat : σ) : Bool :=
  if st.x.domain seat = some .run ∧ st.base.kinds seat = some .Thinker then
    match st.x.seals seat with
    | some (T, n) => (cellObs st seat).any fun o => decide (n ≤ st.x.marks o T)
    | none => true
  else true

/-- `self.last_round.get(&req.seat).is_some_and(|r| req.round <= *r)` refuses. -/
def roundFresh (st : RState σ π δ) (seat : σ) (round : Nat) : Bool :=
  match st.x.lastRound seat with
  | some r => decide (r < round)
  | none => true

/-- `check_live`'s round bound: `rec.actions >= params.round_bound_for(domain)` refuses. -/
def boundOK (P : Params) (st : RState σ π δ) (seat : σ) (fn : Nat) : Bool :=
  decide ((st.x.lx fn).actions < P.bound ((st.x.domain seat).getD .build))

/-- `apply_admit`'s coupling: `Actuate` and `Report` (not a heartbeat) of a Thinker seat need a covering Observer. -/
def coupled (st : RState σ π δ) (seat : σ) (a : ActionKind) (hb : Option (Topic σ × Nat)) : Bool :=
  (a == .Actuate || a == .Report) && hb.isNone && st.base.kinds seat == some .Thinker

def extraOK (P : Params) (st : RState σ π δ) : REntry σ π δ → Bool
  | .grant seat _ _ _ α round => domainOK st seat α && crossRoundOK st seat && roundFresh st seat round
  | .admit seat fn a hb =>
    boundOK P st seat fn &&
      (match hb with | some h => hbOK st seat a h | none => true) &&
      (!coupled st seat a hb || covers P st seat)
  | _ => true

/-! ## The further effects -/

/-- `end_lease`'s seal, for every lease `endMany` ends: a Thinker's round seals at its final sequence number.
```
let seal = (self.rules.seat_kind(&rec.lease.seat) == Some(SeatKind::Thinker))
    .then(|| self.topic_of(rec).map(|topic| (rec.lease.seat.clone(), Seal { topic, seq: rec.seq }))).flatten();
``` -/
def sealEnded (kinds : σ → Option SeatKind) (x : XState σ) (b : MState σ π δ) (P : Nat → Rec σ π δ → Bool) :
    σ → Option (Topic σ × Nat) := fun s =>
  match b.liveBySeat s with
  | some f =>
    if ends b P f && kinds s == some .Thinker && (x.domain s).isSome then some (topicOf x s f, (x.lx f).seq)
    else x.seals s
  | none => x.seals s

/-- The further fields after an applied entry. -/
def xstep (st : RState σ π δ) (i : Nat) : REntry σ π δ → XState σ
  | .grant seat _ _ _ _ round =>
    { st.x with lx := upd st.x.lx i ⟨st.x.epoch, round, 0, 0⟩, lastRound := upd st.x.lastRound seat (some round) }
  | .renew _ fn _ => { st.x with lx := upd st.x.lx i (st.x.lx fn) }
  | .admit seat fn a hb =>
    let l := st.x.lx fn
    let x1 : XState σ :=
      { st.x with
        lx := upd st.x.lx fn { l with actions := l.actions + 1, seq := if effect a then l.seq + 1 else l.seq }
        marks := match hb with
          | some (T, w) => upd st.x.marks seat (upd (st.x.marks seat) T w)
          | none => st.x.marks }
    if terminal a then { x1 with seals := sealEnded st.base.kinds x1 st.base fun g _ => g == fn } else x1
  | .endRound _ fn => { st.x with seals := sealEnded st.base.kinds st.x st.base fun g _ => g == fn }
  | .endSeat seat =>
    match st.base.liveBySeat seat with
    | some f => { st.x with seals := sealEnded st.base.kinds st.x st.base fun g _ => g == f }
    | none => st.x
  | .revoke t => { st.x with seals := sealEnded st.base.kinds st.x st.base fun _ r => t.matches r }
  | .fence => { st.x with seals := sealEnded st.base.kinds st.x st.base (fun _ _ => true), epoch := st.x.epoch + 1 }
  | .issue ks ds cs ss =>
    let x1 : XState σ := { st.x with domain := ds, cell := cs, seats := ss }
    { x1 with seals := sealEnded ks x1 st.base fun _ _ => true }
  | .other => st.x

/-- `State::apply`: the Seats-shaped step with the further checks folded into `ok`, then the further fields. -/
def rapply (P : Params) (st : RState σ π δ) (i : Nat) (e : REntry σ π δ) (ok : Bool) : RState σ π δ × MApplied :=
  let r := SeatsModel.apply st.base i e.base (ok && extraOK P st e)
  ({ base := r.1, x := if r.2 = .rejected then st.x else xstep st i e }, r.2)

/-! ## The model as a transition system -/

def RInit (st : RState σ π δ) : Prop :=
  SeatsModel.Init st.base ∧ (∀ s, st.x.seals s = none) ∧ (∀ o T, st.x.marks o T = 0)

def RNext (P : Params) (st st' : RState σ π δ) : Prop :=
  ∃ i e ok, st.base.last < i ∧ st' = (rapply P st i e ok).1

/-- Every step of this model is a step of the Seats-shaped one. -/
theorem base_step (P : Params) (st st' : RState σ π δ) (h : RNext P st st') : SeatsModel.Next st.base st'.base := by
  obtain ⟨i, e, ok, hi, rfl⟩ := h
  exact ⟨i, e.base, ok && extraOK P st e, hi, rfl⟩

theorem base_reach (P : Params) (st : RState σ π δ) (h : Reachable RInit (RNext P) st) :
    Reachable SeatsModel.Init SeatsModel.Next st.base := by
  induction h with
  | init hi => exact .init hi.1
  | step _ hn ih => exact .step ih (base_step P _ _ hn)

/-! ## The invariant -/

/-- A Thinker seat of the Run domain. -/
def RunThinker (kinds : σ → Option SeatKind) (x : XState σ) (s : σ) : Prop :=
  kinds s = some .Thinker ∧ x.domain s = some .run

/-- A live alphabet is within its seat's domain. -/
def AlphaDom (st : RState σ π δ) : Prop :=
  ∀ f r, st.base.leases f = some r → r.live = true →
    ∃ d, st.x.domain r.seat = some d ∧ ∀ a, r.alphabet a = true → actDom a = d

/-- ADR-0039 §2, `UnreadBounded`'s first half: a Run Thinker's live round has at most `K` effects unread by some
cell Observer, or none yet. -/
def UnreadBounded (P : Params) (st : RState σ π δ) : Prop :=
  ∀ s f, st.base.liveBySeat s = some f → RunThinker st.base.kinds st.x s →
    (st.x.lx f).seq = 0 ∨
      ∃ o, o ∈ cellObsOf st.base.kinds st.x s ∧ (st.x.lx f).seq ≤ st.x.marks o (topicOf st.x s f) + P.K

/-- ADR-0039 §2, `UnreadBounded`'s second half: a Run Thinker with a live round has had its last round read to the
seal by some cell Observer. -/
def PriorRead (st : RState σ π δ) : Prop :=
  ∀ s f, st.base.liveBySeat s = some f → RunThinker st.base.kinds st.x s →
    ∀ T n, st.x.seals s = some (T, n) → ∃ o, o ∈ cellObsOf st.base.kinds st.x s ∧ n ≤ st.x.marks o T

def XInv (P : Params) (st : RState σ π δ) : Prop :=
  Inv st.base ∧ AlphaDom st ∧ UnreadBounded P st ∧ PriorRead st

theorem init_xinv (P : Params) (st : RState σ π δ) (h : RInit st) : XInv P st := by
  obtain ⟨hb, -, -⟩ := h
  have hbi := init_inv st.base hb
  obtain ⟨hl, hlb, -⟩ := hb
  refine ⟨hbi, ?_, ?_, ?_⟩
  · intro f r h; rw [hl] at h; cases h
  · intro s f h; rw [hlb] at h; cases h
  · intro s f h; rw [hlb] at h; cases h

/-! ### The Seats-shaped step: refused, or its gate passed -/

theorem apply_rej (b : MState σ π δ) (i : Nat) (e : MEntry σ π δ) (ok : Bool)
    (h : (SeatsModel.apply b i e ok).2 = .rejected) : (SeatsModel.apply b i e ok).1 = { b with last := i } := by
  cases e with
  | grant seat p ps cf α =>
    rcases applyGrant_cases b i seat p ps cf α ok with h' | ⟨_, _, _, _, _, h'⟩ <;>
      simp only [SeatsModel.apply, applyArm, h'] at h ⊢
    cases h
  | renew seat fn α =>
    rcases applyRenew_cases b i seat fn α ok with h' | ⟨_, _, _, _, _, h'⟩ <;>
      simp only [SeatsModel.apply, applyArm, h'] at h ⊢
    cases h
  | admit seat fn a =>
    rcases applyAdmit_cases b seat fn a ok with h' | ⟨_, _, _, _, _, h'⟩ <;>
      simp only [SeatsModel.apply, applyArm, h'] at h ⊢
    cases h
  | endRound seat fn =>
    revert h; simp only [SeatsModel.apply, applyArm]
    split <;> (try split) <;> simp
  | endSeat seat =>
    revert h; simp only [SeatsModel.apply, applyArm]
    split <;> (try split) <;> simp
  | revoke t => revert h; simp only [SeatsModel.apply, applyArm]; split <;> simp
  | fence => revert h; simp only [SeatsModel.apply, applyArm]; split <;> simp
  | issue ks => revert h; simp only [SeatsModel.apply, applyArm]; split <;> simp
  | other => revert h; simp only [SeatsModel.apply, applyArm]; split <;> simp

theorem apply_gate (b : MState σ π δ) (i : Nat) (e : MEntry σ π δ) (ok : Bool)
    (h : (SeatsModel.apply b i e ok).2 ≠ .rejected) : ok = true := by
  cases ok
  · exfalso; apply h
    cases e with
    | grant seat p ps cf α =>
      rcases applyGrant_cases b i seat p ps cf α false with h' | ⟨_, _, _, _, _, h'⟩
      · simp only [SeatsModel.apply, applyArm, h']
      · revert h'; unfold applyGrant; split <;> (repeat' split) <;> simp_all
    | renew seat fn α =>
      simp only [SeatsModel.apply, applyArm, applyRenew]; split <;> (try split) <;> simp_all
    | admit seat fn a =>
      simp only [SeatsModel.apply, applyArm, applyAdmit]; split <;> (try split) <;> simp_all
    | endRound seat fn => simp only [SeatsModel.apply, applyArm]; split <;> (try split) <;> simp_all
    | endSeat seat => simp only [SeatsModel.apply, applyArm]; split <;> (try split) <;> simp_all
    | revoke t => simp [SeatsModel.apply, applyArm]
    | fence => simp [SeatsModel.apply, applyArm]
    | issue ks => simp [SeatsModel.apply, applyArm]
    | other => simp [SeatsModel.apply, applyArm]
  · rfl

/-! ### Framing lemmas -/

theorem cellObsOf_congr {k1 k2 : σ → Option SeatKind} {x1 x2 : XState σ} (hk : k1 = k2) (hs : x1.seats = x2.seats)
    (hc : x1.cell = x2.cell) (t : σ) : cellObsOf k1 x1 t = cellObsOf k2 x2 t := by
  simp only [cellObsOf, hk, hs, hc]

theorem topicOf_congr {x1 x2 : XState σ} {f : Nat} (h : x1.lx f = x2.lx f) (s : σ) :
    topicOf x1 s f = topicOf x2 s f := by
  simp only [topicOf, h]

theorem sealEnded_keep (ks : σ → Option SeatKind) (x : XState σ) (b : MState σ π δ) (Pd) {s : σ} {f : Nat}
    (hs : b.liveBySeat s = some f) (he : ends b Pd f = false) : sealEnded ks x b Pd s = x.seals s := by
  simp [sealEnded, hs, he]

/-- Two indexed seats hold two fences. -/
theorem fence_seat {b : MState σ π δ} (hb : Inv b) {s t : σ} {f : Nat} (hs : b.liveBySeat s = some f)
    (ht : b.liveBySeat t = some f) : s = t := by
  obtain ⟨r, hr, hrs, -⟩ := hb.1.1 s f hs
  obtain ⟨r', hr', hrt, -⟩ := hb.1.1 t f ht
  rw [hr] at hr'; cases hr'; exact hrs.symm.trans hrt

/-- The arms that end leases: what `endMany` leaves keeps the three invariants, so long as the further fields
move only where a lease ended, and watermarks only rise. -/
theorem end_xinv (P : Params) (st : RState σ π δ) (b0 : MState σ π δ) (Pd : Nat → Rec σ π δ → Bool) (i : Nat)
    (x' : XState σ) (hl : b0.leases = st.base.leases) (hlb : b0.liveBySeat = st.base.liveBySeat)
    (hk : b0.kinds = st.base.kinds) (hA : AlphaDom st) (hU : UnreadBounded P st) (hR : PriorRead st)
    (hseats : x'.seats = st.x.seats) (hcell : x'.cell = st.x.cell) (hdom : x'.domain = st.x.domain)
    (hmk : ∀ o T, st.x.marks o T ≤ x'.marks o T)
    (hkeep : ∀ s f, st.base.liveBySeat s = some f → ends st.base Pd f = false →
      x'.lx f = st.x.lx f ∧ x'.seals s = st.x.seals s) :
    AlphaDom (⟨{ endMany b0 Pd with last := i }, x'⟩ : RState σ π δ) ∧
      UnreadBounded P (⟨{ endMany b0 Pd with last := i }, x'⟩ : RState σ π δ) ∧
      PriorRead (⟨{ endMany b0 Pd with last := i }, x'⟩ : RState σ π δ) := by
  have he : ∀ f, ends b0 Pd f = ends st.base Pd f := by intro f; simp only [ends, hl, hlb]
  have hco : ∀ t, cellObsOf b0.kinds x' t = cellObsOf st.base.kinds st.x t := cellObsOf_congr hk hseats hcell
  refine ⟨?_, ?_, ?_⟩
  · intro f r h hlv
    have h' : (endMany b0 Pd).leases f = some r := h
    obtain ⟨h0, -⟩ := endMany_live h' hlv
    rw [hl] at h0
    obtain ⟨d, hd, hda⟩ := hA f r h0 hlv
    exact ⟨d, hdom ▸ hd, hda⟩
  · intro s f h hrt
    have h' : (endMany b0 Pd).liveBySeat s = some f := h
    obtain ⟨h0, hen⟩ := endMany_lbs h'
    rw [hlb] at h0; rw [he] at hen
    have hrt' : RunThinker st.base.kinds st.x s := by
      obtain ⟨h1, h2⟩ := hrt; exact ⟨hk ▸ h1, hdom ▸ h2⟩
    obtain ⟨hlx, -⟩ := hkeep s f h0 hen
    show (x'.lx f).seq = 0 ∨ ∃ o, o ∈ cellObsOf b0.kinds x' s ∧ (x'.lx f).seq ≤ x'.marks o (topicOf x' s f) + P.K
    rw [hlx, hco, topicOf_congr hlx]
    rcases hU s f h0 hrt' with h1 | ⟨o, ho, hle⟩
    · exact Or.inl h1
    · exact Or.inr ⟨o, ho, Nat.le_trans hle (Nat.add_le_add_right (hmk o _) _)⟩
  · intro s f h hrt T n hsl
    have h' : (endMany b0 Pd).liveBySeat s = some f := h
    obtain ⟨h0, hen⟩ := endMany_lbs h'
    rw [hlb] at h0; rw [he] at hen
    have hrt' : RunThinker st.base.kinds st.x s := by
      obtain ⟨h1, h2⟩ := hrt; exact ⟨hk ▸ h1, hdom ▸ h2⟩
    obtain ⟨-, hsl'⟩ := hkeep s f h0 hen
    rw [hsl'] at hsl
    obtain ⟨o, ho, hle⟩ := hR s f h0 hrt' T n hsl
    exact ⟨o, (hco s).symm ▸ ho, Nat.le_trans hle (hmk o T)⟩

/-! ### Every step keeps the invariant -/

theorem xstep_inv (P : Params) (st : RState σ π δ) (i : Nat) (e : REntry σ π δ) (ok : Bool) (hi : XInv P st)
    (hidx : st.base.last < i) : XInv P (rapply P st i e ok).1 := by
  obtain ⟨hb, hA, hU, hR⟩ := hi
  have hb0 := hb
  obtain ⟨⟨hI1, hI2⟩, hF, -, -, -⟩ := hb0
  have fresh := fresh_of hF hidx
  have hb' := step_inv st.base i (ok && extraOK P st e) e.base hb hidx
  simp only [rapply]
  by_cases hrej : (SeatsModel.apply st.base i e.base (ok && extraOK P st e)).2 = .rejected
  · rw [if_pos hrej]
    refine ⟨hb', ?_, ?_, ?_⟩ <;> rw [apply_rej _ _ _ _ hrej]
    · exact hA
    · exact hU
    · exact hR
  rw [if_neg hrej]
  have hok := apply_gate _ _ _ _ hrej
  have hx : extraOK P st e = true := (Bool.and_eq_true _ _ ▸ hok).2
  refine ⟨hb', ?_⟩
  cases e with
  | grant seat p ps cf α rd =>
    simp only [extraOK, Bool.and_eq_true] at hx
    obtain ⟨⟨hdom, hcross⟩, -⟩ := hx
    have hd : ∃ d, st.x.domain seat = some d ∧ ∀ a, α a = true → actDom a = d := by
      unfold domainOK at hdom
      split at hdom
      · rename_i d hds
        refine ⟨d, hds, fun a ha => ?_⟩
        have := List.all_eq_true.mp hdom a (ActionKind.mem_all a)
        simp [ha] at this; exact this
      · cases hdom
    simp only [REntry.base] at hrej ⊢
    rcases applyGrant_cases st.base i seat p ps cf α (ok && extraOK P st (.grant seat p ps cf α rd)) with
      h | ⟨k, hk, hlb, hw, hh, happ⟩
    · exfalso; apply hrej; simp only [SeatsModel.apply, applyArm, h]
    simp only [SeatsModel.apply, applyArm, happ]
    refine ⟨?_, ?_, ?_⟩
    · intro f r h hlv
      simp only at h ⊢
      by_cases hf : f = i
      · subst hf; rw [upd_same] at h; cases h; exact hd
      · rw [upd_other _ _ _ _ hf] at h; exact hA f r h hlv
    · intro s f h hrt
      simp only at h hrt ⊢
      by_cases hs : s = seat
      · subst hs; rw [upd_same] at h; cases h; left; simp [xstep]
      · rw [upd_other _ _ _ _ hs] at h
        obtain ⟨r, hr, -, -⟩ := hI1 s f h
        have hfi := fresh f r hr
        have hlx : (xstep st i (.grant seat p ps cf α rd)).lx f = st.x.lx f := by simp [xstep, upd_other _ _ _ _ hfi]
        rw [hlx, topicOf_congr hlx]
        exact hU s f h hrt
    · intro s f h hrt T n hsl
      simp only at h hrt hsl ⊢
      by_cases hs : s = seat
      · subst hs
        have hc : crossRoundOK st s = true := hcross
        unfold crossRoundOK at hc
        have hrt' : st.x.domain s = some .run ∧ st.base.kinds s = some .Thinker := ⟨hrt.2, hrt.1⟩
        rw [if_pos hrt'] at hc
        have hsl' : st.x.seals s = some (T, n) := hsl
        rw [hsl'] at hc
        obtain ⟨o, ho, hle⟩ := List.any_eq_true.mp hc
        exact ⟨o, ho, of_decide_eq_true hle⟩
      · rw [upd_other _ _ _ _ hs] at h
        exact hR s f h hrt T n hsl
  | renew seat fo α =>
    simp only [REntry.base] at hrej ⊢
    rcases applyRenew_cases st.base i seat fo α (ok && extraOK P st (.renew seat fo α)) with
      h | ⟨old, hfo, hseat, hlive, hsub, happ⟩
    · exfalso; apply hrej; simp only [SeatsModel.apply, applyArm, h]
    simp only [SeatsModel.apply, applyArm, happ]
    have hbo : st.base.liveBySeat seat = some fo := hseat ▸ hI2 fo old hfo hlive
    have hfi : fo ≠ i := fresh fo old hfo
    refine ⟨?_, ?_, ?_⟩
    · intro f r h hlv
      simp only at h ⊢
      by_cases hf : f = i
      · subst hf; rw [upd_same] at h; cases h
        obtain ⟨d, hd, hda⟩ := hA fo old hfo hlive
        exact ⟨d, hd, fun a ha => hda a (subsetOf_spec hsub a ha)⟩
      · rw [upd_other _ _ _ _ hf] at h
        by_cases hff : f = fo
        · subst hff; rw [upd_same] at h; cases h; simp at hlv
        · rw [upd_other _ _ _ _ hff] at h; exact hA f r h hlv
    · intro s f h hrt
      simp only at h hrt ⊢
      by_cases hs : s = seat
      · subst hs; rw [upd_same] at h; cases h
        have hlx : (xstep st i (.renew s fo α)).lx i = st.x.lx fo := by simp [xstep]
        rw [hlx, show topicOf (xstep st i (.renew s fo α)) s i = topicOf st.x s fo by simp [topicOf, hlx]]
        exact hU s fo hbo hrt
      · rw [upd_other _ _ _ _ hs] at h
        obtain ⟨r, hr, -, -⟩ := hI1 s f h
        have hlx : (xstep st i (.renew seat fo α)).lx f = st.x.lx f := by simp [xstep, upd_other _ _ _ _ (fresh f r hr)]
        rw [hlx, topicOf_congr hlx]
        exact hU s f h hrt
    · intro s f h hrt T n hsl
      simp only at h hrt hsl ⊢
      by_cases hs : s = seat
      · subst hs; exact hR s fo hbo hrt T n hsl
      · rw [upd_other _ _ _ _ hs] at h; exact hR s f h hrt T n hsl
  | admit seat fo a hbt =>
    simp only [extraOK, Bool.and_eq_true, Bool.or_eq_true, Bool.not_eq_true'] at hx
    obtain ⟨⟨-, hhb⟩, hcpl⟩ := hx
    simp only [REntry.base] at hrej ⊢
    rcases applyAdmit_cases st.base seat fo a (ok && extraOK P st (.admit seat fo a hbt)) with
      h | ⟨r, hfo, hseat, hlive, ha, happ⟩
    · exfalso; apply hrej; simp only [SeatsModel.apply, applyArm, h]
    simp only [SeatsModel.apply, applyArm, happ]
    have hbo : st.base.liveBySeat seat = some fo := hseat ▸ hI2 fo r hfo hlive
    -- watermarks only rise: a heartbeat's is at least the last
    have hmk : ∀ o T, st.x.marks o T ≤ (match hbt with
        | some (T, w) => upd st.x.marks seat (upd (st.x.marks seat) T w)
        | none => st.x.marks) o T := by
      intro o T
      cases hbt with
      | none => exact Nat.le_refl _
      | some h =>
        obtain ⟨T0, w⟩ := h
        simp only [hbOK, Bool.and_eq_true] at hhb
        have hle : st.x.marks seat T0 ≤ w := by
          revert hhb; cases st.x.marks seat T0 <;> cases hbUpper st T0 <;> simp_all
        simp only [upd]
        by_cases ho : o = seat
        · subst ho; by_cases hT : T = T0
          · subst hT; simp [hle]
          · simp [hT]
        · simp [ho]
    cases ht : terminal a
    · -- the act recorded; the lease goes on
      simp only [ht, xstep, Bool.false_eq_true, ↓reduceIte]
      refine ⟨?_, ?_, ?_⟩
      · exact hA
      · intro s f h hrt
        have hU' := hU s f h hrt
        simp only [topicOf] at hU' ⊢
        by_cases hff : f = fo
        · subst hff
          have hs : s = seat := fence_seat hb h hbo
          subst hs
          simp only [upd_same]
          cases hef : effect a
          · simp only [Bool.false_eq_true, if_false]
            rcases hU' with h1 | ⟨o, ho, hle⟩
            · exact Or.inl h1
            · exact Or.inr ⟨o, ho, Nat.le_trans hle (Nat.add_le_add_right (hmk o _) _)⟩
          · simp only [if_true]
            -- a Run Thinker's effect is an `Actuate` or a `Report`, never a heartbeat: coupled, so covered
            obtain ⟨hkT0, hdR0⟩ := hrt
            have hkT : st.base.kinds s = some .Thinker := hkT0
            have hdR : st.x.domain s = some .run := hdR0
            obtain ⟨d, hd, hda⟩ := hA f r hfo hlive
            rw [hseat, hdR] at hd; cases hd
            have hdom := hda a ha
            have hnb : hbt = none := by
              cases hbt with
              | none => rfl
              | some h0 => simp [hbOK, hkT] at hhb
            subst hnb
            have hcp : coupled st s a none = true := by
              revert hef hdom; cases a <;> simp [coupled, effect, actDom, hkT]
            have hcov : covers P st s = true := by
              rcases hcpl with h1 | h1
              · rw [hcp] at h1; cases h1
              · exact h1
            unfold covers liveLease at hcov
            simp only [hbo, hfo, Option.map_some, Bool.and_eq_true] at hcov
            obtain ⟨-, hany⟩ := hcov
            obtain ⟨o, ho, ho2⟩ := List.any_eq_true.mp hany
            simp only [Bool.and_eq_true] at ho2
            have hlt := of_decide_eq_true ho2.2
            simp only [topicOf] at hlt
            refine Or.inr ⟨o, ho, ?_⟩
            show _ ≤ st.x.marks o _ + P.K
            omega
        · simp only [upd_other _ _ _ _ hff]
          rcases hU' with h1 | ⟨o, ho, hle⟩
          · exact Or.inl h1
          · exact Or.inr ⟨o, ho, Nat.le_trans hle (Nat.add_le_add_right (hmk o _) _)⟩
      · intro s f h hrt T n hsl
        obtain ⟨o, ho, hle⟩ := hR s f h hrt T n hsl
        exact ⟨o, ho, Nat.le_trans hle (hmk o T)⟩
    · -- a terminal act: recorded, then the lease ends and a Thinker's round seals
      simp only [ht, xstep, ↓reduceIte]
      have hend : ends st.base (fun g _ => g == fo) fo = true := by
        unfold ends; rw [hfo]
        simp only [hlive, hseat, hbo, Bool.true_and, decide_true]
        exact decide_eq_true rfl
      refine end_xinv P st (admitted st.base seat a) (fun g _ => g == fo) i _ rfl rfl rfl hA hU hR rfl rfl rfl
        hmk ?_
      intro s f hs hen
      have hff : f ≠ fo := fun he => by subst he; rw [hend] at hen; cases hen
      exact ⟨upd_other _ _ _ _ hff, sealEnded_keep _ _ _ _ hs hen⟩
  | endRound seat fo =>
    simp only [REntry.base] at hrej ⊢
    revert hrej; simp only [SeatsModel.apply, applyArm, xstep]
    split <;> (try split) <;>
      first
      | (intro h; exact absurd rfl h)
      | (intro _
         exact end_xinv P st st.base _ i _ rfl rfl rfl hA hU hR rfl rfl rfl (fun _ _ => Nat.le_refl _)
           fun s f hs hen => ⟨rfl, sealEnded_keep _ _ _ _ hs hen⟩)
  | endSeat seat =>
    simp only [REntry.base] at hrej ⊢
    revert hrej; simp only [SeatsModel.apply, applyArm]
    cases hls : st.base.liveBySeat seat with
    | none => intro h; exact absurd rfl h
    | some fs =>
      simp only [xstep, hls]
      split <;>
        first
        | (intro h; exact absurd rfl h)
        | (intro _
           exact end_xinv P st st.base _ i _ rfl rfl rfl hA hU hR rfl rfl rfl (fun _ _ => Nat.le_refl _)
             fun s f hs hen => ⟨rfl, sealEnded_keep _ _ _ _ hs hen⟩)
  | revoke t =>
    simp only [REntry.base] at hrej ⊢
    revert hrej; simp only [SeatsModel.apply, applyArm, xstep]
    split <;>
      first
      | (intro h; exact absurd rfl h)
      | (intro _
         exact end_xinv P st st.base _ i _ rfl rfl rfl hA hU hR rfl rfl rfl (fun _ _ => Nat.le_refl _)
           fun s f hs hen => ⟨rfl, sealEnded_keep _ _ _ _ hs hen⟩)
  | fence =>
    simp only [REntry.base] at hrej ⊢
    revert hrej; simp only [SeatsModel.apply, applyArm, xstep]
    split <;>
      first
      | (intro h; exact absurd rfl h)
      | (intro _
         exact end_xinv P st st.base _ i _ rfl rfl rfl hA hU hR rfl rfl rfl (fun _ _ => Nat.le_refl _)
           fun s f hs hen => ⟨rfl, sealEnded_keep _ _ _ _ hs hen⟩)
  | issue ks ds cs ss =>
    simp only [REntry.base] at hrej ⊢
    revert hrej; simp only [SeatsModel.apply, applyArm]
    have hnone := endAll_none st.base hb
    split <;> first
      | (intro h; exact absurd rfl h)
      | (intro _
         refine ⟨?_, ?_, ?_⟩
         · intro f r h hlv
           have h' : (endMany st.base fun _ _ => true).leases f = some r := h
           rw [endAll_dead st.base hb f r h'] at hlv; cases hlv
         · intro s f h
           have h' : (endMany st.base fun _ _ => true).liveBySeat s = some f := h
           rw [hnone s] at h'; cases h'
         · intro s f h
           have h' : (endMany st.base fun _ _ => true).liveBySeat s = some f := h
           rw [hnone s] at h'; cases h')
  | other =>
    simp only [REntry.base] at hrej ⊢
    revert hrej; simp only [SeatsModel.apply, applyArm, xstep]
    split <;> first | (intro h; exact absurd rfl h) | (intro _; exact ⟨hA, hU, hR⟩)

/-! ## The theorems -/

/-- **The model's invariant**, at any number of seats and principals, whatever the checks it leaves out decide. -/
theorem model_xinv (P : Params) : ∀ st : RState σ π δ, Reachable RInit (RNext P) st → XInv P st :=
  invariant (XInv P) (XInv P) (init_xinv P)
    (fun st _ hi ⟨i, e, ok, hidx, he⟩ => he ▸ xstep_inv P st i e ok hi hidx) (fun _ h => h)

/-- ADR-0039 §2 of the code's `apply`: a Run Thinker's live round has at most `K` effects unread by some cell
Observer. -/
theorem model_unread_bounded (P : Params) (st : RState σ π δ) (h : Reachable RInit (RNext P) st) :
    UnreadBounded P st :=
  (model_xinv P st h).2.2.1

/-- ADR-0039 §2 of the code's `apply`: a Run Thinker's live round is granted only after its last round was read to
the seal by some cell Observer, and that stays so while the round is live. -/
theorem model_prior_read (P : Params) (st : RState σ π δ) (h : Reachable RInit (RNext P) st) : PriorRead st :=
  (model_xinv P st h).2.2.2

/-- The Seats-shaped model's theorems hold here: ADR-0037 §1 and §4. -/
theorem model_seats_inv (P : Params) (st : RState σ π δ) (h : Reachable RInit (RNext P) st) : Inv st.base :=
  model_inv st.base (base_reach P st h)

/-- `Coupling.tla`'s `UnreadBounded`, `Unread + PriorUnread <= K`, of a Run Thinker whose cell has one Observer:
what that Observer has not read of the live round and of the sealed one together is at most `K`. -/
theorem model_unread_bounded_one (P : Params) (st : RState σ π δ) (h : Reachable RInit (RNext P) st) (s o : σ)
    (f : Nat) (hs : st.base.liveBySeat s = some f) (hrt : RunThinker st.base.kinds st.x s)
    (hone : cellObsOf st.base.kinds st.x s = [o]) (T : Topic σ) (n : Nat) (hsl : st.x.seals s = some (T, n)) :
    ((st.x.lx f).seq : Int) - st.x.marks o (topicOf st.x s f) + ((n : Int) - st.x.marks o T) ≤ P.K := by
  obtain ⟨o', ho', hle'⟩ := model_prior_read P st h s f hs hrt T n hsl
  rw [hone] at ho'
  simp only [List.mem_singleton] at ho'
  subst ho'
  rcases model_unread_bounded P st h s f hs hrt with h0 | ⟨o2, ho2, hle⟩
  · rw [h0]; omega
  · rw [hone] at ho2
    simp only [List.mem_singleton] at ho2
    subst ho2
    omega

/-- `NoAdmitWithoutLiveObserver`, at apply: an admitted `Actuate` or `Report` of a Thinker had a cell Observer with
a live lease whose watermark was within `K` of the Thinker's sequence. -/
theorem admit_coupled (P : Params) (st : RState σ π δ) (i : Nat) (s : σ) (f : Nat) (a : ActionKind) (ok : Bool)
    (h : (rapply P st i (.admit s f a none) ok).2 ≠ .rejected) (ha : a = .Actuate ∨ a = .Report)
    (hk : st.base.kinds s = some .Thinker) : covers P st s = true := by
  have hg := apply_gate _ _ _ _ h
  simp only [Bool.and_eq_true] at hg
  have hx := hg.2
  simp only [extraOK, Bool.and_eq_true, Bool.or_eq_true, Bool.not_eq_true'] at hx
  rcases hx.2 with hc | hc
  · exfalso
    rcases ha with rfl | rfl <;> simp [coupled, hk] at hc
  · exact hc

#print axioms model_xinv
#print axioms model_unread_bounded_one
#print axioms admit_coupled

end Topak.CouplingModel
