# A diagram per TLA+ module: scope, starting with the floor and the seats (2026.11.26)

Derived. Plans a new diagram family; decides nothing. Where it and a record disagree, the record wins.

## Why

gov-tla draws each of its six modules on a diagram of its own (B1 `Constitution.tla` … B6 `SenateRules.tla`):
the module's actions as cards, and four tables anchored by name, `#mutations`, `#matrix`, `#witnesses`,
`#theorems`. Every name the module declares is anchored or linked to its line at the pin, and a module's file name
opens its diagram. A1 indexes them.

TOPAK's 58 diagrams are drawn by record and concept. A module appears as one row of H3 (41 modules), or as a panel
of a concept diagram (E2, E4; H8 for the eight overlay modules, the nearest thing to gov-tla's B diagrams). No
diagram draws a module's mutation matrix, witnesses and theorems together, and `Workflow_A1.tla` is drawn nowhere.

## The first batch: the floor and the seats

All seven modules are unchanged since September and match the digests their evidence cites (checked 2026.11.26).

| Module | Record | Status | TLC (named file) | TLAPS | Certified | Lean |
|---|---|---|---|---|---|---|
| `Seats.tla` | ADR-0037 §9 | Accepted (genesis), C3, C4 | `Seats-results-2026.09.29.txt`: 9 rows; `M_KIND`, `M_SEAT`; 3 witnesses | 3 theorems, 10 lemmas, 110 obligations | 107 + 3 on LS4 | `TopakSpec/Seats.lean`, `Mirror/Seats.lean` |
| `RunSeats.tla` | ADR-0043 §8 | Accepted (genesis), C4 | `RunSeats-results-2026.09.29.txt`: 14 rows; `M_KIND`, `M_DOMAIN`, `M_OBSEMIT` (ADR-0037 §4's provisional column) | 4 theorems, 16 lemmas, 147 obligations | 143 + 4 on LS4 | `TopakSpec/RunSeats.lean` |
| `FloorComposition.tla` | ADR-0030 §1, §3, §5 | Accepted (genesis), C1 | `FloorComposition-results-2026.09.24.txt`: 12 sections; `M_OVERRIDE`, `M_ERR`, `M_FAILOPEN`, `M_WRITE` | 6 theorems, 16 lemmas, 171 obligations | 165 + 6 on LS4 | `TopakSpec/FloorComposition.lean`, `Mirror/FloorComposition.lean` |
| `FloorRouting.tla` | ADR-0030 §5 | Accepted (genesis), C1 | the same file: its 6 `=== FloorRouting` sections; `M_ROUTE`, `M_GATE` | 3 theorems, 5 lemmas, 36 obligations | 33 + 3 on LS4 | `TopakSpec/FloorRouting.lean` |
| `RulesFloorNV_rev5.tla` | ADR-0026 §6–§7 | Accepted (genesis) | `RulesFloorNV-rev5-results-2026.09.23.txt`: 8 sections (base, reach, a dropped entry each, envrecuse) | 7 theorems, 20 lemmas, 262 obligations; `ASSUME ActiveEntries` | **NOT CERTIFIED**: Isabelle rejected 1 of Zenon's proofs | `TopakSpec/RulesFloorNV_rev5.lean` |
| `RulesFloorBase.tla` | ADR-0029 §5 | Accepted (genesis) | none: shared definitions, `EXTENDS`-ed by `Anchor`, `BreakGlass`, `BreakGlass_A1` | none | — | `TopakSpec/RulesFloorBase.lean`: `GenesisEntries`, `GenesisFloor` |
| `RulesFloorNV.tla` | ADR-0026 (G1 copy) | frozen, cited by digest | `RulesFloorNV-results-2026.09.15.txt`: 26 rows, no header | none | — | none |

Proof results are the files `*-proof-results-<date>.txt` and `*-proof-cert-results-<date>.txt`; Lean, 
`spec/lean/TopakSpec-results-2026.10.07.txt` (its `Transcribes:` digests match all six).

## What each diagram draws

gov-tla's layout, with two columns gov-tla has no evidence for (certification and Lean):

1. **Header.** Module, record and section, status pill (with its C markers), the module's sha256, the constants
   TLC ran at (the boundedness caveat, said as such).
2. **The machine.** Constants, variables, and one card per action, each linked to its line at the pin.
3. **Properties.** Each invariant, the record section it states, and its theorem.
4. **`#matrix`.** Mutation × property, HOLDS or COUNTEREXAMPLE, from the named results file, compared with the
   file's own `expected:` line; a disagreement is an `ERROR`, not a drawing.
5. **`#witnesses`.** The `Never…` rows: COUNTEREXAMPLE means reachable.
6. **`#theorems`.** Theorems and lemmas, the obligation count, and the certification line as the file states it,
   LS4 counted separately. On `RulesFloorNV_rev5` the NOT CERTIFIED line is drawn in red; nothing on that diagram
   says *certified*.
7. **Lean.** The transcription's theorems, and the Mirror equivalence where one exists.
8. **Where else it is drawn.** Links out to the concept diagrams that use the module (`Seats` is read by 20 of
   them; B4, B3, B8, C1, C2 are the main ones), so the module page and the concept page point at each other.

AUTHORING.md's rules hold as written: *proved*, *certified* and *checked* stay distinct, and every statement
traces to a record or a results file.

## How it is built

- **A reader, `diagrams/topak/src/modules.py`**, ported from gov-tla's `corpus.py`. It names the results file per
  module (never "the newest") and parses strictly, raising on any shape it does not expect. The floor and seats
  files come in three shapes, and it needs a reader for each:
  - *pipe with header*: `Seats`, `RunSeats` (`name | Mut=… | property | result | states`);
  - *pipe, no header*: `RulesFloorNV` 2026.09.15;
  - *raw TLC log in `=== ` sections*: `RulesFloorNV_rev5`, `FloorComposition` (with `FloorRouting`'s sections).

  The proof, cert and Lean files share one header shape, so one reader each covers all of them. The modules built
  since October have `-rows.txt` row lists, so later batches mostly use a fourth, standard reader.
- **One template, `d_i_module.py`**, drawing sections 1 and 3–7 from the reader, with hand-written prose and
  action cards per module (`d_i1_seats.py` …). gov-tla wrote each B generator by hand (820–1,440 lines). The
  tables here are uniform enough to generate; only the cards and prose need authoring.
- The usual family loop: Python 3.9 under uv, render light (rsvg) and dark (Chrome), the `--expect` regression
  check, the manifest's second run, `check-links.py`, `diagrams.yml` green.

## Phases

1. **Reader.** `modules.py` over the seven modules' files, failing loud on each. No diagrams yet.
2. **Pilot: `Seats.tla`.** Template plus I1, rendered in both themes, for review before the rest.
3. **The rest of the batch:** `RunSeats`, `FloorComposition`, `FloorRouting`, `RulesFloorNV_rev5`,
   `RulesFloorBase`.
4. **Knock-ons.** H3's rows link to their module diagrams. The README's link table, family table and counts are
   updated; the manifest is regenerated and run a second time; links are checked. Released as `diagrams-v0.2.0`
   (MINOR: new diagrams, and no drawing moves).

## Decisions for the custodian

**Decided 2026.11.26: all five as recommended** (the custodian). Phase 1 (the reader) and phase 2 (the `Seats.tla`
pilot, I1) are built on branch `module-diagrams` and committed (ec8777d). Phase 3 is built the same day: I1's mechanism picture, and I2 `RunSeats`, I3 `FloorComposition`, I4 `FloorRouting`, I5 `RulesFloorNV_rev5` and I6 `RulesFloorBase`, on shared bands (`modpage.py`). Phase 4 (H3's links, the module-file-name rule, the release) is next. For decision 3, the pilot changes no
other diagram's links yet. It adds the I family's local names (`lib.LOCAL_FAMILIES`, `MODULE_FILES`), and the
module-file-name rule lands with phase 4.

1. **Family letter.** I propose **I** (I1–I6), the next letter after H. gov-tla's B is taken here.
2. **Legacy TLC files.** Read them as they are, with the three readers above (recommended: accepted records cite
   these files by date), or backfill `-rows.txt` and rerun to the standard shape. Rerunning makes new evidence
   files, which is its own decision.
3. **Link rule.** Adopt gov-tla's rule that a module's file name opens its diagram (recommended), in place of the
   file at the pin. This moves links in about 20 diagrams that name `Seats.tla` alone, but no drawing moves. The
   diagram's header still links to the file.
4. **`RulesFloorNV.tla`**, the frozen G1 copy. Leave it to its H3 row for now (recommended), or draw it with a
   `superseded` pill.
5. **The rev5 certification gap.** The diagram will show it. Whether to close it (another backend, or a rewritten
   step) is a proof task, outside this scope.

## Later batches (the other modules)

| Batch | Modules |
|---|---|
| Confinement and leases | `Confinement`, `Confinement_A1`, `ConfinementRefinement`, `RunConfinement`, `Lease`, `Lease_A1`, `Labels`, `ToolList` |
| Emergency, liveness and observers | `BreakGlass`, `BreakGlass_A1`, `Emergency`, `Emergency_live`, `Coupling`, `Coupling_live`, `RunCoupling`, `Observers`, `Correlator`, `Operators`, `Anchor` |
| Composition | `NonComposition`, `NonComposition_A1` |
| Workflow and mesh | `Workflow`, `Workflow_A1` (drawn nowhere today), `Mesh` |
| Command-chain overlay | the eight H8 modules: per-module pages beside H8, or H8 left as their page |
| Consensus and the trace | `Paxos`, `PaxosTrace`, `Mechanism` |

`spec/defects/` (the tlapm defect cases) and the `Trace_*` modules are not in scope.
