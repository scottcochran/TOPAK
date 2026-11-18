# Policy as code, externalized: how much of the refinement from model to code it removes

**2026.11.18** · derived · an answer, not a record · basis: the tree at `6588bce` (after G12), ADR-0010, ADR-0030,
ADR-0033, ADR-0045 (T-0045-3, T-0045-28, T-0045-37), ADR-0053, ADR-0057 (Proposed),
`mechanism/GAPS-AND-ASSUMPTIONS.md`, `mechanism/lean/`, `spec/FloorComposition.tla`, and
`derived/topak-refinement-verification-options-2026.11.04.md` · written by the assistant in answer to the
custodian's question, quoted below · nothing here is built or ratified, and the only measurements are line counts
read from the tree.

> how much does declarative externalization of "policy as code" minimize the complexity of formal model to code
> refinement?

**Short answer.** It removes almost all of the refinement work that depends on what the policy says, and none of
the work that depends on state. In this corpus the first is the smaller part. What it removes also does not vanish:
it comes back as a short list of premises, each of which has to be named and kept in step. And the saving exists
only because ADR-0030 constrains how the two tiers compose and puts the floor in a language with a mechanized
semantics. Externalizing policy into an unconstrained language would move the problem and not shrink it.

---

## 1. Three refinements, not one

The corpus uses "refinement" for three relations, and externalization does something different to each.

| | What refines what | What externalization does to it |
|---|---|---|
| **Policy to policy** | A bundle refines the floor, `bundle ⊑ floor` (ADR-0010) | **Discharged by construction.** Under `admit ⟺ floor_permit ∧ ¬bundle_deny` the relation holds of the composed decision for every bundle at every age, so no bundle can fail it (ADR-0030 §1) |
| **The decision** | The code's admit decision is a `Decide` step of `spec/FloorComposition.tla` | **Made small, and done once.** The proof is of the wrapper and `compose`, with the engine premised (§2) |
| **The state machine** | `State::apply` refines `Lease`, `Seats`, `Coupling`, `Confinement` and the rest | **Nothing.** T-0045-28 still reads "No refinement exists" (ADR-0045 Annex A) |

## 2. What it removes

**The bundle's text leaves the proof entirely.** `spec/FloorComposition.tla` models the bundle as havoc: at every
decision it may return any of six outcomes, which quantifies over every bundle at once, stale and hostile ones
included. The module's theorems are therefore true of bundles nobody has written yet. A new bundle owes its three
gates (ADR-0007) and a signature, not a proof.

**The composition is a few lines, and what is proved of it holds for any policy.** `compose` and `floor_gate` are
pattern matching over two enums, in an 87-line file (`mechanism/crates/topak-core/src/admit.rs`).
`mechanism/lean/Topak/Admit.lean` proves `admit_iff` and the three §1 properties of a transcription of them, for
every floor outcome and every bundle outcome. No policy appears in those statements.

**The floor has no model-to-code gap of its own.** The Cedar text the gates analyse is the text the linked engine
runs. ADR-0030 §6 refuses a transpiler in either direction for that reason: "the proven text is not the enforced
text" is the failure the record exists to rule out. ADR-0057 (Proposed) calls this edge spec-as-source: "the floor
is run as written."

**A policy change stops reopening the refinement.** ADR-0030 §2 states the alternative it declined: a floor written
in the mechanism's own verification language is admissible, and "each floor change then requires a re-proof."
With the floor external, a floor change owes decidable checks over schema S (§5), not a new refinement.

One qualification, which an earlier chat answer of the same day put too broadly. The floor side of the *refinement*
is not policy-independent as built. `mechanism/lean/Topak/FloorRefinement.lean` proves the code's decision a
`Decide` step at the module's four policies, P1 to P3 and F1. Only the bundle side and the composition theorems
quantify over every policy.

## 3. What it relocates

Each item below is refinement work that externalization did not remove. It became a premise or a separate check.

| Where the work went | What the corpus holds | Source |
|---|---|---|
| **The engine** | A trust-root row: the Cedar engine is faithful to the Lean model. Residual: divergence on inputs outside the conformance corpus | T-0045-3; ADR-0030 §3 |
| **The lift** | 422 lines of Rust (`mechanism/crates/topak-core/src/lift.rs`) that compute the facts both tiers read. `FloorRefinement.lean` does not transcribe it and takes the module's `Reassign` and `Seal` as its steps | ADR-0030 §4; the file's own header |
| **The schema** | The analyses quantify over all requests satisfying S, so S must be enforced on every request. "A proof about a schema the running system does not enforce proves nothing about the running system" | ADR-0030 §4 |
| **Which policy is in force** | At ADR-0053 R2 there were three floors: the module's 4 policies, the genesis floor's 17 stated in Lean, and the 28 the reference linked. "Each result is true of the floor it names, and none is of the floor in force." R3 closed it for the gate claims, not for the refinement | ADR-0053 finding 6 |
| **Keeping the proof in step** | `mechanism/lean` is stale at G12. `admit.rs` still has the digest the results name; `mechanism/crates/topak-floor/src/lib.rs` does not, since it now links the `workflow` stage of 30 policies | G12 §7 item 103; digests read at `6588bce` |

The fourth row is the cost particular to externalization. A policy inside the verified artifact cannot be proved
about under one text and run under another. An external one can, and it took a finding to notice.

Two limits are structural, not debts.

- **A request-time policy sees only request-time facts.** `policies/actuate.rego` refuses a tool that declares no
  channel, "and that is all a request-time policy can do: whether the tool opens that channel is a fact about the
  tool, not the request" (`mechanism/GAPS-AND-ASSUMPTIONS.md` finding 14).
- **History is the mechanism's, not the policy's.** `clearSet` is the first attribute in S that depends on a
  round's history. It is "a monotone fold the mechanism computes", and "a policy, floor or bundle, declares no
  history attribute of its own" (ADR-0030 §4, A2). Every such attribute is state-machine code, in the third row
  of §1's table.

## 4. What it does not touch

Leases, seats, epochs, fencing, consensus order and coupling are imperative, stateful code, and their refinement is
as hard as it would be with no policy tier at all. The tree gives three measures of the difference.

| | The decision | The state machine |
|---|---|---|
| **Rust** | `admit.rs`, 87 lines, and the `topak-floor` wrapper | `state.rs`, 1,979 lines |
| **Lean** | `Admit.lean` 349 lines and `FloorRefinement.lean` 275 | `SeatsModel.lean` 1,038 lines for one module; `CouplingModel.lean` 748 for another |
| **What the Lean covers** | The whole of its slice, the engine premised | Seat and lease fields only; "the oracle `ok` stands for most of `apply`", so it is not a stage of T-0045-28's chain |
| **Estimated cost of a mechanical route** | Days, for `admit.rs`, `clock.rs` and `lift.rs` | Months, "and needs refactoring first" |

The last row is the 11.04 options document's estimate for Aeneas, not a measurement. Line counts are a crude proxy.
The third row is the one that matters: the decision's proof is complete over what it names, and the state
machine's is a model with an oracle, differentially tested.

That model also shows what reading a model against code is worth. Written without the end of the lease after
`Submit` and `Vote`, it was proved anyway, and the first replay failed 25 of 58 traces. "A model that is read
against the code and not run against it can be wrong and still proved" (ADR-0053 finding 7). Nothing about
externalized policy helps there.

## 5. The conditions the saving depends on

Externalization alone does not produce §2. Three decisions of ADR-0030 do, and each gives something up.

1. **The composition is monotone and is a mechanism constant** (§1). This is what lets the bundle be havoc. The
   price is stated in the record: "A bundle cannot establish that something is allowed."
2. **The floor's language has a mechanized semantics and decidable comparisons** (§2). The bundle tier is held to
   neither, and the reference found what that costs: ADR-0031 §4 allowed a renewal to narrow the bundle, "but
   nothing orders Rego bundles", so renewal now keeps the bundle identical (`mechanism/GAPS-AND-ASSUMPTIONS.md` I4).
3. **The floor is linked, and its inputs are written only by the lift** (§3). No bundle has a write path to
   anything the floor reads, so the floor can be analysed alone. `BundleCannotWriteFloorInputs` is the theorem.

Without the first, every bundle would owe a proof against the floor. Without the second, the floor's text would
need a hand-built semantics, which is a model-to-code gap again. Without the third, the analyses would describe
entity stores the running system does not have.

## 6. What follows

Nothing here asks for a record. Three observations, each already carried somewhere:

- **The remaining refinement debt is the state machine's**, and policy design will not reduce it further. The
  11.04 options document is the place that work is weighed.
- **The lift is the cheapest uncovered piece on the policy side.** It is small, mechanical by its own
  description ("every fact is a set membership, an equality, or a path-syntax check"), and the 11.04 document
  prices it with `admit.rs` in days.
- **A refinement of the floor in force, and not of the module's four policies, is still owed** if
  `FloorRefinement` is ever to be a stage of T-0045-28's chain (ADR-0053 finding 6, R1's two conditions).
