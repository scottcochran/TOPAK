# Authoring a deployment

Layout, under `derived/<slug>-<date>/`:

| Directory | Holds |
|---|---|
| `1-bundles/<name>/` | One directory per unique bundle, Rego and tests only, not built |
| `2-workflows/` | DAG and mesh JSON, in the reference's schema plus overlay fields |
| `3-planes/` | Plane configurations, charters, tallies |
| `4-mission/` | The task's own plan and rules as a bundle: geography, rules of engagement, approval limits |
| `5-deployment/` | Where each application and mechanism component runs, the values with their arithmetic, and the declarations |
| `tools/check_consistency.py` | This deployment's cross-file facts |

## Bundles

**One bundle per rate of change.** Standing rules, what a boundary may hand down, the class of equipment, this task. A
charter's list only grows, so a bundle that changes often should sit last in the chain.

Each bundle's entrypoint:

```rego
package topak.bundle

import data.topak.standing   # the package holding this bundle's rules

default allow := false

allow if not refused

refused if count(standing.violations) > 0

violations := standing.violations
```

- **A rule refuses, and says why**, as `sprintf("ROE-3: ...", [...])` or a plain string. Start with a stable identifier and a
  colon: the kernel tallies refusals by whatever comes before the colon.
- **`sprintf` takes `%s`.** `%q` and `%v` trap under `opa-wasm`, and so does `%d` on a value that is not a number. It still denies,
  but the reason is lost. `policies/*.rego` has this defect, so copies of `tool_schema`, `actuate` and `tool_invocation` need `%q`
  changed to `%s`, and they go in the bundle's `copied` list in `scenario.json`.
- **Check a number is a number.** Rego orders across types, and every string sorts after every number, so `amount > limit` is true of
  the string `"500"`. Guard any limit a stack can reach with `is_number`. Only a second engine's re-decision caught this in testing.
- **Read a safety fact only from what the mechanism lifts for itself**: `input.facts` for a governor, `input.context` for the
  plane. `input.inputs` is what the untrusted side asked for. It is what you bound, and never what you trust.
- **State what the rules cannot enforce**, at the top of the file. ADR-0067 §6 is the model: identification, necessity and
  proportion are enforced by nothing in Rego.
- **Tests sit beside the rules**, as `*_test.rego`, with a permit case on each side of every boundary. A fixture must supply
  every field a rule reads. A rule over a missing field does not fire, so the test passes for the wrong reason. Override data at a
  narrow path: `with data.topak as x` from a test in `data.topak` is a recursion error.

An allowlist entry in `data.json`, keyed `name@digest` under `topak.tools`, in the form `allowlist.rs` reads, plus the overlay's `effect`
part if the use case has one:

```json
"example.lookup@<digest>": {
  "name": "example.lookup", "digest": "<digest>", "domain": "run", "purpose": "What it does, for the reviewer.",
  "inputs": {"ref": {"type": "string", "required": true, "note": "", "destination": false, "accepts": []}},
  "destinations": "none",
  "result": {"label": ["untrusted"], "releases": []},
  "channel": {"kind": "https", "target": "lookup.internal:443"}
}
```

`destination` and `channel` are what make floor rules R5 to R7 fire. `lift.label_facts` computes the floor's facts from them.

## Workflows

The reference's `Definition` is a closed schema. The overlay adds `lease` and `observer` to nodes and `topics` at the top,
and the kernel strips those before loading and records that it did.

Decide these, for every edge, before running anything:

| Ask | Why |
|---|---|
| What fires when a round ends `expired`? | That is the only end a lost link gives you |
| What fires on `revoked`? | In the reference a fenced or revoked round is a failed activation and fires nothing |
| What fires for a body that can never seal? | An edge needs its source covered, and coverage needs a seal |
| Does a chain of rounds run through one body? | Then losing that body ends the chain |
| Should the next round start before this one ends? | A round has one outcome, and an edge fires after it ends |

Each node's `outcomes` is a closed enum, and a stack can report only those. A guard reads enums, labels and a bounded count,
never a clock.

**A person's decision is its own node.** The reference opens a decision event on any node with a chosen edge, and fails the run if none
is enabled. So put a gate node before the decision, give it only chosen edges, one per choice, each with a target, and let a
computed fork happen elsewhere. A "reject" needs somewhere to go.

`assets/starter-commanded/2-workflows/main.dag.json` is a complete small DAG that loads: every node field, guards, an orchestrator
seating. Guards are `"true"`, `{"outcome": {"node": n, "any_of": [...]}}`, `{"end": {"node": n, "any_of": ["expired"]}}`,
`{"label": {"node": n, "has": "untrusted"}}`, `{"count": {"node": n, "of": "actuates", "cmp": "le", "value": 3}}`, `{"all": [...]}`, `{"any": [...]}`
and `{"not": g}`.

## Planes

- **A charter is closed and only narrows.** Every field of a child is at most its parent's. `tools/check_consistency.py`
  should check each one.
- **An autonomous plane's charter is its intent.** Its `expiry` in ticks is the end of its authority.
- **Off-by-one:** no grant happens at or after (expiry + 1) · `T_tick`, so a period of N ticks needs `expiry` of N − 1.
- **Derive every bound and show the arithmetic** in `5-deployment/values.yaml`: budget from the waves and the lease length with a
  stated margin, `K_up` from what the deployment will tolerate unwatermarked, the time to fence as `K_up` over the spend rate.
- **Name each open question** a record leaves to the deployer, and which way you went, with `⟨Q⟩` numbers where they exist.

## Deployment files

`5-deployment/deployment.yaml` says where each mechanism component and each application runs: replicas, Observers (on another host
from what they watch), the bundle server, tool hosts. `values.yaml` holds each number with its derivation. A declaration file lists each
departure a record asks to be declared, with the record's section. On a single commanded plane this is short, and still worth writing,
because it is where the deployment admits what it assumes.

## The pin chain

Files pin each other by digest, in one direction, so build them in this order and re-pin on any change:

```
Rego and data.json → bundle revision → charter's bundle list → tally's artifacts
mesh JSON and plane YAML ──────────────────────────────────────→ tally's artifacts
```

A bundle's revision is `topak_sim.policy.bundle_rev(dir)`, the computation in `mechanism/scripts/build-bundle.sh`.

- **Real digests:** bundle revisions, charter, mesh and plan digests.
- **Placeholders, each stated as one in the README:** keys, personas, task templates, tool digests, floor digest in a charter.
  Use the SHA-256 of a label.

Declare the pins in `scenario.json` so the simulator refuses a mismatch:

```json
"pins": [
  {"kind": "bundle_list", "in": "3-planes/ap1.charter.yaml", "at": "bundles"},
  {"kind": "bundle", "bundle": "mission", "in": "3-planes/tally.yaml", "at": "artifacts/mission_bundle"},
  {"kind": "file", "file": "2-workflows/x.mesh.json", "in": "3-planes/tally.yaml", "at": "artifacts/mesh"}
]
```

## A use case's own consistency check

`tools/check_consistency.py` compares two files that state one fact, or recomputes a fact one derives: every field of a charter
against its parent, the tick arithmetic, the budget, each route against the no-go areas, each seat against the tree. It should
read constants out of the Rego with `opa eval` and not retype them. The recon-7 one is the model, and it caught a wrong budget
formula and a recovery route through a no-fly zone before any simulation ran.
