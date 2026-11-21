# Refinement and composition between the specification modules: what is missing, what it costs, and what the Lean models show

**2026.11.21** · derived · an answer, not a record · basis: the tree at `ffd02f1`; the modules, proof modules and
results files of `spec/` named below; `spec/README.md`, `spec/proof-method.md`; `mechanism/lean/` and
`mechanism/crates/topak-core/src/state.rs` and `workflow.rs`; ADR-0033, ADR-0045 (T-0045-28), ADR-0046, ADR-0053;
G12 item 56; and three derived documents, the 11.04 options paper, the 11.11 findings register and the 11.19
practice assessment · written by the assistant at the custodian's request, as the write-up of one session: three
answers, then a re-read of the sources that the custodian asked for after changing the session's model · nothing
here is built or ratified, and nothing was run: no model checker, prover, Lean build or test.

> What is the impact of not having inter module refinement in TOPAK?
>
> same question for module composition.
>
> how does the rust to lean refinement inform this discussion
>
> review this session and give me your independent assessment by reading from sources yourself

**How it was read.** Opened and read where cited: the headers and `Next` of `Seats`, `RunSeats`, `Lease_A1`,
`Confinement_A1`, `Coupling`, `RunCoupling`, `RunConfinement`, `Emergency`, `Emergency_live`, `NonComposition`,
`NonComposition_A1`, `BreakGlass_A1`, `RulesFloorNV_rev5` and `Workflow_A1`; `Mechanism.tla`'s header and its last
twenty lines; `ConfinementRefinement.tla` whole; the theorem lists of the two liveness proof modules and of four
of the six successors' proof modules; four theorem statements and the entry type of `mechanism/lean/Topak/`; the `Entry`
enum and the workflow grant arm of the Rust. Counts are `grep` over the tree and say how often a construct is
written. The other modules were placed from their `spec/README.md` rows and were not opened. §5 lists what the
session's first three answers got wrong; §7 says what none of this shows.

**Short answer.**

1. **Nothing formal links one module to another, and the corpus says so of itself.** No `.tla` file outside
   `skills/` contains `INSTANCE`. ADR-0045 T-0045-28 reads "No refinement exists". The 11.19 assessment already
   records the absence as a choice (§0 and §1 there).
2. **Refinement and composition are one gap here, not two.** The modules are not components to be composed. Each
   is a slice of the same lease life cycle, restated with the guards one record is about. The composite already
   exists: `Mechanism.tla`. What is missing is the link from that composite to each slice.
3. **The composite has no checked property of its own.** It replays recorded traces and nothing else, and at this
   tree it is two entry kinds behind the code.
4. **The cost falls unevenly.** Safety invariants would carry across such a link if it were built. Six
   availability properties, four leads-to properties and the reachability witnesses would not, whatever is built,
   and would have to be stated again on the composite.
5. **The Lean models are that link, built for one slice.** They show its shape, what it finds, and how it goes
   stale.

---

## 1. What links exist between modules

Every link at `ffd02f1`, by kind. "Formal" means a checker or a prover reads it.

| Link | Where | Formal | What it carries |
|---|---|---|---|
| `EXTENDS` for shared definitions | `Anchor`, `BreakGlass`, `BreakGlass_A1` extend `RulesFloorBase` | yes | Definitions. No theorem crosses |
| `EXTENDS` for liveness | `Coupling_live`, `Emergency_live` extend their base module | yes | `SpecLImpliesSpec == SpecL => Spec` is proved (`Coupling_live_proof.tla:65`, `Emergency_live_proof.tla:136`) and the base theorems are carried by it (`BY SpecLImpliesSpec, UnreadBoundedAlways`). A refinement by the identity mapping, over the same variables |
| `EXTENDS` for replay | `ConfinementRefinement` extends `Mechanism`; `PaxosTrace` extends `Paxos` | yes, on traces | See §2 |
| Proof modules | each `*_proof.tla` extends the module it proves | yes | The module's own theorems |
| Successor | `Lease_A1`, `Confinement_A1`, `Workflow_A1`, `BreakGlass_A1`, `NonComposition_A1`, `RulesFloorNV_rev5` | no | A header sentence. No successor extends or instantiates its predecessor |
| Reliance stated in a header | `RunSeats.tla:14`: the one-seat rule "is its, and is not restated here"; `RunCoupling.tla:28`: the correlator "is Coupling.tla's and is not modeled"; `RunConfinement.tla:26`: "those conjuncts are Confinement_A1.tla's" | no | A premise the reader supplies |
| Restatement | `Emergency.tla` proves `ThinkerStillCoupled` (line 191) over coupling reduced to one Boolean, `obsLive` (line 77) | no | A second, smaller model of the neighbour, checked against nothing |
| Lean | `SeatsModel` refines `Seats`; `CouplingModel` is built on `SeatsModel`; `FloorRefinement` refines `FloorComposition` | yes, of models and re-encodings | §4 |

## 2. The modules are slices, and the composite already exists

**The slices overlap and their shapes differ.** `lease` is a function of seats in `Seats.tla:42` and
`RunSeats.tla:55`, and a function of principals in `Lease_A1.tla:55` and `Confinement_A1.tla:82`, with a different
record in each. `Seats` has three actions: `Grant`, `Act`, `EndRound`. `Lease_A1` has those and `Renew`, the fleet
fence and `RevokeLease`. `Confinement_A1` has them again with launch, appraisal and the verifier. A grant in the
running system is all of these at once: one step that must pass every slice's guard. So the modules cannot be
conjoined as written, and conjoining them was never the design.

**The corpus says what the modules are.** The theory of operation: "The per-property modules are not a
specification of the mechanism. Fourteen modules each check one property over its own small abstraction; nothing a
refinement could be *to* existed until `Mechanism.tla`" (`narrative/theory-of-operation.md`, line 2291).

**`Mechanism.tla` is the composite.** Its header: "the same rules the discriminating modules state (Lease_A1,
Seats, Observers, Coupling, RunCoupling, RunSeats) written once, operationally" (lines 14 to 15), with confinement,
labels, operators and the emergency seating as `apply` holds a replica to them. Three things limit it:

- **It has no behaviour of its own.** Its only specification is `TraceSpec` over the constants `InitState` and
  `Trace` (line 712). There is no free `Next`, no type invariant and no stated property but `TraceMatches`.
- **Its one link to a slice restates the slice.** `ConfinementRefinement.tla` gives the correspondence with
  `Confinement_A1` as a table in a comment and then writes four predicates of its own over `st`. No instance of
  `Confinement_A1` is formed, so nothing checks the four against the module's definitions.
- **It is behind the code.** `Apply` handles fourteen entry kinds. The Rust `Entry` enum has sixteen
  (`state.rs:367`): `WorkflowLoad` and `WorkflowGrant` are in neither `Mechanism.tla` nor `trace2tla.py`. G12 item
  56: "the self review's rerun matched 82 of 83 traces, the end-to-end workflow trace does not replay, and
  `tests/workflow.rs` is not traced."

So the question the custodian asked twice has one answer. With slices of this kind, "the modules hold together"
and "the composite refines each module" are the same statement, and `proof-method.md:209` already names it: for
`Mechanism`, "the meaningful target is a refinement from it to the small modules".

## 3. What the absence costs

1. **Every theorem is of a slice.** `Spec => []P` is proved of `Seats`, of `Lease_A1`, of `Coupling`, each alone.
   That the system these describe keeps all the `P` together is argued in the records and tested by the suites. It
   is not checked or proved of any model. This is part of T-0045-28 and not beside it: that row's premise, "The code
   admits exactly what the checked modules admit", has the modules in the plural with nothing joining them.
2. **The composite could be wrong where no test goes.** With no free `Next`, no state of `Mechanism.tla` is examined
   except those a recorded trace reaches.
3. **Some properties would not carry even over a finished link.** *(The assistant's inference; no file in the tree
   states it.)* A slice's safety invariant survives more guards on an action, because more guards only remove
   behaviours. Three kinds of property do not:
   - the six stated over `ENABLED`: `ConsultNeverCoupled` (`RunCoupling.tla:162`), `LagNeverGates`
     (`Correlator.tla:302`), `DenyAlwaysAvailable` (`Operators.tla:248`), `EmergencyNeverCoupled` and
     `EmergencyCallsWithoutObserver` (`Emergency_live.tla:80`, `:82`), `FenceFailsWorkflow` (`Workflow_A1.tla:378`).
     Each says some step stays possible. Another slice's guard on the same step can make it false;
   - the four leads-to properties of `Coupling_live.tla` (lines 149 to 156), for the same reason, and because the
     fairness they assume is stated for one slice;
   - the 226 `Never…` witnesses in the 42 specification modules. Each shows a state reachable in its own slice, and
     says nothing about whether the composite can reach it.
   These are the claims that something is available, and they are where a composite check would find the most.
4. **Reliance between slices rests on the reader.** The header sentences and the restatement of §1 are premises no
   tool sees. `Emergency.tla`'s one Boolean is right only if it abstracts `Coupling.tla` faithfully, and nothing
   compares the two.
5. **A successor inherits nothing.** None of the six is a narrowing of its predecessor, by their own headers:

   | Successor | What changed | Kind |
   |---|---|---|
   | `Lease_A1` | Renewal keeps the rung; rungs run 0 to 3 where the frozen module stopped at 2 (`Lease.tla:37`, `Lease_A1.tla:46`) | narrows an action and widens a domain |
   | `Confinement_A1` | `Evidence` at rung 0 reads the profile the launcher was asked for, as rung 1 did, and not a measurement | changes a definition |
   | `Workflow_A1` | A fenced epoch is a new cause for `Settle` to fail the workflow | widens an action, to remove a stall |
   | `BreakGlass_A1`, `NonComposition_A1` | X1 replaced by the emergency seating | remodelled |
   | `RulesFloorNV_rev5` | R3 withdrawn, R9 added, quorum a threshold | remodelled |

   So a theorem `Successor!Spec => Predecessor!Spec` would be false for most of them. What the corpus does instead
   is prove each successor again, and all six have proof modules. What is missing is a stated difference: which
   behaviours of the predecessor are gone and which are new.
6. **The obligation has no line of its own in a record.** ADR-0033's chain has three items: trace validation, "a
   Lean model with differential testing" and "its compilation" (`decisions/ADR-0033.md`, line 1149). The link from the
   composite to the slices is named in `proof-method.md:209`, in ADR-0046's open obligations (line 449) and as step
   2 of the 11.04 paper (line 524), which is derived. *(Found by a search of `decisions/` for five patterns; a
   record that words it otherwise was not found and may exist.)*

**What it does not cost.** Each module's own results stand. `bundle ⊑ floor` holds by construction (ADR-0030 §1).
The two modules that model a combination whole, `NonComposition` and `FloorComposition`, are unaffected.

## 4. What the Rust-to-Lean models show

`mechanism/lean/Topak/SeatsModel.lean` is the composite-to-slice link, built once and proved.

- **Its shape.** A model of `State::apply` over the code's own fields; the code's action kinds read as the four
  variants `Seats` has; every check outside those fields one Boolean, `ok`, that can only refuse. `step_refines`
  (line 885) proves each model step is a run of `Seats.Next` steps, `Steps` being the reflexive and transitive
  closure (line 788), since one revocation ends several leases. `model_refines_seats` (line 1011) maps every state
  the model reaches to one `Seats` reaches, at the module's constants, and `model_seats_safe` (line 1029) reads
  `Seats`' proved invariants off it.
- **A slice need not be an abstraction of the code.** `CouplingModel.lean` proves `UnreadBounded` of its model
  directly. Its README: "A refinement would need history the code does not keep." `Coupling.tla` keeps a seal for
  every round; the code keeps the last.
- **Building the link found what the slices could not.** ADR-0053's findings 7 (the model omitted an effect and
  every proof still held; the replay found it), 8 (an issuance may change a seat's kind, which `Seats`' constants
  forbid), 10 (with several Observers the bound holds only of what none has read) and 11 (`Observers.tla`'s
  findings "are not in `apply`").
- **The oracle is the argument for the other mechanisms, and it rests on a list.** "Everything else is `other`: it
  touches none of the model's fields" (`SeatsModel.lean:127`), and the replay maps every kind it does not name to
  `other` (`SeatsReplay.lean:133`). That was true at the commit the model was written against. Two days later
  `Entry::WorkflowGrant` was added, and its arm calls `apply_grant` (`workflow.rs:1069`), which writes the leases.
  No file under `mechanism/lean/` or `spec/lean/` contains `Workflow`. The model's `state.rs` is `25eeeeb3830ee9f8`
  in `SeatsReplay-results-2026.10.06.txt`, and the file is `e6a927a19935e329` now.
- **There are two composites and no link between them.** `Mechanism.tla` in TLA+ and the two Lean models were each
  written from `state.rs` by hand. They agree, where they do, because each replayed the 82 traces of the same six
  suites.

What it informs: the link can be built, slice by slice; it is worth building for what it finds; and whichever
composite is chosen needs a check that fails when the code grows an arm.

## 5. Corrections to the session's first three answers

| Said | What the sources say |
|---|---|
| "`Workflow_A1` has none yet" (no proof) | `Workflow_A1_proof.tla` is proved, 1,169 obligations, and its certified run of 2026.11.20 leaves 12 temporal steps to LS4. The answer followed line 38 of `spec/README.md`, which still says "Not yet proved"; lines 95 and 197 of the same file say it is proved. The row at line 38 is stale |
| "`NonComposition` is the one deliberate exception" | `FloorComposition` models a combination whole too, and `Emergency`, `Lease_A1` and `Confinement_A1` each restate a neighbour (§1, §2) |
| "Every theorem assumes its mechanism runs alone", with interference between mechanisms as the risk | The modules are overlapping slices, not parallel mechanisms. The missing obligation is the projection of §2 |
| Trace validation: 82 traces, 1,007 steps, all matching | The 2026.10.05 results file. At G12, 82 of 83 match (item 56; register L-8, whose driver exits 0 with the ERROR row) |
| Compose by mapping the four `lease` variables onto one shared state | They are keyed differently and hold different records (§2) |
| Prove `M_A1!Spec => M!Spec` "wherever the change is a pure narrowing" | No successor is a pure narrowing (§3 item 5) |
| No refinement between modules in TLA+ | One, by the identity mapping: `SpecL => Spec` (§1) |
| The Lean model covers interference on the lease fields | At its own commit. Not at this tree (§4) |
| "The cheapest route is TLAPS, not TLC" | The 11.04 paper puts a refinement mapping checked by TLC at small constants first, and nothing read here argues against that order |
| Not said | The 11.04, 11.06 and 11.19 derived documents and the narrative's own sentence (§2) had already covered much of this ground; the first three answers read none of them |

## 6. What follows

Nothing here asks for a record. In the order the sources suggest:

1. Bring `Mechanism.tla` and `trace2tla.py` up to the workflow entries, trace `tests/workflow.rs`, and make the
   driver's exit status report a trace that does not replay (G12 item 56; L-8). Correct line 38 of `spec/README.md`.
2. Give the composite a free `Next` in a module that extends it, so its states can be checked and not only replayed.
3. Check the composite against `Seats`, `Lease_A1` and `Coupling` by a mapping, at small constants, with the
   module instantiated and not restated (the 11.04 paper's step 2; the 11.19 assessment's §5 item 2).
4. State the six `ENABLED` properties and the witnesses again on the composite.
5. For each successor, state what differs from its predecessor.

A plan for these was drafted in the same session. It is not in the tree at this commit.

## 7. What this does not show

- **Nothing was run.** Every count is of text. The trace figures are G12's and the register's, not a rerun. Whether
  a replay of a workflow grant through the Lean model fails, as its definition implies, was not tried.
- **Most modules were not opened.** Sixteen of 42 specification modules were read at their headers, and single
  lines of five more by `grep`. The eight command-chain modules, `Observers`, `Labels`, `ToolList`, `Mesh`, the
  frozen predecessors and the bodies of `Paxos`, `Operators` and `Correlator` were not, so §1's table may miss a
  reliance stated in one of them.
- **§3 item 3 is an argument, not a finding.** No property is shown to fail on the composite. The claim is that
  nothing shows it holds.
- **Three of the sources are derived documents the assistant wrote**, and agreement with them is not independence.
- **The re-read is not a second reader.** It was the same assistant under another model, in the same session, with
  the first answers in view. It caught what §5 lists. What both missed is not listed anywhere.
