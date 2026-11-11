---
name: use-case-simulator
description: "Turns a stated TOPAK use case into a self-consistent illustrative deployment (Rego bundles, workflow DAG or mesh, plane configs, charters, tallies, task rules, deployment declaration) and plays out its whole life cycle with injected adversity, evaluating every decision with the real compiled bundles, the linked Cedar floor and the reference's workflow Run, and capturing a hash-chained trace that replays with no simulator. Use whenever the custodian describes a deployment or mission and wants it configured, simulated, stress-tested, played out or replayed: a drone or robot fleet, an agent pipeline with human sign-off, a SOC or claims workflow, a command chain, 'what would this look like under TOPAK', 'generate configs for this use case', 'simulate this mission', 'replay that run', 'what happens if the link is cut'. Also use to re-run or extend a simulation already in derived/. Not for model-checking a record (writing-tla-specs-and-proofs), not for testing the reference itself (cargo test), and not for changing a record (drafting-records)."
---

# Use-Case Simulator

## Contents

- [When to Use](#when-to-use)
- [When NOT to Use](#when-not-to-use)
- [What is real](#what-is-real)
- [The workflow](#the-workflow)
- [Verification](#verification)
- [Handing it over](#handing-it-over)
- [Quick reference](#quick-reference)
- [Rationalizations to reject](#rationalizations-to-reject)
- [References](#references)

A method for finding out what a TOPAK deployment does before anyone builds it, distilled from the recon-fleet-7 run
(`derived/recon-fleet-7-2026.11.10/` and its `-simulation-` sibling).

**Core principle: a simulation is worth what it actually evaluated, and its value is in what the configuration got
wrong.** Evaluate everything that exists with the code that exists. Name everything that does not, and the record each
stand-in comes from. Then believe the result over the plan. The recon run's first output was a list of its own
author's claims that the run disproved, such as "coverage is continuous", and that list was the point.

Scripts live in `scripts/` next to this file. From the repository root,
`SK=.claude/skills/use-case-simulator`.

## When to Use

- A use case is described and a deployment for it is wanted, whatever the domain
- A deployment should be played out, attacked, or checked for what it delivers
- A trace needs replaying, re-deciding or explaining
- A configuration changed and the run should be repeated to compare

## When NOT to Use

- **Proving a property.** A simulation shows one path. Use TLA+ or Lean.
- **Testing the reference.** `cargo test --workspace` does that. This drives parts of it from outside.
- **Deciding anything.** The output is derived. A finding is a lead for the custodian, and no record changes here.

## What is real

The kernel evaluates with the reference's own code wherever that code exists, through one process (`scripts/engine`).

| Tier | In the simulation | Real when |
|---|---|---|
| Bundle chain | Rego compiled to Wasm, in `opa-wasm`, the engine `topak-bundle` uses | Always |
| Policy floor | `topak_floor::Floor`, digest-pinned, schema-validated | `"floor": "cedar"`. The linked stage is `workflow`, which is **not** the floor in force. Say so |
| Workflow | `topak_core::workflow::Run`: guards, taint, joins, skips, budget, completion | Always. Text the closed schema refuses is stripped of overlay fields, and the strip is recorded |
| Promotion gate | `opa test` on the bundles the tally votes on | When the world runs it |
| The lift | `topak_sim/lift.py`, a port of `lift.rs`. Cedar rejects anything off-schema | **Modelled**, because the real one needs a replica's State |
| Federation stage (FD1 to FD15) | Named checks in `topak_sim/overlay.py` | **Modelled**: it is unwritten |
| Consensus, governor, watermark | `overlay.py` | **Modelled**: unbuilt |
| Network, physics, stacks, people | The world | **Modelled**, always |

## The workflow

1. **Pin the use case.** Write down what was stated and what was not. Ask only about what would change the deployment's
   shape. Choose the rest, and list each choice in the configuration's README.
2. **Choose the shape** from [deployment-shapes.md](references/deployment-shapes.md): commanded workflow, mesh, Build and
   promote, or command chain. The shape decides which records to read and how much is modelled.
3. **Read those records whole**, as revised, and note the status of each. An unratified record yields an illustrative
   configuration, and the README says so in its first lines.
4. **Scaffold**: `python3 $SK/scripts/new_usecase.py <slug> --shape commanded|autonomous`. It lays out both directories
   under `derived/` and vendors the kernel, because a derived directory is frozen and the skill's kernel will change.
5. **Author the configuration** by [config-authoring.md](references/config-authoring.md). Before simulating, walk every
   failure class through the workflow's edges by hand: what fires on an expired round, a revoked one, a body that is lost
   and can never seal. Most of recon-7's findings were sitting in that walk.
6. **Check it**: `uv run --with pyyaml $SK/scripts/check_deployment.py --mutate derived/<slug>-simulation-<date>`, then
   the use case's own `tools/check_consistency.py`. A rule no test needs fails the check: strengthen the test or delete
   the rule. Advisory survivors are conditions or boundaries no test pins, to judge one by one. Do this before the
   simulation, or the run tests rules that may not work.
7. **Write the scenario and the world** by [simulator-design.md](references/simulator-design.md). Replace every TODO. The
   scenario must exercise every fault class that applies, and give every refusal rule a request meant to trigger it.
8. **Run it and triage.** A result that contradicts a record is a simulator bug: fix the world. A result that follows
   from the configuration is a finding: keep it, however bad it looks. Do not tune the scenario until the findings go away.
9. **Verify** (below), then write the simulation's README from the trace, and hand over.

## Verification

All four, and report what each returned. A run that skipped one says which.

| Check | Command, from the simulation's directory | What it shows |
|---|---|---|
| Replay | `python3 -m topak_sim.replay` | The hash chain, and every state hash from patches alone |
| Determinism | Run twice into two directories, and `shasum` the traces | Byte-identical, so the seed is the whole input |
| Differential | `--reeval rego` and `--reeval wasm` | Two engines re-decide every recorded decision, 0 differences |
| Tamper | Alter one recorded decision in a copy, and replay it with `--trace` | The replay exits 1 at that event |

Then, for each headline number you intend to report, get it from `--summary` or `--explain`, not from memory of the run.

## Handing it over

Open with what was modelled and which assumptions no record settles. Then what happened, what was verified, and the
findings. Correct plainly any claim in the configuration that the run disproved. See
[findings.md](references/findings.md).

The configuration is pinned by its charters and tallies, and a derived directory is frozen. A fix is a decision: name it
and offer it. It means a new mesh or bundle digest, a new tally and a new run. Commit only when asked, and add the
`derived/README.md` rows with that commit.

## Quick reference

| Task | Command |
|---|---|
| Lay out a use case | `python3 $SK/scripts/new_usecase.py <slug> --shape commanded\|autonomous [--date yyyy.mm.dd]` |
| Check a deployment | `uv run --with pyyaml $SK/scripts/check_deployment.py --mutate <sim-dir>` |
| Run | `TOPAK_SIM_TARGET=<dir> uv run --with pyyaml world.py [out-dir]`, from the simulation's directory |
| Verify and replay | `python3 -m topak_sim.replay [--reeval rego\|wasm]` |
| Another trace | `--trace <file>`. Run from the simulation's directory, or add `--sim <dir>` |
| What happened | `--timeline`, `--summary` |
| State at a tick | `--at TICK [--path bodies/v1]` |
| One event, in full | `--explain SEQ` |
| One principal's admits | `--admits v3 --from 160 --to 200` |
| After changing the kernel | Run `examples/recon-fleet-7/world.py`, then `$SK/scripts/regress.py <trace>` |

`TOPAK_SIM_TARGET` is where the engine builds. Use one directory across runs, since the first build takes minutes.
`opa` must be the host binary. `/opt/homebrew/bin/opa` has no Wasm runtime for `opa eval -t wasm`, which is why decisions
go through the engine, but it builds and tests bundles correctly.

## Rationalizations to reject

| Rationalization | Reality |
|---|---|
| "The bundle would refuse this, so I'll just record a refusal." | Then it evaluated nothing. Every decision goes through `admit`, and the trace holds its input. |
| "I'll compute this outcome in the world, it's simpler than a workflow edge." | Workflow semantics are the reference's. A hand-rolled edge hides exactly the defects worth finding. |
| "This modelled check is obviously what the floor would do." | Then cite the entry it stands in for, in the check. Unnamed, it reads as real. |
| "The scenario looks bad, I'll soften the fault." | The bad result is the deliverable. |
| "The plan says 30 minutes of overlap, so there is overlap." | The plan is a claim. The measure in the trace is what happened. |
| "The configuration has a bug, I'll quietly fix it and re-run." | The run then reports on a deployment nobody reviewed. Report it, and offer the fix as a new pinned set. |
| "I'll fix the one wrong sentence in the frozen README." | A derived file is not revised. The simulation's README says what the run disproved. |
| "Replay passes, so the decisions are right." | Replay checks the record is intact. `--reeval` checks the decisions. |
| "`datetime.now()` is only for a log line." | It breaks byte-identical reruns, and with them the claim that the seed is the whole input. |
| "This simulation proves the design is safe." | It shows one path, under stated assumptions, on a model of the unbuilt parts. |

## References

- [deployment-shapes.md](references/deployment-shapes.md): the shapes, what each makes real, the records each needs.
- [config-authoring.md](references/config-authoring.md): the five kinds of file, the rules each follows, the pin chain.
- [simulator-design.md](references/simulator-design.md): the kernel's API, tick ordering, scenarios, faults, invariants.
- [findings.md](references/findings.md): what counts as a finding, the patterns to look for, the report.
- `examples/recon-fleet-7/`: the worked autonomous world on this kernel, which makes all 1,396 admits and 61 grants of
  the frozen run. The configuration and frozen run it reads are in `derived/`.
