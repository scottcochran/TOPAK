# TOPAK — Residual-risk statement

**2026.10.09** · derived · **the statement NIST AI RMF MANAGE 1.4 asks for**, written for an acquirer or a user of the
pattern, not for its author · against Genesis Checkpoint G11 (2026.10.09), Theory of Operation revision 15, ADR-0045
Annex A and Annex B as ratified through Batch 37, `spec/theorem-premise-binding.md` and
`mechanism/GAPS-AND-ASSUMPTIONS.md` at the tree after `ba3e4a3`, the 10.02 critical review (CR-27 to CR-39) and the
10.09 external alignment (§1.6, which itemized what the 10.03 statement had got wrong) · prepared by Claude at the
custodian's request · **supersedes `topak-residual-risk-statement-2026.10.03.md`** as the current statement

**What this is.** One document that says what is left when TOPAK's guarantees are read against what has actually been
built, declared and reviewed. Every sentence here is drawn from a record, a checkpoint, a results file or the trusted
base's residual column; nothing is new, and that is the point: the content exists in pieces (ToO §12's twenty-one
thin places, §13's eighteen assumptions of use, Annex A's residual column, `spec/inventory.py`'s gap premises,
ADR-0025's custody pair, G11 §8) and MANAGE 1.4 asks for it in one place. It is a derived document and not a record:
nothing here is ratified, and a deployment that adopts it writes its own numbers into §5 and §6. **It is the author's
statement about the author's work**, and §1.5 says what that costs.

**What changed since the 10.03 statement.** Two checkpoints, G10 and G11. Break-glass is no longer a floor exception
with no time box but a provisional emergency seating for one person and one round (§1.9). The operator is a principal
with a key, provisionally, and the first lease from a quorum is still unbuilt (§1.4). The prover every proof rests on
is known to prove false statements in two ways, and is kept in use under a rule and a scan (§1.11). A second deductive
method, Lean 4, re-proves fifteen modules and two pieces of the code, and adds a trust root (§1.6, §1.11). Labels now
say where untrusted bytes may go, as declarations (§1.8). Two workflow records are Proposed and the reference follows
them on a floor that is not in force (§1.13). Liveness is stated for the first time, checked and not proved (§1.14).
The trusted base has thirty-seven rows, up from thirty-one (§2). No real principal is `Contained`, as before.

**Two deployments are described.** The *archetype* is the configuration every theorem is about, declared in ADR-0045
Annex A, and nobody runs it. The *reference* is the configuration ADR-0033 cites, declared in Annex B, and it is the
only one that runs. Any other deployment computes its own version of §2 and §3 with `spec/inventory.py` from its
trusted-base declaration (ADR-0045 §1; ADR-0023 §6), and this document says where a reader would start.

---

## 0. In one paragraph

TOPAK's guarantees are theorems about a mechanism, proved of twenty-four TLA+ proof modules (5,416 obligations, every
one proved; twenty-one modules certified; fifteen proved again in Lean of re-encodings) and checked at small
constants, under premises that name every component the mechanism trusts. **At the reference today, every theorem
about confinement, gate evidence, tool hermeticity and effect-channel fidelity is void**, because the components
those theorems rest on are absent, simulated or excluded: no real principal is `Contained`, every principal is
`Mediated`, and the claim that an agent's effects are exactly its admitted actions is an assumption of the same
strength as the one the pattern set out to replace. **What holds at the reference** is the control-plane half: a
lease is the only credential, authority only ever changes by promotion or anchor issuance, every admitted effect is
ordered and recorded, denials are recorded, revocation and expiry subtract without a quorum, detection failing by
absence stalls rather than admits, an emergency call cannot be blocked by an Observer, and the rules floor bounds
what the anchor may issue. Those theorems hold of the modules, and of the running code only on every path a test has
taken, and the test paths have not been replayed since the reference was rebuilt for workflows. **The prover that
proved them can prove false statements in two known ways**; a scan and the author's reading say no cited result
rests on either, and no check detects the first. **Nothing has been reviewed by anyone but its author.** The numbers
the mechanism runs on are placeholders. The headline residual is numeric and is stated first.

---

## 1. The headline residuals, in order

### 1.1 Anchor capture: a coalition at the custody threshold can issue any floor-conformant rules

ADR-0025 makes the anchor a havoc issuer whose intent is the one axiom. **No safety theorem covers anchor intent.** The
rules floor (ADR-0026: R1, R2, R5, R6, R7, R9 in force; R3 and R8 withdrawn) bounds what an issuance may say, and the
bound is what remains: an issuance cannot make a solo grant (R9), cannot seat the anchor as an approver (R5), cannot
give break-glass authority over `Issue`, `Vote` or promotion (R7), cannot exceed the exception count, now one (R6).
Within that bound a coalition at the capture threshold issues any roster, any seat, any verifier, bundle, provider or
gate-runner key, and, at the reference, **may change a seat's kind**, which `rules::validate_issuance` does not refuse
and no record decides (ADR-0053 finding 8; G11 item 106).

| | Archetype | Reference |
|---|---|---|
| Custody pair (capture threshold, loss tolerance), ADR-0025 §2 | Declared per deployment; no archetype value is fixed in a record | **(1, 0)**: three dev keys held by one person, secrets in the clear (`dev/secrets/`, G6) |
| What a captured anchor can do | Issue any floor-conformant rules at the next epoch; nothing below the floor | The same, and the policy floor it issues against is genesis-provisional (ADR-0030 A3), with a fourth stage linked that is not in force (§1.13) |
| What it cannot do | Admit an action the floor refuses; change the rules floor itself (R1–R9 are mechanism constants); erase the forensic floor (ADR-0028) | The same |
| Numeric residual (ADR-0025 Consequences: "the capture threshold feeds MANAGE 1.4 directly") | **The threshold is the deployment's to declare, and none has** | **1**: one key-holder is the coalition |

### 1.2 Effect exclusivity is assumed: no principal is `Contained`

The pattern's distinctive claim is that an agent's effects are exactly its admitted actions, as a mechanism claim and
not an assumption (ADR-0015 E2). The design half closed on 09.28 (ADR-0034); the launcher in the node was ratified on
10.04 (ADR-0033 A7, Batch 29); the mechanism half is open (G11 item 1, "as at G9").

- **Rung 1 trusts the host by construction** (ADR-0034 §6; ADR-0036 §5): the person who runs the launcher, the
  launcher, the container runtime and the image are trusted for guest integrity, and the reference's own test shows
  a launcher that reports the image it was asked for while running another is believed (`every_host_power_subtracts`).
- **Every rung-1 profile declares a failing clause.** The host-process profile fails P1 to P3; the container profile
  fails P3 (ADR-0036 §4, still Proposed). No P3-passing image exists.
- **Rung 3 is SIMULATED**: the CPU root of trust and the verifier (T-0045-16, 17) are keys a test made. `contained =
  true` appears only there, under a criterion the test issues, and is a witness that the lookup is reachable, not a
  claim.
- **The independence criterion is in force nowhere.** `Contained` has a fourth conjunct, ADR-0035's criterion in the
  issued rules (ADR-0034 §4); ADR-0035 is Proposed (now at R8) and no shipped rules set it. Even a real rung 3 would
  not be `Contained` today.
- **Rung 2 is a seam**; `apply_grant` refuses it.
- **A workflow's seating above rung 0 does not load** at the reference (`mechanism/` I49 (c)).

**Consequence for a user.** An agent with a shell outside the launcher bypasses the front door, and nothing in the
mechanism sees it (`mechanism/` G1). Until this moves, ADR-0015's claim and Moon & Varshney's assumption are
identical in strength (ADR-0015 E2; CR-1, CR-27).

### 1.3 Detection fails open against a colluding Observer

ADR-0039 closed three of four failure cases by mechanism: a dead, partitioned or starved Observer stalls its Thinker
(coupling). **The fourth, collusion, is open and declared** (ADR-0039 §5; ToO A13): every liveness fact the mechanism
reads is the Observer's own assertion, a heartbeat and a watermark, and an Observer that lies about keeping up is
indistinguishable from one that does. The only structural cover is lineage independence (ADR-0035), which is Proposed,
unbuilt in the reference, and whose correlated-miss test has never run (ToO §12 item 12). **The correlator now has a
drafted detection function**, five folds over facts in ADR-0051, Proposed, with `Correlator.tla` proved and
certified; **nothing at the reference computes one** (G11 item 97). The code also allows several Observers in one
cell, which gives each half of `UnreadBounded` its own witness and which no record decides (ADR-0053 finding 10; item
106).

### 1.4 The operator is a principal on paper; the first lease still comes from a socket

The 10.03 statement called the operator channel the untyped half of the control plane (CR-34). ADR-0050, ratified
**provisional** in Batch 34, answers it in design: an operator holds a seat of kind `operator`, is `Mediated`, signs
six control requests decided by nine floor entries `C1` to `C9`, can deny without a lease, and can add only inside a
quorum's grant with a live peer. The reference follows that for the six requests (`mechanism/` I47). **What it does
not follow is the record's centre**: a first lease from a completed quorum. At the reference whoever reaches the
socket can still seat, as a BOOTSTRAP path, which is D-0050-1, the degeneracy under which no operator theorem holds
(ADR-0050 §8; ToO §12 item 17). The operator's identity provider and key custody (T-0045-35, 36) have no instance.
Gate evidence is still an operator's unsigned assertion (T-0045-13, excluded: **every promotion theorem that assumes
gates ran is void**). The task's label on a grant is the operator's word on the same channel (T-0045-33). Replica-to-
replica traffic is unauthenticated (T-0045-1). The record is provisional for these reasons and break-glass, which
rests on it, has no settled form if it is redesigned (§1.9).

### 1.5 Nothing is independently reviewed

Fifty-four record files; forty-seven Accepted, of which twenty-nine carry a confirmation-required marker, two of them
provisional; five Proposed; twelve amendments pending, every one depending on a Proposed record (G11 §1.1). Every text
ratified since G9, in eleven batches across five days, was drafted by the assistant at the custodian's direction,
built at the reference, modelled, proved, trace-checked and regenerated by the same hand, including the three Lean
packages and the review runs that found the prover's defects (ToO §12 item 3; G11 §4). ADR-0029 A2 makes a
full-corpus independent review a bootstrap precondition. The A2.5 line reads: **bootstrap reviewer engaged, none;
last completed review pass, none** (`checkpoints/README.md`). The custodian's readings at Batches 36 and 37 were of
one transcription and of 67 proof steps, and are the ratifier's, not a reviewer's. TACIP 12.2.1's meta-safeguard for
AI-assisted verifiers and MEASURE 1.3's independent assessors both land here. Every claim below, including this
document, is the author's.

### 1.6 What runs is not what is proved

Twenty-four proof modules' invariants are proved (5,416 obligations) and their mutations and witnesses checked at
small constants. The running reference (155 tests across fifteen binaries, 38 Rego tests, at `749d54f`) is asserted
to follow them. Three kinds of evidence connect them, and none is a refinement (T-0045-28):

- **Trace validation**: every recorded behaviour of the tests replayed through `spec/Mechanism.tla`, 82 traces and
  1,007 steps matching, **last run 2026.10.05**. `Mechanism.tla` does not model workflows, so the rebuilt reference
  of 10.08 and 10.09 has not been replayed (ADR-0033 A16, A17, pending; G11 item 56). It covers no path a test does
  not take and cannot check `ContainedMeansConfined`, which is about the image the host actually ran.
- **Lean transcriptions and models** (ADR-0053, Batch 36): `admit.rs`'s decision proved a step of
  `FloorComposition`'s `Decide`; `clock.rs`'s interval proved to fail closed; two models of `apply` proved and replayed
  against the recorded traces. They are of a transcription read against the Rust and of models, not of the compiled
  code or every path, and **the package is stale at G11**: the enums it transcribes gained `Route` and `orchestrator`
  and `tools/lean-sync.sh` exits 1 (item 103). `refines(Seats)`, the one route around T-0045-28 the premise table
  names, is confirmation-required and no ADR-0033 addendum cites it as a stage (item 107).
- **The reference follows text that is not in force, again** (item 102): two Proposed records and a floor stage that
  is not the floor in force, at the custodian's direction, as it followed ADR-0047 to ADR-0052 for two days before
  Batch 34.

No reproducible build fixes the release's provenance from its source (T-0045-30). In Moon & Varshney's ordering the
modules are *Universal* and the running reference is *Empirical* (CR-4).

### 1.7 A compromised replica forges admits

The replicas are crash-fault, not Byzantine (ADR-0033 §3; T-0045-1). A compromised replica can propose an admit no
floor evaluated; the apply-time re-check stops stale admits, not forged ones. Mutual authentication, the delegated
mitigation, is unbuilt; it would stop impersonation and not compromise. BFT was considered and declined (ADR-0045 §6).
Since Batch 34 the label facts and an activation's envelope are the deciding replica's computation, which the others
re-check only as far as `clearSet` (G10 item 93), and a handle resolves from results one replica holds in memory.

### 1.8 Prompt injection inside the envelope: labels say where bytes may go, as declared

The floor bounds what *can* happen; nothing bounds what an injected Thinker *will* do inside the bound. Since Batch 34
ADR-0047 adds what the 10.03 statement said had no record: every item a Run principal consults carries its source's
label, a join computes the result's label, a table says what is delivered clear and what as a handle, and `clearSet`
bounds the round; three floor entries named by ADR-0041 A1, `R5-no-read-then-send`, `R6-no-steered-destination` and
`R7-no-replayed-destination`, forbid the three label failures. **What remains is
declared, not found** (ToO §12 item 18): the labels on an allowlist entry, the Run root and the task are the word of
whoever issued the bundle or the grant (T-0045-33, excluded), and a source declared trusted that carries an attacker's
text is seen by nothing. The label computation itself is a new trust root (T-0045-32): a `clearSet` computed too
small lets a forbid not fire. The reference does not yet carry a task at a first seating, so the refusal of a grant
with no label is not followed, and ADR-0049 §2's digest over an entry's inputs, which would pin a tool's interface
text, is not computed (G10 item 94). Tool purpose text is prose that passed promotion and nothing checks (ADR-0048
§5). The Observer is what remains for everything a label does not see.

### 1.9 Break-glass is a provisional emergency seating, and the mechanism cannot tell a person from a program

The two faults the 10.03 statement named are gone by record: the emergency path no longer waits on a dead Observer,
and no longer lacks a time box. ADR-0052 (Batch 34, **provisional**) retires floor exception X1: a roster's quorum
activates a seating for one named person and one round; the lease ends with its round, has no successor and no
renewal; its envelope is the domain's ordinary allowlist; it is not coupled, because coupling is a `thinker`'s rule.
R8 was withdrawn (ADR-0026 W1). That an emergency call cannot be blocked by an Observer is now a proved invariant over
`ENABLED`, not a reachability witness (`Emergency_live.tla`; proved through Isabelle and in Lean). **What remains:**

- "Only a person holds an emergency seat" is a rule about what is seated. **The mechanism cannot tell a person from a
  program holding the person's key** (T-0045-36; ADR-0052 §4), and the reason for the emergency is unknown to it by
  construction.
- The record is **in force and subject to redesign** (ADR-0029 A4). A deployment that builds on it builds on a design
  its own corpus says may change, and ADR-0050's redesign, if any, carries it along (G10 items 88, 92).
- At the reference a seating prepared by promotion is stood in for by the BOOTSTRAP path; there is no socket path for
  a person's signed action and nothing counts the drill (`mechanism/` I48).
- An activation's record kept only while its round is live is a third non-composition failure the seating made
  possible (`NonComposition_A1.tla`); the module forbids it and the reference's archive does not exist (§1.12).

### 1.10 Every number is a placeholder, and nothing is measured

`T_obs` 5000 ms, `K` 8, Run's `R` 64, `T_persona` one hour, the five lineage thresholds unset
(`floor/genesis-values.json`, header still "DRAFT · PLACEHOLDERS · not measured"; ADR-0035). Two Proposed records
add three more: `T_wf` and the step bound on a workflow (ADR-0054), and the activation budget `N` on a mesh
(ADR-0055), each a placeholder a deployment is to set (G11 item 101). No Observer has been measured; `L`, the
detection latency the whole oversight argument turns on, is unmeasured; `T_irrev` is declared for no effect class
(§5 below). The proofs quantify over these values and cannot say what they should be (CR-36). A deployment that ships
them is declaring them. One attribute, `denials`, was dropped from the workflow records on 10.09 because no replica
holds a count every replica agrees on (ADR-0054 R6; `mechanism/` finding 22).

### 1.11 The prover is known to be unsound in two ways, and is kept in use

The 10.03 statement said the verifiers were trusted as written. **T-0045-31's instance, `tlapm` 7824dab, is now
recorded to have two known unsound cases** (ADR-0046 A2; ADR-0045 A3; Batch 37). In the first, the translation
abstracts a term it does not translate (an `ENABLED` or `\cdot` not expanded, a temporal formula) as a constant that
drops any variable bound around it. In the second, every abstracted term and every atom handed to LS4 is named by 20
bits of a hash the prover does not check, of a print that does not tell a bound variable from a constant of its
name. A module that extends only `TLAPS` proves `FALSE` twice and certifies (`spec/proof-certification.md` §8).
What stands between the proofs and the cases is a writing rule (§10), a scan over the obligations sent to a backend
(1,853, every one printed normalized, no capture) and the custodian's reading of 67 steps. **No check detects the
first case** (G11 item 104). The proofs written before 10.07 were written without the rule. The defects are not
reported upstream, by the custodian's decision. No row changes class, and the claim that no cited result rests on
either case is confirmation-required (C2).

What the rest of the toolchain is: twenty-one of twenty-four proof modules are certified, meaning cvc5's proofs are
checked by the checker of T-0045-14 and Zenon's by Isabelle, so for those the SMT solver's soundness is no longer a
premise and the prover's translation is (T-0045-31 since B28). The Lean kernel and toolchain are a new trust root
(T-0045-37): the replay is the same kernel, not an independent one; `#print axioms` misses a declaration added past
the kernel and only the replay refuses it (ADR-0053 finding 1); `native_decide` trusts the compiler in the floor
package; the kernel's soundness is unexamined. The Cedar engine (T-0045-3), TLC at the constants run (T-0045-29)
and the build toolchain (T-0045-30) are as before. A certified proof is not a verified one, and a second derivation
by the same hand is not a second reader.

### 1.12 Legibility residuals

The archive does not exist (T-0045-7): evidence bytes are retained by the appraising node alone, so a Contested
revocation's attribution cites evidence one node holds (I40). Denials reach the round topic and the bounded `after`
companion, and are still erasable with the topic (CR-7); they are never ordered, which is why a workflow cannot count
them (§1.10). Workspaces are not replicated, so a `Submit` is checkable only where its drafts were written. Erasure
(ADR-0006) is unbuilt. Replay is boundary events only (ADR-0020), and a deployment claiming root-cause capability
under TACIP 8.2 would have to say what compensates (CR-38). A clear workflow input needs a read path the reference
does not have: the transport writes topics and does not read them (`mechanism/` finding 23).

### 1.13 Workflows and meshes: Proposed, built, and followed on a floor not in force

ADR-0054 (a workflow is a promoted DAG) and ADR-0055 (a workflow may be a mesh) were drafted 10.07 and are Proposed.
**The reference was built to both** and links the proposed floor's `workflow` stage (30 policies, 123 cases, gates
passing) at the custodian's direction, so **the floor the reference follows is not the floor in force** (G11 §2.2,
item 102). Ten dependent amendments to accepted records are pending on them, among them a fourth Run variant `Route`
classed as an emission, a sixth seat kind `orchestrator`, and a third grant path. What the records say of their own
residual: the orchestrator is a Byzantine principal of its own that **can stall a workflow and cannot misroute it**;
without write-once attributes it can loop for ever, and one unbounded run reached depth 665 (ADR-0054 finding 7); a
budget that does not charge the orchestrator leaves the one cell that runs at every decision unbounded (ADR-0055
finding 2). Lineage alternation on a clear edge is declared and not enforced until ADR-0035 is in force, so **every
deployment today declares D-0054-1**. `Workflow.tla` and `Mesh.tla` are TLC-checked with no proof, each with a
remainder checked under a cap by the custodian's decision (`CapLog`, `CapOnePast`), and the reference makes nine
PROVISIONAL choices under them (`mechanism/` I49). ADR-0055's dependent entries are not drafted.

### 1.14 No stall is shown to end

The design's answer to failure is to stall, and a stall that never ends is safe. CR-37 found that no record asked
which stalls must end; the liveness plan of 10.07 sorts them. What exists: two `ENABLED` invariants for the emergency
call, proved (§1.9); four leads-to properties for coupling in `Coupling_live.tla`, **checked by TLC at small constants
and proved by nothing**, under fairness the assumptions of use now name (A12, A18). A mutation, `M_HBLIVE`, passes
every safety check and every witness and only a leads-to property catches it, which is the case for stating them and
for the fact that nothing before 10.07 could have. Proving them is owed, and both of the prover's known cases live in
`ENABLED` premises (ToO §5.5). Not stated at all: that the promotion stall ends, which needs a premise the corpus
lacks; a seal for every ended lease; a lapsed operator seated again; detection itself (G11 item 105). A deployment
that will not accept a stall declares D-0039-1 and detection fails open.

---

## 2. The trusted base, row by row: what stands when each fails

ADR-0045 Annex A's residual column, with Annex B's instance, in one table. *Class* is at the archetype; *At the
reference* is what Annex B declares, as of Batch 37, against the tree ADR-0033 A15 cites; A16 and A17 are pending and
Annex B does not yet reflect the workflow build. **An excluded or absent row voids every theorem premised on it**
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

**Read as an inventory** (ADR-0045 Annex B; `spec/theorem-premise-binding.md`, last column, 43 rows): at the
reference, every theorem premised on confinement, gate evidence, hermeticity or channel fidelity is **void**
(`ContainedMeansConfined`, `ContestedStopped`, effect exclusivity, `PromotionMeetsIssuedQuorum`); the routing theorem
and the gate verdicts rest on checked proofs; the bundle's revision is verified; `ReachIsBounded` is declared and not
enforced; coupling's theorems hold **modulo the collusion gap**; everything else, the lease, the fence, revocation,
composition, the rules floor, the bootstrap pair, seats, any-of, Run's counters and seal, holds of the modules and,
on the paths traced on 10.05, of the code. Every proved row rests on T-0045-31; the Lean route is a second route beside
it, not a replacement, and the inventory is unchanged by it. **Ten checked modules have no row in the table**:
`Labels`, `ToolList`, `Operators`, `Emergency`, `BreakGlass_A1`, `NonComposition_A1`, `Emergency_live`,
`Coupling_live`, `Workflow` and `Mesh` (G11 item 90), so the inventory says nothing about the operator, the emergency
seating, labels, liveness or workflows.

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

---

## 4. What is not measured (MEASURE 1.1's non-measurement declaration; MEASURE 3.2)

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

---

## 5. `T_irrev` per effect class (ToO A10; ADR-0032 §4)

ADR-0032 ratified the budget `W + L + D < T_irrev` "as a form with two unknowns" and said no effect class had a
declared `T_irrev`. That is still so. The form a deployment fills in is below, with the effect classes the alphabets
name (ADR-0022, ADR-0040) and the one rule that applies before any number does: **an effect irreversible on emission
must be removed from the alphabet** (ADR-0032 §4), because no budget can be met for it.

| Effect class | Where it leaves the membrane | `T_irrev` | Declared by |
|---|---|---|---|
| Build `Emit` | The round topic, read by the Observer and the Reader | Reversible until a reader acts on it; the deployment states the horizon | Undeclared |
| Build `Submit` | The artifactory, as a promotion candidate | Reversible until promotion; promotion is the gate, not the effect | Undeclared |
| Build `Invoke` of an allowlisted tool | The tool host; hermetic by P4 or excluded (T-0045-23) | Depends on the tool; a native tool's is unbounded | Undeclared |
| Run `Actuate` on a declared channel | The declared target, over the tool host; a Wasm tool's one socket | **The class the budget exists for**; set per target, from the physical process | Undeclared |
| Run `Report` | The round topic | As Build `Emit` | Undeclared |
| Run `Route` (ADR-0040 A2, **pending**, Proposed with ADR-0054) | The workflow's next cell, inside the membrane; classed as an emission (ADR-0015 A1, pending), and the record states its own doubt about that | Reversible until the next cell acts; a route's own `T_irrev` is the successor's | Not in force |

The reference's effect classes in force are the first five and no others; `Route` is built and not in force. No
deployment has declared a `T_irrev` for any of them, so the HOTL posture ToO §2.6 argues for Run has, at the
reference, no budget behind it. A workflow's `T_wf` is a bound on the whole workflow and is not a `T_irrev`.

---

## 6. For an acquirer or a user: the plain statement

**What you get, at the reference, today.** A control plane in which every agent and human acts through one credential,
the lease, granted by consensus and ended by expiry, revocation or an epoch fence without one; in which authority
changes only by a unanimous promotion or an anchor issuance bounded by a rules floor; in which every admitted effect
and every denial is ordered and recorded; in which the policy tier can only refuse; in which an absent Observer stalls
its agent and cannot block an emergency call; in which, provisionally, an operator is a principal with a key who can
stop things without a lease, and an emergency is one person seated for one round; and in which what a Run principal
reads carries a label that says, as declared, whether it may go outward. Each of those is a proved invariant of a
module, two of them proved twice, and a tested behaviour of the code.

**What you do not get, today.** Confinement. No principal is `Contained`; every one is `Mediated`, which means the
mechanism attributes and authorizes its actions and does not bound its effects. An agent that can reach a shell, a
socket or a filesystem outside the launcher is outside the guarantee, and the mechanism will not know. Detection
cannot tell an honest Observer from a colluding one. Gate evidence is asserted. A first lease comes from whoever
reaches a socket. A label is a declaration. The numbers are placeholders. No stall is proved to end. The proofs are of
the design, not of the binary, and the prover that checked them is known to prove false statements in two ways that
a rule and a reading, not a check, are said to have kept out. The reference follows two records that are Proposed on
a floor that is not in force. The design, the proofs, the code and this statement were written and checked by one
person and one assistant, with no second reader.

**What would change this statement**, in the order the 10.02 review and G11 put them: a reviewer who is not the
author; a P3-passing image under a declared profile; a first lease from a completed quorum at the reference, and
ADR-0050 and ADR-0052 out of provisional; ADR-0035 in force with measured thresholds; real rung-3 hardware behind
T-0045-16 and 17; a check for the prover's first case, or the defects reported and fixed upstream; the correlator's
function computed; measured `L`, `T_obs` and `K`; a declared `T_irrev` per Run target; replica authentication; a
signed gate runner; trace validation rerun over a `Mechanism.tla` that models workflows, and the Lean package brought
to the tree; ADR-0054 and ADR-0055 ratified or withdrawn, so the reference follows text in force; the coupling
leads-to properties proved.

---

## 7. What this document discharges, and what it does not

- **Discharges, as a document:** MANAGE 1.4 (residual risk documented for acquirers and users), which the 10.09
  alignment moved from G to P on the 10.03 statement's existence and marked stale on nine facts; this statement
  answers each of the nine (§1.4, §1.6, §1.9, §1.10, §1.11, §1.13, §1.14, §2, §4) and keeps the row at P, because the
  numbers are still undeclared; MEASURE 2.6's third clause (residual within tolerance: the tolerance is the
  deployment's, and §1 to §5 are what it is measured against); MEASURE 1.1's non-measurement declaration (§4);
  GOVERN 4.2's documentation half (§2; communication outside the repository is still none); TACIP 1.3.4's evidence
  package, in the form of a pointer to the manifests, results files and this statement; the *form* of A10's
  `T_irrev` declaration (§5).
- **Does not discharge:** any number. The custody threshold, `T_irrev` per class, the coupling constants and the
  workflow bounds are a deployment's to declare, and this document records that none has. It is not a review
  (MEASURE 1.3) and it does not make the corpus less self-attested; it makes the self-attestation legible in one
  place. It does not revise Annex B, which still carries T-0045-24 as excluded for a reason that ended at A9 (G10
  item 89).
- **How it moves.** A derived document is frozen. When the state of record moves, a new statement is written against
  the new checkpoint and this one is marked superseded in `derived/README.md`, as the 10.03 statement is now. The
  next checkpoint's §8 ("What G12 does not claim") and this document should agree; where they do not, the checkpoint
  wins. The Playbook marks this statement is read against are the 10.09 alignment's (M 11 · P 27 · C 3 · G 3 · X 28).
