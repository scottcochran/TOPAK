# Encoding

## TLA+ to Lean

One shared prelude states these once, and each file names only its departures.

| TLA+ | Lean | Why |
|---|---|---|
| A set | A predicate, `abbrev PSet α := α → Prop` | `SUBSET S` is every predicate, and no finiteness is assumed where none is needed |
| A string-valued constant set | An inductive type, one constructor per string, `deriving DecidableEq` | Distinctness and exhaustiveness come from the type |
| A BOOLEAN variable | `Prop`, with `x' = (a \/ b)` as `x' ↔ a ∨ b` | Matches how the module uses it |
| A variable only ever set to TRUE or FALSE | May be `Bool` | Simpler case analysis |
| `IF c THEN a ELSE b`, `c` decidable | `if` | |
| `IF` on a set membership | `(c → x = a) ∧ (¬c → x = b)` | Keeps `Classical.choice` out of definitions |
| `S # {}` | `NonEmpty S`, "some element is in S" | The two are equal only classically; this is what modules mean |
| `Cardinality S = n` | A relation `HasCard` built from the empty set, or `card` on `Human → Bool` | Finite-set theory is not in core |
| `[f EXCEPT ![x] = v]` | `upd f x v`, with `upd_same` and `upd_other` as simp lemmas | |
| `UNCHANGED x` | `x' = x`, or `st' = { st with ... }`, which is the primed conjuncts and the `UNCHANGED` list at once | |
| `Next` | A relation, one disjunct per action | |
| `Spec => []P` | `∀ s, Reachable Init Next s → P s` | Stuttering is dropped: a step that changes nothing keeps any invariant |
| `-` on naturals | Compute in `Int` | TLA+'s is integer subtraction; `Nat` truncates |
| `ENABLED A` | `∃ s', A s s'` | Asked of the action, not of `[A]_vars` |

**Keep the action's shape.** An action's guards and primed conjuncts become a conjunction in the same order, because
that is what makes reading it against the source a matter of minutes.

**Mutations.** `inductive Mut | none | M_X | ...`, with the guard written as the module writes it: `m = .M_SEAT ∨ ¬
HoldsElsewhere st p s`.

**Names.** Keep them. When Lean forces a change (`seal` is a keyword, or an action and a set share a name) rename with
a suffix and say so in the header.

**Constants.** Fixed finite constants become inductive types. Parameters go in a `structure Cfg`, and then the theorem
holds for every value. Assumptions that hold by type vanish: `MaxEpoch ∈ Nat`, `TypeOK`. Say so in the header, and do
not prove a counterpart. An assumption about the property itself stays as a hypothesis.

**Successors.** A module replaced by a successor gets a new file. A module extending a frozen one without replacing it
is encoded in the same file, and its results line names both.

## Transcribing code

Each definition's doc-comment carries the code it transcribes. Use the code's types, with machine integers as naturals
below their bound and saturating operations as capped sums. End the file with the code's own test assertions as
`example`s closed by `rfl`, since that shows the transcription evaluates as the code does. Types the composition
neither produces nor inspects can be opaque, with a theorem saying so.

## Modelling code

A transcription of a large function is rarely practical. A model keeps each arm's checks and effects on the fields a
property is about, and folds every other check into one Boolean oracle that can only refuse. Its steps are then every
step the code can take, whatever those other checks decide. State the premises the code has but does not check itself,
for example that indices arrive strictly increasing because the consensus layer delivers them so.

A model may narrow another's oracle: define its `apply` as the first with further checks folded in, and the first's
theorems hold by `Reachable.mono`.

A model is proved at any size. Its refinement to an encoding is proved at the encoding's constants. Those are different
claims, and documents should say which.

## Statements in a verified semantics

Generate them, from the policy's own files through the engine's own parser, with digests of the sources in the
generated header. Regenerate on every results run. The generator and the parser are the premise. Anything in the
semantics the engine does differently (for example action entities the engine adds implicitly) is a finding to record.
Ensure the statement is of the policy that actually runs: a sync check that fails if the linked policy has no statement
catches a move to another stage.
