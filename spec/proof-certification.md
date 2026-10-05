# TLAPS proof certification

**2026.10.04** · the method behind `spec/proof-cert.sh`, `spec/smt-checked` and the
`spec/*-proof-cert-results-<date>.txt` files · DRAFT · companion to `spec/proof-method.md`, which says how the proofs
are written; this says how a proved obligation is checked by something other than the solver that proved it

**What this is.** A proof module checked by the TLA+ Proof System ends with "All N obligations proved". That line is
the word of whichever backend discharged each obligation. This document describes a second run of the same proof in
which that word is not taken: every obligation an SMT solver discharges must come with a proof that an independent
checker accepts, every proof Zenon finds must be re-checked by Isabelle, and a results file accounts for every
obligation by the route that discharged it. It is the method the floor's gates have used since Batch 24
(ADR-0030 §5 A1; `floor/cvc5-checked`), applied to proofs.

**What this is not.** A record: nothing here is ratified. ADR-0046's pending amendment A1 is where the corpus would
adopt it. It is also not a claim that a certified module's theorems hold of anything that runs (T-0045-28), nor that
every step of a certified proof is checked: §8 lists what stays trusted, and it is not nothing.

---

## 1. Why a second run is needed

An ordinary run (`proof-results.sh`) hands each obligation to the prover's backends in turn and stops at the first
that answers.

| Backend | What it returns | Who checks the answer |
|---|---|---|
| tlapm itself | "trivial": the obligation is closed by normalization, with no backend | Nobody |
| Z3 (the default SMT solver) | `unsat` | Nobody. Z3 4.8.9 emits no proof the prover reads |
| Zenon | A proof script in Isabelle's language | Nobody, unless asked (`-C`) |
| Isabelle | A proof, checked by Isabelle's kernel as it is made | Isabelle |
| LS4 | `unsat`, for a step of temporal logic | Nobody |

In the sixteen proof modules that existed on 2026.10.04, about a third of all obligations were SMT's, so a third of
every "proved" was Z3's unsupported word.

**The prover's own check does not cover this.** `tlapm -C` is described as checking proofs in Isabelle, and ADR-0046
as ratified says it "can hand every SMT-proved obligation to Isabelle". It cannot. `-C` checks the scripts Zenon
emits and nothing else. For a module whose obligations are all SMT's, `-C` gives Isabelle a theory with no lemmas in
it, and Isabelle reports "No errors found". That was verified by reading the generated theory for
`RunConfinement_proof`: fourteen lines, no lemma. ADR-0046 E2 (pending) corrects the sentence.

---

## 2. The method

Run the proof again with three changes.

1. **Z3 is replaced** by `spec/smt-checked`, a wrapper that runs cvc5 with proof production and forwards `unsat` only
   when the ethos checker has accepted a proof of false from the query (§3). Z3 is not run at all.
2. **Zenon's proofs are checked** by Isabelle (`-C`).
3. **Every obligation is accounted for** by route, and the run is refused as a whole if any obligation is unproved,
   if an SMT-proved obligation has no accepted proof behind it, or if Isabelle does not confirm a Zenon proof (§4).

| Route | Checked by | Counts toward certification |
|---|---|---|
| Trivial (tlapm) | Nothing beyond tlapm | Yes, on trust in tlapm (§8) |
| SMT: cvc5, with a proof ethos accepted | ethos, against the CPC signature | Yes |
| Zenon, with Isabelle's confirmation | Isabelle | Yes |
| Isabelle | Isabelle | Yes |
| LS4 | Nothing | Yes, **and reported separately as not certified** |
| Anything else: failed, or SMT with no accepted proof, or a Zenon proof Isabelle refused or could not check | — | **No: the module is not certified** |

**A module is certified** when every obligation is on one of the first five rows. The results file always says how
many are on the LS4 row, in the sentence that ends it.

---

## 3. The checked SMT route: `spec/smt-checked`

The prover writes one SMT-LIB file for each obligation it sends to SMT: one sort, function declarations, the
hypotheses and the negated goal as named assertions (some with instantiation patterns), and `(check-sat)`. It runs
the configured solver on the file and reads one word back. `tlapm --solver` sets that solver; the driver sets it to
the wrapper.

For each file the wrapper does five things.

1. **Keeps the query**, under the digest of its text.
2. **Runs cvc5** on the file as written, adding only the flags that make it produce and print a proof in the CPC
   format (`--produce-proofs --dump-proofs --proof-format-mode=cpc --proof-granularity=dsl-rewrite`).
3. **Discards what the proof restates and substitutes the query's own.** cvc5's proof begins by restating the
   declarations. The wrapper drops those lines and writes declarations derived from the query text in their place.
   If the solver had proved something about different symbols, the proof would no longer type-check.
4. **Requires every assumption of the proof to be an assertion of the query.** Each `assume` step in the proof names
   a formula. The wrapper expands cvc5's abbreviations in it and compares the result, structurally, with the query's
   assertions. A proof that assumes anything the query did not assert is refused.
5. **Runs ethos** on the result with `--require-proof-of-false`, against the CPC signature in `tools/cpc/`.

Only if ethos answers `correct` does the wrapper print `unsat`. In every other case, including any error of its own,
it prints `unknown`, which the prover reads as "this backend did not prove it" and passes the obligation on to Zenon
and then Isabelle.

**The comparison in step 4** has to see through two changes of notation that cvc5 makes between reading a formula and
printing it in a proof. Both are made explicit so that a reader can judge them.

| In the query | In the proof | Why the two are the same formula |
|---|---|---|
| `(! φ :named N)`, `(! φ :pattern (…))` | `φ` | A name is a label. A pattern is a hint to the solver about when to instantiate a quantifier, and is no part of what the formula says |
| `(forall ((x S)) φ)`, with `x` in `φ` | `(forall (@list (@var "x" S)) φ′)`, with `(@var "x" S)` where `x` was | The proof format's way of writing a bound variable. The wrapper rewrites the query into this form, scope by scope, and compares exactly |

The rewriting goes from the query to the proof's notation and not the other way, so that a bound variable and a
declared constant of the same name can never be confused.

**What the wrapper refuses.** A query with a form it does not carry into a proof (anything but `set-logic`,
`set-option`, `set-info`, `declare-sort`, `declare-fun`, `declare-const`, `assert`, `check-sat`, `exit`); a `let`;
a binder of a shape it does not read; a proof with a form other than a term abbreviation, `assume`, `assume-push`,
`step` or `step-pop`; a proof that assumes nothing. Each refusal is recorded with its reason. `assume-push` introduces
a local hypothesis inside the proof and is not an assumption about the query, so it is not compared.

**What it writes.** For each query: the query (`q-<digest>.smt2`), the proof as checked (`q-<digest>.cpc`), and a
verdict (`q-<digest>.json`) with the digests of the query, the proof, the solver and the checker, the solver's
answer, what was forwarded and why. And one line in `calls.log` for each call, since two obligations with the same
query share the three files.

**A solver's `sat` or `unknown` needs no certificate.** It can only send the obligation to another backend or fail
the proof.

---

## 4. The driver: `spec/proof-cert.sh`

```
cd spec
./proof-cert.sh <Module>_proof > <Module>-proof-cert-results-<date>.txt
```

It runs `tlapm -C --cleanfp --strict --toolbox 0 0 --solver '<smt-checked> "$file"'` on the module and then reads
two things: the prover's per-obligation messages, which name the backend that discharged each one, and the wrapper's
verdicts.

- **`--cleanfp`** discards the prover's fingerprint cache, so no result is carried over from an earlier run, an
  uncertified one least of all.
- **Within the run** the prover does reuse a result for an obligation identical to one it has just proved. The
  driver counts those separately: SMT-proved obligations, less the ones reused, must not exceed the calls the
  wrapper forwarded on an accepted proof.
- **Exit status** is non-zero unless the module is certified.
- **`STRETCH=n`** multiplies the prover's backend timeouts (default 1). The results file states the value used.
- **The evidence** goes to a temporary directory and is removed, unless a directory is given as the second
  argument. The results file carries a digest of it: the hash of the sorted list of (query digest, proof digest)
  pairs for the accepted proofs. Rerunning reproduces it. The evidence is not tracked (the custodian's decision,
  2026.10.04); it is about 30 KB an obligation.
- **`CVC5=` and `ETHOS=`** override the solver and checker paths, which default to the ones the floor's gates use
  under `tools/`.

---

## 5. Reading a results file

```
TOPAK — TLAPS certified proof results for ToolList.tla: every obligation of ToolList_proof.tla, by the route that discharged it
Modules: ToolList.tla (sha256 7c0a18b897e6cb98) · ToolList_proof.tla (sha256 c6b7ac1be332dfd6)
Prover: tlapm 7824dab (binary sha256 e150fb793fb28592) · zenon version 0.8.4 … · Isabelle2025 · LS4 for PTL · driver: proof-cert.sh
Checked SMT route: smt-checked (sha256 …) · cvc5 1.4.0 … (sha256 …) · ethos (sha256 …) · CPC signature (sha256 … over its .eo files)
An obligation proved by SMT counts only with a proof of false, … that ethos accepted. Z3 is not run. Backend timeouts x1.

Obligations: 215
  trivial, closed by tlapm with no backend            133
  SMT, proof accepted by ethos                        75   (75 calls forwarded on an accepted proof; 0 obligations identical …; evidence digest 120e08ded88bad4a)
  Zenon, proof checked by Isabelle                    0
  Isabelle                                            0
  LS4, temporal step, NOT certified                   7

All 215 obligations proved. 208 of them rest on tlapm's own normalization or on a checked proof; 7 rest on LS4, whose answer no checker confirms.
```

| Line | What it fixes |
|---|---|
| Modules | Exactly which text was proved: every module in the `EXTENDS` chain, by digest |
| Prover | The prover binary and its other backends, as `proof-results.sh` prints them |
| Checked SMT route | The wrapper, the solver, the checker and the signature it checks against, each by digest. A change to any of them is a different certification |
| Obligations | Every obligation, on exactly one row |
| The last line | `All N obligations proved…` for a certified module; `NOT CERTIFIED: …` with the reason otherwise |

A results file is dated and is never edited. A module or proof that changes gets a new run.

---

## 6. Reproducing a result

Prerequisites, all under `tools/`: the prover (`tools/install-tlaps.sh`, pinned by `tools/TLAPS-PIN`); cvc5 1.4.0
(`tools/cvc5-macOS-arm64-static/`); ethos (`tools/install-ethos.sh`, into `tools/ethos-8dc85c4/`); the CPC signature
(`tools/cpc/`, tracked).

```
cd spec
./proof-cert.sh Anchor_proof | cmp - Anchor-proof-cert-results-2026.10.04.txt
```

**The run is deterministic.** On 2026.10.04 the eleven certified results that ADR-0046 A1 cites were regenerated and
each was byte-identical to the file on record, evidence digest included. A difference in any line is a difference in
the module, the proof, the prover, the solver, the checker, the signature or the wrapper, and the header says which.

---

## 7. Testing the wrapper: `spec/smt-checked-selftest.sh`

The wrapper is the one new piece of code the method trusts, so it has a test that tries to make it accept what it
should not. Given any query file the prover wrote (`tlapm --debug tempfiles` keeps them), it runs the wrapper
against four stand-in solvers.

| Stand-in | What it does | The wrapper must | Reason it gives |
|---|---|---|---|
| honest | Runs cvc5 | Forward `unsat` | checker accepted the proof |
| other | Proves the query with `(assert false)` added | Forward `unknown` | an `assume` is not one of the query's assertions |
| empty | Says `unsat` and prints an empty proof | Forward `unknown` | proof assumes nothing |
| cut | Prints an honest proof with its last step removed | Forward `unknown` | checker refused: the last step did not prove false |

All four behave as required. The second is the case the binding in §3 exists for; the fourth shows the checker is
doing work and is not a formality.

---

## 8. What is checked, and what is still trusted

| Trusted before | After certification |
|---|---|
| The SMT solver's soundness | **No longer trusted.** Its answer counts only with a proof the checker accepted |
| Zenon's soundness | **No longer trusted.** Its script is checked by Isabelle |
| — | **The checker, its signature and the wrapper** are trusted in the solver's place. These are the floor's T-0045-14, and the wrapper has the test of §7 |
| Isabelle | Still trusted, for its own proofs and for checking Zenon's |
| **LS4** | **Still trusted.** One to three obligations per theorem: the step that turns "the invariant holds initially and every step keeps it" into "it holds always". No checker confirms it |
| **tlapm's translation** of an obligation into an SMT query | **Still trusted**, as `cedar symcc`'s encoding of a policy question is for the floor. The checker certifies that the query is unsatisfiable. That the query says what the obligation says is the prover's |
| **tlapm's normalization** | **Still trusted.** About two obligations in three are closed by it with no backend |
| The prover's expansion of definitions, of `ENABLED`, and of primes | Still trusted; part of the translation |

So certification removes the largest unexamined premise, the SMT solver, and leaves three: the prover's front end,
its temporal backend, and the checker.

---

## 9. Results, 2026.10.04

Twenty proof modules, 5,084 obligations.

| Route | Obligations |
|---|---|
| Trivial | 3,330 |
| SMT, proof accepted by ethos | 1,621 |
| Zenon, checked by Isabelle | 10 (9 accepted, 1 refused) |
| Isabelle | 2 |
| LS4, not certified | 115 |
| Failed under the checked backends | 6 |

**Seventeen certify:** Anchor, BreakGlass, Correlator, Coupling, Emergency, FloorComposition, FloorRouting, Labels,
Lease_A1, NonComposition, Observers, Operators, RunConfinement, RunCoupling, RunSeats, Seats, ToolList.

**Three do not.**

| Module | Why | What it would take |
|---|---|---|
| `RulesFloorNV_rev5_proof` | Five obligations are Zenon's, under Z3 as under cvc5, and Isabelle refuses the script for one. The 10.02 results never ran the check | Smaller steps for those cases, so that SMT proves them or Zenon's script reconstructs |
| `Confinement_proof` | Three obligations, large type-invariant steps, are proved by Z3 and by nothing else: cvc5 does not prove them at ten times the timeout or under five instantiation strategies | The steps split, in a successor module |
| `Confinement_A1_proof` | The same three | The same |

A refused script and an unproved obligation are missing checks. Neither is a counterexample, and the uncertified
results for these three stand as they did. All three are cited by digest in accepted records, so restructuring them
means successor modules; the custodian deferred that on 2026.10.04.

---

## 10. Writing proofs that certify

What the first twenty modules taught.

- **Most proofs certify unchanged.** Thirteen of the sixteen that existed when the method was first run did, at the
  default timeouts. cvc5 proves what Z3 proved in the great majority of steps.
- **cvc5 is weaker than Z3 on very large single steps.** The three failures in `Confinement` are steps that expand a
  type invariant with many record fields in one `BY`. Splitting such a step by field, or by action, is the remedy.
- **Name the parts of a large action.** `Labels_proof` states one lemma on the shapes a step can have, with the
  action's `LET` named part by part, and proves each invariant from the shape. All 216 of its SMT obligations
  certified at the default timeout.
- **Give the case split explicitly** when an obligation quantifies over a set that has just grown: "an old member, or
  the new one". Both failures met while writing `Labels_proof` and `Emergency_proof` were of this kind, and each was
  a real gap in the argument and not the solver's weakness.
- **An `ENABLED` goal may go to Zenon**, and Zenon's script for it may not reconstruct. `Operators_proof` has two
  that Isabelle accepted. `Emergency_proof` had one, a lemma no theorem used, that Isabelle could not check; it was
  removed and its fact left to a TLC witness. A lemma that cannot be certified should not sit in a certified module.
- **A longer timeout rarely helps.** `STRETCH=10` recovered one obligation in `Confinement` and none elsewhere.
- **Run `proof-results.sh` first.** It is faster and finds real proof failures; then `proof-cert.sh`.

---

## 11. Where this sits in the records

| Record | Relation |
|---|---|
| ADR-0030 §5 A1 (Accepted, Batch 24) | The precedent: a routing verdict counts only with a checked proof. `floor/cvc5-checked` is the wrapper this one follows |
| ADR-0045 T-0045-14 | The checker, its signature and the wrapper as a trust root. Certified proofs rest on the same checker |
| ADR-0045 T-0045-31; ADR-0046 §3 | The prover as a trust root. Its residual names "the SMT backends' soundness" |
| **ADR-0046 E2** (pending) | Corrects the sentence on what `-C` checks (§1) |
| **ADR-0046 A1** (pending) | Gives T-0045-31 a certified configuration and lists which modules are in it. Its ratification condition, the regeneration of §6 and the test of §7, was run on 2026.10.04 and met |
| G9 open item 74 | "The SMT backends' proofs checked by Isabelle": answered by a different checker than it names |
| ADR-0047, 0048, 0050, 0052 (Proposed) | Each cites its module's certified results file by digest in its ratification condition |

---

## 12. Open

- **LS4.** No route checks a temporal step. The steps are few and of one shape, and a small fixed lemma library
  proved once in Isabelle could replace them.
- **The translation.** Nothing here examines how the prover turns an obligation into a query.
- **One solver, one version.** cvc5 1.4.0 is pinned by digest because the floor pins it. A newer cvc5 may prove the
  six obligations that fail, and would be a different certification.
- **The three modules that do not certify** (§9).
- **The evidence is not kept.** A digest and a deterministic rerun stand in for it.
- **This document is the drafter's**, as the wrapper, the driver and seventeen of the twenty results are.
