# Simulated life cycle of deployment <name>

**<yyyy.mm.dd>** · derived · one simulated run of the configurations in `<config dir>`, with injected adversity. The
simulator refuses to start if the pins do not match those files.

## What is real and what is modelled

| Real | Modelled in this directory |
|---|---|
| Every bundle decision, compiled to Wasm, in the reference's `opa-wasm` | <each thing, and the record each modelled check stands in for> |

**Assumptions the records do not settle**, each visible in `scenario.json` or the code:

## What happened

| Tick | Time | Event | Result |
|---|---|---|---|

## Findings

## Replay

```
python3 -m topak_sim.replay                      # chain, state hashes, snapshots
python3 -m topak_sim.replay --reeval rego        # re-decide every bundle decision with the Rego interpreter
python3 -m topak_sim.replay --reeval wasm        # and every linked-floor decision, with the engine
python3 -m topak_sim.replay --at TICK            # the state at a tick
python3 -m topak_sim.replay --explain SEQ        # one event in full
```

To run again: `uv run --with pyyaml world.py`. The same seed gives a byte-identical trace.
