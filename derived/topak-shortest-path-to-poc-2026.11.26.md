# The shortest path to a proof-of-concept demonstration, and the three snags on it

> what is the shortest path to a POC demonstration implementation of a TOPAK solution? Include drop in solutions
> where/if applicaple.

> do the fix and write this up as a derived doc. and commit and push a PR

(The custodian's prompts of 2026.11.26, the second after the answer had been given in the session.)

**2026.11.26** · derived · a reading, not a record · prepared by Claude at the custodian's request · basis: the tree
at `ffd02f1` (`main` after pull request #99), with `mechanism/README.md`, `mechanism/GAPS-AND-ASSUMPTIONS.md`,
`mechanism/scripts/`, `mechanism/docker-compose.yml`, `policies/`, `spec/coupling-run.sh` and the
`use-case-simulator` skill under `.claude/skills/` · every command in §2 and §4 was run in the session, in a Linux
container with rustc 1.97.0, Java, Python 3.13 and jq, and **no Docker daemon** · the same commit changes the three
scripts under `mechanism/scripts/` that §3 names

Nothing here is ratified, and this document proposes no decision text. A demonstration is not a deployment: the
[Adopter's Guide](../ADOPTERS_GUIDE_README.md) §1 and [SECURITY.md](../SECURITY.md) stand as written, and §6 says
what an audience must be told. Each lead in §7 is for the custodian, and no entry is made.

---

## 0. Verdict

1. **The shortest path is already in the tree.** `mechanism/` is a working demonstration of the admit path. Two
   commands start three replicas and drive them with an MCP client, and one screen of output shows a floor permit,
   a floor deny, a bundle deny, a mechanism deny and a fleet fence ordered by consensus. §2.
2. **Before this commit the two commands did not work as written.** Three snags stood in the way, none of them in
   the mechanism: the smoke script read a field the grant reply no longer has, the dev setup needed Docker to
   rebuild a bundle that was already tracked, and a second smoke run was refused. All three are fixed in the
   scripts, and the two-command path was then run three times in a row. §3.
3. **Four steps go further, in order of effort**: a live agent in place of the script, real Kafka and an OPA
   sidecar, a domain story from the use-case simulator, and TLC on screen. The first and the last need no code and
   no Docker. §4.
4. **Every role already has a drop-in at the reference, except P.** Consensus is the in-house `topak-paxos`, and
   replacing it for a demonstration costs the trace replay against `Paxos.tla`. §5.
5. **The demonstration shows mediation and not confinement.** The grant says `contained=False` and lists why, and
   the floor linked is a proposed stage that is not in force. §6.

---

## 1. What "a POC demonstration" is taken to mean

A run a person can watch, on one machine, in which an agent acts through the pattern and the pattern visibly
permits some actions and refuses others, with each letter of the name doing its job. It is not a deployment, a
declaration under ADR-0023, or evidence for any claim the records do not already make.

The question was read as asking for the least work from a clean checkout to that run. So the answer starts from
what exists and counts what must be added, and it does not design a new implementation.

---

## 2. The path: two commands

From `mechanism/`:

```sh
scripts/dev-init.sh        # builds topak-node, generates keys and rules, signs the bundle, writes three replica configs
python3 scripts/smoke.py   # three replicas over TCP, the operator CLI, an MCP client on stdio
```

The first build took 2 min 28 s in the session, and the smoke run a few seconds. The output of a first run after
`dev-init.sh`, with the grant line cut at the margin:

```text
grant a1: round 1, fence 1, contained=False (rung 0 is Mediated (ADR-0031 §3); no Attested appraisal; the profile is not registered; …)
MCP tools offered: ['read', 'draft', 'invoke', 'emit', 'submit', 'abstain', 'vote']
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
replica 2: leader=False last_applied=6 epoch=1 candidates=1 live=0
replica 3: leader=False last_applied=6 epoch=1 candidates=1 live=0
```

What each line demonstrates:

| Line | Tier that decided | What it shows |
|---|---|---|
| `read`, `draft`, `emit`, `submit` admitted | Floor (Cedar), with the entry named | The floor is the only tier that can permit (ADR-0030 §1) |
| `read` outside the corpus, `draft(../escape)` | Floor | No entry permits, so the request is denied |
| `invoke(wordcount)` | Bundle (Rego compiled to Wasm) | The floor permits and the bundle refuses: a bundle can only refuse |
| `emit after submit` | Mechanism | The lease ended at submit, before policy is asked |
| `fence_epoch via replica 2` and the three status lines | Consensus | A request made at a follower is ordered, and all three replicas apply it at the same slot |

What the run does not exercise: **K**. With no flags the transport is in memory. Kafka is step 2 of §4.

---

## 3. The three snags, and what the commit changes

| | Snag | Cause | Change |
|---|---|---|---|
| S-1 | `smoke.py` stopped at its first print with `KeyError: 'note'` | The grant reply carries `contained` and `because`, and no `note` (`crates/topak-node/src/mechanism.rs`) | The script prints `because` |
| S-2 | `dev-init.sh` failed, silently, on a machine with no Docker daemon | It calls `build-bundle.sh`, which always ran OPA in Docker, and it discarded the error output | `build-bundle.sh` reuses a tarball already present under the revision it computes. `dev-init.sh` shows the build's output when the build fails |
| S-3 | A second `smoke.py` was refused at the grant, or met a replica that was not yet listening | The replicas keep their logs under `dev/run/`, and a seat's round number is never reused (`state.rs`: "round numbers are not reused"). The script also waited for socket files, which an earlier run leaves behind | The script takes the next round the seat has not had, puts the round in the draft so each run submits a new artifact, and waits until every replica answers `status` and one leads |

Three notes on the changes.

**S-2 is sound because the revision names the sources.** A bundle's revision is the SHA-256 of the sorted paths
and bytes of every non-test `.rego` file and `data.json`. In the session the revision of `policies/` at `ffd02f1`
was `3e98ed17…5d62`, the name of the tarball tracked in `mechanism/bundles/`. A tarball found under the computed
revision was therefore built from these sources. Change `policies/` and the revision changes, no tarball matches,
and Docker is needed again: this was tried, and `dev-init.sh` then stops and prints Docker's error.
`TOPAK_BUNDLE_REBUILD=1` forces a build. One thing the reuse does not check is which OPA version built the tracked
tarball, which was equally unchecked before.

**S-3 keeps state on purpose.** The alternative was to wipe `dev/run/` at the start of each run. Taking the next
round leaves the logs in place, so a second run also shows the replicas recovering from their logs, with
`candidates` rising by one each run and the epoch by one. `dev-init.sh` still starts again from nothing.

**A refusal is now readable.** `topak op` prints the reply and exits non-zero on a refusal. The script used to
raise on the exit code and lose the reply. It now returns the reply either way.

Nothing under `mechanism/crates/` changed, and no test was added or run for this commit: `cargo test --workspace`
was not run in the session.

---

## 4. Four steps further, in order of effort

| | Step | Needs | Run in the session |
|---|---|---|---|
| 1 | **A live agent in place of the script.** Grant a lease with `topak op`, then point an MCP client at `topak mcp --socket dev/run/n1/agent.sock --token <token> --domain build` | An MCP-capable agent. No code | No. `smoke.py` drives the same `topak mcp` process over the same protocol |
| 2 | **Real Kafka and an OPA sidecar.** `docker compose up -d`, then `scripts/dev-init.sh --kafka --opa` and the smoke run | Docker | No: there was no daemon |
| 3 | **A domain story.** The `use-case-simulator` skill turns a stated use case into configurations and a trace that replays, with the real bundles, the linked floor and the reference's workflow `Run`. `derived/recon-fleet-7-simulation-2026.11.10/` is a worked run | A use case, and an assistant session | No. Consensus, the network and the federation stage are modelled there, and its README says so |
| 4 | **T on screen.** From `spec/`: `./coupling-run.sh c-none-safe none Safe` | Java | Yes: `Safe` holds, 1,124 distinct states, 4 s |

Step 1 is the one that changes what an audience sees most for the least work, since the agent's own tool calls are
then admitted and refused. Step 4 is the cheapest of all and is worth showing beside the two commands, because
the formal layer is otherwise invisible in a demonstration.

---

## 5. Drop-ins, by role

| Role | At the reference | Swap for a demonstration |
|---|---|---|
| **T** | TLC from the tracked `tools/tla2tools.jar`, pinned by `tools/TLA-PIN` | None needed |
| **O**, floor | The `cedar-policy` crate (4.13), linked into `topak-floor` and pinned by digest | None. The pin is the point: a floor that can be swapped without a release is not this floor |
| **O**, bundle | Rego compiled to Wasm, run in process by `opa-wasm`, or asked of the `openpolicyagent/opa` sidecar | Any OPA build that serves the same bundle |
| **P** | The in-house `topak-paxos`, sans-IO, crash-fault | etcd or a Raft library would order the same entries. The replay of recorded runs through `spec/Paxos.tla` would no longer apply, so the swap removes evidence and adds none |
| **A** | An `rmcp` server that offers the action alphabet as MCP tools | Any MCP client or agent framework, with no change to the reference |
| **K** | `rskafka` against `apache/kafka` in `docker-compose.yml`, or in memory | A Kafka-compatible broker such as Redpanda. Untested here |

Two of these are not swaps so much as the reason the path is short. MCP on the agent side means no adapter is
written for an agent. A bundle compiled to Wasm means the demonstration needs no policy server at all.

---

## 6. What an audience must be told

- **The principal is mediated and not confined.** The grant line prints `contained=False` and its reasons. The
  mechanism attributes and authorizes the agent's actions and does not bound its effects (residual-risk statement,
  as the Adopter's Guide §1 quotes it).
- **The floor linked is `floor/proposed/workflow-floor.cedar`, which is not in force** (`mechanism/README.md`,
  crate table).
- **The rules are dev rules.** `dev-init.sh` generates every key and writes the secrets to `dev/secrets/` in the
  clear (`GAPS-AND-ASSUMPTIONS.md` G6). The first lease comes from whoever reaches the operator socket.
- **One machine, three processes.** The run shows ordering among replicas and says nothing of a partition, a slow
  disk or a Byzantine replica. The Paxos is crash-fault.
- **`GAPS-AND-ASSUMPTIONS.md` lists the rest**, and it is the document to hand a reader who asks what is real.

---

## 7. Leads for the custodian

- **L-1.** `GAPS-AND-ASSUMPTIONS.md`'s evidence row says the live smoke run has not been repeated since 2026.09.25.
  It was repeated on 2026.11.26 at `ffd02f1` with the scripts as this commit leaves them, in memory, with no Kafka
  and no sidecar. The row is not edited here.
- **L-2.** S-1 went unseen because nothing runs `smoke.py`. The `results` workflow builds the reference for its
  tests, and a step that ran `dev-init.sh` and `smoke.py` there would have caught it. Whether a script that is not
  evidence belongs in that workflow is the custodian's to say.
- **L-3.** Step 2 of §4 was not run. The Kafka and sidecar path has the same age as the snags above and may have
  its own.
- **L-4.** The reuse in S-2 trusts whichever OPA built the tracked tarball. Recording the OPA version beside the
  tarball, or pinning the image by digest in `build-bundle.sh` and `docker-compose.yml` (both name `latest`), would
  close that.
