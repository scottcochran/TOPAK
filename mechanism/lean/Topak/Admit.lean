/-!
# The admit composition, transcribed and proved

`mechanism/crates/topak-core/src/admit.rs` (ADR-0030 §1) in Lean 4, with the properties that
`spec/FloorComposition.tla` states proved of the transcription rather than of a model. TLAPS proves
them of the TLA+ module (`spec/FloorComposition_proof.tla`). This file proves them of the code's
composition: the step from module to code that ADR-0045 T-0045-28 says the corpus lacks.

What is proved is of the transcription. Its fidelity to `admit.rs` is read, not checked: no
Rust-to-Lean translator was run. Each definition carries the Rust it transcribes in its doc-comment,
so a reader can compare the two without leaving the file.

Core Lean only, no Mathlib. `#print axioms` at the end: no theorem depends on more than `propext`
and `Quot.sound`, Lean's own; none on `Classical.choice`, none on `sorry`.
-/

namespace Topak.Admit

/-- `BundleEngine` (`state.rs`): which bundle engine answered.

```rust
pub enum BundleEngine { Sidecar, LocalWasm }
``` -/
inductive BundleEngine where
  | sidecar
  | localWasm
  deriving DecidableEq, Repr, Inhabited

/-- `Digest` (`types.rs`): lowercase hex SHA-256 as a string. The composition carries one and never reads it.

```rust
pub struct Digest(pub String);
``` -/
structure Digest where
  hex : String
  deriving DecidableEq, Repr, Inhabited

/-- `MechanismDeny` (`state.rs`): a deny the mechanism decides before the floor is asked. Opaque here:
`compose` neither produces nor inspects one (`compose_deny_reasons`). -/
opaque MechanismDeny : Type

/-- ```rust
pub enum FloorOutcome {
    /// Allow with an empty error list. `reasons` are the permitting policy ids.
    Permit { reasons: Vec<String> },
    Deny { reasons: Vec<String> },
    /// Any evaluation error or input-validation failure, whatever the engine decided.
    Error { diagnostics: Vec<String> },
}
``` -/
inductive FloorOutcome where
  | permit (reasons : List String)
  | deny (reasons : List String)
  | error (diagnostics : List String)
  deriving DecidableEq, Repr

/-- ```rust
pub enum BundleOutcome {
    /// An affirmative `allow` from the bundle version the lease names.
    Allow { engine: BundleEngine, bundle: Digest },
    /// Anything else.
    Refuse { engine: Option<BundleEngine>, reason: String },
}
``` -/
inductive BundleOutcome where
  | allow (engine : BundleEngine) (bundle : Digest)
  | refuse (engine : Option BundleEngine) (reason : String)
  deriving DecidableEq, Repr

/-- ```rust
pub enum DenyReason {
    Mechanism(MechanismDeny),
    /// The floor denied because these forbids fired.
    Floor(Vec<String>),
    /// The floor denied because no permit matched: the request is outside every envelope.
    FloorNoPermit,
    FloorError(Vec<String>),
    Bundle(String),
    /// The admit was decided but voided at apply time, or never committed.
    NotCommitted(String),
}
``` -/
inductive DenyReason where
  | mechanism (d : MechanismDeny)
  | floor (reasons : List String)
  | floorNoPermit
  | floorError (diagnostics : List String)
  | bundle (reason : String)
  | notCommitted (why : String)

/-- ```rust
pub enum Decision {
    Admit { floor_reasons: Vec<String>, engine: BundleEngine, bundle: Digest },
    Deny(DenyReason),
}
``` -/
inductive Decision where
  | admit (floorReasons : List String) (engine : BundleEngine) (bundle : Digest)
  | deny (reason : DenyReason)

/-- Needed only so that `compose` can state the Rust `unreachable!` as `panic!`. -/
instance : Inhabited Decision := ⟨.deny .floorNoPermit⟩

/-! ## The code -/

/-- The floor half of the composition. `some deny` means stop: do not consult the bundle.

```rust
pub fn floor_gate(floor: &FloorOutcome) -> Option<DenyReason> {
    match floor {
        FloorOutcome::Permit { .. } => None,
        FloorOutcome::Deny { reasons } if reasons.is_empty() => Some(DenyReason::FloorNoPermit),
        FloorOutcome::Deny { reasons } => Some(DenyReason::Floor(reasons.clone())),
        FloorOutcome::Error { diagnostics } => Some(DenyReason::FloorError(diagnostics.clone())),
    }
}
``` -/
def floorGate (floor : FloorOutcome) : Option DenyReason :=
  match floor with
  | .permit _ => none
  | .deny reasons => if reasons.isEmpty then some .floorNoPermit else some (.floor reasons)
  | .error diagnostics => some (.floorError diagnostics)

/-- The whole composition. A bundle allow never admits what the floor did not permit.

```rust
pub fn compose(floor: &FloorOutcome, bundle: &BundleOutcome) -> Decision {
    if let Some(d) = floor_gate(floor) {
        return Decision::Deny(d);
    }
    let FloorOutcome::Permit { reasons } = floor else { unreachable!("floor_gate") };
    match bundle {
        BundleOutcome::Allow { engine, bundle } => {
            Decision::Admit { floor_reasons: reasons.clone(), engine: *engine, bundle: bundle.clone() }
        }
        BundleOutcome::Refuse { reason, .. } => Decision::Deny(DenyReason::Bundle(reason.clone())),
    }
}
```
The `unreachable!` is the `panic!` arm; `floorGate_none_iff` is why it is unreachable. -/
def compose (floor : FloorOutcome) (bundle : BundleOutcome) : Decision :=
  match floorGate floor with
  | some d => .deny d
  | none =>
    match floor with
    | .permit reasons =>
      match bundle with
      | .allow engine bundle => .admit reasons engine bundle
      | .refuse _ reason => .deny (.bundle reason)
    | _ => panic! "floor_gate"

/-- The call site, `topak-node/src/mechanism.rs` steps 5 and 6: the gate first, and the bundle is
consulted only when the gate passes. `consult` stands for the bundle engine's answer, asked for only
in the second arm.

```rust
let floor_out = self.floor.decide(&frozen);
if let Some(d) = floor_gate(&floor_out) {
    return deny(d);
}
let bundle_out = self.bundle.decide(&lease_bundle, &frozen.bundle_input).await;
let Decision::Admit { floor_reasons, engine, bundle } = compose(&floor_out, &bundle_out) else {
    let Decision::Deny(d) = compose(&floor_out, &bundle_out) else { unreachable!() };
    return deny(d);
};
``` -/
def callSite (floor : FloorOutcome) (consult : Unit → BundleOutcome) : Decision :=
  match floorGate floor with
  | some d => .deny d
  | none => compose floor (consult ())

/-! ## ADR-0030 §1 as the code states it

`floor_permit`, `bundle_deny` and `admit` as predicates on the code's values. These are the
abstraction under which `FloorComposition.tla` speaks: its `FloorPermit` is "Allow with no evaluation
errors", which the engine wrapper has already folded into `FloorOutcome.permit`; its `BundleDeny(b)`
is `b # "allow"`, which is `BundleOutcome.refuse`. -/

/-- The floor returned Allow with no evaluation errors. -/
def floorPermit : FloorOutcome → Bool
  | .permit _ => true
  | .deny _ => false
  | .error _ => false

/-- Anything but an affirmative allow. -/
def bundleDeny : BundleOutcome → Bool
  | .allow _ _ => false
  | .refuse _ _ => true

def isAdmit : Decision → Bool
  | .admit _ _ _ => true
  | .deny _ => false

/-- `Admit(e, p, a, b) == FloorPermit(e, p, a) /\ ~BundleDeny(b)` (`FloorComposition.tla`, Mut = "none"),
with its two arguments already abstracted to Booleans. -/
def tlaAdmit (floorPermit bundleDeny : Bool) : Bool :=
  floorPermit && !bundleDeny

/-! ## The gate -/

/-- The gate passes exactly the permits, so the `unreachable!` in `compose` is unreachable. -/
theorem floorGate_none_iff (f : FloorOutcome) : floorGate f = none ↔ ∃ rs, f = .permit rs := by
  cases f <;> simp [floorGate]
  split <;> simp

/-- The gate's two deny shapes, as the Rust `match` arms state them. -/
theorem floorGate_deny (rs : List String) :
    floorGate (.deny rs) = some (if rs.isEmpty then .floorNoPermit else .floor rs) := by
  by_cases hr : rs.isEmpty <;> simp [floorGate, hr]

theorem floorGate_error (ds : List String) : floorGate (.error ds) = some (.floorError ds) := rfl

/-- ADR-0030 §1 R4 (ADR-0033 finding 10): every floor deny names its reason. A deny with no
determining forbid is `floorNoPermit`; `floor []` is never produced. -/
theorem floor_deny_names_a_reason (f : FloorOutcome) (rs : List String) :
    floorGate f = some (.floor rs) → rs ≠ [] := by
  intro h
  cases f with
  | permit _ => simp [floorGate] at h
  | error _ => simp [floorGate] at h
  | deny rs' =>
    rw [floorGate_deny] at h
    by_cases hr : rs'.isEmpty
    · simp [hr] at h
    · simp [hr] at h; subst h; simpa using hr

/-- The gate short-circuits: when it denies, `compose` returns that deny whatever the bundle says.
This is `M_OVERRIDE` refused at the code: a bundle allow cannot move a floor deny. -/
theorem gate_short_circuits (f : FloorOutcome) (d : DenyReason) (b : BundleOutcome) :
    floorGate f = some d → compose f b = .deny d := by
  intro h; unfold compose; rw [h]

/-- The node's call site is `compose`. Its own gate check adds nothing the composition does not do. -/
theorem callSite_eq_compose (f : FloorOutcome) (b : BundleOutcome) :
    callSite f (fun _ => b) = compose f b := by
  unfold callSite
  split
  · exact (gate_short_circuits f _ b ‹_›).symm
  · rfl

/-! ## `compose`, one equation per Rust arm -/

@[simp] theorem compose_permit_allow (rs : List String) (e : BundleEngine) (d : Digest) :
    compose (.permit rs) (.allow e d) = .admit rs e d := rfl

@[simp] theorem compose_permit_refuse (rs : List String) (e : Option BundleEngine) (r : String) :
    compose (.permit rs) (.refuse e r) = .deny (.bundle r) := rfl

@[simp] theorem compose_deny (rs : List String) (b : BundleOutcome) :
    compose (.deny rs) b = .deny (if rs.isEmpty then .floorNoPermit else .floor rs) :=
  gate_short_circuits _ _ _ (floorGate_deny rs)

@[simp] theorem compose_error (ds : List String) (b : BundleOutcome) :
    compose (.error ds) b = .deny (.floorError ds) := rfl

/-! ## The five properties, of the code

`BundleCannotWriteFloorInputs` and `EnvelopeHolds` are about the lift and the store, which this
function never touches: its inputs are the engines' outcomes, already evaluated. What the code can
state is the other three, and the shape of every decision. -/

/-- What an admit witnesses: the floor permitted, and the admit carries exactly its reasons; the bundle
affirmatively allowed, and the admit carries exactly its engine and digest. Everything below about
admits is a corollary. -/
theorem admit_witnesses (f : FloorOutcome) (b : BundleOutcome)
    (rs : List String) (e : BundleEngine) (d : Digest) :
    compose f b = .admit rs e d → f = .permit rs ∧ b = .allow e d := by
  cases f <;> cases b <;> simp

/-- `AdmitImpliesFloorPermit` (ADR-0030 §1): no admit without a floor permit. -/
theorem admit_implies_floor_permit (f : FloorOutcome) (b : BundleOutcome)
    (rs : List String) (e : BundleEngine) (d : Digest) :
    compose f b = .admit rs e d → floorPermit f = true := by
  intro h; rw [(admit_witnesses f b rs e d h).1]; rfl

/-- `FloorErrorIsDeny` (ADR-0030 §1): a floor evaluation error is a deny, whatever the engine decided
and whatever the bundle said. `M_ERR` refused at the code. -/
theorem floor_error_is_deny (ds : List String) (b : BundleOutcome) :
    compose (.error ds) b = .deny (.floorError ds) := compose_error ds b

/-- `BundleRefusalHonored` (ADR-0030 §1): an admit needs an affirmative bundle allow, so a deny, an
error, an undefined, an absent or an unreachable bundle, all `refuse` here, never admit.
`M_FAILOPEN` refused at the code. -/
theorem bundle_refusal_honored (f : FloorOutcome) (b : BundleOutcome)
    (rs : List String) (e : BundleEngine) (d : Digest) :
    compose f b = .admit rs e d → bundleDeny b = false := by
  intro h; rw [(admit_witnesses f b rs e d h).2]; rfl

/-- The same, in the shape the Rust test states it: a bundle refusal on a floor permit is a deny that
names the bundle's reason. -/
theorem bundle_refusal_is_deny (rs : List String) (e : Option BundleEngine) (reason : String) :
    compose (.permit rs) (.refuse e reason) = .deny (.bundle reason) := compose_permit_refuse rs e reason

/-- Reachability (`NeverAdmitted` must be violated): a permit and an allow admit. -/
theorem permit_and_allow_admit (rs : List String) (e : BundleEngine) (d : Digest) :
    compose (.permit rs) (.allow e d) = .admit rs e d := compose_permit_allow rs e d

/-- **admit ⟺ floor_permit ∧ ¬bundle_deny** (ADR-0030 §1). The code's decision is the module's `Admit`
at Mut = "none", applied to the abstraction of the code's inputs. This is the refinement statement
for the composition: `FloorComposition.tla` quantifies over every bundle outcome and every floor
outcome, and the code agrees with it at each one. -/
theorem admit_iff (f : FloorOutcome) (b : BundleOutcome) :
    isAdmit (compose f b) = tlaAdmit (floorPermit f) (bundleDeny b) := by
  cases f <;> cases b <;> simp [isAdmit, tlaAdmit, floorPermit, bundleDeny]

/-- Every deny the composition returns is the floor's or the bundle's, and a floor deny is never an
empty `floor` list. `mechanism` and `notCommitted` are decided before and after the composition. -/
theorem compose_deny_reasons (f : FloorOutcome) (b : BundleOutcome) (d : DenyReason) :
    compose f b = .deny d →
      (∃ rs, d = .floor rs ∧ rs ≠ []) ∨ d = .floorNoPermit ∨
      (∃ ds, d = .floorError ds) ∨ (∃ r, d = .bundle r) := by
  intro h
  cases f with
  | permit rs => cases b <;> simp at h <;> subst h <;> simp
  | error ds => simp at h; subst h; simp
  | deny rs =>
    simp at h; subst h
    by_cases hr : rs = [] <;> simp [hr]

/-! ## The Rust tests, as instances

`crates/topak-core/tests/mutations.rs`, the two `FloorComposition.tla` tests and the R4 test. Each
assertion there is one point of a theorem above; `rfl` evaluates the transcription at that point. -/

example : compose (.permit ["B1"]) (.allow .localWasm ⟨"b"⟩) = .admit ["B1"] .localWasm ⟨"b"⟩ := rfl
example : compose (.deny []) (.allow .localWasm ⟨"b"⟩) = .deny .floorNoPermit := rfl
example : compose (.error ["skipped forbid"]) (.allow .localWasm ⟨"b"⟩)
    = .deny (.floorError ["skipped forbid"]) := rfl
example : compose (.permit ["B1"]) (.refuse none "unreachable") = .deny (.bundle "unreachable") := rfl
example : floorGate (.deny []) = some .floorNoPermit := rfl
example : floorGate (.deny ["B7-author-recused"]) = some (.floor ["B7-author-recused"]) := rfl
example : floorGate (.permit []) = none := rfl

/-! ## What the proofs rest on -/

#print axioms floorGate_none_iff
#print axioms floor_deny_names_a_reason
#print axioms gate_short_circuits
#print axioms callSite_eq_compose
#print axioms admit_witnesses
#print axioms admit_implies_floor_permit
#print axioms floor_error_is_deny
#print axioms bundle_refusal_honored
#print axioms bundle_refusal_is_deny
#print axioms permit_and_allow_admit
#print axioms admit_iff
#print axioms compose_deny_reasons

end Topak.Admit
