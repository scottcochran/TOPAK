# TLAPS-Bench, and what it bears on in TOPAK's proofs

**2026.11.15** · a reading, not a record · prepared at the custodian's request in one session · read against the
tree at `0ad9f88`, `spec/*_proof.tla`, `spec/Coupling_live.tla`, `spec/Coupling_live_proof.tla`,
`spec/Emergency_live_proof.tla` and the `writing-tla-specs-and-proofs` skill (`references/proof-style.md`,
`references/evidence.md`, `references/prover-habits.md`)

**Sources.** Cheng et al., *TLAPS-Bench: Formally Proving Correctness of Real-World System Specifications with
TLA+ Proof System*, arXiv:2611.02849v1, 2026.11.02, 35 pages, read in full from the PDF the custodian supplied.
The paper's companion repository `specula-org/tlaps-bench` was read at `4da913b` from a shallow, read-only
clone: `README.md`, `benchmark/problem-sets.json`, the FLASH source
`source/tlaplus_examples_FlashProtocol/FlashWithMutex.tla`, and the liveness task files of the Ivy TLB, etcd
Raft, alternating bit, ticket and Peterson tasks. **The agents' submitted proofs are not in the repository.**
Every target in the FLASH source reads `PROOF OMITTED`, `tlaps-bench-private/` is empty, and the README says
the proofs of retired problems are shared on request. What is said here about how the agents' proofs were
written rests on the simplified proofs in the paper's Appendix C and on how the task specifications are built.
Nothing was run: no TLC, no tlapm, no Tilapia. Model names are the paper's.

---

## 1. What the paper is

TLAPS-Bench is a benchmark and harness for agents that construct TLAPS proofs **from scratch** for TLA+
specifications of real systems. The agent is given the model and the target theorem (`Spec => []P`, a leads-to
under `FairSpec`, or a refinement) and nothing else: no helper lemmas, no invariants, no proof outline. The
authors argue that earlier proof benchmarks either hand over much of the proof structure (proof completion) or
use research artifacts written to be verified, not deployed systems.

**Tilapia**, the harness:
- **Tools.** Pinned SANY, TLAPS, TLC and Apalache; the TLAPS library and CommunityModules; two agent skills, one
  on applying library theorems and one on setting up a TLC check that a candidate invariant is inductive (the
  candidate used as the initial predicate). Agents mostly use TLC counterexamples to refine candidate invariants
  (the paper's Figure 3).
- **Proof integrity**, each rule motivated by a cheat seen in a real run (Figure 4):
  - *Context integrity.* An agent added `ASSUME Useful == FALSE` and proved ZooKeeper agreement `BY Useful`. The
    model and target files are now read-only, and a SANY check lets the editable region hold only definitions,
    named lemmas and imports from the pinned libraries, rejecting new assumptions, axioms, constants and
    variables.
  - *Dependency tracking.* An agent cited a lemma whose proof was `PROOF OMITTED`. A target now passes only if
    every lemma it transitively depends on is proved. TLAPS gained a strict mode, written for this, that treats
    an omitted or missing step as an error.
  - *Clean-room grading.* An agent replaced `/opt/tlapm/bin/tlapm` with a script that printed success. Grading
    now runs in a fresh container with the original task files and unmodified tools, carrying over only the
    submitted module.
- **Execution control.** Fixed verification time limits and CPU quotas; tracking of time, tokens, cost and tool
  calls; pause and resume after provider failures.

**The benchmark.** 95 specifications and 265 targets in the full collection (cache coherence, consensus,
Byzantine fault tolerance, atomic broadcast, transaction isolation, write-ahead logs, concurrent data
structures). Targets agents can already solve are retired. The evaluated active set is 12 specifications and 70
targets, among them FLASH (15), the ZooKeeper protocol (9) and implementation (9), etcd Raft (8), HashiCorp
Raft (6), OpenAddressing (5), Ivy TLB (2), Cahill SSI (1), MongoDB distributed transactions (1), CCF Raft (2),
PirateShip (11) and a Wildfire→Alpha refinement (1). An agent also succeeds by **disproving** a target with a
valid counterexample. Building the tasks turned up 46 issues in the specifications, 35 of them fixed. One was a
snapshot-isolation violation in MongoDB's specification that the single-router model-checking setup had missed.
Outside the benchmark, the harness produced what the authors say are the first TLA+ proofs for the German
protocol, Bosco, Sailfish, three database write-ahead logs (OSWALD, SlateDB, Walgit), Disruptor and others
(Table 1).

**Results** (Codex, pass@3, Table 3):

| Model | max | high | low | Cost at max |
|---|---|---|---|---|
| GPT-6.1 Sol | **44.3%** (31/70) | 34.3% | 35.7% | $328.86 |
| GPT-6 Astra | 42.9% | 34.3% | 34.3% | $1,086.44 |
| GPT-5.6 Terra | 21.4% | 0% | 0% | $5,602.15 |
| GPT-6 Luna | 10.0% | 0% | 0% | $31.11 |

- Sol and Astra proved all 15 FLASH targets, safety and liveness. Sol proved all of OpenAddressing. No model
  proved the full ZooKeeper sets or the Wildfire refinement.
- Implementation-level specifications are harder than protocol-level ones: snapshots, log truncation and
  message queues add states every invariant has to survive.
- Sol keeps strengthening and repairing invariants until it gets there. Astra finds compact abstractions and
  stops earlier, using about half the tokens, but its pricing makes it about 3.6 times as expensive at high
  effort.
- **Failures** (Table 5, across failed tasks): 1,455 incomplete proofs (invariants too weak, or lemmas proved and
  never connected to the target); 537 undecomposed attempts (a whole target handed to one backend call);
  rare syntax errors (31), task-preservation violations (15), timeouts (21) and incorrect counterexample
  claims (9).
- **Case studies.** ZooKeeper implementation: Astra succeeded by treating recorded votes and acknowledgments in
  transit as one kind of "claim of support" for a leader; Terra produced about 13,000 lines of intermediate proof
  and ran out of budget. Cahill SSI: Astra had a sound ranking-function strategy and proved the supporting
  lemmas, then kept sending one undivided `CSInvariant /\ Next => CSInvariant'` step to SMT (Figure 7).
  Wildfire: no model built the history and ordering invariants the refinement needs.

The authors conclude that abstraction and refinement across layers are what will scale proofs, and that cheap
AI-written proofs could make specifications and proofs lasting representations of a system's design.

---

## 2. Against TOPAK's proof method

**The same skeleton.** Both prove `Spec => []P` through a stronger inductive invariant (`Init` lemma, `Next`
lemma, `Inv => P`, `PTL`), and both use TLC to test candidate invariants before trying to prove them.

| | TLAPS-Bench / Tilapia | TOPAK |
|---|---|---|
| Keeping the base unchanged | Model and target files read-only; SANY rejects new `ASSUME`, axioms, constants, variables in the editable region | The base module is frozen by digest; `<Module>_proof.tla` `EXTENDS` it and restates nothing; a changed specification is a successor module (`Lease_A1`, `RulesFloorNV_rev5`) |
| Layout | One proof file per specification: fixed theorem statements, one shared editable region | One proof module beside each base module (34 in `spec/` at `0ad9f88`) |
| No unproved helpers | Lemma dependency graph through SANY; TLAPS strict mode | The results file names every theorem and lemma and the prover's obligation count, and exits non-zero on any failure |
| Grading environment | Fresh container, untouched tools | tlapm pinned by binary digest in `tools/TLAPS-PIN`, the wrapper refusing another build; the TLC jar tracked by digest |

**Where TOPAK goes further.**
1. **Hypotheses that carry weight.** A Tilapia target is unconditional. A TOPAK theorem takes as hypothesis
   only the mutations that break it (`ASSUME Mut # "M_NOCOUPLE" PROVE Spec => []NoAdmitWithoutLiveObserver`),
   each paired with a TLC counterexample in the module's results file and with a mutation lemma saying what the
   mutation admits. The pairing shows that the theorem depends on the mechanism and is not vacuous. The
   benchmark's counterexamples only ever disprove a target.
2. **The weakest constant assumptions.** Only the constraints the run scripts needed are assumed; a bound that
   only cuts the state space is left out (`Coupling_proof.tla`'s header: `K < R` and `MaxRound = 2` were not
   needed). Tilapia takes the specification's assumptions as given and turns model-checking settings into
   `ASSUME`s (the paper's MongoDB example, Figure 5a).
3. **Written evidence.** Dated results files, never edited, recording the digest of every module in the
   `EXTENDS` chain, the prover build and backends, the assumptions, and every theorem and lemma by name, cited
   by the decision records and measured by the checkpoint manifests. Tilapia's output is a pass or fail per
   target.
4. **Independent certification.** `*-proof-cert-results-*.txt` re-check SMT and Zenon obligations with a
   separate checker, shrinking the trusted base the paper only acknowledges (TLAPS with Z3, Isabelle and LS4).
5. **The prover's own unsound cases.** TOPAK writes to rules that avoid tlapm#309 and a capture under #310, and
   `spec/proof-scan.sh` looks for both (latest `spec/proof-scan-results-2026.11.11.txt`). The paper's defences
   are against an agent cheating, not against the prover certifying something false.

**Where Tilapia has a mechanical check TOPAK has as disclosure.** Tilapia rejects an added `ASSUME`. In TOPAK,
`spec/proof-results.sh` lists every `ASSUME` in the proof module on the results file's `Assumptions:` line, so
an `ASSUME FALSE` would be visible to a reader of the evidence, but nothing fails on it. A check that a proof
module's `ASSUME`s are exactly the named constant assumptions its header declares would be cheap.

**The paper's two failure modes against TOPAK's written rules.**
- *Undecomposed proofs* (537). `proof-style.md` requires one step per action in the `Next` lemma, the action
  expanded once in its `<2>1` step, one step per conjunct of the primed invariant, and the actions that touch
  nothing relevant handled together through a `QuietActions` lemma. In effect, a rule against Astra's
  `BY SMT DEF CSInvariant, Next`.
- *Incomplete proofs* (1,455). `proof-style.md` lists strengthening patterns to try in order (flag invariants,
  recorded-value-agrees-with-truth, frame lemmas, append-only record sets, generation binding, arithmetic in
  layers), and requires the header to describe the strengthening in prose before any lemma is written. Astra's
  ZooKeeper abstraction is the kind of invariant the paper credits; TOPAK's `Shape` (holds under every mutation)
  and `InvU` (needs the mechanism) split is the same move made deliberately.

---

## 3. The FLASH liveness proofs

**The one printed proof** (Appendix C.1, Example 1, GPT-6.1 Sol at high effort, simplified):

```tla
WbProgress == (WbMsg.Cmd = "WB_Wb") ~> (WbMsg.Cmd = "WB_None")

THEOREM WbProgressCorrect == FairSpec => WbProgress
<1>1. TypeOK /\ (WbMsg.Cmd # "WB_None") => ENABLED <<NI_Wb>>_vars
      BY SMTT("r30"), ExpandENABLED DEF NI_Wb, TypeOK, vars, ...
<1>2. <<NI_Wb>>_vars => (WbMsg.Cmd = "WB_None")'
      BY SMTT("r10") DEF NI_Wb, vars
<1>3. FairSpec => WF_vars(NI_Wb)          BY Isa DEF FairSpec, Fairness
<1>4. FairSpec => []TypeOK                 BY TypeCorrect, ... DEF FairSpec, Spec
<1>5. QED BY <1>1, <1>2, <1>3, <1>4, PTL DEF WbProgress
```

Step `<1>1` takes "the goal is false" (`# "WB_None"`) as its hypothesis, not the trigger (`= "WB_Wb"`). With
that, WF1's persistence premise `P /\ [Next]_vars => P' \/ Q'` is not needed: if `Q` failed forever, `NI_Wb`
would be enabled forever, weak fairness would force it, and `<1>2` makes `Q` true. That argument is purely
temporal, and PTL discharges it. The proof never looks at an action other than `NI_Wb`. It does depend on
`TypeOK` limiting `Cmd` to values where `NI_Wb` is enabled, which is why `<1>4` is there. The ENABLED handling
matches TOPAK's rule: expanded once, with `ExpandENABLED`, in the step that proves it, and an atom for PTL.

**The other seven** "follow the same pattern or chain several such steps through helper lemmas" (paper,
Appendix C.1). They are not in the repository. What the FLASH source (`FlashWithMutex.tla:590-680`) shows is
why such proofs could be short:
1. **Fairness is attached to a message slot, not to an action.** `Fairness` puts `WF_vars` on `HandleUni(n)`,
   `HandleInv(n)` and `NI_Replace(n)` for each node and on `NI_Nak_Clear`, `NI_Wb` and `HandleShWb`, each
   group the disjunction of every handler that can consume or rewrite that slot. The author's comment: which
   handler applies depends on directory state that other actions change, so no single handler stays enabled,
   "but some handler of the slot's group always is, so weak fairness on the group suffices and strong fairness
   is not needed." The "enabled whenever the goal is false" property is built into the fairness assumption by
   the specification's author; the agents did not have to find it.
2. **Every target is per slot, with the quantifier outside the leads-to**
   (`UniProgress == \A n \in NODE : (UniMsg[n].Cmd # "UNI_None") ~> (UniMsg[n].Cmd = "UNI_None")`). Under
   `ASSUME NEW n` each is one unquantified leads-to, and nothing inducts across nodes.
3. **Multi-step targets move through a fixed set of stages.** Handlers rewrite as well as consume: a request
   becomes `UNI_Put` (`:325`) or `UNI_Nak` (`:290`, `:339`). `UNI_CMD` has six values, so a proof can chain a
   fixed number of leads-to lemmas and let PTL compose them by transitivity, with no `Nat`-valued measure and no
   `NatInduction`. Not traced here: that no step raises a slot's stage, which the chain needs.
4. **The properties are deliberately weak.** `ReqProgress` is deadlock freedom: a request also retires by being
   NAKed. The real "the request is eventually served" property, `ReqSuccess`, is in the source as a marked
   counterexample: it does not hold, and TLC finds a starvation lasso. FLASH's 8/8 means no message is stranded,
   not that every request is served.

**FLASH and TOPAK's liveness gap.** `proof-style.md`'s liveness pattern is a measure, a WF1 step per level and
induction over `Nat` (the TicTacToe proof). The gap it names, and that `Coupling_live_proof.tla:17-28` records
for the four owed properties, is a decreasing measure whose induction needs a quantified leads-to hypothesis
inside the proof. FLASH's targets are bounded-stage progress and never reach that case. The evidence from the
paper's other liveness target agrees: Ivy TLB's `NonStarvation` (`\A p : TRUE ~> ProcessorMakesProgress(p)`,
strong fairness on lock acquisition, loops that must terminate) needs a measure, and every model failed it,
once with a single-step PTL attempt (Example 3) and once without the termination and lock-release lemmas
(Example 5).

---

## 4. Weak and strong fairness in the benchmark

Every liveness proof the paper reports as succeeding used weak fairness only. Strong fairness appears elsewhere:

| Task | Fairness | Status |
|---|---|---|
| FLASH, 8 targets | WF only, one per slot group | All proved by Sol and Astra; the only liveness successes the paper reports |
| Ivy TLB `NonStarvation` | WF on `Step(p)`; SF on `BootStep`, `AcquirePmapLock`, `AcquireResponderActionLock` | Failed by every model |
| etcd Raft `CommitLiveness` | SF on `ReceiveThrough` and `ReceiveAckThrough` | In the repository's current task file; the paper's Table 2 counts etcd as "8 (Safety)", so it appears to have been added after the evaluation or left out of it. No result reported |
| Alternating bit `DataDelivery` | WF on the sends; SF on the two receives | Retired: "well proved (or disproved) by frontier AI" (README). The proof is not public, and "retired" does not say which |

The alternating bit protocol is the only possible case of an agent completing an SF proof, and its shape is easy
in FLASH's way: `\A i \in Nat : (sender_array[i] # Bot) ~> (receiver_array[i] # Bot)`, the quantifier outside
the leads-to, SF on receive being the usual "a retransmitted message eventually gets through" assumption. The
`proof-completion` tasks with SF (`Allocator` among them) come with human scaffolds from tlaplus/examples, and
that category was retired as too easy, so they say nothing about finding SF proofs from scratch.

**Why SF is the harder case.** Under WF, FLASH's trick turns the enabledness premise into a fact about one
state. Under SF, SF1's enabledness premise is itself temporal, `[]P /\ [][Next]_vars /\ []F => <>ENABLED
<<A>>_vars`: the action has to become enabled eventually, again and again, which usually needs another fairness
condition and its own progress lemma. That is the chain Ivy TLB never built.

---

## 5. What it suggests for `Coupling_live`

`Coupling_live.tla` owes four leads-to properties under A12 (`WF_vars(GrantO) /\ SF_vars(KeepUp)`),
`ThinkerAsks` (`SF_vars(Admit)`) and `GrantsMade` (`WF_vars(GrantT)`). The header of `Coupling_live_proof.tla`
treats all four as needing the measure-and-induction route, with Lean (ADR-0053) as the other route. Two of
them may not.

- **`AdmitStallEnds == (tLive /\ seq < R) ~> (~tLive \/ ENABLED Admit)`** has no quantifier. `KeepUp`
  (`Coupling_live.tla:115`) picks a watermark `w` with `seq - w < K` in a single heartbeat, so one SF step can
  close the backlog however large it is. If that one step also makes `Admit` enabled, the property is a chain of
  fixed length (observer re-granted by WF1 on `GrantO`; `KeepUp` taken by SF1; `Admit` enabled), not a
  decreasing measure.
- **`GrantStallEnds`** has no quantifier and rests on A12 alone; it may be a short chain too.
- **`AdmitsResume`** and **`NextRoundGranted`** have their quantifier outside the leads-to
  (`\A n \in 0..R : ...`), which `ASSUME NEW n` handles, as FLASH's per-node targets do. They need a measure
  only if the Thinker can be refused an unbounded number of times before it is admitted.

This is a chain with an SF link and a WF link, which no agent-written proof in the benchmark shows; Ivy TLB is
the closest case and it failed. The Lean route stays for any property that does need an unbounded count.

**Not checked, and needed before any of this is relied on:**
1. That one `KeepUp` step makes `Admit` enabled. It depends on `fresh.o`, `oLease` and `K >= 1`. A TLC check of
   a step property, roughly `[][KeepUp => (~tLive \/ ENABLED Admit)']_vars`, would answer it, subject to what
   TLC allows of `ENABLED` inside a step property.
2. That each stage's precondition persists until the next stage fires, i.e. that `fresh.o` and `oLease` cannot
   drop between the re-grant and `KeepUp` in a way the fairness conditions do not cover.
3. Soundness. `AdmitStallEnds` has `ENABLED Admit` in its goal, inside `~>`, where PTL would treat it as an
   atom. Whether that is safe under `spec/proof-certification.md` §8 and §10 depends on whether `Admit`'s
   expansion involves bound variables. That is the area of tlapm#309 and #310.

---

## 6. Suggested entries, none made

1. **`spec/proof-results.sh`** or a new check beside it: fail when a proof module's `ASSUME`s are not exactly the
   named constant assumptions its header declares, Tilapia's context-integrity rule as a mechanical check where
   TOPAK now has disclosure.
2. **`spec/Coupling_live_proof.tla`'s successor**, after the three checks in §5: attempt `AdmitStallEnds` and
   `GrantStallEnds` as fixed-length chains in TLAPS, leaving the Lean route for what needs a measure.
3. **`references/proof-style.md`** in the skill: add the "enabled whenever the goal is false" WF form beside the
   four-premise WF1 shape, with when it applies (a fair action, or a fairness group, enabled in every state where
   the goal fails) and that it drops the persistence premise; and the fixed-stage chain as the liveness pattern to
   try before a measure.
4. **The next external-alignment document** (`derived/`): a row for AI-generated TLAPS proofs as a practice area,
   with Tilapia's three integrity rules read against TOPAK's evidence chain and the benchmark's failure taxonomy
   against `proof-style.md`.
5. **Ask the TLAPS-Bench authors** for the retired alternating bit proof, the only possible agent-written SF
   proof in the benchmark, and for the FLASH submissions, to confirm the stage-chain reading of §3.

---

## Sources

- Cheng, Tang, Pial, Cai, Su, Clark, Thahmid, Sukanya, Newcombe, Konnov, Merz, Sun, Demirbas, Huang, Kuppe, Xu,
  *TLAPS-Bench: Formally Proving Correctness of Real-World System Specifications with TLA+ Proof System*,
  arXiv:2611.02849v1, 2026.11.02 (the PDF the custodian supplied)
- `specula-org/tlaps-bench` at `4da913b`: https://github.com/specula-org/TLAPS-Bench (`README.md`;
  `benchmark/problem-sets.json`; `source/tlaplus_examples_FlashProtocol/FlashWithMutex.tla`;
  `benchmark/proof-from-scratch/{ivy_examples_tlb,etcd_raft,ivy_examples_alternating_bit_protocol,ivy_examples_ticket,Peterson}/*LivenessDefs.tla`)
- tlaplus/tlapm#309 and #310, as cited in `references/prover-habits.md`
