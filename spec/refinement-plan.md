# Linking the specification modules: a plan for composition and refinement

**2026.11.21** · a plan for linking `Mechanism.tla` to the per-property modules, the successors to their
predecessors, and the mechanism's components to each other · DRAFT, revised as its steps are done

**What this is.** A plan, not a record and not yet a method note. No step of it is built except where one is marked
done, nothing here is ratified, and every size is a guess. It answers the findings of
`derived/topak-module-refinement-and-composition-2026.11.21.md` ("the write-up" below) and was prepared by the
assistant at the custodian's request, against the tree at `ffd02f1`. The custodian asked that each step note where
it differs from standard or best practice and where it is unique to TOPAK's choices. The state of record for the
work it plans is the checkpoint's open list (G12 item 56), not this file.

**How it is kept.** It was first committed as an undated draft under `derived/` (`32958b0`) and moved here the same
day at the custodian's request: a derived document is frozen once it is on `main`, and this one is meant to change.
A step that is done is marked done where it stands, with the commit. A later revision adds a dated note under the
step it changes and does not rewrite what was planned, as `proof-method.md` does with its assessments.

**How to read the two notes on each step.** *Standard practice* says what the published TLA+ and verification
practice does at that point and whether this plan follows it. *TOPAK's choice* says what in the step exists only
because of a decision this corpus made. The practice statements are from the drafter's knowledge of the literature
named in §9. None of it was re-read in this session, so each is a claim to check, not a citation. The corpus's
sourced survey of the code-to-model side is the 11.04 options paper, and this plan does not redo it.

---

## 0. In one paragraph

Do not compose the small modules. They are slices of one life cycle, their variables do not line up, and a composite
already exists: `Mechanism.tla`. Bring that composite up to the code, let it run freely so it can be checked, and
then link it to each slice by an instance and a mapping, checked by TLC at small constants with mutants that must
fail. State again on the composite the properties no mapping can carry. Say what each successor changed. Name the
three places where there is a real boundary between components and write the assumption each side makes. Decide
which of the two hand-written composites, the TLA+ one or the Lean one, is the one of record. None of this removes
T-0045-28. It replaces "nothing joins the modules" with a checked link, and it gives the code-to-model work one
target instead of thirty.

## 1. The four joints

| | Joint | State at `ffd02f1` | This plan |
|---|---|---|---|
| J1 | Composite to slice: `Mechanism.tla` to each per-property module | One, on traces, with the slice restated (`ConfinementRefinement.tla`); one in Lean, of a model (`SeatsModel.lean`) | Steps 1 to 3, 6 |
| J2 | Successor to predecessor | A header sentence | Step 4 |
| J3 | Component to component: the log to `apply`; the admit decision to `apply`; issuance to `apply`; Build to Run | A sentence in `Mechanism.tla`'s header ("Not modelled: … the Paxos log itself (entries arrive in index order)") | Step 5 |
| J4 | Code to composite: T-0045-28 itself | Trace validation, 82 of 83 at G12; two Lean models, stale | Not here. The 11.04 paper's order stands; Steps 1 and 6 feed it |

## 1a. What `INSTANCE` is, and what it buys alone

*Added 2026.11.21, after the custodian asked what it means that no module has an `INSTANCE`, and whether having
one would change anything without composition and refinement.*

**What it is.** `EXTENDS` copies a module in as written: the same names and the same variables. `INSTANCE Foo WITH
x <- e` imports `Foo` with the instancing module's own expressions in place of `Foo`'s constants and variables, and
every definition and theorem of `Foo` is then read under that substitution, as `M!Next`, `M!Spec` and so on.

**What its absence means here.**

- **No module speaks of another module's specification over its own state.** `INSTANCE` is the only way in TLA+ to
  write "that module's `Spec`, read over my variables". With `EXTENDS` the variables are the same ones and nothing
  is substituted, which is why the one theorem that crosses modules is `SpecLImpliesSpec == SpecL => Spec`
  (`Coupling_live_proof.tla:65`, `Emergency_live_proof.tla:136`).
- **Nothing is reused by parameter.** What is shared is written again: `RunSeats` has `Seats`' shape with a domain
  added, and `ConfinementRefinement` writes four of `Confinement_A1`'s predicates by hand.
- **It is a count, not the gap.** The corpus has refinement without the keyword: `SeatsModel.lean` states its
  mapping as a function, `abs`, and `SpecL => Spec` needs only `EXTENDS`. What is missing is the claims of §1, and
  zero `INSTANCE` is how their absence shows in a search.

**What an instance gives with no refinement or composition claimed.** Three things:

1. **One definition in place of copies.** A check uses the module's own predicate, so a restatement cannot drift
   from what it restates.
2. **The mapping written down and checked for form.** A `WITH` clause must give a value to every constant and
   variable of the module it instances. Writing one forces the questions of Step 2: `lease` is a function of seats
   in one module and of principals in another, and the code keeps no `acted`.
3. **Theorems reused across constants.** A module proved once can be instanced for Build and again for Run, and
   its theorems hold of each instance where its assumptions do.

A sketch of the first two, in a module that extends the composite, with the second line checked as an invariant.
The mapping's name is invented and nothing here was parsed or checked:

```tla
C == INSTANCE Confinement_A1 WITH lease <- LeaseByPrincipal(st), Mut <- "none"   \* and every other name
NoSilentDowngradeHere == C!NoSilentDowngrade   \* the module's own predicate, read over the mechanism's state
```

**What it does not give.** No proved theorem crosses an instance by itself. `Confinement_A1`'s invariants are
proved of the states its own `Next` reaches. An instance lets the invariant be *stated* over the mechanism's state;
it must still be *checked* there, as the trace replay checks its four predicates now. To carry the proof across
takes the further claim that every step of the mechanism maps to a step of `Confinement_A1`, and that claim is
refinement. So in Step 2's table, grade (a) is an instance alone, and grades (b) and (c) are the refinement.

It does not make the six `ENABLED` properties readable over the composite either. Substitution for variables does
not distribute over `ENABLED` *(the drafter's recollection of Specifying Systems; to check)*, which is one more
reason Step 3 states them afresh.

- *Standard practice.* `INSTANCE` is the ordinary instrument for reuse and for refinement alike, and one module
  instanced twice is the usual way to write "one component instantiated twice". A development of this size with no
  instance at all is unusual.
- *TOPAK's choice.* It was left out to keep the proofs cheap: `proof-method.md` §5 names "no `INSTANCE`, no
  refinement mapping" among the reasons, and the `writing-tla-specs-and-proofs` skill puts refinement mappings out
  of its scope. The freezing rule does not stand in the way of an instance, which edits nothing. It does stand in
  the way of folding `Seats` and `RunSeats` into one parameterized module: that would be a successor, with its own
  proof.

## 2. Step 0: preconditions

1. **Bring the composite up to the code.** Model `WorkflowLoad` and `WorkflowGrant` in `Mechanism.tla` and
   `trace2tla.py`, trace `tests/workflow.rs`, rerun (G12 item 56).
2. **Make the replay driver fail.** Its exit status is 0 with an ERROR row (register L-8).
3. **Done at `18d2e61`.** Line 38 of `spec/README.md` said `Workflow_A1` was not yet proved; it now points at the
   proof module.
4. **Answer Q1 (§10)**: which composite is of record. Steps 1 to 3 assume the TLA+ one.

- *Standard practice.* Nothing to note: a model that is validated against code is kept in step with it. As the
  drafter recalls them, the MongoDB report describes what keeping the two in step cost, and the CCF one runs its
  replay in continuous integration.
- *TOPAK's choice.* `Mechanism.tla` is "pinned, not frozen", so it may be edited where a slice may not; its digest
  is printed in every trace results file, so an edit means a new results file from the generator.

Size: days.

**Note, 2026.11.21: the size, estimated.** *Added at the custodian's request.* About four working days, with a range
of three to five, for an assistant drafting and the custodian reviewing, as the corpus has worked so far. It is a
judgement from sizes read in the tree at `e0f49ef`, not a measurement, and it replaces "days" above without
striking it.

| Part | Work | Estimate |
|---|---|---|
| Record the workflow state | `trace.rs` writes the two workflow entries as their kind and id only (lines 488 to 489), and the projected state has no workflow fields. Add both, and add the `traced` helper the other suites have to `tests/workflow.rs`: 18 tests, none traced | 0.5 to 1 day |
| Model it in `Mechanism.tla` | `WorkflowLoad`, `WorkflowGrant`, the advance that follows every applied entry once a workflow is loaded (`state.rs:931`), and the three hooks in the admit arm (`state.rs:1599`, `:1697`, `:1747`) | 1.5 to 3 days |
| Replay until it matches | Rerun every trace, correct the model where a step differs, regenerate the results file | 0.5 to 1 day |
| Make the driver fail (item 2) | `mechanism-trace-run.sh` ends in an unconditional `exit 0` | under an hour |
| Q1 (item 4) | The custodian's. Not counted | |

*What it rests on.*

- **Earlier catch-ups were quick.** `Mechanism.tla` has five dated results files from 2026.09.30 to 2026.10.05: it
  was brought up to the code four times in six days. The largest, on 2026.10.05, added 258 lines for labels,
  operators and the emergency seating.
- **This one is larger and of another kind.** `workflow.rs` is 1,381 lines, about 800 of them on the `apply` side.
  At the model's present ratio, 720 lines for the fourteen kinds it handles, that is 400 to 550 new lines: about
  twice the largest earlier catch-up.
- **It touches every arm.** The advance runs after every applied entry, so every existing replay path changes and
  not only the two new kinds.

*What would take it past a week.*

- **The graph.** `Workflow.tla` models one small fixed graph. The operational model needs joins, dead edges and
  guard evaluation for whatever graph a test loads.
- **A real divergence.** The first Lean replay failed 25 of 58 traces (ADR-0053 finding 7). A step that differs
  because the code and the intended rule disagree is a finding for a record, and stops being modelling.
- **The checks at load.** The estimate takes a definition's parse and its cycle and dominator checks as a trusted
  input of the trace, as a profile's parse already is. Modelling them adds one to two days.

*What it leaves out.* The ADR-0033 addendum that would cite the new results; the Lean replays, which Step 6 brings
up to the workflow entries; anything on `main`. One signal is unread: the item has been open since 2026.10.08 and
was carried through G11 and G12, which may mean it is harder than these sizes suggest, or only that it was not the
priority.

**Note, 2026.11.21: items 1 and 2 are done**, at `b46ed37`, with the run in
`Mechanism-trace-results-2026.11.21.txt`. Item 4 is open.

*What was done.* `Mechanism.tla` models the workflow engine as `apply` runs it, 720 lines grown to 1,141: the two
entries, the advance after every entry, the admit's three hooks, and the three places outside workflows where the
code had moved (an orchestrator seat is coupled, `Route` is an effect, a finding is checked under the variant it
arrived as). `trace.rs` projects the workflow entries, the loaded workflows and the bindings. The generator traces
the core's and the floor's `tests/workflow.rs`. The driver exits 1 on a trace that is not a MATCH, and the generator
on that or on a suite that records nothing. `trace2tla.py` needed no change. The module is re-pinned in
`mechanism/corpus-pins.sha256`.

*The run.* **Checked**: 106 traces, 1,716 steps, every step matching, every state keeping
`ConfinementRefinement.tla`'s four predicates. Rerun first at the tree as it stood, the old generator gave what G12
item 56 records: 83 traces, 82 matching, and an exit status of 0. The 23 new traces are the workflow suites', and
the end-to-end workflow trace that did not replay now does.

*A control.* Twenty-seven mutants of the new part of the model, one rule changed in each, were replayed in a
scratch copy, as the Lean mutants were; they are not an artefact. All were run against the core suite's 19 workflow
traces, and those no trace caught against the floor's four and the end-to-end one as well. Eighteen are caught.
Nine are not, by any of the 24, and each names something the traces do not show:

| Mutant | The rule changed | Why no trace sees it |
|---|---|---|
| The routing rule dropped | A tainted read no longer disables an edge into an outward node | The tests' tainted routes are refused at decide, so no entry reaches `apply` |
| No failure of a dead decision event | An open event with no chosen edge left stays open | No trace has one |
| An `any` join entered twice | A second edge into an entered node makes a second activation | In the tests' graph one of the two branches is always skipped |
| No wait at a grant | A slot is granted while its seat is busy or its last round unread | No trace orders such a grant |
| Any grant taken as the seating's | The ordered grant is not compared with the one the slot is entitled to | No trace orders a different one |
| An orchestrator's route not coupled | A route needs no live cell Observer at apply | No trace applies a route without one |
| No epoch check at a grant | A grant after a fence is not failed there | The advance has already failed the workflow |
| A route's stamp not checked | Only the round's own binding is checked | The two agree unless an entry is forged |
| A report's outcome not checked | Any outcome is accepted at apply | An outcome outside the node's enum is refused at decide |

The first six are paths no test takes through `apply`. The last three are checks that another check shadows in
every trace. For all nine, the model's rule and the code's could differ and this run would not show it.

*What else the traces do not reach.* Read from the 24 traces: no `all` join, so no activation ever waits; no
guard but `true` and `outcome`, so `not`, `all`, `any`, `end`, `label` and `count` are never evaluated; no
per-node budget; no load with an outward set from the bundle; no node whose round ended any way but by its outcome.
The model has all of these and nothing has checked them against the code.

*What the estimate above got wrong.* It said about four days, and the work took one session. The engine is a
deterministic function in the shape the model already had, one operator for each function of the code; the parse
and the load checks were taken as trusted inputs, as the estimate assumed; the converter is generic; and the model
matched on its first replay, which the estimate, reasoning from the Lean model's first replay, did not expect. One
line of its table was wrong in the tree: `tests/workflow.rs` already named its traces, in `tests/support/wf.rs`.
What was missing was the generator running the suite.

*What it leaves.*

- **A required check that disagrees with this step.** `frozen-files` (rule F7) reports `spec/Mechanism.tla` as
  frozen, because ADR-0033 cites the digest it had. `spec/README.md` says of the same module "Pinned, not frozen:
  the operational model moves with the code", and the note on *TOPAK's choice* above followed it. The change is
  made in place, as the README has it and as the module was changed four times before the check existed. A pull
  request that carries it fails that check until the custodian labels it `frozen-override`, or the check learns
  the README's exception, or the custodian rules that the model should have been a successor module.
- **A record.** No ADR-0033 addendum cites the run; that is the custodian's. `mechanism/` has moved, so no
  reference manifest measures this tree.
- **More inputs.** The nine survivors and the unreached paths are an argument for the generated inputs of Step 1
  and of the 11.04 paper's step 1, replayed through the code as well as the model.
- **The Lean replays** cannot read a workflow trace: `Route`, `Finding` and the `orchestrator` seat kind are
  unknown to their parsers. They were stale before this (Step 6). The other 83 traces changed only by added fields.

## 3. Step 1: a composite that runs

A new module, here called `MechanismFree.tla`, that extends `Mechanism.tla` and edits nothing in it.

- **A generator.** One operator per entry kind, producing a finite set of entries over the seats and principals of
  a fixture taken from an existing test, with every trusted input the trace now supplies (`ok`, `sigOk`,
  `signOnOk`, `proofOk`, `approvers`) ranging over all its values. Indices increase by one.
- **A free `Next`**: any generated entry, applied by the module's own `Apply`, to a stated depth.
- **Rows.** A type invariant for the projected state, which the module does not have. The four predicates of
  `ConfinementRefinement.tla` as invariants of every generated behaviour. A witness per result kind, so the generator
  is shown to reach grants, admits, revocations and refusals. A line in the deadlock audit.
- **Evidence.** *Checked* to the stated depth at the fixture; *sampled* beyond it with `-simulate`, and said so.
- **Two by-products for J4.** The generated entry sequences can be replayed through the Rust `apply`, which is the
  11.04 paper's step 1 run in the other direction, and through the Lean replays (Step 6).

- *Standard practice.* This step moves TOPAK toward it. Published trace validation checks an implementation's traces
  against the specification that is itself model-checked, so what is verified of the specification is at least
  tested of the code. Here the validated model has never been model-checked: its only run is the replay.
- *TOPAK's choice.* `Apply` is a deterministic function whose unknowns are read from the trace as trusted inputs.
  Published trace validation usually leaves unlogged state nondeterministic and lets TLC search for a matching
  behaviour. TOPAK's form is stricter per step, and it makes this step simple: the trusted inputs become choices.
  The wrapper, in place of an edit, is the freezing habit applied to a module that is only pinned.

Size: one to two weeks, nearly all of it the generator. The state space is unmeasured.

**Note, 2026.11.21.** *Added with the note under Step 0.* The size above stands. As a split: a first useful run
over the six basic entry kinds (grant, renewal, admit, end of round, revocation, the fleet fence) is perhaps two to
three days; the other ten kinds, and bringing the state space within reach, are the rest.

## 4. Step 2: the composite against each slice

One new module per slice, extending `MechanismFree`. It adds the history variables the slice has and the composite
lacks, forms `S == INSTANCE <Slice> WITH …, Mut <- "none"`, and states the slice's own properties through `S`.
Nothing is restated.

**Three grades of check**, each a row with its expected verdict written before the run:

| Grade | Statement | What it shows |
|---|---|---|
| a | `INVARIANT S!Safe` | The slice's invariants hold on every mapped state the composite reaches |
| b | `PROPERTY [][S!Next \/ <closure>]_<S's variables>` | Every composite step is a slice step, a named finite run of slice steps, or no change. With (a)'s initial condition, every mapped reachable state is one the slice reaches, so the slice's *proved* invariants apply |
| c | `PROPERTY S!Spec` | Plain refinement, where no closure is needed |

**The closure.** One revocation, fence or issuance ends several leases; a slice's `EndRound` ends one. Three ways to
handle it: a stuttering variable in the wrapper that unfolds the step; a derived action defined in the wrapper with
a lemma that it is a run of the slice's steps, which is what `SeatsModel.lean`'s `Steps` and `endMany_steps` do; or
grade (a) alone. The plan takes the second.

**Three controls**, without which a passing row says little:

1. **A mutant composite must fail.** For each mutation of the slice that has a counterpart in the code (`M_SEAT`,
   `M_KIND`; `M_RENEW`, `M_FENCE`, `M_REVOKE`), a scratch copy of the composite with that check removed must violate
   the mapped property.
2. **The slice's witnesses must be violated through the mapping.** A mapping that sends every state to the slice's
   initial state passes grade (a) and (b). `S!Never…` rows on the composite rule it out.
3. **The generator's witnesses of Step 1** rule out a composite too constrained to reach anything.

**Order, with what the sources say to expect.**

| | Slice | Expect |
|---|---|---|
| 1 | `Seats` | The Lean model gives the mapping. History: `acted`. Two premises to state in the generator: no issuance changes a seat's kind (ADR-0053 finding 8), and indices increase (finding 9) |
| 2 | `RunSeats` | The same shape with a domain. With (1), this discharges the reliance `RunSeats.tla:14` states in prose |
| 3 | `Lease_A1` | Keyed by principal where the code is keyed by fence and seat. "The principal's live lease" is a function only where `OneSeatPerPrincipal` holds, so this mapping rests on `Seats`' theorem: the first dependency between slices to be written down. History: `prev`, `staleAdmitted`, `acted` |
| 4 | `Confinement_A1` | Replaces the four restated predicates. `ContainedMeansConfined` stays out, as the header says: it is about the image the host ran |
| 5 | `Coupling`, `RunCoupling` | The module keeps a seal per round and a freshness flag; the code keeps the last seal and reads freshness from a clock at decide. State `UnreadBounded` on the composite directly first, as the Lean did, and map only if that is cheap. Q5 first |
| 6 | `Observers` | ADR-0053 finding 11: its findings "are not in `apply`". Record that there is no counterpart; do not force a mapping |
| 7 | `Emergency`, `Operators`, `Labels` | Proposed records. After the accepted ones |

No counterpart in the composite, so no mapping: `FloorComposition` and `FloorRouting` (the decision; J3);
`RulesFloorNV_rev5`, `Anchor` and the break-glass modules (issuance; J3); `Correlator`, `ToolList`, `Mesh` and the
eight command-chain modules. *(The last group is placed from `spec/README.md`'s rows; the modules were not opened.)*

- *Standard practice.* The instrument is the textbook one: an instance with a substitution, the abstract
  specification checked as a property by TLC, then proved by step simulation. The plan departs from practice in
  four ways, and each is a weakness to hold in view:
  1. **Direction.** Practice writes the abstract specification first and refines downward, so the mapping exists by
     construction. This is a retrofit from an operational model written from the code to modules that were written
     for cheap proofs. Their flags, ghost sets and index sets were chosen for induction, not for being mapped onto.
  2. **Many targets.** Practice has one abstract specification per layer with its internal state hidden. Here there
     are a dozen targets, each with its ghost state exposed. A method built on stepwise refinement, Event-B's for
     instance, would have grown the composite one feature at a time, each step inheriting the invariants before it.
  3. **Safety only.** Practice aims at behaviour inclusion, with a stuttering variable where steps do not line up,
     and with liveness. The closure of grade (b) carries reachable states and nothing else: no action property and
     no liveness crosses it.
  4. **Checked, not proved**, at small constants and a depth bound.
- *TOPAK's choice.* The slices are frozen by digest, so none can be given a multi-lease action or a different key;
  every accommodation is on the composite's side or in a new file. A mutant and a witness on a refinement check are
  not common practice; they come from this corpus's rule that a check must be shown to discriminate (ADR-0026 §6)
  and from ADR-0053 finding 12, that an invariant cannot see a mapping that is too lax. `Mut <- "none"` is the one
  place the modules' mutation switch meets instantiation: the mapping is claimed of the unmutated slice only.

Size: a week for `Seats`, days for each slice of the same shape, unknown for `Coupling`.

## 5. Step 3: what no mapping carries

1. **The six `ENABLED` properties** (the write-up, §3 item 3). On the composite each becomes a state predicate with
   no `ENABLED` in it: for the entry the property is about, `Apply`'s result is not a rejection. Say with each what
   it leaves out: the composite does not model the decide path, so an availability claim that depends on the floor,
   the bundle or the clock is covered only as far as `apply`.
2. **The witnesses.** For each `Never…` of a slice with a counterpart, the same row on the free composite.
3. **Leads-to: not in this plan.** It needs fairness stated for the composite, and the 11.19 assessment (§5 item 1)
   orders the slice-level proofs first.

- *Standard practice.* Followed. Refinement preserves safety and does not preserve what remains possible, so
  possibility is stated again at each level or checked as deadlock freedom at the lowest.
- *TOPAK's choice.* Enabledness without `ENABLED` is available because `Apply` is a function. It also keeps these
  statements clear of the construct the first of tlapm's two known unsound cases concerns (ADR-0046 A2), should
  they ever be proved.

Size: days, after Step 1.

## 6. Step 4: what each successor changed

For `Lease_A1`, `Confinement_A1` and `Workflow_A1`, whose variables line up with their predecessors', a small
module that extends the successor, instantiates the predecessor under the same mutation, and has two kinds of row,
each with the verdict the successor's header implies written down before the run: `Old!Spec` as a property, where a
violation's counterexample is kept as the statement of what is new; and the same property under a restriction to
what the predecessor could express (rungs 0 to 2 for `Lease_A1`), expected to hold. `Confinement_A1`'s header says
its change showed under `M_HOST` at rung 0, so that row and the unmutated one are the two to predict. For
`BreakGlass_A1`, `NonComposition_A1` and `RulesFloorNV_rev5`, which remodel, one sentence in `spec/README.md`: a
successor by record, not by mapping.

- *Standard practice.* There is none to follow. Specifications are normally edited in place and re-verified, and
  version control holds what changed.
- *TOPAK's choice.* The whole step. A module cited by digest in an accepted record is frozen, so a change is a new
  module, and the relation between the two is otherwise a header comment.

Size: days.

## 7. Step 5: the real boundaries

Here, and only here, composition in the usual sense applies: two components, each correct under an assumption
about the other.

1. **The log to `apply`.** State the assumption `Mechanism.tla`'s header makes as a named predicate in the
   generator: one entry per index, indices increasing, a repeated id absorbed by `appliedIds`. On the other side,
   add to a wrapper of `Paxos.tla` the sequence each replica delivers and check that it satisfies the predicate and
   that two replicas' sequences agree where both are defined, from `Agreement`. Do the 11.19 assessment's
   `Paxos` to `Voting` instance first: it is the corpus's cheapest first instance and touches nothing frozen.
2. **The decision to `apply`.** "An Admit entry is already a decision" (`Mechanism.tla:58`). Name the assumption,
   that every `Admit` entry was a `Decide` step of `FloorComposition` that admitted, and bind it to the rows it
   already rests on: the replica set, and the call-site exclusivity the 11.04 paper names (§5 item 4). Not provable
   here; nameable.
3. **Issuance to `apply`.** The `ok` of an `Issue` entry stands for `validate_issuance`. Name it, against
   `RulesFloorNV_rev5`.
4. **Build to Run.** Q3.

- *Standard practice.* Followed, in the form practice prefers. The theory offers assume-guarantee specifications
  and a composition theorem. Lamport's own advice for a system one party specifies is to write the environment into
  one closed specification instead, and replicated state machines are layered exactly so: a log, and a
  deterministic machine that consumes it. The plan writes named assumptions into a closed composite and uses no
  `-+->`.
- *TOPAK's choice.* The replicas are crash-recovery by decision and the agents Byzantine (ADR-0033 §3), so agents
  appear as arbitrary entries, which the generator already is, and a forged admit is a row and not a theorem. Each
  assumption gets a premise row, which practice rarely keeps.

Size: a week for (1); (2) and (3) are a paragraph each and a custodian's decision on the rows.

## 8. Step 6: two composites, and proof

- **Cross-check the two models.** Replay `MechanismFree`'s generated behaviours through `SeatsReplay.lean` and
  `CouplingReplay.lean`, after they learn the workflow entries. It needs a converter from TLC's output to
  `trace.rs`'s format, the reverse of `trace2tla.py`. It is a differential test between two hand-written models,
  with no code in it.
- **Proof.** Do not prove a mapping in TLAPS until two are checked in TLC. Lean has the precedent and the closure
  already proved for `Seats`. A TLAPS step simulation over instantiated definitions has not been tried in this
  corpus, and whether the certified run's rules admit it is unknown.

- *Standard practice.* One composite and one proof system. Two unlinked operational models of one function is not
  a practice anyone recommends.
- *TOPAK's choice.* It follows from ADR-0053 taking Lean as a second deductive method beside TLAPS, each with its
  own fidelity premise.

**Accounting, throughout.** Every step ends in rows and a results file from a generator, with "checked",
"proved" or "sampled" as it was. Nothing enters `theorem-premise-binding.md` and nothing is called a stage of
ADR-0033's chain without a record. A candidate for the custodian: a derived premise beside `refines(Seats)` (ADR-0053
R7) for a composite-to-slice mapping, once one is proved. The `writing-tla-specs-and-proofs` skill puts refinement
mappings out of scope; write that method down after two mappings exist, from what was done.

## 9. Where the plan stands against practice, in one table

| | Published practice | This plan | Because TOPAK |
|---|---|---|---|
| Direction | Abstract first, refine downward | Retrofit upward from an operational model | wrote a module per record, for cheap inductive proofs |
| Abstraction | One specification per layer, internals hidden | A dozen slices, ghost state exposed, one mapping each; no single abstract `Contain` | treats the modules as discriminators, not as the specification (ToO §11.3) |
| Composition | One closed specification; assume-guarantee only at open boundaries | The same | — |
| Refinement relation | Behaviour inclusion with stuttering; liveness | Reachable states, through a closure; safety only | froze the slices, and its code ends many leases in a step |
| Evidence for a mapping | Model-checked or proved | Checked, with mutants that must fail and witnesses through the mapping | requires every check to discriminate |
| Trace validation | Against the model-checked specification, nondeterministic matching | Against a deterministic `Apply`, which Step 1 makes checkable | made the composite a function of trusted inputs |
| A changed specification | Edited in place | A successor and a stated difference | cites modules by digest |
| What remains possible | Stated again at each level | The same, without `ENABLED` | — |
| Proof systems | One | TLC and TLAPS, and Lean, with fidelity premises between | took a second deductive method |
| What a result is worth | Usually informal | A row with premises; no stage claimed without a record | keeps a trusted-base table |

Where the plan is *below* best practice by choice: there is no single abstract specification, nothing is proved by
it, and liveness is left out. Where it is *above* common practice: the controls on each mapping, and the accounting.

**The practice the notes lean on**, named so it can be checked: Lamport, *Specifying Systems* (2002), on
implementation by instance and on composing specifications; Abadi and Lamport, "The Existence of Refinement
Mappings" (1991) and "Conjoining Specifications" (1995); Lamport, "Composition: A Way to Make Proofs Harder" (1998);
Lamport and Merz, "Auxiliary Variables in TLA+" (2017); Lamport's Paxos, Voting and Consensus modules; Abrial,
*Modeling in Event-B* (2010); Hawblitzel et al., "IronFleet" (2015); Davis, Hirschhorn and Schvimer, "eXtreme
Modelling in Practice" (2020); Cirstea, Kuppe, Loillier and Merz, "Validating Traces of Distributed Programs Against
TLA+ Specifications" (2024); Howard et al., "Smart Casual Verification of the Confidential Consortium Framework"
(2025).

## 10. Questions for the custodian

- **Q1. Which composite is of record?** `Mechanism.tla`: every arm but workflows, checked by TLC, nothing proved.
  Or the Lean models: two slices, proved, most of `apply` behind one Boolean. The plan assumes the first and keeps
  the second as the proof route.
- **Q2. Where does J1 sit in ADR-0033's chain?** Its three items do not name it. An addendum could, or could say it
  is part of T-0045-28 and leave the chain as it is.
- **Q3. `Build(Contain) → Run(Contain)`.** The narrative calls the parentheses "a refinement boundary:
  specification conjunction plus existential hiding". No module states that. Either write `Contain` once and
  instantiate it twice, which is what "one component instantiated twice" says and what `Seats` and `RunSeats` do by
  copy, or reword the sentence. The narrative is the custodian's.
- **Q4. Is a mapping checked at small constants enough to cite**, as TLC's rows are, or does it wait for a proof?
- **Q5. The collective bound or the per-Observer one** (ADR-0053 finding 10), before `Coupling` is mapped.
- **Q6. A single abstract specification of `Contain`**, which is what practice would have started from: wanted
  later, or declined with the reason written down?

## 11. What this plan does not show

- **Feasibility is unmeasured.** No generator was written and no state space counted. `Mechanism.tla`'s state is a
  record of thirty-eight fields by its header's list, and a free run may not finish at any useful depth.
- **The expected results in §4 are read off the Lean work and the modules' headers**, not off a run. A mapping may
  fail for a reason no source mentions, which would be a finding.
- **It does not shorten T-0045-28.** A composite linked to every slice is still a model written by hand from the
  code.
- **The practice notes are the drafter's recollection** (§9), and a wrong one would mislabel a step as standard or
  as TOPAK's own.
- **Most of the specification modules were not opened** when this was drafted (sixteen of 42 were), so §4's table
  of slices is incomplete.
