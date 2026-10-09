# The genesis floor, the floor in force and the linked floor under Cedar's verified semantics

`genesis-floor.cedar` and `genesis.cedarschema` stated in the abstract syntax of cedar-spec, the Lean model of
Cedar that AWS maintains and proves properties of, with ADR-0030 §5's totality gate proved as a theorem of that
model and the 62 behavioral cases of `genesis-tests.json` checked under its authorizer. **And since 2026.10.06 the
floor in force**: `proposed/emergency-floor.cedar` and `emergency.cedarschema`, the stage the reference links and
pins (`mechanism/crates/topak-floor`), with the same theorems and its 107 cases (`InForce.lean`; ADR-0053 R3).
**And since 2026.10.08 the floor the reference links**, which is not the floor in force: `proposed/workflow-floor.cedar`
and `workflow.cedarschema`, with the same theorems and its 123 cases (`Linked.lean`; ADR-0033 A16).

## Why

`run-gates.py` runs `cedar symcc never-errors` for every policy on every action it applies to. On the genesis
floor cedar decides all 23 of those checks by folding the authorizer term, with no solver query, so the run
marks them `holds°` and they rest on the engine's row, ADR-0045 T-0045-3, not on the checker's
(`floor/README.md`, "What the checker does not cover"). Here the same claim is a theorem: cedar-spec proves
`validation_is_sound`, that a policy set the validator accepts never errors on a schema-conforming input
except for three runtime errors the validator cannot see, and the genesis floor validates
(`floor_validates`). The `holds°` rows become `floor_never_errors`.

## What is proved (`TopakFloor/Gates.lean`)

| Theorem | Claim |
|---|---|
| `schema_wf` | schema S is well-formed under the model's `Schema.validateWellFormed` |
| `floor_validates` | the 17 policies validate against S under the model's `validate` |
| `floor_never_errors` | for every request and store that validate against S, every policy evaluates to a boolean or to `entityDoesNotExist`, `extensionError` or `arithBoundsError` (`validation_is_sound`) |
| `policy_never_errors` | the same, read per policy: the 23 `holds°` rows |
| `floor_no_ext_no_arith` | the floor's expressions call no extension and do no arithmetic, so of the three residual errors only `entityDoesNotExist` can occur, which is a lift fault (ADR-0030 §4) |
| `cases_conform` | every test request and the shared store validate against S |
| `not_always_allows` | non-vacuity: for each of the ten actions, a conforming case the floor denies |
| `not_always_denies_but_erase` | discrimination: for each action but `Erase`, a conforming case the floor allows; at genesis no erasure roster is issued, so `X2-erasure` admits nothing |
| `case01` to `case62` (`Tests.lean`) | each case's request, under `isAuthorized`, returns the case's decision, its determining policies and no error |

## The floor in force (`TopakFloor/InForce.lean`, 2026.10.06)

`gen.py emergency` states the `emergency` stage from the bytes `topak-floor` pins (28 policies; schema S with the
control alphabet), into `Emergency.lean` and `EmergencyTests.lean`. `gen.py` with no stage writes both statements; the
genesis files come out byte for byte as before.

| Theorem | Claim |
|---|---|
| `inForce_schema_wf`, `inForce_validates` | the stage's schema is well-formed, and its 28 policies validate against it |
| `inForce_never_errors` | totality: on every conforming request and store, every policy evaluates to a boolean or a residual runtime error; the `emergency` gate run's 41 totality `holds°` rows as one theorem |
| `inForce_no_ext_no_arith` | no extension call and no arithmetic, so the residual is `entityDoesNotExist`, a lift fault |
| `inForce_cases_conform` | every one of the 107 cases' requests, and the shared store, validate against S |
| `inForce_not_always_allows`, `inForce_not_always_denies` | non-vacuity and discrimination on **all sixteen** actions, with no exception: the stage's cases include an allowed `Erase` |
| `emCase001` to `emCase107` (`EmergencyTests.lean`) | each case under `isAuthorized` returns its decision, its determining policies and no error |

`tools/lean-sync.sh` reads the floor and schema `topak-floor` links and fails if the newest results file does not state
them, so a move of the reference to another stage cannot leave the floor that runs without a Lean statement.

## The floor the reference links (`TopakFloor/Linked.lean`, 2026.10.08)

On 2026.10.08 the reference moved to the `workflow` stage (ADR-0041 A4, pending, with ADR-0054, Proposed), which is
not in force. `gen.py workflow` states it into `Workflow.lean` and `WorkflowTests.lean` (30 policies; schema S with
`Route`, `WorkflowNode`, `Edge` and `RunCtx.decisionPoint`), and `Linked.lean` proves of it what `InForce.lean` proves
of the floor in force: `linked_schema_wf`, `linked_validates`, `linked_never_errors`, `linked_no_ext_no_arith`,
`linked_cases_conform`, and non-vacuity and discrimination on all seventeen actions, `Route` among them. `wfCase001` to
`wfCase123` hold under `isAuthorized`. The results file's `Floor:` line names the linked files after `linked:`.

What stays with `run-gates.py` and the checker: the every-entry-matters gate and routing, which are solver
queries about pairs of floors (`implies`, `equivalent`), and the negative controls.

## What it rests on

- **The Lean kernel**, toolchain `leanprover/lean4:v4.33.1`, cedar-spec's own and the one `tools/LEAN-PIN` names.
- **cedar-spec at tag `v4.13.0`**, the tag matching the cedar-policy 4.13.0 the mechanism links and the
  cedar-policy-cli 4.13.0 the gate run records. `lakefile.lean` pins the tag; `lake-manifest.json` the commit.
  The model's fidelity to the Rust engine is cedar-spec's claim, kept by differential testing; the symbolic
  compiler whose verdicts the gate run already uses rests on the same model.
- **The parse.** `gen.py` asks cedar-policy-cli to translate the Cedar text to JSON and walks that JSON into
  the model's syntax, policy by policy under its `@id`; `Genesis.lean` and `Tests.lean` are generated, with the
  sources' digests in their header, and are regenerated by `results.sh`.
- **`native_decide`** for the closed evaluations (validation, the 62 cases, the witnesses): Lean's compiler is
  trusted for them, and `#print axioms` shows one axiom per such use (`floor_validates._native.native_decide.ax_1_1`
  and so on). The kernel's own `decide` was tried and cannot reduce the model's definitions (its maps and sets
  are built by well-founded recursion), so this is not a choice. `floor_never_errors` itself is a kernel-checked
  application of cedar-spec's theorem to those two evaluations; the model's proofs bring `propext`,
  `Classical.choice` and `Quot.sound`.
- **The replay.** Every results file ends with `leanchecker --fresh`, which replays every constant the package
  reaches, Lean's own library included, through the kernel in a fresh environment (`tools/lean-report.sh`).
  `#print axioms` alone misses a declaration added with the kernel check off; the replay refuses it
  (`spec/proof-method.md` §5b). It is the same kernel in a fresh process, not an independent checker.
- **The row.** ADR-0053, ratified 2026.10.06 (Batch 36), declares the method and makes the kernel and toolchain
  trusted-base row T-0045-37, pinned in `tools/LEAN-PIN`. A Lean result is cited by the results file ADR-0053 §4 names.

## Mutation check

Two mutated floors were built on 2026.10.05 from copies of the generated terms, with the 62 case theorems
removed so the gate theorems are what fails. Each fails to build in the theorem the mutation breaks.

| Mutant | Fails in |
|---|---|
| `B1-read-corpus` compares `principal.domain` with a `Long` instead of a `String` | `floor_validates` (the policy is false under every environment), and `not_always_denies_but_erase` (nothing admits `Read`) |
| a permit-all policy appended to the floor | `not_always_allows` (the actions with no forbid are then always allowed) |
| the floor in force with a permit-all appended (2026.10.06) | `inForce_not_always_allows` |
| the floor in force with `F-forensic-classes` made inert, a condition that never holds (2026.10.06) | `emCase052` to `emCase057`, the six cases that erase a forensic class under an erasure quorum |

With the case theorems left in, both mutants fail there first: the first in `case01`, the second in every
denied case of an action with no forbid.

## Run it

```sh
cd floor/lean
export PATH="$HOME/.cargo/bin:$PATH"               # cedar-policy-cli 4.13.0
python3 gen.py                                     # regenerate every statement: genesis, emergency (in force), workflow (linked)
lake build                                         # first run fetches cedar-spec and batteries and builds the model: minutes, ~GB
./results.sh > TopakFloor-results-<date>.txt       # regenerate, clean build, digests, axioms, replay (~2 min); byte for byte
../../tools/lean-sync.sh                           # STALE when a floor, schema or tests moved; checks cedar-spec and the linked floor
```

`TopakFloor-results-2026.10.06.txt` is the results file ADR-0053 cites since R3; the 2026.10.05 file, the genesis
floor alone, stays beside it unchanged. The statements are pinned, not frozen: a floor change is a regenerated results
file, and `tools/lean-sync.sh` reports one that was not regenerated.
