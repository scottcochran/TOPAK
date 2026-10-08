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

**What this is not.** A record. ADR-0046 A1, ratified 2026.10.04 in Batch 28, is where the corpus adopts the method;
this document describes it and is itself a draft. It is also not a claim that a certified module's theorems hold of anything that runs (T-0045-28), nor that
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
`RunConfinement_proof`: fourteen lines, no lemma. ADR-0046 E2 corrects the sentence.

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
  pairs for the accepted proofs. Rerunning reproduces it, save where tlapm reuses results, which can give another
  (§6). The evidence is not tracked (the custodian's decision, 2026.10.04); it is about 30 KB an obligation.
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
| Prover | The prover binary and its other backends, as `proof-results.sh` prints them; the driver is named, without a digest |
| Checked SMT route | The wrapper, the solver, the checker and the signature it checks against, each by digest. A change to any of them is a different certification |
| Obligations | Every obligation, on exactly one row. Where Isabelle refuses Zenon's proofs, `ISABELLE REJECTED n` counts the refusals tlapm reports, and tlapm reports only the first Isabelle prints: Isabelle's own log can show more (2026.10.08) |
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

**The run is deterministic, but for two things.** On 2026.10.04 the eleven certified results that ADR-0046 A1 cites
were regenerated and each was byte-identical to the file on record, evidence digest included. A difference in any
line is a difference in the module, the proof, the prover, the solver, the checker, the signature or the wrapper,
and the header says which, or in the driver, which the header names without a digest, with two exceptions. The
first, found on 2026.10.07: tlapm finds some obligations identical before it names any term, as it does two that
differ only in the names of their `NEW` constants or bound variables. It always sends the first of them, and reuses
its result for a later one only if the first is already proved when it comes to it; otherwise it sends that one too.
On one thread, as `proof-scan.sh` runs, every later one is reused; on several, as `proof-cert.sh` runs, how many are
reused, and which, depends on scheduling. A query carries the line it was generated from, so the split between calls
and reuse, and with it the evidence digest, can differ between runs, while the route counts do not, where no result
rests on a name (§8). `Labels_proof`, whose file records 211 calls and 5 reused, gave 214 and 2, and 212 and 4, in
two reruns; the eleven of ADR-0046 A1 regenerate byte for byte. The second, found on 2026.10.08: in
`RulesFloorNV_rev5_proof`, which does not certify, Isabelle refuses all five of Zenon's proofs, and tlapm reports
only the first refusal Isabelle prints, so which one a run names varies, on one thread too: the proof at line 126 in
the file on record, at line 124 in one run of `proof-scan.sh` and at line 122 in the next; `proof-scan.sh` reads
tlapm's trace of Isabelle's check, and marks all five in every run.

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
| **LS4** | **Still trusted.** One to three obligations per theorem: the step that turns "the invariant holds initially and every step keeps it" into "it holds always". No checker confirms it. For fifteen of the proof modules a second derivation, in Lean, does that step as a kernel-checked induction (`proof-method.md` §5b; ADR-0053); it does not change what this run certifies. Its input is the prover's translation, and has the second case below |
| **tlapm's translation** of an obligation into an SMT query | **Still trusted**, as `cedar symcc`'s encoding of a policy question is for the floor. The checker certifies that the query is unsatisfiable. That the query says what the obligation says is the prover's. It has two known unsound cases, below |
| **tlapm's normalization** | **Still trusted.** About two obligations in three are closed by it with no backend |
| The prover's expansion of definitions, of `ENABLED`, and of primes | Still trusted; part of the translation |

So certification removes the largest unexamined premise, the SMT solver, and leaves three: the prover's front end,
its temporal backend, and the checker.

**Two known unsound cases in the translation (2026.10.07).** In each the checker certifies a query that does not say
what the obligation says, and `proof-cert.sh` detects neither.

*The first: a term under a binder.* `tlapm` 7824dab hands SMT, Zenon and Isabelle, as an opaque constant, a term it
does not translate: an `ENABLED` or a `\cdot` (action composition) it has not expanded, or a temporal formula (`[]`,
`<>`, `~>`). That constant does not depend on any variable bound around the term, by `\A`, `\E` or a set
`{x \in S : ...}`, so the backend receives another obligation than the one stated, and a false statement can prove.
Before it abstracts, tlapm distributes `[]` over `/\` and `<>` over `\/`, and moves a `\A` at the head of a `[]`
body or of a conjunct of one, and an `\E` at the head of a `<>` body or of a disjunct of one, outward; so a closed
temporal formula whose body, once its definitions are expanded, has such a quantifier is the case too. The
abstraction is made before a backend sees the obligation, so SMT, Zenon checked by Isabelle, and Isabelle each accept
such a statement; LS4 does not. Over `Emergency_live.tla`:

| Statement | Proof | Certified by |
|---|---|---|
| `(\E t \in Tools : ENABLED EmAdmit(t)) => (\A t \in Tools : ENABLED EmAdmit(t))` | `OBVIOUS` | SMT: cvc5, proof accepted by ethos |
| the same | `BY Zenon`, in a module of its own | Zenon, its proof checked by Isabelle |
| the same | `BY Isa` | Isabelle |
| `(\E t \in Tools : <>(t \in em.envelope)) => (\A t \in Tools : <>(t \in em.envelope))` | `OBVIOUS` | SMT |
| `(\E t \in Tools : em.live ~> (t \in em.envelope)) => (\A t \in Tools : em.live ~> (t \in em.envelope))` | `OBVIOUS` | SMT |
| `(\E t \in Tools : EmAdmit(t) \cdot EmAdmit(t)) => (\A t \in Tools : EmAdmit(t) \cdot EmAdmit(t))` | `OBVIOUS` | SMT |
| `\A t \in Tools : SpecL => [](em.round > 0 => t \in em.envelope)`, from a lemma that proves it for `te` alone, `ASSUME NEW t \in {"te"} PROVE ...` | `BY` the lemma | SMT |
| `SpecL => []InvBig`, where `InvBig` says the envelope holds `te` and `t2`, from `SpecL => []InvSmall`, where `InvSmall` says it holds `te`: closed, but each body begins with `\A` | `BY` the second, `DEF InvSmall, InvBig` | SMT |
| `LB({"te", "t2"})`, from `LB({"te"})`, where `LB(S) == SpecL => [](\A t \in S : em.round > 0 => t \in em.envelope)`: the eighth through a definition with a parameter, expanded at constant arguments | `BY` the second, `DEF LB` | SMT |
| `SpecL => [](em.round >= 0 /\ \A t \in {"te", "t2"} : em.round > 0 => t \in em.envelope)`, from the same with `{"te"}`: the `\A` heads a conjunct | `BY` the second | SMT |
| `SpecL => <>(em.round < 0 \/ \E t \in {"tx"} : t \in domainTools)`, from the same with `{"tx", "t1"}`: the `\E` heads a disjunct | `BY` the second | SMT |

Each is false. TLC finds the first violated three steps from `Init`: after two approvals and an activation the
envelope is `{t1, te}`, so `t1` can be called and `t2` cannot. It finds the fourth, fifth and seventh to tenth
violated by a run in which the seat is activated and `t2` never enters the envelope, and the eleventh by every run:
`tx` is in no bundle, and no round is negative. TLC does not evaluate `\cdot`; the sixth fails at a pair of states in
which the seat is live with envelope `{t1, te}` and a call of `t1` is admitted, so admitting `t1` twice composes and
admitting `t2` cannot. The seventh and eighth are the ones a proof is likely to write: each starts from a true fact
soundly proved, and the step that reaches the false one goes to SMT with the temporal formula as one constant. The
ninth is the eighth behind a definition with a parameter: expanded in an SMT step, even at constant arguments, it is
the case again, which is why §10 expands such a definition only in a `PTL` step. The tenth and eleventh are the
eighth with the quantifier in a conjunct and in a disjunct. Citing an instance theorem at an instance fails the same
way: a lemma `ASSUME NEW t \in {"te"} PROVE F(t)`, cited for a goal `F(t)` about a constant of the same name `t`
drawn from all the tools, proves it. A hidden definition, even one with parameters, is an uninterpreted function of
them, declared under its own name, which is what §10's rule uses. A closed term is not safe for being closed: it is
named, and two names can be one (the second case).

*What it touches.* `spec/proof-scan.sh` looks from both ends, and `proof-scan-results-2026.10.08.txt` is its run.
In the sources, `ENABLED` occurs in the definitions and steps of six proof modules, all certified: `Coupling`,
`Correlator`, `Emergency_live`, `Lease_A1`, `Operators` and `RunCoupling`; and in `Coupling_live.tla`'s leads-to
properties and fairness conditions, which `Coupling_live_proof` extends and no step expands. `\cdot` occurs
nowhere. Temporal formulas occur in proof modules only as theorems `Spec => []P` and `SpecL => Spec`, each closed,
`P` the name of a definition with no parameters (one conjunction of three such names aside, in `Labels_proof`, cited
only in `PTL` steps), and are cited in steps a backend discharges by name with their bodies hidden, or in `PTL`
steps. In the six, every `ENABLED` under a binder is expanded in the step that proves it; one step,
`RunCoupling_proof`'s `ConsultValid` (line 342), passes the closed term `ENABLED Consult`, under no binder, to cvc5 by
name, which the case does not touch. In the runs, 53 SMT queries in 18 of the 24 proof modules hold an opaque term
under a binder, twelve of them in the six; in each the term is the step's primed goal or the prime of a
variable-tuple definition (`RunCoupling`'s `seals`, `flags` and `counters`), which mentions no bound variable, and
none is a temporal body moved out of a `[]`. Fourteen obligations go to Zenon or Isabelle, and none cites a temporal
fact: six in the six, all `BY ExpandENABLED` steps (`Correlator` line 518, `Lease_A1` 301, `Operators` 303 and 499,
`Emergency_live` 209 and 266), and eight in `RulesFloorNV_rev5` and `Seats`, which state no `ENABLED`. No result in
the 24 proof modules, certified or not, rests on the case, so none a record cites does. A check that refused every
opaque term under a binder would refuse those 53 sound queries along with any unsound one, since what an opaque
constant stood for cannot be read from the query, which keeps only its name; it could not see the Zenon and Isabelle
routes at all; and a check of the source alone could not see a body moved out of a `[]`. The scan says where to
look; reading the step at each line is what decides.

*The second: two terms with one name.* `tlapm` 7824dab names each term it abstracts, and each atom it hands LS4, `h`
and the first five hex digits of the MD5 of the term as it prints it: `[]D33`, with `D33` hidden, prints
`[]STATE_D33_` and is named `h4cb21`, and so is `[]E280`. That is 20 bits, and tlapm does not check that the terms
of one obligation get distinct names. Nor is the print one to one: it shows a bound variable as it shows a constant
of its name (`CONSTANT_k_`), and an expansion, a `TAKE` or a `WITNESS` that puts a constant under a binder of its
name does not rename the binder, so the result prints, and is named, as another term does; tlapm also accepts a
binder that shadows a constant, which SANY refuses. Two that share a name and take the same number of arguments are
one symbol to every backend: an opaque constant, or the function lifted from a primed definition with parameters,
for SMT; `a_h…a`, or a bare `h…` when the name ends in a letter, for Zenon and Isabelle; an atom for LS4. No bound
variable is needed and no untranslated operator: a primed hidden definition is named the same way. `NameCollision`,
which extends only `TLAPS`, proves `FALSE` twice and certifies: by SMT from `[]D33` and `~[]E280`, each proved, and
by `PTL` from `R63` and `~R699`, both atoms `h0823c`. `EnabledCollision` proves `ENABLED EmAdmit(c905)` from
`ENABLED EmAdmit(c32)`, both `h84173`, which TLC finds false as it finds `BadInv`; with `t` and `u`, in a module of
its own, the same step fails. `CaptureName` proves `[](P(k))`, with `P(z) == \E k \in D : w = <<k, z>>` and `k` a
`NEW` constant, from `[]Q`, with `Q == \E k \in D : w = <<k, k>>`: expanded, `P(k)` prints as `Q` does, and both are
one name. `CapturePTL` reaches a false theorem by §10's working form itself: a hidden `LH(v) == SpecL => []Has(v)`,
expanded only in a `PTL` step and at a `NEW` constant `x` that `Has`'s body binds, proves `LH(x)` through the
capture, and `\A x \in Tools : LH(x)` follows by SMT; TLC finds `\A v \in Tools : [](Has(v))` false. A hash's name
depends only on how its term prints, so a pair that collides can be found offline in about a thousand tries; by
accident, an obligation whose input to a backend holds k names has a chance of about k(k−1)/2^21 of a collision. A
capture is no accident, and recurs under every renaming that renames each identifier alike. Between terms that take
the same number of arguments a collision can only make a step prove that should not; between terms that take
different numbers, SMT keeps a constant and a lifted function apart, or applies a lifted function at the other's
arity, which cvc5 refuses as ill-formed, and Isabelle refuses the obligation as ill-typed, so a true step can fail,
and under `-C` the check of every Zenon proof in the module with it. No rule on the forms a proof writes avoids a
collision of the hash, a `PTL` step included; §10's rule against expanding a definition at an argument that names
one of its bound variables, in the obligation as tlapm forms it, avoids a capture. Neither `proof-cert.sh` nor a
reading of the input sees either, since the input keeps one name for both terms.

*What it touches.* A term that prints differently is named anew, so two terms whose names collide by the hash under
one naming will share one under another only by a second accident; two that print alike by capture share one under
every naming that renames each identifier alike, and the scan's section 4 looks for those instead.
`spec/proof-scan.sh` runs every proof module twice on one thread, so that each backend is called in the same order,
the second time over a copy of `spec/` in which every identifier but the keywords, the names the standard modules
define, the module names and record fields has a new name of the same length; it pairs the two runs' inputs to each
backend in order, and compares in each pair the shape, with identifiers and names masked, and the pattern of names,
and every obligation's route. In `proof-scan-results-2026.10.08.txt` the 24 proof modules give 1,883 inputs, 452 of
them with two or more names and 3,283 pairs of names within an input, so about 0.003 collisions to expect by
accident; every pair agrees, no input keeps a name under the renaming, no input holds a name the scan does not read,
and every obligation ends by the same route in both runs. An obligation whose result is reused is sent in neither
run: tlapm finds obligations identical before it names any term, and the renaming gives each identifier one new name
of its own, so on one thread the same obligations are sent, and the same reused, in both runs; a reused obligation's
result is that of the one sent, whose input is compared, and a collision among its own terms reaches no backend.
Section 4 reads every obligation the runs send to a backend as tlapm's display printer prints it once normalized
(`--printallobs`). That printer renames a bound variable whose scope holds a free name it would capture (`k` becomes
`k_1`), and the print tlapm hashes does not, so a renamed name whose scope holds the name it was renamed from, as a
variable and not as a record field, is a capture, whatever the source wrote: an expansion, a `TAKE` or a `WITNESS`,
an operator or infix argument, or a shadowing binder. Of the 1,853 obligations the runs send to a backend, all are
printed, and none holds a capture; each proof module parses under SANY, which refuses the shadowing tlapm accepts.
No result in the 24 proof modules rests on the case. Not seen: a collision both namings share in one input; a
collision between terms that hold no renamed identifier, of which there is none; and a capture the display printer
failed to rename, on which section 4 relies.

The two are recorded against T-0045-31 (ADR-0046 A2, with ADR-0045 A3, ratified 2026.10.08 in Batch 37), and are not
reported upstream yet (the custodian's decision, 2026.10.07). §10 has the rules that avoid the first and a capture;
nothing a proof writes avoids a collision of the hash, and the scan's renamed run is what checks a module for it. To
reproduce them, put these in a copy of `spec/` with `tools/` beside it and run `../tools/tlapm --toolbox 0 0` on
each prover module, which reports the backend that closed each obligation, and `./proof-cert.sh`, which certifies
`EnabledUnderBinder`, `TemporalUnderBinder`, `CdotUnderBinder`, `CombineUnderBinder`, `BoxNorm`, `ConjBox`,
`NameCollision`, `EnabledCollision`, `CaptureName` and `CapturePTL`, and, as it should, not `HiddenDef` or
`HiddenBox`, each of which holds a statement that must fail. Run TLC on the model module with `SPECIFICATION SpecL`,
`Mut = "none"` and `MaxRound = 2`, once each with `INVARIANT BadInv`, `PROPERTY BadEventually`,
`PROPERTY BadLeadsTo`, `PROPERTY AllTools`, `INVARIANT InvBig`, `INVARIANT ConjBig`, `PROPERTY SmallE` and
`PROPERTY AllHas`. `HiddenDef` shows the rule's form: `Closure` and `Literal` prove, and the two false statements,
`SuperBad` and `OutsideBad`, do not. `HiddenBox` is the ninth row: `BigBad` proves, and `BigPTL`, the same statement
by `PTL`, does not. `ConjBox` is the tenth and eleventh: `BigI` and `SmallE` prove.

```tla
---- MODULE EnabledUnderBinder ----
EXTENDS Emergency_live, TLAPS
LEMMA Bad == (\E t \in Tools : ENABLED EmAdmit(t)) => (\A t \in Tools : ENABLED EmAdmit(t))
OBVIOUS
====
---- MODULE TemporalUnderBinder ----
EXTENDS Emergency_live, TLAPS
LEMMA BadEventually == (\E t \in Tools : <>(t \in em.envelope)) => (\A t \in Tools : <>(t \in em.envelope))
OBVIOUS
LEMMA BadLeadsTo == (\E t \in Tools : em.live ~> (t \in em.envelope)) => (\A t \in Tools : em.live ~> (t \in em.envelope))
OBVIOUS
====
---- MODULE CdotUnderBinder ----
EXTENDS Emergency_live, TLAPS
LEMMA BadCdot == (\E t \in Tools : EmAdmit(t) \cdot EmAdmit(t)) => (\A t \in Tools : EmAdmit(t) \cdot EmAdmit(t))
OBVIOUS
====
---- MODULE CombineUnderBinder ----
EXTENDS Emergency_live_proof, TLAPS
LEMMA OneInst == ASSUME NEW t \in {"te"} PROVE SpecL => [](em.round > 0 => t \in em.envelope)
<1>1. t = "te"
    OBVIOUS
<1>2. SpecL => []EnvelopeHasTe
    BY EnvelopeHasTeAlwaysL
<1>3. EnvelopeHasTe <=> (em.round > 0 => t \in em.envelope)
    BY <1>1 DEF EnvelopeHasTe
<1> QED
    BY <1>2, <1>3, PTL
LEMMA AllFromOne == \A t \in Tools : SpecL => [](em.round > 0 => t \in em.envelope)
BY OneInst
====
---- MODULE BoxNorm ----
EXTENDS Emergency_live_proof, TLAPS
InvSmall == \A t \in {"te"} : em.round > 0 => t \in em.envelope
InvBig   == \A t \in {"te", "t2"} : em.round > 0 => t \in em.envelope
LEMMA InvSmallAlways == SpecL => []InvSmall
<1>1. SpecL => []EnvelopeHasTe
    BY EnvelopeHasTeAlwaysL
<1>2. EnvelopeHasTe <=> InvSmall
    BY DEF EnvelopeHasTe, InvSmall
<1> QED
    BY <1>1, <1>2, PTL
LEMMA InvBigAlways == SpecL => []InvBig
BY InvSmallAlways DEF InvSmall, InvBig
====
---- MODULE HiddenDef ----
EXTENDS Emergency_live_proof, TLAPS
LT(t) == SpecL => [](em.round > 0 => t \in em.envelope)
LEMMA InstTe == ASSUME NEW t \in {"te"} PROVE LT(t)
<1>1. t = "te"
    OBVIOUS
<1>2. SpecL => []EnvelopeHasTe
    BY EnvelopeHasTeAlwaysL
<1>3. EnvelopeHasTe <=> (em.round > 0 => t \in em.envelope)
    BY <1>1 DEF EnvelopeHasTe
<1> QED
    BY <1>2, <1>3, PTL DEF LT
LEMMA Closure == \A t \in {"te"} : LT(t)
BY InstTe
LEMMA Literal == LT("te")
BY InstTe
LEMMA SuperBad == \A t \in {"te", "t2"} : LT(t)
BY InstTe
LEMMA OutsideBad == ASSUME NEW t \in Tools PROVE LT(t)
BY InstTe
====
---- MODULE HiddenBox ----
EXTENDS Emergency_live_proof, TLAPS
LB(S) == SpecL => [](\A t \in S : em.round > 0 => t \in em.envelope)
LEMMA Small == LB({"te"})
<1>1. SpecL => []EnvelopeHasTe
    BY EnvelopeHasTeAlwaysL
<1>2. EnvelopeHasTe <=> (\A t \in {"te"} : em.round > 0 => t \in em.envelope)
    BY DEF EnvelopeHasTe
<1> QED
    BY <1>1, <1>2, PTL DEF LB
LEMMA BigBad == LB({"te", "t2"})
BY Small DEF LB
LEMMA BigPTL == LB({"te", "t2"})
BY Small, PTL DEF LB
====
---- MODULE ConjBox ----
EXTENDS Emergency_live_proof, TLAPS
LEMMA SmallI == SpecL => [](em.round >= 0 /\ \A t \in {"te"} : em.round > 0 => t \in em.envelope)
<1>1. SpecL => []TypeOK
    BY TypeAlwaysL
<1>2. SpecL => []EnvelopeHasTe
    BY EnvelopeHasTeAlwaysL
<1>3. TypeOK /\ EnvelopeHasTe => (em.round >= 0 /\ \A t \in {"te"} : em.round > 0 => t \in em.envelope)
    BY DEF TypeOK, EmType, EnvelopeHasTe
<1> QED
    BY <1>1, <1>2, <1>3, PTL
LEMMA BigI == SpecL => [](em.round >= 0 /\ \A t \in {"te", "t2"} : em.round > 0 => t \in em.envelope)
BY SmallI
LEMMA BigE == SpecL => <>(em.round < 0 \/ \E t \in {"tx", "t1"} : t \in domainTools)
<1>1. Init => (em.round < 0 \/ \E t \in {"tx", "t1"} : t \in domainTools)
    BY DEF Init
<1> QED
    BY <1>1, PTL DEF SpecL
LEMMA SmallE == SpecL => <>(em.round < 0 \/ \E t \in {"tx"} : t \in domainTools)
BY BigE
====
---- MODULE NameCollision ----
EXTENDS TLAPS
VARIABLE x
D33  == x = x
E280 == x # x
LEMMA BoxD33 == []D33
<1>1. D33
    BY DEF D33
<1> QED
    BY <1>1, PTL
LEMMA NotBoxE280 == ~[]E280
<1>1. ~E280
    BY DEF E280
<1> QED
    BY <1>1, PTL
LEMMA FalseBySMT == FALSE
BY BoxD33, NotBoxE280
R63  == x = x
R699 == x # x
LEMMA In == R63
BY DEF R63
LEMMA Out == ~R699
BY DEF R699
LEMMA FalseByPTL == FALSE
BY In, Out, PTL
====
---- MODULE EnabledCollision ----
EXTENDS Emergency_live, TLAPS
LEMMA TwoNew == ASSUME NEW c32 \in Tools, NEW c905 \in Tools, ENABLED EmAdmit(c32) PROVE ENABLED EmAdmit(c905)
OBVIOUS
====
---- MODULE CaptureName ----
EXTENDS TLAPS
CONSTANT D
VARIABLE w
P(z) == \E k \in D : w = <<k, z>>
Q    == \E k \in D : w = <<k, k>>
LEMMA Capture == ASSUME NEW k \in D, []Q PROVE [](P(k))
BY DEF P, Q
====
---- MODULE CapturePTL ----
EXTENDS Emergency_live_proof, TLAPS
Diag   == em.round > 0 => \E x \in Tools : x = x /\ x \in em.envelope
Has(v) == em.round > 0 => \E x \in Tools : x = v /\ x \in em.envelope
LH(v)  == SpecL => []Has(v)
LEMMA DiagAlways == SpecL => []Diag
<1>1. SpecL => []EnvelopeHasTe
    BY EnvelopeHasTeAlwaysL
<1>2. EnvelopeHasTe => Diag
    BY DEF EnvelopeHasTe, Diag, Tools
<1> QED
    BY <1>1, <1>2, PTL
LEMMA LHInst == ASSUME NEW x \in Tools PROVE LH(x)
BY DiagAlways, PTL DEF LH, Has, Diag
LEMMA LHAll == \A x \in Tools : LH(x)
BY LHInst
====
---- MODULE BinderDefectTLC ----
EXTENDS Emergency_live
BadInv        == (\E t \in Tools : ENABLED EmAdmit(t)) => (\A t \in Tools : ENABLED EmAdmit(t))
BadEventually == (\E t \in Tools : <>(t \in em.envelope)) => (\A t \in Tools : <>(t \in em.envelope))
BadLeadsTo    == (\E t \in Tools : em.live ~> (t \in em.envelope)) => (\A t \in Tools : em.live ~> (t \in em.envelope))
AllTools      == \A t \in Tools : [](em.round > 0 => t \in em.envelope)
InvBig        == \A t \in {"te", "t2"} : em.round > 0 => t \in em.envelope
ConjBig       == em.round >= 0 /\ \A t \in {"te", "t2"} : em.round > 0 => t \in em.envelope
SmallE        == <>(em.round < 0 \/ \E t \in {"tx"} : t \in domainTools)
Has(v)        == em.round > 0 => \E x \in Tools : x = v /\ x \in em.envelope
AllHas        == \A v \in Tools : [](Has(v))
====
```

`Bad` with `BY Zenon` in place of `OBVIOUS`, in a module that holds only it, certifies through Zenon and Isabelle;
with `BY Isa`, through Isabelle. `InvBigAlways` certifies through those two routes as well, by `Isa` and by `Zenon`.

---

## 9. Results, 2026.10.04

Twenty proof modules, 5,084 obligations.

| Route | Obligations |
|---|---|
| Trivial | 3,330 |
| SMT, proof accepted by ethos | 1,621 |
| Zenon, checked by Isabelle | 10 (5 accepted, 5 refused: tlapm reported one refusal, the first Isabelle printed, and Isabelle's own log shows all five of `RulesFloorNV_rev5`'s refused, 2026.10.08) |
| Isabelle | 2 |
| LS4, not certified | 115 |
| Failed under the checked backends | 6 |

**Seventeen certify:** Anchor, BreakGlass, Correlator, Coupling, Emergency, FloorComposition, FloorRouting, Labels,
Lease_A1, NonComposition, Observers, Operators, RunConfinement, RunCoupling, RunSeats, Seats, ToolList.

**Three do not.**

| Module | Why | What it would take |
|---|---|---|
| `RulesFloorNV_rev5_proof` | Five obligations are Zenon's, under Z3 as under cvc5, and Isabelle refuses their scripts: tlapm reports one, and Isabelle's log shows all five (2026.10.08). The 10.02 results never ran the check | Smaller steps for those cases, so that SMT proves them or Zenon's script reconstructs |
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
  (`Emergency_live_proof`, 2026.10.06, proves that fact as two invariants, each `BY ExpandENABLED, Isa`: Isabelle
  proves the expanded goal itself. cvc5 cannot, since tlapm writes the set equality `calls' = {...}` through an
  extensionality trigger and leaves cvc5 no term to instantiate `calls'` with.)
- **Keep untranslated terms behind hidden definitions** (2026.10.07). In a step SMT, Zenon or Isabelle discharges,
  no `ENABLED` or `\cdot` that is not expanded, and no temporal formula, may mention a variable bound in the
  obligation as tlapm forms it, once it has distributed `[]` over `/\` and `<>` over `\/` and moved a `\A` at the
  head of a `[]` body or conjunct, and an `\E` at the head of a `<>` body or disjunct, outward (§8). LS4 is not
  affected by this case, so a `PTL` step is free of it, though not of the second (§8). The working form:
  - Name a temporal property of a parameter by a definition, `LT(n) == Spec => (P(n) ~> Q(n))`, and keep it hidden in
    every step SMT, Zenon or Isabelle discharges. There it is an uninterpreted function of `n`, and quantifying over
    `n` is sound: the closure of an instance theorem and its use at any instance prove, and a closure over a larger
    domain or a use outside the domain does not (§8, `HiddenDef`). Expand it only in a `PTL` step: expanded in a step
    SMT discharges, even at constant arguments, a body with a `\A` at the head of a `[]` is the first case again
    (§8, `HiddenBox`: `LB({"te", "t2"})` proves from `LB({"te"})` `BY ... DEF LB`, and by `PTL` does not).
  - Prove an `ENABLED` or `\cdot` goal `BY ExpandENABLED` (`ExpandCdot`), with the action's definition, in the step
    that proves it, and do not carry such a fact across a quantifier by name.
  - Cite a theorem `Spec => []P` in such a step only with `P` hidden and applied to no variable bound in the
    obligation; a property of a parameter is the first sub-bullet's `LT(n)`. Prove an implication between invariants
    as a state-level step, and leave the temporal step to `PTL`.
  - Do not cite an instance theorem `ASSUME NEW n \in D PROVE F(n)` whose `F` holds an untranslated term over `n` in
    such a step. At a constant of the same name it proves `F` outside `D`, and a universal derived from it certifies
    from a smaller domain or without one of its hypotheses. Its exact closure, the bound name, the domain and every
    hypothesis unchanged and no fact in scope by `USE`, is sound, and so is `TAKE` over it; the hidden definition
    makes both unnecessary.
  Two of the four leads-to properties `Coupling_live.tla` states are quantified, all four have `ENABLED` premises,
  and a `WF1` or `SF1` argument over a decreasing measure needs a quantified leads-to hypothesis inside the proof,
  which `PTL` cannot combine from instances. A proof of them in Lean (ADR-0053) cannot meet either case. In TLAPS no
  route for the measure step under this rule is known yet.
- **Expand no definition at an argument that names one of its bound variables** (2026.10.08). In any step, `PTL`
  included, no definition may be expanded at an argument, in the obligation as tlapm forms it, that mentions a name
  its body binds, or that a definition it passes the argument to binds: the expansion prints, and is named, as
  another term (§8, `CaptureName`, `CapturePTL`). The argument is the one tlapm forms: `TAKE x \in S` on a goal
  `\A z \in S : F(z)` leaves `F(x)`, `WITNESS e \in S` on `\E z \in S : F(z)` leaves `F(e)`, and a definition named
  in an argument, an operator passed as one and an infix operator are expanded as well. Rename the bound variable,
  and take, witness and name nothing a definition binds; and write no binder that shadows a constant, which tlapm
  accepts and SANY refuses. The scan's section 4 reads every obligation as tlapm prints it and lists each capture;
  the 24 proof modules have none.
- **Run the scan on every new proof module** (2026.10.07). No form a proof is written in avoids a collision of the
  hash. `proof-scan.sh <Module>_proof` runs the module again over renamed sources and reports every input whose
  names differ, and every obligation whose route differs, between the runs; a step at such an input rests on a
  collision until a reading of it shows otherwise. Its section 4 lists every capture in the obligations as tlapm
  prints them, and every module SANY does not parse.
- **A longer timeout rarely helps.** `STRETCH=10` recovered one obligation in `Confinement` and none elsewhere.
- **Run `proof-results.sh` first.** It is faster and finds real proof failures; then `proof-cert.sh`.

---

## 11. Where this sits in the records

| Record | Relation |
|---|---|
| ADR-0030 §5 A1 (Accepted, Batch 24) | The precedent: a routing verdict counts only with a checked proof. `floor/cvc5-checked` is the wrapper this one follows |
| ADR-0045 T-0045-14 | The checker, its signature and the wrapper as a trust root. Certified proofs rest on the same checker |
| ADR-0045 T-0045-31; ADR-0046 §3 | The prover as a trust root. Its residual names "the SMT backends' soundness" |
| **ADR-0046 E2** (ratified 2026.10.04, Batch 28) | Corrects the sentence on what `-C` checks (§1) |
| **ADR-0046 A1** (ratified 2026.10.04, Batch 28) | Gives T-0045-31 a certified configuration and lists which modules are in it. Its ratification condition, the regeneration of §6 and the test of §7, was run on 2026.10.04 and met |
| **ADR-0046 A2, ADR-0045 A3** (ratified 2026.10.08, Batch 37) | Record the two unsound cases of §8 against T-0045-31: in its residual, in Annex B's instance for build 7824dab, and as an open obligation for a check that sees the first. Their ratification condition, §8's reproductions, a rerun of `proof-scan.sh` and a reading of each step it lists, was met on 2026.10.08 |
| **ADR-0045 E1** (ratified 2026.10.08, Batch 37) | Corrects what Annex B says of a certified results file: it names the driver without its digest, and a rerun can differ in its split between calls and reuse, and in which of Zenon's refused proofs it names (§6) |
| **ADR-0046 E3, E4** (ratified 2026.10.08, Batch 37) | Correct what §3 says a rerun reproduces (§6), and how many of `RulesFloorNV_rev5`'s Zenon proofs Isabelle refuses (all five; §9) |
| **ADR-0053 E1** (ratified 2026.10.08, Batch 37) | The same correction of the refused proofs |
| G9 open item 74 | "The SMT backends' proofs checked by Isabelle": answered by a different checker than it names |
| ADR-0047, 0048, 0050, 0052 (Proposed) | Each cites its module's certified results file by digest in its ratification condition |

---

## 12. Open

- **LS4.** No route checks a temporal step. The steps are few and of one shape, and a small fixed lemma library
  proved once in Isabelle could replace them. *2026.10.05:* the Lean re-encodings in `spec/lean/` are a route beside this one
  in which the temporal step is an induction the Lean kernel checks, for fifteen of the proof modules, at the price of
  the encoding (`proof-method.md` §5b). They do not certify the TLAPS proofs; they prove the same theorems again.
- **The translation.** Nothing here examines how the prover turns an obligation into a query in general. Two cases
  are known to be unsound (§8). No check detects the first, and ADR-0046 A2 (Batch 37) owes one: it needs what the
  prover's abstractions stand for, in the obligation as the prover forms it, and neither the query, which keeps only
  a name, nor the source, before quantifiers are moved out of temporal bodies, shows that; `spec/proof-scan.sh` says
  where to look. For a collision of the hash the scan's renamed run is a check by a second naming, not a proof, and
  the certified run does not make it; for a capture, the scan's reading of the obligations as tlapm's display
  printer shows them is, as far as that printer renames what it must. A prover that named each term by the whole
  term in a form that tells a bound variable from a constant (bound variables by position), or checked that two
  terms with one name are one term, would close both; the whole term as it prints would not.
- **One solver, one version.** cvc5 1.4.0 is pinned by digest because the floor pins it. A newer cvc5 may prove the
  six obligations that fail, and would be a different certification.
- **The three modules that do not certify** (§9). Still uncertified here. Their theorems are also proved in Lean,
  every step kernel-checked, of a re-encoding (`spec/lean/TopakSpec/RulesFloorNV_rev5.lean`,
  `spec/lean/TopakSpec/Confinement.lean`; ADR-0053).
- **The evidence is not kept.** A digest and a rerun stand in for it; where tlapm reuses results a rerun can give
  another digest (§6), so the digest on record cannot always be confirmed.
- **This document is the drafter's**, as the wrapper, the driver and seventeen of the twenty results are.
