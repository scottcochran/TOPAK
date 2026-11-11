# Simulated life cycle of deployment recon-7

**2026.11.10** · derived · one simulated run of the configurations in `../recon-fleet-7-2026.11.10`, with injected
adversity. The simulator refuses to start if the charters' or the tally's pins do not match those files.

## What is real and what is modelled

| Real | Modelled in `sim/simulate.py` |
|---|---|
| Every bundle decision: the four bundles, compiled to Wasm, in `opa-wasm`, the crate `topak-bundle` uses | The floor's federation stage, which is unwritten. Each check names the entry of ADR-0067 §3 it stands in for |
| Bundle revisions, charter, tally and mesh pins | PBFT, the radios and flight, at one-tick (30 s) resolution |
| The mesh and DAG files, and their guards | The stacks: a simple scripted planner, plus the requests in `scenario.json` |
| `opa test` at the promotion gate | The governor, which is unbuilt |

The Wasm is built with one extra entrypoint so refusal reasons can be read. The Rego source is the pinned source.

**Assumptions the records do not settle**, each visible in `scenario.json` or the code:

- A governor waits 4 ticks for a successor lease before starting its terminal behaviour. No record says how long.
- Renewing a lease costs one tick, an upper bound on the rounds it takes.
- A mesh edge needs its source's Observer to have read the sealed record (ADR-0054 §7). A vehicle that is destroyed
  never seals.
- A stack reports `relief_due` at the next wave's planned launch.

## What happened

61 leases of a budget of 112. 1,396 admits, of which 100 were refused: 3 by the modelled floor and 97 by the bundles.
No invariant failed, and removing peer-originated labels changed none of 224 permits.

| Tick | Time | Event | Result |
|---|---|---|---|
| before 0 | | Staff DAG, go/no-go, gate, tally | An agent in the commander's seat, a 2880-tick intent and a second fleet are refused. The commander routes `e-go` |
| 130 to 205 | H+1 | Eleven bad stack requests | All refused, each by the rule meant to catch it |
| 300 | H+2:30 | v2 cut from its plane for 8 ticks | Lease ends at once, 4 beacons, returns. After its seal, `spare-v2` launches v7 |
| 481 | H+4:00 | SAR by v1 at a lease's start | Admitted. v7's second emitter and v3's mid-lease attempt are refused |
| 920, 1820 | H+7:40, H+15:10 | Reliefs | 20 minutes uncovered at the first. See finding 1 |
| 1380 to 1900 | H+11:30 | Link above the plane cut | Grants stop at tick 1761, 3 h 10 min in. SAR refused by ROE-8. Recovers on restore |
| 1500 | H+12:30 | v5 revoked during the cut | Arrives 3 h 20 min later. 55 further effects in the fleet, against a bound of 120 |
| 2300 | H+19:10 | v3 destroyed in flight | Dropped from the plane at 2320: 6 members, certificate 4, cap 96. v7 stays on the ground |
| 2499 | H+20:49 | Host of v1's Observer silent 12 ticks | v1 starts home, then is re-leased when the Observer reads |
| 2700 to 2703 | H+22:30 | `wave3_complete`, `close` | Mesh completes |
| 2879 | H+23:59 | Intent expires | No live lease survives it |

Coverage from tick 60 to 2700: **A 92.6%, B 61.2%, C 78.4%.** `out/summary.json` has every gap and rule count, and
`out/timeline.txt` has the events.

## Findings

1. **The mesh cannot deliver the plan's overlapping relief.** A round has one outcome. `relief_due` ends the outgoing
   vehicle's lease and only then launches its relief, so each relief leaves about 20 minutes uncovered, against a plan
   that says 30 minutes of overlap. Letting `loop-*` also fire on `relief_due` would fix it, and needs a new tally.
2. **The spare is never launched for a vehicle that is destroyed.** `spare-*` waits for coverage of a seal that cannot
   arrive. Sector C stayed empty for 3 h 20 min with v7 fuelled on the ground.
3. **One revocation ends a sector for the rest of the mission.** The relief chain runs through the vehicle, and no edge
   fires on `revoked`. Together with the link cut, sector B was uncovered from tick 1760 to the end.
4. **ROE-11 nearly disables SAR.** `peer.coverage` is delivered clear to every leased stack, so SAR is admissible only
   before a lease's first coverage report arrives.
5. **A destroyed vehicle's charge is never released.** Its lease cannot be sealed, so 8 stays outstanding against
   `K_up` for good.
6. **Between a lease's end and its successor, no record says what a body in flight does.** The 4-tick wait is this
   simulation's.

Confirmed as declared: `K_up` stopped a cut-off plane after about 3 hours, the figure in `values.yaml`.

## Replay

```
python3 sim/replay.py                      # chain, 3026 state hashes, snapshots
python3 sim/replay.py --reeval rego        # re-decide every recorded admit, with the Rego interpreter
python3 sim/replay.py --at 1800            # the fleet at a tick
python3 sim/replay.py --admits v3 --from 160 --to 200
python3 sim/replay.py --explain 1016       # one event: input, each bundle's decision, state change
```

Replay needs no simulator or random numbers: each event's patch is the only thing that changes state.
`--reeval rego` needs `opa`. `--reeval wasm` also needs PyYAML and cargo.

To run again: `uv run --with pyyaml sim/simulate.py`. The same seed gives a byte-identical trace.
