# Linking the specification modules: a plan for composition and refinement

**UNDATED DRAFT** · derived · a plan offered, not a record · prepared by the assistant at the custodian's request ·
basis: the tree at `ffd02f1`, on branch `claude/loving-gauss-3q99gi`, and
`derived/topak-module-refinement-and-composition-2026.11.21.md` (the findings this plan answers; "the write-up"
below) · first drafted uncommitted, as the custodian asked; the custodian then asked for it committed as an undated
live document. It has no row in `derived/README.md`. It takes its date, its row and its freeze when the custodian
says it has settled, and until then it may change. Revised once before its first commit: Step 0 item 3 is done ·
nothing here is built, run or ratified, and every size is a guess.

> separately, draft an uncommitted plan for composition+refinement and note in the plan where it differs from
> standard or best practice and where it is unique to TOPAK's choices.
>
> commit the plan as an undated live doc

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

## 2. Step 0: preconditions

1. **Bring the composite up to the code.** Model `WorkflowLoad` and `WorkflowGrant` in `Mechanism.tla` and
   `trace2tla.py`, trace `tests/workflow.rs`, rerun (G12 item 56).
2. **Make the replay driver fail.** Its exit status is 0 with an ERROR row (register L-8).
3. **Done at `18d2e61`.** Line 38 of `spec/README.md` said `Workflow_A1` was not yet proved; it now points at the
   proof module.
4. **Answer Q1 (§8)**: which composite is of record. Steps 1 to 3 assume the TLA+ one.

- *Standard practice.* Nothing to note: a model that is validated against code is kept in step with it. As the
  drafter recalls them, the MongoDB report describes what keeping the two in step cost, and the CCF one runs its
  replay in continuous integration.
- *TOPAK's choice.* `Mechanism.tla` is "pinned, not frozen", so it may be edited where a slice may not; its digest
  is printed in every trace results file, so an edit means a new results file from the generator.

Size: days.

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
