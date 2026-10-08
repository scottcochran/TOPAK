import TopakSpec.Emergency
/-!
# A decidable mirror of the `Emergency` encoding at `MaxRound = 2`, for checking it against TLC's state graphs

`TopakSpec/Emergency.lean` states `Emergency.tla` and `Emergency_live.tla` with sets as predicates and `quorate` and
`allowlisted` as `Prop`s, so its `Next` and `NextL` cannot be evaluated. As `Mirror/Seats.lean`: a concrete state,
`CState`, with Booleans and Boolean functions, a map `toState` into the encoding's states, and lists of successors,
`succC` for Emergency.tla's `Next` and `succLC` for Emergency_live.tla's `NextL`, with these proved:

- `next_iff`: from `toState c`, the encoding's `Next` reaches exactly the states `toState d` for `d` in `succC m c`;
- `nextL_iff`: the same of `NextL` and `succLC m c`;
- `init_iff`: a state satisfies the encoding's `Init` iff it is `toState cInit`;
- `eqC_iff`: the mirror's equality is equality of the encoding's states;
- one `*_iff` per property: Emergency.tla's six (`elhq_iff`, `elo_iff`, `nah_iff`, `caa_iff`, `tsc_iff`, `aif_iff`)
  and Emergency_live.tla's two over `ENABLED` (`enc_iff`, `ecwo_iff`), through `enabled_iff`: `ENABLED EmAdmit(t)` at
  a mirrored state is the Boolean `emAdmitB`.

The constants are fixed at the values TLC's results use: `MaxRound = 2` (`cfg m`), under every `Mut`. Nothing here is
proved for another `MaxRound`; the encoding's theorems are, for every `MaxRound`.

The state, and why it is canonical:
- a set of tools or of members is a Boolean function over the type;
- `quorate` and a call's `allowlisted`, `Prop`s in the encoding, are Booleans;
- `calls` is a Boolean function over `CallKey`, the 32 call records: a seat, a tool and two Booleans;
- `records` is a Boolean function over `RecKey`, the 48 activation records whose round is 1 or 2, with a holder and
  three Booleans for the approvers. At `MaxRound = 2` `Activate` writes no other round: it needs
  `em.round < MaxRound`, and the record's round is `em.round + 1`.

`toState` maps a key to the encoding's record and a Boolean function to the set of what it holds. Both maps are
injective, so the mirror's equality, field by field and key by key, is equality of the encoding's states (`eqC_iff`).

`spec/lean/GraphCheckEmergency.lean` evaluates these on TLC's dumped state graphs (`graph-check-emergency.sh`). The
theorems here are proved; the evaluation is a test.
-/

namespace Topak.Spec.Emergency.Mirror
open Topak.Spec Topak.Spec.Emergency

/-- The constants TLC's results use: `MaxRound = 2`, under every `Mut`. -/
abbrev cfg (m : Mut) : Cfg := ⟨m, 2⟩

def tools : List Tool := [.t1, .t2, .te, .tx]
def members : List Member := [.r1, .r2, .r3]
def holders : List Holder := [.h, .g, .none]
def seats : List Seat := [.emergency, .thinker]
def bools : List Bool := [false, true]

theorem mem_tools (t : Tool) : t ∈ tools := by cases t <;> simp [tools]
theorem mem_members (r : Member) : r ∈ members := by cases r <;> simp [members]
theorem mem_holders (w : Holder) : w ∈ holders := by cases w <;> simp [holders]
theorem mem_seats (s : Seat) : s ∈ seats := by cases s <;> simp [seats]
theorem mem_bools (b : Bool) : b ∈ bools := by cases b <;> simp [bools]

/-! ## The state -/

/-- A call record, its `allowlisted` a Boolean. -/
structure CallKey where
  seat : Seat
  tool : Tool
  allowlisted : Bool
  observed : Bool
  deriving DecidableEq

/-- An activation record at `MaxRound = 2`: `second` for round 2, else round 1; the holder; whether r1, r2 and r3
approved. -/
structure RecKey where
  second : Bool
  holder : Holder
  r1 : Bool
  r2 : Bool
  r3 : Bool
  deriving DecidableEq

def callKeys : List CallKey :=
  seats.flatMap fun s => tools.flatMap fun t => bools.flatMap fun a => bools.map fun o => ⟨s, t, a, o⟩

def recKeys : List RecKey :=
  bools.flatMap fun n => holders.flatMap fun w => bools.flatMap fun a => bools.flatMap fun b => bools.map fun c =>
    ⟨n, w, a, b, c⟩

theorem mem_callKeys (k : CallKey) : k ∈ callKeys := by
  cases k with
  | mk s t a o =>
    simp only [callKeys, List.mem_flatMap, List.mem_map]
    exact ⟨s, mem_seats s, t, mem_tools t, a, mem_bools a, o, mem_bools o, rfl⟩

theorem mem_recKeys (k : RecKey) : k ∈ recKeys := by
  cases k with
  | mk n w a b c =>
    simp only [recKeys, List.mem_flatMap, List.mem_map]
    exact ⟨n, mem_bools n, w, mem_holders w, a, mem_bools a, b, mem_bools b, c, mem_bools c, rfl⟩

/-- The emergency seat's lease, its envelope a Boolean function and `quorate` a Boolean. -/
structure CEm where
  live : Bool
  round : Nat
  holder : Holder
  envelope : Tool → Bool
  quorate : Bool
  grantor : Grantor
  renewed : Bool

/-- A state: each set a Boolean function over its elements' type, `calls` and `records` over their keys. -/
structure CState where
  domainTools : Tool → Bool
  approvals : Member → Bool
  em : CEm
  thinkerAllow : Tool → Bool
  obsLive : Bool
  calls : CallKey → Bool
  refused : Bool
  records : RecKey → Bool

/-- The set a Boolean function holds. -/
def toSet {α : Type} (f : α → Bool) : PSet α := fun a => f a = true

@[simp] theorem mem_toSet {α : Type} (f : α → Bool) (a : α) : a ∈ toSet f ↔ f a = true := Iff.rfl

/-- The images, under `g`, of the keys a Boolean function holds. -/
def image {κ α : Type} (f : κ → Bool) (g : κ → α) : PSet α := fun x => ∃ k, f k = true ∧ x = g k

def toEm (e : CEm) : EmRec :=
  { live := e.live, round := e.round, holder := e.holder, envelope := toSet e.envelope, quorate := e.quorate = true,
    grantor := e.grantor, renewed := e.renewed }

def toCall (k : CallKey) : CallRec := ⟨k.seat, k.tool, k.allowlisted = true, k.observed⟩

/-- Whether a member approved, by the key's three Booleans. -/
def RecKey.approved (k : RecKey) : Member → Bool
  | .r1 => k.r1
  | .r2 => k.r2
  | .r3 => k.r3

def toRec (k : RecKey) : ActRec := ⟨if k.second then 2 else 1, k.holder, toSet k.approved⟩

def toState (c : CState) : State :=
  { domainTools := toSet c.domainTools, approvals := toSet c.approvals, em := toEm c.em,
    thinkerAllow := toSet c.thinkerAllow, obsLive := c.obsLive, calls := image c.calls toCall,
    refused := c.refused, records := image c.records toRec }

/-! ## Equality -/

def eqF {α : Type} (xs : List α) (f g : α → Bool) : Bool := xs.all fun a => f a == g a

def eqEm (e f : CEm) : Bool :=
  e.live == f.live && e.round == f.round && e.holder == f.holder && eqF tools e.envelope f.envelope &&
    e.quorate == f.quorate && e.grantor == f.grantor && e.renewed == f.renewed

def eqC (c d : CState) : Bool :=
  eqF tools c.domainTools d.domainTools && eqF members c.approvals d.approvals && eqEm c.em d.em &&
    eqF tools c.thinkerAllow d.thinkerAllow && c.obsLive == d.obsLive && eqF callKeys c.calls d.calls &&
    c.refused == d.refused && eqF recKeys c.records d.records

theorem bool_eq_of_prop {a b : Bool} (h : (a = true) = (b = true)) : a = b := by
  cases a <;> cases b <;> simp_all

private theorem eqF_iff {α : Type} {xs : List α} (hxs : ∀ a, a ∈ xs) (f g : α → Bool) : eqF xs f g = true ↔ f = g := by
  simp only [eqF, List.all_eq_true, beq_iff_eq]
  exact ⟨fun h => funext fun a => h a (hxs a), fun h a _ => congrFun h a⟩

theorem toSet_inj {α : Type} {f g : α → Bool} : toSet f = toSet g ↔ f = g :=
  ⟨fun h => funext fun a => bool_eq_of_prop (congrFun h a), fun h => h ▸ rfl⟩

theorem image_inj {κ α : Type} {g : κ → α} (hg : ∀ k k', g k = g k' → k = k') {f f' : κ → Bool} :
    image f g = image f' g ↔ f = f' := by
  constructor
  · intro h
    funext k
    have hk : image f g (g k) ↔ image f' g (g k) := by rw [h]
    apply bool_eq_of_prop
    apply propext
    constructor
    · intro hf
      obtain ⟨k', hk', he⟩ := hk.mp ⟨k, hf, rfl⟩
      rw [hg k k' he]; exact hk'
    · intro hf
      obtain ⟨k', hk', he⟩ := hk.mpr ⟨k, hf, rfl⟩
      rw [hg k k' he]; exact hk'
  · intro h; rw [h]

theorem toCall_inj (k k' : CallKey) (h : toCall k = toCall k') : k = k' := by
  cases k with
  | mk s t a o =>
    cases k' with
    | mk s' t' a' o' =>
      simp only [toCall, CallRec.mk.injEq] at h
      obtain ⟨h1, h2, h3, h4⟩ := h
      cases h1; cases h2; cases bool_eq_of_prop h3; cases h4; rfl

theorem toRec_inj (k k' : RecKey) (h : toRec k = toRec k') : k = k' := by
  cases k with
  | mk n w a b c =>
    cases k' with
    | mk n' w' a' b' c' =>
      simp only [toRec, ActRec.mk.injEq] at h
      obtain ⟨h1, h2, h3⟩ := h
      have hn : n = n' := by cases n <;> cases n' <;> simp_all
      have ha : a = a' := bool_eq_of_prop (congrFun h3 .r1)
      have hb : b = b' := bool_eq_of_prop (congrFun h3 .r2)
      have hc : c = c' := bool_eq_of_prop (congrFun h3 .r3)
      cases hn; cases h2; cases ha; cases hb; cases hc; rfl

theorem toEm_inj (e f : CEm) : toEm e = toEm f ↔ eqEm e f = true := by
  simp only [eqEm, Bool.and_eq_true, beq_iff_eq, eqF_iff mem_tools]
  constructor
  · intro h
    simp only [toEm, EmRec.mk.injEq] at h
    obtain ⟨h1, h2, h3, h4, h5, h6, h7⟩ := h
    exact ⟨⟨⟨⟨⟨⟨h1, h2⟩, h3⟩, toSet_inj.mp h4⟩, bool_eq_of_prop h5⟩, h6⟩, h7⟩
  · rintro ⟨⟨⟨⟨⟨⟨h1, h2⟩, h3⟩, h4⟩, h5⟩, h6⟩, h7⟩
    cases e; cases f
    simp only at h1 h2 h3 h4 h5 h6 h7
    subst h1; subst h2; subst h3; subst h4; subst h5; subst h6; subst h7; rfl

theorem eqC_iff (c d : CState) : eqC c d = true ↔ toState c = toState d := by
  simp only [eqC, Bool.and_eq_true, beq_iff_eq, eqF_iff mem_tools, eqF_iff mem_members, eqF_iff mem_callKeys,
    eqF_iff mem_recKeys, toState, State.mk.injEq, toSet_inj, image_inj toCall_inj, image_inj toRec_inj, toEm_inj,
    and_assoc]

/-! ## Sets, as Boolean functions -/

/-- `S \cup {x}` -/
def add {α : Type} [DecidableEq α] (f : α → Bool) (x : α) : α → Bool := fun a => f a || decide (a = x)
/-- `S \ {x}` -/
def remove {α : Type} [DecidableEq α] (f : α → Bool) (x : α) : α → Bool := fun a => f a && !decide (a = x)
/-- `{x}` -/
def single {α : Type} [DecidableEq α] (x : α) : α → Bool := fun a => decide (a = x)

theorem toSet_add {α : Type} [DecidableEq α] (f : α → Bool) (x : α) : toSet (add f x) = toSet f ∪ {x} :=
  PSet.ext fun a => by simp [add]

theorem toSet_single {α : Type} [DecidableEq α] (x : α) : toSet (single x) = {x} :=
  PSet.ext fun a => by simp [single]

theorem toSet_false {α : Type} : toSet (fun _ : α => false) = ∅ :=
  PSet.ext fun _ => ⟨Bool.false_ne_true, False.elim⟩

theorem image_false {κ α : Type} (g : κ → α) : image (fun _ => false) g = ∅ :=
  PSet.ext fun _ => ⟨fun ⟨_, h, _⟩ => Bool.false_ne_true h, False.elim⟩

theorem image_add {κ α : Type} [DecidableEq κ] (f : κ → Bool) (g : κ → α) (k : κ) :
    image (add f k) g = image f g ∪ {g k} := by
  apply PSet.ext; intro x
  constructor
  · rintro ⟨k', hk', rfl⟩
    simp only [add, Bool.or_eq_true, decide_eq_true_eq] at hk'
    rcases hk' with h | rfl
    · exact Or.inl ⟨k', h, rfl⟩
    · exact Or.inr rfl
  · rintro (⟨k', hk', rfl⟩ | h)
    · exact ⟨k', by simp [add, hk'], rfl⟩
    · exact ⟨k, by simp [add], h⟩

theorem image_remove {κ α : Type} [DecidableEq κ] {g : κ → α} (hg : ∀ k k', g k = g k' → k = k')
    (f : κ → Bool) (k : κ) : image (remove f k) g = image f g \ {g k} := by
  apply PSet.ext; intro x
  constructor
  · rintro ⟨k', hk', rfl⟩
    simp only [remove, Bool.and_eq_true, Bool.not_eq_true', decide_eq_false_iff_not] at hk'
    exact ⟨⟨k', hk'.1, rfl⟩, fun h => hk'.2 (hg _ _ h)⟩
  · rintro ⟨⟨k', hk', rfl⟩, hne⟩
    refine ⟨k', ?_, rfl⟩
    simp only [remove, Bool.and_eq_true, Bool.not_eq_true', decide_eq_false_iff_not]
    exact ⟨hk', fun h => hne (by rw [h]; rfl)⟩

theorem image_single {κ α : Type} [DecidableEq κ] (g : κ → α) (k : κ) : image (single k) g = {g k} := by
  apply PSet.ext; intro x
  constructor
  · rintro ⟨k', hk', rfl⟩
    simp only [single, decide_eq_true_eq] at hk'
    rw [hk']; rfl
  · intro h; exact ⟨k, by simp [single], h⟩

/-! ## The guards, as Booleans -/

/-- `Quorate(S)`: two distinct members. -/
def quorateB (f : Member → Bool) : Bool := f .r1 && f .r2 || f .r1 && f .r3 || f .r2 && f .r3

private theorem quorateB_iff (f : Member → Bool) : quorateB f = true ↔ Quorate (toSet f) := by
  constructor
  · intro h
    simp only [quorateB, Bool.or_eq_true, Bool.and_eq_true] at h
    rcases h with (⟨h1, h2⟩ | ⟨h1, h3⟩) | ⟨h2, h3⟩
    · exact ⟨.r1, .r2, h1, h2, by decide⟩
    · exact ⟨.r1, .r3, h1, h3, by decide⟩
    · exact ⟨.r2, .r3, h2, h3, by decide⟩
  · rintro ⟨a, b, ha, hb, hab⟩
    have ha : f a = true := ha
    have hb : f b = true := hb
    cases a <;> cases b <;> simp_all [quorateB]

/-- `X1 == Mut = "M_X1" /\ Quorate(approvals)` -/
def x1B (m : Mut) (c : CState) : Bool := decide (m = .M_X1) && quorateB c.approvals

private theorem x1B_iff (m : Mut) (c : CState) : x1B m c = true ↔ X1 (cfg m) (toState c) := by
  simp only [x1B, Bool.and_eq_true, decide_eq_true_eq, quorateB_iff]
  exact Iff.rfl

/-- `EmCall(t)`'s `IF`: `t \in em.envelope \/ X1` -/
def emCondB (m : Mut) (c : CState) (t : Tool) : Bool := c.em.envelope t || x1B m c

private theorem emCondB_iff (m : Mut) (c : CState) (t : Tool) :
    emCondB m c t = true ↔ (t ∈ (toState c).em.envelope ∨ X1 (cfg m) (toState c)) := by
  simp only [emCondB, Bool.or_eq_true, x1B_iff]
  exact Iff.rfl

/-- `ThinkerCall(t)`'s `IF`: `(t \in thinkerAllow \/ X1) /\ (obsLive \/ Mut = "M_UNCOUPLE")` -/
def thCondB (m : Mut) (c : CState) (t : Tool) : Bool :=
  (c.thinkerAllow t || x1B m c) && (c.obsLive || decide (m = .M_UNCOUPLE))

private theorem thCondB_iff (m : Mut) (c : CState) (t : Tool) :
    thCondB m c t = true ↔ ((t ∈ (toState c).thinkerAllow ∨ X1 (cfg m) (toState c)) ∧
      ((toState c).obsLive = true ∨ (cfg m).m = .M_UNCOUPLE)) := by
  simp only [thCondB, Bool.and_eq_true, Bool.or_eq_true, x1B_iff, decide_eq_true_eq]
  exact Iff.rfl

/-- `EmCoupled == \/ Mut = "M_EMCOUPLE" \/ (Mut = "M_EMCOUPLE2" /\ em.round >= 2)` -/
def emCoupledB (m : Mut) (c : CState) : Bool :=
  decide (m = .M_EMCOUPLE) || decide (m = .M_EMCOUPLE2) && decide (c.em.round ≥ 2)

private theorem emCoupledB_iff (m : Mut) (c : CState) : emCoupledB m c = true ↔ EmCoupled (cfg m) (toState c) := by
  simp only [emCoupledB, Bool.or_eq_true, Bool.and_eq_true, decide_eq_true_eq]
  exact Iff.rfl

private theorem bool_false_iff {b : Bool} {P : Prop} (h : b = true ↔ P) : b = false ↔ ¬ P := by
  cases b
  · exact ⟨fun _ hp => Bool.false_ne_true (h.mpr hp), fun _ => rfl⟩
  · exact ⟨fun h' => Bool.noConfusion h', fun hn => absurd (h.mp rfl) hn⟩

/-- `EmAdmit(t)`'s guard: `em.live /\ (t \in em.envelope \/ X1) /\ (obsLive \/ ~EmCoupled)` -/
def emAdmitB (m : Mut) (c : CState) (t : Tool) : Bool := c.em.live && emCondB m c t && (c.obsLive || !emCoupledB m c)

private theorem emAdmitB_iff (m : Mut) (c : CState) (t : Tool) :
    emAdmitB m c t = true ↔ ((toState c).em.live = true ∧ (t ∈ (toState c).em.envelope ∨ X1 (cfg m) (toState c)) ∧
      ((toState c).obsLive = true ∨ ¬ EmCoupled (cfg m) (toState c))) := by
  simp only [emAdmitB, Bool.and_eq_true, Bool.or_eq_true, Bool.not_eq_true', emCondB_iff,
    bool_false_iff (emCoupledB_iff m c)]
  exact ⟨fun ⟨⟨h1, h2⟩, h3⟩ => ⟨h1, h2, h3⟩, fun ⟨h1, h2, h3⟩ => ⟨⟨h1, h2⟩, h3⟩⟩

/-- `h \in (IF Mut = "M_AGENT" THEN Holders ELSE Persons)` -/
def holderB (m : Mut) (who : Holder) : Bool := if m = .M_AGENT then who == .h || who == .g else who == .h

private theorem holderB_iff (m : Mut) (who : Holder) :
    holderB m who = true ↔ who ∈ (if m = .M_AGENT then Holders else Persons) := by
  unfold holderB
  by_cases hm : m = .M_AGENT
  · rw [if_pos hm, if_pos hm]
    cases who <;> simp [Holders, Persons, Agents]
  · rw [if_neg hm, if_neg hm]
    cases who <;> simp [Persons]

/-- `Activate(h)`'s guard at `MaxRound = 2`. -/
def activateB (m : Mut) (c : CState) (who : Holder) : Bool :=
  !c.em.live && decide (c.em.round < 2) && (quorateB c.approvals || decide (m = .M_NOQUORUM)) && holderB m who

private theorem activateB_iff (m : Mut) (c : CState) (who : Holder) :
    activateB m c who = true ↔ ((toState c).em.live = false ∧ (toState c).em.round < (cfg m).MaxRound ∧
      (Quorate (toState c).approvals ∨ (cfg m).m = .M_NOQUORUM) ∧
      who ∈ (if (cfg m).m = .M_AGENT then Holders else Persons)) := by
  simp only [activateB, Bool.and_eq_true, Bool.not_eq_true', decide_eq_true_eq, Bool.or_eq_true, quorateB_iff,
    holderB_iff]
  exact ⟨fun ⟨⟨⟨h1, h2⟩, h3⟩, h4⟩ => ⟨h1, h2, h3, h4⟩, fun ⟨h1, h2, h3, h4⟩ => ⟨⟨⟨h1, h2⟩, h3⟩, h4⟩⟩

/-! ## The successors -/

def promoteC (c : CState) (t : Tool) : CState := { c with domainTools := add c.domainTools t }
def approveC (c : CState) (r : Member) : CState := { c with approvals := add c.approvals r }
/-- The record `Activate(h)` appends, at `em.round < 2`: round `em.round + 1`, the holder, the approvals. -/
def recKeyOf (c : CState) (who : Holder) : RecKey :=
  ⟨c.em.round == 1, who, c.approvals .r1, c.approvals .r2, c.approvals .r3⟩
def activateC (c : CState) (who : Holder) : CState :=
  { c with
    em := ⟨true, c.em.round + 1, who, add c.domainTools .te, quorateB c.approvals, .roster, false⟩,
    records := add c.records (recKeyOf c who),
    approvals := fun _ => false }
def endC (c : CState) : CState := { c with em := { c.em with live := false } }
def regrantC (c : CState) : CState :=
  { c with em := { c.em with live := true, round := c.em.round + 1, quorate := false, grantor := .operator } }
def renewC (c : CState) : CState := { c with em := { c.em with renewed := true } }
def toggleC (c : CState) : CState := { c with obsLive := !c.obsLive }
/-- An admitted call: `calls' = {[seat |-> s, tool |-> t, allowlisted |-> al, observed |-> obsLive]}` -/
def admitC (c : CState) (s : Seat) (t : Tool) (al : Bool) : CState := { c with calls := single ⟨s, t, al, c.obsLive⟩ }
def refuseC (c : CState) : CState := { c with refused := true }
def eraseC (c : CState) (k : RecKey) : CState := { c with records := remove c.records k }

/-- `\E t \in Domain : Promote(t)` -/
def promoteSucc (c : CState) : List CState :=
  [Tool.t1, .t2].filterMap fun t => if c.domainTools t then none else some (promoteC c t)
/-- `\E r \in Roster : Approve(r)` -/
def approveSucc (c : CState) : List CState :=
  members.filterMap fun r => if c.approvals r then none else some (approveC c r)
/-- `\E h \in Holders : Activate(h)` -/
def activateSucc (m : Mut) (c : CState) : List CState :=
  [Holder.h, .g].filterMap fun who => if activateB m c who then some (activateC c who) else none
/-- `EndEm` -/
def endSucc (c : CState) : List CState := if c.em.live then [endC c] else []
/-- `Regrant` -/
def regrantSucc (m : Mut) (c : CState) : List CState :=
  if decide (m = .M_REGRANT) && !c.em.live && decide (0 < c.em.round) && decide (c.em.round < 2) then [regrantC c]
  else []
/-- `Renew` -/
def renewSucc (m : Mut) (c : CState) : List CState := if decide (m = .M_RENEW) && c.em.live then [renewC c] else []
/-- `ObsToggle` -/
def toggleSucc (c : CState) : List CState := [toggleC c]
/-- `EmCall(t)` for each tool: the admit or the refusal its `IF` picks. -/
def emCallC (m : Mut) (c : CState) (t : Tool) : CState :=
  if emCondB m c t then admitC c .emergency t (c.em.envelope t) else refuseC c
/-- `\E t \in Tools : EmCall(t)` -/
def emCallSucc (m : Mut) (c : CState) : List CState := if c.em.live then tools.map (emCallC m c) else []
/-- `ThinkerCall(t)` for each tool. -/
def thinkerC (m : Mut) (c : CState) (t : Tool) : CState :=
  if thCondB m c t then admitC c .thinker t (c.thinkerAllow t) else refuseC c
/-- `\E t \in Tools : ThinkerCall(t)` -/
def thinkerSucc (m : Mut) (c : CState) : List CState := tools.map (thinkerC m c)
/-- `\E x \in records : Erase(x)` -/
def eraseSucc (m : Mut) (c : CState) : List CState :=
  if m = .M_ERASE then recKeys.filterMap fun k => if c.records k then some (eraseC c k) else none else []
/-- `EmAdmit(t) \/ EmRefuse(t)` for each tool: exactly one is enabled while the seat is live. -/
def emLC (m : Mut) (c : CState) (t : Tool) : CState :=
  if emAdmitB m c t then admitC c .emergency t (c.em.envelope t) else refuseC c
/-- `\E t \in Tools : EmAdmit(t) \/ EmRefuse(t)` -/
def emLSucc (m : Mut) (c : CState) : List CState := if c.em.live then tools.map (emLC m c) else []

/-- `Next`'s successors, disjunct by disjunct. -/
def succC (m : Mut) (c : CState) : List CState :=
  promoteSucc c ++ (approveSucc c ++ (activateSucc m c ++ (endSucc c ++ (regrantSucc m c ++ (renewSucc m c ++
    (toggleSucc c ++ ((emCallSucc m c ++ thinkerSucc m c) ++ eraseSucc m c)))))))

/-- `NextL`'s successors: `Next`'s, with `EmCall(t)` replaced by `EmAdmit(t) \/ EmRefuse(t)`. -/
def succLC (m : Mut) (c : CState) : List CState :=
  promoteSucc c ++ (approveSucc c ++ (activateSucc m c ++ (endSucc c ++ (regrantSucc m c ++ (renewSucc m c ++
    (toggleSucc c ++ ((emLSucc m c ++ thinkerSucc m c) ++ eraseSucc m c)))))))

theorem ex_append (l₁ l₂ : List CState) (P : CState → Prop) :
    (∃ d, d ∈ l₁ ++ l₂ ∧ P d) ↔ (∃ d, d ∈ l₁ ∧ P d) ∨ (∃ d, d ∈ l₂ ∧ P d) := by
  simp only [List.mem_append, or_and_right, exists_or]

/-! ### Action by action -/

private theorem promote_iff (c : CState) (S : State) :
    (∃ t, t ∈ Domain ∧ Promote t (toState c) S) ↔ ∃ d, d ∈ promoteSucc c ∧ S = toState d := by
  constructor
  · rintro ⟨t, hD, ⟨-, hn⟩, rfl⟩
    have hf : c.domainTools t = false := by
      cases h : c.domainTools t
      · rfl
      · exact absurd h hn
    refine ⟨promoteC c t, ?_, ?_⟩
    · simp only [promoteSucc, List.mem_filterMap]
      refine ⟨t, ?_, by rw [hf]; rfl⟩
      rcases hD with rfl | rfl <;> simp
    · show _ = { toState c with domainTools := toSet (add c.domainTools t) }
      rw [toSet_add]; rfl
  · rintro ⟨d, hd, rfl⟩
    simp only [promoteSucc, List.mem_filterMap] at hd
    obtain ⟨t, ht, hd⟩ := hd
    have hD : t ∈ Domain := by
      simp only [List.mem_cons, List.mem_nil_iff, or_false] at ht
      rcases ht with rfl | rfl
      · exact Or.inl rfl
      · exact Or.inr rfl
    split at hd
    · cases hd
    · rename_i hf
      cases hd
      refine ⟨t, hD, ⟨hD, hf⟩, ?_⟩
      show { toState c with domainTools := toSet (add c.domainTools t) } =
        { toState c with domainTools := toSet c.domainTools ∪ {t} }
      rw [toSet_add]

private theorem approve_iff (c : CState) (S : State) :
    (∃ r, Approve r (toState c) S) ↔ ∃ d, d ∈ approveSucc c ∧ S = toState d := by
  constructor
  · rintro ⟨r, ⟨-, hn⟩, rfl⟩
    have hf : c.approvals r = false := by
      cases h : c.approvals r
      · rfl
      · exact absurd h hn
    refine ⟨approveC c r, ?_, ?_⟩
    · simp only [approveSucc, List.mem_filterMap]
      exact ⟨r, mem_members r, by rw [hf]; rfl⟩
    · show _ = { toState c with approvals := toSet (add c.approvals r) }
      rw [toSet_add]; rfl
  · rintro ⟨d, hd, rfl⟩
    simp only [approveSucc, List.mem_filterMap] at hd
    obtain ⟨r, -, hd⟩ := hd
    split at hd
    · cases hd
    · rename_i hf
      cases hd
      refine ⟨r, ⟨trivial, hf⟩, ?_⟩
      show { toState c with approvals := toSet (add c.approvals r) } = { toState c with approvals := toSet c.approvals ∪ {r} }
      rw [toSet_add]

theorem rec_of (c : CState) (who : Holder) (hr : c.em.round < 2) :
    toRec (recKeyOf c who) = ⟨c.em.round + 1, who, toSet c.approvals⟩ := by
  have ha : toSet (recKeyOf c who).approved = toSet c.approvals := by
    funext r; cases r <;> rfl
  have hn : (if (recKeyOf c who).second = true then 2 else 1) = c.em.round + 1 := by
    show (if (c.em.round == 1) = true then 2 else 1) = c.em.round + 1
    cases h : c.em.round with
    | zero => rfl
    | succ n =>
      cases n with
      | zero => rfl
      | succ n => rw [h] at hr; exact absurd hr (by omega)
  show (⟨if (recKeyOf c who).second = true then 2 else 1, who, toSet (recKeyOf c who).approved⟩ : ActRec) = _
  rw [ha, hn]

theorem activate_eq (c : CState) (who : Holder) (hr : c.em.round < 2) :
    toState (activateC c who) = { toState c with
      em := { live := true, round := (toState c).em.round + 1, holder := who,
              envelope := (toState c).domainTools ∪ {.te}, quorate := Quorate (toState c).approvals,
              grantor := .roster, renewed := false },
      records := (toState c).records ∪ {⟨(toState c).em.round + 1, who, (toState c).approvals⟩},
      approvals := ∅ } := by
  refine State.eq_of rfl toSet_false ?_ rfl rfl rfl rfl ?_
  · show (⟨true, c.em.round + 1, who, toSet (add c.domainTools .te), quorateB c.approvals = true, .roster, false⟩
      : EmRec) = ⟨true, c.em.round + 1, who, toSet c.domainTools ∪ {.te}, Quorate (toSet c.approvals), .roster, false⟩
    rw [toSet_add, propext (quorateB_iff c.approvals)]
  · show image (add c.records (recKeyOf c who)) toRec = image c.records toRec ∪ {⟨c.em.round + 1, who, toSet c.approvals⟩}
    rw [image_add, rec_of c who hr]

private theorem activate_iff (m : Mut) (c : CState) (S : State) :
    (∃ who, who ∈ Holders ∧ Activate (cfg m) who (toState c) S) ↔ ∃ d, d ∈ activateSucc m c ∧ S = toState d := by
  constructor
  · rintro ⟨who, hw, hl, hr, hq, hh, rfl⟩
    refine ⟨activateC c who, ?_, (activate_eq c who hr).symm⟩
    simp only [activateSucc, List.mem_filterMap]
    refine ⟨who, ?_, ?_⟩
    · rcases hw with h | h
      · rw [h]; simp
      · rw [h]; simp
    · rw [if_pos ((activateB_iff m c who).mpr ⟨hl, hr, hq, hh⟩)]
  · rintro ⟨d, hd, rfl⟩
    simp only [activateSucc, List.mem_filterMap] at hd
    obtain ⟨who, hw, hd⟩ := hd
    split at hd
    · rename_i hb
      cases hd
      obtain ⟨hl, hr, hq, hh⟩ := (activateB_iff m c who).mp hb
      refine ⟨who, ?_, hl, hr, hq, hh, activate_eq c who hr⟩
      simp only [List.mem_cons, List.mem_nil_iff, or_false] at hw
      rcases hw with rfl | rfl
      · exact Or.inl rfl
      · exact Or.inr rfl
    · cases hd

private theorem end_iff (c : CState) (S : State) : EndEm (toState c) S ↔ ∃ d, d ∈ endSucc c ∧ S = toState d := by
  constructor
  · rintro ⟨hl, rfl⟩
    have hl' : c.em.live = true := hl
    exact ⟨endC c, by simp [endSucc, hl'], rfl⟩
  · rintro ⟨d, hd, rfl⟩
    unfold endSucc at hd
    split at hd
    · rename_i hl
      simp only [List.mem_singleton] at hd
      subst hd
      exact ⟨hl, rfl⟩
    · cases hd

theorem regrant_eq (c : CState) :
    toState (regrantC c) = { toState c with
      em := { (toState c).em with
              live := true, round := (toState c).em.round + 1, quorate := False, grantor := .operator } } := by
  refine State.eq_of rfl rfl ?_ rfl rfl rfl rfl rfl
  show (⟨true, c.em.round + 1, c.em.holder, toSet c.em.envelope, false = true, .operator, c.em.renewed⟩ : EmRec) =
    ⟨true, c.em.round + 1, c.em.holder, toSet c.em.envelope, False, .operator, c.em.renewed⟩
  rw [Bool.false_eq_true]

private theorem regrant_iff (m : Mut) (c : CState) (S : State) :
    Regrant (cfg m) (toState c) S ↔ ∃ d, d ∈ regrantSucc m c ∧ S = toState d := by
  constructor
  · rintro ⟨hm, hl, hp, hr, rfl⟩
    have hb : (decide (m = .M_REGRANT) && !c.em.live && decide (0 < c.em.round) && decide (c.em.round < 2)) = true := by
      have hl' : c.em.live = false := hl
      simp only [Bool.and_eq_true, decide_eq_true_eq, Bool.not_eq_true']
      exact ⟨⟨⟨hm, hl'⟩, hp⟩, hr⟩
    refine ⟨regrantC c, ?_, (regrant_eq c).symm⟩
    simp only [regrantSucc, hb, if_true, List.mem_singleton]
  · rintro ⟨d, hd, rfl⟩
    unfold regrantSucc at hd
    split at hd
    · rename_i hb
      simp only [List.mem_singleton] at hd
      subst hd
      simp only [Bool.and_eq_true, decide_eq_true_eq, Bool.not_eq_true'] at hb
      obtain ⟨⟨⟨hm, hl⟩, hp⟩, hr⟩ := hb
      exact ⟨hm, hl, hp, hr, regrant_eq c⟩
    · cases hd

private theorem renew_iff (m : Mut) (c : CState) (S : State) :
    Renew (cfg m) (toState c) S ↔ ∃ d, d ∈ renewSucc m c ∧ S = toState d := by
  constructor
  · rintro ⟨hm, hl, rfl⟩
    have hl' : c.em.live = true := hl
    have hm' : m = .M_RENEW := hm
    exact ⟨renewC c, by simp [renewSucc, hl', hm'], rfl⟩
  · rintro ⟨d, hd, rfl⟩
    unfold renewSucc at hd
    split at hd
    · rename_i hb
      simp only [List.mem_singleton] at hd
      subst hd
      simp only [Bool.and_eq_true, decide_eq_true_eq] at hb
      exact ⟨hb.1, hb.2, rfl⟩
    · cases hd

private theorem toggle_iff (c : CState) (S : State) : ObsToggle (toState c) S ↔ ∃ d, d ∈ toggleSucc c ∧ S = toState d := by
  constructor
  · rintro rfl
    exact ⟨toggleC c, List.mem_singleton.mpr rfl, rfl⟩
  · rintro ⟨d, hd, rfl⟩
    simp only [toggleSucc, List.mem_singleton] at hd
    subst hd
    rfl

/-- An admitted call, in the encoding's terms. -/
theorem admit_eq (c : CState) (s : Seat) (t : Tool) (al : Bool) :
    toState (admitC c s t al) = { toState c with calls := {⟨s, t, al = true, c.obsLive⟩} } := by
  show { toState c with calls := image (single (⟨s, t, al, c.obsLive⟩ : CallKey)) toCall } = _
  rw [image_single]; rfl

private theorem emCall_iff (m : Mut) (c : CState) (S : State) :
    (∃ t, EmCall (cfg m) t (toState c) S) ↔ ∃ d, d ∈ emCallSucc m c ∧ S = toState d := by
  constructor
  · rintro ⟨t, hl, hthen, helse, hdt, hap, hem, hta, hobs, hrec⟩
    have hl' : c.em.live = true := hl
    refine ⟨emCallC m c t, ?_, ?_⟩
    · simp only [emCallSucc, hl', if_true, List.mem_map]
      exact ⟨t, mem_tools t, rfl⟩
    · cases hb : emCondB m c t
      · have hn : ¬ (t ∈ (toState c).em.envelope ∨ X1 (cfg m) (toState c)) := fun h => by
          rw [(emCondB_iff m c t).mpr h] at hb; cases hb
        obtain ⟨hr, hc⟩ := helse hn
        have he : emCallC m c t = refuseC c := by simp [emCallC, hb]
        rw [he]
        exact State.eq_of hdt hap hem hta hobs hc hr hrec
      · obtain ⟨hc, hr⟩ := hthen ((emCondB_iff m c t).mp hb)
        have he : emCallC m c t = admitC c .emergency t (c.em.envelope t) := by simp [emCallC, hb]
        rw [he, admit_eq]
        exact State.eq_of hdt hap hem hta hobs hc hr hrec
  · rintro ⟨d, hd, rfl⟩
    unfold emCallSucc at hd
    split at hd
    · rename_i hl
      obtain ⟨t, -, rfl⟩ := List.mem_map.mp hd
      refine ⟨t, ?_⟩
      cases hb : emCondB m c t
      · have he : emCallC m c t = refuseC c := by simp [emCallC, hb]
        rw [he]
        refine ⟨hl, fun h => ?_, fun _ => ⟨rfl, rfl⟩, rfl, rfl, rfl, rfl, rfl, rfl⟩
        rw [(emCondB_iff m c t).mpr h] at hb; cases hb
      · have he : emCallC m c t = admitC c .emergency t (c.em.envelope t) := by simp [emCallC, hb]
        rw [he, admit_eq]
        refine ⟨hl, fun _ => ⟨rfl, rfl⟩, fun h => absurd ((emCondB_iff m c t).mp hb) h, rfl, rfl, rfl, rfl, rfl, rfl⟩
    · cases hd

private theorem thinker_iff (m : Mut) (c : CState) (S : State) :
    (∃ t, ThinkerCall (cfg m) t (toState c) S) ↔ ∃ d, d ∈ thinkerSucc m c ∧ S = toState d := by
  constructor
  · rintro ⟨t, hthen, helse, hdt, hap, hem, hta, hobs, hrec⟩
    refine ⟨thinkerC m c t, List.mem_map.mpr ⟨t, mem_tools t, rfl⟩, ?_⟩
    cases hb : thCondB m c t
    · have hn : ¬ ((t ∈ (toState c).thinkerAllow ∨ X1 (cfg m) (toState c)) ∧
          ((toState c).obsLive = true ∨ (cfg m).m = .M_UNCOUPLE)) := fun h => by
        rw [(thCondB_iff m c t).mpr h] at hb; cases hb
      obtain ⟨hr, hc⟩ := helse hn
      have he : thinkerC m c t = refuseC c := by simp [thinkerC, hb]
      rw [he]
      exact State.eq_of hdt hap hem hta hobs hc hr hrec
    · obtain ⟨hc, hr⟩ := hthen ((thCondB_iff m c t).mp hb)
      have he : thinkerC m c t = admitC c .thinker t (c.thinkerAllow t) := by simp [thinkerC, hb]
      rw [he, admit_eq]
      exact State.eq_of hdt hap hem hta hobs hc hr hrec
  · rintro ⟨d, hd, rfl⟩
    obtain ⟨t, -, rfl⟩ := List.mem_map.mp hd
    refine ⟨t, ?_⟩
    cases hb : thCondB m c t
    · have he : thinkerC m c t = refuseC c := by simp [thinkerC, hb]
      rw [he]
      refine ⟨fun h => ?_, fun _ => ⟨rfl, rfl⟩, rfl, rfl, rfl, rfl, rfl, rfl⟩
      rw [(thCondB_iff m c t).mpr h] at hb; cases hb
    · have he : thinkerC m c t = admitC c .thinker t (c.thinkerAllow t) := by simp [thinkerC, hb]
      rw [he, admit_eq]
      refine ⟨fun _ => ⟨rfl, rfl⟩, fun h => absurd ((thCondB_iff m c t).mp hb) h, rfl, rfl, rfl, rfl, rfl, rfl⟩

theorem erase_eq (c : CState) (k : RecKey) :
    toState (eraseC c k) = { toState c with records := (toState c).records \ {toRec k} } := by
  show { toState c with records := image (remove c.records k) toRec } = _
  rw [image_remove toRec_inj]; rfl

private theorem erase_iff (m : Mut) (c : CState) (S : State) :
    (∃ x, x ∈ (toState c).records ∧ Erase (cfg m) x (toState c) S) ↔ ∃ d, d ∈ eraseSucc m c ∧ S = toState d := by
  constructor
  · rintro ⟨x, ⟨k, hk, rfl⟩, hm, -, rfl⟩
    have hm' : m = .M_ERASE := hm
    refine ⟨eraseC c k, ?_, (erase_eq c k).symm⟩
    rw [eraseSucc, if_pos hm', List.mem_filterMap]
    exact ⟨k, mem_recKeys k, by rw [hk]; rfl⟩
  · rintro ⟨d, hd, rfl⟩
    unfold eraseSucc at hd
    split at hd
    · rename_i hm
      obtain ⟨k, -, hk⟩ := List.mem_filterMap.mp hd
      split at hk
      · rename_i hck
        cases hk
        exact ⟨toRec k, ⟨k, hck, rfl⟩, hm, ⟨k, hck, rfl⟩, erase_eq c k⟩
      · cases hk
    · cases hd

private theorem emL_iff (m : Mut) (c : CState) (S : State) :
    (∃ t, EmAdmit (cfg m) t (toState c) S ∨ EmRefuse (cfg m) t (toState c) S) ↔
      ∃ d, d ∈ emLSucc m c ∧ S = toState d := by
  constructor
  · rintro ⟨t, ⟨hl, hc, hb, rfl⟩ | ⟨hl, hn, rfl⟩⟩
    · have hl' : c.em.live = true := hl
      refine ⟨emLC m c t, by simp only [emLSucc, hl', if_true, List.mem_map]; exact ⟨t, mem_tools t, rfl⟩, ?_⟩
      have he : emLC m c t = admitC c .emergency t (c.em.envelope t) := by
        simp [emLC, (emAdmitB_iff m c t).mpr ⟨hl, hc, hb⟩]
      rw [he, admit_eq]; rfl
    · have hl' : c.em.live = true := hl
      refine ⟨emLC m c t, by simp only [emLSucc, hl', if_true, List.mem_map]; exact ⟨t, mem_tools t, rfl⟩, ?_⟩
      have hf : emAdmitB m c t = false := by
        cases h : emAdmitB m c t
        · rfl
        · exact absurd ((emAdmitB_iff m c t).mp h).2 hn
      have he : emLC m c t = refuseC c := by simp [emLC, hf]
      rw [he]; rfl
  · rintro ⟨d, hd, rfl⟩
    unfold emLSucc at hd
    split at hd
    · rename_i hl
      obtain ⟨t, -, rfl⟩ := List.mem_map.mp hd
      refine ⟨t, ?_⟩
      cases hb : emAdmitB m c t
      · have he : emLC m c t = refuseC c := by simp [emLC, hb]
        rw [he]
        refine Or.inr ⟨hl, fun h => ?_, rfl⟩
        rw [(emAdmitB_iff m c t).mpr ⟨hl, h⟩] at hb; cases hb
      · have he : emLC m c t = admitC c .emergency t (c.em.envelope t) := by simp [emLC, hb]
        rw [he, admit_eq]
        obtain ⟨-, hc, hb'⟩ := (emAdmitB_iff m c t).mp hb
        exact Or.inl ⟨hl, hc, hb', rfl⟩
    · cases hd

/-! ### `Next` and `NextL` -/

theorem next_iff (m : Mut) (c : CState) (S : State) :
    Next (cfg m) (toState c) S ↔ ∃ d, d ∈ succC m c ∧ S = toState d := by
  simp only [succC, ex_append]
  unfold Next
  rw [promote_iff, approve_iff, activate_iff, end_iff, regrant_iff, renew_iff, toggle_iff, exists_or, emCall_iff,
    thinker_iff, erase_iff]

theorem nextL_iff (m : Mut) (c : CState) (S : State) :
    NextL (cfg m) (toState c) S ↔ ∃ d, d ∈ succLC m c ∧ S = toState d := by
  simp only [succLC, ex_append]
  unfold NextL
  rw [promote_iff, approve_iff, activate_iff, end_iff, regrant_iff, renew_iff, toggle_iff, erase_iff, ← emL_iff,
    ← thinker_iff]
  constructor
  · rintro (h | h | h | h | h | h | h | ⟨t, h | h | h⟩ | h)
    · exact Or.inl h
    · exact Or.inr (Or.inl h)
    · exact Or.inr (Or.inr (Or.inl h))
    · exact Or.inr (Or.inr (Or.inr (Or.inl h)))
    · exact Or.inr (Or.inr (Or.inr (Or.inr (Or.inl h))))
    · exact Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inl h)))))
    · exact Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inl h))))))
    · exact Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inl (Or.inl ⟨t, Or.inl h⟩))))))))
    · exact Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inl (Or.inl ⟨t, Or.inr h⟩))))))))
    · exact Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inl (Or.inr ⟨t, h⟩))))))))
    · exact Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr h)))))))
  · rintro (h | h | h | h | h | h | h | (⟨t, h | h⟩ | ⟨t, h⟩) | h)
    · exact Or.inl h
    · exact Or.inr (Or.inl h)
    · exact Or.inr (Or.inr (Or.inl h))
    · exact Or.inr (Or.inr (Or.inr (Or.inl h)))
    · exact Or.inr (Or.inr (Or.inr (Or.inr (Or.inl h))))
    · exact Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inl h)))))
    · exact Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inl h))))))
    · exact Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inl ⟨t, Or.inl h⟩)))))))
    · exact Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inl ⟨t, Or.inr (Or.inl h)⟩)))))))
    · exact Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inl ⟨t, Or.inr (Or.inr h)⟩)))))))
    · exact Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr h)))))))

/-! ## `Init` -/

def cNoEm : CEm := ⟨false, 0, .none, fun _ => false, false, .none, false⟩

def cInit : CState :=
  ⟨single .t1, fun _ => false, cNoEm, single .t1, true, fun _ => false, false, fun _ => false⟩

theorem toEm_noEm : toEm cNoEm = NoEm := by
  show (⟨false, 0, .none, toSet (fun _ => false), false = true, .none, false⟩ : EmRec) =
    ⟨false, 0, .none, ∅, False, .none, false⟩
  rw [toSet_false, Bool.false_eq_true]

theorem init_iff (S : State) : Init S ↔ S = toState cInit := by
  have h : toState cInit = ⟨{.t1}, ∅, NoEm, {.t1}, true, ∅, false, ∅⟩ :=
    State.eq_of (toSet_single _) toSet_false toEm_noEm (toSet_single _) rfl (image_false _) rfl (image_false _)
  rw [h]
  constructor
  · rintro ⟨h1, h2, h3, h4, h5, h6, h7, h8⟩
    exact State.eq_of h1 h2 h3 h4 h5 h6 h7 h8
  · rintro rfl
    exact ⟨rfl, rfl, rfl, rfl, rfl, rfl, rfl, rfl⟩

/-! ## The properties -/

/-- `EmergencyLeaseHasARosterQuorum == em.live => em.quorate` -/
def elhqB (c : CState) : Bool := !c.em.live || c.em.quorate
/-- `EmergencyLeaseIsOneRound == em.round > 0 => (em.by = "roster" /\ ~em.renewed)` -/
def eloB (c : CState) : Bool := !decide (c.em.round > 0) || (c.em.grantor == .roster && !c.em.renewed)
/-- `NoAgentHoldsAnEmergencySeat == em.live => em.holder \in Persons` -/
def nahB (c : CState) : Bool := !c.em.live || c.em.holder == .h
/-- `CallsAreAllowlisted == \A c \in calls : c.allowlisted` -/
def caaB (c : CState) : Bool := callKeys.all fun k => !c.calls k || k.allowlisted
/-- `ThinkerStillCoupled == \A c \in calls : c.seat = "thinker" => c.observed` -/
def tscB (c : CState) : Bool := callKeys.all fun k => !c.calls k || k.seat != .thinker || k.observed
/-- `ActivationIsForensic == \A n \in 1..em.round : \E x \in records : x.round = n`. The mirror's records are of
rounds 1 and 2, so the property needs `em.round <= 2`. -/
def aifB (c : CState) : Bool :=
  (decide (c.em.round < 1) || recKeys.any fun k => c.records k && !k.second) &&
    (decide (c.em.round < 2) || recKeys.any fun k => c.records k && k.second) && decide (c.em.round ≤ 2)
/-- `EmergencyNeverCoupled == \A t \in Tools : (em.live /\ t \in em.envelope) => ENABLED EmAdmit(t)` -/
def encB (m : Mut) (c : CState) : Bool := tools.all fun t => !(c.em.live && c.em.envelope t) || emAdmitB m c t
/-- `EmergencyCallsWithoutObserver == (em.live /\ ~obsLive) => \E t \in Tools : ENABLED EmAdmit(t)` -/
def ecwoB (m : Mut) (c : CState) : Bool := !(c.em.live && !c.obsLive) || tools.any (emAdmitB m c)

theorem elhq_iff (c : CState) : elhqB c = true ↔ EmergencyLeaseHasARosterQuorum (toState c) := by
  show (!c.em.live || c.em.quorate) = true ↔ (c.em.live = true → c.em.quorate = true)
  cases c.em.live <;> cases c.em.quorate <;> simp

theorem elo_iff (c : CState) : eloB c = true ↔ EmergencyLeaseIsOneRound (toState c) := by
  show (!decide (c.em.round > 0) || (c.em.grantor == .roster && !c.em.renewed)) = true ↔
    (c.em.round > 0 → c.em.grantor = .roster ∧ c.em.renewed = false)
  by_cases h : c.em.round > 0 <;> cases c.em.grantor <;> cases c.em.renewed <;> simp [h]

theorem nah_iff (c : CState) : nahB c = true ↔ NoAgentHoldsAnEmergencySeat (toState c) := by
  show (!c.em.live || c.em.holder == .h) = true ↔ (c.em.live = true → c.em.holder ∈ Persons)
  cases c.em.live <;> cases c.em.holder <;> simp [Persons]

theorem caa_iff (c : CState) : caaB c = true ↔ CallsAreAllowlisted (toState c) := by
  simp only [caaB, List.all_eq_true, Bool.or_eq_true, Bool.not_eq_true']
  constructor
  · rintro h x ⟨k, hk, rfl⟩
    rcases h k (mem_callKeys k) with h | h
    · rw [hk] at h; cases h
    · exact h
  · intro h k _
    cases hk : c.calls k
    · exact Or.inl rfl
    · exact Or.inr (h (toCall k) ⟨k, hk, rfl⟩)

theorem tsc_iff (c : CState) : tscB c = true ↔ ThinkerStillCoupled (toState c) := by
  simp only [tscB, List.all_eq_true, Bool.or_eq_true, Bool.not_eq_true', bne_iff_ne, ne_eq]
  constructor
  · rintro h x ⟨k, hk, rfl⟩ hs
    rcases h k (mem_callKeys k) with (h | h) | h
    · rw [hk] at h; cases h
    · exact absurd hs h
    · exact h
  · intro h k _
    cases hk : c.calls k
    · exact Or.inl (Or.inl rfl)
    · cases hs : k.seat
      · exact Or.inl (Or.inr (by decide))
      · exact Or.inr (h (toCall k) ⟨k, hk, rfl⟩ hs)

theorem aif_iff (c : CState) : aifB c = true ↔ ActivationIsForensic (toState c) := by
  have h1 : (recKeys.any fun k => c.records k && !k.second) = true ↔ ∃ x, x ∈ (toState c).records ∧ x.round = 1 := by
    simp only [List.any_eq_true, Bool.and_eq_true, Bool.not_eq_true']
    constructor
    · rintro ⟨k, -, hk, hs⟩
      exact ⟨toRec k, ⟨k, hk, rfl⟩, by simp [toRec, hs]⟩
    · rintro ⟨x, ⟨k, hk, rfl⟩, hr⟩
      refine ⟨k, mem_recKeys k, hk, ?_⟩
      cases hs : k.second
      · rfl
      · simp [toRec, hs] at hr
  have h2 : (recKeys.any fun k => c.records k && k.second) = true ↔ ∃ x, x ∈ (toState c).records ∧ x.round = 2 := by
    simp only [List.any_eq_true, Bool.and_eq_true]
    constructor
    · rintro ⟨k, -, hk, hs⟩
      exact ⟨toRec k, ⟨k, hk, rfl⟩, by simp [toRec, hs]⟩
    · rintro ⟨x, ⟨k, hk, rfl⟩, hr⟩
      refine ⟨k, mem_recKeys k, hk, ?_⟩
      cases hs : k.second
      · simp [toRec, hs] at hr
      · rfl
  have h3 : ¬ ∃ x, x ∈ (toState c).records ∧ x.round = 3 := by
    rintro ⟨x, ⟨k, -, rfl⟩, hr⟩
    cases hs : k.second <;> simp [toRec, hs] at hr
  unfold aifB ActivationIsForensic
  simp only [Bool.and_eq_true, Bool.or_eq_true, decide_eq_true_eq, h1, h2]
  constructor
  · rintro ⟨⟨ha, hb⟩, hc⟩ n ⟨hn1, hn2⟩
    have hr : (toState c).em.round = c.em.round := rfl
    rw [hr] at hn2
    have : n = 1 ∨ n = 2 := by omega
    rcases this with rfl | rfl
    · rcases ha with ha | ha
      · exfalso; omega
      · exact ha
    · rcases hb with hb | hb
      · exfalso; omega
      · exact hb
  · intro h
    have hr : (toState c).em.round = c.em.round := rfl
    refine ⟨⟨?_, ?_⟩, ?_⟩
    · by_cases h0 : c.em.round < 1
      · exact Or.inl h0
      · exact Or.inr (h 1 ⟨Nat.le_refl 1, by rw [hr]; omega⟩)
    · by_cases h0 : c.em.round < 2
      · exact Or.inl h0
      · exact Or.inr (h 2 ⟨by decide, by rw [hr]; omega⟩)
    · by_cases h0 : c.em.round ≤ 2
      · exact h0
      · exact absurd (h 3 ⟨by decide, by rw [hr]; omega⟩) h3

/-- `ENABLED EmAdmit(t)`, at a mirrored state, is `EmAdmit(t)`'s guard: when the guard holds, the step that records
the call and changes nothing else is an `EmAdmit(t)` step. -/
theorem enabled_iff (m : Mut) (c : CState) (t : Tool) :
    emAdmitB m c t = true ↔ Enabled (EmAdmit (cfg m) t) (toState c) := by
  rw [emAdmitB_iff]
  constructor
  · rintro ⟨hl, hc, hb⟩
    exact ⟨_, hl, hc, hb, rfl⟩
  · rintro ⟨_, hl, hc, hb, -⟩
    exact ⟨hl, hc, hb⟩

theorem enc_iff (m : Mut) (c : CState) : encB m c = true ↔ EmergencyNeverCoupled (cfg m) (toState c) := by
  unfold encB EmergencyNeverCoupled
  simp only [List.all_eq_true]
  constructor
  · intro h t ⟨hl, ht⟩
    have h' := h t (mem_tools t)
    have hl' : c.em.live = true := hl
    have ht' : c.em.envelope t = true := ht
    rw [hl', ht'] at h'
    exact (enabled_iff m c t).mp h'
  · intro h t _
    cases hl : c.em.live
    · rfl
    · cases ht : c.em.envelope t
      · rfl
      · exact (enabled_iff m c t).mpr (h t ⟨hl, ht⟩)

theorem ecwo_iff (m : Mut) (c : CState) : ecwoB m c = true ↔ EmergencyCallsWithoutObserver (cfg m) (toState c) := by
  have hany : tools.any (emAdmitB m c) = true ↔ ∃ t, Enabled (EmAdmit (cfg m) t) (toState c) := by
    simp only [List.any_eq_true, enabled_iff]
    exact ⟨fun ⟨t, _, h⟩ => ⟨t, h⟩, fun ⟨t, h⟩ => ⟨t, mem_tools t, h⟩⟩
  show (!(c.em.live && !c.obsLive) || tools.any (emAdmitB m c)) = true ↔
    (c.em.live = true ∧ c.obsLive = false → ∃ t, Enabled (EmAdmit (cfg m) t) (toState c))
  rw [← hany]
  cases c.em.live <;> cases c.obsLive <;> simp

end Topak.Spec.Emergency.Mirror

#print axioms Topak.Spec.Emergency.Mirror.next_iff
#print axioms Topak.Spec.Emergency.Mirror.nextL_iff
#print axioms Topak.Spec.Emergency.Mirror.init_iff
#print axioms Topak.Spec.Emergency.Mirror.eqC_iff
#print axioms Topak.Spec.Emergency.Mirror.elhq_iff
#print axioms Topak.Spec.Emergency.Mirror.elo_iff
#print axioms Topak.Spec.Emergency.Mirror.nah_iff
#print axioms Topak.Spec.Emergency.Mirror.caa_iff
#print axioms Topak.Spec.Emergency.Mirror.tsc_iff
#print axioms Topak.Spec.Emergency.Mirror.aif_iff
#print axioms Topak.Spec.Emergency.Mirror.enabled_iff
#print axioms Topak.Spec.Emergency.Mirror.enc_iff
#print axioms Topak.Spec.Emergency.Mirror.ecwo_iff
