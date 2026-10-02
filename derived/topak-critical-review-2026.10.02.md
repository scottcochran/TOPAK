# TOPAK — Critical Review

**2026.10.02** · derived · review, not a record · basis: Theory of Operation revision 13 (`5022ccaec0ca64b4…`), Genesis
Checkpoint G9 (`228422d80155862b…`), the record files, `spec/`, `floor/`, `policies/`, `mechanism/` and `slm/` at
commit `fccf374`, the 09.16 and 09.25 critical reviews, and three external documents: Moon & Varshney
arXiv:2605.09045v2 (`06e699209e2bd6ba…`), the NIST AI RMF TACIP community-of-interest discussion draft of 2026.09.13(b)
(`1a37852f316e819e…`), and the NIST AI RMF Playbook, pulled from the web on 2026.10.02. The Playbook was read from the
structured export mirrored at `github.com/Agent-Threat-Rule/ai-rmf-oscal-catalog` (`source/ai-rmf-playbook.json`,
`abf907645b9310d8…`, 72 subcategories with suggested actions and documentation prompts), because every `nist.gov`
host was refused by this session's network policy; the mirror's own cross-check reports that 41 of the 72
subcategory descriptions in NIST's JSON export differ in wording from the AI RMF Core text, so Core wording is used
where it matters. Integrity, proof-sync, reference-path and one TLC regeneration were **run against this tree**
and their results are stated in §1. The floor gates, the TLAPS proofs and the live smoke run were **not** re-run.
· prepared by Claude in one session at the custodian's request

Nothing here is ratified, and this document proposes no decision text. Findings continue the tags of the earlier
reviews: CR-1 to CR-20 are the 09.16 review's, CR-21 to CR-26 the 09.25 review's, and CR-27 onward are new. The brief
is the 09.25 brief: **grade the pattern against the three external documents, at the state of record**, and say what
moved in the seven days between G3 and G9.

---

## 0. Verdict

Seven days ago the delivered guarantee was far below the designed guarantee and the repository said so. Today the
gap is narrower in every place a single author can narrow it, and unchanged in the one place a single author cannot.
Fifteen TLA+ modules are proved as well as checked, every tested behaviour of the reference is replayed through an
operational model, a launcher issues the first leases above rung 0, a Run tool can be held to one declared network
target, bundles are signed, and detection no longer fails open against an absent Observer. None of that was true on
09.25. And every one of those artifacts was drafted, built, checked, proved and ratified by the same two hands in
the same seventeen days, with no second reader yet engaged: the recursion the 09.25 review called the pattern's
central weakness has grown faster than it has been answered.

| Graded against | 09.25 | **10.02** | In one sentence |
|---|---|---|---|
| Moon & Varshney (arXiv:2605.09045v2) | B | **B+** | The paper's universal guarantee now has a counterpart at the specification level (fifteen proofs, quantified over the constants), and the paper's defining artifact, a refinement to the running code, is still absent, so the guarantee delivered by anything that runs is still *Empirical* in the paper's own ordering |
| TACIP discussion draft (2026.09.13b) | B | **B+** | The profile's hardest technical asks (P5 identity, 7.3.2 signed policy-as-code, 10.1.2 the inference receipt, 13.2 authority withdrawal) now have mechanism behind them; the 3.9.5 enforceability pentad still fails on *Verifiable* and *Timely*, 13.2.2's cascading revocation has nothing to cascade through, and 12.2.1's warning about AI-written verifiers lands on this corpus by name |
| NIST AI RMF Playbook | B− | **B** | MAP 2.3 and MEASURE 2.1 close, MANAGE 3.2 moves, the mechanism's answers to MANAGE 2.3 and 2.4 strengthen; MEASURE 1.3 is still zero, MANAGE 1.4 is still unwritten after being named the highest-leverage document on 09.12, 09.16 and 09.25, and the two mapping artifacts are three weeks and eight checkpoints stale |
| The repo as evidence for the pattern | B+ / C | **A− / C+** | A− as an architecture corpus: every manifest verifies at the commit it measured, every proof is in sync with its module, a results file regenerates with identical outcomes; C+ as evidence that the architecture *works*: rung 1 trusts the host by construction, rung 3 is two test keys, the Observer is still an e2e fixture, and zero independent review |

The pattern's most distinctive virtue is unchanged: it grades itself about this harshly, and G9 §8's "What G9 does
not claim" anticipates most of this review. Its most distinctive vice is sharper: the corpus now ships proofs of its
own design written by the design's drafter, and its state of record is a revision behind its own narrative on the
day both were cut.

---

## 1. What was verified, and held

Run against this tree, not read from results files:

- **`tools/verify-manifest.sh --all`: every one of the 21 manifests verifies at the commit it measured**, G1 through
  G9, the ten reference cuts and the `slm/` cut, with each expected-failure count met exactly. (The session's clone
  was shallow at 53 commits; the check needs 137 and was run after unshallowing.)
- **`shasum -a 256 -c manifests/SHA256SUMS-G9` at today's tree: 390 of 392.** The two failures are
  `narrative/theory-of-operation.md` and `narrative/glossary.md`, revised after G9's cut in commit `9e811bc`. Expected,
  and the subject of CR-31.
- **`spec/proof-sync.sh`: 15 proof modules IN SYNC** with the modules they extend, and each of the five unproved base
  modules carries a reason. The obligation counts printed by the fifteen results files sum to **3,036**, the figure G9
  §2.9 states.
- **`spec/runconfinement-gen-results.sh` regenerated from `runconfinement-rows-2026.10.02.txt`: all 13 rows return
  the outcome the committed file records**, `Safe` holding in four, the two invariants violated under exactly the
  mutations stated, five witnesses violated. State counts on the nine counterexample rows differ from the committed
  file, as ToO §11.3 predicts for a parallel search. This is CR-23's "one driver per results file" working for one
  module; G9 item 78 is right that it is only "in part".
- **`tools/check-refs.py`: four missing paths**, three of them untracked installs the corpus declares as such
  (`tools/tlaps-1.6.0-pre/`, `tools/cvc5-macOS-arm64-static/`) and one a false positive on the string `tools/call` in
  the 10.01 competitive assessment.
- **The three citation-hygiene items the 10.01 competitive assessment could not verify** (it read the paper through
  summaries) are checked against the PDF here: Theorem 3.2 is the soundness theorem, not a "collapse case"; §4.6 and
  Appendix B carry the silent-abstention result and say nothing about human reviewers, so ToO §7.1's "unanimous humans
  … fail together (Moon & Varshney §4.6; Knight & Leveson)" owes the human half to Knight & Leveson alone; and the
  paper's trusted base (§3.4) does name the Dafny verifier and compiler, as ToO §11.1 item 7 says. The 09.10
  narrative's reading of Theorem 3.2 is in a closed revision; §7.1's sentence is live and still miscited.
- **`cargo test --workspace --release`: 103 tests across ten binaries, the count `mechanism/README.md` states.** On
  the first run, made while the workspace was still compiling on the same machine, three tests in
  `topak-node/tests/contain.rs` failed (`an_unreachable_verifier_grants_nothing`,
  `an_epoch_fence_voids_a_pending_appraisal`, `withdrawing_a_profile_fences_its_leases`; the binary took 54 s against
  3 s unloaded, and the revocation found no live lease to end). Five further runs of that binary, one under parallel
  load from four concurrent `e2e` runs, passed 13 of 13 each time. See CR-39.

Not re-run, for lack of the tools on this machine: the Cedar gates (`cedar-policy-cli`, cvc5, `ethos`), the TLAPS
proofs (the 1.9 GB prover is not tracked), and the live smoke run (G9 item 52, not rerun by anyone since 09.25).

As on 09.25: where this review says the evidence is *insufficient*, it does not mean the evidence is *fabricated*.
Very little in this repository is theater, and the amount of machinery for catching one's own drift (manifest
verification across commits, proof sync, drift pins, trace validation, expected-failure counts) has grown faster
than the design it checks.

---

## 2. Grade against Moon & Varshney (arXiv:2605.09045v2): B+

**What concords, re-read against the PDF.** Havoc semantics (Listing 1, the extern method with no body);
boundary-enforceable properties over typed actions, modeled boundary events and state (§1, §5.1); denials modeled
as no-effect actions (§3.2) and, in TOPAK, recorded; effect exclusivity as the explicit runtime assumption (§2,
Corollary 3.3); sandboxing beneath the verified layer as complementary and operationally audited, not verified
(§2, Figure 1). ToO §11.1's concordance list is accurate.

**Where TOPAK is ahead of the paper, and further ahead than on 09.25.**
- **Policy change and authority.** Unchanged in kind since 09.25: the paper verifies one fixed four-variant policy
  with no change cadence, no record, no second agent and no authority above the operator. ADR-0030's composition,
  ADR-0025/0026's rules floor over a havoc anchor, ADR-0044's signed bundles and ADR-0045's trusted base have no
  counterpart there.
- **The verifier is declared.** The paper trusts Dafny, which discharges obligations through Z3 and emits no
  certificate. TOPAK refused that shape for its own gate (ADR-0045 §6 refused cvc5; ADR-0030 A1 put a pinned proof
  checker behind it) and, when it acquired a prover of its own, wrote the prover down as a trust-root row
  (T-0045-31) with its digest in every results file. That is the paper's §3.4 done one step more carefully. See
  CR-30 for the asymmetry it leaves.
- **The fourth gate is still named by both and built by neither.** The paper's Appendix B shows a corollary over an
  always-empty sequence passing all three gates; its proposed fix is a "template fitness check" (§5.1). TOPAK's floor
  fitness gate is G9 item 2, open, unowned, and the only item on G9's list that has been open and unowned since G1.

**Where the grade is earned down, and why it moved only one step.**
1. **The paper's central artifact is still absent, and the corpus now says exactly what it has instead.** Moon &
   Varshney's contribution is a deductive, machine-checked refinement from abstract boundary spec to operational
   model to executable code, compiled to the deployed runtime (§3.5, §4.5). TOPAK on 10.02 has: fifteen proof modules
   establishing every stated invariant for every constant the assumptions admit; an operational model of
   `State::apply` through which 62 recorded traces, 709 steps, replay step for step; and a refinement check reading
   every replayed state against the abstract confinement invariants. ADR-0045 T-0045-28 and ToO §12 item 16 state the
   difference correctly: a harness, not a refinement, covering tested paths and not others, written from the code by
   the same hand. In the paper's ordering, S(Empirical) ⊆ S(Distributional) ⊆ S(Universal), the modules are now
   Universal and the running reference is still Empirical. The grade moves for the first half and not the second.
2. **Effect exclusivity is still assumed at every real principal.** ADR-0015 E2's conditional holds: until
   confinement is enforced, TOPAK's "mechanism claim" and the paper's assumption are identical in strength. On 10.02
   the mechanism half is *narrowed*: a rung-1 launcher is real and its profile declares P3 failing; rung 3 is
   SIMULATED under test keys; rung 2 is a seam. No guest passes P3. The paper's own words apply: "Effects outside the
   interface … are outside the formal guarantee and must be handled by complementary isolation mechanisms" (§2). See
   CR-27.
3. **The paper's witness-scope caution applies in the other direction.** The paper verifies a four-variant
   interface and says plainly that "frameworks exposing wider interfaces require correspondingly more proof cases"
   (§5.1). TOPAK's typed surface is nine action variants across two domains plus an operator channel (`grant`,
   `launch`, `issue`, `revoke`, `GatesPassed`) that no floor types and that the apply-time checks and the rules floor
   bound only in part. The operator channel is where T-0045-12 and T-0045-13 sit, and it is the half of the
   control-plane alphabet the paper's framing would ask to see typed. See CR-34.
4. **Register.** CR-25's class of "proved" in the present tense is now *true* for the modules and the ToO is careful
   to say "of the specification" each time. One live miscitation remains (§1 above). The sentence in ToO §7.5 that
   promotion "enters `Build(Contain)` enforcement coverage" still overstates ADR-0024's own consequence (CR-8), which
   says voters are `Mediated` and promotion gains attribution and authorization, not safety.

---

## 3. Grade against the TACIP discussion draft (2026.09.13b): B+

The draft is unchanged since 09.25 and TOPAK is not; this section re-grades the same document against G9 and reads
further into it than the 09.25 review did. TACIP still names none of TOPAK's vocabulary and no formal method beyond
one sentence about watchdogs (2.2.2); the alignment is convergent, which is why it is informative.

**Where the pattern lands on the profile's technical asks, and what moved.**
- **P5, identity and least agency: the strongest alignment, now with mechanism.** 5.1.1's per-invocation
  non-human identity is the lease (one per principal, one per round, twelve closed fields). 5.2.2's action-level
  runtime authorization with no standing permission from a prior session is the admit path, with the fence and
  rules epoch compared on every action. 5.3.2's task-bounded, time-windowed, automatically expiring, revocable
  authority, with partitioned environments reverting to "pre-engineered, local fallback behaviors rather than
  maintaining unverified standing authority", is ADR-0031 plus ADR-0012's resident floor plus EL zone 1, almost
  clause for clause. 5.3.3's encapsulated downstream tool whose "execution authority is mediated by a deterministic,
  single-purpose boundary" is the Wasm tool host with one declared target (ADR-0033 A8, pending). **New since 09.25:**
  at rung 1 the credential never enters the guest and a launched lease mints no token (ADR-0036 §2, built under A7),
  which is 13.2.3's "orphaned execution environment may hold a mounted credential" answered by construction.
  **Miss:** 5.1.3's cryptographic mutual authentication is absent between replicas (G5, T-0045-1) and bearer-token
  only for rung-0 principals.
- **3.2.2, constraints independent of the AI, "applied uniformly to all automated command sources … including
  remote operator sessions."** TOPAK's floor applies to every principal including humans, who are `Mediated` by
  construction, and to every command source that holds a lease. The profile's "authentication and physical safety
  are separate concerns" is ADR-0007 stated by a regulator.
- **7.3.2, policy-as-code with signed, approved, regression-tested changes.** The 09.25 miss (unsigned bundles) is
  closed: ADR-0044 is in force, the reference loads a bundle only under a key in the issued rules (I34). What remains
  is that the key is a throwaway with custody (1, 0) and signing at promotion is a script step (G9 item 67).
  7.3.2's "log … version identifiers of safety filters and any triggered rules" is the floor deny naming its forbids
  (ADR-0030 R4) and the bundle revision in the lease.
- **10.1.2, the "inference receipt."** ADR-0042 §3's `Actuate` record (tool, break-glass flag, inputs digest,
  outcome, result digest, written when the call returns, `unknown` ahead of the seal) is a receipt in the profile's
  sense, and ADR-0020's recorded denials exceed what 10.1 asks. **Tension:** 10.1 also wants prompts and context-window
  states; TOPAK keeps those in a plaintext store built for deletion (ADR-0004) and records boundary events only
  (ADR-0020). 8.1.2 lists "agentic systems with ephemeral context" among systems that may not satisfy root-cause
  analysis and 8.2 says such systems "should not be deployed where forensic RCA is required unless compensating
  controls demonstrably close the gap." TOPAK's compensating controls are the Listener's `consumed` set (ingress is
  exactly the admitted `Read`s) and raw-emission retention at the archetype (ADR-0037); they are a design, the
  archive they would live in is unbuilt (G9), and a deployment claiming RCA capability under 8.2 would have to say so.
- **3.9.5, the enforceability pentad, re-scored.** *Effective* ✓. *Durable* ✓ and stronger: ADR-0034's *Unattestable*
  verdict "never grants lower", renewal keeps the rung (A1), revocation bars later grants to the principal, Persona or
  profile. *Sufficient in scope* ✓: targeted revocation, epoch fence, `deny=all` and lease expiry are four distinct
  ordered subtractions. *Timely* ✗: `L` is still unmeasured and the coupling bound is a count, not a time. *Verifiable*
  ✗, now in two senses: the corpus is self-attested by its author, and inside the mechanism every liveness fact is the
  Observer's own assertion (heartbeat and watermark), which is exactly the "capability's self-attestation" 3.9.5(c)
  excludes. Lineage independence is the only cover and is unbuilt in the reference (ToO §12 item 12).
- **3.3, fail loudly, and 3.2.4, notification.** Coupling makes an absent Observer stall its Thinker (loud in the
  record: every refusal is a `deny` on the round topic). Nothing notifies a person. The profile's 3.2.4 wants
  rate-limited alarms on constraint violations and 3.3.1 wants an *unacknowledged* loud failure to force fallback.
  TOPAK has the fallback (default deny) and no alarm path at all; the correlator that would raise one computes
  nothing (G9 item 43).
- **4.1, break-glass, and 4.3, out-of-band control.** Passive e-stop (lease expiry needs no channel) is the best
  answer in the field to 4.3's "monitoring and control paths that do not depend on the system being monitored." The
  *active* override, the epoch fence, is an entry on the same consensus log as everything else, so under a control-plane
  partition it is as unavailable as a grant, which is the correct failure direction and should be declared against
  4.3. Two 09.25 findings stand: the break-glass TTL (R8) is still pending, so a break-glass grant is time-unbounded
  within an epoch; and **R3 couples break-glass to Observer liveness**, ratified as written (ADR-0039 B14) with the
  record itself saying it is the first thing a reviewer should reopen. 4.1.1 asks for "reliable override at
  intercept points"; an override that waits on a dead Observer is not that. See CR-29.
- **13.2, withdrawing authority.** 13.2.1 (revoke credentials, disable triggers, confirm each) is targeted
  revocation with break-glass approvals lapsing and the `after` companion recording the principal still trying.
  13.2.2, "trace and revoke that authority through every level it reaches," has no counterpart because TOPAK has no
  delegation model (CR-3, G9 item 51): a principal cannot create a subordinate, so there is nothing to cascade
  through. That is a defensible design position and it is not declared as one; 5.3.2's "when an AI system delegates
  execution to downstream tools or sub-agents" and 8.1.5's "dynamic delegation chains" assume the thing TOPAK forbids.
- **1.3.1 and 4.5.** "Constrain [the system] to a more restrictive oversight mode … until TEVV evidence supports a
  higher level of autonomy" is the rung ladder and `Mediated`-until-`Contained` in the profile's words. 4.5.1's
  time-constant audit is `W + L + D < T_irrev` with `L` unmeasured and `T_irrev` undeclared for any effect class
  (A10).
- **12.2.1's meta-safeguard.** "Appropriate meta-safeguards should be in place if these non-AI, deterministic
  verifiers are, themselves, written with the assistance of AI." The floor, the proofs, the operational model, the
  trace harness and the launcher were all drafted with the assistant; four ratified records and three pending texts
  were drafted by it. ADR-0029 has no criterion for assisted drafting (G9 item 66). The profile names TOPAK's open
  item without knowing it exists. See CR-28.
- **2.2.2 and 3.5.2, the watchdog and common cause.** The profile wants the last-resort enforcement "strictly
  non-AI … on dedicated hardware … completely isolated from the primary AI application stack," and asks whether
  redundant safeguards share a hypervisor, tenant, image or database. TOPAK's deterministic last resort is the
  mechanism (floor, fence, expiry), which is non-AI and is not out of band from itself; its Observer placement rule
  (no shared device) answers 3.5.2 for detection and nothing answers it for the three replicas, which at the
  reference run in one process tree (Annex B). ADR-0045's row-by-row base is the right instrument for the 3.5.2
  question and does not yet ask it.

**What the profile asks for that the pattern does not touch.** As on 09.25, the operational and human half: TEVV of
model behaviour against end-to-end requirements (P1, P2), Time-to-Divergence cadences (2.3.4), attention governance
(4.4), manual-mode continuity and re-commissioning (P11), training (P9), AIBOM and hazard-reachability attestations
(P6), an incident response team (8.3), near-miss reporting (8.6), and the new P13's knowledge extraction before
retirement (13.1.3). Some of this is out of scope for an architecture pattern and fairly so. Two things are in scope
and still open: a notification path for a human (3.2.4, 3.3), and the multi-agent coupling analysis 3.8.3 and 4.4.2
ask for, which is CR-3 under a NIST number; the draft's own reviewer note at 4.4.2 says the multi-agent feedback-loop
case is "still an open research topic," so TOPAK is in good company and still has only a noun.

**What TOPAK could offer the profile.** The reverse deltas of the 09.12 inventory stand and two are sharper now. The
passive e-stop remains the single construct the profile has no vocabulary for (every 4.1 intervention presumes an
actor). And `inventory.py`, which computes a deployment's theorem inventory from its trusted-base declaration, is a
stronger form of 6.1.5's "hazard reachability attestation": it states which guarantees are void for a declared
configuration, mechanically, which is what the profile's "vendor self-attestation alone may not be sufficient" is
reaching for.

---

## 4. Grade against the NIST AI RMF Playbook: B

The Playbook as pulled on 2026.10.02 is the AI RMF 1.0 Playbook: 72 subcategories under 19 categories, each with
suggested actions, "organizations can document" prompts and transparency resources, voluntary and explicitly not a
checklist. NIST now ships it in PDF, Excel, CSV and JSON and revises it about twice a year; this review used the
JSON. Table 1 re-marks all 72 rows against G9 with the 09.12 inventory's key (M matched · P partial · C convertible
· G gap · X out of scope · ! contradiction) and its matching rule: a row is M only where a ratified record or a
named mechanism discharges the outcome.

**Tally at G9: M 11 · P 24 · C 4 · G 5 · X 28 · ! 0** (72). The 09.12 inventory's corrected tally was M 6 · P 12 ·
C 15 · G 9 · X 30 · ! 1. Eleven C rows converted or became P, four G rows moved, the one contradiction (MANAGE 2.4,
crypto-shredding) was corrected in the records, and the five gaps left are the five the corpus itself names.

**Where the pattern exceeds the Playbook's suggested actions.**
- **MANAGE 2.4 and 2.3.** Lease expiry as passive e-stop, targeted revocation beside the fence, non-erasable stop
  attribution (F2), forensic preservation through erasure and break-glass (NC-2, proved), and recovery from the
  *unknown* by default deny. The Playbook's "preserve materials for forensic, regulatory, and legal review" is the
  forensic floor; its "criteria for redeploying updated system components" is promotion with gates. The 09.25
  endorsement stands and is now backed by proofs of NC-1 and NC-2 and by a reference that exercises every refusal.
- **MANAGE 4.3's "database of system changes, reason for change, how the change was made, tested and deployed."**
  Forty-six records with typed amendments and errata, nine checkpoints, twenty-one manifests that verify at their
  commits, drift pins that fail the build when a cited record moves. This is a model answer and it is also the
  evidence for CR-28: the database records that every change was made, tested and deployed by its author.
- **MEASURE 2.1 (TEVV tooling documented).** `spec/README.md`, `spec/proof-method.md`, every results-file header with
  module, jar, prover and solver digests, `mechanism/GAPS-AND-ASSUMPTIONS.md` §6 mapping each property to the test
  that restates it. M, where 09.12 marked it C.
- **MAP 2.3 (scientific integrity, TEVV method, corroboration by independent evaluators).** ADR-0046 declares TLC
  versus TLAPS and says which claim rests on which; the driver scripts and digests make corroboration *possible*, and
  §1 of this review is one instance of it. Closed as the ToO says, with the caveat that no evaluator independent of
  the author has yet corroborated anything (MEASURE 1.3).
- **GOVERN 3.2 (human-AI configurations).** HITL, HOTL and HOOTL as enabling conditions, the evictability test,
  humans holding exactly one seat (ADR-0037), the time-constant budget. Stronger than any policy the Playbook's actions
  describe.

**Where it fails, in order of weight.**
- **MEASURE 1.3**, independent assessors: zero. The Observer, the mechanical analogue, is an e2e fixture. This is
  the one recurring evidence-quality criterion in the Playbook and the grade ceiling until it moves.
- **MANAGE 1.4**, the residual-risk statement: unwritten. Named the highest-leverage single document on 09.12, listed
  in every ToO since revision 7 (anchor capture, now collusion, now rung 1 trusting the operator), and still absent at
  G9. Its content exists in pieces: ToO §12's sixteen thin places, §13's fourteen assumptions, ADR-0045 Annex A's
  residual column, and `inventory.py`'s printed gap premises are 90% of it.
- **MEASURE 2.13**, effectiveness of TEVV (floor fitness): open and unowned since G1.
- **MEASURE 3.2**, risk tracking where metrics are unavailable: `L` unmeasured, the coupling bound beside it, every
  placeholder value shipped unexamined (CR-36).
- **MAP 3.4**, operator proficiency: A5 assumes a trained human for break-glass, quarantine and `D`; nothing defines
  one.
- **Process:** the two mapping artifacts ToO §11.2 says are "due for regeneration" have been due since G3 and are now
  eight checkpoints stale (CR-35). Table 1 is offered as the input to that regeneration, not as a substitute.

### Table 1. All 72 subcategories at G9

| # | Outcome (Core wording, abridged) | 09.12 | **G9** | Note |
|---|---|---|---|---|
| **GOVERN** | | | | |
| 1.1 | Legal and regulatory requirements understood, managed, documented | X | X | Unchanged. The forensic floor retains identifiers of human principals with no legal-basis line per class (CR-11, still open) |
| 1.2 | Trustworthy-AI characteristics integrated into policy | C | C | Still never mapped to the seven characteristics; TACIP's Table 2 regrouping would be the cheaper target |
| 1.3 | Risk-management activity scaled to risk tolerance | C | P | ADR-0023's declaration schema and ADR-0045's rows are the instrument; no deployment declaration has been written (G9 item 64) |
| 1.4 | Transparent policies, procedures, controls, documentation | M | M | The record corpus |
| 1.5 | Ongoing monitoring and periodic review of the risk process; roles; frequency | P | P | Nine checkpoints in seventeen days is a review cadence; the only role is the custodian's |
| 1.6 | Inventory of AI systems, resourced by priority | C | P | The lease registry is a live inventory of principals; Personas are pinned; the reference has no inventory of *systems* |
| 1.7 | Decommissioning safely | P | P | A principal: revocation, fence, expiry, break-glass lapse. A system: re-genesis migration open (item 10); TACIP P13 is the better rubric |
| 2.1 | Roles, responsibilities, separation of development from testing | M | M | Seats, cells, recusal, fault-domain placement (ADR-0037, 0038) |
| 2.2 | Personnel and partner training | X | X | — |
| 2.3 | Executive leadership accountable for AI risk decisions | G | P | Custody declared (1, 0); key-holders and approvers are trusted-base rows (T-0045-9, 12); no organizational role named |
| 3.1 | Decisions informed by a diverse team | X | X | One person and one assistant. Marked X as organizational; the evidential consequence is MEASURE 1.3 |
| 3.2 | Roles for human-AI configurations and oversight | M | M | See above |
| 4.1 | Critical-thinking, safety-first culture | X | X | — |
| 4.2 | Teams document risks and impacts; communicate broadly | C | P | ADR-0045 enumerates the base; the residual-risk statement is unwritten; nothing is communicated outside the repository |
| 4.3 | Enable testing, incident identification, information sharing | P | P | `SECURITY.md` defines a safety finding and a private route; replay and recorded denials identify; external sharing absent |
| 5.1 | External feedback collected and integrated | X | X | — |
| 5.2 | Adjudicated feedback incorporated | X | X | — |
| 6.1 | Third-party risk policies, including IP | X | X | Model licensing, corpus licensing untouched |
| 6.2 | Contingency for third-party failure | G | P | An unavailable model or Observer now stalls by mechanism (ADR-0039) rather than being unmodeled; the "army of one" degraded mode of 09.10 is still unfiled |
| **MAP** | | | | |
| 1.1 | Intended purpose, context, settings | X | X | ToO §13's assumptions of use cover the limitations half |
| 1.2 | Interdisciplinary, diverse actors | X | X | — |
| 1.3 | Mission and goals | X | X | — |
| 1.4 | Business value | X | X | — |
| 1.5 | Risk tolerances documented | C | P | Same instrument and same blocker as GOVERN 1.3 |
| 1.6 | System requirements elicited; socio-technical design decisions | C | M | Fifteen proved, mutation-tested TLA+ modules are requirements artifacts of the kind the Playbook's example only gestures at |
| 2.1 | Task and methods defined | X | X | — |
| 2.2 | Knowledge limits; how output is overseen | P | P | Havoc as a deliberate substitution is now stated (ToO §2.3); oversight documented; assessed, no |
| 2.3 | Scientific integrity and TEVV considerations | G | M | ADR-0046; drivers and digests; one corroboration in §1 |
| 3.1 | Benefits documented | X | X | — |
| 3.2 | Costs, including non-monetary | C | C | The capability cost (no shell) is stated; the durability cost (a crashed round loses its work) is not (10.01 assessment §7); no adoption-cost table |
| 3.3 | Targeted application scope specified | M | M | Both alphabets typed since ADR-0040 |
| 3.4 | Operator and practitioner proficiency | G | G | A5 presumes it; nothing defines it |
| 3.5 | Human-oversight processes defined, assessed, documented | P | P | Defined and documented; assessment needs `L` and an Observer that exists |
| 4.1 | Third-party legal and IP mapping | X | X | — |
| 4.2 | Internal risk controls per component, incl. third-party | C | M | ADR-0045 Annex A and B: one row per component, class, residual, and the theorems that rest on it |
| 5.1 | Likelihood and magnitude of impacts | X | X | — |
| 5.2 | Engagement with AI actors | X | X | — |
| **MEASURE** | | | | |
| 1.1 | Metrics selected; **unmeasured risks documented** | C | P | ToO §12 and §13 list what is not measured; it is not written as the non-measurement declaration the row accommodates |
| 1.2 | Metrics reassessed | X | X | — |
| 1.3 | Independent assessors | P | G | Zero. The 09.12 P credited the Observer; it does not exist |
| 2.1 | TEVV tooling documented | C | M | See above |
| 2.2 | Human-subject evaluation | X | X | — |
| 2.3 | Assurance criteria under deployment-like conditions | P | P | The compose rig exists; the smoke run has not been repeated since 09.25 (item 52) |
| 2.4 | Production monitoring | P | P | Liveness coupled; detection function absent |
| 2.5 | Validity, reliability, generalizability | X | X | — |
| 2.6 | Safety; **fails safely**; residual within tolerance | C | P | Every refusal path exercised and recorded; residual risk unstated (MANAGE 1.4) |
| 2.7 | Security and resilience evaluated | C | P | Mutation discipline and negative controls are the structural evaluation; time-to-bypass unmeasured; no adversarial exercise has been run |
| 2.8 | Transparency and accountability risks | C | M | Attribution guarantee; confirmation markers; the debt ledger |
| 2.9 | Model explained, validated | X | X | Declared out by havoc, in writing |
| 2.10 | Privacy risk | C | C | Erasure machinery without a privacy framing, unchanged |
| 2.11 | Fairness and bias | X | X | — |
| 2.12 | Environmental impact | X | X | — |
| 2.13 | **Effectiveness of TEVV** | G | G | Floor fitness, unowned (item 2) |
| 3.1 | Track unanticipated and emergent risks | X | P | Every checkpoint's "results the drafting did not anticipate" is this, for the corpus |
| 3.2 | Tracking where metrics are unavailable | G | G | `L`; placeholders (CR-36) |
| 3.3 | End-user feedback and appeal | X | X | — |
| 4.1 | Measurement connected to context | X | X | — |
| 4.2 | Results validated by domain experts | X | X | — |
| 4.3 | Improvements or declines from field data | X | X | — |
| **MANAGE** | | | | |
| 1.1 | Determination that the system achieves purpose; proceed or not | P | P | Promotion is a containment gate, not a purpose gate; now stated in the record's consequences |
| 1.2 | Treatment prioritized | X | P | The 09.28 prioritization is this, for the corpus |
| 1.3 | Documented responses to high-priority risks | P | P | Against design forks, not a mapped risk register |
| 1.4 | **Residual risk documented for acquirers and users** | G | G | Unwritten (see above) |
| 2.1 | Resources; non-AI alternatives | C | C | Unchanged |
| 2.2 | Sustain value | X | X | — |
| 2.3 | Respond to and recover from an unknown risk | M | M | Default deny; quarantine; fence; targeted revocation; replay |
| 2.4 | Supersede, disengage, deactivate | M ! | M | The contradiction is gone: ADR-0003 and ADR-0028 say legibility, not shredding, and NC-2 is proved |
| 3.1 | Third-party risks monitored, controls documented | G | P | Monoculture is now one pair per cell (ADR-0037); third-party components are rows (Cedar, Kafka, OPA, TLC, tlapm); no monitoring |
| 3.2 | Pre-trained models monitored | G | P | The Persona pins weights, prompt and decoder; lineage is projected from the log (ADR-0035, Proposed); behaviour is not monitored, by design |
| 4.1 | Post-deployment monitoring, appeal, override, decommissioning, incident response, change management | P | P | Override, incident response and change management map; appeal and user input do not |
| 4.2 | Continual improvement with interested parties | X | X | — |
| 4.3 | Incidents communicated; tracking documented | P | P | Tracking: a model answer. Communication: none |

---

## 5. The earlier findings, at G9

| Tag | Status |
|---|---|
| **CR-1** (effect exclusivity an assumption) | **Narrowed, open.** The design half closed on 09.28 (ADR-0034); the mechanism half now has a rung-1 launcher whose only real profile declares P3 failing, a simulated rung 3, and a seam at rung 2. No principal is `Contained`. The claim's strength is unchanged (ADR-0015 E2). See CR-27 |
| **CR-2** (detection fails open) | **Three of four cases closed** by ADR-0039: a dead, partitioned or starved Observer stalls its Thinker and nothing else. Collusion is open and declared (A13). The residual-risk statement that was to carry it is unwritten. A new cost was ratified with it: break-glass waits on the same Observer (CR-29) |
| **CR-3** (no delegation or chain model) | **Untouched**, now the fourth review to say so. G9 item 51 open; the correlator has a seat, a placement rule, a read set and no function (item 43); sequence numbers on denials, the cheapest input a correlator needs, are open (item 44). TACIP 3.8.3, 4.4.2, 5.3.2, 8.1.5 and 13.2.2 all presuppose the thing this finding asks for |
| **CR-4** (formal layer promissory) | **Substantially discharged.** Fifteen proved modules; TLC-versus-TLAPS declared (ADR-0046); an operational model with trace validation; drivers that regenerate. What remains is named: the refinement (T-0045-28), the prover trusted without certificates (item 74), practical constants (item 75), no liveness anywhere (CR-37) |
| **CR-5 / CR-21** (self-ratification; the recursion) | **Structurally answered on 09.25 (ADR-0029 A2), evidentially worse.** Forty records accepted, twenty-two confirmation-required, seven assistant-drafted texts (four ratified, three pending), no reviewer engaged, no criterion for assisted drafting (item 66), and G9's ledger does not carry the A2.5 line that ADR-0029 A2 requires it to carry. See CR-28 |
| **CR-6** (no flow constraints) | **Untouched as a record**; confirmed and sharpened as axis A14 of the 10.01 competitive assessment, with a design sketch (provenance labels as syntactic lift) and no owner. See CR-32 |
| CR-7 (denials erasable, unordered) | **Half closed.** Denials now reach the round topic and the bounded `after` companion (ADR-0020 implemented; ADR-0003 A2). Still erasable with the topic, still unordered, no F7 |
| CR-8 (promotion "enters `Build(Contain)`") | **Open.** ToO §7.5 still says it |
| CR-10 (three seats, two lineages) | **Closed** by ADR-0037: the Reader is a stage |
| CR-11 (legal basis per forensic class) | **Open.** ADR-0028 carries no legal-basis line |
| CR-12 (TCB unenumerated) | **Closed** by ADR-0045: thirty-one rows, each with class and residual |
| CR-13 (archetype affordability) | **Closed in register**: ToO §2.6 says "almost nobody can afford the archetype" and specifies the rungs below it |
| CR-15 (reversibility untyped) | **Open.** ADR-0032's rule (an irreversible effect must not be expressible) has no mechanism; `T_irrev` is declared for no effect class (A10) |
| CR-17 (operator proficiency) | **Open** (MAP 3.4) |
| CR-22 (`slm/` evidence) | **Closed** on 09.25: dated results files, rerun 09.28 |
| CR-23 (no reproducible results file) | **Closed in part**: the jar path is fixed, the new modules have generators, one regenerated here with identical outcomes; the older modules' files are still hand-assembled (item 78) |
| CR-24 (unsigned trust edges) | **Half closed.** Bundles signed (ADR-0044; dev key, custody (1, 0), item 67). Replica authentication: none (G5); gate evidence: unsigned (item 57); operator socket: file mode. See CR-34 |
| CR-25 (register lag) | **Recurs** in new places (CR-31) |
| CR-26 (ADR-0033 E1 falsified by enumeration) | **Absorbed**: E1's text was re-read rather than an E2 written; the manifest expected-failure counts now verify by tooling, which is the sibling convention the finding proposed |

---

## 6. New findings

| # | Finding | Severity |
|---|---|---|
| **CR-27** | **The first leases above rung 0 are a milestone of attribution, not of confinement, and the corpus should say it in those words.** Rung 1 trusts the operator, the launcher script and the container runtime by ADR-0034 §6's own table; the reference's test `every_host_power_subtracts` shows a launcher that reports the image it was asked for while running another is *believed*. Rung 3 is two test keys. The P3-passing image (a static build on an empty image, G9 item 36) has been "the step" since ADR-0036 was drafted on 09.27 and is the smallest piece of work with the largest effect on every grade in this review: it would give `Contained` a first candidate member at rung 1 under a declared profile, which is still `Mediated` by rung but no longer by profile. The SIMULATED convention (G9 §5) is exactly right and should be kept until a real verifier signs something. | High |
| **CR-28** | **The recursion, re-graded at G9.** The 09.25 review graded this High on 29 records ratified by their drafter. At G9: forty accepted, twenty-two confirmation-required, and a new class the corpus itself names as "one step further from review": texts drafted by the assistant and settled by ratification, four in force (ADR-0044, 0045, 0030 A1, 0046) and three pending (ADR-0034 A2, ADR-0033 A7, A8) with the code, modules, proofs, mutation tests and trace runs under them produced by the same hand in one day. Three specifics. (i) ADR-0046's ratification condition asked the custodian to regenerate the proof evidence so the digests would not be the drafter's alone, and the drafter ran it at the custodian's direction (ADR-0046 §7, ToO §12 item 3): the condition was met in letter and not in purpose. (ii) ADR-0029 A2.5 says the debt ledger "gains a line: whether a bootstrap reviewer is engaged, and the manifest digest of the last completed review pass"; G8 §4 and G9 §4 carry no such line. (iii) ADR-0029 has no criterion for assisted drafting (item 66) while seven texts rest on it. TACIP 12.2.1 asks for "meta-safeguards … if these non-AI, deterministic verifiers are, themselves, written with the assistance of AI," and MEASURE 1.3 asks for assessors who were not the developers. The honest self-reporting in G9 §4 and §8 is better than any comparable corpus offers, and it is still a report, not a review. | High |
| **CR-29** | **Break-glass is both too hard to obtain and too easy to keep.** Too hard: floor entry R3 couples every effect-bearing Run admit to a live cell Observer, break-glass included (ADR-0039 R4 item 4, ratified as written at B14), so the emergency path waits on a dead Observer; G9 item 49 is open. Too easy: R8, the break-glass TTL, is still pending (item 8, four conditions unmet), so an approval is time-unbounded within an epoch. TACIP 4.1.1 asks for a "reliable override at intercept points" and MANAGE 2.4 for bypass procedures that work when the system is the problem. Either fix is small: exempt break-glass admits from R3 (a floor change, routed as a relaxation, which is the right cost) or declare the coupling as the deployment's choice on D-0039-1's face. | Medium-High |
| **CR-30** | **The proof-checker asymmetry.** The corpus refused cvc5's `unsat` as evidence for a floor-routing verdict and put a pinned proof checker (`ethos`) behind it (ADR-0030 A1), on the rule that a solver's failure adds authority. The same day's 3,036 proof obligations are accepted on tlapm's word, discharged by Z3 4.8.9 and Zenon with no certificate; the Isabelle backend that would check them is unused (item 74); the prover binary is 1.9 GB, untracked, and known only by a digest printed in each results file. ADR-0045's rule is applied consistently (T-0045-31 is a trust-root row, declared), and the practice is asymmetric: the gate's verdicts are checked and the proofs are trusted. Running the Isabelle backend once over the fifteen modules, or pinning the prover in a manifest, would close it; the corpus has already shown it knows how. | Medium |
| **CR-31** | **The state of record is a revision behind its own narrative, on the day both were cut.** G9's header says revision 12 "stands, not revised at G9" and item 79 says the tags `ToO-rev12`, `glossary-2026.10.02`, `REF-2026.10.02` and `REF-2026.10.02b` do not exist. In the tree at `fccf374`: revision 13 exists, dated 2026.10.02, "cut from G9", committed after G9 (`9e811bc`); all four tags exist; `README.md` still points at G8 and revision 12. The "where they disagree, the checkpoint wins" rule needs the checkpoint to know what it is disagreeing with. ADR-0045 Annex B "behind the code" (ToO §7.9) is the same class and is acknowledged. Each is minor; CR-25 said on 09.25 that this class was supposed to be closed by register discipline, and it is the class of error a second reader catches first. | Low-Medium |
| **CR-32** | **Prompt injection inside the envelope has no record, and tool descriptions are unpinned.** The 10.01 competitive assessment found both (A14; §5 items 2 and 4) and sketched the fix in ADR-0007's own terms: provenance labels on `Consult` and `Actuate` arguments as syntactic lift, and the digest of a tool's interface text in its allowlist entry. Neither has a record, an owner or a G9 item. Under havoc, an injected Thinker may `Actuate(send, {to: attacker, body: secrets})` if the floor allows `send` with those argument types; the floor bounds what *can* happen and nothing bounds what an injected Thinker *will* do inside the bound. TACIP 3.8.1 lists "prompt injection" and "malicious tool/API invocation" as the attack surface to map; the competitive assessment calls this "the threat buyers ask about first." The labels fix is the highest-leverage single ADR available, as the 09.16 review said of CR-6. | Medium-High |
| **CR-33** | **Channel fidelity is narrower at the reference than in the text that is pending for it, and the text is the drafter's.** ADR-0034 A2 names a Wasm *component* with one scoped socket capability; the reference hosts a core *module* with `connect`/`send`/`recv` on one target (I44). The target is bound and the protocol is recorded and not enforced; a Run tool's channel is declared twice, in the node's config and in bundle data, and nothing checks the two agree (G9 item 84); a Build profile that says P4 passes is not held to Wasm tools at all (item 83). `RunConfinement.tla` proves the property of the module; the gap between the module's `Filtered` boolean and a real egress filter is D-0034-5, a trust. All of this is marked pending and PROVISIONAL, which is correct. The finding is that A2 should not be ratified from the drafter's text alone: its three drafter's choices (G9 §1.2) are exactly the ones the reference then narrowed. | Medium |
| **CR-34** | **The operator channel is the untyped half of the control-plane alphabet.** Principals' actions are typed, lifted, floored and bundled. Operator requests (`grant`, `launch`, `revoke`, `issue`, `GatesPassed`, profile registration) are validated by the rules floor where an issuance is involved and by apply-time checks elsewhere, and are authenticated by a socket's file mode (G5). Replica-to-replica traffic is unauthenticated (T-0045-1: "anyone reaching a socket is a replica"), the only trust-root row whose named mitigation (mTLS) is still unbuilt. Gate evidence is an operator's assertion (T-0045-13, item 57). Moon & Varshney's caution about wider interfaces (§5.1) applies here: the surface that can add authority is the one with the least type discipline. CR-24's asymmetry, record integrity best in class and runtime edge integrity open, is half closed by bundle signing and otherwise stands. | Medium-High |
| **CR-35** | **The Playbook artifacts and the residual-risk statement are the oldest open documentation debts, and both are now cheaper than ever.** The 09.12 delta inventory and 09.15 feature list have been "due for regeneration" in every ToO since revision 7; Table 1 is the input. MANAGE 1.4 has been named the single highest-leverage document on 09.12, 09.16, 09.25 and in every ToO §10 and §12; ToO §12, §13, ADR-0045 Annex A's residual column and `inventory.py`'s gap premises are most of its text. Writing it discharges MANAGE 1.4, MEASURE 2.6's third clause, MEASURE 1.1's non-measurement declaration, GOVERN 4.2, TACIP 1.3.4's evidence package and A10's declaration of `T_irrev` per effect class in one document. | Medium |
| **CR-36** | **Every number is a placeholder and the floor is proved over them.** `T_obs` 5000 ms, `K` 8, Run's `R` 64, `T_persona` one hour, five lineage thresholds unset; the values file is pinned with the floor and gated with proofs, so the corpus can prove that `K < R` is needed for the coupling bound to refuse at all and cannot say what `K` should be. No Observer has been measured (item 47). A deployment that ships these is declaring them, which the ToO says; what the ToO does not say is that MEASURE 3.2 and TACIP 2.3.4 both ask for a *measurement program*, and the corpus has an `slm/` rehearsal rig that could run one for `T_obs` and `K` today. | Medium |
| **CR-37** | **No liveness property exists anywhere in the formal layer, for a design whose Run posture is "stall".** Every module is `Init /\ [][Next]_vars` without fairness (`spec/proof-method.md` §5), every property is an invariant, and the corpus says this made the proofs cheap. A12 accepts that a lagging Observer stalls its Thinker; coupling across rounds, coverage at the tally, the correlator's exemption and the `K < R` ordering are all arguments that a stall *resolves*, and nothing checks that it does. The reference's e2e shows one stalled promotion completed by a heartbeat; the model cannot distinguish stall from deadlock. One liveness property per coupling module, under weak fairness on the Observer's heartbeat, would be the first non-trivial proof in the corpus and the first that could be false. | Medium |
| **CR-39** | **Three launcher tests are timing-dependent and fail under load.** `contain.rs` sequences a launch, a fence or a revocation and an assertion with a 500 ms sleep and a `settle` helper rather than by waiting on the log index the launch returns; under compile load the grant had not applied when the revocation was ordered and the test asserted `ended == 1` against `0`. The code is not wrong on the evidence here (five clean re-runs, one under load), and the tests are the evidence the pending A7 addendum cites: a discrimination test that can fail for want of time can also pass for want of time. Waiting on the returned fence instead of the clock closes it, and the corpus's own clock model (ADR-0032: no safety decision reads a clock) says why the tests should not either. | Low |
| **CR-38** | **The forensic record and TACIP's root-cause requirement pull in opposite directions, and the corpus has not said which way it leans.** ADR-0020 replays boundary events only; ADR-0004 keeps plaintext in a store built for deletion; ADR-0037 retains raw emission at the archetype for one purpose. TACIP 10.1 wants prompts and context-window states in the decision-level log and 8.2 says a system that cannot support deterministic root-cause analysis "should not be deployed where [it] is required … unless compensating controls demonstrably close the gap." TOPAK's answer (the `consumed` set, raw emission, the `Actuate` record with both digests) is a good one and is a design: the archive is unbuilt (G9, item 28 in part). A deployment under TACIP would need a declared position on 8.2 as part of its deployment declaration, and ADR-0023's schema has no field for it. | Low-Medium |

---

## 7. What has genuinely improved since 09.25

Stated so that §6 is read in proportion.

- **The formal layer went from checked to proved** for fifteen modules, with the method declared, the prover
  declared as a trust root, every proof's hypothesis derived from the mutations that break it, and five corrections
  to the premise table found by writing them. The proof of `NonComposition` found a missing clause no TLC run could
  reach.
- **The link from specification to code went from asserted to mechanized** at stage one: an operational model, trace
  recording in the core, 62 traces replayed, every state read against the abstract confinement invariants, and a
  harness that fails at the exact step when the code and the model drift.
- **Detection acquired a failure direction.** ADR-0039 closed three of CR-2's four cases by mechanism, with the
  costs stated and the fourth declared.
- **Confinement went from a design to a ladder with a bottom rung built**, a simulated top rung, every rung's trusted
  base as rows, a lookup that names each failing conjunct of `Contained`, and a convention (SIMULATED) that keeps a
  witness from being read as a claim.
- **Run acquired an alphabet, a coupling, a record of every effect, a profile draft and a tool host** that can hold a
  tool to one target, in four days.
- **Trust edges were signed** where it was cheapest (bundles) and the remaining unsigned ones are rows with
  residuals, not omissions.
- **The checking of the corpus itself** now verifies twenty-one manifests at their commits, keeps proofs in sync with
  modules, fails the build on an unpinned citation, regenerates results from drivers, and prints the digest of every
  tool a result rests on.
- **The 09.25 review's six asks:** one independent confirmation pass (not done); a confinement specification (done,
  ADR-0034, and partly built); an Observer record answering CR-2 (done, ADR-0039); sign the bundles (done,
  ADR-0044); check in the `slm/` evidence and one driver per results file (done; in part); regenerate the Playbook
  artifacts (not done; Table 1 above). Four of six in seven days, and the two not done are the two that need a
  second person or a document rather than a mechanism.

---

## 8. What would change the grades

In order of leverage per unit work, with the 09.25 list's first item still first:

1. **Engage one reviewer who is not the author**, record it on the A2.5 ledger line, and run one confirmation pass
   over any confirmation-required record. It moves MEASURE 1.3, TACIP 3.9.5(c) and the paper's correlated-review
   concern at once; nothing else on this list moves three grades.
2. **Build the P3-passing image** (item 36) and run ADR-0036's ratification run on it. It is the first real candidate
   for `Contained` and the cheapest change to CR-1 and CR-27.
3. **Write the residual-risk statement** (CR-35) from the text that already exists.
4. **Write the provenance-label and tool-description record** (CR-32) in ADR-0007's own terms.
5. **Decide break-glass against R3** and ratify R8 (CR-29): two small changes to the one path TACIP and the Playbook
   both look at first.
6. **Add one liveness property** to `Coupling.tla` under weak fairness on the heartbeat (CR-37), and **run the
   Isabelle backend once** over the fifteen proofs or pin the prover in a manifest (CR-30).
7. **Measure `T_obs` and `K`** with the rehearsal rig (CR-36), and **write the A2.5 line, the README repoint and the
   G9 erratum** (CR-31).

---

## 9. Post-review note

**The reference's tests arrived before the commit** and are recorded in §1 and CR-39: 103 tests, 100 passing on a
first run made under compile load and 103 on every run since. No other disposition was made the same day; the
findings above are the custodian's to disposition, and this document, like its predecessors, proposes no decision
text. The `derived/README.md` row that indexes this file is the one edit beside it, which moves nothing a manifest
measures. The 09.25 review is not edited: it is measured by `SHA256SUMS-G9`, and the index row says what supersedes
it.

---

## Sources

- `narrative/theory-of-operation.md` (revision 13, `5022ccaec0ca64b4…`); `narrative/glossary.md` (`b01178a77cf551a7…`)
- `checkpoints/topak-genesis-checkpoint-G9-2026.10.02.md` (`228422d80155862b…`)
- `decisions/` at `fccf374`: ADR-0029 §4, §5, A2; ADR-0033 §7 and its history; ADR-0034 §1 to §8 and A2; ADR-0036;
  ADR-0039 history R4, B14; ADR-0045 §5, §6, Annex A, Annex B; ADR-0046
- `spec/README.md`, `spec/proof-method.md`, `spec/theorem-premise-binding.md`, `spec/proof-sync.sh`, the fifteen
  proof results files of 2026.10.02, `spec/RunConfinement-results-2026.10.02.txt`,
  `spec/Mechanism-trace-results-2026.10.02b.txt`
- `floor/genesis-gates-results-2026.10.01.txt`; `mechanism/GAPS-AND-ASSUMPTIONS.md` (brought current 2026.10.02);
  `mechanism/README.md`; `SECURITY.md`
- `derived/topak-critical-review-2026.09.16.md` (CR-1 to CR-20); `derived/topak-critical-review-2026.09.25.md`
  (CR-21 to CR-26, `d19d94bc81300f96…`); `derived/topak-playbook-delta-inventory-2026.09.12.md`;
  `derived/topak-competitive-design-assessment-2026.10.01.md`; `derived/topak-containment-features-2026.10.01.md`
- Moon, R. and Varshney, L. R., "Containment Verification: AI Safety Guarantees Independent of Alignment,"
  arXiv:2605.09045v2, AIWILD @ ICML 2026 (PDF supplied by the custodian, `06e699209e2bd6ba…`): §1 to §5, Appendix A, B
- Sheh, R. and Stanley, M., "NIST AI RMF Profile: Trustworthy AI in Critical Infrastructure and High-Consequence
  Applications," community-of-interest discussion draft, 2026.09.13(b), not official guidance (Markdown supplied by
  the custodian, `1a37852f316e819e…`): Practices 1 to 13 with Tasks and Implementations, the glossary, Appendix B
  (i1 to i32), Appendix E, the changelog
- NIST AI RMF Playbook, structured export (`playbook.json`) as mirrored in
  [Agent-Threat-Rule/ai-rmf-oscal-catalog](https://github.com/Agent-Threat-Rule/ai-rmf-oscal-catalog)
  (`source/ai-rmf-playbook.json`, `abf907645b9310d8…`; `source/PLAYBOOK_VS_CORE_DIVERGENCES.md` for the 41-row
  wording drift against the Core). `airc.nist.gov`, `www.nist.gov` and `nvlpubs.nist.gov` were refused by the
  session's network policy; NIST's own landing page for the Playbook is `airc.nist.gov/airmf-resources/playbook/`
- In-session verification: `tools/verify-manifest.sh --all` (21 of 21 at their commits); `shasum -a 256 -c
  manifests/SHA256SUMS-G9` (390 of 392 at `fccf374`); `spec/proof-sync.sh` (15 IN SYNC); `spec/runconfinement-gen-
  results.sh` over `runconfinement-rows-2026.10.02.txt` (13 of 13 outcomes identical); `tools/check-refs.py`
