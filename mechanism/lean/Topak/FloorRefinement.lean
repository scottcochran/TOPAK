import Topak.Admit
import TopakSpec.FloorComposition
/-!
# The code's decision refines `FloorComposition.tla`'s `Decide`

`spec/lean/TopakSpec/FloorComposition.lean` re-encodes `FloorComposition.tla` and proves its five invariants.
`Admit.lean` transcribes `compose` and `floor_gate`. This file transcribes the third piece, the `topak-floor` wrapper
that turns the Cedar engine's response into a `FloorOutcome`, and proves that **the code's decision, the wrapper and
`compose` together, is a `Decide` step of the module** (`codeDecide_refines`). So every behaviour in which the lift
moves the store as the module's lift does and the code decides is a behaviour of the module, and the module's five
invariants hold of it (`code_behaviours_safe`).

**What is premised, not proved.**
- **The engine (T-0045-3).** `authorize` states Cedar's authorization rule as cedar-spec defines `isAuthorized`
  (`Cedar/Spec/Authorizer.lean`): deny on any satisfied forbid, else allow on any satisfied permit, else deny; the
  erroring policies reported apart; the determining policies the permits on allow and the forbids on deny.
  `EngineFaithful` says the Rust engine either rejects the input before evaluating it (an entity id, the context, the
  request or the entities fail against S) or returns that rule's response over the module's four policies evaluated
  on the slice. That is T-0045-3's own premise, the engine faithful to the Lean model, at the size of this module.
- **The floor is the module's.** `floorResults` is the module's P1 to P3 and F1. The floor in force has 28 policies;
  this is a refinement of the module, not of the floor in force.
- **The lift.** The code's lift is not transcribed. `CodeNext` takes the module's own `Reassign` and `Seal` as the
  lift's steps, which is what `BundleCannotWriteFloorInputs` needs: the floor's store moves only with the truth.
- **The transcriptions**, each read beside the Rust it states, as in `Admit.lean`.
-/

namespace Topak.FloorRefinement
open Topak.Admit Topak.Spec
open Topak.Spec.FloorComposition (State Rec Seat Act Target BOut Res Drop Dropped OwnerIs SealedIs
  EngineAllow EngineErr FloorPermit BundleDeny Permits Forbids decided Decide Next Init Safe Reassign Seal SafeAlways)
open Topak.Spec.FloorComposition renaming Admit → fcAdmit

/-! ## The engine's response, and the wrapper -/

/-- `cedar_policy::Decision` -/
inductive CedarDecision | allow | deny
  deriving DecidableEq

/-- The parts of `cedar_policy::Response` the wrapper reads: `decision()`, `diagnostics().errors()` rendered, and
`diagnostics().reason()`, the determining policies' ids. -/
structure Response where
  decision : CedarDecision
  errors : List String
  reason : List String

/-- `Floor::decide` and `Floor::evaluate` (`crates/topak-floor/src/lib.rs`), from the point the inputs are parsed:
`.error ds` when an entity id, the context, the request or the entities fail to parse or validate against S, `.ok
resp` the authorizer's response. `ids` is the floor's map from Cedar's policy ids to the `@id` annotations.

```rust
let response = Authorizer::new().is_authorized(&request, &self.policies, &entities);
let diagnostics: Vec<String> = response.diagnostics().errors().map(|e| e.to_string()).collect();
if !diagnostics.is_empty() {
    // Cedar skipped the erroring policy; a skipped forbid must not let a permit through.
    return FloorOutcome::Error { diagnostics };
}
let reasons: Vec<String> = response.diagnostics().reason()
    .map(|id| self.ids.get(id).cloned().unwrap_or_else(|| id.to_string())).collect();
match response.decision() {
    Decision::Allow => FloorOutcome::Permit { reasons },
    Decision::Deny => FloorOutcome::Deny { reasons },
}
```
and, before it, each of the four input failures `return FloorOutcome::Error { diagnostics }`. -/
def floorOutcome (ids : String → Option String) : Except (List String) Response → FloorOutcome
  | .error ds => .error ds
  | .ok resp =>
    if !resp.errors.isEmpty then .error resp.errors
    else
      let reasons := resp.reason.map (fun id => (ids id).getD id)
      match resp.decision with
      | .allow => .permit reasons
      | .deny => .deny reasons

/-! ## Cedar's authorization rule, over a floor's evaluated policies (T-0045-3) -/

inductive Effect | permit | forbid
  deriving DecidableEq

/-- One policy evaluated against a request: its id, its effect, and whether it was satisfied ("T"), not ("F"), or
errored ("ERR"), as the module evaluates P1 to P3 and F1. -/
structure PolicyResult where
  id : String
  effect : Effect
  res : Res

/-- cedar-spec's `isAuthorized`, over evaluated policies. -/
def authorize (rs : List PolicyResult) : Response :=
  let forbids := (rs.filter (fun r => r.effect == .forbid && r.res == .T)).map (·.id)
  let permits := (rs.filter (fun r => r.effect == .permit && r.res == .T)).map (·.id)
  let errs := (rs.filter (fun r => r.res == .ERR)).map (·.id)
  if forbids.isEmpty && !permits.isEmpty then ⟨.allow, errs, permits⟩ else ⟨.deny, errs, forbids⟩

/-- The module's floor, P1 to P3 and F1, evaluated on slice `e` for seat `p` and act `a`: `Permits(e, p, a)` and
`Forbids(e, a)` with their ids. -/
def floorResults (e : Rec) (p : Seat) (a : Act) : List PolicyResult :=
  [⟨"P1", .permit, if a = .Read then .T else .F⟩,
   ⟨"P2", .permit, if a = .Draft then OwnerIs e p else .F⟩,
   ⟨"P3", .permit, if a = .Emit then OwnerIs e p else .F⟩,
   ⟨"F1", .forbid, if a = .Emit then SealedIs e else .F⟩]

/-- T-0045-3 at the size of this module: the engine rejects the input, or answers by Cedar's rule over the floor. -/
def EngineFaithful (e : Rec) (p : Seat) (a : Act) (resp : Except (List String) Response) : Prop :=
  (∃ ds, resp = .error ds) ∨ resp = .ok (authorize (floorResults e p a))

/-! ## The wrapper, proved -/

/-- An input that fails before evaluation is an `Error`, so a deny. -/
theorem input_failure_is_error (ids : String → Option String) (ds : List String) :
    floorOutcome ids (.error ds) = .error ds := rfl

/-- Any error diagnostic is an `Error`, whatever Cedar decided: a skipped forbid cannot let a permit through. -/
theorem engine_error_is_error (ids : String → Option String) (resp : Response) (h : resp.errors ≠ []) :
    floorOutcome ids (.ok resp) = .error resp.errors := by
  cases hr : resp.errors with
  | nil => exact absurd hr h
  | cons x xs => simp [floorOutcome, hr]

/-- The wrapper permits exactly when Cedar allows with no error. -/
theorem wrapper_permit_iff (ids : String → Option String) (resp : Response) :
    floorPermit (floorOutcome ids (.ok resp)) = true ↔ resp.decision = .allow ∧ resp.errors = [] := by
  cases hr : resp.errors <;> cases hd : resp.decision <;> simp [floorOutcome, floorPermit, hr, hd]

/-- ADR-0030 §1 R4 through the wrapper: on Cedar's rule with no error, a deny's reasons are the satisfied forbids, so
a deny names no reason exactly when no forbid was satisfied, and `floor_gate` then reports `FloorNoPermit`. -/
theorem wrapper_deny_reasons (ids : String → Option String) (rs : List PolicyResult)
    (hne : (authorize rs).errors = []) (reasons : List String)
    (h : floorOutcome ids (.ok (authorize rs)) = .deny reasons) :
    reasons = ((rs.filter (fun r => r.effect == .forbid && r.res == .T)).map (·.id)).map (fun id => (ids id).getD id) := by
  have key : ∀ resp : Response, resp.errors = [] → floorOutcome ids (.ok resp) = .deny reasons →
      resp.decision = .deny ∧ reasons = resp.reason.map (fun id => (ids id).getD id) := by
    intro resp he hd
    cases hdec : resp.decision <;> simp [floorOutcome, he, hdec] at hd ⊢
    exact hd.symm
  obtain ⟨hdeny, hr⟩ := key _ hne h
  rw [hr]
  unfold authorize at hdeny ⊢
  dsimp only at hdeny ⊢
  split <;> simp_all

/-! ## The abstraction, and the floor half refined -/

/-- The module's `Permits` and `Forbids`, read as Cedar reads the floor. -/
theorem engine_allow_iff (e : Rec) (p : Seat) (a : Act) :
    (authorize (floorResults e p a)).decision = .allow ↔ EngineAllow e p a := by
  unfold EngineAllow Permits Forbids floorResults
  generalize OwnerIs e p = o
  generalize SealedIs e = s
  cases a <;> cases o <;> cases s <;> simp [authorize]

theorem engine_err_iff (e : Rec) (p : Seat) (a : Act) :
    (authorize (floorResults e p a)).errors ≠ [] ↔ EngineErr e p a := by
  unfold EngineErr Permits Forbids floorResults
  generalize OwnerIs e p = o
  generalize SealedIs e = s
  cases a <;> cases o <;> cases s <;> simp [authorize]

/-- **The floor half refines `FloorPermit`**: the wrapper's permit, on the engine's answer for the module's floor,
is the module's `FloorPermit` at `Mut = "none"`. -/
theorem floorPermit_refines (ids : String → Option String) (e : Rec) (p : Seat) (a : Act) :
    floorPermit (floorOutcome ids (.ok (authorize (floorResults e p a)))) = true ↔ FloorPermit .none e p a := by
  rw [wrapper_permit_iff]
  unfold FloorPermit
  rw [if_neg (by decide), ← engine_allow_iff, ← engine_err_iff]
  simp

/-- The code's bundle outcome as the module's: an affirmative allow, or a refusal, which the module writes as any of
five outcomes and which `BundleDeny` treats alike at `Mut = "none"`. -/
def bundleAbs : BundleOutcome → BOut
  | .allow _ _ => .allow
  | .refuse _ _ => .deny

/-- The code admits: the wrapper's outcome composed with the bundle's (`compose`, and the node's call site, which
`callSite_eq_compose` shows is `compose`). -/
def codeAdmits (ids : String → Option String) (resp : Except (List String) Response) (b : BundleOutcome) : Prop :=
  isAdmit (compose (floorOutcome ids resp) b) = true

/-- **The decision refines `Admit`**: on the engine's answer, the code admits exactly when the module's `Admit` does at
`Mut = "none"`, for every slice, seat, act and bundle outcome. -/
theorem codeAdmits_iff (ids : String → Option String) (e : Rec) (p : Seat) (a : Act) (b : BundleOutcome) :
    codeAdmits ids (.ok (authorize (floorResults e p a))) b ↔ fcAdmit .none e p a (bundleAbs b) := by
  unfold codeAdmits
  rw [admit_iff]
  unfold tlaAdmit fcAdmit BundleDeny
  rw [if_neg (by decide), if_neg (by decide), ← floorPermit_refines ids]
  cases b <;> simp [bundleDeny, bundleAbs]

/-- An input rejected before evaluation is never admitted. -/
theorem codeAdmits_input_failure (ids : String → Option String) (ds : List String) (b : BundleOutcome) :
    ¬ codeAdmits ids (.error ds) b := by
  unfold codeAdmits; cases b <;> simp [compose, floorGate, floorOutcome, isAdmit]

/-- The module never admits on a refusal at `Mut = "none"`. -/
theorem fcAdmit_deny (e : Rec) (p : Seat) (a : Act) : ¬ fcAdmit .none e p a .deny := by
  unfold fcAdmit BundleDeny; rw [if_neg (by decide), if_neg (by decide)]; intro h; exact h.2 (by decide)

/-! ## The step refinement -/

/-- A decision as the code takes it, at `(p, a, r)`: the slice is the store's entry with at most one attribute
dropped (the module's §4 fault), the engine answers faithfully, the bundle answers anything, and the flags record the
code's admit. -/
def CodeDecide (ids : String → Option String) (st st' : State) : Prop :=
  ∃ (p : Seat) (a : Act) (r : Target) (d : Drop) (resp : Except (List String) Response) (b : BundleOutcome),
    EngineFaithful (Dropped (st.fstore r) d) p a resp ∧
    st' = decided st .none (Dropped (st.fstore r) d) p a r (bundleAbs b) (codeAdmits ids resp b)

/-- **`codeDecide_refines`: every code decision is a `Decide` step of the module**, at `Mut = "none"`. On an input
rejected before evaluation the witness is the module's refusal; otherwise it is the code's own bundle outcome. -/
theorem codeDecide_refines (ids : String → Option String) (st st' : State) (h : CodeDecide ids st st') :
    Next .none st st' := by
  obtain ⟨p, a, r, d, resp, b, hf, rfl⟩ := h
  refine Or.inr (Or.inr ⟨p, a, r, ?_⟩)
  rcases hf with ⟨ds, rfl⟩ | rfl
  · -- rejected before evaluation: no admit, as the module's refusal
    refine ⟨.deny, d, ?_⟩
    have h1 : codeAdmits ids (.error ds) b = False := propext ⟨codeAdmits_input_failure ids ds b, False.elim⟩
    have h2 : fcAdmit .none (Dropped (st.fstore r) d) p a .deny = False :=
      propext ⟨fcAdmit_deny _ p a, False.elim⟩
    rw [h1, h2]
    have h3 : (False ∧ bundleAbs b ≠ .allow) = (False ∧ BOut.deny ≠ .allow) :=
      propext ⟨fun h => h.1.elim, fun h => h.1.elim⟩
    unfold decided
    rw [h3]
  · -- answered by Cedar's rule: the code's admit is the module's Admit on the code's bundle outcome
    refine ⟨bundleAbs b, d, ?_⟩
    rw [propext (codeAdmits_iff ids _ p a b)]

/-- The behaviours the code produces: the module's lift, and the code's decisions. -/
def CodeNext (ids : String → Option String) (st st' : State) : Prop :=
  (∃ t s, Reassign t s st st') ∨ (∃ t, Seal t st st') ∨ CodeDecide ids st st'

theorem codeNext_refines (ids : String → Option String) (st st' : State) (h : CodeNext ids st st') :
    Next .none st st' := by
  rcases h with ⟨t, s, h⟩ | ⟨t, h⟩ | h
  · exact Or.inl ⟨t, s, Or.inl h⟩
  · exact Or.inr (Or.inl ⟨t, h⟩)
  · exact codeDecide_refines ids st st' h

/-- **`code_behaviours_safe`**: every state reached by the module's lift and the code's decisions keeps all five of
`FloorComposition.tla`'s invariants: `AdmitImpliesFloorPermit`, `FloorErrorIsDeny`, `BundleRefusalHonored`,
`BundleCannotWriteFloorInputs` and `EnvelopeHolds`, proved of the module in `spec/lean`. -/
theorem code_behaviours_safe (ids : String → Option String) :
    ∀ st, Reachable Init (CodeNext ids) st → Safe st :=
  fun st h => SafeAlways st (Reachable.mono (codeNext_refines ids) st h)

/-- And the code can take every decision the module can: each `Decide` step at `Mut = "none"` is a code decision,
with the engine answering and the bundle allowing or refusing as the module's outcome says. -/
theorem decide_is_code (ids : String → Option String) (st st' : State) (p : Seat) (a : Act) (r : Target)
    (h : Decide .none p a r st st') : CodeDecide ids st st' := by
  obtain ⟨b, d, rfl⟩ := h
  let bc : BundleOutcome := if b = .allow then .allow .localWasm ⟨""⟩ else .refuse none ""
  refine ⟨p, a, r, d, .ok (authorize (floorResults (Dropped (st.fstore r) d) p a)), bc, Or.inr rfl, ?_⟩
  rw [propext (codeAdmits_iff ids _ p a bc)]
  by_cases hb : b = .allow
  · subst hb; rfl
  · have hbc : bundleAbs bc = .deny := by simp [bc, hb, bundleAbs]
    rw [hbc]
    have e1 : fcAdmit .none (Dropped (st.fstore r) d) p a b = fcAdmit .none (Dropped (st.fstore r) d) p a .deny := by
      unfold fcAdmit BundleDeny; rw [if_neg (by decide), if_neg (by decide), if_neg (by decide)]
      simp [hb]
    rw [e1]
    have h3 : (fcAdmit .none (Dropped (st.fstore r) d) p a .deny ∧ b ≠ .allow) =
        (fcAdmit .none (Dropped (st.fstore r) d) p a .deny ∧ BOut.deny ≠ .allow) :=
      propext ⟨fun h => ⟨h.1, by decide⟩, fun h => ⟨h.1, hb⟩⟩
    unfold decided
    rw [h3]

#print axioms wrapper_permit_iff
#print axioms floorPermit_refines
#print axioms codeAdmits_iff
#print axioms codeDecide_refines
#print axioms code_behaviours_safe
#print axioms decide_is_code

end Topak.FloorRefinement
