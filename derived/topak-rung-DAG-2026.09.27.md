> If we treat the "archetype" as a moveable indicator on the rung ladder, fix ordering to increasing by theorems holding, fix rung 0 as maximum degeneracy that is still TOPAK, and identifyinterim rungs by theorems voided, and archtype can increase rungs by adding theorems via bootstrap, is that a valid approach?

**Verdict:** valid as a re-indexing of what ADR-0023 already defines, with one part that does not survive contact with the corpus and three conditions that have to be met first. The corpus already computes a deployment's inventory as the archetype's theorems minus those voided, so "identify rungs by theorems voided" is ADR-0023 §2 restated. What you are adding is a bottom, a bottom-anchored index, and a rule for moving the top. Those are decisions the corpus has deferred, not contradictions of it.

**What holds up**

- **Rung 0 as a fixed bottom.** The corpus has no bottom today; ADR-0023 says finiteness with a bottom is unproven. You can define one mechanically: the theorems whose premises reference no degeneracy parameter. Those are the mechanism constants the records already say "hold on every rung": epoch fencing, composition, recusal, timeout never grants, rung-0-is-`Mediated`, and the non-relaxable rules-floor entries. Things the corpus refuses to call degeneracies, such as permit-override composition or semantic lift, are exactly what falls below rung 0. That gives "still TOPAK" a checkable meaning.
- **Bottom-anchored ordering.** Today positions are defined relative to the archetype, so moving the archetype relabels every deployment. Indexed from the bottom, a deployment's rung is stable when the archetype moves, and only the archetype's rung changes. That is a cleaner form of the "(archetype version, rung tuple)" conformance binding ADR-0023 deferred, and it softens the declaration-debt problem ToO §7.8 names.
- **Moveable archetype.** ADR-0023 clause 4 already forces the archetype to grow when a variation fails admission, and the deferred dominance rule already says it may only move to Pareto-dominating values. Your scheme makes that a rung increment. The only bound missing today is the rule for how it moves, which is the unwritten archetype-evolution record, G3 item 7.
- **Composition dissolves.** If the inventory is computed per deployment against the theorem-premise binding, the composition note becomes a computed result instead of a claimed delta. The 09.16 review offered exactly this "per-tuple inventory" option.

**What does not survive**

- **"Ladder" asserts a total order the corpus has already refuted.** ADR-0023 rejected the single total order because Observer scoping is incomparable: shared Observers see cross-principal timelines that per-principal ones cannot, and per-principal ones bound `L`. Theorem sets under inclusion form a lattice, not a chain. You have three honest options. Index by set and report height as the count, accepting that two rungs can share a height. Or fix a canonical hardening order of theorems so rung k means the first k hold, and treat deployments off that order as declaring by set. Or keep the lattice and drop the word ladder. The count alone loses the information ADR-0023 §2 says is the whole point, which theorems, not how many.
- **"Via bootstrap" is the wrong instrument.** Bootstrap is the one-time anchor ceremony of ADR-0029. Adding a theorem is a corpus change: a record, a TLA+ property with a mutation, and for mechanism theorems a release promoted under ADR-0024. After bootstrap that is a promotion; during genesis it is a ratification. Say "via archetype version" and the rest of your sentence is right.

**Conditions before it is usable**

1. **Publish the theorem-to-premise binding.** ADR-0023 says the composition note is only as good as the binding the archetype publishes, and no such table exists. Without it "theorems voided" cannot be computed for any tuple, and the whole index is prose.
2. **Carry the trusted base as a second coordinate.** ADR-0023 §4a exists because D-0025-1, D-0025-2, D-0034-1 and D-0034-2 void no theorem while moving the gate or enlarging the TCB. Under a theorems-held index they sit at the archetype's rung. Either state TCB membership as theorems with premises, or the rung carries a declared TCB row beside it.
3. **Decide whether rung 0 is a claimable conformance.** ADR-0033 refuses to call the reference a deployment because every principal is `Mediated`. Under your scheme the reference and the SLM rehearsal sit at or near rung 0 with A1 failing, which is the honest label for them. Saying so changes ADR-0033 §1's stance.

**Two consequences to accept**

- The per-axis rung numbers in ADR-0017, ADR-0031 and ADR-0034 become parameter values, not rungs. That resolves the naming collision from the audit, but the lease field `confinement: [digest, rung]` is in an Accepted C1 record and in the reference, so it is an amendment plus a code change.
- A theorem-count height rewards many cheap properties over one expensive one. Confinement at rung 3 is one parameter and carries every containment theorem; a clock drift bound carries almost none. Height is a fair ordinal only if the theorems are of comparable weight, or if the canonical order encodes the weighting.

**Where to write it.** As the archetype-evolution record, not as a supersession of ADR-0023. The relation, premise-loss rule and admission test stay; the new record adds the bottom, the index, the binding table as an obligation, and the movement rule. That keeps ADR-0023's C3 marker from acquiring a second reversal.

> What if we use a heap instead of a tuple. that way the hierachy is captured and extensible.

**Short answer:** a heap is the wrong structure, but the instinct behind it is right. What you want is the theorem-dependency graph with a closure property, and that is a DAG with order ideals, not a heap. The heap fails on the first theorem with two premises, and the theorems that matter most in TOPAK all have several.

**Why not a heap**

- **A heap orders a scalar key and its shape means nothing.** Parent-child position in a binary heap is an artifact of insertion order. Siblings have no relation. So a heap cannot express "`Contained` depends on attested confinement," which is the hierarchy you want captured. It can only say one node's key is bigger than another's.
- **If the key is "holds," the heap property degenerates into closure.** Put the mechanism constants at the root and read parent ≥ child as "a child holds only if its parent holds." That is a real structure: a rooted subtree of theorems that hold. But it is a tree, so each theorem gets exactly one premise.
- **The corpus's load-bearing theorems have multiple premises.** `Contained` needs attested confinement, profile clauses P3 to P5, and in-house provenance. NC-1 needs the break-glass entry, the erasure entry, and R7. Composition in ADR-0023 §7 is literally a node with two parents where neither parent alone decides it. A tree cannot represent any of these.

**What captures the hierarchy and is extensible**

Take the theorem-to-premise binding, the table I said was the missing prerequisite, and read it as a graph.

- **Nodes of two kinds.** Premise nodes, one per degeneracy parameter value, such as "confinement rung ≥ 2" or "custody is (n, 0)". Theorem nodes, one per checked property, such as `Rung0NeverContained` or `NoSilentDowngrade`.
- **Edges run from a theorem to every premise it needs.** A theorem holds for a deployment iff every premise it points to holds. That is the same rule ADR-0035 uses for lineage strength, weakest link over a DAG projected from evidence, applied to theorems instead of training rounds.
- **A deployment is a down-closed subset**, an order ideal. Its declared parameter values fix the premise nodes, and the inventory is computed by closure. Nothing is asserted about which theorems hold; it is projected from the declaration, which is the same "projected, not authored" move ADR-0035 makes and the reason a Byzantine Build author cannot relabel.
- **Rung 0 is the set of theorems with no premise node**, the mechanism constants. The archetype is the whole graph at a version. Height is derived, longest chain or count, and is a label rather than the position.
- **Extension is adding nodes and edges.** A new theorem is a new node with edges to existing or new premises. A new axis is a new family of premise nodes. No existing deployment's ideal is invalidated; it just does not reach the new node. Adding a premise edge *into* an existing theorem weakens that theorem, which is the move ADR-0023's carried scope says needs its own record, and the graph makes that visible as an edit to a published node.

**Two rules you have to fix for it to work**

1. **Undeclared premises are false.** When the archetype grows an axis, every existing deployment sits at the bottom of it until it declares. That is fail-closed, matches ADR-0031's "undeclared confinement is no confinement," and turns ToO §7.8's declaration debt into a computed fact rather than a warning.
2. **Type changes are premise nodes too.** "Key-holders are at the gate" and "the hypervisor is outside the trusted base" become premises that D-0025-n and D-0034-1 falsify. Then ADR-0023 §4a stops being a side condition and the trusted base is read off the same graph.

**What this does to the existing pieces**

- The tuple survives as the *input*: the declared parameter values. The graph is the *evaluation*. You do not lose the tuple, you stop treating it as the position.
- The composition note becomes a graph query. Any theorem with premises on two different axes is a composition node, and the gate can list them instead of asking the declarer to assert a delta.
- ADR-0023's relation, admission test and premise-loss rule stay as written. What changes is that "theorems voided" is computed by closure rather than listed by hand, and per-axis "rungs" become premise-node families.
- The graph is also what `mechanism/corpus-pins.sha256` is trying to be for code: every theorem node cites the TLA+ property and mutation that check it, so a re-pin is an edge whose evidence moved.

If you want the word to keep, it is a **lattice of order ideals over the theorem DAG**. A heap would be a fine choice only for the evaluation order when computing an inventory, and that is an implementation detail nobody needs to name in a record.

---

> **Added 2026.09.29.** A path through the lattice, worked for the reference's own occupant.

**The `slm/serve` ladder as a path of order ideals.** ADR-0036 R1 lets a rung-0 grant name a profile, and holds the
profile schema constant across rungs. That gives a concrete path in the DAG above, in which every step adds exactly
one premise node, so each step's added inventory is a closure query rather than a claim:

| Step | Premise nodes added | What becomes reachable |
|---|---|---|
| `serve.py` on the host, rung 0, `profile-host-rung0.json` declared | None. The ideal is rung 0's mechanism constants. The profile is an *input* whose clause nodes (P5, P6, P7) are declared true and unverified; a declared premise contributes nothing to the ideal, by rule 1 (undeclared or unverified premises are false) | Nothing beyond rung 0. `Mediated` is derived from the profile, not from its absence, but no theorem moves |
| Docker plus the ADR-0036 launcher, rung 1 | "confinement rung ≥ 1"; P1, P2 asserted | The rung-1 conditional theorems: session binding by construction; `NoSilentDowngrade` at grant and renewal. `Contained` still unreachable: P3 false |
| P3-passing image, still rung 1 | P3 | `Contained` reachable, conditional on the ADR-0035 criterion node |
| Firecracker or Kata, rung 2 | "confinement rung ≥ 2"; the launch-measurement premise | *Contested* becomes a reachable verdict (ADR-0034 §7); the launcher leaves the trusted base for guest integrity (a type-change premise node, rule 2) |
| Confidential VM with accelerator attestation, rung 3 | "confinement rung = 3"; the inference-attestation premise (G4 item 29) | The host leaves the trusted base; the Reader's conformance fact stops being a self-report and ADR-0019's admitting use has a premise (ADR-0037 §3 R3) |

Two things the table shows that the prose in the records does not. First, **the rung-0 profile adds no node**: a
declaration is an input to the graph, and rule 1 makes an unverified premise false, so being explicit at rung 0 changes
what the verdict is *derived from* without changing the inventory. That is the right reading of ADR-0036 R1's
"declared by the operator and verified by nobody". Second, **the P3 step and the rung-2 step are incomparable** in
the lattice: a rung-2 guest with an interpreter and a rung-1 guest without one are two ideals neither of which
contains the other, which is the same shape as the Observer-scoping pair that made ADR-0023 refuse a total order.
The ladder is a path, not the order; a deployment may take the two steps in either sequence.
