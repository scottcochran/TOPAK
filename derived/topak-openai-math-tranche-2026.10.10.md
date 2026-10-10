# The OpenAI mathematics tranche of 2026.10.06, and what it bears on in TOPAK

**2026.10.10** · a reading, not a record · prepared at the custodian's request · read against G11 (`ce8f460`),
ADR-0046, ADR-0053, ADR-0045 Annex A, `spec/proof-certification.md` and `spec/proof-method.md`

**Sources.** The OpenAI post itself (`openai.com/index/sharing-ai-progress-in-mathematics/`) could not be fetched
from this session: the environment's proxy refuses the host. What follows is reconstructed from the companion
repository `openai/math` (its top README, `lean/README.md`, `lean/ComparatorChallenges/README.md`, the head of
`lean/formalization.yaml`), the earlier `openai/ten-proofs` README, the `leanprover/comparator` README, and press
coverage (Scientific American, TechCrunch, Fortune, OfficeChai, Developers Digest and two aggregators). Figures
are marked by where they come from. Nothing here was verified by building any of OpenAI's Lean.

---

## Part I — What was released

**The tranche.** On 2026.10.06 OpenAI published, under Apache-2.0 at `github.com/openai/math`, manuscripts produced
by an unreleased internal model on open research problems, with Lean formalizations for a part of them. The post
says it will add formalizations over time, and the repository keeps a public version history in which corrections
are published as new versions and earlier versions stay accessible.

| Figure | Value | Source |
|---|---|---|
| Manuscripts | 719, grouped into 372 families, each classed by discipline | `openai/math` README (press says 722) |
| Problems posed to the model | about 4,000 | README |
| Compute per result | about three hours of ChatGPT Pro thinking compute, on average | README |
| Top-line results with a Lean formalization | "~42%" | README |
| Reasoning summaries released | ten families (007, 017, 087, 102, 159, 197, 221, 271, 287, 362) | README |
| Erdős problems touched | 23, per Thomas Bloom, who calls all 23 significant | OfficeChai |
| Catalogue | `lean/formalization.yaml` v0.4; project `status.scope: "Partial progress."` | the file |

**What the repository says of its own verification status, verbatim.**
- "This collection includes results at different stages of verification." The stages are not defined or labelled.
- "Not all have accompanying Lean formalizations."
- "Some of the unformalized results could have issues," and OpenAI will "endeavor to fix any such issues quickly."
- Of the five Comparator setups for supporting results: "These setups verify supporting results, not the
  corresponding papers' main theorems."
- The Lean README names no Lean or Mathlib version, says nothing about axioms, `sorry` or `native_decide`, and
  gives no statement of what a passing build establishes. It points to the Comparator README for "how to verify".

**How a formalized result is checked.** Each `main_results` entry in the catalogue names a Lean declaration, its
file, and a `comparator_config` JSON. Comparator (Lean FRO, built for AIMO and Kaggle evaluation) takes a Challenge
module holding the statement with a `sorry`, and a Solution module; it requires the statement to be identical
down to every declaration it uses, restricts the Solution to an axiom allowlist (`propext`, `Quot.sound`,
`Classical.choice` by default), replays the Solution environment through the Lean kernel, builds and exports each
file inside a `landrun` sandbox, and can hand the `lean4export` output to an external kernel (nanoda, or any binary
named in `external_kernels`). Its README lists its trust assumptions: the Challenge and its import closure, that
the Solution was never compiled beforehand, `landrun`'s sandbox, the kernel (or at least one of several), and an
unprivileged user. Its stated limitation: a definition hole "can be gamed" (define the answer as the conjecture
itself and close by reflexivity), so every definition-hole result "needs an additional human or other review".

**Lineage.** The tranche follows a May unit-distance disproof, the 2026.08.01 "Ten advances" batch (`openai/ten-proofs`,
Lean 4.32.0, one file per result, Erdős 146, 180 and 183 among them), the Epoch FrontierMath Erdős benchmark (68
problems curated by Bloom, formalized, scored with Comparator) and a September Navier–Stokes claim still under review.

**Reception, as far as it bears on method.**
- The field's objection is not to the kernel. It is that (i) less than half of the top-line results are formalized,
  (ii) where they are, the formal statement is not always the prose claim: coverage reports the Lean file for
  Erdős problem 3 proving a weaker bound than the manuscript claims, and TechCrunch cites a paper on the gap between
  the natural-language and the formal solution of the Navier–Stokes claim, and (iii) the volume outruns human
  understanding: Tao's objection is that the prompter cannot answer questions on the result, and the Association
  for Human Mathematics asked mathematicians to stop working with OpenAI.
- Bloom froze proof claims on the Erdős problem pages on 2026.10.06 and will link only Lean formalizations registered
  on Palomar: a curator's response that takes a formal artifact as the unit of record and not the manuscript.
- OpenAI "takes responsibility for the correctness of the Lean proofs", while the arguments were the model's.

---

## Part II — Applicability to TOPAK

**What does not apply.** None of the mathematics does. TOPAK's theorems are safety invariants of small transition
systems (`Spec => []P` over a floor, a lease, a seat, an admit), proved by induction and checked by TLC at small
constants. No result in the tranche is a lemma TOPAK could cite, and no benchmark score says anything about whether
a model-drafted proof of `FloorPreserved` is right. The applicability is entirely in method: how a corpus that is
mostly model-written (G11 §8: "one hand's"; the reviewer's guide: nearly every text since 2026.10.02 drafted by the
assistant) states, checks and discloses what its proofs claim. On that question the tranche is a large natural
experiment, and TOPAK's records already take most of the positions the field is now demanding of OpenAI.

### 1. Where TOPAK already has what the tranche lacks

| The field's complaint about the tranche | TOPAK's standing answer |
|---|---|
| "Different stages of verification", undefined | ADR-0046 §1 fixes the words: *checked* (TLC), *proved* (TLAPS, under named hypotheses), *certified* (every obligation accounted for by a checked route); ADR-0053 adds *proved in Lean* with the premise each use adds. The reviewer's guide's glossary line says what none of them means |
| 42% formalized, the rest "could have issues" | Every theorem a record cites has a results file by digest, and `proof-sync.sh` and `lean-sync.sh` exit 1 when any is stale or unproved (`Workflow.tla`, `Mesh.tla`, item 101). There is no "unformalized" class that a record may cite |
| The formal statement is weaker than the prose claim (Erdős 3) | ADR-0053 §2's table: a re-encoding adds the premise "the Lean transition system is the TLA+ module", read and not checked, except for the three encodings the graph check runs against TLC's state graph. T-0045-37's failure column names exactly this: "a true theorem about a Lean that is not the module". Finding 12 is the local instance: an encoding too lax or too strict passes every invariant and only the graph check sees it |
| `#print axioms` taken as the audit | ADR-0053 finding 1: a theorem on `False` added with the kernel check off reports no axioms; only the `leanchecker --fresh` replay refuses it. Every Lean results file carries the replay |
| A passing build taken as a verified proof | ADR-0046 A2 and `proof-certification.md` §8: the pinned TLAPS proves `FALSE` twice and certifies; "a certified proof is not a verified one" (G11 §8) |
| Corrections silently | Frozen results files, successor modules, dated derived documents never revised; `history.md` in `openai/math` is the same instinct, adopted later |
| No reviewer | ADR-0029 A2.5: the debt ledger carries the line "bootstrap reviewer engaged: none", in every checkpoint |

The tranche therefore confirms the design rather than changing it. Its specific value is as an external witness
that the disclosures TOPAK makes (what is proved of what, under which premise, by which checker, with what left
trusted) are the ones a field actually asks for when model-written proofs arrive in volume.

### 2. Comparator, as a design to borrow

Comparator is the closest external artifact to TOPAK's proof-carrying gate and certified prover run: an untrusted
producer, a trusted checker, the statement fixed by someone other than the producer. Three of its elements map
onto open obligations in ADR-0053 and item 107.

1. **The independent kernel for the replay.** ADR-0053's first open obligation is "an independent kernel for the
   replay: lean4lean", because `leanchecker` is "the same kernel in a separate process, not an independent
   checker". Comparator already packages the route: `lean4export` to an export file, then nanoda or any
   `external_kernels` binary. Adopting it, or its two-step shape, discharges the obligation with a tool the Lean
   FRO maintains, and gives T-0045-37 the same pair the floor has in T-0045-14 (cvc5 produces, ethos checks).
2. **The Challenge/Solution split and the axiom allowlist.** TOPAK's encodings and their proofs sit in one file,
   and the axiom budget is prose in ADR-0053 §2 (`propext`, `Quot.sound`, `Classical.choice` in `NonComposition`
   alone; `native_decide` in `floor/lean` only). A Comparator config per package would make the statement module
   the frozen object the results file digests, and the allowlist a checked value: the floor package's
   `native_decide` would have to be named (`Lean.ofReduceBool`) or removed, which is itself an open obligation.
3. **The gamed definition hole.** Comparator's own limitation is TOPAK's encoding premise in miniature: when the
   solver may supply a definition, equality of statements proves nothing. TOPAK's answer, the graph check and the
   trace replay, is stronger than Comparator's ("additional human or other review"), and is run for three of
   sixteen encodings. The tranche is an argument for finishing the other thirteen (item 107) before any Lean
   result carries a claim about the code (ADR-0053 §5's precondition).

Comparator's trust-assumption list is also a worked example of ADR-0045 §1's row schema applied to a checker: the
sandbox (`landrun`), the OS and hardware, the kernel, the unprivileged user, the Challenge's import closure. If the
corpus adopts it, those become rows or sub-rows of T-0045-37, and the sandbox-escape assumption is the one TOPAK's
own confinement work (ADR-0034, ADR-0036) has vocabulary for.

### 3. A proof as a Byzantine agent's action

TOPAK treats every agent as Byzantine and admits actions at a gate whose check does not trust the actor. The tranche
is a case of exactly that shape at scale: a model emits a manuscript and a Lean term, and the only part the field
accepts without reading is the part a checker fixed in advance. Two consequences for the design.

- **The statement is the mechanism's, the proof is the agent's.** In Comparator terms the custodian writes the
  Challenge. In TOPAK terms the frozen TLA+ module and its encoding are the Challenge, and a model-drafted proof
  module or Lean file is a Solution the gate admits or refuses. The corpus already does this by hand (the assistant
  drafts; the custodian ratifies on byte-identical regeneration and a mutation check). The tranche suggests that
  if the corpus ever lets an agent *inside* a TOPAK deployment contribute proofs or policy, the gate for that
  action is a Comparator-shaped check and not a reading: an action-alphabet entry whose admit condition is
  "statement equal, axioms within allowlist, external kernel accepts", with the reading left to the human seat.
- **Volume is the failure mode to design against.** The field's rejection was of 719 manuscripts at once, not of
  any one proof. TOPAK's ratification unit is the batch, read by the custodian, with the reviewer's guide's line
  that the custodian "read one transcription and 67 steps" at G11. That is small, and it is stated. The analogue
  of Tao's objection is that a custodian who ratifies model-drafted proofs they have not read is the prompter who
  cannot answer questions on the result; ADR-0029 A2.5's ledger line is the honest form of that, and the tranche
  argues for keeping the number of steps read in the checkpoint as a measure, not as an aside.

### 4. What the tranche does not help with

- **The prover's two unsound cases** (item 104). The tranche's whole verification story rests on the Lean kernel
  and an external re-check. TOPAK's harder residual is in TLAPS's front end, where no checker sees the translation,
  and nothing in the tranche touches it. The Lean route is TOPAK's own mitigation, and the tranche only confirms
  that the Lean kernel is the checker the field accepts.
- **Liveness** (item 105). Nothing in the tranche is a temporal proof. `Coupling_live`'s four leads-to properties
  stay unproved, and `proof-certification.md` §10's note that a Lean proof of them "cannot meet either case"
  stands.
- **The stale code-level package** (item 103). `openai/math`'s catalogue with a `comparator_config` per result is a
  weaker form of `tools/lean-sync.sh`; nothing there improves on digests and byte-for-byte regeneration.

### 5. Suggested entries, for the custodian's decision

None of these is made here.

1. **ADR-0053, open obligations:** name Comparator's `lean4export` + external-kernel route as the candidate for
   "an independent kernel for the replay", beside lean4lean, and record the axiom allowlist per package as a
   checked value in each results file.
2. **ADR-0053 §2 or `theorem-premise-binding.md`:** add the tranche's Erdős-3 pattern, "a formal statement weaker
   than the claim it is cited for", as the named failure of `enc-faithful(M)`, with the graph check as its only
   check and thirteen encodings without one.
3. **The next external-alignment document** (`derived/`): a row for AI-generated proof artifacts as a practice
   area, with Comparator's trust assumptions read against ADR-0045 Annex A, and the field's reception of the
   tranche as evidence for the disclosure lines the reviewer's guide already carries.
4. **ADR-0029 or the checkpoint template:** carry "steps read by the custodian" as a measured line in §4's ledger,
   as G11 §8 states it in prose.

---

## Sources

- OpenAI, *Sharing AI progress in mathematics*, 2026.10.06: https://openai.com/index/sharing-ai-progress-in-mathematics/ (not fetchable here)
- `openai/math`: https://github.com/openai/math (README; `lean/README.md`; `lean/ComparatorChallenges/README.md`; `lean/formalization.yaml`)
- `openai/ten-proofs`: https://github.com/openai/ten-proofs
- OpenAI, *Ten advances in mathematics and theoretical computer science*: https://openai.com/index/ten-advances-in-mathematics/
- `leanprover/comparator`: https://github.com/leanprover/comparator
- Epoch AI, *Announcing FrontierMath Erdős*: https://epoch.ai/latest/announcing-frontiermath-erdos (not fetchable here; read through search results)
- Scientific American: https://www.scientificamerican.com/article/openai-unleashes-hundreds-more-math-results-upon-a-field-already-in-shock/
- TechCrunch, 2026.10.08: https://techcrunch.com/2026/10/08/openais-math-solutions-arent-meeting-the-fields-standards-yet/
- Fortune, 2026.10.07: https://fortune.com/2026/10/07/openai-math-controversy-solutions-370-outstanding-challenges-published-criticisms-celebration/
- OfficeChai (Bloom, 23 Erdős problems): https://officechai.com/ai/openai-has-also-included-proofs-for-23-erdos-problems-in-its-latest-math-proof-drop/
- Developers Digest, *What the Lean proofs do and don't verify*: https://www.developersdigest.tech/blog/openai-math-repo-lean-proofs-what-they-verify-2026
- Redreamality, *What a passing Lean proof actually verifies*: https://redreamality.com/blog/ai-math-verification-lean-faithfulness/
- Tech-Insider (42% figure; aggregator): https://tech-insider.org/openai-math-papers-lean-verification-42-percent-2026/
