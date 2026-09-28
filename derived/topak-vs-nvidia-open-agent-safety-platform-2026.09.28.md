# TOPAK vs. NVIDIA Open Agent Safety Platform — Comparison

**2026.09.28** · derived · comparison, not a record · TOPAK basis: Genesis Checkpoint G4, Theory of Operation rev 8,
the records at their G4 digests, `mechanism/` at `5b25245`, `slm/` at `SHA256SUMS-SLM-2026.09.28`, and the 09.25
critical review · NVIDIA basis: the OpenShell repository at commit `eef8bec` (2026.09.28, version 0.1.x) read in
full for its `docs/`, `architecture/`, `rfc/` and `crates/openshell-prover/`; the NemoClaw, NeMo Guardrails and
safety-for-agentic-ai repositories; and the 2026.09.28 launch coverage · prepared by Claude in one session at the
custodian's request

Nothing here is ratified, and this document proposes no decision text. §12 lists what could not be verified.

---

## 0. Verdict

The two are not competitors. They are the two halves of one problem, built from opposite ends.

**NVIDIA's Open Agent Safety Platform** (announced 2026.09.28) is a *product stack*: OpenShell, a shipping
open-source sandbox runtime that puts an agent behind kernel controls and a policy proxy; Sentry, an announced
out-of-band watchdog on BlueField-4 data-processing units with no ship date; and the surrounding NeMo tooling for
scanning, red-teaming and runtime guardrails. It has running code, a 0.1 release cadence, four compute drivers, a
Kubernetes chart, SDKs in four languages, and roughly a hundred named partners. Its guarantees are engineering
claims about defense in depth, and its documentation is careful about what each control does not cover.

**TOPAK** is an *architecture corpus in genesis*: 35 decision records, eleven TLA+ modules with mutation checks, a
gated Cedar floor, a Rust reference of the admit path with 44 tests, and a lineage rehearsal. It has no Observer,
no sandbox, no deployment, and one author. Its guarantees are stated as theorems over a configuration nobody
ships, with the assumptions that would make them hold listed on the front page.

The comparison that matters is not maturity, where NVIDIA wins on every row, but *what each thing is trying to be
true about*:

| | NVIDIA | TOPAK |
|---|---|---|
| **Object of the guarantee** | The running agent's reach: files, syscalls, network, credentials | The mechanism that admits effects, under an agent that may do anything its alphabet allows |
| **Premise about the model** | Untrusted at runtime; also *tested*, *guarded* and *shaped* by other models | Byzantine at every position; models stay out of the trusted computing base entirely |
| **Where the threat lives** | Run: a deployed agent going out of bounds | Build: the agents who author the specs, policy and floor Run is judged against |
| **Semantic judgment** | In the loop: guardrails, classifiers, content middleware can allow, deny or rewrite | Deny-only, as an Observer finding; never an admit precondition (ADR-0007) |
| **Policy authority** | Human operator approves; agent may *propose* widening mid-run | Renewal only narrows; widening is a new grant after the round ends; relaxations need the anchor |
| **Ordering and record** | OCSF event logs, rotated daily, exported to a SIEM | Consensus-ordered admits, denials recorded, six non-erasable forensic classes, erasure as a modeled event |
| **Confinement evidence** | The launcher's own assertion (container or microVM, no measurement) | Attested at grant; the archetype is a confidential VM with an independent verifier |
| **Verification** | Z3 prover over a policy-reachability model, as a *change-review* layer | TLC over the mechanism, Cedar analysis over the floor; also evidence, not proof |
| **Delivered today** | OpenShell, broadly available; Sentry, a reference design | An admit path at rung 0; `Contained` has no members |

In TOPAK's own vocabulary, OpenShell is a **rung-1 launcher for a `Mediated` principal**, built well, shipping, and
carrying exactly the failures TOPAK's first profile declares (P3, P4, P5). Sentry is closer to TOPAK's **Observer
placement rule** than to any confinement rung: a watcher on a different device from the watched. And the NeMo
evaluation stack is the **model-level MEASURE function TOPAK disclaims by havoc**. Read that way, NVIDIA has built the
substrate and the detector TOPAK's open list asks for, and TOPAK has written down the authority model, the
monotonicity discipline, the record and the verification obligations that NVIDIA's platform does not attempt.

---

## 1. What each thing is

### 1.1 NVIDIA Open Agent Safety Platform

Announced 2026.09.28 as "an open software platform and reference system design to strengthen AI security from agent
testing to deployment, with full-stack governance and control across software and the hardware, compute and
robotics systems that run agents." Its named parts:

| Part | What it is | Status |
|---|---|---|
| **OpenShell** | Open-source (Apache-2.0) runtime, mostly Rust. Gateway control plane; per-sandbox supervisor on the trusted side; sandbox runtime on the untrusted side; declarative YAML policy over filesystem, process, network and provider credentials; a Z3-backed policy prover; Docker, Podman, MicroVM and Kubernetes drivers | Version 0.1.x, "broadly available"; ~9k GitHub stars, 1,390+ commits |
| **Sentry** | A reference system design: an out-of-band watchdog on BlueField-4 DPUs, programmed through DOCA, that inspects agent requests and responses, verifies agent identity, provides "attested telemetry", enforces access policy for data, tools, APIs and services, and "quarantines and stops [an agent] in milliseconds" when it leaves its boundary. In the Vera Rubin POD design the DPU sits on the node's only path to the model | Announced; no availability date; existing Vera systems with BlueField-4 "can turn on the protections with a software update" |
| **NemoClaw** | Reference stack that installs Nemotron models and OpenShell for OpenClaw, Hermes and LangChain Deep Agents, with policy presets, provider trust tiers and posture profiles | Shipping, Apache-2.0 |
| **NeMo Guardrails, Nemotron safety models** | Programmable input, dialog, output, retrieval and execution rails; classifiers for content safety, topic control, PII and jailbreak detection | Shipping |
| **garak / NeMo Auditor, Agent Toolkit red-teaming, NeMo Evaluator** | Pre-deployment vulnerability scanning and agentic red-teaming; benchmarking | Shipping; the older "safety-for-agentic-ai" blueprint is unmaintained since 2026.04 |
| **Partners** | Anthropic (Claude Managed Agents run their work in OpenShell sandboxes), Microsoft, Red Hat, SAP, Salesforce, ServiceNow, JPMorganChase, Palo Alto Networks, CrowdStrike, Figure, Gecko Robotics, Skild AI, SpaceXAI, others | Announced |

The platform is Run-side by construction: it wraps an agent that already exists and has already been given a
shell, a package manager and API credentials, and it decides what that agent's processes may reach.

### 1.2 TOPAK

An architecture pattern for autonomous multi-agent collaboration that is safe by design (README; ToO §1). Five
roles, T·O·P·A·K, filled at the reference by TLA+/TLC, Cedar plus OPA, Multi-Paxos, MCP-connected agents and Kafka.
The corpus is thirty Accepted (genesis) records, four Proposed, one tombstone; eleven of the accepted records are
confirmation-required and author-ratified. The reference implements the admit path end to end and issues every lease
at rung 0. G4 §8 states what is not claimed: nothing independently reviewed, no theorem proved, no principal
`Contained`, no floor ratified, no deployment declared.

TOPAK is Build-first by construction: its sharpest claims are about who may change the rules, how a change is
classified, and what survives erasure, and it treats the coding agent with a shell as the thing to be designed
out, not wrapped.

---

## 2. Threat model and premise

**Shared ground.** Both refuse to trust the agent. OpenShell's architecture page: the sandbox "shares the boundary
with the untrusted agent, so it never makes policy decisions"; policies are "enforced at the infrastructure layer,
[so] a compromised agent cannot override them." TOPAK: "an agent is Byzantine at every deployment position" and
"safety cannot depend on what a model means or intends" (ToO §1). Both deny by default. Both keep credentials out
of the agent's hands: OpenShell injects provider credentials only at profile-authorized endpoints and the sandbox
"holds nothing worth stealing"; ADR-0036's rung-1 bridge keeps the lease token outside the guest so "the session is
the pipe." That last one is a genuine convergence, arrived at independently.

**Where they part.**

1. **Models in or out of the trusted base.** NVIDIA's stack uses models to defend against models at several points:
   Nemotron classifiers inside NeMo Guardrails, LLM self-check rails, and supervisor middleware that can "allow, deny,
   or change" a request. A guardrail that *allows* is a semantic judgment acting as an enabling condition, which is
   what ADR-0007 prohibits in the admit path. TOPAK admits only by syntactic lift and lets a classifier subtract
   authority, never add it. NVIDIA's position is the industry default and buys expressiveness; TOPAK's buys a
   smaller trusted base at the price of policies that "become inexpressible at admit time and have to be restated
   as detections" (ToO §2.2).
2. **Build versus Run.** NVIDIA's threat is the deployed agent that "attempt[s] to move outside [its] boundaries."
   TOPAK's inversion puts the Byzantine threat in Build: the author of the policy, not its subject. OpenShell's
   policy advisor (RFC 0002, accepted) leans the other way on purpose: "agents have the most task context and can
   often draft narrower changes than humans," so an in-sandbox agent may propose the rule that unblocks it. TOPAK
   would call that a Build author choosing its own authority path. OpenShell's mitigation is convergent with
   TOPAK's, though: the prover computes the *delta* the proposal would grant, and the docs tell the reviewer to
   "review the rule that `openshell rule get` shows, not the agent's description of it." That is "the classification
   is computed, not asserted" (ADR-0030 §5) in different words.
3. **What the host may do.** TOPAK's delegate-by-failure-direction test (ADR-0034) ranks substrates by whether a
   host fault can *add* authority. OpenShell names its host trust plainly: user-namespace isolation means "even if a
   container escape vulnerability exists, the attacker lands as an unprivileged host user," and the Kubernetes driver
   warns that without a CNI that enforces `NetworkPolicy` "sandbox pods can bypass OpenShell network policy." In
   TOPAK's table that is rung 1: the operator, the orchestrator and the launcher are in the trusted base for guest
   integrity. Sentry's pitch is that a DPU "operates independently from the agent's host system," so it "can observe
   agent activity and enforce policy even if the host itself has been compromised." Whether a Sentry fault can add
   authority (fail-open on DPU loss) is not stated anywhere read for this review.

---

## 3. Architecture, side by side

| TOPAK role | TOPAK instrument | Nearest NVIDIA part | Fit |
|---|---|---|---|
| **T** formal specification | TLA+ modules checked in TLC with mutations; Cedar's symbolic analysis over the floor | `openshell-prover`: Z3 over a reachability model of one sandbox's policy | Different objects. TLC checks the *mechanism* (leases, fences, composition, rules floor, confinement); the prover checks a *policy* against a boundary or a baseline. Neither is a refinement proof to code |
| **O** policy as code | A minimal Cedar floor on a verified evaluator, linked into the mechanism; per-request OPA bundles that can only refuse; `admit ⟺ floor_permit ∧ ¬bundle_deny` | One YAML policy per sandbox, compiled into an embedded OPA engine (`regorus`) with a baked `sandbox-policy.rego`; optional global policy; provider profiles that add rules | Both use OPA. TOPAK moved its floor *off* Rego because Rego has no mechanized semantics (ADR-0030 §3), and a deployment that keeps a Rego floor declares D-0030-1. OpenShell's whole enforcement tier is that degeneracy, tested rather than proven |
| **P** consensus | Sans-IO Multi-Paxos; every admit, grant, revocation, expiry and issuance is a log entry; the fence is the log index | Gateway with SQLite, or PostgreSQL for HA replicas that relay to the replica holding a sandbox's supervisor | No consensus, no ordering authority. In TOPAK terms, crash-recovery replicated state with no total order over decisions. That is fine for a control plane and fatal for a forensic claim (§7) |
| **A** agents | Six-variant Build alphabet exposed as MCP tools and nothing else; leases with twelve fields; `Contained` versus `Mediated` | Any agent binary in an Ubuntu image: Claude Code, Codex, Copilot CLI, OpenCode, Pi, OpenClaw; shell, package manager, git | OpenShell preserves the shell by design ("read files, install packages, call APIs"); TOPAK removes it by design and says so as a capability cost (ToO §2.4) |
| **K** event transport | Kafka, one topic per principal per round, sealed on emit, denials recorded | OCSF v1.8 events in the sandbox log, JSONL export, daily rotation, three files kept; Sentry's "contextual activity records" | Both record denials, which TOPAK singles out as the clause implementers drop. OpenShell has no seal, no erasure unit, no retention model beyond export |
| **Observer** | Deny-only, cross-family, never on the watched device; per-principal plus a correlator; not built | Sentry on a DPU; NeMo Guardrails rails; supervisor middleware content guards | NVIDIA has built detectors; TOPAK has placement rules and no detector. NVIDIA's detectors can also *allow*; TOPAK's cannot |
| **Confinement** | Profile P1–P7, rungs 0–3, appraisal at grant, archetype confidential VM + independent verifier; rung-1 launcher Proposed | Landlock, seccomp, no-capabilities non-root user, network fence, supervisor as launcher-and-appraiser; MicroVM driver with no guest network device | OpenShell is a rung-1 launcher (§4) |
| **Trust anchor, rules floor, promotion** | Havoc issuer bounded by R1–R9; quorum promotion with author recusal and Observer veto; genesis ceremony | Gateway RBAC (admin/user), OIDC or mTLS; operator approves proposals; RFC 0011 (draft) adds workspaces and roles | No counterpart. Authority in OpenShell is whoever holds the gateway |
| **Persona** | Model pinned with prompt, decoder, decode-observability class; in-house lineages with an independence criterion | Provider profiles bind a *credential* to endpoints and binaries; "provider attachment does not select or rewrite a model" | OpenShell does not pin the model. Silent substitution is undetected there, and is TOPAK's G13 as well |

---

## 4. Confinement: OpenShell against the seven clauses

This is the section that matters most, because confinement is TOPAK's largest gap and OpenShell's whole product.

ADR-0034 fixes a confinement profile by seven clauses. Applying them to an OpenShell sandbox as documented at
commit `eef8bec`:

| Clause | Requirement | OpenShell (container drivers) | OpenShell (MicroVM driver) |
|---|---|---|---|
| **P1** one channel, no network device | | Workload container has networking off; the authenticated Unix socket to the supervisor is the only egress; the outer fence denies everything else | **Pass.** "Guest has no network device"; vsock to the supervisor only |
| **P2** measured read-only root; workspace and pinned corpus root only | | Landlock confines paths to those listed; system paths read-only; a mandatory baseline protects `/.openshell`. Root is *restricted*, not *measured* | Same; no launch measurement |
| **P3** no shell, package manager or interpreter reachable | | **Fail, by design.** The default image is Ubuntu; coding agents need bash, git, python, node | Fail |
| **P4** tools as Wasm components, per call, workspace capability only | | **Fail.** Tools are native binaries. Identity is the executable path plus a SHA-256 digest pinned on first observed use (trust on first use) and denied on later mismatch | Fail |
| **P5** Persona weights inside the guest, in the launch measurement | | **Fail.** Inference is a network call to a provider endpoint with an injected credential; the model runs elsewhere | Fail (GPU pass-through exists, but nothing measures what runs on it) |
| **P6** one principal per guest, one guest per round | | One agent process per sandbox; sub-agents get their own sandboxes; a sandbox "generation" gets fresh tokens and certificates | Pass in spirit; "round" has no counterpart |
| **P7** the profile's own reference values | | Image by digest, policy revision, digest-pinned binaries | Pass in part; no measurement to compare them against |

The verdict falls out of ADR-0034 §4 rather than being asserted: an OpenShell sandbox is a **`Mediated` principal
under a declared profile at rung 1**. That is precisely the shape ADR-0036 asks the reference to build first, and
ADR-0036's own first profile fails only P3. OpenShell's would fail P3, P4 and P5, and it would pass P1 more cleanly
than the reference's Docker Desktop host can, because its VM driver removes the network device outright.

Three OpenShell mechanisms map onto ADR-0034 and ADR-0036 directly:

- **The supervisor is the launcher.** It "holds launch until [it] confirms" the boundary, "freezes the agent if the
  connection drops," and "a new supervisor can't take over a running sandbox, even with valid credentials." Compare
  ADR-0036: "a dead guest closes the pipe and the round ends; a dead launcher takes the token with it and the lease
  expires." The failure directions match.
- **The isolation-backend interface is typed so that a step cannot be skipped**: `attach → confirm → start_agent`
  each returns a new type, "so the supervisor can't start an agent on a boundary that hasn't been confirmed." That is
  the "instant" ADR-0034 calls the hard part, realized as a type discipline in one process rather than as an ordered
  appraisal in a log.
- **Trust on first use for binary digests** is the weak sibling of TOPAK's `Invoke(tool)` allowlist by name and
  digest. TOFU pins whatever ran first; the allowlist pins what was promoted.

What OpenShell does not have, and what would move it up the ladder: a launch measurement (rung 2 needs measured
boot; "a container has no launch measurement," ADR-0036), an independent verifier (rung 3), and any appraisal
verdict beyond the supervisor's own success. Sentry's "attested telemetry" is attestation *of the watcher's report*,
not of the guest's launch, and it does not change the guest's rung.

**Sentry and the Observer.** Sentry is a better fit for ADR-0008 than for ADR-0034. ADR-0008's rule is that
Observer replicas never share a device with the Thinker, because a shared device is a shared fault domain and an
unmodeled effect path. A DPU on the node's only path to the model is a different device by construction, sees the
traffic the Observer needs, and cannot be reached from the guest. Two things TOPAK would ask of it: (1) is it
deny-only, or can its policy decisions *grant* (the press language says "enforce access policies," which can be
either); (2) what happens to admits when the DPU is unreachable. ADR-0034's test says a component whose failure could
add or preserve authority must be consensus-backed, and a watchdog whose loss fails open would fail that test.
Neither question is answerable from public material today, and the quarantine latency is a design claim, not a
measurement.

---

## 5. Policy: floor and bundle versus YAML, OPA and the prover

**Language and evaluator.** TOPAK's floor is Cedar because the floor tier needs "an evaluator with a mechanized
semantics, an implementation checked against it, and a decidable comparison of two policy sets" (ADR-0030 §2), and
Rego has none of those. OpenShell's supervisor compiles each sandbox's YAML into an embedded OPA engine (`regorus`
0.9) with a built-in Rego ruleset. Both projects therefore run OPA; only TOPAK treats that as a declared degeneracy
(D-0030-1: non-vacuity and revision classification become measured rather than proven).

**Composition and monotonicity.** TOPAK's admit is `floor_permit ∧ ¬bundle_deny`: a bundle can only refuse, a
floor error is a deny, a stale bundle is monotone-safe under partition, and no bundle can widen anything. OpenShell
has one policy per sandbox plus provider-contributed rules, merged: "a request is allowed when either rule allows
it, and deny rules in either rule still apply." A gateway-wide global policy can override every sandbox. There is
no floor that a later revision cannot cross, except the always-blocked set (loopback, link-local, cloud metadata)
and the protected `/.openshell` path. The nearest thing to `bundle ⊑ floor` is the prover's *boundary check*, which
an operator or a parent agent runs by hand to show a candidate "allows nothing beyond the boundary" — a check
outside the enforcement path, where TOPAK's is a property of the composed decision at every admit.

**Change classification.** ADR-0030 §5 decides `F′ ⇒ F` and `F ⇒ F′` between a deployed floor and a candidate and
routes the change to an authority path by the answer, so a Byzantine author cannot relabel a relaxation. OpenShell's
proposal risk check is the same move on a narrower question: the prover runs on the baseline and the merged policy
and surfaces *new* credentialed reach, new HTTP methods on a credentialed host, link-local reach, and L7 bypass by
binaries whose traffic it cannot inspect. Any finding blocks auto-approval. The four categories are stated, the
model is per-sandbox, and the crate's README is explicit that it "doesn't observe the proxy's actual decisions."

**Gates.** TOPAK runs totality, non-vacuity and discrimination gates on the floor itself, with counterexamples, and
names floor fitness as the unowned fourth gate. OpenShell has schema validation twice (gateway, then sandbox), a
`fail_closed` default when a revision cannot load, and the prover's `unsupported` result whenever a policy uses a
shape it cannot model (GraphQL, MCP, WebSocket rules, audit-mode endpoints, non-ASCII selectors, differing paths).
Failing closed on the unmodeled is the right instinct and is the same instinct as TOPAK's "any error is a deny." There
is no non-vacuity check: nothing tells an operator that a rule can never fire.

**Who can widen, and when.** In TOPAK a renewal "only narrows," the bundle is fixed for the round, and a widening is
a fresh grant after the round ends; relaxing the floor takes an anchor issuance *and* a promotion. In OpenShell
network rules are hot-reloadable, an agent may propose an addition, an operator approves it in a TUI inbox, and an
opt-in automatic mode approves proposals that raise no finding, "including OpenShell's own drafts from blocked
connections." Filesystem and process settings are the one place OpenShell is as strict as TOPAK: they are "locked at
sandbox creation" and a change means a new sandbox, which is a round ending.

**What each is silent on.** OpenShell says nothing about who may author the boundary policy or how it changes; that
is the operator's problem. TOPAK says nothing about L7 request shape: its alphabet has no HTTP method, path or MCP
tool-name matcher, because its principals are not supposed to have a network at all. OpenShell's `protocol: mcp`
rules, which allow-list `tools/call` by tool name at the proxy, are the closest thing in either project to a typed
tool alphabet enforced on the wire, and they are enforced on a channel the agent is not supposed to be able to
bypass. That is a real point of contact with ADR-0022's "the alphabet is the whole protocol; it is not the whole
channel."

---

## 6. Authority, credentials and consensus

| Concern | TOPAK | OpenShell |
|---|---|---|
| Credential | A lease: one composite credential, twelve fields, one live lease per principal, round-coterminous, fence = Paxos log index | A gateway JWT and a sandbox JWT per sandbox *generation*, held by the supervisor, renewed together, invalid once the sandbox is deleted; provider credentials never leave the supervisor |
| Narrowing versus widening | Renewal narrows only and keeps bundle, round, role, confinement digest and rung | Provider detach and rotation take effect on the next poll; new environment variables need a new process; network widening via approved proposal |
| Revocation | Targeted revocation (principal, Persona or profile) and a fleet-wide epoch fence, both ordered, neither needing a quorum | Delete or stop the sandbox; detach the provider; Sentry "quarantine" (mechanism unstated) |
| Grants | Consensus for grants, local for denials; privileged grants are quorum votes on an anchor-issued roster | Gateway RBAC; two-tier admin/user; OIDC or mTLS; workspaces and per-workspace roles proposed (RFC 0011, draft) |
| Promotion of the enforcement artifact | The floor ships in the mechanism; a release is promoted by unanimous grant seats with author recusal and an Observer veto | Operator installs a release; no promotion concept |
| Anchor | Havoc issuer bounded by a rules floor (R1–R9); custody declared as (capture, loss) | The gateway operator |
| Time | Clocks buy liveness, never safety; intervals trusted by failure direction | Token TTLs; a `--wait` on policy loads; nothing stated about clock trust |

The generation-bound JWT pair is a good design and is the same *shape* as TOPAK's round-coterminous lease: both
end the credential when the unit of work ends, and both make a stolen credential worthless outside its pipe. What
TOPAK adds is the ordering: because the fence is a log index, every replica agrees which leases are live and when a
slot freed, and a decision made under epoch *e* is voided at apply if the epoch moved on (ADR-0033 §4). OpenShell's HA
mode replicates state through PostgreSQL and relays session-bound requests to the replica that holds the supervisor,
which is enough to keep the control plane up and says nothing about the order of decisions.

---

## 7. The record

TOPAK's record claims are its most distinctive and the ones NVIDIA's platform does not attempt:

- Every effect has "a consensus-ordered, signed, authorizing predecessor in the Paxos log" (ADR-0015).
- Denials are recorded, unordered, to the principal's round topic, and after the seal to a bounded `after`
  companion (ADR-0020, ADR-0003 A2), so replay can tell *behaved* from *was prevented*.
- Six forensic classes are non-erasable for the declared horizon, erasure is itself a modeled and recorded event,
  and "legibility replaces immutability" (ADR-0028).
- Control-plane facts are separated from cognitive payloads; the plaintext store is built for deletion (ADR-0004).

OpenShell's record is OCSF v1.8 structured events for network, HTTP, SSH, process, filesystem, configuration and
API activity, including denials with reasons, in a shorthand log and an optional JSONL export that "rotates daily
and retains the three most recent files." Durable retention, ordering, erasure and reader-set control are the
deployment's job, presumably via the SIEM the export targets. Sentry promises to correlate "agent interactions,
policy decisions, tool access, and data access into contextual activity records," with the DPU as the vantage
point; how those records are ordered against the supervisor's and whether they survive host compromise is not
public.

The honest summary: OpenShell logs what TOPAK's Observer would need and what ADR-0020 predicted implementers would
drop, and it drops what TOPAK's forensic floor exists to keep. Neither has a running Observer that reads the stream.

---

## 8. Detection and evaluation

**Detection.** TOPAK's Observer is specified and not built (G12; CR-2 open since 09.16: detection fails open, and
"a dead, partitioned, or colluding Observer is still indistinguishable from a clean system"). NVIDIA has three
detectors running today (Guardrails rails, Nemotron classifiers, supervisor middleware) and one announced (Sentry).
Middleware "fails closed by default" when its service is unavailable, which is a liveness coupling of the kind
CR-2 asks for and TOPAK has not written down. Against that, every NVIDIA detector can also allow or rewrite, and none
is placed by a rule like ADR-0008's; a Nemotron classifier judging a Nemotron agent is the monoculture ADR-0008 warns
against, and a guardrail that rewrites a request is a semantic component with write access to the admit path.

**Evaluation.** NVIDIA's "from testing to deployment" is a lifecycle with real tools at the testing end: garak (now
NeMo Auditor) for vulnerability probes, Agent Toolkit's red-teaming runner, NeMo Evaluator for benchmarks. All of it
measures the occupant. TOPAK deliberately does not: MEASURE 2.2, 2.5, 2.9 and 2.11 are marked out of scope
"disclaimed by havoc" in the feature list, and its testing is TLC mutations, Cedar gates, Rust mutation tests and
drift checks, all about the cage. The two are complementary, not competing. A deployment could run garak over its
Persona before promotion and admit the result only as gate evidence; TOPAK's rule is that the result may deny and
may never be the thing that grants.

**The Moon & Varshney ordering.** The 09.25 review graded TOPAK's delivered guarantee *Empirical*, because
composition is checked in TLC and asserted of the Rust. OpenShell is also Empirical, for a different reason: its
prover is a change-review layer over a model that "doesn't observe the proxy's actual decisions," so the running
supervisor is trusted to match the policy the prover reasoned about. Neither project has a refinement from a checked
model to the code that runs.

---

## 9. Where each is ahead

**NVIDIA is ahead on everything that runs.**
- A sandbox with kernel enforcement (Landlock, seccomp with user notification for network operations, capability
  drop, user and network namespaces), four drivers, GPU pass-through, Kubernetes with `NetworkPolicy` and HA.
- Credential injection at the proxy, so agents work with placeholders and real secrets never enter the workload.
- L7 enforcement on REST, GraphQL, WebSocket, MCP and JSON-RPC, including per-tool `tools/call` allow-lists.
- A shipping SMT-backed prover with a stated coverage line and a fail-closed `unsupported` result.
- Structured audit events in an open schema, SIEM export, and an agent-readable denial format.
- Three runtime detectors and an announced hardware watchdog on a separate device.
- Partners, adopters, a release cadence, an RFC process, a security disclosure policy, and telemetry that excludes
  content.

**TOPAK is ahead on everything that is written down about authority and evidence.**
- A stated premise (Byzantine at every position) and the consequence taken seriously: models out of the TCB,
  semantic lift prohibited in the admit path, findings deny-only.
- Monotonicity at ten layers (ToO §7.8), from decision to time, with the one that OpenShell violates most plainly
  (an agent proposing its own widening mid-round) made structurally impossible.
- A floor on a verified evaluator, a computed tighten/relax classification, and a non-vacuity gate on the floor.
- Consensus ordering of every authority-changing event, decide-then-recheck at apply, and denials in the record.
- A forensic floor, erasure as a modeled event, and non-composition of break-glass with erasure, all checked.
- An authority regress that ends in one axiom bounded by two verified floors, with custody as a declared axis.
- A confinement ladder with a failure-direction test that says *why* rung 3 is the archetype, and a first profile
  that lists its own failures.
- A Persona that pins the model, and a lineage-independence criterion computed from the log rather than claimed.
- A process that records its own debts, revisions and unreviewed ratifications on the face of each record.

**Where they converge**, which is worth noting because it was not coordinated: deny by default; fail closed on
loss of the supervisor or the launcher; the token stays outside the guest; binaries identified by digest, not by
path; denials recorded with reasons; per-generation and per-round credentials; a sub-agent's policy checked against
its parent's boundary; change classification computed from the two policies rather than trusted from the author;
an explicit list of what the verifier does not cover.

---

## 10. What this implies for the corpus

None of the following is decision text. Each names the record it would touch.

1. **OpenShell is a candidate substrate for ADR-0036's rung-1 launcher**, and a better-fenced one than the
   reference's Docker Desktop host. Its MicroVM driver gives P1 outright; its supervisor already plays the
   launch-confirm-bridge role; its per-generation credentials are the session binding. The profile ADR-0036 §1
   requires would declare P3, P4 and P5 as `fail` with their subtractions, and P2 as `pass` only in the restricted
   sense. That is a declared `Mediated` principal, which the 09.27 feasibility note says to build first. The cost is
   that OpenShell's policy tier is Rego (D-0030-1 for that tier) and its tool identity is TOFU rather than promoted
   digests (a new declared degeneracy would be needed under ADR-0022 §3).
2. **Sentry belongs to the ADR-0008 supersession, not to ADR-0034.** The unwritten record that reverses shared
   Observer scoping (G4 item 6) now has a shipped-hardware shape to argue against: a per-node watcher on a separate
   device, seeing the model path. The two questions §4 raises (deny-only? fail-open?) are what that record would
   need answered before it could cite Sentry as an instance.
3. **CR-2 has an external answer to borrow.** OpenShell's middleware blocks traffic when the middleware service is
   unavailable. An Observer record answering CR-2 could adopt the same coupling: admission requires a live Observer
   heartbeat within `L`, and its absence is a deny. That is a liveness cost TOPAK has been unwilling to state and
   OpenShell states as a default.
4. **The L7 tool alphabet is a gap in TOPAK's Run story.** Run's alphabet is open (G4 item 13). OpenShell's MCP rules
   show what a typed, wire-enforced tool vocabulary looks like when the principal *does* have a network, and they
   would be the natural shape for a Run alphabet at a degenerate confinement rung where P1 is not met.
5. **The feature list's Playbook mapping should add a column.** Several MEASURE rows TOPAK marks out of scope are
   exactly what garak, the red-teaming runner and NeMo Evaluator produce. A deployment declaration could point at
   them as the source of gate evidence without moving them into the admit path.
6. **The register warning applies to NVIDIA too.** "Formally verified policy changes" in OpenShell's architecture
   page means a Z3 reachability check over a model that excludes the proxy's behavior, and "quarantines in
   milliseconds" is a design claim about hardware that has not shipped. TOPAK's CR-25 discipline, where "proven"
   was struck for "checked," is the standard both should be read against.

---

## 11. Maturity, in numbers

| | TOPAK (G4, 2026.09.28) | OpenShell (`eef8bec`, 2026.09.28) | Sentry |
|---|---|---|---|
| Runs in production | No | Yes (Anthropic Claude Managed Agents, SpaceXAI, others named) | No |
| License | Apache-2.0 code, CC BY 4.0 docs | Apache-2.0 | Reference design; hardware required |
| Contributors | One | Many; RFC process; maintainers file | NVIDIA |
| Independent review | None; a full-corpus review is a bootstrap precondition | Public issues, PSIRT disclosure, external write-ups | None public |
| Formal artifacts | 11 TLA+ modules with mutations; Cedar floor with gates; 44 Rust tests | Z3 prover, covering filesystem, process, Landlock, L4 and REST; `unsupported` elsewhere | None stated |
| Confinement rung (ADR-0034) | 0 at the reference; 1 designed | 1, with P3, P4, P5 failing | Not a rung; a watcher |
| Consensus | Multi-Paxos | None | None |
| Detection | Not built | Middleware, Guardrails, classifiers | Announced |
| Record | Ordered log, denials, forensic floor (designed; archive not built) | OCSF events, 3-day local retention, SIEM export | "Contextual activity records" |

---

## 12. What could not be verified

- NVIDIA's own pages (`nvidia.com`, `nvidianews.nvidia.com`, `developer.nvidia.com`, `docs.nvidia.com`,
  `nvidia.github.io`) were blocked by this session's network policy. Everything attributed to the announcement,
  the Sentry design and the technical blog comes from the GlobeNewswire release as syndicated and from
  third-party coverage dated 2026.09.28, read through search summaries. Quotations from those sources are as
  relayed, not as checked against the originals.
- OpenShell was read from its repository at commit `eef8bec` (the `docs/`, `architecture/`, `rfc/` trees and the
  prover crate). Its behavior was not run. The Rego engine and baked ruleset were confirmed in
  `crates/openshell-supervisor-network`.
- The OpenShell-Research post on lessons from the policy prover, and the NemoClaw posture profiles, were not
  readable; both are cited only as existing.
- No Sentry documentation exists publicly beyond the launch material. Its fail-open or fail-closed behavior, its
  policy language, and whether its enforcement can grant are unknown.
- TOPAK was read at the working tree of `908363d`; `SHA256SUMS-G4` was not re-verified for this review.

---

## Sources

TOPAK: `README.md`; `checkpoints/topak-genesis-checkpoint-G4-2026.09.28.md`;
`checkpoints/topak-theory-of-operation-2026.09.28-rev8.md`; `decisions/ADR-0007.md`, `ADR-0008.md`, `ADR-0034.md`,
`ADR-0036.md`; `derived/topak-critical-review-2026.09.25.md`; `derived/topak-feature-list-2026.09.15.md`;
`mechanism/README.md`; `mechanism/GAPS-AND-ASSUMPTIONS.md`.

NVIDIA, read directly:
- [NVIDIA/OpenShell](https://github.com/NVIDIA/openshell) at `eef8bec`: `docs/about/overview.mdx`,
  `docs/about/architecture.mdx`, `docs/how-it-works/policies/{overview,prover,advisor,default-policy,manage-policies,schema}.mdx`,
  `docs/how-it-works/{inference,sandboxes/runtimes}.mdx`, `docs/security/best-practices.mdx`,
  `docs/observability/{logging,ocsf-json-export}.mdx`, `docs/extensibility/{isolation-backends,supervisor-middleware/index}.mdx`,
  `docs/kubernetes/high-availability.mdx`, `architecture/security-policy.md`, `rfc/0002-agent-driven-policy-management`,
  `rfc/0011-multi-player-design`, `crates/openshell-prover/{README.md,src/lib.rs}`,
  `crates/openshell-supervisor-network/{Cargo.toml,src/opa.rs}`.
- [NVIDIA/OpenShell issue #781, Policy Prover roadmap](https://github.com/NVIDIA/OpenShell/issues/781)
- [NVIDIA/NemoClaw](https://github.com/NVIDIA/NemoClaw); [NVIDIA-NeMo/Guardrails](https://github.com/NVIDIA-NeMo/Guardrails);
  [NVIDIA-AI-Blueprints/safety-for-agentic-ai](https://github.com/NVIDIA-AI-Blueprints/safety-for-agentic-ai)

NVIDIA, via search summaries (originals unreachable from this session):
- [NVIDIA Launches Open Agent Safety Platform, newsroom](https://nvidianews.nvidia.com/news/open-agent-safety-platform);
  [GlobeNewswire release](https://www.globenewswire.com/news-release/2026/09/28/3369606/0/en/nvidia-launches-open-agent-safety-platform-to-secure-agents-from-testing-to-deployment.html)
- [NVIDIA Open Agent Safety Platform solution page](https://www.nvidia.com/en-us/solutions/ai/agent-safety/)
- [NVIDIA technical blog: a reference for continuous in-silicon agent monitoring](https://developer.nvidia.com/blog/nvidia-open-agent-safety-platform-a-reference-for-continuous-in-silicon-agent-monitoring/)
- [Help Net Security](https://www.helpnetsecurity.com/2026/09/28/nvidia-open-agent-safety-platform/);
  [SecurityWeek](https://www.securityweek.com/nvidia-unveils-ai-agent-safety-platform-with-hardware-based-watchdog/);
  [CNBC](https://www.cnbc.com/2026/09/28/nvidia-releases.html);
  [FourWeekMBA, "only one layer is shipping"](https://fourweekmba.com/ai-nvidia-open-agent-safety-platform-openshell-sentry/);
  [The Next Web](https://thenextweb.com/news/nvidia-open-agent-safety-platform);
  [Techzine](https://www.techzine.eu/news/security/144615/nvidia-puts-ai-agents-behind-a-hardware-lock-with-openshell/)
- [OpenShell docs: overview](https://docs.nvidia.com/openshell/latest/about/overview);
  [policy prover](https://docs.nvidia.com/openshell/how-it-works/policies/prover);
  [security best practices](https://docs.nvidia.com/openshell/security/best-practices)
- [OpenShell-Research: what we learned applying formal methods](https://nvidia.github.io/OpenShell-Research/dev-notes/posts/2026-09-10-learning-formal-methods-agent-policy-prover/)
- [Lakera: red teaming in NeMo Agent Toolkit](https://www.lakera.ai/blog/red-teaming-agentic-capabilities-in-nvidia-nemo-agent-toolkit)
