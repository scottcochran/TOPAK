# Decisions

Architecture decision records, one file each, numbered in the order they were settled. **Status is as of Genesis
Checkpoint G10 (2026.10.05)**; the checkpoint is the state of record and this index is a convenience. A record is never
edited after ratification except by a typed History row: an amendment, an erratum, a revision before ratification,
or a dependent entry written when another record's ratification touches it. Accepted records that carry a
confirmation-required criterion (ADR-0029 §4: C1 privileged path, C2 exhaustiveness or confinement, C3 reversal, C4
resolves a debt) were ratified by one person and await the first post-bootstrap quorum.

`mechanism/corpus-pins.sha256` pins the digest of every record the reference follows; a test fails when one moves.

| Record | Title | Status at G8 | Superseded by |
|---|---|---|---|
| [ADR-0001](ADR-0001.md) | Rename the CI domain to `Build`; adopt `Build(Contain) → Run(Contain)` | Accepted (genesis) | |
| [ADR-0002](ADR-0002.md) | Apply the membrane in `Build` as well: `Build(Contain) → Run(Contain)` | Accepted (genesis) | |
| [ADR-0003](ADR-0003.md) | Topic per principal per round, sealed on emit, as the unit of erasure | Accepted (genesis); confirmation required: C1, for A2 only | |
| [ADR-0004](ADR-0004.md) | Separate control-plane facts from cognitive payloads | Accepted (genesis) | |
| [ADR-0005](ADR-0005.md) | Kafka is neither the ordering authority nor the system of record | Accepted (genesis), Batch 27, 2026.10.04, after G9; confirmation required: C4 | |
| [ADR-0006](ADR-0006.md) | Erasure is a privileged, modeled, consensus-ordered event | Accepted (genesis); confirmation required: C1, C4 via 0013 | |
| [ADR-0007](ADR-0007.md) | Semantic judgment is never a lift | Accepted (genesis) | |
| [ADR-0008](ADR-0008.md) | Observer replicas are not colocated with the Thinker | Superseded | ADR-0038 |
| [ADR-0009](ADR-0009.md) | Break-glass is a modeled, quorum-witnessed path, not a prohibition | Accepted (genesis); confirmation required: C1, C4 via 0013 | |
| [ADR-0010](ADR-0010.md) | The verified object is the enforcement mechanism, its epoch discipline, and a minimal policy floor | Accepted (genesis) | |
| [ADR-0011](ADR-0011.md) | Observer placement and fault-domain independence | Tombstone | |
| [ADR-0012](ADR-0012.md) | The default-deny bundle is the policy floor: pre-blessed, resident, verified | Accepted (genesis) | |
| [ADR-0013](ADR-0013.md) | Exception mechanism for privileged paths through the floor | Accepted (genesis); confirmation required: C1, C4 | |
| ADR-0014 | — | Reserved, no file (the per-class floor question) | |
| [ADR-0015](ADR-0015.md) | Effects are boundary crossings; every crossing is authorized, ordered, and auditable | Accepted (genesis); confirmation required: C2 | |
| [ADR-0016](ADR-0016.md) | The model enters the system as a Persona | Accepted (genesis) | |
| [ADR-0017](ADR-0017.md) | Archetype admits only in-house pre-trained Personas | Accepted (genesis) | |
| [ADR-0018](ADR-0018.md) | The typed lift splits: decoder in the Persona, validator in the mechanism | Accepted (genesis) | |
| [ADR-0019](ADR-0019.md) | Optional decode observability | Accepted (genesis) | |
| [ADR-0020](ADR-0020.md) | Replay scope is boundary events only | Accepted (genesis) | |
| [ADR-0021](ADR-0021.md) | Build emits to the effect stream; Build has an Observer | Accepted (genesis); confirmation required: C4 | |
| [ADR-0022](ADR-0022.md) | Typed action alphabet for Build principals | Accepted (genesis) — §1–§5, §7, §8 only | |
| [ADR-0023](ADR-0023.md) | Degeneracy as the deployment-variation relation; archetype as its unique maximum | Accepted (genesis); confirmation required: C3 | |
| [ADR-0024](ADR-0024.md) | Promotion requires a unanimous quorum | Accepted (genesis) | |
| [ADR-0025](ADR-0025.md) | The trust anchor is a havoc issuer; intent is the sole axiom | Accepted (genesis) | |
| [ADR-0026](ADR-0026.md) | The rules floor bounds every anchor issuance | Accepted (genesis) | |
| [ADR-0027](ADR-0027.md) | Genesis rules are resident | Accepted (genesis) | |
| [ADR-0028](ADR-0028.md) | The forensic floor: authority facts survive erasure and break-glass | Accepted (genesis); confirmation required: C1 | |
| [ADR-0029](ADR-0029.md) | The design process is genesis; the custodian may ratify unilaterally; the anchor bootstraps on a drafted TLA+ specification | Accepted (genesis) | |
| [ADR-0030](ADR-0030.md) | Bundles cannot add authority by construction, and the policy floor runs on a verified evaluator | Accepted (genesis); confirmation required: C1 | |
| [ADR-0031](ADR-0031.md) | The lease is the composite credential, and its grant is the instant | Accepted (genesis); confirmation required: C1; C2 for A1 only | |
| [ADR-0032](ADR-0032.md) | The clock model: clocks buy liveness, and intervals are trusted by failure direction | Accepted (genesis) | |
| [ADR-0033](ADR-0033.md) | The mechanism has a reference implementation, and it is evidence, not the verified object | Accepted (genesis) | |
| [ADR-0034](ADR-0034.md) | Confinement is attested at lease grant, and the archetype rung is a confidential VM | Accepted (genesis); confirmation required: C2, C4 | |
| [ADR-0035](ADR-0035.md) | Persona lineage is a projection of the Build log, and independence is an exclusion rule over it | Proposed | |
| [ADR-0036](ADR-0036.md) | At rung 1 the launcher is the channel: the reference's guest launcher, its profile, and a principal `Mediated` by declaration | Proposed | |
| [ADR-0037](ADR-0037.md) | The LTRO decomposes into principals: Thinker and Observer are seats, Listener and Reader are stages, and a principal holds one seat | Accepted (genesis); confirmation required: C3, C4 | |
| [ADR-0038](ADR-0038.md) | Observers are per cell, the shared group becomes the correlator, and neither needs a quorum | Accepted (genesis); confirmation required: C3, C4 | |
| [ADR-0039](ADR-0039.md) | Observer liveness is progress, not presence: Run couples every admit to it, Build couples the gate, and the correlator is never coupled | Accepted (genesis); confirmation required: C4 | |
| [ADR-0040](ADR-0040.md) | Run has its own alphabet: `Consult`, `Actuate` and `Report`, and it shares only the carrier with Build | Accepted (genesis); confirmation required: C3, C4 | |
| [ADR-0041](ADR-0041.md) | Policy obligations for Run: one envelope for each variant, and coupling on effects only | Accepted (genesis); confirmation required: C1, C4 | |
| [ADR-0042](ADR-0042.md) | Mechanism obligations for Run: the sequence counts effects, every `Actuate` leaves a record, and the round seals when the lease ends | Accepted (genesis), whole: §6 ratified in Batch 30, 2026.10.04, after G9; confirmation required: C4, and C2 for §6 | |
| [ADR-0043](ADR-0043.md) | Cell obligations for Run: what the Listener delivers, what each seat holds, and what the Observer must read | Accepted (genesis); confirmation required: C4 | |
| [ADR-0044](ADR-0044.md) | A bundle is trusted by its signature, not its file name: the bundle key lives in the issued rules | Accepted (genesis); confirmation required: C1 | |
| [ADR-0045](ADR-0045.md) | The trusted base is declared row by row, and a component enters it only if its failure can only subtract, or its identity is issued | Accepted (genesis); confirmation required: C2, C4 | |
| [ADR-0046](ADR-0046.md) | The formal layer's method is declared: TLC checks mutations and witnesses at small constants, TLAPS proves the invariants, and the prover is a trusted-base row | Accepted (genesis); confirmation required: C2, C4 | |
| [ADR-0047](ADR-0047.md) | The Listener labels what it delivers: a label on every item, and a handle in place of what is suppressed | Accepted (genesis) · Batch 34, 2026.10.05 (drafted 2026.10.03, after G9) | |
| [ADR-0048](ADR-0048.md) | A Thinker learns its tools from the mechanism: the allowlist entry carries its interface, and the Listener delivers it | Accepted (genesis) · Batch 34, 2026.10.05 (drafted 2026.10.03, after G9) | |
| [ADR-0049](ADR-0049.md) | The allowlist entry has one schema: identity, inputs, interface, labels and channel, each marked checked or claimed | Accepted (genesis) · Batch 34, 2026.10.05 (drafted 2026.10.03, after G9) | |
| [ADR-0050](ADR-0050.md) | An operator is a principal: seated by promotion, renewing within its domain under a lease, and able to deny without one | Accepted (genesis) · **provisional** · Batch 34, 2026.10.05 (drafted 2026.10.04, after G9) | |
| [ADR-0051](ADR-0051.md) | The correlator computes named folds over facts: five correlations a second reader can recompute, a judgment tier beside them, and a store that never outlives its sources | Proposed (drafted 2026.10.04, after G9) | |
| [ADR-0052](ADR-0052.md) | Break-glass is an emergency seating: a roster's quorum seats a person for one round, and the floor's exception for it is retired | Accepted (genesis) · **provisional** · Batch 34, 2026.10.05 (drafted 2026.10.04, after G9) | |
