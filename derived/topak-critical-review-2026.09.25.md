# TOPAK — Critical Review

**2026.09.25** · derived · review, not a record · basis: Theory of Operation rev 7 (`e8f4b3a107ae7020…`), Genesis
Checkpoint G3 (`2198e90059a658e7…`), the record files at their G3 digests, `spec/`, `floor/`, `policies/`,
`mechanism/` and `slm/` at the current tree, the 09.16 critical review, and the three documents in `doc/`: Moon &
Varshney arXiv:2605.09045v2, the NIST AI RMF Playbook, and the NIST AI RMF TACIP discussion draft of 2026.09.13(b).
Integrity commands (`shasum -a 256 -c`, `opa test` via Docker) were run against this tree and their results are
stated where they carry weight; TLC, the Cedar gates, and `cargo test` were **not** re-run. · prepared by Claude
(Fable 5) in one session at the custodian's request

Nothing here is ratified, and this document proposes no decision text. Findings continue the 09.16 review's tags:
CR-1…CR-20 belong to that review; CR-21 onward are new. The brief differs from 09.16's: this review **grades the
pattern against the documents in `doc/`**, which the 09.16 review predates.

---

## 0. Verdict

TOPAK is an unusually honest and internally rigorous corpus whose **delivered guarantee is far below its designed
guarantee, and the repo mostly says so itself**. The grades:

| Graded against | Grade | In one sentence |
|---|---|---|
| Moon & Varshney (arXiv:2605.09045v2) | **B** | High conceptual fidelity and genuine extensions, but the paper's defining artifact — a machine-checked refinement from spec to running code — is absent, so in the paper's own guarantee ordering TOPAK today delivers *Empirical*, not *Universal* |
| TACIP discussion draft (2026.09.13b) | **B** | A strong, largely convergent instantiation of the profile's hardest technical asks (P5 identity, P7 policy-as-code, P10 logging, P4 break-glass); the operational/human half is out of scope by design; the 3.9.5 enforceability pentad fails on *Verifiable* and *Timely* |
| NIST AI RMF Playbook | **B−** | Exemplary on documentation, change management, and MANAGE 2.4 outcomes; failing on MEASURE 1.3 (independence) and on measurement of any actual model behavior, because no model runs |
| The repo as evidence for the pattern | **B+ / C** | B+ as an architecture corpus — the integrity chain, mutation discipline, and self-accounting all verify; C as evidence that the architecture *works* — A1 undischarged, no Observer, zero independent review |

The pattern's most distinctive virtue is that it grades itself almost this harshly: rev 7 §12's nine thin places
and G3 §8's "What G3 does not claim" anticipate most of this review. The most distinctive vice is the recursion it
does not survive — a corpus whose premise is that Build authors are Byzantine, ratified end to end by its own
author at custody (1, 0).

---

## 1. What was verified, and held

Stated first because the grades below lean on it. The following were **run against this tree**, not read from
results files:

- `shasum -a 256 -c SHA256SUMS-G3`: **86 of 86 OK.**
- The checkpoint chain: G3's header digest for G2 matches the G2 file exactly; G2's for G1 likewise. The
  G1 → G2 → G3 chain is cryptographically coherent.
- `SHA256SUMS-G2`: 58/64 OK, and the six failures are exactly the six records G3 §1/§6 record as amended after
  G2's cut (0003, 0015, 0021, 0022, 0024, 0026). Expected and documented.
- `SHA256SUMS-REF-2026.09.25`: 59/61 OK, and the two failures are the two files ADR-0033 E1 predicted
  (`GAPS-AND-ASSUMPTIONS.md`, `corpus-pins.sha256`). The checkpoint predicted its own manifest's failures.
- `mechanism/corpus-pins.sha256`: **24 of 24 pins verify**, and `tests/drift.rs` fails the build when a pinned
  record changes or an unpinned record is cited.
- The floor digests pinned in the Rust floor crate match `floor/genesis-floor.cedar` and
  `floor/genesis.cedarschema` and the digests cited in `floor/genesis-gates-results-2026.09.24.txt`.
- The OPA bundle tarball's content-revision filename recomputes from the current `policies/` tree.
- `opa test` (via the Docker image present on this machine): **14 of 14 pass**, and the tests assert denial
  *reasons*, not just decisions.
- The sha256 prefixes cited inside the TLA+ results headers match the current modules (`FloorComposition`,
  `FloorRouting`, `Confinement`, `Lease` checked).

Every TLA+ invariant ships with a must-fail mutation and a must-be-violated reachability witness, and the results
files record both. The Cedar gates carry three negative controls that must be caught. Very little in this repo is
theater. That is the finding that licenses everything below: where this review says the evidence is *insufficient*,
it does not mean the evidence is *fabricated*.

---

## 2. Grade against Moon & Varshney (arXiv:2605.09045v2): B

**What concords.** Havoc semantics; boundary-enforceable properties only; the closed typed alphabet; denials
modeled explicitly; models outside the TCB. Rev 7 §11.1's self-assessment of the concordance is accurate.

**Where TOPAK is genuinely ahead of the paper.**
- **Policy change cadence.** The paper verifies one fixed four-variant policy and never addresses change. The
  floor + monotone bundle composition (`admit ⟺ floor_permit ∧ ¬bundle_deny`, ADR-0030) with stale bundles
  monotone-safe under partition is a real extension.
- **Authority regress.** The rules floor over a havoc anchor (ADR-0025/0026) carries the paper's move one layer
  up, to the authority that defines who promotes. The paper has no counterpart.
- **The fourth gate.** §11.1 correctly reads the paper's own Appendix B negative result — silent abstention
  producing vacuously true corollaries past all three spec-quality gates — as proof that a floor-fitness gate is
  required. The paper names the need; TOPAK owns it as an open item (G3 item 2). Neither has built it.

**Where the grade is earned down.**
1. **The paper's central artifact is absent.** Moon & Varshney's contribution is a *deductive, machine-checked
   refinement chain*: abstract boundary spec → operational model → executable implementation, in Dafny, compiled
   to the deployed runtime, with Theorem 3.2 discharged mechanically. TOPAK has TLC model checking at small
   constants (2 principals, MaxEpoch ≤ 2, three-element ground sets, 5 humans), safety invariants only, no
   liveness, and the TLA+ mutations *hand-restated* as Rust tests with no mechanized link between `spec/` and
   `mechanism/`. In the paper's Table-1 ordering — S(Empirical) ⊆ S(Distributional) ⊆ S(Universal) — the
   guarantee TOPAK delivers today is **Empirical**. G3 §8 concedes this ("No theorem is proved"). The Cedar
   choice (ADR-0030) is a defensible partial substitute — the evaluator's Lean-checked semantics is real
   verification done by others — but composition is checked in TLC and *asserted* of the Rust code, not proved
   of it.
2. **Effect exclusivity is elevated rhetorically and discharged less than in the paper.** Rev 7 §4.1 calls the
   enumeration "a mechanism claim, strictly stronger than Moon & Varshney's assumed version." The paper assumes
   effect exclusivity and mandates sandboxing beneath the verified layer; TOPAK asserts the stronger claim with
   **no sandbox at all** — gap G1, every lease at rung 0, `Contained` empty, assumption A1 failing everywhere
   including in the reference. CR-1 stands as written in the 09.16 review. Until a confinement mechanism exists,
   the "strictly stronger" sentence is a liability in any publication.
3. **Register drift against the paper's own care.** Rev 7 still says "containment is proven against the floor"
   (§3.1), "a quorum predicate proven in TLA+" (§3.3), "safety is proven for every issuance" (§7.2), and "the
   TLA+ theorems are proved" (§8.1) — in a corpus whose state of record says no theorem is proved. The paper is
   scrupulous about what its verification does not cover (its §4.6, §5.1); the narrative's register is not yet,
   and this is the residue of CR-4.

---

## 3. Grade against the TACIP discussion draft: B

TACIP appears nowhere in the corpus by name, and none of TOPAK's vocabulary appears in the draft (verified by
search: no "TOPAK", "lease", "persona", "genesis", "TLA"; "floor" once, in an unrelated phrase). The alignment
below is convergent evolution, which makes it more informative, not less.

**Where the pattern lands squarely on the profile's hardest technical asks.**
- **P5 (IdAM for AI entities) — the strongest single alignment.** The lease (ADR-0031) is nearly a specification
  of TACIP 5.3.2: task-bounded, time-windowed, revocable authority with automatic expiration, one live credential
  per principal, narrowing-only renewal. Action-level runtime authorization (5.2.2) *is* the admit path. The MCP
  front door plus deterministic floor is the "guarded proxy" of 5.3.3: the probabilistic agent never holds
  execution credentials. Per-invocation non-human identities map to principal + seat + Persona + round.
- **P7 (internal supply chain).** Policy-as-code with OPA — 7.3.2 names OPA explicitly; cryptographic hashing for
  immutable lineage (7.2.2) is the manifest and pin discipline; signed-and-regression-tested safety-logic change
  (7.3.2) is promotion plus the gates. One material miss: **bundles are unsigned** (gap G7), which 7.3.2
  requires; bundle identity is a content revision until that closes (G3 item 18).
- **P10 (logging and audit).** Consensus-ordered admits, denials recorded (ADR-0020, plus the `after` topic),
  the six non-erasable forensic classes, erasure as a modeled event — this meets, and at legibility-vs-immutability
  exceeds, the profile's immutable/tamper-evident telemetry asks.
- **P4 / P13 (break-glass; retirement).** Targeted revocation vs. epoch fence is exactly 3.9.5's "sufficient in
  scope — not a single all-or-nothing stop"; quorum-on-roster matches multi-person authorization for high-impact
  intervention; revocation permanence plus resignation semantics per custody rung is a serious partial answer to
  P13's authority-withdrawal regime. The break-glass TTL (R8) is still pending — a break-glass grant with no
  expiry is precisely what P4/P13 would flag first.
- **4.5.1's time-constant audit.** `W + L + D < T_irrev`, with "an effect irreversible on emission must not be
  expressible in the alphabet at all" (ADR-0032), is a near-verbatim counterpart of TACIP's requirement to audit
  the paths where human intervention is not a primary control. But `L` is unmeasured, so the budget cannot be
  evaluated for any effect class — the *Timely* leg has a form and no number.

**The 3.9.5 enforceability pentad, scored.** Effective ✓ (revocation and fencing are mechanism, not policy).
Durable ✓ (renewal only narrows; revocation is permanent within the chain; re-grant is barred). Sufficient in
scope ✓ (restriction, suspension, rollback, and reduction are all distinct, ordered operations). Timely ✗ (`L`
unmeasured). **Verifiable ✗** — the draft demands verification "not the capability's self-attestation," from
incident records rather than a separate attestation process. Everything in this repo is attested by one person.
This is CR-5's finding restated in an external document's words, and it is the profile's sharpest cut.

**What the profile asks for that the pattern does not touch.** The entire operational and human half: TEVV of
actual model behavior against requirements (P1–P2), drift programs and Time-to-Divergence cadences (2.3.4),
attention governance and alarm-flood design (4.4), manual-mode continuity and re-commissioning gates (P11),
training and competency records (P9), AIBOM and vendor hazard-reachability attestations for external models (P6),
an incident response team (8.3). Some of this is out of scope for an architecture pattern and fairly so; some of
it — the Observer that does not exist (G12), the detection-fails-open finding (CR-2) — is squarely in scope and
open. A deployment claiming TACIP alignment via TOPAK alone would cover perhaps a third of the profile, weighted
toward the third the profile's other adopters will find hardest.

---

## 4. Grade against the NIST AI RMF Playbook: B−

Rev 7 §11.2's self-mapping is accurate, which is itself worth recording: the gaps the corpus names (MEASURE 2.13
floor fitness, MEASURE 3.2 `L`, MAP 3.4 operator proficiency, MANAGE 1.4 residual-risk statement, MANAGE 3.1
monoculture, MAP 2.3 TLC-versus-TLAPS — the last now half-declared via G3 §8) are confirmed by this pass.

**Where the pattern exceeds the Playbook's suggested actions.**
- **MANAGE 2.4** (supersede/disengage/deactivate): legibility, non-erasable stop attribution (F2), forensic
  preservation through erasure and break-glass, and ordered subtraction are a stronger answer than the Playbook's
  own action list. Rev 7 §11.2's claim that MANAGE 2.4 "is resolved by mechanism" is the one self-assessment this
  review endorses nearly as written — *as design*; no mechanism is deployed.
- **MANAGE 4.3** (change/incident database): the ADR corpus with typed amendments and errata, dated checkpoints,
  and hash manifests is a model answer to "database of system changes with version history and metadata."
- **GOVERN 1.4 / 1.7**: documentation with alternatives-considered is the ADR form itself; decommissioning
  semantics exist per custody rung and in P13-adjacent detail most organizations never write down.
- **MEASURE 2.8**: the confirmation-required markers, the debt ledger, and the declaration-record schema are
  literally "track and document policy exceptions and escalations."

**Where it fails.**
- **MEASURE 1.3** — independent assessors — is the Playbook's one recurring evidence-quality criterion, and the
  count of independent assessments is zero. The structure for corroboration (digests, pins, checked-in results)
  is unusually good; the corroboration has not happened.
- The behavioral **MEASURE** function is empty because no AI runs. The one place the repo asserts behavioral
  outcomes — `slm/` Part B's rehearsal claims — is the one place with no checked-in evidence (CR-22 below).
- **GOVERN 3.1** (diverse team): one person. **MAP 3.4**, **MEASURE 2.13**, **MEASURE 3.2**: open, as the corpus
  says.

The delta inventory and feature list in `derived/` predate two checkpoints (G3 item 12); the regeneration rev 7
§11.2 promises should treat this section as its input.

---

## 5. The 09.16 findings, six days on

| Tag | Status at this review |
|---|---|
| **CR-1** (effect exclusivity an assumption) | **Open.** ADR-0034 (Proposed) and `Confinement.tla` give the attestation-rung *design*; no mechanism exists; every lease is rung 0. The reference made the gap concrete rather than smaller (ADR-0033 §6, gap G1). |
| **CR-2** (detection fails open) | **Untouched.** No Observer exists (gap G12), no liveness coupling, no honeypots or elicitation tests; a dead, partitioned, or colluding Observer is still indistinguishable from a clean system. No record has been written against it. |
| **CR-3** (no delegation or chain model) | **Untouched.** Nothing in the corpus models multi-principal task provenance or coordination depth. |
| **CR-4** (formal layer promissory) | **Substantially discharged, register excepted.** Ten modules with mutations exist where one did; the TLC-not-TLAPS status is declared in G3 §8; a reference implementation exists and demonstrably improved the records (eleven findings, five records changed). Still no refinement from any spec to any implementation, and rev 7's prose still says "proven" in at least four places (§2 above). |
| **CR-5** (load-bearing records exempt from review) | **Open, and sharpened.** C1–C4 still never reach ADR-0007, 0010, 0012, or the Persona series; the bootstrap set is structurally unreviewable; and Batches 5–9 added nine records drafted, checked, implemented, and ratified by one person within two days. G3 §4 names it as a debt no confirmation repays. |
| **CR-6** (no flow constraints) | **Untouched.** No taint/label record exists. |

Two of the three high-severity operational findings (CR-2, CR-3) have had no motion in six days of otherwise
intense corpus activity. The activity went to authority, credentials, and the floor — the places the reference
forced — which is legitimate, but detection is the half of the architecture that still exists only as placement
rules for a component nobody has built.

---

## 6. New findings

| # | Finding | Severity |
|---|---|---|
| **CR-21** | **The recursion, stated as a grade.** By the pattern's own premise (Byzantine Build authors), TACIP 3.9.5 (*verifiable, not self-attestation*), and MEASURE 1.3, nothing in this corpus is yet evidence in the sense the documents in `doc/` require: 29 records ratified by their drafter, nine within 48 hours, checked by specs and code written by the same hand. The confirmation-marker machinery is a real mitigation *design*; zero confirmations have run; the bootstrap set never will. G3 §8 says this plainly — saying it does not discharge it. | High |
| **CR-22** | **`slm/` asserts outcomes with no checked-in evidence.** Part B's claims (gate suite "passes", monotonicity "fails as the ADR is written", projection "done") have every output gitignored, and the session file ADR-0035 and `slm/README.md` cite (`sessions/2026.09.25-SLM.md`) is gitignored too. This is the only area of the repo that breaks the otherwise uniform results-file discipline of `spec/` and `floor/`, and it is cited by a Proposed record. Either check in dated results files or strike the claims to "run, unrecorded". | Medium-High |
| **CR-23** | **No results file is reproducible end to end.** The results files are hand-assembled concatenations with no driver that regenerates one; the Cedar gates need `cedar` + `cvc5`, absent here; `spec/RulesFloorNV-run.sh` hardcodes a jar path that no longer resolves. The digest pinning makes the checked-in results trustworthy; it does not make them repeatable, and MAP 2.3's "corroboration by independent evaluators" needs repeatable. One driver script per results file would close this cheaply. | Medium |
| **CR-24** | **Unsigned trust edges under a signed corpus.** Bearer-token auth, no replica authentication, unsigned bundles (gaps G5/G7, G3 items 18 and 23): a swapped bundle tarball whose filename recomputes would be trusted by the very mechanism whose corpus is pinned to 24 digests. The asymmetry — record integrity best-in-class, runtime artifact integrity open — is the kind of gap the pattern's own A9 predicts. Acknowledged, but it belongs on the residual-risk statement's first page with anchor capture. | Medium-High |
| **CR-25** | **Register lag, small but persistent.** Rev 7's four present-tense "proven"s (§2 above); `mechanism/README.md` says 44 tests where `GAPS-AND-ASSUMPTIONS.md`'s evidence row still describes the 38-test 09.24 run; the root `SHA256SUMS` carries no in-file note that it is historical; `derived/` predates two checkpoints. Each is minor; together they are the gap between "state of record" and "state of prose," and CR-4's register finding was supposed to close exactly this class. | Low-Medium |

---

## 7. What would change the grades

In order of leverage per unit work:

1. **One independent confirmation pass** over any confirmation-required record. It converts self-attestation into
   evidence against all three documents simultaneously (TACIP 3.9.5, MEASURE 1.3, and the paper's A4-shaped
   correlated-review concern), and it exercises the promotion machinery the corpus has only modeled. Nothing else
   on this list moves three grades at once.
2. **A confinement-mechanism specification** for A1 — even a declared, testable sandbox profile for one deployment
   position. CR-1 is the pattern's largest gap, the corpus knows it, and sandboxing is commodity; this is
   integration and attestation work, not research.
3. **An Observer record answering CR-2** — liveness coupled to admission, or an explicit declared acceptance that
   detection fails open, on the residual-risk statement. Six days of silence on a High finding is itself a datum.
4. **Sign the bundles** (CR-24, G7). Small, closes a named TACIP 7.3.2 miss, and removes the asymmetry.
5. **Check in the `slm/` evidence** (CR-22) and **one driver script per results file** (CR-23).
6. **Regenerate the two Playbook artifacts** against G3 (item 12), using §4 of this review as the delta input.

---

## 8. Post-review dispositions (2026.09.25, same evening)

The sections above are the record of the review's cut; this section records what moved the same evening, after
the custodian committed that cut (`82d8c2b`).

**Doc-only fixes applied**, at the custodian's instruction; each is a working-tree change awaiting commit:

- **CR-25, rev 7 register.** The four "proven"/"proved" sentences (§3.1, §3.3, §7.2, §8.1) are corrected to
  "checked"/"must hold", with an erratum bullet added to rev 7's Appendix C. Rev 7 is cited by digest in no
  manifest or accepted record, so the frozen-artifact convention permits the in-place edit; its digest is now
  `f485fca37a216ebe…` (the basis line above cites the reviewed bytes, `e8f4b3a107ae7020…`).
- **CR-25, test count.** `mechanism/GAPS-AND-ASSUMPTIONS.md`'s evidence row now records both runs — 38 tests at
  `4fd9677`, 44 at `453801c` — removing the mismatch with `mechanism/README.md`, which was deliberately left
  untouched so ADR-0033 E1's file enumeration stays as ratified (the assumptions register is one of E1's two
  named files; the README is not).
- **CR-25, root manifest.** `SHA256SUMS` now opens with a two-line HISTORICAL comment. `shasum -a 256 -c`
  ignores `#` lines on this platform — verified before the edit — so verification behavior is unchanged.
- **CR-22, the doc half.** `slm/README.md` Part B now carries an evidence-status note marking its four claims
  **run, unrecorded**. Checking in dated results files remains open.
- After the edits, `SHA256SUMS-G3` still verifies **86 of 86**.

**A new finding, surfaced by making them.**

| # | Finding | Severity |
|---|---|---|
| **CR-26** | **A post-review commit falsified ADR-0033 E1 by enumeration.** Commit `f59941d` ("LICENSE files", 19:16) changed `mechanism/Cargo.toml` (`license = "UNLICENSED"` → `"Apache-2.0"`). `SHA256SUMS-REF-2026.09.25` now fails **three** entries where G3 §9 says to expect two, and E1's ratified sentence — later changes under `mechanism/` are "the assumptions register and the pin file — and no code" — no longer holds as written: `Cargo.toml` is a third file. A license field is not code, so the sentence's intent survives; its letter does not, and the letter is what was ratified. | Low |

The repair is erratum-class and the custodian's to ratify, not this review's: an ADR-0033 E2 extending the
enumeration, recorded the way Batch 9 recorded E1. Neither ADR-0033 nor G3 was touched here — both are measured
entries in `SHA256SUMS-G3`, and editing either breaks the manifest §1 verified. Worth noting: this is the second
time in two days the E1 sentence class has drifted, which suggests a sibling to G3 §5's one-results-file-per-run
convention — *a manifest's expected-failure list is part of the checkpoint that states it, and a commit that
grows the list owes the erratum in the same push.*

**ADR-0029 A2, drafted and ratified the same evening.** The custodian reversed the no-review declaration:
the bootstrap set's marker exclusion stands, but a full-corpus independent review — bootstrap set included — is
now a precondition of the ceremony, its attestation signed into the genesis bundle (A2.1–A2.5; C3, scoped to the
amendment). This answers the structural half of **CR-5** and **CR-21**: no record is now exempt from review by
construction. The evidential half stays open exactly as §7 item 1 states — the grade moves when a reviewer is
engaged and the review runs, not when the rule changed. The amendment's narrative pass moved rev 7's
digest again, to `cb43938d5e68c17c…`; rev 7 remains in no manifest.

**CR-22, closed the same evening.** The whole of `slm/` Part B was rerun in this session and captured to four
dated results files (`gate-suite-`, `e3-overlap-`, `independence-`, `rehearsal-results-2026.09.25.txt`).
Every recorded claim reproduced: the gate suite's cases and both monotonicity verdicts at the exact trial
counts (13/2000, 241/2000), the ×12 containment at 1.00000 (3,911 of 3,911), the §8 independence table at
9 of 28, and the rehearsal's honest-consistent / three-tampers-Contested verdicts, with the honest round's
training at 569 s against the recorded 551 s. The README's evidence-status note now points at the files.
The gitignored session citation remains (CR-25-adjacent), and the `full`-profile θ measurements stay the
author's call.

**The "strictly stronger" overclaim, resolved.** At the custodian's instruction, §2 item 2's liability
sentence is scrubbed: ADR-0015 E2 (ratified 2026.09.25) conditions the comparison on ADR-0022 §6's discharge —
until confinement is enforced the two positions are identical in strength — and rev 7 §4.1 now carries the
conditional form. The frozen rev 5 and rev 6 cuts and the documents that critique the old wording are
deliberately untouched. ADR-0015's entry in `mechanism/corpus-pins.sha256` was re-pinned, which under the
drift convention is the record that the change was reviewed against the code.

**Not done here**, being script, code, or process work: the `RulesFloorNV-run.sh` jar path and per-results-file
drivers (CR-23), bundle signing (CR-24), the slm results files (CR-22's other half), and the regeneration of the
two Playbook artifacts against G3 (§4 is the input).

---

## Sources

- `checkpoints/topak-theory-of-operation-2026.09.25-rev7.md` (`e8f4b3a107ae7020…`)
- `checkpoints/topak-genesis-checkpoint-G3-2026.09.25.md` (`2198e90059a658e7…`)
- `derived/topak-critical-review-2026.09.16.md` (CR-1…CR-20)
- `doc/2605.09045v2.pdf` — Moon & Varshney, "Containment Verification: AI Safety Guarantees Independent of
  Alignment," AIWILD @ ICML 2026
- `doc/DiscussionDraft_NIST_AIRMF_TACIP_20260913b.md` — Sheh & Stanley, NIST AI RMF TACIP profile, discussion
  draft, not official guidance
- `doc/AI_RMF_Playbook.pdf` — NIST AI RMF Playbook
- In-session verification: `shasum -a 256 -c` over `SHA256SUMS-G3`, `-G2`, `-REF-2026.09.25`,
  `mechanism/corpus-pins.sha256`; checkpoint-chain digests recomputed; `opa test` via Docker (14/14); floor and
  spec digest prefixes recomputed against results headers.
