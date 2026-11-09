<!-- AUTHORED · 2026-11-09 · plan, nothing built -->
# TOPAK — A staged plan for compiling TLA+ to Rust, with refinement

**2026.11.09** · derived · a plan for a tool that compiles the corpus's TLA+ modules to Rust and ties the Rust that
runs to them, read against G11, ADR-0053, ADR-0057 and the tree at `7771a8a` · prepared by Claude at the custodian's
request · nothing here is built, and no record is made

> Let's plan a staged approach to implementing a direct compilation refinement tool for TLA+ to Rust. Similar to
> c2rust? Lean 4 to Rust?

**Verdict:** the tool is worth building, in two halves that the word *refinement* covers at once, and the corpus
already holds every piece it needs except the compiler itself. The first half **compiles a module to a Rust crate**
that is the module's transition system, executable: its state, its actions as an enum, its successors, its
invariants and witnesses. The second half **ties the hand-written mechanism to that crate**, by a refinement
harness the tool generates and an abstraction map a person writes, so that the replay the corpus does today through
TLC and through Lean runs in-process, on every step, in `cargo test` and later on every replica. Neither half is a
verified compiler. Nothing in the ecosystem has one for Rust: Dafny's Rust backend is trusted, Lean's Rust backend is
an experimental fork, and c2rust is faithful by construction and checked by tests. What the corpus has instead,
and what the plan rests on, is **translation validation by state graph**: the method ADR-0053 R6 already uses for
the Lean encodings, in which TLC dumps the module's whole graph at its constants and the generated artifact must
reach the same states by the same steps with the same property values. A generated crate that passes it at the
module's constants is checked, not trusted, and the generator never enters the trusted base for that use. The
analogies hold in one way each: **c2rust** for the order of work, faithful first and idiomatic after, with an oracle
that catches every regression; **Lean 4 to Rust** for what the Rust is, an extraction from a proved artifact, with the
graph check standing where a verified backend would. The closest real prior art is **PGo**, which compiles Modular
PlusCal to Go and TLA+ at once, and whose central lesson, that the system and its environment must be separated
before anything compiles, the corpus has already taken in `Mechanism.tla`'s oracle split.

---

## 1. What the tool is

### 1.1 Two refinements, one generator

The request names a *compilation refinement tool*. Two relations answer to *refinement* here, and the tool serves
both:

| Refinement | From | To | What the tool does | ADR-0057 edge it produces |
|---|---|---|---|---|
| **Behavioural** | `State::apply` and the rest of the reference | a module (`Seats`, `Coupling`, `Mechanism`) | Generates the module as executable Rust and a harness that checks every concrete step is a module step or a stutter, under an abstraction map a person writes | *replayed* on recorded traces; *tested* under model-based exploration; *proved* if the generated Rust is extracted to Lean (§5, stage 4) |
| **Representational** | the generated crate, TLC-faithful (`BTreeSet`, `BTreeMap`, cloned records) | the same crate, idiomatic (enum-indexed arrays, bitsets, in-place updates) | Applies optimizing passes, each validated by the same graph check | *generated*, unchanged: the check is what makes the pass safe |

The first is the one ADR-0045 T-0045-28 is about: "the running code refines the checked specification" is a
trust-root row today, with trace validation as its stage 1 and two Lean models of `apply` as its first proved pieces,
each proved of a reading. The second is c2rust's order of work, and it exists so that the generated spec is fast
enough to run beside the mechanism, not only in a test.

### 1.2 The fragment: what TLC enumerates

TLA+ is not executable. TLC executes a fragment of it, by enumeration: finite constant sets, records, functions over
finite domains, `\E` and `\A` over finite sets, `EXCEPT`, `CASE`, `IF`, `CHOOSE` over a finite set, `Cardinality`,
`SUBSET` and `[S -> T]` over small sets, sequences, bounded naturals. **The compilable fragment is TLC's**, by
definition, and TLC's evaluator is the fragment's semantics. That choice has three consequences. The tool's oracle
is TLC, which the corpus pins and trusts for its results already. A module outside the fragment is one TLC could not
check, which the corpus has none of. And the conformance question is never "does the Rust mean what the TLA+
means" in the abstract, but "does it reach TLC's graph", which is decidable at the module's constants.

The corpus's modules sit well inside it. The twenty modules below, every one TLC checks, use no `INSTANCE`, no
`RECURSIVE`, no unbounded quantification, and `Sequences` in one module only:

| Module | Lines | Beyond sets, records, `EXCEPT`, `CASE`, `\E`/`\A` | Note |
|---|---|---|---|
| `Seats`, `FloorComposition`, `RunSeats`, `Anchor`, `BreakGlass`, `Coupling`, `Confinement`, `Confinement_A1`, `Emergency`, `Operators` | 55 to 320 | nothing | the first two have graphs, Lean mirrors and mechanism refinements already |
| `Observers`, `RulesFloorNV_rev5`, `FloorRouting`, `NonComposition`, `RulesFloorBase`, `Lease_A1` | 64 to 192 | `Cardinality`, `SUBSET` over small sets | `SUBSET` of a two- or three-element set enumerates |
| `Emergency_live` | 89 | `ENABLED` in two invariants | `ENABLED A` is "some successor under `A`", computable from the action's guard |
| `Labels`, `Workflow` | 267, 385 | one `CHOOSE` each: `CHOOSE x \in items : x.id = i`, `CHOOSE x \in Chosen : Enabled(x)` | the first is unique, the second is not (§4.3) |
| `Mechanism` | 720 | two `CHOOSE … : TRUE`, `Append`, `Len`, `:>`, `@@`, 55 `DOMAIN` | the stage-6 target; its functions are built from the trace, not enumerated |

`snooker-tla`'s `Snooker.tla` (349 lines, `Naturals`, `FiniteSets`, `WF_`, two `CHOOSE` with a unique selector) is
in the fragment too, and is the right second-domain pilot (§8).

### 1.3 Where it sits in the chain

The corpus has, from the top: records read by modules; modules checked by TLC and proved by TLAPS; Lean re-encodings
proved by the kernel and, for three modules, checked against TLC's graphs; Lean transcriptions and models of the code,
proved to refine encodings, replayed against recorded traces; and trace validation of the code through
`Mechanism.tla`. Every edge from a module to the code is *proved of a reading*, *replayed* or *trusted* (ADR-0057
§3). The tool adds an edge of type *generated* from each module to a crate, and moves the module-to-code edges from
readings by hand to checks by a tool whose output is itself checked. It does not touch the TLAPS or Lean proofs,
which stay canonical for what they prove.

---

## 2. The analogies, read against the corpus

| Prior art | Direction | What it establishes | How | Lesson taken here |
|---|---|---|---|---|
| **c2rust** (Immunant) | C → Rust | behaviour-preserving `unsafe` Rust, mirroring the C | faithful translation, then refactoring passes, with the project's own test suite as the regression oracle | Faithful first, idiomatic after (stages 2 then 5). The oracle must be strong: here it is the whole state graph, not a test suite. And the practitioners' finding that it is better to refactor the *source* toward the target than the output: here, the fragment and the runtime library are shaped for Rust and for Aeneas before the first module is compiled |
| **Lean 4 → Rust** | Lean → Rust | an executable extraction of a proved artifact | no official backend; an experimental fork of the compiler (`sdiehl/lean4`, `backend := .rust`) and a bytecode fork | The *shape* of the claim is right: the module is the proved artifact (TLAPS, Lean) and the Rust is extracted from it. What Lean lacks, a trusted or verified Rust backend, the graph check replaces at the module's constants |
| **Dafny → Rust** (Dafny 2025) | Dafny → Rust | readable, near-native-speed Rust | a backend in Dafny's trusted computing base; a verified route exists only through CakeML, not Rust | A Rust backend is *trusted*, whatever the source language. No plan here should promise a verified compiler |
| **PGo** (UBC; ASPLOS '23, OOPSLA '25 TraceLink) | Modular PlusCal → Go and TLA+ | an implementation and a model from one source, with trace validation of the implementation against the model | MPCal separates the system from its environment (archetypes, mapping macros); the compiler emits both; TraceLink links runtime traces back to the model | The one true predecessor. Its separation of system from environment is `Mechanism.tla`'s oracle split (the facts "taken from the trace rather than computed"), already made. PGo compiles an algorithmic language, PlusCal; this tool compiles the transition-system style the corpus writes, which is simpler to compile and harder to make efficient |
| **Aeneas**, **hax** (Charon) | Rust → Lean | pure functional Lean from Rust, for proof | active, used on SymCrypt and libsignal; extraction fails on generics, dynamic dispatch and external crates; toolchain drift across Lean versions is the reported friction | The route from *generated* to *proved* for the Rust the tool emits (stage 4): generated Rust is small and first-order and can be written in the fragment Aeneas extracts. ADR-0057 §11 already lists it as a "could" |
| **tla-connect**, Apalache, Quint | TLA+ → traces → Rust tests | model-based testing: spec-generated traces replayed against the implementation; implementation traces validated against the spec | an external checker generates the traces | Stage 3's cousin. A compiled spec removes the external checker: the oracle runs in-process, chooses actions itself, and can run on a replica, which a trace file cannot |
| **tlaplus-rs**, **tla-rust** | Rust DSL → TLA+; hand-written pairs | a Rust-like DSL compiled to TLA+; TLA+ beside Rust by hand | — | The opposite direction or no tool. Nothing found compiles TLA+ to Rust |

No tool was found that compiles TLA+ to Rust (sources in §9). The gap is real, and it is narrower than it looks: the
hard part of PGo, compiling an algorithm with processes and channels to a runtime, does not arise for a transition
system whose environment is already an oracle.

---

## 3. What the corpus already has

Every input the tool needs exists, and most of its checks do:

| Need | What exists | Where |
|---|---|---|
| A front end | SANY, in the tracked `tla2tools.jar`, exports the semantic tree as XML: `java -cp tools/tla2tools.jar tla2sany.xml.XMLExporter -o Seats.tla` ran today and produced 242 KB of resolved operators, levels and arities | `tools/tla2tools.jar` (pinned by digest, 2024-08-08 build); `tla2sany/xml/sany.xsd` inside it |
| The oracle | TLC's `-dump dot,actionlabels` of a module's whole graph under a wrapper that carries each property's value, and `dot2lines.py` reading it | `spec/lean/graph-check.sh`, `spec/lean/dot2lines.py`, `GraphCheckCore.lean` |
| The check's form | "every TLC edge a `Next` step, every `Next` step from a TLC state an edge or a stutter, the same initial states, every property TLC's value" | `spec/lean/README.md`; `GraphCheck-results-2026.10.07.txt`: eight graphs, 128 to 53,248 states |
| The projection of the code | `trace.rs` projects `State` into the shapes `Mechanism.tla` fixes, and `SeatsModel.lean` projects it into `Seats`'s | `mechanism/crates/topak-core/src/trace.rs`; `mechanism/lean/Topak/SeatsModel.lean` |
| Recorded behaviour | 82 traces, 1,014 steps, from six suites, replayed through TLC and through Lean | `spec/mechanism-trace-results.sh`, `mechanism/lean/seats-replay.sh` |
| An encoding target | The conventions a TLA+ module takes in Lean, stated once | `spec/lean/TopakSpec/Prelude.lean` |
| The oracle split | `Mechanism.tla`'s header: the facts the model takes from the trace rather than computing | `spec/Mechanism.tla` |
| Where results go | Dated results files, a sync script per method, derived premises in the binding | `spec/proof-sync.sh`, `tools/lean-sync.sh`, `spec/inventory.py`, ADR-0053 R7 |
| Where the tool's edges go | Eight edge types, the premise `edge(t, x → y)`, grades | ADR-0057 §3 to §5 (Proposed) |

What does not exist is the compiler, its runtime library, the Rust-side graph comparison, and the harness.

---

## 4. Design

### 4.1 Architecture

```text
 spec/<M>.tla ─SANY (jar)─▶ sany XML ─▶ IR: typed, first-order, TLC's fragment
                                          │
                 ┌────────────────────────┼─────────────────────────┐
                 ▼                        ▼                         ▼
     Rust, faithful (stage 2)   Rust, refined (stage 5)      Lean encoding + mirror (stage 4)
       crate <m>-spec             the same crate, passes        TopakSpec/<M>.lean, Mirror/<M>.lean
       on tla-rt                  on tla-rt                     on Prelude.lean
                 │                        │                         │
                 ▼                        ▼                         ▼
     explorer: BFS from Init, dump .lines ──▶ compare with TLC's dump ──▶ GenCheck-results-<date>.txt
                 │
                 ▼
     refinement harness (stage 3): trait Refines<M>, step checker, action chooser
       + a hand-written abstraction map from topak_core::State to <m>_spec::State
       ─▶ replay of recorded traces in cargo test · model-based exploration · a shadow on a replica (stage 6)
```

The tool is one Rust workspace, `tools/tla2rs/`, outside `mechanism/` so that the reference's `Cargo.lock` and its
pins do not move: a `tla2rs` binary (XML to IR to backends), a `tla-rt` library the generated crates depend on, and
`tla-explore`, the graph walker and comparer. Generated crates land beside their modules, `spec/gen/<m>-spec/`, each
carrying the digest of the module and of the generator that produced it, as the Lean results files carry theirs.

### 4.2 The IR and its types

TLC is untyped; Rust is not. The IR is the fragment with types inferred: a constant set of strings is an enum; a
record is a struct; `[S -> T]` over an enum domain is an array indexed by the enum, else a `BTreeMap`; a set of an
enum is a bitset, else a `BTreeSet`; `BOOLEAN` is `bool`; a bounded natural is `u64` with the bound a parameter;
`Seq(T)` is `Vec<T>`; a value that is a string in one branch and `"none"` in another is an `Option` (the corpus's
`NONE` convention, which the Lean encodings already read so). Inference fails where a variable takes two shapes;
there the module carries an annotation in Apalache's `\* @type:` syntax, which SANY passes through as a comment and
which the corpus's modules may later also hand to Apalache. **The generator refuses rather than guesses**: a module
with an uninferred type does not compile, and the diagnosis names the operator.

### 4.3 Semantics decisions, each made as TLC makes it

- **`Next` is a sum of actions.** Each disjunct of `Next`, with its bound parameters, is a variant of an `Action`
  enum: `Action::Grant { p, s }`, `Action::Act { s }`, `Action::EndRound { s }`. `step(&self, a: Action) ->
  Option<State>` is the action's guard and effect; `successors(&self) -> Vec<(Action, State)>` enumerates the
  parameters over their finite sets. The `Action` enum is the refinement interface: a concrete step is checked by
  naming the abstract action it claims to be.
- **Primed variables are assigned in TLC's order.** `x' = e` and `x' \in S` are assignments, the second
  enumerated; `UNCHANGED` is a copy; a conjunct that reads `x'` before it is assigned is an error, as in TLC.
- **Stuttering is dropped** in the generated step relation and allowed by the harness, as `Prelude.lean` does.
- **`Mut` is a constant**, so it is a field of a `Config` the crate takes at construction, as the Lean encodings
  take `m : Mut`; so are `K`, `R`, `MaxRound` and every constant a `.cfg` sets.
- **`CHOOSE x \in S : P(x)` with a unique `x`** compiles to a search and an assertion. **With a non-unique `x`**
  (`Mechanism.tla`'s two, `Workflow.tla`'s one) the result depends on TLC's enumeration order, which is by value
  and stable within a TLC version but not something the Rust should reproduce. The generator compiles it to the
  least element under the generated type's `Ord`, and the graph check tells whether the module's behaviour depends
  on which element was chosen: a mismatch there is a finding about the module, not the tool.
- **`ENABLED A`** is `successors` filtered to `A`, non-empty.
- **Liveness is out of scope.** `WF_`, `SF_`, `[]<>` and `~>` are not compiled; the harness checks safety steps and
  the explorer walks graphs. TLC keeps liveness, as it keeps witnesses under ADR-0046.

### 4.4 The runtime library, shaped for both targets

`tla-rt` holds the representations the faithful backend uses and the traits the refined backend specializes:
`Set<T>`, `Fun<K, V>`, `Record` derive macros, `Choose`, `Card`. It is written in the Rust that Aeneas extracts, no
generics beyond what Aeneas's standard-library model covers, no trait objects, no `unsafe`, so that stage 4 does
not begin with a rewrite. That is the c2rust lesson applied before the first line: shape the source for the targets.

---

## 5. The stages

Each stage names its exit criterion as a file the corpus can cite, and the edge type (ADR-0057 §3) the work reaches.
Effort is in custodian-days, as `topak-effort-estimate-2026.09.28.md` counts them; each is a range and an estimate.

### Stage 0 — Scope and record (2 to 3 days)

Fix the fragment as §1.2 states it, the two outputs as §1.1 states them, the location (`tools/tla2rs/`), the pilots
(`Seats` and `FloorComposition`, because they have TLC graphs, Lean mirrors and mechanism refinements already, so
every new result has a sibling to agree with) and the trusted-base position (§6). Draft a Proposed record in the form
of ADR-0053: the method declared, what a generated result claims and does not, how results are cited. **The corpus
does not cite a result of a method without a record** (ADR-0046, ADR-0053), so the record precedes the first cited
results file, though the code may precede the record. Exit: the record drafted; this note cited as its source.

### Stage 1 — Front end and IR (5 to 8 days)

`tla2rs parse <M>.tla`: run SANY's exporter from the pinned jar, read the XML, build the IR, infer types, report.
Exit: every module in §1.2's table parses to a typed IR or fails with the operator and reason named; a fragment
report per module is committed as `spec/gen/fragment-report-<date>.txt`. Risk: the XML exporter has known rough
edges around `INSTANCE … WITH` substitutions, which the corpus does not use; the `TLAPS` module the proof modules
extend is not parsed, since the tool reads base modules only.

### Stage 2 — The faithful backend and the graph check (8 to 12 days)

Generate `<m>-spec` for the pilots: `Config`, `State`, `Action`, `init() -> Vec<State>`, `step`, `successors`, one
`fn` per invariant and witness. `tla-explore` walks from `init` under each `Mut`, writes the graph in
`dot2lines.py`'s line format, and compares it with TLC's dump: the same four checks `GraphCheckCore.lean` makes.
Exit: `GenCheck-results-<date>.txt`, in the form of `GraphCheck-results-2026.10.07.txt`, with `Seats` under three
`Mut` and `FloorComposition` under five all MATCH at the same state and edge counts (6,656 to 53,248 states; 128 to
768). Then the other fourteen Lean-encoded modules under their `.cfg` constants, as a second series. A mutated
generator (an `EXCEPT` that forgets to copy, a guard dropped) must fail the check, as the mutated encodings did under
ADR-0053 R6: three such mutations, each caught, go in the results file. **Edge reached: *generated*, checked at the
module's constants.** What this is worth on its own: a second, independent evaluator of every module, in a language
the mechanism's authors read, with TLC's graph as the referee between them.

### Stage 3 — The refinement harness (8 to 12 days)

Generate, per module, `trait Refines<M> { fn abstract(&self) -> M::State; }` and a checker: given a concrete state
before and after a step and the `Action` it claims, assert `abstract(before).step(action) == Some(abstract(after))`
or that the abstraction did not move. Write by hand, in `topak-core`'s tests, the abstraction map from `State` to
`seats_spec::State`, following `SeatsModel.lean`'s projection and `trace.rs`'s, and the map from `Entry` and
`Applied` to `Action`. Drive it two ways:

1. **Replay.** The six traced suites run with a `Refines<Seats>` check on every `apply`, in-process, no JSONL and no
   TLC: the replay `seats-replay.sh` does in Lean, in `cargo test`. Exit: the same 82 traces and 1,014 steps match;
   a copy of `state.rs` without ADR-0037 §1's check fails at the grant it lets through, as it fails the Lean replay.
2. **Exploration.** A driver chooses `Action`s from `successors` of the abstract state, builds the concrete entry
   for each, applies it, and checks the step; a bounded random walk and a bounded exhaustive one. This is the
   "downward complement of replay" ADR-0057 §11 names as a *could*: the paths no recorded trace reached. Exit: the
   same mutation is caught with no recorded trace; a second, chosen for a path the suites do not take, is caught.

**Edge reached: *replayed* for the traces, *tested* for the exploration.** The grade does not rise above what the
corpus has; the cost of keeping it falls, and the coverage of the tested edge is measured by the explorer, not by
which tests someone wrote. This is also where the `Coupling` model's checks move into Rust.

### Stage 4 — The same IR to Lean, and the generated Rust to Lean (10 to 15 days, with Aeneas the uncertain part)

Emit `TopakSpec/<M>.lean` and `Mirror/<M>.lean` from the IR under `Prelude.lean`'s conventions, which are already
written as rules. Exit: the generated `Seats.lean` and `FloorComposition.lean` prove the existing theorems with their
existing proof scripts, or with scripts ported once; the `graph-check.sh` series passes on the generated mirrors.
**The module-to-encoding edge becomes *generated***: `enc-faithful(M)` stops being a reading and becomes one tool's
two backends agreeing with TLC's graph, which is higher in ADR-0057's order than *proved of a reading*. Then, as
the uncertain half: run Aeneas over `<m>-spec` and `tla-rt`, and prove in Lean that the extracted `step` equals the
generated encoding's `Next` on the mirror's states. If it goes through, **the generated Rust is *proved* equal to the
encoding**, and a mechanism theorem proved of a refinement of the generated crate rests on no reading at all between
the module and the Rust. If Aeneas refuses the crate, the stage ends with the first half, which stands alone.

### Stage 5 — Representational refinement (5 to 8 days)

Optimizing passes, each a transformation of the IR or of the backend's choices: enum-indexed arrays for functions,
bitsets for subsets of enums, in-place `EXCEPT`, guards evaluated before any clone, `successors` without allocation
where the action count is static. Each pass is switched on alone and the graph check rerun; a pass that changes a
graph is wrong. Exit: the second `GenCheck` series at every pass enabled, every graph MATCH, with the explorer's
wall time beside the faithful backend's. The point is stage 6: a spec that runs beside the mechanism must cost less
than the mechanism.

### Stage 6 — `Mechanism.tla` as a shadow, then as the source (15 to 25 days; needs a record)

`Mechanism.tla` is written as a function from a projected state and an entry to the next state and a result, with
the facts it does not compute taken from the trace. Compile it: `mechanism_spec::apply(state, entry, oracle) ->
(state, applied)`, the oracle a struct of the facts the header lists. Run it as a **shadow** on every `apply` of
every replica in the six suites, then in the node behind a flag: project, step, compare, as the trace validation does
after the fact, now before the next entry. Exit: every suite agrees at every step, continuously, and the
`Mechanism-trace-results` series is reproduced by the shadow. Then the inversion the stage is named for: for the
fields the module models, the generated `apply` *is* the apply, and the hand-written code becomes the oracle layer,
computing signatures, digests and the floor's answers, and performing effects. That is spec-as-source for the
replicated state machine, PGo's claim, and it is the one place where T-0045-28 moves: the route from module to
code becomes *generated* plus the oracle boundary, and the boundary is a list in the module's header. It touches a
pinned module and ADR-0033, so it needs its own record, and it is not to be started before stage 3 has run for a
while on the shadow.

### What the order buys

Stages 1 and 2 are the tool and are useful alone. Stage 3 is the refinement and is what the request asks for. Stage 4
raises the grade and is where the plan may stall on an outside tool. Stage 5 is c2rust's second phase and is only
needed for stage 6. Stage 6 is the prize and the risk. Stopping after any stage leaves a usable thing with a results
file.

---

## 6. The trusted base and the records

**The generator is not a trusted-base row for a checked use.** A generated crate used at the constants the graph
check ran at is checked exhaustively, and the generator's failure can only produce a crate that fails the check, as a
mutated encoding fails it under ADR-0053 R6. The rows that do enter are the ones already there: TLC for the dump
(T-0045-29's checker), and rustc, which `topak-core` already rests on. `tla-rt` enters as part of the generated
artifact, checked with it.

**It becomes a row, or needs the Aeneas route, for an unchecked use.** A generated monitor in a deployment at
constants no graph was dumped at, or a generated `apply` in stage 6 at the reference's sizes, runs where the check did
not. There the generator's correctness is a premise, and ADR-0045 §5's test applies: its failure can admit what the
module forbids, so it is a row, or the generated code is *proved* through stage 4 and the row is Lean's. The record of
stage 0 says which, per use.

**Results and sync.** Each generated crate carries the digests of its module, its generator and `tla-rt`; each
`GenCheck` results file lists them and TLC's jar; a `gen-sync.sh` in the form of `lean-sync.sh` fails when a digest
moves. Under ADR-0057 §4 each check is a premise `edge(generated, <m>-spec → M)`, true while fresh.

**Frozen or pinned.** A generated crate of a frozen module is regenerated only by a generator change, and the change
is a new results file; a crate of a pinned module (`Mechanism`) follows it as `mechanism/lean/` follows the code.

---

## 7. Risks, and what would stop the plan

| Risk | Where | What is done about it |
|---|---|---|
| TLC's dump is not the semantics: a Rust that agrees with TLC on every graph may still disagree with TLA+ where TLC is unusual (`CHOOSE` order, `Cardinality` of a set TLC cannot enumerate) | stages 2, 6 | The fragment is TLC's by definition (§1.2), and the corpus's claims about modules are TLC's and TLAPS's already; the Lean encodings agree with the same dumps |
| Type inference fails on a module written for TLC, not for types | stage 1 | Annotations in Apalache's syntax, refused rather than guessed; the fragment report says where |
| SANY's XML has gaps | stage 1 | None of the known ones (`INSTANCE … WITH`) occur in the corpus; a fallback is to read SANY's semantic tree from Java directly, in a small exporter of our own against the same jar |
| The exploration driver cannot build a concrete entry for every abstract action (signatures, digests, keys) | stage 3 | The oracle split: the driver uses the test suites' key material and `support/` builders, which already construct every entry kind |
| Aeneas refuses `tla-rt` or the generated crate | stage 4 | Shape `tla-rt` for it from stage 2; if it still refuses, the stage's first half stands and the grade stays *generated* |
| The shadow costs more than the apply | stage 6 | Stage 5 exists for this; the flag is off by default and the suites are the first place it runs |
| The generated `apply` and the hand-written one disagree on a field the module does not model | stage 6 | They can only disagree on modelled fields; the unmodelled ones stay with the hand-written code, as the header lists |
| One author, one tool, read by nobody else | all | The same as every method in the corpus (ADR-0057 finding 5); the graph check is what makes a reading unnecessary at the module's constants |

What would stop it: the type inference turning out to need annotations on most modules (then the fragment is not
TLC's but a typed subset, and the record must say so); or stage 2's check failing on a module for a reason that is
TLC's enumeration order, not a bug, in a way the module's properties depend on.

---

## 8. Suggested entries, none made

- **A Proposed record**, in ADR-0053's form, declaring the method: the fragment, the two outputs, what a generated
  result claims, the graph check as the fidelity check, the citation form, the row question of §6. Drafted at stage 0.
- **`tools/tla2rs/`**, a Rust workspace with `tla2rs`, `tla-rt` and `tla-explore`; `spec/gen/` for generated crates
  and `GenCheck-results-*.txt`; `spec/gen-sync.sh`.
- **ADR-0057 §11's table**: the rows "tests generated from the modules" and "monitors derived from the modules'
  invariants" move from *could* to *should*, and "Rust-to-Lean extraction in place of hand transcription" gains the
  generated route beside it, if the record is ratified.
- **`snooker-tla`** as the second-domain pilot after stage 2: `Snooker.tla` compiled to a crate, and `replay.sh`'s
  TLC replay of a recorded frame run in-process against the acquisition layer's shot events. It tests whether the
  fragment and the inference are general or shaped to this corpus, on a module written by the same hand but for a
  different kind of system, and it gives the feature plan's live referee an engine that is the specification.
- **G12's open list**: an item for the tool, cross-referenced to item 56 (trace validation behind the workflow
  build), which stage 6's shadow would close by construction.

---

## 9. Sources

Corpus: ADR-0033, ADR-0045 (T-0045-28, T-0045-29, T-0045-37), ADR-0046, ADR-0053 (§1, §2, R4 to R7),
ADR-0057 (§3 to §5, §11), ADR-0058; `spec/README.md`; `spec/lean/README.md` and `graph-check.sh`;
`mechanism/lean/README.md`, `SeatsModel.lean`, `seats-replay.sh`; `mechanism/crates/topak-core/src/trace.rs`;
`spec/Mechanism.tla`; `spec/trace2tla.py`; `derived/topak-lean-formalization-options-2026.10.05.md`;
`derived/topak-specification-graph-2026.11.06.md`; `skills/writing-tla-specs-and-proofs/`. The SANY export was run
today against the tracked jar.

Outside, read on 2026.11.09:
[c2rust](https://docs.rs/crate/c2rust/latest/source/README.md) and its
[manual](https://proxy-dev.blitzz.co/proxy/123456/c2rust.com/manual/);
[PGo (ASPLOS '23)](https://www.cs.ubc.ca/~bestchai/papers/asplos23-pgo.pdf),
[TraceLink (OOPSLA '25)](https://www.cs.ubc.ca/~bestchai/papers/oopsla25-trace-link.pdf),
[PGo at ETAPS 2025](https://conf.tlapl.us/2025-etaps/hackett-slides.pdf), [the project page](https://systopia.cs.ubc.ca/pgo);
[Performant, Readable and Interoperable Rust from Dafny (Dafny 2025)](https://popl25.sigplan.org/details/dafny-2025-papers/14/Performant-Readable-and-Interoperable-Rust-from-Dafny),
[a CakeML backend for Dafny](https://popl25.sigplan.org/details/dafny-2025-papers/3/Baking-for-Dafny-A-CakeML-Backend-for-Dafny),
[Dafny's trusted backends, as stated in arXiv:2510.24798](https://arxiv.org/pdf/2510.24798);
[sdiehl/lean4, an experimental Rust backend](https://github.com/sdiehl/lean4),
[sdiehl/lean4-rust](https://github.com/sdiehl/lean4-rust);
[Aeneas](https://lean-lang.org/use-cases/aeneas), [hax's Lean quick start](https://hax.cryspen.com/manual/lean/quick_start/),
[A Rust-to-Lean Verification Pipeline with AI Provers: An Experience Report (arXiv:2605.30106)](https://arxiv.org/abs/2605.30106),
[Runtime Verification on Rust to Lean](https://runtimeverification.com/blog/from-rust-source-code-to-mathematical-proof);
[tla-connect](https://docs.rs/tla-connect), [tlaplus-rs](https://github.com/drbh/tlaplus-rs), [tla-rust](https://github.com/spacejam/tla-rust);
[SANY's XML exporter, discussed on the TLA+ list](https://groups.google.com/g/tlaplus/c/TeC4hxNZIuM),
[the TLA+ tools' standalone use](https://lamport.azurewebsites.net/tla/standalone-tools.html),
[tree-sitter-tlaplus](https://docs.rs/crate/tree-sitter-tlaplus/1.2.3).
