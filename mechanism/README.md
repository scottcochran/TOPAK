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
| `topak-floor` | Cedar engine with the proposed floor's `emergency` stage compiled in (`floor/proposed/emergency-floor.cedar`, `emergency.cedarschema`; since 2026.10.05 a proposed stage is linked in place of the genesis floor), pinned by digest | none |
| `topak-bundle` | OPA sidecar client; local OPA WASM fallback bound to the lease's bundle | HTTP |
| `topak-transport` | Round topics over `rskafka` (or in memory) | Kafka |
| `topak-mcp` | The alphabet as MCP tools (`rmcp` server); downstream tool host (`rmcp` client) | stdio |
| `topak-contain` | The launcher (ADR-0036 §6): backends, the guest channel, appraisers, the bridge; `topak-demo-guest`, a scripted occupant. Rung 1 real; rung 3 SIMULATED behind feature `sim`. And the Run tool host, `wasmtool` (ADR-0034 A2, pending) | processes, docker, the declared target |
| `topak-node` | Replica: Paxos driver, WAL, admit pipeline, effects, sockets, `topak` CLI | all |

## Run it

```sh
cargo test --workspace --release           # 131 tests (2026.10.05); needs a built bundle (next line); builds topak-demo-guest
TOPAK_DOCKER_IMAGE=<image with python3> cargo test --release -p topak-contain --test launch   # + a real container round (skipped without it)
scripts/build-bundle.sh                    # policies/ → bundles/<revision>.tar.gz (docker, OPA); TOPAK_BUNDLE_SECRET=<hex> also writes <revision>.sig

TOPAK_TRACE_DIR=/tmp/t cargo test --release -p topak-core --test mutations   # record every apply …
../spec/mechanism-trace-run.sh /tmp/t/*.jsonl                                 # … replay it through spec/Mechanism.tla,
                                                                             # and read each state against ConfinementRefinement.tla
../spec/mechanism-trace-results.sh > ../spec/Mechanism-trace-results-<date>.txt  # every suite, one results file
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
`prepare_emergency` and `activate` for an emergency seating; `break_glass_approve` is retired and
refused (ADR-0052). See `crates/topak-node/src/ops.rs`.
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

- The floor text is **not copied**. `topak-floor` includes `../floor/proposed/emergency-*` and `../floor/genesis-values.json` by path and refuses to load
  unless the bytes match the digests the gate run recorded. Changing the floor means re-running
  the gates and changing the pin, which is a mechanism release.
- **A bundle loads only under a signature** over its revision that verifies under a key in the rules' `bundle_keys`
  (ADR-0044). The tests sign a copy under their own key; `dev-init.sh` signs one into `dev/bundles/`.
- The bundle entrypoint is `policies/bundle.rego` (`data.topak.bundle.allow`), which composes
  `policies/tool_invocation.rego`.
- `PROVISIONAL (<tag>)` in the code marks every place a gap or assumption lives.
- Records are **pinned, not followed silently**. `corpus-pins.sha256` holds the digest of every
  record and TLA+ module the reference follows, as it last followed them. `cargo test -p topak-core
  --test drift` fails when a pinned file changes, or when the code cites a record that is not
  pinned. To clear it, review the change against the code, bring the code into line or register the
  divergence in GAPS-AND-ASSUMPTIONS.md, then replace the pin line (`shasum -a 256 <path>` from
  the repository root).

## Operators (ADR-0050, Proposed)

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

## Break-glass (ADR-0052, Proposed)

Break-glass is an emergency seating, and the floor has no X1. A seat of kind `emergency` is leased
only by an `activate` request carrying a quorum of the break-glass roster's signatures over one
person's key, one round and the task. The person then signs each action with that key; there is no
bearer token to the lease. The seat may call what its seating's envelope holds: by default every
Run allowlist entry in force in the domain. An operator may stop it and nobody may regrant it.

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
