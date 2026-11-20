# TOPAK — Reviewer's Guide

**2026.11.20** · DRAFT · written against Genesis Checkpoint G12 (2026.11.16) and Theory of Operation revision 16, at
commit `ffd02f1` of `main` (2026.11.20), which is after G12 and after Batch 40 · a convenience, not a record: where
this guide and the checkpoint disagree, the checkpoint wins. It is kept current and is not measured by any manifest
(`manifests/EXCLUDE`).

**Drafted by the assistant** at the custodian's request. Like most of this corpus, it has not been read by anyone
independent of its author. Every count below was taken from the files on 2026.11.20, by the commands §9 names; if a
count here and a file disagree, the file wins and the disagreement is a finding. If this guide steers you away from
something, treat that as a finding too.

---

## 1. What you are being asked to do

TOPAK is an architecture pattern for multi-agent systems that treats every agent as Byzantine and keeps models out
of the trusted computing base. This repository is its design corpus, plus a Rust reference implementation of one
path through it. Nothing here is deployable ([SECURITY.md](SECURITY.md)).

Every record, specification, proof, policy, test and line of code was written or ratified by one person, working
with an AI assistant. The corpus says so repeatedly, and its own rules make your review a precondition for the next
phase:

- ADR-0029 A2 requires an **independent review of the entire corpus, at one named manifest digest, by at least one
  reviewer who is not the author**, before the system's trust anchor may bootstrap.
- The review is complete when **every finding is dispositioned**: applied as a change, declined with recorded
  reasons, or carried as named debt.
- The review's attestation (who reviewed, which digest, what scope, how findings were disposed) is signed into the
  genesis bundle.
- Since ADR-0029 A4 the reviewer has **two further duties**. To **establish that the policy floor is fit**: no
  floor text has been ratified, and the floor is ratified with your finding that it is fit. Nothing in the corpus
  says what the test for that is, so you would be writing it (G12 §7, item 87). And to **attest to rules that
  include three provisional amendments**, named as provisional (ADR-0024 A3, ADR-0025 A3, ADR-0026 A2).

A partial review is still useful. Say what you read and at which digest, and it will be recorded as that.

## 2. What state the corpus is in

Read this before forming a view of how finished anything is. The counts are of the tree at `ffd02f1`; where a
number has moved since G12, both are given.

| Fact | Where it is stated |
|---|---|
| **Seventy-six record files**, numbered ADR-0001 to ADR-0077 (0014 is reserved and has no file). **Forty-seven are accepted**: eighteen plain, twenty-seven marked confirmation-required, and two provisional. **Twenty-seven are Proposed**, one is superseded (0008, by 0038) and one is a tombstone (0011) | [G12](checkpoints/topak-genesis-checkpoint-G12-2026.11.16.md) §1.1; [decisions/README.md](decisions/README.md); each record's status line |
| **Twenty-nine records need independent confirmation** (ADR-0029 C1 to C4): the twenty-seven marked, among them ADR-0029 itself for its A2 only, and the two provisional records. Confirmation waits for the first post-bootstrap quorum; the bootstrap set (ADR-0024 to ADR-0027) can never have one | G12 §4; ADR-0029 §4 |
| "Accepted" means ratified by the sole custodian, in forty numbered batches between 2026.09.23 and 2026.11.17. It is a declaration, not a review | ToO §0, §9; ADR-0029 §2 |
| **Two records are provisional**: in force, and subject to redesign. ADR-0050 (the operator as a principal) was ratified without its central behaviour built; ADR-0052 (break-glass as an emergency seating) rests on it. Every amendment that depends on either is provisional too | G12 §1.2; ADR-0029 A4 |
| **Twenty-seven records are Proposed**, twenty-two of them (ADR-0056 to ADR-0077) drafted since G11 and none in force. Two, ADR-0054 and ADR-0055 on workflows, are built at the reference, which links a floor stage that is not the floor in force, and are proved. Ten (ADR-0059 to ADR-0068) are a command-chain overlay with eight proved modules and no floor and no code | G12 §1.1, §2.2, §7 items 101 and 112 |
| **Fifteen amendments are pending**, every one on a Proposed record: twelve wait on ADR-0054 (ADR-0015 A1, ADR-0024 A4, ADR-0031 A4, ADR-0033 A16 and A17, ADR-0037 A5, ADR-0039 A3, ADR-0040 A2, ADR-0041 A4, ADR-0042 A3, ADR-0043 A3, ADR-0047 A1; A16 also on ADR-0055) and three on ADR-0057 (ADR-0033 A18, ADR-0045 A5, ADR-0053 A1). G12 counted sixteen; the sixteenth, ADR-0033 A19, was ratified with A20 in **Batch 40 on 2026.11.17**, after G12 | G12 §1.1, §6; ADR-0033 B40; each record's Pending line |
| **The reference's measure is `SHA256SUMS-REF-2026.11.16b`** at `36269bc` (ADR-0033 A20, Batch 40): the tree after `spec/Paxos.tla` and `spec/PaxosTrace.tla` were added and pinned. G12's manifest measures the earlier `-2026.11.16` at `d1b72db` (A19). There is no tag for the `b` cut yet; `REF-2026.11.16` tags the earlier one | [manifests/index.tsv](manifests/index.tsv); ADR-0033 A20 |
| Nearly every text ratified since 2026.10.02 was drafted by the assistant, and everything drafted since G11: twenty-two records, four amendments, eleven proof modules, a specification graph, a CI pipeline and a rung-1 run | ToO §0, §12 item 3; G12 §4 |
| No reviewer is engaged and no review pass has been completed. Two reviews since G11 were fresh sessions of the same model, and say so | G12 §4; [checkpoints/README.md](checkpoints/README.md) |
| No floor is ratified. The floor in force is the `emergency` stage (28 policies, 107 cases), gated and genesis-provisional: ratified when the bootstrap reviewer finds it fit. The reference links the `workflow` stage (30 policies, 123 cases), Proposed | G12 §2.2; ADR-0030 A3 |
| Every numeric parameter is a placeholder; nothing has been measured | [Residual-risk statement](derived/topak-residual-risk-statement-2026.11.11.md) |
| The proofs are of the TLA+ modules, not of the running code. No refinement exists. **Forty-two TLA+ modules and thirty-five proof modules, 14,791 obligations, every one proved; thirty-two certify, three do not** (`RulesFloorNV_rev5`, `Confinement`, `Confinement_A1`). G12 counted thirty-four, 13,622 and thirty-one; `Workflow_A1_proof` (1,169 obligations) was added on 2026.11.20. **Eleven proof modules are under Proposed records**, eight of them of the overlay, and `Workflow_A1` is a draft successor that ADR-0054 does not yet carry. Fifteen modules are proved again in Lean, of re-encodings; twenty are not | G12 §2.9, §8; [spec/README.md](spec/README.md); ADR-0045 T-0045-28; `tools/lean-sync.sh` |
| **The prover is known to be unsound in two ways.** A rule and a scan keep a proof from them, and no check detects the first. Both are reported upstream and partly fixed there (`ff40755`), and **the pinned build, `7824dab`, has both.** CI now also reruns every proof module in the tla-kit image, whose prover is a different build; that run corroborates and regenerates nothing | G12 §2.6, §2.9, item 104; ADR-0046 A2, A3; ADR-0077 (Proposed); `tools/TLAPS-PIN`, `tools/TLA-KIT-PIN` |
| No liveness property is proved. Coupling's leads-to properties are checked by TLC at small constants. Six `ENABLED` invariants are proved, one of them in the draft `Workflow_A1` | G12 §8, item 105; ToO §5.5; spec/README.md |
| **The consensus log is modelled and not proved.** `Paxos.tla` was written from `replica.rs` by the same hand, is checked by TLC at three replicas and one round, and the reference's simulated runs replay through it. Its safety argument is `Voting`'s, which is not written as a module | ADR-0033 A20 and finding 9; spec/README.md "The consensus log" |
| At the reference, no real principal is confined. Every theorem about confinement is void there. One guest passes P3, as the rung-1 launcher asserts on DEV rules. 159 tests pass | G12 §2.3, §8; ADR-0033 A20 |
| **CI runs on every pull request and gates nothing**: the ruleset that would require its checks (`03-main-required-checks`) is disabled on GitHub, as it was at G12 (checked 2026.11.20). The `sources` workflow has never run | G12 §8, item 114; [.github/rulesets/README.md](.github/rulesets/README.md) |
| The dated critical reviews under `derived/` are the drafter's own and do not count as review. They are frozen. The newest, 2026.11.11, found 108 open items no list carries, and is not dispositioned | G12 item 121; checkpoints/README.md |

G12 §8, "What G12 does not claim", is the shortest honest summary of all of this.

## 3. The rule for resolving disagreements

The corpus has layers, and they are ranked.

| Rank | Layer | Path | Changes how |
|---|---|---|---|
| 1 | **State of record** | [`checkpoints/`](checkpoints/) (currently G12) | Never revised; a new checkpoint is cut. Errata are in `checkpoints/README.md` |
| 2 | **Decisions** | [`decisions/`](decisions/README.md) | Only by typed History rows: amendment, erratum, revision before ratification, dependent entry |
| 3 | **Narrative** | [`narrative/`](narrative/README.md) | Revised against each checkpoint, after it is cut, and tagged |
| 4 | **Evidence** | [`spec/`](spec/README.md), [`floor/`](floor/README.md), [`mechanism/`](mechanism/README.md), [`slm/`](slm/README.md) | Results files are dated and never edited; frozen modules change only as successors |
| 5 | **Derived** | [`derived/`](derived/README.md), [`diagrams/`](diagrams/README.md) | Dated and frozen; a new one is written |

A disagreement between layers is a finding, whichever layer is right. The author's own lists of known
disagreements are G12 §7, items 89 to 94, 98, 102, 103, 106, 108, 111, 113 and 119, and §11 of the
[format and schema inventory](derived/topak-format-and-schema-inventory-2026.10.03.md), which predates the
reference's 2026.10.05 rebuild.

**Mind the working tree.** G12 was cut at commit `0a1bc8d` (tag `G12`), and `main` has moved since. At `ffd02f1`
(2026.11.20):

- **Batch 40** (2026.11.17) ratified ADR-0033 A19 and A20. ADR-0077 was revised twice (R1, R2: the custodian's
  answers Q1 to Q3, tla-kit `v0.4.0` pinned in `tools/TLA-KIT-PIN`, the TLA+ checks run in its image) and ADR-0069
  once (R4). ADR-0077's status note still says its sections "have not run on GitHub"; the `results` workflow has
  since run them on `main` and passed (2026.11.20), so that sentence is behind the tree.
- **The narrative was revised against G12** after it was cut: Theory of Operation revision 16 (tag `ToO-rev16`), the
  glossary (tag `glossary-2026.11.16`) and the architecture description's revision 4 (untagged). G12's manifest
  measures their predecessors.
- **`spec/` grew**: `Paxos.tla` and `PaxosTrace.tla` with their results and the trace replay (2026.11.14, pinned by
  the reference); `Workflow_A1.tla` and its proof, certification and scan (2026.11.20, a draft successor); three more
  deadlock audits; a rebuilt specification graph (`specification-graph-results-2026.11.17.txt`, the check passing
  with fifteen stale edges), which `Workflow_A1` has since put behind the tree again (§5).
- **Seven derived documents were added** (2026.11.16 to 2026.11.20), one of them undated and marked DRAFT. Five
  entries under `derived/` have no row in its index (§9).
- **The diagrams were amended** on 2026.11.17 against G12 and Batch 40: six new, fifteen amended, fifty-nine in the
  family. They now cover ADR-0056 to ADR-0058 and ADR-0069 to ADR-0077; nothing is drawn for `Paxos.tla` or
  `Workflow_A1`, and H9's counts predate the rebuilt graph.
- **Twenty-three of G12's 1,100 entries differ at today's tree**: three records (ADR-0033, ADR-0069, ADR-0077), the
  three narrative heads, four files of the `writing-tla-specs-and-proofs` skill, ten under `spec/` (scripts, the
  wrapper `smt-checked`, `proof-certification.md`, `modules.tsv`, the graph), and three under `tools/` (`TLAPS-PIN`,
  `check-pins.sh`, `ci-plan.sh`). No results file, proof module or checkpoint moved. `SHA256SUMS-REF-2026.11.16b`
  differs in one entry, the pin file, as A20 says it should. Every manifest verifies in full at the commit it
  measured (`tools/verify-manifest.sh --all`, 2026.11.20).
- **Eighteen pull requests are open** (2026.11.20), nearly all derived documents from cloud sessions. None is on
  `main` and none is part of the corpus until merged.

Agree with the custodian which manifest digest you are reviewing, and check out that commit. The two candidates are
`G12` (`0a1bc8d`) and the head of `main`, which no manifest measures until G13 is cut.

## 4. Reading order

About a day for the first pass; the records and specifications are the weeks.

1. **[README.md](README.md)**. The five roles and the layout.
2. **[Theory of Operation](narrative/theory-of-operation.md) §0, §1, §13, §12**, in that order: how to read it,
   the pattern, the assumptions of use, and where the author thinks the argument is thin. Then the rest.
3. **[Residual-risk statement](derived/topak-residual-risk-statement-2026.11.11.md)**. What is not guaranteed,
   in order of severity.
4. **[G12](checkpoints/topak-genesis-checkpoint-G12-2026.11.16.md)**. Status of every record, the debt ledger (§4),
   the open list (§7, items 1 to 122), the non-claims (§8), what the manifest measures (§9).
5. **[Glossary](narrative/glossary.md)**, as needed. The vocabulary is dense and several words (*rung*, *floor*,
   *round*, *provisional*) carry more than one meaning; §13 lists the hazards and §10.1 the terms the twenty-two
   records drafted since G11 would add.
6. **The records**, starting with the ones everything rests on:

   | Read first | Why |
   |---|---|
   | ADR-0007, ADR-0010, ADR-0015 | The premise: no semantic judgment in the admit path; a verified floor; effects are enumerated |
   | ADR-0024 to ADR-0027 | The bootstrap set: promotion, the trust anchor, the rules floor, resident genesis rules. **These can never have a confirmation vote; your review is the only one they get** |
   | ADR-0029 | The process you are part of |
   | ADR-0030, ADR-0031, ADR-0034 | Policy composition, the lease, confinement |
   | ADR-0047 to ADR-0049 | What an agent is given: labelled ingress, handles, the tool list, the allowlist entry. The newest ratified design, and the corpus's answer to prompt injection |
   | ADR-0050, ADR-0052 | **Provisional.** Who may put a lease on the log, and break-glass. Read each record's ratification condition first: it says what was not built |
   | ADR-0045, ADR-0046 | What is trusted without proof (thirty-seven rows in force), and what the proofs do and do not show. ADR-0046 A2 is the prover's two known unsound cases; A3 the upstream report |
   | ADR-0053 | The second method of proof, Lean 4: what *proved in Lean* claims, the premise each use adds, and the one route it is confirmation-required for |
   | ADR-0033 | What the reference implementation is evidence of. Its §7 addenda, A1 to A20, are the history of what was built when; A20 is the consensus log's model |
   | ADR-0054, ADR-0055 | **Proposed.** How one cell's work reaches another: a promoted graph, an orchestrator that only narrows, a mesh under a budget. Built at the reference before ratification, and proved. `Workflow_A1` is a drafted successor the record does not yet carry |
   | ADR-0059 to ADR-0068 | **Proposed, an overlay.** TOPAK as the top tier of a command chain: planes that only narrow, vehicles with a trusted governor, revocation bounded in effects, an irreversible effect only a person's. Eight modules proved; no floor, no code. Read ADR-0068 first: it is the overlay's own trusted base and what it gives up |
   | ADR-0056 to ADR-0058, ADR-0069 to ADR-0077 | **Proposed.** User scope; the specification graph; the Build-Run pipeline and CI; lifecycle security; user documentation and the archive; the TLA+ tools in an image. Only CI, the graph and the image pin are built. ToO §0 says where each is described |
   | ADR-0035, ADR-0036, ADR-0051 | **Proposed since September and October.** Lineage independence, the rung-1 launcher, the correlator's folds. ADR-0036 §7 is not met as written by the one rung-1 run that exists (G12 item 119) |

7. **[`spec/theorem-premise-binding.md`](spec/theorem-premise-binding.md)**. One row per checked property, with
   everything it assumes. This is the table to attack. Since Batch 36 it carries derived premises, so a theorem
   with two derivations can be carried by either. Its rows cite eighteen modules. **Twenty-two modules with
   results have no row**: `Labels`, `ToolList`, `Operators`, `Emergency`, `Correlator`, the `_A1` successors of
   `BreakGlass` and `NonComposition`, the two liveness extensions, `Workflow`, `Mesh`, the overlay's eight, and
   three added since G12 (`Paxos`, `PaxosTrace`, `Workflow_A1`). G12 item 90 counts eighteen; the graph checker's
   own list (`specification-graph.py check`, "no binding row") is the one above less `Workflow_A1`, which the graph
   does not hold yet. For those modules, read each one's results file and the record that cites it;
   `spec/specification-graph.json` holds their edges.

Two aids, neither authoritative: the [diagram family](diagrams/README.md) (start with A1, A2, D1, H1 and H2; drawn
at G10 and amended through 2026.11.17; each amended diagram names its state in its footer), and a draft
[architecture description](narrative/architecture-description.md), revised against G12, that lists the parts, the
runtime scenarios and a guarantee-to-evidence table, with the blocks the Proposed records would add.

## 5. Checking it yourself

Do not take a results file's word. Everything below can be re-run; each directory's README has the details. The
"At `ffd02f1`" column is what each check reported on 2026.11.20.

| Check | Command | Needs | At `ffd02f1` |
|---|---|---|---|
| Every manifest matches the tree it measured | `tools/verify-manifest.sh --all` | git, shasum | every one of the thirty-three dated manifests verifies as its index row expects; G1 and G2 predate git and verify in part, as recorded |
| Every cited path resolves | `python3 tools/check-refs.py` | python3 | exits 1, ratcheted in CI: twenty missing paths and 113 date tokens not in the house form, all predating CI; 140 citations resolve through the 2026.09.30 layout map (`-v` lists them) |
| The three tool pins agree | `tools/check-pins.sh` | shasum | agree; reports that the image's prover is not the pinned one, by design until ADR-0077 §5 |
| A TLA+ module: invariants hold, every mutation fails, every witness is reached | `cd spec && ./<module>-run.sh`, or `live-gen-results.sh` with the module's rows file (`spec/modules.tsv` lists the drivers) | Java; the jar is tracked at `tools/tla2tools.jar` | |
| A proof | `cd spec && ./proof-results.sh <Module>_proof` | TLAPS via `tools/install-tlaps.sh` (large download) | |
| A proof's certification: every obligation accounted for by the route that closed it | `cd spec && ./proof-cert.sh <Module>_proof`; method in [spec/proof-certification.md](spec/proof-certification.md) | TLAPS, cvc5 1.4.0, the pinned `ethos` checker | |
| Every proof module reruns to the same outcome | `tools/check-proofs.sh` | TLAPS | CI's `proofs` job, in the tla-kit image, unpinned |
| Proofs still match the modules they prove | `cd spec && ./proof-sync.sh` | | exits 0; thirty-five in sync, seven base modules state why they have no proof |
| No proof rests on the prover's known unsound cases | `spec/proof-scan.sh`; method in spec/proof-certification.md §10 | TLAPS, cvc5, the pinned `ethos` checker; about a quarter of an hour | four scan files cover the thirty-five |
| The Lean results: every theorem kernel-checked and replayed, and in step with the tree and the pin | each package's `results.sh` (`spec/lean/`, `mechanism/lean/`, `floor/lean/`); `tools/lean-sync.sh` | Lean via `tools/install-lean.sh` (elan, about 2 GB); the floor package also needs `cedar` | `lean-sync` exits 1, by decision (item 103) |
| The policy floor: validate, behavioural tests, gates. The floor in force is the `emergency` stage under `floor/proposed/`; the reference links the `workflow` stage | see [floor/README.md](floor/README.md) "Running" | `cedar` built with `--features analyze`, cvc5 1.4.0, the pinned `ethos` checker | unchanged since G11 |
| The bundle policies | OPA's test runner over [`policies/`](policies/) | OPA (a container is enough) | |
| The reference's tests | `cd mechanism && scripts/build-bundle.sh && cargo test --workspace --release` | Rust, Docker | 159 at A20 |
| The reference still follows the records it cites | `cargo test -p topak-core --test drift` | | ratcheted in CI |
| The reference's admit path matches its operational model | see [mechanism/README.md](mechanism/README.md) "Run it" (trace lines); `spec/mechanism-trace-results.sh` | Java | not rerun since A14 (item 56) |
| The reference's replicas match `Paxos.tla` | `spec/paxos-trace-results.sh`, after a traced run of `topak-paxos`'s simulation | Java, Rust | `Paxos-trace-results-2026.11.14.txt` |
| Which theorems a declared configuration keeps | `python3 spec/inventory.py <declaration.json>`; `--check` keeps the table and its matrix in step | python3; a declaration you write (the script's header gives the shape) | |
| The prover's two known cases still reproduce under the pin | `spec/defects/defects-run.sh`; expectations in `spec/proof-certification.md` §8 | TLAPS, cvc5, the pinned `ethos` checker, Java | |
| The specification graph and every theorem's grade (Proposed, ADR-0057) | `cd spec && python3 specification-graph.py check` | python3 | exits 1: `proof-sync.sh` reads `Workflow_A1_proof.tla`, which no edge of the graph holds, since the proof was added after the graph was rebuilt on 2026.11.17; fifteen stale edges, two premise-route verdicts moved by them. The 2026.11.17 results file records the check passing on that tree |
| Where a module can stop with no successor | `spec/deadlock-audit.sh` | Java | five results files; no stray deadlock |
| Nothing frozen is changed between two commits | `python3 -I .github/scripts/frozen-files.py <base> <head>` | python3, git | runs on every pull request |

Some cautions:

- **Do not run `tools/install-tla.sh` casually.** It downloads a jar over the tracked one, whose digest the results
  files cite.
- **A fresh TLAPS install may not be the pinned prover.** The upstream release tag was rebuilt; `tools/TLAPS-PIN`
  and [spec/README.md](spec/README.md) explain, and the wrapper refuses an unpinned binary unless told otherwise.
  The tla-kit image's prover (`tools/TLA-KIT-PIN`) is another build again; a result under it is a result of a
  different trust root (ADR-0077, Proposed).
- **Do not run the reference against anything you care about.** Its replica channel is unauthenticated, and
  whoever reaches its operator socket can seat a principal.
- **The floor stage files open with a comment that is wrong** ("not what the reference follows"). It is false of the
  `workflow` stage, which the reference links. The bytes are kept as gated so the cited digests hold (G12 item 91).
- **One sync check fails, and says why.** `tools/lean-sync.sh` exits 1 because `mechanism/lean` is stale, by the
  custodian's decision (item 103); CI ratchets it. `spec/proof-sync.sh` exits 0. Neither is a regression you
  introduced.
- **The pinned prover can prove false statements.** If you write or change a proof module, follow
  `spec/proof-certification.md` §10 and run the scan on it. A build that fixes the cases exists upstream (`ff40755`),
  and is not the pinned one.
- **The drift test fixes the repository's root when it is compiled.** If you have more than one working tree, run
  `cargo clean -p topak-core` before it, or it may check another tree's pins (G12 item 120).
- **`Workflow_A1` is a draft.** Its module, proof and results exist and certify; no record cites them, and ADR-0054
  has no A1 row. Read it as evidence of a finding against `Workflow.tla` (a workflow left running at its end, found
  by the 2026.11.20 deadlock audit), not as a design in force.

## 6. Where to push

The author's view of the weak points, as a starting list. You should not trust it to be complete.

- **Vacuity.** The corpus's founding worry is a property that is true because it constrains nothing. For any
  invariant, ask what mutation breaks it and whether that mutation is the one that matters. For the floor, ask
  what request each policy actually refuses.
- **The bootstrap set** (ADR-0024 to ADR-0027) and the single axiom it rests on: an authentic issuance is what the
  anchor intended.
- **Model against prose.** Does each TLA+ module say what its record says? Several past findings were a model
  that omitted the path a rule was about (ToO §11.3). The newest is the workflow stall above: ADR-0054 §9 fails a
  workflow when its epoch is fenced, and `Workflow.tla` fails only the nodes running at the fence.
- **Proof hypotheses.** Each theorem is proved under the absence of the mutations that break it, and under named
  assumptions. Check the hypotheses are not doing the work.
- **Code against model.** The trace harness shows the code agrees with an operational model on tested paths. The
  model was written from the code, by the same hand, on the same day. `Paxos.tla` is the second such model, of the
  replicas, and is not proved.
- **The trusted base** (ADR-0045 Annex A). Is any component relied on that is not a row? Is any row's failure
  direction misjudged?
- **Effect exclusivity.** The central safety claim is conditional on confinement that is designed and not built.
  Is the condition stated everywhere the claim is used?
- **Collusion.** Detection fails open against an Observer colluding with the agent it watches. Is the stated cover
  (lineage independence, ADR-0035, Proposed) adequate even in principle?
- **Whether the floor is the right floor.** The gates check that the floor is well-formed. Nothing checks that it
  is fit for purpose. Since ADR-0029 A4 that judgment is yours, and no test for it is written.
- **The provisional records.** ADR-0050's centre is that a first lease comes from a quorum; at the reference a
  marked bootstrap path seats instead. X1, the old break-glass exception, was retired on a record that is itself
  subject to redesign. Ask whether a design should be in force on those terms, and whether its exits are the right
  ones (G12 items 88 and 92).
- **Labels are declarations.** The three label forbids read what a source was declared to be. Ask what a wrong
  declaration costs, whether the three paths are the right minimum, and what the deciding replica is trusted for
  (G12 item 93).
- **Operators watch each other by presence.** An add needs a live peer, and nothing says what the peer must have
  read.
- **The prover's front end.** Two unsound cases were found in the prover's translation by reviewing one module's
  proofs. A scan and one reading say no cited result rests on either, and no check detects the first. Ask what else
  the translation could do, and whether the rule for writing proofs is enough.
- **Proved in Lean.** Each use adds a premise that is read and not checked: that the encoding is the module, the
  transcription the Rust, the model the code, the parse the policy. The graph check and the trace replay are checks
  beside two of them. Ask where the reading is doing the work, and read one transcription against its source.
- **Workflows** (Proposed). The orchestrator may only choose among enabled edges, guards read only settled
  attributes, and a route is checked again at apply. Ask whether `Route` is really an emission and not a third kind of
  authority change (ADR-0054 finding 3), and whether two parallel branches of one lineage need to differ.
- **Liveness.** The coupling stall is shown to end only under fairness: the Observer regranted and keeping up, a
  refused Thinker asking again, grants being made (ToO §13, A12 and A18). Ask whether a deployment can meet them.
- **The command-chain overlay** (Proposed). It answers a sentence the archetype holds, that no principal grants
  another, by letting a mechanism delegate. Ask whether "an overlay, not the archetype" is a status ADR-0029 knows
  (the self review's CR-40 says it is not), whether a plane's clock as a quorum's count of ticks is a safety premise
  in disguise, and whether four trusted-base rows that meet neither of ADR-0045's tests should be rows at all.
- **The specification graph** (Proposed). Ask whether a grade is partial credit, which would need ADR-0023 amended
  (ADR-0057 finding 3), and why every theorem the reference keeps grades *trusted* and nothing higher.
- **The toolchain under the corpus.** The prover pin, the image pin and the Lean pin name three different
  decisions about what a result is a result of (ToO §12 item 24). Ask what moving any of them does to every
  results file that cites it, and who decides.
- **Self-consistency of the process.** Records ratified within days of drafting; records the assistant drafted;
  a reference built ahead of the records it follows, for two days before Batch 34 and again since 2026.10.08;
  eleven batches ratified in five days; twenty-two records drafted in ten days and none read by another; a module
  and its proof written and certified on one day (2026.11.20) for a record that does not yet cite them.

ToO §12 lists twenty-five such places. The
[critical review of 2026.11.11](derived/topak-critical-review-2026.11.11.md) lists findings CR-40 to CR-61, with an
[open-findings register](derived/topak-open-findings-register-2026.11.11.md) of every earlier finding; the
[critical review of 2026.10.02](derived/topak-critical-review-2026.10.02.md) lists CR-1 to CR-39; the
[scenario findings](derived/scenarios-2026.11.12/FINDINGS_TOPAK.md) list SF-1 to SF-26; and the
[design-gap assessment](derived/topak-design-gap-assessment-2026.10.03.md) separates gaps in the design from gaps in
the build. All are the author's or the assistant's, and none is dispositioned in full.

## 7. Reporting findings

A finding is most useful when it names:

1. **What it is against**: the file, and the manifest (`manifests/SHA256SUMS-*`) or commit you read it at.
2. **The claim**, quoted or closely paraphrased.
3. **Why it is wrong**: a counterexample trace, a failing model configuration, a request the floor should deny
   and does not, or a written argument.
4. **Where you think the fix belongs**: the claim, the specification, the policy or the code.

**A wrong safety claim goes through the private channel first**, not a public issue: GitHub's private
vulnerability reporting on this repository, or the address in [SECURITY.md](SECURITY.md), which also gives the
response windows (acknowledgement within five business days, an assessment within fifteen more). Ordinary defects
that do not bear on a safety claim can be public issues.

Each finding will be applied, declined with written reasons, or carried as named debt, and the disposition
recorded. A change moves the manifest digest, so review and corpus converge by iteration. You are free to publish
after the assessment window whatever the outcome.

## 8. Conventions you will trip over

- **Dates** are `YYYY.MM.DD`. Files are named with their date and, once dated, do not change.
- **Digests** identify everything. A record cites a module or a results file by digest; the reference pins every
  record it follows in `mechanism/corpus-pins.sha256` (sixty-three lines: forty-two records, twenty-one modules).
- **Status words are exact.** *Accepted (genesis)*, *Proposed*, *pending* (an amendment drafted and not
  ratified; fifteen today, all on Proposed records), *an overlay, not the archetype* (a Proposed record's deployment
  position, ADR-0059 to ADR-0068), *confirmation-required* (C1 to C4), *author-ratified*, *provisional* (in force
  and subject to redesign, with its exit stated), *genesis-provisional* (the floor: ratified at bootstrap).
  *Checked* means model-checked at small constants; *proved* means proved of the module by the TLA+ Proof System;
  *proved in Lean* means the Lean kernel discharged it, of the encoding, transcription or statement it names;
  *certified* means every obligation's proof was machine-checked or is accounted for; *trace-validated* means a
  recorded run of the code replays through an operational model; none of them means reviewed.
- **Identifiers.** `ADR-nnnn` a record, with `§n`, `An` (amendment), `En` (erratum), `Rn` (revision), `Bn` (the
  batch that ratified); `Gn` a checkpoint; `T-0045-n` a trusted-base row; `D-nnnn-n` a declared degeneracy;
  `B1`–`B14` boundaries (and `B1`–`B29` in ADR-0070); `R1`–`R9` rules-floor entries; `F1`–`F6` forensic classes;
  `P1`–`P7` confinement-profile clauses; `CR-n` a critical-review finding; `SF-n` a scenario finding; `In` and `Gn`
  in `mechanism/` an assumption and a gap of the reference; `W1`–`W10` an allowlist entry's load checks (ADR-0056,
  Proposed, would add `W11`–`W13`);
  ⟨K1⟩–⟨K9⟩ and ⟨M1⟩–⟨M5⟩ what the custodian settled for ADR-0054 and ADR-0055, ⟨Q1⟩ a custodian's answer to a
  proposal's numbered question, and other marks each record declares; `T-0068-n` and `T-0070-n` proposed
  trusted-base rows; `TM1`–`TM14` the overlay's adversaries; `F1`–`F9` either the frozen-files guard's rules or
  ADR-0070's findings, beside ADR-0028's forensic classes `F1`–`F6`. `R3` to `R7` and `B6`, `B10` are also
  floor-policy names, `C1`–`C9` are floor entries as well as `C1`–`C4` confirmation criteria, and `G` numbers also
  name diagrams; context decides, and the glossary's §13 lists the collisions.
- **Paths moved once**, on 2026.09.30. Frozen files cite old paths; `checkpoints/README.md` holds the map.
- **`PROVISIONAL (<tag>)`** in the Rust marks every place a gap or assumption lives.
- **`SIMULATED`** means run under test keys standing in for hardware or a verifier. It is a witness that a path is
  reachable and claims nothing.
- **`BOOTSTRAP`** marks the reference's unsigned operator path wherever it stands in for a quorum or a promotion.
- **`Mut = "none"`** in a results file is the unmutated run; a row named for a mutation is expected to fail, and a
  `Never…` property is a witness that must be violated. A results file in which everything passes is a finding.

## 9. What is in scope, and what is not

ADR-0029 A2 asks for a review of "the entire corpus, at one named manifest digest". This section says what that
digest measures and what it does not, so that scope is a decision and not an accident. SECURITY.md draws the line
more widely for reports: everything tracked at the default branch or at a tagged checkpoint is in scope there.

### 9.1 In scope: what `SHA256SUMS-G12` measures

1,100 entries at `0a1bc8d`, by area (G12 §9), with what the tree holds today beyond them. The counts are of
tracked files; `git ls-files <dir> | wc -l` reproduces them.

| Area | Entries at G12 | What they are | Today (`ffd02f1`) |
|---|---|---|---|
| `decisions/` | 76 | every record file, ADR-0001 to ADR-0077 less 0014 | 76; three changed since G12 (ADR-0033 by Batch 40, ADR-0069 R4, ADR-0077 R1 and R2) |
| `checkpoints/` | 13 | the v1 corpus manifest and G1 to G12 | 13, unchanged |
| `narrative/` | 12 | the three heads (Theory of Operation, glossary, architecture description) and nine archived revisions | 12; all three heads revised against G12 after the cut |
| `derived/` | 287 | 54 dated documents and 233 files in five directories (`sdd-equivalents-2026.11.06`, `recon-fleet-7-2026.11.10`, `recon-fleet-7-simulation-2026.11.10`, `topak-self-review-annex-2026.11.11`, `scenarios-2026.11.12`) | 294; seven documents added |
| `spec/` | 321 | 41 TLA+ modules, 34 proof modules, every results file, the rows files, the run and generator scripts, `spec/defects/` (13 listings), `spec/lean/` (the TopakSpec package and its results), the premise binding, the specification graph and its checker, `modules.tsv`, `proof-certification.md`, `proof-method.md` | 343; 22 added (`Paxos`, `PaxosTrace`, `Workflow_A1` and their results and scripts, three deadlock audits, a scan, a graph result) and ten changed |
| `floor/` | 170 | the genesis floor in Cedar, its schema, values and tests, the gate runner and its results and evidence, the four proposed stages (`labels`, `control`, `emergency`, `workflow`) with their gate results, the cvc5-checked evidence, `floor/lean/` | 170, unchanged since G11 |
| `process/` | 6 | the genesis cleanup's logs of 2026.09.15 to 09.17 | 6, unchanged |
| `manifests/` | 20 | the nineteen reference manifests `SHA256SUMS-REF-*` and the rehearsal manifest `SHA256SUMS-SLM-2026.09.28`, measured in turn | 21: `SHA256SUMS-REF-2026.11.16b` added |
| `tools/` | 63 | `tla2tools.jar`, `tools/cpc/` (the proof checker's rule signature), the four pin files, the CI scripts, `check-pins.sh`, `ratchet.py` | 65: `TLA-KIT-PIN` and `check-proofs.sh` added; `TLAPS-PIN`, `check-pins.sh` and `ci-plan.sh` changed |
| `skills/` | 132 | four skills packaged as plugins: `writing-tla-specs-and-proofs`, `writing-lean-encodings-and-proofs`, `generating-corpus-diagrams`, `auditing-claims-against-evidence` | 133; one skill changed in four files, one file added |

**Measured by their own tree manifests, which G12 measures in turn:**

| Tree | Manifest | Commit | Entries | Note |
|---|---|---|---|---|
| `mechanism/` and `policies/` | `SHA256SUMS-REF-2026.11.16b` (the measure of the reference since Batch 40) | `36269bc` | 116 | one entry, `corpus-pins.sha256`, differs at today's tree, as ADR-0033 A20 says it should. G12 itself names `-2026.11.16` at `d1b72db` |
| `slm/` | `SHA256SUMS-SLM-2026.09.28` (the lineage rehearsal only) | `7542730` | 40 | `slm/` has 58 tracked files today. The rung-1 occupant run (`slm/occupant-rung1-results-2026.11.11.txt`) is cited by digest in G12 §2.3 and measured by no manifest |

### 9.2 Out of scope of the manifest, and present in the repository

These are tracked and are not measured by any manifest (`manifests/EXCLUDE`). Read them; cite them by commit, not by
manifest. A finding against one is still a finding.

| Path | Tracked files | What it is | Why excluded |
|---|---|---|---|
| `README.md`, `REVIEWERS_GUIDE_README.md`, `ADOPTERS_GUIDE_README.md`, `SECURITY.md`, `LICENSE`, `LICENSE-DOCS`, `NOTICE`, `CODEOWNERS`, `.gitignore` | 9 | the root conveniences and the licence | kept current; a convenience is not a record. The adopter's guide is marked work in progress with no independent reader |
| `decisions/README.md`, `derived/README.md`, `spec/README.md`, `checkpoints/README.md`, `process/README.md`, `narrative/README.md`, `manifests/README.md` | 7 | directory indexes | conveniences, revised in place. Every other README is measured: `floor/`'s three, `spec/lean/`'s, the skills', the five inside `derived/` directories and `tools/cpc/`'s by G12, and `mechanism/`'s and `slm/`'s by their tree manifests |
| `diagrams/` | 124 | the diagram family (fifty-nine SVGs under `diagrams/topak/`, one older SVG, the generators and their library) | not measured, by decision (G12 item 76); a diagram is derived and decides nothing |
| `.claude/` | 195 | the assistant's settings and four project skills (`drafting-records`, `ratifying-records`, `cutting-manifests`, `use-case-simulator`) that encode this repository's own procedures | tooling for the drafter, not the corpus. G12 §5 notes that the drafting conventions of ADR-0054 to ADR-0077 are set out here and not measured |
| `.github/` | 12 | the four workflows (`checks`, `frozen-files`, `results`, `sources`), the frozen-files guard, the five rulesets as JSON, `CONTRIBUTING.md` | the carrier, not the corpus (ADR-0069, Proposed). The rulesets in force are GitHub's copy; the JSON is the reviewable text |
| `manifests/SHA256SUMS`, `SHA256SUMS-G1` to `-G12`, `index.tsv`, `EXCLUDE` | 17 | the checkpoint manifests themselves, their index and the exclusion list | a manifest cannot measure itself; `index.tsv` names the commit each verifies at |
| `tools/tlc`, `tlc-workers`, `tlapm`, `install-tla.sh`, `install-tlaps.sh`, `install-lean.sh`, `install-ethos.sh`, `cut-manifest.sh`, `verify-manifest.sh`, `check-refs.py`, `lean-report.sh`, `lean-sync.sh` | 12 | wrappers, installers and checkers | they run the checks and are not evidence; the jar and pins they read are measured |
| `mechanism/`, `policies/`, `slm/` beyond their tree manifests | | files added or changed after the manifest's commit | measured at the next reference or rehearsal cut |

### 9.3 Not in the repository

| What | Where | Status |
|---|---|---|
| `doc/` | the custodian's working tree only | gitignored third-party reference material (the NIST AI RMF Playbook, the SICI drafts, Moon and Varshney, vendor guides) and local drafts. Not redistributed; SECURITY.md puts third-party material out of scope, and ToO §11 and the dated assessments under `derived/` are where the corpus reads it |
| The prover, the Lean toolchain, cvc5, ethos | `tools/tlaps-*`, `~/.elan`, `tools/cvc5-*`, `tools/ethos-*` | installed by the scripts, identified by the pin files and by the digest each results file prints. The pin files are measured; the binaries are not |
| TLC's working files, Lake's build directories, Cargo's target | `spec/*.cfg`, `spec/Trace_*.tla`, `spec/states/`, `*/.lake/`, `mechanism/target/` | regenerated; the `Trace_*` modules are written from the reference's traces on each replay |
| Session exports | `sessions/`, `cloud.ai.exports/` | gitignored; the process logs under `process/` are what was recovered from them in September |
| Eighteen open pull requests | GitHub | derived documents, a CLAUDE.md, a tool-host bound; none merged, none part of the corpus |

### 9.4 In the repository, and not where a reader would look

- **Five entries under `derived/` have no row in its index**: `recon-fleet-7-2026.11.10/`,
  `recon-fleet-7-simulation-2026.11.10/` (both G12 item 12), `topak-assessment-2026.10.03.md`,
  `topak-assisted-development-house-style-proposal-DRAFT.md` (undated, the only undated file under `derived/`) and a
  PDF rendering of the 2026.10.05 external assessment, which is gitignored and untracked.
- **`REF-2026.11.16b` has no tag**; `index.tsv` names its commit. `REF-2026.11.16` tags the earlier cut.
- **The architecture description is untagged** at every revision; its digest at each cut is the manifest's row.
- **ADR-0077's status note** says its built sections "have not run on GitHub"; they have, on `main`, since PR #91
  merged on 2026.11.18.
- **`Workflow_A1`** has a module, a proof, a certification, a scan and a deadlock audit, and no record cites any of
  them.

### 9.5 What a review of G12 would not cover

If you review at `G12`, the following exist on `main` and are outside your digest: Batch 40 and its two addenda;
`Paxos.tla`, `PaxosTrace.tla` and `Workflow_A1`; ADR-0077 R1 and R2 and ADR-0069 R4; revision 16 of the Theory of
Operation and the glossary and architecture description against G12; seven derived documents; six new and fifteen
amended diagrams; the tla-kit pin and the image's run in CI. If you review at the head of `main`, no manifest
measures it until G13 is cut, and the custodian should cut one for the attestation.
