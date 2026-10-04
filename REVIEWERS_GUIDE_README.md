# TOPAK — Reviewer's Guide

**2026.10.03** · DRAFT · written against Genesis Checkpoint G9 and Theory of Operation revision 13 · a convenience,
not a record: where this guide and the checkpoint disagree, the checkpoint wins

**Drafted by the assistant** at the custodian's request. Like most of this corpus, it has not been read by anyone
independent of its author. If it steers you away from something, treat that as a finding.

---

## 1. What you are being asked to do

TOPAK is an architecture pattern for multi-agent systems that treats every agent as Byzantine and keeps models out
of the trusted computing base. This repository is its design corpus, plus a Rust reference implementation of one
path through it. Nothing here is deployable ([SECURITY.md](SECURITY.md)).

**You would be its first independent reader.** Every record, specification, proof, policy, test and line of code
was written or ratified by one person, working with an AI assistant. The corpus says so repeatedly, and its own
rules make your review a precondition for the next phase:

- ADR-0029 A2 requires an **independent review of the entire corpus, at one named manifest digest, by at least one
  reviewer who is not the author**, before the system's trust anchor may bootstrap.
- The review is complete when **every finding is dispositioned**: applied as a change, declined with recorded
  reasons, or carried as named debt.
- The review's attestation (who reviewed, which digest, what scope, how findings were disposed) is signed into the
  genesis bundle.

A partial review is still useful. Say what you read and at which digest, and it will be recorded as that.

## 2. What state the corpus is in

Read this before forming a view of how finished anything is.

| Fact | Where it is stated |
|---|---|
| Forty decision records are accepted; twenty-two of them are marked as needing independent confirmation | [G9](checkpoints/topak-genesis-checkpoint-G9-2026.10.02.md) §1 |
| "Accepted" means ratified by the sole custodian. It is a declaration, not a review | ToO §0, §9 |
| Seven texts were drafted by the assistant; four are ratified and three are pending | ToO §0 |
| No reviewer is engaged and no review pass has been completed | [checkpoints/README.md](checkpoints/README.md) |
| The policy floor is a draft that passes its gates; no floor is ratified | [floor/README.md](floor/README.md) |
| Every numeric parameter is a placeholder; nothing has been measured | [Residual-risk statement](derived/topak-residual-risk-statement-2026.10.03.md) §4 |
| The proofs are of the TLA+ modules, not of the running code. No refinement exists | G9 §8; ADR-0045 T-0045-28 |
| At the reference, no real principal is confined. Every theorem about confinement is void there | G9 §8 |
| The dated critical reviews under `derived/` are the drafter's own and do not count as review | checkpoints/README.md |

G9 §8, "What G9 does not claim", is the shortest honest summary of all of this.

## 3. The rule for resolving disagreements

The corpus has layers, and they are ranked.

| Rank | Layer | Path | Changes how |
|---|---|---|---|
| 1 | **State of record** | [`checkpoints/`](checkpoints/) (currently G9) | Never revised; a new checkpoint is cut. Errata are in `checkpoints/README.md` |
| 2 | **Decisions** | [`decisions/`](decisions/README.md) | Only by typed History rows: amendment, erratum, revision before ratification, dependent entry |
| 3 | **Narrative** | [`narrative/`](narrative/README.md) | Revised and tagged with each checkpoint |
| 4 | **Evidence** | [`spec/`](spec/README.md), [`floor/`](floor/README.md), [`mechanism/`](mechanism/README.md), [`slm/`](slm/README.md) | Results files are dated and never edited; frozen modules change only as successors |
| 5 | **Derived** | [`derived/`](derived/README.md), [`diagrams/`](diagrams/README.md) | Dated and frozen; a new one is written |

A disagreement between layers is a finding, whichever layer is right. The author's own list of known
disagreements is §11 of the
[format and schema inventory](derived/topak-format-and-schema-inventory-2026.10.03.md).

**Mind the working tree.** G9 was cut at commit `97a61e8` (tag `G9`). The default branch has moved since: three
Proposed records (ADR-0047 to ADR-0049), several derived documents and the redrawn diagrams are later than G9.
Agree with the custodian which manifest digest you are reviewing, and check out that commit.

## 4. Reading order

About a day for the first pass; the records and specifications are the weeks.

1. **[README.md](README.md)**. The five roles and the layout.
2. **[Theory of Operation](narrative/theory-of-operation.md) §0, §1, §13, §12**, in that order: how to read it,
   the pattern, the assumptions of use, and where the author thinks the argument is thin. Then the rest.
3. **[Residual-risk statement](derived/topak-residual-risk-statement-2026.10.03.md)**. What is not guaranteed,
   in order of severity.
4. **[G9](checkpoints/topak-genesis-checkpoint-G9-2026.10.02.md)**. Status of every record, the debt ledger (§4),
   the open list (§7), the non-claims (§8).
5. **[Glossary](narrative/glossary.md)**, as needed. The vocabulary is dense and several words (*rung*, *floor*,
   *round*) carry more than one meaning; the glossary says which.
6. **The records**, starting with the ones everything rests on:

   | Read first | Why |
   |---|---|
   | ADR-0007, ADR-0010, ADR-0015 | The premise: no semantic judgment in the admit path; a verified floor; effects are enumerated |
   | ADR-0024 to ADR-0027 | The bootstrap set: promotion, the trust anchor, the rules floor, resident genesis rules. **These can never have a confirmation vote; your review is the only one they get** |
   | ADR-0029 | The process you are part of |
   | ADR-0030, ADR-0031, ADR-0034 | Policy composition, the lease, confinement |
   | ADR-0045, ADR-0046 | What is trusted without proof, and what the proofs do and do not show |
   | ADR-0033 | What the reference implementation is evidence of |

7. **[`spec/theorem-premise-binding.md`](spec/theorem-premise-binding.md)**. One row per checked property, with
   everything it assumes. This is the table to attack.

Two aids, both derived and neither authoritative: the [diagram family](diagrams/README.md) (start with A1, A2, D1
and H1), and a draft [architecture description](narrative/architecture-description.md) that lists the parts, the
runtime scenarios and a guarantee-to-evidence table.

## 5. Checking it yourself

Do not take a results file's word. Everything below can be re-run; each directory's README has the details.

| Check | Command | Needs |
|---|---|---|
| Every manifest matches the tree it measured | `tools/verify-manifest.sh --all` | git, shasum |
| Every cited path resolves | `python3 tools/check-refs.py` | python3 |
| A TLA+ module: invariants hold, every mutation fails, every witness is reached | `cd spec && ./<module>-run.sh` | Java; the jar is tracked at `tools/tla2tools.jar` |
| A proof | `cd spec && ./proof-results.sh <Module>_proof` | TLAPS via `tools/install-tlaps.sh` (large download) |
| Proofs still match the modules they prove | `cd spec && ./proof-sync.sh` | |
| The policy floor: validate, behavioural tests, gates | see [floor/README.md](floor/README.md) "Running" | `cedar` built with `--features analyze`, cvc5 1.4.0, the pinned `ethos` checker |
| The bundle policies | OPA's test runner over [`policies/`](policies/) | OPA (a container is enough) |
| The reference's tests | `cd mechanism && scripts/build-bundle.sh && cargo test --workspace --release` | Rust, Docker |
| The reference still follows the records it cites | `cargo test -p topak-core --test drift` | |
| The reference's behaviour matches the operational model | see [mechanism/README.md](mechanism/README.md) "Run it" (trace lines) | |
| Which theorems a declared configuration keeps | `python3 spec/inventory.py <declaration.json>`; `--check` keeps the table and its matrix in step | python3; a declaration you write (the script's header gives the shape) |

Three cautions:

- **Do not run `tools/install-tla.sh` casually.** It downloads a jar over the tracked one, whose digest the results
  files cite.
- **A fresh TLAPS install may not be the pinned prover.** The upstream release tag was rebuilt; `tools/TLAPS-PIN`
  and [spec/README.md](spec/README.md) explain, and the wrapper refuses an unpinned binary unless told otherwise.
- **Do not run the reference against anything you care about.** Its operator and replica channels are
  unauthenticated.

## 6. Where to push

The author's view of the weak points, as a starting list. You should not trust it to be complete.

- **Vacuity.** The corpus's founding worry is a property that is true because it constrains nothing. For any
  invariant, ask what mutation breaks it and whether that mutation is the one that matters. For the floor, ask
  what request each policy actually refuses.
- **The bootstrap set** (ADR-0024 to ADR-0027) and the single axiom it rests on: an authentic issuance is what the
  anchor intended.
- **Model against prose.** Does each TLA+ module say what its record says? Several past findings were a model
  that omitted the path a rule was about (ToO §11.3).
- **Proof hypotheses.** Each theorem is proved under the absence of the mutations that break it, and under named
  assumptions. Check the hypotheses are not doing the work.
- **Code against model.** The trace harness shows the code agrees with an operational model on tested paths. The
  model was written from the code, by the same hand, on the same day.
- **The trusted base** (ADR-0045 Annex A). Is any component relied on that is not a row? Is any row's failure
  direction misjudged?
- **Effect exclusivity.** The central safety claim is conditional on confinement that is designed and not built.
  Is the condition stated everywhere the claim is used?
- **Collusion.** Detection fails open against an Observer colluding with the agent it watches. Is the stated cover
  (lineage independence, ADR-0035, Proposed) adequate even in principle?
- **Whether the floor is the right floor.** The gates check that the floor is well-formed. Nothing checks that it
  is fit for purpose, and the corpus says this gate has no owner.
- **Self-consistency of the process.** Records ratified within days of drafting; records the assistant drafted;
  a reference built ahead of the records it follows.

ToO §12 lists sixteen such places, the
[critical review of 2026.10.02](derived/topak-critical-review-2026.10.02.md) lists findings CR-1 to CR-39, and
the [design-gap assessment](derived/topak-design-gap-assessment-2026.10.03.md) separates gaps in the design from
gaps in the build. All three are the author's.

## 7. Reporting findings

A finding is most useful when it names:

1. **What it is against**: the file, and the manifest (`manifests/SHA256SUMS-*`) or commit you read it at.
2. **The claim**, quoted or closely paraphrased.
3. **Why it is wrong**: a counterexample trace, a failing model configuration, a request the floor should deny
   and does not, or a written argument.
4. **Where you think the fix belongs**: the claim, the specification, the policy or the code.

**A wrong safety claim goes through the private channel first**, not a public issue: GitHub's private
vulnerability reporting on this repository, or the address in [SECURITY.md](SECURITY.md), which also gives the
response windows. Ordinary defects that do not bear on a safety claim can be public issues.

Each finding will be applied, declined with written reasons, or carried as named debt, and the disposition
recorded. A change moves the manifest digest, so review and corpus converge by iteration. You are free to publish
after the assessment window whatever the outcome.

## 8. Conventions you will trip over

- **Dates** are `YYYY.MM.DD`. Files are named with their date and, once dated, do not change.
- **Digests** identify everything. A record cites a module or a results file by digest; the reference pins every
  record it follows in `mechanism/corpus-pins.sha256`.
- **Status words are exact.** *Accepted (genesis)*, *Proposed*, *pending* (an amendment drafted and not
  ratified), *confirmation-required* (C1 to C4), *author-ratified*. *Checked* means model-checked at small
  constants; *proved* means proved of the module; neither means reviewed.
- **Identifiers.** `ADR-nnnn` a record, with `§n`, `An` (amendment), `En` (erratum), `Rn` (revision); `Gn` a
  checkpoint; `T-0045-n` a trusted-base row; `D-nnnn-n` a declared degeneracy; `B1`–`B14` boundaries; `R1`–`R9`
  rules-floor entries; `F1`–`F6` forensic classes; `P1`–`P7` confinement-profile clauses; `CR-n` a critical-review
  finding; `In` and `Gn` in `mechanism/` an assumption and a gap of the reference. `R3`, `R4` and `B6`, `B10` are
  also floor-policy names, and `G` numbers also name diagrams; context decides.
- **Paths moved once**, on 2026.09.30. Frozen files cite old paths; `checkpoints/README.md` holds the map.
- **`PROVISIONAL (<tag>)`** in the Rust marks every place a gap or assumption lives.
- **`SIMULATED`** means run under test keys standing in for hardware or a verifier. It is a witness that a path is
  reachable and claims nothing.
