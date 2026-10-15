# TOPAK

TOPAK is a safe-by-design architecture pattern for agentic AI collaboration. It treats every
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

- **How it fits together:** [Theory of Operation](narrative/theory-of-operation.md) (revision 15, tag `ToO-rev15`)
- **State of record** (what is ratified, owed and open): [Genesis Checkpoint G11](checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md). Where it and the narrative disagree, the checkpoint wins; where a frozen checkpoint is known to be wrong, [`checkpoints/README.md`](checkpoints/README.md) says so.
- **Vocabulary:** [Glossary](narrative/glossary.md)
- **Reviews:** [Reviewer's Guide](REVIEWERS_GUIDE_README.md): guidance for potential reviewers.
- **Building on the pattern:** [Adopter's Guide](ADOPTERS_GUIDE_README.md) (draft): the deployment declaration, with the reference worked as the example, and the conformance checklist

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
| [`tools/`](tools/) | The TLC jar and wrappers, the TLAPS wrapper and pin, the Lean pin, report and sync, the installers, and the manifest and reference checkers |
| [`diagrams/`](diagrams/) | Diagrams and their generators |

## Running things

### Model checking

`tools/tlc` and `tools/tlc-workers` wrap TLC over the tracked `tools/tla2tools.jar`; each module has a `*-run.sh` in
`spec/` ([README](spec/README.md)).

Run TLC on `Coupling` under a config you write, here `Coupling.cfg` with
`SPECIFICATION Spec`, `INVARIANT Safe` and `CONSTANTS Mut = "none"  K = 1  R = 3  MaxRound = 2` (from `spec/`):
```sh
../tools/tlc -config Coupling.cfg -deadlock Coupling.tla
```

Run the same check with a worker per CPU core (from `spec/`):
```sh
../tools/tlc-workers -config Coupling.cfg -deadlock Coupling.tla
```

Run a module's checks through its run script, which writes the config itself: here `Coupling`'s `Safe` invariant
with no mutation, under a run named `c-none-safe` (from `spec/`; each script's header gives its arguments):
```sh
./coupling-run.sh c-none-safe none Safe
```

### Proofs

`tools/tlapm` wraps the TLA+ Proof System. The build pinned has two known unsound cases, recorded against its
trusted-base row in Batch 37 (ADR-0046 A2): write proofs by `spec/proof-certification.md` §10, and run
`spec/proof-scan.sh` on every new proof module.

Install the pinned prover beside the wrapper (1.9 GB, not tracked):
```sh
tools/install-tlaps.sh
```

Check a proof module, here `Coupling_proof`, and write its results file (from `spec/`):
```sh
./proof-results.sh Coupling_proof > Coupling-proof-results-2026.10.13.txt
```

Scan a proof module, here `Coupling_proof`, for the known unsound cases (from `spec/`; with no module named it scans
every `*_proof.tla`, about 16 minutes):
```sh
./proof-scan.sh Coupling_proof > proof-scan-results-2026.10.13.txt
```

Check every proof results file against the tree and the pin:
```sh
spec/proof-sync.sh
```

### Lean

Three packages prove in Lean what the TLAPS proofs and the gates claim, by a second route (ADR-0053, ratified in
Batch 36). `spec/lean/` re-encodes sixteen modules, and checks the `Seats`, `FloorComposition` and `Emergency`
encodings against TLC's state graphs. `mechanism/lean/` transcribes `admit.rs`, `clock.rs` and the floor wrapper and
proves the admit decision a step of `FloorComposition`. It also models `State::apply`'s seat and lease arms and proves
that model refines `Seats`. It proves `Coupling`'s properties of a second model built on the first, and replays the
reference's recorded traces through both. `floor/lean/` states the floor in Cedar's verified model.

Install the toolchain `tools/LEAN-PIN` names, through elan (not tracked):
```sh
tools/install-lean.sh
```

Build and check the specification package (from `spec/lean/`):
```sh
./results.sh > TopakSpec-results-2026.10.13.txt
```

Build and check the mechanism package (from `mechanism/lean/`):
```sh
./results.sh > Admit-results-2026.10.13.txt
```

Build and check the floor package (from `floor/lean/`; needs `cedar` on `PATH`):
```sh
./results.sh > TopakFloor-results-2026.10.13.txt
```

Check every Lean results file against the tree and the pin:
```sh
tools/lean-sync.sh
```

### Verifying a cut

Check every manifest at the commit it measured:
```sh
tools/verify-manifest.sh --all
```

Check every path a document cites:
```sh
tools/check-refs.py
```

### Floor, mechanism, SLM

See the README in each directory.

## License

Code, specifications, policies and tooling are Apache-2.0 ([LICENSE](LICENSE)); documentation is CC BY 4.0
([LICENSE-DOCS](LICENSE-DOCS)). See [NOTICE](NOTICE) for how the split applies.
