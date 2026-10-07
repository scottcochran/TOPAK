/-
The genesis floor under Cedar's verified semantics. Depends on the Lean model AWS keeps in cedar-spec, at the tag
that matches the cedar-policy 4.13.0 the mechanism links (mechanism/Cargo.lock) and the cedar-policy-cli 4.13.0
the gate run records. The toolchain is cedar-lean's own (lean-toolchain), so its oleans are used as built.
-/
import Lake
open Lake DSL

require Cedar from git "https://github.com/cedar-policy/cedar-spec" @ "v4.13.0" / "cedar-lean"

package «topak-floor»

@[default_target]
lean_lib TopakFloor
