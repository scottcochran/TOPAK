# TOPAK — Residual-risk statement

**2026.10.03** · derived · **the statement NIST AI RMF MANAGE 1.4 asks for**, written for an acquirer or a user of the
pattern, not for its author · against Genesis Checkpoint G9 (2026.10.02), Theory of Operation revision 13, ADR-0045
Annex A and Annex B, `spec/theorem-premise-binding.md` and `mechanism/GAPS-AND-ASSUMPTIONS.md` at the tree after
`0f94f31`, and the 10.02 critical review (CR-35) · prepared by Claude at the custodian's request

**What this is.** One document that says what is left when TOPAK's guarantees are read against what has actually been
built, declared and reviewed. Every sentence here is drawn from a record, a checkpoint, a results file or the trusted
base's residual column; nothing is new, and that is the point: the content has existed in pieces since 09.12 (ToO
§12's sixteen thin places, §13's fourteen assumptions of use, Annex A's residual column, `spec/inventory.py`'s gap
premises, ADR-0025's custody pair) and MANAGE 1.4 asks for it in one place. It is a derived document and not a
record: nothing here is ratified, and a deployment that adopts it writes its own numbers into §5 and §6. **It is the
author's statement about the author's work**, and §1.5 says what that costs.

**Two deployments are described.** The *archetype* is the configuration every theorem is about, declared in ADR-0045
Annex A, and nobody runs it. The *reference* is the configuration ADR-0033 cites, declared in Annex B, and it is the
only one that runs. Any other deployment computes its own version of §2 and §3 with `spec/inventory.py` from its
trusted-base declaration (ADR-0045 §1; ADR-0023 §6), and this document says where a reader would start.

---

## 0. In one paragraph

TOPAK's guarantees are theorems about a mechanism, proved of fifteen TLA+ modules and checked at small constants, under
premises that name every component the mechanism trusts. **At the reference today, every theorem about confinement,
gate evidence, tool hermeticity and effect-channel fidelity is void**, because the components those theorems rest on
are absent, simulated or excluded: no real principal is `Contained`, every principal is `Mediated`, and the claim that
an agent's effects are exactly its admitted actions is an assumption of the same strength as the one the pattern set
out to replace. **What holds at the reference** is the control-plane half: a lease is the only credential, authority
only ever changes by promotion or anchor issuance, every admitted effect is ordered and recorded, denials are
recorded, revocation and expiry subtract without a quorum, detection failing by absence stalls rather than admits, and
the rules floor bounds what the anchor may issue. Those theorems hold of the modules, and of the running code only on
every path a test has taken. **Nothing has been reviewed by anyone but its author.** The numbers the mechanism runs on
are placeholders. The headline residual is numeric and is stated first.

---

## 1. The headline residuals, in order

### 1.1 Anchor capture: a coalition at the custody threshold can issue any floor-conformant rules

ADR-0025 makes the anchor a havoc issuer whose intent is the one axiom. **No safety theorem covers anchor intent.** The
rules floor (ADR-0026: R1, R2, R5, R6, R7, R9 in force; R8 pending) bounds what an issuance may say, and the bound is
what remains: an issuance cannot make a solo grant (R9), cannot seat the anchor as an approver (R5), cannot give
break-glass authority over `Issue`, `Vote` or promotion (R7), cannot exceed the exception count (R6). Within that bound
a coalition at the capture threshold issues any roster, any seat, any verifier or bundle key.

| | Archetype | Reference |
|---|---|---|
| Custody pair (capture threshold, loss tolerance), ADR-0025 §2 | Declared per deployment; no archetype value is fixed in a record | **(1, 0)**: three dev keys held by one person, secrets in the clear (`dev/secrets/`, G6) |
| What a captured anchor can do | Issue any floor-conformant rules at the next epoch; nothing below the floor | The same, and the floor is a DRAFT (G9 §2.2) |
| What it cannot do | Admit an action the floor refuses; change the rules floor itself (R1–R9 are mechanism constants); erase the forensic floor (ADR-0028) | The same |
| Numeric residual (ADR-0025 Consequences: "the capture threshold feeds MANAGE 1.4 directly") | **The threshold is the deployment's to declare, and none has** | **1**: one key-holder is the coalition |

### 1.2 Effect exclusivity is assumed: no principal is `Contained`

The pattern's distinctive claim is that an agent's effects are exactly its admitted actions, as a mechanism claim and
not an assumption (ADR-0015 E2). The design half closed on 09.28 (ADR-0034); the mechanism half is open (G9 item 1).

- **Rung 1 trusts the host by construction** (ADR-0034 §6; ADR-0036 §5): the person who runs the launcher, the
  launcher, the container runtime and the image are trusted for guest integrity, and the reference's own test shows
  a launcher that reports the image it was asked for while running another is believed (`every_host_power_subtracts`).
- **Every rung-1 profile declares a failing clause.** The host-process profile fails P1 to P3; the container profile
  fails P3 (ADR-0036 §4). No P3-passing image exists (G9 item 36).
- **Rung 3 is SIMULATED**: the CPU root of trust and the verifier (T-0045-16, 17) are keys a test made. `contained =
  true` appears only there, under a criterion the test issues, and is a witness that the lookup is reachable, not a
  claim (G9 §5).
- **The independence criterion is in force nowhere.** `Contained` has a fourth conjunct, ADR-0035's criterion in the
  issued rules (ADR-0034 §4); ADR-0035 is Proposed and no shipped rules set it. Even a real rung 3 would not be
  `Contained` today.
- **Rung 2 is a seam**; `apply_grant` refuses it.

**Consequence for a user.** An agent with a shell outside the launcher bypasses the front door, and nothing in the
mechanism sees it (`mechanism/` G1). Until this moves, ADR-0015's claim and Moon & Varshney's assumption are
identical in strength (ADR-0015 E2; CR-1, CR-27).

### 1.3 Detection fails open against a colluding Observer

ADR-0039 closed three of four failure cases by mechanism: a dead, partitioned or starved Observer stalls its Thinker
(coupling). **The fourth, collusion, is open and declared** (ADR-0039 §5; ToO A13): every liveness fact the mechanism
reads is the Observer's own assertion, a heartbeat and a watermark, and an Observer that lies about keeping up is
indistinguishable from one that does. The only structural cover is lineage independence (ADR-0035), which is Proposed,
unbuilt in the reference, and whose correlated-miss test has never run (ToO §12 item 12). The correlator, the seat
that would detect correlated Observers, has a seat kind, a placement rule and a read set, and computes nothing (G9
item 43).

### 1.4 Rung 1 trusts the operator; the operator channel is the untyped half of the control plane

Principals' actions are typed, lifted, floored and bundled. Operator requests (`grant`, `launch`, `revoke`, `issue`,
`GatesPassed`, profile registration) are authenticated at the reference by a socket's file mode; replica-to-replica
traffic is unauthenticated (T-0045-1: anyone reaching a socket is a replica, mitigation unbuilt); gate evidence is an
operator's assertion (T-0045-13, excluded: every promotion theorem that assumes gates ran is void). The surface that
can add authority is the one with the least type discipline (CR-34).

### 1.5 Nothing is independently reviewed

Forty records are Accepted, twenty-two carry a confirmation-required marker, seven texts were drafted by the assistant
(four ratified, three pending), and the pending ones were drafted, built, checked, mutation-tested, proved and
regenerated by the same hand in one day (G9 §4, §8). ADR-0029 A2 makes a full-corpus independent review a bootstrap
precondition; **no reviewer is engaged and no review pass has run** (`checkpoints/README.md`, the A2.5 line). TACIP
12.2.1's meta-safeguard for AI-assisted verifiers and MEASURE 1.3's independent assessors both land here. Every claim
below, including this document, is the author's.

### 1.6 What runs is not what is proved

Fifteen modules' invariants are proved (3,036 obligations) and their mutations checked at small constants. The running
reference is asserted to follow them, and shown to agree with an operational model of itself on every tested path (62
traces, 709 steps, every state keeping the abstract confinement invariants). **That is a harness, not a refinement**
(T-0045-28): it covers no path a test does not take, and it cannot check `ContainedMeansConfined`, which is about the
image the host actually ran. No reproducible build fixes the release's provenance from its source (T-0045-30). In Moon
& Varshney's ordering the modules are *Universal* and the running reference is *Empirical* (CR-4, §2 of the 10.02
review).

### 1.7 A compromised replica forges admits

The replicas are crash-fault, not Byzantine (ADR-0033 §3; T-0045-1). A compromised replica can propose an admit no
floor evaluated; the apply-time re-check stops stale admits, not forged ones. Mutual authentication, the delegated
mitigation, is unbuilt; it would stop impersonation and not compromise. BFT was considered and declined (ADR-0045 §6).

### 1.8 Prompt injection inside the envelope has no record

The floor bounds what *can* happen. Nothing bounds what an injected Thinker *will* do inside the bound: under havoc an
injected Run principal may `Actuate(send, …)` to any target the floor allows with those argument types. Provenance
labels on `Consult` and `Actuate` arguments, and the digest of a tool's interface text in its allowlist entry, are
sketched in the 10.01 competitive assessment and have no record, owner or open-list item (CR-32). Tool descriptions
are unpinned.

### 1.9 Break-glass is both too hard to obtain and too easy to keep

Floor entry R3 couples every effect-bearing Run admit to a live cell Observer, break-glass included, so the emergency
path waits on a dead Observer (ADR-0039 R4, ratified as written; G9 item 49). R8, the break-glass TTL, is pending with
four unmet conditions, so an approval is time-unbounded within an epoch (ADR-0026 A1; G9 item 8). Both fixes are small
and both wait on a decision (CR-29).

### 1.10 Every number is a placeholder, and nothing is measured

`T_obs` 5000 ms, `K` 8, Run's `R` 64, `T_persona` one hour, the five lineage thresholds unset (`floor/genesis-values.json`;
ADR-0035). No Observer has been measured; `L`, the detection latency the whole oversight argument turns on, is
unmeasured; `T_irrev` is declared for no effect class (§5 below). The proofs quantify over these values and cannot say
what they should be (CR-36). A deployment that ships them is declaring them.

### 1.11 The verifiers are trusted as written

The Cedar engine (T-0045-3, residual: divergence on inputs outside the conformance corpus), TLC at the constants run
(T-0045-29), the prover and its backends with no certificate checked (T-0045-31; the Isabelle backend is unused), the
proof checker behind routing (T-0045-14, a trust root since Batch 24) and the build toolchain (T-0045-30) are trust
roots whose soundness the corpus does not examine. The prover's release tag has since been rebuilt upstream, so the
build the results cite is pinned by digest and not re-fetchable from its tag (`tools/TLAPS-PIN`).

### 1.12 Legibility residuals

The archive does not exist (T-0045-7; `mechanism/` G9): evidence bytes are retained by the appraising node alone, so a
Contested revocation's attribution cites evidence one node holds (I40). Denials reach the round topic and the bounded
`after` companion, and are still erasable with the topic (CR-7). Workspaces are not replicated, so a `Submit` is
checkable only where its drafts were written. Erasure (ADR-0006) is unbuilt. Replay is boundary events only
(ADR-0020), and a deployment claiming root-cause capability under TACIP 8.2 would have to say what compensates (CR-38).

---

## 2. The trusted base, row by row: what stands when each fails

ADR-0045 Annex A's residual column, with Annex B's instance, in one table. *Class* is at the archetype; *At the
reference* is what Annex B declares. **An excluded or absent row voids every theorem premised on it** (ADR-0045 §3).

| Row | Component | Class | Residual when it fails as named | At the reference |
|---|---|---|---|---|
| T-0045-1 | The replicas, crash-fault | trust root | A forged admit; the apply-time re-check does not re-run the floor | Three replicas in one process tree, no authentication |
| T-0045-2 | Ed25519, domain-separated | trust root | Cryptanalysis; key theft is T-0045-8 | Pinned in `Cargo.lock` |
| T-0045-3 | The Cedar engine | trust root | Divergence on inputs outside the conformance corpus; D-0030-1 drops the premise | `cedar-policy` 4.13, linked |
| T-0045-4 | The local monotonic clock | delegated | A slow clock stretches `ttl` past `T_persona`; no safety decision reads it | The host's clock |
| T-0045-5 | The round-topic transport | delegated | Availability; topic ACLs are declared and not enforced at the reference (G5 item 46) | `rskafka` or in-memory |
| T-0045-6 | The bundle-tier engines | delegated | Availability; a divergence lifts a narrowing only within the floor | OPA sidecar; WASM fallback |
| T-0045-7 | The archive and plaintext store | delegated | Evidence lost within the horizon, legibility subtracted; a failed erasure is the residual the other way | `archive.jsonl` per replica; no horizon, no audit read path |
| T-0045-8 | The anchor key store | trust root | Capture below the custody threshold | `dev/secrets/` in the clear |
| T-0045-9 | The anchor's key-holders | trust root | **Any floor-conformant rules, issued** (§1.1) | One person |
| T-0045-10 | The resident genesis rules | trust root | The chain's root authority wrong from the start; ADR-0029 A2's review is the check | Dev rules, not genesis rules |
| T-0045-11 | The corpus and its custodian | trust root | Every theorem, if the corpus is not what it says; solo authorship until A2's review | This corpus, pinned; custody (1, 0) |
| T-0045-12 | Break-glass approvers | trust root | A grant within the envelope that should not have been made; bounded by R6 and R7 | The operator; no human process |
| T-0045-13 | The gate runner and its evidence | **excluded** | **Every promotion theorem that assumes gates ran is void** | `GatesPassed` from the operator channel, unsigned |
| T-0045-14 | The proof checker behind routing | trust root | A checker bug or a wrong rule in the signature | `ethos` at `8dc85c4`, CPC signature from cvc5 1.4.0 |
| T-0045-15 | The lineage gate tools | trust root (once ADR-0035 is in force) | An independence pass for a correlated pair; the bound is unreviewed | Not instantiated |
| T-0045-16 | CPU root of trust and firmware | trust root, rung 3 | Side channels and physical access; the "operationally audited" layer | **None; SIMULATED by a test key** |
| T-0045-17 | The independent verifier | trust root, rung 3 | Its own compromise; replacing it is an issuance | **None; SIMULATED by a test key** |
| T-0045-18 | Host firmware and hypervisor | trust root, rung 2 | Alteration after launch undetected by re-attestation | None; rung 2 is a seam |
| T-0045-19 | The host operator and orchestrator | trust root, rung 1 | **Anything**: every host power is an addition at rung 1 | The node's launcher and its process or container backend |
| T-0045-20 | The promoted image, runtime and profile | trust root, rungs 1–3 | A guest that is not what its profile says | The demo guest; every rung-1 profile declares a failure |
| T-0045-21 | Inference attestation | trust root, reserved | Conformance admits on a self-report; no theorem cites it yet | None |
| T-0045-22 | The host at rung 0 | excluded | Every containment premise void: `Mediated`, always | Every rung-0 seat |
| T-0045-23 | A native tool under `Invoke` | excluded | Hermeticity void for it; its principal `Mediated` | Every Build tool is native |
| T-0045-24 | A Run tool's declared channel | excluded (pending A2: delegated to T-0045-25) | Channel fidelity has no owner in force; every Run containment theorem conditional on this row | Declared in bundle data and node config, not checked to agree (G9 item 84) |
| T-0045-25 | The tool host | trust root | The envelope collapses if it runs other than the allowlisted binary | `toolhost.rs`; Wasm tools for Run, pending A8 |
| T-0045-26 | Decoding conformance | trust root at rung 3; excluded below | An admit on a self-reported distribution | None admits |
| T-0045-27 | The bundle signer | trust root | Unbounded within the floor; never above it | A dev key, custody (1, 0), signing as a script step |
| T-0045-28 | The implementation as a refinement | trust root | **Every theorem at once**, on every path no test reaches (§1.6) | Trace harness, stage one |
| T-0045-29 | TLC at the constants run | trust root | A mutation or witness result that does not generalize; TLC's soundness unexamined | `tla2tools.jar` 1.7.4, tracked |
| T-0045-30 | The build toolchain | trust root | An admit the source would refuse, inserted below it; no reproducible build | One developer's toolchain |
| T-0045-31 | The prover and its backends | trust root | A theorem taken as proved that is not; no certificate checked | `tlapm` at `7824dab`, pinned by digest (`tools/TLAPS-PIN`); its tag has since been rebuilt |

**Read as an inventory** (ADR-0045 Annex B; `spec/theorem-premise-binding.md`, last column): at the reference,
`ContainedMeansConfined`, `ContestedStopped`, effect exclusivity and `PromotionMeetsIssuedQuorum` are **void**;
`ReachIsBounded` is declared and not enforced; `NoAdmitWithoutLiveObserver`, `UnreadBounded`, `UnreadEffectsBounded`
and `NoEffectWithoutLiveObserver` hold **modulo the collusion gap**; everything else, the lease, the fence,
revocation, composition, the rules floor, the bootstrap pair, seats, any-of, Run's counters and seal, holds of the
modules and, on tested paths, of the code.

---

## 3. Assumptions of use (ToO §13), and whether the reference meets them

| # | Assumption | At the reference | Residual if unmet |
|---|---|---|---|
| A1 | Effect exclusivity enforced by an attested profile at rung ≥ 1 | **Not met**: rung 1 with a failing P3, rung 3 simulated | Every containment theorem void (§1.2) |
| A2 | Every allowlisted tool is hermetic | **Not met** for Build (native tools, T-0045-23); built for Run tools as Wasm, pending A2 and A8 | One tool with a socket collapses the envelope |
| A3 | Key-holders honest at the capture threshold | Declared trivially: threshold 1, one holder | §1.1 |
| A4 | Grant seats review independently | **Not met**: no independence table (G18), A2.2 unbuilt | Unanimity multiplies signatures, not judgment |
| A5 | A trained, authorized human present for break-glass, quarantine release and `D` | **Not met**: the operator is a socket; no human process | HITL and HOTL degrade to unattended operation |
| A6 | Trusted time for intervals that preserve authority | **Not met**; R8 pending; `T_persona` on a local clock (item 62) | Those intervals stretch under a slow clock |
| A7 | The deployment declares its degeneracies | **In part**: Annex B is the trusted-base half; no deployment declaration under ADR-0023 §6 is written (item 64) | The theorem inventory is unfounded except as Annex B computes it |
| A8 | Confirmation-required records cited as author-ratified | Met in the narrative; this document complies | Overstatement in anything published |
| A9 | Replicas not compromised, authenticated to one another | **Not met**: unauthenticated (§1.7) | Forged admits |
| A10 | Each effect class declares `T_irrev`, and `W + L + D < T_irrev` | **Not met**: no effect class enumerated, `L` unmeasured (§5) | HOTL has no budget |
| A11 | The lineage-independence criterion in force with θ set at training scale | **Not met**: ADR-0035 Proposed, θ unset, criterion in no shipped rules | `Contained` has no members whatever the rung |
| A12 | Every Run Thinker's cell Observer keeps up | Enforced by coupling, with an e2e fixture as the Observer | A stall, which is the intended direction |
| A13 | The cell Observer is not colluding | **Uncovered** (§1.3) | Detection fails open |
| A14 | The deployment declares its trusted base under ADR-0045 | **Met**: Annex B, behind the code at A7 and A8 (G9 §2.6) | An undeclared row is false |

---

## 4. What is not measured (MEASURE 1.1's non-measurement declaration; MEASURE 3.2)

| Quantity | Role | State |
|---|---|---|
| `L`, detection latency | The term the oversight placement argument turns on (ADR-0032 §4) | Unmeasured; no Observer exists to measure |
| `D`, human response budget | Same budget | Undeclared; no human process (A5) |
| `W`, propagation window | Same budget | Order-of-magnitude placeholder, ~1 s at the archetype |
| `T_obs`, `K`, Run's `R` | Coupling constants (ADR-0039, ADR-0042) | Placeholders; the `slm/` rehearsal rig could measure `T_obs` and `K` today (CR-36) |
| `T_persona` | Re-attestation cadence bound (ADR-0031 A2) | One hour, a placeholder; read at the reference |
| θ<sub>exact</sub>, θ<sub>near</sub>, θ<sub>gen</sub> and the two others | The independence criterion's thresholds (ADR-0035) | Unset; first measurements exist in the 09.28 rehearsal and were not adopted |
| Observer false-negative rate; time-to-bypass | Detection quality; security evaluation (MEASURE 2.4, 2.7) | Unmeasured; no adversarial exercise has been run |
| The correlator's detection function | What correlated Observers would be caught by | Does not exist (item 43) |
| Floor fitness | Whether the floor is the right floor (MEASURE 2.13) | No gate, no owner, open since G1 |

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
| Run `Actuate` on a declared channel | The declared target, over the tool host | **The class the budget exists for**; set per target, from the physical process | Undeclared |
| Run `Report` | The round topic | As Build `Emit` | Undeclared |

The reference's effect classes are these five and no others. No deployment has declared a `T_irrev` for any of them,
so the HOTL posture ToO §2.6 argues for Run has, at the reference, no budget behind it.

---

## 6. For an acquirer or a user: the plain statement

**What you get, at the reference, today.** A control plane in which every agent and human acts through one credential,
the lease, granted by consensus and ended by expiry, revocation or an epoch fence without one; in which authority
changes only by a unanimous promotion or an anchor issuance bounded by a rules floor; in which every admitted effect
and every denial is ordered and recorded; in which the policy tier can only refuse; and in which an absent Observer
stalls its agent. Each of those is a proved invariant of a module and a tested behaviour of the code.

**What you do not get, today.** Confinement. No principal is `Contained`; every one is `Mediated`, which means the
mechanism attributes and authorizes its actions and does not bound its effects. An agent that can reach a shell, a
socket or a filesystem outside the launcher is outside the guarantee, and the mechanism will not know. Detection
cannot tell an honest Observer from a colluding one. Gate evidence is asserted. The numbers are placeholders. The
proofs are of the design, not of the binary, and the design, the proofs, the code and this statement were written and
checked by one person and one assistant, with no second reader.

**What would change this statement**, in the order the 10.02 review puts them: a reviewer who is not the author; a
P3-passing image under a declared profile; ADR-0034 A2 and ADR-0033 A7 and A8 ratified after review; ADR-0035 in
force with measured thresholds; real rung-3 hardware behind T-0045-16 and 17; the correlator's function; measured
`L`, `T_obs` and `K`; a declared `T_irrev` per Run target; replica authentication; a signed gate runner; R8 and the
break-glass coupling decided.

---

## 7. What this document discharges, and what it does not

- **Discharges, as a document:** MANAGE 1.4 (residual risk documented for acquirers and users); MEASURE 2.6's third
  clause (residual within tolerance: the tolerance is the deployment's, and §1 to §5 are what it is measured
  against); MEASURE 1.1's non-measurement declaration (§4); GOVERN 4.2's documentation half (§2); TACIP 1.3.4's
  evidence package, in the form of a pointer to the manifests, results files and this statement; the *form* of A10's
  `T_irrev` declaration (§5).
- **Does not discharge:** any number. The custody threshold, `T_irrev` per class and the coupling constants are a
  deployment's to declare, and this document records that none has. It is not a review (MEASURE 1.3) and it does not
  make the corpus less self-attested; it makes the self-attestation legible in one place.
- **How it moves.** A derived document is frozen. When the state of record moves, a new statement is written against
  the new checkpoint and this one is marked superseded in `derived/README.md`. The next checkpoint's §8 ("What G10
  does not claim") and this document should agree; where they do not, the checkpoint wins.
