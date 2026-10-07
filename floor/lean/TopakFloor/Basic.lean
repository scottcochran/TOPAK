import Cedar.Spec
import Cedar.Validation
/-!
Helpers for stating the genesis floor in the Lean model's abstract syntax. Nothing here is proved; these
are constructors, named so the generated `Genesis.lean` and `Tests.lean` read like the Cedar they transcribe.
-/
namespace TopakFloor
open Cedar.Spec Cedar.Validation Cedar.Data

/-- `Topak::Seat` is `ety ["Topak"] "Seat"`. -/
def ety (path : List String) (id : String) : EntityType := ⟨id, path⟩
/-- `Topak::Seat::"a1"` -/
def uid (path : List String) (id eid : String) : EntityUID := ⟨ety path id, eid⟩
/-- `Topak::Action::"Read"` -/
def act (name : String) : EntityUID := uid ["Topak"] "Action" name

/-- A Cedar `Long` literal, in the model's checked 64-bit integers. -/
def long (i : Int) : Value := .prim (.int (Int64.ofInt i))

/-- `validate` as a Bool, so the kernel or the compiler can decide it. -/
def validates (ps : Policies) (s : Schema) : Bool :=
  match validate ps s with
  | .ok () => true
  | .error _ => false

theorem validates_ok {ps : Policies} {s : Schema} (h : validates ps s = true) : validate ps s = .ok () := by
  unfold validates at h
  split at h
  · rename_i heq; exact heq
  · cases h

def schemaWellFormed (s : Schema) : Bool :=
  match s.validateWellFormed with
  | .ok () => true
  | .error _ => false

theorem schemaWellFormed_ok {s : Schema} (h : schemaWellFormed s = true) : s.validateWellFormed = .ok () := by
  unfold schemaWellFormed at h
  split at h
  · rename_i heq; exact heq
  · cases h

end TopakFloor
