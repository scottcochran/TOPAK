# TOPAK — Genesis Checkpoint G7

**2026.10.01** · genesis custodian: Scott, (1, 0) · supersedes G6 (`6b6bd0af64f5d7da`) as the state of record · narrative: revision 10 of the Theory of Operation (`narrative/theory-of-operation.md`, tag `ToO-rev10`) stands, **not revised at G7**; where it and this checkpoint disagree, this document wins (§7, item 14)

**What G7 is.** The state of record, as G6 was: what each record says, what was ratified and by whom, what is owed,
and what is open. It is the first checkpoint cut under the 2026.09.30 layout (`checkpoints/README.md` is the map),
and the first whose manifest measures the proof checker's rule signature beside the TLC jar.

**What changed at G7.** G6 froze a corpus whose trusted base was declared in a Proposed record, whose solver was
trusted on every gate run, whose bundles were unsigned at the reference, and whose binding table did not exist. In
one day, three batches. **The trusted base is in force** (ADR-0045, Batch 22, C2 and C4): the admission rule, thirty
rows, the reference's own declaration, and the theorem-to-premise binding table its §3 owed, forty-two rows that
compute which properties hold at the reference and which are void. **Batch 17's reference debts are built** (ADR-0033
A6, Batch 23): `ttl ≤ T_persona` refused at grant and renewal, the two key fields in the issued rules, and a bundle
loaded only under a signature; 61 tests, 22 traces and 168 steps matching the operational model. **The solver is
trusted for nothing** (ADR-0030 A1, Batch 24): every routing `holds` in the gate run of 2026.10.01 carries a proof
that a pinned, independent checker accepted from the query's own declarations and assertions, and three controls
show a lying solver producing a failure and never a `holds`. Two trusted-base rows changed class on the way: the
bundle signer from excluded to a trust root under a dev key, and the solver's refused row to a trust root for the
checker. Between G6 and these batches the repository was reorganized, thirty-three files moved with no byte changed,
and the glossary was revised in place against G6. **Every lease the reference issues is still rung 0. Nothing is
`Contained`.** The bootstrap trigger is still unmet, and remains optional.

---

## 1. Ratification record

All by the genesis custodian under ADR-0029 §2.

| Batch | Date | Contents | Notes |
|---|---|---|---|
| **22 · Trusted base** | 10.01 | **ADR-0045** at R6 (C2, C4) | As drafted and revised six times: R1 what runs is a row; R2 the refinement gap as ADR-0033's debt; R3 the jar's digest; R4 stage 1 of the chain; R5 a citation; R6 the binding table. Its §9 condition met. Dependent entries in 0030, 0033, 0034, 0036, 0037, 0042, 0043. Drafted by the assistant; every drafter's choice settled by ratification |
| **23 · Reference** | 10.01 | 0033 A6 | Batch 17's three reference debts built; dependent entries strike them on 0025, 0031 and 0044; ADR-0045 Annex B's T-0045-27 changes class. ADR-0044's D-0044-1 is no longer the reference's position |
| **24 · The solver** | 10.01 | 0030 A1 | A `holds` counts only with a checked proof. Not confirmation-required on the drafter's reading, unchallenged. The drafter's choice of format and checker resolved by the first run: cvc5's CPC, checked by `ethos` 8dc85c4 against the signature from cvc5 1.4.0. ADR-0045 T-0045-14 rewritten by dependent entry |

### 1.1 Record status at G7

| Status | Count | Records |
|---|---|---|
| Accepted (genesis) | 18 | 0001, 0002, 0004, 0007, 0010, 0012, 0016, 0017, 0018 (in part, §1.2), 0019, 0020, 0022 (in part, §1.2), 0024, 0025, 0026, 0027, 0032, 0033 |
| Accepted (genesis) · confirmation required | **21** | 0003 (for A2 only), 0006, 0009, 0013, 0015, 0021, 0023, 0028, 0029 (for A2 only), 0030, 0031 (C2 for A1 only, beside its C1), 0034, 0037, 0038, 0039, 0040, 0041, 0042 (in part, §1.2), 0043, 0044, **0045** |
| Proposed | 3 | 0005, 0035, 0036; and ADR-0042 §6 |
| Superseded | 1 | 0008, by 0038 |
| Tombstone | 1 | 0011 |
| Reserved, no file | 1 | 0014 |

44 record files, numbered to 0045. 0014 is the only reserved number.

**One pending amendment.** ADR-0026 A1 (R8, the break-glass TTL), drafted 2026.09.24, none of its four conditions
met (§7, item 8). ADR-0030 A1 was ratified in Batch 24. Every other `Pending:` field reads none.

### 1.2 What is ratified in part, or with a scoped marking

Unchanged from G6: ADR-0022 §6 and ADR-0042 §6 are not Accepted; ADR-0018 is reversed in part; ADR-0024 A2 is in
force in the record and in part in the reference (A2.2 is still G18); the four markings scoped to an amendment
stand; ADR-0003 A3 carries none.

**Three records were drafted by the assistant**, at the custodian's request, each marking every choice as the
drafter's, and **all three are now ratified**: ADR-0044 (Batch 17), ADR-0045 (Batch 22) and ADR-0030 A1 (Batch 24).
The custodian settled each by ratifying the text; A1's one open choice, the proof format and the checker, was left
to the first run and the B24 row records what it chose. ADR-0029 still has no criterion for this kind of authorship
(§4; item 66).

---

## 2. The floors as ratified

### 2.1 The rules floor

Unchanged since G6: **R1, R2, R5, R6, R7, R9**; R3 and R4 withdrawn; **R8** pending. The ADR-0026 §6 rerun is still
owed (§7, item 39). The reference now carries `verifier_keys` and `bundle_keys` in the issued rules (ADR-0025 §1 (f),
`mechanism/` I36); the floor is unchanged by them.

### 2.2 The policy floor

**Unchanged since G6 in text, and still DRAFT.** One more gate run, the first with proofs behind it:

| Run | What changed | Policies | Cases | Digests |
|---|---|---|---|---|
| `genesis-gates-results-2026.10.01.txt` (ADR-0030 A1, Batch 24) | Nothing in the floor, the schema or the values. Every solver call goes through `floor/cvc5-checked`; the header names the checker (`ethos` 8dc85c4, binary `4eb41c1f1f9fce88`), the signature (`tools/cpc/`, tree `6d7e8d208d223985`) and the wrapper (`dfe159e9c21a549e`). 81 cedar calls, 56 solver queries, 4 `unsat` each with a checked proof, 49 `sat`, 3 `unknown` from the lying-solver controls, 25 `holds°` decided by cedar without a query. Evidence tree `f8b1196a427a35ed` in `floor/genesis-gates-evidence-2026.10.01/`, reproducible run to run | 17 | 62 | floor `28ec0e4552c6a915`, schema `0ec2fa215eefe136`, values `85ab6fefb66f0316` (as at 09.30) |

**The floor bundle is three files**, as at G5. **Every number in the values file is a placeholder.** `T_persona` is
now read by the reference (ADR-0033 A6, I35) and still measured on the local clock (item 62).

### 2.3 Confinement, 2.4 the LTRO, 2.5 Run

Unchanged in force since G6. ADR-0036 R3 (Proposed) points its §5 rows at ADR-0045 Annex B, T-0045-19 and 20.
**`Contained` still has no members at any rung.**

### 2.6 The trusted base

**In force** (ADR-0045, Batch 22, C2 and C4). The rule, the thirty rows and the reference's declaration are as G6
§2.6 described them at R4, with two more revisions before ratification: R5 a corrected citation, **R6 the binding
table**, `spec/theorem-premise-binding.md`, forty-two rows naming for every checked property the trusted-base rows,
the degeneracy parameters and the declared gaps it rests on, and computing in its last column what holds at the
reference. Two Annex B rows changed class after ratification, each by dependent entry: **T-0045-27** from excluded
to a trust root instantiated by a dev bundle key with custody (1, 0) (B23), and **T-0045-14** from refused to a trust
root for the proof checker, with the solver trusted for nothing (B24). The inventory at the reference is unchanged
in shape: every theorem premised on confinement, gate evidence, hermeticity or channel fidelity is void; the routing
theorem and the gate verdicts now rest on checked proofs, where before they were the solver's assertion.

### 2.7 Bundle signing

**Implemented at the reference** (ADR-0033 A6, Batch 23): `<revision>.sig` beside the tarball, a `Signed` over the
content revision for the purpose `bundle`; `LocalBundles::load_dir` loads only what verifies under the rules'
`bundle_keys`; the sidecar's decision counts only from a verified revision; a grant naming an unverified one is
refused; `build-bundle.sh` signs under a secret and `dev-init.sh` signs a copy under a dev key. Four tests, one of
which renames a tarball with a forged manifest and is refused. Not done: signing at promotion as a pipeline step,
and the custody row for the bundle key (item 67).

### 2.8 The proof-carrying gate

New at G7 (ADR-0030 §5 as amended by A1). `cedar symcc` runs `floor/cvc5-checked` in place of cvc5. The wrapper
keeps every query, runs cvc5 with proof production on, discards the solver's restatement of the query, prefixes the
proof with declarations derived from the query's own text, requires every assumption in the proof to be one of the
query's assertions verbatim, refuses a restatement that disagrees with the query's, and forwards `unsat` only after
`ethos` accepts the proof of `false`; anything else is `unknown`, which cedar reports as a failure. A `refuted` needs
no certificate. The checker is pinned by three digests in the gate header and the signature is tracked and measured
(§9). Two things the checker does not cover, said in the records: a `holds°` is cedar's own term folding with no
query to check, resting on T-0045-3; and the signature's rules are trusted as written by cvc5's authors.

---

## 3. Verified artifacts

G6's artifacts keep their digests except `Mechanism.tla`, which is pinned and not frozen. New since G6:

| Artifact | SHA-256 (16) | Records | Result |
|---|---|---|---|
| **`spec/Mechanism.tla`** | `3bfbc88be6cf7fe7` (was `73e1ceecff13437d`) | ADR-0033 A6; ADR-0045 T-0045-28 | Carries `persona`, the two key sets through `Issue`, and the `ttl` bound at grant and renewal. **Trace validation, 2026.10.01: 22 traces, 168 applied entries, every step matching** (`Mechanism-trace-results-2026.10.01.txt`) |
| **`spec/theorem-premise-binding.md`** | in the manifest | ADR-0045 R6, §3; ADR-0023 §2 | Forty-two rows; the last column is the reference's inventory, revised at B24 for T-0045-14 |
| The floor, one run | `28ec0e4552c6a915` / `0ec2fa215eefe136` / `85ab6fefb66f0316`; evidence tree `f8b1196a427a35ed` | ADR-0030 A1 | §2.2. All gates pass; every solver-backed `holds` is a checked proof |
| **`tools/cpc/`**, the CPC signature | tree `6d7e8d208d223985` over 51 `.eo` files; each in the manifest | ADR-0030 §5; ADR-0045 T-0045-14 | Copied unchanged from cvc5 `cvc5-1.4.0` (`b432cd7`), `proofs/eo/cpc/`. The rules a gate proof is checked against |
| The checker and the wrapper | `ethos` binary `4eb41c1f1f9fce88` (built by `tools/install-ethos.sh`, not tracked); `floor/cvc5-checked` in the manifest | ADR-0030 A1 | Printed in every gate header from 2026.10.01 on |
| Reference, one run | manifest `48f92ab89086adce` (`dacbb0c`, 66 entries) | ADR-0033 A6 | 61 tests across six binaries, up from 55; eighteen files under `mechanism/`, 381 lines, and the model |

**Frozen from G7 on.** Nothing new; `Mechanism.tla` and the binding table move with the code and the records.

**Results the drafting did not anticipate**, since G6:
1. **The checker and the solver do not share a namespace.** cedar names every record constructor after its sort,
   which SMT-LIB allows and Eunoia does not, so the first real gate proof was refused at its datatype declaration.
   The wrapper alpha-renames those constructors in the script the solver sees; the saved query is the original.
2. **One operator differs between SMT-LIB and the signature.** The n-ary `set.insert` is a list application in CPC;
   the wrapper translates it, and the cross-check against the solver's restatement would refuse any other divergence.
3. **The checker's reference mode does not bind.** `ethos --reference` accepted a tampered query, so the wrapper
   does the binding itself: the prelude is derived from the query and every assumption must be an assertion of it.
4. **cedar decides most of the totality gate without the solver.** Every never-errors check on the genesis floor and
   a permit-all under always-allows fold to a constant before any query is sent. Those are `holds°`, 25 of the
   run's 29 `holds`, and they rest on the engine's row, not the checker's. "Every `holds` has a proof" was never
   true of the gate as cedar runs it, and the records now say which `holds` has one.
5. **The trace harness caught a test, not the code** (ADR-0033 A6). The first `ttl` test lowered the bound between
   two log entries, which the model cannot see without an entry; the test was wrong and now keeps the bound constant.
6. **No Alethe proof for the queries' set theory.** cvc5 1.4.0's Alethe output refuses the gate queries, which
   decided the drafter's choice: CPC with cvc5's own checker, independent in code and not in authorship.

**What these checks are.** Unchanged from G6, with one addition: a checked proof certifies that the query's
declarations and assertions entail false under the signature's rules; it does not certify that cedar's encoding of
the floor into that query is faithful, which is T-0045-3's claim and ADR-0030 §3's soundness argument.

---

## 4. Genesis debt ledger (ADR-0029 §7)

**Confirmation-required count: 21 records**, up from 20.

| Record | Criterion | What the first quorum has to review |
|---|---|---|
| 0003 (A2), 0006, 0009, 0013, 0015, 0021, 0023, 0028, 0029 (A2), 0030, 0031, 0034, 0037, 0038, 0039, 0040, 0041, 0042 (§1–§5, §7, §8), 0043, 0044 | as at G6 | Unchanged from G6, except that 0030 now carries A1: the checker as a trust root and the solver trusted for nothing |
| **0045** | C2, C4 | The admission rule in ADR-0015's terms; the three classes and the refusal; that Annex A enumerates what the theorems assume; the reference's declaration and its inventory; the refusal of trusted time; that what runs is a row; the two rows that changed class after ratification; that every drafter's choice was settled by ratification |

**Bootstrap specification: partial.** Unchanged since G5.

**Debts no confirmation repays.** Those of G2 to G6 stand. G7 adds one kind and settles none. **The checker's
authorship**: the proof-rule signature in `tools/cpc/` is cvc5's own formalization of its calculus, trusted as
written, and the wrapper that binds a proof to its query was written by the same hand that wrote the gates on the
same day; the three lying-solver controls test the wrapper's refusals and not the signature's rules. The assisted
drafting of G6 is now three ratified texts, which is where ADR-0029's missing criterion bites (item 66).

---

## 5. Conventions carried at G7

G2 to G6's conventions stand. Added since G6:

- **A manifest is verified at the commit it measured** (`manifests/index.tsv`, `tools/verify-manifest.sh --all`),
  and `manifests/EXCLUDE` states the cut rule once for `tools/cut-manifest.sh`. The index is not itself measured.
- **Frozen files are not edited for a move.** The 2026.09.30 layout map in `checkpoints/README.md` resolves every
  stale path; `tools/check-refs.py` checks the rest.
- **The glossary is revised in place** and measured by the checkpoint cut with it; there are no dated copies from
  2026.09.30 on.
- **A gate `holds` is marked** `holds✓` when every solver query behind it came back as a checked proof and `holds°`
  when cedar needed no query; `holds?` never appears in a passing run.
- **Evidence trees sit beside their results** (`<results>.evidence/`), and the tree digest is printed at the end of
  the results file: that is what joins the gate-evidence digest.
- **A trust root may be pinned by digests printed in a results header** before a release exists to carry them
  (ADR-0045 T-0045-14, T-0045-29).
- **A dependent entry may change an Annex B row's class** when the owing record's ratification instantiates the row
  (B23, B24), with the old text struck and the batch marked inline.

---

## 6. Records changed after their own ratification

Since G6:

| Record | Change | Why |
|---|---|---|
| 0025 | B23 (dependent) | The key-field debt struck |
| 0030 | B22 (dependent); A1, Batch 24 | The engine-divergence obligation struck; the solver |
| 0031 | B23 (dependent) | The `ttl` debt struck |
| 0033 | B22 (dependent); A6, Batch 23 | The refinement debts owned; Batch 17's debts built |
| 0034 | B22 (dependent) | Its §6 rows taken by ADR-0045 |
| 0036 | R3 (Proposed) | Its §5 rows taken by ADR-0045 |
| 0037, 0042, 0043 | B22 (dependent) | Their rows taken by ADR-0045 |
| 0044 | B23 (dependent) | Implemented; D-0044-1 no longer the reference's position |
| 0045 | R5, R6; B22; B23, B24 (dependent) | A citation; the binding table; ratified; two rows change class |

---

## 7. Open list at G7

**G6's sixty-six items, as they stand.**

| # | Item | At G7 |
|---|---|---|
| 1 | **The sandbox gap** | Unchanged |
| 2 | **Floor fitness** | Open, unowned |
| 3 | The clock model | Discharged (G3) |
| 4 | ADR-0021 | Discharged (G6) |
| 5 | **ADR-0005** | Proposed, unchanged |
| 6 | **The ADR-0017 supersession** | Unwritten |
| 7 | **The archetype-evolution record** | Unwritten. The binding table now exists (ADR-0045 R6); its versioning is still this record's |
| 8 | **R8** | Drafted, pending; four conditions unmet |
| 9 | The per-class floor question | ADR-0014, reserved |
| 10 | **Re-genesis migration** | Open |
| 11 | **Custody** | (1, 0). The corpus's own row is T-0045-11, now in force; the dev bundle key is a second (1, 0) custody (item 67) |
| 12 | **Derived documents** | **Discharged in part**: the glossary is revised in place against G6 (`narrative/glossary.md`, tag `glossary-2026.09.30`) and names the three Run names and the trusted base; `derived/README.md` indexes the rest |
| 13 | Run's alphabet | Discharged (G6) |
| 14 | **The ToO** | **Revision 11 owed.** Revision 10 describes ADR-0045 as Proposed, the solver as trusted and bundles as unsigned at the reference; this checkpoint wins on each |
| 15 | **Solver trust** | **Discharged**: ADR-0030 A1, Batch 24 |
| 16 | **The TCB declaration record** | **Discharged**: ADR-0045, Batch 22 |
| 17 | **Decoder–alphabet compatibility** | Open |
| 18 | **Bundle signing** | **Discharged** in the record (G6) and at the reference (ADR-0033 A6); the promotion step and the key's custody row are item 67 |
| 19 | The attestation-rung record | Discharged (G4) |
| 20 | **The provenance independence criterion** | ADR-0035, Proposed at R4 |
| 21 | **Persona expiry** | **Discharged** in the record (G6) and at the reference (ADR-0033 A6, I35); the clock residual is item 62 |
| 22 | **Lifting a revocation** | Open |
| 23 | Replica authentication | Sorted at G6; the mitigation is unbuilt |
| 24 | **Finding 9**, proposer retry | Open |
| 25 | **The genesis floor text and S**, DRAFT | Open; unchanged since 09.29 in text |
| 26 | **The Run profile** | Unwritten |
| 27 | **The verifier key in issued rules** | **Discharged** in the record (G6) and at the reference (ADR-0033 A6, I36); never read, since the reference issues rung 0 only |
| 28 | **Evidence and lineage retention** | Open |
| 29 | **Platform TCB updates; accelerator attestation** | Open |
| 30 | **θ values** | Open |
| 31 | The ADR-0024 amendment | Discharged (G5) |
| 32 | ADR-0035 finding 1 of ADR-0036 | Discharged (G6) |
| 33 | **The best-practice review of ADR-0035's bound** | Open |
| 34 | **ADR-0036's ratification run** | Open |
| 35 | **The launcher in `topak-node`** | Open |
| 36 | **A P3-passing image** | Open |
| 37 | The ToO, revision 8 | Discharged |
| 38 | **The 09.26 accounting's discrepancies** | As at G6 |
| 39 | **ADR-0026 §6 rerun** with A2.2 and A2.3 | Open |
| 40 | **A *properties lost* field** | Open |
| 41 | **A seat-registration record** | Open |
| 42 | **ADR-0037 §9's occupant steps** | Open |
| 43 | **The correlator's detection function** | Open |
| 44 | **Sequence numbers on denials; the correlator's store** | Open |
| 45 | **A scripted cell Observer; the scripted Run cell** | Open |
| 46 | **`W(p)` as an ACL; the gate-side `K < R` check; A2.2 in the reference** | Open |
| 47 | **Measured values** for `T_obs`, `K`, `T_persona`, Run's `R` | Open |
| 48 | **The quarantine hold** | Open |
| 49 | **Break-glass under a dead Observer** | Open |
| 50 | The ADR-0017 supersession | Open (item 6) |
| 51 | **Delegation; attenuation; honeypot validation** | Open |
| 52 | **ADR-0033's live smoke run** | Open; not rerun since 09.25 |
| 53 | ADR-0045's ratification | **Discharged**: Batch 22, with the binding table |
| 54 | ADR-0030 A1 | **Discharged**: Batch 24; `floor/cvc5-checked`, `tools/install-ethos.sh`, `tools/cpc/`, the 10.01 run |
| 55 | Batch 17's reference debts | **Discharged**: ADR-0033 A6, Batch 23; `mechanism/` I34 to I36; G7 of the register retired |
| 56 | **The refinement chain, stages 2 and 3**; the reproducible build | Open; stage 1 rerun at A6 against the changed model |
| 57 | **Gate evidence signed**; T-0045-13 changes class | Open. The evidence now has a tree digest to sign |
| 58 | **ADR-0042 §6, the Run profile, channel fidelity's owner** | Open |
| 59 | **The allowlist entry's schema** | Open (I33) |
| 60 | **A record that lays out rounds** | Open |
| 61 | **ADR-0042's remainders** | Open |
| 62 | **`T_persona` on a local clock** | Open; the bound is now enforced, the interval still drifts |
| 63 | The glossary | **Discharged** (item 12) |
| 64 | **ADR-0023 §6b amendment; a deployment declaration template** | Open |
| 65 | The repository reorganization | **Discharged**: `a372315`, moves only; this is the first cut under it |
| 66 | **An ADR-0029 criterion for assisted drafting** | Open; now three ratified texts rest on it |

**New since G6.**

| # | Item | Where it sits |
|---|---|---|
| 67 | **Signing at promotion as a pipeline step, and a custody row for the bundle key** (today a dev key at (1, 0)) | ADR-0033 A6; ADR-0044 §4; ADR-0045 T-0045-27 |
| 68 | **The checker carried in a release.** T-0045-14 is pinned by three digests in a results header; a mechanism release does not exist to carry them (T-0045-30) | ADR-0030 open obligations; ADR-0045 Annex B |
| 69 | **What `holds°` rests on.** cedar folds the totality gate and the vacuity control without a query; a check of that folding, or a solver query forced for it, would move 25 verdicts onto the checker's row | ADR-0030 §5; `floor/README.md` |
| 70 | **Theory of Operation, revision 11**, against this checkpoint | item 14 |
| 71 | **`mechanism/GAPS-AND-ASSUMPTIONS.md` header** still names G5 as the state of record and revision 9 as narrative; the register's rows are current through I36 | the next ADR-0033 addendum |

**Not on this list, deliberately:** bootstrap itself, as at G2 to G6.

---

## 8. What G7 does not claim

- **Nothing here is independently reviewed.** Every record, run and ratification of 2026.10.01 was made by the
  person who ratified it or drafted at that person's request, on the day; the wrapper and the controls that test it
  are the same hand's.
- **No theorem is proved.** The TLA+ artifacts discriminate and check non-vacuity at small constants; the trace
  validation is drift detection against a model of the code; a checked proof certifies an implication between two
  Cedar encodings, not the encoding.
- **No principal is `Contained`**, at any rung.
- **The values are placeholders.** `T_persona` is enforced as a bound and runs on the local clock.
- **The solver is trusted for nothing, and the checker is trusted as written.** Its signature is cvc5's own
  formalization; a wrong rule there is the residual T-0045-14 states. Twenty-five of the run's `holds` never reached
  the solver and rest on the engine.
- **Bundles are signed under a throwaway key** with custody (1, 0), at the reference; gate evidence is still an
  operator's assertion.
- **The trusted base is in force and its binding table is a draft**, revised with the records it binds and not yet
  versioned by the archetype-evolution record.
- **Detection still fails open against a colluding Observer**, and the residual-risk statement is unwritten.
- **The reference is not the mechanism** (ADR-0033 §1). Its run since G6 is evidence of the same kind as before.
- **The narrative is a revision behind.** Revision 10 stands and disagrees with this checkpoint where §7 item 14 says.
- **No floor is ratified, no deployment conforms, and no deployment declaration has been written.**
- **The corpus is not closed.**

---

## 9. Manifest

`SHA256SUMS-G7` · 336 entries, cut from commit `839ef34` plus this checkpoint.

As at G2 to G6, the manifest's own digest cannot appear inside the file it measures, and this checkpoint is an entry
in it; both are recorded where they are cut, in the commit that adds them, and `manifests/index.tsv` names that
commit so `tools/verify-manifest.sh --all` checks this manifest at the tree it measured.

| Area | Entries |
|---|---|
| `decisions/` | 44 records |
| `checkpoints/` | 8 — the v1 corpus manifest, G1 to G7 |
| `narrative/` | 11 — the Theory of Operation head, its nine revisions, the glossary head |
| `derived/` | 18 dated artifacts |
| `spec/` | 54 — seventeen modules, sixteen run scripts, the converter, the binding table, nineteen dated results |
| `floor/` | 132 — the three bundle files, the generator, the gates, the wrapper, the tests, six dated results, the README, and the 118 files of the 2026.10.01 evidence tree |
| `process/` | 6 logs |
| `manifests/` | 9 — eight reference manifests and the `slm/` tree manifest |
| `tools/` | 54 — `tla2tools.jar` (ADR-0045 T-0045-29) and the 53 files of `tools/cpc/` (T-0045-14): the signature, its licence and its note |

The reference trees are measured by `SHA256SUMS-REF-2026.09.24` through `-2026.10.01`; the rehearsal tree by
`SHA256SUMS-SLM-2026.09.28`; this manifest measures those nine in turn.

Verify from the repository root, at this checkpoint's commit:

```sh
shasum -a 256 -c manifests/SHA256SUMS-G7 | grep -c ': OK$'                  # expect 336
tools/verify-manifest.sh --all                                              # every manifest at the commit it measured
```

**`SHA256SUMS-REF-2026.10.01` fails one entry at today's tree, and should**: it measures `dacbb0c`, and Batch 23 then
re-pinned ADR-0033. `tools/verify-manifest.sh --all` reports 66 of 66 at `dacbb0c`.

**`SHA256SUMS-G6` fails 41 entries at today's tree**, by construction: the thirty-three files the reorganization
moved, the records changed in Batches 22 to 24, the operational model, the glossary and the floor driver. It verifies
159 of 159 at `5244aab`.

The manifest excludes what `manifests/EXCLUDE` lists: material not ours to redistribute, the exports and archives,
the working directories, `doc/` and `sessions/`, the licence and notice files, every `README.md`, the manifest index
and the earlier checkpoint manifests, and the scripts in `tools/` (the installers, the TLC wrappers, the manifest and
reference tools). Two things under `tools/` are measured deliberately: the TLC jar, since G6, and the checker's rule
signature, from G7 on. `mechanism/`, `policies/` and `slm/` are measured by their tree manifests, not directly.
`slm/serve/profile-host-rung0.json` is still not in an `SLM` manifest; the next rehearsal cut measures it. The
checker binary is not tracked and not measured; its digest is in the gate header, and `tools/install-ethos.sh`
rebuilds it from the pinned commit.
