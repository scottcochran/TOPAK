import TopakSpec.Temporal
/-!
# Emergency.tla and Emergency_live.tla in Lean

ADR-0052 (accepted, provisional, B34), break-glass as an emergency seating, and ADR-0039 A2: an emergency seat is not coupled to the
Observer. `spec/Emergency.tla` re-encoded, and in the same file `spec/Emergency_live.tla`, which extends it.

What is proved, and of what:
- `spec/Emergency_proof.tla`'s theorems, by induction on reachable states with its inductive invariants
  `LiveHasRound` and `HolderIsPerson` and with the same hypotheses on `Mut`: the six invariants, `LiveHasRoundAlways`
  and `SafeAlways`. `TypeOK` has no counterpart. Nothing is assumed of `MaxRound`.
- In place of the `ENABLED` lemma `Emergency_proof.tla` dropped (its lines 401 to 404: only Zenon proved it, and
  Isabelle could not check Zenon's script; the statement itself was never committed, so this is the fact its comment
  names, not its text): `UnobservedEmergencyCallEnabledAlways`, stated of the frozen module's own `Next`. In every
  state its `Spec` reaches with the seat live and no live Observer, some `EmCall` step admits a call of a tool in the
  envelope, recorded as not observed. It holds under every `Mut` and every `MaxRound`: `EmCall`'s guard does not read
  the Observer.
- Emergency_live.tla. `nextL_next`: every `NextL` step is a `Next` step, under every `Mut` and from every state, so
  every state `SpecL` reaches is one `Spec` reaches (`reachL_reach`) and the invariants above hold of `SpecL`
  (`SafeLAlways`, under `none` and the two coupling mutations). `nextL_iff_next`, over every pair of states, and
  `reachL_iff`, over the reachable ones: under every other `Mut`, `NextL` is `Next`. `EmergencyNeverCoupledValid`:
  under every other `Mut`, `EmergencyNeverCoupled` holds in every state, reachable or not, as `ConsultNeverCoupled`
  does in `RunCoupling_proof.tla`. `EmergencyNeverCoupledAlways` and `EmergencyCallsWithoutObserverAlways`: both hold
  in every state `Spec` reaches, and so in every state `SpecL` reaches, under `NoCoupledRound`, that no round in which
  the seat can be live is coupled. This is weaker than "not a coupling mutation", and it is the weakest hypothesis there is:
  `EmergencyNeverCoupledIff` and `EmergencyCallsWithoutObserverIff` prove that each property holds of every state
  `Spec` reaches, and of every state `SpecL` reaches, exactly when `NoCoupledRound` holds.

Encoding notes beyond the prelude's:
- `Mut` has Emergency.tla's eight values and Emergency_live.tla's two. Emergency.tla compares `Mut` only with its own
  strings, so under `M_EMCOUPLE` and `M_EMCOUPLE2` its definitions are as under `none`, as in TLA+.
- `live` and `renewed`, which the module only ever sets to TRUE or FALSE, are `Bool`. So is `refused`, set to FALSE
  and then only to TRUE (Coupling.lean and Confinement.lean keep their `refused` as `Prop`; nothing here depends on
  the choice), and so is `obsLive`, set to TRUE and then only negated, as Confinement.lean's `verifierUp` is, with the
  call record's `observed`, which copies it. `quorate`, set to `Quorate(approvals)`, and `allowlisted`, set to a
  membership, are `Prop`.
- `holder` ranges over `Holders \cup {"none"}`, the type `Holder`. The record field `by` is `grantor`, since `by` is a
  Lean keyword. `Activate(h)`'s parameter, and the `h` of `\E h \in Holders`, is `who`, since `h` is the person's
  name, the constructor `Holder.h`.
- `Roster` and `Tools` are whole types, so `\E r \in Roster` and `\E t \in Tools` range over the type.
  `\E t \in Domain`, `\E h \in Holders` and `\E x \in records` keep their bounds.
- A successor is written `st' = { st with ... }`, except in `EmCall` and `ThinkerCall`. There, as in the TLA+ text,
  the `IF` on a membership is a conjunct of its own, the pair of implications the prelude describes, and the
  `UNCHANGED` list beside it is `CallFrame`. `IF Mut = "M_AGENT"` is `if`.
- `ENABLED A` is `Enabled A` (`Temporal.lean`): a successor in the encoding's `State` type. TLA+ asks for any values
  of the primed variables; `EmAdmit` fixes each of them to a value of its type, so the two agree.

Readings chosen: none. Every definition is the TLA+ text under the conventions above.

Invariants that are not `Emergency_proof.tla`'s:
- `Decided`, the encoding's own: membership in the tool sets and in the approvals is decided. TLA+ decides every membership by excluded
  middle, and a predicate does not. Every set the module builds is a finite union of literals, so `Decided` holds of
  every reachable state under every `Mut`. With it the step of `CallsAreAllowlisted` cases on the `IF` of `EmCall` and
  of `ThinkerCall` without `Classical.choice`. NonComposition.lean, whose `Erase` cases on a membership in the same
  way, uses `Classical.choice` there instead.
- `EnvelopeHasTe` (every lease the seat has had holds te), which is `Emergency_live_proof.tla`'s, and
  `RoundBounded` (`em.round <= MaxRound`), which is the encoding's own, both for the `ENABLED` theorems.

`#print axioms`: `propext` and `Quot.sound` at most, except `nextL_iff_next`, which also uses `Classical.choice`. Over every
pair of states, splitting `EmCall`'s `IF` into `EmAdmit` or `EmRefuse` decides a membership in an arbitrary
envelope, and `nextL_iff_next_needs_em` proves that the statement implies excluded middle, so no proof of it can do
without. Nothing rests on it: `reachL_iff` states the same over the reachable states, from `Decided`, without it.

Mutations: Emergency.tla's seven and Emergency_live.tla's two. Each theorem takes only the mutations that break it;
the two `ENABLED` theorems take `NoCoupledRound`, which excludes the two coupling mutations only where their coupled
round can be reached.
-/

namespace Topak.Spec.Emergency
open Topak.Spec PSet

/-- `Mut`: Emergency.tla's eight values, then Emergency_live.tla's `M_EMCOUPLE` and `M_EMCOUPLE2`. -/
inductive Mut
  | none | M_NOQUORUM | M_REGRANT | M_RENEW | M_AGENT | M_X1 | M_UNCOUPLE | M_ERASE
  | M_EMCOUPLE | M_EMCOUPLE2
  deriving DecidableEq

/-- `CONSTANTS Mut, MaxRound` -/
structure Cfg where
  m : Mut
  MaxRound : Nat

/-- `Roster == {"r1", "r2", "r3"}`: the members, as a type. -/
inductive Member | r1 | r2 | r3
  deriving DecidableEq
/-- `Roster`, as a set: every member. -/
def Roster : PSet Member := univ

/-- `Holders \cup {"none"}`: the values of a lease's `holder`. -/
inductive Holder | h | g | none
  deriving DecidableEq
/-- `Persons == {"h"}` -/
def Persons : PSet Holder := {.h}
/-- `Agents == {"g"}` -/
def Agents : PSet Holder := {.g}
/-- `Holders == Persons \cup Agents` -/
def Holders : PSet Holder := Persons ∪ Agents

/-- `Tools == Domain \cup {"te", "tx"}`: te is emergency-only, tx is in no bundle. -/
inductive Tool | t1 | t2 | te | tx
  deriving DecidableEq
/-- `Domain == {"t1", "t2"}`: the tools a promotion can put in force. -/
def Domain : PSet Tool := {.t1, .t2}

/-- The values of a lease's `by`: `{"none", "roster", "operator"}`. -/
inductive Grantor | none | roster | operator
  deriving DecidableEq

/-- A quorum of the roster: two distinct members. `Quorate(S) == \E a \in S, b \in S : a # b` -/
def Quorate (S : PSet Member) : Prop := ∃ a b, a ∈ S ∧ b ∈ S ∧ a ≠ b

/-- The emergency seat's lease, with what was true when it was granted (`EmType` in the TLAPS proof):
`[live : BOOLEAN, round : Nat, holder : Holders \cup {"none"}, envelope : SUBSET Tools, quorate : BOOLEAN,
by : {"none", "roster", "operator"}, renewed : BOOLEAN]` -/
structure EmRec where
  live : Bool
  round : Nat
  holder : Holder
  envelope : PSet Tool
  quorate : Prop
  grantor : Grantor
  renewed : Bool

/-- `NoEm == [live |-> FALSE, round |-> 0, holder |-> "none", envelope |-> {}, quorate |-> FALSE, by |-> "none",
renewed |-> FALSE]` -/
def NoEm : EmRec :=
  { live := false, round := 0, holder := .none, envelope := ∅, quorate := False, grantor := .none, renewed := false }

/-- The seat a call is made from: "emergency" or "thinker". -/
inductive Seat | emergency | thinker
  deriving DecidableEq

/-- An admitted call: `[seat |-> s, tool |-> t, allowlisted |-> ..., observed |-> obsLive]` -/
structure CallRec where
  seat : Seat
  tool : Tool
  allowlisted : Prop
  observed : Bool

/-- An activation record: `[round |-> n, holder |-> h, approvers |-> approvals]` -/
structure ActRec where
  round : Nat
  holder : Holder
  approvers : PSet Member

/-- `VARIABLES domainTools, approvals, em, thinkerAllow, obsLive, calls, refused, records` -/
structure State where
  domainTools : PSet Tool
  approvals : PSet Member
  em : EmRec
  thinkerAllow : PSet Tool
  obsLive : Bool
  calls : PSet CallRec
  refused : Bool
  records : PSet ActRec

/-- ```
Init == /\ domainTools = {"t1"} /\ approvals = {} /\ em = NoEm /\ thinkerAllow = {"t1"}
        /\ obsLive = TRUE /\ calls = {} /\ refused = FALSE /\ records = {}
``` -/
def Init (st : State) : Prop :=
  st.domainTools = {.t1} ∧ st.approvals = ∅ ∧ st.em = NoEm ∧ st.thinkerAllow = {.t1} ∧
  st.obsLive = true ∧ st.calls = ∅ ∧ st.refused = false ∧ st.records = ∅

/-- A promotion puts a tool in force. It does not reach a live round's envelope.
`Promote(t) == t \in Domain \ domainTools /\ domainTools' = domainTools \cup {t} /\ UNCHANGED <<...>>` -/
def Promote (t : Tool) (st st' : State) : Prop :=
  t ∈ Domain \ st.domainTools ∧ st' = { st with domainTools := st.domainTools ∪ {t} }

/-- `Approve(r) == r \in Roster \ approvals /\ approvals' = approvals \cup {r} /\ UNCHANGED <<...>>` -/
def Approve (r : Member) (st st' : State) : Prop :=
  r ∈ Roster \ st.approvals ∧ st' = { st with approvals := st.approvals ∪ {r} }

/-- The roster's quorum seats a named holder for one round, on the domain's envelope as it stands, and the
activation is recorded.
```
Activate(h) ==
  /\ ~em.live /\ em.round < MaxRound
  /\ (Quorate(approvals) \/ Mut = "M_NOQUORUM")
  /\ h \in (IF Mut = "M_AGENT" THEN Holders ELSE Persons)
  /\ em' = [live |-> TRUE, round |-> em.round + 1, holder |-> h,
            envelope |-> domainTools \cup {"te"},
            quorate |-> Quorate(approvals), by |-> "roster", renewed |-> FALSE]
  /\ records' = records \cup {[round |-> em.round + 1, holder |-> h, approvers |-> approvals]}
  /\ approvals' = {}
  /\ UNCHANGED <<domainTools, thinkerAllow, obsLive, calls, refused>>
``` -/
def Activate (c : Cfg) (who : Holder) (st st' : State) : Prop :=
  st.em.live = false ∧ st.em.round < c.MaxRound ∧
  (Quorate st.approvals ∨ c.m = .M_NOQUORUM) ∧
  who ∈ (if c.m = .M_AGENT then Holders else Persons) ∧
  st' = { st with
    em := { live := true, round := st.em.round + 1, holder := who, envelope := st.domainTools ∪ {.te},
            quorate := Quorate st.approvals, grantor := .roster, renewed := false },
    records := st.records ∪ {⟨st.em.round + 1, who, st.approvals⟩},
    approvals := ∅ }

/-- The lease ends: the round bound, its ttl, a revocation or a fence.
`EndEm == em.live /\ em' = [em EXCEPT !.live = FALSE] /\ UNCHANGED <<...>>` -/
def EndEm (st st' : State) : Prop :=
  st.em.live = true ∧ st' = { st with em := { st.em with live := false } }

/-- Mutation only: an operator continues the emergency seat.
```
Regrant == /\ Mut = "M_REGRANT"
           /\ ~em.live /\ em.round > 0 /\ em.round < MaxRound
           /\ em' = [em EXCEPT !.live = TRUE, !.round = @ + 1, !.quorate = FALSE, !.by = "operator"]
           /\ UNCHANGED <<...>>
``` -/
def Regrant (c : Cfg) (st st' : State) : Prop :=
  c.m = .M_REGRANT ∧ st.em.live = false ∧ st.em.round > 0 ∧ st.em.round < c.MaxRound ∧
  st' = { st with em := { st.em with live := true, round := st.em.round + 1, quorate := False, grantor := .operator } }

/-- Mutation only. `Renew == Mut = "M_RENEW" /\ em.live /\ em' = [em EXCEPT !.renewed = TRUE] /\ UNCHANGED <<...>>` -/
def Renew (c : Cfg) (st st' : State) : Prop :=
  c.m = .M_RENEW ∧ st.em.live = true ∧ st' = { st with em := { st.em with renewed := true } }

/-- X1, where it is left in the floor: a quorum's approvals admit any tool for any seat.
`X1 == Mut = "M_X1" /\ Quorate(approvals)` -/
def X1 (c : Cfg) (st : State) : Prop := c.m = .M_X1 ∧ Quorate st.approvals

/-- `UNCHANGED <<domainTools, approvals, em, thinkerAllow, obsLive, records>>`: the frame `EmCall` and
`ThinkerCall` share, beside their `IF`. -/
def CallFrame (st st' : State) : Prop :=
  st'.domainTools = st.domainTools ∧ st'.approvals = st.approvals ∧ st'.em = st.em ∧
  st'.thinkerAllow = st.thinkerAllow ∧ st'.obsLive = st.obsLive ∧ st'.records = st.records

/-- A call by the emergency seat. No Observer is asked for: R3 is over Thinkers.
```
EmCall(t) ==
  /\ em.live
  /\ IF t \in em.envelope \/ X1
       THEN /\ calls' = {[seat |-> "emergency", tool |-> t, allowlisted |-> t \in em.envelope,
                          observed |-> obsLive]}
            /\ UNCHANGED refused
       ELSE /\ refused' = TRUE
            /\ UNCHANGED calls
  /\ UNCHANGED <<domainTools, approvals, em, thinkerAllow, obsLive, records>>
``` -/
def EmCall (c : Cfg) (t : Tool) (st st' : State) : Prop :=
  st.em.live = true ∧
  ((t ∈ st.em.envelope ∨ X1 c st) →
    st'.calls = {⟨.emergency, t, t ∈ st.em.envelope, st.obsLive⟩} ∧ st'.refused = st.refused) ∧
  (¬ (t ∈ st.em.envelope ∨ X1 c st) → st'.refused = true ∧ st'.calls = st.calls) ∧
  CallFrame st st'

/-- A call by the Thinker: its allowlist, and a live Observer (R3).
```
ThinkerCall(t) ==
  /\ IF (t \in thinkerAllow \/ X1) /\ (obsLive \/ Mut = "M_UNCOUPLE")
       THEN /\ calls' = {[seat |-> "thinker", tool |-> t, allowlisted |-> t \in thinkerAllow,
                          observed |-> obsLive]}
            /\ UNCHANGED refused
       ELSE /\ refused' = TRUE
            /\ UNCHANGED calls
  /\ UNCHANGED <<domainTools, approvals, em, thinkerAllow, obsLive, records>>
``` -/
def ThinkerCall (c : Cfg) (t : Tool) (st st' : State) : Prop :=
  (((t ∈ st.thinkerAllow ∨ X1 c st) ∧ (st.obsLive = true ∨ c.m = .M_UNCOUPLE)) →
    st'.calls = {⟨.thinker, t, t ∈ st.thinkerAllow, st.obsLive⟩} ∧ st'.refused = st.refused) ∧
  (¬ ((t ∈ st.thinkerAllow ∨ X1 c st) ∧ (st.obsLive = true ∨ c.m = .M_UNCOUPLE)) →
    st'.refused = true ∧ st'.calls = st.calls) ∧
  CallFrame st st'

/-- The environment: the Observer fails or returns. `ObsToggle == obsLive' = ~obsLive /\ UNCHANGED <<...>>` -/
def ObsToggle (st st' : State) : Prop := st' = { st with obsLive := !st.obsLive }

/-- Mutation only: erasure removes an activation record.
`Erase(x) == Mut = "M_ERASE" /\ x \in records /\ records' = records \ {x} /\ UNCHANGED <<...>>` -/
def Erase (c : Cfg) (x : ActRec) (st st' : State) : Prop :=
  c.m = .M_ERASE ∧ x ∈ st.records ∧ st' = { st with records := st.records \ {x} }

/-- ```
Next ==
  \/ \E t \in Domain : Promote(t)
  \/ \E r \in Roster : Approve(r)
  \/ \E h \in Holders : Activate(h)
  \/ EndEm \/ Regrant \/ Renew \/ ObsToggle
  \/ \E t \in Tools : EmCall(t) \/ ThinkerCall(t)
  \/ \E x \in records : Erase(x)
``` -/
def Next (c : Cfg) (st st' : State) : Prop :=
  (∃ t, t ∈ Domain ∧ Promote t st st') ∨ (∃ r, Approve r st st') ∨ (∃ who, who ∈ Holders ∧ Activate c who st st') ∨
  EndEm st st' ∨ Regrant c st st' ∨ Renew c st st' ∨ ObsToggle st st' ∨
  (∃ t, EmCall c t st st' ∨ ThinkerCall c t st st') ∨ (∃ x, x ∈ st.records ∧ Erase c x st st')

/-! ## The six properties -/

/-- `EmergencyLeaseHasARosterQuorum == em.live => em.quorate` -/
def EmergencyLeaseHasARosterQuorum (st : State) : Prop := st.em.live = true → st.em.quorate

/-- `EmergencyLeaseIsOneRound == em.round > 0 => (em.by = "roster" /\ ~em.renewed)` -/
def EmergencyLeaseIsOneRound (st : State) : Prop :=
  st.em.round > 0 → st.em.grantor = .roster ∧ st.em.renewed = false

/-- `NoAgentHoldsAnEmergencySeat == em.live => em.holder \in Persons` -/
def NoAgentHoldsAnEmergencySeat (st : State) : Prop := st.em.live = true → st.em.holder ∈ Persons

/-- `CallsAreAllowlisted == \A c \in calls : c.allowlisted` -/
def CallsAreAllowlisted (st : State) : Prop := ∀ x, x ∈ st.calls → x.allowlisted

/-- `ThinkerStillCoupled == \A c \in calls : c.seat = "thinker" => c.observed` -/
def ThinkerStillCoupled (st : State) : Prop := ∀ x, x ∈ st.calls → x.seat = .thinker → x.observed = true

/-- `ActivationIsForensic == \A n \in 1..em.round : \E x \in records : x.round = n` -/
def ActivationIsForensic (st : State) : Prop :=
  ∀ n, 1 ≤ n ∧ n ≤ st.em.round → ∃ x, x ∈ st.records ∧ x.round = n

/-- `Safe == /\ EmergencyLeaseHasARosterQuorum /\ EmergencyLeaseIsOneRound /\ NoAgentHoldsAnEmergencySeat
/\ CallsAreAllowlisted /\ ThinkerStillCoupled /\ ActivationIsForensic` -/
def Safe (st : State) : Prop :=
  EmergencyLeaseHasARosterQuorum st ∧ EmergencyLeaseIsOneRound st ∧ NoAgentHoldsAnEmergencySeat st ∧
  CallsAreAllowlisted st ∧ ThinkerStillCoupled st ∧ ActivationIsForensic st

/-! ## The TLAPS proof's inductive invariants -/

/-- A live lease has had a round. `LiveHasRound == em.live => em.round > 0` -/
def LiveHasRound (st : State) : Prop := st.em.live = true → st.em.round > 0

/-- Every holder the seat has had is a person: the property over every lease and not only a live one.
`HolderIsPerson == em.round > 0 => em.holder \in Persons` -/
def HolderIsPerson (st : State) : Prop := st.em.round > 0 → st.em.holder ∈ Persons

theorem InitLiveHasRound (st : State) (h : Init st) : LiveHasRound st := by
  intro hl; rw [h.2.2.1] at hl; cases hl

/-- `LiveHasRoundNext`, under every `Mut`. -/
theorem NextLiveHasRound (c : Cfg) (st st' : State) (hi : LiveHasRound st) (hn : Next c st st') :
    LiveHasRound st' := by
  rcases hn with ⟨t, -, -, rfl⟩ | ⟨r, -, rfl⟩ | ⟨who, -, -, -, -, -, rfl⟩ | ⟨-, rfl⟩ | ⟨-, -, -, -, rfl⟩ |
    ⟨-, -, rfl⟩ | rfl | ⟨t, ⟨-, -, -, -, -, hem, -⟩ | ⟨-, -, -, -, hem, -⟩⟩ | ⟨x, -, -, -, rfl⟩
  · exact hi
  · exact hi
  · intro _; exact Nat.succ_pos _
  · intro h; cases h
  · intro _; exact Nat.succ_pos _
  · exact hi
  · exact hi
  · intro h; rw [hem] at h ⊢; exact hi h
  · intro h; rw [hem] at h ⊢; exact hi h
  · exact hi

/-- `THEOREM LiveHasRoundAlways == Spec => []LiveHasRound`, under every `Mut`. -/
theorem LiveHasRoundAlways (c : Cfg) : ∀ st, Reachable Init (Next c) st → LiveHasRound st :=
  invariant LiveHasRound LiveHasRound InitLiveHasRound (NextLiveHasRound c) (fun _ h => h)

theorem InitHolder (st : State) (h : Init st) : HolderIsPerson st := by
  intro hr; rw [h.2.2.1] at hr; exact absurd hr (Nat.lt_irrefl 0)

/-- `HolderIsPersonNext == ASSUME Mut # "M_AGENT", ... PROVE HolderIsPerson'` -/
theorem NextHolder (c : Cfg) (hm : c.m ≠ .M_AGENT) (st st' : State) (hi : HolderIsPerson st)
    (hn : Next c st st') : HolderIsPerson st' := by
  rcases hn with ⟨t, -, -, rfl⟩ | ⟨r, -, rfl⟩ | ⟨who, -, -, -, -, hh, rfl⟩ | ⟨-, rfl⟩ | ⟨-, -, hpos, -, rfl⟩ |
    ⟨-, -, rfl⟩ | rfl | ⟨t, ⟨-, -, -, -, -, hem, -⟩ | ⟨-, -, -, -, hem, -⟩⟩ | ⟨x, -, -, -, rfl⟩
  · exact hi
  · exact hi
  · -- Activate(h): only a person can be seated
    intro _; rw [if_neg hm] at hh; exact hh
  · exact hi
  · -- Regrant: the holder is the last round's, who was a person
    intro _; exact hi hpos
  · exact hi
  · exact hi
  · intro h; rw [hem] at h ⊢; exact hi h
  · intro h; rw [hem] at h ⊢; exact hi h
  · exact hi

/-! ## Each property, action by action -/

theorem InitQuorum (st : State) (h : Init st) : EmergencyLeaseHasARosterQuorum st := by
  intro hl; rw [h.2.2.1] at hl; cases hl

/-- `EmergencyLeaseHasARosterQuorumNext == ASSUME Mut \notin {"M_NOQUORUM", "M_REGRANT"}, ...` -/
theorem NextQuorum (c : Cfg) (h1 : c.m ≠ .M_NOQUORUM) (h2 : c.m ≠ .M_REGRANT) (st st' : State)
    (hi : EmergencyLeaseHasARosterQuorum st) (hn : Next c st st') : EmergencyLeaseHasARosterQuorum st' := by
  rcases hn with ⟨t, -, -, rfl⟩ | ⟨r, -, rfl⟩ | ⟨who, -, -, -, hq, -, rfl⟩ | ⟨-, rfl⟩ | ⟨hm, -, -, -, rfl⟩ |
    ⟨-, -, rfl⟩ | rfl | ⟨t, ⟨-, -, -, -, -, hem, -⟩ | ⟨-, -, -, -, hem, -⟩⟩ | ⟨x, -, -, -, rfl⟩
  · exact hi
  · exact hi
  · -- Activate(h): the guard asks for a quorum, and the lease records that one stood behind it
    intro _
    rcases hq with hq | hq
    · exact hq
    · exact absurd hq h1
  · intro h; cases h
  · exact absurd hm h2
  · exact hi
  · exact hi
  · intro h; rw [hem] at h ⊢; exact hi h
  · intro h; rw [hem] at h ⊢; exact hi h
  · exact hi

theorem InitOneRound (st : State) (h : Init st) : EmergencyLeaseIsOneRound st := by
  intro hr; rw [h.2.2.1] at hr; exact absurd hr (Nat.lt_irrefl 0)

/-- `EmergencyLeaseIsOneRoundNext == ASSUME Mut \notin {"M_REGRANT", "M_RENEW"}, ...` -/
theorem NextOneRound (c : Cfg) (h1 : c.m ≠ .M_REGRANT) (h2 : c.m ≠ .M_RENEW) (st st' : State)
    (hi : EmergencyLeaseIsOneRound st) (hn : Next c st st') : EmergencyLeaseIsOneRound st' := by
  rcases hn with ⟨t, -, -, rfl⟩ | ⟨r, -, rfl⟩ | ⟨who, -, -, -, -, -, rfl⟩ | ⟨-, rfl⟩ | ⟨hm, -, -, -, rfl⟩ |
    ⟨hm, -, rfl⟩ | rfl | ⟨t, ⟨-, -, -, -, -, hem, -⟩ | ⟨-, -, -, -, hem, -⟩⟩ | ⟨x, -, -, -, rfl⟩
  · exact hi
  · exact hi
  · -- Activate(h): granted by the roster, not renewed
    intro _; exact ⟨rfl, rfl⟩
  · exact hi
  · exact absurd hm h1
  · exact absurd hm h2
  · exact hi
  · intro h; rw [hem] at h ⊢; exact hi h
  · intro h; rw [hem] at h ⊢; exact hi h
  · exact hi

/-- Not in the TLAPS proof: membership in the tool sets and in the approvals is decided. TLA+ decides every
membership by excluded middle, and a predicate does not. Every set the module builds is a finite union of literals,
so this holds of every reachable state under every `Mut`, and with it a proof can case on the `IF` of `EmCall` and
`ThinkerCall` without `Classical.choice`. -/
def Decided (st : State) : Prop :=
  (∀ t, t ∈ st.domainTools ∨ ¬ t ∈ st.domainTools) ∧ (∀ r, r ∈ st.approvals ∨ ¬ r ∈ st.approvals) ∧
  (∀ t, t ∈ st.em.envelope ∨ ¬ t ∈ st.em.envelope) ∧ (∀ t, t ∈ st.thinkerAllow ∨ ¬ t ∈ st.thinkerAllow)

theorem decided_singleton {α : Type} [DecidableEq α] (x a : α) : a ∈ ({x} : PSet α) ∨ ¬ a ∈ ({x} : PSet α) :=
  if h : a = x then Or.inl h else Or.inr h

theorem decided_union {α : Type} [DecidableEq α] (S : PSet α) (x a : α) (h : a ∈ S ∨ ¬ a ∈ S) :
    a ∈ S ∪ {x} ∨ ¬ a ∈ S ∪ {x} := by
  rcases h with h | h
  · exact Or.inl (Or.inl h)
  · rcases decided_singleton x a with h' | h'
    · exact Or.inl (Or.inr h')
    · exact Or.inr (fun h'' => h''.elim h h')

theorem InitDecided (st : State) (h : Init st) : Decided st := by
  obtain ⟨hd, ha, he, ht, -⟩ := h
  refine ⟨fun t => ?_, fun r => ?_, fun t => ?_, fun t => ?_⟩
  · rw [hd]; exact decided_singleton _ _
  · rw [ha]; exact Or.inr id
  · rw [he]; exact Or.inr id
  · rw [ht]; exact decided_singleton _ _

/-- `Decided` is kept by every step, under every `Mut`. -/
theorem NextDecided (c : Cfg) (st st' : State) (hd : Decided st) (hn : Next c st st') : Decided st' := by
  obtain ⟨hD, hA, hE, hT⟩ := hd
  rcases hn with ⟨t, -, -, rfl⟩ | ⟨r, -, rfl⟩ | ⟨who, -, -, -, -, -, rfl⟩ | ⟨-, rfl⟩ | ⟨-, -, -, -, rfl⟩ |
    ⟨-, -, rfl⟩ | rfl | ⟨t, ⟨-, -, -, hdt, hap, hem, hta, -⟩ | ⟨-, -, hdt, hap, hem, hta, -⟩⟩ |
    ⟨x, -, -, -, rfl⟩
  · exact ⟨fun u => decided_union _ t u (hD u), hA, hE, hT⟩
  · exact ⟨hD, fun u => decided_union _ r u (hA u), hE, hT⟩
  · exact ⟨hD, fun _ => Or.inr id, fun u => decided_union _ .te u (hD u), hT⟩
  · exact ⟨hD, hA, hE, hT⟩
  · exact ⟨hD, hA, hE, hT⟩
  · exact ⟨hD, hA, hE, hT⟩
  · exact ⟨hD, hA, hE, hT⟩
  · unfold Decided; rw [hdt, hap, hem, hta]; exact ⟨hD, hA, hE, hT⟩
  · unfold Decided; rw [hdt, hap, hem, hta]; exact ⟨hD, hA, hE, hT⟩
  · exact ⟨hD, hA, hE, hT⟩

/-- `Decided` holds of every reachable state, under every `Mut`. -/
theorem decided_reach (c : Cfg) : ∀ st, Reachable Init (Next c) st → Decided st :=
  invariant Decided Decided InitDecided (NextDecided c) (fun _ h => h)

theorem InitAllowlisted (st : State) (h : Init st) : CallsAreAllowlisted st := by
  intro x hx; rw [h.2.2.2.2.2.1] at hx; exact hx.elim

/-- `CallsAreAllowlistedNext == ASSUME Mut # "M_X1", ...`. The step cases on each call's `IF`, as TLA+ does;
`Decided` decides it. -/
theorem NextAllowlisted (c : Cfg) (hm : c.m ≠ .M_X1) (st st' : State) (hd : Decided st)
    (hi : CallsAreAllowlisted st) (hn : Next c st st') : CallsAreAllowlisted st' := by
  have hx1 : ¬ X1 c st := fun h => hm h.1
  rcases hn with ⟨t, -, -, rfl⟩ | ⟨r, -, rfl⟩ | ⟨who, -, -, -, -, -, rfl⟩ | ⟨-, rfl⟩ | ⟨-, -, -, -, rfl⟩ |
    ⟨-, -, rfl⟩ | rfl | ⟨t, ⟨-, hthen, helse, -⟩ | ⟨hthen, helse, -⟩⟩ | ⟨x, -, -, -, rfl⟩
  all_goals try exact hi
  · -- EmCall(t): with no exception, a call is admitted only for a tool of the envelope
    intro x hx
    rcases hd.2.2.1 t with ht | ht
    · rw [(hthen (Or.inl ht)).1] at hx
      have hx : x = ⟨.emergency, t, t ∈ st.em.envelope, st.obsLive⟩ := hx
      subst hx; exact ht
    · rw [(helse (fun h => h.elim ht hx1)).2] at hx
      exact hi x hx
  · -- ThinkerCall(t): with no exception, a call is admitted only for a tool of the Thinker's allowlist
    intro x hx
    rcases hd.2.2.2 t with ht | ht
    · by_cases ho : st.obsLive = true ∨ c.m = .M_UNCOUPLE
      · rw [(hthen ⟨Or.inl ht, ho⟩).1] at hx
        have hx : x = ⟨.thinker, t, t ∈ st.thinkerAllow, st.obsLive⟩ := hx
        subst hx; exact ht
      · rw [(helse (fun h => ho h.2)).2] at hx
        exact hi x hx
    · rw [(helse (fun h => h.1.elim ht hx1)).2] at hx
      exact hi x hx

theorem InitCoupled (st : State) (h : Init st) : ThinkerStillCoupled st := by
  intro x hx; rw [h.2.2.2.2.2.1] at hx; exact hx.elim

/-- `ThinkerStillCoupledNext == ASSUME Mut # "M_UNCOUPLE", ...`. The goal for a call is a Boolean, so the step
needs no decision of the `IF`: a call recorded unobserved could have come from neither branch. -/
theorem NextCoupled (c : Cfg) (hm : c.m ≠ .M_UNCOUPLE) (st st' : State)
    (hi : ThinkerStillCoupled st) (hn : Next c st st') : ThinkerStillCoupled st' := by
  rcases hn with ⟨t, -, -, rfl⟩ | ⟨r, -, rfl⟩ | ⟨who, -, -, -, -, -, rfl⟩ | ⟨-, rfl⟩ | ⟨-, -, -, -, rfl⟩ |
    ⟨-, -, rfl⟩ | rfl | ⟨t, ⟨-, hthen, helse, -⟩ | ⟨hthen, helse, -⟩⟩ | ⟨x, -, -, -, rfl⟩
  all_goals try exact hi
  · -- EmCall(t): an admitted call is the emergency seat's, not a Thinker's
    intro x hx hs
    cases ho : x.observed
    · exfalso
      have hna : ¬ (t ∈ st.em.envelope ∨ X1 c st) := by
        intro ha
        rw [(hthen ha).1] at hx
        have hx : x = ⟨.emergency, t, t ∈ st.em.envelope, st.obsLive⟩ := hx
        subst hx; cases hs
      rw [(helse hna).2] at hx
      have h' := hi x hx hs
      rw [ho] at h'; cases h'
    · rfl
  · -- ThinkerCall(t): admitted only with a live Observer, whose state the record copies
    intro x hx hs
    cases ho : x.observed
    · exfalso
      have hna : ¬ ((t ∈ st.thinkerAllow ∨ X1 c st) ∧ (st.obsLive = true ∨ c.m = .M_UNCOUPLE)) := by
        intro ha
        rw [(hthen ha).1] at hx
        have hx : x = ⟨.thinker, t, t ∈ st.thinkerAllow, st.obsLive⟩ := hx
        subst hx
        have ho : st.obsLive = false := ho
        rcases ha.2 with h | h
        · rw [ho] at h; cases h
        · exact hm h
      rw [(helse hna).2] at hx
      have h' := hi x hx hs
      rw [ho] at h'; cases h'
    · rfl

theorem InitForensic (st : State) (h : Init st) : ActivationIsForensic st := by
  rintro n ⟨h1, h2⟩; rw [h.2.2.1] at h2
  exact absurd (Nat.le_trans h1 h2) (by decide)

/-- `ActivationIsForensicNext == ASSUME Mut \notin {"M_REGRANT", "M_ERASE"}, ...`: "an old round, or the new one". -/
theorem NextForensic (c : Cfg) (h1 : c.m ≠ .M_REGRANT) (h2 : c.m ≠ .M_ERASE) (st st' : State)
    (hi : ActivationIsForensic st) (hn : Next c st st') : ActivationIsForensic st' := by
  rcases hn with ⟨t, -, -, rfl⟩ | ⟨r, -, rfl⟩ | ⟨who, -, -, -, -, -, rfl⟩ | ⟨-, rfl⟩ | ⟨hm, -, -, -, rfl⟩ |
    ⟨-, -, rfl⟩ | rfl | ⟨t, ⟨-, -, -, -, -, hem, -, -, hrec⟩ | ⟨-, -, -, -, hem, -, -, hrec⟩⟩ |
    ⟨x, -, hm, -, rfl⟩
  · exact hi
  · exact hi
  · -- Activate(h): the new round's record is appended
    rintro n ⟨hn1, hn2⟩
    by_cases hle : n ≤ st.em.round
    · obtain ⟨x, hx, hxr⟩ := hi n ⟨hn1, hle⟩
      exact ⟨x, Or.inl hx, hxr⟩
    · refine ⟨⟨st.em.round + 1, who, st.approvals⟩, Or.inr rfl, ?_⟩
      have hn2 : n ≤ st.em.round + 1 := hn2
      show st.em.round + 1 = n
      omega
  · exact hi
  · exact absurd hm h1
  · exact hi
  · exact hi
  · intro n hn; rw [hem] at hn; rw [hrec]; exact hi n hn
  · intro n hn; rw [hem] at hn; rw [hrec]; exact hi n hn
  · exact absurd hm h2

/-! ## The theorems -/

/-- `THEOREM EmergencyLeaseHasARosterQuorumAlways == ASSUME Mut \notin {"M_NOQUORUM", "M_REGRANT"}
PROVE Spec => []EmergencyLeaseHasARosterQuorum` -/
theorem EmergencyLeaseHasARosterQuorumAlways (c : Cfg) (h1 : c.m ≠ .M_NOQUORUM) (h2 : c.m ≠ .M_REGRANT) :
    ∀ st, Reachable Init (Next c) st → EmergencyLeaseHasARosterQuorum st :=
  invariant EmergencyLeaseHasARosterQuorum EmergencyLeaseHasARosterQuorum InitQuorum (NextQuorum c h1 h2)
    (fun _ h => h)

/-- `THEOREM EmergencyLeaseIsOneRoundAlways == ASSUME Mut \notin {"M_REGRANT", "M_RENEW"}
PROVE Spec => []EmergencyLeaseIsOneRound` -/
theorem EmergencyLeaseIsOneRoundAlways (c : Cfg) (h1 : c.m ≠ .M_REGRANT) (h2 : c.m ≠ .M_RENEW) :
    ∀ st, Reachable Init (Next c) st → EmergencyLeaseIsOneRound st :=
  invariant EmergencyLeaseIsOneRound EmergencyLeaseIsOneRound InitOneRound (NextOneRound c h1 h2) (fun _ h => h)

/-- `THEOREM NoAgentHoldsAnEmergencySeatAlways == ASSUME Mut # "M_AGENT" PROVE Spec => []NoAgentHoldsAnEmergencySeat`,
from `HolderIsPerson` and `LiveHasRound`. -/
theorem NoAgentHoldsAnEmergencySeatAlways (c : Cfg) (hm : c.m ≠ .M_AGENT) :
    ∀ st, Reachable Init (Next c) st → NoAgentHoldsAnEmergencySeat st :=
  invariant (fun st => HolderIsPerson st ∧ LiveHasRound st) NoAgentHoldsAnEmergencySeat
    (fun st h => ⟨InitHolder st h, InitLiveHasRound st h⟩)
    (fun st st' hi hn => ⟨NextHolder c hm st st' hi.1 hn, NextLiveHasRound c st st' hi.2 hn⟩)
    (fun _ hi hl => hi.1 (hi.2 hl))

/-- `THEOREM CallsAreAllowlistedAlways == ASSUME Mut # "M_X1" PROVE Spec => []CallsAreAllowlisted`, with `Decided`. -/
theorem CallsAreAllowlistedAlways (c : Cfg) (hm : c.m ≠ .M_X1) :
    ∀ st, Reachable Init (Next c) st → CallsAreAllowlisted st :=
  invariant (fun st => CallsAreAllowlisted st ∧ Decided st) CallsAreAllowlisted
    (fun st h => ⟨InitAllowlisted st h, InitDecided st h⟩)
    (fun st st' hi hn => ⟨NextAllowlisted c hm st st' hi.2 hi.1 hn, NextDecided c st st' hi.2 hn⟩)
    (fun _ h => h.1)

/-- `THEOREM ThinkerStillCoupledAlways == ASSUME Mut # "M_UNCOUPLE" PROVE Spec => []ThinkerStillCoupled` -/
theorem ThinkerStillCoupledAlways (c : Cfg) (hm : c.m ≠ .M_UNCOUPLE) :
    ∀ st, Reachable Init (Next c) st → ThinkerStillCoupled st :=
  invariant ThinkerStillCoupled ThinkerStillCoupled InitCoupled (NextCoupled c hm) (fun _ h => h)

/-- `THEOREM ActivationIsForensicAlways == ASSUME Mut \notin {"M_REGRANT", "M_ERASE"}
PROVE Spec => []ActivationIsForensic` -/
theorem ActivationIsForensicAlways (c : Cfg) (h1 : c.m ≠ .M_REGRANT) (h2 : c.m ≠ .M_ERASE) :
    ∀ st, Reachable Init (Next c) st → ActivationIsForensic st :=
  invariant ActivationIsForensic ActivationIsForensic InitForensic (NextForensic c h1 h2) (fun _ h => h)

/-- `THEOREM SafeAlways == ASSUME Mut = "none" PROVE Spec => []Safe`, for every MaxRound. -/
theorem SafeAlways (MaxRound : Nat) :
    ∀ st, Reachable Init (Next ⟨.none, MaxRound⟩) st → Safe st :=
  fun st h => ⟨EmergencyLeaseHasARosterQuorumAlways ⟨.none, MaxRound⟩ nofun nofun st h,
    EmergencyLeaseIsOneRoundAlways ⟨.none, MaxRound⟩ nofun nofun st h,
    NoAgentHoldsAnEmergencySeatAlways ⟨.none, MaxRound⟩ nofun st h,
    CallsAreAllowlistedAlways ⟨.none, MaxRound⟩ nofun st h,
    ThinkerStillCoupledAlways ⟨.none, MaxRound⟩ nofun st h,
    ActivationIsForensicAlways ⟨.none, MaxRound⟩ nofun nofun st h⟩

/-! ## What each mutation admits: the guard it removes (the counterexamples are TLC's) -/

/-- `LEMMA MutX1AdmitsAnything == (Mut = "M_X1" /\ Quorate(approvals)) => X1` -/
theorem MutX1AdmitsAnything (c : Cfg) (st : State) (h : c.m = .M_X1 ∧ Quorate st.approvals) : X1 c st := h

/-- `LEMMA NoneHasNoException == Mut # "M_X1" => ~X1` -/
theorem NoneHasNoException (c : Cfg) (st : State) (h : c.m ≠ .M_X1) : ¬ X1 c st := fun hx => h hx.1

/-- `LEMMA NoneNeverContinues == Mut \notin {"M_REGRANT", "M_RENEW"} => ~Regrant /\ ~Renew` -/
theorem NoneNeverContinues (c : Cfg) (h1 : c.m ≠ .M_REGRANT) (h2 : c.m ≠ .M_RENEW) (st st' : State) :
    ¬ Regrant c st st' ∧ ¬ Renew c st st' :=
  ⟨fun h => h1 h.1, fun h => h2 h.1⟩

/-- `LEMMA NoneNeverErases == Mut # "M_ERASE" => \A x \in records : ~Erase(x)` -/
theorem NoneNeverErases (c : Cfg) (h : c.m ≠ .M_ERASE) (st st' : State) :
    ∀ x, x ∈ st.records → ¬ Erase c x st st' :=
  fun _ _ he => h he.1

/-! ## In place of the ENABLED lemma Emergency_proof.tla dropped, of Emergency.tla itself -/

/-- Not in `Emergency_proof.tla`; `Emergency_live_proof.tla`'s `EnvelopeHasTe`: every lease the seat has had holds
te, which `Activate` puts in every envelope and nothing takes out. `em.round > 0 => "te" \in em.envelope` -/
def EnvelopeHasTe (st : State) : Prop := st.em.round > 0 → Tool.te ∈ st.em.envelope

/-- Not in the TLAPS proof: `em.round <= MaxRound`. -/
def RoundBounded (c : Cfg) (st : State) : Prop := st.em.round ≤ c.MaxRound

/-- What the `ENABLED` theorems need of a reachable state: `LiveHasRound`, `EnvelopeHasTe`, `RoundBounded`. -/
def SeatInv (c : Cfg) (st : State) : Prop := LiveHasRound st ∧ EnvelopeHasTe st ∧ RoundBounded c st

theorem InitSeatInv (c : Cfg) (st : State) (h : Init st) : SeatInv c st := by
  refine ⟨InitLiveHasRound st h, fun hr => ?_, ?_⟩
  · rw [h.2.2.1] at hr; exact absurd hr (Nat.lt_irrefl 0)
  · unfold RoundBounded; rw [h.2.2.1]; exact Nat.zero_le _

/-- `SeatInv` is kept by every step, under every `Mut`. -/
theorem NextSeatInv (c : Cfg) (st st' : State) (hi : SeatInv c st) (hn : Next c st st') : SeatInv c st' := by
  have hl' := NextLiveHasRound c st st' hi.1 hn
  obtain ⟨-, hte, hb⟩ := hi
  rcases hn with ⟨t, -, -, rfl⟩ | ⟨r, -, rfl⟩ | ⟨who, -, -, hlt, -, -, rfl⟩ | ⟨-, rfl⟩ | ⟨-, -, hpos, hlt, rfl⟩ |
    ⟨-, -, rfl⟩ | rfl | ⟨t, ⟨-, -, -, -, -, hem, -⟩ | ⟨-, -, -, -, hem, -⟩⟩ | ⟨x, -, -, -, rfl⟩
  · exact ⟨hl', hte, hb⟩
  · exact ⟨hl', hte, hb⟩
  · -- Activate(h): te is in the new envelope, and the round stays within the bound
    exact ⟨hl', fun _ => Or.inr rfl, Nat.succ_le_of_lt hlt⟩
  · exact ⟨hl', hte, hb⟩
  · -- Regrant: the envelope is the last round's, which held te
    exact ⟨hl', fun _ => hte hpos, Nat.succ_le_of_lt hlt⟩
  · exact ⟨hl', hte, hb⟩
  · exact ⟨hl', hte, hb⟩
  · refine ⟨hl', ?_, ?_⟩
    · intro hr; rw [hem] at hr ⊢; exact hte hr
    · unfold RoundBounded; rw [hem]; exact hb
  · refine ⟨hl', ?_, ?_⟩
    · intro hr; rw [hem] at hr ⊢; exact hte hr
    · unfold RoundBounded; rw [hem]; exact hb
  · exact ⟨hl', hte, hb⟩

/-- `SeatInv` holds of every reachable state, under every `Mut`. -/
theorem seatInv_reach (c : Cfg) : ∀ st, Reachable Init (Next c) st → SeatInv c st :=
  invariant (SeatInv c) (SeatInv c) (InitSeatInv c) (NextSeatInv c) (fun _ h => h)

/-- The fact `Emergency_proof.tla` records dropping (its statement was never committed), kernel-checked: in every
state Emergency.tla's `Spec` reaches with the seat live and no live Observer, an `EmCall` step of a tool in the
envelope admits the call, and records it as not observed. The step is a `Next` step, and its record is the only
call. Under every `Mut` and every `MaxRound`: the guard of Emergency.tla's `EmCall` does not read the Observer. The
tool is te, which every live envelope holds; t1 would do as well. -/
theorem UnobservedEmergencyCallEnabledAlways (c : Cfg) :
    ∀ st, Reachable Init (Next c) st → st.em.live = true → st.obsLive = false →
      ∃ t st', Next c st st' ∧ EmCall c t st st' ∧ t ∈ st.em.envelope ∧
        st'.calls = {⟨.emergency, t, t ∈ st.em.envelope, false⟩} := by
  intro st hr hl ho
  obtain ⟨hlr, hte, -⟩ := seatInv_reach c st hr
  have hte : Tool.te ∈ st.em.envelope := hte (hlr hl)
  have he : EmCall c .te st { st with calls := {⟨.emergency, .te, .te ∈ st.em.envelope, st.obsLive⟩} } :=
    ⟨hl, fun _ => ⟨rfl, rfl⟩, fun hn => absurd (Or.inl hte) hn, rfl, rfl, rfl, rfl, rfl, rfl⟩
  refine ⟨.te, _, Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inl ⟨.te, Or.inl he⟩))))))),
    he, hte, ?_⟩
  show ({⟨.emergency, .te, .te ∈ st.em.envelope, st.obsLive⟩} : PSet CallRec) =
    {⟨.emergency, .te, .te ∈ st.em.envelope, false⟩}
  rw [ho]

/-! ## Emergency_live.tla -/

/-- Under Emergency_live.tla's two mutations, an emergency call is coupled.
`EmCoupled == \/ Mut = "M_EMCOUPLE" \/ (Mut = "M_EMCOUPLE2" /\ em.round >= 2)` -/
def EmCoupled (c : Cfg) (st : State) : Prop := c.m = .M_EMCOUPLE ∨ (c.m = .M_EMCOUPLE2 ∧ st.em.round ≥ 2)

/-- `EmCoupled` compares `Mut` and a round, so it is decided. -/
instance (c : Cfg) (st : State) : Decidable (EmCoupled c st) := by unfold EmCoupled; infer_instance

/-- `EmCall(t)`'s admit, open to the coupling.
```
EmAdmit(t) ==
  /\ em.live
  /\ (t \in em.envelope \/ X1)
  /\ (obsLive \/ ~EmCoupled)
  /\ calls' = {[seat |-> "emergency", tool |-> t, allowlisted |-> t \in em.envelope,
                observed |-> obsLive]}
  /\ UNCHANGED <<domainTools, approvals, em, thinkerAllow, obsLive, refused, records>>
``` -/
def EmAdmit (c : Cfg) (t : Tool) (st st' : State) : Prop :=
  st.em.live = true ∧ (t ∈ st.em.envelope ∨ X1 c st) ∧ (st.obsLive = true ∨ ¬ EmCoupled c st) ∧
  st' = { st with calls := {⟨.emergency, t, t ∈ st.em.envelope, st.obsLive⟩} }

/-- `EmCall(t)`'s refusal.
```
EmRefuse(t) ==
  /\ em.live
  /\ ~((t \in em.envelope \/ X1) /\ (obsLive \/ ~EmCoupled))
  /\ refused' = TRUE
  /\ UNCHANGED <<domainTools, approvals, em, thinkerAllow, obsLive, calls, records>>
``` -/
def EmRefuse (c : Cfg) (t : Tool) (st st' : State) : Prop :=
  st.em.live = true ∧ ¬ ((t ∈ st.em.envelope ∨ X1 c st) ∧ (st.obsLive = true ∨ ¬ EmCoupled c st)) ∧
  st' = { st with refused := true }

/-- ```
NextL ==
  \/ \E t \in Domain : Promote(t)
  \/ \E r \in Roster : Approve(r)
  \/ \E h \in Holders : Activate(h)
  \/ EndEm \/ Regrant \/ Renew \/ ObsToggle
  \/ \E t \in Tools : EmAdmit(t) \/ EmRefuse(t) \/ ThinkerCall(t)
  \/ \E x \in records : Erase(x)
``` -/
def NextL (c : Cfg) (st st' : State) : Prop :=
  (∃ t, t ∈ Domain ∧ Promote t st st') ∨ (∃ r, Approve r st st') ∨ (∃ who, who ∈ Holders ∧ Activate c who st st') ∨
  EndEm st st' ∨ Regrant c st st' ∨ Renew c st st' ∨ ObsToggle st st' ∨
  (∃ t, EmAdmit c t st st' ∨ EmRefuse c t st st' ∨ ThinkerCall c t st st') ∨
  (∃ x, x ∈ st.records ∧ Erase c x st st')

/-- While the seat is live, a call of any tool in its envelope can be admitted, whatever the Observer's state.
`EmergencyNeverCoupled == \A t \in Tools : (em.live /\ t \in em.envelope) => ENABLED EmAdmit(t)` -/
def EmergencyNeverCoupled (c : Cfg) (st : State) : Prop :=
  ∀ t, (st.em.live = true ∧ t ∈ st.em.envelope) → Enabled (EmAdmit c t) st

/-- While the seat is live and the Observer is not, some emergency call can be admitted.
`EmergencyCallsWithoutObserver == (em.live /\ ~obsLive) => \E t \in Tools : ENABLED EmAdmit(t)` -/
def EmergencyCallsWithoutObserver (c : Cfg) (st : State) : Prop :=
  (st.em.live = true ∧ st.obsLive = false) → ∃ t, Enabled (EmAdmit c t) st

/-! ### NextL against Next -/

/-- Every `NextL` step is a `Next` step, under every `Mut` and from every state. An `EmAdmit` is an admitting
`EmCall`. An `EmRefuse` is a refusing `EmCall` when the coupling does not hold the call back. When it does, the
Observer is not live and `Mut` is a coupling mutation, not `M_UNCOUPLE`, so `ThinkerCall` of the same tool refuses
by R3 and makes the same change, `refused' = TRUE` and nothing else. -/
theorem nextL_next (c : Cfg) (st st' : State) (h : NextL c st st') : Next c st st' := by
  rcases h with h | h | h | h | h | h | h | ⟨t, h | h | h⟩ | h
  · exact Or.inl h
  · exact Or.inr (Or.inl h)
  · exact Or.inr (Or.inr (Or.inl h))
  · exact Or.inr (Or.inr (Or.inr (Or.inl h)))
  · exact Or.inr (Or.inr (Or.inr (Or.inr (Or.inl h))))
  · exact Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inl h)))))
  · exact Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inl h))))))
  · -- EmAdmit(t): an EmCall(t) that admits
    obtain ⟨hl, ha, -, rfl⟩ := h
    exact Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inl ⟨t, Or.inl
      ⟨hl, fun _ => ⟨rfl, rfl⟩, fun hn => absurd ha hn, rfl, rfl, rfl, rfl, rfl, rfl⟩⟩)))))))
  · obtain ⟨hl, hr, rfl⟩ := h
    by_cases hb : st.obsLive = true ∨ ¬ EmCoupled c st
    · -- not held back: the tool is outside the envelope, and EmCall(t) refuses it
      exact Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inl ⟨t, Or.inl
        ⟨hl, fun ha => absurd ⟨ha, hb⟩ hr, fun _ => ⟨rfl, rfl⟩, rfl, rfl, rfl, rfl, rfl, rfl⟩⟩)))))))
    · -- held back: the Observer is not live, so ThinkerCall(t) refuses, with the same change
      have ho : st.obsLive = false := by
        cases h : st.obsLive
        · rfl
        · exact absurd (Or.inl h) hb
      have hu : c.m ≠ .M_UNCOUPLE := by
        intro hmu
        apply hb; apply Or.inr; intro hc
        rcases hc with hc | ⟨hc, -⟩ <;> rw [hmu] at hc <;> cases hc
      exact Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inl ⟨t, Or.inr
        ⟨fun hc => hc.2.elim (fun h => by rw [ho] at h; cases h) (fun h => absurd h hu),
          fun _ => ⟨rfl, rfl⟩, rfl, rfl, rfl, rfl, rfl, rfl⟩⟩)))))))
  · exact Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inl ⟨t, Or.inr h⟩)))))))
  · exact Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr h)))))))

/-- Every state Emergency_live.tla's `SpecL` reaches is one Emergency.tla's `Spec` reaches, under every `Mut`. -/
theorem reachL_reach (c : Cfg) : ∀ st, Reachable Init (NextL c) st → Reachable Init (Next c) st :=
  Reachable.mono (nextL_next c)

/-- Every invariant of Emergency.tla holds of `SpecL`, under `none` and under Emergency_live.tla's two mutations,
which break none of them. -/
theorem SafeLAlways (c : Cfg) (hm : c.m = .none ∨ c.m = .M_EMCOUPLE ∨ c.m = .M_EMCOUPLE2) :
    ∀ st, Reachable Init (NextL c) st → Safe st := by
  intro st hr
  have hr := reachL_reach c st hr
  rcases hm with hm | hm | hm <;>
  exact ⟨EmergencyLeaseHasARosterQuorumAlways c (by rw [hm]; decide) (by rw [hm]; decide) st hr,
    EmergencyLeaseIsOneRoundAlways c (by rw [hm]; decide) (by rw [hm]; decide) st hr,
    NoAgentHoldsAnEmergencySeatAlways c (by rw [hm]; decide) st hr,
    CallsAreAllowlistedAlways c (by rw [hm]; decide) st hr,
    ThinkerStillCoupledAlways c (by rw [hm]; decide) st hr,
    ActivationIsForensicAlways c (by rw [hm]; decide) (by rw [hm]; decide) st hr⟩

/-- A state, field by field. -/
theorem State.eq_of {s t : State} (h1 : s.domainTools = t.domainTools) (h2 : s.approvals = t.approvals)
    (h3 : s.em = t.em) (h4 : s.thinkerAllow = t.thinkerAllow) (h5 : s.obsLive = t.obsLive)
    (h6 : s.calls = t.calls) (h7 : s.refused = t.refused) (h8 : s.records = t.records) : s = t := by
  cases s; cases t; cases h1; cases h2; cases h3; cases h4; cases h5; cases h6; cases h7; cases h8; rfl

/-- Outside the coupling mutations, an `EmCall(t)` step whose `IF` is decided is an `EmAdmit(t)` or an
`EmRefuse(t)` step. -/
theorem emCall_split (c : Cfg) (h1 : c.m ≠ .M_EMCOUPLE) (h2 : c.m ≠ .M_EMCOUPLE2) (t : Tool) (st st' : State)
    (hdec : (t ∈ st.em.envelope ∨ X1 c st) ∨ ¬ (t ∈ st.em.envelope ∨ X1 c st)) (h : EmCall c t st st') :
    EmAdmit c t st st' ∨ EmRefuse c t st st' := by
  have hnc : ¬ EmCoupled c st := fun h => h.elim h1 (fun h => h2 h.1)
  obtain ⟨hl, hthen, helse, hdt, hap, hem, hta, hobs, hrec⟩ := h
  rcases hdec with ha | ha
  · obtain ⟨hc, hr⟩ := hthen ha
    exact Or.inl ⟨hl, ha, Or.inr hnc, State.eq_of hdt hap hem hta hobs hc hr hrec⟩
  · obtain ⟨hr, hc⟩ := helse ha
    exact Or.inr ⟨hl, fun h => ha h.1, State.eq_of hdt hap hem hta hobs hc hr hrec⟩

/-- Outside the coupling mutations, a `Next` step from a state where each call's `IF` is decided is a `NextL` step. -/
theorem next_nextL (c : Cfg) (h1 : c.m ≠ .M_EMCOUPLE) (h2 : c.m ≠ .M_EMCOUPLE2) (st st' : State)
    (hdec : ∀ t, (t ∈ st.em.envelope ∨ X1 c st) ∨ ¬ (t ∈ st.em.envelope ∨ X1 c st)) (h : Next c st st') :
    NextL c st st' := by
  rcases h with h | h | h | h | h | h | h | ⟨t, h | h⟩ | h
  · exact Or.inl h
  · exact Or.inr (Or.inl h)
  · exact Or.inr (Or.inr (Or.inl h))
  · exact Or.inr (Or.inr (Or.inr (Or.inl h)))
  · exact Or.inr (Or.inr (Or.inr (Or.inr (Or.inl h))))
  · exact Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inl h)))))
  · exact Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inl h))))))
  · rcases emCall_split c h1 h2 t st st' (hdec t) h with h | h
    · exact Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inl ⟨t, Or.inl h⟩)))))))
    · exact Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inl ⟨t, Or.inr (Or.inl h)⟩)))))))
  · exact Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inl ⟨t, Or.inr (Or.inr h)⟩)))))))
  · exact Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr h)))))))

/-- Emergency_live.tla's header: "Under every Mut of Emergency.tla the two together are EmCall exactly, so NextL
is Emergency's Next". Over every pair of states, so the split of `EmCall`'s `IF` is by excluded middle on the
membership, as in TLA+: this is the one theorem here that uses `Classical.choice`, and `nextL_iff_next_needs_em`
shows that it must. (`Mirror.nextL_iff` is another theorem: the mirror's successor list for `NextL`.) -/
theorem nextL_iff_next (c : Cfg) (h1 : c.m ≠ .M_EMCOUPLE) (h2 : c.m ≠ .M_EMCOUPLE2) (st st' : State) :
    NextL c st st' ↔ Next c st st' :=
  ⟨nextL_next c st st', next_nextL c h1 h2 st st' (fun _ => Classical.em _)⟩

/-- Why `nextL_iff_next` cannot do without `Classical.choice`: over every pair of states it gives excluded middle, which
`propext` and `Quot.sound` do not. Take a live seat whose envelope is `fun _ => P`, with a call already recorded and
a refusal already made. The step that changes nothing is then an `EmCall` step, by either branch of its `IF`, so a
`Next` step. As a `NextL` step it can only be an `EmAdmit`, which needs `P`, or an `EmRefuse`, which needs `¬ P`:
the Thinker's allowlist is every tool and its Observer is live, so no `ThinkerCall` leaves `calls` as it is. -/
theorem nextL_iff_next_needs_em (h : ∀ st st', NextL ⟨.none, 0⟩ st st' ↔ Next ⟨.none, 0⟩ st st') (P : Prop) :
    P ∨ ¬ P := by
  let st : State :=
    { domainTools := ∅, approvals := ∅,
      em := { live := true, round := 1, holder := .h, envelope := fun _ => P, quorate := True,
              grantor := .roster, renewed := false },
      thinkerAllow := univ, obsLive := true, calls := {⟨.emergency, .t1, P, true⟩}, refused := true,
      records := ∅ }
  have hn : Next ⟨.none, 0⟩ st st :=
    Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inl ⟨.t1, Or.inl
      ⟨rfl, fun _ => ⟨rfl, rfl⟩, fun _ => ⟨rfl, rfl⟩, rfl, rfl, rfl, rfl, rfl, rfl⟩⟩)))))))
  rcases (h st st).mpr hn with ⟨t, -, -, he⟩ | ⟨r, -, he⟩ | ⟨_, -, hl, -⟩ | ⟨-, he⟩ | ⟨-, hl, -⟩ | ⟨-, -, he⟩ | he |
    ⟨t, ⟨-, ha, -, -⟩ | ⟨-, hr, -⟩ | ⟨hthen, -, -⟩⟩ | ⟨x, hx, -⟩
  · -- Promote(t) would put t in an empty domain
    have h' := congrFun (congrArg State.domainTools he) t
    exact (h'.mpr (Or.inr rfl) : False).elim
  · -- Approve(r) would put r in empty approvals
    have h' := congrFun (congrArg State.approvals he) r
    exact (h'.mpr (Or.inr rfl) : False).elim
  · cases hl                                   -- Activate(h) needs the seat not live
  · cases congrArg (fun s => s.em.live) he     -- EndEm would end the lease
  · cases hl                                   -- Regrant needs the seat not live
  · cases congrArg (fun s => s.em.renewed) he  -- Renew would mark the lease renewed
  · cases congrArg State.obsLive he            -- ObsToggle would flip the Observer
  · -- EmAdmit(t): t is in the envelope, so P; the approvals are empty, so X1 does not hold
    rcases ha with ha | ⟨-, _, _, ha, -⟩
    · exact Or.inl ha
    · exact (ha : False).elim
  · -- EmRefuse(t): with a live Observer and no coupling, t is not in the envelope, so ¬ P
    exact Or.inr (fun hp => hr ⟨Or.inl hp, Or.inl rfl⟩)
  · -- ThinkerCall(t) admits, and would replace the emergency call by a Thinker's
    have hc := (hthen ⟨Or.inl trivial, Or.inl rfl⟩).1
    have hx : (⟨.emergency, .t1, P, true⟩ : CallRec) ∈ st.calls := rfl
    rw [hc] at hx
    cases hx
  · exact (hx : False).elim                    -- Erase(x) needs a record, and there is none

/-- A quorum of a decided set of members is decided: three members, three pairs. -/
theorem quorate_decided (S : PSet Member) (h : ∀ r, r ∈ S ∨ ¬ r ∈ S) : Quorate S ∨ ¬ Quorate S := by
  rcases h .r1 with h1 | h1 <;> rcases h .r2 with h2 | h2 <;> rcases h .r3 with h3 | h3
  all_goals first
    | exact Or.inl ⟨.r1, .r2, h1, h2, by decide⟩
    | exact Or.inl ⟨.r1, .r3, h1, h3, by decide⟩
    | exact Or.inl ⟨.r2, .r3, h2, h3, by decide⟩
    | exact Or.inr (fun ⟨a, b, ha, hb, hab⟩ => by
        cases a <;> cases b <;> first | exact hab rfl | contradiction)

/-- In a state where membership is decided, each call's `IF` is decided. -/
theorem call_decided (c : Cfg) (st : State) (hd : Decided st) (t : Tool) :
    (t ∈ st.em.envelope ∨ X1 c st) ∨ ¬ (t ∈ st.em.envelope ∨ X1 c st) := by
  rcases hd.2.2.1 t with ht | ht
  · exact Or.inl (Or.inl ht)
  · by_cases hm : c.m = .M_X1
    · rcases quorate_decided st.approvals hd.2.1 with hq | hq
      · exact Or.inl (Or.inr ⟨hm, hq⟩)
      · exact Or.inr (fun h => h.elim ht (fun h => hq h.2))
    · exact Or.inr (fun h => h.elim ht (fun h => hm h.1))

/-- Outside the coupling mutations, `Spec` and `SpecL` reach the same states, and from them take the same steps:
the state graph is the same. Without `Classical.choice`: in a reachable state membership is decided. -/
theorem reachL_iff (c : Cfg) (h1 : c.m ≠ .M_EMCOUPLE) (h2 : c.m ≠ .M_EMCOUPLE2) (st : State) :
    (Reachable Init (NextL c) st ↔ Reachable Init (Next c) st) ∧
    (Reachable Init (Next c) st → ∀ st', NextL c st st' ↔ Next c st st') := by
  refine ⟨⟨reachL_reach c st, fun hr => ?_⟩, fun hr st' =>
    ⟨nextL_next c st st', next_nextL c h1 h2 st st' (call_decided c st (decided_reach c st hr))⟩⟩
  induction hr with
  | init hi => exact .init hi
  | step hr hn ih =>
    exact .step ih (next_nextL c h1 h2 _ _ (call_decided c _ (decided_reach c _ hr)) hn)

/-! ### The two ENABLED invariants -/

/-- Outside the coupling mutations `EmergencyNeverCoupled` holds in every state, not only the reachable ones: the
specified admit asks nothing of the Observer. -/
theorem EmergencyNeverCoupledValid (c : Cfg) (h1 : c.m ≠ .M_EMCOUPLE) (h2 : c.m ≠ .M_EMCOUPLE2) (st : State) :
    EmergencyNeverCoupled c st :=
  fun _ ⟨hl, ht⟩ => ⟨_, hl, Or.inl ht, Or.inr (fun h => h.elim h1 (fun h => h2 h.1)), rfl⟩

/-- No round in which the seat can be live is a coupled one. `M_EMCOUPLE` couples every round, so it needs `MaxRound = 0`, where
the seat is never seated; `M_EMCOUPLE2` couples from the second, so it needs `MaxRound <= 1`. Every other `Mut`
satisfies it (`noCoupledRound_of`). Not in the TLA+: the hypothesis of the two `ENABLED` theorems. -/
def NoCoupledRound (c : Cfg) : Prop := (c.m = .M_EMCOUPLE → c.MaxRound = 0) ∧ (c.m = .M_EMCOUPLE2 → c.MaxRound ≤ 1)

theorem noCoupledRound_of (c : Cfg) (h1 : c.m ≠ .M_EMCOUPLE) (h2 : c.m ≠ .M_EMCOUPLE2) : NoCoupledRound c :=
  ⟨fun h => absurd h h1, fun h => absurd h h2⟩

/-- When no round the seat can reach is coupled, a live lease in a reachable state is not coupled. -/
theorem uncoupled_live (c : Cfg) (hu : NoCoupledRound c) (st : State) (hi : SeatInv c st)
    (hl : st.em.live = true) : ¬ EmCoupled c st := by
  obtain ⟨hlr, -, hb⟩ := hi
  have hpos := hlr hl
  unfold RoundBounded at hb
  rintro (hm | ⟨hm, hge⟩)
  · have := hu.1 hm; omega
  · have := hu.2 hm; omega

/-- `SpecL => []EmergencyNeverCoupled`, proved of every state Emergency.tla's `Spec` reaches, and so (`reachL_reach`)
of every state `SpecL` reaches, under `NoCoupledRound`. It can be no weaker: `EmergencyNeverCoupledIff`. -/
theorem EmergencyNeverCoupledAlways (c : Cfg) (hu : NoCoupledRound c) :
    ∀ st, Reachable Init (Next c) st → EmergencyNeverCoupled c st := by
  intro st hr t ⟨hl, ht⟩
  exact ⟨_, hl, Or.inl ht, Or.inr (uncoupled_live c hu st (seatInv_reach c st hr) hl), rfl⟩

/-- `SpecL => []EmergencyCallsWithoutObserver`, proved of every state Emergency.tla's `Spec` reaches, and so of
every state `SpecL` reaches, under `NoCoupledRound`: the call of te can be admitted, since every live envelope
holds te (t1 would do as well). It can be no weaker: `EmergencyCallsWithoutObserverIff`. -/
theorem EmergencyCallsWithoutObserverAlways (c : Cfg) (hu : NoCoupledRound c) :
    ∀ st, Reachable Init (Next c) st → EmergencyCallsWithoutObserver c st := by
  rintro st hr ⟨hl, -⟩
  have hi := seatInv_reach c st hr
  exact ⟨.te, _, hl, Or.inl (hi.2.1 (hi.1 hl)), Or.inr (uncoupled_live c hu st hi hl), rfl⟩

/-! ### Why the two mutations must fail (the counterexamples are TLC's) -/

/-- A coupled emergency call waits for the Observer: with none live, no `EmAdmit(t)` step exists. -/
theorem coupled_waits (c : Cfg) (st : State) (ho : st.obsLive = false) (hc : EmCoupled c st) (t : Tool) :
    ¬ Enabled (EmAdmit c t) st := by
  rintro ⟨_, -, -, hb, -⟩
  rcases hb with hb | hb
  · rw [ho] at hb; cases hb
  · exact hb hc

/-- `MutEmCoupleWaits`: under `M_EMCOUPLE`, with no live Observer, no emergency call can be admitted. -/
theorem MutEmCoupleWaits (MaxRound : Nat) (st : State) (ho : st.obsLive = false) (t : Tool) :
    ¬ Enabled (EmAdmit ⟨.M_EMCOUPLE, MaxRound⟩ t) st :=
  coupled_waits _ st ho (Or.inl rfl) t

/-- `MutEmCouple2Waits`: under `M_EMCOUPLE2`, from the seat's second round on, with no live Observer,
no emergency call can be admitted. -/
theorem MutEmCouple2Waits (MaxRound : Nat) (st : State) (hr : st.em.round ≥ 2)
    (ho : st.obsLive = false) (t : Tool) : ¬ Enabled (EmAdmit ⟨.M_EMCOUPLE2, MaxRound⟩ t) st :=
  coupled_waits _ st ho (Or.inr ⟨rfl, hr⟩) t

/-! ### The hypothesis is exact

Under a coupling mutation whose coupled round can be reached, `SpecL` reaches a state with the seat live in a
coupled round and the Observer down, and there both properties fail. The path is two approvals and an activation,
for `M_EMCOUPLE2` an end and the same three steps again, then the Observer's failure: steps of `NextL` and of `Next`
alike. -/

/-- From a reachable state with the seat not live, no approvals and a round below the bound, r1 and r2 approve and
the roster's quorum seats h for the next round: three steps of `NextL`. -/
theorem reachL_seat (c : Cfg) (st : State) (hr : Reachable Init (NextL c) st) (hl : st.em.live = false)
    (ha : st.approvals = ∅) (hb : st.em.round < c.MaxRound) :
    ∃ st', Reachable Init (NextL c) st' ∧ st'.em.live = true ∧ st'.em.round = st.em.round + 1 ∧
      st'.obsLive = st.obsLive ∧ st'.approvals = ∅ ∧ Tool.te ∈ st'.em.envelope := by
  have h1 := Reachable.step hr (Or.inr (Or.inl ⟨.r1, ⟨trivial, fun h => by rw [ha] at h; exact h⟩, rfl⟩) :
    NextL c st { st with approvals := st.approvals ∪ {.r1} })
  have h2 := Reachable.step h1 (Or.inr (Or.inl ⟨.r2, ⟨trivial, fun h => h.elim (fun h => by rw [ha] at h; exact h)
    (fun h => by cases h)⟩, rfl⟩) :
    NextL c { st with approvals := st.approvals ∪ {.r1} } { st with approvals := (st.approvals ∪ {.r1}) ∪ {.r2} })
  have hseat : Holder.h ∈ (if c.m = .M_AGENT then Holders else Persons) := by
    split
    · exact Or.inl rfl
    · exact rfl
  have h3 := Reachable.step h2 (Or.inr (Or.inr (Or.inl ⟨.h, Or.inl rfl, hl, hb,
    Or.inl ⟨.r1, .r2, Or.inl (Or.inr rfl), Or.inr rfl, by decide⟩, hseat, rfl⟩)))
  exact ⟨_, h3, rfl, rfl, rfl, rfl, Or.inr rfl⟩

/-- The initial state, reached. -/
theorem reachL_init (c : Cfg) : Reachable Init (NextL c) ⟨{.t1}, ∅, NoEm, {.t1}, true, ∅, false, ∅⟩ :=
  .init ⟨rfl, rfl, rfl, rfl, rfl, rfl, rfl, rfl⟩

/-- The Observer fails, or returns, in a reachable state. -/
theorem reachL_toggle (c : Cfg) (st : State) (hr : Reachable Init (NextL c) st) :
    Reachable Init (NextL c) { st with obsLive := !st.obsLive } :=
  .step hr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inl rfl)))))))

/-- Under `M_EMCOUPLE` with a round to seat, `SpecL` reaches the seat live in round one with the Observer down. -/
theorem coupled_reachable1 (c : Cfg) (hm : c.m = .M_EMCOUPLE) (hb : 1 ≤ c.MaxRound) :
    ∃ st, Reachable Init (NextL c) st ∧ st.em.live = true ∧ st.obsLive = false ∧ EmCoupled c st ∧
      Tool.te ∈ st.em.envelope := by
  obtain ⟨s1, h1, hl1, -, ho1, -, hte1⟩ := reachL_seat c _ (reachL_init c) rfl rfl hb
  exact ⟨_, reachL_toggle c s1 h1, hl1, by show (!s1.obsLive) = false; rw [ho1]; rfl, Or.inl hm, hte1⟩

/-- Under `M_EMCOUPLE2` with two rounds to seat, `SpecL` reaches the seat live in round two with the Observer down:
seated, ended, seated again. -/
theorem coupled_reachable2 (c : Cfg) (hm : c.m = .M_EMCOUPLE2) (hb : 2 ≤ c.MaxRound) :
    ∃ st, Reachable Init (NextL c) st ∧ st.em.live = true ∧ st.obsLive = false ∧ EmCoupled c st ∧
      Tool.te ∈ st.em.envelope := by
  obtain ⟨s1, h1, hl1, hr1, ho1, ha1, -⟩ := reachL_seat c _ (reachL_init c) rfl rfl (by show 0 < c.MaxRound; omega)
  have h2 := Reachable.step h1 (Or.inr (Or.inr (Or.inr (Or.inl ⟨hl1, rfl⟩))) :
    NextL c s1 { s1 with em := { s1.em with live := false } })
  obtain ⟨s3, h3, hl3, hr3, ho3, -, hte3⟩ :=
    reachL_seat c _ h2 rfl ha1 (by show s1.em.round < c.MaxRound; rw [hr1]; exact hb)
  have hr3 : s3.em.round = 2 := by rw [hr3]; show s1.em.round + 1 = 2; rw [hr1]; rfl
  exact ⟨_, reachL_toggle c s3 h3, hl3, by show (!s3.obsLive) = false; rw [ho3, ho1]; rfl,
    Or.inr ⟨hm, by show s3.em.round ≥ 2; rw [hr3]; exact Nat.le_refl 2⟩, hte3⟩

/-- In such a state both properties fail. -/
theorem coupled_blocks (c : Cfg) (st : State) (hl : st.em.live = true) (ho : st.obsLive = false)
    (hc : EmCoupled c st) (hte : Tool.te ∈ st.em.envelope) :
    ¬ EmergencyNeverCoupled c st ∧ ¬ EmergencyCallsWithoutObserver c st :=
  ⟨fun h => coupled_waits c st ho hc .te (h .te ⟨hl, hte⟩),
    fun h => let ⟨t, ht⟩ := h ⟨hl, ho⟩; coupled_waits c st ho hc t ht⟩

/-- A property that such a state breaks holds of every state `SpecL` reaches only if no coupled round can be
reached. -/
theorem noCoupledRound_needed (c : Cfg) (P : State → Prop)
    (hP : ∀ st, st.em.live = true → st.obsLive = false → EmCoupled c st → Tool.te ∈ st.em.envelope → ¬ P st)
    (h : ∀ st, Reachable Init (NextL c) st → P st) : NoCoupledRound c := by
  refine ⟨fun hm => ?_, fun hm => ?_⟩
  · by_cases h0 : c.MaxRound = 0
    · exact h0
    · obtain ⟨st, hr, hl, ho, hc, hte⟩ := coupled_reachable1 c hm (by omega)
      exact absurd (h st hr) (hP st hl ho hc hte)
  · by_cases h1 : c.MaxRound ≤ 1
    · exact h1
    · obtain ⟨st, hr, hl, ho, hc, hte⟩ := coupled_reachable2 c hm (by omega)
      exact absurd (h st hr) (hP st hl ho hc hte)

/-- `EmergencyNeverCoupled` holds of every state `Spec` reaches, and of every state `SpecL` reaches, exactly when
no coupled round can be reached. -/
theorem EmergencyNeverCoupledIff (c : Cfg) :
    ((∀ st, Reachable Init (Next c) st → EmergencyNeverCoupled c st) ↔ NoCoupledRound c) ∧
    ((∀ st, Reachable Init (NextL c) st → EmergencyNeverCoupled c st) ↔ NoCoupledRound c) :=
  ⟨⟨fun h => noCoupledRound_needed c _ (fun st hl ho hc hte => (coupled_blocks c st hl ho hc hte).1)
        (fun st hr => h st (reachL_reach c st hr)),
      fun hu => EmergencyNeverCoupledAlways c hu⟩,
    ⟨fun h => noCoupledRound_needed c _ (fun st hl ho hc hte => (coupled_blocks c st hl ho hc hte).1) h,
      fun hu st hr => EmergencyNeverCoupledAlways c hu st (reachL_reach c st hr)⟩⟩

/-- `EmergencyCallsWithoutObserver` holds of every state `Spec` reaches, and of every state `SpecL` reaches, exactly
when no coupled round can be reached. -/
theorem EmergencyCallsWithoutObserverIff (c : Cfg) :
    ((∀ st, Reachable Init (Next c) st → EmergencyCallsWithoutObserver c st) ↔ NoCoupledRound c) ∧
    ((∀ st, Reachable Init (NextL c) st → EmergencyCallsWithoutObserver c st) ↔ NoCoupledRound c) :=
  ⟨⟨fun h => noCoupledRound_needed c _ (fun st hl ho hc hte => (coupled_blocks c st hl ho hc hte).2)
        (fun st hr => h st (reachL_reach c st hr)),
      fun hu => EmergencyCallsWithoutObserverAlways c hu⟩,
    ⟨fun h => noCoupledRound_needed c _ (fun st hl ho hc hte => (coupled_blocks c st hl ho hc hte).2) h,
      fun hu st hr => EmergencyCallsWithoutObserverAlways c hu st (reachL_reach c st hr)⟩⟩

#print axioms LiveHasRoundAlways
#print axioms EmergencyLeaseHasARosterQuorumAlways
#print axioms EmergencyLeaseIsOneRoundAlways
#print axioms NoAgentHoldsAnEmergencySeatAlways
#print axioms CallsAreAllowlistedAlways
#print axioms ThinkerStillCoupledAlways
#print axioms ActivationIsForensicAlways
#print axioms SafeAlways
#print axioms UnobservedEmergencyCallEnabledAlways
#print axioms nextL_next
#print axioms SafeLAlways
#print axioms nextL_iff_next
#print axioms nextL_iff_next_needs_em
#print axioms reachL_iff
#print axioms EmergencyNeverCoupledValid
#print axioms EmergencyNeverCoupledAlways
#print axioms EmergencyCallsWithoutObserverAlways
#print axioms EmergencyNeverCoupledIff
#print axioms EmergencyCallsWithoutObserverIff

end Topak.Spec.Emergency
