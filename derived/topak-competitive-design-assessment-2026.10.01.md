# TOPAK Competitive Design Assessment

**2026.10.01** · derived · assessment, not a record · **design level only**: what each design commits to and how
it is structured. It does not judge whether anything works, how fast it is, how mature it is, or whether it has been
adopted. · TOPAK basis: Genesis Checkpoint G7 and Theory of Operation revision 11, at `33a01c2` · Comparables:
Moon & Varshney (arXiv:2605.09045v2), NVIDIA OpenShell at `348a1fc` (2026.10.01), Temporal (server, SDK
integrations and Agent Harness, as of Replay 2026), AWS Bedrock AgentCore Policy with Dogwood, Google DeepMind CaMeL
and CaMeLoT, Microsoft FIDES and the Agent Governance Toolkit, Progent, AgentSpec, Invariant/Snyk, Anthropic
`sandbox-runtime`, and Restate and DBOS · prepared by Claude in one session at the custodian's request

Nothing here is ratified, and this document proposes no decision text. It extends the 2026.09.28 NVIDIA comparison
and does not repeat it: OpenShell gets only its changes since then. §9 lists what could not be verified. Several
comparables were read only through search summaries, and the text says so wherever that matters.

---

## 0. Verdict

**No surveyed design is aiming at the same thing as TOPAK.** The field has settled into three families. Each one
governs a different object, and none of them governs *the authority to change the rules*:

| Family | Members | What it governs | Premise about the agent |
|---|---|---|---|
| **Containment runtimes** | OpenShell (+ Sentry), Anthropic `srt` | A process's reach: syscalls, files, egress, credentials | Untrusted subprocess |
| **Action-policy layers** | AgentCore Policy + Dogwood, Progent, AgentSpec, Invariant, MS Agent Governance Toolkit, MCP gateways | Each tool call, sometimes against history | Untrusted, or scored |
| **Data-flow layers** | CaMeL / CaMeLoT, FIDES | Which values may reach which tool, by provenance | The planner is trusted; the data is not |
| **Durable execution** | Temporal, Restate, DBOS | That a workflow survives crashes and can be replayed | Trusted worker code |
| **Verified containment** | Moon & Varshney | One agent framework's action boundary, proved down to code | Havoc oracle |

TOPAK fits none of these families cleanly, for the reason the 09.28 comparison gave: its threat sits in **Build**. The
Byzantine party is the author of the specification, policy and floor, not only the agent that runs under them. Every
comparable treats policy authorship as an operator's trusted act, or as a proposal from the agent that a human
approves. **TOPAK's distinctive design surface has no counterpart in any surveyed design.** That surface is a rules
floor over a havoc anchor, a computed tighten/relax classification, quorum promotion with recusal, a
consensus-ordered record that includes denials, and erasure as a modeled event.

Against that, **three comparables now do things at design level that TOPAK's design does not**:

1. **Moon & Varshney** specify a *refinement chain to the running code*. TOPAK names that chain as a debt
   (T-0045-28).
2. **CaMeL and FIDES** constrain *which arguments an authorized action may carry*, by the provenance of those
   arguments. Under havoc, TOPAK says nothing about prompt injection inside the authority envelope.
3. **Dogwood** gives the policy tier *history-dependent* conditions on a formal temporal-logic basis: rate limits,
   prerequisites and running totals. TOPAK's floor is per-request and stateless by construction. Its only history
   lives in mechanism constants such as `K`, `R` and the watermark.

None of the three needs semantic lift. All three are compatible with ADR-0007, and §7 says how each could be stated
in TOPAK's vocabulary.

**One-line positioning.** The rest of the field governs *what the agent may do*. TOPAK governs that, and in addition
*who may change what the agent may do, how that change is classified, and what record survives it*. At design level,
TOPAK's competitors are not the products listed here. Its competitor is the default assumption, shared by every one
of them, that the policy author is trusted.

---

## 1. Scope and method

**Design level** means the architecture as each project's own primary texts state it:

- components and their trust relations;
- where enforcement happens;
- the policy language and how policies compose;
- who may widen authority;
- what is ordered and recorded;
- what is verified, and about which object.

It excludes performance, correctness of implementation, adoption, maturity and release status. Where a design is
announced but unbuilt (Sentry, CaMeLoT's integration, TOPAK's confinement), it is assessed as designed, and that is
marked.

**The axes used throughout** (§2) are TOPAK's own, because the assessment asks where TOPAK stands. The cost is that
TOPAK's vocabulary frames the questions: a design that never asked a question scores "absent" rather than "different".
§6 corrects for that by listing what the comparables value and TOPAK does not.

---

## 2. Design matrix

Legend:

- **●** the design commits to it as a structural property;
- **◐** partially, optionally, or as a manual or out-of-path check;
- **○** absent;
- **—** out of the design's scope by intent.

| Axis | TOPAK | Moon & Varshney | OpenShell (+Sentry) | Temporal | AgentCore + Dogwood | CaMeL / CaMeLoT | FIDES | MS AGT |
|---|---|---|---|---|---|---|---|---|
| **A1** Model out of the trusted base | ● | ● | ◐ ¹ | — | ● | ◐ ² | ◐ ² | ○ ³ |
| **A2** Closed, typed action alphabet | ● | ● | ◐ ⁴ | ○ | ◐ ⁵ | ● ⁶ | ○ | ○ |
| **A3** Semantic judgment can only subtract | ● | ● | ○ | — | ◐ ⁷ | ● | ● | ○ |
| **A4** Policy tier with mechanized semantics | ● Cedar floor | ● Dafny | ◐ Rego + Z3 model | ○ | ● Cedar | ◐ ⁸ | ○ | ◐ ⁹ |
| **A5** Composition is monotone (later layers only narrow) | ● | — ¹⁰ | ○ ¹¹ | — | ◐ ¹² | ● | ● | ○ |
| **A6** Policy *change* governed and classified | ● | ○ | ◐ ¹³ | ○ | ○ | ○ | ○ | ○ |
| **A7** Authority over the rule-makers (anchor, rules floor) | ● | ○ | ○ | ○ | ○ | ○ | ○ | ○ |
| **A8** Separation of duties among agents | ● seats, cells, recusal | ○ | ○ | ○ | ○ | ◐ ¹⁴ | ◐ ¹⁴ | ◐ ¹⁵ |
| **A9** Total order over authority-changing decisions | ● Paxos | ○ | ○ | ◐ ¹⁶ | ○ | ○ | ○ | ○ |
| **A10** Denials in the record | ● | ○ | ● | ○ ¹⁷ | ● | ◐ | ◐ | ● |
| **A11** Erasure and legibility modeled | ● | ○ | ○ | ○ | ○ | ○ | ○ | ○ |
| **A12** OS / guest confinement | ● designed, unbuilt | ◐ assumed | ● | ○ | ○ | ○ | ○ | ○ |
| **A13** Attested confinement (measured, verified) | ● rung 3 designed | ○ | ◐ Sentry, of the watcher | ○ | ○ | ○ | ○ | ○ |
| **A14** Provenance / data-flow on arguments | ○ | ○ | ○ | ○ | ○ | ● | ● | ○ |
| **A15** History-dependent policy | ◐ ¹⁸ | ◐ loop bound | ○ | — | ● MFOTL | ● CTL over plan | ○ | ◐ trust score |
| **A16** Detection placed by rule, deny-only, cross-family | ● designed, unbuilt | ○ | ◐ Sentry placement | ○ | ○ | — | — | ○ |
| **A17** Model identity pinned | ● Persona | ○ | ○ | ○ | ○ | ○ | ○ | ◐ DID per agent |
| **A18** Verification object is the mechanism | ● TLC + op. model | ● | ○ ¹⁹ | ○ | ○ | ◐ the plan | ○ | ○ |
| **A19** Refinement to running code | ○ debt T-0045-28 | ● | ○ | ○ | ○ | ○ | ○ | ○ |
| **A20** Durable, replayable execution | ◐ ²⁰ | ○ | ○ | ● | ○ | ○ | ○ | ◐ sagas |
| **A21** Trusted base declared row by row | ● | ● short list | ◐ prose | ○ | ○ | ◐ | ◐ | ○ |

1. OpenShell's enforcement is model-free, but its supervisor middleware, Guardrails and Nemotron classifiers can
   *allow* or *rewrite*. Those are optional and outside the core.
2. CaMeL and FIDES keep the *quarantined* model out of authority, but the *planner* model is trusted to write the
   plan from the user's query.
3. AGT's trust score, 0–1000, sets privilege rings and can include a semantic intent classifier, so a model's
   judgment can *raise* privilege.
4. OpenShell's MCP `tools/call` allow-lists and per-binary L7 rules type the wire. The agent still has a shell.
5. AgentCore types the gateway's tool calls. The agent may hold other channels.
6. CaMeL's restricted Python plan is a closed language. Its tools are not.
7. AgentCore allows Cedar to be generated from natural language, which puts a semantic step in *authoring*. A
   reviewer can see the generated text.
8. CaMeL's policies are Python predicates. CaMeLoT model-checks the plan, not the policy.
9. AGT accepts Cedar or Rego, but YAML and a classifier sit beside them.
10. Moon & Varshney verify one fixed policy and have no change cadence.
11. OpenShell merges rules: "a request is allowed when either rule allows it". A global policy replaces sandbox
    policy.
12. Cedar's forbid-overrides is monotone within one policy set. Dogwood's temporal conditions add to it. Nothing
    bounds a revision.
13. OpenShell's prover computes the reach a proposal adds, and any finding blocks auto-approval. This is a manual,
    out-of-path check, and there is no authority routing.
14. The privileged/quarantined planner split is a duty separation *inside one agent*.
15. AGT's privilege rings are separations by score, not by role.
16. Temporal uses per-shard fencing (RangeID) over a database transaction: an order within a workflow, not over
    decisions about authority.
17. Temporal records accepted Updates. A validator's rejection is not written to history.
18. TOPAK's history-dependent controls are mechanism constants (the round bound `R`, the watermark bound `K`, coverage
    across rounds), not policy text.
19. OpenShell's prover verifies a *policy's* reach, not the supervisor.
20. TOPAK's log can replay what crossed the membrane. It does not resume a crashed computation, by design.

Read down the TOPAK column and three things are true: TOPAK's ● cells are ●; A14 is a hole; A19 is an admitted
debt. Read across rows A6, A7, A9 and A11, and TOPAK is alone. Those four rows are the Build-side inversion made
concrete.

---

## 3. The comparables, one at a time

### 3.1 Moon & Varshney, "Containment Verification: AI Safety Guarantees Independent of Alignment"

**What it is.** A single agent framework (PocketFlow) whose action boundary is a reference monitor written in Dafny.
The proof is a forward-simulation refinement from a boundary-event policy to an operational model to code. The code
is compiled to Python, and the model is a havoc `extern` behind a shim.

- **Policy.** Three invariants: reads under the workspace root, tool calls on an allowlist, and steps under a loop
  bound.
- **Theorem 3.2, Containment Verification Soundness.** Under boundary-event refinement and effect exclusivity, every
  modeled external effect satisfies the policy for every typed action sequence.
- **Building the specification.** An LLM pipeline synthesizes the specification and the proof, behind an
  "architectural information barrier", and three gates check the result: resolution, vacuity and discrimination.
- **Trusted base.** The concrete policy, the state and event abstractions, the effect-exclusivity boundary, the
  runtime type boundary and shim, and the Dafny verifier and compiler.

**Design relationship.** TOPAK's closest relative, and the one ToO §11.1 already aligns to.

- **What it shares with TOPAK:**
  - havoc semantics;
  - a typed boundary as the only channel;
  - boundary-enforceable properties only;
  - an explicit trusted base;
  - gates against vacuous specifications.
- **Where it is ahead:**
  - It carries the proof to code that runs. TOPAK's design names that chain as a debt, and its stage 1 is a trace
    harness, not a refinement.
  - Its trusted base is short enough to read in one sentence. TOPAK's has thirty rows: more honest, and harder to
    audit.
- **Where TOPAK is ahead:**
  - everything that changes over time: bundle cadence, floor revisions and their classification, the anchor, the
    rules floor, promotion, revocation, erasure;
  - everything with more than one agent: seats, cells, recusal, Observers;
  - everything recorded: the paper has no log, no audit trail and no provenance.

  The paper's design is a snapshot. TOPAK's is a process.
- **Where they agree on an open problem.** The paper's own negative result is silent abstention: a corollary
  quantified over an always-empty sequence passes all three gates. Its proposed fix is a "template-fitness check".
  That fix is TOPAK's unowned fourth gate (floor fitness), named by the paper and built by neither.
- **One design asymmetry that favors TOPAK.** The paper trusts the Dafny verifier, which discharges obligations
  through Z3 without a certificate. ADR-0030 A1 refused exactly that for TOPAK's own gate and put a pinned proof
  checker behind cvc5. If TOPAK adopted a Dafny or Verus chain, it would have to declare the verifier as a trust root.

**Citation hygiene the corpus owes** (found while researching this; see §9 for confidence):

- **Theorem 3.2.** The corpus's 09.10 narrative calls it "the collapse case" for missing typed action discipline. In
  the paper as relayed, Theorem 3.2 is the *soundness* theorem. The collapse follows from failing its premises; it is
  not a theorem of its own.
- **"Unanimous humans reading the same vacuous gate output fail together."** ToO §7.1 cites this to "Moon & Varshney
  §4.6; Knight & Leveson". §4.6 is about the *pipeline's* silent abstention passing automated gates, and nothing
  found attributes a claim about human reviewers to it. The human-correlation half belongs to Knight & Leveson alone.
  The sentence should cite §4.6 for the vacuous output and Knight & Leveson for the correlated reviewers.

Both should be checked against the PDF before any external draft. ToO §11.1 already carries the paper's
publication caution.

### 3.2 NVIDIA OpenShell: what changed since 2026.09.28

The 09.28 comparison stands. It placed OpenShell as a rung-1 launcher for a `Mediated` principal failing P3, P4 and
P5. The design changes since then, at `348a1fc`:

- **The privacy router is gone.** Release 0.1.0 removed the managed inference routes and `inference.local`. Agents now
  call providers' native APIs, and the credential is substituted at egress. In TOPAK's terms, P5 is still a fail, and
  the inference path is now an ordinary credentialed egress like any other, so the 09.28 note that inference was a
  separate mediated channel no longer applies.
- **MCP inspection by protocol profile** (#3335). MCP denials now cite the policy revision (#3850). The second change
  is the shape of ADR-0030's "a floor deny names its reason" and of a bundle decision counting only from a named
  revision. It is a convergence.
- **Gateway audit to OCSF JSONL** (#3264). This adds control-plane events to the record. There is still no ordering,
  seal or erasure model.
- **Sandbox identity separated from TLS** (#3110). This moves toward identity as a first-class field, the direction
  of TOPAK's lease, which binds principal, seat and Persona.
- **Unknown policy fields are rejected.** Schema closure: the shape of TOPAK's schema S being enforced on every
  request (ADR-0030 §4).
- **RFC 0011 (multi-player) is still a draft.** It proposes workspaces, Platform/Workspace Admin/User roles, and
  attribution of audit to principals. There is still no agent-to-agent protocol. Multi-agent support is separate
  sandboxes plus a parent's prover boundary over a child's policy.

None of this changes the 09.28 verdict. The direction of travel is toward TOPAK's
structure on three axes (A2 typed wire, A10 attributed denials, closed schema), and away from it on none.

### 3.3 Temporal

**What it is.** Durable execution.

- **Workflow and activities.** Workflows are deterministic code, rebuilt by replaying an append-only event history.
  Activities hold every side effect and are retried under policy.
- **Talking to a running workflow.** Signals, queries and Updates (with an optional validator).
- **Pinning code.** Workflows are pinned to builds by Worker Versioning.
- **Server.** History is split into shards. Each shard is owned by one host and fenced by a monotone RangeID.
  History and mutable state are written in one database transaction, with an outbox to matching. There is no
  consensus protocol of Temporal's own; it inherits ordering from Cassandra lightweight transactions or SQL
  transactions. Multi-cluster replication is asynchronous, with failover versions.
- **Security.** Namespaces, mTLS, a pluggable ClaimMapper/Authorizer, and client-side payload codecs, so the server
  sees ciphertext. Nexus endpoints connect namespaces.
- **AI position.** Integrations with the OpenAI Agents SDK (GA) and Google ADK. The experimental **Agent Harness**
  adds a Python tool-approval engine and durable pauses for a human decision.

**Why it is in this assessment.** Temporal is not a safety design, but it is the default *substrate* agent systems are
being built on. Several of its structures look like TOPAK's at a glance, and the differences are instructive:

| Concern | Temporal | TOPAK | Design difference |
|---|---|---|---|
| Fencing | Shard RangeID; a stale owner cannot write | Fence = Paxos log index at grant; epoch fence; apply-time re-check | Same idea, different object. Temporal fences *ownership of a shard*; TOPAK fences *authority of a principal*. Neither fence says anything about the other's object |
| Replay | Re-executes workflow code against history to rebuild state | Reconstructs what crossed the membrane, including denials | Temporal replays the *computation*; TOPAK replays the *boundary*. Temporal's history cannot tell *behaved* from *was prevented*, because rejected Updates are not recorded (ADR-0020's dropped clause, by design) |
| Effect semantics | Activities **at least once**, retried; idempotency is the user's problem | Effects **at most once**: run only after commit; a crash between commit and effect leaves no effect (ToO §4.1) | The most important difference. A Temporal retry after a worker crash may repeat an effect. TOPAK chose the opposite failure direction, which is subtractive. A TOPAK effect hosted in a Temporal activity would inherit at-least-once semantics unless the admit, not the activity, is the unit of retry |
| Determinism | Workflow code must be deterministic; checked by replay, raises on divergence | The typed lift is total and mechanical; the floor is a pure library | Both make the decision path deterministic. Temporal does it so it can recover; TOPAK does it so the record can be audited |
| Versioning | Patching and Worker Versioning pin a run to the build that started it | Renewal keeps the bundle; tightening a live round ends it; a bundle reaches a principal at its next grant | Convergent: *a running unit of work keeps the rules it started under*. TOPAK adds that changing them mid-unit ends the unit |
| Human in the loop | A durable wait on a signal or Update; a human approves a paused tool call | Grant seats vote; break-glass is a quorum on a roster; Run is HOTL inside `W`; Build gates block | Temporal makes waiting cheap and leaves who approves to the application. TOPAK specifies who approves and leaves waiting to the round bound |
| Authorization | Namespace and API level, through pluggable claims; Harness approvals in application Python | Per action: floor ∧ ¬bundle, at the lease's bundle revision | Temporal trusts worker code entirely. Its authorization stops at the frontend |
| Payload privacy | Client-side codec; the server sees only ciphertext | Control-plane facts vs. a plaintext store built for deletion (ADR-0004) | Convergent separation of metadata and content. TOPAK adds erasure by topic and a forensic floor; Temporal has retention only |
| Replication | Asynchronous, active/passive per namespace; unreplicated events can be lost or reapplied at failover | Multi-Paxos over crash-recovery replicas (A9) | Temporal accepts divergence on failover; TOPAK's control plane cannot |

**Design-level reading.** Temporal *is* TOPAK's "K" role done more ambitiously: a durable, replayable transport for
work. It is *not* TOPAK's "P" role, because it orders nothing about authority. It is the cleanest example of the
field's default premise: the code that runs is trusted, and safety means not losing work. A TOPAK deployment could
host its Thinkers' loops on Temporal. ADR-0045's delegate-by-failure-direction test would then sort Temporal's parts:

- **Delegated.** Retry timers and durable waits fail by stalling, which only subtracts.
- **Refused as an admit path.** A workflow that decides whether to invoke a tool fails by adding authority, so it
  cannot be the admit path. The admit must stay in the mechanism, and the activity must be the *transport* of an
  already-ordered admit.
- **Effect semantics.** At-least-once retry must be bounded to the admit's fence. Otherwise a retried activity is an
  effect without a fresh authorizing predecessor, which falsifies ADR-0015's enumeration.

**Restate and DBOS** take the same design position with different substrates: a replicated log in Restate, a
Postgres you already run in DBOS. Neither has a policy or confinement layer. Restate is the only one of the three
with a replicated log at its core, so it is the nearest to TOPAK's P role. It still orders execution, not authority.

### 3.4 AWS Bedrock AgentCore Policy, and Dogwood

**What it is.**

- **AgentCore Policy** enforces Cedar policies at the AgentCore Gateway, outside agent code, on traffic from agent to
  tool. It is default-deny, has log-only and enforce modes, and can author Cedar from natural language.
- **Dogwood** (Apache-2.0, 2026.08) embeds Cedar and adds `when temporal` conditions over the agent's event history:
  prerequisites, rate limits, running totals and approvals. It is grounded in Metric First-Order Temporal Logic and
  runtime verification.

**Design relationship.** The nearest *policy-tier* design to TOPAK's, and it made the same language choice for the
same reason: Cedar is analyzable.

- **Shared with TOPAK:**
  - an untrusted agent;
  - an enforcement point outside the agent;
  - a Cedar evaluator;
  - default deny.
- **What AgentCore lacks:**
  - a floor/bundle split;
  - any rule for classifying a revision;
  - anything above the operator.

  AgentCore's composition is one Cedar policy set, edited by whoever holds the console.
- **What Dogwood adds that TOPAK's design lacks: A15.** TOPAK's floor is deliberately per-request, with every input
  from the typed lift and the issued rules. Its stateful controls are mechanism constants that the floor reads as
  lifted values from the values file. That is sound and narrow. A deployment wanting "no more than N `Actuate` calls
  to tool T per round" or "`Actuate(pay)` only after a `Consult(invoice)`" has two options in TOPAK. It can express
  the rule in the bundle tier (Rego, unanalyzed, but it can only subtract), or it can ask for a new mechanism
  constant. Dogwood shows a third design: temporal policy with a formal semantics, evaluated over a history the
  enforcement point owns. In TOPAK the history the mechanism owns is the round topic and the log, so the lift is
  available. §7 item 2.
- **One thing TOPAK would reject.** Natural-language authoring of policy is a semantic step in Build. Under TOPAK's
  premise it is acceptable *only* because the output is text a computed classification then routes (ADR-0030 §5).
  AgentCore has no such routing, so a mistranslation that relaxes the policy is indistinguishable from an intended
  edit. This is the transpiler concern of ADR-0030 §6, in a product.

### 3.5 CaMeL, and CaMeLoT

**What it is.**

- **CaMeL** separates a *privileged* planner, which writes a restricted-Python plan from the trusted user query
  alone, from a *quarantined* model, which parses untrusted data and has no tools.
- A custom interpreter attaches **capabilities** (provenance and allowed readers) to every value and checks
  deterministic policies before each tool call.
- **CaMeLoT** (2026.09) turns the plan into a finite-state system and model-checks CTL properties with nuXmv before
  execution.

**Design relationship.** This is the comparable that exposes TOPAK's largest design-level hole in Run (A14):

- **What TOPAK does not cover.** TOPAK's premise makes the Thinker havoc, so prompt injection is irrelevant to
  *containment*. Whatever the injected Thinker does is inside the alphabet and the floor. But that is all TOPAK
  promises. Inside the envelope, an injected Thinker may `Actuate(send_email, {to: attacker, body: secrets})` if the
  floor allows `send_email` with those argument types. TOPAK's argument constraints live in the bundle tier, and
  nothing there knows *where an argument came from*.
- **What CaMeL adds.** It narrows exactly that, deterministically, and its labels are computed by the interpreter, not
  judged by a model. In ADR-0007's vocabulary, **a provenance label computed by the mechanism is a syntactic lift**:
  mechanical, total, and drawn from the record of which `Consult` or `Actuate` result a value derives from.
- **Why TOPAK cannot simply adopt it.** TOPAK's Thinker emits typed actions as text through a decoder; it does not run
  a plan in an interpreter the mechanism owns. Dataflow from a `Consult` result into an `Actuate` argument passes
  through the model, where labels cannot follow it. Two designs can get it back:
  - **CaMeL's split.** The planner never sees untrusted content, and the quarantined parser has no alphabet. This maps
    onto TOPAK's cell, as a third seat kind with no effect variants.
  - **FIDES's approach** (§3.6). Content stays opaque to the planner and is referenced by handle.

  §7 item 1.
- **Where TOPAK is ahead.** CaMeL trusts the planner model to write the plan, and the plan's correctness is the
  planner's. CaMeLoT checks the plan's properties *before execution*, which is a mechanism-side verification of a
  model-authored artifact. That is the Build-side shape TOPAK formalized, applied per request. Neither has a record,
  an authority model, or multiple agents.

### 3.6 Microsoft FIDES, and the Agent Governance Toolkit

**FIDES** applies information-flow control to agent messages:

- integrity and confidentiality labels on a lattice, propagated automatically;
- a deterministic check before consequential tool calls;
- untrusted results held in variables the planner cannot read, with explicit operations to hide and reveal them.

**Design relationship.** It is CaMeL's goal reached by a different route. It shows that *the planner never reading
untrusted content* can be achieved by handles rather than by a second model. For TOPAK that is the more natural
route. The Listener (ADR-0043) already delivers `Consult` content and `Actuate` results to the Thinker as the
mechanism's own act, so it could deliver a *handle* plus a label instead, and the typed lift could carry the label
into the admit. That would be a mechanism change with a floor consequence, and §7 item 1 lists it.

**The Agent Governance Toolkit** combines:

- an in-process policy engine (YAML, Rego or Cedar, plus a semantic intent classifier);
- Ed25519 DID identities and an inter-agent trust protocol;
- a **dynamic trust score from 0 to 1000** that assigns privilege rings, with sagas and a kill switch.

**Design relationship.** The plainest design *opposite* of TOPAK in the survey, and worth stating as such:

- **The score moves upward**, so behavior that a classifier judges good *adds* privilege. That is semantic lift into
  the admit path (ADR-0007) and a violation of monotonicity at the decision, credential and detection layers (ToO
  §7.8).
- **Enforcement is in-process middleware**, so the enforcement point shares a fault domain with the agent (the
  concern behind ADR-0034, and ADR-0045's "refused" class).

AGT does share three things with TOPAK: per-agent cryptographic identity (cf. the lease's principal and Persona), a
kill switch (cf. the epoch fence), and a choice of Cedar. Its design premise is that agents earn trust. TOPAK's is
that they never do.

### 3.7 Progent, AgentSpec, Invariant/Snyk

- **Progent.** A DSL for tool-call privileges: per-tool rules with conditions on arguments, forbid over allow, default
  deny, and fixed generic policies that override task policies. An LLM may *generate* the task policies.
  - Its two-tier priority is a floor/bundle composition in all but name: fixed generic policies over task policies,
    forbid winning.
  - It lacks TOPAK's rule that the task tier may only subtract. An LLM-generated task policy can allow what the
    generic tier did not forbid.
  - A reported 2026 extension (unverified, §9) auto-applies an update only if an SMT check shows it narrows
    privilege. If that is accurate, it is ADR-0030 §5's computed classification, one tier down, without the
    authority routing for relaxations.
- **AgentSpec.** A trigger/check/enforce rule DSL hooked into the LangChain loop. Its enforcement options include
  "LLM self-reflection", a semantic step that can *repair* an action rather than only deny it. The framework is in
  the trusted base. Design-wise it is a policy layer inside the agent's own process, the placement TOPAK's
  Observer rules forbid for detection.
- **Invariant Guardrails / Snyk Agent Scan.** A trace-matching rule language at a proxy, plus a pre-runtime scanner
  that hashes tool descriptions to detect a "rug-pull". The hashing is the design idea worth noting: it is TOFU on
  tool *descriptions*. TOPAK's `Invoke` allowlist by name and **digest of a promoted artifact** is the stronger
  form, since it pins what was promoted, not what was first seen. But TOPAK pins the tool's code and says nothing
  about the *description* the Thinker reads. In MCP, the description is where poisoning lives. §7 item 4.

### 3.8 Anthropic `sandbox-runtime`

Seatbelt on macOS; on Linux, bubblewrap with seccomp-BPF and no network namespace. All egress goes through host-side
HTTP and SOCKS5 proxies on a Unix socket, with domain allow and deny lists, default deny, fixed per session.

**Design relationship.** In ADR-0034's terms, a rung-1 launcher:

- **P1** fails in the strict reading: there is one channel, but it is a general proxy.
- **P3** fails: there is a shell by design.
- **P4 and P5** fail.

It is narrower than OpenShell: no L7 rules, no credential injection, no prover. Its one structural point of
contact with TOPAK is ADR-0036's: *the channel is a socket the host owns and the guest cannot route around*.
Policy is static for the session, which is TOPAK's "the bundle is fixed for the round" without the
promotion around it.

---

## 4. Where TOPAK's design is alone

Each item is a design commitment no surveyed comparable makes, as found at the date of this assessment:

1. **The threat is in Build.** Every comparable trusts the policy author: an operator, a console user, a human
   approving the agent's proposal. TOPAK alone treats the author of the policy as Byzantine and builds the authority
   path around that (A6, A7).
2. **A rules floor over a havoc anchor.** No comparable states what bounds the authority that defines who may approve.
   The regress ends in an operator in all of them. TOPAK's ends in one axiom bounded by two verified floors.
3. **Computed classification with authority routing.** OpenShell's prover and the reported Progent extension compute
   what a change adds. Only TOPAK *routes the change to a different authority path* on that answer, so an author
   cannot pick the cheaper path.
4. **A total order over authority, and an apply-time re-check.** No comparable orders grants, revocations and
   expiries in one log with the fence as the log index. Temporal's fencing is the nearest structure and is about
   shard ownership, not authority.
5. **Denials as evidence, erasure as a modeled event, and a forensic floor.** OpenShell, AgentCore and AGT log
   denials. None models what survives erasure, or separates legibility from immutability.
6. **Separation of duties as seats.** Author/voter disjointness, recusal enforced in the action envelope, and seat
   kinds that bound alphabets. The nearest comparables (CaMeL, FIDES) separate duties *inside* one agent, between a
   planner and a parser. TOPAK separates them *between principals*.
7. **Detection with a placement rule, deny-only, and coupled to admission.** Sentry has a placement (a separate
   device) but neither a stated deny-only rule nor a stated failure direction. No other comparable couples admission
   to a detector's liveness.
8. **Confinement as a ladder decided by failure direction**, with attestation at grant and no silent downgrade.
   Containment runtimes ship one rung. None states which host failures they tolerate, by direction.
9. **The model pinned as an artifact** (Persona), with lineage independence computed from the log. No comparable pins
   the model, its prompt and its decoder as one promoted identity.
10. **Monotonicity stated at fourteen layers** (ToO §7.8). Several comparables are monotone at one layer: Cedar
    forbid-overrides, CaMeL's labels, OpenShell's locked filesystem. None states it as a design-wide discipline, and
    one (AGT) violates it as a feature.

---

## 5. Where TOPAK's design is behind or exposed

These are design-level only. Every gap that is merely "not built" is excluded, because the design itself
covers it.

1. **No refinement to code (A19).** Moon & Varshney's design *includes* the chain. TOPAK's design names its absence
   as a debt with an owner and a first stage, which is honest and is still a gap in the design, not only in the
   build.
2. **No provenance or data flow on arguments (A14).** Under havoc, TOPAK bounds what *can* happen, not what an
   injected Thinker *will* do inside that bound. CaMeL and FIDES show deterministic, mechanism-computed narrowing
   inside the envelope. It is compatible with ADR-0007, and the corpus has no record for it. This is the most
   consequential design gap the survey surfaced, because in practice prompt injection is the threat buyers ask about
   first.
3. **History-dependent policy is a mechanism constant, not policy (A15).** Dogwood shows temporal conditions with a
   formal semantics at the policy tier. In TOPAK, every such control is either a mechanism release or unanalyzed Rego.
4. **Tool descriptions are not pinned.** TOPAK pins tool code by digest. In an MCP world the description a Thinker
   reads is part of the tool's interface, and poisoning there needs no change to the code. In TOPAK's terms the
   description is `Consult`-like ingress whose digest no allowlist entry names.
5. **The trusted base is long.** Thirty rows is the honest count for what TOPAK covers. Next to Moon & Varshney's
   one-sentence list, it is a design whose audit surface grows with its scope. That is a real trade, not a defect,
   and it should be stated as such in any external comparison.
6. **No resumption.** Temporal's durability is a property TOPAK's design does not offer. A crashed round ends, and
   the work is lost by design, the subtractive direction. That is correct for safety and is a capability cost the
   ToO states for confinement (no shell) but not for durability. Long-horizon Run tasks will meet it.
7. **Replicas are crash-recovery, not Byzantine.** No comparable is better on this axis; most have no replicated
   control plane at all. It is listed because TOPAK is the only design whose premise makes the gap visible (ToO §12
   item 9).

---

## 6. What the comparables value that TOPAK's axes do not ask about

So that §2's matrix does not read as a scoreboard built by one side:

- **Expressiveness for the agent.** OpenShell, `srt`, Temporal and AGT all keep the shell, the network and the
  package manager because agents are useful with them. TOPAK's Build alphabet removes them. The design pays that
  price knowingly, and the market has so far chosen the other side.
- **Incremental adoption.** Every comparable can be put in front of an existing agent: a proxy, a middleware, a
  gateway, a sandbox around a binary. TOPAK's guarantees need the agent to speak its alphabet and nothing else. The
  rung-0 `Mediated` path is TOPAK's adoption on-ramp. It delivers attribution and authorization, not containment,
  and should be marketed as exactly that.
- **Agent-assisted policy authoring.** OpenShell's advisor, Progent's generated task policies and AgentCore's natural
  language to Cedar all use models to *write* policy, because humans are slow. TOPAK allows this. A Build Thinker
  may `Draft` a bundle. But it routes the result through promotion, which is the cost of the inversion.
- **Latency.** Gateway designs evaluate in-process in microseconds. TOPAK puts grants, heartbeats and effect admits
  on a consensus log, and couples Run's liveness to an Observer. Design-level only: the cost is structural, and ToO
  §5.4 states it.

---

## 7. Design ideas worth considering

None of the following is decision text. Each names the record it would touch.

1. **Provenance labels as a syntactic lift (from CaMeL and FIDES).** The Listener (ADR-0043) delivers ingress
   to the Thinker; it could deliver *handles* with labels, and the typed lift could carry the label of any
   argument that is a handle into schema S. A floor or bundle rule could then say "`Actuate(t, a)` is denied if
   `a.to` derives from a `Consult` outside root R". Labels are computed by the mechanism and never by a model, so
   ADR-0007 holds. The cost: the Thinker reasons over handles it cannot read, which is FIDES's trade, and a decoder
   that can dereference a handle collapses it. This would be a Run-alphabet amendment (ADR-0040) and a schema-S
   change (ADR-0030 §4).
2. **Temporal conditions in the floor language (from Dogwood).** Cedar has no history. Dogwood shows a design that
   keeps Cedar and adds an MFOTL layer evaluated over a history the enforcement point owns. In TOPAK that history is
   the round topic, already per principal per round and sealed. Two placements are possible:
   - **In the bundle tier.** It can only subtract, so it is safe at once.
   - **In the floor.** It would need the same mechanized-semantics obligation ADR-0030 §2 sets for the floor, which
     MFOTL has.

   Either would move `R`, and perhaps `K`, from mechanism constants to policy values, where parametricity (ToO §7.3)
   says a floor entry can bound them.
3. **Temporal as a delegated substrate, with the boundary stated (from §3.3).** If a deployment hosts Thinker loops on
   Temporal, the deployment declaration should say:
   - the admit is the unit of retry;
   - an activity transports an already-ordered admit and never decides one;
   - at-least-once retry is fenced by the admit's log index.

   That is an ADR-0045 Annex row (delegated, for durable waits and timers) and a refusal (any workflow logic on the
   admit path). It fits naturally in the archetype-evolution record (§8.2), or as a worked declaration.
4. **Pin tool descriptions with the tool (from Invariant/Snyk).** An `Invoke`/`Actuate` allowlist entry
   could carry the digest of the interface text the Thinker is shown, and the Listener could deliver only that text.
   That is ADR-0022 §3 and ADR-0040's entry schema. It is cheap, and it closes a poisoning path the digest of the
   code does not.
5. **Correct the two citations in §3.1** before any external draft: ToO §7.1's "unanimous humans … (Moon & Varshney
   §4.6; Knight & Leveson)", and the 09.10 narrative's reading of Theorem 3.2, which is in a closed revision and needs
   only a note in the next one.
6. **State the durability cost beside the capability cost** (ToO §2.4). "A crashed round loses its work" belongs
   with "no shell, no package installation, no network, no git", for the same reason: a reader who has used Temporal
   will say it first.
7. **Put the positioning sentence of §0 in the ToO's opening.** The ToO's §1 states the premise and the inversion. It
   does not state that the inversion is what separates TOPAK from the field, and every comparable here would be read
   by a reviewer as a competitor until it does.

---

## 8. Summary table: how each design answers TOPAK's three questions

| | *What may the agent do?* | *Who may change that, and how is the change classified?* | *What record survives?* |
|---|---|---|---|
| **TOPAK** | Alphabet ∩ floor ∩ ¬bundle, per lease | Byzantine authors; computed classification routes to promotion or anchor + promotion; rules floor bounds the anchor | Ordered admits, recorded denials, six non-erasable classes, erasure modeled |
| Moon & Varshney | Verified policy at the typed boundary | Not addressed; one fixed policy | Not addressed |
| OpenShell | YAML/Rego over FS, process, L4–L7, per binary | Operator; agent may propose network rules; prover flags added reach | OCSF events, attributed denials, SIEM export |
| Temporal | Whatever worker code does | Whoever deploys the worker | Event history of accepted events; not of denials |
| AgentCore + Dogwood | Cedar (+ MFOTL) at the gateway | Console user; natural-language authoring | Gateway logs |
| CaMeL / CaMeLoT | Plan ∩ capability policy; plan model-checked | Policy author, unaddressed | Not addressed |
| FIDES | Label-lattice policy before tool calls | Developer | Not addressed |
| MS AGT | Policy ∩ trust-score ring | Operator; score moves with behavior | Audit logs |
| Progent / AgentSpec | Per-tool rules / trigger-check-enforce | Developer; LLM may generate | Not addressed |
| `srt` | Domain allowlist, static | User settings | Not addressed |

Everyone answers the first question. Almost nobody answers the third. Only TOPAK answers the second.

---

## 9. What could not be verified

- **Moon & Varshney.** arXiv was blocked by this session's network policy, so the paper was read through search
  summaries only.
  - The title, authors (Royce Moon; Lav R. Varshney), arXiv ID and dates (v1 2026.05.09, v2 2026.06.29), the design
    above, and the number and statement of Theorem 3.2 are from multiple consistent summaries.
  - The ICML 2026 workshop venue is from summaries only.
  - Two section numbers are inferred from the corpus's own citations, not confirmed: §3.4 for the trusted base and
    Appendix B for the negative result.
  - The two citation findings in §3.1 are therefore *probable*, not confirmed. Check them against the PDF.
- **OpenShell.** Read from its repository at `348a1fc` (2026.10.01): `docs/`, `rfc/` and the commit log since
  2026.09.28. Sentry's internals remain unpublished; the 09.28 comparison's open questions about deny-only and
  fail-open stand.
- **Temporal.** Server internals are from `temporalio/temporal` `docs/architecture/history-service.md` and the
  assessor's prior knowledge of the public design. temporal.io was blocked.
  - The 2026 product statuses are from search summaries: Replay 2026 announcements, Worker Versioning GA, Nexus
    status, and the Agent Harness design.
  - The claim that an Update validator's rejection is not written to history is the public design as known to the
    assessor and was not re-checked.
- **AgentCore Policy and Dogwood, CaMeLoT, FIDES, AGT, Progent, AgentSpec, Invariant/Snyk, Restate, DBOS.** Read
  through search summaries and, where reachable, GitHub.
  - AGT's trust-score bands and performance figures are vendor claims.
  - The Progent "monotonic confinement" extension could not be attributed with confidence; it may be a different
    2026 paper.
  - The CaMeLoT arXiv number and venue are from summaries.
- **Not included.** Comparables with no public design text: Sentry beyond the launch material, and closed agent
  platforms. Also the Sokolov AEP/RATS composition (arXiv:2608.00801), already cited in the corpus. It is a
  record-attestation design, not a governance design, and is the natural comparable for a future note on ADR-0028's
  archive, not for this one.

---

## Sources

**TOPAK.**
- `README.md`
- `checkpoints/topak-genesis-checkpoint-G7-2026.10.01.md`
- `narrative/theory-of-operation.md` (revision 11): §1–§5, §7, §10–§13
- `derived/topak-vs-nvidia-open-agent-safety-platform-2026.09.28.md`
- `derived/topak-critical-review-2026.09.25.md` §2

**Moon & Varshney.**
- [arXiv:2605.09045](https://arxiv.org/abs/2605.09045) ([HTML](https://arxiv.org/html/2605.09045)), via summaries
- Related: [Sokolov, arXiv:2608.00801](https://arxiv.org/abs/2608.00801);
  [draft-sokolov-rats-aep-composition-03](https://www.ietf.org/archive/id/draft-sokolov-rats-aep-composition-03.html)

**OpenShell.**
- [NVIDIA/OpenShell](https://github.com/NVIDIA/OpenShell) at `348a1fc`: `docs/about/architecture.mdx`, the policy and
  prover docs, `rfc/0011`, `rfc/0013`
- PRs #3110, #3264, #3275, #3335, #3788, #3796, #3841, #3850, #3876
- [NVIDIA Open Agent Safety Platform](https://www.nvidia.com/en-us/solutions/ai/agent-safety/)
- [Technical blog](https://developer.nvidia.com/blog/nvidia-open-agent-safety-platform-a-reference-for-continuous-in-silicon-agent-monitoring/),
  via summaries

**Temporal.**
- [history-service architecture](https://github.com/temporalio/temporal/blob/main/docs/architecture/history-service.md)
- [Replay 2026 announcements](https://temporal.io/blog/replay-2026-product-announcements)
- [OpenAI Agents SDK integration](https://temporal.io/blog/announcing-openai-agents-sdk-integration)
- [Agent Harness](https://temporal.io/blog/temporal-agent-harness-durable-agent-infrastructure);
  [repository](https://github.com/temporal-community/temporal-agent-harness)
- [Series E release](https://am.gs.com/en-us/institutions/news/press-release/2026/temporal-raises-550m-ai-infrastructure-demand)
  (context only)

**Other comparables.**
- [AgentCore Policy GA](https://aws.amazon.com/about-aws/whats-new/2026/03/policy-amazon-bedrock-agentcore-generally-available/)
- [Dogwood](https://aws.amazon.com/blogs/opensource/introducing-dogwood-runtime-verification-for-ai-agents/)
- [CaMeL, arXiv:2503.18813](https://arxiv.org/abs/2503.18813); [CaMeLoT, arXiv:2609.18674](https://arxiv.org/abs/2609.18674v1)
- [FIDES, Agent Framework security](https://learn.microsoft.com/en-us/agent-framework/agents/security);
  [FIDES blog](https://devblogs.microsoft.com/agent-framework/fides/)
- [Agent Governance Toolkit](https://opensource.microsoft.com/blog/2026/04/02/introducing-the-agent-governance-toolkit-open-source-runtime-security-for-ai-agents/);
  [repository](https://github.com/microsoft/agent-governance-toolkit)
- [Progent, arXiv:2504.11703](https://arxiv.org/abs/2504.11703)
- [AgentSpec, ICSE 2026](https://cposkitt.github.io/files/publications/agentspec_llm_enforcement_icse26.pdf)
- [Invariant](https://github.com/invariantlabs-ai/invariant);
  [guardrails reference](https://invariantlabs-ai.github.io/docs/mcp-scan/guardrails-reference/)
- [Anthropic sandbox-runtime](https://github.com/anthropic-experimental/sandbox-runtime);
  [Claude Code sandboxing](https://code.claude.com/docs/en/sandboxing)
