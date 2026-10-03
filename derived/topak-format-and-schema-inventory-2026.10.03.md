# TOPAK — Inventory of Message Formats, Schemas and Configuration Settings

**2026.10.03** · derived · inventories every message format, schema, on-disk format and configuration setting in the
corpus at Genesis Checkpoint G9 (2026.10.02), Theory of Operation revision 13 and the tree at `c51d0ec` · the
record layer is read from `decisions/`, the policy layer from `floor/` and `policies/`, the reference from
`mechanism/`, the model layer from `spec/`, the rehearsal from `slm/`, and the tooling from `tools/`, `manifests/`
and `checkpoints/README.md` · prepared by Claude at the custodian's request

**What this is.** One document that says, for every structured thing the corpus passes between its parts, what the
thing is, which record defines it, where the reference implements it, what fields it has, and what value every
setting takes today. The corpus has five layers that each hold formats: the records define schemas in prose; schema
S and the floor type the admit path; the Rust reference serializes everything; the TLA+ operational model projects
the reference's state; and the tooling measures all of it by digest. A reader has had to walk all five to answer
"what fields does a lease have, and who checks them?" This is that walk, done once. **It is a derived document and
not a record**: nothing here is ratified, and where the layers disagree §11 says so and decides nothing.

**How to read a status.** *Record* means a ratified record defines the format. *Proposed* and *Pending* mean a
record or amendment defines it and is not in force. *Reference* means the format exists only in `mechanism/`, as a
PROVISIONAL choice or an implementation detail, and is cited by no record. *Placeholder* means the value is a
stand-in, chosen so a check could run, and the record that owns it says so. Line numbers are as of the tree named
above and will drift; file names are the stable citation.

---

## 0. Conventions every format rests on

| Convention | Definition | Where |
|---|---|---|
| **Digest** | Lowercase hex SHA-256, serialized as a bare string; `short()` is the first sixteen hex characters | `mechanism/crates/topak-core/src/types.rs` |
| **Canonical JSON** | Object keys sorted recursively, no whitespace; every `of_json` digest and every signature is over this form. Sorted by hand because `cedar-policy-core` turns on `serde_json`'s `preserve_order` (register finding 15) | `types.rs`; `mechanism/GAPS-AND-ASSUMPTIONS.md` §4 |
| **Signature (`Signed`)** | `{key: hex Ed25519 public key, sig: hex signature}` over `"topak/<purpose>/v1\n" ‖ canonical_json(body)` | `mechanism/crates/topak-core/src/authentic.rs`; PROVISIONAL (Authentic), I7 |
| **Signature purposes** | `issuance` (the `Rules`), `break-glass` (`{seat, epoch}`), `bundle` (`{revision}`), `appraisal` (the statement), `agent-op` (`{fence, epoch, ctr, op}`), `sim-report`, `key` (null; derives a public key) | `rules.rs`, `state.rs`, `topak-bundle/src/lib.rs`, `confine.rs`, `topak-contain/src/sim.rs` |
| **Tool id** | `<name>@<digest>`; both the allowlist key and the Cedar `Tool` entity id | `action.rs` |
| **Tree digest** | SHA-256 over sorted `path \0 bytes \0`; used for workspaces, bundle revisions and the rehearsal's code digest | `confine.rs`; `mechanism/scripts/build-bundle.sh`; `slm/common.py` |
| **Serde tagging** | `Action`, `Admitted`, `Evidence` tagged `kind`; `Entry` tagged `entry`; `AgentOp`, `OperatorOp` tagged `op` (snake_case); `GuestMsg`, `HostMsg` tagged `msg`; `BackendConfig`, `VerifierConfig` tagged `kind` (kebab-case); `RevocationTarget` adjacently tagged `{kind, id}`; everything else externally tagged, unit variants as bare strings | the respective `src` files |
| **Manifest line** | `<sha256><two spaces><root-relative path>`, as `shasum -a 256` prints it | `manifests/README.md` |
| **Dated results file** | Named `<Subject>-results-YYYY.MM.DD[b].txt`, never edited; a later run the same day takes a suffix | `spec/README.md`; G9 §5 |

---

## 1. Record-defined schemas

The records are the canonical layer. Each row gives the record's field list, then where the reference carries it.

### 1.1 The lease and its events (ADR-0031)

| Field | Record content | Reference (`topak-core/src/lease.rs`) |
|---|---|---|
| `principal` | principal identity | `String` |
| `seat` | the seat held this round | `SeatId` |
| `persona` | Persona id, attested at grant and renewal | `Digest` |
| `epoch` | epoch the lease is valid at; any increment fences it | `u64` |
| `fence` | Paxos log index at grant; the lease's identity | `LogIndex` |
| `rulesEpoch` | rules epoch in force at grant | `u64` |
| `bundle` | bundle revision the principal is admitted against | `Digest` |
| `confinement` | `[digest, rung]` | `Confinement{digest, rung: u8}`; `MAX_RUNG = 3` |
| `alphabet` | variants this seat may express | `BTreeSet<ActionKind>` |
| `round` | round granted for, never reused per seat | `u64` |
| `role` | `author` or `voter` | `RoundRole` |
| `ttl` | duration on the local monotonic clock, at most `T_persona` (A2) | `ttl_ms: u64` |

- **Closed schema**: twelve fields; adding one is a mechanism release. **Renewal** keeps everything but may shrink the
  alphabet and shorten the TTL; the rung is fixed (A1) and the bundle is fixed (I4). **Status: Record** (C1; A1 C2).
- **Kept beside the lease, not in it** (`state.rs` `LeaseRecord`): `ended`, `actions`, `seq`, `attestation`
  (I39; ADR-0034 A3 pending writes this choice down), `session_ctr` (I41). **Status: Reference.**
- **End reasons** (`state.rs` `EndReason`, snake_case): `submitted`, `abstained`, `voted`, `expired`, `fenced`,
  `revoked`, `rules_changed`, `operator`, `renewed`. ADR-0042 §5's seal table says which of these seals a Run topic.
- **Revocation target** (ADR-0031 §5): a principal, a Persona digest or a confinement digest; `{kind, id}` on the wire.
- **`T_persona`**: policy-floor value, 3,600,000 ms, placeholder; relaxing it is an issuance plus a promotion. Enforced
  at grant and renewal (`state.rs`, I35).

### 1.2 The two alphabets (ADR-0022, ADR-0040)

| Domain | Variant | Parameters | Envelope | Class (ADR-0015) |
|---|---|---|---|---|
| Build | `Read(ref)` | `object: Digest` | inside the pinned corpus root | ingress |
| Build | `Draft(target, content)` | `target: String`, `content: String` | inside the round workspace | effect (workspace write) |
| Build | `Invoke(tool, inputs)` | `tool`, `digest`, `inputs: Map` | allowlisted by name and digest; inputs workspace-resident; hermeticity obligation | effect: tool invocation |
| Build | `Emit(record)` | `record: Value` | own topic, this epoch and round, unsealed | effect: emission |
| Build | `Submit(digest \| ⊥)` | `artifact: Digest`, or `submit_workspace`, or `abstain` | terminal for the authoring round | — |
| Build | `Vote(verdict, digest, evidence, rulesEpoch)` | `verdict`, `artifact`, `evidence`, `rules_epoch` | seated at `rulesEpoch`; grant only from a grant seat; never the author | — |
| Run | `Consult(ref)` | `object: Digest` | inside the pinned Run root | ingress, no effect |
| Run | `Actuate(tool, inputs)` | `tool`, `digest`, `inputs` | allowlisted; the entry declares its channel | effect: tool invocation |
| Run | `Report(record)` | `record: Value` | own topic, unsealed | effect: emission |

- **Mechanism parameters** (ADR-0022 §3; ADR-0040 §3): corpus root, Run root, tool allowlist with digests, round
  bound `R` per domain. In the reference these are `Params` (§5.3). **No variant name is shared** (ADR-0022 A2).
  `RunInvoke` and `RunEmit` are retired and fail schema validation. **Status: Record** (ADR-0040 C3, C4).
- **The allowlist entry's schema is an open obligation** (ADR-0040 finding 4; G9 item 59). The reference's stand-in is
  `channel: {kind, target}` in bundle data, shape-checked only (I33, G19), and a second declaration in the node's
  `wasm_tools` config (I44). The two are not checked to agree (G9 item 84).
- **Per-kind alphabet bound** (ADR-0037 §4; ADR-0043 §2): `thinker` holds every variant; `observer` holds `Read`,
  `Emit`, `Vote(deny)` on the veto roster, and in Run `Consult`, `Report`; `grant` holds `Read`, `Emit`, `Vote`.
  Reference: `SeatKind::allows()`; floor: `B10`, `B6`.

### 1.3 The `Actuate` record (ADR-0042 §3)

Written by the mechanism, one per admitted `Actuate`, when the call returns; an unreturned call at the seal is
written as `unknown` before the seal marker.

| Field | Side | Reference (`mechanism.rs` `InFlight::record`, I29) |
|---|---|---|
| `seat`, `fence`, `admit`, `seq` | control plane | `EmitRecord` envelope: `seat`, `fence`, `admit`, `seq` |
| `tool` | control plane | `actuate.tool` (`name@digest`) |
| `breakGlass` | control plane | `actuate.breakGlass` |
| `inputs` digest, `outcome` (`returned` \| `failed` \| `unknown`), `result` digest | control plane | `actuate.inputs`, `actuate.outcome`, `actuate.result`; plus `actuate.channel?: {kind, target}` (Reference) |
| the inputs and the result | cognitive payload | `body: {inputs, result}` |

The record digest is over the `actuate` envelope only. **Status: Record** (C4); the `channel` field is Reference.

### 1.4 Seats, cells and the heartbeat (ADR-0037, ADR-0038, ADR-0039)

| Schema | Record fields | Reference |
|---|---|---|
| **Seat declaration** | a key and a domain (ADR-0037 §1); `kind` ∈ thinker, observer, grant (§2); `cell`, empty for a correlator (ADR-0038 §8); `rung` per seat (ADR-0023 A1, **pending**) | `rules.rs` `SeatDecl{domain, kind, cell?, key, rung}`; `rung` defaults to 0 and is omitted when 0 (I8, I37) |
| **Cell** | the principals seated around one Thinker for a round; not a principal, holds no lease | declared, not enforced (`W(p)` as an ACL is G9 item 46) |
| **Heartbeat** | a fixed-schema fact with two fields: the watched round topic and the watermark; sent as `Emit` in Build, `Report` in Run | `observer.rs` `Heartbeat`: a record that is exactly `{"heartbeat": {"topic", "watermark"}}`; admitted as `Admitted::Heartbeat{via, topic, watermark}` (I27) |
| **`live(o)`** | a live lease; fewer than `T_obs` since `heard(o)` with the asymmetric margin; `seq − mark < K` strict | `mechanism.rs` `fresh` at decide; `state.rs` `observer_covers` at decide and apply; lifted as `observerLive` |
| **Mechanism state** | `heard(o)` per replica on its own clock; `mark(o, round)` replicated, only rising | `heard` (per replica, non-replicated); `State.marks` |

**Status: Record** (ADR-0037 C3, C4; ADR-0038 C3, C4; ADR-0039 C4).

### 1.5 Promotion and the vote (ADR-0024)

| Item | Record | Reference |
|---|---|---|
| Vote triple | (artifact digest, gate-evidence digest, rules epoch); a rules-epoch change voids in-flight votes | `promotion.rs` `VoteRecord{verdict, evidence, rules_epoch}` |
| Candidate | keyed by artifact digest | `Candidate{artifact, author, votes, promoted_at}` in `State.candidates` |
| Issued parameters | `quorum` ∈ `"all"` or threshold *k*; `minGrant`; `"any"` withdrawn | `Quorum` serializes as `"all"` or an integer; `"any"` rejected with a message |
| Tally constants | a timeout never grants; the author is recused; an independent veto seat leased (A2.2, unbuilt, G18); coverage to the seal (A2.3) | `Tally::{Promoted, Pending, Stalled, Denied}`; promotion happens inside `apply` when a `Vote` or `Heartbeat` admit completes the tally |
| Gate evidence | enables voting; `GatesPassed{artifact, evidence}` is an operator assertion | `Entry::GatesPassed`; PROVISIONAL (gate runner), I18, G8 |

There is **no promotion log entry and no `promote` operator op**; the admit that completes the tally is the event.

### 1.6 The Persona (ADR-0016 to ADR-0020)

| Field (ADR-0016 §1) | Note |
|---|---|
| provenance / lineage | ADR-0035 makes it the digest of the lineage record |
| Persona id | signed over the whole record |
| sequence number | monotone per Persona line |
| system prompt | byte-exact, hashed |
| decoding parameters | temperature, top-k, top-p, penalties, stop sequences |
| decoding stack version; determinism class; context window and truncation policy | — |
| decoder | identifier and hash of the emission decoder (ADR-0018: the model-specific half of the lift) |
| decode observability | `none` \| `topk_logprobs` (ADR-0019; the second is rung-gated) |
| seat binding | `thinker` \| `observer` (ADR-0037) |

- **Provenance axis** (ADR-0017; `confine.rs` `Provenance`): `in_house_pretrain`, `in_house_finetune`,
  `attested_external`, `asserted_external`. Carried in `Rules.personas` as a map from digest to provenance.
- **The reference has no Persona record.** Its Persona is a `model.json` bundle, `{family, params, weights,
  weights_sha256}`, whose digest is the SHA-256 of the file's bytes (`topak-contain`; `slm/`). **Status: Reference.**
- **Replayable record** (ADR-0020): actions attempted including denied, effects emitted, lease and epoch transitions,
  the Persona binding in force. The denial record is §4.4.

### 1.7 Confinement (ADR-0034; ADR-0036 Proposed; ADR-0035 Proposed)

**The profile file** (ADR-0036 §1; `confine.rs` `Profile`), JSON, identity `Digest::of(bytes)`, keys starting `_` ignored:

| Part | Content | Reference type |
|---|---|---|
| `image` | guest image by content digest | `Option<Digest>` |
| `launch` | runtime constraints: network, root fs, capabilities, user, IPC, limits, mounts and modes | opaque `Value`; the Docker backend types it as `DockerLaunch{kind, network: "none", read_only, cap_drop, security_opt, ipc?, pids_limit?, user?, tmpfs, runtime?, mounts:[{dst, mode: "ro"}]}` |
| `channel` | the one channel and its protocol | opaque `Value` |
| `persona` | digest of `model.json` | `PersonaRef{model_json_sha256}` |
| `reference` (P7) | expected launch measurement; minimum platform TCB | `ReferenceValues{launch_measurement?, min_tcb?}` |
| `clauses` | P1–P7, each `pass` \| `fail` \| `vacuous` with a reason; a missing clause is malformed | `Map<Clause, {verdict, why}>` |
| `subtractions` | for each `fail`, what must be removed | `Map<Clause, String>` |
| `domain` | `build` or `run` (A2, pending) | default `build` |

- **Clauses** (ADR-0034 §1): P1 one channel, no network device; P2 measured read-only root, workspace, corpus root and
  nothing else; P3 no shell, package manager or interpreter; P4 tools as Wasm components per call with a workspace
  capability only, or for Run (A2, pending) channel fidelity; P5 inference inside, weights in the measurement; P6 one
  principal per guest and one guest per round; P7 reference values. Build's profile is determined by the alphabet.
- **Reference values per rung** (`check_for_rung`): rung ≥1 needs `image` and `persona`; rung ≥2 adds the
  launch measurement; rung 3 adds `min_tcb`.
- **Promotion artifact**: a one-file workspace `profile.json`, keyed by the file's digest (ADR-0036 R4; PROVISIONAL
  (profile-artifact), I38).
- **Rungs** (ADR-0034 §2): 0 none, `Mediated`; 1 the launcher's assertion; 2 a measured-boot quote; 3 a
  confidential-VM report appraised by an independent verifier whose key is in the issued rules.
- **Nonce** = hash of (epoch, committed log index, principal, round): `NonceInput{epoch, index, principal, round}`,
  digest by canonical JSON. **Report data** = `Digest::of_json({nonce, sessionKey})`.
- **Verdicts**: `attested`, `unattestable`, `contested`. Contested revokes the principal (F2); A3 (pending) limits
  Contested to a verdict signed under an issued verifier key at rung ≥ 2.
- **Appraisal statement** (`AppraisalStatement`): `{nonce, profile, persona, rung, verdict, evidence, session_key?,
  measurement?, tcb?, platform}`; `platform` ∈ `launcher`, `sim-snp`. Signed under `appraisal` at rung 3.
  **Appraisal** = `{statement, instance, signature?}`, carried in `Grant`, `Renew` and `Contested` entries.
  **Attestation** (beside the lease) = `{verdict, n_epoch, nonce_index, instance, session_key, evidence,
  verified_by?, platform}`.
- **Session proof** (rungs 2 and 3): `{ctr, op: Digest of the AgentOp JSON, sig}` under `agent-op` over
  `{fence, epoch, ctr, op}`; the action binding is checked at decide and the counter at apply (I41).
- **Evidence** (`Evidence`, tagged `kind`): `launcher_assertion{image?, persona}`; `sim_snp{report, signature}`
  where `SimReport = {measurement, report_data, tcb, platform: "sim-snp"}`; `snp`, `tdx`, `tpm_quote` seams.
  Retained at `<data_dir>/evidence/<digest>.json` (I40).
- **`Contained(p)`** (ADR-0034 §4): a live lease at rung ≥ 1 on an Attested verdict at the declared rung; P3–P5 met;
  an in-house Persona; the lineage criterion in force. Reference: `Containment{contained, because, simulated}`,
  returned by `grant`, `launch` and `status`; `Rules.criterion = {record, independence_table, floor_values}` is the
  reference's reading of "in force" (A3, pending; I39). **No shipped rules set it.**
- **Status**: ADR-0034 Record (C2, C4); A2 and A3 Pending; ADR-0036 Proposed; ADR-0035 Proposed.

**The lineage record** (ADR-0035 §1; `slm/lineage/record.py`, schema `topak.lineage/0`):

| Field | Record | Rehearsal |
|---|---|---|
| `root`, `parents`, `weights` | projected | plus `weight_ancestry` |
| `ingress` | what the round could read, over-approximated | sorted union with parents'; `ingress_bytes` |
| `consumed` (R2) | what it did read, never over-approximated | own read set plus parents'; `consumed_bytes` |
| `generatedBy`, `curatedBy` | projected or declared at admission | byte-weighted shares; `generated_share`, `generated_bytes` |
| `tokenizer`, `family`, `trainer` | projected; `family` declared | `trainer = {tool, config, seed}` |
| `rung` | lowest confinement rung over the DAG | weakest link across parents |
| strength | — | `projected` \| `declared`; drops to declared at rung 0 or with a declared parent |

E1–E5 and the distillation rule are `slm/lineage/independence.py`; the thresholds are §9.

### 1.8 Authority (ADR-0025, ADR-0026, ADR-0027, ADR-0029)

**Rules contents** (ADR-0025 §1; `rules.rs` `Rules`):

| Record item | Reference field |
|---|---|
| (a) promotion roster and parameters | `rules_epoch`, `quorum`, `min_grant`, `seats`, `grant_roster`, `veto_roster` |
| (b) break-glass and erasure rosters | `break_glass: {roster, quorum, tools, actions}` (quorum PROVISIONAL, I9); `erasure_roster` (never read, G11) |
| (c) the anchor key set | `anchor_keys` |
| (d), (e) floor relaxations and rules-floor changes | not representable as fields; the rules floor is mechanism constants |
| (f) keys the mechanism accepts a signature from (A1) | `verifier_keys`, `bundle_keys` (I34, I36) |
| — | `personas: Map<Digest, Provenance>`, `criterion?` (Reference; omitted when empty so older rules keep their bytes) |

- **Issuance** = `{rules, signatures: [Signed]}`; valid when the rules epoch increases by exactly one, every current
  anchor key signs under `issuance`, the rules are well formed, and the rules floor holds.
- **Rules floor** (ADR-0026 §2): R1 `quorum = "all"`; R2 `minGrant ≥ 2`; R3, R4 withdrawn; R5 no key both anchor and
  roster; R6 exception count ≤ 2 (`EXCEPTION_BOUND`); R7 no break-glass grant over `Issue`, `Vote`, promotion
  (`R7_FORBIDDEN`); R8 `0 < breakGlass.ttl ≤ T_BG` **pending**, `T_BG` has no archetype value; R9 `quorum = "all" ∨
  quorum ≥ 2`, conditional. In force: R1, R2, R5, R6, R7, R9. Live definition: `spec/RulesFloorBase.tla` (ADR-0046 E1).
- **Custody pair** (capture threshold, loss tolerance): archetype (n, 0), n ≥ 3; D-0025-1 (k, n−k); D-0025-2 (n−1, 1);
  today (1, 0).
- **Genesis rules** are resident (ADR-0027); the chain id is `Digest::of_json(genesis rules)`, and the first twelve
  hex characters name every topic (§4.4). An issuance does not change the chain.
- **ADR-0029 forms**: status classes (Accepted (genesis); Accepted (genesis) · confirmation required; Proposed);
  criteria C1–C4; the checkpoint debt ledger (count, records, bootstrap spec, and since A2.5 the reviewer engaged and
  the last review pass digest); the genesis bundle (corpus manifest, specification digest, review attestation with
  reviewers, manifest digest, scope and findings disposition, genesis rules, and the trusted-base declaration).

### 1.9 The record: topics, classes, exceptions (ADR-0003, ADR-0013, ADR-0028)

| Schema | Record | Reference |
|---|---|---|
| **Topic name** | one per principal per epoch or round; identity includes the rules-epoch chain (A1); the naming scheme left open | `lift.rs`: `topak.<chain12>.<domain>.<seat>.e<epoch>.r<round>`, one partition (I17) |
| **After companion** (A2) | denials only, after the seal; same ACL and erasure; bounded, with a marker | `<topic>.after`; `after_topic_limit` 64, then one `overflow` record (I23) |
| **Floor-exception entry** (ADR-0013 §2) | named and versioned; action envelope; roster reference; non-composition obligations | Cedar policies whose `@id` starts with `X`; `exception_count` feeds R6 |
| **Forensic classes** (ADR-0028 §1) | F1 admit decisions, F2 stop attribution, F3 promotion votes, F4 anchor issuances, F5 break-glass invocations, F6 erasure events; each with a declared horizon and audit authority | F1 is `AdmitRecord`; F2 is `EndRound` and `Revoke` attribution; F3 the `Vote` admit; F4 `Entry::Issue`; F5 `BreakGlassApprove`; F6 unbuilt. Floor: one policy `F-forensic-classes` with a set literal |
| **Hash and pointer** (ADR-0004) | control-plane record keeps a hash and a pointer; plaintext in a separately governed store | payloads are digested in `Admitted`; the store does not exist |
| **Erasure event** (ADR-0006) | consensus-ordered, modeled, recorded in the log it modifies | schema S has `Erase`; no lift path, no entry (G11) |

### 1.10 Policy (ADR-0010, ADR-0012, ADR-0030, ADR-0044, ADR-0032)

| Schema | Record | Reference |
|---|---|---|
| **The verified object** | mechanism, version pinning, epoch fencing, minimal policy floor, minimal rules floor | the `topak-floor` crate with the three floor files compiled in and pinned (§2.3) |
| **Composition** | `admit ⟺ floor_permit ∧ ¬bundle_deny` over one frozen input; a floor deny names its reason or *no permit matched*; a bundle decision counts only from the lease's revision | `admit.rs`: `FloorOutcome`, `BundleOutcome`, `DenyReason::{Mechanism, Floor, FloorNoPermit, FloorError, Bundle, NotCommitted}` |
| **Schema S** | enforced per request; the PARC map: principal = seat, action = variant, resource = ref / target / tool / topic / artifact, context = epoch, fence, rulesEpoch, round, lease fields | `floor/genesis.cedarschema` (§2.1); `lift.rs` builds it |
| **Gate verdicts and routing** (§5, A1) | totality, non-vacuity, discrimination, entry matters, routing; a `holds` counts only with a checked proof | `floor/run-gates.py` (§2.5); `holds✓`, `holds°`, `holds?`, `refuted` |
| **Gate evidence** | schema version, checks run, classification, analyzer, solver and engine versions, per-`holds` query, proof and checker digests, the evidence-tree digest | `floor/genesis-gates-evidence-<date>/` (§2.5); the vote's `evidence` digest is an operator's assertion at the reference |
| **Bundle signature** (ADR-0044) | the content revision signed under an issued key; shipped as `<revision>.sig` | `topak-bundle`: `Signed` over `{revision}`, purpose `bundle` (§3) |
| **Clock model** (ADR-0032) | subtracting intervals on a local monotonic clock with an asymmetric margin; preserving intervals need trusted time; `W + L + D < T_irrev` per effect class | `clock.rs` `subtracting_interval_elapsed(start, len, margin, now)`; `lease_margin_ms`; no `T_irrev` anywhere |

### 1.11 Deployment and the trusted base (ADR-0023, ADR-0045, ADR-0046)

| Schema | Fields |
|---|---|
| **Declaration record** (ADR-0023 §6) | kind (mechanism \| declaration degeneracy); parameter; archetype value; deployed value; premises falsified; theorems voided; type changes (6b: archetype type, deployed type, where the gate sits, what enters or leaves the trusted base; "no participant changes type" when empty); mitigation (optional); composition note (mandatory above one parameter); **6c (A1, pending)**: the declared rung per seat with the Annex A rows it rests on. A *properties lost* field is proposed and open (G9 item 40) |
| **Trusted-base row** (ADR-0045 §1) | `T-0045-n`; Component; Layer (`mechanism-boundary` \| `substrate` \| `toolchain` \| `people`); Trusted for; Rungs; Class (delegated \| trust root \| excluded; or refused); Failure can produce; Identity fixed by; Residual (never empty). Annex A: thirty-one rows. Annex B: Row \| Instance at the reference \| Class here \| Note |
| **Binding table** (`spec/theorem-premise-binding.md`) | Theorem \| Checked in \| Record \| Breaks under \| Row premises \| Parameter and gap premises \| At the reference (Annex B); forty-three rows; base premises T-0045-1, -11, -28, -29, -30, with -31 for a proved row. **`spec/theorem-premise-binding.json`** (2026.10.03) is the same table as a Boolean incidence matrix, one row per theorem and one column per premise, with `_about` and the parameter, condition and gap columns transcribed; `inventory.py --check` fails when the two disagree at any rung |
| **Deployment declaration input** (`spec/inventory.py`) | `{"rung": N, "rows": {"T-0045-16": "trust root" \| "delegated" \| "excluded", …}}`; an unnamed row is undeclared and false; evaluated against the `.md` table or the `.json` matrix. **No example declaration file exists in the repository** |
| **Proof citation** (ADR-0046 §4) | Base module (digest) \| Proof module (digest) \| Results file (digest) \| Obligations \| Theorems and hypotheses |
| **Record file** | header comment (`AUTHORED` / `RECOVERED` / `ON DISK` with date); `**Status:** <class> · <date> [· confirmation required (C…)] ⟨Bn⟩`; the field order in `process/NORMALIZATION-LOG-2026.09.15.md` §2; body Context · Decision · Options · Consequences · Findings · Open obligations · History; History columns Tag \| Kind \| Change \| Source \| State (ADR-0044 to 0046 use Entry \| Kind \| What changed \| Source \| Status); inline markers ⟨A1⟩ ⟨R2⟩ ⟨B20⟩ ⟨E1⟩ ⟨C1⟩ ⟨N1⟩; pending text as `*Pending ⟨A2⟩, not applied.*` |

---

## 2. Schema S and the policy floor (`floor/`)

All three floor files are DRAFT and not ratified. Their digests are pinned in the reference and printed in every
gate header: floor `28ec0e4552c6a915`, schema `0ec2fa215eefe136`, values `85ab6fefb66f0316`, unchanged since
2026.09.30.

### 2.1 Schema S (`floor/genesis.cedarschema`, namespace `Topak`)

**Entity types** (no attribute is optional):

| Entity | Parents | Attributes |
|---|---|---|
| `Roster` | — | — |
| `Seat` | `Roster` | `domain: String` (build \| run), `kind: String` (thinker \| observer \| grant) |
| `CorpusRoot` | — | — |
| `CorpusObject` | `CorpusRoot` | — |
| `Workspace` | — | — |
| `WorkspaceTarget` | `Workspace` | — |
| `ToolSet` | — | — |
| `Tool` | `ToolSet` | `digest: String` |
| `Topic` | — | `owner: Seat`, `epoch: Long`, `round: Long`, `sealed: Bool` |
| `Artifact` | — | `author: Seat` |
| `ArchiveRecord` | — | `class: String` (F1..F6 \| payload) |

**Context records:**

| Type | Fields |
|---|---|
| `Lease` | `alphabet: Set<String>`, `rulesEpoch: Long` |
| `BuildCtx` | `lease`, `epoch`, `round`, `roundRole` (author \| voter), `corpusRoot`, `workspace`, `toolAllowlist`, `inputsInWorkspace: Bool` |
| `VoteCtx` | `lease`, `epoch`, `rulesEpoch`, `verdict` (grant \| deny), `voteRulesEpoch`, `grantRoster`, `vetoRoster` |
| `RunCtx` | `lease`, `epoch`, `round`, `runRoot`, `toolAllowlist`, `breakGlass: {quorum: Bool, tools: ToolSet}`, `observerLive: Bool` |
| `EraseCtx` | `erasureQuorum: Bool` (FALSE at genesis) |

**Actions** (principal always `Seat`): `Read` → `CorpusObject`, `BuildCtx`; `Draft` → `WorkspaceTarget`;
`Invoke` → `Tool`; `Emit` → `Topic`; `Submit` → `Artifact`; `Vote` → `Artifact`, `VoteCtx`; `Consult` →
`CorpusObject`, `RunCtx`; `Actuate` → `Tool`, `RunCtx`; `Report` → `Topic`, `RunCtx`; `Erase` → `ArchiveRecord`,
`EraseCtx`.

**As the lift builds it** (`lift.rs`): the entities always present are `Roster::grant`, `Roster::veto`, the
requesting `Seat` with its roster parents, `CorpusRoot::pinned`, `CorpusRoot::run-pinned`, the `Workspace`
`ws-<seat>-e<epoch>-r<round>`, and `ToolSet::build-allow`, `run-allow`, `bg-tools`; the resource per action; and
the context in the shapes above. `Erase`, `EraseCtx` and `ArchiveRecord` are never produced.

### 2.2 The seventeen policies (`floor/genesis-floor.cedar`)

| `@id` | Effect | Action(s) | Reads |
|---|---|---|---|
| `B1-read-corpus` | permit | Read | domain build; alphabet has Read; `resource in corpusRoot` |
| `B2-draft-workspace` | permit | Draft | alphabet has Draft; `resource in workspace` |
| `B3-invoke-allowlisted` | permit | Invoke | alphabet has Invoke; `resource in toolAllowlist`; `inputsInWorkspace` |
| `B4-emit-own-topic` | permit | Emit | owner is principal; topic epoch and round match; not sealed |
| `B5-submit-own-artifact` | permit | Submit | author is principal |
| `B6-vote-seated` | permit | Vote | `voteRulesEpoch == rulesEpoch`; grant roster with kind grant, or veto roster with kind observer |
| `B7-author-recused` | forbid | Vote | author is principal |
| `B8-grant-only-from-grant-seat` | forbid | Vote | verdict grant and not on the grant roster |
| `B9-voters-do-not-author` | forbid | Draft, Invoke, Submit | `roundRole == voter` |
| `B10-only-thinkers-author` | forbid | Draft, Invoke, Submit, Actuate | kind ≠ thinker |
| `R1-actuate-allowlisted` | permit | Actuate | domain run; alphabet has Actuate; `resource in toolAllowlist` |
| `R2-report-own-topic` | permit | Report | as B4 |
| `R4-consult-pinned` | permit | Consult | `resource in runRoot` |
| `R3-observer-live` | forbid | Actuate, Report | kind thinker and `!observerLive`; not Consult; applies under break-glass |
| `X1-break-glass` | permit (exception) | Actuate | `breakGlass.quorum`; `resource in breakGlass.tools`; does not read the alphabet |
| `X2-erasure` | permit (exception) | Erase | `erasureQuorum` |
| `F-forensic-classes` | forbid | Erase | `class` in F1..F6 |

Left out of the floor on purpose: epoch fencing, the round bound, the rules floor, `Invoke` hermeticity. An
evaluation error is a deny. Three schema attributes are read by no policy: `Lease.rulesEpoch`, `Tool.digest`,
`VoteCtx.epoch`.

### 2.3 The values file (`floor/genesis-values.json`)

The numbers the typed lift reads that Cedar text cannot hold. Every one is a placeholder and says so.

| Path | Value | Unit | Record | Read by |
|---|---|---|---|---|
| `observer.T_obs_ms` | 5000 | ms | ADR-0039 §1 | `Mechanism::fresh` at decide (per-replica clock, not re-checked at apply) |
| `observer.K` | 8 | unread emissions | ADR-0039 §1; ADR-0042 §2 | `State::observer_covers`; startup check `K < R` for both domains |
| `persona.T_persona_ms` | 3,600,000 | ms | ADR-0031 A2 | `apply_grant`, `apply_renew` |
| `lineage.theta_exact`, `theta_near`, `theta_gen`, `beta`, `near_tool` | `null` | — | ADR-0035 §3 | nobody; the gate counts how many are unset |

The round bound `R` is **not** in this file; it is a mechanism parameter (§5.3). Relaxing a value is an issuance
plus a promotion; tightening is a promotion. The file is compiled into `topak-floor` and only the `observer` and
`persona` blocks are deserialized.

### 2.4 The behavioural tests (`floor/genesis-tests.json`, `floor/gen-tests.py`)

- **Case**: `{name, request: {principal, action, resource, context}, entities, decision: allow \| deny, reason:
  [@ids], num_errors: 0}`. Entity refs in context are `{"__entity": {"type", "id"}}`. The full 44-entity slice is
  repeated in every case, which is why the file is 558 KB.
- **Count**: 62 cases, 17 allow, 45 deny; every permit has an allow and a deny case, every forbid is some deny's reason.
- **Fixed constants**: `EPOCH 3`, `ROUND 7`, `RULES 5`; five alphabets (`BUILD`, `VOTE`, `OBS`, `RUN`, `RUN_OBS`).
- Consumed by `cedar run-tests` and replayed by `topak-floor`'s tests. The generator writes to the current directory.

### 2.5 The gates (`floor/run-gates.py`, `floor/cvc5-checked`)

| Setting | Value |
|---|---|
| Environment | `CVC5` (default `cvc5`; the static build is `tools/cvc5-macOS-arm64-static`, untracked), `ETHOS` (default `tools/ethos-8dc85c4/bin/ethos`), `cedar` on PATH built with `--features analyze` |
| Wrapper environment | `TOPAK_CVC5`, `TOPAK_ETHOS` required; `TOPAK_CPC` default `../tools/cpc`; `TOPAK_PROOF_DIR` |
| Solver flags | `--produce-proofs --dump-proofs --proof-format-mode=cpc --proof-granularity=dsl-rewrite`; cedar's `--lang smt --tlimit=60000` |
| Header lines | title; floor, schema and values digests and policy count; cedar and cvc5 versions with the solver binary digest; checker commit and binary digest, CPC tree digest, wrapper digest |
| Verdicts | `refuted`; `holds✓` (every query checked); `holds°` (cedar decided without a query); `holds?` (unchecked; the run requires zero); `ERROR` |
| Routing | (F′⇒F, F⇒F′): holds/holds equivalent → promotion; holds/refuted tightening → promotion; refuted/holds relaxation → issuance + promotion; refuted/refuted incomparable → issuance + promotion |
| Controls | four negative floors (permit-all on Read and on Consult, a Long overflow on Emit, a duplicate F1 forbid); three lying solvers (no proof; proves `false`; one line deleted) |
| Evidence tree | `genesis-gates-evidence-<date>/index.tsv` (`call analysis action result queries checked sat unknown`) and `NNN/q-N.smt2`, `q-N.json`, `q-N.cpc` |
| `q-N.json` | `index, query, query_sha256, solver, solver_sha256, solver_argv, checker, checker_sha256, checked, answer, forwarded, reason, renamed, solver_stderr?, proof?, proof_sha256?` |
| `.cpc` | the Eunoia prelude derived from the query's own text, then the solver's `@` defines, `assume` and `step` lines; checked by `ethos --require-proof-of-false` printing exactly `correct`; every `assume` must be one of the query's `assert`s |
| Results file | header; values; totality rows; non-vacuity and discrimination rows; entry-matters rows; routing rows; negative and checker controls; `N cedar calls · M solver queries · …`; `RESULT: all gates pass` |
| Last run | 2026.10.01: cedar-policy-cli 4.13.0, cvc5 1.4.0 `a4ce24a176532209`, ethos 8dc85c4 `4eb41c1f1f9fce88`, CPC tree `6d7e8d208d223985`, wrapper `dfe159e9c21a549e`, evidence tree `f8b1196a427a35ed` |

A run without the wrapper and checker declares D-0030-2; every run before 2026.10.01 was one.

---

## 3. The bundle tier (`policies/`, `mechanism/bundles/`)

### 3.1 The input document

Built by `lift.rs` `bundle_input`, declared in `policies/bundle.rego`:

```
{ "action":    "Read" | "Draft" | "Invoke" | "Emit" | "Submit" | "Vote" | "Consult" | "Actuate" | "Report",
  "principal": {"seat": <id>, "domain": "build" | "run"},
  "resource":  {"object"} | {"target"} | {"tool", "digest"} | {"topic"} | {"artifact"[, "evidence"]},
  "inputs":    <object> | null,
  "request":   <the typed Action>,
  "context":   {"epoch", "round", "roundRole", "rulesEpoch", "lease": <fence>} }
```

The modules read only `input.action`, `input.resource.tool`, `input.resource.digest` and `input.inputs`.

### 3.2 Packages, data and output

| Package | Decides | Reads |
|---|---|---|
| `topak.bundle` (entrypoint `topak/bundle/allow`) | `default allow := false`; refuses an `Invoke` that `tool_invocation` refuses or an `Actuate` that `actuate` refuses; everything else passes | `input.action` |
| `topak.bundle.tool_invocation` | Invoke conforms to its schema | via `tool_schema` |
| `topak.bundle.actuate` | Actuate conforms and declares a well-formed channel | `tool_schema.schema.channel` |
| `topak.bundle.tool_schema` | `tool_key = "<name>@<digest>"`; `conforms`; `violations` | `data.topak.tools[key]` |

- **`data.json`**: `{"topak": {"tools": {"<name>@<digest>": {"required": {field: type}, "optional"?: {…},
  "channel"?: {"kind", "target"}}}}}`. Types are `string`, `number`, `boolean`, `array`, `object`, `null`; flat
  objects only. Today: `tlc@d1` (no channel) and `search@d3` (`https`, `search.internal:443`).
- **Output**: only `allow` is read by the mechanism; `violations` strings exist for a decision log nobody writes.
- **Channel** (PROVISIONAL, I33): `{kind: non-empty, target: non-empty}`, declared and not interpreted.

### 3.3 Packaging, revision and signature (`mechanism/scripts/build-bundle.sh`, `topak-bundle`)

| Item | Definition |
|---|---|
| Revision | SHA-256 over `path \0 bytes \0` for every non-test `.rego` and `data.json`, paths `LC_ALL=C` sorted; today `be46c574dfeeed16…`, equal to the tracked tarball's name |
| Build | `opa build -t wasm -e topak/bundle/allow --revision $rev --ignore '*_test.rego'` in the `openpolicyagent/opa` image on `linux/amd64` (**unpinned tag**) |
| Tarball | `/.manifest` `{"revision", "roots": [""], "wasm": [{"entrypoint": "topak/bundle/allow", "module": "/policy.wasm"}], "rego_version": 1}`; `/data.json`; `/policy.wasm`; `/policies/*.rego` (OPA rewrites `bundle.rego` on the way in; the revision hashes the source) |
| Signature | `<revision>.sig` = `Signed` over canonical `{"revision": rev}`, purpose `bundle`, key in `Rules.bundle_keys`; `TOPAK_BUNDLE_SECRET` makes the script sign; dev-init signs under the dev bundle key |
| Loading | `load_dir` requires the file name to equal the manifest revision, a `.sig`, an issued key and a verifying signature; one failing tarball stops the node |
| Sidecar | `POST {base}/v1/data/topak/bundle/allow?provenance=true` with `{"input": …}`; expects `{"result": true, "provenance": {"bundles": {<name>: {"revision"}}}}`; exactly one bundle at the lease's revision; non-2xx, timeout (`opa_timeout_ms` 250) or another revision falls back to WASM |
| WASM fallback | `opa-wasm` on wasmtime, one compiled policy per revision with its `data.json`; only `[{"result": true}]` allows; a fallback allow logs a warning |
| Binding to the lease | `Lease.bundle` is the revision, fixed across renewal; `grant` and `launch` refuse an unverified revision before proposing; `AdmitRecord.bundle` and `.engine` (`sidecar` \| `local_wasm`) record what decided |

---

## 4. Wire formats of the reference (`mechanism/`)

### 4.1 The agent socket (`<data_dir>/agent.sock`, mode 0660, one JSON line each way)

- **Request** `{"token": <64 hex>, "op": "act", "action": <Action>}`, or `{"op": "submit_workspace"}` (the
  mechanism computes the workspace digest, I12), or `{"op": "abstain"}` (refused for Run seats, I31).
- **Response** `{"admitted": bool, "detail": …}`; `detail` is `{"decision": "deny", "reason": <DenyReason>}`,
  `{"decision": "admit", "slot", "floor": [@ids], "engine", "result"}`, `{"abstained": true}` or `{"error"}`.
- **`result` per action**: Read and Consult `{object, content}`; Draft `{written, digest}`; Invoke the downstream
  `CallToolResult` or the Wasm tool's JSON; Actuate `{topic, offset, seq, outcome, result_digest, result}` or after
  a seal `{seq, outcome: "unknown", withheld}`; Emit and Report `{topic, offset, seq}`; Submit `{submitted}`; Vote
  `{recorded, artifact, promoted}`.
- **Token**: 32 random bytes as hex, minted by the applying replica, held in a per-replica `sessions` map as
  `{seat, fence, epoch}`; not replicated; `renew` moves its fence. PROVISIONAL (session binding), I14, G5. **A
  launched lease mints no token**: the bridge is the session.

### 4.2 The MCP front door (`topak mcp`, `topak-mcp/src/server.rs`)

| Domain | Tools | Input schema |
|---|---|---|
| build | `read{object}`, `draft{target, content}`, `invoke{tool, digest, inputs}`, `emit{record}`, `submit{artifact?}`, `abstain{}`, `vote{verdict, artifact, evidence, rules_epoch}` | every schema is `type: object`, `additionalProperties: false`, digests as `string` described as lowercase hex SHA-256 |
| run | `consult{object}`, `actuate{tool, digest, inputs}`, `report{record}` | as above |

A tool name maps to an `AgentOp` by adding `kind`; an unknown tool or a domain mismatch is `invalid_params`. The
result is a `CallToolResult` with one text block holding the pretty-printed `detail`. Protocol version seen in the
smoke client and the rehearsal server: `2025-06-18`.

### 4.3 The operator socket (`<data_dir>/operator.sock`, mode 0600; PROVISIONAL (operator authentication), G5)

| `op` | Request fields | Reply |
|---|---|---|
| `grant` | `principal, seat, persona, bundle, confinement{digest, rung}, alphabet[], ttl_ms, round, role` | `{ok, fence, token, lease, contained, because}`; an unverified bundle is refused before proposing |
| `renew` | `token, alphabet[], rung, ttl_ms` | `{ok, fence}` |
| `end_round` | `token, reason?` (default `operator`) | generic |
| `revoke` | `target{kind, id}, reason, attribution` | generic |
| `fence_epoch` | `reason, attribution` | generic |
| `issue` | `issuance{rules, signatures[]}` | generic |
| `gates_passed` | `artifact, evidence` | generic |
| `break_glass_approve` | `seat, epoch, approval: Signed` | generic |
| `register_profile` | `profile`: the file text verbatim | generic, `ProfileRegistered{digest}` |
| `launch` | `principal, seat, profile, bundle, alphabet[], ttl_ms, round, role` | `{ok, verdict: attested, fence, lease, rung, instance, evidence, contained, because, simulated}`; or `{ok: false, verdict: refused \| unattestable, reason}`; or `{ok: false, verdict: contested, evidence, applied}` |
| `status` | — | `{replica, chain, leader, last_applied, epoch, rules_epoch, floor, schema, params, live_leases[], candidates[], launched[]}` |

Generic reply: `{ok, slot, applied: <Applied>}` or `{ok: false, error}` after the 5 s commit deadline. The
`topak op` CLI takes the request inline, as a file path, or as `-`.

### 4.4 The guest channel (stdio, line-delimited JSON; `topak-contain/src/guest.rs`)

The guest writes first, exactly once, within `hello_timeout_ms`. **No token crosses this channel.**

| Direction | Message |
|---|---|
| guest → host | `{"msg": "hello", "persona", "family", "params", "root", "session_key"?}` |
| guest → host | `{"msg": "evidence", "report_data"}` in answer to `attest` |
| guest → host | `{"msg": "op", "op": <AgentOp>, "proof"?: <SessionProof>}` |
| host → guest | `{"msg": "attest", "nonce"}` |
| host → guest | `{"msg": "granted", "fence", "epoch"}` at grant and after every renewal |
| host → guest | `{"msg": "response", "response": <AgentResponse>}` |
| host → guest | `{"msg": "shutdown"}` |

A second hello or unsolicited evidence is a protocol error; the bridge ending while the lease is live proposes
`EndRound(operator)`. The guest-io buffer holds 64 lines.

### 4.5 Replica to replica (`topak-node/src/net.rs`; PROVISIONAL (replica authentication), G5)

Plain TCP; each frame is a big-endian `u32` length then the JSON of `[from_node_id, <Msg<Entry>>]`. `MAX_FRAME` 64
MiB; connect timeout 200 ms; per-peer queue 4096, dropping when full. The Paxos messages (`topak-paxos`): `Prepare`,
`Promise`, `Nack`, `Accept`, `Accepted`, `Commit`, `Heartbeat`, `CatchUp`, `Forward`. Frames are unauthenticated.

### 4.6 Kafka round topics (`topak-transport/src/lib.rs`)

| Item | Format |
|---|---|
| Record kinds | `emit`, `actuate`, `deny`, `overflow` |
| `EmitRecord` | `{topic, seat, fence, kind, admit?, seq?, digest, payload}` |
| Kafka key | the seat |
| Kafka value | `serde_json::to_vec(payload)`, **not canonical**; the `digest` is canonical |
| Headers | `topak-kind`, `topak-seat`, `topak-fence`, `topak-digest`, `topak-admit`?, `topak-seq`? |
| Seal marker | no key, no value, one header `topak-seal: <reason>`; the reason is the **Debug form** of `EndReason` (`Submitted`), not the serde form (`submitted`) |
| Emit / Report payload | the record verbatim; heartbeats travel this way |
| Actuate payload | `{"actuate": {tool, breakGlass, inputs, outcome, result, channel?}, "body": {inputs, result}}` |
| Deny payload | `{denied: <Admitted>, reason: <DenyReason>, epoch, round, at, decided_by}`; to the round topic while open, else `<topic>.after` |
| Overflow payload | `{overflow: true, limit, epoch, round, at, decided_by}`, once, on `.after`; later denials dropped; the counter is per replica (I23) |
| Topic settings | one partition, `replication` from config (default 1), `acks=-1`, no compression, create timeout 5000 ms |
| Sequence | per round topic, continued across renewal; Build counts emissions and heartbeats, Run counts Actuate, Report and heartbeats; Consult advances nothing (I28) |

Only the deciding replica writes, and only after commit. An unknown token writes nothing and logs to target `security`.

### 4.7 The Wasm Run tool ABI (`topak-contain/src/wasmtool.rs`; PROVISIONAL (tool-abi), I44)

Imports, all from module `topak`: `input_len() -> i32`, `input_read(ptr)`, `output(ptr, len)`, `connect() ->
handle | -1` (only to the declared target; no address crosses), `send(h, ptr, len)`, `recv(h, ptr, cap)`. Exports
`memory` and `run() -> i32` (0 is ok). Input is the inputs map as JSON; output must be JSON, empty meaning `null`.
Any other import is refused at load and the node does not start. Limits: `FUEL` 50,000,000; `NET_TIMEOUT` 2 s. One
fresh instance per call. `WasmToolSpec = {module, module_sha256, channel?: {kind, target}}` under the node config's
`wasm_tools`, keyed `name@<module sha256>`; `channel: None` is hermetic. `ChannelUse{connects, sent, received}` is
returned and not recorded.

### 4.8 The native tool host (`topak-mcp/src/toolhost.rs`)

`ToolSpec = {command, args[], binary_sha256, mcp_tool}` under the node config's `tools`, keyed `name@digest`. The
allowlist digest is `SHA-256(binary_sha256 ‖ 0x00 ‖ canonical_json(MCP input schema))` (I13). Every call re-hashes
the binary, spawns it with a cleared environment in the workspace or run directory, runs the MCP list-tools method, recomputes
the digest, then makes one call-tools request. Nothing is checked about hermeticity or channel (G4, G19).

---

## 5. The replicated log, state and configuration of the reference

### 5.1 Log entries (`topak-core/src/state.rs` `Entry`, tagged `entry`)

Every variant has an `id` of the form `n<replica>-<boot hex16>-<counter>`, which makes re-proposal idempotent.

| Variant | Payload | Produced by |
|---|---|---|
| `Grant` | `req: GrantRequest` (the lease without epoch, fence, rulesEpoch), `appraisal?` | `grant` op; the launcher |
| `Renew` | `req: {seat, fence, alphabet, rung, ttl_ms}`, `appraisal?` | `renew` op; the launcher's renewal loop |
| `Admit` | `rec: AdmitRecord` | the admit path |
| `EndRound` | `seat, fence, reason, attribution` | `end_round`; abstain; the expiry sweep; the bridge closing |
| `Revoke` | `target, reason, attribution` | `revoke` op |
| `EpochIncrement` | `reason, attribution` | `fence_epoch` op |
| `Contested` | `appraisal, attribution` | the launcher |
| `ProfileRegister` | `profile`: the file bytes verbatim | `register_profile` op |
| `Issue` | `issuance` | `issue` op (F4) |
| `GatesPassed` | `artifact, evidence` | `gates_passed` op (PROVISIONAL (gate runner)) |
| `BreakGlassApprove` | `seat, epoch, approval: Signed` | `break_glass_approve` op |

**`AdmitRecord`** (F1): `{seat, lease, epoch, action: Admitted, input, floor, schema, floor_reasons, bundle, engine,
params, decided_by, session?}`. `Admitted` is the payload-free summary (`Read{object}`, `Draft{target, content:
digest}`, `Invoke{tool, inputs: digest}`, `Emit{record: digest}`, `Submit`, `Vote`, `Consult`, `Actuate{tool,
inputs, break_glass}`, `Report`, `Heartbeat{via, topic, watermark}`). **The values-file digest is recorded nowhere.**

**`Applied`**: `LeaseGranted{fence}`, `Renewed{fence}`, `Admitted{seq, promoted}`, `RoundEnded`, `Revoked{ended}`,
`EpochIncremented{epoch}`, `Contested{ended}`, `ProfileRegistered{digest}`, `Issued{rules_epoch}`, `GatesRecorded`,
`BreakGlassApproved{approvals}`, `Rejected(String)`, `Duplicate`.

**`MechanismDeny`**: `UnknownLease`, `WrongSeat`, `BadHeartbeat`, `FencedEpoch`, `RequestEpochMismatch`,
`FencedRulesEpoch` (PROVISIONAL (rules-epoch fence), I6), `LeaseEnded`, `LeaseExpired`, `NotInAlphabet`,
`RoundBoundReached`, `ArtifactNotSubmitted`, `ArtifactAlreadySubmitted`, `GatesNotPassed`, `EvidenceMismatch`,
`AlreadyPromoted`, `Other`.

### 5.2 State (`State`, in memory only; rebuilt by replaying the log; no snapshots)

`chain`, `epoch`, `rules`, `floor_exceptions`, `leases: fence → LeaseRecord`, `live_by_seat`, `last_round`,
`candidates`, `gates`, `break_glass: seat → epoch → keys`, `revoked`, `applied_ids` (PROVISIONAL (dedupe growth),
G14), `last_applied`, `observer`, `persona` (the floor values), `marks: observer → topic → watermark`, `seals: seat →
{topic, seq}`, `profiles: digest → {profile, artifact, registered_at}`, `contested: principal → evidence`.
Per-replica and not replicated: `sessions`, `observed`, `heard`, `after_written`, `in_flight`, `launched`.

### 5.3 Mechanism parameters (`Params`; `dev/params.json`; identical on every replica; digest in every admit, I21)

| Field | Dev value | Record |
|---|---|---|
| `corpus: Set<Digest>` | `../spec/*.tla` | ADR-0022 §3 corpus root |
| `build_tools`, `run_tools: Set<name@digest>` | the demo tool | the allowlists (channel elsewhere, I33) |
| `run_root: Set<Digest>` | — | ADR-0040 §3 (I32) |
| `wasm_tools: Set` | — | PROVISIONAL (wasm-tools), I44 |
| `round_bound` | 200 | Build `R`, placeholder |
| `run_round_bound` | 64 | Run `R`, placeholder |
| `lease_margin_ms` | 500 | ADR-0032 §2 asymmetric margin |
| `after_topic_limit` | 64 | ADR-0003 A2 bound (I23) |

### 5.4 Node configuration (`topak-node/src/config.rs`; `dev/n{1,2,3}.json`; relative paths resolve against the file)

| Field | Default or dev value |
|---|---|
| `id`, `peers: {id: host:port}` | dev peers `127.0.0.1:7101`–`7103` |
| `data_dir`, `agent_socket`, `operator_socket` | `run/n<i>`, `run/n<i>/{agent,operator}.sock` |
| `rules`, `params`, `corpus_dir`, `bundles_dir` | paths |
| `opa_sidecar: Option<URL>` | null, or `http://127.0.0.1:18181` with `--opa` |
| `opa_timeout_ms` | 250 |
| `kafka: {brokers[], replication}` | null, or `127.0.0.1:9092`, replication 1 |
| `tools: {id: ToolSpec}`, `wasm_tools: {id: WasmToolSpec}` | the demo `wordcount` tool; no Wasm tools |
| `heartbeat_ms` | 50 |
| `election_timeout_ms` | 400 (the Paxos crate's own default is 300) |
| `contain: {backends: {rung: BackendConfig}, verifier?, evidence_dir, hello_timeout_ms}` | none in dev; `evidence_dir` default `<data_dir>/evidence`; `hello_timeout_ms` 10000 |

**Backends** (tagged `kind`): `process{command, args}` and `docker{docker, image_ref, args, mounts}` at rung 1;
`sim-cvm{command, args, model, chip_secret, tcb}` at rung 3 (SIMULATED, feature `sim`); `measured-boot`, `snp`,
`tdx` seams that always fail. **Verifiers**: `http{url}` (always unreachable) and `sim{secret, endorsement}`.
A backend whose rung does not match its key is refused; a sim config without the `sim` feature is refused.

### 5.5 On-disk files under `data_dir` and beside it

| Path | Format | Note |
|---|---|---|
| `wal.jsonl` | one JSON line per persisted Paxos output: `{"Promise": {"ballot"}}` or `{"Accept": {"slot", "ballot", "cmd": "Noop" \| {"Value": <Entry>}}}` | append-only, fsync per batch, replay stops at a torn line, never compacted (G14) |
| `archive.jsonl` | `{"slot", "entry", "applied"}` per line | truncated at startup and rebuilt (G9) |
| `workspaces/ws-<seat>-e<epoch>-r<round>/` | Draft targets | not replicated |
| `run/<seat>-e<epoch>-r<round>/` | working directory for native Run tools | |
| `evidence/<digest>.json` | `Evidence` | named by the canonical digest, written non-canonically |
| `corpus_dir/<sha256>` | one file per object, named by its bytes' digest | re-checked on Read and Consult |
| `bundles_dir/<rev>.tar.gz`, `<rev>.sig` | §3.3 | |
| `dev/secrets/<name>.json` | `{public, secret}` **in the clear** | names `seat-*`, `anchor-1..3`, `bg-1..2`, `bundle` (G6) |
| `mechanism/corpus-pins.sha256` | 49 `shasum` lines: 35 records, 14 modules | `tests/drift.rs` fails on drift and on an unpinned citation |
| `.env` under `mechanism/` (generated, gitignored) | `TOPAK_BUNDLE=<rev>` | read by docker-compose |

### 5.6 Constants, timers, environment and CLI

| Setting | Value | Where |
|---|---|---|
| `COMMIT_DEADLINE` | 5 s | `mechanism.rs` |
| `RETRY_EVERY` | 750 ms, same id | `mechanism.rs` |
| driver tick | 10 ms | `driver.rs` |
| expiry sweep | 250 ms | `topak-node/src/lib.rs` |
| channel sizes | proposals 1024, inbound 8192, launcher ctl 8 | `lib.rs`, `launch.rs` |
| launcher renewal | every `ttl_ms / 2`, minimum 1 ms, fresh nonce, same guest | `launch.rs` |
| Paxos `Config` | `heartbeat_ms 50`, `election_timeout_ms 300`, `max_catchup 256`; staggered as `et + rank·et/n` | `topak-paxos/src/replica.rs` |
| startup checks | `K < R` both domains; every `wasm_tools` id hosted; genesis rules satisfy the rules floor; every bundle verifies; floor digests match | `mechanism.rs`, `lib.rs`, `topak-floor` |
| `TOPAK_TRACE_DIR` | per-apply `.jsonl` recording for named states | `trace.rs` |
| `TOPAK_BUNDLE_SECRET` | hex32; signs the bundle | `build-bundle.sh` |
| `TOPAK_BUNDLE` | which tarball the sidecar loads | `docker-compose.yml`, `.env` |
| `TOPAK_DOCKER_IMAGE` | enables the real-container launcher test | `topak-contain/tests/launch.rs` |
| `RUST_LOG` | log filter, default `info`; targets `security`, `guest` | `main.rs` |
| `topak` CLI | `node --config`; `mcp --socket --token [--domain]`; `op --socket <json\|file\|->`; `keygen`; `sign --purpose --secret <body>`; `tool-digest --command --tool [-- args]`; `check-rules <rules.json>`; `profile-digest <profile.json>` | `main.rs` |
| docker-compose | `apache/kafka:latest` on 9092; `openpolicyagent/opa:latest` on 18181 serving `/bundles/${TOPAK_BUNDLE}.tar.gz` unsigned | `docker-compose.yml` |
| Cargo features | `sim` on `topak-node` and `topak-contain` | `Cargo.toml` |

Process guests and downstream tools run with a cleared environment; no other `env::var` reads exist.

### 5.7 The scripted guests (`topak-demo-guest`, `guest/demo_guest.py`)

`--model <model.json>` (required), `--rung N` (1), `--read`, `--consult`, `--tool`, `--script` steps from `read`,
`draft`, `emit`, `submit`, `consult`, `actuate`, `report`, `wait:<ms>`, `--exit`, `--rogue` (changes only the
measured arguments). Exit 3 if the weights mismatch `model.json`, before any hello. At rung ≥ 2 it signs every op
with a session key, `ctr` from 1. Fixed payloads: Draft target `notes.md`; Emit and Report `{"note": "occupant"}`;
Actuate inputs `{"open": "v7", "by": <persona short>}`.

---

## 6. The specification layer (`spec/`)

### 6.1 Modules, constants and the values the drivers assign

Conventions (`spec/README.md`): one `Mut` switch and one guard per mutation; a `Never…` witness per reachability
claim; a type invariant; constants unconstrained in the module and bound in the run script. Every `*-run.sh` writes a
`.cfg` (gitignored), runs TLC with `-workers auto -deadlock -metadir /tmp/tlc_<name>`, and prints one line
`name | … | inv | HOLDS | COUNTEREXAMPLE | ERROR | N distinct states`.

| Module | CONSTANTS | Driver values | Mutations |
|---|---|---|---|
| `RulesFloorBase` | `Active` | via the bootstrap driver; defines Humans h1..h5, AnchorKeys {h4}, entries R1 R2 R5 R6 R7 R9 | — (live, ADR-0046 E1) |
| `RulesFloorNV` (frozen, G1) | `h1..h4, Humans, Author, AnchorKeys, Active, Mech` | four humans; `Mech` ∈ param, as0024, rev4 | drop entries from `Active` |
| `RulesFloorNV_rev5` | `Active, Mech` | `Active = {R1,R2,R5,R7,R9}` and drop sets; `Mech` ∈ rev5, norecuse | drop entries |
| `NonComposition` | `Mut` | — | `M1`, `M2` |
| `Anchor`, `BreakGlass` | `Mut, MaxEpoch` (+ `Active`) | `MaxEpoch 2`; `Active = {R1,R2,R5,R6,R7,R9}` | `M_FLOOR`; `M_SCOPE` |
| `Lease` (frozen), `Lease_A1` | `Mut, MaxEpoch, MaxFence` | 2, 3; rungs 0..2 / 0..3 | `M_RENEW M_FENCE M_RUNG M_ROLE M_REVOKE` (+ `M_LOWER`) |
| `FloorComposition` | `Mut` | fixed literals | `M_OVERRIDE M_ERR M_FAILOPEN M_WRITE` |
| `FloorRouting` | `Mut` | — | `M_ROUTE M_GATE` |
| `Confinement` (frozen), `Confinement_A1` | `Mut, Declared, MaxEpoch, MaxIdx, MaxGen` | `Declared` 0..3; 1, 4, 2 | `M_HOST M_HW M_CONTESTED M_UNBOUND M_STALE M_DOWNGRADE M_PROFILE M_RENEWLOW` |
| `Seats`, `RunSeats` | `Mut` | — | `M_KIND M_SEAT`; `M_KIND M_DOMAIN M_OBSEMIT` |
| `Observers` | `Mut` | — | `M_QUORUM M_REACH` |
| `Coupling`, `RunCoupling` | `Mut, K, R, MaxRound` | `K 1`, `R 3` / `R 4`, `MaxRound 2` | `M_NOCOUPLE M_MARK M_ROUNDS M_CORR`; + `M_EMITSEQ M_COUPLEALL M_BOUNDEFF` |
| `RunConfinement` | `Mut, Filtered` | `Filtered` TRUE / FALSE; tools w, f, n; targets a, b, c | `M_CHANNEL M_NATIVE M_FILTER` |
| `Mechanism` | `InitState, Trace` | bound by the generated `Trace_*.cfg` | `TraceMatches`, violated at the first differing step |
| `ConfinementRefinement` | — | reads every replayed state | `RNoSilentDowngrade RContestedStopped RFreshAppraisal RContainedAttested ConfinementRefined` |

A planned `-medium` run at practical constants (`K 8`, `R 64`, three rounds, two epochs) has no results file yet
(G9 item 75). `simulate-run.sh` exists with no results file.

### 6.2 The operational model's projected shapes (`spec/Mechanism.tla` header)

- **State**: `epoch, rulesEpoch, seats, grantRoster, vetoRoster, quorum, minGrant, bgIssued, bgRoster, verifierKeys,
  bundleKeys, personas, criterion, leases, liveBySeat, lastRound, candidates, gates, approvals, revoked, appliedIds,
  lastApplied, k, tPersona, marks, seals, profiles, contested, contained, wasmTools, buildBound, runBound`.
- **Lease**: `principal, seat, persona, epoch, rulesEpoch, conf, rung, alphabet, round, role, ttl, ended, actions,
  seq, att, sessionCtr`. **Att**: `verdict, nEpoch, nIndex, gen, key, platform`. **Seat**: `domain, kind, cell, rung`.
- **Profile**: `artifact, summary{image, persona, measurement, minTcb, domain, p3, p4, p5}, registeredAt`.
- **Appraisal**: `verdict, rung, profile, persona, nEpoch, nIndex, principal, round, key, measurement, tcb, platform,
  gen, evidence`. **Candidate**: `artifact, author, votes, promotedAt`.
- **Encoding**: functions as `(k :> v @@ …)`, a topic as `<<seat, epoch, round>>`, `"none"` for absent.
- **Oracle fields** the model takes from the trace rather than computing: `ok` (Issue, BreakGlassApprove, Admit,
  ProfileRegister), `proofOk` (Admit), `sigOk`, `sigKey` (Grant, Renew, Contested), the ProfileRegister parse.

### 6.3 The trace pipeline

| Stage | Format |
|---|---|
| Recorder (`trace.rs`) | `<TOPAK_TRACE_DIR>/<prefix>-<thread>-<n>.jsonl`; prefixes `mut`, `conf`, `e2e-<fixture>`, `contain-<name>` |
| Line 1 | `{"init": <projected state>}` |
| Later lines | `{"index", "entry": <projected entry + oracle fields>, "applied", "state"}` |
| Encoding | `{"$f": [[k, v], …]}` a function; `{"$s": […]}` a set; arrays tuples; other objects records; `"none"` absent; topics `[seat, epoch, round]` |
| Converter (`trace2tla.py`) | `Trace_<basename>.tla` extending `ConfinementRefinement` with `TraceInitState` and `TraceSeq`; `.cfg` with `SPECIFICATION TraceSpec`, `INVARIANT TraceMatches`, `INVARIANT ConfinementRefined` |
| Driver (`mechanism-trace-run.sh`) | `-workers 1`; prints `<mod> \| <steps> steps \| MATCH`, `MISMATCH at step N`, `REFINEMENT <Inv> violated at step N`, or `ERROR`; removes the `.cfg`, **leaves `Trace_*.tla`** |
| Results (`mechanism-trace-results.sh`) | header: `Module: Mechanism.tla (sha256) · TLC <ver> (jar sha256) · <java>`; `Reference: mechanism/ at <sha>[ + working tree] · recorder · converter · driver`; `Suites traced`; body: cargo result lines, per-trace lines, `N traces · S steps` |

### 6.4 Results, proofs and sync

| Artifact | Format |
|---|---|
| TLC results header (since 09.30) | `TLC Version 2.19 of 08 August 2024 (jar sha256 936a262061c91469)`; sections `=== name · Declared=… · Mut=… · INVARIANT …` |
| Row lists | `<lowercase>-rows-<date>.txt`: `name mut declared invariant` (confinement) or `name mut filtered invariant` (runconfinement) |
| Proof results header (`proof-results.sh`) | title; `Modules:` every local module in the EXTENDS chain with digests; `Prover: tlapm <version> (binary sha256 <16>) · backends: <SMT> · <zenon> · <Isabelle> · LS4 for PTL · driver`; `Assumptions:`, `Theorems:`, `Lemmas:`; the `tlapm --cleanfp --strict` output ending `All N obligations proved` |
| Proof naming (`proof-method.md`) | `<Invariant>Always == Spec => []<Inv>` under `ASSUME Mut # "M_X"` for the mutations that break it; `SafeAlways` under `Mut = "none"`; one `Mut<Name>…` lemma per mutation |
| `proof-sync.sh` | newest `<M>-proof-results-*.txt`; every `Modules:` digest compared with the tree; `IN SYNC` \| `STALE` \| `MISSING RESULTS`; the prover digest on every results file must equal `tools/TLAPS-PIN`; every unproved module needs a reason (RulesFloorBase, RulesFloorNV, Lease, Mechanism, ConfinementRefinement are listed); exit 1 otherwise |
| Obligations | Anchor 40 · BreakGlass 37 · Confinement 502 · Confinement_A1 503 · Coupling 320 · FloorComposition 171 · FloorRouting 36 · Lease_A1 200 · NonComposition 58 · Observers 65 · RulesFloorNV_rev5 262 · RunConfinement 116 · RunCoupling 469 · RunSeats 147 · Seats 110; total 3,036 |
| Prover | `tlapm 7824dab`, binary `e150fb793fb28592`, Z3 4.8.9, zenon 0.8.4, Isabelle2025 |

---

## 7. Tooling, manifests and tags (`tools/`, `manifests/`, `checkpoints/README.md`)

| Item | Format or value |
|---|---|
| `tools/TLAPS-PIN` | `key value` lines: `version 1.6.0-pre`, `commit 7824dab`, `binary_sha256_16 e150fb793fb28592`, `platform arm64-darwin`, `backends …`, `pinned 2026.10.03`; the full digest is still owed |
| `tools/tlapm` | runs `${TLAPM:-tools/tlaps-<version>/bin/tlapm}`; refuses a digest mismatch unless `TLAPM_UNPINNED=1` |
| `tools/tlc`, `tools/tlc-workers` | `java -XX:+UseParallelGC -jar tla2tools.jar` (+ `-workers auto`); jar v1.7.4, TLC 2.19, sha256 `936a2620…`, tracked |
| `tools/install-tla.sh` | `TLA_VERSION v1.7.4`; refuses to overwrite the tracked jar |
| `tools/install-tlaps.sh` | version from the pin; `arm64-darwin` or `x86_64-linux-gnu`; extracts into `tools/tlaps-<version>/` (untracked, 1.9 GB) |
| `tools/install-ethos.sh` | `ETHOS_COMMIT 8dc85c4db8d6…`; builds `tools/ethos-8dc85c4/bin/ethos` and a `COMMIT` file |
| `tools/cpc/` | the cvc5 1.4.0 CPC Eunoia signature, 53 `.eo` files, tracked and measured |
| `tools/cvc5-macOS-arm64-static` | cvc5 1.4.0, untracked, no installer; pinned only by the digest the gate header prints |
| `tools/verify-manifest.sh` | `MANIFEST COMMIT [expected]`: `git archive` then `shasum -c`; `--all` reads `index.tsv` |
| `tools/cut-manifest.sh` | `git ls-files -co --exclude-standard`, minus `manifests/EXCLUDE`, `LC_ALL=C` sorted; **`-co` includes untracked files** |
| `tools/check-refs.py` | every backticked root-relative path in tracked `*.md` must exist; dates in the wrong form are flagged; `KNOWN`, `KNOWN_FILES` and `MOVED` lists |
| `manifests/index.tsv` | `name kind cut commit entries expected_ok note`; kinds historical, checkpoint, reference, rehearsal |
| `manifests/EXCLUDE` | one ERE per line: root files, `.claude/`, `.github/`, `doc/`, `sessions/`, the tool scripts, `diagrams/`, the manifest files, `mechanism/`, `policies/`, `slm/` (measured by their own manifests), the README files |
| Manifest kinds | `SHA256SUMS-G<n>` the corpus at a checkpoint; `SHA256SUMS-REF-<date>` `mechanism/` and `policies/` at the commit an ADR-0033 addendum cites; `SHA256SUMS-SLM-<date>` the rehearsal tree; the historical flat layout |
| The self-digest rule | a manifest's own digest and the checkpoint entry are recorded in the commit that adds them, and `index.tsv` names that commit (G9 §9) |
| Tags | `G3`–`G9`; `ToO-rev7`–`ToO-rev13`; `glossary-2026.09.30`, `-10.01`, `-10.02`; `REF-2026.09.24` … `-2026.10.02b` (**no `REF-2026.10.01`**); `SLM-2026.09.28` |
| Checkpoint file | `topak-genesis-checkpoint-G<n>-YYYY.MM.DD.md`; §9 gives the manifest name, count and per-area table |

---

## 8. The rehearsal's schemas (`slm/`)

Every rehearsal artifact carries a `schema` field of the form `topak.<name>/0`.

| Schema | Fields |
|---|---|
| `topak.slm.corpus/0` (`prepare_corpus.py`) | `id, source, slice, declaration, objects, bytes, docs, est_tokens, prepared_by{tool, digest}, objects_digest`; shards are JSONL `{"id", "text"}` named by their sha256 under `objects/` |
| `topak.slm.tokenizer/0` (`train_tokenizer.py`) | `vocab_size, eot_id, digest, sample, config`; byte-level BPE, `<\|endoftext\|>`, vocab 16384 default |
| `topak.slm.tokens/0` (`pretokenize.py`) | `dtype, eot_id, vocab_size, tokenizer, objects, val_permille (5), splits, bytes_per_token, bins, config`; `train.bin`/`val.bin` as uint16 |
| `topak.slm.model/0` (`train.py`) | `model_config, family_tag, params, root, init, weights, tokenizer, tokens_meta, seed, config_digest, steps, total_steps, tokens_seen, stopped, complete, final_val_loss, elapsed_s` |
| `topak.slm.manifest/0` (`manifest.py`) | `lineage, authored{by, at}, corpus[], tokenizer, tokens, code{git, files, digest}, config, seed, family, model{…}, parent` |
| `topak.lineage/0` (`lineage/record.py`) | §1.7 |
| `topak.overlap/0` (`lineage/overlap.py`) | `tool, params, a, b, smaller, exact{share_of_smaller, matched_bytes_a, matched_bytes_b}, near{…}, partial, elapsed_s`; normalization `nfkc-lower-alnum-v1`; defaults granularity `doc`, ngram 5, perms 112, bands 14, seed 35 |
| `topak.independence-table/0` (`lineage/independence.py`) | `thresholds, thresholds_digest, lineages[], table[{pair, strength}], evaluations[{pair, independent, fired, clauses{E1..E5}, strength, archetype_eligible}]` |
| `topak.lineage-crosscheck/0` (`lineage/project.py`) | `lineage, record, verdict: consistent \| Contested, divergences[{field, claimed, projected, attribution{seat, lease, slot}}], strength, rung`; exit 4 when Contested |
| `corpora.json` | `{corpora: {id: {role, source{hf_repo, revision, files, text_column, id_column, max_doc_chars?}, declaration{generators, generated_share, curators, notes}}}}`: the corpus admission declaration |
| `lineages.json` | `profiles{smoke, small, full}` with `preset, tokens_budget, corpus_max_bytes, micro_batch, tokens_per_step`; `lineages{L-A … L-E5}` with `corpus, family, seed, expect, init_from?, tokenizer_from?, budget_frac?, lr_peak?, warmup_frac?, corpus_scale?` |
| Thresholds (`lineage/thresholds.example.json`, PLACEHOLDER) | `mode bounded`; `theta_exact 0.01`, `theta_near 0.05`, `theta_gen 0.5`; `*_bytes 1e6, 1e7, 1e8`; `near_tool null`; `granularity window:256`. **A different field set from the values file's `lineage` block** (no `beta`; adds `*_bytes` and `granularity`), and non-null where the floor's are null |
| Rehearsal cluster (`rehearsal/init.py`) | `rules.json` (quorum all, min_grant 2, seats, rosters, three anchor keys, break-glass quorum 2, actions `RunInvoke`); `params.json` (round_bound 200, lease_margin_ms 500, after_topic_limit 64); `n1..n3.json` on ports 7201–7203; `cluster.json` |
| `rehearsal/slm_tool.py` | MCP over stdio; tools `slm_tokenizer`, `slm_pretokenize`, `slm_pretrain`, each `{config: string}` |
| `serve/serve.py` | JSON-RPC 2.0 over stdio, protocol version echoed (default `2025-06-18`); tools `generate{prompt, max_new_tokens ≤ SLM_MAX_NEW (512), temperature, top_k, seed}` and `model_info`; `SLM_MAX_PROMPT_CHARS` 16384; exit 3 on a bundle digest mismatch |
| `serve/run.sh` | `--network none --read-only --tmpfs /tmp:…,size=16m --cap-drop ALL --security-opt no-new-privileges --user 10001:10001 --ipc none --pids-limit 64 --memory ${SLM_MEMORY:-2g} --cpus ${SLM_CPUS:-4} --log-driver none`; three read-only mounts; `SLM_IMAGE`, `SLM_MODEL_SHA256`, `SLM_RUNTIME` |
| `serve/profile-host-rung0.json` | the rung-0 declared profile: `image null`, `launch{kind host-process, …}`, `channel`, `persona`, `clauses` P1 fail, P2 fail, P3 fail, P4 vacuous, P5–P7 pass, `subtractions` P1–P3, `_ladder` |
| Training constants | presets 1m / 10m / 30m / 46m / 125m (`d_model` 64 … 768); `ModelConfig` vocab 16384, rope 10000, `norm_eps_e6 10`; `train.py` defaults seed 1234, lr_peak 6e-4, warmup 0.01, weight_decay 0.1, betas 0.9/0.95, grad_clip 1.0, bf16 |
| Pins | `uv.lock` (mlx 0.32.2, numpy 2.5.3, tokenizers 0.23.2, pyarrow 25.0.1); the serve image `python:3.12-slim@sha256:f77ac9e4…`, pip `--require-hashes` |

The rehearsal's canonical JSON (sorted keys) differs from the reference's insertion-order JSON; the register's
finding 15 and the 2026.10.02 fix in `topak-core` are the consequence.

---

## 9. Settings with their values, in one place

| Setting | Value | Kind | Owner |
|---|---|---|---|
| `K` | 8 | placeholder, policy-floor value | ADR-0039 §1 |
| `T_obs` | 5000 ms | placeholder, policy-floor value | ADR-0039 §1 |
| `T_persona` | 3,600,000 ms | placeholder, policy-floor value | ADR-0031 A2 |
| θ_exact, θ_near, θ_gen, β, near_tool | null | unset, policy-floor values | ADR-0035 §3 |
| `R` (Build) | 200 | placeholder, mechanism parameter | ADR-0022 §3 |
| `R` (Run) | 64 | placeholder, mechanism parameter | ADR-0040 §3 |
| `lease_margin_ms` | 500 | mechanism parameter | ADR-0032 §2 |
| `after_topic_limit` | 64 | mechanism parameter | ADR-0003 A2 |
| `T_BG` | none | archetype value undeclared | ADR-0026 A1 (R8, pending) |
| `T_irrev`, `W`, `L`, `D` | undeclared; `W` about 1 s | a form, per effect class | ADR-0032 §4 |
| `EXCEPTION_BOUND` | 2 | mechanism constant | ADR-0026 R6 |
| `quorum`, `minGrant` | `"all"`, 2 | issued rules; archetype values | ADR-0024 §2 |
| custody pair | (1, 0) | declared | ADR-0025; ADR-0029 |
| `MAX_RUNG` | 3 | mechanism constant | ADR-0034 §2 |
| `opa_timeout_ms` | 250 | node config | Reference |
| `heartbeat_ms`, `election_timeout_ms` | 50, 400 | node config | Reference |
| `hello_timeout_ms` | 10000 | node config | Reference |
| `COMMIT_DEADLINE`, `RETRY_EVERY` | 5 s, 750 ms | constants | Reference |
| `FUEL`, `NET_TIMEOUT` | 50,000,000; 2 s | Wasm host limits | Reference (I44) |
| `MAX_FRAME` | 64 MiB | replica transport | Reference |
| TLC constants in runs | `MaxEpoch 2`, `MaxFence 3`, `MaxIdx 4`, `MaxGen 2`, `K 1`, `R 3 / 4`, `MaxRound 2` | small constants | `spec/*-run.sh` |
| prover, checker, solver, engine | tlapm 7824dab; ethos 8dc85c4; cvc5 1.4.0; cedar-policy 4.13 | toolchain pins | `tools/TLAPS-PIN`, `tools/install-ethos.sh`, gate headers, `topak-floor` |
| OPA, Kafka images | `latest` | **unpinned** | `docker-compose.yml`, `build-bundle.sh` |

---

## 10. What this inventory does not cover

The diagrams and their generators (`diagrams/`, unmeasured, G9 item 76). The content of frozen revisions and
earlier derived documents. The `doc/` reference material, which is not the corpus's to redistribute. Runtime
directories (`dev/` and `target/` under `mechanism/`, `slm/data/`, `slm/runs/`, `spec/.tlacache/`). The byte-level
Paxos state machine beyond its messages and config. Anything the records describe and nothing implements, such as
the archive, the plaintext store, write-time masking, the Persona record proper and the bootstrap ceremony, beyond
naming them as absent.

---

## 11. Findings: where the layers disagree

Each was verified against the tree named in the header. None is a decision; each names where a fix would go.

**Documentation behind the code**

1. **The values file and the floor crate say `T_persona` is unread.** `floor/genesis-values.json` labels the
   `persona` block "ADR-0031 A2 (Pending)" and "Not yet read by the reference"; the comment in
   `mechanism/crates/topak-floor/src/lib.rs` says the same. A2 was ratified in Batch 17 and the bound is enforced at
   grant and renewal since ADR-0033 A6. The `K` note also calls ADR-0042 §2 "Proposed".
2. **`spec/README.md` counts thirteen proof modules** and omits `Confinement_A1.tla`, `RunConfinement.tla` and
   `ConfinementRefinement.tla` from its module table; there are fifteen, and `proof-sync.sh` reports all fifteen in
   sync.
3. **`manifests/README.md` still says `SHA256SUMS-G1` … `-G8`**, and its verification example names G8.
4. **The glossary's own body is behind its header**: the Theory of Operation entry says "Rev 9 is current", and the
   hazards list names assumptions A1–A10 where the table has A14. Frozen between checkpoints; for the next cut.
5. **`decisions/README.md` is headed "Status at G8."**
6. **ADR-0037 §4 names the retired `RunInvoke` once unstruck**, in the B10 bullet; two other sites strike it.
7. **`checkpoints/README.md` lists tags `ToO-rev7`–`ToO-rev12`** while `ToO-rev13` exists; and **no `REF-2026.10.01`
   tag exists** although `SHA256SUMS-REF-2026.10.01` and its index row (`dacbb0c`) do.
8. **The gaps register says every item is tagged in code**, and the code lacks `PROVISIONAL (evidence-retention)`
   (I40) and `PROVISIONAL (session-proof)` (I41); I42 is marked only SIMULATED; two sites carry a bare
   `PROVISIONAL:` with no tag (`rules.rs` break-glass quorum, `state.rs` channel schema). Fifteen tagged sites exist.
9. **The register's G6 says the dev rules issue "1 veto seat"**; `dev-init.sh` issues two (`o1` and `corr`) and eight
   seats.
10. **`run-gates.py`'s docstring says evidence goes to `<results>.evidence/`**; the code writes
    `genesis-gates-evidence-<date>/`.

**Pins, digests and canonical forms**

11. **The OPA image is unpinned** in `build-bundle.sh` (`openpolicyagent/opa`, so `latest`) and in
    `docker-compose.yml` (`:latest`); so is `apache/kafka:latest`. The bundle revision hashes the Rego source, not
    the compiled `policy.wasm`, so a different OPA can produce a different module under the same revision.
12. **The values-file digest is pinned but recorded nowhere**: `AdmitRecord` carries the floor and schema digests
    only, and `status` prints the same two.
13. **Evidence files and Kafka values are written as non-canonical JSON** while their names, headers and digests use
    canonical JSON; a reader must re-canonicalize to check a digest, and an evidence file's own SHA-256 will
    generally not equal its name.
14. **The seal marker's reason is the Rust Debug form** of `EndReason` (`Submitted`), not the serde form every other
    surface uses (`submitted`).
15. **The rehearsal's thresholds file and the floor's `lineage` block disagree in shape**: the floor has `beta` and
    no byte thresholds or granularity; `slm/lineage/thresholds.example.json` has `*_bytes` and `granularity` and no
    `beta`; the gate suite hard-codes a third set. ADR-0035 says these are policy-floor values.
16. **`tools/TLAPS-PIN` postdates G9** and is measured by no manifest; its full digest is owed (the file says so).
17. **`tools/cut-manifest.sh` uses `git ls-files -co`**, which sweeps untracked, non-ignored files into a cut.
    Today that would include the untracked `derived/topak-assessment-2026.10.03.md` and this document.
18. **Two 09.28 results files print a different TLC build** (`TLC2 2026.09.25.163503 rev 8f4bc8b`) from the
    tracked jar (TLC 2.19, rev 5a47802). Frozen; worth a line in the next checkpoint's conventions.

**Code**

19. **`scripts/smoke.py` would crash** at its grant line on `g['note']`: the `grant` reply has no `note` key. The
    live smoke run has not been repeated since 2026.09.25 (G9 item 52), which is consistent.
20. **One failing bundle file in `bundles_dir` stops the node from starting**; `load_dir` returns an error rather
    than skipping the file. Its error messages slice `[..16]` of the key and revision strings, which would panic on
    a short string.
21. **`Action::control_plane()`** in `action.rs` is defined and never called; `Admitted` is the summary in use.
22. **The node's default `election_timeout_ms` is 400 and the Paxos crate's is 300.** The node's wins; the crate's
    default is reachable only from its tests.
23. **`Erase` exists in schema S, the floor (`X2`, `F`) and the gates, and nowhere else**: no lift path, no entry, and
    `Rules.erasure_roster` is never read (G11). Three S attributes are read by no policy (`Lease.rulesEpoch`,
    `Tool.digest`, `VoteCtx.epoch`).
24. **A Run tool's channel is declared twice**, in the node's `wasm_tools` config and in bundle `data.json`, and not
    checked to agree; `kind` is recorded, not enforced (G9 item 84, carried here for completeness).
25. **`mechanism-trace-run.sh` leaves `Trace_*.tla` behind**: 229 untracked files sit in `spec/`, some extending the
    older `Mechanism` and most `ConfinementRefinement`. They are gitignored and harmless, and they make
    `spec/` misleading to list.

**Rehearsal**

26. **`slm/serve/profile-host-rung0.json` names a launch command `serve.py --occupant`** and `serve.py` defines no
    such flag; the profile describes the channel as "agent socket via `topak mcp`, JSON lines" while the server
    speaks MCP over stdio. The declared profile does not describe the process it declares.
27. **Three rehearsal results files carry defects**: `e3-overlap-results-2026.09.25.txt` includes xtrace lines
    exposing a scratchpad path; `independence-results-2026.09.25.txt` prints `?` where record digests belong;
    `gate-suite-results-2026.09.25.txt` has a host line broken across lines. All are frozen and cited by digest.
28. **`spec/inventory.py` takes a deployment declaration file and none exists in the repository**, not even an
    example. The format is documented only in the script's docstring.

**Structural**

29. **There is no promotion log entry and no `promote` operator op.** Promotion happens inside `apply` when a `Vote`
    or `Heartbeat` admit completes the tally, so the record of a promotion is the admit that caused it plus
    `Candidate.promoted_at` in state. ADR-0024 §8 places the authoritative vote in the consensus log, which this
    satisfies; it leaves the *promotion* as a derived fact rather than an entry, which the archive and F3 should
    say.
30. **Nothing records `T_irrev`, `W`, `L` or `D`**, in a record's values, the values file or the reference. The
    budget is a form (ADR-0032 §4), and the residual-risk statement of 2026.10.03 says a deployment writes the
    numbers; there is no field for them to be written into.
