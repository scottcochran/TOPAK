# Deployment shapes

Choose by the questions below, and read the records for the shape chosen. A use case can combine shapes. recon-fleet-7 is
a command chain whose intent boundary runs a staff DAG and whose autonomous plane runs a mesh.

| Question | If yes |
|---|---|
| Is the work a fixed sequence with sign-offs? | Commanded workflow |
| Does the work loop, or relieve itself, with no fixed length? | Mesh |
| Does the system change its own rules, code or policy? | Build and promote |
| Do bodies act while out of reach of a person or of a quorum? | Command chain |
| Is there more than one level of authority? | Command chain |
| Can any effect not be undone? | Add a release seat, and read ADR-0060 |

## Commanded workflow

Agents and people on one plane, under a promoted DAG. People hold the chosen edges.

- **Real:** bundles, the Cedar floor, the workflow `Run`.
- **Modelled:** the lift, Paxos, transport, containment, and whatever the agents do.
- **Records:** ADR-0030 (composition), ADR-0040 (Run alphabet), ADR-0047 (labels), ADR-0049 (handles), ADR-0054 (workflow).
- **World:** `--shape commanded`. Drive `WorkflowRun.step`, once per tick for a workflow that takes time, or `drive` for
  one that happens in an instant.
- **Rung:** the reference refuses a seating above rung 0 at load. Declare the rung the use case needs, and let
  `check_deployment.py` report the refusal as the provisional limit it is.

## Mesh

A workflow with cycles, under a budget. Each round is one activation.

- **Real:** as above, plus the budget and causal history.
- **Records:** add ADR-0055. Read its failure rules (§8) and fan-out scope (§4).
- **Not built:** an `all` join in a mesh. So a mesh cannot wait for several branches, and `close` joins `any`.

## Build and promote

Thinkers author, grant seats vote, and a tally promotes. Use this when the use case's interesting events are changes to
itself.

- **Real:** the Build alphabet in the floor (`lift.build_action`), `opa test` as the gate.
- **Modelled:** the tally's arithmetic, unless you lift `Vote` for each voter, which is real and better.
- **Records:** ADR-0022, ADR-0024, ADR-0030.

## Command chain

A tree of planes under charters: commanded planes, an intent boundary, autonomous planes of bodies, each a trusted
governor and a Byzantine stack. All of it is ADR-0059 to ADR-0068, Proposed and unbuilt.

- **Real:** the bundle chain, the workflow `Run`, and the floor's existing rules, with `"floor": "cedar"`.
- **Modelled:** every overlay rule in `overlay.py`: leases by count and ticks, `K_up` and watermarks, the membership
  schedule, alone and terminal behaviour, peer topics, revocation. Each names its FD entry or section.
- **Records:** ADR-0059 charters, ADR-0060 intent and release, ADR-0061 consensus, ADR-0062 governor, ADR-0063 outstanding
  bound, ADR-0064 ticks, ADR-0065 peers, ADR-0067 floor federation and ROE, ADR-0068 trust roots.
- **World:** `--shape autonomous`. Copy the structure of `examples/recon-fleet-7/world.py`.
- **Open choices** to take and list: ADR-0060 §5's unattended rule, and each ⟨Q⟩ the charter fields leave open.
- **Several autonomous planes:** add each to `self.auto`, each with its own bodies and mesh. The kernel steps them in
  order. The recon example has one, so a multi-plane world is the kernel's least-tested path. Say so if you use it.

## What the shape does not change

The admit rule, `floor_permit ∧ ¬bundle_deny`, and the fact that a bundle can only refuse. If a use case seems to need
a bundle to grant something, it needs a seat, a charter or an allowlist entry instead.
