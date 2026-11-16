# Checking the premise

Three checks, in order of cost. The first is routine for every file. The other two are for where a wrong encoding would
do damage.

## Mutants

Copy the package to a scratch directory, break one thing, and build. Each mutant is the code-level or encoding-level
shape of a mutation the source already has.

Revise the case lemma that states the mutated arm, as an honest revision would. Otherwise you are only testing that an
equation changed.

Record the result in the package README:

| Module | Mutant | Fails in |
|---|---|---|
| Seats | a grant does not refuse a principal holding a live lease elsewhere | `NextInvS` (feeds `OneSeatPerPrincipalAlways`) |

A lemma whose proof fails although its statement still holds in the mutant, because its proof names the mutated guard,
is not a result. Leave it out.

A mutant under which everything still proves is the finding. Either the theorem does not depend on the guard, or
another guard covers it, and only a witness catches it. One real example: an envelope field dropped from an activation
left every theorem provable, re-proved from a fact in force from `Init` on, and the model checker agreed. Only a
reachability witness caught it.

## A mirror against the state graph

An encoding can be too lax or too strict and still prove every invariant. A grant on a seat that already has a live
lease keeps both invariants of one module. To check rather than read:

1. Write a mirror: a concrete state with Booleans and Boolean functions, a map `toState` into the encoding's states,
   and a list of successors `succC`.
2. Prove `next_iff` (the encoding's `Next` from a mirrored state reaches exactly the mirrored states in the list),
   `init_iff`, `eqC_iff`, and one `*_iff` per property. These are proved.
3. Have the model checker dump its whole state graph, through a wrapper module whose one derived variable carries every
   property's value, so the graph's shape is unchanged.
4. Evaluate the mirror on the dump: every edge is a `Next` step, every `Next` step from a graph state is an edge or a
   stutter, the initial states are `Init`, and every property has the checker's value in every state.

The theorems are proved; the evaluation is a test, and covers what the checker reached. Where the encoding fixes the
module's constants, that is every state. Do this when something refines the encoding, or when an `ENABLED` theorem
claims a step exists.

## Trace replay

For a model of running code, record the code's own steps during its test suites. Run each recorded entry through the
model's own `apply`, with the oracle set to whether the code applied it, and compare the result and the fields modelled
afterward.

That is the direction proofs need: every recorded code step is a model step. It is a test over the traces the suites
produce, and says nothing about a step they never take.

Then mutate the code, not the model: remove a check from a copy of the source and record its traces. Replay should fail
at the step where the code and model diverge, which shows the replay can see the gap.

A replay that fails right after a step the model treats as inert usually means an effect was left out. The proofs will
not have complained, because leaving out an effect that only ends things breaks no safety invariant.
