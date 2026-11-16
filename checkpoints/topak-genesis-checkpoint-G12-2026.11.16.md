# TOPAK — Genesis Checkpoint G12

**2026.11.16** · genesis custodian: Scott, (1, 0) · supersedes G11 (`9d6f95f444455510`) as the state of record · narrative: revision 15 of the Theory of Operation (`narrative/theory-of-operation.md`, `e737aa042625678d`, cut from G11, tag `ToO-rev15`) stands, **not revised at G12**, and is behind this checkpoint on both batches, the upstream report and its fixes, the proofs of `Workflow` and `Mesh`, and twenty-two Proposed records; where it and this checkpoint disagree, this document wins (§7, item 109)

**What G12 is.** The state of record, as G11 was: what each record says, what was ratified and by whom, what is owed,
and what is open. It is the first checkpoint at which **the prover's two known unsound cases are reported upstream**,
and the first with **ten more proof modules, every one under a Proposed record**.

**What changed at G12.** Two batches were ratified, **38 and 39**, as at G11, and neither changes a record's status.
Batch 38 corrected a citation in ADR-0024 (E1). Batch 39 recorded that the prover's two unsound cases were reported
upstream on 2026.10.18 (ADR-0046 A3, ADR-0045 A4). **No record drafted after G11 is in force.** Twenty-two were
drafted, **ADR-0056 to ADR-0077**, and all are Proposed: user scope, the specification graph and its declaration, a
command-chain overlay of ten records, the Build-Run pipeline, lifecycle security, six records on user documentation
and the archive, and the move of TOPAK's TLA+ checks into the tla-kit image. **Sixteen amendments are pending**, up
from twelve. Fifteen depend on a Proposed record. The sixteenth, **ADR-0033 A19**, measures the reference for this cut
and stands alone.

**The proofs grew, and none of the growth is in force.** `Workflow` and `Mesh` are proved (ADR-0054 R7, ADR-0055 R3),
and so are the eight modules of the command-chain overlay (ADR-0059 to ADR-0066). That is **34 proof modules, 13,622
obligations, every one proved, 31 certified**, where G11 had 24, 5,416 and 21. Every new module is cited only by a
Proposed record. **`spec/proof-sync.sh` exits 0**, where at G11 it exited 1. **Upstream fixed the first case and the
collision half of the second** after the report, in `tlapm` `ff40755`. **The pin has not moved**: it is still
`7824dab`, with both cases, and moving it is ADR-0077's open decision.

**The reference was measured again** for this cut (ADR-0033 A19, pending): a dependency update that moves the bundle
tier's WASM runtime, a test's race fixed, and two records re-pinned. **No source file of the reference changed** since
G11. **No liveness is proved**, as at G11. **No real principal is `Contained`**, as at G11; a trained model now runs as
a compiled occupant at rung 1 on DEV rules, with every clause passing or vacuous and the criterion unset. The
bootstrap trigger is still unmet, and remains optional.

---

## 1. Ratification record

All by the genesis custodian under ADR-0029 §2. Batch 38 on 2026.11.02; Batch 39 on 2026.11.03.

| Batch | Date | Contents | Notes |
|---|---|---|---|
| **38 · A citation** | 11.02 | **ADR-0024 E1**, alone | The human half of correlated review failure is Knight and Leveson's, and the gate's half Moon and Varshney's (§4.6, Appendix B). Floor fitness has an owner and a time, and no test. No decision text changes. Found while checking an external draft against the corpus. Nothing was run. ADR-0024 is in the bootstrap set, and no criterion attaches |
| **39 · The upstream report** | 11.03 | **ADR-0046 A3**; **ADR-0045 A4**, its dependent entry | The two cases are reported upstream as `tlapm` #309 and #310 (2026.10.18). **C4 on A3**, the custodian's decision. Condition (1): the assistant checked through GitHub's API that the issues exist and are labelled, and that a maintainer opened the reproducer pull requests #314, #315 and #318. Condition (2): the custodian read the issues against §8. ADR-0045's pin moved, and the premise routes were renewed (`premise-routes-results-2026.11.03.txt`, `bf17bc4488eca0bc`) |

**Withdrawn, not ratified:** none since G11.

### 1.1 Record status at G12

| Status | Count | Records |
|---|---|---|
| Accepted (genesis) | 18 | As at G11: 0001, 0002, 0004, 0007, 0010, 0012, 0016, 0017, 0018 (in part), 0019, 0020, 0022 (in part: §6 is Proposed), 0024, 0025, 0026, 0027, 0032, 0033 |
| Accepted (genesis) · confirmation required | 27 | As at G11. 0046 A3 is C4 inside a record already marked |
| Accepted (genesis) · provisional (confirmation required) | 2 | 0050, 0052 |
| Proposed | **27** | 0035, 0036, 0051, 0054, 0055, and **0056 to 0077**; and ADR-0022 §6 |
| Superseded | 1 | 0008, by 0038 |
| Tombstone | 1 | 0011 |
| Reserved, no file | 1 | 0014 |

76 record files, numbered to 0077; twenty-two added since G11, all Proposed. 0014 is the only reserved number. 0071
to 0076 were renumbered from 0070 to 0075 before ratification, since 0070 was taken (each one's R1).

**How the counts are read.** As at G11: from each record's status line and status note together. 18 + 27 + 2
accepted, 27 Proposed, 1 superseded and 1 tombstone make the 76 files.

**Sixteen amendments are pending**, up from twelve. **G11's twelve are all still pending**: ADR-0054 R3's ten dependent
amendments (ADR-0015 A1, ADR-0024 A4, ADR-0031 A4, ADR-0037 A5, ADR-0039 A3, ADR-0040 A2, ADR-0041 A4, ADR-0042 A3,
ADR-0043 A3, ADR-0047 A1), and ADR-0033 A16 and A17. **Four are new.** ADR-0033 A18, ADR-0045 A5 and ADR-0053 A1 are
ADR-0057's dependent entries, drafted 2026.11.07. **ADR-0033 A19** measures the reference for this cut. It was drafted
2026.11.16 and, by the custodian's decision of the same day (R14), takes force on its own ratification. Fifteen of the
sixteen depend on a Proposed record: twelve on ADR-0054 (A16 also on ADR-0055), and three on ADR-0057.

**Proposed records revised since G11.** ADR-0054 R7 and ADR-0055 R3 (the proofs; no decision text changes);
ADR-0057 R1 (the graph built); ADR-0059 to ADR-0067 R1, and R2 for 0060, 0062, 0063 and 0067 (the modules run and
proved, and claims narrowed to what they show); ADR-0069 R1 to R3; ADR-0070 R1 (on an adversarial review by a second
session of the same model); ADR-0071 to ADR-0076 R1 (renumbering), ADR-0075 R2. ADR-0077's History has two
revisions on 2026.11.16 without R numbers. Every revision is the assistant's, and each row says it was not reviewed.

### 1.2 What is ratified in part, or with a scoped marking

- **ADR-0046 A3 is confirmation-required under C4**, inside a record already marked. Its claim is that the report is
  made, not that the cases are fixed.
- **Neither batch changed decision text.** E1 corrects a citation. A3 and A4 record a fact about a trust root.
- **ADR-0050 and ADR-0052 are provisional**, as at G11. Their exits, items 88 and 92, are unchanged.
- **Every text ratified since G11 is the drafter's**, the assistant's at the custodian's direction. Each ratification
  row says it was not reviewed by a reader other than the drafter, beyond the custodian's reading of the issues (B39).

**Decided for the reference, not in a record.** As at G11: the sixth of G9's choices in ADR-0036, Proposed; nine
choices for workflows (`mechanism/` I49 (a) to (i)); the `workflow` stage linked, and `mechanism/lean` left stale
(ADR-0033 A16). The custodian decided on 2026.11.16 to measure the reference for this cut by a new manifest and
addendum (A19), and that A19 stands alone (R14).

---

## 2. The floors as ratified

### 2.1 The rules floor

**As at G11.** `RulesFloorBase.tla` still carries `bgScope` and a bound of two (§7, item 90). The ADR-0026 §6 rerun
is still owed.

### 2.2 The policy floor

**As at G11.** No file under `floor/` changed. The entries in force are the `emergency` stage,
`floor/proposed/emergency-floor.cedar` (`15c941b9a56a09f7`), 28 policies, 107 cases, genesis-provisional (ADR-0030
A3). The reference links the `workflow` stage (`10ea6818af9b4efe`, 30 policies, 123 cases), Proposed with ADR-0054,
at the custodian's direction (item 102). `floor/lean/` is unchanged and in sync (`69e1c30c61a64771`). No record
drafted since G11 proposes a stage; ADR-0067 places a mission's rules in a bundle, and its floor condition is not met.

### 2.3 Confinement

**As at G11 in the records**: rung 1 real, rung 3 SIMULATED, rung 2 a seam. **One result outside them.** The trained
Persona, compiled, runs as the occupant ADR-0036 §3 describes, at rung 1 on a `FROM scratch` image, under the
reference's launcher, on DEV rules (`slm/occupant-rung1-results-2026.11.11.txt`, `a81f7889e38e229a`). The launch is
attested, every clause passes or is vacuous, and `contained` is false because ADR-0035's criterion is not in force.
**No record cites it.** ADR-0036 §7 names a different image, and is not met as written (item 119).

### 2.4 The LTRO

**As at G11.** ADR-0035 is still Proposed and unrevised since G11.

### 2.5 Run

**As at G11.** ADR-0054's dependent amendments are pending and none is in force. ADR-0054 and ADR-0055 are re-pinned at
R7 and R3 (`d1b72db`), whose changes are to conditions and obligations only. The reference's source is unchanged since
G11 (item 120).

### 2.6 The trusted base

**In force, thirty-seven rows**, as at G11. ADR-0045 changed only by A4 (B39) and A5 (pending, with ADR-0057).
**T-0045-31's instance is reported upstream** (A4). Upstream closed #309 on 2026.11.10 by #314, and fixed the
collisions of #310 by #339; #310 is open, and its capture half is not claimed fixed. Both fixes are in `ff40755`, which
only ADR-0077 (Proposed) records. **The pin, `tools/TLAPS-PIN`, still names `7824dab`**, binary `e150fb793fb28592`,
with "the full digest is owed".

**A second pin file is new**, `tools/TLA-PIN` (`3413293630da647c`): the TLC jar, v1.7.4, `936a262061c91469`, checked
by `tools/check-pins.sh` on every push. It rests on ADR-0069 §10.2, Proposed.

**Rows proposed and not in ADR-0045:** T-0045-38 (a subject provider, trust root) and T-0045-39 (downstream
authorization, excluded), in ADR-0056; T-0045-40 (the archive's governed store, delegated), in ADR-0076. ADR-0077
declines a row for the tla-kit image.

### 2.7 Bundle signing, 2.8 the proof-carrying gate

Unchanged since G7.

### 2.9 The proofs

**Thirty-four proof modules**, up from twenty-four: `Workflow_proof` and `Mesh_proof`, and the overlay's `Federation`,
`Intent`, `Membership`, `Alone`, `Outstanding`, `PlaneClock`, `Peer` and `Release`. **13,622 obligations, every one
proved**; G11's twenty-four still sum to 5,416. **Thirty-one certify.** All ten new modules certify, each with its LS4
steps uncertified, as for every module. The three that did not at G11 still do not. **`spec/proof-sync.sh` exits 0**:
all thirty-four are in sync, every results file cites the pinned prover, and five base modules state why they have no
proof.

**Every new proof module is under a Proposed record**, and freezes at its ratification. `Workflow` and `Mesh` need no
state constraint, so the remainders TLC checked only under `CapLog` and `CapOnePast` hold without them.

**The scan covers the thirty-four in three files**: `proof-scan-results-2026.10.08.txt` (`b69cfbfa09c7def2`) for G11's
twenty-four, `-2026.11.10` (`0dce7e9c9d874063`) for the overlay's eight, and `-2026.11.11` (`78a6725f818e8c5d`) for
`Workflow` and `Mesh`. None finds a capture, and no renamed run differs. **No check detects the first case**, as at
G11 (item 104).

**The Lean route is unchanged.** Nothing under `spec/lean/`, `floor/lean/` or `mechanism/lean/` changed. Proved modules
without a Lean encoding went from nine to nineteen (item 107).

---

## 3. Verified artifacts

G11's artifacts keep their digests. New since G11:

| Artifact | SHA-256 (16) | Records | Result |
|---|---|---|---|
| **`spec/Workflow_proof.tla`** | proof `5dc68f94eeacda28`; results `34a18728d0e92e79`; certified `a961be0445200e94`; module `a72973b5878e9468`, unchanged | ADR-0054 R7 (Proposed) | Ten properties and `SafeAlways`; 1,136 obligations, certified, 11 by LS4; no state constraint |
| **`spec/Mesh_proof.tla`** | proof `1d4bd5ad924b6ab6`; results `4447b8e426f6dd79`; certified `38a0b61ae1bf2872`; module `a5bc64953c38c9a9`, unchanged | ADR-0055 R3 (Proposed) | Seven properties and `SafeAlways`, at the module's mesh and budget of 6; 1,470 obligations, certified, 8 by LS4 |
| **`spec/Federation.tla`** | module `03e0bbb28b5e9a1d`; TLC `7e8e63ddd7fc4475`; certified `5f19d7acc5ad3c70` | ADR-0059 R1 (Proposed) | 41 of 41 rows as expected; 892 obligations, certified. The budget is conserved for an honest subtree only |
| **`spec/Intent.tla`** | `0c90ea5004c4f127`; `16fe802076da93ee`; `6bd2addd6d14054b` | ADR-0060 R1, R2 | 35 of 35; 677, certified |
| **`spec/Membership.tla`** | `bcf3c5d151488133`; `6974af8a38a4b879`; `7b58fb5eb2bbf25d` | ADR-0061 R1 | 28 of 28, at five replicas where the record says seven; 495, certified |
| **`spec/Alone.tla`** | `9e7e04adb2ab5161`; `4d32218a239703f4`; `e22ea91d3419b230` | ADR-0062 R1, R2 | 47 of 47; 263, certified; two `ENABLED` invariants |
| **`spec/Outstanding.tla`** | `8ecb0b147c7748ac`; `b5cfced141d1926e`; `eefef346a4a7f2ca` | ADR-0063 R1, R2 | 40 of 40; 1,871, certified |
| **`spec/PlaneClock.tla`** | `7d7ced23419c1df2`; `60505f0b484ecf8f`; `11e2a6d24dd954d1` | ADR-0064 R1 | 38 of 38, in discrete time; 535, certified |
| **`spec/Peer.tla`** | `5ee3528164cd1a35`; `d3b80c6f31ca83e8`; `12677112bade3a44` | ADR-0065 R1 | 25 of 25; 254, certified |
| **`spec/Release.tla`** | `7a8a212d3f07956b`; `34afe5523f488399`; `5c0b3884c1381f04` | ADR-0066 R1 | 67 of 67; 613, certified; one `ENABLED` invariant |
| **The deadlock audit** | `deadlock-audit-results-2026.11.10.txt` (`f4ad093891b47f0e`) | ADR-0059 R1, ADR-0061 R1 | The eight overlay modules: six with no terminal state, two with terminal states only at the bound; no stray deadlock |
| **The proof scans** | `-2026.11.10` (`0dce7e9c9d874063`); `-2026.11.11` (`78a6725f818e8c5d`) | ADR-0059 R1; ADR-0054 R7, ADR-0055 R3 | §2.9 |
| **`spec/defects/`**, the reproducers | `defects-run.sh` (`76a60927940df503`); `defects-results-2026.10.22.txt` (`692d74d63b6bbec4`) | ADR-0077 (Proposed); `spec/proof-certification.md` §8 | Every outcome as §8 says: both cases reproduce under `7824dab` |
| **The specification graph** | `specification-graph.json` (`01a5dc99d65eb60f`); `specification-graph.py` (`7b4a4d699290d1cb`); `clauses.py` (`d476d7659e44d089`); results `-2026.11.07` (`df1433d8a5f3bd6d`) | ADR-0057 R1 (Proposed); ADR-0033 A18, ADR-0045 A5, ADR-0053 A1 (pending) | 419 nodes, 435 edges, well formed; eight stale edges, all to `mechanism/lean`. Built at `9749dfa`: it holds neither the overlay's modules nor the two new proofs |
| **The premise routes** | `premise-routes-results-2026.11.03.txt` (`bf17bc4488eca0bc`) | ADR-0045 B39, ADR-0046 B39 | Renewed with ADR-0045's pin at Batch 39: 43 rows and 34 other premises agree; 18 derived premises; three of 43 rows hold. Read against ADR-0045 before A5 was drafted |
| **The reference at `d1b72db`** | `SHA256SUMS-REF-2026.11.16` (`5bd868a0ca45e2c5`, 116 entries) | ADR-0033 A19 (pending) | Five entries changed from `-10.09`: the lockfile and `topak-contain`'s manifest (`wasmtime` 48.0.8, `opa-wasm` 0.3.4), an end-to-end test, the pin file, the register. 155 tests across fifteen binaries, none failing, run 2026.11.16. Rego tests and trace validation not rerun |
| **The SLM occupant at rung 1** | results `a81f7889e38e229a`; parity `fe1a20e05811dd46`; profile `fab20bd5be3c9f77` | none | §2.3. Parity with the trained model: identical tokens, logits within 2e-05, 64 greedy tokens identical. **Not measured**: `slm/` is excluded from this manifest, and `SHA256SUMS-SLM-2026.09.28` predates the occupant |
| **CI and the pin tools** | `check-pins.sh` (`391fb7289dbc210f`), `check-results.sh` (`2c6e088995f96772`), `compare-results.py` (`353afc6ccf3f4e85`), `check-sources.sh` (`4a3b4ef6ba95eff7`), `ci-plan.sh` (`880d7a3b83e39b5e`), `ratchet.py` (`2f4aa71a85cb3604`), `spec/modules.tsv` (`011c990f416d8fe3`) | ADR-0069 §10.2 (Proposed) | No results file in the tree. `checks` and `frozen-files` pass on `main`; `sources` has never run |

**Frozen from G12 on**, as G11's are: nothing new. Every module, proof module and results file above is cited only by
Proposed or pending text, and freezes at its ratification.

**Results the drafting did not anticipate**, since G11:

1. **A captured plane breaks the root's budget.** "The root's tally bounds the whole tree" fails under capture, so
   `BudgetConserved` is stated for an honest subtree only (ADR-0059 R1).
2. **A membership can have two successors** without a one-vote rule, which ADR-0061 §3 lacked (`M_TWOVOTES`). The
   module is checked at five replicas, not seven (ADR-0061 R1).
3. **The governor rule, read literally, lets a captured plane admit ordered entries without charge.** It now charges
   them, with `kUp >= 2` (ADR-0063 R1).
4. **The proposal's only effects after expiry conflict with its own beacon**, which is an effect (ADR-0062 R1).
5. **One of PlaneClock's two vote rules carries no property**, and the other carries `NoGrantPastExpiry` (ADR-0064 R1).
6. **A relayed lease enables a permit**, so "every item received from peers removed is still permitted" is false
   (ADR-0065 R1).
7. **The release interlock must check that the act names this vehicle**, or one act fires once per vehicle. A cut link
   stops the order but not an act already sent (ADR-0066 R1).
8. **The predecessor is ordered before the effect but need not be live at it** (ADR-0060 R1).
9. **`Workflow` and `Mesh` need no state constraint** to be proved, and writing the proofs corrected no pairing of a
   property with a mutation (ADR-0054 R7, ADR-0055 R3).
10. **The stale `mechanism/lean` voids the two `Seats` theorems** where T-0045-28 is excluded, while the premise
    routes show them holding (ADR-0057 finding 7).
11. **Upstream fixed the first case before TOPAK adopted any fix.** Under `ff40755` the defect record no longer
    reproduces the false statements, and all 34 modules prove with equal counts (ADR-0077, Proposed).
12. **The launcher applies no resource limits** and ignores a profile's unknown keys, and moving from rung 0 to rung 1
    changes the profile, not only the rung (the occupant's findings; item 119).
13. **The drift test can read another tree.** It fixes the repository root at compile time, and a cached test binary
    built in another worktree reported drift that was not this tree's (ADR-0033 A19).

**What these checks are.** As at G11, and: a proof of an overlay module is of a module whose record is Proposed and
whose floor and reference are not built. A rung-1 run asserts its clause verdicts through the launcher, on DEV rules.

---

## 4. Genesis debt ledger (ADR-0029 §7)

**Confirmation-required count: 29 records**, as at G11: the 27 of §1.1 and the two provisional records, 0050 and 0052.

| Record | Criterion | What the first quorum has to review |
|---|---|---|
| As at G11 | as at G11 | Unchanged |
| 0046 A3 | C4 | That the report is made, and that the record's account of what it asked is faithful |

**The ADR-0029 A2.5 line**, as `checkpoints/README.md` carries it:

| Field | Value at G12 |
|---|---|
| **Bootstrap reviewer engaged** | **None.** Every record, amendment, proof, module and reference tree is one hand's, drafted or ratified by the genesis custodian with the assistant; no reviewer independent of the author has read any record |
| **Last completed review pass** | **None.** No confirmation pass has been run and no review attestation exists. The self review of 2026.11.11 (`derived/topak-critical-review-2026.11.11.md` and its annex) and ADR-0070's adversarial review are the drafter's own, by fresh sessions of the same model, and say so; none counts under A2.1. An upstream maintainer took up the defect reports, which is engagement with a trust root and not a review of any TOPAK text |

**Bootstrap specification: partial**, as at G11.

**Debts no confirmation repays.** Those of G2 to G11 stand. G12 adds: **twenty-two Proposed records, four pending
amendments, ten proof modules, a specification graph, a CI pipeline and a rung-1 run are one hand's**, drafted, built
and checked across five weeks, with no second reader. **A trust root is kept in use with two known defects** that
upstream has since fixed in part, on a pin that has not moved. **The reference still follows text that is not in
force**, as at G11.

---

## 5. Conventions carried at G12

G2 to G11's conventions stand. Added since G11:

- **What is frozen is checked, not only declared.** `.github/scripts/frozen-files.py` refuses a change to a checkpoint,
  a derived document, a results or evidence file, a manifest, the narrative archive, a process log, or a module whose
  digest a record that is not Proposed cites; a record's file is never removed or renamed. A dated file may change on
  its own date, and the custodian may lift the freeze for one pull request (`.github/CONTRIBUTING.md`). It runs on every
  pull request. The required-checks ruleset that would make it binding is disabled (item 114).
- **A check with findings that predate CI is ratcheted**: it shows what stands and fails only on what a change adds
  (`tools/ratchet.py`; ADR-0069 §10.2, Proposed). It applies to the corpus pins, `tools/lean-sync.sh`,
  `tools/check-refs.py` and the record lint.
- **The TLC jar is pinned by digest**, as the prover and Lean are (`tools/TLA-PIN`, `tools/check-pins.sh`).
- **A prover release that fixes either case is a new instance of T-0045-31**, by its digest
  (`spec/proof-certification.md`; ADR-0046 A3).
- **The defect reproducers are files**, run by `spec/defects/defects-run.sh` against `proof-certification.md` §8.
- **Main changes by pull request, merged by merge commit, signed** (`.github/rulesets/`, rulesets 01 and 02, in force on
  the repository; tags immutable and the custodian's, 04 and 05). **An approval is not a ratification**
  (`.github/CONTRIBUTING.md`).
- **Every item of a ratification condition is marked Met, with its evidence and digest, or Not met**, and a record's
  provenance note names each cited record it did not re-read. ⟨Q⟩ marks a custodian's answer to a proposal's numbered
  question, beside G11's ⟨K⟩. These are the drafting conventions of ADR-0054 to ADR-0077, set out in
  `.claude/skills/drafting-records/`, which this manifest does not measure.

---

## 6. Records changed after their own ratification

Since G11:

| Record | Change | Why |
|---|---|---|
| 0024 | E1 (B38) | The human half of correlated review failure is Knight and Leveson's; floor fitness has an owner and a time, and no test |
| 0045 | A4 (B39) | T-0045-31's instance: both cases reported upstream |
| 0046 | A3 (B39) | The upstream report is made: #309 and #310; the status note gains C4 for A3 |

**Pending, not applied**, in records already ratified: G11's twelve (ADR-0015 A1, ADR-0024 A4, ADR-0031 A4, ADR-0033
A16 and A17, ADR-0037 A5, ADR-0039 A3, ADR-0040 A2, ADR-0041 A4, ADR-0042 A3, ADR-0043 A3, ADR-0047 A1), each
depending on ADR-0054, A16 also on ADR-0055; **ADR-0033 A18, ADR-0045 A5 and ADR-0053 A1**, depending on ADR-0057; and
**ADR-0033 A19**, which stands alone (R14). Each is marked inline, with a History row.

---

## 7. Open list at G12

**G10's ninety-nine and G11's nine, as they stand.** An item not listed is as at G11.

| # | Item | At G12 |
|---|---|---|
| 1 | **The sandbox gap** | One guest passes P3, as asserted by the launcher: the compiled occupant at rung 1 (§2.3). No real principal is `Contained` |
| 12 | **Derived documents** | Twenty-seven added since G11: twenty-two dated documents and five directories. Two directories, `recon-fleet-7-2026.11.10/` and `recon-fleet-7-simulation-2026.11.10/`, have no row in `derived/README.md` |
| 14 | **The ToO** | Revision 15, cut from G11, stands, and is behind this checkpoint (item 109) |
| 34 | **ADR-0036's ratification run** | A rung-1 run exists, on an image other than the one §7 names, by the custodian's choice. §7 is not met as written (item 119) |
| 56 | **The refinement chain, stages 2 and 3**; the reproducible build | Open, and stage one is further behind: the self review's rerun matched 82 of 83 traces, the end-to-end workflow trace does not replay, and `tests/workflow.rs` is not traced. A19 did not rerun trace validation. `derived/topak-refinement-verification-options-2026.11.04.md` finds that no tool removes T-0045-28, and recommends an order |
| 66 | **An ADR-0029 criterion for assisted drafting** | Open, and resting on more: twenty-two Proposed records, both batches, and three drafting skills |
| 73 | **The prover pinned for reproducibility** | Not moved: `7824dab`, its full digest still owed. ADR-0077 would move it to `ff40755` (item 117) |
| 74 | **The SMT backends' proofs checked** | **Thirty-one of thirty-four.** The ten new modules certify; the three exceptions are as at G11 |
| 76 | **The diagrams are not measured** | Open. Ten added since G11, and `Emergency` is no longer omitted. Several are behind this checkpoint: `Workflow` and `Mesh` drawn unproved, Batch 39 not drawn, and nothing drawn for ADR-0057, 0058 or 0069 to 0077 |
| 78 | **One driver per TLC results file** | In part. The overlay's modules regenerate from their rows, and `spec/modules.tsv` drives CI's TLC job over fifteen modules |
| 90 | **`spec/` behind the records** | Larger: eighteen modules have no binding rows, now with the overlay's eight. `RulesFloorBase.tla` still carries `bgScope` |
| 99 | **`REVIEWERS_GUIDE_README.md`** | Written against G11, and behind this checkpoint (item 109) |
| 100 | **The narrative against G11, and tags** | **Discharged** at `a77d226`: revision 15, the glossary, the architecture description's revision 3, the reviewer's guide. The tags exist and are pushed. For G12: item 109 |
| 101 | **ADR-0054 and ADR-0055 before ratification** | **Proofs met** (R7, R3), and `spec/proof-sync.sh` exits 0. Still owed: binding rows; values for `T_wf`, the step bound and `N`; finding 5; `all` joins, skips, multi-select, more than one decision point and the orchestrator's own rounds; fan-out, pools and parity seatings; the gate's evidence for a mesh's vote; ADR-0055's dependent entries; the custodian's reading of every drafter's choice |
| 103 | **`mechanism/lean` is stale** | As at G11. `tools/lean-sync.sh` exits 1 for the same three series, now ratcheted in CI. It blocks ADR-0057 §14's third condition |
| 104 | **The prover's two known unsound cases** | **Reported upstream** (B39), and since **fixed upstream** in part (§2.6). The pin has both. No check detects the first case. Sentences saying they are "not reported upstream" remain in the narrative, the glossary and ADR-0046 §8 (item 109) |
| 107 | **ADR-0053's open obligations** | Proved modules without an encoding went from nine to nineteen. `native_decide` is still in the floor package. ADR-0053 A1 is pending |

**New since G11.**

| # | Item | Where it sits |
|---|---|---|
| 109 | **The narrative against this checkpoint, and tags.** Revision 16 and the glossary against G12: both batches; the report and the upstream fixes; `Workflow` and `Mesh` proved; and, as Proposed, the terms the twenty-two records owe. The architecture description and the reviewer's guide. The stale sentences of item 104. Tags owed: `G12`, and `REF-2026.11.16` for the tree A19 cites | `narrative/`; `checkpoints/README.md` |
| 110 | **ADR-0056, user scope.** The subject assertion's form, `subject.attributes`, a task path for end users, the digest of a personal identifier, the label for a `subject` result, the activation under ADR-0054. Its dependent entries are not drafted. It proposes T-0045-38 and T-0045-39 | ADR-0056 |
| 111 | **The specification graph, ADR-0057 and ADR-0058.** Built and committed; A18, ADR-0045 A5 and ADR-0053 A1 pending on it. Findings 7 and 8 await the custodian, and §14's third condition waits on item 103. The graph does not yet hold the overlay's modules or the two new proofs. ADR-0058 owes an ADR-0023 amendment, the supplier subgraph's form and its dependent entries | ADR-0057; ADR-0058 |
| 112 | **The command-chain overlay, ADR-0059 to ADR-0068.** Eight modules checked, proved and certified. No floor stage is written and no reference is built, and each record's floor and reference conditions are not met. Placeholder values; the readings F3, F4, N1, N2 and Z2 to Z4; binding rows; Lean encodings. ADR-0068 still says no module is written | ADR-0059 to ADR-0068 |
| 113 | **The Build-Run pipeline, ADR-0069, and CI.** `checks` and `frozen-files` pass on `main`; `sources` has never run. Owed: Annex B's eight entries, a gate-evidence key (an ADR-0025 §1(f) amendment), §12's module, and four open questions. Standing findings, ratcheted: `lean-sync` (item 103), path citations, and four record-lint failures, a Pending row not on its record's Pending line (ADR-0022 A2, ADR-0033 A4 and A5, ADR-0037 A1) | ADR-0069; `.github/workflows/` |
| 114 | **The repository's rulesets on GitHub.** The required-checks ruleset (03) is disabled, and its copy on GitHub names checks no workflow reports, until `.github/rulesets/03-main-required-checks.json` is imported. The `frozen-override` label does not exist. The DCO app is not installed | `.github/rulesets/README.md` |
| 115 | **ADR-0070, lifecycle security.** The custodian's decision on disclosing F1 under `SECURITY.md`; dispositions for F1 to F9; two rows that fail ADR-0045 §2; the two §13 modules; four gates not run; signed tags; owners for tenancy and jurisdiction; §11's dependent entries | ADR-0070 |
| 116 | **User documentation and the archive, ADR-0071 to ADR-0076.** Nothing built, no module, no dependent entry drafted. A `documentation` manifest kind; an accessibility audit with a named auditor; a mechanism record for the archive mark and compaction; holdings for G1 to G11; an external auditor's role; erasure | ADR-0071 to ADR-0076 |
| 117 | **tla-kit, and the prover's move, ADR-0077.** tla-kit `v0.1.0` is published and attested. Owed on TOPAK's side: `TLA-KIT-PIN` and its check; before the prover moves to `ff40755`, §5's reruns (the defect record, every proof module certified, the scan, the capture listings); §6's two corrections; Annex A's entries; Q1 to Q3. ADR-0046 A3's "neither fixed as of 2026.11.03" is overtaken | ADR-0077 |
| 118 | **Three premises in the reference's toolchain**, found by the 2026.11.04 paper and true at this cut: the Lean pin, v4.33.1, predates v4.34.0's kernel fixes and v4.35.0's `lake check --paranoid`; release builds wrap on integer overflow (no `[profile.release]`); `authentic.rs` calls `verify`, not `verify_strict` | `derived/topak-refinement-verification-options-2026.11.04.md` §5 |
| 119 | **What the rung-1 occupant found.** ADR-0036 §7 is not met as written, and needs a revision to ratify on this run. The rung-0 and rung-1 profiles are different files, against ADR-0036 R1's one change at a time. The launcher applies no memory, CPU or environment limits, and ignores unknown launch keys. `mechanism/` G1 and its rung-0 line are stale, and correcting them moves the reference manifest. The image's identity is stable only with `--provenance=false`, and the build is not reproducible | `slm/occupant-rung1-results-2026.11.11.txt`; ADR-0036 |
| 120 | **The reference measured for this cut, and its tests.** ADR-0033 A19 is pending. The drift test fixes the repository root at compile time (`tests/drift.rs`, `env!("CARGO_MANIFEST_DIR")`), so a cached binary can check another tree; the bundle tests may share the exposure. Trace validation and the Rego tests were not rerun | ADR-0033 A19 |
| 121 | **The self review of 2026.11.11, not dispositioned.** CR-40 to CR-61; 108 open items its register finds carried by no list, among them unpinned OPA and Kafka images; 59 stale sentences; 28 obligations met and not struck | `derived/topak-critical-review-2026.11.11.md`; `derived/topak-open-findings-register-2026.11.11.md` |
| 122 | **The scenario inventory's findings, SF-1 to SF-26.** Several High, against records in force: a stop's cost in the world priced nowhere (SF-1), an effect unverified (SF-4), and those people an effect lands on with no standing (SF-26). Five modules proposed; no suggested entry made | `derived/scenarios-2026.11.12/FINDINGS_TOPAK.md` |

**Not on this list, deliberately:** bootstrap itself, as at G2 to G11.

---

## 8. What G12 does not claim

- **Nothing here is independently reviewed.** Two batches were ratified on two days. The records, the amendments, the
  modules, the proofs, the graph, the pipeline and the reference are one hand's. The custodian read the two issues.
- **The invariants are proved, under named hypotheses, by the prover T-0045-31, and the mutations and witnesses are
  checked by TLC. Neither is a claim about the running reference** (T-0045-28). **Ten of the thirty-four proof modules
  are of Proposed records**, and the overlay's eight are of a design with no floor and no code.
- **The pinned prover can prove false statements.** Two ways are known, both reported and both fixed upstream in part,
  and **the pin has both**. A scan and a reading say that no result a record cites rests on either, and no check
  detects the first. A certified proof is not a verified one.
- **A Lean proof of the code is not a proof of the code**, and the package is stale at this cut, as at G11.
- **No liveness is proved.** Leads-to properties are checked by TLC at small constants, for coupling. Five `ENABLED`
  invariants are proved: two for the emergency call, and three in the overlay, under Proposed records.
- **The workflow records are Proposed, and the reference follows them**, on a floor that is not in force. Their
  modules are now proved; that does not ratify them.
- **The operator design does not stand on evidence**, and **break-glass has no settled form**, as at G11.
- **No floor is ratified.** A floor stated in Lean is not a floor found fit.
- **A label is a declaration and not a finding**, as at G11.
- **No real principal is `Contained`.** A rung-1 occupant on DEV rules is attested, with no criterion in force.
- **The reference is not the mechanism** (ADR-0033 §1).
- **The values are placeholders**, and **detection still fails open against a colluding Observer**.
- **Bundles are signed under a throwaway key**; gate evidence is still an assertion.
- **CI gates nothing.** No ruleset in force requires a check, and during genesis the workflows promote nothing.
- **The narrative is a revision behind** (item 109).
- **No deployment conforms, and no deployment declaration has been written.** `derived/recon-fleet-7-2026.11.10/`
  holds an illustrative one, which says it is not a record and cannot run.
- **The corpus is not closed.**

---

## 9. Manifest

`SHA256SUMS-G12` · 1,100 entries, cut from commit `f4e75f9` plus this checkpoint and the edits that go with it.

As at G2 to G11, the manifest's own digest cannot appear inside the file it measures, and this checkpoint is an entry
in it. Both are recorded where they are cut, in the commit that adds them, and `manifests/index.tsv` names that
commit, so that `tools/verify-manifest.sh --all` checks this manifest at the tree it measured.

| Area | Entries |
|---|---|
| `decisions/` | 76 records: G11's 54 and ADR-0056 to ADR-0077 |
| `checkpoints/` | 13: the v1 corpus manifest, G1 to G12 |
| `narrative/` | 12, as at G11 |
| `derived/` | 287: G11's 32, twenty-two dated documents, and 233 files in five directories (`sdd-equivalents-2026.11.06` 73, `recon-fleet-7-2026.11.10` 34, `recon-fleet-7-simulation-2026.11.10` 11, `topak-self-review-annex-2026.11.11` 65, `scenarios-2026.11.12` 50) |
| `spec/` | 321: G11's 243 and seventy-eight more. The overlay's eight modules with their proofs, rows and results; the `Workflow` and `Mesh` proofs and their results; `spec/defects/`; the specification graph, its checker and clause splitter; `modules.tsv`; the premise routes, two scans and a deadlock audit |
| `floor/` | 170, as at G11 |
| `process/` | 6 logs |
| `manifests/` | 20: nineteen reference manifests and the `slm/` tree manifest |
| `tools/` | 63: G11's 56, `TLA-PIN`, and the CI scripts `check-pins.sh`, `check-results.sh`, `check-sources.sh`, `ci-plan.sh`, `compare-results.py` and `ratchet.py` |
| **`skills/`** | **132, a new area**: four project skills packaged as plugins (writing TLA+ specifications and proofs, Lean encodings and proofs, auditing claims against evidence, generating the corpus's diagrams), added 2026.11.09 to 2026.11.11. Measured at the custodian's decision of 2026.11.16; the skills under `.claude/` stay excluded |

The reference trees are measured by `SHA256SUMS-REF-2026.09.24` through `-2026.11.16`, and the rehearsal tree by
`SHA256SUMS-SLM-2026.09.28`; this manifest measures those twenty in turn. **One reference manifest is cut with
G12**: `-2026.11.16`, at `d1b72db`, for ADR-0033 A19. The reference's code at this cut is the code it measures.

Verify from the repository root, at this checkpoint's commit:

```sh
shasum -a 256 -c manifests/SHA256SUMS-G12 | grep -c ': OK$'                 # expect 1100
tools/verify-manifest.sh --all                                              # every manifest at the commit it measured
```

**`SHA256SUMS-REF-2026.11.16` fails two entries at today's tree, and should**: the pin file, which moved with A19 and
R14, and the register, whose header names G12. It verifies 116 of 116 at `d1b72db`. The older reference manifests
fail more, for the changes A19 lists, and each verifies at its own commit.

**`SHA256SUMS-G11` fails twelve entries at today's tree, by construction**: seven records (ADR-0024, ADR-0033,
ADR-0045, ADR-0046 and ADR-0053, and the Proposed ADR-0054 and ADR-0055), the three narrative files edited after their
tags, `spec/deadlock-audit.sh` and `spec/proof-certification.md`. It verifies 604 of 604 at `ce8f460`.

The manifest excludes what `manifests/EXCLUDE` lists, unchanged since G11 but for `ADOPTERS_GUIDE_README.md`, added
2026.10.09 beside the other root guides. `.claude/` and `.github/` stay excluded, so the drafting conventions of §5,
the frozen-files check and the rulesets are not measured. `diagrams/` stays excluded (item 76). `mechanism/`,
`policies/` and `slm/` are measured by their tree manifests, not directly.
