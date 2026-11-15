# TLA+ mutations and witnesses: generic practice, TOPAK practice, and what passes between them

**2026.11.15** · derived · reference, not design · prepared by Claude at the custodian's request, in a session on
`scottcochran/gov-tla`, a repository that applies this corpus's TLA+ skill to another subject. It replaces a
generic summary of "mutations and witnesses in TLA+" that the custodian asked to have checked against the skill,
and that was found partly right, partly wrong and partly invented (§5). The tree was read at `bb76b46`
(2026.11.12) and `gov-tla` at `39bd8c1`. Paths are this repository's, except those under `scripts/`, `rows/` and
`results/`, which are `gov-tla`'s.

The custodian asked for three sections: generic best practice (§1), TOPAK practice with how it differs and why (§2),
and any cross-pollination between the two (§3). §4 is the checklist the replaced summary ended with, corrected.

**Short answer.** Both techniques ask an existential question of a model checker, and both exist because a `HOLDS`
is the result a wrong specification produces most easily. A **mutation** removes something from the model and
requires a counterexample: it shows a property *discriminates*. A **witness** asserts that something never happens
and requires a counterexample: it shows the property is not *vacuous*, because the states it speaks about are
reached. Generic practice has the witness as long-standing advice to the author, and the mutation only by analogy
with coverage in model checking; it has no convention for recording either. TOPAK makes them the shape of the module
(one `Mut` constant, one guard per mutation, a `Never…` operator per reachability claim), runs the whole mutation ×
property matrix, keeps every cell as a row in a generated results file, and then uses the matrix a second time, as
the hypotheses of its proofs. The differences all follow from that second use and from the rule that a results file
is the only form evidence takes.

## 1. Generic best practice

"Generic" here means what the model-checking literature and the published TLA+ guidance support, independent of
any one project. Sources are numbered in §6; each was checked for this document, and where only a summary of a
source was read §6 says so. Two notes on words first, because the summary this replaces used them loosely.

- **"Witness" is a recent word in TLA+.** Lamport calls the practice a sanity check [6]; the community calls it a
  reachability check [7]. In the vacuity literature a witness is a trace showing that a property holds
  non-vacuously [1][2]. In the TLA+ tools the word first appears in 2026, with TLC's provisional `_POSSIBLE`
  statement, whose conditions are "witnessed" by a state or a step [9].
- **"Mutation testing" of a specification** has three meanings that must be kept apart. *Mutating the model* and
  re-checking a fixed property measures whether the property depends on the mutated part: coverage metrics for
  model checking "are based on modifications we apply to the system in order to check which parts of it were
  actually relevant for the verification process to succeed" [4][3]. *Mutating the property* and checking whether
  it still holds detects vacuity: a subformula that can be changed without changing the verdict does nothing
  [1][2]. *Generating tests* from the counterexamples that mutants produce [5] is about an implementation and not
  about the specification's quality.

**How much of this is established for TLA+.** The witness side is, and has been since *Specifying Systems*. The
mutation side is not: no peer-reviewed paper, operator catalogue or maintained tool for mutation testing of TLA+
specifications was found, only the lineage above, practice in individual projects, and one 2026 preprint [11].
What follows under "Mutations" is therefore the model-checking literature's idea carried to TLA+ by analogy, plus
Lamport's advice about properties that should fail.

### Mutations

1. **Hold the property fixed and weaken the model.** Remove or weaken one guard, one conjunct of an action, or one
   clause of `Init`, and require the checker to report a violation of the property that part was written to
   protect [4]. Flipping operators inside the *invariant* answers the vacuity question, not this one.
2. **Make sure the checker can fail.** Lamport's form of the advice is about properties: "make sure that TLC finds
   errors in properties that should be violated", and for liveness, "have it check a liveness property that the
   specification does not satisfy and make sure it reports an error" [6].
3. **One change per mutant.** A mutant that changes two things cannot say which one the property rested on.
4. **A surviving mutant is a coverage hole with three readings**, and the work is deciding which: the property
   does not depend on that part of the model (the property is too weak, or the guard is redundant); the model is
   too small for the difference to show; or the mutant is equivalent to the original.
5. **Mutants do not replace reading the property.** A trivially true invariant is found by reading it. Mutation
   is for the property that looks substantive and is not.

### Witnesses

1. **For everything the specification is meant to allow, have the checker show that it happens.** "It's very easy
   to satisfy a safety property by simply doing nothing" [6]. The traditional form is an invariant asserting the
   thing never happens, which TLC must violate [6][7]; the trace it prints is the example. The same device
   produces example traces in Apalache [10].
2. **Keep the check, if the checker allows it.** TLC's documentation gives the weakness of the traditional form:
   it is "tedious, easy to forget, and impossible to keep in the configuration file, since it makes a passing run
   fail" [9]. Since 2026 a `_POSSIBLE` section lists state predicates and actions that must each be witnessed, and
   TLC fails the run otherwise. It is provisional and "may be renamed or removed".
3. **Read the coverage the checker will print.** TLC's `-coverage` option counts how often each conjunct of
   the next-state action was used, and "a value of 0 indicates part of the next-state action that was never
   'executed'" [6]; the Toolbox highlights actions that are never enabled [8]. An action never taken is a missing
   witness nobody had to think of. It is necessary, not sufficient: an action can be taken and the interesting
   state still not reached.
4. **A witness is relative to the model.** A state excluded by a `CONSTRAINT` witnesses nothing, and in
   simulation an unwitnessed condition may only have been missed [9].
5. **Reachability is not progress.** A witness says some behaviour reaches a state, and it is checked without
   fairness. A liveness property says every fair behaviour does. "Possibility conditions are not liveness
   properties" [9].
6. **Guard liveness against vacuity separately.** A specification is machine closed when its liveness part is a
   conjunction of weak or strong fairness conditions on subactions of `Next` [6, §8.9.2], so that fairness cannot
   rule out a finite behaviour. Fairness of another form can forbid steps silently, and every property holds of a
   specification with no behaviours. Fairness on `Next` as a whole is machine closed but is rarely the right
   condition: it says something happens, not that the thing which must happen does.

### From models to implementations

Connecting a checked model to code is established practice, and a separate activity with its own literature:
validating traces recorded from the implementation against the specification [14][15], and generating tests from
the model's behaviours [12][13]. The record is mixed. At MongoDB, trace checking of the server was abandoned and
test generation for a second product succeeded [13]. Witness traces and mutant counterexamples can seed such
tests [5]. That is an option, not a part of what mutations and witnesses are for.

### What generic practice does not settle

For TLA+ there is no convention for how a mutant is carried (an edit, a constant, a second module), for which
(mutant, property) pairs to run, for whether results are kept, or for how a mutation relates to a deductive proof
of the same property. Those are the places TOPAK made choices.

## 2. TOPAK practice, how it differs, and why

**Where it came from.** The corpus met vacuity first in policy, not in TLA+: the failure it cites from Moon &
Varshney §4.6 is a boundary predicate quantifying over an always-empty field, vacuously true. ADR-0007's three
gates (totality, non-vacuity, discrimination) answer it, and were extended on 2026.09.12 to run on the floor
itself. `derived/tlaplus-paxos-cheat-sheet-2026.09.13.md` §10 then says the TLA+ analogue is "an invariant whose
antecedent is never satisfied on any reachable state" and recommends the same gate: "seed a mutation that
*should* break each invariant and confirm it does". ADR-0026 §6 ran it two days later, with the three checks the
method still has: satisfiability and independence, reachability ("or every safety property holds vacuously"), and
mutation ("a counterexample is the pass condition"). At `bb76b46`, of the 39 base modules in `spec/`, 32 declare
a `Mut` constant and 35 define `Never…` operators: 136 mutation names and 205 witnesses, by grep.

**What it does** (`spec/README.md`, Practice; `spec/proof-method.md` §1 and §2; the
`writing-tla-specs-and-proofs` skill):

- A module has **one constant `Mut`**. `Mut = "none"` is the mechanism as the record specifies it. Each other
  value removes exactly one guard, written where the guard is, and the module header names the property that
  removal must break. Where one exists, a mutation is a real earlier text ("the record's text before R1").
- Each claim that something can happen is a **`Never…` operator that TLC must violate** under `Mut = "none"`.
- Properties are written to be **local**: a flag the violating action would set, or an append-only set of records,
  with every check a guard on the action that needs it.
- The results file has a row for **every property under `none`** (`HOLDS`), **every mutation against the
  properties it must break** (`COUNTEREXAMPLE`), **every mutation against the properties it must not break**
  (`HOLDS`), and **every witness** (`COUNTEREXAMPLE`). The file is dated, prints the digests of the checker and the
  module, is regenerated by a script and is never edited.
- The proof module proves each invariant as `Spec => []P` **assuming only `Mut # "M_X"` for the mutations that
  break `P`**, carries one lemma per mutation saying what the mutation admits, and is then **flipped**: with one
  hypothesis changed to `Mut = "M_X"` the prover must fail.
- A liveness module adds, for each fairness condition, **a row that drops or weakens it and must break a
  property**, and for each fair specification **a `NoBehaviour` row that must be violated**.

| | Generic practice | TOPAK | Why |
|---|---|---|---|
| What is mutated | No TLA+ convention. In the coverage literature, any part of the model, by syntactic operators [4][5] | One guard of the mechanism, chosen by the author | The mutation has to name the guard a property rests on, because that name becomes a proof hypothesis. A flipped operator names nothing in the design |
| Where the mutant lives | Not settled | In the module, behind `Mut`, usually folded into a constant operator | A module is frozen by digest once a record cites it. TLC and the prover must run the same text, and the hypotheses need `Mut` in scope. A constant operator keeps the actions uniform, so the type invariant holds under every mutation |
| Which pairs are run | Not settled; at least the property expected to fail [6] | Every mutation against every property | The `HOLDS` cells are the "Breaks under" column, and a theorem's hypothesis is exactly that column. Writing the hypotheses corrected the column four times, among them rows that had never been run and a transcription error (`spec/proof-method.md` §1) |
| A surviving mutant | A coverage hole [4] | A wrong header, or a design finding | ADR-0026 §6 found floor entries R1 to R3 vacuous against the mechanism as then written, which was changed to read their values, and R4 vacuous in any design, so it was withdrawn. §7 found a mutant that survived because four humans leave two counted seats, where a threshold is unanimity |
| A witness | An invariant added by hand that TLC must violate, then removed [6][9]; since 2026, a `_POSSIBLE` condition | A named property with an expected verdict, in the same row format as a mutation | One script and one results format serve both, and the expected verdict is what lets the check stay. The pinned checker predates `_POSSIBLE` |
| Witness hygiene | Not addressed in the sources read | The witness's flag is distinct from the property's flag | A witness reading a flag an unrelated event may have set is weaker than it looks |
| Liveness vacuity | Machine closure; check one liveness property that should fail [6] | Fairness on actions named for whose obligation each is; a drop row per condition; `NoBehaviour` per fair spec; a deadlock audit | Two weaker fairness conditions that looked sufficient failed their rows (`SpecAnyBeat`, `SpecWFKeepUp`). TLC's deadlock check does not see a livelock, and most run scripts turn it off; the audit shows every state with no successor is at a bound the module imposes |
| What witnesses cannot see | "Not liveness properties" [9], and no more | A mutation that reaches every state of the unmutated module | `M_HBLIVE` passes every invariant and reaches every witness; only two leads-to properties break (`spec/proof-method.md` §5c). `derived/topak-liveness-2026.10.07.md` gives such a mutation as the reason the liveness work is worth its cost |
| Reachable against available | "Some reachable state", not every behaviour [9] | A witness shows a call can happen in some run; an invariant over `ENABLED` shows it can happen in every state that needs it | The emergency call was the one escape from a stall and rested only on a witness. The claim was universal, so it became a proved `ENABLED` invariant |
| The proof | A separate matter | Hypotheses are the mutations; the flip test mutates the proof | A proof that survives a flipped hypothesis is proving something the mutation does not break |
| Records | No convention; `_POSSIBLE` keeps witnesses in the configuration file [9] | Rows in a dated, digest-stamped, generated file; words fixed as *checked*, *proved*, *sampled* | Records cite the evidence by digest, and each word names what bounds the claim |
| Conformance | Trace validation [14][15], or tests generated from the model [12][13] | Recorded traces of the reference replayed through an operational model; three modules' mutations restated by hand as code tests | "Drift detection, not a refinement" (`spec/README.md`, Practice 5; ADR-0045 T-0045-28). Neither tool's result is a claim about running code, and the corpus says so wherever it cites one |

**The same gate at five layers.** The discipline is not peculiar to TLC in TOPAK. The Cedar floor has
non-vacuity, discrimination and negative-control rows run through an SMT solver (`floor/run-gates.py`). The TLAPS
proofs have the flip test. The Lean encodings have a mutation check: eighteen mutated copies, each of which fails
to build in the lemma that carries the mutated definition (`spec/lean/README.md`). The reference's tests restate
the properties of three modules, each with a test that the corresponding mutation, "or the state the mutation
would admit", is refused (`mechanism/crates/topak-core/tests/mutations.rs`). At every layer the rule is the one
ADR-0026 §6 wrote for the first: a check that could not have failed is not evidence.

**What the method does not catch, on the corpus's own record.** A property can pass every mutation and every
witness and still say less than its record reads as saying, because the model cannot express the violation.
`derived/topak-critical-review-2026.11.11.md` CR-53 lists six such properties: two hold in `Correlator.tla`
because no correlator in the model can report a finding whose condition is false, where the record says the
mechanism does not check findings. Mutations test the guards the author wrote down. They do not test what the
model left out.

## 3. Cross-pollination

### From generic practice into TOPAK (happened, and on the record)

- **Vacuity as a named exposure.** Taken from the policy-verification literature the corpus was reading, by way of
  ADR-0007's gates, into the TLA+ layer (§2, "Where it came from").
- **Machine closure, and a liveness property that should fail.** The caution that a condition on states is not
  machine closed as fairness on an action is, and can leave a specification with no behaviour, is the textbook
  point [6]. So is checking a liveness property the specification does not satisfy. TOPAK turned the first into
  the `NoBehaviour` row and the second into a row per fairness condition.
- **Trace validation.** `spec/Mechanism.tla` with `spec/trace2tla.py` is the generic technique [14][15], adopted
  as stage 1 of the refinement gap and described as no more than that.
- **Mutation testing of code.** `tests/mutations.rs` is ordinary software mutation discipline, pointed at the
  specification's mutations.

### From generic practice, not yet taken

These are suggestions of this document, not findings of the corpus.

- **TLC's coverage output.** No script in `spec/` or `tools/` passes `-coverage` [6][8]. It would list the parts
  of each next-state action never used, cheaply, and would catch a missing witness that nobody thought to write.
  It fits the method as one more generated section of a results file.
- **`_POSSIBLE`, when it is no longer provisional** [9]. It keeps witnesses in the configuration file, takes an
  action directly where TOPAK writes a step witness as `[][~A]_vars`, and counts how often each is witnessed.
  Three things argue for waiting: the statement may be renamed or removed; the checker pinned in `tools/TLA-PIN`
  and printed in every results file (TLC 2.19 of 08 August 2024) predates it, and a new checker is a new
  trusted-base item; and it covers witnesses only, so the mutation rows keep the expected-verdict format either
  way. Its documentation's two uses are TOPAK's already: justifying a reduced model, and regression tests on the
  specification.
- **A standing coverage audit, in both directions.** TOPAK's mutations are chosen by the author. The 11.11 self
  review computed the property side once, for the eight overlay modules
  (`derived/topak-self-review-annex-2026.11.11/runs/22-overlay-mutation-coverage.txt`): which conjuncts of `Safe`
  no mutation breaks, and which mutations break nothing. It found `CountExact`, proved with no hypothesis and
  targeted by no mutation (CR-53). That was one run in a review's annex, over eight of the modules. The guard
  side has not been done at all: mutation operators for specifications [5], applied to each module's guards with
  each mutant run against `Safe`, would list the guards no stated property needs. This is the one use the
  replaced summary's "AST-level mutation" has here: an audit that proposes mutations, not the mutations
  themselves.
- **Antecedent checks, generated.** For a property of the form `A => B`, vacuity detection [1][2] derives the
  witness "never `A`" mechanically. TOPAK writes its witnesses by hand, and a generator over the property list
  would show which are missing.
- **Tests from counterexamples.** Each `COUNTEREXAMPLE` row has a short behaviour that reaches a bad state under
  one mutation. Exported, those are the inputs `tests/mutations.rs` now builds by hand [5]. The direction matters:
  this tests that the code refuses what the mutation admits, and proves nothing about the code.

### From TOPAK toward generic practice

None of these depends on TOPAK's subject matter.

1. **Run the whole matrix, and treat the `HOLDS` cells as data.** The cells that hold say what each property does
   not depend on, which is as much a part of its meaning as what breaks it.
2. **Make the mutation a proof hypothesis, and take the weakest.** This ties the two tools together where generic
   practice leaves them apart: the checker shows the guard is needed, the prover shows it is enough, and a
   disagreement between them is an error in one or in the table. It found five (four rows and one parameter).
3. **Flip one hypothesis.** Mutation testing of a proof costs one scratch run per mutation and has the same
   justification as mutation testing of a model.
4. **State what witnesses and invariants cannot see.** A mutation that reaches every state passes every safety
   check and every witness. Say so in the header, and state the liveness property or the `ENABLED` invariant that
   does catch it.
5. **A `NoBehaviour` row for every fair specification, and a drop row for every fairness condition.** This is
   non-vacuity and discrimination again, for liveness.
6. **A surviving mutant can indict the constants.** Ask whether the model is large enough for the mutation to
   matter before concluding that the guard is redundant.
7. **Prefer a mutation that is a real earlier design.** It records that the current text was a correction, and
   the row shows what the correction bought.
8. **Fix the words.** *Checked* for a model checker at constants, *proved* for a prover under named hypotheses,
   *sampled* for simulation.

**One transfer has been tried.** `scottcochran/gov-tla` applies the skill, copied unchanged, to a subject with no mechanism
and no code: four modules of constitutional structure, with 70 mutations, 60 witnesses, 1,526 TLC rows and 5,599
proof obligations (its README's table). The method carried over without change to what a mutation is. A mutation
there is an earlier law (the Articles of Confederation, *Humphrey's Executor*, the legislative veto before
*Chadha*), which is item 7 with a different kind of record. What changed was tooling, and two of the changes could
go back: one generic row generator in place of a run script per module (`scripts/tlc_rows.py`), and the flip test
as a script that attributes each failure to the lemma carrying the flipped hypothesis (`scripts/flip_test.py`),
where TOPAK's is a scratch run by hand whose outcome is noted in prose.

## 4. Checklist

| | Purpose | Rule | Evidence |
|---|---|---|---|
| **Mutation** | Show a property discriminates: it depends on the guard said to protect it | One guard per mutation, in the module, named in the header with the property it must break. Run every mutation against every property | A `COUNTEREXAMPLE` row for each pair that must break and a `HOLDS` row for each that must not; a proof hypothesis `Mut # "M_X"` for exactly the first kind; a flipped proof that fails |
| **Witness** | Show a property is not vacuous: the states and steps it speaks about are reached | One `Never…` property per claim that something can happen, checked under `Mut = "none"` without fairness, its flag distinct from any property's | A `COUNTEREXAMPLE` row for each |
| **Liveness** | Show progress is neither assumed away nor satisfied by an empty specification | Fairness on actions of `Next`, each named for whose obligation it is. State a liveness property or an `ENABLED` invariant for any mutation that reaches every state | A `HOLDS` row under the fair spec at two sets of constants; a violated row for each condition dropped or weakened; a violated `NoBehaviour` row; a deadlock audit |

None of the three is a claim about an implementation, and none is a proof: a row is *checked* at its constants.

## 5. What the replaced summary got wrong

The summary was a generic account, unsourced, that read as a description of this practice. Its frame was sound:
mutations test that properties are sensitive, witnesses test that they are not vacuous. Against §1 and §2:

- It mutated **invariants and guards** alike, by flipping operators. Mutating the invariant is the vacuity check,
  and neither generic coverage nor TOPAK means that by a mutation.
- It put the `Mut` switch in a **harness, to keep the core module clean**. TOPAK puts it in the module, at the
  guard, for the reasons in §2.
- It said to run each mutant **only against its targeted property**. TOPAK runs the whole matrix, and the rows
  that summary would skip are the ones the proofs need.
- It made a witness a **kept trace**, and used witnesses to validate **liveness under fairness**. A witness is a
  violated property checked without fairness; liveness vacuity has its own rows.
- Its fairness example was **`WF_vars(Next)`**, the form §1 calls rarely the right condition.
- **"Capability profiles"**, **"provider behaviours"** and witness traces as **"golden test vectors"** correspond
  to nothing in either practice as stated. Trace validation and test generation exist (§1), as separate work,
  and TOPAK's runs from the code to the model, not from witness traces to tests.
- **`TypeOK == TRUE`** is not the failure mutations are for.

## 6. Sources

Generic practice. Bibliographic data was checked against the publishers' records on 2026.11.15. The quotations
from [4], [6] and [9] are from the texts themselves; [1], [2], [3] and [15] were read only in summary, and are
cited for what they are about, not for a quotation.

1. I. Beer, S. Ben-David, C. Eisner, Y. Rodeh, "Efficient detection of vacuity in ACTL formulas", CAV 1997, LNCS
   1254, doi:10.1007/3-540-63166-6_28; as "Efficient detection of vacuity in temporal model checking", *Formal
   Methods in System Design* 18, 2001, doi:10.1023/A:1008779610539.
2. O. Kupferman, M. Y. Vardi, "Vacuity detection in temporal model checking", CHARME 1999, LNCS 1703,
   doi:10.1007/3-540-48153-2_8; *STTT* 4(2), 2003, doi:10.1007/s100090100062.
3. Y. Hoskote, T. Kam, P.-H. Ho, X. Zhao, "Coverage estimation for symbolic model checking", DAC 1999,
   doi:10.1145/309847.309936.
4. H. Chockler, O. Kupferman, M. Y. Vardi, "Coverage metrics for temporal logic model checking", TACAS 2001, LNCS
   2031, doi:10.1007/3-540-45319-9_36.
5. P. E. Black, V. Okun, Y. Yesha, "Mutation operators for specifications", ASE 2000,
   doi:10.1109/ASE.2000.873653; P. E. Ammann, P. E. Black, W. Majurski, "Using model checking to generate tests
   from specifications", ICFEM 1998, doi:10.1109/ICFEM.1998.730569. Both mutate a specification so that the
   counterexamples become tests of an implementation.
6. L. Lamport, *Specifying Systems*, Addison-Wesley, 2002: §8.9.2, machine closure; §14.3.5, checking liveness;
   p. 252, the `-coverage` option; §14.5.3, "Hints on Using TLC Effectively", under "Be Suspicious of Success".
7. H. Wayne, "What TLA+ Can't Check", newsletter, 2023.04.17, buttondown.com/hillelwayne/archive/what-tla-cant-check,
   which calls the violated invariant "a well-known idiom"; S. Merz gives the same on the TLA+ mailing list,
   2020.10, discuss.tlapl.us/msg03798.html.
8. TLA+ Toolbox help, "Profiling", tla.msr-inria.inria.fr/tlatoolbox/doc/model/profiling.html; M. A. Kuppe,
   L. Lamport, D. Ricketts, "The TLA+ Toolbox: better, faster, stronger", F-IDE 2019, doi:10.4204/EPTCS.310.6.
9. "Possibility Conditions with TLC's `_POSSIBLE`", `docs/possible-conditions.md` in `tlaplus/tlaplus`, read on
   2026.11.15 at its `master` branch. Provisional.
10. Informal Systems, model-based testing tutorial, "Generating traces",
    mbt.informal.systems/docs/tla_basics_tutorials/generating_traces. Apalache checks liveness by a
    liveness-to-safety transformation and does not support `WF`, `SF` or `ENABLED` directly
    (apalache-mc.org/docs/apalache/features.html).
11. Spencer and others, "TLA-Prover", arXiv:2606.06133, 2026, a preprint that alters a property and requires that
    TLC detect a violation. Nothing else was found on mutation testing of TLA+ specifications. Absence from a
    search is weak evidence.
12. A. Kupriyanov, I. Konnov, "Model-based testing with TLA+ and Apalache", TLA+ Community Event, 2020; the
    Modelator tool, github.com/informalsystems/modelator.
13. A. J. J. Davis, M. Hirschhorn, J. Schvimer, "eXtreme Modelling in Practice", *PVLDB* 13(9), 2020,
    doi:10.14778/3397230.3397233.
14. H. Cirstea, M. A. Kuppe, B. Loillier, S. Merz, "Validating traces of distributed programs against TLA+
    specifications", SEFM 2024, LNCS 15280, doi:10.1007/978-3-031-77382-2_8.
15. H. Howard, M. A. Kuppe, E. Ashton, A. Chamayou, N. Crooks, "Smart Casual Verification of the Confidential
    Consortium Framework", NSDI 2025.

This corpus, at `bb76b46`: `spec/README.md` (Practice, Liveness, TLAPS proofs); `spec/proof-method.md` §1, §2, §5 and
§5c; `decisions/ADR-0007.md`; `decisions/ADR-0026.md` §6 and §7; `decisions/ADR-0045.md` (T-0045-28);
`derived/tlaplus-paxos-cheat-sheet-2026.09.13.md` §10; `derived/topak-liveness-2026.10.07.md`;
`spec/Coupling.tla`, `spec/Coupling_live.tla` and `spec/Coupling_live-rows.txt`; `spec/lean/README.md`;
`floor/README.md`; `mechanism/crates/topak-core/tests/mutations.rs`; `skills/writing-tla-specs-and-proofs/`.

`gov-tla`, at `39bd8c1`: `README.md`; `Executive.tla`; `rows/Executive-rows.txt`;
`results/Executive-results-2026.11.09.txt`; `scripts/tlc_rows.py`; `scripts/flip_test.py`.
