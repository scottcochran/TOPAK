# TOPAK — Genesis Checkpoint G9

**2026.10.02** · genesis custodian: Scott, (1, 0) · supersedes G8 (`98f83acf84fabe26`) as the state of record · narrative: revision 12 of the Theory of Operation (`narrative/theory-of-operation.md`, `1d6c3ed55d168fcb`, written against G8 at `44846b8`) stands, **not revised at G9**; where it and this checkpoint disagree, this document wins (§7, item 79)

**What G9 is.** The state of record, as G8 was: what each record says, what was ratified and by whom, what is owed,
and what is open. It is the first checkpoint at which the reference issues a lease above rung 0.

**What changed at G9.** One batch was ratified: **Batch 26, ADR-0046 E1**, which says `RulesFloorBase.tla` is live and
not frozen. Everything else since G8 is drafted, built and checked, and **nothing else is ratified**. The reference
gained **the launcher in the node** that ADR-0036 §6 describes (ADR-0033 A7, pending): a `launch` operator request
starts a guest from a registered, promoted profile, appraises it, grants to itself at the seat's declared rung and
bridges the guest's actions, with the appraisal re-checked at apply on every replica. **Rung 1 is real**, on a host
process or ADR-0036 §4's container; **rung 3 is SIMULATED**, under test keys standing in for T-0045-16 and T-0045-17;
rung 2 is a seam. The Run profile was drafted as **ADR-0034 A2** (pending, C2 and C4), and the reference built its half
(ADR-0033 A8, pending): Run tools hosted as Wasm modules whose only network capability is their declared target, and a
Run profile's P4 checked at apply. Under `spec/`, ADR-0034 finding 6's successor module (`Confinement_A1`) and a Run
module (`RunConfinement`) are checked and proved, and the trace harness reads every recorded state against the
abstract confinement invariants. After G8's cut, Theory of Operation revision 12 and the glossary were revised
against G8, and the diagrams redrawn. **`Contained` has members only in a SIMULATED run under a test-issued criterion,
which is a witness and not a claim; no real principal is `Contained`.** The bootstrap trigger is still unmet, and
remains optional.

---

## 1. Ratification record

All by the genesis custodian under ADR-0029 §2.

| Batch | Date | Contents | Notes |
|---|---|---|---|
| **26 · An erratum** | 10.02 | **ADR-0046 E1** | §4's sentence that ADR-0026 froze `RulesFloorBase.tla` is struck: the module is the live definition of the floor, and changes with R8; the digest names the version `Anchor_proof` and `BreakGlass_proof` were made against, and a change makes both stale under `spec/proof-sync.sh`. Erratum-class: no decision text, nothing to confirm |

### 1.1 Record status at G9

| Status | Count | Records |
|---|---|---|
| Accepted (genesis) | 18 | As at G8 |
| Accepted (genesis) · confirmation required | 22 | As at G8 |
| Proposed | 3 | 0005, 0035, 0036; and ADR-0042 §6 |
| Superseded | 1 | 0008, by 0038 |
| Tombstone | 1 | 0011 |
| Reserved, no file | 1 | 0014 |

45 record files, numbered to 0046, as at G8.

**Four pending amendments**, up from one:

| Record | Amendment | Kind | Waits on |
|---|---|---|---|
| 0026 | A1 (R8, the break-glass TTL) | decision text | Four conditions, none met (§7, item 8) |
| 0033 | **A7**, the launcher in the node | addendum to §7 | ADR-0036's ratification (§7, item 81) |
| 0033 | **A8**, Run's tools held to their channel | addendum to §7 | ADR-0034 A2 and ADR-0042 §6 (§7, item 80) |
| 0034 | **A2**, the Run profile | decision text, marked inline and not applied; C2, C4 | Review; ADR-0042 §6 with it (§7, item 80) |

### 1.2 What is ratified in part, or with a scoped marking

Unchanged from G8. **Three more texts are drafted by the assistant and pending**: ADR-0034 A2, and ADR-0033 A7 and A8.
Each marks its choices as the drafter's. A2 holds three that need review before anything rests on them: P4 for Run
realized as Wasm modules with one network capability; the Run root delivered over the channel rather than mounted;
the protocol on a declared target recorded and not enforced.

**Decided for the reference, not in a record.** On 2026.10.02 the custodian accepted six recommendations of
`derived/topak-contain-wrapper-design-2026.10.02.md` §8, which the reference now carries as PROVISIONAL tags: the
declared rung is per seat; the attestation is kept beside the lease, not in it; a profile is promoted as a one-file
workspace; the criterion is in force exactly when the issued rules set it; only a signed rung-3 statement may order a
Contested revocation; and a reference value is withdrawn by revoking the profile digest. None is a decision of record
(§7, item 85).

---

## 2. The floors as ratified

### 2.1 The rules floor

Unchanged since G6 in force: **R1, R2, R5, R6, R7, R9**; R3 and R4 withdrawn; **R8** pending. `RulesFloorBase.tla` is
the floor's live definition, not frozen (ADR-0046 E1); when R8 changes it, the two proofs that extend it go stale and
need successors. The ADR-0026 §6 rerun is still owed (§7, item 39).

### 2.2 The policy floor

**Unchanged since G7, in text and in evidence.** No gate run since 2026.10.01.

### 2.3 Confinement

**In force as at G8.** At the reference, for the first time, a lease is issued above rung 0 (ADR-0033 A7, pending):
- **Rung 1**: the node launches a guest, appraises it by its own assertion against the profile's reference values,
  and grants; the bridge holds the session, so no token exists for a launched lease. The only rung-1 profiles are a
  host process, which declares P1 to P3 `fail`, and ADR-0036 §4's container, which declares P3 `fail`. Every rung-1
  principal is `Mediated` by its profile.
- **Rung 3, SIMULATED**: a platform key measures the launch and signs reports; a verifier key signs Attested or
  Contested; the session key binds every action, checked at apply. A rogue launch is Contested and its principal
  revoked; an unreachable verifier grants nothing; an epoch fence voids a pending appraisal. **`contained = true` is
  reached here only, under a criterion the test issues.**
- **Rung 2**: a seam; `apply_grant` refuses it.

**`Confinement_A1.tla`**, ADR-0034 finding 6's successor (`Evidence` reads no measurement at rung 0), is checked at
rungs 0 to 3 in 24 TLC rows and proved, 503 obligations: `Safe` holds at every rung, `M_HOST` breaks rungs 1 and 2 and
changes nothing at 0 and 3, `NeverContainedEffect` holds at rung 0 and is violated at 1 and 3, and the rung-0 row that
reached Contested under `M_HOST` in `Confinement.tla` now holds. `Confinement.tla` and its proof are unchanged.

### 2.4 The LTRO

Unchanged since G7.

### 2.5 Run

**ADR-0042 §6 stays Proposed.** Its condition at B20, a Run profile and an owner for channel fidelity, now has a
draft: **ADR-0034 A2** (pending) writes the Run profile with P4 replaced by channel fidelity, names the tool host's
Wasm runtime as the owner, and adds D-0034-5 (a native tool behind an egress filter) and D-0034-6 (native and
unfiltered, the reference before A8). Its condition (ii) is met in `spec/`: **`RunConfinement.tla`**, 13 TLC rows and
its two invariants proved, 116 obligations. Its condition (iii) is built (ADR-0033 A8, pending): Run profiles
register; a Run tool runs as a Wasm module that can reach only its declared target; an `Actuate` under a Run profile
that says P4 passes names only such a tool, refused otherwise at decide and at apply. Until A2 and §6 are ratified,
**Run principals are `Mediated` by the records**, whatever the reference computes.

### 2.6 The trusted base

**In force**, thirty-one rows, unchanged in the record. **At the reference**, Annex B's line "T-0045-16 to 21: none;
every lease is rung 0" no longer matches the code: T-0045-19 and T-0045-20 have a rung-1 instance (the node's launcher
and its backends), and T-0045-16 and T-0045-17 are played by test keys in the simulated runs only. Annex B moves with
A7's dependent entries. T-0045-24's change from excluded to delegated is owed to an ADR-0045 amendment on A2's
ratification. **The binding table** gained, pending A7 and A2: the four confinement rows' columns at the reference
(`NoSilentDowngrade` and `FreshAppraisal` hold; `ContainedMeansConfined` and `ContestedStopped` are void for a real
deployment), the trace row's refinement check, and a row for `RunConfinement`'s two invariants. `spec/inventory.py`
computes the trusted-base half of the inventory from the table and Annex A for a declared deployment, and prints the
parameter and gap premises for a reader to judge.

### 2.7 Bundle signing, 2.8 the proof-carrying gate

Unchanged since G7.

### 2.9 The proofs

**Fifteen proof modules**, up from thirteen: `Confinement_A1_proof.tla` (Confinement_proof with one case split
changed, so that rung 0 joins rung 1 under the low-rung invariant) and `RunConfinement_proof.tla`. 3,036
obligations, every one proved. `spec/proof-sync.sh` reports every proof in sync, and gives a reason for each module
without one, `ConfinementRefinement.tla` among them: it is a set of predicates over replayed trace states, not a
specification.

---

## 3. Verified artifacts

G8's artifacts keep their digests. New since G8:

| Artifact | SHA-256 (16) | Records | Result |
|---|---|---|---|
| **The reference at `c536e21`**: the launcher in the node | manifest `SHA256SUMS-REF-2026.10.02` (`eba3405b03882c04`, 82 entries) | ADR-0033 A7 (pending) | 96 tests; trace validation `spec/Mechanism-trace-results-2026.10.02.txt` (`24d08cda7f1aa108`), 57 traces, 642 steps, every step matching |
| **The reference at `c534a42`**: Run's tools held to their channel | manifest `SHA256SUMS-REF-2026.10.02b` (`8fa797e317120e54`, 84 entries) | ADR-0033 A8 (pending) | 103 tests; trace validation `spec/Mechanism-trace-results-2026.10.02b.txt` (`d1495a11462b7912`), 62 traces, 709 steps, every step matching and every state keeping `ConfinementRefinement.tla`'s invariants |
| **`spec/Confinement_A1.tla`** and its proof | `715b1c291771c527`; results `Confinement_A1-results-2026.10.02.txt`, `Confinement_A1-proof-results-2026.10.02.txt` | ADR-0034 finding 6; A7 | 24 rows as stated (§2.3); 503 obligations |
| **`spec/RunConfinement.tla`** and its proof | `d0c4aa37934b78b5`; results `RunConfinement-results-2026.10.02.txt` (`76203ee65a85e58f`), `RunConfinement-proof-results-2026.10.02.txt` (`f454ba1badf1cd34`) | ADR-0034 A2 condition (ii) | 13 rows: both invariants hold, and under D-0034-5; `M_CHANNEL`, `M_NATIVE` and `M_FILTER` break them as stated; five witnesses violated. 116 obligations |
| **`spec/ConfinementRefinement.tla`** | `27e47bf343d0794d` | A7 | The abstract invariants read on every traced state; a negative control (a broken invariant) fires |
| **`spec/Mechanism.tla`** | in the manifest | A7, A8 | Gains the appraisal, the session proof, `Contested`, `ProfileRegister`, the `contained` set, channel fidelity; `IsNone` made type-agnostic |
| **`derived/topak-contain-wrapper-design-2026.10.02.md`** | `5972e7ba47f5a937` | A7 | The design, frozen; answers the 28 items of `topak-containment-features-2026.10.01.md` |

**Frozen from G9 on**, as G8's are: the two new modules, their proof modules, and their four results files.
`Confinement.tla` and its proof stay frozen; `Confinement_A1.tla` succeeds the first, not the second.

**Results the drafting did not anticipate**, since G8:
1. **Canonical JSON was not canonical in any build that links the floor.** `cedar-policy-core` turns on `serde_json`'s
   `preserve_order`, so every crate in that build kept insertion order; each binary agreed with itself, and the first
   separately built signer, the guest, disagreed. Fixed in `topak-core`; no pinned digest moved.
2. **A launch measurement cannot cover the profile digest that names it.** ADR-0034 §2 has the rung-3 measurement
   cover the profile digest, and P7 has the profile carry the expected measurement. The simulator measures the parts
   and leaves the profile out (§7, item 82).
3. **`Mechanism.tla` could not test an absent value that might be a number**: TLC refuses `\in STRING` on an integer,
   and no trace had read a promoted candidate's `promotedAt` until a profile was registered.
4. **A Build profile could confine a Run seat.** Neither grant nor launch compared domains; the lookup's Mediated
   verdict was the only guard. Found by the custodian's question, closed before A7's commit, with a model condition
   whose removal a negative control shows.
5. **Finding 6's successor needed its proof changed in one case split**, not unchanged as the drafter first wrote:
   the one step that expands `Evidence` split on `Declared = 1`.
6. **A Run profile's P4 can be enforced where Build's is not.** The reference holds Run tools to their channel and
   does not yet hold Build tools to Wasm under a P4-pass Build profile (§7, item 83).

**What these checks are.** As at G8, and: the reference's rung-3 runs are SIMULATED; `contained = true` in them is a
witness that the lookup is reachable, not a confinement claim. The refinement check reads the code's states against
abstract invariants on every tested path; it does not cover a path no test takes, and it cannot check
`ContainedMeansConfined`, which is about the image the host actually ran.

---

## 4. Genesis debt ledger (ADR-0029 §7)

**Confirmation-required count: 22 records**, as at G8. ADR-0034 A2 would carry C2 and C4 on a record already marked
with both.

| Record | Criterion | What the first quorum has to review |
|---|---|---|
| As at G8 | as at G8 | Unchanged. ADR-0046 gains E1 (Batch 26), erratum-class, which adds nothing to review |

**Bootstrap specification: partial**, as at G8.

**Debts no confirmation repays.** Those of G2 to G8 stand. G9 adds: **three pending texts and the code under them are
the same hand's**, drafted, built, checked, mutation-tested, proved and regenerated by the assistant in one day, with
no second reader; and **six choices of the reference were accepted in conversation**, not by ratification (§1.2).

---

## 5. Conventions carried at G9

G2 to G8's conventions stand. Added since G8:

- **SIMULATED is said wherever it applies.** A trust root played by test keys is marked on every surface that shows a
  lease resting on it, and a result reached under it is a witness, not a claim. A simulated key counts only if an
  anchor issuance puts it in the rules.
- **A pending amendment to an accepted record is marked inline and not applied**, site by site, as ADR-0039 A1 was;
  ADR-0034 A2 is the second.
- **A dated results file cited by digest is never regenerated in place.** A later run of the same day takes a suffix
  (`-2026.10.02b`).
- **Trace validation checks two things**: that the code agrees with the operational model at every step, and that
  every state keeps the abstract confinement invariants.
- **Every unproved module states why**, in `spec/proof-sync.sh`, which fails on a module with no proof and no reason.

---

## 6. Records changed after their own ratification

Since G8:

| Record | Change | Why |
|---|---|---|
| 0046 | E1 (Batch 26) | `RulesFloorBase.tla` is live, not frozen |
| 0033 | A7, A8 drafted, pending | §7 gains two addenda: the launcher in the node; Run's tools held to their channel |
| 0034 | A2 drafted, pending | The Run profile, marked inline at five sites and not applied |

---

## 7. Open list at G9

**G8's seventy-eight items, as they stand.**

| # | Item | At G9 |
|---|---|---|
| 1 | **The sandbox gap** | **Narrowed at the reference, pending A7**: a rung-1 launcher on a process or container, rung 3 simulated, rung 2 a seam. No guest passes P3 (item 36), so no real principal is `Contained` |
| 2 | **Floor fitness** | Open, unowned |
| 3 | The clock model | Discharged (G3) |
| 4 | ADR-0021 | Discharged (G6) |
| 5 | **ADR-0005** | Proposed, unchanged |
| 6 | **The ADR-0017 supersession** | Unwritten |
| 7 | **The archetype-evolution record** | Unwritten. The binding table was revised again (§2.6), pending A7 and A2 |
| 8 | **R8** | Drafted, pending; four conditions unmet |
| 9 | The per-class floor question | ADR-0014, reserved |
| 10 | **Re-genesis migration** | Open |
| 11 | **Custody** | (1, 0), as at G8 |
| 12 | **Derived documents** | **Discharged in part**; one added since G8 and indexed; item 77 closed with this cut |
| 13 | Run's alphabet | Discharged (G6) |
| 14 | **The ToO** | **Revision 12 written after G8's cut**, against G8 (`44846b8`). This checkpoint wins where it says every lease the reference issues is rung 0 (item 79) |
| 15 | Solver trust | Discharged (G7) |
| 16 | The TCB declaration record | Discharged (G6) |
| 17 | **Decoder–alphabet compatibility** | Open |
| 18 | **Bundle signing** | Discharged in the record and at the reference; item 67 |
| 19 | The attestation-rung record | Discharged (G4) |
| 20 | **The provenance independence criterion** | ADR-0035, Proposed. The reference reads it as `Rules.criterion` set (I39); no shipped rules set it |
| 21 | **Persona expiry** | Discharged; the clock residual is item 62 |
| 22 | **Lifting a revocation** | Open |
| 23 | Replica authentication | Sorted at G6; the mitigation is unbuilt |
| 24 | **Finding 9**, proposer retry | Open |
| 25 | **The genesis floor text and S**, DRAFT | Open |
| 26 | **The Run profile** | **Drafted** as ADR-0034 A2, pending (item 80) |
| 27 | **The verifier key in issued rules** | Discharged; **now read** at the reference at every rung-3 grant, renewal and Contested entry (A7, pending) |
| 28 | **Evidence and lineage retention** | **In part**: evidence bytes kept by the appraising node by digest (I40); the archive is open |
| 29 | **Platform TCB updates; accelerator attestation** | The design record recommends a targeted revocation by profile digest, with the raised floor a new profile, and the reference tests it; ADR-0034's obligation is open until a record decides it. Accelerator attestation open |
| 30 | **θ values** | Open |
| 31 | The ADR-0024 amendment | Discharged (G5) |
| 32 | ADR-0035 finding 1 of ADR-0036 | Discharged (G6) |
| 33 | **The best-practice review of ADR-0035's bound** | Open |
| 34 | **ADR-0036's ratification run** | Open. The node's tests rehearse its §7 refusals on the demo guest; the run on `slm/serve`'s image is unrun |
| 35 | **The launcher in `topak-node`** | **Built**, pending ADR-0033 A7 and ADR-0036 |
| 36 | **A P3-passing image** | Open. The demo guest is compiled; a static build on an empty image is the step |
| 37 | The ToO, revision 8 | Discharged |
| 38 | **The 09.26 accounting's discrepancies** | As at G6 |
| 39 | **ADR-0026 §6 rerun** with A2.2 and A2.3 | Open |
| 40 | **A *properties lost* field** | Open |
| 41 | **A seat-registration record** | Open |
| 42 | **ADR-0037 §9's occupant steps** | Open |
| 43 | **The correlator's detection function** | Open |
| 44 | **Sequence numbers on denials; the correlator's store** | Open |
| 45 | **A scripted cell Observer; the scripted Run cell** | **In part**: a launched Run principal plays a round with a scripted Observer heartbeat, in a test |
| 46 | **`W(p)` as an ACL; the gate-side `K < R` check; A2.2 in the reference** | Open |
| 47 | **Measured values** for `T_obs`, `K`, `T_persona`, Run's `R` | Open |
| 48 | **The quarantine hold** | Open |
| 49 | **Break-glass under a dead Observer** | Open |
| 50 | The ADR-0017 supersession | Open (item 6) |
| 51 | **Delegation; attenuation; honeypot validation** | Open |
| 52 | **ADR-0033's live smoke run** | Open; not rerun since 09.25 |
| 53 | ADR-0045's ratification | Discharged (G7) |
| 54 | ADR-0030 A1 | Discharged (G7) |
| 55 | Batch 17's reference debts | Discharged (G7) |
| 56 | **The refinement chain, stages 2 and 3**; the reproducible build | Open. Stage one widens to launch, appraise, grant and revoke, with the abstract invariants checked on every state (A7, A8) |
| 57 | **Gate evidence signed**; T-0045-13 changes class | Open |
| 58 | **ADR-0042 §6, the Run profile, channel fidelity's owner** | **Drafted and built, pending**: A2 names the owner; A8 builds it; `RunConfinement` checked and proved (item 80) |
| 59 | **The allowlist entry's schema** | Open; a Run tool's channel is now declared twice (item 84) |
| 60 | **A record that lays out rounds** | Open |
| 61 | **ADR-0042's remainders** | Open |
| 62 | **`T_persona` on a local clock** | Open |
| 63 | The glossary | Revised against G8 after its cut (`44846b8`) |
| 64 | **ADR-0023 §6b amendment; a deployment declaration template** | Open; the reference declares rung per seat meanwhile (item 85) |
| 65 | The repository reorganization | Discharged (G7) |
| 66 | **An ADR-0029 criterion for assisted drafting** | Open; four ratified texts rest on it, and three pending ones (A2, A7, A8) |
| 67 | **Signing at promotion; a custody row for the bundle key** | Open |
| 68 | **The checker carried in a release** | Open |
| 69 | **What `holds°` rests on** | Open |
| 70 | Theory of Operation, revision 11 | Discharged (G8) |
| 71 | The register's header | **Discharged** with this cut: it names G9 and revision 12 |
| 72 | Theory of Operation revision 12 and the glossary, against G8 | **Discharged**: `44846b8` (item 79 for its tags) |
| 73 | **The prover pinned for reproducibility** | Open |
| 74 | **The SMT backends' proofs checked by Isabelle** | Open |
| 75 | **Model checking at practical constants** | Open |
| 76 | **The diagrams are not measured** | Open; redrawn since G8 (`44846b8`, `4b417ba`) and still excluded |
| 77 | `topak-containment-features-2026.10.01.md` in the derived index | **Discharged** with this cut |
| 78 | **One driver per TLC results file** | In part: the two new modules' results regenerate from scripts |

**New since G8.**

| # | Item | Where it sits |
|---|---|---|
| 79 | **Tags, and the narrative against this checkpoint.** `ToO-rev12` and `glossary-2026.10.02`, which revision 12 and the glossary cite, do not exist; nor do `REF-2026.10.02` (`c536e21`) and `REF-2026.10.02b` (`c534a42`). Revision 13 and the glossary against G9: the reference's first leases above rung 0, the launcher, SIMULATED, the Run profile draft | `checkpoints/README.md` (tags); `narrative/` |
| 80 | **Review and ratification of ADR-0034 A2 with ADR-0042 §6**, then ADR-0033 A8. A2's three drafter's choices (§1.2). On ratification: ADR-0045 amended for T-0045-24 (excluded → delegated) and T-0045-25; ADR-0040 §3's "who checks"; ADR-0022 §6 discharged for Run | ADR-0034 A2; ADR-0033 A8 |
| 81 | **ADR-0036's ratification, then ADR-0033 A7.** On A7's: dependent entries in ADR-0034 (the reference launcher; finding 6's successor), ADR-0025 A1 (the key read), ADR-0045 Annex B (T-0045-17, 19, 20) | ADR-0036; ADR-0033 A7 |
| 82 | **ADR-0034 §2 against P7**: a measurement cannot cover the profile digest that names it | ADR-0034; `mechanism/` finding 16 |
| 83 | **Build's P4 at the reference**: a Build profile that says P4 passes is not held to Wasm tools for `Invoke` | `mechanism/` I43 |
| 84 | **A Run tool's channel declared twice**, in the node's config and in bundle data, and not checked to agree; the Wasm tool interface is a core module, not A2's component; the protocol on a declared target is unenforced | `mechanism/` G19, I44 |
| 85 | **Six choices of the reference accepted in conversation** (§1.2), owed to records: the declared rung to the deployment declaration (item 64), withdrawal and the Contested rule to ADR-0034 | `mechanism/` I37 to I42 |

**Not on this list, deliberately:** bootstrap itself, as at G2 to G8.

---

## 8. What G9 does not claim

- **Nothing here is independently reviewed.** Batch 26 was ratified on the day; the pending texts, the code under
  them, the modules, the proofs and the runs are one hand's.
- **No real principal is `Contained`.** Rung 1 trusts the host by construction and every rung-1 profile declares a
  failure; rung 3 is SIMULATED; the criterion is in force in no shipped rules. `contained = true` appears only in a
  simulated test under a criterion the test issues.
- **Run is not confined by any record.** ADR-0034 A2 and ADR-0042 §6 are not in force, so Run principals are
  `Mediated`, whatever the reference's lookup computes under them.
- **Fifteen modules' invariants are proved, and nothing about the running reference is.** The refinement check covers
  tested paths; T-0045-28 stands.
- **The reference is not the mechanism** (ADR-0033 §1). Its two new trees are cited by pending addenda only.
- **The prover is trusted as written**, as TLC and the checker are.
- **The values are placeholders**, and **detection still fails open against a colluding Observer**.
- **Bundles are signed under a throwaway key**; gate evidence is still an operator's assertion.
- **The trusted base is in force and its binding table is a draft**, revised again, pending.
- **The narrative is a revision behind** on the reference (item 79).
- **No floor is ratified, no deployment conforms, and no deployment declaration has been written.**
- **The corpus is not closed.**

---

## 9. Manifest

`SHA256SUMS-G9` · 392 entries, cut from commit `66b8e55` plus this checkpoint and the edits that go with it.

As at G2 to G8, the manifest's own digest cannot appear inside the file it measures, and this checkpoint is an entry
in it; both are recorded where they are cut, in the commit that adds them, and `manifests/index.tsv` names that
commit so `tools/verify-manifest.sh --all` checks this manifest at the tree it measured.

| Area | Entries |
|---|---|
| `decisions/` | 45 records |
| `checkpoints/` | 10 — the v1 corpus manifest, G1 to G9 |
| `narrative/` | 11 — as at G8 |
| `derived/` | 21 dated artifacts |
| `spec/` | 102 — G8's 86, and sixteen more: three modules (`Confinement_A1`, `ConfinementRefinement`, `RunConfinement`), two proof modules and their two results files, four dated TLC results (two trace-validation runs, `Confinement_A1`, `RunConfinement`), two dated row files, two run scripts and `inventory.py` |
| `floor/` | 132 — as at G7 |
| `process/` | 6 logs |
| `manifests/` | 11 — ten reference manifests and the `slm/` tree manifest |
| `tools/` | 54 — as at G8 |

The reference trees are measured by `SHA256SUMS-REF-2026.09.24` through `-2026.10.02b`; the rehearsal tree by
`SHA256SUMS-SLM-2026.09.28`; this manifest measures those eleven in turn. No reference manifest is cut at G9: since
`c534a42`, `mechanism/` changed in two files, the pin file (ADR-0033's pin, with A8) and the register (A8's path fix and
the header, item 71).

Verify from the repository root, at this checkpoint's commit:

```sh
shasum -a 256 -c manifests/SHA256SUMS-G9 | grep -c ': OK$'                  # expect 392
tools/verify-manifest.sh --all                                              # every manifest at the commit it measured
```

**`SHA256SUMS-REF-2026.10.02b` fails two entries at today's tree, and should**: it measures `c534a42`, and the pin file
and the register moved after it. It verifies 84 of 84 there. **`SHA256SUMS-REF-2026.10.02` fails 18 entries at today's
tree**, for A8's changes and the same two; it verifies 82 of 82 at `c536e21`.

**`SHA256SUMS-G8` fails 14 entries at today's tree**, by construction: ADR-0033 (A7, A8), ADR-0034 (A2) and ADR-0046
(E1); the Theory of Operation and glossary revised against G8; and under `spec/`, `Mechanism.tla`, the binding table,
the method note, `proof-sync.sh`, `trace2tla.py` and four run scripts. It verifies 372 of 372 at `1151832`.

The manifest excludes what `manifests/EXCLUDE` lists, as at G8. `diagrams/` stays excluded (item 76). `mechanism/`,
`policies/` and `slm/` are measured by their tree manifests, not directly.
