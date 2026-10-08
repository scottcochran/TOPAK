import TopakSpec.Prelude
/-!
# Temporal: the TLA+ beyond `[]P` that the encodings need

`Prelude.lean` gives `Spec => []P` as an induction on reachable states. This file gives the temporal vocabulary
beyond `[]P` that an encoding states its properties in. For now that is `ENABLED`, which an availability invariant
("X cannot block Y") asks of an action in every reachable state; such an invariant is still a `[]P`, proved by
`invariant`. Behaviours, weak and strong fairness and leads-to are not here: they come with the leads-to proofs, the
liveness plan's next step, and nothing in this file assumes them.
-/

namespace Topak.Spec

/-- `ENABLED A`: at the state `s`, the action `A` has a successor. In TLA+, `ENABLED A` holds at a state when some
state `s'` makes the pair `(s, s')` an `A` step. Nothing is added for stuttering: `ENABLED` is asked of the action
`A`, not of `[A]_vars`, so a step that changes nothing counts only when `A` itself allows it. -/
def Enabled {σ : Type} (A : σ → σ → Prop) (s : σ) : Prop := ∃ s', A s s'

end Topak.Spec
