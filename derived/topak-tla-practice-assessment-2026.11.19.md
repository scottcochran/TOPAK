# TOPAK's TLA+ and TLAPS practice against the advanced concepts

**2026.11.19** · derived · an answer, not a record · basis: the tree at `6a26310`; `spec/` (41 specification
modules, 34 proof modules), `spec/README.md`, `spec/proof-method.md`, `spec/proof-certification.md`, the latest
`spec/*-proof-cert-results-*.txt` of each proof module, `spec/lean/`, `mechanism/lean/`, the
`writing-tla-specs-and-proofs` skill (`skills/writing-tla-specs-and-proofs/`), `derived/topak-liveness-2026.10.07.md`
and `derived/topak-refinement-verification-options-2026.11.04.md` · written by the assistant at the custodian's
request · nothing here is built or ratified.

> Assess TOPAK TLA practice against the following concepts: [a list of sixteen concepts in four groups: refinement
> and composition; advanced temporal logic and liveness; TLAPS proof engineering; specification hygiene and
> meta-verification]

**How it was read.** The method notes and the skill were read in full where they bear on a concept; the modules
were read where a note's claim needed checking. Counts are occurrences in the tree at `6a26310`, by `grep` over
`spec/*.tla`, split into proof modules (`*_proof.tla`) and the rest; obligation and LS4 totals are summed from the
newest certified results file of each proof module. A count says how often a construct is written, not how well it
is used; where the two differ the text says so.

---

## 0. Short answer

1. **The practice is built for cheap safety proofs and for distrusting them.** It is strongest in the third and
   fourth groups: finding inductive invariants, and checking the checks (vacuity, witnesses, mutation, the trusted
   base). In the fourth group it goes further than most published TLAPS work: it found and reported two unsound
   cases in tlapm's translation, certifies SMT obligations with a proof checker, and proves the same theorems again
   in Lean.
2. **It understands the second group and has proved none of its hard half.** Machine closure, the choice between
   weak and strong fairness, and `ENABLED` are handled with care and evidence. No leads-to property is proved, in
   TLAPS or in Lean. Coupling's four are owed, and TLC checks them at small constants.
3. **The first group is absent from the TLA+ layer by choice.** No module uses `INSTANCE`, `\EE` or `-+->`. The
   skill puts refinement outside its scope, and `proof-method.md` §5 says the proofs were cheap because there was
   no `INSTANCE`, no refinement mapping and no liveness. Refinement exists only in Lean, and code-to-spec stays a
   tested premise (T-0045-28).
4. **The next steps that would move the most:** two unquantified leads-to proofs that the documented shape appears
   to fit (§2.2); a first spec-to-spec refinement, `Paxos` to a `Voting` module, whose history variable is already
   written (§1.1); keeping the proofs' flip-test outcomes as evidence (§4.1).

## 1. Refinement and composition

| Concept | Standing | Evidence |
|---|---|---|
| Refinement mapping | Absent in TLA+; partial in Lean | 0 `INSTANCE` in the corpus |
| History, prophecy, stuttering variables | History variables only, used for instrumentation | ghost variables in most modules; no prophecy or stuttering variables |
| Assume-guarantee | Absent | 0 `-+->`; contracts appear at the record level only |
| Temporal existential quantification | Absent | 0 `\EE` |

### 1.1 Refinement mapping

No module instantiates another. What the corpus calls refinement takes three other forms:

- **Projected invariants over replayed traces.** `spec/ConfinementRefinement.tla` extends `Mechanism.tla`, which
  replays recorded traces of the reference, and checks four predicates over the projected state. Its header gives
  the correspondence in a table, but no `Confinement_A1` instance is formed and no `L => H` is stated. Trace
  validation is, in the corpus's words, "stage one of a refinement" (`Paxos.tla` header).
- **`SpecL => Spec`** in the two liveness proof modules. `NextL` is the extended module's `Next`, restricted under
  the new mutations, over the same variables. It is a refinement in the trivial sense, by an identity mapping.
- **Lean.** `mechanism/lean/Topak/SeatsModel.lean` proves a model of `State::apply` refines `Seats` at the module's
  constants, `FloorRefinement.lean` proves the admit decision a `Decide` step of `FloorComposition`, and
  `CouplingModel.lean` refines `SeatsModel` by definition (`proof-method.md` §5b). These are real refinements, of
  re-encodings, with the encoding's fidelity as a premise.

The skill's "When NOT to Use" puts refinement mappings out of scope ("a refinement proof is a different and harder
job"), and the 11.04 options paper lists "`Mechanism.tla` against `Seats`, `Lease_A1` and `Coupling` by refinement
mapping at small constants" as its step 2, not yet built.

**A natural first target.** `Paxos.tla` keeps a ghost `votes`, "the `Voting` layer's `votes`, as voting.rs keeps
it", and states `Voting`'s invariants (`OneValuePerBallot`, `ChosenUnique`) directly on the message-level model.
That is the layering of Lamport's Paxos → Voting → Consensus, with the history variable the mapping needs already
written. A small `Voting.tla` and `V == INSTANCE Voting WITH votes <- ..., maxBal <- ...`, checked by TLC as
`PROPERTY V!Spec` at the constants `Paxos-rows.txt` already uses, would be the corpus's first TLA+ refinement and
would replace two directly stated invariants with a theorem about a layer. `Paxos` has no proof module, so nothing
frozen is disturbed.

### 1.2 Auxiliary variables

Ghost variables are pervasive and well understood: `acted`, `bgDid`, `findings`, the write-once flags, and
`Paxos`'s `votes`, `learned`, `handed`, `assigned`, `duped`. `proof-method.md` §5 names monotone ghost variables as
the main reason the proofs were cheap. They are history variables in the strict sense, but they serve to
instrument properties, not to build a mapping.

No prophecy or stuttering variable appears, and none is yet needed, since there is no mapping to build. Each will be
needed when a mapping is attempted where the lower level takes several steps for one abstract step, or commits later
than the abstract one. `Mechanism.tla` against the small modules is the likely first place.

### 1.3 Assume-guarantee

No module is written as an open system with an environment assumption. Composition properties are stated as single
closed modules: `NonComposition` and `FloorComposition` model the composed system whole. Assume-guarantee contracts appear at the level of records, in
`derived/topak-specification-graph-2026.11.06.md`, which maps decision records' givens and guarantees onto
Benveniste et al.'s contracts. No TLA+ statement carries them.

This is a design choice with a cost. Each of the 41 modules is proved alone, and the claim that they hold together
in one deployment is argued in the records, not proved. The command-chain overlay of 2026.11.10 (`Federation`,
`Membership`, `Peer` and five more) is the first set of modules that share a chain of concepts, and would be the
place to try an assume-guarantee statement, or to write down why closed modules suffice.

### 1.4 Hiding

`\EE` occurs nowhere. Every `Spec` exposes its ghost state. For invariants that is harmless. For refinement it is
not: a high-level spec whose ghost variables are visible cannot be implemented by a low-level spec that lacks them,
so hiding becomes necessary at the first mapping where internal state differs between levels.

## 2. Advanced temporal logic and liveness

| Concept | Standing | Evidence |
|---|---|---|
| Machine closure | Strong | fairness only on actions of `Next`, with the reason written; a row per fair spec showing it has a behaviour |
| Well-founded induction | Not yet practiced | 0 `~>` in proof modules; Coupling's four leads-to properties owed |
| `ENABLED`, `ExpandENABLED` | Strong | 23 `ExpandENABLED`; `ENABLED` invariants as state lemmas |
| Weak versus strong fairness | Strong in the reasoning; the proof cost not yet met | rows showing the weaker choices fail |

### 2.1 Machine closure

`proof-method.md` §5c and the skill's rule table state the discipline: fairness only as `WF` or `SF` on actions of
`Next`, named for whose obligation it is, never as a condition on states, "a state condition is not machine-closed
and can leave an empty spec under which everything holds". Every fair spec has a row showing it has a behaviour.
This is the concept as the question states it, applied, and with the failure it guards against named.

### 2.2 Well-founded induction

No leads-to property is proved. `Coupling_live.tla` states four (`AdmitStallEnds`, `GrantStallEnds`,
`AdmitsResume`, `NextRoundGranted`) under `WF` and `SF` on named actions, and TLC checks them at small constants
(`Coupling_live-rows.txt`: `K` in 0..2, `R` 3 or 4, `MaxRound` 2 or 3). `Coupling_live_proof.tla` proves
`SpecL => Spec` and says the four are owed. The Lean packages have no behaviours, `WF` or `SF` yet.

The method knows the shape. The skill's `proof-style.md` gives "a measure, WF1 and induction": a `Nat`-valued
measure, one `WF1` step that lowers it, and induction over a local `G(n)` hidden outside `PTL` steps. The example is
an external proof (`TicTacToe_proof.tla`), not one of the corpus's. The skill also records where the shape stops: a
leads-to quantified inside its temporal body needs a quantified leads-to hypothesis that `PTL` cannot combine from
instances, and the corpus's rule for avoiding tlapm's translation defect forbids the obvious workaround.

**What appears within reach.** `AdmitStallEnds` and `GrantStallEnds` are unquantified, which is the condition under
which the documented shape works. The measure for the first is the one `proof-method.md` §5c names, the unread
backlog `seq - mark[round]` with the Observer's lease, with `K >= 1` as a hypothesis. Both have `ENABLED` in the
consequent, which has to be expanded in the step that proves it, as the corpus's `ENABLED` invariants already are.
`AdmitsResume` and `NextRoundGranted` are quantified over `n` and `r`; for them the skill's own advice applies:
prove them in Lean, or restate them one instance at a time.

### 2.3 `ENABLED` and `ExpandENABLED`

This is a strength. `ExpandENABLED` occurs 23 times; `ENABLED` invariants (`ConsultNeverCoupled`,
`EmergencyNeverCoupled`, `ReleaseNeverCoupled`, `Alone`'s `LocalNeverWaits`) are proved as state lemmas
`BY ExpandENABLED, Isa` and lifted by `PTL`, which is the strongest form a "the mechanism never gates this" claim
can take. Mutation lemmas are stated as `ENABLED` facts where a mutation enables an action. Probing `ENABLED` under
binders is how the first of tlapm's two unsound cases was found (§4.4). In Lean, the `ENABLED` encodings are checked
against TLC's state graphs (`spec/lean/graph-check-emergency.sh`), since an `ENABLED` theorem over a laxer encoding
could be proved and false.

### 2.4 Weak versus strong fairness

The choices are argued and tested. `SF` on `KeepUp` because the Observer's lease may end first; `SF` on `Admit`;
`WF` on the grants. Each weaker choice has a row that fails: `SpecWFKeepUp` (weak fairness on keeping up fails once
leases turn over), `SpecAnyBeat` (fairness on any heartbeat fails even strong), `SpecWFAdmit`. Each condition has a
row that drops it and breaks a property. What has not been met is the proof-side cost: `SF1` over `WF1`, and the
`[]<>ENABLED` premise it carries, will arrive with the first leads-to proof that needs `ThinkerAsks` or
`ObserverKeepsUp`.

## 3. TLAPS proof engineering

| Concept | Standing | Evidence |
|---|---|---|
| Inductive invariant strengthening | The core of the practice | named patterns in `proof-method.md` §3 |
| Backend orchestration | Light on tactics; route accounting and certification instead | 203 `PTL`; explicit `Isa` on 9 lines, all `ExpandENABLED` steps; 13,622 obligations accounted by route |
| Context hygiene | Weak | 0 `ONLY`, 0 `USE`, 5 `HIDE` |
| Opaque definitions, `BY DEF` | Good at the leaves; hiding by default not adopted | narrow `DEF` lists at leaf steps |
| `PICK`, `WITNESS` | Adequate | 100 `PICK`, 1 `WITNESS`, with a documented workaround |

### 3.1 Inductive invariant strengthening

This is what the practice is about. `proof-method.md` §2 requires deciding the inductive invariant before writing
the proof, and §3 names the patterns found: flag invariants; append-only record sets, whose auxiliary invariant is
the guard's precondition as a state fact; a type invariant proved once under every mutation; generation binding
(Confinement's six conditional clauses carrying history set three actions earlier); arithmetic invariants in layers
(Coupling's five clauses, `RunCoupling`'s one more); established and frozen at a commit point; and invariants
stated over every lease rather than the live ones, because a regrant revives a lease the stated property is silent
about.

`proof-method.md` §5 records the caveat itself: most properties were stated as flags or over append-only sets
precisely so they would be inductive, and TLC had already confirmed each at small constants, so no conjecture
turned out false. The strengthening was real where the property was not flag-shaped (Confinement, Coupling,
`Outstanding`, `Mesh`), and the method note says so.

### 3.2 Backend orchestration

Steps mostly go to the default SMT backend. Explicit backend directives are rare: `Isa` appears on nine lines, every
one of them a `BY ExpandENABLED, Isa` step, and `Zenon` in no step outside comments; `PTL` appears 203 times, at
the temporal step of each theorem. Tactical orchestration has not been needed, because the obligations are shallow
and `proof-method.md` §4 records that cost "scales with actions times invariant clauses, not with reasoning".

The corpus spent the effort on the answers instead. `spec/proof-cert.sh` re-runs every proof with `spec/smt-checked`
in place of Z3: cvc5 1.4.0 with proof production, an `unsat` forwarded only when ethos accepts a proof of false.
Zenon's proofs are checked by Isabelle (`-C`), and every obligation is accounted for by its route. That work found
that `-C` does not check SMT obligations at all, contrary to ADR-0046's open obligation as first written
(`proof-method.md` §5a). Across the 34 proof modules' newest certified runs, 13,622 obligations are accounted for and
197 rest on LS4. Three modules do not certify: `Confinement` and `Confinement_A1` (three steps Z3 proves and cvc5
does not) and `RulesFloorNV_rev5` (Zenon proofs Isabelle refuses). The Lean re-encodings prove their theorems with
every step kernel-checked.

### 3.3 Context hygiene

`ONLY` and `USE` do not occur. `HIDE` occurs five times, in `Federation_proof`, `Membership_proof` and
`Peer_proof`, all of 2026.11.10. Facts are cited explicitly (`BY <1>0, <2>4 DEF InvH`), so each step's
context is narrow in what it adds, but nothing is removed from it.

It has not cost anything yet: Confinement's 502 obligations prove in about eleven seconds. Two proofs are now large,
`Outstanding_proof.tla` at 1,781 lines and `Mesh_proof.tla` at 1,734, and they are where an upstream change would
first produce solver timeouts. The corpus's protection against upstream change is a different one: a base module
cited by digest is frozen, and a change is a successor module with its own proof (`proof-method.md` §6). That
removes the problem `BY ONLY` addresses for frozen modules, and leaves it for modules still Proposed.

### 3.4 Opaque definitions and `BY DEF`

Definitions are expanded at the leaves, by name and narrowly (`DEF PUnmarked`, `DEF CA`, `DEF HonestBound,
EffCharge`), and a large `LET` is named part by part so a step can expand one part (`Labels_proof`'s `Actuate`).
That is the discipline the concept describes. Hiding by default, with definitions exposed only where needed, is
not adopted.

`HIDE DEF` has a second use here that the concept does not name: soundness. `proof-certification.md` §10 requires
that a definition containing `ENABLED`, `\cdot` or a temporal formula be hidden in every step a backend other than
LS4 discharges, because tlapm abstracts such a term to a constant that drops variables bound around it. The newest
modules' `HIDE`s are of this kind. A module-level `HIDE DEF` with explicit re-exposure in the two large proofs would
serve both purposes at once.

### 3.5 `PICK` and `WITNESS`

`PICK` is used routinely (100 occurrences). `WITNESS` is used once (`PlaneClock_proof.tla`, line 79), because a
`WITNESS` step takes no `DEF` and cannot show a record is in a record set; `proof-method.md` §4 records the
workaround, `DEFINE w == ...`, prove `w \in S` and the property as two steps, and let the QED find the witness.
Existential introduction is otherwise done by `ExpandENABLED` and by explicit witness records in the lemmas that
replace a module's unnamed `ASSUME`s (`RulesFloorNV_rev5`'s "why dropping must fail" witnesses).

## 4. Specification hygiene and meta-verification

| Concept | Standing | Evidence |
|---|---|---|
| Vacuity guards | Strong, with one gap | `Never…` witnesses, empty-behaviour rows, `deadlock-audit.sh`, `flip_test.py` |
| Witness traces | Exemplary | 116 `Never…` definitions, each required `VIOLATED` |
| Mutation testing | The organizing principle; hand-picked | 35 of 41 modules declare a `Mut` switch |
| Trusted base, `AXIOM`, `OMITTED` | Exceptional | 0 `AXIOM`, 0 `OMITTED`; T-0045-31; two upstream reports |

### 4.1 Vacuity guards

Every check the concept names is present. `Init` and reachability: every reachability claim has a `Never…` witness
that must be violated. Deadlock: `-deadlock` is on by default, and `deadlock-audit.sh` asks the converse question of
every module, finding each state with no successor at a bound the module imposes (`deadlock-audit-results-2026.11.10.txt`).
Fair specs: each has a row showing it has a behaviour. Antecedents: a module's unnamed `ASSUME`s are re-proved as
named lemmas, and constant assumptions are kept to well-formedness (`K \in Nat`, `Active \subseteq AllEntries`),
which TLC checks against each configuration. Proofs: `proof-method.md` §2 step 9 and the skill's `flip_test.py`
flip one hypothesis to the mutation it excludes and require the proof to fail in a statement that carried it.

**The gap.** The flip test's outcomes are not kept: "a mutated proof is not an artefact", and "the failing count is
in the session, not in the corpus". The mutation rows that show the specification discriminates are dated results
files; the evidence that each proof discriminates is not. A section in each proof results file giving, per
hypothesis flipped, the count of failed obligations and the statements they fell in would make it evidence of the
same kind, without committing a mutated proof.

### 4.2 Witness traces

This is the corpus's convention exactly: 116 `Never…` definitions across the specification modules, each run as an
invariant that must come back `VIOLATED`, so that TLC produces the trace that shows the path is reachable.

### 4.3 Mutation testing

Mutation is the organizing principle of the specification layer. Thirty-five of the 41 specification modules
declare one `Mut` switch with one guard per mutation; the six without are trace replays (`Mechanism`, `PaxosTrace`,
`ConfinementRefinement`) and the rules-floor family, whose proofs take floor entries in force as hypotheses in place
of mutations. Every mutation must produce a counterexample on the property it targets. Each proof module carries one
lemma per mutation stating the guard it removes, and each theorem takes as hypothesis only the mutations that break
it. That practice corrected the premise table's "Breaks under" column four times and its parameter column once
(`proof-method.md` §1). `Coupling_live`'s `M_HBLIVE` and `Emergency_live`'s `M_EMCOUPLE2` reach every state the
unmutated module reaches, so no invariant detects them; only the liveness properties and the `ENABLED` invariants do.

**The limit.** The mutations are hand-picked: each is a guard its author thought to remove. A generated pass that
drops each conjunct of each action's guard in turn, and reports which survive every property, would show whether
an invariant depends on a guard nobody mutated, or whether a guard is redundant.

### 4.4 Trusted base

No proof module uses `AXIOM` or `OMITTED`. `OBVIOUS` occurs 100 times, and every obligation, `OBVIOUS` or not, is
accounted for by route in the certified results. The prover is a trusted-base row of its own (T-0045-31, ADR-0046
§3). Beyond that:

- **Two unsound cases in tlapm 7824dab's translation**, each demonstrated by false statements that prove and
  certify (`proof-certification.md` §8): a term the prover does not translate drops variables bound around it; and
  terms are named by 20 bits of an unchecked hash of a print that does not tell a bound variable from a constant, so
  two terms can share one name, by collision or by capture. Both are reported upstream (tlaplus/tlapm#309 and #310;
  ADR-0046 A3).
- **`spec/proof-scan.sh`** re-runs every proof module over a copy with every identifier renamed, compares each
  backend's inputs pair by pair, and reads every obligation for a capture.
- **A second derivation in Lean** for fifteen of the proof modules (`proof-certification.md` §8), in which the step LS4 carries in
  TLAPS is an induction the kernel checks; every Lean results file ends with a `leanchecker` replay, after a control
  showed that `#print axioms` misses a `False` added with the kernel check switched off.

What stays trusted is listed in `proof-certification.md` §8 and §12: LS4, for 197 temporal steps; tlapm's
normalization and translation; ethos and its signature; Isabelle; and, for a Lean result, the encoding's fidelity to
the module.

## 5. What would move the most, in order

1. **Prove `AdmitStallEnds` and `GrantStallEnds`** with the skill's measure-and-`WF1` shape, `K >= 1` as a
   hypothesis of the first. They are unquantified, so the shape fits, and the result would be the corpus's first
   proved liveness property. Route `AdmitsResume` and `NextRoundGranted` to Lean, or state them per instance.
2. **Write `Voting.tla` and check `Paxos` refines it** by `INSTANCE ... WITH`, TLC first. It exercises a mapping
   with a history variable already present, touches no frozen module, and turns two directly stated invariants into
   a layering theorem. Then the 11.04 paper's step 2, `Mechanism` against `Seats`, `Lease_A1` and `Coupling`, where
   stuttering and hiding will first be needed.
3. **Keep the flip-test outcomes** in each proof results file, so that a proof's non-vacuity is evidence in the
   corpus as a mutation row is.
4. **Generate guard-dropping mutations** beside the hand-picked `Mut` set, and report the survivors.
5. **An assume-guarantee experiment on the command-chain overlay**, or a written reason why closed modules suffice
   there.
6. **Module-level `HIDE DEF` in `Outstanding_proof` and `Mesh_proof`**, with re-exposure at the leaves, serving
   both solver load and the translation rule of `proof-certification.md` §10.
7. **The LS4 residual**: the small Isabelle-proved temporal lemma library `proof-certification.md` §12 proposes, or
   the Lean route extended to the remaining proof modules.

The pattern across all four groups is the one `proof-method.md` §5 already names. The practice made safety proofs
cheap by stating properties so that they are inductive and by leaving refinement and liveness out, and then examined
those proofs more thoroughly than is usual. The concepts it has not taken up are the ones it left out.
