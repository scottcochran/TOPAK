# Shrink-wrapping a premise lattice: havoc actors, the mutation matrix, witnesses and flips, and what other fields call them

> Isnt modelling the "black boxes" as havoc actors a valid approach to modelling the overall architecture?

> Can TOPAKs patterns of mutation matrix, witnessess, and hypothesis flipping be used to iteratively shrink wrap a
> theorem/properties lattice to the minimum which satisfies the requirements/invariants?

> what are the analogous practices in other formal methods practices? Math, crypto, etc ...

(The custodian's three prompts of 2026.11.16, in order, in a discussion that began with a fourth: "Isnt TLA+
specificlly suited to the problem. Even if it only identifies the gaps?", asked about a failure of an air traffic
control telecommunications network.)

**2026.11.16** · derived · a reading, not a record · prepared by Claude at the custodian's request · read against
`9656e35` and against the `gov-tla` repository at `182053d` (branch `ccr-a0b798bc-jsm766`, not merged when this was
written)

**What this is.** The answers given in that discussion, written up and checked against the corpus. Two of the
answers were given before the corpus was read and were wrong about it in one respect each; §3 and §4 say where.
**It decides nothing.** §6 lists suggested entries, none made. The external literature in §5 is cited from
memory and was not re-read for this note. The author is the assistant that wrote the experiment in §1, so the
reading of it is one reader's.

---

## Verdict

1. **Havoc actors: yes.** Modelling a component nobody can open as an actor that may do anything its interface
   allows is sound for safety, and it turns the question from "what does the box do" into "what must the box not
   do". The answer to the second question is a requirement that can be written into a contract and tested.
2. **Shrink-wrapping: yes, to a minimal set, not to the minimum.** The mutation matrix, the witnesses and the
   hypothesis flip are together a loop that removes every premise a property does not need. What the loop reaches
   is a set from which nothing more can be removed. It is not shown to be the smallest such set, nor the only one,
   and the corpus already holds a theorem with two.
3. **Analogues: every mature formal discipline has the same three moves.** Several also have a fourth and a
   fifth, reversal and separation, which are how they close the distance between minimal and minimum. The corpus
   has half of the fourth and none of the fifth.

## 1. The experiment behind the question

The discussion started from another assistant's claim that an abstract TLA+ specification of a converged air
traffic control network "would likely expose" three faults: failover states that never converge, control-plane
starvation by data traffic, and a permanent failover oscillation. That was an assertion, so it was tested.
`AtcNetwork.tla` in `gov-tla` is the test, written by the method of the `writing-tla-specs-and-proofs` skill. It
is not a model of any fielded network and was written from no design document.

The module is one failover mechanism with three checks, and one mutation removes each. All 62 rows of its row
list came out as expected (`gov-tla`, `results/AtcNetwork-results-2026.11.16.txt`). Three things in it bear on
this note:

- **Every gap was written in on purpose.** Each row came out as predicted before it was run. TLC confirmed,
  found the shortest traces and filled the cells that say a mutation breaks nothing else. It discovered nothing.
- **One HOLDS cell hid a dependency.** With the control plane in band, the shared backup path is still safe,
  because admission control keeps it from congesting. Two defences cover the same fault, and a matrix of single
  mutations reads that as "the mutation does no harm here". §3 returns to this.
- **The model's own control plane was the part under suspicion.** The environment in that module is already a
  havoc actor: links fail and traffic surges whenever they like. The routers are not. They follow a mechanism the
  author chose, with defects the author chose. The custodian's first prompt above is the observation that this is
  the wrong way round.

## 2. Black boxes as havoc actors

**Why it is valid.** A havoc actor over-approximates. If a safety property holds while the box may do anything
its interface permits, it holds for whatever is really inside, because the real behaviours are among the modelled
ones. No vendor specification is needed, only the interface. This answers the objection that a network of
commercial equipment cannot be specified because its firmware is closed.

**Where the value is.** A wholly unconstrained box breaks every property, and that says nothing. The work is the
next step: find the weakest constraint on the box under which the property holds again. "The router may drop any
packet at any time" breaks a no-false-alarm property at once. "The router drops a keepalive only when the link is
down or the control queue is full" restores it. The second sentence is the output. The method does not find gaps
inside the box. It finds what the architecture was silently relying on the box to do.

**The corpus already reasons this way about its trusted base.** ADR-0045 admits a component only if "its failure
can only subtract, or its identity is issued". Read as a model, that is a havoc actor held to omission: it may
withhold, and it may not add. `spec/theorem-premise-binding.md` then names, row by row, which properties rest on
which component behaving so. What the corpus does not do is model a trusted-base row as an unconstrained actor
and derive the constraint by checking. The constraint is declared, and the properties are checked under it.

**Three limits.**

- **A counterexample may be spurious.** It can use a behaviour the real box never shows. The supplier may say
  so, and must then state the constraint that excludes it, which becomes a written premise. The dispute is
  productive, but it is a dispute.
- **Liveness needs more than havoc.** A box that may always drop lets nothing converge. Progress needs a
  fairness premise ("a message sent repeatedly is eventually delivered"), which is harder to justify and to test
  than a safety premise. In the lattice of `derived/topak-safety-liveness-quorum-lattice-2026.11.05.md` these are
  the premise nodes that sit under liveness theorems only.
- **The premises still have to be true.** The model shows the architecture is right if the boxes meet their
  premises. Whether they do is for a laboratory and the field. A redundant circuit that exists on paper and
  shares a conduit with the primary is a false premise, and no specification of the design can see it. This is
  T-0045-28 in another setting: the thing running is not shown to be the thing specified.

**How strong the havoc is, is a choice.** Crash, omission (drops and delays) and arbitrary behaviour give three
different premise sets. For commercial routers, omission with stale state is probably the honest level.

## 3. Shrink-wrapping

**What each device bounds.**

| Device | Where the corpus defines it | What it bounds |
|---|---|---|
| Mutation matrix | ADR-0046 §1; the "Breaks under" column of `spec/theorem-premise-binding.md` | Necessity, from above. Remove a guard and get a counterexample: the property needs it. Remove one and break nothing: the guard is surplus, or a property is missing |
| Witnesses | ADR-0026 (a TLC result is non-vacuity and discrimination, not proof) | Non-vacuity, from below. They stop the shrinking from succeeding by over-constraint, where the states of interest become unreachable and every invariant holds for no reason |
| Hypothesis flip | `spec/proof-method.md` §1 (weakest hypothesis) and §2 step 9 (the flip) | The edges. Each theorem takes only the mutations that break it, and flipping one must break the proof. That labelling is the lattice |

**The loop.** Start from the havoc actor. Take the counterexample. Add the weakest guard that excludes it.
Repeat until the property holds. Then try deleting each guard, and keep a witness for every state the
requirements say must stay reachable. What survives is the premise set.

**The corpus has run this loop, in one direction.** Writing each theorem's weakest hypothesis corrected the
binding table five times (ADR-0046 §5; `spec/proof-method.md` §1). Four were "Breaks under" entries, each a
mutation or a guard set against the wrong property. The fifth struck a parameter premise, `K < R`, from two
bounds that are proved without it. Each is one turn of the loop: the proof found the
premise set was not the minimal one and the table was changed.

**Where the loop stops short of the minimum.**

- **Single mutations miss overlapping defences.** If two guards each cover for the other, removing either
  breaks nothing and the matrix calls both unnecessary. §1 has an instance. In the discussion I said the method
  forbids the remedy, because the skill's rule is one guard per mutation, so that a broken property can be
  attributed. *That was wrong about the corpus.* `spec/RulesFloorNV_rev5.tla` does not take one mutation. It
  takes the set of floor entries in force, `Active`, and its rows drop entries singly and together:
  `spec/RulesFloorNV-rev5-results-2026.09.23.txt` has a row that drops R1 and R9 at once. The set-valued form is
  the remedy, and attribution is kept because each theorem names the entries it needs.
- **There is usually more than one minimal set.** The same module shows it. The hypothesis of `P9Always` in
  `spec/RulesFloorNV_rev5_proof.tla` is R2 and either R1 or R9, which is two minimal premise sets, {R2, R1} and
  {R2, R9}, neither inside the other. `derived/topak-rung-DAG-2026.09.27.md` made the same point about
  deployments: theorem sets under inclusion are a lattice, not a chain. Choosing between minimal sets is a
  judgement of cost, and no tool here makes it.
- **A guard is tested only at the points someone wrote.** A mutation removes a guard whole. The weakenings in
  between are unbounded, so "weakest" means weakest among the candidates proposed.
- **TLC can shrink too far.** A counterexample stands at any size. "Holds without this guard" is checked at
  small constants, and a guard needed only at larger ones would be dropped. The proof is the stop on that, which
  is why the flip belongs inside the loop and not after it.
- **Liveness does not shrink monotonically.** A fairness premise, or a mutation that removes an action,
  restricts behaviours. Dropping or adding one can leave a specification with no behaviour at all, under which
  everything holds. The `NoBehaviour` rows of `spec/Coupling_live-rows.txt` exist for this.

**The fixed point is the requirements.** The loop minimizes mechanism against a property set it takes as given.
It cannot say the properties are right or complete, and every "this guard breaks nothing" has two repairs:
delete the guard, or add the property that was missing. Which one is the custodian's decision, not the
checker's.

## 4. The same moves elsewhere

| Field | Is each hypothesis necessary? (mutation) | Is the theorem non-vacuous? (witness) | Does the proof use it? (flip) |
|---|---|---|---|
| Mathematics | A counterexample showing a hypothesis is sharp; independence by a model in which one axiom fails (the parallel postulate) | An object that satisfies the hypotheses; consistency by a model | Reverse mathematics; a referee asking where compactness was used |
| Proof assistants | Delete a hypothesis and re-check | Show the hypotheses are inhabited | Unused-argument linters (Lean's Mathlib); `Print Assumptions` in Coq, which lists the axioms a proof rests on |
| Cryptography | An attack once an assumption is dropped (a reused nonce, an oracle that is not random) | Correctness: the scheme decrypts, the honest run completes. Tamarin's `exists-trace` lemmas are this | The reduction: breaking the scheme breaks the assumption |
| Hardware verification | Mutation coverage: inject a fault into the design, and some assertion must fail | `cover` properties; vacuity detection for an assertion whose antecedent never fires | Proof cores: the constraints the solver used |
| SAT and SMT | Minimal unsatisfiable subsets | A model of the assumptions alone | Unsatisfiable cores |
| Program verification | Weakest preconditions (Dijkstra); counterexample-guided refinement | Reachability of the cases the postcondition is about | Interpolants, which extract what the proof needed |
| Safety engineering | Single-point-of-failure analysis; fault injection | A demonstration that the nominal mission completes | Fault-tree minimal cut sets |
| Software testing | Mutation testing, where the word comes from (DeMillo, Lipton and Sayward, 1978) | A test that passes on the real program | A surviving mutant: the suite does not depend on that line |

**What the others do that the corpus's pattern does not, or does in part.**

- **Reversal.** Reverse mathematics does not stop at "the theorem fails without this axiom". It proves the
  axiom from the theorem over a weak base theory, so the two are equivalent and the hypothesis is the weakest
  possible, not only the weakest tried. The corpus has half of this. Each proof module carries one lemma per
  mutation saying what the mutation admits (`spec/proof-method.md` §1), which is the direction "without the
  guard, the bad step is allowed". It has no lemma in the other direction, "the property implies the guard".
- **Minimal cut sets.** A fault tree enumerates every minimal combination of failures that causes the top
  event. That is the systematic form of the dropped-together rows above. In the discussion I said the corpus's
  dependencies are declared by hand and only tested. *That understated it.* `spec/inventory.py` computes, from
  the binding table and a deployment's declaration, which theorems are void. It answers "what is lost if these
  rows fail". It does not answer the converse, "which smallest sets of rows, failing, lose this theorem".
- **Separations.** Cryptography has results that no proof of a given shape can exist (Impagliazzo and Rudich,
  on key agreement from one-way functions). Distributed computing has lower bounds of the same kind, such as
  3f+1 replicas for f Byzantine faults. These say a premise set cannot be shrunk by any mechanism, not only by
  the one in hand. The corpus has nothing of this kind, and for a governance mechanism it may have little use
  for it.

Reversal and separation are how those fields turn "minimal" into "minimum": they close the distance from below
with a proof, where mutation only approaches it from above.

## 5. What this note does not establish

- **Nothing about any air traffic control network.** The experiment's module is abstract, small, and the work
  of one author who had no design document.
- **Nothing new about the corpus's proofs.** No module was run for this note. The statements about the corpus
  are read from the files cited, at the commit named.
- **The external references are from memory.** Names, dates and tool features in §4 were not checked against
  their sources.

## 6. Suggested entries, none made

1. **A cut-set view of the binding table.** For each property, the minimal sets of premises whose loss voids
   it, computed by `spec/inventory.py` from the table it already reads. It would show where a property has one
   premise standing between it and void, and where it has several minimal sets, as `P9_NoSoloGrant` does.
2. **Dropped-together rows where two guards cover one fault.** A row list could carry, for each pair of
   mutations that each break nothing against some property, one row with both. A module written with a set of
   checks in force, as `RulesFloorNV_rev5` is, gets these for the cost of a row.
3. **One reversal lemma, as a trial.** For a flag property, prove that the property implies the guard at the
   action that sets the flag. If it is cheap, the "Breaks under" column for that row is then tight by proof and
   not by search.
4. **A trusted-base row modelled as a havoc actor.** Take one row that ADR-0045 admits on the ground that its
   failure only subtracts, model the component as free to withhold anything, and check which properties
   survive. The binding table says what should happen. The run would say whether it does.

---

## Sources

The discussion of 2026.11.16. `gov-tla` at `182053d`: `AtcNetwork.tla`, `rows/AtcNetwork-rows.txt`,
`results/AtcNetwork-results-2026.11.16.txt`, `docs/ATC-NETWORK.md`. ADR-0023 §2; ADR-0026 (Findings); ADR-0045 (title
and Annex A, T-0045-28); ADR-0046 §1, §5; `spec/proof-method.md` §1, §2, §3; `spec/theorem-premise-binding.md`
(the head and the `P9_NoSoloGrant` row); `spec/RulesFloorNV_rev5.tla`; `spec/RulesFloorNV_rev5_proof.tla`;
`spec/RulesFloorNV-rev5-results-2026.09.23.txt` (the `dropR1R9` row); `spec/inventory.py`; `spec/Coupling_live-rows.txt`;
`derived/topak-rung-DAG-2026.09.27.md`; `derived/topak-safety-liveness-quorum-lattice-2026.11.05.md`;
the `writing-tla-specs-and-proofs` skill, `references/spec-design.md` (one guard per mutation).
