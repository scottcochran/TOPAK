# The contain wrapper: a design for the launcher in the node, rung-generic, with rung 1 real and rung 3 simulated

**Date:** 2026.10.02 · **Against:** corpus at `25b9b23` · **Answers:** `derived/topak-containment-features-2026.10.01.md`
(the 28 items, cited below as F1 to F28) · **Carries out, when built:** ADR-0036 §6 (Proposed) and, in part, ADR-0034's
obligation for the reference · **Status:** design. Nothing here is a decision. §8 lists six questions for the custodian,
each with a recommended answer. §10 is a draft ADR-0033 addendum that stays a draft until the code it describes exists.

---

## 1. What is being built, and what is not

The reference has the lease's `confinement: [digest, rung]` field (`topak-core/src/lease.rs` L10-16). It has
`check_renewal`'s equal-rung rule (L64-86, ADR-0031 A1, `M_LOWER`), and it has `spec/Confinement.tla` and
`spec/Lease_A1.tla`. Several things are missing:

- **No launcher.** There is no guest, appraisal, nonce or session key.
- **No reader of `verifier_keys`.** `Rules` carries them (`rules.rs` L92-96, register I36), and nothing reads them.
- **`is_contained()` is a constant.** It is `rung >= 1 && PROVENANCE_CRITERION_DEFINED`, and the constant is `false`
  (L46-52).
- **The session is a bearer token.** The token is 32 random bytes held in one replica's memory and never replicated
  (`topak-node/src/mechanism.rs` L102, L690; I14).

**The design builds one pipeline for every rung: launch → appraise → grant → bridge** (ADR-0036 §2). It has three
kinds of backend behind it:

| Backend | Rung | Status in this design | Why |
|---|---|---|---|
| `ProcessBackend` | 1 | Built. Runs in CI | Exercises the pipeline on any host. Its profile declares P1 and P2 `fail`. That is honest, because rung 1 says only that the launcher asserts the launch |
| `DockerBackend` | 1 | Built. Tests gated on `TOPAK_DOCKER_TESTS=1` | ADR-0036 §4's guest. It ports `slm/serve/run.sh`'s flags from the profile's typed `launch` part |
| `SimCvmBackend` with `SimVerifier` | 3 | Built behind cargo feature `sim`. **Simulated** | Every rung-3 path runs on a macOS host: nonce, bound session key, signed verdict, Contested, fence |
| `MeasuredBootBackend` | 2 | Seam: types only | Firecracker or Kata with a TPM quote. That is the rung-2 record's problem (ADR-0036 §6) |
| `SnpBackend`, `TdxBackend`, `HttpVerifier` | 3 | Seam: types only | Needs hardware and an independent verifier (F20, T-0045-16, T-0045-17) |

**What a simulated rung 3 is.** It is a test double for two trust roots, T-0045-16 (the CPU vendor's root) and
T-0045-17 (the verifier). Both are played by keys the test generates. A lease the simulator attests reports
`contained = true` only when every other conjunct of ADR-0034 §4 holds, including a criterion set in the test's issued
rules. That `true` makes no confinement claim. **It is a witness that the lookup is reachable and that each refusal
fires.** It plays the role `NeverContainedEffect` plays in TLC, at the level of running code. Every place that shows a
simulated verdict prints `SIMULATED`.

**What is out of scope**, and stays an external obligation:

- F19 needs a P3-passing image, a Wasm tool host and vsock.
- F20 needs real SNP or TDX evidence.
- F21 needs accelerator attestation.
- F22 needs the Run profile.
- F24 needs the deployment declaration.
- F25 needs the Persona premises.

§9 says which items the code realizes and which it does not.

---

## 2. Where the pieces live

### 2.1 `topak-core`: new `src/confine.rs`, deterministic, no I/O

Everything a replica checks at apply lives here. That keeps ADR-0033 §4's rule that apply reads no clock and no file.

- **`Profile`** is ADR-0036 §1's schema:
  - `image`, a content digest;
  - `launch`, which is opaque to core and typed in `topak-contain`;
  - `channel`;
  - `persona.model_json_sha256`, the same name `slm/serve/profile-host-rung0.json` uses;
  - `reference { launch_measurement, min_tcb }`, which are P7's two values;
  - `clauses`, mapping each of P1 to P7 to `{ verdict: pass | fail | vacuous, why }`;
  - `subtractions`;
  - `domain`, which defaults to Build.

  `check_well_formed(rung)` refuses a profile in three cases: a clause is missing, a `fail` has no subtraction, or
  the rung is ≥ 1 and either P7 value is absent. `meets_p3_p5(alphabet)` reads P4 `vacuous` as meeting P4 only when
  the alphabet has no `Invoke`, which is D-0034-3 as a check.
- **Two digests.** The profile digest is `Digest::of(file bytes)`. ADR-0036 §1 says "the digest of the file", so the
  digest is taken over the raw bytes, whitespace included. The **profile artifact** is the single-file workspace digest
  of `profile.json`, which is what promotion keys on (§8, decision 3). That needs `workspace_digest_of` moved into
  core from `mechanism.rs` L553-566, where it is computed today.
- **`NonceInput { epoch, index, principal, round }`** and its digest (F8, ADR-0034 §3.1). `report_data(nonce,
  session_key)` is the value the evidence must bind. No clock is read, so ADR-0032's trusted-time requirement does not
  arise.
- **`Appraised { Attested, Unattestable, Contested }`.** The name `Verdict` is taken: it is promotion's
  `{Grant, Deny}` (`types.rs` L81).
- **`AppraisalStatement`** is what a verifier signs, under the purpose `appraisal`. Its fields are `nonce`, `profile`,
  `persona`, `rung`, `verdict`, `evidence`, `session_key?`, `measurement?`, `tcb?` and `platform`, where `platform`
  is one of `launcher`, `sim-snp`, `snp` or `tdx`. **`Appraisal { statement, instance, signature? }`** wraps it.
  Signatures go through the existing `authentic::valid_signers` (`authentic.rs` L48), as issuances and break-glass
  approvals already do.
- **`Attestation`** is the replicated record a grant leaves behind: `verdict`, `n_epoch`, `nonce_index`, `instance`,
  `session_key?`, `evidence` and `verified_by?`.
- **`SessionProof { ctr, op, sig }`** is signed under the purpose `agent-op` over `(fence, epoch, ctr, op digest)`.
  At rungs 2 and 3 it replaces I14's bearer token (F12, ADR-0034 §3.5).
- **`Containment { contained, because }`** is the result of the lookup. `because` names each conjunct that failed,
  so a `Mediated` verdict comes with its reasons (ADR-0036's "derived, not empty").

Changes to existing core files:

- **`lease.rs`.** `PROVENANCE_CRITERION_DEFINED` and `is_contained()` are deleted.
- **`State`** gains `profiles`, the registered profiles by digest, and `contested`, mapping each Contested principal
  to its evidence digest. `contested` is the state `ContestedStopped` quantifies over, and `Entry::Revoke` alone does
  not record it.
- **`LeaseRecord`** gains `attestation` and `session_ctr`.
- **`State::contained(fence)`** replaces the constant (§4).

### 2.2 New crate `crates/topak-contain`: I/O, tokio, anyhow, feature `sim`

| Item | Shape |
|---|---|
| `Backend` | `rung()`, `kind()`, `launch(LaunchRequest) -> LaunchedGuest { instance, io, launched_image, handle }` |
| `GuestHandle` | `evidence(nonce)`, `alive()`, `destroy()`, for P6. Backends kill their guest on drop |
| `GuestIo` | Line-delimited JSON over `AsyncRead`/`AsyncWrite`. Today that is the guest's stdio; vsock is a backend swap. The guest's first line is `GuestHello { persona, family, params, root, session_key? }` (ADR-0036 §2.1). Host to guest: `Attest { nonce }`, `Response`, `Shutdown`. Guest to host: `Evidence`, `Op` (rung 1, token-less, ADR-0036 §2.4), `SignedOp { proof, op }` (rungs 2–3) |
| `Evidence` | `LauncherAssertion`, `SimSnp`; seams for `Snp`, `Tdx`, `TpmQuote`; one reserved accelerator field (T-0045-21) |
| `LauncherAssertion` | The rung-1 appraiser. It compares the launched image and `hello.persona` with P7 and returns Attested or Unattestable. It can never return Contested, because rung 1 has no measurement (`NeverContested` at rung 1) |
| `Verifier` | The rung-3 appraiser, T-0045-17. It returns `Result<Appraisal, VerifierError>`, with errors `Unreachable`, `EndorsementExpired` and `Malformed`. **Every error is Unattestable**, which is PC/EC (F14) |
| `bridge` | Forwards guest ops to the node through an `ActSink`, and responses back to the guest. At rung 1 it is the only holder of the session. Ends with `GuestClosed`, `Shutdown` or `ProtocolError` |
| `sim::SimPlatform` | Stands in for the PSP. Its measurement is `H(binary, profile digest, persona digest)`, and it signs a `SimReport { measurement, report_data, tcb, platform: "sim-snp" }` |
| `sim::SimCvmBackend` | A process launch with a `SimPlatform`. It can do a rogue launch (a different binary gives a different measurement) and a tamper (the "hardware" kills the guest) |
| `sim::SimVerifier` | Checks the report's signature, the measurement and TCB against the profile's P7, and `report_data`, then signs Attested or Contested. Its test knobs are `reachable`, `min_tcb_override`, and a `gate` that holds an appraisal so the stale-nonce test is deterministic |
| `bin/topak-demo-guest` | A scripted occupant. It writes its hello, with an ed25519 session key at rung ≥ 2, answers `Attest`, and plays `Read → Draft → Submit`, signing each op with an increasing counter. CI needs it because `serve.py` has no `--occupant` mode yet |

### 2.3 `topak-node`: the launch path

- **New operator ops.**
  - `OperatorOp::Launch { principal, seat, profile, bundle, alphabet, ttl_ms, round, role }`. **It takes no persona
    argument**: the persona comes from the profile, so the lease, the profile and the statement name one digest (F26).
  - `OperatorOp::RegisterProfile { profile }`, carrying the raw bytes.
  - CLI conveniences: `topak op launch`, `topak op register-profile`, and `topak profile-digest <file>`, which prints
    the file digest and the artifact digest.
- **Config.** `contain { backends: rung → BackendConfig, verifier, evidence_dir }`. The kinds `sim-cvm` and `sim` are
  refused at load unless the binary is built with `sim`.
- **`launch.rs`** runs one launch:
  1. **Refuse** if the profile is unregistered or unpromoted, if the principal, Persona or profile is revoked, or if
     the seat's declared rung differs from the backend's.
  2. **Launch** the guest and read its hello under a timeout. A guest that writes no hello is Unattestable, and the
     guest is destroyed.
  3. **Derive the nonce** from `(epoch, last applied index, principal, round)`.
  4. **Ask the guest for evidence** and appraise it, with `LauncherAssertion` at rung 1 or the `Verifier` at rung 3.
  5. **Act on the verdict:**
     - **Unattestable:** destroy the guest, write a `security` log line and store the evidence locally. Nothing is
       ordered: a refusal needs no quorum.
     - **Contested:** propose `Entry::Contested` and destroy the guest.
     - **Attested:** propose `Entry::Grant { req, appraisal }`. If the epoch moved after the nonce was derived, the
       launch task drops the appraisal before proposing. Apply would refuse it anyway.
  6. **On `LeaseGranted`,** register the guest under its fence and spawn the bridge and the renewal driver.
- **Renewal driver** (F13). It fires at TTL/2 on the local monotonic clock. ADR-0032 §2 permits this because a missed
  renewal only subtracts. The driver sends a fresh nonce to **the same instance**, then acts on the result:
  - Attested proposes `Renew { req, appraisal }`.
  - Unattestable stops renewing, and the lease lapses through the existing `sweep_expired`. The principal loses its
    lease, not its containment (F11).
  - Contested proposes `Entry::Contested`.

  No interval re-attests a running guest. The driver re-measures the launch at an event.
- **End of round.** Guest EOF proposes `EndRound` attributed `launcher: guest closed channel`, under F2. When
  `apply_committed` sees a fence end, for any reason, it destroys that fence's guest (P6).
- **The session.** `Mechanism::act_bound(fence, op, proof)` builds the session from replicated state, and a launched
  lease mints no token. `AgentRequest` (`topak-mcp/src/proto.rs`) gains an optional `session`. `token` takes a serde
  default so existing callers do not change.

---

## 3. What the log carries, and what every replica re-checks

```rust
Entry::Grant           { id, req, #[serde(default)] appraisal: Option<Appraisal> }
Entry::Renew           { id, req, #[serde(default)] appraisal: Option<Appraisal> }
Entry::Contested       { id, appraisal: Appraisal, attribution: String }   // F2
Entry::ProfileRegister { id, profile: String }                             // raw bytes
AdmitRecord            { .., #[serde(default)] session: Option<SessionProof> }
```

The grant entry carries what F9 lists:

- profile digest and rung, in `req.confinement`;
- verdict, nonce, evidence digest and session public key, in `appraisal.statement`.

**One replica appraises, and every replica re-checks at apply.** This is ADR-0033 §4's apply-time re-check with the
conditions ADR-0034 §3.2 adds. The order below is fixed, because `Mechanism.tla`'s `ApplyGrant` mirrors it.

**`apply_grant`** (`state.rs` L763-841). After the existing checks:

1. **Declared rung.** `req.confinement.rung` must equal the seat's declared rung (§4). Without this check, an
   Unattestable principal could be granted at rung 0. That is `M_DOWNGRADE`.
2. **At rung ≥ 1, an appraisal is required.** All of the following must hold:
   - The verdict is Attested.
   - The statement's profile equals `req.confinement.digest` and is registered, hence promoted (F7).
   - The statement's Persona equals the request's Persona, which equals the profile's Persona (F26).
   - The nonce names this principal and round.
   - **`nonce.epoch` is the current epoch** (FreshEpoch, `M_STALE`), and `nonce.index` is below this entry's index.
   - At rung ≥ 2, a session key is present.
   - **At rung 3, the signature verifies under a key in the issued rules' `verifier_keys`.** That is the first read of
     the field (F15, ADR-0025 §1(f)).
3. **Rung 2 is refused** ("not implemented"). That is its seam.
4. **At rung 0, a profile may be named** (ADR-0036 R1), and the appraisal must be absent.

**`apply_renew`** (L863-896). A lease with an attestation renews only on an Attested appraisal that meets three
conditions:

- `nonce.epoch` is current and `nonce.index ≥ fence`. The nonce is fresh relative to this lease and can never equal
  the grant's nonce.
- The instance and the session key are unchanged (SameGuest).
- At rung 3, the signature is valid.

`check_renewal` still refuses any change of rung (`M_LOWER`, `M_RENEWLOW`). A token-only `Renew` of an attested lease
is refused, because every renewal re-attests (F11, F13).

**`apply_admit`** (L898-980). For a lease with a session key, the admit must carry a `SessionProof` that verifies
under that key with `ctr > session_ctr`, and the counter then advances. `spec/theorem-premise-binding.md` records that
`ContainedMeansConfined` rests on the generation binding **at `Act`**, not on `SameGuest` at grant. So the check lives
at apply, where every replica runs it. The Rust mirror of `M_UNBOUND` targets this check.

- **Residual for the register.** The proof's binding to the `Admitted` summary is checked at decide, on crash-fault
  replicas (I1). Apply checks that the attested session signed this counter, not which operation it signed.

**`Entry::Contested`** is refused in two cases:

- below rung 2, because rung 1 cannot produce Contested;
- at rung 3 without a valid verifier signature. The operator's plain `Revoke` stays available in either case.

On success it applies `apply_revoke(Principal(p))` and records `contested[p] = evidence`. **The target is the
principal: never the profile, never the Persona** (ADR-0034 §3.7, F10). The revocation is permanent and attributed
under F2.

**`Entry::ProfileRegister`** registers a profile only when all of these hold:

- The profile parses and is well-formed.
- Its domain is Build. A Run profile is refused while ADR-0042 §6 is Proposed (F22).
- Its artifact digest names a promoted candidate (`promotion.rs` L26, `promoted_at`).

**Pending appraisals are node-local.** They are the interval between appraise and commit, held by the launch task. The
fence reaches them at apply through the nonce epoch. The correspondence with `Confinement.tla` is:

| `Confinement.tla` | This design |
|---|---|
| `guest[p].gen` | `Appraisal.instance`. At rungs 2–3 it is also the session key |
| `pending[p].nEpoch`, `lease[p].nEpoch` | `nonce.epoch`, `Attestation.n_epoch` |
| `FreshEpoch` at `Grant` | the nonce-epoch check in `apply_grant` and `apply_renew` |
| `SameGuest` at `Grant` | instance equality at renew |
| `lease.gen = guest.gen` at `Act` | the session proof at `apply_admit` |
| `contested` | `State.contested` |

**The attestation lives on `LeaseRecord`, not on `Lease`.** ADR-0031 §1 closes the lease's field set (`lease.rs`
L20-21), and a new field would be a C1 amendment (§8, decision 2). Because `LeaseRecord` is replicated, the session
key is too, so every replica can verify a `SessionProof`. Today's token map cannot do that.

---

## 4. `Contained(p)` is a lookup

ADR-0034 §4 sets the conjuncts. F16 asks that each be a check of state and that nothing semantic enter. Three fields
are added to the issued rules (`rules.rs`), each `#[serde(default)]`.

| Field | Meaning | Provisional? |
|---|---|---|
| `SeatDecl.rung: u8` | The seat's declared confinement rung. Well-formed only if ≤ 3, and rung 3 requires `verifier_keys` to be non-empty | Yes, `declared-rung`: ADR-0023's deployment declaration is unwritten (§8, decision 1) |
| `Rules.personas: Digest → Provenance` | ADR-0017's axis: `InHousePretrain`, `InHouseFinetune`, `AttestedExternal` or `AssertedExternal`. The first two are in-house | No |
| `Rules.criterion: Option<Criterion { record, independence_table, floor_values }>` | ADR-0035's criterion is in force exactly when an anchor issuance sets this field (§8, decision 4). The node warns if it is set while `floor/genesis-values.json`'s θ values are null | No |

**`State::contained(fence)`** returns `contained = true` only if every conjunct below holds. Otherwise it lists each
conjunct that failed:

1. the lease is live;
2. its rung is ≥ 1 and equals the seat's declared rung;
3. its attestation is Attested;
4. its profile is registered and `meets_p3_p5` for the lease's alphabet;
5. its Persona is in-house under `Rules.personas`;
6. `Rules.criterion` is set;
7. its seat's domain is Build. Run is `Mediated` at every rung until the Run profile exists (F22).

`status()` (`mechanism.rs` L746) and the replies to Grant and Launch (L694) call it.

**A discrepancy, noted rather than resolved.** F16 says "live lease at rung 3". Ratified ADR-0034 §4 says rung ≥ 1 at
the declared rung. The design follows ADR-0034. At the archetype the declared rung is 3, and the two agree.

---

## 5. Item 17, decided as a recommendation

**When a vendor revokes a firmware version, the profile's minimum platform TCB version moves by promotion under P7.**
The changed value is a new profile with a new digest and a new promotion. **Live leases on the old profile are fenced
by a targeted revocation of the old profile digest:** `Revoke { target: Confinement(old) }`. That entry exists today
(`state.rs` L121-135, L846-860). It ends every live lease that names the digest and bars any later grant on it,
permanently.

- **No new entry kind is needed.** The decision is that this tool is the one to use, and a test shows it fencing a
  live attested lease.
- **The fleet fence is the wrong tool.** `EpochIncrement` would end every lease in the fleet, which takes away more
  than the withdrawal requires.
- **A Contested revocation is the wrong tool too.** It is about a principal, and here no principal did anything.

There is one interaction to note. A renewal on the old profile after the new minimum is promoted is still appraised
against the old profile's P7, because the profile is the reference value. The revocation by digest is what stops it.
The simulator's `min_tcb_override` exercises the other path: a verifier that has learned of the revocation independently
returns Unattestable at the next renewal, and the lease lapses.

---

## 6. Tests

### 6.1 `topak-core/tests/confinement.rs`

Each test is paired with the `Confinement.tla` mutation it refuses, under the discipline of `tests/mutations.rs`.

| Test | Mirrors |
|---|---|
| A grant on a Contested verdict is refused. `Contested` revokes the principal, a later grant is refused, and `contested` records it | `M_CONTESTED`; `ContestedStopped` |
| A session proof under another guest's key is refused at apply; so is a replayed counter, and so is a renewal from a different instance | `M_UNBOUND` |
| Appraise, then `EpochIncrement`, then grant: refused. A renewal nonce below the fence: refused | `M_STALE`; `FreshAppraisal` |
| A rung-0 grant on a seat declared rung 3 is refused, and so is an Unattestable grant | `M_DOWNGRADE`; `NoSilentDowngrade` |
| `contained` is false for each conjunct that fails alone (P3 `fail`; P4 `vacuous` with `Invoke`; an external Persona; no criterion; a Run seat), and true only when all hold | `M_PROFILE` |
| An Unattestable renewal is refused, and so is a renewal at a lower rung | `M_RENEWLOW`; `M_LOWER` |
| A rung-1 `Contested` entry is refused | `NeverContested` at rung 1 |
| Refused: an unpromoted profile; a key not in the issued rules; a nonce for another principal or round | Extra: `M_UNPROMOTED`, sim segregation, `M_NONCE` |
| `Revoke(Confinement)` ends a live attested lease and bars the digest | F17 |

`tests/mutations.rs`'s `grant_req` fixture (L64-76) grants at rung 1 with no appraisal. It moves to rung 0.
`rung_zero_is_never_contained…` (L261) moves to `State::contained`.

### 6.2 `topak-node/tests/contain.rs`

These tests run three in-process replicas, as `e2e.rs` does, in a separate file so `e2e.rs` stays intact. Tests 4 to 8
are F28's ratification run, simulated.

1. **Rung-1 honest round** on `ProcessBackend`. `Read → Draft → Submit`, then the guest is destroyed. The lease
   reports `contained = false`, with P3 and the criterion as reasons. This is ADR-0036 §7.
2. **ADR-0036 §7's refusals.** A wrong image digest is Unattestable and no grant is ordered. A guest that exits before
   its hello gets no grant. A second process at the agent socket with neither token nor proof is refused. A launch of
   an unpromoted profile is refused before anything starts.
3. **Docker rung 1.** Test 1 again with real containers, gated on `TOPAK_DOCKER_TESTS=1`.
4. **Simulated rung-3 honest round.** `contained = true` when the test's rules set `criterion`, and `false` on an
   otherwise identical cluster without it.
5. **Rogue image.** The verdict is Contested, the principal is revoked, and re-launching that principal is refused.
6. **Unreachable verifier.** No grant is made, while a lease already live keeps admitting until renewal (PC/EC).
7. **A rung-0 principal beside a rung-3 one.** It is `contained = false`, so `Contained` is not everyone.
8. **Stale nonce.** Hold the verifier's gate, fence the epoch, then release the gate. The grant is refused at apply.
9. **Another guest's session.** A proof from guest B against guest A's fence is denied, and so is a replayed proof.
10. **Renewal.** A renewal keeps the rung and the instance. The lease lapses, with no `Renew` entry, when the verifier
    is down or the minimum TCB is raised.
11. **Every host power subtracts** (F23, ADR-0034 §5).
    - Killing the guest ends the round.
    - A tamper ends the round.
    - Withholding the channel lets the lease expire.
    - A `LyingBackend` at rung 1, which reports the image it was asked for while launching another, **is** Attested.
      That is the `M_HOST` witness at running-code level: at rung 1, T-0045-19 is load-bearing.
12. **Profile withdrawal.** `Revoke(Confinement)` ends a live simulated lease (§5).

---

## 7. The trace harness and the spec (F3, F4, F5)

- **`trace.rs`.**
  - `oracle()` (L46-58) gains `sigOk` for a verifier signature and `proofOk` for a session proof. They follow the
    pattern of the three facts it already takes on trust: issuance validity, the break-glass signature and the params
    digest.
  - `project_entry` gains the appraisal tuple and the `Contested` and `ProfileRegister` kinds.
  - `project_state` gains several items:
    - the seat's `rung`;
    - `personas`;
    - `criterionInForce`;
    - for each lease, `attested`, `gen`, `nEpoch`, `sessionCtr` and **`contained`**, so that the model recomputes the
      lookup and the lookup itself is trace-validated;
    - `profiles` and `contested`.

  **Every change to the projection lands in the same commit as the matching `spec/Mechanism.tla` change.** TLC's
  record equality fails on a field the model does not have. `Mechanism.tla` is re-pinned.
- **`spec/Confinement_A1.tla`**, the successor F3 asks for. It carries finding 6's fix,
  `Evidence(p) == IF Declared <= 1 THEN asked ELSE boot`, and a rung-0 row. `Safe` holds at every rung, `M_HOST`
  breaks rungs 1 and 2 and changes nothing at 3, and `NeverContainedEffect` is violated at rung 3 and holds at rung 0.
  A per-principal `Declared` lets it model F28's rung-0 principal beside a rung-3 one. The proof module adapts
  `Confinement_proof.tla`, and the runner gains rows and a results file.
- **`spec/ConfinementRefinement.tla`.** It maps each projected trace state onto `Confinement_A1`'s `lease`, `revoked`
  and `contested`. On every step it checks `NoSilentDowngrade`, `ContestedStopped` and `FreshAppraisal`. That is
  T-0045-28 stage one, extended to launch, appraise, grant and revoke (F4).
  - `ContainedMeansConfined` cannot be checked from mechanism traces, because the mechanism does not see the image the
    host actually ran. The simulator could emit that as a ground-truth oracle, but this design does not require it.
- **`spec/theorem-premise-binding.md`.** The rung-3 premise rows for `ContainedMeansConfined`, `ContestedStopped` and
  `FreshAppraisal` are filled with T-0045-16, 17, 20 and 25. The reference's verdict reads "holds under SIMULATED
  T-0045-16/17", and a script computes an archetype deployment's inventory from the table instead of stating it (F5).

---

## 8. Six questions for the custodian

| # | Question | Recommended | Why |
|---|---|---|---|
| 1 | Is the declared rung per seat or per deployment? | **Per seat**, `SeatDecl.rung`, provisional until ADR-0023's declaration is written | F28 and ADR-0036 §7 both run a rung-0 principal beside a higher one |
| 2 | Is the attestation a lease field or kept beside the lease? | **Beside it**, on `LeaseRecord` | Avoids a C1 amendment to ADR-0031 §1's closed field set. Nothing a principal presents changes |
| 3 | What does promotion key a profile on? | **The single-file workspace digest of `profile.json`**, provisional | Promotion keys candidates on workspace digests (`mechanism.rs` L553-566). The profile digest stays the file's own |
| 4 | What does "criterion in force" mean? | **`Rules.criterion` is set** by an anchor issuance | F16: a check of the issued rules, nothing semantic |
| 5 | Who may order `Contested`? | **Only at rung ≥ 2, and at rung 3 only under a verifier signature.** Plain `Revoke` stays available | `NeverContested` at rung 1; a Contested entry is a claim about evidence |
| 6 | How is reference-value withdrawal done (F17)? | **`Revoke(Confinement(old digest))`**, with the new minimum TCB as a new profile | §5 |

---

## 9. The 28 items, accounted for

| Item | Realized by | Class |
|---|---|---|
| F1 | Appraisal-at-grant path, each condition paired with a refused mutation (§6.1); `Confinement_A1` | Code and spec |
| F2 | The binding table cites T-0045-16, 17, 20, 21 and 25 by theorem; `status` prints the rows a `contained` rests on | Spec and record |
| F3 | `Confinement_A1.tla` | Spec |
| F4 | `trace.rs`, `Mechanism.tla`, `ConfinementRefinement.tla` | Code and spec |
| F5 | `theorem-premise-binding.md` rows, and the inventory script | Spec |
| F6 | `OperatorOp::Launch`, `launch.rs` | Code |
| F7 | `ProfileRegister`, the promoted-artifact check at apply | Code |
| F8 | `NonceInput`, the epoch and index checks at apply | Code |
| F9 | `Grant.appraisal`, apply-time signature and epoch re-check | Code |
| F10 | Unattestable is never ordered; `Entry::Contested` targets the principal | Code |
| F11 | `check_renewal` (exists), the seat's declared rung, the renewal appraisal | Code |
| F12 | `SessionProof`, checked at decide and at apply | Code, rungs 2–3, simulated |
| F13 | Renewal driver with a fresh nonce at the same instance; the nonce-epoch fence | Code |
| F14 | `VerifierError` maps to Unattestable; e2e test 6 | Code |
| F15 | `apply_grant`, `apply_renew` and `Contested` read `verifier_keys` | Code |
| F16 | `State::contained`, three rules fields | Code |
| F17 | §5; e2e test 12 | Decision and test |
| F18 | A local evidence store by digest. **Not the archive**: G9 stays open, and an F2 attribution to a Contested principal cites evidence only this node holds | Partial |
| F19 | Not realized. Needs a P3-passing image, a Wasm tool host (P4), vsock (P1). The simulated profile *declares* the clauses passing, and a declaration is not a build | External |
| F20 | Seams only. The simulator has the evidence's shape, not its substance | External |
| F21 | A reserved field. T-0045-21 stays reserved | External |
| F22 | Run profiles are refused at registration; Run is `Mediated` in the lookup | External |
| F23 | e2e test 11; `Confinement_A1` | Code tests and spec |
| F24 | Not realized. The deployment declaration is a record | External |
| F25 | Not realized. Pre-training on two lineages, and ADR-0035 ratified | External |
| F26 | One Persona digest bound across lease, profile and statement. What the digest covers is a guest-build obligation | Partial |
| F27 | Observer seats launch as their own guests with their own declared rung. Separate devices are a deployment fact | Partial |
| F28 | e2e tests 4–8 as a **simulated** rehearsal. The real run waits on F19, F20 and F25 | Partial |

---

## 10. Build order, risks, and the draft addendum

### 10.1 Phases

| Phase | Work | Verified by |
|---|---|---|
| 1 | Core schema: `confine.rs`, `workspace_digest_of` moved, rules fields, `profiles`, `ProfileRegister`, `State::contained`, fixture migration, projection and `Mechanism.tla` together | Existing suite green; every trace MATCH |
| 2 | Apply path: appraisals on Grant and Renew, `Contested`, admit session proof, declared rung; drift pins for ADR-0036 and the `Confinement*` modules | `tests/confinement.rs`; trace MATCH |
| 3 | `topak-contain`: traits, guest protocol, Process and Docker backends, `LauncherAssertion`, bridge, demo guest | Crate tests against a fake `ActSink` |
| 4 | Node wiring: `Launch`, `RegisterProfile`, `launch.rs`, renewal driver, destroy-on-end, `act_bound`, proto `session` | e2e tests 1–3 and 11 |
| 5 | `sim`: platform, CVM backend, verifier, signed ops | e2e tests 4–10 and 12 |
| 6 | `Confinement_A1` and its proof, `ConfinementRefinement`, binding rows, results files; register entries (I36 struck; G1, G2 and I14 amended; tags `declared-rung`, `profile-artifact`, `evidence-retention`, `session-proof`); `mechanism/README`; the addendum below, with its manifest | TLC and TLAPS results; trace results; `shasum -c` |

### 10.2 Risks

- **Determinism at apply.** ed25519 verification is deterministic, and apply already verifies issuance and break-glass
  signatures. Profiles parse with serde and contain no floats. Apply reads no clock and no file.
- **Simulator segregation.** Five guards keep the simulator out of a real deployment:
  - The `sim` feature is enabled only from dev-dependencies.
  - Sim kinds are refused at config load without it. Feature unification under `cargo test` makes this runtime
    refusal the real guard.
  - Simulated statements say `platform: "sim-snp"`, and every surface prints SIMULATED.
  - A sim key is accepted only if an anchor issuance puts it in `verifier_keys`.
  - `dev-init.sh` never issues one unless asked.
- **No vsock on macOS.** At rung 1 the channel is the stdio pipe, which is ADR-0036 §2's shape. `GuestIo` is generic
  over the stream.
- **Docker is not a VM boundary on a Linux host.** The profile's `launch` part must say `runsc` there (ADR-0036,
  Consequences).
- **A launching replica that crashes** orphans its guest. The lease expires, which is a subtraction. Backends kill
  guests on drop.
- **Fixture churn.** Literal `SeatDecl`, `Rules`, `AdmitRecord` and `LeaseRecord` constructions in tests and in
  `mechanism.rs` change. The generated `spec/Trace_*.tla` files regenerate.

### 10.3 Draft: ADR-0033 addendum ⟨A7⟩, the launcher in the node

> *Draft, 2026.10.02. Not inserted. Its artifacts line, test count and trace numbers are filled when the code exists.*
>
> **Artifacts:** `mechanism/` and `policies/` at commit `⟨tbd⟩` · manifest `SHA256SUMS-REF-⟨date⟩` · floor, schema and
> values unchanged · the pin file gains ADR-0036, `spec/Confinement.tla` and `spec/Confinement_A1.tla`, and re-pins
> `spec/Mechanism.tla`.
>
> **What changed.** ADR-0036 §6, carried out. The launch, appraise, grant and bridge steps move into `topak-node` as a
> `launch` operator request, under a new crate `topak-contain`:
>
> | Debt | Record | What the reference does now | Checked by |
> |---|---|---|---|
> | The launcher in the node | ADR-0036 §6 | The node starts the guest from a registered, promoted profile, appraises, grants to itself with the appraisal in the grant entry, and bridges | `contain.rs` 1–3 |
> | Appraisal is part of the grant | ADR-0034 §3.1–3.3 | The nonce comes from the log. Every replica re-checks the verifier signature, the nonce epoch and the profile at apply. Contested revokes the principal | `confinement.rs`, `M_CONTESTED`, `M_STALE`, `M_DOWNGRADE` |
> | The session is the attested guest's | ADR-0034 §3.5, I14 | At rung 1 the bridge is the only holder. At rungs 2–3 a per-admit proof under the attested session key, checked at apply | `confinement.rs` `M_UNBOUND`; `contain.rs` 9 |
> | The verifier key is read | ADR-0025 A1, I36 | Rung-3 grants, renewals and Contested entries verify under `verifier_keys` | `confinement.rs` |
> | `Contained` is a lookup | ADR-0034 §4 | `State::contained` over the declared rung, the attestation, P3–P5, the Persona's provenance and the criterion in the issued rules | `confinement.rs` `M_PROFILE`; `contain.rs` 4, 7 |
>
> **The run.** ⟨n⟩ tests. Trace validation reruns against the changed model, and `ConfinementRefinement.tla` checks
> `NoSilentDowngrade`, `ContestedStopped` and `FreshAppraisal` on every trace.
>
> **What it discharges, and what it does not.** In the record: ADR-0036 §6's step, the first read of `verifier_keys`,
> and I14 for launched leases. **`contained = true` is reached only in a SIMULATED rung-3 run, under test keys standing
> in for T-0045-16 and T-0045-17, and makes no confinement claim.** Rung 1 is real and every principal it launches is
> `Mediated` by its profile. Not discharged:
>
> - rung 2, and real SNP or TDX evidence;
> - a P3-passing image, Wasm tools, vsock (F19);
> - accelerator attestation (T-0045-21);
> - the Run profile;
> - the evidence archive (G9);
> - the deployment declaration;
> - the Persona premises.
>
> Of the refinement chain, stage one widens to launch, appraise, grant and revoke. Stages two and three do not move.
>
> **Confirmation.** Recommended not confirmation-required on its own terms, as at B7 and later: the confinement claim
> belongs to ADR-0034 and ADR-0036, and this addendum states that its `true` is simulated. It precedes ADR-0036's
> ratification as A3 preceded ADR-0040 to ADR-0043. If ADR-0036 changes in ratification, the addendum is revised before
> it is. On ratification, dependent entries go to ADR-0034, ADR-0036 and ADR-0025, and ADR-0045 Annex B's T-0045-17,
> 19 and 20 rows are annotated.
