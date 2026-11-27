# Beyond the two-command POC: containers first, Kubernetes second

> Let's talk about a next step beyond the proof-of-concept demonstration described in the derived doc. Is a local
> kubernetes deployment feasible? Or should a docker container only version be first?

(The custodian's prompt of 2026.11.26. The answer was given as a plan, and the custodian approved it before the
build.)

**2026.11.26** · derived · a reading, not a record · prepared by Claude at the custodian's request · basis: the tree
at `f3c0bfb` (`main` after pull request #103), with
[`topak-shortest-path-to-poc-2026.11.26.md`](topak-shortest-path-to-poc-2026.11.26.md) (cited below as *the POC
doc*), `mechanism/crates/topak-node/src/{config,net,api}.rs`, `mechanism/crates/topak-contain/src/docker.rs` and
`mechanism/docker-compose.yml` · every command in §3 was run in the session, on macOS arm64 with Docker 29.9.3 · the
same commit adds `mechanism/Dockerfile`, `mechanism/compose.cluster.yml` and `mechanism/scripts/faults.sh`, and
changes the three scripts under `mechanism/scripts/` that the POC doc's commit changed

Nothing here is ratified, and this document proposes no decision text. A cluster on one Docker host is a
demonstration and not a deployment. The POC doc's §6 still says what an audience must be told, and §6 here adds to
it. Each lead in §7 is for the custodian, and no entry is made.

---

## 0. Verdict

1. **A local Kubernetes deployment is feasible, but containers come first.** Nothing in the reference stops it.
   The compose stage is not a detour, either: the image and the configs that name replicas by service are half of
   what Kubernetes needs. §1.
2. **The compose cluster is built and runs.** It has three replicas in three containers, real TCP between them,
   real Kafka, and an OPA sidecar beside the in-process Wasm bundle. The POC's eight ADMIT and DENY lines came out
   unchanged, and the lease's round topics appeared in Kafka. §2 and §3.
3. **It shows two things the POC could not: a crash and a partition.** The leader was killed, the two survivors
   kept ordering, and the restarted replica caught up. Then the leader was cut off from the network: an entry
   through it was not ordered, an entry through the other two was, and it converged once reconnected. §3.
4. **The POC doc's step 2 runs as written** on today's tree, with the replicas on the host, Kafka and the sidecar
   in Docker. That answers its L-3. §3.
5. **One snag was found and fixed:** `docker compose start` on a replica re-ran the init job, which emptied the
   dev volume under the running replicas. §4.

---

## 1. Why containers first

- **The Kafka and sidecar path had not been run since 2026.09.25** (POC doc L-3). Kubernetes on top of it would
  have stacked new unknowns on old ones.
- **Compose already gives each replica its own network namespace.** That is enough to show a crash
  (`docker kill`) and a partition (`docker network disconnect`). For an audience those count for more than an
  orchestrator.
- **Kubernetes adds operations, not mechanism.** StatefulSets, volumes and sidecars interest a platform audience.
  Nothing the records claim becomes newly visible.

What the code says about Kubernetes:

| | Finding | Where |
|---|---|---|
| Fits | Peers are a static `id → "host:port"` map. The node binds its own entry and reconnects on a 200 ms loop, so DNS names work. That maps onto a StatefulSet of 3 with a headless Service | `config.rs:26`, `net.rs:41`, `net.rs:77` |
| Fits | Config paths resolve against the config file's directory, so one layout serves the host, the container and a pod | `config.rs:204-210` |
| Fits | The OPA sidecar is already a URL in the config, which is a Kubernetes sidecar on localhost | `config.rs:40` |
| Friction | The agent and operator front doors are Unix sockets only. A client must share the replica's filesystem: a container on the same volume here, a sidecar or `kubectl exec` in a pod. That is the right shape, since the front door is local to the replica | `api.rs:21` |
| Friction | Binding the node's own DNS name may race the DNS record at pod start. A listen address separate from the advertised peer address would close it. It was not hit in compose | `net.rs:41` |
| Friction | The rung-1 launcher shells out to the `docker` CLI. A pod has no Docker, and mounting the host's socket would undo what the launcher claims. A Kubernetes backend, for instance a gVisor `RuntimeClass` (the `runsc` ADR-0036 names), would be a record-level change and not scaffolding | `topak-contain/src/docker.rs` |

The demonstration never uses the launcher: the grant is at rung 0. So the third friction bounds what a Kubernetes
stage could claim, but it does not block one.

---

## 2. What was built

| File | What it is |
|---|---|
| `mechanism/Dockerfile` | A multi-stage build of `topak` and `topak-demo-tool` (release, `--locked`, Rust 1.100.0) into Debian bookworm-slim with `jq`, `perl` and `python3`. The context is the repository root, so the image carries `policies/`, `spec/*.tla` and the three floor files `topak-floor` links in with `include_str!`. Both bases are pinned by digest. The image is 373 MB, and a cold build took 1 min 17 s for cargo |
| `mechanism/Dockerfile.dockerignore` | Sends only those paths as context |
| `mechanism/compose.cluster.yml` | Project `topak-cluster`: an `init` job (`dev-init.sh --compose --kafka --opa`, once per volume), `kafka` (4.3.1, KRaft, one broker, healthchecked), `opa` (1.22.4, native arm64 and amd64), `n1` to `n3`, and a `client` under a profile that runs `smoke.py`. Every image is pinned by digest. One `dev` volume holds the rules, keys, logs and sockets. No host ports are published |
| `mechanism/scripts/faults.sh` | From the host: kill the leader, order an entry, restart it with plain `docker start`, and wait until it catches up. Then disconnect the leader, try an entry through it and through the majority, reconnect it and wait. It ends by listing the Kafka topics |
| `scripts/dev-init.sh` | `--compose` names the peers `nN:710N`, Kafka `kafka:9092` and OPA `http://opa:8181`. `TOPAK_BIN_DIR` uses prebuilt binaries and skips cargo, and `TOPAK_DEV` moves `dev/`. It empties `dev/` but keeps the directory, which is a mount point in compose, and copies `.env` into it. In compose mode it also gives the sidecar a copy of the tracked tarball under a fixed name. An unknown flag is now an error |
| `scripts/smoke.py` | Reads `TOPAK_DEV` and `TOPAK_BIN_DIR`. `TOPAK_NODES_EXTERNAL=1` (set by the `client` service) uses running replicas and starts none. It reads the bundle revision from `dev/.env` when present |
| `scripts/build-bundle.sh` | Signs with `$TOPAK_BIN_DIR/topak` when that is set |

The tool's allowlist id pins its binary. The image's Linux binary therefore has a different id from the host's
(`wordcount@9e07…a689` against `wordcount@d83e…f8b`), which is why the rules are generated inside the image and
not on the host.

`docker-compose.yml`, the host-mode file, is unchanged and still names `:latest` (§7, L-3).

---

## 3. The runs

**Cluster, smoke.** After `docker compose -f compose.cluster.yml up -d --build` and
`docker compose -f compose.cluster.yml run --rm client`:

```text
grant a1: round 1, fence 1, contained=False (rung 0 is Mediated (ADR-0031 §3); no Attested appraisal; …)
  ADMIT  read(corpus object)                          ["B1-read-corpus"]
  DENY   read(object outside the corpus root)         "FloorNoPermit"
  ADMIT  draft(spec/Lease.tla)                        ["B2-draft-workspace"]
  DENY   draft(../escape)                             "FloorNoPermit"
  ADMIT  emit(record)                                 ["B4-emit-own-topic"]
  DENY   invoke(wordcount) — bundle has no schema     {"Bundle": "bundle did not allow"}
  ADMIT  submit(workspace)                            ["B5-submit-own-artifact"]
  DENY   emit after submit                            {"Mechanism": {"LeaseEnded": "submitted"}}
fence_epoch via replica 2: slot 6, {'EpochIncremented': {'epoch': 1}}
replica 1: leader=True last_applied=6 epoch=1 candidates=1 live=0
```

**K and the sidecar took part.** Kafka then held `topak.<id>.build.a1.e0.r1` and its `.after` topic. The OPA
log showed `POST /v1/data/topak/bundle/allow` requests from a replica on the cluster network. The POC run in
memory exercised neither.

**Cluster, faults.** `scripts/faults.sh` on the same cluster, 12 s:

```text
== 1. crash: kill replica 1 (the leader)
fence_epoch through replica 2, with 1 down:
{"slot":7,"applied":{"EpochIncremented":{"epoch":2}}}
  replica 1: no answer
  replica 2: {"leader":true,"last_applied":7,"epoch":2}
  replica 3: {"leader":false,"last_applied":7,"epoch":2}
restart replica 1
replica 1 is back and has caught up:
  replica 1: {"leader":false,"last_applied":7,"epoch":2}

== 2. partition: disconnect replica 2 (the leader) from the network
fence_epoch through replica 2 (the minority):
  (no reply in 5 s: not ordered)
fence_epoch through replica 1 (the majority):
{"slot":8,"applied":{"EpochIncremented":{"epoch":3}}}
  replica 1: {"leader":false,"last_applied":8,"epoch":3}
  replica 2: {"leader":true,"last_applied":7,"epoch":2}
  replica 3: {"leader":true,"last_applied":8,"epoch":3}
reconnect replica 2
replica 2 converged:
  replica 2: {"leader":false,"last_applied":8,"epoch":3}
```

Three points for whoever presents this:

- **Two replicas said `leader=true` at once** during the partition. Only one of them could reach a majority, and
  only that one ordered anything. `status` reports the replica's own belief, not that it can reach a quorum (L-5).
- **The minority's request was not applied after the heal either.** All three ended at slot 8, epoch 3.
- **Replica 1 caught up to slot 7, which was decided while it was down.** It must have learned that slot from its
  peers. Its log was on the volume when it restarted. No line in the node log says whether it replayed that log
  first (L-4).

**Cluster, a second smoke run** after the faults took round 2, fence 10. Replica 3 led, and the grant went to
replica 1 and was forwarded. All eight lines matched, and the fence landed at slot 15 on all three.

**Host mode, unchanged.** `scripts/dev-init.sh` then `python3 scripts/smoke.py`, twice, gave the eight lines
again, with round 1 and then round 2. **Host mode with Kafka and the sidecar**, the POC doc's step 2 (`docker compose
up -d`, `scripts/dev-init.sh --kafka --opa`, `python3 scripts/smoke.py`), gave the same lines, the round topics in
Kafka, and bundle queries in the sidecar's log.

`cargo test --workspace` was not run. Nothing under `mechanism/crates/` changed.

---

## 4. The snag: init ran twice

The first `faults.sh` run killed the leader and brought it back with `docker compose start n1`. Compose started
n1's dependencies again with it, and so it re-ran `init`, which is a `service_completed_successfully` dependency.
`dev-init.sh` then emptied the dev volume under replicas 2 and 3 while they ran, generated new keys and rules, and
deleted their sockets. The script reported "no answer" from both.

Two changes:

- The `init` service runs `dev-init.sh` only when `dev/rules.json` is absent, so `down -v` is the only way to
  start again from nothing.
- `faults.sh` restarts a replica with plain `docker start <container>`, which starts nothing else.

Either change would have been enough. The guard on `init` is the one that protects a person typing compose
commands by hand.

---

## 5. Stage B: local Kubernetes, if wanted

This was not built. It would take, on kind or k3d:

- A StatefulSet of 3 with a headless Service (`publishNotReadyAddresses: true`) and a PersistentVolumeClaim per
  replica for `data_dir`. A seat's round numbers are never reused, so losing a claim is a real fault and not a
  reset.
- An OPA container in each pod, a single-broker Kafka, and the dev rules, parameters, corpus and bundle generated
  by an init Job (the tool id pins the image's binary, §2). The rules are still dev rules, labelled as such, and
  their secrets would sit in a Kubernetes Secret.
- An agent or smoke container in each pod, sharing an `emptyDir` for the sockets.
- The listen and advertise split (§1), if the DNS race shows up.
- The same two faults: `kubectl delete pod` for a crash, and a NetworkPolicy for a partition.

Stage B is worth bringing forward if the audience is a platform team deciding whether the reference fits their
cluster. For a reviewer or a funder, the compose cluster and its faults make the stronger show.

---

## 6. What an audience must be told, in addition to the POC doc's §6

- **One Docker host.** A partition here is a clean `docker network disconnect`. A crash is a `SIGKILL` with the
  disk intact. Neither stands for a slow disk, a lost disk, clock skew, a flapping link or a Byzantine replica, and
  the Paxos is crash-fault.
- **The cluster's dev volume holds every secret in the clear**, as `dev/` does on the host (`GAPS-AND-ASSUMPTIONS.md`
  G6). Anyone who can mount the volume holds the operator socket.
- **The sidecar serves the tracked tarball unsigned**, as in host mode. The node verifies revisions against the
  signed copy in `dev/bundles/`.

---

## 7. Leads for the custodian

- **L-1.** `GAPS-AND-ASSUMPTIONS.md`'s evidence row says the live smoke run has not been repeated since
  2026.09.25. The POC doc's L-1 reported a run in memory on 2026.11.26. This doc reports, from the same day, runs
  with real Kafka and the sidecar, both from the host and as a cluster. The row is not edited here.
- **L-2.** The POC doc's L-3 is answered: its step 2 runs as written at `f3c0bfb`.
- **L-3.** `docker-compose.yml` and `build-bundle.sh` still name `:latest`, and both force `linux/amd64` for OPA,
  which runs under emulation on Apple Silicon. `compose.cluster.yml` pins Kafka 4.3.1 and OPA 1.22.4 by digest, and
  OPA runs natively there. Bringing the host-mode file into line is the POC doc's L-4, and it is left to the
  custodian.
- **L-4.** No line in the node log says that a replica replayed its log at start. One info line with the slot
  replayed to would let a demonstration show recovery from the log rather than infer it.
- **L-5.** During a partition the cut-off leader still reports `leader=true`. A field in `status` that says
  whether the replica heard from a majority within the election timeout would stop an audience reading two leaders
  as split brain.
- **L-6.** If Stage B is wanted, the listen and advertise split in §1 is the one code change it is likely to need.
  A launcher backend for Kubernetes is a question for ADR-0036 and not for scaffolding.
