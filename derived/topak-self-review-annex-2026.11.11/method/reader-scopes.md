# The thirteen readers' scopes

What filled `{SCOPE}`, `{DEPTH}` and `{PUSH}` in the reader brief. Readers B, D, F, H, I2 and K1 were pointed at the Reviewer's Guide §6, "Where to push"; readers A, C, E, G, I1 and J were told to leave the guide closed; reader K2 had the guide in scope as a document under review.


## Reader A

**Primary (read all of it):** `decisions/ADR-0001.md` to `decisions/ADR-0023.md` (ADR-0014 is a reserved number with no file).

**Compare against:** the Theory of Operation sections that restate these records (`narrative/theory-of-operation.md` §1 to §4, §8), `decisions/README.md`, `checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md` §1 and §6, and any later record that amends, supersedes or reverses one of these.

These are the foundations: domains, the membrane, the action alphabet, effects as boundary crossings, the Persona records, the degeneracy relation. Several are single-clause records recovered early. Ask of each whether what it says is still what the rest of the corpus does.

**One pass.** Read every clause once. Compare in depth the rows whose `since_G9` column says `new` or `changed`, and any clause that another record in your scope cites. Mark the rest `read only`.


## Reader B

**Primary (read all of it):** `decisions/ADR-0024.md` to `decisions/ADR-0029.md`: promotion and the quorum, the anchor as a havoc issuer, the rules floor, resident rules, the forensic floor, and the genesis process (ADR-0029, with amendments A1 to A4).

**Compare against:** `spec/Anchor.tla`, `spec/BreakGlass.tla`, `spec/RulesFloorBase.tla`, `spec/RulesFloorNV_rev5.tla`, `spec/NonComposition.tla` and their results and proof-results files; `checkpoints/README.md`; `checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md` §1, §4, §7, §8; `decisions/README.md`.

This is the bootstrap set and the process that governs every other record: who may ratify, what status classes exist, what a batch is, what is owed before bootstrap. Check the process records against what the corpus actually did after them: read the History rows and Status lines of ADR-0050 to ADR-0068 for how each used the status classes and ratification rules these records define.

**Full depth.** Read every row of your ledger skeleton in full. For every clause, compare it with at least one other artifact wherever one exists: the module, the policy, the code, the results file, or the record it cites.


## Reader C

**Primary (read all of it):** `decisions/ADR-0030.md`, `ADR-0031.md`, `ADR-0032.md`, `ADR-0034.md`, `ADR-0035.md`, `ADR-0036.md` (ADR-0033 belongs to another reader): bundles and the floor gates, the lease, the clock model, confinement at grant, Persona lineage (Proposed), the rung-1 launcher (Proposed).

**Compare against:** `floor/genesis-floor.cedar`, `floor/genesis.cedarschema`, `floor/genesis-values.json`, `floor/README.md`, the newest `floor/genesis-gates-results-*.txt`; `policies/*.rego`; `spec/FloorComposition.tla`, `spec/FloorRouting.tla`, `spec/Lease_A1.tla`, `spec/Confinement.tla`, `spec/Confinement_A1.tla` with their results files.

Check each record's stated entries, fields, gates and numbers against the policy text and the modules.

**One pass.** Read every clause once. Compare in depth the rows whose `since_G9` column says `new` or `changed`, and any clause that another record in your scope cites. Mark the rest `read only`.


## Reader D

**Primary (read all of it):** `decisions/ADR-0037.md` to `decisions/ADR-0043.md` and `decisions/ADR-0051.md`: seats, per-cell Observers, liveness coupling, the Run alphabet, Run policy, the Run mechanism, the Run cell, and the correlator's folds (Proposed).

**Compare against:** `spec/Seats.tla`, `spec/Observers.tla`, `spec/Coupling.tla`, `spec/Coupling_live.tla`, `spec/RunSeats.tla`, `spec/RunCoupling.tla`, `spec/RunConfinement.tla`, `spec/Correlator.tla` with their results files; the floor entries these records name (`floor/genesis-floor.cedar`, `floor/proposed/*-floor.cedar`); `floor/genesis-values.json`.

Six of these records carry a pending amendment that depends on a Proposed record. For each, check that the record makes clear what is in force today.

**One pass.** Read every clause once. Compare in depth the rows whose `since_G9` column says `new` or `changed`, and any clause that another record in your scope cites. Mark the rest `read only`.


## Reader E

**Primary (read all of it):** `decisions/ADR-0044.md`, `ADR-0045.md` (with Annex A and Annex B), `ADR-0046.md`, `ADR-0053.md`: bundle signing, the trusted base row by row, the declared formal method, and Lean as a second deductive method.

**Compare against:** `spec/theorem-premise-binding.md` and `.json`; `spec/proof-method.md`; `spec/proof-certification.md`; `spec/README.md`; `tools/TLAPS-PIN`, `tools/LEAN-PIN`; `spec/proof-scan-results-*.txt`; the READMEs of `spec/lean/`, `mechanism/lean/`, `floor/lean/`; `spec/defects/`; a sample of at least six `spec/*-proof-results-*.txt` and `*-proof-cert-results-*.txt` files.

Check every count these records and documents state (rows, modules, obligations, what certifies, what is proved in Lean) against the files, and check that every proved module has what the method says it must have.

**One pass.** Read every clause once. Compare in depth the rows whose `since_G9` column says `new` or `changed`, and any clause that another record in your scope cites. Mark the rest `read only`.


## Reader F

**Primary (read all of it):** `decisions/ADR-0047.md` to `ADR-0050.md` and `ADR-0052.md`: labels, the tool list, the allowlist entry, the operator as a principal (provisional), and break-glass as an emergency seating (provisional).

**Compare against:** `spec/Labels.tla`, `spec/ToolList.tla`, `spec/Operators.tla`, `spec/Emergency.tla`, `spec/Emergency_live.tla`, `spec/BreakGlass_A1.tla`, `spec/NonComposition_A1.tla` with their results files; `floor/proposed/README.md` and the `labels`, `control` and `emergency` stage floors; `mechanism/GAPS-AND-ASSUMPTIONS.md` where it speaks of these records; ADR-0029 §3 and A4 for what "provisional" means.

No review has read these five records as a set.

**Full depth.** Read every row of your ledger skeleton in full. For every clause, compare it with at least one other artifact wherever one exists: the module, the policy, the code, the results file, or the record it cites.


## Reader G

**Primary (read all of it):** `decisions/ADR-0054.md` (a workflow is a promoted DAG), `ADR-0055.md` (a workflow may be a mesh), `ADR-0056.md` (a call's user scope). All three are Proposed.

**Compare against:** `spec/Workflow.tla`, `spec/Mesh.tla`, their rows and results files; `floor/proposed/workflow-floor.cedar` and `floor/proposed/README.md`; `mechanism/crates/topak-core/src/workflow.rs`; and each accepted record that carries a pending amendment for these three (ADR-0015, ADR-0024, ADR-0031, ADR-0033, ADR-0037, ADR-0039, ADR-0040, ADR-0041, ADR-0042, ADR-0043, ADR-0047): read the pending text there.

The reference follows ADR-0054 and ADR-0055 before they are in force. Check what each record says it owes before ratification against what exists.

**Full depth.** Read every row of your ledger skeleton in full. For every clause, compare it with at least one other artifact wherever one exists: the module, the policy, the code, the results file, or the record it cites.


## Reader H

**Primary (read all of it):** `decisions/ADR-0057.md` (the corpus's specifications form a graph) and `ADR-0058.md` (a deployment declares its graph as an overlay). Both Proposed.

**Compare against:** `spec/specification-graph.json`, `spec/specification-graph.py`, `spec/clauses.py`, `spec/specification-graph-results-2026.11.07.txt`, `spec/inventory.py`, `spec/theorem-premise-binding.md`; the pending amendments these records put into accepted records (ADR-0033 A18, ADR-0045 A5, ADR-0053 A1); `ADOPTERS_GUIDE_README.md` on the deployment declaration; and how ADR-0059 to ADR-0068 use the word "overlay" and ADR-0058.

Check the graph's own claims (what it has nodes for, what its check reports, when it was built) against the tree, and check that every later use of these records matches what they define.

**Full depth.** Read every row of your ledger skeleton in full. For every clause, compare it with at least one other artifact wherever one exists: the module, the policy, the code, the results file, or the record it cites.


## Reader I1

**Primary (read all of it):** `decisions/ADR-0059.md` to `ADR-0068.md` (the command-chain overlay, all Proposed) and the eight TLA+ modules written for them: `spec/Federation.tla`, `Intent.tla`, `Membership.tla`, `Alone.tla`, `Outstanding.tla`, `PlaneClock.tla`, `Peer.tla`, `Release.tla`, each with its `-rows.txt`, its `-results-2026.11.10.txt`, the header and theorem statements of its `_proof.tla`, and its proof-results file.

**Your comparison is record against module.** For each record: every property, mutation, witness, constant, bound, count and check that the record states, against the module's text, its rows file and its results file. And the reverse: what each module's header says it models, abstracts or found, against the record. Read each record's History rows.

Another reader has the comparison of these records against the rest of the corpus. You need not make it.

**Full depth.** Read every row of your ledger skeleton in full. For every clause, compare it with at least one other artifact wherever one exists: the module, the policy, the code, the results file, or the record it cites.


## Reader I2

**Primary (read all of it):** `decisions/ADR-0059.md` to `ADR-0068.md` (the command-chain overlay, all Proposed), and `derived/topak-federated-c2-design-proposal-2026.11.10b.md`, the proposal they were drafted from.

**Your comparison is the overlay against the rest of the corpus.** Each overlay record lists what it depends on, relates to, relaxes, and what the archetype's records "would owe". For each such citation, open the cited record or Theory of Operation section and check that it says what the overlay says it says, and that the overlay names everything in accepted text that it contradicts. The base records are listed in your ledger skeleton (kind `base-record`); ADR-0059's provenance note names eight that its drafter did not re-read. Also check the ten records against each other, and against ADR-0058 and ADR-0029 §3 for the status they claim.

Another reader has the comparison of these records against their TLA+ modules. You need not make it.

**Full depth.** Read every row of your ledger skeleton in full. For every clause, compare it with at least one other artifact wherever one exists: the module, the policy, the code, the results file, or the record it cites.


## Reader J

**Primary (read all of it):** `decisions/ADR-0033.md` (the reference implementation, with addenda A1 to A18), `mechanism/README.md`, `mechanism/GAPS-AND-ASSUMPTIONS.md`, `mechanism/corpus-pins.sha256`.

**Compare against:** the Rust source under `mechanism/crates/` (read `topak-core/src/` in full; sample the other crates and the tests by what the documents claim about them); `spec/Mechanism.tla`, `spec/ConfinementRefinement.tla`, `spec/Mechanism-trace-results-2026.10.05.txt`; `mechanism/lean/README.md`; `mechanism/docker-compose.yml` and `mechanism/scripts/`.

Check what the documents say the code does, pins, tests and traces against the code: counts of tests, crates and markers, which records are pinned, which floor is linked, what is PROVISIONAL or SIMULATED, and whether each register row still describes the tree.

**One pass.** Read every clause once. Compare in depth the rows whose `since_G9` column says `new` or `changed`, and any clause that another record in your scope cites. Mark the rest `read only`.


## Reader K1

**Primary (read all of it):** `narrative/theory-of-operation.md` (revision 15).

**Compare against:** the records it cites (`decisions/`), `decisions/README.md`, `checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md`, and the History rows of records changed since 2026.10.09 (find them with `grep -l "2026.11" decisions/*.md`).

The narrative is cut with a checkpoint and the tree has moved since. For each section: is each statement of status, count, "not yet" and "Proposed" still true of the tree, and does each citation of a record say what the record says? Also note what the tree now holds that the narrative has no word for.

**One pass.** Read every clause once. Compare in depth the rows whose `since_G9` column says `new` or `changed`, and any clause that another record in your scope cites. Mark the rest `read only`.


## Reader K2

**Primary (read all of it):** `narrative/glossary.md`, `narrative/architecture-description.md`, `README.md`, `REVIEWERS_GUIDE_README.md`, `ADOPTERS_GUIDE_README.md`, `decisions/README.md`, `checkpoints/README.md`, `manifests/README.md`, `narrative/README.md`, `process/README.md`, `SECURITY.md`, `NOTICE`, the READMEs of `spec/`, `floor/`, `mechanism/`, `slm/` and the two `skills/`, `diagrams/topak/src/AUTHORING.md`, `tools/LEAN-PIN`, `tools/TLAPS-PIN`, `manifests/index.tsv`.

**Compare against:** the tree. These are the living and index documents. For each: every status, count, date, file name, tag, "newest" and "current" it states, against the files (`ls`, `grep`, the records' Status lines and History rows, `checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md`). Check the indexes for completeness against the directories they index.

**One pass.** Read every clause once. Compare in depth the rows whose `since_G9` column says `new` or `changed`, and any clause that another record in your scope cites. Mark the rest `read only`.
