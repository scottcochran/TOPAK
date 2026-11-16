# TOPAK — Reviewer's Guide

**2026.11.16** · DRAFT · written against Genesis Checkpoint G12 and Theory of Operation revision 16 · a convenience,
not a record: where this guide and the checkpoint disagree, the checkpoint wins. It is kept current and is not
measured by any manifest (`manifests/EXCLUDE`)

**Drafted by the assistant** at the custodian's request. Like most of this corpus, it has not been read by anyone independent of its author. If it steers you away from something, treat that as a finding.

---

## 1. What you are being asked to do

TOPAK is an architecture pattern for multi-agent systems that treats every agent as Byzantine and keeps models out
of the trusted computing base. This repository is its design corpus, plus a Rust reference implementation of one
path through it. Nothing here is deployable ([SECURITY.md](SECURITY.md)).

Every record, specification, proof, policy, test and line of code
was written or ratified by one person, working with an AI assistant. The corpus says so repeatedly, and its own rules make your review a precondition for the next phase:

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

Read this before forming a view of how finished anything is.

| Fact | Where it is stated |
|---|---|
| Forty-seven decision records are accepted; twenty-nine of them are marked as needing independent confirmation | [G12](checkpoints/topak-genesis-checkpoint-G12-2026.11.16.md) §1.1, §4 |
| "Accepted" means ratified by the sole custodian. It is a declaration, not a review | ToO §0, §9 |
| **Two records are provisional**: in force, and subject to redesign. ADR-0050 (the operator as a principal) was ratified without its central behaviour built; ADR-0052 (break-glass as an emergency seating) rests on it. Every amendment that depends on either is provisional too | G12 §1.2; ADR-0029 A4 |
| **Twenty-seven records are Proposed**, twenty-two of them drafted since G11 and none in force. Two, ADR-0054 and ADR-0055 on workflows, are already built at the reference, which links a floor stage that is not the floor in force. Sixteen amendments are pending, fifteen on Proposed records | G12 §1.1, §2.2; ADR-0033 A16 |
| Nearly every text ratified since 2026.10.02 was drafted by the assistant, and everything drafted since G11: twenty-two records, four amendments, ten proof modules, a specification graph, a CI pipeline and a rung-1 run | ToO §0; G12 §4 |
| No reviewer is engaged and no review pass has been completed. Two reviews since G11 were fresh sessions of the same model, and say so | G12 §4; [checkpoints/README.md](checkpoints/README.md) |
| No floor is ratified. The floor in question is gated and genesis-provisional: ratified when the bootstrap reviewer finds it fit | G12 §2.2; ADR-0030 A3 |
| Every numeric parameter is a placeholder; nothing has been measured | [Residual-risk statement](derived/topak-residual-risk-statement-2026.11.11.md) |
| The proofs are of the TLA+ modules, not of the running code. No refinement exists. Thirty-four proof modules, 13,622 obligations; thirty-one certify, three do not. Ten are under Proposed records, eight of them of a command-chain design with no floor and no code. Fifteen modules' theorems are proved again in Lean, of re-encodings | G12 §2.9, §8; ADR-0045 T-0045-28 |
| **The prover is known to be unsound in two ways.** A rule and a scan keep a proof from them, and no check detects the first. Both are reported upstream and partly fixed there, and **the pinned build has both** | G12 §2.6, §2.9, item 104; ADR-0046 A2, A3 |
| No liveness property is proved. Coupling's are checked by TLC at small constants | G12 §8, item 105; ToO §5.5 |
| At the reference, no real principal is confined. Every theorem about confinement is void there. One guest passes P3, as the rung-1 launcher asserts on DEV rules | G12 §2.3, §8 |
| CI runs on every pull request and gates nothing: the ruleset that would require its checks is disabled | G12 §8, item 114 |
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

**Mind the working tree.** G12 was cut at commit `0a1bc8d` (tag `G12`). The narrative was revised against it
afterwards: Theory of Operation revision 16, the glossary of 2026.11.16 and the architecture description's revision 4
are later than G12's manifest, which measures their predecessors. The diagrams were drawn against G10 and amended
since, among them for workflows and the command-chain overlay; several are behind G12, and nothing is drawn for
ADR-0057, ADR-0058 or ADR-0069 to ADR-0077 (G12 item 76). The derived documents are older still. Agree with the
custodian which manifest digest you are reviewing, and check out that commit.

## 4. Reading order

About a day for the first pass; the records and specifications are the weeks.

1. **[README.md](README.md)**. The five roles and the layout.
2. **[Theory of Operation](narrative/theory-of-operation.md) §0, §1, §13, §12**, in that order: how to read it,
   the pattern, the assumptions of use, and where the author thinks the argument is thin. Then the rest.
3. **[Residual-risk statement](derived/topak-residual-risk-statement-2026.11.11.md)**. What is not guaranteed,
   in order of severity.
4. **[G12](checkpoints/topak-genesis-checkpoint-G12-2026.11.16.md)**. Status of every record, the debt ledger (§4),
   the open list (§7), the non-claims (§8).
5. **[Glossary](narrative/glossary.md)**, as needed. The vocabulary is dense and several words (*rung*, *floor*,
   *round*, *provisional*) carry more than one meaning; the glossary says which (§13).
6. **The records**, starting with the ones everything rests on:

   | Read first | Why |
   |---|---|
   | ADR-0007, ADR-0010, ADR-0015 | The premise: no semantic judgment in the admit path; a verified floor; effects are enumerated |
   | ADR-0024 to ADR-0027 | The bootstrap set: promotion, the trust anchor, the rules floor, resident genesis rules. **These can never have a confirmation vote; your review is the only one they get** |
   | ADR-0029 | The process you are part of |
   | ADR-0030, ADR-0031, ADR-0034 | Policy composition, the lease, confinement |
   | ADR-0047 to ADR-0049 | What an agent is given: labelled ingress, handles, the tool list, the allowlist entry. The newest ratified design, and the corpus's answer to prompt injection |
   | ADR-0050, ADR-0052 | **Provisional.** Who may put a lease on the log, and break-glass. Read each record's ratification condition first: it says what was not built |
   | ADR-0045, ADR-0046 | What is trusted without proof, and what the proofs do and do not show. ADR-0046 A2 is the prover's two known unsound cases |
   | ADR-0053 | The second method of proof, Lean 4: what *proved in Lean* claims, the premise each use adds, and the one route it is confirmation-required for |
   | ADR-0054, ADR-0055 | **Proposed.** How one cell's work reaches another: a promoted graph, an orchestrator that only narrows, a mesh under a budget. Built at the reference before ratification, and proved |
   | ADR-0059 to ADR-0068 | **Proposed, an overlay.** TOPAK as the top tier of a command chain: planes that only narrow, vehicles with a trusted governor, revocation bounded in effects, an irreversible effect only a person's. Eight modules proved; no floor, no code. Read ADR-0068 first: it is the overlay's own trusted base and what it gives up |
   | ADR-0056 to ADR-0058, ADR-0069 to ADR-0077 | **Proposed.** User scope; the specification graph; the Build-Run pipeline and CI; lifecycle security; the archive and user documentation; the TLA+ tools in an image. Only CI and the graph are built. ToO §0 says where each is described |
   | ADR-0033 | What the reference implementation is evidence of |

7. **[`spec/theorem-premise-binding.md`](spec/theorem-premise-binding.md)**. One row per checked property, with
   everything it assumes. This is the table to attack. Since Batch 36 it carries derived premises, so a theorem
   with two derivations can be carried by either. It has no rows yet for eighteen modules added since 2026.10.04
   (`Labels`, `ToolList`, `Operators`, `Emergency`, two successors, two liveness extensions, `Workflow` and `Mesh`, and
   the command-chain overlay's eight); for those, read each module's results file beside its record.

Two aids, neither authoritative: the [diagram family](diagrams/README.md) (start with A1, A2, D1 and H1; drawn
at G10 and amended since, and behind G12 in places), and a draft
[architecture description](narrative/architecture-description.md), revised against G12, that lists the parts, the
runtime scenarios and a guarantee-to-evidence table, with the blocks the Proposed records would add.

## 5. Checking it yourself

Do not take a results file's word. Everything below can be re-run; each directory's README has the details.

| Check | Command | Needs |
|---|---|---|
| Every manifest matches the tree it measured | `tools/verify-manifest.sh --all` | git, shasum |
| Every cited path resolves | `python3 tools/check-refs.py` | python3 |
| A TLA+ module: invariants hold, every mutation fails, every witness is reached | `cd spec && ./<module>-run.sh` | Java; the jar is tracked at `tools/tla2tools.jar` |
| A proof | `cd spec && ./proof-results.sh <Module>_proof` | TLAPS via `tools/install-tlaps.sh` (large download) |
| A proof's certification: every obligation accounted for by the route that closed it | `cd spec && ./proof-cert.sh <Module>_proof`; method in [spec/proof-certification.md](spec/proof-certification.md) | TLAPS, cvc5 1.4.0, the pinned `ethos` checker |
| Proofs still match the modules they prove | `cd spec && ./proof-sync.sh` | |
| No proof rests on the prover's known unsound cases | `spec/proof-scan.sh`; method in spec/proof-certification.md §10 | TLAPS, cvc5, the pinned `ethos` checker; about a quarter of an hour |
| The Lean results: every theorem kernel-checked and replayed, and in step with the tree and the pin | each package's `results.sh` (`spec/lean/`, `mechanism/lean/`, `floor/lean/`); `tools/lean-sync.sh` | Lean via `tools/install-lean.sh` (elan, about 2 GB); the floor package also needs `cedar` |
| The policy floor: validate, behavioural tests, gates. The floor in force is the `emergency` stage under `floor/proposed/`; the reference links the `workflow` stage | see [floor/README.md](floor/README.md) "Running" | `cedar` built with `--features analyze`, cvc5 1.4.0, the pinned `ethos` checker |
| The bundle policies | OPA's test runner over [`policies/`](policies/) | OPA (a container is enough) |
| The reference's tests | `cd mechanism && scripts/build-bundle.sh && cargo test --workspace --release` | Rust, Docker |
| The reference still follows the records it cites | `cargo test -p topak-core --test drift` | |
| The reference's behaviour matches the operational model | see [mechanism/README.md](mechanism/README.md) "Run it" (trace lines); `spec/mechanism-trace-results.sh` | Java |
| Which theorems a declared configuration keeps | `python3 spec/inventory.py <declaration.json>`; `--check` keeps the table and its matrix in step | python3; a declaration you write (the script's header gives the shape) |
| The prover's two known cases still reproduce under the pin | `spec/defects/defects-run.sh`; expectations in `spec/proof-certification.md` §8 | TLAPS, cvc5, the pinned `ethos` checker, Java |
| The specification graph and every theorem's grade (Proposed, ADR-0057) | `python3 spec/specification-graph.py check` | python3. It does not pass today, and says why |
| The tracked TLC jar is the pinned one | `tools/check-pins.sh` | shasum |
| Nothing frozen is changed between two commits | `python3 -I .github/scripts/frozen-files.py <base> <head>` | python3, git |

Some cautions:

- **Do not run `tools/install-tla.sh` casually.** It downloads a jar over the tracked one, whose digest the results
  files cite.
- **A fresh TLAPS install may not be the pinned prover.** The upstream release tag was rebuilt; `tools/TLAPS-PIN`
  and [spec/README.md](spec/README.md) explain, and the wrapper refuses an unpinned binary unless told otherwise.
- **Do not run the reference against anything you care about.** Its replica channel is unauthenticated, and
  whoever reaches its operator socket can seat a principal.
- **The floor stage files open with a comment that is wrong** ("not what the reference follows"). It is false of the
  `workflow` stage, which the reference links. The bytes are kept as gated so the cited digests hold (G12 item 91).
- **One sync check fails at G12, and says why.** `tools/lean-sync.sh` exits 1 because `mechanism/lean` is stale, by the
  custodian's decision (item 103); CI ratchets it. `spec/proof-sync.sh` exits 0. Neither is a regression you
  introduced.
- **The pinned prover can prove false statements.** If you write or change a proof module, follow
  `spec/proof-certification.md` §10 and run the scan on it. A build that fixes the cases exists upstream (`ff40755`),
  and is not the pinned one: a result under it is a result of a different trust root (ADR-0077, Proposed).
- **The drift test fixes the repository's root when it is compiled.** If you have more than one working tree, run
  `cargo clean -p topak-core` before it, or it may check another tree's pins (G12 item 120).

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
- **Self-consistency of the process.** Records ratified within days of drafting; records the assistant drafted;
  a reference built ahead of the records it follows, for two days before Batch 34 and again since 2026.10.08;
  eleven batches ratified in five days; twenty-two records drafted in ten days and none read by another.

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
response windows. Ordinary defects that do not bear on a safety claim can be public issues.

Each finding will be applied, declined with written reasons, or carried as named debt, and the disposition
recorded. A change moves the manifest digest, so review and corpus converge by iteration. You are free to publish
after the assessment window whatever the outcome.

## 8. Conventions you will trip over

- **Dates** are `YYYY.MM.DD`. Files are named with their date and, once dated, do not change.
- **Digests** identify everything. A record cites a module or a results file by digest; the reference pins every
  record it follows in `mechanism/corpus-pins.sha256`.
- **Status words are exact.** *Accepted (genesis)*, *Proposed*, *pending* (an amendment drafted and not
  ratified; sixteen at G12, fifteen of them on Proposed records), *an overlay, not the archetype* (a Proposed
  record's deployment position, ADR-0059 to ADR-0068), *confirmation-required* (C1 to C4), *author-ratified*,
  *provisional* (in force and subject to redesign, with its exit stated), *genesis-provisional* (the floor: ratified
  at bootstrap). *Checked* means model-checked at small constants; *proved* means proved of the module by the TLA+
  Proof System; *proved in Lean* means the Lean kernel discharged it, of the encoding, transcription or statement it
  names; *certified* means every obligation's proof was machine-checked or is accounted for; none of them means
  reviewed.
- **Identifiers.** `ADR-nnnn` a record, with `§n`, `An` (amendment), `En` (erratum), `Rn` (revision); `Gn` a
  checkpoint; `T-0045-n` a trusted-base row; `D-nnnn-n` a declared degeneracy; `B1`–`B14` boundaries; `R1`–`R9`
  rules-floor entries; `F1`–`F6` forensic classes; `P1`–`P7` confinement-profile clauses; `CR-n` a critical-review
  finding; `In` and `Gn` in `mechanism/` an assumption and a gap of the reference; `W1`–`W10` an allowlist's load
  checks; ⟨K1⟩–⟨K9⟩ and ⟨M1⟩–⟨M5⟩ what the custodian settled for ADR-0054 and ADR-0055, ⟨Q1⟩ a custodian's answer to
  a proposal's numbered question, and other marks each record declares; `T-0068-n` and `T-0070-n` proposed
  trusted-base rows; `TM1`–`TM14` the overlay's adversaries; `F1`–`F9` either the frozen-files guard's rules or
  ADR-0070's findings, beside ADR-0028's forensic classes `F1`–`F6`. `R3` to `R7` and `B6`, `B10` are also floor-policy names, `C1`–`C9` are floor entries as well as
  `C1`–`C4` confirmation criteria, and `G` numbers also name diagrams; context decides, and the glossary's §13
  lists the collisions.
- **Paths moved once**, on 2026.09.30. Frozen files cite old paths; `checkpoints/README.md` holds the map.
- **`PROVISIONAL (<tag>)`** in the Rust marks every place a gap or assumption lives.
- **`SIMULATED`** means run under test keys standing in for hardware or a verifier. It is a witness that a path is
  reachable and claims nothing.
- **`BOOTSTRAP`** marks the reference's unsigned operator path wherever it stands in for a quorum or a promotion.
