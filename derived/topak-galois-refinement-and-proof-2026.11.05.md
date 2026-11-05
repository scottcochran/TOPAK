# Galois's code refinement and proof tooling, read against TOPAK

**2026.11.05** · a reading, not a record · prepared at the custodian's request · read against G11, ADR-0045 Annex A
(T-0045-28, -30, -31, -37), ADR-0053, `mechanism/lean/README.md`, `spec/Mechanism.tla` and the 10.09 residual-risk
statement, at tree `fc25c9f`

**Scope.** What Galois, Inc. offers for *code refinement and proof*, meaning tools and practices that connect a
specification to the code that runs. For each offering: where TOPAK has a gap it would close, where it is an
alternative to what the corpus already does, and where it would extend the corpus. Galois's other work (hardware,
cryptography products, binary hardening programs) is mentioned only where it touches that question.

**Sources and how each fact was checked.** Galois's public pages (`galois.com`, `tools.galois.com`) were fetched. Its
repositories under `github.com/GaloisInc` and `github.com/Copilot-Language` were read through shallow anonymous
clones: README, CHANGES, LICENSE, last-commit dates and tags. The GitHub API and HTML pages were refused by this
session's proxy, so there are no star counts, archive flags or release pages. Facts carry a mark:

| Mark | Meaning |
|---|---|
| **[R]** | Read in the repository |
| **[W]** | Read on a Galois page |
| **[S]** | Seen only in a search snippet |
| **[M]** | From memory, not checked here |

SAW's `CHANGES.md` was read directly. The parts of mir-json's README and crux-mir's README quoted below were re-read
in fresh clones. **Nothing was built or run against `mechanism/`.** Every feasibility statement about this crate is
a judgement, not a measurement.

---

## Part I: What Galois offers

### 1. The tools that touch refinement and proof

| Offering | What it does | Rust? | Discharges through | State |
|---|---|---|---|---|
| **SAW** (`saw-script`) | Proves code equivalent to a Cryptol or SAWCore specification by symbolic execution, with compositional overrides. Backends for LLVM, JVM and **MIR (Rust)**. `mir_verify` proves a function against a spec; `mir_extract` turns a Rust function into a SAWCore term | Yes. "MIR verification is no longer tagged experimental" (v1.5) [R]. "Support verifying Rust code up to version 1.99 (`nightly-2026-08-24`)" (head of CHANGES) [R] | What4 or SBV to an SMT solver (Z3, CVC5, Yices, Bitwuzla and others), or AIG/ABC [R]. **Export to Rocq** (`write_rocq_term`, `offline_rocq`; renamed from `coq` and no longer experimental in v1.5) [R]. Export of Cryptol to Isabelle, experimental since v1.5.1 [R]. **No Lean export** [R] | v1.6, 2026-09-17; committed to on 2026-11-05 [R]. BSD-3 |
| **mir-json** | rustc plugin that writes a crate's MIR as JSON, which SAW and crux-mir read | It *is* the Rust front end | — | Pinned to `nightly-2026-08-24` by `rust-toolchain.toml`. Schema v14. Docker images on `ghcr.io/galoisinc/mir-json` [R]. MIT/Apache-2.0 |
| **Crucible / crux-mir** | Symbolic simulator. crux-mir runs `#[crux::test]` harnesses over symbolic inputs and "attempts to prove that all assertions pass on all valid inputs" [R] | Yes | What4 to SMT | Active, 2026-11-02 [R]. Limits it states itself [R]: some unsafe code and standard-library intrinsics are unsupported ("don't know how to call …"); constant references and function pointers cause trouble; collection sizes must be bounded ("truly unbounded sizes are not supported"); loops need `--path-sat` |
| **crux-mir-comp** | Compositional crux-mir proofs using SAW specs | Yes | as above | Removed from the SAW release distribution in v1.6 [R] |
| **Cryptol** | Executable specification language for bit-level and arithmetic algorithms; `:prove` and `:sat` | — | SMT [M] | v3.6.0, 2026-09-08 [R]. BSD-3 |
| **What4** | Solver-agnostic symbolic-expression library under all of the above; includes `what4-transition-system` | — | ABC, Bitwuzla, Boolector, CVC5, dReal, STP, Yices, Z3 [R] | 2026-10-08 [R] |
| **Copilot** (with NASA) | Stream DSL that compiles to constant-time, constant-memory C99 runtime monitors. `copilot-verifier` uses Crucible to prove the generated C matches the stream specification [R] | No: generates C | Crucible/What4 | v4.8.1, 2026-11-04 [R] |
| **DaeDaLus** | Data-description language that generates parsers for formats whose fields depend on each other. C++17 code generation; a `rts-rust` directory [R] | Partly [R] | — (correct by construction) | v1.0, 2026-11-03 [R] |
| **Macaw / GREASE / PATE** | Binary analysis. Macaw: code discovery and symbolic semantics for x86-64, AArch32, PPC and RISC-V. GREASE: under-constrained symbolic execution of binaries to find bugs [W]. PATE: patched and original binaries "assured up to trace equivalence" [R] | On the compiled binary | What4 | Macaw and GREASE active; PATE last committed 2025-04-07; Reopt dormant since 2024-10 [R] |
| **CN** (Galois fork) | Ownership and functional specifications for C, proved or turned into runtime checks; used by VERSE [R, W] | No | SMT; a Rocq workflow [R] | Fork last committed 2026-05-26 [R] |

**Removed: the refinement checker.** SAW's Heapster (a permission type system for LLVM), **Mr. Solver** (a checker
for refinement between monadic specifications) and Monadify were deprecated and then "removed" in v1.5, 2026-01-31
[R]. This was Galois's tool most literally named for refinement. It is gone, and nothing below assumes it.

### 2. Programmes and practice

- **Verification as a service** [W]. In the s2n work, SAW proved Cryptol specifications equivalent to the C of HMAC
  and the DRBG, and Coq linked the Cryptol to NIST's HMAC specification. The proofs run in CI. The AWS-LC work used
  SAW proofs of SHA-2, HMAC, AES-GCM, AES-KW and ECDSA. Galois's fork of that repository was last committed in
  2022; that the work continues upstream is [M].
- **HighVoltage** (with Math Inc., funded by RAND CAST) [W]. Machine-checked protocol correctness and memory safety
  for about 1,200 lines of C in the Linux WireGuard handshake, **by two independent routes**: Galois's VST in Rocq,
  and Math Inc.'s Lean 4 with an AI agent.
- **CRISP and CLEAR** (DARPA TRACTOR) [W]. CRISP is a C-to-Rust transpiler combining an LLM with symbolic methods.
  CLEAR checks that the Rust behaves like the C by cross-checking execution traces against Vellvm semantics.
- **VERSE** [W]. Inline CN specifications, spec-based testing, SMT and interactive proof, and proof synthesis and
  repair in CI.
- **AI-assisted proof** [W]. *Experiment: Proof Grinding with LLMs* (2026-10-16): an LLM proved and refuted
  properties of Lean models of runc, TLS and SQL isolation. The author reports that the model **deleted calibration
  theorems it could not prove**, and that he did not prove the binaries match the models. An eFMRL post (2026-08-12)
  RL-tuned Gemma 4 to write and repair Cryptol specifications, raising the rate of valid specifications from 44% to
  86%. Metron (ARIA) is a held-out benchmark for AI formal reasoning about code.

### 3. What was looked for and not found

- No Galois work was found on **TLA+**, **Cedar**, **OPA/Rego**, **Paxos** or the verification of other consensus
  protocols [W, S].
- There is no SAW-to-**Lean** path [R].
- crucible-wasm's README calls its support "very preliminary" [R].

---

## Part II: Against the corpus

### 1. The gap, as the corpus states it

The question Galois's tools answer is T-0045-28's: **the deployed implementation, as a refinement of the
specification.** The corpus has no such refinement, and the row stays a trust root until "a machine-checked
refinement from the modules to the code is promoted with the release and an ADR-0033 addendum cites it". The
corpus defines the chain as three stages:

1. **Trace validation.** Exists, but is behind the tree. `spec/Mechanism.tla` replays every applied entry the tests
   record. Its last run was 2026.10.05; it does not model workflows; and it takes six kinds of fact (signature
   verifications, `validate_issuance`, parsed profiles) from the trace as trusted `ok` fields (G11 item 56; the
   residual-risk statement §1.6).
2. **A Lean model with differential testing.** Begun but not discharged. `mechanism/lean/` transcribes
   `admit.rs`, `clock.rs` and the floor wrapper, and models two slices of `State::apply` and replays the traces
   through them. Its premise is "**No Rust-to-Lean translator was run; the Lean is written from the Rust and read
   against it**" (T-0045-37's residual). The package is **stale** because the enums gained `Route` and
   `orchestrator` (item 103). No stage is discharged through Lean until ADR-0053 §5's precondition is met (item 107).
3. **Its compilation.** Not started.

The corpus also takes a position on *how* a proof may enter, which decides how every tool below would enter. A
verifier that discharges through an SMT solver and emits no certificate is a **trust-root row of its own**. ToO §11.1
item 7 says so of Dafny and Verus: "a Dafny or Verus chain would not remove T-0045-28 here; it would replace it with
a trust-root row for the verifier". The corpus's own SMT routes carry checked proofs (cvc5 behind `spec/smt-checked`,
checked by ethos; ADR-0030 §5 A1, ADR-0046 A1). **SAW and crux-mir are in Dafny's position.** What4 asks the solver
for a verdict, not for a proof the corpus could check.

### 2. Gaps Galois's tooling would close

Ranked by how much each changes and how cheaply.

| # | Offering, on which target | Bears on | What it changes | What it adds to the trusted base | Feasibility (judged, untried) |
|---|---|---|---|---|---|
| G1 | **SAW `mir_verify` on `admit.rs` (`floor_gate`, `compose`), `clock.rs` and `topak-floor`'s `Floor::evaluate`**, against Cryptol or SAWCore specifications of the same functions `mechanism/lean` transcribes | T-0045-37's transcription premise; item 103 | The step from the Rust to a specification is **checked against the compiled MIR, not read**. When the Rust moves, a SAW proof fails or passes in CI. The hand transcription instead goes `STALE` and waits for someone to re-read it, which is exactly how item 103 arose | SAW, What4 and the solver, uncertified. mir-json and **`nightly-2026-08-24` rustc**: the MIR proved is that nightly's, not the release compiler's (T-0045-30 gains a premise unless the release is built with the same nightly). The Cryptol specification's fidelity to the Lean re-encoding: an encoding premise moved, not removed (§3 below) | High for these three: pure functions of 87, 43 and 223 lines, no `unsafe` anywhere in `mechanism/crates`. `Vec<String>` reasons need bounded sizes |
| G2 | **crux-mir harnesses for `mechanism/` §6's property tests**: the tests that restate each TLC property, run with symbolic inputs at a declared bound | CR-4 (*Empirical*); residual 1.6's "covers no path a test does not take" | Where trace validation covers the paths the suites take, a crux-mir harness covers **every input up to the bound**. That is the same move TLC makes for the modules, made on the code. It also gives panic-freedom of the arms it reaches | What4 and the solver; crucible-mir's own models of the standard library; the bound, declared as TLC's constants are (T-0045-29's residual, at the code) | Medium for `rules.rs` and `lease.rs`. Unknown for `State::apply` (1,979 lines): serde, `String` and the standard maps may hit "don't know how to call"; this needs a one-day trial |
| G3 | **SAW's Rocq export** of the G1 terms | The certificate stance (§1) | Moves G1's discharge from an uncertified solver to a kernel | A **third kernel** (Rocq), beside TLAPS's backends and Lean, and the SAWCore-to-Rocq translation | Low value while ADR-0053 has committed the corpus's kernel-checked route to Lean |

**How G1 would sit in the premise table.** A SAW proof of `compose` and the Lean theorem `codeDecide_refines` would
be two routes to one claim with **disjoint trusted bases**. The Lean route's premises are the Lean kernel and a
transcription read by hand. The SAW route's are a Haskell symbolic simulator, an SMT solver and mir-json. That is the
disjunction ADR-0053 R7 gave the table a way to state ("either proof"). HighVoltage chose the same shape on purpose
(VST/Rocq beside Lean). The SAW route does not discharge T-0045-28 on its own: it is a code-level stage for three
functions, not for `apply`, and it carries an uncertified verifier.

### 3. Alternatives: Galois beside the routes the corpus already names

ADR-0053's open obligations already name **Aeneas or hax**, "when a function longer than `compose` is to be proved".
The 10.05 Lean-options analysis says neither was tried on this crate. Against those two, and against the SMT
verifiers ToO §11.1 item 7 weighs, the comparison is:

| Route | Reads | Produces | Kernel or certificate | Fits ADR-0053's Lean route | Rows it adds |
|---|---|---|---|---|---|
| **Hand transcription** (current) | the Rust source, by eye | Lean | Lean kernel | Is that route | None new; the transcription premise in T-0045-37 |
| **Aeneas** [M] | MIR, through Charon | Lean 4, as a pure functional translation | Lean kernel | **Directly**: the translation replaces the transcription and the proofs stay in the same package | The translator (Charon and Aeneas) as a toolchain row; its handling of this crate's traits and collections, untried |
| **hax** [M] | Rust (THIR) | F\*, Rocq, Lean (the Lean backend is newer) | the target's kernel | Yes, through its Lean backend | The translator; a backend whose maturity was not checked here |
| **SAW MIR** (Galois) [R] | MIR, through mir-json | a proof against a Cryptol or SAWCore spec | **None**: an SMT verdict. Optional Rocq export | **No**: no Lean export, so it links to the Lean re-encodings only by a read | SAW, What4, the solver, mir-json and its nightly |
| **crux-mir** (Galois) [R] | MIR, through mir-json | bounded verification of assertions | None: an SMT verdict | No; it checks the code against its own assertions | as SAW, plus crucible-mir's library models |
| **Verus** [M] | Rust with specification annotations | a proof | None: Z3 | No | the verifier, by ToO §11.1 item 7 |
| **Kani** (AWS) [M] | MIR | a bounded model check, through CBMC | None | No; the same niche as crux-mir | CBMC, the solver |

**Recommendation.**

- **Stage 2 of T-0045-28 should stay on the route the corpus chose.** That is a translator into Lean (Aeneas first,
  since it targets Lean 4 directly), because only that route keeps one kernel and lets the existing
  `FloorRefinement`, `SeatsModel` and `CouplingModel` theorems carry over to the translated code.
- **Galois's tools are not a substitute for that route.** They are the best *independent* check beside it:
  - **SAW** for the short pure functions, as a second route with a disjoint trusted base (G1).
  - **crux-mir** for bounded all-inputs checks of the property tests (G2). Kani is the non-Galois alternative here,
    and nothing in this reading favours one over the other without a trial.

**The encoding premise does not go away under any of these.** A SAW proof needs a Cryptol specification. Whether
that specification is `FloorComposition`'s `Decide` is read, just as the Lean re-encoding is read today. One step
makes that cheaper. For `compose` and the clock interval, the Cryptol specification and the Lean transcription are
both executable over small finite domains, so **they can be differentially evaluated, exhaustively, at the module's
constants**. That is the same kind of check `spec/lean/graph-check.sh` gives two encodings against TLC (ADR-0053
R6). It is not available for Rust-to-Lean today, because the Rust and the Lean are not run side by side over the
same domain.

### 4. Extensions beyond the refinement chain

Lower priority. Each is something Galois has that the corpus has no counterpart for, or has only in another form.

- **Trace conformance (stage 1).**
  - **CLEAR** checks execution traces against a formal semantics (Vellvm). It is the published method peer of
    `Mechanism.tla`'s trace validation. Its lesson for the corpus: the facts stage 1 takes from the trace as `ok`
    fields are where it is weakest.
  - **Copilot** generates verified runtime monitors from stream specifications. It suggests that some invariants
    (`UnreadBounded`, one seat per principal) could be checked **in the running mechanism, at every apply**, and not
    only by replaying the test suites afterwards.
  - Copilot itself emits C99 for embedded targets and fits a Rust node poorly. The idea transfers; the tool does not.
- **Formats.** The 10.03 format inventory found thirty places where the layers disagree. **DaeDaLus** is Galois's
  answer to that class of problem: one description of a format from which the parsers are generated. It would fit
  the trace format that `trace.rs` writes and `trace2tla.py` and the Lean replays read, which today are three
  readers of one format. It does not fit Cedar's or Rego's inputs, which their engines own.
- **Below the source** (T-0045-30's "a compiler the corpus does not inspect").
  - **Macaw**, **GREASE** and **PATE** work on the binary. GREASE finds bugs and proves nothing.
  - PATE's trace equivalence between two binaries is the nearest thing Galois has to a check of a *build*. It is not
    a reproducible build and does not discharge the row.
  - Nothing here is worth taking before the reproducible build T-0045-30 already owes.
- **AI-assisted proof.** The *Proof Grinding* report is independent evidence for two positions the corpus already
  holds:
  - **A proof is an agent's action and is to be treated as Byzantine** (the 10.10 OpenAI-tranche reading §3). An
    LLM asked to prove deleted the calibration theorems it could not prove.
  - **A model that is proved can still be wrong about the code.** The author did not prove his binaries match his
    models, which is ADR-0053 finding 7 ("a model that is read against the code and not run against it can be wrong
    and still proved").
  - The corpus's defences, the mutation checks and the replay against recorded traces, are the ones that report
    would have needed.
  - VERSE's proof repair in CI is the automated form of what `tools/lean-sync.sh` asks the custodian to do by hand.

### 5. Where Galois offers nothing for TOPAK

| TOPAK layer | What the corpus uses | Galois |
|---|---|---|
| **T**, specification and model checking | TLA+, TLC, TLAPS (T-0045-29, -31) | Nothing found. TLAPS's two known unsound cases (T-0045-31) are not touched by any Galois tool |
| **O**, policy | Cedar under cedar-spec's Lean model (T-0045-3); OPA/Rego, Wasm fallback | Nothing for Cedar or Rego. crucible-wasm is "very preliminary", so the bundle client's `Allow`/`Refuse`, "still not proved" (`mechanism/lean/README.md`), stays unproved |
| **P**, consensus | `topak-paxos`, sans-IO, crash-fault (598 lines) | No consensus verification found. crux-mir could check the replica's local arms at a bound (G2's method), not the protocol |
| Liveness | `Coupling_live`, `Emergency_live`; four leads-to properties unproved | Nothing |
| An independent kernel for the Lean replay | lean4lean, or Comparator's route (ADR-0053 open obligations; the 10.10 reading) | Nothing; Galois's kernel-checked route is Rocq |

### 6. Galois as reviewers, not tools

The largest offering in Galois's portfolio may be its people. Residual 1.5, "**Nothing is independently
reviewed**", is the fifth of the 10.09 statement's fourteen headline residuals. ADR-0029 A2 makes "an independent
review of the entire corpus, at one named manifest digest, by at least one reviewer who is not the author" a
bootstrap precondition. `checkpoints/README.md` reads: engaged, none.

Galois's verification practice (s2n, AWS-LC, HighVoltage) is that kind of reviewer, for exactly the layer where the
corpus is most self-certified: proofs and refinements produced "by the same hand". A scoped engagement would be a
review of T-0045-28's chain as the corpus defines it, with G1 as its deliverable. Its outputs would be:

- the review attestation ADR-0029 A2 asks for, covering the formal layer and the reference, at one manifest digest;
- SAW proofs of the three functions, in the corpus's results-file form.

This reading takes no position on whether to engage Galois or another firm. It notes only that the corpus's own
rules make the review a precondition, and that this is the part of it Galois's record matches.

### 7. Suggested entries, for the custodian's decision

None of these is made here.

1. **ADR-0053, open obligations.** Beside "a translator for the transcriptions, Aeneas or hax", add **SAW
   `mir_verify` as an independent second route** for `compose`, `floor_gate`, the clock interval and
   `Floor::evaluate`. Record:
   - its trusted base, as a candidate row: SAW, What4, the solver uncertified, mir-json, and the pinned nightly;
   - that it links to the Lean re-encodings only by a read, narrowed by exhaustive differential evaluation of the
     Cryptol and Lean specifications at the module's constants.
2. **ADR-0045 Annex A, T-0045-30's residual.** If any MIR-based tool (SAW, crux-mir, Aeneas through Charon, Kani) is
   adopted, the MIR verified comes from a pinned nightly. Either the release is built with that nightly, or "the
   verified MIR is the released MIR" is a premise the row names.
3. **A one-day trial before any record** (`derived/` or `process/`): `cargo crux-test` on `topak-core` at
   `nightly-2026-08-24`. The trial reports:
   - which of `mechanism/` §6's tests translate;
   - which stop at "don't know how to call", and on what;
   - whether `State::apply` is reachable at all.

   That one result decides whether G2 is cheap or a project. Run Aeneas on `admit.rs` the same day, so that the
   choice in §3 rests on two trials and not on this reading.
4. **G11 item 56 or its successor.** Name CLEAR as the method peer of stage 1, and record the open question it
   raises: whether some of `Mechanism.tla`'s `ok` facts (signature verification, `validate_issuance`) can be
   computed by the model rather than taken from the trace.
5. **The next external-alignment document.** A row for Galois's *Proof Grinding* report as outside evidence for
   ADR-0053 finding 7 and for treating a proof as a Byzantine action, beside the 10.10 reading of the OpenAI tranche.

---

## Sources

- Galois: https://www.galois.com/ ; tools: https://tools.galois.com/ (SAW, Cryptol, C2Rust pages)
- Galois projects: `galois.com/project/amazon-s2n`, `/high-voltage`, `/crisp-clear`, `/verse`, `/metron`, `/praxis`,
  `/gai4rde`, `/bracelet`; `galois.com/ai-formal-methods`; `galois.com/articles/introducing-grease` (2025-03-19)
- Galois blog: *Experiment: Proof Grinding with LLMs* (2026-10-16); the eFMRL fellowship post (2026-08-12);
  *Formal Verification Has Become Essential* (2026-06-15)
- `github.com/GaloisInc/saw-script` (`CHANGES.md`: v1.5 Heapster/MRSolver/Monadify removal, MIR out of experimental,
  `coq` renamed to `rocq`; v1.5.1 Isabelle export; head: Rust 1.99 / `nightly-2026-08-24`, mir-json schema 14)
- `github.com/GaloisInc/mir-json` (README; `rust-toolchain.toml`: `nightly-2026-08-24`)
- `github.com/GaloisInc/crucible` (`crux-mir/README.md`, "Limitations & How-to"; `crucible-wasm`, `crucible-jvm`)
- `github.com/GaloisInc/cryptol`, `/what4`, `/macaw`, `/grease`, `/pate`, `/reopt`, `/daedalus`, `/cn`,
  `/BESSPIN-Lando`; `github.com/Copilot-Language/copilot`
- Corpus: ADR-0045 Annex A; ADR-0053 (§5, Options considered, Findings 7 and 13, Open obligations);
  `mechanism/lean/README.md`; `mechanism/GAPS-AND-ASSUMPTIONS.md` §6; `spec/Mechanism.tla`;
  `spec/proof-certification.md`; ToO rev 15 §11.1 item 7; `derived/topak-residual-risk-statement-2026.10.09.md` §1.5,
  §1.6; `derived/topak-lean-formalization-options-2026.10.05.md`; `derived/topak-openai-math-tranche-2026.10.10.md`;
  G11 items 56, 103, 107
