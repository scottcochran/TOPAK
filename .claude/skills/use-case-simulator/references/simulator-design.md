# Designing the simulation

## Contents

- [Rules that make a trace worth having](#rules-that-make-a-trace-worth-having)
- [The kernel](#the-kernel)
- [Inputs to the policies](#inputs-to-the-policies)
- [Tick ordering](#tick-ordering)
- [The scenario](#the-scenario)
- [Invariants and measures](#invariants-and-measures)
- [Bug or finding](#bug-or-finding)

## Rules that make a trace worth having

- **State changes only through `set`, `inc`, `delete` and `sync`,** and reach the trace only through `emit`. Mutating `self.s`
  directly makes the replay diverge.
- **The only randomness is `self.rng`.** No clock, no hash of a Python object, no iteration over a `set` where the order matters.
- **Every decision goes through `admit`** or `refuse_modelled`. `admit` records the input, so the decision can be re-made.
- **A stand-in names what it stands in for**, in the rule string: `refuse_modelled(by, "FD11-alone-permits-nothing", ...)`.
- **State the assumptions in `scenario.json`** under `assumptions`, each one a value no record gives. Name them in the README.

## The kernel

`Core` (commanded worlds subclass it):

| Member | Use |
|---|---|
| `load()`, `initial_state()`, `preflight()`, `step(t)`, `last_tick()`, `summary()` | What a world provides |
| `load_cfg(rel)`, `rego_value(bundle, ref)` | Read configuration, and read constants from the Rego |
| `admit(by, chain, inp, what, why=None, floor=None)` | The admit path. Pass `floor=` a lift's floor part |
| `refuse_modelled(by, rule, action, what, why)` | A refusal by a check that is not running code |
| `invariant(ok, message)` | A property of the records |
| `measure(name, on, t)`, `close_measure(name, end)` | An interval outcome, with its gaps |
| `emit(kind, **detail)` | Record what happened and any pending state changes |
| `self.chains`, `self.a`, `self.sc`, `self.rng` | Chains, assumptions, the scenario, the RNG |

`lift.run_action` and `lift.build_action` build a frozen input from a seat, its kind and the action's facts. Each returns
`{"floor": ..., "bundle_input": ...}`. Add `facts` or anything else your bundles read to the bundle input. Never add to the floor
part, because the schema is closed. **Spread `lift.label_facts(entry, inputs, handles, inside_targets)` into every `Actuate`.** Without it the
call is lifted as inward with no labels, and floor rules R5 to R7 silently cannot fire.

`WorkflowRun(sim, name, rel, seats=None)`. Load it in `preflight`. Use `step(work, route, observed)` or `drive`:

- `work(act, node)` makes the round's requests and returns `{"outcome": ..., "end": ..., "label": [...], "actuates": n}`.
- `route(event, enabled)` admits a `Route`, built with `lift.run_action(seat, "orchestrator", "Route", alphabet, **wf.route_facts(event, edge))`,
  and returns the edge. `None` lets the round lapse, which fails the event. `wf.WAIT` holds the event for a later tick, for a person
  who has not answered. `enabled` maps each chosen edge to `None`, or to why it is disabled: `guard`, `uncovered`, `finding`, `history` or `taint`.
- `observed(act)` says whether the node's Observer can read to the seal. Make it false to test a dead Observer.
- For finer control, call `grant`, `grant_decision`, `end`, `cover`, `route`, `lapse`, `finding`, `fail` or `fence`, and read `ready`,
  `open_events`, `served_events` or `enabled`. The reply's `fired` lists the edges.

`AutonomousPlane` and `AutonomousWorld`: the hooks are listed at the top of `topak_sim/overlay.py`, and all but `body_of`, `seat_of`,
`principal`, `parent_context` and `stack` have defaults. Call `plane.actuate`, `plane.consult`, `plane.peer_report` and
`plane.round_report` from `stack`. The stack is Byzantine. It only ever asks.

## Inputs to the policies

The frozen request's fields come from the lift. What an overlay bundle also reads, by convention:

| Field | Written by | Contains |
|---|---|---|
| `input.inputs` | The stack | What it asks for. Bound it; do not trust it |
| `input.handles` | The mechanism | The label of each input given as a handle |
| `input.context` | The kernel | `plane`, `planeKind`, `tick`, `permittedBy`, `hearsPlane`, `ticksSinceWatermark`, `clearSet`, `sendsThisTick`, `sendsThisLease`, `beaconsThisLease`, `outstanding`, plus `context_extra` |
| `input.facts` | The governor (`facts` hook) | What it lifts for itself: position, integrity, resource levels, peers |
| `input.resource.effect` | The allowlist | `class`, `t_irrev_ms`, `permit`, `extent`, `beacon`, `while_unattended` |

`sendsThisTick` lists every declared topic, with 0 for unused ones, so a rule reading one never sees a missing field.

## Tick ordering

`AutonomousPlane.step` runs in this order, and the reasons are the ones that bit:

| Step | Why here |
|---|---|
| Environment | Faults land first, so everything else sees them |
| Tick ordered, then hearing | A body hears the tick or it does not, before anything is granted |
| Watermark, then membership | Credit is released before the grants that need it |
| Intent expiry | No lease survives its last tick |
| Observers read, edges fire | An edge needs coverage (ADR-0054 §7) |
| Grants | Fired edges can be granted in the same tick |
| Entries expire | Before the stacks, or a stack cannot follow an entry at once and every renewal shows a false one-tick gap |
| Scripted bad requests, then stacks | Each with fresh state |
| Beacons, lease ends, physics, measures, invariants | The world moves on what was permitted, and the checks see the tick's result |

Renewal costs one tick here, an upper bound on the rounds a real renewal takes. Say so if a result depends on it.

## The scenario

A scenario should cover, where the shape has them:

| Fault | `environment` kind | What it tests |
|---|---|---|
| A body cut from its plane | `silence` | Alone, terminal behaviour, lease end, the spare edge |
| The Observer's host lost | `silence`, or `silence_on_lease_end` | Coupling: no coverage, no next round |
| The link above a plane cut | `link_cut` | `K_up` stopping grants, what still works, recovery |
| Authority withdrawn during a cut | `revoke` | How late it lands, how much happened first |
| A body destroyed | `destroy` | No seal, membership shrink, charge never released |
| Degraded sensing | your own, in `inject` | The rules that read `input.facts` |

A commanded world's scenario keys are its own: `Core` only reads `seed`, `assumptions` and `deployment`, so the world reads `environment` and
any scripted requests in `step`. The analogues of the faults: an Observer that stops reading, a person who does not answer at a decision point, a finding
against an ended round, a fence mid-run, and a tool that returns tainted data.

**Give every refusal rule a request meant to trigger it**, with a `why`, under `stack_misbehaviour` or your own key. Also keep the
organic refusals, those a plain planner runs into. Those are the ones nobody predicted: recon-7's 79 ROE-9 refusals were organic.

**Attack the people too.** An agent in a person's seat, an intent one tick too long, a second child where one is allowed.

**Assume a planner that is simple and honest,** plus the scripted bad requests. An ingenious planner makes the run hard to read,
and the stack's worst case is the scripted requests.

## Invariants and measures

- **An invariant is a property a record states**, cited in its message: outstanding below `K_up`, a lease's count within `K`, no lease
  past the intent, no lease held while alone. The run should end with zero. A nonzero count is a simulator bug or a major finding.
- **A counterfactual re-evaluation is the strongest invariant**: remove the peer-originated labels from a permitted request and evaluate
  it again. `actuate` does this for ADR-0065 §1. Use the same pattern for any "X must not have enabled this".
- **A measure is what the use case was for**: sector coverage, claims decided in SLA, downtime. Compute it in the state, per tick, and
  report the gaps. Without one, a run can pass every check and deliver nothing.

## Bug or finding

| Observed | Verdict |
|---|---|
| An invariant failed, and the world did something a record forbids | Bug in the world |
| A flicker at every renewal, an event in the wrong tick | Bug in the tick ordering |
| A bundle errors on an input field | Bug in the fixture or the bundle. Fix before going on |
| A floor error rather than a deny | Bug in the world's lift. The trace shows the diagnostic |
| The plan says one thing and the measure another | **Finding** |
| A rule refuses everything, or nothing | **Finding**, if the rule is as written and the input is right |
| A workflow never finishes because an edge cannot fire | **Finding** |
| Nothing was refused all run | The scenario is too kind. Add requests |
