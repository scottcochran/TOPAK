<!-- RECOVERED · HISTORICAL · 2026-09-15 · tranche 3 -->
> **Recovery note.** Source: TOPAK theory of operation assessment session 09.12 (https://claude.ai/chat/816fe6b6-9f6b-4f7b-ad08-06e5137d7a45), `create_file` turn 3, file `topak-external-assessment-2026.09.12.md`. No later edits.
>
> **Marked historical.** II.2 says "ADR-0006 crypto-shreds"; ADR-0003 rejects crypto-shredding, and erasure is sealed round-topic deletion plus ADR-0004 plaintext-store deletion. Corrected in the 09.15 checkpoint §9 and feature list; the MANAGE 2.4 contradiction stands on the correct mechanism. See also registry finding T3-3 (forensic-floor direction wording).
>
> Text below is verbatim from session history (HTML entities normalized). **Historical artifact:**
> nothing folds into it. Later corrections live in the records and checkpoints that supersede it.

# TOPAK — External Assessment

**2026.09.12** · assesses the Theory of Operation checkpoint of the same date · *The Gripping Hand*

Two external references:

- **Moon & Varshney**, *Containment Verification: AI Safety Guarantees Independent of Alignment*,
  arXiv:2605.09045v2 [cs.AI], 29 Jun 2026. Published at the Second Workshop on Agents in the Wild
  (AIWILD) at ICML 2026. Royce Moon (Enclave Intelligence), Lav R. Varshney (AI Innovation
  Institute, Stony Brook). **Name correction:** the checkpoint and draft article should read
  *Varshney*, not *Varney*.
- **NIST**, *AI Risk Management Framework Playbook* (AI RMF 1.0 companion), 142 pp.

**Verdict in one line.** TOPAK is well aligned with Moon & Varshney on the core move and has one
genuine extension of it; it is citing the wrong section for its central threat and has inherited a
gap the paper explicitly proves exists. Against the Playbook it is strong in MANAGE, partial in
GOVERN, and essentially absent from MAP and MEASURE — with one outright contradiction.

---

## Part I — Against Moon & Varshney

### I.1 Concordances (state these as concordance, not as originality)

| TOPAK | Paper | Note |
|---|---|---|
| "Agents are unverifiable in principle; verify the cage, not the occupant" | Havoc oracle semantics (§2, Listing 1) | Same construction. The paper models the AI as a Dafny method with an empty body whose return value ranges over the entire `Action` type. |
| `Contain` | The containment layer (agentic framework) | Same object. Their witness is PocketFlow. |
| ADR-0007, semantic judgment is never a lift | Boundary-enforceable property class (§1) | Predicates over typed action, modeled boundary event, action arguments, and state, with no reliance on the natural-language semantics of the AI's reasoning. TOPAK derived the same line independently. |
| §4 scope correction: `Contain` enforces the syntactic envelope only; semantics is Observer detection | Containment-level vs oracle-level split (§5) | Content-level properties (truthfulness, non-deception, persuasion resistance) are out of scope *by design* in both. |
| Typed action alphabet, totality extraction | "Narrowness of the action interface determines the strength of the guarantee" (§5) | Their formulation is publishable ammunition for ADR-0007: a narrow typed enum yields a strong guarantee; a generic shell or `eval` primitive collapses the guarantee onto the primitive. |
| Trusting-trust regress terminating on one verified artifact | Trusted base (§3.4) | Same move, different scope. See I.6. |

The article should cite the concordance explicitly. Independent arrival at the same boundary from a
distributed-systems starting point is a stronger claim than novelty would be, and it is defensible.

### I.2 Where TOPAK genuinely extends the paper — ADR-0010

The paper verifies a **concrete** boundary policy ΠI over a fixed four-variant action interface:

```
datatype Action =
  | NoAction
  | ReadPathAction(path: string)
  | ToolCallAction(tool: string)
  | StepAction
```

with three induced state invariants (reads under the workspace root, tool calls allowlisted, step
counter bounded). In the 09.12 checkpoint's own vocabulary, **that is the pure-inclusion option**.
The paper gets the absolute result and pays the price the checkpoint identified: the theorem is about
that ΠI, and every policy edit invalidates it.

**The paper never addresses policy change cadence.** There is no discussion of what happens when the
allowlist changes at incident cadence while the mechanism changes at release cadence. ADR-0010's
minimal floor plus `bundle ⊑ floor` refinement is a parameterization of their result that they do not
have, and the rate-mismatch argument is the reason it is needed.

**This is the contribution to lead with.** Framed against the paper it is a clean delta: *they proved
soundness for a fixed policy; TOPAK shows how to keep that soundness under a policy that changes
faster than the verified artifact.*

### I.3 Exposure 1 — the §4.2 citation is wrong

The checkpoint cites **§4.2** in three places for the "vacuously true predicate sails through green
gates" failure, including the §2 rationale for ADR-0010 and the §1 claim that Moon & Varshney §4.2 is
now a threat inside Build.

§4.2 is the **seven-phase agentic specification synthesis pipeline**. It is infrastructure, not a
failure mode.

The failure being described is **§4.6 (the ablation) with the worked diff in Appendix B**. The
schema-mismatch result: when the trusted property template's `Variables` schema has no field
corresponding to a witness Flow's privileged effect, the no-barrier mode (with implementation access)
recognizes the mismatch and **silently abstains** — it writes `v'.tool_calls == v.tool_calls` at every
node, and the `ToolAllowlisted` corollary then quantifies over an always-empty sequence and is
vacuously true along every reachable state.

Correct citation form for the article: *Moon & Varshney §4.6 and Appendix B*, with §5.1 (*Template
fitness*) for the limitation statement.

A reviewer who knows the paper will catch the mispointer, and it sits under the load-bearing rationale
of ADR-0010.

### I.4 Exposure 2 — the three gates do not protect the floor (highest-value finding)

This is the substantive consequence of I.3, and it is worse than the citation error.

The paper's three-gate validation (§4.4), adapted from IronSpec:

- **(G1) Resolution** — synthesized Dafny parses and type-checks within a 30s timeout.
- **(G2) Vacuity** — a permissive-stub proof variant, invariant gutted to well-formedness alone and
  lemma bodies emptied, must *fail* verification.
- **(G3) Discrimination** — an LLM-generated plausible modeling error inside the proof file must also
  *fail* verification.

**Appendix B.3 reports that both the barrier and no-barrier bundles pass all three gates**, including
the no-barrier bundle whose safety predicate is vacuously discharged. The gates audit the
protocol-invariant portion of the proof, not whether each conjunct of the safety predicate is
non-vacuously discharged. The paper's own conclusion: *the gates are necessary but not sufficient for
specification quality, and an additional template fitness check is needed to catch silent abstention.*

ADR-0007, as ratified on 09.12, extends **totality, non-vacuity and discrimination gates to the floor
itself**, and the checkpoint §2 calls that extension "the only thing standing between TOPAK and its
own §4.2."

**Those are the same three gates the paper just demonstrated a vacuous specification can pass.** The
extension is necessary and insufficient, by a published result, on the exact failure mode TOPAK cites
as its widest-blast-radius silent failure.

**What is needed: a fourth gate — floor fitness.** Stated in TOPAK's vocabulary:

> For every privileged effect reachable through the extracted action alphabet, the floor's variable
> schema contains a field that models it. No effect may be discharged by abstention.

Properties of this obligation:

- It is decidable under ADR-0007's syntactic-lift discipline, for the same reason `bundle ⊑ floor` is:
  the action alphabet is finite and totally extracted.
- It is a **Build obligation**, alongside the refinement check, which is consistent with ADR-0010's
  placement argument.
- **It currently has no owner.** ADR-0014 (floor authorship and change control) is the natural home,
  since "does the floor cover the alphabet" is adjacent to "who may change the floor." Alternatively a
  new ADR-0016.

Note the structural resonance worth using in the article: a vacuous floor admits every bundle and
discharges every containment property over nothing, *invisibly*. That is the same shape as the
paper's silent abstention. TOPAK and the paper found the same failure at different layers.

### I.5 Exposure 3 — the sandbox gap is the paper's gift, not TOPAK's embarrassment

Checkpoint §5 concedes: "TOPAK has a containment *claim* and no containment *mechanism*."

The paper hands over the vocabulary to convert that into a scoping statement. §5.1, *Effect
exclusivity*:

> The deployed guarantee requires every agent-accessible external effect to pass through the verified
> typed action boundary. Direct Python calls, foreign-function interfaces, ambient filesystem or
> network access, concurrency effects, runtime bugs, kernel vulnerabilities, and hardware faults are
> outside the theorem unless mediated by that boundary.

And Figure 1 gives the stack, layer by layer:

| Layer | Status |
|---|---|
| AI model | Modeled as havoc oracle |
| **Containment layer** (agentic framework) | **Formally verified** |
| Sandbox (Bubblewrap, Firecracker, Docker, Podman) | Operationally audited |
| Host kernel / hypervisor | Operationally audited |
| Hardware | Operationally audited |

TOPAK occupies the containment-layer row. Everything below it is out of scope in the same way and for
the same reason it is out of scope for the paper, which recommends layering: containment verification
prevents forbidden effects at the agent boundary, sandboxing limits damage from bugs or bypasses below
it. The paper also cites the Copy Fail Linux privilege-escalation disclosure (Xint Code Research Team,
2026) as the empirical case for why the lower rows are audited rather than verified.

**This is the highest-value, lowest-cost move available.** Adopt Figure 1's stack as a positioning
diagram, state TOPAK's row, and the open item stops being a hole and becomes a declared boundary with
a citation behind it. It also partially discharges the article's need for the architecture diagram,
which has been on the open list since 09.11.

### I.6 Exposure 4 — `Contained`/`Mediated` cuts in the wrong place

Checkpoint §5 splits the theorem inventory as **safety properties over `Contained`, attribution and
authorization properties over both**.

The paper's structure suggests a cleaner cut. Effect exclusivity is not an assumption of Theorem 3.2.
It is the antecedent of **Corollary 3.3 (Deployed Boundary Safety)**:

> If every externally visible boundary effect of the deployed runtime is represented by some concrete
> event eI ∈ EI, then every externally visible boundary effect produced under any concrete oracle
> satisfies the concrete boundary policy ΠI.

Theorem 3.2 itself is a trace-refinement result over the shared action space, conditional only on
abstract havoc safety (A1) and boundary-event refinement (A2). It says nothing about effects outside
the modeled interface, so it survives a `Mediated` principal untouched.

**Recommended restatement:**

- **Theorem-level (3.2 analogue):** holds for every principal. Every *in-band* action is typed,
  policed, and emits only policy-compliant boundary events. `Contained(p)` and `Mediated(p)` alike.
- **Corollary-level (3.3 analogue):** holds for `Contained(p)` only. The antecedent is precisely
  effect exclusivity, which is false for humans by construction.

This gives back more than the safety/attribution split does. A `Mediated` human principal still gets
the full in-band guarantee, and what is lost is exactly and only the deployment-closure step. It also
gives the article a precise sentence for the uncomfortable §5 admission that human principals are
atomic and therefore less internally separated than agent principals: they are `Mediated`, so the
corollary never applied to them, and the four-way LTRO separation was never what was buying it.

### I.7 Missing section — the trusted base

The paper's §3.4 enumerates the trusted base after verification in one paragraph: the concrete
boundary policy ΠI, the abstraction and event relations R and Q, the effect-faithfulness boundary, the
Dafny verifier and compiler, and the small extern shim supplying arbitrary typed actions. Explicitly
**not** trusted: the AI model, prompting procedure, training process, action-selection strategy.

TOPAK has no equivalent section anywhere in the checkpoint series, and its trusted base is materially
larger. A first-pass enumeration, for drafting:

- The minimal policy floor (ADR-0010) and its fitness relative to the alphabet (I.4)
- The refinement checker discharging `bundle ⊑ floor`
- OPA's evaluation semantics, and the assumption that Rego evaluation is a pure local function
- The signing key at the Build promotion gate, and the human holding it
- Epoch fencing and lease-expiry mechanics
- Kafka's durability within the `acks=all` window (ADR-0005 having removed ordering and
  system-of-record status from the trusted set — worth noting as a *reduction*)
- Paxos liveness assumptions for the grant path
- The TLA+ toolchain
- The two floor exceptions (ADR-0006 erasure, ADR-0009 break-glass), pending ADR-0013

The paper's §3.4 is a short paragraph and it buys a great deal of reviewer credibility. This is cheap
to write and will be asked for.

### I.8 Method asymmetry worth resolving before borrowing their language

The paper uses **deductive verification in Dafny**: forward-simulation refinement, machine-checked,
universally quantified over the action type, with the Dafny compiler emitting Python from verified
source. Capability invariance follows immediately from havoc's quantification over every value of the
action type.

TOPAK says TLA+. If the containment properties are established by **TLC over a bounded configuration**,
they are not universally quantified in the paper's sense, and the checkpoint's phrasing — "containment
properties are proven absolutely against the floor" — claims more than the method delivers. If the
route is **TLAPS**, the claim holds and should say so.

Either answer is fine. What is not fine is borrowing the paper's absoluteness language without
declaring which one TOPAK is doing. Flagging this as an open item rather than a defect, since the
checkpoint does not record the answer either way.

---

## Part II — Against the NIST AI RMF Playbook

### II.0 Framing

The Playbook is explicit that it is **neither a checklist nor a set of steps to be followed in its
entirety**, and that its suggestions are voluntary. So the argument is not compliance.

The argument that works: **TOPAK makes several Playbook outcomes mechanically satisfiable rather than
procedurally attested.** Where the Playbook suggests establishing a protocol, TOPAK offers a
transition that cannot be omitted. That is a real claim, it is narrow, and it is defensible.

### II.1 Strong fits

**MANAGE 2.4 — supersede, disengage, deactivate.** The closest fit in the document. It asks for
mechanisms and assigned responsibilities to supersede, bypass or deactivate systems demonstrating
outcomes inconsistent with intended use, with incident thresholds for activating bypass, change
management for upstream and downstream consequences, and root-cause review of bypass events.

TOPAK's answer is stronger than the suggested actions in one specific respect: **lease expiry is a
passive e-stop requiring no human action at all.** Every Playbook suggestion here presumes someone
decides to act. Expiry-as-default-deny does not. That distinction is the single best governance beat
in the architecture and belongs in the article explicitly.

Also mapping here: eviction as the principal test (§1), epoch fencing, and e-stop-versus-break-glass
(unilateral and authority-subtracting versus quorum-witnessed and authority-granting).

**GOVERN 2.1 — roles, responsibilities, independent course-correction.** The Playbook asks for
policies that *separate management of AI system development functions from AI system testing
functions, to enable independent course-correction*, and names groupthink and sunk-cost bias as the
reason. ADR-0008 (Observer replicas not colocated with the Thinker, fault-domain independence) is the
architectural form of that organizational suggestion. The monoculture declaration and cross-family
Observer requirement from the 09.12 open list answer the groupthink concern almost verbatim, at the
model layer rather than the org-chart layer. Good article material: the Playbook's separation-of-duties
intuition, mechanized.

**MAP 3.3 — targeted application scope.** *"Systems that function in a narrow scope tend to enable
better mapping, measurement, and management of risks... A narrow application scope also helps ease TEVV
functions."* This is the governance-side statement of Moon & Varshney's *"a containment layer that
exposes a narrow typed enum yields a strong guarantee."* TOPAK's typed action alphabet satisfies both
at once, from two unrelated literatures. Three-way concordance; worth a short subsection.

**GOVERN 1.4 — documentation policies.** The suggested documentation list includes business
justification, scope and usages, expected and potential risks, **assumptions and limitations**,
evaluated alternative approaches, down- and up-stream dependencies, and plans for change management.
The ADR log is close to this artifact already, particularly on alternatives-considered and
assumptions. The 0011 tombstone convention (gaps in an ADR log are self-documenting; silent
renumbering breaks cross-references) is a documentation-integrity practice the Playbook implies but
does not state. Claim the ADR log as the GOVERN 1.4 deliverable.

**MEASURE 2.7 — security and resilience.** Suggested metrics include frequency and rate of anomalous
events, incident response times, and **time-to-bypass**. Red-team exercises to evaluate *potential
mismatches between claimed and actual system performance* is the operational analogue of the paper's
G3 discrimination gate. TOPAK has no metrics program; see II.3.

**GOVERN 1.5 — monitoring, incident response, appeal and override.** HOTL with a response budget maps
directly. See II.4 for why this is the strongest section available.

### II.2 One outright contradiction

**MANAGE 2.4 requires: "Preserve materials for forensic, regulatory, and legal review"** as a suggested
action on bypass or deactivation events, and asks organizations to conduct internal root-cause analysis
and process reviews of those events.

**ADR-0006 crypto-shreds.** ADR-0003's topic-per-principal-per-round scheme makes the round the unit of
erasure. Demand type 5 (hide that a record ever existed) goes further still, and per checkpoint §6 it
is now entangled with break-glass: a privileged path able to suppress an erasure record either closes
type 5 by an ugly route or opens a hole.

This is not a gap. It is a direct conflict between a ratified ADR and a named Playbook suggestion on
the *same* control (bypass and deactivation), and a governance reviewer will find it faster than a
systems reviewer will find the composition hole.

It lands in **ADR-0013**, which does not exist. ADR-0013's obligation list should gain a fifth item:

> **Forensic floor.** A bounded set of facts that survives erasure and break-glass, sufficient to
> support root-cause analysis of a bypass event. Otherwise erasure and the MANAGE 2.4 preservation
> requirement are mutually unsatisfiable.

Note the shape: this is a *floor* in exactly ADR-0010's sense, applied to retention rather than
authority, and it is monotone in the same direction (exceptions may preserve more, never less).
That symmetry is probably the cheapest route to a defensible answer, and it reuses machinery that is
already ratified.

### II.3 Coverage shape — TOPAK is a MANAGE architecture

| Function | TOPAK coverage |
|---|---|
| GOVERN | Partial. Strong on 1.4 (documentation), 1.5 (incident response), 2.1 (separation of duties). Silent on 1.1 (legal/regulatory), 3.x (workforce), 4.x (culture), 5.x (stakeholder engagement). |
| MAP | **Essentially none.** Context, intended purpose, affected individuals and communities, impact assessment, categorization. |
| MEASURE | **Near none**, with one hole that is not out of scope (II.5). |
| MANAGE | **Strong.** 1.3, 2.3, 2.4, 4.1 in particular. |

This is a legitimate scope, and the paper models how to declare it. Their Impact Statement is explicit:

> A verified containment layer is therefore not a complete safety solution. It is a fail safe for a
> specific class of harms, intended to compose with oracle-level methods, sandboxing, and statistical
> certification rather than replace any of them.

**The article needs the TOPAK-shaped equivalent of that paragraph.** Without it, a governance reader
arrives assuming TOPAK is an AI risk-management answer and leaves having found four functions' worth
of absence. With it, TOPAK is a mechanism that discharges a named subset of MANAGE and composes with
the rest. Same facts, opposite reception.

### II.4 The strongest available section — human oversight

The Playbook's human-oversight references (under the AI-oversight subcategory) include:

- **Ben Green**, *The Flaws of Policies Requiring Human Oversight of Government Algorithms*
- **Madeleine Clare Elish**, *Moral Crumple Zones: Cautionary Tales in Human-Robot Interaction*
- **Mary Cummings**, *Automation and Accountability in Decision Support System Interface Design*
- **Siebert et al.**, *Meaningful human control: actionable properties for AI system development*

Checkpoint §4 contains this line: *"HOTL without a response budget is decoration. An admin who may
intervene but is never required to is structurally the ignored first-officer warning."*

That is the moral-crumple-zone critique, independently derived, **with an answer attached** — `D` as a
human-response budget in `W < L < D`, and HITL derived as *unavailable* in Run rather than declined,
because no human fits inside a ~1s propagation window.

Citing Green and Elish and then answering them with `D` is the strongest paragraph available to the
article in this section, and it inoculates TOPAK against the most common objection to any architecture
with a human in a box on the diagram. The Siebert "meaningful human control" line is also the right
vocabulary for the HITL/HOTL/HOOTL trichotomy, which the Playbook does not itself supply.

### II.5 The MEASURE hole that is not out of scope

Declaring MAP and MEASURE out of scope is defensible for context, purpose, bias, and impact. It is
**not** defensible for this one:

`W < L < D` requires a detection latency `L`. The Observer is the detection mechanism. **Its
false-negative rate and its latency distribution are unmeasured and unbounded anywhere in the
checkpoint series.**

MEASURE 3.2 is precisely about risks that are difficult to assess with currently available measurement
techniques, and asks for systematic tracking approaches, determination of rate of occurrence and
severity, and identification of AI actors responsible for tracking emergent risks. MEASURE 2.7 asks
for anomalous-event rates and incident response times.

An unmeasured `L` inside an inequality that the whole quarantine and HOTL argument rests on is a
MEASURE-shaped hole inside a MANAGE-shaped design. It is the item most likely to be attacked by a
reviewer from either community, and unlike the MAP absences it cannot be scoped away, because TOPAK's
own safety argument invokes it.

Minimum acceptable answer for the article: state `L` as an obligation on the deployment rather than a
property of the architecture, name what must be measured to instantiate it, and make the rung manifest
carry the measured value. That keeps TOPAK out of the metrics business while refusing to pretend the
inequality is free.

### II.6 Third-party and supply chain

**GOVERN 6.1/6.2 and MANAGE 3.1** cover third-party dependencies, contingency for third-party failure,
and monitoring of third-party risk controls. Two TOPAK items land here and are currently filed
elsewhere or nowhere:

- The **monoculture declaration** (one model family across LTRO seats is a shared blind spot) is a
  third-party concentration risk in the Playbook's terms, and MANAGE 3.1's language supports it
  directly.
- **The model provider is a third party whose failure is not a TOPAK-modeled event.** Provider
  outage, silent model substitution, and version drift beneath a stable API are all outside the
  current model. Under havoc semantics a *worse* model is harmless, which is a genuine strength worth
  stating; an *unavailable* model is a liveness question TOPAK has not addressed, and silent
  substitution interacts with the monoculture item.

---

## Part III — Consolidated open items generated by this assessment

New, with proposed placement:

| Item | Placement | Priority |
|---|---|---|
| **Floor fitness check** — every privileged effect in the alphabet has a field in the floor's schema; no discharge by abstention | ADR-0014, or new ADR-0016 | **High** — I.4 |
| **Forensic floor** — bounded fact set surviving erasure and break-glass | ADR-0013, fifth obligation | **High** — II.2 |
| **Trusted base enumeration** | New article section, modeled on paper §3.4 | Medium — I.7 |
| **TLC-versus-TLAPS declaration** | Article methods; affects claim language throughout | Medium — I.8 |
| `Contained`/`Mediated` recut as theorem-versus-corollary | Checkpoint §5 amendment | Medium — I.6 |
| Observer detection rate and `L` as a deployment obligation | Rung manifest; article | Medium — II.5 |
| Model provider as unmodeled third party | Open list | Low-medium — II.6 |
| §4.2 → §4.6 + Appendix B citation fix | Article, checkpoint §1, §2 | **Blocking for publication** — I.3 |
| Varshney spelling sweep | Everywhere | **Blocking for publication** |
| Scope-declaration paragraph (MAP/MEASURE out of scope, explicitly) | Article | **Blocking for publication** — II.3 |

### Revised next-four

The 09.12 checkpoint's recommended sequence was: Observer quarantine gate → ADR-0013 → rename sweep →
ADR-0003 bundling check. Proposed revision:

1. **ADR-0013.** Promoted above the quarantine gate. It now carries a governance contradiction
   (II.2) on top of the composition hole, and it is the only item where an external reviewer finds a
   contradiction rather than a gap.
2. **Floor fitness (new).** Published result says ADR-0007's three-gate extension is insufficient.
   Cheap to specify, decidable under existing discipline, currently unowned.
3. **Observer quarantine gate**, picking up the `L` measurement question (II.5) in the same pass,
   since both concern what the Observer is and what it costs.
4. **Publication-blocking sweep**, bundled: CI → `Build` rename, Varshney spelling, §4.2 → §4.6
   citation, scope-declaration paragraph. All trivial, all embarrassing if missed.

ADR-0003's bundling check drops to fifth. The masking clause is still independently supersedable and
that has not changed.

---

## Appendix — citation-ready pointers into Moon & Varshney

| Use | Section |
|---|---|
| Havoc oracle semantics, Dafny listing | §2, Listing 1 |
| Soundness theorem | Theorem 3.2, §3.3 |
| Deployed boundary safety, effect exclusivity antecedent | Corollary 3.3, §3.3 |
| Trusted base enumeration | §3.4 |
| Failure taxonomy (refinement, effect-faithfulness, property-completeness gaps) | §3.5 |
| PocketFlow witness, four-variant `Action` | §4.1 |
| Seven-phase synthesis pipeline, information barrier | §4.2, §4.3 |
| Three-gate validation (G1 resolution, G2 vacuity, G3 discrimination) | §4.4 |
| **Schema mismatch, silent abstention, gates insufficient** | **§4.6, Appendix B (B.1–B.3)** |
| Deployment stack figure (containment layer verified; sandbox/kernel/hw audited) | Figure 1, §2 |
| Narrow-interface design pressure | §5 |
| Limitations: effect exclusivity, template fitness | §5.1 |
| Scope-declaration model paragraph | Impact Statement |
