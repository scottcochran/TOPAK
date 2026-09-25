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
| `topak-floor` | Cedar engine with `floor/genesis-floor.cedar` and `genesis.cedarschema` compiled in, pinned by digest | none |
| `topak-bundle` | OPA sidecar client; local OPA WASM fallback bound to the lease's bundle | HTTP |
| `topak-transport` | Round topics over `rskafka` (or in memory) | Kafka |
| `topak-mcp` | The alphabet as MCP tools (`rmcp` server); downstream tool host (`rmcp` client) | stdio |
| `topak-node` | Replica: Paxos driver, WAL, admit pipeline, effects, sockets, `topak` CLI | all |

## Run it

```sh
cargo test --workspace --release           # 40 tests; needs a built bundle (next line)
scripts/build-bundle.sh                    # policies/ → bundles/<revision>.tar.gz (docker, OPA)

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

Operator requests are `grant`, `renew`, `end_round`, `revoke`, `issue`, `gates_passed`,
`break_glass_approve` and `status`; see `crates/topak-node/src/ops.rs`. `topak keygen`,
`topak sign`, `topak tool-digest` and `topak check-rules` are the helpers.

## Where the corpus is in the code

- The floor text is **not copied**. `topak-floor` includes `../floor/*` by path and refuses to load
  unless the bytes match the digests the gate run recorded. Changing the floor means re-running
  the gates and changing the pin, which is a mechanism release.
- The bundle entrypoint is `policies/bundle.rego` (`data.topak.bundle.allow`), which composes
  `policies/tool_invocation.rego`.
- `PROVISIONAL (<tag>)` in the code marks every place a gap or assumption lives.
- Records are **pinned, not followed silently**. `corpus-pins.sha256` holds the digest of every
  record and TLA+ module the reference follows, as it last followed them. `cargo test -p topak-core
  --test drift` fails when a pinned file changes, or when the code cites a record that is not
  pinned. To clear it, review the change against the code, bring the code into line or register the
  divergence in GAPS-AND-ASSUMPTIONS.md, then replace the pin line (`shasum -a 256 <path>` from
  the repository root).
