# Deployment recon-7: one reconnaissance fleet of seven, one 24-hour intent

**2026.11.10** · derived · an illustrative use-case configuration, not a record · against ADR-0054, ADR-0055 and
ADR-0059 to ADR-0068, all Proposed.

**Nothing here can run today.** The governor, PBFT, the watermark, the federation floor stage and the overlay's
fields are unbuilt. The files are self-consistent with each other and with the records. They are not a working
deployment, and every number is a placeholder.

## The deployment

```
 root           commanded · 5 replicas, Paxos, declared unexposed     chain: standing
   |            seats ib1 and nothing else
 ib1            commanded, the INTENT BOUNDARY · 4 replicas, PBFT     chain: standing, command
   |            staff DAG, commander's go/no-go, mission tally, watermarks
 ap1            autonomous · 7 replicas, signed PBFT, cert 5          chain: standing, command, fleet, mission
   |            the mesh, no person, no path that changes authority
 v1 ... v7      a governor (trusted) and a stack (Byzantine) each
```

| Ask | Where |
|---|---|
| 1. OPA policies, one directory per unique bundle | `1-bundles/standing`, `command`, `fleet`. The fourth, `mission`, is item 4 |
| 2. Workflow DAG and mesh | `2-workflows/staff-cycle.dag.json` at ib1, `recon-sectors.mesh.json` at ap1 |
| 3. C2 plane configs | `3-planes/`: root, ib1 and ap1, the two charters, and the mission tally |
| 4. Mission plan and ROE in Rego | `4-mission/plan.rego`, `roe.rego`, with `geo.rego`, and `data.json` for the allowlist and topics |
| 5. Deployment of applications and mechanism | `5-deployment/deployment.yaml`, with `values.yaml` and `overlay.declaration.yaml` |

**Why four bundles.** They change at four different rates, and a charter's list only grows. `standing` is the
deployment's own rules. `command` is what the intent boundary may hand down. `fleet` is the airframe. `mission` is
this tasking. All seven vehicles share one chain, so there are no per-vehicle bundles.

**This mission has no irreversible effect.** It only flies, senses and transmits, so no plane seats a release seat,
and `standing` refuses any irreversible entry on any chain.

## How the 24 hours work

The charter of ap1 is the intent. Its expiry is **tick 2879**, with `T_tick` = 30 s. `PlaneClock`'s bound is that no
grant happens at or after (expiry + 1) · `T_tick`, so 2879 keeps every grant inside 24 hours and 2880 would not.

The bound rests on a premise: captured and slow replicas together are at most four of seven. The count starts when
the charter is **applied**, and not at the vote ⟨Q13⟩.

| Wave | Launch | On station | Recover by | A | B | C |
|---|---|---|---|---|---|---|
| W1 | 20 | 60 to 1020 | 1100 | v1 | v2 | v3 |
| W2 | 920 | 960 to 1920 | 2000 | v4 | v5 | v6 |
| W3 | 1820 | 1860 to 2700 | 2780 | v1 | v2 | v3 |
| Spare | 20 | 60 to 2700 | 2780 | v7, any sector | | |

Ticks throughout, 120 to the hour. Coverage is continuous from H+0:30 to H+22:30.

## What bounds it

| Bound | Value | Meaning |
|---|---|---|
| Lease | 8 entries, 120 ticks (1 h) | `K` and `T_persona` from the floor's placeholder values |
| `K_up` | 120 | After a fence, fewer than 120 further effects, with no premise about time |
| Budget | 112 leases | 109 planned, plus 3 re-leases ⟨Q15⟩ |
| Link above ap1 lost | about 3 to 4 hours | Grants then stop, and vehicles spend what they hold and hold |
| Vehicle loses its plane | 40 s at most | One tick period plus the grace below. The lease ends and the governor returns it |
| SAR while unattended | refused after 30 min | ROE-8. EO/IR collection continues |

`5-deployment/values.yaml` has the arithmetic.

## Choices made for you

- **ADR-0060 §5 is your open choice, and this takes option 3**, the drafter's recommendation. Each entry declares
  `while_unattended`. If you choose another option, `sensor.sar_strip`'s treatment and ROE-8 change.
- **`sensor.sar_strip` is the one `ordered` entry** ⟨Q20⟩: one emitter per sector has to be the same for all seven.
- **Observers sit on another vehicle** ⟨Q9⟩, in rings v1-v2-v3 and v4-v5-v6, with v7 watched from v1. Losing an Observer's
  vehicle holds up the next lease of the vehicle it watches. The `spare-*` edges fire only once that lease has expired.
- **`peer.coverage` is delivered clear among stacks of one build**, which is D-0065-1, declared. `peer.tracks` is a handle.
- **Identification, necessity and proportion are enforced by nothing here** (ADR-0067 §6). `roe.rego` says so at the top.

## Findings against the corpus

1. **`policies/tool_schema.rego` and `actuate.rego` trap under the reference's Wasm engine on a refusal.** `opa-wasm`
   fails on `sprintf` with `%q` and `%v`. Confirmed on the repository's own bundle with a missing required field. It
   still denies, since an error is not an `allow`, but the reason is lost. The copies here use `%s`.
2. **ADR-0064 §5, read literally, leaves no room for a round.** A replica signs tick τ only once its clock reaches
   τ periods, and a governor finds tick τ overdue when its clock reaches the same moment. `PlaneClock` hides this
   because discrete time lets both happen at once. `ap1.plane.yaml` sets `overdue_grace_ms: 10000`, which the record
   does not provide for.
3. **The charter has no field for an envelope in the world** (ADR-0059's open F4). So the areas live in the mission
   bundle, and a commander's next intent cannot shrink an area without a promotion. It can shrink the alphabet, the
   budget and the time.
4. **A mesh cannot wait for all three sectors to finish.** An `all` join is not built in a mesh. `close` joins `any`, so
   the mesh completes when the first sector reports W3 complete, and the others ride out their last lease.

## What the reference does with these files

Run through the real code: `Definition::parse` and `check`, and the `opa-wasm` engine.

- **The DAG parses, and its only load errors are "seating above rung 0"**, a provisional limit of the reference. The
  seats are rung 2 on purpose.
- **The mesh is refused as written**, on the overlay's `lease` field. With `topics`, `lease` and `observer` removed it
  parses, with the same rung errors and no others.
- **`data.json` carries the `effect` part**, which `allowlist.rs` would refuse as an unknown field.

## Checking it

From this directory:

```
for b in 1-bundles/standing 1-bundles/command 1-bundles/fleet 4-mission; do opa test $b; done
uv run --with pyyaml tools/check_consistency.py
```

118 policy tests pass. `check_consistency.py` makes 425 cross-file checks, including every digest pin, every charter
field against its parent, the tick arithmetic, the budget, the graph properties, and recovery routes against no-fly zones.

**Real against placeholder.** The bundle revisions and the charter, mesh and plan digests are real, computed as
`build-bundle.sh` computes them. Keys, tool digests, personas, task templates and the floor digest are placeholders,
each a SHA-256 of a label. A change to any Rego changes its revision and the pins must follow.
