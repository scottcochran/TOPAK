# Verifying that the reference refines the specification: the options at G11

**2026.11.04** · derived · an answer, not a record · basis: the tree at `147bc72` (G11, ToO rev 15), ADR-0033, ADR-0045
(T-0045-28, Annex B), ADR-0046, ADR-0053, `mechanism/lean/README.md`, `spec/Mechanism.tla`, `tools/LEAN-PIN` ·
written by the assistant in answer to "what are the options for verifying the refinement of the Rust admit-path
reference implementation; Verus, Kani, what AWS and Cedar use" · not entered in `derived/README.md`; nothing here is
built or ratified.

**How it was researched.** Fifty-one agent runs with web access on 2026.11.04: ten surveys (Verus, Kani, Aeneas and
Charon, hax, the rest of the Rust verification landscape, Cedar, AWS's other systems, TLA+-to-code methods, the
"compile the model" family, proof certificates), forty load-bearing claims each re-read against a primary source by a
separate run told to refute it, and one completeness pass. Every external fact below carries the source it was read
in; "read 2026.11.04" means the page as it stood that day. Where a verifier could not reach a primary source the claim
is marked so. Repository facts were read from the tree directly.

---

## 0. Short answer

1. **No tool removes T-0045-28.** Every route either keeps the code-to-spec link a tested premise, or replaces the
   premise with a trust-root row for a verifier or translator. The narrative's sentence that "a Dafny or Verus chain
   would not remove T-0045-28; it would replace it with a trust-root row for the verifier" is confirmed by the
   evidence for Verus, Dafny, Kani, Creusot, Prusti, Flux and hax-to-F\*. The question is therefore which premise the
   corpus would rather hold, and what it costs to make each one checkable.
2. **Verus** proves a rewritten dialect of the code against a hand-written Verus spec, through Z3 without a
   certificate. It would add a row the corpus has said it will not add, and move the READ premise from the code side
   (Rust is the Lean) to the spec side (the Verus spec is `Mechanism.tla`). Not a fit under ADR-0045 §2 as written.
3. **Kani** checks the real code, bounded, through CBMC and a SAT solver without a certificate. It fits the corpus only
   as a tester whose failures subtract: an exhaustive-within-bounds differential check, and an unbounded one for the
   loop-free `compose` and clock check. It adds no row if no theorem is claimed from it.
4. **Aeneas** (Charon → LLBC → Lean) is the one route that yields kernel-checked statements about definitions derived
   mechanically from the real code, inside the row the corpus already holds (T-0045-37). It trades the READ premise for
   a pinned, deterministic, replayable translator premise and hand-written models of `BTreeMap`/`BTreeSet`. It is the
   right reading of "stage 3", and it has not been tried on this crate (ADR-0053's own note). A pilot on `admit.rs`,
   `clock.rs` and `lift.rs` is days; `State::apply` is months and needs refactoring first.
5. **AWS does not prove its Rust against specifications.** Cedar is a Lean model with proofs, a Rust implementation,
   and differential random testing between them; the production symbolic analyser is a Rust port tested the same way.
   The Nitro Isolation Engine proves a hand-transcribed model of its Rust in Isabelle/HOL and replays traces of the
   binary through a code-generated executable model: the shape this corpus already has. Kani runs in CI as a bounded
   bug-finder. Dafny-compiled Rust ships in the Encryption SDK. AWS's stated position is "formal specifications as
   oracles or monitors" for testing.
6. **The cheapest real gain is already in the tree.** `mechanism/lean/SeatsReplay.lean` and
   `spec/mechanism-trace-run.sh` consume any trace file `trace.rs` writes. Driving them with generated action sequences
   instead of the test suites' is Cedar's differential testing without Cedar's compiled-oracle rows, and mutation
   analysis over `state.rs` with those replays as the test gives the residual of T-0045-28 a number. Both add no row.
7. **One precondition first.** The Lean pin, `leanprover/lean4:v4.33.1`, predates kernel soundness fixes shipped in
   v4.34.0 (2026.09.14) and the external checkers `lake check --paranoid` runs since v4.35.0 (2026.10.12). No new Lean
   work should be cited on the current pin.

---

## 1. The question in the corpus's terms

**The row.** ADR-0045 T-0045-28: the deployed implementation as a refinement of the specification, `mechanism/`
against `spec/`; a trust root until "a machine-checked refinement from the modules to the code is promoted with the
release and an ADR-0033 addendum cites it". ADR-0033 owns it as a debt in three stages: trace validation (exists since
2026.09.30), "a Lean model with differential testing", "its compilation". ADR-0053 §5 R1 adds the precondition for any
stage discharged through Lean: the premise table must state alternative premise sets (done, R7), and every encoding the
stage refines must have a check or a second reader behind it (done for `Seats` and `FloorComposition` by the graph
check, R6; owed for the rest).

**The acceptance test.** ADR-0045 §2: a component enters the trusted base only if its failure can only subtract, or it
is a trust-root row with an issued or pinned identity. Finding 1 refused the solver's bare UNSAT and ADR-0030 A1 put
`ethos` behind cvc5's CPC proofs; ADR-0046 A1 did the same for the TLAPS run; ADR-0053 took the Lean kernel as a row
with `leanchecker --fresh` replay and lean4lean as the open item. So the survey's question for each option is: does it
yield an artifact a small pinned checker can re-check, and if not, which row does it add, and can that row's failure
be made to subtract?

**The code.** `topak-core`, 6,239 lines, edition 2024, no `unsafe`, no `async`, four `dyn Fn` parameters, about fifty
closures in `state.rs`, 66 `BTreeMap` and 87 `BTreeSet` mentions, serde derives on every type, `ed25519-dalek` 2.2.0
for signatures (`authentic.rs` calls `verify`, not `verify_strict`), `sha2` 0.10.9. `State::apply` is about a thousand
lines in ten arms; `admit.rs` is 87 lines; `clock.rs` 43. `topak-floor` links `cedar-policy` 4.13.0, already a row
(T-0045-3). `mechanism/Cargo.toml` declares no release profile, so release builds wrap on integer overflow.

**What exists.** Stage 1: every applied entry of six suites recorded by `trace.rs` and replayed through
`spec/Mechanism.tla` by TLC, with `spec/ConfinementRefinement.tla` reading the states (82 traces, about 1,000 steps;
behind the tree since the workflow build, G11 item 56). Beside it, ADR-0053: hand transcriptions of `admit.rs`,
`clock.rs` and the floor wrapper proved in Lean, the decision proved a `Decide` step of `FloorComposition`; a model of
`apply`'s seat and lease arms proved to refine `Seats` at its constants; a second model proving `Coupling`'s properties;
both models replaying the same 82 traces through `lake env lean --run`, the compiler path, not the kernel. The
fidelity of each transcription to the Rust is read, not checked. Mechanical translation (Aeneas, hax) was "not taken
now: neither was tried on this crate".

So the question splits in three: how to replace or check the code-side READ premise; which verifier's trust the corpus
can declare; and what "stage 2" and "stage 3" should be taken to mean, since the words in ADR-0033 admit more than one
reading (§5).

---

## 2. The options

Each option is read against the same frame: what it proves and of what artifact (the real code, a dialect, or a
translation); what it adds to or removes from the trusted base; whether it yields an independently checkable
certificate; its fit with this code; effort; verdict.

### 2.1 Verus

**What it is, at the read.** Weekly releases (0.2026.11.02 the latest), the toolchain file on `main` pinning a stable
rustc (1.99.1), Z3 pinned at 4.16.0 (released 2026.02.19), `vstd` at edition 2021. Code is verified inside the
`verus!` macro; the same source builds under plain cargo because the ghost code is erased, so the verified artifact
can be the shipped artifact. Sources: https://github.com/verus-lang/verus/releases,
https://raw.githubusercontent.com/verus-lang/verus/main/rust-toolchain.toml,
https://raw.githubusercontent.com/verus-lang/verus/main/source/tools/get-z3.sh (read 2026.11.04).

**Refinement in Verus.** `state_machine!` generates `init`/`next` and the user writes an abstraction function and one
lemma per transition (`examples/state_machines/refinement.rs`); the reference chapter "Refinements" is a TODO. Anvil
(OSDI 2024) connects implementation to model by a postcondition `ensures res@ == Model::m_step(d@, r@, s@)` over
`view()` functions, and its conformance proofs are 172 to 290 lines for 1,100 to 1,600 lines of implementation, plus a
ghost model of about the implementation's size; the 4.5 to 7.4 proof-to-code ratios come from the liveness proofs,
which this corpus does in TLAPS and Lean. Temporal reasoning needs the hand-written `verus-tla` embedding (85 trusted
lines; "an embedding of the logic, not a translator"). Sources:
https://www.usenix.org/system/files/osdi24-sun-xudong.pdf, https://github.com/anvil-verifier/verus-tla (read 2026.11.04).

**The peer the corpus cites.** Khan (arXiv:2606.17182, 2026.06.15) hand-writes Verus `spec fn`s beside separate TLA+
modules; nothing mechanical links them; the TLAPS work is self-described as "a textual-consistency check, not a
correctness argument"; the refinements are of "a concrete-side state record mirroring the relevant fields of the
deployed Rust `Inner` struct"; the stated trust base is Verus and its SMT solver, `vstd`, two axioms and three
`external_body` stubs. The artifact's README (`mac-consistency-mono`) discloses that one definition "is transcribed in
four places" with a script that fails if they disagree on committed cells: a finite agreement test on a hand
transcription, not a bridge. Source: https://arxiv.org/html/2606.17182 (read 2026.11.04).

**Fit.** Closures may not capture by mutable borrow; `dyn` is "partially supported"; serde derives need
`#[verifier::external_derive]`, whose stacked form is broken for a type deriving both `Serialize` and `Deserialize`
(issue #3413, opened 2026.11.02); `vstd::std_specs::btree` models `BTreeMap`/`BTreeSet` but a soundness fix (issue
#3029, PR #3365) was approved and not yet merged at the read, and `range`/`entry` have no spec; async is on `main` with
an open soundness issue (#3175). Edition-2024 support of the macro could not be verified. The port is a rewrite of
`topak-core` into the Verus subset with `vstd` views for every collection. Sources:
https://verus-lang.github.io/verus/guide/features.html, https://github.com/verus-lang/verus/issues/3413,
https://github.com/verus-lang/verus/pull/3365 (read 2026.11.04).

**Trusted base and certificates.** The OOPSLA 2023 and SOSP 2024 papers name the Verus pipeline, rustc's borrow
checker, `vstd`'s axioms, every `external_body` and Z3; Amazon's 2026.08.31 post says Verus's guarantees "rely on the
correctness of Verus itself". No certificate: `-V cvc5-smtlib` (PR #3205, merged 2026.10.15, an Amazon contributor)
re-answers the same queries with cvc5, a second solver verdict; `-V cvc5` exists as an experimental solver mode
pinning cvc5 1.3.4, which can emit CPC proofs, but Verus requests none and nobody has shown its quantifier-heavy
queries discharge in cvc5's safe mode with complete proofs. Vermilion (2026.10.18) sends Verus obligations to Lean;
its lowering is "the largest Vermilion-specific trusted component" and it "cannot tell us that we emitted the right
statements". A CMU thesis (2026.05) formalises one translation pass with the soundness theorem unfinished. Sources:
https://github.com/verus-lang/verus/pull/3205,
https://proofsandintuitions.net/2026/10/18/vermilion-experiment-lean-backend-verus/,
https://www.amazon.science/blog/developing-provably-correct-rust-code-with-verus (read 2026.11.04).

**Industrial use.** Amazon: "key primitives used by the Nitro Isolation Engine" and unnamed infrastructure
(2026.08.31). Microsoft Research: verified-storage, a JPEG 2000 decoder with 3,544 obligations under `--no-lifetime`,
a research preview of a proof-driven development kit (2026.10.21). Verus's application to the Rust standard library
verification campaign was approved 2026.05.11 and not integrated as of 2026.10.21. Sources:
https://github.com/model-checking/verify-rust-std/issues/554, https://github.com/microsoft/jpeg2000_rs/issues/132.

**Verdict.** It proves a dialect against a third encoding of the spec (TLA+, Lean, Verus), adds Verus plus Z3 4.16.0
plus `vstd` as an uncertified row, and keeps a READ premise, now "the Verus `spec fn` is `Mechanism.tla`". The one
case in which it earns its row: the corpus decides the reference itself must be the proved artifact, accepts a verifier
row on the terms it accepted TLAPS, and someone first shows the `-V cvc5` output can be checked by `ethos`. Then the
smallest coherent package is Anvil's: `ensures post@ == mechanism_step(pre@, cmd@)` on `State::apply`, under
`--no-cheating`, with the Verus spec and `Mechanism.tla` replaying the same traces. It should be declared as an
alternative route, not as stage 2 or 3.

### 2.2 Kani

**What it is, at the read.** kani-verifier 0.68.0 (2026.09.16), CBMC 6.11.0, CaDiCaL default, its own pinned nightly
so the crate's toolchain is irrelevant. Function contracts, loop contracts, stubbing and quantifiers are all `-Z`
unstable; `#[kani::loop_decreases]` is new in 0.68.0; `BoundedArbitrary` for `BTreeMap`/`BTreeSet` shipped in 0.68.0
(PR #4626), whose own CI test stalled at bound 2 and was reduced to 1. Sources:
https://github.com/model-checking/kani/releases/tag/kani-0.68.0, https://github.com/model-checking/kani/pull/4626,
https://model-checking.github.io/kani/reference/experimental/loop-contracts.html (read 2026.11.04).

**What it proves, of what.** The real MIR of `topak-core`, for all inputs up to the unwinding and collection bounds;
unbounded where there are no loops. For `floor_gate`, `compose` and `subtracting_interval_elapsed` a harness comparing
the Rust against a Rust transcription of the Lean definitions is loop-free and so a full check over all enum and `u64`
inputs, with no contracts: a mechanical check that the hand transcription matches the code, for those two files. For
`State::apply` the arms iterate `BTreeMap`s, which are custom iterators outside the loop-contract list, so the result
is bounded to two to four keys and restates what TLC already explores. `cedar_policy`, `ed25519-dalek`, `sha2` and
`serde_json` would be stubbed, so the check is "for every outcome of those components": the right shape for T-0045-3,
and nothing about their behaviour. Kani has no refinement feature; the published pattern is the differential harness
(s2n-quic's RFC decoder against the RFC pseudocode; the ASE 2026 paper's Cedar experiment, which found a panic Cedar's
differential testing against its formal model had missed, and which Cedar does not run in CI). Sources:
https://arxiv.org/html/2607.01504, https://github.com/cedar-policy/cedar/pull/1037 (read 2026.11.04).

**Trusted base and certificates.** AWS's own papers: the MIR-to-GOTO translation, CBMC and the SAT/SMT solver, "none of
these tools have been formally verified themselves" (NFM 2026). CBMC accepts a solver's UNSAT from a bare status line
on every backend path and emits no DRAT, LRAT or SMT proof; Kani's artifacts are status reports and, for failures,
concrete-playback tests. The only certificate route is a solver wrapper writing DRAT checked by `drat-trim` or a
verified LRAT checker, which certifies the CNF and leaves CBMC's symbolic execution, bit-blasting and Kani's
translation trusted. Sources: https://arxiv.org/html/2606.17374,
https://github.com/diffblue/cbmc/blob/cbmc-6.11.0/src/solvers/sat/external_sat.cpp (read 2026.11.04).

**Verdict.** Under ADR-0045 §2 Kani is admissible as a tester: a FAIL is a replayable witness that subtracts, a PASS
claims nothing the corpus writes down. Filed that way it adds no row and is the only option that executes the real
MIR with symbolic inputs. Filed as proof it adds a four-component row with no `leanchecker`-style replay. Effort: one
to three days to build the crate under Kani with stubs; a week for the `admit.rs`/`clock.rs` equivalence harnesses;
two to six weeks for per-arm `apply` harnesses at small bounds, with a CI budget near Firecracker's twenty minutes.
Kani also carries an undocumented, unstable `-Z lean` backend that emits Charon LLBC for Aeneas; it inherits every
Aeneas limit below and offers nothing over running Charon directly.

### 2.3 Aeneas and Charon (Rust to Lean), and hax

**What it is, at the read.** Charon (rustc driver, MIR to LLBC) and Aeneas (LLBC to pure functional Lean, F\*, Rocq or
HOL4) are active (commits 2026.11.03); Lean is the recommended backend, pinned to Lean v4.35.0 with Mathlib; Charon
on the nightly of 2026.09.17. Generated Lean is executable: `Result` is a coinductive `ITree` since 2026.09.08 with a
`Repr` instance since 2026.10.06, run through Lean's compiler (`#eval`, `#guard`), while closed `Result` terms do not
reduce by `rfl` or `decide` in the kernel (the con-ron findings, 2026.10). Sources: https://github.com/AeneasVerif/aeneas,
https://raw.githubusercontent.com/AeneasVerif/aeneas/main/backends/lean/Aeneas/Std/Primitives.lean,
https://github.com/leanprover/con-ron/blob/master/AENEAS_FINDINGS.md (read 2026.11.04).

**Subset against this code.** Loops become recursive functions or loop combinators; traits and generics become explicit
dictionaries; nested borrows in signatures and borrows inside ADTs translate (brittle in context joins); closures that
are stateless or capture by shared borrow translate; what does not: a method call through `dyn` (issue #1500; the four
`dyn Fn` parameters in `state.rs` and `workflow.rs`), an ADT holding a nested mutable borrow (#1503), `break` to an
outer loop (#1501; `workflow.rs` has one labelled `break 'find`), a closure writing through a captured `&mut`, a
generic instantiated with `&mut`. Upstream Aeneas ships no model of any `std::collections` type: the generated builtin
table has zero `BTreeMap`, `BTreeSet` or `HashMap` entries, so every collection call becomes an opaque external the
user models by hand in Lean (`FunsExternal.lean`), or the collections are replaced by an in-subset map (the con-ron port
did the latter). A public fork (gilescope) carries partial models, unproposed upstream. Integer arithmetic is modelled
with panic-on-overflow semantics, so the verified semantics is the debug build's unless the release profile enables
overflow checks. Serde derives would be excluded through Charon's `--opaque`/`--exclude` patterns; no primary source
addresses serde. Sources: https://github.com/AeneasVerif/aeneas/issues/1500,
https://github.com/AeneasVerif/aeneas/issues/1501, https://github.com/AeneasVerif/aeneas/issues/1503,
https://raw.githubusercontent.com/AeneasVerif/aeneas/main/src/extract/ExtractBuiltinLean.ml (read 2026.11.04).

**Trusted base and certificates.** The ICFP 2024 paper proves the symbolic semantics a sound borrow checker and "leave[s]
a discussion of the correctness of the Aeneas functional translation to future work"; the Rocq mechanisation
(`mechanized-llbc`) covers the calculus, not the OCaml implementation; Charon calls itself "beta software" whose
translation is "well-tested"; the SymCrypt report (2026.09.14) lists Charon and Aeneas as trusted. Charon's output is
documented deterministic per version and options, so a translator row has a pinned identity and a replayable product.
Soundness-shaped reports exist (#1525, 2026.11.03, a `Cell::set` through `&self` modelled as pure, open and
unanswered at the read). The theorems proved over the output are Lean terms the existing row replays; the `#eval` replay
of traces through the output is testing, under the compiler. Sources: https://arxiv.org/abs/2404.02680,
https://arxiv.org/html/2609.15648v1, https://github.com/AeneasVerif/aeneas/issues/1525 (read 2026.11.04).

**Users.** Microsoft SymCrypt: 16.7 KLOC of Rust (ML-KEM, SHA-3) verified with 237 KLOC of Lean, shipping in Windows
insider builds (2026.07.13); Google's jxl-rs case study and a zerocopy investigation; the Lean FRO's con-ron (a Rust
kernel checker, about 50 KLOC Rust, 18 refactors to translate); hax 0.4's Lean backend. No AWS use found. Sources:
https://www.microsoft.com/en-us/research/blog/verifying-rust-cryptography-in-symcrypt-from-standards-to-code/,
https://github.com/leanprover/con-ron (read 2026.11.04).

**hax.** Since 0.4.0 (2026.09.04) `cargo hax into lean` runs Charon and a fork of Aeneas (`pereq-dev/aeneas`, fourteen
fork patches, the hax-specs producer among them) and "does not use the hax engine"; the shipped 0.4.2 pins Lean
v4.31.0, which Cryspen's own release post says "has some known soundness bugs", while `main` is on v4.35.0. Its
`core-models` library has a dummy `BTreeSet` with `new` only and no `BTreeMap`. Its F\* backend, the only one marked
stable, is Z3 without certificates plus `assume val` axioms, which the corpus has refused elsewhere; a 2026.04.07
third-party analysis documented silent failure modes on that path. For a Lean-anchored, non-cryptographic state machine
hax adds a fork and a spec layer to the row and removes nothing. Sources:
https://hax.cryspen.com/blog/2026/09/29/hax-04-easier-to-install-and-configure-and-a-new-lean-backend/,
https://raw.githubusercontent.com/cryspen/hax/main/docs/manual/faq/trust.md, and the analysis as IACR ePrint
2026/670, https://eprint.iacr.org/2026/670.pdf (read 2026.11.04).

**Verdict.** Aeneas is the only route in which the kernel-checked artifact is about definitions derived from the code by
a tool rather than by a reader, and the only one whose added row is a translator with a deterministic, pinned,
replayable product rather than a solver's verdict. It does not remove T-0045-28: it replaces a READ premise with a
translator row plus hand-written collection models, and it needs a refactor before it runs (`dyn Fn` to generics or
enums, the labelled break, closures over `&mut`, `entry`/`get_mut` shapes). The honest sequence is: run it as a
non-trusted oracle first (generate Lean for `admit.rs`, `clock.rs`, `lift.rs`; prove the generated functions equal the
hand transcriptions in `mechanism/lean/Topak/Admit.lean` and `mechanism/lean/Topak/Clock.lean`; replay the 82 traces
through both); promote Charon and Aeneas to a row only when that equivalence holds and the collection models exist. Pilot:
days. `State::apply`: two to six weeks of refactoring and modelling, then proofs; SymCrypt's ratio is about seven lines
of hand Lean per generated line, so months of human work or weeks of agent-written proofs under review. Lock-step pins
(Lean, Mathlib, the Charon nightly) are a standing cost, and `spec/lean` would move with them.

### 2.4 The rest of the Rust verification landscape

| Tool | Artifact and method | Adds | Certificate | Fit with `topak-core` | Verdict |
|---|---|---|---|---|---|
| **Creusot** 0.14.0 (2026.10.12) | Pearlite contracts on the real MIR; Rust → Coma → Why3 → why3find → Alt-Ergo/Z3/cvc5; prophecies for `&mut`; closures, traits, iterators, minimal `dyn` | Creusot translator, Why3 VC generation, solver verdicts; `creusot-std` ships `HashMap` views only, no `BTreeMap`/`BTreeSet` specs; Alt-Ergo's licence excluded by the std-library campaign | None by default; a per-goal Rocq escape hatch through Why3 the maintainers do not plan to support; Why3 1.9.0 (2026.10.19) has no certificate feature | Most practical annotation route; `apply` would need hand-written trusted specs for every map call | Adds the uncertified-solver row plus two translator rows; the refinement statement would be a third hand encoding of the spec |
| **Prusti** | Viper (Silicon over Z3); active again (24 PRs merged 2026.10.19 to 10.30) | Viper and Z3 | None | Closures, iterators, references in enums unsupported per its guide | Not a fit |
| **Flux** | Quantifier-free refinement types over Z3 and liquid-fixpoint; no releases | Z3 | None | Cannot state a transition-system refinement; arithmetic only | A subtract-only extra check for `clock.rs` at most |
| **RefinedRust** (OOPSLA2, 2026.10) | Foundational: real post-borrowck MIR against the Radium semantics, Rocq proof terms; traits, closures, iterators | Rocq kernel (a second kernel row), the frontend, Radium, rustc trait resolution | Rocq kernel | No `dyn`, no slices, no async; proof burden set by invariant depth (about ten proof lines per LOC on the allocator case) | The only annotation route that meets the certificate bar, at person-year cost and in the wrong prover |
| **Corten** (2026.09), **rocq-of-rust** | THIR to Rocq, unverified transpiler; ~300 LOC and work-in-progress respectively | Rocq kernel plus transpiler | Rocq kernel | Same translator shape as Aeneas, second kernel | Not a fit |
| **Foundational VeriFast** (2026.01) | VeriFast emits a Rocq replay script; no loops, structs or generics yet | Rocq kernel | Rocq kernel | Unsafe-code tool; rejects closures | Watch only |
| **Crux-MIR** v0.12 (2026.01) | Bounded symbolic execution against an executable spec; AWS used it on ShardStore deserialisers | What4, Yices or Z3 | None | Kani-class bounded equivalence | Redundant with Kani |
| **KMIR** | Executable K semantics of stable MIR with a prover | K framework | None | No `Vec`, `BTreeMap`, `dyn`, strings | Not usable |
| **AutoCorrode** (awslabs, Isabelle/HOL) | Shallow embedding of a Rust subset, hand-transcribed; the Nitro Isolation Engine's method | Isabelle kernel and runtime | Isabelle | Exactly the corpus's current shape in a third prover | Rejected explicitly, so the survey is complete |

Every tool in this table and above trusts rustc's lowering to MIR as the de facto Rust semantics: there is no official
formal or executable semantics (MiniRust "extremely incomplete"; a-mir-formality "early-stage experimental"; the 2026
executable-specification goal accepted and marked "Funded: No", with no progress reported through 2026.10.29). The
corpus should declare that premise once, as one row, and note that no option removes it. Sources:
https://github.com/creusot-rs/creusot/blob/master/CHANGELOG.md, https://iris-project.org/pdfs/2026-oopsla-refinedrust2.pdf,
https://goals.rust-lang.org/2026/executable-spec.html, https://github.com/rust-lang/goals/issues/749 (read 2026.11.04).

### 2.5 Compile the model: Dafny to Rust, Lean as the core, Lean to Rust

**Dafny to Rust.** Dafny's Rust backend is marked `IsStable` (run in integration tests) and `IsInternal` ("should not
be documented in the reference manual"); the manual's target list omits it and the integration page says it "is not an
officially supported backend yet"; seven wrong-code or invalid-code issues were filed against 4.11.0 in late 2026.10
and are open. AWS ships it anyway: `aws-esdk` 1.0.0 (2025.02.03), `aws-db-esdk`, `dafny-runtime`, the Material
Providers Library vendored and as `aws-mpl-legacy`, with a separate Dafny version pinned for the Rust build. Dafny's
verifier is Boogie and Z3 with no certificate; the only verified extraction is a HOL4 Dafny-to-CakeML chain for a
subset (2025.12), which does not target Rust. For TOPAK this would mean rewriting the specification in Dafny, adding a
verifier row and a backend row, and setting the Lean row aside. Sources:
https://raw.githubusercontent.com/dafny-lang/dafny/master/Source/DafnyCore/Backends/Rust/RustBackend.cs,
https://dafny.org/latest/DafnyRef/integration-rust/IntegrationRust, https://github.com/dafny-lang/dafny/issues/6592,
https://crates.io/api/v1/crates/aws-esdk (read 2026.11.04).

**The Lean model compiled and run as the decision core.** Cedar's FFI shape makes it mechanically possible
(`cedar-lean-ffi`: six static libraries from `lake build :static`, the Lean runtime initialised once, one Lean thread,
protobuf in, JSON out). It replaces the transcription premise for the arms the model covers with the Lean code
generator, the Lean runtime, a C compiler and the marshalling layer, none certified and each a failure that can add.
Lean's new code generator (default since v4.22.0, 2025.08.14) is unverified, the FRO roadmap plans no verification,
and a wrong-code bug (match on a boxed `USize`, `native_decide` proving `False`) was fixed on `master` on 2026.11.03
with no release containing the fix at the read; it affects every release with the new compiler, the pinned 4.33.1
included. Cedar's own paper rejected deployment of compiled Lean ("a bug in the Lean compiler could lead to security
issues", among maintainability reasons), and the production analyser is a Rust port. Sources:
https://raw.githubusercontent.com/cedar-policy/cedar-spec/main/cedar-lean-ffi/src/lean_ffi.rs,
https://github.com/leanprover/lean4/issues/16205, https://github.com/leanprover/lean4/pull/16211,
https://arxiv.org/html/2407.01688 (read 2026.11.04).

**Lean to Rust.** Two hobby extractors (`lean4-prod`, pinned to Lean 4.32.1, with a documented semantic divergence on
`Nat % 0`; `lustc`, one star). No pinned identity worth declaring. **A verified Rust compiler** does not exist;
RustCompCert (2026.02) is an in-progress CompCert-based prototype for a sequential subset without generics, traits or
closures; rustc 1.96.1, 1.97.1 and 1.98.1 each fixed a miscompilation. rustc stays a row in every option, the status
quo included. Sources: https://github.com/auser/lean4-prod/issues/56, https://arxiv.org/abs/2602.07455 (read 2026.11.04).

**What "stage 3: its compilation" should mean.** Four readings: (A) the Lean model compiled and run as the core, which
Cedar declined and which adds compiler rows; (B) Rust generated from the model, the Dafny shape, which adds a backend
row and drops the Lean row; (C) a verified extractor, which exists for Dafny to CakeML only; (D) the Rust compiled, by
Charon and Aeneas, into Lean, so the proved artifact is derived from the code that runs. Only (D) keeps the Lean kernel
as the sole prover row, and only (D) has an industrial instance at scale (SymCrypt). ADR-0033 should pin the reading
before any addendum claims a stage.

### 2.6 Testing-shaped links, and what each would add

None of these yields a machine-checked refinement; each shrinks the residual of T-0045-28 from "every untested path"
to a measured set, and none adds a row.

**(i) Generated inputs through the replays the tree already has.** `mechanism/lean/seats-replay.sh` runs six test
suites with `TOPAK_TRACE_DIR` set and passes every file to `mechanism/lean/SeatsReplay.lean`; `spec/mechanism-trace-run.sh`
does the same for TLC. Neither requires the traces to come from the suites. A property-based driver generating random
`apply` sequences arm by arm (the `proptest-state-machine` crate, 0.9.0 on 2026.10.10, or Bolero), recording them with
`trace.rs`, and feeding both replays is the corpus's declared stage 2 in Cedar's shape with no FFI, no compiled-Lean
oracle, no protobuf bridge and no new row: a false mismatch can only subtract. The Lean replay runs under the compiler,
as today; a kernel-checked replay of the minimised corpus by `decide` is the optional upgrade for the small step
functions. The first replay already found what the reading missed (ADR-0053 finding 7); generated inputs are how it
keeps finding it. Days to two weeks. **This does not make `SeatsModel` a stage**: ADR-0053 R4 withholds the label
because the oracle stands for most of `apply`, which is a scope rule; generated inputs plus modelling the remaining arms
is the path to lifting it.

**(ii) Cedar-style compiled oracle.** The same differential test with the Lean model compiled and called over FFI, as
Cedar does. It adds the Lean compiler, runtime and marshalling as silently trusted components of the oracle, which
Cedar's chain also trusts without declaring; a miscompiled oracle can agree with buggy Rust, so this is not
subtract-only. Option (i) gets the same evidence without them. Worth doing only if replay through `lean --run` becomes
too slow for the generated corpus.

**(iii) Model-based testing from `Mechanism.tla`.** The direction stage 1 does not cover: spec-allowed behaviours the
code refuses or diverges on. TLC can dump the state graph of `Mechanism.tla` at small constants and a generator can emit
one Rust test per behaviour, compared through a hand-written state mapping. The precedent is MongoDB's operational
transformation engine, about 1,000 lines like `State::apply`: 30,184 states, 4,913 behaviours, one test each, 100%
branch coverage against 21% for the hand-written tests, one real bug. The mapping is the abstraction function any later
refinement proof needs, so the work carries forward. Weeks. Quint would require re-encoding 24 modules and is a worse
fit than TLC's own graph; `tla-connect` (2026.02) drives Apalache from TLA+ directly but is early. Source:
https://www.mongodb.com/company/blog/engineering/conformance-checking-at-mongodb-testing-our-code-matches-our-tla-specs
(read 2026.11.04).

**(iv) Hardening stage 1.** Cirstea, Kuppe, Loillier and Merz state in print that trace validation checks compatibility
(S ∩ T ≠ ∅), "not refinement of the high-level specification by the trace", and can accept a trace that logs too
little. The marginal work here is a coverage count (`spec/mechanism-trace-run.sh` passes no `-coverage`, so how many of
`Mechanism.tla`'s action disjuncts the 82 traces exercise is not a number), a negative control (a deliberately perturbed
trace must fail, as the floor gates carry lying-solver controls), and logging enough of the state that TLC has nothing
to guess. Source: https://arxiv.org/html/2404.16075v2 (read 2026.11.04).

**(v) Mutation analysis of the chain.** The corpus already practises hand mutations (`mechanism/crates/topak-core/tests/mutations.rs`,
36 tests; the mutants in `mechanism/lean/README.md`). `cargo-mutants` (27.1.0, 2026.06.02) over `state.rs`, `admit.rs`,
`clock.rs` and `lift.rs`, with the TLC and Lean replays as the test, gives the surviving-mutant list: a direct,
quantitative statement of what the two hand models cannot see, and the negative control (iv) asks for. Hours of CPU,
no row, an artifact an addendum can cite.

**(vi) Cross-checking the two hand models, and `Mechanism.tla` against the modules.** `Mechanism.tla` and
`SeatsModel.lean` are independent hand models of the same Rust, each with its own READ premise, linked only by the 82
traces both replay. No module in `spec/` instantiates `Mechanism` (there is no `INSTANCE` anywhere in `spec/`), so
`Mechanism.tla` has never been checked to refine `Seats`, `Lease_A1` or `Coupling` at small constants; only
`spec/ConfinementRefinement.tla` reads invariants on trace states. Two additions on rows the corpus holds: TLC
refinement checks of `Mechanism.tla` against the discriminating modules through refinement mappings; and TLC's state
graph of `Mechanism.tla` as a behaviour generator fed to `SeatsReplay.lean`, so the two transcriptions are compared on
spec-allowed behaviour, not only on code-produced behaviour.

**(vii) The spec-side premise.** `spec/lean/README.md` says plainly that its theorems replace the LS4 premise with "a
different one added: that the Lean encoding is the TLA+ module". The graph check (`spec/lean/graph-check.sh`) discharges
that for `Seats` and `FloorComposition` by exhaustive comparison with TLC's state graph; ADR-0053 lists the other
encodings as an open obligation. A chain whose stage refines an encoding read by one person has a premise at both ends;
R1(b) already says so, and the finite-set modules can all be checked the same way.

---

## 3. What AWS does, and what Cedar does

**Cedar.** The Lean model (`cedar-spec/cedar-lean`, pinned to Lean v4.35.0 since 2026.10.20) carries the proofs:
authorizer properties, sound slicing, validator soundness, level-based slicing, the symbolic compiler's soundness and
completeness, and (SymCert, FMCAD 2026) five analyses. The Rust (`cedar-policy` 4.14.1, 2026.11.02) is never claimed
verified; parsers are not modelled at all. The link is differential random testing: the Lean model compiled to static
libraries and called from Rust through `cedar-lean-ffi` (protobuf in, JSON out); 18 differential and 23 property-based
targets plus about 26 for the symbolic compiler; daily runs on Amazon's container service at six hours per target,
"millions of inputs for most targets" (the 2024 figures; the corpus refreshes for 4.11 through 4.14.0 on 2026.10.19
show the pipeline alive). The durable, third-party-replayable artifact is the minimised corpus
(`cedar-integration-tests`), consumed by `cedar-go` daily. The production analysis service is the Rust crate
`cedar-policy-symcc` (0.8.1, 2026.11.02), whose core "maps directly to the Lean model"; SymCert states the Rust port
"now runs in production, while the original Lean implementation serves as a correctness oracle for daily differential
random testing". The 2024 paper considered compiling the Lean model to C for production and rejected it, and considered
Aeneas, Kani, Prusti, Creusot and Verus for the Rust and found them "not (yet) up to the task"; nothing public revises
either judgement, though one Kani harness lives in the Rust crate outside CI. Cedar moved from Dafny to Lean (RFC 0032,
accepted 2023.10.24) because meta-theory proofs fit Dafny's automation poorly, the executable Lean model was faster for
differential testing than the Rust, and the trusted base reduced to the kernel. What Cedar trusts silently in the
testing chain: the Lean compiler and runtime, the FFI and marshalling glue, generator coverage, and cvc5's UNSAT for
the analyses (no certificate; the corpus already declined that last one). Sources:
https://github.com/cedar-policy/cedar-spec/blob/main/cedar-lean/README.md,
https://raw.githubusercontent.com/cedar-policy/cedar-spec/main/cedar-drt/README.md,
https://www.amazon.science/publications/symcert-verifying-smt-based-policy-analyses,
https://arxiv.org/pdf/2407.01688, https://raw.githubusercontent.com/cedar-policy/rfcs/main/text/0032-port-formalization-to-lean.md
(read 2026.11.04).

**Two directional facts for TOPAK.** Cedar's model preceded the code, so its oracle is independent of the
implementation; `mechanism/lean` was transcribed from the code, so a differential test against it detects transcription
drift, not shared design error. The independent oracle in this corpus is `spec/lean`'s encodings, reached through the
refinement proofs, and `Mechanism.tla` through TLC. And T-0045-3 already rests on exactly Cedar's chain for
`cedar-policy` 4.13.0, so declaring the compiler and FFI rows for a TOPAK oracle would make explicit a trust the corpus
carries implicitly today.

**The Nitro Isolation Engine** (whitepaper published 2026.06; ITP 2026 invited paper; about 330,000 lines of
Isabelle/HOL). The Rust hypercalls are written in a subset avoiding traits and dynamic dispatch and transcribed by hand
into µRust, a shallow embedding (`awslabs/autocorrode`): "the translation from Rust to µRust is manual and translation
errors could change the meaning of the code. Conformance testing is our primary mitigation and ongoing work to automate
the translation will further close the gap." Traces of the compiled binary on real hardware are replayed on an
executable reference model extracted from the Isabelle model by code generation; "the Rust compiler and LLVM backend
are therefore in the trust boundary"; parts of the Rust and the Isabelle definitions are co-generated from one
machine-readable specification. The soundness statement is organised as Gap A (specification against requirements), Gap
B (model against the real system), Gap C (prover). Concurrency primitives were proved in Iris and Verus. This is the
corpus's current shape with better instrumentation and a taxonomy worth adopting verbatim. Sources:
https://d1.awsstatic.com/onedam/marketing-channels/website/aws/en_US/whitepapers/compliance/nitro-isolation-engine-whitepaper.pdf,
https://github.com/awslabs/autocorrode (read 2026.11.04).

**Kani in CI.** Firecracker (34 harnesses, 21 minutes, every pull request), s2n-quic (102 Bolero harnesses), the Rust
standard library campaign (16,748 generated harnesses; 10 of 29 challenges resolved, 7 by Kani; scope memory safety and
a subset of undefined behaviour; "has not uncovered any previously unknown memory safety vulnerabilities"). Bounded,
bug-finding, no refinement to a specification anywhere. Source: https://arxiv.org/html/2607.01504,
https://github.com/model-checking/verify-rust-std (read 2026.11.04).

**Dafny-compiled Rust in production**, §2.5; the IAM authorization engine rewritten in Dafny was shadow-tested against
production samples before deployment (ICSE 2025), compiled to Java; the Dafny toolchain is fuzzed (XDsmith, 31 bugs),
not certified.

**S3.** ShardStore (SOSP 2021): "property-based testing to check that implementation code refines the reference
model", reference models about one percent of the implementation, tens of millions of random sequences before each
deployment, Shuttle and Loom for concurrency, Crux for bounded panic-freedom of deserialisers. OSDI 2026 "High Fidelity
Models for Large Scale Stateful Services": reference models used in a model-based-testing style as "de facto
specifications of S3", running continuously in CI/CD. Neither proves the implementation. Sources:
https://jamesbornholt.com/papers/shardstore-sosp21.pdf, https://www.usenix.org/conference/osdi26/presentation/jaber.

**P and PObserve.** P specifications model-checked; PObserve validates post hoc that structured logs "match behaviors
allowed by the formal P specification". Desai's FMCAD 2025 abstract states the position: "formal specifications as
oracles or monitors that provide the correct answers for many of AWS's testing practices". No evidence was found of
AWS using TLA+ trace validation; its runtime validation is PObserve against P. Source:
https://p-org.github.io/P/advanced/pobserve/pobserve/ (read 2026.11.04).

**The sum.** AWS writes and proves models, tests the shipped code against them, declares the compiler and the
transcription as gaps, and mitigates by conformance testing and fuzzing. Its one effort proving Rust in a theorem
prover transcribes by hand and replays traces. Its one Rust-dialect verifier in production use is declared trusted.
The question "what does AWS use to prove its Rust refines its spec" has the answer "nothing; it tests, and says so".

---

## 4. The options compared

| Option | Proved of | Removes | Adds to the trusted base | Checkable by a pinned checker | Fit | Effort | Verdict |
|---|---|---|---|---|---|---|---|
| Generated-input differential replay through the existing TLC and Lean replays (§2.6 i) | Nothing proved; agreement observed | Nothing; measures the READ premise | Nothing (failure subtracts) | The corpus of generated traces, replayable | Immediate | Days to two weeks | Do first |
| Mutation analysis with the replays as the test (§2.6 v) | Nothing proved; a score | Nothing | Nothing | The surviving-mutant list | Immediate | Hours of CPU | Do first |
| `Mechanism.tla` against the modules; the two hand models against each other; graph checks for the other encodings (§2.6 vi, vii) | TLC results at small constants | Part of two READ premises | Nothing (TLC and Lean are rows) | TLC output; Lean terms | Immediate | Weeks | Do next |
| Aeneas pilot on `admit.rs`, `clock.rs`, `lift.rs` (§2.3) | Lean theorems over generated definitions | The code-side READ premise for those files, once generated equals hand | Charon and Aeneas as a pinned translator row, when promoted | Lean terms, replayed | Refactor-free for those files | Days | Start as a pilot |
| Aeneas on `State::apply` | As above, for the arms | The READ premise behind `SeatsModel` and `CouplingModel` | Translator row; hand models of `BTreeMap`/`BTreeSet` | Lean terms | Refactor: `dyn Fn`, labelled break, `&mut` captures, map shapes | Weeks to months | After the pilot |
| Kani as a tester (§2.2) | Real MIR, bounded; unbounded for the loop-free files | Nothing | Nothing if no theorem is claimed | Counterexamples as concrete tests; DRAT for the SAT step only | Stubs for Cedar, signatures, hashing | One to six weeks | Optional amplifier |
| Verus (§2.1) | A rewritten dialect against a Verus spec | The code-side READ premise, for the dialect | Verus, Z3 4.16.0, `vstd`: uncertified; a spec-side READ premise | None in pipeline; `-V cvc5` plus CPC unproven | Rewrite; serde and `dyn` edges | Months | Only under a changed policy |
| Creusot, Prusti, Flux (§2.4) | Real MIR with contracts | Nothing without a spec encoding in Pearlite | Translator rows plus uncertified solvers; no `BTreeMap` specs | None by default | Partial | Months | Reject |
| RefinedRust, Corten, rocq-of-rust, Foundational VeriFast, AutoCorrode (§2.4) | Real MIR or a hand model, foundational | The READ premise, in a second kernel | A second prover kernel and a translator | Rocq or Isabelle kernel | No `dyn`; person-years | Person-years | Reject with reasons |
| Dafny to Rust; compiled Lean as the core; Lean to Rust (§2.5) | A model, with its compilation trusted | The transcription premise | Compiler or backend rows whose failure adds; for Dafny also Boogie and Z3 | None | Cedar declined the first two | Months | Reject; reread "stage 3" as the Rust-to-Lean direction |

---

## 5. Premises the survey exposed in the tree

1. **The Lean pin.** `tools/LEAN-PIN` and the three `lean-toolchain` files name v4.33.1 (2026.08.21). Lean v4.34.0
   (2026.09.14) made `is_def_eq` caching order-independent (#14806), made the kernel's `is_prop` require a sort after a
   proof-irrelevance guard was skipped on projections (#14807, #14843), prevented a reference-count overflow the notes
   say "could be turned into a use-after-free in the official kernel" (#14838), and requires GMP 6.3.0 or newer because
   earlier versions "can cause Lean to produce unsound (i.e., incorrect) results in corner cases". The notes say the
   #14807 proof "was also accepted by `nanoda`"; `leanchecker` is derived from the same C++ kernel. v4.35.0 (2026.10.12)
   adds `lake check` and `lake check --paranoid`, which replays an export through `leanchecker-paranoid`, `lean4lean`,
   `nanoda` and `con-leche` (a kernel written in Lean with a kernel-checked consistency theorem relative to a
   set-theoretic model; the notes are inconsistent on whether `con-ron` runs too). `con-leche` accepts only the three
   standard axioms: `floor/lean/TopakFloor/InForce.lean` and `floor/lean/TopakFloor/Gates.lean` use `native_decide`
   (six files in `floor/lean`, none in `spec/lean` or `mechanism/lean`), so the floor package would be refused as it
   stands, the other two replayed. Re-pinning is the precondition of every Lean item above, and `lake check --paranoid`
   is the natural successor to `leanchecker --fresh` in `tools/lean-report.sh`; lean4lean's own verification is still
   "expected in the next few months" (de Moura's post "Lean Now Ships with Verified Kernels", 2026.10.15). Sources:
   https://lean-lang.org/doc/reference/latest/releases/v4.34.0/,
   https://lean-lang.org/doc/reference/latest/releases/v4.35.0/, https://github.com/digama0/lean4lean,
   https://github.com/leanprover/con-leche (read 2026.11.04).
2. **Overflow semantics.** No `[profile.release]` in `mechanism/Cargo.toml`: release builds wrap. Aeneas (and Kani
   by default) check overflow as a failure. Either the release profile sets `overflow-checks = true`, or the records say
   the verified semantics is the debug build's. `clock.rs` saturates explicitly; the rest of `state.rs` does not say.
3. **Signature semantics.** `authentic.rs` calls `verify`; `ed25519-dalek` documents `verify_strict` as rejecting
   small-torsion components and weak keys and "technically non-RFC8032 compliant", and point decoding under ZIP-215
   rules. For a replicated state machine whose `sigOk` and `signOnOk` are trusted trace inputs to `Mechanism.tla`, which
   semantics is the specification is a premise to state, not a crate default to inherit. `curve25519-dalek` 4.1.3 offers
   a `fiat` backend (fiat-crypto, field arithmetic with Rocq-checked proofs) by a build flag; it shrinks an existing row
   for free. Sources: https://docs.rs/ed25519-dalek/latest/ed25519_dalek/struct.VerifyingKey.html,
   https://raw.githubusercontent.com/dalek-cryptography/curve25519-dalek/main/curve25519-dalek/README.md (read 2026.11.04).
4. **The node's call site.** Every option above verifies `topak-core`. The admit path's safety also rests on
   `floor_gate` and `compose` being the only decision path in `mechanism/crates/topak-node/src/mechanism.rs` (today
   `callSite_eq_compose`, a hand transcription of seven lines), and on the trusted trace inputs (`ok`, `sigOk`,
   `signOnOk`, `proofOk`, `approvers`) being computed where the model assumes and the same on every replica. Moon and
   Varshney name this "effect exclusivity" and list it in their trusted base; it belongs in Annex B as a premise, and a
   Kani or property harness on the call site is its cheap check.
5. **"Stage 2 not begun" is a rule, not a fact.** `SeatsReplay.lean` already differentially tests a Lean model against
   the code on recorded inputs. What is missing is generated inputs and the arms outside the two models; ADR-0053 R4
   withholds the word "stage" by scope. The records should say so, so that the next addendum is about scope and inputs
   rather than about a stage that does not exist.

---

## 6. A recommended order

0. Re-pin Lean to v4.35.0 and adopt `lake check --paranoid` as T-0045-37's replay; decide what to do about
   `native_decide` in `floor/lean` (prove the closed evaluations another way, already an ADR-0053 open item). Days.
1. Generated-input differential replay through both existing replays, with `cargo-mutants` over the core and a TLC
   action-coverage count, and the perturbed-trace negative control. Days to two weeks; no row; produces the corpus of
   traces, the mutation score and the coverage figure an addendum can cite.
2. The intra-spec checks: `Mechanism.tla` against `Seats`, `Lease_A1` and `Coupling` by refinement mapping at small
   constants; TLC-generated behaviours replayed through `SeatsModel.lean`; graph checks for the remaining finite-set
   encodings. Weeks; no row.
3. The Aeneas pilot on `admit.rs`, `clock.rs` and `lift.rs` as a non-trusted oracle: generated Lean proved equal to the
   hand transcriptions, the 82 traces replayed through both. Then the refactor and the `BTreeMap`/`BTreeSet` models
   for `State::apply`, and only then a decision on declaring Charon and Aeneas a row. Days, then months.
4. Kani harnesses filed as testing: unbounded equivalence for `compose`, `floor_gate` and the clock check against a
   Rust transcription of the Lean; bounded per-arm differential harnesses for `apply`; optionally DRAT for the SAT
   step. One to six weeks.
5. Declare the premises of §5: overflow semantics, signature semantics (and the `fiat` backend), the call-site
   exclusivity premise, the rustc-as-semantics row, and the reading of "stage 3".
6. Record Verus, Dafny-to-Rust, compiled Lean as the core, Creusot and the foundational Rocq tools as considered and
   not taken, with the reasons in §2, so that the next reviewer finds them answered.

---

## 7. Sources read

Repository: `decisions/ADR-0033.md`, `decisions/ADR-0045.md`, `decisions/ADR-0046.md`, `decisions/ADR-0053.md`,
`decisions/ADR-0030.md`, `mechanism/lean/README.md`, `mechanism/lean/seats-replay.sh`, `mechanism/lean/SeatsReplay.lean`,
`spec/Mechanism.tla`, `spec/ConfinementRefinement.tla`, `spec/mechanism-trace-run.sh`, `spec/lean/README.md`,
`spec/proof-method.md`, `tools/LEAN-PIN`, `tools/lean-report.sh`, `mechanism/Cargo.toml`,
`mechanism/crates/topak-core/src/admit.rs`, `mechanism/crates/topak-core/src/state.rs`,
`mechanism/crates/topak-core/src/clock.rs`, `mechanism/crates/topak-core/src/authentic.rs`,
`mechanism/crates/topak-core/src/workflow.rs`, `mechanism/crates/topak-core/src/trace.rs`,
`mechanism/crates/topak-core/tests/mutations.rs`, `mechanism/GAPS-AND-ASSUMPTIONS.md`, `narrative/theory-of-operation.md`,
`checkpoints/topak-genesis-checkpoint-G11-2026.10.09.md`, `derived/topak-lean-formalization-options-2026.10.05.md`.

External, in addition to the URLs inline (all read 2026.11.04): Verus, "Verifying Rust Programs using Linear Ghost
Types", OOPSLA 2023, https://arxiv.org/pdf/2303.05491; Verus SOSP 2024,
https://www.research-collection.ethz.ch/server/api/core/bitstreams/b6c5b30f-8192-476a-8dc2-a99fb45d448f/content;
Kani ICSE-SEIP 2022, https://cs.wellesley.edu/~avh/dyn-trait-icse-seip-2022-preprint.pdf; Charon CAV 2025,
https://arxiv.org/abs/2410.18042; Aeneas ICFP 2022, https://arxiv.org/abs/2206.07185; cvc5 NEWS,
https://raw.githubusercontent.com/cvc5/cvc5/main/NEWS.md; ethos, https://github.com/cvc5/ethos; Logos,
https://github.com/cvc5/logos; Z3 release notes, https://raw.githubusercontent.com/Z3Prover/z3/master/RELEASE_NOTES.md;
Lean 4.22.0 and 4.30.0 release notes, https://lean-lang.org/doc/reference/latest/releases/v4.22.0/ and
https://lean-lang.org/doc/reference/latest/releases/v4.30.0/; lean4lean, https://github.com/digama0/lean4lean;
con-leche, https://github.com/leanprover/con-leche; the AWS Open Source Blog on Cedar and Lean,
https://aws.amazon.com/blogs/opensource/lean-into-verified-software-development/; Cedar Analysis,
https://aws.amazon.com/blogs/opensource/introducing-cedar-analysis-open-source-tools-for-verifying-authorization-policies/;
cedar-policy-symcc, https://crates.io/api/v1/crates/cedar-policy-symcc; the AWS Compute Blog on the Nitro Isolation
Engine, https://aws.amazon.com/blogs/compute/aws-nitro-isolation-engine-formally-verifying-the-hypervisor-in-the-aws-nitro-system/;
Systems Correctness Practices at AWS (FMCAD 2025 abstract), https://repositum.tuwien.at/handle/20.500.12708/219530;
Khan, https://arxiv.org/abs/2606.17182; Moon and Varshney, https://arxiv.org/html/2605.09045; MAREF,
https://dev.to/maref/how-to-formally-verify-an-agent-governance-framework-with-tla-4ei0; TraceLink (OOPSLA 2025),
https://www.cs.ubc.ca/~bestchai/papers/oopsla25-trace-link.pdf; OmniLink, https://arxiv.org/abs/2601.11836; Quint
model-based testing, https://quint.sh/docs/model-based-testing; CCF trace validation, https://arxiv.org/html/2406.17455v2;
RefinedRust 2, https://doi.org/10.1145/3839484; Corten, https://arxiv.org/abs/2609.04372; Foundational VeriFast,
https://arxiv.org/abs/2601.13727; Crux, https://arxiv.org/html/2410.18280v1; KMIR, https://github.com/runtimeverification/mir-semantics;
rocq-of-rust, https://github.com/formal-land/coq-of-rust; proptest-state-machine, https://crates.io/api/v1/crates/proptest-state-machine;
cargo-mutants, https://crates.io/api/v1/crates/cargo-mutants.

**Caveat on negatives.** Several verifiers reported the shared web-search budget exhausted and rested their
"nothing newer" findings on the projects' own repositories, release pages and papers. Negative-existence claims
(no TLA+-to-Rust compiler; no Rust verifier routing proofs to cvc5; no AWS use of Aeneas) are therefore well
supported for the named projects and not exhaustive across the web.
