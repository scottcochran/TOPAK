# TOPAK admit-path reference mechanism

A Rust baseline of the verified object's admit path: the part of TOPAK that decides, orders
and performs every effect an agent causes. It is a reference, not a deployment. It runs the
archetype values and nobody ships the archetype. Read [GAPS-AND-ASSUMPTIONS.md](GAPS-AND-ASSUMPTIONS.md)
before trusting anything here.

```text
 agent ──MCP/stdio──▶ topak mcp ──unix socket──▶ replica
                                                   1 session → ActionRequest (seat, lease, epoch)
                                                   2 local expiry (ADR-0032)          liveness
                                                   3 epoch fence, lease, alphabet     mechanism
                                                   4 lift → one frozen input          syntactic
                                                   5 floor: Cedar, linked, pinned     can permit
                                                   6 bundle: OPA sidecar | WASM       can only refuse
                                                   7 Admit ─▶ Paxos ─▶ apply (re-check 3)
                                                   8 effect: read · draft · tool (MCP) · emit (Kafka)
```

**admit ⟺ floor_permit ∧ ¬bundle_deny** (ADR-0030 §1). A floor error is a deny. Anything but an
affirmative bundle `true`, from the bundle revision the lease names, is a deny.

## Crates

| Crate | What | I/O |
|---|---|---|
| `topak-core` | Types, lease (ADR-0031), rules floor (ADR-0026), tally (ADR-0024), lift, composition, replicated state | none |
| `topak-paxos` | Sans-IO crash-fault Multi-Paxos plus a `Voting` ghost | none |
| `topak-floor` | Cedar engine with the proposed floor's `workflow` stage compiled in (`floor/proposed/workflow-floor.cedar`, `workflow.cedarschema`; since 2026.10.05 a proposed stage is linked in place of the genesis floor, and since 2026.10.08 this one, which is not in force), pinned by digest | none |
| `topak-bundle` | OPA sidecar client; local OPA WASM fallback bound to the lease's bundle | HTTP |
| `topak-transport` | Round topics over `rskafka` (or in memory) | Kafka |
| `topak-mcp` | The alphabet as MCP tools (`rmcp` server); downstream tool host (`rmcp` client) | stdio |
| `topak-contain` | The launcher (ADR-0036 §6): backends, the guest channel, appraisers, the bridge; `topak-demo-guest`, a scripted occupant. Rung 1 real; rung 3 SIMULATED behind feature `sim`. And the Run tool host, `wasmtool` (ADR-0034 A2, pending) | processes, docker, the declared target |
| `topak-node` | Replica: Paxos driver, WAL, admit pipeline, effects, sockets, `topak` CLI | all |

## Run it

```sh
cargo test --workspace --release           # 155 tests (2026.10.08); needs a built bundle (next line); builds topak-demo-guest
TOPAK_DOCKER_IMAGE=<image with python3> cargo test --release -p topak-contain --test launch   # + a real container round (skipped without it)
scripts/build-bundle.sh                    # policies/ → bundles/<revision>.tar.gz (docker, OPA); TOPAK_BUNDLE_SECRET=<hex> also writes <revision>.sig

TOPAK_TRACE_DIR=/tmp/t cargo test --release -p topak-core --test mutations   # record every apply …
../spec/mechanism-trace-run.sh /tmp/t/*.jsonl                                 # … replay it through spec/Mechanism.tla,
                                                                             # and read each state against ConfinementRefinement.tla
../spec/mechanism-trace-results.sh > ../spec/Mechanism-trace-results-<date>.txt  # every suite, one results file
(cd lean && ./results.sh > Admit-results-<date>.txt)   # Lean: admit.rs, clock.rs, the floor wrapper and a model of apply, proved, with the kernel replay (lean/README.md)
(cd lean && ./seats-replay.sh > SeatsReplay-results-<date>.txt)   # every suite traced and replayed through the Lean model of apply
(cd lean && ./coupling-replay.sh > CouplingReplay-results-<date>.txt)   # … and through the Coupling-shaped model on it
../tools/lean-sync.sh                      # STALE when a file the Lean results transcribe, model or replay moved
scripts/dev-init.sh                        # 3 replicas, in-memory transport, WASM bundle only
python3 scripts/smoke.py                   # live: processes, TCP, operator CLI, MCP client

docker compose up -d                       # Kafka :9092, OPA sidecar :18181
scripts/dev-init.sh --kafka --opa
python3 scripts/smoke.py
docker compose down
```

Point an MCP-capable agent at a session:

```sh
topak op --socket dev/run/n1/operator.sock '{"op":"grant", ...}'      # returns a token
topak mcp --socket dev/run/n1/agent.sock --token <token> --domain build
```

Operator requests are `grant`, `renew`, `end_round`, `revoke` (targeted; names a principal, Persona or
confinement digest), `fence_epoch` (the fleet fence), `issue`, `gates_passed`,
`register_profile`, `launch` and `status`, with `control` for an operator's signed request and
`prepare_emergency` and `activate` for an emergency seating, `load_workflow` and `workflow_status`
for a workflow; `break_glass_approve` is retired and refused (ADR-0052). See
`crates/topak-node/src/ops.rs`.
`topak keygen`, `topak sign`, `topak tool-digest`, `topak check-rules` and `topak profile-digest`
are the helpers.

## Launching a guest (ADR-0036 §6)

A node with a `contain` block in its config launches, appraises, grants to itself and bridges:

```json
"contain": {
  "backends": { "1": { "kind": "process", "command": "target/release/topak-demo-guest",
                       "args": ["--model", "persona/model.json", "--script", "read,draft,submit"] } }
}
```

1. Draft the profile as the only file of an authoring round, submit it, pass the gates, promote it;
   then `{"op":"register_profile","profile":"<the file's text>"}`. `topak profile-digest <file>` prints
   the digest a lease will name and the artifact digest promotion keys on.
2. Declare the seat's rung in the rules (`"rung": 1`; rung 3 also needs `verifier_keys`).
3. `{"op":"launch","principal":…,"seat":…,"profile":<digest>,"bundle":…,"alphabet":[…],"ttl_ms":…,"round":…,"role":"author"}`.
   The reply says `attested`, `unattestable` (nothing granted) or `contested` (the principal revoked),
   and for a grant, `contained` and every reason it is not. There is no token: the bridge is the session.

A `sim-cvm` backend and a `sim` verifier need a build with `--features sim`, and count only when an
anchor issuance puts the simulator's key in `verifier_keys`. What they reach is SIMULATED.

## Where the corpus is in the code

- The floor text is **not copied**. `topak-floor` includes `../floor/proposed/workflow-*` and `../floor/genesis-values.json` by path and refuses to load
  unless the bytes match the digests the gate run recorded. Changing the floor means re-running
  the gates and changing the pin, which is a mechanism release.
- **A bundle loads only under a signature** over its revision that verifies under a key in the rules' `bundle_keys`
  (ADR-0044). The tests sign a copy under their own key; `dev-init.sh` signs one into `dev/bundles/`.
- The bundle entrypoint is `policies/bundle.rego` (`data.topak.bundle.allow`), which composes
  `policies/tool_invocation.rego`.
- `PROVISIONAL (<tag>)` in the code marks every place a gap or assumption lives.
- **One function is proved, not only tested.** `lean/Topak/Admit.lean` transcribes `admit.rs` into Lean 4 and proves
  `FloorComposition.tla`'s three composition properties and ADR-0030 §1's `admit ⟺ floor_permit ∧ ¬bundle_deny`
  of the transcription; `lean/Topak/Clock.lean` does the same for `clock.rs`'s subtracting interval, the margin
  moving expiry earlier and never later; `lean/results.sh` rebuilds both and prints the results file. The transcription is read against
  the Rust, not generated from it ([lean/README.md](lean/README.md)).
- **`apply`'s seat rules are proved of a model and checked against the traces.** `lean/Topak/SeatsModel.lean`
  models the grant, renewal, admit, end-of-round, revocation, fence and issuance arms of `State::apply` on the
  leases, the live index and the seat kinds, every other check an oracle that can only refuse. It proves ADR-0037
  §1 and §4 of the model at any number of seats, and the model a refinement of `Seats.tla` at that module's
  constants. `lean/seats-replay.sh` runs every recorded trace through the model and compares each step with the
  reference's; on 2026.10.06 all 82 traces matched. Evidence, not a stage of T-0045-28 (ADR-0053 R4).
  `lean/Topak/CouplingModel.lean` narrows that oracle with ADR-0039's checks, the cross-round condition, the round
  bound, heartbeats and coupling, and proves at any number of seats that a Run Thinker's live round has at most `K`
  effects unread by some cell Observer and its last round was read to the seal; `lean/coupling-replay.sh` replays
  every trace through it, sequence numbers, watermarks and seals compared (ADR-0053 R5).
- Records are **pinned, not followed silently**. `corpus-pins.sha256` holds the digest of every
  record and TLA+ module the reference follows, as it last followed them. `cargo test -p topak-core
  --test drift` fails when a pinned file changes, or when the code cites a record that is not
  pinned. To clear it, review the change against the code, bring the code into line or register the
  divergence in GAPS-AND-ASSUMPTIONS.md, then replace the pin line (`shasum -a 256 <path>` from
  the repository root).

## Operators (ADR-0050, provisional)

Where the rules declare a seat of kind `operator`, an operator's request is signed and decided by the
floor's control entries (`C1` to `C9`), and the unsigned requests on the operator socket are a
**bootstrap path** that seats and does nothing else:

```json
{ "op": "control",
  "request": { "operator": "op1", "epoch": 0, "ctr": 7, "action": "end_round", "target": "a1" },
  "sig": { "key": "<the seat's key>", "sig": "<over topak/control/v1 and {chain, request}>" } }
```

The six actions are `regrant`, `renew`, `attest_gates`, `end_round`, `revoke` and `fence_epoch`
(`crates/topak-core/src/control.rs`). An operator's own lease needs a sign-on assertion under a key in
the rules' `provider_keys`, and so does a deny it makes with no live lease. Rules that declare no
operator seat leave the socket as it was (D-0050-1); `scripts/dev-init.sh` writes such rules.

## Break-glass (ADR-0052, provisional)

Break-glass is an emergency seating, and the floor has no X1. A seat of kind `emergency` is leased
only by an `activate` request carrying a quorum of the break-glass roster's signatures over one
person's key, one round and the task. The person then signs each action with that key; there is no
bearer token to the lease. The seat may call what its seating's envelope holds: by default every
Run allowlist entry in force in the domain. An operator may stop it and nobody may regrant it.

## Workflows and meshes (ADR-0054, ADR-0055; Proposed)

A workflow is promoted like any other Build artifact: one file, `workflow.json`, in an author's workspace,
submitted, gated and voted on. `load_workflow` loads it only once that artifact is promoted, and from then on the
mechanism grants every lease it issues, each node's when the node becomes ready and an orchestrator's for each
decision event, under the promotion's authority and with nothing wider than the seating:

```json
{ "kind": "dag", "root": "s", "sinks": ["j"],
  "nodes": { "s": { "seat": "ws", "outcomes": ["ok", "bad"], "lineage": "A", ... }, ... },
  "edges": { "e1": { "from": "s", "to": "b", "kind": "chosen", "delivery": "clear",
                     "guard": { "outcome": { "node": "s", "any_of": ["ok"] } } }, ... },
  "orchestrator": { "seat": "orc", "alphabet": ["Route", "Report"], ... } }
```

A worker ends its round by reporting `{"outcome": ...}` from its node's enum. A computed edge fires once its
source's cell Observer has read the round to the seal. An orchestrator chooses with the `route` tool among the
chosen edges the mechanism has enabled, and the route is checked again where it is applied. A `mesh` may have
cycles and does not load without a `budget`. `workflow_status` shows a run and, as a bootstrap, hands out the
sessions this replica opened for its leases (`GAPS-AND-ASSUMPTIONS.md` I49).

## Run tools held to their channel (ADR-0034 A2)

A Run tool listed under `wasm_tools` in the node's config runs as a Wasm module whose only network
capability is its declared target. The config says where the module is and what its bytes are:

```json
"wasm_tools": { "valve@<module sha256>": { "module": "tools/valve.wasm", "module_sha256": "<sha256>" } }
```

It says nothing of the channel. The target is the one the tool's allowlist entry declares, in the
bundle revision the lease names (ADR-0049 §5; ADR-0034 A2):

```json
"valve@<module sha256>": { "name": "valve", "digest": "<module sha256>", "domain": "run", "...": "...",
                           "channel": { "kind": "tcp", "target": "plc.internal:502" } }
```

Name the same ids in the parameters' `wasm_tools`; a replica that does not host one refuses to start.
A Run profile (`"domain": "run"`) that says P4 passes then admits `Actuate` of those tools only. The
module's interface is in `crates/topak-contain/src/wasmtool.rs`: PROVISIONAL, a core module and not
the component A2 names.
