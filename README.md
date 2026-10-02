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

- **How it fits together:** [Theory of Operation](narrative/theory-of-operation.md) (revision 10, tag `ToO-rev10`)
- **State of record** (what is ratified, owed and open): [Genesis Checkpoint G7](checkpoints/topak-genesis-checkpoint-G7-2026.10.01.md). Where it and the narrative disagree, the checkpoint wins.
- **Vocabulary:** [Glossary](narrative/glossary.md)

## Layout

| Path | Contents |
|---|---|
| [`decisions/`](decisions/) | Architecture decision records, ADR-0001 onward ([index](decisions/README.md)) |
| [`checkpoints/`](checkpoints/) | Genesis checkpoints, the state of record; the layout map from the 2026.09.30 cut ([README](checkpoints/README.md)) |
| [`narrative/`](narrative/) | The living layer: the Theory of Operation and the glossary, cut with each checkpoint, and the closed archive of earlier revisions ([README](narrative/README.md)) |
| [`spec/`](spec/) | TLA+ modules, run scripts, generators, and dated TLC results ([README](spec/README.md)) |
| [`floor/`](floor/) | Draft genesis policy floor in Cedar, with tests and gates ([README](floor/README.md)) |
| [`policies/`](policies/) | Rego bundle-tier policies and tests |
| [`mechanism/`](mechanism/) | Rust reference implementation of the admit path ([README](mechanism/README.md), [gaps](mechanism/GAPS-AND-ASSUMPTIONS.md)) |
| [`slm/`](slm/) | Small-model pre-training and the ADR-0035 lineage rehearsal ([README](slm/README.md)) |
| [`derived/`](derived/) | Dated, frozen analyses, reviews and assessments ([index](derived/README.md)) |
| [`manifests/`](manifests/) | Digest manifests for checkpoint, reference and rehearsal cuts, with an index of what each measures ([README](manifests/README.md)) |
| [`process/`](process/) | The genesis cleanup's process logs ([README](process/README.md)) |
| [`tools/`](tools/) | The TLC jar and wrappers, the TLAPS wrapper, the installers, and the manifest and reference checkers |
| [`diagrams/`](diagrams/) | Diagrams and their generators |

## Running things

- **Model checking:** `tools/tlc` and `tools/tlc-workers` wrap TLC over the tracked `tools/tla2tools.jar`; each
  module has a `*-run.sh` in `spec/` ([README](spec/README.md)).
- **Proofs:** `tools/tlapm` wraps the TLA+ Proof System, which `tools/install-tlaps.sh` installs beside it (1.9 GB,
  not tracked); `spec/proof-results.sh` checks a `spec/*_proof.tla` module and prints its results file.
- **Verifying a cut:** `tools/verify-manifest.sh --all` checks every manifest at the commit it measured;
  `tools/check-refs.py` checks every path a document cites.
- **Floor, mechanism, SLM:** see the README in each directory.

## License

Code, specifications, policies and tooling are Apache-2.0 ([LICENSE](LICENSE)); documentation is CC BY 4.0
([LICENSE-DOCS](LICENSE-DOCS)). See [NOTICE](NOTICE) for how the split applies.
