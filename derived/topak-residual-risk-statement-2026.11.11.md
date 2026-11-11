# TOPAK — Residual-risk statement

**2026.11.11** · derived · **the statement NIST AI RMF MANAGE 1.4 asks for**, written for an acquirer or a user of the
pattern, not for its author · against Genesis Checkpoint G11 (2026.10.09), Theory of Operation revision 15, ADR-0045
Annex A and Annex B as ratified through Batch 39, `spec/theorem-premise-binding.md` and
`mechanism/GAPS-AND-ASSUMPTIONS.md`, all at commit `bbda621`, and the critical review of the same date
(`topak-critical-review-2026.11.11.md`, CR-40 to CR-61) with its register · one of five documents of the self review
of 2026.11.11 · prepared by the assistant at the custodian's request · **supersedes
`topak-residual-risk-statement-2026.10.09.md`** as the current statement

**What this is.** One document that says what is left when TOPAK's guarantees are read against what has been
built, declared and reviewed. It is in two parts, because the tree is. **Part I** is what is in force: G11 and the
two batches ratified after it. **Part II** is what would be left if the eighteen Proposed records were in force,
and most of it is the command-chain overlay's own statement of its residuals, with the places where this review
found that statement short. Nothing in Part II is a residual of anything that exists: no Proposed record is in
force, and nothing of the overlay is built.

**How it was made, and what it carries.** The 10.09 statement stands for the argument of each residual it named;
this one states each in a few lines, says what has moved, and adds what the review found. The tables of §2 to §5
are the 10.09 statement's, carried whole, with what has moved in them listed beneath each. Every change of fact
rests on a check run for the review or on a finding a verifier confirmed, and cites it. It is a derived document
and not a record: nothing here is ratified, and a deployment that adopts it writes its own numbers into §5 and
§9.

**It is the author's statement about the author's work**, and so was the review it draws on (§1.5).

**Two deployments are described**, as before. The *archetype* is the configuration every theorem is about
(ADR-0045 Annex A), and nobody runs it. The *reference* is the configuration ADR-0033 cites (Annex B), and it is
the only one that runs.

---

## 0. In one paragraph

TOPAK's guarantees are theorems about a mechanism. Under the records in force they are proved of twenty-four TLA+
proof modules (5,416 obligations, every one proved; twenty-one certified; fifteen proved again in Lean of
re-encodings) and checked at small constants, under premises that name every component the mechanism trusts.
**At the reference today every theorem about confinement, gate evidence, tool hermeticity and effect-channel
fidelity is void**, because the components those theorems rest on are absent, simulated or excluded: no real
principal is `Contained`, every principal is `Mediated`, and the claim that an agent's effects are exactly its
admitted actions is an assumption. **What holds at the reference** is the control-plane half: a lease is the only
credential, authority changes only by promotion or anchor issuance, every admitted effect is ordered and
recorded, denials are recorded, revocation and expiry subtract without a quorum, absence of detection stalls and
does not admit, an emergency call cannot be blocked by an Observer, and the rules floor bounds what the anchor
may issue. Those hold of the modules, and of the code on the paths a test takes; replayed for this review, 82 of
the 83 recorded traces follow the operational model and one, the workflow test's, does not. **The prover that
proved them can prove false statements in two known ways**, now reported to its maintainers and unfixed in the
build in use. **Nothing has been reviewed by anyone but its author**, this statement included. The numbers the
mechanism runs on are placeholders. **Since the last statement the state of record has fallen behind the tree**:
two ratified batches, thirteen Proposed records and 190 files stand outside any checkpoint or manifest, and the
review found that what is in force cannot always be told from the page.

---

# Part I: What is in force

## 1. The headline residuals, in order

The fourteen of the 10.09 statement, in its order, each as it stands at `bbda621`. Its §1.1 to §1.14 carry the
argument at length. "Moved" is against that statement.

| # | Residual | At `bbda621` | Moved since 10.09 |
|---|---|---|---|
| 1.1 | **Anchor capture.** A coalition at the custody threshold can issue any floor-conformant rules. No safety theorem covers anchor intent | Custody at the reference is (1, 0): one person is the coalition. No deployment has declared a threshold | **In one place.** The 10.09 statement said the exception count is "now one (R6)". That is the record. The reference's `rules.rs` still checks R7 over the retired break-glass envelope and keeps two as R6's constant bound (J-2), and no non-vacuity run has ever covered R6 (B-7) |
| 1.2 | **Effect exclusivity is assumed.** No principal is `Contained` | Unchanged: rung 1 trusts the host, rung 3 is SIMULATED, no image passes P3, and the independence criterion is in force nowhere | **One qualification.** `NoSilentDowngrade` is checked and proved with one declared rung per deployment; ADR-0023 §6c, in force, makes the rung per seat, so for the mixed-rung deployment the reference runs it is checked on the reference's recorded traces only, and is neither model-checked nor proved (C-35) |
| 1.3 | **Detection fails open against a colluding Observer** | Unchanged. Nothing at the reference computes a correlation | **One qualification.** `Correlator.tla`'s `FindingHasEvidence` and `HonestNeverCharged` hold because no correlator in the model can report a false finding; ADR-0051 says the mechanism does not check findings (D-6). ADR-0051 is Proposed |
| 1.4 | **The operator is a principal on paper; the first lease still comes from a socket** | Unchanged: D-0050-1 is the reference. Gate evidence is an unsigned assertion | **Stated worse than before.** Seventeen ratification rows say "The reference follows the text"; for the first lease from a quorum, and for several other texts, it does not (B-2, A-5) |
| 1.5 | **Nothing is independently reviewed** | Sixty-seven record files; eighteen Proposed; fifteen amendments pending. Reviewer engaged: none. Review pass: none | **Larger.** Thirteen more records, eight modules and 5,600 proof obligations are one hand's, ten of the records in one day. The review this statement draws on is the drafter's lineage reading its own work, and does not count under ADR-0029 A2.1 |
| 1.6 | **What runs is not what is proved** | Three kinds of evidence connect code to modules, and none is a refinement (T-0045-28) | **Measured.** Trace validation, rerun for the review: 83 traces, 1,053 steps, 82 matching; the end-to-end workflow test does not replay (L-8). The reference tree at this commit is measured by no manifest: two build inputs moved on 2026.11.03 with no addendum (J-1). `mechanism/lean` is still stale |
| 1.7 | **A compromised replica forges admits** | Unchanged: replicas are crash-fault and unauthenticated | No |
| 1.8 | **Prompt injection inside the envelope.** Labels say where bytes may go, as declared | Unchanged: the labels are the word of whoever issued the bundle or the grant | **One qualification.** The narrative presents the label forbids as a bound on what an injection can reach without the confinement condition every principal fails today (K1-10). The root's missing label has no check in the load checks ADR-0047 calls definitive (F-7) |
| 1.9 | **Break-glass is a provisional emergency seating**, and the mechanism cannot tell a person from a program | Provisional, as before | **In three places** (§1.17, §1.18): the one-round rule is not in the floor; the invariant that no agent holds the seat rests on a fact the mechanism cannot see; and the retirement of the old exception was not carried through the records and the reference |
| 1.10 | **Every number is a placeholder, and nothing is measured** | Unchanged | No. Part II lists the numbers the Proposed records would add |
| 1.11 | **The prover is known to be unsound in two ways, and is kept in use** | `tlapm` 7824dab has both cases; a rule, a scan and a reading stand between them and the proofs; no check detects the first | **Reported.** The defects were reported upstream on 2026.10.18 as tlaplus/tlapm#309 and #310 and the report ratified (ADR-0046 A3, ADR-0045 A4; Batch 39). The 10.09 statement's "not reported upstream" is no longer true; the build in use is unchanged. Eight more proof modules were written under the rule and scanned on 2026.11.10 (no collision, no capture); the custodian's reading that Batch 37 gave the first twenty-four is not recorded for them |
| 1.12 | **Legibility residuals** | Unchanged: no archive, erasure unbuilt, replay is boundary events only | No. The 11.05 feature list had marked erasure, retention, replay authorization and masking *Built*; they are not, and the regenerated list corrects it |
| 1.13 | **Workflows and meshes: Proposed, built, and followed on a floor not in force** | Unchanged in standing | **Sharper.** The record, the module and the reference disagree on what a lapsed lease does, what closes an edge on a finding and whether a refused grant fails a node or waits (G-3, G-4, G-5). The properties were checked of one thing and the reference runs another |
| 1.14 | **No stall is shown to end** | Unchanged: four leads-to properties checked, none proved | **One addition.** The `Workflow` and `Mesh` run scripts pass `-deadlock` and are in neither deadlock audit, so for the two modules the reference follows nothing says where a state with no successor may be |

**What the review adds.** Six residuals the 10.09 statement did not have, each from a finding a verifier
confirmed. None shows a theorem false of its module.

### 1.15 The state of record is not the tree

G11 measures a tree seventy-one commits old. Batches 38 and 39 are in force and in no checkpoint, index or
narrative; 190 tracked files are measured by no manifest; the newest reference manifest fails four files at this
commit, two of them unrecorded anywhere (B-6, K1-2, L-4, J-1). **For a user:** the rule "where the checkpoint and a record disagree, the
checkpoint wins" currently makes a frozen sentence outrank a ratified amendment, and nothing but a reading of
History rows says what is in force today. The digests an acquirer would check a copy against stop at 2026.10.09.

### 1.16 A clause in force rests on a record that is not, and is enforced nowhere

ADR-0024 A2.2, part of the bootstrap set's promotion rule, reads an independence table that only ADR-0035 defines.
ADR-0035 is Proposed, and the reference does not follow A2.2 "since no independence table exists" (B-1, C-43).
**For a user:** the promotion rule as ratified is stricter than anything that runs or that any module states with
its two conjuncts (B-8, B-10); a deployment that cites the rule cites a clause nobody has built.

### 1.17 The emergency seat's one-round rule is held by the reference, and not by the floor

"An operator's `Regrant` or `Renew` naming an emergency seat is refused" (ADR-0052 §3). The floor in force does not refuse
either: run for the review, it decides both **allow**. The refusal is an apply-time check in the reference, with a
test, and a property with two mutations in `Emergency.tla` (F-1). `NoAgentHoldsAnEmergencySeat` is proved, of a model whose activation guard reads whether
the holder is a person, which the record says the mechanism cannot know (F-2). **For a user:** the time box on
break-glass is as strong as the mechanism that implements it. A deployment that builds its own mechanism to the
floor and the gates, as the pattern invites, inherits no such refusal from either.

### 1.18 Break-glass was retired as a floor exception, and five places still describe it as one

ADR-0015's exhaustive classification of effects still files break-glass under a floor-exception entry that no
longer exists (A-1); ADR-0043 §2 still says only a `thinker` seat holds `Actuate`, and `OnlyThinkersActuate`,
proved against that clause, no longer states the design in force (D-1); the bootstrap trigger still names the
old module and invariant (B-15, F-26); `RulesFloorBase.tla` and the reference's rules floor still carry the old
R6 and R7 (F-27, J-2). **For a user:** an inventory computed from the binding table reports a theorem as
holding whose clause has been overtaken, and the exhaustiveness claim that earns ADR-0015 its confirmation marking
has a row that is out of date.

### 1.19 Some proved properties say less than they read as saying

`NoSilentDowngrade` (one rung per deployment in the module and its proof), `FindingHasEvidence` and `HonestNeverCharged` (no false finding is
possible in the model), `NoAgentHoldsAnEmergencySeat` (a guard over ghost truth), and R6 (never run for
non-vacuity) are each true of their module and narrower than the sentence that cites them (C-35, D-6, F-2, B-7).
Three modules abstract more than their records list (F-18, F-19, F-20). **For a user:** "proved" in this corpus means
proved of a module under its abstractions. The corpus says so everywhere; these are the places where the list of
abstractions is short.

### 1.20 Four of the corpus's own checkers report success on a failure

The manifest verifier and the trace driver exit 0 when they find a mismatch; the reference checker does not look
under two directories; nothing reports a change to an overlay record or to a TLC results file (L-1, L-2, L-8, L-3).
**For a user:** every check this statement cites was read for its output, not its status. Anyone who automates
them should do the same until they are fixed.

---

## 2. The trusted base, row by row: what stands when each fails

ADR-0045 Annex A's residual column with Annex B's instance, as the 10.09 statement tabulated them. The rows are
unchanged by Batch 39 but for T-0045-31's note. **An excluded or absent row voids every theorem premised on it**
(ADR-0045 §3).

| Row | Component | Class | Residual when it fails as named | At the reference |
|---|---|---|---|---|
| T-0045-1 | The replicas, crash-fault | trust root | A forged admit; the apply-time re-check does not re-run the floor | Three replicas in one process tree, TCP, no authentication |
| T-0045-2 | Ed25519, domain-separated | trust root | Cryptanalysis; key theft is T-0045-8 | Pinned in `Cargo.lock` |
| T-0045-3 | The Cedar engine | trust root | Divergence on inputs outside the conformance corpus; D-0030-1 drops the premise | `cedar-policy` 4.13, linked; totality of the floors proved in Lean under cedar-spec's model (B36) |
| T-0045-4 | The local monotonic clock | delegated | A slow clock stretches `ttl` past `T_persona`; no safety decision reads it | The host's clock; `clock.rs`'s interval proved to fail closed in Lean |
| T-0045-5 | The round-topic transport | delegated | Availability; topic ACLs declared and not enforced | `rskafka` or in-memory; writes topics, reads none (finding 23) |
| T-0045-6 | The bundle-tier engines | delegated | Availability; a divergence lifts a narrowing only within the floor | OPA sidecar; WASM fallback |
| T-0045-7 | The archive and plaintext store | delegated | Evidence lost within the horizon; a failed erasure is the residual the other way | `archive.jsonl` per replica; no horizon, no audit read path |
| T-0045-8 | The anchor key store | trust root | Capture below the custody threshold | `dev/secrets/` in the clear |
| T-0045-9 | The anchor's key-holders | trust root | **Any floor-conformant rules, issued** (§1.1) | One person |
| T-0045-10 | The resident genesis rules | trust root | The chain's root authority wrong from the start; ADR-0029 A2's review is the check | Dev rules, not genesis rules |
| T-0045-11 | The corpus and its custodian | trust root | Every theorem, if the corpus is not what it says; solo authorship until A2's review | This corpus, pinned; custody (1, 0) |
| T-0045-12 | Break-glass approvers | trust root | A grant within the envelope that should not have been made; bounded by R6 and R7, and since ADR-0052 by one round | The operator, signing from the operator channel; no human process |
| T-0045-13 | The gate runner and its evidence | **excluded** | **Every promotion theorem that assumes gates ran is void** | `GatesPassed` from the operator channel, unsigned |
| T-0045-14 | The proof checker behind routing, and behind the certified proofs | trust root | A checker bug or a wrong rule in the signature | `ethos` at `8dc85c4`, CPC signature from cvc5 1.4.0 |
| T-0045-15 | The lineage gate tools | trust root (once ADR-0035 is in force) | An independence pass for a correlated pair; the bound is unreviewed | Not instantiated |
| T-0045-16 | CPU root of trust and firmware | trust root, rung 3 | Side channels and physical access | **None; SIMULATED by a test key** |
| T-0045-17 | The independent verifier | trust root, rung 3 | Its own compromise; replacing it is an issuance | **None; SIMULATED by a test key** |
| T-0045-18 | Host firmware and hypervisor | trust root, rung 2 | Alteration after launch undetected by re-attestation | None; rung 2 is a seam |
| T-0045-19 | The host operator and orchestrator | trust root, rung 1 | **Anything**: every host power is an addition at rung 1 | Whoever runs the node, and the node's launcher with its process or container backend (B29) |
| T-0045-20 | The promoted image, runtime and profile | trust root, rungs 1–3 | A guest that is not what its profile says | The image by digest and its declared profile; every rung-1 profile declares a failure |
| T-0045-21 | Inference attestation | trust root, reserved | Conformance admits on a self-report; no theorem cites it | None |
| T-0045-22 | The host at rung 0 | excluded | Every containment premise void: `Mediated`, always | Every rung-0 seat |
| T-0045-23 | A native tool under `Invoke` | excluded | Hermeticity void for it; its principal `Mediated` | Every Build tool is native |
| T-0045-24 | A Run tool's declared channel | **delegated** to T-0045-25 for a Wasm tool (B30); excluded for a native one | The target is an address and the protocol on it is unchecked; a native Run tool is D-0034-5 or 6 | **Still excluded in Annex B** (G10 item 89): the entry became the only declaration at A9, and Annex B has not been revised to say so |
| T-0045-25 | The tool host | trust root | The envelope collapses if it runs other than the allowlisted binary; it is what holds a Wasm tool to its channel | `toolhost.rs`: cleared environment, digests re-checked per call |
| T-0045-26 | Decoding conformance | trust root at rung 3; excluded below | An admit on a self-reported distribution | None admits |
| T-0045-27 | The bundle signer | trust root | Unbounded within the floor; never above it | A dev key, custody (1, 0), signing as a script step |
| T-0045-28 | The implementation as a refinement | trust root | **Every theorem at once**, on every path no test reaches (§1.6) | Trace harness, stage one, last run 10.05; Lean transcriptions and models as evidence, stale (B36; item 103) |
| T-0045-29 | TLC at the constants run | trust root | A mutation or witness result that does not generalize; TLC's soundness unexamined | `tla2tools.jar` 1.7.4, tracked |
| T-0045-30 | The build toolchain | trust root | An admit the source would refuse, inserted below it; no reproducible build | One developer's toolchain |
| T-0045-31 | The prover and its backends | trust root | A theorem taken as proved that is not; **two known unsound cases in the translation** (A3), kept from by a rule and a scan, the first undetectable by any check | `tlapm` 7824dab, pinned by digest, **has both**; no cited result rests on either, by scan and reading (C2) |
| T-0045-32 | The label computation and delivery (ADR-0047) | trust root | Bytes delivered that the table suppresses; a `clearSet` too small, so a forbid does not fire | Built (I46); the facts are the deciding replica's, re-checked at apply as `clearSet` only |
| T-0045-33 | The label and destination declarations, and the task's label | **excluded** | A source declared trusted that is not is seen by nothing; **every label forbid is conditional on these being right** | Declared in the bundle; the task's label is the operator's, not followed at a first seating |
| T-0045-34 | Handle resolution and the tool list's rendering (ADR-0047, 0048) | trust root | Suppressed bytes reaching the wrong tool; a Thinker told of a tool it may not call | Built; a handle resolves only to a scalar one replica holds in memory |
| T-0045-35 | An operator's identity provider (ADR-0050) | trust root | A forged operator: adds within the envelope, denies anywhere in its domain; bounded by the peer rule only with different providers (D-0050-2) | **None** (D-0050-1) |
| T-0045-36 | An operator's custody of its key | trust root | Whatever that operator may do, done by another; a person and a program with the key are the same to the mechanism | **None** (D-0050-1) |
| T-0045-37 | The Lean 4 toolchain: kernel, elaborator, Lake, `leanchecker`, the compiler under `native_decide` | trust root | A theorem taken as proved in Lean that is not; or a true theorem about a Lean that is not the module, code or floor it claims to state | Lean 4.33.1, pinned in `tools/LEAN-PIN`; the replay is the same kernel |

**What has moved in these rows.**

- **T-0045-28.** "Last run 10.05" is superseded by the review's rerun: 82 of 83 traces match (§1.6).
- **T-0045-31.** The two cases are reported upstream and ratified as reported (Batch 39). Class and residual are
  unchanged.
- **T-0045-24.** Annex B still carries it as excluded "until the tool host reads the entry", and says elsewhere
  that it does (E-2). Unchanged since G10 item 89.
- **T-0045-6 and T-0045-27.** Annex B's note on the first says bundle signing is not implemented; its own second
  row says it was built on 2026.10.01 (E-3).
- **T-0045-32 to 36**, the label and operator rows, are in force and are premises of no theorem row in the
  binding table, though ADR-0045 §9 is marked met for "every row but T-0045-7, 21 and 26" (E-1).
- **T-0045-37.** Its identity is said to be printed in every Lean results file, each with a replay; five of the
  sixteen print neither (E-6).
- **Two Proposed records would add rows**, by two conventions: ADR-0056 numbers two in this series (T-0045-38,
  39) with no amendment to ADR-0045, and ADR-0068 numbers twelve in its own (L-7). Neither is in force.

**Read as an inventory.** As on 10.09: at the reference every theorem premised on confinement, gate evidence,
hermeticity or channel fidelity is void; the routing theorem and the gate verdicts rest on checked proofs, and
the gates reproduced on a second platform for the review; coupling's theorems hold modulo the collusion gap;
everything else holds of the modules and, on the paths traced, of the code, with the one trace of §1.6 excepted.
**Twenty-one of the thirty-nine modules in `spec/` have no row in the binding table**: the ten the 10.09
statement named, `Correlator`, two base modules that hold only definitions or are superseded, and the overlay's
eight. So the inventory says nothing about the operator, the emergency seating, labels, liveness, workflows or
the overlay.

---

## 3. Assumptions of use (ToO §13), and whether the reference meets them

| # | Assumption | At the reference | Residual if unmet |
|---|---|---|---|
| A1 | Effect exclusivity enforced by an attested profile at rung ≥ 1 | **Not met**: rung 1 with a failing P3, rung 3 simulated | Every containment theorem void (§1.2) |
| A2 | Every allowlisted tool is hermetic | **Not met** for Build (native tools, T-0045-23); Run tools held to one socket as Wasm, the target read from the entry (A9), the protocol unchecked | One tool with a socket collapses the envelope |
| A3 | Key-holders honest at the capture threshold | Declared trivially: threshold 1, one holder | §1.1 |
| A4 | Grant seats review independently | **Not met**: no independence table; the gate evidence they read is asserted (T-0045-13) | Unanimity multiplies signatures, not judgment |
| A5 | A trained, authorized human present for the emergency seat, quarantine release and `D` | **Not met**: the operator is a socket on the BOOTSTRAP path; an emergency seat is a key, and no drill is counted | HITL and HOTL degrade to unattended operation |
| A6 | Trusted time for intervals that preserve authority: Persona expiry | **Not met**: `T_persona` bounds the declared `ttl` and expiry runs on the local clock. Break-glass no longer has such an interval (it ends with its round), and re-attestation is triggered by renewal | That interval stretches under a slow clock; no clock failure costs containment |
| A7 | The deployment declares its degeneracies | **In part**: Annex B is the trusted-base half; no deployment declaration under ADR-0023 §6 is written and no template exists (G10 item 64) | The theorem inventory is unfounded except as Annex B computes it |
| A8 | Confirmation-required records, twenty-nine, cited as author-ratified | Met in the narrative; this document complies | Overstatement in anything published |
| A9 | Replicas not compromised, authenticated to one another | **Not met**: unauthenticated (§1.7) | Forged admits |
| A10 | Each effect class declares `T_irrev`, and `W + L + D < T_irrev` | **Not met**: no class declared, `L` unmeasured (§5) | HOTL has no budget |
| A11 | The lineage-independence criterion in force with θ set at training scale | **Not met**: ADR-0035 Proposed, θ unset, criterion in no shipped rules; D-0054-1 declared by every deployment | `Contained` has no members whatever the rung |
| A12 | Every Run Thinker's cell Observer keeps up (fairness in `Coupling_live`) | Enforced as safety by coupling, with an e2e fixture as the Observer; the fairness is assumed, not measured | A stall, which is the intended direction |
| A13 | The cell Observer is not colluding | **Uncovered** (§1.3) | Detection fails open |
| A14 | The deployment declares its trusted base under ADR-0045 | **Met, behind the code**: Annex B is current to Batch 37 and to ADR-0033 A15; the workflow build (A16, A17) is pending | An undeclared row is false |
| A15 | Sources are declared as what they are: entry labels, the Run root, destinations, the task (ADR-0047 §9) | **In part**: entry and root labels declared in the bundle; no task at a first seating, so no task label (G10 item 94) | A source declared trusted that carries an attacker's text is seen by nothing |
| A16 | Operators are people with their own keys, vouched for by independent providers (ADR-0050, provisional) | **Not met**: D-0050-1, the unsigned socket, is the reference today; no provider (T-0045-35, 36 absent) | Whatever an operator may do is done by another |
| A17 | A provisional record is cited as provisional (ADR-0029 A4) | Met here: ADR-0050 and ADR-0052 are cited so throughout | A deployment rests on a design its own corpus says may change |
| A18 | A refused Thinker asks again, and grants are made (`Coupling_live`) | Holds in the tests by construction; nothing in the mechanism makes it so | The coupling stall may never end, and the leads-to properties are void |

**What has moved.** Nothing in the reference's standing against A1 to A18. Two of the assumptions read differently
after the review. **A1** asks for a profile "attested ... at rung 1 or above ..., not asserted", and rung 1's
evidence is an assertion (K1-20). **A8** counts twenty-nine confirmation-required records; at least four more carry
a C3 on a ratified amendment that never reached their status line, so the set is larger than the count (K1-6, A-2, A-3, C-14).

---

## 4. What is not measured

| Quantity | Role | State |
|---|---|---|
| `L`, detection latency | The term the oversight placement argument turns on (ADR-0032 §4) | Unmeasured; no Observer exists to measure |
| `D`, human response budget | Same budget | Undeclared; no human process (A5) |
| `W`, propagation window | Same budget | Order-of-magnitude placeholder, ~1 s at the archetype |
| `T_obs`, `K`, Run's `R` | Coupling constants (ADR-0039, ADR-0042) | Placeholders; the `slm/` rehearsal rig could measure `T_obs` and `K` today (CR-36) |
| `T_persona` | Re-attestation cadence bound (ADR-0031 A2) | One hour, a placeholder; read at the reference |
| `T_wf`, the step bound | A workflow's time and step bounds (ADR-0054, Proposed) | Placeholders, undeclared; the record owes values |
| `N` | A mesh's activation budget, what makes a mesh end (ADR-0055, Proposed) | Placeholder, undeclared; checked at small `N` |
| θ<sub>exact</sub>, θ<sub>near</sub>, θ<sub>gen</sub>, β, the near-duplicate tool | The independence criterion's thresholds (ADR-0035) | Unset (`null`); first measurements exist in the 09.28 rehearsal and were not adopted |
| Observer false-negative rate; time-to-bypass | Detection quality; security evaluation (MEASURE 2.4, 2.7) | Unmeasured; no adversarial exercise has been run |
| The correlator's detection function | What correlated Observers would be caught by | **Drafted** (ADR-0051, Proposed; `Correlator.tla` proved); computed by nothing at the reference |
| Floor fitness | Whether the floor is the right floor (MEASURE 2.13) | **Owned** by the bootstrap reviewer, timed (ADR-0030 A3); **nothing names what the test is** (G10 item 87); the reviewer does not exist |
| The liveness fairness | Whether A12 and A18 hold of a real Observer and real operators | Assumed in `Coupling_live`; nothing measures a heartbeat cadence or a grant latency |
| The drill | Whether the emergency path works (ADR-0052 §6) | Nothing counts it (`mechanism/` I48) |

Unchanged. The Proposed records would add to this table (§7.4).

---

## 5. `T_irrev` per effect class (ToO A10; ADR-0032 §4)

| Effect class | Where it leaves the membrane | `T_irrev` | Declared by |
|---|---|---|---|
| Build `Emit` | The round topic, read by the Observer and the Reader | Reversible until a reader acts on it; the deployment states the horizon | Undeclared |
| Build `Submit` | The artifactory, as a promotion candidate | Reversible until promotion; promotion is the gate, not the effect | Undeclared |
| Build `Invoke` of an allowlisted tool | The tool host; hermetic by P4 or excluded (T-0045-23) | Depends on the tool; a native tool's is unbounded | Undeclared |
| Run `Actuate` on a declared channel | The declared target, over the tool host; a Wasm tool's one socket | **The class the budget exists for**; set per target, from the physical process | Undeclared |
| Run `Report` | The round topic | As Build `Emit` | Undeclared |
| Run `Route` (ADR-0040 A2, **pending**, Proposed with ADR-0054) | The workflow's next cell, inside the membrane; classed as an emission (ADR-0015 A1, pending), and the record states its own doubt about that | Reversible until the next cell acts; a route's own `T_irrev` is the successor's | Not in force |

Unchanged: no deployment has declared a `T_irrev` for any class, so the posture ToO §2.6 argues for Run has no
budget behind it at the reference. The overlay would change the rule above the table, and not only add rows
(§7.3).

---

# Part II: If the Proposed records were in force

Eighteen records are Proposed. None is in force, and the reference follows two of them. This part says what each
set would leave, in the set's own words where it has them.

## 6. ADR-0035, ADR-0036, ADR-0051, and ADR-0054 to ADR-0058

- **ADR-0035** (lineage independence) and **ADR-0036** (the rung-1 launcher) are what §1.2 and §1.3 wait on. Their
  residuals are the 10.09 statement's: thresholds unset, no image that passes P3. In force, ADR-0035 would also
  end §1.16.
- **ADR-0051** (the correlator's folds) would give §1.3 a detection function. What it would leave is §1.3's
  qualification: the mechanism does not check a finding, and the model that proves the folds cannot express a
  false one.
- **ADR-0054 and ADR-0055** (workflows) are §1.13. In force as written, they would put the three-way disagreement
  of that row into force with them.
- **ADR-0056** (user scope) would add a trust root, a subject provider, and an excluded row, the downstream
  system's own authorization: "No theorem rests on" it, by the record's own position. It contradicts itself on
  whether the signed assertion naming a user is on the record or kept off it (G-6), which is the one thing an
  acquirer with a privacy obligation needs it to say. Nothing is built or modelled.
- **ADR-0057 and ADR-0058** (the specification graph; deployment overlays) add no residual of their own. They
  would change how this statement's §2 is computed: every theorem would be inherited at a grade. At this tree the
  graph is behind the tree and grades every theorem *trusted* (H-1, H-4).

## 7. The command-chain overlay, ADR-0059 to ADR-0068

Ten records, drafted in one day, that would let a deployment be a tree of control planes, the lowest of them
autonomous. ADR-0068 is the overlay's own residual statement and is carried here. **It was not revised when the
overlay's modules were written, and still says "no module is written"** (I1-1, I2-6); its tables are otherwise the
set's current text.

### 7.1 Fourteen adversaries, each with what bounds it and what is left (ADR-0068 §1)

| # | Adversary | What it can do | What bounds it | What is left |
|---|---|---|---|---|
| TM1 | **The stack**, Byzantine as ADR-0007 has it | Request anything, at any time | The governor, the alphabet, the envelope | Anything inside the envelope was voted acceptable. What the vehicle's body does that no entry names is outside the alphabet |
| TM2 | **The link adversary**: jams, drops, delays, replays, injects | Cut the link above a plane; cut vehicles from their plane, making them alone; delay a revocation; block every irreversible effect | Certificates stop forgery. Fences and sequence numbers stop replay. `K_up` bounds what a delay buys, in effects, and an intent's named tick stops a withheld one from starting late (ADR-0063, ADR-0064) | Denial is always available to it, and the response is predictable: a plane cut off above stops granting before `K_up`, and a vehicle cut off from its plane loses its lease within a tick period and does its terminal behaviour. Silencing vehicles also walks a plane down its shrink schedule (TM12) |
| TM3 | **A captured vehicle** | Extract the key and the lease; act as that principal and as one replica; sign any local record; report anything to its peers | The lease's envelope and what is left of its count. Revocation, once its plane knows. One replica is within what Byzantine agreement tolerates. Its reports are `untrusted` and enable nothing, and its governor's facts can only make others refuse (ADR-0065) | The interlock is moot when the effector itself is captured. Resistance to tampering is the builder's, and is a trust-root residual |
| TM4 | **Compromised replicas, fewer than a third** of a plane | Lie to the others | Byzantine agreement and commit certificates (ADR-0059 §5) | Under crash-recovery consensus one such replica can propose an admit no floor evaluated (A9). That is why ADR-0059 §5 asks for more |
| TM5 | **A captured plane**: a quorum of its replicas, which for an autonomous plane means that share of its vehicles | Issue any lease within its charter, to anyone; ignore fences; falsify its log | The charter or the intent, checked by every governor. Each honest governor keeps its own account against `K_up` and checks every watermark itself (ADR-0063 §3). An autonomous plane adds nothing: it cannot seat, promote or release | Fewer than `K_up` effects from each honest vehicle, within the intent. Its ticks are the captor's, so the duration bound there rests on each honest governor's own clock, which treats a lagging tick as overdue |
| TM6 | **A partitioned mesh** | Leave two groups of vehicles each believing it is the plane | A certificate needs a quorum of the current membership, so at most one side grants and at most one side can order a step of the schedule. The other side's vehicles are alone | A mesh split into pieces all too small admits nothing, and every vehicle is alone |
| TM7 | **An insider with a key**: an operator or a release person | Whatever that seat may do | Attribution. An operator's add needs a live peer (ADR-0050) | The mechanism cannot tell a person from a program holding the key. A wrong act by a release person is recorded and not prevented |
| TM8 | **Navigation deception** | Move the envelope in the world by falsifying a governor's position | Nothing in this design | The navigation source is a trust root with this residual. Time is not exposed the same way, since no external time is read |
| TM9 | **Deception of perception**, the stack's or a person's | Make the stack or the person wrong about the world | For the stack, the premise already assumes it. Perception never adds authority | A deceived person at a release seat is a semantic failure. Nothing here sees it |
| TM10 | **Supply chain**: weights, tools, bundles | Ship a bad artifact | Promotion by digest. Lineage independence, which is Proposed (ADR-0035) | As the corpus states it today |
| TM11 | **A colluding Observer** | Stay silent | Nothing. Coupling cannot see collusion (A13). Declared on another vehicle, it shares no hardware with its Thinker and may share its lineage. Declared on the same vehicle, no claim rests on it (ADR-0062 §8) | As the corpus states it today |
| TM12 | **Attrition**: vehicles destroyed, or silenced until their replicas are dropped | Take a plane below a quorum of its membership | The shrink schedule (ADR-0061 §3): at the archetype's size, four losses one at a time or two at once | Below the capture floor the plane ends and every survivor is alone. An adversary that can silence vehicles gets the floor's tolerance from the start |
| TM13 | **A stack that lies to its peers**, under a signature that verifies | Report false tracks, claim every task, send another stack text meant to steer it | Nothing a peer originates enables anything. Its reports are `untrusted`, and listening narrows (ADR-0065) | An honest stack misled inside its own envelope, and peers stalled by claims. These are the swarm reading's two hardest classes, and nothing here rests on detecting them |
| TM14 | **Clock faults** among a plane's replicas | A slow clock holds an intent open, and a fast one ends it early | Captured and slow replicas together fewer than a certificate (ADR-0064). A fast clock only subtracts | Past that, the duration bound is void. The bound in effects still holds |

Two are bounded by nothing, and the record says so: navigation deception (TM8) and a colluding Observer (TM11).
Its Consequences count three (I1-23, I2-35).

### 7.2 Twelve trusted-base rows, and ten assumptions of use (ADR-0068 §2, §3)

| Id | Row | Class | If it fails |
|---|---|---|---|
| T-0068-1 | The governor's admit path, which now makes every `local` permit | Trust root | Anything the stack requests may reach an actuator |
| T-0068-2 | The governor's clock | A residual, in the slow direction | It finds a tick overdue late. An entry in progress runs on, and only when the plane's ticks have also stopped reaching it (ADR-0064) |
| T-0068-3 | A plane's clocks, taken together | Trust root for the duration bound only | With captured and slow replicas at a certificate or more, an intent outlives its `expiry`. The bound in effects still holds |
| T-0068-4 | The governor's measure of an extent | Trust root for an entry whose extent is a distance or a region | An entry runs past what was voted |
| T-0068-5 | The intent boundary's reading | Trust root for the watermark | A watermark for a record nobody checked releases a charge nobody read |
| T-0068-6 | The governor's key store | Trust root | The vehicle's principal, and its replica, are whoever holds the key |
| T-0068-7 | The navigation source | Trust root for area checks | The envelope is somewhere else |
| T-0068-8 | The effector interlock | Trust root | An irreversible effect without a person's act |
| T-0068-9 | The recovery function | Trust root for the terminal behaviour | Expiry with no safe state |
| T-0068-10 | Cedar and the Wasm engine on the vehicle | Existing rows, instantiated on every vehicle | As those rows say |
| T-0068-11 | The link and the radios | Delegated | Loss only subtracts: a plane cut off above stops granting before `K_up`, and a vehicle cut off from its plane loses its lease. The NATO reading's F2 found this inexact of the proposal's first revision, where a vehicle alone kept entries and lost checks |
| T-0068-12 | Byzantine agreement at an exposed plane, with its reconfiguration step (ADR-0061) | Trust root, in place of the replica row there | A forged certificate, or two successors to one membership |

| Id | Assumption | If it does not hold |
|---|---|---|
| A-0068-1 | The governor is separate from the stack and is the only path to the actuators and the radio | The stack is `Mediated`, and every property here is void. This is A1 for a vehicle |
| A-0068-2 | Captured and slow replicas together are fewer than a certificate, and each sound clock's margin covers its drift | `NoGrantPastExpiry` is void. `EffectsAfterRevocationBounded` is not |
| A-0068-3 | Effect classes are declared as what they are | An irreversible effect is reachable by an agent, or by a governor alone |
| A-0068-4 | Each vehicle class has a declared safe state, and its recovery function reaches it in bounded time | The terminal behaviour is a stall, which for a body in motion is not safe |
| A-0068-5 | A trained, authorized person is at each release seat and can see what the act requires | HITL is a key and not a judgment |
| A-0068-6 | No more replicas of an exposed plane are captured than its current membership tolerates, at every step of its schedule | That plane is captured. It is bounded by its charter or intent, and by each honest governor's account against `K_up` |
| A-0068-7 | What a vehicle does to the world other than through its entries is declared as outside the alphabet | Effect exclusivity is claimed for a body, and is false |
| A-0068-8 | Every entry's extent is declared as what it is | A count bounds how many acts and not what they do |
| A-0068-9 | Envelopes, counts and budgets are voted against what every stack could do together | The joint effect of permitted acts is one no tally weighed |
| A-0068-10 | `T_tick` is long against a round of the plane over its radios | Ticks fall behind and leases end, with no adversary present |

By the record's own Findings, four of the twelve rows (the governor's measure of an extent, the navigation source,
the effector interlock and the recovery function) meet neither of ADR-0045's tests for admitting a component: their
failure can add, and nothing issues their identity. The review counts six such rows by the record's own text, and
the rows are not in ADR-0045's schema or classes (I2-17).

### 7.3 What the overlay gives up (ADR-0068 §4), and what it would reverse

In the record's words: no delegation; a bound in seconds as a theorem; an ordered admit before every effect; a
person in reach, for a plane that is cut off; any act by a vehicle that is alone; inexpressibility of irreversible
effects; a small trusted base; a fixed capture threshold; one bus; and "not autonomous", of which it says the words
stay true and "it is no longer true that a person is always on the plane that orders an effect".

Against Part I, that is: §1.7 changes kind (Byzantine agreement at an exposed plane, with a forged certificate as
the new residual); §5's rule, that an effect irreversible on emission is removed from the alphabet, is replaced
by a person at a `release` seat; and ADR-0032 §4's budget cannot be met while a plane is unattended, with three
options open and none chosen (ADR-0060 §5, R2).

### 7.4 What the overlay's own statement does not say

From the review's two readings of the overlay (CR-48, CR-49), each confirmed by a verifier. These are residuals of
the text as proposed, and each is a place where a reader of ADR-0068 alone would be told less than the records
and modules together say.

| | What the records say | What the review found |
|---|---|---|
| **Budget** | A charter's `budget` is "the most leases the plane and every plane below it may ever issue" | An intent's budget is bounded by the seating's figure and starts afresh with each intent, on one operator's signature; n intents issue up to n times the figure (I2-2). Under capture, nothing bounds what is allocated across the tree (I1-3, I2-7) |
| **Effects after a revocation** | "Fewer than `K_up` further effects" | Proved of charged entries. Sends, beacons, hold, terminal behaviour and a delivered release act are effects by the same records and are not charged (I2-3). Under a captured plane the unread tail is bounded per honest governor, not in total (I1-4) |
| **Duration** | "No grant under an intent more than one tick period past its `expiry`", and "that bounds effects too" | The module does not model a lease's `ttl` (I1-5). As §5 defines it, a tick is overdue at the instant it first becomes signable, so with any round time above zero at least a certificate's worth of vehicles go alone every period; no grace is defined (I2-12) |
| **What the proofs assume** | "Assumptions: none" (`Membership`); seven type assumptions (`PlaneClock`) | The proofs use the base modules' `ASSUME`s, among them the bound on captured replicas and the premise about time; the results files' header does not list them (I1-2) |
| **The replica fault model** | Byzantine agreement "reverses ADR-0045's decision" | ADR-0033 §3 sets the fault model and defers Byzantine agreement; the owed lists do not name it (I2-9) |
| **Where a cell's Observer sits** | "Either, declared per mission" ⟨Q9⟩ | The accepted placement rule says otherwise and no overlay record cites it (I2-5) |
| **Containment of the stack** | Assumption A-0068-1: "This is A1 for a vehicle" | Accepted text requires an appraisal at every grant; here it is an assumption of use (I2-10) |
| **Seats below the root** | A commanded plane promotes and has operators | The charter has no field for grant or operator seats, and accepted text reserves both to the anchor (I2-13) |
| **New undeclared numbers** | `K_up`, `T_tick`, the freshness window, the capture floor, the schedule, each charter's budgets and counts | None has a value. `K_up` must exceed `K`, which is itself a placeholder (R2) |
| **Status** | "Proposed, an overlay, not the archetype"; in eight of ten, "C3 does not apply while this is an overlay" | The process in force defines neither (I2-1, H-2, B-21) |

**For an acquirer.** The overlay's modules are checked, proved and reproduce. What they prove is narrower than the
sentences that cite them in four of the rows above, nothing is built, no floor entry is written, and no reader who
is not the drafter has read any of it. It is a design proposal with unusually good models, and should be cited as
that.

---

# Part III

## 8. For an acquirer or a user: the plain statement

**What you get, at the reference, today.** What the 10.09 statement said, and it still holds: a control plane in
which every agent and human acts through one credential, the lease, granted by consensus and ended by expiry,
revocation or an epoch fence without one; in which authority changes only by a unanimous promotion or an anchor
issuance bounded by a rules floor; in which every admitted effect and every denial is ordered and recorded; in
which the policy tier can only refuse; in which an absent Observer stalls its agent and cannot block an emergency
call; in which, provisionally, an operator is a principal with a key and an emergency is one person seated for one
round; and in which what a Run principal reads carries a label that says, as declared, whether it may go outward.
Each is a proved invariant of a module and a tested behaviour of the code. For this statement the tests were run
(155 pass), the gates were run on a second platform (every verdict reproduces), and the proofs were read and not
re-run.

**What you do not get, today.** Confinement: no principal is `Contained`. Detection that can tell an honest
Observer from a colluding one. Gate evidence that is more than an assertion. A first lease from anything but a
socket. A label that is more than a declaration. Numbers. A stall proved to end. A proof of the binary. A prover
without two known unsound cases. A floor that states the emergency seat's time box. A state of record that matches
the tree: what is in force today is G11 plus two batches that only History rows record. And a second reader: the
design, the proofs, the code, the review and this statement were written and checked by one person and one
assistant.

**What you would get, and not get, from the Proposed records.** Workflows, which already run at the reference on a
floor not in force and whose record, model and code disagree in three places. A binding of calls to users, which
contradicts itself on what it puts on the record. A way to grade how much of each theorem a deployment inherits,
whose own check fails at this tree. And an overlay for groups of vehicles that lose their link, which is the only
part of the Proposed set with proofs, and which gives up delegation, a bound in time, an ordered admit before
every effect and the rule that an irreversible effect is inexpressible, in exchange for bounds that are narrower
than its headline sentences.

**What would change this statement**, in the review's order: a reviewer who is not the author; a checkpoint cut,
so that the state of record is the tree; a decision on what an overlay record is; the Batch 34 retirement carried
through ADR-0015, ADR-0043, ADR-0029 §5 and the reference's rules floor; ADR-0035 ratified, or A2.2 out of force;
a floor entry for the emergency seat's rule, or a sentence that it is the mechanism's; and then the 10.09
statement's list, none of which has moved: a P3-passing image, a first lease from a quorum, measured `L`, `T_obs`
and `K`, a declared `T_irrev`, replica authentication, a signed gate runner, a `Mechanism.tla` that models
workflows, and the coupling leads-to properties proved.

---

## 9. What this document discharges, and what it does not

- **Discharges, as a document:** MANAGE 1.4, at P, as before: the numbers are still undeclared. It answers the one
  fact the 10.09 statement now has wrong (§1.11, the upstream report) and the six it did not have (§1.15 to
  §1.20). MEASURE 1.1's non-measurement declaration (§4). GOVERN 4.2's documentation half (§2).
- **Does not discharge:** any number. It is not a review (MEASURE 1.3). It does not revise Annex B. It does not
  make Part II a statement about anything in force.
- **How it moves.** A derived document is frozen. When a checkpoint is cut, a new statement is written against it
  and this one is marked superseded in `derived/README.md`, as the 10.09 statement is now. The next checkpoint's
  "What G12 does not claim" and this document should agree; where they do not, the checkpoint wins.

## Sources

`derived/topak-residual-risk-statement-2026.10.09.md` (`0af0a985fb418cec`), whose tables §2 to §5 carry;
`decisions/ADR-0045.md` and `decisions/ADR-0068.md` at `bbda621`; `derived/topak-critical-review-2026.11.11.md` and
`derived/topak-open-findings-register-2026.11.11.md`, with the annex's `findings/` for every finding cited by
identifier and `runs/` for every check; `checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md`
(`9d6f95f444455510`). Playbook marks are the 10.09 alignment's and are not re-made.
