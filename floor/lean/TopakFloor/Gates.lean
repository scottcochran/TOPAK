import Cedar.Thm.Validation
import TopakFloor.Tests
/-!
# The genesis floor under Cedar's verified semantics

ADR-0030 §5's totality gate, closed in Lean. `floor/run-gates.py` runs `cedar symcc never-errors` for every
policy on every action it applies to, and on the genesis floor cedar decides each of those 23 checks by
folding the authorizer term, with no solver query: the run marks them `holds°`, and they rest on the engine's
row (ADR-0045 T-0045-3). Here the same claim is a theorem of cedar-spec's Lean model, which AWS proves
sound: `validation_is_sound` says that if the validator accepts a policy set against a schema, then on every
request and entity store the schema admits, every policy evaluates to a boolean or to one of three runtime
errors the validator cannot exclude. The floor validates (`floor_validates`, decided by evaluation), so the
theorem applies.

What is proved of the floor:
- `schema_wf`: schema S is well-formed under the model's `Schema.validateWellFormed`.
- `floor_validates`: the floor validates against S under the model's `validate`: every policy is boolean-typed
  in every environment and none is impossible.
- `floor_never_errors`: for every request and entity store that validate against S, every policy of the
  floor evaluates to a boolean, or to `entityDoesNotExist`, `extensionError` or `arithBoundsError`. The floor
  has no extension call and no arithmetic (`floor_no_ext_no_arith`, by inspection of the terms), so the
  residual is `entityDoesNotExist`: a request naming an entity the store lacks. That is a lift fault, §4.
- `genesis_tests`: the 62 behavioral cases of `genesis-tests.json`, each under the model's `isAuthorized`
  with the case's decision, determining policies and no errors (`Tests.lean`); and from them the witnesses
  the non-vacuity and discrimination gates need: for every action, a conforming request the floor refuses
  and one it admits.

What this rests on: the Lean kernel; the Lean model's fidelity to the Rust engine, which cedar-spec tests by
differential testing and which the symbolic compiler's own proof assumes too; cedar-policy-cli 4.13.0's parse
of the Cedar text into JSON, and `gen.py`'s walk of that JSON into the model's syntax; and `native_decide`,
which trusts Lean's compiler for the closed evaluations (one `*.native_decide.ax_1_1` axiom per use in
`#print axioms`; the kernel's `decide` cannot reduce the model's definitions).
-/

namespace TopakFloor
open Cedar.Spec Cedar.Validation Cedar.Thm Cedar.Data

/-- Schema S is well-formed. -/
theorem schema_wf : genesisSchema.validateWellFormed = .ok () :=
  schemaWellFormed_ok (by native_decide)

/-- The floor validates against S. -/
theorem floor_validates : validate genesisFloor genesisSchema = .ok () :=
  validates_ok (by native_decide)

/-- Totality (ADR-0030 §5): on every schema-conforming request and store, every policy of the floor evaluates
to a boolean or to a runtime error the validator cannot exclude. The 23 `holds°` rows of the gate run, as one
theorem of the verified model. -/
theorem floor_never_errors (request : Request) (entities : Entities)
    (hr : validateRequest genesisSchema request = .ok ())
    (he : validateEntities genesisSchema entities = .ok ()) :
    AllEvaluateToBool genesisFloor request entities :=
  validation_is_sound genesisFloor genesisSchema request entities schema_wf floor_validates hr he

/-- The per-policy reading of the gate row: each of the 17 policies, on any conforming input. -/
theorem policy_never_errors (p : Policy) (hp : p ∈ genesisFloor) (request : Request) (entities : Entities)
    (hr : validateRequest genesisSchema request = .ok ())
    (he : validateEntities genesisSchema entities = .ok ()) :
    ∃ b : Bool, EvaluatesTo p.toExpr request entities b :=
  floor_never_errors request entities hr he p hp

/-! The floor's text calls no extension function and does no arithmetic, so of the three errors the validator
cannot exclude only `entityDoesNotExist` can occur. Checked over the policies' expressions. -/
mutual
def noExtNoArith : Expr → Bool
  | .lit _ | .var _ => true
  | .ite a b c => noExtNoArith a && noExtNoArith b && noExtNoArith c
  | .and a b | .or a b => noExtNoArith a && noExtNoArith b
  | .unaryApp op a => (match op with | .neg => false | _ => true) && noExtNoArith a
  | .binaryApp op a b =>
    (match op with | .add | .sub | .mul => false | _ => true) && noExtNoArith a && noExtNoArith b
  | .getAttr a _ | .hasAttr a _ | .extHasAttr a _ _ => noExtNoArith a
  | .set xs => noExtNoArithList xs
  | .record m => noExtNoArithAttrs m
  | .call _ _ => false
def noExtNoArithList : List Expr → Bool
  | [] => true
  | x :: xs => noExtNoArith x && noExtNoArithList xs
def noExtNoArithAttrs : List (Attr × Expr) → Bool
  | [] => true
  | (_, x) :: xs => noExtNoArith x && noExtNoArithAttrs xs
end

theorem floor_no_ext_no_arith : genesisFloor.all (fun p => noExtNoArith p.toExpr) = true := by native_decide

/-! ## Witnesses: non-vacuity and discrimination

The 62 cases of `Tests.lean` are each a theorem under the model's authorizer. Here they are read as the gates
read them: for each of the ten actions, a schema-conforming request the floor refuses (non-vacuity: the floor
is not always-allows) and one it admits (discrimination: the floor is not always-denies). Each witness is a
case from `genesis-tests.json`, so its request validates against S and its store validates against S. -/

def actions : List String :=
  ["Read", "Draft", "Invoke", "Emit", "Submit", "Vote", "Consult", "Actuate", "Report", "Erase"]

/-- Every case's request validates against S, and the shared store validates against S. -/
theorem cases_conform :
    (caseRequests.all (fun r => match validateRequest genesisSchema r with | .ok () => true | .error _ => false)) = true ∧
    (match validateEntities genesisSchema genesisEntities with | .ok () => true | .error _ => false) = true := by
  constructor <;> native_decide

/-- Non-vacuity: for every action, some conforming case is denied. -/
theorem not_always_allows :
    actions.all (fun a => caseRequests.any (fun r =>
      r.action == act a && (isAuthorized r genesisEntities genesisFloor).decision == .deny)) = true := by
  native_decide

/-- Discrimination: for every action, some conforming case is allowed. `Erase` is the exception: at genesis
no erasure roster is issued, so `X2-erasure` admits nothing until bootstrap, and the cases say so. -/
theorem not_always_denies_but_erase :
    (actions.filter (· != "Erase")).all (fun a => caseRequests.any (fun r =>
      r.action == act a && (isAuthorized r genesisEntities genesisFloor).decision == .allow)) = true := by
  native_decide

#print axioms floor_never_errors
#print axioms floor_validates
#print axioms not_always_allows

end TopakFloor
