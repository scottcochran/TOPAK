# A complete reference mechanism: the components, what stands for each today, and an order to build them

**2026.11.07** · derived · a plan, not a record · prepared by Claude at the custodian's request · read against
Genesis Checkpoint G11 (`checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md`), Theory of Operation revision 15
(`narrative/theory-of-operation.md`), the Adopter's Guide draft of 2026.10.09 (`ADOPTERS_GUIDE_README.md`) and the
reference's register (`mechanism/GAPS-AND-ASSUMPTIONS.md`), at the tree after `9749dfa`. Nothing in it is built,
and nothing is decided.

**The question.** The reference under `mechanism/` is the admit path: epoch fence → lease → lift → floor → bundle →
consensus-ordered admit → effect, with the launcher, the operator channel, the emergency seating and the workflow
engine around it (ToO §15; ADR-0033). What would a *complete* reference mechanism contain: every component the
records hand to "the mechanism", the register lists as not in scope, or ToO §15 says the reference does not show?

**The answer, in one paragraph.** Forty-seven components in six layers. Sixteen exist, as the baseline's eight crates
and what they carry; of those, four are partial in a way that matters (the floor links a stage not in force, the
transport is write-only, the launcher is real at one rung, the formal harnesses are stale). Thirty-one are missing or
stood in for by a register assumption. Three of the missing ones gate most of the rest: **a read path on the
transport** (nothing in the reference reads a round topic), **the Observer as a principal** (the reference hears its
heartbeats and seats nothing that could produce a finding), and **promotion as a pipeline** (the tally exists and
nothing feeds it, so no first lease has ever come from a quorum). A complete reference would also widen what the
reference claims to be: the register's scope line excludes confinement and the anchor ceremony by design, and rows
34 and 36 below cross that line, which is the custodian's to move.

**Basis.** Every row cites the record it follows and the register item, gap, finding or open-list item it would
close. Status words are the corpus's own. *Built* means code exists and a test exercises it; *partial* means the
code exists and the register names what it does not do; *missing* means no code, and the register names a stand-in
or says *none*. Records marked Proposed are ADR-0035, ADR-0036, ADR-0051, ADR-0054, ADR-0055, ADR-0056, ADR-0057 and
ADR-0058; ADR-0050 and ADR-0052 are Accepted (genesis) and provisional. A component that rests on a Proposed record
is evidence for text not in force, as the workflow engine is today (G11 §7, item 102).

---

## 1. Components by layer

The layers are the Theory of Operation's: the membrane (§2), the record (§4), detection (§5), authority (§7),
confinement and identity (§2.6, §2.7, §7.10), and operation and assurance (§15, §7.11). A row's number is used in
§2 and §3 below.

### 1.1 Membrane and admit path

The part that exists. Every row here is the baseline, and the *Closes* column names what the baseline itself still
owes.

| # | Component | Status at `9749dfa` | Record | Closes |
|---|---|---|---|---|
| 1 | **Front door**: the alphabet as MCP tools, one per variant, and nothing else | Built: `mechanism/crates/topak-mcp` | ADR-0033 §2; ADR-0022 §2; ADR-0040 §1 | |
| 2 | **Syntactic lift** and schema S enforced on every request | Built: `topak-core` `lift.rs` | ADR-0018; ADR-0030 | |
| 3 | **Lease manager**: grant, renewal that only narrows, targeted revocation, the epoch fence, local-then-ordered expiry | Built: `topak-core` `lease.rs`, `clock.rs`, `state.rs`; the expiry race of finding 19 fixed (ADR-0033 A13) | ADR-0031; ADR-0032 | |
| 4 | **Policy floor evaluator**: Cedar, linked, the floor text included by path and refused unless its bytes match the gated digests | Built: `mechanism/crates/topak-floor`. Links the proposed floor's `workflow` stage, which is not in force | ADR-0030; ADR-0033 A2, A16 | G11 §7 item 102 |
| 5 | **Bundle tier**: OPA sidecar, in-process WASM fallback bound to the lease's revision, signature verified at load, allowlist well-formedness W1 to W10 | Built: `mechanism/crates/topak-bundle` | ADR-0030; ADR-0044; ADR-0049 §6 | |
| 6 | **Composition**: `admit ⟺ floor_permit ∧ ¬bundle_deny` over one frozen input, re-checked at apply | Built: `topak-core` `admit.rs`; transcribed and proved in `mechanism/lean/Topak/Admit.lean` | ADR-0030 §1; ADR-0033 §4 | |
| 7 | **Consensus**: sans-IO crash-fault Multi-Paxos with a `Voting` ghost, the driver and the WAL | Built: `mechanism/crates/topak-paxos`, `topak-node` `driver.rs`, `wal.rs`. No proposer-retry model; no snapshots | ADR-0033 §3 | finding 9; G14 |
| 8 | **Replicated state and `apply`**: one arm per entry kind, every check rerun at the entry's position | Built: `topak-core` `state.rs`. The Lean models of `apply` are stale since the workflow build | ADR-0037 to ADR-0043; ADR-0053 | G11 §7 item 103 |
| 9 | **Effect executors**: Build tool host over MCP, Run tool host as Wasm modules with one network capability, emission | Built: `topak-mcp` `toolhost.rs`, `topak-contain` `wasmtool.rs`, `topak-node` `mechanism.rs`. A Build tool is pinned and unsandboxed; a native Run tool is checked by nobody | ADR-0042 §3, §4; ADR-0034 A2 | G4; G19 |
| 10 | **Transport**: one single-partition topic per principal per round, the seal marker, the `after` companion, denials written unordered | Built: `mechanism/crates/topak-transport`. **Write-only**: `emit` and `seal`, no consumer | ADR-0003 A1, A2; ADR-0005; ADR-0020 | finding 23 |
| 11 | **Labels, handles, the clear set, the tool list and the opening record** | Built: `topak-core` `labels.rs`; the labels of a call are one replica's computation; only a scalar passes by handle; a failed call's error text reaches the principal unlabelled | ADR-0047; ADR-0048; ADR-0049 | ToO §15 "that a label is true" |
| 12 | **Operator channel**: six signed control actions decided by C1 to C9, re-checked at apply; the unsigned socket kept as the BOOTSTRAP path | Built, provisional: `topak-core` `control.rs`, `topak-node` `ops.rs` | ADR-0050 | D-0050-1 |
| 13 | **Emergency seating**: activation by the break-glass roster's quorum over one person, one round and one task; the person's signed actions; no successor | Built in-process; a person's signed action has no socket path | ADR-0052 | |
| 14 | **Launcher**: launch → appraise → grant → bridge; a process and a container backend at rung 1; rung 3 SIMULATED behind feature `sim`; rung 2 a seam | Partial: `mechanism/crates/topak-contain`, `mechanism/crates/topak-node/src/mechanism/launch.rs` | ADR-0036 §6; ADR-0034 | G1 |
| 15 | **Workflow and mesh engine**: load from a promoted artifact, the grant of every slot, `Route` checked twice, attributes, coverage at the edge, activations, the budget | Built against Proposed records with the nine stand-ins of I49 (a) to (i) | ADR-0054; ADR-0055 | I49 |
| 16 | **Corpus pins and the drift check; the trace recorder and the `Mechanism.tla` replay** | Built: `mechanism/corpus-pins.sha256`, `topak-core` `trace.rs`, `spec/mechanism-trace-run.sh`. Replay not rerun since the workflow build | ADR-0033 A5, A14; ADR-0045 T-0045-28 | G11 §7 item 56 |

### 1.2 The record

The system of record. Every row is missing; the reference's `archive.jsonl` is a per-replica projection with no
horizon and no read path (G9; Adopter's Guide boundary 5.13).

| # | Component | Status | Record | Closes |
|---|---|---|---|---|
| 17 | **Transport read path**: a consumer for round topics and their `after` companions, under `W(p)` | **Missing.** Prerequisite for 18, 20, 22, 23, 24 and for a clear workflow input to reach a node from any replica | ADR-0005; ADR-0038 §1 | finding 23; G11 §7 item 108 |
| 18 | **Archive**: hash-and-pointer control-plane records, the declared horizon per forensic class, an audit-authority read path, rebuilt from the log | Missing; `archive.jsonl` stands in | ADR-0004; ADR-0020; ADR-0028 §3 | G9; T-0045-7 |
| 19 | **Plaintext store**: payloads under a separately governed authority, built for deletion, reached by pointer | Missing; payloads live on the deciding replica and in Kafka | ADR-0004 | G9 |
| 20 | **Write-time masking** by wrapper Rego, per topic | Missing | ADR-0003 | |
| 21 | **Erasure execution**: the X2 envelope as an admit, deletion of sealed topics and store entries, F1 to F6 refused on the erasure path, F6 written | Missing; no erasure roster is issued at genesis, so X2 admits nothing | ADR-0006; ADR-0013; ADR-0028 | G11 |
| 22 | **Replay reader**: reconstructs the boundary events of a round, denials included, from the log and the topics | Missing | ADR-0020 | |

### 1.3 Detection

Every row is missing beyond the heartbeat plumbing. The reference seats an `observer`, hears its heartbeats, moves
its watermark and stalls its Thinker on its absence; the Observer that would produce a finding is an e2e fixture
(ToO §15).

| # | Component | Status | Record | Closes |
|---|---|---|---|---|
| 23 | **Cell Observer as a principal**: a Reader stage over its Thinker's round topic, a watermark that never falls, heartbeats within `T_obs`, deny-only findings as `Report` | Partial: heartbeats, marks and `live(o)` built; no Reader, no finding producer | ADR-0038; ADR-0039; ADR-0043 §4, §5 | G12 |
| 24 | **Listener stage**: delivers each item of ingress clear or by handle under the bundle's table, with its label, and the tool list at the round's opening | Partial, inside `topak-node` `mechanism.rs`; the guest cannot resolve a handle to a non-scalar | ADR-0043 §1; ADR-0047 §4; ADR-0048 | I49 (e) |
| 25 | **Correlator**: five named folds over facts a second reader can recompute, a judgment tier beside them, a store that never outlives its sources | Missing | ADR-0051 (Proposed) | G12; G11 §7 item 97 |
| 26 | **`W(p)` as an enforced ACL** on topic reads: a cell's Observer and the domain's correlators, nobody else | Declared, not enforced | ADR-0038 §1 | ToO §15 "`W(p)` as an ACL" |
| 27 | **The finding record**: a settled form, and the path from a finding into a block, a quarantine trigger or an eviction | A reference-chosen shape, read only by the workflow engine | ADR-0007; ADR-0038 §5 | I49 (a), PROVISIONAL (finding-record) |

### 1.4 Authority and promotion

| # | Component | Status | Record | Closes |
|---|---|---|---|---|
| 28 | **Gate runner**: totality, non-vacuity and discrimination run by a named principal, with evidence attested and bound into the vote's triple; the floor-fitness gate beside them | Missing; an operator records an `(artifact, evidence)` pair | ADR-0007; ADR-0030 §6; ADR-0024 §3 | G8; G16; Adopter's Guide 4.12 |
| 29 | **Promotion pipeline**: votes bound to (artifact, gate evidence, rules epoch), recusal, coverage to the seal, the bundle signed as a step of promotion under a key with declared custody | Partial: the tally is built; signing is `scripts/build-bundle.sh` under a dev key | ADR-0024; ADR-0044 §4 | G10 item 67 |
| 30 | **The independent veto seat**: ADR-0035's independence table read at the tally, so a correlated veto seat does not complete a promotion | Missing; the tally checks coverage (A2.3) and not independence (A2.2) | ADR-0024 A2.2; ADR-0035 (Proposed) | G18 |
| 31 | **Seatings as promoted artifacts**, and the first lease granted by the mechanism when the tally completes | Missing; every seating is made by the unsigned path | ADR-0024 A3; ADR-0050 §2 | ToO §7.10 "a first lease from a quorum" |
| 32 | **Lineage projector** from the Build log, and the criterion E1 to E5 read from `Rules.criterion` | A rehearsal under `slm/`; `Rules.criterion` unset in every shipped rules file | ADR-0035 (Proposed) | G2; I39 |
| 33 | **Persona attestation**: a digest that covers prompt, decode and weights, checked at grant and at every renewal within `T_persona` | Missing; `persona` is an operator-supplied digest for a granted principal | ADR-0016 §6; ADR-0031 A2 | G13 |
| 34 | **Anchor tooling**: the genesis ceremony, issuance signing under `Authentic`, the rules-epoch chain, the custody declaration | Missing; `scripts/dev-init.sh` writes dev rules with secrets in the clear. **Outside the register's scope line** | ADR-0025 to ADR-0027; ADR-0029 §5 | G6; PROVISIONAL (custody), (Authentic) |
| 35 | **Re-genesis migration**: a new chain at epoch 0, no topic name reused, inherited forensic read access to the predecessor's F1 to F6 | Chain id in topic names only | ADR-0003 A1; ADR-0028 §4 | G17 |

### 1.5 Confinement and identity

| # | Component | Status | Record | Closes |
|---|---|---|---|---|
| 36 | **A real rung-3 verifier client**, and a rung-2 backend behind the seam | SIMULATED under test keys. **Outside the register's scope line** | ADR-0034 §2, §3 | G1; Adopter's Guide boundary 5.8 |
| 37 | **Build tool hermeticity enforced**: a sandbox for the Build tool host, or every tool hosted as a Wasm module, so that no socket is reachable rather than none declared | Pinning and a cleared environment | ADR-0022 §3, §6 | G4; assumption of use A2 |
| 38 | **Native Run tools held to their channel**, or refused: a tool not hosted as Wasm either runs under an enforced channel or does not run | Nothing sees an undeclared channel | ADR-0034 A2; ADR-0042 §6 | G19 |
| 39 | **Identity provider client** for an operator's sign-on assertion at every lease boundary and on a deny without a lease | Test keys in `provider_keys` | ADR-0050 §3, §4 | Adopter's Guide boundary 5.5 |
| 40 | **Replica authentication** (mTLS between replicas) and principal authentication beyond a bearer token | None between replicas; a 0600 socket; a bearer token | ADR-0033 §3 | G5; assumption of use A9; PROVISIONAL (replica authentication), (session binding) |
| 41 | **A signed-action socket** for an emergency seat's person, and **ADR-0036's occupant** that runs a workflow's cells from their launched sessions | In-process and scripted | ADR-0052 §3; ADR-0036 | I49 (g), PROVISIONAL (workflow-occupant) |
| 42 | **A trusted time source**, and the clock-drift bound as a declared degeneracy parameter | A local monotonic clock plus a margin that errs early | ADR-0032 §2, §6 | assumption of use A6; Adopter's Guide value 6.16 |

### 1.6 Operation and assurance

| # | Component | Status | Record | Closes |
|---|---|---|---|---|
| 43 | **Log compaction, snapshots, state transfer**; the dedupe set and the WAL bounded | None: the log, `chosen` map, dedupe set and WAL grow without bound | ADR-0033 | G14; PROVISIONAL (dedupe growth) |
| 44 | **`Mechanism.tla` and the Lean models extended to workflows**, and the replay rerun on the tree | Stale since 2026.10.08, by the custodian's decision | ADR-0053; ADR-0033 A16 | G11 §7 items 56, 103 |
| 45 | **The refinement chain's stages 2 and 3**: a Lean model of `apply` with differential testing, then a reproducible build whose digest a manifest can cite | Open | ADR-0045 T-0045-28; ADR-0053 §5 | G11 §7 item 56 |
| 46 | **The reference's own deployment declaration** and a theorem inventory computed from the binding | `spec/inventory.py` and `spec/theorem-premise-binding.json` exist; no declaration is written | ADR-0023 §6; ADR-0058 (Proposed) | G11 §8 "no deployment declaration has been written" |
| 47 | **A measurement rig** for `T_obs`, `K` and `L`, reading the `slm/` rig's Observer against planted defects | Placeholders in `floor/genesis-values.json`; `L` unmeasured | ADR-0039 §1; ADR-0032 §4 | Adopter's Guide values 6.1, 6.2, 6.5 |

---

## 2. Cross-cutting prerequisites

Three rows gate most of the rest, and they would come first in any order.

- **The transport read path (17).** The Observer's Reader (23), the Listener's delivery of another replica's
  reports (24), the correlator (25), the replay reader (22) and a clear workflow input (I49 (f)) all read a round
  topic, and today the transport has `emit` and `seal` and nothing else. Finding 23 is the register's statement of
  it, and G11 §7 item 108 carries it for the corpus.
- **The Observer as a principal (23).** Coupling (ADR-0039), coverage at the tally (ADR-0024 A2.3), the veto roster
  (ADR-0038 §6), the finding record (27) and the routing rule's "no finding in the causal history" (ADR-0054 §5)
  all assume an Observer that reads and reports, and the reference has only its heartbeats. Until it exists, G12
  stands and every detection claim is a fixture's.
- **Promotion as a pipeline (28 to 31).** Bundles, profiles, seatings, workflows and the mechanism release itself
  are promoted, and the reference has the tally with nothing feeding it: gate evidence is asserted (G8), the bundle
  is signed by a script (item 67), independence is unchecked (G18), and the operator record's centre, a first lease
  from a quorum, is unshown (ToO §7.10). Building the pipeline is what would let the reference promote itself,
  which ADR-0033 §1 notes it has never been.

---

## 3. An order to build them

Each step leaves a tree that the register can describe and an ADR-0033 addendum can cite, as every build since
2026.09.24 has (ADR-0033 A1 to A17).

1. **Detection has a producer and a consumer**: the read path (17), the Observer's Reader and findings (23), the
   Listener completed (24), the finding record (27), `W(p)` enforced (26). The Observer that results is still a
   scripted seat, as the demo guest is; what changes is that a finding has a source the records name and a path the
   records name.
2. **The record exists before erasure can be exercised**: the archive (18), the plaintext store (19), masking (20)
   and the replay reader (22). Erasure (21) waits for step 4.
3. **A first lease comes from a quorum**: the gate runner (28), the pipeline with signing (29), the independence
   table (30), seatings (31) and the lineage projector that feeds the table (32). Row 30 and row 32 rest on
   ADR-0035, which is Proposed, so the step builds to text not in force unless ADR-0035 is ratified first.
4. **Erasure (21)**, once the anchor tooling (34) can issue a roster, and re-genesis (35) beside it. Row 34 is outside
   the register's scope line; see §4.
5. **Confinement and identity**, rows 36 to 42, the verifier last, as the Adopter's Guide §5 advises: the front door
   and the tool host are what every other row is checked against, and the verifier is the one row that needs
   hardware and a vendor.
6. **Alongside, since none blocks the others**: compaction (43), the stale models and the replay (44), the refinement
   chain (45), the declaration (46) and the measurement rig (47). Row 44 is the cheapest of the forty-seven and
   the one G11 lists twice.

---

## 4. What this plan does not settle

- **Scope.** The register's scope line (§1 of `mechanism/GAPS-AND-ASSUMPTIONS.md`) excludes the Observer and
  correlator, the archive and plaintext store, write-time masking, the anchor ceremony and bootstrap, confinement
  and erasure execution, by design. Rows 17 to 27, 34 and 36 cross it. A complete reference is a different claim
  from an admit-path reference, and ADR-0033 §1's sentence that the reference is evidence and not the verified
  object gets harder to keep in view as the reference grows. Whether to widen the scope line, and how to keep the
  sentence true, is the custodian's decision.
- **Proposed records.** Rows 25, 30, 32 and the workflow stand-ins rest on ADR-0051, ADR-0035, ADR-0054 and
  ADR-0055. Building them repeats what the workflow build did on 2026.10.08: evidence for text not in force, on a
  floor stage not in force. G11 §7 item 102 is the open item for that.
- **Values.** Rows 42 and 47 produce numbers, and every number the corpus ships is a placeholder (Adopter's Guide
  §6). A measurement at the reference is a measurement of the reference's Observer and clock, not of a deployment's.
- **Nothing here is a design.** Each row says what the records ask for and what stands in for it. The design of any
  one row is a document of the kind `derived/topak-contain-wrapper-design-2026.10.02.md` was for row 14.

---

## 5. Suggested entries, none made

1. An ADR-0033 amendment, if the custodian widens the reference's scope, restating §6's scope and the sentence that
   the reference is evidence and not the verified object, against the wider claim.
2. A register revision adding a row per component built, under the existing convention of one `PROVISIONAL (<tag>)`
   per assumption.
3. A G12 revision in the register once row 23 exists, since G12's text is "none".
4. A G11 §7 item for row 17, beside item 108, if the read path is treated as owed by the reference rather than as
   finding 23's observation about the corpus.
