# Admit-path reference mechanism: gaps and assumptions

**2026.09.24** · initial design · **not a corpus record** · state of record is G2 · narrative is ToO rev 6

This file lists what the Rust baseline in `mechanism/` had to decide that the corpus does not
decide. Each item is also marked in the code as `PROVISIONAL (<tag>)`, so
`grep -rn PROVISIONAL crates/` and this file should stay in step. Nothing here ratifies or
amends a record. Where the build turned up something about the corpus itself, it is listed
under **Findings** (§4) as a candidate for the next checkpoint.

---

## 1. What this baseline is

| | |
|---|---|
| **Scope** | The admit path of the verified object: epoch fence → lease → lift → policy floor → bundle → consensus-ordered admit → effect. Build's six actions and Run's three (ADR-0040 §1, Proposed) |
| **Stack** | `cedar-policy` 4.13 (floor, linked) · OPA sidecar with in-process OPA WASM fallback (bundle tier) · sans-IO crash-fault Multi-Paxos (`topak-paxos`) · `rskafka` 0.6 (round topics) · `rmcp` 3.4 (agent front door and downstream tools) |
| **Not in scope** | Observer and correlator · archive and plaintext store (ADR-0004) · write-time masking (ADR-0003) · anchor ceremony and bootstrap · confinement · erasure execution |
| **Evidence** | At commit `4fd9677` (2026.09.24): 38 tests — 21 core mutation tests (Lease, FloorComposition, RulesFloorNV_rev5 restated), 4 Paxos simulation tests, 4 floor tests (includes a replay of the 38-case gate suite), 6 bundle-fallback tests, 3 end-to-end cluster tests — plus a live smoke run: 3 processes over TCP, real Kafka, a real OPA sidecar, and an MCP client over stdio. At commit `453801c` (2026.09.25, manifest `dcad5e8e3236cbc7`): 44 tests, the run ADR-0033 §7's addendum and `mechanism/README.md` cite; the smoke run was not repeated |

### 1.1 Records it builds on, by status

The baseline implements some records that are **not ratified**. Code that rests on them is
provisional twice over.

| Record | Status (G2 + later) | What the baseline takes from it |
|---|---|---|
| ADR-0030 floor on a verified evaluator, monotone composition | Accepted (genesis), Batch 6 · **confirmation required (C1)** | Cedar floor, `admit ⟺ floor_permit ∧ ¬bundle_deny`, error-as-deny, the linked floor, S enforced per request |
| ADR-0031 lease schema | Accepted (genesis), Batch 5 · **confirmation required (C1)** | Twelve lease fields, one live lease, monotone renewal with the bundle fixed, targeted revocation and the epoch fence |
| ADR-0003 A1, A2 | Accepted (genesis), Batch 5 · A2 **confirmation required (C1)** | Chain id in topic names (I17); the round's `after` companion for denials after the seal (I23) |
| ADR-0005 Kafka is transport only | **Proposed** | Kafka carries emissions after commit; order comes from the log |
| ADR-0015 effects are boundary crossings | Accepted · **confirmation required (C2)** | Every effect has an `Admit` predecessor in the log; denials are not ordered |
| ADR-0013, ADR-0028 exceptions and forensic floor | Accepted · **confirmation required (C1)** | X1/X2 and F1–F6 as floor entries (via the draft floor); `break_glass` flag on F5 admits |
| ADR-0022 §6 confinement | **Proposed** (the rest is Accepted) | Nothing is enforced; every lease is rung 0 |
| ADR-0024, 0025, 0026, 0027, 0032 | Accepted (genesis) | Tally, `Authentic`, rules floor, resident rules, clock model |
| `floor/genesis-floor.cedar`, `genesis.cedarschema` | **DRAFT**, not ratified | Linked verbatim and pinned by digest |

---

## 2. Assumptions: decisions the baseline made

Each one is a choice among defensible options, taken so the code could exist. **Change** says
what would replace it.

| ID | Assumption | Where | Why this way | Change |
|---|---|---|---|---|
| **I1** | **Crash-fault Multi-Paxos**, not Byzantine. Replicas are in the TCB; agents never speak Paxos | `topak-paxos` | The Byzantine premise (ADR-0007) is about agents. BFT consensus would be a large expansion in scope | A record on the replica fault model |
| **I2** | **Fallback is an engine fallback.** The local WASM decides only if it holds exactly the lease's `bundle` revision; a reachable sidecar's deny is authoritative; a sidecar serving another revision is treated like an unreachable one | `topak-bundle` | Otherwise a sidecar outage lifts post-build narrowings (ADR-0030 §9 finding 3) | **Settled 2026.09.25**: ADR-0030 §1 names it (R4) |
| **I3** | **Bundle identity = content revision**: SHA-256 over sorted (path, bytes) of non-test `.rego` and `data.json`, stamped as the OPA `--revision` | `scripts/build-bundle.sh` | Sidecar provenance and the local tarball must name the same thing | Signed-bundle identity (G7) |
| **I4** | **Renewal keeps the bundle identical.** Bundle changes take effect at the next grant; an urgent one fences the epoch | `lease.rs` `check_renewal` | ADR-0031 §4 allowed "narrow the bundle", but nothing orders Rego bundles (Finding 2) | **Settled 2026.09.25** by ADR-0031 R2, which adopts this rule |
| **I5** | **Epoch is global**, as in `spec/Lease.tla`. ~~Any revocation fences every lease and ends every live round~~ The epoch fence ends every live round; a targeted revocation (`Entry::Revoke`) ends only the leases its target matches, bars later grants through the revocation set, and lapses the seat's break-glass approvals | `state.rs` `EpochIncrement`, `apply_revoke` | **Settled 2026.09.25** by ADR-0031 R3 (Finding 5) | — |
| **I6** | **Rules-epoch fence.** An issuance ends every live lease; a lease granted under superseded rules is refused | `state.rs` `check_live`, `Issue` | Same shape as ADR-0024 §3 for votes; fail-closed | ADR-0031 saying what `rulesEpoch` is "compared" against |
| **I7** | **`Authentic` = Ed25519, and every current anchor key signs** (A-0025 strict unanimity). Domain-separated signing bytes | `authentic.rs`, `rules.rs` | ADR-0025 leaves `Authentic` opaque; unanimity is the archetype | A custody declaration per rung |
| **I8** | **Seats, their domains and their kinds are declared in the issued rules**, with one key per seat. R5 compares seat keys with anchor keys. The kind (`thinker`, `observer`, `grant`) bounds the alphabet a grant may issue and is carried into schema S (ADR-0037 §2, §4; 2026.09.29). An observer seat may name its `cell`, the thinker seat it watches; one with none is a correlator (ADR-0038 §1). The veto roster holds both (ADR-0038 §6, ADR-0024 A2 pending). **`W(p)` as a topic read ACL is not realized**: the reference has no per-topic read authorization, so the cell is declared and not enforced | `rules.rs` `SeatDecl`, `state.rs` `apply_grant` | Rosters are issued (ADR-0025 §1a), and R5 needs keys to compare | A record on seat registration: who declares seats, and how the persons behind them are compared (ADR-0037 finding 2) |
| **I9** | **Break-glass**: roster keys sign approvals scoped to (seat, epoch); quorum *k* is issued; approvals lapse at the next epoch. Rules carry `actions` so R7 has a value to bound | `state.rs`, `rules.rs` | ADR-0009/0013 give the model, not the quorum rule or scope | ADR-0009 detail; R8 TTL (G10) |
| **I10** | **Abstention (`Submit(⊥)`) is an `EndRound` entry**, not an admitted action | `proto.rs`, `mechanism.rs` | Nothing crosses the boundary, and the floor has no resource for ⊥ | ADR-0022 clarification |
| **I11** | **`Submit` and `Vote` are terminal**: applying them ends the lease; the author's topic seals | `state.rs` `apply_admit` | ADR-0022 §1: "Terminal for the authoring/voter's round" | — |
| **I12** | **The submitted artifact must equal the workspace digest**, computed by the mechanism (sorted path + bytes). The MCP `submit` tool may omit it | `mechanism.rs` | "Offer the sealed workspace": a syntactic fact | A record on artifact identity (ADR-0024 §7) |
| **I13** | **Tool allowlist digest = SHA-256(binary digest ‖ canonical input schema)**, both re-checked on every call; tools run with a cleared environment in the workspace | `toolhost.rs` | "Allowlisted by name and digest" names no digest | A record on tool identity |
| **I14** | **Session = bearer token** minted at grant by the granting replica, not replicated. It carries (seat, lease, epoch) into every action | `mechanism.rs`, `proto.rs` | ADR-0022 §2 says every action carries epoch and lease; the MCP transport has no identity of its own | Real principal authentication (G5) |
| **I15** | **Local expiry is proposed as `EndRound(Expired)`**, by whichever replica sees it first | `mechanism.rs` `sweep_expired` | Expiry is local (ADR-0032), but lease liveness is replicated state and must agree (Finding 7) | — |
| **I16** | **Round numbers are never reused** per seat | `state.rs` `apply_grant` | A reused round would reopen a sealed topic | — |
| **I17** | **Topics are `topak.<chain>.<domain>.<seat>.e<epoch>.r<round>`**, where chain = genesis-rules digest; one partition each; sealing is a marker record plus the floor's `sealed` attribute | `lift.rs`, `topak-transport` | Kafka has no seal; re-genesis would otherwise collide (Finding 4) | ADR-0003/0021 on naming |
| **I18** | **Gate evidence is recorded from the operator channel** (`GatesPassed`), and `Vote` is refused until it exists and matches | `state.rs` | ADR-0024 §4 requires gates before votes, and no record says who runs them or how evidence is authenticated | G8 |
| **I19** | **`inputsInWorkspace` lift**: every string leaf of the tool inputs must be workspace-relative by syntax | `lift.rs` | Tool schemas do not mark path arguments. Coarse, fail-closed | Path-typed tool schemas |
| **I20** | **Recusal is enforced twice**: floor forbid B7 and the tally's counted seats | floor, `promotion.rs` | Follows the draft floor. **Settled 2026.09.25**: ADR-0030 R4 keeps B7 in the floor; ADR-0022 A1 (Batch 6) amends §7's path | — |
| **I27** | **Observer liveness (ADR-0039)**: a heartbeat is `{"heartbeat": {"topic", "watermark"}}` and nothing else, carried verbatim into the log as `Admitted::Heartbeat`; `marks` (observer → topic → watermark) and `seals` (thinker → last topic and its final sequence) are replicated state; `heard(o)` is per replica on its own clock, like lease expiry, so `T_obs` is checked at decide and conditions 1 and 3 at apply; `live(o)` uses the strict form `seq − mark < K`; the floor's R3 is scoped to Thinker seats; the values file is compiled in beside the floor and pinned (`topak-floor` `PINNED_VALUES_SHA256`), and `K < R` is refused at startup for both domains; `run_round_bound` is Run's `R` | `observer.rs`, `state.rs`, `lift.rs`, `topak-floor` `lib.rs`, `mechanism.rs` | ADR-0039 §1, §2 (Proposed); the values are placeholders | A scripted cell Observer beside the rehearsal; the gate-side `K < R` check; `T_obs` and `K` from measurement |
| **I21** | **Mechanism parameters** (corpus set, allowlists, round bound, lease margin) ship as config, must match on every replica, and their digest is in every admit; `apply` rejects an admit decided under other parameters | `state.rs` `Params` | ADR-0022 §3 names the parameters, not their delivery | Parameters inside the mechanism release |
| **I22** | **Deny reasons are returned to the agent** | `mechanism.rs` | Debuggability; the floor text is not secret | Reason categories only, if disclosure matters |
| **I23** | **Denials after the seal go to the round's `after` companion** (`…r<round>.after`), up to `after_topic_limit` records, then one `overflow` marker, then nothing. An attempt with no session goes to the `security` log target | `mechanism.rs` `record_denial`, `act`; `Params` | ADR-0020 wants the attempt; ADR-0003 0003.2 forbids reopening the sealed topic. ADR-0003 A2, ratified in Batch 5 | The bound is counted per replica, not replicated |
| **I24** | **Renewal keeps the confinement rung.** A renewal that changes the rung either way is refused | `lease.rs` `check_renewal` | ADR-0031 §4 allowed lowering the rung, which ADR-0034 §3.4 forbids at grant (a silent downgrade) | **Settled 2026.09.28** by ADR-0031 A1 (Batch 10); `Lease_A1.tla` `M_LOWER` |
| **I28** | **In Run the sequence counts effect-bearing admits.** `Actuate` and `Report` advance `seq`; `Consult` advances `actions` only, so it counts toward the round bound and not toward the watermark. The field was `emit_seq`; in Build it still counts emissions only. The apply-time re-check of `live(o)` covers `Actuate` and `Report` and not `Consult` | `state.rs` `apply_admit`, `LeaseRecord`; `types.rs` `is_run_effect` | ADR-0042 §2, ADR-0041 §2 (both Proposed). Before 2026.09.29 only emissions counted, which is D-0042-1 and `RunCoupling.tla`'s `M_EMITSEQ` | Ratification of ADR-0042, and the ADR-0039 §1 amendment it carries |
| **I29** | **Every admitted `Actuate` leaves a record on the round topic**, written by the deciding replica when the call returns: kind `actuate`, the admit's log index, the sequence number, and a payload of `actuate` (tool, `breakGlass`, inputs digest, `outcome`, result digest) and `body` (the inputs and the result). The record's digest is over `actuate`. Calls in flight are held in a registry keyed by round topic; when the round seals, each is written as `unknown`, in sequence order, ahead of the seal marker | `mechanism.rs` `effect`, `apply_committed`, `InFlight`; `topak-transport` `RecordKind::Actuate` | ADR-0042 §3 (Proposed). **The registry is per replica and not replicated**: a replica that fails with a call in flight leaves an admit with no record, which is ADR-0042 finding 2 | A rule for the missing record after a replica failure |
| **I30** | **A result that arrives after the seal is withheld from the principal.** The response says `outcome: unknown` and carries no result | `mechanism.rs` `effect` | ADR-0042 §4: what the principal receives is what the record's digest names, and an `unknown` record names nothing. **The record does not say this**; it follows from §3 and §4 together | A sentence in ADR-0042 §3 or §4 |
| **I31** | **A Run seat cannot abstain.** Refused at `act`, before proposing, and again at `apply`, where an `EndRound(Abstained)` naming a Run seat is `Rejected`. Build's abstain is unchanged | `mechanism.rs` `act`; `state.rs` `apply` | ADR-0042 §5 (Proposed), and its finding 3: the node's handler did not check the domain | — |
| **I32** | **One content-addressed store, two pinned sets.** `Consult` is served from the same directory as `Read`; what differs is the set the floor checks membership in, `Params::run_root` for Run and `Params::corpus` for Build. An object in one set is not thereby in the other | `state.rs` `Params`; `lift.rs`; `mechanism.rs` `effect` | ADR-0040 §3 says the Run root is a pinned set and not where its objects live | A record on what may enter either root, and who admits it (ADR-0041, open obligations) |
| **I33** | **A Run tool's entry declares a channel, and the bundle refuses one that does not.** `policies/data.json` carries `channel: {kind, target}`, two non-empty strings; `actuate.rego` checks presence and shape and interprets neither. The Build check is `tool_invocation.rego`; both read `tool_schema.rego` | `policies/` | ADR-0040 §3 requires a declared channel and lists the entry's schema as an open obligation. **This schema is invented here** | A record that writes the allowlist entry's schema. See G19 |

---

## 3. Gaps: what the corpus does not supply, and what stands in for it

| ID | Gap | Stand-in in the baseline | Consequence |
|---|---|---|---|
| **G1** | **Confinement (ADR-0022 §6, the sandbox gap)** | Nothing. Every lease is rung 0 and `is_contained()` is false by construction | Every principal is `Mediated`. An agent with a shell bypasses the MCP front door entirely. **The largest gap, and code cannot close it; only a sandbox can.** The design half is ADR-0034 (ratified 2026.09.28); the smallest mechanism step is its rung-1 launcher, which the reference does not have |
| **G2** | **Provenance independence criterion** (ADR-0031 §3; a conjunct of `Contained` by ADR-0034 §4) | `PROVENANCE_CRITERION_DEFINED = false` | Even rung 3 would not be `Contained`. ADR-0035 writes the criterion and is Proposed; once it is in force the constant becomes a check of the issued rules |
| **G3** | **Run's alphabet** | `Consult`, `Actuate`, `Report`, as ADR-0040 §1 names them, in the draft floor, the bundle and the MCP surface. **ADR-0040 to ADR-0043 are Proposed, not ratified.** `RunInvoke` and `RunEmit` are retired: a request naming either fails validation against S | The Run half follows records the custodian has not ratified. A change to them in ratification is a change here (the pins say when) |
| **G4** | **Tool hermeticity** (ADR-0022 §3, A2) | Binary + schema pinning, cleared env, workspace as working directory | A tool with a socket collapses the envelope and nothing notices |
| **G5** | **Authentication**: principals, operators, replicas | Bearer token (principals); socket file mode 0600 (operator); none (replica TCP) | Anyone who can reach a socket can act. Replica traffic needs mTLS |
| **G6** | **Genesis rules and the bootstrap spec** | `dev/rules.json` from `scripts/dev-init.sh` (3 anchor keys, 3 grant seats, 1 veto seat), checked by the rules floor at startup, which is a runtime `GenesisSatisfiesFloor` | **Dev rules are not genesis rules.** Secrets are in `dev/secrets/` in the clear |
| **G7** | **Bundle signing** (ADR-0030 §2 "signed") | None; revision read from the manifest; file name must match | A swapped tarball with a forged manifest would be trusted |
| **G8** | **Who runs the ADR-0007 gates, and how their evidence is attested** | Operator records `(artifact, evidence)` | Gate evidence is asserted |
| **G9** | **Archive and plaintext store** (ADR-0004); forensic horizon | `archive.jsonl` per replica, a projection of the log rebuilt on restart; payloads (drafts, emissions) live only on the deciding replica and in Kafka | No governed store, no horizon, no audit-authority read path. Workspaces are not replicated, so a Submit is checkable only where its drafts were written |
| **G10** | **R8 break-glass TTL** | Approvals lapse at the next epoch increment | Break-glass is time-unbounded within an epoch. ADR-0032 says a TTL needs trusted time |
| **G11** | **Erasure** (ADR-0006) | Not implemented; no erasure roster exists at genesis, so X2 admits nothing | Matches the corpus position; nothing to exercise |
| **G12** | **Observer, quarantine gate, correlator** | None. Veto seats are ordinary seats voting through MCP | Deny-only findings have no producer |
| **G13** | **Persona attestation** (ADR-0016 §6) | `persona` is an operator-supplied digest | Silent substitution is undetected |
| **G14** | **Log compaction and snapshots** | None: the log, `chosen` map, dedupe set and WAL grow without bound | Fine for a baseline, not for a service |
| **G15** | **Vector clock / per-principal ordering** (ADR-0005) | `topak-seq` header: per-lease emission sequence number, plus the admit's log index | Covers the ADR-0015 residual as that record suggests; nothing more |
| **G16** | **Floor fitness** (MEASURE 2.13) | None | The floor is well-formed and non-vacuous; nothing says it is the right floor |
| **G17** | **Re-genesis migration** | Chain id in topic names only | No inherited forensic read access |
| **G18** | **ADR-0024 A2.2, an independent veto seat leased for the round** | Nothing. The tally checks coverage (A2.3) and not independence, because no independence table exists in the reference (ADR-0035 §4 is unbuilt) | A promotion completes with a correlated veto seat; the independence half of the veto-seat-outage discharge is declared and not enforced |
| **G19** | **Channel fidelity, and the allowlist entry's schema** (ADR-0040 §3; ADR-0042 §6) | A declared `channel` in bundle data, checked for presence and shape (I33). The tool host pins a Run tool's binary and schema as it does a Build tool's, and nothing more | **A Run tool that opens a channel it did not declare is not seen by anything.** The declaration is an operator's assertion, as a rung-0 profile is |

---

## 4. Findings: what building it showed about the corpus

These are observations for the next checkpoint. Findings 1, 2, 4, 5, 6, 10 and 11 have been acted on,
finding 4 through ADR-0003 A1 (ratified in Batch 5). Findings 3, 7 and 8 closed with ADR-0015 E1 and
ADR-0031 E1 (Batch 8); finding 8 still owes a model in the bootstrap `Promotion` module. Finding 9 remains.
Findings 12 to 14 are from 2026.09.29, carrying ADR-0040 to ADR-0043 (all Proposed) into the reference.

1. **The gate suite has a case that does not test what it names.** `floor/genesis-tests.json`,
   "B6 vote from an unseated principal", votes **grant**, so forbid B8 fires and is the reason for
   the deny. B6's roster conjunct is never isolated. The decision matches, so `cedar run-tests`
   passes; the linked engine reports the reason, so the replay test caught it. The fix is a
   **deny** vote from `n1`. **Fixed 2026.09.24** in `gen-tests.py`; the replay test no longer
   allows a divergence.
2. **ADR-0031 §4 "a renewal may … narrow the bundle" names an order that does not exist.**
   ADR-0030 removes the need to compare a bundle with the floor, but nothing compares two bundles.
   The baseline fails closed (I4). **Resolved 2026.09.25** by ADR-0031 R2: renewal keeps the
   bundle, and a new bundle reaches a live principal only at its next grant.
3. **Ordering and authorization are different properties, and the corpus uses them as one.**
   Revocation, abstention and expiry need no quorum (ADR-0031 §5), but they change replicated
   state (lease liveness, the epoch), so they must be consensus-*ordered* or replicas disagree.
   The baseline logs them as unauthorized subtractions. ADR-0015's "denials are not ordered" still
   holds: these are not denials, they are state changes.
4. **Re-genesis reuses topic names.** A successor chain starts at epoch 0, round 1 again. This
   was shown live: two dev resets wrote into the same Kafka topic. Fixed in the baseline by a
   chain id (I17). It belongs with the re-genesis migration obligation (G2 §7 item 10).
5. **With a global epoch, one revocation ends every live round**, not just the revoked
   principal's. ADR-0031 lists "a revocation storm is an availability event"; the sharper
   statement is that *a single* revocation is a system-wide round reset. `Lease.tla` models one
   global epoch, so the checked property does not distinguish the two. **Resolved 2026.09.25**
   by ADR-0031 R3: a targeted revocation ends one principal's lease, and the epoch fence is
   kept for the fleet. `Lease.tla` gains `RevokeLease`, a selective witness and `M_REVOKE`.
6. **"Round-coterminous" needs the round in the credential.** ADR-0031 grants a lease "for a
   round", but `round` is not among the ten fields. The baseline carries it beside the lease
   (`Assignment`). Either the field list is not closed, or the grant record is part of the
   credential. The same holds for the round *role*, which the floor keys on (ADR-0022 §7).
   **Resolved 2026.09.25** by ADR-0031 R1: `round` and `role` are lease fields, fixed across
   renewal. `Assignment` is folded into `Lease`, and `Lease.tla` gains `M_ROLE`.
7. **Local expiry cannot free the one-live-lease slot by itself.** If each replica judged
   liveness by its own clock, a later `Grant` would apply on some replicas and not others. Expiry
   is decided locally and then *ordered* (I15), which is Finding 3 again.
8. **The admit decision and its commit are separated by time, so the mechanism checks run
   twice.** An admit decided under epoch *e* can commit after a revocation to *e*+1. The
   baseline re-runs the fence and lease checks at apply and voids a stale admit. This is the
   implementation of "rejected by the mechanism, not by policy" (ADR-0022 §2) across the
   consensus gap. The bootstrap `Promotion` module will need the same two-step shape.
9. **A Paxos host that retries lost proposals must not also re-queue them on step-down.** The
   first implementation re-queued in-flight values when a leader lost its ballot. Values
   inherited through phase 1 were then proposed twice per leadership change, and the backlog
   doubled every term (a million slots in the simulation). The fix is host-level retry under an
   idempotent entry id. This is an implementation lesson, but the `Paxos` TLA+ module the ToO
   calls for should model proposer retry, because that is where it goes wrong.
10. **Floor denials carry reasons only from forbids.** A deny because no permit matched has an
    empty reason list, so "why was this denied?" has no answer for most denials. ADR-0030 §5 gate
    evidence is unaffected. For the Observer and for operators it is a legibility gap.
    **Resolved 2026.09.25** by ADR-0030 R4: a deny with no determining forbid is reported as
    `FloorNoPermit` (`admit.rs` `floor_gate`); the engine's own reasons are unchanged, so the
    replay against the gate suite still compares like with like.
11. **Denials never reach the round topic.** Found 2026.09.25 in review, not by the build.
    ADR-0020 (Accepted) makes "actions attempted, including those denied" part of the replayable
    record, and says it is the clause an implementer is most likely to drop. The baseline dropped
    it: a denial goes only to a `tracing` line on the deciding replica (`mechanism.rs`), so replay
    and the Observer see a clean system. ADR-0033 §2's "written only after commit" forbids the fix
    as written, since a denial is never committed. **Resolved in part 2026.09.25** (ADR-0033
    R8): a denial under an open round is written to its topic as a `deny` record, with no admit
    and no sequence, content by digest. **Resolved 2026.09.25** for the sealed case by ADR-0003
    A2 (ratified in Batch 5): the round's `after` companion, bounded (I23). An attempt with no session goes to
    the replica's security log.

12. **ADR-0041 §7 names the wrong gate for its negative control.** Found 2026.09.29, building the
    floor. The record says `R4` with its Run-root condition removed "is caught by the non-vacuity
    gate on `Consult`". It is not: the domain and alphabet conjuncts still refuse requests, so
    `always-allows` stays refuted and the gate passes. What catches it is routing, which classes
    the candidate a relaxation (`F ⇒ F′` holds, `F′ ⇒ F` is refuted). The gate run carries that
    control, and a permit-all on `Consult` for non-vacuity. ADR-0041 is Proposed, so the fix is a
    revision in place; it is the custodian's to make.
13. **`Coupling.tla` and the reference counted different things**, which ADR-0042 finding 1
    records. It is restated here because the register's §6 listed `UnreadBounded` against an e2e
    test that reports and never invokes: the restatement was faithful to the model and the model
    was not the mechanism. `RunCoupling.tla` separates the counters; `M_EMITSEQ` is the old
    behaviour.
14. **The bundle tier cannot hold a Run tool to its channel.** `actuate.rego` refuses a tool that
    declares none (I33), and that is all a request-time policy can do: whether the tool opens
    that channel is a fact about the tool, not the request. It is G19, and ADR-0042 §6 says it
    has no owner.

---

## 5. Assumptions of use (ToO §13), as the baseline stands

| # | Assumption | Baseline |
|---|---|---|
| A1 | Effect exclusivity enforced by a mechanism | **Not met** (G1). Every principal is `Mediated` |
| A2 | Every allowlisted tool is hermetic | **Not checked** (G4). Identity pinned; behaviour not |
| A3 | Anchor key-holders honest at the capture threshold | Assumed; `Authentic` is strict unanimity (I7) |
| A4 | Grant seats review independently | Not addressed |
| A5 | A trained human present for break-glass and quarantine | Not addressed; break-glass approvals are signatures from the operator channel |
| A6 | The clock model holds | **Implemented as ADR-0032 states it**: local monotonic, asymmetric margin, expiry early; no decision reads a principal's clock; safety is carried by the fence |
| A7 | Degeneracies declared | The baseline declares none; it runs the archetype values (quorum all, minGrant 2, unanimity custody) |
| A8 | Confirmation-required records cited as author-ratified | This file does so in §1.1 |

---

## 6. TLA+ properties and the tests that restate them

| Artifact | Property / mutation | Rust test |
|---|---|---|
| `Lease.tla` | `LeaseAuthorityMonotone` / `M_RENEW` | `mutations.rs` `lease_renewal_is_monotone_and_m_renew_is_refused` |
| `Lease.tla` | C1 one live lease | `one_live_lease_per_principal` |
| `Lease.tla` | `NoActionUnderFencedEpoch` / `M_FENCE` | `no_action_under_a_fenced_epoch_and_m_fence_is_refused`; e2e `FencedEpoch` |
| `Lease.tla` | `Rung0NeverContained` / `M_RUNG` | `rung_zero_is_never_contained_and_nothing_is_contained_yet` |
| `Lease.tla` | `LeaseAuthorityMonotone` / `M_ROLE` (ADR-0031 R1) | `renewal_cannot_change_round_or_role_and_m_role_is_refused` |
| `Lease.tla` | `NeverSelectiveRevoke` witness (ADR-0031 R3) | `a_targeted_revocation_ends_one_round_and_not_the_fleet`; e2e targeted revocation leaves a bystander live |
| `Lease.tla` | `RevokedStaysStopped` / `M_REVOKE` (ADR-0031 R3) | `a_revoked_principal_persona_or_profile_is_not_granted_again_and_m_revoke_is_refused` |
| `Seats.tla` | `OnlyThinkersAuthor` / `M_KIND` (ADR-0037 §4) | `alphabets_are_bounded_by_seat_kind_and_m_kind_is_refused`; `floor.rs` replays B10 and the tightened B6 (47 cases); e2e: the author's voter grant is refused |
| `Seats.tla` | `OneSeatPerPrincipal` / `M_SEAT` (ADR-0037 §1; finding 1: the reference's behavior before 2026.09.29) | `one_seat_per_principal_and_m_seat_is_refused` |
| `Observers.tla` | `DenyByAnyOf` / `M_QUORUM` (ADR-0038 §5) | `a_correlator_on_the_veto_roster_vetoes_and_its_silence_does_not` (the tally is any-of over the veto roster); e2e: two veto seats silent, promotion completes |
| `Observers.tla` | `ReachIsBounded` / `M_REACH` (ADR-0038 §1) | `a_cell_names_a_thinker_seat_in_its_domain_and_only_observers_have_one` (declared reach); **not enforced**: no topic read ACL (I8) |
| `Coupling.tla` | `NoAdmitWithoutLiveObserver` / `M_NOCOUPLE` (ADR-0039 §2) | e2e `observer_liveness_couples_run_admits`: refused with no Observer lease, no heartbeat, and after `T_obs` (floor R3); `floor.rs` replays R3 |
| `Coupling.tla` | `UnreadBounded` / `M_MARK`, `M_ROUNDS` (ADR-0039 §2) | same e2e: refused at a backlog of `K`, refused on a fresh heartbeat with an unchanged watermark, refused a round-2 grant while round 1 is unread (`apply_grant`); `State::observer_covers` is the strict form |
| `RunCoupling.tla` | `UnreadEffectsBounded` / `M_EMITSEQ` (ADR-0042 §2; **the reference's behaviour before 2026.09.29**, D-0042-1) | `mutations.rs` `the_sequence_counts_effects_and_m_emitseq_is_refused`; e2e `actuate_is_counted_recorded_and_sealed`: `K` invocations and no report, the next refused by R3 |
| `RunCoupling.tla` | `ConsultNeverCoupled` / `M_COUPLEALL` (ADR-0041 §2) | same two tests: a `Consult` admitted with no heartbeat at all, and again while `Actuate` and `Report` are refused for the backlog; `floor.rs` replays "R3 does not couple Consult" |
| `RunCoupling.tla` | `SealCountsEffects`, and `M_ROUNDS` carried over (ADR-0042 §5) | `a_run_round_seals_with_its_lease_and_a_run_seat_cannot_abstain`: a renewal does not seal, the seal is 3 after three invocations, and the round-2 grant waits on it; e2e: the grant refused with one invocation unread |
| `RunCoupling.tla` | `RoundBoundCountsAll` / `M_BOUNDEFF` (ADR-0042 §2) | `the_round_bound_counts_consult` |
| `RunSeats.tla` | `OnlyThinkersActuate`, `ObserversConsultAndReport` / `M_KIND`; `NoNameCrossesDomains` / `M_DOMAIN` (ADR-0043 §2; ADR-0040 §2) | `run_alphabets_are_bounded_by_seat_kind_and_domain`; `floor.rs` replays B10 over `Actuate` and R4 for an observer seat |
| ADR-0042 §3, §4 | the `Actuate` record; `unknown` ahead of the seal; the late result withheld | e2e `actuate_is_counted_recorded_and_sealed`. **Not modeled in TLA+**: `RunCoupling.tla` assumes a record at every sequence number |
| ADR-0040 §1, ADR-0041 §4 | a retired name is an error, and an error is a deny | `floor.rs` `a_retired_run_action_is_an_error_not_a_decision` |
| `Coupling.tla` | `CorrelatorNeverGates` / `M_CORR` (ADR-0039 §4) | `Rules::cell_observers` excludes correlators from `live(o)`; e2e: the correlator is never granted a Run lease and Run admits proceed |
| ADR-0039 §3 (ADR-0024 A2.3) | coverage to the seal completes a promotion | e2e `build_round_promotion_and_fencing`: every grant seat granted, `Tally::Stalled` until `o1` heartbeats `a1`'s seal |
| `FloorComposition.tla` | `AdmitImpliesFloorPermit` / `M_OVERRIDE` | `admit_implies_floor_permit_and_m_override_is_refused`; e2e allow-all bundle still floor-bounded |
| `FloorComposition.tla` | `FloorErrorIsDeny` / `M_ERR` | same test; `floor.rs` `an_incomplete_slice_is_a_deny_not_a_skipped_forbid` |
| `FloorComposition.tla` | `BundleRefusalHonored` / `M_FAILOPEN` | `bundle_refusal_is_honored…`; `fallback.rs` (6 cases) |
| `FloorComposition.tla` | narrowing witness | e2e: `Invoke` floor-permitted, bundle-refused |
| `RulesFloorNV_rev5.tla` | each entry's mutation fails | `every_rules_floor_entry_has_a_violation_it_catches`; e2e issuance rejections (R1+R9, R2, Authentic) |
| `RulesFloorNV.tla` | dropping R2 promotes with zero votes | `without_r2_an_empty_roster_promotes_with_zero_votes` |
| G2 §3 | a threshold needs ≥ 3 counted seats | `a_threshold_needs_three_counted_seats_to_differ_from_unanimity` |
| ADR-0024 | recusal, timeout ≠ grant, stale votes, veto | four `tally` tests; e2e promotion |
| `Voting` (cheat sheet) | `OneValuePerBallot`, chosen-unique, agreement | `topak-paxos/tests/sim.rs`, both mutations caught |

**What these are:** the same kind of evidence the TLA+ runs are, restated against running code,
written by the same hand. They are discrimination tests, not proofs.
