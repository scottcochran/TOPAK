# TOPAK

TOPAK is an architecture pattern for autonomous multi-agent collaboration guided by "safe by design" principles. It treats every
agent as Byzantine, keeps models out of the trusted computing base, and states every guarantee against what an
agent's action alphabet allows. The letters name roles, not products:

| | Role | Instrument at the reference |
|---|---|---|
| **T** | Formal specification and model checking | TLA+ / TLC |
| **O** | Policy as code: a verified floor and a per-request bundle | Cedar (floor), OPA/Rego (bundle) |
| **P** | Consensus over the control plane | Multi-Paxos |
| **A** | Agents, the principals doing the work | MCP-connected agents |
| **K** | Event transport | Kafka |

**Status:** a design corpus in its genesis phase, with a reference implementation of the admit path. It is not a
deployable system.

## Start here

- **How it fits together:** [Theory of Operation, rev 8](checkpoints/topak-theory-of-operation-2026.09.28-rev8.md)
- **State of record** (what is ratified, owed and open): [Genesis Checkpoint G4](checkpoints/topak-genesis-checkpoint-G4-2026.09.28.md). Where it and the narrative disagree, the checkpoint wins.
- **Vocabulary:** [Glossary](derived/topak-glossary-2026.09.26.md)

## Layout

| Path | Contents |
|---|---|
| [`decisions/`](decisions/) | Architecture decision records (ADR-0001 onward) |
| [`checkpoints/`](checkpoints/) | Genesis checkpoints and Theory of Operation revisions |
| [`spec/`](spec/) | TLA+ specifications, run scripts, and dated TLC results |
| [`floor/`](floor/) | Draft genesis policy floor in Cedar, with tests and gates ([README](floor/README.md)) |
| [`policies/`](policies/) | Rego bundle-tier policies and tests |
| [`mechanism/`](mechanism/) | Rust reference implementation of the admit path ([README](mechanism/README.md), [gaps](mechanism/GAPS-AND-ASSUMPTIONS.md)) |
| [`slm/`](slm/) | Small-model pre-training and the ADR-0035 lineage rehearsal ([README](slm/README.md)) |
| [`derived/`](derived/) | Reviews, assessments and reference material derived from the corpus |
| [`diagrams/`](diagrams/) | Diagrams and their generators |
| Root `*-LOG-*.md`, `RECOVERY-REGISTRY-*`, `FREEZE-*` | Process logs from the genesis cleanup |
| `SHA256SUMS-*` | Digest manifests for checkpoint (`G1`–`G4`), reference (`REF`) and rehearsal (`SLM`) cuts |

## Running things

- **Model checking:** `./install-tla.sh` fetches `tla2tools.jar` into `tools/`; `./tlc` and `./tlc-workers` wrap
  TLC. Each spec has a `*-run.sh` in `spec/`.
- **Floor, mechanism, SLM:** see the README in each directory.

## License

Code, specifications, policies and tooling are Apache-2.0 ([LICENSE](LICENSE)); documentation is CC BY 4.0
([LICENSE-DOCS](LICENSE-DOCS)). See [NOTICE](NOTICE) for how the split applies.
